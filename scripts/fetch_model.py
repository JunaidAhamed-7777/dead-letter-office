#!/usr/bin/env python3
"""Fetch fixed upstream artifacts once. Serving and inference never use the network."""
import hashlib
import json
from pathlib import Path
import shutil
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
REPO = "sentence-transformers/all-MiniLM-L6-v2"
FILES = {"model.onnx": "onnx/model.onnx", "tokenizer.json": "tokenizer.json",
         "config.json": "config.json", "model-card.md": "README.md"}
EXPECTED_SHA256 = {
    "model.onnx": "6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452",
    "tokenizer.json": "be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037",
    "config.json": "953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41",
    "model-card.md": "dcd602d2fd35c203a247304a06fec6654a12f7941b739f9221a064fe8dc3b7f0",
}


def main():
    destination = ROOT / "models" / "all-MiniLM-L6-v2"
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {"repository": REPO, "revision": REVISION, "license": "Apache-2.0", "files": {}}
    for local, remote in FILES.items():
        url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{remote}"
        path = destination / local
        print(f"Fetching {remote} at {REVISION} …", flush=True)
        temporary = path.with_suffix(path.suffix + ".part")
        try:
            with urlopen(Request(url, headers={"User-Agent": "DeadLetterOffice-setup/1.0"}), timeout=90) as response:
                with temporary.open("wb") as handle:
                    size = 0
                    while chunk := response.read(1024 * 1024):
                        size += len(chunk)
                        if size > 150 * 1024 * 1024:
                            raise ValueError("Unexpected model artifact larger than 150 MiB")
                        handle.write(chunk)
            digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
            if digest != EXPECTED_SHA256[local]:
                raise ValueError(f"SHA-256 mismatch for {remote}; refusing to install.")
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        manifest["files"][local] = {"url": url, "bytes": path.stat().st_size,
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    shutil.copyfile(ROOT / "THIRD_PARTY_MODEL_LICENSE.txt", destination / "APACHE-LICENSE.txt")
    print(f"Ready. Offline artifacts are in {destination}")


if __name__ == "__main__":
    main()
