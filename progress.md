# progress — 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-10-21-50-17.md（含 2026-11-09-20-35 唤醒灯、2026-11-09-21-19 start_all ASCII/CRLF、2026-11-09-21-55 阈值 0.7+ack 内存直放、2026-11-10-17-31 HF 环境变量丢失+whisper 预热、2026-11-10-17-43 工具文案汉化+录音落盘+ASR 参数、2026-11-10-21-02 真人录音重训练全节等）。本文件保留长期规则 + Git 提交记录 + 最近三批。 -->

## 长期规则与约定

### 工作约定（2026-11-08-14-35，用户指示）
- **不允许使用子智能体（subagent / subagent_fork）**；需要时必须先询问用户并获批准。

### 浏览器共用插件准入规则（用户 2026-11-09 指示，长期有效）
1. **口碑与评分**：仓库 star / npm·Chrome 商店下载量与评分 / issue 活跃度 / 是否官方厂商维护（Google·Microsoft 官方优先）；无口碑 = 不装。
2. **恶意执行**：是否执行任意代码（stdio 命令、postinstall、native 消息宿主）、是否要求管理员、是否写 startup/服务、是否可被远端下发指令。
3. **数据外发**：是否向远程地址发送页面内容/URL/凭据/剪贴板（遥测、云 relay、统计）。本地 stdio + 仅回环 = 通过；云端中转 = 拒绝；官方遥测须告知用户并可关闭。
4. 三问逐条写入 `records/时间.md` 与本节，**通过才装**；装前取得用户明确授权（本会话审批关闭，需审批的动作会被自动拒绝）。
5. 优先「共用用户自己的浏览器」形态（扩展 / CDP 附着用户 Chrome），避免我再开一套 Playwright/Edge 实例。
6. 本批评估结论：Playwright MCP `--cdp-endpoint`（回环附着用户 Chrome）**通过（推荐）**；Chrome DevTools MCP **通过**（二者择一，勿同时装）；Browser MCP（云端 relay）**拒绝**。三问明细见 `records/2026-11-09-15-37-58.md`；配置需用户授权（建议 Chrome 加 `--remote-debugging-port=9222`，我用 `--cdp-endpoint` 附着）。

### 观测配额规则（用户 2026-11-09-15:5x：「禁止大量截图/读图，会导致隧道崩溃」）
1. 禁止批量截图/读图；一次会话内截图只用于「首次定位 + 真需要目视验收」，优先 ≤ 个位数。
2. 观察走**文本通路**：`computer_windows` 窗口列表（窗口标题即 UIA 文本）、`computer_accessibility` + `computer_find` + `computer_read`、命令输出重定向到 `.tmp/*.log` 后用 `read` 读、HTTP/WS 探针。
3. 目视验收时截图 + `save_to`；需 OCR 只对已存文件跑一次。轮询用文件日志，不「截图→看→再截图」。

### 执行通道（本会话沉淀，可复用）
- **首选 `pwsh` 工具通道**：直接跑 `git` / `netstat` / `Invoke-WebRequest` / `tasklist` / python 探针，无需前台、无需弹窗。`cmd /c start_all.bat` 在 stdout 被重定向时不会退出（子窗口继承管道），脚本类启动仍走双击 / `Win+R` 弹窗。
- 弹窗通道（次选）：`write` 生成纯 ASCII `.bat` → `Win+R` 填全路径 →「打开文件 - 安全警告」用 **`Alt+R`（运行(R) 助记键）** 放行（UIA `invoke` 与鼠标点击对该弹窗无效）→ 输出重定向 `.tmp\*.log` → `read`。window_id 每次动作前重新 `list`（id 会被成功动作消耗/过期）。
- 编码坑：中文路径在 `.bat` 里被 cmd 当 GBK → 用 `%USERPROFILE%`/`%~dp0`；PowerShell `>` 产生 UTF-16 不可读，CJK 日志需 `Get-Content | Out-File -Encoding utf8`；python 探针设 `PYTHONIOENCODING=utf-8`、`PYTHONPATH=%CD%`（否则 `No module named 'jarvis'`）；commit 主题用 ASCII。
- 运维：重启 `:7860` 用 `Get-NetTCPConnection -LocalPort 7860 -State Listen` 找 pid → `Stop-Process` → `Start-Process -WindowStyle Hidden` 拉起 `.venv\Scripts\python.exe -u -m jarvis.main`（精确，不伤 GPT-SoVITS）。**重启 Jarvis 必须带 `HF_ENDPOINT=https://hf-mirror.com` + `HF_HOME=<repo>\.hf-cache` + `HF_HUB_DISABLE_XET=1`**：whisper-small 的快照只存在于仓库内 `.hf-cache`（默认用户缓存没有），漏了这三个变量 faster-whisper 会去 huggingface.co 找快照并抛 `ConnectError WinError 10054`，转写直接为空（`records/2026-11-10-17-31-10.md`）。

