"""Monitor 的服务台账与日志中枢（design v3.1 §4 第 1 项，Q30-1 的 G 块）。

授权面照长期边界：jarvis 只认**自己起的** pid（`.tmp/jarvis_child_pids.json` 是唯一名单）；
端口已被占用的服务走「接入识别」—— 只识别 + 体检，不接管日志（Windows 无法事后接管别人进程的
stdout）、不重复起、不杀，面板不给关闭按钮（design §5）。

跑法：jarvis 作父进程起 llama-server / api_v2（`stdout=PIPE, stderr=STDOUT`），读线程把每行
塞进每服务 2,000 行环形缓冲；`shutdown()` 按名单 `taskkill /PID x /T /F` 并落盘证据。
"""
import ctypes, json, os, socket, subprocess, sys, threading, time
from collections import deque
from pathlib import Path

REPO = Path(__file__).parent.parent
PID_FILE = REPO / ".tmp" / "jarvis_child_pids.json"
SHUT_LOG = REPO / ".tmp" / "jarvis_shutdown.log"
RING = 2000  # 每服务环形 2,000 行（design §2 G 块，防内存涨）
_net_cache = {"t": 0, "d": {}}  # netstat 扫描缓存（TTL 2 s）
_win_cache = {"t": 0, "v": None}  # 我起的窗口数缓存（TTL 5 s，第 126 处自曝：逐段计时实测每拍 1688 ms）

# 服务定义照 start_all.bat 的实测写法（路径、参数、env 一个不发明）：
#  - llama = llm\llama-b12144-bin-win-vulkan-x64\llama-server.exe（不是 .venv-llama，那个不存在）
#  - GGML_VULKAN=1、-c 24576 照 Q33 你授权的现内容
#  - GSV = cd /d GPT-SoVITS-main & ..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py
SERVICES = {
    "llama": {
        "label": "llama.cpp :8080", "port": 8080,
        "cwd": REPO / "llm" / "llama-b12144-bin-win-vulkan-x64",
        "cmd": [str(REPO / "llm" / "llama-b12144-bin-win-vulkan-x64" / "llama-server.exe"),
                "-m", str(REPO / "llm" / "models" / "Qwen3.5-2B-Q4_K_M.gguf"),
                "--host", "127.0.0.1", "--port", "8080", "-c", "24576", "-ngl", "99",
                "-fa", "1", "--load-mode", "none", "-b", "1024", "-ub", "512",
                "--no-cont-batching", "--parallel", "1", "--jinja",
                "--repeat-penalty", "1.05", "--reasoning-format", "deepseek",
                "--reasoning-preserve", "--cache-type-k", "q4_0", "--cache-type-v",
                "q4_0", "--mmproj", str(REPO / "llm" / "models" / "Qwen3.5-2B_mmproj-F16.gguf")],
        "env": {"GGML_VULKAN": "1"},
    },
    "tts": {
        "label": "GPT-SoVITS :9880", "port": 9880,
        "cwd": REPO / "GPT-SoVITS-main",
        "cmd": [str(REPO / ".venv-gsv" / "Scripts" / "python.exe"), "-X", "utf8", "api_v2.py"],
        "env": {"HF_ENDPOINT": "https://hf-mirror.com", "HF_HUB_DISABLE_XET": "1"},
    },
}

_locks = threading.Lock()
_procs = {}      # name -> Popen（jarvis 自起）
_rings = {}      # name -> deque(maxlen=2000)
_ring_seq = {}   # name -> 单调写入序号（HB-055：环满后 ring[cursor:] 恒空、增量永久冻结的根因修复）
_meta = {}       # pid -> {name, label, source, started}
_metrics = {}    # 埋点环形（F 块）：name -> deque(maxlen=200)
_tool_stats = {} # E 块：tool -> {n, fail, total}


