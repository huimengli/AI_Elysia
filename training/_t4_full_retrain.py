r"""全量重训驱动 v1.2（2026-11-17 12:20 需求，records/2026-11-17-12-20-00.md）。

你 11:00 第 4 条：「全量重训练(基于现有多音色tts,我的部分音频,和噪音)一个版本出来,如果还不如0.9就不改了」；
12:01 答复「先用现有多音色 TTS 合成训」→ 本驱动**不等你真人音频**，用现有多音色 TTS + 重生成噪音出一版 v1.2，
与 **v0.9 同口径**验收，**任一条不如 v0.9 就不改 `config.yaml` 指向**（`v0.9 + 0.75` 保持现役）。

**全部复用既有脚本，不造新约定（AGENTS §0）**：

| step | 调用 | 需要 |
| --- | --- | --- |
| `bg` | `openWakeWord/_make_background.py` 的 `make_noise(24)`（纯合成）+ `make_speech(30)`（GSV） | `make_speech` 需 `:9880` |
| `synth` | `training/_t2_v11_tts.py`（GSV 爱莉希雅 / 流萤 Firefly / Kokoro 中文 4 声 → `.tmp/v11tts`，断点续传） | `:9880` |
| `score` | `training/_t2_v11_score.py`（v0.9 部署管线 + **3 独立实例取多数**，HB-032；判据：正 ≥1 检出且中位 ≥0.70，负全 <0.70） | 离线，需 v0.9.onnx |
| `clips` | `training/_t2_v11_clips.py`（15xx，件长即 clip，按音色交替 train/test 对半分） | 先跑 `score` |
| `feat` | `training/_t2_v11_features.py`（v0.9 基线 + 新件，正 ×5 / 负 ×1，HB-027 逐件流式） | 先跑 `clips` |
| `train` | `training/_t2_train_cn.py --training_config openWakeWord/train_config_v12.yaml`（steps 3000，`max_negative_weight 1`，HB-021） | **停 `:7860/:8080/:9880`** |
| `eval` | `training/_t2_verify_onnx.py <n> aili_xiya_v1.2`（阈值矩阵 + 边界 ≥3 实例） | 训练产物 |

**本驱动做的事**：按顺序跑，日志写 `.tmp/bats/v12_<step>.log`；`clips`/`feat` 前把脚本里的 `V11` 常量覆写为
`openWakeWord/output/aili_xiya_v1.2`（这两个脚本是 v1.1 写死的，不改它们的源文件）；每步跑完打印真实计数。

Run（由你在会话跑，训练前停服务）：
  .venv\Scripts\python.exe -X utf8 training\_t4_full_retrain.py --step all
  .venv\Scripts\python.exe -X utf8 training\_t4_full_retrain.py --step bg --step synth
"""
import argparse
import os
import subprocess
import sys
import urllib.request

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
OUT = os.path.join(ROOT, "openWakeWord", "output")
V12 = os.path.join(OUT, "aili_xiya_v1.2")
LOGDIR = os.path.join(ROOT, ".tmp", "bats")
PY = sys.executable
ENV = dict(os.environ, HF_ENDPOINT="https://hf-mirror.com",
           HF_HOME=os.path.join(ROOT, ".hf-cache"), HF_HUB_DISABLE_XET="1")
ORDER = ("bg", "synth", "score", "clips", "feat", "train", "eval")


def gsv_ready() -> bool:
    """True if :9880 answers ANY HTTP response. 2026-11-17 13:22 fix: the root path
    returns **404**, and `urllib` raises `HTTPError` for it, so the first version
    reported "service not ready" while the TTS service was live (4-lamp health said
    tts online). Any reply — 200, 404, 400 — means the server is listening.
    """
    import urllib.error
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:9880/", timeout=3):
            return True
    except urllib.error.HTTPError:
        return True  # server answered (404/400): listening
    except Exception:
        return False


