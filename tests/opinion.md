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


## 2026-11-10-21-02-16 真人「爱莉希雅」录音分段 + 唤醒词重训练 + 抗干扰后训练（3 轮，验收 FAIL）

- 需求：①「有一次录制慢了30s」；② 用真人录音分割后重训练 onnx；③ 追加「将噪音和已有音频样本混合，进行抗干扰的后训练」（
ecords/2026-11-10-21-02-16.md）。
- 3 轮（零截图，脚本打分）：① 录音解码 36.12 s，ASR 词级时间戳只确认 **4 次**「爱莉希雅」（1.3–2.5、2.8–4.6、30.6–31.7、33.1–34.3，后两次繁体 愛里西亞），24 s 出现 prompt 词幻觉（该段无可识别语音），v0.3 全文件 mean 0.39 / peak 0.753 —— 噪声本身就能把分抬到 0.7；② 真人 clip（2 训练正 + 2 验收留出 + 11 真人负 + 10 静音负）走既有流式滑窗管线并入 v0.3 特征，steps 2500 训练 aili_xiya_v0.4.onnx：阈值 0.7 真人 fp 0.70→0.20（方向对），真人 recall 0.50（FAIL）；③ 噪声池按 SNR -5/0/5/10 dB 与真人/合成样本混合 164 条 + 8 条纯噪声负样本，真人行 ×5、带噪 ×2，训练 aili_xiya_v0.5.onnx：带噪 fp 0.69→0.00（抗干扰目标达成），但 recall 全面塌陷（合成 0.60、真人 0.00）=> 整体 **FAIL**。
- 结论：抗干扰后训练**有效且值得保留**（带噪 fp 归零、真人 fp 大降），失败点不在方法而在**真人正样本量**（真人正特征仅 24/120 行，呼唤本身电平弱）。config.yaml **不改**，Jarvis 继续用 aili_xiya_v0.3.onnx + threshold 0.7；v0.4/v0.5 留在 openWakeWord/output/ 作为下一轮补录后的基线。补录要求（≥20 次干净呼唤，安静+带噪各半、离麦近）已写入 
eed_user.md Q8。
- 新登记遗留：高分未标注窗口（27.0–30.2、31.7–32.7）未入库，等 Q8 确认；「无人说话录满 30 s」的代码修复（
o_speech_seconds）本批未实施，仍挂在 todo。

## 2026-11-10-22-17-39 真人录音重标（13 次全为正样本）→ aili_xiya_v0.6 重训练 + 抗干扰后训练（3 轮，部分 PASS / 按写死判据 FAIL）

- 需求：用户答复 Q8「这段录音总计 13 次, 没有噪音,平均2-3秒一次, 补录的活明天弄」（records/2026-11-10-22-17-39.md）。
- 3 轮（零截图）：① 重标——v0.3 分数局部峰检出**恰好 13** 个呼唤（0.56/3.44/7.36/9.36/12.24/15.04/18.40/20.72/23.28/26.00/29.68/31.76/34.40 s，间隔 2.0–3.9 s），全部作正样本（10 训练 + 3 留出，编号 posx_tr_1200-1209 / pos_te_1200-1202），真人特征行 24 → **1195**；同时证明「两峰间隙」不能当负样本（noise_tr_1200 的 v0.3 窗口最高分 **0.822** > 多数真呼唤），程序化低分区（平滑分 < 0.25、≥0.8 s、剔除呼唤窗）在本录音返回 **0 段** → 真人负样本 0（显式 N/A，Q9 等补录）；② 抗干扰后训练方向纠正：带噪呼唤（SNR −5/0/5/10 dB，seed 42）作**正样本**，负样本只用 v0.3 合成对抗 + 定标纯噪声（RMS 1994/1121/630/355），特征合并 25195 正 / 57696 负行，steps 2500、max_negative_weight 1 导出 aili_xiya_v0.6.onnx，训练自带 Final Model False Positives per Hour: 0.0；③ 四模型矩阵（阈值 0.7）：v0.3 真人留出 0.67 / 带噪 0.50 / 纯噪声 fp 0.25；v0.4 0.33/0.33/0.25；v0.5 0.00/0.00/0.00；**v0.6 真人留出 1.00 / 带噪 0.83 / 纯噪声 fp 0.00**，合成 rec 0.92–0.97、对抗子集 fp 0.17。
- 结论：上一批塌陷的根因是**标注错误**（8 段真呼唤被当负样本 = 教模型拒绝唤醒词），不是抗干扰方法无效；v0.6 在全部真人维度严格优于现役 v0.3，是现有最好模型。按写死判据（带噪 rec ≥0.9、合成 fp ≤0.1）仍 FAIL，故 config.yaml **未改**，Jarvis 继续用 aili_xiya_v0.3.onnx + 0.7；是否切换 v0.6 写入 need_user.md Q10 请用户决定（0.7 是唯一可用阈值，0.6 时合成 fp 0.73–0.85）。
- 新登记：真人负样本（无关中文短句）缺口未补，等明日补录（Q9：≥20 次干净呼唤 + ≥10 句无关短句 + ≥10 次带噪呼唤）；补录后重跑同一套流程，目标把带噪 recall 推到 ≥0.9 并补齐真人 fp 指标。

## 2026-11-11-19-45-46 唤醒模型切换到 aili_xiya_v0.6.onnx（3 轮：切换 PASS / 检出量部分 PASS / 0.7 阈值下环境音 FAIL）

