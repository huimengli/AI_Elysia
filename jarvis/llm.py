"""Lightweight LLM chat function for internal tasks (context summarization, etc.)."""
from pathlib import Path
import yaml

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def _load_config():
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def chat(messages: list[dict]) -> str:
    """Send messages to the active LLM provider and return response text.

    Uses the same provider system as main.py — reads active_provider from config.
    Used for internal tasks like context summarization.
    """
    cfg = _load_config()
    llm_cfg = cfg.get("llm", {})
    temperature = llm_cfg.get("temperature", 0.7)
    active = llm_cfg.get("active_provider", "ollama")
    providers = llm_cfg.get("providers", {})
    provider = providers.get(active, {})
    ptype = provider.get("type", "ollama")

    if ptype == "openai":
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url=provider["base_url"],
                api_key=provider.get("api_key", "lm-studio"),
                # 15 s killed 2B generations mid-flight, which pushed summarization
                # and subagents onto the (not-running) Ollama fallback.
                timeout=90.0,
            )
            resp = client.chat.completions.create(
                model=provider["model"],
                messages=messages,
                temperature=temperature,
                # llama.cpp needs the flag explicitly: without it Qwen3.x spends
                # the whole budget on reasoning_content and content comes back empty
                # (see records/2026-11-08-17-29-39.md round 1).
                extra_body={"chat_template_kwargs": {"enable_thinking": llm_cfg.get("enable_thinking", False)}},
            )
            return resp.choices[0].message.content or ""
        except Exception:
            pass  # fall through to Ollama

    # Ollama (default or fallback)
    import ollama
    ollama_cfg = providers.get("ollama", provider)
    model = ollama_cfg.get("model", "qwen3:8b")
    try:
        response = ollama.chat(model=model, messages=messages)
        return response.message.content or ""
    except Exception as e:
        return f"[LLM error: {e}]"
