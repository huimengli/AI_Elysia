# 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-17-19-49-00.md（102 行全量：逐条 hash + 结论 + 自曝 + 逐条提交流水）。本文件为压缩版。 -->

## Git 提交记录（最近 18 条，**全部已本地 commit，未 push**；结论细节在归档与 `records/`、`tests/`）

```text
b7e6e57 fix(AI): 播歌走 play_music 的 keyword 直达最播放第一支，并修 fetch_page 中文编码与工具打印截断
87ca284 docs(AI): 把 20 轮明确测试的逐轮脚本落盘（说什么/期望/判据）
d2ac66e docs(AI): 实测「和我一起看界面实时更新」——连接器自带浏览器已够，不需要 9222
98154ea docs(AI): 取消「看屏幕改走浏览器快照」并厘清零截图的边界
6fd7aa6 docs(AI): 把 d30afda 的 hash 追加到进度台账
d30afda feat(web): 设置里可切换唤醒 ONNX，只列 Git 里的 3 项（v0.3 0.70 / v0.9 0.75 / v1.0c 0.72）
b84d4a5 docs(AI): 把 dec93db 的台账、开工清单与 tree.md 重建落盘
dec93db build(AI): 把现役 v0.9 与 v1.0c 唤醒 ONNX（含外部权重 .onnx.data）入 Git，并归档压缩 hard_bug 与 todo
3e14163 docs(AI): 把 a604481 的 hash 追加到进度台账
a604481 feat(web): favicon 消除页面唯一的 console 404，并加只读的 hot_phrases CSV 导出
91c2251 docs(AI): 把 9b13ac5 的 hash 与 4 灯复核追加到进度台账
9b13ac5 feat(AI): 未完项 1 落地——「我没听清，请再说一遍」预合成进 RAM 具名应答池、只接空转录与低质量转录；hot_phrases 小表 + whisper 热词偏置默认关
c5a2d04 docs(AI): 把服务重启与 4 灯复核追加到 Q17 批记录（stt.engine 保持 whisper）
f72d7c1 docs(AI): 把 3cc0ded 的 hash 追加到进度台账
3cc0ded feat(AI): Q17 裁决 C 落地——sherpa 路径加能量门（span 只掐头尾静音，默认 THR 0.008）+ 3 轮三配置 A/B，已知集 2/6、乱码 0、耗时减半，stt.engine 保持 whisper
6cc0000 docs(AI): 把服务重启与 4 灯复核追加到 Q16 复测批记录（保持 v0.9+0.75）
8d99b42 docs(AI): 把 d283fe9 的 hash 追加到进度台账
d283fe9 test(AI): Q16 只 B 复测 v1.0c 三轮（0.65/0.70/0.72，NINST 3/5/7）——复测可重复、0.65 禁区（环境音双模型 1 次检出违反期望 0）、最佳点 0.72，不换现役保持 v0.9+0.75，补录与换阈值提 Q17 待裁决
ce50c7e docs(AI): 把服务重启与 4 灯复核追加到 Q15 批记录（保持 v0.9+0.75）
```

## 当前未结案（口径与依据见归档、`todo.md`、`need_user.md`）

## 当前未结案（口径与依据见归档、`todo.md`、`need_user.md`）

- **P0**：`-c` 取值（实测 16384=2,339 / 24576=3,476 / 65536=4,522 MB；图不进主上下文 → 主上下文需求 ≈7,863 tokens，建议 `-c 16384` 省 2,183 MB）→ **等 Q33 授权**
- **P1 播放链**：数据侧通（服务端 HTML 266,710 字节 / 126 bvid / `BV1Ki4y1y7HC`）；**窗口边界是真阻塞**
  （`open_url L171/L195` 与 `navigate_url L404` 遍历全部可见窗口，实测打进我的 DSH 浏览器窗口 pid 16732/15416）→ **等 Q32 授权**
  （只认 `_jarvis_windows()`，你的窗口不聚焦不输入）；`navigate_url` **沙箱不可能验通**（键盘注入落沙箱窗口站），真验通需你跑 `start_all.bat`
