# MRF R4 — GRADED. VERDICT: `NOT A RESULT`

**Graded 2026-09-14 by a cfd `lab-lane`, on the supervisor's dispatch.** Written here, beside
the run, so that nobody re-derives it. **Row:** `MRF_R4_GRADED_ROW.json` (this directory) —
the frozen comparator's own output, unedited.

> **SINGLE GRID — NO GRID-CONVERGENCE CLAIM.**

**Full path of the graded level, given in full because two MRF trees share zone names and
differ in cell count:** `verification/runs/navier_class/MRF/R4/fine` — **3,641,246 cells**
(`log.checkMesh`, line `cells: 3641246`). It is **not** `…/MRF/fine` (394,039) and **not**
`…/MRF/R2/fine` (871,880).

---

## 1. THERE IS NO ROACHE TRIPLE TO LOOK FOR, AND THAT IS REGISTERED, NOT MISSING

`MRF_R4_PREREGISTRATION.md` §2 **drops the three-level family by Sanaa's ruling of
2026-09-12**, and §2.1 registers the consequence before the run: **`PASS` is not claimable by
this rung**, because rule 5 reserves `PASS` for a `CONVERGING` triple. The available verdicts
were fixed in advance as `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

**So `R4/fine` being the only level on disk is not a gap. One level is the registered design.**
No level is owed, none is costed, and no GCI is quotable or quoted. The gate is an **external
experimental reference**, not a grid family: Beshay et al., *Acta Polytechnica* 41(6) 2001,
`Po = 5.41` measured by strain-gauge torquemeter; band **`Np ∈ [5.29, 5.53]`**, envelope
`[4.54, 6.28]` reported and never gated.

## 2. COMPLETION — RULE 4, CLAUSE BY CLAUSE, EACH WITH THE ARTIFACT IT WAS READ FROM

All artifacts under `verification/runs/navier_class/MRF/R4/fine/`.

| clause | artifact | reading | holds |
|---|---|---|---|
| `rc == 0`, from the sidecar written inside the detached wrapper | `RC.txt` (and `rc`) | `0` | ✔ |
| an `End` line | `log.simpleFoam` | exactly one `End`, followed by `Finalising parallel run` | ✔ |
| last written time == `endTime` | time dirs `0`, `8000`; `system/controlDict` | `endTime 8000`; highest time dir `8000` | ✔ |
| `ExecutionTime` count == `round(endTime/deltaT)` | `log.simpleFoam`, `system/controlDict` | `deltaT 1`; **8000** `ExecutionTime` lines == 8000 | ✔ |
| fields present at `endTime` | `8000/` | `U p phi k omega nut` all present | ✔ |
| **age guard** — every field at `endTime` newer than the case's own `0/` | `stat` mtimes | oldest `8000/` field **1789286366**, newest `0/` reference **1789249667**; margin **+36,699 s** | ✔ |

**Completion holds on every clause.** The comparator reproduced all six independently
(`MRF_R4_GRADED_ROW.json`, `completion` block, each clause its own boolean).

**A note on `0.snappyLevels/`, so no reader meets it cold.** `AGE_GUARD_NOTE.md` in the run
directory records that snappy's `cellLevel`/`pointLevel` bookkeeping directory was **renamed,
not deleted**, and that `launch_graded.sh:101` re-stages `0/` from `0.orig/` immediately before
the solve — which is exactly why `0/` dates the run. The age guard above is measured against
that re-staged `0/`, i.e. against the intended reference.

## 3. THE FREEZE, AND THE PROOF THE GRADED PATH DID NOT DRIFT

| item | value |
|---|---|
| registration | `verification/campaign/MRF_R4_PREREGISTRATION.md` |
| registration blob frozen at §11.1 | `fa0069709d19511e601aeb20a9694d7c3b6353c3` |
| freeze commit | `2e50cfcb56cc4a947faef7fb8fe6f5c136f78024`, 2026-09-12T20:18:24Z |
| banner struck in place (rule 6, no line numbers moved) | `62a6f58bd50558bf5273476474714cbfbdc103c1`, 20:41:26Z |
| **grading path, pinned at the freeze** | `cases/navier_class/MRF/R4/grade_mrf_r4.py` |
| frozen blob | `2b8b367d7d6e7cb82d5b87eb0367dae1b5231067` |
| blob at HEAD, and on disk at grading time | `2b8b367d7d6e7cb82d5b87eb0367dae1b5231067` — **IDENTICAL** |
| sha256 of the file that actually ran | `e0ee0ea2be0dcbaf6309fe7011f263748601b81a556643ae6e96663d15fd607d` |

The comparator was **committed 2026-09-12T19:55:09Z at `6957b10ec254281ae547da83e761460e4eb2375d`
— before the freeze (20:18:24Z) and before first compute (solve start 21:48:35Z,
`SOLVE_START_UTC.txt`).** Rule 2's hash check therefore has a referent and it matches.
**The comparator was run unmodified. Nothing in it was edited, before or after.**

## 4. THE INSTRUMENT WAS SHOWN ABLE TO REFUSE (RULE 3)

A grade from an instrument not shown able to say no is not evidence. Three controls, all on the
**unmodified** file:

| control | result |
|---|---|
| **planted zero, on the graded run** — `PLANT = 1.234e-03` N·m into a copy of `moment.dat`, read back through the same reader | expected ΔNp `3.107595458540925e-02`, **seen `3.107595458540402e-02`** — the reader **sees** the perturbation |
| **negative control A** — the same plant made invisible (col-3 torque set to `1e10`, so the plant rounds away) | `REFUSING: PLANTED-ZERO CONTROL FAILED — the reader cannot see a known perturbation`, **exit 2** |
| **negative control B** — `RANKS.txt` = 4 against the registered 6 (§6) | `NOT A RESULT`, "a run at any other rank count is not this registration's run" |

Both negative controls were built as **copies in scratch**; the graded run directory was not
altered, and the comparator's own transient probe file was removed by the script.

## 5. THE VERDICT

> # `NOT A RESULT`
> **SINGLE GRID — NO GRID-CONVERGENCE CLAIM.**
> `Np = 5.1136` (final iteration), window mean `5.1233` — **quoted only as the value the
> refused row carries, never as a measurement.** Rule 5's discipline applies with equal force to
> a refused iterative criterion: a number inside a row that is not a result is not a result.

**All four iterative-convergence limbs refuse** (`MRF_R4_PREREGISTRATION.md` §5; a level is
converged only if IC-1 ∧ IC-2 ∧ IC-3 ∧ IC-4):

| limb | registered requirement | measured | |
|---|---|---|---|
| **IC-1** bounding quiescence, absolute pinned left edge at 2000 | **zero** events at `i > 2000` | **eight**: `2352, 3085, 3358, 3845, 4793, 4839, 4872, 7274` | ✗ |
| **IC-2** no NaN, no FPE | none | `nan` false; `fpe` **true** — **see §6, this limb's reading is unsound** | ✗ (unsound) |
| **IC-3** final initial residuals `Ux,Uy,Uz,k,omega ≤ 1e-5` | ≤ 1e-5 | `Ux 1.724e-2`, `Uy 1.638e-2`, `Uz 1.534e-2`, `k 6.151e-3`, `omega 1.420e-3` — **three orders of magnitude out** | ✗ |
| | cumulative continuity ≤ 1e-6 | `5.325e-15` | ✔ |
| **IC-4** stationarity over the last 2000 iterations | excursion ≤ 0.5 %, drift ≤ 0.2 % | excursion **4.92 %**, drift **0.86 %** | ✗ |

**IC-1 is monotone by construction** — its window's left edge is pinned at 2000 and only the
right edge grows — so this row **cannot be rescued by a longer run on the same events**, and
§5 forecloses extending `endTime` to chase a limb. The physics reading is plain and is not
softened: **at `t/D = 0.0155` the fine level had not settled at 8,000 iterations.** `Np` was
still drifting at ~0.86 % across the last 2,000.

**IC-1's event list was independently re-read from the log before the comparator was run** and
matches the comparator exactly. It is **eight** events, not four; a four-event figure circulating
on the session board undercounted by missing `4793, 4839, 4872, 7274`. Recorded so the larger
figure is the one that survives.

## 6. AN INSTRUMENT DEFECT IN THE FROZEN COMPARATOR — DISCLOSED, NOT PATCHED, AND HERE IT CHANGES NOTHING

`grade_mrf_r4.py:97` reads `("Floating point exception" in t)` over the whole log. **Every
OpenFOAM log prints `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).` in its
header** — confirmed in this run's `log.simpleFoam` at **line 29, and it is the only occurrence
in the file**. `IC2` therefore reports `fpe = true` on **any** run, sound or not, so
**`GATE REACHED` and `GATE FAIL` are unreachable through this comparator.** The companion
`split("floating")[0]` on line 96 also truncates the NaN search at that same header line, so a
real NaN later in the run would be invisible to the `nan` limb.

**This is not patched here and must not be.** The file is the frozen graded path (rule 2, rule 6);
an instrument edited toward a wanted answer is worthless. It is **referred to the verification
supervisor for a `VERIFICATION_CHARTER` §2d.1 ruling**, which is the only route that can touch a
frozen comparator.

**The defect does not decide this row, and the row does not depend on it.** Strike IC-2 out
entirely and **IC-1, IC-3 and IC-4 — none of which touches that code path — still refuse
independently**, each by a wide margin. The verdict is `NOT A RESULT` with or without the
defective limb. What the defect costs the lab is the *ability to reach a band verdict at all* on
a future R4-family run; it costs this row nothing.

## 7. COST — ESTIMATE VERSUS ACTUAL (rule 12)

| | core-min | source |
|---|---|---|
| registered at the queue entry | **6,275.1** | `verification/queue/LAUNCH_LOG.tsv:448` (the §11.4 re-derivation from the built mesh) |
| registered in the frozen §9 (whole rung, incl. build + post) | **8,130** | `MRF_R4_PREREGISTRATION.md` §9 |
| registered cap | **24,400** | `MRF_R4_PREREGISTRATION.md` §9 |
| **actual, solve** | **3,663.70** | `verification/runs/navier_class/MRF/R4/fine/CORE_MINUTES.txt` (36,637 wall s × 6 ranks ÷ 60; solver's own clock `ExecutionTime = 36585.27 s` ⇒ 3,658.53) |
| **actual, mesh build** | **22.28** | `verification/runs/navier_class/MRF/R4/WALL_SECONDS.build` = 1,337 s, serial basis, as §11.2 reads it |
| **actual, total** | **3,685.98** | sum of the two above |

- **ratio, solve vs queue-registered: 0.5838.** **ratio, total vs frozen §9: 0.4534.**
- **The cap was never approached** (15.1 % of 24,400), so no cap clause fires.
- **Attribution: misprediction of solver rate, in the conservative direction.** The registered
  6,275.1 was built on **7.735 s/iteration**, measured early in the run; the run actually averaged
  **4.58 s/iteration** (36,637 s ÷ 8,000). The early-iteration rate is not the run's rate, and that
  is the transferable lesson for the next MRF estimate. **Not contention and not waste.**
- **The §9 meshing term remains an 11× over-estimate** (250 registered against 22.28 measured) —
  the supervisor already recorded this at §11.4 and it is carried here unchanged.
- **No waste row.** Every core-minute spent produced field and force data the comparator read;
  the `NOT A RESULT` is a **physics** verdict about convergence, not lost measurement, and is
  not laundered into the ratio. The one queue refusal (2026-09-12T20:41:01Z, `writeInterval`)
  consumed no compute.
- **No cleaning applied, and the reason is stated rather than assumed:** the charter §2 3,600-s
  stall rule matches *ledger rows*; this rung is one continuous 36,637-s solver run, not a sweep,
  so gross and cleaned are the same figure here. That is this lane's reading, flagged as such.
- Dollars **derived, not measured** — the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5): 3,685.98 core-min = 61.433 core-h × $0.0513/core-h =
  **$3.1515 derived**, reported-by-owner rate.

## 8. WHAT THIS ROW DOES NOT SAY

- **It does not vindicate or condemn the thickness mechanism.** `5.1136` sits inside the
  reported `[4.54, 6.28]` envelope and below the `[5.29, 5.53]` band, but **the row is not a
  result**, so neither reading is available. §4.4 of the registration already forecloses the
  symmetric move for R2.
- **It makes no grid-convergence claim**, has no triple, and quotes no GCI.
- **It does not rehabilitate R2's `4.382`**, which stays inside its own `NOT A RESULT` row.
- **It is not a `PENDING`.** Nothing here is waiting on a level that has not run: the rung is
  single-grid by ruling, it ran, it was graded, and the graded answer is a refusal.
- Submissions parked (rule 7). Nothing filed, sent or uploaded.
