# 轮 13 — `write_file` + `read_file` + `list_files`（含越界）
- **时间**：2026-11-13 13:26
- **场景**：写工作区 `.tmp/tooltest.txt`，读回、列表校验；再喂越界路径 `C:/Windows/win.ini`（零截图）
- **期望**：只写允许清单内的路径；读回一致；越界必须被拒
- **实际**：
  ```
  已写入：.tmp/tooltest.txt
  read_file: '工具测试\n第二行'
  list_files('.tmp') 含 tooltest.txt: True
  越界路径（期望被拒）: 工具「读取文件」执行失败：路径不在允许清单内：C:/Windows/win.ini
  ```
- **结果**：**PASS**
- **备注**：`_check_allowed` 用 `allowed_dir in target.parents`（`jarvis/tools/file_ops.py` 第 19 行）—— 对 `startswith` 前缀攻击免疫，这条判据成立。
