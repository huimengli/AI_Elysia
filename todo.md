# Todo

<!-- 已归档于 ai_buckup/todo.md_2026-11-10-21-52-25.md（含 2026-10-12 运行环境搭建全链、2026-10-13 GPT-SoVITS 接入、2026-10-13-21-38 自训唤醒词 v0.1→v0.3c 全链、2026-10-17 Web UI 记录/应答词/start_all、2026-11-08 各修复批次、2026-11-09 状态灯/插件评估/阈值 0.7、2026-11-10-17-31 HF 预热、2026-11-10-17-43 汉化+ASR 参数 等已完成条目）。本文件保留未完成项 + 最近三批。 -->

## 未完成（等用户 / 需授权 / 延后）

- [ ] 2026-10-13-11-45 三问题排查收尾（→ records/2026-10-13-11-45.md；剩余：用户对新进程实测唤醒）
- [ ] 2026-10-13-21-38-01 T4 仓库私有化/描述改「自用」（AGENTS 禁远程写入，需用户手动；need_user.md Q5，用户确认延后）
- [ ] 2026-10-13-21-38-01 T6 网页 UI 爱莉希雅化（当时仅记录，后续已由 2026-11-08-14-12-32 完成）
- [ ] 2026-10-14-22-23-49 TTS 迁移 SoulX-Podcast（用户当时要求，**本轮不做**，仅记录）
- [ ] 2026-10-17-19-11-07 README 中文化 + 来源声明 + 仓库更名 AI_Elysia + LICENSE + push（→ records/2026-10-17-19-11-07.md；用户当时允许 push，AGENTS §4 禁 push，需用户明确操作）
- [ ] 2026-10-17-19-52-00 唤醒词 v0.3 onnx 入库（用户批准推送；AGENTS 禁 push → 需用户执行）
- [ ] 2026-11-08-12-08-49 LLM 基准台账 `AI_Benchmark.md` 继续补测更多模型（T14 decode 仅 IQ3 2B 已测）
- [ ] 2026-11-08-20-44-17 剩余：幻觉治理与「说完刷已停止」的 20 轮明确测试未跑完；轮 4 barge-in 结论待追加到累积 `tests/opinion.md`
- [ ] 2026-11-09-19-45-46 剩余 3 轮验证未跑完（1 轮已做）
- [ ] 2026-11-09-15-37-58 浏览器共用插件**安装/配置**（Playwright MCP `--cdp-endpoint` 已评估通过；需用户授权 Chrome `--remote-debugging-port=9222` 后执行）
- [ ] 2026-11-10-17-43-08 真人 3 句语音验证 + 是否换 sherpa-onnx paraformer-zh —— 等 `need_user.md` Q7 回复（汉化 44 处 / 乱码 / 重试判定 / 录音落盘 / 参数优化已 commit，3 轮已验）

## 2026-11-10-21-02-16 真人录音分段重训练 + 抗干扰后训练 + 「录满 30 s」修复 (→ records/2026-11-10-21-02-16.md)

- [x] 解码 36.12 s + ASR 词级时间戳定位呼唤（确认 4 次：1.3–2.5 / 2.8–4.6 / 30.6–31.7 / 33.1–34.3）+ 逐 0.5 s 响度剖面
- [x] 真人 clip 切分入库（2 训练正 / 2 验收留出 / 真人负 8+3 / 静音负 3+7，编号延续 10xx）→ `aili_xiya_v0.4` 流式特征（24024 正 / 57708 负行）→ 训练 `aili_xiya_v0.4.onnx`
- [x] **抗干扰后训练**（用户追加）：噪声池按 SNR -5/0/5/10 dB 混合 164 条带噪 clip + 8 条纯噪声负样本，真人行 ×5 / 带噪 ×2 → `aili_xiya_v0.5.onnx`
- [x] 验收矩阵（合成 + 真人留出 + 带噪留出，阈值 0.4–0.8，`v05verify.log`）：v0.3 真人 rec 1.00/fp 0.70；v0.4 0.50/0.20；v0.5 0.00/0.00（带噪 fp 归零、recall 塌陷）→ **三者在写死判据下全 FAIL，`config.yaml` 未改，Jarvis 仍用 v0.3 + 0.7**
- [x] 修「无人说话录满 30 s」：`record_until_silence` 新增 `no_speech_seconds`（默认 2.0，`config.yaml` `stt.no_speech_seconds`）；模拟 3 例 2.10/4.20/30.00 s 达标，21:48 线上实测 2.1 s 提前退出
- [x] 3 轮验证落盘（`tests/2026-11-10-21-02-16_cc/record_1..3.md` + `opinion.md`，累积追加 `tests/opinion.md`）
- [ ] 等用户在 `need_user.md` Q8 回复：① 录音里喊了几次「爱莉希雅」、分别在几秒；② 高分未标注窗口（27.0–30.2、31.7–32.7）是呼唤还是噪声（未入库）；③ **补录 ≥20 次干净呼唤**（安静 + 带噪各半、离麦近、系统录音音量调高）——真人正样本量是抗干扰链的硬瓶颈，补录后重跑同一套特征+训练+矩阵
- [ ] 补录后的后续：v0.4/v0.5 数据与 ONNX 留在 `openWakeWord/output/`（未 commit）作基线；新脚本 6 个需进 `tree.md` 重建

