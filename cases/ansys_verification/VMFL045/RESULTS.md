# VMFL045 — Oblique Shock Over an Inclined Ramp: RESULTS (run 1)

**NOT FILED ANYWHERE. Nothing here is sent, emailed, uploaded, filed, posted,
registered or commented outside this box** (CLAUDE.md rules 7, 8). The manual is
proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**This file records run 1 and does NOT revise the frozen pre-registration**
(`PREREGISTRATION.md`, blob `7a7f9d52fe8666a5ef3dd72c6dd4262e93b75b74`, freeze commit
`6a9701e1`). It is written by the **run-and-grade lane** (`ansys-lane-opus48`, Opus
4.8) after the supervisor's triage. The **crash-triage report of record is the first
lane's** committed `LANE_REPORT.md` (blob at commit `f1f58fd`); this file credits it
and does not duplicate or contradict it.

---

## VERDICT: `NOT A RESULT`  ·  TIER: `NOT HELD`  ·  COST: 0.0000 core-min

**Nothing gradeable was produced.** `rhoCentralFoam` crashed on its first timestep, at
`wall = 0 s`, before any real solve. The comparator, run against the tree, correctly
**refuses** (clause C1, `rc = 1`) and grades nothing. The tier is `NOT HELD` under the
supervisor's standing default and this team's own precedent (VMFL001 run 1, VMFL051):
**a `NOT A RESULT` that produced no measurement has nothing to hold.** There is no gate
value, no triple, no observed order and no GCI — because the solver never advanced a
real step.

This is the verdict framing ruled by the `ansys-verification-supervisor`. (This lane
had proposed `BLOCKED`; both are in the rule-1 vocabulary and the supervisor's
`NOT A RESULT` is adopted, matching the team's row #1 precedent for a comparator
refusal.)

---

## 1. What ran, and exactly where it stopped

**Run 1 tree:** `verification/runs/ansys_verification/VMFL045/L1_90x76/` (only L1;
L2/L3 were never created). All of it timestamped `01:36:45Z`.

| stage | outcome |
|---|---|
| `blockMesh` | OK |
| `checkMesh` | **`Mesh OK`** (a clean mesh; the first lane records max non-orthogonality 14.9°, max skewness 0.398, max aspect ratio 1.49) |
| `topoSet` | filled **both** frozen zones: **`gateZone` 252 cells, `gateZoneInner` 148 cells** — matching the pre-registration's predicted ~252. **The frozen §5 sampling rule is sound.** |
| `rhoCentralFoam` | **CRASHED, `rc = 1`, `wall = 0 s`**, inside the first pseudo-timestep (`deltaT = 1.2e−8`), before any real solve, with the fatal below |

**The fatal, verbatim from `L1_90x76/log.rhoCentralFoam`:**

> `--> FOAM FATAL IO ERROR: (openfoam-2606)`
> `Entry 'e' not found in dictionary "system/fvSolution/solvers"`
> (`dictionary.C` at line 457)

`RUN_RC.txt` records `rc=1`, `wall_s=0`, `core_min=0.0000`, and carries the frozen blob
stamps `prereg_blob=7a7f9d52…`, `grader_blob=0c83eeef…` — so the crashed run is bound
to the same freeze the supervisor verified. The launcher then **refused (exit 2)** —
*"a crash is a finding, triage before anything else"* — and never proceeded to L2/L3.
Both instruments (launcher and comparator) behaved correctly.

## 2. The finding — a frozen-input setup defect, INDEPENDENTLY REPLICATED

This is a **setup defect in the frozen case inputs, not a numerical failure of the
case.** It was reached **independently by three readers converging on one mechanism**,
which is stronger evidence than any one alone:

