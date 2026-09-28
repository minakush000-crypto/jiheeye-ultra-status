# Brief 02 report: voice clone, first Somali audio, vertical avatar ($10 cap)

Engineer: Flash. Session date: 2026-09-28. Brief: briefs/brief02.md (827 words,
committed verbatim as 0dbe260). Coordinator: Claude (claude.ai Project "jiheeye
ultra"). Every claim below names the command that proved it; output is quoted
from this session's real runs. STATUS AT WRITING: J1-J5 and J8 COMPLETE, J6
half done (Modal cleanup done, clone blocked at the provider), J7 prepared but
its run is blocked behind J6, J9 done for the completed parts. The blocker and
its exact unblock steps are in section J6.

## J1 Brief import

- `cp /mnt/c/Users/muads/Claude/briefs/jiheeye-brief02.md briefs/brief02.md`,
  then `diff` (silent) and `echo VERBATIM-OK`:
  ```
  VERBATIM-OK
  ```
- `wc -w briefs/brief02.md`:
  ```
  827 briefs/brief02.md
  ```
- `head -1 briefs/brief02.md`:
  ```
  # Brief 02: voice clone, first Somali audio, vertical avatar ($10 cap)
  ```
- Commit: `git commit -m "docs: brief 02 verbatim copy"` ->
  `[main 0dbe260] docs: brief 02 verbatim copy` (1 file changed, 88 insertions).
  Only briefs/brief02.md was staged; CONSENT.md and .env were left untouched.

## J2 Voice file

Input age: inbox clip1.mp3 mtime 2026-09-28 01:50 CDT (14 min before session
start); staged copy verified byte-identical to it. Brief fact said sha256
prefix 35cb41ae21cf94e4 — **the artifact does not match**, so J2's delete
precondition FAILED and the inbox copy was KEPT (details in the deviation
note below and in DECISIONS.md).

- Staging (cp, not mv, because verification failed):
  `cp /mnt/c/Users/muads/Claude/jiheeye-inbox/clip1.mp3 pipeline/assets/voice/raw/clip1.mp3`
- `sha256sum pipeline/assets/voice/raw/clip1.mp3`:
  ```
  44575846ec3e2069a9c207f59a41e3d64a4642c36404937829ed7204eb5da99b  pipeline/assets/voice/raw/clip1.mp3
  ```
  Brief expected prefix 35cb41ae21cf94e4. MISMATCH.
- Investigation, command 1: `sha256sum "/mnt/c/Users/muads/Downloads/jiheeye voice.mp3"`:
  ```
  35cb41ae21cf94e4c2e5dca2f7d2fb9b564376a840be5230f6b308f731369877  /mnt/c/Users/muads/Downloads/jiheeye voice.mp3
  ```
  The brief's hash IS a real file: the Downloads original. ffprobe duration of
  both files: 108.460408 s (identical to the microsecond).
- Investigation, command 2 — decoded PCM comparison (mono 44.1 kHz s16le):
  ```
  ffmpeg -v error -i pipeline/assets/voice/raw/clip1.mp3 -f s16le -ac 1 -ar 44100 - | sha256sum
  f9ff0f939aa64f8153512b1f534e20e6ec5ecf28e5a215c80608b89e1778cf43  -
  ffmpeg -v error -i "/mnt/c/Users/muads/Downloads/jiheeye voice.mp3" -f s16le -ac 1 -ar 44100 - | sha256sum
  f9ff0f939aa64f8153512b1f534e20e6ec5ecf28e5a215c80608b89e1778cf43  -
  ```
  BYTE-IDENTICAL decoded audio. The inbox copy is the same recording with
  different container framing (128 kb/s CBR, 1,779,772 bytes vs 1,773,970).
- Music-bed check reproduced on the staged bytes
  (`ffmpeg -i ... -af silencedetect=noise=-30dB:d=0.3 -f null -`):
  ```
  0 silence events
  ```
  Confirms the coordinator's finding: no gap below -30 dB for >=0.3 s, so
  Demucs stays ON (config unchanged). ebur128 peak: -1.0 dBFS.
- Config fix (would have failed the voice stage otherwise):
  `voice.prep.source_clips: assets/voice/raw/clip1.mp4 -> clip1.mp3`
  (commit 977fb5c). Inbox copy NOT deleted (precondition failed); Mayo can
  delete it after approving the ad00 audio.

## J3 Consent gate

First run FAILED — Mayo had signed but kept the template's angle brackets:
```
Traceback ... ugc.common.StageError: CONSENT.md is not filled in (VOICE_OWNER and SIGNED_DATE). Cloning blocked.
```
Reported to Mayo; Mayo authorized this exact edit (recorded in DECISIONS.md):
`VOICE_OWNER: Mayo Ali Aden` and `SIGNED_DATE: 2026-09-28` (nothing else
changed in CONSENT.md). Re-run
(`pipeline/.venv/bin/python -c "...check_consent(Path('.'))..."`):
```
CONSENT-OK Mayo Ali Aden
```
Commit 14e8b2d.

## J4 Keys

- Machine-wide search (paths only, per brief): env-style files found under
  /home/muads: jiheeye-ultra/.env (0 bytes), jiheeye-ultra/pipeline/.env,
  jiheeye-ultra/pipeline/.env.example, ECC/.env.example, .opencli/spotify.env,
  yt-digest/.env, yt-digest/.env.example, yt-digest/.env.bak-sep7,
  yt-digest/.env.bak-voice, yt-digest/soccer-channel/.env.
  Files containing ELEVENLABS (grep -qiE 'ELEVENLABS'):
  ```
  /home/muads/yt-digest/.env              VAR: ELEVENLABS_API_KEY
  /home/muads/yt-digest/.env.bak-sep7     VAR: ELEVENLABS_API_KEY
  /home/muads/yt-digest/.env.bak-voice    VAR: ELEVENLABS_API_KEY
  /home/muads/jiheeye-ultra/pipeline/.env          VAR: ELEVENLABS_API_KEY
  /home/muads/jiheeye-ultra/pipeline/.env.example  VAR: ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
  ```
  No values printed anywhere at any point.
- REPLICATE_API_TOKEN confirmed present (name + length only):
  `REPLICATE_API_TOKEN value length: 40`.
- Mayo first pasted an ELEVENLABS_API_KEY into pipeline/.env
  (value length 64, first char "3"). The API rejected it:
  ```
  {"detail":{"type":"authentication_error","code":"invalid_api_key",
  "message":"API key ID used as API key - only valid API keys can be used.
  API keys start with 'sk_' and are shown when the key is created or rotated.",
  "status":"api_key_id_used_as_api_key", ...}}  HTTP_STATUS:400
  ```
- Per J4's designed path, the machine-found key was installed by command
  (`python3` rewrite of the one line in pipeline/.env, value never printed):
  the yt-digest/soccer key (sk_..., 51 chars). Note: that file holds TWO
  duplicate ELEVENLABS_API_KEY lines; the first was used. Key identity was
  compared only by sha256-of-value: yt-digest c4304e73dcc5 vs Mayo's pasted
  ecc793f54fdf -> DIFFERENT-KEY. pipeline/.env now holds the working sk_ key.
- Live checks with the working key:
  `GET /v1/models` -> HTTP 200, 9 models, including:
  ```
  eleven_v3  <== eleven_v3
     somali (so) listed: True | language count: 74
  eleven_v3_conversational, eleven_multilingual_v2, eleven_flash_v2_5,
  eleven_turbo_v2_5, eleven_turbo_v2, eleven_flash_v2, eleven_english_sts_v2,
  eleven_multilingual_sts_v2
  ```
  This closes the uncertainty "whether eleven_v3 accepts language_code 'so'":
  the model's own language list contains 'so'.
  `GET /v1/user/subscription` -> HTTP 401 missing_permissions (the key lacks
  user_read; it is TTS/voices-scoped). Credit state therefore cannot be read
  via API; cost estimates use the published pricing (TTS = 1 credit per
  character; plan allowances Free 10k / Starter 30k / Creator 121k).
- Secret scan: run at the end of the session with the mirror publish (see J9);
  repo .gitignore now also covers a root .env (hardening, commit 977fb5c).

## J5 Preflight

`python run.py preflight`, FIRST run (before the key fix and before J8):
```
PASS  ffmpeg on PATH  /usr/bin/ffmpeg
PASS  ffprobe on PATH  /usr/bin/ffprobe
PASS  ELEVENLABS_API_KEY set
PASS  REPLICATE_API_TOKEN set
PASS  CONSENT.md signed  Mayo Ali Aden
PASS  avatar license (CONSENT.md sec 2)  @jean_philanthrope on 2026-09-27
FAIL  avatar image  assets/avatar.png
PASS  Modal app jiheeye-ultra deployed  assemble_remote reachable
PASS  lipsync model schema  veed/fabric-1.0
PASS  broll model schema  kwaivgi/kling-v2.1
FAIL  ElevenLabs model eleven_v3 available  HTTP 400
WARN  eleven_v3 lists Somali (so)  ids seen: []
PREFLIGHT EXIT: 1
```
The two FAILs were the missing avatar (J8 had not run yet) and the invalid
key. FINAL run (after J8 + key fix), all PASS, exit 0:
```
[03:45:14] [preflight] PASS  ffmpeg on PATH  /usr/bin/ffmpeg
[03:45:14] [preflight] PASS  ffprobe on PATH  /usr/bin/ffprobe
[03:45:14] [preflight] PASS  ELEVENLABS_API_KEY set
[03:45:14] [preflight] PASS  REPLICATE_API_TOKEN set
[03:45:14] [preflight] PASS  CONSENT.md signed  Mayo Ali Aden
[03:45:14] [preflight] PASS  avatar license (CONSENT.md sec 2)  @jean_philanthrope on 2026-09-27
[03:45:14] [preflight] PASS  avatar image  assets/avatar.png
[03:45:15] [preflight] PASS  Modal app jiheeye-ultra deployed  assemble_remote reachable
[03:45:16] [lipsync] veed/fabric-1.0 schema OK (version 21b8969754f6)
[03:45:16] [preflight] PASS  lipsync model schema  veed/fabric-1.0
[03:45:16] [broll] kwaivgi/kling-v2.1 schema OK (version daad218feb71)
[03:45:16] [preflight] PASS  broll model schema  kwaivgi/kling-v2.1
[03:45:16] [preflight] PASS  ElevenLabs model eleven_v3 available  HTTP 200
[03:45:16] [preflight] PASS  eleven_v3 lists Somali (so)  ids seen: ['af','ar','hy','as','az','be','bn','bs','bg','ca','ceb','ny','hr','cs','da','nl','en','et','fil','fi','fr','gl','ka','de','el','gu','ha','he','hi','hu','is','id','ga','it','ja','jv','kn','kk','ky','ko','lv','ln','lt','lb','mk','ms','ml','zh','mr','ne','no','ps','fa','pl','pt','pa','ro','ru','sr','sd','sk','sl','so','es','sw','sv','ta','te','th','tr','uk','ur','vi','cy']
PREFLIGHT EXIT: 0
```

## J6 Voice (Modal cleanup DONE; ElevenLabs clone BLOCKED at the provider)

- Modal run (`python run.py voice`, timed):
  ```
  [03:46:41] [voice_prep] voice sample ready: /home/muads/jiheeye-ultra/pipeline/assets/voice/voice_sample.wav (9.5 MB, rendered on Modal)
  [03:46:45] [modal_client] volume GC removed jobs/voice/9651dcb6578c75ba
  [03:46:45] [voice_clone] consent OK, voice owner: Mayo Ali Aden
  real    1m22.390s
  ```
  Modal runtime recorded: 82 s wall for the whole command (staging + container
  + Demucs + denoise + loudnorm on a 4-core Modal CPU container).
  Artifact: pipeline/assets/voice/voice_sample.wav (9,527,382 bytes) with
  cache stamp voice_sample.wav.key.
- ElevenLabs instant voice clone FAILED — provider-side entitlement, not a
  code or key problem:
  ```
  FAILED: ElevenLabs voice clone failed 400: {"detail":{"type":"payment_required",
  "code":"paid_plan_required","message":"Your subscription does not include
  instant voice cloning. Please upgrade your plan.",
  "status":"can_not_use_instant_voice_cloning",
  "request_id":"7185e9dfc60a80a303c3b287f243188b"}}
  ```
  Cost of the failed call: $0.00 (rejected before execution). The soccer
  account's tier has no IVC. UNBLOCK (Mayo's side only): put an sk_ secret
  key of an ElevenLabs account that includes Instant Voice Cloning into
  pipeline/.env (replace the ELEVENLABS_API_KEY line). ElevenLabs pricing
  page: IVC is a paid-tier feature (Starter $5/mo and up); TTS = 1 credit per
  character. The $10 cap can absorb Starter for this month. THE MOMENT the
  key lands: rerun `python run.py voice` — the Modal part is cached, so the
  rerun is fast and adds no Modal cost; then `voice_id.txt` appears.
