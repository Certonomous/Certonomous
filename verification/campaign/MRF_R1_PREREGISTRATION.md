# MRF_R1 — Rushton-turbine power number Np via whole-tank MRF

**STATUS: DRAFT / UNFROZEN. NO COMPUTE HAS RUN. NOT A GATE YET.**
This document is a working-tree draft authored by a cfd lab-lane. It is **not
frozen**: no sha binds it, no run directory exists, and no verdict may be read
from it. The FREEZE (sha) and the graded launch are the cfd-supervisor's
check-4; the grader diff-read is the supervisor's check-1. Both are the
supervisor's and neither has been done. Until the freeze commit, every gate,
threshold, cap and band below is amendable and carries no evidentiary weight
(CLAUDE.md rule 2).

- **Case family:** `navier_class` / `MRF` (rotating machinery, Case 2 of the
  Navier-class parity pack).
- **Rung:** R1 — the cheapest defensible first rung (see §1).
- **Prose:** `docs/campaigns/navier_class/MRF/MRF_R1_rushton_power_number.md`
- **Inputs / grader / mesh scripts:** `cases/navier_class/MRF/`
- **Outputs (none yet):** `verification/runs/navier_class/MRF/`
- **Precedent reused:** `verification/campaign/F8_MRF_HAND2001_GATE.md` — the
  lab's existing whole-domain MRF torque gate. Its torque-from-`moment.dat`
  convention, its `nonRotatingPatches` discipline, its settledness (S12) test
  and its "predict, then name the risk" structure are carried here.

---

## 1. The rung, and why it is the cheapest defensible one

**Chosen rung: the Rushton-turbine power number `Np`, computed from the steady
MRF impeller torque, graded against the Rushton/Costich/Everett 1950
turbulent-plateau power-number correlation.**

Two candidates were on the table (Case-2 manifest):

1. **Rushton power number `Np`** — one operating point, one geometry, one
   integral scalar (impeller torque). No inlet/outlet, no diffuser, no
   flow-rate matching. The reference is a **correlation** (a curve `Np(Re)`
   with a flat turbulent plateau), which for a *standard* geometry behaves as
   a near-exact tier value. Directly analogous to F8's torque integral, so the
   whole read/plant/complete machinery transfers.
2. **ERCOFTAC centrifugal pump head-flow point** (Ubaldi 1996 / Combès U3) —
   requires a vaned-diffuser mesh, an inlet/outlet, a matched flow coefficient
   and a head definition (Dixon & Hall 2014). Materially more mesh and more
   setup for the same *class* of verdict.

`Np` wins on cost and defensibility and is registered as R1. The pump head-flow
point is deferred to a later rung (R2+), and its harder question — MRF vs AMI
sliding for the rotor/stator gap — is deliberately not incurred here: **a
Rushton power number needs only a frozen-rotor MRF** (see §4).

**A third, title-verified option considered and DECLINED for R1 (scope).** A
retrieval lane offered NASA TP-1337 Rotor 37 (Reid 1978,
`docs/papers/benchmark_test_cases/reid_1978_nasa_tp1337_rotor37_compressor.*`) —
a title-verified reference that could claim a higher tier. It is declined for
this rung on two grounds: (1) **scope** — Rotor 37 is a *compressible transonic
axial-compressor* rotor, different physics from Case 2's *incompressible* MRF
stirred-tank / centrifugal-pump manifold, and this lane is scoped to Case 2;
(2) **cost** — a shocked, wall-resolved compressible rotor is the opposite of
"the cheapest defensible first rung." Rotor 37 is noted here as a strong
candidate for a *separate* compressible-turbomachinery case (its own prereg),
not as R1 of the incompressible MRF family. The tier below therefore stays
manifest-only / bounded-agreement, as the tasking's Case-2 references dictate.

**Quantity graded.** With impeller torque `Q` [N·m] about the shaft axis,
impeller speed `N` [rev/s], impeller diameter `D` [m] and density `ρ`:

    P  = ω · Q = 2π N · Q            (power drawn by the impeller)
    Np = P / (ρ N³ D⁵) = 2π Q / (ρ N² D⁵)

`ρ`, `N`, `D` are fixed inputs; `Np` is therefore a fixed scaling of the
measured torque `Q`, and both the grid-convergence triple and the band act on
`Np` directly.

---

## 2. Reference value and REFERENCE TIER

**Reference (manifest, NOT yet title-verified):** for a standard fully-baffled
stirred tank with a 6-blade Rushton disc turbine at fully-turbulent Reynolds
number (`Re = N D² / ν ≳ 10⁴`), the power number sits on a flat plateau
independent of `Re`. Manifest correlation value:

    Np_ref = 5.0   (turbulent plateau, standard geometry)

