# Todo

<!-- 已归档于 ai_buckup/todo.md_2026-11-16-15-27-00.md（102 行全量：11-13 拼音索引节、应用表节、11-16 三批 11:46/12:18/12:33 全部待办与已勾项）。本文件为压缩版：保留全部未完成项 + 已结案批次要点。 -->

## 通用规矩（长期，勿违反）

- [ ] 每批：先落 `records/` + `todo.md` 再开工；测试 20 轮（明确）/ 3 轮（验证）并写 `tests/opinion.md`
- [ ] 少量局部小截图允许（`maxWidth/maxHeight` 压小）；页面结构首选 a11y；不用子智能体（「子智能体也不允许它启动」）；commit 中文主题（type/scope 英文）+ hash 追加台账 + **禁止 push**
- [ ] `progress.md` / `todo.md` > 100 行先归档再压缩；`tree.md` 文件增删后重建（仅非 `.gitignore`）
- [ ] 打分/训练前停掉 `:7860/:8080/:9880`（提交量是硬约束），跑完重启 + 4 灯复核；每个 python 跑带 `HF_ENDPOINT=https://hf-mirror.com` + `HF_HOME=<repo>\.hf-cache` + `HF_HUB_DISABLE_XET=1` + `MPLCONFIGDIR`
- [ ] 边界样本必须 ≥3 个独立 Model 实例复测取多数（HB-032）

## 2026-11-16-11-46-56 UI 确认与优化（→ records/2026-11-16-11-46-56.md + 追加节）

- [x] 确认插件：`dsh-builtin-browser` 系列 enabled（共用浏览器**是独立窗口、你看得到**；我 12:12 的「你看不到」推断是错的，已如实更正，启用 `ui-sidebar-browser` 面板取消）
- [x] `send()` 判 `ws.readyState === 1`、断线提示「消息未发送（每 3 秒自动重连）」并保留输入文本 —— **未做**
- [x] 12 个快捷按钮换中文指令（应用表真存在的程序；Spotify 路线删掉）→ 已改并 commit
- [ ] 活动条默认文案改中文「处理中…」+ 去掉 `toUpperCase()`；`#messages`/`#statusText` 加 `aria-live`，`#modelSelect`/`#muteBtn`/`#input` 加 `aria-label` —— **未做**
- [x] 窄窗口断点三项**撤掉**（你：窄窗口不用管，默认最低 1080p）；560×520 测量数据保留为已知边界
- [ ] `WebSocketDisconnected` traceback（15:11 日志）记为观察，未定根因（`ws.accept()` 在 L339 存在）

## 2026-11-16-12-33-59 六条需求按 1→6 开工（→ records/2026-11-16-12-33-59.md）

- [x] 1 窄窗口 UI：**无代码工作**（撤规则）
- [x] 3 dsh-builtin-browser 独立窗口：**无代码工作**（撤启用面板 + 已更正）
- [x] 4 允许少量局部小截图：**无代码工作**（判据口径）
- [ ] 2 播放音乐走 **浏览器 + B 站搜索播放**：6 轮结论见 `tests/2026-11-16-11-46-56_cc/opinion.md`
  - [x] 中文命令 + `open_url` 被选中（描述规则按 `agent-experience` 重写，3 轮 0 次 → 3 次）
  - [x] `open_url` 假成功已修（HB-044）：`webbrowser.open` 返回值不再被丢；应用表浏览器真路径 + `--new-window` + **进程内 ctypes 复读到窗口标题**才算成功，读不到如实报
  - [x] `desktop.py` 窗口证据改进程内 ctypes（HB-045）：`_visible_windows()` + `get_open_windows` + `focus_window`，不起 powershell 子进程（子进程看 **0** 窗口）、不用 `Add-Type`（沙箱拒）
  - [ ] **Q25**：真端到端必须由你在沙箱外跑 jarvis 验（**沙箱内 python 起的进程不能产生可见窗口**，实测对照定论）
  - [ ] **Q24**：pwsh 启动的 B 站窗口（进程 8228）要不要关？`kill_process` 授权只到记事本，我不能自行结束 chrome
  - [ ] 播放点击仍未达成：`find_on_screen` 中文分词 overlap 不可靠（轮 6 实锤 OCR「稻 杳 一 哔 哩」→ 只给 Hi•Res）
- [ ] 5 内存提交量优化（同口径全程量）：llama 去 `--mmproj` + `-c 16384` → `PF 3866→2339MB`；页面文件在系统托管下上涨（上限 25,134→29,812 MB），可用提交 461→521→3,451→2,929 MB
  - [ ] **Q21**：`python.exe -m src.server`（`F:\2D23D\venv`，非 jarvis）占 1,291 MB 提交、工作集仅 6 MB → 只允许我结束它？
  - [ ] **Q22**：页面文件增大是系统级、需你/admin（我只给命令）
  - [ ] TTS `is_half: true` 的量与速度 3 轮（现 `is_half: false` + `device: cpu`，`api_v2.py` 单进程 5,822 MB 是最大头）
- [ ] 6 视觉塔 + 多模态 + 保留 OCR：`llama.ps1` 恢复 `--mmproj`（**已在 14:41 重启时恢复，mmproj 增量实测 1,527 MB**）、`llm.py` 支持图片消息、新增 `describe_screen`（参数规则写在参数上）、`read_screen` 保留；3 轮判据 = 视觉与 OCR 互补 + 4 灯 + 提交量

