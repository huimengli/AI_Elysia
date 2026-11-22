<!-- 已归档于 ai_buckup/progress.md_2026-11-22-13-12-00.md（155 行 > 100，抽取最近 72 行；旧内容全在备份里） -->
<!-- 归档动作记录：2026-11-22 13:12，见 records/2026-11-22-11-48-11.md 第「归档照实」段 -->

- 2026-11-21 16:40 **Monitor 验证 3 轮跑完**：轮 1 PASS 5/5（含外部 pid 关闭被拒）、轮 2 **部分 PASS**（协议全对，1 s 节拍未达：实测 4.26-4.66 s/拍、首拍 14.87 s，根因单拍采样耗时）、轮 3 PASS 4/4 + 外部起追加段 PASS（pid 与 `netstat` 真值一致，外部服务没被杀）。5 项未测照实（真机节拍、隐藏页省电、前端渲染、关窗全关 5 s 时限、`/monitor` 窗口不最大化 + 窗口数口径）。
- 本批自曝 **第 98-111 共 14 处**，最贵的是 ctypes 查监听 pid 连踩 4 次（结构字段顺序、bOwner、把返回码 122 当失败、行距 24 且 IPv4 表不含通配/IPv6 行），最后改用 `netstat -ano`；另有 四灯没进 `/api/monitor`、`_mon_interval` 少 `global`、`windll.psapi` 查不到 `K32GetProcessMemoryInfo`、`ws.onclose = ws.onclose` 自赋值、驱动没设超时 16 分钟不出结果、JS 写出 null 字节。
- 2026-11-21 16:44 **Monitor 验证批收尾 commit f7c444d**（`git rev-list --count HEAD` = 276）。第 112 处自曝：我先写了 `commit -F .tmp/commit_msg18.txt` 却没建这个文件，commit 没发生（当时 hash/count 都停在 0439033 / 275），补写消息文件才提交上。
- 2026-11-21 16:38 **tree.md 照实重建并 commit（8644b3e，705 文件 / 65 目录）**；随后 progress 补 hash 的 commit **3836875**（`rev-list --count` = 278）。`git status` 只剩照旧不 commit 的 3 个根目录垃圾。本条的 hash（3836875 的后续 commit）照规则只能在下一批补记。
- 2026-11-21 18:23 **真会话截图打穿 Monitor 前端**：页面是空壳，根因 = JS 转义（`class=\"ext"` 少闭合转义）→ 整段 script 语法错。修 2 处 + 排版（标签/下拉重叠）+ 推送「一阵就停」（`send_text` 异常就 pop，改为仅真断开才摘）+ 前端 10 s 心跳重注册。
  复测（共用浏览器真页）：无语法错、`ws.readyState 1`、真数据渲染全对（`jarvis 起 pid 8440/1516`、提交 MB 1060/3、`log_lines 13/19`、四灯全 online、我起窗口 1/3、F 块 `wake 0.75 · ASR 0.03 s`、日志 2 面板）→ `C:\Users\楼听\Downloads\monitor_after.png`。
  真机节拍（设 1 s，29 拍）：中位 1.9 s / 均值 1.8 s / 最小 1.4 / 最大 2.0；逐段计时坐实瓶颈是窗口计数 1688 ms（不是 netstat 67 ms）；加缓存后稳态 50→0 ms。1 s 节拍达标 **未测**（要重启 jarvis 生效）。
  **本批自曝第 113-127 处（15 处）**：113 `dsh_browser_state` 传空参被拒；114 探针写多语句被当表达式拒；115 逐行前缀扫描对截断必然报错（方法无效）；116 `new Function` 只给「Invalid or unexpected token」，靠塞进 `<script>` 才拿到行号列号；117 用字符串拼接躲转义把 TS 解析器炸了；118 快照实测 1998 ms；119 推送「一阵就停」根因（pop 过早）；120 我的计数挂在旧 socket 上读到 0 拍（假象），逐段计时才定准瓶颈；121 探针在 `try` 里直返，TTL 缓存写不进去；122 删死代码时把 `def listen_pids` 一起带走（`NameError`）；123 凭记忆写锚点没命中（`命中 1/0`）；124 netstat TTL 1 s 在 1 s 节拍全 miss；125 `all(p in cache)` 让缓存形同虚设；126 窗口计数每拍 1688 ms 才是真瓶颈。
