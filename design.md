# 总设计

- **版本**：v3.2 —— **v3.1 已归档到 `ai_buckup/design.md_2026-11-21-18-27-30.md`**（v3.0 在 `ai_buckup/design.md_2026-11-20-22-14-46.md`，v2.0 在 `ai_buckup/design.md_2026-11-17-10-44-33.md`，v1.0 在 `ai_buckup/design.md_2026-11-17-10-24-25.md`）
- **更新时间**：2026-11-21-18-27
- **v3.2 唯一变化**：新增 §3-5 **分页标签**（照你 18:27 逐字「在页面最顶部添加分页标签,允许切换主界面,monitor(监视界面),about(相关页面)」）——三页共用一条顶栏、当前页高亮、新增 `/about` 路由；§6 验收随之补第 10 条。其余照 v3.1 不动。
- **v3.1 变化（照旧保留）**：启动脚本定案为**两版并存**（照你 22:14 逐字「保留原start_all,写新start_all_in_one.bat」）——新增 §8，§4 第 4 项、§6 第 9 条、§7 补一条随之改。
- **关联需求（v3.2 新增）**：`records/2026-11-21-18-27-30.md`（18:27 分页标签三页）
- **关联需求**：`records/2026-11-17-10-24-25.md`（「在 UI 中制作一个 moniter 界面」「先做 design，不开工」）
  + `records/2026-11-17-10-44-33.md`（Q30 答复：**Monitor = 日志中枢 + 单窗口托管 + 指定关闭 + 外部接入**）
  + `records/2026-11-20-22-14-46.md`（22:14：**保留原 `start_all.bat`，新写 `start_all_in_one.bat`** → §8）
- **状态**：**只 design，未开工**（你 22:14：「记录后停工，明天开工」）。开工授权与关闭授权见 `need_user.md` **Q31（status: wait）**。

## 1. 你 10:44 的原话与逐条可行性（不假装都能做）

> 「f 这个其实是最重要的, Monitor 我希望的是将启动的所有 cmd stdout 全显示在这个界面上,
> start_all.bat 启动后就一个窗口, 关闭窗口直接全部关闭, monitor 中允许关闭指定的服务, 从别的地方启并接入」

| 需求 | 可行性（依据） | 设计结论 |
| --- | --- | --- |
| **显示所有启动 cmd 的 stdout** | **只有 jarvis 是父进程时抓得到管道**。现在 `start_all.bat` 用 `start ... cmd /k` 给每个服务开自己的控制台，stdout 归那个控制台，**jarvis 抓不到** | jarvis 必须成为 llama-server / api_v2 的**父进程**（`stdout=PIPE, stderr=STDOUT`）；`start_all.bat` 不再为服务开窗口 |
| **start_all 后只有一个窗口** | 现 `start_all.bat` 开 **4 个窗口**（llama / GPT-SoVITS / jarvis / status panel，实测文件内容） | 只留 jarvis 一个窗口；status panel 的 powershell 循环被 `/monitor` 页面取代 |
| **关闭窗口直接全部关闭** | **不能靠控制台语义**：用管道起的子进程**不挂在控制台上**，关父窗口它们会活着。`taskkill /T` 杀进程树可行（`manage_browser_windows` 已用） | jarvis **退出时按记录的 pid 主动杀子进程**（`atexit` + `SIGBREAK` 处理，Windows 关控制台后只给约 5 s 清理窗口）；每次起子进程把 pid 落盘 `.tmp/jarvis_child_pids.json`（复用 Q29 的 pid 记录模式） |
| **从别的地方启并接入** | Windows 下**无法事后接管别人进程的 stdout**（无 ptrace 这类机制） | 接入 = **识别 + 体检**：按命令行匹配找 pid、读 `PageFileUsage`、探 `:8080/:9880` 健康；面板必须写明「外部进程：无日志接管」——**不显示假日志** |
| **面板允许关闭指定服务** | 可行（`kill_process` 已有，`taskkill /PID /T /F` 已实测） | **撤销我 v2.0 立的「面板不做动作」非目标**（那是我防虚假成功的规矩，你明确要控制）。关闭按钮必须带 **pid 证据 + 点击前确认**，禁止静默杀 |

