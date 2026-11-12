# Todo

<!-- 已归档于 ai_buckup/todo.md_2026-11-12-19-23-02.md（99 行全量，含 2026-11-10 真人重训练链、2026-11-11 三批、2026-11-12 Q13 清理与 16:58 对比台账的逐条明细）。上一版归档 ai_buckup/todo.md_2026-11-12-16-58-46.md。本文件为压缩版：保留全部未完成项 + 最近批次要点。 -->

## 未完成（等用户 / 需授权 / 延后）

- [ ] 2026-10-13-11-45 三问题排查收尾（剩余：用户对新进程实测唤醒）
- [ ] 2026-10-13-21-38-01 T4 仓库私有化/描述改「自用」（AGENTS §4 禁远程写入，需用户手动，用户确认延后）
- [ ] 2026-10-14-22-23-49 TTS 迁移 SoulX-Podcast（当时要求，**本轮不做**，仅记录）
- [ ] 2026-10-17-19-11-07 README 中文化 + 来源声明 + 仓库更名 AI_Elysia + LICENSE + push（禁 push，需用户操作）
- [ ] 2026-10-17-19-52-00 唤醒词 v0.3 onnx 入库（需用户执行 push）
- [ ] 2026-11-08-12-08-49 `AI_Benchmark.md` 继续补测更多模型（T14 decode 仅 2B/IQ3 已测）
- [ ] 2026-11-08-20-44-17 **20 轮明确测试**未跑完（1 轮已做）；轮 4 barge-in 结论待追加累积 `tests/opinion.md`
- [ ] 2026-11-09-19-45-46 剩余 3 轮验证未跑完（1 轮已做）
- [ ] 2026-11-09-15-37-58 浏览器共用插件**安装/配置**（需用户授权 Chrome `--remote-debugging-port=9222` + Playwright MCP）
- [ ] 2026-11-11-21-36-30（已落盘，**未开工**）：① 「我没听清，请再说一遍」预合成 wav 入内存 ack 池（`tts.ack_phrases`，只在识别失败/空转录时播放，不改 barge-in 语义）② `memory.db` 小表 `hot_phrases(text, kind, count, first_seen, last_seen)`（kind = user/hot/near_miss，≤200 行）③ 热词接 ASR 偏置（whisper `initial_prompt` / sherpa hotwords），与 A/B 一起 3 轮验收。**新参考音频已到位**：`C:\Users\楼听\Documents\录音\'我没听清,请再说一遍'.m4a`
- [ ] **need_user.md Q14（status: wait）**：真人近音件入库规则冲突裁决（推荐「峰值 ≥0.80 的真人近音件移出训练集、只作验收集」）；裁决后重训 v1.0b + 3 轮，达标才换 `config.yaml`
- [ ] 给 sherpa 路径加能量门（VAD/静音跳过），门生效后重跑 A/B 3 轮再定 `stt.engine` 默认
- [ ] 真人补录缺口（`need_audio.md` §5）：**竞品唤醒词真人句补 ≥4 条**（现仅 天猫精灵 1 条）、**无关中文短句补 ≥3 句**（现 7 句，规格 ≥10）

## 已结案批次（压缩，明细见归档与 `tests/`、`records/`）

