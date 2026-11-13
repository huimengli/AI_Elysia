# 验证轮 3 — 浏览器 UI 切回 v0.9 + 0.75（零截图）+ 重启后一致

- **时间**：2026-11-13 11:04-11:05
- **场景**：Playwright 连接器打开 `http://127.0.0.1:7860/` → 点「设置」tab → 下拉选 v0.9 → 看阈值自动预填 → 点「保存设置」→ 读 health / `config.yaml` / console；随后**重启 `:7860`** 再读 health
- **期望**：① 下拉恰好 3 项，且服务端把「当前模型」标为 selected；② 选 v0.9 后阈值框自动变 0.75；③ 保存后 health = `aili_xiya_v0.9.onnx` / 0.75 且 4 灯 online；④ `config.yaml` 落盘为 v0.9 + 0.75；⑤ 重启后仍是 v0.9 + 0.75（**现役必须回到 v0.9 + 0.75**）；⑥ console 0 error
- **实际**：
  1. 下拉 3 项，v1.0c 为 `[selected]`（承接轮 2 的服务端状态）：
     ```
     - option "v0.3（2026-10-17 PASS：recall 0.94 / fp 0.09，推荐阈值 0.70）"
     - option "v0.9（现役，推荐：14 次件 12 / 近音 fp 6 / 对抗 4 / 环境音 0，阈值 0.75）"
     - option "v1.0c（音节窗约定：判别轴首次达标 fp 1 / 对抗 3 / 定标与环境 0，召回塌，可用区间 0.70-0.72，推荐 0.72）" [selected]
     ```
  2. 选 v0.9 后 `#s-wake-threshold` = `0.75`（`pickWakeModel()` 预填生效）
  3. 保存后 toast 文本 `设置已保存，唤醒模型已重载`；health：
     `{"online":true,"listening":true,"model":"aili_xiya_v0.9.onnx","threshold":0.75,...}`，`lamps: wake=True listening=True asr=True llm=True tts=True`
  4. `config.yaml` wake 块：`model: ...aili_xiya_v0.9.onnx`、`threshold: 0.75`（`model_options` 3 条保留）
  5. **重启后**：`{"online":true,"listening":true,"model":"aili_xiya_v0.9.onnx","threshold":0.75,"peak":0.796}`，4 灯 online
  6. `browser_console_messages(level=warning)` → `Total messages: 2 (Errors: 0, Warnings: 0)`
- **结果**：**PASS**（①-⑥ 全部满足）。零截图（只用 snapshot / find / evaluate / curl）。
- **备注**：UI 全程用 `browser_snapshot`（`combobox [ref=e152]`）、`browser_find`（「唤醒词」）、`browser_evaluate`（读 toast 与阈值框），无截图。`browser_click` 用 `button:has-text("保存设置")`；`button.settings-btn.primary` 会同时命中弹窗里的「保存」按钮（strict mode violation），改精确文本后通过。