## 2. 已定内容（Q30-1 多选：A + B + C + E + F，F 最重要）

| 块 | 内容 | 数据来源 | 备注 |
| --- | --- | --- | --- |
| **G 日志中枢（新，最核心）** | 每个服务的 stdout/stderr 逐行，带服务标签与时间戳 | jarvis 子进程管道 + 自身日志 | 每服务环形缓冲 **2,000 行**（防内存涨）；WS 每轮最多 20 行批量 |
| **F 语音链路指标（你说最重要）** | wake 置信度 / ASR 耗时 / LLM tokens 每秒 / TTS 耗时 | **需新增埋点**：`main.py` 唤醒（`L548` 附近）、转写（`L627` 附近）、回复（`L668` 附近）、`tts.py` 合成前后打点 | 无埋点则这块只能是空壳，如实标注 |
| **A 资源仪表** | 提交 上限/已用/可用 MB、物理%、CPU% | `Win32_OperatingSystem` + CPU 采样 | 颜色安全线取实测（可用一度 237 MB）：≥2,000 粉 / 300–2,000 gold / <300 新增 `--danger` |
| **B 服务健康四灯** | wake / asr / llm / tts | 现有 `/api/health` 的 `_tcp_probe`（`web.py`） | 复用 `.svc-lamp` 三态 |
| **C 进程与窗口清单** | 各服务 pid + 提交 MB；我起的浏览器窗口数（上限 3） | `Win32_Process` 命令行匹配 + `_browser_windows()`（`app_control.py`） | 与 Chrome 管理器 ≤3 联动 |
| **E 工具调用统计** | 每工具调用次数、耗时、失败率 | `main.py L404/410/453/458` 的 tool/tool_result 广播侧写 | 对"点不进/没跳转"这类诚实失败最有用 |

## 3. 独立页 `/monitor`（Q30-2 选定，1080p 起）

`index.html` 现 1001 行、`body{overflow:hidden}`（`L25` 区域）、side-panel 380 px（`L186`）。
独立页沿用同一配色令牌（`--pink/--pink-2/--gold/--lilac/--text/--text-dim`，`L10-13`）与 `.svc-lamp` 三态。

```
1920×1080（最低 1080p，不做窄窗口）
┌ /monitor ──────────────────────────────────────────────┐
│ 提交 28,990 · 已用 16,581 · 可用 12,408 MB   ▓▓▓▓▓░ 57% │  ← A
│ ● 唤醒 ● 语音识别 ● LLM ● TTS      我起窗口 1/3          │  ← B + C
├ 服务（pid / 提交 MB / 来源 / [关闭]）───────────────────┤
│ llama-server  15600  4,522 MB  jarvis 起   [关闭]        │  ← C + 控制
│ api_v2        13756  6,518 MB  jarvis 起   [关闭]        │
│ jarvis        11222  2,004 MB  本进程      ——            │
│ chrome 13 进程 3,139 MB  我起窗口 1/3                    │
│ 外部接入：ffmpeg 4412  120 MB  外部起 · 无日志接管        │  ← 接入=识别
├ 语音链路 ── LLM 18 tok/s · ASR 1.2 s · TTS 1.9 s ·      │  ← F（埋点后）
│ wake 0.81  曲线 5s×10min ▁▂▃▂▅▆                          │
├ 工具统计 ── 播放第一支视频 3 次 · 失败 1 · 均 11.4 s      │  ← E
├ 日志区（每服务可折叠，最新在上，2,000 行环形）───────────┤
│ [llama] slot prompt 712/16384 ...                        │
│ [tts]  合成 1.9 s → 24kHz mp3 42 KB                      │
│ [jarvis] 已在被聚焦的窗口导航：基准「…」-> 现在「…」      │
└ 推送间隔 [1s ▾]  ← 前端可调（Q30-3，最低 1 s）───────────┘
```