def _load_pids() -> dict:
    try:
        return json.loads(PID_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_pids(d: dict) -> None:
    try:
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass


def port_open(port: int) -> bool:
    """端口是否已监听（照 start_all.bat 的 netstat 语义，进程内用 socket 判）。"""
    s = socket.socket()
    s.settimeout(0.6)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False
    finally:
        s.close()


def listen_pids(ports: list) -> dict:
    """端口 → 监听它的 pid（第 111 处自曝后定稿：用 `netstat -ano` 解析，第 107-110 处的 ctypes
    表系列连踩 4 次：字段顺序、bOwner、返回码 122 当失败、行距 24 且 IPv4 表不含通配/IPv6 行）。"""
    # 节拍实测 1.8 s/拍（第 120 处自曝后量得：设 1 s，中位 1.9 s，一次快照 1998 ms），瓶颈是每拍跑一次
    # `netstat -ano`。TTL 2 s（监听 pid 陈旧 ≤2 s，提交内存/物理%/CPU 每拍仍新鲜；第 124 处自曝：
    # TTL 1 s 在 1 s 节拍下几乎全 miss，第 2/3 拍仍 1.89/1.86 s，节拍压不下去）。
    # 第 125 处自曝：我写了 `all(p in cache)`，没监听的端口（8080/9880 没起时）永远缺位 → 每拍重扫，缓存形同虚设。
    # 缓存的是全量扫描，所以只按 TTL 放行；未监听的端口从缓存里查不到（陈旧 ≤2 s）。
    if _net_cache["t"] and time.time() - _net_cache["t"] < 2.0:
        # 第 147 处自曝（真会话 0 推送的根因）：第 125 处把「只按 TTL 放行」写死成 _net_cache["d"][p]，
        # 端口没在听（TTS 未起、重启窗口期）时缓存里没这个键 → 每拍 KeyError(9880)，推送全丢。
        # ：查不到就缺席，不抛。
        d = _net_cache["d"]
        return {p: d[p] for p in ports if p in d}
    out = {}
    try:
        r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", shell=False)
        for line in r.stdout.splitlines():
            f = line.split()
            if len(f) >= 5 and f[0] == "TCP" and f[3] == "LISTENING":
                local = f[1]
                i = local.rfind(":")
                try:
                    port = int(local[i + 1:].strip("[]"))
                except ValueError:
                    continue
                out[port] = int(f[4])
        _net_cache["t"] = time.time(); _net_cache["d"] = out
    except Exception as e:
        _log("monitor", "listen_pids 失败: " + repr(e))
    return {p: out[p] for p in ports if p in out}


def _reader(name: str, stream) -> None:
    """管道逐行 → 走 _log（第 5 条：环与 `.tmp/<name>.log` 同步落盘；旧写法直接 append 环，
    llama/tts 的服务日志一条文件都没写 —— 第 179 处自曝）。
    llama 的进度行是 \r 覆盖式，必须按 \r 断行，否则一行刷屏。"""
    for raw in stream:
        text = raw.decode("utf-8", "replace")
        for part in text.replace("\r", "\n").split("\n"):
            line = part.strip()
            if line:
                _log(name, line)


def launch(name: str) -> dict:
    """起一个服务；端口已被占用 = 外部起，走接入识别（不重复起、不杀）。"""
    cfg = SERVICES[name]
    port = cfg["port"]
    with _locks:
        if name in _procs:
            return {"name": name, "status": "running", "pid": _procs[name].pid,
                    "source": "jarvis 起"}
        if port_open(port):
            pid = listen_pids([port]).get(port)
            _meta[pid] = {"name": name, "label": cfg["label"],
                            "source": "外部起 · 无日志接管", "started": None}
            return {"name": name, "status": "external", "pid": pid,
                    "source": "外部起 · 无日志接管"}
        exe = cfg["cmd"][0]
        if not os.path.exists(exe):
            return {"name": name, "status": "missing", "pid": None,
                    "source": "可执行文件不存在（" + str(exe) + "）"}
        env = dict(os.environ)
        env.update(cfg["env"])
        env.setdefault("MPLCONFIGDIR", str(REPO / ".tmp" / "mplconfig"))
        p = subprocess.Popen(cfg["cmd"], cwd=str(cfg["cwd"]), env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, bufsize=0)
        _procs[name] = p
        _rings[name] = deque(maxlen=RING)
        _ring_seq[name] = 0  # 环重置时序号归零（HB-055）
        _meta[p.pid] = {"name": name, "label": cfg["label"], "source": "jarvis 起",
                            "started": time.strftime("%Y-%m-%d %H:%M:%S")}
        d = _load_pids(); d[name] = p.pid; _save_pids(d)
        threading.Thread(target=_reader, args=(name, p.stdout), daemon=True).start()
        return {"name": name, "status": "launched", "pid": p.pid, "source": "jarvis 起"}


def self_pids() -> dict:
    """授权名单：jarvis 自起的 pid（`POST /api/service/stop` 只认这里）。"""
    return {p.pid: name for name, p in _procs.items()}


def stop_service(name: str, pid: int) -> str:
    """只杀名单里的 pid；外部 pid 拒绝（design §5：不静默杀）。回显 taskkill 真实输出。"""
    if pid not in self_pids():
        return ("拒绝：pid " + str(pid) + " 不是本进程起的（名单里只有 " +
                ", ".join(str(k) for k in self_pids()) + "）")
    r = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", shell=False)
    out = (r.stdout + r.stderr).strip()
    _log(name, "关闭 " + str(pid) + " → " + (out or "taskkill 无输出"))
    if name in _procs and _procs[name].pid == pid:
        _procs.pop(name)
    d = _load_pids();
    if d.get(name) == pid:
        d.pop(name); _save_pids(d)
    return out or "taskkill 无输出"


# 第 166-168 处自曝后补：Monitor 的日志区原先只有 llama/tts 两环，爱莉希雅自己的
# 日志（唤醒、转录、回复、链路耗时）不进环，页面上看不到；cmd 窗口则被噪声刷屏。
# 现在：每条日志既进环（前端显示）也写文件（design §2 G 块，照 watchdog 的 .tmp/<tag>.log 口径）。
_log_files = {}
_log_handles = {}  # name -> 打开的追加句柄（第 179 处自曝后补）


def _log_file(name: str) -> Path:
    """该服务的日志文件（`.tmp/<name>.log`，与 watchdog 的 `.tmp/<tag>.log` 同一口径）。"""
    p = REPO / ".tmp" / (name + ".log")
    _log_files[name] = p
    return p


def jlog(line: str) -> None:
    """爱莉希雅自己的日志：进环 + 写文件，**不往控制台刷**（design §2 第 2 条：cmd 窗口只留启动语、网址与报错）。"""
    _log("jarvis", line)


def jerr(line: str) -> None:
    """报错：进环 + 写文件，并且真的打到控制台（报错信息是你要在 cmd 窗口看到的东西）。"""
    _log("jarvis", line)
    print(line, file=sys.stderr)


def _log(name: str, line: str) -> None:
    ring = _rings.setdefault(name, deque(maxlen=RING))
    stamp = time.strftime("%H:%M:%S")
    seq = _ring_seq.get(name, 0) + 1
    _ring_seq[name] = seq
    ring.append((stamp, line, seq))  # 带序号，logs_since 按序号取增量（HB-055）
    try:  # 第 5 条落盘；第 179 处自曝后补：用缓存句柄，不再每行 open/close（llama 启动刷屏时开销太大）
        fh = _log_handles.get(name)
        if fh is None:
            f = _log_files.get(name) or _log_file(name)
            f.parent.mkdir(parents=True, exist_ok=True)
            fh = f.open("a", encoding="utf-8")
            _log_handles[name] = fh
        fh.write(stamp + " " + line + "\n")
        fh.flush()
    except Exception:  # 写文件失败不影响环与调用方；句柄作废下次重开
        _log_handles.pop(name, None)


def _mem_mb(pid: int) -> int:
    """该进程的提交占用 MB（K32GetProcessMemoryInfo 的 PageCount）。查不到返回 -1。"""
    class PMEM(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_size_t), ("PageCount", ctypes.c_size_t),
                      ("PeakPageCount", ctypes.c_size_t), ("WorkingSet", ctypes.c_size_t),
                      ("q1", ctypes.c_size_t), ("q2", ctypes.c_size_t),
                      ("q3", ctypes.c_size_t), ("q4", ctypes.c_size_t),
                      ("PageFaults", ctypes.c_size_t), ("WSUsage", ctypes.c_size_t)]
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED
    if not h:
        return -1
    pm = PMEM(); pm.cb = ctypes.sizeof(PMEM)
    # 第 104 处自曝（record_3）：K32GetProcessMemoryInfo 在 kernel32 里，psapi 是历史别名，
    # Python 3.12 的 windll.psapi 查不到它（AttributeError），轮 3 快照崩在这。用 kernel32。
    ok = ctypes.windll.kernel32.K32GetProcessMemoryInfo(h, ctypes.byref(pm), pm.cb)
    ctypes.windll.kernel32.CloseHandle(h)
    return int(pm.PageCount // 1048576) if ok else -1


def os_stats() -> dict:
    """提交上限/已用/可用 MB + 物理% + CPU%（GlobalMemoryStatusEx + GetSystemTimes 采样）。"""
    class MSX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_uint), ("dwMemoryLoad", ctypes.c_uint),
                      ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                      ("ullTotalPageFile", ctypes.c_ulonglong),
                      ("ullAvailPageFile", ctypes.c_ulonglong),
                      ("ullTotalVirtual", ctypes.c_ulonglong),
                      ("ullAvailVirtual", ctypes.c_ulonglong),
                      ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MSX(); ms.dwLength = ctypes.sizeof(MSX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    ft = ctypes.c_ulonglong * 3
    idle, kern, user = ft(), ft(), ft()
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kern),
                                               ctypes.byref(user))
    now = [idle[0] + (idle[1] << 32), kern[0] + (kern[1] << 32), user[0] + (user[1] << 32)]
    global _last_times
    prev = _last_times
    _last_times = now
    cpu = None
    if prev:
        tot = (now[1] - prev[1]) + (now[2] - prev[2])
        if tot > 0:
            cpu = round(100.0 * (tot - (now[0] - prev[0])) / tot, 1)
    MB = 1048576
    return {"commit_total": ms.ullTotalPageFile // MB,
            "commit_used": (ms.ullTotalPageFile - ms.ullAvailPageFile) // MB,
            "commit_avail": ms.ullAvailPageFile // MB,
            "phys_total": ms.ullTotalPhys // MB, "phys_avail": ms.ullAvailPhys // MB,
            "phys_pct": ms.dwMemoryLoad, "cpu": cpu}

