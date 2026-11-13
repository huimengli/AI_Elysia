# 批次结论 tests/2026-11-13-00-12-17_cc（第 4 项：设置里可切换唤醒 ONNX，3 轮）

用户 2026-11-13 00:12 第 4 项「将唤醒 onnx 也做进设置中，允许用户选择，暂时只提供 git 中有的选项(0.3,0.9,1.0c)」→ 实现 + 3 轮验证（10:30 开工，11:05 完成）。

## 1. 实现（三处，一次到位）

- **`config.yaml` `wake_word.model_options`**：3 条 `label / model / threshold`。列表是**数据驱动**的：`GET /api/settings` 直接由它生成选项，「只列 Git 里的 3 项」由配置保证，未入 Git 的 v1.0 / v1.0b / v1.1 不出现在 UI。推荐阈值 = `ai_buckup/onnx_opinion.md` 表 3 的实测结论（v0.3 0.70、v0.9 0.75、v1.0c 0.72），不是拍脑袋。
- **`jarvis/wake.py` 热重载**：`_reload = threading.Event()` + `request_wake_reload()`；监听循环每轮检查该标志，重读配置，模型键变化时重建 `Model(...)` 并 `reset()`，**mic 流复用**（chunk_size 不变），阈值变化只改 `cfg`。`state["model"] / state["threshold"]` 同步更新，`/api/health` 立刻可见。重载后 2 s 冷却覆盖 `Model()` 的 1 s 随机播种 warmup（HB-032），换模型瞬间不会误触发。重建失败（路径缺失 / onnx 载入失败）只打印并**保留旧模型**，监听不退出。
- **`jarvis/web.py`**：GET 增加 `wake_model_options`（含 `current`）；PUT 在 `wake_word` 变更后 `_save_config` 然后 `request_wake_reload()`。
- **`jarvis/static/index.html`**：「唤醒词」组加模型下拉（`#s-wake-model`），`loadSettings()` 填充选项并选中服务端当前项；`pickWakeModel()` 把阈值框预填成该模型的推荐值（用户仍可改）；`saveSettings()` 把 `model + threshold` **一起**提交，toast 变「设置已保存，唤醒模型已重载」。

## 2. 3 轮结果

| 判据（record 指定） | 轮 1（GET） | 轮 2（PUT→health，不重启） | 轮 3（浏览器 UI + 重启） |
| --- | --- | --- | --- |
| 3 选项 + 推荐阈值 + current | 3 项，`current` = v0.9 ✓ | — | — |
| 换模型后 health 变 v1.0c/0.72、4 灯 online | — | `model=aili_xiya_v1.0c.onnx threshold=0.72`，`wake/asr/llm/tts` 全 True，`listening=True` ✓ | — |
| 日志重载行 + 分数来自新模型 | — | `[Wake] reloaded …` + 峰值 0.717/0.523（非 0 缺省）✓ | — |
| 切回 v0.9+0.75、config 落盘、重启后一致 | — | — | toast「已重载」+ health v0.9/0.75 + `config.yaml` 落盘 + **重启后仍 v0.9/0.75** ✓ |
| console 0 error | — | — | `Total messages: 2 (Errors: 0, Warnings: 0)` ✓ |

**3 轮全 PASS。现役已切回 v0.9 + 0.75，`config.yaml` 与重启后一致。**

## 3. 结论与规矩

1. **切换必须 model + threshold 成对写入**：v1.0c 的可用区间是 0.70-0.72，若换模型留 0.75 会直接塌召回（14 次件 11、基线 8）；UI 预填 + PUT 成对提交 + 循环成对读取，三处都锁死这一点。
2. **预测键名依赖 filename stem**：openwakeword 用 `Path(path).stem` 作 predictions 键（`aili_xiya_v1.0c`），循环里必须用同一规则，否则 `predictions.get(key, 0)` 恒为 0 = 永不触发。本轮日志里峰值非零是这条正确的直接证据。
3. **零截图在浏览器路径成立**：`browser_snapshot` + `browser_find` + `browser_evaluate` + `curl` 足够读下拉选项、阈值框、toast 与 4 灯；`browser_click` 目标要用精确按钮文本（`button.settings-btn.primary` 会同时命中弹窗「保存」，strict mode violation）。
4. 服务在浏览器验证期间未被停止（本次是 UI 路径，不是打分/训练，不触发虚拟内存约束）。

## 4. 后续（未做，留给 9:00 清单其余项）

- 20 轮明确测试补齐（`2026-11-12` 前两批 1/20、1/3）需用户配合；
- Jarvis「看屏幕」改走浏览器快照（零截图）；
- `need_audio.md` 补录后重训 v1.0d（召回短板 = 音节窗正样本仅 45 件）。
