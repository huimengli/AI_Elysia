# Hard Bug 记录

<!-- 已归档于 ai_buckup/hard_bug.md_2026-10-13-17-45.md（HB-001~HB-008 全文，含 HB-007 未解决状态快照） -->

> 2026-10-13-17:4x：HB-001/002/004/005/006/008 已解决并归档；**HB-007（chroma embedding 下载目录 PermissionError）当日解决**——根因：chromadb 默认 ONNXMiniLM 模型硬编码下载到 `C:\Users\楼听\.cache\chroma`（沙箱不可写）；方案：模型预下载至工作区 `.chroma-models/` + `jarvis/memory.py` `WorkspaceMiniLM` 子类指路，实测 store/search OK。详见 records/2026-10-13-11-55.md 与 progress.md。

## HB-003 Jarvis 与 llama.cpp 27B 并存内存耗尽（部分解决）

- 时间：2026-10-12-16-50
- 状态：部分解决（策略缓解，根因是系统物理内存不足，需用户知悉）
- 影响：`python -m jarvis.main` 启动阶段 `import kokoro → misaki → spacy` 链中 `MemoryError`，进程退出；同时把 llama.cpp 的内存/显存撑爆（用户反馈并重启了 llama.cpp）。
- 现象：Web 服务已起（[Web] Event loop captured）后 TTS 问候崩溃；llama.cpp 重启前 `/v1/models` 503。
- 根因：llama.cpp 27B BF16（8.7GB 常驻内存/显存）+ Jarvis 侧 torch + Kokoro + faster-whisper + 各原生库并发，超出系统可用物理内存。
- 方案：
  1. 用户重启 llama.cpp 释放内存后启动 Jarvis（当前可用约 6.2 GB）。
  2. 用轻量 `_precache.py` 预下载 TTS/STT 大模型到 `.hf-cache`，避免主进程"边下载边加载"的峰值。
  3. 若仍 OOM：建议用户降低 llama.cpp 占用（减小 `-c` 上下文、减少 GPU 层 `-ngl`）或错峰运行。
- 关联需求：records/2026-10-12-12-28-30.md

## HB-009 jieba_fast 无 Windows wheel，venv 构建死挂（已解决）

- 时间：2026-10-13-17-4x
- 状态：已解决
- 影响：`.venv-gsv` 按 `GPT-SoVITS-main/requirements.txt` 安装时，jieba_fast（sdist + C 扩展）在 PEP517 隔离构建处死挂（>900s 无进展），阻断 TTS venv 就绪。
- 现象：pip "Installing build dependencies: started" 后长时间无输出；tuna 镜像页确认 jieba/jieba_fast 均零 wheel。
- 尝试：默认安装（死挂）→ 预装 setuptools/wheel + `--no-build-isolation` 本地构建 jieba 成功；jieba_fast 仍不可行（C 扩展构建环境缺失）。
- 根因：镜像无 Windows wheel；沙箱拦截 PEP517 隔离临时 venv 写入导致构建挂起。
- 方案：jieba 以 `--no-build-isolation` 本地构建；**api_v2 导入 `jieba_fast.posseg` 缺失 → 仓库根建 shim 包 `GPT-SoVITS-main/jieba_fast/`（`__init__.py` re-export jieba、`posseg.py` re-export jieba.posseg）**，repo 根在 sys.path[0] 优先命中，不动 site-packages。
- 关联需求：records/2026-10-13-11-55.md

## HB-010 torchaudio≥2.9 `load()` 依赖 torchcodec（无 Windows wheel），/tts 返回 400（已解决）

- 时间：2026-10-13-19-2x
- 状态：已解决
- 影响：api_v2 `/tts` 首次合成必崩：`TorchCodec is required for load_with_torchcodec. Please install torchcodec to use this function.`（HTTP 400）。
- 现象：Elysia 权重加载成功后，任何 /tts 请求均 400；错误体来自 `TTS_infer_pack/TTS.py` 的 `torchaudio.load`。
- 尝试：tuna 镜像 simple index 确认 torchcodec **353 个文件、0 个 Windows wheel** → 无法 pip 安装。
- 根因：torchaudio 2.14 运行时将 `load()` 委托给 torchcodec 后端；该包无 win64 wheel。
- 方案：本地补丁（仅仓库副本，不碰 site-packages）：`GPT_SoVITS/TTS_infer_pack/TTS.py` 增 `_load_audio_compat(path)`（soundfile + `torch.from_numpy(data.T).contiguous()`，float32 always_2d，与 torchaudio.load 语义等价），替换 `load_audio_gpu` 与 `_get_ref_spec` 两处调用。
- 关联需求：records/2026-10-13-11-55.md

## HB-011 fast_langdetect/split_lang 强制下载 ~1GB 模型（外网不可达），/tts 请求挂死（已解决）

- 时间：2026-10-13-19-4x
- 状态：已解决
- 影响：/tts 请求处理中 `split_lang` 语言检测调用 `fast_langdetect.detect(model="full")` → 尝试从 `dl.fbaipublicfiles.com` 下载 `lid.176.bin`（~1GB），连接不可达 → 服务端卡死、客户端超时。
- 现象：服务器日志停在 "fast-langdetect: Downloading model from https://dl.fbaipublicfiles.com/..."；先因缓存目录不存在报 400（"Cache directory not found"），建目录后转为下载挂死。
- 尝试：① 在 `langsegmenter.py` 给 `_default_detector` 设 `model="lite"` → 无效，因 `split_lang` 包内 `detector.py` **硬编码** `model="full"` 且自建 detector；② 确认无本地全量模型、外网 CDN 不可达。
- 根因：`split_lang` pip 包（site-packages）硬编码 full 模型 + Facebook CDN 在本环境不可达。
- 方案：不碰 site-packages——在仓库副本 `GPT_SoVITS/text/LangSegmenter/langsegmenter.py` 运行期 monkey-patch `_detector.fast_lang_detect` / `_possible_detection_list` 为 `model="lite"`（fast-langdetect 包自带量化模型 `lid.176.ftz`，938KB，零下载）；并建 `GPT_SoVITS/pretrained_models/fast_langdetect/` 空目录防"目录不存在"报错。
- 关联需求：records/2026-10-13-11-55.md

