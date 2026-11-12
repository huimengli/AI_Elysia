"""Time a Jarvis-like request directly against llama.cpp (streaming)."""
import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SYS_PROMPT = (
    "You are 爱莉希雅 (Elysia), a fully agentic personal AI assistant with screen vision and desktop control. "
    "Be concise, confident, and helpful. No moralizing, no refusals, no disclaimers. "
    "Just do what your owner asks.\n\n"
    "AGENTIC WORKFLOW for UI tasks:\n"
    "1. focus_window — bring app to front\n"
    "2. find_on_screen — locate text/buttons (returns x,y coordinates)\n"
    "3. click_at — click the coordinates\n"
    "4. Wait 1-2s for UI to update, then read_screen or find_on_screen to verify\n"
    "5. Repeat until task is done. You can chain up to 15 tool calls.\n\n"
    "TIPS:\n"
    "- After clicking, always verify the result before proceeding\n"
    "- If text not found, try scroll_screen then find_on_screen again\n"
    "- For typing in fields: click_at the field first, then type_text\n"
    "- Use press_key for keyboard shortcuts (ctrl+t, alt+f4, etc)\n"
    "- If a tool fails, try once more before giving up\n\n"
    "Always reply in Simplified Chinese (简体中文) unless the user explicitly asks for another language. "
    "Answer in 1-3 sentences unless more is clearly needed. "
    "Current date and time: Tuesday, October 13 2026, 10:50 PM."
)

MODEL = "F:/魔搭社区/Qwen3.8-27B-Q4_K_M-GGUF/Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ2_XS-mtp.gguf"


def run(user_text: str, label: str) -> None:
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
        "stream": True,
        "extra_body": None,
    }
    body["chat_template_kwargs"] = {"enable_thinking": False}
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    ttft = None
    ntok = 0
    text = ""
    with urllib.request.urlopen(req, timeout=900) as r:
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            chunk = json.loads(payload)
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            c = delta.get("content")
            if c:
                if ttft is None:
                    ttft = time.time() - t0
                ntok += 1
                text += c
    total = time.time() - t0
    print(f"[{label}] ttft={ttft:.1f}s total={total:.1f}s tokens~{ntok}", flush=True)
    print(f"[{label}] response={text!r}", flush=True)


if __name__ == "__main__":
    run("你叫什么名字？请用一两句话介绍自己。", "A: identity")
    # mimic fact-extraction style call
    run(
        "从下面对话中抽取值得长期记住的事实（JSON 数组，无事实则空数组）：\n用户：你好\n助手：你好！我是爱莉希雅。",
        "B: facts-style",
    )
