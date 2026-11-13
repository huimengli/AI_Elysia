# Hard Bug 记录

<!-- 已归档于 ai_buckup/hard_bug.md_2026-11-13-00-12-17.md（321 行全量，HB-003 起逐条全文）。上一版归档 ai_buckup/hard_bug.md_2026-10-13-17-45.md（HB-001~HB-008 全文）。本文件为压缩版：**已解决条目 = 一行摘要**，**未解决 / 部分解决条目 = 全文保留**。 -->

## 未解决 / 部分解决（全文保留）

### HB-003 Jarvis 与 llama.cpp 27B 并存内存耗尽（**部分解决**，根因是物理内存不足，需用户知悉）

- 时间：2026-10-12-16-50 ｜ 状态：**部分解决**（策略缓解，根因 = 系统物理内存不足）
- 影响：`python -m jarvis.main` 在 `import kokoro → misaki → spacy` 链中 `MemoryError` 退出；同时把 llama.cpp 的内存/显存撑爆（用户重启过 llama.cpp）。
- 现象：Web 服务已起后 TTS 问候崩溃；llama.cpp 重启前 `/v1/models` 503。
- 根因：llama.cpp 27B BF16（8.7 GB 常驻）+ Jarvis 侧 torch + Kokoro + faster-whisper + 各原生库并发，超出可用物理内存。
- 方案：① 用户重启 llama.cpp 释放内存后再启动 Jarvis（当时可用约 6.2 GB）；② 轻量 `_precache.py` 预下载 TTS/STT 大模型到 `.hf-cache`，避免「边下载边加载」峰值；③ 仍 OOM 则降 llama.cpp 占用（减 `-c` 上下文、减 `-ngl`）或错峰。
- **后续实证（2026-11-12）**：**虚拟内存（页面文件）才是硬约束** —— `av` 报 `DLL load failed … 页面文件太小`、`onnxruntime bad allocation`，停掉 `:7860/:8080/:9880` 后 Free 虚拟 7.5→13.78→15.9 GB 才跑通打分/训练。规矩：**打分、训练、ASR 探针前先停三个服务，跑完重启 + 4 灯复核**。
- 关联需求：records/2026-10-12-12-28-30.md

### HB-032 openWakeWord 打分非确定性：贴近阈值的单次测量不可信（**未解决**，需复测规范 + 补录音）

- 时间：2026-11-11-21-12 ｜ 状态：**未解决**（测量规范已定，数据缺口需用户补录音，见 need_user.md Q13 / `need_audio.md`）
- 影响：唤醒验收与模型换代判据的边界样本结论会随运行翻转。真人近音负样本「爱丽安娜」「爱丽丝」在 v0.6 上 0.7 阈值的检出 1/1 → 1/0 两次不一致，直接决定「是否换模型」的判定。
- 现象：同一音频、同一 `aili_xiya_v0.6.onnx`、同一部署管线，3 次独立 Model 实例（`.tmp/bats/v06determinism.log`）：`爱丽安娜` max 0.753 / 0.730 / 0.732（≥0.7 的 chunk 数 7/4/4），`爱丽丝` max 0.681 / 0.713 / 0.671（0/1/0）。漂移 ±0.02–0.07。
- 尝试：把打分改成与线上完全一致（1280 chunk 逐块、检出后 reset、2 s 冷却）仍不复现同值；训练日志 `Final Model False Positives per Hour: 0.0`（三次训练都是 0.0）也压不住边界翻转。
- 根因：`openwakeword.utils.AudioFeatures.__init__` 用 `np.random.randint(-1000, 1000, 16000*4)` 的随机噪声初始化特征缓冲（utils.py L169），1 s warmup 前缀进入 embedding 流状态，逐 chunk 分数随之每次漂移；贴近 0.7 的近音样本因此落在阈值两侧。
- 方案：① 验收规范：**边界样本必须 ≥3 次独立实例复测**，以「检出次数中位数 + 峰值区间」判定，禁止单次结论；② 判据以部署管线矩阵为准，不采信 `Final Model False Positives per Hour`（只统计 400 条合成 val_fp，反映不出真人近音）；③ 阈值 0.7 对真人近音本质是掷硬币（v0.6 给 0.735/0.708，v0.8 给 0.703/0.789/0.723），要真正消除必须补真人近音 + ≥10 句无关中文短句作负样本（Q13）。
- 关联需求：records/2026-11-11-20-34-04.md；测试 tests/2026-11-11-20-34-04_cc/record_4..6.md

