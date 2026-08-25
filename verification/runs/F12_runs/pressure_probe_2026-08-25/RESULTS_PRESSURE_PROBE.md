# F12 pressure probe — relaxation is a REAL lever but NOT sufficient, and `transonic yes` is WORSE

**Both arms ran on the real coarse mesh, OUTSIDE the repository**, at
`/home/ubuntu/certonomous-runs/F12_pressure_probe_2026-08-25/`, and outside every
registered run root. `residualControl` was **NOT** loosened — that is a threshold
change and is unavailable post-freeze. **Every residual below is a FIRST-SOLVE
initial residual — the value `simpleControl` reads — never a tail read.**

## 0. The result

| arm | change from rung 1 | rc | iterations | outcome |
| --- | --- | --- | --- | --- |
| **A** | relaxation only: `rho` 0.05→**0.01**, `U` 0.3→**0.15**, `e` 0.5→**0.3**, `(k\|omega)` 0.5→**0.3**, correctors 1→**2** | **134** | **1,803** | `Negative initial temperature T0: -14.40533294` |
| **B** | arm A **+ `transonic yes`** | **136** (SIGFPE) | **1** | **floating-point exception inside the FIRST pressure solve** |

Rung 1, with F12's frozen relaxation, reached **148**.

## 1. Relaxation IS a real lever — and it is NOT enough

**148 → 1,803 iterations is a 12.2× improvement in survival**, from the
relaxation change alone. The supervisor's reading that relaxation explains the
*severity* difference between F2 and F12 is **supported**.

**But arm A still aborts, and `p` never converges.** First-solve `p`:

| iterations | median | min |
| --- | --- | --- |
| 0–200 | 5.7395e-02 | **8.4010e-03** ← the global minimum, at iteration 6 |
| 400–600 | 5.1445e-02 | 3.1402e-02 |
| 800–1000 | 1.0713e-01 | 6.5787e-02 |
| 1200–1400 | 1.3279e-01 | 1.0104e-01 |
| 1600–1803 | 5.9252e-02 | 2.4599e-02 |

**First-solve `p` bottoms at 8.4010e-03 — at iteration 6, in the initial
transient — and never returns there.** Against F12's frozen `residualControl` of
**1e-6**, that is **8,400× too high**. **Iterations with every channel below
1e-6: ZERO of 1,803.**

For scale: F2's `p` bottomed at 1.812e-04. **Arm A's floor is 46× worse than
F2's**, on the same condition and a better mesh.

## 2. `transonic yes` is WORSE, not better — the counterfactual runs the other way

Arm B exited **rc = 136 = 128 + 8 = SIGFPE** after **one** iteration. It logged
**three** solves — `Ux`, `Uy`, `e`, all at initial residual 1.0 — and **ZERO `p`
solves**. The stack puts the fault inside the pressure solve itself:

```
sigFpe::sigHandler  <-  sumProd  <-  PBiCGStab::scalarSolve
                    <-  GAMGSolver::solveCoarsestLevel  <-  Vcycle
                    <-  GAMGSolver::solve  <-  fvMatrix<double>::solveSegregated
```

**The transonic branch's very first pressure matrix is already non-finite**, from
the uniform initial field, before a single `p` solve completes. The switch was
verified applied (`transonic       yes;` at line 37 of the arm's own
`fvSolution`, copied beside this record).

**What this establishes:** `transonic yes`, added as a **naked switch** to this
case with this initial field, produces a non-finite pressure matrix on the first
solve. **What it does NOT establish:** that `transonic` is wrong for this case.
It may need a developed initial field, a different `p` boundary condition, or a
ramped start. **That is crash triage and crash triage is the supervisor's**; this
record does not do it.

## 3. Against the supervisor's own decision rule, stated in advance

| forecast branch | outcome |
| --- | --- |
| arm A survives **and** `p` bottoms near or below 1e-6 → **fire attempt 3 as planned** | **NO.** Arm A aborted at 1,803; `p` bottomed 8,400× high. |
| arm A survives, `p` floors high, **arm B reaches it** → `transonic` demonstrated by counterfactual | **NO.** Arm B crashed at iteration 1 with zero `p` solves. |
| neither reaches it → gate B fails on a stable run | **CLOSEST, AND WORSE: neither arm is stable at all.** |

**Attempt 3 as scoped would not merely fail gate B — it would ABORT**, at roughly
iteration 1,800 instead of 148. **The probe has saved a registered attempt and a
120 core-min cap for 4.0 core-min.**

## 4. Cost

| | value |
| --- | --- |
| registered before the probe | **6 core-min per arm, 12 total**, enforced by `timeout` |
| **actual** | **4.0 core-min** — arm A 220 s, arm B 20 s, ranks 1 |
| cap breached | **no** (arm A used 3.67 of its 6) |
| waste, named separately | **0.00 core-min** — both arms answered their question, including the one that crashed |
| loadavg, in every sample | 5.01 → 6.01 over arm A's 11 samples |
| dollars | **$0.0034, DERIVED at $0.0513/core-h, reported-by-owner, never measured** |

## 5. The registered roots were untouched, asserted before AND after

