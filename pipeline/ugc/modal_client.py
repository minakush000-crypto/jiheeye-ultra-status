"""Client side of the Modal backend (brief 01 job 5).

Stages the ugc code and run inputs on volume jiheeye-build, calls the deployed
functions of app jiheeye-ultra, and saves outputs into the local tree. The
remote functions run the REAL ugc modules, so local and remote never drift;
this file is only staging + transport. Used by run.py (backend: modal) and
tests/test_modal.py (ephemeral app, no deploy needed).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import modal

from .common import ROOT, StageError, cached, log, sha256_of, stamp

APP_NAME = "jiheeye-ultra"
VOL_NAME = "jiheeye-build"
VOL_MOUNT = "/vol"          # mountpoint inside containers; used in spec paths
# batch_upload takes paths RELATIVE TO THE VOLUME ROOT (no /vol prefix):
# a "/vol/x" argument lands at /vol/vol/x inside the container (verified
# 2026-09-28: the first Modal test run created /vol/vol/jobs/...).
UPLOAD_ROOT = "jobs"


def _code_dir() -> str:
    """Staging copy of ugc/ without __pycache__ (batch_upload has no exclude)."""
    tmp = Path(tempfile.mkdtemp(prefix="ugc_code_")) / "ugc"
    shutil.copytree(ROOT / "ugc", tmp,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return str(tmp.parent)


def _volume():
    return modal.Volume.from_name(VOL_NAME, create_if_missing=True)


def _ephemeral(name: str):
    """Local function object for tests: runs via an ephemeral app (fresh code,
    no prior deploy). Imports pipeline/modal_app.py by path."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import modal_app
    return getattr(modal_app, name), getattr(modal_app, "app")


def _remote(name: str, spec: dict, ephemeral: bool) -> bytes:
    """Call a Modal function; wrap remote failures in StageError so a remote
    failure surfaces in the pipeline's error contract, not a raw traceback."""
    try:
        if ephemeral:
            fn, app = _ephemeral(name)
            with app.run():
                return fn.remote(spec)
        return modal.Function.from_name(APP_NAME, name).remote(spec)
    except StageError:
        raise
    except Exception as e:  # noqa: BLE001
        raise StageError(f"{name} (Modal) failed: {type(e).__name__}: {e}") from e


def _remove_volume_dir(job_rel: str) -> None:
    """Garbage-collect a finished job dir (code + intermediates + a duplicate
    of the output) so the volume does not grow without bound. Best effort:
    failures are logged and left for the next run."""
    try:
        subprocess.run(
            [sys.executable, "-m", "modal", "volume", "rm", "-r", VOL_NAME, job_rel],
            capture_output=True, text=True,
        )
    except OSError as e:
        log("modal_client", f"volume GC skipped for {job_rel}: {e}")
        return
    log("modal_client", f"volume GC removed {job_rel}")


def voice_prep_via_modal(cfg: dict, ephemeral: bool = False) -> Path:
    """Stage 1 via Modal. Same output path, cache key and stamps as the local
    stage, so switching backends never pays twice or invalidates a cache."""
    pcfg = cfg["voice"]["prep"]
    sources = [ROOT / s for s in pcfg["source_clips"]]
    missing = [str(s) for s in sources if not s.exists()]
    if missing:
        raise StageError(f"Source clips not found: {missing}. "
                         "Put your own recordings in pipeline/assets/voice/raw/")

    out = ROOT / "assets" / "voice" / "voice_sample.wav"
    key = sha256_of(*sources, pcfg)
    if cached(out, key):
        log("voice_prep", f"cached -> {out}")
        return out

    vol = _volume()
    job_rel = f"{UPLOAD_ROOT}/voice/{key}"
    job = f"{VOL_MOUNT}/{job_rel}"
    code_dir = _code_dir()
    try:
        with vol.batch_upload(force=True) as b:
            b.put_directory(code_dir, f"{job_rel}/pipeline")
            # preserve each clip's config-relative path so the remote
            # voice_prep.run resolves source_clips exactly as written
            for rel in pcfg["source_clips"]:
                b.put_file(str(ROOT / rel), f"{job_rel}/pipeline/{rel}")
    finally:
        shutil.rmtree(code_dir, ignore_errors=True)

    spec = {"root": f"{job}/pipeline", "cfg": {"voice": {"prep": pcfg}}}
    wav = _remote("voice_prep_remote", spec, ephemeral)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(wav)
    stamp(out, key)
    log("voice_prep", f"voice sample ready: {out} "
        f"({out.stat().st_size / 1e6:.1f} MB, rendered on Modal)")
    _remove_volume_dir(job_rel)
    return out


def assemble_via_modal(cfg: dict, run_dir: Path, scenes: list[dict],
                       avatar: Path, broll: dict[str, Path], vo: Path,
                       srt: Path, ephemeral: bool = False) -> Path:
    """Stage 7 via Modal. Inputs upload to volume jiheeye-build; the returned
    final.mp4 lands in run_dir on D: for the local qc gate."""
    for name, p in (("avatar", avatar), ("vo", vo), ("srt", srt)):
        if not Path(p).exists():
            raise StageError(f"assemble: missing {name}: {p}")
    for sid, clip in broll.items():
        if not Path(clip).exists():
            raise StageError(f"assemble: missing broll {sid}: {clip}")

    rid = run_dir.name
    vol = _volume()
    job_rel = f"{UPLOAD_ROOT}/assemble/{rid}"
    job = f"{VOL_MOUNT}/{job_rel}"
    music = cfg.get("music") or {}
    music_rel = music.get("file") or ""
    if music_rel:
        if not (ROOT / music_rel).exists():
            raise StageError(f"assemble: config music.file not found: {ROOT / music_rel}")
    code_dir = _code_dir()
    try:
        with vol.batch_upload(force=True) as b:
            b.put_directory(code_dir, f"{job_rel}/pipeline")
            b.put_file(str(avatar), f"{job_rel}/avatar_full.mp4")
            for sid, clip in broll.items():
                b.put_file(str(clip), f"{job_rel}/broll_{sid}.mp4")
            b.put_file(str(vo), f"{job_rel}/run/vo.mp3")
            # vo + srt go INSIDE the remote run dir: assemble references them
            # by bare name with cwd=run_dir (-i vo.mp3, subtitles=filter)
            b.put_file(str(srt), f"{job_rel}/run/captions.srt")
            if music_rel:
                b.put_file(str(ROOT / music_rel), f"{job_rel}/pipeline/{music_rel}")
    finally:
        shutil.rmtree(code_dir, ignore_errors=True)

    spec = {
        "root": f"{job}/pipeline",
        "run_dir": f"{job}/run",
        "cfg": cfg,
        "scenes": scenes,
        "avatar": f"{job}/avatar_full.mp4",
        "broll": {sid: f"{job}/broll_{sid}.mp4" for sid in broll},
        "vo": f"{job}/run/vo.mp3",
        "srt": f"{job}/run/captions.srt",
    }
    final_bytes = _remote("assemble_remote", spec, ephemeral)
    final = run_dir / "final.mp4"
    final.write_bytes(final_bytes)
    log("assemble", f"final (rendered on Modal) -> {final}")
    _remove_volume_dir(job_rel)
    return final