## HB-012 GBK 控制台打印含 ⌵（U+21B5）异常信息崩溃，掩盖真实错误（已解决）

- 时间：2026-10-13-20-4x
- 状态：已解决（修复已实施，随 HB-013 一并于 e2e 复验）
- 影响：`_process_request` 捕获 LLM 异常后执行 `print(f"[WARN] Primary provider failed ({e}), trying Ollama fallback")`；当 `{e}` 文本含 Qwen thinking 标记 ⌵（U+21B5）时，GBK 控制台 `UnicodeEncodeError: 'gbk' codec can't encode character '\u21b5'`，异常从 print 处上抛 → Web WS 收到 `Error: 'gbk' codec...`，**真实 LLM 错误被完全掩盖**，且 Ollama 回退路径从未执行。
- 现象：`.jarvis-run.log` traceback：`main.py line 416 print` → `UnicodeEncodeError`；WS e2e 两案例均返回该 GBK 错误文本。
- 根因：Windows 控制台默认 GBK 编码；LLM/工具输出可含 GBK 不可编码字符（Qwen thinking 标记 ⌵/⌖）。
- 方案：`jarvis/main.py` 顶部对 `sys.stdout`/`sys.stderr` `reconfigure(encoding="utf-8", errors="replace")`，print 永不因编码崩溃；同时增强 `_strip_think`：剥离成对 thinking 标签后，额外清除残留 ⌵（U+21B5）/⌖（U+21B6）字符，防止泄漏进 TTS/前端。
- 关联需求：records/2026-10-13-11-55.md

## HB-013 Qwen3.8 chat template 拒绝第二条 system 消息，llama.cpp 返回 500（已解决）

- 时间：2026-10-13-20-5x
- 状态：已解决（修复已实施，随 e2e 复验）
- 影响：memory facts 非空时 `_process_request` 构造 `[system(主提示)] + [system(facts)] + ...` 双 system 消息 → llama.cpp Jinja `500 System message must be at the beginning.` → 经 HB-012 的 GBK print 崩溃后以 `Error: 'gbk' codec...` 呈现给 WS 客户端。
- 现象：curl 矩阵隔离——单 system + user/tools/chat_template_kwargs 全部 OK；**两条 system 必 500**。从 GGUF metadata（`_gguf_template.py` 手工解析 header）提取 `tokenizer.chat_template`（8952 字符）证实：该模板 `{%- for message in messages %}` 循环内对任何非首位 system 消息 `raise_exception('System message must be at the beginning.')`（标准 Qwen3 模板只检查 messages[0]，此"Qwen3.8"新模板检查所有位置）。
- 根因：`jarvis/main.py` `_process_request` 将 memory facts 作为独立 system 消息插入；新模型模板不允许多条 system。
- 方案：facts 合并进主 system prompt 单条消息（`sys_content = _system_prompt(); if facts: sys_content += "\n\nRelevant context from memory: ..."`），全链路仅一条 system。curl 双 system 500 / 单 system OK 已实测验证。
- 关联需求：records/2026-10-13-11-55.md

## HB-014 WS chat 请求 >600s 挂死：OpenAI stream 迭代器在死连接上无限阻塞（已解决）

- 时间：2026-10-13-23-5x ～ 2026-10-14-18-5x
- 状态：已解决（修复已实施，随 e2e 复验）
- 影响：WS chat（及语音管线）触发的 `_process_request` 在"思考中…"之后可能 >600s 无任何响应、无报错；`_cn_test.py` 首 recv 超时。
- 现象：打点复测 `[DBG] chunks=1 +17.3s` 后不再有任何 chunk，`llm done` 永不打印；期间 llama-server（pid 11012）5 s CPU 零增长、`/health` ok，且 Jarvis(868)↔:8080 **无任何 TCP 连接**——socket 两端已死，客户端 `for chunk in stream` 迭代器既不抛错也不结束。
- 尝试/排除：
  1. 直接复刻 `_call_openai_provider`（tools=TOOL_SCHEMAS、max_tokens=2048、streaming、enable_thinking=False）：113 s 完成、loop 1、无 tool call → LLM+tools 路径本身健康；
  2. 新进程 `Memory()` 初始化 1.3 s、`search_facts` 0.4 s → chroma/ONNXMiniLM 路径快；
  3. `_play_beep` 7.6 s（慢但有限）；无并发请求时全链路 37.6 s（probe：connected→response 全程计时）→ 服务器进程各阶段本身均快。
- 根因：客户端侧——openai SDK stream 迭代器在 chunk 之间没有独立停滞超时（`timeout=300` 只约束连接级读）；llama.cpp 中途掐断流（进程存活、health ok、CPU 零，疑似 slot idle/重置或 iGPU TDR，本环境无法进一步确认服务端原因）后，死/半开 socket 使 recv 既不返回数据也不可靠地得到 EOF，生成器永久阻塞。
- 方案：`jarvis/main.py` 新增 `_iter_stream_with_timeout(stream, timeout=120)`——daemon 线程 pump chunk 入 `queue.Queue`，主循环 `q.get(timeout=120)`：120 s 无 chunk → 抛 `TimeoutError` → 经 `_process_request` "Primary provider failed" 分支在有限时间内向 WS 回 `Error: ...`（不再静默挂死）；配套收敛最坏时长：`_MAX_TOOL_LOOPS` 15→3、`config.yaml llm.max_tokens` 2048→512。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-015 e2e "WS 无响应"假阴性：测试脚本收 response 后未 break，持续等待下一条消息至 600s 超时（已解决）

