# JobMatch UA: Short CRISP-DM Report

> Status update: this report describes the initial local iteration. Subsequent authorized live checks, the successful single-CV NVIDIA extraction, failed Ling/ERNIE attempts and observed ranking weaknesses are documented in [live validation](live_validation.md). That update supersedes the original no-key/pending-live statements below; it does not establish independently reviewed model quality.

## 1. Business Understanding

Problem: a candidate manually compares a CV with many vacancy descriptions. The agreed prototype produces a traceable shortlist for Ukrainian-market **Data Engineering, Data Analytics and AI/ML Engineer** roles. Inputs are a searchable PDF/TXT CV and confirmed preferences; outputs are ranked retrieved jobs, genuine source links when present, explicit unknowns and portable reports. It does not apply to employers. Experience must be read from the CV, not assumed to be Junior.

The assignment permits another NLP idea (page 2). Requirements specific to its BA or recruiter examples do not automatically become requirements for this candidate-oriented system. The chosen workflow combines extraction, user clarification, constraints, retrieval and grounded reports. Scope/criteria are in `requirements.md`; execution sequence is in `docs/plan.md`. Resources are a local CPU, an AI coding assistant, public text sources and an optional OpenRouter key. The author explicitly requested preparation without a key and deferred live inference.

Business success would mean a useful shortlist with less manual comparison and no misleading source claims. Technical targets are source/quote integrity, zero controlled explicit-filter violations, skill micro F1 >=0.85 on the starter reference, and a measured baseline comparison. User time savings and hiring outcomes are not measured. The timebox motivated one feed, 1,000 archive rows, no OCR, no model training from scratch and no public deployment. External API/free capacity and sparse/old metadata are the main operational risks.

## 2. Data Understanding

The provided recruitment paper and publisher links were checked before synthetic cases were created. The Ukrainian Djinni job subset is a good domain source, but historical and unlabelled. Raw rows were inspected through the Hugging Face rows API and the official DOU RSS was actually retrieved. `data/source_inspection.json` contains exact URLs/timestamps/hashes; `docs/data.md` documents the schema and quality.

An initial five-page slice had poor priority-role coverage: one Data Analyst category and no Data Engineer/Data Science categories. This triggered a return to collection. The expanded sample has 59/4/18 respectively, yet remains biased and sparse. Source category is unreliable as a relevance label. All 1,000 archive records lack structured Ukraine/remote status and application links; 382 lack English level. The DOU snapshot has 50 real links but is only a recent feed window. Neither source verifies that a job is still open or that a particular candidate can be hired.

## 3. Data Preparation

We selected public job descriptions and excluded public CV profiles because the user's CV is the input. Text was cleaned, missing essential fields rejected, IDs/source/dates preserved, vocabulary skills derived, experience/coarse English metadata converted, and duplicate IDs/exact normalized content checked. Missing country/city/remote/URLs remain unknown rather than being invented. RSS links are restricted to actual DOU vacancy patterns and tracking queries are removed. Archive and feed sources are kept visibly separate.

The saved UTF-8 corpus has 1,000 unique records and a byte-level manifest. Hash checks detect source changes. Twelve clearly synthetic extraction cases (4 development, 8 held-out) and a fixed 16-job/3-profile judged pool were created after source inspection. Label rationale and limitations are in `evaluation/README.md`: all relevance judgments are provisional AI-authored references; independent human review is pending. This distinction prevents treating synthetic or heuristic labels as hiring truth.

## 4. Modeling

The architecture diagram/contracts in `docs/architecture.md` explain each stage. Local extraction uses a small auditable bilingual skill dictionary, explicit year mentions and explicit CEFR patterns. OpenRouter provides an optional real JSON-schema extraction adapter with source-quote validation, capability/zero-price preflight and visible errors. It has not been called with real credentials. Model identity is configured explicitly; no usage ranking is interpreted as quality evidence.

The user reviews extraction and confirms role/location/work format/unknown policy before search. Known metadata contradictions reject a vacancy; unknown fields remain visible and can be excluded. TF-IDF character 3–5 grams form the lexical baseline. The main ranker adds query role/skill terms and combines similarity (0.65) with recognized job-skill coverage (0.35). These weights were fixed without tuning on the judged pool. No supervised training is needed. Explanations pair exact CV/job mentions and label other job skills as unmentioned, not a proven deficiency. Streamlit supplies the interface and three exports.

## 5. Evaluation and decision

The actual reproducible results are in `docs/evaluation_local.md`, with per-case errors/top ranks/timings/code and dataset fingerprints in `artifacts/evaluation_local.json`. Tests cover operational contracts separately from semantic references.

