from pathlib import Path
import time
import yaml
import numpy as np

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def _load_config():
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

_model = None
_model_device = None  # track what device the model is on

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None  # type: ignore

# Engine switch (2026-11-11, records/2026-11-11-20-34-04.md item 4): `stt.engine`
# picks the ASR backend — "whisper" (faster-whisper, default) or "sherpa"
# (sherpa-onnx Paraformer-zh, better on short Chinese utterances). Selectable from
# config.yaml **and from the web settings page** (`api_get_settings` returns the
# whole `stt` dict, `api_update_settings` merges it), so the user can flip engines
# without editing files. `stt.sherpa.model_dir` points at the downloaded model.
_sherpa_rec = None


def _engine() -> str:
    return _load_config()["stt"].get("engine", "whisper")


def _get_sherpa():
    global _sherpa_rec
    if _sherpa_rec is None:
        import os
        import sherpa_onnx

        sh = _load_config()["stt"].get("sherpa", {})
        md = sh["model_dir"]
        # sherpa-onnx 2.0.1 的签名是 from_paraformer(paraformer, tokens, num_threads, ...)
        # —— 没有 paraformer_model / language_hints 参数（实测 TypeError，见 2026-11-12 记录）
        _sherpa_rec = sherpa_onnx.OfflineRecognizer.from_paraformer(
            paraformer=os.path.join(md, sh.get("model_file", "model.int8.onnx")),
            tokens=os.path.join(md, sh.get("tokens_file", "tokens.txt")),
            num_threads=int(sh.get("num_threads", 2)),
            debug=False,
        )
        print(f"[STT] sherpa-onnx Paraformer loaded from {md}")
    return _sherpa_rec


def _energy_gate(audio: np.ndarray, sample_rate: int = 16000,
                threshold: float = 0.008, window_ms: int = 100,
                mode: str = "span") -> np.ndarray:
    """Silence skip for the sherpa path (records/2026-11-12-22-51-09.md).

    whisper 有 `vad_filter=True`，Paraformer 什么都没有 —— 含长静音的整段会让 sherpa
    吐乱码（上一批 A/B：whisper 3/6 vs sherpa 2/6，sim >= 0.8）。两种模式：

    - `mode="span"`（默认）：**只掐头尾静音**，保留第一个/最后一个 voiced 窗之间的一切，
      前后各留 100 ms。第 1 轮实测：`mode="concat"` 在 THR=0.015 下把已知集从 2/6 打到 1/6
      —— 逐窗拼接会在音节中间切（100 ms 窗会切掉轻声/擦音），丢掉上下文；
    - `mode="concat"`：按 `window_ms` 窗算 RMS，只保留 voiced 窗并拼接（逐件打分用）。

    全静音时返回原数组（不制造空输入）。"""
    window = max(1, int(sample_rate * window_ms / 1000))
    n = len(audio)
    voiced = []
    for i in range(0, n, window):
        seg = audio[i : i + window]
        if len(seg) < window * 0.3:
            continue
        if float(np.sqrt(np.mean(seg.astype(np.float32) ** 2))) > threshold:
            voiced.append(i)
    if not voiced:
        return audio
    if mode == "concat":
        return np.concatenate([audio[i : i + window] for i in voiced])
    pad = int(sample_rate * 0.1)
    a = max(0, voiced[0] - pad)
    b = min(n, voiced[-1] + window + pad)
    return audio[a:b]


def _sherpa_transcribe(audio: np.ndarray) -> str:
    """sherpa-onnx 2.0.1: OfflineStream 只有 `accept_waveform(sample_rate, samples)`，
    没有 `accept_audio`（实测 AttributeError）。`audio` 是 [-1,1] 的 float 数组，16 kHz。"""
    sh = _load_config()["stt"].get("sherpa", {})
    if sh.get("energy_gate", True):
        # 默认 0.008：第 1 轮 0.015 在 span 模式下把已知集从 2/6 打到 1/6（切掉轻声音节），
        # 第 3 轮 0.008 保住 2/6、乱码 0、耗时减半（tests/2026-11-12-22-51-09_cc/opinion.md）
        audio = _energy_gate(audio, threshold=float(sh.get("energy_threshold", 0.008)),
                             mode=sh.get("energy_mode", "span"))
    rec = _get_sherpa()
    stream = rec.create_stream()
    stream.accept_waveform(16000, np.asarray(audio, dtype=np.float32))
    rec.decode_stream(stream)
    return stream.result.text

