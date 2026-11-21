"""Monitor 的服务台账与日志中枢（design v3.1 §4 第 1 项，Q30-1 的 G 块）。

授权面照长期边界：jarvis 只认**自己起的** pid（`.tmp/jarvis_child_pids.json` 是唯一名单）；
端口已被占用的服务走「接入识别」—— 只识别 + 体检，不接管日志（Windows 无法事后接管别人进程的
stdout）、不重复起、不杀，面板不给关闭按钮（design §5）。

跑法：jarvis 作父进程起 llama-server / api_v2（`stdout=PIPE, stderr=STDOUT`），读线程把每行
塞进每服务 2,000 行环形缓冲；`shutdown()` 按名单 `taskkill /PID x /T /F` 并落盘证据。
"""
import ctypes, json, os, socket, subprocess, threading, time
from collections import deque
from pathlib import Path

REPO = Path(__file__).parent.parent
PID_FILE = REPO / ".tmp" / "jarvis_child_pids.json"
SHUT_LOG = REPO / ".tmp" / "jarvis_shutdown.log"
RING = 2000  # 每服务环形 2,000 行（design §2 G 块，防内存涨）

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


def listen_pids(ports):
    """端口 -> 占用 pid。第 111 处自曝：ctypes 的 AF_INET 扩展表连踩 4 次（结构字段顺序、
    bOwner、把返回码 122=ERROR_INSUFFICIENT_BUFFER 当失败、行距 24 不是 16），而且绑通配/IPv6
    的行不在 IPv4 表里，50015（Umi 在监听）都查不出来。改用与 start_all.bat 同语义的
    `netstat -ano`：权威、含 IPv6，一次进程内解析（单拍多花 0.2-0.4 s，记进 record）。"""
    out = {}
    try:
        r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", shell=False)
        wanted = {int(p) for p in ports}
        for line in r.stdout.splitlines():
            f = line.split()
            if len(f) >= 5 and f[0] == "TCP" and f[3] == "LISTENING":
                local = f[1]
                i = local.rfind(":")
                try:
                    port = int(local[i + 1:].strip("[]"))
                except ValueError:
                    continue
                if port in wanted:
                    out[port] = int(f[4])
    except Exception as e:
        _log("monitor", "listen_pids 失败: " + repr(e))
    return out
    if rc2 != 0:
        _log("monitor", "listen_pids 第二次调用 rc=" + str(rc2))
        return {}
    n = int.from_bytes(buf[0:4], "little")
    out = {}
    for i in range(n):
        e = Entry.from_buffer_copy(buf, 4 + i * ctypes.sizeof(Entry));
        if e.dwState == 2:  # LISTENING
            out[socket.ntohl(e.dwLocalPort) & 0xFFFF] = e.bpid
    return out


def _reader(name: str, stream) -> None:
    """管道逐行 → 环形缓冲。llama 的进度行是 \\r 覆盖式，必须按 \\r 断行，否则一行刷屏。"""
    ring = _rings[name]
    for raw in stream:
        text = raw.decode("utf-8", "replace")
        for part in text.replace("\r", "\n").split("\n"):
            line = part.strip()
            if line:
                ring.append((time.strftime("%H:%M:%S"), line))


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
                    "source": "照实：可执行文件不存在（" + str(exe) + "）"}
        env = dict(os.environ)
        env.update(cfg["env"])
        env.setdefault("MPLCONFIGDIR", str(REPO / ".tmp" / "mplconfig"))
        p = subprocess.Popen(cfg["cmd"], cwd=str(cfg["cwd"]), env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, bufsize=0)
        _procs[name] = p
        _rings[name] = deque(maxlen=RING)
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


def _log(name: str, line: str) -> None:
    _rings.setdefault(name, deque(maxlen=RING)).append((time.strftime("%H:%M:%S"), line))


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
    try:
        from jarvis.tools.app_control import _jarvis_windows
        mine = len(_jarvis_windows())
    except Exception:
        mine = None  # 照实：读不到就写 null，不猜窗口数
    return {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "os": os_stats(),
            "services": rows, "jarvis_windows": mine,
            "metrics": {k: list(v) for k, v in _metrics.items()},
            "tools": {k: {"n": v["n"], "fail": v["fail"],
                              "avg": round(v["total"] / v["n"], 2) if v["n"] else 0}
                          for k, v in _tool_stats.items()},
            "self_pids": {str(p): n for n, p in self_pids().items()}}


def logs_since(name: str, cursor: int) -> tuple:
    """该服务日志的增量（WS 每轮最多 20 行，design §2 G 块）。返回 (lines, new_cursor)。"""
    ring = list(_rings.get(name, ()))
    part = ring[cursor:cursor + 20]
    return [[t, s] for t, s in part], min(cursor + len(part), len(ring))


def shutdown(reason: str = "exit") -> str:
    """退出时按名单只杀自起 pid，每条 kill 结果落盘（design §5 第 3 条）。"""
    lines = [time.strftime("%Y-%m-%d %H:%M:%S") + " " + reason];
    for name, p in list(_procs.items()):
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

