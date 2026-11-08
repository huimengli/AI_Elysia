# 轮 2：合并后 UI / API / WS（2026-11-08-18:46）

- 场景：`Stop-Process` 释放 `:7860`（job pwsh-21 的旧 python）后重启 `jarvis.main`（**job pwsh-23**，合并后的 main 代码）。
- 期望：main 上也是 Elysia 版 UI，API 与 WS 正常。
- 实际：`GET /` **200 / 42,420 B**，`<title>爱莉希雅</title>`、`--pink`/`petal` true、无 `@import`、含 `向爱莉希雅说`/`逐火十三英桀`，**无 `J.A.R.V.I.S.`**；`/api/settings` 200（active=llamacpp、stt small）；WS `chat` → **RESPONSE「我是爱莉希雅，一个充满智慧与灵性的助手。」**。
- 结果：**PASS**
- 备注：`jarvis/static/index.html` 磁盘 42,597 字符 → 线上 42,420 B（含 UTF-8 转码差异，与 T6 的 42,363 B 记录口径一致）。
