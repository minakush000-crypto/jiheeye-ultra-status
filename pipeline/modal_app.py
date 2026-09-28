"""Modal backend for jiheeye-ultra (brief 01 job 5, closed decision 2026-09-27).

Demucs voice cleanup AND the final ffmpeg assembly run here, never on the
laptop. The functions below run the REAL ugc code: the client copies ugc/*.py
onto volume jiheeye-build before every call, so local and remote logic can
never drift (SYSTEM.md section 6: pod-side code lives on the volume; stale
code must not run).

Deploy once per change to THIS file (image/app wiring):
    pipeline/.venv/bin/modal deploy pipeline/modal_app.py
Code changes to ugc/*.py need no redeploy: the client re-uploads them per run.
"""
from __future__ import annotations

import sys
from pathlib import Path

import modal

APP_NAME = "jiheeye-ultra"
VOL_NAME = "jiheeye-build"
VOL_MOUNT = "/vol"

volume = modal.Volume.from_name(VOL_NAME, create_if_missing=True)

# torch first from the CPU wheel index, then demucs on top, so the image
# carries no CUDA payload (no GPU here; uncertainty J5: CPU sufficiency for a
# 1-3 min clip is measured by tests/test_modal.py, not assumed)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "fonts-dejavu-core")
    .run_commands("pip install --no-cache-dir torch torchaudio "
                  "--index-url https://download.pytorch.org/whl/cpu")
    .pip_install("demucs>=4.0", "noisereduce>=3.0", "numpy>=1.26",
                 "soundfile>=0.12", "PyYAML>=6.0")
)

app = modal.App(APP_NAME)

_COMMON_ENV = {
    "HF_HOME": f"{VOL_MOUNT}/caches/hf",     # demucs model download persists on the volume
    "TORCH_HOME": f"{VOL_MOUNT}/caches/torch",
    "PYTHONDONTWRITEBYTECODE": "1",          # keep __pycache__ off the volume
}


def _import_ugc(root: str) -> None:
    """Make the volume's copy of ugc/ importable inside the container, and
    purge any cached ugc modules first: on a warm reused container Python
    would otherwise serve the modules of the PREVIOUS run, silently ignoring
    the fresh code the client just uploaded (adversarial review 2026-09-28)."""
    if root not in sys.path:
        sys.path.insert(0, root)
    for name in [n for n in sys.modules if n == "ugc" or n.startswith("ugc.")]:
        del sys.modules[name]


@app.function(image=image, volumes={VOL_MOUNT: volume}, timeout=3600,
               cpu=4.0, memory=8192, env=_COMMON_ENV)
def voice_prep_remote(spec: dict) -> bytes:
    """Stage 1 on Modal: ffmpeg decode/join -> Demucs --two-stems=vocals ->
    noisereduce -> ffmpeg loudnorm. Runs the real ugc.voice_prep. Returns WAV."""
    root = Path(spec["root"])
    _import_ugc(str(root))
    volume.reload()  # the client just uploaded code + clips via batch_upload
    from ugc import voice_prep
    out = voice_prep.run(spec["cfg"], root)
    volume.commit()
    return Path(out).read_bytes()


@app.function(image=image, volumes={VOL_MOUNT: volume}, timeout=1800,
               cpu=4.0, memory=4096, env=_COMMON_ENV)
def assemble_remote(spec: dict) -> bytes:
    """Stage 7 on Modal: segments, concat, burned captions, loudnorm. Runs the
    real ugc.assemble on inputs staged under /vol by the client. Returns the
    final MP4 bytes; qc.py runs locally on the downloaded file."""
    root = Path(spec["root"])
    run_dir = Path(spec["run_dir"])
    _import_ugc(str(root))
    volume.reload()
    from ugc import assemble
    final = assemble.run(
        spec["cfg"], root, run_dir, spec["scenes"],
        Path(spec["avatar"]),
        {k: Path(v) for k, v in spec["broll"].items()},
        Path(spec["vo"]), Path(spec["srt"]),
    )
    volume.commit()
    return Path(final).read_bytes()