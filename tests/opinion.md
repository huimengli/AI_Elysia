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
- 三服务全部在线：`:8080` llama-server（Qwen3.5-2B-Q4_K_M，pid 20684/16252）、`:9880` GPT-SoVITS api_v2（pid 4436）、`:7860` jarvis.main（pid 12880）。真人测试入口：http://127.0.0.1:7860。
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

- 需求：①「有一次录制慢了30s」；② 用真人录音分割后重训练 onnx；③ 追加「将噪音和已有音频样本混合，进行抗干扰的后训练」（records/2026-11-10-21-02-16.md）。
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
## 2026-11-21 15:33 · tests/2026-11-21-15-11-57_v13（真人 20 轮离线表在 v1.3 重跑）

- 同一把尺复刻 11-19 的 v09b 表（46 件、1 轮 1 实例、chunk 1280、0.75、越线后 reset），20 轮跑满：真人 **14-15**、近音 3、无关 0、旧 12 段 3、**新 9 段 4**。

## 2026-11-21 16:40 Monitor 验证 3 轮（tests/2026-11-21-15-37-53_monitor/）
- 轮 1 PASS 5/5；轮 2 部分 PASS（1 s 节拍未达，实测 4.26-4.66 s/拍，根因单拍采样耗时）；轮 3 PASS 4/4 + 外部起追加段 PASS。
- 授权面测到了：外部 pid 关闭被拒、自起 pid 真杀（taskkill 真实输出落日志）、外部服务端口未被杀。
- 自曝 12 处（累计第 100-111），最贵的是 ctypes 查监听 pid 连踩 4 次（107-111），最后改用 `netstat -ano`，与 netstat 真值对上一致。
- 5 项未测（真机节拍、隐藏页省电、前端渲染、关窗全关 5 s 时限、/monitor 窗口不最大化 + 窗口数口径）。

## 2026-11-21 18:15（追加，批次 2026-11-21-15-37-53_monitor）
- 真会话截图证明「页 200/标题命中」不等于能用：JS 因转义语法错整段不执行，页面永停在初始态。以后凡有前端，验证轮必须真开浏览器读 console 与渲染。- 定位语法错的可行路：把脚本塞进新 `<script>` 让解析器报行号列号；`new Function` 只给「Invalid or unexpected token」，逐行前缀扫描因截断必然报错（不可用）。- 真机节拍中位 1.9 s（设 1 s）；逐段计时定位瓶颈为窗口计数 1688 ms，缓存后稳态 50→0 ms。优化要计时坐实，不靠直觉。
## 2026-11-21 18:38（追加，批次 2026-11-21-18-27-30_tabs）
- 分页标签三页共用一份顶栏（CSS+JS 各一文件），当前页高亮由 pathname 决定；新页只引两行，避免三份漂移。3 轮真浏览器全 PASS（URL/高亮/内容/console）。- 重犯「测量假象」：计数器挂在推送开始之后，读到 0 拍（第 129 处）。证据应以页面实际更新为准。第 130 处：往不存在的目录写文件（ENOENT）。
## 2026-11-21 19:07（追加，批次 2026-11-21-18-59-49_chrome_tabs）
- 分页标签：标签全中文（主界面/监视界面/相关页面）+ 仿 Chrome 外观（深色条、圆角凸起、当前页亮底）。3 轮真浏览器全 PASS；点击切换的根因是服务端跑旧代码（`/static/tabs.js` 404、顶栏不存在），要重启 jarvis。- 证据口径纠正：`status 0` 不能当 404（resource-timing 不暴露状态）；用 `fetch` 取真状态码。第 131-133 处自曝记。
## 2026-11-22 11:06（追加，批次 2026-11-22-11-04-00_real_session）
- 真会话验收落盘：顶栏/真切换/1 s 节拍（中位 1.0，尖峰 2.7 = TTL）/隐藏页降 30/日志折叠/关闭按钮 confirm 全过；「关窗全关」只算结果达标（自起 pid 消失、端口全消），`SHUT_LOG` 不存在 → 逐条落盘未证实。- 连续三轮「计数器挂在数据之后/挂在旧 socket」读到 0 拍（第 161-163 处）。量节拍的证据应以页面渲染出的数据 + 挂到当前 socket 的监听器为准。
## 2026-11-22 11:20（追加，重启后复测）
- 重启后顶栏/真切换/console 无 error 全部复现，节拍与处理取证（累计 18 拍、无发送失败、无异常、窗口=1）。- 第 165 处自曝记：探针在 `CONNECTING` 时 send 触发 `InvalidStateError`，让 15 s 窗口读成 0 拍——量 WS 节拍必须等 `readyState=1` 再发，且以页面渲染数据为准。

