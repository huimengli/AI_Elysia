<!-- 已归档于 ai_buckup/hard_bug.md_2026-11-17-13-26-51.md（全量备份，含 HB-047 立案结案、11-06 更正、HB-040 结案）；本文件只保留结案摘要 -->

# hard_bug（compact，已解决）

- **影响**：模型省略可选参数时，播报/行为用**空串**而不是函数的中文默认值（`set_timer` 定时提醒不播报文案）
- **现象**：`dispatch('set_timer', {'seconds':3600})` → 「已设置 1小时 0分 后的提醒：**（空）**」
- **尝试**：只读 `_coerce` 与 schema，确认 schema 里 `message` **没有** `default` 字段，函数默认值是唯一来源
- **根因**：`jarvis/tools/router.py::_coerce` 遍历**所有** schema 属性写值，`out.get(key)` 缺席时得 `None`
  → 被写成 `""`，且**键存在于 dict** → `set_timer(seconds, message="定时到了！")` 收到 `""`，默认值被架空
- **方案**：`if key not in out: continue`（模型没传就不注入，函数默认值生效）；显式 `null` 仍 coerce（防 `NoneType` 崩）。
  **不改 schema 文案、不增删工具**（工具面 token 不变）
- **验证**：**3 轮全 PASS**（`tests/2026-11-17-13-25-00_coerce/record_1..3.md` + `opinion.md`），附加 `click_at` 缺省 `button` 生效
- **关联**：`records/2026-11-17-13-25-00.md`、`records/2026-11-13-*`（立案）、`events.db` 242/245（当年崩溃源）
- **归档**：本条结案后 `hard_bug.md`（HB-047 立案结案 + 11-06 更正 + 本条）全量备份到
  `ai_buckup/hard_bug.md_2026-11-17-{ts_tail}.md`，原文件 compact + 顶部归档注记（§3）


## HB-048 — 2026-11-17 22:05 · 状态：**未修（open）** · 语音整句被「吃尾」，LLM 用对话历史关键词播了之前指定的歌

- **影响**：语音播歌不可信 —— 唤醒正常、播放链路正常，但**歌名丢失**，播的是**上一轮的歌曲**；且听感上「无法语音唤醒」（其实是它自己被打断停了）。20 轮语音验收的轮 11 因此 FAIL。
- **现象**（`.tmp\jarvis6.log` + `.tmp\bats\voice_r11.log` 原样）：
  ```
  [爱莉希雅] Wake word detected! ×4（peak 0.768 / 0.778 / 0.783 / 0.798，阈值 0.75）
  [TTS] ack played (2.26 s)
  [STT] Speech detected (rms=0.0192) → [STT] Recording aborted. → capture saved (1 s)
  [爱莉希雅] Recorded 1.5s of audio, transcribing...
  [You] 播放到
  [Tool: play_music] 关键词「心灯明」→ 最多播放第一支 BV1RMYF6kEze（1770213 播放）
  [ABORT] set by listen_for_wake_word:212 → [爱莉希雅] Stopped. (voice interrupt)
  ```
  你说的是整句「爱莉希雅，播放《稻香》」。驱动前 90 s WS **零消息**（说话落在采样窗外），日志里另有 3 次唤醒 + **3 次转录全空**（`Transcription empty — didn't catch anything`）。
- **尝试**：读 jarvis stdout（新码 `.tmp\jarvis6.log`，工具全文行不截断，main.py:413）+ WS 全事件 + CDP 5 判据；确认唤醒模型正常（峰持续 0.76-0.79）、导航/关弹幕/最低分辨率三项 PASS。
- **根因**（已定位，5 条）
  1. **转录吃尾**：唤醒后先播 ack `2.26 s`，`[STT] Recording aborted` 把录音截到 1.5 s → 录进的是指令被截后剩下的半句 `[You] 播放到`，歌名丢失；
  2. **LLM 用历史关键词**：`播放到` 没有歌名 → 模型从对话历史取上一轮的「心灯明」→ 播了你之前指定的歌（`order=play` 本身没错，错在关键词不是你要的）；
  3. **「无法语音唤醒」是现象不是模型失效**：`[ABORT]` + `Stopped. (voice interrupt)` 自停；峰照常触发；
  4. **CDP 9333 随 Chrome 实例漂移**：实例 pid 11820 → 12808，端口随旧实例消失 → 播中 51 s 断读，「到达结尾」无法判；
  5. **关窗仍用「pid 对标题」**：`play_music` 结尾报「找不到我自己起的 B 站窗口…没有关闭任何窗口」，与第 2 项刚修的窗口计数**同族**（pid 会随实例漂移，profile 才是身份）→ 旧窗口残留，直接撞上 22:05 的**音乐唯一性**新规则。
