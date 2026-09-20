from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


class RAGModule:
    """Мінімальний локальний пошук по текстових файлах."""

    extensions = {".txt", ".md", ".json"}

    def __init__(self, data_path: str | Path) -> None:
        self.data_path = Path(data_path)
        self.files = self._collect_files()
        self.index = self._build_index()

    def _collect_files(self) -> list[Path]:
        if not self.data_path.exists():
            return []
        return [
            path for path in self.data_path.rglob("*")
            if path.is_file() and path.suffix.lower() in self.extensions
        ]

    @staticmethod
    def _words(text: str) -> list[str]:
        return re.findall(r"[\wа-яіїєґА-ЯІЇЄҐ]+", text.lower())

    def _build_index(self) -> dict[str, set[str]]:
        index: dict[str, set[str]] = {}
        for path in self.files:
            try:
                words = set(self._words(path.read_text(encoding="utf-8")))
            except (OSError, UnicodeError):
                continue
            for word in words:
                index.setdefault(word, set()).add(str(path))
        return index

    def search(self, query: str, top_k: int = 3) -> list[str]:
        query_words = self._words(query)
        scores: Counter[str] = Counter()
        for word in query_words:
            for path in self.index.get(word, set()):
                scores[path] += 1
        return [path for path, _ in scores.most_common(top_k)]

    @staticmethod
    def load_context(path: str | Path) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return ""