## 2026-11-10-22-17-39 重标真人录音（13 次全为正样本）→ `aili_xiya_v0.6` 重训练 + 重验收 (→ records/2026-11-10-22-17-39.md)

- 用户答复（`need_user.md` Q8，status done）：录音总计 **13 次**呼唤、**没有噪音**、平均 2–3 秒一次；补录明天做（规格见 Q9）。
- 关键修正：上一批把 8 段真呼唤（`negx_tr_1000-1005` / `negx_te_1000-1002` 及其 SNR 带噪版 `negx_*_11xx`）当**负样本**训练 = 教模型拒绝唤醒词，这是 v0.4 真人 recall 0.50 / v0.5 塌陷的直接原因
- [x] 重标切分：13 次呼唤窗口全部作正样本（`posx_tr_1200-1209` 训练 / `pos_te_1200-1202` 留出，逐 clip 断言不重叠）；本录音**无真人负样本、无干净静音负样本**（程序化低分区返回 0 段，显式 N/A 等补录）
- [x] 抗干扰后训练（保留 21:1x 需求，方向纠正）：13 条真呼唤按 SNR -5/0/5/10 dB 与噪声池混合，作**正样本**（52 条 121x）+ 8 条定标纯噪声负样本
- [x] 流式滑窗特征（真人行 ×5 / 带噪 ×2，与 v0.3 合成特征合并 = 25195 正 / 57696 负行）→ `aili_xiya_v0.6.onnx` 训练（`steps 2500`、`max_negative_weight 1`，训练自带 FP 0.0/hour）
- [x] 阈值 0.4–0.8 矩阵（合成 + 真人 13 + 带噪 12 + 纯噪声 4）：**v0.6 真人留出 rec 1.00 / 带噪 0.83 / 纯噪声 fp 0.00 / 合成 rec 0.92–0.97 / 对抗 fp 0.17**，全部真人维度严格优于现役 v0.3（0.67/0.50/0.25/0.97/0.30）；按写死判据（带噪≥0.9、合成 fp≤0.1）仍 FAIL → `config.yaml` **未改**
- [x] 3 轮验证 `tests/2026-11-10-22-17-39_cc/record_1..3.md` + `opinion.md`，累积追加 `tests/opinion.md`
- [ ] 等 `need_user.md` Q10 用户决定：是否把 `wake_word.model` 切到 `aili_xiya_v0.6.onnx`（阈值必须 0.7）；授权后重启 Jarvis（带 3 个 HF 变量）+ 真人唤醒复验 3 轮
- [ ] 等 `need_user.md` Q9 明日补录（≥20 次干净呼唤 + ≥10 句无关中文短句作真人负样本 + ≥10 次带噪呼唤）→ 重跑同一套流程，目标带噪 recall ≥0.9 并补齐真人 fp

## 2026-11-10-22-48-24 commit 标题改中文（→ `records/2026-11-10-22-48-24.md`）

- [x] 长期约定写入 `progress.md`：以后 commit subject 一律中文（`type(AI): 中文标题`；type/scope 保持英文，与 AGENTS §4 的 Conventional Commits 兼容，AGENTS.md 本身只读不改）
- [x] 用户选定范围（`need_user.md` Q11，status done）：**最近 12 条**（含 HF 预热、barge-in、阈值 0.7 等）
- [x] reword 执行：`git branch -f backup-before-reword HEAD` → `git rebase -i 8aada16~1` + `.tmp\reword\se.ps1` / `ed.ps1` / `msgmap.json`；12 条英文主题全改中文，14 commit 重放，`git diff backup-before-reword HEAD --stat` 为空（工作树逐文件一致）；旧→新 hash 对照写入 `progress.md`；`progress.md` 101 行 → 归档 `ai_buckup/progress.md_2026-11-10-23-00-30.md` 并压缩到 46 行；全程本地、**未 push**
- [x] 补 commit 本次文档（`records/2026-11-10-22-48-24.md` 结果节 + `todo.md` + `need_user.md` Q11 done + `progress.md` + `tree.md` 187 项），中文主题

## 2026-11-11-19-45-46 唤醒模型切换到 `aili_xiya_v0.6.onnx`（→ `records/2026-11-11-19-45-46.md`）

