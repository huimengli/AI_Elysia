# Need User（需用户确认的问题）

<!-- 已归档于 ai_buckup/need_user.md_2026-11-12-12-20-21.md（Q5-Q13 全部 status: done，含 Q13 根目录清理方案与音频清单的原始问答） -->

本文件当前**无未解决问题**（status: wait 条目为 0）。以下为已完成问题的结论摘要，完整问答见归档文件。

## Q5 / Q6 仓库私有化与 push（status: done，2026-11-11 20:34）
用户答复「Q5、Q6 关闭掉，我自己推」→ 仓库可见性、描述与 push 全部由用户在 GitHub 端自行推进，Agent 不跟进、不索取 PAT。本地提交持续保留，**未 push**（AGENTS §4 禁止任何远程写入）。

## Q7 ASR 引擎授权与真人验证（status: done，2026-11-11 20:34）
用户答复「asr 的引擎下载下来，也到设置中，允许用户选择」→ sherpa-onnx 2.0.1 + core 依赖已装（pip 卡死后改 wheel 直接解包），paraformer-zh small `model.int8.onnx` **81.8 MB** 已后台下载；`stt.engine` + 网页设置项已接。A/B 3 轮（`tests/2026-11-12-10-35-29_cc/record_3.md`、`tests/opinion.md`）：**sim ≥0.8 whisper 3/6 vs sherpa 2/6**，sherpa 快 10-20 倍但**无 VAD，静默处幻觉**（`嗯`/`北京`/`小一瓶`），写不出「爱莉希雅」正字 → **`stt.engine` 保持 whisper**，sherpa 作为可选项。待办：给 sherpa 加能量门后重跑 3 轮。

## Q8 真人录音 13 次确认（status: done，2026-11-10 22:17）
用户答复「这段录音总计 **13 次**，没有噪音，平均 2-3 秒一次」→ 推翻我此前的标注：`录音.m4a` 的有声段全是呼唤，不是噪声。此前把 8 段当真人负样本入库（`negx_tr_1000-1005`、`negx_te_1000-1002`）等于**教模型拒绝唤醒词**，即 v0.4 recall 0.50、v0.5 recall 0.00 塌陷的直接原因。v0.6 重标（13 次全正样本，负样本只用合成对抗 + 纯噪声窗口）后重训练、重验收。

## Q9 补录规格（status: done，部分满足）
规格：干净呼唤 ≥20 次、无关短句/近音 ≥10 句、带噪呼唤 ≥10 次、分文件提供。2026-11-11 到位 7 件（3 近音 + 2 带噪 + 3 整句）；2026-11-12 到位 8 件（4 近音 + 7 无关短句 + 长噪音）。当前缺口逐条列在 **`need_audio.md`**。

## Q10 切换 v0.6（status: done，2026-11-11 19:45）
用户答复「先将模型切换到 0.6，我看看效果」→ `config.yaml` 切 `aili_xiya_v0.6.onnx` + `threshold 0.7`，重启带 3 个 HF 变量，3 轮验证。

## Q11 commit 标题改中文（status: done，2026-11-10 22:58）
用户选定范围「最近 12 条」→ `git branch -f backup-before-reword HEAD` 保留原历史，`git rebase -i` 逐条 reword 成中文（`type(AI): 中文标题`），`git diff backup-before-reword HEAD --stat` 为空；旧→新 hash 对照在 `progress.md`。更早 25 条英文标题按用户范围保持原样。**长期约定：commit subject 一律中文**。全程本地，未 push。

## Q12 阈值选择与真人实测（status: done，2026-11-11 20:34）
用户答复「先用 v0.6 + 0.7，之后训练测试如果更好就换」→ 11-11 保持 `v0.6 + 0.7`；11-12 因 `v0.9 + 0.75` 在两个轴上同时更优（检出 12 vs 10、真人近音 fp 6 vs 6-7、合成对抗 4 持平）→ 按该规则切换 `aili_xiya_v0.9.onnx` + `threshold 0.75`，health 实测生效。严格判据「真人近音 fp ≤1」仍未达标（缺口逐条见 `need_audio.md`）。

## Q13 根目录清理方案与音频清单（status: done，2026-11-12 12:12）
用户答复（原话摘要）：
1. 「照办，`_xx.py` 既然是可复用的脚本，那就别放 `.tmp/` 中，放到 `training/` 中，并从 `.gitignore` 中移除；`jarvis_screen.png`、`love_silvia.txt` 不动，就留在根目录中」→ 根目录全部 `_*` 的 `.py` → **`training/`（进 Git、进 tree.md）**；其余 `_*`（`.log`/`.txt`/`.yaml`/`.gz`/`.jinja`/`.wav`）→ **`.tmp/`**（仍被忽略）；`AI_Benchmark.md`、`JARVIS_STATE.md`、`PROJECT_SUMMARY.txt` → **`records/`**。
2. 「缺少的音频你单独列个文件出来，格式："音频内容"，"文件路径"（如果没有就留空）」→ 新建 **`need_audio.md`**。
3. 「下载，作为后台任务，不要阻塞」→ 授权确认（模型已后台下载完成），**后续所有下载一律后台任务**。
实施见 `records/2026-11-12-12-12-28.md`。
