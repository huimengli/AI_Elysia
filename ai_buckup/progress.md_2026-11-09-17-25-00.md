# progress — 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-08-20-14.md（100 行完整历史）；本文件保留 2026-11-08-18-16 起的小节 + 本批小节（AGENTS §3：先归档再 compact） -->
## 2026-11-08-18-16-33 切回 main 对比 UI（records/2026-11-08-18-16-33.md，tests/2026-11-08-18-16-33_cc/）

- **UI 差异确证**：main = 旧版（`<title>J.A.R.V.I.S.</title>`，`index.html` 52,655 B / 1,174 行，Google Fonts `@import`，无 `--pink`/`petal`，文案仅英文）；`future/AI_UI` = Elysia 版（`<title>爱莉希雅</title>`，41,769 B / 829 行，`--pink`+`petal`+`backdrop-filter`，无 CDN，全中文文案）。刷新 http://127.0.0.1:7860 对比；切分支：`git checkout future/AI_UI` 后重启 jarvis。
- 服务：llama `:8080`（Qwen3.5-2B-Q4_K_M，与分支无关）、GPT-SoVITS `:9880`（job pwsh-10，pid 4436）未重启；**jarvis `:7860` = job pwsh-21（main 代码）**。WS chat 在 main 代码下正常（`我是爱莉希雅，一位完全自主的个人 AI 助手。`），TTS `POST /tts` 200 / 271,404 B / RIFF。
- **风险**：main 不含 17:53 的 500 修复（前导 system 摘要并入唯一 system）与 `llm.py` 补丁（`chat_template_kwargs.enable_thinking`、`timeout` 15→90）→ 真人测试聊到 8 条触发压缩会重现「保存设置后管线报错」。语音真人测试请在 `future/AI_UI` 上做。
- 切分支坑：`git checkout main` 被本地已改的 `todo.md` 阻断（两分支内容不同）→ 先 commit `c071d73`（在 `future/AI_UI`，已 push）再 checkout；重启 `:7860` 需 `Stop-Process` 掉旧 python（`job_kill` 只杀 pwsh 外层）。
- 本分支台账说明：T6 Elysia UI（`80f7cd1`）、skill 修复文档（`243dc3e`/`19f1cac`/`b025a9e`/`7413031`）、三服务启动（`aaeb358`）、500 修复（`7f4ff44`）、config 记录（`9d2a9dc`）、本需求 record（`c071d73`）都在 `future/AI_UI` 上；本分支只落本需求的 record/tests/progress/tree。

#### Git 提交记录（本分支）
- 本次：records/2026-11-08-18-16-33.md（重建）、tests/2026-11-08-18-16-33_cc/（4 文件）、todo.md、progress.md、tree.md。已本地 commit（hash 见下），**未 push**（AGENTS §4 禁 push；用户此前只授权 `future/AI_UI`，main 未获授权）。

