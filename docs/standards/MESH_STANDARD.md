# Certonomous Mesh Standard

Version 1.2, dated 2026-08-11. **Adds section 7, marine / free-surface meshes,
and changes no existing gate value.** Section 7 is house practice with its
evidence attached, at the maturity of section 3.4's proposed gate: nothing in it
is written to `docs/physics_rules.yaml` and no code enforces it yet (section
7.6 says so explicitly). Its numbers come from one case family, the F7a dam
break, and section 7.6 records that limitation rather than generalising past it.

Version 1.1, dated 2026-08-08. **Adds exactly one mechanism, the mesh birth
certificate, and changes no gate value.** The Verification Charter's v1.5
section 9 clause -- born clean or it does not enter; a mesh whose birth
certificate is missing is quarantined from new work -- gets its mechanics
(section 6 below), adopted by the infrastructure family after the 2026-08-08
archive sweep measured the gap: 178 unique reachable meshes, 105 already
certified, 47 certified clean by the sweep, exactly one born broken (the A3
vcoarse pyHyp mesh, 23 negative-volume cells, aspect ratio 2.08e95, three
case entries with zero certificate checks), and one structural hole -- the
mesh caches, which stored bare polyMesh with no quality record behind 400+
run directories even where the generating workflow HAD run checkMesh. The
adopting supervisor re-verified the sweep's evidence by hand before adoption:
the born-broken specimen's checkMesh reproduces digit-for-digit, a born-clean
certificate reproduces digit-for-digit, and the dedupe-by-points-hash claim
holds on the largest shared-mesh family. Nothing else in 1.0 is changed.

Version 1.0, dated 2026-07-25. Produced by the overnight reading program (R1).
Governs every mesh-quality gate the lab enforces before a solve is admitted as
evidence. Gates change only through the governed path: an edit to
`docs/physics_rules.yaml` carrying its citation, plus a proposal in the agenda
inbox so the owner sees the change. Enforcement code is never edited to move a
threshold silently.

## 1. Purpose and scope

A mesh gate exists to answer one question before solver time is spent: can the
discretization on this mesh support the accuracy claim the result will carry?
This standard states every gate the lab enforces, the literature or source-code
basis for its value, the failure mode it prevents, and the prescribed action on
breach. It also calibrates the bands against what reference-grade grids
actually achieve, using the NASA TMR flat-plate grids on disk under
`models/tmr/` and their checkMesh reports under
`demo-output/website/tmr/runs/*/log.checkMesh`.

## 2. Where the gates live

- Values: `docs/physics_rules.yaml`, section `mesh_quality` (added 2026-07-25
  by this program, with citations inline).
- Enforcement: the geometry workflow (`sdk/workflows/geometry_study.py`,
  `MAX_NON_ORTHOGONALITY`, `MAX_SKEWNESS`, `mesh_validity`,
  `enforce_boundary_skewness`). Wiring the workflow to read the yaml section is
  proposed, not done here; the values written to the yaml match what the
  workflow enforces today, so there is no divergence window.

## 3. Gates

### 3.1 Max non-orthogonality: hard gate 70 degrees, warning band 65 to 70

- Basis: checkMesh itself warns at 70 degrees; the threshold is
  `nonOrthThreshold_ = 70` in the OpenFOAM source
  (`src/OpenFOAM/meshes/primitiveMesh/primitiveMeshCheck/primitiveMeshCheck.C`,
  v2606 tree on disk). snappyHexMesh generates to `maxNonOrtho 65`
  (`etc/caseDicts/meshQualityDict`) and relaxes to 75 only during layer
  addition. 65 is the generation constraint, 70 the acceptance threshold.
- Failure mode: above 70 degrees the non-orthogonal correction to the
  Laplacian becomes large and explicit; with zero or few correctors the
  diffusion term loses accuracy first and boundedness second, and steady
  convergence stalls or oscillates.
- Action: above 70, no validated force from this mesh; the numerical channel
  carries the breach and the fidelity chip is capped. Between 65 and 70, solve
  but record the warning.
- Lab evidence: motorcycle case at max non-ortho 65.0 converged with one
  corrector; the airliner-class hex meshes sit far below the gate.
- Exemption on record, 2026-08-07 (ruling R12,
  `docs/charters/SUPERVISOR_RULINGS.md`): for MODEL-FORM BANDING ONLY, a grid
  that is the reference community's own canonical verification grid may carry
  a band above this gate — first instance the TMR-distributed NACA 0012
  coarse C-grid at max non-orthogonality 85.70 degrees vs this 70-degree
  gate. The ruling owns the exemption and sets its three mandatory
  conditions (stated on the band artifact with the failing number, scoped to
  banding only, grid provenance named); this note is a pointer, not a change
  to the gate. Physics gates and credential verdicts still require compliant
  meshes.

