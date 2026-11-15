"""Package the explicit coursework deliverables, excluding secrets/runtime uploads."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    files=[]
    for name in ['README.md','AGENTS.md','requirements.md','requirements-tested.txt','pyproject.toml','.gitignore','.env.example']:
        path=ROOT/name
        if not path.is_file():raise SystemExit(f'Missing required source file: {name}')
        files.append(path)
    for directory in ['src','tests','scripts','docs','evaluation','examples','.agents/skills']:
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in {'.py','.md','.json','.txt'} and '__pycache__' not in p.parts and not any(part.endswith('.egg-info') for part in p.parts))
    for name in ['manifest.json','source_inspection.json','jobs.json','djinni_sample.json','dou_snapshot.json']:
        files.append(ROOT/'data'/name)
    for name in ['evaluation_local.json','evaluation_openrouter.json','launch_check.json','openrouter_catalog.json','pytest.xml']:
        path=ROOT/'artifacts'/name
        if path.exists():files.append(path)
    files.extend((ROOT/'artifacts').glob('evaluation_*.json'))
    files.extend(p for p in (ROOT/'artifacts/demo').glob('*') if p.suffix in {'.json','.md','.csv'})
    files=sorted(set(files));records=[]
    for path in files:
        if path.is_symlink() or ROOT not in path.resolve().parents:raise SystemExit('Unexpected external/symlink file.')
        relative=path.relative_to(ROOT).as_posix()
        if path.name=='.env' or any(part in {'.venv','runs','raw','exports'} for part in path.relative_to(ROOT).parts):raise SystemExit('Unexpected private file.')
        records.append({'file':relative,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    destination=ROOT/'dist';destination.mkdir(exist_ok=True)
    target=destination/'jobmatch-ua-submission.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:archive.write(path,arcname='jobmatch-ua/'+path.relative_to(ROOT).as_posix())
        archive.writestr('jobmatch-ua/SUBMISSION_MANIFEST.json',json.dumps(records,indent=2))
    manifest={'archive':target.name,'archive_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':records,'video_included':False,'live_openrouter_measured':(ROOT/'artifacts/evaluation_openrouter.json').exists()}
    (destination/'submission_manifest.json').write_bytes(json.dumps(manifest,indent=2).encode('utf-8'))
    print(json.dumps({'archive':str(target),'files':len(records),'bytes':target.stat().st_size,'sha256':manifest['archive_sha256'],'video_included':False},indent=2))

if __name__=='__main__':main()
