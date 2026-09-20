from __future__ import annotations

import os
from typing import Any


class GeminiLLM:
    """Small Gemini API wrapper with a safe local fallback."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.client: Any = None
        self.available = False
        self._configure()

    def _configure(self) -> None:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[GeminiLLM] API key not found; using local fallback.")
            return

        try:
            from google import genai

            self.client = genai.Client(api_key=api_key)
            self.available = True
        except Exception as exc:
            print(f"[GeminiLLM] Setup error: {exc}")

    def generate(self, prompt: str, max_output_tokens: int = 256) -> str:
        if not self.available or self.client is None:
            return "Gemini API недоступний. Куб працює в локальному fallback-режимі."

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": max_output_tokens,
                },
            )
            text = getattr(response, "text", None)
            if text:
                return text.strip()
            return "Gemini не повернув текстову відповідь."
        except Exception as exc:
            print(f"[GeminiLLM] Generation error: {exc}")
            return "Gemini тимчасово недоступний. Куб залишився у fallback-режимі."
