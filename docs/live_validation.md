# Live OpenRouter Validation — November 15, 2026

The author explicitly authorized sending the contact-redacted test CV to OpenRouter. No Git commit, push, publication or application submission was performed. The key was read through the existing adapter and never printed. Personal PDF input, extracted profiles, current feed snapshot and any personal exports remain in ignored `cv/`, `runs/` and `exports/` directories. Public evaluation artifacts contain synthetic cases only.

## Actual observations

- The searchable PDF parsed successfully. The local rule baseline produced a false total-experience value from a statement about the duration of historical data. This is a semantic failure, not verified professional experience; do not use that count for eligibility decisions.
- The current DOU RSS was genuinely retrieved: 50 jobs with 50 source URLs; 22 parser-known Ukrainian locations, 24 unknown Ukraine conditions and 4 explicitly foreign-only entries. These are metadata-parser outputs, not independently verified eligibility.
- The author confirmed all Ukrainian cities plus remote work, with visibly marked unknown conditions, for Data Engineering, Data Analytics and AI/ML Engineer. Human review of the extracted profile and shortlist remains necessary.
- Real Ling calls authenticated and returned responses. With default reasoning, one measured response used all 2,048 completion tokens for reasoning, returned no content and reported zero cost. Strict validation rejected it.
- Reasoning was disabled only when catalog metadata explicitly advertised optional reasoning. This avoided the empty-output token-budget failure, but Ling still produced empty profiles, schema violations and unsupported evidence on some inputs.
- The frozen initial live reference run is `artifacts/evaluation_openrouter_ling_prompt_v1.json`: 12 synthetic cases, including 8 held-out cases. Of those 8, 5 passed extraction/validation; skill micro F1 was 0.512, years accuracy 0.500 and English accuracy 0.250. This is availability plus extraction performance for that exact prompt/settings, not the quality of later revisions.
- ERNIE correctly extracted the synthetic demonstration profile. It exhausted 2,048 and then 4,096 output tokens on the real CV. Its public catalog metadata advertises mandatory high reasoning, so disabling it is not assumed safe.

## Changes justified by the checks

### Recruiter evidence recovery and Streamlit hot reload

The later recruiter example exposed brittle quote validation. The adapter now recovers case/whitespace variants by locating and storing the original source span. Claims with no recoverable evidence are discarded individually and unsupported experience/English fields become unknown. The interface visibly reports discarded claims and cleared fields. A wholly unsupported nonempty skill list still fails; no evidence is fabricated and schema failures remain fatal. The prompt includes recruitment/HR skills and distinguishes technologies a recruiter hired for from personal programming skills. This supersedes the earlier all-or-nothing policy for an unsupported duplicate below. Counts of quote recovery, discarded skills and duplicate removal remain in local traces; these are transformations, not evidence of semantic accuracy.

The separate `Recommendation.job` error was reproduced with a second class named Job loaded from the same model definitions. Search and Streamlit session restoration now validate serialized record data instead of relying on stale Pydantic class identity. No schema/type check was disabled. Regression cases cover recruiter quote recovery, unsupported claims/fields, duplicates and old class identities. The local suite passes 37 tests after these fixes. No real CV/provider call was made for this patch; earlier benchmark scores describe their original code/prompt revisions.

### Repeated skill mentions in Embedded CVs

A user-reported `Duplicate extracted skills` failure led to local regression coverage with a synthetic C/C++/FreeRTOS response. The adapter now validates all original evidence before merging repeated skill names, ignoring case and surrounding spaces. It retains the first exact quote and records `duplicate_skills_removed` in its hash-only trace. C and C++ remain separate; unsupported evidence in a duplicate still rejects the output. The prompt also requests one entry per skill. This correction was tested with mocked HTTP responses, without sending the user's CV externally. Earlier live scores remain historical measurements and are not replaced by a claim of improved live quality.

The original prompt ambiguously requested the schema rather than a data instance. It now explicitly requests a JSON instance, enumerates the field names and asks for short exact source spans. Optional reasoning is disabled when supported; the default output budget is 4,096, with a bounded explicit override for controlled tests. Truncated output is rejected with an actionable error. Failure traces preserve actual model, usage, finish reason and safe validation locations/types without raw CV or model text. No silent local fallback or paid-model fallback was added.

Existing exact-quote/schema checks remain strict. A valid empty profile is not treated as successful semantic extraction. New provider regression coverage checks reasoning settings and truncation diagnostics. These changes use observed errors as development feedback; the original reference is now a regression benchmark rather than a fresh independent held-out claim for improved prompts. A new untouched reference is needed for generalization claims.

The raw private CV is not copied into public documentation or the source archive. `.env` model selection remains under the author's control; comparison scripts use explicit temporary overrides rather than silently changing it.

## Interpretation and remaining quality gates

### Final controlled CV outcome

ERNIE also exhausted an explicitly increased 8,192-token budget; it was not accepted. An explicit temporary comparison with `nvidia/nemotron-3.5-super-vl:free` returned a schema-valid profile in approximately 6.3 seconds: 29 skill entries with exact source spans, English B2 and unknown total professional experience. This establishes one successful operational extraction, not independently reviewed semantic accuracy. The configured `.env` model was not changed.

The validated NVIDIA profile was used with the author's confirmed filters against the actual current 50-entry DOU snapshot. Local reports for all three directions were produced in ignored `exports/real_cv/`. Four explicitly foreign-only jobs were rejected. The top three results were identical across all three directions and included adjacent Senior BA/QA roles; a Data Platform Engineer title was present in the source. This exposes insufficient role sensitivity, rather than merely absent source coverage. Source minimum experience/English is unknown, so senior roles can remain in the shortlist when unknowns are included. These are draft results for human review, not validated personal recommendations.

A proposed additional 12-case NVIDIA reference evaluation was not started because its network-execution request was rejected. No alternative route was used to run that denied action. The initial Ling benchmark remains the only full live synthetic benchmark; the successful NVIDIA call is a single real-CV check. Next work is explicit profile/shortlist review, role-sensitive ranking and a separately authorized comparative evaluation. No more external calls were made after that rejection.

The API connection has been demonstrated, and live evaluation has actually been performed. Catalog support for structured outputs did not establish reliable extraction in practice. Do not equate successful HTTP/JSON validation or zero billing with useful CV analysis. Review the final controlled CV outcome in the ignored private report before relying on a shortlist; broader human relevance annotation and a personal <=10-minute demo are still required for a stronger submission.

References: [OpenRouter reasoning/budget documentation](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens), [Ling model metadata](https://openrouter.ai/inclusionai/ling-3.2-flash:free), [ERNIE model metadata](https://openrouter.ai/baidu/ernie-5.5-flash-preview:free). Measured behavior above comes from the local private traces and synthetic evaluation artifacts, not model-page marketing claims.
