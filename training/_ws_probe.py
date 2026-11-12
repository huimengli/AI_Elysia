import asyncio, json, sys
import websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:7860/ws") as ws:
        first = json.loads(await ws.recv())
        print("first:", first)
        await ws.send(json.dumps({"type": "chat", "text": "请只回复：好"}))
        for _ in range(30):
            raw = await asyncio.wait_for(ws.recv(), timeout=120)
            msg = json.loads(raw)
            print("msg:", msg.get("type"), "|", (msg.get("text") or msg.get("message") or "")[:100])
            if msg.get("type") == "response":
                break
    return 0

sys.exit(asyncio.run(main()))
