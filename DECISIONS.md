# DECISIONS.md: dated decision log

Format: `YYYY-MM-DD — decision — who decided — why`.

## Seeded from brief 01 (closed by Mayo, 2026-09-27; do not reopen)

- 2026-09-27 — Demucs voice cleanup AND the final ffmpeg assembly run on Modal, not the laptop — Mayo — brief 01 closed decision 1.
- 2026-09-27 — Public status mirror: yes, allowlisted, secret-scanned — Mayo — brief 01 closed decision 2.
- 2026-09-27 — Private repo name minakush000-crypto/jiheeye-ultra; mirror minakush000-crypto/jiheeye-ultra-status — Mayo — brief 01 closed decision 3.
- 2026-09-27 — Avatar: one-time AI extend + upscale to 9:16 (brief 02, not this brief) — Mayo — brief 01 closed decision 4.
- 2026-09-27 — AI label: platform toggle only (no burned-in tag). License expiry: warning only — Mayo — brief 01 closed decision 5.

## Coordinator design choices carried into this brief (change only with a reason)

- 2026-09-27 — One TTS call + one lip-sync call per ad — coordinator.
- 2026-09-27 — Paid stages cached by input hash — coordinator.
- 2026-09-27 — QC reads the final file — coordinator.

## Engineer decisions during brief 01 (Flash; change with a recorded reason)

- 2026-09-28 — Modal functions import the REAL `ugc` code from a `/vol/code`
  copy uploaded to volume `jiheeye-build` before each call, instead of a
  re-implemented ffmpeg chain in modal_app.py — Flash — prevents logic drift
  between local and remote; matches SYSTEM.md section 6 (pod-side code lives on
  the volume; stale code must not run).
- 2026-09-28 — `backend: local` additionally requires env `JIHEEYE_ALLOW_LOCAL=1`
  in run.py — Flash — brief says local is allowed only for tests; the env flag
  makes that rule enforced, and the offline tests never invoke run.py so they
  are unaffected.
- 2026-09-28 — Mirror working clone lives at /mnt/d/scratch/jiheeye-ultra/
  status-mirror (not in home, per SYSTEM.md section 11; not on C:) — Flash.
- 2026-09-28 — Mirror copies of allowlisted files get Mayo's git email masked
  to `[redacted-email]`; the private copy stays byte-verbatim (G1) — Flash —
  the secret scan (correctly) blocked the owner's gmail address inside
  briefs/brief01.md; redacting the mirror copy only keeps both closed
  decisions: verbatim private brief AND no personal email on the public
  mirror.
- 2026-09-28 — The mirror clone commits with
  minakush000-crypto@users.noreply.github.com (set repo-local by
  push_status.sh) — Flash — the fresh clone had no identity (first push
  failed with "empty ident name"); the noreply address keeps Mayo's personal
  email off the PUBLIC commit log as well, matching the content scan's rule.
- 2026-09-28 — SYSTEM.md drift found and reported: (1) §4 claims the Modal CLI
  is installed; the machine check found it missing (exit 127), fixed by
  installing `modal` into pipeline/.venv (J3); ~/.modal.toml survived and is
  the only Modal credential — Flash, machine wins over SYSTEM.md.
- 2026-09-28 — test_offline.py pins `demucs: false` in its own config copy —
  Flash — config now sets demucs true (J5) for Modal; local demucs must never
  be installed (J3), so the local test defines its own scenario.
- 2026-09-28 — Added PROGRESS.md beyond the brief's file list — Flash — the
  global working agreement requires a PROGRESS.md; STATUS.md stays the
  coordinator-facing state file. Not in the mirror allowlist, so it stays
  private.
- 2026-09-28 — Voice sample and voice_id stay under pipeline/assets/voice/
  (gitignored working copies; brief J4 moves only runs/ and work/ to D:) —
  Flash.