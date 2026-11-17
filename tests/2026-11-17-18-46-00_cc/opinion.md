# 批次结论 · 2026-11-17-18-46 · jarvis 端到端播放「月声尽,心灯明」（`record_1..4.md`）

**你要的是 3 轮（18:46 答复：「重启三服务，跑 jarvis 端到端 3 轮」）。结果：轮 1 FAIL、轮 2 部分 PASS（4 项）、轮 3 FAIL、轮 4 全五项 PASS —— 轮 4 是我加的越界诊断轮，用途与越界都记在 `record_4.md`。3 轮口径下没有全项 PASS 轮。**

## 三轮 + 诊断轮

| 轮 | 结果 | 直接证据 |
| --- | --- | --- |
| 1 | **FAIL** | jarvis 选旧工具 `play_first_video`，启动 URL 停在 `.../all?keyword=`（中文尾巴被 `_extract_url` 吞），`fetch_page` 中文 URL 报 `'ascii' codec can't encode`，页面停在搜索页（`ct/du/paused` 全 null），窗口未关 |
| 2 | **4 项 PASS + 第 5 项间接证明** | jarvis 自选 `play_music` + `keyword`，页面 `BV1RMYF6kEze`、`弹幕checked=false`、`640x338`、`ct` 172.3→231.6 前进；我的后拍在 `ct=231.6`（距结尾 24.4 s）结束，之后窗口消失、记录 pid 21200 已死 |
| 3 | **FAIL** | jarvis 先 `find_on_screen("月声尽")` 并如实报「找不到」（好），再用 `play_music`；**工具只跑 ~110 s**（歌长 256 s），播报「播放失败，已关闭我自己起的窗口。」；失败原因被 `result[:120]`/`result[:200]` 截断，**读不到** |
| 4（诊断轮） | **全五项 PASS** | jarvis 完整播报：直达 `BV1RMYF6kEze`（1,768,296 播放）→ `danmakuChecked=false` → 点过「360P 流畅」判定 `640x338` → 受信点击播放 → **连播发生 = 播完信号**（`BV1RMYF6kEze → BV1DepY6BE1G`，t+288 s）→ kill 自起 pid 1552 进程树 9 个全 SUCCESS → 「关后我起的窗口数：0」 |

## 本批落地的三件改动

1. **`play_music` 加 `keyword` 入参**：歌名或搜索页里的 `keyword=` 都走 B 站 API（`order=play`）取最播放第一支的直达 BV 链接再导航（丙方案，无视觉坐标、无点击）
   —— 顺带自曝：`first_bilibili_video` 返回的是**带修饰的句子**（`最多播放第一支：https://…（1768208 播放…）`），我第一版用 `startswith("http")` 判会把**成功查询误报成查不到**，改成 `_extract_url(direct)` 后再判
2. **schema 引导生效**：`play_music` 写成「播歌唯一工具 + `keyword` 首选参数」，`play_first_video` 明写「播歌不要用我」→ 轮 2 起 jarvis 自己就选 `play_music`
3. **`fetch_page` 先编码再请求**（path `quote(safe="/%")`、query `quote(safe="=&%")`）；**`main.py` 工具打印不再截断**（`result[:120]` 把失败原因切掉了，WS/UI 仍保持 200 字上限）

## 未闭合（照实记，不迁就）

- **轮 3 的失败细节永久读不到**（跑的是旧打印）。轮 4 只证明「同一份代码在打印补丁后走完全程」，**没有复原轮 3**；轮 3 保持 FAIL
- **窗口计数假阴性（新记 P1）**：`_jarvis_windows()` 按 pid 匹配，Chrome 多进程下**窗口 pid ≠ 启动 pid**（轮 2 实测启动 21200 vs 窗口 10848）→ 轮 2/4 后拍「我起的窗口数 0」不可作数
- **轮 3 的 `PID_FILE` 没有新增**（`n = 22`，尾 6 无本轮 pid）→ 与上一条同一族缺陷的两面：一边漏记、一边漏计
- **驱动演进**：v1（收流 45 s 太短 + 后拍只拍一次、拍太早）→ v2（收流 300 s，仍在 t+310.2 s 超时，`tool_result` 全文没收到）→ v3（收流 400 s，轮 4 收到全文）