with a documented literature spread of roughly **5.0–6.0** across blade-thickness
and baffle conventions. Sources named in the Case-2 manifest, to be fetched and
**title-page-verified (L-144)** by the paper-retrieval lane:

- Rushton, Costich & Everett (1950), *Power characteristics of mixing
  impellers*, Chem. Eng. Prog. 46, 395–404 & 467–476 — the power-number
  correlation (the manifest calls this "an exact-tier gate for a mixer").
- Zhou & Kresta (1996), AIChE J. 42(9), 2476–2490 — stirred-tank power numbers.
- Wu & Patterson (1989), Chem. Eng. Sci. 44(10), 2207–2221 — LDA data (a later
  tier upgrade path toward experiment-validated local fields).

**REFERENCE TIER (per `verification/credibility/REFERENCE_TIER_STANDARD.md`):**

> **bounded-agreement (rank 3)** — provisional, **capped by evidence state.**

Rationale, stated honestly:

- Against **manifest values only** (papers not yet fetched or title-verified),
  this case is at best **code-verified / bounded-agreement, NOT
  experiment-validated** — exactly the cap the tasking sets. The band in §3 is
  the "explicitly-stated quantitative band vs a named reference" that the
  bounded-agreement tier requires, and it will always be shown WITH the case.
- A power-number *correlation* for a *standard* geometry can support a tighter
  claim than a bare code-to-code reproduction, which is why bounded-agreement
  (not code-verified) is claimed — but the claim is **provisional until a
  title-verified Rushton-1950 (or Zhou & Kresta) PDF lands** in
  `docs/papers/`. Until then the case carries the disavowal: *"reference is a
  manifest correlation value, not yet title-verified; NOT validated against a
  wind-tunnel/rig experiment."*
- **Registry note:** this case is NOT yet a *completed 3D case*, so it does not
  belong in `verification/credibility/reference_tier_registry.json` (which is a
  frozen, verification-team-owned artifact scoped to completed cases). It is
  registered there — via `scripts/check_reference_tier.py` — **only once it
  completes and only by the verification supervisor**. This lane does not edit
  the frozen registry. The tier is **upgradable** to experiment-validated later
  if the case is graded against Wu & Patterson LDA data at a title-verified
  source.

The tier is displayed subject to the reference-tier gate: any page showing this
case must carry the §3 band; none may show it as experiment-validated.

---

## 3. THE GATE, threshold, band and cap (pre-registered, before any compute)

**Gate primary quantity:** fine-level power number `Np` (from the finest of a
three-level geometrically-similar mesh family), graded by the shared instrument
`scripts/roache_triple.py` in its exact rule-5 order.

**Grid-convergence precondition (rule 5, Sanaa's 3-level standard,
`MESH_STANDARD.md` §9.1).** Three levels, each iteratively converged and
plateaued; the finest triple must be **CONVERGING**; the observed order `p` and
the GCI at **Fs = 1.25** are computed and printed. A triple that is
`DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT`/`DEGENERATE`, or any level not
converged/plateaued, is **NOT A RESULT** whatever the value.

**Reynolds regime the band is tied to (a Rushton `Np` is regime-dependent).**
The band below is valid ONLY on the **fully-turbulent Np plateau**, where `Np`
is independent of `Re`. This case fixes `Re = N D²/ν = 5.0 × 10⁴` (§4), which
sits well above the `Re ≳ 10⁴` plateau onset for a fully-baffled tank. The band
is meaningless off this plateau: a transitional or laminar `Re` would demand a
different reference and a different band, and this pre-registration does not
cover those regimes. The grader records the case's `N, D, ν` so the graded `Re`
is reconstructible and the regime assumption is checkable.

**Pre-registered PASS band (bounded-agreement, on the fine-level `Np`, on the
fully-turbulent plateau `Re = 5.0 × 10⁴`):**

    PASS band:  Np ∈ [4.0, 6.0]

i.e. the reference plateau `Np_ref = 5.0` widened to cover the 5.0–6.0
literature spread plus a ~20% low-side margin for the documented steady-MRF
bias. The torque→power definition the grader uses is stated explicitly:
`P = ω·Q = 2π N·Q`, hence `Np = 2π Q / (ρ N² D⁵)` (grader
`power_number()` and its module docstring). Verdicts, in the fixed vocabulary only:

