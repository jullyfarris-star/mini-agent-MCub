from __future__ import annotations

import json
import time
from pathlib import Path


class Safeguards:
    def __init__(self, config_path: str | Path) -> None:
        self.config = self._load(Path(config_path))
        self.error_count = 0
        self.last_reset = time.time()
        self.rate_limit_seconds = float(self.config.get("rate_limit_seconds", 1.0))

    def _load(self, path: Path) -> dict:
        if not path.exists():
            return {"max_context_size": 10, "rate_limit_seconds": 1.0}
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def check_context_overflow(self, context_size: int) -> bool:
        return context_size > int(self.config.get("max_context_size", 10))

    def check_rate_limit(self, last_call_time: float) -> bool:
        return time.time() - last_call_time < self.rate_limit_seconds

    def report_error(self) -> None:
        self.error_count += 1
