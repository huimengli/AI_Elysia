# 轮 3：新增 get_time 工具，「现在几点」答对时间（2026-11-08-20:12）

- 场景：真人反馈「这次回答了,但是回答是天气」→ `jarvis/tools/system.py` 加 `get_time()`（本地日期/时间/星期），`router.py` 加 TOOL_MAP 与 schema，`main.py` 系统提示加「问时间/日期用 get_time，不要用 get_weather」。
- 期望：问时间得到时间答复，不再调用 get_weather。
- 实际：单元检查 `schemas 33 / get_time in schemas: True / in map: True`，`dispatch('get_time', {})` → `2026-11-08 20:09:20 星期日`；真人语音 217 行 `现在几点了` → 218 行 `现在是 2026年 11月 8 日 20 点 10 分，星期日。`；220 行 `幾秒` → `Tool: get_time` → 221 行 `現在是晚上 8 點 12 分，星期日。`；`GET /` 200 / 42,517 B（title 爱莉希雅）。
- 结果：**PASS**
- 备注：whisper 会输出繁体（`幾秒`/`現在`），「爱莉希雅」仍常听成「爱利西亚/爱里西亚」；真人测试会真机 `type_text` 打字，先按「中止」。当前 jarvis = **job pwsh-50**。