- 时间：2026-10-14-21-3x ～ 2026-10-14-22-0x
- 状态：已解决（测试脚本修复；正式 e2e PASS 34.7s）
- 影响：`_cn_test.py` 连续多次"失败"（每次 600s 超时、无响应），误导排查方向——一度怀疑 web.py 响应投递路径缺失，甚至临时加过直接 `ws.send_text`（造成 response 双份投递后撤除）。
- 现象：服务器端打点证明全链路完整：`after_call_llm len=65` → `_process_request returned` →（加测后）`response send completed`；而客户端 600s 收不到任何东西。
- 根因：**测试脚本缺陷**——recv 循环中 `if mtype == "response": response_parts.append(...)` 之后没有 `break`，服务器每轮 chat 只发一条完整 response 即静默，于是循环以新的 600s 超时继续等下一条永远不来的消息 → `TimeoutError`。收包日志（`_cn_test_recv.log`）证实 response 实际在 **37.0s** 已送达（且 HB-014 修复后广播路径正常）。
- 方案：`_cn_test.py` 收到 `type == "response"` 即 `break`；并加逐条收包日志（时间戳 + 原文）防再误判。服务器代码保持原设计：response 仅经 `main._broadcast`（事件监听 → `_broadcast_to_ws`）单路径投递，web.py 不重复直发。
- 教训：e2e "无响应"类故障先核对**客户端收包日志**再动服务端；打点应覆盖收发两端。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-016 openwakeword 训练链在"venv 残缺 + Windows 沙箱"下的四类环境坑（已解决，shim 固化于 _t2_train_cn.py）

- 时间：2026-10-14-23-0x
- 状态：已解决（全部以 `_t2_train_cn.py` 模块级 shim/补丁方式规避，不动 site-packages；dry-run 全链 PASS 验证）
- 影响：`--augment_clips` / `--train_model` 在本环境直接运行必崩（四处独立阻塞点，逐一定位修复后才跑通 dry-run）。
- 现象与根因：
  1. **torchaudio 无可用后端**：torchaudio 2.11+cpu 默认后端 torchcodec 未装（`ImportError`），soundfile 后端缺 `libsndfile.dll`（OSError 0x7e）→ `openwakeword.data.augment_clips` 运行时 `torchaudio.load/.info`（9 处）全崩。shim：scipy.io.wavfile + wave 替换（int16→float32/32768、声道取均值；info 返回 SimpleNamespace）。
  2. **沙箱禁命名管道**：CPU provider 下 `AudioFeatures._get_melspectrogram_batch/_get_embeddings_batch` 必建 `multiprocessing.pool.ThreadPool`（Windows 下 Pool 创建即走命名管道 IPC）→ `PermissionError WinError 5`；且无 ncpu=1 串行分支。shim：`openwakeword.utils.ThreadPool` 替换为串行假池。**注意**：对已 `from ... import X` 的模块须重绑其自身全局名，仅改源模块属性无效。
  3. **numpy 2.x `np.memmap` 写裸二进制无 .npy header**（venv 实测）：上游 `trim_mmap` 用 `np.load(mmap_mode='r')` 读回在任何平台都失败（`ValueError: pickled (object) data`）；且训练分支 `mmap_batch_generator`（788 行）同样 `np.load` → 最终特征文件必须 `np.save` 成规范 .npy。
  4. **Windows 删打开中的 memmap 文件**：`compute_features_from_generator` 写句柄 `fp` 未关时调 trim → `WinError 32`。须先 `del fp + gc.collect()`。
  5. **torch DataLoader `num_workers>0`**（trainer 1060 行）：Windows spawn 上下文同样依赖命名管道 → 沙箱 WinError 5。改 `num_workers=0`（进程内加载，仅变慢）。
- 方案：`_t2_train_cn.py` shim 区固化：torchaudio 替换 / `_SerialThreadPool` / `_finalize_feature_file`（np.fromfile 读裸数组→按 row_counter 截断→np.save 规范 .npy）+ `_compute_features_patched`；train 分支 `num_workers=0`。全风险清单见 records/2026-10-13-21-38-01.md 23:1x/23:3x。
- 教训：本 venv 训练任何依赖 torchaudio/多进程/np.memmap 的开源流水线前先查这三类坑；沙箱内命名管道类失败（WinError 5）一律改单进程路径，不要尝试提权绕过。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-017 DataLoader `num_workers=0` 与显式 `prefetch_factor` 冲突（已解决）

- 时间：2026-10-15-13-5x
- 状态：已解决
- 影响：T2 `--train_model` 在 DataLoader 构造处即崩，训练无法启动（augment 阶段已成功，四特征 .npy 已落盘）。
- 现象：`ValueError: prefetch_factor option could only be specified in multiprocessing. Let num_workers > 0 to enable multiprocessing, otherwise set prefetch_factor to None.`（torch 2.x 对 `num_workers=0` + `prefetch_factor=16` 的硬校验；dry-run 未触达该行，故此前漏检）。
- 根因：HB-016 第 5 条改 `num_workers=0` 时保留了上游显式 `prefetch_factor=16`。
- 方案：`_t2_train_cn.py` train 分支 DataLoader 去掉 `prefetch_factor`（`num_workers=0` 时默认即 None），py_compile 通过；重跑链（augment 因特征文件已存在而跳过，直达 train）。
- 教训：改 DataLoader 并发参数时同步清掉只与多进程相关的选项（prefetch_factor/persistent_workers）。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-018 `mmap_batch_generator` 的 `n_per_class` 收到 int 而非 dict（已解决）

- 时间：2026-10-15-14-1x
- 状态：已解决
- 影响：T2 `--train_model` 在批次生成器构造处即崩，训练无法启动。
- 现象：`AttributeError: 'int' object has no attribute 'items'`（`openwakeword/data.py:825` `for label, n in self.n_per_class.items()`）。
- 根因：上游 `train.py:847` 直接把 `config["batch_n_per_class"]`（int=32）传给 `mmap_batch_generator(n_per_class=...)`，而该参数需要 `{类名: 每类窗口数}` dict；自动计算分支（data.py:800-816）仅在参数为假值时触发。
- 方案：`_t2_train_cn.py` train 分支改传 `n_per_class={key: config["batch_n_per_class"] for key in feature_data_files.keys()}`（3 类 × 32；每类 32 clip × 27 帧窗口 = 864 条，整除无余）。
- 教训：上游 train.py 与 data.py 接口不一致属上游 bug，fork 副本中修参即可，勿改 site-packages。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-019 `data_transforms` 构建顺序早于正样本类注册 + 窗口函数硬编码 `n=16`（已解决）

