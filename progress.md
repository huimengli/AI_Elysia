# progress — 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-10-23-00-30.md（含 2026-11-09-20-35 唤醒灯、21-19 start_all ASCII/CRLF、21-55 阈值 0.7+ack 内存直放、2026-11-10-17-31 HF 预热、17-43 工具文案汉化+录音落盘+ASR 参数、21-02 真人录音重训练全节、22-17 重标 13 次+v0.6、22-48 commit 标题改中文全节等）。本文件保留长期规则 + Git 提交记录（含旧→新 hash 对照）+ 最近三批要点。 -->

## 长期规则与约定

- **不允许使用子智能体**（subagent / subagent_fork）；需要时必须先询问用户并获批准（用户 2026-11-08-14-35）。
- **禁止大量截图/读图**（用户 2026-11-09-15:5x，会导致隧道崩溃）：观察走文本通路（`computer_windows` 标题、`computer_accessibility` + `computer_find` + `computer_read`、命令输出重定向 `.tmp/*.log` 后 `read`、HTTP/WS 探针）；截图只用于首次定位与目视验收，一次会话 ≤ 个位数；轮询用文件日志，不「截图→看→再截图」。
- **浏览器共用插件准入三问**（口碑评分 / 是否执行任意代码 / 是否外发数据）逐条写入 record 与本节，通过才装，装前取得用户授权；优先「共用用户自己的浏览器」（CDP 附着）。已评估：Playwright MCP `--cdp-endpoint` 通过（推荐）、Chrome DevTools MCP 通过（择一，勿同装）、Browser MCP（云 relay）拒绝。明细 `records/2026-11-09-15-37-58.md`。
- **执行通道**：首选 `pwsh` 通道跑 `git` / `Invoke-WebRequest` / python 探针（无需前台/弹窗）；`cmd /c start_all.bat` 在 stdout 重定向时不退出，脚本类启动走 `Win+R` +「安全警告」的 **`Alt+R`** 放行。编码坑：`.bat` 里中文被 cmd 当 GBK（用 `%USERPROFILE%`/`%~dp0`）；PowerShell `>` 产生 UTF-16（用 `Out-File -Encoding utf8`）；python 探针设 `PYTHONIOENCODING=utf-8`、`PYTHONPATH=%CD%`。**commit 主题自 2026-11-10-22-48 起一律中文**（`type(AI): 中文标题`，type/scope 保持英文）：`pwsh` UTF-8 正常，历史 ASCII 主题源于当时走 `cmd`（GBK 写乱）；含反引号的长中文用 `write` 工具，不要用 pwsh heredoc（会吞反引号）。
- **重启 Jarvis（`:7860`）**：`Get-NetTCPConnection -LocalPort 7860 -State Listen` 找 pid → `Stop-Process` → `Start-Process -WindowStyle Hidden .venv\Scripts\python.exe -u -m jarvis.main`，**必须带 `HF_ENDPOINT=https://hf-mirror.com` + `HF_HOME=<repo>\.hf-cache` + `HF_HUB_DISABLE_XET=1`**（漏了会 `ConnectError WinError 10054`、转写为空）。llama `:8080` / GPT-SoVITS `:9880` 掉线时用 `cmd /c start_all.bat` 后台任务恢复。
- **唤醒训练链**（可复用）：`_t2_stream_features_v02.py`（1 s 零填充 + 1280 滑窗、chunk-boundary last-24 帧，与 `Model.predict_clip` 一致，HB-027；`AudioFeatures(onnx, ncpu=1)`，prefix 53 / NFR 24）→ `_t2_train_cn.py --training_config … --train_model`（需 `output/<model>/` 里有 `positive_features_train/test.npy`、`negative_features_train.npy`、`val_fp.npy`，且 `positive_test` 目录含 wav）→ `_t2_verify_onnx.py`。教训：HB-021 平权重 `max_negative_weight: 1`；HB-023 正负样本同变换分布 → 内容是唯一可分线索；HB-028 过期 npy/wav 会被静默消费。
- **音频 I/O**：`soundfile` 在 `.venv` 不可用（`libsndfile.dll error 0x7e`）→ 用 stdlib `wave` 读写；m4a 解码用 PyAV `av.AudioResampler(format="s16", layout="mono", rate=16000)` + `frame.to_ndarray()`。`onnx_tf` 缺 → tflite 跳过，只出 ONNX。

## Git 提交记录（全部**已本地 commit，未 push**；AGENTS §4 禁 push）

- 早期（ASCII 主题，当时走 `cmd` 会 GBK 写乱，未改写）：`35984ac`（修 barge-in + get_time）、`904dbc8`/`104045f`（网页实时状态）、`a0ecd92`（4 状态灯）、`1e16ca6`/`cc6830a`/`9939d8d`（台账）、`324fe25`/`10d2b55`（MPLCONFIGDIR + llama 启动）、`4840591`/`c1f358e`（唤醒灯）、`387b320`/`4ab19ea`（start_all 纯 ASCII CRLF）。
- **2026-11-10-22-58 已把最近 12 条英文标题 reword 成中文**（`git rebase -i 8aada16~1` + 脚本改主题；旧历史保留在本地分支 `backup-before-reword`；工作树逐文件一致）。**旧 hash → 新 hash**：`8aada16`→`58c322e`（feat: 唤醒阈值定 0.7、应答音频缓存内存并复用单条输出流、TTS 与 UI 工具标签汉化，3 轮验证）、`510b26b`→`8fad6b7`、`f7abb54`→`f84e5ff`（test: 补第 4 轮 barge-in 回归）、`cbff3bd`→`35fb9f0`、`d7d8132`→`5e5112b`（fix: 重启补齐 HF 环境变量 + whisper 预热）、`54474ba`→`c470e9e`、`5292ccd`→`2c02937`（feat: 工具结果文案汉化、录音落盘、whisper prompt/vad 调参）、`8b78934`→`5e70996`、`4586671`→`91d88f0`（feat: 无人说话提前结束录音，真人数据集与 SNR 抗干扰后训练）、`7f5341b`→`f5984a4`、`d5c2f35`→`2998a5c`（docs: 真人录音重标 13 次，重训 v0.6 带噪正样本，四模型验收）、`c85069d`→`8d2a201`；内容未改仅换 hash：`023a987`→`432f5ab`（定「commit 标题用中文」+ Q11）、`811b576`→`244fd12`。
- 最新一条：`244fd12` `docs(AI): 把 023a987 的 hash 追加到进度台账`。最后一条 hash 的「记录该 hash 的 commit」不再追加，避免无限循环。