- 2026-11-21 18:24 **Monitor 前端与节拍修复 commit 4e40a24**（`feature/AI_monitor`，`rev-list --count` = 280）；本条的 hash 照规则在下一批补记。未 push。
- 2026-11-21 18:40 **分页标签（主界面 / monitor / about）开工并验证 3 轮全 PASS**：三页共用一份顶栏（`tabs.css`+`tabs.js`，当前页高亮由 `location.pathname` 决定），新页 `about.html` + 新路由 `@app.get("/about")`，`web.py` 新增 `app.mount("/static", StaticFiles(...))`；design v3.1 → **v3.2**（先归档 `ai_buckup/design.md_2026-11-21-18-27-30.md`），§6 补第 10 条「必须真开浏览器看渲染与 console」。
  3 轮证据照实：轮 1 `顶栏第1子节点=true`+三标签+主界面高亮+padding 38px+console 无 error（主界面排版未压坏）；轮 2 `URL=/monitor`+高亮跟着+资源条填上（提交 25815·已用 22559·可用 3255·物理 54%·CPU 3.5%）+服务行 3；轮 3 `URL=/about`+表 5/6/8 行+未测条 3+`tokens/s 未埋`在场+回切 `URL=/` 高亮回主界面。截图 `C:\Users\楼听\Downloads\tabs_index.png`、`tabs_about.png`。
  **本批自曝第 128-130 处**：128 凭 grep 摘要拼长锚点，头部替换命中 0（改成按行索引替换才成）；129 重犯第 120 处——计数器挂在推送开始之后，读到 0 拍是假象；130 往不存在的目录写文件（ENOENT）。
- 2026-11-21 18:41 **分页标签 commit ac65d39**（`feature/AI_monitor`，`rev-list --count` = 282，tree.md 715 文件同步重建）。本条 hash 照规则下一批补记。未 push。
- 2026-11-21 18:42 **need_user Q45 commit a2c9d15**（count 284）；本条 hash 照规则下一批补记。未 push。
- 2026-11-21 19:08 **分页标签三条修改（全中文 + 仿 Chrome）并验证 3 轮全 PASS**：第 1 条「点击无法切换」根因照实坐实——你的 jarvis 跑旧代码，`fetch("/static/tabs.js")` 真状态码 **404**、顶栏不存在（`body` 第 1 子节点无 `.dsh-tabs`），不是顶栏代码坏（沙箱 7861 新代码 3 次点击 URL/高亮都跟着走）。
  标签改全中文「主界面 / 监视界面 / 相关页面」（路由 `/` `/monitor` `/about` 不变），`about.html` 的 title/h1 也全中文；外观仿 Chrome：条 36 px 底 `rgb(21,15,31)`，标签圆角 `11px 11px 0 0`、高 30 px、非当前页底 `rgb(36,26,49)`、当前页粉渐变 + 深色字、8 px 圆点。design v3.2 → **v3.3**（先归档 `ai_buckup/design.md_2026-11-21-18-59-49.md`）。
  **本批自曝第 131-133 处**：131 我把 network 的 `status 0` 当 404 证据（不成立，resource-timing 不暴露状态），改 `fetch` 取真状态码；132 正则塞进探针字符串把 TS 解析器炸了；133 `args` 通道没注入（`arguments[0]` undefined），改用字面量。另照实记：改静态页后浏览器给缓存旧页，**刷新后复测**才算数。
- 2026-11-21 19:09 **仿 Chrome 标签页批 commit 47ffef0**（`feature/AI_monitor`，count 286，tree.md 721 文件同步重建）。本条 hash 照规则下一批补记。未 push。

## 2026-11-22 11:14 会话追加（jarvis 真会话验收 + 根因修复）

