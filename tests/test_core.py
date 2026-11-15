import io
import json
import hashlib
from pathlib import Path
import pytest
from jobmatch.models import Job, Preferences, Profile, Skill
from jobmatch.extraction import parse_cv, extract_local, skill_spans, validate_profile, redact_contacts
from jobmatch.sources import parse_dou, normalize_djinni, deduplicate, load_jobs, plain
from jobmatch.search import SearchIndex, filter_job, validate_recommendations
from jobmatch.export import export_results

@pytest.fixture
def profile():return extract_local("Python, SQL, Pandas. 2 years of experience. English B2.")

@pytest.fixture
def job():return Job(id="fixture-1",title="Data Engineer",company="Test company",description="Python SQL",source="authored test fixture",published=None,retrieved_at="2026-11-15",historical=True,url=None,skills=["python","sql"],min_years=1,english="B1",remote=True,city="Kyiv",ukraine=True)

def test_skill_boundaries_and_aliases():
    found=skill_spans("JavaScript React.js C++ .NET PostgreSQL and GitHub; PySpark")
    assert set(found)=={"javascript","react","c++",".net","postgresql","spark"}
    assert "java" not in found and "git" not in found

@pytest.mark.parametrize("text,years,english",[("Python. 3 years of experience. English B2.",3,"B2"),("SQL, 2 роки досвіду. Англійська C1.",2,"C1"),("SQL. Experience unspecified.",None,None)])
def test_profile_extraction(text,years,english):
    result=extract_local(text)
    assert result.years_experience==years and result.english==english
    validate_profile(result,text)

def test_invalid_evidence_rejected(profile):
    profile.skills[0].evidence="invented source quote"
    with pytest.raises(ValueError):validate_profile(profile,"Python SQL English B2.")

@pytest.mark.parametrize("data,name",[(b"","cv.txt"),(b"short","cv.txt"),(b"invalid pdf","cv.pdf"),(b"x"*30,"cv.docx"),(b'\xff'*30,"cv.txt")])
def test_invalid_uploads(data,name):
    with pytest.raises(ValueError):parse_cv(data,name)

def test_txt_and_contact_redaction():
    text=parse_cv(b"Python developer. Contact person@example.com or +380 67 123 45 67.","cv.txt")
    assert "person@example.com" not in text and "[EMAIL]" in text and "[PHONE]" in text

def test_searchable_and_blank_pdf():
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
    writer=PdfWriter();page=writer.add_blank_page(width=612,height=792)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
    stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 72 720 Td (Python SQL developer. English B2.) Tj ET')
    page[NameObject('/Contents')]=writer._add_object(stream)
    buffer=io.BytesIO();writer.write(buffer)
    assert 'Python SQL' in parse_cv(buffer.getvalue(),'cv.pdf')
    writer=PdfWriter();writer.add_blank_page(width=612,height=792)
    buffer=io.BytesIO();writer.write(buffer)
    with pytest.raises(ValueError,match='Too little'):parse_cv(buffer.getvalue(),'scan.pdf')

def test_source_normalization_and_url_rejection():
    xml=b'''<rss><channel><item><title>Data Engineer &#1074; Example, &#1050;&#1080;&#1111;&#1074;</title><link>https://jobs.dou.ua/companies/example/vacancies/123/?utm_source=x</link><description>&lt;p&gt;Python SQL&lt;/p&gt;</description></item><item><title>Fake</title><link>https://evil.example/x</link><description>text</description></item></channel></rss>'''
    jobs=parse_dou(xml,'2026-11-15')
    assert len(jobs)==1 and jobs[0].ukraine is True
    assert jobs[0].city=='Kyiv' and jobs[0].historical is False
    assert jobs[0].url=='https://jobs.dou.ua/companies/example/vacancies/123/'
    assert jobs[0].description=='Python SQL'
    assert plain('<script>fake</script><p>Real</p>')=='Real'

def test_historical_unknowns_and_no_invented_link():
    jobs=normalize_djinni([{'id':'1','Position':'Data analyst','Long Description':'Python SQL','Company Name':'X','Exp Years':'2y','English Level':'upper'}],'2026-11-15')
    assert jobs[0].url is None and jobs[0].ukraine is None and jobs[0].remote is None
    assert jobs[0].min_years==2 and jobs[0].english=='B2'
    assert len(deduplicate(jobs*2))==1

@pytest.mark.parametrize('attribute,value,expected', [('min_years',3,'experience'),('english','C1','English'),('remote',False,'remote'),('ukraine',False,'Ukraine'),('city','Lviv','City')])
def test_explicit_filter_rejections(job,profile,attribute,value,expected):
    setattr(job,attribute,value)
    reasons,_=filter_job(job,profile,Preferences(city='Kyiv',remote_only=True,include_unknown=True,confirmed=True))
    # A remote job can be based in another city without violating a city preference.
    if attribute=='city':
        job.remote=False
        reasons,_=filter_job(job,profile,Preferences(city='Kyiv',include_unknown=True,confirmed=True))
    assert any(expected in reason for reason in reasons)

def test_unknown_is_explicit_and_user_controlled(job,profile):
    job.ukraine=None;job.remote=None
    reasons,unknown=filter_job(job,profile,Preferences(remote_only=True,include_unknown=True))
    assert not reasons and len(unknown)==2
    reasons,_=filter_job(job,profile,Preferences(remote_only=True,include_unknown=False))
    assert reasons

def test_preference_gate_ranking_and_explanation(job,profile):
    irrelevant=job.model_copy(update={'id':'other','title':'React Developer','description':'JavaScript React','skills':['javascript','react']})
    index=SearchIndex([irrelevant,job])
    with pytest.raises(ValueError):index.rank('Python SQL',profile,Preferences())
    prefs=Preferences(role='Data Engineer',confirmed=True,include_unknown=True)
    results,diagnostics=index.rank('Python, SQL, Pandas. 2 years of experience. English B2.',profile,prefs,k=2)
    assert results[0].job.id==job.id
    assert set(results[0].matched_skills)=={'python','sql'}
    validate_recommendations(results,'Python, SQL, Pandas. 2 years of experience. English B2.')
    assert diagnostics['searched']==2

def test_export_and_source_snapshot_integrity(job,profile):
    cv='Python, SQL, Pandas. 2 years of experience. English B2.'
    job.title='=malicious formula'
    prefs=Preferences(confirmed=True,include_unknown=True)
    results,diagnostics=SearchIndex([job]).rank(cv,profile,prefs)
    files=export_results(results,cv,profile,prefs,diagnostics)
    assert set(files)=={'recommendations.csv','recommendations.md','recommendations.json'}
    assert "'=malicious" in files['recommendations.csv']
    assert json.loads(files['recommendations.json'])['preferences']['confirmed'] is True
    corpus=load_jobs()
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'data/manifest.json').read_text())
    assert len(corpus)==manifest['jobs']
    assert hashlib.sha256((root/'data/jobs.json').read_bytes()).hexdigest()==manifest['jobs_sha256']
