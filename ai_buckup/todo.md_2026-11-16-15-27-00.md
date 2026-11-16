# Todo

<!-- 已归档于 ai_buckup/todo.md_2026-11-13-14-22-30.md（108 行全量，含 11-13 09:00 开工清单、11-12 各批唤醒训练结论、通用规矩、看屏幕取消节、12-25-43 修复节、12-59-10 二十轮两节、13-46-12 应用表节、14-08 ASR 容错节、14-22 拼音索引节）。本文件为压缩版：保留全部未完成项 + 已结案批次要点。 -->

## 通用规矩（长期，勿违反）

- [ ] 每批：先落 `records/` + `todo.md` 再开工；测试 20 轮（明确）/ 3 轮（验证）并写 `tests/opinion.md`
- [ ] 零截图；不用子智能体（未询问）；commit 中文主题（type/scope 英文）+ hash 追加台账 + **禁止 push**
- [ ] `progress.md` / `todo.md` > 100 行先归档再压缩；`tree.md` 文件增删后重建（仅非 `.gitignore`）
- [ ] 打分/训练前停掉 `:7860/:8080/:9880`（虚拟内存是硬约束），跑完重启 + 4 灯复核；每个 python 跑都带 `HF_ENDPOINT=https://hf-mirror.com` + `HF_HOME=<repo>\.hf-cache` + `HF_HUB_DISABLE_XET=1` + `MPLCONFIGDIR`
- [ ] 边界样本必须 ≥3 个独立 Model 实例复测取多数（HB-032）

## 2026-11-13-14-22 拼音索引层（→ records/2026-11-13-13-46-12.md 追加节）

- [ ] `apps` 加 `py` / `py_tone` 两列，`populate()` 写入，`ALTER TABLE` 幂等升级已有表
- [ ] 拼音直达层：查询是纯字母串时与 `py` 比对（完全相等→命中，前缀/包含→候选），优先于音近层
- [ ] 音近层改为**读索引列**算相似度（不再每次现算 227 次 pypinyin）
- [ ] 验证 3 轮零截图：① `open_app('jishiben')` → 记事本 + 复读 `notepad`；② `open_app('话图')` → 画图 + 复读 `mspaint`；③ `open_app('jishib')` → 不打开、返回候选

## 2026-11-13-13-46-12 应用列表入库 + `open_app` 先匹配（已完成 → records/2026-11-13-13-46-12.md）

- [x] 扫开始菜单（`%APPDATA%` + `ProgramData`，`WScript.Shell` 解析 `.lnk`）灌入 `events.db` 的 `apps` 表：**227 条**（58 条中文名，5 条无 target 跳过），`name/norm/aliases/launch/args/kind/hits/last_used`；`main.py` 启动时幂等 `populate()`
- [x] `open_app` 三段：① 先匹配表（精确→唯一子串→音近）；② 不匹配才走 `APP_MAP`/补 `.exe`/`PATH`；③ **复读到进程出现才算成功**，失败带原因。3 轮 PASS（`记事本` 匹配 + `hits` 增加、`foobarapp` 如实失败、多候选不乱选）
- [x] ASR 容错层（14:08 节全部完成）：字符 Levenshtein + `pypinyin` 带调/无声调，阈值写死（高置信 ≥0.66 且 gap ≥0.12 → 打开并登记别名；0.45-0.66 或候选接近 → **不打开、返回候选**；<0.45 → 其它路径）；`app_queries(raw, matched, ts)` + 别名自学习。工具级 3 轮 PASS：「计时本」→ 记事本（别名 `["notepad","计时本"]`）、「话图」→ 画图、「控置」→ 候选且**无进程启动**（`control.exe` None）、「foobarapp」→ 音近够不上、如实失败
- [x] 服务级 6 轮（14:17-14:20，浏览器打字，零截图）：「打开计时本」→ `已打开：记事本（从应用列表匹配，复读确认进程 notepad）`；「列出窗口」→ 中文标题「无标题 - 记事本」；「打开控置」→ 模型自己规范化成 `settings`，撞 `Settings`/`设置` 两候选，工具**如实拒绝选**、无进程启动；「打开话图」→ 模型理解成 `chatgpt`，工具如实报「227 条里没有、本机也找不到可执行文件」（**没假成功**）
- [x] **已修（14:19 服务级暴露）**：同一个程序的两种写法被当「2 个候选」（`Notepad`=`C:\Windows\system32\notepad.exe` vs `记事本`=`notepad.exe`）→ 改成按 **exe 文件名**判同，并优先 `hits` 高的那条
- [x] **已修**：`get_open_windows` 残留 `text=True`（UI 历史「列出窗口」的 `'NoneType' ... strip'` 就是它）→ UTF-8 + returncode 检查，空输出算合法结果
- [ ] **如实边界**：模型会把听到的词**规范化成它认为的应用名**（「话图」→`chatgpt`、「控置」→`settings`），所以音近层在语音链路上主要作用于**表内名字的音近**（「计时本」→ 别名精确命中）；同音撞车（微星/微信 拼音相似度 0.86）时宁可不打开、让爱莉希雅问一句

