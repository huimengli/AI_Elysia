# 批次结论（tests/2026-11-09-21-19-29_cc，验证 3 轮）

需求：① `start_all.bat` 必须是 CRLF + ASCII；② 用 `start` 打开三个（或更多）cmd 界面。

- 轮 1（字节属性）：改前 `CR=56 LF=56`（换行已是 CRLF）但 `nonASCII=250`（框线字符 + 中文），不满足 ASCII；改后 `len=2912 CR=50 LF=50 nonASCII=0`，`starts=4`、`cmd_window_starts=3`。→ PASS
- 轮 2（窗口弹出 + 幂等）：`start "标题" cmd /k "单行命令"` 开出 `GPT-SoVITS :9880`、`AiliXiya :7860` 两个 cmd 窗口（标题带出启动命令），第 4 个 `Jarvis Status` powershell 窗口；`:8080` 已占用时只打印 `[Skip]` 且未多开窗口。→ PASS
- 轮 3（服务真起来）：`:7860` 由脚本窗口子进程 pid 4920 监听、`:9880` 由 pid 7028 监听、`:8080` pid 13808 存活；`/api/health` 四灯全 `online:true`（`asr.warm=true`，`wake.last_detect=21:37:48`）。→ PASS

**3/3 PASS。** 关键点：
1. 编码——`.bat` 想被 cmd 与 `read` 都读通，必须纯 ASCII；所有注释/提示改英文，路径全用 `%~dp0`（路径含中文时 cmd 按 GBK 处理，文件本体保持 ASCII 即可）。用 `Set-Content -Encoding Ascii` + 显式 `\r\n` 连接生成。
2. `start` 的写法——`start "标题" cmd /k ( 多行 )` 括号复合不可靠；改成 `start "标题" cmd /k "cd /d ... & set ... & 程序"` 单行形式，标题即窗口名，路径无空格故不需嵌套引号。
3. 幂等——每段先 `netstat` 查端口，占用则 `[Skip]` 跳过启动，双击多次不会堆出重复服务或窗口。
4. 4 个窗口：llama :8080 / GPT-SoVITS :9880 / Jarvis :7860 / Jarvis Status（5 s 刷新端口与 health）。关窗即停该服务。

遗留：`call start_all.bat` 后父脚本尾部输出未落盘（`exit /b 0` 交互），不影响使用；改 `config.yaml` 的 `wake_word.threshold` 仍需重启 Jarvis 才刷新灯上的数值。
