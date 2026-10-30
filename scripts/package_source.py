#!/usr/bin/env python3
"""Create a private source/demo bundle without models, dependencies, or screenshots."""
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".git", ".venv", ".verify-venv", ".vendor", ".tools", ".demo-frames", ".media-work", "models", "__pycache__", "deliverables"}


def main():
    destination = ROOT / "deliverables"
    destination.mkdir(exist_ok=True)
    output = destination / "dead-letter-office-source.zip"
    count = 0
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as bundle:
        for file in sorted(ROOT.rglob("*")):
            relative = file.relative_to(ROOT)
            if not file.is_file() or any(part in EXCLUDE for part in relative.parts):
                continue
            if file.name == "raw-ui-demo.mp4":
                continue
            if file.suffix == ".pyc":
                continue
            # Only deliberate README media belong in a deliverable. Internal
            # browser inspection screenshots are not included accidentally.
            if file.suffix in {".png", ".jpg", ".jpeg"} and relative.parts[:2] != ("docs", "media"):
                continue
            bundle.write(file, "dead-letter-office/" + relative.as_posix())
            count += 1
    with ZipFile(output) as bundle:
        assert bundle.testzip() is None
        assert not any("/models/" in name or "/.vendor/" in name for name in bundle.namelist())
    print(f"{output}\n{count} files; {output.stat().st_size} bytes\nSHA-256 {hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
