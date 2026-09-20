from __future__ import annotations

import json
import time
from pathlib import Path

from .initiative import Initiative
from .rag import RAGModule
from .safeguards import Safeguards


class AIMini:
    """Small orchestration layer for the Cube agent."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path(__file__).resolve().parents[1])
        self.dna = self._load_json(self.root / "config" / "cube_dna.json")
        safeguards_config = self.root / "config" / "safeguards_config.json"
        self.safeguards = Safeguards(safeguards_config)
        self.rag = RAGModule(self.root / "data" / "knowledge")
        self.initiative = Initiative()
        self.context: list[dict[str, str]] = []
        self.state = self.dna["states"]["system"][0]
        # Минус rate-limit, щоб перший запит після запуску дозволявся.
        self.last_active = time.time() - self.safeguards.rate_limit_seconds

    @staticmethod
    def _load_json(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def process(self, user_input: str) -> str:
        """Приймає повідомлення, оновлює контекст і повертає відповідь."""
        if not isinstance(user_input, str):
            raise TypeError("user_input must be a string")

        if self.safeguards.check_rate_limit(self.last_active):
            return "Зачекай секунду, я ще не готовий."

        if self.safeguards.check_context_overflow(len(self.context)):
            self.context = self.context[-self.max_context // 2 :]

        self.last_active = time.time()
        self.context.append({"role": "user", "content": user_input})
        response = self._generate_response(user_input)
        self.context.append({"role": "assistant", "content": response})
        return response

    def _generate_response(self, user_input: str) -> str:
        text = user_input.strip()
        if not text:
            return "Куб слухає. Напиши щось, і я відповім."

        matches = self.rag.search(text, top_k=2)
        if matches:
            snippets = [self.rag.load_context(path)[:500] for path in matches]
            return "Куб знайшов у локальній пам'яті:\n" + "\n---\n".join(snippets)

        return f"Куб отримав: {text}"

    @property
    def max_context(self) -> int:
        return int(self.dna["rules"]["style"]["max_context"])

    def status(self) -> dict:
        return {
            "name": self.dna["cube_dna"]["name"],
            "version": self.dna["cube_dna"]["version"],
            "state": self.state,
            "context_size": len(self.context),
            "max_context": self.max_context,
            "knowledge_files": len(self.rag.files),
        }

    def check_initiative(self) -> str | None:
        reason = self.initiative.should_speak(self.status(), self.last_active)
        return self.initiative.generate_message(reason) if reason else None
