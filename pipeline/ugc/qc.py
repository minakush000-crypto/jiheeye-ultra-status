"""Stage 8: machine quality gate on the final file. Any FAIL -> exit code 1.
Checks the artifact itself (ffprobe/ffmpeg), never a stage's own success message.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .common import ffprobe_json, log

STAGE = "qc"


def _measure(path: Path, filt: str) -> str:
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-filter_complex", filt,
                           "-f", "null", "-"], capture_output=True, text=True).stderr


def run(cfg: dict, final: Path, vo: Path, srt: Path) -> list[tuple[str, bool, str]]:
    oc = cfg["output"]
    results: list[tuple[str, bool, str]] = []

    def check(name, ok, detail):
        results.append((name, bool(ok), detail))

    if not final.exists():
        check("file exists", False, str(final))
        return results
    info = ffprobe_json(final)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    vo_dur = float(ffprobe_json(vo)["format"]["duration"])

    check("video stream", v is not None, v["codec_name"] if v else "none")
    check("audio stream", a is not None, a["codec_name"] if a else "none")
    if v:
        check("resolution", (v["width"], v["height"]) == (oc["width"], oc["height"]), f"{v['width']}x{v['height']}")
        num, den = map(int, v["r_frame_rate"].split("/"))
        check("fps", abs(num / den - oc["fps"]) < 0.01, f"{num/den:.2f}")
        check("pix_fmt yuv420p", v.get("pix_fmt") == "yuv420p", v.get("pix_fmt", "?"))
    check("duration matches voiceover", abs(dur - vo_dur) <= 0.35, f"final {dur:.2f}s vs vo {vo_dur:.2f}s")
    check("duration within platform max", dur <= oc["max_seconds"], f"{dur:.1f}s <= {oc['max_seconds']}s")

    ebu = _measure(final, "[0:a]ebur128")
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", ebu)
    lufs = float(m[-1]) if m else None
    check("loudness", lufs is not None and abs(lufs - oc["loudness_lufs"]) <= 1.5,
          f"{lufs} LUFS (target {oc['loudness_lufs']})")

    bd = _measure(final, "[0:v]blackdetect=d=0.8:pix_th=0.10")
    blacks = re.findall(r"black_start:([\d.]+)", bd)
    check("no black gaps >0.8s", not blacks, f"black at {blacks}" if blacks else "none")

    sd = _measure(final, "[0:a]silencedetect=n=-45dB:d=1.5")
    sil = re.findall(r"silence_start: ([\d.]+)", sd)
    check("no dead air >1.5s", not sil, f"silence at {sil}" if sil else "none")

    n_caps = srt.read_text(encoding="utf-8").count("-->") if srt.exists() else 0
    check("captions present", n_caps > 0, f"{n_caps} blocks")

    size_mb = final.stat().st_size / 1e6
    check("file size sane", 0.5 < size_mb < float(oc.get("max_mb", 250)), f"{size_mb:.1f} MB")

    width = max(len(r[0]) for r in results)
    for name, ok, detail in results:
        log(STAGE, f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {detail}")
    return results
