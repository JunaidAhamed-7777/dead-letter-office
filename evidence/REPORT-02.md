# Independent audit — candidate 02, fresh smoke + disclosed regression

## Bottom line

Candidate 02 repairs three false abstentions observed in the first audit and successfully returns all primary evidence groups for **12/12 fresh answerable smoke questions**. That is **not 100% answer accuracy**: only 6/12 have a primary answer-supporting passage ranked first, many add unrelated excerpts, and **3/4 fresh hard out-of-domain questions still return historical passages instead of abstaining**. Quotes remain exact. This is a useful, transparent fictional-archive retrieval demo, not a calibrated question-answering or current-information system.

Do not hide the fresh negative results behind the old out-of-domain set's now-perfect regression score. Do not label the 38 exposed cases “held out” in later evaluation claims.

## Exact frozen candidate

- Source copy: `/workspace/shared/ghost-audit/candidate-02`.
- `archive.py`: `9f20f982823cd49103c01ded56772aa8b0228a008c068d062f323a6a5bea9ec3`.
- Corpus unchanged: `e7c6b644e0c89d5d4209145cca3b6eeb616e85aa694a2a8f65348bb7463169f3`.
- Snapshot manifest digest: `16a554f7124b6385346a51366abfbb61b54f43e60d86ada413e41662fc74f466`; individual source/frontend/model hashes in `candidate-02-manifest.json`.
- Fresh smoke registered 2026-10-30 03:57:19 UTC, hash `f08338b0bc5d5543f36c167de03a8915f9c187b0dbabdba836801787ad707896`. Executed only after freeze, about 04:02 UTC, before questions were exposed to the builder.
- First snapshot and its complete results are preserved separately, not replaced.

### What changed

The learned model, input context and 50/50 hybrid ranking are unchanged. Selection now gates on hybrid relevance at .12 instead of neural cosine at .30. This explains the increased primary-source inclusion without a raw-rank improvement. Narrow deterministic live-service / transaction rules were added and explicitly disclosed as rules, not learned answerability. Conflict summaries now describe disagreement in the reading set rather than implying it necessarily settles the question; weaker incidental conflict links do not expand the set. The empty-result explanation now accurately refers to shortlisted passages. Frontend hash navigation closes open dialogs and moves restoration to the destination navigation control; parent owns actual browser verification.

## Fresh unseen-query smoke, 18 cases

| Category | n | Observed result |
|---|---:|---|
| Paraphrase, mostly newly queried facts | 10 | All 10 return primary evidence; 4 primary top-1 and 10 top-3 |
| Compound | 2 | Both return all required source groups |
| Missing fact | 2 | Both return explicit uncertainty evidence; one API status is still `found` |
| Hard out-of-domain | 4 | 1 correct empty result; 3 non-abstentions |

All 18 responses have exact corpus-matching quotation text, citation IDs, letter IDs and metadata. No novel fact, forecast, technical instruction, sale offer or numeric calculation was fabricated.

### Identical-context raw-rank comparison on the 12 answerable cases

| Method | Primary top-1 | Primary top-3 | All groups top-3 | MRR |
|---|---:|---:|---:|---:|
| Actual MiniLM + TF-IDF | 6/12 | 12/12 | 12/12 | .708 |
| MiniLM alone | 7/12 | 12/12 | 11/12 | .750 |
| TF-IDF alone | 5/12 | 7/12 | 6/12 | .536 |

The neural component adds useful retrieval on this set, but the hybrid is **not uniformly better**: pure MiniLM wins top-1 here. These are small, hand-authored, nonrandom same-corpus samples. They do not establish statistical generalization or production performance. The test author was aware of candidate 01's behavior, though candidate 02 was not read or executed before the new set was registered. Same corpus and same evaluator limit independence.

### Every fresh-smoke failure / shortcoming

1. **S15:** “Is the scarf at the postal counter available for me to purchase today?” returns **L11-P3**, describing the historical two-week holding period. No current stock, purchase availability or sale is supported. Status uncertain, not unknown. The generic warning is truthful but not an explicit scope refusal.
2. **S16:** “Show me how to repair the electric motor in a modern lighthouse beacon.” returns **L02-P2, L09-P3, L02-P1, L03-P1**: a historical drive-pin failure, material choice, and light-visibility dispute. No modern electrical repair instructions exist. The result is uncertain and does not synthesize dangerous instructions; it is nevertheless irrelevant to the requested procedure.
3. **S17:** “What will the harbour water level be at 9 a.m. next Tuesday?” returns **L10-P2, L02-P1, L01-P1**, historical tide/lantern/flood passages. No requested future water-level estimate exists. No number is invented, but the narrow live-data rule misses this forecast.
4. **S01:** The six-refunds answer is present at rank 3, after money in an apology and Ada's station visit. Correct evidence is included, but ordering makes the reader sift unrelated text.
5. **S04:** Blue-tea-towel toy padding is present at rank 3, after a toy reminiscence and an unrelated recovered scarf.
6. **S06:** School-performance year 1919 is present at rank 2; first quote explains preservation/headteacher custody instead of the date.
7. **S07:** Headteacher custody is present at rank 2; first quote concerns train boiler pressure.
8. **S09:** Observatory reference at noon is present at rank 2; first quote describes Nora's separate mantel clock.
9. **S10:** Reason for brass rather than iron is present at rank 3, behind mechanism failure and keeper observation, with an extra conflict counterpart. The revised “reading set includes accounts that disagree” statement is literally accurate, but the conflict is not about the metal choice and still distracts.
10. **S02:** The question asks when the keeper *said* he stopped watching; midnight is directly supplied. The visibility-conflict material is also returned, though that specific duration report is not itself contradicted. Revised copy avoids claiming question-specific contradiction.
11. **S13:** Exact error of Nora's clock is explicitly unknown in the returned passages, yet API status is `found`. User-facing caveats reduce false confidence, but this remains a relevance status, not an answerability status.

