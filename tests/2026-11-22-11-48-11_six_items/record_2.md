# 轮 2 · cmd 窗口只留三样与爱莉希雅日志（第 2 条）

- **时间**：2026-11-22-12:33 → 12:44
- **场景**：重启 jarvis（含新 services.py/main.py/wake.py/stt.py/tts.py），40 s 与 120 s 后截 cmd 窗口；同时看页面板与 .tmp/*.log。
- **期望**：cmd 窗口只有「爱莉希雅已经启动 http://127.0.0.1:7860」+ 网址 + 报错；爱莉希雅自己的日志进环并落盘。
- **实际**：120 s 后截图 .tmp/jarvis_console6.png 只有 1 行「爱莉希雅已经启动 http://127.0.0.1:7860」；面板 3 个（llama / tts / 爱莉希雅），jarvis.log 1201 行、llama.log 13 行、tts.log 74 行、monitor.log 156 行。
- **结果**：**PASS**。
- **备注**：记第 175 处——我把 wake.py:104 改 svc.jlog 时，函数内原有局部「from jarvis import services as svc」让 svc 变局部变量 → UnboundLocalError 跑死 jarvis，控制台截图 .tmp/jarvis_console2.png 显示 traceback + RuntimeError: can't create new thread at interpreter shutdown；第 179 处（_reader 直接塞环绕过 _log，服务日志一条文件都没写）；第 187 处（我用了改前号、漏 [Wake] peak / [TTS] output stream warmed 等站点，并把 peak 归进 jerr → 每拍刷屏）。F2 打字提示保留 → Q46（status: wait）。
