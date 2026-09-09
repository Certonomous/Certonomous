# DRIVAER R1 — DrivAer notchback, drag/lift parity vs DrivAerML — PRE-REGISTRATION

**STATUS: DRAFT / UNFROZEN. NO compute has run. NOT FROZEN (no sha).
BLOCKED-geometry (a LEAD, not a terminal verdict): no DrivAer STL is on disk yet.**
Drafted by a cfd lab-lane for the cfd supervisor. The **freeze (sha) and any graded
launch are the supervisor's check-4**; the grader diff-read is the supervisor's
check-1. Nothing below is graded.

Case family: Navier-class parity, `navier_class` convention.
- Campaign prose: `docs/campaigns/navier_class/DRIVAER/`
- Case inputs / grader: `cases/navier_class/DRIVAER/` (grader `grade_drivaer.py`)
- Run outputs (none yet): `verification/runs/navier_class/DRIVAER/`
- Reference values: `verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json`

This rung is the **DrivAer step of the vehicle-external-aero ladder** the lab already
holds on the Ahmed body (`W3_AHMED_PREREGISTRATION.md`, `R4_AHMED_*`): a real 3-D road
car rather than a slant-back reference body. The Ahmed setup/gate template transfers;
the geometry and reference do not.

---

## 1. GEOMETRY AVAILABILITY — the finding, and the lead

**No DrivAer STL is on disk.** Searched `cases/`, `models/`, `mission-output/` and the
large stores `/home/ubuntu/{closure-data,certonomous-runs,closure-challenge-benchmark}/`
2026-09-09: the only `driv*` hits are `*driver*` scripts (false positives). **This is a
LEAD to resolve, NOT a terminal verdict — `BLOCKED-geometry`, not BLOCKED.**

Leads to resolve (a retrieval/meshing lane, not this drafting lane):
- The **DrivAerML** dataset (Ashton et al. 2024, arXiv:2408.11969v2) ships the notchback
  geometry and per-run meshes; the baseline STL is the natural source and matches the
  reference (below). Provenance/title verification (rule 15, L-144) is required on the
  retrieved STL before it is meshed — a geometry file is trusted no more cheaply than a
  paper.
- Alternatives: the DrivAer public geometry (Heft/Indinger/Adams 2012, SAE
  2012-01-0168) and the AutoCFD workshop case geometries (autocfd.org).

Until a provenance-verified STL lands, the run cannot start and the exercise smoke
(§6) cannot run. The grader and this pre-registration stand ready so that meshing can
begin the moment geometry is in hand.

---

## 2. THE GATE — declared now, one-way

> **Gate V1 (PRIMARY).** The vehicle drag coefficient `Cd` at `Re_L = 7.19×10⁶`
> (DrivAerML conditions), from the finest grid of a **CONVERGING** Roache triple, is
> **PASS** iff `|Cd_cfd − Cd_ref| ≤ 0.10·Cd_ref` (±10%), else **GATE FAIL**.
> **Gate V2 (SECONDARY).** The vehicle lift coefficient `Cl` is **PASS** iff
> `|Cl_cfd − Cl_ref| ≤ 0.05` (ABSOLUTE band — Cl is small and sign-sensitive), else
> **GATE FAIL**; V2 is graded only if `Cl_ref` is pinned.
> A non-CONVERGING triple is **NOT A RESULT** whatever the value (rule 5).

**Band rationale, recorded now.** DrivAerML's own per-run statistical accuracy is
`ΔCd = ±0.001` (≈ 1 drag count). A ±10% band (≈ ±0.028 at Cd≈0.28) is far wider than
the reference's uncertainty and is the appropriate width for a **steady-RANS vs
scale-resolving** parity gate, where model-form (RANS closure) error dominates
numerical error. It will not be tightened after the run.

**Reference values `Cd_ref`, `Cl_ref`** come from the **DrivAerML baseline-geometry
mean coefficients**. Provisional `Cd_ref = 0.28` (mid-scatter placeholder; the
500-variant scatter runs ~0.237–0.340) — to be **pinned to the exact DrivAerML baseline
run value at freeze** (a legal pre-compute amendment stating the condition, rule 2).
The band shape (±10%, ±0.05) does not move.

**Reference constants (frozen into forceCoeffs; grader asserts them on disk):**
`magUInf = 38.889 m/s`, `lRef = 2.786 m` (wheelbase), `Aref = 2.17 m²` (frontal),
`rhoInf = 1.225 kg/m³` (air — **confirm against the DrivAerML value at freeze**). Source:
arXiv:2408.11969v2 pp.5–6. Incompressible (M ≈ 0.11).

