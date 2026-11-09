# 验证轮 2 — 双击后真实弹出的 cmd 窗口（零截图，只读窗口标题文本）

- 时间：2026-11-09 21:36
- 场景：以 `call start_all.bat > .tmp\bats\launch1.log` 方式执行改后的脚本（当时 `:8080` 已被用户自己起的 llama 占用，`:9880`、`:7860` 空闲）。
- 期望：`start` 为每个未运行的服务开一个独立窗口；已占用端口只打印 `[Skip]` 且**不**多开窗口（幂等，双击两次不会堆服务）。
- 实际窗口标题（`computer_windows list`，UIA 文本，无截图）：
  - `GPT-SoVITS :9880 - ..\.venv-gsv\Scripts\python.exe  -X utf8 api_v2.py`（cmd，pid 21056）
  - `AiliXiya :7860 - .venv\Scripts\python.exe  -u -m jarvis.main`（cmd，pid 18696）
  - `Jarvis Status`（powershell，pid 21348，每 5 s 刷新端口与 health）
  - llama 无新窗口（端口占用）
- `launch1.log` 关键行：
  ```
  === before launch ===
    TCP    127.0.0.1:8080  0.0.0.0:0  LISTENING  13808
  === call start_all.bat ===
  [Skip] :8080 already in use - llama.cpp is running.
   Windows opened: llama.cpp :8080 / GPT-SoVITS :9880 / AiliXiya :7860 / Jarvis Status
  ```
- 结果：**PASS**（窗口标题里带出各自启动命令，证明 `start "标题" cmd /k "..."` 单行形式可靠；`[Skip]` 幂等生效，llama 未重复启动）
- 备注：改前的 `start "标题" cmd /k ( 多行 )` 括号写法已废弃；`cmd /k` 窗口关闭即停止该服务（脚本尾部已提示）。另记一处观察：`launch1.log` 里 `call` 之后的 `=== after launch ===` 段未写入（`exit /b 0` 在 `call` 后未回到父脚本），不影响双击使用；改用 `run37.bat` 独立采集端口/health 后补齐了第 3 轮数据。
