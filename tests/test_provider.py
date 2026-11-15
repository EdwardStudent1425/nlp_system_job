import json
import httpx
import pytest
from jobmatch.llm import OpenRouter, ProviderError, free_models

def test_catalog_excludes_dynamic_router_and_paid_models():
    data=catalog()
    base=data['data'][0]
    data['data'] += [dict(base,id='openrouter/free'),dict(base,id='paid/model',pricing={'prompt':'1','completion':'0'})]
    client=httpx.Client(transport=httpx.MockTransport(lambda _:httpx.Response(200,json=data)))
    assert free_models(client)==[{'id':'test/free','structured_outputs':True}]

def test_missing_configuration_never_attempts_network(tmp_path,monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.delenv('OPENROUTER_MODEL',raising=False)
    monkeypatch.setattr('jobmatch.llm.dotenv_values',lambda _: {})
    def handler(request):raise AssertionError('Unconfigured adapter attempted a network call')
    model=OpenRouter(client=httpx.Client(transport=httpx.MockTransport(handler)),log_dir=tmp_path)
    assert not model.configured
    with pytest.raises(ProviderError,match='Set OPENROUTER'):model.extract('Python developer')

def catalog():return {'data':[{'id':'test/free','architecture':{'output_modalities':['text']},'supported_parameters':['structured_outputs'],'pricing':{'prompt':'0','completion':'0'}}]}

@pytest.mark.parametrize('unsupported_duplicate',[False,True])
def test_repeated_embedded_skills_preserve_evidence_validation(tmp_path,unsupported_duplicate):
    # Synthetic response reproduces repeated stack/project mentions; no live call.
    cv='C and Modern C++17. Firmware in C++ with FreeRTOS. CMake and Git.'
    skills=[{'name':'C++','evidence':'C++17'},
            {'name':' c++ ','evidence':'invented evidence' if unsupported_duplicate else 'C++'},
            {'name':'C','evidence':'C'}, {'name':'FreeRTOS','evidence':'FreeRTOS'},
            {'name':'Git','evidence':'Git'}, {'name':'git','evidence':'Git'}]
    def handler(request):
        if request.method=='GET':return httpx.Response(200,json=catalog())
        profile={'skills':skills,'years_experience':None,'years_evidence':None,'english':None,'english_evidence':None,'mode':'openrouter'}
        return httpx.Response(200,json={'model':'test/free','choices':[{'message':{'content':json.dumps(profile)}}]})
    adapter=OpenRouter('test/free','fake-key',client=httpx.Client(transport=httpx.MockTransport(handler)),log_dir=tmp_path)
    result=adapter.extract(cv)
    assert [s.name for s in result.skills]==['c++','c','freertos','git']
    assert result.skills[0].evidence=='C++17'
    log=json.loads(next(tmp_path.glob('*.json')).read_text())
    assert log['duplicate_skills_removed']==(1 if unsupported_duplicate else 2)
    assert log['evidence_cleanup']['skills_discarded']==int(unsupported_duplicate)


def test_optional_reasoning_is_disabled_and_truncation_is_visible(tmp_path):
    def handler(request):
        if request.method=='GET':
            data=catalog();data['data'][0]['supported_parameters'].append('reasoning')
            data['data'][0]['reasoning']={'mandatory':False,'default_enabled':True}
            return httpx.Response(200,json=data)
        assert json.loads(request.content)['reasoning']=={'enabled':False}
        return httpx.Response(200,json={'model':'test/free','usage':{'completion_tokens':2048},'choices':[{'finish_reason':'length','message':{'content':None}}]})
    model=OpenRouter('test/free','fake-key',client=httpx.Client(transport=httpx.MockTransport(handler)),log_dir=tmp_path)
    with pytest.raises(ProviderError,match='token budget'):model.extract('Python developer')
    log=json.loads(next(tmp_path.glob('*.json')).read_text())
    assert log['finish_reason']=='length' and log['output_characters']==0 and not log['success']

def test_real_adapter_contract_without_external_calls(tmp_path):
    def handler(request):
        if request.method=='GET':return httpx.Response(200,json=catalog())
        body=json.loads(request.content)
        assert body['response_format']['json_schema']['name']=='CandidateProfile'
        profile={'skills':[{'name':'python','evidence':'Python'}],'years_experience':None,'years_evidence':None,'english':None,'english_evidence':None,'mode':'openrouter'}
        return httpx.Response(200,json={'model':'test/free','provider':'mock','usage':{'total_tokens':10},'choices':[{'message':{'content':json.dumps(profile)}}]})
    client=httpx.Client(transport=httpx.MockTransport(handler))
    model=OpenRouter('test/free','secret-test-key',client=client,log_dir=tmp_path)
    assert model.extract('Python developer').mode=='openrouter:test/free'
    log=next(tmp_path.glob('*.json')).read_text()
    assert 'secret-test-key' not in log and 'Python developer' not in log

@pytest.mark.parametrize('failure',['quota','invalid_json','unsupported_evidence','paid'])
def test_errors_are_visible_and_not_replaced_with_local_output(tmp_path,failure):
    def handler(request):
        if request.method=='GET':
            data=catalog()
            if failure=='paid':data['data'][0]['pricing']['completion']='1'
            return httpx.Response(200,json=data)
        if failure=='quota':return httpx.Response(429,json={'error':'quota'})
        raw='not json' if failure=='invalid_json' else json.dumps({'skills':[{'name':'java','evidence':'Not in CV'}],'years_experience':None,'years_evidence':None,'english':None,'english_evidence':None,'mode':'x'})
        return httpx.Response(200,json={'choices':[{'message':{'content':raw}}]})
    model=OpenRouter('test/free','fake-key',client=httpx.Client(transport=httpx.MockTransport(handler)),log_dir=tmp_path)
    with pytest.raises(ProviderError):model.extract('Python developer')
    assert json.loads(next(tmp_path.glob('*.json')).read_text())['success'] is False