1. the **first lane** (crash-triage `LANE_REPORT.md`, commit `f1f58fd`);
2. the **run-and-grade lane** (this file's author), from the same log and HEAD blobs;
3. the **`ansys-verification-supervisor`**, whose triage added the load-bearing
   viscous-corrector proof below.

**Root cause.** The frozen `thermophysicalProperties` (blob `f13a67413…`) declares
`energy sensibleInternalEnergy`, so the thermo energy field is **`e`**. The frozen
`fvSolution` (blob `1e3fb953…`), cloned from VMFL051, provides a solver named **`h`**
and no `e`. When viscosity is nonzero, `rhoCentralFoam` runs an **implicit viscous
energy-diffusion correction** that solves a linear system for the thermo's energy
variable and therefore requires an `fvSolution/solvers` entry named for it. With `e`
absent, the solver aborts on the first step. The `h` entry is also simply the wrong
name for `sensibleInternalEnergy`; it was never exercised.

**Why VMFL051 ran 1,693 steps on a byte-identical `solvers` block and VMFL045 died on
the first — the supervisor's proof, credited:**

| | viscosity | viscous energy corrector | `fvSolution/solvers` energy entry | `smoothSolver: Solving for Ux` lines | outcome |
|---|---|---|---|---|---|
| **VMFL051** | **μ = 0** (inviscid) | **skipped** | `h` only | **0** (entire successful run) | ran — the missing `e` was **latent** |
| **VMFL045** | **μ = 1e-8** (the manual's own, p. 153) | **runs** (μ ≠ 0) | `h` only | **1** (before death) | **crash: no `e`** |

The `0`-versus-`1` count of the implicit `Ux` solve is the reader shown able to see
both states: VMFL045 honouring the manual's stated **nonzero** viscosity exercised the
implicit viscous path VMFL051's `μ = 0` never touched, exposing that the inherited
`fvSolution` is **complete for the inviscid case and incomplete for the viscous one.**

**Why the pre-compute checks could not have caught it, and this is the generalisable
lesson:** the comparator's `--selftest` passed **45/45** and proves the **grader**
(arithmetic, readers, planted-zero controls, Roache states, gate arms) — **not the
case dictionaries**. Nothing in the freeze exercised the actual OpenFOAM solver
dictionary set against the solver. A case cloned from an **inviscid** precedent
silently inherits an `fvSolution` incomplete for the viscous path, latent until a
nonzero viscosity invokes the energy corrector. **The repair is R2 (`R2/`), and the
generalisable fix is a pre-flight smoke test in the launcher** — one timestep on the
coarsest mesh in a scratch directory before the graded levels run (R2 §, launcher).

## 3. The process finding — dispatch on a reading stale by seconds (the supervisor's, recorded plainly)

Two lanes were dispatched on VMFL045 concurrently. The supervisor checked at
`01:35:26Z`, saw no run directory, concluded the first lane was dead, and dispatched
the run-and-grade lane. **That reading was stale by seconds:** the first lane launched
`rhoCentralFoam` at `01:36:45Z` — one second after the run-and-grade lane's own
pre-launch safety check at `01:36:44Z` had also (correctly, at that instant) found the
directory absent. When the run-and-grade lane's launcher started, it **refused with
`LAUNCHER_EXIT=2`** because `L1_90x76` already existed (guard 1). **No second solver
launched into the live run; nothing was corrupted.** The run-and-grade lane created
nothing inside `L1_90x76` (all its files are timestamped `01:36:45Z`, the first lane's).

**The launcher's pre-existing-directory guard is the only reason no corruption
occurred.** This is the same failure class as a **stale git base** — a decision taken
on a reading that a peer moved out from under between the read and the act — in agent
dispatch rather than in a tree. It is recorded here beside the toolchain finding, as
the supervisor directed, because it is the supervisor's finding and not the lanes'.

(One further honesty note: the run-and-grade lane's launch-time `>` rewrite of
`CONTENTION.txt` inadvertently overwrote the first lane's contention samples; those
values are recovered from the first lane's committed report `f1f58fd` and preserved,
attributed, in the current `CONTENTION.txt`. No evidence was lost.)

## 4. Cost and calibration (rule 12)

| item | value |
|---|---|
| predicted (pre-registration §9.1 point estimate) | **20.4 core-min** (cap 48) |
| **actual measured** | **0.0000 core-min** — crash at `wall = 0 s` before any real solve (`RUN_RC.txt`) |
| **ratio actual/predicted** | **UNDEFINED — the run never executed.** Not `0.0×`: **an interruption is not a calibration** (this team's C-10 / C-90 pattern, L-265). There is no throughput to compare, because no solver work happened |
| waste | **0.000 core-min** — the crash *is* the finding and it was free; its log is the evidence the finding rests on (cf. cfd C-4) |
| contention | **not applicable** — no real compute ran, so there is nothing to time against the box's ~2.1–2.9 load (far below VMFL051's 68–76) |
| dollars | **$0.00 derived** at $0.0513/core-h (c7a.4xlarge, owner-stated; **derived, not measured** — the box cannot read its own billing) |

The estimate-versus-actual comparison itself is the deliverable here: it says the
20.4 core-min estimate was **never tested**, because the process did not complete a
solve. Calibration row **`C-<derived at commit>`** in `docs/COST_CALIBRATION.md`.

## 5. What this run does and does not claim

- **Nothing about the physics.** No Mach, temperature or density was measured. The
  gate (|M_lab − 1.874|/1.874 ≤ 1 %), the exact-solution diagnostics and the Roache
  triple are all untouched — carried unchanged into R2.
- **Nothing about Ansys.** This box has no Fluent and no CFX. The frozen
  Fluent-would-fail declaration (Fluent's 1.902 point-sampled would `GATE FAIL` at
  +1.494 %; CFX's 1.871 would pass at −0.160 %) is carried into R2 unchanged; a
  near-Fluent value is a `GATE FAIL` and is not narrated as agreement with Ansys.
- **The freeze is intact, not broken.** All three named blobs and all ten §10 input
  blobs match HEAD; the worktree copies of the prereg, comparator and launcher are
  byte-identical to their HEAD blobs. The `e`/`h` defect was **frozen in** — never
  caught, because §11 confirms no `rhoCentralFoam` ran before the freeze.

## 6. Artifacts (all on disk at HEAD after this commit set)

- Run-1 tree: `verification/runs/ansys_verification/VMFL045/L1_90x76/` —
  `log.blockMesh`, `log.checkMesh`, `log.topoSet`, `log.rhoCentralFoam` (the fatal),
  `RUN_RC.txt` (`rc=1`); run-root `CONTENTION.txt`, `launch.stdout.txt`
  (records the run-and-grade lane's `REFUSE`/`LAUNCHER_EXIT=2`). No time directories,
  no fields. `COST.txt` was never written (the launcher refused before its summary).
- First lane's crash-triage report of record: `cases/ansys_verification/VMFL045/LANE_REPORT.md` (commit `f1f58fd`).
- Frozen pre-registration: `cases/ansys_verification/VMFL045/PREREGISTRATION.md` (blob `7a7f9d52…`).
- Frozen comparator: `cases/ansys_verification/VMFL045/grade_vmfl045.py` (blob `0c83eeef…`).
- Repair: the R2 rung, `cases/ansys_verification/VMFL045/R2/`.

**Verdict vocabulary only** (rule 1): `PASS` / `GATE REACHED` / `GATE FAIL` /
`NOT A RESULT` / `BLOCKED` / `PENDING`. Run 1 is **`NOT A RESULT`**, tier **`NOT
HELD`**, and it is never removed, re-labelled or softened; R2 cites it.