- **真会话 0 推送根因**：`services.py` `listen_pids` 缓存命中分支写死 `_net_cache["d"][p]`，端口没在听（TTS 未起/重启窗口期）每拍抛 `KeyError(9880)`（**自曝第 147 处**）。修：命中分支只返回缓存里存在的端口。
- **自曝第 154 处**：把「启动 + 轮询」塞进一个 pwsh 调用，超时被提升为后台作业（返回 `kind:"promoted"`，没有 `stdout`）→ `Cannot read properties of undefined (reading "text")`。我一开始误判成语法炸，照实更正根因。
- **自曝第 149-151 处**：pwsh 直连 `ClientWebSocket` 探测连错三轮——类型名打错（`[Th=CancellationToken]`）、`SendAsync` 少参数、传整数组绑不上（要 `ArraySegment[byte]`）；修后 16 条里 15 条是 M（中位 1.0 s）。
- **自曝第 153 处**：用 `snap["lamps"]` 当锚点插入，它在循环里也存在 → 带进 12 空格缩进，`py_compile FAIL`。读现场修缩进后 OK。
- **自曝第 157-159 处**：为做逐客户端隔离写了占位伪代码（`and_false`）炸 TS 解析器；随后在 `batch = []` 前插 `try:` 却没有配套 `except`（必语法炸），而且 `as e2` 落到了**第一个** `except Exception:`（`_broadcast_to_ws` 里，无关函数）。按行索引整块重写后 `py_compile OK`。教训照实：改代码块要用行索引整块替换，不能用「看起来唯一」的锚点。
- **自曝第 158 处（真 bug）**：`web.py` 发送失败的 `except Exception:` 没有 `as e`，行内 `repr(e)` 用的是外层已被 Python 回收的 `e` → 发送失败时 `NameError`。改成 `except Exception as e2` + 落环。
- **自曝第 160-163 处**：真会话量节拍连读 0 拍全是我的假象——标签页被会话重置成 `about:blank`、计数器挂在数据到达之后、挂在重连前的旧 socket。挂 `addEventListener` 到**当前** `ws` 后 32 s 计 27 拍、累计 49 拍，中位 1.0 s。教训照实记进测试批次的 opinion。
- 顺带加取证口（照实命名，不发明）：`GET /api/monitor_logs` 只读取日志环、`snap["clients"]` + `snap["client_info"]`（逐客户端 iv/cursor/socket id）、每 10 拍记「处理客户端」一条、发送失败落环。
- **真会话验收 3 轮 PASS/部分 PASS**：顶栏全中文+真切换+console 无 error、1 s 节拍（中位 1.0/均值 1.1/最大 2.7 = TTL 重扫）、隐藏页降 30（隐藏 40 s 0 拍）、日志折叠 `none`↔`block`、关闭按钮 confirm 取消不杀进程；「关窗全关」端口全消、自起 pid 15276/9608 消失，`SHUT_LOG` 不存在 → **逐条落盘未证实**。
- 落盘：`records/2026-11-22-11-06-00.md`、`todo.md` 勾条、`tests/2026-11-22-11-04-00_real_session/record_1..3.md + opinion.md`、`tests/opinion.md` 追加。

- 2026-11-22-11-16-00 `81a0f6e` fix(monitor): 修 Monitor 推送链根因并落盘真会话验收（自曝 147、149-163；已本地 commit，未 push）
- 2026-11-22-11-17-00 `a105727` docs(progress): 追加 81a0f6e 提交记录与自曝段（已本地 commit，未 push）
- **自曝第 164 处**：我引用了**还没写**的 `.tmp/commit_msg31.txt` 去 `commit -F` → `could not read log file`。规矩照实：消息文件必须先写再提交。
- **自曝第 165 处**：真会话探针在 `CONNECTING` 时 `ws.send` → `InvalidStateError`，让 15 s 窗口读成 0 拍。量 WS 节拍要等 `readyState=1` 再发 config，并以页面渲染出的数据为证据。
- 重启后复测照实：`标签=主界面/监视界面/相关页面 ｜ 高亮=主界面 ｜ 条高=36 ｜ 底=rgb(21,15,31)`、点击三条 URL 真变（`/about` title 全中文）、console(含error) 0、累计 18 拍、发送失败 0、异常 0、窗口=1。
- 2026-11-22-11-21-00 `d41f726` docs(tests): 追加重启后健康复测与自曝 164-165（已本地 commit，未 push）