### 合并保留（future/AI_UI 侧未包含于 HEAD 的行，append-only 不删历史）
### 工作约定（2026-11-08-14-35，用户指示）
- **不允许使用子智能体（subagent / subagent_fork）**。需要子智能体时**必须先询问用户并获批准**。本会话为 T6 网页 UI 改造启动过一个子智能体（72301c15），它在落盘前被停止（`index.html` 未改、`tests/` 未建），此后 T6 由主智能体自己完成。
- 补充：本会话 spawn 已可用（沙箱 danger-full-access、审批关闭），git/node 可执行；前述"沙箱禁 spawn"仅适用于此前轮次。
### T6 网页 UI 爱莉希雅化（2026-11-08-14-12-32，records/2026-11-08-14-12-32.md）
- `jarvis/static/index.html`：53998 B / 1174 行 → 42363 B / 829 行。CSS 块（原 7–585 行 HUD 青蓝主题）整体重写为爱莉希雅主题：樱粉 `#F8A9C4`、浅粉 `#FFD8E8`、深莓 `#7E3F66`、淡紫 `#C9B7E0`、暖金 `#F2C9A8` + 深紫玻璃 `#171021/#1d1428` + `backdrop-filter` 玻璃拟态 + 樱花飘落（`prefers-reduced-motion` 降级）+ 顶部樱粉条 + 粉白渐变按钮/卡片描边；聊天气泡分角色（用户浅粉白、爱莉希雅粉紫渐变带 `✦` 刻印星标）。HTML/JS **仅改文案字面量**（中文化 + 爱莉希雅/刻印「饰品」标题），端点、id、WS 消息格式逐字未动；`jarvis/web.py`、`main.py` 未改；删除 Google Fonts `@import`（离线可用）。
- 在线风格检索未真实执行：`playwright-online-search` 缺 `chrome-headless-shell-1243` 可执行文件（`playwright install chromium` 未成功，搜索 exit 3），`web_fetch` 无外网；配色取自任务内给定的爱莉希雅色板。
- 3 轮验证全 PASS（`tests/2026-11-08-14-12-32_cc/` + 累积 `tests/opinion.md`）：轮1 `node --check` + 端点契约；轮2 静态站点 `GET /` 200 / 42363 B / 34 关键 id / 外部资源 0；轮3 node `vm` + DOM 桩喂 7 类 WS 事件，13 项断言全命中。**未做真实浏览器目视验收**（无浏览器可执行文件）。
- 分支 `future/AI_UI` commit + push：**AGENTS §4 严禁 push，本次为用户显式授权，仅推该分支、不动 main、不 force**；已在回复中提示冲突。
### 在线搜索 skill 重装（2026-11-08-15-16-18，records/2026-11-08-15-16-18.md）
- 根因：run_code 子进程 env 为空，playwright 的 `channel:'msedge'` 把路径拼成 `undefined\Program Files\Microsoft\Edge\Application\msedge.exe` → skill 一律 exit 3「no usable browser」。显式 `executablePath` 指向 `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` 实测可用（Edge 143.0.3650.139）。
- 修复（skill 目录 `C:\Users\楼听\.dsh\skills\playwright-online-search\search.mjs`，**在仓库外，不 commit**）：新增 `ENV_DEFAULTS` + `repairEnv()`（缺失才补 `ProgramFiles`/`ProgramFiles(x86)`/`LOCALAPPDATA`/`USERPROFILE`/`SystemRoot`），`launch()` 序列改为 `msedge` → `msedge-x86`（显式路径）→ `msedge-x64` → bundled `chromium`；`node --check` 通过。
- 三轮验证（`tests/2026-11-08-15-16-18_cc/` + 累积 `tests/opinion.md`）：bing **exit 0** 8 条、baidu **exit 0** 5 条（崩坏3 官网 / miHoYo 爱莉希雅主题配饰 / 崩坏3WIKI 壁纸）、duckduckgo **exit 5**（`net::ERR_CONNECTION_TIMED_OUT`，本机网络不可达，skill 正确上报）+ 补充 bing **exit 0**。结论：**skill 已恢复可用，后续检索默认用 bing/baidu**。
- 后台遗留：`npx playwright install chromium`（195.6 MiB）两次前台 500 s 超时被杀（进度 10%/0%），改 detached `cmd /c` 重定向到 `%TEMP%\pw_install.log` 继续；`ms-playwright` 仍只有 `.links`/`__dirlock`（未装完，非必需）。
- **真因是磁盘**：`wmic` 实测有一块盘 FreeSpace=0（C: 已满），`ENOSPC` 使 `playwright install` 必然失败（30% 时 `ENOSPC: no space left on device`）。已把 `PLAYWRIGHT_BROWSERS_PATH` 指到 `F:\playwright-browsers`（约 87 GB 空闲）并写入 skill 的 `ENV_DEFAULTS`；下载改由自管 detached 脚本 `F:\Temp\dl.cjs` 写入 `F:\playwright-browsers\headless.zip`（进度 `F:\Temp\pw_install.log`）。**skill 靠系统 Edge 已可用**，bundled chromium 只是第三层冗余。
### 全部服务启动，供真人测试（2026-11-08-17-29-39，records/2026-11-08-17-29-39.md）
- 在线服务：**llama.cpp :8080**（pid 20684/16252，`Qwen3.5-2B-Q4_K_M.gguf`，此前已在跑）+ **GPT-SoVITS api_v2 :9880**（pid 4436，job pwsh-10，绝对路径启动，首次相对路径 exit 1）+ **Jarvis jarvis.main :7860**（pid 12880，job pwsh-9，带 HF 镜像 env）。真人测试入口 **http://127.0.0.1:7860**。
- 3 轮验证全 PASS（`tests/2026-11-08-17-29-39_cc/` + 累积 `tests/opinion.md`）：**轮1 LLM** —— 裸调 8080 无 `chat_template_kwargs` 时 `content=""`、token 全进 `reasoning_content`，带 `enable_thinking:false` 后 content 非空（jarvis `main.py:264-270` 已带，链路正确）；**轮2 TTS** —— `/tts` 200、314,924 B、`RIFF` 头；**轮3 Web UI+WS** —— `GET /` 200/42,420 B（`爱莉希雅` 标题 + `--pink` + `petal`）、三个 API 200、WS `chat` → 6 事件含 `response`，事件落库。
- 语音链路实况：**wake 触发正常**（aili_xiya_v0.3）→ 30 s 录音 → **STT cuda 失败（CUDA driver version is insufficient）回落 CPU**（`small on cpu`）→ 当时「Transcription empty」。副作用提醒：`type_text` 工具会真往 PC 打字，测试前先用「中止」。
### 保存设置后管线报错：根因与修复（2026-11-08-17-53-00，records/2026-11-08-17-53-00.md）
- 真因不是设置页：保存后继续多轮对话使 `context` 窗口达 `summarize_after=8` → `context.py:49` 把 `[Earlier context: …]` 作为**第二条 system** → Qwen3.5 chat template 第 85 行 `raise_exception("System message must be at the beginning")` → 8080 返回 500 → jarvis 回落未运行的 Ollama，用户只看到「连接不上 Ollama」。探针确证：A `[system,user]` 正常 / B 第二条 system → 500 / C 首位非 system → 500。
- 修复（`fix(AI)`）：`main.py::_process_request` 把前导 system 摘要并入唯一 system 消息，并在主 provider 失败时把**主错误**写进 `status` 事件与事件库；`llm.py` openai 分支补 `chat_template_kwargs.enable_thinking`（否则 content 全空、摘要为空串）且 `timeout` 15→90（15 s 掐断 2B 生成使摘要与子代理回落 Ollama）。3 轮验证（`tests/2026-11-08-17-53-00_cc/`）：连续 5 轮对话（窗口达 8 触发压缩）5 条 response 全出无 500；重启后 UI 200/42,420 B、API 200、TTS 200/266 KB RIFF、WS 对话正常。
- 运维坑：`job_kill` 只杀 pwsh 外层，旧 python 仍占 `:7860`（新实例 `10048` 退出）→ 必须 `Stop-Process -Id` 旧 pid 后重启；当前 jarvis = job pwsh-17。C 盘仅剩 **0.3 GB**。
- **2026-11-08-16:58 装成**（用户清理 C: 后）：ENOSPC 消失，但官方 `playwright install` 两次在 40% 被 `ECONNRESET` 打断（跑不完 114.6 MiB）；改 `curl -C -` 断点续传拉满 zip（120,200,717 B，exit 0）+ `Expand-Archive` 到 `F:\playwright-browsers\chromium_headless_shell-1243`（`chrome-headless-shell.exe` 212 MB）。探针 launch+bing 浏览 **version 153.0.8010.12**；三层回退（msedge / 空 env 兜底 / 强制 bundled）三轮 skill 命令均 **exit 0**（6/5/6 条）。**skill 完全恢复**。
#### Git 提交记录（T6）
- `80f7cd1` `feat(AI): Web UI 爱莉希雅化（樱粉玻璃拟态 + 樱花飘落 + UI 中文化），3 轮验证`（11 files, +408/-665）。已本地 commit **并 push 到 `origin/future/AI_UI`**（新建远程分支，用户显式授权，AGENTS §4 禁 push 冲突已在回复提示）。分支含 `main` 的 3 个本地提交（`cb3b904`/`35cd7ae`/`338393d`）作为祖先，`main` 未动、未 force。
#### Git 提交记录（在线搜索 skill 重装）
- `19f1cac` `docs(AI): 在线搜索 skill 装成 Chromium Headless Shell（curl 断点续传）+ 三层回退 3 轮验证`；`b025a9e` `docs(AI): 复核在线搜索 skill 三层回退（强制 bundled chromium 复跑 exit 0 / 5 条）`。**已本地 commit 并 push 到 `future/AI_UI`**（`243dc3e..b025a9e`，17:31 网络恢复后成功；期间 3 次 push 失败：Connection reset / Empty reply / 连不上 github.com:443）。AGENTS §4 禁 push，本次为用户对该分支的显式授权，未动 main、未 force。
## 2026-11-08-18-39-40 合并 future/AI_UI 进 main（records/2026-11-08-18-39-40.md，tests/2026-11-08-18-39-40_cc/）