def run(mod, argv, log, override=None) -> int:
    """Run one existing training script as a module, with V11 redirected to v1.2."""
    os.makedirs(LOGDIR, exist_ok=True)
    if override:
        # 2026-11-17 13:32 fix (records/2026-11-17-13-20-00.md): the first version did
        # `import mod` + `mod.V11 = V12` + `runpy.run_module(mod)`, and **runpy re-executes
        # the source**, so the patch was thrown away: clips/feat rc=0 but wrote into
        # aili_xiya_v1.1 (overwriting that version's npy and 15xx clips) while
        # aili_xiya_v1.2 stayed empty. The patched copy goes to .tmp/, so the original
        # scripts under training/ are never modified.
        src = os.path.join(ROOT, "training", f"{mod}.py")
        dst = os.path.join(LOGDIR, f"_t4_{mod}_v12.py")
        text = open(src, encoding="utf-8").read()
        new = "\n".join(l if not l.startswith("V11 =") else f"V11 = {V12!r}"
                        for l in text.splitlines())
        if new == text:
            print(f"[FAIL] {mod}.py 里没有 V11 行，拒绝假装重定向", flush=True)
            return 1
        open(dst, "w", encoding="utf-8").write(new + "\n")
        print(f"[run] patched copy {dst} -> {log}", flush=True)
        with open(log, "wb") as fh:
            return subprocess.call([PY, "-X", "utf8", dst], cwd=ROOT, env=ENV,
                                   stdout=fh, stderr=subprocess.STDOUT)
    code = (
        "import sys, runpy\n"
        f"sys.path.insert(0, {os.path.join(ROOT, 'training')!r})\n"
        f"sys.path.insert(0, {ROOT!r})\n"
        + f"sys.argv = ['{mod}.py'] + {argv!r}\n"
        + f"raise SystemExit(runpy.run_module('{mod}', run_name='__main__'))\n"
    )
    print(f"[run] {mod} {' '.join(argv)} -> {log}", flush=True)
    with open(log, "wb") as fh:
        return subprocess.call([PY, "-X", "utf8", "-c", code], cwd=ROOT,
                               env=ENV, stdout=fh, stderr=subprocess.STDOUT)


def step_bg() -> int:
    if not gsv_ready():
        print("[bg] :9880 未就绪 → make_speech 不能跑；make_noise 纯合成可跑", flush=True)
    log = os.path.join(LOGDIR, "v12_bg.log")
    code = (
        f"import sys\nsys.path.insert(0, {os.path.join(ROOT, 'openWakeWord')!r})\n"
        "import _make_background as mb\n"
        "mb.make_noise(24)\n"
        "mb.make_speech(30)\n"
    )
    with open(log, "wb") as fh:
        rc = subprocess.call([PY, "-X", "utf8", "-c", code], cwd=ROOT, env=ENV,
                             stdout=fh, stderr=subprocess.STDOUT)
    print(f"[bg] rc={rc} 日志 {log}", flush=True)
    return rc


def step_train() -> int:
    log = os.path.join(LOGDIR, "v12_train.log")
    os.makedirs(V12, exist_ok=True)
    print(f"[train] 训练前请停 :7860/:8080/:9880（你的既定口径）；日志 {log}", flush=True)
    with open(log, "wb") as fh:
        rc = subprocess.call([PY, "-X", "utf8", "training/_t2_train_cn.py",
                              "--training_config", "openWakeWord/train_config_v12.yaml"],
                             cwd=ROOT, env=ENV, stdout=fh, stderr=subprocess.STDOUT)
    print(f"[train] rc={rc}", flush=True)
    return rc


def step_eval() -> int:
    log = os.path.join(LOGDIR, "v12_eval.log")
    with open(log, "wb") as fh:
        rc = subprocess.call([PY, "-X", "utf8", "training/_t2_verify_onnx.py", "25",
                              "aili_xiya_v1.2"], cwd=ROOT, env=ENV,
                             stdout=fh, stderr=subprocess.STDOUT)
    print(f"[eval] rc={rc} 日志 {log}（与 v0.9 逐条比，任一条不如则不改 config）", flush=True)
    return rc


def counts(tag: str) -> None:
    for sub in ("positive_train", "positive_test", "negative_train", "negative_test"):
        d = os.path.join(V12, sub)
        n = len([f for f in os.listdir(d) if f.endswith(".wav")]) if os.path.isdir(d) else -1
        print(f"[counts] {tag} {sub}: {n} 件", flush=True)
    for name in ("positive_features_train.npy", "negative_features_train.npy",
                 "positive_features_test.npy", "negative_features_test.npy", "val_fp.npy"):
        p = os.path.join(V12, name)
        print(f"[counts] {tag} {name}: {'存在' if os.path.exists(p) else '缺'}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", action="append", choices=ORDER, required=True)
    steps = [s for s in ORDER if s in ap.parse_args().step]
    print(f"[plan] {steps}  V12 = {V12}", flush=True)
    for s in steps:
        if s == "bg":
            rc = step_bg()
        elif s == "synth":
            rc = run("_t2_v11_tts", [], os.path.join(LOGDIR, "v12_synth.log"))
        elif s == "score":
            rc = run("_t2_v11_score", [], os.path.join(LOGDIR, "v12_score.log"))
        elif s == "clips":
            os.makedirs(V12, exist_ok=True)
            rc = run("_t2_v11_clips", [], os.path.join(LOGDIR, "v12_clips.log"), override=True)
        elif s == "feat":
            rc = run("_t2_v11_features", [], os.path.join(LOGDIR, "v12_feat.log"), override=True)
        elif s == "train":
            rc = step_train()
        else:
            rc = step_eval()
        print(f"[step {s}] rc={rc}", flush=True)
        counts(s)
        if rc:
            print(f"[stop] step {s} 非 0，后续步骤不跑（不假装成功）", flush=True)
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
