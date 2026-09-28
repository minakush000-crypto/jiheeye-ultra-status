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

## Engineer decisions during brief 02 (Flash)

- 2026-09-28 — CONSENT.md section 1: VOICE_OWNER set to "Mayo Ali Aden" and
  SIGNED_DATE set to "2026-09-28" (angle-bracket template markers removed) —
  Mayo authorized this exact two-line edit in the session prompt after the J3
  gate correctly rejected the bracketed values; Flash changed nothing else in
  CONSENT.md — Mayo + Flash.
- 2026-09-28 — Brief 02's stated voice-clip sha256 prefix (35cb41ae21cf94e4,
  coordinator-verified) does NOT match the staged inbox file
  (44575846ec3e2069...). Evidence: both files decode to byte-identical mono
  44.1 kHz s16le PCM (f9ff0f939aa64f8153512b1f534e20e6ec5ecf28e5a215c80608b89
  e1778cf43) and both are 108.460408 s; /mnt/c/Users/muads/Downloads/"jiheeye
  voice.mp3" IS the brief's 35cb41ae21cf94e4 file byte-for-byte; the inbox
  copy is the same audio with different container framing (128 kb/s CBR,
  +5802 bytes). Decision: use the inbox copy Mayo staged (clip1.mp3) as the
  clone source; J2's inbox delete is SKIPPED because its verify precondition
  failed; Mayo deletes the inbox copy after approving the ad00 audio.
  silencedetect (-30 dB, 0.3 s) on the staged bytes found 0 silence events,
  so the Demucs-ON decision holds for these bytes too — Flash, doctrine 6
  (check the artifact, not the report).
- 2026-09-28 — config.yaml voice.prep.source_clips corrected clip1.mp4 ->
  clip1.mp3: the delivered file is an MP3; the .mp4 entry would fail the
  voice stage with "Source clips not found" — Flash, J2/J5 config fix.
- 2026-09-28 — .gitignore now also covers a repo-root .env: a 0-byte .env
  sat untracked and unignored at the repo root; a stray secret file at the
  root must never be committable — Flash, security hardening.
- 2026-09-28 — ElevenLabs key resolution: Mayo's pasted pipeline/.env value
  was the key ID, not the secret (API rejected it:
  api_key_id_used_as_api_key, "API keys start with 'sk_'"). Replaced by
  command with the machine-found working sk_ key from
  /home/muads/yt-digest/.env (the soccer pipeline's ElevenLabs account),
  exactly as brief J4 prescribes for machine-found keys; no key value was
  ever printed — Flash, brief 02 J4.
- 2026-09-28 — J6 instant voice clone BLOCKED at the provider: that
  ElevenLabs account has no instant-voice-cloning entitlement (HTTP 400
  paid_plan_required, request_id 7185e9dfc60a80a303c3b287f243188b). The
  Modal part of J6 (Demucs cleanup) completed: voice_sample.wav rendered in
  82 s wall and cached. Unblocking needs Mayo's billing choice (a plan with
  IVC, Starter or above) plus that account's sk_ secret key in
  pipeline/.env — Flash, reported 2026-09-28.