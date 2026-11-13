# 批次结论 tests/2026-11-13-12-59-10_cc（全部 32 个工具的 20 轮 + 1 附加项）

**覆盖**：32 个工具全部过过一遍（`delegate_task` 按新规矩摘除，记为附加项轮 21）。逐轮 PASS：**1、2、4、5、6、7（判据修正后）、8（修后）、9（修后）、10、11、12、13、14、15、16（修后，工具级+服务级）、17（部分）、18、19（拒绝分支 + 修后）、20 的 media 部分、21**；FAIL：**轮 3（外网不可达，环境限制）**、`screenshot` 修前（桌面禁写）。

## 1. 最重要的一条：「跑了就算成功」的工具批量存在

这一轮把同一族的**五条虚假成功**全抓出来了（都是「执行动作后不校验，直接返回成功文案」）：

| 工具 | 修前 | 修后 |
| --- | --- | --- |
| `set_volume` | 无条件「音量已设为 X%」（HB-033，12:13 回复 100% 而设备 20%） | **复读音量作证据**，差 ≤2 才报成功，否则带 stdout/stderr 报失败 |
| `type_text` | 中文静默跳过却报「已输入文本」（HB-036） | 不可映射字符走**剪贴板粘贴 + 先存后还**，文案明写「键盘打不出 N 个字符」 |
| `press_key` | `not_a_key` 也报「已按下」（HB-038） | 逐段校验 `KEYBOARD_KEYS`，不可识别报失败并列出可用键 |
| `show_notification` | 整条 UWP toast **永远弹不出**（`0x80073D54` 无包标识），却报「已弹出通知」（HB-037） | 改 **NotifyIcon 气泡**（不需要包标识）+ `balloon shown` 作证据 + stderr 进文案 |
| `set_brightness` | 无条件「这台台式机不支持」（文案对，无原因无证据） | 带 UTF-8 解码的 stderr 真原因 |

**规矩（沿用并加强）**：**工具必须自带证据**（复读/复测/产物字节/枚举校验），证据不符就返回失败文本。虚假成功让模型永远拿不到失败信号，把「工具失败要直说」架空 —— 比模型编造更危险。

## 2. 本机环境边界（三条，必须写进代码，不能靠文档）

1. **`%TEMP%` 禁写**：`Add-Type -TypeDefinition` 要写 Temp（`focus_window`、音量）→ 把 `$env:TEMP` 指到工作区 `.tmp/pscompile`（`_vol_ps` 与 `focus_window` 已做）。`run_python` 的临时脚本同理改到 `.tmp/pyrun`。
2. **桌面目录禁写**：`screenshot` 写 `~/Desktop` 被拒（HB-039）→ 写工作区 `.tmp/screens`。
3. **外网不可达**：`web_search`/`fetch_page` 对 yahoo/DuckDuckGo/Wikipedia/example.com 全超时，**只有 `wttr.in` 通**（天气可用）。我这条 Agent 会话的 python 子进程同样无外网（`curl rc=000` + `failed to load native root certificate … 拒绝访问`）。判据诚实：**「工具如实报失败」不等于 PASS**，轮 3 记 FAIL。

## 3. 中文与本地化的坑（三条）

- **窗口标题是中文本地化的**（`无标题 - 记事本`），`focus_window('Notepad')` 匹配不到 → 匹配中文标题要用中文。
- **`pyautogui.write` 打不出中文**（键盘不可映射字符静默跳过）→ 必须走剪贴板粘贴，且**先保存后还原**用户剪贴板。
- **OCR 中文插空格 + 有错字**（轮 3 前一批实测 `实 酎 对 话 与 状 态`）→ `find_on_screen` 的按空格分词 overlap 匹配在中文上不可靠，`read_screen` **不能当写入证据**。

## 4. 一处更正（我先前说错了）

20 轮轮 6 的 `'NoneType' object has no attribute 'strip'` **不是「dispatch 没强制参数类型」** —— `_coerce`（`jarvis/tools/router.py` 第 320 行）**早已落地**，把 schema 里 string 的 `None` 强制成 `""`。真实根因是 `text=True` 时 reader 线程被 GBK 解码崩掉，`result.stderr`/`result.stdout` 变 `None`（HB-034 家族），`show_notification` 死在 `result.stderr.strip()`。我先前在 `todo.md` 里写「计划① 未落地」是错的，已追加更正（`records` 与 `progress` 是 append-only，用追加更正节，不覆盖）。

**新暴露的小缺陷（HB-040 候选）**：`_coerce` 对缺省的可选参数无脑给 `""`，把工具自己的默认值架空 —— `set_timer(3)` 的默认中文「定时到了！」被覆盖成空串，文案尾巴空（轮 17）。修法：`_coerce` 应优先用 schema 的 `default`/工具默认值。

## 5. 副作用披露（对用户的真实影响，不隐瞒）

- **剪贴板里的 JWT 被覆盖，无法恢复**（13:21 读到 193 字符的 `sub=lt, role=admin` JWT；轮 9 做 `ctrl+a`/`ctrl+c` 证据时把它覆盖成记事本内容）。我没有把它写进任何文件、没有 commit；已记 `need_user.md`。
- `next` 让播放器跳到下一首（已授权）；`mute` 连打两次回到原状态；记事本已 `kill_process` 清场、未保存内容丢弃。
- **真锁屏没做**（我把它拆到批次收尾，等你说「锁」）；`power_command` 只测了拒绝分支，**没有触发任何关机/重启**。
- 音量、剪贴板已还原（音量 20%、剪贴板还原一致 `True`）；亮度未改动（台式机 WMI Access denied）。

## 6. 现役状态

`:7860` 已重启加载本轮全部修复，4 灯 online，唤醒 **`aili_xiya_v0.9.onnx` / threshold 0.75`（未动，Q16/Q17 裁决）；`delegate_task` 已从模型可见工具面摘除（32 个工具）。已本地 commit，未 push。
