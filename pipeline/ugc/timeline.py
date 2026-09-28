"""Stage 4 (local, free): scene boundaries + caption file from TTS alignment."""
from __future__ import annotations

import json
from pathlib import Path

from .common import log

STAGE = "timeline"


def _scene_char_spans(script: dict) -> list[tuple[int, int]]:
    spans, pos = [], 0
    for s in script["scenes"]:
        t = s["text"].strip()
        spans.append((pos, pos + len(t)))
        pos += len(t) + 1  # joining space
    return spans


def scene_times(script: dict, alignment: dict, total: float) -> list[dict]:
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    spans = _scene_char_spans(script)
    n_chars = spans[-1][1]
    exact = len(chars) == n_chars

    out = []
    for i, (a, b) in enumerate(spans):
        if exact:
            t0 = starts[a]
        else:  # provider normalized the text: fall back to proportional mapping
            t0 = starts[min(len(starts) - 1, int(a / n_chars * len(starts)))]
        out.append({"id": script["scenes"][i]["id"], "type": script["scenes"][i]["type"], "start": round(t0, 3)})
    out[0]["start"] = 0.0
    for i, s in enumerate(out):
        s["end"] = out[i + 1]["start"] if i + 1 < len(out) else round(total, 3)
        s["dur"] = round(s["end"] - s["start"], 3)
    log(STAGE, f"alignment exact={exact}; scenes: " + ", ".join(f"{s['id']}={s['dur']}s" for s in out))
    return out


def _fmt(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def words_from_alignment(alignment: dict) -> list[tuple[str, float, float]]:
    chars = alignment["characters"]
    st = alignment["character_start_times_seconds"]
    en = alignment["character_end_times_seconds"]
    words, cur, t0 = [], "", None
    for c, a, b in zip(chars, st, en):
        if c.isspace():
            if cur:
                words.append((cur, t0, prev_end))
                cur = ""
            continue
        if not cur:
            t0 = a
        cur += c
        prev_end = b
    if cur:
        words.append((cur, t0, prev_end))
    return words


def write_srt(alignment: dict, path: Path, words_per_caption: int = 3) -> int:
    words = words_from_alignment(alignment)
    blocks = []
    for i in range(0, len(words), words_per_caption):
        chunk = words[i:i + words_per_caption]
        blocks.append((chunk[0][1], chunk[-1][2], " ".join(w for w, _, _ in chunk)))
    path.write_text(
        "\n".join(f"{n}\n{_fmt(a)} --> {_fmt(b)}\n{txt}\n" for n, (a, b, txt) in enumerate(blocks, 1)),
        encoding="utf-8",
    )
    return len(blocks)


def run(run_dir: Path, script: dict, align_path: Path, vo_duration: float, words_per_caption: int) -> tuple[list[dict], Path]:
    alignment = json.loads(align_path.read_text(encoding="utf-8"))
    scenes = scene_times(script, alignment, vo_duration)
    (run_dir / "scenes.json").write_text(json.dumps(scenes, indent=2))
    srt = run_dir / "captions.srt"
    n = write_srt(alignment, srt, words_per_caption)
    log(STAGE, f"{n} caption blocks -> {srt}")
    return scenes, srt
