"""Offline end-to-end test. No API keys, no paid calls.

Replaces the three paid stages (TTS, lipsync, B-roll) with synthetic media made by
ffmpeg, then runs the REAL timeline, assembly and QC code on them, plus the real
voice_prep, consent gate and script validator.

Run (WSL2 terminal, in pipeline/):  python tests/test_offline.py
Success looks like: last line "ALL OFFLINE TESTS PASSED" and exit code 0.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import yaml  # noqa: E402

import run as runner  # noqa: E402
from ugc import assemble, qc, timeline, voice_clone, voice_prep  # noqa: E402
from ugc.common import StageError, duration_of  # noqa: E402


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def main() -> None:
    cfg = yaml.safe_load((HERE / "config.yaml").read_text())
    script = json.loads((HERE / "scripts" / "ad01.json").read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="ugc_test_"))
    root = tmp / "pipeline"
    (root / "assets" / "voice" / "raw").mkdir(parents=True)
    run_dir = root / "runs" / "t"
    run_dir.mkdir(parents=True)

    # 1. script validator blocks unreviewed Somali
    try:
        runner.validate_script(script)
        raise AssertionError("validator should block reviewed_by_native_speaker=false")
    except StageError:
        print("PASS validator blocks unreviewed script")
    script["reviewed_by_native_speaker"] = True
    runner.validate_script(script)
    bad = copy.deepcopy(script)
    bad["scenes"][0]["type"] = "broll"
    try:
        runner.validate_script(bad)
        raise AssertionError("validator should require avatar hook")
    except StageError:
        print("PASS validator requires avatar hook first")

    # 2. consent gate
    repo = tmp
    (repo / "CONSENT.md").write_text("VOICE_OWNER: <your full name>\nSIGNED_DATE: <YYYY-MM-DD>\n")
    try:
        voice_clone.check_consent(repo)
        raise AssertionError("unsigned consent must block")
    except StageError:
        print("PASS consent gate blocks unsigned CONSENT.md")
    (repo / "CONSENT.md").write_text("VOICE_OWNER: Test Owner\nSIGNED_DATE: 2026-09-27\n")
    assert voice_clone.check_consent(repo) == "Test Owner"
    print("PASS consent gate accepts signed CONSENT.md")

    # 2b. avatar license gate
    lic_fields = ("AVATAR_LICENSOR: @jean_philanthrope\nAVATAR_LICENSE_DATE: 2026-09-27\n"
                  "AVATAR_LICENSE_SCOPE: paid ads, AI lip-sync, TikTok+YouTube, 12 months\n"
                  "AVATAR_LICENSE_EVIDENCE: pipeline/assets/licenses/dm.png\n")
    (repo / "CONSENT.md").write_text("VOICE_OWNER: Test Owner\nSIGNED_DATE: 2026-09-27\n" + lic_fields)
    try:
        voice_clone.check_avatar_license(repo)
        raise AssertionError("missing evidence file must block")
    except StageError:
        print("PASS license gate blocks when evidence screenshot is missing")
    (repo / "pipeline" / "assets" / "licenses").mkdir(parents=True)
    (repo / "pipeline" / "assets" / "licenses" / "dm.png").write_bytes(b"x" * 100)
    assert "@jean_philanthrope" in voice_clone.check_avatar_license(repo)
    print("PASS license gate accepts filled CONSENT.md + evidence file")
    (repo / "CONSENT.md").write_text("VOICE_OWNER: Test Owner\nSIGNED_DATE: 2026-09-27\n" + lic_fields
                                     + "AVATAR_LICENSE_EXPIRES: 2020-01-01\n")
    assert voice_clone.check_avatar_license(repo)  # expired: warns, does not block
    print("PASS expired license warns but does not block (warning-only mode)")

    # 3. voice_prep on a synthetic noisy 40s clip
    raw = root / "assets" / "voice" / "raw" / "clip1.mp4"
    ff("-f", "lavfi", "-i", "sine=frequency=180:duration=40", "-f", "lavfi", "-i", "anoisesrc=d=40:a=0.05",
       "-f", "lavfi", "-i", "color=c=black:s=320x240:d=40",
       "-filter_complex", "[0:a][1:a]amix=inputs=2[a]", "-map", "2:v", "-map", "[a]", "-shortest", str(raw))
    vcfg = copy.deepcopy(cfg)
    vcfg["voice"]["prep"]["source_clips"] = ["assets/voice/raw/clip1.mp4"]
    vcfg["voice"]["prep"]["demucs"] = False  # Demucs runs on Modal (brief 01 job 5); the local test has no demucs and must not install torch.
    sample = voice_prep.run(vcfg, root)
    d = duration_of(sample)
    assert 30 <= d <= 41, d
    print(f"PASS voice_prep produced {d:.1f}s clean sample")
    voice_prep.run(vcfg, root)  # second run must hit cache
    print("PASS voice_prep cache hit on re-run")

    # 4. fake paid outputs: 22s voiceover + uniform alignment
    text = " ".join(s["text"] for s in script["scenes"])
    vo = run_dir / "vo.mp3"
    ff("-f", "lavfi", "-i", "sine=frequency=220:duration=22", "-af", "volume=0.5", "-c:a", "libmp3lame", str(vo))
    vo_dur = duration_of(vo)
    n = len(text)
    step = vo_dur / n
    align = {"text": text, "characters": list(text),
             "character_start_times_seconds": [i * step for i in range(n)],
             "character_end_times_seconds": [(i + 1) * step for i in range(n)]}
    (run_dir / "alignment.json").write_text(json.dumps(align, ensure_ascii=False))

    scenes, srt = timeline.run(run_dir, script, run_dir / "alignment.json", vo_dur, 3)
    assert abs(sum(s["dur"] for s in scenes) - vo_dur) < 0.01
    assert scenes[0]["start"] == 0.0 and scenes[-1]["end"] == round(vo_dur, 3)
    print(f"PASS timeline covers full voiceover ({vo_dur:.2f}s) in {len(scenes)} scenes")

    avatar = run_dir / "avatar_full.mp4"  # 720x1280 like a lipsync render, 1s SHORT to test padding
    ff("-f", "lavfi", "-i", f"testsrc2=s=720x1280:r=25:d={vo_dur-1:.2f}", "-pix_fmt", "yuv420p", str(avatar))
    br = run_dir / "broll_product.mp4"  # landscape 5s clip, shorter than its scene to test looping
    ff("-f", "lavfi", "-i", "testsrc=s=1280x720:r=24:d=5", "-pix_fmt", "yuv420p", str(br))

    final = assemble.run(cfg, root, run_dir, scenes, avatar, {"product": br}, vo, srt)
    results = qc.run(cfg, final, vo, srt)
    failed = [r for r in results if not r[1]]
    assert not failed, failed
    print(f"PASS assemble + QC ({len(results)} checks) on {final}")

    # 5. QC must catch a wrong-size file
    wrong = run_dir / "wrong.mp4"
    ff("-i", str(final), "-vf", "scale=720:1280", "-c:a", "copy", str(wrong))
    assert any(n == "resolution" and not ok for n, ok, _ in qc.run(cfg, wrong, vo, srt))
    print("PASS QC fails a 720x1280 file")

    keep = HERE / "tests" / "_last_offline_final.mp4"
    shutil.copy(final, keep)
    print(f"sample output kept at {keep}")
    print("ALL OFFLINE TESTS PASSED")


if __name__ == "__main__":
    main()
