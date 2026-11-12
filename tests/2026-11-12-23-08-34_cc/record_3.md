# 第 3 轮：hot_phrases 小表 + whisper initial_prompt 偏置 A/B（2026-11-12 23:30-23:42）

- 时间：2026-11-12 23:41
- 场景：`jarvis/memory.py` 在既有 `memory.db` 加 `hot_phrases(text, kind, count, first_seen, last_seen)`，`record_phrase()`（count 累加、`ON CONFLICT` 更新、上限 `_HOT_CAP=200` 淘汰低 count）、`top_hot_phrases()`、`hot_phrase_rows()`；`jarvis/main.py` 在真实转录成功后 `_record_hot_phrase()` 记 `user`，句内 2-5 字子串与「爱莉希雅」的 difflib 相似度落在 0.5-0.9 时记 `near_miss`；`jarvis/stt.py` 新增 `set_hot_words()/get_hot_words()/_bias_prompt()`，`config.yaml` 加 `stt.hot_bias`（默认 **false**）。探针 `training/_t2_hot_bias_ab.py`（已知 6 件复用 `training/_t2_asr_ab_gate.py` 的路径与解码），跑两次：`HOT_BIAS=1`（开）与 `HOT_BIAS=0`（关，即默认）
- 期望：表行为正确（写入/累加/上限）；偏置后 `sim ≥0.8` 计数不低于无偏置，且逐件不变差
- 表行为（两次独立临时库）：
  - 12 条写入后 `行数 12`，`爱莉希雅` 行 = `('爱莉希雅','near_miss',2,...)`（count 累加、kind 以最后写入为准）；
  - 造 210 条后 **行数 200**（= `_HOT_CAP`），top5 保留的是高 count 真热词（`HOT_BIAS=1` 那次 top5 = 爱莉希雅 / 爱莉希雅，帮我打开浏览器 / 爱莉希雅，帮我打开电视机 / 你好啊爱莉希雅，你在干什么呢 / 米希雅）。
- **A/B 结果（HOT_BIAS=1，真热词 8 条注入 initial_prompt）**：

| 真值 | A 无偏置 | B 有偏置 | 变化 |
| --- | --- | --- | --- |
| 爱莉希雅，帮我打开电视机 | 爱莉希雅帮我打开电视机。（0.92） | 爱莉希雅，帮我打开电视机。（**0.96**） | ↑ |
| 爱莉希雅，帮我打开浏览器 | 爱莉希雅帮我打开浏览器。（0.92） | 爱莉希雅，帮我打开浏览器。（**0.96**） | ↑ |
| 你好啊爱莉希雅，你在干什么呢 | 你好啊,爱莉希,你在干什么呢?（0.83） | 你好啊爱莉希,你在干什么呢。（0.86） | ↑（但这次 **61840 ms**，转录失控） |
| 爱丽安娜 | 爱莉安娜（0.75） | 爱莉安娜，（0.67） | ↓ |
| 爱丽丝 | 爱莉斯（0.33） | 爱莉希。（**0.29**） | ↓（吸附到热词） |
| 米希雅 | 爱莉希雅（0.57） | 爱莉希雅，（0.50） | ↓ |
| **sim ≥0.8** | **3/6** | **3/6** | 计数不变，**变差 3 件** |
| 总耗时（6 件） | 23125 ms | **81531 ms** | 3.5 倍（61.8 s 失控件） |

- **A/B 结果（HOT_BIAS=0，默认）**：B 与 A **逐件完全一致**（3/6，变差 0，总耗时 21852 → 18700 ms）。
- 结果：**表留下（数据源：统计 + 训练/验收导出），偏置默认关** —— `initial_prompt` 热词偏置对**短句有害**（whisper 会把短音频吸附到 prompt 里的热词：爱丽安娜 / 爱丽丝 / 米希雅 三件变差），并出现过一次转录失控与 3.5 倍耗时；`stt.hot_bias: false` 已写进 `config.yaml`，要开需显式改 true。
- 副作用与修正（都写进探针）：
  - 探针第一轮用现役 `memory.db` 造 210 条 filler，**挤掉了真实热词**（清理后剩 12 行，filler 188 行已删，脚本 `.tmp/clean_hot.py`）→ 之后改用**每次独立的临时 sqlite 库**；
  - `chromadb.PersistentClient` 在 `.tmp` 下起不来（`InternalError (code: 14) unable to open database file`）→ 探针用 `Memory.__new__` + 自建 `create_engine`（`record_phrase`/`top_hot_phrases`/`hot_phrase_rows` 只用 `_engine` 与 `_HOT_CAP`）；
  - `record_phrase` 的形参不能叫 `text`（遮蔽 sqlalchemy 的 `text()`，实测 `TypeError: 'str' object is not callable`）→ 改 `phrase`。
- 备注：零截图；打分前停掉 `:7860/:8080`（虚拟内存 7.5 GB → 11.2 GB）。