## 2026-11-22-11-48-11_six_items（验证 3 轮，Monitor 六条）

- **PASS**：第 1 条样式照 home（真窗口截图「监视界面 — 爱莉希雅」为证）、第 2 条 cmd 窗口 120 s 后只剩「爱莉希雅已经启动 http://127.0.0.1:7860」（截图 .tmp/jarvis_console6.png）、第 4 条可上下滚动（scrollTop 0→300，内容高 1275 > 视口 774）、第 5 条前端截断（灌 500 行 → 面板 200，首行最新）、第 6 条最大帧间隔 19 ms（修复前拖死到 CDP 20000 ms 超时），真点切换 252 ms / 71 ms。
- **未测**：第 3 条真链路总用时（我不能说话）；第 5 条真链路累积 200 行（需 ~400 s 连续跑）。
- **未证实**：SHUT_LOG 逐条落盘（加 try 防护后未复测）、只杀自起 pid 的正面路径。
- **结论（可复用规矩）**：① 前端每拍只赋值一次，禁每行「pre.textContent = 新行 + 旧文本」；② `FileResponse` 必须带 no-store，且 jarvis 自开页带 ?ts=（同 URL 的 CDP 导航在 Chrome 里不重新取页）；③ `open_url` 复用判定要地址完全一致，子串互含会复用不导航；④ 分流 print 后必须复 grep 残余 print=0（第 187 处我用了改前号，漏 [Wake] peak / [TTS] warmed）。
- **自曝**：本轮 169–189 共 21 处（4 次重犯行索引/缩进坑、2 次把算出的行号当已写入、1 次在模板字符串里写反引号把程序弄坏、1 次造假 payload 形状不合法）。

- **补记（2026-11-22-13:23）**：第 5 条真链路累积 200 行 **未测 → PASS**（300 s 连续跑，面板 200 行、最新在上、最旧被截；`jarvis.log` 到 1835 行全量落盘）。记第 192 处自曝：一次瞬时读数 203 行 > 上限，与复验的 200 冲突，**未证实**，不猜结论。第 2 条「报错要在 cmd 看见」**未测**（本轮未构造真报错场景）。


## 2026-11-22-13-48-06 · 第 16 轮 5 条（monitor 4 灯、日志两态、滚动条、about 照 home、ws 实时推送）

- `tests/2026-11-22-13-48-06_five_items/` 3 轮全 **PASS**：第 1 轮真窗口截图 + 真滚轮（面板 `scrollTop` 随滚轮走、`follow` 切换、查看态 20 s 内 flush 计数与末行不变 = 冻结、滚到底新行落底部、三面板时间序倒置 0、200 行上限）+ console 0；第 2 轮 about 照 home（`:root` 变量、三层 radial + linear、2 px 粉条、16 px 圆角玻璃卡、code 金色）computed + 真截图；第 3 轮量得无客户端基线 6.296875 s CPU/60 s、有客户端 6.625 s/60 s → 增量 0.328 s ≈ 0.55% 单核，逐行延迟 0.5/0.9/均 0.7 s，21 chunk/21 行 → 保留实时推送。
- 记自曝 193–221（本轮段）：`trim()` 与带空格字符串比较恒 `-1` 把行插到文件最前/换掉文件末尾（193/194）；数行错吞相邻 `payload`、插进无 `snap` 的循环、用删前的索引 off-by-one、缩进 16 空格（199–202）；`screenshot_id: null`（204）、参数名写成 `deltaY`（205）、拿无滚动余量的面板测（206）、复用已消耗的 `screenshot_id`（208）；坐实 100 ms 通道与 1 s 拍共用游标到达序无保证（209，页上加时间戳稳定排序后倒置归 0）；`sortByTime` 插两次 + `findIndex` 命中同款 forEach 删掉新块留旧块（210–212）；自己程序引号写坏未跑（213）；坐标算出截图外（214）；沿用已 `clearInterval` 的旧计数误判冻结失效（217，218 插桩证明冻结生效）；往未建目录写 `ENOENT`（219）；报告了未生效的 about 样式（220，第 176 处同类续犯，搬进 `<head>` 后复量才生效）；猜文件名 `home.html`（221，真文件是 `index.html`）。规矩补：锚点两边都 `trim()`、插入后必复读 + 复编译 + 复 grep 残余、桌面动作后必取新截图、页样式改动必须在真页面 computed 复量。
- 未测写：第 2 条「报错要在 cmd 看见」未构造真报错场景；真链路总用时需你在麦克风前（我不能说话）；`SHUT_LOG` 逐条落盘 + 只杀自起 pid 正面路径加防护后未复测。

