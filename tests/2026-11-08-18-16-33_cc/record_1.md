# 轮 1：切回 main 后页面差异（2026-11-08-18:20）

- 场景：`git checkout main`（首次 checkout 被本地改动阻断：`todo.md` 已改且两分支内容不同 → 先 commit `c071d73` 再 checkout 成功），停掉 `:7860` 旧 python 后重启 `jarvis.main`（job pwsh-21），抓 `GET /` 与 T6 版页面（`F:\Temp\ui_elysia.html`）对比。
- 期望：main 返回旧版 UI（`J.A.R.V.I.S.` 标题、无 Elysia 主题、有 Google Fonts `@import`）。
- 实际：`GET /` **200 / 52,825 B**（页面 52,655 字符 / 1,174 行），`<title>J.A.R.V.I.S.</title>`，`--pink` **false**、`petal` **false**、`@import` **true**（`fonts.googleapis`），文案标记只有 `J.A.R.V.I.S.`。Elysia 版（future/AI_UI，快照）为 **41,769 字符 / 829 行**，`<title>爱莉希雅</title>`、`--pink`/`petal`/`backdrop-filter` 均 true、无 `@import`，中文文案标记 `爱莉希雅, 逐火十三英桀, 向爱莉希雅说, 发送, 中止, 聆听中, 待机`。
- 结果：**PASS**（差异确证：main = 旧 UI；Elysia 版仅存在于 `future/AI_UI`）
- 备注：`git show main:jarvis/static/index.html` 52,655 B / `future/AI_UI` 41,769 B，与线上抓取一致。
