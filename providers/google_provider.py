from google import genai

MODELS = [
    ("gemini-2.0-flash", "Gemini 2.0 Flash"),
    ("gemini-2.0-flash-lite", "Gemini 2.0 Flash Lite"),
    ("gemini-1.5-pro", "Gemini 1.5 Pro"),
    ("gemini-1.5-flash", "Gemini 1.5 Flash"),
]


def get_models() -> list[tuple[str, str]]:
    return MODELS


def stream_chat(model_id: str, messages: list[dict], api_key: str):
    client = genai.Client(api_key=api_key)

    # Convert OpenAI-style messages to Google's format
    contents = [
        {
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}],
        }
        for msg in messages
    ]

    for chunk in client.models.generate_content_stream(
        model=model_id,
        contents=contents,
    ):
        if chunk.text:
            yield chunk.text
