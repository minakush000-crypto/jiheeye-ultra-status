"""Stage 2: one-time ElevenLabs Instant Voice Clone of the OWNER's voice.

Hard gate: refuses to run unless CONSENT.md at the repo root carries a filled-in
owner attestation. The pipeline clones only the voice of the person who signs it.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import requests

from .common import StageError, env, log

STAGE = "voice_clone"
API = "https://api.elevenlabs.io"


def check_consent(repo_root: Path) -> str:
    f = repo_root / "CONSENT.md"
    if not f.exists():
        raise StageError("CONSENT.md missing at repo root. Voice cloning is blocked until the voice owner signs it.")
    text = f.read_text(encoding="utf-8")
    owner = re.search(r"^VOICE_OWNER:\s*(\S.+)$", text, re.M)
    signed = re.search(r"^SIGNED_DATE:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    if not owner or not signed or "<" in owner.group(1):
        raise StageError("CONSENT.md is not filled in (VOICE_OWNER and SIGNED_DATE). Cloning blocked.")
    return owner.group(1).strip()


def check_avatar_license(repo_root: Path) -> str:
    """Blocks lip-sync unless CONSENT.md section 2 is filled and the evidence file exists."""
    f = repo_root / "CONSENT.md"
    text = f.read_text(encoding="utf-8") if f.exists() else ""
    fields = {}
    for k in ("AVATAR_LICENSOR", "AVATAR_LICENSE_DATE", "AVATAR_LICENSE_SCOPE", "AVATAR_LICENSE_EVIDENCE"):
        m = re.search(rf"^{k}:\s*(\S.*)$", text, re.M)
        if not m or "<" in m.group(1):
            raise StageError(f"CONSENT.md: {k} is not filled in. Lip-sync of the licensed face is blocked.")
        fields[k] = m.group(1).strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields["AVATAR_LICENSE_DATE"]):
        raise StageError("CONSENT.md: AVATAR_LICENSE_DATE must be YYYY-MM-DD")
    exp = re.search(r"^AVATAR_LICENSE_EXPIRES:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    if exp:  # warning only, by owner's decision 2026-09-27
        import datetime as _dt
        days = (_dt.date.fromisoformat(exp.group(1)) - _dt.date.today()).days
        if days < 0:
            log("license", f"WARNING: avatar license EXPIRED {exp.group(1)} ({-days} days ago). Do not publish new ads with this face.")
        elif days <= 30:
            log("license", f"WARNING: avatar license expires {exp.group(1)} (in {days} days).")
    ev = repo_root / fields["AVATAR_LICENSE_EVIDENCE"]
    if not ev.is_file() or ev.stat().st_size == 0:
        raise StageError(f"License evidence file missing: {ev}. Save the screenshot of the written approval there.")
    return f"{fields['AVATAR_LICENSOR']} on {fields['AVATAR_LICENSE_DATE']}"


def run(cfg: dict, root: Path, sample: Path) -> str:
    owner = check_consent(root.parent)
    log(STAGE, f"consent OK, voice owner: {owner}")

    if os.environ.get("ELEVENLABS_VOICE_ID"):
        vid = os.environ["ELEVENLABS_VOICE_ID"]
        log(STAGE, f"using ELEVENLABS_VOICE_ID from .env: {vid}")
        return vid

    id_file = root / "assets" / "voice" / "voice_id.txt"
    if id_file.exists() and id_file.read_text().strip():
        vid = id_file.read_text().strip()
        log(STAGE, f"reusing cloned voice {vid} (delete {id_file} to re-clone)")
        return vid

    vc = cfg["voice"]["clone"]
    with open(sample, "rb") as fh:
        r = requests.post(
            f"{API}/v1/voices/add",
            headers={"xi-api-key": env("ELEVENLABS_API_KEY")},
            data={"name": vc["name"], "description": vc.get("description", ""),
                  "remove_background_noise": "false"},
            files=[("files", (sample.name, fh, "audio/wav"))],
            timeout=180,
        )
    if r.status_code != 200:
        raise StageError(f"ElevenLabs voice clone failed {r.status_code}: {r.text[:500]}")
    body = r.json()
    vid = body["voice_id"]
    if body.get("requires_verification"):
        log(STAGE, "WARNING: ElevenLabs says this voice requires verification. Finish it in the ElevenLabs dashboard.")
    id_file.write_text(vid)
    log(STAGE, f"cloned voice id {vid} saved to {id_file}")
    return vid