- 时间：2026-10-15-14-3x
- 状态：已解决（待冒烟/正式训练运行时复验）
- 影响：T2 `--train_model` 首批 vstack 即崩；且即使不崩，模型输入帧数与特征文件不符导致前向失败。
- 现象：`ValueError: ... along dimension 1, the array at index 0 has size 16 and the array at index 1 has size 27`（`data.py:852` `np.vstack(X)`）。
- 根因（两处独立缺陷叠加）：
  1. **行序 bug**：上游 train 分支先构建 `data_transforms = {key: f for key in feature_data_files}`，之后才把 `'positive'/'adversarial_negative'` 追加进 `feature_data_files` → 这两个类在生成器中 `self.data_transform_funcs.get(label)` 为 None（data.py:835）跳过窗口变换，保持原始 27 帧；而 'negative' 被切成 16 帧 → vstack 维数不一致。
  2. **硬编码 n=16**：上游 `f(x, n=16)` 仅在 total_length ≤ 36000 样本（16 帧）时成立；本数据集 clip > 2 s → 特征 (N, 27, 96)，模型 `input_shape[0]=27`（`get_embedding_shape(total_length//16000)`），n=16 的窗口与模型输入不符。
- 方案：`_t2_train_cn.py` train 分支：① 把 positive/adversarial_negative 的文件赋值移到 `data_transforms` 构建**之前**（三类同享同一变换）；② `def f(x, n=input_shape[0])` 动态取帧数（NOTE 注释说明上游 16 的适用边界）。
- 教训：改训练分支逻辑顺序前，先核对"字典构建点"与"其依赖数据完成填充点"的先后；窗口/池化类参数一律与 `input_shape` 联动，勿沿用上游魔数。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-020 `total_length` 双重缺陷 → 模型输入帧数与特征不符（已解决）

- 时间：2026-10-15-16-2x
- 状态：已解决（待冒烟复验）
- 影响：T2 `--train_model` 训练循环本身正常（~100 it/s），但首次 X_val 验证前向即崩，模型无法收敛/导出。
- 现象：先 `mat1 and mat2 shapes cannot be multiplied (800x2592 and 1536x128)`（模型 T=16）；改浮点后仍 `(800x2592 and 2400x128)`（模型 T=25，特征实为 27 帧）。
- 根因（两层独立缺陷叠加）：
  1. **整除截断**：`utils.py:238 get_embedding_shape(audio_length: float, sr=16000)` 入参是**秒（浮点）**；上游 train.py 传 `total_length//16000`。上游默认 total_length=32000 恰为 16000 整数倍无感；本数据 total_length≈44000–47000 → 截断到 2 s → 合成 32000 样本 → 16 帧。
  2. **total_length 不持久 + 随机采样漂移**（改浮点后暴露）：`total_length` 每次运行都从 positive_test 的 **50 个随机 clip 中位数**重算（train.py:937-947），**不写入 yaml**。本数据 clip 时长双峰，两次运行的随机中位数分属不同峰 → generate 运行得 27 帧特征、train 运行得 25 帧模型输入。
- 方案：`_t2_train_cn.py` train 分支不再调 `get_embedding_shape`，直接 `np.load("positive_features_test.npy", mmap_mode="r").shape` 取 `(frames, melbins)`=(27,96) 作为 `input_shape`（确定性、与数据恒一致）。
- 教训：凡"运行期重算且未持久化"的量，跨进程/跨阶段复用前必须核对一致性；模型输入形状一律以落盘特征文件为准。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-021 训练塌缩：高损失挖掘 + 负权重 ramp → 全输入常数 0.999（修复中，重训 pwsh-23）

- 时间：2026-10-15-17-0x
- 状态：修复已实施，重训+验收运行中（pwsh-23）
- 影响：生产训练（60000+6000+6000 步）"正常完成"并导出 ONNX，但验收全阈值 FAIL：pos/neg 均 ≈0.999（recall=1.0 / false=1.0），模型不可用。
- 现象：`_t2_verify_result.txt` pos mean/max=0.999/0.999、neg 0.999/0.999；诊断脚本 `_diag_onnx.py`：静音→0.999、随机噪声→0.9989、8 个真实 pos/neg clip 全部 0.999（仅 1 个 neg=0.000）；最终层 Gemm 权重 L2=1.35（非零）但**最终偏置≈+7.4**（sigmoid(7.4)≈0.9994），决策被偏置主导。
- 根因（训练动力学缺陷，非数据管线 bug——标签映射已核实正确 positive→1/adversarial_negative→0）：
  1. `train_model` 的"高损失样本挖掘"（只回传 pred≥0.001 的负样本与 pred<0.999 的正样本）+ seq1 负权重 `linspace(1→1000)`；
  2. 负样本被快速压到 <0.001 后**永久退出 batch**，之后数万步 batch 几乎全是正样本（权重 1）→ 最终层偏置被单向推高至饱和；
  3. 待所有正样本也达到 0.999 上限后，batch 变空，训练空转"收敛"——退化解固定点。
- 附带缺陷：验证指标只写内存 `self.history`，且脚本未配置 logging handler（INFO 级被静默丢弃）→ `_t2_train.log` 无任何验证轨迹，事故无法从日志回溯。
- 方案：① `_t2_train_cn.py` 禁用高损失挖掘（全量平衡 batch，两类始终有梯度）；② `train_config.yaml` `max_negative_weight: 1000→1`（去 ramp）；③ `__main__` 加 `logging.basicConfig(level=INFO)` 保留验证轨迹；④ 重训链 `_wheels\_t2_train_verify.ps1`（跳过已完成的 augment）后台运行 pwsh-23，完成后跑 `_t2_verify_onnx.py 40`。
- 教训：带"样本筛选 + 类别权重 ramp"的训练配方在负样本易压制的数据集上会塌缩为常数输出；验收必须包含"静音/噪声输入分数应≈0"的健全性检查（已写入 `_diag_onnx.py`）。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-022 lr=1e-4 振荡+直流漂移 → 全输入饱和常数 1（修复中，重训 pwsh-1）

