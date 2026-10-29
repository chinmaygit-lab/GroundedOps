"""Small, deterministic BM25 document retriever for a portfolio-sized RAG demo."""
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TOKENS = re.compile(r"[a-z0-9]+")
STOP = frozenset("a an and are as at be by can do does for from how i in is it of on or our should the their then there these this to what when where which who why with you your".split())
MAX_FILE_BYTES = 300_000
ALLOWED_EXT = {".md", ".txt", ".csv", ".json"}


def tokenize(value: str) -> list[str]:
    return [word for word in TOKENS.findall(value.lower()) if word not in STOP and len(word) > 1]


@dataclass(frozen=True)
class Passage:
    id: str
    source: str
    text: str


@dataclass(frozen=True)
class Hit:
    id: str
    source: str
    text: str
    score: float

    def to_dict(self) -> dict:
        return {"id": self.id, "source": self.source, "text": self.text, "score": round(self.score, 3)}


def _chunks(text: str, max_words: int = 105, overlap: int = 22):
    words = text.split()
    if not words:
        return
    step = max_words - overlap
    for start in range(0, len(words), step):
        portion = words[start:start + max_words]
        if portion:
            yield " ".join(portion)
        if start + max_words >= len(words):
            break


def _load_text(path: Path) -> str:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f"Document exceeds {MAX_FILE_BYTES} bytes: {path.name}")
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames:
                return ""
            rows = []
            for n, row in enumerate(reader, 1):
                if n > 1000:
                    raise ValueError("CSV is too large for this demo (1000 rows maximum)")
                rows.append(f"Row {n}: " + "; ".join(f"{k}: {v}" for k, v in row.items()))
            return "\n".join(rows)
    if path.suffix.lower() == ".json":
        return json.dumps(json.loads(path.read_text(encoding="utf-8-sig")), ensure_ascii=False)
    return path.read_text(encoding="utf-8-sig")


def load_passages(root: Path) -> list[Passage]:
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Knowledge directory does not exist: {root}")
    passages: list[Passage] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in ALLOWED_EXT:
            continue
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        text = _load_text(path)
        relative = path.relative_to(root).as_posix()
        for i, chunk in enumerate(_chunks(text), 1):
            passages.append(Passage(f"{relative}#{i}", relative, chunk))
    return passages


class Retriever:
    def __init__(self, passages: list[Passage]):
        self.passages = passages
        self.terms = [Counter(tokenize(p.text)) for p in passages]
        self.lengths = [sum(c.values()) for c in self.terms]
        self.avglen = max(1.0, sum(self.lengths) / max(1, len(passages)))
        counts = Counter()
        for termset in self.terms:
            counts.update(termset.keys())
        n = len(passages)
        self.idf = {term: math.log(1 + (n - df + 0.5) / (df + 0.5)) for term, df in counts.items()}

    @classmethod
    def from_folder(cls, folder: Path) -> "Retriever":
        return cls(load_passages(folder))

    def search(self, query: str, top_k: int = 4) -> list[Hit]:
        if not (1 <= top_k <= 10):
            raise ValueError("top_k must be between 1 and 10")
        terms = set(tokenize(query))
        if not terms:
            return []
        scored = []
        for passage, tf, length in zip(self.passages, self.terms, self.lengths):
            score = sum(self.idf.get(term, 0) * (f * 2.2) /
                        (f + 1.2 * (0.25 + 0.75 * length / self.avglen))
                        for term in terms if (f := tf.get(term, 0)))
            if score > 0:
                scored.append(Hit(passage.id, passage.source, passage.text, score))
        scored.sort(key=lambda hit: (-hit.score, hit.id))
        return scored[:top_k]
