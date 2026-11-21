<!-- 已归档于 ai_buckup/progress.md_2026-11-21-14-42-00.md（103 行 > 100，抽取最近 72 行；旧内容全在备份里） -->
<!-- 归档动作记录：2026-11-21 14:42，见 records/2026-11-21-13-05-50.md 第 9 条 -->

  播歌唯一性起点复用、整句录音、CDP 重连）；**HB-049**（进程死亡无退出码证据；WS `WebSocketDisconnected` 已修）；
  **HB-040**（`_coerce` 架空中文默认参数，未全解决）；**HB-052 蓝屏（P2 · 等复现）**；
  **HB-047 closed/wontfix**（chrome 崩溃 = 内存溢出，你裁决「不需要修，需要用户注意」）。
- **口径对齐（2026-11-20 22:14，追加，不改历史条目）**：**HB-050 closed**（2026-11-18 20:24 方案②端到端 PASS）——
  `hard_bug.md`:66 的 `status: open` 已追加「状态更新」宣布结案；`todo.md`:25 的「方案②待做」同口径改为已 PASS。
  保留的诚实边界照实：`click_page_text` 受信点击在 SPA 导航链接上**仍未证实触发导航**（坐标对、`elementFromPoint` 点下就是目标 SPAN、
  地址复读不变），导航能力照「取 `href` + `Page.navigate`」口径，不照「我点到了」口径。
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

## Git 提交记录（最近条目，全部已本地 commit，未 push；`git rev-list --count HEAD` = 256）
- 2026-11-20 22:14 **19bb430** `docs(AI): 台账对齐 + 蓝屏降 P2 等复现（HB-052）+ design v3.1 加 start_all_in_one` —— 8 文件 +222/−23（record 22-14-46 + `ai_buckup/design.md_2026-11-20-22-14-46.md` + design v3.1 + hard_bug HB-050 状态更新/HB-052 + need_user Q41 状态更新 + todo P2 加一条 + progress P2/open bug 段 + tree.md 重建 607 文件）。照你的话逐字执行：「先对齐,今天就到这,蓝屏的问题改为等复现,p2,monitor加一条start_all改版->保留原start_all,写新start_all_in_one.bat,记录后停工,明天开工」。**今天零代码改动**（`start_all.bat` 未动一个字节，未建 `start_all_in_one.bat`）。开工授权照旧等 Q31-1。自曝第 55 处：沙箱 `process.env` 空 → `git commit` 报 `Author identity unknown`（`$HOME not set`，全局 config 读不到）；照仓库既有身份用 `git -c user.name=绘梦璃 -c user.email=2913394404@qq.com commit -F` 提交，**未改任何 config**。自曝第 56 处：第一次 `git commit -q -F` 失败我没看 stderr（`rev-list` 停在 255、HEAD 没动才发现），第二次才读到身份报错——commit 后必查 `rev-list`/`status`。 (→ records/2026-11-20-22-14-46.md)

