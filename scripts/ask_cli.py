#!/usr/bin/env python3
"""Read the same model-backed evidence in a terminal."""
import argparse
import json
from pathlib import Path
import sys
import textwrap

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from archive import Archive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = Archive().ask(args.question)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print("DEAD LETTER OFFICE / LOCAL CPU / FICTIONAL ARCHIVE\n")
    print(f"> {result['question']}\n\n{result['status'].upper()}: {result['summary']}\n")
    for source in result["sources"]:
        print(f"[{source['id']}] {source['title']} / similarity {source['score']:.3f}")
        print(textwrap.fill(source["text"], 88), "\n")
    print(textwrap.fill(result["limitation"], 88))
    print(f"\nModel retrieval: {result['elapsed_ms']} ms. No generated testimony.")


if __name__ == "__main__":
    main()
