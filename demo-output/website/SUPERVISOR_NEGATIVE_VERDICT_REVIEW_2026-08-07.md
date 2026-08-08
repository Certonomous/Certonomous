# Supervisor review of every standing negative verdict — 2026-08-07

Written personally by the chief supervisor under Katie's directive of 2026-08-07: anything that
closed with a negative verdict gets a supervisor review proposing new diagnostics, recorded here.
Each entry: the verdict as it stands, what it actually taught, and the new diagnostics I propose,
each costed and carrying its hardness/source rationale. Diagnostics marked [FILE] go to the docket
as proposals; the filing mechanics are delegated, the judgments are mine.

## 1. F6b periodic hills — physics FAIL (+72% reattachment vs the Rapp/Breuer/Fröhlich band)
Verified on our own mesh (0.043% agreement with the shipped grid, 0.097% grid sensitivity), so the
failure is the model's, not ours. Taught: SST overpredicts separated-region length on the hills the
same way it does on the hump — a two-leg pattern.
**New diagnostics:**
- [FILE] Model-form matrix on the hills (extend the standing batch's family set): do any of the four
  closures enter the literature band, and does the inter-model band contain it? ~35 core-min at the
  medium rung. Criterion: existing-family; feeds the epistemic-uncertainty showcase directly.
- [FILE] QCR2000 on the hills (~12 core-min): the ducts proved QCR resurrects missing physics cheaply;
  the hills' failure is APG separation, where anisotropy also matters. Either outcome instructive:
  improvement implicates constitutive form, no change implicates the omega budget.
- The finest-rung non-convergence discriminator is already filed (`f6b-why-the-finest-hill-will-not-converge`, 55) — unchanged.

## 2. F6a NASA hump — bubble-length overprediction (pass with asterisk)
Same family as (1). The model-form matrix at challenge conditions is already approved
(`w1-hump-challenge-conditions`, 60). **New diagnostic:** [FILE] add a QCR arm to that run when it
executes (marginal cost ~8 core-min) so the two-leg pattern gets the same constitutive probe on both legs.

**Outcome (2026-08-08, chief review of the executed arm):** both diagnostics ran at challenge
conditions (pre-reg 74797a57, results 9d711efb). Gate V passed against the verified F6a answer to
the fourth digit; Gate P failed on reattachment at +13.92% — inside the +12–16% window the
pre-registration predicted, so the two-leg SST bubble bias is now CONFIRMED at challenge
conditions, not merely carried over. The QCR arm returned outcome two: +0.0022 x/c AWAY from
experiment against a 0.010 materiality bar — the constitutive/anisotropy route is ruled out on the
hump leg, and the omega budget (separated-shear-layer stress magnitude) is implicated. Set against
the ducts, where the same untrained QCR was decisive (0.0811→0.0455), this is a clean separation
of "anisotropy missing" (ducts) from "shear stress mis-scaled" (hump). The hills leg
(`f6b-qcr2000-on-the-hills`) stays pending and now carries more weight: it decides whether the
separation generalizes.
**Next diagnostic:** [FILE] a1 shear-stress-limiter sensitivity arm on the hump (~6 core-min at
the now-measured price): single parameter, identical mesh — if reattachment moves materially with
the limiter, the mis-scaled-stress hypothesis gains a mechanism, not just an implication; if it
does not, the budget question moves upstream to the omega production/destruction balance.
Criterion: existing-family; the pre-registration must state a materiality bar before launch.

## 3. F8 NREL Phase VI — steady-MRF closed three ways, motoring limit cycle persists
Geometry exonerated to the millimeter, frame terms audited to source lines, initialization tested
single-variable. Taught: the steady branch cannot host this physics, and the S10 divergence-behind-
a-converged-residual specimen is real. **New diagnostics:**
- [FILE] Zero-compute BEM cross-check: compute the blade-element expected torque at Sequence S
  (published S809 polars + the verified chord/twist) to bound what ANY attached-flow steady solution
  could deliver. If BEM says ≈+800 N·m, the limit cycle is numerical/basin; if BEM itself is
  ambiguous at λ=5.4, the case is intrinsically unsteady and the transient branch is not optional.
  Criterion: instrument-check.
- [FILE] The S10 specimen goes to the monitor-standard replay corpus (the archive-replay rule the
  charters now enforce): does S10/S12 as written catch this run's history? 0 core-min.
- The transient branch inherits the quantified target (turbine-signed, ≤400 N·m band) — already filed.

## 4. B52 — the ladder is noise (increment 15% of the measured 1.91e-3 floor)
Taught: the family's question was answered; the remaining question is the floor's origin.
**New diagnostic:** [FILE] two same-recipe replicate meshes at rung 6 (seed-varied snappy), Cd spread
vs the 1.91e-3 floor — the mesh-draw-sensitivity protocol (`w3-a-verdict-protocol...`) applied to its
second family. ~14 core-min. If replicates reproduce the floor, the recipe owns it (castellation);
if not, the floor is iteration-history noise and the settle gate needs work.

## 5. F5c backward-facing step — converged solves 4–12× wrong on reattachment, wandering
The OOM premise is dead (our own record refuted it). **New diagnostics, ordered by cost:**
- [FILE] Inlet-development audit first (0 core-min): Driver–Seegmiller's reference has a developed
  boundary layer of stated thickness at the step; verify our inlet reproduces δ/h at the step within
  the experiment's tolerance. The classic BFS trap, and the 4–12× magnitude smells like it.
- [FILE] If the inlet is clean: one unsteady probe run (~25 core-min) — a steady solver on a flow
  with a genuinely unsteady reattachment region wanders exactly as recorded.
- The slate's diagnosis plan (NEXT_CASES_SLATE item 3) stands; these two sharpen its order.

## 6. S1 first inversion — both gates FAIL (objective was measuring a corrupted inlet)
Diagnosed and reinverting. The meta-lesson is the one to institutionalize:
**New diagnostic:** [FILE] case-integrity rule for the standards: any case directory used as a
reference or objective source gets a manifest of input checksums at validation time; any writer to
it invalidates the badge until re-validated. The S1 pilot's write-back would have been caught at
cost zero. Criterion: instrument-check; this is a MESH_STANDARD/VERIFICATION_CHARTER addition, not a run.

## 7. alpha_05 regime model — NO-GO on its own pre-registered cap
The boundary moved instead of vanishing (L-33), and the census showed the correction relocating
error into the metric's blind strip. **New diagnostic:** [FILE] offline, validation-only: a
spatially-weighted loss variant (weight by local truth-magnitude or by the metric's own point
density) trained on the same split — tests whether the relocation is an artifact of equal-weight
training. 0 solver core-min (sklearn-class work). Its pre-registration must state the same hurt-cap
discipline that killed R5's predecessor.

## 8. A3 ONERA M6 — adjoint blocked by conditioning at every mesh size
The block predates the sub-LU tool, and the unblock was never carried to this family. That is a gap,
not a verdict. **New diagnostic:** [FILE] one arm: A3 vcoarse adjoint under DAFOAM_SUBPC_TYPE=lu +
the liaison's transonicPCOption lead (never set on our M6 runs; the official transonic tutorial sets
it). ~30 core-min. If it converges, A3's ladder reopens and the DIVERGED_BREAKDOWN story gets its
epilogue; if not, the conditioning wall is confirmed beyond the incompressible family.

