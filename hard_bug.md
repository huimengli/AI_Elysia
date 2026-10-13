# Hard Bug 记录

<!-- 已归档于 ai_buckup/hard_bug.md_2026-10-13-17-45.md（HB-001~HB-008 全文，含 HB-007 未解决状态快照） -->

> 2026-10-13-17:4x：HB-001/002/004/005/006/008 已解决并归档；**HB-007（chroma embedding 下载目录 PermissionError）当日解决**——根因：chromadb 默认 ONNXMiniLM 模型硬编码下载到 `C:\Users\楼听\.cache\chroma`（沙箱不可写）；方案：模型预下载至工作区 `.chroma-models/` + `jarvis/memory.py` `WorkspaceMiniLM` 子类指路，实测 store/search OK。详见 records/2026-10-13-11-55.md 与 progress.md。

## HB-003 Jarvis 与 llama.cpp 27B 并存内存耗尽（部分解决）

- 时间：2026-10-12-16-50
- 状态：部分解决（策略缓解，根因是系统物理内存不足，需用户知悉）
- 影响：`python -m jarvis.main` 启动阶段 `import kokoro → misaki → spacy` 链中 `MemoryError`，进程退出；同时把 llama.cpp 的内存/显存撑爆（用户反馈并重启了 llama.cpp）。
- 现象：Web 服务已起（[Web] Event loop captured）后 TTS 问候崩溃；llama.cpp 重启前 `/v1/models` 503。
- 根因：llama.cpp 27B BF16（8.7GB 常驻内存/显存）+ Jarvis 侧 torch + Kokoro + faster-whisper + 各原生库并发，超出系统可用物理内存。
- 方案：
  1. 用户重启 llama.cpp 释放内存后启动 Jarvis（当前可用约 6.2 GB）。
  2. 用轻量 `_precache.py` 预下载 TTS/STT 大模型到 `.hf-cache`，避免主进程"边下载边加载"的峰值。
  3. 若仍 OOM：建议用户降低 llama.cpp 占用（减小 `-c` 上下文、减少 GPU 层 `-ngl`）或错峰运行。
- 关联需求：records/2026-10-12-12-28-30.md
