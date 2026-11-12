# 第 3 轮：`training/_t2_hot_export.py` 导出判据（2026-11-13 00:00）

- 时间：2026-11-13 00:00
- 场景：只读导出 `hot_phrases` → CSV，列固定 `kind,text,count,first_seen,last_seen`，按 `count` 降序；`DB=<路径>` 指定库（默认现役 `config.yaml memory.db_path`），`KIND=near_miss` 只导一类；输出到 `.tmp/hot_phrases_<时间戳>.csv`
- 期望：现役库全表 12 行、`kind` 分布正确；临时库 60 行（40 user + 20 near_miss）全导与只导 near_miss 都对；**现役库不被写入测试数据**
- 实际：

| 运行 | 库 | 结果 |
| --- | --- | --- |
| 全表（默认） | `jarvis/data/memory.db` | 12 行，`{'near_miss': 1, 'user': 11}`，近音前 10 = `['爱莉希雅']` |
| `KIND=near_miss` | `jarvis/data/memory.db` | 1 行，`{'near_miss': 1}` |
| 全表 | `.tmp/hot_probe_export_test.db`（造 60 条） | 60 行，`{'user': 40, 'near_miss': 20}`，近音按 count 降序 `near19, near18, …` |
| `KIND=near_miss` | 同上 | 20 行，`{'near_miss': 20}`，顺序同上 |

- CSV 头行：`kind,text,count,first_seen,last_seen`（第 2 行 `near_miss,near19,19,2026-11-12-00-00-00,2026-11-12-00-00-00`）
- 现役库行数复核：导出后仍是 **12 行**（未被测试数据污染）
- 结果：**通过** —— 列序、KIND 过滤、count 降序、只读性都正确
- 备注：零截图；测试数据全部在 `.tmp/`，CSV 是探针产物（被 `.gitignore` 忽略）。
