<!-- 已归档于 ai_buckup/todo.md_2026-11-18-12-52-45.md（126 行全量：逐条勾选 + 自曝 + 证据）。本文件只保留未完成项与最近小节。 -->

# todo（compact）

## 常驻纪律（每轮都算）

- [ ] 先落 `records/` + `todo.md` 再开工；明确测试 20 轮 / 验证 3 轮，每轮 `record_i.md` + 批次 `opinion.md` + 累积 `tests/opinion.md`
- [ ] 局部小截图允许（压小）；页面结构用 a11y/DOM；不用子智能体；commit 用 Conventional Commits（type/scope 英文 + 中文主题），先写 `.tmp/commit_msg.txt` 再 `git commit -q -F`，hash 追加 `progress.md`，**禁止 push**
- [ ] `progress.md`/`todo.md` > 100 行先归档再压缩；`tree.md` 文件增删后重建（仅非 `.gitignore`）；**追加中文一律先写 `.tmp/*.py` 再跑，不要把带反引号的中文塞进 `pwsh -c`**（12:21 与 12:25 两次把字母吃掉的事故）
- [ ] 训练/打分前停 `:7860/:8080/:9880`，跑完重启 + 4 灯复核；python 带 `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET/MPLCONFIGDIR`
- [ ] 边界样本必须 ≥3 个独立 Model 实例复测取多数（HB-032）；**不碰页面文件**（Q22：你只设 8G 分页）

## P1 · 播放 / B 站（判据五项：导航 / 关弹幕 / 最低档=点过「360P 流畅」+宽度640 / 时间前进+播完信号(BV 变化) / 播完关窗）

- [x] 2026-11-17 播放链 CDP 落地 + 20 轮（全项 PASS 4 轮：5/7/19/20）；判据两处修正（宽度 640 高度随源；播完信号 = BV 变化）
- [x] 2026-11-18 12:07 **播放控制三项实测 PASS**（暂停回读 `paused=True`、恢复 `explicit=True` 回读 `paused=False`、关闭只关我起 pid 且**关后窗口数 0**）；播歌唯一性全程 ≤1
- [ ] **到达结尾在实例存活下的复现**：轮 11/15 两次都在 t+93/105 s **CDP 断读 = Chrome 实例死亡**处，如实记 False（→ HB-048）
- [ ] **jarvis 看门狗 / 退出码落盘**（HB-049：jarvis17 播放批次中进程死亡，无退出码证据）

## P1 · 页面读取（2026-11-18 新增，本机无中文 OCR）

- [x] 12:25 `read_page` / `find_on_page` / `click_page_text` 落地（CDP 读 DOM，只碰我起窗口，无 OCR、无视觉坐标）；轮 24/25/27 **实证中文正文读出**
- [x] 12:38 分发层闸门：话里有「点击/找到」+「页面/页」→ 拒 `web_search`/`run_python`/`read_screen`/`find_on_screen`/`fetch_page`，指名 `find_on_page`/`click_page_text`（轮 26 FAIL → 轮 28 模型只调 `find_on_page`，没越界）
- [x] 12:43 修我漏的花括号（外层 `for` 右括号 → JS 求值 undefined → CDP 回 `null` → `json.loads('null')=None` → `.get` 崩）+ 非 dict 防御；直测命中 `2 处「番剧」 (100,32) (204,186)`
- [ ] **HB-050 未结案**：`click_page_text` 点了、坐标对（矩形中心 100,32）、`elementFromPoint` 点下就是目标链接的 SPAN，**地址复读没变（导航未证实）**；方案②「取 `href` + `Page.navigate` 我自己起的窗口」待做
- [ ] **Q37 待你裁决**：本机无中文 OCR（WinRT 不可用、Umi-OCR 只有 Downloads 自解压包未装、`:50015` 无监听）→ 装并常驻 Umi-OCR，还是桌面中文识别记「不做」

## P1 · 唤醒 / 训练

- [x] 2026-11-17 v1.2（交集 正20/负12=32）与 v1.3（正74/负15=89）重训：两次都「任一条不如 v0.9 → `config.yaml` 不动」，现役 `aili_xiya_v0.9.onnx` + `0.75`
- [ ] v1.2 若继续：①扩数据（正样本行占比 8.2%）②你真人音频扩正样本（真人克隆实测不可用，60 s 失控音频）③接受 v0.9 现役。**等你挑，不自行推进**
- [ ] **补 v1.3 部署 3 轮**（现 1 轮 @0.75 + 1 轮 @0.70，表 2 先写未测）→ `WTHR=0.70` 再跑 2 轮 `.tmp\probe_v09_deploy.py`
- [ ] **语音 20 轮 轮 11-20 + 语音 ducking 真人验收**（需你在麦克风前）→ `tests/2026-11-08-20-44-17_cc/record_11..20.md`（现 11/20；第 1 项 ducking 机械与 CDP 证据已到位，真人验收未测 → 整项不勾选）

## P2 · Monitor 面板 + 自定义对象设置界面（只做 design，不开工）

- [ ] design v3.0 已定（日志中枢 + 单窗口托管 + 指定关闭 + 外部接入）；开工授权等 Q31-1；自定义对象设置界面同级 P2

## P3 · 全部挂起（你 11:01 定「P2 级以下先不管」）

- [ ] Q18 剪贴板 JWT 193 字符善后、Q19 通知气泡肉眼确认、Q20「锁」真锁屏、Q36 微信登录凭据（只打开 PASS，登录阻塞）、Q24（你的窗口你自己关）、`kill_process` 英文进程名、`pyautogui.FAILSAFE`
- [x] **HB-047 结案 wontfix**（你 10:52 定：chrome 崩溃 = 内存溢出，属用户需注意）

## 21:13 onnx_opinion 规矩（永久生效）

1. `onnx_opinion.md` 放仓库根目录；2. **每次追加之前**先备份到 `ai_buckup/onnx_opinion.md_<ts>.md`；3. 只允许 6 块、顺序固定（0 规则/1 版本表/2 部署 3 轮表/3 峰值表/4 结论/5 追加内容）；4. 追加 = 直接改表 1/2/3，第 5 块每次**只写一行**；5. 数字全部来自日志，未测写「未测」；6. `tree.md` 随之重建。

## 最近小节（2026-11-18 10:17 批次，37 条记录，非语音）

- **2a 打开浏览器** `[x]`、**2c 自定义对象** `[x]`（19b 编造名字→诚实拒绝列名字→19c 导航成功）、**2d 搜索 baidu 首选** `[x]`（bing 兜底未触发 = 未测）、**2e github** `[x]`、**2f b站** `[x]`、**第 3 项播放控制** `[x]`、**20 轮非语音** `[x]`；
- **2b 打开微信** `[ ]`：只打开 PASS（轮 23 复读进程 Weixin），登录被 **Q36** 阻塞；
- **第 1 项 ducking** `[ ]`：机械 + CDP 回读证据到位（`[Duck] 已暂停…paused=True` / `已恢复…paused=False`），真人麦克风验收未测；
- 本地 commit **2ab1ebe**（37 轮收口）+ **383ea5e**（控制字符修复 + progress 归档）；`tree.md` 516 文件。
