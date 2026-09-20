from __future__ import annotations

import re


class LanguageModule:
    """Minimal language detection and response-language selection."""

    def __init__(self, supported: list[str] | None = None, default: str = "uk") -> None:
        self.supported = supported or ["uk", "en", "ko"]
        self.default = default

    @staticmethod
    def detect_language(text: str) -> str:
        if re.search(r"[а-яїієґА-ЯЇІЄҐ]", text):
            return "uk"
        if re.search(r"[가-힣]", text):
            return "ko"
        return "en"

    def get_response_language(self, text: str) -> str:
        detected = self.detect_language(text)
        return detected if detected in self.supported else self.default
