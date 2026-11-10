# 测试总结论（累积）

## 2026-10-17-15-5x v0.3c 唤醒词验收（verify 第 3 轮）

- 脚本：`_t2_verify_onnx.py 400 aili_xiya_v0.3`（pwsh-7，全测试集 800 条 = 400 pos_te + 150 negadv_te + 150 negx_te + 100 noise_te + 100 预留/重复集内）
- 模型：`openWakeWord/output/aili_xiya_v0.3/aili_xiya_v0.3.onnx`（steps=3000，特征 24000+57600 行流式窗）
- 结果：pos mean/max = 0.807/0.888；neg mean/max = 0.453/0.833
  - 阈值 0.4: recall 1.00 / fp 0.57；0.5: 1.00/0.38；**0.6: 0.97/0.20；0.7: 0.94/0.09 ✅；0.8: 0.67/0.01**
- 结论：**PASS**（阈值 0.7，recall≥0.9 且 false≤0.1）。对比 v0.3（0.7: 0.87/0.05 recall 不足）、v0.3b（0.7: 0.98/0.16 fp 超标）——v0.3c 新内容+噪声同时守住两侧。
- 后续：已接入 `config.yaml wake_word.model` + threshold 0.7，Jarvis 重启生效。


# 批次结论（tests/2026-11-08-18-16-33_cc，验证 3 轮）

- UI 差异确证：**main = 旧版**（`J.A.R.V.I.S.` 标题，52,655 B / 1,174 行，Google Fonts `@import`，无粉色主题/花瓣动画/中文文案）；**Elysia 版只在 `future/AI_UI`**（`爱莉希雅` 标题，41,769 B / 829 行，`--pink`+`petal`+`backdrop-filter`，无 CDN，全中文文案）。刷新 http://127.0.0.1:7860 即可对比。
- 切分支要点：`git checkout main` 会被本地已改的 `todo.md` 阻断（两分支内容不同），先 commit 再 checkout；重启 `:7860` 需 `Stop-Process` 掉旧 python（`job_kill` 只杀 pwsh 外层）。
- 风险提醒：main 上**没有** 17:53 的 500 修复与 llm.py 补丁，真人测试聊到 8 条触发压缩时会重现「保存设置后管线报错」。建议看 UI 后切回 `future/AI_UI` 再做语音真人测试。
- 三服务不受分支影响：llama `:8080`（gitignore 的 `llm/`）、GPT-SoVITS `:9880`（job pwsh-10）、jarvis `:7860`（main 代码，job pwsh-21）。

