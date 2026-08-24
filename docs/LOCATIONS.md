# LOCATIONS: where every part of this lab's work lives

For a reader who needs to find something and has only this repository to start
from. Most of the lab's output is too large to commit, so this file enumerates
every part of it by exact location. Nothing is invisible merely because it is
big.

Every count and size on this page is a reading taken at commit frame
`8cefb4e9`, and each carries the command that reproduces it. **These are not
constants.** The tracked and gitignored arms move several times an hour while
the lab is working, and the run tree grows with every solve. Re-derive rather
than quote.

**Say which quantity a size figure is.** Sizes here are decimal GB summed from
apparent file sizes unless a row says otherwise, and apparent size is not disk
usage and not a deduplicated byte count. Section 6 states the three that differ
here and by how much.

**If you are sitting on the machine rather than reading the repository, start at
`/home/ubuntu/README.md`.** That page is the orientation document: what this box
is, what each top-level folder means, which things cannot be moved and why, and
the traps that will cost you an afternoon. It deliberately does not repeat the
figures below — this page remains the index, and a second copy of an index is a
second thing to go stale. Every themed directory under `/home/ubuntu` also has
its own README; §4.3a lists them.

---

## 1. The whole picture

| Body | Files | Apparent | Deduplicated | Where |
|---|---|---|---|---|
| Tracked in this repository | 20,764 | 1.82 GiB packed | | on GitHub |
| Gitignored inside the working tree | 37,243 | 11.90 GB | 11.90 GB | this machine only |
| The solve run tree | 132,049 regular files | 75.79 GB | 69.36 GB | this machine only |
| Other directories outside the repository | 17,558 | 2.06 GB | 2.06 GB | this machine only |
| Loose files directly in `/home/ubuntu` | 39 | 0.91 GB | 0.91 GB | this machine only |
| **Cannot live in a git repository** | | **90.66 GB** | **84.24 GB** | |
| Dotted directories in `/home/ubuntu` (§4.6, frame 2026-08-17) | 37,837 | 12.04 GB | | this machine only |
| The scorer mirror, `/home/ubuntu/mirrors/` (§4.2b, frame 2026-08-17) | 22 | 0.0012 GB | 0.0012 GB | this machine only |
| **Including them** | | **102.70 GB** | | |

The deduplicated column is measured on all four off-repository bodies, not
assumed. Only the run tree contains hardlinks; on the other three the two
columns are equal because there are none to remove. File counts are the
enumeration commands' own counts; sizes are summed over the regular files among
them.

**The last three rows are a later frame and are set apart on purpose.** Until
2026-08-17 this page enumerated the run tree, the named directories and the
loose files, and stopped there. A reader reconstructing this machine from it was
short by the whole of §4.6 — 12.04 GB, including the agent dispatch records that
§4.5 calls the only sound R-ISOLATE evidence and which had no size or location on
this page at all. It was also short of §4.2b, the scorer mirror, which did not
exist until 2026-08-17 and which is small enough to overlook and load-bearing
enough that seven published records depend on what it holds. Those rows carry
their own frame stamp because the five rows above them are readings at
`8cefb4e9` and mixing frames in one total is the defect this page exists to
prevent. The mirror's 0.0012 GB does not move either printed total. The 12.04 GB in the Apparent column is
apparent bytes, 12,038,545,742 B, to match the column it sits in; `du -sb` over
the same population reads 12,038,546,180 B and §4.6 gives both with the commands.

Both totals are computed from unrounded bytes, so adding the deduplicated column
as printed gives 84.23 rather than 84.24. That 0.01 GB is per-row rounding and
nothing else. The apparent column happens to sum exactly.

GitHub rejects any file over 100 MB, warns above 50 MB, and treats repositories
over roughly 5 GB as out of policy. Everything that can be committed has been.
Everything that cannot is enumerated below.

---

## 2. In this repository, and on GitHub

Remote `git@github.com:Certonomous/Certonomous.git`, branch `main`.

| Quantity | Value | How to re-derive |
|---|---|---|
| Tracked files | 20,764 | `git ls-files \| wc -l` |
| Packed size | 1.82 GiB | `git count-objects -vH` |
| Tracked blobs over 50 MB | 1 | `git ls-tree -r -l HEAD` |
| Tracked blobs over 100 MB | 0 | same |
| Largest tracked file | 68.05 MB | same |

The largest tracked file is
`demo-output/website/campaign/F8_runs/phase6_mrf/constant/triSurface/blade.stl`.
It sits above GitHub's 50 MB warning threshold and below its 100 MB hard reject,
and it is the only tracked blob in either band.

---

## 3. Inside the repository but deliberately not committed

`.gitignore` excludes 37,243 files totalling 11.90 GB. They sit in the working
tree on this machine and are reachable by path, but no clone contains them.

```bash
git ls-files --others --ignored --exclude-standard
```

