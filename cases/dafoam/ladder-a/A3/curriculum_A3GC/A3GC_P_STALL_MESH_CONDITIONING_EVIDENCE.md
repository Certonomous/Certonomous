# A3GC — THE p-STALL IS MESH CONDITIONING, NOT SOLVER SETTINGS, NOT THE CASE

**Evidence note by a dafoam lane, 2026-09-12T03:0xZ. NOT a pre-registration. Freezes nothing,
authorises no launch, no commit, no send. Read-only on both live runs. ZERO compute spent.**
**SUBMISSIONS PARKED.**

**Filed here and not in the R2 draft because a sibling lane owns that draft and overwrote it at
03:07:01Z while this lane was writing** (see §5). Nothing of theirs was reverted.

---

## 1. THE MEASUREMENT

| level | cells | max aspect ratio | max non-orthogonality | small-determinant cells | p plateau (initRes) | GAMG iters/step | final/initial ratio |
|---|---|---|---|---|---|---|---|
| validated 399k anchor | 399,360 | not measured (no checkMesh in archive) | — | — | **3.744e-07** | **2** | 0.084 |
| **A3GC L3** | 99,840 | **222.35** | **61.16°** | 18,471 (18.5 %) | **2.290e-05** | **2** | 0.0324–0.0347 |
| **A3GC L2** | 798,720 | **792.38** | **72.07°** | 110,979 (13.9 %) | **1.035e-03** | **15–17** | 0.0913–0.09999 |

Sources: `A3GC-L3/meshgen/logCheckMesh.txt`, `A3GC-L2/meshgen/logCheckMesh.txt`;
every `GAMG:  Solving for p` line in each `primal.log` (6,000 steps L3, 781 steps L2), last-200
window; anchor from `cases/dafoam/ladder-a/logs_A3/run_model_run3.log:1590`.

## 2. THE CONTROL THAT NAMES THE VARIABLE — AND RULES OUT fvSolution

**All three runs use a BYTE-IDENTICAL `system/fvSolution`:**

    SIMPLE { nNonOrthogonalCorrectors 0; }
    "(p|p_rgh|G)" { solver GAMG; smoother GaussSeidel; relTol 0.1; tolerance 0; }
    relaxationFactors { fields { "(p|rho)" 1.0; } equations { p 1.0; ... 0.80; } }