### 3.2 Max skewness: hard gate 4, boundary faces included

- Basis: checkMesh fails skewness at 4 (`skewThreshold_ = 4`, same source
  file). snappyHexMesh generation allows `maxInternalSkewness 4` but
  `maxBoundarySkewness 20`; the lab deliberately enforces 4 on boundary faces
  as well (`enforce_boundary_skewness(MAX_SKEWNESS)` in the geometry workflow)
  because forces are integrated on boundary faces, exactly where the upstream
  default is loosest.
- Failure mode: skewness moves the face interpolation point away from the face
  center; convective fluxes pick up a first-order error that concentrates on
  the very patches the force report reads.
- Action: above 4, trust is capped and the mesh channel carries the value as
  measured; the run may proceed for ranking purposes only.
- Lab evidence: motorcycle case max skew 8.94 on 13 faces capped the result
  below VALIDATED even with converged forces; two overnight missions recorded
  the same cap at skew 5.06 and 8.94.

### 3.3 Aspect ratio: advisory at 1000, never a lone rejection

- Basis: checkMesh reports high-aspect-ratio cells above
  `aspectThreshold_ = 1000` (same source file) but counts this as a failed
  check without stopping anything.
- Calibration, and why this gate must stay advisory: the NASA TMR flat-plate
  grids are reference-grade by construction, and their checkMesh reports on
  disk measure max aspect ratio 74041 (coarse, 816 cells), 69043 (medium,
  3264 cells), 66643 (fine, 13056 cells), each with max non-orthogonality 0
  and skewness at machine precision. The fine grid resolves the wall to
  average y-plus 0.14 and reproduces the flat-plate drag benchmark. A hard
  aspect-ratio gate at 1000 would reject every reference-grade wall-resolved
  RANS grid the lab owns.
- The defensible rule: high aspect ratio is legitimate where the anisotropy is
  aligned with a resolved direction on orthogonal cells (wall-normal
  boundary-layer grids), and dangerous where it coincides with
  non-orthogonality or skew. Gate written to `physics_rules.yaml`: aspect
  ratio above 1000 requires an alignment justification on the record; aspect
  ratio above 1000 together with non-orthogonality above 60 degrees or
  skewness above 2 is a flag for investigation.
- Failure mode prevented: on non-orthogonal or skewed cells, extreme
  anisotropy amplifies the interpolation and correction errors and produces
  stiff, poorly conditioned matrices that stall linear solvers.

### 3.4 Volume ratio: proposed gate, warn below 0.01

- Basis: snappyHexMesh refuses adjacent-cell volume ratios below
  `minVolRatio 0.01` at generation (`etc/caseDicts/meshQualityDict`).
  checkMesh reports the metric under `-allGeometry`. The lab currently has no
  volume-ratio gate; this standard proposes adopting 0.01 as a warning
  threshold, carried in `physics_rules.yaml` and surfaced through proposal
  `r1-mesh-gate-extension`.
- Failure mode: abrupt cell-size jumps degrade linear interpolation weights
  and multigrid coarsening; the error appears as local wiggles near refinement
  boundaries and slow pressure convergence.

### 3.5 Informational metrics, recorded but not gated

- Cell determinant (snappy generation floor `minDeterminant 0.001`) and face
  interpolation weight (`minFaceWeight 0.05`): recorded when checkMesh
  reports them; persistent values at the floor accompany the failure modes
  above rather than causing new ones.

## 4. Calibration table: what reference-grade grids achieve

From `demo-output/website/tmr/runs/*/log.checkMesh` and `record.json`
(OpenFOAM v2606, NASA TMR 2-D zero-pressure-gradient flat plate):

| Grid | Cells | Max non-ortho | Max skewness | Max aspect ratio | Cd |
| --- | --- | --- | --- | --- | --- |
| Coarse | 816 | 0 | 3.3e-15 | 74041 | see record.json |
| Medium | 3264 | 0 | 8.0e-15 | 69043 | see record.json |
| Fine | 13056 | 0 | 2.1e-14 | 66643 | 0.0028343 |

Reading: reference grids are orthogonal and unskewed to machine precision and
buy wall resolution with aspect ratio, not with cell count. The lab's gates on
non-orthogonality and skewness are the load-bearing ones; aspect ratio is a
context signal.

## 5. Change control

1. A gate value changes only in `docs/physics_rules.yaml`, with the citation
   in a comment beside the number.
