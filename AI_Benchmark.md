# AI_Benchmark — LLM 基准台账

- **版本**: v1.2（2026-11-08-12-29 加入 Qwen3.5-4B-UD-IQ3_XXS）
- **更新时间**: 2026-11-08-12-29-18
- **关联需求**: records/2026-11-08-12-08-49.md
- **维护约定**: 每测一个新模型，在「各模型明细」追加一节并把行加入汇总对比表；**不覆盖已有模型数据**（AGENTS §2 追加原则）。

## 测试环境（固定）

- 硬件：AMD Ryzen 7 7840U（16 线程）、Radeon 780M iGPU、总内存 27.8 GB（测试时空闲约 18 GB）
- 服务：llama.cpp `llama-server` 于 `:8080`，单槽，`n_ctx=65536`
- 接口：OpenAI 兼容 `POST /v1/chat/completions`；`chat_template_kwargs.enable_thinking=false`（与 Jarvis 运行路径一致，见 config.yaml `llm.enable_thinking`）
- 计时口径：decode tps = `usage.completion_tokens` / wall；prefill tok/s = 非缓存 prompt token / wall；TTFT = 流式首个 `data:` 块延迟（`stream=true`）
- 工具 schema 规模：12 工具 ≈ 980 prompt token；32 工具 ≈ 2,075 prompt token；Jarvis 真实 `TOOL_SCHEMAS`（[jarvis/tools/router.py:63](jarvis/tools/router.py#L63)）为 34 工具、9,795 字符 ≈ 3,000 token
- 执行方式：DSH run_code（Node）直连 `:8080`；未在工作区落基准脚本（`.gitignore` 覆盖 `_*.py/_*.txt/_*.yaml/_*.tar.gz`，不新增仓库文件）

## 测试项定义（固定 prompt 集，新模型请逐字复用）

| 编号 | 内容 | 期望 |
| --- | --- | --- |
| T0 | 你好，20 tok（warm-up，消除冷槽） | — |
| T1 | 中文 100 字短文介绍爱莉希雅（120 tok，temp 0.7） | 中文、非乱码 |
| T2 | 10 条「提高本地语音助手响应速度」的工程手段（300 tok） | 条目结构清晰 |
| T3 | 帮我打开记事本。 + 12 工具 | `open_app` |
| T4 | 工具链：user → assistant tool_call(find_on_screen) → tool 结果 `{x:812,y:456}` | `click_at(812,456)` |
| T5 | 6 项指令：音量调大 / 上海天气 / 搜索爱莉希雅 / 运行 python 1+1 / 关掉微信 / 网页下滚 | media_control, get_weather, web_search, run_python, kill_process, scroll_screen |
| T6 | 纯聊天（system 要求简体中文 + 爱莉希雅人格） | 中文、不滥用工具 |
| T7 | 严格 JSON（temp 0，跑 3 次）：把「打开浏览器并搜索天气」解析为 `{"tool","args"}` | args 保留「天气」 |
| T8 | `context.py` 真实摘要 prompt：`Summarize this conversation in 2-3 sentences:` + 8 条对话 | 2–3 句摘要 |
| T9 | 流式 TTFT（120 tok，中文 50 字） | TTFT 与总时长 |
| T10 | 长上下文 2.7k：60 条日志 + 埋「秘密数字 7128，代号紫罗兰」 | 答 7128；给出 prefill tok/s |
| T11 | 32 工具全量 schema，4 项：音量调到40 / 亮度调低 / 10分钟定时器 / 清空剪贴板 | set_volume, set_brightness, set_timer, set_clipboard |
| T12 | 多步指令：打开记事本 → 输入 hello → 搜索天气 | 顺序单调用（配合 15 步链） |
| T13 | ASR 噪声输入 `打开机台本 然麻搜诗爱莉希雅` | 理想应纠错为「记事本」；观察是否照字面执行 |
| T14 | **decode 速度**：400 token 流式生成，逐行解析 `data:` JSON 取 `delta.content` 计 token；报 TTFT + decode tps 窗口（0-50 / 50-150 / 150-260 / 全程） | 全程 decode tps 与是否随长度衰减 |
| E | 整数参数：点击坐标 (320, 640)。 | `click_at{x:320,y:640}` |

## 汇总对比表

| 指标 | Qwen3.5-0.8B Q4_K_M | **Qwen3.5-2B Q4_K_M** | Qwen3.5-4B Q4_K_M | Qwen3.5-4B **IQ3_XXS** |
| --- | --- | --- | --- | --- |
| 参数量 / 体积 | 752 M / 521 MB | 1.88 B / 1.27 GB | 4.20 B / 2.73 GB | 4.20 B / 1.94 GB |
| 解码速度（热） | **41.8–42.4 tps** | 20.4–20.8 tps | 8.4–9.8 tps | 7.1–8.5 tps |
| **T14 decode（400 tok 流式，剔除 prefill）** | 未测 | **21.2 tps**（窗口 21.5/21.2/21.2，TTFT 248 ms） | 未测 | **8.7 tps**（窗口 8.8/8.7/8.7，TTFT 355 ms） |
| 流式 TTFT | **83 ms** | 162 ms | 428 ms | 684 ms |
| Prefill（无缓存） | **388 tok/s**（2,773→7.1 s） | 204 tok/s（2,773→13.6 s） | 78 tok/s（2,786→35.3 s） | 91 tok/s（2,773→30.5 s） |
| Prefill（缓存命中） | 2,769 cached→0.1 s | 181 tok/s（515 新 token→2.8 s） | 1,065 cached→3.1 s | 2,769 cached→0.8 s |
| 冷槽首轮（32 工具 2,075 tok） | **5.7 s** | 11.1 s | 27.8 s | 25.1 s |
| 热工具轮 | **0.7–1.0 s** | 1.3–1.6 s | 3.0–3.2 s | 3.6–4.4 s |
| 12 工具 6 项选择 | **4/6**（搜索选成 run_python；音量给 play，方向错） | **6/6**（音量→media_control） | 5/6（音量绕成 focus_window） | 6/6（音量→media_control{volume_up}） |
| 32 工具 4 项选择 | **3/4**（清空剪贴板选成 get_clipboard） | **4/4** | 4/4 | 4/4 |
| 工具链 T4（用 tool 结果坐标） | ✅ `click_at(812,456)` | ✅ `click_at(812,456)` | ✅ `click_at(812,456)` | ✅ `click_at(812,456)` |
| E 整数参数 | ❌ 无 tool_call，只回「已定位到目标位置」 | ✅ 320/640 为真 int | 未测 | ✅ 320/640 |
| 长上下文检索（2.7k 埋 7128） | ✅ | ✅ | ✅ | ✅ 3/3 |
| 上下文内算术 | ✅ 记录30=190 MB | ✅ 记录30=190 MB | ✅ 记录0 CPU 20% | ❌ 160 / 250（期望 190，2 次皆错） |
| T8 真实摘要 prompt | ✅ **1.1 s，中文**（自定义中文指令曾 echo） | ✅ 2.7 s，**中文**摘要 | ✅ 6.9 s，英文摘要 | ✅ 7.1 s 中文 |
| T7 严格 JSON 保真 | ✅ 保留 `args.query` | ❌ 3/3 丢 args | ✅ 保留 `args.query` | ✅ 3/3 保留 args |
| T12 多步指令 | ✅ `open_app(notepad)`（英文名，非「记事本」） | ✅ 单调用顺序合理 | ✅ | ✅ `open_app(notepad)` |
| T13 ASR 乱码 | ❌ 照字面 `open_app(机台本)` | ❌ 照字面 `open_app(机台本)` | ❌ 照字面 `open_app(机台本)` | ⚠ **唯一纠错**：`focus_window(记事本)`（未照字面） |
| 中文/人格（T6） | ✅ 中文，人格未保持（T0 自称 Qwen3.5） | ✅（语气更贴爱莉希雅） | ✅ | ✅ |
| 事实性（T1 自由生成） | ❌ 两次均编造（《疯狂动物城》/《哈利波特》） | ❌ 编造「《原神》五星角色/狂流」 | ❌ 编造「愚人众执行官第十人」 | ⚠ 称《崩坏：星穹铁道》（实为崩坏3），最接近真 |

## 各模型明细

### Qwen3.5-0.8B-Q4_K_M（2026-11-08 上午，`C:\Users\楼听\Desktop\test\testGame\models\Qwen3.5-0.8B-Q4_K_M.gguf`，752 M / 521 MB）

- 120 tok 生成 2.9 s → **42 tps**；流式 TTFT、长上下文、prefill 未测。
- 3 工具场景（打开记事本 + 搜索）：`finish=tool_calls`，两个调用与参数全对（`app_control{open,notepad}`、`web_search{爱莉希雅是谁}`）。
- 严格 JSON 保留 `args`；`enable_thinking` 默认开启时 200 token 全被 reasoning 吃掉（content 为空），关闭后 60 token 直出答案。
- 自定义中文摘要指令退化为 echo（复读最后一句，1 token）——摘要能力未验证。

#### 复测 v1.1（2026-11-08-12-19-15，records/2026-11-08-12-19-15.md；补齐全部缺口）

- 解码 41.8–42.4 tps；**TTFT 83 ms**（三模型最快）；**prefill 388 tok/s**（2,773 tok→7.1 s）；缓存命中 2,769→0.1 s。
- 冷槽 32 工具首轮 **5.7 s**；热工具轮 **0.7–1.0 s**（最快）。
- 12 工具 **4/6**：`media_control{play}`（问「音量调大」，方向错）、`get_weather{上海}` ✅、搜索爱莉希雅 → 选成 **`run_python`**（幻觉自造解释，❌ 应选 `web_search`）、`run_python{print(1+1…)}` ✅、`kill_process{微信}` ✅、`scroll_screen{down}` ✅。
- 32 工具 **3/4**：`set_volume{40}` ✅、`set_brightness{50}` ✅、`set_timer{10}` ✅、清空剪贴板 → **`get_clipboard`**（读而非写，❌）。
- **E 整数参数失败（最严重）**：「点击坐标 (320, 640)」→ 无 tool_call，`finish=stop`，回复「已定位到目标位置」——**幻觉宣称已执行**。对 Jarvis 是明确风险：模型可能声称做过而实际没有调用工具。
- 工具链 T4 正确消费 tool 结果 `click_at(812,456)` ✅；长上下文 2.7k 检索 7128 ✅（含无 system 变体）；上下文内算术 190 MB ✅。
- `context.py` 真实摘要 prompt：1.1 s，中文，内容正确 ✅ → **摘要能力确认可用**（此前 echo 系自定义中文指令所致，非模型缺陷）。
- T7 严格 JSON 3/3 保留 `args`（`{"tool":"weather","args":{"query":"天气"}}`）✅。
- T6 中文但人格未保持（T0 自称「我是 Qwen3.5」）；T1 自由生成再次编造（《哈利波特》角色）。
- T10 首次调用返回 raw 错误（服务槽占用），重跑两次均 7128。

#### 0.8B 结论

- 速度是三者最快（TTFT 83 ms、prefill 388 tok/s、热工具轮 0.7 s），**适合内部摘要与意图解析**（1.1 s，已验证）。
- **不适合 32 工具调度**：工具选错、方向错、读写混淆，以及「口头宣称已完成但不发 tool_call」——后者是幻觉执行，必须避免在工具链中使用。

### Qwen3.5-4B-Q4_K_M（2026-11-08 上午，`F:\qwen_gguf\Qwen3.5-4B-Q4_K_M.gguf`，4.20 B / 2.73 GB）

- 解码 8.4–9.8 tps；TTFT 428 ms；prefill 78 tok/s；冷槽首轮 27.8 s（2,075 tok 全量工具 schema），热轮 3.0–3.2 s。
- 32 工具 4/4；12 工具 5/6（「把音量调大」选 `focus_window(系统设置)` 而非 `media_control`，走操作路径而非一步到位）。
- 工具链正确消费 tool 结果坐标；长上下文 2.7k 检索 7128 正确；上下文内算术（记录0 CPU 20%）正确。
- `context.py` 真实摘要 6.9 s 出 2–3 句（英文）；`llm.py` 的 `timeout=15.0` 有余量。
- T1 自由生成出现事实编造；T13 ASR 乱码照字面执行。

### Qwen3.5-2B-Q4_K_M（2026-11-08 中午，`F:\qwen_gguf\Qwen3.5-2B-Q4_K_M.gguf`，1.88 B / 1.27 GB）

- 解码 20.4–20.8 tps；TTFT **162 ms**；prefill **204 tok/s**（2,773 tok→13.6 s），缓存命中后 181 tok/s（515 新 token→2.8 s）。
- 冷槽首轮 11.1 s；热工具轮 **1.3–1.6 s**。语音预算：工具轮 1.4 s + GSV 合成 5–8 s ≈ **8 s**，可接受。
- 12 工具 **6/6**（含 `media_control(increase_volume)`，比 4B 更准）；32 工具 **4/4**；工具链 `click_at(812,456)` 通过；整数参数 `click_at{320,640}` 为真 int。
- 长上下文检索 7128 通过；上下文内算术 190 MB 通过；T12 多步指令顺序单调用；顺序编号指令 1–4 行完全照做。
- `context.py` 真实摘要 2.7 s，**中文**且内容正确。
- **短板**：自由格式 JSON 3/3 丢 `args`（`{"tool":"search_weather","args":{}}`）。Jarvis 走 OpenAI `tools` 结构，此路径参数均填对，故实际影响小。
- T13 ASR 乱码照字面 `open_app(机台本)`（与 4B 同）。
- **T14 decode（2026-11-08-12-51-25 补测）**：**21.2 tps**，TTFT **248 ms**，400 tokens / 19.1 s；窗口 0-50=21.5、50-150=21.2、150-260=21.2 → 260 token 内不衰减。为 4B（T14 未测，热测 9 tps）的 2.3 倍、IQ3（8.7 tps）的 2.4 倍。第 2 次流式试验 `socket hang up`（连续流式断连，三模型复测均出现）。

### Qwen3.5-4B-UD-IQ3_XXS（2026-11-08-12-29-18，`F:\qwen_gguf\Qwen3.5-4B-UD-IQ3_XXS.gguf`，4.20 B / 1.94 GB，IQ3_XXS 3.0625 bpw）

- 解码 7.1–8.5 tps；**TTFT 684 ms（四模型最慢）**；prefill **91 tok/s**（2,773 tok→30.5 s）；缓存命中 2,769→0.8 s。
**T14 decode 复测（2026-11-08-12-40-22，服务端换版本后）**：286 tokens / 33.3 s，**TTFT 355 ms，decode 全程 8.7 tps**，窗口 0-50=8.8、50-150=8.7、150-260=8.7 → **decode 在 260 token 内几乎不衰减**（本机 KV/带宽在该长度非瓶颈）。
- 口径说明：服务端换版本后 SSE 变为 `data:{`（无空格），旧正则计数失效；T14 改用逐行 `data:` JSON 解析（`parseErrs=0`）。上一轮的 7.1-8.5 tps 与 steady 7.1 系该计数问题所致，**以 T14 的 8.7 tps 为准**。第 2 次试验 `socket hang up`（槽占用），仅 1 次有效。
- 跨轮比对注意：`/v1/models` 响应形态已变为 `{"models":[...]}` 且 meta 为空，说明 llama-server 在会话中被更换；各模型数据的服务端版本未必一致。
- 冷槽 32 工具首轮 25.1 s；热工具轮 3.6–4.4 s。整体与 4B Q4_K_M 同级（略慢）。
- **12 工具 6/6 全对**（含 `media_control{volume_up}` 方向正确，优于 4B Q4 的 focus_window 绕路和 0.8B 的方向错）；32 工具 **4/4**。
- 工具链 T4 `click_at(812,456)` ✅；**E 整数参数 ✅**（`click_at{x:320,y:640}`，与 2B/4B 同级；0.8B 在此失败）。
- 长上下文 2.7k 检索 7128 **3/3 全对**（含缓存命中复测）。
- **上下文内算术连续 2 次答错**（记录30 应为 190，答 160、250）——2B 与 0.8B 均答对，说明该 IQ3 量化在数值/事实抽取上退化明显。（4B Q4_K_M 对同一算术题未测，其已测的算术为记录0 CPU 20% 且正确。）
- T7 严格 JSON 3/3 保留 `args`（`{"tool":"browser_search","args":{"query":"天气"}}`）✅；T8 `context.py` 真实摘要 7.1 s 中文 ✅。
- **T13 ASR 乱码：四个模型中唯一做了纠错**——`打开机台本` 识别为「记事本」并发 `focus_window(记事本)`（工具选择偏操作路径，但语义识别正确）。这是首个不照字面执行的模型。
- T1 自由生成称爱莉希雅为《崩坏：星穹铁道》角色（实际是《崩坏 3》），是四模型中最接近真实的表述；T6 中文人格保持 ✅。

#### IQ3_XXS 结论

- **省 0.79 GB 内存，但没换来速度**：1.94 GB 只跑出 7.2 tps（4B Q4_K_M 2.73 GB 跑 9.8 tps），IQ3 的解包开销抵消了带宽优势；TTFT 与 prefill 也更差。
- 工具调度质量与 4B Q4 同级且 12 工具 6/6 最佳；但**上下文内数值抽取两次皆错**，不适合依赖精确数字的场景。
- 在 Jarvis 选型上：**2B 仍是甜点位**；IQ3_XXS 仅当内存极度紧张（如 4B 必须跑）时才值得，本机 18 GB 空闲无此约束。

## 选型结论（截至 2B 测毕）

1. **2B 是本机甜点位**：解码比 4B 快 2.2 倍、prefill 快 2.6 倍、内存省 1.46 GB；工具调度与 4B 同级（32 工具 4/4），工具链/长上下文/算术全过。
2. **4B 的质量优势只在「裸写 JSON 的参数保真」**；在 Jarvis 的 `tools` 路径两者同级，不值得为 4B 付出 27 s 冷 prefill。
3. **0.8B 摘要能力已确认**（T8 真实 prompt，1.1 s 中文摘要）：可作内部摘要/意图解析的专用小模型（0.52 GB）。是否值得多起一个进程取决于摘要触发频率（`context.summarize_after: 8`）；2B 摘要 2.7 s 已够用。
5. **工具语义纪律排序：2B > 4B > 0.8B**。0.8B 出现工具选错（搜索→`run_python`）、方向错（音量→`play`）、读写混淆（清空剪贴板→`get_clipboard`），以及**不发 tool_call 却口头宣称已执行**（E 整数参数）——后者属幻觉执行，是 Jarvis 工具链的硬风险，故 0.8B 不应进入 32 工具调度路径。
4. 已知待修：[config.yaml:18](config.yaml#L18) 的 `llamacpp.model` 仍是 27B 路径，与 `:8080` 实际加载模型不符 → Jarvis 会 model-not-found 并静默 fallback 到未启动的 Ollama（[jarvis/llm.py:42-48](jarvis/llm.py#L42-L48)）。改 config 属实施，按 AGENTS §2 须先落 records/ 与 todo.md。
6. **IQ3_XXS 是"省内存不省时间"的典型**：比 Q4_K_M 省 0.79 GB 却更慢（7.2 vs 9.8 tps、TTFT 684 vs 428 ms、prefill 91 vs 78 tok/s 仅略优），且上下文内数值抽取两次皆错。四模型速度排序：0.8B ≫ 2B ≳ 4B-Q4 > 4B-IQ3；工具纪律排序：2B ≈ 4B-IQ3 > 4B-Q4 > 0.8B。

## 新模型记录模板（追加用）

### `<模型名 + 量化>`（`<日期>`，`<路径>`，`<参数量 / 体积>`）

- 解码 tps（T1/T2 热）：
- TTFT / prefill tok/s（T9/T10）：
- 冷槽首轮 / 热工具轮（T11 首项 / T5）：
- 12 工具 6 项：x/6（逐条列出工具名）
- 32 工具 4 项：x/4
- 工具链 T4 / E 整数参数 / 长上下文检索 / 上下文算术：
- T7 严格 JSON 保真 / T8 真实摘要 / T12 多步 / T13 ASR 乱码：
- 中文人格 T6 / 事实性 T1：
- 结论一句话：