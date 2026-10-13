# Need User（需用户确认的问题）

<!-- 已归档于 ai_buckup/need_user.md_2026-10-13-17-45.md -->

- Q2（chroma embedding 下载目录无权限，HB-007）：2026-10-13-17:4x 已解决。回答用户三连问：① chromadb 存储本来就是 SQLite（`jarvis/data/memory.db` + `jarvis/data/chroma/chroma.sqlite3`，均在工作区），无需改动；② 唯一阻塞是默认 embedding 模型硬编码下载到 `C:\Users\楼听\.cache\chroma`（沙箱不可写）——已改 `jarvis/memory.py` 子类把模型目录指到工作区 `.chroma-models/` 并预下载 83MB 模型（SHA256 校验通过），**用户无需任何操作**；③ 降级方案不再需要。实测 store/search OK。
- Q3（api_v2 推理前停 llama :8080，HB-003）：2026-10-13-17:4x 已解决。用户已停 llama-server，内存空出，可启动 api_v2。

- Q4（最终聊天 e2e 需要 LLM 在线）：2026-10-13-20:0x 提出，status: wait。
  - 背景：GPT-SoVITS 链路已全部验证通过——api_v2(:9880) 爱莉希雅权重推理 PASS（84s/541KB WAV/32kHz）、`config.yaml` 已切 `tts.provider: gptsovits`、Jarvis 已带 gptsovits 重启于 :7860。但完整聊天 e2e（WS 发问 → LLM 回答 → 爱莉希雅语音）需要 llama-server :8080 在线，而它是您为本次 TTS 测试停掉的。
  - 请确认：**请重启 llama-server（:8080）**，我将复跑 `_e2e_stream_test.py`（两个 WS 用例：自我介绍 + 时间工具）完成端到端验收。若担心 HB-003 内存压力，api_v2 常驻约 4–5 GB，两者并存时请留意任务管理器；若内存不足，可先停 api_v2 验证 LLM+WS 链路、再恢复。
  - **2026-10-13-20:4x 用户已重启 llama-server（:8080，IQ2_XS-mtp 量化，上下文 16348），status: done。** 随后完成 e2e 复验（期间定位并修复 HB-012 GBK print 崩溃、HB-013 双 system 消息 500）。

（当前无待用户确认问题。）
