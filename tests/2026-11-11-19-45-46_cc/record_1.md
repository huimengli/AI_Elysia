# 轮 1 — 配置切换 + 重启后 health 达标（2026-11-11 19:45–19:52）

- 时间：2026-11-11 19:45–19:52（`config.yaml` 改模型、`Stop-Process`/`Start-Process` 重启、`api/health` 探针；日志 `.tmp\jarvis8.log`）
- 场景：用户答复 `need_user.md` Q10 = 选项 1「先将模型切换到 0.6，我看看效果」。`config.yaml` `wake_word.model` 由 `aili_xiya_v0.3/aili_xiya_v0.3.onnx` 改为 `aili_xiya_v0.6/aili_xiya_v0.6.onnx`；`threshold` 保持 **0.7**、`chunk_size` 保持 1280（改前已读原文，用 `edit` 精确替换三行）。重启走「执行通道」既定命令：`Get-NetTCPConnection -LocalPort 7860 -State Listen` 找 pid（旧 pid 7580）→ `Stop-Process -Force` → `Start-Process .venv\Scripts\python.exe -u -m jarvis.main`，带齐 3 个 HF 变量（`HF_ENDPOINT=https://hf-mirror.com`、`HF_HOME=<repo>\.hf-cache`、`HF_HUB_DISABLE_XET=1`），stdout/stderr 重定向到 `.tmp\jarvis8.log`/`.tmp\jarvis8.err`。
- 期望：health `wake.model = aili_xiya_v0.6.onnx`、`threshold 0.7`、`listening=true`，4 灯全 online，`asr.warm=true`，llama `:8080` 与 GPT-SoVITS `:9880` 不受影响
- 实际（`api/health` 原文）：`wake.model = "aili_xiya_v0.6.onnx"`、`threshold: 0.7`、`listening: true`、`score 0.152`、`peak 0.185`、`last_detect 19:51:23`；`asr.online=true / warm=true / model small / cpu / zh`；`llm.online=true（llama.cpp :8080）`；`tts.online=true（GPT-SoVITS :9880）`。启动日志：`[STT] whisper warmed in 3384 ms`、`[TTS] output stream warmed in 4027 ms`、`[TTS] ack audio preloaded: 5 clips in memory`、`[爱莉希雅] Listening for wake word...`
- 结果：**PASS**
- 备注：首次 health 采样落在「检出后录音」窗口内，`listening` 显示 `false`（`[Wake] Mic paused for STT recording.`），6 s 与二次采样均为 `true`，属线上既有语义，非缺陷
