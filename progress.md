# Progress — 跨会话进度台账

<!-- 已归档于 ai_buckup/progress.md_2026-10-15-13-49-00.md（至 2026-10-15）与 ai_buckup/progress.md_2026-11-08-12-40-22.md（至 2026-11-08 12:29） -->

## 归档摘要（已完成需求，详见备份全文）

- **2026-10-12**（records/2026-10-12-12-28-30.md）："将 Jarvis 项目跑起来"：.venv、config llamacpp active、依赖（清华镜像）、端到端跑通。
- **2026-10-13**（records/2026-10-13-11-45.md、11-55.md）："接入 GPT-SoVITS 2.0 爱莉希雅 TTS"完成（venv 分批安装、jieba 补丁、:9880 验证）。Q1 已归档。
- **2026-10-13 深夜–10-17**（records/2026-10-13-21-38-01.md）：爱莉希雅化 T1/T5 完成并 e2e PASS；自训唤醒词 v0.1→v0.2→v0.2b→**v0.3c 验收 PASS（pos 0.807 / neg 0.453，阈值 0.7 → recall 0.94 / fp 0.09）并接入 config.yaml**；排障链 HB-014/017/018/019/020/021/022/023/024/025/027/028。
- **2026-10-17**（records/2026-10-17-17-16-41.md）：T7 事件记录 + SQLite（events.db, WAL）+ 网页历史展示 / T8 5 句固定应答词 wav 随机播放 / T9 start_all.bat 一键启动；WS 冒烟 3/3 PASS；排障 HB-030（`_abort` 跨轮污染）、HB-031（唤醒 barge-in 误杀并发 Web 轮次）。
- **2026-10-17**（records/2026-10-17-19-11-07.md、19-52-00.md）：README 全文中文化（fork 说明 + 权重来源/类型 + 自用声明）+ MIT LICENSE；仓库指向 AI_Elysia；唤醒词 onnx v0.3（13 KB，自训练）入库；push 已随 Q6 由用户完成（Q6 事实已解决，待归档）。

## Git 提交记录

- `7d279a7` `docs(AI): 补全 Jarvis 运行记录并归档 Q1（端到端 CHAT_OK）`。已本地 commit。
- `f444b85` `feat(AI): 新增 gptsovits TTS provider 并关闭 Qwen3 thinking 解决 LLM 挂起`。已本地 commit。
- `409cc3f` `docs(AI): sync GPT-SoVITS venv retry, e2e PASS, and user asks`。已本地 commit。
- `f4e1b48` `fix(AI): repair config.yaml escape/encoding, pin chroma embedding`。已本地 commit。
- `e9b90f0` `fix(AI): gptsovits provider live + GPT-SoVITS runtime patches, TTS verified`。已本地 commit。
- `6b1b545` `fix(AI): merge memory facts into single system message; UTF-8 console`。已本地 commit。
- `a15c1ab` `feat(AI): 爱莉希雅 self-reference + forced Chinese, HB-014 stream stall guard`。已本地 commit。
- `c63c8ef` `docs(AI): record commit a15c1ab in ledger; rebuild tree snapshot`。已本地 commit。
- `d8567cb` `docs(AI): record TTS migration request to SoulX-Podcast (todo only)`。已本地 commit。
- `30eba61` `docs(AI): T2 pre-training audit — tflite best-effort, generation`。已本地 commit。
- `3bb5b7d` `feat(AI): wake.py supports local ONNX model paths`。已本地 commit。
- `8a97e4a` `docs(AI): ledger backfill (c63c8ef..3bb5b7d) + T2 augment chain de-risk`。已本地 commit。
- `8c33f74` `feat(AI): 爱莉希雅自称与中文强制收尾，v0.2 唤醒词数据重建中`。已本地 commit。
- `be4e07c` `docs(AI): HB-024 Kellet IIR 粉噪溢出已解决（FFT 基替换）；todo 作业号更正`。已本地 commit。
- `07bd022` `docs(AI): T2 train-branch HB-017..020 fixes, smoke PASS, production training`。已本地 commit。
- `38b1d02` `feat(AI): add DSH agent presets PTC-MY 与 创造模式-MY via workspace bundle`。已本地 commit。
- `a390837` `feat(AI): v0.3c 唤醒词验收 PASS 并接入 config.yaml（recall 0.94 / fp 0.09 @ 阈值 0.7）`。已本地 commit。
- `1072661` `docs(AI): 勾选 T2 唤醒词完成（v0.3c PASS 已接入）；T4 用户确认延后记 todo`。已本地 commit。
- `2222230` `feat(AI): Web UI 事件记录 + SQLite 持久化 + 固定应答词 wav + start_all.bat`。已本地 commit。
- `999cc32` `docs(AI): README 中文化（fork 说明 + 权重来源/类型 + 自用声明）+ MIT LICENSE`。已本地 commit。
- `251f7b0` `docs(AI): 台账补记 999cc32（README 中文化 + AI_Elysia 命名 + LICENSE）`。已本地 commit。
- `193e8cd` `docs(AI): push 受阻（本机无 GitHub 凭据 SEC_E_NO_CREDENTIALS）记 need_user.md Q6；records 实施记录回填`。已本地 commit。
- `451226f` `feat(AI): 唤醒词模型 onnx v0.3 入库（自训练，13 KB）`。已本地 commit。
- `2eaa648` = 当前 HEAD = `origin/main`（2026-10-17-19:5x）。`.git/logs` reflog 有 3 次 `update by push`（18:43 / 19:40 / 19:52），即 Q6 的 push 由用户完成；本条为台账补记（原 451226f 之后未记录）。
- `cb3b904`（2026-11-08-13:40，main）`docs(AI): LLM 基准台账 AI_Benchmark.md（四模型 T0-T13+E + T14 decode）+ progress 归档`。**已本地 commit，未 push。** 10 文件（AI_Benchmark.md、progress.md、todo.md、tree.md、ai_buckup 备份、records 五则）。
- `35cd7ae`（2026-11-08-13:40，main，= 当前 HEAD）`feat(AI): llm/ 启动脚本自包含仓库内路径，.gitignore 排除 llama.cpp 二进制与 gguf`。**已本地 commit，未 push。** 8 文件（.gitignore、config.yaml、README.md、三个 .ps1、records 两则）。
- 排障（非阻塞，已解决）：本会话沙箱默认禁进程 spawn（`EPERM spawnSync cmd.exe`），git 需逐次申请 wider sandbox 批准；且 spawn 环境无 HOME → `git commit` 报 `unable to auto-detect email address`。解法：不改/不写 git 配置，用 `GIT_AUTHOR_NAME=绘梦璃 GIT_AUTHOR_EMAIL=2913394404@qq.com`（取自 2eaa648 作者）+ `GIT_COMMITTER_*` 同值，`git commit -m` 成功。`-c user.name=…` 与 `-m` 不能同用（`options '-m' and '-c' cannot be used together`）。

