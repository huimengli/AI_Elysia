# 轮 1：LLM 链（llama.cpp :8080）（2026-11-08-17:31）

- 场景：确认 :8080 已监听并加载正确模型；跑 chat 探针。
- 期望：`GET /v1/models` 返回 Qwen3.5-2B-Q4_K_M；chat 有非空 content。
- 实际：`/v1/models` → `C:\Users\楼听\Desktop\git\JarvisAi\llm\models\Qwen3.5-2B-Q4_K_M.gguf`（capabilities completion+multimodal）。**裸请求（无 `chat_template_kwargs`）返回 `content: ""` + `finish_reason: length` + 60 全在 `reasoning_content`**（模型在 thinking）。带 `chat_template_kwargs:{enable_thinking:false}` → **content 非空**（「艾露莎·卡彭特，风纪委员长与最强魔女。」）。jarvis `main.py:264-270` 正是用 `extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}}`（config `enable_thinking: false`），故链路正确。
- 结果：**PASS**（注意：外部裸调 8080 必须带 enable_thinking=false，否则 content 为空）
- 备注：2B 模型对「爱莉希雅」身份识别不稳（把名字认成其它角色），与链路无关，属模型能力。