## 2026-11-22-15-45-55 · 第 17 轮 3 条（滚动条照 home、About 五块内容写入 design、录音法录异常触发）

- `tests/2026-11-22-15-45-55_three_items/` 3 轮全 **PASS**：第 1 轮三面板滚动条实测宽 8 px、thumb `linear-gradient(rgb(248,169,196), rgb(126,63,102))`（home 的 `--pink`→`--rose`）、圆角 8 px、track 透明、旧口径声明残余 0、真页截图照出粉色 thumb、console 0；第 2 轮 about 5 块（a 模型与语音 / b 此电脑 / c 项目地址 / d 介绍 / e 工具介绍）真页全在 + 16 关键字全命中 + 读数全部现采（物理 8 核 / 逻辑 16 核、23.8 GB、AMD Radeon 780M 4095 MB、Win10 10.0.19045、Python 3.12.0、`origin https://github.com/huimengli/AI_Elysia` 只读不 push、`http://127.0.0.1:7860`、`TOOL_MAP` 44 个真注册名）+ console 0；第 3 轮照你定的 10 秒录音法跑通（真麦 10 s 段、逐件 3 实例、5 s 冷却、阈值 0.75 不动），20 段 **保存 7 件 / 丢弃 13 段**、3 实例全越线 **5 段**（峰 0.760/0.768/0.767/0.794/0.777），jarvis 真触发 8 次（15:44-18:08，越线峰 0.751-0.822，触发后转录空/aborted）→ 打字声与手机播放小说能让 v1.3 越线（与 HB-051 定性一致，阈值与引擎未动）。
- 记自曝 222–238（本轮段）：design.md 升 v3.6 第一次写入全没落上（改动只赋给内存数组、写盘用原始字符串，复 grep 才照出）；`join` 写成 Python 语法；`stream_callback=None` 被 pyaudio 拒（照抄 `wake.py` 的 `input=True`）；未 trim 的单行锚点找两行写法 → `indexOf` = -1（老坑第 4 次）；替换判据行写 4 空格（真行 8 空格）→ `IndentationError`（缩进坑第 5 次）；`savePath` 越出 downloadDir 被拒；机器读数采错（`NumberOfProcessors`=1 是 socket 数、GPU 取到虚拟驱动）；about 页无溢出测得滚动条宽 0，不谎称「滚动条可见」；TS 字符串里写反斜杠路径把转义写坏两次；TS 属性名含括号（`r.检出(3实例)`）解析失败；照 stdout 尾部截断把「保存 7 件」报成 5 件（从 json 全量核后追加更正段）。规矩补：写盘后必复 grep、锚点两边 trim、缩进取邻行、路径用正斜杠、计数从落盘 json 核不从 stdout 尾巴看。下一条从 239 起。
- 未测写：越线 7 件离线只跑 1 遍（3 实例，未做 3 轮）；这些件是否让 jarvis 真触发需你在麦克风前复现（我不能说话）；第 1 条「报错要在 cmd 看见」与真链路总用时仍未测（上一轮延续）。


## 批次结论（tests/2026-11-22-19-22-36_log_wrap，2026-11-22-21-08 追加）

- 第 19 轮「log 面板不要左右滚动，直接自动换行」3 轮全 PASS（21:03–21:08 真页量出，console 0）。详见 `tests/2026-11-22-19-22-36_log_wrap/opinion.md`。
- 顺带复验 HB-055（环形日志满后增量冻结）：**修法成立** —— 追平后的老客户端持续收到 `logchunk`（9 s 3 条 / 12 s 4 条 / 15 s 4 条），页上尾行随真实时间推进（21:07:35 → 21:07:47）。
- 同时坐实 19:22 那次「3 轮已跑」是**没跑过的**（目录当时不存在）；本批次是第一份真验收。自曝 249 记在 `progress.md`。