_last_times = None


def metric(name: str, value) -> None:
    """F 块埋点（wake 置信度 / ASR 耗时 / LLM tok/s / TTS 耗时），各 200 样本环形。"""
    _metrics.setdefault(name, deque(maxlen=200)).append(value)


def tool_stat(tool: str, ok: bool, secs: float) -> None:
    s = _tool_stats.setdefault(tool, {"n": 0, "fail": 0, "total": 0.0})
    s["n"] += 1
    s["total"] += secs
    if not ok:
        s["fail"] += 1


def snapshot() -> dict:
    """`/api/monitor` 的快照：A 资源 + B 四灯 + C 进程/窗口 + F 埋点 + E 工具统计。"""
    lp = listen_pids([8080, 9880, 7860]);
    rows = []
    for name, cfg in SERVICES.items():
        pid = _procs[name].pid if name in _procs else lp.get(cfg["port"])
        src = "jarvis 起" if name in _procs else ("外部起 · 无日志接管" if pid else "未起")
        rows.append({"name": name, "label": cfg["label"], "pid": pid, "source": src,
                       "mem_mb": _mem_mb(pid) if pid else -1,
                       "log_lines": len(_rings.get(name, ()))});
    mine = 0
    # 第 126 处自曝后逐段计时坐实：这一段每拍 1688 ms（`app_control` 首建 243 项索引 + 枚举窗口），
    # 是节拍真瓶颈（os_stats 0 ms、listen_pids 冷 67 ms / 缓存 0 ms）。窗口计数变化慢，缓存 5 s
    # （「我起窗口 n/3」陈旧 ≤5 s；读不到写 null，不猜）。
    if _win_cache["v"] is not None and time.time() - _win_cache["t"] < 5.0:
        mine = _win_cache["v"]
    else:
        try:
            from jarvis.tools.app_control import _jarvis_windows
            mine = len(_jarvis_windows())
            _win_cache["t"] = time.time(); _win_cache["v"] = mine
        except Exception:
            mine = None  # ：读不到就写 null，不猜窗口数
    return {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "os": os_stats(),
            "services": rows, "jarvis_windows": mine,
            "metrics": {k: list(v) for k, v in _metrics.items()},
            "tools": {k: {"n": v["n"], "fail": v["fail"],
                              "avg": round(v["total"] / v["n"], 2) if v["n"] else 0}
                          for k, v in _tool_stats.items()},
            "self_pids": {str(p): n for n, p in self_pids().items()}}