## 已解决条目（一行摘要，全文见归档）

- **HB-001/002/004/005/006/008**（2026-10-13 已解决，全文在 `ai_buckup/hard_bug.md_2026-10-13-17-45.md`）。
- **HB-007**（2026-10-13 已解决）chroma embedding 下载目录 `PermissionError` → 根因 chromadb 硬编码 `C:\Users\楼听\.cache\chroma`；方案预下载至 `.chroma-models/` + `WorkspaceMiniLM` 子类指路。
- **HB-003**（部分解决）见上节。
- **HB-009** jieba_fast 无 Windows wheel、venv 构建死挂 → 仓库根建 shim 包 re-export `jieba.posseg`。
- **HB-010** torchaudio≥2.9 `load()` 依赖 torchcodec（无 win wheel）→ 本地补丁 `_load_audio_compat`（soundfile + `from_numpy(data.T)`）替换两处调用。
- **HB-011** `fast_langdetect` 强制下载 ~1 GB 模型致 `/tts` 挂死 → 仓库副本 monkey-patch 为 `model="lite"`（自带 938 KB `lid.176.ftz`，零下载）。
- **HB-012** GBK 控制台打印 ⌵（U+21B5）崩溃掩盖真实 LLM 错误 → `sys.stdout/stderr.reconfigure(utf-8, errors=replace)` + `_strip_think` 清除残留 thinking 字符。
- **HB-013** Qwen3.8 chat template 拒绝第二条 system（llama.cpp 500）→ memory facts 合并进主 system 单条消息。
- **HB-014** WS 请求 >600 s 挂死（openai stream 迭代器在死连接上无停滞超时）→ `_iter_stream_with_timeout(stream, 120)`（daemon 线程 pump + `q.get(timeout)`）；`max_tokens` 2048→512、`_MAX_TOOL_LOOPS` 15→3。
- **HB-015** e2e「WS 无响应」假阴性 = 测试脚本收到 response 后未 `break`（服务器只发一条）→ 收包日志 + 收 response 即 break；教训「先核对客户端收包日志再动服务端」。
- **HB-016** openWakeWord 训练链四类环境坑（torchaudio 无后端 / 沙箱禁命名管道 / `np.memmap` 无 .npy header / Windows 删打开中的 memmap / DataLoader `num_workers>0`）→ 全部以 `_t2_train_cn.py` 模块级 shim 规避（scipy wavfile、`_SerialThreadPool`、`_finalize_feature_file` → `np.save`、`del fp + gc.collect()`、`num_workers=0`）。
- **HB-017** `num_workers=0` 与显式 `prefetch_factor` 冲突（torch 2.x 硬校验）→ 去掉 `prefetch_factor`。
- **HB-018** `mmap_batch_generator(n_per_class=)` 收 int 而非 dict（上游 train.py/data.py 接口不一致）→ 改传 `{类: 每类窗口数}`。
- **HB-019** `data_transforms` 构建早于正样本类注册 + 窗口函数硬编码 `n=16` → 把 positive/adversarial 文件赋值移到构建之前，`n=input_shape[0]` 动态取帧数。
- **HB-020** `total_length` 双重缺陷（`get_embedding_shape` 入参是秒、上游传整除结果；且 `total_length` 每次从 50 随机 clip 中位数重算、不写 yaml）→ 直接 `np.load(特征.npy).shape` 取 `input_shape`。
- **HB-021 / HB-022 / HB-023**（训练塌缩与音色捷径，2026-10-15~16 记「修复中/执行中」，**已随 v0.3c PASS（10-17 15:44）结案**）：① 高损失挖掘 + 负权重 ramp 致全输入常数 0.999 → 禁挖掘、`max_negative_weight` 1000→1、加 INFO logging；② seq1 `lr=1e-4` 在弱信号上振荡 + DC 漂移致饱和 → `lr=1e-5`（实测 1e-5 无 runaway）；③ 正负样本同一 GSV 音色 → 模型学「音色→触发」→ v0.2/v0.3 数据重造（强变换共享分布 + 真人对抗句）。附带：**torchmetrics stateful 指标必须 reset**（训练日志的 Final Accuracy/Recall 是全程累计值，不可采信）。
- **HB-024** Kellet 粉噪 IIR 极点半径 >1 长信号溢出 inf → 改 FFT 基 1/f 谱整形（任意长度稳定）。
- **HB-025** `make_texts(1700)` 拒绝采样池仅 1075 < 1700 → 死循环空转；改确定性全池构建（池 3935）+ 池 ≥ 目标数 assert；教训「edit 失败后必须重读文件确认落盘再启长作业」。
- **HB-026** v0.2 `train_config` 引用 `val_fp.npy` 但从未为该目录生成 → `_t2_make_val_fp_v02.py` 同配方补齐；教训「换 model_name 时 config 引用的全部产物都要在新目录就位」。
- **HB-027 / HB-028**（2026-10-16~17，**v0.3c PASS 结案**）：~1150 epoch 记忆化 + 训练（batch `embed_clips`）与推理（`predict_clip` 流式）特征管线不一致；特征 npy 两套命名并存导致训练静默消费 2000 行陈旧文件（移入 `_stale_npy/` 隔离）。方案 = `_t2_stream_features_v02.py` 按部署管线重算全部特征 + `steps` 60000→2500；教训「训练实际加载的文件名与行数必须核对」。
- **HB-029** `HF_ENDPOINT=hf-mirror.com` 缺 `https://` scheme → whisper 加载抛「URL missing protocol」；方案启动 env 一律带 scheme。
- **HB-030** 单次 abort 后全局 `_abort` Event 永久置位，污染其后所有 Web/语音请求（每次 0 s 回「已停止。」）→ `_process_request` 顶部 `_abort.clear()`（abort 是一次性信号，不是持久状态）。
- **HB-031** 误唤醒 + 录音期 barge-in 的 `abort_all()` 误杀并发 Web 轮次 + `oww.predict` MemoryError 崩进程 → BUSY 分支先查 `is_recording()`（录音期不打断，仅 2 s 冷却）、IDLE 分支若 `is_speaking()` 视为自身回声（`stop_speaking()` + 3 s 冷却）、predict 加 try/except。