| Component | Evaluation evidence / metric | Practical limit |
| --- | --- | --- |
| PDF/TXT parsing and redaction | Searchable PDF/TXT, blank/corrupt/unsupported/short/invalid-UTF8 fixtures and contact tests | No OCR, encrypted/layout-heavy PDF benchmark |
| Profile extraction | Held-out skill P/R/F1 0.939/0.969/0.954; years 7/8; English 8/8 | Eight synthetic cases, shared author bias |
| Profile validation | Invalid quotes rejected; exact-span integrity recorded | Does not detect negation or false entailment |
| Ingestion/normalization | 1,000 unique nonempty archive records, 50 genuine distinct RSS links, exact byte hashes; URL rejection/dedup tests | No exhaustive corpus/manual location audit |
| Preference collection | Gate blocks unconfirmed searches; actual Streamlit form-flow tests | Limited fixed form, no conversational ambiguity resolution |
| Constraint filter | Five controlled explicit contradictions rejected; unknown inclusion/exclusion and remote/city behavior checked | Known source metadata only; some metadata contradicts descriptions |
| Ranking | Same 16-job judged pool, 3 queries; macro P@5 0.467 lexical vs 0.600 skill-aware; nDCG@5 0.827 vs 0.867 | Provisional judgments, sparse ML, no significance/generalization claim |
| Explanations | 26/26 valid CV/job quote pairs in 10 archive recommendations; tamper validation | Positive semantic relevance needs human review |
| Export/end-to-end | JSON/CSV ID/order agreement, Markdown/JSON/CSV generation, formula escaping; actual local workflow/UI tests | Synthetic CV; timings are one local CPU run |
| OpenRouter | Mocked success, quota/paid model/malformed output/unsupported evidence checks; missing-key check | Contract evidence only; real response quality/latency pending |

The local skill F1 target is met on the starter reference. That does not mean reliable extraction on arbitrary CVs: the measured negation case produces false Java/Python skills; per-skill years become an incorrect total; OpenCV is missed by the dictionary. Exact quotes can be entirely valid while those facts are semantically wrong. Profile review remains necessary. A future version should add negation/total-experience handling on separate development material and collect new held-out cases before claiming improvement.

The skill-aware ranker improves the average on this diagnostic pool, but ML nDCG slightly decreases (0.886 to 0.881) and ML P@5 remains 0.2 because only one strongly relevant ML vacancy exists. This is a coverage limitation, not evidence of a 20% hiring probability. Source expansion with several relevant ML/engineering roles and human adjudication comes before more parameter tuning. Cross-language semantic retrieval and finer requirement extraction are potential later improvements.

Process review: data collection was corrected after role-coverage inspection; encoding/fixture-schema issues were caught and corrected by running tests; the UI clears/rejects stale results after CV/source changes. The held-out semantic cases and ranking weights were not edited to remove observed failures. Based on this evidence, the local prototype is suitable for an academic demonstration with manual review. Production usefulness and live model quality are not established.

## 6. Deployment, monitoring and retrospective

Local delivery includes source, sample data, an install specification/tested versions, runnable UI, evaluation scripts, machine-readable results, architecture, assistant instructions/skills and a submission packager. The launch health artifact records an actual HTTP health check; UI tests exercise the example/confirmation/search/error paths. Public hosting is optional and was not needed. `docs/runbook.md` covers source refresh, model changes, failure recovery and privacy-aware traces.

Before submission, independently inspect the provisional labels and several shortlist explanations, run the deferred live OpenRouter evaluation if demonstrating that mode, then record the required <=10-minute personal walkthrough using `docs/demo_script.md`. No recording or real API performance has been fabricated. The author should understand why each component exists and why imperfect scores occur; the rubric is not satisfied by simply reading a success message.

The key lesson from this CRISP-DM iteration is that data provenance/coverage and transparent unknowns matter as much as adding an LLM. The persistent `AGENTS.md` and two custom development skills helped enforce source checks, component evaluation and honest pending-work tracking. They also exposed the limits of self-authored evaluation. A larger independently reviewed benchmark and real user usefulness study are the next iteration, after the runnable submission is demonstrated.

## References

- [Djinni dataset paper and citation](https://aclanthology.org/2024.unlp-1.2/); [publisher/license](https://lang.org.ua/uk/produkty/datasety/recruitment-datasets-djinni/).
- [CRISP-DM article supplied by the author](https://www.datascience-pm.com/crisp-dm-2/); [DOU public feed](https://jobs.dou.ua/vacancies/feeds/).
- [OpenRouter free models](https://openrouter.ai/collections/free-models); [structured-output API](https://openrouter.ai/docs/guides/features/structured-outputs).