- **2026-11-10 真人重训练链**（`records/2026-11-10-21-02-16.md`、`22-17-39.md`）：`v0.4` rec 0.50 / `v0.5` **rec 0.00 塌陷** → Q8 重标（13 次全正样本，10xx/12xx 编号）→ `v0.6`（25195 正 / 57696 负行）真人 rec 1.00 / 带噪 0.83 / 纯噪声 0；写死判据仍 FAIL。3 轮 + 阈值扫描已落盘。线上修复：`no_speech_seconds`（默认 2.0）实测 2.1 s 提前退出。
- **2026-11-11-19-45-46 切 v0.6（Q10）**：health 实测生效；轮 2 部署管线 **v0.6 检出 10 vs v0.3 5**；轮 3 现场环境音 0.703 触发 → 0.7 FAIL，0.75 时环境音归零（检出 5）。
- **2026-11-11-20-34-04 六项批量**：TTS 按标点切句队列（首声 14.08→2.44 s、总时长 −27%、打断后 played 0）；新录 7 件 → `v0.7`（近音 ×5，检出 10→5）/ `v0.8`（×5/×3，检出 12、近音 fp 3/3、对抗 6>4）均未采用；ASR `stt.engine` 可切换（sherpa Paraformer-zh small 81.8 MB）+ A/B 3 轮（sim ≥0.8 **whisper 3/6 vs sherpa 2/6**，sherpa 快 10-20× 但无 VAD 幻觉、写不出正字）→ 默认 whisper；Q5/Q6 关闭归档。打分非确定性记 **HB-032**（边界须 ≥3 独立实例）。
- **2026-11-12-10-35-29 第 8 项**：15 件真人负样本入库（13xx）；**TTS 合成负样本判定为无效**（同音色近音词峰值 0.796-0.839 > 真人唤醒整件 0.73-0.75，禁 爱丽西亚/艾丽西亚 类）；`v0.9`（正 ×5 / 新负 ×2）→ **采用 v0.9 + 阈值 0.75**（12 / 近音 fp 6 / 无关 2 / 对抗 4 / 长噪音 1 / 环境 0）；「真人近音 fp ≤1」**未达标**，阻塞于补录。
- **2026-11-12-12-12-28 Q13 清理**：Q13 done + `need_user.md` 归档；新建 `need_audio.md`；71 个 `_*.py` → `training/`（进 Git），49 个 `_*` → `.tmp/`，3 份总结 → `records/`；28 脚本补 `sys.path`；修 pwsh 反引号转义损伤（规矩：含反引号与 CJK 用 write 工具，追加用 `@' ... '@`）。
- **2026-11-12-16-58-46 唤醒 ONNX 全版本对比**：9 个 ONNX（v0.1-v0.9，均 13,735 B）写入 **`ai_buckup/onnx_opinion.md`**（版本谱系 / 3 轮矩阵 / 阈值取舍 / HB-032 / 结论与缺口），未重跑探针。
- **2026-11-12-17-22-40 新补录 14 件验收**：**数据可用**（无过静音；14 次件 v0.9 检出 **14/14** max 0.819、键盘 4 次件 4/4、6 件带噪全命中；真呼唤 13→25 次、带噪 2→12 条）；入库 36 clip（14xx）→ `v1.0`（正 ×5 / 负 ×1，26515 / 58128 行）**Recall 0.3009**（@0.70 真呼唤 10、@0.75 合计 3）→ **未采用**，`config.yaml` 保持 `v0.9 + 0.75`。根因 = 与真唤醒同强度（`米雅` 0.827、键盘噪音 0.816-0.844）的件被标负。脚本入 Git：`training/_t2_newaudio_probe.py`、`_t2_v10_clips.py`（窗口校验条件已修）、`_t2_v10_features.py`。3 轮 + 累积 opinion 已落盘。
- **2026-11-12-18-49-50 多音色 TTS 训练集（→ records/…）**：[x] 音色清点：爱莉希雅参考音频池 50+ 件**全部同音色**；真人录音（文件名即真值 = `prompt_text`）作参考 = 用户本人音色；Kokoro-82M 支持 `lang_code="z"`，本地 `.hf-cache` 已缓存 7 个中文音色（`zf_xiaoxiao/xiaoni/xiaoyi`、`zm_yunyang/yunxi/yunxia/yunjian`）；[x] 修 Kokoro 依赖：`soundfile` 包目录被 sherpa wheel 解包覆盖丢失（`ModuleNotFoundError: _soundfile_data`）→ tuna wheel 直装 0.14.0（含 `libsndfile_x64.dll`）import 正常；`av` 在 Free 7.9 GB 时对 aac `avcodec_open2` 报 `MemoryError`（停 TTS 后 Free 16 GB）。[x] 生成脚本 `training/_t2_v11_tts.py`（6 音色 × 20 文本，16k mono）。
  - [x] 生成 + 逐件打分（v0.9 部署管线 + 3 实例峰值）：正样本 21/21 入库（>=0.70）、负样本仅 13/119 合格（3 实例全 <0.70）；真人音色克隆定案不可用（60 s 失控）
  - [x] 新集编号 **15xx**（34 clip）→ 特征（正 ×5 / 合格负 ×1，并入 **v0.9 基线**）→ `train_config_v11.yaml`（steps 3000）→ **v1.1** Recall 0.6179 + 3 轮矩阵 → **不采用，保持 v0.9 + 0.75**
  - [x] 3 轮落在 `tests/2026-11-12-20-03-41_cc/record_1..3.md` + `opinion.md`（与流萤/白厄合并成一批），累积 `tests/opinion.md` 已追加

