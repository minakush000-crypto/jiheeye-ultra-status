"""Stage 3: Somali voiceover in the cloned voice, with per-character timestamps.

One TTS call for the whole script (keeps delivery continuous). The character
alignment drives scene cut points and captions later.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import requests

from .common import StageError, cached, env, log, sha256_of, stamp

STAGE = "tts"
API = "https://api.elevenlabs.io"


def full_text(script: dict) -> str:
    return " ".join(s["text"].strip() for s in script["scenes"])


def run(cfg: dict, run_dir: Path, script: dict, voice_id: str) -> tuple[Path, Path]:
    tcfg = cfg["tts"]
    text = full_text(script)
    body = {
        "text": text,
        "model_id": tcfg.get("model_id", "eleven_v3"),
        "language_code": script.get("language", "so"),
        "output_format": "mp3_44100_128",
    }
    if tcfg.get("voice_settings"):
        body["voice_settings"] = tcfg["voice_settings"]

    audio = run_dir / "vo.mp3"
    align = run_dir / "alignment.json"
    key = sha256_of(body, voice_id)
    if cached(audio, key) and align.exists():
        log(STAGE, "cached voiceover")
        return audio, align

    log(STAGE, f"requesting TTS: {len(text)} chars, model={body['model_id']}, lang={body['language_code']}")
    r = requests.post(
        f"{API}/v1/text-to-speech/{voice_id}/with-timestamps",
        headers={"xi-api-key": env("ELEVENLABS_API_KEY"), "Content-Type": "application/json"},
        json=body, timeout=300,
    )
    if r.status_code != 200:
        raise StageError(f"ElevenLabs TTS failed {r.status_code}: {r.text[:500]}")
    data = r.json()
    audio.write_bytes(base64.b64decode(data["audio_base64"]))
    alignment = data.get("alignment") or data.get("normalized_alignment")
    if not alignment:
        raise StageError("TTS response has no alignment; cannot time scenes or captions")
    align.write_text(json.dumps({"text": text, **alignment}, ensure_ascii=False))
    stamp(audio, key)
    log(STAGE, f"voiceover -> {audio}")
    return audio, align
