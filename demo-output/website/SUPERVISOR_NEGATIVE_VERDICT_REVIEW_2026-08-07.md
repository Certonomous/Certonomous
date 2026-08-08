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

**Outcome (2026-08-08, chief review of the executed QCR arm):** null — reattachment 7.6814 vs
SST's 7.6472, +0.034 x/h against a 0.10 bar, away from the 4.21–4.7 band; the +72% FAIL stands
untouched (results 2544c9af; the resized 12,000 cap earned its keep at 6,177 iterations — the
inherited cap would have guillotined the run 177 iterations short). Combined with the hump null
and the ducts' decisive win, the record now carries a three-leg class sentence: QCR2000
resurrects anisotropy-driven secondary flow and does not touch 2D separated-shear-layer bubble
length. **Chief caveat before that sentence hardens:** both separated-class legs are NULLS, and a
null from a silently inactive model is indistinguishable from a null from real physics — an
independent QCR-activity check (fields differ between SST and QCR runs by more than roundoff,
model selection verified in the archived dicts, by an agent that ran neither) is ordered as the
adversarial defense; the class sentence is provisional until it reports.
**Hold LIFTED (same day, 1a14e90b):** the check returned ACTIVE on both legs with the strongest
possible evidence class — selection lines and Ccr1 banners in both logs, wall-shear deltas of
8.97%/18.8% max on identical grids, and the confound-closers: pressure extrema and internal |ΔU|
move too (up to 4.9% of Ubar on the hills), which no stress-definition formula can produce, plus
the momentum-equation wiring cited to kOmegaSSTQCR.C:142-154 through UEqn.H:9. Fields materially
different + reattachment unmoved = the nulls are physics. The class sentence STANDS as a
record-grade finding: QCR2000 resurrects anisotropy-driven secondary flow and does not touch 2D
separated-shear-layer bubble length. The hills model-form matrix (~35 core-min) is next in the
family queue.

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

**a1-arm outcome (2026-08-08, chief review):** OUTCOME ONE — mechanism. The converged a1=0.34 arm
moved reattachment −0.0498 x/c toward experiment, five times the materiality bar, while still
failing Gate P at +9.4% (the pre-registration predicted exactly this shape: material movement
without a pass). Reconciled against the registry's previously-uncited 2026-08-01 a1 arms
(a1=0.40 converged at 1.1873; a1=0.25 not converged — citation defect dated by the runner), the
converged curve 0.31→0.34→0.40 is monotone and sublinear: d(reatt)/d(a1) ≈ −1.66 per unit a1
just above stock, flattening to −0.27 beyond — the stress-magnitude route now carries a named
knob with a measured slope, and the low-a1 convergence pathology is reproduced at a second value.
The omega-budget implication from the QCR null is upgraded to a mechanism-backed finding,
subject to the same QCR-activity check ordered under entry 1. — steady-MRF closed three ways, motoring limit cycle persists
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

**Outcome (2026-08-08, chief review of both executed diagnostics — 6d806733):** the BEM
cross-check RESOLVED THE FORK: four pre-registered arms spanning pitch convention, polar
treatment, and Cd+50% give Q = +686 to +793 N·m turbine-signed, fully attached (α 4.8–8.2°,
a ≤ 0.26) at λ = 5.42 — an attached steady solution exists in principle within −14% to −1% of the
+800 N·m reference, so the motoring limit cycle (≈−1004 N·m) is solver basin behavior, not
intrinsic unsteadiness. The transient branch keeps its ≤400 N·m target with the bound now
independently confirmed, and the BEM's tip-chord convention reproduced §10's "+1.8° STL offset"
exactly, closing that ambiguity. The S10 replay found the OPPOSITE of comfort: NO CATCH, five
clauses deep — every detector as written stays silent on the archived divergence (floor-bounds
masking, residual eleven orders above the S10c floor, sample-count floor, monotonicity ridden by
oscillation, and a corpus glob that never ingests the history at all); the gap that converts
"Mx = 10⁹⁹ behind a 10⁻⁸ residual" into FATAL simply does not exist. The filed S10d
magnitude-explosion amendment arrives with its adoption evidence already attached (974 archived
histories replayed: fires on exactly the 5 genuinely diverged runs, zero false positives) —
CHIEF-ENDORSED for adoption; application routed to the Infra family with the corpus widening.
One overstatement to correct in the F8 gate record: §12's "converged to any residual-only
monitor" — p sat at 0.51 and S6 does flag it; the true gap is the FATAL conversion (dated note
ordered).
**S10d ADOPTED (same day, a217d393):** the Infra family re-ran the full replay with its own hands
— 974 histories, fires on exactly 5 (the two F8 specimens at 83–85 orders of magnitude, plus
three dpw5-committee-probe histories at 21–30 orders, verified genuinely diverged on their own
records), zero false positives across 969. MONITOR_STANDARD v1.4; the corpus rail now ingests
forces-object histories so the specimen class can never again sit outside the glob; suite 1182/0
with the specimen firing from its own file on disk in the test set. One evidence discrepancy was
found and resolved honestly (the archived replay JSON held only half the corpus; the full claim
lived in prose — the rerun confirmed both halves and the numbers now live in the structured
record). The S6/S4 FATAL-conversion question was judged closed by S10d itself, with the
revisit condition written into the standard. This thread — from "does the standard catch our own
specimen?" through NO-CATCH-five-clauses-deep to an adopted rule with a reproduced replay line —
is the archive-replay charter working end to end.

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

