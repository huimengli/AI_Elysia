from __future__ import annotations
from pathlib import Path
import threading
import time
import numpy as np
import yaml

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def _load_config():
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Mic pause/resume for STT recording ───
# When STT needs to record, it pauses the wake word mic so both don't fight
# over the same hardware device. Wake word detection resumes after recording.

_mic_pause = threading.Event()


def pause_wake_mic() -> None:
    """Pause wake word mic stream to free it for STT recording."""
    _mic_pause.set()


def resume_wake_mic() -> None:
    """Resume wake word mic stream after STT recording is done."""
    _mic_pause.clear()


# ─── Model/threshold hot reload (records/2026-11-13-00-12-17.md 第 4 项) ───
# The settings page writes model + threshold into config.yaml, then raises this
# flag; the listening loop rebuilds the Model on its next iteration. The mic
# stream is reused (chunk_size stays 1280), so only the ONNX graph + weights swap.
_reload = threading.Event()


def request_wake_reload() -> None:
    """Ask the listening loop to re-read wake_word (model + threshold) from config."""
    _reload.set()


# ─── Live wake-word state, read by GET /api/health (2026-11-09-20-35-43) ───
# Everything the wake loop knows about itself, published for the UI's 唤醒 lamp.
# Model construction sets online; the mic-pause window (STT holds the device)
# sets listening=False; each chunk updates score, the rolling window updates
# peak, and a threshold crossing updates last_detect.
state = {
    "online": False,
    "listening": False,
    "model": "",
    "threshold": None,
    "score": 0.0,
    "peak": 0.0,
    "last_detect": 0.0,
}


