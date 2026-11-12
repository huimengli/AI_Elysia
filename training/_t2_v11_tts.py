r"""多音色 TTS 生成（2026-11-12 18:49 需求，records/2026-11-12-18-49-50.md）。

三组音色，同一套文本：

- **A = GPT-SoVITS 爱莉希雅本人音色**（`config.yaml` 的 `tts.gptsovits.ref_audio_path` + `prompt_text`）
  → 与真唤醒同音色，用于**基线对照**（既往结论：同音色近音词峰值 0.796-0.839，高于真人唤醒整件，不能作负样本）
- **B = GPT-SoVITS 用户本人音色**（参考音频 = 真人录音，`prompt_text` = 文件名真值）
- **C..F = Kokoro-82M 中文音色**（`lang_code="z"`，本地 `.hf-cache` 已缓存 `zf_xiaoxiao` / `zf_xiaoni` /
  `zf_xiaoyi` / `zm_yunyang` / `zm_yunxi` / `zm_yunjian`）

输出 16 kHz 单声道 int16 wav 到 `.tmp/v11tts/<音色>__<slug>.wav`。**先测后训**：本脚本只生成，打分由
`training/_t2_v11_score.py` 做（v0.9 部署管线 + HB-032 三次实例）。入库判据（本批新增，与 Q14 推荐一致）：
**正样本峰值 >=0.70 才入库；负样本峰值落在低分区（3 实例一致 <0.70）才入库，>=0.70 不入库。**

Run:
  生成：.venv\Scripts\python.exe training\_t2_v11_tts.py            # 全量（GSV + Kokoro）
  只测：.venv\Scripts\python.exe training\_t2_v11_tts.py --smoke     # 每音色 1 条，验证通路
"""
import io
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
SR = 16000
OUT = os.path.join(ROOT, ".tmp", "v11tts")
REC = r"C:\Users\楼听\Documents\录音"
API_URL = "http://127.0.0.1:9880/tts"
SET_GPT = "http://127.0.0.1:9880/set_gpt_weights"
SET_SOVITS = "http://127.0.0.1:9880/set_sovits_weights"
# 爱莉希雅现役权重（GPT-SoVITS-main/GPT_SoVITS/configs/tts_infer.yaml custom 节，相对 GPT-SoVITS-main 工作目录）
ELYA_GPT = r"GPT_weights_v2\【GPT2.0】Elysia-e20.ckpt"
ELYA_SOVITS = r"SoVITS_weights_v2\【GPT2.0】Elysia_e24_s13080.pth"
# 2026-11-12 19:23 新权重：流萤（Firefly）完整 GPT-SoVITS 包
FL_DIR = r"F:\BaiduNetdiskDownload\流萤"
FL_GPT = os.path.join(FL_DIR, "GPT_weights", "Firefly-e15.ckpt")
FL_SOVITS = os.path.join(FL_DIR, "SoVITS_weights", "Firefly_e16_s1872.pth")
# 参考音频文件名尾部带空格，必须用 os.listdir 精确解析（直接拼路径会 not exists）
FL_REF_SPEC = [
    ("钟表小子的雕像怎么了吗？", "钟表小子的雕像怎么了吗？"),
    ("有棱有角的小鸟，可我好像什么都没看见哎。", "有棱有角的小鸟，可我好像什么都没看见哎。"),
    ("我最喜欢这家店的橡木蛋糕卷，每天都要吃一个。", "我最喜欢这家店的橡木蛋糕卷，每天都要吃一个。"),
]


def resolve_ref(spec):
    d = os.path.join(FL_DIR, "参考音频")
    for n in os.listdir(d):
        if n.startswith(spec[0]):
            return os.path.join(d, n), spec[1]
    raise FileNotFoundError(spec[0])
REF_ELYA = r"F:\BaiduNetdiskDownload\爱莉希雅\【GPT-SoVITS 2.0】爱莉希雅\参考音频\【感动】欸嘿，大家笑一笑，好吗？.wav"
PROMPT_ELYA = "欸嘿，大家笑一笑，好吗？"
# 2026-11-12 20:03 新权重：白厄（下载方称 v2ProPlus，版本由权重内容自动判定）
BE_DIR = r"F:\BaiduNetdiskDownload\白厄"
BE_GPT = os.path.join(BE_DIR, "白厄-e10.ckpt")        # 155,313,312 B
BE_SOVITS = os.path.join(BE_DIR, "白厄_e10_s680.pth")  # 172,765,299 B（>v2 的 106 MB）
BE_REF_DIR = os.path.join(BE_DIR, "reference_audios", "中文", "emotions")


def be_refs():
    """白厄 参考音频：文件名 = 【情绪】+台词，台词即 prompt_text；尾部可能有空格，用 listdir 原样取。"""
    out = []
    for n in sorted(os.listdir(BE_REF_DIR)):
        if not n.endswith(".wav"):
            continue
        stem = n[:-4]
        parts = stem.split("】", 1)
        text = (parts[1] if len(parts) > 1 else stem).strip()
        out.append((os.path.join(BE_REF_DIR, n), text))
    return out
