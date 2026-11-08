# 批次结论（tests/2026-11-08-18-16-33_cc，验证 3 轮）

- UI 差异确证：**main = 旧版**（`J.A.R.V.I.S.` 标题，52,655 B / 1,174 行，Google Fonts `@import`，无粉色主题/花瓣动画/中文文案）；**Elysia 版只在 `future/AI_UI`**（`爱莉希雅` 标题，41,769 B / 829 行，`--pink`+`petal`+`backdrop-filter`，无 CDN，全中文文案）。刷新 http://127.0.0.1:7860 即可对比。
- 切分支要点：`git checkout main` 会被本地已改的 `todo.md` 阻断（两分支内容不同），先 commit 再 checkout；重启 `:7860` 需 `Stop-Process` 掉旧 python（`job_kill` 只杀 pwsh 外层）。
- 风险提醒：main 上**没有** 17:53 的 500 修复与 llm.py 补丁，真人测试聊到 8 条触发压缩时会重现「保存设置后管线报错」。建议看 UI 后切回 `future/AI_UI` 再做语音真人测试。
- 三服务不受分支影响：llama `:8080`（gitignore 的 `llm/`）、GPT-SoVITS `:9880`（job pwsh-10）、jarvis `:7860`（main 代码，job pwsh-21）。
