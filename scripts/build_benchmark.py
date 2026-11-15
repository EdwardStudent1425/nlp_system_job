"""Materialize a fixed judged pool. Never derive judgments from ranker output."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from jobmatch.sources import load_jobs

ROOT=Path(__file__).resolve().parents[1]

def main():
    jobs=load_jobs(); chosen=[]
    for category,count in [('Data Analyst',4),('Data Engineer',4),('Data Science',2),('Python',2),('DevOps',2),('Android',1),('Design',1)]:
        pool=[j for j in jobs if j.category==category]
        if category=='Data Science':
            pool=[j for j in pool if 'Deep Learning' in j.title or 'Hadoop' in j.title]
        chosen.extend(pool[:count])
    # Judgments made from descriptions before running either retrieval method.
    # Each tuple is (analytics, engineering, ML, rationale), not a skill-overlap formula.
    labels=[
        (1,0,0,'Blockchain/AML-specific analysis; generic analyst only adjacent.'),
        (3,1,1,'Supply-chain SQL/Python analysis and dashboards; ETL and ML are secondary.'),
        (2,0,0,'Marketing analytics and reporting; requires additional domain tools.'),
        (3,1,0,'Product metrics, experiments and BigQuery reporting.'),
        (2,1,0,'Python dashboards, not primarily platform engineering or ML.'),
        (3,2,0,'API collection/cleaning plus BI dashboards; analytics dominates.'),
        (0,2,1,'Data-platform architecture and ML architecture; seniority and architecture need review.'),
        (0,3,1,'Streaming/bank data platform with Python AWS Kafka and team leadership.'),
        (0,3,1,'Explicit Hadoop/Spark data-platform development; not predictive-model work.'),
        (0,0,3,'Explicit computer-vision model training and production deployment.'),
        (0,0,0,'Business workflow automation, not the requested Data/ML work.'),
        (0,1,0,'Python network test/CI automation, adjacent infrastructure only.'),
        (0,0,0,'1C accounting-configuration development.'),
        (0,0,0,'BSS configuration/support; overlapping tools do not establish role fit.'),
        (0,0,0,'Android/Qt client development, different work.'),
        (0,0,0,'2D animation and visual production, different work.')]
    assert len(chosen)==len(labels)==16
    profiles=[
        ('analytics','Data Analytics','Data analyst: SQL Python Excel Power BI Tableau BigQuery Pandas. I analyze product metrics, experiments and dashboards. 5 years of experience. English C1.',0),
        ('engineering','Data Engineering','Data engineer: Python SQL AWS Airflow Kafka Spark Hadoop Docker Kubernetes. I build streaming data pipelines and data warehouses and lead a technical team. 5 years of experience. English C1.',1),
        ('ml','AI/ML Engineer','Machine learning engineer: Python PyTorch TensorFlow scikit-learn NumPy Pandas Docker AWS GCP. I train computer vision models and deploy inference services. 5 years of experience. English C1.',2)]
    data={'revision':'v1-frozen-before-metric-run','label_provenance':'AI-authored provisional judgments from public descriptions, not independent human review or hiring outcomes.',
          'human_reviewed':False,'grade_definition':{'0':'different work','1':'adjacent/weak','2':'relevant with material gaps','3':'strong task alignment'},
          'binary_relevant_min_grade':2,'jobs':[{'id':j.id,'title':j.title,'description_sha256':hashlib.sha256(j.description.encode()).hexdigest(),'rationale':labels[i][3]} for i,j in enumerate(chosen)],
          'queries':[{'id':qid,'role':role,'cv':cv,'grades':{j.id:labels[i][col] for i,j in enumerate(chosen)}} for qid,role,cv,col in profiles]}
    path=ROOT/'evaluation/ranking_pool.json'
    if path.exists():
        raise SystemExit('Benchmark already exists. Preserve the frozen reference; use a new revision for changes.')
    path.write_bytes(json.dumps(data,ensure_ascii=False,indent=2).encode('utf-8'))
    print('Created 16-job, 3-query provisional benchmark (48 judgments).')

if __name__=='__main__':main()
