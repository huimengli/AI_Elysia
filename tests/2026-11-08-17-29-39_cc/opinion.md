# 批次结论（tests/2026-11-08-17-29-39_cc，验证 3 轮）

- 三服务全部在线：`:8080` llama-server（Qwen3.5-2B-Q4_K_M，pid 20684/16252）、`:9880` GPT-SoVITS api_v2（pid 4436）、`:7860` jarvis.main（pid 12880）。真人测试入口：http://127.0.0.1:7860 。
- 轮1 LLM PASS（裸调必须带 `chat_template_kwargs.enable_thinking=false`，jarvis 已带）；轮2 TTS PASS（200 + 314 KB RIFF wav）；轮3 Web UI/WS 全链 PASS（6 事件 + 事件落库）。
- 已知短板：2B 模型对「爱莉希雅」身份识别不稳；STT 的 cuda 因驱动版本不足回落 CPU（可用，速度较慢）；GPT-SoVITS 启动时 `MPLCONFIGDIR` 默认路径不可写（仅警告）。
- 副作用提醒：`type_text` 等工具会真实操作 PC（打字），真人测试前建议先测静音/中止（UI 的「中止」按钮 / `type:'interrupt'`）。
