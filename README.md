# JobMatch UA

A runnable NLP prototype that compares a Ukrainian/English CV with Ukrainian-market IT vacancies. It extracts an evidence-backed profile, asks for role/location/work-format preferences, filters known constraints, ranks retrieved records, explains overlaps and unknowns, and exports JSON, CSV and Markdown.

Priority directions: **Data Engineering, Data Analytics, AI/ML Engineer**. Experience comes from the CV, not an assumed Junior label. This is a custom Assignment 1 idea: information extraction + clarification + filtering + retrieval + grounded reports. The implementation does not require training a large model or a RAG chatbot.

## Run on Windows / PowerShell

Run commands from the repository root (the local project folder is named `nlp_system2`; a GitHub clone may be named `nlp_system_job`). Use **Python 3.11** to reproduce the measured environment; the package declares 3.11+, but these pinned NumPy/scikit-learn versions are not suitable for every newer Python release. The included 1,000-job sample works without downloading data or configuring a key.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]" -c requirements-tested.txt
.venv\Scripts\python -m streamlit run app.py --server.port 8502
```

Open http://localhost:8502. If the environment is already installed, run only the last command. Activation is unnecessary. macOS/Linux: use `.venv/bin/python` instead.

1. Choose the synthetic Data/AI example or upload a searchable PDF/UTF-8 TXT CV; select the **Local rule baseline** to work without a key.
2. Click **Analyze CV**, inspect the extracted facts and exact evidence. To correct an extraction, revise/paste the CV text and analyze again; unsupported facts should remain unknown.
3. Select a direction, city/work format and whether visibly unknown conditions are acceptable. Tick the profile/preference confirmation and search.
4. Review the ranked jobs, paired quotes and unmentioned skills. Download the reports.
5. For real internet retrieval, click **Fetch current DOU RSS**, then search again. The latest public feed is a small recent window, not a search of every Ukrainian job board. **Use saved DOU snapshot** provides reproducible feed examples with genuine URLs and a visible retrieval date.

Historical records date from 2020–2023 and lack original application URLs. They demonstrate matching, not current open positions. A DOU entry has a genuine retrieved URL; recruitment status is not independently verified. Unknown Ukraine/location/remote information is never presented as confirmed eligibility. Role selection guides ranking rather than being an exact category filter.

## Verify and inspect results

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python scripts/evaluate.py --with-tests
```

The second command creates `artifacts/evaluation_local.json`, `artifacts/pytest.xml`, synthetic demo exports and [the measured results](docs/evaluation_local.md). It makes no generation/API calls. The initial measured run has skill F1 0.954 on 8 synthetic held-out cases and macro Precision@5 0.600 versus 0.467 for lexical retrieval on 3 queries / 16 real jobs. Labels are provisional AI-authored judgments; these are diagnostic results, not a validated hiring benchmark.

## Optional OpenRouter integration

Local mode is fully runnable without credentials. Real calls have now been checked: the initial Ling benchmark exposed poor extraction, and a temporary NVIDIA override successfully extracted one real CV. See [live validation](docs/live_validation.md) for settings, failures and limits. A full NVIDIA benchmark and human suitability review remain pending; HTTP/quote validation alone does not prove semantic accuracy.

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.venv\Scripts\python scripts/list_models.py
```

Edit `.env` locally: set `OPENROUTER_API_KEY` and a fixed `OPENROUTER_MODEL` ID from the catalog with `structured_outputs=True`. Never paste the key into chat or commit it. Do not overwrite an existing `.env` when repeating setup. Catalog access requires internet but no generation key. The adapter checks zero input/output pricing and schema capability again before generation; capabilities, availability and limits can change. The [free collection](https://openrouter.ai/collections/free-models) ranks usage, not extraction quality. Pin a model for each recorded experiment.

The public catalog was successfully checked without a key during preparation. The listing script saves a dated `artifacts/openrouter_catalog.json`; this is real capability-discovery evidence, not a generated-CV evaluation. Dynamic `openrouter/free`/`openrouter/auto` routers are excluded to keep model selection explicit.

Select OpenRouter in the app and analyze a **synthetic** CV first. It sends the contact-redacted CV to the configured external provider. Redaction removes common email/phone patterns, not all personal information; use a sanitized CV if you do not want other details sent. Review the provider's current data handling before using a personal CV. [Structured output documentation](https://openrouter.ai/docs/guides/features/structured-outputs) explains the JSON-schema API contract used here.

To measure real extraction later (12 synthetic cases; quota permitting):

```powershell
.venv\Scripts\python scripts/evaluate.py --mode openrouter
```

This produces separate `evaluation_openrouter.json` / `evaluation_openrouter.md` files. Ranking remains deterministic; only extraction metrics use the selected provider. Compare extraction with the local reference, inspect failures and actual model/provider/settings in ignored `runs/` traces. There is no silent local/paid fallback, automatic retry, automatic application submission or internet-search function provided by the LLM. Missing credentials, quota errors, malformed output and unsupported quotes are surfaced.

## Documentation and hand-in

- [Requirements and success criteria](requirements.md), [step-by-step plan](docs/plan.md), [assignment checklist](docs/submission_checklist.md).
- [Architecture and component contracts](docs/architecture.md), [data sources and inspection](docs/data.md), [annotation policy](evaluation/README.md).
- [Short CRISP-DM report](docs/report.md), [evaluation](docs/evaluation_local.md), [coding-assistant controls and reflection](docs/assistant_workflow.md).
- [Demo script, under 10 minutes](docs/demo_script.md), [maintenance/runbook](docs/runbook.md).
- [Full assignment audit and per-component evaluation](docs/assignment_audit.md), [timed video plan and complete narration](docs/video_narration.md).
- [Ukrainian presentation: step-by-step demo and spoken text for 5–7 minutes](docs/video_narration_uk.md).

```powershell
.venv\Scripts\python scripts/package_submission.py
```

Creates `dist/jobmatch-ua-submission.zip` and its SHA-256 manifest, excluding environments, keys, raw caches, private runtime logs and arbitrary uploads. Actual video recording is a separate required deliverable; no video has been fabricated or recorded by this project. Live OpenRouter evaluation and independent annotation review remain explicit quality gaps. Grades depend on the instructor and your explanation.

## Main limitations

The local extractor can mishandle negation, per-skill experience and unlisted skills. Character n-grams have weak cross-language semantics. The archive sample is deliberately small and biased; only four records use the Data Engineer category. Metadata categories/English/experience can disagree with full text. No broad market coverage, salary optimization, verified hiring probability, OCR, CV-to-job ground-truth dataset or production deployment is claimed.
