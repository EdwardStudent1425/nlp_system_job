"""Inspect the public catalog without sending a key, CV or generation request."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from jobmatch.llm import free_models

if __name__=="__main__":
    try:rows=free_models()
    except Exception as error:raise SystemExit(f'Public model catalog unavailable ({type(error).__name__}). Check internet access and retry.') from None
    record={'checked_at':datetime.now(timezone.utc).isoformat(),'url':'https://openrouter.ai/api/v1/models','generation_calls':0,'key_or_cv_sent':False,'models':rows}
    path=Path(__file__).resolve().parents[1]/'artifacts/openrouter_catalog.json'
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(json.dumps(record,indent=2).encode('utf-8'))
    for row in rows:print(row)
    print('Choose a fixed ID with structured_outputs=True; this is capability metadata, not measured model quality.')
