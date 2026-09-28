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
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra/pipeline; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=a4812af73b323c06e283d2b2ebf709a8862f9402e0a878ea92c8e714b5dd3312; output-bytes=4767

- [x] G8: Modal render test passes with all 12 QC checks green on a file rendered on Modal
  CHECK: .venv/bin/python tests/test_modal.py
  CWD: pipeline
  EXPECT: ALL MODAL TESTS PASSED (QC checks 12/12)
  EVIDENCE: exit=0; shell=/bin/bash; cwd=/home/muads/jiheeye-ultra/pipeline; path=5fb5264d6ab0/20 entries; EXPECT=matched; output-sha256=f87dd59597024cfaac22214236c165d56c29c2cd56ff1d3c9129b0a17346433c; output-bytes=1140

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