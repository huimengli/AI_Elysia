# progress — 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-09-17-25-00.md（含 2026-11-08 全部批次小节：T6 网页 UI、在线搜索 skill、三服务启动、500 修复、STT 语言/空 content、唤醒阈值 0.65、abort 宽限 + get_time、网页实时状态中文匹配）。本文件保留长期规则 + 最近批次 + Git 提交记录（AGENTS §3：先归档再 compact）。 -->

## 长期规则与约定

### 工作约定（2026-11-08-14-35，用户指示）
- **不允许使用子智能体（subagent / subagent_fork）**；需要时必须先询问用户并获批准。

### 浏览器共用插件准入规则（用户 2026-11-09 指示，长期有效）
1. **口碑与评分**：仓库 star / npm·Chrome 商店下载量与评分 / issue 活跃度 / 是否官方厂商维护（Google·Microsoft 官方优先）；无口碑 = 不装。
2. **恶意执行**：是否执行任意代码（stdio 命令、postinstall、native 消息宿主）、是否要求管理员、是否写 startup/服务、是否可被远端下发指令。
3. **数据外发**：是否向远程地址发送页面内容/URL/凭据/剪贴板（遥测、云 relay、统计）。本地 stdio + 仅回环 = 通过；云端中转 = 拒绝；官方遥测须告知用户并可关闭。
4. 三问逐条写入 `records/时间.md` 与本节，**通过才装**；装前取得用户明确授权（本会话审批关闭，需审批的动作会被自动拒绝）。
5. 优先「共用用户自己的浏览器」形态（扩展 / CDP 附着用户 Chrome），避免我再开一套 Playwright/Edge 实例。
6. 本批评估结论：Playwright MCP `--cdp-endpoint`（回环附着用户 Chrome）**通过（推荐）**；Chrome DevTools MCP **通过**（二者择一，勿同时装）；Browser MCP（云端 relay）**拒绝**。三问明细见 `records/2026-11-09-15-37-58.md`。

### 观测配额规则（用户 2026-11-09-15:5x：「禁止大量截图/读图，会导致隧道崩溃」）
1. 禁止批量截图/读图；一次会话内截图只用于「首次定位 + 真需要目视验收」，优先 ≤ 个位数。
2. 观察走**文本通路**：`computer_windows` 窗口列表、`computer_accessibility` + `computer_find` + `computer_read`（UIA/MSAA 语义树，Chrome 页面全文可用 RootWebArea 的 TextPattern 直接读出）、命令输出重定向到 `.tmp/*.log` 后用 `read` 读、HTTP 探针。
3. 目视验收时截图 + `save_to`；需 OCR 只对已存文件跑一次。轮询用文件日志，不「截图→看→再截图」。

### 执行通道（本会话沉淀，可复用）
- 本会话无 shell 工具，键盘注入到控制台不落地。可用通道：`write` 生成 `.bat`（纯 ASCII + `%USERPROFILE%`，避免 PS 5.1 把 UTF-8 当 GBK）→ 资源管理器**文件列表 UIA `invoke`**（地址栏只接受纯可执行文件，带参数的命令行会被当导航）→「打开文件 - 安全警告」点「运行(R)」→ 输出重定向 `.tmp\*.log` → `read`。
- `cmd` 的 `>` 保留原始字节（curl 的 UTF-8 JSON 可读）；PowerShell 的 `>` 生成 UTF-16 不可读。中文 commit message 在 `cmd` 里会被当 GBK → commit 用 ASCII 主题。
- 运维：重启 `:7860` 需 `Stop-Process` 掉旧 python（`job_kill` 只杀外层 pwsh）；C 盘曾仅剩 0.3 GB；`PLAYWRIGHT_BROWSERS_PATH` 指向 `F:\playwright-browsers`。

## 2026-11-08-20-22-00 网页端不实时更新：状态只匹配英文字面量（records/2026-11-08-20-22-00.md，tests/2026-11-08-20-22-00_cc/）

