# 第 1 轮：白厄（v2ProPlus）权重接入 + 7 音色矩阵打分入库（2026-11-12 20:03-20:45）

- 时间：2026-11-12 20:03:41（需求提出）→ 20:45（入库完成）
- 场景：用户给出 `F:\BaiduNetdiskDownload\白厄`，下载方称 v2ProPlus；接入 18:49 起的多音色 TTS 训练集
- 期望：① 判定权重是否可用 ② 生成 20 条文本 ③ 按「正样本 3 实例峰值中位数 ≥0.70 入库 / 负样本 3 实例全 <0.70 入库」判据入库
- 实际：见下
- 结果：**权重可用（版本判定由内容证实）**；7 音色 140 件中 34 件合格入库（21 正 / 13 负）
- 备注：零截图，全部文字与文件产出

## 1. 权重真实性判定（不靠文件名，也不靠下载方说法）

| 检查 | 结果 |
| --- | --- |
| `白厄_e10_s680.pth` 首 2 字节 | `b"06"` —— `GPT_SoVITS/process_ckpt.py:22-28` 的 `model_version2byte["v2ProPlus"] = b"06"`（v2Pro=b"05"、v3=b"03"、v4=b"04"）。**v2ProPlus 说法被权重内容证实** |
| 文件大小 | SoVITS 172,765,299 B > 本机 v2 `s2G2333k.pth` 106,035,259 B / 爱莉希雅 85,007,488 B，符合 v2ProPlus 参数量 |
| GPT `白厄-e10.ckpt` | 155,313,312 B，`/set_gpt_weights` 返回 `{"message":"success"}`，v2ProPlus 的 GPT 架构被接受 |
| 首次加载失败根因 | `HTTP 400: change sovits weight failed → [Errno 2] No such file or directory: 'GPT_SoVITS/pretrained_models/sv/pretrained_eres2netv2w24s4ep4.ckpt'` —— v2ProPlus 需要 speaker encoder `ERes2NetV2` 预训练权重（`GPT_SoVITS/sv.py:6` 硬编码路径），本机 `pretrained_models` **原本没有 `sv` 目录**（v2 不需要） |
| 修复 | 从 hf-mirror 下载 `lj1995/GPT-SoVITS/resolve/main/sv/pretrained_eres2netv2w24s4ep4.ckpt` → `GPT-SoVITS-main/GPT_SoVITS/pretrained_models/sv/`，**107,528,697 B / 46 s**（2.2 MB/s；`--ssl-no-revoke`。hf-mirror 的 `/api/v1` 返回 503，只能对 tree 页面正则取 `resolve/main` 链接） |

## 2. 冒烟（`--only bai_e --smoke`）

```
[weights] gpt <- 白厄-e10.ckpt: {"message":"success"}
[weights] sovits <- 白厄_e10_s680.pth: {"message":"success"}
[bai_e] pos ai_li_xi_ya 1.06s rms=4098 -> bai_e__pos__ai_li_xi_ya.wav
[weights] gpt <- 【GPT2.0】Elysia-e20.ckpt: {"message":"success"}
[weights] sovits <- 【GPT2.0】Elysia_e24_s13080.pth: {"message":"success"}
```

时长正常（1.06 s，无真人克隆那类 60 s 失控），生成后**已切回 Elysia 权重**，线上 TTS 音色不变。日志 `.tmp/bats/v11_bai_smoke3.log`。

## 3. 生成与打分

- 生成：`--only bai_e` 20 件，全量 7 音色 × 20 = **140 件**（`elya`/`firefly`/`bai_e`/`k_zf_xiaoxiao`/`k_zf_xiaoni`/`k_zm_yunyang`/`k_zm_yunxi`）；真人音色克隆已定案不可用（`SKIP_USER`）。日志 `.tmp/bats/v11_bai_gen.log`、`.tmp/bats/v11_gen2.log`。
- 打分口径修正（本轮重要发现，可复用）：
  - 跨件连续流式复用 4 个 Model 实例 → **不可比**：上一件 mel 缓冲带进下一件 + 检出后 `reset()` 清零缓冲，把 `elya__pos__ai_li_xi_ya` 峰值从 **0.873**（逐件新建实例，与部署同口径）压到 **0.483/0.483/0.483**（三实例完全相同 = 播种独立性丢失，HB-032）。
  - 一次性 560 次 Model 构造 → onnxruntime `bad allocation` 崩（20:30，当时 GSV 服务在跑）。
  - 最终：**逐件新建实例 + `del` + `gc.collect()`**，打分前停掉 `:9880`（Free 15.9 GB）→ 140 件跑完。日志 `.tmp/bats/v11_score70_all3.log`。

## 4. 入库结果（v0.9 @0.70，判据：正样本检出 ≥1 且 3 实例峰值中位数 ≥0.70；负样本 3 实例全 <0.70）

| 音色 | 正样本入库 | 负样本入库 |
| --- | --- | --- |
| bai_e（白厄，新） | 3/3 | 6/17 |
| elya（爱莉希雅，同音色基线） | 3/3 | 5/17 |
| firefly（流萤） | 3/3 | 2/17 |
| k_zf_xiaoxiao / k_zf_xiaoni / k_zm_yunyang / k_zm_yunxi | 各 3/3 | **各 0/17** |
| 合计 | **21/21** | **13/119** |

- clip 编号 15xx：`positive_train 10 / positive_test 10 / negative_train 7 / negative_test 7`（用号 `posx 1520 / negx 1514`），日志 `.tmp/bats/v11_clips.log`。
- 特征并入 **v0.9 基线**（v1.0 特征不带入）：正样本 ×5、合格负样本 ×1
  `positive_features_train 25435+600 → 26035`、`positive_features_test 5304+600 → 5904`、
  `negative_features_train 58008+84 → 58092`、`negative_features_test 5016+84 → 5100`，`val_fp` 复制自 v0.9。日志 `.tmp/bats/v11_features.log`。

## 5. 结论（第 1 轮）

1. **白厄权重可用**，v2ProPlus 说法由首 2 字节 `b"06"` 证实；本机缺 `sv/pretrained_eres2netv2w24s4ep4.ckpt` 是唯一障碍，补齐后即通。
2. **多音色正样本全面有效**：7 个音色（含白厄、流萤、4 个 Kokoro 中文音色）的 `爱莉希雅` 3 条文本在 v0.9 @0.70 上全部检出且峰值 ≥0.70 → 21 件全入库，可扩宽召回。
3. **多音色对「负样本」几乎无效**：119 件负样本仅 13 件合格（Kokoro 4 音色 0/17，白厄 6/17，流萤 2/17，同音色 elya 5/17）。近音词在**任意音色**下峰值都 ≥0.70（与真唤醒 0.82 同量级）→ 与长期结论一致：**换音色不能产生近音判别力，只能扩大召回**。
4. 可入库负样本全部落在低分区（<0.70），入库不会触发 v1.0 式塌陷（那批的机制是负样本与真唤醒峰值重叠）。