- **推送间隔前端可调**（Q30-3 原话「推送间隔允许前端修改，最低可以设置成 1s」）：UI 下拉 `1/2/5/10/30 s`，
  存 localStorage，通过 WS 首条 `{"type":"monitor_config","interval":5}` 告知服务端；服务端采样与推送同一节拍
- **节流**：`document.hidden` 时服务端降到 30 s（省 CPU），前端停渲染
- **曲线**：环形 120 样本（5 s × 10 min）≈ 1 KB，canvas 手绘，无图表库

### §3-5 分页标签（v3.2 新增，照你 18:27 逐字）

> 「在页面最顶部添加分页标签,允许切换主界面,monitor(监视界面),about(相关页面)」

- 三页：**主界面** = 现成的 `/`（`jarvis/static/index.html`）、**monitor** = 现成的 `/monitor`、**about** = 新页（现无 `/about` 路由，本版本新增）。
- 顶栏**三页共用一份**（`tabs.css` + `tabs.js`），不在每页手写，避免三份漂移；当前页高亮，点击即切页（真跳转，不是隐藏/显示同一页的块）。
- `about` 内容照实，只写已实现的事实：组件与端口表（jarvis 7860 / llama 8080 / GPT-SoVITS 9880 / Umi-OCR 50015）、唤醒模型与阈值（`aili_xiya_v1.3.onnx` / 0.75，**不可改**）、埋点口径（`asr_secs`/`llm_secs`/`llm_chars`/`tts_secs`/`wake_peak`，**tokens/s 未埋**）、design 版本与归档位置、台账文件位置（`records/` `tests/` `progress.md` `tree.md` `hard_bug.md` `need_user.md`）、照实的**未测项清单**。不写没实现过的功能。

---

## 4. 架构改动（开工后的实现拆分，Q31 未答复前不写）

1. **`jarvis/services.py`（新）**：`launch(name) -> pid`（`Popen(..., stdout=PIPE, stderr=STDOUT)`）+ 每服务读线程 →
   `RingBuffer(2000)`；pid 落盘 `.tmp/jarvis_child_pids.json`（复用 Q29 模式）；`shutdown()` 按 pid `taskkill /PID /T /F`，
   每个 kill 记录成败文本（`manage_browser_windows` 的现成口径）
2. **`jarvis/main.py`**：启动时 `launch("llama")` / `launch("tts")`（若端口未被占用；`start_all.bat` 的
   `netstat` 检查逻辑移到 jarvis 侧，**外部已起的服务走接入识别，不重复起、不杀**）；`atexit` + `SIGBREAK` 挂 `shutdown()`
3. **`jarvis/web.py`**：`GET /monitor`（页面）+ `GET /api/monitor`（快照）+ WS 类型
   `monitor`（指标）/ `log_batch`（≤20 行）/ `monitor_config`（间隔）+ `POST /api/service/stop`（body `{"name","pid"}`，
   **只接受 jarvis 自起 pid**，外部 pid 返回"拒绝：不是本进程起的"）
4. **启动脚本（22:14 定案：两版并存，见 §8）**：**`start_all.bat` 原样保留、不改**（现 4 窗口；`cmd /k` 起的进程 stdout 归各自控制台，jarvis 抓不到；status panel 的 powershell 循环继续存在）；
    新写 **`start_all_in_one.bat`**：只开 **1 个窗口**（jarvis），jarvis 作父进程起 llama-server / api_v2（`stdout=PIPE, stderr=STDOUT`），浏览器开 `/monitor`。
5. **`jarvis/static/monitor.html`（新页面）**：布局如上；日志区每服务折叠，最新在上；
   每行 `[服务] 原文`；控制按钮带 pid 与确认
