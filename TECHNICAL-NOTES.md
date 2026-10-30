# Dead Letter Office

**Some stories end. Some just stop arriving.**

A private, local reading room for twelve fictional letters from Morrow Quay, October 1924. Ask about the train that never left, the voice in the wireless room, or the lighthouse that two witnesses remember differently. Every result leads back to the actual paragraph. The app never writes in a missing person's voice.

Started October 30, 2026 for the DEV **Ghost in the Machine** challenge. The public source repository is [JunaidAhamed-7777/dead-letter-office](https://github.com/JunaidAhamed-7777/dead-letter-office).

## Run it

Python 3.12 is the tested environment. The UI needs a current browser with native `<dialog>` support. No API keys, paid APIs, GPU, accounts, JavaScript package installation, or frontend build step.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/fetch_model.py
python server.py
```

Open **http://127.0.0.1:8765**. Use `python server.py --port 8766` if that port is busy.

Installation downloads dependencies and about 91 MB of pinned model artifacts from the official Sentence Transformers repository on Hugging Face. The fetch script checks SHA-256 hashes before installing them. After that, disconnect the internet: the model, corpus, fonts, UI, and searches stay local. Startup does not fetch missing files silently; it gives a setup error.

This prepared workspace already has model files and project-local ONNX/tokenizer packages, so `python server.py` works here directly. `.vendor/`, `.tools/`, and `models/` are excluded from source control. Reproducible setup uses the commands above instead of relying on that convenience.

## A three-minute visit

1. Ask **“Why did the night train never leave?”** Open a source and read its surrounding letter.
2. Ask **“Was the lighthouse burning that night?”** Both contradictory accounts appear. They are not averaged into a confident answer.
3. Ask **“Where was the little tin bird hidden?”** Read the specific drawer and wrapping instructions.
4. Ask **“What is the current price of Bitcoin?”** The archive abstains rather than borrowing knowledge from outside its record.
5. Ask **“Who owned the red mitten on the lighthouse stairs?”** Notice the distinction: a strong match can be a paragraph that says the answer is unknown. Similarity is not certainty.
6. Browse all letters, open one with the keyboard, close with Escape, and export your findings as a local text file.

## What the AI actually does

- Model: [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), upstream revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, Apache-2.0.
- Runtime: ONNX Runtime, CPU only. The full floating-point model is about 90.4 MB.
- The Hugging Face Tokenizers library tokenizes paragraphs and queries. Inputs are capped at the model's 256-token sentence-transformer limit.
- Attention-mask-aware mean pooling and L2 normalization produce 384-dimensional embeddings, following the upstream model card.
- Index text includes the actual source title, author, recipient, and paragraph. No evaluation questions, expanded answers, or artificial synonyms are inserted into the index.
- Ranking blends **50% MiniLM cosine similarity and 50% TF-IDF similarity**. This preserves meaning-based matching while helping exact names and objects.
- Up to three passages pass a fixed **0.12 hybrid-relevance floor** and a 0.16 distance-from-top window. Closely ranked, explicitly catalogued contradictory counterparts are added. These are retrieval heuristics, not calibrated correctness probabilities.
- The UI's displayed similarity is the **neural cosine**, not the blended rank score. A 0.48 neural threshold labels a stronger related match; it does not mean the question has been answered.
- Narrow deterministic scope rules reject relative live-service questions (such as tomorrow's forecast) and direct transaction requests (such as booking a flight). These rules are openly separate from the model; they are not a general answerability classifier.
- Reconstruction is **extractive**, not generative: all evidence text is copied verbatim, with stable letter/paragraph IDs. There is no hidden chat model.

The AI supplies meaning-based retrieval. Source links, scope rules, conflict links, and quote assembly are ordinary code. The app does **not** claim to detect contradictions automatically or identify a missing person's fate.

## Measured result, including the misses

The original 32-question synthetic set became **development data** when its failures were used to compare index context and ranking weights. All 33 candidates are recorded in `evidence/development-tuning.json`; nothing is hidden as a failed run. No model fine-tuning or question-specific answer lookup was used.

| Development retrieval measure, 32 questions | MiniLM + TF-IDF | Same-context TF-IDF |
|---|---:|---:|
| Correct source ranked first | 24/32 · 75.00% | 20/32 · 62.50% |
| At least one relevant source in top 3 | 31/32 · 96.88% | 28/32 · 87.50% |
| Mean reciprocal rank | 0.8633 | 0.7542 |

The final source-selection policy also shows supporting evidence on **31/32** development questions. The baseline uses the same actual title/byline/paragraph context, English stopwords, unigram/bigram terms, and sublinear term frequency. Full rankings, selection results, and file hashes are in [`evidence/evaluation-results.json`](evidence/evaluation-results.json).

A separate reviewer then authored **38 unseen questions** against the frozen first candidate: 24 answerable, six missing-fact, five out-of-domain, and three injection-style cases. On that initial blind run, the hybrid ranked relevant evidence in the top three for **22/24** answerable cases, but the old cosine-only gate displayed useful evidence on only **19/24**. This exposed a real defect: relevance ranking and evidence selection were being judged separately. Literal-quote integrity had zero errors. The complete first report is preserved in `evidence/independent-candidate-01.json`.

Those 38 questions are now **diagnostic/regression cases**, not a fresh holdout. Candidate 02 uses the hybrid rank for inclusion, describes conflict at source level, and adds explicit live-service/transaction scope rules. Supporting evidence rose to **22/24** on that now-seen set. This is a regression improvement, not an independent accuracy claim. The first run, tuning record, and failed cross-encoder experiment are retained.

All six development out-of-domain questions abstain, sometimes because of the explicit scope rules. In-domain missing facts still retrieve related writing, and a plausible paragraph can be the wrong one. For example, asking whether the late service carried anyone inland during the gale can retrieve the ferry account instead of the canceled train. The model also struggles with “repairer kept the recording”: there are several repairers in this small archive. It never invents an ending, but it can hand you unhelpful evidence.

After candidate 02 froze, the independent reviewer ran a **new 18-case smoke set**. All **12 answerable cases returned every required evidence group**, and both missing-fact cases returned passages acknowledging the gaps; citation integrity had zero errors. But only **one of four difficult out-of-domain cases abstained**. A current purchase question, modern lighthouse repair request, and next-Tuesday water-level question received related historical excerpts instead. All were labeled uncertain and no current facts were invented. The scope rules are intentionally narrow, not reliable general intent detection. See `evidence/independent-candidate-02-smoke.json`.

On that fresh smoke set, hybrid top-1 ranking was 6/12 versus 7/12 for neural-only and 5/12 for TF-IDF; hybrid and neural both had top-3 support on 12/12 versus 7/12 for TF-IDF. The hybrid is not universally better than neural-only. The useful result here is a traceable reading set, not a claim to have solved question answering.

The evaluation disables Python socket connections before model loading and inference. The final recorded run took about 705 ms to load the model and encode the archive on this machine. Device performance varies. This small fictional collection is not a general question-answering benchmark.

## Verify

```bash
python -m unittest discover -s tests -v
python scripts/evaluate.py
node --check web/app.js
python -m compileall -q archive.py server.py scripts tests
# Optional browser checks (requires Playwright + Chromium; not a runtime dependency):
python tests/browser_check.py
```

The 15 unit/API tests exercise real model vectors, exact citation integrity, repeatability, irrelevant questions, scope guards, weak-paraphrase retention, incidental-conflict handling, validation, missing-model errors, host/origin restrictions, file allowlisting, and malformed HTTP input. The browser script is supplied for reproducibility; it was not run in the restricted execution sandbox. Browser interaction checks were performed separately through the connected browser; see `VALIDATION.md`.

## Privacy and boundaries

- The server binds only to `127.0.0.1`; do not expose this development server to the internet.
- No analytics, remote fonts, telemetry, external inference, request logs, accounts, or cookies are added by the app.
- Questions live in memory while the page is open. They are not saved in URLs or browser storage. Export only saves the findings file you request.
- Source data are entirely fictional and original to this project. No user email, family record, or real deceased person's identity was used.
- The demo is read-only. There is no upload or browser-based archive editor. To experiment, edit a **copy** of `data/letters.json` locally and restart. Keep IDs unique and conflict references valid. The included evaluation only describes the original corpus.
- This is not a historical authentication, legal, medical, missing-person investigation, or bereavement service. Related wording does not prove a fact or establish that a question is answerable.

## Why open matters here

The story is small enough to carry with its model. It remains readable if a hosted API disappears, and a search does not send a letter to another organization. The retrieval model, pooling, ranking, cutoffs, source data, and every quoted result are inspectable. Anyone can replace the model and rerun the same questions—including the ones this version gets wrong.

## Demo recordings

The primary demo is `docs/media/demo.mp4`: 78 seconds of actual browser interaction, cropped to the app and edited for pace. `MASTER.gif` and four feature GIFs are cut from it. Capture/edit details are in `docs/media/capture-notes.json`. The raw desktop recording is excluded from source packages.


## Layout

```text
archive.py                  Local model, ranking, evidence assembly
server.py                   Loopback HTTP API and static server
web/                        Reading room UI; no build tooling
data/letters.json           Original fictional archive
data/evaluation.json        Frozen evaluation questions
scripts/fetch_model.py      Pinned download and integrity verification
scripts/evaluate.py         Offline model vs lexical evaluation
tests/                      Model/API/browser checks
evidence/                   Actual results, provenance, screenshots
DESIGN.md / UX-CONTRACT.md   Visual and interaction contracts
```

## License and acknowledgments

Project code and original fictional archive: MIT, see [`LICENSE`](LICENSE). Model weights: Apache-2.0, see [`THIRD_PARTY_MODEL_LICENSE.txt`](THIRD_PARTY_MODEL_LICENSE.txt), upstream model card, and the hash/URL record in [`evidence/model-manifest.json`](evidence/model-manifest.json). The project does not claim authorship of MiniLM or its training data.

Runtime dependencies: ONNX Runtime (MIT), Hugging Face Tokenizers (Apache-2.0), NumPy (BSD-style). Evaluation dependencies: scikit-learn (BSD-3-Clause), SciPy (BSD-style; distributions include third-party notices). Each installed distribution retains its own license and bundled notices. Python's standard HTTP server and a handwritten vanilla frontend avoid a separate web-framework dependency.

No partner-category technology is claimed. Competition publication and final submission remain separate user decisions.
