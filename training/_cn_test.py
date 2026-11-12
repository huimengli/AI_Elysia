"""Temp e2e: verify 爱莉希雅 self-reference + forced Chinese via WS chat."""
import asyncio
import json
import sys
import time

import websockets

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


async def main():
    uri = "ws://127.0.0.1:7860/ws"
    t0 = time.time()
    async with websockets.connect(uri, open_timeout=15) as ws:
        # drain connect message
        try:
            await asyncio.wait_for(ws.recv(), timeout=5)
        except asyncio.TimeoutError:
            pass
        await ws.send(json.dumps({"type": "chat", "text": "你叫什么名字？请用一两句话介绍自己。"}))
        response_parts = []
        recv_log = open("_cn_test_recv.log", "w", encoding="utf-8")
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=600)
            recv_log.write(f"[{time.time()-t0:.1f}s] {raw[:200]}\n")
            recv_log.flush()
            msg = json.loads(raw)
            mtype = msg.get("type")
            if mtype == "response":
                response_parts.append(msg.get("text", ""))
                break  # server sends one complete response per chat
            elif mtype == "status" and msg.get("message") in ("正在说话…",):
                continue
        elapsed = time.time() - t0
        text = "".join(response_parts)
        with open("_cn_test_result.log", "w", encoding="utf-8") as f:
            f.write(f"elapsed={elapsed:.1f}s\nresponse={text!r}\n")
            has_name = "爱莉希雅" in text
            # crude Chinese check: CJK chars dominate
            cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
            is_chinese = cjk >= max(5, len(text) // 3)
            ok = has_name and is_chinese
            f.write(f"has_elysia_name={has_name} cjk_ratio_ok={is_chinese}\nE2E_CN_RESULT: overall={'PASS' if ok else 'FAIL'}\n")


asyncio.run(main())