**Outcome (2026-08-08, chief review of the executed audit — 6d806733): this entry's premise was
dead on arrival, and the audit is what found it.** The 4–12× reattachment error NEVER EXISTED:
commit fe121af2 (2026-07-31) had already proven it was the OpenFOAM wallShearStress sign
convention (lower-wall τ_x is negative under attached flow; the archived sign_convention_control
run is the proof), giving a corrected x_r/H ≈ 5.6 = −10.5% vs Driver–Seegmiller — and neither
`F5bc_unsteady_statistics.md` nor this review entry was ever updated. A finding proven in the
repo nine days ago was still being treated as an open mystery by the chief's own review; this is
the strongest argument yet for the case-integrity/record-reconciliation discipline entry 6
proposed. The inlet itself: clean at the reference station (δ/h +0.3%, Re_θ +5.0%, inside the
declared ±10%), mildly under-developed at the step (Re_θ −4.6%), owned by the uniform-k inlet
whose equilibrium-k repair already exists unrun (`--inlet-bl-turbulence`). Rulings: (1) the
record correction is ordered — F5bc_unsteady_statistics.md gets the dated sign-convention
amendment; (2) the unsteady-probe arm STAYS LIVE but retargeted at the honest question: a −10.5%
steady miss with wander, not a 4–12× catastrophe — its pre-registration must be rewritten against
the corrected numbers before launch, and the equilibrium-k inlet repair becomes its cheap first
leg.

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

**Outcome (2026-08-08, chief review of the executed arm — 54a2f2ff, docket c6f4644f): NOT
EVALUABLE, the pre-registered branch fired, and the arm earned its cost three times over at 0.53
of 30 core-min.** DAFoam's mesh gate rejected the archived vcoarse mesh before any iteration ran:
23 negative-volume cells, aspect ratio 2.08e+95, non-orthogonality 135.3° — adversarially
defended (standalone checkMesh reproduces every figure; the preserved July-28 decomposition
carries the identical 23 negatives to the last digit). The mesh was born broken by the pyHyp tip
collapse on the 4× coarsened surface — which makes it a SECOND SPECIMEN of entry 10's
generator-owned aspect-ratio pathology, on a different geometry. Larger finding: **`
transonicPCOption: 2` is dead code for DARhoSimpleCFoam** (only `== 1` exists at
DAResidualRhoSimpleCFoam.C:173; `== 2` lives in the Turbo solver) — every archived M6 script set
2, so NO archived M6 adjoint ever ran with an active transonic preconditioner, and the A3
"conditioning wall at every mesh size" was measured entirely with that lever silently off. The
liaison's lead is thereby upgraded from "never set" to "set but inert". Also en route: the
record's "SEGV during decomposePar" rediagnosed as two orphan autoPatch patches unmapped by the
tutorial createPatchDict — the old wrapper ran the solver on half-written processor dirs.
**Chief ruling — the RE-FILE is approved:** the same two levers (sub-LU + transonicPCOption: 1,
now known-active) on the 21,840-cell archived sweep mesh, which passes the mesh gate and matches
the proposal's cost basis, ~30 core-min. The question entry 8 asked is still open and now sharper:
the wall has never been probed with the preconditioner actually on.

## 9. Model-form family B (bump) — no band, all four closures stall
The archived rung never met residualControl either. **New diagnostic:** [FILE] one diagnosis arm
(~15 core-min): the bump at doubled iteration cap with per-quantity settle monitoring — decides
"slow but convergent" vs "genuinely stalled", which decides whether family B gets a band or a
documented exclusion. Criterion: instrument-check.

## 10. TMR NACA 0012 — aspect-ratio pathology under refinement (generator-owned)
Standing finding (`GENERATOR_FINDING_pyhyp_aspect_ratio.md`). **New diagnostic:** [FILE] one mesh
from an alternative generator (blockMesh C-grid per the TMR recipe or gmsh) at matched cell count:
if the ladder behaves, the generator owns the pathology and the family unblocks. ~20 core-min.
*(2026-08-08 note: the A3 arm under entry 8 surfaced a second specimen — the archived M6 vcoarse
mesh was born with 23 negative-volume cells and aspect ratio 2.08e+95 from the pyHyp tip collapse
on a 4× coarsened surface. The pathology is now cross-geometry; this diagnostic's priority rises
accordingly.)*

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

