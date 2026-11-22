"""jarvis 看门狗（HB-049，records/2026-11-21-10-39-00.md 第 1 项）。

**只做一件事：把「死掉的那一刻」落成第一手证据。** 现台账的痛点是进程在批次里死亡后
没有任何退出码（hard_bug.md HB-049：jarvis17、jarvis21 都死过，无退出码证据）。
**不自动重启**（照台账口径：要的是硬证据，不是自愈），也**不碰窗口、不碰服务**。

三个落盘文件（全在 .tmp/，被 .gitignore 忽略）：

| 文件 | 内容 |
| .tmp/<tag>.start | pid、argv、起时刻、日志路径 |
| .tmp/<tag>.log | 子进程 stdout+stderr 合并（**文件重定向，不是管道**，沙箱里 piped stdio 会 EPERM） |
| .tmp/<tag>.exit | 退出码、结束时刻、存活秒数、watchdog 是否杀的、日志尾 40 行、子进程自己写的干净退出标记在不在 |

用法：
    python -m jarvis.watchdog run <tag> -- .venv/Scripts/python.exe -u -m jarvis.main
    python -m jarvis.watchdog run <tag> --no-wait -- <cmd>
    python -m jarvis.watchdog status <tag>
    python -m jarvis.watchdog verdict <tag>

子进程侧配合（jarvis/main.py 已挂）：环境变量 JARVIS_TAG 存在时，jarvis 正常收尾会写
.tmp/<tag>.clean_exit。exit 文件里的 clean_exit_marker 就是判据：码 0 且标记在 = 正常收尾；
码 0 且标记不在 = 不是正常收尾（被外部终止的表现之一）；码非 0 = 崩溃/异常退出。
按 pid 轮询探活（不持管道、不持 Popen 对象，跨命令调用留不住对象）。
"""

import argparse
import ctypes
import ctypes.wintypes
import json
import os
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(REPO_ROOT, ".tmp")
STILL_ACTIVE = 259


def _p(tag, kind):
    return os.path.join(TMP, tag + "." + kind)


def _now():
    return {"wall": time.strftime("%Y-%m-%d %H:%M:%S"), "mono": time.monotonic()}


def tail_lines(tag, n=40):
    path = _p(tag, "log")
    if not os.path.exists(path):
        return []
    raw = open(path, "rb").read().decode("utf-8", errors="replace")
    return [ln for ln in raw.splitlines() if ln.strip()][-n:]


def _handle(pid):
    return ctypes.windll.kernel32.OpenProcess(0x1004, False, pid)


def _exit_code(handle):
    code = ctypes.wintypes.DWORD(0)
    ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
    return code.value


