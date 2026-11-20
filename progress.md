# 进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-11-20-13-57-30.md（99 行全量：逐条 hash + 结论 + 自曝 + 流水）。
     本文件为压缩版；逐轮细节在 records/、tests/，逐条 hash 完整流水在归档。归档动作记在本台账。 -->

## 当前未结案（口径与依据见 todo.md、need_user.md、hard_bug.md）

- **等你确认（status: wait）**：**Q37**（本机有 OCR，你说「晚点找出来发你地址」；20:26 实测 Umi-OCR 窗口在跑
  pid 8232 **但无监听 50015**，需要你在 Umi-OCR 开「HTTP 服务」并告诉我端口）、**Q36**（微信登录凭据，
  我只「只打开」，不猜密码）、**Q18**（剪贴板 JWT 193 字符善后）、**Q19**（通知气泡肉眼确认）、
  **Q20**（「锁」才真锁屏）。已结案口径：**Q22**（页文件不碰，8 GB 分页）、**Q29/Q32/Q34**（只认 jarvis 自起窗口
  ≤3、只关自起 pid）、**Q31**（chrome 崩溃属内存溢出，wontfix）、**Q33**（`-c 24576` 授权改）、
  **Q35**（你在 jarvis 起的窗口登录一次，cookie 留在 `.tmp\chrome_profile`，取两次交集）。
- **等你授权（HB-051，现象已定性成立）**：方案①播放期间给麦克风门加 ducking（播完/关窗恢复）/
  方案②播放期间暂停唤醒线程 / 方案③写进使用须知。**阈值与 `aili_xiya_v0.9.onnx` 不动。**
- **P1 待办**：①语音 20 轮 **轮 11-20 + 语音 ducking 真人验收**（你 20:21 选「先不跑语音」，现 11/20，照口径未测）；
  ②**jarvis 看门狗 / 退出码落盘**（HB-049：jarvis17、jarvis21 都死过，无退出码证据）；
  ③**到达结尾在实例存活下的复现**（轮 11/15 都在 CDP 断读 = Chrome 实例死亡处，如实记 False）；
  ④**bing 兜底路径**（baidu 从未被挡，未测）；⑤桌面（非我起窗口）中文识别 = Q37 未测。
- **P2**：**项目整体迁移**（你 19:57 定，**Monitor 开工前必须先迁移**）；**Monitor 全系列** +
  **自定义对象设置界面**（design v3.0 已定，同级 P2，先不开工）。
- **open bug**：**HB-051**（播放视频音频触发唤醒，**现象定性成立**，方案等你授权）；**HB-048**（CDP 断读、
  播歌唯一性起点复用、整句录音、CDP 重连）；**HB-049**（进程死亡无退出码证据；WS `WebSocketDisconnected` 已修）；
  **HB-040**（`_coerce` 架空中文默认参数，未全解决）；**HB-050 closed**（2026-11-18 20:24 方案②端到端 PASS）；
  **HB-047 closed/wontfix**（chrome 崩溃 = 内存溢出，你裁决「不需要修，需要用户注意」）。
- **禁区/边界（长期）**：`v0.9 + 阈值 0.75`、`stt.engine: whisper`、`stt.hot_bias: false`、`is_half: false` 不动；
  **0.65 禁区**；边界样本 ≥3 独立 Model 实例取多数（HB-032，实例必须**依次**构造，一次构造 3 个会 `bad allocation`）；
  单探针串行；**页文件不碰（Q22）**；**不最大化窗口**、点击需在任意窗口尺寸准确；jarvis 起窗口 ≤3、播歌唯一 ≤1、
  关后 0；只认 jarvis 自起窗口（profile `.tmp\chrome_profile` = 身份）、**窗口数只认 `_jarvis_windows()`**；
  剪贴板先存后还；`kill_process` 只到记事本；**禁止 git push**；不自行发明命名；`onnx_opinion.md` 6 块 +
  每次追加前备份到 `ai_buckup/`；**md 内容用 write 工具写，不要把带反引号的中文塞进 `Add-Content`/`pwsh -c`**。

## 最近结论（细节在 tests/、records/；全量在归档）