### 合并保留（future/AI_UI 侧未包含于 HEAD 的行，append-only 不删历史）
# 批次结论（tests/2026-11-08-14-12-32_cc，验证 3 轮）
- 3 轮全 PASS：JS 语法 + 端点契约、页面加载 + 无外部资源、WS 事件渲染路径（node 桩驱动）。
- 接口契约零改动：JS 端点与 `jarvis/web.py` 路由逐字一致；`web.py`/`main.py` 未修改。
- 主题落地：HUD 青蓝色 → 爱莉希雅樱粉/淡紫/暖金 + 深紫玻璃拟态；中文化 UI 文案；删除 Google Fonts `@import`（离线可用）；樱花飘落 + `prefers-reduced-motion` 降级。
- 局限（真实缺口，不虚报）：本机无可用浏览器（`playwright-online-search` 报缺 `chrome-headless-shell-1243` 可执行文件；`npm exec playwright install chromium` 未能完成）、`web_fetch` 无外网 → **在线风格检索未能真实执行**，配色取自任务内给定的爱莉希雅色板；**未做真实浏览器目视验收**。
- 建议：用户启动 Jarvis（`:7860`）后浏览器验收外观；若要真实浏览器验证，需先安装 Playwright chromium（约 150 MB，需外网）。
# 批次结论（tests/2026-11-08-15-16-18_cc，验证 3 轮）
- skill 已恢复可用：bing PASS、baidu PASS（均 exit 0 + 结构化结果）；duckduckgo 为本机网络不可达（exit 5 正确上报），补充 bing 轮 PASS。
- 根因与修复：`channel:'msedge'` 依赖 `ProgramFiles`/`ProgramFiles(x86)` 环境变量，run_code 子进程 env 为空 → 路径拼成 `undefined\...` → 误判「无浏览器」(exit 3)。修复：`repairEnv()` 补 5 个变量 + 新增显式 Edge `executablePath`（x86/x64）回退，再落到 bundled chromium。Edge 实测版本 143.0.3650.139。
- Playwright 自带 chromium（195.6 MiB，`chrome-win64` + `chrome-headless-shell`）正在后台下载（`cdn.playwright.dev`，进度慢；`ms-playwright` 目前仍只有 `.links`/`__dirlock`）。装好后将增加第三层可用浏览器；当前 skill 靠系统 Edge 已可用。
- 影响：T6 的在线风格检索当时未真实执行；现在可执行（用 bing/baidu）。
## 追加（2026-11-08-17:12，chromium 装成后的 3 轮）
- 轮4：C: 清理后 ENOSPC 消失，但 `npx playwright install` 两次（前台 540 s / 后台 job pwsh-3）都在 40% 被 `ECONNRESET` 打断，官方安装器在此网络跑不完 114.6 MiB。
- 轮5：`curl -C -` 断点续传把 zip 拉满（120,200,717 B，exit 0），`Expand-Archive` 解到 `F:\playwright-browsers\chromium_headless_shell-1243`，`chrome-headless-shell.exe`（212 MB）就位；探针 launch + bing 浏览 OK（版本 153.0.8010.12）。
- 轮6：三层回退全链验证 exit 0（msedge 通道 / 空 env 兜底 / 强制 bundled chromium），bundled 轮拿到真实玻璃拟态 CSS 参考站点。
- 结论：**在线搜索 skill 完全恢复**：可用浏览器 = 系统 Edge 143.0.3650.139 + 自装 Chromium Headless Shell 153.0.8010.12（F: 盘）。duckduckgo 仍因本机网络不可达（exit 5 正确上报）。
# 批次结论（tests/2026-11-08-17-29-39_cc，验证 3 轮）
- 三服务全部在线：`:8080` llama-server（Qwen3.5-2B-Q4_K_M，pid 20684/16252）、`:9880` GPT-SoVITS api_v2（pid 4436）、`:7860` jarvis.main（pid 12880）。真人测试入口：http://127.0.0.1:7860 。
- 轮1 LLM PASS（裸调必须带 `chat_template_kwargs.enable_thinking=false`，jarvis 已带）；轮2 TTS PASS（200 + 314 KB RIFF wav）；轮3 Web UI/WS 全链 PASS（6 事件 + 事件落库）。
- 已知短板：2B 模型对「爱莉希雅」身份识别不稳；STT 的 cuda 因驱动版本不足回落 CPU（可用，速度较慢）；GPT-SoVITS 启动时 `MPLCONFIGDIR` 默认路径不可写（仅警告）。
- 副作用提醒：`type_text` 等工具会真实操作 PC（打字），真人测试前建议先测静音/中止（UI 的「中止」按钮 / `type:'interrupt'`）。
# 批次结论（tests/2026-11-08-17-53-00_cc，验证 3 轮）
- 根因：**不是设置页保存本身**，而是保存后继续多轮对话使 `context` 窗口达到 `summarize_after=8` → `context.py:49` 把 `[Earlier context: …]` 作为第二条 system 消息 → Qwen3.5 chat template 第 85 行 `raise_exception('System message must be at the beginning')` → 8080 返回 500；jarvis 回落 Ollama（未运行）→ 用户看到「连接不上 Ollama」，真因被掩盖。三组探针（A 正常 / B 第二条 system 500 / C 首位非 system 500）确证。
- 修复（commit fix(AI)）：`main.py::_process_request` 把前导 system 摘要并入唯一 system 消息，并让主 provider 失败时在 `status` 事件与事件库写出**主错误**；`jarvis/llm.py` 的 openai 分支补 `chat_template_kwargs.enable_thinking`（否则 content 全空）并把 `timeout` 15→90（子代理/摘要此前被 15 s 掐断后回落 Ollama）。
- 3 轮验证：轮1 根因确证；轮2 连续 5 轮对话（窗口达 8 触发压缩）5 条 response 全出、无 500；轮3 重启后 UI 200/42,420 B、API 200、TTS 200/266 KB RIFF、WS 对话正常。
- 运维提醒：重启 jarvis 必须 `Stop-Process` 掉旧的 python（job kill 只杀 pwsh 外层，`job_kill` 后旧实例仍占 :7860，导致新实例 `10048 端口已占用` 退出）。


