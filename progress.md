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
- 进行中/待办：T2 重训验收中（pwsh-1）；T4 待用户手动 GitHub 操作（need_user.md Q5）；T6 仅 todo。

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
- `07bd022`（2026-10-15-16:5x，main）`docs(AI): T2 train-branch HB-017..020 fixes, smoke PASS, production training launched`。**已本地 commit，未 push。**
- `38b1d02`（2026-10-15-21:1x，main）`feat(AI): add DSH agent presets PTC-MY and 创造模式-MY via workspace bundle`。**已本地 commit，未 push。**