- **2026-11-18 10:17-12:07（37 条记录，非语音）**：2a-2f 站点与微信只打开、播放控制三项（暂停/恢复/关闭，
  CDP 回读为证、关后我起的窗口数 0）、播歌唯一性全程 ≤1 **实测 PASS**；播歌 5 判据 ①导航 ②关弹幕
  ③最低分辨率（640x360/640x338 都判过）④时间前进 成立，⑤关窗轮 15 达成，**「到达结尾」未复现**。
- **2026-11-18 12:25-12:52（record_10/11）**：本机无中文 OCR（WinRT 不可用、Umi-OCR 未装、`:50015` 无监听）
  → 中文读取改走 CDP 读 DOM（`read_page`/`find_on_page`/`click_page_text`，只碰我起窗口）+ 分发层闸门；
  轮 24/25/27 中文正文读出 PASS，轮 26 FAIL（模型 web_search + bs4）→ 闸门后轮 28 只调 `find_on_page`。
- **2026-11-18 20:21-20:26（record_12 轮 29-33）**：**HB-050 结案（方案②端到端 PASS，轮 33）** —— 受信点击后
  地址复读不变 → 取 `href` + CDP `Page.navigate` 导航我起窗口，`https://www.bilibili.com/` →
  `https://www.bilibili.com/anime/`、标题变「番剧 - …」，回复同时写两条事实；轮 33 工具链全由 2B 自选、
  我起窗口数 1（pid 15124）；轮 31b 诚实样本（你关窗口 → 我起窗口数 0，CDP 如实报连不上，闸门挡 `run_python`）。
- **2026-11-18 20:31-20:40（HB-051 定性）**：你逐字「从现在开始录制音频(我用手机放的视频),10秒一段,没有触发就丢弃,
  接下来我不会说触发词」；20 段（16k/mono/10 s、部署语义、不逐 chunk reset）**保存 3 / 丢弃 17**（丢弃段峰值
  0.237-0.689）；**3 个依次构造的独立实例**（同一 onnx + 0.75 不动）：seg_203413_1 → [0.76, 0.795, 0.769]
  越线 [1,1,1] **True**；seg_203623_14 → [0.791, 0.794, 0.773] [2,2,2] **True**；seg_203633_15 →
  [0.676, 0.676, 0.676] [0,0,0] **False**（漂移 ±0.09 照实记）。交叉验证：jarvis22 `Wake word detected!`
  4 → 13、越线 peak 行 9 → 31、`Transcription empty` 3 → 12。**手机视频音频在部署条件下能让 v0.9 越线**
  （两段在 3 实例下稳定越线，不是随机漂移）；你全程没说触发词。自曝：一次构造 3 实例 `bad allocation`、
  `predict(bytes)` 要 numpy 数组。

## Git 提交记录（最近条目，全部已本地 commit，未 push；`git rev-list --count HEAD` = 246）

- 709d87a docs(AI): HB-051 定性成立（10 秒录音法 + HB-032 三实例），progress.md 归档压缩 —— **已本地 commit，未 push**（rev-list = 226）
- 1505453 docs(AI): 1 小时录音法的部分分布 + 停电窗口口径 + 两条自曝 —— **已本地 commit，未 push**（rev-list = 228）
- 3d433b0 docs(AI): HB-051 1 小时 360 段跑完 —— 越线率 2.5%、HB-032 12 段 10 True/2 False —— **已本地 commit，未 push**（rev-list = 230）
- 242e4a3 docs(AI): 12 段越线位置表（听点已切）+ 入库规矩硬冲突摆明 —— **已本地 commit，未 push**（rev-list = 232）
- **e083145** `feat(AI): 复训产出 aili_xiya_v0.9b（12 段真实负样本），3 轮对照铁门槛过线` —— **已本地 commit，未 push**（rev-list = 234）。
  - **自曝（第 14 处）**：commit 信息里我用反引号包文件名，pwsh 把反引号当转义吃掉字母 → python SyntaxError、信息文件没写、
    第一次 `git commit -F` 用了上一轮的**旧信息**（产生错位 commit `32284dc`）；改用 write 工具写信息 + `git commit --amend` 改正为
    `e083145`（本地，未 push，`32284dc` 已被 amend 替换）。规矩复述：**md/commit 内容用 write 工具写，绝不在 `pwsh -c` 里写带反引号的文本**（第 14 次同类事故）。
  - 结果摘要：v0.9b 产物 + 3 轮对照（真人 5/6/5 → 6/5/6 不掉基线；12 段 10/10/10 → 5/4/5；近音 6/7/9 → 3/2/1；无关 2/2/2 → 2/2/2）；
    训练自报 Acc 0.7203 / Rec 0.5958 / FP per Hour 0.0；**现役 `config.yaml` 指向 v0.9 + 0.75 未改（照你「不改」）**。
  - 未测照口径写：部署 13 次真呼唤 3 轮、长噪 62.83 s、环境音期望 0、到达结尾、真人 @0.85 3 轮（服务照「不重启」全停）。