def start_child(tag, argv):
    """Launch with stdout+stderr merged into a FILE (piped stdio is denied in the sandbox)."""
    os.makedirs(TMP, exist_ok=True)
    env = dict(os.environ)
    env["JARVIS_TAG"] = tag
    log = open(_p(tag, "log"), "ab")
    child = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, env=env, cwd=REPO_ROOT)
    rec = {"tag": tag, "pid": child.pid, "argv": argv, "start": _now(),
           "log": _p(tag, "log"), "exit_file": _p(tag, "exit")}
    json.dump(rec, open(_p(tag, "start"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log.close()
    return rec


def wait_by_pid(tag, start, timeout=None):
    pid = start["pid"]
    handle = _handle(pid)
    if not handle:
        rec = {"tag": tag, "pid": pid, "exit_code": None, "killed_by_watchdog": False,
               "end": _now(), "alive_s": 0.0, "note": "OpenProcess 失败（pid 已没了？）",
               "clean_exit_marker": os.path.exists(_p(tag, "clean_exit")),
               "log_tail": tail_lines(tag)}
        json.dump(rec, open(_p(tag, "exit"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return rec
    t0 = time.monotonic()
    killed = False
    code = _exit_code(handle)
    while code == STILL_ACTIVE:
        if timeout is not None and time.monotonic() - t0 > timeout:
            killed = True
            ctypes.windll.kernel32.TerminateProcess(handle, 1)
            time.sleep(0.5)
            code = _exit_code(handle)
            break
        time.sleep(0.5)
        code = _exit_code(handle)
    rec = {"tag": tag, "pid": pid, "exit_code": int(code), "killed_by_watchdog": killed,
           "end": _now(), "alive_s": round(time.monotonic() - t0, 1),
           "clean_exit_marker": os.path.exists(_p(tag, "clean_exit")),
           "log_tail": tail_lines(tag)}
    json.dump(rec, open(_p(tag, "exit"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ctypes.windll.kernel32.CloseHandle(handle)
    return rec


def status(tag):
    start = json.load(open(_p(tag, "start"), encoding="utf-8")) if os.path.exists(_p(tag, "start")) else None
    ex = json.load(open(_p(tag, "exit"), encoding="utf-8")) if os.path.exists(_p(tag, "exit")) else None
    alive = None
    if start:
        h = _handle(start["pid"])
        alive = bool(h) and _exit_code(h) == STILL_ACTIVE
        if h:
            ctypes.windll.kernel32.CloseHandle(h)
    return {"tag": tag, "start": start, "exit": ex, "alive": alive,
            "clean_exit_marker": os.path.exists(_p(tag, "clean_exit")),
            "log_tail": tail_lines(tag, 8)}


def verdict(tag):
    s = status(tag)
    ex = s["exit"]
    if ex is None:
        return tag + "：没有退出记录（" + ("进程还活着" if s["alive"] is True else "状态未知") + "）"
    code = ex["exit_code"]
    clean = ex["clean_exit_marker"]
    if ex["killed_by_watchdog"]:
        kind = ("被 watchdog 杀掉。码 " + str(code) + " 记：**259 = STILL_ACTIVE，杀后读到的值不是真实退出码**；"
                "被杀这件事由 killed_by_watchdog=True 作证，不靠码")
    elif code == 0 and clean:
        kind = "正常收尾（子进程自己写了 clean_exit 标记）"
    elif code == 0:
        kind = "码 0 但没有 clean_exit 标记 —— 不是正常收尾（被外部终止的表现之一）"
    else:
        kind = "非 0 退出码 " + str(code) + "（崩溃/异常退出）"
    tail = "\n".join(ex["log_tail"][-6:])
    return (tag + "：pid " + str(ex["pid"]) + " 退出码 " + str(code) + "，存活 " + str(ex["alive_s"]) +
            " s，结束于 " + ex["end"]["wall"] + "，watchdog 杀=" + str(ex["killed_by_watchdog"]) +
            "，clean_exit=" + str(clean) + "。" + kind + " 日志尾： " + tail)


def main():
    """手工切参数：**不用 argparse**（第 59 处自曝：REMAINDER 把 --no-wait 吞进命令串，
    CreateProcess 拿 --no-wait 当可执行文件，报 WinError 2「系统找不到指定的文件」，
    看着像路径问题、实为参数解析问题）。命令尾巴一律取第一个 `--` 之后的全部内容。
    """
    args = sys.argv[1:]
    if len(args) < 2:
        print("用法：run <tag> [--timeout N] [--no-wait] -- <cmd...> | status <tag> | verdict <tag>")
        sys.exit(2)
    mode, tag = args[0], args[1]
    if mode not in ("run", "status", "verdict"):
        print("mode 必须是 run / status / verdict，收到：" + mode)
        sys.exit(2)
    rest = args[2:]
    no_wait = "--no-wait" in rest
    timeout = None
    if "--timeout" in rest:
        i = rest.index("--timeout")
        timeout = float(rest[i + 1])
        del rest[i:i + 2]
    if "--" in rest:
        cmd = rest[rest.index("--") + 1:]
    else:
        cmd = [t for t in rest if t not in ("--no-wait")]
    if mode == "status":
        print(json.dumps(status(tag), ensure_ascii=False, indent=2))
        return
    if mode == "verdict":
        print(verdict(tag))
        return
    if not cmd:
        print("run 需要 -- 后面的命令（例：run t1 -- .venv/Scripts/python.exe -u -m jarvis.main）")
        sys.exit(2)
    if cmd[0].startswith("-"):
        print("命令以 - 打头（" + cmd[0] + "），多半是分隔符 -- 位置写错；拒绝当可执行文件跑")
        sys.exit(2)
    rec = start_child(tag, cmd)
    print("[watchdog] " + rec["tag"] + " pid=" + str(rec["pid"]) + " 起于 " + rec["start"]["wall"] + " log=" + rec["log"])
    if no_wait:
        print("[watchdog] --no-wait：不写 exit 文件。要落退出码请去掉 --no-wait。")
        return
    rec = wait_by_pid(tag, rec, timeout)  # 真正等完并落 .exit
    print(verdict(tag))


if __name__ == "__main__":
    main()