"""Shared helpers: config, logging, hashing, subprocess, run manifest."""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent  # .../pipeline


class StageError(RuntimeError):
    """A stage failed. The message says which stage and why."""


def log(stage: str, msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] [{stage}] {msg}", flush=True)


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    _load_dotenv(ROOT / ".env")
    return cfg


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def env(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise StageError(f"Missing environment variable {name}. Put it in pipeline/.env")
    return val


def sha256_of(*parts) -> str:
    h = hashlib.sha256()
    for p in parts:
        if isinstance(p, (str, Path)) and Path(p).is_file():
            h.update(Path(p).read_bytes())
        else:
            h.update(json.dumps(p, sort_keys=True, default=str).encode())
    return h.hexdigest()[:16]


def cached(out: Path, key: str) -> bool:
    """True if `out` exists and was built from the same inputs (same key).
    Paid stages call this first so a re-run never pays twice for the same thing."""
    stamp = out.with_suffix(out.suffix + ".key")
    return out.exists() and stamp.exists() and stamp.read_text() == key


def stamp(out: Path, key: str) -> None:
    out.with_suffix(out.suffix + ".key").write_text(key)


def sh(cmd: list[str], stage: str, cwd: Path | None = None) -> str:
    """Run a command, raise StageError with stderr tail on failure."""
    log(stage, "$ " + " ".join(shlex.quote(c) for c in cmd[:12]) + (" ..." if len(cmd) > 12 else ""))
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if p.returncode != 0:
        raise StageError(f"{stage}: command failed ({p.returncode}):\n{p.stderr[-2000:]}")
    return p.stdout + p.stderr


def ffprobe_json(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def duration_of(path: Path) -> float:
    return float(ffprobe_json(path)["format"]["duration"])


class Manifest:
    """One JSON file per run: every stage, its inputs key, outputs, timing, status."""

    def __init__(self, run_dir: Path):
        self.path = run_dir / "manifest.json"
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {"stages": {}}

    def record(self, stage: str, **fields) -> None:
        self.data["stages"].setdefault(stage, {}).update(fields, at=time.strftime("%Y-%m-%dT%H:%M:%S"))
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def set(self, key: str, value) -> None:
        self.data[key] = value
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))


def die(msg: str) -> None:
    print(f"\nFAILED: {msg}", file=sys.stderr)
    sys.exit(1)