- 时间：2026-10-15-18-1x（chain #2 verify FAIL），当日晚间完成全面再诊断
- 状态：根因已定位，修复已实施（seq1 lr 0.0001→1e-5），重训+验收运行中（pwsh-1）
- 影响：HB-021 修复（禁挖掘、负权重=1、INFO 日志）后重训仍塌缩——`_t2_verify_result.txt` pos/neg 均 1.000/1.000，全阈值 FAIL，T2 ONNX 不可用。
- 现象：chain #2（pwsh-23）"正常完成"并导出 ONNX（opset 18），验收依旧恒定 ≈1.0；`_t2_train.log` 打印 "Final Model Accuracy: 0.676 / Recall: 0.637"，看似"有区分度"，实为假象。
- 尝试/排除：
  1. 疑 ONNX 导出 → `_diag_onnx2.py`：图结构正确（Reshape→Gemm→LayerNorm(eps=1e-5)→ReLU×2 块→Gemm→Sigmoid），`last_layer.weight` L2=1.97、**`last_layer.bias`=0.0666**（此前"+7.4 偏置"结论系误判——那是 `w·h+b` 总和而非偏置单项）→ 权重正常；
  2. `_diag_onnx3.py`：用 ONNX initializers 重建 torch Net，与 ORT 在 zeros/random/pos/neg 上输出**完全一致**（logits +11.75/+12.30/+15.94/+12.51）→ **导出无罪，torch 模型本身已塌缩**；
  3. `_diag_train_mini.py`（复刻 `__main__` 数据配置的插桩迷你训练）：lr=1e-4 下 loss 每 100 步在 0.008↔0.53 间大幅振荡、pos 预测 0.36↔0.98 摆动，同时 relu_1 sum 缓慢直流漂移（51→57 / 3000 步）→ 60k 步累积成全输入饱和；
  4. lr 对照实验（balanced 32p+32n、5000 步）：lr=3e-5 → pos≈0.97/neg≈0.78（漂移仍继续）；**lr=1e-5 → pos≈0.93/neg≈0.64，振荡抑制、无 runaway** → 选定 1e-5。
- 根因：seq1 `lr=0.0001`（`_t2_train_cn.py` auto_train 硬编码）过大；数据侧正负类分布几乎不可分（pos mean 1.8540/std 15.44 vs neg 1.8931/15.50，最大逐维均值差 5.5，唯一可学习线索是帧 13–26 的"短语后尾部上下文"）→ 大 lr 在弱信号上表现为"振荡 + DC 漂移"，最终层对所有输入（含全零）输出 logit +11..+15。
- 附带缺陷：**torchmetrics stateful 指标陷阱**——`self.recall`/`self.accuracy` 在整个训练过程累积、从不清零，merge 后打印的 "Final Model Accuracy/Recall" 是全程累计值，不是最终模型真实验证分（最终模型实际全类 ≈1.0）。
- 方案：① `_t2_train_cn.py` seq1 `lr = 0.0001 → 1e-5`（带 HB-022 注释）；② 重训链 `_wheels\_t2_train_verify.ps1` 后台运行（pwsh-1），完成后自动跑 `_t2_verify_onnx.py 40`。若再 FAIL：数据侧强化——yaml `negative` 改为由 `background\noise`+`background\speech` wav 生成的普通/易负样本特征（当前与 adversarial 同文件、1:2 负偏），adversarial 移出训练集仅作验证；进一步降 lr / 增 steps。
- 教训：① stateful 指标使用前必须 reset，训练日志里的"final model"指标不可信，验收以 clip 级 `_t2_verify_onnx.py` 结果为准；② 类别分布近乎相同（弱判别信号）的数据集对饱和型塌缩的 lr 窗口极窄，全量训练前先用迷你运行标定 lr。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-023 数据侧根因：正负样本同一音色 → 模型学"音色→触发"，v0.2 数据重造（执行中）

- 时间：2026-10-15-20-1x（chain #3 verify FAIL），当夜启动 v0.2 数据方案；2026-10-16 续跑
- 状态：v0.2 数据集构建中（合成 pwsh-5 / 变换 pwsh-6），训练链待数据就绪
- 影响：HB-021/022 修复后第 3 次生产重训仍验收全 FAIL——`_t2_verify_onnx.py` pos/neg 全阈值均 1.000，模型不可用。
- 现象：lr=1e-5 + 禁挖掘 + 负权重=1 的"干净"训练仍饱和；clip 级验收 pos mean≈1.0、neg mean≈1.0。
- 根因（数据分布，非训练动力学）：v0.1 全部 4000 个训练 clip（pos 2000 + neg 2000）都是**同一个 GSV 爱莉希雅音色**——负样本只是"同音色、不含短语的其它句子"。模型最省力的判别面是"爱莉希雅音色→开火"，与内容无关；验收 clip 同为该音色 → pos/neg 全 1.000。`augment_clips`（openwakeword/data.py L558-700）标准增强音移上限 ±3 semitone，不足以制造音色差异。
- 方案（v0.2 数据集，杀掉音色捷径）：
  1. 正样本 2000 = 1000 干净（v0.1 positive_train 后 1000）+ 1000 强变换（前 1000），**正负两类共享同一变换分布**，变换状态不携带类别信息，内容成为唯一可分线索；
  2. 负样本 2000 = 1550 强变换他人语音（GSV 合成 1700 条不含短语的新句子 `_t2_synth_neg.py` → 强变换）+ 450 噪声/静音；
  3. 负测试 400 = 150 干净对抗样本（v0.1 negative_train 前 150，**含短语、同音色**——内容判别探针）+ 150 强变换他人语音 + 100 噪声/静音；正测试 400 干净不变；
  4. 强变换（`_t2_transform_v02.py`，scipy 纯本地）：音移 ±4–10 semitone + 时域拉伸 0.78–1.28（长度还原）+ 随机低/高/带通（2 阶 butter, p=0.65）+ 彩色噪声 SNR 8–20dB (p=0.5) + 峰值归一 0.9。标准增强（±3 st）之后仍保留音色差异。