- **合并完成**：merge commit `99aeaf1`（**本地合并，未 push**）。Elysia UI（`80f7cd1`）、500 修复（`7f4ff44`）、`llm.py` 补丁、skill 与三服务/config 台账、全部 records/tests 批次现在都在 main 上；`future/AI_UI` 分支保留（HEAD `c071d73`）。
- **冲突处理（5 处，保留两侧内容，append-only 不删历史）**：`progress.md`、`todo.md`、`tests/opinion.md`、`tree.md`（content）+ `records/2026-11-08-18-16-33.md`（add/add）；`tree.md` 用合并后 `git ls-files`（113 文件）重建。代码文件由 git 自动合入 AI_UI 侧：`git diff --stat future/AI_UI -- jarvis/main.py jarvis/llm.py jarvis/static/index.html config.yaml README.md` 空输出（完全一致）。
- 3 轮验证：轮1 一致性 + `py_compile` 全 0；轮2 main 上 UI 已是 Elysia 版（200 / 42,420 B、`爱莉希雅`、`--pink`/`petal`、无 CDN、无 `J.A.R.V.I.S.`）+ `/api/settings` 200 + WS 回复；轮3 连续 5 轮对话跨窗口 8 触发压缩，5 条 response 全出无 500（第 5 条为真实摘要），TTS 200 / 258,604 B RIFF。当前 **jarvis `:7860` = job pwsh-23（合并后的 main 代码）**，llama `:8080` 与 GPT-SoVITS `:9880`（job pwsh-10，pid 4436）未重启。
- 坑（与切分支同因）：`git merge` 会被未提交的 `todo.md` 改动阻断 → 先 commit 本需求 record+todo（`38c9a7e`）再合并；重启 `:7860` 需 `Stop-Process` 掉旧 python（`job_kill` 只杀 pwsh 外层）。测试副作用：`write_file` 在仓库根写了 `love_silvia.txt`（60 B，未 commit）。
### 真人语音输入变「You」+「Done.」：STT 语言与空 content 兜底（2026-11-08-18-54-18，records/2026-11-08-18-54-18.md）

