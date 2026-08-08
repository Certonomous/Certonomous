# Zero-compute diagnostics — 2026-08-08

Executes the three zero-compute diagnostics approved out of the supervisor's
negative-verdict review of 2026-08-07 (entries 3 and 5): the F5c inlet-development
audit (`f5c-inlet-development-audit`), the F8 BEM torque bound
(`f8-bem-torque-bound-at-sequence-s`), and the S10/S12 monitor-standard replay
(`f8-s10-replay-of-the-mrf-limit-cycle`). No solver was launched anywhere in this
record; every number below comes from a file already on disk, from arithmetic, or
from a fetched published document. The docket carries these three items; docket.json
itself is another agent's uncommitted working file this session and is deliberately
not touched — the per-item updates are recorded here and in the filed proposal.

---

## Task 1 — F5c backward-facing step: inlet-development audit

### Pre-registered reference (stated before reading our fields)

From Driver & Seegmiller (1985), AIAA J. 23(2):163–171, as carried in the case
record (`F5bc_unsteady_statistics.md` §Reference, retrieved from the primary source
via the NASA TMR mirror 2026-07-28/29):

- Boundary-layer thickness at x/H = −4 (the paper's own U_ref station):
  δ = 1.9 cm against h = 1.27 cm → **δ/h = 1.50** (stated "≈1.5H").
- Inlet momentum-thickness Reynolds number **Re_θ = 5,000**; Re_H = 36,000.
- Reattachment x_r/H = 6.26 ± 0.10.
- The experiment states δ with "≈"; no tolerance is published. **Adopted tolerance
  for this audit, declared here: ±10% on δ/h** (the precision of the "≈1.5"
  statement), assessed at the same station the experiment states it.

### Inlet as-built (from `sdk/workflows/backstep_case.py`, the committed case module)

- Mean profile: 1/7-power-law, `codedFixedValue`, **δ = 1.5H imposed exactly at
  x = −4H** — the same station the experiment quotes (lines 27–33, 124, 351–371).
- Turbulence: **uniform** k/ω across the inlet plane (Tu = 2%, μt/μ = 10) in every
  archived run; the equilibrium-BL k/ω profile exists in the module only as an
  unrun `--inlet-bl-turbulence` sensitivity arm.

### The arithmetic

| quantity | required (D&S) | as-built | deviation |
| --- | --- | --- | --- |
| δ/h at x/H = −4 | 1.496 | 1.500 (imposed) | **+0.3%** |
| Re_θ at x/H = −4 | 5,000 | 5,250 (1/7-law: θ = 7δ/72 = 0.1458H × Re_H) | **+5.0%** |
| Re_θ at the step lip | ~5,460 (equilibrium growth: dθ/dx = Cf/2, Cf = 0.025·Re_θ^(−1/4) = 2.97×10⁻³ over 4H) | **4,768 — measured on the archived baseline coarse solve** (documented in `backstep_case.py` lines 379–386) | **−4.6% vs 5,000; ~−13% vs equilibrium growth** |
| δ/h at the step (1/7 shape from measured θ) | ~1.5–1.55 | ~1.36 | **−9 to −12%** |

The inlet is **clean at the reference station** (+0.3% in δ/h, +5% in Re_θ — well
inside the adopted tolerance). Over the 4H fetch the layer loses ground instead of
growing, because the imposed profile arrives with no turbulence inside it (the
module's own measurement: peak k at the lip about half the equilibrium value); at
the step it sits at the edge of the ±10% band. That is a real, documented blemish
with an already-built repair (`--inlet-bl-turbulence`), but it is a ~10% effect on
the incoming layer — nothing in it can manufacture a 4–12× reattachment error.

### The finding that overrides the audit's premise

**The 4–12× number the review's entry 5 is built on is already refuted inside this
repository, and neither the verdict record nor the review was ever updated.**
Commit `fe121af2` (2026-07-31) documents, in `backstep_case.py::parse_wall_raw`,
that the original F5c detector read OpenFOAM's `wallShearStress` with the sign
backwards: on a lower wall the function object returns τ_x **negative** under
attached forward flow (`ssp = (−Sfp/magSfp) & Reffp` with
`Reff = −nuEff·devTwoSymm(grad(U))`), so the neg→pos crossing the detector called
"reattachment at 0.5–1.5H" was actually the downstream edge of the secondary corner
eddy, and the "unexplained second separation at ~6–8H persisting to exit" was the
real reattachment followed by ordinary attached flow. The archived control run
(`F5c_runs/sign_convention_control/`, plain channel, no step) proves the
convention empirically: attached forward flow, τ_x negative at every one of the 100
wall faces (`evidence/wallShearStress_bottomWall_iter322.raw`). Under the corrected
sign the same solutions reattach at the **≈5.6–8H** crossing family the record had
mislabelled — the SIMPLEC coarse case at x_r/H ≈ 5.6, **−10.5%** against 6.26±0.10,
i.e. inside the documented linear-eddy-viscosity underprediction family, not 4–12×
outside it. Two caveats stated plainly: (i) no corrected-detector run record was
ever archived — the ≈5.6 lives in the committed docstring, and the original runs'
raw profiles are gone (postProcessing is gitignored; scratch dirs no longer exist),
so re-collection on an `xr-*` rung is needed to put the corrected number on the
evidence rails; (ii) the coarse-mesh face spacing near x/H = 6 is 0.55–0.81H, so
the pre-fix levels could not have adjudicated the ±0.10 band anyway (the
`x_resolved` levels added in the same commit exist for exactly this).

### Verdict — Task 1

**Inlet is clean at the experiment's own reference station (δ/h +0.3%, Re_θ +5%,
inside the declared ±10% tolerance); mildly under-developed at the step (−9 to
−12% in δ/h, owned by the uniform-k inlet, repair already built and unrun).** The
classic BFS inlet trap is NOT the mechanism. But the review's fork is mis-posed:
the "4–12× reattachment error" it sends to the unsteady-probe arm does not exist —
it was an instrument sign-convention defect, corrected in code on 2026-07-31 and
never propagated to `F5bc_unsteady_statistics.md`, the NOT_PASSING register, or
review entry 5. The genuinely open physics question is the remaining ≈−10%
underprediction plus the SIMPLEC wandering (non-monotonic 1.07–1.49H pre-fix
readings — which under the corrected sign are wandering of the corner-eddy edge,
with the primary reattachment's own wandering not yet measured cleanly).

**Which way this moves the record:** F5c moves from "converged solves 4–12× wrong,
mechanism unknown" to "detector defect, corrected; residual ≈−10% deviation;
inlet exonerated at the reference station". Before any solve is spent: (1) amend
`F5bc_unsteady_statistics.md` and the review's entry 5 with the sign-convention
correction — the record currently contradicts the committed code; (2) the
unsteady-probe arm (`f5c-unsteady-probe-run`) stays live, now aimed at the honest
target (the ≈−10%+wander family on an `xr-*` detector-resolved mesh), and one
`xr-coarse` re-collection would simultaneously archive the corrected x_r and the
inlet-turbulence sensitivity arm at ~25 core-min as already filed.

---

## Task 2 — F8 NREL Phase VI: zero-compute BEM torque bound at Sequence S

Pre-registration: the method, geometry source, polar source and arm list were
written into the header of
`F8_runs/bem_analysis/bem_sequence_s.py` before the integrator was first run. The
+800 N·m reference was already in context (it is in the proposal text); what is
pre-registered is the calculation, not blindness to the target.

### Inputs and their provenance

- **Conditions** (the case on disk): U = 7 m/s, Ω = +7.5398 rad/s (72 RPM),
  ρ = 1.225 kg/m³ (the bladeForces `rhoInf`), R = 5.029 m, B = 2 →
  **λ = 5.42** (Sequence S, TP-500-29955 Table C-18).
- **Geometry**: Hand et al. 2001, NREL/TP-500-29955, **Table A-1 in full** (fetched
  from the OSTI full text 2026-08-08) — the same table the F8 record's §10 STL
  audit verified against the case geometry to 2–3 mm chord. Twist datum: zero at
  the 3.772-m station; tip (5.029 m) twist −1.815°.
- **Polars**: NREL S809, AERODAS parameterisation of the TU Delft measured
  pre-stall data — Spera, NASA/CR-2008-215434 (2008), Table 5 "S809 Smooth"
  (+2012 errata for eq. 12b). Chosen because it is a published, closed-form,
  citable representation of the measured polar, and because the same report
  validates BEM+these-polars against this exact turbine at 72 RPM: −1.3% ± 4.0%
  over 54 measured power points.
- **Method**: standard annular BEM, a/a′ iteration, Prandtl tip+hub loss, Buhl
  correction above a = 0.4; root cylinder (0.508–1.257 m) excluded from the
  lifting integral and charged as a Cd = 1.0 drag penalty.
- **Pitch convention, run as two arms** because §10 left it open: Sequence S tip
  pitch 3° referenced to the tip chord (θ = twist + 4.815°) versus referenced to
  the zero-twist station (θ = twist + 3°). Side finding: the tip-chord convention
  reproduces the §10 STL audit's "+1.8° uniform offset" **exactly**
  (19.1/5.9/3.3° measured vs 17.3/4.1/1.5° for twist+3°; twist_tip = −1.815°),
  so the offset §10 attributed to "measurement bias and/or ≤2° of pitch" is most
  simply the pitch convention itself, and the as-built STL sits at the correct
  Sequence S setting. This does not move any §10 conclusion (chord, twist span,
  handedness, camber all still verified); it sharpens it.

### Result (`F8_runs/bem_analysis/bem_result.json`)

| arm | Q (N·m) | Q incl. root drag | P (kW) | thrust (N) |
| --- | --- | --- | --- | --- |
| A: tip-chord pitch, 2D polar + tip loss (primary) | **+748.8** | +724.8 | 5.65 | 1150 |
| B: station-ref pitch, 2D polar + tip loss | +775.6 | +751.7 | 5.85 | 1280 |
| C: tip-chord pitch, Spera AR-15.28 polar, no tip loss (his method) | +792.7 | +768.7 | 5.98 | 1132 |
| D: arm A with Cd × 1.5 | +710.0 | +686.1 | 5.35 | 1152 |

Every arm is **turbine-signed (+Mx for +ω) and fully attached**: angle of attack
4.8–8.2° across the entire S809 span (stall at ACL1 = 14–15.7°), Cl 0.68–0.92,
axial induction a = 0.13–0.26. The polar/pitch/drag sensitivity band is
**+686 to +793 N·m**, i.e. −14% to −1% of the +800 N·m secondary-tier reference
(Processes 12(9):1994 Table 6, digitised from Hand et al. 2001; corroborated by
Spera fig. 7: measured rotor power ≈5.5–6.5 kW at 7 m/s → Q ≈ 730–860 N·m).
BEM thrust 1130–1280 N also brackets the experiment's ≈1.2 kN (§10), where the
CFD's stalled solution reads +811 N.

### Verdict — Task 2

**BEM ≈ +750 ± 50 N·m, unambiguously turbine-signed and attached at λ = 5.42 —
the review's fork resolves to outcome one.** An attached-flow steady solution
exists in principle and delivers the published torque to within the polar
uncertainty; blade-element theory is not ambiguous at this tip-speed ratio. The
persisting motoring limit cycle (window means −1004 to −1037 N·m across the
original and arm-A runs) is therefore **numerical/basin behaviour of the steady
SIMPLE+MRF solve** — the solver is trapped in a stalled basin that the physics
does not require — and not evidence that the flow refuses a steady description.

**Which way this moves the record:** the transient branch keeps its inherited
quantified target (settle turbine-signed within the 400 N·m band of 800) and now
carries the bound that makes the target fair: the attached solution it is hunting
exists at blade-element order. Any future steady-solver rescue attempt
(pseudo-transient, relaxation continuation, initialised-from-BEM velocity field)
has the same +750 N·m target; and the §10 pitch-convention side finding should be
appended to the F8 gate record when it is next amended.

---

## Task 3 — S10 specimen: monitor-standard replay against the archived F8 history

The specimen: `F8_runs/phase6_mrf_pfinit` (gate record §12) — blade moment
diverging exponentially from −1.5×10⁴ N·m at t=50 to −2.5×10⁹⁹ at t=1500 while
the final momentum residuals read 1.0–1.4×10⁻⁸. Replayed with the lab's own
detector functions from `sdk/chief_engineer/log_signatures.py`, verbatim, no
threshold changes (`F8_runs/s10_replay/replay_s10_s12_pfinit.py`, artifact
`replay_result.json`). The original `phase6_mrf` limit cycle replayed alongside
for contrast.

### Clause-by-clause: the standard as written does NOT catch the specimen

| rule / clause | fires? | the measured reason |
| --- | --- | --- |
| **S10a** ceiling clip ("clipped at the TOP of its permitted range") | **no** | all 692 bound lines are `bounding nuTilda, min: −…` — classic **floor** bounds; `classify_bound_line` direction test excludes them by design. Zero ceiling clips in the log. |
| **S10b** normalisation collapse ("at or below 1e-20 for 100 consecutive iterations") | **no** | smallest normalised residual anywhere in the log is **1.86×10⁻⁹** (Uy) — eleven orders above the floor. The A4 mechanism (ratio collapsing because its denominator blew up) never happened here; the tiny momentum residual is a genuine ratio of a huge, self-consistent velocity field. |
| **S10c** residual-norm contradiction ("where a solver prints unnormalised residual norms") | **no** | simpleFoam prints no such block — the branch's required input does not exist for this solver family. |
| **S12** unsettled stop, on the Mx history | **no — twice over** | (1) the history holds **30 samples** (writeInterval 50) against `UNSETTLED_MIN_ITERATIONS = 40`: the detector returns None before grading anything. (2) Counterfactual with the floor removed: rel_drift = **−2.0** (2000× the 1e-3 tolerance) but monotone fraction = **0.789 < 0.90** — the AND clause fails because exponential divergence rides on the oscillation. S12's own doctrine ("a settled history wobbles, a truncated one travels") has no branch for "explodes". |
| **rail** | **no** | `sdk/scripts/replay_s12_unsettled_stop.py` builds its corpus from `rglob("coefficient.dat")` only — forces-object `moment.dat`/`force.dat` histories, including this specimen, never enter the archive-replay rail at all. |
| S1 / S2 | no | no FPE handler frame, no NaN on a solver line (the values stop at 10⁹⁹, below double overflow). |
| S4 bounding | FLAG-class | 692 nuTilda floor bounds persisting to the end — but §3.5's finding stands: the implemented S4 carries no severity ladder. |
| S6 residual stall | **FLAG** (p and nuTilda) | with the case's declared `residualControl` 1e-4, `detect_residual_stall` fires on p (final 0.51) and nuTilda (0.082). True, and a category miss: it says "UNCONVERGED, prescribe the regime check" — the same thing it says about a mild stall — while the monitored quantity sits at 10⁹⁹. |

One correction to the gate record's own wording: §12's "converged to any
residual-only monitor" is too strong — p at 0.51 is loudly unconverged and S6
FLAGs it. The precise statement, and the one that indicts the standard, is:
**the momentum residual reads deeply converged, the flags that do fire say only
"unconverged", and no rule in the standard converts a monitored quantity at 10⁹⁹
behind a 10⁻⁸ residual into a FATAL.** For contrast, on the original limit cycle
(60 samples) S12 grades and correctly stays silent (monotone 0.53 — oscillation,
not travel), matching the gate record's §3.

### Verdict — Task 3

**NO CATCH.** Every clause of S10 fails to bind for a measured, structural reason
(wrong bound direction, wrong floor regime, missing input block), S12 fails on its
length floor and then on its monotone clause, and the archive-replay rail cannot
even see the history. The standard's strongest failure class has a solver family
(plain OpenFOAM, no norm block, floor-bounding turbulence variable) it is blind to.

**Minimal amendment — proposed, not applied**, filed per the intake convention as
`agenda/proposals/s10d-monitored-quantity-magnitude-explosion.json` with its
pre-adoption replay line already attached (standing rule 6):

> **S10d, magnitude explosion in a monitored quantity.** Over the history with the
> first 10% of samples excluded as startup, let m = median |q| of the first half of
> the remainder. FATAL when |q_final| ≥ 10⁶·m AND the last five magnitude steps all
> increase. Second clause: the S12 replay corpus glob adds forces-object
> `moment.dat`/`force.dat` histories.

Replay line (`F8_runs/s10_replay/s10d_corpus_replay.py`, artifacts committed):
**974 histories** graded across both corpus roots (194 under demo-output, 780
under certonomous-runs); **fires on exactly 5**, all from runs the record already
names diverged — the two F8 specimen histories (83.3 and 84.5 orders; caught by
nothing today) and three dpw5-committee-probe histories (20.9–29.5 orders) from
runs recorded "diverged, signal 8" (an S1 overlap of the same acceptable kind S3
has). **Zero completed-run false positives.**

**Which way this moves the record:** the S10 specimen did its job — it is the
second real member of the divergence-behind-a-converged-residual class and the
first the standard misses, which is exactly what the archive-replay rail exists to
surface. The standard is wrong in a named, repairable way; adoption of S10d goes
through the innovation path with the replay line above as its evidence.

---

## Costs

| task | solver core-min | external fetches |
| --- | --- | --- |
| 1 — F5c inlet audit | 0 | none (all repo-internal) |
| 2 — F8 BEM | 0 (pure arithmetic) | TP-500-29955 full text (OSTI), NASA/CR-2008-215434, Processes 12(9):1994 |
| 3 — S10/S12 replay | 0 (file reading) | none |