- voice_id.txt does NOT exist yet (clone blocked); ELEVENLABS_VOICE_ID is not
  set. Nothing else in the pipeline can legally substitute (the soccer
  VOICE_ID=onwK4e9Z... is a preset/other voice, not the consented owner's
  clone; using it would bypass the consent design and is refused).

## J7 Test script + allow-unreviewed (prepared; run blocked by J6)

- `pipeline/scripts/ad00_test.json` created = ad01.json minus the "product"
  broll scene (commit de86a98): ids hook, problem, cta; all avatar;
  `reviewed_by_native_speaker` stays false; notes preserved.
- `--allow-unreviewed` added to run.py (commit de86a98): argparse flag +
  guard in main():
  ```
  if a.allow_unreviewed and not (a.cmd == "make" and a.until == "tts"):
      die("--allow-unreviewed is valid ONLY with: make <script> --until tts ...")
  ```
  and `validate_script(script, allow_unreviewed=False)` gained the escape
  hatch; make() prints `UNREVIEWED: audio for Mayo's review` when it runs
  unreviewed. Docstring updated with the example command.
- Guard-rail tests (real runs):
  ```
  FAILED: --allow-unreviewed is valid ONLY with: make <script> --until tts (brief 02 J7: unreviewed audio never proceeds past TTS)
  exit: 1                                  (make without --until: blocked)
  make --until lipsync with flag exit: 1   (blocked)
  preflight with flag exit: 1              (blocked)
  ```
