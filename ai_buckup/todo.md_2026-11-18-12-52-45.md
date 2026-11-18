<!-- 已归档于 ai_buckup/todo.md_2026-11-17-15-51-09.md（157 行全量备份）；本文件只保留去重未完成项与最近小节 -->

# todo（compact）

## 常驻纪律（每轮都算）

- [ ] 先落 `records/` + `todo.md` 再开工；明确测试 20 轮 / 验证 3 轮，每轮 `record_i.md` + 批次 `opinion.md` + 累积 `tests/opinion.md`
- [ ] 局部小截图允许（压小）；页面结构用 a11y/DOM；不用子智能体；commit 用 Conventional Commits（type/scope 英文 + 中文主题），先写 `.tmp/commit_msg.txt` 再 `git commit -q -F`，hash 追加 `progress.md`，**禁止 push**
- [ ] `progress.md`/`todo.md` > 100 行先归档再压缩；`tree.md` 文件增删后重建（仅非 `.gitignore`）
- [ ] 训练/打分前停 `:7860/:8080/:9880`（提交量硬约束），跑完重启 + 4 灯复核；python 跑带 `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET/MPLCONFIGDIR`
- [ ] 边界样本必须 ≥3 个独立 Model 实例复测取多数（HB-032）；**不碰页面文件**（Q22：你只设 8G 分页）

## P1 · 播放 / B 站（判据五项已定：导航 / 关弹幕 / 最低档=点过「360P 流畅」+宽度640 / 时间前进+播完信号(BV 变化) / 播完关窗）

- [x] 2026-11-17-15-48 用「月声尽,心灯明」（`BV1RMYF6kEze`，1,765,329 播放，20 条）跑 3 轮 → `record_18..20.md` + 批次/累积 opinion
      **轮 18 部分 FAIL、轮 19/20 全项 PASS**。判据两处修正（轮 18 暴露，不是迁就结果）：
      **最低分辨率 = 点过「360P 流畅」+ 宽度 640（高度随源比例，这支是 640x338）**；
      **播完信号 = BV 号变化**（连播发生在结尾那一刻，`ct >= du-1.2` 常差 0.7 秒）
- [x] 2026-11-17-17-45 批次（98 行）+ 累积（398 行）opinion 已追加
- [ ] 2026-11-17-14-01 修 `play_first_video` 假阴性：直连 BV URL 时不走 Route B 视觉点击（标题一开始就是视频页，「标题未变→失败」不成立）
- [ ] 2026-11-17 **jarvis 端到端验收**：你跑 `start_all.bat`（`-c 24576` 已定）后由 jarvis 自己走完 3 轮，4 灯复核
- [ ] 2026-11-17 播放链收尾：`video.play()` 被 Chrome 自动播放策略挡住，必须受信点击播放按钮 —— 兜底路径需在真实 jarvis 进程里复现（沙箱外）

## P1 · 唤醒 / 训练

- [x] 2026-11-17-13-52 按**交集**重算 `aili_xiya_v1.2` clip 集合 → `records/2026-11-17-17-55-00.md`
      **交集：正 20 / 负 12 / 合计 32**（第一次正20/负13，第二次正21/负12）。差异 2 件：
      `elya pos_hello`（第一次 `检出=0` 不入库）剔出 → `pos_te_1505.wav` 挪到 `.tmp/excluded_v12/`（不删）；
      `firefly neg_comp xiao_ai_tong_xue`（第二次不入库）产物里本来就没有。特征已按交集重建（正×5/负×1，合并 v0.9 基线）
