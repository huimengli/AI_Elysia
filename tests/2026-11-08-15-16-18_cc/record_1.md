# 轮 1：bing 真实搜索（2026-11-08-15:31）

- 场景：修复 `search.mjs` 的 `launch()`（补 `ProgramFiles`/`ProgramFiles(x86)`/`LOCALAPPDATA`/`USERPROFILE`/`SystemRoot` 环境变量 + 显式 Edge `executablePath` 回退）后，跑 bing 搜索。
- 期望：退出码 0，输出 JSON `{query, engine, count, results:[{title,url,snippet}]}`。
- 实际：`node search.mjs "Elysia Honkai Impact 3rd pink theme colors" --engine bing --count 8` → **exit 0**，8 条结构化结果（含 `爱莉希雅_百度百科`：「逐火十三英桀之一」；知乎 Elysia 讨论等）。无 captcha、无 error 字段。
- 结果：**PASS**
- 备注：修复前同一命令 exit 3（`no usable browser`，msedge 路径被拼成 `undefined\Program Files\Microsoft\Edge\Application\msedge.exe`）。根因是 run_code 子进程 env 为空，playwright 的 `channel:'msedge'` 路径解析依赖 `ProgramFiles` 类变量。
