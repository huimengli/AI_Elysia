"""Smoke: 3 WS chat rounds → assert source=web events land in sqlite.

Run: python _smoke_ws.py   (Jarvis :7860 must be running)
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request

import websockets
import asyncio

BASE = "ws://127.0.0.1:7860/ws"


def get_events(limit: int = 50) -> list[dict]:
    with urllib.request.urlopen(f"http://127.0.0.1:7860/api/events?limit={limit}", timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))["events"]


async def one_round(ws_url: str, text: str, expect_marker: str) -> tuple[str, bool]:
    async with websockets.connect(ws_url) as ws:
        await ws.send(json.dumps({"type": "chat", "text": text}))
        deadline = time.time() + 180
        got = ""
        while time.time() < deadline:
            raw = await asyncio.wait_for(ws.recv(), timeout=deadline - time.time())
            msg = json.loads(raw)
            if msg.get("type") == "response":
                got = msg.get("text", "")
                break
    ok = expect_marker in got
    return got, ok


async def main() -> int:
    before_ids = {e["ts"] + e["kind"] + e["text"] for e in get_events(100)}
    prompts = [
        ("请用一句话自我介绍。", "爱莉希雅"),
        ("数字 42 加 8 等于多少？只答数字。", "50"),
        ("用三个字形容今天。", ""),  # any reply counts
    ]
    results = []
    for i, (text, marker) in enumerate(prompts, start=1):
        t0 = time.time()
        got, ok = await one_round(BASE, text, marker)
        dt = time.time() - t0
        results.append((i, text, got, ok, dt))
        print(f"[round {i}] {dt:.1f}s ok={ok} reply={got[:80]!r}")

    # give the DB a beat, then verify source=web rows appeared
    await asyncio.sleep(2)
    after = get_events(200)
    web_users = [e for e in after if e["kind"] == "user" and e["source"] == "web"]
    web_assist = [e for e in after if e["kind"] == "assistant" and e["source"] == "web"]
    new_users = [e for e in web_users if (e["ts"] + e["kind"] + e["text"]) not in before_ids]
    print(f"[db] web user events total={len(web_users)} new_this_run={len(new_users)}")
    print(f"[db] web assistant events total={len(web_assist)}")
    for e in new_users:
        print(f"[db]   {e['ts']} {e['text']!r}")

    all_ok = all(r[3] for r in results) and len(new_users) >= 1 and len(web_assist) >= 1
    print("SMOKE " + ("PASS" if all_ok else "FAIL"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
