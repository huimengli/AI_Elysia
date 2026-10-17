# Progress — 跨会话进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-10-15-13-49-00.md -->

## 归档摘要（已完成需求，详见备份全文）

- **2026-10-12**（records/2026-10-12-12-28-30.md）："将 Jarvis 项目跑起来"：.venv、config llamacpp active、依赖（清华镜像）、openWakeWord ONNX ×9、espeak-ng 数据目录、spacy wheel；HB-001/003/004。
- **2026-10-13 上午**：运行需求完成（e2e CHAT_OK）；Q1 归档。
- **2026-10-13 下午至深夜**（records/2026-10-13-11-45.md、11-55.md）："接入 GPT-SoVITS 2.0 爱莉希雅 TTS"完成：venv 分批安装、jieba shim、torchaudio/langsegmenter 补丁、api_v2 :9880 冒烟 PASS、`tts.provider: gptsovits`、e2e 验证；HB-005..HB-013 全部解决；Q2/Q3/Q4 done 并归档。

## 2026-10-13 深夜至 2026-10-15（爱莉希雅化 + 自训唤醒词，records/2026-10-13-21-38-01.md）

- 需求（6 项）：T1 自称"爱莉希雅" / T2 openwakeword-train 自训唤醒词 / T3 先落盘 / T4 仓库私有或描述改"自用" / T5 强制中文 / T6 网页 UI 爱莉希雅化（仅记 todo）。
- **T1/T5 完成并 e2e PASS**（34.7s，自称 ✓ 简体中文 ✓）：系统提示词、启动问候、停止命令、Windows 通知、web.py 中文化；HB-014（stream 死连接阻塞：120s 超时 + 工具循环 3 轮 + max_tokens 512）、HB-015（测试脚本假阴性）已解决。
- T2 训练链全部去风险：依赖装齐（urllib+wheel 本地安装模式）；`openWakeWord/generate_samples.py` GSV shim（断点续传）；`_t2_train_cn.py`（CJK 对抗句池 + torchaudio shim / 串行 ThreadPool / memmap finalize / num_workers=0 / onnx 依赖 / tflite best-effort / export 子目录修正）；验收脚本 `_t2_verify_onnx.py`（positive_test + negative_test，阈值矩阵 0.4–0.8）。
- 2026-10-14 22:2x 新需求：TTS 迁移 SoulX-Podcast（**仅记 todo，不做**）→ records/2026-10-14-22-23-49.md。
- **2026-10-15 13:3x 夜间关机中断**：pwsh-103（生成）与 pwsh-42（GSV :9880）被杀；落盘 2000/400/2000/217。恢复：GSV 重启（pwsh-3）→ `--generate_clips` 续跑（pwsh-5）→ Jarvis 重启（pwsh-7，HF 三 env）；llama.cpp :8080 未受影响。
- **2026-10-15 13:4x 生成完成**：四目录 **2000/400/2000/400 = 4800 条**（目标 = n_samples/n_samples_val；此前"negative_test 2400"为误记，已修正）。
- **2026-10-15 13:5x–16:3x T2 训练链排障**：augment PASS（四特征 .npy + val_fp）；train 分支连修 **HB-017/018/019/020**（prefetch_factor、n_per_class dict、data_transforms 行序 + n=16 硬编码、`total_length//16000` 截断 + 不持久化漂移 → `input_shape` 改从 .npy shape 读取）；冒烟 #4 PASS（120 步全链路含验证与 ONNX 导出，verify 框架实测可用，冒烟模型 FAIL 属预期）。
- **2026-10-15 17:0x 正式训练完成但验收 FAIL → HB-021**：pwsh-12 跑完 60000+6000+6000 步并导出 ONNX，verify FAIL——模型对静音/噪声/pos/neg **恒定输出 ≈0.999**（最终层偏置≈+7.4 饱和）。根因：高损失样本挖掘 + 负权重 ramp(1→1000) → 负样本退出 batch 后数万步纯正样本训练。修复已实施：禁用高损失挖掘、`max_negative_weight: 1`、补 `logging.basicConfig(INFO)`。**重训中**（pwsh-23：`_wheels\_t2_train_verify.ps1` = train→verify）。服务齐备：llama :8080（pwsh-1）、Jarvis :7860（pwsh-3）、GSV :9880（pwsh-8）。**config.yaml 暂不指向新 ONNX**；verify PASS 后再改指 → 重启服务器 + e2e 复验。
- **2026-10-15 晚间 chain #2 FAIL → HB-022**：pwsh-23 重训"正常完成"但验收再次恒定 1.0（pos/neg 均 1.000）。全面再诊断：ONNX 导出无罪（`_diag_onnx2`：图/权重正常、最终 bias=0.0666，此前"+7.4"系 w·h+b 总和误判；`_diag_onnx3`：用 ONNX 权重重建 torch ≡ ORT 输出）→ **根因 = seq1 `lr=0.0001` 过大**，正负类分布几乎不可分（mean 1.854/1.893、std≈15.5）下训练呈"振荡 + DC 漂移"、全输入饱和；日志 "Final Recall 0.637" 系 torchmetrics stateful 指标全程累计值，非最终模型真实分。迷你运行对照（balanced 32:32、5k 步）：lr=1e-5 → pos≈0.93/neg≈0.64、振荡抑制。**修复已实施**：seq1 lr 0.0001→1e-5，重训链运行中（pwsh-1）。若再 FAIL：数据侧强化（background noise/speech wav 生成普通负样本、adversarial 移训练集外仅验证）。
- **2026-10-15 21:0x 新增 DSH Agent 预设**（records/2026-10-15-21-05-48.md）：PTC-MY / 创造模式-MY，与工作区 bundle `dsh-my-presets` 一并落盘；插件列表逐字复制内置 ptc/cordis，仅 compaction-basic 参数自定义（0.8/16348/0.16）。旧 profile patch 的 id-覆盖行无法创建新预设（Loader 跳过），已改 bundle `insert:` 方案，install_bundle 成功、两行 active。
- **2026-10-15 20:1x–22:0x chain #3 FAIL → HB-023（数据侧根因）+ v0.2 方案**：pwsh-1 完成 60000 步（lr=1e-5）导出 ONNX，verify 仍 pos/neg 全 1.000。根因 = v0.1 全部 4000 训练 clip 同一 GSV 爱莉希雅音色 → 模型学"音色→触发"；标准增强音移上限 ±3 st 不足以破捷径。v0.2：正负共享同一强变换分布（音移 ±4–10 st + 时域拉伸 + 滤波 + 彩色噪声），内容成为唯一可分线索；负测试含 150 干净对抗探针（含短语同音色）。工具 `_t2_synth_neg.py` / `_t2_transform_v02.py`；验收 `40 aili_xiya_v0.2`。
- **2026-10-16 16:0x v0.2 构建续跑**：会话间隙 GSV :9880、Jarvis :7860 掉线 → 重启（pwsh-4）+ 合成续跑（pwsh-5，自带就绪等待）+ 顺序变换（pwsh-6）。沙箱禁命名管道 → `ProcessPoolExecutor` 弃用改单进程；venv 缺 pooch 且无网 → 变换纯 scipy。train_config.yaml 已切 v0.2（model_name + negative 特征路径 + val_fp）；训练链 `_wheels\_t2_train_verify_v02.ps1`（augment→train 60000→verify）待数据齐后启动（预计 ~4 h CPU）。**config.yaml 仍不指向新 ONNX**。
- **2026-10-16 17:5x HB-025 定位并解决**：`_t2_synth_neg.py` 多个作业"ready 后静默、零文件、满核空转"——根因 = 旧版 `make_texts(1700)` 拒绝采样死循环（句池 1075 < 1700），且上一会话的修复 edit 因程序解析失败从未落盘。修复：四个词表 10→20 项 + make_texts 确定性全池构建（3935，seed=42 可断点续传）；重启合成 **pwsh-63**（~4 s/clip，ETA ≈ 2 h），变换 **pwsh-13** 随 neg_src 自动消费。当前落盘 2000/400/497/250 + neg_src 增长中。
- 进行中/待办：T2 = v0.2 数据构建中（neg 合成 pwsh-63 → 变换 pwsh-13 自动补齐 2000/400/2000/400 → 启训练链）→ verify PASS 才改 config.yaml + e2e；T4 待用户手动 GitHub 操作（need_user.md Q5）；T6 仅 todo。
- **2026-10-16 19:3x v0.2 数据齐**：neg_src 1700/1700（pwsh-63 exit 0）+ 强变换消费齐（pwsh-13 exit 0）→ **2000/400/2000/400 = 4800 条**（negx_tr 1550 + noise_tr 450；negadv_te 150 + negx_te 150 + noise_te 100）。**19:4x 训练链 pwsh-136**：augment PASS 后 train 秒挂（HB-026：v0.2 目录缺 `val_fp.npy`，config 引用了但未生成）→ 20:0x `_t2_make_val_fp_v02.py` 补生成（(120,96) float32，45.1KB，pwsh-142 exit 0）→ **20:0x 重启训练链 pwsh-144**：`_wheels\_t2_train_verify_v02.ps1`（augment→train 60000→verify `40 aili_xiya_v0.2`，CPU ~3.5–4 h；日志 `_t2_augment_v02.log`/`_t2_train_v02.log`/`_t2_verify_v02.log`）。**config.yaml 仍不指向新 ONNX**：verify PASS（recall≥0.9 且 false≤0.1，阈值 0.4–0.8）才改 wake_word.model → 重启 e2e → records/progress/todo 更新 + 本地 commit；若 FAIL（尤其 150 negadv_te_* 内容探针）→ v0.3 数据侧方案（HB-023 音色捷径），不做 lr 调参。
- **2026-10-16 21:0x v0.2 训练链完成、验收 FAIL → HB-027**：pwsh-144 全链约半小时（augment→train 72000 步→verify，远低于预估 3.5–4 h），80 条测试 clip 经 predict_clip 打分全 ≈1.000、全阈值 FAIL。根因 = ~1150 epoch 记忆化 + 训练/推理特征管线不一致（batch embed_clips vs streaming predict_clip）。修复执行中：① `_t2_stream_features_v02.py` 流式滑窗重算全部特征（**pwsh-152**，ETA 1–2.5 h，日志 `_t2_streamfeat_v02.log`）；② train_config `steps: 60000→2500`（总 3000 步 ≈7–8 epoch）；③ 重训 `--train_model` → verify `40 aili_xiya_v0.2`。**config.yaml 仍不指向新 ONNX**。
- **2026-10-17 11:0x v0.2b FAIL 定因 + HB-028 + v0.3 执行中**：pwsh-154 流式特征重算完成（57600 行）→ pwsh-156 steps=2500 重训 → verify `40` **FAIL**（pos 0.946 vs negadv_te ≈0.92–0.95；`_t2_diag_v02b.py` 证明模型已学会类分离，negadv_te = v0.1 干净对抗句、v0.2 训练从未见过 → **数据侧缺口**）。另发现 **HB-028**：`_t2_stream_features_v02.py` 写 `<set>_features_<split>.npy`（24000 行），而 `_t2_train_cn.py` 读标准名 `positive/negative_features_train.npy`——目录里同名的 7:49/7:55 陈旧 2000 行损坏文件被训练静默消费，v0.2b ONNX 实际只学 4000 行 → 无效。已修复：4 个陈旧 npy 移入 `aili_xiya_v0.2/_stale_npy/`；v0.3 = v0.2 + 800 条干净对抗句（v0.1 池 [150:950]，与测试留出 [0:150] 不相交）→ negative_train 33600 行（新 800 条流式窗 9600 行，skipped=0）→ 重训 pwsh-8 完成（期间补 v0.3 目录旧命名 test npy，训练脚本 L1105/1106 需要）→ verify `400` **FAIL**（pos 0.785/0.901，negadv_te 0.504 为主要误报源：32% ≥0.6；无阈值同时满足 recall≥0.9 且 false≤0.1）→ v0.3b（+1050 对抗句，特征 46200）→ verify `400` **FAIL**：pos 0.844（recall@0.7=0.98）但全部负类均匀上移（negadv_te 0.649 / negx_te 0.403 / noise_te 0.333，fp@0.7=0.16）——同音色基线敏感度增强。**v0.3c 执行中**（2026-10-17-11:5x）：+500 条新 Elysia 句子强变换（negx2_tr）+450 噪声（noise2_tr）→ 特征 ~57600 → steps=3000 重训 → verify `400`。**config.yaml 仍不指向新 ONNX**。12:0x 发现会话间隙 GSV :9880 与 Jarvis :7860 再次掉线（首次合成即连拒，0 条落盘）→ GSV 重启（pwsh-20）、Jarvis 重启（pwsh-21，含 3 HF env）、v0.3c 数据续跑（pwsh-22，内置 :9880 就绪探测；首次探测误把 404 当未就绪，已修复为"任意 HTTP 应答即就绪"→ pwsh-28）。15:0x 会话间隙 ~2h：pwsh-27/28 被杀，落盘 neg_src 新句 **188/500**（可续传）→ GSV/Jarvis/数据再次重启（pwsh-2/3/4）。**v0.3c PASS**（15:5x）：数据 pwsh-28（500 新句合成 + 500 negx2_tr + 450 noise2_tr）→ 特征 **57600** 行（pwsh-5）→ steps=3000 重训 ONNX（pwsh-6）→ verify `400`（pwsh-7）**PASS @ 阈值 0.7：recall 0.94 / fp 0.09**；pos mean 0.807，neg 三集同步回落（mean 0.453）。`config.yaml wake_word.model` 已接入 `openWakeWord/output/aili_xiya_v0.3/aili_xiya_v0.3.onnx` + threshold 0.5→0.7，Jarvis 重启加载验证 OK（pwsh-9，期间发现并修复 **HB-029**：HF_ENDPOINT 缺 `https://` 前缀致 STT 加载失败 → pwsh-10 修正 env 重启）。**HB-027 已解决**。

