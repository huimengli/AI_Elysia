# 轮 24-28：中文读取改走 CDP（P1 的可行路线）+ 页面点击闸门

- **时间**：2026-11-18 12:25-12:40（jarvis19 / jarvis20），WS 文本，无语音、无视觉、无坐标。

## 前置事实（12:25 实测，自曝）
- 本机**没有可用中文 OCR**：`read_screen`/`find_on_screen` 走 `Windows.Media.Ocr`
  （`TryCreateFromUserProfileLanguages`），这台机器 WinRT OCR 不可用（wow-sight selftest 早测过）；
  Umi-OCR 只有 `C:\Users\楼听\Downloads\Umi-OCR_Paddle_v2.1.5.7z.exe`（自解压安装包，**未安装**），
  `:50015` **无监听**（`urllib` 实测 `WinError 10061 目标计算机积极拒绝`）。
  轮 20 的「屏幕上找不到『打开浏览器』」就是这条，不是模型笨。
- 因此 P1「`find_on_screen` 中文 OCR」卡在**引擎**上，已提 **Q37**（装并常驻 Umi-OCR / 记「不做」），
  status: wait。我这边先走**不依赖 OCR 的 CDP DOM 读取**，只碰我自己起的窗口。

## 新工具（12:27 编译通过，jarvis19 载入）
- `read_page`：CDP 读我起窗口的 `innerText`（前 1200 字）+ 标题 + 地址复读；连不上如实报。
- `find_on_page`：DOM 文本匹配（`a,button,[role=button],h1-h4,li`），返回命中条目 + 页面 CSS 坐标；
  找不到时把页面上实际可见的条目列出来（诚实拒绝带证据）。
- `click_page_text`：命中第一个元素后用 **CDP 受信点击**（`getBoundingClientRect` 页面坐标，非视觉坐标），
  点击后复读标题+地址为证。
- 提示词改：浏览器内容一律 `read_page`/`find_on_page`/`click_page_text`，明确写「这台机器没有中文 OCR」。

## 轮 24（搜索 爱莉希雅 歌曲，12:32）：**核心 PASS**
- `web_search` → baidu 搜索页地址证据；`read_page` 读到 **中文正文**：
  `标题「爱莉希雅 歌曲_百度搜索」 地址 https://www.baidu.com/s?wd=…` + 正文（百度一下/综合/文心/图片/资讯/视频/笔记…）；
- 模型又想 `play_music(keyword=爱莉希雅)`，被动词闸门挡回（`没有播歌：这句话里没有播放指令（原文「搜索 爱莉希雅 歌曲」）`）✓；
- 我起的窗口数 1（复用），无新实例。

## 轮 25（打开b站 + 告诉我首页有什么栏目，12:33）：**PASS（P1 路线实证）**
- `open_site(b站)` CDP 导航成功（复读 `['https://www.bilibili.com/']（含 www.bilibili.com）`）；
- `read_page` 读出首页栏目：**首页 / 番剧 / 直播 / 游戏中心 / 会员购 / 漫画 / 赛事 / 下载客户端 / 动态 / 热门 /
  番剧 / 电影 / 国创 / 电视剧 / 综艺 / 纪录片 / 动画 / 游戏 / 鬼畜 / 音乐 / 舞蹈 / 影视 / 娱乐 / 知识 / 科技数码 /
  资讯 / 美食 / 专栏 / 活动 / 课堂 / 社区中心 / 新歌热榜**（+ 视频卡片标题、播放量、时长），
  回复照正文列出「首页、番剧、直播、游戏中心、会员购、漫画、赛事、下载客户端、热门、动态、新歌热榜」——
  **中文 DOM 读取在真实页面上成立，全程无 OCR、无视觉、无坐标**。

## 轮 26（在页面上找到「番剧」并点击，12:35）：**FAIL（模型不点页面，去搜索+抓网页）**
- 模型调 `web_search("打开 b 站")` → 把 b 站**导航走**（`导航成功`，落到 baidu 搜索页）；
- 再两次 `run_python` bs4 → `ModuleNotFoundError: No module named 'bs4'`（这台机器没装，11:14 起就记过），
  一个链接都没读到；全程没调 `find_on_page`/`click_page_text`。
- **修法**（分发层，12:38 编译）：话里有「点击/找到」+「页面/页」→ 拒 `web_search`/`run_python`/
  `read_screen`/`find_on_screen`/`fetch_page`，指名 `find_on_page`/`click_page_text`；
  `web_search` 尾话也改成「要看结果请用 `read_page`（这台机器没有中文 OCR）」。
- 复测轮 27（打开b站）/ 轮 28（点击页面上的番剧）见下一节（跑在 jarvis20）。

## 结果
- **P1 中文读取路线（我起窗口）实证成立**：轮 24/25；
- 页面点击路线工具已就位，模型使用待复测（轮 26 FAIL → 闸门 + 28 复测）；
- **桌面（非我起窗口）中文识别仍未解决**，记 Q37 待你裁决；
- 新增自曝：`pwsh -c` 带反引号的中文串被 PowerShell 转义打断（追加没执行）；我那个「no-op」edit
  把 `s, e = evaluate(RESUME_JS)` 的换行删掉，和下一行黏成一行 → `SyntaxError`（第四次同类事故），补回编译通过。

## 关联
records/2026-11-18-10-17-23.md、record_9.md、need_user.md Q37、progress.md P1②、tests/opinion.md。
