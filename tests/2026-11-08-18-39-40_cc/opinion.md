# 批次结论（tests/2026-11-08-18-39-40_cc，验证 3 轮）

- `future/AI_UI` → `main` 合并完成（merge commit `99aeaf1`，**本地合并、未 push**）。Elysia UI、500 修复、`llm.py` 补丁、skill/三服务/config 台账与全部 records/tests 批次现在都在 main 上。
- 冲突处理原则：5 处冲突全部**保留两侧内容**（append-only：`records/`、`tests/`、`tests/opinion.md`、`todo.md`、`progress.md`），`tree.md` 用合并后的 `git ls-files` 重建；代码文件由 git 自动合入 AI_UI 侧，`git diff --stat future/AI_UI -- <code>` 为空（完全一致）。
- 3 轮：轮1 一致性 + `py_compile` 全 0；轮2 main 上 UI 已是 Elysia 版（200/42,420 B、`爱莉希雅`、`--pink`/`petal`、无 CDN、无 `J.A.R.V.I.S.`）；轮3 连续 5 轮对话跨窗口 8 触发压缩，5 条 response 全出无 500（第 5 条是真实摘要），TTS 200/258,604 B RIFF。
- 合并坑（同切分支）：`git merge` 会被**未提交的 todo.md 改动阻断**（`error: Your local changes ... would be overwritten by merge`）→ 先 commit 本需求 record+todo 再合并；重启 `:7860` 仍需 `Stop-Process` 掉旧 python。
- 当前服务：llama `:8080`、GPT-SoVITS `:9880`（job pwsh-10，pid 4436）、**jarvis `:7860` = job pwsh-23（合并后的 main 代码）**。真人测试可直接在 main 上做：UI 是 Elysia 版且含 500 修复。
