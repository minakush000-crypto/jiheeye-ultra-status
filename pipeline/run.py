#!/usr/bin/env python3
"""Jiheeye Ultra UGC pipeline orchestrator.

Usage (WSL2 Ubuntu terminal, inside the repo's pipeline/ folder):
  python run.py preflight                      # checks tools, keys, consent, model schemas. No paid calls.
  python run.py voice                          # stage 1-2: clean your clips, clone your voice (one time)
  python run.py make scripts/ad01.json         # stage 3-8: script -> final.mp4 -> QC
  python run.py make scripts/ad01.json --until tts   # stop after a stage (cheap test)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from ugc import assemble, broll, lipsync, qc, timeline, tts, voice_clone, voice_prep
from ugc.common import ROOT, Manifest, StageError, die, duration_of, load_config, log

ORDER = ["tts", "timeline", "lipsync", "broll", "assemble", "qc"]
SCRATCH_ROOT = "/mnt/d/scratch/jiheeye-ultra"


def resolve_scratch(cfg: dict) -> tuple[Path, Path]:
    """runs_dir and work_dir from config.paths. Only paths inside the project's
    D: scratch root are accepted; anything else (C: included) is refused before
    anything is created (doctrine 8: scratch failure stops work, no fallback)."""
    prefix = SCRATCH_ROOT.rstrip("/") + "/"
    out = []
    for key in ("runs_dir", "work_dir"):
        raw = str((cfg.get("paths") or {}).get(key, ""))
        if not raw.startswith(prefix):
            raise StageError(
                f"config paths.{key}={raw!r} is not under {prefix}. "
                "Scratch lives on D: only (doctrine 8: never falls back to C:).")
        out.append(Path(raw))
    runs_dir, work_dir = out
    try:
        runs_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise StageError(f"scratch tree under {SCRATCH_ROOT} is unusable ({e}). "
                         "Work stopped; nothing is written to C: (doctrine 8).")
    return runs_dir, work_dir


def run_disk_guard() -> None:
    """brief 01 job 4: the disk guard gates run.py voice and run.py make."""
    guard = ROOT.parent / "tools" / "disk_guard.sh"
    if not guard.is_file():
        raise StageError(f"disk guard missing: {guard}. It is required before any render.")
    r = subprocess.run(["bash", str(guard), "--quiet"], cwd=str(ROOT.parent))
    if r.returncode != 0:
        raise StageError("disk guard FAILED (see its output above). Work stopped; "
                         "nothing falls back to C: (doctrine 8).")


def validate_script(script: dict) -> None:
    if not script.get("scenes"):
        raise StageError("script has no scenes")
    ids = [s["id"] for s in script["scenes"]]
    if len(set(ids)) != len(ids):
        raise StageError(f"duplicate scene ids: {ids}")
    for s in script["scenes"]:
        if s["type"] not in ("avatar", "broll"):
            raise StageError(f"scene {s['id']}: type must be avatar or broll")
        if not s.get("text", "").strip():
            raise StageError(f"scene {s['id']}: empty text")
        if s["type"] == "broll" and not (s.get("image") and s.get("prompt")):
            raise StageError(f"scene {s['id']}: broll needs image and prompt")
    if script["scenes"][0]["type"] != "avatar":
        raise StageError("first scene must be avatar (the hook is a face)")
    if not script.get("reviewed_by_native_speaker"):
        raise StageError("script.reviewed_by_native_speaker is false. Read the Somali text aloud once, then set it true.")


def preflight(cfg: dict) -> bool:
    ok = True

    def item(name, good, detail=""):
        nonlocal ok
        ok &= bool(good)
        log("preflight", f"{'PASS' if good else 'FAIL'}  {name}  {detail}")

    for tool in ("ffmpeg", "ffprobe"):
        item(f"{tool} on PATH", shutil.which(tool), shutil.which(tool) or "install: sudo apt install ffmpeg")
    for k in ("ELEVENLABS_API_KEY", "REPLICATE_API_TOKEN"):
        item(f"{k} set", os.environ.get(k), "" if os.environ.get(k) else "add to pipeline/.env")
    try:
        owner = voice_clone.check_consent(ROOT.parent)
        item("CONSENT.md signed", True, owner)
    except StageError as e:
        item("CONSENT.md signed", False, str(e))
    try:
        item("avatar license (CONSENT.md sec 2)", True, voice_clone.check_avatar_license(ROOT.parent))
    except StageError as e:
        item("avatar license (CONSENT.md sec 2)", False, str(e))
    item("avatar image", (ROOT / cfg["lipsync"]["avatar_image"]).exists(), cfg["lipsync"]["avatar_image"])
    if cfg.get("backend", "modal") == "modal":
        try:
            import modal as _modal
            _modal.Function.from_name("jiheeye-ultra", "assemble_remote")  # hydrates: free, no compute
            item("Modal app jiheeye-ultra deployed", True, "assemble_remote reachable")
        except Exception as e:  # noqa: BLE001
            item("Modal app jiheeye-ultra deployed", False,
                 f"{type(e).__name__}: run `pipeline/.venv/bin/modal deploy pipeline/modal_app.py` ({e})")
    if os.environ.get("REPLICATE_API_TOKEN"):
        from ugc import replicate_io as rio
        for name, sec in (("lipsync", cfg["lipsync"]), ("broll", cfg["broll"])):
            try:
                rio.validate(sec["model"], sec["inputs"], name)
                item(f"{name} model schema", True, sec["model"])
            except Exception as e:  # noqa: BLE001
                item(f"{name} model schema", False, str(e))
    if os.environ.get("ELEVENLABS_API_KEY"):
        import requests
        r = requests.get("https://api.elevenlabs.io/v1/models",
                         headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}, timeout=30)
        want = cfg["tts"]["model_id"]
        models = r.json() if r.ok else []
        m = next((x for x in models if x.get("model_id") == want), None)
        langs = [l.get("language_id") for l in (m or {}).get("languages", [])]
        item(f"ElevenLabs model {want} available", m is not None, f"HTTP {r.status_code}")
        # advisory only: the exact language-id format in /v1/models is not verified yet
        log("preflight", f"{'PASS' if 'so' in langs else 'WARN'}  {want} lists Somali (so)  ids seen: {langs[:80]}")
    return ok


def make(cfg: dict, script_path: Path, until: str | None) -> int:
    script = json.loads(script_path.read_text(encoding="utf-8"))
    validate_script(script)
    runs_dir, _ = resolve_scratch(cfg)
    run_dir = runs_dir / script.get("id", script_path.stem)
    run_dir.mkdir(parents=True, exist_ok=True)
    man = Manifest(run_dir)
    man.set("script", str(script_path))
    man.set("ai_disclosure_required", True)
    t0 = time.time()

    def done(stage):
        return until is not None and ORDER.index(stage) >= ORDER.index(until)

    sample = ROOT / "assets" / "voice" / "voice_sample.wav"
    if not sample.exists() and not os.environ.get("ELEVENLABS_VOICE_ID"):
        raise StageError(
            f"Clean voice sample missing: {sample}. Run `python run.py voice` first "
            "(it renders the sample on Modal and clones the voice once).")
    voice_id = voice_clone.run(cfg, ROOT, sample) \
        if not os.environ.get("ELEVENLABS_VOICE_ID") else os.environ["ELEVENLABS_VOICE_ID"]

    vo, align = tts.run(cfg, run_dir, script, voice_id)
    vo_dur = duration_of(vo)
    man.record("tts", out=str(vo), seconds=vo_dur)
    if done("tts"):
        return 0

    scenes, srt = timeline.run(run_dir, script, align, vo_dur, cfg["captions"]["words_per_caption"])
    man.record("timeline", scenes=scenes, captions=str(srt))
    if done("timeline"):
        return 0

    avatar = lipsync.run(cfg, ROOT, run_dir, vo)
    man.record("lipsync", out=str(avatar))
    if done("lipsync"):
        return 0

    clips = broll.run(cfg, ROOT, run_dir, script)
    man.record("broll", out={k: str(v) for k, v in clips.items()})
    if done("broll"):
        return 0

    if cfg.get("backend", "modal") == "modal":
        from ugc.modal_client import assemble_via_modal
        final = assemble_via_modal(cfg, run_dir, scenes, avatar, clips, vo, srt)
    else:
        final = assemble.run(cfg, ROOT, run_dir, scenes, avatar, clips, vo, srt)
    man.record("assemble", out=str(final), backend=cfg.get("backend", "modal"))

    results = qc.run(cfg, final, vo, srt)
    passed = all(ok for _, ok, _ in results)
    man.record("qc", passed=passed, checks=[{"check": n, "pass": o, "detail": d} for n, o, d in results])
    log("done", f"{'QC PASSED' if passed else 'QC FAILED'} in {time.time()-t0:.0f}s -> {final}")
    log("done", "Before posting: turn ON TikTok's AI-generated content label / YouTube's altered-or-synthetic disclosure.")
    return 0 if passed else 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["preflight", "voice", "make"])
    ap.add_argument("script", nargs="?")
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    ap.add_argument("--until", choices=ORDER)
    a = ap.parse_args()
    allow_local = os.environ.get("JIHEEYE_ALLOW_LOCAL")  # captured BEFORE .env loads
    cfg = load_config(a.config)
    try:
        if a.cmd in ("voice", "make"):
            run_disk_guard()
        backend = cfg.get("backend", "modal")
        if backend == "local" and not allow_local:
            die("config backend=local is allowed ONLY for tests/test_offline.py synthetic "
                "media. Real renders run on Modal (backend: modal). If you really mean it, "
                "launch with JIHEEYE_ALLOW_LOCAL=1 in the environment (not pipeline/.env; "
                "doctrine 1, brief 01 job 5).")
        if a.cmd == "preflight":
            sys.exit(0 if preflight(cfg) else 1)
        if a.cmd == "voice":
            voice_clone.check_consent(ROOT.parent)
            if backend == "modal":
                from ugc.modal_client import voice_prep_via_modal
                sample = voice_prep_via_modal(cfg)
            else:
                _, work_dir = resolve_scratch(cfg)
                sample = voice_prep.run(cfg, ROOT, work_dir=work_dir)
            voice_clone.run(cfg, ROOT, sample)
            return
        if not a.script:
            die("make needs a script path, e.g. scripts/ad01.json")
        sys.exit(make(cfg, Path(a.script).resolve(), a.until))
    except StageError as e:
        die(str(e))


if __name__ == "__main__":
    main()
