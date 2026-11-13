# 轮 5 — `get_weather`（中文地名）
- **时间**：2026-11-13 12:29:50（服务级首验）+ 13:25（复测）
- **场景**：浏览器输入框打字「北京今天天气怎么样」+ 工具级直调 `get_weather('北京')`（零截图）
- **期望**（HB-035 判据）：URL 全 ASCII；返回气温/湿度/风速
- **实际**：`[Tool: get_weather] Beijing：Smoky haze，气温 11°C，湿度 50%，风速 4 km/h`（日志 47 行），直调同结果
- **结果**：**PASS**
- **备注**：`format=j1` 是纯 ASCII JSON，中文文案在 Python 侧拼；`quote(location, safe="")` 消掉 URL 里的非 ASCII。这条也是**本轮唯一外网可达的端点**（见轮 3）。