# 用户本人音色参考：真人录音，文件名即真值（GSV 要求参考音频 3~10 s）
REF_USER_WAV = os.path.join(ROOT, ".tmp", "v11tts", "ref_user.wav")
PROMPT_USER = "我没听清，请再说一遍"

TEXTS = [
    ("pos", "ai_li_xi_ya", "爱莉希雅"),
    ("pos", "pos_browser", "爱莉希雅，帮我打开浏览器"),
    ("pos", "pos_hello", "你好啊爱莉希雅，你在干什么呢"),
    ("neg_near", "ai_li_an_na", "爱丽安娜"),
    ("neg_near", "ai_li_si", "爱丽丝"),
    ("neg_near", "mi_xi_ya", "米希雅"),
    ("neg_near", "ai_li_ya", "爱莉雅"),
    ("neg_near", "mi_ya_xi", "米雅希"),
    ("neg_near", "xi_ya", "希雅"),
    ("neg_near", "xi_ya_lao_shi", "希雅老师"),
    ("neg_near", "ai_ni_lao_shi", "爱你老师"),
    ("neg_near", "ya_shi_lan_dai", "雅诗兰黛"),
    ("neg_near", "mi_ya", "米雅"),
    ("neg_comp", "tian_mao_jing_ling", "天猫精灵"),
    ("neg_comp", "xiao_ai_tong_xue", "小爱同学"),
    ("neg_comp", "xiao_du_xiao_du", "小度小度"),
    ("neg_comp", "jia_wei_si", "贾维斯"),
    ("neg_unrel", "unrel_monitor", "小爱同学，打开手机监控"),
    ("neg_unrel", "unrel_hear", "我没听清，请再说一遍"),
    ("neg_unrel", "unrel_love_you", "我爱你"),
]

KOKORO_VOICES = ["zf_xiaoxiao", "zf_xiaoni", "zm_yunyang", "zm_yunxi"]


