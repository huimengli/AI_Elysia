# Tree — 结构快照（仅非 .gitignore 文件）

更新时间: 2026-11-12-16-58-46。新增 3 项：
- **`ai_buckup/onnx_opinion.md`** — 9 个自训练唤醒 ONNX（v0.1→v0.9）的横向对比台账（版本谱系 / 部署管线 3 轮实测 / 阈值取舍 / HB-032 边界复测 / 结论与缺口），关联 records/2026-11-12-16-58-46.md；
- `records/2026-11-12-16-58-46.md` — 本批需求记录；
- `ai_buckup/todo.md_2026-11-12-16-58-46.md` — `todo.md` 103 行 > 100 触发 AGENTS §3 归档（压缩版留在 `todo.md`，81 行 / 非空 60 行）。

结构现状（承 2026-11-12-12-26 根目录清理，Q13 结案）：可复用脚本 **71 个在 `training/`**（已入 Git、入本树）；日志与探针产物在 `.tmp/`（被忽略）；`jarvis_screen.png`、`love_silvia.txt` 留在根目录（未跟踪）；`AI_Benchmark.md`、`JARVIS_STATE.md`、`PROJECT_SUMMARY.txt` 已 `git mv` 入 `records/`；`need_audio.md` 为缺录清单（格式 `"音频内容", "文件路径"`，路径为空 = 需录）。上一版（275 项）内容见归档链 `ai_buckup/tree.md_2026-11-12-11-20-31.md` 的更新说明。

