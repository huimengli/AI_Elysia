<!-- 已归档于 ai_buckup/hard_bug.md_2026-11-17-13-26-51.md（全量备份，含 HB-047 立案结案、11-06 更正、HB-040 结案）；本文件只保留结案摘要 -->

# hard_bug（compact，已解决）

- **影响**：模型省略可选参数时，播报/行为用**空串**而不是函数的中文默认值（`set_timer` 定时提醒不播报文案）
- **现象**：`dispatch('set_timer', {'seconds':3600})` → 「已设置 1小时 0分 后的提醒：**（空）**」
- **尝试**：只读 `_coerce` 与 schema，确认 schema 里 `message` **没有** `default` 字段，函数默认值是唯一来源
- **根因**：`jarvis/tools/router.py::_coerce` 遍历**所有** schema 属性写值，`out.get(key)` 缺席时得 `None`
  → 被写成 `""`，且**键存在于 dict** → `set_timer(seconds, message="定时到了！")` 收到 `""`，默认值被架空
- **方案**：`if key not in out: continue`（模型没传就不注入，函数默认值生效）；显式 `null` 仍 coerce（防 `NoneType` 崩）。
  **不改 schema 文案、不增删工具**（工具面 token 不变）
- **验证**：**3 轮全 PASS**（`tests/2026-11-17-13-25-00_coerce/record_1..3.md` + `opinion.md`），附加 `click_at` 缺省 `button` 生效
- **关联**：`records/2026-11-17-13-25-00.md`、`records/2026-11-13-*`（立案）、`events.db` 242/245（当年崩溃源）
- **归档**：本条结案后 `hard_bug.md`（HB-047 立案结案 + 11-06 更正 + 本条）全量备份到
  `ai_buckup/hard_bug.md_2026-11-17-{ts_tail}.md`，原文件 compact + 顶部归档注记（§3）


## HB-048 — 2026-11-17 22:05 · 状态：**未修（open）** · 语音整句被「吃尾」，LLM 用对话历史关键词播了之前指定的歌

- **影响**：语音播歌不可信 —— 唤醒正常、播放链路正常，但**歌名丢失**，播的是**上一轮的歌曲**；且听感上「无法语音唤醒」（其实是它自己被打断停了）。20 轮语音验收的轮 11 因此 FAIL。
- **现象**（`.tmp\jarvis6.log` + `.tmp\bats\voice_r11.log` 原样）：
  ```
  [爱莉希雅] Wake word detected! ×4（peak 0.768 / 0.778 / 0.783 / 0.798，阈值 0.75）
  [TTS] ack played (2.26 s)
  [STT] Speech detected (rms=0.0192) → [STT] Recording aborted. → capture saved (1 s)
  [爱莉希雅] Recorded 1.5s of audio, transcribing...
  [You] 播放到
  [Tool: play_music] 关键词「心灯明」→ 最多播放第一支 BV1RMYF6kEze（1770213 播放）
  [ABORT] set by listen_for_wake_word:212 → [爱莉希雅] Stopped. (voice interrupt)
  ```
  你说的是整句「爱莉希雅，播放《稻香》」。驱动前 90 s WS **零消息**（说话落在采样窗外），日志里另有 3 次唤醒 + **3 次转录全空**（`Transcription empty — didn't catch anything`）。
- **尝试**：读 jarvis stdout（新码 `.tmp\jarvis6.log`，工具全文行不截断，main.py:413）+ WS 全事件 + CDP 5 判据；确认唤醒模型正常（峰持续 0.76-0.79）、导航/关弹幕/最低分辨率三项 PASS。
- **根因**（已定位，5 条）
  1. **转录吃尾**：唤醒后先播 ack `2.26 s`，`[STT] Recording aborted` 把录音截到 1.5 s → 录进的是指令被截后剩下的半句 `[You] 播放到`，歌名丢失；
  2. **LLM 用历史关键词**：`播放到` 没有歌名 → 模型从对话历史取上一轮的「心灯明」→ 播了你之前指定的歌（`order=play` 本身没错，错在关键词不是你要的）；
  3. **「无法语音唤醒」是现象不是模型失效**：`[ABORT]` + `Stopped. (voice interrupt)` 自停；峰照常触发；
  4. **CDP 9333 随 Chrome 实例漂移**：实例 pid 11820 → 12808，端口随旧实例消失 → 播中 51 s 断读，「到达结尾」无法判；
  5. **关窗仍用「pid 对标题」**：`play_music` 结尾报「找不到我自己起的 B 站窗口…没有关闭任何窗口」，与第 2 项刚修的窗口计数**同族**（pid 会随实例漂移，profile 才是身份）→ 旧窗口残留，直接撞上 22:05 的**音乐唯一性**新规则。
- **方案**（待实施，明天）
  1. `play_music` 起手先数我起的窗口（profile 认 pid），已有播歌窗口 → **复用导航**或先关旧的，**绝不并存 2 个**（22:05 唯一性规则）；
  2. 结尾关窗改**同一口径**（profile 认 pid），关后「我起的窗口数」必须 0；
  3. 转录侧：让录音拿到**整句**（ack 期间不采 / 录完再播 ack，或提高 VAD 中止门限），并在歌名缺失时**如实问用户**而不是用历史关键词；
  4. CDP 侧：断读后重连新实例，不许把「断读」当「到达结尾」。
- **关联**：`tests/2026-11-08-20-44-17_cc/record_11.md`、`records/2026-11-17-22-05-05.md`（唯一性新规则）、`records/2026-11-17-20-16-55.md`（第 4 项 20 轮）、`0221012`（第 2、3 项）。
