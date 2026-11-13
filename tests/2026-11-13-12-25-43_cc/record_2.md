# 轮 2 — HB-035：`get_weather` 中文地名 URL quote + `format=j1`

- **时间**：2026-11-13 12:29:50
- **场景**：修完后在浏览器输入框打字「北京今天天气怎么样」（零截图），并用独立 python 直调 `get_weather('北京')`
- **期望**（`hard_bug.md` HB-035 方案）：URL 里不出现非 ASCII 字节；中文文案在 Python 侧拼装；查询成功返回天气
- **实际**：
  - 修前（12:12:23 连 3 次，日志 1771-1773）：`天气查询失败：'ascii' codec can't encode characters in position 15-17: ordinal not in range(128)` —— 中文地名直接拼进 URL，且 `format=` 里也带中文。
  - 修后（服务级，日志 47 行）：
    ```
    [Tool: get_weather] Beijing：Smoky haze，气温 11°C，湿度 50%，风速 4 km/h
    ```
  - 独立直调复测：`Beijing：Smoky haze，气温 11°C，湿度 50%，风速 4 km/h`（同一结果）
- **结果**：**PASS**。中文地名不再崩，读数正常。
- **备注**：改用 `format=j1`（wttr.in 的纯 ASCII JSON）+ `urllib.parse.quote(location, safe="")`，`current_condition[0]` 取 `temp_C / humidity / windspeedKmph / weatherDesc`，`nearest_area` 取地名；超时从 5 s 提到 8 s。中文在 Python 侧拼，URL 全 ASCII。