## 2026-11-12-19-23-02 流萤音色权重接入（→ records/2026-11-12-19-23-02.md）

- [x] 清点：`F:\BaiduNetdiskDownload\流萤` 是**完整 GPT-SoVITS 包** = `GPT_weights\Firefly-e15.ckpt`（155.1 MB）+ `SoVITS_weights\Firefly_e12_s1404.pth` / `Firefly_e16_s1872.pth`（84.9 MB）+ 9 件参考音频（**文件名即台词 = `prompt_text`**）
- [x] 通路确认：`GPT-SoVITS-main/api_v2.py:555 /set_gpt_weights?weights_path=`、`:567 /set_sovits_weights?weights_path=`（运行时换权重，服务 `:9880` + `.venv-gsv`）
- [x] 生成脚本接入 `firefly` 音色（换权重 → 20 件 → **换回 Elysia 权重**）；参考音频文件名尾部带空格，需 `os.listdir` 前缀匹配（直接拼路径 `not exists`）。真人音色 `user` 定案**不可用**，矩阵为 7 音色（含白厄）
- [x] 打分判定：`firefly` 正 3/3 入库、负 2/17 入库（近音/竞品峰值 0.71-0.84 与真唤醒同量级 → 不入库）；合格件入 15xx，并入 v0.9 基线，v1.1 **不采用**
- [x] 3 轮落 `tests/2026-11-12-20-03-41_cc/record_1..3.md` + `opinion.md`（与 18:49/20:03 合并成一批），累积 `tests/opinion.md` 已追加；commit + hash，禁止 push；`tree.md` 重建

## 通用规矩（长期，勿违反）

- [ ] 每批：先落 `records/` + `todo.md` 再开工；测试 20 轮（明确）/ 3 轮（验证）并写 `tests/opinion.md`
- [ ] 零截图；不用子智能体（未询问）；commit 中文主题 + hash 追加台账 + **禁止 push**
- [ ] `progress.md` / `todo.md` > 100 行先归档再压缩；`tree.md` 文件增删后重建（仅非 `.gitignore`）

## 2026-11-12-20-03-41 白厄（自称 v2ProPlus）权重接入（→ records/2026-11-12-20-03-41.md）

- [x] 清点：`白厄_e10_s680.pth` 172.77 MB（>v2 的 106 MB，与 v2ProPlus 参数量一致）+ `白厄-e10.ckpt` 155.31 MB + 5 件参考音频（文件名即台词）；本机 `TTS.py` 支持 v2ProPlus（`default_configs` 行 353-358、assert 行 429），版本由 `get_sovits_version_from_path_fast` 从权重内容自动判定
- [x] 冒烟通过：首 2 字节 `b"06"` 证实 v2ProPlus；首次失败根因是缺 `GPT_SoVITS/pretrained_models/sv/pretrained_eres2netv2w24s4ep4.ckpt`（v2ProPlus 需 ERes2NetV2，`sv.py:6` 硬编码），从 hf-mirror 补 107,528,697 B 后切换 + 生成 1.06 s 正常，已切回 Elysia 权重
- [x] 20 文本 × 5 参考音频轮换（音色 `bai_e`，第 7 音色）生成完毕，生成后已切回 Elysia 权重
- [x] 打分判据不变：`bai_e` 正 3/3 入库、负 6/17 入库；15xx clip 与其余音色合并（34 件），并入 v0.9 基线特征 → `train_config_v11.yaml` → **v1.1 Recall 0.6179** → 3 轮矩阵 **不采用**（0.75 下 14 次件 12 < 14）
- [x] 3 轮落 `tests/2026-11-12-20-03-41_cc/` + 累积 `tests/opinion.md`；commit 中文主题 + hash，禁止 push

