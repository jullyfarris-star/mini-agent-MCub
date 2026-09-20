from __future__ import annotations

import random
import time


class Initiative:
    def __init__(self, cooldown_seconds: float = 300) -> None:
        self.cooldown_seconds = cooldown_seconds
        self.last_initiative = 0.0

    def should_speak(self, status: dict, last_active: float) -> str | None:
        now = time.time()
        if now - self.last_initiative < self.cooldown_seconds:
            return None
        if now - last_active > 3600:
            self.last_initiative = now
            return "idle_too_long"
        if status.get("context_size", 0) >= status.get("max_context", 10) - 2:
            self.last_initiative = now
            return "context_full"
        return None

    def generate_message(self, reason: str) -> str:
        messages = {
            "idle_too_long": ["Я тут, якщо що.", "Давно не спілкувались. Усе гаразд?"],
            "context_full": ["Контекст майже заповнений.", "Час очистити тимчасову пам'ять."],
        }
        return random.choice(messages.get(reason, ["Куб на зв'язку."]))