- **a94d591** docs(AI): 第 2 轮 1 小时录音 360 段实测（14 越线 / 346 丢弃）+ 越线位置表 + 2 处自曝 —— **已本地 commit，未 push**。
  - 360 段 / 越线保存 14 / 丢弃 346（3.9%），节奏实测 10.0 s/段；丢弃段 peak 中位 0.441，8 段 >=0.70 按判据不能入库；14 段未入库，等你听 + 授权。
  - 自曝第 15、16 处：越线时刻两次跑会变（2.4 s / 14 次 -> 1.4 s / 7 次），听点改用三实例交集；对照 python 有未定义变量 run（NameError，exit 1）。
  - Q38（数据积累路线）保持 status: wait；真人件不在训练集（时长可重叠对数 0/38）。

- **089c251** docs(AI): rebuild tree.md for record 2026-11-19-15-18-21 —— tree.md 重建 532 文件 / 603 行。**已本地 commit，未 push**。
- 2026-11-19 18:46 5dbf73f test(model): 复训 v0.9c（只入三实例交集 9 段）— 3 轮逐实例真人 [5,5,4] < v0.9 [5,6,5] -> 铁门槛 FAIL，建议废 v0.9c，config.yaml 不动；v0.9b 仍是唯一过线候选。**已本地 commit，未 push**（rev-list 240，main ahead 84）。自曝第 17-24 处。
- 2026-11-19 19:59 6fd7c1b test(model): 20 轮明确测试 v0.9c / v0.9 / v0.9b（同协议 46 件，60 条 record + opinion）。20 轮均值：真人 v0.9 4.00 / v0.9b 4.00 / v0.9c 4.05；近音 5.05 / 1.00 / 2.00；无关 1.10 / 0.00 / 0.00；旧 12 段 8.95 / 0.00 / 2.00；新 9 段 9.00 / 2.00 / 4.00；三家逐轮 PASS 均 0/20（真人判据 >=5 高于现役 20 轮水平，自曝第 28 处）。铁门槛（真人掉于基线->废）**未被违反**；v0.9b 是真人不降+压制最强；config.yaml 不动。**已本地 commit，未 push**（rev-list 241，main ahead 85）。自曝第 25-29 处。
- 2026-11-20 12:33 853205 feat(wake): 换 v0.9b 启动 — config.yaml 指向 aili_xiya_v0.9b（threshold 0.75 不动，model_options 3->4）。三服务起（8080/9880/7860），health 报 model=aili_xiya_v0.9b.onnx / threshold 0.75 / asr+llm+tts online。照实写：启动时 startup greeting 因 :9880 未起完报 WinError 10061；起服务后 1 次唤醒触发（12:28:53，你未对麦克风说话，STT 无语音、max rms 0.0038）= **1 次环境 FP（期望 0，违反）**。自曝第 32 处（peak 日志不是触发，读 wake.py:175-180 纠正）。部署 3 轮仍**未测**（等你麦克风前）；@0.85 不做。**已本地 commit，未 push**（rev-list 242，main ahead 86）。
- 2026-11-20 12:40 3084bb2 chore(services): 停掉所有服务（你要开始迁移）。停 llama 17988 / GSV 17096+17676 / jarvis 18556+10556，复验 8080/9880/7860 全 DOWN、无残留进程、health 连不上。config.yaml 仍指向 v0.9b（threshold 0.75 不动）；部署 3 轮继续**未测**；@0.85 不做。自曝第 33 处（$pid 只读自动变量坑，第一次读到的是我自己 pwsh 的 pid）。**已本地 commit，未 push**（rev-list 244，main ahead 88）。
- 2026-11-20 13:20 迁移校验（只读，无代码改动）：全量递归 + 逐文件 SHA-256（27 GB，290 s）。原/新各 141236 文件，相对路径与大小 100% 一致，内容 0 处不一致，目录 13776/13776，符号链接 0/0，`.git`（2257 文件、13,276,709 B、HEAD/packed-refs/config/index）完全相同，`main` = 3084bb27d81d4405b49ebe0530882f897b785f6e。**新址是全量完整副本，文件零缺失**。清空前的实测阻塞点：全树 269 处硬编码旧路径（`config.yaml` 7、`.venv*/activate.bat` 各 1、`openWakeWord/train_config*` 112、`training/` 67、`tests/` 82、`.tmp/` 183 等）；`jarvis/` 与 `start.bat`/`start_all.bat`/`install.bat` 用 `%~dp0` 不受影响。自曝第 34 处（沙箱 `spawn EPERM` 跑不了 git，改用直读 `.git` 文件比对）。Q39 等你定。(→ records/2026-11-20-13-20-00.md)
- 2026-11-20 13:44 **c51482e** `fix(AI): config.yaml 改相对地址（照你的话：我的名字不应出现在数据里）` —— 6 行 `C:\Users\楼听\Desktop\git\JarvisAi\` 前缀删掉（唤醒 ONNX x4、sherpa `model_dir`、llama gguf → `openWakeWord/output/<模型>/<模型>.onnx` / `.hf-cache/sherpa-paraformer-zh` / `llm/models/Qwen3.5-2B-Q4_K_M.gguf`），threshold 与 label 不动。照实测：config 里 `楼听` 0 / `u697C` 0 / 旧前缀 0；7 条相对路径逐一实测存在（onnx 13852/13735/13735/13852 B、sherpa `model.int8.onnx` 81,828,675 B + `tokens.txt`、gguf 1,280,835,840 B）；YAML 解析器读一遍确认解析后就是相对路径，`wake.py`:82 `Path(spec).exists()` 在 cwd=项目根时 true。**起服务复测未做（沙箱跑不了 python）**；自曝第 36 处（第一次替换漏吃一个反斜杠，留下前导 `\`）。**已本地 commit，未 push**（rev-list 245，main ahead 89）。(→ records/2026-11-20-13-44-31.md)

- 2026-11-20 13:56 **08005a5** `docs(AI): config.yaml 相对路径的真加载验证 + Q40 姓名残留清点` —— 照 wake.py/stt.py 的实际调用跑 venv python（cwd=项目根，只读盘不碰麦克风）：openwakeword `Model(wakeword_models=[相对路径])` 加载成功，`m.models`=[aili_xiya_v0.9b]，predict 后 `prediction_buffer` 有 `aili_xiya_v0.9b`（wake.py:82 用的 key）→ 相对路径与改前等效；sherpa `from_paraformer` 从 `.hf-cache/sherpa-paraformer-zh` 加载成功。姓名残留 560 行清点进 Q40（代码/配置 366、历史 md 194，改历史需你逐字授权）。自曝第 37 处（查 `m.wakeword_models` 不存在）。部署 3 轮照旧未测。**已本地 commit，未 push**（rev-list 246，main ahead 90）。(→ records/2026-11-20-13-44-31.md)
- 2026-11-20 15:12 **姓名残留清扫（照你的话「能改相对地址的改,不行就算了」）** —— 157 文件 323 处旧前缀 → 0（`training/*.py` 用 `ROOT = r"."`、`openWakeWord/train_config*` 相对、`_wheels/*.ps1` 用 `$PSScriptRoot\..`、`.venv*` 文本改新址、`desktop.py:309` 姓名泛化）。验证：338 `.py` py_compile 全过、18 yaml 全解析、3 ps1 PowerShell Parser PARSE OK；照 stt.py/wake.py 的调用实测 SHERPA LOADED + WAKE key `aili_xiya_v0.9b` 在 buffer、阈值 0.75；`jarvis` 8 模块 import OK；`start.bat` 链实测 python = 新址。**删掉 41,433 个 `.pyc`（763 MB）**，重生后 2,401 个 pyc 含旧前缀 0、含姓名 0。照「就算了」不动：123 个 launcher `.exe`（定长 shebang，两种保长度改法实测启动失败，已按原字节从旧址恢复）、`pyvenv.cfg` 的 `home`（AppData 全局 Python）、103 行旧路径全在追加式历史 md（改历史需你逐字授权）、108 行外部绝对路径、23 行纯人名、`.git` 历史对象。自曝第 38-42 处（先动文件后落盘；`fs` 直写 `.exe` 写坏 132 个后逐字节恢复；「未清干净 0」是假的、转义形式漏 6 文件；ps1 检查手拼引号报错；空 env 下 `Path.home()` 让我误判 jarvis import 失败）。部署 3 轮照旧未测。(→ records/2026-11-20-15-12-16.md)
- 2026-11-20 15:47 **abf2491** `refactor(AI): 照你的话「能改相对地址的改,不行就算了」—— 旧项目前缀清成相对地址` —— 46 文件 +128/−68（`training/*.py` 42 个脚本 `ROOT` 相对化、`desktop.py` 姓名泛化、record/todo/progress）。工作区里另有 111 个被 .gitignore 的文件同批改（`openWakeWord/train_config*` 16、`.tmp/` 92、`_wheels/` 3、`.venv*` 文本 4）。已本地 commit，未 push（rev-list 248）。
- 2026-11-20 15:48 **56f9881** `docs(AI): 重建 tree.md（602 非忽略文件，含 3 条新 record + progress 归档）` —— 照 AGENTS.md 第 2 节重建。已本地 commit，未 push（rev-list 249，main ahead 93）。
- 自曝第 43 处：上一条 commit 的信息里我把 tree.md 的哈希写成 `56f9886`（真哈希 `56f9881`），已 `--amend` 改正为 9ff2d07。哈希要照 `git rev-parse` 取，不能凭记忆。
- 2026-11-20 18:20 **本地起服务实测（照你的「本地起一下服务,看看能不能启动」）** —— 三台全起得来：llama :8080 加载 3.4 s + health 200；GPT-SoVITS :9880 约 77 s 起（Elysia GPT/SoVITS + roberta + hubert，cpu），真 TTS 探针 200 / 162,604 B / 32000 Hz / 2.54 s / 4,054 ms；jarvis :7860 1.7 s 起，`/api/health` 四块全 online（wake `aili_xiya_v0.9b.onnx` 0.75、whisper small warm、llama、GSV）。真 LLM 探针照 jarvis 形状 → content「收到」385 ms；照签名 `jarvis.llm.chat([…])` → `'收到'`。起的进程随我的程序结束被杀（两次实测端口全 FREE），常驻要你自己跑 `start_all.bat`。起 jarvis 期间真触发 3 次唤醒（peak 0.768/0.765/0.757，ack 播 2.26/3.32 s，录音 2.1 s 空转录），照实写、不算 3 轮验收。自曝第 44-47 处 (→ records/2026-11-20-16-26-59.md)
- 自曝第 48 处：我起的三台服务（env 是我拼的，缺 `ALLUSERSPROFILE`）在**项目根**造了个垃圾目录 `%ALLUSERSPROFILE%\Application Data\Tencent\QQPCMgr\`（`dr.ini` 2 B + `dr_packet.dat` 0 B，创建 16:38，正好是我第一次起服务的时刻）—— 有代码把 `%ALLUSERSPROFILE%` 当字面路径写。已整目录删掉（5 项 2 字节），未进 Git。教训：**我拼的 env 和真实会话的 env 不等价**，起服务要照 `start_all.bat` 在你的会话里起，我这边起的进程随程序结束被杀、还会留下这类残渣。


