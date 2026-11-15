# Data Understanding and Preparation

## Sources checked before synthetic additions

The supplied paper, [Drushchak and Romanyshyn, UNLP 2024](https://aclanthology.org/2024.unlp-1.2/), describes a historical recruitment corpus. [The authors' source page](https://lang.org.ua/uk/produkty/datasety/recruitment-datasets-djinni/) and [Ukrainian job dataset card](https://huggingface.co/datasets/lang-uk/recruitment-dataset-job-descriptions-ukrainian) identify the data and MIT license. The Ukrainian jobs subset is 27,461 records in the paper; the full bilingual corpus contains 169,358 jobs and 234,480 candidate profiles. Only job descriptions are needed here. The data covers 2020–2023, not today's open positions. The paper is a dataset reference, not a requirement to process its full size or reproduce its research experiments.

The dataset has **no candidate-to-job relevance, interview or hired labels**. A CV corpus alone would not supply those labels. We therefore use existing real vacancies for retrieval and a small separately labeled diagnostic reference. Synthetic CVs avoid collecting private CVs. The chronological evidence is raw-page cache timestamps/source inspection before `evaluation/` reference creation; no synthetic job corpus replaces the public-data inspection.

| Resource | Actual use | Identity/limits |
| --- | --- | --- |
| Ukrainian Djinni jobs on Hugging Face | 1,000 real rows; normalized archive in `data/jobs.json` | MIT per publisher; source IDs retained, original job URLs absent |
| DOU official [RSS feed](https://jobs.dou.ua/vacancies/feeds/) | 50 genuinely retrieved entries, saved in `data/dou_snapshot.json`; separate live fetch supported | A public recent window with original URLs; no open redistribution license is asserted for DOU content |
| Supplied CRISP-DM article / [source](https://www.datascience-pm.com/crisp-dm-2/) | Process structure and task checklist | Methodology reference, not evaluation data |
| OpenRouter [free collection](https://openrouter.ai/collections/free-models) / [schema docs](https://openrouter.ai/docs/guides/features/structured-outputs) | Dynamic free-model discovery and structured extraction contract | Usage rank does not prove quality; live inference deferred |
| Synthetic CV cases | 4 development and 8 held-out extraction cases | AI-authored diagnostic facts, not independent human labels |
| Judged real-job pool | 16 public descriptions × 3 synthetic role profiles = 48 relevance judgments | Provisional AI-authored description-based judgments; human review pending |

Keep source attribution with the public sample. DOU snapshots are local academic evaluation artifacts; original employer text and links retain their source attribution. Do not infer a content license from public accessibility.

## Sample inspection

Ten 100-row pages use fixed offsets `0, 1000, 2000, 3000, 4000, 4500, 5000, 10000, 15000, 20000`. These are convenient, category-enriched slices of a largely title-ordered dataset. They are **not random, balanced or representative** of the Ukrainian market. The original five-page/500-row slice had just one Data Analyst-category record and no Data Engineer/Data Science-category records. Data Understanding sent the process back to collection: adding title ranges produced 59 Data Analyst, 4 Data Engineer and 18 Data Science records. Those categories themselves can be wrong: e.g., a 1C Developer is labeled DevOps and a dashboard/BI role can be labeled Data Engineer.

Observed final archive properties: 1,000 unique IDs, 1,000 nonempty descriptions, all language tags `uk` (some descriptions mix languages), no duplicate IDs/exact normalized content removed, 382 unknown English levels. Every archived row lacks structured city/remote/Ukraine eligibility and original application URL. Experience metadata is present for every sample row but is coarse; it can disagree with full text. Ukrainian provenance is not proof of current work eligibility in Ukraine.

RSS snapshot retrieval: `2026-11-15T16:07:13.959259+00:00`; 50 entries and 50 distinct genuine URLs. The title-based location parser identifies 23 entries with a recognized Ukrainian location, 23 with unknown Ukraine eligibility, and 4 explicitly foreign-only entries. These are parser outputs, not independently verified geographic truth. Experience/English minima stay unknown for this feed. The feed can contain foreign roles and does not cover every priority direction at every moment.

## Schema and transformations

Raw Djinni fields are `Position`, `Long Description`, `Company Name`, `Exp Years`, `Primary Keyword`, `English Level`, `Published`, `Long Description_lang`, `id`, `__index_level_0__`.

1. Select Ukrainian job descriptions; exclude the CV corpus because the user supplies the CV and no linked outcomes exist.
2. Strip markup/scripts/styles and normalize whitespace. Reject missing title/description/ID. Retain employer/source/date and original UUID with a `djinni:` namespace.
3. Convert `no_exp` to 0 and `Ny` to N. Coarse historical English values map `basic/pre/intermediate/upper/fluent` to `A1/A2/B1/B2/C1`; this is an approximate application convention, not validated CEFR equivalence. Description contradictions need review.
4. Construct dictionary skill mentions using exact boundaries/aliases. They support retrieval/explanations; they do not distinguish mandatory, optional or negated mentions.
5. Deduplicate by ID and hash of case-folded title/company/description. Mark every archive record historical; retain null unknowns. No invented URL, country or remote status.
6. Normalize RSS separately, validating link host/path, stripping tracking query strings, preserving feed dates and deriving only limited title-based location hints. Do not merge archive and current-window claims.
7. Serialize exact UTF-8/LF bytes and record SHA-256 in `data/manifest.json`. The loader rejects changed bytes. `source_inspection.json` records raw-page URLs, hashes and cache timestamps. This helps detect revision changes; it does not prove source truth.

Current corpus SHA-256: `2eecaa03b92ab2814b0dca1ee107b6f87efd34f70f8e19d1e64a8b1397d84f45`. The manifest is authoritative if a new revision is deliberately prepared.

## Reproduce / refresh

Default run/evaluation uses included snapshots and needs no network. With internet, `python scripts/inspect_sources.py` reuses existing raw files or downloads missing pages/feed, then `python scripts/prepare_data.py` verifies and normalizes them. Raw caches are excluded from submission. If refreshing sources intentionally, move the specific old cache to a backup first, rerun collection/preparation, inspect differences, version the manifest and re-annotate changed descriptions. The script refuses a source hash mismatch, and the evaluation refuses changed judged descriptions.

Sampling more data may improve coverage; it cannot create relevance ground truth. Expand roles and independently review annotations before making broader quality claims.
