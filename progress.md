# Progress — 跨会话进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-12-12-25-50.md（101 行，含 2026-10-13 至 2026-11-12 全部逐批要点与 hash 台账；本文件为 compact 版） -->

## 当前状态（2026-11-12 12:26）

- **服务**：`:9880` GPT-SoVITS、`:8080` llama.cpp（Qwen3.5-2B-Q4_K_M）、`:7860` Jarvis 全部 LISTEN。Jarvis 启动带 3 个 HF 变量（`HF_ENDPOINT=https://hf-mirror.com`、`HF_HOME=<repo>\.hf-cache`、`HF_HUB_DISABLE_XET=1`）。
- **唤醒**：`config.yaml` = **`aili_xiya_v0.9.onnx` + `threshold: 0.75`**，health 实测生效；`chunk_size` 1280、检出后 reset、冷却 2 s。
- **ASR**：`stt.engine` = **whisper**（faster-whisper small / cpu / int8 / zh）；sherpa-onnx Paraformer-zh small（`model.int8.onnx` 81.8 MB）已就位、可在网页设置里切换，分发与回退已实测。
- **TTS**：GPT-SoVITS + 按标点切句的队列（首声 14.08→2.44 s，总时长 −27%）。
- **结构**：根目录清理完成（Q13 结案），可复用脚本在 **`training/`**（71 个，已入 Git），日志类在 `.tmp/`（49 个 `_*`，忽略）。`tree.md` 275 项。`need_audio.md` 是缺录清单（格式 `"音频内容", "文件路径"`，路径为空 = 需录）。
- **无未答复问题**：`need_user.md` Q5-Q13 全部 status: done（已归档）。待办见 `todo.md`。
- **文档（2026-11-12 17:0x）**：9 个自训练唤醒 ONNX（v0.1→v0.9，体积均 13,735 B）的横向对比台账落盘在 **`ai_buckup/onnx_opinion.md`**（表 1 版本谱系 / 表 2 部署管线 3 轮实测 / 表 3 阈值取舍 / 表 4 HB-032 边界复测 / 结论与缺口 / 复现命令）；`todo.md` 103 行 > 100 → 归档 `ai_buckup/todo.md_2026-11-12-16-58-46.md` 并压缩为 60 行；`tree.md` 重建为 **278** 项。本批**未重跑任何探针**，全部数据取自已落盘日志与结论。
- **新补录批（2026-11-12 17:22，→ `records/2026-11-12-17-22-40.md`）**：你补录 14 件（14 次干净呼唤 / 键盘噪音 4 次 / 轻音乐 3 + 歌声 3 / 爱你老师 / 雅诗兰黛 / 米雅 / 天猫精灵 / 我没听清 / 机械键盘噪音 / 环境音），**数据本身可用**（无过静音件，v0.9 上 14 次件检出 14/14、键盘件 4/4、6 件带噪全命中，真呼唤 13→25 次、带噪正样本 2→12 条）。按现行规则重训 **`aili_xiya_v1.0`**（正 ×5 / 负 ×1，26515 / 58128 行，steps 3000）**Recall 0.3009 → 未采用**，`config.yaml` 保持 `v0.9 + 0.75`，服务未重启。3 轮落 `tests/2026-11-12-17-22-40_cc/`；`need_audio.md` §7 填路径、§5 剩余缺口（竞品唤醒句 ≥4、无关短句 ≥3）。**`need_user.md` Q14（status: wait）= 真人近音件入库规则冲突裁决**，未裁决前不推进重训。

## 关键结论（跨批次，勿再重复踩）