- 需求：用户答复 need_user.md Q10 选项 1「先将模型切换到 0.6,我看看效果」（records/2026-11-11-19-45-46.md）。config.yaml wake_word.model 由 aili_xiya_v0.3.onnx 改为 aili_xiya_v0.6.onnx，threshold 保持 0.7，chunk_size 1280；带 3 个 HF 变量重启 Jarvis。
- 3 轮（零截图）：① health 实测 wake.model=aili_xiya_v0.6.onnx / threshold 0.7 / listening=true，4 灯全 online，asr.warm=true，llama :8080 与 GPT-SoVITS :9880 未受影响 → PASS；② 用线上同款部署管线（1280 chunk 逐块、检出后 reset、2 s 冷却）复放整段 36.12 s 真人录音：**v0.6 检出 10 次 vs v0.3 检出 5 次**（期望 ≥12 未达；未触发的约 20.7 s、23.3 s 是峰值压线 0.70–0.73，不是标注问题），阈值扫描 v0.6 0.75→5 次、0.8→1 次；③ 误触发面：定标纯噪声 16 s 检出 0（达标）；合成对抗 20 条 v0.6 触发 4 次（v0.3 2 次）；**现场环境音 10 s 实录（rms 1484，笔记本风扇+键盘）v0.6 触发 1 次(0.703)，v0.3 0 次**，线上日志实证启动阶段两次连触发后 No speech in 2.0s（无语音）；阈值 0.75 时环境音归零。
- 结论：切换生效，效果 = 真人检出 5→10、环境音偶发误触发。三档实测对照：v0.3+0.7 = 检出 5 / 环境音 0；**v0.6+0.7（现行）= 10 / 1**；v0.6+0.75 = 5 / 0。建议先按现行配置让用户实测 3 次唤醒，若误触发烦人则改 0.75；理想解仍是明日补录（Q9）补真人负样本，把带噪 recall 推到 ≥0.9。阈值选择与实测结果登记为 need_user.md **Q12**（status: wait）。
- 新登记：环境音（笔记本风扇+键盘，rms 1484）在 v0.6+0.7 下会偶发无语音触发；真人负样本缺口未补（Q9）。

## 2026-11-11-20-34-04 TTS 分段队列（3 轮：拆分 PASS / 队列加速 PASS / 打断 PASS）

- 需求：「将朗读内容拆分，按照标点符号拆分语句，丢给Sovits，设计一个队列管理，加速tts」（records/2026-11-11-20-34-04.md 第 1 项）。
- 改动：jarvis/tts.py 的 _split_sentences 改按中文+拉丁标点切句（2 字以下碎片并入前段，旧正则只按拉丁 .!+空白，中文整句切不出段）；新增 speak_queued + _produce_segments（bounded queue maxsize=4，producer 线程在播放段 k 时合成段 k+1，消费端按序写复用输出流）；stop_speaking 增加 flush 复用输出流（只 sd.stop 会让缓冲播完）；speak_streamed 的 gptsovits 分支改走队列，main.py 调用点不变。
- A/B 实测（6 段应答，逐段合成 2453/2570/2556/3747/2815/2908 ms，串行合计 17049 ms，音频 11.48 s）：**首声 14.08 s → 2.44 s（约 5.8 倍）**，**总时长 27.04 s → 19.56 s（约 -27%）**。打断：播放 1.2 s 后 stop_speaking → played 0.00 s、is_speaking=False、无残留播放。
- 服务侧：本批开始时 :9880/:8080/:7860 全部 DOWN（机器重启），cmd /c start_all.bat 后台任务 10 s 拉起 3 个端口，Jarvis 加载新代码（health 仍 aili_xiya_v0.6 + 0.7）。
- 结论：TTS 队列达标保留；瓶颈是 SoVITS 单请求 2.5-3.7 s，队列使合成与播放重叠，总时长 ≈ max(串行合成, 播放) + 首段。

## 第 2 项（新录音继续训练）3 轮结论（2026-11-11 20:45–21:12）

- 轮 1 PASS：7 件新 m4a 标注为 5 正 + **3 真人近音负样本**（'爱丽安娜'/'爱丽丝'/'米希雅'），切片 8 件入 openWakeWord/output/aili_xiya_v0.7/（编号延续 13xx，前缀沿用）。真人负样本缺口首次补上。
- 轮 2 FAIL：v0.7（近音负样本行重复 x5）→ 部署管线 0.7 阈值 13 次呼唤检出 **10→5**，真人近音 fp 仍 2。行重复比就是灵敏度旋钮，负样本过密 = 教模型拒绝语音。
- 轮 3 FAIL：v0.8（正 x5 / 近音负 x3，3000 步）→ 召回最高 **12**，但真人近音 fp **3/3**、合成对抗 **6**（判据 ≤4）；0.75 阈值 v0.8 = 8 检出 + fp 0 + 对抗 6，v0.6 = 5 检出 + fp 0 + 对抗 2。**没有模型在「召回 + 拒绝」两个维度同时优于 v0.6**。
- 关键发现（新，HB-029）：AudioFeatures 用 np.random 噪声初始化特征缓冲，**同一音频同一模型 3 次独立实例分数漂移 ±0.02-0.07**（ailianna max 0.753/0.730/0.732，aisli 0.681/0.713/0.671）。贴近阈值的单次测量不可信，边界样本必须多轮复测；训练日志的 Final Model False Positives per Hour: 0.0 只统计 400 条合成 val_fp，反映不出真人近音，验收必须以部署管线矩阵为准。
- 决定（Q12 规则「更好就换」）：**保持 aili_xiya_v0.6 + 阈值 0.7 不改**（v0.7/v0.8 未达标）。真人近音在 0.7 上本就是掷硬币（v0.6 也给出 0.735/0.708），要真正消除需更多真人近音 + 无关句负样本（need_user.md Q13）。

> 更正（2026-11-11 21:15）：上文「HB-029 拟记」应为 **hard_bug.md HB-032**（本文件为追加式记录，故以追加更正为准）

## 2026-11-12-10-35-29 批次（真人补录负样本 → v0.9；TTS 合成负样本实测排除）— 3 轮验证结论

3 轮一致（tests/2026-11-12-10-35-29_cc/，阈值 0.7，部署管线逐块 1280 + reset + 2 s 冷却）：

