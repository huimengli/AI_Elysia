# 批次结论 tests/2026-11-13-12-25-43_cc（20 轮测试暴露的 3 个工具层缺陷，修 + 3 轮，全 PASS）

20 轮明确测试第 9、10 轮暴露三条：音量虚假成功、`read_screen` GBK 崩、`get_weather` ascii 崩。本批修完并 3 轮验收（全程零截图，浏览器打字 + `curl` + 日志 + 独立 python 复测）。

## 1. 三条根因（都不是模型的锅）

| # | 现象 | 根因 | 修法 |
| --- | --- | --- | --- |
| HB-033 | 「把音量调大」→ 回复「已调至最大 (100%)」，设备仍 20% | ① `set_volume` 不检查 returncode/输出，无条件返回成功；② `[MMDeviceEnumerator] -as [IMMDeviceEnumerator]` 在 PS 里**返回 null**（COM coclass 不会被 `-as` 激活），整条调用链打在 null 上；③ 服务作为 harness 后台任务启动时 python 子进程 `%TEMP%` 禁写，`Add-Type` 编译被拒 | C# 类里 `new MMDeviceEnumerator()` 做 COM 激活；`set_volume` **复读音量作证据**（读数与目标差 ≤2 才报成功，否则带 stdout/stderr 报失败）；`get_volume` 改读 `eMultimedia`（`role=0`）；`$env:TEMP` 指到工作区 `.tmp/pscompile` |
| HB-034 | 「屏幕读取失败」，日志 `UnicodeDecodeError 'gbk' … 0x9c` 崩在 `_readerthread` | `_ocr_image` 用 `subprocess.run(..., text=True)` → 按本机代码页 GBK 解码 OCR 输出，reader 线程崩 → `result.stdout` 变 `None` → `.strip()` 报 `'NoneType'` | PS 头部设 `[Console]::OutputEncoding = UTF8`；Python 侧 `text=False` + `decode("utf-8", errors="ignore")`（照抄同族已有的 `_ps_utf8` 写法） |
| HB-035 | 中文地名天气连 3 次 `'ascii' codec can't encode` | 中文地名**拼进 URL 未 quote**，`format=` 里也带中文 | `urllib.parse.quote(location, safe="")` + 改 `format=j1`（纯 ASCII JSON，中文在 Python 侧拼） |

## 2. 3 轮结果

| 轮 | 判据 | 结果 |
| --- | --- | --- |
| 1（音量） | 复读证据 + 如实报失败 + 端点正确 | **PASS**：直调 `20%→60%（已复读确认）→60%→20%（已复读确认）→20%`；服务级日志 26/36 行两次「已复读确认」，独立复测 60% 与 20% 一致 |
| 2（天气） | URL 全 ASCII、查询成功 | **PASS**：日志 47 行 `Beijing：Smoky haze，气温 11°C，湿度 50%，风速 4 km/h`，独立直调同结果 |
| 3（屏幕） | 不再 `'NoneType'`、返回真实文本 | **PASS（能力恢复）**：日志 59 行返回 OCR 文本；诚实记录 **WinRT OCR 中文质量差**（字间插空格、有错字）→ `find_on_screen` 的按空格分词子串匹配在中文上不可靠 |

## 3. 结论与规矩

1. **虚假成功比编造更危险**：模型永远拿不到失败信号，「工具失败要直说」被工具本身架空。规矩：**工具必须自带证据**（复读/复测），证据不符就返回失败文本 —— 这一条同样适用于 `show_notification`（`title=None` 时炸，`records/2026-11-08-20-44-17.md` 轮 6）与 `open_app` 之类「跑了就算成功」的工具。
2. **PowerShell 里 COM coclass 不能被 `-as` 激活**：必须写 C# 类并用 `new`（COM activation）。这条是音量类工具的通用坑。
3. **沙箱边界要写进代码**：`Add-Type -TypeDefinition` 要写 Temp，服务在 harness 后台任务里跑时 Temp 禁写。规矩：**凡要 `Add-Type -TypeDefinition` 的工具，把 `$env:TEMP` 指到工作区**（`Add-Type -AssemblyName` 不需要，OCR 路径不受影响）。
4. **解码一律 UTF-8**：`subprocess` 对 PowerShell 输出不要用 `text=True`（本机代码页 GBK 会崩在 reader 线程，症状是 `'NoneType' ... strip'`）。
5. **WinRT OCR 中文质量是硬限制**：`find_on_screen` 的中文匹配不可靠，后续要改（按行文本包含匹配，不靠空格分词），属下一批。

## 4. 现役状态

`:7860` 已重启加载修复，4 灯 online，唤醒 **`aili_xiya_v0.9.onnx` / threshold 0.75**（未动，Q16/Q17 裁决）；音量已还原 **20%**。本地 commit，未 push。
