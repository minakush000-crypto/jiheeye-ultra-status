# STATUS.md

Updated: 2026-09-28 00:45 CDT (session running brief 01; ages checked at update)

## Current phase

Brief 01 executing, closing phase (report, mirror push, reverify pending).

## Brief 01 jobs

| Job | What | State |
|---|---|---|
| J1 | Scaffolding (CLAUDE.md, GATES.md, DECISIONS.md, STATUS.md, briefs/, reports/) | done |
| J2 | Project skill at .claude/skills (+ source copy synced) | done |
| J3 | venv + requirements + modal | done |
| J4 | Scratch paths on D: + disk guard (selftest 6/6) | done |
| J5 | Modal port (modal_app.py, backend: modal, demucs true) | done |
| J6 | test_offline passes; test_modal 12/12 QC on a Modal render | done |
| J7 | Private GitHub repo pushed (main) | done |
| J8 | Mirror publisher + verifier + Stop hook; repo created | done, first publish pending |
| J9 | Old C: copy deleted (16G free before and after at GB rounding) | done |

## Uncertainty answers (brief section 3)

- ffmpeg on the Modal image HAS libass: captions burn (19 blocks) — verified by
  test_modal's QC.
- Image build 14.5s, app deploy 75s; a 22s ad assembles on Modal CPU in ~1 min.
  Demucs on CPU with a real 1-3 min clip: still unmeasured (needs Mayo's real
  clips; the synthetic sine in tests does not represent real separation time).

## Blockers

- CONSENT.md section 1 (voice owner signature) unsigned; blocks `run.py voice`,
  not this brief. Mayo's raw voice clips not yet in the repo.

## Next (coordinator)

- First mirror publish + gate-check --reverify (closing steps of this session).
- Brief 02 (avatar 9:16 extend/upscale) after voice + first ad run.