- [x] 2026-11-17-13-44 `train` + `eval`（18:11-18:26 跑完，三服务已停）→ `records/2026-11-17-18-30-00.md`
      **结论：v1.2 不如 v0.9 → `config.yaml` 未动**（现役仍 `aili_xiya_v0.9.onnx` + `0.75`）。
      eval：pos mean/max `0.536/0.622`，neg `0.197/0.214`；阈值矩阵 0.70 处 **recall 0.00**、fp 0.00（灵敏度过低，不是误报）。
      **自曝两处**：驱动 `step_train` 少传 `--train_model`（默认 False）→ **train rc=0 是假成功**（无 onnx 产物，日志 532 字节）；
      verify 的 `ROOT = 脚本父目录`（= `training/`）→ 产物路径拼成 `training/openWakeWord/output/...`（不存在）。
      两处已在驱动修（train 加产物检查：rc=0 无 onnx 改判 rc=1；verify 用 `.tmp` 补丁副本把 ROOT 钉到仓库根）
- [ ] 2026-11-17-18-30 v1.2 若要继续：①扩数据（15xx 合格件 32 件，正 train 11 件只占 v0.9 基线 2.6%）②你真人音频扩正样本
      （真人克隆实测不可用，60 s 失控音频）③接受 v0.9 继续现役。**等你挑，不自行推进**
- [ ] 2026-11-17 语音 20 轮 · 轮 11-20（需你在麦克风前）→ `tests/2026-11-08-20-44-17_cc/record_11..20.md`（轮 1-10 已跑：1-4 PASS、5 部分、6-10 FAIL）

## P1 · 不需你配合

- [ ] `find_on_screen` 中文匹配方式（WinRT OCR 字间插空格 + 错字 → 按空格分词算 overlap 基本匹配不上，HB-040 家族）
- [ ] `WebSocketDisconnected` traceback 根因（观察中，`ws.accept()` 在 L339 存在）

## P2 · Monitor 面板（只做 design，不开工）

- [ ] design v3.0（日志中枢 + 单窗口托管 + 指定关闭 + 外部接入）已定；**开工授权等 Q31-1**；可行性边界已写进设计（stdout 只能在 jarvis 是父进程时抓、start_all 只留一个窗口、关窗口不能靠控制台语义、外部接入只能识别+体检）

## P3 · 全部挂起（你 11:01 定「P2 级以下先不管」）

- [ ] Q18 剪贴板 JWT 193 字符善后、Q19 通知气泡肉眼确认、Q20「锁」真锁屏、`kill_process` 英文进程名、`pyautogui.FAILSAFE` 坐标约束、Q24（你的窗口你自己关）
- [ ] **HB-047 已结案 wontfix**（你 10:52 定：chrome 崩溃 = 内存溢出，属用户需注意的问题）

## 最近小节

- [x] 2026-11-17-15-50 查得「月声尽,心灯明」→ `BV1RMYF6kEze`（1,765,329 播放 / 20 条 / 31466 字节）
- [x] 2026-11-17-15-46 **轮 7 全项 PASS**（`record_17.md`，`BV13G411Q76u`，ct 0.2→222.5/223.466，关 pid 1748，窗口数 0）
- [x] 2026-11-17-15-28 **轮 6 FAIL 如实记录**（`record_16.md`）：设置时控件不在 DOM、B 站续播到 209s、连播换歌
- [x] 2026-11-17-15-22 **轮 5 全项 PASS**（`record_15.md`）；轮 3 FAIL（无播放动作）、轮 2 FAIL（长连接崩溃）、轮 1 部分 FAIL（复用假成功）
- [x] 2026-11-17-14-09 CDP 实现路径落地：`jarvis/tools/browser_cdp.py` + Chrome `--remote-debugging-port=9333`（只监听 127.0.0.1，只作用于 jarvis 自起窗口/profile）
- [x] 2026-11-17-13-25 **HB-040 结案**（`_coerce` 加 `if key not in out: continue`，3 轮全 PASS）
- [x] 2026-11-17-13-30 合成+打分跑完（正 20/负 13 = 33）；自曝心算错 34→33
- [x] 2026-11-17-13-44 自曝驱动 monkeypatch 失效覆盖 `aili_xiya_v1.1` 产物（不可恢复，无功能影响）
- [x] 2026-11-17-13-52 你定「取两次交集」+ train 稍后；已登录（cookie 留在 `.tmp\chrome_profile`）
- [x] 2026-11-17-15:52 **状态落盘 + 停手**（你说要用电脑）：progress 快照 99 行、todo 归档（备份 157 行→60 行）、tree 重建 548 行/481 文件、批次+累积 opinion 追加；本地 commit **5af39ad**（CDP 播放链 17 files）+ **520c9bd**（record 追加节补提交）+ **185b22d**（hash 追加，本条 hash 下次 commit 时补进台账）；挂着的旧 llama 探测作业 `pwsh-37` 已 job_kill 释放内存；我起的窗口数 0

