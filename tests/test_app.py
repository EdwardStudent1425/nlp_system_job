from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_ui_local_workflow_and_confirmation_gate():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=30)
    assert not app.exception
    app.checkbox[0].check()
    next(b for b in app.button if b.label == 'Analyze CV').click().run(timeout=30)
    assert not app.exception
    assert app.session_state.profile.mode == 'local-rule-baseline'
    next(b for b in app.button if b.label == 'Find matching vacancies').click().run(timeout=30)
    assert any('confirm' in w.value.lower() for w in app.warning)
    assert 'result' not in app.session_state
    next(c for c in app.checkbox if c.label.startswith('I reviewed')).check()
    next(b for b in app.button if b.label == 'Find matching vacancies').click().run(timeout=30)
    assert not app.exception
    results, diagnostics, prefs, *_ = app.session_state.result
    assert results and diagnostics['searched'] == 1000 and prefs.confirmed
    assert all(r.job.historical and r.job.url is None for r in results)
    next(b for b in app.button if b.label == 'Use saved DOU snapshot').click().run(timeout=30)
    assert any('source changed' in w.value.lower() for w in app.warning)
    assert not app.exception and len(app.session_state.jobs) == 50
    next(b for b in app.button if b.label == 'Find matching vacancies').click().run(timeout=30)
    assert not app.exception
    feed_results=app.session_state.result[0]
    assert feed_results
    visible_links=[m.value for m in app.markdown if m.value.startswith('Vacancy URL:')]
    assert len(visible_links)==len(feed_results)
    assert all(f'[{r.job.url}]({r.job.url})' in link for r,link in zip(feed_results,visible_links))
    next(b for b in app.button if b.label == 'Analyze CV').click().run(timeout=30)
    assert 'result' not in app.session_state


def test_ui_invalid_input_is_reported():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=30)
    next(b for b in app.button if b.label == 'Analyze CV').click().run(timeout=30)
    assert app.error and not app.exception
