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
- 3 轮（零截图，脚本打分）：① 录音解码 36.12 s，ASR 词级时间戳只确认 **4 次**「爱莉希雅」（1.3–2.5、2.8–4.6、30.6–31.7、33.1–34.3，后两次繁体 愛里西亞），24 s 出现 prompt 词幻觉（该段无可识别语音），v0.3 全文件 mean 0.39 / peak 0.753 —— 噪声本身就能把分抬到 0.7；② 真人 clip（2 训练正 + 2 验收留出 + 11 真人负 + 10 静音负）走既有流式滑窗管线并入 v0.3 特征，steps 2500 训练 ili_xiya_v0.4.onnx：阈值 0.7 真人 fp 0.70→0.20（方向对），真人 recall 0.50（FAIL）；③ 噪声池按 SNR -5/0/5/10 dB 与真人/合成样本混合 164 条 + 8 条纯噪声负样本，真人行 ×5、带噪 ×2，训练 ili_xiya_v0.5.onnx：带噪 fp 0.69→0.00（抗干扰目标达成），但 recall 全面塌陷（合成 0.60、真人 0.00）=> 整体 **FAIL**。
- 结论：抗干扰后训练**有效且值得保留**（带噪 fp 归零、真人 fp 大降），失败点不在方法而在**真人正样本量**（真人正特征仅 24/120 行，呼唤本身电平弱）。config.yaml **不改**，Jarvis 继续用 ili_xiya_v0.3.onnx + 	hreshold 0.7；v0.4/v0.5 留在 openWakeWord/output/ 作为下一轮补录后的基线。补录要求（≥20 次干净呼唤，安静+带噪各半、离麦近）已写入 
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
