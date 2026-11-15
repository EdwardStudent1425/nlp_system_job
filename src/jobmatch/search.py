"""Transparent lexical baseline and skill-aware ranking; no hire probabilities."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .models import Job, Preferences, Profile, Recommendation
from .extraction import skill_spans
from .sources import CITIES

LEVEL = {name: i for i, name in enumerate(["A1", "A2", "B1", "B2", "C1", "C2"])}

def canonical_city(city: str) -> str:
    for canonical, aliases in CITIES.items():
        if city.casefold() in [canonical.casefold(), *aliases]: return canonical
    return city.strip()

def filter_job(job: Job, profile: Profile, prefs: Preferences) -> tuple[list[str], list[str]]:
    reasons, unknown = [], []
    if job.ukraine is False: reasons.append("Not explicitly available in Ukraine")
    elif job.ukraine is None: unknown.append("Ukraine eligibility unknown")
    if prefs.city:
        if job.city is None: unknown.append("City unknown")
        elif canonical_city(job.city) != canonical_city(prefs.city) and job.remote is not True: reasons.append("City does not match")
    if prefs.remote_only:
        if job.remote is False: reasons.append("Not remote")
        elif job.remote is None: unknown.append("Remote eligibility unknown")
    if job.min_years is not None:
        if profile.years_experience is None: unknown.append("Candidate experience unknown")
        elif profile.years_experience < job.min_years: reasons.append("Stated experience below listed minimum")
    else: unknown.append("Job experience minimum unknown")
    if job.english:
        if profile.english is None: unknown.append("Candidate English level unknown")
        elif LEVEL[profile.english] < LEVEL[job.english]: reasons.append("Stated English below listed minimum")
    else: unknown.append("Job English minimum unknown")
    if unknown and not prefs.include_unknown: reasons.append("Unknown conditions excluded by preference")
    return reasons, unknown

class SearchIndex:
    def __init__(self, jobs: list[Job]):
        if not jobs: raise ValueError("No searchable jobs available.")
        # Session objects can belong to a pre-reload Pydantic class identity.
        self.jobs = [Job.model_validate(j.model_dump() if hasattr(j,'model_dump') else j) for j in jobs]
        # Character n-grams tolerate morphology/spelling variation; they are not semantic embeddings.
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=40000, sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([j.title+" "+j.title+" "+j.category+" "+j.description for j in self.jobs])

    def rank(self, cv: str, profile: Profile, prefs: Preferences, *, method="skill-aware", k=5) -> tuple[list[Recommendation], dict]:
        if not prefs.confirmed: raise ValueError("Confirm search preferences before recommendations.")
        if not 1 <= k <= 50: raise ValueError("Choose between 1 and 50 results.")
        if method not in {"lexical", "skill-aware"}: raise ValueError("Unknown ranking method.")
        names = {s.name.casefold(): s for s in profile.skills}
        query = cv if method == "lexical" else " ".join([prefs.role]*3 + list(names)*2 + [cv])
        similarities = (self.matrix @ self.vectorizer.transform([query]).T).toarray().ravel()
        ranked, rejected = [], []
        for i, job in enumerate(self.jobs):
            reasons, unknown = filter_job(job, profile, prefs)
            if reasons:
                rejected.append({"job_id": job.id, "reasons": reasons}); continue
            spans = skill_spans(job.title+"\n"+job.description)
            matched = sorted(set(names) & set(job.skills))
            coverage = len(matched)/len(job.skills) if job.skills else 0.0
            lexical = float(similarities[i])
            score = lexical if method == "lexical" else 0.65*lexical + 0.35*coverage
            if score <= 0: continue
            evidence = [{"skill": s, "cv_quote": names[s].evidence, "job_quote": spans[s]} for s in matched if s in spans]
            ranked.append(Recommendation(job=job.model_dump(), score=score, lexical_score=lexical, matched_skills=matched, unmentioned_skills=sorted(set(job.skills)-set(names)), unknowns=unknown, evidence=evidence))
        ranked.sort(key=lambda r: (-r.score, r.job.id))
        return ranked[:k], {"method": method, "searched": len(self.jobs), "eligible": len(ranked), "rejected": rejected, "weights": {"lexical": 1.0 if method=="lexical" else 0.65, "mentioned_skill_coverage": 0 if method=="lexical" else 0.35}}

def validate_recommendations(results: list[Recommendation], cv: str) -> None:
    for result in results:
        for evidence in result.evidence:
            if evidence["cv_quote"] not in cv or evidence["job_quote"] not in result.job.title+"\n"+result.job.description:
                raise ValueError("Explanation evidence does not occur in the supplied documents.")
