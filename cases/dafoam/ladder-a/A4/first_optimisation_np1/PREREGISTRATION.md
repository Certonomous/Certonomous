# A4 Ahmed body — the lab's first optimisation, np=1: PRE-REGISTRATION

**Filed 2026-08-21, Lane A, BEFORE any arm launched.** Predictions, ceilings and falsifiers are
committed first; `RESULTS.md` does not revise this file. Nothing filed upstream.

---

## 1. Why A4, and why now

A4 is the only Ladder-A case with a **PASS gradient at np=1 against the shipped toolchain**
(1.10%, `2.3965e-01` vs FD `2.4232e-01`, `a4_np1_stock.log`). It is 2,777 cells, so a full
optimisation costs minutes. And its gradient's one known defect — the `scotch` decomposition — is
**structurally absent at np=1**, which is the whole reason this runs serial.

**This is the lab's first optimisation in the strict sense.** A2 ran IPOPT for 47 major iterations
on 2026-07-28, but that run is graded **OPTIMISATION RUN, NOT A RESULT**: time-boxed at 60 minutes,
`converged_to_optimizer_tolerance: false`, and IPOPT emitted **no EXIT line and no convergence
statement anywhere** in `opt_IPOPT.txt`. It also destroyed its own case directory. This item is
designed to produce the thing A2 did not: an optimisation that **stops for a stated reason**, whose
final design point is **re-verified against finite differences**, and whose case directory survives.

## 2. Decomposition disclosure, and its justification

**np=1. No decomposition of any kind.** `system/decomposeParDict` is rewritten by DAFoam from
`daOptions` to match the rank count; the log must print `nProcs : 1` or the arm is void.

**Justified against the scotch finding, not merely asserted.** A4 is the case on which the
decomposition defect was found: at np=4 with the shipped `scotch` default, the converged adjoint is
the solution of an operator that is **not the transpose Jacobian** — cross-residual **328.8× ‖b‖**
under the serial operator while the KSP itself reports `PetscConvergedReason: 2` at true-residual
1.7e-07 — and `dCD/dshape` reads **10.04%** against its own FD instead of 1.10%
(`../../UPSTREAM_BUG_REPORT_decomposition_adjoint.md`, `../../DISCRIMINATORS_A4_decomposition_mechanism.md`).
**Driving an optimiser with that gradient would be optimising on a wrong derivative.** np=1 removes
the partition entirely and is the only configuration on this case whose gradient is both graded and
free of that defect. The cost is wall time on a 2,777-cell case, which is negligible.

## 3. Optimisation problem, exactly as the verified case defines it

| item | value | source |
|---|---|---|
| mesh | **2,777 cells** — the *adjoint/FD* mesh, the one the 1.10% PASS was measured on. **Not** the 45,760-cell primal mesh | `../../A4_ahmed_body.md` §3 |
| solver | `DASimpleFoam`, kOmegaSST, `primalMinResTol 1.0e-4`, `primalMinResTolDiff 1.0e5` | archived `runScript.py`, unchanged |
| **design variables** | **ONE.** `shape`, a `nom_addShapeFunctionDV` moving the two top-row FFD control points at the middle x-plane (x=0.80, just upstream of the measured slant break at x=0.8428) together, purely in z. Nose, rear tip and underbody are fixed by construction | `runScript.py:104-112` |
| DV bounds | `lower=-0.05, upper=+0.05`, `scaler=1.0` | `runScript.py:114` |
| objective | `scenario1.aero_post.CD`, `scaler=1.0` | `runScript.py:115` |
| **constraints** | **NONE. There are no `add_constraint` calls in this case at all** — no thickness, no volume, no LE/TE. The FFD is 3×2×2, too coarse to carry them | verified by grep over `runScript.py` |
| image | **`dafoam-idwarp-rot:v1`** (patched IDWarp, `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425`) | `../../patched_build/idwarp_rot/BUILD.md` |

**The absence of constraints is disclosed, not fixed.** Adding a volume or thickness constraint would
change the case away from the configuration whose gradient is verified, and the verification is the
only reason this case was chosen. **This is therefore a bound-constrained one-dimensional
minimisation**, and it must be described that way and never as a constrained shape optimisation.
The supervisor's falsifier "a constraint violated at the reported optimum" is re-expressed as
**"the DV bound violated at the reported optimum"**, which is the only feasibility condition here.

## 4. Optimiser

**IPOPT 3.13.5 via pyOptSparse**, settings mirroring A2's precedent
(`A2-mach-wing/runScript_AeroOnly.py:212-223`) with the iteration cap tightened:

```
tol 1e-6 | constr_viol_tol 1e-6 | max_iter 15 | print_level 5
output_file opt_IPOPT.txt | mu_strategy adaptive
limited_memory_max_history 10 | nlp_scaling_method none
alpha_for_y full | recalc_y yes
```