## HB-033 · 2026-11-13 · **已解决（12:20 修复+3 轮）** · `set_volume` 虚假成功、`get_volume` 读错端点

- **影响**：音量类指令永远「报告成功、实际无效」；模型拿不到失败信号，2026-11-08 治理的「工具失败要直说」被工具本身架空。比「模型编造」更危险。
- **现象**（`tests/2026-11-08-20-44-17_cc/record_9.md`，12:12:48）：说「把音量调大」→ 回复「音量已调至最大 (100%)」→ **你核对设备音量仍是 20%**。绕开对话直调工具（零截图）：
  ```
  before: 当前音量 0%。
  音量已设为 40%。      ← 声称成功
  after: 当前音量 0%。   ← 未变
  ```
- **尝试**：直调 `set_volume(40)` + `get_volume()` 复测，确认与模型无关，是工具层问题。
- **根因**：[jarvis/tools/system.py](jarvis/tools/system.py:33) 跑完 PowerShell **不检查 returncode / 不检查输出**，无条件 `return f"音量已设为 {level}%。"`；`get_volume` 用 `GetDefaultAudioEndpoint(0,1)`（`eConsole`），与播放器看到的 20% 不是同一端点，读数恒 0%。
- **方案（已实施）**：`set_volume` 跑完**复读音量做证据**：读数与目标一致（含浮点容差）才返回成功，否则返回 `音量设置失败（stdout/stderr）`；`get_volume` 改读 `GetDefaultAudioEndpoint(0,0)`（`eMultimedia`）。3 轮见 `tests/2026-11-13-12-13-14_cc/`。