| Location | Files | Size |
|---|---|---|
| `demo-output/website/dafoam/` | 20,105 | 5.76 GB |
| `demo-output/website/campaign/` | 5,272 | 3.50 GB |
| `demo-output/website/solve_registry/` | 300 | 1.51 GB |
| `mission-output/` | 8,625 | 0.57 GB |
| `demo-output/website/mega-batch/` | 1,235 | 0.50 GB |
| `sdk/` | 1,578 | 0.04 GB |
| everything else | 128 | 0.02 GB |
| **Total** | **37,243** | **11.90 GB** |

These are case archives and solver output, not source. A repository-wide
`grep -r` cannot see them at all: the shell `grep` here is `ugrep
--ignore-files`, which honours `.gitignore` silently. Any sweep claiming to
cover the corpus must say which of the four arms it read (section 5).

---

## 4. Outside the repository, on this machine

### 4.1 The run tree, the largest single body of work

```
/home/ubuntu/certonomous-runs/
```

Every solver run the lab has executed. It is outside the repository entirely and
invisible to every git-based route.

| Quantity | Value | How to re-derive |
|---|---|---|
| Top-level study directories | 446 | `/usr/bin/find … -maxdepth 1 -mindepth 1 -type d` |
| Apparent size | 75.79 GB (70.59 GiB) | summed `st_size` over regular files |
| Deduplicated size | 69.36 GB | same, keyed on `(st_dev, st_ino)` |
| Extra hardlink instances | 135 | same |
| Disk usage | 69.85 GB | `du -s --block-size=1` |

**The file count depends on what you count.** All three of these are correct,
and a total is meaningless without saying which population it is over.

| Population | Count |
|---|---|
| Regular files only (`-type f`) | 132,049 |
| Regular files plus 748 symlinks | 132,797 |
| The same, excluding 36 loose files at the tree root | 132,761 |

The 36 loose files at the tree root sit in no study directory and are easy to
miss. `ls /home/ubuntu/certonomous-runs/` reaches them.

The eleven largest studies, by apparent size:

| Size | Files | Study |
|---|---|---|
| 12.57 GB | 6,342 | `dpw5-committee-probe` |
| 7.64 GB | 2,446 | `w3-naca4412-layered-replicates` |
| 2.24 GB | 462 | `f5a-cylinder-ladder` |
| 2.14 GB | 1,898 | `w3-naca0012_wing-family` |
| 1.53 GB | 210 | `credential-repair-naca4412-finer` |
| 1.51 GB | 1,264 | `w3-naca4412_wing-family` |
| 1.48 GB | 257 | `hlpw6-memory-probe` |
| 1.46 GB | 196 | `credential-repair-naca4412-finer_relayered_ngrow0` |
| 1.10 GB | 37,064 | `W5-regrade` |
| 1.02 GB | 172 | `A3-diag-rung3` |
| 1.01 GB | 3,048 | `F6a_diffusion` |

Next after those: `credential-repair-naca4412-finer_relayered`, 0.88 GB over
206 files.

**A measurement trap specific to this tree.** GNU `find`'s `-size -2M` and
`-size +2M` are not complementary, and a size-banded sweep that assumes they are
loses files silently.

| Band | Files |
|---|---|
| `-size -2M` | 121,523 |
| `-size +2M` | 6,108 |
| In neither strict band | 4,418 |
| **Total, regular files** | **132,049** |

`-size ±2M` rounds up to whole MiB, so anything above 1 MiB and up to 2 MiB
rounds to exactly 2 and falls in neither strict band. Any size-banded sweep must
reconcile its bands against an independently obtained total, and must say which
file population that total is over. `find` on this box is `bfs`, which rejects
GNU expressions such as `-printf`; use `/usr/bin/find`.

### 4.2 The scoring benchmark clone

```
/home/ubuntu/closure-challenge-benchmark/
```

| Quantity | Value |
|---|---|
| Files | 6,263 |
| Size | 1.30 GB |
| Pinned at | `deb91557184af3cb95f5190494ec52d8f2c6a0d1` |
| Upstream | `https://github.com/rmcconke/closure-challenge-benchmark.git` |

This one is reachable by anyone. It is not private lab state.

**One file in it is, and it is now also in git.** `scripts/rans_identity_baseline.py`
(2,827 B, MD5 `e5faef412884f3552222752e5a277c74`) is lab-authored, was the only
untracked file in the clone, and existed in **no other copy anywhere on this
machine**. It is the sole generator of the published **0.1036 RANS-identity
floor** — the figure in `demo-output/website/closure_challenge_rans_floor.json`,
carried into `benchmarks.json`, and argued in
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §7.2. A `git clean` or a re-clone of the
benchmark would have destroyed it, and
`campaign/AUDIT_AGED_FAIL_SWEEP_2026-08-14.md` already recorded it as a FAIL:
*"cited evidence paths … Files not in git history."*

