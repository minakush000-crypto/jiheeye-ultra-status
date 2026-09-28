"""Stage 5: animate the avatar image with the full voiceover (one paid call)."""
from __future__ import annotations

from pathlib import Path

from . import replicate_io as rio
from .common import StageError, cached, duration_of, log, sha256_of, stamp

STAGE = "lipsync"


def run(cfg: dict, root: Path, run_dir: Path, vo: Path) -> Path:
    from .voice_clone import check_avatar_license
    log(STAGE, f"avatar license OK: {check_avatar_license(root.parent)}")
    lc = cfg["lipsync"]
    avatar = root / lc["avatar_image"]
    if not avatar.exists():
        raise StageError(f"Avatar image not found: {avatar}")
    vo_dur = duration_of(vo)
    if vo_dur > float(lc.get("max_audio_seconds", 60)):
        raise StageError(f"Voiceover is {vo_dur:.1f}s; {lc['model']} limit in config is {lc['max_audio_seconds']}s. Shorten the script.")

    out = run_dir / "avatar_full.mp4"
    key = sha256_of(avatar, vo, lc)
    if cached(out, key):
        log(STAGE, "cached avatar video")
        return out

    rio.validate(lc["model"], lc["inputs"], STAGE)
    inputs, handles = rio.build_inputs(lc["inputs"], {"avatar": avatar, "audio": vo}, {})
    try:
        rio.run_to_file(lc["model"], inputs, out, STAGE)
    finally:
        for h in handles:
            h.close()
    got = duration_of(out)
    if abs(got - vo_dur) > 1.0:
        log(STAGE, f"WARNING: avatar video {got:.2f}s vs voiceover {vo_dur:.2f}s; assembly will pad/trim")
    stamp(out, key)
    return out
