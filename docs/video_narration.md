# Video Plan and Ready-to-Speak Narration

Target duration: **9 minutes 30 seconds**, hard maximum 10 minutes. English narration follows the project's language convention. Use your own voice and adapt wording to what you actually show. This file is a script, not evidence of a completed recording. Do not claim a fresh network call if you show a saved snapshot or previously obtained model result.

## Prepare before pressing Record

1. Start from your own PowerShell/VS Code terminal in `nlp_system2`: `.venv\Scripts\python -m streamlit run app.py --server.port 8503`. Open http://localhost:8503. A server launched in a restricted agent environment may fail network access even when DOU is reachable.
2. Confirm the model locally, then **close the .env tab**. Hide names/contact details in your CV, desktop notifications, terminal history and any private report you show. Use the labeled synthetic example if you do not want personal data in the video.
3. Open rendered `requirements.md`, `docs/architecture.md`, `docs/data.md`, `docs/assignment_audit.md`, `docs/evaluation_local.md`, `docs/live_validation.md`, `AGENTS.md` and the two project SKILL.md files. Verify the Mermaid diagram is visible as a diagram in your preview. Keep the normal source editor available.
4. Preflight the example/profile and DOU source once. During recording show an actual run where practical. If inference is slow, use an honestly labeled previously obtained result or make a clearly indicated time cut; do not substitute a local result as live output.
5. Have an export ready to open. Tests are already measured; show their saved results or run them before recording to avoid wasting video time. Rehearse and measure your own duration.

## 0:00–0:45 — Problem, scope and requirements

**Show:** requirements.md, J-01…J-10. Point to the three priority directions and confirmed preferences.

> My project is JobMatch UA, an NLP assistant for a candidate looking for Ukrainian-market IT jobs. It accepts a CV and confirmed preferences and produces a ranked shortlist with source links, evidence and unknown conditions. The priority directions are Data Engineering, Data Analytics and AI/ML Engineering. I chose this custom idea under the assignment's alternative-task option. The prototype supports searchable PDF and text files. It does not submit applications. The goal is useful, traceable comparison; hiring probability and time savings have not been established.

## 0:45–1:40 — Components, data flow and design choices

**Show:** rendered architecture diagram, then briefly the contracts table. Trace one path with the pointer.

> The parser extracts text locally and removes common email and phone patterns. The profile extractor is either a transparent rule baseline or an OpenRouter model. Pydantic checks the schema, and evidence validation checks source quotes. The user reviews the profile and confirms preferences. A separate adapter provides job records. Known contradictions are filtered, then TF-IDF similarity and skill overlap rank the remaining jobs. Finally, the system displays paired evidence and exports reports. OpenRouter extracts the CV; it does not search the internet or rank vacancies. This separation makes each stage inspectable and testable.

## 1:40–2:30 — Data and CRISP-DM

**Show:** docs/data.md, data/manifest.json, then the six-phase table in assignment_audit.md.

> I followed CRISP-DM from business understanding through local delivery. Before constructing synthetic cases, I inspected the Djinni paper and public job records. The reproducible sample contains one thousand historical vacancies from 2020 to 2023. It has no linked hiring labels or original application URLs. DOU RSS provides a separate recent feed window; the saved snapshot contains fifty entries. These sources are selected separately. An initial sample lacked the target roles, so I returned to data collection and expanded it. Missing location and eligibility information remains unknown. The report records this iteration and the preparation decisions.

## 2:30–4:10 — Run input, extraction and confirmation

**Do:** select the labeled synthetic example; choose the actual mode you intend to demonstrate; click Analyze CV. Show the displayed analysis mode and fields. Try search without confirmation, show the warning, then confirm preferences and search. If showing previously obtained NVIDIA results, explicitly identify them as saved results instead of pretending to run inference.

> Here I analyze a clearly labeled demonstration CV. I check that the skills, experience and English level agree with the input. Unknown experience is acceptable; a model should not invent it. The interface identifies the extraction mode and supporting quotes. Searching without confirmation is blocked. I then confirm my target direction, location, remote preference and policy for unknown requirements. The ranker combines sixty-five percent lexical similarity with thirty-five percent recognized job-skill coverage. This score is retrieval relevance, not a percentage chance of being hired. Direction guides ranking rather than enforcing an exact title category.

