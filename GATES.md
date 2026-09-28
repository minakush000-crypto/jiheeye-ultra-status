# Gates: brief 01 (jiheeye-ultra to SYSTEM.md standard, Modal compute, status mirror)

OWNS: **

Scope: execute every job in briefs/brief01.md (J1-J9) so that each "done means" in the brief is proven by a command, not a summary.

- [x] G0: this ledger states outcomes that can fail
  CHECK: node /home/muads/.claude/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=48630b7361dd44ee870917b12c3d19b9d7bdea738aaca16bb04d4cab83b772d2; output-bytes=8

- [x] G1: briefs/brief01.md is a byte-exact copy of the coordinator brief
  CHECK: diff -q /mnt/c/Users/muads/Claude/briefs/jiheeye-brief01.md briefs/brief01.md && echo BRIEF-VERBATIM-OK
  EXPECT: BRIEF-VERBATIM-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=e22f85bc58b7e632713eeded83288767637bbdd12bfbfc2abf49417795fbd5da; output-bytes=18

- [x] G2: scaffolding files exist and DECISIONS.md seeds the five closed decisions
  CHECK: bash -c 'test -s CLAUDE.md && test -s DECISIONS.md && test -s STATUS.md && test -s PROGRESS.md && test -d briefs && test -d reports && grep -q "Demucs voice cleanup" DECISIONS.md && grep -q "jiheeye-ultra-status" DECISIONS.md && echo SCAFFOLD-OK'
  EXPECT: SCAFFOLD-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=3545fe373d22a727eddfff776643da807b43f9d3431c5993054e9972e3b96204; output-bytes=12

- [x] G3: project skill installed at .claude/skills with the repo path set
  CHECK: bash -c 'test -s .claude/skills/jiheeye-ugc-pipeline/SKILL.md && grep -q "jiheeye-ultra" .claude/skills/jiheeye-ugc-pipeline/SKILL.md && echo SKILL-OK'
  EXPECT: SKILL-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=d820f7ee173e38f9762669b3ea34ce3a1b689b4ff6fd0560d601cc02d8827423; output-bytes=9

- [x] G4: pipeline/.venv has every runtime dependency including modal
  CHECK: pipeline/.venv/bin/python -c "import yaml, requests, numpy, soundfile, noisereduce, replicate, modal; print('VENV-OK')"
  EXPECT: VENV-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=8df0145c04928e1ac952b9c0ce8511dd979a81fa865b566ff0e4b58a1bec4c5a; output-bytes=8

- [x] G5: config points at the D: scratch tree, backend is modal, disk guard is wired into run.py
  CHECK: pipeline/.venv/bin/python tools/check_wiring.py
  EXPECT: WIRING-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=8736ec8a3562172ff0d8a6e55edd24a92408d46d2ebe2c5cdc28ee94f9d8f61a; output-bytes=10

- [x] G6: the jiheeye-ultra Modal app is deployed
  CHECK: pipeline/.venv/bin/modal app list --json 2>/dev/null | grep -A1 '"description": "jiheeye-ultra"' | grep -q '"state": "deployed"' && echo MODAL-DEPLOYED-OK
  EXPECT: MODAL-DEPLOYED-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=2e1a28d1adc2dba711644966d0ffc9944831b57675f4ee8f6019bb5b7b59a8fb; output-bytes=18

- [x] G7: offline end-to-end test passes with the real local backend
  CHECK: .venv/bin/python tests/test_offline.py
  CWD: pipeline
  EXPECT: ALL OFFLINE TESTS PASSED
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra/pipeline; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=ec51ad6b6f6dc46953e3933a6206aa935c4b53f875a4cb84ee9489791ad5fec3; output-bytes=4767

- [x] G8: Modal render test passes with all 12 QC checks green on a file rendered on Modal
  CHECK: .venv/bin/python tests/test_modal.py
  CWD: pipeline
  EXPECT: ALL MODAL TESTS PASSED (QC checks 12/12)
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra/pipeline; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=fccec9e728851910ff3ff2de2d0df935101405e4e0d215c9f2b92bcf2888136c; output-bytes=1140

- [x] G9: private GitHub repo has main pushed
  CHECK: bash -c 'git ls-remote https://github.com/minakush000-crypto/jiheeye-ultra.git refs/heads/main | grep -q main && echo PRIVATE-REPO-OK'
  EXPECT: PRIVATE-REPO-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=a1b03b952d3bdcccbe50d6d8485cceef64fe8b481e8c003bb995af6d41390caa; output-bytes=16

