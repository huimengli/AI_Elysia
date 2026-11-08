# 批次结论（tests/2026-11-08-15-16-18_cc，验证 3 轮）

- skill 已恢复可用：bing PASS、baidu PASS（均 exit 0 + 结构化结果）；duckduckgo 为本机网络不可达（exit 5 正确上报），补充 bing 轮 PASS。
- 根因与修复：`channel:'msedge'` 依赖 `ProgramFiles`/`ProgramFiles(x86)` 环境变量，run_code 子进程 env 为空 → 路径拼成 `undefined\...` → 误判「无浏览器」(exit 3)。修复：`repairEnv()` 补 5 个变量 + 新增显式 Edge `executablePath`（x86/x64）回退，再落到 bundled chromium。Edge 实测版本 143.0.3650.139。
- Playwright 自带 chromium（195.6 MiB，`chrome-win64` + `chrome-headless-shell`）正在后台下载（`cdn.playwright.dev`，进度慢；`ms-playwright` 目前仍只有 `.links`/`__dirlock`）。装好后将增加第三层可用浏览器；当前 skill 靠系统 Edge 已可用。
- 影响：T6 的在线风格检索当时未真实执行；现在可执行（用 bing/baidu）。

## 追加（2026-11-08-17:12，chromium 装成后的 3 轮）
- 轮4：C: 清理后 ENOSPC 消失，但 `npx playwright install` 两次（前台 540 s / 后台 job pwsh-3）都在 40% 被 `ECONNRESET` 打断，官方安装器在此网络跑不完 114.6 MiB。
- 轮5：`curl -C -` 断点续传把 zip 拉满（120,200,717 B，exit 0），`Expand-Archive` 解到 `F:\playwright-browsers\chromium_headless_shell-1243`，`chrome-headless-shell.exe`（212 MB）就位；探针 launch + bing 浏览 OK（版本 153.0.8010.12）。
- 轮6：三层回退全链验证 exit 0（msedge 通道 / 空 env 兜底 / 强制 bundled chromium），bundled 轮拿到真实玻璃拟态 CSS 参考站点。
- 结论：**在线搜索 skill 完全恢复**：可用浏览器 = 系统 Edge 143.0.3650.139 + 自装 Chromium Headless Shell 153.0.8010.12（F: 盘）。duckduckgo 仍因本机网络不可达（exit 5 正确上报）。
