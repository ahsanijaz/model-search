"""HuggingFace Hub search and model card retrieval tools."""

import json

import httpx

HF_API_BASE = "https://huggingface.co/api"
HF_CDN_BASE = "https://huggingface.co"


def search_hf_models(query: str, task: str = "", limit: int = 20) -> str:
    """Search HuggingFace Hub for AI models matching a query string and optional task type.

    Args:
        query: Keywords to search (e.g., "multilingual OCR", "code generation", "small fast LLM").
        task: HuggingFace pipeline tag to filter results (e.g., "text-generation",
              "token-classification", "image-to-text", "automatic-speech-recognition").
              Leave empty to search across all tasks.
        limit: Maximum number of results to return (default 20, max 100).

    Returns:
        JSON string with a list of model metadata including model_id, downloads, likes,
        pipeline_tag, tags, and whether the model is gated (requires approval).
    """
    params: dict = {
        "search": query,
        "sort": "downloads",
        "direction": -1,
        "limit": limit,
    }
    if task:
        params["filter"] = task

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{HF_API_BASE}/models", params=params)
            resp.raise_for_status()
        models = resp.json()
        trimmed = [
            {
                "model_id": m.get("modelId") or m.get("id", ""),
                "downloads": m.get("downloads", 0),
                "likes": m.get("likes", 0),
                "pipeline_tag": m.get("pipeline_tag", ""),
                "tags": (m.get("tags") or [])[:12],
                "gated": bool(m.get("gated", False)),
            }
            for m in models
        ]
        return json.dumps(trimmed, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc), "models": []})


def get_hf_model_card(model_id: str) -> str:
    """Fetch the model card (README) and metadata for a specific HuggingFace model.

    Args:
        model_id: Full HuggingFace model ID, e.g. "mistralai/Mistral-7B-v0.1" or
                  "microsoft/phi-3-mini-4k-instruct".

    Returns:
        The model card text (up to 4000 characters) with key metadata including
        license, languages, tags, and task type. Returns a JSON fallback if the
        README is unavailable.
    """
    readme_url = f"{HF_CDN_BASE}/{model_id}/resolve/main/README.md"
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(readme_url)
            if resp.status_code == 200:
                text = resp.text[:4000]
                return f"=== Model Card: {model_id} ===\n{text}"

            # Fallback: API metadata
            api_resp = client.get(f"{HF_API_BASE}/models/{model_id}")
            if api_resp.status_code == 200:
                data = api_resp.json()
                card_data = data.get("cardData") or {}
                return json.dumps(
                    {
                        "model_id": model_id,
                        "pipeline_tag": data.get("pipeline_tag", ""),
                        "tags": (data.get("tags") or [])[:20],
                        "license": card_data.get("license", "unknown"),
                        "language": card_data.get("language", []),
                        "library_name": data.get("library_name", ""),
                        "downloads": data.get("downloads", 0),
                        "likes": data.get("likes", 0),
                        "url": f"https://huggingface.co/{model_id}",
                    },
                    indent=2,
                )
    except Exception as exc:
        return f"Error fetching model card for {model_id}: {exc}"

    return f"Model card not available for {model_id}"
