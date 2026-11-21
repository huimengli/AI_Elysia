# 批次结论 · 2026-11-21-10-39-00（P1 · 不需要你参与）

口径照实：**18 轮 PASS / 1 轮 FAIL / 3 轮照实记判据未达**。计划 20 轮，实际 22 轮 —— 第 7 项审计挖出新洞（`TOOL_MAP` 直取键 → `KeyError`），补了 1 轮直调；部署侧 3 轮里环境音判据 PASS、长噪/键盘/13 次件判据未达，照实记。

| 轮 | 项 | 结果 |
| --- | --- | --- |
| 1-6 | watchdog 子进程监督 | **6 轮全 PASS**。含真 jarvis 在 watchdog 下跑 25.5 s；判读口径修正：被杀后读到的 259 = STILL_ACTIVE，不是真实退出码 |
| 7-8 | 真机搜索落地（baidu 首选 / bing 落地） | **PASS**。baidu 落到搜索页（标题「爱莉希雅 官方_百度搜索」）；bing 落地 `cn.bing.com/search`（www→cn 重定向）。**真机反爬本轮未发生** |
| 9-10 | 兜底代码路径（打桩） | **PASS，标「非真机反爬」**。wappass 验证页 → 「换 bing 兜底」；两引擎都失败 → 「没有搜到」，不出现「已用 baidu」 |
| 11 | 关窗 3 轮口径的第 1 轮 | **PASS（平凡通过照实写）**：关前 0、关后 0，没有窗口可关 |
| 12 | 到达结尾（`max_wait=420`） | **FAIL（照实记）**：时间前进 True、ct 0→388.8、弹幕关、640x360，**到达结尾未达成** —— 我 `max_wait` 定小于片长 506 s |
| 13 | 到达结尾（600 s） | **PASS**：`ct=505.2 / du=505.166`（537 s）。`video.play()` 不生效 → 走 CDP 受信点击 |
| 14 | 到达结尾 + 播完关窗 + 关后 0 | **PASS（全判据第一手）**：`taskkill` SUCCESS 关掉自己起的 pid 3584，关后我起的窗口 0；独立复核 profile 认 pid = 0 条，窗口只剩 DSH（不计） |
| 15-17 | sherpa 能量门 3 轮 A/B（离线，已有音频） | **PASS 3 轮（照实记）**：span+0.015 → 门 1/6；concat+0.015 → 1/6（空/乱码 4）；**config 现值 span+0.008 → 2/6 与无门持平、空/乱码 0（最好）**；whisper 3/6 最好 → **引擎与阈值都不改** |
| 18、19、22 | 部署侧管线 3 轮（长噪/环境音/键盘/13 次件，`v0.9b @0.75`，逐件 3 实例） | **照实记判据未达**：**环境音 3 轮 × 3 实例全 0 PASS**；长噪 3 轮里 2 轮出现 1 次检出（峰值 0.771/0.756 踩在 0.75 上）；键盘 3 轮全出现（峰值最高 0.809 = 真唤醒 0.82 量级）；13 次件稳定 3（期望 13）。与 `onnx_opinion.md`:106 的 v0.9b 召回轴（83%→40%）一致，**不是管线新问题**；「期望 13」在 5 s 冷却下数学上限约 7，照实记 |
| 20 | `_coerce` 42 工具全量审计 | **PASS**（含挖出真洞）：省略键注入 0、null 未强制 0、类型未强制 0；审计自己的洞照实记（lambda 直取键看不到函数中文默认） |
| 21 | 34 项必填无默认空参数直调（补丁后） | **PASS（KeyError 通道关闭）**+ 照实记 4 处真实副作用：`web_search("")` 起窗口、`focus_window("")` 聚焦「星之翼」、`set_clipboard("")` 后还原（存的 37 字）、**`click_page_text("")` 把 DSH 窗口（pid 5244，不是我起的）点到必应搜索页**（按 back 后回到「P2以上项目问题列出 — DSH 本地构建」页，已复原）。音量/亮度/鼠标坐标**没被动过** |

## 批次结论（照实，不粉饰）

1. **watchdog 是本轮唯一的净新增能力**：起子进程用**文件重定向**（不用管道）、pid 判活 + `GetExitCodeProcess`、超时 `TerminateProcess`、jarvis 自己写 `.clean_exit` 当「正常收尾」凭据。`start_all_in_one.bat` / Monitor 消费面**还没接**，照旧 open。
2. **`_coerce` 的第二个洞是真的，且已修**：`TOOL_MAP` 直取键让模型省略必填键变成 `KeyError` → 失败文案灌回模型（2026-11-08 关掉的幻觉通道从这条缝又漏）。规则分两档照实：字符串必填灌 `""`（走工具自己的如实分支）、数字/布尔必填**不注入不执行**（灌 0 是音量/亮度/鼠标坐标的真实副作用）。
3. **CDP 页面工具没有「只动我起的窗口」这道闸（HB-053，open）**：`find_on_page`/`click_page_text` 连上任何 CDP 页面就动，且空串在 DOM 里是通配（`indexOf("") == 0`）。我把你手上的 DSH 页面点走了 —— 这条照实立案，本轮不修。
4. **部署侧验收在现役 `v0.9b @0.75` 上未达（3 项）**：长噪、键盘、13 次件。这是**模型的召回/判别轴**问题，与台账一致；**换模型（v1.3）/调阈值是你的决定**（`onnx_opinion.md`:113），本轮**没改 config、模型、阈值**，已追加 need_user.md Q42。
5. **能量门在 config 现值（span+0.008）下与无门持平、消除空/乱码**；sherpa 仍不如 whisper（2/6 vs 3/6）→ **`stt.engine: whisper` 照旧不动**（禁用区）。
6. **沙箱边界照实记三条**：①piped stdio 被拒 → `_jarvis_profile_pids()` 返回空集（`capture_output=True` = piped），关窗在我这边只能走**记录 pid**；②jarvis 起的窗口随我的驱动进程结束一起没（job object），轮 13 的窗口例外活着（pid 3584）→ 轮 14 的关窗第一手由它提供；③`Path.home()` 在空 env 里崩（`tts.py:33`）→ 驱动必须带 `USERPROFILE/MPLCONFIGDIR/HF_*`，这是环境事实，不是 jarvis 缺陷。
7. **自曝第 57-69 处**（本轮 13 处，逐条在 record 里）：JS 模板字面量转义、单引号吞路径、多余逗号、argparse REMAINDER 吞 `--no-want`、JS/Python 引号混用、stub 返回单串解包崩、`t in want` 对 `False` 崩、裸中文注释行写进 router（SyntaxError）、JS 对象没有 `.get`、数组尾 `"";` 连犯两次、`node:fs/promises` 没有 `existsSync`、piped stdio spawn 拿到 null、把 60 s 限时程序当长跑驱动用。

## 更正（2026-11-21 12:04，追加不改上文）

第 7 条里的 `--no-want` 是笔误，应为 **`--no-wait`**：argparse 的 `REMAINDER` 把 `--no-wait` 吞进 `cmd`，`CreateProcess` 把 `--no-wait` 当可执行文件 → `FileNotFoundError: [WinError 2] 系统找不到指定的文件。`（看起来像路径问题，实为参数被吞）。改法是 `main()` 里手工按 `--` 切分，不走 argparse REMAINDER（自曝第 59 处）。