## Git 提交记录

- `7d279a7`（2026-10-13-10:4x，main）`docs(AI): 补全 Jarvis 运行记录并归档 Q1（端到端 CHAT_OK）`。**已本地 commit，未 push。**
- `f444b85`（2026-10-13-12:5x，main）`feat(AI): 新增 gptsovits TTS provider 并关闭 Qwen3 thinking 解决 LLM 挂起`。**已本地 commit，未 push。**
- `409cc3f`（2026-10-13-14:5x，main）`docs(AI): sync GPT-SoVITS venv retry, e2e PASS, and user asks`。**已本地 commit，未 push。**
- `f4e1b48`（2026-10-13-18:1x，main）`fix(AI): repair config.yaml escape/encoding, pin chroma embedding to workspace, close Q2/Q3`。**已本地 commit，未 push。**
- `e9b90f0`（2026-10-13-20:1x，main）`fix(AI): gptsovits provider live + GPT-SoVITS runtime patches, TTS verified`。**已本地 commit，未 push。**
- `6b1b545`（2026-10-13-21:3x，main）`fix(AI): merge memory facts into single system message; UTF-8 console hardening`。**已本地 commit，未 push。**
- `a15c1ab`（2026-10-14-22:1x，main）`feat(AI): 爱莉希雅 self-reference + forced Chinese, HB-014 stream stall guard, e2e PASS`。**已本地 commit，未 push。**
- `c63c8ef`（2026-10-14-22:18，main）`docs(AI): record commit a15c1ab in ledger; rebuild tree snapshot`。**已本地 commit，未 push。**
- `d8567cb`（2026-10-14-22:27，main）`docs(AI): record TTS migration request to SoulX-Podcast (todo only, not started)`。**已本地 commit，未 push。**
- `30eba61`（2026-10-14-22:41，main）`docs(AI): T2 pre-training audit — tflite conversion best-effort, generation at 900/2000`。**已本地 commit，未 push。**
- `3bb5b7d`（2026-10-14-22:51，main）`feat(AI): wake.py supports local ONNX model paths (prediction key = filename stem); T2 acceptance script ready`。**已本地 commit，未 push。**
- `8a97e4a`（2026-10-14-23:2x，main）`docs(AI): ledger backfill (c63c8ef..3bb5b7d) + T2 augment chain de-risked (3 blockers fixed)`。**已本地 commit，未 push。**
- `8c33f74`（2026-10-16-16:3x，main）`feat(AI): 爱莉希雅自称与中文强制收尾，v0.2 唤醒词数据重建中`。**已本地 commit，未 push。**
- `be4e07c`（2026-10-16-17:1x，main）`docs(AI): HB-024 Kellet IIR 粉噪溢出已解决（FFT 基替换）；todo 作业号更正 pwsh-10/13`。**已本地 commit，未 push。**（台账补记）
- `07bd022`（2026-10-15-16:5x，main）`docs(AI): T2 train-branch HB-017..020 fixes, smoke PASS, production training launched`。**已本地 commit，未 push。**
- `38b1d02`（2026-10-15-21:1x，main）`feat(AI): add DSH agent presets PTC-MY and 创造模式-MY via workspace bundle`。**已本地 commit，未 push。**
- `a390837`（2026-10-17-15:5x，main）`feat(AI): v0.3c 唤醒词验收 PASS 并接入 config.yaml（recall 0.94 / fp 0.09 @ 阈值 0.7）`。**已本地 commit，未 push。**
