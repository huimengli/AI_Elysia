# 轮 2：阈值降到 0.65，复测触发与 UI（2026-11-08-19:38）

- 场景：`config.yaml` `wake_word.threshold` 0.75 → **0.65**（缺省不动 model/chunk_size），重启（**job pwsh-36**）；日志、UI、WS、`/api/settings` 一起看。
- 期望：真实语音能越过阈值触发 wake；后台各端点正常。
- 实际：真人语音**连续触发** —— 事件库 162/166/168/173 行 `wake Wake word triggered`（19:32:48、19:36:41、19:37:33、19:39:57），日志 `peak 0.716 / 0.689 / 0.734` 均 > 0.65；`GET /` 200 / 42,420 B（title 爱莉希雅、`--pink`）；`/api/settings` 回 `threshold: 0.65`；WS chat → `已输入文字："今天天气很好。"`（2B 把「回答」理解成 `type_text`，属工具行为）。
- 结果：**PASS**
- 备注：触发成功后出现新现象 —— 录音只有 **0.3 s** 就 `Recording aborted.`，随后 `Transcription empty — didn't catch anything`（169/167/165/160 行 `Wake: no voice recognized`）。