| 模型 | 13 次真人呼唤（36.12 s） | 真人近音 fp（7 件） | 真人无关短句 fp（7 件） | 合成对抗（20 条） | 定标纯噪声 | 长噪音 4 段 | 环境音 10 s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v0.9（新） | **14 / 14 / 14** | 9 / 11 / 10 | 5 / 3 / 4 | 6 / 6 / 6 | 0 | 1 | 1 |
| v0.6（现役） | 10 / 10 / 10 | 6 / 6 / 7 | 4 / 5 / 4 | 4 | 0 | 1 | 0 |
| v0.8（上一批） | 12 / 12 / 12 | 7 / 8 / 7 | 4 / 4 / 4 | 6 | 0 | 1 | 1 |

- **行重复比只移动灵敏度曲线，不产生近音判别力**：v0.7（负 ×5）检出 10→5；v0.8（正 ×5 / 负 ×3）近音 fp 3/3；v0.9（正 ×5 / 负 ×2，新增真人负样本 11 speech + 4 噪音）检出 14 但近音 fp 9-11。同一件在 v0.9 的峰值高于 v0.6（爱莉雅 0.838 vs 0.782），即「新负样本没被学成拒绝，只是把曲线整体上移」。
- 阈值扫描后采用 **v0.9 + 0.75**：检出 12、近音 fp 6、无关短句 2、合成对抗 4、长噪音 1、环境音 0 —— 两个轴同时优于现役 v0.6 + 0.7（10 / 6-7 / 4-5 / 4 / 1 / 0）。严格判据「近音 fp ≤1 且 13 次 ≥10」在 0.70/0.75/0.80 均无法同时满足，此条记为未达标。
- **TTS 合成负样本对本项目无效（实测排除）**：GPT-SoVITS 参考音频就是爱莉希雅本人音色，合成近音词在 v0.6 峰值 0.796-0.839，高于真人唤醒词整件 0.73-0.75；16 件里 7 件峰值 ≥0.7 剔除，剩 9 件低分件（0.575-0.694）排除不入库。与用户要求剔除 爱丽西亚/艾丽西亚 完全一致。
- 新发现：62.83 s 长噪音里 rms 18-47 的低分窗在 v0.6 上峰值 0.700-0.758（低响度真实噪声即可触发）；定标纯噪声（rms<15）三轮全 0。已入库 4 件噪音负样本。
- HB-032 复测规则生效：米雅希 在 v0.9 是 [0.692, 0.769, 0.73]（漂移 0.077 跨 0.7 边界），必须 3 次多数判定。并发 4 个探针会触发 MemoryError（_streaming_melspectrogram），验收必须单探针串行。

## ASR 引擎 A/B（3 轮，2026-11-12-10-35-29 第 3 轮记录；引擎开关来自 2026-11-11-20-34-04 第 4 项）

3 轮（asr_ab_r3/r4/r5.log）结果**逐条完全一致**，耗时稳定：

| 真值（文件名） | whisper sim | sherpa sim | whisper 耗时 | sherpa 耗时 |
| --- | --- | --- | --- | --- |
| 爱莉希雅，帮我打开电视机 | **0.92** | 0.78 | 3609-3702 ms | 2234-2567 ms |
| 爱莉希雅，帮我打开浏览器 | **0.92** | 0.78 | 3612-4121 ms | **154-218 ms** |
| 你好啊爱莉希雅，你在干什么呢 | **0.83** | 0.81 | 3655-3745 ms | **192-228 ms** |
| 爱丽安娜 | 0.75 | 0.75 | 2880-3278 ms | **121-144 ms** |
| 爱丽丝 | 0.33 | **1.00** | 2810-3117 ms | **123-143 ms** |
| 米希雅 | 0.67 | 0.67 | 2745-3167 ms | **134-150 ms** |

- **sim >=0.8：whisper 3/6，sherpa 2/6（三轮同）**。长句 18.30 s：whisper 8218 ms vs sherpa 418 ms，文本质量相当。
- **sherpa 无 VAD，是致命弱点**：12 条真实抓取里 7 条几乎无人声，whisper（vad_filter=True）正确返回空串（走「没听清」路径），sherpa 产生幻觉：嗯 / 有有逼 / 北京 / 你就我特我 / 小一瓶 / 啊 —— 会被当作用户指令送进 LLM 触发错误动作。
- sherpa 写不出唤醒词正字：爱丽希亚 / 泰利西亚泰利西亚（whisper 爱莉希雅）。
- **结论：stt.engine 保持 whisper，sherpa 作为网页可选项保留**（长句/低延迟场景手动切换，快 10-20 倍）。分发已实测：PUT /api/settings {"stt":{"engine":"sherpa"}} → transcribe_audio 走 sherpa 得 你能看得见屏幕吗；切回 whisper 得 你能看得见屏幕吗?（同一音频，两条路径都正确）。
- 待办（写 todo.md）：给 sherpa 路径加能量门（VAD/静音跳过），门生效后重跑 A/B 3 轮再决定默认；热词表（2026-11-11-21-36-30 第 2 项）接 sherpa 原生 hotwords + whisper initial_prompt。
- 顺带修正的 API（前两轮是失败诊断，不是引擎质量结论）：from_paraformer(paraformer=, tokens=, num_threads=)（无 paraformer_model/language_hints）；OfflineStream.accept_waveform(sample_rate, samples)（无 accept_audio）；probe 需带 HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET，否则 whisper 去联网下载报 LocalEntryNotFoundError。

## 2026-11-12-17-22-40 — 新补录 14 件真人音频可用性（3 轮，→ tests/2026-11-12-17-22-40_cc/opinion.md）