## Git 提交记录（全部**已本地 commit，未 push**；AGENTS §4 禁 push）

- `35984ac` `fix(AI): 修录音被自己的 barge-in 打断（1.5s 宽限 + 5s 冷却）并新增 get_time 工具`
- `904dbc8` `fix(AI): 网页端实时状态改为匹配中文广播并加心跳/重连重拉历史`；`104045f` `docs(AI): 网页实时批次提交台账（904dbc8）`
- `a0ecd92` `fix(AI): add status display + ASR/LLM/TTS health lamps, restart services and verify realtime UI in 3 rounds`（16 files；commit 主题 ASCII，`cmd` 会把中文当 GBK）
- `1e16ca6` `docs(AI): rebuild tree.md, archive+compact progress.md, todo status, add untracked record 2026-11-08-20-44-17`（4 files）
- `cc6830a` `docs(AI): record 1e16ca6 hash, 18-21 service restart re-verification, Alt+R run channel fix`（2 files / 16 insertions）
- `9939d8d` `docs(AI): append cc6830a commit hash to progress ledger`（1 file）
- `324fe25` `fix(AI): start_all.bat sets MPLCONFIGDIR to kill matplotlib WinError5 and launches llama :8080 too`（3 files / 57 insertions）
- `10d2b55` `docs(AI): append 324fe25 hash and 19-45 matplotlib/launch fix section to progress ledger`（1 file / 10 insertions）
- `4840591` `feat(AI): add wake-word health lamp left of ASR via wake.state plus 4-lamp api health, verified 3 rounds`（11 files / 220+ / 76-）
- `c1f358e` `docs(AI): append 4840591 hash to progress ledger and add 20-35 batch conclusion to cumulative opinion`（2 files / 8 insertions）
- `387b320` `fix(AI): rewrite start_all.bat as pure ASCII CRLF with start-opened cmd windows for llama gptsovits jarvis and status panel, verified 3 rounds`（10 files / 158+ / 47-；本批起改用 `pwsh` 通道跑 git）
- `4ab19ea` `docs(AI): append 387b320 hash to ledger, mark 21-19 start_all todo done`（2 files / 3+ / 1-）
- `8aada16` `feat(AI): wake threshold 0.7, ack audio cached in memory with one warmed output stream, Chinese tool labels for tts and ui, verified 3 rounds`（15 files / 426+ / 95-；**已本地 commit，未 push**）
- `f7abb54` `test(AI): add round 4 barge-in regression for cached ack playback path, update ledgers`（4 files / 26+ / 4-；**已本地 commit，未 push**）
- `d7d8132` `fix(AI): restore HF cache env vars on jarvis restart and add startup whisper warm-up so asr loads from repo .hf-cache, verified 3 rounds`（10 files / 136+ / 5-；**已本地 commit，未 push**）
- `5292ccd` `feat(AI): localize tool result strings, dump captured audio for ASR replay, tune whisper with simplified prompt and vad, verified 3 rounds`（21 files / 331+ / 74-；**已本地 commit，未 push**）
- `4586671` `feat(AI): exit mic capture early when no speech, add real-person wake-word dataset and SNR noise post-training, verified 3 rounds with config unchanged`（14 files / 220+ / 4-：`config.yaml`、`jarvis/stt.py`、`jarvis/main.py`、`records/2026-11-10-21-02-16.md`、`tests/2026-11-10-21-02-16_cc/` 5 件、`tests/opinion.md`、`need_user.md`（Q8）、`progress.md`（已归档 `ai_buckup/progress.md_2026-11-10-21-50-17.md`）、`todo.md`（已归档 `ai_buckup/todo.md_2026-11-10-21-52-25.md`）、`tree.md`；新脚本与 `aili_xiya_v0.4/v0.5` 数据被 `.gitignore` 排除，未 commit；**已本地 commit，未 push**）
- 最后一条 hash 的「记录该 hash 的 commit」不再追加，避免无限循环。

