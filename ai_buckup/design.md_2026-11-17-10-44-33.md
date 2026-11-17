# 总设计

- **版本**：v2.0（v1.0 已归档到 `ai_buckup/design.md_2026-11-17-10-24-25.md`）
- **更新时间**：2026-11-17-10-24
- **关联需求**：`records/2026-11-17-10-24-25.md`（「在 UI 中制作一个 moniter 界面」「内容我还没做好决定，先做 design，**不开工**」）
- **决定权在用户**：内容候选与 4 个决定点见 `need_user.md` **Q30（status: wait）**。**Q30 未答复前不写实现代码。**

> 本版只做设计。`jarvis/static/index.html` 与后端**未改动**；下方所有落点都是实测量，不是推测。

## 1. 目标与非目标

**目标**：在爱莉希雅 UI 里加一个 **只读的 Monitor 面板**，把"这台机器现在扛不扛得住"摆在眼前。
动机是实测过的两次事故：`hard_bug.md` **HB-047**（进 B 站视频页后 chrome 抛异常 `0x00000008`，你判定内存溢出）
与 12:18 第 5 条（「内存可用还有 6g，但已提交内容却满了」——上限 30,283→32,575 MB、可用一度 **237 MB**）。

**非目标（明确不做）**：
- **不做窄窗口适配**（12:18 第 1 条：默认最低 1080p，窄窗口 UI 不用管）
- **面板不执行任何动作**：关窗口、杀进程只走已有工具（`manage_browser_windows` / `kill_process`），Monitor 只展示——**"看到数字就自动杀进程"是虚假成功的温床，禁止**
- 不引第三方图表库（canvas 手绘 sparkline 足够）；不加新依赖
- 不改 `aili_xiya_v0.9.onnx` + `thr 0.75`、`stt.engine: whisper`、`stt.hot_bias: false`

## 2. 落点（实测量，2026-11-17）

`jarvis/static/index.html` **1001 行**；`.side-panel{width:380px}`（`L186`），`.side-tabs{gap:6px;padding:10px 12px}`（`L191`），
`.side-tab{flex:1;font-size:12.5px;padding:8px 6px}`（`L192`）。现 4 个 tab（`L359-363`）：
`data-tab="tools|live|actions|settings"`。**加第 5 个 tab「监控」**后每 tab 宽约
`(380 − 2×12 − 4×6) / 5 = 66.4 px`，两字中文标签放得下。

复用现成的视觉语言，不新造样式体系：
- 四灯 `.svc-lamp`（`L294-298`，`#svcLamps`）已有 `off / warm / on` 三态与 `.dot` 发光（`L88-95`）→ Monitor 里的服务健康直接用同一组件
- `.tool-log-entry`（`L209`，`padding:8px 10px; border-radius:12px`）→ 列表行的样式基线
- 配色令牌（`:root`，`L10-13`）：`--pink:#F8A9C4`、`--pink-2:#FFD8E8`、`--gold:#F2C9A8`、`--lilac:#C9B7E0`、
  `--text:#F6ECF2`、`--text-dim:#CDBCC8`。**需新增 1 个令牌** `--danger:#E57878`（低于安全线时用，现无危险色）

WS 消息 12 类（前端 `L592-664`：connected/status/user/wake/tool/tool_result/response/mute/provider_changed + reactor 状态），
服务端广播在 `main.py L404/410/453/458`（`tool` / `tool_result`，result 截 200 字节）。

## 3. 内容候选（A-F，决定权在 Q30）

