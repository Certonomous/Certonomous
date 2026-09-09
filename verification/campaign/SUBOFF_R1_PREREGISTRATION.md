# SUBOFF R1 — DARPA SUBOFF bare hull, zero incidence, total-drag parity — PRE-REGISTRATION

**STATUS: DRAFT / UNFROZEN. NO compute has run for this rung. NOT FROZEN (no sha).**
This document is drafted by a cfd lab-lane for the cfd supervisor. The **freeze
(sha) and any graded launch are the supervisor's check-4**; the grader diff-read is
the supervisor's check-1. Nothing below is graded, and no number here is a result.
Written before any solver launch, in the W3-Ahmed pre-registration pattern: if a
result later falsifies a prediction, the prediction stays as written and the result
says so.

Case family: Navier-class parity, `navier_class` convention.
- Campaign prose: `docs/campaigns/navier_class/SUBOFF/`
- Case inputs / grader: `cases/navier_class/SUBOFF/` (grader `grade_suboff.py`)
- Run outputs (none yet): `verification/runs/navier_class/SUBOFF/`
- Reference values: `verification/runs/navier_class/SUBOFF/suboff_reference_ReL1p2e7.json`

---

## 1. What this rung is, and what it is NOT

The DARPA SUBOFF ladder's full ambition (Case 1) is forces and moments through an
angle-of-attack / drift sweep, yielding the stability derivatives Z_w, M_w and the
neutral point (Roddy 1990 DTRC/SHD-1298-08; conventions Gertler & Hagen 1967 NSRDC
2510, Feldman 1979). **That is a LATER ladder step (§8), not this rung.** R1 is the
**cheapest defensible gate**: the **bare-hull, zero-incidence TOTAL DRAG (axial force)
coefficient at a single Reynolds number** — one scalar, one published reference class
(Crook 1990 drag-vs-speed; consolidated in Liu & Huang 1998), a fully attached
axisymmetric turbulent boundary layer that steady RANS handles well. The bare hull
is the axisymmetric Model 5470 body (Groves/Huang/Chang 1989), regenerable exactly
from the report equations.

Because the bare hull at zero incidence is **axisymmetric**, R1 is run as an
axisymmetric wedge. Under the reference-tier standard's dimension axis it is
therefore **not-applicable-dimension** and **must never appear in a 3-D reference-tier
listing** (`REFERENCE_TIER_STANDARD.md` §4). The 3-D reference-tier entry is earned by
the later at-incidence rung, not this one.

---

## 2. THE GATE — declared now, one-way

> **Gate D1.** The bare-hull zero-incidence total drag coefficient
> `CT = R_T / (½ ρ U² S_wetted)` at `Re_L = 1.2×10⁷`, taken from the finest grid of a
> **CONVERGING** Roache triple, is **PASS** iff `|CT_cfd − CT_ref| ≤ 0.10·CT_ref`
> (±10%), else **GATE FAIL**. A non-CONVERGING triple is **NOT A RESULT** whatever the
> value (rule 5). The band ±10% is the frozen threshold.

**Threshold band: ±10% relative.** Rationale, recorded in advance: bare-hull
straight-course RANS drag on an attached axisymmetric body is a case where published
RANS (Toxopeus 2008 is the closest analogue for expected accuracy) agrees with
measurement to a few percent; ±10% is a **conservative** first-rung band that a
correct solve should clear with margin, and it will not be tightened after the run.

**Reference value `CT_ref`.** Anchor **3.6×10⁻³ on wetted-surface area**, an ITTC-1957
friction-line + body-of-revolution form-factor engineering estimate
(`suboff_reference_ReL1p2e7.json`). This is a **MANIFEST / engineering anchor and it
STAYS one**: there is **no title-verified SUBOFF report PDF on disk** (the Crook 1990 /
Liu & Huang 1998 references are NTIS/TRID landing pages only, 2026-09-09), so the gate
is **BOUNDED-AGREEMENT against this manifest anchor and remains so until a real,
title-verified SUBOFF report PDF lands.** This is explicitly **NOT** a promise to
"replace the anchor with a title-verified value before freeze" — no such value is
retrievable today. If a title-verified SUBOFF report is obtained later, the anchor is
confirmed or corrected by a dated addendum then; the band shape (±10%) does not move.

