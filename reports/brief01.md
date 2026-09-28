# Brief 01 report: jiheeye-ultra to SYSTEM.md standard, Modal compute, status mirror

Engineer: Flash. Session date: 2026-09-28. Brief: briefs/brief01.md (913 words,
committed verbatim as ae81577; re-verified byte-exact against the coordinator
source at the end of the session). Coordinator: Claude (claude.ai Project
"jiheeye ultra"). Every claim below names the command that proved it; output is
quoted from this session's real runs.

## J1 Scaffolding

- Brief imported verbatim: cp
  /mnt/c/Users/muads/Claude/briefs/jiheeye-brief01.md briefs/brief01.md
  followed by diff (silent) and wc -w, which printed 913 words; first line:
  "# Brief 01: jiheeye-ultra to SYSTEM.md standard, Modal compute, status
  mirror". Commit ae81577.
- Created CLAUDE.md, GATES.md (13-gate unlazy ledger), DECISIONS.md (seeded with
  the five closed decisions, dated 2026-09-27), STATUS.md, PROGRESS.md and
  reports/. Gate G2 evidence: SCAFFOLD-OK, exit 0. Commit b7603e0.

## J2 Project skill

- cp -r skills/jiheeye-ugc-pipeline .claude/skills/ , then updated the SKILL.md
  header with the repo path (~/jiheeye-ultra), the modal backend, the
  JIHEEYE_ALLOW_LOCAL guard and the scratch paths. The SOURCE copy was synced
  to the same text later (audit finding). Gate G3 evidence: SKILL-OK, exit 0.

## J3 Venv

- python3 -m venv pipeline/.venv ; .venv/bin/pip install -r requirements.txt
  modal (background, quiet). Output ended: VENV-OK. Modal client:
  pipeline/.venv/bin/modal --version printed "modal client version: 1.5.5".
- No demucs/torch installed locally (J3 rule). Gate G4 evidence: VENV-OK.

## J4 Scratch + disk guard

- pipeline/config.yaml: paths.runs_dir and paths.work_dir point at
  /mnt/d/scratch/jiheeye-ultra/runs and /work; run.py resolve_scratch() refuses
  anything outside /mnt/d/scratch/jiheeye-ultra/ and dies before creating
  anything (doctrine 8).