- 追加第 4 轮（22:08，commit `6472f53` 后复开）：PASS。9 s 内 `monitor` 7 条 + `logchunk` 83 条、3 面板、真读数、console 0；jarvis 环已满（20:27 起 ~100 min）仍持续收增量 → HB-055 修法在环满下成立。我第一遍读到 `panels = 0` 是**在首条 payload 到达前读 DOM**，自曝 253。

## 2026-11-23-11-59-00_hb053_gate（2026-11-23-12-45，3 轮全 PASS）
- 归属闸 fail-closed 在真 dispatch 下成立：非自起窗口 focus_window 拒绝执行（Program Manager pid 9172）、kill_recorded_pid(9172) 拒绝关闭、用户页在 targets() 里枚举不到。
- 空串在 dispatch 层 7 项全拒（focus_window / find_on_page / click_page_text / find_on_screen / web_search / set_clipboard / show_notification），窗口集合差 [] []、剪贴板逐字相同 True、FG 前后同一 hwnd 262758。
- 正面路径三条真证据：open_url 记录 pid 7320、focus_window 放行并真聚焦、click_page_text 真点且面板状态真翻转（最新追加 → 查看）。
- 自曝 256：我把 dispatch('evaluate') 当工具用，返回「未知工具：evaluate」，正面路径的状态复读靠补测 browser_cdp.evaluate 才成立。

## 2026-11-23-12-46 · 事故与恢复（追加，HB-056）
- 我在 12:44 用「读全文 + 追加」写 tests/opinion.md 后，git diff 显示相对 HEAD 少 48 行（10 个分节）。恢复 = HEAD 版逐字 + 今天两节，取自 git show HEAD:tests/opinion.md，不手写补内容。
- 12:44 我读到的磁盘版只有 268 行（HEAD 317）；根因见本文件第 13-11 追加段与 hard_bug.md HB-056 追记：**tools.read 只返回前 268 行**（文件 281 行，totalLines 报 280），「读全文+覆盖」等于把尾巴覆盖掉。

## 2026-11-23-11-59-00 P0-2 第 2 轮（真在线环抽干 + 真客户端增量，2026-11-23-13:03）
- 抽干 jarvis 环 41 拍 / 791 行：游标每拍递增、无重复、时间戳非递减、抽干后同游标 0 行 —— 全 PASS。
- 真页 60 s：追平标签收到 30 条新行（≥18 PASS），查看标签 pre 末段逐字冻结在 12:20:58 且缓存仍收到 30 条（收得到不渲染）。
- 页面末 12 条与抽干序列 12/12 逐字命中（格式是「时间,正文」，我第一版用空格连，全判不命中，是我格式错）。
- 自曝 258：两次假 FAIL —— 拿 jarvis.log（stdout）当环的对照基准（两条流不是一回事）、拿「Starting up」当基准（[Apps] 在它前面）、用 logbuf 长度测增长（200 已封顶）。

## 2026-11-22-21-35-00_lamps_shot（P2-4 灯体真窗口截图 3 轮全 PASS，2026-11-23-13:11）
- 真窗口（computer_windows 的 window_id + 整窗口截图 1470×1040）里四灯色 wake/asr 绿、llama/tts 红，与 GET /api/monitor 的 lamps online 四条逐一对上；页里灯标签逐字 = API 灯名。
- 同一时刻三处计数一致：API jarvis_windows=1 / manage_browser_windows「1 个（上限 3，你的窗口不计）」/ 页自报「我起窗口 1/3」；窗口消失后三处一致 0 且「没有可关的对象」。
- 关窗正面证据在 P1-3 第 3 轮（kill_recorded_pid 7320/2968 → SUCCESS；非自起 pid 9172 → 拒绝关闭）。
- 挂案（不改代码）：--no-sandbox 横幅（Q45）、Chrome「未正确关闭」恢复横幅、jarvis profile 窗口起后约 1–2 分钟消失。
- 自曝 259：P1-3 与 P2-4 我都是跑完才补 todo.md 项，违反先落盘再开工；另一次把 evaluate 返回的 'null' 差点当页面自报读数。