| 块 | 内容 | 数据来源 | 成本 | 备注 |
| --- | --- | --- | --- | --- |
| **A 资源仪表** | 提交 上限/已用/**可用 MB**、物理内存占用%、CPU% | `Win32_OperatingSystem` + CPU 采样 | 低（1 次 WMI/轮） | **HB-047 与 12:18 第 5 条的直接动机，推荐必选** |
| **B 服务健康** | wake / asr / llm / tts 四灯（已有语义） | 现有 `/api/health` 逻辑（`web.py` `_tcp_probe`） | 低 | 复用 `.svc-lamp`，零新语义 |
| **C 进程与窗口清单** | jarvis / api_v2 / llama-server / GPT-SoVITS / chrome 的 pid + **提交 MB**；我起的浏览器窗口数（上限 3） | `Win32_Process` 按命令行匹配 + `_browser_windows()`（`app_control.py`） | 中（枚举 13-25 进程） | 与 Chrome 管理器 ≤3 联动；**只展示，不在此关** |
| D 事件时间线 | wake/user/assistant/tool 流水 + 时间戳 | 已有 `events.db` + WS | 低 | 与「实时」tab 重叠，价值边际低 |
| E 工具调用统计 | 各工具调用次数、耗时、失败率 | `main.py` tool/tool_result 广播侧写 | 中（需累计器） | 对"点不进/没跳转"这类诚实失败最有用 |
| F 语音链路指标 | wake 置信度、ASR 耗时、LLM tokens/s、TTS 耗时 | **需新增埋点** | 高 | 成本最高，建议 Q30 之后再说 |

**推荐首屏：A + B + C**（三块都能用现成数据，无需新埋点，直接对准内存溢出与窗口上限两条已发生的事）。

## 4. 布局（380 px 宽，最低 1080p）

```
┌ side-panel (380px) ─────────────────────────────┐
│ [工具][实时][快捷][设置][监控]   ← 第 5 个 tab    │
├─────────────────────────────────────────────────┤
│ 提交 28,990 · 已用 16,581 · 可用 12,408 MB       │  ← A：一行大数字
│ ▓▓▓▓▓▓▓▓░░░░░░░  57%        （提交占用条）       │
│ 物理内存 57%   CPU 12%                            │
│ ● 唤醒  ● 语音识别  ● LLM  ● TTS                 │  ← B：复用 .svc-lamp
├─────────────────────────────────────────────────┤
│ 我起的浏览器窗口 1 / 3                            │  ← C：上限联动
│ jarvis 2,004 · api_v2 6,518 · llama 4,522 ·      │
│ chrome 13 进程 3,139 MB                          │
└─────────────────────────────────────────────────┘
```

- 数字用等宽感（tabular）呈现，避免跳动时行宽变化；单位统一 MB，**≥1024 MB 显示 GB 保留 1 位小数**
- 颜色语义复用三态：`可用 ≥2,000 MB` → `on`（粉），`300–2,000 MB` → `warm`（gold），`<300 MB` → `--danger`
  （**这条线来自实测**：可用 237 MB 那次就是出事的那次）
- 空态文案与现有一致（`等待工具调用` / `记录待机` 风格），Monitor 空态：`等待第一次采样`

## 5. 数据流与 payload（设计级 schema）

**采样在 jarvis 侧**（你的会话里跑，`start_all.bat`），不是前端拉 WMI。

- 新端点 `GET /api/monitor` → 单次采样，返回同一 payload（供 curl 验收与前端首轮渲染）
- **推荐 WS 推送**：服务端后台线程每 **5 s** 采样一次，广播新类型
  `{"type":"monitor", "ts":"2026-11-17 10:24:25", "commit":{"total":28990,"used":16581,"free":12408}, "phys_pct":57, "cpu_pct":12, "lamps":{"wake":true,"asr":true,"llm":true,"tts":true}, "windows":{"mine":1,"limit":3,"titles":[...]}, "procs":[{"name":"jarvis","pid":1234,"commit_mb":2004}]}`
  （payload 约 1–2 KB，5 s 一轮 ≈ 12 KB/min，可忽略）
- **节流**：`document.hidden` 时前端不渲染、服务端可降频到 30 s；页面不可见时不停止采样会导致无谓开销
- **历史曲线（可选，Q30 第 4 点）**：环形缓冲 120 样本（5 s × 10 min）≈ 1 KB，canvas 手绘 2px 高 sparkline；
  要更长历史（1 h @5 s = 720 样本）仍是 KB 级，**不是内存瓶颈**；瓶颈在 jarvis 自身 2,004 MB 提交，与曲线无关

**采样成本与边界（实测口径）**：一次 `Win32_OperatingSystem` 查询数十毫秒；`Win32_Process` 全枚举在 13-25 个 chrome 进程时约 100–300 ms，
放后台线程、**不阻塞 WS 与语音链路**（语音 20 轮判据不能被采样拖慢）。沙箱里我的 pwsh 用 PowerShell 自带 pipeline 测过同样查询，可用。

## 6. 无障碍与文案（延续 2792acf 的口径）

- 数字面板 `aria-live="off"`（每 5 s 变动的数字会让读屏器刷屏）；**只有一条摘要行** `aria-live="polite"`
  （`可用 12,408 MB · 我起窗口 1/3 · 四灯全亮`）
- tab 标签中文，和页面 `lang=zh-CN` 一致（2792acf 的教训：英文 `data-cmd` 让中文页里的用户气泡变成英文）
- 每个数字块有中文标签与 `title` 提示（沿用 `.svc-lamp` 的 title 语义写法）

## 7. 验收（验证 3 轮，`tests/<ts>_cc/`）

1. **数字对得上**：面板显示与同时刻手动 `Get-CimInstance Win32_OperatingSystem` 读数一致（±1%）
2. **上限联动**：我起的窗口数与 `manage_browser_windows()` 报的数量一致（现测 1/3）
3. **节流生效**：页面隐藏时不再推送/渲染（记录时间戳间隔）
4. **无副作用**：jarvis 提交内存连续 30 min 增长 < 50 MB；语音链路不被采样拖慢
5. 面板**没有任何动作按钮**（设计约束，代码审查确认）

## 8. 实现拆分（Q30 答复后才做，本轮不写）

- `jarvis/monitor.py`（新模块，采样 + 缓存最近 payload；风格跟 `events.py` 的短事务模式）
- `jarvis/web.py`：`GET /api/monitor` + 后台采样线程 + WS `monitor` 广播
- `jarvis/static/index.html`：第 5 个 tab `data-tab="monitor"` + `#tab-monitor` + 渲染函数 + `--danger` 令牌
- 前端事件类型在 `L592-664` 的 `switch` 里加 `monitor` case（与 `tool`/`tool_result` 同层）

## 9. 风险

- WMI 全枚举在你的会话里可用（我沙箱的 pwsh 也测过），但**在沙箱里跑 jarvis 时键盘注入落在沙箱窗口站**（已量过）→ Monitor 的验收必须在你的会话里做
- 采样线程若异常（WMI 抖动）必须**如实显示"采样失败 + 原因"**，不能显示上一次的数字装作正常（虚假成功预防）
- `chrome` 进程数与窗口数不是一对一（13-25 进程 / 1-6 窗口）→ 面板必须写"进程数"与"窗口数"两件事，不能混说
