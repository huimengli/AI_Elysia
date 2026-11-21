# 验证轮 1 — Monitor 路由与关闭授权闸门

时间：2026-11-21 16:03（复跑 16:12，沙箱内 TestClient 直连 jarvis.web.app）
场景：`jarvis/web.py` 新加 3 条路由（GET /monitor、GET /api/monitor、POST /api/service/stop）。用 fastapi TestClient 起 app，不碰真服务（沙箱内 8080/9880 都未监听）。
期望（design v3.1 §3/§5）：
1. `/api/monitor` 200，键含 time/os/services/jarvis_windows/metrics/tools/self_pids/lamps。
2. `os` 有提交内存 总/已用/可用 与 物理%、CPU%（A 块）。
3. 服务行含 name/label/pid/source/mem_mb/log_lines（C 块），未起时 source=「未起」。
4. `POST /api/service/stop` 对 **不是 jarvis 起的 pid**（999999）必须拒绝，`refused=true`。
5. `/monitor` 200，页面含标题与 `/api/service/stop`（关闭按钮接线）。

实际（16:12 复跑，逐字照实）：
```
[Web] Event loop captured — WebSocket broadcast ready.
[Apps] {'added': 0, 'skipped_existing': 243, 'no_target_skipped': 5, 'pinyin_filled': 227, 'total': 227}
轮1 /api/monitor 状态 200
轮1 键 ['jarvis_windows', 'lamps', 'metrics', 'os', 'self_pids', 'services', 'time', 'tools']
轮1 os {"commit_total": 27089, "commit_used": 23702, "commit_avail": 3386, "phys_total": 24382, "phys_avail": 8772, "phys_pct": 64, "cpu": null}
轮1 services [{"name": "llama", "label": "llama.cpp :8080", "pid": null, "source": "未起", "mem_mb": -1, "log_lines": 0}, {"name": "tts", "label": "GPT-SoVITS :9880", "pid": null, "source": "未起", "mem_mb": -1, "log_lines": 0}]
轮1 四灯键 ['asr', 'llm', 'tts', 'wake']
轮1 外部pid关闭 True 拒绝：pid 999999 不是本进程起的（名单里只有 ）
轮1 /monitor 状态 200 标题命中 True 关闭按钮命中 True 长度 6570
```

结果：**PASS（5/5）**。第 1 遍（16:03）四灯键是 `[]`，第 100 处自曝：四灯只在 WS 推送里加，`/api/monitor` 的快照没带；补上后复跑才有 4 个键。
备注（照实）：
- `cpu: null` 是第 1 次采样（`GetSystemTimes` 要两次采样才有差值），不是故障。
- `[Apps]` 那行是 `app_control` 首次导入建的 243 项应用索引：快照第一次调用要付这个成本，后面缓存（轮 2 的节拍问题根因之一，见 record_2）。
- 关闭闸门在沙箱内可测（拒绝外部 pid 这条测到了）；**真关自起 pid 的 taskkill 走轮 3**。「关窗全关」的 CTRL_CLOSE_EVENT 5 s 时限在沙箱不可测，照实留未测。
- 真机三件套（jarvis 起 /monitor 窗口、不最大化、窗口数 ≤3 口径一致）需要你在会话里看，照实记未测。
