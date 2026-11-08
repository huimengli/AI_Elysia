# 轮 1：JS 语法与接口契约（2026-11-08-14:52）

- 场景：CSS/文案改造后，页面 `<script>` 必须仍可解析，且 JS 使用的端点与 `jarvis/web.py` 路由逐字一致。
- 期望：`node --check` 通过；JS 端点 ⊆ web.py 路由；WS 路径 `/ws`。
- 实际：`node --check` 退出 0（脚本 16503 B）；JS 端点：`/api/mute`、`/api/providers`、`/api/providers/`、`/api/events?limit=100`、`/api/settings`；WS `new WebSocket('ws://'+host+'/ws')`。web.py 路由：`/`、`/api/providers`、`/api/providers/{provider_key}`、`/api/settings`、`/api/mute`、`/api/events`。逐字一致。
- 结果：**PASS**
- 备注：未改动 `jarvis/web.py`；JS 仅改字符串字面量（状态/提示文案中文化），控制流与端点未动。
