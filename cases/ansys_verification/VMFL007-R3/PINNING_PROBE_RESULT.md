# VMFL007-R3 — PINNING PROBE RESULT — 2026-08-31

**This is a DIAGNOSTIC record, not a graded run and not a verdict.** It records the
two-level pinning probe the supervisor authorised, its pre-fixed decision rule, and
what it measured. **The result is fail-closed: the freeze is BLOCKED.**

## Authorisation and rule (both the supervisor's, fixed BEFORE the probe ran)

- **Authorised:** L1 (25×25) and L2 (50×50) only, each toward convergence, solver
  arm **A5 (PBiCGStab/DIC)**, in a SCRATCH directory OUTSIDE
  `verification/runs/ansys_verification/` (so it could not consume the graded run
  root or trip the rule-4 age guard), cap **3 core-min total**. Diagnostic, not
  graded. The gate quantity read on its functional **plateau window** (peak-to-peak
  of Δp over a flat window), not the residual.
- **Decision rule, fixed in advance, fail-closed** (the supervisor's; not adjusted
  to fit the return): with `d21 = |Δp(L2) − Δp(L1)|` and `ptp` = the larger of the
  two levels' plateau peak-to-peak,
  - `d21/ptp ≥ 100` → Δp moves with the mesh well above iterative noise → **NOT
    pinned** → gradeable → proceed toward freeze.
  - `d21/ptp < 100` → Δp pinned or near-pinned → the triple is structurally EXACT →
    rule 5 limb 2 → **DO NOT FREEZE.**
  - Anchors: VMFL021-R2 measured ≈ 300× (sound); VMFL003-M2 measured d21 = 0 exactly
    (pinned).

## What was measured

Case built from the byte-identical VMFL007 run-1 physics inputs (0/U `b626d65a`,
transportProperties `db848a12`, fvSchemes `ad718abf`, blockMeshDict.template
`9ea967eb`), arm A5 `fvSolution`, endTime 30000, Δp = ρ(⟨p⟩_inlet − ⟨p⟩_outlet),
ρ = 1000. Ran in scratch outside the runs tree (path not cited, CLAUDE.md rule 13;
the numbers below are the record).

| level | mesh | outcome | Δp (Pa) | plateau ptp (Pa) | dev vs 60 521.969 Pa |
|---|---|---|---|---|---|
| L1 | 25×25 (625) | **CONVERGED**, rc 0, 30000 iters, 72 wall-s | **60 437.9488** | **0.0000** (bit-flat, last 6000 iters) | **−0.1388 %** (inside §6's 0.5 % band) |
| L2 | 50×50 (2500) | **DIVERGED** — SIGFPE / core dump at iter ≈ 13 275, 96 wall-s | — (blew up to ≈ 1e308, garbage) | — (no plateau) | — |

- **L2 divergence signature:** the U (`smoothSolver`/`symGaussSeidel`) initial
  residual was **rising** (≈ 0.069 → 0.071 and climbing) near the end, then the run
  hit a floating-point exception (`the monitored command dumped core`, rc 136). It
  never reached a Δp plateau.
- **Probe cost: 72 + 96 = 168 wall-s = 2.8 core-min** (serial, RANKS 1), under the
  3-core-min cap. ≈ **$0.0024 DERIVED** at $0.0513/core-h (owner-stated, not
  measured). The authorisation was later WITHDRAWN by the supervisor under Sanaa's
  demo priority; **the probe had already completed when the withdrawal arrived**, so
  no compute was spent against a withdrawn authorisation and nothing was left running.

## The rule, applied

**`d21` is UNMEASURED — L2 produced no converged Δp — so `d21/ptp` CANNOT be
evaluated. The rule is UNSATISFIED. Fail-closed: DO NOT FREEZE.**

The "d21/ptp = 1.0" a naive script printed is meaningless: it divided two garbage
(≈ 1e308) values from the diverged L2 series. **It is not a measurement and must not
be read as `< 100 → pinned`.** The pinning question is not answered either way; it is
UNMEASURED.

## Two blockers, both of which must clear before any freeze

1. **The pinning question is OPEN (unmeasured).** L1's clean converged Δp
   (60 437.9488 Pa, bit-flat) is consistent with the physics argument that Δp is not
   pinned (it is the output of an imposed-flow-rate solve, carrying the radial
   wall-gradient error) and refutes nothing — but a valid `d21` needs two converged
   levels, and L2 did not converge. The pre-fixed `d21/ptp ≥ 100` rule must be
   re-run to a PASS.
2. **Arm A5 is NOT mesh-robust** — converges at 25×25, diverges at 50×50. No graded
   triple can run on it. A configuration proven to converge on 25/50/100 must be
   found FIRST (candidates: tighter U relaxation, a Krylov U solver, SIMPLEC). This
   is a solver-robustness finding the single-grid R2 slate could not have surfaced —
   the "cause class is not repair class" pattern again.

**The §11 comparator's fail-closed pinning-refusal stays regardless** — even a future
probe that clears the rule does not exempt the graded comparator from refusing if d21
collapses on the real triple.

## What a resumed effort does, in order

1. Find a solver arm that converges on all three levels (25/50/100) — proof, not
   assertion.
2. Re-run the pinning probe (L1+L2, that arm) and clear `d21/ptp ≥ 100`.
3. Only then: fix the frozen numeric constants and freeze (the supervisor's).

**No graded run has run. Nothing is frozen. The scratch probe directory is outside
the runs tree and is not a graded artifact.**