## 待修 / 待确认（跨批次）

- [ ] **HB-040**：`_coerce` 把可选参数的默认值架空（`set_timer` 的中文默认文案「定时到了！」被空串覆盖）
- [ ] **`find_on_screen` 中文匹配方式**（WinRT OCR 字间插空格 + 有错字 → 按空格分词算 overlap 基本匹配不上）
- [ ] **`lock_screen` 真锁屏**（已授权，拆到收尾，等你说「锁」；Q20）
- [ ] **通知气泡肉眼确认**（Q19）；**剪贴板 JWT 覆盖的善后**（Q18）
- [ ] `kill_process` 的进程名必须是**英文进程名**（中文被洗成空串 → `taskkill /IM .exe`），schema description 该写清
- [ ] `pyautogui.FAILSAFE = False` → `click_at`/`move_mouse` **没有越界保护**，坐标必须受窗口位置约束

## 20 轮明确测试语音部分（`tests/2026-11-08-20-44-17_cc/`）

- [ ] **轮 11-20 需你在麦克风前配合**（打断三态 / 近音「米雅·爱莉雅·希雅老师」/ 安静 5 s + 轻敲期望 **0 检出** / 空转录必须播 `ack_no_heard` / 长句 8 s 完整不截断）。轮 1-10 已跑完（1-4 PASS、5 部分、6-10 FAIL），采样器 `pwsh-39` 每 1.5 s 写 `.tmp/sampler_health.log`
- [ ] `need_audio.md` §5 缺口（干净呼唤 ≥20、带噪 ≥10 分文件、竞品真人句 ≥4、无关短句 7→10）→ 重训 v1.0d（召回短板 = 音节窗正样本仅 45 件）
- [ ] 可选：共享你正在看的那个页面（需你启带 CDP 的 Chrome `--remote-debugging-port=9222`，我不代启）

## 等用户 / 需授权 / 延后（历史遗留）

- [ ] 2026-10-13-11-45 三问题排查收尾（剩余：用户对新进程实测唤醒）
- [ ] 2026-10-14-22-23-49 TTS 迁移 SoulX-Podcast（本轮不做，仅记录）
- [ ] 2026-10-17-19-11-07 README 中文化 + 来源声明 + 仓库更名 AI_Elysia + LICENSE + push（禁 push，需用户操作）
- [ ] 2026-10-13-21-38-01 T4 仓库私有化 / 描述改「自用」（需用户手动，已确认延后）
- [ ] 2026-11-08-12-08-49 `AI_Benchmark.md` 继续补测更多模型（T14 decode 仅 2B/IQ3 已测）

## 已结案批次（压缩，明细见归档与 `tests/`、`records/`、`ai_buckup/onnx_opinion.md`）

