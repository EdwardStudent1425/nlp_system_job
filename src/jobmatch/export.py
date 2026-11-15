import csv
import io
import json
from datetime import datetime, timezone
from .models import Preferences, Profile, Recommendation
from .search import validate_recommendations

def export_results(results: list[Recommendation], cv: str, profile: Profile, prefs: Preferences, diagnostics: dict) -> dict[str,str]:
    if not prefs.confirmed: raise ValueError("Preferences not confirmed.")
    validate_recommendations(results, cv)
    markdown = ["# JobMatch UA Results", "", "Ranking scores express retrieval relevance, not hiring probability.", "Unmentioned skills are not proof of missing ability."]
    buffer=io.StringIO(newline=""); writer=csv.writer(buffer)
    writer.writerow(["id","title","company","score","source","historical","published","retrieved_at","url","matched_skills","unmentioned_skills","unknowns"])
    for r in results:
        markdown += [f"\n## {r.job.title} — {r.job.company}", f"Source: {r.job.source}; historical: {r.job.historical}; retrieved: {r.job.retrieved_at}", f"URL: [{r.job.url}]({r.job.url})" if r.job.url else 'URL: Unavailable in historical source', f"Matched: {', '.join(r.matched_skills) or 'No explicit skill overlap'}", f"Unmentioned in CV: {', '.join(r.unmentioned_skills) or 'None in known skill vocabulary'}", f"Unknown conditions: {'; '.join(r.unknowns) or 'None detected'}"]
        markdown += [f"- {e['skill']}: CV '{e['cv_quote']}' / job '{e['job_quote']}'" for e in r.evidence]
        row=[r.job.id,r.job.title,r.job.company,f"{r.score:.4f}",r.job.source,r.job.historical,r.job.published or "",r.job.retrieved_at,r.job.url or "",';'.join(r.matched_skills),';'.join(r.unmentioned_skills),';'.join(r.unknowns)]
        writer.writerow(["'"+str(x) if str(x).lstrip().startswith(('=','+','-','@')) else x for x in row])
    record={"created_at":datetime.now(timezone.utc).isoformat(),"profile":profile.model_dump(),"preferences":prefs.model_dump(),"diagnostics":diagnostics,"results":[r.model_dump() for r in results]}
    return {"recommendations.md":"\n".join(markdown)+"\n","recommendations.csv":buffer.getvalue(),"recommendations.json":json.dumps(record,ensure_ascii=False,indent=2)}