- **方案**（待实施，明天）
  1. `play_music` 起手先数我起的窗口（profile 认 pid），已有播歌窗口 → **复用导航**或先关旧的，**绝不并存 2 个**（22:05 唯一性规则）；
  2. 结尾关窗改**同一口径**（profile 认 pid），关后「我起的窗口数」必须 0；
  3. 转录侧：让录音拿到**整句**（ack 期间不采 / 录完再播 ack，或提高 VAD 中止门限），并在歌名缺失时**如实问用户**而不是用历史关键词；
  4. CDP 侧：断读后重连新实例，不许把「断读」当「到达结尾」。
- **关联**：`tests/2026-11-08-20-44-17_cc/record_11.md`、`records/2026-11-17-22-05-05.md`（唯一性新规则）、`records/2026-11-17-20-16-55.md`（第 4 项 20 轮）、`0221012`（第 2、3 项）。

## HB-049 · 2026-11-18-11-56 · 状态：open
- **影响**：20 轮批次跑到轮 21-23 时 WS 连不上，**jarvis 进程已消失**（jarvis.main 无 python 进程、
  /api/health 空回），轮 21/22/23 直接 ConnectionRefused 崩掉。
- **现象**：.tmp\jarvis17.log 尾是连续的 [Wake] peak …/ threshold 0.75（主线程无 traceback）；
  .tmp\jarvis17.err 只有 WS 断连的 ASGI 栈：ws.receive_text() 抛 starlette.websockets.WebSocketDisconnected
  （「WebSocket is not connected. Need to call "accept" first.」），websocket_endpoint 的
  except WebSocketDisconnect（web.py:387）**接不住这个类型**，每条断连刷一次栈。
- **尝试**：查 health / 进程表 / 两份日志；没有主线程崩溃证据 → **进程死亡原因未证实**
  （最可能 OOM/系统杀，24 GB 内存 + 8 GB 分页，你 2026-11-16 定过「chrome 崩溃属内存溢出，
  需要用户注意的问题」，Q31/Q22 口径：页文件不动）。
- **根因（已证实部分）**：WS 断连异常类型不匹配，错误日志刷爆且断连不被优雅处理；
  进程死亡本身无证据链（隐藏 Start-Process + 重定向日志没有退出码记录）。
- **方案**
  1. web.py 补 except WebSocketDisconnected（已落地，编译通过）；
  2. 给 jarvis 加**看门狗/退出码落盘**：外层启动脚本把退出码写进 .tmp\jarvisN.exit，
     下次死亡就有硬证据（未做，P1）；
  3. 每轮驱动在 WS 连不上时**如实记 FAIL 并查 health**，不把连不上算成模型失败。
- **关联需求/测试**：records/2026-11-18-10-17-23.md、tests/2026-11-18-10-17-23_cc/record_9.md、
  HB-047（chrome 崩溃，wontfix，Q31）、Q22（8 GB 分页不动）。

## HB-050 · 2026-11-18-12-44 · 状态：open（我暂停落盘时未结案）
- **编号/时间**：HB-050，2026-11-18 12:40-12:44（jarvis20，WS 文本，无语音）。
- **影响**：`click_page_text`（我起窗口里的页面点击）能否真的导航**未证实**；「页面里找字并点击」
  这条能力现在只能记「命中坐标 + 点下元素 = 目标链接」。
- **现象**：直测 `find_page_text("番剧", click=True)` 报「已用 CDP 受信点击『番剧』 @(x=100,y=32)」，
  点击后复读 标题「哔哩哔哩 (゜-゜)つロ 干杯~-bilibili」 地址 `https://www.bilibili.com/` —— **地址没变**。
  轮 28 用户话「点击页面上的番剧」，模型只调 `find_on_page`（闸门生效），工具崩在我自己的代码上。
- **尝试与实测**：
  1. 复现崩因：`c.ev` 返回 `'null'` → `json.loads('null')` = `None` → `.get` 崩（`'NoneType' object has no attribute 'get'`）；
     **根因是我拼接 JS 字符串时漏了外层 `for` 的右花括号**（`if(hits.length>=5) break; }` 只闭合 `if`），
     `return` 落进 for 体、函数体未闭合 → 表达式求值 undefined → CDP 回 `null`；补 ` }` 后立刻命中
     `{"命中":[{"文本":"番剧","x":100,"y":32,"href":"https://www.bilibili.com/anime/"},…]}`；已加防御（非 dict 如实报）。
  2. 坐标核对：`a[href="https://www.bilibili.com/anime/"]` 矩形 `x=86,y=0,w=28,h=64` → 中心 (100,32)；
     `document.elementFromPoint(100,32)` → `{"点下元素":"SPAN","文本":"番剧","祖先a":"…/anime/"}`，点下就是目标链接。
  3. 对照：DOM `a.click()`（不可信事件）同页面不导航；且同一页面两次查询该 href，一次列出 3 个、一次返回「没有该链接」
     —— **同一页面查询不一致，原因未证实**。
