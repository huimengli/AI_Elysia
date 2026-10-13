# Need User（需用户确认的问题）

<!-- 已归档于 ai_buckup/need_user.md_2026-10-13-17-45.md -->

- Q2（chroma embedding 下载目录无权限，HB-007）：2026-10-13-17:4x 已解决。回答用户三连问：① chromadb 存储本来就是 SQLite（`jarvis/data/memory.db` + `jarvis/data/chroma/chroma.sqlite3`，均在工作区），无需改动；② 唯一阻塞是默认 embedding 模型硬编码下载到 `C:\Users\楼听\.cache\chroma`（沙箱不可写）——已改 `jarvis/memory.py` 子类把模型目录指到工作区 `.chroma-models/` 并预下载 83MB 模型（SHA256 校验通过），**用户无需任何操作**；③ 降级方案不再需要。实测 store/search OK。
- Q3（api_v2 推理前停 llama :8080，HB-003）：2026-10-13-17:4x 已解决。用户已停 llama-server，内存空出，可启动 api_v2。

（当前无待用户确认问题。）
