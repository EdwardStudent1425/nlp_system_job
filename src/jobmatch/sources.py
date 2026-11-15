"""Normalize historical Djinni records and genuinely retrieved DOU feed entries."""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from .models import Job
from .extraction import skill_spans

ROOT = Path(__file__).resolve().parents[2]
FEED = "https://jobs.dou.ua/vacancies/feeds/"
CITIES = {"Kyiv": ["київ", "киев", "kyiv", "kiev"], "Lviv": ["львів", "львов", "lviv"], "Dnipro": ["дніпро", "днепр", "dnipro"], "Odesa": ["одеса", "одесса", "odesa", "odessa"], "Kharkiv": ["харків", "харьков", "kharkiv"], "Vinnytsia": ["вінниця", "vinnytsia"], "Ivano-Frankivsk": ["івано-франківськ", "ivano-frankivsk"], "Ternopil": ["тернопіль", "ternopil"], "Ukraine": ["україна", "украина", "ukraine"]}

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}: self.hidden += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style"}: self.hidden = max(0, self.hidden-1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def plain(text: str) -> str:
    parser = TextParser(); parser.feed(text)
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def normalize_djinni(rows: list[dict], retrieved_at: str) -> list[Job]:
    jobs = []
    english_map = {"basic": "A1", "pre": "A2", "intermediate": "B1", "upper": "B2", "fluent": "C1"}
    for row in rows:
        description = plain(str(row.get("Long Description") or ""))
        title = str(row.get("Position") or "").strip()
        if not description or not title or not row.get("id"): continue
        experience = str(row.get("Exp Years") or "")
        years = 0 if experience == "no_exp" else (float(experience[:-1]) if re.fullmatch(r"\d+y", experience) else None)
        jobs.append(Job(id="djinni:"+str(row["id"]), title=title, company=str(row.get("Company Name") or "Unknown"), description=description, category=str(row.get("Primary Keyword") or ""), source="Djinni historical sample (2020-2023)", published=row.get("Published"), retrieved_at=retrieved_at, historical=True, url=None, skills=sorted(skill_spans(title+"\n"+description)), min_years=years, english=english_map.get(row.get("English Level"))))
    return deduplicate(jobs)

def deduplicate(jobs: list[Job]) -> list[Job]:
    seen_ids, seen_text, output = set(), set(), []
    for job in jobs:
        fingerprint = hashlib.sha256((job.title.casefold()+"|"+job.company.casefold()+"|"+job.description.casefold()).encode()).hexdigest()
        if job.id in seen_ids or fingerprint in seen_text: continue
        seen_ids.add(job.id); seen_text.add(fingerprint); output.append(job)
    return output

def parse_dou(payload: bytes, retrieved_at: str) -> list[Job]:
    if len(payload) > 10_000_000: raise ValueError("RSS response too large.")
    tree = ET.fromstring(payload)
    jobs = []
    for item in tree.findall("./channel/item"):
        url = item.findtext("link", "").strip()
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "jobs.dou.ua" or not re.fullmatch(r"/companies/[^/]+/vacancies/\d+/?", parsed.path): continue
        url = urlunsplit(("https", "jobs.dou.ua", parsed.path, "", ""))
        full_title = plain(item.findtext("title", ""))
        title, separator, tail = full_title.rpartition(" в ")
        if not separator: title, tail = full_title, ""
        company, _, location = tail.partition(",")
        description = plain(item.findtext("description", ""))
        if not title or not description: continue
        city = next((canonical for canonical, variants in CITIES.items() if any(re.search(r"(?<!\w)"+re.escape(v)+r"(?!\w)", location, re.I) for v in variants)), None)
        remote = True if re.search(r"віддалено|remote", location, re.I) else (False if city else None)
        ukraine = True if city else (False if re.search(r"за кордоном|варшава|прага|берлін|warsaw|prague|berlin", location, re.I) and not remote else None)
        jobs.append(Job(id="dou:"+hashlib.sha256(url.encode()).hexdigest()[:20], title=title, company=company.strip() or "Unknown", description=description, source="DOU RSS", published=item.findtext("pubDate"), retrieved_at=retrieved_at, historical=False, url=url, skills=sorted(skill_spans(title+"\n"+description)), city=city, remote=remote, ukraine=ukraine))
    return deduplicate(jobs)

def fetch_dou() -> list[Job]:
    request = urllib.request.Request(FEED, headers={"User-Agent": "JobMatch-UA-Academic-Prototype/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read(10_000_001)
    return parse_dou(payload, now())

def load_jobs() -> list[Job]:
    manifest = json.loads((ROOT/"data/manifest.json").read_text(encoding="utf-8"))
    payload = (ROOT/"data/jobs.json").read_bytes()
    if hashlib.sha256(payload).hexdigest() != manifest["jobs_sha256"]:
        raise ValueError("Corpus hash mismatch. Rebuild or restore the recorded data revision.")
    return [Job.model_validate(row) for row in json.loads(payload)]