- **根因**：**未证实**。可能方向（都未验证，不写成结论）：SPA 路由对 CDP 事件的响应需要额外的 pointer/时间序列；
  我的 `real_click` 序列（mouseMoved → 250 ms → mousePressed → 80 ms → mouseReleased）在这类导航链接上
  是否被页面识别为一次有效点击，没有证据；我的查询语句在 SPA 重渲染后的时序敏感也可能造成「没有该链接」。
- **方案（下一步，未开工）**：①在同一个 CDP 会话里做「点击前后连续读 `location.href` + 记录 DOM 快照」的
  最小实验，判定是事件没被识别还是页面在点击后立刻重渲染；②若事件路线不稳，改用「找到元素后取 `href`，
  用 `Page.navigate` 导航我自己起的窗口」（丙方案精神：无视觉、无坐标，导航成功以地址复读为证）；
  ③`click_page_text` 在实验结论出来前，回复里必须如实说「点了、地址没变」，不承诺导航成功。
- **关联**：tests/2026-11-18-10-17-23_cc/record_10.md、record_11.md、need_user.md Q37、progress.md P1②。

# HB-051（2026-11-18 20:21，status: open）播放中的视频音频触发唤醒（你确认没说话）

- **编号/时间/状态**：HB-051，2026-11-18 20:21，**open**（等你选方案，我不自行推进）。
- **影响**：环境音期望必须 0（`onnx_opinion.md` 第 0 块 / 12:18 约束）被打破；播歌期间唤醒被视频声音
  抢走 → 录音、转录为空、可能打断播放中的动作（轮 11/15 的 toggle 副作用同族）。
- **现象（全部来自日志与你的确认）**：你 20:21 逐字「**我刚刚没说话,但是好像触发了3次(播放视频)**」；
  我读 jarvis22 日志 336 行：**`Wake word detected!` 4 次**、peak 日志 257 条中 **9 条越线**
  （0.783 / 0.818 / 0.808 / 0.820 / 0.804 …，阈值 0.75）、**`Transcription empty` 3 次**；
  health `last_detect` 20:02:29 / 20:14:22（`last_detect` 只在 `score >= threshold` 时写，
  `wake.py:182-187`；`peak` 是 3 秒节流窗口峰值，不是触发值 —— 已核实，不猜）。
- **尝试**：①核字段语义（`web.py:264-272` + `wake.py:175-187`）→ 触发真实，不是读数误判；
  ②数日志（上）；③检查自声抑制覆盖面 —— `_ignore_until` 冷却窗与 `is_speaking()` 只覆盖 **jarvis 自己的 TTS**，
  **浏览器视频音频不在 ducking 范围**（2a-2f 播放链只控 B 站播放器，不控麦克风门）。
- **根因（未定性，机制成立）**：视频音频的声学内容能让 oww 越线（机制上成立，你确认无说话）；
  **要定性必须 ≥3 个独立 Model 实例对同一段音频取多数（HB-032），我还没做。**
- **方案（待你选）**：①播放期间给麦克风门加 ducking（与 10:17 第 1 项同源，播完恢复）；
  ②播放期间暂停唤醒线程（最省事，播完必须恢复，且不能漏真人打断）；③接受现状，把「播放中不认唤醒」
  写进使用须知。
- **关联**：records/2026-11-18-20-21-00.md、tests/2026-11-18-10-17-23_cc/record_12.md、todo.md、
  HB-048（到达结尾被实例死亡打断）、HB-032（取多数规矩）、Q37（无中文 OCR，与本条无关）。

## HB-051 状态更新（2026-11-18 20:40，追加，不改历史条目）：现象定性成立

- **状态**：`open` → **现象定性成立**（手机视频音频在部署条件下能让 v0.9 越线）。
- **证据（你定的 10 秒录音法，20 段，20:34-20:38）**：保存 3 段 / 丢弃 17 段；HB-032 口径 **3 个依次构造的独立实例**（同一 `aili_xiya_v0.9.onnx` + `threshold 0.75` 不动）：
  seg_203413_1 live 0.766/越线1 -> 3 实例 peak [0.76, 0.795, 0.769] 越线 [1,1,1] **多数触发 True**；
  seg_203623_14 live 0.773/越线2 -> [0.791, 0.794, 0.773] 越线 [2,2,2] **True**；
  seg_203633_15 live 0.767/越线1 -> [0.676, 0.676, 0.676] 越线 [0,0,0] **False**（漂移 ±0.09，照实记）。
- **交叉验证**：jarvis22 日志 `Wake word detected!` 4 -> **13**、越线 peak 行 9 -> **31**、`Transcription empty` 3 -> **12**（同一麦克风，录音期间同步上升）。你全程没说触发词（20:21、20:31 两次确认）。
- **仍待你授权**：方案①播放期间给麦克风门加 ducking（播完/关窗恢复）；方案②播放期间暂停唤醒线程；方案③写进使用须知。**阈值与 onnx 不动。**
- **自曝（脚本级两条）**：一次构造 3 个实例 -> `bad allocation`（必须依次构造，`peak3()` 已是这个写法）；`predict(bytes)` -> `ValueError`，要 numpy 数组。