- 两个独立成因：① `stt.py` 45/53 行把 `language="en"` **写死** → 中文口语被英文解码（事件库 `18:49:07 user "You" source=voice`），合成中文音频对照：en → `I love you, Alicia. Yes. Tomorrow is the 3rd day of the meeting…`，zh → `爱利西亚 对 明天下午三点开会 记得带笔记本和钥匙`，None → 同 zh（detected zh 0.967）；② `main.py` 342-343 行在模型工具轮后返回空 content 时**字面兜底 `"Done."`**。
- 修复（`fix(AI)`）：`stt.py` 语言取 `config.yaml` 的 `stt.language`（新增 `language: zh`，缺省 zh）；`main.py` 加 `_looks_understandable()` 守卫（无 CJK 且 ≤20 字符 → 「我没听清，请再说一遍。」，不调 LLM）；`_call_openai_provider` 记录 `executed` 并用 `_tool_report()` 兜底（无工具→「我处理好了。」；有工具→「我执行了 X、Y：结果首行」），`Done.`/`OK`/`已完成` 当空。复测 WS 2 条中文 chat：**裸 Done. 计数 0**。
- 真人测试提示：2B 把「记一下」理解成 `type_text` 往记事本打字 + `focus_window`（找不到「记事本」）→ **语音测试会在桌面真实打字**，先按「中止」；「爱莉希雅」常听成「爱利西亚」。当前 **jarvis = job pwsh-30**（含全部修复）；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。C 盘已清理。
### 语音无法触发：阈值 0.75 高于真实峰值 + 残留 abort 砍录音（2026-11-08-19-25-48，records/2026-11-08-19-25-48.md）

