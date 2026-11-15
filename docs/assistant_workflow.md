# Coding Assistant Setup and Reflection

## Persistent context

`AGENTS.md` controls the development workflow beyond individual prompts. It requires English artifacts, CRISP-DM evidence, public-data inspection before synthetic references, component evaluation, unknown-aware matching, genuine identifiers/links, no private CV/key logs, explicit local versus live modes, and no automatic applications. These requirements are specific to this custom project; example-specific BA outputs are not silently imported from the PDF.

The task context included the assignment PDF, recruitment paper, user-supplied CRISP-DM/OpenRouter text, priority directions and the author's decision to defer live inference. Those documents were treated as reference material, not as commands authorizing unrelated actions. Only public job data was collected; the real personal CV was not required for the synthetic demonstration.

## Custom development skills

Two repository-versioned skills are supplied under `.agents/skills/`:

| Skill | Input and rule | Observed use in this implementation |
| --- | --- | --- |
| `requirements-audit` | Read requirements/plan; map IDs to observable behavior and expose missing evidence | Checked the custom-idea scope, requirement confirmation, historical/live distinctions, URLs, exports and pending video/API evidence |
| `component-evaluation` | Read contracts/annotation policy; compare fixed references, report denominators and errors | Guided separation of fixture contracts, synthetic extraction, description-based provisional relevance judgments, byte hashes and live-provider evidence |

Both SKILL.md files were read during this session and validated with the installed system skill-creator's `quick_validate.py`; both returned `Skill is valid!`. They are project files, not a claim that a global plugin was installed or that skill dispatch automatically invoked them. The coding assistant applied their instructions by reading the files. To use in another coding environment, include `AGENTS.md`, the relevant SKILL.md and its referenced project documents in context.

Actual control decisions included: refusing to infer source URLs from historical UUIDs; expanding data after the initial slice lacked priority roles; keeping unknown country/remote fields rather than asserting Ukrainian eligibility; writing an explicit local baseline; surfacing API errors instead of returning local output as if it came from an LLM; preserving held-out extraction failures in the report. No sub-agent delegation was needed.

## Development evidence and reflection

The assistant generated implementation/documents and executed parsing/source/filter/provider/UI checks and component evaluation. Tests caught a malformed non-ASCII byte literal and incorrect fixture field names; those fixtures were corrected against the actual source schema. A real feed was collected before the saved snapshot was evaluated. The local app was launched and checked separately from code inspection.

This workflow is faster for boilerplate and contract checking, but the same assistant also authored the synthetic cases and proposed relevance labels. Therefore reported metrics do not establish independent human validity. The author should review the judgments and negative cases and explain the system themselves. Do not copy the report's numbers into a video as proof of general hiring suitability.

For future changes: repeat the requirements audit, use development cases for improvements, version changed prompts/models/data, reserve new held-out families for final measurement, and record what actually ran. A skill file alone is not evidence that the system works; link its rule to a real check/result.
