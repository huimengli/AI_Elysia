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