- 用户答复 `need_user.md` Q10 = 选项 1：「先将模型切换到0.6,我看看效果」→ Q10 追加 A + `status: done`
- [x] `config.yaml` `wake_word.model` → `openWakeWord/output/aili_xiya_v0.6/aili_xiya_v0.6.onnx`，`threshold` 保持 **0.7**，`chunk_size` 1280
- [x] 重启 Jarvis（带 3 个 HF 变量）→ `api/health` 的 `wake.model` = `aili_xiya_v0.6.onnx`、4 灯 online、`asr.warm=true`（实测 `listening=true`，`whisper warmed in 3384 ms`）
- [x] 3 轮验证 `tests/2026-11-11-19-45-46_cc/record_1..3.md` + `opinion.md`（累积追加 `tests/opinion.md`）：轮 1 PASS；轮 2 部署管线复放 36.12 s 录音 → **v0.6 检出 10 次 vs v0.3 5 次**（期望 ≥12 未达）；轮 3 定标纯噪声 0（达标）、合成对抗 4 次、**现场环境音 10 s 实录触发 1 次（0.703）→ 0.7 阈值 FAIL**，阈值 0.75 时环境音归零（检出降为 5）
- [ ] 等 `need_user.md` **Q12** 用户回复：真人实测 3 次唤醒结果 + 阈值选择（保持 0.7 / 改 0.75 / 回退 v0.3）；我按答复改 `config.yaml` 并重启（带 3 个 HF 变量）
- [x] commit（中文主题）+ hash 追加台账 + `tree.md` 重建（193 项），**禁止 push**

## 2026-11-11-20-34-04 TTS 分段队列 / 新录音继续训练 / ASR 引擎可选 / 关闭 Q5-Q6 / 根目录清理（→ records/2026-11-11-20-34-04.md）

- [x] Q12 已答复：**保持 aili_xiya_v0.6 + threshold 0.7**（现行不改），「之后训练测试如果更好就换」
- [x] Q5 / Q6 关闭（用户自己推进）→ need_user.md 标 status: done 并归档已解决项
- [x] 新录音 7 件（3 条真人近音负样本 + 2 条带噪呼唤 + 3 条含唤醒词整句）切样本 → 与 v0.6 数据合并训练 aili_xiya_v0.7 / v0.8 → 部署管线矩阵对比（真人检出、带噪、近音负样本、环境音）：**两代均未达标，按 Q12 保持 v0.6 + 0.7**（v0.7 13 次呼唤 10→5；v0.8 12 检出但真人近音 fp 3/3、合成对抗 6>4）。3 轮见 tests/2026-11-11-20-34-04_cc/record_4..6.md；打分非确定性记 hard_bug.md HB-032
- [x] TTS 分段队列：应答文本按标点切句，逐句 POST GPT-SoVITS :9880/tts，队列按序播放 + 合成与播放重叠，降低首声延迟；barge-in 时 flush 输出流。改 jarvis/tts.py，3 轮验证 PASS：**首声 14.08 s → 2.44 s（≈5.8×）、总时长 27.04 s → 19.56 s（−27%）、打断后 played 0.00 s**
- [ ] ASR 引擎可选：下载第二引擎（候选 sherpa-onnx + paraformer-zh，需 Q13 授权磁盘 200-400 MB）→ config.yaml stt.engine + 网页设置项允许选择，3 轮 A/B 对比转写质量
- [ ] 根目录清理：约 100 个 _* 脚本/日志 + jarvis_screen.png / love_silvia.txt / AI_Benchmark.md / JARVIS_STATE.md / PROJECT_SUMMARY.txt 移入对应文件夹（**移动不删除**），目标目录等 Q13 确认（推荐 .tmp/），tree.md 重建
- [x] 需要更多音频的规格写入 need_user.md Q13（缺「≥10 句无关中文短句」+ 更多真人近音/干净呼唤）；Q13 同时请示根目录清理目标目录与 ASR 磁盘授权，**status: wait**
- [ ] commit（中文主题）+ hash 追加台账，**禁止 push**

## 2026-11-11-21-36-30 「我没听清，请再说一遍」入 ack 池 + sqlite 热词(热句)小表（→ records/2026-11-11-21-36-30.md）**本批只落盘，明天开工**

