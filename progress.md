<!-- 已归档于 ai_buckup/progress.md_2026-11-22-18-30-00.md -->

# Progress — 跨会话进度台账（compact，保留最近三段原文与全部 Git 提交记录）

- 归档动作照实记（2026-11-22-18-30）：本文件 105 行 > 100 → 备份到 `ai_buckup/progress.md_2026-11-22-18-30-00.md`（105 行全量），本文件只留最近三段原文与全部「Git 提交记录」，不删历史内容。
- 更早段照实见归档件（11:14 会话追加段、Monitor 六条改造段的前半、自曝 147-191 的要点、`81a0f6e`/`a105727`/`d41f726` 三条提交记录上下文）。
- 自曝编号照实连续，下一条从 239 起。



## Git 提交记录（照实全量，含归档时被切掉的 3 条）

- 2026-11-22-11-16-00 `81a0f6e` fix(monitor): 修 Monitor 推送链根因并落盘真会话验收（自曝 147、149-163；已本地 commit，未 push）
- 2026-11-22-11-17-00 `a105727` docs(progress): 追加 81a0f6e 提交记录与自曝段（已本地 commit，未 push）
- 2026-11-22-11-21-00 `d41f726` docs(tests): 追加重启后健康复测与自曝 164-165（已本地 commit，未 push）
- 2026-11-22-13-16-00 `23fdf38` feat(monitor): Monitor 六条改造（自曝 169–191；已本地 commit，未 push）
- 2026-11-22-15-06-00 `ebe1d80` feat(monitor): 五处改造（自曝 193–221；已本地 commit，未 push）


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



«已去重（第 240 处自曝：补回时重复）»


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

«已去重（第 240 处自曝：补回时重复）»

## 2026-11-22-15-45-55 · 第 17 轮 3 条（滚动条照 home、About 五块写入 design、录音法录异常触发）

- 落盘在先：`records/2026-11-22-15-45-55.md`（3 条原话 + 理解 + 设计影响 + 测试安排 + 状态）、`todo.md` 第 98 行；`design.md` 先归档 v3.5 到 `ai_buckup/design.md_2026-11-22-15-45-55.md` 后升 **v3.6**（§6 第 17 条滚动条改 home 口径、新增第 20 条录音法、新增 **§9 About 内容 5 块 a–e**）。照实记第 222 处自曝（连续两次）：第一次升版写入全没落上（改动只赋给内存数组、写盘用原始字符串），照实重做（数组 join 写盘）后复 grep 才落上（行 9 = v3.6 + 归档提示、更新时间 15-48）。
- `jarvis/static/monitor.html`（202 行）与 `jarvis/static/about.html`（89 行）滚动条照实照抄 home 真口径（`index.html` 132-134、199-200）：`width:8px` + `linear-gradient(var(--pink),var(--rose))` + `border-radius:8px` + `track:transparent`；照实记第 223/224 处自曝（about 原先一条滚动条规则都没有；第一次替换把 thumb 的多行声明留在原地成悬空声明，CSS 残缺，照实删净后复验）。照实记 13:48 你贴的那段 CSS 入台账，15:45 你说「不符合 home 设计」→ 以 home 为准。
- `jarvis/static/about.html`（100 行）正文照实重写成 5 块（a 模型与语音 / b 此电脑 / c 项目地址（远程 `origin https://github.com/huimengli/AI_Elysia` 照实只读不 push + 本机 `http://127.0.0.1:7860` 三页）/ d 介绍照实链路 / e 工具介绍照实取 `TOOL_MAP` 44 个真注册名分类），读数全部现采；照实记第 226 处自曝（第一次采机器读数采错：`NumberOfProcessors`=1 是 socket 数、GPU 取到虚拟驱动 `OrayIddDriver Device` 显存 0 MB，照实重采得物理 8 核 / 逻辑 16 核、AMD Radeon 780M 4095 MB，照实把虚拟驱动一并列出）。
- 第 3 条照实复用真口径写两脚本：`.tmp/abnormal_capture_rounds.py`（喂 STT 落盘件）、`.tmp/abnormal_10s_recorder.py`（真麦 10 s 段，照实照抄 `wake.py` 90-96 行 `input=True` + `deploy_rounds.py` 逐件 3 实例 + `del`/`gc` + 5 s 冷却，阈值 0.75 不动）。照实记第 229-234 处自曝（`join` 写成 Python 语法、`stream_callback=None`、未 trim 锚点、4 空格缩进 `IndentationError`）与第 235-238 处（TS 反斜杠转义写坏两次、TS 属性名含括号、照 stdout 尾部把「保存 7 件」报成 5 件，照实从 json 全量核后追加更正段）。
- 验收 3 轮全 PASS（`tests/2026-11-22-15-45-55_three_items/record_1..3.md + opinion.md`，累积追加 `tests/opinion.md`）：第 1 轮三面板滚动条实测宽 **8 px**、thumb `linear-gradient(rgb(248,169,196), rgb(126,63,102))`、圆角 **8px**、track 透明、旧口径声明残余 0、真页截图照出粉色 thumb、console 0；第 2 轮 about 5 块真页全在 + 16 关键字全命中 + console 0（照实记 about 无溢出测得滚动条宽 0，不谎称可见）；第 3 轮 20 段 **保存 7 件 / 丢弃 13 段**、3 实例全越线 **5 段**（峰 0.760/0.768/0.767/0.794/0.777），jarvis 真触发 8 次（15:44-18:08，越线峰 0.751-0.822，触发后转录照实空/aborted）→ 打字声与手机播放小说照实能让 v1.3 越线（与 HB-051 定性一致），7 件照实补登 `need_audio.md`（第 12 节 + 照实补登节）。
- **未测照实照实写**：越线 7 件离线只跑 1 遍（未做 3 轮）；这些件是否让 jarvis 真触发需你在麦克风前复现（我不能说话）；「报错要在 cmd 看见」与真链路总用时照实仍未测。
- `need_user.md` 照实未答照实不动（Q46/Q45/Q44/Q43/Q41/Q19/Q18/Q21-Q24/Q30/Q31-1/Q36/Q39/Q40）。



- 2026-11-22-18-50-00 `7c0beae` feat(monitor,about): 滚动条照 home 真口径、about 五块内容照实写入 design v3.6、录音法录到异常触发段（自曝 222–243；已本地 commit，未 push）