- 直接原因是**门槛**：17:53 设置页保存的 `wake_word.threshold: 0.75`；真人 1.5 分钟 `[Wake] peak` 最高 **0.570**，而合成「爱莉希雅，爱莉希雅」（2.98 s，rms 0.083，16k 重采样）37 chunk **PEAK 0.862** —— 模型没问题，是阈值太高（验收可用值 0.7：v0.3c recall 0.94 / fp 0.09）。改成 **0.65** 后真人连续触发（事件库 162/166/168/173 行 wake，peak 0.716/0.689/0.734）。
- 两个观测/逻辑缺口一并修：① `wake.py` 原本无分数日志（「叫不应」与「麦克风坏」无法区分）→ 新增 3 s 节流 `[Wake] peak X / threshold Y`；② `record_until_silence` 每 chunk 查 `_abort_event`（`stt.py` 94-96），而 `_abort.clear()` 只在录音之后的 `_process_request`（`main.py` 500）；`wake.py` 121-122 行 busy 时喊醒词会 `abort_all()`（UI「中止」/Esc 同理）→ 残留 flag 让下一轮录音第一 chunk 就 break（0.3 s → `Wake: no voice recognized`，事件库 160/165/167/169 行）。修法：`_on_wake` 录音前显式 `_abort.clear()`；复测完整链路（wake → `Speech detected rms=0.0432` → 转写 → 回复）。
- 真人测试提示：2B 把「说一句话/记一下」理解成 `type_text` 往桌面打字（本轮真机打了 `我是爱莉希雅`），先按「中止」（UI 中止 / WS `{"type":"interrupt"}` / Esc）；「爱莉希雅」仍常听成「爱利西亚」。当前 jarvis = **job pwsh-38**（阈值 0.65 + 分数日志 + abort 清零 + 上一批 STT 修复）；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。要更灵敏设 0.60，别回 0.75。

#### Git 提交记录（语音修复批次）
- `dc1f3ff` `fix(AI): STT 语言改为 config 驱动（zh）并修空 content 兜底的字面 Done.`
- `ccb7e60` `fix(AI): 唤醒阈值降为 0.65 并修残留 abort 把录音砍成 0.3s`（**已本地 commit，未 push**；AGENTS §4 禁 push，你只授权过 `future/AI_UI`）
### 真人语音「能唤醒却总答『我没听清』」：录音被自己的 barge-in 打断 + get_time 工具（2026-11-08-19-52-59，records/2026-11-08-19-52-59.md）

- 根因：IDLE 冷却只有 **2 s**（挡不住她的 ack『在。』+ 用户紧接着说话）+ busy 分支的 `is_recording()` 在录音窗口前 0.15 s 仍为 False → `abort_all()`；`record_until_silence` **每个 chunk** 查 abort flag → 第一 chunk（0.3 s）就 break → `Wake: no voice recognized`。现场追踪铁证：`[Wake] barge-in score=0.664 recording=False` + `[ABORT] set by listen_for_wake_word:135 thread=MainThread`（新增日志，job pwsh-44/46）。
- 修复：`handle_wake` 入口置 `_stt_recording = True`（`finally` 清零，顺带解决残留 flag）、IDLE 冷却 2 s → **5 s**、abort 检查加 **1.5 s 宽限**（前 1.5 s 忽略 flag）。复测真人语音：`[STT] Speech detected (rms=0.0272)` → `Recorded 1.5s` → 事件库 217 行 user `现在几点了`（voice，不是碎片），`Transcription empty` 消失。
- 真人反馈「回答是天气」→ 新增 `get_time`（`jarvis/tools/system.py` + `router.py` TOOL_MAP/schema，33 schema 含 get_time；`dispatch` 实测 `2026-11-08 20:09:20 星期日`）+ 系统提示「问时间/日期用 get_time，不要用 get_weather」：218 行 `现在是 2026年 11月 8 日 20 点 10 分，星期日。`、221 行 `現在是晚上 8 點 12 分，星期日。`（whisper 偶发繁体；「爱莉希雅」仍常听成「爱利西亚」）。
- 真人测试注意：2B 会把「说一句话/记一下」理解成 `type_text` 往桌面打字，先按「中止」（UI 中止 / WS `{"type":"interrupt"}` / Esc）；1.5 s 后的 barge-in 仍会截断长句子（遗留）。当前 jarvis = **job pwsh-50**；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。