## 待修 / 待确认（跨批次）

- [ ] **HB-040**：`_coerce` 把可选参数默认值架空（`set_timer` 中文默认文案被空串覆盖）
- [ ] **`find_on_screen` 中文匹配方式**（WinRT OCR 字间插空格 + 有错字 → 按空格分词算 overlap 基本匹配不上）
- [ ] `kill_process` 的进程名必须**英文**（中文被洗成空串 → `taskkill /IM .exe`），schema description 写清
- [ ] `lock_screen` 真锁屏（已授权，等你说「锁」，Q20）；通知气泡肉眼确认（Q19）；剪贴板 JWT 覆盖善后（Q18）
- [ ] `pyautogui.FAILSAFE = False` → `click_at`/`move_mouse` 无越界保护，坐标须受窗口位置约束

## 20 轮明确测试语音部分（`tests/2026-11-08-20-44-17_cc/`）

- [ ] **轮 11-20 需你在麦克风前配合**（打断三态 / 近音「米雅·爱莉雅·希雅老师」每次最多 1 次 / 安静 5 s + 轻敲期望 **0 检出** / 空转录必须播 `ack_no_heard` / 长句 8 s 不截断）。轮 1-10 已跑（1-4 PASS、5 部分、6-10 FAIL）
- [ ] `need_audio.md` §5 缺口（干净呼唤 ≥20、带噪 ≥10、竞品真人句 ≥4、无关短句 10）→ 重训 v1.0d（召回短板 = 音节窗正样本仅 45 件）

## 已结案批次（压缩，明细见归档、`tests/`、`records/`）

- **唤醒谱系**：`v0.4` rec 0.50 → `v0.5` **0.00 塌陷** → `v0.6`（真人 1.00 / 带噪 0.83）→ **v0.9 采用 + 阈值 0.75**（12 / 近音 fp 6 / 无关 2 / 对抗 4 / 长噪 1 / 环境 0）；`v1.0` 0.3009、`v1.0b` 0.6106 未采用；`v1.0c` 0.5865，可用 0.70-0.72（判别轴达标、召回轴塌 → 不采用）。**0.65 禁区**；环境音期望必须 **0**；「真人近音 fp ≤1」未达标。
- **裁决与默认值**：`stt.engine` = **whisper**；`stt.hot_bias` = **false**（实测有害）；sherpa 能量门 `span` + THR 0.008；`ack_no_heard` 具名池只接空/低质量转录；`hot_phrases` 上限 200；favicon 路由（console 0 error）。
- **已结案工具批**：20 轮 32 工具全过（虚假成功 5 条封住、`delegate_task` 摘除）；`tests/2026-11-13-12-25-43_cc/` 3 轮 PASS（HB-033 音量、HB-034 屏幕 GBK、HB-035 天气 ascii）；应用表 227 条 + `open_app` 三段（表匹配→APP_MAP→**复读到进程才算成功**）；ASR 容错（高置信 ≥0.66 且 gap ≥0.12 打开并登记别名；0.45-0.66 只给候选、**不打开**）；拼音索引 `py`/`py_tone`（修 `errors=ignore` 丢非中文、快捷方式尾巴剥）；同程序判据按 **exe basename**。
- **已取消**：看屏幕改走浏览器快照（11:20 你纠正 —— 零截图边界是 Agent 会话，爱莉希雅全本地，OCR 路径不动）。

- [x] 6 视觉塔 + 多模态 + 保留 OCR：**代码已落地**（`llm.py` `chat_image`、`jarvis/tools/vision.py` `describe_screen`、router 注册 33 工具，标签「看屏幕画面」，参数规则写在 `question` 上）；`--mmproj` 已恢复（llama PF 3,797 MB）
- [x] 轮 1（16:58）达标：**OCR 把「QuietLink 远程控制」读成 `远 程扌 空 制 台`，视觉认对程序名并给出按钮坐标**（刷新 (200,400)、退出登录 (200,700)）→ 互补性有硬证据，OCR 保留（`tests/2026-11-16-12-33-59_vision_cc/record_1.md`）
- [ ] **Q22 结案（你 16:47 定「不要动，硬盘空间不够，只设 8G 虚拟内存分页」）**：内存优化只能往下减占用；视觉塔 1,527 MB 增量由 Q21 释放的 1,291 MB + 现有 2,9xx MB 余量承接
- [x] **Q21 结案**：授权已给，16:47 复读 `src.server` 已不在进程里（你自行处理），我没有执行结束操作；可用提交 2,921 MB
- [x] `is_half: true` 实测**无收益** → **不采用**：省 7 MB（6,672→6,026 属噪声）、实时率 1.60-1.68 vs 1.81-1.87 波动无稳定差；`tts_infer.yaml` 保持 `is_half: false`（你已回改，该文件被 gitignore 不入库）
- [ ] **轮 2 需你启动 jarvis（Q27 已定）**：我 16:59 停掉我的沙箱 7860（`pwsh-39`），你在沙箱外启 jarvis，我在共用浏览器点「播放音乐」，让 jarvis 自己用 `open_url` 打开 B 站搜索页 + `看屏幕画面` 找封面 + `点击坐标` 点进去，你确认页面出现与播放
- [ ] 轮 3：同口径复测视觉轮的提交量（单 PID 读法，llama 多进程时 `.ps1` 取标量会失败）+ 4 灯 + `v0.9/0.75`