## 最近三批要点

### 2026-11-10-21-02-16 真人录音切分 + SNR 抗干扰后训练 + 「录满 30 s」修复（`91d88f0`）

- `record_until_silence` 新增 `no_speech_seconds`（默认 2.0，`config.yaml` `stt.no_speech_seconds`）：无人说话 2 s 即退出（线上实测 `[STT] No speech in 2.0s, stopping early` → `Recorded 2.1s`），修「静默录满 30 s」。
- 真人 clip（编号 10xx）+ SNR −5/0/5/10 dB 混合（11xx）训练出 `aili_xiya_v0.4`/`v0.5`；3 轮验收全 FAIL（当时真人负样本里有 8 段其实是呼唤，见下批）。`aili_xiya_v0.4/v0.5` 的 ONNX 与数据留在 `openWakeWord/output/`（gitignore，未 commit）作基线。

### 2026-11-10-22-17-39 真人录音重标（13 次全为正样本）→ `aili_xiya_v0.6`（`2998a5c`）

- 用户答复 Q8：「这段录音总计 **13 次**, 没有噪音, 平均 2-3 秒一次, 补录的活明天弄」→ 上一批把 8 段真呼唤当负样本训练 = 教模型拒绝唤醒词，是 recall 塌陷根因。
- v0.3 分数局部峰检出**恰好 13** 个呼唤（0.56–34.40 s，间隔 2.0–3.9 s）→ 13 条全部作正样本（10 训练 `posx_tr_1200-1209` + 3 留出 `pos_te_1200-1202`），真人特征行 24→**1195**；带噪呼唤作**正样本**（52 条 121x），负样本只用 v0.3 合成对抗 + 8 条定标纯噪声；与 v0.3 特征合并 25195 正 / 57696 负行 → `aili_xiya_v0.6.onnx`（训练自带 `Final Model False Positives per Hour: 0.0`）。
- **新发现**：「两峰之间的间隙」不能当负样本（`noise_tr_1200` 的 v0.3 窗口最高分 0.822 > 多数真呼唤）；程序化低分区（平滑分 <0.25、≥0.8 s、剔除呼唤窗）在本录音返回 0 段 → **本录音无真人负样本、无干净静音负样本**（显式 N/A，等补录 Q9）。
- 矩阵（阈值 0.7）：**v0.6 = 真人留出 rec 1.00 / 带噪真人 0.83 / 纯噪声 fp 0.00 / 合成 rec 0.92–0.97 / 对抗子集 fp 0.17**；v0.3（现役）= 0.67 / 0.50 / 0.25 / 0.97 / 0.30；v0.4 = 0.33；v0.5 = 0.00。v0.6 全部真人维度严格优于现役，但按写死判据（带噪 ≥0.9、合成 fp ≤0.1）仍 FAIL → `config.yaml` **未改**，Jarvis 仍用 `aili_xiya_v0.3.onnx` + 0.7；是否切换写入 `need_user.md` **Q10**（推荐切，阈值必须 0.7）。
- 3 轮：`tests/2026-11-10-22-17-39_cc/record_1..3.md` + `opinion.md`，累积追加 `tests/opinion.md`。全程零截图、无子智能体。

### 2026-11-10-22-48-24 commit 标题改中文（`432f5ab` + 本批）

- 用户：「最近的一些提交的 commit 标题怎么都是英文的? 需要改成中文」。原因说明：早期走 `cmd`（GBK 乱码）刻意写 ASCII；`pwsh` 通道 UTF-8 正常。长期约定已入执行通道节。
- 用户选定范围 = **最近 12 条**，已 reword（对照见上）；更早 25 条英文标题保持原样。改写后 `progress.md` >100 行 → 归档 `ai_buckup/progress.md_2026-11-10-23-00-30.md` 并压缩重写。

## 阻塞与等用户

- `need_user.md` **Q10**（是否切 `aili_xiya_v0.6.onnx`，阈值 0.7）与 **Q9**（明日补录：≥20 次干净呼唤 + ≥10 句无关中文短句作真人负样本 + ≥10 次带噪呼唤，三段分文件）均 `status: wait`；Q11（改写范围）已答复 → `status: done`（本批）。
- **Q7** 真人 3 句语音验证 + 是否换 sherpa-onnx paraformer-zh（约 30 MB 依赖 + 200–400 MB 模型，C 盘剩 17.7 GB）`status: wait`。
- 未跑完的验证：`2026-11-09-19-45-46` 剩 2 轮；`2026-11-08-20-44-17` 的 20 轮明确测试未跑完、轮 4 barge-in 结论待追加累积 `tests/opinion.md`。
- 浏览器共用插件安装/配置等用户授权 Chrome `--remote-debugging-port=9222`。
