# 第 1 轮 · 带 HF 环境变量重启，asr.warm 立刻为 true

- 时间：2026-11-10 17:32–17:34
- 场景：`pwsh` 通道重启 Jarvis，显式带上 `HF_ENDPOINT=https://hf-mirror.com`、`HF_HOME=C:\Users\楼听\Desktop\git\JarvisAi\.hf-cache`、`HF_HUB_DISABLE_XET=1`；`main.py` 新增 `_warm_stt()` 在后台线程调 `jarvis.stt._get_model()`
- 期望：启动日志出现模型加载行（不再出现 `ConnectError 10054`），`/api/health` 的 `asr.warm=true`
- 实际（`.tmp\jarvis5.log` 前 9 行 + `.tmp\bats\h8.log`）：

```
[TTS] ack audio preloaded: 5 clips in memory
[STT] cuda failed to load (CUDA failed with error CUDA driver version is insufficient for CUDA runtime version), falling back to CPU
[STT] Loaded small on cpu
[STT] whisper warmed in 2866 ms
[TTS] output stream warmed in 2879 ms

"asr":{"online":true,"warm":true,"model":"small","language":"zh","device":"cpu",
      "detail":"faster-whisper small / cpu / zh（模型已加载=True）"}
```

- 结果：**PASS** — 模型从仓库内 `.hf-cache` 命中，无联网请求；`warm` 在启动后 2.9 s 就为 `true`（旧行为是首次真人转写时才加载，失败只在语音轮暴露）
- 备注：`config.yaml` 写 `device: cuda`，本机 CUDA 驱动版本不足 → `_get_model()` 按既有逻辑自动回退 CPU（`stt.py:32-37`），日志如实记录，属正确行为；wake/tts/llm 三灯同时正常（`threshold=0.7`、`listening=true`、`llm online`、`tts online`）
