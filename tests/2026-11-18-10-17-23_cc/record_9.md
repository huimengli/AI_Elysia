# 轮 15-23：播放控制复测 + 站点/自定义对象/微信（10:17 第 1/2/3 项）

- **时间**：2026-11-18 11:52-12:05（jarvis17 与 jarvis18）
- **场景**：WS 文本，全部非语音（你不在电脑前）；语音 ducking 验收记为待你在麦克风前。

## 播放控制（第 3 项）复测：三项全 PASS
- **轮 16（暂停播放，播放中）**：**PASS** —— `music_control(pause)` →
  `已暂停我自己的播放（回读 paused=True，ct=14.3/224）`，回复「已暂停我自己的播放。」；
  轮 15 播放中同一指令同证据（`paused=True，ct=14.3/224`）。
- **轮 17（恢复播放）**：**PASS** —— `已恢复播放（回读 paused=False，ct=14.3/224；
  暂停来源：我按的暂停，按用户指令恢复）`。
- **轮 18（关闭音乐）**：**PASS** —— `关闭我自己起的窗口 pid 16408…SUCCESS: … terminated.`；
  pid 随 Chrome 实例漂移（16408 → 2820）后 `play_music` 收尾仍按 profile 口径认出并关掉，
  **`关后我起的窗口数：0`**（22:05 唯一性成立）。
- **播歌 5 判据**：①导航 ②关弹幕 ③最低分辨率（这支 640x360，判据 = 点过「360P 流畅」+ 宽度 640）
  ④时间前进 全 ✓；④「到达结尾」两次都在 **t+93/105 s CDP 断读**处如实记 False
  （`断读重连` 没触发，因为 `pages()` 扫不到标签 = 实例死亡），⑤在轮 15 的收尾达成（关后 0）。
  **到达结尾在实例存活下仍未复现**，不写成达成。

## 站点与自定义对象（2a-2f）
- **轮 20（打开浏览器）**：**核心 PASS**（`open_site(浏览器)` → baidu，地址+标题证据，pid 17252）；
  自曝：模型之后拿 `find_on_screen("打开浏览器")` + `type_text("打开浏览器")` 凑数 —— 把**你说的话**
  粘进被聚焦窗口。已加凑数动作闸门覆盖「打开 + 对象」话术。
- **轮 21（打开github）**：**PASS**（复用窗口，CDP `Page.navigate`，复读 `['https://github.com/']（含 github.com），导航成功`），
  尾随 `get_open_windows` + `focus_window` 属铺张（非判据）。
- **轮 22（打开b站）**：**PASS**（`导航成功`，地址 `https://www.bilibili.com/`），模型两次想播歌
  都被闸门挡回（`没有播歌：这句话里没有播放指令（原文「打开b站」）`）✓。
- **轮 19b（打开我的播歌页，2c）**：**FAIL（模型编造站点名）** —— 先 `play_music`（动词「播」假阳性，
  已修闸门），再 `open_site(site="我的服务器")` —— 用户说的是 `我的播歌页`，模型编造名字；
  工具诚实拒绝并**把可用名字列出来**（用户自定义 `['github','b站','我的播歌页']`）；补 19c 复测。
- **轮 23（打开微信，2b）**：**PASS（只打开口径）** —— `已打开：微信（从应用列表匹配，复读确认进程 Weixin）`；
  登录没做（无凭据），Q36 继续挂着（`只打开` vs 你提供加密凭据）。

## 进程事故（自曝，进 hard_bug.md HB-049）
- **jarvis17 在轮 21-23 期间进程消失**：`jarvis.main` 无进程、`/api/health` 空回，三轮驱动
  `ConnectionRefused` 崩。主线程无 traceback → **死亡原因未证实**（最可能 OOM/系统杀，
  24 GB 内存 + 8 GB 分页，Q22/Q31 口径）。
- **已证实的 WS 缺陷**：断连时 `ws.receive_text()` 抛 starlette `WebSocketDisconnected`，
  `web.py:387` 的 `except WebSocketDisconnect` 接不住 → 每条断连刷 ASGI 栈。已补 `except
  WebSocketDisconnected`（编译通过）。计划：启动脚本落退出码 `.tmp\jarvisN.exit`（未做）。

## 轮 19c（打开我的播歌页复测，12:07）：**PASS**
- 第 1 次 `open_site(site="我的服务器")` 仍编造名字 → 工具诚实拒绝并列出可用名字
  （用户自定义 `['github','b站','我的播歌页']`）；
- 第 2 次模型照名字调 `open_site(site="我的播歌页")` →
  `打开「我的播歌页」→ https://www.bilibili.com/video/BV1RMYF6kEze（来源：config.yaml 的 sites（用户自定义））`
  + `复读全部标签（0.0 秒）：['https://www.bilibili.com/video/BV1RMYF6kEze/']（含 BV1RMYF6kEze），**导航成功**`；
  snap 我起的窗口数 1（复用 pid 17252），CDP 地址 `…/BV1RMYF6kEze/?vd_source=…` ✓；
- 之后模型又想 `play_music(url=…BV1RMYF6kEze…)`，被「打开 + 页」闸门挡回（`没有播歌…「播歌页」里的「播」撞了播放动词`）✓。
- **设计结论**：**诚实拒绝里把可用名字列出来**，能把编造名字的小模型拉回正确条目 —— 19b FAIL → 19c PASS 就是这条起的作用。

## 结果
- 播放控制三项：**PASS**（16/17/18）；播歌 5 判据 4 项成立、到达结尾未复现（如实 False）；
- 2a/2e/2f/2b：**PASS**；2c：**FAIL → 19c 复测中**；2d bing 兜底：**未触发、未测**。

## 关联
records/2026-11-18-10-17-23.md、record_7.md、record_8.md、hard_bug.md HB-049、need_user.md Q36、tests/opinion.md。
