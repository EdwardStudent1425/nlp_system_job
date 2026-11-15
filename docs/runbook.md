# Local Delivery and Maintenance

## Launch and recovery

Use the README commands from the project directory. A missing dependency means the install step needs repeating in the selected environment. A corpus hash error means bytes changed: restore the matching snapshot/manifest or deliberately prepare and evaluate a new revision. Do not silently rewrite hashes to conceal the difference.

If live RSS fails, the UI reports failure and retains the existing visibly labeled source. Choose the dated saved DOU snapshot or historical dataset to continue. Refreshing a source does not make old search results current: rerun the search. A feed item may no longer accept applications even if its link resolves.

If OpenRouter has no key/model, use explicit local mode. If selected live mode fails, inspect configuration/capability/quota/transport and ignored `runs/` traces; the app will not silently substitute baseline output. A different free model/provider may change behavior even at temperature 0. Choose a fixed currently free schema-capable model, version the choice and repeat the reference evaluation. Catalog support is a preflight check, not a guarantee that the eventual serving endpoint succeeds. No retries or paid fallback are made automatically.

## What to monitor

- Before each demo: tests/evaluation, corpus hash, number of usable records, sample links, archive/snapshot label and source timestamp.
- On each data refresh: missing fields, duplicate IDs/text, category/role coverage, changed judged descriptions, country/remote ambiguity and site/feed contract changes. Refresh frequency for a real job seeker should be user-driven per search; no scheduler is implemented.
- On each extraction change: skill precision/recall, years/English exact match, span integrity, negation/unknown errors, schema/transport failures and live latency/token usage. Do not claim deployment quality from mocked provider tests.
- On each ranking change: the same fixed pool plus a new separately reviewed set, per-direction results and hard negatives. Broad usefulness requires manual shortlist review with a sanitized real CV.

`runs/` uses hash-only traces for real configured extraction attempts: requested/actual model, provider if returned, prompt/schema/input/output hashes, settings, timestamp, latency and usage/error type. Raw CVs, model responses and API keys are not logged. Hashes support correlation and are not anonymization guarantees. The app holds CV/results in session memory. Downloaded personal reports contain extracted facts and quotes; keep them private. No persistent database or upload directory is created by the app.

No automatic alerting, retention service, production access control or hosted deployment is implemented. For local coursework, close the server when finished and manually remove private `.env`, runtime logs and downloaded personal reports before sharing. The packager uses an explicit source/data/doc allowlist and excludes runtime secrets/environments.

## Review / handoff

`docs/submission_checklist.md` identifies completed and pending items. Re-run `scripts/evaluate.py --with-tests` after a meaningful change; it records code/data/reference hashes and current measured timings. `scripts/package_submission.py` creates a reviewable archive and file-hash manifest. Review the archive listing, record the personal <=10-minute demo, and submit the actual code/report/video according to the course platform. The project does not publish or submit files externally.
