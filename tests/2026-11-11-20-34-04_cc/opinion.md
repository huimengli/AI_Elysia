# 批次结论 — 2026-11-11-20-34-04（TTS 分段队列，本批第 1 项）

3 轮（零截图、无子智能体，走 python 探针 + 服务端口轮询）：

1. **按标点拆分 PASS**：`_split_sentences` 改用 `re.split(r"(?<=[。！？，；、!?;,\n])", text)`，2 字以下碎片并入前段。中文长句切 6 段（旧正则只切 1 段），短句保持 1 段。
2. **队列加速 PASS（A/B 实测）**：新增 `speak_queued()` + `_produce_segments()`（bounded `queue.Queue(maxsize=4)`，producer 线程在播放段 k 时合成段 k+1，消费端按序写复用输出流）。6 段应答：逐段合成 2453/2570/2556/3747/2815/2908 ms（串行合计 17049 ms，音频 11.48 s）→ **首声 2435 ms、总 19560 ms**；基线（整句一次合成后播放）整句合成 14083 ms、总 27038 ms。**首声 14.08 s → 2.44 s（≈5.8×），总时长 −27%**。`speak_streamed()` 的 gptsovits 分支已改为走队列，`main.py` 调用点不变。
3. **打断 PASS**：`stop_speaking()` 现在 flush 复用输出流（只 `sd.stop()` 会让队列缓冲播完）。播放 1.2 s 后打断：`played 0.00 s`、`is_speaking=False`、函数 2363 ms 返回，无残留播放。唤醒 barge-in 路径语义不变。

服务侧：本批开始时 `:9880`/`:8080`/`:7860` 全部 DOWN（机器重启），用 `cmd /c start_all.bat` 后台任务 10 s 内拉起全部 3 个端口；Jarvis 加载的是新代码（`:7860` health 显示 `aili_xiya_v0.6.onnx` + 0.7）。

**结论**：TTS 队列达标，保留。第 2 项（新录音训练 v0.7）、第 4 项（ASR 引擎可选）、第 6 项（根目录清理）后续在本 record 续写；第 3 项（Q12 = 保持 v0.6+0.7）与第 5 项（关闭 Q5/Q6）已落盘。Q13（清理目标目录 + 仍缺音频 + ASR 磁盘授权确认）`status: wait`。
