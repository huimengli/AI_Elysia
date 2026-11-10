# 批次结论 · 2026-11-10-17-43-08（工具结果文案汉化 + 录音落盘 + ASR 参数优化）

**3/3 PASS**（零截图；探针 + 日志 + WS 事件 + health JSON）

| 轮 | 期望 | 证据 | 结果 |
| --- | --- | --- | --- |
| ① 工具结果文案全中文 | `Typed:`→`已输入文本：`、`Pressed:`→`已按下：`、`Clicked`→`已用左键点击 (x, y)` 等；协议字段仍英文 | `lab2.log` 12 条逐条中文；发现并当场修掉 `get_system_info` 乱码（`lab3.log` 复测正常） | PASS |
| ② 录音落盘 + ASR A/B | 每次录音落 `.tmp\capture_*.wav`，可离线复现；新参数不劣于旧参数 | 合成语音 A/B **3/3**（旧参数繁体 `你能看得見屏幕嗎`/`調到20` → 新参数逐字正确带标点）；真人 1 句 6 种参数组合均为 `你看得见吗?`（丢「能」「屏幕」） | 部分 PASS |
| ③ WS 端到端无回归 | 中文 label + 中文结果 + 英文 `name` + 四灯在线 | `ws3.log`（`看时间` 中文 label、结果中文、`name=get_time`）、`h9.log`（`asr warm=true, device cpu`，四灯全在线） | PASS |

**汉化补全的边界（写清）**：本轮覆盖的是**用户听到的文案**——`tools/*.py` 的返回值（`desktop.py` 14 处、`system.py` 13 处、`app_control.py` 6 处、`web_search.py` 4 处、`file_ops.py` 2 处、`code_exec.py` 3 处、`subagent.py` 2 处、`router.py` 2 处）。协议层刻意保持英文：`TOOL_SCHEMAS` 的工具名/参数名、WS 事件的 `name`、`events.db` 的 `tool` 行、`TOOL_LABELS` 的 key。这样 UI/播报是中文，而 LLM 的函数调用与检索键不受影响。顺带修一个静默缺陷：`main.py` 的重试判定原为 `result.startswith("Tool '")`，文案改中文后会失效，已改为判定 `执行失败：`。

**ASR 结论**：参数级优化（beam 10 + 简体中文 `initial_prompt` + `vad_filter` + 去头部静音）**能解决繁体与标点**，合成语音 3/3 全对；但真人短句「你能看得见屏幕吗？」在 6 种参数组合下都只得到 `你看得见吗?`，且 2x 增益无效，说明瓶颈是 `whisper small` 对中文短句的鲁棒性（不是电平、不是参数）。要显著改善只能换引擎（sherpa-onnx paraformer-zh：中文专强、带标点、CPU 更快；需 pip 安装 + 200–400 MB 模型，从 hf-mirror 下载），**已写入 `need_user.md` Q7 等用户授权**，未擅自安装。

**新增发现（登记，未改）**：① 18:03 的 `peak 0.736/0.799` 在 0.7 阈值下误触发，随后录满 30 s、转写为空——`record_until_silence` 缺「无人说话就快速退出」；② 真人录音 rms 仅 0.010，建议同时调高麦克风增益；③ 上一批的「星期五」问题本轮未复现。

**运维新增**：重启 Jarvis 必带 `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET`（`records/2026-11-10-17-31-10.md`）；`config.yaml` 的 `stt.device` 已按实测改为 `cpu`（本机 CUDA 驱动不足）。