- **数据可用**：14 件无过静音（rms 0.0005-0.0371）；`14次 几乎干净的'爱莉希雅'` 在 v0.9 上检出 14/14（max 0.819）、`带键盘噪音的 4次` 4/4，6 件带轻音乐/歌声全命中 -> 真呼唤 13 -> **25 次**，带噪正样本 2 -> 12 条；need_audio.md 的干净呼唤/带噪呼唤/真人近音/安静环境音/应答语缺口**已满足**。
- **按现行规则重训不可用**：`aili_xiya_v1.0`（正 x5 / 新负 x1，26515/58128 行，3000 步）**Recall 0.3009**（v0.9 = 0.6048）-> @0.70 真呼唤合计 10（14 次件 7、键盘件 0），@0.75 真呼唤合计 3（6 件带噪全漏）= v0.4/v0.5 的同一 recall 塌陷。**未采用**，config.yaml 保持 v0.9 + 0.75。
- **根因是标签强度重叠**：入库真人负样本中 米雅 峰值 **0.827**、机械键盘噪音 0.816-0.844（3 实例稳定）与真呼唤整段峰值（0.819/0.860）同量级 -> 把与真唤醒同强度的输入标为负，模型压低整体响应；v1.0 全部新负 fp = 0 是靠灵敏度塌陷换来的。
- **新数据的正向价值已被证实**：天猫精灵（竞品唤醒词）与雅诗兰黛在 v1.0 上归零、合成对抗 6->2、长噪音 1->0 -> 这类样本能被学到，缺的是不牺牲 recall 的入库方式。规则冲突（真人件不按峰值剔除 vs 同峰值近音件训练即塌陷）已提 **need_user.md Q14** 等裁决。
- **仍缺真人数据**：竞品唤醒词真人句 >=4 条（现仅 天猫精灵 1 条）、无关中文短句 >=3 句（现 7 句，规格 >=10）。
- **HB-032 再证**：我没听清 峰值 [0.567,0.669,0.674] vs events 0.704；环境音 events 1 次（0.704）vs 3 实例 [0.688,0.633,0.676] -> 边界件必须 3 实例取多数。

## 2026-11-12 18:49-20:47 多音色 TTS 训练集批（流萤 + 白厄 + Kokoro 4 音色，3 轮，详见 tests/2026-11-12-20-03-41_cc/opinion.md）

1. **三份权重全部可用**：流萤（`Firefly-e15.ckpt` + `Firefly_e16_s1872.pth`）运行时切换实测通；白厄的 v2ProPlus 说法由**权重内容**证实（`白厄_e10_s680.pth` 首 2 字节 `b"06"` = `process_ckpt.model_version2byte["v2ProPlus"]`），唯一障碍是本机缺 v2ProPlus 所需 `GPT_SoVITS/pretrained_models/sv/pretrained_eres2netv2w24s4ep4.ckpt`（v2 不需要），从 hf-mirror 补 107,528,697 B 后通；真人音色克隆定案**不可用**（爱莉希雅权重 + 真人参考音频 → 60.26/63.28 s 失控，第 3 件 timed out）。
2. **多音色是召回轴，不是判别轴**：7 音色 × 3 条正文本 **21/21 全部入库**（检出 ≥1 且 3 实例峰值中位数 ≥0.70），部署召回合计 +1；119 件负样本仅 **13 件合格**（Kokoro 4 音色 0/17、白厄 6/17、流萤 2/17、同音色 elya 5/17）—— 近音词在**任意音色**下峰值都 ≥0.70（与真唤醒 0.82 同量级），**换音色不能产生近音判别力**。
3. **v1.1 不采用，保持 v0.9 + 阈值 0.75**：v1.1（特征 = v0.9 基线 + 15xx 合格件，正 ×5/合格负 ×1，Recall 0.6179、FP/hour 0.0）在 @0.75 下 14 次件 **12 < 14**、新正样本 20 vs 24、合成对抗 5 vs 4、近音 fp 6 vs 5；@0.70 亦无净收益（基线 12 vs 14 回落、合成对抗 8 vs 6、环境音 1 次误触发）。`config.yaml` 未改，`aili_xiya_v1.1.onnx` 留盘不部署。
4. **期望口径更正（用户）**：`环境音.m4a`（30.85 s 安静房间底噪）**没有呼唤，期望必须是 0**；`training/_t2_newaudio_probe.py` 已改。判据第 5 条统一为「定标纯噪声与环境音：检出 0」。
5. **方法学规矩**：打分必须**逐件新建 Model 实例 + `del` + `gc.collect()`**（连续流式复用实例跨件污染，正样本峰值 0.873 → 0.483 且三实例完全相同 = HB-032 播种独立性丢失；一次性 560 次构造会 `onnxruntime bad allocation`；打分前停掉 `:9880` 腾出 15.9 GB）。
6. 阻塞仍在 **need_user.md Q14（status: wait）**：真人近音件「不按峰值剔除」的规矩与「峰值与真唤醒重叠 → Recall 塌陷」的实测冲突（v1.0 0.3009 / v1.1 0.6179），裁决前不推进训练集规则，真人 `米雅` 保持仅验收集。

## 2026-11-12 21:40-21:59 Q14 裁决 + v1.0b 批（3 轮，详见 tests/2026-11-12-21-40-35_cc/opinion.md）

