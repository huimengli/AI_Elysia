# 第 1 轮（灯体真窗口截图 + 四灯逐字对照，2026-11-23-13:06）· P2-4 第 1 轮

- **时间**：2026-11-23 13:04–13:06（本地）。jarvis 在线（12:19:44 起，pid 5924，`:7860`），测试桩不弹浏览器；本轮用 `dispatch('open_url')`（`.tmp/open_jarvis_win_2026-11-23.py`）让 **jarvis 自己起一个真窗口**。
- **场景**：真窗口截图（`computer_screenshot` 带 `window_id`，整窗口 1470×1040），与只读取证口 `GET /api/monitor` 的 `lamps` 逐字对照；页里的灯标签用 `browser_cdp.evaluate` 直读。
- **期望**：截图里「四灯」这一排真渲染，灯色与 API 的 `online` 逐一对上；页里的灯标签逐字 = API 里的灯标签。
- **实际**：
  - 真窗口命中：`监视界面 — 爱莉希雅 - Google Chrome`，pid **17812**，bounds 100,0,1470,1040（`computer_windows` 列的 id，不是我的 DSH 标签页）。截图存 `C:\Users\楼听\Downloads\p24_lamp_win_2026-11-23.png`（1470×1040）。
  - 截图里读到的四灯：`四灯:` 一排 **wake 绿**、**asr 绿**、**llama.cpp (Local) 红**、**tts 红**，右边「**我起窗口 1/3**」。
  - `GET /api/monitor` 的 `lamps`：`wake online=true`（`aili_xiya_v1.3.onnx / threshold 0.75 / peak 0.195 / 上次触发 13:04:07`）、`asr online=true`（`faster-whisper small / cpu / zh（模型已加载=False）`）、`llm online=false`（`llama.cpp (Local) @ http://127.0.0.1:8080/v1`）、`tts online=false`（`GPT-SoVITS @ http://127.0.0.1:9880/tts`）—— 灯色与 `online` **四条全对上**（绿=在线，红=离线）。
  - `evaluate` 直读页里的灯标签：`["wake","asr","llama.cpp (Local)","tts"]` —— 与 API 的四个灯名**逐字相同**（顺序 wake→asr→llama→tts 也和页一致）。
- **结果**：**PASS**
- **环境事实（照第一手，不改代码）**：jarvis profile 起的 Chrome 带 `--no-sandbox` 警告横幅（页顶「您使用的是不受支持的命令行标记：--no-sandbox」，Q45 挂案）与「Chrome 未正确关闭」恢复横幅；**自起窗口存活很短**（13:04 起，13:05 窗口清单里就没了），截图必须紧跟 `open_url`。