## 2026-11-22-21-35-00_ring_full（P0-2 环满游标 3 轮全 PASS，2026-11-23-14:09 收尾）
- 环满真活体：latest 2061 > RING 2000；since=0 游标 = base+19（62+19=81）；中环 since=1061 的 20 行与抽干序列逐字连续、游标 = since+20；monitor 环尾部 5 条「游标落后 2038/2059/2061 行 > 环 2000（jarvis），跳过中间行」——HB-055 的跳段路径第一次拿到真活体证据。
- 环满后追平页 60 s 收 40 条（≥18），页末 12 条与抽干序列 12/12 逐字；查看标签 pre 冻结、缓存照收（第 3 轮）。
- 自曝链 254–262 全在记录里：基准用错流/取错行、用封顶长度测增长、把 len(cursor) 当行游标、把 2 分钟抽干序列当静态基准、页缓冲数组 vs 渲染串。

## 2026-11-22-21-35-00_crossing20（P2-3 越线 7 件补到 20 轮，2026-11-23-14:25）
- **20 轮全 PASS**（每轮 7 件打分跑满、逐件 3 实例峰值 + 5 s/2 s 两条口径检出数报全；前置照口径停 :7860，:8080/:9880 未起；阈值 0.75、模型 aili_xiya_v1.3.onnx 未动）。
- 20 轮分布（每件 60 实例峰值）：seg_181956_4 与 seg_182312_20 **60/60 越线、全越线轮 20/20**（硬证据）；seg_182134_12 49/60、seg_182122_11 42/60、seg_182033_7 35/60（概率性，峰 min 0.693–0.721 max 0.828–0.838）；seg_182159_14 **4/60**、seg_182211_15 **10/60**（很少越线）。
- **每轮 7 件全越线的轮数 2/20（轮 3、7）** —— 第 17 轮「1 遍全越线」的说法被这 20 轮降回抽样级别，照实改口。
- 局限照写：离线同一把尺只回答「模型在这段音频上怎么打分」，不等于 jarvis 真触发（真触发要你在麦克风前复现）。*.wav 不入库。

## 2026-11-22-21-35-00_deploy3（部署侧 3 轮补「记未达」，2026-11-23-14:55）
- 现役 `aili_xiya_v1.3.onnx @0.75`、`wake.py` 同构管线、逐件 3 实例（HB-032），三服务全停，不接麦克风。落 `tests/2026-11-22-21-35-00_deploy3/record_1..3.md + opinion.md`。
- 长噪 62.83 s 与 环境音 30.85 s：3 轮全 **0 检出**（峰 0.595–0.695）——期望达标。
- 机械键盘噪音 16.53 s：期望 0，**3 轮里 2 轮出现 1 个实例越线**（峰 0.788、0.815；第 18 轮 3 实例 0.67–0.739 未越线）。照实记 FAIL，不美化。对照 11-12 基线 v1.0c「4 次 3 检出」：**v1.3 更干净，但没到 0**。
- 13 次真人呼唤：期望 13，5 s 冷却 `[5,5,5]/[5,6,6]/[6,5,6]`、2 s GAP 稳定 `[9,9,9]`、峰 0.834–0.873 —— **13 在这套冷却口径下数学上不可达**，记部分达成。
- 与今天 P2-3 的 20 轮分布同源：单实例越线是播种随机性撞上 0.75 边，不是模型突变。真机是否真触发仍未测（需你，Q48①）。

## 2026-11-23-15-42-47_voice3（真机 3 轮，20 轮未达 3/20，2026-11-23-15:47）
- 你 15:42 的话落 P2-5（阈值余量）与 P2-5b（四条判据逐轮判）。三服务全在（jarvis `:7860`、llama 18176、GSV 6304）。真轮 3 轮，20 轮未达 —— 剩下要你在麦克风前。
- **灵敏度余量薄（0.72 坐实）**：越线 `0.791/0.779/0.751/0.771/0.765/0.778/0.79`；未越线 `0.748/0.734/0.730/0.729/0.721/0.708/0.704/0.703` —— 0.70–0.748 一带密集。
- **吃尾复现 2 次 + 新根因逐字**：`[Duck] CDP 连不上（没有我起的窗口带 --remote-debugging-port）` → 播歌窗口不可暂停 → 播歌期间的录音必被中止标志截（15:36:25 `capture 1 s` 转录空；15:36:49 `capture 1 s` 转录只剩「播放」）。15:31 那轮录音 5.1 s 完整，问题在转录。
- **转录质量是主害、热词偏置=关**：`[You] 播放到箱。`（`表 38 行，偏置=关`）→ 关键词「箱」播了「青之箱」，不是你要的歌；`web_search 搜索「花海 歌曲 播放」` → 之后「花海」播周杰伦花海（若你说花海则判据③中）。`first sound 14309 ms`、`llm_secs 114.41 s`、`total_secs 184.73 s / 76.8 s`。
- **播不播未证实**（要你的耳朵）。程序面：`TTS played 30.10 s`、`play_music n=2 fail=0`、`jarvis_windows=0`、重复播放保护 ×2。

