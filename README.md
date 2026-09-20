# mini-agent-MCub

Mini-agent prototype inspired by the "Kub" concept: a personal/local AI agent with a small memory, a local knowledge base (RAG), language detection, and modular expansion.

This project is intentionally lightweight and beginner-friendly. It is not a full production LLM stack yet, but it is a solid starting point for experiments, demos, and Hugging Face Spaces.

## What is inside

- `config/` — DNA config and safety settings
- `core/` — agent logic, memory, RAG, planner, safeguards, and language support
- `data/knowledge/` — local text knowledge files used by the retrieval layer
- `tests/` — basic functional tests
- `scripts/` — quick local run scripts

## Local run

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the demo:

```bash
python scripts/test_runner.py
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Hugging Face Space

This project is already structured for a small Gradio app.

Run the web app locally:

```bash
python app.py
```

On Hugging Face Spaces, upload the repository files and use a Python Space with:

- `app.py`
- `requirements.txt`
- the existing `core/`, `config/`, `data/` folders

## Current capabilities

- reads a DNA config from `config/cube_dna.json`
- keeps a short conversation context
- searches local `.txt/.md/.json` knowledge files
- stores small notes in a local memory JSON file
- detects simple language (`uk`, `en`, `ko`)
- can decide whether a message should be answered, retrieved, or remembered
- has safety guardrails for basic rate limiting and context overflow

## Notes

This is a learning project and a starter prototype. It is intentionally simple and modular so it can grow into a stronger agent over time.

It is totally okay to build this step by step. A lot of people start with a messy repo, then clean it up into a real project. You are learning, and this is a good foundation.

## Project structure

```text
mini-agent-MCub/
├── README.md
├── LICENSE
├── .gitignore
├── app.py
├── requirements.txt
├── pyproject.toml
├── config/
│   ├── cube_dna.json
│   └── safeguards_config.json
├── core/
│   ├── __init__.py
│   ├── ai_mini.py
│   ├── initiative.py
│   ├── language.py
│   ├── memory.py
│   ├── planner.py
│   ├── rag.py
│   ├── safeguards.py
│   └── token_wallet.py
├── data/
│   ├── knowledge/
│   │   └── notes.txt
│   └── memory.json
├── scripts/
│   └── test_runner.py
├── tests/
│   └── test_ai_mini.py
└── .venv/
```
