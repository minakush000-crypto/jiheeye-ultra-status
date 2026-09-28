"""Stage 7 (local, free): cut avatar + B-roll to the scene timeline, lay the
voiceover (and optional music) under it, burn captions, loudness-normalize.
Output: 1080x1920 H.264/AAC MP4.
"""
from __future__ import annotations

from pathlib import Path

from .common import StageError, duration_of, log, sh

STAGE = "assemble"


def _vf(w: int, h: int, fps: int) -> str:
    # cover-crop to the target frame, constant fps, square pixels
    return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},setsar=1,format=yuv420p"


def run(cfg: dict, root: Path, run_dir: Path, scenes: list[dict], avatar: Path,
        broll: dict[str, Path], vo: Path, srt: Path) -> Path:
    oc = cfg["output"]
    w, h, fps = int(oc["width"]), int(oc["height"]), int(oc["fps"])
    seg_dir = run_dir / "segments"
    seg_dir.mkdir(exist_ok=True)
    avatar_dur = duration_of(avatar)

    segs = []
    for i, s in enumerate(scenes):
        seg = seg_dir / f"{i:02d}_{s['id']}.mp4"
        dur = s["dur"]
        if dur <= 0.05:
            raise StageError(f"Scene {s['id']} has duration {dur}s; check the script split")
        common = ["-t", f"{dur:.3f}", "-an", "-vf", _vf(w, h, fps),
                  "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(seg)]
        if s["type"] == "avatar":
            # clone the last frame if the avatar render is short; the seek is
            # clamped so a scene starting past the render's end seeks to its
            # tail instead of EOF (zero-frame segment, review 2026-09-28)
            seek = min(s["start"], max(0.0, avatar_dur - 0.05))
            pad = max(0.0, s["dur"] - (avatar_dur - seek)) + 0.5
            sh(["ffmpeg", "-y", "-ss", f"{seek:.3f}", "-i", str(avatar),
                "-vf", f"tpad=stop_mode=clone:stop_duration={pad:.2f}," + _vf(w, h, fps),
                "-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(seg)], STAGE)
        elif s["type"] == "broll":
            if s["id"] not in broll:
                raise StageError(f"No B-roll clip for scene {s['id']}")
            sh(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(broll[s["id"]])] + common, STAGE)
        else:
            raise StageError(f"Unknown scene type {s['type']}")
        segs.append(seg)

    lst = run_dir / "segments.txt"
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in segs))
    silent = run_dir / "video_silent.mp4"
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], STAGE)

    # audio: voiceover, optional music bed ducked under it
    final = run_dir / "final.mp4"
    cap = cfg["captions"]
    style = (f"FontName={cap['font']},Fontsize={cap['size']},Bold=1,PrimaryColour={cap['colour']},"
             f"OutlineColour=&H00000000,BorderStyle=1,Outline={cap['outline']},Shadow=0,"
             f"Alignment=2,MarginV={cap['margin_v']}")
    vf = f"subtitles={srt.name}:force_style='{style}'" if cap.get("burn", True) else "null"
    loud = f"loudnorm=I={oc['loudness_lufs']}:TP=-1.5:LRA=11"

    music = cfg.get("music") or {}
    mpath = root / music["file"] if music.get("file") else None
    if mpath and mpath.exists():
        afc = (f"[2:a]volume={music.get('volume', 0.12)}[m];"
               f"[1:a][m]amix=inputs=2:duration=first:dropout_transition=0,{loud}[a]")
        cmd = ["ffmpeg", "-y", "-i", silent.name, "-i", vo.name, "-stream_loop", "-1", "-i", str(mpath.resolve()),
               "-filter_complex", f"[0:v]{vf}[v];{afc}", "-map", "[v]", "-map", "[a]"]
    else:
        cmd = ["ffmpeg", "-y", "-i", silent.name, "-i", vo.name,
               "-filter_complex", f"[0:v]{vf}[v];[1:a]{loud}[a]", "-map", "[v]", "-map", "[a]"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final.name]
    sh(cmd, STAGE, cwd=run_dir)
    log(STAGE, f"final -> {final}")
    return final