- [x] G10: public mirror contains only allowlisted files and none of the hard-denied kinds
  CHECK: bash tools/verify_mirror.sh
  EXPECT: MIRROR-CLEAN-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=6cddf6303f265c0818613bfbb392bf62c4539bc57205c6c8d99cfb7ba6a1128f; output-bytes=27

- [x] G11: the old C: copy is deleted
  CHECK: bash -c 'test ! -d /mnt/c/Users/muads/Claude/jiheeye-ultra && echo OLDCOPY-GONE-OK'
  EXPECT: OLDCOPY-GONE-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=67bc10f574ad82773193f221191b3a41fc75b2e0a03aad41cfebc085ef2af5b1; output-bytes=16

- [x] G12: reports/brief01.md covers every job J1-J9 with commands and outputs
  CHECK: bash -c 'for j in J1 J2 J3 J4 J5 J6 J7 J8 J9; do grep -q "^## $j" reports/brief01.md || exit 1; done && echo REPORT-OK'
  EXPECT: REPORT-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=b5d799b8ae3e8271ceb1d56f5cb1568d96693dfbb46d5b606ffa2133a3bc5c18; output-bytes=10

# Gates: brief 02 (voice clone, first Somali audio, vertical avatar, $10 cap)

Scope: execute every job in briefs/brief02.md (J1-J9) so each "done means" is
proven by raw pasted command output in reports/brief02.md, and cumulative paid
spend (ElevenLabs + Replicate + Modal) stays <= $10.

- [x] G13: briefs/brief02.md is a byte-exact copy of the coordinator brief
  CHECK: diff -q /mnt/c/Users/muads/Claude/briefs/jiheeye-brief02.md briefs/brief02.md && echo BRIEF02-VERBATIM-OK
  EXPECT: BRIEF02-VERBATIM-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=be5e093e6089ff7d0d4f3a871f99bddd22b854ce5811545fd07da79962254ae9; output-bytes=20

- [x] G14: voice clip staged at pipeline/assets/voice/raw/clip1.mp3; its real sha256 recorded; the deviation from the brief's stated prefix 35cb41ae21cf94e4 investigated with decoded-PCM evidence and documented in DECISIONS.md; the inbox delete skipped because the verify precondition failed
  CHECK: bash -c 'test -s pipeline/assets/voice/raw/clip1.mp3 && grep -q "44575846ec3e2069" DECISIONS.md && grep -q "35cb41ae21cf94e4" DECISIONS.md && test -f /mnt/c/Users/muads/Claude/jiheeye-inbox/clip1.mp3 && echo CLIP-STAGED-DEVIATION-DOCUMENTED'
  EXPECT: CLIP-STAGED-DEVIATION-DOCUMENTED
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=c3314d548a3156b2d74981a1919c77a3f8cac80d687f16723832e286ed23a343; output-bytes=33

- [x] G15: CONSENT.md voice gate passes (J3, output pasted in report)
  CHECK: pipeline/.venv/bin/python -c "import sys; sys.path.insert(0, 'pipeline'); from pathlib import Path; from ugc.voice_clone import check_consent; print('CONSENT-OK', check_consent(Path('.')))"
  EXPECT: CONSENT-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=54d68f1353775987e31fa5c17c784640b9698df076a5a3ce9b443661fd4603f5; output-bytes=25

- [x] G16: both API keys present in pipeline/.env; machine-wide ElevenLabs key search done (paths/names only, no values)
  CHECK: bash -c 'grep -qE "^ELEVENLABS_API_KEY=.+" pipeline/.env && grep -qE "^REPLICATE_API_TOKEN=.+" pipeline/.env && grep -q "^## J4 Keys" reports/brief02.md && echo KEYS-OK'
  EXPECT: KEYS-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=1d9ad8cf5f7d02e54f4040a103991a3bf2a9999505528337cc783177954a6da7; output-bytes=8

- [x] G17: preflight exits 0 (schema lookups, consent, Modal reachability, ElevenLabs model+Somali listing; no paid calls)
  CHECK: bash -c 'cd pipeline && .venv/bin/python run.py preflight && echo PREFLIGHT-OK'
  EXPECT: PREFLIGHT-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=54c39f77454f1515657088fdd60847069556b20c78d97c8a4cf71906f70d7a81; output-bytes=1422

