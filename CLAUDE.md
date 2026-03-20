# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in API key
cp .env.example .env   # add ANTHROPIC_API_KEY

# Run the app
streamlit run app.py
```

## Architecture

This is an AI model recommendation app. The user describes a task and constraints (e.g. "cheap multilingual OCR with high throughput"), and a Google ADK multi-agent pipeline searches AI leaderboards, fetches model cards, and returns top 3 recommendations with a side-by-side comparison table and expert critique.

### Agent pipeline (`agents/`)

Two-agent `SequentialAgent` pipeline powered by Claude via LiteLLM:

```
data_gatherer (LlmAgent + 6 tools) → critic (LlmAgent, no tools)
```

**`data_gatherer`** calls these tools in sequence:
1. `search_hf_models` — HuggingFace Hub REST API
2. `get_hf_model_card` — fetches raw README.md from HF CDN
3. `search_pwc_tasks` / `get_pwc_sota` — Papers with Code API (degrades gracefully if offline)
4. `get_chatbot_arena_leaderboard` — live CSV from HF Spaces, falls back to static snapshot
5. `get_model_performance_data` — static Artificial Analysis dataset (cost, speed, context)

The agent writes its final JSON output to session state via `output_key="gathered_data"`.

**`critic`** receives `{gathered_data}` injected by ADK from session state and produces a Markdown response with a comparison table, model cards, critique paragraph, and "similar models" section.

### Multi-turn support

`session_id` persists across follow-up messages in the same Streamlit conversation. The data_gatherer prompt instructs the agent to reuse existing `gathered_data` in session state for follow-ups like "make it cheaper" or "I need open source only", avoiding redundant leaderboard fetches.

### Streamlit + async bridge (`agents/orchestrator.py`)

ADK uses async; Streamlit is sync. `run_query()` submits each pipeline run to a `ThreadPoolExecutor` where a fresh `asyncio` event loop is created per call. This avoids all "loop already running" conflicts.

### Static data maintenance

Two files contain static data that should be refreshed periodically:
- `agents/tools/lmsys.py` → `STATIC_ARENA_DATA` — update from https://lmarena.ai/leaderboard
- `agents/tools/artificial_analysis.py` → `PERFORMANCE_DATA` — update from https://artificialanalysis.ai/leaderboards/models

### Adding a new data source

1. Add a tool function in `agents/tools/<source>.py` with a clear docstring (ADK uses it for tool schema generation).
2. Export it from `agents/tools/__init__.py`.
3. Add it to the `tools=[]` list in `_build_pipeline()` in `agents/orchestrator.py`.
4. Update `DATA_GATHERER_PROMPT` in `agents/prompts.py` to instruct the agent when to call it.

### Key technical notes

- `load_dotenv()` in `app.py` **must** run before the `agents.orchestrator` import — the ADK runner is a lazy singleton initialized on first call, but `ANTHROPIC_API_KEY` must already be in the environment.
- Tool functions must have Python type hints — ADK uses them to generate the tool JSON schema sent to the LLM.
- `output_key="gathered_data"` on the data_gatherer writes to session state; `{gathered_data}` in the critic's instruction substitutes it automatically (ADK state injection).
- Papers with Code was shut down by Meta in mid-2025 — those tools degrade gracefully.
