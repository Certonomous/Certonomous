# F6b periodic hill — relaxation-invariance check (L-47), pre-registration

Date: 2026-08-11. **Written and committed before any iteration of either new arm
ran.** Instrument: `LESSONS.md` L-47 — relaxation factors are a *path* parameter;
they change how a steady solve reaches its fixed point and cannot change where
the fixed point is. Two runs of the same case differing only in relaxation must
therefore agree at convergence, and disagreement is proof of non-convergence
**that never consults a residual**.

## 0. Frame — stated before any number in this file

**The frame is the rung the standing verdict is read off, not the rung the
record's prose names.**

`F6b_ERCOFTAC_RESULTS.md` names its relaxation gap in §4, in its own words:
*"the relaxation factors (0.5/0.5/0.7/0.7) are the shipped case's, tuned for the
shipped resolution, and a 62,400-cell mesh may simply need tighter
under-relaxation. This is cheaper still to test and should be tested first."*
That sentence is about the **veryfine** rung, and the question it asks is *does a
steady solution exist at 62,400 cells* — a question whose answer changes §4 and
nothing else.

The **standing verdict** — Gate P FAIL, reattachment `x_R/h = 7.6472` against
Fröhlich et al. 4.6–4.7, **+63% to +66%** (`F6b_ERCOFTAC_RESULTS.md:190`) — is
read off the **medium** rung, and so is the Gate V PASS at 0.043% and the Gate Q
PASS at 12.82%. Both are stated in the record itself: *"Both are decided on the
medium rung"* (§4). The veryfine rung is quoted for no separation or
reattachment number anywhere.

So this check is registered against the **medium rung**. The veryfine relaxation
question is a different question, is not what the +63–66% rests on, and is
priced but not spent here (§7). Running the veryfine arm and reporting it as if
it had tested the verdict would be the L-55 shape — a true sentence about one
artifact standing in for a claim about another.

## 1. What is on the table

| item | value | source |
| --- | --- | --- |
| reattachment `x_R/h`, medium rung | **7.6472** | `F6b_runs/gate_result.json` |
| separation `x_S/h`, medium rung | **0.2604** | same |
| skin-friction sign changes | **2** (steady bubble) | same |
| profile scaled MAE, 9 stations | **12.821%** | same |
| Gate P deviation vs 4.6–4.7 | **+63% to +66%** | `F6b_ERCOFTAC_RESULTS.md:190` |
| Gate V deviation vs shipped mesh | **0.043%** | `F6b_ERCOFTAC_RESULTS.md:92` |
| convergence evidence | `SIMPLE solution converged in 5997 iterations`, 1 sentence | `F6b_runs/residual_history.txt` |

Every one of those numbers is read off a solve whose relaxation setting has
never been varied.

## 2. The two relaxation settings, and why these two

**Arm A (incumbent, already on disk, not re-run):** `p 0.5, U 0.5, k 0.7, omega 0.7`.
Case `F6b_runs/medium`, written time 5997. These are the shipped ERCOFTAC
`PH_Breuer` case's own factors, inherited unchanged — which is precisely why
they are the untested switch.

**Arm B (new solve):** `p 0.3, U 0.7, k 0.7, omega 0.7`.

**Arm C (new solve):** `p 0.3, U 0.3, k 0.5, omega 0.5`.

Why these:

- **Materially different.** Arm B moves the pressure factor by −40% and the
  momentum factor by +40% — it *inverts the split* between the pressure and
  momentum legs of SIMPLE rather than scaling both the same way. Arm C is
  uniformly tighter, −40% on `p`, −40% on `U`, −29% on the turbulence fields.
  The two alternatives perturb the path in different directions, so a spurious
  agreement caused by two settings tracing near-identical trajectories is ruled
  out by construction rather than by hope. The L-47 precedent (F5c, 0.15/0.4 vs
  0.3/0.6) separated its arms by a factor of 2 and found 2.6× in the answer;
  these are separated by 1.4–1.7× in each factor, across two independent
  directions.