- tools/disk_guard.sh modeled on soccer's
  (~/yt-digest/soccer-channel/tools/disk_guard.sh) and adapted: reads
  pipeline/config.yaml for the /mnt/d paths, enforces the
  /mnt/d/scratch/jiheeye-ultra root, keeps the C: floor (15 GB), the retired-F
  check, the vhdx log (on the scratch tree, never in the repo: reports/** is
  mirrored) and the ECC cap. Selftest: bash tools/disk_guard.sh --selftest
  printed GUARD-SELFTEST-OK (6 of 6 controls).
- Live run: bash tools/disk_guard.sh --report printed PASS c_floor 17G, PASS
  d_paths mounted+writable, PASS retired_f, PASS vhdx logged, PASS ecc_data
  2603475B within the 10 MB cap. Gate G5 evidence: WIRING-OK.

## J5 Modal port

- pipeline/modal_app.py: app name jiheeye-ultra, volume jiheeye-build;
  voice_prep_remote (ffmpeg decode, Demucs two-stems=vocals, noisereduce, then
  ffmpeg loudnorm; returns WAV) and assemble_remote (runs the real ugc.assemble
  on inputs staged on the volume; returns final.mp4 bytes). The functions run
  the REAL ugc code, uploaded to the volume before every call, and purge ugc
  from sys.modules first so a warm container never serves stale code.
- pipeline/ugc/modal_client.py: staging, transport, cache-key parity with the
  local voice_prep stage, StageError wrapping for remote failures, and volume
  garbage-collection after each successful call.
- pipeline/config.yaml: backend modal by default; voice.prep.demucs true;
  backend local additionally needs JIHEEYE_ALLOW_LOCAL=1 captured at process
  launch (before .env loads, so .env cannot flip it).
- Deploy command: pipeline/.venv/bin/modal deploy pipeline/modal_app.py.
  Output: Built image im-kWHGZ5GlFlhc9eKv1bHcAm in 14.53s; App deployed in
  74.661s. Gate G6 evidence: MODAL-DEPLOYED-OK (modal app list --json shows
  description jiheeye-ultra with state deployed).

## J6 Tests

- python tests/test_offline.py printed ALL OFFLINE TESTS PASSED (13 PASS lines
  including the 12-check QC; the deliberate negative control FAILs a
  720x1280 file).
- python tests/test_modal.py printed 12 PASS QC lines on a file rendered on
  Modal and the final line: ALL MODAL TESTS PASSED (QC checks 12/12).
  Detail from the QC lines: 1080x1920 h264+aac, 30.00 fps, yuv420p, final
  22.00s vs vo 22.00s, loudness -14.0 LUFS, no black gaps, no dead air,
  captions present (19 blocks burned, so libass IS on the image), 12.3 MB.
- Uncertainty answers: image build 14.5s; app deploy 74.7s; a 22s ad assembles
  on Modal CPU in about 1 minute. Demucs on CPU for a real 1-3 min clip is
  still unmeasured (needs Mayo's real clips; the test's synthetic sine is not
  representative of real separation time).

## J7 GitHub private repo

- gh repo create minakush000-crypto/jiheeye-ultra --private --source . --push
  printed the repo URL: https://github.com/minakush000-crypto/jiheeye-ultra
- git ls-remote https://github.com/minakush000-crypto/jiheeye-ultra.git
  refs/heads/main printed a line (gate G9 evidence: PRIVATE-REPO-OK). Pushed
  after every commit; the last code commit pushed is 8a0a3ff.

## J8 Mirror

- tools/push_status.sh (allowlist per brief J8): STATUS.md, GATES.md,
  DECISIONS.md, reports/**, briefs/**, docs/**, pipeline/*.py,
  pipeline/config.yaml, pipeline/scripts/*.json (single level). Hard-deny
  (case-insensitive after the adversarial probe): .env* and env-like names,
  *.png *.jpg *.jpeg *.mp3 *.wav *.mp4, consent.md at any depth,
  pipeline/assets/**. Symlinks at allowlisted paths are REFUSED. The mirror is
  rebuilt from scratch each run so only copied files can travel. The secret
  scan runs text-forced, line-by-line (tokens, key assignments, PEM private
  keys, emails, the git user email, phone numbers, account money), and the
  owner's git email is redacted in the mirror copy only, so the private brief
  stays byte-verbatim (gate G1) while no personal email publishes.
- tools/verify_mirror.sh: independent check (fetch, ls-tree of origin/main,
  deny check, allowlist-only check, symlink check, expected-files check) that
  prints MIRROR-CLEAN-OK only if every assertion passes.
- .claude/settings.json adds the project Stop hook running push_status.sh
  (project hook only).
- gh repo create minakush000-crypto/jiheeye-ultra-status --public printed
  https://github.com/minakush000-crypto/jiheeye-ultra-status
- Dry run staged 27 files and the scan correctly BLOCKED Mayo's email inside
  the verbatim brief; the mirror-copy-only redaction resolves the conflict
  (recorded in DECISIONS.md, 2026-09-28).

## J9 Old copy

- Pre-deletion check: diff -rq (excluding .venv and .git) between
  /mnt/c/Users/muads/Claude/jiheeye-ultra and /home/muads/jiheeye-ultra showed
  nothing "Only in /mnt/c" (zero unique files in the old copy).
- df -h /mnt/c: 16G free BEFORE the deletion; 16G free AFTER (the 355 MB freed
  is below df's GB rounding; the stale .venv is gone either way).
- test ! -d /mnt/c/Users/muads/Claude/jiheeye-ultra printed OLDCOPY-GONE-OK
  (gate G11 evidence).

## Review round (adversarial, 2026-09-28)

Three reviewers (modal-code review, allowlist probe, done-means audit). Applied
fixes: sys.modules purge for warm containers (HIGH), StageError wrapping for
remote failures, volume garbage-collection after each successful Modal call,
avatar seek clamp (zero-frame segment on short renders), missing-sample
StageError in make, preflight Modal-deploy check, the .env-cannot-flip-local
guard, publisher hardening (case-insensitive deny, consent.md anywhere, env
variants, NUL-byte text-forced scan, filename-to-line scan filters, symlink
refusal, scratch rebuild, PEM and uppercase-secret patterns), source skill copy
synced, ARCHITECTURE.md section 5 added. Committed 8a0a3ff and pushed.

## SYSTEM.md drift found (machine wins; report the difference)

- SYSTEM.md section 4 says the Modal CLI is installed; the machine check found
  it MISSING (exit 127, twice). Fixed for this project by J3 (modal 1.5.5 in
  pipeline/.venv). ~/.modal.toml (profile minakush000-crypto) survived and is
  the only Modal credential: do not delete it.
- The machine scout also found: npm_config_cache (lowercase) is set while the
  uppercase NPM_CONFIG_CACHE is empty in env.sh; D: probe writable; gh authed;
  no git remotes existed before J7. Reported for a SYSTEM.md fix on the
  claude.ai side.
## Gate evidence (unlazy, after the last code commit)

Final state: commit fcffc34 (last code commit: scan filter fix; everything after it is docs and the mirror publish), working tree clean, pushed to origin. Command:
node /home/muads/.claude/skills/unlazy/scripts/gate-check.mjs --reverify
GATES.md --timeout 3600, run AFTER commit fcffc34:

  PASS G0 lint (LINT OK) ... PASS G12 report sections, ALL MET
  GATES.md: 13 gates
  ALL MET (13 met, reran: 13, previously met reverified: 13)

(A second, identical ALL MET run followed commit 3603dff as well; the appendix
was updated to reference the final code commit fcffc34.)

Per-gate: G0 G1 G2 G3 G4 G5 G6 G7 G8 G9 G10 G11 G12 all PASS with exit=0 and
matched EXPECT. G7 offline: ALL OFFLINE TESTS PASSED (bytes=4767). G8 Modal:
ALL MODAL TESTS PASSED (QC checks 12/12) (bytes=1140). G10 verify_mirror:
MIRROR-CLEAN-OK (27 files). Full transcript: /mnt/d/scratch/jiheeye-ultra/
(push_status.log) and the session log.
