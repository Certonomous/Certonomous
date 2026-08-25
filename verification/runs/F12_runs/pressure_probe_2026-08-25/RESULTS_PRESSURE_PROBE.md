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
