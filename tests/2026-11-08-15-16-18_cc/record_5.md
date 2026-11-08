# 轮 5：curl 断点续传 + 手工布局（2026-11-08-17:10）

- 场景：`curl.exe -L --retry 20 --retry-all-errors --retry-delay 5 -C - -o F:\playwright-browsers\headless.zip <官方 zip>`（后台 job pwsh-5），完成后用 `Expand-Archive` 解到 `F:\playwright-browsers\chromium_headless_shell-1243`（目录名 = `name.replace(/-/g,'_') + '-' + 版本大版本`，与 playwright `EXECUTABLE_PATHS['chromium-headless-shell']['win-x64'] = ['chrome-headless-shell-win64','chrome-headless-shell.exe']` 布局一致）。
- 期望：zip 完整落地、可执行文件在 playwright 期望路径上。
- 实际：curl 从 1.87 MB 续传至 **120,200,717 字节（100%），exit 0**；解压后 `F:\playwright-browsers\chromium_headless_shell-1243\chrome-headless-shell-win64\chrome-headless-shell.exe` 存在（212 MB）。探针 `chromium.launch({headless:true})` + `page.goto(bing)` → **launch OK version 153.0.8010.12**，页面标题 `glassmorphism pink CSS - 搜索`，`li.b_algo` 计数 10。
- 结果：**PASS**
- 备注：`PLAYWRIGHT_BROWSERS_PATH` 已在 skill 的 `ENV_DEFAULTS` 里兜底为 `F:\playwright-browsers`（C: 只剩 6 GB，且 playwright 官方安装器在此网络下跑不完）。
