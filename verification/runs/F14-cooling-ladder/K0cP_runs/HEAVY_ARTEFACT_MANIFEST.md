# HEAVY ARTEFACT MANIFEST — `K0cP_runs`

**These paths are ON DISK and NOT AT HEAD.** They are filed here, by digest, so that a
later reader can prove the copy on disk is the copy the grade read — a gitignored path is
not a filed path, and this file is what makes the difference (`CLAUDE.md` WHERE THINGS
LIVE: *"Nothing is invisible merely because it is big"*).

Written 2026-08-27T16:28:06Z by a heat-transfer lane while landing the `K0cP_runs` evidence chain, under the
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
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_c/30000` | 5,223,633 | 16 | `c3e22d9793c2f90a97cf54309518bba5a24a3861e9418478df86788a615f9c29` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_c/constant/polyMesh` | 3,229,207 | 5 | `75111874d8644d44d9212061b54eacf5ec113871fb95f938c12dd09aded14e49` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_f/40000` | 13,274,823 | 16 | `f19e827d2de8fa2ba060d7f175a1395f335d4a0115213049952b13e7ecb51d57` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_f/constant/polyMesh` | 8,496,048 | 5 | `1144318b5d0b743e8e3f2355aecb35ca6e499c232b66cb3cba84d0a1cdbb048b` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_c/30000` | 5,245,556 | 16 | `b4989e8f5b2d945d1cf8b37078228b49fac78da05c21b7ee4340fbe9307ea7a5` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_c/constant/polyMesh` | 3,229,207 | 5 | `75111874d8644d44d9212061b54eacf5ec113871fb95f938c12dd09aded14e49` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_f/40000` | 13,330,191 | 16 | `558365ce2fa5ea9406a3c652aae8cdc65ac1564e9aa4312c7aace69539fb318e` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_f/constant/polyMesh` | 8,496,048 | 5 | `1144318b5d0b743e8e3f2355aecb35ca6e499c232b66cb3cba84d0a1cdbb048b` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |

**Total: 60,524,713 bytes across 84 files in 8 directories.**

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
`log.solve` remains at HEAD (`log.blockMesh`, `log.checkMesh`, `log.cellCentres`).

### Now untracked by this amendment — ON DISK, NOT AT HEAD

Removed from the index with `git update-index --force-remove` under the private-index
protocol. **The working tree was not touched**: no `git rm`, no `git reset`, no
`git clean`, no `git checkout --`. Every path below was confirmed present on disk with
its original byte count *after* the commit.

| Path | Bytes | Files | SHA-256 | Why not at HEAD |
| --- | ---: | ---: | --- | --- |
| `.../K0cP_runs/P021_sq_c/log.solve` | 29,474,075 | 1 | `2ac808f276a9aa689a562424ddf73ad10b621adacd067ff1f166bbdf91ff9541` | solver log — Sanaa §1 "logs ... stay out of git" |
| `.../K0cP_runs/P021_sq_f/log.solve` | 39,345,705 | 1 | `c9a25bdca2696a9548df63b5230aeedf45f2c1c01aca0a9a395d497934bf74b3` | solver log — Sanaa §1 "logs ... stay out of git" |
| `.../K0cP_runs/P102_sq_c/log.solve` | 29,463,777 | 1 | `f3a4314b14da6a841226e0d96b8ec3348d479eced80a9a1902b2660cfa21346c` | solver log — Sanaa §1 "logs ... stay out of git" |
| `.../K0cP_runs/P102_sq_f/log.solve` | 39,342,136 | 1 | `ad9dad9f3c82f06cfb3773f2af47fe07dcf1664457a6dd9ea8fdf1fb23763f4c` | solver log — Sanaa §1 "logs ... stay out of git" |

Single files are hashed directly (`sha256sum`). There is **no** attempt directory in this
run root: `.attempt1_stale/` exists only under `K0cG_runs/` and is filed in that root's
own AMENDMENT 1. This root's four rows are logs only.

**Untracked by this amendment, in this run root: 137,625,693 bytes across 4 files.**

### Now filed by digest that never was — `postProcessing/`

These were always on disk and never at HEAD, and the previous text wrongly said otherwise.
They are the directories the gate values are actually read from, so filing them by digest
is what makes this an evidence chain rather than an assertion. They are **not** force-added:
`.gitignore:67` is a repo-wide standing policy this lane did not write and may not retire.

| Directory | Bytes | Files | SHA-256 directory digest |
| --- | ---: | ---: | --- |
| `.../K0cP_runs/P021_sq_c/postProcessing` | 379,105 | 7 | `2da6a76f94cdfbba43c99cb07a6fdd41d71e793bd68dd378d00bd80597b027de` |
| `.../K0cP_runs/P021_sq_f/postProcessing` | 504,905 | 7 | `3b2868b169718e0c9cd67080ce48ee761df4a064854e067bef729863417a841c` |
| `.../K0cP_runs/P102_sq_c/postProcessing` | 379,106 | 7 | `d971e2d7e233ed36c57a6594c9efbfed8b24a95297406b087e33946d025a9b1b` |
| `.../K0cP_runs/P102_sq_f/postProcessing` | 504,906 | 7 | `2c94fabe49e49a519aace40f7aa194b1d838b0b5e94212619c9d4c352a305d4d` |

### What remains at HEAD in this run root — MEASURED, not inferred from a sibling

`git ls-tree -r -l HEAD` after this amendment, over both K0c run roots: **172 files,
345,091 bytes.** Per subtree in this root, measured individually:
`P021_sq_c` 37,958 B / 23 files · `P021_sq_f` 37,956 B / 23 files ·
`P102_sq_c` 37,958 B / 23 files · `P102_sq_f` 37,956 B / 23 files ·
`gate_k0cp.json` 23,096 B · `analyse_k0cp.py` 6,038 B · `build_cases.sh` 1,651 B ·
`launch_all.sh` 762 B · `PREREG_TIMESTAMP.txt` 374 B · `LAUNCH.log` 52 B ·
`ALL_DONE` 65 B · `DONE.*` 74-75 B each.

Every subtree here was measured on its own. Inferring one directory's size from a
sibling's is the error that let 56 MB land in `05241ab2`, and it is not repeated.

### What this does NOT do

- It does **not** re-grade anything. `K0cP_RESULTS.md` is at HEAD with its verdict landed
  and was **not touched**. No gate, threshold, cap or label moved.
- It does **not** reclaim `.git` space (see FORWARD-ONLY above).
- It does **not** add a `.gitignore` entry: the untracked paths stay visible to
  `git status` deliberately, so their absence from HEAD is a decision a reader can see
  rather than a rule that hides them.

*Nothing here was sent, filed, uploaded, posted or registered outside this box
(`CLAUDE.md` rule 7).*
