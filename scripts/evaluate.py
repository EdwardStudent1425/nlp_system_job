"""Reproducible component and retrieval evaluation; no invented live LLM results."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from jobmatch.extraction import extract_local, validate_profile
from jobmatch.export import export_results
from jobmatch.llm import OpenRouter, ProviderError
from jobmatch.models import Job, Preferences
from jobmatch.search import SearchIndex, validate_recommendations
from jobmatch.sources import load_jobs

ROOT=Path(__file__).resolve().parents[1]

def read(relative):return json.loads((ROOT/relative).read_text(encoding='utf-8'))
def write(relative,value):
    path=ROOT/relative;path.parent.mkdir(exist_ok=True,parents=True)
    path.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode('utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def extraction(mode,model=None):
    cases=read('evaluation/extraction_cases.json')['cases']; output=[]
    adapter=OpenRouter(model=model) if mode=='openrouter' else None
    if adapter and not adapter.configured:
        raise SystemExit('Live evaluation requires local OPENROUTER_API_KEY and OPENROUTER_MODEL. No calls made.')
    for case in cases:
        started=perf_counter()
        try:
            profile=adapter.extract(case['text']) if adapter else extract_local(case['text'])
            validate_profile(profile,case['text'])
            predicted={s.name.casefold() for s in profile.skills}; reference=set(case['skills'])
            output.append({'id':case['id'],'split':case['split'],'success':True,'tp':len(predicted&reference),'fp':len(predicted-reference),'fn':len(reference-predicted),
                           'extra_skills':sorted(predicted-reference),'missed_skills':sorted(reference-predicted),'years_correct':profile.years_experience==case['years'],
                           'years_predicted':profile.years_experience,'years_reference':case['years'],'english_correct':profile.english==case['english'],
                           'quote_count':len(profile.skills)+int(profile.years_experience is not None)+int(profile.english is not None),'quote_valid':True,'actual_mode':profile.mode})
        except (ValueError,ProviderError) as error:
            output.append({'id':case['id'],'split':case['split'],'success':False,'error':str(error)})
        output[-1]['seconds']=perf_counter()-started
    metrics={}
    for split in ['development','held-out']:
        rows=[r for r in output if r['split']==split];good=[r for r in rows if r['success']]
        tp=sum(r['tp'] for r in good);fp=sum(r['fp'] for r in good);fn=sum(r['fn'] for r in good)
        # End-to-end extraction errors count all reference skills as missed.
        fn+=sum(len(c['skills']) for c in cases if c['id'] in {r['id'] for r in rows if not r['success']})
        metrics[split]={'cases':len(rows),'successful':len(good),'tp':tp,'fp':fp,'fn':fn,
                        'skill_micro_precision':tp/(tp+fp) if tp+fp else 0,'skill_micro_recall':tp/(tp+fn) if tp+fn else 0,
                        'skill_micro_f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,
                        'years_accuracy':sum(r['years_correct'] for r in good)/len(rows),'english_accuracy':sum(r['english_correct'] for r in good)/len(rows),
                        'valid_quotes':sum(r['quote_count'] for r in good),'quote_integrity_successful_outputs':1.0 if good else None}
    return {'metrics':metrics,'cases':output}

def dcg(grades):return sum((2**g-1)/math.log2(i+2) for i,g in enumerate(grades))

def ranking(jobs):
    reference=read('evaluation/ranking_pool.json');mapping={j.id:j for j in jobs}
    pool=[mapping[row['id']] for row in reference['jobs']]
    for row,job in zip(reference['jobs'],pool):
        if sha_description(job)!=row['description_sha256']:raise ValueError('Judged description changed.')
    index=SearchIndex(pool);rows=[]
    for query in reference['queries']:
        profile=extract_local(query['cv']);prefs=Preferences(role=query['role'],confirmed=True,include_unknown=True)
        for method in ['lexical','skill-aware']:
            started=perf_counter();results,diagnostics=index.rank(query['cv'],profile,prefs,method=method,k=5)
            grades=[query['grades'][r.job.id] for r in results]
            ideal=dcg(sorted(query['grades'].values(),reverse=True)[:5])
            validate_recommendations(results,query['cv'])
            rows.append({'query':query['id'],'method':method,'precision_at_5':sum(g>=2 for g in grades)/5,
                         'ndcg_at_5':dcg(grades)/ideal if ideal else 0,'returned':len(results),'seconds':perf_counter()-started,
                         'ranked':[{'id':r.job.id,'title':r.job.title,'grade':g,'score':r.score} for r,g in zip(results,grades)],
                         'rejected':diagnostics['rejected']})
    average={m:{key:sum(r[key] for r in rows if r['method']==m)/len(reference['queries']) for key in ['precision_at_5','ndcg_at_5']} for m in ['lexical','skill-aware']}
    return {'pool_size':len(pool),'queries':len(reference['queries']),'judgments':len(pool)*len(reference['queries']),'human_reviewed':False,'per_query':rows,'macro':average}

def sha_description(job):return hashlib.sha256(job.description.encode()).hexdigest()

def operational(jobs):
    cv=(ROOT/'examples/data_profile.txt').read_text(encoding='utf-8');profile=extract_local(cv)
    prefs=Preferences(role='Data Analytics',confirmed=True,include_unknown=True)
    started=perf_counter();index=SearchIndex(jobs);build_seconds=perf_counter()-started
    started=perf_counter();results,diagnostics=index.rank(cv,profile,prefs,k=10);seconds=perf_counter()-started
    validate_recommendations(results,cv);files=export_results(results,cv,profile,prefs,diagnostics)
    for filename,content in files.items():
        target=ROOT/'artifacts/demo'/filename;target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(content.encode('utf-8'))
    import csv,io
    exported=json.loads(files['recommendations.json'])
    csv_rows=list(csv.DictReader(io.StringIO(files['recommendations.csv'])))
    consistent=[r.job.id for r in results]==[r['job']['id'] for r in exported['results']]==[r['id'] for r in csv_rows]
    snapshot=[Job.model_validate(j) for j in read('data/dou_snapshot.json')]
    feed_index=SearchIndex(snapshot)
    feed_results,_=feed_index.rank(cv,profile,prefs,k=5)
    validate_recommendations(feed_results,cv)
    return {'corpus':{'records':len(jobs),'distinct_ids':len({j.id for j in jobs}),'nonempty_descriptions':sum(bool(j.description.strip()) for j in jobs),'historical':sum(j.historical for j in jobs),
                      'urls_available':sum(j.url is not None for j in jobs),'unknown_ukraine':sum(j.ukraine is None for j in jobs),'unknown_remote':sum(j.remote is None for j in jobs),
                      'unknown_english':sum(j.english is None for j in jobs),'unknown_min_years':sum(j.min_years is None for j in jobs),'categories':dict(Counter(j.category for j in jobs))},
            'feed_snapshot':{'records':len(snapshot),'distinct_urls':len({j.url for j in snapshot}),'known_ukraine':sum(j.ukraine is True for j in snapshot),
                             'unknown_ukraine':sum(j.ukraine is None for j in snapshot),'retrieved_at':snapshot[0].retrieved_at,'ranked':len(feed_results),'status':'previously retrieved public feed; not a fresh evaluation-time fetch'},
            'end_to_end':{'source':'historical','returned':len(results),'searched':diagnostics['searched'],'index_seconds':build_seconds,'rank_seconds':seconds,
                          'paired_evidence_spans':sum(len(r.evidence) for r in results),'all_quote_pairs_valid':True,'export_formats':len(files),'export_id_order_consistent':consistent,
                          'top_ids':[r.job.id for r in results],'synthetic_cv':True}}

def tests():
    target=ROOT/'artifacts/pytest.xml'
    result=subprocess.run([sys.executable,'-m','pytest','-q',f'--junitxml={target}'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(result.stdout)
    if result.returncode:raise SystemExit(result.stderr or 'Tests failed; evaluation incomplete.')
    cases=list(ET.parse(target).getroot().iter('testcase'))
    return {'total':len(cases),'passed':sum(not list(c) or all(x.tag not in {'failure','error','skipped'} for x in c) for c in cases),
            'cases':[{'component':c.attrib.get('classname'),'name':c.attrib['name'],'seconds':float(c.attrib.get('time',0))} for c in cases]}

def render(report):
    e=report['extraction']['metrics']['held-out'];o=report['operational'];r=report['ranking']
    lines=['# Measured Evaluation Results','',f"Run: {report['created_at']}. Extraction mode: {report['mode']}.",
           '','Synthetic reference cases and provisional AI-authored relevance judgments are diagnostic benchmarks. Independent human review is pending.',
           '','| Component | Measured result | Limit |','| --- | --- | --- |',
           f"| Extraction | Held-out skill P/R/F1 {e['skill_micro_precision']:.3f}/{e['skill_micro_recall']:.3f}/{e['skill_micro_f1']:.3f}; {e['cases']} cases | Small synthetic, vocabulary-dependent |",
           f"| Profile facts | Years accuracy {e['years_accuracy']:.3f}; English accuracy {e['english_accuracy']:.3f} | Exact field match, not proficiency verification |",
           f"| Ingestion | {o['corpus']['records']} archive records, {o['feed_snapshot']['records']} retrieved RSS records | Not exhaustive/current availability verification |",
           f"| Explanations | {o['end_to_end']['paired_evidence_spans']} valid paired spans in 10 archive results | Quote presence does not prove semantic entailment |",
           f"| Export | {o['end_to_end']['export_formats']} formats; ID/order consistency {o['end_to_end']['export_id_order_consistent']} | Synthetic demonstration CV |",
           f"| End-to-end | Index {o['end_to_end']['index_seconds']:.3f}s; ranking {o['end_to_end']['rank_seconds']:.3f}s | One local CPU run; excludes upload/API |"]
    if 'tests' in report:lines.append(f"| Contracts/UI | {report['tests']['passed']}/{report['tests']['total']} automated tests | Includes mocked provider, not real LLM calls |")
    lines+=['','## Retrieval on the same fully judged 16-job pool','','Relevant means grade >=2. Precision@5 uses denominator 5; nDCG uses gains 2^grade-1. Macro averages over 3 queries.','',
            '| Query | Method | Precision@5 | nDCG@5 |','| --- | --- | --- | --- |']
    for row in r['per_query']:lines.append(f"| {row['query']} | {row['method']} | {row['precision_at_5']:.3f} | {row['ndcg_at_5']:.3f} |")
    for method,value in r['macro'].items():lines.append(f"| Macro | {method} | {value['precision_at_5']:.3f} | {value['ndcg_at_5']:.3f} |")
    lines+=['','## Observed extraction failures','']
    for case in report['extraction']['cases']:
        if case['success'] and (case['fp'] or case['fn'] or not case['years_correct'] or not case['english_correct']):
            lines.append(f"- {case['id']}: extra={case['extra_skills']}, missed={case['missed_skills']}, years predicted/reference={case['years_predicted']}/{case['years_reference']}, English correct={case['english_correct']}.")
    lines+=['','## Interpretation','',
            'The rule extractor recognizes listed terms but does not understand negation, unlisted skills or per-skill versus total experience. Profile review is required. A high span-integrity score only establishes provenance.',
            'Data-engineering/ML pools are sparse. Matching tools can promote adjacent support/automation roles; character n-grams provide weak Ukrainian-English semantic alignment. The skill-aware method must be judged by the numbers above, not its name. No weights were tuned on this pool.',
            'Filtering is evaluated with controlled contradictions and unknown cases in tests/test_core.py. The RSS experience/English minima remain unknown; coarse historical metadata can disagree with description text. Broad job-market suitability, user time savings and hiring outcomes were not measured.',
            'In local mode, extraction uses no provider. OpenRouter-mode runs contain actual generation attempts and case-level failures; HTTP mocks alone verify only the adapter contract. Independent annotation, a larger separately frozen benchmark and actual provider evaluation remain the next quality gates.','']
    (ROOT/f"docs/evaluation_{report['mode']}{'_'+report['tag'] if report.get('tag') else ''}.md").write_bytes('\n'.join(lines).encode('utf-8'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['local','openrouter'],default='local');parser.add_argument('--with-tests',action='store_true');parser.add_argument('--model');parser.add_argument('--tag',default='');args=parser.parse_args()
    if args.tag and not all(c.isalnum() or c in '_-' for c in args.tag):raise SystemExit('Use an alphanumeric tag.')
    (ROOT/'artifacts').mkdir(exist_ok=True)
    extracted=extraction(args.mode,args.model)
    report={'created_at':datetime.now(timezone.utc).isoformat(),'mode':args.mode,'tag':args.tag,'environment':{'python':platform.python_version(),'platform':platform.platform(),
            'packages':{p:version(p) for p in ['pydantic','httpx','scikit-learn','numpy','streamlit','pypdf','pytest']}},
            'fingerprints':{str(p.relative_to(ROOT)):sha(p) for p in sorted([*ROOT.glob('src/jobmatch/*.py'),ROOT/'app.py',ROOT/'data/jobs.json',*ROOT.glob('evaluation/*.json')])},
            'extraction':extracted,'ranking':ranking(load_jobs()),'operational':operational(load_jobs())}
    if args.with_tests:report['tests']=tests()
    write(f"artifacts/evaluation_{args.mode}{'_'+args.tag if args.tag else ''}.json",report);render(report)
    print(json.dumps({'mode':args.mode,'held_out_extraction':extracted['metrics']['held-out'],'ranking_macro':report['ranking']['macro'],'tests':report.get('tests',{}).get('total')},indent=2))

if __name__=='__main__':main()