### 文件数（git ls-files --cached --others --exclude-standard）：278
```
JarvisAi/
├── .gitignore
├── LICENSE
├── README.md
├── config.yaml
├── design.md
├── hard_bug.md
├── install.bat
├── jarvis_screen.png
├── love_silvia.txt
├── need_audio.md
├── need_user.md
├── progress.md
├── requirements.txt
├── start.bat
├── start_all.bat
├── todo.md
├── tree.md
├── ai_buckup/
│   ├── hard_bug.md_2026-10-13-17-45.md
│   ├── need_user.md_2026-10-13-09-56-54.md
│   ├── need_user.md_2026-10-13-17-45.md
│   ├── need_user.md_2026-10-13-21-12-19.md
│   ├── need_user.md_2026-11-12-12-20-21.md
│   ├── onnx_opinion.md
│   ├── progress.md_2026-10-15-13-49-00.md
│   ├── progress.md_2026-11-08-12-40-22.md
│   ├── progress.md_2026-11-08-18-48.md
│   ├── progress.md_2026-11-08-20-14.md
│   ├── progress.md_2026-11-09-17-25-00.md
│   ├── progress.md_2026-11-10-16-56-00.md
│   ├── progress.md_2026-11-10-21-50-17.md
│   ├── progress.md_2026-11-10-23-00-30.md
│   ├── progress.md_2026-11-12-12-25-50.md
│   ├── todo.md_2026-11-10-21-52-25.md
│   ├── todo.md_2026-11-12-16-58-46.md
│   ├── tree.md_2026-11-11-21-15-00.md
│   └── tree.md_2026-11-12-11-20-31.md
├── dsh-my-presets/
│   ├── cordis.patch.yml
│   └── package.json
├── jarvis/
│   ├── __init__.py
│   ├── context.py
│   ├── events.py
│   ├── llm.py
│   ├── main.py
│   ├── memory.py
│   ├── stt.py
│   ├── tts.py
│   ├── wake.py
│   ├── web.py
│   ├── static/
│   │   └── index.html
│   └── tools/
│       ├── __init__.py
│       ├── app_control.py
│       ├── code_exec.py
│       ├── desktop.py
│       ├── file_ops.py
│       ├── router.py
│       ├── subagent.py
│       ├── system.py
│       └── web_search.py
├── llm/
│   ├── startLlama.ps1
│   ├── startLlamaCpu.ps1
│   └── startLlamaVulkanTest.ps1
├── openWakeWord/
│   ├── generate_samples.py
│   └── output/
│       └── aili_xiya_v0.3/
│           └── aili_xiya_v0.3.onnx
├── records/
│   ├── 2026-10-12-12-28-30.md
│   ├── 2026-10-13-11-45.md
│   ├── 2026-10-13-11-55.md
│   ├── 2026-10-13-21-38-01.md
│   ├── 2026-10-14-22-23-49.md
│   ├── 2026-10-15-21-05-48.md
│   ├── 2026-10-17-17-16-41.md
│   ├── 2026-10-17-19-11-07.md
│   ├── 2026-10-17-19-52-00.md
│   ├── 2026-11-08-12-08-49.md
│   ├── 2026-11-08-12-19-15.md
│   ├── 2026-11-08-12-29-18.md
│   ├── 2026-11-08-12-40-22.md
│   ├── 2026-11-08-12-51-25.md
│   ├── 2026-11-08-13-04-48.md
│   ├── 2026-11-08-13-29-56.md
│   ├── 2026-11-08-14-12-32.md
│   ├── 2026-11-08-15-16-18.md
│   ├── 2026-11-08-17-29-39.md
│   ├── 2026-11-08-17-53-00.md
│   ├── 2026-11-08-18-16-33.md
│   ├── 2026-11-08-18-39-40.md
│   ├── 2026-11-08-18-54-18.md
│   ├── 2026-11-08-19-25-48.md
│   ├── 2026-11-08-19-52-59.md
│   ├── 2026-11-08-20-22-00.md
│   ├── 2026-11-08-20-44-17.md
│   ├── 2026-11-09-15-37-58.md
│   ├── 2026-11-09-19-45-46.md
│   ├── 2026-11-09-20-35-43.md
│   ├── 2026-11-09-21-19-29.md
│   ├── 2026-11-09-21-55-14.md
│   ├── 2026-11-10-17-31-10.md
│   ├── 2026-11-10-17-43-08.md
│   ├── 2026-11-10-21-02-16.md
│   ├── 2026-11-10-22-17-39.md
│   ├── 2026-11-10-22-48-24.md
│   ├── 2026-11-11-19-45-46.md
│   ├── 2026-11-11-20-34-04.md
│   ├── 2026-11-11-21-36-30.md
│   ├── 2026-11-12-12-12-28.md
│   ├── 2026-11-12-16-58-46.md
│   ├── AI_Benchmark.md
│   ├── JARVIS_STATE.md
│   └── PROJECT_SUMMARY.txt
├── tests/
│   ├── __init__.py
│   ├── opinion.md
│   ├── test_context.py
│   ├── test_llm.py
│   ├── test_memory.py
│   ├── test_stt.py
│   ├── test_tools.py
│   ├── test_tts.py
│   ├── 2026-11-08-14-12-32_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-15-16-18_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   ├── record_3.md
│   │   ├── record_4.md
│   │   ├── record_5.md
│   │   └── record_6.md
│   ├── 2026-11-08-17-29-39_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-17-53-00_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-18-16-33_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-18-39-40_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-18-54-18_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-19-25-48_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-19-52-59_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-20-22-00_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-09-15-37-58_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-09-20-35-43_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-09-21-19-29_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-09-21-55-14_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   ├── record_3.md
│   │   └── record_4.md
│   ├── 2026-11-10-17-31-10_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-10-17-43-08_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-10-21-02-16_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-10-22-17-39_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-11-19-45-46_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-11-20-34-04_cc/
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   ├── record_3.md
│   │   ├── record_4.md
│   │   ├── record_5.md
│   │   └── record_6.md
│   └── 2026-11-12-10-35-29_cc/
│       ├── opinion.md
│       ├── record_1.md
│       ├── record_2.md
│       └── record_3.md
└── training/
    ├── _chk_feat_stats.py
    ├── _chk_jieba_fast.py
    ├── _chk_mirror.py
    ├── _chk_onnx_probe.py
    ├── _chk_predict_pipeline.py
    ├── _chk_torchcodec.py
    ├── _cn_adv_test.py
    ├── _cn_test.py
    ├── _diag_onnx.py
    ├── _diag_onnx2.py
    ├── _diag_onnx3.py
    ├── _diag_train_mini.py
    ├── _dl_batch2.py
    ├── _dl_numpy.py
    ├── _dl_onnx.py
    ├── _dl_scipy.py
    ├── _dl_wheels.py
    ├── _dump_line.py
    ├── _extract_ar.py
    ├── _fetch_ar.py
    ├── _fetch_oww.py
    ├── _fix_records.py
    ├── _gen_ack_wavs.py
    ├── _inspect_ar.py
    ├── _list_tags.py
    ├── _llm_probe.py
    ├── _llm_quick.py
    ├── _llm_tools_probe.py
    ├── _probe_gsv.py
    ├── _probe_mirror.py
    ├── _probe_onnx_v02.py
    ├── _probe_pandas.py
    ├── _probe_rows.py
    ├── _probe_scipy.py
    ├── _probe_scipy2.py
    ├── _probe_scipy3.py
    ├── _route_check.py
    ├── _setup_gsv.py
    ├── _setup_gsv2.py
    ├── _setup_gsv3.py
    ├── _setup_gsv4.py
    ├── _smoke_check.py
    ├── _smoke_ws.py
    ├── _sync_repo.py
    ├── _t2_augment_dryrun.py
    ├── _t2_diag_v02b.py
    ├── _t2_exp_stream_vs_batch.py
    ├── _t2_make_val_fp_v02.py
    ├── _t2_smoke_stream.py
    ├── _t2_stream_features_v02.py
    ├── _t2_synth_neg.py
    ├── _t2_train_cn.py
    ├── _t2_transform_v02.py
    ├── _t2_v03_fix_features.py
    ├── _t2_v03_negadv_feat.py
    ├── _t2_v03_stage.py
    ├── _t2_v03b_stage.py
    ├── _t2_v03c_data.py
    ├── _t2_v03c_feat.py
    ├── _t2_v04_features.py
    ├── _t2_v04_noisy_clips.py
    ├── _t2_v04_real_clips.py
    ├── _t2_v05_features.py
    ├── _t2_v06_clips.py
    ├── _t2_v06_features.py
    ├── _t2_v06_noisy_clips.py
    ├── _t2_verify_onnx.py
    ├── _tts_400.py
    ├── _tts_api_test.py
    ├── _tts_direct_test.py
    └── _ws_probe.py
```