- [ ] G18: voice stage done: clean sample + cloned voice id exist on disk, Modal runtime and IVC result recorded in the report
  CHECK: bash -c 'test -s pipeline/assets/voice/voice_sample.wav && test -s pipeline/assets/voice/voice_id.txt && grep -q "Modal runtime" reports/brief02.md && grep -q "voice_id" reports/brief02.md && echo VOICE-STAGE-OK'
  EXPECT: VOICE-STAGE-OK

- [x] G19: pipeline/scripts/ad00_test.json is ad01 minus the product scene with reviewed_by_native_speaker still false
  CHECK: bash -c 'cd pipeline && .venv/bin/python -c "import json; s=json.load(open(\"scripts/ad00_test.json\")); ids=[x[\"id\"] for x in s[\"scenes\"]]; assert \"product\" not in ids, ids; assert s[\"reviewed_by_native_speaker\"] is False; assert len(ids)==3, ids; print(\"AD00-OK\")"'
  EXPECT: AD00-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=1af73591f76a0bebcfe942c1c1f1c32685b9181d72a5b3c55949d21d4449270c; output-bytes=8

- [x] G20: --allow-unreviewed implemented (valid only with --until tts) and the offline regression suite still passes
  CHECK: bash -c 'grep -q "allow-unreviewed" pipeline/run.py && cd pipeline && JIHEEYE_ALLOW_LOCAL=1 .venv/bin/python tests/test_offline.py | tail -1'
  EXPECT: ALL OFFLINE TESTS PASSED
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=90c2a968a832dbcf389b9cb1c12ae2404ec6239eb351685c4f1ef75f1d279ed1; output-bytes=25

- [ ] G21: make --until tts --allow-unreviewed ran; UNREVIEWED line printed; ad00_vo.mp3 + ad00_script.txt on C: for Mayo
  CHECK: bash -c 'test -s /mnt/c/Users/muads/Claude/jiheeye-review/ad00_vo.mp3 && test -s /mnt/c/Users/muads/Claude/jiheeye-review/ad00_script.txt && grep -q "UNREVIEWED: audio for Mayo" reports/brief02.md && echo REVIEW-FILES-OK'
  EXPECT: REVIEW-FILES-OK

- [x] G22: avatar extended to 1080x1920 (9:16) and preview written to C:; method (model+schema, or blurred fallback) documented
  CHECK: bash -c 'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 pipeline/assets/avatar.png | grep -q "^1080,1920" && test -s /mnt/c/Users/muads/Claude/jiheeye-review/avatar_preview.png && grep -q "schema" reports/brief02.md && echo AVATAR-OK'
  EXPECT: AVATAR-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=3b09ad7866579f74e0b249d054df55c4888da0cf03b7ddace89d5d68f79bb1d8; output-bytes=10

- [x] G23: spend ledger complete and cumulative <= $10
  CHECK: bash -c 'test -s reports/brief02_spend.csv && awk -F, "NR>1{c=\$6} END{if(c<=10){print \"SPEND-OK\", c; exit 0} else {exit 1}}" reports/brief02_spend.csv'
  EXPECT: SPEND-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=cb5a9f4b8e62d74b77c83392b0c3e6b8390c69d3cbc4192b3ece4f61b4f3cf91; output-bytes=14

- [x] G24: reports/brief02.md holds RAW pasted outputs for J2-J8 (sha256sum, consent gate, key search, preflight, voice run, make run, model schema) and the spend CSV
  CHECK: bash -c 'for j in J2 J3 J4 J5 J6 J7 J8; do grep -q "^## $j" reports/brief02.md || exit 1; done && grep -q "brief02_spend.csv" reports/brief02.md && echo REPORT-OK'
  EXPECT: REPORT-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=b5d799b8ae3e8271ceb1d56f5cb1568d96693dfbb46d5b606ffa2133a3bc5c18; output-bytes=10

- [x] G25: private repo pushed and public mirror republished clean
  CHECK: bash -c 'git ls-remote https://github.com/minakush000-crypto/jiheeye-ultra.git refs/heads/main | grep -q main && bash tools/verify_mirror.sh'
  EXPECT: MIRROR-CLEAN-OK
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=57be2f5dc30bbdf8e2b9a4c4cdf4031eecf990f02ff09fc1c9fda9a724dce17f; output-bytes=27

- [ ] G26: gate-check --reverify ran AFTER the last code commit and its output is pasted in reports/brief02.md under the REVERIFY marker (the reverify command itself runs from the shell, not from inside a gate)
  CHECK: grep -q "REVERIFY-OUTPUT-BELOW" reports/brief02.md && echo REVERIFY-IN-REPORT
  EXPECT: REVERIFY-IN-REPORT