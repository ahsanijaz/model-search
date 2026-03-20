"""
ADK 2-agent pipeline: data_gatherer → critic.

Architecture:
- data_gatherer: LlmAgent (Claude via LiteLLM) with search tools.
  Writes its JSON output to session state under key "gathered_data".
- critic: LlmAgent (Claude via LiteLLM) with no tools.
  Reads {gathered_data} from session state via ADK's template injection.
- SequentialAgent runs data_gatherer then critic in sequence.

Both the Runner and InMemorySessionService are lazy singletons — built once
on first call after load_dotenv() has run in app.py.
"""

import asyncio
import os
import queue as queue_module
import threading
import uuid
from collections.abc import Generator
from typing import Optional

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agents.prompts import CRITIQUE_AGENT_PROMPT, DATA_GATHERER_PROMPT
from agents.tools import (
    fetch_webpage,
    get_chatbot_arena_leaderboard,
    get_hf_model_card,
    search_hf_models,
    web_search,
)

APP_NAME = "agents"
_MAX_SESSIONS = 50  # prune oldest sessions beyond this limit

# Lazy singletons — built once, reused across all requests
_runner: Optional[Runner] = None
_session_service: Optional[InMemorySessionService] = None
_init_lock = threading.Lock()

# Session registry for cleanup: ordered list of (user_id, session_id)
_session_registry: list[tuple[str, str]] = []


def _get_runner() -> tuple[Runner, InMemorySessionService]:
    """Thread-safe lazy singleton. Builds the full pipeline once after env vars are set."""
    global _runner, _session_service
    if _runner is None:
        with _init_lock:
            if _runner is None:  # double-checked locking
                if not os.getenv("ANTHROPIC_API_KEY"):
                    raise RuntimeError(
                        "ANTHROPIC_API_KEY is not set. Add it to your .env file."
                    )
                model = LiteLlm(model="anthropic/claude-sonnet-4-6")

                data_gatherer = LlmAgent(
                    name="data_gatherer",
                    model=model,
                    description="Searches HuggingFace, Chatbot Arena, and the web to gather live model data.",
                    instruction=DATA_GATHERER_PROMPT,
                    tools=[
                        web_search,
                        fetch_webpage,
                        search_hf_models,
                        get_hf_model_card,
                        get_chatbot_arena_leaderboard,
                    ],
                    output_key="gathered_data",
                )

                critic = LlmAgent(
                    name="critic",
                    model=model,
                    description="Synthesizes gathered model data into a top-3 recommendation.",
                    instruction=CRITIQUE_AGENT_PROMPT,
                )

                pipeline = SequentialAgent(
                    name="model_selector_pipeline",
                    description="Finds and recommends the best AI models for a given use case.",
                    sub_agents=[data_gatherer, critic],
                )

                _session_service = InMemorySessionService()
                _runner = Runner(
                    agent=pipeline,
                    app_name=APP_NAME,
                    session_service=_session_service,
                )

    return _runner, _session_service


async def _ensure_session(
    session_service: InMemorySessionService, user_id: str, session_id: str
) -> None:
    """Create session if new; prune oldest sessions when over _MAX_SESSIONS."""
    global _session_registry
    try:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        _session_registry.append((user_id, session_id))
    except Exception:
        return  # Already exists — multi-turn follow-up, nothing to do

    while len(_session_registry) > _MAX_SESSIONS:
        old_uid, old_sid = _session_registry.pop(0)
        try:
            await session_service.delete_session(APP_NAME, old_uid, old_sid)
        except Exception:
            pass


# ── Progress event labels ──────────────────────────────────────────────────────

_TOOL_LABELS: dict[str, str] = {
    "web_search": "Searching the web…",
    "fetch_webpage": "Reading page…",
    "search_hf_models": "Searching HuggingFace Hub…",
    "get_hf_model_card": "Fetching model card…",
    "get_chatbot_arena_leaderboard": "Fetching Chatbot Arena leaderboard…",
}

_AGENT_LABELS: dict[str, str] = {
    "data_gatherer": "Gathering live data from leaderboards and model cards…",
    "critic": "Synthesizing top-3 recommendations…",
}


async def _run_pipeline_streaming_async(
    query: str,
    session_id: str,
    user_id: str,
    progress_q: "queue_module.Queue[dict]",
) -> None:
    """Async pipeline that pushes typed progress events into a queue."""
    runner, session_service = _get_runner()
    await _ensure_session(session_service, user_id, session_id)

    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=query)],
    )

    seen_agents: set[str] = set()
    tool_call_counts: dict[str, int] = {}

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        # Detect agent phase transitions
        author_path = getattr(event, "author", "") or ""
        author = author_path.split("/")[-1] if "/" in author_path else author_path

        if author and author not in seen_agents and author in _AGENT_LABELS:
            seen_agents.add(author)
            if author == "critic":
                total = sum(tool_call_counts.values())
                label = (
                    f"Research complete ({total} searches) — synthesizing top 3…"
                    if total else _AGENT_LABELS[author]
                )
                progress_q.put({"type": "agent", "text": label})
            else:
                progress_q.put({"type": "agent", "text": _AGENT_LABELS[author]})

        # Detect tool calls — suppress large data blobs (>200 chars) from agent events
        if event.content and event.content.parts:
            for part in event.content.parts:
                fn_call = getattr(part, "function_call", None)
                if fn_call:
                    tool_call_counts[fn_call.name] = tool_call_counts.get(fn_call.name, 0) + 1
                    label = _TOOL_LABELS.get(fn_call.name, f"Calling `{fn_call.name}`…")
                    args = getattr(fn_call, "args", {}) or {}

                    if fn_call.name == "get_hf_model_card":
                        mid = args.get("model_id", "")
                        if mid:
                            label = f"Fetching model card: `{mid}`"
                    elif fn_call.name == "web_search":
                        q_text = args.get("query", "")
                        if q_text:
                            label = f"Searching: *{q_text[:80]}*"
                    elif fn_call.name == "fetch_webpage":
                        u = args.get("url", "")
                        if u:
                            label = f"Reading: {u[:70]}…"

                    progress_q.put({"type": "tool", "text": label})

        if event.is_final_response():
            text = ""
            if event.content and event.content.parts:
                text = event.content.parts[0].text or ""
            progress_q.put({"type": "result", "text": text or "No response generated."})
            return

    progress_q.put({"type": "result", "text": "No response generated."})


def stream_query(
    query: str,
    session_id: Optional[str] = None,
    user_id: str = "streamlit_user",
) -> Generator[dict, None, None]:
    """Synchronous generator that yields progress dicts then the final result.

    Yields:
        {"type": "agent", "text": str}   — agent phase announcement
        {"type": "tool",  "text": str}   — individual tool call
        {"type": "result","text": str}   — final JSON response
        {"type": "error", "text": str}   — on failure
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    progress_q: queue_module.Queue[dict] = queue_module.Queue()

    def _run_in_thread() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                _run_pipeline_streaming_async(query, session_id, user_id, progress_q)
            )
        except Exception as exc:
            progress_q.put({"type": "error", "text": str(exc)})
        finally:
            loop.close()

    thread = threading.Thread(target=_run_in_thread, daemon=True)
    thread.start()

    while True:
        try:
            item = progress_q.get(timeout=180)
            yield item
            if item["type"] in ("result", "error"):
                break
        except queue_module.Empty:
            yield {"type": "error", "text": "Timed out waiting for agent response."}
            break

    thread.join(timeout=5)
