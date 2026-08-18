# A3 ladder rung 2 (42,120 cells) — RESULT: **CONVERGED + FD PASS. The ladder has two verified rungs.**

Pre-registration `A3_RUNG2_N28_PREREGISTRATION.md`: base `22c8e988` (14:54:38Z), addendum
`2b3e6517` (15:06:27Z, before attempt 2). Case: staged copy
`/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/` (guidelines §8 staged-copy pattern; the
archived D3 member left pristine as the record it is).

## Outcome per the pre-registered mapping — branch one fires

> Arm A converges AND arm B passes → the ladder has two verified rungs and the mesh-size
> question opens honestly.

**Arm A (convergence): both adjoint solves `PetscConvergedReason: 2`.**

| solve | iterations | reason | residual path |
|---|---|---|---|
| CD | **987** | **2** | 2.121211553380e−02 → below the 1e−4 relative target, 237.01 s |
| CL | **1171** | **2** | 1.839192419993e−01 → **1.824629776972e−05**, monotone, 423.13 s |

**Arm B (FD verification, charter §7): PASS — and stronger than rung 1, all three components
evaluable and step-consistent.** Noise floor (repeat-baseline drift) 8.093e−07; evaluability
threshold 8.09e−06; every component's CD delta clears it by 45x–3,213x.

| component (runtime argmax\|g\|) | adjoint | FD(h=1e−2) | FD(2h) | step-cons | rel err | verdict |
|---|---|---|---|---|---|---|
| patchV[1] (AoA) | 7.90292883e−03 | 7.90232345e−03 | 7.90521694e−03 | 0.0366% ✓ | **0.0077%** | **PASS** |
| twist[1] | 1.80386732e−03 | 1.80882369e−03 | 1.80327914e−03 | 0.3065% ✓ | **0.2740%** | **PASS** |
| shape[115] (max \|g\|) | −1.30055677e−01 | −1.30078078e−01 | −1.30084297e−01 | 0.0048% ✓ | **0.0172%** | **PASS** |

Arm verdict per §5: all evaluable components PASS with ≥2 evaluable → **PASS**. The rung-2
gradient is FD-verified, not an existence proof. The runtime `argmax|g|` selection (§4) chose
`shape[115]` on its own — the same FFD component that was rung 1's true maximum, reached with
no hand-transcribed index and therefore no repeat of the rung-1 mis-parse.

## Attempt 1, and why its `-3` was refused rather than mapped

Attempt 1 (rc=0, 606 s = 40.4 core-min) returned CD reason 2 at 987 iterations and CL
**`-3` (KSP_DIVERGED_ITS) at exactly the default `gmresMaxIters` 1000**, residual
1.307615741156e−04 after a monotone 1407x descent. §5's letter would have called that DIVERGED
and §6 would have called it "the wall is real above this rung" — a false statement, refused for
the same reason the sub-LU memory death was refused. The addendum's falsifiable prediction was
that a raised budget alone would finish it.

**It is now proven, not argued.** Attempt 2 (identical but `gmresMaxIters` 1000 → 2000)
reproduces attempt 1's CL residual at iteration 1000 as **1.307615740828e−04 vs
1.307615741156e−04 — ten significant digits** — then continues to convergence at 1171. The two
runs are the same solve, one of them truncated. The `-3` was a budget knob and nothing else.

## Independent adversarial verification (produced by a second agent, dispatched on a mistaken-kill belief; it staged nothing and stood down)

Three items, all independently derived — verification rather than duplication:

1. **The admission gate replicated.** That agent ran `checkMesh` on the archived member in its
   own container 52 s before mine landed. Both agree to every printed digit: clean, 42,120
   cells, `points_sha256 7eb9866e…`, max AR 608.214865637278, max non-orthogonality
   61.49354913677975, max skewness 1.916854554279592, zero hard errors. Two independently
   launched checks, identical numbers — a free replication of the gate this rung entered on.