6. **埋点**：`main.py` 唤醒/转写/回复、`tts.py` 合成耗时 → 同一环形缓冲（各 200 样本）供 F 块

## 5. 控制授权（撤销「面板不做动作」后的新规矩）

- **关闭按钮只对 jarvis 自起的 pid 生效**（`POST /api/service/stop` 校验 pid 在 `jarvis_child_pids.json` 里）；
  外部起的进程**面板不给关闭按钮**，只给"识别 + 体检"（Q24/Q29 的边界：你的浏览器与你的进程我不动）
- **点击前确认**：弹一层「要关 llama-server（pid 15600，4,522 MB，jarvis 起的）？确认/取消」，
  **不静默杀**；结果行必须回显 `taskkill` 真实输出（成功/失败），失败时保留行，不显示"已关闭"
- jarvis 退出关全部：**只杀记录里的 pid**，退出时把每条 kill 结果写入日志区并落盘 `.tmp/jarvis_shutdown.log`

## 6. 验收（验证 3 轮，`tests/<ts>_cc/record_1..3.md` + `opinion.md`）

1. **单窗口**：`start_all.bat` 后**只有 1 个窗口**；`Get-Process` 里 llama-server/api_v2 的父进程是 jarvis
2. **关窗口全关**：关闭该窗口后 `7860/8080/9880` 全部不通（现口径），`.tmp/jarvis_shutdown.log` 有每条 kill 证据
3. **日志真可见**：日志区出现 llama 的 `slot prompt ...` 行与 TTS 合成行，内容与各自控制台原文一致
4. **接入诚实**：外部起的进程显示"外部起 · 无日志接管"，**没有假日志**
5. **控制边界**：外部 pid 的关闭请求被拒（返回"不是本进程起的"）；jarvis 自起 pid 关闭后端口不通
6. **间隔可调 1 s**：UI 选 1 s 后 WS 推送间隔实测 ≈1 s；隐藏页面后降频
7. **内存**：日志环形 2,000 行/服务下，jarvis 提交 30 min 增长 <50 MB
8. 语音 20 轮判据不被采样/日志拖慢（轮 11-20 仍等你在麦克风前）
9. **两版并存不互相破坏**（§8）：先跑 `start_all.bat` 再起 `start_all_in_one.bat` 时，端口检查照现逻辑**跳过已起的服务**（不重复起、不杀），面板把它们标成「外部起 · 无日志接管」；`start_all.bat` 的 4 窗口行为与今天完全一致
10. **分页标签（v3.2）**：三页顶部都有同一份顶栏、当前页高亮、点击切页后 URL 与页面对应；**必须真开浏览器看渲染与 console**（v3.1 的验证轮只测了「页 200 + 标题命中」，被你的截图打穿过一次：JS 转义语法错导致整页不执行）

## 7. 风险与边界（如实）

- **CTRL_CLOSE_EVENT 只有约 5 s 清理窗口**：`shutdown()` 必须轻（只杀 pid，不做长 I/O）；**这条必须在你会话实测**，
  我沙箱里量不了关控制台的行为
- **管道在沙箱里不可用**（我的子进程无 piped stdio，EPERM）→ 日志接管只能在你的会话验证；沙箱里我可以验
  环形缓冲、WS 推送节奏、pid 记录与 kill 证据文本
- **stdout 缓冲**：llama 的进度行是 `\r` 回车覆盖式，管道读到的是一串连续块 → 日志区必须按 `\r` 断行处理，
  否则一行刷屏
- **GPT-SoVITS api_v2 由 jarvis 起时工作目录与 env 要照 `start_all.bat` 现内容设**（`cd /d GPT-SoVITS-main`、
  `MPLCONFIGDIR`、`HF_ENDPOINT=https://hf-mirror.com` 带 scheme，HB-029）
