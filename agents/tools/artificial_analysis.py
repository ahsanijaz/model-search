"""Artificial Analysis model performance, cost, and speed data.

Static dataset sourced from https://artificialanalysis.ai/leaderboards/models
Updated: early 2026. Refresh periodically from the source.
"""

import json

# Static performance data: speed, cost, context, quality
# quality_index: Artificial Analysis quality score (0–100)
PERFORMANCE_DATA = [
    # === Anthropic ===
    {
        "model": "claude-opus-4-6",
        "provider": "Anthropic",
        "type": "API",
        "context_k": 200,
        "output_tokens_per_sec": 32,
        "input_cost_per_m": 15.0,
        "output_cost_per_m": 75.0,
        "quality_index": 88,
        "license": "Proprietary",
        "hf_url": None,
    },
    {
        "model": "claude-sonnet-4-6",
        "provider": "Anthropic",
        "type": "API",
        "context_k": 200,
        "output_tokens_per_sec": 85,
        "input_cost_per_m": 3.0,
        "output_cost_per_m": 15.0,
        "quality_index": 83,
        "license": "Proprietary",
        "hf_url": None,
    },
    {
        "model": "claude-haiku-4-5",
        "provider": "Anthropic",
        "type": "API",
        "context_k": 200,
        "output_tokens_per_sec": 210,
        "input_cost_per_m": 0.8,
        "output_cost_per_m": 4.0,
        "quality_index": 71,
        "license": "Proprietary",
        "hf_url": None,
    },
    # === OpenAI ===
    {
        "model": "gpt-4.1",
        "provider": "OpenAI",
        "type": "API",
        "context_k": 128,
        "output_tokens_per_sec": 120,
        "input_cost_per_m": 2.0,
        "output_cost_per_m": 8.0,
        "quality_index": 84,
        "license": "Proprietary",
        "hf_url": None,
    },
    {
        "model": "gpt-4o-mini",
        "provider": "OpenAI",
        "type": "API",
        "context_k": 128,
        "output_tokens_per_sec": 190,
        "input_cost_per_m": 0.15,
        "output_cost_per_m": 0.6,
        "quality_index": 68,
        "license": "Proprietary",
        "hf_url": None,
    },
    # === Google ===
    {
        "model": "gemini-2.5-pro",
        "provider": "Google",
        "type": "API",
        "context_k": 1000,
        "output_tokens_per_sec": 75,
        "input_cost_per_m": 1.25,
        "output_cost_per_m": 10.0,
        "quality_index": 87,
        "license": "Proprietary",
        "hf_url": None,
    },
    {
        "model": "gemini-2.0-flash",
        "provider": "Google",
        "type": "API",
        "context_k": 1000,
        "output_tokens_per_sec": 380,
        "input_cost_per_m": 0.075,
        "output_cost_per_m": 0.30,
        "quality_index": 74,
        "license": "Proprietary",
        "hf_url": None,
    },
    {
        "model": "gemini-2.0-flash-lite",
        "provider": "Google",
        "type": "API",
        "context_k": 1000,
        "output_tokens_per_sec": 500,
        "input_cost_per_m": 0.02,
        "output_cost_per_m": 0.08,
        "quality_index": 62,
        "license": "Proprietary",
        "hf_url": None,
    },
    # === Meta (Llama) ===
    {
        "model": "llama-4-maverick",
        "provider": "Meta",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 145,
        "input_cost_per_m": 0.22,
        "output_cost_per_m": 0.88,
        "quality_index": 80,
        "license": "Llama 4 Community",
        "hf_url": "https://huggingface.co/meta-llama/Llama-4-Maverick",
    },
    {
        "model": "llama-3.3-70b-instruct",
        "provider": "Meta",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 180,
        "input_cost_per_m": 0.23,
        "output_cost_per_m": 0.40,
        "quality_index": 72,
        "license": "Llama 3.3 Community",
        "hf_url": "https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct",
    },
    {
        "model": "llama-3.1-8b-instruct",
        "provider": "Meta",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 580,
        "input_cost_per_m": 0.05,
        "output_cost_per_m": 0.08,
        "quality_index": 55,
        "license": "Llama 3.1 Community",
        "hf_url": "https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct",
    },
    # === DeepSeek ===
    {
        "model": "deepseek-v3",
        "provider": "DeepSeek",
        "type": "Open/API",
        "context_k": 128,
        "output_tokens_per_sec": 95,
        "input_cost_per_m": 0.27,
        "output_cost_per_m": 1.10,
        "quality_index": 78,
        "license": "MIT",
        "hf_url": "https://huggingface.co/deepseek-ai/DeepSeek-V3",
    },
    {
        "model": "deepseek-r1",
        "provider": "DeepSeek",
        "type": "Open/API",
        "context_k": 128,
        "output_tokens_per_sec": 55,
        "input_cost_per_m": 0.55,
        "output_cost_per_m": 2.19,
        "quality_index": 82,
        "license": "MIT",
        "hf_url": "https://huggingface.co/deepseek-ai/DeepSeek-R1",
    },
    # === Alibaba (Qwen) ===
    {
        "model": "qwen3-235b-a22b",
        "provider": "Alibaba",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 65,
        "input_cost_per_m": 0.22,
        "output_cost_per_m": 0.88,
        "quality_index": 79,
        "license": "Apache 2.0",
        "hf_url": "https://huggingface.co/Qwen/Qwen3-235B-A22B",
    },
    {
        "model": "qwen2.5-72b-instruct",
        "provider": "Alibaba",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 165,
        "input_cost_per_m": 0.20,
        "output_cost_per_m": 0.35,
        "quality_index": 73,
        "license": "Apache 2.0",
        "hf_url": "https://huggingface.co/Qwen/Qwen2.5-72B-Instruct",
    },
    {
        "model": "qwen2.5-7b-instruct",
        "provider": "Alibaba",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 450,
        "input_cost_per_m": 0.03,
        "output_cost_per_m": 0.06,
        "quality_index": 58,
        "license": "Apache 2.0",
        "hf_url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct",
    },
    # === Mistral ===
    {
        "model": "mistral-large-2411",
        "provider": "Mistral",
        "type": "Open/API",
        "context_k": 128,
        "output_tokens_per_sec": 95,
        "input_cost_per_m": 2.0,
        "output_cost_per_m": 6.0,
        "quality_index": 70,
        "license": "Mistral Research",
        "hf_url": "https://huggingface.co/mistralai/Mistral-Large-Instruct-2411",
    },
    {
        "model": "mistral-nemo-12b",
        "provider": "Mistral",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 255,
        "input_cost_per_m": 0.03,
        "output_cost_per_m": 0.10,
        "quality_index": 55,
        "license": "Apache 2.0",
        "hf_url": "https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407",
    },
    # === Microsoft ===
    {
        "model": "phi-4",
        "provider": "Microsoft",
        "type": "Open",
        "context_k": 16,
        "output_tokens_per_sec": 350,
        "input_cost_per_m": 0.07,
        "output_cost_per_m": 0.28,
        "quality_index": 67,
        "license": "MIT",
        "hf_url": "https://huggingface.co/microsoft/phi-4",
    },
    # === Google (Gemma) ===
    {
        "model": "gemma-3-27b-it",
        "provider": "Google",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 130,
        "input_cost_per_m": 0.15,
        "output_cost_per_m": 0.50,
        "quality_index": 68,
        "license": "Gemma",
        "hf_url": "https://huggingface.co/google/gemma-3-27b-it",
    },
    {
        "model": "gemma-3-4b-it",
        "provider": "Google",
        "type": "Open",
        "context_k": 128,
        "output_tokens_per_sec": 600,
        "input_cost_per_m": 0.03,
        "output_cost_per_m": 0.10,
        "quality_index": 50,
        "license": "Gemma",
        "hf_url": "https://huggingface.co/google/gemma-3-4b-it",
    },
]