1. **用户直觉证实并给出结构性根因**：`米雅` 与 `爱莉希雅` 音节差别大，在**音节位置**上 v0.9 只给它 0.38-0.60（真唤醒音节位置 0.80-0.83）；**部署峰值来自说完之后的衰减/静音窗**（`米雅` 有声段内最高 0.604、峰值 0.827 落在 rms=12.8 的静音 chunk；`14次件` 峰值 0.869 落在 rms=15.6；`雅诗兰黛` 峰值在说话**前**静音）→ **模型判别面被「尾音衰减 + 静音」主导，不是音节序列**。这一条统一解释了检出延迟、近音同峰值、v1.0 Recall 0.3009 塌陷、行重复比只移动灵敏度曲线、多音色合成负样本 0/17 合格。
2. **Q14 定案（选项 1）**：真人件按文件名真值入库，**峰值 ≥0.80 的件只作验收集、不入训练集**；剔除 `雅诗兰黛` 0.822、`米雅` 0.827。`need_user.md` Q14 status: done，归档 `ai_buckup/need_user.md_2026-11-12-21-40-35.md`。
3. **v1.0b：Recall 0.6106 / FP/hour 0.0 / Accuracy 0.7208**（v1.0 是 0.3009）—— 塌陷避免；但 3 轮矩阵 @0.70 新正样本 24 vs 28、定标纯噪声 1 次误触发，@0.75 14 次件 11 < 14、基线 13 件 8 低于区间、新正 17 vs 24 → **没有任何一轴更好，不采用 v1.0b，保持 v0.9 + 0.75**（`config.yaml` 未改）。
4. **新阻塞 need_user.md Q15（status: wait）**：要利用音节差异必须改窗口约定（正样本窗锚定有声段、尾音压短；负样本剔除纯静音窗；真人近音件只在音节窗作验收集）→ 重训 v1.0c。AGENTS §0 不自行发明规则，裁决前不推进。
5. 环境事实：`av` 报 `页面文件太小` = 虚拟内存耗尽；停 `:9880/:7860/:8080` 后 Free 虚拟 13.78 GB 跑通，跑完重启并复核 4 灯。

## 2026-11-12 22:11-22:27 Q15 改窗口约定 → v1.0c 批（3 轮，详见 tests/2026-11-12-22-11-29_cc/opinion.md）

1. **Q15 落地（用户选「改窗口约定」）**：正样本窗 `[检出-0.5, 检出+1.0]` → **`[检出-0.5, 检出+0.3]`（0.8 s，既有 clip 截前 0.8 s）**；负样本剔除 24 帧窗原始 RMS < 120 的纯静音窗（**环境音 3 窗全部被剔除**）；真人近音件（米雅 0.827 / 雅诗兰黛 0.822 / 爱你老师 0.756 + 基线爱莉雅/米雅希/希雅老师）只作音节窗验收集、不入训。特征 26990/6099/58056/5028。
2. **判别轴首次达标**：@0.75 v1.0c 真人近音 fp **1 件次（判据 ≤1 首次达标）**，`米雅`/`雅诗兰黛`/`天猫精灵`/`希雅老师`/键盘噪音/长噪音全 0 检出，合成对抗 3（≤4），定标与环境音 0；音节窗分数上移（14 次件 max 0.806、基线 max 0.824）→ **模型开始在音节上打分，Q15 规则方向被证明正确**。
3. **召回轴塌到不可用 → 不采用 v1.0c，保持 v0.9 + 0.75**：@0.75 14 次件 11 < 14、基线 13 件 8（低于 11-14 区间）、带歌声 3 件全漏、新正样本 16 vs 24；Recall 0.5865（v0.9 0.6048）。`config.yaml` 未改。
4. **根因是正样本音节窗数量，不是规则**：0.8 s 音节窗只有 45 件真人 clip；`need_audio.md` 缺口未补（干净呼唤 ≥20 次、带噪呼唤 ≥10 次未达 Q9 规格，竞品唤醒词真人句仅 1 件、无关中文短句 7/10）。新阻塞 **need_user.md Q16（status: wait）**：A 补录正样本重训 v1.0d / B 用 0.70 复测 v1.0c（推荐 A+B 并行）。

## 2026-11-12 22:29-22:40 Q16 只 B：0.70 复测 v1.0c（3 轮，详见 tests/2026-11-12-22-30-00_cc/opinion.md）

1. **复测可重复**：@0.70 与上一批逐件差异仅 ±1 件次（雅诗兰黛 0→1、希雅老师 1→0、其余一致），判据结论不变 → 逐件新建实例的播种差异幅度 = ±1 件次，结论稳定。
2. **0.65 是禁区**：v1.0c 与 v0.9 的环境音（安静房间 rms=0.0005）均出现 1 次检出，违反 20:47 更正的「环境音期望必须是 0」；合成对抗 6/8、fp 6/6 同时爆表 → 阈值下限锁定 ≥0.70。
3. **最佳点 0.72**：v1.0c 14 次件 14 ✓、基线 12 ✓（区间 11-14）、定标/环境音/长噪音全 0 ✓、合成对抗 3 ✓、汇总 fp 1 ✓（判据 ≤1 达标）；未达 = 带歌声 2 漏检、键盘 4 次 3 检出、真人近音含基线 3 件次。
4. **不换现役，保持 v0.9 + 0.75**（召回轴 2 项未达 + 新正样本 22 vs 27，Q12 不成立）；v1.0c 可用区间 0.70-0.72 记录在案，onnx 留盘。
5. **瓶颈确认**：音节窗正样本数量（45 件）是召回轴的唯一短板；新阻塞 **need_user.md Q17（status: wait）**：A 补录重训 v1.0d / B 换 v1.0c+0.72 为现役（需明确批准）/ C 保持不动做别的未完项。

## 2026-11-12 22:51-23:00 Q17 裁决 C：sherpa 能量门 + 3 轮 A/B（详见 tests/2026-11-12-22-51-09_cc/opinion.md）

