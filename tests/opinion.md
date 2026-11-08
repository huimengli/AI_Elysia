# 测试总结论（累积）

## 2026-10-17-15-5x v0.3c 唤醒词验收（verify 第 3 轮）

- 脚本：`_t2_verify_onnx.py 400 aili_xiya_v0.3`（pwsh-7，全测试集 800 条 = 400 pos_te + 150 negadv_te + 150 negx_te + 100 noise_te + 100 预留/重复集内）
- 模型：`openWakeWord/output/aili_xiya_v0.3/aili_xiya_v0.3.onnx`（steps=3000，特征 24000+57600 行流式窗）
- 结果：pos mean/max = 0.807/0.888；neg mean/max = 0.453/0.833
  - 阈值 0.4: recall 1.00 / fp 0.57；0.5: 1.00/0.38；**0.6: 0.97/0.20；0.7: 0.94/0.09 ✅；0.8: 0.67/0.01**
- 结论：**PASS**（阈值 0.7，recall≥0.9 且 false≤0.1）。对比 v0.3（0.7: 0.87/0.05 recall 不足）、v0.3b（0.7: 0.98/0.16 fp 超标）——v0.3c 新内容+噪声同时守住两侧。
- 后续：已接入 `config.yaml wake_word.model` + threshold 0.7，Jarvis 重启生效。


# 批次结论（tests/2026-11-08-14-12-32_cc，验证 3 轮）

- 3 轮全 PASS：JS 语法 + 端点契约、页面加载 + 无外部资源、WS 事件渲染路径（node 桩驱动）。
- 接口契约零改动：JS 端点与 `jarvis/web.py` 路由逐字一致；`web.py`/`main.py` 未修改。
- 主题落地：HUD 青蓝色 → 爱莉希雅樱粉/淡紫/暖金 + 深紫玻璃拟态；中文化 UI 文案；删除 Google Fonts `@import`（离线可用）；樱花飘落 + `prefers-reduced-motion` 降级。
- 局限（真实缺口，不虚报）：本机无可用浏览器（`playwright-online-search` 报缺 `chrome-headless-shell-1243` 可执行文件；`npm exec playwright install chromium` 未能完成）、`web_fetch` 无外网 → **在线风格检索未能真实执行**，配色取自任务内给定的爱莉希雅色板；**未做真实浏览器目视验收**。
- 建议：用户启动 Jarvis（`:7860`）后浏览器验收外观；若要真实浏览器验证，需先安装 Playwright chromium（约 150 MB，需外网）。


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


# 批次结论（tests/2026-11-08-17-29-39_cc，验证 3 轮）

- 三服务全部在线：`:8080` llama-server（Qwen3.5-2B-Q4_K_M，pid 20684/16252）、`:9880` GPT-SoVITS api_v2（pid 4436）、`:7860` jarvis.main（pid 12880）。真人测试入口：http://127.0.0.1:7860 。
- 轮1 LLM PASS（裸调必须带 `chat_template_kwargs.enable_thinking=false`，jarvis 已带）；轮2 TTS PASS（200 + 314 KB RIFF wav）；轮3 Web UI/WS 全链 PASS（6 事件 + 事件落库）。
- 已知短板：2B 模型对「爱莉希雅」身份识别不稳；STT 的 cuda 因驱动版本不足回落 CPU（可用，速度较慢）；GPT-SoVITS 启动时 `MPLCONFIGDIR` 默认路径不可写（仅警告）。
- 副作用提醒：`type_text` 等工具会真实操作 PC（打字），真人测试前建议先测静音/中止（UI 的「中止」按钮 / `type:'interrupt'`）。
