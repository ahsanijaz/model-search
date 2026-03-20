"""Papers with Code SOTA leaderboard tools.

NOTE: Papers with Code was shut down by Meta in mid-2025 and redirected to HuggingFace.
These tools attempt the API first and degrade gracefully on failure.
"""

import json

import httpx

PWC_BASE = "https://paperswithcode.com/api/v1"


def search_pwc_tasks(query: str) -> str:
    """Search Papers with Code for benchmark tasks related to a query.

    Args:
        query: Task description to search for, e.g. "optical character recognition",
               "machine translation", "image captioning", "question answering".

    Returns:
        JSON string with a list of matching tasks including their id, name, and
        short description. Returns a degraded message if the API is unavailable.
    """
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{PWC_BASE}/tasks/", params={"q": query, "limit": 10})
            resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or []
        trimmed = [
            {
                "id": t.get("id", ""),
                "name": t.get("name", ""),
                "description": (t.get("description") or "")[:250],
            }
            for t in results
        ]
        return json.dumps(trimmed, indent=2)
    except Exception as exc:
        return (
            f"Papers with Code API unavailable ({exc}). "
            "Skip this source and rely on HuggingFace and Chatbot Arena data instead."
        )


def get_pwc_sota(task_id: str) -> str:
    """Get state-of-the-art benchmark results for a Papers with Code task.

    Args:
        task_id: Task slug from search_pwc_tasks, e.g. "optical-character-recognition",
                 "machine-translation", "text-generation".

    Returns:
        JSON string with top models and their benchmark scores. Returns a degraded
        message if the API is unavailable.
    """
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{PWC_BASE}/sota/",
                params={"task": task_id, "limit": 10},
            )
            resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or []

        models = []
        for entry in results[:5]:
            for row in (entry.get("rows") or [])[:3]:
                models.append(
                    {
                        "model_name": row.get("model_name", ""),
                        "benchmark": (entry.get("benchmark") or {}).get("name", ""),
                        "metrics": row.get("metrics", {}),
                        "paper_title": (entry.get("paper") or {}).get("title", ""),
                    }
                )

        return json.dumps({"task": task_id, "sota": models}, indent=2)
    except Exception as exc:
        return (
            f"Papers with Code SOTA unavailable for task '{task_id}' ({exc}). "
            "Proceed with other data sources."
        )