def get_model_performance_data(model_name: str = "") -> str:
    """Look up cost, speed, context length, and quality data for AI models.

    Use this to compare pricing ($/M tokens), throughput (tokens/sec), context window,
    and quality index across API and open-source models from Artificial Analysis.

    Args:
        model_name: Optional model name to filter results (partial match, case-insensitive).
                    E.g. "llama", "claude", "gemini". Leave empty to get the full table.

    Returns:
        JSON string with matching model performance data including input/output cost,
        tokens per second, context window (in thousands), quality index, license, and
        whether it is an API or open-source model. Reference: https://artificialanalysis.ai
    """
    if not model_name:
        return json.dumps(
            {"source": "artificialanalysis.ai (static)", "models": PERFORMANCE_DATA},
            indent=2,
        )

    needle = model_name.lower()
    matches = [
        m
        for m in PERFORMANCE_DATA
        if needle in m["model"].lower() or needle in m["provider"].lower()
    ]

    if matches:
        return json.dumps(
            {"source": "artificialanalysis.ai (static)", "models": matches},
            indent=2,
        )

    # No match — return full table so agent has context
    return json.dumps(
        {
            "source": "artificialanalysis.ai (static)",
            "note": f"No exact match for '{model_name}'. Full table returned.",
            "models": PERFORMANCE_DATA,
        },
        indent=2,
    )