**Reference constants (frozen into the forceCoeffs block; the grader asserts them on
disk and refuses on mismatch):** `magUInf = 2.893 m/s` (so `Re_L = U·L/ν = 1.2×10⁷`
with `L = 4.356 m`, `ν = 1.05×10⁻⁶ m²/s`), `lRef = 4.356 m`, `rhoInf = 1000 kg/m³`,
`Aref = S_wetted` **read back from the built hull patch area** and cross-checked
(±3%) against the analytic Groves/Huang/Chang 1989 hull surface area.

---

## 3. REFERENCE TIER — manifest-only, stated honestly

Applying `verification/credibility/REFERENCE_TIER_STANDARD.md`:

- **Tier: BOUNDED-AGREEMENT (rank 3) at best, against MANIFEST VALUES ONLY.** The
  SUBOFF drag references (Crook 1990, Liu & Huang 1998) are **NTIS/TRID landing pages
  only; no free title-verified PDF is on disk** as of 2026-09-09 (peer retrieval lane
  `a8dea886569cec3a3`). **This rung is NOT experiment-validated and may not be shown as
  such** until a real SUBOFF report PDF is title-page verified (rule 15). Any page
  showing D1 against the experiment must carry the ±10% band.
- If the solve reproduces only the ITTC engineering anchor (not a title-verified
  experiment), the honest tier is **CODE-VERIFIED (rank 2)** with the disavowal
  "NOT experiment-validated", and the tier is **upgraded to bounded-agreement once the
  title-verified Crook/Liu-Huang value lands.**
- **Registry action is deferred to completion.** `reference_tier_registry.json` is the
  frozen registry of *completed 3-D cases*; R1 is neither completed nor 3-D, so it is
  **not** added now (adding an uncompleted/axisymmetric case would be a dimension leak
  / registry drift). The tier is pre-declared here; the verification team registers it
  at completion of the 3-D at-incidence rung. `scripts/check_reference_tier.py
  --selftest` was confirmed green by this lane (all four RED-plant arms flip).

---

## 4. MESH PLAN (per `docs/standards/MESH_STANDARD.md`)

**Topology.** Axisymmetric wedge (single cell in azimuth, `wedge` patches),
`blockMesh`-generated in the (x, r) plane over the analytic hull profile. If
`blockMesh` refuses the topology, **the topology is redesigned, not bypassed by
hand-writing polyMesh** (§8.2).

**Three-level family (rule 5; §9.1 three levels is the gate standard).** Geometric
similarity is mandatory: first-cell height and expansion ratio **scale with the mesh**,
recipe otherwise fixed (§9.2). Target ~40k / 90k / 202.5k cells (2.25× per level ⇒
`r ≈ 1.5` in `h ~ 1/√N` for a 2-D-like refinement); the grader treats SUBOFF as
`dim = 2`. **Per-level graded values (first-cell, expansion) are read back from the
built mesh** and recorded in each level's birth certificate (§9.2), never from the
requested parameter.

**Admission gates (§3), and BUILD-BEFORE-FREEZE (§8.1).** Each level must be built,
`checkMesh`'d and **shown admissible** before this pre-registration is frozen: max
non-orthogonality **≤ 70°**, max skewness **≤ 4**; aspect ratio and whole-mesh
cell-volume ratio **recorded** in the birth certificate (§11 — recorded, not gated).
A `birth_certificate.json` sits beside each `polyMesh`.

**Wall treatment.** First rung uses **kOmegaSST with wall functions**, target
`y⁺ ≈ 30–100` (cheapest defensible; wall-resolved `y⁺ < 1` is a later rung). The
achieved `y⁺` band is read back and recorded; Menter/Kuntz/Langtry 2003 is the
wall-function-vs-wall-resolved basis.

