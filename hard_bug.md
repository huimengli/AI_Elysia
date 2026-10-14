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