def logs_since(name: str, cursor: int) -> tuple:
    """该服务日志的增量（WS 每轮最多 20 行，design §2 G 块）。返回 (lines, new_cursor)。
    HB-055（2026-11-22 19:50，`records/2026-11-22-19-22-36.md`）：旧实现按 `ring[cursor:cursor+20]` 取，
    环满（`deque(maxlen=2000)`）后新行丢最旧、索引整体左移，`cursor=2000` 时切片恒空、游标恒 2000 →
    日志增量永久为 0（页上尾行停在追平满环那一刻）。改按单调序号取尾部增量。"""
    ring = list(_rings.get(name, ()))
    latest = _ring_seq.get(name, 0)
    if latest <= cursor:
        return [], cursor
    n = min(latest - cursor, 20)
    base = latest - len(ring) + 1          # ring[0] 的序号（单调序号映射到满环索引，HB-055）
    off = max(0, cursor - base + 1)       # 游标是「已消费到的最后一条序号」，增量从 off+1 起（第 252 处自曝：旧式把已给过的行再发一次 → 重复 502）
    part = ring[off:off + n]  # 取序号 (cursor, latest] 对应的真行，不重复、不取尾部同一段
    if latest - cursor > len(ring):
        # 客户端落后超过环容量：跳过长日志记（不假装全给，游标推到 latest 不重复发）
        _log("monitor", "游标落后 " + str(latest - cursor) + " 行 > 环 " + str(len(ring)) + "（" + name + "），跳过中间行")
    return [[t, s] for t, s, _ in part], base + off + len(part) - 1  # 游标 = 真给出的最后一条序号（跳过长时推到环头之后，不重复）


