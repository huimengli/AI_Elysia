# 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-18-12-20-10.md（99 行全量：逐条 hash + 结论 + 自曝 + 流水）。
     本文件为压缩版；逐轮细节在 `records/`、`tests/`，逐条 hash 完整流水在归档。 -->

## Git 提交记录（最近 12 条，**全部已本地 commit，未 push**；`git rev-list --count HEAD` = 219）

```text
2ab1ebe feat(AI): 播放控制三项实测通过 + 站点打开与播歌唯一性收口（10:17 批次 37 轮）
f2e6bdc feat(AI): 只听歌播放链走 CDP —— 关弹幕、最低分辨率、播完关掉我自己起的窗口
8127a2f test(AI): 新歌曲「月声尽,心灯明」跑 3 轮 —— 轮 18 暴露判据过死，轮 19/20 全项 PASS
6bcb386 docs(AI): 语音轮 11 落盘（转录吃尾根因链）+ 音乐唯一性新规则
0221012 fix(AI): 窗口计数认 jarvis profile 的 Chrome 进程，播歌判定改 CDP 证据（去视觉点击）
4dda29 docs(AI): onnx_opinion 按 21:13 新规矩重排进根目录，收口 v1.3 扩数据重训
1c50ed1 fix(AI): 训练驱动补 --train_model 与 verify 路径（v1.2 不如 v0.9，config 未动）
fb873e6 docs(AI): 按交集重算 v1.2 入库集合（正20/负12=32，剔 elya pos_hello）
185b22d docs(AI): 把 5af39ad 与 520c9bd 的 hash 追加到进度台账
5af39ad feat(AI): 只听歌播放链走 CDP（关弹幕 / 最低分辨率 / 播完关窗）
520c9bd docs(AI): 13:52 三条答复与截图判据口径落盘补提交
d283fe9 test(AI): Q16 只 B 复测 v1.0c 三轮（0.65/0.70/0.72）—— 0.65 禁区，最佳 0.72，不换现役
```

## 当前未结案（口径与依据见 `todo.md`、`need_user.md`、`hard_bug.md`）

- **等你确认（status: wait）**：**Q36**（微信登录：只打开 / 你提供加密凭据 —— 我只「只打开」，不猜密码）；
  **Q18**（剪贴板 JWT 193 字符被覆盖善后）、**Q19**（通知气泡肉眼确认）、**Q20**（「锁」才真锁屏）。
  已结案口径：**Q22**（页文件不碰，8 GB 分页）、**Q29/Q32/Q34**（只认 jarvis 自起窗口 ≤3、只关自起 pid）、
  **Q31**（chrome 崩溃属内存溢出，wontfix）、**Q33**（`-c 24576` 授权改）、**Q35**（你在 jarvis 起的窗口登录一次，
  cookie 留在 `.tmp\chrome_profile`，取两次交集）。
- **P1 待办**：①语音 20 轮 **轮 11-20 + 语音 ducking 真人验收**（需你在麦克风前，
  `tests/2026-11-08-20-44-17_cc/record_11..20.md`，现 11/20）；②`find_on_screen` **中文 OCR**（HB-040 家族）；
  ③**jarvis 看门狗 / 退出码落盘**（HB-049：jarvis17 播放批次中进程死亡，无退出码证据）；
  ④**到达结尾在实例存活下的复现**（轮 11/15 两次都在 t+93/105 s CDP 断读 = Chrome 实例死亡处，如实记 False）；
  ⑤**bing 兜底路径**（本轮 baidu 从未被挡，记未测）。
- **P2**：**Monitor 全系列** + **自定义对象设置界面**（design v3.0 已定，同级 P2，先不开工）。
- **open bug**：**HB-048**（CDP 断读、播歌唯一性起点复用、整句录音、CDP 重连）；**HB-049**（进程死亡无退出码证据；
  WS `WebSocketDisconnected` 已修）；**HB-040**（`_coerce` 架空中文默认参数，未全解决）；
  **HB-047 closed/wontfix**（chrome 崩溃 = 内存溢出，你裁决「不需要修，需要用户注意」）。
- **禁区/边界（长期）**：`v0.9 + 阈值 0.75`、`stt.engine: whisper`、`stt.hot_bias: false`、`is_half: false` 不动；
  **0.65 禁区**；边界样本 ≥3 独立 Model 实例取多数（HB-032）；单探针串行；**页文件不碰（Q22）**；
  **不最大化窗口**、点击需在任意窗口尺寸准确；jarvis 起窗口 ≤3、播歌唯一 ≤1、关后 0；只认 jarvis 自起窗口
  （profile `.tmp\chrome_profile` = 身份）；剪贴板先存后还；`kill_process` 只到记事本；**禁止 git push**；
  不自行发明命名；`onnx_opinion.md` 6 块 + 每次追加前备份到 `ai_buckup/`。

