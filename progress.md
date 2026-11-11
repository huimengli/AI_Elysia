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
- `9d724cd` `feat(AI): 唤醒模型切到 aili_xiya_v0.6（真人检出 5→10），部署管线复放 3 轮验收并登记 Q12 阈值选择`（10 files / 123+ / 6-：`config.yaml`（`wake_word.model` 改 `aili_xiya_v0.6.onnx`，`threshold` 保持 0.7）、`records/2026-11-11-19-45-46.md`、`tests/2026-11-11-19-45-46_cc/` 5 件、`tests/opinion.md`、`need_user.md`（Q10 done + Q12 wait）、`todo.md`、`tree.md`（193 项）；`aili_xiya_v0.6.onnx` 与数据被 `.gitignore` 排除，未 commit；**已本地 commit，未 push**）
- 最新一条：`4b0f64f` `docs(AI): 把 9d724cd 的 hash 追加到进度台账并补 2026-11-11-19-45 批次节`（1 file；**已本地 commit，未 push**）。最后一条 hash 的「记录该 hash 的 commit」不再追加，避免无限循环。

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

- `need_user.md`：**Q9**（真人负样本）部分满足——2026-11-11 20:19 新录音给出 3 件真人近音负样本 + 2 件带噪呼唤，仍缺「≥10 句无关中文短句」与更多干净呼唤；**Q10 / Q11 / Q12** 已答复（`status: done`）。新增 **Q13**（`status: wait`）：① 缺的音频规格（≥10 句无关中文短句、≥10 件真人近音词、更多带噪呼唤）；② 根目录清理的目标目录（`_*` 脚本/日志、`jarvis_screen.png`、`love_silvia.txt`、`AI_Benchmark.md`、`JARVIS_STATE.md`、`PROJECT_SUMMARY.txt` 归入何处，推荐 `.tmp/`）；③ ASR 第二引擎的磁盘授权（C 盘现剩 14.48 GB）。第 6 项清理与 ASR 模型下载在 Q13 答复前不推进（AGENTS §2）。
- **Q7** 真人 3 句语音验证 + 是否换 sherpa-onnx paraformer-zh `status: wait`（本批已开工引擎开关，模型下载待授权）。
- 未跑完的验证：`2026-11-09-19-45-46` 剩 2 轮；`2026-11-08-20-44-17` 的 20 轮明确测试未跑完、轮 4 barge-in 结论待追加累积 `tests/opinion.md`。
- 浏览器共用插件安装/配置等用户授权 Chrome `--remote-debugging-port=9222`。

## 2026-11-11-19-45 唤醒模型切到 aili_xiya_v0.6（用户「先将模型切换到0.6,我看看效果」）

- config.yaml wake_word.model → openWakeWord/output/aili_xiya_v0.6/aili_xiya_v0.6.onnx，threshold 保持 0.7、chunk_size 1280；带 3 个 HF 变量重启 Jarvis（旧 pid 7580），api/health 实测 wake.model=aili_xiya_v0.6.onnx / threshold 0.7 / listening=true、4 灯全 online、asr.warm=true。
- **部署管线复放（关键新数据）**：用与线上一致的判定方式（1280 chunk 逐块、检出后 reset、2 s 冷却）复放 36.12 s 真人录音 —— **v0.6 检出 10 次（0.48/5.12/9.04/11.92/14.72/18.16/26.24/28.56/31.60/34.16 s），v0.3 检出 5 次**；阈值 0.75 时 v0.6 降到 5 次、0.8 降到 1 次。clip 级 recall 1.00 与部署级 10/13 的差来自逐 chunk 分数在 0.7 附近波动 + 冷却合并（约 20.7 s、23.3 s 峰值压线 0.70–0.73 未触发）。
- **代价实证（新登记）**：现场环境音 10 s 实录（rms 1484，笔记本风扇 + 键盘）v0.6 触发 1 次 0.703、v0.3 0 次；线上日志实证启动阶段连触发两次（peak 0.737、0.716）后 [STT] No speech in 2.0s, stopping early (max rms=0.0024) → Transcription empty，即无人说话时它会自己应答。定标纯噪声 16 s 检出 0；合成对抗 20 条 v0.6 触发 4 次（v0.3 2 次，句子本身含唤醒词）。阈值 0.75 时环境音触发归零。
- 3 轮（tests/2026-11-11-19-45-46_cc/，累积 tests/opinion.md）：轮 1 PASS、轮 2 部分 PASS（期望 ≥12 未达）、轮 3 FAIL（0.7 下环境音会触发）。全程零截图、无子智能体。commit 9d724cd（10 files / 123+ / 6-；**已本地 commit，未 push**）。阈值选择与真人实测结果登记 need_user.md **Q12**（status: wait）：保持 0.7（现行，检出 10）/ 改 0.75（环境音归零、检出 5）/ 回退 v0.3。

## 2026-11-11-20-34-04 TTS 分段队列 + 新录音训练 v0.7/v0.8 + ASR 引擎开关（第 6 项清理待 Q13）

