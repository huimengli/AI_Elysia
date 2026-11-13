import subprocess
import sys
import tempfile
import os
import time
import yaml
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"

def _load_config():
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_python(code: str) -> str:
    """Execute Python code in a subprocess sandbox. Returns stdout/stderr.

    HB-033 延伸 + HB-034 家族（2026-11-13）：临时脚本以前写 `%TEMP%`，服务作为
    harness 后台任务启动时 python 子进程的 `%TEMP%` 禁写 → 工具直接炸；子进程输出
    以前用 `text=True`，按本机代码页 GBK 解码，中文输出会在 reader 线程崩。现在脚本
    写工作区 `.tmp/pyrun`，输出按 UTF-8 解码。
    """
    timeout = _load_config()["tools"]["code_timeout"]
    run_dir = Path(__file__).parent.parent.parent / ".tmp" / "pyrun"
    run_dir.mkdir(parents=True, exist_ok=True)
    tmp = run_dir / f"run_{int(time.time() * 1000)}.py"
    tmp.write_text(code, encoding="utf-8")
    fname = str(tmp)
    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", fname],
            capture_output=True,
            timeout=timeout,
        )
        out = result.stdout.decode("utf-8", errors="ignore")
        err = result.stderr.decode("utf-8", errors="ignore")
        return (out + err).strip() or "(无输出)"
    except subprocess.TimeoutExpired:
        return f"代码执行超时（{timeout} 秒）。"
    except Exception as e:
        return f"执行出错：{e}"
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass
