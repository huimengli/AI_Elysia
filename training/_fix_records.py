# -*- coding: utf-8 -*-
"""Update records/2026-10-13-11-55.md with assert-guarded replacements."""
P = r"C:\Users\楼听\Desktop\git\JarvisAi\records\2026-10-13-11-55.md"
s = open(P, encoding="utf-8").read()

# 1) status line (no leading space in file — verified by char dump)
old_status = "进行中(pwsh-77 venv 三批安装中 → 之后 api_v2.py 推理验证[需用户停 llama,need_user Q3] → provider 切换 + e2e)"
assert s.count(old_status) == 1, "status anchor missing"
new_status = ("进行中(pwsh-105 venv 批次安装中[jieba 死挂已解] → api_v2.py :9880 "
              "推理验证[llama 已停,内存空出] → tts.provider: gptsovits 切换 + "
              "_e2e_stream_test.py 复验)")
s = s.replace(old_status, new_status)

# 2) insert new implementation bullets after the Q3 line
anchor = "need_user.md **Q3**:请用户在 api_v2 推理前停 llama-server :8080(HB-003)。"
assert s.count(anchor) == 1, "Q3 anchor missing"
i = s.index(anchor) + len(anchor)
eol = s.index("\n", i)
newlines = (
    "\n   - 17:2x **Q2(HB-007)修复完成**:chroma 默认 ONNX 模型(all-MiniLM-L6-v2,83MB)"
    "自 S3 预下载至工作区 `.chroma-models/all-MiniLM-L6-v2/`(SHA256 校验通过);"
    "`jarvis/memory.py` 增 `WorkspaceMiniLM(ONNXMiniLM_L6_V2)` 子类(`DOWNLOAD_PATH` 指工作区)"
    "并传给 `get_or_create_collection(\"facts\")`;旧空 chroma 库因 EF 配置冲突"
    "(persisted `default` vs onnx_mini_lm_l6_v2)删除重建;实测 store/search → STORE_SEARCH_OK,"
    "不再触碰 home `.cache`。"
    "\n   - 17:3x **config.yaml 潜伏 bug**:ref_audio_path 行双引号内含未转义 `\\B`(无效 YAML,"
    "任何进程重新加载即崩;旧服务启动时该行尚不存在故未暴露)→ 自 HEAD 恢复并改单引号;"
    "工作区文件此前已变 GBK/UTF-8 混合编码(编辑以 UTF-8 写入 GBK 文件所致)→ 转纯 UTF-8,"
    "jarvis 全部 11 处读写 config.yaml 的 `open()` 补 `encoding=\"utf-8\"`。"
    "\n   - 17:4x pwsh-89 批次 A2 又在 jieba sdist 构建处死挂(\"Installing build dependencies"
    ": started\" 后 900s 超时)→ 根因:jieba 无 wheel(仅 zip sdist),pip PEP517 隔离构建在 "
    "%LOCALAPPDATA%\\Temp 建临时 venv 被沙箱拦截;镜像页确认 jieba/jieba_fast 零 wheel。"
    "方案 `_setup_gsv4.py`(作业 pwsh-105):预装 setuptools/wheel + `--no-build-isolation` "
    "本地构建 jieba;jieba_fast 跳过(sdist+C 扩展,可选依赖);其余批次纯 wheel。"
    "\n   - need_user.md **Q2/Q3** 均已解决并归档 `ai_buckup/need_user.md_2026-10-13-17-45.md`"
    "(Q3:用户已停 llama :8080,可启动 api_v2);hard_bug.md 同目录归档,HB-007 标记解决。"
)
s = s[:eol] + newlines + s[eol:]

open(P, "w", encoding="utf-8", newline="\n").write(s)
print("RECORDS_UPDATED")
print(open(P, encoding="utf-8").read().splitlines()[-1])