**Why IPOPT and not SLSQP, stated with the trade-off.** SLSQP is the better-matched algorithm for a
1-variable bound-constrained problem and would converge in fewer function evaluations. **IPOPT is
chosen anyway, for two reasons**: it is the A2 precedent, so the lab's two optimisations are
comparable artifact-for-artifact; and it emits exactly the per-major-iteration columns this item is
required to report (`objective`, `inf_pr`, `inf_du`), which SLSQP does not. The cost is that an
interior-point method is overkill on one variable and will spend iterations on barrier bookkeeping.
**Disclosed as a deliberate trade of efficiency for comparability.**

**Stopping criterion**: IPOPT terminates on `tol 1e-6` (converged) or on `max_iter 15`.
**Per the verdict vocabulary, an optimiser that stops on the iteration cap without meeting tolerance
is GATE REACHED at best, never PASS.**

## 5. Warm-start handling — the house rule, and the trap already sprung today

`../../WARMSTART_AUDIT.md` establishes that **pyDAFoam writes the primal end state back into the
time-0 directory at run end**, silently warm-starting every subsequent run of the same case
directory, and that `renameSolution` hard-raises on a leftover `0.0001`. Its recommendation:
*"The staged-copy pattern (per-arm case subdirs …) is inherently immune to the hazard and is the
recommended pattern for A/B arms going forward; sequential reruns in one case dir REQUIRE the
cold-start restoration step."*

**This trap was sprung earlier today on the A6 rung** — a calibration primal was run in the same
directory a later arm used, and that arm died with `AnalysisError: Primal solution failed!` while a
sibling arm staged from the pristine base ran cleanly with a bit-identical cold-start continuity
error. That is recorded in the A6 results, and it is why the rule is restated here before this item
runs rather than after.

**Applied here:**
* **Three arms, three staged copies**, each made from a pristine `base/` that has never been run in.
* **Within the optimisation arm, warm-starting is intended and correct** — each IPOPT major
  iteration re-solves the primal from the previous design's converged state. That is standard for
  optimisation and is not the hazard; the hazard is *cross-arm* contamination.
* **The final-design check (arm b) runs in the SAME process as the optimisation**, immediately after
  `run_driver()` returns, so the design vector is already at the optimum and no reload, no restart
  and no directory reuse is involved. **This is a deliberate departure from running it as a separate
  container**, chosen precisely because reloading a design point through a contaminated directory is
  the failure A2 suffered (its preserved case reads CD 0.03142 against a published 0.02773 because
  the IPOPT run left the mesh deformed).
* `sudo rm -rf processor*` before every arm.

## 6. Arms, predictions, falsifiers

### Arm (a) — the optimisation

> **PREDICTION P1 — a corner solution at the lower bound.** `dCD/dshape` at the baseline is
> **+2.3965e-01** (np=1 stock analytic) — positive and, over this DV's small range, expected to stay
> positive — so descent means driving `shape` **negative**, and the optimiser should run into
> `lower = -0.05` rather than find an interior stationary point. **Predicted final
> `shape` = −0.05 (at the bound), reached in ≤ 8 major iterations.**
>
> **PREDICTION P2 — the descent, with its basis.** Baseline CD on this mesh is **0.15297492**
> (`../../A4_ahmed_body.md` §3). A first-order extrapolation along the full bound travel gives
> ΔCD ≈ 0.2396 × (−0.05) = **−0.01198**, i.e. CD ≈ **0.1410**, a **7.8% reduction**. Real curvature
> will cost some of that. **Predicted CD reduction: 4–9%, i.e. final CD in [0.139, 0.147].**
> *(For scale, not as a target: A2 achieved 28.3% in 47 iterations on a 105-DV wing. That number is
> not transferable — this is one DV with a hard bound, and the comparison is offered only so nobody
> reads a single-digit percentage here as underperformance.)*
>
> **FALSIFIERS.** (a) **The objective increases on an accepted step** ⇒ the gradient is not a descent
> direction and the whole item fails, regardless of the final number. (b) **The DV bound is violated
> at the reported optimum** (|shape| > 0.05 + 1e-9) ⇒ infeasible, GATE FAIL. (c) IPOPT stops on
> `max_iter 15` without meeting `tol` ⇒ **GATE REACHED, not PASS**. (d) Final CD outside
> [0.139, 0.147] ⇒ P2 missed; reported as a miss, and the direction matters — above 0.147 suggests
> curvature or a line-search failure, below 0.139 suggests the linear extrapolation understated the
> gain.

### Arm (b) — FD-vs-adjoint at the FINAL design point

`check_totals(step=1e-3, form=central, step_calc=abs)` on the optimised design, in-process,
immediately after `run_driver()`.

