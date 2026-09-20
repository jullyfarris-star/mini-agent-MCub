from __future__ import annotations

import json
import time
from pathlib import Path


class TokenWallet:
    """Опційний простий гаманець; поки не підключений до оплати запитів."""

    def __init__(self, path: str | Path = "data/token_wallet.json", initial_balance: float = 100.0) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load(initial_balance)

    def _load(self, initial_balance: float) -> dict:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as file:
                return json.load(file)
        return {"balance": initial_balance, "history": [], "created_at": time.time()}

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    @property
    def balance(self) -> float:
        return float(self.data["balance"])

    def spend(self, amount: float, reason: str = "unknown") -> bool:
        if amount < 0 or self.balance < amount:
            return False
        self.data["balance"] -= amount
        self.data["history"].append({"type": "spend", "amount": amount, "reason": reason, "timestamp": time.time()})
        self._save()
        return True

    def earn(self, amount: float, reason: str = "reward") -> None:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self.data["balance"] += amount
        self.data["history"].append({"type": "earn", "amount": amount, "reason": reason, "timestamp": time.time()})
        self._save()
