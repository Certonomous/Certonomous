# A3 ladder rung 3 (79,560 cells) — RESULT: **DIVERGED by stagnation. The reopened ladder has a ceiling, and it sits between 42,120 and 79,560 cells.**

Pre-registration `A3_RUNG3_N52_PREREGISTRATION.md` (`3e585b07`), stage-0 outcome and lever
withdrawal recorded in `A3_TRIAGE_LEVERS_PREREGISTRATION.md` §10 (`feb79e45`). Staged case
`/home/ubuntu/certonomous-runs/A3-rung3-n52/`. Mesh certified before launch (verdict `clean`,
`points_sha256 cf35cf14…`).

## Stage 0 (mandatory transfer test): FAILED — and it earned its 15.9 core-min

L3 Richardson at rung 2, the only change from the arm that converged there:
**both solves `-5`, collapsing to exactly 0.0 at iteration 200 — `gmresRestart`, the first
restart boundary.** The pre-registered third branch fired ("the lever collapses at the next
rung", not merely "benefit fails to transfer"). Consequences, both executed: rung 3 reverted to
the baseline basis (`gmresMaxIters` 4000), and my own over-broad R5 retraction was corrected on
R5's face the same hour (`5aa3a142`). **Stage 0 stopped rung 3 from launching on a lever that
would have collapsed it.**

## Stage 1 (arm A, baseline config): DIVERGED — stagnation, not budget, not memory

| solve | iterations | reason | residual |
|---|---|---|---|
| CD | 4000 (the cap) | **−3** | 2.121343646203e−02 → **1.615245992220e−02** |
| CL | never attempted | — | DAFoam raised `AnalysisError("Adjoint solution failed!")` after CD |

Ledger rc=1, wall 1,426 s = **95.07 core-min**. Proofs in-log: `transonicPCOption 1;`, no
sub-LU banner, `GMRES Max Iterations: 4000`, cold start from uniform.

**Why this `-3` is the wall and rung 2's `-3` was not — the distinction was pre-registered
before either was seen** (§5: *"a `-3` at exactly the cap with monotone descent is reported as
budget-limited, not as a wall"*):

| | rung 2 CL (`-3`, budget) | rung 3 CD (`-3`, **wall**) |
|---|---|---|
| total residual reduction | **1407x**, monotone | **1.31x** |
| behaviour at the cap | still descending ~3x per 100 iterations | **flat** |
| residual change, iter 1300 → 4000 | n/a (converged at 1171) | **3.79e−07 relative over 2,700 iterations** |
| resolved by raising the cap? | **yes** — converged at 1171, and the iteration-1000 residual reproduced to ten significant digits | **no** — extrapolating the observed rate, the 1e−4 relative target is unreachable |

The residual is flat to nine significant figures across 2,700 iterations. That is stagnation.

**It is not a memory death, and that matters for what may be claimed.** Peak container usage
**11.65 GiB against the 22 GiB cap**, host MemAvailable never below 17 GB, no swap growth, no
OOM — the memory guard never approached tripping. The standing family rule (a memory death is
NOT EVALUABLE, never a conditioning verdict) is what makes this verdict sayable: memory was
comfortable and the solver still would not converge, so this **is** a conditioning result.

## Outcome per the pre-registered mapping (§7, third branch)

> DIVERGED (negative reason, not the cap case, PC and lever proven active) → the wall is real
> above 42,120 cells with the PC active: a clean ceiling statement for the reopened ladder,
> and the extrapolation stops there honestly.

**The reopened ladder's ceiling lies between 42,120 and 79,560 cells.** Two rungs converge and
pass FD with the transonic PC active; the third stagnates with the same configuration, ample
memory, and a cap 1.6x above the predicted requirement.

## The ladder-level question, answered (§1)

§1 asked whether the iteration exponent (CD cells^1.50, CL cells^1.70) **holds or breaks at the
next doubling**, because every extrapolation toward production meshes rests on it. Pre-stated
prediction: **CD ≈ 2,570 iterations**.

**The exponent BREAKS — and it breaks in the worst of the available ways.** Not a larger
number: no convergence at all. The prediction is falsified not by 20% or 50% but by kind, and
the honest reading is that the two-rung law had no predictive authority across this doubling.
**A two-point slope in this family is a description of the two points, not a cost law** — which
is exactly what this rung was run to find out, and it is worth more than a third confirming
rung would have been. Any extrapolation toward the 399,360-cell class is now foreclosed by
measurement rather than by caution.

## Stage 2 (FD arm): correctly NOT LAUNCHED

Pre-registered as conditional on stage 1 converging (§8). It did not, so the ~60–70 core-min
were not spent. Rung 3 total: stage 0 15.93 + stage 1 95.07 = **111.0 core-min against the
approved 170–190** — under budget because the pre-registered gate did its job.

## What stands, and what this does not claim

- **Stands:** rungs 1 (21,840) and 2 (42,120) converge and are FD-verified; the transonic-PC
  token remains the difference between double `-5` and convergence at both; the negative
  control's bit-for-bit reproduction is untouched.
- **Not claimed:** that 79,560 cells is *the* boundary — the ceiling is bracketed by two
  measured points, not located. Nothing here says the M6 adjoint is unreachable at that size by
  any means; it says the configuration that works at two rungs stagnates at this one, with
  memory comfortable.
- **Not claimed:** that stagnation and the earlier `-5` breakdown are the same mechanism. They
  are different signatures (flat stall at a cap vs collapse to denormal) and this arm does not
  identify the mechanism behind either.

## Named follow-ups (reported, not run — the chief's call)

1. **Bracket the ceiling**: one arm at the untested intermediate size (the D3 family's ~63k
   rung, or a fresh pyHyp N between 28 and 52) would halve the bracket for ~40–60 core-min.
2. **Attack the stagnation directly**: `gmresRestart` is 200 at every rung; at rung 3 the CD
   solve crosses 20 restarts. L2 (restart 1000) was a material winner at rung 1 and costs
   memory rung 3 has to spare (11.65 of 22 GiB) — the one untried lever whose mechanism
   (retaining search directions instead of discarding them 20 times) matches this failure mode.
   This is the follow-up I would run first.
3. **The restart hypothesis** from stage 0 (`R5_ADJOINT_CONDITIONING.md`, 5aa3a142) predicts
   fill1 also collapses at rung 2 — one cheap arm falsifies or supports it.

## Artifacts

`A3-rung3-n52/`: `rung3_stage1.log`, `runScript_rung3.py`, ledger `.t0/.rc/.t1`,
`lever_echo.txt`, `constant/birth_certificate.json`, `log.checkMesh`.
`A3-stage0-n28-richardson/`: `stage0_richardson.log`, `runScript_stage0.py`, ledger.