- 附带发现：① DSH 沙箱禁命名管道 → `concurrent.futures.ProcessPoolExecutor` 不可用，变换改单进程顺序执行（~20 min 可接受）；② GSV :9880 与 Jarvis :7860 在会话间隙均掉线，需重启；③ venv 缺 `pooch`（librosa 依赖）且无网不可装 → 变换管线弃用 librosa，纯 scipy 实现。
- 验收门槛不变：`_t2_verify_onnx.py 40 aili_xiya_v0.2` PASS = recall≥0.9 AND false≤0.1（阈值 0.4–0.8）。若 150 条干净对抗探针仍误触，说明模型仍依赖音色/变换状态 → 需 v0.3。
- 教训：唤醒词数据的负样本必须覆盖**部署分布**（同说话人、同 TTS 音色、含短语的其它句子），仅"不同文本的同音色负样本"会让模型学到音色捷径；验收集必须包含干净对抗样本作内容判别探针。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-024（已解决）
- 时间：2026-10-16 16:2x
- 状态：已解决（FFT 基粉噪替换，受影响 clip 全部清除重生成）
- 影响：`_t2_transform_v02.py` 的 Kellet IIR 粉红噪声在 float32/float64 均溢出 inf（`overflow encountered in square` / `invalid value in cast`），v0.2 已写入的 posx/noise clip 部分损坏，两次变换作业作废。
- 现象：lfilter(Kellet b,a,white) 输出出现 inf；48k 样本即触发（float64）。
- 根因：经典 Kellet 粉噪 IIR 滤波器极点半径 |z|≈1.0074，长信号指数增长超过 float64 上限（~1e308）→ 溢出 inf → 下游 rms/peak-norm NaN → int16 cast 损坏。
- 方案：`_pink_noise` 改 FFT 基 1/f 谱整形（rfft × 1/√f × irfft），任意长度稳定；sanity 48k 样本全有限、RMS=0.5。b/a 系数弃用。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-025 `make_texts(1700)` 死循环：句池 1075 < 1700，合成作业静默空转（已解决）
- 时间：2026-10-16 17:0x 发现，17:5x 解决
- 状态：已解决（列表 10→20 项扩容 + 确定性全池构建，池 3935 ≥ 1700；pwsh-63 重启后 ~4 s/clip 正常写盘）
- 影响：`_t2_synth_neg.py` 多个作业（pwsh-43/49/50/52/61）启动打印 "GSV ready" 后静默、worker python 满核空转、`neg_src` 零文件；GSV 服务器与逐 clip 管线本身健康（前台实测 5.7–14 s/clip）。
- 现象：后台作业日志仅一行 ready；neg_src >5 min 0 文件；Get-Process 显示 worker CPU 时间持续攀升；_gsv.log 无对应新 /tts 请求。
- 尝试：排除 GSV 排队（前台新探针 5.7 s）、文件写权限（transform 作业同目录正常写入）、脚本后处理代码（前台复刻全管线均快）→ 定位到循环前 `make_texts`。
- 根因：旧版 `make_texts` 拒绝采样 while 循环；唯一句池 = 9×双槽模板×100 + 16×单槽模板×10 + 15 固定句 = 1075 < 1700，池耗尽后永远凑不齐 → 死循环。且上一会话的修复 edit 因 run_code 程序 TS 解析失败**从未落盘**（磁盘文件仍是旧版），导致多次重启全部照转。
- 方案：① PEOPLE/PLACES/FOODS/TIMES 各 10→20 项；② `make_texts` 改确定性全池构建（按占位符键 itertools.product、去重 + assert 池≥n + shuffle + 切片）——每次运行同 1700 句，保持按文件名断点续传；③ 杀光空转作业后重启（pwsh-63），~4 s/clip，1700 条 ETA ≈ 2 h。
- 教训：① "后台作业静默 + 满核空转"先查脚本 I/O 前的循环是否死循环（拒绝采样必须池≥目标数，优先确定性构建）；② edit 失败后必须重读文件确认落盘再重启长作业；③ `import module; f(n)` 探针本身会卡在同一 bug 上，需结合进程状态交叉定位。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-026 v0.2 train_config 引用 val_fp.npy 但未生成，训练秒挂（已解决）
- 时间：2026-10-16 19:58 发现，20:0x 解决
- 状态：已解决（`_t2_make_val_fp_v02.py` 按 v0.1 同配方为 v0.2 目录补生成 val_fp.npy；pwsh-142 exit 0）
- 影响：pwsh-136 训练链 augment PASS 后 train 阶段 `FileNotFoundError: ...\aili_xiya_v0.2\val_fp.npy`（_t2_train_cn.py L1097）秒挂，verify 未执行。
- 现象：`[chain-v02] train FAILED (exit 1)`；四特征 .npy 均已落盘，仅 val_fp 缺失。
- 根因：v0.1 的 `val_fp.npy`（5 分钟背景混音 AudioFeatures）由 `_make_background.py` 一次性写入 `output/aili_xiya_v0.1/`；v0.2 train_config.yaml 把 `false_positive_validation_data_path` 改指 v0.2 目录，但该文件从未为 v0.2 生成。
- 方案：新增 `_t2_make_val_fp_v02.py`（同 source dirs、同 seed=3、同 5 min 配方），输出 `openWakeWord/output/aili_xiya_v0.2/val_fp.npy`；随后重启 `_wheels\_t2_train_verify_v02.ps1`（augment 重跑 ~10 min 可接受）。
- 教训：换 model_name/输出目录时，config 引用的**全部**产物文件（特征 npy、val_fp、checkpoint 路径）都要在新目录就位或重生成；train_config 字段逐一核对后再启长训练。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-027 v0.2 verify FAIL：~1150 epoch 记忆化 + 训练/推理特征管线不一致（修复中）
- 时间：2026-10-16 21:0x 发现，修复已启动
- 状态：根因已定位；修复执行中——流式滑窗重算全部特征（pwsh-152），随后 steps=2500 重训 + verify
- 影响：`_t2_verify_onnx.py 40 aili_xiya_v0.2`（pwsh-144）全阈值 FAIL——80 条测试 clip 经 Model.predict_clip 打分全部 ≈1.000；v0.2 ONNX 不可用，config.yaml wake_word.model 未改动。
- 现象：pos/neg max_score 在 0.4–0.8 全阈值均 ≈1.000；训练"正常完成"（60000+6000+6000 步、ONNX 导出 OK）。
- 尝试/排除：
  1. `_probe_rows.py`：已存特征 npy 行过 ONNX——train 行 pos→1.0000 / neg→~8e-6（模型背下了训练行），test 行混沌（pos_test 行100→0.0；neg_test 行0→0.978，且用 BATCH 特征喂入同样高）；
  2. `_t2_exp_stream_vs_batch.py`：batch vs streaming 特征对照——saved neg row0=0.9778615（BATCH 特征下仍高）→ **记忆化为主因**，流式/批量失配为次因；
  3. auto_train 序列分析：3 段 = steps + steps/10 + steps/10 = 72k 有效步 × batch 64 ≈ 4.6M 样本 / 4000 行 ≈ **~1150 epoch**；
  4. 部署管线确认：`Model(wakeword_models=[onnx])` → tflite 缺省回退 onnx → `AudioFeatures(inference_framework="onnx", ncpu=1)`；`predict_clip` 两端各补 1 s 零、1280 样本/块流式、每块取最近 24 帧窗打分、初始化前 5 帧强制 0——训练特征（batch `embed_clips`，整 clip melspec）与其分布无交集。