## 2026-11-22-13-12 · Monitor 六条改造（你 11:48 逐字六条）

- **落盘先于开工（照实补记）**：`records/2026-11-22-11-48-11.md` + `todo.md` 第 95 行先行；`design.md` v3.3 → 归档 `ai_buckup/design.md_2026-11-22-11-48-11.md` → **v3.4**（§2 G/F 块、§3 样式与滚动、§5 cmd 窗口口径、§6 第 11–14 条、§7 缓存与复用判定）。
- **第 1 条（样式照 home）**：`monitor.html` 的 `<style>` 整块照 `index.html`（同一套 CSS 变量、多层径向渐变、PingFang SC/Microsoft YaHei、玻璃卡 blur + 圆角 16 px + `--shadow`、粉色顶条），标题「监视界面 — 爱莉希雅」。真窗口截图为证。
- **第 2 条（爱莉希雅日志 + cmd 窗口只留三样）**：`services.py` 加 `jlog`（环 + `.tmp/jarvis.log`，不刷控制台）与 `jerr`（环 + stderr），`web.py` 日志循环加 `"jarvis"` 键，页上显示名「爱莉希雅」（`LBL`，环与文件的 key 照实是 `jarvis`）；`main.py` 启动只 print 一行「爱莉希雅已经启动 http://127.0.0.1:7860」，其余 print 站点全分流（`main/wake/stt/tts/apps/events/web`）。实测 120 s 后 cmd 只有这一行（截图 `.tmp/jarvis_console6.png`）。
- **第 3 条（总用时）**：`main.py` 唤醒确认处记 `t_total`，TTS 播放结束后 `svc.metric("total_secs", ...)`（照实口径 = 唤醒确认 → 播放结束，含 ASR/LLM/TTS 合成与播放），F 块加「· 总用时 X s」。灌入 `total_secs=[3.81]` → 页上显示 3.81 s。**真链路 未测**（我不能说话）。tokens/s 仍未埋（要 tokenizer）。
- **第 4 条（可滚动）**：`body` 由 `overflow:hidden` → `overflow-y:auto`；实测 `scrollBy(0,300)` 后 `scrollTop=300`（内容高 1275 > 视口 774），日志面板 `max-height:220px` + `overflow:auto`。
- **第 5 条（200 行 + 落盘）**：`LOGCAP = 200`，每拍只赋值一次（旧写法每行把整段已累积文本复制一遍 → 第 168 处坐实的卡因）；灌 500 行 → 面板停在 200、首行是最新。落盘照实逐条：`jarvis.log` 1201、`llama.log` 13、`tts.log` 74、`monitor.log` 156 行。真链路累积 200 行 **未测**（需 ~400 s 连续跑）。
- **第 6 条（切换不卡）**：监视页 rAF 心跳实测**最大帧间隔 19 ms**（修复前主线程被拖死到 CDP `Runtime.evaluate` 20000 ms 超时）；收拍 114/120 s（≈1.05 s）；真点 主界面→home 落地 252 ms、监视界面 71 ms。
- **顺带照实坐实的根因**：① `FileResponse` 无缓存头 → jarvis 起的窗口被 Chrome 启发式缓存喂旧页，现三条页面路由带 `Cache-Control: no-store`，自开监视页带 `?ts=<秒>`；② `open_url` 旧判定「标签地址含目标子串」→ 带 `?ts=` 与旧地址互含 → 复用不导航（12:37 实测导航后标题变「监视界面 — 爱莉希雅」）；③ `_reader` 此前直接塞环绕过 `_log` → 服务日志一条文件都没写；④ `shutdown()` 的 `taskkill` 在解释器退出时撞 `RuntimeError: can't create new thread`，atexit 回调被抛掉 → `SHUT_LOG` 一行都没写（加 try 防护后 **未复测**）。
- **自曝第 169 处**：把 9 行 `_log` 体拼到 1 行函数体上 → `IndentationError`（行 217），并吃掉 `_mem_mb` 的 def/docstring 与 `class PMEM` 头；按行索引插回后 `py_compile OK`。
- **自曝第 171 处**：把分流用的 import 插到 `from __future__ import annotations` **之前**（我拼串成「import + 原行」，把 future 行吞进配对）→ `SyntaxError: from __future__ imports must occur at the beginning of the file`；照实把 import 放到 future 行之后，并改用子串定位。
- **自曝第 174 处**：探针里调用未定义的 `as e2` 包装 → `ReferenceError`；改 `repr(e)` 后成立。
- **自曝第 175 处（真 bug）**：`wake.py` 行 191 函数内 `from jarvis import services as svc` 让 `svc` 变**局部变量** → 行 104 `svc.jlog` 撞 `UnboundLocalError`，唤醒线程跑死、jarvis 退出；控制台截图照实显示 traceback + `RuntimeError: can't create new thread at interpreter shutdown`（atexit 里的 `subprocess.run`）。修：函数内局部 import 全去掉、`shutdown()` 逐条 try 包住并落盘。
- **自曝第 176 处**：我把**算出的行号**当「已写入」报告（「插入行 170 ｜ taskkill 行 170」），grep 显示行 170 没改；插入文本还带重复关键字参数 `timeout=10, timeout=None`。规矩照实：插入/替换后必须复读目标区 + 复编译 + 复 grep 命中数，再报结果。
- **自曝第 177 处**：「删函数内局部 import」的过滤条件 `i > 5` 连我加在 `main.py` 行 34 的**模块级** import 一起删了；照实补回行 37，`main/wake 导入 OK`。
- **自曝第 178 处**：样式改动「量到旧版」（`overflowY=hidden`、旧字体、旧标题）——是 Chrome 启发式缓存喂的旧页；带 cache-buster 的 `fetch` 后 9268 字符的新页全命中。教训照实：验证 HTML 改动必须带 cache-buster 或 `cache:"no-store"`，且以真浏览器 + console 为证（design §6 第 10 条）。
- **自曝第 179 处**：`llama.log`/`tts.log` 不存在——`_reader` 直接塞环绕过 `_log`；照实改 `_reader` 走 `_log` + 缓存文件句柄，复测三行假流落盘（`12:21:21 line1/line2/line3`）。
- **自曝第 180 处（行序坑第 3 次重犯）**：`splice(k, 10, wblk)` 又把 `def _mem_mb` + docstring 吃掉 → `class PMEM` 变成 `_log` 的一部分，`_reader` 线程里 `NameError: name 'pid' is not defined`；照实恢复 def 头并复验。
- **自曝第 181 处**：三条页面路由没有缓存头 → jarvis 起的窗口拿到缓存旧页（第 1/4/5/6 条的前端改动在真会话里全不生效）。照实加 `_NO_STORE`。
- **自曝第 182 处**：我在程序里把 `JSON.stringify(tabs.tabs)` 当数组 `.map` → `TypeError`。
- **自曝第 183 处**：我拿改前的行号 370/364/63 做替换，插入块后行号偏移，三条 `return` 一条没改、只插了常量（grep 命中 `headers=_NO_STORE` = 0）；照实改用内容定位，复验命中 3、`exit=0`。
- **自曝第 184 处**：同一 URL 的 CDP 导航在 Chrome 里不重新取页 → 自开页必须带 `?ts=`。
- **自曝第 185 处（缩进坑第 4 次重犯）**：我按 4 缩进整行替换 `try:` 块内的一行（块是 8/12 缩进），把 `try` 拆掉 → `SyntaxError: expected 'except' or 'finally' block`；照实读原缩进整块重写，`exit=0`。
- **自曝第 186 处**：`open_url` 的复用判定是子串匹配（`ident in a`），带 `?ts=` 与旧地址互含 → 复用不导航，真窗口永远跑第一次的旧页（12:33 日志「没有导航」为证）；照实改成地址**完全一致**才复用。
- **自曝第 187 处**：分流 print 用的是改前号，`tts.py` 残余 7 处 print（`[TTS] output stream warmed`、`stream ready`、`played`、`segment synth failed` 等），且把 `[Wake] peak` 归进 `jerr` → 每拍刷控制台；照实复 grep 残余=0 后 cmd 才干净。教训照实：分流后必须复 grep 残余 print 数并复截控制台。
- **自曝第 188 处**：灌入的假 payload 我写 `data: {os: null}` → `render` 第 88 行读 `commit_total` 撞 `TypeError`；照实先抓真推送的 data 再灌。
- **自曝第 189 处**：我在程序里的模板字符串中写了反引号（代码片段），把字符串提前终止 → TS 报 `'**' cannot be applied to unary/await`；照实改用中文引号包裹。
- **自曝第 190 处**：`const add = [...].join('\r\n')` 后写 `L.push(...add)`，`add` 是**字符串**被 `...` 展开成逐字符 → `progress.md` 灌成 5108 行（每行一个字符「2」「0」「2」「6」…），本轮段内容全部丢失（复验「自曝第 169 处」命中 0）。照实修：取回原尾行 `d41f726` 之前的 123 行、丢掉碎字符尾巴，按**数组**追加本轮段。规矩照实：**追加多行用数组 push，不 join 后展开字符串。**
- 落盘：`records/2026-11-22-11-48-11.md`（追加实现与验收段）、`todo.md` 第 95 行 `[x]`（照实标注未测）、`need_user.md` **Q46（status: wait，F2 打字提示是否允许留在 cmd）**、`tests/2026-11-22-11-48-11_six_items/record_1..3.md + opinion.md`、`tests/opinion.md` 追加、`tree.md` 重建、`design.md` v3.4。
- **未测照实保留**：真链路总用时、真链路累积 200 行、`SHUT_LOG` 逐条落盘（加防护后未复测）、只杀自起 pid 的正面路径。



