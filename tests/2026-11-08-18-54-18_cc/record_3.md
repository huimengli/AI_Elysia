# 轮 3：空 content 兜底改为工具汇报，重启复测（2026-11-08-19:04）

- 场景：`_call_openai_provider` 记录 `executed=[(name,result)]`，兜底改 `_tool_report()`（无工具 → 「我处理好了。」；有工具 → 「我执行了 X、Y：末条结果首行 80 字」），并把模型返回的 `Done.`/`OK`/`已完成` 当空处理；重启 jarvis（**job pwsh-30**）后 WS 连发 2 条中文 chat（用轮1 的真实转写文本）。
- 期望：不再出现裸「Done.」，回复是中文整句。
- 实际：**裸 Done. 计数 0**。R1 `我执行了 type_text、type_text、focus_window：No window matching '记事本' found.`；R2 `我执行了 type_text、press_key、focus_window：No window matching '记事本' found.`；`GET /` 200 / 42,420 B（爱莉希雅 / --pink / petal），无「主模型失败」。
- 结果：**PASS**
- 副作用披露（真人测试同样会发生）：测试真机执行了工具 —— `type_text` 往桌面打字（`我需要在明天下午三点准时参加会议，请确保携带笔记本电脑和钥匙。` / `请在明天下午三点时提醒我准备好会议用品` / 复述句）、`press_key ctrl+t`、`focus_window 记事本`（找不到窗口）。2B 模型把「记一下」理解成往记事本打字，真人测试建议先按「中止」。