1. **实现**：`jarvis/stt.py` 新增 `_energy_gate`（100 ms 窗 RMS；`mode="span"` 只掐头尾静音、保留中间内容；`mode="concat"` 逐窗拼接已否决），在 sherpa 分支调用；config 键 `stt.sherpa.energy_gate`（默认 true）、`energy_mode`（默认 span）、`energy_threshold`（最终默认 **0.008**）。探针 `training/_t2_asr_ab_gate.py` 三配置对照（whisper 现役 / sherpa 无门 / sherpa 能量门），已知 6 件 + 真实抓取 12 件。
2. **逐窗拼接 = 音节切碎**：concat + THR 0.015 把已知集从 2/6 打到 **1/6**（`米希雅`→「对呀」、`爱丽丝`→「还一个」，5 件里 4 件降）；100 ms 窗会在轻声/擦音中间切。
3. **门限必须低**：span + 0.015 仍切轻声音节（`电视机`→「电脑」、`米希雅` 整件没，已知集 1/6）；span + **0.008** 复原全部已知件（**2/6**），**乱码 0 件**（无门 1、whisper 9）、**耗时 5308 ms（无门 10847 ms，减半）**，8 条 30 s 无声件从 627-868 ms 降到 26-40 ms。
4. **sherpa 天花板不在静音**：已知集 sim 停在 2/6（whisper 3/6），瓶颈是 Paraformer 对近音的声学判别（爱莉希雅→爱丽西雅/艾丽安娜/泰利西亚）→ **`stt.engine` 保持 whisper，`config.yaml` 未改**；能量门作为可用组件留用。Q7 的「sherpa 加能量门后重跑 3 轮」待办结案。

## 2026-11-12 23:08-23:42 未完项 1：「我没听清，请再说一遍」入 RAM 应答池 + hot_phrases 小表（详见 tests/2026-11-12-23-08-34_cc/opinion.md）

1. **实现**：`jarvis/data/ack/ack_no_heard.wav`（现役 :9880 预合成 3.32 s @32 kHz）；`jarvis/tts.py` 的 `preload_ack_audio` 统一采样率 + 具名缓存 `_ack_named`，新增 `play_ack_phrase(name)` 与共用 `_play_cached()`（打断/`stop_speaking` 语义不变，`play_ack_wav` 轮播不变）；`jarvis/main.py` 的 `_ask_repeat_if_unmuted()` 只在 `Transcription empty` 与 `Low-quality transcription` 两分支播该句（缓存缺句才回退 live TTS）。
2. **3 轮**：具名池 6 clip 统一 32000 Hz、`play_ack_phrase` 3330/3300/3330 ms（流就绪 0 ms），打断清队列 1219 ms 后 `is_speaking=False`；分支接线 empty/lowq 都播具名句、normal 不播；`hot_phrases(text,kind,count,first_seen,last_seen)` 写入/累加/上限 200 淘汰均正确。
3. **偏置判据不通过 → 默认关**：`HOT_BIAS=1` 时长句 ↑（0.92→0.96、0.83→0.86）但**短句被吸附到热词**（爱丽安娜 0.75→0.67、爱丽丝 0.33→0.29、米希雅 0.57→0.50，变差 3 件），且一次 61.8 s 转录失控、总耗时 23125→81531 ms；`HOT_BIAS=0` 时 B 与 A 逐件完全一致（变差 0）。`config.yaml` 加 **`stt.hot_bias: false`**，表只作数据源（统计 + `near_miss` 训练/验收导出）。
4. **探针纪律**：低质量件必须用**无 CJK 且 ≤20 字符**的退化输出（literal `You`，见 records/2026-11-08-18-54-18.md）；第一次注入「嗯」被判据当成「能理解」→ 真跑 LLM/TTS、真开 Edge、压死 :8080/:9880。探针用每次独立的临时 sqlite（第一轮在现役 `memory.db` 造 210 filler 挤掉真热词，已清理）；`record_phrase` 形参不能叫 `text`（遮蔽 sqlalchemy `text()`）。

## 2026-11-12 23:45-23:53 未完项 4：浏览器共享插件（详见 tests/2026-11-12-23-08-35_cc/opinion.md）

1. **阻塞原因不是 Chrome 调试端口，是连接器从未安装**：货架有 `[playwright]`（`none` 鉴权，另有 `chrome-devtools`/`firefox-devtools`），已配置的只有 `json-mcp-unity` 与 `custom-wow-sight`（都 `host-tools-pending`）。`mcp_connector_connect(connectorId="playwright")` **一次直连成功**，注册 **25 个工具**。
2. **3 轮全过**：① 货架/状态探测 ✓；② 连接 + `browser_navigate` 到 `http://127.0.0.1:7860/`（`Page Title: 爱莉希雅`）+ `browser_snapshot` 读到 4 灯区 / LLM 下拉框 / 🔈 / textbox / 工具·实时·快捷·设置 ✓；③ `browser_find` 不截图读到 4 盏灯 —— 唤醒 `aili_xiya_v0.9.onnx / 0.75 / peak 0.422 / 23:51:46`、语音识别 `whisper small cpu zh`、LLM `:8080`、TTS `:9880`，与 `/api/health` 一致 ✓。页面唯一 console 错误 = `favicon.ico` 404（良性）。
3. **零截图达成**：读页面走可访问性快照（`browser_snapshot`/`browser_find`），与 AGENTS「禁止大量截图」一致；若要共享**你正在用的 Chrome**（已打开的页面），才需要 Chrome 带 `--remote-debugging-port=9222` 启动 —— 必须你在 Chrome 侧配合，我不擅自拉起带调试端口的浏览器。

## 2026-11-13 00:00 小收尾：favicon + near_miss 导出（详见 tests/2026-11-12-23-58-00_cc/opinion.md）

1. **favicon**：`.tmp/gen_favicon.py`（PIL，主题色粉/丁香/金/玫瑰）→ `jarvis/static/favicon.ico`（16/32/48/64 四档，788 B）；`jarvis/web.py` 新增 `@app.get("/favicon.ico")`（`FileResponse`，缺文件 204 不抛 500）+ `index.html` 加 `<link rel="icon">`。3 轮：`curl` = **200 / 788 字节哈希一致**；浏览器 `console_messages(error)` **0 条**（上一批是 1 条 404）。
2. **near_miss 导出**：`training/_t2_hot_export.py`（入 Git，**只读**）把 `hot_phrases` 导出 `.tmp/hot_phrases_<时间戳>.csv`，列 `kind,text,count,first_seen,last_seen` 按 count 降序，`DB=`/`KIND=` 可指定库与类别。判据全过：现役库 12 行（`near_miss 1 / user 11`）、只导 near_miss 1 行；临时库 60 行（40 user + 20 near_miss）与只导 20 行顺序正确；**现役库导出后仍 12 行（未被污染）**。
3. **通路打通**：真实转录写入近音行 → 导出 CSV → 作后续重训/验收负样本（records/2026-11-11-21-36-30.md 第 3 项、Q13 真人近音来源同一）。现役库只 1 条 near_miss，需真实使用累积。