def _get_model(force_cpu=False):
    global _model, _model_device
    if _model is not None and not force_cpu:
        return _model
    cfg = _load_config()
    stt = cfg["stt"]
    device = "cpu" if force_cpu else stt["device"]
    compute_type = "int8" if force_cpu else stt["compute_type"]
    try:
        _model = WhisperModel(stt["model"], device=device, compute_type=compute_type)
        _model_device = device
        print(f"[STT] Loaded {stt['model']} on {device}")
    except Exception as e:
        if device != "cpu":
            print(f"[STT] {device} failed to load ({e}), falling back to CPU")
            _model = WhisperModel(stt["model"], device="cpu", compute_type="int8")
            _model_device = "cpu"
            print(f"[STT] Loaded {stt['model']} on cpu")
        else:
            raise
    return _model

def _dump_audio(audio: np.ndarray, sample_rate: int = 16000) -> Path:
    """Write the captured audio to `.tmp/capture_<ts>.wav` (gitignored) so an ASR
    miss can be replayed offline against any engine — the only way to A/B
    whisper parameters vs. a candidate engine (records/2026-11-10-17-43-08.md)."""
    import wave
    import time as _time

    out_dir = Path(__file__).parent.parent / ".tmp"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"capture_{int(_time.time())}.wav"
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm)
    print(f"[STT] capture saved: {path.name} ({len(pcm) // 2 // sample_rate} s)")
    return path


