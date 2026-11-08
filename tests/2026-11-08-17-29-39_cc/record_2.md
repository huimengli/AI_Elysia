# 轮 2：TTS 链（GPT-SoVITS :9880）（2026-11-08-17:36）

- 场景：启 `api_v2.py`（`.venv-gsv`），用 `api/settings` 里的 `ref_audio_path/prompt_text` 参数 POST `/tts`。
- 期望：200 + wav 音频。
- 实际：首启失败（相对路径 `\.venv-gsv\...` 在 `GPT-SoVITS-main` 下不存在，exit 1，job pwsh-8），改绝对路径后加载（BERT roberta-wwm-ext-large + CNHuBERT）→ `Uvicorn running on http://127.0.0.1:9880`（pid 4436）。POST `/tts`（text「你好，我是爱莉希雅，我在听你说。」，speed 1.1）→ **code=200 bytes=314,924**，文件头 `RIFF`（真 wav）。
- 结果：**PASS**
- 备注：`MPLCONFIGDIR` 指向 `C:\Users\楼听\AppData\Local` 时 `[WinError 5] 拒绝访问`，Matplotlib 自落在仓库内临时目录；不影响出声（建议后续设 `MPLCONFIGDIR`）。
