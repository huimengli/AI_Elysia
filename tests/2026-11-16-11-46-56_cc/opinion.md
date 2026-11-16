# 批次结论 · 2026-11-16-11-46-56（UI 确认与优化 · 第 2 条 B 站播放路径 6 轮）

## 判据（第 2 条，你 12:18 定的「播放音乐走浏览器→B站搜索→播放」）
1. 「播放音乐」快捷按钮发**中文命令**（不再是 `Open Spotify`）
2. 模型选中 `open_url`，URL = `https://search.bilibili.com/all?keyword=<歌名>`
3. 进入视频页并播放（`<video>` 时长非 0、`paused=false`）
4. 事件账本可见、4 灯不掉、`v0.9 + 0.75` 不动

## 6 轮结果
| 轮 | 时间 | 选工具 | 页面 | 播放 | 结果 |
| --- | --- | --- | --- | --- | --- |
| 1 | 12:31 | 未选 `open_url` | 我用共用浏览器手工验通机制（86 个 `a[href*="/video/"]`，点进 `BV13G411Q76u`，`duration 224 s`、`currentTime 6.97→9.48`、`paused=false`） | 手工 ✓ | 机制可行、工具未选中 |
| 2 | 12:48 | `web_search`→`open_app`→`type_text` | 无 | ✗ | 未达标 |
| 3 | 12:50 | `open_app`+`ctrl+t`+`find_on_screen` | 无 | ✗ | 未达标（模型把「打开网址工具」执行成打开 Chrome） |
| 4 | 14:43 | **`open_url` ✓** | 当时无窗口证据 | ✗ | 选工具卡点解除 |
| 5 | 15:10 | `open_url`（真路径启动） | 无可见窗口 | ✗ | 工具**如实报失败**（不再假成功） |
| 6 | 15:20 | `open_url` + **复读到真窗口标题** | B 站搜索页 OCR 读到 | ✗（`find_on_screen` 中文匹配不可靠） | 部分达标 |

## 结论
- **判据 1、2 达成**：中文命令生效；`open_url` 被选中且 URL 正确。修法按 `agent-experience`：把「用 `open_url` 到达网页，不要打开浏览器应用再打字」写在 `open_url` 的 description 上、只说一次（规则从 `url` 参数移到参数外、删重复），模型选择行为改变可测（轮 3 的 0 次 → 轮 4 起 3 次）。
- **判据 3 未达成**，卡点有两处，都是实测不是猜：
  1. **`open_url` 的假成功已修**：原实现 `webbrowser.open(url)` **不检查返回值**，直接回「已在浏览器打开」→ 属虚假成功（你 14:40 指认「爱莉希雅没能真正打开网站」，成立）。现在：用应用表里浏览器真路径 + `--new-window` + **进程内 ctypes 复读到窗口标题**才算成功，拿不到证据就如实说「页面可能没有真的打开，请确认」。
  2. **沙箱边界定论（新发现，最重要）**：同一个 `.ps1` 枚举 `MainWindowTitle`，我的 pwsh 工具里 **7 个窗口**，python 子进程里的 powershell/pwsh 里 **0 个**；`ctypes.EnumWindows` 在 python 自己进程里 **9 个**；pwsh `Start-Process chrome --new-window` → **窗口标题出现**，python `Popen` 同一命令 → **只有进程、无可见窗口**。定论：**沙箱内 python 起的进程不能产生可见窗口**，且**窗口证据必须进程内 ctypes 取**（powershell 子进程看不见窗口、Add-Type 又被沙箱拒）。→ 第 2 条的**真端到端必须在沙箱外跑 jarvis 验**（Q25）。
- **OCR 短板实锤**：轮 6 读到 `稻 杳 一 哔 哩 哔 哩 bilibili`（稻→杳错字、字间插空格），`find_on_screen` 中文分词 overlap 不可靠 → 只给出「最接近的匹配 Hi•Res」。这正是第 6 条（视觉塔 + 保留 OCR）要补的洞：**视觉负责「找到第一支视频在哪」，OCR 负责读文字**。
- **4 灯与现役口径全程保住**：每轮 4 灯全 online，`model=aili_xiya_v0.9.onnx thr=0.75` 未动，`stt.engine: whisper`、`stt.hot_bias: false` 未动。
- **提交量全程量**（同口径）：32,575→28,261→29,684→29,812 MB 上限，可用 521→3,451→3,405→2,929 MB；页面文件在系统托管下从 16 MB 起涨（峰值 724 MB），你把上限从 32.5 GB 改到过 25.1 GB，现在 29.8 GB。**接视觉塔的 1,527 MB 仍要在 Q21/Q22 落地后才能加**。

## 副作用（全部披露）
- 我在共用浏览器里开过 B 站搜索页与视频页（轮 1，未关）。
- pwsh 工具启动的 B 站窗口（进程 8228）**未关**。
- 多轮真启动 chrome（后台标签，无可见窗口）；`type_text` 走过剪贴板粘贴（先存后还）。
- 断线测试注入文本让模型尝试 3 次写文件，全被白名单/路径拒，**未产生文件**。
- 我这侧边界：`dsh_browser_execute` 20 s 超时吃掉 25 s 等待；`capture_output=True` 在沙箱 EPERM；`Add-Type -TypeDefinition` 被拒；python 子进程无网络（`web_search` 必失败，不代表你直接跑 jarvis 的表现）。

## 未下结论的部分
- 轮 5 的 `WebSocketDisconnected` traceback（`ws.accept()` 在 L339 存在）——记为观察，未定根因。
- 语音 20 轮的轮 5 `11:59:26` 触发归因仍「不确定」，不在本批次。