- Offline regression suite (with the new validator test):
  ```
  PASS validator blocks unreviewed script
  PASS validator allow_unreviewed accepts unreviewed script
  PASS validator requires avatar hook first
  ...
  ALL OFFLINE TESTS PASSED      (exit 0)
  ```
- THE RUN IS NOT EXECUTED YET: `make --until tts` needs the cloned voice
  (J6). When Mayo's IVC-capable key lands, the exact command is:
  ```
  cd ~/jiheeye-ultra/pipeline && .venv/bin/python run.py make scripts/ad00_test.json --until tts --allow-unreviewed
  ```
  then the run's vo.mp3 is copied to
  /mnt/c/Users/muads/Claude/jiheeye-review/ad00_vo.mp3 (ad00_script.txt is
  already written there). TTS cost estimate before that call: ad00 text is
  ~250 chars -> ~250-500 credits at 1-2 credits/char; marginal USD ~$0.00
  against the account's plan allowance (well inside the $10 cap).

## J8 Avatar 9:16 extend (COMPLETE)

Method: masked generative fill with the brief's candidate model, then a
pixel-exact paste-back so the face is untouched by the model. Canvas/mask
composition and all measurements were one-off asset prep; the pixel compute
(scale, paste-back, preview) ran on Modal as an ad-hoc `modal run`
(ephemeral app jiheeye-avatar-finish; nothing deployed, no orphan tool).