## 21:13 onnx_opinion 新规矩（你 21:13 定，→ [records/2026-11-17-21-13-04.md](records/2026-11-17-21-13-04.md)）

**规矩（以后每次追加照此执行，永久生效）**
1. `onnx_opinion.md` 放**仓库根目录**，不在 `ai_buckup/`
2. **每次追加之前**先备份到 `ai_buckup/onnx_opinion.md_<yyyy-mm-dd-hh-mm-ss>.md`，再改
3. 只允许 6 块，顺序固定：`0 规则和口径` / `1 版本表（版本号, 构建时间, 正样本, 负样本, steps, 训练 Acc/Rec, 离线验收 @0.7）` / `2 部署 3 轮实测表（模型, 轮1, 轮2, 轮3, 13次(3轮), 近音 fp(3轮), 无关 fp(3轮), 对抗, 长噪, 环境, 纯噪）` / `3 峰值数据表（真人数据为列）` / `4 结论` / `5 追加内容（版本, 时间, 关联, 结论）`
4. **追加 = 直接改表 1/2/3**；第 5 块每次追加**只写一行**
5. 数字全部来自日志/输出；未测格子写「未测」，不留空、不猜
6. `tree.md` 随之重建（根目录新增非 .gitignore 文件）

- [ ] **重构 `onnx_opinion.md`**：备份旧文件 → 根目录新文件按 6 块重排（含 v1.2 §9、v1.3 §10 拆进表 1/2/3 + 第 5 块单行），旧 `ai_buckup/onnx_opinion.md` 移出入根
- [ ] **补 v1.3 部署 3 轮**（现只有 1 轮 @0.75 + 1 轮 @0.70，表 2 先写未测，跑完回填）→ `WTHR=0.70` 再跑 2 轮 `.tmp\probe_v09_deploy.py`
- [x] 21:13 规矩写入 todo（本块）


- [x] **第 1 项 扩数据后重训**（20:20-20:52 跑完，**不采用**）：合成 266 件（新增 126）→ 交集 **正 74 / 负 15 / 合计 89**（v1.2 是 20/12=32）→ 正样本行占比 2.6%→**8.2%** → train rc=0 且 `aili_xiya_v1.3.onnx` 存在 → eval **VERDICT PASS (best 0.6)**、25 件合成 test pos 0.757/0.877、@0.75 逐文件 14/25。
      **部署轴 @0.75**：13 次 **10**（v0.9 12）、5 件新录音 **6**（7）、近音 4（4）、无关 1（2）、定标 0（0）、长噪 **0**（1）、对抗 4（4）、环境音 **0**（1）；@0.70：13 次 11（14）、新录音 6（10）、对抗 6 BAD。
      **合成/噪声轴改善，真人召回轴劣化 → 任一条不如 v0.9 → `config.yaml` 不动，现役 `v0.9 + 0.75` 保持**。结论第 10 节在 [ai_buckup/onnx_opinion.md](ai_buckup/onnx_opinion.md)