1. **行重复比只移动灵敏度曲线，不产生近音判别力**：v0.7（近音负 ×5）检出 10→5；v0.8（正 ×5 / 负 ×3）近音 fp 3/3；v0.9（正 ×5 / 真人新负 ×2，15 件入库）检出 **14/14/14** 但真人近音 fp **9-11**。严格判据「真人近音 fp ≤1 且 13 次呼唤 ≥10」在 0.70/0.75/0.80 三个阈值下**均无法同时满足**；采用 `v0.9 + 0.75`（12 / 6 / 2 / 对抗 4 / 长噪音 1 / 环境 0），两轴同时优于 `v0.6 + 0.7`（10 / 6-7 / 4-5 / 4 / 1 / 0）。
2. **TTS 合成负样本对本项目无效（实测排除）**：GPT-SoVITS 参考音频就是爱莉希雅本人音色，同音色合成近音词在 v0.6 峰值 **0.796-0.839**，高于真人唤醒词整件 0.73-0.75；16 件里 7 件 ≥0.7 剔除、9 件低分件排除。**真人补录是唯一有效负样本来源**；禁 爱丽西亚/艾丽西亚/爱X西亚 类（与唤醒词几乎无区别 = 教模型拒绝唤醒词，v0.4/v0.5 recall 塌陷机制）。
3. **真人件入库条件是「不含唤醒词 + 文件名即真值」，不按峰值剔除**；峰值只作验收证据。
4. **HB-032 打分非确定性**：`AudioFeatures` 用 `np.random` 播种缓冲 → 同一音频同一模型跨实例分数漂移 ±0.02-0.07。边界判定必须 **≥3 个独立实例复测取多数**；`Final Model False Positives per Hour` 只统计合成 val_fp，不可采信。
5. **并发 4 个探针触发 `MemoryError`**（`_streaming_melspectrogram`，与训练 `DefaultCPUAllocator` 同源）；验收必须单探针串行。
6. **长噪音发现**：62.83 s 长噪音里 rms 18-47 的低响度段在 v0.6 峰值 0.700-0.758（真实低能量噪声可触发）；定标纯噪声（rms<15）三轮全 0。
7. **sherpa-onnx 2.0.1 实测签名**：`from_paraformer(paraformer=, tokens=, num_threads=)`（无 `paraformer_model`/`language_hints`）；`OfflineStream.accept_waveform(sample_rate, samples)`（无 `accept_audio`）。A/B 3 轮逐条一致：sim ≥0.8 **whisper 3/6 vs sherpa 2/6**，sherpa 快 10-20 倍但**无 VAD，静默处幻觉**（`嗯`/`北京`/`小一瓶`），写不出「爱莉希雅」正字 → 默认保持 whisper；待办给 sherpa 加能量门后重跑 3 轮。
8. **pip 在本机卡死**（13+ 分钟）→ 下载 wheel 直接 `Expand-Archive` 到 site-packages；curl 需 `--ssl-no-revoke`；hf-mirror 吞吐 ~40 KB/s，DNS 不稳。pwsh 双引号 heredoc 会吃掉 `\n`/`\t`（曾把 `training/` 写成 tab）→ 含 CJK 与反引号的文本用 write 工具，append 用 `Add-Content`。
9. **规矩**：commit subject 一律中文（type/scope 英文）；**禁止 push**；hash 追加台账；零截图；不用子智能体（未询问）；先落盘再开工；`training/` 内脚本的 `sys.path` 已含 `training` 目录。
10. **与真唤醒同等强度的真人负样本会压塌 recall（2026-11-12 17:22 批实测）**：`米雅` 峰值 **0.827**、`机械键盘噪音` 0.816-0.844（3 实例稳定），与真呼唤整段峰值（v0.9 上 0.819 / 0.860）同量级 → 入库后 `aili_xiya_v1.0` **Recall 0.3009**（v0.9 = 0.6048），部署管线真呼唤 @0.70 合计 10（14 次件 7、键盘件 0）、@0.75 合计 3（6 件带噪全漏）；fp 归零是靠灵敏度塌陷换来的。与 v0.4 / v0.5 同一机制。第 3 条「不按峰值剔除」与此冲突，已提 **need_user.md Q14** 裁决（推荐：峰值 ≥0.80 的真人近音件移出训练集、只作验收集）。

## Git 提交记录（最近，全部**已本地 commit，未 push**）

