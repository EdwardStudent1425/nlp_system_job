"""Small auditable extraction baseline and input/source validation."""
import io
import re
from .models import Profile, Skill

ALIASES = {
    "python": ["python", "пайтон"], "sql": ["sql"], "javascript": ["javascript", "java script"],
    "typescript": ["typescript"], "java": ["java"], "c++": ["c++"], "c#": ["c#"],
    ".net": [".net", "dotnet"], "react": ["react", "react.js"], "angular": ["angular"],
    "vue": ["vue", "vue.js"], "node.js": ["node.js", "nodejs"], "django": ["django"],
    "fastapi": ["fastapi"], "flask": ["flask"], "pandas": ["pandas"], "numpy": ["numpy"],
    "pytorch": ["pytorch"], "tensorflow": ["tensorflow"], "scikit-learn": ["scikit-learn", "sklearn"],
    "docker": ["docker"], "kubernetes": ["kubernetes", "k8s"], "aws": ["aws"],
    "azure": ["azure"], "git": ["git"], "linux": ["linux"], "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"], "mongodb": ["mongodb"], "redis": ["redis"], "excel": ["excel"],
    "power bi": ["power bi", "powerbi"], "tableau": ["tableau"], "figma": ["figma"],
    "selenium": ["selenium"], "playwright": ["playwright"], "jira": ["jira"], "php": ["php"],
    "laravel": ["laravel"], "symfony": ["symfony"], "golang": ["golang", "go language"],
    "airflow": ["airflow"], "spark": ["apache spark", "spark", "pyspark"], "kafka": ["kafka"],
    "dbt": ["dbt"], "snowflake": ["snowflake"], "databricks": ["databricks"],
    "bigquery": ["bigquery"], "gcp": ["gcp", "google cloud"], "etl": ["etl", "elt"],
    "hadoop": ["hadoop"], "mlflow": ["mlflow"], "scipy": ["scipy"],
    "swift": ["swift"], "kotlin": ["kotlin"], "html": ["html"], "css": ["css"],
}

def skill_spans(text: str) -> dict[str, str]:
    found = {}
    for name, aliases in ALIASES.items():
        for alias in aliases:
            match = re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", text, re.I)
            if match:
                found[name] = match.group()
                break
    return found

def redact_contacts(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    return re.sub(r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)", "[PHONE]", text)

def parse_cv(data: bytes, filename: str) -> str:
    if not data or len(data) > 5_000_000:
        raise ValueError("Provide a nonempty CV smaller than 5 MB.")
    if filename.lower().endswith(".pdf"):
        from pypdf import PdfReader
        try:
            reader = PdfReader(io.BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages[:15])
        except Exception as exc:
            raise ValueError("Cannot read this PDF. Use a searchable PDF or paste plain text.") from exc
    elif filename.lower().endswith(".txt"):
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("TXT files must be UTF-8.") from exc
    else:
        raise ValueError("Supported formats: searchable PDF and UTF-8 TXT.")
    if len(text.strip()) < 20:
        raise ValueError("Too little readable text. Scanned PDFs require OCR outside this MVP; paste the text.")
    if len(text) > 40_000:
        raise ValueError("Use a CV with at most 40,000 characters.")
    return redact_contacts(text.strip())

def extract_local(text: str) -> Profile:
    years = list(re.finditer(r"\b(\d{1,2}(?:[.,]\d)?)\s*(?:years?(?:\s+of\s+experience)?|рок\w*|рік)\b", text, re.I))
    year = max(years, key=lambda m: float(m[1].replace(",", "."))) if years else None
    english = re.search(r"(?:english|англій\w*)\s*[:—-]?\s*(A1|A2|B1|B2|C1|C2)\b", text, re.I)
    return Profile(skills=[Skill(name=n, evidence=q) for n, q in skill_spans(text).items()], years_experience=float(year[1].replace(",", ".")) if year else None, years_evidence=year.group() if year else None, english=english[1].upper() if english else None, english_evidence=english.group() if english else None, mode="local-rule-baseline")

def validate_profile(profile: Profile, text: str) -> None:
    _validate_profile_evidence(profile, text)
    if len({s.name.casefold() for s in profile.skills}) != len(profile.skills):
        raise ValueError("Duplicate extracted skills.")


def _validate_profile_evidence(profile: Profile, text: str) -> None:
    for skill in profile.skills:
        if not skill.name.strip() or skill.evidence not in text:
            raise ValueError("Extracted skill lacks an exact CV evidence span.")
    for value, quote in [(profile.years_experience, profile.years_evidence), (profile.english, profile.english_evidence)]:
        if value is not None and (not quote or quote not in text):
            raise ValueError("Extracted value lacks exact CV evidence.")


def deduplicate_profile_skills(profile: Profile, text: str) -> tuple[Profile, int]:
    """Validate every original quote, then combine repeated names, ignoring case/spaces.

    Keep the first evidence span. Different technologies such as C and C++ remain
    separate. A duplicate with unsupported evidence still rejects the whole output.
    """
    _validate_profile_evidence(profile, text)
    unique = {}
    for skill in profile.skills:
        name = skill.name.strip().casefold()
        if name not in unique:
            unique[name] = skill.model_copy(update={"name": name})
    result = profile.model_copy(update={"skills": list(unique.values())})
    validate_profile(result, text)
    return result, len(profile.skills) - len(result.skills)


def ground_profile(profile: Profile, text: str) -> tuple[Profile, dict]:
    """Recover case/whitespace variants as real spans; never invent support.

    Unsupported individual claims are removed, with counts for the UI/trace.
    Fully unsupported nonempty skill output still fails instead of masquerading
    as successful extraction. Schema errors remain fatal.
    """
    stats = {"quotes_recovered": 0, "skills_discarded": 0,
             "fields_cleared": 0, "duplicate_skills_removed": 0}

    def span(quote):
        if not quote or not quote.strip(): return None
        if quote in text: return quote
        pattern = r"\s+".join(re.escape(token) for token in quote.strip().split())
        match = re.search(r"(?<!\w)" + pattern + r"(?!\w)", text, re.I)
        if match:
            stats["quotes_recovered"] += 1
            return match.group()
        return None

    skills = []
    for skill in profile.skills:
        evidence = span(skill.evidence)
        if evidence and skill.name.strip():
            skills.append(skill.model_copy(update={"evidence": evidence}))
        else:
            stats["skills_discarded"] += 1
    if profile.skills and not skills:
        raise ValueError("No extracted skills have verifiable CV evidence. Review the input or try another model.")
    updates = {"skills": skills}
    for field, evidence_field in [("years_experience", "years_evidence"), ("english", "english_evidence")]:
        value = getattr(profile, field)
        evidence = span(getattr(profile, evidence_field)) if value is not None else None
        updates[field] = value if evidence else None
        updates[evidence_field] = evidence
        if value is not None and evidence is None: stats["fields_cleared"] += 1
    result, removed = deduplicate_profile_skills(profile.model_copy(update=updates), text)
    stats["duplicate_skills_removed"] = removed
    return result, stats