# 批次结论（tests/2026-11-08-18-39-40_cc，验证 3 轮）

- `future/AI_UI` → `main` 合并完成（merge commit `99aeaf1`，**本地合并、未 push**）。Elysia UI、500 修复、`llm.py` 补丁、skill/三服务/config 台账与全部 records/tests 批次现在都在 main 上。
- 冲突处理原则：5 处冲突全部**保留两侧内容**（append-only：`records/`、`tests/`、`tests/opinion.md`、`todo.md`、`progress.md`），`tree.md` 用合并后的 `git ls-files` 重建；代码文件由 git 自动合入 AI_UI 侧，`git diff --stat future/AI_UI -- <code>` 为空（完全一致）。
- 3 轮：轮1 一致性 + `py_compile` 全 0；轮2 main 上 UI 已是 Elysia 版（200/42,420 B、`爱莉希雅`、`--pink`/`petal`、无 CDN、无 `J.A.R.V.I.S.`）；轮3 连续 5 轮对话跨窗口 8 触发压缩，5 条 response 全出无 500（第 5 条是真实摘要），TTS 200/258,604 B RIFF。
- 合并坑（同切分支）：`git merge` 会被**未提交的 todo.md 改动阻断**（`error: Your local changes ... would be overwritten by merge`）→ 先 commit 本需求 record+todo 再合并；重启 `:7860` 仍需 `Stop-Process` 掉旧 python。
- 当前服务：llama `:8080`、GPT-SoVITS `:9880`（job pwsh-10，pid 4436）、**jarvis `:7860` = job pwsh-23（合并后的 main 代码）**。真人测试可直接在 main 上做：UI 是 Elysia 版且含 500 修复。


# 批次结论（tests/2026-11-08-18-54-18_cc，验证 3 轮）

- 真人语音「变成 You + Done.」有两个独立成因：**① `stt.py` 把 `language="en"` 写死**（中文口语被英文解码，短语音只能拼出 `You` 这类碎片；事件库 `user "You" source=voice` 是铁证）；**② `main.py` 342-343 行在模型工具轮后返回空 content 时字面兜底 `"Done."`**。同一段合成中文音频：en → `'I love you, Alicia. Yes. Tomorrow is the 3rd day of the meeting…'`，zh → `'爱利西亚 对 明天下午三点开会 记得带笔记本和钥匙'`，None → 同 zh（detected zh 0.967）。
- 修复（`fix(AI)`）：`stt.py` 语言取 `config.yaml` 的 `stt.language`（新增 `language: zh`，缺省 zh，两处 transcribe 同步）；`main.py` 加 `_looks_understandable()` 空/碎片守卫（无 CJK 且 ≤20 字符 → 播「我没听清，请再说一遍。」，不调 LLM）；`_call_openai_provider` 记录 `executed` 并用 `_tool_report()` 兜底（无工具 → 「我处理好了。」；有工具 → 「我执行了 …：结果首行」），`Done.`/`OK`/`已完成` 视为空。3 轮全 PASS，WS 回复裸 Done. 计数 0。
- 真人测试提示：2B 模型会把「记一下」理解成 `type_text` 往记事本打字 + `focus_window`（找不到「记事本」窗口）→ **语音测试会在桌面真实打字**；先按「中止」（WS `{"type":"interrupt"}` / UI 中止 / Esc）。「爱莉希雅」仍常听成「爱利西亚」（2B 身份识别遗留）。
- 当前 jarvis = **job pwsh-30**（含全部修复）；llama `:8080`、GPT-SoVITS `:9880`（job pwsh-10，pid 4436）未重启。C 盘已由用户清理。