## 9. Model-form family B (bump) — no band, all four closures stall
The archived rung never met residualControl either. **New diagnostic:** [FILE] one diagnosis arm
(~15 core-min): the bump at doubled iteration cap with per-quantity settle monitoring — decides
"slow but convergent" vs "genuinely stalled", which decides whether family B gets a band or a
documented exclusion. Criterion: instrument-check.

## 10. TMR NACA 0012 — aspect-ratio pathology under refinement (generator-owned)
Standing finding (`GENERATOR_FINDING_pyhyp_aspect_ratio.md`). **New diagnostic:** [FILE] one mesh
from an alternative generator (blockMesh C-grid per the TMR recipe or gmsh) at matched cell count:
if the ladder behaves, the generator owns the pathology and the family unblocks. ~20 core-min.

---
Review discipline note: every diagnostic above is falsifiable, costed, and names which way each
outcome moves the record. None requires a scoring call. Filing mechanics delegated to the docket
agent; wording above is binding.

## 11. (Added same day) Family-N a10 band — Cl NOT contained (0.22% below the band floor)
The first N band (post-R12 regrade, 43ac7287) contains CFL3D's Cd but misses Cl by 0.22% — on a
TWO-member band (kOmegaSST, kEpsilon; SA and realizableKE excluded on residualControl). Taught: an
n=2 model-form band is a lower bound on the true spread, and a miss this small at n=2 is more likely
under-membership than model-family failure.
**New diagnostic:** [FILE] one arm (~10 core-min): converge a third member at a10 — SA under an
adjusted-but-preregistered settle criterion (its exclusion was residualControl, not divergence) —
and re-state containment at n=3. If Cl still sits outside, the miss is real and the aero-family
bands need a membership-minimum rule; if it enters, the rule becomes "no containment verdict below
n=3", which is worth having either way. Criterion: existing-family.