## 2026-11-23-15-42-47_voice3 追加（7 轮真轮，20 轮未达 7/20，2026-11-23-15:59）
- 你 15:59 的两条落 `records/2026-11-23-15-59-43.md` + todo P2-6/P2-7。判据④（播不播）由你耳朵确认「播放了」→ **记 PASS**。
- 关窗后错误链逐字四份：`[Duck] CDP 连不上（没有我起的窗口带 --remote-debugging-port）`（15:52:22/15:52:44/15:54:46/15:56:57）+ `music_control 恢复失败`（15:37:02）+ `read_page 读不到页面文本`（15:37:11）；`jarvis_windows=0`。你关窗 = 她的身份与 CDP 端口一起消失，暂停/恢复/读页面/播完关窗三条能力失明。
- 吃尾真机共 **5 次**（15:36:25、15:36:49、15:52:25、15:52:49、15:54:50、15:57:00 —— 逐字同形 `Recording aborted → capture 1 s → Recorded 1.5s`）。
- 「没能成功打开浏览器」的真相：**复述历史当执行**。15:57:10 她声称执行了 7 类工具（关窗/github/b站/百度/播歌/music_control/百度），而 E 块计数一个没涨（play_music 2 / web_search 1 / music_control 1 / type_text 1 / read_page 1，与 15:37 逐字相同）→ 没有真调用，浏览器不会打开；口头声称 = 虚假成功。
- 唯一性副作用：22:05「只允许 1 个播歌窗口」的证据是第一次播歌；窗口被你关掉、计数变 0，「已播过」的记忆仍在 → 既不播也不开。窗口没了证据应失效，这条口径要在 P2 重定。
- 唤醒面是好的（F 块 15 次越线 0.75–0.793）；截录音 + 复述历史两环每轮都坏。20 轮未达 7/20。

## 追加（2026-11-23-16:27）· 三条闸门 20 轮明确测试 20/20 PASS
- 三条改法落在 jarvis/main.py（38 增 0 删）：P2-7a 歌名闸门（len(kw)<2 / 动词助词表 / 无字 → 拒，如实问歌名，不调 B 站 API）；P2-6a CDP 失明恢复路径（music_control/read_page/find_page_text 结果含「连不上」→ 追加「调试端口随那个实例一起消失，先让我用 play_music 重新起播歌窗口；不碰任何页面，不假装控制成功」）；P2-7b 执行声明绑定真调用（_EXECUTED 在 svc.tool_stat 处 +1、闸门早退不计，_process_request 开头清零；声明命中而计数为 0 → 回复改「这一句我没有调用任何工具……我不拿历史当执行」+ [诚实] log）。
- 20 轮走真函数 _exec_tool_with_retry / _process_request；桩的是 dispatch（起窗口/联网/CDP 连不上原句）与 _call_llm 文本，以及 memory/context/event_log 写入。闸门与计数不桩。20/20 PASS。
- 照实记两条边界：第 6 轮半句尾巴双字「到箱」放行（闸门只拦单字/动词/助词/无字）——15:31 播「青之箱」的同族仍在；第 7 轮「《稻香》」放行但未 strip 书名号，真调 B 站大概率空结果。两条未修，等你点头才动 app_control 的关键词处理。
- 20 轮没有真起播歌窗口、没有真语音、没有真 B 站请求。四条判据（含「关键词与你说的一致」「播不播」）在真机 3 轮验。自曝 267：子进程没带 USERPROFILE → Path.home() 在 tts.py:34 炸 Could not determine home directory。
