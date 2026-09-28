"""Modal end-to-end test (brief 01 job 6).

Builds the same synthetic media as test_offline.py, renders final.mp4 with
assemble_remote on Modal (ephemeral app: always tests the current local code,
no deploy required), then runs the REAL qc.py locally on the returned file.
No API keys needed. Requires `modal` auth (~/.modal.toml).

Run (WSL2 terminal, in pipeline/):  python tests/test_modal.py
Success: 12 PASS QC lines and last line "ALL MODAL TESTS PASSED (QC checks 12/12)".
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import yaml  # noqa: E402

from ugc import qc, timeline  # noqa: E402
from ugc.common import duration_of  # noqa: E402


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def main() -> None:
    cfg = yaml.safe_load((HERE / "config.yaml").read_text())
    script = json.loads((HERE / "scripts" / "ad01.json").read_text(encoding="utf-8"))
    script["reviewed_by_native_speaker"] = True
    tmp = Path(tempfile.mkdtemp(prefix="ugc_modal_test_"))
    run_dir = tmp / "run"
    run_dir.mkdir(parents=True)

    # synthetic paid-stage outputs, same recipe as test_offline.py
    text = " ".join(s["text"] for s in script["scenes"])
    vo = run_dir / "vo.mp3"
    ff("-f", "lavfi", "-i", "sine=frequency=220:duration=22", "-af", "volume=0.5",
       "-c:a", "libmp3lame", str(vo))
    vo_dur = duration_of(vo)
    n = len(text)
    step = vo_dur / n
    align = {"text": text, "characters": list(text),
             "character_start_times_seconds": [i * step for i in range(n)],
             "character_end_times_seconds": [(i + 1) * step for i in range(n)]}
    align_path = run_dir / "alignment.json"
    align_path.write_text(json.dumps(align, ensure_ascii=False))

    scenes, srt = timeline.run(run_dir, script, align_path, vo_dur, 3)

    avatar = run_dir / "avatar_full.mp4"  # 1s short, like a real lipsync render
    ff("-f", "lavfi", "-i", f"testsrc2=s=720x1280:r=25:d={vo_dur - 1:.2f}",
       "-pix_fmt", "yuv420p", str(avatar))
    br = run_dir / "broll_product.mp4"
    ff("-f", "lavfi", "-i", "testsrc=s=1280x720:r=24:d=5", "-pix_fmt", "yuv420p", str(br))

    from ugc import modal_client
    final = modal_client.assemble_via_modal(
        cfg, run_dir, scenes, avatar, {"product": br}, vo, srt, ephemeral=True)
    assert final.exists() and final.stat().st_size > 10_000, "Modal returned no file"

    results = qc.run(cfg, final, vo, srt)  # the artifact, not the stage report
    failed = [r for r in results if not r[1]]
    assert not failed, failed
    assert len(results) == 12, f"expected 12 QC checks, got {len(results)}"
    print("ALL MODAL TESTS PASSED (QC checks 12/12)")


if __name__ == "__main__":
    main()