## HB-034 · 2026-11-13 · **已解决（12:20 修复+3 轮）** · `read_screen` / `find_on_screen` 因 GBK 解码崩在 reader 线程

- **影响**：屏幕读取能力整条不可用（「你能看得见屏幕吗？」必失败）；`find_on_screen` 依赖 `read_screen`，一并失效。
- **现象**（`record_10.md`，12:13:14；日志 1832-1852 行两次）：`UnicodeDecodeError: 'gbk' codec can't decode byte 0x9c` 抛在 `subprocess.py:1597 _readerthread`，随后 `[Tool: read_screen] 工具「读取屏幕」执行失败：'NoneType' object has no attribute 'strip'`。
- **尝试**：读日志定位解码位置；与轮 6 的 `'NoneType' ... strip'` 症状比对，确认**同名症状、不同根因**（轮 6 是 `title=None`）。
- **根因**：[jarvis/tools/desktop.py](jarvis/tools/desktop.py:117) 的 `_ocr_image` 用 `subprocess.run(..., text=True)`，读取线程按本机代码页 GBK 解码 PowerShell OCR 输出；`result.stdout` 变 `None` → `.strip()` 崩。同文件族已有正确写法 `_ps_utf8`（`text=False` + `decode("utf-8", errors="ignore")`）没被复用。
- **方案（已实施）**：PowerShell 里先设 `[Console]::OutputEncoding = UTF8`，用 `text=False` 拿字节再按 UTF-8 解码；OCR 空结果仍返回 `NO_TEXT`。3 轮见 `tests/2026-11-13-12-13-14_cc/`。

## HB-035 · 2026-11-13 · **已解决（12:20 修复+3 轮）** · `get_weather` 中文地名未 URL quote → ascii 编码崩

- **影响**：所有中文地名的天气查询必失败（12:12:23 连 3 次）。
- **现象**（`record_10.md` 备注；日志 1771-1773 行）：`天气查询失败：'ascii' codec can't encode characters in position 15-17: ordinal not in range(128)`。
- **尝试**：直调 `get_weather("北京")` 复现，确认与模型无关。
- **根因**：[jarvis/tools/web_search.py](jarvis/tools/web_search.py:19) 把中文地名**拼进 URL 未 quote**，`urllib` 在 ascii 编码阶段崩。
- **方案（已实施）**：`urllib.parse.quote(location, safe="")` 后拼 URL。3 轮见 `tests/2026-11-13-12-13-14_cc/`。

## HB-036 · 2026-11-13 13:25 · 已解决（修 + 复测）· `type_text` 中文虚假成功
- **影响**：语音助手让模型「输入文字」时，中文一个字都写不进去却报成功；模型拿到假成功，后续动作全建立在假事实
- **现象**：新起记事本、聚焦、`type_text('爱莉希雅工具测试')` → 返回「已输入文本…」，而记事本标题保持 `无标题 - 记事本`（无 `*` 已修改标记）；ASCII `ABC123` 则标题变 `*无标题 - 记事本`
- **尝试**：先用 OCR 当证据（不可靠，中文插空格）；再用剪贴板 `ctrl+a`/`ctrl+c`（当时 hotkey 未验，证据 False）；最后用标题 `*` 做确定性证据
- **根因**：`pyautogui.write` 对键盘不可映射字符（中文）**静默跳过、不抛异常**；老实现无条件 `return "已输入文本：…"`
- **方案**（已实施）：全部字符可映射时正常键入；含不可映射字符走**剪贴板粘贴**（`set_clipboard(text)` + `ctrl+v`），并**先保存后还原**用户剪贴板；文案明写「键盘打不出 N 个字符」
- **关联**：`tests/2026-11-13-12-59-10_cc/record_8.md`、`need_user.md`（剪贴板 JWT 被覆盖）

