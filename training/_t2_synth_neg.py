"""v0.2 normal-negative speech: GSV-Elysia TTS of Chinese sentences WITHOUT the
wake phrase, to be timbre-transformed later (see _t2_transform_v02.py).

1700 clips -> openWakeWord/output/aili_xiya_v0.2/neg_src/  (1550 train + 150 test holdout)
Pipeline per clip is IDENTICAL to the v0.1 positives (speed 0.9-1.1, length scales
0.75/1.0/1.25, light white noise p=0.5, peak-norm 0.9, edge silence 0.1-0.4 s) so the
only difference from positives is CONTENT. Resumable.
"""
import os
import random
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "openWakeWord"))
from generate_samples import synth, _to_target_rate, _length_scale, _finalize, _save_wav  # noqa: E402

random.seed(42)

PEOPLE = ["小明", "小红", "老王", "小李", "阿强", "小美", "小军", "丽丽", "大伟", "静静",
         "小芳", "小刚", "阿杰", "小婷", "大壮", "小雪", "老张", "小周", "阿丽", "大鹏"]
PLACES = ["学校", "公司", "家里", "餐厅", "图书馆", "超市", "健身房", "电影院", "公园", "商场",
         "医院", "银行", "酒店", "博物馆", "火车站", "咖啡馆", "书店", "动物园", "游泳馆", "棋牌室"]
FOODS = ["面条", "饺子", "寿司", "披萨", "沙拉", "火锅", "奶茶", "汉堡", "蛋糕", "炒饭",
         "包子", "馄饨", "烧烤", "冰淇淋", "三明治", "皮蛋瘦肉粥", "豆腐脑", "烤肉", "汤圆", "春卷"]
TIMES = ["明天", "后天", "下周一", "周五", "周末", "晚上", "下周", "下个月", "中午", "傍晚",
         "大后天", "下周五", "周一", "周二", "上午", "下午", "月初", "月底", "凌晨", "夜里"]

TEMPLATES = [
    "{p}今天去{pl}了", "{p}说想吃{fd}", "我们{tm}一起去{pl}吧", "{tm}的{fd}准备好了吗",
    "{p}周末有安排吗", "帮我订一张去{pl}的票", "今晚{p}来家里吃饭", "下周{pl}有个活动",
    "{p}把{fd}带过来了", "明天早上叫{p}起床", "我想学做{fd}", "{tm}去{pl}的路上堵车吗",
    "{p}说{tm}要出差", "帮我查一下{pl}的营业时间", "这家的{fd}真好吃", "{p}喜欢喝{fd}吗",
    "把灯关一下谢谢", "现在几点了", "外面下雨了记得带伞", "明天天气怎么样",
    "帮我定个{tm}的闹钟", "冰箱里还有{fd}吗", "今天早点休息吧", "{p}的电话打不通",
    "把窗户开一点", "空调温度调高一些", "我有点累了想睡觉", "帮我看看快递到哪了",
    "这周末有什么计划", "{p}生日快到了", "买两斤苹果回来", "晚上煮碗{fd}吧",
    "{tm}开会别忘了", "把书放回{pl}", "今天运动了一下", "帮我倒杯水",
    "{p}说{fd}要涨价了", "去{pl}顺路买点东西", "明天记得交作业", "晚上一起看个电影吗",
]

def make_texts(n: int) -> list[str]:
    """Deterministic full-pool build (resumable-by-filename across relaunches)."""
    import itertools
    values = {"p": PEOPLE, "pl": PLACES, "fd": FOODS, "tm": TIMES}
    pool: list[str] = []
    for t in TEMPLATES:
        keys = [k for k in ("p", "pl", "fd", "tm") if ("{%s}" % k) in t]
        combos = itertools.product(*[values[k] for k in keys]) if keys else [()]
        for combo in combos:
            kw = dict(zip(keys, combo))
            pool.append(t.format(p=kw.get("p", ""), pl=kw.get("pl", ""),
                                 fd=kw.get("fd", ""), tm=kw.get("tm", "")))
    pool = list(dict.fromkeys(pool))
    assert len(pool) >= n, f"sentence pool too small: {len(pool)} < {n}"
    for s in pool:
        assert "爱莉希雅" not in s
    random.shuffle(pool)
    return pool[:n]

def wait_gsv(timeout_s: float = 900.0) -> None:
    import urllib.request
    t0 = time.time()
    while True:
        try:
            urllib.request.urlopen("http://127.0.0.1:9880/", timeout=5)
            print("[synth_neg] GSV :9880 ready", flush=True)
            return
        except urllib.error.HTTPError:
            # server answered (any status) -> up and serving
            print("[synth_neg] GSV :9880 ready (HTTP answer)", flush=True)
            return
        except Exception:  # noqa: BLE001
            if time.time() - t0 > timeout_s:
                raise RuntimeError(f"GSV :9880 not ready after {timeout_s}s: {e}")
            print("[synth_neg] waiting for GSV :9880 ...", flush=True)
            time.sleep(15)


def main() -> None:
    import time
    wait_gsv()
    n_total = 1700
    out_dir = ROOT / "openWakeWord" / "output" / "aili_xiya_v0.2" / "neg_src"
    out_dir.mkdir(parents=True, exist_ok=True)
    texts = make_texts(n_total)
    length_scales = [0.75, 1.0, 1.25]
    for i, text in enumerate(texts):
        path = out_dir / f"neg_src_{i:04d}.wav"
        if path.exists() and path.stat().st_size > 0:
            continue
        x, rate = synth(text, speed=random.uniform(0.9, 1.1))
        x = _to_target_rate(x, rate)
        x = _length_scale(x, length_scales[i % len(length_scales)])
        if random.random() < 0.5:
            x = x + (np.random.randn(len(x)).astype("float32") * (0.98 * 0.01))
        x = _finalize(x)
        _save_wav(x, str(path))
        if (i + 1) % 25 == 0:
            print(f"[synth_neg] {i + 1}/{n_total} written", flush=True)
    done = len([p for p in out_dir.glob("*.wav") if p.stat().st_size > 0])
    print(f"[synth_neg] done: {done}/{n_total} clips in {out_dir}", flush=True)

import numpy as np  # noqa: E402

if __name__ == "__main__":
    main()