## 最近结论（细节在 `tests/`、`records/`；全量在归档）

- **2026-11-18 10:17-12:07（37 条记录，非语音）**：2a-2f 站点与微信只打开、播放控制三项（暂停/恢复/关闭，CDP 回读为证、
  关后我起的窗口数 0）、播歌唯一性全程 ≤1 **实测 PASS**；播歌 5 判据 ①导航 ②关弹幕 ③最低分辨率（640x360/640x338 两种都判过）
  ④时间前进 成立，⑤关窗轮 15 达成，**「到达结尾」未复现**（两次都被 Chrome 实例死亡打断，如实记 False）。
  闸门与修码见 `tests/2026-11-18-10-17-23_cc/opinion.md`；自曝（三次吃掉代码头部、一次发明不存在的
  `_visible_windows_all()`、驱动 60 s 硬 break、10b 编造叙述、**here-string 反引号转义把字母吃掉**）全部落盘。
- **2026-11-17 播放链 20 轮**：全项 PASS 4 轮（5、7、19、20），FAIL 6 轮全部当场暴露根因并修；判据修正两处
  （最低分辨率 = 点过「360P 流畅」+ **宽度 640**，高度随源比例；**播完信号 = BV 号变化**）。
- **2026-11-17 v1.2/v1.3 重训**：两次都「任一条不如 v0.9 → `config.yaml` 不动」，现役保持 `aili_xiya_v0.9.onnx` + `0.75`；
  v1.2 交集 正20/负12=32、v1.3 交集 正74/负15=89，@0.75 部署轴 13 次 10（v0.9 12）、长噪 0、环境音 0。
  数字全部来自日志；自曝三次解析 bug（`endswith('入库')` 把「不入库」判成入库、正样本 76 心算成 75、交集上界数学不可能）。

- **2026-11-18 12:25-12:52 · 中文读取改走 CDP（P1 路线实证）+ 页面点击未结案（→ record_10/11.md）**：
  本机没有可用中文 OCR（12:25 实测：WinRT 不可用、Umi-OCR 只有 Downloads 自解压包**未装**、`:50015` 无监听
  `WinError 10061`）→ 提 **Q37** 待你裁决；我起窗口改走 CDP 读 DOM。新工具 `read_page`/`find_on_page`/
  `click_page_text`（只碰我起窗口，无 OCR、无视觉坐标）+ 分发层闸门（「点击/找到」+「页面/页」→ 拒
  `web_search`/`run_python`/`read_screen`/`find_on_screen`/`fetch_page`）。**实测 PASS**：轮 24（baidu 搜索页
  中文正文读出 + `play_music` 被动词闸门挡回）、轮 25/27（B 站首页栏目与卡片读出、回复照正文列出）、
  轮 28 模型**只调 `find_on_page`**（闸门生效，没越界）。**未结案 HB-050**：`click_page_text` 直测说
  「已用 CDP 受信点击 @(x=100,y=32)」，坐标核对正确（`a[href=…/anime/]` 矩形中心 = 100,32、
  `elementFromPoint` 点下就是该链接的 SPAN），**地址复读没变** → 导航未证实；下一步方案②「取 `href` +
  `Page.navigate` 我自己起的窗口」。**自曝**：我拼接 JS **两次漏花括号**（外层 `for` 的 `}`、诊断 JS 箭头函数体的 `}`），
  都表现为「表达式返回 `null`」（第一次误当工具逻辑 bug）；`pwsh -c` 带反引号的中文串被转义打断（追加没执行）；
  「no-op」edit 删掉 `s, e = evaluate(RESUME_JS)` 的换行 → `SyntaxError`（第四次同类事故）。教训：JS 拼接后先用
  最小表达式自测（`(() => JSON.stringify({a:1}))()`）。12:44 你要求「先暂停并落盘」：驱动轮次已停；
  jarvis20 + llama `:8080` + api_v2 仍在跑（是否停来腾内存由你定）。本地 commit hash 见下一条台账。

- 383ea5e docs(AI): 修复 here-string 反引号转义吃掉的字母，归档压缩 progress.md —— **已本地 commit，未 push**（rev-list = 220）