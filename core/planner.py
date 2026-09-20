from __future__ import annotations


class Planner:
    """Simple action planner for a lightweight agent."""

    def decide_action(self, user_input: str, context_size: int, knowledge_hits: int = 0) -> dict:
        text = user_input.strip().lower()

        if not text:
            return {"action": "idle", "reason": "empty_input"}

        if any(word in text for word in ["запам'ятай", "запамятай", "запиши", "remember", "save"]):
            return {"action": "remember", "reason": "explicit_memory_request"}

        if any(word in text for word in ["швидко", "срочно", "терміново", "urgent", "now"]):
            return {"action": "priority", "reason": "urgent_request"}

        if context_size >= 6 or knowledge_hits >= 2:
            return {"action": "answer_with_context", "reason": "context_or_rag_relevant"}

        if any(word in text for word in ["що", "коли", "як", "why", "how", "what", "when"]):
            return {"action": "answer", "reason": "informational_query"}

        return {"action": "answer", "reason": "default"}