- **更早的 commit 条目（709d87a → 08005a5，rev-list 226→246）全量在归档 `ai_buckup/progress.md_2026-11-20-22-14-46.md`**（逐条 hash + 自曝 + 结论），本段只保留 2026-11-20 起。
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
- 2026-11-20 20:45 **蓝屏取证（照你的「start_all 起服务后执行指令后蓝屏了，查怎么回事」）** —— 证实蓝屏码 **0x0000003B SYSTEM_PTE_MISUSE**，参数 `(c0000005, fffff80480908f75, ffffbe88ad5d5fd0, 0)`，dump `C:\Windows\Minidump\112026-9859-01.dmp`（mtime 20:22:48），时间线 20:22:41 开机 / 20:22:42 Kernel-Power 41 / 20:22:51 6008（18:52:46 意外关闭）/ 20:22:52 1001；**10-17 00:29 也蓝屏过**。崩掉的驱动名拿不到：`Minidump`/`WER` 我沙箱读不了（需管理员），机器没有 kd/cdb/windbg。机器是 GPD WIN 4、集显 780M（驱动 2026-07-24）、25 GB、19045；第三方内核驱动一堆（腾讯 ACE、HoYoProtect、QQPCMgr、向日葵、虚拟声卡、inpoutx64、TweakCube 调功率、AMD 性能档）。项目侧：jarvis 18:24 起、19:04:30 最后一条 ASR「播放月增进新声明。」（`near_miss`），19:04:49 起 Chrome，之后无写入；`start_all` 窗口 stdout 不落文件，控制台文字随窗口没了。自曝第 49-51 处，need_user Q41 三样要你给（dump 拷贝授权 / 指令原话 / 内核层装了啥） (→ records/2026-11-20-20-25-21.md)
- 2026-11-20 21:45 **改名后的销毁前检查（照「改源地址文件夹名，试启动，成功就销毁」）** —— 源地址现为 `C:\Users\楼听\Desktop\git\JarvisAi2`；全树逐文件 SHA-256：141,236 文件里 **99,900 逐字节相同**、7,632 哈希不同（7,510 是 `.pyc`；122 文本 = 101 清扫生效 + 18 无路径 + 3 追加式历史照「就算了」）、33,704 新址缺的全是 `.pyc`/Chrome 运行时/commit-graph 派生物，**不是内容缺失**；旧址仍含旧路径 483 文件 1,561 处（新址 0）。计划任务/服务/PATH/Run 键 **零引用旧址**；`.lnk` 未验（脚本两次失败）。123 个 launcher exe 改名后实测全坏，替代 `python -m pip`（pip 26.2.1 正常）。照 `start_all.bat` 权威写法实测三台齐（llama 3.4 s、GSV ~77 s、jarvis `:7860`），与你「用 start_all 好像可以启动」一致。自曝第 52-54 处（我的测试 bat 用了不存在的路径 + latin1 写中文，让你空看三个空转窗口；把残留端口当启动成功；latin1 查旧路径得出假结论） (→ records/2026-11-20-21-01-37.md)
- 2026-11-21 10:30 **修好 DSH 跳过 @local/dsh-my-presets（照「旧版本删除后 dsh 出大问题，怎么才不影响 dsh」）** —— 根因不是 DSH 坏：profile package.json 的 dsh.profile.bundles 列了 @local/dsh-my-presets，dependencies 是**绝对路径** link C:/Users/楼听/Desktop/git/JarvisAi/dsh-my-presets；删旧目录后 node_modules/@local/dsh-my-presets 成悬空链接，resolveBundleDir（apps/cli → app-boot profile.ts）两个锚点都 require.resolve 不到 → **按设计跳过该 bundle 并报错**，DSH 照启动，只是 PTC-MY / 创造模式-MY 不挂载。pnpm 把 link 存成相对路径（lockfile link:../../../Desktop/git/JarvisAi/dsh-my-presets），所以「绝对路径 + 删目录」= 必坏。你把两个包拷进 .dsh\profiles\web2\vendor\，我把两条依赖改成相对 link（link:./vendor/dsh-my-presets、link:./vendor/wow-kit），跑 node apps/cli/lib/bin.js plugin --profile web2 install → pnpm 报 + @local/dsh-my-presets 1.0.0 <- vendor\dsh-my-presets、+ wow-kit 0.1.0 <- vendor\wow-kit（1.5 s）。--dump-config 实测 1,824 行里有「# == @local/dsh-my-presets」层、preset-ptc-my / ptc-my、preset-cordis-my / cordis-my（创造模式-MY），无 skipping。**生效副本从此是 vendor，仓库里的 dsh-my-presets 只是源码备份，改完必须拷过去。** 顺带发现（非本次故障）：profile patch 第 127 行覆盖 id handoff-compaction，而 dsh-handoff-compaction 只在 dependencies、不在 bundles → dump 的 stderr 报 entry "handoff-compaction" not found，你那份 thresholdRatio 0.8 / retainTokens 16000 配置**从来没生效**；wow-kit 同样只在 dependencies，不在 bundles，它的 cordis.patch.yml 一直没挂载。自曝第 55 处：先拿 pnpm dsh --help 试启动器，沙箱里 tsx 拉 esbuild 报 spawn EPERM 白跑一轮，改用编译产物 apps/cli/lib/bin.js 才通；--dump-config 会重写 profile 的 cordis.yml 占位文件，沙箱内 EPERM，需提权才跑得动 (→ records/2026-11-21-10-13-16.md)

