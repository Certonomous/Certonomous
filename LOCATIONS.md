# LOCATIONS — where every part of this lab's work lives

Measured 2026-08-16 at repository HEAD `60795b90`, and **re-measured against an
independent audit at `1fc1f639` which refuted six figures in the first version of
this file.** Every correction below is marked; the wrong figures are named rather
than quietly replaced, because this file is the one a reader trusts to locate
things.

Sizes are **decimal GB from summed apparent file sizes**, and the distinction
that matters is not the one the first version drew:

- **Apparent size counts a hardlinked file once per link.** The run tree holds
  **135 extra hardlink instances**, so its naive apparent total of **75.79 GB
  counts about 6.43 GB of bytes twice.** Deduplicating by `(st_dev, st_ino)`
  gives **69.36 GB**, which matches `du -sb` exactly.
- **Disk usage EXCEEDS apparent size here, which is the normal direction**:
  `du -sb` 69.36 GB against `du -s --block-size=1` 69.85 GB.
  ~~The first version of this file attributed the gap to "sparse files or
  filesystem compression" and had the direction backwards.~~ **There are no
  sparse files driving this; the cause is hardlinks.**

**A size figure is meaningless without saying which quantity it is.** Several
older lab records state "66 GB" as a byte total for the run tree; as a byte total
that is wrong. Where a figure below is a floor rather than a census, it says so.

**Why this file exists.** ~~Roughly 80 GB~~ **Roughly 90 GB apparent, or 83 GB
once hardlinks are deduplicated,** of this lab's output cannot live in a git
repository: GitHub rejects any file over 100 MB, warns above 50 MB, and treats
repositories over ~5 GB as out of policy. Everything that *can* be committed has
been. Everything that cannot is enumerated here with its exact location, so that
nothing is invisible merely because it is large.

The composition, since "roughly 90 GB" should not be an unexplained number:
run tree 75.79 GB apparent (69.36 GB deduplicated) + gitignored-in-repo 11.90 GB
+ external directories 2.06 GB + loose files in `/home/ubuntu` 0.91 GB =
**90.66 GB apparent, 84.23 GB deduplicated.**

---

## 1. In this repository, and on GitHub

| | Files | Size |
|---|---|---|
| Tracked | 20,750 | 1.82 GiB packed |

Remote: `git@github.com:Certonomous/Certonomous.git`, branch `main`. **The
tracked count moves several times an hour while the lab is working**, so treat it
as a reading at a frame, not a constant; re-derive with `git ls-files | wc -l`.

The largest tracked file is
`demo-output/website/campaign/F8_runs/phase6_mrf/constant/triSurface/blade.stl`
at **68.1 MB** — above GitHub's 50 MB warning threshold and below its 100 MB
hard reject. It is the only tracked file over 50 MB (verified at `1fc1f639`:
exactly one blob exceeds 50 MB).

---

## 2. Inside the repository but deliberately not committed

`.gitignore` excludes **37,256 files totalling 11.90 GB** (the first version of
this file said 37,258 / 11.91). These sit in the
working tree on this machine and are reachable by path, but no clone contains
them. Enumerate with:

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
| `sdk/` | 1,590 | 0.04 GB |
| everything else | ~131 | <0.03 GB |

**These are case archives and solver output**, not source. A repo-wide `grep -r`
**cannot see them at all** — the shell `grep` here is `ugrep --ignore-files`,
which honours `.gitignore` silently. Any sweep claiming to cover "the corpus"
must say which of the four arms it read (see §5).

---

## 3. Outside the repository, on this machine

### 3.1 The run tree — the largest single body of work

```
/home/ubuntu/certonomous-runs/
```

**446 top-level study directories, 75.79 GB apparent (70.59 GiB) — 69.36 GB once
the 135 hardlinks are deduplicated.** This is every solver run the lab has
executed. It is outside the repository entirely and invisible to every git-based
route.

**The file count depends on what you count, and the first version of this file
gave two different populations without saying so.** All three are correct:

| Population | Count |
|---|---|
| Regular files only (`find -type f`) | **132,049** |
| Regular files + 748 symlinks | **132,797** |
| The same, excluding 36 loose files at the tree root | **132,761** |

Ten largest studies. ~~The first version of this file omitted rank 8 and
presented the remainder as "the ten largest"~~ — every individual size and count
in it reproduced, but the table was ten of the eleven largest:

| Size | Files | Study |
|---|---|---|
| 12.57 GB | 6,342 | `dpw5-committee-probe` |
| 7.64 GB | 2,446 | `w3-naca4412-layered-replicates` |
| 2.24 GB | 462 | `f5a-cylinder-ladder` |
| 2.14 GB | 1,898 | `w3-naca0012_wing-family` |
| 1.53 GB | 210 | `credential-repair-naca4412-finer` |
| 1.51 GB | 1,264 | `w3-naca4412_wing-family` |
| 1.48 GB | 257 | `hlpw6-memory-probe` |
| **1.46 GB** | **196** | **`credential-repair-naca4412-finer_relayered_ngrow0`** ← omitted before |
| 1.10 GB | 37,064 | `W5-regrade` |
| 1.02 GB | 172 | `A3-diag-rung3` |

Next after those: `F6a_diffusion` 1.01 GB / 3,129 files, then
`credential-repair-naca4412-finer_relayered` 0.88 GB / 206 files.

Full listing: `ls /home/ubuntu/certonomous-runs/`. Note the **36 loose files at
the tree root**, which sit in no study directory and are easy to miss.

