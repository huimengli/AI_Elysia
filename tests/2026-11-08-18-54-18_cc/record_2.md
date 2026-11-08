# 轮 2：修语言与空转录守卫，复测转写与守卫（2026-11-08-19:00）

- 场景：`stt.py` 语言改取 `config.yaml` 的 `stt.language`（新增 `language: zh`，缺省 zh，两处 transcribe 同步）；`main.py` 新增 `_looks_understandable()`：含 CJK 即通过，无 CJK 且长度 ≤20 视为「没听清」→ 播「我没听清，请再说一遍。」、记 system 事件、不调 LLM。`py_compile` 全 0。
- 期望：同一中文 wav 转写为中文；守卫拒绝 `You`/`Done.`/`ok` 这类碎片。
- 实际：`transcribe_audio(audio)` → **'爱利西亚 对 明天下午三点开会 记得带笔记本和钥匙'**（cuda 载入失败 → CPU 回退照常）；守卫用 AST 抽出函数单测：`You`→False、`You.`→False、`Done.`→False、`ok`→False、`OK, I will do it.`→False、`明天下午三点开会记得带钥匙`→True、`好的，我知道了。`→True、`I love you, Alicia. Yes.`→True（长英文仍放行）。
- 结果：**PASS**
- 备注：`soundfile` 在本 venv 坏（`No module named '_soundfile_data'`）→ 探针改用 stdlib `wave` 解 wav；`TranscriptionInfo` 属性是 `language` / `language_probability`（不是 `lang`）。
