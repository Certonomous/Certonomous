# VMFL007-R3 — SOLVER-ARM SELECTION RECORD — 2026-09-02

**Written by `ansys-lane-opus` under the supervisor's Task-2 brief. This is a
DIAGNOSTIC record. It is not a pre-registration, it freezes nothing, it grades
nothing and it carries no verdict word. The freeze remains BLOCKED and is the
supervisor's alone.**

---

## 1. The selection rule, fixed BEFORE any candidate ran

The supervisor's brief fixed it and it is absolute:

> **An arm is selected on CONVERGENCE ROBUSTNESS ALONE. No deviation from the
> 60 521.969 Pa closed form may be computed for any candidate arm until AFTER the
> arm has been selected and the selection recorded in writing with its convergence
> evidence.**

**Compliance, stated plainly: no Δp deviation was computed, printed or stored for
any candidate arm at any point before this record was written — and none has been
computed since either (§6).** The screening runner
`cases/ansys_verification/VMFL007-R3/arm_screen.sh` records `rc`, the `End` line,
the iteration count reached and the wall cost, and nothing else; the only Δp
quantity read anywhere in this exercise is the **peak-to-peak of the Δp monitor on
its own tail window**, which is a flatness measure of a series against itself and
contains no reference value.

**A lever that changes the fluid is disqualified.** None was used: every candidate
below leaves `constant/transportProperties` byte-identical to the run-1 physics
input (`k` 0.01, `n` 0.4, `nuMin` 1e-8, `nuMax` 1.0). The candidates differ only in
`system/fvSolution`. `system/fvSchemes` was also left untouched, so no candidate
bought stability with a lower-order `div` scheme.

## 2. The failure being repaired

Arm **A5** (`p` PBiCGStab/DIC, `U` smoothSolver/symGaussSeidel, SIMPLE, `p` 0.3 /
`U` 0.7) converges at 25×25 and **dies at 50×50**. Reproduced here as the screen's
negative control: `rc = 136` (SIGFPE), stopping at **iteration 13274**, against the
2026-08-31 pinning probe's independently recorded "≈ 13 275". The control fires, so
the screen can tell a survivor from a casualty.

## 3. Candidates and outcome — all at 50×50, endTime 30000, serial

| arm | change from A5 | rc | iters reached | `End` | core-min |
|---|---|---|---|---|---|
| **A5** (control) | — | **136** | 13274 | 0 | 1.55 |
| B1 | relax `p` 0.2 / `U` 0.5 | **136** | 15667 | 0 | 1.68 |
| B3 | relax `p` 0.1 / `U` 0.3 | **136** | 20626 | 0 | 2.33 |
| B4 | `U` → PBiCGStab/DILU, `p` relTol 1e-3, `U` 0.5 | **136** | 8086 | 0 | 1.25 |
| **B2** | **SIMPLEC** (`consistent yes`), `p` 1.0 / `U` 0.9 | **0** | **30000** | **1** | 3.00 |

**The finding underneath the table, and it is the useful part:** under-relaxation
alone does not repair this. Halving the relaxation factors (B1) and halving them
again (B3) only **postpone** the blow-up — 13274 → 15667 → 20626 — and a stronger
Krylov solve on `U` (B4) makes it **worse** (8086). The failure is therefore not a
relaxation-magnitude problem and not a linear-solver-quality problem; it is the
SIMPLE velocity-correction inconsistency, which SIMPLEC removes. That also retires
the earlier hypothesis on record — that the negative power-law exponent makes `nu`
singular on the centreline — which had already been refuted at source (`calcNu()`
floors the strain rate at `SMALL` before the `pow` and hard-clips the result, so the
viscosity evaluation is bounded and cannot itself raise the exception).

## 4. THE SELECTION

**Selected arm: `B2` — SIMPLEC.**

```
solvers
{
    p { solver PBiCGStab; preconditioner DIC;  tolerance 1e-12; relTol 0.01; }
    U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-12; relTol 0.1; nSweeps 2; }
}
SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }
relaxationFactors { fields { p 1.0; } equations { U 0.9; } }
```

