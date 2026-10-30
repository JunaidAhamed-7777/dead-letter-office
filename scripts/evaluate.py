#!/usr/bin/env python3
"""Reproducible small fictional-archive evaluation, with a lexical comparator."""
import hashlib
import json
from pathlib import Path
import socket
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from archive import Archive
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def metrics(rows, key):
    reciprocal_ranks = []
    top1, hit3, recall3 = [], [], []
    for row in rows:
        expected = set(row["relevant"])
        ranking = row[key]
        top1.append(ranking[0] in expected)
        hit3.append(bool(set(ranking[:3]) & expected))
        recall3.append(len(set(ranking[:3]) & expected) / len(expected))
        reciprocal_ranks.append(next((1 / (i + 1) for i, value in enumerate(ranking) if value in expected), 0))
    return {"top1_accuracy": round(float(np.mean(top1)), 4), "hit_at_3": round(float(np.mean(hit3)), 4),
            "recall_at_3": round(float(np.mean(recall3)), 4), "mean_reciprocal_rank": round(float(np.mean(reciprocal_ranks)), 4)}


def main():
    # Prove this process performs model inference without a socket connection.
    def no_network(*args, **kwargs):
        raise AssertionError("Network access is forbidden during evaluation")
    socket.socket.connect = no_network
    test_path = ROOT / "data" / "evaluation.json"
    cases = json.loads(test_path.read_text())
    start = time.perf_counter()
    archive = Archive()
    startup = round((time.perf_counter() - start) * 1000, 1)
    baseline = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    matrix = baseline.fit_transform(archive.index_texts)
    rows = []
    for case in cases["retrieval"]:
        scores = (matrix @ baseline.transform([case["question"]]).T).toarray().ravel()
        lexical = [archive.passages[i]["id"] for i in np.argsort(-scores, kind="stable")]
        neural = archive.rank(case["question"])
        result = archive.ask(case["question"])
        rows.append({**case, "hybrid_ranking": [p["id"] for p in neural], "tfidf_ranking": lexical,
                     "selected_sources": [p["id"] for p in result["sources"]],
                     "selected_hit": bool(set(case["relevant"]) & {p["id"] for p in result["sources"]}),
                     "top_similarity": neural[0]["score"]})
    unknown = []
    for case in cases.get("unknown", []):
        result = archive.ask(case["question"])
        unknown.append({**case, "status": result["status"], "top_similarity": result["top_similarity"],
                        "sources": [p["id"] for p in result["sources"]],
                        "all_text_verbatim": all(p["text"] == archive.by_id[p["source_id"]]["text"] for p in result["answer"])})
    report = {"methodology": "Small authored fictional DEVELOPMENT set. Corpus/questions frozen before first run; index context and blend chosen using these results. Not a held-out or general benchmark. No fine-tuning or query-specific rules. Evaluation questions are never inserted into the index. TF-IDF baseline uses the same contextualized source text as the hybrid model.",
              "network_disabled": True, "startup_and_corpus_encoding_ms": startup,
              "model": archive.metadata, "answerable_count": len(rows),
              "evaluation_sha256": hashlib.sha256(test_path.read_bytes()).hexdigest(),
              "corpus_sha256": hashlib.sha256((ROOT / "data" / "letters.json").read_bytes()).hexdigest(),
              "hybrid": metrics(rows, "hybrid_ranking"), "tfidf": metrics(rows, "tfidf_ranking"),
              "selected_evidence_hit": sum(row["selected_hit"] for row in rows),
              "retrieval": rows, "unknown": unknown,
              "unknown_abstention_count": sum(case["status"] == "unknown" for case in unknown),
              "unknown_count": len(unknown),
              "limitations": ["A related passage is not necessarily an answer.", "Similarity is not probability or truth.",
                               "In-domain missing facts can retrieve strongly related text instead of abstaining.",
                               "Conflict flags are manually catalogued, not automatically inferred.",
                               "Synthetic corpus and authored tests are small and not independently validated."]}
    path = ROOT / "evidence" / "evaluation-results.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ["network_disabled", "answerable_count", "hybrid", "tfidf", "selected_evidence_hit", "unknown_abstention_count", "unknown_count", "startup_and_corpus_encoding_ms"]}, indent=2))
    print(f"Full ranking and failure cases: {path}")


if __name__ == "__main__":
    main()
