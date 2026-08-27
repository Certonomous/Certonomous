# K2b-U3 — the 3D unsteadiness check: OUTCOME P3, declared by its own registered gate

**Written 2026-08-27 by a heat-transfer lane on the supervisor's dispatch;
decisions `[lab-attributed]`. Zero new compute — the compute this record grades
was already on disk and the frozen comparator was run READ-ONLY.** Verdict
vocabulary fixed by `CLAUDE.md` rule 1. **Nothing here has been sent, filed,
submitted, uploaded, registered or posted outside this box (`CLAUDE.md` rule 7).**

## 1. The verdict

> **OUTCOME P3 — UNDECIDABLE AT THIS PRICE.**
> **The 3D question is `NOT A RESULT`: Test D was never run and no 3D verdict is
> claimed.**
> **Control M itself is a real reading and it says `DAMPS`.**

This is the outcome `K2b_3D_UNSTEADINESS_PREREGISTRATION.md` §4 fixed **before**
either run, in its own words:

> *"**Control M shows it damping** → mesh and dimensionality are confounded at
> this price and **Test D cannot answer the question**. Outcome **P3**, declared
> without running Test D, with the cost of the un-confounded experiment stated."*
> — §2

> *"**P3 — UNDECIDABLE AT THIS PRICE.** Control M fails, or the aliasing guard of
> §3.1 fails, or Test D reads UNDECIDABLE. → **Stated as the answer, not resolved
> by preference.**"* — §4

**The rung had therefore already closed itself, and the outcome was recorded
nowhere.** This document is that record. It changes no threshold, no gate and no
outcome definition: every number below was fixed before the run and is read back
out of the frozen comparator.

## 2. What was measured, and where

`verification/runs/F14-cooling-ladder/K2b_runs/analyse_k2bU3.py`, the comparator
frozen against `K2b_3D_UNSTEADINESS_PREREGISTRATION.md` (sha256 `91a26fc9…`), was
run **read-only** on 2026-08-27 and returned **rc 0**, leaving the run tree
byte-unchanged (`git status --porcelain` on `K2b_runs` is empty after the run).
It printed:

| reading | value | registered threshold | verdict |
|---|---|---|---|
| Control M, final window **60–80 s**, peak-to-peak of `weightedAverage(rack_in) of T` | **0.7792 K** (mean 296.0933 K) | `≤ 0.10 K` → DAMPS | not by p2p |
| Control M, preceding window **40–60 s**, peak-to-peak | **1.6156 K** | — | — |
| **ratio final / preceding** | **0.482** | **`≤ 0.5` → DAMPS** | **DAMPS** |
| aliasing guard, steps per period | **34.4** | floor **20** | **passes** |
| aliasing guard, samples per period | **29.9** | floor **10** | **passes** |
| dominant period after the 40 s discard | **none extracted** | the 2D limit cycle was **6.000 s** | — |

**The aliasing guard passing is what makes this a reading rather than a
non-detection.** §3.1 of the pre-registration registers the guard precisely so
that "no oscillation seen" cannot be reported when the sampling could not have
seen one; here it could have, at 34.4 steps and 29.9 samples per the 6.000 s
period the 2D slice showed, and it did not. The ratio 0.482 sits **below** the
registered DAMPS threshold of 0.5, so the DAMPS reading is not a marginal call
on the p2p (0.7792 K is between the two p2p thresholds and decides nothing by
itself) — **it is decided by the ratio, and the ratio is the arm that fired.**

**The case behind the numbers.** `K2bU3_M`: the 2D `y`–`z` slice, one rack pitch,
3.5 m × 2.7 m, **100 mm cells, 725 cells**, `buoyantBoussinesqPimpleFoam` (`Exec`
line of `log.buoyantBoussinesqPimpleFoam`; Euler `ddt`), 70 % provisioning,
**459 time steps to t = 80.00 s**, mean `dt` 0.1743 s, one monitored face.

**One infrastructure discrepancy, disclosed and not load-bearing:**
`K2bU3_M/CASE.txt` line 8 reads `solver buoyantBoussinesqSimpleFoam`, which is
the builder's template header and is **wrong about what ran**. The
`system/controlDict` says `application buoyantBoussinesqPimpleFoam`, the log's
`Exec` line says `buoyantBoussinesqPimpleFoam`, and the `ddtSchemes` default is
`Euler` — the transient solver the pre-registration registers. This is a
**bookkeeping defect in a metadata file, not a physics finding** (L-342, Sanaa's
universal rule `d4d0c29d`: a bookkeeping failure invalidates the bookkeeping,
never the physics artifacts). It is stated here so no later reader takes
`CASE.txt` as evidence of a steady run.

## 3. What this closes, and what it explicitly does NOT

**Closed.** The 3D unsteadiness question is not answerable at 100 mm, because a
3D run at 100 mm could not separate three-dimensionality from mesh coarsening —
and Control M has now shown that coarsening **alone**, in 2D, damps the mode. The
`K2bU3_D` case is therefore **not run and must not be run at this resolution**;
its tree holds `0.orig/`, `CASE.txt`, `constant/`, `system/` and no compute.

**NOT closed, and not retracted.** K2b's pilot outcome **O1 — PHYSICALLY
UNSTEADY**, the 6.0 s limit cycle of ≈1.1 K at 12.5 mm in 2D
(`K2b_PILOT_RESULTS.md:883`, `:1501-1507`), **stands exactly as it stood.** This
record says nothing against it: Control M is a *different mesh*, and the whole
point of the gate is that a null at 100 mm cannot speak about 12.5 mm. Under §4's
own reading of P3 the 3D module **stays held** and the K2a §9 steady estimate
**stays void**.

**The un-confounded experiment, named by the registration and not by this lane:**
a 3D transient at the spec's own **60 mm** coarse mesh for **80 s**,
**≈ 42 core-minutes** at the rung's measured transient rate of
`4.26e4 cell·steps/(core·s)` (`K2b_3D_UNSTEADINESS_PREREGISTRATION.md` §4). It is
**not** proposed, scheduled or enqueued here.

## 4. Cost, and the rule-12 estimate-versus-actual comparison

| | registered estimate | actual | ratio | attribution |
|---|---|---|---|---|
| Control M | **≈ 0.2 core-min** (§2, "Control M costs ~0.2 core-minutes") | **0.0397 core-min** — `ExecutionTime = 2.38 s`, serial, from `K2bU3_M/log.buoyantBoussinesqPimpleFoam` | **0.198×** | **misprediction, conservative direction.** 725 cells is far inside the overhead-dominated regime C-118 names, where linear cell-step scaling over-predicts; no contention explanation is needed and contention could only have pushed the other way |
| Test D | ≈ 42 core-min at 60 mm (the un-confounded experiment) | **0 — not run** | — | the registered gate fired first, exactly as designed |
| this record | — | **0 core-min** | — | the comparator was run read-only on compute already on disk |

**USD: 0.0397 core-min = 6.6e-4 core-h = $3.4e-05 — DERIVED, NOT MEASURED**
(owner-stated $0.0513/core-h; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). A `docs/COST_CALIBRATION.md` row is owed for
this completion and is the supervisor's to land under that file's append rules.

## 5. What a reader must not take from this

- **Not a statement that the 2D limit cycle was an artefact.** It is a statement
  that a 100 mm 2D slice does not sustain it, which is what the gate was built to
  ask.
- **Not a 3D verdict of any kind.** No 3D case has been graded on this ladder.
- **Not a licence to revive the K2a §9 steady estimate.** §4's P3 branch holds it
  void, and only P2 — which required Control M to *pass* — would have made it
  revivable, and even then "revivable but not revived".
