# 验证轮 1 — 文件字节属性：ASCII + CRLF

- 时间：2026-11-09 21:33（`TIME=21:19:10` 需求提出，21:33 完成重写）
- 场景：把 `start_all.bat` 用 PowerShell `Set-Content -Encoding Ascii`（行连接 `\r\n`）从 ASCII 源 `.tmp\start_all_src.txt` 重建，逐字节统计。
- 期望：`nonASCII=0`（纯 ASCII），`CR == LF`（每条换行都是 CRLF），`start` 语句数 = 4（三服务 + 状态窗口），其中 `cmd /k` 形式 = 3。
- 实际（`.tmp\bats\conv2.log`）：
  ```
  report: len=2912 CR=50 LF=50 nonASCII=0
  starts=4
  cmd_window_starts=3
  ```
- 对照改前（`.tmp\bats\time1.log`）：`len=2395 CR=56 LF=56 nonASCII=250` → 换行本来就是 CRLF（已满足第 1 条），但含 250 个非 ASCII 字节（`rem` 框线 `─` 与中文「爱莉希雅」），导致 `read` 直读报 `invalid UTF-8 text`。
- 结果：**PASS**（非 ASCII 归零，CR/LF 各 50 一一对应；`start` 4 条，3 条为 `cmd /k`）
- 备注：ASCII 编码会把源里的 `─` 变成 `?`，所以源文件里全部改用 ASCII `----`，注释与提示一律英文；`.bat` 内的路径全部用 `%~dp0`，不含中文与空格，因此 `cmd /k "..."` 内无需再嵌套引号。
