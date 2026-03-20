"""LMSYS / lmarena Chatbot Arena ELO leaderboard tool."""

import csv
import io
import json

import httpx
from ddgs import DDGS

ARENA_CSV_URL = (
    "https://huggingface.co/spaces/lmarena-ai/arena-leaderboard"
    "/resolve/main/leaderboard_table_df.csv"
)


def get_chatbot_arena_leaderboard(top_n: int = 30) -> str:
    """Fetch the Chatbot Arena ELO leaderboard with human preference rankings.

    Tries the live CSV from HuggingFace Spaces first. Falls back to a live
    web search for current rankings if the CSV is unavailable.

    Args:
        top_n: Number of top-ranked models to return (default 30, max 50).

    Returns:
        JSON string with ranked models including ELO score, organization, and license.
    """
    top_n = min(top_n, 50)

    # 1. Try the live CSV
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            resp = client.get(ARENA_CSV_URL)
            if resp.status_code == 200 and resp.text.strip():
                reader = csv.DictReader(io.StringIO(resp.text))
                rows = list(reader)[:top_n]
                if rows:
                    return json.dumps(
                        {"source": "live_lmarena_csv", "leaderboard": rows},
                        indent=2,
                    )
    except Exception:
        pass

    # 2. Fallback: live web search for current rankings
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                "chatbot arena leaderboard ELO rankings lmarena site:lmarena.ai OR site:huggingface.co",
                max_results=5,
            ))
        return json.dumps(
            {
                "source": "web_search_fallback",
                "note": "Live CSV unavailable. Use these search snippets to find current rankings. See https://lmarena.ai/leaderboard for the full table.",
                "search_results": results,
            },
            indent=2,
        )
    except Exception as exc:
        return json.dumps(
            {"source": "unavailable", "error": str(exc),
             "note": "Check https://lmarena.ai/leaderboard manually."},
            indent=2,
        )
