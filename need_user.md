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
