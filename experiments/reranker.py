"""Local open-weight query–passage relevance model; no generated text."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from archive import LocalEncoder, ROOT, np


class LocalReranker(LocalEncoder):
    def __init__(self, directory: Path = ROOT / "models" / "ms-marco-MiniLM-L6-v2"):
        super().__init__(directory)
        self.tokenizer.enable_truncation(max_length=512)

    def score(self, question: str, passages: list[str]) -> np.ndarray:
        if not passages:
            return np.empty(0, dtype=np.float32)
        with self.lock:
            batch = self.tokenizer.encode_batch([(question, passage) for passage in passages])
            inputs = {
                "input_ids": np.asarray([item.ids for item in batch], dtype=np.int64),
                "attention_mask": np.asarray([item.attention_mask for item in batch], dtype=np.int64),
                "token_type_ids": np.asarray([item.type_ids for item in batch], dtype=np.int64),
            }
            names = {x.name for x in self.session.get_inputs()}
            return self.session.run(None, {key: value for key, value in inputs.items() if key in names})[0].reshape(-1)