- 根因：① ~1150 epoch 过拟合背下全部 4000 行训练特征（train recall→1、train neg→~0），OOD 流式输入 logit 饱和 ≈1.0；② 次因：训练特征由 batch `embed_clips` 计算 ≠ 推理侧 `predict_clip` 流式特征，模型从没见过部署形态的输入。
- 方案（修复）：
  1. `_t2_stream_features_v02.py`：按部署同管线重算四个特征 npy——`AudioFeatures(inference_framework="onnx", ncpu=1)`，逐 clip 前后各 1 s 零、1280 样本/块流式、warmup 后滑动 24 帧窗；pos clip 仅保留与有声段重叠 ≥12/24 帧的窗（80 ms RMS 门限、±2 帧裕量；无有声段时仅留中央窗）；neg clip 全部窗；val_fp.npy 用同 seed-3 配方流式重生成（保持 120 帧上限）。预计总行数 ~26k → epoch ≈ 400 步（batch 64）。
  2. `train_config.yaml` `steps: 60000→2500`（总 3000 步 ≈7–8 epoch）打破记忆化；seq1 warmup/hold/cosine 结构不变。
  3. 重训仅 `--train_model`（直接消费替换后的 npy，不重 augment），随后 `_t2_verify_onnx.py 40 aili_xiya_v0.2`。
- 若 verify 仍 FAIL（尤其 150 条 negadv_te_* 干净对抗探针）→ v0.3 数据侧方案（HB-023 音色捷径），不做 lr 调参；边界情况则试 steps {4000, 6000} 网格，每候选存 ONNX 副本。
- 教训：① 唤醒词训练预算必须按 epoch 标定（rows / (batch × 总步数)）——为 ~1k 行特征写的 steps 在特征文件涨到 ~26k 行后会变成上千 epoch；② 训练/推理特征管线必须位级一致（同 padding、同流式 AudioFeatures），严禁 batch `embed_clips` 训练特征对 streaming 部署打分。
- 关联需求：records/2026-10-13-21-38-01.md
- 状态更新（2026-10-16-21:3x）：首次流式重算 pwsh-152 暴露第一版脚本的帧率映射 bug——假设 1 特征帧/1280 样本块，实测本 venv AudioFeatures ≈ 1 帧/~730 样本（~22 Hz，24 帧窗 ≈ 330 ms）。后果：pos 有声段被映射到 n_start=53 之前 → 全部跳过（pos_train 仅产出 2 行）；neg 每 clip ~680 个滑动窗（总计 ~2.7M 行，不可行）。已杀 pwsh-152。窗口选择改写为 chunk-boundary last-24 帧窗（与 `Model.predict` 的 ==1280 分支逐位一致）+ 每 clip 实测 samples/frame 映射有声段 + 每 clip ≤12 窗等距截取；5+5 clip 冒烟 PASS（pos/neg 均 12 窗/clip，M≈84–120 帧，spf≈660–915）。以 pwsh-154 重启，预计总行数 ≈57.6k → batch 64 下 epoch ≈900 步 → 3000 步 ≈3.3 epoch。