## 2026-11-10-17-31 ASR「不能转写」真因（重启丢 HF 环境变量）+ whisper 启动预热

- 真因：重启 Jarvis 时没带 `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET` 三个变量 → faster-whisper 去 huggingface.co 找快照，抛 `ConnectError WinError 10054`，转写为空。修复 = 重启命令固定带三变量（已进「执行通道」节）+ `main.py` 启动后台线程 `_warm_stt()` 预加载模型（`[STT] whisper warmed in N ms`，health `asr.warm=true`）。
- 3 轮全 PASS（`tests/2026-11-10-17-31-10_cc/`）。顺带实测 `stt.device: cuda` 本机不可用（`CUDA driver insufficient`）自动回 CPU，`config.yaml` 已改 `cpu`。
- 新登记（未改）：`get_time` 返回「星期二」但模型回答写「星期五」；回答/转写出现繁体（`我愛你`、`現在是…`）。

## 2026-11-10-17-43 工具结果文案汉化补全 + 录音落盘 + ASR 参数优化

- 汉化边界：只汉化**用户听到的文案**（`tools/*.py` 返回值 44 处 + `router.py` 2 处，如 `已输入文本：`、`已用左键点击 (x, y)`、`已滚动：向下 3 格`、`工具「读取文件」执行失败：路径不在允许清单内：…`）；协议层（`TOOL_SCHEMAS`、WS `name`、`events.db` 的 `tool` 行、`TOOL_LABELS` key）保持英文。修 2 真缺陷：`get_system_info` 中文乱码（`text=True` 用系统代码页解码 PS 输出 → 新增 `_ps_utf8()` 强制 UTF-8，`get_clipboard` 同步）；`main.py` 重试判定原依赖 `Tool '…'`，中文化后静默失效，改判 `执行失败：`。
- ASR 参数优化（`beam_size 10 / best_of 5 / initial_prompt=<简体中文+项目词表> / vad_filter=True / condition_on_previous_text=False` + `_trim_leading_silence()`）+ **录音落盘** `_dump_audio()`（每次写 `.tmp\capture_<ts>.wav`，不 commit）——首次让 ASR 误识别可离线复现。注意：faster-whisper 1.2.1 **不支持** `suppress_non_speech_tokens`（传了会 TypeError）。
- A/B：合成语音（GSV 做已知文本对照）**3/3 全对**（旧参数繁体 `你能看得見屏幕嗎`/`調到20` → 新参数逐字带标点）；真人 1 句（rms 0.010）在 6 种参数组合含 2x 增益下均为 `你看得见吗?`（丢「能」「屏幕」）→ 瓶颈是 whisper small 中文短句鲁棒性，不是电平/参数。换引擎（sherpa-onnx paraformer-zh）写入 `need_user.md` Q7 等授权，未擅自安装。
- 3 轮全 PASS（②部分 PASS，`tests/2026-11-10-17-43-08_cc/`）。新登记：18:03 `peak 0.736/0.799` 误触发后录满 30 s、转写为空。

## 2026-11-10-21-02 真人录音分段重训练（v0.4/v0.5）+ 抗干扰后训练 + 「录满 30s」修复

