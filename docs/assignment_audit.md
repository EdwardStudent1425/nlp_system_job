# Assignment 1: Requirement-by-Requirement Audit

Audited November 15, 2026 against the supplied assignment PDF and its pasted text. Status reflects observable evidence, not a predicted grade. **Done** means an artifact or behavior is present; **Partial** means important quality evidence remains; **Pending** means the actual deliverable does not exist. A custom candidate-oriented job assistant is permitted; requirements specific to the recruiter/BA/HR example are not automatically applicable.

## Complete requirement checklist

| # | Assignment requirement | Status | Evidence / remaining work |
| --- | --- | --- | --- |
| 1 | Select an NLP application idea and define the task | Done | requirements.md: candidate CV-to-vacancy matching |
| 2 | Define business scope and requirements | Done | requirements.md, docs/architecture.md |
| 3 | Choose tools, model and interface | Done | pyproject.toml; Streamlit; rule/TF-IDF baselines; OpenRouter adapter |
| 4 | Accept input and produce useful output | Partial | Input-to-export works, but live role-specific shortlist quality is weak; usefulness is not established |
| 5 | Make the prototype runnable; deployment is optional | Done | README setup/run commands, launch artifact, UI tests; public hosting is unnecessary |
| 6 | Go beyond vanilla RAG | Done | Extraction, clarification, constraint filtering, ranking and evidence/export; no vanilla-RAG-only design |
| 7 | Produce an original implementation | Author confirmation | Custom source is present; independent authorship compared with classmates cannot be certified by repository inspection |
| 8 | Inspect existing datasets before generating synthetic data | Done | Source inspection timestamps, paper/publisher review, docs/data.md |
| 9 | Prepare the data | Done | scripts/prepare_data.py, normalized corpus, manifest, documented missing fields and sampling |
| 10 | Draw the data-flow diagram | Done | Mermaid diagram in docs/architecture.md; render it before recording |
| 11 | Describe each component's purpose, input and output | Done | Architecture contracts table |
| 12 | Identify model and external-tool calls | Done | Architecture call inventory; OpenRouter and DOU have distinct roles |
| 13 | Explain one input through the full system | Done in docs | Architecture walkthrough; personal explanation still needed in video |
| 14 | Manage the coding assistant beyond repeated prompts | Done | AGENTS.md and docs/assistant_workflow.md |
| 15 | Create custom development SKILLS | Done | .agents/skills/requirements-audit and component-evaluation; documented use/validation |
| 16 | Instruct the assistant to follow CRISP-DM | Done | AGENTS.md explicitly requires the cycle and evidence |
| 17 | Reflect CRISP-DM application in the report | Done | docs/report.md, phase mapping below, live iteration addendum |
| 18 | Evaluate every component | Partial | Every local stage has contract/diagnostic evidence; selected NVIDIA model has only one real-CV operational check, not a full quality benchmark |
| 19 | Select appropriate metrics | Done at diagnostic scope | Skill P/R/F1, field accuracy, P@5/nDCG@5, explicit violation counts, provenance/consistency checks; rationale below |
| 20 | Distinguish high and low scores | Done | High local F1 versus low initial Ling F1; sparse ML and weak live role sensitivity explicitly explained |
| 21 | Explain errors and possible improvements | Done | Local negation/year errors; live prompt/reasoning failures; role-ranking weakness; concrete next steps |
| 22 | Supply source code or notebook | Done locally | Source/tests/scripts supplied; GitHub publication is optional and not authorized |
| 23 | Supply setup and run instructions | Done | README.md and docs/runbook.md |
| 24 | Supply a short report | Done | docs/report.md plus docs/live_validation.md status update |
| 25 | Include diagrams, scoped business logic and measured evaluation results | Done | Architecture, requirements, evaluation Markdown/JSON, this component audit |
| 26 | Record an actual video of at most 10 minutes | Pending | docs/demo_script.md is a plan and narration, not a recording |
| 27 | Show selected requirements in the video | Pending | Script segment 1 |
| 28 | Show components/diagram and explain choices | Pending | Script segment 2 |
| 29 | Run several cases in the video | Pending | Script segments 4–5: profile, gate, source, URL/export and invalid input |
| 30 | Show and explain evaluations in the video | Pending | Script segments 6–7, including limitations |
| 31 | Show assistant setup/context/behavior controls and reflect | Pending | Script segment 8: AGENTS.md, custom skills, actual decisions |
| 32 | Submit the actual code/report/video | Pending | The author must record and submit through the course platform; no external submission performed |

This granular list contains **22 Done, 2 Partial, 7 Pending and 1 Author confirmation**. Several pending entries describe different parts of the same missing video; this is not a meaningful equal-weight completion percentage. Do not translate the count into rubric marks. The earlier 13-task preparation checklist uses different granularity.

## Evaluation for every component