- 2026-11-21 10:39 **P1 · 不需要你参与的批次收口（22 轮，18 PASS / 1 FAIL / 3 照实未达）** —— `jarvis/watchdog.py`（194 行，起子进程用**文件重定向**不用管道、pid 判活 + `GetExitCodeProcess`、超时 `TerminateProcess`）+ `jarvis/main.py` 的 `register_clean_exit_hook()`（atexit 写 `.tmp/<tag>.clean_exit`）6 轮全 PASS；真 jarvis 在监督下跑 25.5 s（顺带看到 1 次唤醒触发，`[Wake] peak 0.278 / threshold 0.75`）。到达结尾：轮 12 FAIL（我 `max_wait` 定小）、轮 13 PASS（505.2/505.166）、轮 14 **PASS（到达结尾 + `taskkill` 关掉自己起的 pid 3584 + 关后 0 + profile pids 全 0）**。搜索兜底 3 轮齐（真机 baidu + `cn.bing.com/search` + 打桩路径，真机反爬照旧未测）。能量门 3 轮：span+0.015 → 1/6、concat → 1/6（空/乱码 4）、**span+0.008 → 2/6 与无门持平、空/乱码 0**；whisper 3/6 → 引擎与阈值不动。部署侧 3 轮：**环境音全 0 PASS**、**长噪 3 轮里 2 轮 1 次（峰 0.771）、键盘 3 轮全出现（峰 0.809）、13 次件稳定 3（期望 13）** → 与 v0.9b 召回轴一致，Q42 交你。`_coerce` 42 工具审计干净，**挖出 `TOOL_MAP` 直取键 → `KeyError` 洞并修**（字符串必填灌 `""`、数字/布尔必填不注入不执行），32 项空参数直调无 KeyError。**立案 HB-053：CDP 页面工具没有「只动我起的窗口」闸 + 空串是通配**（我的空参数测试把 DSH 窗口点到必应，back 后已复原）。自曝第 57-69 处。→ records/2026-11-21-10-39-00.md、tests/2026-11-21-10-39-00_cc/（22 轮 + opinion）、hard_bug.md、need_user.md Q42。
- 自曝第 64 处（照实）：**我把「规则说明」当裸中文行写进 `router.py`**（不是注释也不是字符串）→ `SyntaxError: invalid character '，'`，import 全废；修成 `#` 注释才通。写文档串/注释要连引号一起写，不能只写文字。
- 台账动作：`tree.md` 重建（632 非忽略文件，新增 `jarvis/watchdog.py` + 22 件 record + opinion + `ai_buckup/todo.md_2026-11-21-12-00-00.md`）；`todo.md` 101 → 61 行（归档先落）。commit hash 见下条（提交后补记）。

## Git 提交记录（2026-11-21 12:17 追加，提交后补记 hash）

