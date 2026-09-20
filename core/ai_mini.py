from __future__ import annotations

import json
import re
import time
from pathlib import Path

from .initiative import Initiative
from .language import LanguageModule
from .memory import MemoryModule
from .planner import Planner
from .rag import RAGModule
from .safeguards import Safeguards


class AIMini:
    """Orchestration layer for the Cube agent."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path(__file__).resolve().parents[1])
        self.dna = self._load_json(self.root / "config" / "cube_dna.json")
        safeguards_config = self.root / "config" / "safeguards_config.json"

        self.safeguards = Safeguards(safeguards_config)
        self.rag = RAGModule(self.root / "data" / "knowledge")
        self.memory = MemoryModule(self.root / "data" / "memory.json")
        self.planner = Planner()
        self.language = LanguageModule(
            supported=self.dna.get("language", {}).get("supported", ["uk"]),
            default=self.dna.get("language", {}).get("default", "uk"),
        )
        self.initiative = Initiative()

        self.context: list[dict[str, str]] = []
        self.state = self.dna["states"]["system"][0]
        # Allow the first request immediately after startup.
        self.last_active = time.time() - self.safeguards.rate_limit_seconds

    @staticmethod
    def _load_json(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _memory_content(user_input: str) -> str:
        """Remove a common memory command prefix before storing the note."""
        pattern = r"^\s*(запам'ятай|запамятай|запиши|remember|save)\s*[:,-]?\s*"
        content = re.sub(pattern, "", user_input, flags=re.IGNORECASE).strip()
        return content or user_input.strip()

    def process(self, user_input: str) -> str:
        """Process one user message and update short-term context."""
        if not isinstance(user_input, str):
            raise TypeError("user_input must be a string")

        if self.safeguards.check_rate_limit(self.last_active):
            return "Зачекай секунду, я ще не готовий."

        if self.safeguards.check_context_overflow(len(self.context)):
            self.context = self.context[-max(1, self.max_context // 2) :]

        knowledge_hits = self.rag.search(user_input, top_k=3)
        decision = self.planner.decide_action(
            user_input=user_input,
            context_size=len(self.context),
            knowledge_hits=len(knowledge_hits),
        )

        self.last_active = time.time()

        if decision["action"] == "remember":
            content = self._memory_content(user_input)
            self.memory.add_entry(
                topic="user_note",
                content=content,
                metadata={"source": "conversation", "language": self.language.get_response_language(content)},
            )
            return f"Запам'ятав: {content}"

        self.context.append({"role": "user", "content": user_input})
        response = self._generate_response(user_input, decision, knowledge_hits)
        self.context.append({"role": "assistant", "content": response})
        return response

    def _generate_response(self, user_input: str, decision: dict, knowledge_hits: list[str]) -> str:
        text = user_input.strip()
        if not text:
            return "Куб слухає. Напиши щось, і я відповім."

        lang = self.language.get_response_language(text)
        remembered = self.memory.search(text, limit=2)
        snippets = [self.rag.load_context(path)[:500] for path in knowledge_hits]

        if snippets:
            body = "Куб знайшов релевантні знання:\n" + "\n---\n".join(snippets)
        elif remembered:
            notes = "\n".join(f"- {entry['content']}" for entry in remembered)
            body = "Куб знайшов у пам'яті:\n" + notes
        else:
            body = f"Куб отримав: {text}"

        prefixes = {"uk": "Куб каже:", "ko": "큐가 말해요:", "en": "Cube says:"}
        return f"{prefixes.get(lang, prefixes['uk'])}\n{body}"

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
            "memory_entries": len(self.memory.data.get("entries", [])),
        }

    def check_initiative(self) -> str | None:
        reason = self.initiative.should_speak(self.status(), self.last_active)
        return self.initiative.generate_message(reason) if reason else None