- [x] **第 2 项 修 `_jarvis_windows()` 窗口计数假阴性**（21:44-21:47 改码 + 实测通过）：认「记录 pid ∪ **跑 jarvis 专属 profile（`.tmp\chrome_profile`）的 Chrome 进程 pid**」，`jarvis_pids()` 同口径。实测：改动前你 1 窗口（pid 15416）→ 我起的 0（profile pids 空）✓；`open_url` 后窗口 pid **20468** 被认出 → 我起的 1、总 2（你的窗口不计）✓；杀我起的 pid 20468 + 8 子进程成功、杀你的 15416 **被拒绝**（Q32/Q34）✓。附带修自曝瑕疵：**杀成功就忘掉 pid**（`forget_pid`；20468 杀后仍留在记录里 = 死 pid 带杀权限），验：忘后不在记录、再杀被拒 ✓
- [x] **第 3 项 修 `play_first_video` 直连 BV 假阴性**（21:49 改码 + 实测通过）：①Route A 用 `_extract_url` 从「最多播放第一支：https://…」取 URL（旧代码匹配「第一支视频：」→ 永不命中，白落回视觉）；②直达 BV URL 不再用 URL 关键词匹配窗口标题（标题不含 `video/BV…` → 旧代码「没有基准，中止」落回视觉点击）。现在导航后**用 CDP 读 `video`+duration 判定**，全程无视觉、无点击。实测：关键词「稻香」→ `BV1oj411G7sR` → 判定进入视频页（`有video:true, du:405`）；直达 URL → 复用我起的窗口（「没有导航」证据）→ `有video:true, du:405, 菜单项数:6, 弹幕input:true`；播完关掉我起的窗口（pid 1836 + 8 子进程）→ 我起的 0、你的窗口未动 ✓
- [ ] **第 4 项 语音 20 轮 轮 11-20（放最后，需你在麦克风前）** → `tests/2026-11-08-20-44-17_cc/record_11..20.md`（轮 1-10：1-4 PASS、5 部分、6-10 FAIL）
- [x] 2026-11-17-20-17 三服务 4 灯复核（wake `v0.9 + 0.75` online+listening / asr warm / llm `:8080 -c 24576` / tts `:9880`），我起的窗口数 0


- [ ] 2026-11-17-18-46 `onnx_opinion` 补 v1.0c / v1.2 行（**追加，不覆盖**；数据源只用已落盘证据，本批不重跑探针）
- [x] 2026-11-17-18-46 **jarvis 端到端 3 轮播放验收**（`tests/2026-11-17-18-46-00_cc/record_1..4.md` + 批次 `opinion.md` + 累积 `tests/opinion.md` 406 行）
      —— 三服务已重启，**4 灯这轮适用**：wake `v0.9 + 0.75` online+listening / asr whisper warm / llm `:8080` / tts `:9880`
      判据五项不变（导航 / 关弹幕 / 最低档 = 点过「360P 流畅」+ 宽度 640 / 时间前进 + 播完信号 BV 变化 / 播完关掉我起的窗口）
      **结果：轮 1 FAIL、轮 2 部分 PASS（4 项）、轮 3 FAIL、轮 4（我加的越界诊断轮）全五项 PASS —— 3 轮口径没有全项 PASS 轮。**
      轮 1 根因：jarvis 选旧工具 `play_first_video` + `_extract_url` 吞中文关键词（启动 URL 停在 `keyword=`）+ `fetch_page` 中文不编码（`'ascii' codec can't encode`）
      → 已修：`play_music` 加 `keyword`（走 API `order=play` 直达最播放第一支）+ schema 把「播歌唯一工具」写成 `play_music`（轮 2 起 jarvis 自选它）+ `fetch_page` 先 `quote` 编码
      **自曝**：`first_bilibili_video` 返回带修饰句子，我第一版用 `startswith("http")` 判会把成功查询误报成查不到（改 `_extract_url` 后判）；轮 3 的失败原因被 `result[:120]`/`result[:200]` 截断，**永久读不到**，轮 3 保持 FAIL
