# 批次结论（tests/2026-11-08-18-54-18_cc，验证 3 轮）

- 真人语音「变成 You + Done.」有两个独立成因：**① `stt.py` 把 `language="en"` 写死**（中文口语被英文解码，短语音只能拼出 `You` 这类碎片；事件库 `user "You" source=voice` 是铁证）；**② `main.py` 342-343 行在模型工具轮后返回空 content 时字面兜底 `"Done."`**。同一段合成中文音频：en → `'I love you, Alicia. Yes. Tomorrow is the 3rd day of the meeting…'`，zh → `'爱利西亚 对 明天下午三点开会 记得带笔记本和钥匙'`，None → 同 zh（detected zh 0.967）。
- 修复（`fix(AI)`）：`stt.py` 语言取 `config.yaml` 的 `stt.language`（新增 `language: zh`，缺省 zh，两处 transcribe 同步）；`main.py` 加 `_looks_understandable()` 空/碎片守卫（无 CJK 且 ≤20 字符 → 播「我没听清，请再说一遍。」，不调 LLM）；`_call_openai_provider` 记录 `executed` 并用 `_tool_report()` 兜底（无工具 → 「我处理好了。」；有工具 → 「我执行了 …：结果首行」），`Done.`/`OK`/`已完成` 视为空。3 轮全 PASS，WS 回复裸 Done. 计数 0。
- 真人测试提示：2B 模型会把「记一下」理解成 `type_text` 往记事本打字 + `focus_window`（找不到「记事本」窗口）→ **语音测试会在桌面真实打字**；先按「中止」（WS `{"type":"interrupt"}` / UI 中止 / Esc）。「爱莉希雅」仍常听成「爱利西亚」（2B 身份识别遗留）。
- 当前 jarvis = **job pwsh-30**（含全部修复）；llama `:8080`、GPT-SoVITS `:9880`（job pwsh-10，pid 4436）未重启。C 盘已由用户清理。
