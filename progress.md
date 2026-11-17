# 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-17-11-58-00.md（101 行全量：逐条 hash + 结论 + 自曝）。本文件为压缩版：hash 索引（最近 45 条，结论见归档与 records/tests）+ 当前未结案状态。 -->

## Git 提交记录（最近 45 条，**全部已本地 commit，未 push**；结论细节在归档与 `records/`、`tests/`）

```text
197803c docs(AI): 把 07251b4 的上下文修正追加到台账
07251b4 docs(AI): 实测 -c 24576 = 3,476 MB 后把上下文建议改回 16384（图不进主上下文）
3929ed9 docs(AI): 把 b9492e4 的上下文区间结论追加到台账
b9492e4 docs(AI): 上下文合理区间用实测 token 判定 —— 建议 -c 24576（省 ~1,630 MB），单位口径更正
bd01ebb docs(AI): 把 7d733f8 的播放 3 轮结论追加到台账并开 Q32
7d733f8 test(AI): 丙方案追加 3 轮 —— 数据侧通了，窗口边界是新的真问题（我两条前置判断作废）
c7a4bc4 docs(AI): 把 3b153c9 的优先级盘点结论追加到台账
3b153c9 docs(AI): Q31 答复落盘 + 未完成 todo 优先级盘点（Monitor 降 P2，先不开工）
adb6514 docs(AI): 把 5a89934 的 Monitor v3.0 结论追加到台账
5a89934 docs(design): Monitor v3.0 —— 日志中枢 + 单窗口托管 + 指定关闭 + 外部接入的可行性边界
f5b4a1d docs(AI): 把 f867084 的 Monitor 设计结论追加到台账
f867084 docs(design): Monitor 面板设计 v2.0（只 design，不开工，内容决定权交回用户）
ac82b48 docs(AI): 关闭所有服务的执行结果落盘（7860/8080/9880 全部不通，可用 12,408 MB）
bbc0acc docs(AI): 落盘窗口上限/pid 记录结论与关闭服务的执行口径
e758788 feat(AI): 记录自起窗口 pid + 上限只数 jarvis 自起窗口，同实例共享 pid 时拒绝杀进程
dd93752 feat(AI): 播放走直达 URL 导航 + 浏览器窗口上限 3，校验只认被聚焦的窗口
2792acf fix(UI): send 要求 readyState===1 不再断线吞消息，补 aria-live 与中文活动文案
72f395e fix(AI): open_url 加 --no-sandbox 让浏览器真开窗口，视觉坐标解析改取前两个整数
22cde20 feat(AI): 接上视觉塔（describe_screen + 图片消息），OCR 保留作文字读取
dc803cb docs(AI): 把 4327eea 的 hash 与沙箱窗口站定论追加到台账，todo 归档入备份
4327eea fix(AI): open_url 假成功改为窗口标题复读，窗口证据改进程内 ctypes
58ae173 docs(AI): 把 6c7ab8e 的 hash 与应用表 8 轮结论追加到台账
6c7ab8e feat(tools): 本机应用表入库 + open_app 先匹配列表，拼音索引解决 ASR 名称听不准
0f4346e docs(AI): 把 f05c9c5 的 hash 与 32 工具 20 轮结论追加到台账
f05c9c5 fix(tools): 全部 32 个工具 20 轮测完，封掉 4 条新的「跑了就算成功」，并按规矩摘掉子智能体
e42f03a docs(AI): 把 a671bfa 的 hash 与 20 轮前 10 轮结论追加到台账
a671bfa fix(tools): 修掉 20 轮暴露的 3 条工具层缺陷（音量虚假成功 / 屏幕读取 GBK 崩 / 天气 ascii 崩）
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
- 播放链修复 本地 commit：**81bf17c** `feat(AI): 播放链按最多播放取第一支，复用/导航只认 jarvis 自起窗口，-c 降到 24576`（9 files：`app_control.py` + `start_all.bat` + record 12-01-00 + need_user + todo + `record_8.md` + 批次/累积 opinion + tree）。**①** `first_bilibili_video` 走 API `order=play`（你原话「按照最多播放来」）→ 实跑「最多播放第一支 `BV1Ki4y1y7HC`，**9488894** 播放，29786 字节」（比服务端 HTML 266,710 省 8 倍）。**②** `open_url` 复用与 `navigate_url` 选窗口**只认 `_jarvis_windows()`**，只有你的窗口时如实「不聚焦、不输入」（消除打进 pid 16732/15416）。**③** `start_all.bat` `-c 65536` → `24576`（CR 50/LF 50/非 ASCII 0）。**第一次真跑通**（record_8）：`open_url` 起自起窗口 pid 9952 → `navigate_url` **1.0 秒**标题变视频页；`manage` 计数 1（共 2，你的不计）。**未取证**：`<video>` 播放状态（时间条没截到；OCR `:50015` 未开、WinRT 不可用、llama 已杀）。**两条判断作废**：`navigate_url` 在沙箱可验通（真原因是敲进 DSH 的 Electron 窗口，不是注入落沙箱窗口站）；复用改对后不再打进你的窗口。**自曝**：改 ② 时删了 `_visible_windows` 导入 → `L250` `NameError`，测试当场暴露后补导入。pid 9952 窗口仍在桌面（计数 1）。`v0.9+0.75` 未动，页面文件未动（Q22）。**已本地 commit，未 push**。
- 全量重训 v1.2 本地 commit：**cb262e0** `feat(AI): 全量重训 v1.2 方案落盘 + train_config_v12 + 驱动脚本（复用既有训练链，不造新约定）`（4 files：record 12-20-00 + todo + `training/_t4_full_retrain.py` + tree）。家底实测：13 版特征 npy 齐、`.tmp/v11tts` **141 件 / 7 音色**、`rir` 10 件、`background/speech` **30 件旧件**（10-13 22:21-22:25）、`background/noise` 由驱动生成 **24 件**（12:28）。驱动 `--step bg/synth/score/clips/feat/train/eval` 复用既有 6 脚本、`V11` 覆写指向 `aili_xiya_v1.2`、**非 0 即停**（`py_compile` rc=0；`--step bg` 的 `make_noise(24)` 成功、`make_speech` 遇 `:9880` 拒连 rc=1 如实停）。**自曝两处**：①「noise/speech 目录都不存在」是**路径查错**（真路径带 `background\` 前缀，speech 有 30 件旧件）；②commit 正文写「新增两件」，**`train_config_v12.yaml` 实际没进 git**（`.gitignore:11 openWakeWord/*`，13 份旧 yaml 全未入库 → 符合仓库约定，未用 `-f`），已在 record 追加 12-31 披露。另记一条坑：含转义反斜杠的中文长串塞进 `python -c` 会 `SyntaxError` → 追加没跑、commit 被静默跳过（HEAD 未变）。**已本地 commit，未 push**。
- 播放链修复 + 3 轮重跑本地 commit：**efd56e0** `fix(AI): 修 _url_keys 对 B 站视频页的假阴性，并跑完 3 轮播放验证（导航 3/3 PASS、播放 3/3 FAIL 卡在登录墙）`（11 files：`jarvis/tools/app_control.py` + record 13-00-51 + todo + need_user Q35 + tree + `record_9..11.md` + 批次/累积 opinion）。**假阴性定因**：`_url_keys` 的 keys 对 `www.bilibili.com/video/...` 只有 `{www, www.bilibili.com}`，B 站视频页标题尾部「_哔哩哔哩_bilibili」永远匹配不上 → `open_url` 把**已打开**的页面判成「页面可能没有真的打开」。**修法**：keys 追加注册域二段`netloc.split('.')[-2]`（先剥 `:port`），单测 4 例 PASS，修后 3 轮 `open_url` 全走「复用我自己起的窗口（匹配关键词 bilibili）」+「已聚焦窗口」，不再起新实例。**3 轮结果**：导航 3/3 PASS（地址栏照抄 BV 页）、播放 3/3 FAIL，真因是**B 站登录墙**（13:06 整窗截图见「扫描二维码登录」+「二维码已过期 点击刷新」，播放器在弹窗后是暗的）；jarvis Chrome 用独立 profile `.tmp\chrome_profile`（L237-244，注释刻意避开你的登录 profile）→ 无 cookie，已提 **need_user Q35**（你在 jarvis profile 登录一次 / 授权复用你的 profile / 播放降级），**我不自行决定、不动你的登录态**。**自曝**：全屏幕缩放下视觉读小字不可靠，那几次读数（`20:15→19:03`、`19:01→19:01`、`19:02→19:01`）读的是**侧栏其它视频时长标签**，不是进度条 → 播放判据改为「裁剪控制条我自己看 + 两次读数前进」。内存实测（你跑的 `start_all.bat`）：4 灯全 online、llama **`-c 24576` / 3,587 MB**、python 5,892 + 1,836 MB、chrome 12 进程 2,165 MB、可用提交 **3,167 MB**；窗口 2/3（我起），共 3 个。**页文件未动（Q22）**、`v0.9 + 0.75` 未动。**已本地 commit，未 push**。
- todo.md 归档 + 去重本地 commit：**15c5d45 → amend 后见 git log -1** chore(AI): todo.md 归档 + 未完成项去重（86 -> 73，文件 220 -> 111 行）。全量备份 i_buckup/todo.md_2026-11-17-13-11-17.md（220 行），顶部留归档注记；三步 compact 的真实数字：160 → 124 → 111 行（前两次仍超一百行，如实重做），未完成项按前 60 字符去重 86 → 73 条。历史内容全在备份，未删记录。**自曝**：第一条提交正文我写「73 -> 43」与实测不符，已用 --amend 改准（本地，未 push）。
- 驱动探测修复本地 commit：`fix(AI): 修驱动里的 :9880 探测 —— 把 404 当成"服务未就绪"会让 bg 步虚假失败`（`training/_t4_full_retrain.py`）。我的 `gsv_ready()` 用 urlopen 打 9880 根路径，GPT-SoVITS 根路径 **404** → `HTTPError` → 落 `except Exception` → 被判未就绪，而 4 灯 tts 是 online 的；改成「任何 HTTP 响应都算就绪」，实测 `gsv_ready() = True`（服务在跑）。作业 pwsh-92 已 job_kill（reason 写明），修后重跑 pwsh-95（bg→synth→score）。**自曝**：这条把服务活着判成死了，会让整条合成链虚假失败（比虚假成功安全，但会伪装成环境问题）。**顺带记一条 pwsh 坑**：含反引号 + 转义引号的中文长串塞进 `pwsh -c` 会报「Unicode 转义序列无效」，规矩是**先写 `.tmp/*.py` 文件再跑**。**已本地 commit，未 push**。