## 4:10–5:25 — DOU URL, evidence, export and failure case

**Do:** click Fetch current DOU RSS. If unsuccessful, select Use saved DOU snapshot and say it is saved. Rerun search after switching sources. Show one visible URL outside the details; open it, return, expand evidence/unknowns, download and open a report. Finally, clear input and example selection and submit an empty CV to show the error.

> This source has genuine DOU vacancy links. The visible URL comes from the retrieved record, and the details show source and retrieval date. A feed entry does not prove recruitment is still open. Historical records have no invented application links. Each explanation pairs a CV quote with a job quote; other skills are described as unmentioned in the CV. I can export JSON, CSV and Markdown. The program also reports invalid input clearly. If a network request fails, the existing source remains labeled rather than being presented as a fresh retrieval.

## 5:25–7:05 — Evaluation at every stage

**Show:** assignment_audit.md component-evaluation table; scroll through parsing, extraction, ingestion, preferences/filters, ranking, explanation, URL/export and end-to-end rows. Show evaluation_local.md and one failure case.

> I evaluate components separately. Parser, redaction, preference gates, known constraint violations, source normalization and export integrity have controlled checks. The latest run passes thirty-two automated tests, including visible DOU links. Semantic metrics are separate: on eight synthetic reference CVs, local skill F1 is point nine five four, experience accuracy is seven out of eight, and English accuracy is eight out of eight. On sixteen real jobs and three queries, macro Precision at five improves from point four six seven to point six, while nDCG improves from point eight two seven to point eight six seven. Precision measures relevant results; nDCG also considers order. The labels are provisional AI-authored judgments. These small references do not establish general quality. Negation, unlisted skills and ambiguous year counts explain observed extraction errors. Quote integrity measures provenance, not suitability.

## 7:05–8:10 — Live findings, low scores and improvements

**Show:** docs/live_validation.md. Show safe model/settings/finish-reason metadata if desired, never a key. Briefly compare search directions in the app or show the documented observed weakness.

> Live checks exposed additional failures. The initial Ling run had held-out skill F1 around point five one two. Reasoning could consume the entire output budget, and some outputs failed schema or quote checks. I clarified the JSON-instance prompt, controlled optional reasoning and improved diagnostics. NVIDIA passed one real-CV extraction, but its full benchmark remains pending; the local F1 is not NVIDIA's score. The current shortlist also repeats top results across directions. This indicates weak role sensitivity. Next improvements are better role matching, finer requirements extraction and independently reviewed relevance labels. I preserve these failures rather than presenting technical execution as proof of usefulness.

## 8:10–9:30 — Assistant controls, reflection and submission

**Show:** AGENTS.md, both custom skills, assistant_workflow.md, then the audit/video checklist. Leave time to explain one rule and its concrete effect.

> I used an AI coding assistant with persistent instructions, not only repeated prompts. AGENTS.md requires CRISP-DM, real source identity, explicit unknowns, component evaluation and separation of local and live results. I created requirements-audit and component-evaluation skills. They guided requirement mapping and the distinction between contract tests, provisional labels and genuine inference. For example, the workflow rejected unsupported evidence rather than silently returning local output as an LLM response. It also prevented invented archive links. The assistant accelerated implementation, but self-authored evaluation still needs human review. The submission includes code, setup instructions, architecture, business scope, measured results and this personal demonstration. The prototype runs locally, while recommendation quality and broader validation remain clear limitations.

## Final recording checklist

- [ ] Actual duration is below 10 minutes; target 9:30 leaves a buffer.
- [ ] Requirements, diagram, component choices and one complete input flow are visible.
- [ ] A real app run shows input, review/confirmation, results, DOU URL and export.
- [ ] At least one negative case is visible; saved/live/local modes are described truthfully.
- [ ] Every component's evaluation evidence is shown in the table, with metric meaning, failures and improvements explained.
- [ ] Local extraction scores, old Ling scores and the one-CV NVIDIA check are not mixed.
- [ ] AGENTS.md, both custom skills and their concrete effects are shown.
- [ ] No API key or unwanted personal information appears in the recording.
- [ ] Actual video and final code/report are submitted by the author; this script alone is not the video deliverable.
