# 轮 1 · 2026-11-16-16-58-20（第 6 条：视觉塔 + 多模态 + 保留 OCR，3 轮之 1）

- **时间**：16:55 重启 9880（`is_half` 回 false，`start9880_1655.log`）；16:57 代码落地；16:58 探针跑视觉与 OCR
- **场景**：新增 `jarvis/tools/vision.py` 的 `describe_screen(question)`（整屏 `pyautogui.screenshot()` → PNG → `chat_image` 走 llama.cpp 带 `--mmproj`），`llm.py` 加 `chat_image`（OpenAI 内容数组 `text` + `image_url` data URI，`enable_thinking: false`，`max_tokens 256`，`timeout 120`）；router 注册 33 个工具，description 说「OCR 不够用时用（找控件/封面/图标/布局）」，**参数规则写在 `question` 上、只说一次**；OCR 的 `read_screen`/`find_on_screen` **保留不动**
- **期望**：视觉与 OCR **互补** —— 视觉认得出 OCR 读成乱码的东西，并给出可点击坐标
- **实际**：
  - `ast.parse`：`llm.py` 107 行 / `vision.py` 52 行 / `router.py` 378 行全过；schema 工具数 **33**，`TOOL_MAP` **33**，无缺项，`describe_screen` 标签「看屏幕画面」
  - `describe_screen("屏幕上有哪几个可见窗口？各是什么程序？")`（耗时 37.3 s，截图 214,020 字节）回答：
    - 「**Google Chrome 浏览器**，标题 `QuietLink 远程控制`，中心坐标 (900, 200)」
    - 「**QuietLink 远程控制**主界面，『刷新客户端列表』按钮 (200, 400)、『退出登录』按钮 (200, 700)」
    - 「**IntelliJ IDEA** 控制台，位于屏幕右侧」
  - 同屏 `read_screen` OCR 对照（同一时刻）：`QuietLink 远 程扌 空 制 台 | 462,26`（**「控制」读成「扌空制」**）、`继 续 ， 写 到 60 童 一 DSH*jtY*ö × | 202,26`、`PassMark 0 更 新 小 说 | 274,125`、`搜 云 盘 | 432,12`
  - 提交量（同口径）：前 上限 30,283 / 已用 27,365 / **可用 2,918 MB**；后 已用 27,778 / **可用 2,569 MB**（探针 python 进程临时占用；llama 带 mmproj 的 PF 单独读为 3,797 MB，本轮 `.ps1` 因 llama 多进程数组取标量失败，改在轮 3 用单 PID 读法）
  - 4 灯（16:55 复测）：`wake=True asr=True llm=True tts=True`，`model=aili_xiya_v0.9.onnx thr=0.75`
- **结果**：**达标**。互补性有硬证据：**同一屏 OCR 把「QuietLink 远程控制」读成 `远 程扌 空 制 台`，视觉认对了程序名并给出按钮坐标**（OCR 给不出「刷新客户端列表」这个控件）。OCR 保留（`read_screen` 仍是读文字的首选）。
- **备注**：副作用 —— 探针在 `.tmp/screens/` 写 1 张截图（被忽略，不 commit）；无窗口操作、无进程启动。视觉一次回答 37.3 s（比 OCR 慢，用于「找东西在哪」，不是每步都用）。`is_half: true` 实测**无收益**（省 7 MB、实时率 1.6-1.87 波动无稳定差）→ **不采用**，`tts_infer.yaml` 保持 `is_half: false`（你已回改，我没再动，该文件被 gitignore 不入库）。
