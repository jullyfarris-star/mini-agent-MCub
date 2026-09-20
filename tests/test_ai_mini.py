from __future__ import annotations

import time
import unittest
from pathlib import Path

from core.ai_mini import AIMini
from core.rag import RAGModule


class CubeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = AIMini(Path(__file__).resolve().parents[1])

    def test_agent_starts(self) -> None:
        self.assertEqual(self.agent.status()["state"], "stable")

    def test_process_updates_context(self) -> None:
        response = self.agent.process("Привіт, Кубе")
        self.assertIsInstance(response, str)
        self.assertEqual(len(self.agent.context), 2)

    def test_rag_finds_knowledge(self) -> None:
        rag = RAGModule(Path(__file__).resolve().parents[1] / "data" / "knowledge")
        self.assertTrue(rag.search("контекст"))


if __name__ == "__main__":
    unittest.main()
