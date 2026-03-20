"""Live web search and page fetch tools for current model data."""

import functools
import json
import re

import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS


def web_search(query: str, max_results: int = 8) -> str:
    """Search the web for current information about AI models, benchmarks, pricing, and leaderboards.

    Use this as the primary way to find up-to-date data. Good for:
    - Current model rankings and leaderboard positions
    - Latest benchmark results for a specific task (e.g., "best OCR model benchmark 2026")
    - Current API pricing (e.g., "claude sonnet pricing per million tokens")
    - New model releases (e.g., "best small multilingual LLM 2026")
    - Specific capability comparisons (e.g., "Qwen2.5 vs LLaMA3 multilingual benchmark")

    Args:
        query: Search query. Be specific — include the task, year, and relevant constraints.
               Example: "best open source OCR model low GPU 2026 multilingual benchmark"
        max_results: Number of results to return (default 8).

    Returns:
        JSON string with search results, each containing 'title', 'href', and 'body' snippet.
    """
    original_query = query
    for attempt in range(2):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if results:
                return json.dumps(results, indent=2)

            # Empty results — likely rate-limited. Retry with a shorter query.
            if attempt == 0:
                query = " ".join(original_query.split()[:6])

        except Exception as exc:
            if attempt == 1:
                return json.dumps({
                    "error": str(exc),
                    "warning": "Web search is currently unavailable. DO NOT RETRY web_search. Proceed with your other available tools.",
                    "results": [],
                })

    return json.dumps({
        "warning": "No results returned. DO NOT RETRY web_search. Proceed with your other available tools instead.",
        "results": [],
    })


@functools.lru_cache(maxsize=64)
def fetch_webpage(url: str) -> str:
    """Fetch and extract the text content of a webpage.

    Use this to read specific pages found via web_search — e.g., a model's documentation,
    a leaderboard page, a pricing page, or a benchmark results page.
    Results are cached for the session to avoid redundant HTTP requests.

    Args:
        url: Full URL to fetch (must start with http:// or https://).

    Returns:
        Cleaned text content of the page (up to 6000 characters).
    """
    if not url.startswith(("http://", "https://")):
        return f"Invalid URL: {url}"

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "html" in content_type:
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            text = re.sub(r"\n{3,}", "\n\n", text)
        else:
            text = resp.text

        return text[:6000]
    except Exception as exc:
        return f"Failed to fetch {url}: {exc}"