2. **The L-40 and cold-start proofs verified from the raw log by an outside reader:**
   `transonicPCOption 1;` at line 410 of the arm log (the record log reads `2;` at its own line
   410); zero sub-LU banner occurrences; first continuity error 0.6833296303785072 matching
   this mesh's cold-from-uniform signature; staged `0/` bit-identical to `0.orig` on all six
   fields; runScript diff vs archived = the single token.
3. **A pre-answer prediction, graded.** Author: the independent agent, before attempt 2
   returned. Method: CL fell 1.364 decades over iterations 600→1000 (0.341 decades/100), with
   0.852 decades left to target → predicted convergence **near iteration ~1250, inside the
   2000 cap**. **Actual: 1171 — the prediction was correct in direction and inside 7% on
   magnitude (conservative by 79 iterations).** It belongs in the calibration cohort as a hit.

## Pricing basis for rung 3, measured (the finding that outlives this rung)

Iteration count scales **superlinearly in cells, and pricing off cells alone will underestimate
badly**: CD went 368 → 987 iterations for 21,840 → 42,120 cells (**2.68x the iterations for
1.93x the cells**, exponent **1.50**); CL went 383 → 1171 (3.06x, exponent **1.70**).
Per-iteration cost scales about linearly (0.144 s/iteration at this rung).

Extrapolated for **rung 3 (79,560 cells)**, to be inherited as a measured basis rather than a
forecast: CD ≈ **2,570 iterations**, CL ≈ **3,460 iterations** — so `gmresMaxIters` must be
raised to **≥ 4000** before that arm launches or it will die on the cap the way attempt 1 did,
and per-iteration cost ≈ 0.27 s puts arm A near **~1,700 s wall ≈ 113 core-min**. Rung 3 is
therefore roughly 4x rung 2's arm A, not 1.9x.

## Spend, reported against the estimate without softening

| arm | wall | core-min | vs estimate |
|---|---|---|---|
| A attempt 1 (cap 1000) | 606 s | 40.4 | est. ~15 → **2.7x over** |
| A attempt 2 (cap 2000) | 434 s | 28.9 | — |
| B (FD) | 452 s | 30.1 | est. ~32 → inside |
| **rung 2 total** | | **99.5** | est. ~47 → **2.1x over** |

The overrun is real and its cause is the finding above: the arm was priced off cells (1.93x)
when iterations scale at cells^1.5–1.7. That mis-pricing is now corrected for rung 3.

## Certification and artifacts

Birth certificate (MESH_STANDARD v1.1 §6) written by `sdk/chief_engineer/mesh_certificate.py`
beside both the staged and archived `polyMesh`: verdict **clean**, `certificate_admits() ==
True`, hash-bound `points_sha256 7eb9866e…`. Note for the standard's own record: this appears
to be the **first `birth_certificate.json` sidecar minted in the lab** (the 2026-08-08 sweep
issued retained checkMesh logs; the JSON mechanism had not yet been exercised) — and it
reproduces that sweep's row for this mesh exactly. `log.checkMesh` is also placed beside the
case so the standard's second enforcement layer (`assert_mesh_certified_at_entry`, which gates
on that filename) admits it. Canonical hash-bound lever evidence
(`sdk/chief_engineer/lever_echo.echo_block`) captured as `lever_echo_block.txt`, 10 files
hashed, alongside the launcher's own declared echo `lever_echo.txt`.

Artifacts in the staged case: `tpc1_computetotals_attempt{1,2}.log`, `fd3_run.log`,
`runScript_tpc1.py`, `runScript_fd3.py`, `run_arm_{a,b}.sh`, ledgers `.t0/.rc/.t1`,
`checkMesh_rung2.log` / `log.checkMesh`, `constant/birth_certificate.json`.

## What this opens, stated without overselling

Two rungs (21,840 and 42,120 cells) now converge and pass FD with the transonic PC active,
where the archived record had double `-5` at both. The mesh-size question is open and
answerable rather than hopeful — but nothing here claims the taller rungs (79,560 / 99,840 /
399,360 cells) will converge, and at those sizes the memory wall the envelope measured is a
separate blocker from conditioning. Rung 3 is priced above and is the chief's call, not this
arm's claim.