## 2026-11-13-00-12-17_cc（第 4 项：设置里可切换唤醒 ONNX，3 轮，全 PASS）

- 用户 00:12 第 4 项「将唤醒 onnx 做进设置中，允许用户选择，暂时只提供 git 中有的选项(0.3,0.9,1.0c)」→ 10:30 开工，11:05 完成 3 轮。
- **实现**：`config.yaml` `wake_word.model_options`（3 条 label/model/threshold，数据驱动）；`wake.py` `_reload` Event + `request_wake_reload()`，监听循环内重建 `Model()` 并复用 mic 流、同步 `state`，失败保留旧模型；`web.py` GET 返回 `wake_model_options`（含 `current`）、PUT 成对写 model+threshold 后触发重载；`index.html` 唤醒词组加下拉 + `pickWakeModel()` 预填推荐阈值 + 保存时成对提交。
- **3 轮**：① GET 恰好 3 项（v0.3 0.70 / v0.9 0.75 / v1.0c 0.72），`current` = v0.9，未入 Git 的版本不出现；② PUT 切 v1.0c+0.72 → health 即刻变 `aili_xiya_v1.0c.onnx`/0.72、4 灯 online、`listening=True`，日志 `[Wake] reloaded …`，新峰值 0.717/0.523 证明分数来自新模型（键名 `Path().stem` 解析正确）；③ 浏览器（零截图）选 v0.9 → 阈值预填 0.75 → 保存 toast「已重载」→ health/config 均 v0.9+0.75，**重启后仍 v0.9/0.75**，console 0 error。
- **规矩新增**：切换必须 **model + threshold 成对**（v1.0c 留 0.75 会塌召回）；预测键名用 filename stem，否则恒 0 永不触发；`browser_click` 用精确按钮文本避免 strict mode violation。
- **现役：v0.9 + 0.75，已切回。** 本地 commit，未 push。

## 2026-11-13-12-25-43_cc（20 轮第 9/10 轮暴露的 3 条工具层缺陷，修 + 3 轮，全 PASS）

- **音量虚假成功（HB-033）**：`set_volume` 不检查 returncode/输出、无条件返回成功 → 12:13:03 回复「已调至最大 (100%)」而设备 20%。三层根因：① 无证据校验；② `[MMDeviceEnumerator] -as [IMMDeviceEnumerator]` 在 PowerShell 里**返回 null**（COM coclass 不被 `-as` 激活）→ 调用链打在 null 上；③ 服务在 harness 后台任务里 python 子进程 `%TEMP%` 禁写，`Add-Type -TypeDefinition` 编译被拒。修法：C# 类内 `new MMDeviceEnumerator()` COM 激活 + **复读音量作证据**（差 ≤2 才报成功，否则带 stdout/stderr 报失败）+ 读 `eMultimedia`（role=0）+ `$env:TEMP` 指到工作区 `.tmp/pscompile`。3 轮：直调 `20→60（已复读确认）→60→20（已复读确认）→20`，服务级日志两次「已复读确认」+ 独立复测 60/20 一致。
- **屏幕读取 GBK 崩（HB-034）**：`_ocr_image` 用 `text=True`，reader 线程按 GBK 解码 OCR 输出崩在 `0x9c` → `stdout` 变 None → `'NoneType' ... strip'`。修法：PS 设 `[Console]::OutputEncoding = UTF8` + `text=False` + UTF-8 解码。3 轮：`read_screen` 返回真实 OCR 文本。诚实记录：**WinRT OCR 中文质量差**（字间插空格、有错字）→ `find_on_screen` 的按空格分词子串匹配在中文上不可靠，留下一批改匹配方式。
- **天气 ascii 崩（HB-035）**：中文地名未 URL quote + `format=` 带中文 → `'ascii' codec can't encode`。修法：`quote(location, safe="")` + `format=j1`（纯 ASCII JSON，中文在 Python 侧拼）。3 轮：`Beijing：Smoky haze，气温 11°C，湿度 50%，风速 4 km/h`。
- **规矩新增**：**工具必须自带证据**（复读/复测），证据不符就返回失败文本 —— 虚假成功比编造更危险，它让「工具失败要直说」被工具本身架空；**PowerShell 里 COM coclass 不能用 `-as` 激活**，必须 C# 类 `new`；**凡要 `Add-Type -TypeDefinition` 的工具把 `$env:TEMP` 指到工作区**；**对 PowerShell 输出不要用 `text=True`**（GBK 会崩在 reader 线程）。
- 20 轮第 11-20 轮（打断三态、近音、安静/轻敲、空转录、长句）**未跑**，需你在麦克风前配合。待修两条：`show_notification` 的 `title=None`（2026-11-08 计划①「dispatch 按 schema 强制参数类型」没落地，轮 6 复现）、`find_on_screen` 中文匹配方式。现役 **v0.9 + 0.75** 未动，音量已还原 20%。已本地 commit，未 push。

## 2026-11-13-12-59-10_cc（32 个工具全过一遍，20 轮 + 1 附加项，零截图）