**Outcome (2026-08-08, chief review of the executed arm):** the under-membership reading was
correct. SA converged under the adjusted-but-preregistered criterion (pre-reg 9374f807 at
02:01:52Z, launch 02:02:02Z — ordering proven by the runner quoting the prereg path; outcome
06b78343) at 1.07 of 10 core-min, bit-identical to the archived excluded run. At n=3 the Cl band
[1.0290490, 1.1164337] CONTAINS CFL3D's 1.0778081; the third member entered 0.051 BELOW the old
floor — the n=2 band under-stated the Cl spread by 2.4×, which is the quantitative version of
"an n=2 band is a lower bound on the true spread". The declared branch fired: the rule proposal
`no-containment-verdict-below-n3` is filed (instrument-check, archive replay as its adoption
gate). Bonus finding: the arm exposed a wrapper defect — the runner stamped `admitted: true` and
excluded anyway (the C1-fix conservatism outranking the registered criterion); fixed, with the
wrong record superseded-not-deleted and a correction block naming the chain. I endorse the rule
proposal for adoption once its archive replay runs: no containment verdict, pass or fail, below
three converged members.

## 12. (Added 2026-08-08) S1 reinversion — G1 PASS, G2 FAIL (26.9% vs the pre-registered >50%)
The reinversion on the repaired inlet (records in `dafoam/ladder-b/S1_CBFS_REINVERSION_*.md`)
passed G1 decisively (−74.2% where the corrupted objective managed −0.149%) and failed G2 — but
the failure DECOMPOSES, and the decomposition is the finding: window error −94.9%, near-wall
−95.9%, with 77.6% of the residual loss sitting at y>2 where the reference-level mismatch lives,
and the optimizer was budget-capped still descending (J_qoi 0.25847 at eval 16). Two hypotheses
survive: budget-limited (it would have gotten there) or loss-placement (equal-weight training
spends effort where the metric doesn't look — the same relocation mechanism entry 7 caught in the
closure family, now measured a second way; the limiter-overlap growth to 51.6% of the top decile
is the second Dow-style argument).
**New diagnostics:**
- [FILE] The entry-7 weighted-loss variant EXTENDED to the S1 objective, offline and validation-
  only first (~0 solver core-min, sklearn-class): re-weight the existing eval-16 residual field by
  window/near-wall membership and ask whether the achieved β field already contains the window
  answer under a loss that looks at it. This is now the highest-information-per-core-min arm in
  the family — two independent measurements point at it. If it says the window is capturable, a
  weighted REINVERSION arm (priced separately, ~250 core-min class) gets filed; if not, G2's bar
  itself is interrogating reference-level mismatch, not model correction, and the bar needs a
  documented revision proposal — not a quiet one.
- [FILE] Continuation arm, second priority: warm-start from beta_final under the same lambdas
  with a pre-registered plateau stop rule — decides budget-limited vs structurally-stuck directly,
  but at ~26 core-min/eval it waits behind the offline variant's answer.
- The agent's own named follow-up (TV regularization term) stays filed as-is.
**Stage-2 ruling (the hand-off was flagged to me):** Stage 2 HOLDS until the offline weighted-loss
variant reports. Training an ML generalizer on a β field known to under-serve the window would
bake the placement defect into the learned model; the variant is cheap and decides within the day
whether Stage 2 trains on this β or on a weighted successor's. Training-legality is unaffected
(CBFS is a training case; nothing scored).

**Outcome (2026-08-08, chief review of the executed variant):** CAPTURABLE, decisively — R_W1
0.9494 and R_W2 0.9468 against the 0.70 pre-registered bar (pre-reg 2c475ab5 committed before any
weighted number existed; results 71dbf5a8), with the hurt cap clean where it binds (near-wall
hurt exactly zero). The relocation census makes entry 7's mechanism concrete here: 35.0% of gross
reduction was spent HURTING y>2 — but outside the physics regions, exactly where the equal-weight
loss pointed the effort — and the trajectory decomposition shows it temporally (in/out-window
effort ratio 11.2 → 3.7 after J_qoi passed ~0.44: window harvested first, then the pivot). The
Wu/Zhang-style sparse-point proxy agrees with the primaries (0.9340). The agent also disclosed
and corrected a labeling error pre-compute: the FD "neighborhood spread" claim was a
serial-vs-DV-index confusion (the FD values stand; all three verified cells are in the separated
shear layer; dated retraction on the result doc).
**Chief rulings on the recommendation:**
1. The weighted reinversion arm (`s1-cbfs-weighted-reinversion-arm`, 250 core-min) is APPROVED,
   with its own pre-flight as filed and in this order: the ~8 core-min masked-β nonlocality
   control FIRST — it is the one thing offline analysis cannot rule out, and if the in-window fix
   turns out to ride on out-of-window β through the flow, the arm's premise weakens and it comes
   back to me before the 250 is spent — then the FD gate on the new objective configuration, then
   pre-registered optimization under the same budget-guard discipline that served S1.
2. NO G2-bar revision, agreed: the bar caught a real property of the equal-weight loss. The fix
   belongs in the loss, and the record now says so with numbers.
3. Stage 2 REMAINS HELD until the weighted arm delivers its β; if the arm's gates pass, Stage 2
   trains on the weighted successor's field, not eval-16's.
4. The continuation arm is now DEPRIORITIZED below the weighted arm permanently — capturability
   answered the question the continuation arm was priced to answer.
