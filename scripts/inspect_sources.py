"""Collect a deterministic public-data sample and probe the advertised DOU feed."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "JobMatch-UA-Academic-Prototype/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(10_000_000)

def main():
    raw_dir = ROOT / "data/raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    report = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "historical_dataset": "lang-uk/recruitment-dataset-job-descriptions-ukrainian", "pages": [], "live_feed": {}}
    records = []
    for offset in [0, 1000, 2000, 3000, 4000, 4500, 5000, 10000, 15000, 20000]:
        query = urllib.parse.urlencode({"dataset": report["historical_dataset"], "config": "default", "split": "train", "offset": offset, "length": 100})
        url = "https://datasets-server.huggingface.co/rows?" + query
        target = raw_dir / f"djinni-{offset}.json"
        if not target.exists():
            target.write_bytes(get(url))
        payload = target.read_bytes()
        data = json.loads(payload)
        rows = [item["row"] for item in data["rows"]]
        records.extend(rows)
        report["pages"].append({"offset": offset, "rows": len(rows), "sha256": hashlib.sha256(payload).hexdigest(), "url": url, "cache_file_timestamp": datetime.fromtimestamp(target.stat().st_mtime, timezone.utc).isoformat()})
    output = ROOT / "data/djinni_sample.json"
    output.write_bytes(json.dumps(records, ensure_ascii=False, indent=2).encode("utf-8"))
    report["sample"] = {"rows": len(records), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "columns": sorted(records[0]) if records else []}
    url = "https://jobs.dou.ua/vacancies/feeds/"
    try:
        feed_path = raw_dir / "dou.xml"
        if not feed_path.exists(): feed_path.write_bytes(get(url))
        payload = feed_path.read_bytes()
        feed = ET.fromstring(payload)
        items = feed.findall("./channel/item")
        report["live_feed"] = {"url": url, "items": len(items), "retrieved_at": datetime.fromtimestamp(feed_path.stat().st_mtime, timezone.utc).isoformat(), "sample_fields": [child.tag for child in items[0]] if items else [], "description_lengths": [len(item.findtext("description", "")) for item in items[:5]]}
    except Exception as exc:
        report["live_feed"] = {"url": url, "error_type": type(exc).__name__, "error": str(exc)}
    (ROOT / "data/source_inspection.json").write_bytes(json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
