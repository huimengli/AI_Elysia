# 验证轮 3 — 2026-11-09-20-35-43 唤醒灯（key 顺序与离线态优雅退化）

- 时间：2026-11-09 21:06
- 场景：进程内直调 `jarvis.web._health_snapshot()`（`.tmp\probe.py`，由 `.tmp\bats\run30.bat` 跑，`PYTHONPATH=%CD%` 修掉首版 `ModuleNotFoundError: No module named 'jarvis'`）。此进程里 `jarvis.wake` 是**全新导入**，唤醒线程从未启动 → `state` 保持默认值，正好检验「模型未加载」这条离线路径
- 期望：① `key` 顺序为 `wake → asr → llm → tts`；② 未加载时 `wake.online=false`、不抛异常、`detail` 不出现假「上次触发」
- 实际：
  ```
  state_default= {"online": false, "listening": false, "model": "", "threshold": null,
                  "score": 0.0, "peak": 0.0, "last_detect": 0.0}
  keys= ["wake", "asr", "llm", "tts"]
  wake= {"online": false, "listening": false, "model": "", "threshold": null,
         "score": 0.0, "peak": 0.0, "last_detect": "",
         "detail": " / threshold None / peak 0.0"}
  ```
- 结果：**通过**
- 备注：
  - `keys` 顺序与轮 2 的 DOM 灯序一致（数据源和 UI 两侧都核对，不靠猜测）；
  - `last_detect` 在 0 值时被格式化成 `""`，`detail` 里的「上次触发 …」片段被条件跳过 → 不会出现 `上次触发 00:00:00` 这种假信号；
  - `online=false` 走前端灰灯分支（`if (!s.online)`），与轮 2 的 JS 判定闭合；
  - 全链路无异常：`_health_snapshot()` 只读 `getattr(wake_mod, "state", {})`，即使 `state` 缺失也返回 `{}` 而不 KeyError；
  - 对照轮 1（真实运行进程 `online=true` / `listening=true` / `last_detect=21:03:00`）：在线与离线两态都验证过，`threshold 0.65` 与 `config.yaml` 一致。