- **TTS 分段队列（第 1 项，完成）**：jarvis/tts.py 的 _split_sentences 按中文+拉丁标点切句（旧正则只按拉丁 .!?+空白，中文整句切不出段）；_produce_segments（queue.Queue(maxsize=4)，生产者线程在播放段 k 时合成段 k+1）+ speak_queued（按序播放、记录首声、打断即 flush 输出流）；speak_streamed 的 gptsovits 分支走队列，main.py 调用点不变。A/B 实测（6 段应答，逐段合成 2453/2570/2556/3747/2815/2908 ms，串行合计 17049 ms，音频 11.48 s）：**首声 14.08 s → 2.44 s（≈5.8 倍）、总时长 27.04 s → 19.56 s（−27%）**；打断 1.2 s 后 played 0.00 s、is_speaking=False。commit 44f0be（perf(AI)，10 files；**已本地 commit，未 push**）。3 轮见 	ests/2026-11-11-20-34-04_cc/record_1..3.md。
- **新录音训练（第 2 项，两代均未达标）**：7 件新 m4a → 5 件含唤醒词（编号 13xx）+ **首批真人近音负样本 3 件**（'爱丽安娜' 0.735 / '爱丽丝' 0.708 / '米希雅' 0.683，v0.6 峰值）。部署管线矩阵（阈值 0.7，检出后 reset + 2 s 冷却）：**v0.6 = 13 次呼唤 10、真人近音 fp 1–2、合成对抗 4、定标纯噪声 0、环境音 0**；**v0.7（近音负 x5，2500 步）= 10→5、fp 2 → FAIL**（负样本行重复压过正样本，模型学会「语音密集=拒绝」）；**v0.8（正 x5 / 近音负 x3，3000 步）= 12 检出、真人近音 fp 3/3、合成对抗 6>4 → FAIL**；0.75 阈值 v0.8 = 8 + fp 0 + 对抗 6（对抗判据仍破）。按 Q12 规则**保持 v0.6 + 0.7 不改**，config.yaml 未动。3 轮见 ecord_4..6.md；训练配置 openWakeWord/train_config_v07.yaml、	rain_config_v08.yaml（新增，已 commit）。
- **新发现（记 hard_bug.md HB-032，未解决）**：AudioFeatures 用 
p.random 噪声初始化特征缓冲，**同一音频同一模型 3 次独立实例分数漂移 ±0.02–0.07**（ailianna max 0.753/0.730/0.732，aisli 0.681/0.713/0.671）。边界样本必须 ≥3 次独立复测；训练自带 Final Model False Positives per Hour: 0.0（三次都是 0.0）只统计 400 条合成 val_fp，**反映不出真人近音**，验收一律以部署管线矩阵为准。
- **ASR 引擎开关（第 4 项，进行中）**：jarvis/stt.py 新增 stt.engine（whisper/sherpa）+ _get_sherpa()（OfflineRecognizer.from_paraformer）+ _sherpa_transcribe()，网页设置复用现有 pi_get_settings/pi_update_settings 的 stt 字典（用户可在网页选引擎）。sherpa-onnx 依赖：pypi 官方源 14 分钟无进度（已停），改清华镜像重试；模型（paraformer-zh int8）下载与 3 轮 A/B 待完成（Q13 磁盘授权）。
- **第 3 项 Q12 已答复并执行**（保持 v0.6+0.7）；**第 5 项 Q5/Q6 标 done**；**第 6 项根目录清理阻塞于 Q13，未移动任何文件**。
- 服务侧：本批开始时 :9880/:8080/:7860 全 DOWN（机器重启），cmd /c start_all.bat 后台任务 10 s 拉起；两次训练失败（positive_test 缺 wav = HB-028 已知；补齐后一次 DefaultCPUAllocator: not enough memory 内存峰值），第三次成功。全程零截图、无子智能体。
- 最新一条：4f3e964 	est(AI): 新录音训练 v0.7/v0.8 三轮验收未达标（保持 v0.6+0.7），记录打分非确定性 HB-032 并加 ASR 引擎开关（11 files / 232+ / 11-；**已本地 commit，未 push**）。上一条 44f0be 的 hash 记录在同批 TTS 提交里，见本批要点节。
- 最新一条：71a6a27 eat(AI): ASR 引擎可切换（whisper/sherpa-onnx Paraformer），网页设置新增引擎选择，3 轮验收（3 files / 27+ / 2-；jarvis/stt.py 的引擎开关在 4f3e964 已提交；**已本地 commit，未 push**）。上一条 hash 的记录 commit 不再追加。
- 最新一条：621308a docs(AI): 落盘新需求（我没听清入 ack 池 + sqlite 热词热句表），明天开工，本批停工（2 files / 31+；ecords/2026-11-11-21-36-30.md + 	odo.md 5 条待办；**已本地 commit，未 push**）。上一条 hash 的记录 commit 不再追加。
