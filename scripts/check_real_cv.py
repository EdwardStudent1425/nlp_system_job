"""Explicitly authorized live extraction smoke check; private results stay in runs/."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from jobmatch.extraction import parse_cv,extract_local,validate_profile
from jobmatch.llm import OpenRouter,ProviderError

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('cv',type=Path);parser.add_argument('--model');parser.add_argument('--max-tokens',type=int,default=4096);args=parser.parse_args()
    text=parse_cv(args.cv.read_bytes(),args.cv.name)
    local=extract_local(text);adapter=OpenRouter(model=args.model,max_tokens=args.max_tokens);started=perf_counter()
    try:profile=adapter.extract(text)
    except ProviderError as error:
        print(json.dumps({'success':False,'error':str(error),'requested_model':adapter.model}))
        raise SystemExit(1)
    finally:adapter.client.close()
    validate_profile(profile,text)
    record={'checked_at':datetime.now(timezone.utc).isoformat(),'cv_sha256':hashlib.sha256(args.cv.read_bytes()).hexdigest(),
            'redacted_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'profile':profile.model_dump(),
            'local_profile':local.model_dump(),'seconds':perf_counter()-started,'exact_quote_validation':True,
            'semantic_human_review':'pending','search_preferences_confirmed':False}
    suffix=hashlib.sha256((record['cv_sha256']+profile.mode).encode()).hexdigest()[:12]
    target=ROOT/f'runs/private_cv_check_{suffix}.json';target.parent.mkdir(exist_ok=True)
    target.write_bytes(json.dumps(record,ensure_ascii=False,indent=2).encode('utf-8'))
    print(json.dumps({'success':True,'mode':profile.mode,'skills':[s.name for s in profile.skills],
                      'years_experience':profile.years_experience,'english':profile.english,'exact_quotes_valid':True,
                      'seconds':record['seconds'],'saved_private_report':str(target.relative_to(ROOT))},ensure_ascii=True))

if __name__=='__main__':main()