- **唤醒谱系结论**：`v0.4` rec 0.50 → `v0.5` **rec 0.00 塌陷** → Q8 重标 → `v0.6`（真人 rec 1.00 / 带噪 0.83）；15 件真人负样本 → **v0.9 采用 + 阈值 0.75**（12 / 近音 fp 6 / 无关 2 / 对抗 4 / 长噪 1 / 环境 0）；`v1.0` Recall 0.3009 未采用；`v1.0b` 0.6106 未采用；`v1.0c` 0.5865，**可用区间 0.70-0.72、最佳 0.72**（判别轴首次达标：近音 fp 1 ✓、对抗 3 ✓、定标/环境 0 ✓；召回轴塌 → 不采用）。**0.65 禁区**（两模型环境音均检出，违反期望 0）。环境音期望必须 **0**。「真人近音 fp ≤1」**未达标**（阻塞补录）。**多音色是召回轴不是判别轴**；高分在尾音衰减/静音窗，不在音节。
- **裁决与默认值**：`stt.engine` 保持 **whisper**（sherpa 天花板 = 近音声学判别）；`stt.hot_bias` 默认 **false**（实测有害）；sherpa 能量门 `span` + THR 0.008 落地；`ack_no_heard` 入 RAM 具名池只接空转录/低质量转录；`hot_phrases` 表上限 200；favicon 与 `/favicon.ico` 路由（console 0 error）。
- **已结案工具批**：20 轮 32 工具全过（`tests/2026-11-13-12-59-10_cc/`，5 条虚假成功封住、`delegate_task` 摘除、工具数 32/32）；`tests/2026-11-13-12-25-43_cc/` 3 轮 PASS（HB-033 音量、HB-034 屏幕 GBK、HB-035 天气 ascii）。
- **已取消**：看屏幕改走浏览器快照（11:20 用户纠正 —— 「零截图」边界是 Agent 会话，爱莉希雅全本地，OCR 路径不动）；浏览器共用插件已实测可实时看界面（无需 9222）。

## 2026-11-16-11-46-56 用 dsh-builtin-browser 插件确认并优化 UI 设计（→ records/2026-11-16-11-46-56.md）

- [ ] 确认插件：`plugin_manager` 列 profile 里的插件，`dsh-builtin-browser` 存在且 enabled；`dsh_browser_session` 建会话
- [ ] 重启服务（`:7860` + `:8080` + `:9880`）并复核 4 灯 online，才能验证 UI（四任务都被用户 killed）
- [ ] 用**零截图**读法理解页面：`dsh_browser_a11y` / `snapshot` / `content` / `state`；视觉参数用 CSS 计算值（`getComputedStyle`），不用 `dsh_browser_screenshot`
- [ ] 列出用户视角的真实问题（结构、可读性、状态可见性、交互、WS 实时性），**不自行发明设计方向**
- [ ] 逐条改 CSS/HTML，每条 3 轮验证（文本证据）→ `tests/2026-11-16-11-46-56_cc/` + `opinion.md`
- [ ] 不碰现役唤醒配置（v0.9 + 0.75，Q16/Q17 裁决）
- [ ] 布局改 flex 列 + 3 档断点（≤1000 / ≤780 / ≤520），去掉 `calc(100vh - 92px)` 硬假设，`min-width:0` 防挤压
- [ ] `send()` 判 `ws.readyState === 1`；断线时明确提示「消息未发送（每 3 秒自动重连）」并**保留输入文本**（不清空）
- [ ] 12 个快捷按钮换中文指令，目标必须是应用表里真实存在的程序（Spotify 不在表里 → 去掉「播放音乐」）
- [ ] 活动条默认文案改中文「处理中…」，去掉 `toUpperCase()`
- [ ] 可访问性：`#messages`/`#statusText` 加 `aria-live=polite`，`#modelSelect`/`#muteBtn`/`#input` 加 `aria-label`
- [ ] 3 轮验证（零截图）：① 560×520 量输入栏可见 + 输入框宽 > 200 + 无水平溢出；② readyState≠1 时发送出现「消息未发送」气泡、文本保留；③ 点「时间」气泡是中文，`[aria-live]` 计数 ≥ 2、`select` 可访问名是标签

## 2026-11-16-12-18 用户 5 条约束（→ records/2026-11-16-11-46-56.md 追加节）