`rung1_fingerprint_before.txt` and `rung1_fingerprint_after.txt` are equal — the
fired rung-1 directory is byte-unchanged. Rungs 2–5 asserted absent before and
confirmed absent after. No gate, threshold, cap or label was touched. The probe's
own builder **refuses** if any intended `fvSolution` edit fails to apply, and
asserts `residualControl` still reads `1e-06` — a silently-unapplied edit would
otherwise have made arm A a re-run of rung 1 wearing arm A's name.

---

## 6. ADDENDUM 2026-08-25 — ARM B′, AND A STRUCK MECHANISM ON BOTH SIDES

### 6.1 The supervisor's cause for arm B is FALSIFIED FROM SOURCE

The triage handed to this lane was: *"`fvm::div` makes the pressure matrix
ASYMMETRIC … GAMG in OpenFOAM is a symmetric-matrix solver."* **That is not true
of OpenFOAM 2606 on this box.** `GAMGSolver.C` registers **both** tables:

```
src/OpenFOAM/matrices/lduMatrix/solvers/GAMG/GAMGSolver.C
  :40   lduMatrix::solver::addsymMatrixConstructorToTable<GAMGSolver>
  :43   lduMatrix::solver::addasymMatrixConstructorToTable<GAMGSolver>
```

The `GaussSeidel` **smoother** is likewise registered for both
(`GaussSeidelSmoother.C:38,41`). And a solver that is *not* registered for a
matrix type raises a **`FatalIOError` at selection time** — *"Unknown asymmetric
matrix solver"* — **not a SIGFPE deep inside `GAMGSolver::solveCoarsestLevel`.**
Arm B's own traceback is therefore inconsistent with the proposed cause.

**Both readings of arm B are struck:** this lane's *"the first pressure matrix is
already non-finite from the uniform initial field"* (never demonstrated) and the
supervisor's *"GAMG cannot represent the matrix"* (falsified above). **What arm B
established is narrower than either: GAMG, on the asymmetric matrix the transonic
branch produces for this case, failed with a floating-point exception in its
coarsest-level solve.** Why it did is not established here.

### 6.2 The prescription was right even though the mechanism was wrong

**Arm B′** — arm B with `p` moved from `GAMG`/`GaussSeidel` to
`PBiCGStab`/`DILU`, the solver this case already uses for `U`, `k`, `omega` and
`e`; one change from arm B, nothing else touched, `residualControl` untouched.

| arm | `p` solver | rc | iterations | `p` solves | died on |
| --- | --- | --- | --- | --- | --- |
| A | GAMG (no `transonic`) | 134 | **1,803** | 3,606 | `Negative initial temperature T0: −14.4053` |
| B | GAMG + `transonic` | 136 | 1 | **0** | SIGFPE inside the first `p` solve |
| **B′** | **PBiCGStab + `transonic`** | 134 | **3** | **6** | **`Negative initial temperature T0: −259152.9888`** |

**The solver swap worked**: `p` now solves — 72, 90, 52, 1, 50, 50 inner
iterations — where arm B logged none. So GAMG *was* the obstacle to getting past
the first pressure solve, and the supervisor's prescription was the right
experiment on a wrong rationale.

### 6.3 AND THE COUNTERFACTUAL IS NEGATIVE FOR `transonic`

With the pressure equation actually solving, `transonic yes` makes this case
**dramatically worse, not better**:

- arm A reaches **1,803** iterations and fails at **T = −14.4**;
- arm B′ reaches **3** iterations and fails at **T = −259,152.99**.

That is **600× fewer iterations and an 18,000× larger excursion.** The energy
residual never moves: `e` reads 1.0000, 0.99476, 0.99384 on the three iterations.

**The missing `transonic` flag is REFUTED as the cause of F12's pathology, by the
counterfactual the supervisor designed.** It is not an untested switch any more.

**A consequence the supervisor named in advance, and it is confirmed as
relevant:** `rho.relax()` fires **only** in the non-transonic branch
(`pEqn.H:107`), so enabling `transonic` silently retires the `rho` relaxation
factor — the very lever that bought arm A its 12.2× survival. The two are **not
independent**, and arm B′ is what that looks like when they are changed together.

### 6.4 Still open, and NOT answered by any arm

Where first-solve `p` floors on a **stable** run remains unmeasured, because
**no arm has been stable.** Arm A's floor of **8.4010e-03** is the floor of a run
that aborts, not of a converged one. `roache_triple` pins remain owed.

### 6.5 Cost

Arm B′: **0.333 core-min** (20 wall s, ranks 1) against the 6 core-min registered
per arm; cap not breached; waste **0.00** — it answered its question. Probe total
across all three arms: **4.33 core-min** of 18 registered. Dollars **$0.00037**,
DERIVED at \$0.0513/core-h, reported-by-owner, never measured. `rung1_fp_before_Bprime.txt`
and `rung1_fp_after_Bprime.txt` are equal — rung 1 byte-unchanged; rungs 2–5
asserted absent before and confirmed absent after.

### 6.6 The interim log policy is applied from here

`scripts/extract_residual_series.py` emits the **first-solve** residual series as
CSV — the first-class artifact records cite — and the raw log is gzipped beside
it. The extractor is self-checked against the discrepancy that started this: on
F2 it returns **4.2657e-04** for the final-iteration `p`, matching the hand
analysis, where a tail read gives 3.2756e-06. Arm B′'s raw log is gzipped (12K →
4.0K); series extracted for arms A, B and B′. **Arm A's already-committed 3.4 MB
log is left exactly as it is**, per the policy's own do-not-rewrite clause.