- 真 bug：`index.html` 的 `case 'status'` 只匹配 `Thinking...`/`Listening...`/`Stopped.` 等英文，后端发的是中文（`思考中…`/`在。`/`已停止。`）→ 状态灯与状态文字停在 `待命`，观感是「刷新才有新内容」。修复：同时匹配中英、`onopen` 加 20 s 心跳 + 重连重拉历史、`onclose` 清心跳；复测发送后 `处理中→说话中`、主动断开后 4 s 自动 `已上线`。改 `index.html` 不需重启 jarvis（FastAPI 从磁盘读）。

## 2026-11-09-15-37-58 状态显示器 + ASR/LLM/TTS 在线灯 + 服务重启 + 插件评估（records/2026-11-09-15-37-58.md，tests/2026-11-09-15-37-58_cc/）

- 落地：`web.py` 新增 `GET /api/health`（asr 进程内在线 + `warm`=模型已加载；llm/tts = `base_url`/`api_url` TCP 探测）；`index.html` 页头 6 芯片按 `待命中/已离线/聆听中/说话中/执行中/思考中` + 右侧 `语音识别/LLM/TTS` 三盏灯（5 s 轮询，WS 断开 = `已离线`）。
- 服务由本会话重启并实测监听：llama `:8080`(pid 16876)、GPT-SoVITS `:9880`(pid 18284，CPU 回退，权重 Elysia e20/e24)、jarvis `:7860`(pid 1924)；GSV 日志出现真实 `GET /tts … 200 OK`。
- 验证 3 轮全 PASS（`tests/2026-11-09-15-37-58_cc/`，累积结论见 `tests/opinion.md` 末段）：① 协议层（health 三项在线、WS connected/stop 应答、页面标记含芯片与 `svcLamps`/`pollHealth`）；② 真实 Chrome 渲染（页头顺序 + 三盏灯 + 状态文字，事件条目已出现，2 s 轮询兜底）；③ `stop` 去重与「当下真实回答」：两次 1.2 s 的 stop 各一条应答、无重复系统气泡；17:17/17:19 问时间 → **简体**中文 + **真实时钟**，应答 2 s。
- 需求 1（幻觉）结论：`Tool 'xxx' failed: 'NoneType' object has no attribute 'strip'` 是 11-08 历史事件（`router.py::_coerce` 904dbc8 已修，`None` 参数强转 `""/0`）；繁体与「问时间答天气」本轮未复现；遗留是 2B 模型措辞啰嗦（`星期一是星期一`）。
- 双浏览器根因确认：我驱动 Playwright/Edge、用户用 Chrome，两套实例互不可见；共用浏览器方案见上节评估结论，配置需用户授权（建议 Chrome 加 `--remote-debugging-port=9222`，我用 `--cdp-endpoint` 附着）。
- 待办：`todo.md` 的 `2026-11-08-20-44-17` 仍未勾选（代码在 HEAD，未真人复验）。