- **P1**：语音 20 轮 **轮 11-20**（轮 1-10：1-4 PASS、5 部分、6-10 FAIL）→ 需你在麦克风前
- **新需求（你 11:00 第 4 条）**：**全量重训练**（现有多音色 TTS + 你的部分音频 + 噪音）出一个版本，与 `v0.9` 同口径比，**不如 0.9 就不改**；`v1.0d` **跳过**（第 5 条）
- **P2**：**Monitor 全系列**（design v3.0 已定，Q31 三条口径确认：只关 jarvis 自起 pid / 接受无 stdout 接管 / 你跑 start_all 我关窗口复测）→ **先不开工**
- **P3 全部挂起**（你 11:00 第 6 条「p2 级以下先不管」）：`kill_process` 英文进程名、`pyautogui.FAILSAFE`、`WebSocketDisconnected`
- **open bug**：**HB-040** `_coerce` 架空可选参数中文默认值（`set_timer` 默认文案被空串覆盖）→ `hard_bug.md` **不归档**（未全解决）
  ；**HB-047 closed/wontfix**（你裁决：chrome 崩溃属内存溢出，"不需要修，需要用户注意"）
- **等你确认（status: wait）**：**Q18**（剪贴板 JWT 193 字符被覆盖善后）、**Q19**（通知气泡肉眼确认）、**Q20**（「锁」才真锁屏）、
  **Q32**（窗口边界修法 + "第一支"三种口径）、**Q33**（`-c` 取值 + 改 `start_all.bat` 授权）
- **禁区/边界（长期）**：`v0.9 + 阈值 0.75`、`stt.engine: whisper`、`stt.hot_bias: false`、`is_half: false` 不动；
  **页面文件不碰（Q22 结案，你只设 8 GB 分页，现分配 16 MB）**；不最大化窗口、点击需在任意窗口尺寸准确；剪贴板先存后还；
  `kill_process` 授权只到记事本；**禁止 git push**
- **新记 P1（19:49）**：`_jarvis_windows()` 按 pid 匹配，**Chrome 多进程下窗口 pid ≠ 启动 pid**（轮 2 实测 21200 vs 10848）
  → 后拍「我起的窗口数 0」不可作数；轮 3 的 `PID_FILE` 也没新增本轮 pid（`n = 22`）

## 最近提交（逐条自曝与数字，细节在 `tests/`、`records/`；全量在归档）

- 只听歌播放链本地 commit：**5af39ad** feat(AI): 只听歌播放链走 CDP —— 关弹幕、最低分辨率、播完关掉我自己起的窗口（17 files：`jarvis/tools/browser_cdp.py` + `jarvis/tools/app_control.py` + record 13-56/14-01/14-08/15-48 + `record_12..17.md` + 批次/累积 opinion + todo 归档备份 + progress + tree）。**全项 PASS 2 轮（轮 5、7），FAIL 4 轮全部当场暴露根因并修**（复用假成功 / 长连接崩溃 / 无播放动作 / 控件不在 DOM + 续播 + 连播换歌）。**自曝**：追加 hash 时把中文长串带反引号塞进 `pwsh -c`，PowerShell 解析后反引号被吞 → `SyntaxError`，追加**没执行**（这条是重犯，规矩重申：先写 `.tmp/*.py` 再跑）。**已本地 commit，未 push**。
- 落盘补提交本地 commit：**520c9bd** docs(AI): 把 13:52 的三条答复与截图判据口径落盘补提交（`records/2026-11-17-13-20-00.md` 追加 20 行 + progress）。**自曝**：13-56 那批提交时我只 add 了四个 record，把这个 record 的追加节**漏加**了（工作区一直显示 M，直到这次 status 复查才发现）。**已本地 commit，未 push**。

