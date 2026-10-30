"""Local neural retrieval with deliberately non-generative evidence reconstruction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
import threading
import time

ROOT = Path(__file__).resolve().parent
if (ROOT / ".vendor").is_dir():
    sys.path.insert(0, str(ROOT / ".vendor"))

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

MODEL_DIR = ROOT / "models" / "all-MiniLM-L6-v2"
MODEL_NAME = "MiniLM + TF-IDF · local CPU"
# A hybrid retrieval floor, not a calibrated correctness probability. Candidate
# 02 replaces the cosine-only gate that discarded relevant paraphrases.
RELATED_THRESHOLD = 0.12
STRONG_THRESHOLD = 0.48
LEXICAL_WEIGHT = 0.5


def requests_live_data(question: str) -> bool:
    """Transparent capability guard, separate from learned passage retrieval.

    Relative live-service questions cannot be answered by a closed 1924 archive.
    This is deliberately narrow: narrative questions about plans for 'tomorrow'
    remain searchable. It is not a general answerability classifier.
    """
    temporal = re.search(r"\b(now|today|tomorrow|current|currently|latest|live)\b", question, re.I)
    service = re.search(r"\b(weather|forecast|price|prices|stock|stocks|score|scores|election|availability|flight|flights)\b", question, re.I)
    return bool(temporal and service)


def requests_transaction(question: str) -> bool:
    """This read-only archive cannot book, buy, pay, or send on a reader's behalf."""
    request = re.search(r"\b(can you|could you|would you|should i|please)\b", question, re.I)
    action = re.search(r"\b(book|reserve|buy|purchase|pay|send)\b", question, re.I)
    target = re.search(r"\b(flight|flights|hotel|tickets|reservation|money|payment|email|emails)\b", question, re.I)
    return bool(request and action and target)


class LocalEncoder:
    def __init__(self, directory: Path = MODEL_DIR):
        if not (directory / "model.onnx").is_file():
            raise RuntimeError("Model not found. Run python scripts/fetch_model.py once, then restart.")
        self.manifest = json.loads((directory / "manifest.json").read_text())
        for name in ("model.onnx", "tokenizer.json"):
            expected = self.manifest["files"][name]["sha256"]
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected:
                raise RuntimeError(f"Model integrity check failed for {name}; fetch the pinned model again.")
        self.tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        self.tokenizer.enable_truncation(max_length=256)
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(directory / "model.onnx"), sess_options=options,
                                            providers=["CPUExecutionProvider"])
        self.lock = threading.Lock()

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        with self.lock:
            batch = self.tokenizer.encode_batch(texts)
            inputs = {
                "input_ids": np.asarray([item.ids for item in batch], dtype=np.int64),
                "attention_mask": np.asarray([item.attention_mask for item in batch], dtype=np.int64),
                "token_type_ids": np.asarray([item.type_ids for item in batch], dtype=np.int64),
            }
            inputs = {key: value for key, value in inputs.items() if key in {x.name for x in self.session.get_inputs()}}
            tokens = self.session.run(None, inputs)[0]
            mask = np.asarray([item.attention_mask for item in batch], dtype=np.float32)[..., None]
            # The upstream model card specifies attention-mask-aware mean pooling.
            pooled = (tokens * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1e-9)
            return pooled / np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)


