from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.ai_mini import AIMini
from core.memory import MemoryModule
from core.rag import RAGModule


class CubeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.agent = AIMini(self.root)

    def test_agent_starts(self) -> None:
        status = self.agent.status()
        self.assertEqual(status["state"], "stable")
        self.assertIn("memory_entries", status)

    def test_process_updates_context(self) -> None:
        response = self.agent.process("Привіт, Кубе")
        self.assertIsInstance(response, str)
        self.assertEqual(len(self.agent.context), 2)

    def test_rag_finds_knowledge(self) -> None:
        rag = RAGModule(self.root / "data" / "knowledge")
        self.assertTrue(rag.search("контекст"))

    def test_memory_command_is_saved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            memory = MemoryModule(Path(directory) / "memory.json")
            entry = memory.add_entry("test", "Куб пам'ятає цю нотатку")
            self.assertEqual(entry["content"], "Куб пам'ятає цю нотатку")
            self.assertTrue(memory.search("пам'ятає"))

    def test_memory_command_strips_prefix(self) -> None:
        response = self.agent.process("Запам'ятай: я будую Куба")
        self.assertEqual(response, "Запам'ятав: я будую Куба")
        entries = self.agent.memory.recent(1)
        self.assertEqual(entries[0]["content"], "я будую Куба")
        self.assertEqual(len(self.agent.context), 0)


if __name__ == "__main__":
    unittest.main()
