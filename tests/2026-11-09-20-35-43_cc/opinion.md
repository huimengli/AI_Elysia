# 批次结论（tests/2026-11-09-20-35-43_cc，验证 3 轮）

- 需求：状态灯在「语音识别」左侧再加一盏「唤醒」（`records/2026-11-09-20-35-43.md`）
- 改动：`jarvis/wake.py`（模块级 `state` 发布在线/监听/score/peak/last_detect）、`jarvis/web.py`（`_health_snapshot()` 由三灯变四灯，`wake` 排最前）、`jarvis/static/index.html`（`lamp-wake` 插在 `lamp-asr` 前 + `pollHealth` keys 加 `wake`，让出麦克风时黄灯）
- 三轮：① `GET /api/health` 真值（`online=true/listening=true/threshold=0.65/last_detect=21:03:00`，另三灯无回归）；② 服务端返回 HTML 的灯序与 JS 绑定（`lamp-wake` 行号紧邻 `lamp-asr` 之前，keys `['wake','asr','llm','tts']`）；③ 进程内直调快照，核对 `keys=["wake","asr","llm","tts"]` 与**未加载态**优雅退化（`online=false`、`last_detect=""`、不抛异常）
- 结果：**3/3 PASS**
- 结论：数据源（后端快照）与 UI（DOM 灯序 + 轮询绑定）两侧都闭合，在线/离线/让麦克风三态都有明确视觉语义；复用既有灯样式，无新增 CSS，`asr/llm/tts` 行为零回归。
- 已知边界（不算缺陷）：`threshold` 改动后需重启 Jarvis 才在 `state` 里刷新；UI 灯 5 s 轮询，`peak` 是 3 s 日志窗峰值（非逐帧显示）。
