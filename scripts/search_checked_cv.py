"""Local shortlist smoke check with user-confirmed filters; private exports only."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from jobmatch.extraction import parse_cv,validate_profile
from jobmatch.models import Profile,Preferences,Job
from jobmatch.search import SearchIndex
from jobmatch.export import export_results

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('cv',type=Path);parser.add_argument('checked_profile',type=Path);args=parser.parse_args()
    reference=json.loads(args.checked_profile.read_text(encoding='utf-8'))
    if hashlib.sha256(args.cv.read_bytes()).hexdigest()!=reference['cv_sha256']:raise SystemExit('CV changed since extraction.')
    text=parse_cv(args.cv.read_bytes(),args.cv.name);profile=Profile.model_validate(reference['profile']);validate_profile(profile,text)
    if not profile.skills:raise SystemExit('Empty profile: review extraction before a personalized shortlist.')
    jobs=[Job.model_validate(j) for j in json.loads((ROOT/'runs/latest_dou.json').read_text(encoding='utf-8'))]
    index=SearchIndex(jobs);summary=[]
    for role,slug in [('Data Engineering','engineering'),('Data Analytics','analytics'),('AI/ML Engineer','ml')]:
        prefs=Preferences(role=role,city='',remote_only=False,include_unknown=True,confirmed=True)
        results,diagnostics=index.rank(text,profile,prefs,k=5)
        diagnostics['candidate_profile_human_review']='pending; shortlist for review, not validated suitability'
        target=ROOT/'exports/real_cv'/slug;target.mkdir(parents=True,exist_ok=True)
        for name,content in export_results(results,text,profile,prefs,diagnostics).items():(target/name).write_bytes(content.encode('utf-8'))
        summary.append({'role':role,'source_records':len(jobs),'returned':len(results),'rejected':len(diagnostics['rejected']),
                        'top':[{'title':r.job.title,'url':r.job.url,'matched_skills':r.matched_skills,'unknowns':r.unknowns} for r in results[:3]],'private_export':str(target.relative_to(ROOT))})
    (ROOT/'runs/private_search_summary.json').write_bytes(json.dumps(summary,ensure_ascii=False,indent=2).encode('utf-8'))
    print(json.dumps(summary,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
