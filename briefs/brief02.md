# Brief 02: voice clone, first Somali audio, vertical avatar ($10 cap)

Coordinator: Claude (claude.ai Project "jiheeye ultra"). Engineer: Flash. Date: 2026-09-28.
Repo ~/jiheeye-ultra. Read ~/.claude/SYSTEM.md and the repo CLAUDE.md first. Self-contained.

## 1. Verified facts

- Brief 01 closed: mirror minakush000-crypto/jiheeye-ultra-status at 4df63fa, 27 files, no private
  files (coordinator cloned it). Coordinator re-ran the mirror's tests/test_offline.py in its own
  sandbox: ALL OFFLINE TESTS PASSED. [coordinator, 2026-09-28]
- Gap in brief 01 report: Modal test and gate-check results were summarized in prose, not pasted.
  This brief requires raw pasted output (see Done means).
- Voice clip: C:\Users\muads\Claude\jiheeye-inbox\clip1.mp3 (/mnt/c/Users/muads/Claude/jiheeye-inbox/clip1.mp3),
  108.46 s MP3, sha256 prefix 35cb41ae21cf94e4. Mayo's own voice. ffmpeg silencedetect found no gap
  below -30 dB for >=0.3 s anywhere: probably a music bed, so Demucs stays ON. [coordinator ffprobe/sha256sum]
- Mayo reports CONSENT.md section 1 is signed. Not yet verified by anyone.
- Mayo is creating pipeline/.env with REPLICATE_API_TOKEN (gitignored).
- Mayo believes an ElevenLabs API key already exists "in a .env somewhere" on this machine. Location unknown.
- Avatar: pipeline/assets/avatar_source.png, 511x512, head + shoulders, bob hair spans nearly the full width.
  A plain 9:16 cover-crop cuts the hair off (coordinator rendered and viewed it).

## 2. Closed decisions (Mayo, 2026-09-28)

1. Hard spend cap for this brief: $10 USD total across ElevenLabs + Replicate + Modal. Before each paid
   call, estimate its cost from the provider's current pricing page or API response; stop and report if
   cumulative spend would exceed $10. Record every paid call in reports/brief02_spend.csv
   (time, provider, model, units, est_usd, cumulative_usd).
2. First test ad is avatar-only: no B-roll scene, no product image.
3. Mayo only handles credentials and listening/approval. Flash does all file moves and runs.
4. Avatar: one-time AI extend to 9:16 + upscale, reused for every ad (decided 2026-09-27).
5. Lip-sync is NOT in this brief. It runs in brief 03, after Mayo approves the Somali audio.

## 3. Uncertainty set

- ○ Where the ElevenLabs key lives. ○ Whether ElevenLabs IVC returns requires_verification.
- ○ Which Replicate model can outpaint a square portrait to 9:16. Candidate (unverified):
  black-forest-labs/flux-fill-pro. Verify the live schema with ugc/replicate_io.validate()-style lookup;
  if no suitable model is confirmed, fall back to blurred padding and say so.
- ○ Demucs on Modal CPU runtime for a 108 s clip.
- ○ Whether eleven_v3 accepts language_code "so" (preflight prints the model's language list).
- ○ Somali script wording (ad01.json lines came from a Google chat, never native-reviewed).

## 4. Jobs

J1 Copy this brief verbatim to briefs/brief02.md; print wc -w and first line; commit.
J2 Voice file: move /mnt/c/Users/muads/Claude/jiheeye-inbox/clip1.mp3 to pipeline/assets/voice/raw/clip1.mp3
   (gitignored). Verify sha256 prefix 35cb41ae21cf94e4. Then delete the inbox copy and the empty
   jiheeye-inbox folder from C:.
J3 Consent: run the voice_clone.check_consent gate; paste its output. If it fails, stop and report
   which field is missing. Do not edit CONSENT.md section 1 yourself.
J4 Keys: search the machine for an ElevenLabs key (e.g. grep -l ELEVENLABS across ~/*/.env,
   ~/.config, ~/yt-digest). Print ONLY file paths and variable names, never values. Add it to
   pipeline/.env as ELEVENLABS_API_KEY (copy the value by command, not by printing). If none found,
   stop J6-J8 and report "Mayo must add ELEVENLABS_API_KEY". Confirm REPLICATE_API_TOKEN is present
   (print its length only). Secret-scan the repo and mirror after.
J5 Preflight: python run.py preflight. Paste full output. Fix config inputs if a model schema fails.
J6 Voice: python run.py voice (Modal: Demucs + denoise + loudnorm, then ElevenLabs instant voice clone).
   Record Modal runtime. Keep voice_id in pipeline/assets/voice/voice_id.txt (gitignored).
J7 Test script: create pipeline/scripts/ad00_test.json = ad01.json minus the "product" broll scene.
   Leave reviewed_by_native_speaker false. For this run only, add a --allow-unreviewed flag to
   run.py make that is valid ONLY with --until tts, and prints "UNREVIEWED: audio for Mayo's review".
   Run: python run.py make scripts/ad00_test.json --until tts --allow-unreviewed.
   Copy the resulting vo.mp3 to /mnt/c/Users/muads/Claude/jiheeye-review/ad00_vo.mp3 and write the
   Somali script text beside it as ad00_script.txt, so Mayo can listen on Windows.
J8 Avatar: extend avatar_source.png to 1080x1920 (9:16) with the hair, face and suit intact, then
   upscale if needed. Save pipeline/assets/avatar.png and a side-by-side preview to
   /mnt/c/Users/muads/Claude/jiheeye-review/avatar_preview.png. Do not change the face.
J9 Report reports/brief02.md; push repo; mirror publishes (mp3/png stay denied).

## 5. Done means

- reports/brief02.md contains RAW pasted output (not summaries) of: J2 sha256sum, J3 consent gate,
  J4 key search (paths/names/lengths only), J5 preflight, J6 voice run incl. Modal runtime, J7 make
  --until tts, J8 model name + schema check, and the spend CSV.
- /mnt/c/Users/muads/Claude/jiheeye-review/ holds ad00_vo.mp3, ad00_script.txt, avatar_preview.png.
- Total spend <= $10, shown in reports/brief02_spend.csv (mirrored).
- gate-check --reverify output after the last code commit, published to the mirror.

## 6. Doctrine footer

1. Nothing local except footage acquisition (harness tooling exempt).
2. Use tools before guessing.
3. No orphan tools.
4. Facts from data.
5. Report input age.
6. Check the artifact, not the report.
7. "Done" requires --reverify output after the last code commit, published to the mirror. --status is never proof.
8. Scratch-drive failure stops work. Nothing ever falls back to C:.