## 2026-11-12-20-47-51 环境音期望值更正（→ records/2026-11-12-20-47-51.md）

- [x] `training/_t2_newaudio_probe.py` 的 `环境音（安静房间）` 期望 1 → **0**（该件无呼唤）
- [x] `tests/2026-11-12-20-03-41_cc/record_2.md`、`record_3.md` 追加更正节（0.70 下 v1.1 环境音 1 次 = BAD，v0.9 = OK）
- [x] 累积 `tests/opinion.md` 追加本批结论（含期望口径更正）

## 2026-11-12-21-40-35 Q14 裁决（选项 1）+ 重训 v1.0b（→ records/2026-11-12-21-40-35.md）

- [x] `need_user.md` Q14 append 答复 + status: done + 归档 `ai_buckup/need_user.md_2026-11-12-21-40-35.md`（60 行 → 压缩 25 行）
- [x] 音节级诊断：**高分不在音节上，而在说完后的衰减/静音尾巴上**（`米雅` 有声段内最高 0.604，峰值 0.827 落在 rms=12.8 的静音窗；`14次件` 峰值 0.869 落在 rms=15.6）→ `training/_t2_miya_score_curve.py` + `.tmp/bats/miya_curve.log`，写在 `tests/2026-11-12-21-40-35_cc/record_1.md`
- [x] `training/_t2_v10b_features.py`：v0.9 基线 + 14xx（正 ×5 / 合格负 ×1），剔除 `negx_tr_1401`（雅诗兰黛 0.822）与 `negx_tr_1402`（米雅 0.827）→ 26515 / 5649 / 58104 / 5028
- [x] `openWakeWord/train_config_v10b.yaml` → 训练 **v1.0b**：**Recall 0.6106、FP/hour 0.0、Accuracy 0.7208**，`aili_xiya_v1.0b.onnx` 13,852 B
- [x] 3 轮矩阵 @0.70 / @0.75 vs v0.9：**v1.0b 无一轴更好 → 不采用，保持 v0.9 + 0.75**（@0.75 14 次件 11、基线 8、新正 17 vs 24；@0.70 定标纯噪声 1 BAD、新正 24 vs 28）
- [x] 3 轮落 `tests/2026-11-12-21-40-35_cc/record_1..3.md` + `opinion.md`，累积 `tests/opinion.md` 已追加；commit 中文主题 + hash 追加台账，禁止 push；`tree.md` 重建
- [x] **need_user.md Q15 已裁决（2026-11-12 22:11，用户选「改窗口约定」）**：正样本窗 `[检出-0.5, 检出+0.3]`（既有 clip 截到前 0.8 s）；负样本剔除 24 帧窗内 RMS 全 <120 的纯静音窗；真人近音件（米雅/雅诗兰黛/爱莉雅/米雅希/希雅老师/爱你老师）只作音节窗验收集

## 2026-11-12-22-11-29 Q15 改窗口约定 → 重训 v1.0c（→ records/2026-11-12-22-11-29.md）