---

## 3. REFERENCE TIER — title-verified CODE reference

Applying `verification/credibility/REFERENCE_TIER_STANDARD.md`:

- **Tier: CODE-VERIFIED (rank 2).** DrivAerML is a **scale-resolving CFD dataset**
  (hybrid RANS-LES), a **CODE reference — NOT experiment.** The gate therefore
  reproduces a code reference and **carries the mandatory disavowal: "reproduces the
  DrivAerML CFD dataset; NOT experiment-validated."** It must **never** be shown as
  experiment- or workshop-validated.
- **Title-page verified (rule 15, L-144) by this lane 2026-09-09.** The PDF page 1
  reads *"DrivAerML: High-Fidelity Computational Fluid Dynamics Dataset for Road-Car
  External Aerodynamics"*, arXiv:2408.11969v2, Neil Ashton (AWS) et al. — matches the
  intended identity. PDF outside git at
  `/home/ubuntu/certonomous-runs/reference_pdfs/benchmark_test_cases/ashton_2024_drivaerml.pdf`;
  pointer `docs/papers/benchmark_test_cases/ashton_2024_drivaerml.POINTER.md`. This is
  **higher than manifest-only**: the code reference is real, filed and verified.
- **Upgrade path.** If an **AutoCFD-workshop EXPERIMENTAL Cd** is later retrieved and
  title-verified, the tier may be upgraded to **bounded-agreement** (with band) or
  experiment-validated. AutoCFD is **manifest-only** today (not confirmed filed).
- **Registry action deferred to completion.** DrivAer is not yet a *completed 3-D case*,
  so it is **not** added to the frozen `reference_tier_registry.json` now (that would be
  registry drift). The tier is pre-declared here; the verification team registers it at
  completion. `scripts/check_reference_tier.py --selftest` confirmed green by this lane.

---

## 4. MESH PLAN (per `docs/standards/MESH_STANDARD.md`)

**Generator.** `snappyHexMesh` on the DrivAer STL — the canonical real-STL 3-D external
case is the OpenFOAM `incompressible/simpleFoam/motorBike` tutorial
(`/usr/lib/openfoam/openfoam2606/tutorials/...`, v2606), the template for surface
extraction, castellation, snapping and prism layers. cfMesh `cartesianMesh` is the
alternative cut-cell lane (Juretić 2015).

**Three-level family (rule 5; §9.1).** Geometrically similar refinement (§9.2):
surface-refinement level and background-cell size scale together, recipe otherwise
fixed. Target ~3M / 6M / 12M cells (≈2× per level ⇒ `r ≈ 2^{1/3} ≈ 1.26` in `h`);
grader treats DrivAer as `dim = 3`. **Per-level graded values (refinement levels,
first-layer thickness) read back from the built mesh** into each birth certificate
(§9.2), never from the requested parameter.

**Admission gates (§3) and BUILD-BEFORE-FREEZE (§8.1).** snappyHexMesh generates to
`maxNonOrtho 65` and relaxes to 75 only during layer addition; acceptance is **≤ 70°**
non-orthogonality and **≤ 4** skewness. Aspect ratio and whole-mesh cell-volume ratio
**recorded** (§11). Each level built + `checkMesh`'d + **shown admissible** before
freeze — a real risk on a complex STL with prism layers, so at minimum the **coarse**
level must be built and admissible before this pre-registration is frozen, and the
finer levels' admissibility is a freeze precondition too.

**Wall treatment.** kOmegaSST with **wall functions**, target `y⁺ ≈ 30–100` (first
rung). DrivAerML itself is wall-modelled scale-resolving; our RANS wall-function rung
is the cheapest defensible parity check. Achieved `y⁺` recorded. (Wall-resolved is a
later rung.)

**Domain / blockage.** Open-road (free-air) domain per the motorBike template and
DrivAerML's own open domain: inlet ~3–5 body-lengths upstream, outlet ~8–10
downstream, height/half-width sized so **domain blockage < 1%** (measured and
recorded). DrivAerML is free-air, so **no wind-tunnel (Barlow-Rae-Pope 1999) blockage
correction is applied** — it would apply only if graded against a tunnel reference.
Spalart-Rumsey 2007 sets the effective inflow turbulence values and their placement.
Moving-ground / rotating-wheel effects are **out of scope** for R1 (the DrivAerML
baseline uses static wheels; match it).

**GCI.** Celik 2008 `Fs = 1.25` via `scripts/roache_triple.py`; never quoted for a
non-monotone triple.