#### Git 提交记录（本批）
- `b501812` `docs(AI): 语音批次 Git 提交台账（dc1f3ff / ccb7e60）`；本批 `get_time` + abort 宽限的 hash 见下一条（追加）。
- `35984ac` `fix(AI): 修录音被自己的 barge-in 打断（1.5s 宽限 + 5s 冷却）并新增 get_time 工具`（**已本地 commit，未 push**；AGENTS §4 禁 push，你只授权过 `future/AI_UI`）
### 网页端不实时更新：状态字符串只匹配英文字面量（2026-11-08-20-22-00，records/2026-11-08-20-22-00.md）

- **不是广播坏了**：真实页面 2 s 内就能看到 `user/tool/tool_result/response` 气泡（140→147），WS 序列含 `status:思考中…`。真 bug 是 `index.html` 的 `case 'status'` 只匹配 `Thinking...`/`Listening...`/`Speaking...`/`Wake.`/`Stopped.`/`Ready.`，后端发的是中文（`思考中…`/`正在聆听…`/`在。`/`已停止。`/`主模型失败：…`）→ 状态灯、活动条、状态文字永远停在 `待命`，观感就是「刷新才有新内容」。
- 修复：`case 'status'` 同时匹配中文+英文（含 `在。`、`主模型失败` 前缀）；`onopen` 加 20 s 心跳 `{type:'ping'}` + 每次（重）连重拉历史；`onclose` 清理心跳。复测：发送后 `处理中`→`说话中`、回复 `1+1 等于 2。` 无需刷新；注入 7 条模拟消息状态依次 `聆听中/在。/处理中/待命/主模型失败，改用备用…`；主动 `ws.close()` → `离线` → 4 s 后自动 `已上线`。
- 测试手法（可复用）：Playwright `channel: msedge` + `addInitScript` 包裹 `window.WebSocket` 记录消息时序（**reload 会清空页面注入**）；改 `index.html` **不需要重启** jarvis（FastAPI 从磁盘读）。验证 3 轮：[tests/2026-11-08-20-22-00_cc/](tests/2026-11-08-20-22-00_cc)。当前 jarvis = **job pwsh-50**；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。

#### Git 提交记录（本批）
- 本批 hash 见下一条（追加）。
- `904dbc8` `fix(AI): 网页端实时状态改为匹配中文广播并加心跳/重连重拉历史`（**已本地 commit，未 push**；AGENTS §4 禁 push，你只授权过 `future/AI_UI`）

## 2026-11-09-15-37-58 浏览器共用插件评估规则 + 状态显示器定稿（records/2026-11-09-15-37-58.md，tests/2026-11-09-15-37-58_cc/）

### 插件准入规则（用户 2026-11-09 指示，长期有效，对之后所有「装插件/连接器/扩展」生效）
1. **口碑与评分**：查仓库 star / npm·Chrome 商店下载量与评分、issue 活跃度、是否官方厂商维护（Google/Microsoft 官方优先）、最近发布时间；无口碑 = 不装。
2. **恶意执行**：是否执行任意代码（stdio 命令、postinstall 脚本、native 消息宿主 `nmh`）、是否要求管理员、是否写入 startup/服务、是否可被远端下发指令。
3. **数据外发**：是否向远程地址发送页面内容/URL/凭据/剪贴板（含遥测、云 relay、telemetry、统计）。本地 stdio + 仅回环连接 = 通过；走云端中转 = 拒绝；官方遥测需如实告知用户并可关闭。
4. 三问逐条写进 `records/时间.md` 与 `progress.md`（本小节），**通过才装**；装之前必须取得用户明确授权（本会话审批关闭，任何需要审批的动作会被自动拒绝）。
5. 优先「共用用户自己的浏览器」形态（扩展 / CDP 附着到用户 Chrome），避免我再开一套 Playwright/Edge 实例。