Complete rows, primary judgments, all raw ranks and full structured responses are in `candidate-02-smoke-results.json`; concise all-18 table in `candidate-02-smoke-outcomes.md`.

## Old 38 cases: explicitly a diagnostic regression

| Metric | Candidate 01 | Candidate 02 |
|---|---:|---:|
| Answerable responses with preregistered primary support | 19/24 | 22/24 |
| Answerable responses with all required groups | 18/24 | 21/24 |
| Paraphrase responses with primary support | 11/16 | 14/16 |
| Known out-of-domain empty results | 4/5 | 5/5 |
| Missing-fact responses with primary uncertainty evidence | 5/6 | 5/6 |
| Citation errors | 0 | 0 |
| Raw hybrid primary top-3 | 22/24 | 22/24 |

All three false abstentions P04/P13/P15 are repaired by selecting the hybrid-ranked passages. Remaining issues are not hidden:

- **P01:** No primary L01-P1; returned L01-P2 gives indirect train/refund evidence, plus unrelated ledger/ferry material. The wording “late service” is somewhat ambiguous, so this is reported as a strict primary-source miss, not zero useful evidence.
- **P16:** Still fails to retrieve L06-P3 explaining why the recording was preserved; now returns three irrelevant passages rather than one.
- **C04:** Correct no-arrival record L12-P1 is present, but planned-visit L10-P1 remains absent.
- **M04:** Undecided move L10-P3 present, but explicit no-later-address L12-P1 omitted.
- **M05:** Body-recovery presupposition still gets scarf/sighting passages and omits explicit no-proof-of-death L12-P1.
- **M02/M03/M06:** Missing quantities/identity/diameter continue to get API `found`, though quotes correctly say the facts are unavailable.
- **I02:** No longer expands to the keeper counterpart or declares disagreement in its summary; bird location is present. An unrelated window/witness quote remains.
- Existing explicit-conflict cases preserve both accounts; all three injection cases remain non-generative and preserve citation integrity.

The new 18 smoke cases were revealed only after execution and are now also diagnostic material. Adding new regexes for the three newly exposed negative phrases would not retroactively improve this recorded unseen result.

## Safety, privacy, and UX verification

- **Candidate 02 local HTTP probes: 19/19 passed** again; full headers/status/body results in `candidate-02-http-probes.json`. Host/Origin restrictions, static allowlist, malformed/nonobject/type/empty/oversized inputs and valid query remain correct.
- `node --check candidate-02/web/app.js` passed. No new independent browser launch was attempted after the parent requested none.
- All inference measurements were under the same Python socket-connection guard; fresh smoke load/index 699 ms, median ask 5.0 ms. Native libraries / OS traffic are outside this guard; no full-network-isolation claim.
- Parent reported independently reproducing the Back-with-open-modal bug. The snapshot contains a source-level fix; actual browser validation is the parent's evidence, not a claimed result of this auditor's blocked browser run.
- Local-only development server, source-verbatim output, no uploads, no authored query persistence, safe text insertion and explicit fiction labeling remain appropriate. No code or prompt path exists for query text to execute transactions or reveal secrets; the added capability guard is a relevance UX feature, not a new authorization boundary.

## Recommendation and stopping point

Deliver as **local source retrieval with visible uncertainty and inspectable letters**. Report real positive retrieval results together with the fresh negative failures. Avoid wording that promises the system knows when a question cannot be answered. Prefer “finds surviving words without inventing missing details” to claims of calibrated silence or correctness.

The useful next quality step would be a genuinely larger, independently labeled corpus/query set and a principled relevance/answerability model or explicit retrieval-only UX—not more tuning to these now-exposed phrases. That expands scope beyond this small demo. This audit establishes the specified frozen candidates, completes all authorized local inference/API checks, preserves original evidence, and hands UI verification back to the parent. No external publication, uploads, account actions, or app-source/test edits were performed by the auditor.
