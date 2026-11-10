# Need User（需用户确认的问题）

<!-- 已归档于 ai_buckup/need_user.md_2026-10-13-21-12-19.md（Q2/Q3 历史条目 + Q4 llama 重启请求，全部 status: done） -->

## Q5 2026-10-13-22-30 GitHub 仓库私有化 / 描述改"自用"（status: wait）

**问题**: 用户要求把 `github.com/huimengli/JarvisAi` 改为私有仓库，若不可行则把仓库描述改为"自用"。AGENTS.md 禁止 Agent 执行 `git push` 或任何远程写入（含 GitHub API/网页操作），此操作只能由用户在 GitHub 端手动完成。

**给用户的步骤**:
1. 打开 https://github.com/huimengli/JarvisAi → 右上角 **Settings**。
2. 左侧 **General**：
   - "Change repository visibility" → **Make private**（需要账号有私有仓库权限；免费版账号有数量限制，超限则只能改描述）。
   - "Description" 输入 `自用`。
3. 保存（Save）。
4. 注意：本 Agent 从未执行过 push，本地提交不会自动同步到 GitHub；若仓库此前是公开空仓库/已有公开内容，改私有后历史内容仍保留在仓库中。

**A**: （待用户回复）

## Q6 2026-10-17-19-5x push 到 AI_Elysia：本机 git 无 GitHub 凭据（status: wait）

**问题**: 用户已批准本次 `git push`，本地两个提交（`999cc32`、`251f7b0`）就绪、remote origin 已指向 `https://github.com/huimengli/AI_Elysia`，但执行 `git push -u origin main` 失败：`schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030E)` —— 本机 git 没有任何 GitHub 凭据（无 credential manager 条目、无 PAT），Agent 无法代为推送。

**给用户的方案（三选一）**:
1. **用户自己在终端 push（推荐）**: 在 `C:\Users\楼听\Desktop\git\JarvisAi` 下执行 `git push -u origin main`（凭据弹窗正常输入即可）。
2. **提供 PAT**: 给我一个有 `repo` 权限的 GitHub Personal Access Token，爱莉希雅写入本机 credential store 后自行完成 push。
3. **继续延后**：本地提交已保留，remote 已指向正确仓库，之后随时可推。

**A**: （待用户回复）

## Q7 2026-11-10-18-2x 真人语音 3 句验证 + 是否更换 ASR 引擎（status: wait）

**问题**: 新 ASR 参数（`beam_size 10` + 简体中文 `initial_prompt` + `vad_filter` + 去头部静音）在合成语音 A/B 中 3/3 全对（旧参数输出繁体/丢字：`你能看得見屏幕嗎` → 新参数 `你能看得见屏幕吗?`）。真人第一轮只得到 `你看得见吗?`（你说的是「你能看得见屏幕吗？」，丢了「能」「屏幕」），该次录音 rms 仅 0.015，说明离麦克风远/音量大小说明采集电平偏低。要定论需你配合说 3 句，并由你决定是否换引擎。

**选项 1（推荐）**:
1. 说「爱莉希雅」唤醒，等应答音后依次说一句（每句说完停 3 秒，再唤醒下一句）：
   - ① 「你能看得见屏幕吗？」
   - ② 「现在几点了？」
   - ③ 「把音量调到二十。」
   每次录音都落盘到 `.tmp\capture_<时间>.wav`（gitignore，不 commit），我读日志与 wav 做逐句 A/B 比对。
2. 顺带把系统录音音量/麦克风增益调高（本次实测 rms 0.015 是丢字主要原因之一）。

**选项 2（换引擎，需授权）**: 安装 `sherpa-onnx` + paraformer-zh（pip 约 30 MB，模型 200–400 MB，需从 hf-mirror 下载；C 盘剩 17.7 GB）。优点：中文短句精度高于 whisper small、自带标点、CPU 更快；代价：新增依赖与模型、需联网下载。授权后我先出真人 A/B 对比表再定是否切主引擎。

**选项 3**: 先提交已验证部分（工具结果文案汉化 + 录音落盘 + 参数优化），真人轮延后。

**A**: （待用户回复）