- Schema check (free lookup via ugc.replicate_io.input_schema):
  ```
  version: 41c767bcbfffe54ef8f05eb4d0100f9314790f7fc43a7b88d73ec06839deddb9
  required: ['prompt', 'image']
  mask: "A black-and-white image ... Black areas will be preserved while white
         areas will be inpainted. Must have the same size as image."
  outpaint enum: None / Zoom out 1.5x / Zoom out 2x / Make square /
                 Left outpaint / Right outpaint / Top outpaint / Bottom outpaint
  ```
  The outpaint presets cannot produce 9:16 from a square (Zoom-out keeps the
  square aspect; side outpaints do one fixed side), so a composed canvas +
  explicit mask was used instead. Confirmed suitable model: black-forest-labs/flux-fill-pro.
- Canvas: source 511x512 lanczos-upscaled to 1080x1082, placed at y=50 on a
  1080x1920 canvas; mask white ONLY on the extension bands (top 0-50,
  bottom 1132-1920), black over the whole source region.
- Paid call 1: prediction ff7q5w1smsrmy0d0wwc9wqngxc, succeeded 13.9 s,
  metrics {"image_count": 1, "image_output_count": 1, "predict_time": 13.89}.
  OUTPUT CAME BACK 810x1440 (the model caps resolution at 0.75x), so the
  brief's "then upscale if needed" applied.
