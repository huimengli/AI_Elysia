# Need User（需用户确认的问题）

## Q2 chroma embedding 下载目录无权限（HB-007）

- 时间：2026-10-13-12-35
- status: wait
- 背景：唤醒请求在 TTS 之后执行 `memory.extract_and_store_facts()`，chromadb 默认 ONNXMiniLM embedding function 首次运行需创建/下载模型到 `C:\Users\楼听\.cache\chroma`，被拒（WinError 5），整条请求报错。
- 请用户选择：
  - A. 你自行修复 `C:\Users\楼听\.cache` 目录权限（推荐：管理员身份在该目录执行 `mkdir chroma` 或重置 ACL），agent 验证后关 HB-007；
  - B. agent 改 `jarvis/memory.py` 使用显式本地 embedding_function，绕开默认下载路径（需要确定本地模型来源，可能再占 ~90MB 磁盘）;
  - C. 记忆入库失败降级为 warning（功能暂时弃用，主链路不受影响）。
- 说明：该问题不阻塞 TTS/LLM/唤醒主链路，只影响长期记忆写入。

## Q3 请在 GPT-SoVITS api_v2.py 启动推理前停掉 llama-server :8080（HB-003）

- 时间：2026-10-13-14-5x
- status: wait
- 背景：`.venv-gsv` 依赖正在安装（作业 pwsh-64，预计 30–90min）。装完 agent 将启动 `GPT-SoVITS-main/api_v2.py`（:9880，CPU 推理）并加载爱莉希雅权重做 `/tts` 冒烟测试。Qwen3.8-27B llama-server 常驻内存 ~18GB，与 GPT-SoVITS 推理叠加可能触发 HB-003（C: 盘+RAM 压力导致崩溃/极慢）。
- 请用户：在 agent 回复「可以启动 api_v2」之前（或看到本条后择机）手动停掉 llama-server :8080。测试完成后用户可随时重启 llama-server，Jarvis 的 LLM 配置无需改动。
- 说明：不阻塞依赖安装本身；只阻塞 api_v2 推理验证这一步。