- 停手后继续 · hash 补记：**185b22d** `docs(AI): 把 5af39ad 与 520c9bd 的 hash 追加到进度台账` + **f5bdd03** `docs(AI): todo 补记状态落盘与停手（progress/todo 均 <100 行）`。**已本地 commit，未 push**。
- 新歌曲 3 轮本地 commit：**48913bf** `test(AI): 新歌曲「月声尽,心灯明」跑 3 轮 —— 轮 18 暴露判据过死，轮 19/20 全项 PASS`（9 files：`app_control.py` + todo + tree + 累积/批次 opinion + `record_18..20.md`）。**判据两处修正（轮 18 暴露，不是迁就结果）**：①最低分辨率 = 点过「360P 流畅」+ **宽度 640**，高度随源比例（这支是 `640x338`，写死 640x360 把合法结果判成 FAIL）；②**播完信号 = BV 号变化**（连播发生在结尾那一刻，`ct >= du-1.2` 常差 0.7 秒）。累计 20 轮：**全项 PASS 4 轮（5、7、19、20），FAIL 6 轮全部当场暴露根因并修**。**4 灯本轮不适用**（三服务在你用完电脑后停了）。**已本地 commit，未 push**。
- 按交集重算 v1.2 入库集合本地 commit：**fb873e6** docs(AI): 按交集重算 v1.2 入库集合（正20/负12=32，剔 elya pos_hello）（`records/2026-11-17-17-55-00.md` + todo + tree）。**自曝 3 版解析 bug**：①判定行首正则只吃到 clips 格式（score 逐件 0 条）；②`endswith('入库')` 把 `不入库` 判成入库 + 「不入库」行无 `rms=` 被正则跳过（第二次只吃到 33 条）+ `pos_ok.append` 写成元组；③用「检出=1 且峰值>=0.70」重算判定得出负样本交集 **14 件 > min(13,12)** —— 数学上不可能，数字不可信。第 4 版只用日志判定标记做集合交集才成立：**正 20 / 负 12 / 合计 32**；`pos_te_1505.wav` 挪到 `.tmp/excluded_v12/`（不删），特征按交集重建（正×5/负×1 合并 v0.9 基线）。**已本地 commit，未 push**；`train`+`eval` 仍未跑（三服务现在是停的）。
- v1.2 train+eval 本地 commit：**1c50ed1** fix(AI): 训练驱动补 --train_model 与 verify 路径（v1.2 不如 v0.9，config 未动）（驱动 + `records/2026-11-17-18-30-00.md` + todo + tree）。**train 假成功自曝**：驱动只传 `--training_config`，`--train_model` 默认 False → rc=0 且无 onnx 产物（日志 532 字节只有 matplotlib 警告）；修后显式加 flag + **产物检查**（rc=0 无 onnx → 改判 rc=1）。**eval 路径自曝**：verify 的 `ROOT = 脚本父目录`（= `training/`）→ 产物被拼成 `training/openWakeWord/output/...`（不存在），改用 `.tmp` 补丁副本把 ROOT 钉到仓库根。**结果**：v1.2 pos mean/max `0.536/0.622`、neg `0.197/0.214`，阈值 0.70 处 **recall 0.00**（fp 0.00）→ **不如 v0.9，`config.yaml` 未动（现役 `aili_xiya_v0.9.onnx` + `0.75`）**。验收矩阵其余项（25 真呼唤 / 真人近音 / 合成对抗 / 定标纯噪声 / 环境音）**未跑，如实记**（基础矩阵在 0.70 已 0 检出，跑全套无意义；要跑需你配合麦克风与真人音频）。**已本地 commit，未 push**。

## 2026-11-17-19-49 jarvis 端到端 3 轮播放验收（18:46 需求）

- 批 `tests/2026-11-17-18-46-00_cc/record_1..4.md` + 批次 `opinion.md` + 累积 `tests/opinion.md`（406 行）。
  **3 轮口径没有全项 PASS 轮：轮 1 FAIL、轮 2 部分 PASS（4 项）、轮 3 FAIL；轮 4 是我加的越界诊断轮，全五项 PASS。**
- 落地改动：`play_music` 加 `keyword`（API `order=play` 直达最播放第一支，丙方案无视觉无点击）+ schema 把播歌唯一工具写成 `play_music`
  + `fetch_page` 先 `quote` 编码（修轮 1 的 ascii 崩）+ `main.py` 工具打印不再截断（轮 3 失败原因被 120/200 字截掉，**永久读不到**）。
- 轮 4 五项证据（jarvis 自己的完整播报）：直达 `BV1RMYF6kEze`（1,768,296 播放）/ `danmakuChecked=false` / 点过「360P 流畅」判定 `640x338`
  （**起始读数分辨率 `0x0`，判据不能只看首拍**）/ 受信点击播放 → **连播发生 = 播完信号**（`BV1RMYF6kEze → BV1DepY6BE1G`，t+288 s）
  / kill 自起 pid 1552 进程树 9 个全 SUCCESS +「关后我起的窗口数：0」。
- 自曝三条：`first_bilibili_video` 返回带修饰句子，我第一版用 `startswith("http")` 判会把成功查询误报成查不到（改 `_extract_url` 后判）；
  驱动 v1 收流 45 s 太短 + 后拍拍太早（轮 1 记窗口数 0 不可作数）→ v2（300 s，t+310.2 超时，`tool_result` 全文没收到）→ v3（400 s，轮 4 收到全文）；
  **新记 P1：`_jarvis_windows()` 按 pid 匹配，Chrome 多进程下窗口 pid != 启动 pid**（轮 2 实测 21200 vs 10848；轮 3 `PID_FILE` 未新增，`n = 22`）。
- 4 灯这轮全程适用（wake `v0.9 + 0.75` / asr warm / llm `:8080 -c 24576` / tts `:9880`），三服务未停（本轮是端到端，不是训练）。
- 本地 commit（**未 push**）：hash 见下一条台账。
## 21:35 第 1 项收口 + 21:13 新规矩（→ records/2026-11-17-20-16-55.md、21-13-04.md）

