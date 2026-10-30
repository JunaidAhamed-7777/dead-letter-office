# Validation record

## Automated checks actually run

- Clean-source reinstall: a fresh Python 3.12 virtual environment installed `requirements.txt`, an extracted source package ran without the prepared `.vendor` directory, and all **15 tests passed** using a copied, hash-verified local model cache. See `evidence/clean-source-tests.txt` and `evidence/clean-install.txt`.
- `python -m unittest discover -s tests -v`: **15 tests passed**. Real ONNX inference, not mocked embeddings. See `evidence/unit-tests.txt`.
- `python scripts/evaluate.py`: completed with socket connections blocked; ranking and selected-source results saved. Synthetic development evaluation, not general accuracy.
- Independent local HTTP probes: **19/19 passed**; see `evidence/candidate-02-http-probes.json` and the full audit `evidence/REPORT-02.md`.
- `node --check web/app.js`: passed.
- `python -m compileall -q archive.py server.py scripts tests`: passed.
- Official frontend-design-premium static auditor, strict mode: **0 findings** in `evidence/premium-audit.json`. The auditor is a build-time review tool, not included as an application dependency.
- Corpus validation: 12 letters / 36 unique passage IDs; valid cross-references; each original passage 30–65 words.
- Pinned model artifacts downloaded through ordinary HTTPS; full model SHA-256 matches the upstream artifact. Runtime rechecks its model/tokenizer hashes.

## Browser checks

The build's Playwright launch could not run in the restricted tool environment (browser executable/sandbox socket limitations). `tests/browser_check.py` is supplied as a reproducible future test; it is **not** represented as executed here.

Interactive checks in the connected browser verified the real localhost UI: lighthouse search, all returned quotations, editorial conflict explanation, source-letter open, and close. It found a real Back-navigation defect: the view changed while a letter dialog stayed open. `showView()` now closes open dialogs and restores focus to the destination navigation control. A subsequent browser check retested that exact Back flow: the letter closed and Ask view returned. Catalogue navigation was also checked. Mobile, error/retry, storage, and browser-network checks were not executed, and are not claimed.

The official DESIGN.md package linter was unavailable in the tool environment's cache. The project design/interaction contracts and runtime CSS tokens were inspected, and the strict project audit passed; this is not a WCAG conformance certification.

## Retrieval evidence and limitations

- Original results are preserved; development selection is documented rather than renamed “held out.”
- Candidate 01 blind audit: 38 cases, zero literal-quote/citation integrity errors, but real ranking and source-selection misses. See `evidence/independent-candidate-01.json`.
- Candidate 02 repairs source-selection and incidental-conflict behavior. Previously exposed cases are now regression data. The new 18-case independent smoke returned all required evidence on 12/12 answerable cases and gap evidence on 2/2 missing-fact cases, with zero citation errors. Only 1/4 hard out-of-domain cases abstained; related but inapplicable quotations remain a known failure. See `evidence/independent-candidate-02-smoke.json`.
- No human-review feedback, independent benchmark, or real-person testimony is invented.

## Deliberately unverified or absent

Validation was performed locally before publication. No Windows/macOS setup, assistive-technology audit, full browser matrix, concurrent-load testing, user-upload flow, or production security assessment is claimed.

## Requested demo media

The 78-second `docs/media/demo.mp4` is actual browser footage captured through CUA, with application-only cropping and external captions. `MASTER.gif` and four feature GIFs are derived from it. No UI result was reconstructed or changed. Capture/editorial notes are included. The raw desktop recording is excluded from the source bundle.
