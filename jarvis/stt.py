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