- **v1.3 全链跑完（20:20–20:52，三服务先停）**：266 wav（期望 266 缺 0）→ 打分 rc=0 正 76/77、负 17/189 → clips rc=0 正 75/负 20 → **两次交集 正 74 / 负 15 / 合计 89**（上界合法性 OK，v1.2 是 32）→ feat 正 train `25,435+2,280=27,715`（新占 8.2%）→ **train rc=0 且产物在**（Acc **0.6737** / Rec **0.5768**）→ **eval VERDICT PASS (best 0.6)**、pos 0.757/0.877、@0.75 逐文件 14/25。
- **部署轴对照（单探针串行，复用 `.tmp/probe_v09_deploy.py`）**：@0.75 v1.3 = 13 次 **10**（v0.9 12）、5 件新录音 **6**（7）、近音 4（4）、无关 1（2）、定标 0、长噪 **0**（1）、对抗 4 ✓、环境音 **0**（1）；@0.70 = 13 次 **11**（14）、近音 7（11）、无关 3（6）、对抗 **6 BAD**。
- **判据结论：任一条不如 v0.9 → `config.yaml` 不动，现役保持 `aili_xiya_v0.9.onnx` + `0.75`**。合成/噪声轴改善、真人召回轴劣化 → 合成多音色 TTS 到顶（1.0 之后 6 次全部未采用）。
- **21:13 新规矩落地**：`onnx_opinion.md` **移入仓库根目录**、只保留 6 块（0 口径 / 1 版本表 / 2 部署 3 轮实测表 / 3 峰值数据表（真人件为列）/ 4 结论 / 5 追加内容单行），**每次追加前先备份到 `ai_buckup/onnx_opinion.md_<时间>.md`**；规矩写进 `todo.md`。旧 168 行原件已备份，新文件 76 行（v1.2/v1.3 拆进表 1/2/3，第 5 块 3 行）。
- **自曝（计数与两次崩溃的真因）**：①我把正样本 76 **心算成 75** 报「差 1 件」，逐音色重数证明日志无矛盾；②Kokoro 第一次崩 = **commit 耗尽**（可用提交 1,487 MB，`DefaultCPUAllocator` 连 1 MB 都要不到，属 HB-047 同族），第二次崩 = **我直跑没带 `HF_HOME/HF_ENDPOINT/HF_HUB_DISABLE_XET`**（常驻纪律第 10 条）；③合成脚本加「已存在即跳过」门，GSV 非逐位确定，重合成会让「两次交集」失效。
- **重启三服务时的两次自曝**：①`Start-Process` 的 `WorkingDirectory` 写成 `git\GPT-SoVITS-main`（真路径是仓库内 `JarvisAi\GPT-SoVITS-main`）→ 参数无效，api_v2 没起；②llama 直跑 `llama-server.exe` **没带你的 `PATH=BinDir` + `GGML_Vulkan` 环境**，`ggml-vulkan.dll` 加载不到、进程秒退，且我 `Start-Process -WindowStyle Hidden` **没重定向日志 → 现场无日志可读**。照 `llm/startLlama.ps1 -Ctx 24576` 起后 `/health` ok（`n_ctx_slot = 24576`），4 灯全绿（wake 0.75 / whisper small cpu / llm online / gptsovits）。当前可用提交 2,448 MB、总提交 30,308 MB。
- **第 2 项代码已改未验**：`_jarvis_windows()` 改为认「记录 pid ∪ **跑 jarvis 专属 profile（`.tmp\chrome_profile`）的 Chrome 进程 pid**」，`jarvis_pids()` 同口径（Q32/Q34 边界：你的窗口用你自己的 profile，永不匹配）；根因是 launch pid 是秒退的 launcher，窗口归已有实例（轮 2 实测 21200 vs 10848）。验证排在下面。
- 4dda29 docs(AI): onnx_opinion 按 21:13 新规矩重排进根目录，收口 v1.3 扩数据重训 —— **已本地 commit，未 push**
- **第 2、3 项改码 + 实测通过（21:44-21:49）**：窗口计数认 jarvis profile 的 Chrome 进程 pid（实测你窗口不计、我起 1、杀自己成功、杀你的被拒、杀后忘掉 pid）；play_first_video 改 CDP 判定（关键词「稻香」→ BV1oj411G7sR → 有video:true du:405；直达 URL 复用窗口判定；播完关掉我起的窗口，全程无视觉无点击）。jarvis 已用新码重启（pid 16716），4 灯全绿。
-  221012 fix(AI): 窗口计数认 jarvis profile 的 Chrome 进程，播歌判定改 CDP 证据（去视觉点击）—— **已本地 commit，未 push**
