# 轮 1 · 2026-11-17 19:11-19:20 · jarvis 端到端播放「月声尽,心灯明」→ **FAIL**

- **时间**：前拍 19:11:04，发消息 19:11:04，收流在 t+55.9 s 超时退出（驱动 v1 缺陷），后拍 19:12:00-19:12:01
- **场景**：三服务由我 19:09 重启（jarvis 新实例 pid 19188 侧的 trampoline 7376），**4 灯全 online**（wake `aili_xiya_v0.9.onnx` + 0.75 / asr whisper small cpu warm / llm llama.cpp `:8080` / tts GPT-SoVITS `:9880`）；经 `ws://127.0.0.1:7860/ws` 发一句「播放「月声尽,心灯明」」，播放完全交给 jarvis 自己的 LLM 工具链
- **期望（判据五项）**：①导航到最播放第一支（`BV1RMYF6kEze`）②关弹幕 ③最低档（点过「360P 流畅」+ 宽度 640，高度随源比例）④时间前进 + 播完信号（BV 号变化）⑤播完关掉我自己起的窗口

## 实际（逐条证据）

1. **jarvis 选了旧工具 `play_first_video`，不是已验证的 `play_music`**
   WS：`{"type":"tool","name":"play_first_video","args":{"url":"https://search.bilibili.com/all?keyword=月声尽,心灯明"}}`（t+10.9 s）
2. **关键词被吞**：`jarvis2.log` L88
   `[Tool: play_first_video] 已用 chrome.exe 带参数启动 https://search.bilibili.com/all?keyword=，并复读到窗口证据：搜索 - 哔哩哔哩_bilibili - Google Chrome（进程 9180）（匹配关键词 `
   —— 启动 URL 停在 `keyword=`，中文尾巴被 `_extract_url`（只吃 ASCII）丢掉，「匹配关键词」后是空的
3. **`fetch_page` 中文 URL 崩**：`jarvis2.log` L89
   `[Tool: fetch_page] 读取网页失败 https://search.bilibili.com/all?keyword=月声尽,心灯明：'ascii' codec can't encode characters in position 17-19: ordinal`
4. **页面停在搜索页，没有任何播放**：播完拍 CDP
   `{"标题":"搜索 - 哔哩哔哩_bilibili","地址":"https://search.bilibili.com/all?vt=13974521","ct":null,"du":null,"paused":null,"ended":null,"分辨率":null,"弹幕checked":null,"autoplay":null}`
   → ①未导航到视频 ②弹幕未关 ③分辨率未设 ④ct/du 皆 null（无播放、无播完）⑤窗口未关（窗口拍：`[(330638, 9180, '搜索 - 哔哩哔哩_bilibili - Google Chrome')]`，pid 9180 存活）
5. **无 `tool_result`**：WS 只收到 `tool` 事件，收流 45 s 超时（驱动 v1 的收流超时太短，工具是阻塞式的，一首歌 255 s 起）
6. **后拍拍太早（驱动 v1 缺陷）**：19:12:01 我记「我起的窗口数 0」，而窗口在之后出现，稍后实测 1（pid 9180）——**当时的 0 不可作数**

## 结果：FAIL（五项全 FAIL，根因当场定位，未迁就结果）

## 备注（本批修的动作，19:25）

- `play_music` 加 `keyword` 入参：歌名或搜索页里的 `keyword=` 都走 B 站 API（`order=play`）取最播放第一支的直达 BV 链接再导航（丙方案，无视觉坐标、无点击）
  —— 顺带自曝：`first_bilibili_video` 返回的是**带修饰的句子**（`最多播放第一支：https://…（1768005 播放…）`），我第一版用 `startswith("http")` 判会把**成功查询误报成查不到**，改成 `_extract_url(direct)` 后再判
- `play_music` 的 schema 写成「**播歌唯一工具**」，`play_first_video` 的 schema 明写「播歌不要用我，走 `play_music`」；`keyword` 列为首选参数
- `fetch_page` 先对 path `quote(safe="/%")`、query `quote(safe="=&%")` 编码再请求（轮 1 第 3 条根因）
- 离线复测（探针，无副作用）：`first_bilibili_video('月声尽,心灯明')` → `BV1RMYF6kEze`（**1,768,005 播放**，共 20 条）；`fetch_page('...keyword=月声尽,心灯明')` 不再 ascii 崩，返回搜索页正文
- 驱动 v2（`.tmp/e2e_round2.py`）修收流超时（45 s → 300 s，预算 600 s）与后拍（连续 60 s 每 5 s 拍窗口/CDP 状态）