---

## 5. THE GRADER — `cases/navier_class/DRIVAER/grade_drivaer.py`

Diff-read is the supervisor's check-1. Same discipline as `grade_suboff.py`:

- **Live planted-zero control (rule 3):** PLANT `5.0` into ONE body owner-cell of a
  COPY of the finest `p` field, re-read the body mean-surface-pressure through the same
  reader, **REFUSE (exit 2)** unless the mean moves by the expected `PLANT/n_body`. The
  body patch group is matched by name (`body`, and any `*body*` sub-patch — mirrors,
  wheels, underbody).
- **Refuse-not-degrade:** exit 2 bad input/control; exit 70 internal defect only; exit
  0 only when a verdict was produced.
- **Rule-4 strict completion:** `rc==0`/`End`; last==`endTime`; incompressible-RANS set
  `p U k omega nut phi` present at endTime and newer than `0/` (age guard).
- **forceCoeffs constants asserted on disk** (`magUInf/lRef/Aref/rhoInf` = registered)
  or refuse — wrong normalisation is not the gated quantity.
- **Rule-5 Roache triple via the shared instrument** (`grade_ladder`, `dim=3`) for both
  Cd (V1) and Cl (V2); no `P_MIN`/`STAGNANT_FLOOR` redefined (§10.5). Fixed verdict
  vocabulary only.
- **Same disclosed NB as SUBOFF:** per-level iterative-convergence state is to be handed
  in from `log.simpleFoam` by the launcher; the grader defaults CONVERGED on an `End`
  line and measures the plateau itself. A revision to read iterative state from the log
  is owed before freeze.

Selftest confirmed green by this lane: CONVERGING-in-band → PASS, CONVERGING-out-of-band
→ GATE FAIL, missing control → refuse.

---

## 6. EXERCISE-SMOKE PLAN (A3FL1 — a real run, blocked on geometry)

New solver config on a new geometry ⇒ a real EXERCISE smoke is required before the
graded freeze. It **cannot run until the STL lands** (§1); it is a freeze precondition:

1. `surfaceFeatureExtract` + `snappyHexMesh` the **coarse** DrivAer mesh; `checkMesh`
   and confirm §3 admissibility (this is the BUILD-BEFORE-FREEZE mesh line, §8.1).
2. Launch `simpleFoam` for **~50 iterations** with the R1 config; **assert `rc==0`**,
   residuals decreasing, no unbounded turbulence-field messages, and that
   `coefficient.dat` is written with parseable `Cd`/`Cl` columns.
3. `grade_drivaer.py --selftest --smoke <coarse-smoke-dir>` so the **planted-zero
   control fires on a real on-disk field** before any graded run.

---

## 7. COST (rule 12 — core-minutes; c7a.4xlarge $0.0513/core-h, derived-not-measured)

Compute cap, **frozen**: **22,000 core-minutes** for the whole rung (coarse ~3M +
medium ~6M + fine ~12M graded triple + exercise smoke). Derived dollar cost at the
recorded rate: 22000/60 core-h × $0.0513 = **≈ $18.8, derived not measured**. Under the
$25 pre-authorised tier — **but this is the lab's most expensive Navier-class rung and
the estimate is SOFT: the lab has no DrivAer precedent.** Therefore, per §8.1
BUILD-BEFORE-FREEZE, **the coarse level's MEASURED cost re-sizes the cap before the
medium/fine grids launch**; if the honest re-sized cap exceeds $25 the rung is
re-registered with the measured cap for the supervisor's check-4 (a blanket approval is
not a per-item read, rule 9). **Overrun stops the run; it does not get a new budget.**
Estimate-vs-actual calibration lands in `docs/COST_CALIBRATION.md` at completion.

---

## 8. LATER LADDER STEPS (named, not registered here)

- **R2 — wall-resolved (`y⁺ < 1`)** re-grade for a tighter numerical channel.
- **R3 — AutoCFD-workshop parity** once an AutoCFD experimental Cd is title-verified
  (would upgrade the tier to bounded-agreement/experiment-validated).
- **R4 — moving ground + rotating wheels** (a physics extension beyond the static-wheel
  baseline).

---

*Nothing in this file is frozen. The supervisor freezes (sha), authorises launch
(check-4) and diff-reads the grader (check-1). This rung is additionally gated on the
BLOCKED-geometry lead (§1). Results, when they exist, land in
`verification/campaign/DRIVAER_R1_RESULTS.md` citing this file by commit hash.*
