# 第 1 轮：货架与连接状态探测（2026-11-12 23:45-23:47）

- 时间：2026-11-12 23:46
- 场景：`mcp_connector_catalog`（关键词 playwright + 分类「开发工具」）与 `mcp_connector_status`，看是否已有浏览器类连接器
- 期望：确认货架有 Playwright（`none` 鉴权）与 `chrome-devtools`，并确认它们**未连接**
- 实际：
  - 货架命中 **`[playwright] Playwright · 开发工具 · none — 浏览器自动化 / 页面检查 / 交互测试 / 可访问性快照`**；同分类还有 `[chrome-devtools]`（浏览器调试/网络分析/性能追踪/自动化）与 `[firefox-devtools]`（macOS 已验收）；
  - 已配置的 2 条连接都是别的项目：`json-mcp-unity`（stdio node，项目 my21Point2/truck/my21Point）与 `custom-wow-sight`（stdio powershell，全局），两条都是 `host-tools-pending`（Host 尚未注册工具）；**没有任何浏览器类连接**。
- 结果：**通过** —— 阻塞点定位清楚：不是「Chrome 必须带 `--remote-debugging-port=9222`」，而是**连接器从未安装/连接**；Playwright 连接器是 `none` 鉴权，可直连（第 2 轮验证），**不需要你改 Chrome 启动参数**。
- 备注：零截图。
