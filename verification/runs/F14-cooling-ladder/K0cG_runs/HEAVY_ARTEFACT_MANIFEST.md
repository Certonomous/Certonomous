# HEAVY ARTEFACT MANIFEST — `K0cG_runs`

**These paths are ON DISK and NOT AT HEAD.** They are filed here, by digest, so that a
later reader can prove the copy on disk is the copy the grade read — a gitignored path is
not a filed path, and this file is what makes the difference (`CLAUDE.md` WHERE THINGS
LIVE: *"Nothing is invisible merely because it is big"*).

Written 2026-08-27T16:28:04Z by a heat-transfer lane while landing the `K0cG_runs` evidence chain, under the
heat-transfer supervisor's ruling of 2026-08-27 amending item 5 of that lane's brief.
**No solver ran, no gate was graded and no verdict moved to write this file.**

## Why these are not at HEAD

Two different reasons, and they are not interchangeable:

- **`constant/polyMesh/`** — excluded **repo-wide, by standing policy**, at
  `.gitignore:66` (`**/constant/polyMesh/`). This lane did not choose that and did not
  change it. Regenerable from the case's tracked `build_cases.*` + `system/blockMeshDict`.
- **Numeric time directories** — excluded **by the supervisor's ruling** as reproducible
  bulk. The values a gate reads are not taken from these directories: they come from
  `postProcessing/` and `log.solve`, both of which ARE at HEAD.

## What IS at HEAD, so the chain is complete

Every `log.*`, `STATUS.*`, `DONE.*`, `ALL_DONE`, `*.out`, all of `system/`, all of
`postProcessing/`, the non-`polyMesh` `constant/` dictionaries, and `0/` + `0.orig/`.
The comparator (`analyse_*.py`), the gate (`gate_*.json`), `PREREG_TIMESTAMP.txt` and the
`RESULTS` record were already at HEAD before this landing.

## Digest method

For each directory: every file under it, recursively, is hashed with SHA-256; the lines
`<sha256>  <path relative to that directory>` are **sorted**; and the digest below is the
SHA-256 of those sorted lines joined by newline, with a trailing newline. Reproduce it
with the `digest()` function described in this paragraph — the ordering and the trailing
newline are both load-bearing.

## Manifest

| Directory | Bytes | Files | SHA-256 directory digest | Why not at HEAD |
| --- | ---: | ---: | --- | --- |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_KE_x/38000` | 22,995,096 | 12 | `dd8893ec0034733bbdc1e21debf3aad8259111560fe95d5607b676191c0b6759` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_KE_x/40000` | 33,854,182 | 16 | `92e7986388e2691582118e2d5ad7056f93c3c2f04320566757c0021e3f818a47` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_KE_x/constant/polyMesh` | 22,631,845 | 5 | `19e5f24a813e0915e4bba1c91e934a3cf82fe8dcc3017478e1046b4abcf6a704` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_SST_x/38000` | 22,712,997 | 12 | `e62373a3a9924345b93be2c4c417b00a20184406cd4f4c671015a290e9c95074` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_SST_x/40000` | 33,571,522 | 16 | `c92114f811a59de2b1443986f738a52de8c5f08a6ea17227d0c54c79db8ddf6c` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_SST_x/constant/polyMesh` | 22,631,845 | 5 | `19e5f24a813e0915e4bba1c91e934a3cf82fe8dcc3017478e1046b4abcf6a704` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |

**Total: 158,397,487 bytes across 66 files in 6 directories.**

*Nothing here was sent, filed, uploaded, posted or registered outside this box
(`CLAUDE.md` rule 7).*

---

## AMENDMENT 1 — 2026-08-27, remediation of `05241ab2` under Sanaa's standing directive §1

*Appended, not rewritten. **Lines whose number changed above this section: 0.***

Sanaa's standing directive of 2026-08-27T16:54Z (`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`),
§1 COMMIT HYGIENE, verbatim: *"explicit path lists, no directory sweeps; **logs and attempt
dirs stay out of git**; pre-commit guard blocks >50 files or >5 MB without a manifest."*

`05241ab2` predates that directive, so this is **remediation, not misconduct**. It was an
explicit path list, not a directory sweep — established by exclusion: the two trees hold
~210 MB of `constant/polyMesh` and numeric time directories and that commit landed **zero**
of either. The half of §1 it did breach is the log-and-attempt-dir half.

**FORWARD-ONLY. No history rewrite.** The blobs remain reachable in history; `.git`
`size-pack` is unchanged (~2.12 GiB). Only a history rewrite would reclaim that, a rewrite
is irreversible, and it is reserved to Sanaa. **It is not being requested here.**

### Struck

The following sentence of "Why these are not at HEAD" (lines 19-21 above) is **STRUCK**:

> *"The values a gate reads are not taken from these directories: they come from
> `postProcessing/` and `log.solve`, both of which ARE at HEAD."*

It was wrong on **both** halves, and the correction is measured, not inferred:

