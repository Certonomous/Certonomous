# F7c — DTMB 5415 staging plan

**Written 2026-08-11. Zero compute. No mesh exists, no run exists, nothing is
authorised.** This is a plan for how the case would be staged if Katie buys it,
with the acceptance criterion for each stage fixed **before** any number exists.

**Status of the case itself: BLOCKED.** F7 rung (a) fails its gate
(`F7a_REGATE_SPEC.md` §3: FAIL, +11.03% max), and the standing ladder rule is
that (b) does not start until (a) passes and (c) depends on (b). This plan
does not unblock anything and does not argue for unblocking. It exists so that
if Katie lifts the block — or rules, per R1 §7, that a dry-bed contact-line
failure should not gate a wave-resistance case — the staging is already written
and cannot be drafted to fit results that by then exist.

**Doctrine followed:** the campaign's standard three-stage ladder,
**Feasibility → Physics → Gate**, as recorded for every other case family in
`CAMPAIGN_STATUS.md` and as F7a itself ran. Each stage has one question, one
acceptance criterion, and one named comparison. **A stage that cannot state what
it is checked against does not exist as a stage.**

---

## 0. Why DTMB 5415 and not something easier

It is the hull naval engineers recognise on sight, and its workshop data is the
credibility case for the marine line. That is a go-to-market argument, not a
technical one, and it is recorded as such: the technical argument for staging it
*third* is that it is a full 3D free-surface case with sinkage and trim, and
every one of those is a capability this lab has not yet demonstrated.

**What F7a establishes that carries over:** the free-surface mesh discipline in
`docs/standards/MESH_STANDARD.md` §7, and the measurement-definition contract
discipline in `F7a_REGATE_SPEC.md`. **What it does not:** §7.6 says plainly that
§7's *numbers* are calibrated on a 2D laminar dry-bed collapse, and a hull's
controlling scale is wave height and wavelength, not a bed film. Stage 1 below
exists partly to recalibrate them.

---

## Stage 1 — FEASIBILITY: does it run at all

**Question.** Can this lab build a 3D hull mesh with a free surface, run
`interFoam` on it to a converged steady resistance, and produce a number — any
number — without the solver diverging, the mesh failing its gates, or the
free surface being destroyed by the outlet?

**What is run.** Coarsest defensible mesh, model scale, one Froude number, fixed
sinkage and trim (no body motion). Symmetry plane on the centreline.

**Acceptance criterion — all five, and all are pass/fail, not judgement:**

1. `checkMesh` passes `docs/standards/MESH_STANDARD.md` §3 hard gates
   (non-orthogonality ≤ 70°, skewness ≤ 4), with a birth certificate written per
   §6 and the §7.5 free-surface fields populated.
2. `interFoam` reaches `endTime` with no floating-point trap and no solver
   divergence.
3. α stays bounded within the §7.5 proposed band; `max_Co_over_run` and
   `max_alphaCo_over_run` are recorded **from the log maximum, not the last
   line** (§7.4).
4. Water volume in the domain is conserved to < 1% over the run, or the
   inflow/outflow imbalance is accounted for.
5. A total resistance coefficient C_T is extractable and **settles**: the
   trailing 25% of the time history varies by < 2% of its mean.

**Checked against:** nothing external. **This stage compares against no
published data and must not claim to.** It is an "it ran" stage. A number
produced here is not evidence of accuracy and is labelled `feasibility, not
graded` wherever it appears.

**Failure action.** Report and stop. Do not proceed to Stage 2 on a mesh that
failed its gates or a run whose C_T never settled.

---

## Stage 2 — PHYSICS: is the wave pattern qualitatively right

**Question.** Does the solution show the phenomena a ship wave field must show,
in the places theory puts them? This is the stage that catches "it ran and
produced a plausible-looking number from wrong physics."

**Acceptance criterion — three checks, each against something independent of the
CFD:**

1. **Kelvin wedge half-angle ≈ 19.47°.** The deep-water Kelvin wake angle is a
   result of linear dispersion theory, independent of the hull and of our
   solver — arcsin(1/3) = 19.47°. Measured from the free-surface elevation field
   as the angle of the cusp locus from the bow. **Accept within ±3°.** This is
   the single strongest qualitative check available and it costs nothing beyond
   the run.
   - **Caveat that must be stated, not skipped:** at high Froude number and in
     finite depth the wedge narrows, and the classical angle applies in the deep
     water, low-Froude limit. The stage records the depth Froude number and
     states whether the deep-water assumption holds before applying the ±3°.
