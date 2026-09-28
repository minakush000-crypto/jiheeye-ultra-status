"""Stage 1: turn the owner's own raw clips into one clean voice sample for cloning.

raw clip(s) (mp4/mp3/m4a/wav) -> mono 44.1 kHz wav -> [optional Demucs vocal split]
-> spectral noise gate -> loudness normalize -> assets/voice/voice_sample.wav
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

from .common import StageError, cached, duration_of, log, sh, sha256_of, stamp

STAGE = "voice_prep"


def _demucs_vocals(wav: Path, work: Path) -> Path:
    if shutil.which("demucs") is None:
        raise StageError("voice.prep.demucs is true but the `demucs` command is not installed "
                         "(pip install demucs). Set demucs: false if your clips have no music.")
    sh(["demucs", "--two-stems=vocals", "-o", str(work / "demucs"), str(wav)], STAGE)
    out = work / "demucs" / "htdemucs" / wav.stem / "vocals.wav"
    if not out.exists():
        raise StageError(f"Demucs ran but {out} is missing")
    return out


def _denoise(src: Path, dst: Path, strength: float) -> None:
    import noisereduce as nr

    data, sr = sf.read(str(src), always_2d=False)
    if data.ndim > 1:
        data = data.mean(axis=1)
    clean = nr.reduce_noise(y=data.astype(np.float32), sr=sr, stationary=True, prop_decrease=strength)
    sf.write(str(dst), clean, sr, subtype="PCM_16")


def run(cfg: dict, root: Path, work_dir: Path | None = None) -> Path:
    """work_dir overrides root/'work' (brief 01 job 4: real runs put work/ on
    the D: scratch tree; tests pass nothing and use their temp root)."""
    pcfg = cfg["voice"]["prep"]
    sources = [root / s for s in pcfg["source_clips"]]
    missing = [str(s) for s in sources if not s.exists()]
    if missing:
        raise StageError(f"Source clips not found: {missing}. Put your own recordings in pipeline/assets/voice/raw/")

    out = root / "assets" / "voice" / "voice_sample.wav"
    key = sha256_of(*sources, pcfg)
    if cached(out, key):
        log(STAGE, f"cached -> {out}")
        return out

    work = (work_dir / "voice_prep") if work_dir else (root / "work" / "voice_prep")
    work.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1. decode every clip to mono 44.1k wav and join them
    parts = []
    for i, s in enumerate(sources):
        w = work / f"src_{i}.wav"
        sh(["ffmpeg", "-y", "-i", str(s), "-vn", "-ac", "1", "-ar", "44100", str(w)], STAGE)
        parts.append(w)
    joined = work / "joined.wav"
    if len(parts) == 1:
        shutil.copy(parts[0], joined)
    else:
        lst = work / "list.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
        sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], STAGE)

    # 2. optional music removal
    stage_in = _demucs_vocals(joined, work) if pcfg.get("demucs", False) else joined

    # 3. hiss/hum removal
    den = work / "denoised.wav"
    _denoise(stage_in, den, float(pcfg.get("denoise_strength", 0.85)))

    # 4. loudness normalize and cap length
    max_s = float(pcfg.get("max_seconds", 180))
    sh(["ffmpeg", "-y", "-i", str(den), "-t", str(max_s),
        "-af", "silenceremove=start_periods=1:start_threshold=-45dB,loudnorm=I=-18:TP=-2:LRA=11",
        "-ac", "1", "-ar", "44100", str(out)], STAGE)

    dur = duration_of(out)
    min_s = float(pcfg.get("min_seconds", 30))
    if dur < min_s:
        raise StageError(f"Clean voice sample is {dur:.1f}s, below min_seconds={min_s}. Add more of your own speech.")
    stamp(out, key)
    log(STAGE, f"voice sample ready: {out} ({dur:.1f}s)")
    return out
