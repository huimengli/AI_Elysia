# 第 3 轮（真机 · 你 15:36:43 那一次 + 15:35 的花海链）· 转录半句「播放」

- **时间**：15:34:50–15:36:53。三服务全在。
- **期望**：同四条判据。
- **实际（逐字日志）**：
  - `15:34:50 [TTS] queued: 6 segments, first sound 14309 ms, played 30.10 s, total 60779 ms` **她播了 30.10 s（first sound 14.3 s 才出声）**
  - `15:34:59 [Tool: web_search] 搜索「花海 歌曲 播放」已用 baidu 打开浏览器` **LLM 去搜「花海 歌曲 播放」= 转录里没拿到可播的歌名结构，走了搜索路径**
  - `15:35:36 [ABORT] set by websocket_endpoint:540 thread=Thread-7 (_run)` **中止标志由网页端置位（页面上的停止），不是语音**
  - `15:35:40 [Tool: play_music] 关键词「花海」→ 最多播放第一支：BV1E23n6QEBs（标题「花海 - 周杰伦 【无损音质】」，210980 播放，共 20 条，30002 字节）` **若你说的是「花海」，判据③ 中 ✓**
  - `15:36:43 [Wake] peak 0.778` → `15:36:45 [爱莉希雅] Wake word detected!` → `ack played (2.58 s)` → `15:36:49 [STT] Speech detected (rms=0.0281)` → **`[STT] Recording aborted.` → capture 1 s → `Recorded 1.5s`** → `15:36:53 [You] 播放` **判据② FAIL、判据① FAIL（只剩「播放」两个字）**
  - `15:36:21/15:36:45 [Duck] CDP 连不上（没有我起的窗口带 --remote-debugging-port）` 两次同证据；`15:36:50 peak 0.790`（F 块 `wake_peak` 末值 0.79）。
- **结果**：**FAIL**（判据②①不中；③「花海」那步中；④待你耳确认）。
- **备注**：`llm_secs` 这一轮 **17.5 s**、`tts_secs` **50.65 s**、`total_secs` **76.8 s**。`E` 块实测：`play_music n=2 fail=0 avg=63.14 s`、`web_search n=1 fail=0`、`music_control n=1`、`type_text n=1`、`read_page n=1`。`jarvis_windows=0`（我起的窗口现在为 0，播歌窗口已关）。