- 需求（`records/2026-11-10-21-02-16.md`）：①「有一次录制慢了30s」；② 用户提供真人录音 `录音.m4a`（795,632 bytes），要求分割后重训练 onnx；③ 追加「将噪音和已有音频样本混合，进行抗干扰的后训练」。
- 数据勘察（`seg3.log`）：解码 36.12 s 16 kHz 单声道；faster-whisper 词级时间戳**只确认 4 次**「爱莉希雅」（1.3–2.5、2.8–4.6、30.6–31.7、33.1–34.3，后两次识别为繁体 `愛里西亞`），2.84–24.92 s 是 prompt 词幻觉（该段无可识别语音）；v0.3 全文件 mean 0.39 / peak 0.753（14.9 s 峰不是呼唤）——**噪声本身就能把分抬到 0.7**。真人正样本仅 4 条 → 2 训练 + 2 验收留出（逐 clip 不重叠）；有声段切真人负样本（8 训练 + 3 验收）、安静段切静音负样本（3 训练 + 7 验收）。高分未标注窗口 27.0–30.2、31.7–32.7 **未入库**，等 `need_user.md` Q8 确认。
- 新脚本（沿用 `_t2_*` 与既有四个目录）：`_t2_v04_real_clips.py`（切真人 clip，编号延续 10xx）、`_t2_v04_features.py`（真人 clip 走 `_t2_stream_features_v02` 流式滑窗，与 v0.3 特征合并成 v0.4：24024 正 / 57708 负行）、`_t2_v04_noisy_clips.py`（噪声池 24 文件按 **SNR -5/0/5/10 dB** 与真人+合成样本混合，seed 42，164 条 11xx clip + 8 条纯噪声负样本）、`_t2_v05_features.py`（真人行 ×5、带噪行 ×2 → v0.5）、`openWakeWord/train_config_v04.yaml`、`train_config_v05.yaml`（`steps 2500`、`max_negative_weight 1`，沿用 HB-021/027）。
- 验收矩阵（阈值 0.7，`v05verify.log`）：v0.3 = 合成 rec 0.97/fp 0.30、真人 1.00/0.70、带噪真人 0.75/带噪 fp 0.69；v0.4 = 0.97/0.30、真人 0.50/0.20、带噪 0.38/0.69；v0.5 = 合成 0.60/**0.00**、真人 0.00/0.00、带噪 0.00/0.00。**三者在写死判据（真人 rec≥0.9 且 fp≤0.1）下全部 FAIL**，故 `config.yaml` **未改**，Jarvis 继续用 `aili_xiya_v0.3.onnx` + `threshold 0.7`。方向结论：**抗干扰后训练有效**（带噪 fp 0.69→0.00、真人 fp 0.70→0.20），失败点是**真人正样本量**（真人正特征仅 24 行 / 120 行，且呼唤电平弱）。补录要求（≥20 次干净呼唤、安静+带噪各半、离麦近）写入 `need_user.md` Q8。
- 第 ① 点修复：`record_until_silence` 新增 `no_speech_seconds`（默认 2.0，`config.yaml` `stt.no_speech_seconds`，`main.py` 传入）。模拟 3 例（`nospeech.log`）：无人说话 2.10 s 退出 / 说话后安静 4.20 s（保留 3.0 s 收尾，2026-11-08 的 2.1 s 教训不回归）/ 持续说话 30.00 s。21:48 重启后线上实测 `[STT] No speech in 2.0s, stopping early (max rms=0.0018)` → `Recorded 2.1s`，18:03 那类「噪声误触发后录满 30 s」已消除。
- 3 轮验证（`tests/2026-11-10-21-02-16_cc/`，累积见 `tests/opinion.md`）：① 分段与标注（部分达标：4 次呼唤定位，数量远少于「多次」）；② v0.4 矩阵 FAIL（真人 rec 0.50）；③ v0.5 抗干扰矩阵 FAIL（recall 塌陷、带噪 fp 归零）。全程零截图、无子智能体。
- 新登记遗留：v0.4/v0.5 的 ONNX 与 npy/clip 数据留在 `openWakeWord/output/`（**未 commit**，等补录后作基线）；`tree.md` 需为 6 个新脚本/配置重建；`todo.md` 已归档 compact（>100 行）。
