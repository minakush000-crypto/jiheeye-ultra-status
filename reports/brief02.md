# Brief 02 report: voice clone, first Somali audio, vertical avatar ($10 cap)

Engineer: Flash. Session date: 2026-09-28. Brief: briefs/brief02.md (827 words,
committed verbatim as 0dbe260). Coordinator: Claude (claude.ai Project "jiheeye
ultra"). Every claim below names the command that proved it; output is quoted
from this session's real runs. STATUS: brief 02 CLOSED on the engineering
side (session 2, 2026-09-28 ~20:00 CDT / 2026-09-29 01:00Z): Mayo upgraded the
ElevenLabs account to an IVC-capable plan and put its new sk_ key in
pipeline/.env (mtime 19:57:41 CDT); J6 completed (voice id
SzG54l8uNzFFwtJDDtxw, Modal stage was a cache hit), J7's ad00 test audio
rendered and delivered to Mayo's review folder, gates G18/G21 re-established
with evidence, and the final gate-check --reverify paste sits under
"REVERIFY" below. Estimated spend total: $5.25 of the $10 cap ($5.00 =
Mayo's Starter month subscription, $0.24 usage + $0.01 QA rerun; reports/brief02_spend.csv).
Mayo's next action: listen to
/mnt/c/Users/muads/Claude/jiheeye-review/ad00_vo.mp3; brief 03 (lip-sync)
starts on approval.

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
- ADDENDUM (session 2): Mayo put the new IVC-capable sk_ key into
  pipeline/.env; preflight was re-run FREE (same checks, key identity
  changed) - ALL PASS, exit 0:
  ```
  [20:02:09] [preflight] PASS  ffmpeg on PATH  /usr/bin/ffmpeg
  [20:02:09] [preflight] PASS  ffprobe on PATH  /usr/bin/ffprobe
  [20:02:09] [preflight] PASS  ELEVENLABS_API_KEY set
  [20:02:09] [preflight] PASS  REPLICATE_API_TOKEN set
  [20:02:09] [preflight] PASS  CONSENT.md signed  Mayo Ali Aden
  [20:02:09] [preflight] PASS  avatar license (CONSENT.md sec 2)  @jean_philanthrope on 2026-09-27
  [20:02:09] [preflight] PASS  avatar image  assets/avatar.png
  [20:02:10] [preflight] PASS  Modal app jiheeye-ultra deployed  assemble_remote reachable
  [20:02:11] [lipsync] veed/fabric-1.0 schema OK (version 21b8969754f6)
  [20:02:11] [preflight] PASS  lipsync model schema  veed/fabric-1.0
  [20:02:12] [broll] kwaivgi/kling-v2.1 schema OK (version daad218feb71)
  [20:02:12] [preflight] PASS  broll model schema  kwaivgi/kling-v2.1
  [20:02:12] [preflight] PASS  ElevenLabs model eleven_v3 available  HTTP 200
  [20:02:12] [preflight] PASS  eleven_v3 lists Somali (so)  ids seen: ['af', 'ar', 'hy', 'as', 'az', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fil', 'fi', 'fr', 'gl', 'ka', 'de', 'el', 'gu', 'ha', 'he', 'hi', 'hu', 'is', 'id', 'ga', 'it', 'ja', 'jv', 'kn', 'kk', 'ky', 'ko', 'lv', 'ln', 'lt', 'lb', 'mk', 'ms', 'ml', 'zh', 'mr', 'ne', 'no', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sr', 'sd', 'sk', 'sl', 'so', 'es', 'sw', 'sv', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi', 'cy']
  PREFLIGHT-EXIT: 0
  ```

## J6 Voice (COMPLETE: Mayo's IVC plan landed; clone created)

Mayo's unblock landed this session (input age: pipeline/.env mtime
2026-09-28 19:57:41 CDT, stated at 20:0x): the file holds exactly ONE
ELEVENLABS_API_KEY line (sk_ prefix, 51 chars, sha16 c07aa7f566131b22 — a
DIFFERENT key from session 1's machine-found one, c4304e73dcc5) plus
REPLICATE_API_TOKEN. No shell-level export shadows it (printenv: set only in
pipeline/.env; the loader uses os.environ.setdefault, so with no shell copy
present the .env value is what the pipeline uses).

- Free subscription READ with the new key — HTTP 200 where session 1's key
  got 401 missing_permissions (this key's scope includes user_read):
  ```
  tier: starter | character_count: 0 | limit: 37438 | GET /v1/user/subscription
  ```
  Starter includes Instant Voice Cloning, and the counter starts at 0, so
  the TTS cost below is measured against a known baseline.
- History (session 1) — Modal part COMPLETE (`python run.py voice`, timed):
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
- History (session 1): the clone call FAILED — provider-side entitlement,
  not a code or key problem:
  ```
  FAILED: ElevenLabs voice clone failed 400: {"detail":{"type":"payment_required",
  "code":"paid_plan_required","message":"Your subscription does not include
  instant voice cloning. Please upgrade your plan.",
  "status":"can_not_use_instant_voice_cloning",
  "request_id":"7185e9dfc60a80a303c3b287f243188b"}}
  ```
  Cost of the failed call: $0.00 (rejected before execution). The account
  then in use had no IVC.
- THIS SESSION'S COMPLETED RUN (`time .venv/bin/python run.py voice`; per
  Mayo's instruction the cached Modal voice sample was reused):
  ```
  [20:00:52] [voice_prep] cached -> /home/muads/jiheeye-ultra/pipeline/assets/voice/voice_sample.wav
  [20:00:52] [voice_clone] consent OK, voice owner: Mayo Ali Aden
  [20:01:00] [voice_clone] cloned voice id SzG54l8uNzFFwtJDDtxw saved to /home/muads/jiheeye-ultra/pipeline/assets/voice/voice_id.txt
  real    0m11.325s
  user    0m1.861s
  sys     0m0.668s
  ```
  Exit 0 in 11.3 s. The Modal stage printed `cached ->` (pure cache hit:
  zero new Modal compute, no volume upload). The instant voice clone
  ACCEPTED the 9,527,382-byte clean sample and returned voice id
  SzG54l8uNzFFwtJDDtxw, saved to pipeline/assets/voice/voice_id.txt
  (gitignored, 20 chars). The stage logs a WARNING when ElevenLabs sets
  requires_verification; NO such warning printed, so the clone needs no
  dashboard verification step. IVC creation cost: character_count still 0
  right after (no credit deduction observed for creating the voice).

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
- THE RUN (executed this session, the exact command briefed above):
  ```
  UNREVIEWED: audio for Mayo's review
  [20:01:17] [voice_clone] consent OK, voice owner: Mayo Ali Aden
  [20:01:17] [voice_clone] reusing cloned voice SzG54l8uNzFFwtJDDtxw (delete /home/muads/jiheeye-ultra/pipeline/assets/voice/voice_id.txt to re-clone)
  [20:01:17] [tts] requesting TTS: 248 chars, model=eleven_v3, lang=so
  [20:01:30] [tts] voiceover -> /mnt/d/scratch/jiheeye-ultra/runs/ad00_test/vo.mp3
  real    0m18.485s
  user    0m1.213s
  sys     0m1.255s
  MAKE-EXIT: 0
  ```
  The UNREVIEWED banner printed BEFORE the paid call; only the TTS stage ran
  (--until tts: timeline/lipsync/broll/assemble never started). Exit 0, and
  exactly ONE ElevenLabs TTS call was made (one call per ad rule).
- Cost, measured at the provider rather than guessed: full_text = 248 chars
  (77 + 82 + 87 with joins, printed by the stage); starter allowance 37,438
  credits; subscription character_count read 0 before and still 0 ~2 minutes
  after the call (metering lag suspected; upper bound 248 credits = 0.66% of
  the allowance, $0.00 marginal inside the plan). Spend rows appended.
- Review deliverables (G21):
  - /mnt/c/Users/muads/Claude/jiheeye-review/ad00_vo.mp3 — cp from
    runs/ad00_test/vo.mp3; BYTE-IDENTICAL:
    ```
    9beab8d48c1b1f17022ddfbeb0d76090dbf248cef088a2e8a09d68e70b2cefeb  /mnt/d/scratch/jiheeye-ultra/runs/ad00_test/vo.mp3
    9beab8d48c1b1f17022ddfbeb0d76090dbf248cef088a2e8a09d68e70b2cefeb  /mnt/c/Users/muads/Claude/jiheeye-review/ad00_vo.mp3
    ```
    252,073 bytes, 15.68 s (ffprobe format=duration).
  - /mnt/c/Users/muads/Claude/jiheeye-review/ad00_script.txt — session 1's
    copy was stale (272 bytes; content no longer matched the current
    ad00_test.json); REWRITTEN this session directly from the script JSON
    (session-2 fix #1).
  - Mayo's next action: listen to ad00_vo.mp3 on Windows. Brief 03 wires the
    voice to the avatar after Mayo's approval; ad00_test.json itself stays
    reviewed_by_native_speaker false (test audio).

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
  2026-09-28T23:57Z,elevenlabs,starter-plan (Mayo's own purchase),1 month,5.00,5.24
  2026-09-29T01:02Z,modal,jiheeye-ultra/voice_prep_remote,0 runs - cache hit on rerun,0.00,5.24
  2026-09-29T01:02Z,elevenlabs,instant-voice-cloning,1 voice created (9.1 MiB sample) - SUCCESS no fee observed,0.00,5.24
  2026-09-29T01:02Z,elevenlabs,eleven_v3,ad00_test TTS 248 chars (counter still 0 at +2min),0.00,5.24
  2026-09-29T01:12Z,modal,tests/test_modal.py (gate rerun),1 run 12 QC checks,0.01,5.25
  ```
  Cumulative estimate: $5.25 of the $10 cap ($5.00 = Mayo's Starter month
  purchase at unblock, $0.24 usage + $0.01 QA rerun). Session 2 replaced
  guesses with a live source: the new key CAN read GET /v1/user/subscription
  (tier starter, character_count 0, limit 37438), so TTS cost is measured
  against the allowance, not a pricing-page estimate. Remaining sources as
  before: BFL FLUX ~$0.05/MP linear (bfl.ai pricing docs); Modal
  usage-based (seconds of CPU, negligible at this scale); Replicate holds
  $10 credit (Mayo, session chat). The TTS row books $0.00 marginal with
  the counter-lag caveat; if provider billing later shows a deduction, the
  row gets a correction.

## Gate status (GATES.md brief 02 section) — brief 02 CLOSED on the engineering side

All 27 gates evidence-backed as of the reverify paste below: G13-G17, G19,
G20, G22-G25 as before; G18 RECREATED met (voice id
SzG54l8uNzFFwtJDDtxw on disk, Modal runtime + IVC result in J6), G21
RECREATED met (ad00_vo.mp3 + ad00_script.txt byte-verified on C:, UNREVIEWED
banner pasted in J7), G26 met (raw gate-check --reverify output pasted under
REVERIFY below, run from the shell after the last commit of this session).
Session-2 fixes applied while closing: ad00_script.txt rewritten from the
script JSON (stale 272-byte copy), report J6/J7/gate sections rewritten with
the fresh raw outputs, spend rows appended (usage $0.24 + $0.01 QA rerun; $5.25 total with
Mayo's Starter month).
Interim ABANDON notes removed from GATES.md; the interim 24/27 note stays as
history there.

## REVERIFY

REVERIFY-OUTPUT-BELOW

(command: `node ~/.claude/skills/unlazy/scripts/gate-check.mjs --approve --reverify --timeout 600 GATES.md`, run from
the repo root, in the shell, AFTER the last code commit of this session -
dce8a88 "chore: archive_b2 manifest inputs parameterized". Result: exit 0,
"GATES.md: 27 gates" / "ALL MET (27 met, reran: 27, previously met
reverified: 27)". Approval mechanics: approvals bind to the session
environment, so the combined --approve --reverify mode re-approves and re-runs
every oracle (reverify alone listed stale-session gates as "reverify not
run"). Two earlier verification passes hit timeouts on the offline suite
(180 s and 300 s per-gate: the suite takes ~3 m on this box; measured
standalone 3m04.9s with SUITE-EXIT 0) and one concurrent pass filled the RAM
backed /tmp ("No space left on device"; cleaned /tmp/ugc_* leftovers, freed
1.4 GB). This final pass ran with a 600 s per-gate budget, jobs=1. Raw
output follows.)

```
  RUN  GATES:G0 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G1 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G2 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G3 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G4 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G5 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G6 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G7 shell=/bin/bash cwd=/home/muads/jiheeye-ultra/pipeline PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G8 shell=/bin/bash cwd=/home/muads/jiheeye-ultra/pipeline PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G9 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G10 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G11 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G12 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G13 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G14 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G15 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G16 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G17 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G18 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G19 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G20 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G21 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G22 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G23 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G24 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G25 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  RUN  GATES:G26 shell=/bin/bash cwd=/home/muads/jiheeye-ultra PATH=/home/muads/.bun/bin:/home/muads/.local/bin:/home/muads/.bun/bin:/home/muads/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/muads/.local/bin:/snap/bin:/home/muads/.claude/plugins/cache/thedotmack/claude-mem/13.28.0/bin
  PASS GATES:G0: this ledger states outcomes that can fail
       exit=0; EXPECT=matched; output=sha256=48630b7361dd44ee870917b12c3d19b9d7bdea738aaca16bb04d4cab83b772d2; bytes=8
  PASS GATES:G1: briefs/brief01.md is a byte-exact copy of the coordinator brief
       exit=0; EXPECT=matched; output=sha256=e22f85bc58b7e632713eeded83288767637bbdd12bfbfc2abf49417795fbd5da; bytes=18
  PASS GATES:G2: scaffolding files exist and DECISIONS.md seeds the five closed decisions
       exit=0; EXPECT=matched; output=sha256=3545fe373d22a727eddfff776643da807b43f9d3431c5993054e9972e3b96204; bytes=12
  PASS GATES:G3: project skill installed at .claude/skills with the repo path set
       exit=0; EXPECT=matched; output=sha256=d820f7ee173e38f9762669b3ea34ce3a1b689b4ff6fd0560d601cc02d8827423; bytes=9
  PASS GATES:G4: pipeline/.venv has every runtime dependency including modal
       exit=0; EXPECT=matched; output=sha256=8df0145c04928e1ac952b9c0ce8511dd979a81fa865b566ff0e4b58a1bec4c5a; bytes=8
  PASS GATES:G5: config points at the D: scratch tree, backend is modal, disk guard is wired into run.py
       exit=0; EXPECT=matched; output=sha256=8736ec8a3562172ff0d8a6e55edd24a92408d46d2ebe2c5cdc28ee94f9d8f61a; bytes=10
  PASS GATES:G6: the jiheeye-ultra Modal app is deployed
       exit=0; EXPECT=matched; output=sha256=2e1a28d1adc2dba711644966d0ffc9944831b57675f4ee8f6019bb5b7b59a8fb; bytes=18
  PASS GATES:G7: offline end-to-end test passes with the real local backend
       exit=0; EXPECT=matched; output=sha256=738ceeecab24ccc07fe3dc4fa2af92f531f652bfd5b41ea3e22e13b87dee6e62; bytes=4825
  PASS GATES:G8: Modal render test passes with all 12 QC checks green on a file rendered on Modal
       exit=0; EXPECT=matched; output=sha256=55759ee90f1d292d6a6d6af41987f82ba46bea58cfaf696b0ea34720a54c6a84; bytes=1140
  PASS GATES:G9: private GitHub repo has main pushed
       exit=0; EXPECT=matched; output=sha256=a1b03b952d3bdcccbe50d6d8485cceef64fe8b481e8c003bb995af6d41390caa; bytes=16
  PASS GATES:G10: public mirror contains only allowlisted files and none of the hard-denied kinds
       exit=0; EXPECT=matched; output=sha256=57be2f5dc30bbdf8e2b9a4c4cdf4031eecf990f02ff09fc1c9fda9a724dce17f; bytes=27
  PASS GATES:G11: the old C: copy is deleted
       exit=0; EXPECT=matched; output=sha256=67bc10f574ad82773193f221191b3a41fc75b2e0a03aad41cfebc085ef2af5b1; bytes=16
  PASS GATES:G12: reports/brief01.md covers every job J1-J9 with commands and outputs
       exit=0; EXPECT=matched; output=sha256=b5d799b8ae3e8271ceb1d56f5cb1568d96693dfbb46d5b606ffa2133a3bc5c18; bytes=10
  PASS GATES:G13: briefs/brief02.md is a byte-exact copy of the coordinator brief
       exit=0; EXPECT=matched; output=sha256=be5e093e6089ff7d0d4f3a871f99bddd22b854ce5811545fd07da79962254ae9; bytes=20
  PASS GATES:G14: voice clip staged at pipeline/assets/voice/raw/clip1.mp3; its real sha256 recorded; the deviation from the brief's stated prefix 35cb41ae21cf94e4 investigated with decoded-PCM evidence and documented in DECISIONS.md; the inbox delete skipped because the verify precondition failed
       exit=0; EXPECT=matched; output=sha256=c3314d548a3156b2d74981a1919c77a3f8cac80d687f16723832e286ed23a343; bytes=33
  PASS GATES:G15: CONSENT.md voice gate passes (J3, output pasted in report)
       exit=0; EXPECT=matched; output=sha256=54d68f1353775987e31fa5c17c784640b9698df076a5a3ce9b443661fd4603f5; bytes=25
  PASS GATES:G16: both API keys present in pipeline/.env; machine-wide ElevenLabs key search done (paths/names only, no values)
       exit=0; EXPECT=matched; output=sha256=1d9ad8cf5f7d02e54f4040a103991a3bf2a9999505528337cc783177954a6da7; bytes=8
  PASS GATES:G17: preflight exits 0 (schema lookups, consent, Modal reachability, ElevenLabs model+Somali listing; no paid calls)
       exit=0; EXPECT=matched; output=sha256=194fae0d7707faa7b6d81e0ce295232fb1f37cdad787f4a6b43aacc51b923119; bytes=1422
  PASS GATES:G18: voice stage done: clean sample + cloned voice id exist on disk, Modal runtime and IVC result recorded in the report
       exit=0; EXPECT=matched; output=sha256=5fca3d663ffb8009713dc69ddb65f826436c151e77e10204afbe64b673a6fff0; bytes=15
  PASS GATES:G19: pipeline/scripts/ad00_test.json is ad01 minus the product scene with reviewed_by_native_speaker still false
       exit=0; EXPECT=matched; output=sha256=1af73591f76a0bebcfe942c1c1f1c32685b9181d72a5b3c55949d21d4449270c; bytes=8
  PASS GATES:G20: --allow-unreviewed implemented (valid only with --until tts) and the offline regression suite still passes
       exit=0; EXPECT=matched; output=sha256=90c2a968a832dbcf389b9cb1c12ae2404ec6239eb351685c4f1ef75f1d279ed1; bytes=25
  PASS GATES:G21: make --until tts --allow-unreviewed ran; UNREVIEWED line printed; ad00_vo.mp3 + ad00_script.txt on C: for Mayo
       exit=0; EXPECT=matched; output=sha256=b89d0bd43608349f60f958ddab2c54b3e97652dcda6b04c1c13b13f8a86551cd; bytes=16
  PASS GATES:G22: avatar extended to 1080x1920 (9:16) and preview written to C:; method (model+schema, or blurred fallback) documented
       exit=0; EXPECT=matched; output=sha256=3b09ad7866579f74e0b249d054df55c4888da0cf03b7ddace89d5d68f79bb1d8; bytes=10
  PASS GATES:G23: spend ledger complete and cumulative <= $10
       exit=0; EXPECT=matched; output=sha256=ae98571990b4eb016f73b43488e5fa5da870664cf841cd42242ec6ce93b85ea5; bytes=14
  PASS GATES:G24: reports/brief02.md holds RAW pasted outputs for J2-J8 (sha256sum, consent gate, key search, preflight, voice run, make run, model schema) and the spend CSV
       exit=0; EXPECT=matched; output=sha256=b5d799b8ae3e8271ceb1d56f5cb1568d96693dfbb46d5b606ffa2133a3bc5c18; bytes=10
  PASS GATES:G25: private repo pushed and public mirror republished clean
       exit=0; EXPECT=matched; output=sha256=57be2f5dc30bbdf8e2b9a4c4cdf4031eecf990f02ff09fc1c9fda9a724dce17f; bytes=27
  PASS GATES:G26: gate-check --reverify ran AFTER the last code commit and its output is pasted in reports/brief02.md under the REVERIFY marker (the reverify command itself runs from the shell, not from inside a gate)
       exit=0; EXPECT=matched; output=sha256=c864cf7a845048dcd561448dbc14c851a000031cf65ba9e2ae5b57a4de0a169c; bytes=19
GATES.md: 27 gates
ALL MET (27 met, reran: 27, previously met reverified: 27)
```
