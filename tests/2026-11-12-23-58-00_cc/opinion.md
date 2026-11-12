# 批次结论 tests/2026-11-12-23-58-00_cc（小收尾：favicon + near_miss 导出）

## 实现

- **favicon**：`.tmp/gen_favicon.py`（PIL）用主题色画 64×64 粉圆盘 + 金色四角星 + 玫瑰中心，存 16/32/48/64 四档 ICO（788 B）到 `jarvis/static/favicon.ico`（与 `index.html` 同一静态约定，不新建目录）；`jarvis/web.py` 新增 `@app.get("/favicon.ico")` → `FileResponse`（缺文件返回 204，不抛 500）；`index.html` 加 `<link rel="icon">`。
- **near_miss 导出**：`training/_t2_hot_export.py`（入 Git）**只读**导出 `hot_phrases` 全表 → `.tmp/hot_phrases_<时间戳>.csv`，列 `kind,text,count,first_seen,last_seen` 按 `count` 降序；`DB=` 指定库、`KIND=near_miss` 只导一类。

## 3 轮结果

| 轮 | 判据 | 结果 |
| --- | --- | --- |
| 1 favicon | `curl` 取 `/favicon.ico` = 200 且字节一致 | ✓ `code=200 bytes=788`，`Get-FileHash` 一致 True |
| 2 console | 浏览器 error 数 = 0（上一批实测 1 条 404） | ✓ `Total messages: 2 (Errors: 0)` |
| 3 导出 | 现役库 12 行 / 临时库 60 行（40 user + 20 near_miss）、KIND 过滤、count 降序、现役库不被污染 | ✓ 全表 12 行 `{'near_miss':1,'user':11}`、只 near_miss 1 行；临时库 60 行 / 20 行，顺序 `near19…near10`；导出后现役库仍 12 行 |

## 结论

1. **控制台干净了**：`:7860` 页面唯一的 console 错误就是 favicon 404，现在 error 数 0，浏览器桥接的日志可以当作「看屏幕」判据的一部分（零截图，读 console + 可访问性快照）。
2. **`near_miss` 通路打通**：转录真实成功后写入近音误识行（与「爱莉希雅」difflib 相似度 0.5-0.9），`training/_t2_hot_export.py` 就能把它们按 count 导出成 CSV，作为后续重训/验收的负样本来源（`records/2026-11-11-21-36-30.md` 第 3 项、Q13 的真人近音来源同一）。现役库目前只有 1 条 near_miss，等真实使用累积。
3. 探针纪律沿用上一批：**测试数据一律进 `.tmp/` 临时库**，现役 `memory.db` 只读；脚本本身不写库。
