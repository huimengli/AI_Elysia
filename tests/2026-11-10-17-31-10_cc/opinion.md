# 批次结论 · 2026-11-10-17-31-10（ASR「不能转写」真因 + 启动预热）

**3/3 PASS**（零截图，全部走 `.tmp/*.log` + `Invoke-WebRequest` + WS 事件）

| 轮 | 期望 | 证据 | 结果 |
| --- | --- | --- | --- |
| ① 带 HF 环境变量重启 | 启动日志出现模型加载行、无 `ConnectError`、`asr.warm=true` | `.tmp\jarvis5.log:6-8`（`cuda failed to load … falling back to CPU` / `Loaded small on cpu` / `whisper warmed in 2866 ms`）+ `.tmp\bats\h8.log`（`asr warm=true, device cpu`） | PASS |
| ② 真人语音轮 | VAD 正常收尾、转写出文本、工具执行 | `.tmp\jarvis5.log:16-25`（`Speech detected rms=0.0222` → `Silence detected` → `Recorded 7.5s` → `[You] 我愛你 愛你 愛你` → `[Tool: press_key]` → `[Tool: get_time] 星期二`） | PASS |
| ③ WS 链路复测 | 连接/工具事件带中文 `label`/应答齐全，无回归 | `.tmp\bats\ws2.log`（`["tool","get_time","看时间"]`、`["tool_result","get_time","看时间"]`、应答 17:35） | PASS |

**定性结论：ASR 代码没有缺陷。** 上一批看到的 `ConnectError WinError 10054` 是**重启通道丢了 HF 环境变量**造成的：whisper-small 的快照在仓库内 `.hf-cache\hub\models--Systran--faster-whisper-small\snapshots\...`（实测存在），而默认用户缓存里没有；没有 `HF_HOME`/`HF_ENDPOINT`，faster-whisper 就去 huggingface.co 找快照，连接被重置 → 加载失败 → 转写为空。`start_all.bat` 里本来就设了这三个变量（19-45 批次加的），我用 `pwsh` 重启时漏了，属操作失误。

改动只有两处：① 运维约定——重启 Jarvis 必须带 `HF_ENDPOINT=https://hf-mirror.com` / `HF_HOME=<repo>\.hf-cache` / `HF_HUB_DISABLE_XET=1`（写入 progress 执行通道）；② `jarvis/main.py` 新增 `_warm_stt()` 后台预加载，使 `asr.warm` 启动即 `true`、加载失败在启动日志立刻暴露，不再等到真人说完话才发现。

登记遗留（本轮不改）：2B 模型把 11-10 答成「星期五」（`tool_result` 是 `星期二`）、转写/回答出现繁体；`config.yaml` 的 `device: cuda` 在这台机器上不可用（驱动版本不足，已自动回 CPU，建议改配置为 `cpu` 以免每次启动都试一遍 CUDA）。