def listen_for_wake_word(callback) -> None:
    """
    Continuously listen for wake word. Calls callback() when detected.
    Blocking — runs forever in the calling thread.

    - IDLE: wake word → start callback (listen for command)
    - BUSY: wake word → abort (stop talking/processing)

    Short cooldown after normal wake prevents "Yes?" echo from re-triggering.
    Mic is paused/resumed via pause_wake_mic()/resume_wake_mic() during STT.
    """
    import pyaudio
    from openwakeword.model import Model

    cfg = _load_config()["wake_word"]
    oww = Model(wakeword_models=[cfg["model"]], inference_framework="onnx")
    # openwakeword keys predictions by the model filename stem for local model
    # files (e.g. "aili_xiya_v0.1" for .../aili_xiya_v0.1.onnx) but by the raw
    # name for built-in models (which may themselves contain a dot, e.g.
    # "hey_jarvis_v0.1"). Mirror that resolution here.
    _model_spec = cfg["model"]
    _model_key = Path(_model_spec).stem if Path(_model_spec).exists() else _model_spec
    state["online"] = True
    state["model"] = Path(_model_spec).name
    state["threshold"] = cfg["threshold"]
    state["listening"] = True

    audio = pyaudio.PyAudio()
    mic = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=cfg["chunk_size"],
    )

    _busy = threading.Lock()
    _ignore_until = [0.0]
    _peak = 0.0
    _last_detect = [0.0]
    _last_log = time.time()

    print("[爱莉希雅] Listening for wake word...")
    try:
        while True:
            # ── Hot reload: settings changed model and/or threshold ──
            if _reload.is_set():
                _reload.clear()
                new_cfg = _load_config()["wake_word"]
                new_spec = new_cfg["model"]
                new_key = Path(new_spec).stem if Path(new_spec).exists() else new_spec
                if new_key != _model_key:
                    try:
                        new_model = Model(wakeword_models=[new_spec], inference_framework="onnx")
                    except Exception as e:
                        # A bad/missing model must not kill listening — keep the old one.
                        print(f"[Wake] reload failed ({e}); keeping {state['model']}")
                    else:
                        oww = new_model
                        _model_key = new_key
                        cfg = new_cfg
                        state["model"] = Path(new_spec).name
                        state["threshold"] = new_cfg["threshold"]
                        oww.reset()
                        # Model() starts with a random-seeded feature buffer (HB-032) and
                        # needs 1 s warmup; ignore hits during the swap.
                        _ignore_until[0] = time.time() + 2.0
                        _peak = 0.0
                        print(f"[Wake] reloaded {state['model']} / threshold {state['threshold']}")
                else:
                    cfg = new_cfg
                    state["threshold"] = new_cfg["threshold"]
                    print(f"[Wake] threshold -> {cfg['threshold']}")
                continue

            # ── Mic pause: STT is recording, yield the hardware ──
            if _mic_pause.is_set():
                state["listening"] = False
                if mic.is_active():
                    mic.stop_stream()
                    print("[Wake] Mic paused for STT recording.")
                while _mic_pause.is_set():
                    time.sleep(0.05)
                # Resume after STT is done
                mic.start_stream()
                state["listening"] = True
                oww.reset()  # Clear stale predictions
                # The user usually keeps talking right after the capture; that speech
                # scores above the threshold and used to abort the turn 1-2s later
                # (records/2026-11-08-20-44-17). Give the turn 4s of grace.
                _ignore_until[0] = time.time() + 4.0
                print("[Wake] Mic resumed.")
                continue

            try:
                pcm = np.frombuffer(mic.read(cfg["chunk_size"]), dtype=np.int16)
            except Exception:
                time.sleep(0.05)
                continue

            try:
                predictions = oww.predict(pcm)
            except Exception as e:
                # Transient allocation failure (e.g. MemoryError under RAM
                # pressure) must not kill the whole process — back off and
                # keep listening.
                print(f"[Wake] predict failed ({e}); continuing")
                time.sleep(0.5)
                continue
            score = predictions.get(_model_key, 0)
            state["score"] = float(score)

            # Throttled sensitivity log. Without it a non-triggering wake is
            # indistinguishable from a dead mic (records/2026-11-08-19-25-48.md).
            _peak = max(_peak, score)
            state["peak"] = float(_peak)
            if time.time() - _last_log >= 3.0:
                print(f"[Wake] peak {_peak:.3f} / threshold {cfg['threshold']}")
                _peak = 0.0
                _last_log = time.time()

            if score < cfg["threshold"]:
                continue

            oww.reset()
            now = time.time()
            state["last_detect"] = now

            # Skip if in cooldown window (prevents echo re-trigger)
            if now < _ignore_until[0]:
                continue

            if _busy.locked():
                # BUSY: wake word = stop everything — unless the pipeline is
                # mid-recording: then the trigger comes from the same mic we
                # are recording (the user's own speech / ambient noise), not
                # a new turn, so aborting would kill our own capture and any
                # in-flight web turn.
                from jarvis.main import abort_all, is_recording
                # The 0.3s-cut evidence (records/2026-11-08-19-25-48.md) shows this
                # branch firing while the flag was already True, so log the decision.
                print(f"[Wake] barge-in score={score:.3f} recording={is_recording()}")
                if is_recording():
                    _ignore_until[0] = now + 2.0
                else:
                    # Abort needs TWO detections inside 1.0s. A single hit is the user's
                    # own speech crossing the 0.65 threshold (measured peaks 0.65-0.78),
                    # and one-hit aborts produced the 2-3 「已停止」 bubbles per turn.
                    if now - _last_detect[0] <= 1.0:
                        _last_detect[0] = 0.0
                        _ignore_until[0] = now + 4.0
                        abort_all()
                        print("[爱莉希雅] Stopped. (voice interrupt)")
                    else:
                        _last_detect[0] = now
                        _ignore_until[0] = now + 0.6
                        print("[Wake] barge-in candidate 1/2 (no abort yet)")
            else:
                from jarvis.main import is_speaking, stop_speaking
                if is_speaking():
                    # TTS is playing — her own voice echoing into the mic is
                    # not a user. Stop the speech and skip the pipeline.
                    stop_speaking()
                    _ignore_until[0] = now + 3.0
                    continue
                # IDLE: normal wake — cooldown to skip her own ack ("在。") and the
                # user's immediately-following speech. 2.0s was too short: the ack
                # plus the start of the user's sentence re-triggered the model inside
                # the turn (barge-in → abort → 0.3s capture; traced live in
                # records/2026-11-08-19-25-48.md). 5.0s covers ack + first sentence.
                _ignore_until[0] = now + 5.0

                def _run():
                    with _busy:
                        callback()

                t = threading.Thread(target=_run, daemon=True)
                t.start()
    finally:
        mic.stop_stream()
        mic.close()
        audio.terminate()
