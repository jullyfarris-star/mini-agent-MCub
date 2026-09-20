from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.ai_mini import AIMini


def main() -> None:
    agent = AIMini(ROOT)
    print("Статус:", agent.status())
    print("Відповідь:", agent.process("Привіт, Кубе"))
    print("Статус після запиту:", agent.status())
    print("RAG:", agent.rag.search("контекст"))
    print("✅ Базовий каркас працює")


if __name__ == "__main__":
    main()
