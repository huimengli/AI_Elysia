# 轮 1：真人语音输入显示「You」+「Done.」的根因（2026-11-08-18:58）

- 场景：`jarvis/data/events.db`（137 行）取 voice 段；用 GPT-SoVITS 合成 6.88 s 中文 wav（`F:\Temp\zh5.wav`，TTS 200 / 440,364 B），同一音频分别以 `language=en`（现状写死）、`zh`、`None` 转写。
- 期望：定位「You」与「Done.」的来源。
- 实际：事件库里 `18:49:07 user "You" source=voice` → `18:49:16 assistant "Done."`（前一条 `18:48:59 wake`）——用户气泡里的「You」就是 STT 的真实转写文本。转写对照：`lang=en` → `'I love you, Alicia. Yes. Tomorrow is the 3rd day of the meeting. Remember to bring your notebook and key.'`；`lang=zh` → `'爱利西亚 对 明天下午三点开会 记得带笔记本和钥匙'`（内容正确，仅「爱莉希雅」听成「爱利西亚」）；`lang=None` → 同 zh，detected zh 0.967。`main.py` 342-343 行的 `return _strip_think(...) or "Done."` 与 `return "Done."` 证实：模型在工具轮后返回空 content 时，代码字面塞「Done.」。
- 结果：**PASS（根因确证）**
- 备注：`stt.py` 45/53 行把 `language="en"` 写死；`_system_prompt`（main.py 150-151 行）已要求中文，问题在输入端与兜底字面量，不在提示端。