- [ ] 2026-11-17-19-35 **新记 P1：`_jarvis_windows()` 按 pid 匹配，Chrome 多进程下窗口 pid ≠ 启动 pid**（轮 2 实测启动 21200 vs 窗口 10848；轮 3 `PID_FILE` 未新增本轮 pid，`n = 22`）→ 「我起的窗口数 0」不可作数，需修匹配（父树/窗口标题双认）
- [x] 2026-11-17-19:35 **`main.py` 工具打印不再截断**（`result[:120]` 把失败原因切掉，WS/UI 保持 200 字上限）—— 轮 4 靠它拿到 jarvis 完整播报，五项全证到
- [ ] 2026-11-17-18-46 **扩数据后重训**（你选「扩数据后重训（推荐）」）：`:9880` 合成更多 TTS 件 → `score` → `clips` → `feat` → `train` → `eval`
      —— 训练前必须**停三服务**，所以排在 3 轮端到端验收之后；判据不变，**任一条不如 v0.9 就不改 `config.yaml`**
- [x] 2026-11-17-18-56 三服务重启 + 4 灯复核（**自曝**：18:57 起服务时 record 未写，违反「先落盘再开工」；`FreePhysicalMemory` 单位 KB 当字节算，报出「可用 12 MB」假危机；`Add-Type -Language CPowerShell` 非法枚举 → 类型没建起来除零；`pwsh -c` 里塞转义引号给 `python -c` → `SyntaxError`，改用读进程命令行核对 `-c 24576`）
- [ ] **音乐唯一性（22:05 新规则，→ records/2026-11-17-22-05-05.md）**：爱莉希雅启动的音乐必须唯一 —— 同一时刻只允许 1 个我起的 B 站播歌窗口。落地：play_music 起手先数我起的窗口（profile 认 pid，第 2 项口径），已有播歌窗口就**复用导航**或先关掉旧的，绝不并存 2 个；播完（ended/连播信号）关掉它，关后「我起的窗口数」必须 0。轮 11 实测就是反面现场（关窗失败 → 旧窗口残留）。验收：任意时刻播歌类窗口 ≤ 1

## 2026-11-18-10-17-23（→ records/2026-11-18-10-17-23.md）

- [ ] **第 1 项 音乐 ducking**：唤醒触发即**暂停**当前播放的视频（CDP，只碰我起的窗口），恢复点 = **回复（TTS）播报完成后**；中途 `ABORT`/`Stopped.` 也必须恢复，不许静音卡死。回读 `paused=true` 才算暂停成立
      —— **机械与现场证据已到位**（12:07 `record_7.md`/`record_9.md`：唤醒时 `[Duck] 已暂停我自己的播放（回读 paused=True，ct=39.6/224）`、TTS 后 `[Duck] 已恢复播放（回读 paused=False，ct=1.9/256）`；恢复口径已放宽成 `explicit=True`，媒体键/手动暂停的自有窗口也能恢复）。**真人麦克风验收仍未测**，所以整项不勾选。
- [x] **第 2a 项 打开浏览器**（11:00-12:05 实测 PASS）：轮 1 FAIL（Sandboxie `Start.exe default_browser` 存根被当成功 + 中文标题假阴性）→ 修存根黑名单 + 「浏览器」走 `open_site` + **扫全部标签读地址**作主判据 → 轮 1b/20 PASS（`https://www.baidu.com/`，标题「百度一下，你就知道」，记录 pid 为我起的窗口）
- [ ] **第 2b 项 打开微信**：打开微信 + **尝试登录**；没有凭据就只打开（不猜密码、不硬塞凭据）
      —— **只打开口径 PASS**（轮 23：`已打开：微信（从应用列表匹配，复读确认进程 Weixin）`，无登录动作）。**登录被 Q36 阻塞**（`need_user.md` status: wait），未答前不推进。
