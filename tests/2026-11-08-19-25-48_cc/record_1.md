# 轮 1：后台重启 + 唤醒分数可见化（2026-11-08-19:30）

- 场景：用户「后台重启一下,现在语音无法触发」；`job pwsh-30`（pid 13152，19:04 起）进程存活、`job_output` 无新日志（监听在跑，无 wake 记录）。`jarvis/wake.py` 99-101 行 `score = predictions.get(_model_key, 0)` → `if score < cfg["threshold"]: continue`，**全文件没有任何分数打印**。
- 期望：重启后台；让「叫爱莉希雅不触发」变得可判定（是听不到，还是分数不够）。
- 实际：`Stop-Process` 掉 7860 的 python 后重启（**job pwsh-34**）；`wake.py` 加 3 s 节流日志 `[Wake] peak X / threshold Y`（`py_compile` 0）。约 1.5 分钟真人环境实测 peak 序列：0.219 / 0.246 / 0.323 / 0.359 / 0.405 / 0.430 / 0.451 / 0.465 / 0.472 / 0.487 / 0.488 / 0.570 —— **最高 0.570 < 阈值 0.75，必然无法触发**。离线对照（GPT-SoVITS 合成「爱莉希雅，爱莉希雅」2.98 s，rms 0.083，重采样 16k 后 37 chunk 喂 openwakeword）：**PEAK 0.862**，top5 0.862/0.849/0.843/0.838/0.833。
- 结果：**PASS（根因确证：阈值 0.75 是 17:53 在设置页保存的，验收可用值是 0.7 —— v0.3c 在 0.7 下 recall 0.94 / fp 0.09）**
- 备注：重采样坑 —— `np.interp` 的 step 要用源索引 `sr/16000`，首版写成 16000 导致只有 3 点、chunk 数 -1；改用 `np.linspace(0, len(a)-1, int(len(a)*16000/sr))`。
