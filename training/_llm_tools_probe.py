"""Exact replica of _call_openai_provider: tools + max_tokens=2048 + streaming.

Times each tool loop and total to explain >600s WS hangs.
"""
import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI  # noqa: E402
from jarvis.tools.router import TOOL_SCHEMAS  # noqa: E402

MODEL = "F:/魔搭社区/Qwen3.8-27B-Q4_K_M-GGUF/Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ2_XS-mtp.gguf"
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="llamacpp")

messages = [
    {"role": "system", "content": "You are 爱莉希雅 (Elysia), a helpful AI assistant. Always reply in Simplified Chinese."},
    {"role": "user", "content": "你叫什么名字？请用一两句话介绍自己。"},
]

t_start = time.time()
for loop in range(1, 6):  # cap at 5 loops for the probe; server uses 15
    t_loop = time.time()
    content_parts: list[str] = []
    tool_acc: dict[int, dict] = {}
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMAS,
        temperature=0.7,
        max_tokens=2048,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        stream=True,
    )
    for chunk in stream:
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            content_parts.append(delta.content)
        tcs = getattr(delta, "tool_calls", None)
        if tcs:
            for tc in tcs:
                slot = tool_acc.setdefault(tc.index, {"id": "", "name": "", "arguments": ""})
                if tc.id:
                    slot["id"] = tc.id
                fn = tc.function
                if fn is not None:
                    if fn.name:
                        slot["name"] += fn.name
                    if fn.arguments:
                        slot["arguments"] += fn.arguments
    loop_dt = time.time() - t_loop
    text = "".join(content_parts)
    if tool_acc:
        names = [s.get("name") for s in tool_acc.values()]
        print(f"[loop {loop}] dt={loop_dt:.1f}s TOOL_CALLS={names}", flush=True)
        # do not actually execute tools; append a fake result to continue the loop
        messages.append({"role": "assistant", "content": None,
                         "tool_calls": [{"id": s.get("id") or f"call_{i}", "type": "function",
                                         "function": {"name": s["name"], "arguments": s["arguments"]}}
                                        for i, s in sorted(tool_acc.items())]})
        for i, s in sorted(tool_acc.items()):
            messages.append({"role": "tool", "content": "OK (fake result)",
                             "tool_call_id": s.get("id") or f"call_{i}"})
    else:
        print(f"[loop {loop}] dt={loop_dt:.1f}s FINAL text={text[:120]!r}", flush=True)
        break

print(f"PROBE_TOTAL={time.time()-t_start:.1f}s", flush=True)
