# Nexus AI

An AI model recommendation app. Describe your task and constraints — Nexus AI searches live leaderboards, fetches model cards, and recommends the top 3 models with a side-by-side comparison table and an expert critique.

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/streamlit-1.40%2B-red) ![License](https://img.shields.io/badge/license-MIT-green)

## What it does

Type something like *"cheap multilingual OCR with high throughput"* or *"best open-source coding model under 8B parameters"* and the app will:

1. Search HuggingFace Hub for relevant models
2. Pull live ELO rankings from Chatbot Arena
3. Run targeted web searches for benchmark results and pricing
4. Return the top 3 recommendations with a comparison table, per-model cards, and a plain-English critique

Follow-up messages like *"make it cheaper"* or *"open source only"* refine the ranking without re-fetching everything.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Add your Anthropic API key
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# Run
streamlit run app.py
```

Get an API key at [console.anthropic.com](https://console.anthropic.com).

## How it works

Two agents run in sequence, powered by Claude Sonnet 4.6 via Google ADK:

```
data_gatherer  →  critic
 (5 tools)         (no tools)
```

**data_gatherer** uses these tools to gather live data:
- `search_hf_models` — HuggingFace Hub REST API
- `get_hf_model_card` — fetches model README from HF CDN
- `get_chatbot_arena_leaderboard` — live CSV from lmarena.ai (HF Spaces)
- `web_search` — DuckDuckGo search for benchmarks, pricing, release notes
- `fetch_webpage` — reads specific pages found via search

**critic** receives the gathered data (injected from ADK session state) and produces a structured JSON response rendered as model cards and a comparison table.

## Docker

```bash
docker build -t nexus-ai .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=sk-ant-... nexus-ai
```

## Project structure

```
app.py                  # Streamlit UI
agents/
  orchestrator.py       # ADK pipeline + async/sync bridge
  prompts.py            # System prompts for both agents
  tools/
    web_search.py       # DuckDuckGo search + page fetch
    huggingface.py      # HF Hub search + model cards
    lmsys.py            # Chatbot Arena leaderboard
    artificial_analysis.py
    papers_with_code.py
styles.css              # Dark glassmorphism theme
```
