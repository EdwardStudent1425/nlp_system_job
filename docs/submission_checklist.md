# Assignment Readiness and Next Actions

This checklist separates implemented local deliverables from missing real-provider/video evidence. Completion counts are task bookkeeping, not predicted grading points.

For the full clause-by-clause assignment audit, per-component metrics/rationale and CRISP-DM mapping, see [assignment_audit.md](assignment_audit.md). The complete timed recording plan and spoken English text are in [video_narration.md](video_narration.md).

| # | Task | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Define custom problem, scope, criteria, resources and risks | Done | requirements.md |
| 2 | Inspect the paper and existing public data before synthetic cases | Done | docs/data.md, data/source_inspection.json |
| 3 | Prepare a traceable normalized corpus with explicit unknowns | Done | data/jobs.json, data/manifest.json, scripts/prepare_data.py |
| 4 | Parse searchable PDF/TXT and extract a local evidence-backed profile | Done, baseline limits documented | src/jobmatch/extraction.py, extraction cases/results |
| 5 | Review profile, confirm preferences and filter known constraints | Done | app.py, core/UI tests |
| 6 | Rank against a lexical baseline and provide grounded results/exports | Done | search.py, export.py, fixed-pool evaluation, artifacts/demo |
| 7 | Integrate a genuine internet source and preserve freshness/URLs | Done | live DOU adapter, retrieved snapshot, source checks |
| 8 | Prepare OpenRouter schema integration and visible error handling | Done at contract level | llm.py, mocked HTTP tests, .env.example |
| 9 | Evaluate components and interpret results/failures | Done for local prototype; provisional labels | docs/evaluation_local.md, artifacts/evaluation_local.json, tests |
| 10 | Manage the coding assistant with persistent instructions/custom skills | Done | AGENTS.md, .agents/skills, docs/assistant_workflow.md |
| 11 | Supply setup, diagram, CRISP-DM report, runbook and source package | Done | README, docs/report.md, docs/architecture.md, packager, dist |
| 12 | Run and evaluate genuine OpenRouter inference | **Partly complete: real CV checks and Ling benchmark done; NVIDIA benchmark pending** | docs/live_validation.md; private CV results in ignored runs/ |
| 13 | Record and submit the personal demo <=10 minutes | **Pending** | docs/demo_script.md is ready; recording not created |

**11 of 13 preparation tasks are complete; 1 is partial and 1 is pending.** Actual live checks now expose provider failures and weak role sensitivity in current-feed ranking. NVIDIA passed one CV extraction, but its full reference evaluation was not started after a network-execution rejection. Item 13 is an explicit assignment deliverable. Independently review labels and the real-CV shortlist before making stronger quality claims; a technically running workflow is not proof of useful recommendations.

## General assignment mapping

| Requirement | Evidence / current state |
| --- | --- |
| G-01 working useful prototype | Local input-to-export flow and UI tests complete; live source integrated |
| G-02 components/data flow/calls/walkthrough | docs/architecture.md complete |
| G-03 existing data and preparation | docs/data.md and source hashes complete |
| G-04 CRISP-DM applied | Six phases, decisions and collection iteration in docs/report.md |
| G-05 assistant instructions and custom skills | Files and recorded actual application in docs/assistant_workflow.md |
| G-06 each-component evaluation | Local/contract evidence complete; live model quality pending, independent labels limited |
| G-07 source/setup/report/diagram/results | Included in project and source-package generation |
| G-08 <=10-minute video | Script prepared; actual video pending |

J-01…J-09 map to the component evidence in the short report. J-10 now has mocked and real inference checks, including negative findings; comparative NVIDIA quality remains unmeasured. No maximum score is guaranteed. The rubric is system understanding 4, prototype 4, evaluation 4, assistant management 3; your actual explanation, evidence quality and instructor judgment determine the result.

## Next steps in execution order

1. Open the app, run the synthetic scenario and inspect the three role shortlists/unknowns. Review provisional relevance grades without looking at rank order; record any human adjudication as a new benchmark revision.
2. When ready, configure a key locally, choose a currently free schema-capable fixed model and run `scripts/evaluate.py --mode openrouter`. Inspect extraction failures, actual model/settings and quota limits. Compare extraction separately with the saved local results.
3. Record your personal <=10-minute walkthrough using the prepared script, including component limitations and assistant controls. Add the actual recording to the course submission.
4. Regenerate the source archive after intentional changes and submit code/report/video. No external publication or course upload is performed automatically.