2. Every change is mirrored by a proposal JSON in the agenda inbox so the
   owner sees it before any surface shows it.
3. A test that pins a gate value is updated only when the new value is the
   cited, defensible one, and the update says so.

## 6. The mesh birth certificate (v1.1, 2026-08-08)

The charter clause this implements is one sentence: every mesh entering an
archive, a pre-registration or a ladder rung carries its checkMesh record at
creation, and a mesh whose record is missing is quarantined from new work
until checkMesh is run and attached.

- **The certificate.** ``birth_certificate.json`` beside the ``polyMesh``
  directory it certifies (`sdk/chief_engineer/mesh_certificate.py`),
  carrying ``points_sha256`` (the hash that binds it to exactly one mesh),
  ``verdict``, ``cells``, ``max_aspect_ratio``, ``max_non_orthogonality``,
  ``max_skewness``, ``hard_errors``, ``generator`` and ``created_at``, with
  the checkMesh log retained beside it. The verdict basis is the audit's:
  hard checkMesh errors (negative volumes, wrong-oriented face pyramids,
  non-orthogonality errors, skewness errors, pathology-range aspect-ratio
  flags) make a mesh ``broken``; the high-aspect-ratio-only signature of the
  reference-grid family is ``flagged`` and admissible per section 3.3;
  ``-allGeometry`` advisories indict nothing.
