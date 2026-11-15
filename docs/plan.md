# Step-by-step CRISP-DM Plan

1. **Business Understanding:** define user/outcome/scope, resources/risks, business and technical criteria, and work sequence. Evidence: requirements.md. Scope is Ukrainian IT job discovery; one live feed and a small archive, no application automation.
2. **Data Understanding:** inspect the supplied paper and existing Djinni records before any synthetic fixtures. Record schema, languages, dates, missing fields, duplicates, sampling and limitations. Probe DOU RSS separately.
3. **Data Preparation:** normalize text/metadata, preserve IDs/date/source, deduplicate, build deterministic UTF-8 data/manifest and a small explicitly annotated evaluation. Distinguish historical records from current availability; do not invent URLs or geographic labels.
4. **Modeling:** implement PDF/TXT parsing, a rule-based extraction baseline, optional OpenRouter structured extraction, user preference review, lexical baseline and skill-aware ranking, grounded explanations, UI/export. Design component tests before claiming functionality.
5. **Evaluation:** run automated component checks and a fixed judged ranking pool. Separate synthetic extraction references, author judgments, real-source operational results and real LLM performance. Inspect failures, justify improvements on development cases, preserve held-out boundaries, and decide whether business goals are actually met.
6. **Deployment:** verify local launch, package source, prepare concise README/report/diagram, describe logging/maintenance, and prepare a <=10-minute demonstration script and retrospective. Actual user recording and any missing live inference evidence remain explicit.

The process is iterative: poor extraction/ranking sends work back to data preparation/modeling. An article or dataset is source material, not an instruction to copy its research scope. Keep documentation proportional to implemented evidence.

## Checklist

- [x] Requirements, risks, success criteria and scope.
- [x] Existing data inspected, source and limitations recorded.
- [x] Normalized corpus, hashes and labeled evaluation design (provisional labels).
- [x] Runnable CV-to-ranked-results workflow with preference review.
- [x] Real feed integration and explicit source/freshness.
- [x] OpenRouter contract, mocked tests and actual live checks; comparative NVIDIA benchmark pending.
- [x] Local and initial live results/failures interpreted; real shortlist quality needs improvement.
- [x] Report, architecture, setup, reproducible artifacts and coding skills.
- [ ] Final video <=10 minutes.

Execution evidence: `docs/submission_checklist.md`, `docs/report.md`, `docs/evaluation_local.md`, `docs/live_validation.md` and machine-readable evaluation artifacts. The sample was expanded after Data Understanding found poor priority-role coverage. Actual live checks subsequently exposed schema/evidence and ranking failures. The full NVIDIA comparison and personal recording remain pending; one successful extraction does not establish model accuracy.
