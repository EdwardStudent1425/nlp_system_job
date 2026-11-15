"""Normalize inspected public records, recording hashes of the actual bytes."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from jobmatch.sources import normalize_djinni, parse_dou

ROOT=Path(__file__).resolve().parents[1]
def main():
    inspection=json.loads((ROOT/"data/source_inspection.json").read_text(encoding="utf-8"))
    raw=(ROOT/"data/djinni_sample.json").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=inspection["sample"]["sha256"]: raise ValueError("Source snapshot changed since inspection.")
    jobs=normalize_djinni(json.loads(raw),inspection["retrieved_at"])
    payload=json.dumps([j.model_dump() for j in jobs],ensure_ascii=False,indent=2).encode("utf-8")
    (ROOT/"data/jobs.json").write_bytes(payload)
    feed=ROOT/"data/raw/dou.xml"
    live=parse_dou(feed.read_bytes(),inspection["live_feed"].get("retrieved_at",inspection["retrieved_at"])) if feed.exists() else []
    (ROOT/"data/dou_snapshot.json").write_bytes(json.dumps([j.model_dump() for j in live],ensure_ascii=False,indent=2).encode("utf-8"))
    manifest={"revision":"starter-v3","jobs_sha256":hashlib.sha256(payload).hexdigest(),"jobs":len(jobs),"sampled_rows":len(json.loads(raw)),"dropped_duplicates_or_invalid":len(json.loads(raw))-len(jobs),"dou_snapshot_items":len(live),"serialization":"UTF-8 bytes, LF, JSON indent=2","source":"https://huggingface.co/datasets/lang-uk/recruitment-dataset-job-descriptions-ukrainian","license":"MIT per dataset card","historical_period":"2020-2023","sampling":"ten 100-row pages at fixed offsets, including Data/AI title ranges; not a random representative sample"}
    (ROOT/"data/manifest.json").write_bytes(json.dumps(manifest,indent=2).encode())
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