- **最重要的一条：「跑了就算成功」的工具批量存在**。这一轮抓出同一族五条虚假成功：`set_volume`（音量，前批已修）、`type_text`（中文静默跳过却报成功，HB-036）、`press_key`（`not_a_key` 也报「已按下」，HB-038）、`show_notification`（UWP toast 在本机永远弹不出，`0x80073D54` 无包标识，却报「已弹出通知」，HB-037）、`set_brightness`（文案对但无原因无证据）。**规矩加强：工具必须自带证据**（复读/复测/产物字节/枚举校验），证据不符就返回失败文本。
- **本机环境边界必须写进代码，不能靠文档**：① `%TEMP%` 禁写 → `Add-Type -TypeDefinition` 的 `$env:TEMP` 指到工作区 `.tmp/pscompile`（音量、`focus_window`），`run_python` 临时脚本指到 `.tmp/pyrun`；② 桌面禁写 → `screenshot` 写工作区 `.tmp/screens`（HB-039）；③ **外网不可达**：yahoo/DuckDuckGo/Wikipedia/example.com 全超时，只有 `wttr.in` 通（天气可用）—— 判据要诚实，「工具如实报失败」不等于 PASS（轮 3 记 FAIL）。
- **中文与本地化的坑**：窗口标题是中文本地化的（`无标题 - 记事本`），`focus_window('Notepad')` 匹配不到；`pyautogui.write` 打不出中文（不可映射字符静默跳过）→ 走剪贴板粘贴且**先保存后还原**；OCR 中文插空格 → **不能拿 OCR 当写入证据**，标题 `*` 已修改标记与剪贴板才是确定性证据。
- **一处更正（我先前说错了）**：`_coerce` 早已落地（把 string 的 `None` 强制成 `""`），20 轮轮 6 的 `'NoneType' ... strip'` 真实根因是 `text=True` 的 GBK reader 线程崩（HB-034 家族），不是「dispatch 没强制参数类型」。新暴露 **HB-040**：`_coerce` 对缺失的可选参数无脑给 `""`，把工具默认值架空（`set_timer` 的中文默认文案被覆盖成空串）。
- **副作用披露（不隐瞒）**：剪贴板里的 193 字符 JWT（`sub=lt, role=admin`）在轮 9 的 `ctrl+c` 实验中被覆盖，**无法恢复**（Q18，未 commit 未落盘）；`next` 让播放器跳下一首（已授权）；`mute` 连打两次回到原状态；记事本已清场；音量/剪贴板已还原；亮度未改动（台式机 WMI Access denied，如实报失败）；**真锁屏未做**（拆到收尾，Q20）；`power_command` 只测拒绝分支，未触发任何电源操作。
- **新规矩**：**爱莉希雅不允许启动子智能体** → `delegate_task` 从 TOOL_MAP / TOOL_SCHEMAS / TOOL_LABELS 摘除（`subagent.py` 保留），实测 `dispatch` 返回「未知工具」，工具数 32/32。现役 **v0.9 + 0.75** 未动，4 灯 online。已本地 commit，未 push。

## 2026-11-13-13-46-12_cc（本机应用表 + `open_app` 先匹配 + 拼音索引，8 轮，零截图）

- **`open_app` 的三段次序写死在代码里，并且带证据**：① 先匹配 227 条本机应用表（拼音直达 → 精确（norm/别名）→ 唯一子串 → 音近打分）；② 不匹配才走其它路径（`APP_MAP`/补 `.exe`/`PATH`）；③ **复读到进程出现才算成功**，失败带原因。音近阈值写死（高置信 ≥0.66 且 gap ≥0.12 → 打开 + 登记别名；0.45-0.66 或候选接近 → **不打开、返回候选**；<0.45 → 其它路径）。`launch` 会真执行本机程序，所以**宁可不打开、多问一句**：`wei`/`cha`/`控置` 三条实测「无进程启动」（`running` 全 None）。
- **ASR 容错必须做在应用匹配层，不能靠热词救**（`stt.hot_bias` 实测有害、保持 false）。真实错词「计时本」→ 高置信命中「记事本」+ 原话登记成别名，`app_queries` 记原话，**自学习只需确认一次**，下次走精确层。「话图」→ 画图（带调拼音完全相同）。
- **同程序判据必须是 exe 文件名，不是 launch 字符串**：14:17 服务级把 `Notepad`（`C:\Windows\system32\notepad.exe`）与 `记事本`（`notepad.exe`）当「2 个候选」，让用户做了一道不存在的选择题。改后按 basename 判同 + 优先 `hits`。
- **拼音索引两个真实坑（HB-041）**：`pypinyin` 的 `errors="ignore"` **丢掉非中文字符** → 158 条纯英文名 `py` 是空串，拼音直达完全失效（修：无中文时用名字字母本身，修后空串 0 条）；「`dnSpy.exe - 快捷方式`」被索引成 `kuaijiefangshi` 与 `HaoZip` 撞车（修：算拼音前剥尾巴）。同音不同字会撞车（微星/微信 0.86）→ 候选机制必须保留。
- **第二条「描述不可发现」家族**（与 20 轮的「跑了就算成功」不同族）：`open_app` 的 description 是 32 个英文硬编码名单，没提拼音、没说传原话 → 14:30 模型对「打开jishiben」**压根不调 open_app**，只 `focus_window`/`列出窗口`；`focus_window.title` 没说标题是中文本地化 → 模型传 `notepad` 报「找不到」。改法按 agent-experience：**参数规则写在参数上、只说一次**（`name` 照原话传；`title` 用屏幕上的中文标题片段；`kill_process.name` 用英文进程名）。14:32 复测模型传原词并成功。
- **判据修正（append，不覆盖）**：① **唯一拼音前缀无歧义时打开才合理**（我 14:22 写的「前缀不打开」不对），多候选才必须不打开；② 模型会**把听到的词规范化成它认为的应用名**（「话图」→`chatgpt`、「控置」→`settings`），所以音近层主要作用于**表内名字的音近**，不是任意错词。
- **副作用**：真打开了记事本（清场）、画图（清场）、**Chrome（未关，留在你屏幕上）**；`wei`/`cha`/`控置` 未启动进程。`todo.md` 108 行已归档 `ai_buckup/todo.md_2026-11-13-14-22-30.md`。4 灯 online，现役 **v0.9 + 0.75** 未动。已本地 commit，未 push。