- **Both defensible.** Arm B is OpenFOAM's own documented steady practice and is
  recorded as this lab's understanding of it at `docs/NUMERICS_KNOWLEDGE.md:106`
  (*"Steady `fvSolution` practice: relaxation p 0.3 / U 0.7"*). Arm A and Arm B
  both satisfy the classical complementarity rule α_p + α_U ≈ 1. Arm C is the
  "tighter under-relaxation" the F6b record itself asks for, and is inside the
  range this lab has run elsewhere (F5c ran p 0.15 / U 0.4; F8 ran p 0.2 / U 0.5).
  Neither alternative is a straw setting chosen to fail.
- **Nothing else changes.** Arm B and Arm C are byte-identical copies of
  `F6b_runs/medium` — same mesh, same `0/` fields, same `fvSchemes`, same linear
  solvers and their tolerances, same `residualControl` 1e-6 on all four fields,
  same nine sampling stations, same serial execution on one core. Two edits
  only: the `relaxationFactors` block, and the iteration cap (§4).

## 3. The agreement bar

Declared on **reattachment `x_R/h`**, the quantity the verdict is read off.

| band | criterion | meaning |
| --- | --- | --- |
| **CONFIRMED** | \|Δx_R\| / x_R(A) ≤ **0.5%** | the fixed point is real |
| **GREY** | 0.5% < \|Δx_R\| / x_R(A) ≤ 5% | fixed point exists but is not tight enough to carry a 0.043% Gate V claim |
| **DISAGREEMENT** | \|Δx_R\| / x_R(A) > **5%** | proof of non-convergence |

Why 0.5% and 5%: 5% is the record's **own** pre-registered Gate V tolerance on
reattachment and its own grid-sensitivity threshold, so a relaxation move at or
past it is a move as large as the tolerance the verification claim was granted.
0.5% is an order of magnitude below that, below the **1.4%** the answer moves
across the ladder's whole four-fold cell range, and about ten times the
**0.043%** the medium rung already achieves against an independently built,
independently solved mesh — so it demands that relaxation move the answer less
than the mesh does, without demanding a precision the case has never shown.

Secondary bars, reported but not decisive on their own:

- **separation `x_S/h`**: ±0.05 h, the record's own Gate V separation tolerance.
- **bubble topology**: arm must produce exactly **2** skin-friction sign changes.
- **profile MAE**: within ±1.0 percentage point of 12.821%.

**Validity precondition.** An arm counts only if it prints
`SIMPLE solution converged` — i.e. reaches `residualControl` 1e-6 on all four
fields — before its cap. An arm that hits the cap is **INCONCLUSIVE for that
arm**, not a disagreement: a run that did not converge cannot be evidence about
where a fixed point is. This is the one place the iteration-cap difference
between arms could matter, and it is disarmed by refusing to read anything off a
capped run.

## 4. Iteration cap and the cost, priced from this case's own measured basis

**Basis, measured on this exact case and no other:** the medium rung's own log
records `ExecutionTime = 407.61 s` for `5997` iterations serial on one core
(`F6b_runs/residual_history.txt`) = **0.06797 s/iteration**, equivalently
**6.79 core-min** for the whole solve. No rate is borrowed from another solver
family, another mesh, or another case size.

Cap: **20,000 iterations** per arm — 3.3× the incumbent's converged count.
Worst case per arm: 20,000 × 0.06797 s = 1,360 s = **22.7 core-min**.

| item | core-min |
| --- | --- |
| arm B, at the incumbent's 5,997 iterations | 6.8 |
| arm C, at the incumbent's 5,997 iterations | 6.8 |
| expected total (both arms, ~1.3× incumbent count) | **≈ 18** |
| hard ceiling (both arms hitting the 20,000 cap) | 45.4 |
| gate re-analysis (`gate.py` path, two cases) | < 1 |
| **declared budget for this check** | **50 core-min** |

Both arms run concurrently, serial, one core each, `taskset`-pinned, on a
16-core box. Wall-clock ≈ the slower arm alone.

## 5. Predictions, labelled by class per L-54

`artifact` = a prediction about a file or a solve. `agent` = a prediction about
what a person or process will do. This file contains no `agent` predictions,
which is itself the point of labelling.