- `log.solve` **was** at HEAD when written; under this amendment it no longer is.
- `postProcessing/` was **never** at HEAD and could not have been: it is excluded
  repo-wide by `.gitignore:67` (`**/postProcessing/`), verified with
  `git check-ignore -v`. Zero `postProcessing` paths appear in `git ls-tree -r HEAD`
  for either run root. The original sentence asserted a tracking state nobody checked.

The sentence in "What IS at HEAD" (lines 25-26) reading *"all of `postProcessing/`"* is
**STRUCK** for the same reason, and `log.*` there is **narrowed**: every `log.*` except
`log.solve` remains at HEAD (`log.blockMesh`, `log.checkMesh`, `log.cellCentres`, and
`CRASHED_ATTEMPT_1/*/log.solve.tail`, which is a different file from `log.solve`).

### Now untracked by this amendment — ON DISK, NOT AT HEAD

Removed from the index with `git update-index --force-remove` under the private-index
protocol. **The working tree was not touched**: no `git rm`, no `git reset`, no
`git clean`, no `git checkout --`. Every path below was confirmed present on disk with
its original byte count *after* the commit.

| Path | Bytes | Files | SHA-256 | Why not at HEAD |
| --- | ---: | ---: | --- | --- |
| `.../K0cG_runs/S_KE_x/log.solve` | 39,426,235 | 1 | `588e2ba99081a19ccfbaf49faf66887670ef06d705dfc1763b988afdb02e4c61` | solver log — Sanaa §1 "logs ... stay out of git" |
| `.../K0cG_runs/S_SST_x/log.solve` | 40,897,193 | 1 | `68b18348127f139d560fc9760d6d65bb06052acfd194332a84d284d846b3054d` | solver log — Sanaa §1 "logs ... stay out of git" |
| `.../K0cG_runs/.attempt1_stale/` | 59,477,123 | 34 | `08bba8acd28cde2caf00d961e795078c817c07c3160dbc3745fa40a052650107` | attempt directory — Sanaa §1 "... and attempt dirs stay out of git" |

Single files are hashed directly (`sha256sum`); the directory row uses the digest method
of the "Digest method" section above, unchanged.

`.attempt1_stale/` holds **34** files on disk totalling 59,477,123 bytes; **20** of them
(58,742,182 bytes) were the ones at HEAD, the other 14 (734,941 bytes) never were. The
digest above covers the full on-disk directory, which is what a later reader can check.

**Untracked by this amendment, in this run root: 22 index entries removed** (2
`log.solve` + the 20 `.attempt1_stale/` paths that were at HEAD), carrying **139,800,551
bytes on disk** across the three rows above. Across BOTH K0c run roots the totals are
**26 index entries, 276,691,303 bytes at HEAD / 277,426,244 bytes on disk** (the 734,941 B
difference is the 14 `.attempt1_stale` files that were on disk but never at HEAD).

### Now filed by digest that never was — `postProcessing/`

These were always on disk and never at HEAD, and the previous text wrongly said otherwise.
They are the directories the gate values are actually read from, so filing them by digest
is what makes this an evidence chain rather than an assertion. They are **not** force-added:
`.gitignore:67` is a repo-wide standing policy this lane did not write and may not retire.

| Directory | Bytes | Files | SHA-256 directory digest |
| --- | ---: | ---: | --- |
| `.../K0cG_runs/S_KE_x/postProcessing` | 504,907 | 7 | `10883bee0c6583d8862d678dfd6f19508465bd429d3bdeae2ae1252dafcb04e6` |
| `.../K0cG_runs/S_SST_x/postProcessing` | 504,907 | 7 | `242e09bfb96e4bf559b3beb6a49d5b71ae2d9adb09783a6edd2cb74b8f14eabf` |
| `.../K0cG_runs/CRASHED_ATTEMPT_1/S_KE_x/postProcessing` | 303,627 | 7 | `01ba3c89f8986be5dd0d6c5bb86791feb3f7e32fd05fdd0387cba6898423ab80` |
| `.../K0cG_runs/CRASHED_ATTEMPT_1/S_SST_x/postProcessing` | 431,314 | 7 | `f5bc2d6357299d7b8ae53c8f5d325c22ede8e06061bb9d463edc81f4852d578a` |

### What remains at HEAD in this run root — MEASURED, not inferred from a sibling

`git ls-tree -r -l HEAD` after this amendment, over both K0c run roots: **172 files,
345,091 bytes.** Per subtree in this root, measured individually:
`S_KE_x` 44,840 B / 25 files · `S_SST_x` 44,882 B / 25 files ·
`CRASHED_ATTEMPT_1` 17,925 B / 7 files · `build_cases.py` 27,874 B ·
`gate_k0cg.json` 9,427 B · `analyse_k0cg.py` 6,404 B · `PREREG_TIMESTAMP.txt` 310 B ·
`launch_all.sh` 1,036 B · `LAUNCH.log` 88 B · `ALL_DONE` 65 B · `DONE.*` 85 B each ·
`relaunch.out` 0 B.

`CRASHED_ATTEMPT_1` is **17,925 bytes across 7 files at HEAD** — not the 752,866 bytes
across 21 files it occupies on disk; the difference is its gitignored `postProcessing/`,
now filed by digest two tables above. Every subtree here was measured on its own. Inferring
one directory's size from a sibling's is the error that let 56 MB land in `05241ab2`, and
it is not repeated.

