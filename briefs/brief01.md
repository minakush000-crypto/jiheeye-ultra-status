# Brief 01: jiheeye-ultra to SYSTEM.md standard, Modal compute, status mirror

Coordinator: Claude (claude.ai Project "jiheeye ultra"). Engineer: Flash. Date: 2026-09-27.
Read ~/.claude/SYSTEM.md first. This brief is self-contained; where it and SYSTEM.md disagree on
facts about the machine, the machine wins: check, then report the difference.

## 1. Verified facts (source in brackets)

- Repo ~/jiheeye-ultra exists, branch main, one commit f8fe8bd "Import jiheeye-ultra pipeline",
  top level: CONSENT.md README.md docs pipeline skills. Git identity set repo-local:
  minakush000-crypto / [redacted-email]. [Mayo pasted `git log --oneline && ls`]
- It was copied from /mnt/c/Users/muads/Claude/jiheeye-ultra (old copy, still on C:, holds an old
  pipeline/.venv). [coordinator listed the folder]
- Pipeline code: pipeline/run.py (preflight | voice | make), pipeline/ugc/{voice_prep, voice_clone,
  tts, timeline, lipsync, broll, assemble, qc, replicate_io, common}.py, config.yaml,
  tests/test_offline.py. Offline test passed in the coordinator sandbox:
  `python3 tests/test_offline.py` -> "ALL OFFLINE TESTS PASSED" (13 PASS lines incl. 12-check QC).
- Paid engines: ElevenLabs eleven_v3 (lists Somali) for clone + TTS; Replicate veed/fabric-1.0
  (lip-sync) and kwaivgi/kling-v2.1 (B-roll). Input key names for both Replicate models are
  UNVERIFIED; replicate_io.validate() checks them live before any paid call.
- CONSENT.md: section 1 (voice) is UNSIGNED; section 2 (avatar license, @jean_philanthrope,
  2026-09-27 to 2027-09-27, warn-only expiry) is filled; evidence file
  pipeline/assets/licenses/jeanphil_dm_full_thread.png exists (content not yet viewed by coordinator).
- The first commit includes pipeline/assets/licenses/*.png and pipeline/assets/avatar_source.png.
  These are private: allowed in the private repo, NEVER in the public mirror.
- Mayo's voice sample (108.5 s MP3, -14.5 LUFS, no gap below -30 dB for 0.3 s anywhere, so likely a
  music bed under the voice) is NOT yet in the repo. Its path on this PC is unknown.

## 2. Closed decisions (Mayo, 2026-09-27; do not reopen)

1. Demucs voice cleanup AND the final ffmpeg assembly run on Modal, not the laptop.
2. Public status mirror: yes, allowlisted, secret-scanned.
3. Private GitHub repo name: minakush000-crypto/jiheeye-ultra. Mirror: minakush000-crypto/jiheeye-ultra-status.
4. Avatar: one-time AI extend + upscale to 9:16 (brief 02, not this one).
5. AI label: platform toggle only (no burned-in tag). License expiry: warning only.

Coordinator's design choices (not Mayo's requirements; change only with a reason in DECISIONS.md):
one TTS call + one lip-sync call per ad; paid stages cached by input hash; QC reads the final file.

## 3. Uncertainty set

- ○ Where soccer's push_status.sh lives and whether it can be copied as-is.
- ○ Exact scratch root on D: (SYSTEM.md says /mnt/d/scratch; verify writable before use).
- ○ Modal image build time/size for demucs+torch; whether CPU is enough for a 1-3 min clip.
- ○ Whether ffmpeg on the Modal image has libass (needed for burned captions).
- ○ Whether ~/jiheeye-ultra already contained anything before the copy.

## 4. Jobs

J1 Scaffolding. Add CLAUDE.md (project rules; points to ~/.claude/SYSTEM.md and this repo's docs),
   GATES.md (unlazy ledger for this brief), DECISIONS.md (seed with section 2 above, dated),
   STATUS.md, briefs/, reports/. Copy this file verbatim to briefs/brief01.md first; print its word
   count and first line; commit.
J2 Project skill. Copy skills/jiheeye-ugc-pipeline to .claude/skills/jiheeye-ugc-pipeline (project
   level only; do NOT touch ~/.claude). Update the skill's repo path to ~/jiheeye-ultra.
J3 Venv. pipeline/.venv inside the repo, `pip install -r pipeline/requirements.txt` plus `modal`.
   Pip cache on the scratch drive per ~/.config/soccer/env.sh. Do not install demucs/torch locally.
J4 Scratch. Move runtime dirs out of the repo: runs/ and work/ go to /mnt/d/scratch/jiheeye-ultra/
   {runs,work}, set via config.yaml `paths:`; code must refuse to fall back to C: (doctrine 8).
   Run the disk guard (copy soccer's tools/disk_guard.sh or call it) at the start of `run.py make`
   and `run.py voice`.
J5 Modal port. New pipeline/modal_app.py, app name jiheeye-ultra, volume jiheeye-build:
   - voice_prep_remote: Demucs --two-stems=vocals + noisereduce + ffmpeg loudnorm, returns WAV.
   - assemble_remote: runs ugc/assemble.py logic (segments, concat, captions, loudnorm) on inputs
     uploaded to the volume, returns final.mp4.
   run.py calls these by default (`backend: modal` in config.yaml); `backend: local` is allowed ONLY
   for tests/test_offline.py synthetic media. Set config voice.prep.demucs: true.
   After editing any pod-side code, `modal volume put`/redeploy (SYSTEM.md section 6).
J6 Tests. tests/test_offline.py must pass locally (local backend, synthetic media). Add
   tests/test_modal.py: runs assemble_remote on the same synthetic media via Modal and runs qc.py on
   the returned file; must print 12 PASS QC lines.
J7 GitHub. Create private repo minakush000-crypto/jiheeye-ultra with gh, push main.
J8 Mirror. Public repo minakush000-crypto/jiheeye-ultra-status, published by tools/push_status.sh
   modeled on soccer's: allowlist = STATUS.md, GATES.md, DECISIONS.md, reports/**, briefs/**,
   docs/**, pipeline/**/*.py, pipeline/config.yaml, pipeline/scripts/*.json. Hard-deny:
   .env*, *.png, *.jpg, *.mp3, *.wav, *.mp4, CONSENT.md, pipeline/assets/**. Secret scan before push.
   Project Stop hook runs push_status.sh (project hook only).
J9 Old copy. After J7 is pushed and J6 passes, delete /mnt/c/Users/muads/Claude/jiheeye-ultra
   (old copy incl. its .venv) and report C: free space before/after.

## 5. Done means

- reports/brief01.md lists each job with the command run and its output (not a summary).
- `python pipeline/tests/test_offline.py` -> "ALL OFFLINE TESTS PASSED" (output in report).
- `python pipeline/tests/test_modal.py` -> 12 QC PASS lines from a file rendered on Modal.
- `git ls-remote` shows main on the private repo; mirror repo shows the allowlisted files only;
  report shows `git -C <mirror> ls-files` and proves no *.png/*.mp3/CONSENT.md/.env present.
- `gate-check --reverify` output after the last code commit, published to the mirror.

## 6. Doctrine footer

1. Nothing local except footage acquisition (harness tooling exempt).
2. Use tools before guessing.
3. No orphan tools.
4. Facts from data.
5. Report input age.
6. Check the artifact, not the report.
7. "Done" requires --reverify output after the last code commit, published to the mirror. --status is never proof.
8. Scratch-drive failure stops work. Nothing ever falls back to C:.