- [x] ~~窄窗口断点三项~~ **撤掉**（用户：窄窗口 UI 不用管，默认最低 1080p）。560×520 的测量数据保留为已知边界
- [x] ~~启用 `ui-sidebar-browser` 面板~~ **取消**（用户：共用浏览器是独立窗口，我本来就能看到；我 12:12 的推断是错的，已如实更正）
- [ ] 播放音乐改走 **浏览器 + B 站搜索播放**（Spotify 路线删掉）；3 轮判据：搜索页 → 视频页 → 播放器存在、时长非 0
- [ ] 允许**少量、局部小截图**（用 `maxWidth/maxHeight` 压小）；读页面结构仍首选 a11y
- [ ] **优化提交量（commit charge）**：先量各进程 `Page File Bytes` / 私有提交，找前 5 名，逐项改并复测同一口径的「已提交」数字，必须有实测下降
- [ ] 改完 4 灯 online + 现役 v0.9 + 0.75 不动；语音 20 轮判据不得放宽

## 2026-11-16-12-33-59 六条需求按 1→6 开工（→ records/2026-11-16-12-33-59.md）

- [x] 1 窄窗口 UI：**无代码工作**（撤规则）
- [ ] 2 播放音乐改 **浏览器 + B 站搜索播放**；删「播放音乐 / Open Spotify」英文指令；3 轮判据：搜索页 → 视频页 → 播放器存在 + 时长非 0
- [x] 3 dsh-builtin-browser 独立窗口：**无代码工作**（撤启用面板待办 + 已如实更正）
- [x] 4 允许少量局部小截图：**无代码工作**（判据口径）
- [ ] 5 内存提交量优化：已量得 llama 去 `--mmproj` + `-c 16384` → `PF 3866→2339MB`、系统提交 `32114→30761MB`、可用提交 `461→1814MB`（4 灯 online、v0.9+0.75 未动）
  - [ ] 待授权的补偿：`python.exe -m src.server`（`F:\2D23D\venv`，**不是 jarvis 的东西**）占 **1,291 MB 提交、工作集仅 6 MB** → **Q21**（只允许我结束它？授权范围同 kill_process 的先存后还）
  - [ ] 页面文件 `InitialSize=16MB`（上限≈8 GB，提交上限 32,575 MB = 物理 24,383 + 约 8 GB）→ 增大页面文件是系统级改动，**Q22** 需你/admin 执行
  - [ ] TTS `is_half: false` + `device: cpu`（fp32 全在内存）：试 `is_half: true` 的量与速度 3 轮，不许只看省的量
- [ ] 6 视觉塔 + 多模态截图 + 保留 OCR：`llama.ps1` 恢复 `--mmproj`、`llm.py` 支持图片消息、新增 `describe_screen` 工具（参数规则写在参数上）、`read_screen` 保留；3 轮判据见 record

- [x] `open_url` 假成功已修（HB-044）：`webbrowser.open` 返回值不再被丢掉；改用应用表浏览器真路径 + `--new-window` + **进程内 ctypes 复读到窗口标题**才算成功，读不到如实报
- [x] `desktop.py` 窗口证据改进程内 ctypes（HB-045）：`_visible_windows()` + `get_open_windows` + `focus_window` 不再起 powershell 子进程（子进程看 0 窗口）、不再用 `Add-Type`（沙箱拒）
- [ ] **Q25**：第 2 条（浏览器→B站搜索→播放）真端到端必须由你在沙箱外跑 jarvis 验（沙箱内 python 起的进程不能产生可见窗口）
- [ ] **Q24**：pwsh 启动的 B 站窗口（进程 8228）要不要关？`kill_process` 授权只到记事本，我不能自行结束 chrome
- [ ] 轮 4-6 已落盘并 commit（`record_4..6.md` + `opinion.md` + `tests/opinion.md` 318 行）
- [ ] 待修（沿用）：`find_on_screen` 中文分词 overlap 不可靠（轮 6 实锤：OCR「稻 杳 一 哔 哩」→ 只给 Hi•Res）、HB-040 `_coerce` 用 schema default、schema 补「进程名必须英文」
- [ ] `WebSocketDisconnected` traceback（15:11 日志）记为观察，未定根因（`ws.accept()` 在 L339 存在）
