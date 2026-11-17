<!-- 已归档于 ai_buckup/todo.md_2026-11-17-15-51-09.md（157 行全量备份）；本文件只保留去重未完成项与最近小节 -->

# todo（compact）

## 常驻纪律（每轮都算）

- [ ] 先落 `records/` + `todo.md` 再开工；明确测试 20 轮 / 验证 3 轮，每轮 `record_i.md` + 批次 `opinion.md` + 累积 `tests/opinion.md`
- [ ] 局部小截图允许（压小）；页面结构用 a11y/DOM；不用子智能体；commit 用 Conventional Commits（type/scope 英文 + 中文主题），先写 `.tmp/commit_msg.txt` 再 `git commit -q -F`，hash 追加 `progress.md`，**禁止 push**
- [ ] `progress.md`/`todo.md` > 100 行先归档再压缩；`tree.md` 文件增删后重建（仅非 `.gitignore`）
- [ ] 训练/打分前停 `:7860/:8080/:9880`（提交量硬约束），跑完重启 + 4 灯复核；python 跑带 `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET/MPLCONFIGDIR`
- [ ] 边界样本必须 ≥3 个独立 Model 实例复测取多数（HB-032）；**不碰页面文件**（Q22：你只设 8G 分页）

## P1 · 播放 / B 站（判据五项已定：导航 / 关弹幕 / 640x360 / 时间前进+到达结尾 / 播完关窗）

- [ ] 2026-11-17-15-48 用「月声尽,心灯明」（`BV1RMYF6kEze`，1,765,329 播放，20 条）跑 3 轮 → `record_18..20.md` + 批次/累积 opinion
- [ ] 2026-11-17-14-01 修 `play_first_video` 假阴性：直连 BV URL 时不走 Route B 视觉点击（标题一开始就是视频页，「标题未变→失败」不成立）
- [ ] 2026-11-17 **jarvis 端到端验收**：你跑 `start_all.bat`（`-c 24576` 已定）后由 jarvis 自己走完 3 轮，4 灯复核
- [ ] 2026-11-17 播放链收尾：`video.play()` 被 Chrome 自动播放策略挡住，必须受信点击播放按钮 —— 兜底路径需在真实 jarvis 进程里复现（沙箱外）

## P1 · 唤醒 / 训练

- [ ] 2026-11-17-13-52 按**交集**重算 `aili_xiya_v1.2` clip 集合（负样本任一次 ≥0.70 不入库、正样本两次都合格才入库；现 clips 33 = 正21/负12，score 33 = 正20/负13）
- [ ] 2026-11-17-13-44 `train` + `eval`（你挑时间停三服务后跑）；判据：25 真呼唤 ≥ v0.9(14)、真人近音 fp ≤1、合成对抗 ≤4、定标纯噪声 0、环境音期望 0、边界 ≥3 实例取多数；**不如 v0.9 就不改 `config.yaml`**（`v0.9 + 0.75` 不动）
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
