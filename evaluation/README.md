# Annotation and Evaluation Policy

Public vacancies were inspected before creating these references. Neither the historical dataset nor RSS supplies CV-job match labels. Current labels are **AI-authored provisional references**, not user-confirmed hiring truth or independent human judgments.

## Extraction references

`extraction_cases.json` freezes 4 development cases and 8 separately authored held-out cases before the first metric run. Development covers simple facts/aliases/boundaries/unknowns; held-out cases add negation, per-skill experience, unseen vocabulary and date-only CVs. There is no supervised training; this split separates reference checks from cases available for routine development. Shared vocabulary and the same author still limit independence. The held-out cases were not tuned after seeing their measured errors.

Annotate technical skills explicitly asserted as known/used by the candidate. A negated skill is not positive. Use lowercase canonical names; preserve a skill such as `opencv` even if the current dictionary cannot extract it. Count total professional experience only when explicit and unambiguous; per-skill counts and employment dates alone do not establish a total. English is an explicitly stated CEFR level; writing the CV in English is not evidence of proficiency.

Skill micro precision/recall/F1 aggregate TP/FP/FN over cases. Years/English use exact-value accuracy including correct nulls; a failed extraction is an incorrect case and its reference skills count as missed. Quote checks test exact span presence on successful outputs and are reported separately from semantic correctness. Empty labels must not inflate skill F1 by treating true negatives as skill predictions.

## Ranking references

`ranking_pool.json` freezes 16 genuine archive jobs and 3 synthetic profiles for the user's priority directions. Full descriptions were read before either ranker was scored. The fixed pool deliberately mixes analytics/engineering/ML and unrelated work, using source categories only for initial sampling, not automatic relevance labels. All 48 pairs are judged, with a rationale stored by vacancy. Judgments compare **work/task alignment**, not the number of matching dictionary skills or the algorithm's score.

Grades: 0 different work; 1 adjacent/weak; 2 relevant with material gaps; 3 strong task alignment. Precision@5 defines relevant as grade >=2 and divides by 5 even if fewer results return. nDCG@5 uses gain `2^grade-1` and discount `log2(rank+1)` with ideal order from the same fully judged pool. Average equally over 3 queries. Both rankers use the same input records/filters; individual top results and rejection reasons are recorded. Unjudged records in the 1,000-job demo are **not automatically negatives**.

This reference is a sanity check with author bias. It has one strong ML vacancy, so ML Precision@5 cannot exceed 0.2 on this pool; nDCG measures whether that strong item is near the top. Do not compare these numbers with an unrelated benchmark or call them general search accuracy. Weights were fixed before this metric run, and no confidence/significance claim is made for three queries.

## Independent review procedure

Have the project author and preferably a second person inspect descriptions and all grades without seeing rank order. Record reviewer/date, disagreements and adjudication. Do not overwrite v1 to improve results: create v2, freeze its hash, use development material for changes and reserve new profiles/job families as a new held-out set. Add multiple genuinely relevant ML/engineering jobs and hard negatives; separate duplicate/reposted job families and similar CV templates across splits. Inter-annotator agreement and larger sample confidence intervals are future work.

For explanations, human review should check that each skill is asserted positively in the CV and is relevant to the job duties, not merely present in both texts. Current automatic quote integrity establishes provenance only. For constraints, annotate literal eligible/ineligible/unknown metadata; do not impute country/remote status from the website's nationality. Real business validation should assess shortlist usefulness with a real sanitized CV, manually reviewed vacancies and a timed comparison against manual search.