- [x] `need_user.md` Q15 标 status: done + 归档 `ai_buckup/need_user.md_2026-11-12-22-11-29.md` + 压缩（39→36 行）
- [x] `training/_t2_v10c_features.py`：正样本 45 件截前 0.8 s（1555/795 行 ×5）、负样本剔除 RMS<120 纯静音窗（环境音 3 窗全剔，48/12 行 ×1）、真人近音件不入库、`val_fp` 复制自 v0.9 → 26990/6099/58056/5028
- [x] `openWakeWord/train_config_v10c.yaml` → 训练 **v1.0c**：**Recall 0.5865、FP/hour 0.0、Accuracy 0.7013**（13,852 B onnx）
- [x] 3 轮矩阵 @0.70 / @0.75 vs v0.9：**判别轴首次达标**（@0.75 fp 1 件次 ≤1、`米雅`/`雅诗兰黛`/`天猫精灵`/`希雅老师`/键盘噪音/长噪音 0、合成对抗 3、定标与环境音 0；音节窗 max 0.806/0.824），**召回轴塌**（@0.75 14 次件 11、基线 8、带歌声 3 件全漏、新正 16 vs 24）→ **不采用 v1.0c，保持 v0.9 + 0.75**
- [x] 落 `tests/2026-11-12-22-11-29_cc/record_1..3.md` + `opinion.md`，累积 `tests/opinion.md` 已追加；`tree.md` 重建；commit 中文主题 + hash 追加台账，禁止 push；重启服务 + 4 灯复核
- [ ] **need_user.md Q16（status: wait）**：A 补录正样本（干净呼唤 ≥20 次、带噪呼唤 ≥10 次，`need_audio.md`）重训 v1.0d / B 用 0.70 复测 v1.0c（推荐 A+B 并行）；裁决前不推进

## 2026-11-12-22-30-00 Q16 裁决（只 B）→ 用 0.70 复测 v1.0c（→ records/2026-11-12-22-30-00.md）

- [x] `need_user.md` Q16 标 status: done + 归档 `ai_buckup/need_user.md_2026-11-12-22-30-00.md` + 压缩
- [x] 3 轮复测 @0.65 / 0.70 / 0.72（`NINST=3/5/7` 独立实例），对照 v0.9；判据不变 → 复测可重复、0.65 禁区、最佳点 0.72，**不换现役，保持 v0.9+0.75**
- [x] 落 `tests/2026-11-12-22-30-00_cc/record_1..3.md` + `opinion.md`，累积 `tests/opinion.md`；`tree.md` 重建（320 项）；commit `d283fe9` + hash `8d99b42` + 收尾 `6cc0000`，禁止 push；服务重启 + 4 灯复核

## 2026-11-12-22-40-00 Q17 待裁决：补录 / 换 v1.0c+0.72 / 保持不动（→ need_user.md Q17）

- [x] **need_user.md Q17（status: done，22:51 裁决「C 保持 v0.9+0.75，做别的未完项」）**：A 补录未选（缺口留 `need_audio.md`）/ B 换 v1.0c+0.72 未获批准 / **C 已执行**（sherpa 能量门，见下一节）

## 2026-11-12-22-51-09 Q17 裁决 C → sherpa 能量门 + 3 轮 A/B（→ records/2026-11-12-22-51-09.md）

- [x] `need_user.md` Q17 标 status: done + 归档 `ai_buckup/need_user.md_2026-11-12-22-51-09.md` + 压缩
- [x] `jarvis/stt.py`：新增 `_energy_gate`（100 ms 窗 RMS；`span` 只掐头尾静音 / `concat` 逐窗拼接已否决）+ config 键 `stt.sherpa.energy_gate`（默认 true）、`energy_mode`（span）、`energy_threshold`（最终默认 **0.008**）；sherpa 分支调用，whisper 分支不变
- [x] `training/_t2_asr_ab_gate.py`（入 Git）三配置对照（whisper 现役 / sherpa 无门 / sherpa 能量门），已知 6 件 + 抓取 12 件
- [x] 3 轮 A/B（concat 0.015 → 1/6 否决；span 0.015 → 1/6；**span 0.008 → 2/6、乱码 0、耗时 5308 ms 减半**）→ **`stt.engine` 保持 whisper，`config.yaml` 未改**（sherpa 瓶颈是近音声学判别，不在静音）
- [x] 落 `tests/2026-11-12-22-51-09_cc/record_1..3.md` + `opinion.md`，累积 `tests/opinion.md`；`tree.md` 重建；commit 中文主题 + hash 追加台账，禁止 push；服务重启 + 4 灯复核
- [x] 「我没听清，请再说一遍」预合成进 RAM 应答池（**已完成 2026-11-12-23-08-34**，见下一节）；余下未完项：20 轮明确测试补齐（2026-11-08-20-44-17 已 1/20；2026-11-09-19-45-46 已 1/3）、`need_audio.md` 补录缺口、浏览器共享插件（Chrome `--remote-debugging-port=9222`）