- `ac5cb0c` `chore(AI): 根目录清理——71 个可复用脚本移入 training/ 并入 Git、49 个 _* 日志类移入 .tmp、3 份总结移入 records，新增 need_audio.md，Q13 结案`
- `8f1aa7d` `docs(AI): Q13 结案落盘——need_audio.md 清单、need_user.md 归档与 tree.md 重建 275 项，hash 追加台账`（4 files / 430+）
- `2846dcc` `docs(AI): Q13 追加进度——真人补录 15 件负样本已入库、ASR 依赖与模型已就位并给出 A/B 对比表，清理目标目录仍等答复`
- `733bf52` `docs(AI): 重建 tree.md（201 项，新增 tests/2026-11-12-10-35-29_cc，config 切 v0.9+0.75）`
- `10398c8` `test(AI): 真人补录 15 件负样本训练 v0.9，3 轮矩阵后采用 v0.9+阈值0.75，实测排除 TTS 合成负样本并修正 sherpa API`（8 files / 131+ / 5-）
- `096f5b9` `docs(AI): ASR 引擎 A/B 三轮结论（whisper 保持默认，sherpa 快 10-20 倍但无 VAD 会幻觉）`（3 files / 65+）
- `4369989` `docs(AI): 追加第 7 项——明天用 GPT-SoVITS 爱莉希雅音色合成近音词与无关短句作负样本训练`
- `621308a` `docs(AI): 落盘新需求（我没听清入 ack 池 + sqlite 热词热句表），明天开工，本批停工`
- `71a6a27` `feat(AI): ASR 引擎可切换（whisper/sherpa-onnx Paraformer），网页设置新增引擎选择，3 轮验收`
- `4f3e964` `test(AI): 新录音训练 v0.7/v0.8 三轮验收未达标（保持 v0.6+0.7），记录打分非确定性 HB-032 并加 ASR 引擎开关`
- `a44f0be` `feat(AI): TTS 按标点切句 + 合成队列，首声 14.1 s→2.4 s`
- `bd46e28` `docs(AI): 落盘第 8 项要求（剔除爱丽西亚/艾丽西亚、允许 TTS 合成无关短句、真人补录清点），开工`
- 更早（commit 标题改写链、v0.3→v0.6 切换、阈值 0.7、barge-in、无人说话提前结束录音等）的逐批要点与旧→新 hash 对照见归档 `ai_buckup/progress.md_2026-11-12-12-25-50.md`；改写前历史保留在分支 `backup-before-reword`。

## 未完待办（详见 `todo.md` 与 `need_audio.md`）