#### Git 提交记录（近三批，均**已本地 commit，未 push**；AGENTS §4 禁 push，用户此前只授权 `future/AI_UI`）
- `35984ac` `fix(AI): 修录音被自己的 barge-in 打断（1.5s 宽限 + 5s 冷却）并新增 get_time 工具`
- `904dbc8` `fix(AI): 网页端实时状态改为匹配中文广播并加心跳/重连重拉历史`；`104045f` `docs(AI): 网页实时批次提交台账（904dbc8）`
- `a0ecd92` `fix(AI): add status display + ASR/LLM/TTS health lamps, restart services and verify realtime UI in 3 rounds`（16 files，含 records/tests/progress/todo + `web.py`/`index.html`/`main.py`/`stt.py`/`wake.py`/`router.py`/`.gitignore`；commit 主题用 ASCII，因 `cmd` 会把中文当 GBK 写入）
- `1e16ca6` `docs(AI): rebuild tree.md, archive+compact progress.md, todo status, add untracked record 2026-11-08-20-44-17`（4 files；`tree.md` 由 `git ls-files` + 未跟踪的非忽略文件重建；`records/2026-11-08-20-44-17.md` 从「未跟踪」补入库；**已本地 commit，未 push**）
- `cc6830a` `docs(AI): record 1e16ca6 hash, 18-21 service restart re-verification, Alt+R run channel fix`（2 files / 16 insertions；**已本地 commit，未 push**）
- `9939d8d` `docs(AI): append cc6830a commit hash to progress ledger`（1 file；**已本地 commit，未 push**）
- `324fe25` `fix(AI): start_all.bat sets MPLCONFIGDIR to kill matplotlib WinError5 and launches llama :8080 too`（3 files / 57 insertions；新增 `records/2026-11-09-19-45-46.md`；**已本地 commit，未 push**）
- `10d2b55` `docs(AI): append 324fe25 hash and 19-45 matplotlib/launch fix section to progress ledger`（1 file / 10 insertions；**已本地 commit，未 push**）
- `4840591` `feat(AI): add wake-word health lamp left of ASR via wake.state plus 4-lamp api health, verified 3 rounds`（11 files / 220 insertions / 76 deletions：`jarvis/wake.py`、`jarvis/web.py`、`jarvis/static/index.html`、`records/2026-11-09-20-35-43.md`、`tests/2026-11-09-20-35-43_cc/` 5 件、`todo.md`、`progress.md`、`tree.md`；**已本地 commit，未 push**）
- `c1f358e` `docs(AI): append 4840591 hash to progress ledger and add 20-35 batch conclusion to cumulative opinion`（2 files / 8 insertions；**已本地 commit，未 push**）
- `387b320` `fix(AI): rewrite start_all.bat as pure ASCII CRLF with start-opened cmd windows for llama gptsovits jarvis and status panel, verified 3 rounds`（10 files / 158 insertions / 47 deletions：`start_all.bat`、`records/2026-11-09-21-19-29.md`、`tests/2026-11-09-21-19-29_cc/` 5 件、`tests/opinion.md`、`todo.md`、`progress.md`、`tree.md`；**已本地 commit，未 push**；本批起改用 `pwsh` 通道跑 git，不再走「运行(R)」弹窗）
- 最后一条 hash 的「记录该 hash 的 commit」不再追加，避免无限循环。

## 2026-11-09-18-21 服务重启复验（用户：「服务你需要重启一下」）

- 重启前实测：`netstat` 无 `:8080/:9880/:7860` 监听，`tasklist` 无 `llama-server`/`python.exe`；只有 pid 3016 对 `:7860` 的 `SYN_SENT`（连不上）。
- 用 `.tmp\start_services.ps1`（ASCII 版）重启三服务：llama `:8080` pid 2072（`llama.log` 显示模型 `Qwen3.5-2B-Q4_K_M`，`n_ctx 65536`，`/v1/models` 正常应答）、GPT-SoVITS `:9880` pid 19084（Elysia e20/e24 权重 + BERT/HuBERT 加载，CPU；cublas/cudart 缺失仅告警，走 CPU）、Jarvis `:7860` pid 2828（`[Web] Event loop captured`，唤醒监听 peak 0.678/0.666 触发）。
- 复验（全部走 `.tmp/*.log` 文本通路，无截图）：
  - `GET /api/health` → `asr online=true warm=true (small/cpu/zh)`、`llm online=true llamacpp @ :8080/v1`、`tts online=true gptsovits @ :9880/tts`。
  - WS 链路：`user` → `status 思考中…` → `tool get_time` → `tool_result 2026-11-09 18:39:49 星期一`。
  - 事件库：`18:39:40 user「现在几点了？用一句简体中文回答」(web)` → `18:39:50 assistant「现在是2026年11月9日星期一，晚上6点39分。」(web)`（10 s，简体中文 + 真实时钟）。
  - 启动时 `startup 爱莉希雅 online`(18:35:08)；18:35:14 唤醒触发 → 18:36:12 `Wake: no voice recognized`（真人录音 30 s 上限，无语音 → 空转录，属已知行为）。