**Farfield / blockage.** Free-stream (free-air) external domain with Spalart-Rumsey
2007 effective inflow turbulence values and placement: radial farfield ≥ 10·L,
inlet ≥ 5·L upstream, outlet ≥ 10·L downstream (domain blockage negligible). The
Crook 1990 reference is a **towing-tank** resistance measurement whose tank blockage
is small, so free-air CFD is the correct comparison for D1. **Note for a later
Cp-vs-Huang-1992 rung:** Huang's data is **wind-tunnel**, so a Barlow-Rae-Pope 1999
solid+wake blockage correction is required there before comparing tunnel-patched CFD
to that reference — it does NOT apply to this towing-tank drag gate.

**GCI.** Celik 2008 `Fs = 1.25`, computed by the shared instrument
`scripts/roache_triple.py`; never quoted for a non-monotone triple.

---

## 5. THE GRADER — `cases/navier_class/SUBOFF/grade_suboff.py`

Diff-read is the supervisor's check-1. Built-in non-negotiables:

- **Live planted-zero controls (rule 3) — TWO, and the gate reader has its own.**
  (i) **Gate-reader control (primary):** PLANT `CT = 1.234×10⁻³` into the last row of a
  COPY of the finest `coefficient.dat` and re-read it through `read_CT` — **the same
  parser the verdict comes from** — refusing (exit 2) unless the returned value moves by
  the plant. This is the control the graded number needs, because `CT` is read from
  `coefficient.dat`, not from the field. (ii) **Field control (secondary):** PLANT
  `500 Pa` into ONE hull owner-cell of a COPY of the finest `p` field, re-read the hull
  mean-surface-pressure through the same reader, refuse unless it moves by `PLANT/n_hull`.
  A zero from a reader not shown able to see a non-zero is not evidence.
- **Refuse-not-degrade.** `exit 2` on any missing/malformed/unreadable input or a
  control that misbehaves; `exit 70` only for an internal grader defect; `exit 0` only
  when a verdict was produced.
- **Rule-4 strict completion, per level.** `rc==0` **read from an rc sidecar / DONE
  marker written INSIDE the detached wrapper** — never inferred from an `End` line (the
  setsid-parent-returns-zero lesson: a `setsid`/`timeout` parent exits 0 for every
  outcome); an `End` line in the log is also required; last time == `endTime`;
  **ExecutionTime count == `round(endTime/deltaT)`** (rule-4 clause 5; the run took the
  registered number of steps); **incompressible-RANS field set `p U k omega nut phi`**
  present at endTime and every field **newer than `0/`** (age guard). The thermal-family
  set (T, p_rgh, alphat) does not apply — simpleFoam incompressible has no energy
  equation; the enforced set is stated in the grader header. **This requires the R1 run
  to write an rc sidecar** (a freeze precondition on the launcher).
- **forceCoeffs normalisation asserted on disk.** `magUInf/lRef/rhoInf` must equal the
  registered values and `Aref` must match the reference wetted area (±3%) or the grader
  refuses — a coefficient on the wrong normalisation is not the gated quantity.
- **Rule-5 Roache triple via the shared instrument** (`grade_ladder`, `dim=2`), so no
  `P_MIN`/`STAGNANT_FLOOR` symbol is redefined (MESH_STANDARD §10.5). Order: iterative
  convergence + plateau first (a level not plateaued ⇒ NOT A RESULT), then the triple
  (DIVERGENT/STAGNANT/OSCILLATORY/EXACT ⇒ NOT A RESULT), then CONVERGING ⇒ band verdict
  with GCI printed. **Fixed verdict vocabulary only.**
- **Iterative convergence READ, never defaulted (rule-5 clause 1).** Per-level iterative
  state comes from `read_iterative_state`, which reads `log.simpleFoam`: CONVERGED iff
  the solver printed "SIMPLE solution converged" OR every monitored field's **final
  Initial residual** (`p Ux Uy k omega`) is below the registered `RES_TOL = 1×10⁻⁴`
  (Initial, not Final — the W3 gate-(b) test). A level that is not iteratively converged
  makes the whole triple **NOT A RESULT** before the triple is even read. Plateau of `CT`
  is measured separately here.