# 批次结论（tests/2026-11-08-19-25-48_cc，验证 3 轮）

- 「语音无法触发」的直接原因是 **阈值**：设置页保存的 `wake_word.threshold: 0.75` 高于真实环境峰值（真人 1.5 分钟 peak 最高 0.570），而干净合成音频 PEAK 0.862 —— 模型没问题，是门槛太高。已改 **0.65** 并重启，真人连续触发（162/166/168/173 行 wake，peak 0.716/0.689/0.734）。
- 顺带修掉两个观测/逻辑缺口：① `wake.py` 原来没有任何分数日志，「叫不应」与「麦克风坏了」无法区分 → 新增 3 s 节流 `[Wake] peak X / threshold Y`；② `_abort` 残留把下一轮录音砍成 0.3 s（`record_until_silence` 每 chunk 查 abort，而 `clear()` 只在录音之后的 `_process_request`）→ `_on_wake` 录音前显式 `_abort.clear()`，复测完整链路（Speech detected rms=0.0432 → 转写 → 回复）。
- 当前 jarvis = **job pwsh-38**（阈值 0.65 + 分数日志 + abort 清零 + 上一批 STT 语言/转录守卫/_tool_report）；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。要更灵敏就设 0.60，别再回 0.75。


# 批次结论（tests/2026-11-08-19-52-59_cc，验证 3 轮）

- 「能唤醒但总答『我没听清』」的根因是**录音被自己的 barge-in 打断**：IDLE 冷却只有 2 s（挡不住她的 ack『在。』+ 用户紧接着说话），busy 分支的 `is_recording()` 在录音窗口前 0.15 s 仍是 False，于是 `abort_all()`；而 `record_until_silence` 每个 chunk 都查 abort flag → 第一 chunk（0.3 s）就 break。修法：`handle_wake` 入口置 `_stt_recording = True`（finally 清零）、冷却 5 s、abort 检查加 1.5 s 宽限；再加 `[ABORT] set by … thread=…` / `[Wake] barge-in score=… recording=…` 让这类问题可现场判定。
- 真人反馈「回答是天气」另修：新增 `get_time` 工具（`jarvis/tools/system.py` + `router.py` TOOL_MAP/schema + 系统提示规则），实测 `dispatch` 返回 `2026-11-08 20:09:20 星期日`，语音问时间得到 `现在是 2026年 11月 8 日 20 点 10 分，星期日。`。
- 真人测试注意：2B 会把「说一句话/记一下」理解成 `type_text` 往桌面打字；「爱莉希雅」常听成「爱利西亚」；whisper 偶发繁体输出；1.5 s 后的 barge-in 仍会截断长句子。当前 jarvis = **job pwsh-50**（阈值 0.65 + 分数日志 + 1.5s 宽限 + 5s 冷却 + STT zh + 转录守卫 + `_tool_report` + get_time）；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。


# 批次结论（tests/2026-11-08-20-22-00_cc，验证 3 轮）

- 「网页端要刷新才显示」不是广播坏了：真实页面 2 s 内就能看到 `user/tool/tool_result/response` 气泡。真正的 bug 是前端 `case 'status'` 只匹配英文字面量（`Thinking...`/`Listening...`…），后端发的是中文（`思考中…`/`正在聆听…`/`在。`/`已停止。`/`主模型失败：…`）→ 状态灯、活动条、状态文字一直停在 `待命`，观感就是「页面不动，刷新才有新内容」。修法是同时匹配中文+英文，并在 `onopen` 加 20 s 心跳 + 每次（重）连重拉历史，`onclose` 清理心跳。
- 断线恢复实测：主动 `ws.close()` → `离线` → 3 s 后自动 `已上线`（重连 + `loadHistory()`），不需要刷新。
- 测试手法可复用：Playwright `channel: msedge` + `addInitScript` 包裹 `window.WebSocket` 记录消息时序（reload 会清页面注入）；改 `index.html` 不需重启 jarvis（FastAPI 从磁盘读）。当前 jarvis = **job pwsh-50**；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。真人测试会往事件库写 user/assistant 行。

