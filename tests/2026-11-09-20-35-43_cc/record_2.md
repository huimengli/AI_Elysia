# 验证轮 2 — 2026-11-09-20-35-43 唤醒灯（前端灯序与绑定）

- 时间：2026-11-09 21:04
- 场景：`curl http://127.0.0.1:7860/` 取**服务真实返回**的页面 HTML（`.tmp\bats\page1.html`），`Select-String` 抽灯位与 JS 绑定，转 UTF-8 到 `.tmp\bats\pagechk.log`（零截图，用文本通路核对渲染要素，不靠肉眼看页面）
- 期望：第 4 盏灯「唤醒」位于「语音识别」**左侧**；`lamps` 绑定 `lamp-wake`；轮询 keys 为 `['wake','asr','llm','tts']`；离线灰灯 / 让出麦克风黄灯
- 实际（行号取自服务端返回的 HTML）：
  - `294: <div class="svc-lamp off" id="lamp-wake" title="唤醒：openWakeWord 模型是否已加载并在监听"><span class="dot"></span>唤醒</div>`
  - `295: <div class="svc-lamp off" id="lamp-asr" ...><span class="dot"></span>语音识别</div>`
  - `744: const lamps = { wake: document.getElementById('lamp-wake'), asr: ..., llm: ..., tts: ... };`
  - `755: for (const k of ['wake', 'asr', 'llm', 'tts']) {`
  - `759: else if (k === 'wake' && s.listening === false) setLamp(lamps[k], 'warm', (s.detail || '') + '（麦克风让给语音识别）');`
  - `763: for (const k of ['wake', 'asr', 'llm', 'tts']) setLamp(lamps[k], 'off', '无法连接 Jarvis 服务（:7860）');`
  - `766–767: pollHealth(); setInterval(pollHealth, 5000);`
- 结果：**通过**
- 备注：
  - `lamp-wake` 行号紧邻且**在 `lamp-asr` 之前** → flex 布局下顺序为 唤醒 / 语音识别 / LLM / TTS，满足「语音识别左边再加一个『唤醒』」；
  - 复用既有 `.svc-lamp` 样式（`on` 粉 / `warm` 金 / `off` 灰），未新增 CSS，灯大小、间距与原有三盏一致；
  - 唤醒灯在 STT 录音期间 `listening=false` → 黄灯并附「麦克风让给语音识别」，避免被读成「唤醒挂了」；`online=false` 才灰灯；
  - 页面标题里的 `Wake.` 状态机（聆听中）与 `case 'wake'`（实时对话 [WAKE] 事件）未被改动，无回归。