Verified at `A3GC-L3/system/fvSolution`, `A3GC-L2/system/fvSolution` and
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/system/fvSolution:20,28,30,31,57`.

**THE SETTINGS ARE NOT THE VARIABLE. THEY CANNOT BE — THEY DO NOT DIFFER.** The validated
399,360-cell primal reaches **p initRes 3.744e-07 at 4x MORE cells than L3**, on the **same c2
surface**, with **this same fvSolution**. It differs from L3 in exactly one registered way: 64
wall-normal layers instead of 16, at the same `s0` and `marchDist`.

**A converged primal on this geometry exists. The stall belongs to the A3GC MESH RECIPE.**

*Honest correction, made by this lane before reporting:* an earlier draft of this note read L2's
`relTol 0.1` termination as a cause. **It is not a cause — it is the same default under which the
anchor converged.** It is a **default the A3GC meshes have outgrown**, and it is demoted here from
cause to symptom. The relTol reading itself stands as a measurement: **L2's pressure solve
terminates on `relTol 0.1` in 103 of its last 200 steps** (median ratio 0.0952, max 0.09999 — the
target hit to four digits), while **L3 is relTol-limited in 0 of 200**. The reader that reports
103/200 on L2 reports 0/200 on L3, so the non-zero control is live and the L2 reading is real
(rule 3).

## 3. WHY CONDITIONING DEGRADES WITH REFINEMENT — and it is the registration's own disclosed choice

A3GC §2.6 holds **`s0 = 1.0e-4` fixed on every level** while the surface is refined 4x in faces per
level. Δx and Δz halve; the first-cell height does not. **Near-wall aspect ratio therefore grows by
the refinement ratio at every level, by construction.** Measured: 222 → 792 (**3.56x**) with
non-orthogonality 61.2° → **72.07°**, past OpenFOAM's 70° threshold, against
`nNonOrthogonalCorrectors 0`.

§2.6 disclosed the fixed `s0` and named its consequence as a y+ / observed-order caveat. **It did
not predict that it makes the pressure equation harder to converge at every refinement step.** That
is what the two checkMesh logs measure. Projected L1: max AR ≈ 3,170, non-orthogonality above 75°.

**[lab-attributed] inference, labelled as such:** the outer p residual plateaus where the
never-iterated non-orthogonal correction balances the inner solve's one-decade reduction. **The
lever set is `nNonOrthogonalCorrectors`, the p linear `tolerance`/`relTol`, and the `s0`-versus-
refinement coupling.** All three are mesh/numerics choices inside supervisor authority
(`CASE_PROTOCOL_CHARTER` §9). A sibling lane owns the root cause; this is evidence offered to it.

## 4. CROSS-ITEM CORROBORATION — A2 ALREADY MEASURED THIS LEVER SET ON A 3D WING

`cases/dafoam/ladder-a/A2/curriculum_D6RF10/D6RF10_GRADE_RECORD.md`; grader `d6rf10_grade.py`
md5 `0cb9d89a11347bc943acf3b38e1766d2` = HEAD blob; both planted controls EXERCISED-PASS.

| rung | configuration | binding `p_first_uncorrected` vs 1.0e-05 floor | verdict |
|---|---|---|---|
| R1 | `DARhoSimpleFoam`, **nNonOrth 3**, relax_p 0.30, endTime 2500 | 1.681e-05 = **1.681x above** | `GATE FAIL` |
| R2 | `DARhoSimpleFoam`, **nNonOrth 12**, relax_p 0.30, endTime 300 | died at Time ≈ 292–299 of 300, `rc=124`, deadline 4 % short | `NOT A RESULT` |
| **R3** | **SIMPLEC, nNonOrth 12, relax_p 0.70**, endTime 2000 | **BELOW the floor, with a MEASURED plateau** | binding `PASS`; rung `GATE FAIL` on nuTilda 1.392x |

Whole graded ladder **759.667 core-min**, hard stop 1275.

**A3GC runs SIMPLEC with `nNonOrth 0` and p relaxation 1.0** — the solver name from A2's winning
rung and **neither of its other two components** — on a mesh at **72.07°**, against A2's R1 which
`GATE FAIL`ed at nNonOrth 3. And **A2 measured the "run longer" lever (R1, endTime 2500) and
CONFIRMED IT INSUFFICIENT**; A3GC's registered endTime 6000 is that same lever.

## 5. TWO OBJECTIONS TO THE SIBLING R2 DRAFT — measured, and offered before it is frozen

`A3GC_R2_PREREGISTRATION.md.DRAFT` (03:07:01Z) registers `c3`/`c2`/`c1` x N=33 →
49,920 / 199,680 / 798,720, r = 1.4006.

1. **Its coarse level is `c3`, which A3GC §2.4 measured as a DIFFERENT DISCRETE BODY.** TE thickness
   **0.0** at root and tip against c0/c1/c2's 6.888e-04; bbox y ±0.039320 against ±0.039426; the mid
   strip empty. §2.4's registered reasoning is that a coarsest level closing a TE the finest resolves
   means the levels are not the same body and **the triple is dead**. The draft's §1.2 cites §2.3
   (the coarsening *chain limit*) and its corroboration is that c3 is **solvable** — a different
   question from body identity, which §2.4 decided against c3 before any solve.
2. **Its finest level is the level that is stalling right now.** The draft states R2-L1 is
   dimensionally identical to the running A3GC L2 (`c1`, N=33, 798,720 cells). That mesh measures
   max AR 792, non-orth 72.07°, and its p residual is **1.0145e-03 and RISING** over steps 700–781.
   Holding `s0` and `N` fixed while refining the surface is the same fixed-`s0` coupling as §3 above:
   **AR doubles at every level of this family too.**

**Neither objection is a ruling.** Both are measurements handed to the supervisor before a freeze.

---

## 6. SURVIVING MEASUREMENT — endTime, from L3's own completed log

`A3GC-L3/primal.log`, `printInterval 100`, 61 samples, rc=0 to endTime 6000.

**CD is within 0.005 % of its endTime value from step 500 onward** — |CD(t) − CD(6000)| ≤ 1.3e-06
for every t ≥ 500. CD(400)=0.02978667 (+0.023 %), CD(500)=0.02977932 (−0.0016 %),
CD(6000)=0.02977980.

`G-PLAT`'s own statistic (AMENDMENT 1(a): peak-to-peak over the last 10 printed samples), rolling:

| window end | CD p2p | CL p2p |
|---|---|---|
| 1200 | 1.867e-04 | 5.744e-05 |
| **1300** | **7.836e-06** | 5.744e-05 |
| **1400** | 2.261e-06 | **7.503e-06** |
| 1500 | 2.261e-06 | 1.444e-06 |
| 6000 | 1.885e-06 | 1.683e-06 |

Bar = 0.1 x min level-to-level difference (AMENDMENT 2(c)); commit `5a05eda76` expects that
difference at 1e-03…7e-03 → bar **1.2e-04…7e-04**. **CD clears from window-end 1300, CL from 1400**,
and the statistic is only ~4x better at 6000 than at 1300 against a bar two decades away.
**Steps 1400–6000 bought no measurable change in either graded functional — 77 % of every level's
cost.** Registrable endTime on this evidence: **2000** (1.43x margin; `writeInterval` 500 or 1000
divides it) — a **3x** cost cut on every level.

**THE CAVEAT THAT BINDS IT.** The functionals plateau; **the p residual never satisfies its floor at
any step**; a cured run's plateau step is unmeasured. **N-D45 in converse form: a flat CD history
proves the INTEGRAL is stationary, not that the FIELD is converged — and CD/CL are surface integrals
of pressure while the equation above its floor IS p.** R2's endTime must be measured on the FIRST
CURED COARSE LEVEL, not inherited from this table.

## 7. SURVIVING MEASUREMENT — per-step cost

| level | cells | np | `ExecutionTime` s/step | core-min/step | basis |
|---|---|---|---|---|---|
| L3 | 99,840 | 4 | **0.07327** | **4.885e-03** | 439.6 s / 6000 steps |
| L2 | 798,720 | 8 | **4.864** | **0.6485** | (3414.02 − 13.9) s / 699 steps |

L2 costs **66.4x** L3 per step in seconds, **132.8x** in core-min (the 2x in ranks). Two-point
exponent on core-min/step against cells: **α = ln(132.8)/ln(8) = 2.351** — superlinear, mechanism
measured: 15–17 GAMG cycles against 2.

L1 (6,389,760 cells = 8x L2, np=8), band with its assumption stated:

| assumption | core-min/step | 6000 steps | 2000 steps | wall at np=8, 2000 steps |
|---|---|---|---|---|
| **floor**, α = 1.0 (GAMG count saturates) | 5.19 | 31,100 | **10,400** | 21.6 h ExecTime → **36.8 h** at the measured 0.587 ExecTime/ClockTime |
| **measured**, α = 2.351 | 86.1 | 516,600 | **172,200** | 21.5 d ExecTime → **36.6 d** |

**Even at a 3x-shortened endTime, L1 is 1.5 days at the floor and 37 days at the measured exponent.
Shortening endTime does not clear the 8x cell jump.** Dollars **DERIVED, NOT MEASURED** at
c7a.4xlarge $0.0513/core-h (`COMPUTE_BUDGET_CHARTER.md` §5): L1 at 2000 steps is **$8.89 to $147**.
3D cap-stop exemption applies (Sanaa 2026-09-10): **costed, never cap-stopped.**

Box at measurement: load1 **71.93** on 16 cores (4.5x oversubscribed); L2's own
`ExecutionTime/ClockTime = 0.587`, read off the solver's two clocks, not inferred from `ps`.

## 8. THE TWO BRIEFED LEVEL FAMILIES WERE ALREADY BLOCKED, INDEPENDENTLY OF THE STALL

- **Option A (12,480 / 99,840 / 798,720).** 12,480 = 1,560 faces x 8 layers needs the **c3** surface
  — the different body of §2.4. The alternative on c2/c1/c0 x 2/4/8 layers puts **2 cells across the
  boundary layer** and 8 layers across marchDist 12.0 at s0 = 1e-4 (per-layer growth ~4.2):
  mesh-infeasible, refused by `G-MESH`.
- **Option B (1,560 / 12,480 / 99,840).** Needs a **c4** surface. §2.3 measured that the exact
  factor-2 chain **BREAKS at c3** — smallest block dim already 3 nodes, blocks (3,3), (3,33), (3,21)
  cannot halve. **Not constructible.** No asymptotic-range probability is offered, because there is
  no family to run.
- **c2/c1/c0 with N−1 = 16/32/64 is the UNIQUE exact-r=2 family on this geometry at this
  `marchDist`.** A3GC chose the only one. Anything cheaper needs a different mesh recipe — scaled
  `s0`, reduced `marchDist`, or a non-factor-2 surface generator — not a different selection from
  the existing chain.