# 批次结论（tests/2026-11-09-15-37-58_cc，验证 3 轮）

- 3 轮全 PASS：① 协议层（`/api/health` 三项在线、WS connected/stop 应答、页面标记含新芯片与 `svcLamps`/`pollHealth`）；② 真实 Chrome 渲染（页头顺序 `待命中/已离线/聆听中/说话中/执行中/思考中` + `语音识别/LLM/TTS` 三盏灯 + 状态文字，事件条目已出现在页面）；③ `stop` 去重与「当下真实回答」（两次 1.2 s 的 stop 只各一条应答、无重复系统气泡；17:17/17:19 问时间得到**简体**中文 + **真实时钟** 17:17/17:19，应答 2 s）。
- 需求 1（幻觉）：`Tool 'xxx' failed: 'NoneType' object has no attribute 'strip'` 属 11-08 历史事件，`router.py::_coerce`（904dbc8）已把 `None` 参数强转；繁体回答与「问时间答天气」本轮实测未复现。遗留为 2B 模型措辞啰嗦（`星期一是星期一`）。
- 双浏览器根因确认：我驱动 Playwright/Edge、用户用 Chrome，两套实例互不可见 → 共用浏览器方案评估：Playwright MCP `--cdp-endpoint`（回环附着用户 Chrome）**通过**、Chrome DevTools MCP **通过**、Browser MCP（云端 relay）**拒绝**；装/配需用户明确授权（见 `records/2026-11-09-15-37-58.md` 追加节与 `progress.md` 规则）。
- 观测配额首次落地执行：以 UIA 语义树 + `.tmp/*.log` 文本为主，仅 3 张小区域截图用于定位与目视验收；新执行通道（`.bat` + 资源管理器「运行(R)」+ 日志重定向）已写入 progress.md。
- 服务：llama `:8080`(pid 16876)、GPT-SoVITS `:9880`(pid 18284)、jarvis `:7860`(pid 1924) 由本会话重启并验证；真人语音测试会继续往事件库写行。

# 批次结论（tests/2026-11-09-20-35-43_cc，验证 3 轮）

- 需求：状态灯在「语音识别」左侧加「唤醒」（`records/2026-11-09-20-35-43.md`）。
- 3 轮全 PASS：① `GET /api/health` 四灯真值（`wake online=true / listening=true / model aili_xiya_v0.3.onnx / threshold 0.65 / last_detect 21:03:00`，`asr.warm` 已为 `true`，`llm/tts` 保持在线）；② 服务端返回 HTML 中 `lamp-wake` 行紧邻 `lamp-asr` **之前**，`lamps` 绑定 4 盏、`pollHealth` keys 为 `['wake','asr','llm','tts']`、让出麦克风时黄灯；③ 进程内直调 `_health_snapshot()` 核对 `keys=["wake","asr","llm","tts"]` 与未加载态优雅退化（`online=false`、`last_detect=""`、不抛异常）。
- 方法学：全程零截图，`curl` + `Select-String` + `.tmp/*.log`（UTF-8 转码后读）；重启走 `.tmp\bats\run28.bat`（`Get-NetTCPConnection -LocalPort 7860` 定位 pid 后杀，再 `Start-Process` 隐藏窗口拉起），执行通道沿用 15-37 批次定稿的「运行(R)」+ 安全警告 Alt+R 放行。
- 结论：唤醒灯数据源与 UI 两侧闭合，在线 / 离线 / 让麦克风三态语义明确；`asr/llm/tts` 零回归。遗留：`threshold` 改后需重启 Jarvis 才刷新 `state`；灯为 5 s 轮询、`peak` 为 3 s 日志窗峰值。

# 批次结论（tests/2026-11-09-21-19-29_cc，验证 3 轮）

