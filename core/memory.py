from __future__ import annotations

import json
import re
import time
from pathlib import Path


class MemoryModule:
    """Simple memory store for notes, facts and conversation snippets."""

    def __init__(self, storage_path: str | Path = "data/memory.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.storage_path.exists():
            return {"entries": []}
        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"entries": []}

    def _save(self) -> None:
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def add_entry(self, topic: str, content: str, metadata: dict | None = None) -> dict:
        entry = {
            "id": len(self.data["entries"]),
            "topic": topic,
            "content": content,
            "metadata": metadata or {},
            "created_at": time.time(),
        }
        self.data["entries"].append(entry)
        self._save()
        return entry

    def search(self, query: str, limit: int = 3) -> list[dict]:
        query_words = set(re.findall(r"[\wа-яіїєґА-ЯІЇЄҐ]+", query.lower()))
        results: list[dict] = []
        for entry in self.data["entries"]:
            text = " ".join([
                entry.get("topic", ""),
                entry.get("content", ""),
                *[str(v) for v in entry.get("metadata", {}).values()],
            ]).lower()
            score = sum(1 for word in query_words if word in text)
            if score:
                results.append({"entry": entry, "score": score})
        results.sort(key=lambda item: item["score"], reverse=True)
        return [item["entry"] for item in results[:limit]]

    def recent(self, limit: int = 5) -> list[dict]:
        return list(reversed(self.data["entries"]))[:limit]
