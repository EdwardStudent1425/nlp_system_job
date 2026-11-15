# JobMatch UA: Requirements and Scope

Date: November 15, 2026. The chosen assignment is a custom NLP application, permitted by page 2 of `NLP. Assignment 1. Build an NLP System (1) (4).pdf`. The BA example's specification/task/RACI outputs are not requirements for this different application.

## Business Understanding

Primary user: a job seeker considering Ukrainian IT roles. Input: a searchable PDF or TXT CV in Ukrainian/English plus explicitly confirmed preferences. Output: a ranked list of retrieved jobs, links when genuinely available, source/date/freshness, matching evidence, gaps and unknowns. The system does not submit applications.

User-confirmed priorities: Data Engineering, Data Analytics, and AI/ML Engineer. Experience level must come from CV/review, not an assumed Junior label. After the initial no-key preparation, the user configured a key locally and explicitly authorized contact-redacted CV transmission to OpenRouter. Current search preferences: all Ukrainian cities plus remote, visibly include unknown conditions. After initially prohibiting Git operations, the author explicitly authorized committing and pushing this project to https://github.com/EdwardStudent1425/nlp_system_job.git. Keys, personal CVs and private runtime outputs remain excluded. See docs/live_validation.md for actual checks and unresolved quality gaps.

Business objectives: reduce manual comparison by producing a useful shortlist, preserve factual support, respect explicitly stated constraints, and make archived versus recently retrieved information clear. Time savings and hiring probability are not established results.

Resources: one developer/coding assistant, local CPU environment, a small public Djinni sample, DOU RSS, optional free OpenRouter endpoint. Initial timebox is approximately three hours, not a completion guarantee. Risks: historical/unlabelled data, unknown location, poor lexical cross-language recall, API limits, variable PDF extraction. Controls: explicit unknowns, local baseline, small fixed evaluation, real sources and component checks.

| ID | Product requirement | Verification |
| --- | --- | --- |
| J-01 | Accept searchable PDF/TXT and reject empty/unreadable input clearly. | Parsing fixtures, PDF/TXT tests. |
| J-02 | Extract skills, experience and English with source evidence; separate unknown from absent qualification. | Labeled extraction cases; source validation. |
| J-03 | Collect/confirm role, city, work format and unknown-information policy before recommendations. | UI and preference-gate tests. |
| J-04 | Search a reproducible historical job corpus and support one real internet feed. | Djinni manifest, DOU retrieval/normalization checks. |
| J-05 | Filter constraints without turning unknown metadata into confirmed eligibility. | Filter positive/negative controls. |
| J-06 | Rank jobs and compare with a simpler lexical baseline. | Fixed judged pool, Precision@5/nDCG@5 and examples. |
| J-07 | Explain results using CV/job evidence and mark gaps as unmentioned, not proof of incompetence. | Evidence checks and qualitative review. |
| J-08 | Preserve genuine identifiers/URLs, source/date and archive/live distinctions. | Normalization/export tests. |
| J-09 | Export a useful results report and settings/provenance. | JSON/CSV/Markdown consistency checks. |
| J-10 | Integrate OpenRouter with explicit credentials/model and transparent failures. | Mocked HTTP tests; live verification only when credentials exist. |

## Assignment obligations

- G-01: working input-to-useful-output prototype; choose tools/model/interface.
- G-02: diagram, purpose/input/output of every component, model/external calls and complete walkthrough.
- G-03: inspect existing datasets before synthetic additions; document data preparation.
- G-04: apply all CRISP-DM phases with decisions, evidence and iteration.
- G-05: persistent coding-assistant instructions and custom development skills with actual use/reflection.
- G-06: evaluation of every component, appropriate metrics, failure interpretation and improvements.
- G-07: source, setup/run instructions, short report, scope, diagrams and actual evaluation results.
- G-08: video <=10 minutes covering requirements, architecture, running examples, evaluation and coding-assistant setup.

Public hosting, multi-agent orchestration, fine-tuning, a particular framework and large-scale model training are optional. Numerical thresholds below are project targets, not instructor-provided marks.

## Proposed technical acceptance targets

Source provenance and explanation quote integrity: 100% on checked outputs. No invented application URL. Explicit constraint violations in controlled fixtures: zero. Extraction skill micro F1 target >=0.85 on annotated starter cases. Ranking must be reported against baseline on the same judged pool; no performance improvement is assumed. Every component needs actual evidence and limitations. A tiny synthetic benchmark is not proof of general usefulness.