1. **真人补录缺口**（`need_audio.md` 第 5 节，路径留空项）：干净呼唤补 ≥10 次、带噪呼唤补 ≥8 条、真人近音补 ≥3 件、无关短句补 ≥3 句、竞品唤醒词真人句 ≥5 条、安静房间 10 s 干净环境音。这是「近音 fp ≤1」无法达标的直接原因。
2. **`我没听清，请再说一遍` 入 ack 池 + sqlite `hot_phrases` 表**（records/2026-11-11-21-36-30.md，已落盘未开工）。
3. **给 sherpa 加能量门（VAD/静音跳过）**，门生效后重跑 A/B 3 轮，再决定 `stt.engine` 默认。
4. **20 轮明确测试**（records/2026-11-08-20-44-17，1 轮已跑）、2026-11-09-19-45-46 的 3 轮验证补齐、barge-in 第 4 轮结论补写 `tests/opinion.md`。
5. 浏览器共享插件阻塞于 Chrome `--remote-debugging-port=9222` + Playwright MCP 授权。
6. 25 条更早的英文 commit 标题按你的选择保持原样，不动。
- 最新一条：`45b0ce4` `fix(AI): 修复 pwsh 双引号转义吃字符造成的文档损伤（training/api_/asr_ab/vad_filter/threshold/tests 等），并记录落盘规矩`（7 files / 87+ / 132-；**已本地 commit，未 push**）。
- 最新两条：`45b0ce4` `fix(AI): 修复 pwsh 双引号转义吃字符造成的文档损伤…`（7 files / 87+ / 132-）与 `f67e121` `docs(AI): tree.md 重生成（275 项，_chat_template.jinja 已随清理出树）`（1 file / 312+）。均**已本地 commit，未 push**。
- 最新三条：`c19988c` `docs(AI): 把 45b0ce4 / f67e121 的 hash 追加到进度台账`（1 file）与 `f68a766` `docs(AI): 9 个唤醒 ONNX 全版本对比落盘 ai_buckup/onnx_opinion.md（谱系+3 轮部署矩阵+阈值取舍+HB-032 复测），todo.md 103 行归档压缩、tree.md 278 项`（6 files / 314+ / 96-）。均**已本地 commit，未 push**。
- 最新四条：`e4599e9` `docs(AI): 把 c19988c / f68a766 的 hash 追加到进度台账`（1 file）与 `ed7e504` `docs(AI): tree.md 头部修正 todo 压缩版行数（81 行 / 非空 60 行）`（1 file / 1+ / 1-）。均**已本地 commit，未 push**；`e4599e9` / `ed7e504` 这两条 hash 追加 commit 的自身 hash 按惯例不再单独入账。
- 最新五条：`77750e1` `docs(AI): 把 e4599e9 / ed7e504 的 hash 追加到进度台账`（1 file）与 `95722b9` `docs(AI): 补入上批 progress.md 归档件（tree.md 已列，此前未跟踪）`（1 file / 102+）。均**已本地 commit，未 push**。
- 最新六条：`54c797c` `docs(AI): 把 77750e1 / 95722b9 的 hash 追加到进度台账`（1 file）与 `498ee45` `docs(AI): tree.md 重生成（278 项，progress.md 归档件已跟踪，计数不变）`（1 file / 4+ / 4-；本条由 `aa3d23c` 本地 `--amend` 改写主题而来，未 push）。本批 `tree.md` 278 项、`todo.md` 81 行、`progress.md` 56 行。
- 新补录批：**`6e0c0ac`** `test(AI): 新补录 14 件真人音频 3 轮验收——数据可用（14 次件检出 14/14）、按现行规则重训 v1.0 recall 0.3009 塌陷未采用，规则冲突提 Q14，脚本入 training/`（14 files / 766+ / 7-；`tree.md` 286 项）。**已本地 commit，未 push**。
- 多音色批（2026-11-12 18:49 需求 + 19:23 流萤 + 20:03 白厄 + 20:47 环境音期望更正）：**7 音色 × 20 文本 = 140 件**全部生成（`elya`/`firefly`/`bai_e` + Kokoro 4 个中文音色；真人音色克隆定案不可用，爱莉希雅权重 + 真人参考音频产出 60 s 失控）。白厄的 v2ProPlus 说法由权重内容证实（首 2 字节 `b"06"` = `process_ckpt.model_version2byte`），唯一障碍是本机缺 v2ProPlus 所需 `pretrained_models/sv/pretrained_eres2netv2w24s4ep4.ckpt`，hf-mirror 补 107.5 MB 后通。打分 @0.70：**正样本 21/21 入库、负样本仅 13/119 合格**（Kokoro 4 音色 0/17、白厄 6/17、流萤 2/17、同音色 5/17）。15xx clip 34 件并入 **v0.9 基线**（正 ×5 / 合格负 ×1）→ **v1.1 Recall 0.6179 / FP/hour 0.0**，3 轮矩阵：**@0.75 14 次件 12 < 14 直接 BAD、合成对抗 5 vs 4、近音 fp 6 vs 5 → 不采用 v1.1，保持 v0.9 + 阈值 0.75，`config.yaml` 未改**（v1.1 仅留盘）。**关键结论第 11 条：多音色是召回轴不是判别轴 —— 近音词在任意音色下峰值都 >=0.70（与真唤醒 0.82 同量级），换音色不能产生近音判别力；环境音期望必须为 0（该件无呼唤，用户更正，判据第 5 条改为「定标纯噪声与环境音检出 0」）。** Q14 仍 `status: wait` 未推进。