## 2026-11-12-23-08-34 未完项 1：应答句「我没听清，请再说一遍」入 RAM 应答池（→ records/2026-11-12-23-08-34.md）

- [x] GPT-SoVITS 预合成 `jarvis/data/ack/ack_no_heard.wav`（现役 `:9880/tts`，3.32 s @32 kHz，与现有 5 条同目录同格式；wav 不入 Git）
- [x] `jarvis/tts.py`：统一采样率 + 具名缓存 `_ack_named` + `play_ack_phrase(name)` + 共用 `_play_cached()`，`play_ack_wav()` 轮播行为不变
- [x] `jarvis/main.py`：`_ask_repeat_if_unmuted()`（先具名 ack，缺句回退 live TTS），只接 `Transcription empty` 与 `Low-quality transcription`；barge-in / `stop_speaking` 语义不变（打断清队列 1219 ms、`is_speaking=False`）
- [x] `memory.db` 加 `hot_phrases(text, kind, count, first_seen, last_seen)`（`user`/`hot`/`near_miss`，上限 200 按 count 淘汰）；写入点 = 真实转录后整句 + 近音句；`stt.set_hot_words`/`_bias_prompt` + `config.yaml` `stt.hot_bias: false`（**偏置默认关**：开则长句升 2 件、短句被吸附 3 件变差、耗时 3.5 倍；表只作数据源）
- [x] 3 轮验证（具名池 / 分支接线 / 表 + initial_prompt A/B）→ `tests/2026-11-12-23-08-34_cc/record_1..3.md` + `opinion.md`，累积 `tests/opinion.md`；`tree.md` 重建；commit 中文主题 + hash 追加台账，禁止 push；服务重启 + 4 灯复核

## 2026-11-12-23-08-35 未完项 4：浏览器共享插件（Playwright MCP + Chrome 9222）（→ records/2026-11-12-23-08-35.md）

- [x] `mcp_connector_catalog` / `mcp_connector_status` 查是否已有 Playwright/浏览器类连接器 → 货架有 `[playwright]`(none 鉴权) + `chrome-devtools` + `firefox-devtools`；已配置的只有 `json-mcp-unity`/`custom-wow-sight`（均 `host-tools-pending`），**浏览器类从未连接**
- [x] 确认本机 Chrome 路径与「需以 `--remote-debugging-port=9222` 启动」这一用户配合项 → **原阻塞判断被推翻**：Playwright 连接器自带浏览器，`mcp_connector_connect` 直连成功，**不需要改 Chrome 启动参数**；共享你正在用的 Chrome 才需要 9222（你在 Chrome 侧配合，我不擅自拉起）
- [x] 连接后 `mcp_connector_tools_list` = **25 个工具**（navigate/snapshot/find/click/type/evaluate/console/network_requests…），限制：读页面走可访问性快照（与「禁止大量截图」一致）
- [x] 3 轮验证全过（工具清单 / 打开 `http://127.0.0.1:7860/` 读快照 / `browser_find` 零截图读 4 盏灯，与 `/api/health` 一致）；页面唯一 console 错误 = favicon 404（良性）；未写 `hard_bug.md`（无阻塞）
- [x] 落盘 + commit 中文主题 + hash 追加台账，禁止 push
- [ ] 待你点头才动代码：把 Jarvis「看屏幕」任务从截图路径改走 `browser_snapshot`/`browser_find`/`browser_click`（零截图）
