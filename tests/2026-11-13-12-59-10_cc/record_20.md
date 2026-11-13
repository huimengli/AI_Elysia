# 轮 20 — `media_control` + `lock_screen`（锁屏**未执行**，留作收尾）
- **时间**：2026-11-13 13:29（`media_control`）；`lock_screen` 待做
- **场景**：`media_control` 五连：`pause`、`mute`、`mute`（**两次连打回到原状态**）、`next`、非法 `xx`（零截图）
- **期望**：媒体键真发出；非法操作如实拒绝；音量静音状态在两次 mute 后回到原状
- **实际**：
  ```
  媒体操作已执行：pause
  媒体操作已执行：mute
  媒体操作已执行：mute
  媒体操作已执行：next
  未知媒体操作：xx，请用 play/pause/next/previous/mute。
  ```
- **结果**：`media_control` **PASS**（非法项如实拒绝；mute 连打两次回到原状态）；`lock_screen` **待做**
- **备注（我改了顺序，必须写清）**：我把真锁屏从本轮**拆出来放到批次最后单独做**，因为锁屏会打断当前会话与正在跑的服务/采样器，跑完其它项更稳。副作用披露：`next` 会让你的播放器**跳到下一首**（已授权）。`lock_screen` 用 `rundll32 user32.dll,LockWorkStation`，无证据校验 —— 文案「已锁定屏幕」在锁屏成功时才可信，判据只能由你肉眼确认。
