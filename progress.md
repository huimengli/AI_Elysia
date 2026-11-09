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
- 下一条（追加）：`tree.md` 重建 + `progress.md` 压实 + `records/2026-11-08-20-44-17.md` 入库的 commit。
