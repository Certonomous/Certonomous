# The inherited relaxation setting costs a third of every steady solve that carries it

Date: 2026-08-11. Zero core-minutes: every number here is read from solves that
already ran. Origin: the one **falsified** prediction of the F6b
relaxation-invariance check (`campaign/F6b_RELAXATION_INVARIANCE_RESULTS.md`,
pre-registered `ce0b14be`). Companion proposal:
`agenda/proposals/test-the-solver-default-relaxation-across-the-family.json`.

## 1. The finding, which is a falsified prediction promoted

The invariance check pre-registered that alternative relaxation settings would
need **at least as many iterations** as the incumbent, and priced them that way.
It was wrong, and the direction it was wrong in is the useful part:

| relaxation | iterations to `SIMPLE solution converged` | ExecutionTime | core-min |
|---|---|---|---|
| **0.5 / 0.5 / 0.7 / 0.7** — the shipped setting | **5,997** | 407.61 s | **6.79** |
| **0.3 / 0.7 / 0.7 / 0.7** — OpenFOAM's documented default | **3,936** | 253.01 s | **4.22** |
| 0.3 / 0.3 / 0.5 / 0.5 — uniformly tighter | 11,700 | 726.63 s | 12.11 |

**The solver's own default converged the same case to the same answer in 66% of
the incumbent's iterations, for 62% of the core-minutes** — a **37.8% saving** on
a solve whose answer was identical to 0.0105%. Per-iteration cost was also
slightly lower (0.0643 s against 0.06797 s), so the saving is not an artefact of
cheaper iterations; it is fewer of them.

**Nobody chose 0.5/0.5.** It is the shipped ERCOFTAC `PH_Breuer` case's value,
inherited unchanged when the case was cloned, and this is the first time it has
been compared against anything.

## 2. Reach — measured, not assumed

Census over **every `fvSolution` in the tree carrying a `relaxationFactors`
block**: 317 files.

| p / U | cases | share |
|---|---|---|
| **0.5 / 0.5 (the untested inheritance)** | **122** | **38.5%** |
| 0.3 / (U unset) | 77 | 24.3% |
| (p unset) / 0.9 | 70 | 22.1% |
| neither set | 33 | 10.4% |
| 0.25, 0.15, 0.2 / (U unset) | 9 | 2.8% |
| **0.3 / 0.7 (the default)** | **5** | 1.6% |
| 0.3 / 0.3 | 1 | 0.3% |

**122 cases carry the inherited setting and 5 carry the default** — and 3 of
those 5 are the arms this check created today. The 122 span three families:
Cases (`F6b_runs`, `W2_sparta_runs`), DAFoam (`f6b_periodic_hills`,
`f6d_random_matrix_uq`, `ladder-b`).

**This is a reach count, not a saving claim.** The 37.8% is measured on **one**
case. Whether it transfers is exactly what the companion proposal asks, and §5
says why it might not.

## 3. What the census turned up on the way, which matters more than the cost

Pricing the proposal meant opening the 122 cases' logs. The largest single block
is the **84-member `f6d_random_matrix_uq` ensemble**, and it carries two defects
this lab has already diagnosed and fixed **somewhere else**.

**(a) All 84 members carry `residualControl { p 1e-15; }`.** That is the exact
defect `F6b_ERCOFTAC_RESULTS.md` §3 documented and closed *for F6b*: *"a
tolerance no GAMG pressure solve reaches on this mesh, so simpleFoam could never
declare convergence and the lab's gate checker returned a documented false
negative."* Measured here: **84 of 84** members carry `1e-15`, and **0 of 84**
print `SIMPLE solution converged`. The zero is not evidence of non-convergence —
it is the unreachable target, and any instrument reading that zero as a
convergence fact is reading a false negative. **The fix was applied to the case
where it was found and never propagated to the ensemble sharing its lineage.**

**(b) 76 of 84 members have a momentum residual that is RISING at the cap.**
Comparing each member's initial Ux residual at its midpoint against its final
iteration: **76 rise, 8 fall.** The `null` member runs
2.10e-6 → 4.30e-6 → 8.02e-6 → **1.57e-5** at iterations 1,000/2,000/3,000/4,000 —
a **7.5× rise**. The worst, `d0.6_s011`, rises **9.94×**. These solves are
drifting away from a fixed point over their second half, not toward one.

**Both are stated as measurements, and (b) is not yet a verdict.** These are
random-matrix UQ members with perturbed Reynolds-stress fields, so some are
legitimately harder than a baseline, and a rising initial residual under a fixed
cap is consistent with more than one cause. What is not in doubt is that **an
84-member ensemble feeding a UQ result has no convergence evidence of any kind**,
because the one sentence that would carry it was made unreachable by an inherited
constant.

**Routed to the DAFoam family, not fixed here** — `f6d_random_matrix_uq` is
theirs, and this note is a Cases-family write-up of a Cases-family measurement
that happened to see over the fence.

## 4. Why this is worth a ruling rather than a quiet edit

The tempting move is to change 122 files. That would be wrong twice over:

- **The 0.5/0.5 in `F6b_runs/{coarse,medium,fine,veryfine}` must not change.**
  Those are the published Gate V / Gate P / Gate Q record. Re-running them at a
  different setting would re-base a result onto a number produced after it, and
  destroy the comparison this note rests on.
- **One case is not a basis.** 37.8% on a 15,600-cell periodic hill says nothing
  certain about a 2,000-cell duct or a snapped-hex external body. The pressure/
  momentum split that helps a separated internal flow can hurt elsewhere, and the
  lab has a measured counter-example in its own ladder: the uniformly tighter arm
  cost **2.97×** the default's iterations on the same case.

## 5. What would falsify the whole idea

Stated now, so the proposal cannot be scored generously later: **if a paired
screen on two further case classes shows the default needing more iterations than
the inherited setting on either one, the general claim dies** and the finding
reduces to "0.3/0.7 suits the periodic hill", which is worth one sentence in the
F6b record and nothing more. The saving is a hypothesis with n = 1 and it is
labelled as one.

## 6. Evidence

- `campaign/F6b_RELAXATION_INVARIANCE_RESULTS.md` §3 and prediction 7 — the measurement and the falsification
- `campaign/F6b_runs/relax_invariance_ledger.txt` — per-arm iteration counts and `ExecutionTime`
- `campaign/F6b_ERCOFTAC_RESULTS.md` §3 — the `p 1e-15` defect, diagnosed and closed for F6b on 2026-08-05
- `dafoam/f6d_random_matrix_uq/ens/*/log.simpleFoam` and `system/fvSolution` — the 84-member census
- `LESSONS.md` L-47 (relaxation is a path parameter), L-55 (find the production call site), L-48 (record a gap as a gap)