| Component | Measured evidence | Why this metric fits | Failure / next improvement |
| --- | --- | --- | --- |
| PDF/TXT parsing | Valid TXT/searchable PDF, five invalid-input cases and a blank PDF are checked in test_core.py; one real PDF parsed | Acceptance/rejection checks isolate format handling from NLP quality | OCR/layout-heavy/multilingual PDF accuracy is not measured; add diverse PDFs with reference text |
| Contact redaction | Fixture checks email/phone removal | Direct checks of the intended transformation | Not complete anonymization; names/other personal data may remain |
| Local profile extraction | 8 synthetic held-out cases: skill precision 0.939, recall 0.969, F1 0.954; years 7/8, English 8/8 | F1 accounts for extra and missed skills; exact field accuracy includes unknown values | Negation causes false skills; per-skill or historical-data years can be wrong; vocabulary misses OpenCV |
| Profile schema/evidence validation | Invalid evidence/schema controls; held-out baseline has 45 checked source spans | Format validity and span presence have different meanings from semantic correctness | A valid span can occur in a negated/unrelated statement; add independent entailment review |
| Live OpenRouter extraction | Frozen initial Ling run: 5/8 held-out cases accepted, skill F1 0.512, years accuracy 0.500, English 0.250. NVIDIA: one real CV, 29 entries with exact quotes, about 6.3s | Failures count in end-to-end metrics; acceptance/latency prove operation, not general quality | Old Ling results use an earlier prompt/settings. Full NVIDIA quality evaluation remains unmeasured; do not attribute local F1 to NVIDIA |
| Ingestion/normalization | 1,000 archive records, 1,000 distinct IDs/nonempty descriptions; saved RSS has 50 distinct source URLs; fixture checks stripping/dedup/URL rejection | Counts/completeness, identity and URL provenance are appropriate for ingestion | Normalized URL shape does not prove availability. Country/experience metadata needs manual audit |
| Preference collection | Core/UI tests block unconfirmed search, then allow confirmed preferences | Gate correctness is a deterministic behavioral check | No measured conversational clarification quality; interface is a fixed form |
| Constraint filtering | Five controlled known contradictions rejected; unknown include/exclude and remote/city behavior checked | Explicit violation tests establish rule behavior under known metadata | RSS experience/English minima remain unknown; Senior roles may pass; evaluate annotated real constraints |
| Ranking | Same 16 real jobs, 3 queries, 48 provisional AI-authored grades: macro P@5 0.467 → 0.600, nDCG@5 0.827 → 0.867 | P@5 measures relevant items among first five; graded nDCG assesses order | ML nDCG slightly worsens; only one strongly relevant ML job. Live top results repeat across directions. Strengthen role sensitivity and source coverage using separate development cases |
| Explanations | 26/26 paired CV/job evidence spans occur in the documents in 10 archive recommendations | Provenance consistency is measurable without an LLM judge | Not a factual-entailment/suitability score; human review remains pending |
| URL presentation and source labels | Genuine DOU URLs retained, now visible outside collapsed details and in export; archive URLs remain absent | UI test checks displayed links equal selected source URLs | A source URL is not proof that recruitment is open; do not invent links for archives |
| Export | JSON/CSV result ID/order consistency; three formats; CSV formula escaping tests | Checks output integrity and portability | Personal exports are private; semantic recommendation quality requires separate review |
| Interface/end-to-end | Automated UI input/review/gate/search/source-change/error paths; latest local run in docs/evaluation_local.md | Integration checks show the components work together | Passing tests does not establish business usefulness or time savings |

**Evidence levels:** automated contracts, synthetic references, provisional relevance judgments, real source retrieval and one-CV inference are separate. No independently adjudicated hiring labels or user time-savings study exists. Correctly identifying poor outputs is part of evaluation; it does not justify describing the prototype as production-ready.

## CRISP-DM evidence

| Phase | Applied decision | Evidence |
| --- | --- | --- |
| Business Understanding | Candidate shortlist for three priority directions; user confirmation, resource/time/privacy constraints; no applications | requirements.md |
| Data Understanding | Inspected public jobs and paper; found missing URLs/location and poor initial role coverage | docs/data.md, source_inspection.json |
| Data Preparation | Expanded sample, normalized text/metadata, preserved unknowns/IDs, deduplicated and hashed; separately labeled diagnostic references | prepare_data.py, manifest, evaluation/README.md |
| Modeling | Rule extractor and lexical baseline, skill-aware extension, optional structured extraction and explicit model failures | src/jobmatch, architecture |
| Evaluation | Compared methods, examined weak cases, discovered live reasoning/schema/evidence and role-sensitivity failures | Local/live evaluation artifacts, docs/live_validation.md |
| Deployment | Local UI/setup, source package, monitoring/recovery guidance and final-report/video preparation | README, runbook, packager, demo script; actual video pending |

The cycle is iterative: poor initial role coverage returned work to collection; live extraction failures returned work to prompt/budget/diagnostic design. The next iteration should address role relevance and a separately frozen NVIDIA reference, not hide negative findings.

## Rubric and final actions

| Rubric | Available evidence | What the author still needs to demonstrate |
| --- | --- | --- |
| System understanding — 4 points | Diagram, contracts and walkthrough | Explain the actual data flow and why each component exists in the video |
| Working prototype — 4 points | Runnable input-to-export flow with actual DOU URLs | Show it running and acknowledge weak role-specific usefulness |
| Evaluation — 4 points | Per-stage checks, metrics, baseline comparison and failure analysis | Explain denominators/limits; fuller NVIDIA and independent relevance review would strengthen evidence |
| Coding assistant management — 3 points | Persistent instructions, custom skills, reflection | Show files and explain concrete decisions they controlled |

Before recording: review provisional labels and sample recommendations; ensure the model name matches the actual shown mode; rehearse source retrieval/URL/export and negative cases; render the diagram. Record a personal video below 10 minutes, rebuild the local source archive after final changes, then submit code/report/video. No maximum score is guaranteed.
