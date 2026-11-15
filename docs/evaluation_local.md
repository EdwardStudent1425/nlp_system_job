# Measured Evaluation Results

Run: 2026-11-15T21:26:41.956282+00:00. Extraction mode: local.

Synthetic reference cases and provisional AI-authored relevance judgments are diagnostic benchmarks. Independent human review is pending.

| Component | Measured result | Limit |
| --- | --- | --- |
| Extraction | Held-out skill P/R/F1 0.939/0.969/0.954; 8 cases | Small synthetic, vocabulary-dependent |
| Profile facts | Years accuracy 0.875; English accuracy 1.000 | Exact field match, not proficiency verification |
| Ingestion | 1000 archive records, 50 retrieved RSS records | Not exhaustive/current availability verification |
| Explanations | 26 valid paired spans in 10 archive results | Quote presence does not prove semantic entailment |
| Export | 3 formats; ID/order consistency True | Synthetic demonstration CV |
| End-to-end | Index 2.430s; ranking 1.587s | One local CPU run; excludes upload/API |
| Contracts/UI | 37/37 automated tests | Includes mocked provider, not real LLM calls |

## Retrieval on the same fully judged 16-job pool

Relevant means grade >=2. Precision@5 uses denominator 5; nDCG uses gains 2^grade-1. Macro averages over 3 queries.

| Query | Method | Precision@5 | nDCG@5 |
| --- | --- | --- | --- |
| analytics | lexical | 0.800 | 0.784 |
| analytics | skill-aware | 1.000 | 0.843 |
| engineering | lexical | 0.400 | 0.812 |
| engineering | skill-aware | 0.600 | 0.878 |
| ml | lexical | 0.200 | 0.886 |
| ml | skill-aware | 0.200 | 0.881 |
| Macro | lexical | 0.467 | 0.827 |
| Macro | skill-aware | 0.600 | 0.867 |

## Observed extraction failures

- test-negative: extra=['java', 'python'], missed=[], years predicted/reference=None/None, English correct=True.
- test-ambiguous-years: extra=[], missed=[], years predicted/reference=3.0/None, English correct=True.
- test-vocabulary: extra=[], missed=['opencv'], years predicted/reference=4.0/4, English correct=True.

## Interpretation

The rule extractor recognizes listed terms but does not understand negation, unlisted skills or per-skill versus total experience. Profile review is required. A high span-integrity score only establishes provenance.
Data-engineering/ML pools are sparse. Matching tools can promote adjacent support/automation roles; character n-grams provide weak Ukrainian-English semantic alignment. The skill-aware method must be judged by the numbers above, not its name. No weights were tuned on this pool.
Filtering is evaluated with controlled contradictions and unknown cases in tests/test_core.py. The RSS experience/English minima remain unknown; coarse historical metadata can disagree with description text. Broad job-market suitability, user time savings and hiring outcomes were not measured.
In local mode, extraction uses no provider. OpenRouter-mode runs contain actual generation attempts and case-level failures; HTTP mocks alone verify only the adapter contract. Independent annotation, a larger separately frozen benchmark and actual provider evaluation remain the next quality gates.