It is the **only** candidate that reached `endTime` with `rc = 0` at 50×50, and it
then did so at all three levels of the intended triple.

### Convergence evidence for B2, all three levels, endTime 30000, serial

| level | cells | rc | iters | `End` | last `Ux` initial residual | last `p` initial residual | Δp plateau ptp, last 1000 iters |
|---|---|---|---|---|---|---|---|
| 25×25 | 625 | 0 | 30000 | 1 | 2.42e-14 | 4.10e-12 | 7.70e-06 Pa |
| 50×50 | 2500 | 0 | 30000 | 1 | 6.45e-14 | 9.13e-12 | 1.49e-05 Pa |
| 100×100 | 10000 | 0 | 30000 | 1 | 3.07e-09 | 1.47e-08 | 1.66e-03 Pa |

Artifacts: `verification/runs/ansys_verification/VMFL007-R3-DIAG/{L1_25x25_B2,
L2_50x50_B2,L3_100x100_B2}/`.

### 4a. THE QUALIFICATION ON THE SELECTION, AND IT IS NOT SMALL

**At 100×100 the run is robust but it is NOT pointwise converged.** The Δp monitor
is flat to 1.7e-3 Pa, but Δp is a global integral and is insensitive to the axis
cell. The **near-axis viscosity is still oscillating at endTime**:

| level | `max(nu)` at endTime | ptp of `max(nu)` over the last 5000 iters |
|---|---|---|
| 25×25 | 0.0063676 | 3.7e-12 |
| 50×50 | 0.018108 | 4.6e-10 |
| **100×100** | **0.40789** | **0.4269 — about 100 % of its own value** |

At 100×100 `max(nu)` wanders over roughly 0.22 … 0.63 across the tail of the run.
So the correct statement of the selection is: **B2 is the arm that does not diverge
at any of the three levels, and it is iteratively converged to machine precision at
25×25 and 50×50; at 100×100 it reaches `endTime` cleanly with a flat Δp but has not
plateaued pointwise in 30000 iterations.** A graded triple on this arm needs either
a longer 100×100 leg or a `residualControl`/plateau criterion the pre-registration
fixes in advance. That determination is the supervisor's, not this lane's.

## 5. Cost

| item | core-min |
|---|---|
| Task 1 converged 25×25 reproduction (A5, 30000 iters) | 0.80 |
| 50×50 five-arm screen (A5 control + B1 + B2 + B3 + B4) | 9.81 |
| B2 @ 25×25 | 0.87 |
| B2 @ 100×100 | 15.97 |
| **waste** — a 100×100 leg killed at ≈ iteration 16 900 by the lane's own tool timeout, restarted clean | **≈ 10.0** |
| **total** | **≈ 37.45 useful + 10.0 waste = 47.45** |

Against the brief's hard cap of **60 core-min**: **actual/cap = 0.79**. No run was
allowed to overrun the cap. Serial (`ranks = 1`) throughout; the box was carrying
another team's `simpleFoam` (jet-flap) the whole time and was never oversubscribed
by this lane. Dollars, if wanted, are **derived not measured** at the owner-stated
$0.0513/core-h: ≈ $0.041.

## 6. What was deliberately NOT done

**No deviation from 60 521.969 Pa was computed for B2 or for any other arm — not
before the selection and not after it.** The brief permits computing them once the
selection is recorded; this lane declines, and says why: the 100×100 leg is not
pointwise converged (§4a), so any agreement number from this triple would be a
number attached to a state the lab has not yet shown to be a solution. Producing it
now would put an agreement figure into the record for a case whose freeze is
`BLOCKED` and whose gate is not fixed, which is the exact ordering `VERIFICATION
_CHARTER` §2b exists to prevent. The monitors are on disk; the figure is seconds of
work whenever the supervisor wants it, from an artifact whose provenance is this
record.

No pre-registration was frozen, amended or promoted. No register row was written or
graded. No verdict word from the fixed vocabulary was applied to this case.
