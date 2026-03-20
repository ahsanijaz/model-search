import ollama


def get_models() -> list[tuple[str, str]]:
    try:
        response = ollama.list()
        return [(m.model, m.model) for m in response.models]
    except Exception:
        return []


def stream_chat(model_id: str, messages: list[dict]):
    stream = ollama.chat(model=model_id, messages=messages, stream=True)
    for chunk in stream:
        content = chunk.get("message", {}).get("content", "")
        if content:
            yield content
