from __future__ import annotations

from pathlib import Path

import gradio as gr

from core.ai_mini import AIMini

ROOT = Path(__file__).resolve().parent
agent = AIMini(ROOT)


def chat(message: str, history):
    if not message or not message.strip():
        return ""
    return agent.process(message)


demo = gr.ChatInterface(
    fn=chat,
    title="mini-agent-MCub",
    description="Локальний AI-mini агент з RAG, пам'яттю та контекстом і Hugging Face LLM fallback",
    chatbot=gr.Chatbot(height=500),
    textbox=gr.Textbox(placeholder="Напиши своє повідомлення...", lines=2),
)


if __name__ == "__main__":
    demo.launch()