- finest triple CONVERGING **and** `Np ∈ [4.0, 6.0]`  → **PASS**
- finest triple CONVERGING **and** `Np ∉ [4.0, 6.0]`  → **GATE FAIL** (a result)
- triple not CONVERGING, or any level not converged/plateaued → **NOT A RESULT**
- reference cannot be title-verified when required, or a run cannot complete →
  **BLOCKED** at the core-minutes actually spent
- not yet run → **PENDING: `verification/runs/navier_class/MRF/`**

The gate is one-way: it may only turn a PASS or GATE FAIL **into** NOT A RESULT,
never the reverse (enforced structurally by `roache_triple._seal`).

**Prediction, carried before the data (and the named risk).** Steady MRF is
documented (Brucato et al. 1998: MRF vs sliding vs inner-outer) to
**under-predict** the Rushton power number because a frozen rotor cannot
capture the periodic blade–baffle interaction and trailing-vortex shedding.
**Predicted:** the fine-level `Np` lands **low-side, in roughly [3.5, 5.0]**.
Named risk, reported as a result if it happens: `Np` falls **below 4.0** →
**GATE FAIL**, and that GATE FAIL is the quantified statement of steady-MRF bias
on this case, not a defect to be hidden (exactly F8's discipline). The opposite
risk — the torque never plateaus and the triple is not CONVERGING — lands
**NOT A RESULT** and turns R1 into a settledness/convergence-fix diagnosis, as
F8's steady branch did.

**COMPUTE CAP (rule 12; c7a.4xlarge $0.0513/core-h, derived-not-measured).**
Unit is core-minutes = wall-s × ranks ÷ 60. The box cannot read its own billing,
so any dollar figure is **reported-by-owner / derived, not measured**.

| level | target cells | ranks | endTime (iters) | est. core-min | sub-cap |
|---|---|---|---|---|---|
| coarse | ~250 k | 16 | 4000 | ~35 | 60 |
| medium | ~0.85 M | 16 | 4000 | ~90 | 140 |
| fine | ~2.9 M | 16 | 4000 | ~200 | 300 |
| meshing + potentialFoam + checkMesh + smoke | — | — | — | ~30 | 60 |
| **total** | | | | **~355** | **cap 420 core-min** |

**Total compute cap: 420 core-minutes** (≈ 7.0 core-h; derived ≈ **$0.36** at
$0.0513/core-h — derived, not measured). This is **under the $25 pre-authorised
ceiling**, and is still costed here per rule 12. **An overrun STOPS the run; it
does not get a new budget.** A per-level sub-cap that trips stops that level and
the level is reported at the core-minutes spent. Estimate-vs-actual calibration
(rule 12, Sanaa 2026-08-23) is owed at rung completion, as a row in
`docs/COST_CALIBRATION.md`.

---

## 4. MRF setup, rotor/stator interface, and the mesh family

**Geometry — a standard fully-baffled stirred tank (concrete dimensions):**

| parameter | symbol | value |
|---|---|---|
| tank diameter | T | 0.300 m |
| liquid height | H | 0.300 m (= T) |
| impeller diameter | D | 0.100 m (= T/3) |
| impeller off-bottom clearance | C | 0.100 m (= T/3) |
| baffles | — | 4, width T/10 = 0.030 m, 90° apart, full height |
| impeller | — | 6-blade Rushton disc turbine: disc Ø 0.75 D, blade L = D/4, blade H = D/5, thin blades |
| shaft | — | Ø ~0.02 m, concentric, full depth |
| fluid | — | water: ρ = 998 kg/m³, ν = 1.0e-6 m²/s |
| speed | N | 5.0 rev/s (300 rpm), ω = 2πN = 31.4159 rad/s about +z |
| Reynolds number | Re = N D²/ν | 5.0×10⁴ (fully turbulent — on the Np plateau) |

**Solver / model.** Steady `simpleFoam` (incompressible), OpenFOAM **v2606**
(the version installed on this box, `/usr/lib/openfoam/openfoam2606/`, `api=2606`
verified). Turbulence: **k-omega SST** with wall functions (`nutkWallFunction`,
`kqRWallFunction`, `omegaWallFunction`) targeting y+ in the log-law band
(30 ≲ y+ ≲ 300) per `MESH_STANDARD` §-cross-cutting (Menter 2003 wall-function
guidance). `potentialFoam` initialisation with the **MRF zone deactivated**
during the init step only — the F8 §15 lesson: `potentialFoam -writephi` inside
an active whole-domain MRF zone writes an absolute frame flux and is toxic; here
the MRF zone is a *sub-region* (the impeller cylinder), and init is run with
`active false`, no `-writephi`, then restored.

**MRF vs AMI — MRF is registered, and why.** For a *steady power-number* gate a
**frozen-rotor MRF** is the correct and cheapest model: the impeller sub-region
rotates in a single frozen position relative to the fixed baffles, and the
integral torque is far less position-sensitive than the local field
(Luo/Issa/Gosman 1994 — the MRF-for-mixers reference; Brucato 1998 — what each
approach gets right/wrong). **AMI sliding mesh** (Farrell & Maddison 2011, the
basis of OpenFOAM's AMI; tutorial `pimpleFoam/RAS/propeller`) is a *transient*
model an order of magnitude more expensive and is **explicitly deferred** to a
later rung if the frozen-rotor position dependence proves to matter. The MRF
setup follows tutorial `incompressible/simpleFoam/mixerVessel2D` (v2606,
verified on disk), lifted to 3D:

- **`constant/MRFProperties`:** one zone `impeller`, `active yes`,
  `cellZone impeller`, `origin (0 0 0)`, `axis (0 0 1)`, `omega 31.4159`.
- **`nonRotatingPatches`:** the tank wall, all four baffles, the flat lid and
  the bottom — everything stationary in the lab frame — are listed, so
  `MRF.correctBoundaryVelocity` does NOT sweep them (F8 §14(2) discipline). The
  impeller blades/disc/hub patches are NOT listed (they rotate).
- **cellZone coverage:** the `impeller` cellZone is a cylinder of radius ~0.6 D
  and height spanning the disc turbine, built with `topoSet`; the `topoSet` log
  cell count is recorded and must equal the enclosed-cell count (F8 §14(3)).
- **Frozen-rotor position:** blades set **midway between adjacent baffles** (the
  conventional choice). The position-dependence of `Np` is a **disclosed,
  ungated uncertainty** for R1; a position-averaged variant is a research option
  for a later rung, not owed here.

**Free surface:** modelled as a **flat rigid lid with a slip condition**
(single-phase, no VOF) — standard for a baffled-tank power-number MRF; the
liquid height H = T fixes the lid. Disclosed limitation: a real vortexing free
surface is not modelled; at fully-baffled conditions the surface deformation is
small and the flat-lid idealisation is the community-standard power-number
setup.

**Mesh generator.** `snappyHexMesh` from an STL of {tank + baffles + shaft +
6-blade disc turbine} (CROSS-CUTTING SETUP: snappyHexMesh + `motorBike` is the
canonical real-STL 3D route; cfMesh is the alternative cut-cell lane). The
rotating cellZone is created post-mesh by `topoSet` (`cellZoneSet` from a
cylinder `searchableSurface`). `blockMesh` is used only for the background box;
per `MESH_STANDARD` §8.2, if `blockMesh`/`snappy` refuses a topology it is a
diagnostic, not an obstacle to route around by hand-writing `polyMesh`.

**Grid family for a Celik-2008 Fs = 1.25 GCI triple (rule 5; `MESH_STANDARD`
§9).** Three geometrically-similar meshes, **linear refinement ratio r ≈ 1.5**
(cell ratio ≈ 3.4), by scaling the snappy background base cell ×1/1.5 per step
while holding **fixed relative surface-refinement levels and a fixed relative
first-layer thickness** so the family is *similar* (§9.2). Because snappy
refines in powers of two, exact geometric similarity is harder than with
blockMesh; therefore, per **`MESH_STANDARD` §9.2 (the similarity read-back
clause)**, the grader/mesh scripts **record, per level, the ACTUAL first-cell
height, expansion ratio and refinement-level counts read back from the built
mesh / `checkMesh`**, never the requested values — the requested value is the
one that lied in the F12 branch-flip defect.

**Mesh admissibility gates (`MESH_STANDARD` §3, hard):** max non-orthogonality
≤ 70°, max skewness ≤ 4 (boundary faces included). **`MESH_STANDARD` §8.1
(BUILD BEFORE FREEZE): this pre-registration MAY NOT be frozen until at least
the coarse level is BUILT, `checkMesh`'d and SHOWN ADMISSIBLE against these
gates.** Each level carries a **§6 mesh birth certificate** recording
`points_sha256`, cell count, max non-orthogonality, max skewness, and — per
**§11.4** — `max_aspect_ratio` (non-null) and the derived whole-mesh
`cell_volume_ratio` (`max_cell_volume / min_cell_volume`), read back from that
level's own `log.checkMesh` under a planted control.

---

## 5. Completion rule (rule 4) — the incompressible field set

A level is **done** only if ALL hold (CLAUDE.md rule 4; `mark_done_t3.py`
precedent):

1. `rc == 0`;
2. an `End` line in the solver log;
3. **last written time == `endTime`**;
4. **fields present at `endTime`** — the incompressible-RAS set for this case:
   **`U p phi k omega nut`** (the rule-4 canonical list `T U p_rgh alphat nut k
   omega phi` is the *thermal*-family list; this case is isothermal
   incompressible, so its analogous complete set is `U p phi k omega nut`, and
   the age guard + End line + last-time + rc=0 clauses apply unchanged — the
   substitution is disclosed here so it is not a silent departure);
5. **every field at `endTime` NEWER than the case's own `0/` directory** — the
   age guard, because `0/` is touched last at launch;
6. the grader **refuses (exit 2)** a case where a `0` or a time directory
   already exists at launch (the age-guard precondition).

A run failing any clause is **not done** and is not graded; the grader refuses
rather than degrade.

---

## 6. Grader — `cases/navier_class/MRF/grade_mrf_np.py`

The grader is built ON the shared, already-selftested instrument
`scripts/roache_triple.py` (Roache rule-5 gating, one-way gate, GCI at Fs=1.25,
fixed vocabulary, refuse-not-degrade all inherited) and adds the MRF-specific
read path plus rule-4 completion. It MUST, before emitting any clean number:

1. **Rule-4 strict completion** per level (§5); refuse (exit 2) on any failure.
2. **LIVE planted-zero control (rule 3)** on the ACTUAL torque read path: copy
   the level's `postProcessing/impellerForces/*/moment.dat` to a temp file,
   plant `PLANT = 1.234e-03` into the graded torque column, re-read it through
   the SAME parser the grade uses, and **REFUSE if the reader does not see it**
   (wrapped via `roache_triple.external_plant_control` + `assert_plant_control`).
   A zero from a reader not shown able to see a non-zero is not evidence.
3. Compute `Np` per level from the read-back torque and the fixed `ρ, N, D`.
4. Build the coarse→fine `Np` series and call `roache_triple.grade_ladder(...)`
   with **dim = 3**, the pre-registered band `[4.0, 6.0]`, and the per-level
   iterative-convergence and plateau (settledness) states — which enforces
   rule 5 in order and the one-way gate.
5. Emit only the fixed verdict vocabulary; write the graded row JSON to
   `verification/runs/navier_class/MRF/`.

`grade_mrf_np.py --selftest` drives the planted control **both directions**
(a blind reader FAILS, a working reader SEES `PLANT`) on a synthetic
`moment.dat`, proving the torque reader is not blind, and cross-checks the `Np`
arithmetic — exit non-zero if the control does not fire (rule 3, L-332
exit-code-driven so `-O` cannot strip it).

---

## 7. Pre-flight EXERCISE-smoke plan (A3FL1 lesson) — before the graded freeze

Static checks are not an exercise. Before the supervisor freezes and launches
the graded triple, the **coarse** level is exercised as a real short run
(A3FL1: run the config → first iterations → rc=0), NOT merely dictionary-linted:

1. Build the coarse mesh; run `checkMesh`; confirm §3 admissibility (non-ortho
   ≤ 70°, skew ≤ 4) and write its birth certificate — this also satisfies
   `MESH_STANDARD` §8.1 (BUILD BEFORE FREEZE), the precondition for the freeze.
2. `topoSet` the impeller cellZone; confirm the logged cell count equals the
   enclosed count (F8 §14(3)).
3. `potentialFoam` init with the MRF zone `active false`; confirm continuity
   error small and rc = 0.
4. `simpleFoam` for **~50 iterations** (well under the coarse sub-cap):
   confirm rc = 0, that residuals fall (not diverge), that the
   `impellerForces` function object writes a **finite** `moment.dat` with a
   torque of a plausible sign and order (F8-style instrument sanity — a
   Rushton impeller draws power, so the axial moment opposes `ω` and gives a
   positive `Np`), and that no `bounding` cascade builds (F8 §12 divergence
   tell).
5. Only if the smoke run is clean does the graded triple get frozen and
   launched. A failed smoke run is a **finding** (crash triage is the
   supervisor's check-2, non-delegable), not a reason to launch anyway.

The smoke run's core-minutes count against the "meshing + smoke" line of §3.

---

## 8. What this document is NOT

- It is **not frozen** — no sha, no committed grading path hash yet.
- **No compute has run** and no verdict exists; all verdicts above are
  templates keyed to data that does not yet exist.
- The reference is **manifest-only**, not title-verified; the tier claim is
  provisional and capped accordingly (§2).
- The mesh line is **assumed, not measured** — §8.1 forbids freezing until the
  coarse level is built and shown admissible.

*Nothing below this line exists yet; addenda after the freeze may not alter any
gate, threshold, cap or band above (rule 2).*
