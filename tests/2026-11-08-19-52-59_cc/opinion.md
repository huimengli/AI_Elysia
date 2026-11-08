# 批次结论（tests/2026-11-08-19-52-59_cc，验证 3 轮）

- 「能唤醒但总答『我没听清』」的根因是**录音被自己的 barge-in 打断**：IDLE 冷却只有 2 s（挡不住她的 ack『在。』+ 用户紧接着说话），busy 分支的 `is_recording()` 在录音窗口前 0.15 s 仍是 False，于是 `abort_all()`；而 `record_until_silence` 每个 chunk 都查 abort flag → 第一 chunk（0.3 s）就 break。修法：`handle_wake` 入口置 `_stt_recording = True`（finally 清零）、冷却 5 s、abort 检查加 1.5 s 宽限；再加 `[ABORT] set by … thread=…` / `[Wake] barge-in score=… recording=…` 让这类问题可现场判定。
- 真人反馈「回答是天气」另修：新增 `get_time` 工具（`jarvis/tools/system.py` + `router.py` TOOL_MAP/schema + 系统提示规则），实测 `dispatch` 返回 `2026-11-08 20:09:20 星期日`，语音问时间得到 `现在是 2026年 11月 8 日 20 点 10 分，星期日。`。
- 真人测试注意：2B 会把「说一句话/记一下」理解成 `type_text` 往桌面打字；「爱莉希雅」常听成「爱利西亚」；whisper 偶发繁体输出；1.5 s 后的 barge-in 仍会截断长句子。当前 jarvis = **job pwsh-50**（阈值 0.65 + 分数日志 + 1.5s 宽限 + 5s 冷却 + STT zh + 转录守卫 + `_tool_report` + get_time）；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。