| # | class | prediction | confidence |
| --- | --- | --- | --- |
| 1 | artifact | Arm B converges (prints `SIMPLE solution converged`) inside 20,000 iterations | 0.85 |
| 2 | artifact | Arm C converges inside 20,000 iterations | 0.75 |
| 3 | artifact | **Arm B lands CONFIRMED: \|Δx_R\|/x_R ≤ 0.5%** | 0.80 |
| 4 | artifact | **Arm C lands CONFIRMED** | 0.75 |
| 5 | artifact | Both arms produce exactly 2 skin-friction sign changes | 0.85 |
| 6 | artifact | Arm C takes more iterations than arm B | 0.85 |
| 7 | artifact | Arm B iteration count lands in [4,000, 12,000] | 0.70 |
| 8 | artifact | Neither arm's `x_R/h` falls inside the literature band [4.21, 4.70] | 0.95 |

**The mechanism behind 3 and 4, predicted as a mechanism and not only as a
number (L-54):** the medium rung's answer already survives two independent
perturbations of the discretization — it agrees with an independently coded,
independently meshed, independently solved shipped case to 0.043%, and it moves
0.097% between the medium and fine rungs. A field that reproducible under
changes of *discretization* is unlikely to be sensitive to a change of *path*,
because path-dependence of this kind is the signature of a solution that is not
a fixed point at all — the failure mode visible in this record's own veryfine
rung, whose residuals do not fall.

**Prediction 8 is the one that separates the two things this check can prove.**
Even a 5% disagreement leaves `x_R/h` at ≈ 7.27, still +55% or more against the
reference band. So:

## 6. What each outcome means — written now, not after

- **CONFIRMED on both arms.** The medium rung is at its fixed point. The
  **+63% to +66% reattachment miss is the model's, and the Gate P verdict
  stands** — stock kOmegaSST over-predicts periodic-hill recirculation length,
  and the number is not an artefact of an untested relaxation switch. The
  0.043% Gate V claim and the 12.82% Gate Q claim keep their precision. The F6b
  record gains the only convergence evidence in the lab that cannot be defeated
  by an instrument error.
- **DISAGREEMENT on either arm.** The medium rung is **not** converged, whatever
  its residuals and its `SIMPLE solution converged` sentence say. **Every number
  read off it is in question** — 7.6472, 0.2604, the 0.043% Gate V PASS, the
  12.82% Gate Q PASS, and the four-decimal precision of all of them. The Gate P
  *direction* would likely survive (prediction 8), and saying so is required:
  the honest claim would become "kOmegaSST over-predicts by a large margin whose
  size we cannot state", not "the verdict is fine". Gate V, which is a claim
  about agreement to 0.043%, would not survive at all.
- **GREY on either arm.** The fixed point exists but is looser than the record's
  own precision. Gate P survives in sign and rough magnitude; the 0.043% Gate V
  agreement becomes a coincidence of two runs at the same relaxation and must be
  restated with the invariance spread attached.
- **INCONCLUSIVE (arm hits cap).** Nothing is read off it. Reported as spent
  budget that bought no evidence, which is the honest accounting.

## 7. Priced but not spent: the veryfine arm

The record's §4 asks for tighter relaxation on the **veryfine** rung. On this
case's own basis that rung cost 25.57 core-min for 6,000 capped iterations =
0.2557 s/iteration; a tighter-relaxation arm at a 20,000 cap prices at
**85 core-min**, nearly twice this whole check. It decides §4's competing
readings and it decides **nothing** about Gate P, Gate V or Gate Q. It is
registered here as an open, priced experiment and deliberately not run in this
check.

## 8. Evidence to be produced

- `F6b_runs/medium_relax_B/` and `F6b_runs/medium_relax_C/` — cases, dictionaries, written fields
- `F6b_runs/relax_invariance.json` — machine-readable result, produced by the same `gate.py` crossing logic
- `F6b_runs/relax_invariance_ledger.txt` — self-ledger: launch time, command, per-arm iteration/residual samples, exit state