- **e1989cb** `feat(AI): watchdog 子进程监督 + 退出码与收尾标记落盘` —— `jarvis/watchdog.py` 新增 194 行 + `jarvis/main.py` 的 `register_clean_exit_hook()`。6 轮全 PASS。
- **a66fad7** `fix(AI): 必填参数缺失不再吐 KeyError 灌回模型` —— `jarvis/tools/router.py`：`_SCHEMA_REQUIRED` 两档规则（字符串灌 `""`、数字/布尔不注入不执行）。32 项空参数直调无 KeyError。
- **65691d1** `test(AI): P1 无你参与批次 22 轮收口 + 立案 HB-053 + Q42` —— 22 件 record + 批次 `opinion.md`（含笔误更正）+ `tests/opinion.md` 累积 + `records/2026-11-21-10-39-00.md` 完成状态 + `hard_bug.md`（HB-049 状态更新、HB-053）+ `need_user.md` Q42 + `todo.md` 归档压缩 + `tree.md` 重建（635 文件）。
- `git rev-list --count HEAD` = **261**（上次 257）。`git status` 干净，只剩 3 个照旧不 commit 的根目录垃圾（`jarvis_screen.png`、`jieba.cache`、`love_silvia.txt`）。**已本地 commit，未 push。**

- 2026-11-21 12:54 **归因更正（照你的话「focus_window("") 聚焦了「星之翼」，可能是我的问题，我在玩游戏」）** —— 我确实发了聚焦调用（返回「已聚焦」文案），**前台是否被我的调用改动无独立证据**（当时没采前台窗口序列、没做时间对齐）。照实改成「归因未证实，可能是你自己的操作」。顺带照实：**空串通配同样命中窗口工具族**（空标题 = 匹配任意窗口），追加进 HB-053；DSH 窗口被点那条的独立证据链不受影响（back 后已复原）。→ records/2026-11-21-12-54-47.md、record_21.md 追加段、hard_bug.md HB-053 追加段。已本地 commit，未 push。

- 2026-11-21 13:56 **Q42 照数定案 + HB-053 两条修法落地（顺序照你的话「先②后①」）**
  - 同一把尺（同 4 件、同管线、同 0.75）：v1.3 = 长噪 3 轮全 0（峰 0.708）、环境音全 0（峰 0.667）、键盘 3 轮里 1 轮 1 次（峰 0.792）、13 次件 5 次 @5s（2s GAP 9-10）；v0.9b = 长噪 2 轮出现（峰 0.771 踩线）、键盘 3 轮全出现（峰 0.809）、13 次件稳定 3。**照数选 v1.3**，`config.yaml` 指向 v1.3，`threshold: 0.75` 未动，v0.9b 的 label 去掉「现役」。未测照实：真人 20 轮离线表在 v1.3 上未重跑。
  - ② `router._WILDCARD_EMPTY`（8 项工具的必填字符串为空 = 通配/真实副作用 → 直接拒）；① `browser_cdp.targets()` 归属先验（`PID_FILE` + profile，fail-closed）+ `focus_window` 只认自起窗口。验证 3+3 轮全 PASS（`record_5-10.md`）；正面路径在你的会话里未测。
  - 自曝第 71-80 处：`Model` 在 `main()` 里 import（模块层看不到）、台账里写出字面量占位符污染 3 个文件（已逐处修，未覆盖历史内容）、打印用了不存在的键名两次、把参数当字符串切片（`KeyError: slice(...)`）、`const new =` 撞保留字、长串嵌套引号两次炸解析器（改单引号外层 + 数组逐行）、批次目录没建就写文件（ENOENT）。已本地 commit，未 push。
- 2026-11-21 15:01 **Q42 明确测试 20 轮跑满（跨唤醒词轴）**：5 s 冷却合计 v1.3 = 28、v0.9b = 36；小度小度两模型同（26、16/20 轮，峰 0.79-0.80）= 共病；小艺小艺 v1.3 干净（0 vs 9）。合全轴照数仍选 v1.3 @0.75。`threshold: 0.75` 未动。记录 `record_16-35.md` + 批次/累积 opinion。未测照实（真人 20 轮离线表未在 v1.3 重跑、麦克风真呼唤、部署侧在你的会话，服务 7860/8080/9880 未监听）。已本地 commit，未 push。