2. **Transverse wavelength λ ≈ 2πU²/g.** Also linear theory, also independent of
   the hull. Measured from a longitudinal cut of the free surface along the
   hull side. **Accept within ±10%.**
3. **Bow and stern wave systems present and phased plausibly** — a bow crest, a
   shoulder trough, a stern system, and the expected interference at the design
   Froude number. **This one is a judgement, and it is labelled as one.** It is
   recorded as an image plus a written assessment, and it may not be quoted as a
   quantitative pass.

**Checked against:** linear water-wave theory for (1) and (2) — closed-form, no
citation risk, no digitisation, no paywall. Published wave-cut data for the hull
is *not* used at this stage, because Stage 3 grades against it and a stage may
not consume its own gate's reference.

**Failure action.** A Kelvin angle outside ±3° or a wavelength outside ±10%
means the free-surface treatment is wrong and Stage 3 is meaningless. Diagnose
before proceeding — most likely candidates are outlet wave reflection, damping
zone length, and vertical resolution at the interface per §7.2.

---

## Stage 3 — GATE: does the number land

**Question.** Does C_T at the graded Froude numbers fall within a declared
tolerance of towing-tank data?

**This stage does not begin until its measurement definition is pinned in a gate
spec built to the `F7a_REGATE_SPEC.md` §2 pattern.** That is the whole lesson of
F7a and it is not optional here. The spec must pin, before any run:

- **What is integrated over what.** Which patches enter C_T; whether the
  transom, the deck and any above-waterline surface are included; pressure and
  viscous components separately as well as summed.
- **Non-dimensionalisation.** C_T = R_T / (½ ρ S U²) — and **S, the wetted
  surface area, is the ambiguity here**, exactly analogous to F7a's probe row:
  static wetted surface or dynamic (at the running attitude)? They differ, and
  the published value is usually the static one. Pin it, and record both.
- **Time origin and averaging window.** Which portion of the time history is
  averaged, chosen by a settling criterion fixed in advance, not by eye.
- **Sinkage and trim.** Fixed or free. If free, the 6-DOF setup is itself a new
  capability and gets its own feasibility stage — it does not ride along inside
  Stage 3.
- **The comparison.** Which dataset, at which Froude numbers, absolute or
  relative tolerance, and whether the gate is decided on the mean or the worst
  station. `F7a_REGATE_SPEC.md` §2.4 decides on the **worst station** and this
  should too, for the reason given there.

**Tolerance.** Not set here. It is set in that spec, anchored — as F7a's 5% was
— to **what a published solver demonstrably achieves on this benchmark**, taken
from the workshop's own comparison volumes, not to a house number. Setting it
before that evidence is in hand would be inventing a threshold.

**Checked against:** towing-tank C_T at model scale. The specific dataset,
its access route, and whether the numbers are tabulated or must be digitised is
recorded in `NAVAL_CAPABILITY_GAP_MAP.md` — including, honestly, where the data
is behind a workshop registration wall rather than openly fetchable.

**Failure action.** Report the FAIL with the same discipline F7a's re-gate
applies: the verdict, the metric's own uncertainty, and the mechanism if one is
isolated. A documented failure ships; a quietly re-tuned tolerance does not.

---

## Staging rules that bind all three

1. **No stage skips.** Stage 2 does not start on a Stage 1 failure, and Stage 3
   does not start on a Stage 2 failure. F7a's own record is the argument: the
   feasibility and physics stages passed there and the gate still failed, which
   is only informative *because* the stages were separated.
2. **One pre-registration per stage**, written before that stage's compute, with
   predictions and thresholds — per this lab's rule that pre-registration
   precedes compute.
3. **Each stage is priced before it is bought**, and a stage that overruns its
   estimate by more than 2× stops and reports rather than continuing.
4. **Each stage's cost is recorded separately** in the `Feasibility X + Physics
   Y + Gate Z` form `CAMPAIGN_STATUS.md` already uses.
5. **No stage may quote the next stage's reference data.** Stage 2 uses linear
   theory precisely so it does not consume Stage 3's towing-tank comparison.

---

## What this plan deliberately does not contain

- **A cost estimate.** A 3D free-surface hull mesh at gate resolution is a
  different order of magnitude from anything in the F7a ladder (76,800 cells at
  its finest graded rung), and this agent has run no 3D hull mesh from which to
  extrapolate. **Quoting a core-min figure here would be a number with no
  basis.** It is estimated in the KCS proposal, where a cell count can be
  reasoned from a stated mesh recipe, and even there it is labelled as an
  estimate from a recipe rather than from a measurement.
- **A tolerance.** See Stage 3.
- **Any claim that the case is unblocked.** It is not.
