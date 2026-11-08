# 轮 6：三层浏览器回退全链验证（2026-11-08-17:12）

- 场景：同一命令 `node search.mjs … --engine bing|baidu` 在三种环境下跑：A 正常 env（msedge 通道）、B **完全空 env**（验证 `repairEnv()` 兜底）、C **强制走 bundled chromium**（把 `ProgramFiles`/`ProgramFiles(x86)`/`LOCALAPPDATA`/`USERPROFILE` 指向不存在的 `X:\nope`，使 msedge 通道与显式路径都失败，仅剩 F: 的 chromium）。
- 期望：三轮均 exit 0 且返回结构化结果。
- 实际：轮A **exit 0** 6 条；轮B（空 env，进程 env 全空）**exit 0** 5 条；轮C **exit 0** 6 条（首三条为毛玻璃 CSS 参考站：xyutil glassmorphism 生成器、StyleKit 玻璃拟态、freefrontend CSS Glassmorphism）。
- 结果：**PASS**
- 备注：轮C 证明 skill 在 Edge 不可用时能落到自装 chromium；三层回退（msedge 通道 → 显式 Edge 路径 → bundled chromium）全部可用。