- **语音/播放判据不能被架构改动破坏**：现役 `aili_xiya_v0.9b.onnx` + `thr 0.75`（2026-11-20 12:33 换，commit 853205；部署 3 轮验收仍未测）、`stt.engine: whisper`、
  `stt.hot_bias: false`、`is_half: false` 不动；**丙方案与轮 5-6 的实测仍等你跑 `start_all.bat`**
- **两版并存的代价照实（§8）**：`start_all.bat` 起的进程 **jarvis 不认 pid**（不是它起的）→ 面板不给关闭按钮、无日志；
  「关窗全关」只在 `start_all_in_one.bat` 版里成立；旧版 4 窗口（含 status panel）继续可用，**不做「自动升级」**


## 8. `start_all_in_one.bat`（2026-11-20 22:14 新增，照你的话）

> 逐字：「monitor加一条start_all改版->保留原start_all,写新start_all_in_one.bat」

**名字照你给的原样，不自行发明命名。** 两版并存，互不替代：

| 脚本 | 状态 | 窗口 | stdout | 关窗全关 | 关闭按钮 |
| --- | --- | --- | --- | --- | --- |
| `start_all.bat` | **保留，不改一个字节** | 4 个（llama / GPT-SoVITS / jarvis / status panel） | 归各自 `cmd /k` 控制台，jarvis 抓不到 | 不成立（各窗口各管自己） | 无（jarvis 不认这些 pid） |
| `start_all_in_one.bat` | **新写** | **1 个**（jarvis） | jarvis 管道（`stdout=PIPE, stderr=STDOUT`）→ 日志中枢 G 块 | 成立：jarvis 退出按 `jarvis_child_pids.json` 只杀自起 pid | 只对自己起的 pid |

**新脚本的硬要求（照现 `start_all.bat` 的实测写法，不凭记忆）**：

1. 全 **ASCII + CRLF**（自曝第 52 处：我用 latin1 写中文进 bat，字节里出现控制字符 0x13 → 窗口「命令语法不正确。」）。
2. 全 **`%~dp0` 相对路径**，不写绝对路径（现 `start_all.bat` 的 `cd /d %~dp0` 模式，迁移后不受影响）。
3. 路径照实测：llama = `llm\llama-b12144-bin-win-vulkan-x64\llama-server.exe`（**不是** `.venv-llama\Scripts\llama-server.exe`，那个路径不存在——自曝第 52 处）；GSV = `..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py`，工作目录 `cd /d %~dp0GPT-SoVITS-main`；jarvis = `.venv\Scripts\python.exe -u -m jarvis.main`。
4. **env 照现内容全带上**：`MPLCONFIGDIR=%~dp0.tmp\mplconfig`、`HF_ENDPOINT=https://hf-mirror.com`、`HF_HOME=%~dp0.hf-cache`、`HF_HUB_DISABLE_XET=1`、`GGML_VULKAN=1`。自曝第 48 处：我拼的 env 缺 `ALLUSERSPROFILE`，代码把 `%ALLUSERSPROFILE%` 当字面路径，在**项目根**造出 `Tencent\...\QQPCMgr\` 垃圾目录（16:xx 删过，21:45 又出现）。
5. `-c 24576` 与其余 llama 参数照现内容**一个不动**（Q33 你授权的就是这一处，已落地 `start_all.bat`:19）。
6. 端口检查照现 `netstat -ano | findstr ":PORT" | findstr "LISTENING"` 的语义移到 jarvis 侧：已起 = 不重复起、不杀、走「接入识别」。
7. jarvis 起浏览器开 `/monitor`；**不最大化窗口**（照长期边界）。

**验收照 §6 第 1/2/3/4/5/9 条**；「关窗全关」必须在**你的会话**实测（`CTRL_CLOSE_EVENT` 只给约 5 s，我沙箱量不了）。
**顺带补上的取证面（HB-052 / 蓝屏 P2 等复现）**：管道里的 stdout 落 jarvis → 蓝屏前的指令文字才可能留证；旧版仍不落文件。