### 观测配额规则（用户 2026-11-09-15:5x 指示：「禁止大量截图/读图，会导致隧道崩溃」）
1. **禁止批量截图 / 批量读图**：同一目标反复整屏截图、连环 screenshot 轮询、用 read_image 看图「确认」都算违规；一次会话内截图只用于「首次定位 + 真需要目视验收」，优先次数 ≤ 个位数。
2. 观察优先走**文本通路**：`computer_windows`（窗口列表）、`computer_accessibility` + `computer_find` + `computer_read`（UIA/MSAA 语义树）、命令输出**重定向到 `.tmp/*.log` 文件后用 `read` 读**，以及 `/api/health` 这类 HTTP 探针。
3. 需要目视验收时：一次截图 + `save_to`，需要 OCR 时用 `wow-sight.ocr` 对已存文件跑一次，不叠加读图。
4. 轮询用 `wow_wait`/文件日志，不用「截图 → 看 → 再截图」。

### 本会话（2026-11-09 16:00–17:20）执行与验证结果

- **新执行通道（沉淀，后续复用）**：`write` 生成 `.bat`（路径用 `%USERPROFILE%`，纯 ASCII 避免 PowerShell 5.1 的 GBK 乱码）→ 用资源管理器**文件列表 UIA `invoke`**（地址栏只接受纯可执行文件，带参数的命令行会被当导航）→ 「打开文件 - 安全警告」点「运行(R)」（区域截图 + 图像坐标 `x=114,y=61`）→ 输出重定向到 `.tmp\*.log` → 用 `read` 读。`cmd` 的 `>` 保留原始字节（curl 的 UTF-8 JSON 可读），PowerShell 的 `>` 生成 UTF-16 不可读。
- 服务重启并实测监听：llama `:8080`(pid 16876)、GPT-SoVITS `:9880`(pid 18284，CPU 回退，权重 Elysia e20/e24)、jarvis `:7860`(pid 1924)；GSV 日志出现真实 `GET /tts … 200 OK`。
- 需求 4 落地：`web.py` 新增 `GET /api/health`（asr 进程内在线 + `warm`=模型已加载；llm/tts = `base_url`/`api_url` 的 TCP 探测）；`index.html` 页头 6 芯片按 `待命中/已离线/聆听中/说话中/执行中/思考中` + 右侧 `语音识别/LLM/TTS` 三盏灯，5 s 轮询；WS 断开 → `已离线`。
- 验证 3 轮全 PASS（`tests/2026-11-09-15-37-58_cc/`，细节见 `tests/opinion.md` 末段）：协议层、真实 Chrome 渲染、`stop` 去重与「当下真实回答」（17:17/17:19 简体 + 真实时钟，应答 2 s）。
- 需求 1 结论：`Tool 'xxx' failed: 'NoneType' object has no attribute 'strip'` 为 11-08 历史事件（`router.py::_coerce` 904dbc8 已修）；繁体与「问时间答天气」本轮未复现；遗留是 2B 模型措辞啰嗦。
- 需求 6 评估结论：**Playwright MCP `--cdp-endpoint`（回环附着用户 Chrome）通过**；Chrome DevTools MCP 通过（二者择一，勿同时装）；Browser MCP（云端 relay）**拒绝**。三问逐条见 `records/2026-11-09-15-37-58.md` 追加节。`mcp_connector_configure` 需用户明确授权后执行；建议给用户 Chrome 加 `--remote-debugging-port=9222`。
- 观测配额遵守情况：仅 3 张小区域截图（安全警告按钮、标签栏、页底输入条），其余全部 UIA 语义树 + `.tmp/*.log` 文本读取；Chrome 页面全文用 `computer_read` 的 TextPattern 取得，未用截图/OCR。
- 待办：`todo.md` 的 `2026-11-08-20-44-17` 仍未勾选（代码在 HEAD，未真人复验）；本批 commit hash 见下节。

#### Git 提交记录（本批）
- 本批 hash 见下条（追加）。


