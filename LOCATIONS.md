# LOCATIONS — where every part of this lab's work lives

Measured 2026-08-16 at repository HEAD `60795b90`. Sizes are **decimal GB from
summed apparent file sizes** (`/usr/bin/find -printf '%s'`, summed), which is a
different quantity from `du` disk usage — on the run tree the two differ by
roughly 7%, apparent size exceeding disk usage, which indicates sparse files or
filesystem compression. **A size figure is meaningless without saying which of
the two it is.** Several older lab records state "66 GB" as a byte total for the
run tree; as a byte total that is wrong, and the correct apparent-size figure is
75.79 GB. Where a figure below is a floor rather than a census, it says so.

**Why this file exists.** Roughly 80 GB of this lab's output cannot live in a git
repository: GitHub rejects any file over 100 MB, warns above 50 MB, and treats
repositories over ~5 GB as out of policy. Everything that *can* be committed has
been. Everything that cannot is enumerated here with its exact location, so that
nothing is invisible merely because it is large.

---

## 1. In this repository, and on GitHub

| | Files | Size |
|---|---|---|
| Tracked and pushed | 20,727 | 1.82 GiB packed |

Remote: `git@github.com:Certonomous/Certonomous.git`, branch `main`.

The largest tracked file is
`demo-output/website/campaign/F8_runs/phase6_mrf/constant/triSurface/blade.stl`
at **68.1 MB** — above GitHub's 50 MB warning threshold and below its 100 MB
hard reject. It is the only tracked file over 50 MB.

---

## 2. Inside the repository but deliberately not committed

`.gitignore` excludes **37,258 files totalling 11.91 GB**. These sit in the
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

**132,761 files, 75.79 GB decimal (70.59 GiB), across 446 top-level study
directories.** This is every solver run the lab has executed. It is outside the
repository entirely and invisible to every git-based route.

Largest studies:

| Size | Files | Study |
|---|---|---|
| 12.57 GB | 6,342 | `dpw5-committee-probe` |
| 7.64 GB | 2,446 | `w3-naca4412-layered-replicates` |
| 2.24 GB | 462 | `f5a-cylinder-ladder` |
| 2.14 GB | 1,898 | `w3-naca0012_wing-family` |
| 1.53 GB | 210 | `credential-repair-naca4412-finer` |
| 1.51 GB | 1,264 | `w3-naca4412_wing-family` |
| 1.48 GB | 257 | `hlpw6-memory-probe` |
| 1.10 GB | 37,064 | `W5-regrade` |
| 1.02 GB | 172 | `A3-diag-rung3` |
| 1.01 GB | 3,129 | `F6a_diffusion` |

Full listing: `ls /home/ubuntu/certonomous-runs/`.

**A measurement trap specific to this tree**, recorded because it has produced a
false reading here: GNU `find`'s `-size -2M` and `-size +2M` are **not
complementary** — they return 121,523 and 6,108 against a true 132,049, leaving
**4,418 files invisible to both bands**. Any size-banded sweep must reconcile its
bands against an independently obtained total. Note also that `find` on this box
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
| `/home/ubuntu/closure-venv/` | 9,800 | 0.40 GB | Python virtualenv for the closure work |
| `/home/ubuntu/dafoam-tutorials/` | 1,215 | 0.01 GB | upstream DAFoam tutorial cases |
| `/home/ubuntu/OpenFOAM/` | 19 | 0.01 GB | OpenFOAM user directory |
| `/home/ubuntu/Certonomous_closure_challenge/` | 59 | <0.01 GB | earlier closure working copy |
| `/home/ubuntu/closure-challenge-pkg/` | 84 | <0.01 GB | packaged submission staging |
| `/home/ubuntu/memory-import/` | 8 | <0.01 GB | memory import staging |

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

| Arm | Reach | How to enumerate |
|---|---|---|
| **Tracked** | 20,727 files | `git ls-files` |
| **Untracked** | 1–5 files | `git ls-files --others --exclude-standard` |
| **Gitignored** | 37,258 files | `git ls-files --others --ignored --exclude-standard` |
| **Run tree** | 132,761 files | `ls /home/ubuntu/certonomous-runs/` |

**Three reach limits inside the tracked arm alone**, all measured:

- `git grep -a` reaches **20,688 of 20,714** tracked blobs at the measured frame.
  The remaining **26 — 17 symlinks (mode 120000) and 9 empty blobs — are
  unreachable by `git grep` in any mode**, including `-a`.
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