- **The chokepoints.** All three mesh-cache layers enforce it: the head
  engineer's WSL cache, the DAFoam docker cache (the pyHyp entry path, the
  pathology's generator), and the shock-bench module cache the unsteady
  workflows share. Save writes the certificate from the case's own checkMesh
  record (running checkMesh at save when the workflow has not yet); lookup
  treats an entry without a matching-hash accepted certificate as NOT
  cached, which is the charter's quarantine (pre-rule entries re-mesh once
  and re-enter certified); restore copies the certificate into the case
  beside the mesh. The geometry workflow saves after its quality gate so the
  certificate is the gate's own persisted reading, and the model-form batch
  refuses a solver launch on an absent, unreadable or gate-breaching record
  (R12 family exemptions preserved through the batch's own exemption logic)
  instead of excluding the cell after the wall time is spent.
- **A failed check never certifies.** A certificate is a record of a check
  that ran: a save whose checkMesh record is absent or unparseable writes
  nothing, and the entry stays quarantined at lookup.

## 7. Marine / free-surface meshes (v1.2, 2026-08-11)

### 7.0 Why this section is in *this* file and not the other MESH_STANDARD

`docs/MESH_STANDARD.md` and this file share a name and govern different
questions; both flag the collision on their own face. The split is: that file
governs how a grid **family** is sized and how family scatter is reported; this
file governs whether **one** mesh is admissible, and owns the birth certificate.

Katie's marine brief asks for four things — free-surface mesh discipline,
refinement at the interface, Courant / interface-Courant limits, and what a
birth certificate must record for a free-surface case. Three of the four are
single-mesh admissibility and certificate matters, and the fourth (the
certificate) is defined only here. **So the marine section lands here.** The one
genuinely family-shaped part — that a free-surface refinement ladder must be
anisotropic and must declare its direction — is stated in §7.3 and
cross-referenced from `docs/MESH_STANDARD.md` rather than copied into it
(one home per fact).

Everything below is derived from the F7a dam-break campaign's own measurements.
Where a number is quoted, the case it came from is named. **No value in §7 is
yet enforced in code**; §7.6 says what would have to happen.

### 7.1 The marine-specific claim: cell shape is not sufficient

Every mesh in the F7a ladder passed §3 cleanly — `log.checkMesh` reports
orthogonal cells, skewness ~1e-13, aspect ratio 1 on the isotropic rungs — and
the gate still failed by 11%. What governed the answer was **vertical spacing
measured against a physical film thickness**, a quantity §3 does not look at.

**Therefore: a free-surface mesh is admissible against a physical length scale,
not only against cell-shape metrics.** A checkMesh-clean free-surface mesh with
no recorded layer resolution is not a gate-grade mesh.

### 7.2 The controlling length scale — resolve the thin layer, not the domain

Measured on F7a (`F7_runs/F7a_R1/`, R1 audit, from `0.65/U` read directly):

| dy | film thickness | cells across film | wall velocity gradient | τ_w |
|---|---|---|---|---|
| a/32 = 1.79 mm | ≈ 2.9 mm | ≈ 2 | 999 s⁻¹ (under-predicted ~40%) | 1.0 Pa |
| a/128 = 0.446 mm | ≈ 2.9 mm | ≈ 6–7 | 1607 s⁻¹ | 1.61 Pa |

The six-station mean deviation tracks this directly: +11.6% at dy = a/32,
+9.8% at a/64, **+8.2% at a/128**. The single-variable proof that the resolved
quantity really is bed shear: at the identical a/32 × a/128 mesh, switching the
floor from `noSlip` to `slip` moves the front from +8.2% back to +13.7% — it
undoes the entire gain.

**Rules.**
1. A free-surface case **declares, before meshing, the thinnest physically
   meaningful layer it must resolve**, and the certificate records it.
2. **≥ 6 cells across that layer for a gate verdict.** 2 cells is a diagnostic,
   never a verdict. Basis: the table above — at 2 cells the wall gradient is
   wrong by ~40%, at 6–7 it is resolved, and the deviation stops improving.
3. A case that cannot state its controlling layer thickness is not thereby
   exempt; it is **diagnostic-only** until it can.

### 7.3 Refinement at the interface is anisotropic — and the ladder must say so

Measured on the same ladder, six-station mean deviation:

- **Isotropic refinement** a/8 → a/64 (1,200 → 76,800 cells, 64×):
  +11.8% → +11.1%. **0.7 points.**
- **dy alone** at fixed dx = a/32, a/32 → a/128 (19,200 → 76,800 cells, 4×):
  +11.6% → +8.2%. **3.4 points.**

An isotropic ladder on a stratified problem spends its cells in the direction
that does not matter.

**Rules.**
1. A free-surface refinement ladder **declares its refinement direction and the
   justification, before the ladder is built.**
2. **Anisotropy has its own limit and the ladder must bracket it.** Pushing dy
   alone to a/256 (cell aspect dx/dy = 16) produced an early-time outlier at
   T = 3.90 (+18.1%, inflating that rung's mean to +10.8%) which R1 attributed
   to cell aspect ratio and **reported rather than smoothed away**. So the
   ladder must include **at least one rung that varies dx at the finest dy**, to
   separate genuine dy convergence from an aspect-ratio artifact. F7a's
   `res64y128_base` is that rung and it is why the a/256 outlier is
   attributable at all.
3. **§3.3's aspect-ratio advisory does not protect against this.** The advisory
   sits at 1000; the value that bit here was **16**. The protection is the
   declared ladder and the certificate field in §7.5, not a threshold.
4. Family growth-rate practice remains `docs/MESH_STANDARD.md`'s; this rule adds
   the direction requirement, it does not restate the sizing formula.

### 7.4 Courant and interface-Courant limits

`interFoam` carries two independent limits: `maxCo` on the velocity field and
`maxAlphaCo` on the interface. F7a ran `maxCo 0.5`, `maxAlphaCo 0.5`,
`nAlphaSubCycles 1`, `nAlphaCorr 2`.

**The reporting defect this rule exists to prevent, measured.** The original F7a
report recorded *"Max Courant ≈ 0.52 (capped target 0.5)"*. That is **the last
timestep's value**. The maximum over the run, from `log.interFoam`, is
**0.7416**, with interface Courant **0.6401**. An `adjustTimeStep` run overshoots
its own cap between adjustments, and the final line of the log is not the
maximum.

**Rules.**
1. The recorded Courant number is the **maximum over the run**, taken from the
   solver log, **for both `Co` and `alphaCo`**, never the final line.
2. **`maxAlphaCo` ≤ `maxCo`.** The interface carries the sharpest gradients.
3. A case run with `adjustTimeStep` records **whether its cap was exceeded and
   by how much**. Exceedance is normal; an unrecorded exceedance is not.
4. **Do not spend a ladder on the Courant knobs.** Measured, at a/16 against a
   +13.5% baseline: tightening `maxCo` 0.5→0.2, `maxAlphaCo` 0.5→0.1 and
   `nAlphaSubCycles` 1→3 gave **+15.1% — worse**; and separately, a 2.4× larger
   fixed timestep at fixed mesh moved the answer by **< 1 point**. On this case
   these are stability and admissibility controls, **not accuracy knobs**.
   Recorded here so the experiment is not repeated by the next agent.

### 7.5 What a birth certificate must record for a free-surface case

In addition to every §6 field, `birth_certificate.json` for a free-surface mesh
records:

| field | why, and what it prevents |
|---|---|
| `free_surface: true` | selects this section's rules; absent ⇒ §7 not applied |
| `dy_at_interface_m`, and the same as a fraction of the case's characteristic length | §7.2's controlling spacing. Whole-mesh `dy_min` is not a substitute — it can be set somewhere the interface never goes |
| `resolved_layer_thickness_m` | the layer §7.2 requires the case to declare |
| `cells_across_layer` | the §7.2 count. **Absent or < 6 ⇒ diagnostic-only, never a gate mesh** |
| `cell_aspect_ratio_at_interface` (dx/dy there) | §7.3's measured hazard at a value (16) three orders below §3.3's advisory. Distinct from checkMesh's whole-mesh maximum |
| `interface_normal_direction` | the direction `cells_across_layer` is counted in; without it the count is unverifiable |
| `max_Co_over_run`, `max_alphaCo_over_run`, each with the log line quoted | §7.4's defect, closed by construction |
| `setfields_sha256` | a free-surface result is a function of its initial interface placement as much as of its mesh. F7a's config hashes already include `setFieldsDict` for this reason |
| `alpha_min_over_run`, `alpha_max_over_run` | boundedness. F7a's gate case measured `Min(alpha.water) = -2.7e-06`, within MULES tolerance |

**Proposed gate, not yet adopted** (following §3.4's convention for a proposed
value): flag any solve whose α leaves **[−1e-4, 1+1e-4]**. Basis is calibration
only — F7a's clean runs measured −2.7e-6, and its feasibility pass accepted
≈ −1e-6 — so the value is a calibrated proposal, **not** a threshold read from
source. It needs a citation or a wider calibration set before it is enforced.

### 7.6 Where these values live, and what is not done

Per §5, no gate value is enforced until it is written to
`docs/physics_rules.yaml` with its citation and mirrored by a proposal in the
agenda inbox.

**None of §7 is in `physics_rules.yaml` today, and no enforcement code reads
it.** §7 is house practice with its evidence attached, at the same maturity as
§3.4's proposed volume-ratio gate. Making it enforceable requires: a
`mesh_quality.free_surface` block in the yaml; extension of
`sdk/chief_engineer/mesh_certificate.py` to write the §7.5 fields; and a
proposal so the owner sees it. That work is **not** done here and should not be
described as done.

**Calibration honesty.** Every number in §7 comes from **one case family** — the
F7a dam break, a 2D laminar VOF collapse on a dry bed. The 6-cell rule, the
anisotropy result and the Courant non-effect are measured **there**. A hull
wave-resistance case has a different controlling scale (wave height and
wavelength, not a bed film) and §7.2's rule will need its own calibration when
F7 rung (b) is run. Applying the *form* of these rules to a hull case is
intended; transplanting the *numbers* is not.

## Sources

- F7a dam-break campaign, R1 audit: `demo-output/website/campaign/F7_marine_free_surface.md`
  §§R1.2–R1.6, and the tracked cases under
  `demo-output/website/campaign/F7_runs/F7a_R1/` with their `CASE_PROVENANCE.txt`,
  `log.checkMesh` and `log.interFoam`. Every §7 number is traceable to one of these.
- `demo-output/website/campaign/F7a_REGATE_SPEC.md` — the measurement definition
  §7.2's deviations are quoted under, and the resolution floor §7.2 restates.
- OpenFOAM v2606 source, primitiveMeshCheck.C, checkMesh thresholds.
- OpenFOAM v2606 source, caseDicts meshQualityDict, snappyHexMesh generation
  defaults.
- NASA Turbulence Modeling Resource, 2-D zero-pressure-gradient flat plate
  grids, as meshed and checked on disk under `models/tmr/` and
  `demo-output/website/tmr/runs/`.
- Certonomous Numericist knowledge base, `docs/NUMERICS_KNOWLEDGE.md`,
  validated facts 2 and 7.

---

## 8. TWO STANDING CONSTRAINTS ON MESH LADDERS (v1.3, 2026-08-25)

**Ruled by the cfd supervisor 2026-08-25, on the F1 (ONERA M6) ladder, which failed §3's
non-orthogonality gate at every level and could not be repaired by amendment.**
Evidence: `verification/runs/F13_ONERA_M6_runs/R0_TERMINAL.md`,
`verification/campaign/F13_RESULTS.md`, and CORRECTION 1 at the foot of
`verification/campaign/F13_ONERA_M6_PREREGISTRATION.md`.

### 8.1 BUILD BEFORE YOU FREEZE

> **No cfd mesh-ladder pre-registration is frozen until at least one level has been BUILT,
> `checkMesh`'d, and SHOWN ADMISSIBLE against the gates that registration will carry.
> Template speed does not exempt it. A ten-line pre-registration form can carry a MEASURED mesh
> line as easily as an ASSUMED one.**

**What it cost to learn.** F1's ladder was frozen from an assumed mesh. It was arithmetically
exact — cell counts to the unit, `r = 2.000000` on both pairs, node nesting **0.000e+00 m** read
from the built `polyMesh` under a live planted control — and **inadmissible at every level**:
max non-orthogonality **84.64 / 86.02 / 86.78°** against a **≤ 70°** gate, **worsening under
refinement** (severe faces **36 → 216 → 1,440**, asymptoting toward 90°). **A fixed fraction of the
mesh, not a marginal miss — so no finer level could ever have cleared it.** Every core-minute of
R1–R4 that the registration costed was unspendable from the moment the ladder was written.

This is the same shape as the F12 attempt-1 failure, and the lesson had **already been written down
in this team's own board** before F1 was dispatched. **L-221/L-222 applies to rulings, not only to
`libs` entries: a lesson is not applied until EVERY call site asserts it**, and the call site that
failed here was the dispatch itself.

### 8.2 `blockMesh` REFUSING IS A DIAGNOSTIC, NOT AN OBSTACLE TO ROUTE AROUND

> **If `blockMesh` cannot express the topology, THE TOPOLOGY IS REDESIGNED — NOT BYPASSED.**
> Hand-writing `constant/polyMesh` is a materially weaker provenance path: it bypasses the one tool
> whose refusals are a check on the block structure.

**What it cost to learn.** F1's tip fill — a lens whose leading- and trailing-edge ends are single
lines — was refused by `blockMesh` v2606 **twice**:

| how it was written | what `blockMesh` / `checkMesh` did |
|---|---|
| repeated-vertex prism block, `hex (0 1 2 0 4 5 6 4)` | **`blockMesh` ABORTS, rc = 134**, `FOAM FATAL ERROR` |
| two distinct but coincident vertices | builds, then `checkMesh`: **`***Zero or negative face area detected`, 48 zero-area faces, max skewness 3.35e+148, `Failed 2 mesh checks`** |

The refusal was **routed around** by writing `polyMesh` directly, where the collapsed ends become
legal prism cells. **The mesh then built cleanly and failed admission at 84.64°.** The tool had been
right: the topology it rejected is the topology that could not pass. **A generator that cannot be
refused is a generator with no second opinion in it.**

### 8.3 Scope

Both constraints bind **cfd mesh ladders**. Neither is retroactive: ladders already frozen are not
re-opened by this section. Neither alters any gate in §3 — §3's thresholds are unchanged, and 8.1
governs **when** a ladder may be frozen against them, not **what** they are.

---

## 9. GRID-LEVEL COUNT, AND THE SIMILARITY CLAUSE THAT GOES WITH IT (v1.4, 2026-08-25)

**Appended at the foot. Lines whose number changed above this section: 0.** Nothing above is
edited, struck or renumbered by this section.

**A version discrepancy recorded rather than silently repaired.** This file's header (line 3) reads
`Version 1.2, dated 2026-08-11`; §8 declares itself `v1.3, 2026-08-25`. The header was not bumped
when §8 landed. **It is not bumped here either**, because editing line 3 would move every line
number above this section and break the zero-lines-changed assertion that other records cite. The
authoritative version of this document is the **highest section version**, which is now **v1.4**.
Repairing the header is a separate, disclosed edit for whoever takes it.

### 9.1 THREE LEVELS — Sanaa's ruling, 2026-08-25, quoted verbatim

Ruled by Sanaa in her own session turn of 2026-08-25. Quoted verbatim and attributed:

> Grid standard ruled: 3 levels. A converging three-level family with observed order and GCI is the
> lab's gate standard (Roache-standard minimum). More levels are a research option, never a gate
> requirement. Update the standards doc; the pending grid-standard desk item is closed with this.

**What this settles:** three is both the **minimum** and the **sufficient** level count for a gate.
A fourth level is a **research option** and is **never owed**. No agent may require a fourth level
of another team, and no gate may be written that presumes one. The pending grid-standard desk item
is **closed** with this ruling.

**WHAT THIS DOES NOT RELAX, and the distinction is the whole point.** The ruling fixes a *count*.
It touches no other condition on a gradeable family. All three of the following continue to bind
in full, unchanged:

1. The family must **CONVERGE**. Standing rule 5 is untouched: a triple that is `DIVERGENT`,
   `STAGNANT`, `OSCILLATORY` or `EXACT` is `NOT A RESULT` whatever its value, and a level that is
   not iteratively converged or not plateaued is `NOT A RESULT` before the triple is even read.
2. An **observed order** must be computed and printed.
3. A **GCI** must be computed and printed, at `Fs = 1.25`, and **never quoted when the three values
   are not monotone**.

**Three levels that do not converge are not a gate. They are three numbers.** A team that reads
this ruling as permission to ship a three-level family without order and GCI has read it backwards.

### 9.2 THE SIMILARITY CLAUSE — letter versus spirit, and the ruling on the far-side branch flip

Ruled by the cfd supervisor, 2026-08-25, under Sanaa's desk-item disposal rule of the same date:
referred with recommendation and reasoning, **ADOPTED unless she rules otherwise within one day**,
recorded `[lab-attributed]`. **Overrulable.**

**The occasion.** F12's ladder generator sets the far-side wall-normal grading of the two wake
blocks from an **absolute** first cell of 0.3 chord, with **no dependence on the level**
(`F12_PREREGISTRATION.md:539`, reading `sdk/workflows/tmr_verification.py`). Evaluated across the
ladder, the total expansion returned is **3.747165 / 1.084468 / 1.000000** at coarse / medium /
fine: at the fine level the requested first cell exceeds the uniform spacing `length / n`, the
generator's own guard `if first_cell >= length / n: return 1.0` fires, and the fine level's wake
blocks get a **UNIFORM** far-side distribution where the coarse level's are graded **3.75:1**.

**The question put to me.** Gate A tests max non-orthogonality and max skewness. A branch-flipped
ladder can pass gate A at **every** level — a uniform wake block is, if anything, *better*
conditioned than a graded one. So by the **letter** of §3, the ladder is admissible. By the
**spirit** of a Roache ladder, the three levels are no longer the same experiment.

**RULING — the spirit governs, and this is not a discretionary reading.**

> **A refinement recipe that FLIPS A BRANCH across the levels produces a family that is NOT a
> Roache ladder, whatever §3 says about each mesh individually. Such a family is `NOT A RESULT`
> under standing rule 5, and gate A passing at every level does not save it.**

**Three reasons, in order of force.**

1. **§3's gates are per-MESH; a Roache triple is a claim about a FAMILY.** Every gate in §3 grades
   one mesh in isolation. None of them can see a relationship *between* levels, and it is exactly
   that relationship the observed order is computed from. A per-mesh gate that passes three times
   has said nothing whatever about whether the three are comparable. **Reading §3 as sufficient for
   ladder admissibility is a category error, not a lenient interpretation.**
2. **The already-standing similarity ruling covers this on its face.** This team has ruled that *a
   mesh ladder is admissible as a Roache ladder only if the refinement is geometrically similar —
   the first cell height and the expansion ratio scale WITH the mesh, and the refinement recipe is
   otherwise held FIXED* (`F12_PREREGISTRATION.md:616-619`). An expansion ratio going 3.75 -> 1.08
   -> 1.00 while the mesh refines by two is the **negation** of "scales with the mesh". §9.2 does
   not extend that ruling; it applies it to a case that tried to slip under it.
3. **A branch flip is WORSE than a drift, and the difference matters.** A recipe that drifts
   smoothly across levels contaminates the observed order continuously and might, with effort, be
   bounded. A guard that fires at one level and not the others makes the fine level a
   **discontinuously different experiment**. There is no expansion of the error in `h` that
   contains it, so the observed order it produces is not an order of anything.

**THE HAZARD THIS CLAUSE EXISTS TO CATCH, stated plainly.** The dangerous property of this defect
is that **it is invisible to every check the lab currently runs.** It passes gate A. It passes
`checkMesh`. It passes the nesting and cell-count assertions, because the *node positions* can
still nest exactly. `scripts/roache_triple.py` **cannot detect it** — the pre-registration says so
at `:468`. It is read only from the dictionary-writing **code**, never from a built mesh. **A
ladder can therefore be dead on arrival while every instrument reports green.**

**THE OPERATIONAL CONSEQUENCE — a required, checkable deliverable.**

> **Every cfd mesh ladder must record, per level, the ACTUAL VALUE of every grading and
> first-cell parameter its generator used — read back from the written dictionary or the built
> mesh, never from the parameter that was requested.** A ladder whose per-level graded values are
> not recorded cannot be shown similar, and a ladder that cannot be shown similar is not gradeable
> as a Roache ladder.

This is deliberately a **read-back**, not an assertion. The F12 defect is precisely a case where
the requested parameter was **identical at every level** — that constancy is what *caused* the
flip — so a check that compared requested values would have reported perfect similarity. **The
requested value is the thing that lied. Only the returned value tells the truth.** It belongs in
the §6 mesh birth certificate for any ladder level.

### 9.3 Scope of §9

§9.1 is **Sanaa's ruling and is lab-wide**. §9.2 binds **cfd mesh ladders** and is offered to other
families rather than imposed on them. Neither is retroactive: **ladders already frozen are not
re-opened by this section**, and F12's and F1's closed verdicts are not regraded by it. Neither
alters any gate value in §3 — §3's thresholds are unchanged. §9.2 governs **whether a set of meshes
is a LADDER**, not what any single mesh must achieve.

---

## 10. `High_order_grid_convergence.pdf` IS NOT A SOURCE FOR THIS DOCUMENT, AND THE ONE THING IT DOES SAY ABOUT GRIDS (v1.5, 2026-08-25)

**Appended at the foot under standing rule 6. Version 1.4 → 1.5. Lines whose number changed
above this section: 0. THIS SECTION MOVES NO GATE, NO THRESHOLD, NO BAND, NO CAP AND NO
LABEL.** §3's values are untouched; §9.1's three-level ruling is untouched and is **not**
re-sourced by anything here.

### 10.1 The prohibition, placed in the file where a lane will look for it

`docs/standards/High_order_grid_convergence.pdf` sits in this directory and **its filename names
a subject it does not have.** Title-page verified three times independently (standing rule 15,
L-144): by cfd at `01fcb3d8`, by heat-transfer at
`docs/campaigns/T-family/STANDARDS_INTAKE_RULING_2026-08-25.md`, and by the cfd supervisor
personally on 2026-08-25. It is:

> *High-order accurate, low numerical diffusion methods for aerodynamics.*
> John A. Ekaterinaris, **Progress in Aerospace Sciences 41 (2005) 192–300**,
> `doi:10.1016/j.paerosci.2005.03.003`. sha256 `dd5b10ca…f035a`.

Measured over its full 66,033-word text with **word-boundary discriminators**: `Roache` **0**,
`GCI` **0**, `Richardson` **0**, `grid refinement` **0**, `mesh refinement` **0**,
`verification` **0**.

> **NO CLAUSE OF THIS STANDARD MAY CITE THAT DOCUMENT, AND NO CLAUSE OF THIS STANDARD DOES.**
> A sentence of the form *"the grid-convergence literature says X, per
> `High_order_grid_convergence.pdf`"* — in this file, in `VERIFICATION_CHARTER.md`, or in the
> GCI/Roache rows of `docs/NUMERICS_KNOWLEDGE.md` — would be a **fabrication**.

**§9.1's three-level ruling comes from Sanaa, quoted verbatim there, and from Roache. It owes
this paper nothing.** That is stated here because §9.1 and this PDF landed in this directory on
the same day, and the coincidence is exactly how a false attribution gets made later.

The naive substring `roache` returns **17** hits in that text. **All 17 are the substring inside
`app-roache-s`.** Full provenance and the count evidence:
`docs/standards/High_order_grid_convergence_PROVENANCE.md`.

### 10.2 The one thing it does say that a mesh ladder must carry: a GCI at a vortex core bounds MESH error only

The paper's thesis, abstract p. 192, is that **the main deficiency of widely available
second-order accurate methods for vortex-dominated flows is the numerical diffusion of vorticity
to unacceptable levels.** The full quotation and its consequences are recorded as **`N-C2`** in
`docs/NUMERICS_KNOWLEDGE.md`. What that means for a **ladder**, and therefore for this standard:

> **A three-level family taken at a vortex-core, tip-vortex or wake station may be perfectly
> `CONVERGING`, with a clean observed order and a small GCI, and still sit outside the true
> error — because the GCI bounds the MESH contribution to a discrepancy that also has a SCHEME
> contribution, and the scheme contribution does not refine away at the same rate.**

**This is a DISCLOSURE requirement, not a gate.** It adds no threshold and rejects no mesh:

- A ladder reporting a GCI at such a station **states beside it that the GCI bounds mesh error
  only**, and names the discretization order actually used.
- It does **not** claim, from a converging triple at such a station, that the remaining
  discrepancy against experiment is mesh-resolvable.

This is `N-T2`'s failure mode — *a `CONVERGING` Roache triple can arm a band narrower than the
finest level's actual error* — reached by a second route, and it is recorded because the two
routes call for the same disclosure.

### 10.3 What is referred elsewhere and NOT decided here

Whether `VERIFICATION_CHARTER.md` should carry §10.2's caveat as a **charter clause** binding
every family is **the verification team's ruling, not cfd's**, and it is referred rather than
taken. Retiring or widening a gate or a charter clause is reserved (`ESCALATION_CHARTER.md`);
this section deliberately does neither.

### 10.4 Scope of §10

§10.1 is a **prohibition on sourcing** and is lab-wide, because the fabrication it prevents
would be lab-wide. §10.2 binds **cfd mesh ladders** and is offered to other families rather than
imposed. Neither is retroactive: **no frozen ladder is re-opened and no closed verdict is
regraded by this section.**
