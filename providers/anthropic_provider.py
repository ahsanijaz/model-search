from anthropic import Anthropic

MODELS = [
    ("claude-opus-4-6", "Claude Opus 4.6"),
    ("claude-sonnet-4-6", "Claude Sonnet 4.6"),
    ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
]


def get_models() -> list[tuple[str, str]]:
    return MODELS


def stream_chat(model_id: str, messages: list[dict], api_key: str):
    client = Anthropic(api_key=api_key)
    with client.messages.stream(
        model=model_id,
        max_tokens=4096,
        messages=messages,
    ) as stream:
        yield from stream.text_stream