- **执行通道修正（重要）**：「打开文件 - 安全警告」弹窗对 UIA `invoke` 与鼠标点击均无效（多次「Performed invoke」/「Clicked」后弹窗仍在）；**`Alt+R`（运行(R) 的助记键）才生效**。键盘注入到弹窗前必须先 `list` 取新 window_id。`Win+R` 可作为无 Explorer 时的启动入口（Run 对话框接受 `.bat` 全路径）。
- 中文路径在 `.bat` 里会被 cmd 当 GBK（`cd /d "C:\Users\楼听\..."` 失效）；一律用 `%USERPROFILE%`。PowerShell 重定向产生的 CJK 日志用 `read` 会报 invalid UTF-8 → 用 `Get-Content | Out-File -Encoding utf8` 转一层再读。

## 2026-11-09-19-45 一键启动：matplotlib 警告 + 补 llama 启动段

- 用户双击 `start_all.bat`，贴出窗口里的 `mkdir -p failed for path C:\Users\楼听\AppData\Local\matplotlib: [WinError 5] 拒绝访问` 与 Matplotlib 建议设置 `MPLCONFIGDIR` 的提示；随后 GPT-SoVITS 正常加载 Elysia 权重、`Uvicorn running on http://127.0.0.1:9880`，浏览器 `GET /`、`GET /favicon.ico` 均 404。
- **判定：这些输出全部无害**。`WinError 5` 只说明 Matplotlib 的字体缓存目录不可写，它自动退回临时目录（`GPT-SoVITS-main\matplotlib-xxxx`）继续跑；`torch.jit.script` FutureWarning 是 PyTorch 2.x 的例行提示；`_IncompatibleKeys(missing_keys=['enc_q...'], unexpected_keys=[])` 是 v2 API 模式的正常现象（推理只用 GPT 侧，`enc_q` 编码头不加载，缺权重不影响合成）；`GET /` 404 是 TTS API 只暴露 `/tts` 的正常行为。
- **真正的问题**：`start_all.bat` 没有设置 `MPLCONFIGDIR`（每次启动都要重建字体缓存，并弹出上述警告），且**不启动 llama.cpp `:8080`**；`cmd /k` 窗口一关，对应 python 进程立刻消失。19:46 实测（`.tmp\bats\chk2.log`）三端口全无监听、无 `llama-server`/`python.exe`。
- 修复（commit `324fe25`）：`start_all.bat` 顶部 `set "MPLCONFIGDIR=%~dp0.tmp\mplconfig"` + 预建目录；新增 llama.cpp `:8080` 启动段（与 `.tmp\start_services.ps1` 同款参数：`-c 65536 -ngl 99 -fa 1 --load-mode none --jinja --reasoning-format deepseek --reasoning-preserve --cache-type-k/v q4_0 --mmproj`）+ `:8080` 占用检查。现在双击一次起齐 llama / GPT-SoVITS / Jarvis。
- 观测方式延续零截图：`netstat`/`tasklist`/`curl /api/health` 全部写进 `.tmp\bats\*.log` 再用 `read` 读；`Out-File -Encoding utf8` 解决 CJK 日志。

## 2026-11-09-20-35 状态灯加「唤醒」（语音识别左侧）