## 2026-11-08 LLM 基准测试（台账 `AI_Benchmark.md`，records/2026-11-08-12-08-49.md 起）

- 用户在 `:8080` 依次加载 4 个 GGUF：0.8B-Q4_K_M(521 MB) → 4B-Q4_K_M(2.73 GB，用户原称 Qwen2.5-4B，实测 Qwen3.5) → 2B-Q4_K_M(1.27 GB) → 4B-UD-IQ3_XXS(1.94 GB)。同一 prompt 集 T0–T13 + E，后加 **T14 decode 速度**。
- 速度（decode / prefill / TTFT）：**0.8B** 42 tps / 388 tok/s / 83 ms；**2B** 20.6 tps / 204 tok/s / 162 ms；**4B-Q4** 9 tps / 78 tok/s / 428 ms；**4B-IQ3** 8.7 tps（T14 实测，窗口 8.8/8.7/8.7 不衰减）/ 91 tok/s / 355–684 ms。
- 能力：2B 与 4B-IQ3 为工具调度最佳档（12 工具 6/6、32 工具 4/4、E 整数参数 ✅、工具链 `click_at(812,456)` ✅）；0.8B **E 项幻觉执行**（无 tool_call 却称已定位）+ 12 工具 4/6、32 工具 3/4；4B-Q4 12 工具 5/6。2.7k 长上下文检索四者全对；**上下文内算术** 2B/0.8B 对（190），**4B-IQ3 连错 2 次（160/250）**。
- **T13 ASR 乱码唯一纠错者是 4B-IQ3**（机台本 → 记事本，发 `focus_window`）；其余三者照字面 `open_app(机台本)`。
- 摘要（`context.py` 真实 prompt）：0.8B 1.1 s 中文 ✅、2B 2.7 s 中文 ✅、4B 6.9 s 英文 ✅、4B-IQ3 7.1 s 中文 ✅。
- **选型：2B 为本机主模型甜点位**；0.8B 适合内部摘要/意图解析；4B-Q4 与 4B-IQ3 在 27 s 冷 prefill 下不适合语音轮（IQ3 省 0.79 GB 但不省时间）。
- ~~待修~~ **已修（2026-11-08-13-04）**：[config.yaml:18](config.yaml#L18) `llamacpp.model` 由 27B 路径改为仓库内 `llm\models\Qwen3.5-2B-Q4_K_M.gguf`（此前与 `:8080` 不符 → model-not-found + 静默 fallback 到未启动的 Ollama，[jarvis/llm.py:42-48](jarvis/llm.py#L42-L48)）。
- 口径提示：llama-server 会话中被换版本（`/v1/models` 形态由 `data:[...]`+meta 变为 `models:[...]`、SSE `data: {`→`data:{`）；跨轮比较需注意服务端版本。
- 未 commit：本机沙箱禁 spawn，`git` 不可执行（与 HB-023 同源环境限制）。**progress.md 已按 §3 归档**（备份 `ai_buckup/progress.md_2026-11-08-12-40-22.md`，本文件为 compact 版，Git 提交台账全保留）。
- **2026-11-08-12-51 2B T14 补测**（records/2026-11-08-12-51-25.md）：**decode 21.2 tps、TTFT 248 ms**，400 tokens / 19.1 s，窗口 21.5/21.2/21.2（260 token 内不衰减）→ 2B decode 为 IQ3（8.7 tps）的 2.4 倍；连续第 2 次流式请求 `socket hang up`（三模型复测均现该现象）。
- **2026-11-08-13-04 llm/ 入库忽略 + 2B 定为主模型**（records/2026-11-08-13-04-48.md）：`llm/` 已含 `llama-b12144-bin-win-cpu-x64/`、`-vulkan-x64/`（含 `llama-server.exe`）、`models/Qwen3.5-2B-Q4_K_M.gguf`(1221.5 MB) + `Qwen3.5-2B_mmproj-F16.gguf`(637.3 MB) 与 3 个 `startLlama*.ps1`。`.gitignore` 追加两 bin 目录 + `llm/models/*.gguf` + `*.gguf`/`*.exe`/`*.dll`（`.ps1` 保留跟踪）；`config.yaml` `llamacpp.model` 改为仓库内 2B 路径；README 三处同步；`tree.md` 加 `llm/`（仅 3 个 .ps1，被忽略的二进制与 gguf 不列）。三个 .ps1 的 `$BinDir` 与默认模型仍指向外部 `testGame`（`startLlamaCpu.ps1` 默认 0.8B 文件仓库内不存在），改动需用户确认（todo 已记）。
- **2026-11-08-13-29 三个 .ps1 改为仓库内路径**（records/2026-11-08-13-29-56.md）：`$BinDir` 与默认模型全部基于 `$PSScriptRoot`（`llm/llama-b12144-bin-win-vulkan-x64` / `-cpu-x64` + `llm/models/Qwen3.5-2B-Q4_K_M.gguf` + `Qwen3.5-2B_mmproj-F16.gguf`），外部 `testGame` 路径已清零（grep 复核）；`startLlamaCpu.ps1` 原默认 0.8B 文件在仓库不存在（会 `找不到模型` 退出）→ 改 2B；`startLlamaVulkanTest.ps1` 补 `Push-Location $BinDir`+`Pop-Location`（原缺，DLL 可能加载失败）并修 API-key 分支误用未定义 `$llamaArgs` → `$args0`。四个校验路径均存在（`llama-server.exe` ×2 + 两个 gguf）。未实机验证：沙箱禁 spawn，无法执行 PowerShell。
## 2026-11-08-18-16-33 切回 main 对比 UI（records/2026-11-08-18-16-33.md，tests/2026-11-08-18-16-33_cc/）

- **UI 差异确证**：main = 旧版（`<title>J.A.R.V.I.S.</title>`，`index.html` 52,655 B / 1,174 行，Google Fonts `@import`，无 `--pink`/`petal`，文案仅英文）；`future/AI_UI` = Elysia 版（`<title>爱莉希雅</title>`，41,769 B / 829 行，`--pink`+`petal`+`backdrop-filter`，无 CDN，全中文文案）。刷新 http://127.0.0.1:7860 对比；切分支：`git checkout future/AI_UI` 后重启 jarvis。
- 服务：llama `:8080`（Qwen3.5-2B-Q4_K_M，与分支无关）、GPT-SoVITS `:9880`（job pwsh-10，pid 4436）未重启；**jarvis `:7860` = job pwsh-21（main 代码）**。WS chat 在 main 代码下正常（`我是爱莉希雅，一位完全自主的个人 AI 助手。`），TTS `POST /tts` 200 / 271,404 B / RIFF。
- **风险**：main 不含 17:53 的 500 修复（前导 system 摘要并入唯一 system）与 `llm.py` 补丁（`chat_template_kwargs.enable_thinking`、`timeout` 15→90）→ 真人测试聊到 8 条触发压缩会重现「保存设置后管线报错」。语音真人测试请在 `future/AI_UI` 上做。
- 切分支坑：`git checkout main` 被本地已改的 `todo.md` 阻断（两分支内容不同）→ 先 commit `c071d73`（在 `future/AI_UI`，已 push）再 checkout；重启 `:7860` 需 `Stop-Process` 掉旧 python（`job_kill` 只杀 pwsh 外层）。
- 本分支台账说明：T6 Elysia UI（`80f7cd1`）、skill 修复文档（`243dc3e`/`19f1cac`/`b025a9e`/`7413031`）、三服务启动（`aaeb358`）、500 修复（`7f4ff44`）、config 记录（`9d2a9dc`）、本需求 record（`c071d73`）都在 `future/AI_UI` 上；本分支只落本需求的 record/tests/progress/tree。

#### Git 提交记录（本分支）
- 本次：records/2026-11-08-18-16-33.md（重建）、tests/2026-11-08-18-16-33_cc/（4 文件）、todo.md、progress.md、tree.md。已本地 commit（hash 见下），**未 push**（AGENTS §4 禁 push；用户此前只授权 `future/AI_UI`，main 未获授权）。
