# 轮 3：TTS 与端口终态（2026-11-08-18:23）

- 场景：分支切换后三服务是否仍在线，TTS 出声链是否不受影响。
- 期望：`:8080`/`:9880` 保持，`:7860` 由 main 代码提供，TTS 出 wav。
- 实际：`POST /tts`（:9880，同一 `ref_audio_path` 参数）→ **code=200 / 271,404 B / `RIFF`**；`jarvis.main`（job pwsh-21）日志 `Web UI: http://localhost:7860` + `Listening for wake word...`；`:8080` llama-server 与 `:9880` GPT-SoVITS（job pwsh-10，pid 4436）未重启、与分支无关。
- 结果：**PASS**
- 备注：看 UI 差异只需刷新 http://127.0.0.1:7860 ；回 Elysia 版用 `git checkout future/AI_UI` 后重启 jarvis（`Stop-Process` 旧 python 再启）。