> **This is the arm that distinguishes "the optimiser moved" from "the optimiser moved on a correct
> gradient", and it is the single most important measurement in this item.** A descent produced by a
> defective gradient is not a result; a descent whose gradient still verifies at the endpoint is.
>
> **PREDICTION P3: `CD wrt shape` stays inside the ≤5% PASS band with zero sign flips at the final
> design.** Basis: 1.10% at the baseline on stock, and this arm runs on the **patched** image where
> A1's equivalent row reads 0.038%.
>
> **The honest uncertainty, and it is real.** The baseline is exactly where the
> `getRotationMatrix3d` `sqrt(eps)` guard fires — regime 1, which the patch removes. **The final
> design is NOT at the baseline**: normals have rotated, the guard no longer fires, and the
> near-threshold ill-conditioned **regime 2 takes over — and regime 2 is unpatched by design**. It
> was measured at ~1.26% on IDWarp's own `onera_m6` mesh and it *survives* the patch
> (`../../ROOTCAUSE_getRotationMatrix3d.md` §6.4, §4.9). **So arm (b) is also the lab's first direct
> look at a gradient in regime 2 on a real case**, and a result in the 1–5% band rather than the
> 0.04% band would be the expected signature of that, not a failure.
>
> **FALSIFIERS.** (a) >15% or any sign flip ⇒ **GATE FAIL**, and arm (a)'s descent must be
> re-described as unverified at its endpoint. (b) 5–15% ⇒ CONDITIONAL, and regime 2 becomes the
> leading explanation and needs its own arm.

### Arm (c) — Charter-2c trivial baseline: the same optimiser on a sign-flipped gradient

> **Implementation, stated exactly because it must not be mistaken for a different experiment:**
> the objective is registered as `add_objective("scenario1.aero_post.CD", scaler=-1.0)`.
> Multiplying the objective scaler by −1 negates **both** the objective and its gradient as the
> optimiser sees them, which is mathematically identical to feeding the unmodified optimiser a
> sign-flipped gradient. Everything else — mesh, DV, bounds, image, IPOPT settings — is byte-identical
> to arm (a). Capped at **3 major iterations**.
>
> **PREDICTION P4: CD does not descend; it increases, and `shape` moves toward the UPPER bound
> +0.05** — the opposite corner from arm (a). **Predicted verdict: NOT A RESULT (control behaved as
> designed).**
>
> **What it discriminates:** that the harness is capable of *not* descending. Without it, arm (a)'s
> reduction is compatible with a driver that scores any move as an improvement.
>
> **FALSIFIER: CD decreasing in arm (c).** That would mean the descent in arm (a) is not attributable
> to the gradient's sign, and both arms would need re-interpretation.

## 7. Cost ceiling — 60 core-min, hard

| arm | ranks | predicted core-min |
|---|---|---|
| (a) optimisation, ≤15 major iterations (1 primal + 1 adjoint each) | 1 | ~30 |
| (b) `check_totals` at the final design (1 DV ⇒ 3 primal solves), in-process with (a) | 1 | ~3 |
| (c) trivial baseline, 3 major iterations | 1 | ~6 |
| **total** | | **~39** |

Basis: A4 coarse at np=4 took 8 s (primal), 28 s (`compute_totals`), 33 s (`check_totals`); at np=1,
roughly 4× the wall on one rank. **Hard ceiling 60 core-min ($0.051).** If reached, remaining arms
are not launched and the shortfall is reported. Each container is `--rm`, `--cpus=4`,
`--memory=8g`, with an explicit `timeout`, and the Bash tool's own `timeout` parameter is set
generously — the A6 rung sprung that trap today and it is not to be sprung twice.

## 8. What this optimisation will not be able to see

1. **It is 2,777 cells, and that mesh exists only to host a gradient.** Its baseline CD, 0.15297,
   is *not* comparable to the 45,760-cell primal (0.06998) or to experiment. **No drag-accuracy or
   physics claim of any kind attaches to the optimised CD.** The percentage reduction is a statement
   about the optimiser and the gradient, not about Ahmed-body aerodynamics.
2. **One design variable is not shape optimisation.** It is a single break-line height. Nothing here
   generalises to the 96- or 105-DV problems the ladder's other cases carry.
3. **No constraints exist**, so nothing is learned about constrained convergence, and the "optimum"
   is expected to be a bound, where the gradient need not vanish and optimality is a KKT condition
   with a bound multiplier rather than `‖∇f‖ → 0`.
4. **The decomposition defect is invisible at np=1 by construction** — and it is the defect that
   makes this case's np=4 gradient wrong. A parallel optimisation of this same case would be a
   different and, on present evidence, unsound experiment.
5. **The limiter axis is not varied.** A4's `fvSchemes` will be audited from disk and reported.
6. **Regime 2 is entered but not isolated.** Arm (b) measures the gradient at a deformed state; it
   does not separate regime-2 error from mesh-quality degradation or from ordinary FD truncation.

## 9. Verdict vocabulary

PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING. Shipped- and patched-toolchain
verdicts are reported as separate rows. **An optimiser that stops on the iteration cap without
meeting tolerance is GATE REACHED at best, never PASS.**