def decode_m4a_to_wav(src, dst, sr=SR):
    import av
    res = av.AudioResampler(format="s16", layout="mono", rate=sr)
    out = []
    with av.open(src) as c:
        for f in c.decode(c.streams.audio[0]):
            for r in res.resample(f):
                out.append(r.to_ndarray().reshape(-1))
    a = np.concatenate(out).astype(np.int16)
    with wave.open(dst, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(a.tobytes())
    return a


def set_weights(kind, path):
    """运行时换权重：/set_gpt_weights、/set_sovits_weights（api_v2.py:555/567）。"""
    url = (SET_GPT if kind == "gpt" else SET_SOVITS)
    q = urllib.parse.urlencode({"weights_path": path})
    try:
        with urllib.request.urlopen(f"{url}?{q}", timeout=300) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        # 权重版本判定/加载失败的真正原因在正文里（v2ProPlus 判定来自 ckpt 内容，不靠文件名）
        raise RuntimeError(f"{kind} 权重加载失败 HTTP {e.code}: {e.read().decode('utf-8', 'replace')}") from None
    print(f"[weights] {kind} <- {os.path.basename(path)}: {body[:80]}", flush=True)
    return body


def gsv(text, ref_audio, prompt_text):
    params = {"text": text, "text_lang": "zh", "ref_audio_path": ref_audio,
              "prompt_lang": "zh", "prompt_text": prompt_text, "speed_factor": 1.0,
              "text_split_method": "cut5"}
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=180) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        # api_v2 在参考音频/权重加载失败时返回 400，正文里有真实原因，必须读出来
        body = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {body}") from None
    with wave.open(io.BytesIO(data), "rb") as w:
        rate = w.getframerate()
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    if rate != SR:
        # av.AudioResampler 在本机对 24k->16k 单帧路径不可靠（无 flush），改用 scipy 多相重采样
        from scipy.signal import resample_poly
        g = np.gcd(int(rate), SR)
        pcm = resample_poly(pcm.astype(np.float32), SR // g, rate // g)
        pcm = np.clip(pcm, -32768, 32767).astype(np.int16)
    return pcm


def save(pcm, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name + ".wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(pcm, -32768, 32767).astype(np.int16).tobytes())
    return p


def kokoro_pipeline():
    from kokoro import KModel, KPipeline
    model = KModel(repo_id="hexgrad/Kokoro-82M").to("cpu").eval()
    return KPipeline(lang_code="z", repo_id="hexgrad/Kokoro-82M", model=model)


def kokoro_synth(pipe, voice_name, text):
    import torch
    vdir = os.path.join(ROOT, ".hf-cache", "hub", "models--hexgrad--Kokoro-82M",
                        "snapshots")
    vp = None
    for d in os.listdir(vdir):
        cand = os.path.join(vdir, d, "voices", voice_name + ".pt")
        if os.path.exists(cand):
            vp = cand
            break
    voice = torch.load(vp, weights_only=True)
    chunks = []
    for _, _, audio in pipe(text, voice=voice, speed=1.0):
        if audio is not None:
            chunks.append(audio)
    if not chunks:
        return np.zeros(0, np.int16)
    combined = np.concatenate(chunks)
    return (combined * 32767).astype(np.int16)


def main() -> int:
    smoke = "--smoke" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(REF_USER_WAV):
        decode_m4a_to_wav(os.path.join(REC, "'我没听清,请再说一遍'.m4a"), REF_USER_WAV)
        print(f"[ref] 用户音色参考 -> {REF_USER_WAV}", flush=True)

    jobs = TEXTS[:1] if smoke else TEXTS
    n = 0

    def gate(name):
        return only is None or only == name

    # A: GPT-SoVITS 爱莉希雅（同音色基线）
    if gate("elya"):
        for kind, slug, text in jobs:
            try:
                pcm = gsv(text, REF_ELYA, PROMPT_ELYA)
                p = save(pcm, f"elya__{kind}__{slug}")
                print(f"[elya] {kind} {slug} {len(pcm)/SR:.2f}s rms={np.sqrt(np.mean(pcm.astype(np.float32)**2)):.0f} -> {os.path.basename(p)}", flush=True)
                n += 1
            except Exception as e:
                print(f"[elya] {kind} {slug} 失败: {e}", flush=True)

    # B: GPT-SoVITS 流萤（新权重，运行时切换 + 切回）
    if gate("firefly"):
        set_weights("gpt", FL_GPT)
        set_weights("sovits", FL_SOVITS)
        for i, (kind, slug, text) in enumerate(jobs):
            ref, prompt = resolve_ref(FL_REF_SPEC[i % len(FL_REF_SPEC)])
            try:
                pcm = gsv(text, ref, prompt)
                p = save(pcm, f"firefly__{kind}__{slug}")
                print(f"[firefly] {kind} {slug} {len(pcm)/SR:.2f}s rms={np.sqrt(np.mean(pcm.astype(np.float32)**2)):.0f} -> {os.path.basename(p)}", flush=True)
                n += 1
            except Exception as e:
                print(f"[firefly] {kind} {slug} 失败: {e}", flush=True)
        set_weights("gpt", ELYA_GPT)
        set_weights("sovits", ELYA_SOVITS)

    # B2: GPT-SoVITS 白厄（2026-11-12 20:03 新权重，下载方称 v2ProPlus；版本由权重内容判定）
    if gate("bai_e"):
        set_weights("gpt", BE_GPT)
        set_weights("sovits", BE_SOVITS)
        refs = be_refs()
        for i, (kind, slug, text) in enumerate(jobs):
            ref, prompt = refs[i % len(refs)]
            try:
                pcm = gsv(text, ref, prompt)
                p = save(pcm, f"bai_e__{kind}__{slug}")
                print(f"[bai_e] {kind} {slug} {len(pcm)/SR:.2f}s rms={np.sqrt(np.mean(pcm.astype(np.float32)**2)):.0f} -> {os.path.basename(p)}", flush=True)
                n += 1
            except Exception as e:
                print(f"[bai_e] {kind} {slug} 失败: {e}", flush=True)
        set_weights("gpt", ELYA_GPT)
        set_weights("sovits", ELYA_SOVITS)

    # C: GPT-SoVITS 用户本人音色 —— **实测不可用，跳过**（2026-11-12 19:47 实测）
    # 爱莉希雅权重 + 真人参考音频（`我没听清` 6.87 s，prompt_text = 文件名真值）：GPT 在参考文本不在
    # 训练语料时不收尾，单件产出 60.26 s / 63.28 s 失控音频，第 3 件直接 timed out。
    # 结论：**用「foreign 参考音频 + 目标语种微调权重」做真人音色克隆在本机不可行**，本音色不入库。
    SKIP_USER = True
    if not SKIP_USER:
        for kind, slug, text in jobs:
            try:
                pcm = gsv(text, REF_USER_WAV, PROMPT_USER)
                p = save(pcm, f"user__{kind}__{slug}")
                print(f"[user] {kind} {slug} {len(pcm)/SR:.2f}s rms={np.sqrt(np.mean(pcm.astype(np.float32)**2)):.0f} -> {os.path.basename(p)}", flush=True)
                n += 1
            except Exception as e:
                print(f"[user] {kind} {slug} 失败: {e}", flush=True)
    else:
        print("[user] 跳过：爱莉希雅权重 + 真人参考音频产出 60 s 失控音频（实测），不入库", flush=True)

    # C..F: Kokoro 中文音色
    if gate("kokoro"):
        pipe = kokoro_pipeline()
        for v in KOKORO_VOICES:
            for kind, slug, text in jobs:
                try:
                    pcm = kokoro_synth(pipe, v, text)
                    p = save(pcm, f"k_{v}__{kind}__{slug}")
                    print(f"[{v}] {kind} {slug} {len(pcm)/SR:.2f}s rms={np.sqrt(np.mean(pcm.astype(np.float32)**2)):.0f} -> {os.path.basename(p)}", flush=True)
                    n += 1
                except Exception as e:
                    print(f"[{v}] {kind} {slug} 失败: {e}", flush=True)

    print(f"\n生成完成：{n} 件 -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