def _trim_leading_silence(audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """Drop the leading quiet block (the mic opens right after the wake ack, so the
    clip starts with ~1 s of silence). Whisper small hallucinates on silent input,
    so the clip is cut to the first window above the speech threshold."""
    window = int(sample_rate * 0.1)
    for i in range(0, len(audio) - window, window):
        rms = float(np.sqrt(np.mean(audio[i : i + window] ** 2)))
        if rms > 0.015:
            keep = max(0, i - int(sample_rate * 0.1))
            return audio[keep:]
    return audio


def transcribe_audio(audio: np.ndarray) -> str:
    """Transcribe a float32 numpy audio array (16kHz mono) to text."""
    # language="en" was hardcoded here, so Chinese speech was decoded as English
    # fragments — a user utterance came back as literal "You" and the LLM answered
    # "Done." (see records/2026-11-08-18-54-18.md). Language now comes from
    # config.yaml stt.language (default zh; set null for auto-detect).
    stt = _load_config()["stt"]
    lang = stt.get("language", "zh")
    # initial_prompt biases the decoder: an explicit Simplified-Chinese prompt with
    # this project's vocabulary keeps whisper small from answering in Traditional
    # (observed: `[You] 我愛你`, `你能看得见屏幕吗？` → `你能看的就`) and stabilises
    # short utterances. Tunable via config.yaml stt.initial_prompt.
    prompt = stt.get("initial_prompt") or None
    audio = _trim_leading_silence(audio)
    if stt.get("engine", "whisper") == "sherpa":
        # Engine switch (records/2026-11-11-20-34-04.md 第 4 项): sherpa-onnx Paraformer
        # is a CPU-only path with no beam search; fall back to whisper if it fails so
        # a model-file problem never turns into an empty transcription.
        try:
            text = _sherpa_transcribe(audio)
            if text.strip():
                return text
            print("[STT] sherpa 空结果，回退 whisper")
        except Exception as e:
            print(f"[STT] sherpa 失败（{e}），回退 whisper")
    try:
        model = _get_model()
        segments, _ = model.transcribe(
            audio,
            beam_size=int(stt.get("beam_size", 10)),
            best_of=int(stt.get("best_of", 5)),
            vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt=prompt,
            language=lang,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
    except Exception as e:
        # If CUDA worked for loading but fails during inference, retry on CPU
        if _model_device != "cpu":
            print(f"[STT] {_model_device} transcription failed ({e}), reloading on CPU")
            try:
                model = _get_model(force_cpu=True)
                segments, _ = model.transcribe(
                    audio,
                    beam_size=int(stt.get("beam_size", 10)),
                    best_of=int(stt.get("best_of", 5)),
                    vad_filter=True,
                    condition_on_previous_text=False,
                    initial_prompt=prompt,
                    language=lang,
                )
                return " ".join(seg.text.strip() for seg in segments).strip()
            except Exception as e2:
                print(f"[STT] CPU transcription also failed: {e2}")
                return ""
        print(f"[STT] Transcription failed: {e}")
        return ""

# Global abort event — set by main.py so recording can be interrupted
_abort_event = None

def set_abort_event(event) -> None:
    """Register the global abort event so recording checks it."""
    global _abort_event
    _abort_event = event

def record_until_silence(
    sample_rate: int = 16000,
    silence_threshold: float = 0.012,
    max_seconds: int = 30,
    no_speech_seconds: float = 2.0,
) -> np.ndarray:
    """Record microphone audio until silence is detected. Returns float32 array.
    Waits for speech to start before counting silence.
    Exits after `no_speech_seconds` if no speech is ever heard (records/2026-11-10-21-02-16:
    a wake triggered by noise peaks 0.736/0.799, VAD never saw speech, so the capture
    ran the full 30 s and transcribed to nothing).
    Can be interrupted via the abort event (Esc key)."""
    import sounddevice as sd

    chunk = int(sample_rate * 0.3)  # 300ms chunks
    recording = []
    silent_chunks = 0
    # 10 chunks = 3.0s of silence to end the capture. At 7 chunks (2.1s) a normal
    # mid-sentence pause ended the recording, so the user's sentence was cut off
    # (records/2026-11-08-20-44-17).
    silent_chunks_needed = 10  # ~2.1s of silence to stop
    heard_speech = False
    speech_threshold = 0.015  # louder than silence — confirms user is talking
    # 2 s without any chunk over speech_threshold = nobody is speaking; stop early.
    no_speech_chunks_needed = max(1, int(round(no_speech_seconds / 0.3)))

    _start = time.time()
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32") as stream:
        while True:
            # Check abort every chunk (~300ms), but ignore the flag for the
            # first 1.5s. Traced live (records/2026-11-08-19-25-48.md, job pwsh-46):
            # the flag is set right at the start of the turn (echo of her own ack /
            # the user's wake word), so `Recording aborted.` fired on the first
            # chunk and the capture was 0.3s → "我没听清，请再说一遍。". The user's
            # sentence needs ~1.5s before an abort is meaningful.
            if _abort_event and _abort_event.is_set() and time.time() - _start > 1.5:
                print("[STT] Recording aborted.")
                break

            data, _ = stream.read(chunk)
            flat = data.flatten()
            recording.append(flat)
            rms = float(np.sqrt(np.mean(flat ** 2)))

            if rms >= speech_threshold:
                if not heard_speech:
                    print(f"[STT] Speech detected (rms={rms:.4f})")
                heard_speech = True
                silent_chunks = 0
            elif heard_speech and rms < silence_threshold:
                silent_chunks += 1

            if heard_speech and silent_chunks >= silent_chunks_needed:
                print("[STT] Silence detected, stopping recording.")
                break
            if not heard_speech and len(recording) >= no_speech_chunks_needed:
                print(f"[STT] No speech in {no_speech_seconds}s, stopping early "
                      f"(max rms={max(float(np.sqrt(np.mean(c ** 2))) for c in recording):.4f}).")
                break
            if len(recording) * chunk >= max_seconds * sample_rate:
                print(f"[STT] Max recording time reached ({max_seconds}s)")
                break

    if not recording:
        return np.zeros(chunk, dtype=np.float32)
    audio = np.concatenate(recording)
    try:
        _dump_audio(audio, sample_rate)
    except Exception as e:
        print(f"[STT] capture dump failed: {e}")
    return audio