- **Solver-config requirement (so `last == endTime` is reachable AND iterative
  convergence is judged).** R1 runs to a **fixed iteration count `endTime` with
  `deltaT = 1` as a HARD stop and NO `residualControl` early-exit**, so every level ends
  at exactly `endTime` and the ExecutionTime count equals `round(endTime/deltaT)`.
  Iterative convergence is then the final-Initial-residual test above (residuals below
  `RES_TOL` at `endTime`), not an early "converged" stop. This is a freeze precondition
  on the case's `system/controlDict` and `fvSolution`.

Selftest (`--selftest`) confirmed green by this lane: CONVERGING-in-band → PASS,
OSCILLATORY → NOT A RESULT, not-plateaued → NOT A RESULT, missing control → refuse.

---

## 6. EXERCISE-SMOKE PLAN (A3FL1 lesson — a real run, not static checks)

Before the graded freeze, and because R1 carries a **new solver config** (first
SUBOFF case in the lab), run a real EXERCISE smoke:

1. Regenerate the analytic hull profile; `blockMesh` the **coarse** wedge; `checkMesh`
   and confirm §3 admissibility (this is the BUILD-BEFORE-FREEZE mesh line, §8.1).
2. Launch `simpleFoam` for **~50–100 iterations** on the coarse level with the R1
   config (kOmegaSST, wall functions, the registered inlet/farfield BCs, the
   forceCoeffs block). **Assert `rc == 0`**, residuals decreasing, no unbounded
   turbulence-field messages, and that `postProcessing/forceCoeffs*/…/coefficient.dat`
   is being written with a parseable `Cd` column.
3. Run `grade_suboff.py --selftest --smoke <coarse-smoke-dir>` so the **planted-zero
   control fires on a real on-disk field** before any graded run.

The smoke is a prerequisite to freeze; a smoke that does not reach `rc==0` blocks the
rung. The smoke run is EXERCISE, not graded, and its `Cd` is sanity-only.

---

## 7. COST (rule 12 — core-minutes; c7a.4xlarge $0.0513/core-h, derived-not-measured)

Compute cap, **frozen**: **150 core-minutes** for the whole rung (coarse + medium +
fine graded triple + the exercise smoke + one rerun allowance). Basis: an axisymmetric
wedge simpleFoam solve to steady convergence is minutes of wall time on 16 ranks;
40k/90k/202.5k cells scale roughly linearly. Derived dollar cost at the recorded rate:
150/60 core-h × $0.0513 = **≈ $0.13, derived not measured** (the box cannot read its
own billing). Well under the $25 pre-authorised tier. **Overrun stops the run; it does
not get a new budget.** Estimate-vs-actual calibration lands in `docs/COST_CALIBRATION.md`
at rung completion (rule 12).

---

## 8. LATER LADDER STEPS (named, not registered here)

- **R2 — bare-hull surface Cp at zero incidence** vs Huang 1992 / Liu & Huang 1998
  (wind-tunnel ⇒ Barlow-Rae-Pope blockage correction applies; distributional gate).
- **R3 — bare-hull at incidence**, AoA/drift sweep → forces & moments → derivatives
  Z_w, M_w and neutral point (Roddy 1990; conventions Gertler & Hagen 1967, Feldman
  1979). This is the **3-D** rung that earns a reference-tier registry entry. Toxopeus
  2008 sets the expected-accuracy band.
- **R4 — wall-resolved (`y⁺ < 1`) re-grade** of D1 for a tighter numerical channel.

---

*Nothing in this file is frozen. The supervisor freezes (sha) and authorises launch
(check-4) and diff-reads the grader (check-1). Results, when they exist, land in
`verification/campaign/SUBOFF_R1_RESULTS.md` citing this file by commit hash.*
