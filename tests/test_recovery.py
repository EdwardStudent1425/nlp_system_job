"""Regression cases for quote formatting and reloaded Pydantic class identities."""
import json
from pathlib import Path
import types
import httpx
import pytest
from jobmatch.extraction import ground_profile, extract_local, validate_profile
from jobmatch.models import Profile, Skill, Job, Preferences
from jobmatch.search import SearchIndex
from jobmatch.llm import OpenRouter


def test_recruiter_quote_recovery_and_unsupported_claims(tmp_path):
    # Anonymous authored fixture, no personal CV/name stored in the tests.
    cv='Boolean Search, X-Ray пошук, HR-співбесіди. ATS: Hurma, Breezy HR. Досвід: 2.5 роки. Англійська: B2.'
    raw={'skills':[{'name':'boolean search','evidence':'boolean search'},
                   {'name':'breezy hr','evidence':'Breezy\n HR'},
                   {'name':'interviewing','evidence':'HR-співбесіди'},
                   {'name':'payroll','evidence':'Payroll management'}],
         'years_experience':2.5,'years_evidence':'2.5 роки','english':'B2','english_evidence':'B2','mode':'openrouter'}
    def handler(request):
        if request.method=='GET':return httpx.Response(200,json={'data':[{'id':'test/free','pricing':{'prompt':'0','completion':'0'},'architecture':{'output_modalities':['text']},'supported_parameters':['structured_outputs']}]})
        return httpx.Response(200,json={'model':'test/free','choices':[{'message':{'content':json.dumps(raw)}}]})
    adapter=OpenRouter('test/free','fake-key',client=httpx.Client(transport=httpx.MockTransport(handler)),log_dir=tmp_path)
    result=adapter.extract(cv)
    assert [s.evidence for s in result.skills]==['Boolean Search','Breezy HR','HR-співбесіди']
    assert result.years_experience==2.5 and result.english=='B2'
    assert adapter.validation_stats['quotes_recovered']==2
    assert adapter.validation_stats['skills_discarded']==1
    validate_profile(result,cv)


def test_unsupported_fact_is_unknown_not_invented():
    profile=Profile(skills=[Skill(name='git',evidence='Git')],years_experience=10,years_evidence='10 years',english='C2',english_evidence='C2',mode='test')
    result,stats=ground_profile(profile,'Git experience. English proficiency unspecified.')
    assert result.years_experience is None and result.english is None
    assert stats['fields_cleared']==2
    with pytest.raises(ValueError):
        ground_profile(profile.model_copy(update={'skills':[Skill(name='java',evidence='Imaginary skill')]}),'Git')


def test_rank_accepts_jobs_from_an_old_class_identity(monkeypatch):
    import jobmatch.models as current
    old_module=types.ModuleType('old_jobmatch_models')
    monkeypatch.setitem(__import__('sys').modules,old_module.__name__,old_module)
    exec(compile(Path(current.__file__).read_text(encoding='utf-8'),current.__file__,'exec'),old_module.__dict__)
    old_job=old_module.Job(id='test:reload',title='Python developer',company='Fixture',description='Python SQL',source='fixture',published=None,retrieved_at='test',historical=True,url=None,skills=['python','sql'])
    assert not isinstance(old_job,Job)
    cv='Python SQL developer. English B2.'
    results,_=SearchIndex([old_job]).rank(cv,extract_local(cv),Preferences(confirmed=True,include_unknown=True))
    assert results and isinstance(results[0].job,Job)
    assert results[0].job.id==old_job.id