class Archive:
    def __init__(self, corpus: Path = ROOT / "data" / "letters.json", encoder=None):
        data = json.loads(corpus.read_text(encoding="utf-8"))
        self.letters = data["letters"] if isinstance(data, dict) else data
        self.passages = []
        self.by_id = {}
        self.letter_by_id = {letter["id"]: letter for letter in self.letters}
        for letter in self.letters:
            for passage in letter["passages"]:
                row = {**passage, "letter_id": letter["id"], "title": letter["title"],
                       "date": letter["date"], "author": letter["author"], "location": letter["location"]}
                if row["id"] in self.by_id:
                    raise ValueError("Passage IDs must be unique")
                self.by_id[row["id"]] = row
                self.passages.append(row)
        for passage in self.passages:
            for target in passage.get("conflicts", []):
                if target not in self.by_id:
                    raise ValueError(f"Missing conflicting source {target}")
        self.encoder = encoder or LocalEncoder()
        self.index_texts = [f"{p['title']}. Letter from {self.letter_by_id[p['letter_id']]['author']} to {self.letter_by_id[p['letter_id']]['recipient']}. {p['text']}" for p in self.passages]
        self.embeddings = self.encoder.encode(self.index_texts)
        self.lexical = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.lexical_matrix = self.lexical.fit_transform(self.index_texts)
        self.metadata = {"name": MODEL_NAME, "description": "384-dimensional MiniLM embeddings with source title/byline context. Ranking blends 50% semantic cosine with 50% TF-IDF. Displayed similarity is neural cosine, not the blended rank or confidence. Quotes pass a 0.12 hybrid relevance floor. A separate narrow scope rule rejects live-service requests; it is not an answerability model.",
                         "dimensions": int(self.embeddings.shape[1]), "passages": len(self.passages),
                         "revision": self.encoder.manifest["revision"], "provider": "CPUExecutionProvider",
                         "index_context": "title + author + recipient + paragraph", "lexical_weight": LEXICAL_WEIGHT,
                         "selection_floor": RELATED_THRESHOLD, "selection_metric": "hybrid relevance", "candidate": "02",
                         "answer_method": "Extractive — no text-generation model"}

    def rank(self, question: str) -> list[dict]:
        vector = self.encoder.encode([question])[0]
        scores = self.embeddings @ vector
        lexical_scores = (self.lexical_matrix @ self.lexical.transform([question]).T).toarray().ravel()
        rank_scores = (1 - LEXICAL_WEIGHT) * scores + LEXICAL_WEIGHT * lexical_scores
        indices = np.argsort(-rank_scores, kind="stable")
        return [{**self.passages[index], "score": round(float(scores[index]), 4),
                 "rank_score": round(float(rank_scores[index]), 4)} for index in indices]

    def ask(self, question: str) -> dict:
        if not isinstance(question, str):
            raise ValueError("Write a question using text.")
        question = question.strip()
        if not question:
            raise ValueError("Write a question about the letters first.")
        if len(question) > 600:
            raise ValueError("Keep the question to 600 characters or fewer.")
        start = time.perf_counter()
        scope_guard = "live_data" if requests_live_data(question) else "transaction" if requests_transaction(question) else None
        if scope_guard:
            summary = "This archive has no live data. Its fictional letters describe October 1924, not current conditions." if scope_guard == "live_data" else "This is a read-only fictional archive. It cannot make bookings, purchases, payments, or send messages."
            return {"question": question, "status": "unknown", "summary": summary,
                    "answer": [], "sources": [], "conflicts": [], "limitation": "A narrow, deterministic scope rule recognized a live-service or transaction request outside this archive's capabilities. This rule is separate from the model and is not a general answerability classifier. No retrieval claim is being made.",
                    "elapsed_ms": round((time.perf_counter() - start) * 1000, 1), "model": self.metadata,
                    "keywords": [], "top_similarity": None, "scope_guard": scope_guard}
        ranked = self.rank(question)
        top = ranked[0]["score"] if ranked else 0.0
        top_rank = ranked[0]["rank_score"] if ranked else 0.0
        # Include up to three related passages, then any explicitly catalogued
        # contradictory counterpart. Conflict links are editorial, not inferred.
        sources = [p for p in ranked[:3] if p["rank_score"] >= RELATED_THRESHOLD and p["rank_score"] >= top_rank - 0.16]
        conflicts = []
        for source in sources[:]:
            # A weak incidental match must not turn an unrelated inquiry into
            # a claim that its central evidence conflicts. The links remain
            # visible inside the source letter; only close primary accounts
            # expand this particular reading set.
            if source["rank_score"] < top_rank - 0.06:
                continue
            for target in source.get("conflicts", []):
                pair = sorted((source["id"], target))
                if pair not in conflicts:
                    conflicts.append(pair)
                if not any(item["id"] == target for item in sources):
                    counterpart = next(item for item in ranked if item["id"] == target)
                    sources.append({**counterpart, "included_because": "Catalogued conflicting account"})
        status = "unknown" if not sources else "uncertain" if conflicts or top < STRONG_THRESHOLD else "found"
        summary = {
            "unknown": "I couldn't find a close match in these letters. The archive does not support an answer.",
            "uncertain": "Related passages survived, but they do not settle the question.",
            "found": "These are the closest surviving passages. Read the accounts before drawing a conclusion.",
        }[status]
        limitation = "Similarity measures related wording and meaning, not truth or answer completeness. These are fictional accounts, quoted without inventing missing details."
        if conflicts:
            summary = "This reading set includes accounts that disagree. Both versions are preserved below; the disagreement may not settle your question."
            limitation = "An editorial conflict link connects these accounts; the model did not discover or resolve the contradiction. No witness is treated as authoritative."
        elif status == "unknown":
            limitation = "No shortlisted passage crossed the fixed 0.12 hybrid relevance floor. This is a retrieval safeguard, not proof that the topic is absent. Try a named place, object, or event."
        return {"question": question, "status": status, "summary": summary,
                "answer": [{"text": source["text"], "source_id": source["id"], "letter_id": source["letter_id"]} for source in sources],
                "sources": sources, "conflicts": conflicts, "limitation": limitation,
                "elapsed_ms": round((time.perf_counter() - start) * 1000, 1), "model": self.metadata,
                "keywords": [], "top_similarity": top}

    def catalogue(self) -> dict:
        return {"letters": self.letters, "model": self.metadata,
                "examples": ["Why did the night train never leave?", "Was the lighthouse burning that night?",
                             "Where was the little tin bird hidden?", "What happened to Ada Venn?"]}