- [ ] 「我没听清，请再说一遍」预合成 wav 入内存 ack 池（config.yaml 	ts.ack_phrases + jarvis/tts.py），**只在识别失败/空转录时播放**，不改 barge-in 语义
- [ ] memory.db 新增小表 hot_phrases(text, kind, count, first_seen, last_seen)，kind = user / hot / near_miss；写入点为 	ranscribe_audio 成功与近音误识，上限 200 行、按 count 淘汰
- [ ] 热词表接 ASR 偏置：whisper 用 stt.initial_prompt 拼 top-N，sherpa-onnx 用原生 hotwords；与 ASR A/B（2026-11-11-20-34 第 4 项）一起 3 轮验收
- [ ] 续传 paraformer-zh model.int8.onnx（81.8 MB，hf-mirror 多次停滞于 9.6 MB，需换源）→ 跑 .tmp/probe_asr_ab.py 3 轮 A/B（已知文本 6 件 + 12 条真实 capture wav）
- [ ] commit（中文主题）+ hash 追加台账，**禁止 push**
- [ ] 明天用 GPT-SoVITS 爱莉希雅音色合成负样本：近音词（爱丽安娜/爱丽丝/米希雅/米雅希/爱丽雅/希雅/爱丽西亚/艾丽西亚）+ 10 句无关中文短句，编号延续 `negx_tr_1302…`/`negx_te_1301…`，逐件 v0.6 打分后与 v0.6/v0.7 特征合并训练（行重复先 ×2，依 HB-032 边界复测），3 轮判据：真人 13 次 ≥10、真人近音 fp ≤1、合成对抗 ≤4、纯噪声 0、环境音 ≤1（→ records/2026-11-11-20-34-04.md 第 7 项）
- [ ] 2026-11-12-10-35 第 8 项开工：清点用户补录的无关中文短句(同一 attachments 位置) + GPT-SoVITS 合成近音词(爱丽安娜/爱丽丝/米希雅/米雅希/爱丽雅/希雅，**剔除爱丽西亚/艾丽西亚**)与 10 句无关短句作负样本，逐件 v0.6 打分过滤(峰值>=0.7 不入库)，与 v0.6 特征合并训练(正 x5 / 新负 x2) → 部署管线 3 轮判据(13 次>=10、真人近音 fp<=1、对抗<=4、纯噪声 0、环境音<=1，边界>=3 次复测)，达标才换 config（→ records/2026-11-11-20-34-04.md 第 8 项）

## 2026-11-12-10-35 第 8 项进度

- [x] 清点真人补录（C:\Users\楼听\Documents\录音 21 件，8 件新录）→ 15 件负样本入库（11 speech + 4 噪音窗，13xx 编号）
- [x] TTS 合成 16 件近音词/无关短句 → 7 件峰值 >=0.7 剔除、9 件低分件排除，**结论：TTS 合成负样本对本项目无效**（同音色 = 唤醒词音色）
- [x] v0.9 训练（正 x5 / 新负 x2，steps 3000）+ 3 轮部署矩阵 + 阈值 0.75/0.80 扫描 → **采用 v0.9 + 0.75**（12 检出 / fp 6 / 对抗 4 / 环境 0，两轴同时优于现役）
- [ ] 严格判据「真人近音 fp <=1」未达标（v0.9 fp 6-11）：需要 >=10 件真人近音负样本与 >=10 句真人无关短句，仍阻塞于 Q13（status: wait）
- [ ] ASR 引擎 A/B 3 轮（whisper vs sherpa，已知文本 6 件 + 12 条真实 capture wav，.tmp/probe_asr_ab.py，rounds 记录进 	ests/2026-11-12-10-35-29_cc/）→ 达标才把 stt.engine 设为默认
- [ ] commit（中文主题）+ hash 追加台账，**禁止 push**
- [ ] ASR：给 sherpa 路径加能量门（VAD/静音跳过，避免 嗯/北京/小一瓶 类幻觉），门生效后重跑 A/B 3 轮再决定 stt.engine 默认（当前保持 whisper；3 轮实测 sim whisper 3/6 vs sherpa 2/6，sherpa 快 10-20 倍）

## 新需求 2026-11-12-12-12-28（Q13 答复 + 根目录清理）(→ records/2026-11-12-12-12-28.md)

- [ ] Q13 标 status: done 并归档 need_user.md 到 ai_buckup/（AGENTS §3）
- [ ] 新建 need_audio.md：逐条 ""音频内容"", ""文件路径""（无音频则路径留空，需用户录）
- [ ] 根目录全部 _*.py 移入 training/，并从 .gitignore 移除该规则（进 Git、进 tree.md）
- [ ] 根目录其余 _* 文件（.log/.txt/.yaml/.gz/.jinja/.wav）移入 .tmp/（仍被忽略）
- [ ] jarvis_screen.png、love_silvia.txt **留在根目录**（用户明确不动）
- [ ] AI_Benchmark.md、JARVIS_STATE.md、PROJECT_SUMMARY.txt 移入 records/（git mv，保留历史）
- [ ] 修 sys.path 与训练/验证调用路径（脚本从 training/ 导入），复跑一次训练链冒烟
- [ ] 重建 tree.md（training/*.py 入树），commit（中文主题）+ hash 追加台账，**禁止 push**
- [ ] 下载类任务一律后台任务，不阻塞（Q13 第 3 问）