- Preservation measurement (output rescaled to 1080x1920, crop y=50..1132 vs
  scaled source): PSNR 43.3 dB, SSIM 0.987 — structurally intact but
  resampled by the model's round-trip.
- Defect found by looking at the artifact: the 50 px generated top band was
  visibly darker than the backdrop (a seam that would appear in every ad).
  Fix: top band replaced by a deterministic edge-smear of the source's own
  top rows (crop top 2 rows -> scale to 1080x50 -> gblur), mask white ONLY on
  the bottom band; paid call 2: prediction p4xbdaha3srmw0d0wwk9gvqcac,
  succeeded 16.5 s, same 810x1440 output.
- Modal finisher (`modal run finish_modal.py`, ad-hoc):
  ```
  AVATAR-FINISH-OK avatar=3926908B preview=2408573B modal_wall=9.7s
  ```
  (upscale 810x1440 -> 1080x1920 lanczos, paste pristine source over
  y=50..1132, build side-by-side preview).
- Face-intact proof on the final file:
  ```
  ffmpeg ... crop=1080:1082:0:50 ... psnr
  PSNR r:inf g:inf b:inf a:inf average:inf min:inf max:inf
  ```
  Infinite PSNR = the face/hair/suit region is pixel-identical to the
  deterministically-upscaled source. The model touched only the bands.
- Deliverables: pipeline/assets/avatar.png (1080x1920, ffprobe verified) and
  /mnt/c/Users/muads/Claude/jiheeye-review/avatar_preview.png (source left,
  final right). Both flux-fill calls and the Modal runs are in the spend CSV.

## J9 Report, repo, mirror

- This report + reports/brief02_spend.csv; committed and pushed to the
  private repo; mirror published by tools/push_status.sh (mp3/png stay
  hard-denied; the mirror scan runs on every publish).
- Spend ledger (reports/brief02_spend.csv):
  ```
  time_utc,provider,model,units,est_usd,cumulative_usd
  2026-09-28T03:18Z,replicate,black-forest-labs/flux-fill-pro,1 image (2.07MP in / 1.17MP out),0.11,0.11
  2026-09-28T03:33Z,replicate,black-forest-labs/flux-fill-pro,1 image (2.07MP in / 1.17MP out),0.11,0.22
  2026-09-28T03:28Z,modal,jiheeye-avatar-finish (ad-hoc run),2 runs x ~11s CPU 1-core,0.01,0.23
  2026-09-28T03:46Z,modal,jiheeye-ultra/voice_prep_remote,1 run 82s wall (4-core container),0.01,0.24
  2026-09-28T03:46Z,elevenlabs,instant-voice-cloning,attempted - REJECTED paid_plan_required,0.00,0.24
  ```
  Cumulative estimate: $0.24, well under the $10 cap. Pricing sources:
  BFL FLUX models ~$0.05/MP linear (bfl.ai pricing docs; 4MP ~= $0.20);
  Modal usage-based (seconds of CPU, negligible at this scale); ElevenLabs
  TTS 1 credit/char (pricing page). Replicate account holds $10 credit
  (Mayo, session chat).

## Gate status (GATES.md brief 02 section)

Met and evidenced: G13 (verbatim), G14 (clip staged + deviation documented +
inbox kept), G15 (consent OK), G16 (keys), G17 (preflight exit 0), G19
(ad00_test.json), G20 (offline suite), G22 (avatar 1080x1920 + preview),
G23 (spend CSV <= 10), G24 (this report).
NOT met yet, blocked on Mayo's ElevenLabs plan/key: G18 (voice_id.txt),
G21 (ad00_vo.mp3 review files), G25/G26 (final reverify + mirror publish
after the last code commit — this report's commit is followed by
gate-check --reverify; G26 will pass only when J6-J7 complete).