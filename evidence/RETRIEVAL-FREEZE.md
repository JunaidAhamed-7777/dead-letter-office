# Retrieval freeze

Configuration frozen for independent holdout evaluation on 2026-10-30.

- Pinned `all-MiniLM-L6-v2`, official full ONNX weights; no fine-tuning.
- Index string: `{title}. Letter from {author} to {recipient}. {paragraph}`.
- Rank score: 0.5 × neural cosine + 0.5 × TF-IDF cosine.
- TF-IDF: English stopwords, (1, 2) ngrams, sublinear term frequency.
- Inclusion: first three ranked passages, neural cosine ≥ 0.30 and ≥ first-ranked cosine − 0.16; catalogued conflicting counterparts added.
- Strong related-match threshold 0.48; not answer certainty.
- Exact quotes only. Conflict links remain editorial. No query-specific behavior.
- Source and evaluation files remain unchanged.

The 32 original questions are DEVELOPMENT data: after seeing their failures, we evaluated all three index-context choices × eleven blend weights. Every candidate is reported in `development-tuning.json`. We selected title/byline context with an even neural/lexical blend, maximizing development top-3 hits then top-1 accuracy and reciprocal rank. A separate reviewer owns unseen holdout cases. The holdout will not be used to retune this freeze.

The original pre-tuning result remains in `development-initial.json`. This is a small fictional demo, not a general question-answering benchmark.

## Candidate 02 (final)

Frozen source: `archive.py` SHA-256 `9f20f982823cd49103c01ded56772aa8b0228a008c068d062f323a6a5bea9ec3`.

Ranking and source data did not change. Inclusion now uses hybrid rank ≥ 0.12 and within 0.16 of the first rank, instead of filtering on cosine alone. Conflict expansion is limited to primary accounts within 0.06 of the first rank, and the summary names source-level disagreement. Deterministic narrow live-service and transaction scope checks are explicit and separate from ML. The existing missing-fact limitations remain.

A fresh 18-case smoke set was run only after this freeze. Its failures were disclosed, not used to append further query exceptions. Candidate 01's 38 cases are now regression data. No more retrieval changes followed the fresh result.