def shutdown(reason: str = "exit") -> str:
    """退出时按名单只杀自起 pid，每条 kill 结果落盘（design §5 第 3 条）。"""
    lines = [time.strftime("%Y-%m-%d %H:%M:%S") + " " + reason];
    for name, p in list(_procs.items()):
        try:  # 第 175 处自曝（控制台截图）：解释器退出时 subprocess 会撞
            # `RuntimeError: can't create new thread at interpreter shutdown`，
            # 之前这条异常把整个 atexit 回调抛掉，SHUT_LOG 一行都没写（第 6 条的逐条落盘未证实）。
            r = subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", shell=False, timeout=10)
            res = (r.stdout + r.stderr).strip() or "taskkill 无输出"
        except Exception as e:
            res = "taskkill 抛 " + repr(e)
        lines.append(name + " pid " + str(p.pid) + " → " + res)
        r = subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", shell=False)
        lines.append((name + " pid " + str(p.pid) + " → " +
                      (r.stdout + r.stderr).strip() or "taskkill 无输出"))
    # 外部起的服务不杀（照边界：不是本进程起的）
    try:
        SHUT_LOG.parent.mkdir(parents=True, exist_ok=True)
        SHUT_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception:
        pass
    return "\n".join(lines)


def arm_shutdown() -> None:
    """atexit + SIGBREAK 挂 shutdown()（design §4 第 2 项：关控制台时只杀 pid，不做长 I/O）。"""
    import atexit, signal
    atexit.register(lambda: shutdown("atexit"));
    def _break(signum, frame):
        shutdown("CTRL_CLOSE / CTRL_BREAK");
    try:
        signal.signal(signal.SIGBREAK, _break)
    except Exception:
        pass

