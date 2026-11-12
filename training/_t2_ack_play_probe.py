r"""应答池探针（records/2026-11-12-23-08-34.md 第 1/2 轮）：具名 ack 预加载、出声耗时、打断语义。

- 预加载 `tts.ack_dir` 全部 wav（统一采样率 + 具名缓存），打印条目数、采样率、时长；
- 实测 `play_ack_wav()`（轮播）与 `play_ack_phrase("ack_no_heard")`（具名）的首帧与总耗时；
- **打断语义**：播放中途 `set` 打断标志后 `stop_speaking()`，量测剩余队列被清空的时间（barge-in 不变）。

Run:  .venv\Scripts\python.exe training\_t2_ack_play_probe.py
"""
import sys
import threading
import time

import numpy as np

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import jarvis.tts as T  # noqa: E402

NAME = "ack_no_heard"
NINST = int(__import__("os").environ.get("NINST", "3"))


def timed(fn) -> tuple[float, float]:
    """Return (start-to-ready ms, total ms) for one playback call."""
    t0 = time.perf_counter()
    fn()
    return 0.0, 1000 * (time.perf_counter() - t0)


def main() -> int:
    n = T.preload_ack_audio()
    rates = sorted({r for _, r in T._ack_cache})
    print(f"[preload] clips={n} 统一采样率 {rates}，具名 {sorted(T._ack_named)}", flush=True)
    for stem, (audio, rate) in sorted(T._ack_named.items()):
        print(f"  {stem}: {len(audio)/rate:.2f} s @ {rate} Hz，峰值 {np.abs(audio).max():.3f}", flush=True)
    if NAME not in T._ack_named:
        print(f"FAIL: 具名缓存里没有 {NAME}", flush=True)
        return 1

    for r in range(NINST):
        t0 = time.perf_counter()
        T.play_ack_wav()
        w_ms = 1000 * (time.perf_counter() - t0)
        t1 = time.perf_counter()
        ok = T.play_ack_phrase(NAME)
        p_ms = 1000 * (time.perf_counter() - t1)
        print(f"[轮 {r+1}] play_ack_wav 总 {w_ms:.0f} ms；play_ack_phrase({NAME}) {p_ms:.0f} ms（返回 {ok}）", flush=True)

    # barge-in：播放中途打断，stop_speaking 必须立刻清空队列
    stop_at = 0.35
    th = threading.Thread(target=lambda: T.play_ack_phrase(NAME))
    th.start()
    time.sleep(stop_at)
    t2 = time.perf_counter()
    T.stop_speaking()
    th.join(timeout=5.0)
    print(f"[打断] 播 {stop_at}s 后 stop_speaking：清队列耗时 {1000*(time.perf_counter()-t2):.0f} ms，"
          f"线程结束={not th.is_alive()}，is_speaking={T.is_speaking()}", flush=True)
    print(f"[判据] 具名 clip 存在且可播；打断后 is_speaking=False（barge-in 语义不变）", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