**A measurement trap specific to this tree**, recorded because it has produced a
false reading here: GNU `find`'s `-size -2M` and `-size +2M` are **not
complementary** — they return 121,523 and 6,108 against a true **132,049 regular
files** (the `-type f` population above, not the 132,761 figure), leaving
**4,418 files invisible to both bands**: `-size ±2M` rounds up to whole MiB, so
anything above 1 MiB and up to 2 MiB rounds to exactly 2 and falls in neither
strict band. `121,523 + 6,108 + 4,418 = 132,049` exactly. Any size-banded sweep
must reconcile its bands against an independently obtained total, **and must say
which file population its total is over**. Note also that `find` on this box
is `bfs`, which rejects GNU expressions such as `-printf`; use `/usr/bin/find`.

### 3.2 The scoring benchmark clone

```
/home/ubuntu/closure-challenge-benchmark/     1.30 GB, 6,263 files
```

Pinned at commit **`deb91557184af3cb95f5190494ec52d8f2c6a0d1`**, from the public
repository `https://github.com/rmcconke/closure-challenge-benchmark.git`. **This
one is reachable by anyone** — it is not private lab state.

**It scores but does not rank.** It is not an admissible board identifier, and
its four-entrant README is not the live board. The live board carries six
entrants plus us, retrieved 2026-08-11T23:33Z and re-verified 2026-08-14T21:01Z.

### 3.3 Everything else outside the repository

| Location | Files | Size | What it is |
|---|---|---|---|
| `/home/ubuntu/backups/` | 8 | 0.36 GB | snapshot archives |
| `/home/ubuntu/closure-venv/` | 9,800 | 0.38 GB | Python virtualenv for the closure work |
| `/home/ubuntu/dafoam-tutorials/` | 1,215 | 0.01 GB | upstream DAFoam tutorial cases |
| `/home/ubuntu/OpenFOAM/` | 19 | 0.01 GB | OpenFOAM user directory |
| `/home/ubuntu/Certonomous_closure_challenge/` | 59 | <0.01 GB | earlier closure working copy |
| `/home/ubuntu/closure-challenge-pkg/` | 84 | <0.01 GB | packaged submission staging |
| `/home/ubuntu/memory-import/` | 8 | <0.01 GB | memory import staging |

**External total: 2.06 GB across 17,456 files.**

**Also outside every row above, and missed by the first version of this file:
0.91 GB of loose files sitting directly in `/home/ubuntu`**, including
`certonomous-cache.tar.gz` and `certonomous-git-backup-*.tar.gz`. They belong to
no directory listed here. `ls -la /home/ubuntu` reaches them; nothing else does.

### 3.4 Agent dispatch records — the independence evidence

```
~/.claude/projects/<project-slug>/<session-id>/subagents/agent-<hex>.jsonl
```

**Per-machine and untracked. No clone contains them.** This matters because
R-ISOLATE — the rule that a rung must be graded by a non-author — cannot be
checked from the repository at all: every commit on this box carries the same
`Ubuntu <ubuntu@ip-172-31-43-247…>` identity, so `git log --format=%an` cannot
discriminate between agents. The dispatch records are the only sound evidence of
who did what, and they live here, outside version control, permanently.

---

## 4. What this machine is

An AWS EC2 instance, hostname `ip-172-31-43-247`. The run tree, the dispatch
records and the gitignored case archives are all local to it. **If this instance
is lost, §2 and §3 are lost with it**; only §1 survives, because only §1 is on
GitHub.

---

## 5. The four corpus arms

Any sweep, count or claim of coverage in this lab must name which arm it read.
They are not interchangeable and no single command reaches all four.

All four counts are readings at `1fc1f639`, not constants — the tracked and
gitignored arms move several times an hour while the lab is working.

| Arm | Reach | How to enumerate |
|---|---|---|
| **Tracked** | 20,750 files | `git ls-files` |
| **Untracked** | 1–5 files | `git ls-files --others --exclude-standard` |
| **Gitignored** | 37,257 files | `git ls-files --others --ignored --exclude-standard` |
| **Run tree** | 132,049 regular files | `/usr/bin/find /home/ubuntu/certonomous-runs -type f` |

For the run tree, **say which population you mean** — 132,049 regular files,
132,797 including symlinks, or 132,761 excluding the 36 loose root files (§3.1).

**Three reach limits inside the tracked arm alone**, all measured:

- `git grep -a` reaches **20,724 of 20,750** tracked blobs at `1fc1f639`.
  The remaining **26 — 17 symlinks (mode 120000) and 9 empty blobs — are
  unreachable by `git grep` in any mode**, including `-a`. That 26-file gap has
  been stable across every frame measured this week even as both totals moved.
- `git grep -I` additionally skips **1,476** files `.gitattributes` marks binary,
  **11 of which contain no NUL byte at all**, including published certificate
  PDFs. A text sweep run with `-I` silently drops them.
- The shell `grep` is `ugrep --ignore-files` and already passes `-I`, so it drops
  both the gitignored arm and the binary-marked files at once.

**PDFs cannot be graded from their text layer.** LaTeX `\sout{}` is
strike-and-keep: a withdrawn figure sits in the text stream of a correctly
repaired document exactly as it does in a stale one. Reading a PDF claim requires
rendering the page to PNG and looking at it. There are **50 tracked PDFs** and 68
whole-tree; the 18-file difference is `certificate.pdf` under
`dist/certonomous-demo/mission-output/` and `mission-output/`, which are
untracked.
