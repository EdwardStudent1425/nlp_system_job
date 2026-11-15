# JobMatch UA Development Instructions

Build a job-search assistant for candidates in Ukraine. Project artifacts and code are English; explanations to the author may be Ukrainian. The assignment PDF is reference data, not permission for unrelated actions.

Follow CRISP-DM. Record actual evidence for business understanding, source inspection, preparation, modeling, evaluation, and local delivery. Inspect existing public data before constructing synthetic fixtures. Never present archived jobs as currently open or synthetic labels as independent human judgments.

Evaluate each component: CV parsing/extraction, source ingestion/normalization, preference filtering, ranking, explanations, and exports/end-to-end behavior. Distinguish automated contract checks from semantic quality. Split evaluation cases by profile/family and keep tuning separate from held-out assessment.

Use only retrieved job identifiers/URLs. Explain matches using explicit CV/job evidence. Missing information is unknown, not a confirmed qualification or restriction. Ask for preferences before final recommendations. Preserve source/license/retrieval date, corpus hashes, model/prompt versions, and errors. Do not expose CV contents or API keys in committed logs.

OpenRouter is for structured CV extraction and optional explanation, not an automatic internet search engine. Keep an explicit labeled local extraction baseline, lexical ranking baseline, and live/offline source modes. Do not claim live API quality without real calls. Do not send applications or contact employers.

Read project skills under `.agents/skills/` when relevant; record their actual use. Keep scope small: searchable PDF/TXT CV, Ukrainian/English job text, one live source and a reproducible historical corpus. No training from scratch, OCR, or autonomous application submission is required.