- 需求（用户原话「语音识别左边再加一个 '唤醒'」）→ `records/2026-11-09-20-35-43.md` + `todo.md` 追加后开工。
- 关键障碍：`jarvis/wake.py` 的模型对象与 `_peak`/`_last_detect` 都是 `listen_for_wake_word()` 里的**函数局部变量**，健康接口读不到。解法：模块级 `state` 字典发布 `online / listening / model / threshold / score / peak / last_detect`，由唤醒线程在各阶段就地写入（模型构造后置 `online`、每块音频更新 `score/peak`、阈值穿越写 `last_detect`、`_mic_pause` 窗口置 `listening=false`）。
- `jarvis/web.py`：`_health_snapshot()` 从三灯变四灯，`wake` 排在 `asr` 前（补 `import time`，`last_detect` 用 `time.strftime` 本地化，0 值时置 `""` 以免显示假「上次触发 00:00:00」）。
- `jarvis/static/index.html`：`lamp-wake` 插在 `lamp-asr` **之前** → 灯序 `唤醒 / 语音识别 / LLM / TTS`；复用现有 `.svc-lamp`（`on` 粉 / `warm` 金 / `off` 灰），`pollHealth` keys 加 `wake`；STT 录音期间 `listening=false` → **黄灯**附「麦克风让给语音识别」，不显示为离线。
- 重启方式升级：`.tmp\bats\run28.bat` 用 `Get-NetTCPConnection -LocalPort 7860 -State Listen` 找 pid 后 `Stop-Process`，再 `Start-Process` 隐藏窗口拉起 `.venv\Scripts\python.exe -u -m jarvis.main`（比杀全部 python 精确，不伤 GPT-SoVITS）。
- 3 轮验证全 PASS（`tests/2026-11-09-20-35-43_cc/`，累积见 `tests/opinion.md`）：`/api/health` 四灯真值（`wake online=true/listening=true/threshold 0.65/last_detect 21:03:00`）、服务端 HTML 灯序与 JS 绑定（`lamp-wake` 行紧邻 `lamp-asr` 前）、进程内快照核对 `keys=["wake","asr","llm","tts"]` 与未加载态优雅退化。全程零截图。
- 小坑：`.tmp\probe.py` 直调快照时 `ModuleNotFoundError: No module named 'jarvis'`（`sys.path[0]` 是脚本目录），在 bat 里 `set "PYTHONPATH=%CD%"` 解决。

## 2026-11-09-21-19 `start_all.bat`：ASCII + CRLF + `start` 开四个 cmd 窗口

- 需求（用户原话「1. start_all.bat 应当是CR LF换行格式 ASCII编码 2. start_all应该通过start打开三个(或者更多)cmd界面」）→ `records/2026-11-09-21-19-29.md` + `todo.md` 追加后开工。
- 实测改前：`CR=56 LF=56`（**换行本来就是 CRLF**，要求 1 已满足），但 `nonASCII=250`（`rem` 框线 `─` + 中文「爱莉希雅」），这也是 `read` 直读 `start_all.bat` 报 `invalid UTF-8 text` 的原因。ASCII 化后：`len=2912 / CR=50 / LF=50 / nonASCII=0`（`starts=4`、`cmd_window_starts=3`）。
- 编码做法：ASCII 源 `.tmp\start_all_src.txt`（注释与提示全英文，框线字符换成 ASCII `----`，因为 ASCII 编码会把 `─` 变 `?`）→ `.tmp\conv.ps1` 用 `(行 -join "`r`n") + "`r`n" | Set-Content -Encoding Ascii` 生成 `start_all.bat`，并逐字节统计 `CR/LF/nonASCII` 写日志。
- 窗口写法定稿：**`start "标题" cmd /k "cd /d %~dp0... & set ... & 程序"` 单行形式**（旧的 `start "标题" cmd /k ( 多行 )` 括号复合不可靠，已废弃）。路径全用 `%~dp0`（无空格、无中文），所以 `cmd /k` 内不需要嵌套引号；4 个窗口：`llama.cpp :8080` / `GPT-SoVITS :9880` / `AiliXiya :7860` / `Jarvis Status`（第 4 窗，PowerShell 每 5 s 刷新 8080/9880/7860 监听 pid + `GET /api/health`）。
- 幂等：每段先 `netstat` 查端口，已 `LISTENING` 就打印 `[Skip] :NNNN already in use` 并跳过启动，双击两次不会堆出重复服务或多余窗口。
- 3 轮验证全 PASS（`tests/2026-11-09-21-19-29_cc/`，累积见 `tests/opinion.md`）：① 字节属性；② 双击后窗口标题实测 `GPT-SoVITS :9880 - ..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py`、`AiliXiya :7860 - .venv\Scripts\python.exe -u -m jarvis.main`、`Jarvis Status`，`:8080` 占用时仅 `[Skip]` 且未多开窗口；③ 脚本开出的窗口确实把服务拉起：`:7860` pid 4920、`:9880` pid 7028、`:8080` pid 13808 全 LISTENING，`/api/health` 四灯 `online:true`（`asr.warm=true`，`wake.last_detect=21:37:48`）。全程零截图（`netstat`/`tasklist`/`curl` + 窗口标题文本）。
- 小坑：`call start_all.bat` 后父脚本尾部输出未落盘（`exit /b 0` 与 `call` 的交互），采集数据改用独立 bat 补齐；关窗即停该服务。

