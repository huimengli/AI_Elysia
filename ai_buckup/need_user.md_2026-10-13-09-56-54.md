# Need User（需用户确认）

## Q1 LLM 服务停摆 + 内存不足，如何恢复？(status: wait)

- 提问时间：2026-10-12-20-28
- 背景：
  - Jarvis 本体已跑通：Web UI :7860 ✓、WebSocket 聊天链路 ✓、Kokoro TTS 合成 ✓（spacy `en_core_web_sm` 已从 HF-mirror 取 wheel 装入 .venv）。
  - 但 LLM 后端不可用：原 `http://127.0.0.1:8080/v1`（Qwen3.8-27B GGUF）服务已停止，**8080 端口现被 Steam（steamwebhelper）占用**；Bonsai 项目的 :8090 服务也未运行。
  - 系统内存：free ≈ 593MB / 20GB，load 97%。当前启动任何 27B GGUF（最小 6.77GB）都会复现 OOM（HB-003）。
- 选项（请选一个，或补充你的做法）：
  - **A（推荐）**：你先释放内存（关掉 Steam / Chrome 标签页等），告诉我"可以了"；我用配置中的 `Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ2_XS-mtp.gguf`（8.17GB）在 **8090** 端口启动 llama.cpp（Vulkan 运行时 `F:\魔搭社区\Bonsai_2_27B\runtime\llama-prism-b10709-win-vulkan\llama-server.exe`，上下文建议 -c 16384 控制 KV），并把 `config.yaml` 的 base_url 改为 `http://127.0.0.1:8090/v1`，然后完成端到端验证。
  - **B**：改用更小的 `Qwen3.8-27B-UD-IQ2_XXS.gguf`（6.77GB）启动于 8090——内存压力略小（仍需先释放内存），质量比 IQ2_XS 略低。
  - **C**：用你 Bonsai 项目的 `Ternary-Bonsai-2-27B-PTQ1_0.gguf`（~5.95GB + mmproj）按现有脚本启动于 8090，Jarvis 指向它。
  - **D**：你自己启动服务器后告诉我端口与模型名，我只改配置并验证。
- 附带确认项（可顺带回答）：
  1. 本机有一个身份不明的系统 Python312 进程（~1.4GB，今天 20:13 启动）——是你有意运行的程序吗？
  2. Steam 占着 8080， Jarvis 配置里的 8080 必须改端口（候选 8090），确认可以改吗？
- 阻塞范围：在解决前不推进"LLM 端到端验证"与最终 git commit；其余收尾工作（记录、清理临时文件）继续。

### A（用户答复，2026-10-13-09-52）
- 用户选择：本地 llama.cpp 由用户自行启动（对应选项 D 的变体）——"本地的 llama 我暂时没启动，需要时你和我说"。
- 处置：agent 在需要 LLM 服务时向用户发出明确请求（模型/端口/参数），用户启动后 agent 更新 `config.yaml` base_url 并完成端到端验证。
- 附带确认项答复：未明确说明；系统 Python312（~1.4GB）与 Steam 均已随机器重启消失，8080/8090 现均空闲，不再跟踪。
- status: done（决策部分）；剩余"LLM 端到端验证"等待用户启动 llama 后继续，转入 todo.md。
