# Jiheeye Ultra UGC pipeline: architecture, review, execution blueprint

Written 2026-09-27. Authorship: the goal (Somali UGC ads for TikTok/YouTube Shorts,
the owner's own voice, a chosen avatar, product B-roll, hands-free) came from the
owner. The stage design, file layout, config format, consent gate, caching and QC
gate below were designed by Claude, not required by the owner.
Updated 2026-09-28 (brief 01): Demucs voice cleanup and the final ffmpeg assembly
now run on Modal by default (section 5); sections 1-4 describe the stage design,
and their "local" wording predates the Modal port.
Evidence marks: ● verified (command named) · ◑ believed · ○ not examined · ★ load-bearing

## 1. What the pipeline does

One command turns a reviewed Somali script into a finished 1080x1920 MP4 in the
owner's cloned voice, spoken by the avatar, cut with product B-roll, captioned,
loudness-normalized, and machine-checked.

```
ONE-TIME SETUP                       PER AD (python run.py make scripts/adNN.json)
────────────────                     ─────────────────────────────────────────────
owner's own clips                    script JSON (scenes: avatar | broll)
   │  voice_prep (local, free)          │  validate: native-speaker review flag, hook = avatar
   ▼                                    ▼
voice_sample.wav                     tts ── ElevenLabs eleven_v3, lang so, WITH timestamps (paid)
   │  CONSENT.md gate                   │  vo.mp3 + alignment.json
   ▼                                    ▼
voice_clone ── ElevenLabs IVC        timeline (local) ── scene cut points + captions.srt
   │  (paid, one time)                  │
   ▼                                    ├── lipsync ── Replicate veed/fabric-1.0: avatar.png + FULL vo (paid, 1 call)
voice_id.txt                            ├── broll ──── Replicate kwaivgi/kling-v2.1: product.png + prompt (paid, 1 per broll scene)
                                        ▼
                                     assemble (local ffmpeg) ── cut avatar at scene times, drop in B-roll,
                                        │                      continuous vo under all of it, burn captions,
                                        │                      optional music bed, loudnorm -14 LUFS
                                        ▼
                                     qc (local) ── 12 checks on the file itself; exit 1 on any FAIL
                                        ▼
                                     runs/<id>/final.mp4 + manifest.json
```

Design decisions (Claude's):

| Decision | Why |
|---|---|
| One TTS call for the whole script | Continuous delivery; no seams between scenes. Scene cut points come from the character timestamps. |
| One lipsync call on the whole voiceover, then cut | One paid call instead of one per scene; mouth stays in sync because audio is never re-timed. |
| B-roll replaces avatar picture only, voice keeps running | Standard UGC grammar: face for hook and CTA, product in the middle. |
| Every paid stage caches on a hash of its inputs | A re-run after a crash never pays twice. Delete the `.key` file to force a redo. |
| Model input names validated against Replicate's live schema before paying | Input names change between model versions. Hard-coded names fail silently or cost a failed run. |
| QC reads the output file, not the stage logs | A stage can print success and still produce a bad file. |
| Consent gate on cloning; AI-label reminder on every run | Owner's voice only; platforms require AI disclosure for realistic synthetic people. |

## 2. Review of the Google-chat plan

Every item below is a defect in the code or advice Google produced earlier in the conversation.

| # | Defect | Evidence | Fixed by |
|---|---|---|---|
| 1 ★ | XTTS-v2 was called with `language="so"`. XTTS-v2 supports 17 languages, and Somali is not one of them. | ● WebFetch huggingface.co/coqui/XTTS-v2 language list | ElevenLabs `eleven_v3` |
| 2 ★ | ElevenLabs `eleven_multilingual_v2` was used for Somali. Its 29-language list does not include Somali. | ● WebFetch elevenlabs.io/docs/overview/capabilities/text-to-speech | `eleven_v3`, whose language list includes Somali (● WebFetch help.elevenlabs.io "What languages do you support?") |
| 3 | The ElevenLabs URL was `https://elevenlabs.io{VOICE_ID}`, with the wrong host and no path. | read the pasted code | `https://api.elevenlabs.io/v1/text-to-speech/{id}/with-timestamps` (● WebFetch API reference) |
| 4 ★ | The "Playwright automation" for Hedra/Kling was commented out. It did nothing, then printed "✓ Web rendering pipeline finished successfully". | read the pasted code | Real API calls through Replicate |
| 5 ★ | `compile_final_video` created **empty placeholder files** when inputs were missing, never ran ffmpeg (the `subprocess.run` line was commented out), and printed "SUCCESS". | read the pasted code | `assemble.py` runs ffmpeg; `qc.py` checks the file |
| 6 | The codec was typed `libx246` (it should be libx264), so ffmpeg would have failed even if it ran. | read the pasted code | fixed |
| 7 | Scene times were hard-coded (`trim=0:12`, etc.) and didn't match the audio. Audio was mapped from the avatar clip. | read the pasted code | timings come from TTS alignment; audio is the voiceover |
| 8 | Replicate calls pinned version hashes that were never checked. | ○ not tested (no token here) | live schema lookup; no pinned hashes |
| 9 | "Claude cannot execute commands." That's wrong for this setup: Claude Code / Cowork can run the pipeline. | n/a | the skill runs it |
| 10 | Somali script lines were never reviewed by a native speaker (e.g. "fican" vs "fiican"). | ◑ spelling, owner to confirm | `reviewed_by_native_speaker` flag blocks the run |
| 11 | Latent bug: `astype(np.int16)` on a float WAV gives total silence. | ● python test: peak 0.4999 → 0 after cast | `soundfile` writes PCM_16 correctly |
| 12 | The plan had no quality check at all. | read the pasted code | `qc.py`, 12 checks |

Pattern to remember: items 4 and 5 are code that exists, looks authoritative,
reports success, and never ran.

## 3. Auto-execution blueprint

Where things run: **WSL2 Ubuntu terminal**, in the repo's `pipeline/` folder.
Claude Code (or Cowork linked to this folder) runs the same commands.

### One-time setup

```bash
cd ~/jiheeye-ultra/pipeline
sudo apt update && sudo apt install -y ffmpeg fonts-dejavu-core python3-venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste ELEVENLABS_API_KEY and REPLICATE_API_TOKEN into .env
```

Then place the input files:

- `CONSENT.md` (repo root): fill in `VOICE_OWNER` and `SIGNED_DATE`.
- `pipeline/assets/voice/raw/clip1.mp4`: 1 to 3 minutes of you talking, as clean as possible.
- `pipeline/assets/avatar.png`: the avatar image.
- `pipeline/assets/product.png`: the product photo.

```bash
python tests/test_offline.py   # success: "ALL OFFLINE TESTS PASSED"
python run.py preflight        # success: every line PASS (the Somali line may say WARN, see ○ below)
python run.py voice            # success: "cloned voice id ... saved to assets/voice/voice_id.txt"
```

### Per ad

```bash
python run.py make scripts/ad01.json --until tts        # cheapest test: listen to runs/ad01/vo.mp3
python run.py make scripts/ad01.json                    # full run; cached stages are not re-paid
```

Success looks like `QC PASSED ... -> runs/ad01/final.mp4` and exit code 0.

### What stays manual (on purpose)

- **Reading the Somali script aloud once and setting `reviewed_by_native_speaker: true`.** A machine can't judge Somali quality here.
- **Posting, with the AI-generated label turned on.** Uploading needs your account session. Automating that is a separate decision.

## 4. Verification status

- ● Offline end-to-end run: `python3 tests/test_offline.py` printed `ALL OFFLINE TESTS PASSED`, with 12/12 QC checks passing on a synthetic 22 s ad and QC correctly failing a 720x1280 file.
- ● Captions render and the avatar last-frame padding works: frames were extracted with ffmpeg at 2 s, 13 s and 21.5 s and viewed.
- ● `python3 run.py preflight` without keys fails cleanly with 4 FAILs that each name the fix. `make` refuses the unreviewed script.
- ○ No paid API has been called. The ElevenLabs Somali voice quality, the Fabric and Kling input key names, and their cost are all untested.
- ○ The language-id format in ElevenLabs `/v1/models` is unverified, so the preflight Somali check is advisory (WARN, not FAIL).
- ◑ Fabric outputs 720p at most (per its Replicate readme), so the face is upscaled to 1080x1920. Expect softness. Test before judging.
- ★ If Replicate renames a model's inputs, preflight fails with the accepted key list. Fix `inputs:` in `config.yaml` and nothing else.

## 5. Modal backend (brief 01 job 5, closed decision 2026-09-27)

Added 2026-09-28. `pipeline/config.yaml` sets `backend: modal` by default:

- `voice_prep_remote` and `assemble_remote` in `pipeline/modal_app.py` run the
  REAL `ugc` code. The client (`pipeline/ugc/modal_client.py`) copies `ugc/*.py`
  onto volume `jiheeye-build` before every call, so local and remote logic can
  never drift; the functions purge `ugc` from `sys.modules` first so a warm
  container never serves stale code.
- `run.py voice` / `make` call these by default. `backend: local` exists only
  for `tests/test_offline.py` synthetic media, and `run.py` additionally
  requires `JIHEEYE_ALLOW_LOCAL=1` captured at process launch (before `.env`
  loads, so .env cannot flip it).
- runs/ and work/ live on `/mnt/d/scratch/jiheeye-ultra/` (config `paths:`);
  `tools/disk_guard.sh` gates `run.py voice` and `run.py make` and refuses an
  unmounted or non-writable D: (doctrine 8).
- Paid stages (ElevenLabs TTS/clone, Replicate lipsync/B-roll) run as local API
  calls; their outputs cache by input hash. QC reads the downloaded final file
  locally. Modal job dirs are garbage-collected after each successful call.
- `preflight` checks that the app is deployed (free, no compute) when backend
  is modal.