- 需求：`start_all.bat` 必须 CRLF + ASCII，且用 `start` 打开三个（或更多）cmd 界面（`records/2026-11-09-21-19-29.md`）。
- 3 轮全 PASS：① 字节统计改后 `len=2912 / CR=50 / LF=50 / nonASCII=0`，改前 `nonASCII=250`（框线 `─` + 中文），换行本来就是 CRLF；`starts=4`、`cmd_window_starts=3`；② 双击后窗口标题实测 `GPT-SoVITS :9880 - ..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py`、`AiliXiya :7860 - .venv\Scripts\python.exe -u -m jarvis.main`、`Jarvis Status`（第 4 窗），`:8080` 已占用时只打印 `[Skip]` 且不多开窗口（幂等）；③ 脚本开出的窗口确实把服务拉起：`:7860` pid 4920、`:9880` pid 7028、`:8080` pid 13808 全 LISTENING，`/api/health` 四灯 `online:true`（`asr.warm=true`，`wake.last_detect=21:37:48`）。
- 方法学定稿：`start "标题" cmd /k "cd /d %~dp0... & set ... & 程序"` 单行形式（旧的 `cmd /k ( 多行 )` 括号复合废弃）；路径全用 `%~dp0`（无空格无中文）故 `cmd /k` 内不需嵌套引号；ASCII 化用 `Set-Content -Encoding Ascii` + 显式 `\r\n`，注释与提示一律英文。全程零截图（`netstat`/`tasklist`/`curl` + 窗口标题文本）。
- 结论：编码与窗口两条要求闭合，四窗口 = llama :8080 / GPT-SoVITS :9880 / Jarvis :7860 / Status 面板；关窗即停对应服务。遗留：`call start_all.bat` 后父脚本尾部输出未落盘（`exit /b 0` 交互，不影响双击），第 4 个状态窗口不需要时可自行关闭。

# 批次结论（tests/2026-11-09-21-55-14_cc，验证 3 轮）

- 需求：① 唤醒触发阈值改 0.7；② 唤醒后固定应答音「直接播放已有音频」不再进 TTS；③ 工具执行播报汉化（`type_text → 输入文本`、`press_key → 按下按钮`）（`records/2026-11-09-21-55-14.md`）。
- 3 轮全 PASS：① 重启后 `/api/health` 的 `wake.threshold=0.7`（`h6.log`/`h7.log`），真人实测 `peak 0.773 ≥ 0.7` 成功触发、环境峰值 0.25–0.62 均不触发（`.tmp\jarvis3.log` 的 `[Wake] peak` 行）；② 热路径改为「内存 PCM + 常驻输出流」，`ack stream ready 0 ms`、2.26 s 音频总 2281 ms（`ack3.log`），真人唤醒实测 `stream ready 0 ms / total 2069 ms`（`.tmp\jarvis3.log:7-10`），首字出声延迟由 ~3.4 s 级降到 ~20 ms 级，全程无 HTTP 合成请求；③ `TOOL_LABELS` 33/33 无遗漏，`_tool_report` 文案为 `我执行了 输入文本、按下按钮：…`（`tool1.log`），真人经网页端触发后 WS 事件带中文 `label`：`["tool","get_time","看时间"]`、`["tool_result","get_time","看时间"]`（`ws1.log`）。
- 方法学新增：`pwsh` 通道可直接跑 `git`/`netstat`/`Invoke-WebRequest`/python 探针（比「运行(R)+安全警告 Alt+R」弹窗便宜得多）；`cmd /c start_all.bat` 在 stdout 被重定向的管道里不会退出（子窗口继承管道），故脚本执行仍走双击/Run 弹窗语义；探针输出需 `PYTHONIOENCODING=utf-8` + `Out-File -Encoding utf8` 才能被 `read` 读。全程零截图。
- 结论：三项要求都是「零新增网络调用、零新增推理」的实现路径；英文工具名保留在协议与事件里（检索/LLM schema 不变），中文只用于播报与 UI。本轮修掉两个真缺陷（`latency="small"` 抛 `TypeError`；首次唤醒仍付 3.4 s 建流成本 → 启动预热建流）。遗留登记：真实语音轮 STT 两次 `ConnectError WinError 10054`、`asr.warm=false`、VAD 录满 30 s 上限，属 STT/VAD 老问题，需另开需求。

# 批次结论（tests/2026-11-10-17-31-10_cc，验证 3 轮）