- [x] **第 2c 项 打开XXX（用户自定义对象）**（12:07 实测 PASS，设置界面仍排 P2）：`config.yaml` `sites:` 用户名字优先；轮 19b 模型编造「我的服务器」→ 工具**诚实拒绝并列出可用名字** → 轮 19c 照名字调 `open_site("我的播歌页")` → `BV1RMYF6kEze` 导航成功、地址复读为证。「拒绝里列出名字」这条设计实证能把小模型拉回正确条目。
- [x] **第 2d 项 搜索改造**（11:21-11:35 实测核心 PASS）：`搜索` → 打开浏览器搜索，引擎 **baidu 首选、bing 兜底**；轮 5/5b 出现**搜索话术越界播歌** → 提示词压不住 2B 模型，改**分发层动词闸门**（无播放动词 + 「打开+…页」都拒 `play_music`）→ 轮 5c 落到 `baidu.com/s?wd=` 带标题证据 ✓。**bing 兜底本轮未触发 = 未测**。
- [x] **第 2e 项 打开github**（11:07-12:00 实测 PASS）：轮 3 FAIL（模型只调 `open_app` 找 Git GUI/Unity Hub，从不 `open_site`）→ 系统提示词路由 + `github` 进 `_BUILTIN_SITES` → 轮 3b/21 PASS（地址复读 `https://github.com/`）
- [x] **第 2f 项 打开b站**（11:10-12:00 实测 PASS）：轮 4b/22 PASS（CDP `Page.navigate` + 复读 `www.bilibili.com`）；轮 4 键盘路线被 chrome「要恢复页面吗？」抢焦点 → 改 CDP 主路径；模型两次想播歌都被闸门挡回 ✓
- [x] **第 3 项 播放控制指令**（11:44-12:00 实测三项 PASS）：`暂停播放` → `music_control(pause)` 回读 `paused=True`（轮 15/16 `ct=14.3/224`）；`恢复播放` → `explicit=True` 放宽后回读 `paused=False`（轮 9c/13/17）；`关闭音乐` → 只关我起的 profile-recognised pid，关后「我起的窗口数 0」（轮 10c/14/18，pid 漂移 16408→2820 仍认得出）。`media_control`（系统媒体键无回读）与 `click_at (0,0)`/`ctrl+c`/`type_text` 凑数动作全部被闸门挡回（8c FAIL 后加的）。
- [x] **20 轮测试（非语音路径：WS 文本 + CDP 证据）**：编号 1-23 + 复测 1b/3b/4b/5b/5c/6b/6c/7b/8c/9c/10c/19b/19c 共 37 条 `record_1..9.md` + 批次 `opinion.md` + `tests/opinion.md` 429 行。**语音 ducking 的真实麦克风验收没做**（你不在电脑前），照口径写未测，不算这 20 轮的 PASS。
- [ ] 语音 20 轮 轮 12-20（旧批 `tests/2026-11-08-20-44-17_cc/`，需你在麦克风前）

- [x] 2026-11-18 12:25 P1 中文读取改走 CDP（我起窗口），无 OCR —— `read_page`/`find_on_page`/`click_page_text` 落地（→ record_10.md、record_11.md）
- [x] 2026-11-18 12:38 分发层闸门：话里有「点击/找到」+「页面/页」→ 拒 web_search/run_python/read_screen/find_on_screen/fetch_page，指名 find_on_page/click_page_text（轮 26 FAIL → 轮 28 模型只调 find_on_page）
- [x] 2026-11-18 12:43 修我漏的花括号（外层 for 的右括号）+ 非 dict 防御（find_on_page 直测命中 2 处「番剧」）
- [ ] 2026-11-18 12:44 HB-050 未结案：click_page_text 点了、坐标对、点下就是目标链接，**地址复读没变**（导航未证实）→ 方案②「取 href + Page.navigate 我自己起的窗口」待做（→ hard_bug.md HB-050）
- [ ] 2026-11-18 12:28 Q37 待你裁决：本机无中文 OCR（WinRT 不可用、Umi-OCR 未装、:50015 无监听）→ 装并常驻 Umi-OCR，还是桌面中文识别记「不做」（→ need_user.md Q37）
- [ ] 2026-11-18 12:44 你要求「先暂停并落盘」：我停了驱动轮次；jarvis20 + llama :8080 + api_v2 仍在跑，是否停来腾内存由你定（→ record_11.md）
