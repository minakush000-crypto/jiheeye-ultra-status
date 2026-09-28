"""Stage 6: product B-roll clips, one paid image-to-video call per broll scene."""
from __future__ import annotations

from pathlib import Path

from . import replicate_io as rio
from .common import StageError, cached, log, sha256_of, stamp

STAGE = "broll"


def run(cfg: dict, root: Path, run_dir: Path, script: dict) -> dict[str, Path]:
    bc = cfg["broll"]
    clips: dict[str, Path] = {}
    scenes = [s for s in script["scenes"] if s["type"] == "broll"]
    if not scenes:
        return clips
    validated = False
    for s in scenes:
        img = root / s["image"]
        if not img.exists():
            raise StageError(f"B-roll scene {s['id']}: product image not found: {img}")
        out = run_dir / f"broll_{s['id']}.mp4"
        key = sha256_of(img, s["prompt"], bc)
        if cached(out, key):
            log(STAGE, f"cached {out.name}")
            clips[s["id"]] = out
            continue
        if not validated:
            rio.validate(bc["model"], bc["inputs"], STAGE)
            validated = True
        inputs, handles = rio.build_inputs(bc["inputs"], {"image": img}, {"prompt": s["prompt"]})
        try:
            rio.run_to_file(bc["model"], inputs, out, STAGE)
        finally:
            for h in handles:
                h.close()
        stamp(out, key)
        clips[s["id"]] = out
    return clips