- 状态更新（2026-10-16-22:4x）：pwsh-154 流式特征重算完成（四集 57600 行 + val_fp，skipped=0）；pwsh-156 以 steps=2500 重训导出新 ONNX；`_t2_verify_onnx.py 40 aili_xiya_v0.2`（pwsh-159）**仍 FAIL**——pos mean/max 0.946/0.955，neg(mean) 0.920/0.955，阈值 0.4–0.8 全不满足（recall≥0.9 且 false≤0.1）。
- 诊断（`_t2_diag_v02b.py`，pwsh-162）：onnxruntime 直接打分——neg_train 行 0.04–0.09、静音窗 0.03、negx_te 0.26–0.71（模型**已学会类分离**），但 **negadv_te（150 条干净对抗句）全部 ≈0.93–0.95 ≈ pos**。`_t2_transform_v02.py` L178-184 证实：negadv_te = v0.1 negative_train 前 150 条**干净未变换**副本，v0.2 训练负例（1550 negx 强变换 + 450 噪声）零条含短语 → 模型从未见过干净对抗分布。结论：**数据侧缺口，非 lr/步数问题**。
- v0.3 方案（执行中）：v0.1 负样本池共 2000 条干净对抗句；取 [150:950] 共 800 条（与测试留出 [0:150] 不相交）加入 negative_train（2000→2800 clip，33600 行），其余集合不变；特征复用 pwsh-154 产物 + 仅新 800 条重算流式窗（9600 行）；steps=2500（总 3000 ≈2.9 epoch）重训，`_t2_verify_onnx.py 400` 全测试集验收。
- 状态（2026-10-17-11:2x）：pwsh-8 训练完成（ONNX 导出成功；期间发现训练脚本 L1105/1106 读旧命名 `positive/negative_features_test.npy`，v0.3 目录已用正确 4800 行文件补齐）。`_t2_verify_onnx.py 400` **FAIL**——pos mean/max 0.785/0.901（51 条 <0.7），negadv_te mean 0.504（32% ≥0.6，max 0.837）= 主要误报源；negx_te 0.210、noise_te 0.139 均健康。无阈值满足 recall≥0.9 且 false≤0.1（0.6: 0.95/0.13；0.7: 0.87/0.05）。模型已学会干净对抗分布（negadv 0.94→0.50），但正负两侧边距均偏薄。**v0.3b 方案**：v0.1 池剩余 [950:2000] 共 1050 条干净对抗句加入 negative_train（行 33600→46200）→ steps=3000（≈2.7 epoch）重训 → verify `400`。不做 lr 调参。
- v0.3b 结果（2026-10-17-11:4x）：**FAIL**。pos 0.785→**0.844**（recall@0.7 = 0.98，正侧显著改善），但全部负类均匀上移：negadv_te 0.504→0.649、negx_te 0.210→0.403、noise_te 0.139→0.333；fp@0.7 = 0.16（超 0.1）。诊断：neg_src 全部为 GSV-Elysia 同音色（`_t2_synth_neg.py` L1-7 明示"唯一差异是内容"），加同音色数据使模型对 Elysia 语音的**基线敏感度整体增强**，而非细化音素边界 → 阈值 0.7 recall 0.98 / fp 0.16，仍无合格阈值（0.8: 0.88/0.04）。
- **v0.3c 方案**：抑制同音色基线响应——+500 条新 Elysia 句子（neg_src 池 [1700:2200]，确定性模板扩展，与既有 1700 条不相交）强变换 → `negx2_tr_*`；+450 条噪声/静音（seed 71000+，不与 70000/80000 段冲突）→ `noise2_tr_*`；特征 46200→~57600 → steps=3000（≈2.36 epoch）重训 → verify `400`。保留 v0.3b 的 negadv 1850 条（其 phonetic 对比是 pos recall 提升的来源）。
- 状态（2026-10-17-15:5x）：**v0.3c PASS**。数据 pwsh-28（500 新句合成，含两次会话间隙续传）→ 特征 46200→**57600** 行（pwsh-5）→ steps=3000 重训 ONNX 导出（pwsh-6）→ `_t2_verify_onnx.py 400`（pwsh-7）**PASS @ threshold 0.7：recall 0.94 / fp 0.09**（0.6: 0.97/0.20；0.8: 0.67/0.01）。pos mean 0.807/max 0.888（v0.3b 0.844 → 微降可接受）；neg 全体回落（mean 0.453 / max 0.833，negadv_te、negx_te、noise_te 三集同步下降）——新内容 + 噪声抑制同音色基线，且未侵蚀 negadv 带来的 pos-recall 收益。v0.3c ONNX 已接入 `config.yaml wake_word.model`（threshold 0.5→0.7），Jarvis 重启生效。**HB-027 已解决**。

## HB-028 特征 npy 命名不一致：v0.2b 训练静默消费 2000 行陈旧损坏文件（已修复）
- 时间：2026-10-17-11:0x 发现（v0.3 staging 时）
- 状态：已修复——v0.2 目录 4 个陈旧文件移入 `aili_xiya_v0.2/_stale_npy/`；v0.3 特征按正确源重建
- 影响：pwsh-156“v0.2b”重训实际只加载了 2000+2000 行陈旧特征（非 24000+24000），等效 ~48 epoch 记忆化训练 → 该 ONNX 无效（与 HB-027 v0.2b FAIL 诊断叠加）。
- 现象：`_t2_stream_features_v02.py`（pwsh-154）写入 `<set>_features_<split>.npy`（如 `positive_train_features_train.npy`，24000 行，10:00/10:13），而 `_t2_train_cn.py` L1049-1050 与 train_config `feature_data_files` 引用 openWakeWord 标准名 `positive_features_train.npy` / `negative_features_train.npy`——目录里恰好存在同名**旧文件**（7:49/7:55，仅 2000 行，系更早被杀运行的部分写入），训练静默消费了它们。
- 根因：两套命名并存且旧文件未清理；训练脚本对特征文件“存在即信任”，无行数/时间戳校验。
- 方案：① v0.2 目录 4 个陈旧 npy（positive/negative × train/test）移入 `_stale_npy/` 隔离；② v0.3 `positive_features_train.npy` ← `positive_train_features_train.npy`（24000 行），`negative_features_train.npy` = 24000 + 9600 新 negadv 行（33600）；测试集 npy 两命名同形不受影响。
- 教训：换特征文件后、启长训练前，必须核对**训练实际加载的文件名与行数**（print np.load(...).shape 或读 _t2_train_cn.py 的加载日志），不能只看“目录里有 npy”。
- 关联需求：records/2026-10-13-21-38-01.md

## HB-029 STT 模型加载失败：HF_ENDPOINT 缺协议前缀（已解决）
- 时间：2026-10-17-15:5x 发现，当日解决
- 状态：已解决（启动环境修正，非代码缺陷）
- 影响：Jarvis 重启（pwsh-9）后首次语音转录失败——`WhisperModel("small")` cuda/cpu 两次加载均抛 `Request URL is missing an 'http://' or 'https://' protocol.`，e2e 语音链中断。
- 现象：模型已完整缓存于 `.hf-cache/hub/models--Systran--faster-whisper-small`（snapshot 536b0662…），加载仍触发在线 etag 检查并失败；日志 `[STT] cuda failed to load (...) → CPU transcription also failed`。
- 根因：启动 env `HF_ENDPOINT=hf-mirror.com` **无 `https://` 前缀**——huggingface_hub 以该值拼接请求 URL，requests 对无 scheme URL 直接抛错。此前会话 STT 正常系模型加载发生在网络/缓存状态不同的时点（etag 命中本地缓存未触发该代码路径）。
- 验证：独立进程 `HF_ENDPOINT=https://hf-mirror.com` + 同 HF_HOME → `WHISPER_LOAD_OK`（exit 0）；旧值必现失败。
- 方案：Jarvis 启动 env 一律 `HF_ENDPOINT=https://hf-mirror.com`（带 scheme）。pwsh-10 以修正 env 重启。
- 教训：HF_ENDPOINT 必须含完整 scheme；服务重启后首次语音交互应作为冒烟检查项。
- 关联需求：records/2026-10-13-21-38-01.md