- 2026-11-22-13-16-00 `23fdf38` feat(monitor): Monitor 六条改造（自曝 169–191；已本地 commit，未 push）


- **补测照实（2026-11-22-13:24）**：第 5 条真链路 300 s 连续跑 → 面板 200 行（缓冲首 = 12:53:39 最新在上、末 = 12:46:13 最旧被截），`jarvis.log` 1835 行全量落盘 → 第 5 条由 未测 转 **PASS**；一次瞬时读数 203 > 上限与复验 200 冲突，照实记第 192 处自曝（**未证实**，不猜）。第 2 条「报错在 cmd 看见」照实 **未测**（未构造真报错场景）。


## 2026-11-22-13-48-06 · 第 16 轮 5 条（monitor 4 灯加大、日志两态、滚动条照你 CSS、about 照 home、ws 实时推送）

- 落盘在先：`records/2026-11-22-13-48-06.md`（5 条原话 + 理解 + 设计影响 + 测试安排 + 状态）、`todo.md` 第 97 行；`design.md` 先归档 `ai_buckup/design.md_2026-11-22-13-48-06.md`（v3.4）后升到 **v3.5**（§7 加第 5 条口径：只发日志增量 100 ms 节流、快照照旧每拍 1 s；§3 加第 2 条两态与 200 行上限；§5 加第 1 条灯与第 3 条滚动条）。
- `jarvis/web.py`：`_batch_lines(st)`（逐客户端取新日志、推进游标、每轮 ≤20 行）；`async def _log_flush_loop()`（100 ms 节流只发 `{"type":"logchunk","logs":[[name,lines]]}`，无客户端 0.1 s skip，`globals()["_rt_sends"]` 计数）紧接 `_monitor_loop` 启动；1 s 拍的 payload 在 `try:` 内（行 472，缩进 20），`ws.send_text` 行 473。
- `jarvis/static/monitor.html`（225 行）：第 1 条灯加大（字号 15 px、胶囊 `border-radius:999px`、外圈 `box-shadow` 光晕、12×12 灯点、亮态 `#7CE2A6` 实心 + 光晕、`.lamp.on`/`.lamp.off`）；第 3 条 `*::-webkit-scrollbar` 与 `::-webkit-scrollbar-thumb` 照你原样一个数值不改；第 2 条两态（`follow[name]` + 每面板「最新追加/查看」按钮与状态文字、`pre.onscroll` 判到底自动切回、查看态冻结视野）；`ensurePanel(name)` 建面板（第 198 处缺口照实补：即时增量也要建面板）；`appendLogs` 为唯一路径（1 s 拍与 100 ms 通道共用），`push` + `splice(0, len-200)` 保最新 200（第 192 处方向）+ `sortByTime` 按时间戳稳定排序（第 209 处坐实到达序无保证）。
- `jarvis/static/about.html`（84 行）：第 4 条照 home 改 —— `:root` 同一套变量、三层 `radial-gradient` + `linear-gradient(165deg)`、`body::before` 2 px 粉条、PingFang/YaHei、表格与 `p,ul` 成 16 px 圆角玻璃卡（`box-shadow:var(--shadow)` + `backdrop-filter:blur(10px)`）、`code` 金色；照实把「当前 v3.2」改「当前 v3.5」。照实记第 220 处自曝：重写块一度追加在 `</html>` 之后（页外游离、浏览器不认），照实搬进 `<head>` 后 computed 复量才生效。
- 自曝第 193–221 处照实记（要点：`trim()` 与带空格字面量比较恒 `-1` → 插到文件最前 / 换掉文件末尾；数行错吞相邻 `payload`、插进无 `snap` 的循环、用删前的索引 off-by-one、缩进 16 空格；`screenshot_id: null`、参数名 `deltaY`（真名 `delta_y`）、拿无滚动余量的面板测、复用已消耗的 `screenshot_id`；100 ms 通道与 1 s 拍共用游标到达序无保证（209）；`sortByTime` 插两次 + `findIndex` 命中同款 forEach 删新块留旧块（210–212）；自程序引号写坏未跑（213）；坐标算出截图外（214）；沿用已 `clearInterval` 的旧计数误判冻结失效（217，218 插桩照实证明冻结生效）；往未建目录写 `ENOENT`（219）；报告未生效的 about 样式（220，第 176 处同类续犯）；猜文件名 `home.html`（221，真文件是 `index.html` 55 KB）。下一条从 222 起。
- 验收 3 轮全 PASS（`tests/2026-11-22-13-48-06_five_items/record_1..3.md + opinion.md`，累积已追加 `tests/opinion.md`）：第 1 轮真窗口截图 + 真滚轮（面板 `scrollTop` 随滚轮走、`follow` 切换、查看态 20 s 内 flush 计数 20 与末行 14:40:26 不变 = 冻结、滚到底 `follow=true` 新行落底部、三面板时间序倒置 0、200 行上限、灯 4、console 0）；第 2 轮 about computed + 真截图照出粉条/三层渐变/16 px 玻璃卡/金色 code；第 3 轮无客户端基线 6.296875 s CPU/60 s、有客户端 6.625 s/60 s → 增量 **0.328 s ≈ 0.55% 单核**，逐行延迟 0.5/0.9/均 **0.7 s**、60 s 21 chunk/21 行 → 照实**保留**实时推送（不算太耗性能）。
- **未测照实照实写**：第 2 条「报错要在 cmd 看见」未构造真报错场景；真链路总用时需你在麦克风前（我不能说话）；`SHUT_LOG` 逐条落盘 + 只杀自起 pid 正面路径加防护后未复测。
- `need_user.md` 照实未答照实不动（Q46/Q45/Q44/Q43/Q41/Q19/Q18/Q21–Q24/Q30/Q31-1/Q36/Q39/Q40）。

