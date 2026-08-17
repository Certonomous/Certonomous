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

The deduplicated column is measured on all four off-repository bodies, not
assumed. Only the run tree contains hardlinks; on the other three the two
columns are equal because there are none to remove. File counts are the
enumeration commands' own counts; sizes are summed over the regular files among
them.

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

**It scores but does not rank.** It is not an admissible board identifier, and
its four-entrant README is not the live board. The live board carries six
entrants plus this lab's entry, retrieved 2026-08-11T23:33Z and re-verified
unchanged 2026-08-14T21:01Z.

### 4.3 Everything else outside the repository

| Location | Files | Size | What it is |
|---|---|---|---|
| `/home/ubuntu/closure-challenge-benchmark/` | 6,263 | 1.30 GB | the pinned scoring clone of section 4.2 |
| `/home/ubuntu/closure-venv/` | 9,797 | 0.38 GB | Python virtualenv for the closure work |
| `/home/ubuntu/backups/` | 8 | 0.36 GB | snapshot archives |
| `/home/ubuntu/dafoam-tutorials/` | 1,215 | 0.01 GB | upstream DAFoam tutorial cases |
| `/home/ubuntu/OpenFOAM/` | 19 | 0.01 GB | OpenFOAM user directory |
| `/home/ubuntu/Certonomous_closure_challenge/` | 164 | <0.01 GB | a second closure working copy |
| `/home/ubuntu/closure-challenge-pkg/` | 84 | <0.01 GB | packaged submission staging |
| `/home/ubuntu/memory-import/` | 8 | <0.01 GB | memory import staging |
| **Total** | **17,558** | **2.06 GB** | |

The benchmark clone is listed here as well as in section 4.2 because the total
includes it. A total that silently included a row the table did not show is the
defect this arrangement closes.

`/home/ubuntu/Certonomous_closure_challenge/` is the most volatile row in this
table: it is a working copy and its file count moved by more than a hundred
inside the hour this frame was taken. Its size stayed below 0.01 GB throughout.

### 4.4 Loose files directly in `/home/ubuntu`

39 files totalling 0.91 GB sit directly in the home directory and belong to none
of the directories above. Two of them carry almost all the bytes:

| File | Size |
|---|---|
| `certonomous-git-backup-20260730T033814Z.tar.gz` | 0.544 GB |
| `certonomous-cache.tar.gz` | 0.362 GB |
| the other 37 | 0.004 GB |

`ls -la /home/ubuntu` reaches them. Nothing else does.

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
| Additionally skipped by `git grep -I` | 1,476 | | files `.gitattributes` marks binary |
| Of those, containing no NUL byte at all | 11 | 1,476 | plain text, including published certificate PDFs |

The 26-file gap has been stable across every frame measured this week even as
both totals moved. The shell `grep` is `ugrep --ignore-files` and already passes
`-I`, so it drops the gitignored arm and the binary-marked files at once.

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

   | Quantity | Run tree value | What it counts |
   |---|---|---|
   | Apparent, summed `st_size` | 75.79 GB | every hardlink instance separately |
   | Deduplicated by `(st_dev, st_ino)` | 69.36 GB | each inode once; matches `du -sb` exactly |
   | Disk usage, `du -s --block-size=1` | 69.85 GB | allocated blocks |

   The run tree holds 135 extra hardlink instances, so its apparent total counts
   about 6.43 GB of bytes twice. Disk usage exceeds the deduplicated byte count,
   which is the normal direction and is block-rounding, not sparseness. A size
   figure quoted without naming which of these three it is cannot be checked.

3. **If this instance is lost, sections 3 and 4 are lost with it.** The machine
   is an AWS EC2 instance, hostname `ip-172-31-43-247`. Only section 2 survives,
   because only section 2 is on GitHub. There is no off-box replica of the run
   tree, the dispatch records or the gitignored case archives.

4. **Some figures here are floors rather than censuses**, and the ones that are
   say so in their own row. Where a row gives no such qualifier it is a complete
   enumeration of the population its column names.

5. **No third party has re-derived any figure on this page.** Every number is the
   lab measuring its own machine.