### What this does NOT do

- It does **not** re-grade anything. `K0cG_RESULTS.md` is at HEAD with its verdict landed
  and was **not touched**. No gate, threshold, cap or label moved.
- It does **not** reclaim `.git` space (see FORWARD-ONLY above).
- It does **not** add a `.gitignore` entry: the untracked paths stay visible to
  `git status` deliberately, so their absence from HEAD is a decision a reader can see
  rather than a rule that hides them.

*Nothing here was sent, filed, uploaded, posted or registered outside this box
(`CLAUDE.md` rule 7).*

---

## AMENDMENT 2 — 2026-08-27, the remaining `log.*` paths, under the live pre-commit guard

*Appended, not rewritten. **Lines whose number changed above this section: 0.***

AMENDMENT 1 untracked the six `log.solve` and `.attempt1_stale/`. It left every
OTHER `log.*` at HEAD, because that lane's brief listed those as KEEP. That
keep-list is **superseded** by `scripts/check_commit_size.py` (`aac938dd`), which
implements Sanaa's §1 and whose LOGS rule is **categorical and not exemptible**:

> *"LOGS: ... logs stay out of git ... a manifest explains bulk, it does not make a
> solver log a repository artifact. File the log by digest outside git."*

The guard matches `log.*`, `*/log.*` and `*.log` (`check_commit_size.py:87`), so
`LAUNCH.log`, `log.blockMesh`, `log.cellCentres`, `log.checkMesh` and
`log.solve.tail` all qualify. **A manifest never exempts a log** — `05241ab2`
carried two valid manifests and still refuses under LOGS. So they are untracked
here and filed by digest, which is what the guard asks for.

**Untracked by this amendment (working tree NOT touched;
`git update-index --force-remove` only), all confirmed on disk afterwards:**

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `K0cG_runs/CRASHED_ATTEMPT_1/LAUNCH.log` | 36 | `d622e0e73136d9d41f8e10f87f7022a8d1a9dab445021b450fc99fce0631fca5` |
| `K0cG_runs/CRASHED_ATTEMPT_1/S_KE_x/log.checkMesh` | 4109 | `a47b1984e9696cf11faccf623f12491de3a904c2b517d6351ab2feeb8d6c96a5` |
| `K0cG_runs/CRASHED_ATTEMPT_1/S_KE_x/log.solve.tail` | 4272 | `8411601610e9bb7f30b493ae034c8c0f726d30f24dbd235dbf03c3f06c7d5051` |
| `K0cG_runs/CRASHED_ATTEMPT_1/S_SST_x/log.checkMesh` | 4110 | `e9de75faba0707491de5d18a49d70aceffa52adc842f2ab50034c21f06a2ce89` |
| `K0cG_runs/CRASHED_ATTEMPT_1/S_SST_x/log.solve.tail` | 5240 | `d372c5cda2530dae9ece27439a5ce6cdb520466981a8da3a32077dac20337588` |
| `K0cG_runs/LAUNCH.log` | 88 | `3089cb4f51f9dddf4aadf06befdabd66912d7b258598ad4bc660129411d83c5f` |
| `K0cG_runs/S_KE_x/log.blockMesh` | 2820 | `81ba0c422f50a5b64a78b477dce7413536106ead2129837a60cda41e6302cc37` |
| `K0cG_runs/S_KE_x/log.cellCentres` | 1847 | `8cc70d75d65e50e1cc7f62c563c639281cfc019c55866e5d088f2fcad04f01db` |
| `K0cG_runs/S_KE_x/log.checkMesh` | 4109 | `7b15bc4e0869995d0d873fbc6bee12d34550f573f2c4a3ea058697fcfee4ed15` |
| `K0cG_runs/S_SST_x/log.blockMesh` | 2821 | `88a46b1074f6066c07e0e36f355f8620ba4cf04a944d07bc614c79d76325009e` |
| `K0cG_runs/S_SST_x/log.cellCentres` | 1848 | `68c5a339f05e35a21c028f2ee3786cf607affe5621eeaf4851904356e2e559aa` |
| `K0cG_runs/S_SST_x/log.checkMesh` | 4110 | `b49b69a711653442483b2f6e1a31da14b3bee04985bf74204587ec454bf11f77` |

**12 paths, 35410 bytes, all ON DISK and NOT AT HEAD.**

### One consequence, flagged for the supervisor rather than absorbed

`log.checkMesh` is the **mesh birth certificate** (`VERIFICATION_CHARTER` §9;
`MESH_STANDARD.md`). It is now filed by digest rather than held at HEAD. The
digest above is what a later reader checks it against, and the file is unchanged
on disk — but a reader who expected to `git show` it will not find it there.
That is a consequence of the categorical LOGS rule, not a lane's judgement call,
and it is stated here rather than discovered later. Whether the birth
certificate should be exempted is the supervisor's and Sanaa's call, not this
lane's; nothing here retires, widens or amends a standard.

*Nothing here was sent, filed, uploaded, posted or registered outside this box
(`CLAUDE.md` rule 7).*
