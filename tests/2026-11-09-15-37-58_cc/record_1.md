# 验证第 1 轮：协议层（接口 / WS / 页面标记）

- 时间：2026-11-09 16:40 – 16:52
- 场景：设备重启后由 Agent 重新启动三个服务（llama.cpp `:8080`、GPT-SoVITS `:9880`、Jarvis `:7860`），随后用 `curl` 与 WebSocket 直连验证新接口，不依赖浏览器。
- 执行通道：`write` 生成 `.bat` → 资源管理器启动 → 「打开文件 - 安全警告」点「运行(R)」→ 输出重定向到 `.tmp\*.log` → 用 read 工具读取（遵守观测配额：几乎不截图）。
- 期望：
  1. `GET /api/health` 返回 asr / llm / tts 三项，且均为在线；
  2. WS `/ws` 连接即收到 connected 广播；
  3. `chat` 发送 `stop` 后收到「已停止。」应答；
  4. 页面 HTML 含新状态芯片（顺序：待命中/已离线/聆听中/说话中/执行中/思考中）、`svcLamps` 三盏灯与 `pollHealth` 轮询。
- 实际：
  1. `.tmp\h1.log`：`asr{online:true, warm:true, model:small, language:zh, device:cpu}`、`llm{online:true, provider:llamacpp, url:http://127.0.0.1:8080/v1}`、`tts{online:true, provider:gptsovits, url:http://127.0.0.1:9880/tts}`；
  2. `.tmp\ws1.log`：`CONNECTED-MESSAGES: 1`（`爱莉希雅已上线。`）；
  3. 同文件 `AFTER-STOP` 收到 `{"type":"response","text":"已停止。"}`，`STOP-RESPONSES: 1`；
  4. `.tmp\pagecheck.log`：命中 `.svc-lamps`、`.svc-lamp.off/warm/on`、`id="svcLamps"`、`lamp-asr/llm/tts`、`async function pollHealth()`、`pollHealth(); setInterval(pollHealth, 5000);`，芯片顺序与要求一致。
- 结果：**通过**（4/4）。
- 备注：`netstat` 证实监听 `:7860`(pid 1924)、`:8080`(pid 16876 llama-server)、`:9880`(pid 18284 python)；GPT-SoVITS 日志 `.tmp\gsv.log` 出现真实合成请求 `GET /tts … 200 OK`（CPU 回退，权重 Elysia e20/e24）。