On **2026-08-17** a byte-identical copy was committed to
**`sdk/scripts/rans_identity_baseline.py`**, alongside the eighteen sibling
`closure_*` scripts. **The original was deliberately left in the clone**, because
two dated documents state as a finding that it lives there and is untracked
(`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §7.2 and
`campaign/LADDER_V_PASS3_COLD_2026-08-11.md`, the latter with a path correction
recorded at `13b965dd`), and removing it would have made both false. Nothing was
deleted; what changed is that the file now survives loss of the clone.

It expects the benchmark clone as its working directory — its data paths are
relative, e.g. `data/DUCT/AR_1_Ret_360/constant/C` — so run it as:

```sh
cd /home/ubuntu/closure-challenge-benchmark && \
  /home/ubuntu/closure-venv/bin/python /home/ubuntu/Certonomous/sdk/scripts/rans_identity_baseline.py
```

**It scores but does not rank.** It is not an admissible board identifier, and
its four-entrant README is not the live board. The live board carries six
entrants plus this lab's entry, retrieved 2026-08-11T23:33Z and re-verified
unchanged 2026-08-14T21:01Z.

### 4.2b The scorer mirror — the eval package's full history

```
/home/ubuntu/mirrors/closure-challenge.git
```

| Quantity | Value | How to re-derive |
|---|---|---|
| Files | 22 | `find /home/ubuntu/mirrors/closure-challenge.git -type f \| wc -l` |
| Size | 1,225,553 B = 1.3 MB (`du -sh` 1.3M, pack 1.14 MiB) | `du -sb /home/ubuntu/mirrors/closure-challenge.git` |
| Commits | 8, the complete history | `git -C … rev-list --all --count` |
| Refs | `main` + tags `v0.2.0`, `v0.2.1`, `v0.3.0`, `v0.3.1` | `git -C … show-ref` |
| Integrity | `git fsck --full` clean, exit 0 | `git -C … fsck --full` |
| Upstream | `https://github.com/rmcconke/closure-challenge.git` | |
| Created | 2026-08-17, frame stamp for §1 and §4.3 | |

Created with:

```sh
git clone --mirror https://github.com/rmcconke/closure-challenge.git \
  /home/ubuntu/mirrors/closure-challenge.git
```

**Why this exists: the working clone is shallow.**
`/home/ubuntu/closure-challenge-pkg` — the clone every scoring script actually
imports, via the editable install in `closure-venv` — is a **depth-1 shallow
clone**. Its `.git/shallow` contains exactly one line,
`1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162`. It holds that single commit and
**cannot show what changed to produce it**. Seven published JSON records pin
`1c4e22c8` as the scorer that produced their figures. Until 2026-08-17 the only
copy of the history behind that pin was GitHub's. **If that repository were
moved, renamed or deleted, every one of those records would keep its hash and
lose its referent**, and the one check that distinguishes the pinned metric from
its predecessor would have become unrebuildable. This is a five-commit, 1.3 MB
exposure on a body of published work; the mirror closes it.

That check is not hypothetical. `evaluate_individual_case` genuinely changed
between tag `v0.2.1` (`4796ce35`, componentwise `np.abs`) and the pin
(vector-magnitude `np.linalg.norm`), which is what lets a record's own figures
say which revision scored it — see `AWS_TREE_PLAN.md` §7.5 and
`demo-output/website/dafoam/ladder-b/duct_baseline/recheck_scorer_revision.py`.
The investigation that established it had to fetch `v0.2.1` from GitHub because
nothing on this machine had it.

**Restored from, not merely written.** A backup nobody has restored from is a
hope. On 2026-08-17 the mirror was restored from inside an empty network
namespace, with a live negative control confirming the network was actually
gone before the restore was attempted:

```sh
sudo unshare -n sudo -u ubuntu bash -c '
  git ls-remote https://github.com/rmcconke/closure-challenge.git   # negative control
  git clone --no-local /home/ubuntu/mirrors/closure-challenge.git rebuilt
  cd rebuilt && git checkout tags/v0.2.1 && git rev-parse HEAD
  grep __version__ src/closure_challenge/__init__.py'
```

Results: the negative control **failed** as required — `fatal: unable to access
… Could not resolve host: github.com`, exit 128 — so the namespace had no
network. The clone then succeeded from the mirror alone, `v0.2.1` checked out at
`4796ce359f8f65930ac641ead59dbc837a39ca94` with `__version__ = "0.2.1"`, and the
pinned commit `1c4e22c8…` checked out from the same rebuilt clone. **The mirror
alone is sufficient to rebuild the check.**

**Do not "tidy" this into `closure-challenge-pkg`.** It is deliberately separate
and deliberately bare. 25 scripts hard-code paths into the working clone and a
published record names the venv welded to it (`AWS_TREE_PLAN.md` §4.2), so the
working clone is not a safe place to add history. Refresh the mirror in place
instead:

```sh
git -C /home/ubuntu/mirrors/closure-challenge.git remote update --prune
```

### 4.3 Everything else outside the repository

| Location | Files | Size | What it is |
|---|---|---|---|
| `/home/ubuntu/closure-challenge-benchmark/` | 6,263 | 1.30 GB | the pinned scoring clone of section 4.2 |
| `/home/ubuntu/closure-venv/` | 9,797 | 0.38 GB | Python virtualenv for the closure work |
| `/home/ubuntu/backups/` | 8 | 0.36 GB | snapshot archives |
| `/home/ubuntu/dafoam-tutorials/` | 1,215 | 0.01 GB | upstream DAFoam tutorial cases |
| `/home/ubuntu/OpenFOAM/` | 19 | 0.01 GB | OpenFOAM user directory |
| `/home/ubuntu/Certonomous_closure_challenge/` | 164 | <0.01 GB | a second closure working copy |
| `/home/ubuntu/closure-challenge-pkg/` | 84 | <0.01 GB | the eval package clone the scorer actually runs from, pinned at `1c4e22c8` — **depth-1 shallow, holds that one commit only**; its history lives in §4.2b |
| `/home/ubuntu/notes/` | 8 | <0.01 GB | hand-written agent-memory notes. **Renamed from `/home/ubuntu/memory-import/` on 2026-08-17**; the 8 files and their MD5s are unchanged, and a 9th file, `README.md`, was added there after this reading |
| **Total** | **17,558** | **2.06 GB** | |
| `/home/ubuntu/mirrors/` (§4.2b, frame 2026-08-17) | 22 | <0.01 GB | full mirror of the scorer's history |
| **Including it** | **17,580** | **2.06 GB** | |

The benchmark clone is listed here as well as in section 4.2 because the total
includes it. A total that silently included a row the table did not show is the
defect this arrangement closes.

**`/home/ubuntu/mirrors/` is set below the total on purpose, for the same reason
§1's last two rows are.** The eight rows above are readings at `8cefb4e9`; the
mirror was created on 2026-08-17 and did not exist when they were taken. Folding
it silently into 17,558 would mix two frames in one total, which is the defect
this page exists to prevent. Its 1,225,553 B do not move the 2.06 GB at the
precision printed — `0.0012 GB` — but the file count does move, from 17,558 to
17,580, and that is shown rather than absorbed.

**One description in the table above was corrected on 2026-08-17, not its
figures.** The `closure-challenge-pkg` row previously read *"packaged submission
staging"*. It is not staging: it is the eval package clone that
`closure-venv`'s editable install imports, i.e. the scorer itself, and it is
shallow. Its 84 files and <0.01 GB are unchanged and remain the `8cefb4e9`
reading.

`/home/ubuntu/Certonomous_closure_challenge/` is the most volatile row in this
table: it is a working copy and its file count moved by more than a hundred
inside the hour this frame was taken. Its size stayed below 0.01 GB throughout.

#### 4.3a The themed directories added on 2026-08-17

**A later frame, set apart from the eight rows above for the reason §1 gives.**
`/home/ubuntu` was reorganised on 2026-08-17 so that every file sits in a folder
named for its theme and every such folder carries a README. Six directories are
new or newly populated. None of the eight rows above changed size as a result —
the bytes came out of §4.4's loose-file population, not out of these — but the
file counts below include the READMEs written at the same time, which did not
exist for any earlier frame.

Re-derived at 2026-08-17 20:47 UTC by one `os.walk(onerror=...)` + `lstat` pass
per directory with errors collected and raised rather than swallowed, **0 walk
errors**:

| Directory | Files | Apparent (B) | Symlinks | What it holds |
|---|---:|---:|---:|---|
| `/home/ubuntu/evidence/` | 12 | 558,709 | 2 | 8 loose evidence files moved out of `$HOME`, 4 READMEs, and symlinks `runs/` → `../certonomous-runs` and `ledger-backups/` → `../backups` |
| `/home/ubuntu/archives/` | 3 | 906,380,615 | 0 | the two large tarballs (§4.4) and a README |
| `/home/ubuntu/lab-scripts/` | 17 | 50,219 | 0 | 13 ParaView ladder rungs, `solverless_plugin.py`, 3 READMEs |
| `/home/ubuntu/notes/` | 9 | 22,278 | 0 | the 8 memory notes of §4.3 plus a README |
| `/home/ubuntu/upstream/` | 1 | 6,391 | 3 | a README and symlinks to the three pinned clones |
| `/home/ubuntu/toolchain/` | 1 | 6,579 | 2 | a README and symlinks to `OpenFOAM/` and `closure-venv/` |
| `/home/ubuntu/mirrors/` | 23 | 1,228,936 | 0 | §4.2b, plus the README added on 2026-08-17 |

```sh
# the walk used, per directory; it raises on any OSError rather than continuing
python3 - <<'EOF'
import os
errs=[]
for dp,dns,fns in os.walk(D, onerror=errs.append):
    ...   # sum st_size over regular files; collect sorted relpaths
assert not errs, errs
EOF
```

**Six of the seven symlinks point *out* of these directories at things that did
not move**, because each target is named by absolute path in code or in a
published record. `/home/ubuntu/README.md` states the rule and the measurements
behind it; `evidence/README.md`, `upstream/README.md` and `toolchain/README.md`
give the per-target detail. `closure-venv/lib64` is the eighth symlink under
`/home/ubuntu` at depth 2 and is the virtualenv's own, not part of this change.

**Nothing in the §4.3 table moved.** `closure-challenge-benchmark/`,
`dafoam-tutorials/`, `backups/`, `closure-venv/`, `closure-challenge-pkg/`,
`OpenFOAM/` and `certonomous-runs/` are all exactly where they were. A reference
sweep on 2026-08-17 (`/usr/bin/grep -rn -I --binary-files=without-match`, no
`head` in the pipeline, stderr captured, 0 errors) measured **85 lines in 59
files** naming `/home/ubuntu/closure-challenge-benchmark` and **17 lines in 14
files** naming `/home/ubuntu/dafoam-tutorials`, including
`sdk/workflows/onera_m6.py:46` and `sdk/workflows/crm_wingbody.py:43`; and
`scripts/ledger_backup.py:26` hard-codes `BACKUP_DIR = Path("/home/ubuntu/backups")`
as its **write target**. `AWS_TREE_PLAN.md` §3 proposed moving all three and did
not measure any of this.

### 4.4 Loose files directly in `/home/ubuntu`

39 files totalling 0.91 GB sit directly in the home directory and belong to none
of the directories above. Two of them carry almost all the bytes:

| File | Size |
|---|---|
| `certonomous-git-backup-20260730T033814Z.tar.gz` | 0.544 GB |
| `certonomous-cache.tar.gz` | 0.362 GB |
| the other 37 | 0.004 GB |

`ls -la /home/ubuntu` reaches them. Nothing else does.

**Changed 2026-08-17: 39 → 26 files.** Thirteen lab-authored ParaView scripts
(`render_naca_*.py` ×6, `test_paraview_*.py` ×7, 38,691 B apparent, 13 distinct
MD5s) were moved out of the home directory to
`/home/ubuntu/lab-scripts/paraview-render/`, which carries a README explaining
the version ladder and the citation evidence for keeping every rung. **Nothing
was deleted and every MD5 is unchanged by the move.** Re-derived after it:

```sh
/usr/bin/find /home/ubuntu -maxdepth 1 -type f | wc -l                              # -> 26
/usr/bin/find /home/ubuntu -maxdepth 1 -type f -exec stat -c %s {} + \
  | awk '{s+=$1} END{print s}'                                                       # -> 909,027,023
```

26 files, 909,027,023 B apparent. The drop from the `8cefb4e9` reading of
909,065,714 B is 38,691 B — exactly the thirteen scripts, and nothing else moved.
The two tarballs still carry 906,375,536 B of the remaining total.

**Changed again 2026-08-17: 26 → 15 files.** Eleven more files were moved out of
the home directory into the themed tree of §4.3a. **Nothing was deleted in this
step and every MD5 is unchanged by it** — each move was verified by comparing the
sorted path set, the byte size and the full-file MD5 before and after, and
asserting the source path gone.

| Moved from `/home/ubuntu/` | To | Bytes | MD5 |
|---|---|---:|---|
| `NIGHT_STATUS.md` | `evidence/status-records/` | 79,268 | `fb1a0abacb0dbe88bc58f7d48d911d19` |
| `MIGRATION_STATUS.md` | `evidence/status-records/` | 4,178 | `1fe90574f921c936c2841efc4f41d167` |
| `provision.log` | `evidence/provisioning-logs/` | 305,369 | `ae4268798a04b0ebb83728aea20b881f` |
| `suite.log` | `evidence/provisioning-logs/` | 135,265 | `79b6a8ddb37982ac3d45ede74a2e9344` |
| `suite-47fffd3.log` | `evidence/provisioning-logs/` | 12,157 | `ccf02dffe8aa9541b9fe491916b98a52` |
| `suite-47fffd3-solverless.log` | `evidence/provisioning-logs/` | 124 | `7c8afbe9fa623b4e466fe7f1cf8e3341` |
| `openvsp.log` | `evidence/provisioning-logs/` | 406 | `3f4d39b7c595421338dba4ab52bc43e8` |
| `scratch_live_readme.md` | `evidence/leaderboard/closure-challenge-live-board-2026-08-11T2333Z.md` | 10,080 | `30a58e97d59ebf8d463b434457d1adb5` |
| `solverless_plugin.py` | `lab-scripts/plugins/` | 1,045 | `accc25ddfb49767a6ccc8df06bef4922` |
| `certonomous-cache.tar.gz` | `archives/` | 362,066,284 | `d8857f35df9d458fa67e9934324feb1b` |
| `certonomous-git-backup-20260730T033814Z.tar.gz` | `archives/` | 544,309,252 | `5469d1873d4941fa8faf753af0750509` |
| **Total moved** | | **906,923,428** | |

**One of the eleven was renamed.** `scratch_live_readme.md` — a name that says
"scratch" about the only copy of the retrieved live leaderboard — is now
`evidence/leaderboard/closure-challenge-live-board-2026-08-11T2333Z.md`. §4.2 of
this page cites the retrieval time, "retrieved 2026-08-11T23:33Z", and the rename
preserved the mtime that carries it: `mv` within one filesystem is a rename, so
the inode, its mtime `2026-08-11 23:33:50 UTC` and its bytes are untouched. The
old name is recorded in `evidence/leaderboard/README.md`. A sweep for the string
`scratch_live_readme` across both repositories returned 10 lines, **all 10 inside
`AWS_TREE_PLAN.md`** — that page's own prose about this rename, i.e. the
instrument matching itself — and zero citations anywhere else.

Re-derived after the moves, stderr captured on every walk (**0 errors**):

```sh
/usr/bin/find /home/ubuntu -maxdepth 1 -type f 2>walk_err.txt | wc -l          # -> 16
/usr/bin/find /home/ubuntu -maxdepth 1 -type f -exec stat -c %s {} + \
  | awk '{s+=$1} END{print s}'                                                  # -> 2,118,479
wc -l < walk_err.txt                                                            # -> 0
```

16 files, 2,118,479 B apparent. That reconciles exactly, in two steps and with no
residue at either. **Moves only:** 909,027,908 (the reading taken immediately
before the moves, 885 B above the 909,027,023 recorded earlier because the three
live logs and `.claude.json` had grown in between) minus the 906,923,428 B in the
table = **15 files, 2,104,480 B**. **Then one file was added:**
`/home/ubuntu/README.md`, the orientation page, 13,999 B — written after that
reading was taken, which is why it is stated as a second step rather than folded
back into the first. 2,104,480 + 13,999 = 2,118,479.

**Fifteen of the sixteen remain because they must**, and
`/home/ubuntu/README.md` — the sixteenth — says why for each: three live logs
whose writers hold open file descriptors on them, the
seven shell/user dotfiles, `.bash_history`, the two `.bashrc` backups awaiting an
answer, and `lab.sh` and `provision.sh` — which are **installed deployments**
registered in `scripts/installed_registry.py`, not the stray duplicates
`AWS_TREE_PLAN.md` §6.4 classified them as. The registry reads MATCH for both
today, and `sdk/tests/test_installed_matches_tracked.py` refuses any difference,
so deleting either would break a passing check and remove the tmux session
operators attach to.

**One file was deleted from `/home/ubuntu` on 2026-08-17, and only one:**
`__pycache__/solverless_plugin.cpython-312-pytest-9.1.1.pyc`, 1,819 B, MD5
`778dd062e28a6e0116fd5304889baf8a`, together with the emptied `__pycache__/`
directory. It was a derived CPython bytecode cache, proved redundant by
regenerating it from the unchanged source and by the fact that
`/home/ubuntu/solverless_plugin.py` no longer exists so CPython could not consult
it. Nothing referenced it. The full manifest line is in `/home/ubuntu/README.md`.
That 1,819 B is the **entire** deletion made against this machine in the
reorganisation.

### 4.5 Agent dispatch records, the independence evidence

```
~/.claude/projects/<project-slug>/<session-id>/subagents/agent-<hex>.jsonl
```

Per-machine and untracked. No clone contains them. This matters because
R-ISOLATE, the rule that a ladder rung must be graded by a non-author, cannot be
checked from the repository at all: every commit on this box carries the same
`Ubuntu <ubuntu@ip-172-31-43-247…>` identity, so `git log --format=%an` cannot
discriminate between agents. The dispatch records are the only sound evidence of
which agent did what, and they live here, outside version control, permanently.

**They have a size and it is in §4.6.** Re-derived 2026-08-17:

```sh
/usr/bin/find /home/ubuntu/.claude/projects /home/ubuntu/.claude-sanaa/projects \
              -type f -name 'agent-*.jsonl' | wc -l                     # -> 1,573
```

**1,573 dispatch records**, in the two `.claude*` trees, which hold 3.58 GB
between them. This count moves: it was 1,557 earlier the same day, because the
fleet writes a new record every time an agent is dispatched. Take your own
reading.

### 4.6 The dotted directories in `/home/ubuntu`

**This section did not exist until 2026-08-17, and its absence was the largest
hole in this page.** Sections 4.1–4.4 enumerate the run tree, the named
directories and the loose files, and a reader who took them as complete would
conclude that everything outside the repositories and the run tree came to
2.06 GB. The true figure is 14.10 GB. The 12.04 GB difference is below, and two
of its entries are the evidence corpus §4.5 has always called irreplaceable.

Frame **2026-08-17 15:52 UTC**. Both columns were re-derived here, not copied
from any other document; stderr was captured on every walk and **zero errors were
recorded**.

```sh
for d in .mutarc-64b13819 .claude .claude-sanaa .local .cache .texlive2023 .npm .ssh .config; do
  /usr/bin/find "/home/ubuntu/$d" -type f 2>>walk_err_$d.txt | wc -l          # Files
  du -sb "/home/ubuntu/$d"                                                    # du -sb
  /usr/bin/find "/home/ubuntu/$d" -type f -exec stat -c %s {} + \
    | awk '{s+=$1} END{print s}'                                              # Apparent
done
```

| Directory | Files | `du -sb` (B) | Apparent (B) | What it is |
|---|---:|---:|---:|---|
| `.mutarc-64b13819/` | 20,853 | 7,036,239,167 | 7,036,238,778 | **harness session scratch, not lab content** — see the note below |
| `.claude/` | 3,734 | 1,821,687,479 | 1,821,687,479 | agent dispatch records (§4.5) — **live, grows while the fleet runs** |
| `.claude-sanaa/` | 3,273 | 1,762,655,576 | 1,762,655,576 | agent dispatch records (§4.5) |
| `.local/` | 9,627 | 1,291,641,783 | 1,291,641,734 | user-installed tooling |
| `.cache/` | 302 | 125,677,762 | 125,677,762 | caches |
| `.texlive2023/` | 23 | 621,612 | 621,612 | TeX Live user tree |
| `.npm/` | 13 | 19,519 | 19,519 | npm cache |
| `.ssh/` | 10 | 3,167 | 3,167 | keys — **do not relocate** |
| `.config/` | 2 | 115 | 115 | |
| **Total** | **37,837** | **12,038,546,180** | **12,038,545,742** | **12.04 GB either way** |

**`.claude/` is a moving target and its row is a floor, not a census.** It read
3,648 files / 1,790,759,298 B a little under an hour earlier the same day. Every
other row reproduced its earlier reading to the byte.

**`.mutarc-64b13819/` is 7.04 GB and it is not lab content.** It is a harness
archive of commit `e1ede44a`, verified an ancestor of `main`, holding exactly one
commit whose message is "archive of `e1ede44a`". It contains **no unlanded git
history**, and nothing in it needs preserving that `main` does not already carry.
It is listed here because it is 58% of this section's bytes and a reader
measuring the machine will trip over it, not because it is evidence. Its name
suffix is an agent session ID.

**What this section changes for a reader of §1.** Outside the two repositories
and the run tree, the machine holds 2.06 GB (§4.3) **plus** 12.04 GB here —
14.10 GB, not 2.06 GB. `ls -la /home/ubuntu` shows these directories; `ls` alone
and every `find` without `-name '.*'` handling does not.

---

## 5. The four corpus arms

Any sweep, count or claim of coverage in this lab must name which arm it read.
They are not interchangeable and no single command reaches all four.

| Arm | Files at `8cefb4e9` | How to enumerate |
|---|---|---|
| Tracked | 20,764 | `git ls-files` |
| Untracked, not ignored | 1 | `git ls-files --others --exclude-standard` |
| Gitignored | 37,243 | `git ls-files --others --ignored --exclude-standard` |
| Run tree | 132,049 regular files | `/usr/bin/find /home/ubuntu/certonomous-runs -type f` |

For the run tree, say which population you mean: 132,049 regular files, 132,797
including symlinks, or 132,761 excluding the 36 loose root files (section 4.1).

**Three reach limits inside the tracked arm alone**, all measured at `8cefb4e9`:

| Limit | Count | Of | What is lost |
|---|---|---|---|
| `git grep -a` reach | 20,738 | 20,764 tracked | 26 files |
| Unreachable by `git grep` in any mode, `-a` included | 26 | | 17 symlinks (mode 120000) and 9 empty blobs |
| Additionally skipped by `git grep -I` | 1,476 | | 981 that `.gitattributes` marks binary, plus 495 git auto-detects from NUL bytes |
| Of the 981 marked, containing no NUL byte at all | 11 | 981 | plain text, including published certificate PDFs |

The 26-file gap has been stable across every frame measured this week even as
both totals moved. The shell `grep` is `ugrep --ignore-files` and already passes
`-I`, so it drops the gitignored arm and the binary-marked files at once.

**The 1,476 and the 981 are different populations and neither is the other.**
`.gitattributes` marks 981 tracked files binary by extension (875 `.png`, 54
`.stl`, 50 `.pdf`, 2 `.obj`, re-derived with `git check-attr --stdin binary`).
`git grep -I` skips those and a further 495 it auto-detects from NUL bytes,
which is where 1,476 comes from. Of the 981, exactly 11 contain no NUL byte in
the whole blob. The figure is 12 if the test looks only at the first 8,000
bytes, and the one file that separates the two readings is
`docs/papers/Paper3.pdf`. Say which window a NUL test used.

**PDFs cannot be graded from their text layer.** LaTeX `\sout{}` is
strike-and-keep: a withdrawn figure sits in the text stream of a corrected
document exactly as it does in a stale one. Reading a PDF claim requires
rendering the page to PNG and looking at it.

| PDF population | Count |
|---|---|
| Tracked | 50 |
| Whole working tree | 68 |
| The difference | 18, all `certificate.pdf` under `dist/certonomous-demo/mission-output/` and `mission-output/`, which are untracked |

---

## 6. Limits, in one place

1. **Every count and size here is a reading at `8cefb4e9`, not a constant.** The
   tracked and gitignored arms move several times an hour. Each row carries the
   command that reproduces it, so take your own reading before quoting one.

2. **Three size quantities differ here, and they are not interchangeable.**

   | Quantity | Run tree value | Exact bytes | What it counts |
   |---|---|---:|---|
   | Apparent, summed `st_size` over regular files | 75.79 GB | 75,789,971,753 | every hardlink instance separately |
   | Deduplicated by `(st_dev, st_ino)` | 69.36 GB | 69,364,664,057 | each regular-file inode once |
   | `du -sb` | 69.36 GB | 69,364,681,327 | the deduplicated figure **plus symlink targets** |
   | Disk usage, `du -s --block-size=1` | 69.85 GB | 69,847,584,768 | allocated blocks |

   The run tree holds 135 extra hardlink instances, so its apparent total counts
   about 6.43 GB of bytes twice. Disk usage exceeds the deduplicated byte count,
   which is the normal direction and is block-rounding, not sparseness. A size
   figure quoted without naming which of these four it is cannot be checked.

   **Correction, 2026-08-17: the deduplicated count does not "match `du -sb`
   exactly", and the 17,270-byte gap is not directory inodes.** This page said
   the first and `AWS_TREE_PLAN.md` §2 said the second. Re-derived by one
   `os.walk(onerror=…)` + `lstat` pass over the tree, 0 walk errors:

   ```
   deduplicated regular-file bytes   69,364,664,057
   du -sb                            69,364,681,327
   difference                                17,270
   sum of st_size over 748 symlinks          17,270   <- exactly the difference
   sum of st_size over 37,650 directories 154,271,744   <- three orders too large
   ```

   `du -sb` is `du --apparent-size --block-size=1`. It counts each regular-file
   inode once (it deduplicates hardlinks itself) **and adds the symlinks**, whose
   apparent size is the byte length of the target path. It does **not** add
   directory `st_size`: if it did, the gap would be about 154 MB, not 17 KB.
   Confirmed in a controlled scratch directory rather than argued from `du`'s
   documentation — one 1,000 B file, a hardlink to it, a 500 B file in a
   subdirectory, and a 2-byte symlink give `du -sb` = 1,502 = 1,000 + 500 + 2,
   with the two 4,096 B directories contributing nothing.

   So the honest statement is: **`du -sb` and a deduplicated `st_size` sum agree
   on this tree to within the symlink targets, and only because they are 17 KB.**
   On a tree with many symlinks they would visibly diverge.

3. **If this instance is lost, sections 3 and 4 are lost with it.** The machine
   is an AWS EC2 instance, hostname `ip-172-31-43-247`. Only section 2 survives,
   because only section 2 is on GitHub. There is no off-box replica of the run
   tree, the dispatch records or the gitignored case archives.

4. **Some figures here are floors rather than censuses**, and the ones that are
   say so in their own row. Where a row gives no such qualifier it is a complete
   enumeration of the population its column names.

5. **No third party has re-derived any figure on this page.** Every number is the
   lab measuring its own machine.


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/Paper3.pdf` | `docs/papers/verification_validation/oberkampf_roy_2011_verification_validation.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.

---

## ansys-verification team — appended 2026-08-24

**Nothing above this line was edited.** Sanaa's directive of 2026-08-24 created
a sixth team, `ansys-verification` (`docs/charters/ANSYS_VERIFICATION_CHARTER.md`),
whose paths are new and are listed here so the index stays whole.

| Location | What | Tracked |
|---|---|---|
| `docs/charters/ANSYS_VERIFICATION_CHARTER.md` | the team's charter, v1.0 | yes |
| `docs/ansys_verification/` | team prose; `README.md` is the map | yes |
| `cases/ansys_verification/<CASE>/` | pre-registrations and RESULTS per manual case | yes, as created |
| `verification/runs/ansys_verification/<CASE>/` | run outputs | per the run-tree rules |
| `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | every case run and its verdict; PASS rows are the credentials | yes, append-only |
| `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.{pdf,txt}` | the manual and its sidecar (8,517,733 B / 368,949 B) — the directory stays with the verification team | yes |
| `VM2026R1_Fluids/` (repository root) | the complete Ansys VM2026R1 archive set: 123 files, 2.5 GB (`du -sh`), FLUENT 77 / CFX 37 / FORTE 9 files | **no** — untracked, not gitignored; canonical home is the team supervisor's first ruling (D-6) |
| `docs/papers/verification_validation/VM2026R1_Fluids/` | a dead partial transfer: 10 CFX files, 26 MB; 9 byte-identical to the root copy, `VMFL011B.wbpz` truncated at 327,680 of 670,152 B | **no** — untracked |

The charter §9 recommends the lab's existing pattern for data too large for
git — a directory under `/home/ubuntu/` beside `closure-data/` and
`certonomous-runs/`, enumerated in §4.3 above — with a `.gitignore` entry for
any in-repository extraction directory. Re-derive the counts with `find … -type
f | wc -l`, `du -sh`, and `sha256sum`; they are readings, not constants.
