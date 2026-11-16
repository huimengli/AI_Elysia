# 轮 1 · 2026-11-16-12-41-30

- **时间**：2026-11-16 12:41:30（点击），12:41:45 读数，12:43 复核内存与事件账本
- **场景**：第 2 条「播放音乐走浏览器 → B 站搜索播放」。共用浏览器（`dsh-builtin-browser`，tab `ca779fdc…`，**零截图**）刷新 7860 页，用 JS 点「播放音乐」快捷按钮（该按钮在 `#tab-actions`，非活动 tab 里 `.tab-panel{display:none}`，坐标点击不可靠，故用 JS `click()`），然后读 DOM + `/api/events`
- **期望**（判据，落盘在 records/2026-11-16-12-33-59.md）：
  1. 用户气泡是中文命令，不是英文；
  2. 模型调用 `open_url`，URL 是 `https://search.bilibili.com/all?keyword=<歌名>`；
  3. 页面进入视频页，`<video>` 存在且时长非 0、`paused=false`；
  4. 4 灯 online，唤醒现役 `v0.9 + 0.75` 不动。
- **实际**：
  1. **通过**：`data-cmd` = `用浏览器打开B站搜索《稻香》并播放第一支视频`，用户气泡文案与命令一致（`btn.dataset.cmd` 与 `.msg.user` 末条逐字比对）。改前实测是 `What time is it?`（「时间」按钮）—— 语言不一致这条已消。
  2. **未发生**：模型没有走到 `open_url`。助手气泡是运行时异常：`Error: [ONNXRuntimeError] : 6 : RUNTIME_EXCEPTION : Exception during initialization: bad allocation in query.`；`jarvis/tools/router.py` 的 `[Tool: open_url]` 行**没有出现**。
  3. 机制侧单独验通（我自己在共用浏览器跑，作为第 2 条的可行性证据）：打开 `https://search.bilibili.com/all?keyword=稻香` → 标题 `稻香-哔哩哔哩_bilibili`、86 个 `a[href*="/video/"]`；点第一支含「稻香」的链接（`BV13G411Q76u`）→ 新 tab 视频页，`videoFound=true`、**duration=224 s**、`currentTime` 6.97 → 9.48、`paused=false`。
  4. **通过**：12:35 复核 `wake=True asr=True llm=True tts=True`，`model=aili_xiya_v0.9.onnx thr=0.75`。
  5. **新暴露的可观测性缺陷**：`/api/events?limit=300` 里 ONNX 命中 **0 条**（事件止于 `user | web`，无 assistant 事件），「实时」面板与 2 秒轮询看不见这次失败；`.tmp\bats\start7860_1235.log` 里 `[You]`/`[爱莉希雅]` 行未刷出（`*>` 重定向缓冲）。根因：`jarvis/web.py` L371 `except Exception as e` 只 `ws.send_text(f"Error: {e}")`，不写事件账本。
  6. 同期内存（口径 `Win32_OperatingSystem` / `Win32_Process.PageFileUsage`）：**可用提交 166 MB**（12:22 为 1,814 MB），物理可用 4,981 MB。
- **结果**：**部分通过 / 未达标**。第 2 条的语言与中文命令部分通过；B 站播放链路在服务级**未达成**，卡在 `onnxruntime` 分配失败（提交额度耗尽）。B 站机制本身已验通（第 3 点）。记 hard_bug **HB-043**（未解决），need_user **Q21/Q22/Q23**（等授权）。
- **备注**：副作用披露 —— 我在共用浏览器**真的打开了** B 站搜索页与视频页（`BV13G411Q76u`，正在播放，时长 224 s），这个 tab 我没关；`F:\2D23D` 的 `src.server` 我**没有**结束（授权范围只到记事本）；本轮**没有**真打开任何本机应用，没有写文件，没有改音量/亮度。零截图：本轮全部证据来自 `dsh_browser_a11y/state/execute` 与 `mcp__playwright__browser_evaluate`（窄窗口量测），两个 surface 的证据分开记录，没有混用 ref/坐标。
