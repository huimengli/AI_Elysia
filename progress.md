# progress — 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-10-16-56-00.md（含 2026-11-08-20-22 网页实时、2026-11-09-15-37 状态显示器+四灯+插件评估、2026-11-09-18-21 服务重启复验+Alt+R 通道、2026-11-09-19-45 matplotlib/llama 启动段等小节）。本文件保留长期规则 + Git 提交记录 + 最近三批。 -->

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
- 运维：重启 `:7860` 用 `Get-NetTCPConnection -LocalPort 7860 -State Listen` 找 pid → `Stop-Process` → `Start-Process -WindowStyle Hidden` 拉起 `.venv\Scripts\python.exe -u -m jarvis.main`（精确，不伤 GPT-SoVITS）。

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
- 最后一条 hash 的「记录该 hash 的 commit」不再追加，避免无限循环。

## 2026-11-09-20-35 状态灯加「唤醒」（语音识别左侧）

- 需求（「语音识别左边再加一个 '唤醒'」）→ `records/2026-11-09-20-35-43.md`。
- 关键障碍：`wake.py` 的模型与 `_peak`/`_last_detect` 是函数局部变量，健康接口读不到 → 模块级 `state` 发布 `online/listening/model/threshold/score/peak/last_detect`，由唤醒线程就地写入。
- `web.py` 三灯→四灯（`wake` 排 `asr` 前，`import time`，`last_detect` 本地化、0 值置 `""`）；`index.html` `lamp-wake` 插在 `lamp-asr` 前，灯序 `唤醒/语音识别/LLM/TTS`，让麦克风时**黄灯**（非离线）。
- 3 轮全 PASS（`tests/2026-11-09-20-35-43_cc/`）：health 四灯真值、服务端 HTML 灯序与 JS 绑定、进程内快照优雅退化。全程零截图。

## 2026-11-09-21-19 `start_all.bat`：ASCII + CRLF + `start` 开四个 cmd 窗口

- 需求（「start_all.bat 应当是 CR LF 换行 ASCII 编码」「应通过 start 打开三个(或更多)cmd 界面」）→ `records/2026-11-09-21-19-29.md`。
- 实测改前 `CR=56 LF=56`（换行本来就是 CRLF），`nonASCII=250`（框线 `─` + 中文）→ 也是 `read` 直读报 `invalid UTF-8` 的原因。改后 `len=2912 / CR=50 / LF=50 / nonASCII=0`，`starts=4`、`cmd_window_starts=3`。
- 窗口写法定稿：**`start "标题" cmd /k "cd /d %~dp0... & set ... & 程序"` 单行形式**（`cmd /k ( 多行 )` 括号复合不可靠，废弃）；4 窗 = `llama.cpp :8080` / `GPT-SoVITS :9880` / `AiliXiya :7860` / `Jarvis Status`（每 5 s 刷新端口 + health）。
- 幂等：每段先 `netstat`，已 `LISTENING` 就 `[Skip] :NNNN already in use` 并跳过；关窗即停该服务。
- 3 轮全 PASS（`tests/2026-11-09-21-19-29_cc/`）。遗留：`call start_all.bat` 后父脚本尾部输出未落盘（`exit /b 0` 交互），不影响双击。

## 2026-11-09-21-55 阈值 0.7 + 唤醒音内存直放 + 工具名汉化

- 需求（`records/2026-11-09-21-55-14.md`）：① 触发阈值 0.7；② 唤醒后固定应答音「直接播已有音频」，不进 TTS；③ 工具播报汉化（`type_text → 输入文本`、`press_key → 按下按钮`）。2026-11-10 16:38 起执行（隔夜后三服务全停，由 `start_all.bat` 重新拉起）。
- ① `config.yaml` `wake_word.threshold 0.65 → 0.7`（`wake.py` 与灯都读该值，无硬编码）。实测 `/api/health` `threshold=0.7`；真人唤醒 `peak 0.773` 命中，环境噪声峰值 0.25–0.62 全不触发（v0.3c 验收：0.7 → recall 0.94 / FP 0.09）。
- ② `jarvis/tts.py` 新增 `preload_ack_audio()`（启动时把 5 条 ack wav 解码成内存 float32 PCM）+ `_output_stream()`（**常驻复用同一条** `sd.OutputStream`）；`play_ack_wav()` 只写流，不再 `wave.open`、不再 `sd.play` 建流、不发 TTS 请求；`main()` 启动时预热。建流 3125–3444 ms 移到启动一次性支付，唤醒后 `ack stream ready 0 ms`，出声延迟 ≈20 ms（2.26 s 音频 total 2281 ms；真人唤醒 total 2069 ms）。
- ② 修的两个真缺陷：`sd.OutputStream(latency="small")` 在这版 sounddevice 抛 `TypeError: must be real number, not str`（要数值 blocksize）→ 去掉；只缓存 PCM 不够（首次唤醒仍付 3.4 s 建流）→ 启动预热建流（`output stream warmed in 2868 ms`）。
- ③ `jarvis/tools/router.py` 加 `TOOL_LABELS`（33 项）+ `tool_label()`；`main.py` `_tool_report()` 用中文名，`tool`/`tool_result` 广播 4 处（llamacpp + ollama 分支）新增 `label`；`index.html` 状态条/活动条/工具日志/实时流用 `msg.label || msg.name`。实测文案 `我执行了 输入文本、按下按钮：OK enter`；真人网页触发事件 `["tool","get_time","看时间"]`、`["tool_result","get_time","看时间"]`。英文 `name` 保留（检索/LLM schema 不变）。
- 3 轮全 PASS（`tests/2026-11-09-21-55-14_cc/`，累积见 `tests/opinion.md`）。全程零截图。
- 遗留登记（未改）：真实语音轮 STT 两次 `ConnectError WinError 10054`（`.tmp\jarvis3.log:19-23`）、`asr.warm=false`、VAD 在噪声下录满 30 s 上限；改 `threshold` 后必须重启 Jarvis 才刷新灯上的数值。