## HB-037 · 2026-11-13 13:26 · 已解决（修 + 3 轮）· UWP toast 在本机永远弹不出
- **影响**：`show_notification` 与依赖它的 `set_timer` 提醒全部不可用；老实现把全崩路径包装成「已弹出通知」，模型拿到假成功
- **现象**：正常参数与空参都失败，stderr：`Collection was modified; enumeration operation may not execute`（模板 1 的 text 节点枚举）、`You cannot call a method on a null-valued expression`（`$text[1]` null）、`CreateToastNotifier` → `The process has no package identity. (HRESULT: 0x80073D54)`
- **尝试**：UTF-8 解码 + returncode 校验（止住了 `'NoneType' ... strip'`，但弹不出就是弹不出）
- **根因**：**UWP toast 必须由有包标识的应用创建**，Python/PowerShell 进程没有包标识 → 该 API 路径在本机不可用
- **方案**（已实施）：改用 **NotifyIcon 气泡**（传统 toast，不需要包标识），`Write-Output 'balloon shown'` 作证据，stderr 进失败文案。诚实边界：**气泡是否真出现在屏幕无法程序验证**，需用户肉眼确认
- **关联**：`tests/2026-11-13-12-59-10_cc/record_16.md`、`record_17.md`

## HB-038 · 2026-11-13 13:25 · 已解决（修 + 复测）· `press_key` 对不可识别键名报成功
- **现象**：`press_key("not_a_key")` 返回「已按下：not_a_key」，键盘上没有任何动作
- **根因**：无条件 `return`，没有键名校验
- **方案**（已实施）：逐段校验 `pyautogui.KEYBOARD_KEYS`，不可识别返回「按键失败：无法识别 …（可用键如 enter/space/tab/esc/ctrl/alt/shift/a-z/0-9）」
- **关联**：`tests/2026-11-13-12-59-10_cc/record_9.md`

## HB-039 · 2026-11-13 13:26 · 已解决（修 + 复测）· `screenshot` 写桌面被沙箱拒
- **现象**：`PermissionError: [Errno 13] Permission denied: 'C:\Users\楼听\Desktop\jarvis_tool_test.png'`（服务作为 harness 后台任务启动时桌面禁写）
- **根因**：产物写到 `~/Desktop`，与 HB-033 延伸同族（禁写边界）
- **方案**（已实施）：写工作区 `.tmp/screens/`，文案给出真实路径与字节数（实测 419024 字节）；不读图
- **关联**：`tests/2026-11-13-12-59-10_cc/record_19.md`

## HB-040 · 2026-11-13 13:26 · 未解决 · `_coerce` 把可选参数的默认值架空
- **现象**：`dispatch("set_timer", {"seconds": 3})` → 文案「已设置 3秒 后的提醒：」尾巴为空；`set_timer` 自己的默认中文 `'定时到了！'` 从未生效
- **根因**：`_coerce`（`jarvis/tools/router.py` 第 320 行）对 schema 声明为 string 的**缺失参数**无脑给 `""`，覆盖工具默认值
- **方案**（待实施）：`_coerce` 优先取 schema 的 `default`，否则保留工具默认（不写入 key），再兜底 `""`；同时把需要默认值的项在 schema 里显式声明
- **关联**：`tests/2026-11-13-12-59-10_cc/record_17.md`