## 2026-11-09-21-55 阈值 0.7 + 唤醒音内存直放 + 工具名汉化

- 需求（`records/2026-11-09-21-55-14.md`）：① 触发阈值 0.7；② 唤醒后固定应答音「直接播已有音频」，不进 TTS；③ 工具播报汉化（`type_text → 输入文本`、`press_key → 按下按钮`）。2026-11-10 16:38 起执行（隔夜后三服务全停，由 `start_all.bat` 重新拉起）。
- ① 实现：`config.yaml` `wake_word.threshold 0.65 → 0.7`（`wake.py` 与灯都读该值，无硬编码）。实测 `/api/health` `threshold=0.7`；真人唤醒 `peak 0.773` 命中，环境噪声峰值 0.25–0.62 全不触发（v0.3c 验收：0.7 → recall 0.94 / FP 0.09）。
- ② 实现：`jarvis/tts.py` 新增 `preload_ack_audio()`（启动时把 5 条 ack wav 解码成内存 float32 PCM）+ `_output_stream()`（**常驻复用同一条** `sd.OutputStream`）；`play_ack_wav()` 只写流，不再 `wave.open`、不再 `sd.play` 建流、不发 TTS 请求；`main()` 启动时调用预热。效果：建流 3125–3444 ms 移到启动阶段一次性支付，唤醒后 `ack stream ready 0 ms`，出声延迟 ≈20 ms（2.26 s 音频 total 2281 ms；真人唤醒 total 2069 ms）。
- ② 修的两个真缺陷：`sd.OutputStream(latency="small")` 在装的这版 sounddevice 抛 `TypeError: must be real number, not str`（要数值 blocksize）→ 去掉；只缓存 PCM 不够，首次唤醒仍付 3.4 s 建流 → 启动预热建流（日志 `output stream warmed in 2868 ms`）。
- ③ 实现：`jarvis/tools/router.py` 加 `TOOL_LABELS`（33 项）+ `tool_label()`；`main.py` `_tool_report()` 用中文名，`tool`/`tool_result` 广播 4 处（llamacpp + ollama 分支）新增 `label`；`index.html` 状态条/活动条/工具日志/实时流改用 `msg.label || msg.name`。实测文案 `我执行了 输入文本、按下按钮：OK enter`；真人网页触发实测事件 `["tool","get_time","看时间"]`、`["tool_result","get_time","看时间"]`。英文 `name` 保留（检索/LLM schema 不变）。
- 3 轮全 PASS（`tests/2026-11-09-21-55-14_cc/`，累积见 `tests/opinion.md`）。方法学变更：**`pwsh` 通道直接跑 git / netstat / Invoke-WebRequest / python 探针**，不再走「运行(R)+安全警告 Alt+R」弹窗；`cmd /c start_all.bat` 在 stdout 被重定向时不会退出（子窗口继承管道）。全程零截图。
- 遗留登记（未改）：真实语音轮 STT 两次 `ConnectError WinError 10054`（`.tmp\jarvis3.log:19-23`）、`asr.warm=false`、VAD 在噪声下录满 30 s 上限；`threshold` 改后必须重启 Jarvis 才刷新灯上的数值。