- 需求：查清「ASR 不能转写」是否 ASR 有问题（`records/2026-11-10-17-31-10.md`）。
- 3 轮全 PASS：① 带 `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET` 重启后启动日志 `[STT] Loaded small on cpu` + `whisper warmed in 2866 ms`，`asr.warm=true`（`.tmp\jarvis5.log:6-8`、`h8.log`）；② 真人语音轮 VAD 正常收尾（`Speech detected rms=0.0222` → `Silence detected` → `Recorded 7.5s`）并转写出文本、`press_key`/`get_time` 执行正常（`.tmp\jarvis5.log:16-25`）；③ WS 链路与中文 `label` 无回归（`ws2.log`）。
- **定性结论：ASR 代码无缺陷。** 根因是重启通道丢了 HF 环境变量：whisper-small 快照在仓库内 `.hf-cache`（实测存在），默认用户缓存里没有，缺 `HF_HOME` 时 faster-whisper 去 huggingface.co 找快照被连接重置（`ConnectError 10054`）→ 加载失败 → 转写为空；`start_all.bat` 本就设了这三个变量，属我的操作失误。改动仅两处：运维约定（重启必带三变量，写入 progress 执行通道）+ `main.py` 新增 `_warm_stt()` 后台预加载，使 `warm` 启动即 true、加载失败在启动日志立刻暴露。
- 顺带发现并登记：`config.yaml` 的 `device: cuda` 在本机不可用（`CUDA driver version is insufficient`，既有逻辑自动回 CPU，建议改配置为 `cpu`）；2B 模型把 11-10 答成「星期五」（`tool_result` 是 `星期二`）、转写/回答出现繁体 —— LLM 侧遗留，需另开需求。

# 批次结论（tests/2026-11-10-17-43-08_cc，验证 3 轮）

- 需求：① 汉化「还是不够全」（工具**返回值文案**）；② 真人语音「你能看得见屏幕吗？」被识别成「你能看的就」，要求优化或更换 ASR 方案（`records/2026-11-10-17-43-08.md`）。
- 3 轮全 PASS（②为部分 PASS）：① `lab2.log` 12 条工具结果逐条中文（`已输入文本：`、`已按下：`、`已用左键点击 (x, y)`、`已滚动：向下 3 格`、`未知媒体操作：…`、`工具「读取文件」执行失败：路径不在允许清单内：…`），并当场修掉 `get_system_info` 乱码（`text=True` 用系统代码页解码 PowerShell 输出，新增 `_ps_utf8()` 强制 UTF-8，`lab3.log` 复测正常）；② 录音落盘 `.tmp\capture_<ts>.wav` 成功，可离线复现，合成语音 A/B **3/3 全对**（旧参数繁体 `你能看得見屏幕嗎`/`調到20` → 新参数逐字正确带标点），真人 1 句在 6 种参数组合下均为 `你看得见吗?`（丢「能」「屏幕」），2x 增益无效；③ `ws3.log` 中文 label 与中文结果、`name` 仍英文、四灯在线（`asr warm=true, device cpu`）。
- 结论：汉化覆盖「用户听到的文案」（`tools/*.py` 返回值共 44 处 + `router.py` 2 处），协议层（`TOOL_SCHEMAS` 名称/参数、WS `name`、事件 `tool` 行、`TOOL_LABELS` key）刻意保持英文；顺带修掉 `main.py` 重试判定失效（原判定 `Tool '…'`，改为 `执行失败：`）。ASR 参数级优化（beam 10 + 简体中文 `initial_prompt` + `vad_filter` + 去头部静音）能消除繁体与标点缺失，但真人短句的丢字无法用参数/增益解决，瓶颈是 whisper small 对中文短句的鲁棒性；换引擎（sherpa-onnx paraformer-zh）需用户授权，已写入 `need_user.md` Q7，未擅自安装。
- 新登记遗留：18:03 的 `peak 0.736/0.799` 在 0.7 阈值下误触发后录满 30 s、转写为空（`record_until_silence` 缺「无人说话快速退出」）；真人录音 rms 仅 0.010（建议调高麦克风增益）；`stt.device` 已按实测改为 `cpu`。

