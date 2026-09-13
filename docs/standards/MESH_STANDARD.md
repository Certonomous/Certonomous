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

### 10.5 Observed-order floor symbols — one name, one number (note of 2026-08-26, chief ruling [lab-attributed]; no threshold moves)

The shared instrument `scripts/roache_triple.py` defines **`STAGNANT_FLOOR = 0.5`** (0 < p < 0.5
is `STAGNANT`) and **`P_MIN = 0.05`** (|p| < 0.05 is `DEGENERATE`; measured at `c525c247`). Some
frozen per-family comparators define a symbol named **`P_MIN = 0.5`** as their observed-order
floor (`analyse_t3_rff.py:34`, `analyse_t4b.py:60`, `analyse_t11.py:48`), while
`analyse_t5.py:34` has `P_MIN = 0.05`. **Verdicts are equivalent — every p below 0.5 is
`NOT A RESULT` in both lineages (`STAGNANT` in the shared instrument, the floor in the others), and
the 0.05 `DEGENERATE` band lies inside that.** The hazard is the symbol carrying two numbers a
decade apart across frozen files. **Rule for NEXT registrations: use the shared instrument's names
(`STAGNANT_FLOOR` / `P_MIN`) with the shared instrument's numbers, or call `grade_ladder` and
define neither.** Frozen files are not edited; no verdict, threshold or band moves. Sanaa's desk
holds this as information, not as a question.

---

## 11. ASPECT RATIO AND CELL-VOLUME RATIO BECOME REPORTED MESH-ADMISSION EVIDENCE — AND NO THRESHOLD IS SET FOR EITHER (v1.6, 2026-08-27)

**Appended at the foot under standing rule 6. Version 1.5 → 1.6. Lines whose number changed
above this section: 0.** Nothing above is edited, struck or renumbered by this section.

**THIS SECTION SETS NO THRESHOLD AND MOVES NO GATE, NO BAND, NO CAP AND NO LABEL.** §3.1's
70°, §3.2's 4, §3.3's advisory at 1000 and its compound flag, §3.4's proposed 0.01 and §7.5's
proposed α bracket are all untouched, and no value is written to `docs/physics_rules.yaml` by
this section. It changes exactly one thing: **two quantities that were optional to record become
required to record.** *(Header discrepancy carried forward per §9: line 3 still reads
`Version 1.2`; the authoritative version is the highest section version, now **v1.6**, and the
header is deliberately not edited here because editing it would move every line number above.)*

### 11.1 The occasion, measured

`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/coarse/log.checkMesh`, OpenFOAM
v2606, F12 RAE 2822 attempt-2 coarse level, 23,040 cells:

| line | what the log says |
|---|---|
| 93 | `Max aspect ratio = 805.199 OK.` |
| 95 | `Min volume = 1.30653e-09. Max volume = 41.8474.  Total volume = 13825.7.  Cell volumes OK.` |
| 96 | `Mesh non-orthogonality Max: 51.1237 average: 17.375` |
| 99 | `Max skewness = 0.95723 OK.` |
| 102 | `Mesh OK.` |

`checkMesh` returned **`Mesh OK.`** The mesh clears §3.1 (51.12 < 70), §3.2 (0.957 < 4) and
§3.3's advisory (805.199 < 1000). Its **whole-mesh cell-volume ratio**, 41.8474 / 1.30653e-09 =
**3.2029e+10**, is a quantity **this standard does not name anywhere, `docs/physics_rules.yaml`
does not carry, and the §6 birth certificate does not record.**

**The sharper finding, and it is the one that motivates §11.4.** The same ladder's own
certificate file,
`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/birth_certificates.json`, records
`"max_aspect_ratio": null` at **all three levels** — while `medium`'s and `fine`'s logs read
`***High aspect ratio cells found, Max aspect ratio: 2842.46 / 1760.97` and end
`Failed 1 mesh checks.` The builder
(`.../build_ladder_attempt2.py`) contains **no occurrence of the string `aspect`**: it never read
the field it left a slot for. Gate A was recorded `PASS` at all three levels with the
aspect-ratio column empty at all three.

Across the lab's whole certificate population, measured 2026-08-27: **64 mesh records carry a
`max_aspect_ratio` key; 61 carry a value and 3 are null (all three are F12 attempt-2's levels);
and 64 of 64 carry NO cell-volume field of any kind.** So the aspect dimension is ~95 % covered
with one measured hole, and **the volume dimension is 0 % covered.**

### 11.2 WHY THIS SECTION SETS NO THRESHOLD — and this refusal, not the reporting rule, is the point of it

**Setting a number here from F12 would be the mesh-quality form of choosing a gate to fit the
answer.** Standing rule 2 freezes a solver gate before the run precisely so the gate cannot be
selected once the answer is visible. A mesh gate written *after* looking at the mesh that
crashed enjoys none of that protection and deserves none of the authority.

**And F12 is weaker evidence than it looked when this amendment was ordered.** F12's Arm A
**exonerated the mesh**: the crash cell, 17152, sits in the **44th–58th percentile in every
dimension**, while the mesh's real extremes — aspect ratio 805.199, non-orthogonality 51.124 at
the trailing edge, minimum cell volume 1.307e-09 at the leading edge — are **nowhere near the
crash**. A threshold fitted to F12 would therefore have **gated against cells that had nothing
to do with the failure**, and would have done it carrying a standard's authority.

*Disclosed, because the strength of a claim is part of the claim:* Arm A's percentile figures
are recorded as supervisor triage prose in `docs/LAB_STATE.md` (cfd section, 2026-08-27) and
have **no artifact of their own under `verification/runs/F12_runs/`**. **No requirement in §11
rests on them.** They are stated here as the reason a threshold is *withheld*, which is the one
direction in which weak evidence is safe to act on.

**The transferable rule, and it is the reason this section exists:**

> **A number that is WRONG in a standard is more expensive than a number that is MISSING from
> one.** A missing number produces a survey. A wrong number produces refusals of admissible
> meshes, retro-invalidated results, and the false confidence that the dimension is under
> control. **Measurement precedes the threshold: a dimension is first made VISIBLE across the
> whole population, then a threshold is argued from the distribution — never from the one case
> that made somebody look.**

§3.3 already records this mistake from the other side and is the lab's own proof of the rule: a
hard aspect-ratio gate at 1000 would reject **every** reference-grade wall-resolved RANS grid
the lab owns, the NASA TMR flat plates measuring 66,643 to 74,041 with non-orthogonality 0 and
machine-precision skewness. That gate was avoided **because the population had been measured
first.** §11 asks the same of its own successor.

### 11.3 The three quantities, disambiguated — because two of them are routinely conflated

Field names below were verified 2026-08-27 against real `log.checkMesh` files in this
repository, not from memory. The verification log for the first two is
`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/coarse/log.checkMesh`; for the
flagged aspect-ratio form,
`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/medium/log.checkMesh`; for the
third, `verification/runs/GEN_ALT_runs/alt_refined/log.checkMesh`.

| # | quantity | how it appears in `log.checkMesh` | status before §11 |
|---|---|---|---|
| (a) | **max aspect ratio** (whole mesh) | **two mutually exclusive labels.** Below `aspectThreshold_ = 1000`: `    Max aspect ratio = 805.199 OK.` (**space, `=`, space**). At or above it: ` ***High aspect ratio cells found, Max aspect ratio: 2842.46, number of cells 34` (**colon, no space before it**), and the run then ends `Failed N mesh checks.` | §3.3 advisory; `aspect_ratio_advisory: 1000.0` in `docs/physics_rules.yaml`; `max_aspect_ratio` already a §6 certificate field |
| (b) | **whole-mesh cell-volume ratio** = max cell volume / min cell volume | **NOT PRINTED BY `checkMesh` AT ALL.** Derived from `    Min volume = 1.30653e-09. Max volume = 41.8474.  Total volume = 13825.7.  Cell volumes OK.` | **named nowhere** — not in this standard, not in `physics_rules.yaml`, not in the certificate |
| (c) | **adjacent-cell (face) volume ratio** | `    Face volume ratio : minimum: 0.0528967 average: 0.877159` — printed **only** under `checkMesh -allGeometry` | §3.4's proposed 0.01; `min_volume_ratio_warn: 0.01` in `physics_rules.yaml` |

**(b) and (c) are different quantities and §3.4 governs only (c).** The 3.2029e+10 figure of
§11.1 is (b). Conflating them would let a reader believe §3.4 already covers the F12 observation;
it does not, and §11 does not touch §3.4.

**Two traps in (a), both measured, both live.** First, a reader matching only the `=` form sees
**761 of the lab's 916 logs and silently misses exactly the 155 pathological ones** — the failure
is invisible because it returns a plausible number for most meshes. `sdk/chief_engineer/mesh_certificate.py:93`
matches both forms (`Max aspect ratio[:=\s]+`); F12's own builder matched neither. Second, the
`=` form carries **a space on both sides of the `=`** while the `:` form has **no space before the
colon**; a pattern of the shape `Max aspect ratio[:=]` matches neither the `=` form nor a run of
`grep` written in haste. *(This was demonstrated live while writing this section: exactly that
pattern returned nothing on two logs that plainly contain the field.)*

### 11.4 THE OBLIGATION — measured and reported, now, with a named home

> **Every cfd mesh entering a pre-registration, a ladder rung or an admission record RECORDS
> its max aspect ratio and its whole-mesh cell-volume ratio, read back from its own
> `log.checkMesh`, in that mesh's §6 birth certificate.**

**No value of either quantity makes a mesh inadmissible under this section. What makes a record
INCOMPLETE is the ABSENCE of the number, never its size.** §11 rejects no mesh.

**The home.** The §6 mesh birth certificate: `birth_certificate.json` beside the `polyMesh` it
certifies, or — for a ladder that writes one aggregate file per family, as F12's
`birth_certificates.json` does — the per-level record inside that file. Fields:

| field | definition | new here? |
|---|---|---|
| `max_aspect_ratio` | the value from **either** label form of §11.3(a) | **no** — already a §6 field; §11 requires it be non-null |
| `aspect_ratio_flagged` | boolean, true iff the log carries `***High aspect ratio cells found` | yes |
| `min_cell_volume`, `max_cell_volume` | the two values on the `Min volume = … Max volume = …` line | yes |
| `cell_volume_ratio` | `max_cell_volume / min_cell_volume`, **stated as derived**, not as a checkMesh output | yes |
| `geometric_directions` | the count on `Mesh has N geometric (non-empty/wedge) directions` | yes — see the 2-D caveat below |
| `checkMesh_log` | absolute path of the log every value above was read from | already present in practice; made explicit |

**The reader carries a planted control (standing rule 3).** A reader that reports `null`, or a
ratio of 1, must first have been shown able to read a non-null value from a log of **each** label
form and to derive a non-trivial ratio. F12's three nulls are exactly the failure this clause
prevents, and they were produced by a reader nobody had asked to see a value.

**The 2-D caveat, measured on the occasion case.** F12 coarse reports `Mesh has 2 geometric
(non-empty/wedge) directions`, and its `Min volume` equals its `Minimum face area` to every
printed digit (1.30653e-09 both). In a 2-D mesh with a unit-thickness empty direction the
cell-volume ratio is an **in-plane area ratio**, not a volume ratio, and is not dimensionally the
same statistic as a 3-D mesh's. Hence `geometric_directions` is required alongside it, and
§11.5's distribution is split on it.

**What is NOT done here, said plainly so it is not described as done.**
`sdk/chief_engineer/mesh_certificate.py` does not yet emit the four new fields; it parses (a) and
not (b). §11 **names** the fields and does not edit that code — a separate, disclosed change.
Until it lands, the case writes them into the certificate file it already produces. A
mesh-admission record without them is **incomplete**, and §8.1's *"SHOWN ADMISSIBLE"* is not shown
by a record with an empty column.

### 11.5 THE SURVEY — **MESH DIMENSION SURVEY, MDS-1** — named, sized, and owned

A deferral with no named survey is a deferral that never lands. MDS-1 therefore has a
population, a statistic, a home, an owner and an exit condition.

**Population, counted 2026-08-27 with `find . -name 'log.checkMesh*' -type f` — measured, not
estimated:**

| class | `log.checkMesh` files |
|---|---|
| `verification/runs/` (40 distinct campaigns) | **837** |
| — of which `T-family/` | 278 |
| — of which `ansys_verification/` | 134 |
| — of which `F14-cooling-ladder/` | 123 |
| — of which `F1_MESH_TRIALS_2026-08-25/` | 50 |
| — of which `MODEL_FORM_runs/` | 36 |
| — of which the remaining 35 campaigns | 216 |
| `mission-output/geometry-study/` | 24 |
| `cases/mega-batch/` | 21 |
| `cases/ansys_verification/` | 17 |
| `cases/tmr/` | 12 |
| `mission-output/` other (skew-experiments 2, uq-studies 1, nasa-hump 1, ahmed-body 1) | 5 |
| **TOTAL** | **916** |

Two population facts recorded because they change how the survey must be run:
- **`cases/committee-grids/` exists and holds ZERO `log.checkMesh` files.** It contributes
  nothing and is named here so a later reader does not assume it was overlooked.
- **Two of the 916 sit inside a hidden directory**
  (`verification/runs/F14-cooling-ladder/K0cG_runs/.attempt1_stale/`). `find` sees them; a
  recursive `**` glob does **not** enter dotted directories, and `grep -r` in this environment
  honours ignore files. **MDS-1 enumerates with `find` and states its enumerator**, or its
  coverage figure is a false zero of exactly the kind standing rule 3 exists to catch.

**Feasibility, measured — MDS-1 costs ZERO new compute for the two quantities §11 names:**
- a `Max aspect ratio` line is present in **916 of 916** logs (761 in the `=` form, 155 in the
  `:` form; the two sets are disjoint and exhaustive);
- a `Min volume = … Max volume = …` line is present in **916 of 916**, and the ratio is derivable
  with `min > 0` in **916 of 916**;
- by contrast a `Face volume ratio` line — §11.3(c), §3.4's quantity — is present in only
  **66 of 916 (7.2 %)**, because the rest were not run with `-allGeometry`. **That is why MDS-1
  surveys (a) and (b) and not (c), and why §11 leaves §3.4 alone:** 93 % of the population cannot
  answer (c) without re-meshing or re-checking.

**Statistic to be taken.** Per log: max aspect ratio and its label form; min and max cell volume
and the derived ratio; `geometric_directions`; max non-orthogonality; max skewness; the
`Mesh OK.` / `Failed N mesh checks.` verdict; and the class. Reported as **the full empirical
distribution** (min, deciles, median, 90th / 95th / 99th percentile, max) of each of (a) and (b),
**split by 2-D versus 3-D**, and **cross-tabulated against non-orthogonality and skewness** —
because §3.3 already asserts that high aspect ratio is dangerous *in company* and harmless when
aligned, and MDS-1 must be able to **test** that assertion rather than inherit it.

**Home:** `verification/runs/MDS1_runs/`, with the reader and its planted control beside the
result. **Owner:** the cfd supervisor.

**WHAT A LATER DATED AMENDMENT NEEDS IN ORDER TO SET A THRESHOLD — all four, not three:**

1. **The MDS-1 distribution**, filed at the home above, its reader carrying a live planted
   control that is shown able to read a non-null value from **both** label forms and to derive a
   non-trivial ratio.
2. **At least one mesh whose failure is attributed to the proposed dimension BY A MECHANISM, not
   by correlation.** **F12 does not supply one** — Arm A exonerated it. Every entry in §3 states
   the failure mode its gate prevents; a threshold with no failure mode is a number.
3. **A statement of what the proposed threshold would have REJECTED in the surveyed population,
   by name and count** — including how many currently-PASSing lab results it would
   retro-invalidate and how many reference-grade grids (NASA TMR, Ansys VM, community canonical
   grids under the R12 exemption) it would refuse. This is the test §3.3 applied and passed;
   every successor answers it before adoption, not after.
4. **§5's governed path:** the value in `docs/physics_rules.yaml` with its citation beside the
   number, and a proposal in the agenda inbox so the owner sees it.

**Anti-deferral clause.** A record that cites §11 to say *"threshold deferred to MDS-1"* while
`verification/runs/MDS1_runs/` **does not exist** is citing a survey that has not been started,
and **must say so in those words.** The survey's absence is a reportable state, not a silence.

### 11.6 Scope of §11

- §11 binds **cfd meshes**; it is offered to other families rather than imposed on them.
- **Not retroactive.** No frozen ladder is re-opened, no closed verdict is regraded — **F12's
  included.** §11.1 reads F12's records as evidence of a reporting gap; it does not regrade F12.
- §11 **sets no threshold and moves no gate value.** §3's and §7's numbers are unchanged, and
  nothing is written to `docs/physics_rules.yaml` by this section.
- §11 does not amend any charter, and does not edit
  `sdk/chief_engineer/mesh_certificate.py`; the four new certificate fields are named here and
  their implementation is a separate, disclosed change.

---

## 12. §11 IS CORRECTED IN SIX PLACES, MDS-1 IS STOOD UP, AND NO THRESHOLD IS SET — STILL (v1.7, 2026-08-27)

**Appended at the foot under standing rule 6. Version 1.6 → 1.7. Lines whose number changed
above this section: 0.** Nothing above is edited, struck or renumbered by this section; §11's
original text stands as written and is corrected here, never rewritten there. *(Header
discrepancy carried forward per §9 and §11: line 3 still reads `Version 1.2`; the authoritative
version is the highest section version, now **v1.7**, and the header is deliberately not edited
because editing it would move every line number above.)*

**THIS SECTION SETS NO THRESHOLD AND MOVES NO GATE, NO BAND, NO CAP AND NO LABEL.** §3.1's 70°,
§3.2's 4, §3.3's advisory at 1000 and its compound flag, §3.4's proposed 0.01 and §7.5's proposed
α bracket are all untouched, and nothing is written to `docs/physics_rules.yaml` by this section.
It corrects six factual claims in §11, discharges §11.5's anti-deferral clause, and files a
distribution. **It issues no verdict word**, because there is no gate and no pre-registration
behind a survey, and a `PASS` or `GATE FAIL` here would be the mesh-quality form of the thing
§11.2 refuses.

**All figures below were re-derived from the corpus on 2026-08-27, not taken on report.** The
corpus is **live**: one log (`verification/runs/F17c_runs/coarse/log.checkMesh`) appeared between
two enumerations taken minutes apart, so every count here is a snapshot with a date, not a
constant.

### 12.1 CORRECTION 1 — §11.5's OWN ENUMERATOR PRODUCES THE FALSE ZERO IT WARNS AGAINST

§11.5 states its population was *"counted 2026-08-27 with `find . -name 'log.checkMesh*' -type f`"*
and, three paragraphs later, instructs its own successor:

> *"**MDS-1 enumerates with `find` and states its enumerator**, or its coverage figure is a false
> zero of exactly the kind standing rule 3 exists to catch."*

**It then produced one.** `-name 'log.checkMesh*'` matches a whole basename. It does not match the
**stem-prefixed filename shape** `<stem>.log.checkMesh` — `rung6b.log.checkMesh`,
`c3b.log.checkMesh`, `A3-vcoarse-smoke.log.checkMesh`. Measured 2026-08-27:

| enumerator | logs seen (repository, F5b pruned) |
|---|---|
| §11.5's, verbatim | **918** |
| both filename shapes | **1005** |
| **invisible to §11.5** | **87** |

The 87 are not scattered. **78 of them are the entire
`verification/runs/MESH_AUDIT_runs/2026-08-08/` pool** — the retained-log corpus of the lab's own
mesh birth-certificate audit, which is to say the single most relevant population §11 could have
surveyed. The remainder: 5 in `verification/runs/B52_RUNG6_REPLICATE_runs/`, 3 in
`verification/runs/R4_runs/`, 1 in `verification/campaign/DRAW_SCATTER_RETROFIT/`.

**The lesson is not that a glob was wrong. It is that §11.5 wrote the warning, named the standing
rule, and did not apply either to the line above it.** A guard stated in prose and not driven is
not a guard. This is recorded here rather than softened because §11's own §11.2 argues that a
wrong number in a standard is more expensive than a missing one, and §11.5 shipped four wrong
ones (916, 761, 155, and 916-of-916) under exactly that heading.

**STRICKEN, and replaced below:** §11.5's population table and its `TOTAL 916` row; the
parenthetical *"counted 2026-08-27 with `find . -name 'log.checkMesh*' -type f` — measured, not
estimated"*.

**THE CORRECTED ENUMERATOR, AS A COMMAND.** MDS-1 and every successor use this, and state it:

```bash
find <root> -path '*/verification/runs/F5b_runs' -prune -o \
     \( -name 'log.checkMesh*' -o -name '*.log.checkMesh*' \) -type f -print
```

**What it excludes, and why — stated, because an exclusion nobody states is a false zero with a
reason:**

- **`.git/`** — the object store is not a run record.
- **`verification/runs/F5b_runs/`** — **QUARANTINED**, pending Sanaa's ruling on a permission
  denial. It is **pruned by explicit path test on every candidate, counted, and never opened.**
  The quarantine names that directory and F5b's *gate quantity*; mesh-quality fields in a
  different tree are neither, so mesh certificates elsewhere remain readable. Pruned at this
  measurement: **1 log**.
- **Nothing else.** Dotted directories are entered (`find` enters them; a recursive `**` glob does
  not, and `grep -r` in this environment honours ignore files — §11.5's two observations on this
  are correct and are carried forward unchanged).

### 12.2 CORRECTION 2 — §11.3's TWO LABEL FORMS ARE NOT EXHAUSTIVE

§11.3 states that of the lab's logs *"761 ... and 155 ... the two sets are disjoint and
exhaustive"*. **Disjoint is correct and is re-confirmed here: 0 logs carry both forms.**
**Exhaustive is false.** Re-measured over the corrected 1006-log repository corpus:

| aspect-ratio label | logs |
|---|---|
| `Max aspect ratio = <value> OK.` (the `=` form) | **838** |
| `***High aspect ratio cells found, Max aspect ratio: <value>` (the `:` form) | **164** |
| **NEITHER — no aspect-ratio field at all** | **4** |

The four are runs that **stop before the aspect check ever executes**, all in
`verification/runs/MESH_AUDIT_runs/2026-08-08/` (the `A3-onera-m6-sweep-n15_21840__…p0–p3` logs).
A reader whose two branches are `=` and `:` has no third branch, and what it does with these four
is undefined — the two available failure modes being to crash, or to silently record the last
value it happened to hold.

**The rule that follows: `ABSENT` IS A THIRD LABEL FORM AND IS RECORDED AS ONE.** A missing
aspect field is reported as missing, with the log's path. It is never a `null` that a later reader
mistakes for unmeasured, and never a number.

**STRICKEN:** the words *"and exhaustive"* in §11.3, and the counts 761 / 155.

### 12.3 CORRECTION 3 — THE CELL-VOLUME RATIO IS UNDEFINED PRECISELY WHERE THE MESH IS WORST

§11.5 states the ratio *"is derivable with `min > 0` in **916 of 916**"*. **False.** Measured over
the corrected corpus, **1000 of 1006** repository logs yield a ratio. Six do not:

| why not | logs |
|---|---|
| no `Min volume = …` line printed at all | **4** |
| `checkMesh` printed `***Zero or negative cell volume detected.` **instead** of the summary line | **2** |

And the two are the worst meshes in the repository:

| log | minimum negative volume | negative cells | max aspect ratio | `checkMesh` |
|---|---|---|---|---|
| `verification/runs/MESH_AUDIT_runs/2026-08-08/A3-onera-m6-adjoint-vcoarse__constant__polyMesh.log.checkMesh` | `-3.30275e-09` | 23 | `2.07741e+95` | `Failed 10 mesh checks.` |
| `verification/runs/MESH_AUDIT_runs/2026-08-08/A3-vcoarse-smoke.log.checkMesh` | `-3.30275e-09` | 23 | `2.07741e+95` | `Failed 10 mesh checks.` |

**A reader that divides `max / min` and keeps only the finite answers therefore drops the two
meshes §11 most wants to see, and drops them silently, leaving a distribution that looks complete.**
The survey would have reported the population of meshes that are *not* degenerate and called it the
population.

**THE RULE, FIXED HERE, BEFORE COLLECTION, WHICH IS THE ONLY TIME IT COUNTS.** A mesh whose minimum
cell volume is **negative, zero, or unprinted**:

1. is recorded with an explicit status — `MIN_NEGATIVE`, `MIN_ZERO`, `MIN_VOLUME_LINE_ABSENT` —
   never a bare `null`;
2. carries its negative value and its negative-cell count in the record;
3. **is counted in the census and is never dropped from it**;
4. is **excluded from ratio percentiles**, because `max/min` is not defined for it, **and the
   exclusion is reported as a number beside the percentiles it was excluded from.**

A percentile that silently excludes is a percentile of a different population.

### 12.4 CORRECTION 4 — A CITED PATH IS EMPTY, AND THE LOGS ARE NOT LOST

`verification/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md:45` cites its 78 retained logs at
`demo-output/website/campaign/MESH_AUDIT_runs/2026-08-08/`. **That directory does not exist**, and
`demo-output/` holds **0** `log.checkMesh` files of either filename shape.

**The logs are not lost.** All 78 are at
**`verification/runs/MESH_AUDIT_runs/2026-08-08/`**, moved at commit `a1fbe127` (2026-08-18,
MOVE_MAP batch 7). A reader following the audit document finds an empty path and would report the
evidence absent — which is the same false zero as §12.1 arriving by a different road. The audit
document is another team's frozen record and is **not edited by this section**; the redirection is
recorded here, and at MDS-1's home, so a reader who lands on either finds it.

### 12.5 CORRECTION 5 — THE ANTI-DEFERRAL CLAUSE WAS LIVE, AND IS DISCHARGED BY THIS SECTION

§11.5 provides that a record citing §11 to say *"threshold deferred to MDS-1"* while
`verification/runs/MDS1_runs/` does not exist *"is citing a survey that has not been started, and
**must say so in those words**"*.

**At the time this section was written that directory did not exist**, so the clause was live and
every §11 citation was of an unstarted survey. **It exists now.** MDS-1's reader, its planted
controls and its first distribution are filed at:

- **`verification/runs/MDS1_runs/mds1_survey.py`** — the reader
- **`verification/runs/MDS1_runs/MDS1_SURVEY.json`** — the distribution, with one record per log

**Cost: ZERO new compute.** Both quantities are read back from `log.checkMesh` files already on
disk, as §11.5 predicted. No solver, no mesher, no `checkMesh` invocation.

**The reader's controls (standing rule 3), each driven in BOTH directions** — the perturbation
must FIRE and its unperturbed twin must STAY SILENT, because a reader that reports the plant on
every input passes a fire-only test and is worthless: a perturbed aspect value; a perturbed cell
count; a removed log; the `:` label form read as a non-null value; a non-positive minimum volume
reported rather than dropped; and the F5b quarantine pruned, counted and never opened. The reader
**refuses (exit 2) rather than degrades** — under `python -O`, if any `assert` statement is found
in its own source (required: **0** `ast.Assert` nodes, verified by the reader on itself at every
run), on any unreadable input, on a corpus root that does not exist, on an unparsable value, and
on any control that does not behave. **The controls run on every survey invocation, not only under
`--selftest`.**

**Recorded because it is the whole point of a driven control:** the quarantine control **fired on
the first run of the reader and caught a real defect in the reader's own pruning** — the guard
stopped at the quarantine's top directory and reported `0` for a populated tree. **The guard
against false zeros was itself producing one, and prose would not have found it.**

### 12.6 CORRECTION 6 — §11.1 UNDERSTATES ITS OWN EXHIBIT: A NULL IS A HOLE, A FALSE POSITIVE CLAIM IS WORSE

§11.1 documents three `"max_aspect_ratio": null` entries in F12 attempt-2's
`birth_certificates.json`. **It does not mention the prose twin, which is worse.**
`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/BIRTH_CERTIFICATES.md`, at lines
**26, 50 and 74** — coarse, medium and fine — states **affirmatively**:

> `| max aspect ratio | < 1000, not printed (advisory, not gated) |`

Against the levels' own cited `log.checkMesh` files:

| level | what the certificate asserts | what its own cited log says | line |
|---|---|---|---|
| coarse | `< 1000, not printed` | `Max aspect ratio = 805.199 OK.` — **printed** | 93 |
| medium | `< 1000, not printed` | `***High aspect ratio cells found, Max aspect ratio: 2842.46, number of cells 34`; `Failed 1 mesh checks.` | 92 |
| fine | `< 1000, not printed` | `***High aspect ratio cells found, Max aspect ratio: 1760.97, number of cells 31`; `Failed 1 mesh checks.` | 92 |

**"Not printed" is false at all three levels. "< 1000" is additionally false at medium and fine, by
factors of 2.8 and 1.8, in a mesh `checkMesh` failed.**

**And the coarse row is the load-bearing one.** At coarse the claim is *half* true — the value
really is below 1000 — so the row reads as a measurement that merely went unrecorded. **That false
half is what makes the medium and fine rows read as measured rather than assumed.** Three identical
rows, one of which happens to be numerically right, present as a field the builder checked and
found unremarkable. The builder
(`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/build_ladder_attempt2.py`) contains
**no occurrence of the string `aspect`**: nothing was checked at any level.

**The transferable rule, and it is sharper than §11.4's:**

> **A `null` is a hole and announces itself. A POSITIVE CLAIM REFUTED BY THE RECORD'S OWN CITED
> LOG does not — it consumes the reader's attention and returns a false answer.** §11.4's planted
> control requires a reader be shown able to read a non-null value. **This clause adds: a stated
> value must be shown to have COME FROM the log the record cites, not from the writer's
> expectation of it.** Where a certificate's prose twin and its JSON disagree, the disagreement is
> itself a finding and neither is believed until the log is read.

**Not retroactive** (§11.6): F12 is not regraded and no verdict of its moves. This is read as
evidence of a reporting gap, exactly as §11.1 read the three nulls.

### 12.7 A SEVENTH FINDING, NOT ON THE LIST: §11.5's POPULATION IGNORES THE OUT-OF-REPOSITORY CORPUS

`CLAUDE.md` names `/home/ubuntu/{closure-data, closure-challenge-benchmark, certonomous-runs}/` as
lab data, and states that *"nothing is invisible merely because it is big"*. §11.5's population
counted the repository only. Measured 2026-08-27:

| root | logs (both shapes) |
|---|---|
| `/home/ubuntu/certonomous-runs/` | **149** |
| `/home/ubuntu/closure-data/` | **3** |
| `/home/ubuntu/closure-challenge-benchmark/` | 0 |

**152 logs, 13 % of the true population, outside §11.5's stated count** — and they are not
redundant. **Three of the lab's five negative-minimum-volume meshes live there**
(`/home/ubuntu/certonomous-runs/rae2822-meshcheck/{og-fine,og-medium,ogrid-coarse}/log.checkMesh`,
minimum negative volumes `-1.504754644e-10`, `-1.9300131e-08`, `-7.410501977e-08`, one negative
cell each, all `Failed 5 mesh checks.`), and **all three additionally carry no aspect-ratio field
at all** — so they fall through §12.2's gap and §12.3's gap simultaneously. A survey that counted
only the repository would have reported **two** degenerate meshes lab-wide instead of **five**.

**These are other teams' records and are READ ONLY.** Nothing outside the repository is modified,
moved or deleted by MDS-1, and nothing outside it is written by this section.

### 12.8 THE FIRST MDS-1 DISTRIBUTION — REPORTED, WITH NO THRESHOLD PROPOSED

Corpus: **1158 logs** (1006 repository + 152 out-of-repository), F5b pruned, both filename shapes,
2026-08-27. Full record-per-log data at `verification/runs/MDS1_runs/MDS1_SURVEY.json`.

**Max aspect ratio**, all logs carrying the field (n = 1151):

| min | d1 | median | d8 | d9 / p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|
| 1.0 | 1.0 | **8.84** | 408 | 5.93e+03 | 6.90e+04 | 2.07e+07 | **2.08e+95** |

**Whole-mesh cell-volume ratio**, logs with a positive minimum (n = 1149; **9 excluded**, see
§12.3):

| min | d1 | median | d8 | d9 / p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|
| 1.0 | 1.0 | **63.0** | 5.02e+05 | 1.28e+08 | 5.52e+09 | 1.38e+12 | **2.08e+17** |

**Split on `geometric_directions`, because §11.4's 2-D caveat makes these two different
statistics and they are never pooled into one judgement:**

| split | logs | aspect median | aspect p95 | ratio n | ratio median | ratio p95 |
|---|---|---|---|---|---|---|
| 2-D | 738 | 16.0 | 2.14e+06 | 735 | 33.4 | 2.38e+10 |
| 3-D | 375 | 4.73 | 6.75e+03 | 373 | 1.80e+04 | 5.52e+09 |
| directions not printed | 45 | 1.0 | 1.0 | 41 | 1.25 | 1.27 |

**Two observations from the distribution, stated as observations and not as arguments for a
number:**

- **`checkMesh` itself already draws the aspect line at 1000.** Exactly **180** logs carry
  `aspect >= 1000` and exactly **180** carry `***High aspect ratio cells found` — the same 180.
  The highest aspect ratio in any log ending `Mesh OK.` is **962.79**. §3.3's advisory at 1000 is
  therefore not merely the lab's convention; it is the value `checkMesh`'s own
  `aspectThreshold_` enforces, and a lab gate at 1000 would be a restatement rather than an
  addition.
- **The cell-volume ratio is genuinely ungated in both directions.** The largest ratio in a mesh
  `checkMesh` declares **`Mesh OK.`** is **2.08e+17**. Seventeen orders of magnitude passes
  every check the lab and `checkMesh` currently apply, which is what §11.1 meant by the volume
  dimension being 0 % covered.

**A CAVEAT ON THE CROSS-TABULATION, WHICH §11.5 ORDERED AND WHICH CANNOT YET DO WHAT IT WAS
ORDERED TO DO.** §11.5 requires MDS-1 to cross-tabulate aspect ratio against non-orthogonality and
skewness so §3.3's assertion — high aspect ratio is dangerous *in company*, harmless when aligned
— can be **tested rather than inherited**. The cross-tabulation is filed. **It cannot test that
assertion, and the reason is circularity:** the only outcome variable available in a
`log.checkMesh` is `checkMesh`'s own verdict, and that verdict is **defined** to fail when aspect
ratio exceeds 1000. Measured: **100 % (180 of 180)** of logs with `aspect >= 1000` are
`Failed N mesh checks.` — which is arithmetic, not evidence. Against a genuinely independent
outcome, meshes with `aspect < 1000` fail on other grounds at **9.6 %** (93 of 971), so the
tabulation does carry signal about the *other* dimensions; it carries none about aspect ratio's.
**§11.5's requirement 2 — a failure attributed to the dimension BY A MECHANISM — therefore remains
unmet, and MDS-1 cannot meet it from retained logs alone.** Naming this now is cheaper than
discovering it inside a threshold proposal.

### 12.9 NO THRESHOLD IS SET. STILL. AND THE GROUND IS NOW WEAKER THAN IT WAS

**§11.2's refusal is reaffirmed in full and none of the four conditions in §11.5 is waived.** The
survey existing does not entitle anyone to a number; it satisfies **one** of four requirements.

**The motivating case is weaker evidence than it was claimed to be, twice over, and this is
recorded against the standard rather than left in a report:**

1. **F12's Arm A exonerated the mesh** — §11.2 already discloses this, and discloses further that
   Arm A's percentile figures live only as supervisor triage prose in `docs/LAB_STATE.md` with
   **no artifact of their own** under `verification/runs/F12_runs/`. A threshold fitted to F12
   would have gated against cells that had nothing to do with the failure.
2. **§11's own characterisation of the F12 exhibit was incomplete** — §12.6 above. The record it
   cited as three `null`s is in fact three affirmatively false rows, one of them half-true in the
   way that makes the other two persuasive.
3. **And the author of §11 has already withdrawn one of his own headline characterisations of the
   occasion case.** That is disclosed here, in the standard, because a standard whose motivating
   narrative has been partly retracted must say so where the standard is read, not where the
   retraction was made.

Add to that §12.8's finding that the cross-tabulation cannot test §3.3's mechanism claim from
retained logs, and the position is: **the dimension is now measured across 1158 meshes and the
mechanism is still unestablished.** §11.2's rule holds and is the reason this section stops here:

> **A number that is WRONG in a standard is more expensive than a number that is MISSING from
> one.** Measurement precedes the threshold; the threshold is argued from the distribution and
> from a mechanism, never from the one case that made somebody look.

**Collecting a survey and setting a gate are different acts, and only the first is performed
here.** Anyone proposing a number cites §11.5's four requirements and answers all four, including
requirement 3 — what the proposed threshold would have rejected in this surveyed population, **by
name and count**, including how many currently-PASSing lab results it would retro-invalidate.
That question is now answerable for the first time. It is not answered here.

### 12.10 Scope of §12

- §12 corrects **§11 only**, and by the striking-and-correcting form of standing rule 6: §11's
  original text is not edited, and lines whose number changed above this section: **0**.
- §12 **sets no threshold and moves no gate value.** §3's, §7's and §11's numbers are unchanged,
  and nothing is written to `docs/physics_rules.yaml`.
- §12 **issues no verdict word**, and MDS-1's reader issues none. There is no gate and no
  pre-registration behind a survey.
- **Not retroactive.** No frozen ladder is re-opened and no closed verdict is regraded — F12's,
  the MESH_AUDIT corpus's and the out-of-repository records' included.
- §12 does not edit `sdk/chief_engineer/mesh_certificate.py`, and does not edit any other team's
  record — including `verification/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md` (§12.4)
  and `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/BIRTH_CERTIFICATES.md` (§12.6),
  both of which are reported and left untouched.
- **Every count in §12 is a dated snapshot of a live corpus**, re-derivable with the §12.1
  command. It is not a constant and a later re-measurement disagreeing with it is not a defect in
  either.

---

## 13. A WEDGE-ANGLE GUARD MAY NOT GATE A QUANTITY DERIVED FROM `wedgePolyPatch`'s SUMMED NORMAL AGAINST A FIXED ABSOLUTE TOLERANCE (v1.8, 2026-08-28)

**Appended at the foot, append-only. Nothing above is edited, struck, widened or narrowed.
`lines whose number changed above this section: 0` — MEASURED, not recited: the md5 of
this document's HEAD blob before the append and the md5 of the first 1,223 lines of this
document after it are both printed in the amendment record below, and the append refused
to proceed unless they were equal.** The header still reads `Version 1.2` and the
authoritative version is the **highest section version**, now **v1.8**, by the convention
this file records at its §11 and §12; the header is deliberately not edited, because
editing it would change a line number above this section and falsify the assertion.

**THIS SECTION GATES NOTHING UNTIL THE VERIFICATION TEAM HAS READ ITS DIFF PERSONALLY.**
It is drafted by cfd; it is not in force on any case until that read.

Content adapted from the cfd draft committed at
`verification/campaign/CFD_MESH_STANDARD_WEDGE_ANGLE_CLAUSE_DRAFT_2026-08-28.md`
(`d606bbd2`, 153 lines).

### 13.1 The occasion, measured

`F23_HP_WEDGE` graded **`NOT A RESULT`**. Its fine level never reached the solver because
the case's builder (`cases/F23_HP_WEDGE/build_f23.py:129`) refused the built mesh on a
**fixed absolute `1e-6` degree** tolerance between `checkMesh`'s printed wedge angle and
the registered half angle of 0.04°:

| level | wedge faces per patch | printed angle | deviation | vs the `1e-6` gate | `checkMesh`'s own verdict |
|---|---|---|---|---|---|
| coarse | 131,072 | 0.0400002766821 | 2.766821e−07 | 0.28× | **`Mesh OK.`** |
| medium | 524,288 | 0.0400007984975 | 7.984975e−07 | **0.80×** | **`Mesh OK.`** |
| fine | 2,097,152 | 0.0400027202903 | 2.720290e−06 | **2.72× — REFUSED** | **`Mesh OK.`** |

**OpenFOAM's own checker passed all three meshes, fine included.** The guard refused a
mesh that is correct. Medium already sat at **80 % of its tolerance budget**, so the
ladder was one refinement level from refusal at registration time and nothing computed it.

### 13.2 Why — the printed angle carries a floor that grows with the mesh

`wedgePolyPatch` stores `cosAngle_ = centreNormal_ & n_`, where `n_` is the **arithmetic
mean of that patch's unit face normals and is never renormalised**, and `checkMesh` prints
`acos` of it. Summing N nearly-identical unit vectors accumulates floating-point rounding,
so `|n̄|` lands **below 1**; and because `d(acos)/dc = −1/sin(a)`, that deficit is amplified
by 1/sin(0.04°) = 1432 on its way to an angle:

    printed deviation  ≈  ( 1 − |n̄| ) / sin(a)        [radians]

Verified three ways, one of them a control that changes nothing else:

1. **Reproduction.** An independent reimplementation of OpenFOAM's face-area-vector
   construction, the unnormalised mean and the snapped `centreNormal_`, run from
   `constant/polyMesh` alone, reproduced the printed value **to its last printed digit at
   all three levels**.
2. **The `math.fsum` control.** Replacing only the summation with exact accumulation —
   **same points, same faces, same geometry, nothing else touched** — drives `1 − |n̄|` from
   **3.371303e−12 / 9.729550e−12 / 3.314704e−11** to **exactly 0.0** at all three levels,
   and the printed angle to **0.03999999999967**. The deviation is arithmetic, not geometry.
3. **The prediction closes.** `(1 − |n̄|)/sin(a)` gives **2.766834e−07 / 7.985058e−07 /
   2.720383e−06** against the printed **2.766821e−07 / 7.984975e−07 / 2.720290e−06**.

**The growth law.** `1 − |n̄|` is bounded by `N·ε` for sequential summation
(ε = 2.220446049250313e−16); measured, `(1 − |n̄|)/(N·ε)` is **0.1158 / 0.0836 / 0.0712** —
a falling fraction of that bound. **The floor grows approximately linearly in the
wedge-patch face count and inversely with sin(a). A fixed absolute tolerance is crossed at
some level of any ladder; only the level is in question.** Because the occupancy FALLS with
N, `Δa ∝ N` is an **upper bound, not a fit**, and is fit only for screening meshes that do
not yet exist.

**The intuitive hypothesis is EXCLUDED by measurement, not by argument.** Catastrophic
cancellation in the cells near the axis is **false here**: across the coarse level's
131,072 wedge faces there are **3 distinct `n_z` values and 10 distinct `n_x` values**,
`Var(n_z) = 8.45e−32`, and binned by radius decile the per-face deviation is **flat** —
the innermost faces' normals are bit-identical to the outermost. **A standard that sent a
lane to look near the axis would send it to the wrong place.**

### 13.3 THE DISCRIMINATOR — this is the test, and it is not a proxy

> ### does the compared quantity ever touch `wedgePolyPatch`'s summed normal?

**If YES, a fixed absolute tolerance is unsafe and §13.4 applies. If NO, the site is
CLEARED regardless of how tight its tolerance is.**

**Do NOT substitute a proxy, and in particular do not substitute "is the tolerance
tight".** Tightness is precisely the property that mis-flags a sound instrument — see
§13.5, where the tightest wedge-angle tolerance in the lab, **1e-15**, is **correct**.
Nor is "does the case run `checkMesh`?" a usable proxy: §13.5's cleared case runs both
`blockMesh` and `checkMesh`, refuses without `Mesh OK`, and consumes checkMesh's volume
numbers elsewhere — and is still cleared, because **the compared quantity** does not come
from there. **The discriminator is about the provenance of the compared quantity, and
answering it requires tracing that provenance to its producer.**

### 13.4 THE CLAUSE

**A mesh guard MUST NOT gate `checkMesh`'s printed wedge angle — or any quantity derived
from `wedgePolyPatch::cosAngle_` — against a tolerance that is fixed and absolute.** A
guard on wedge geometry takes one of two forms, and a case that gates a wedge angle must
state in its pre-registration which it took:

**(a) READ THE GEOMETRY DIRECTLY — preferred, and the sharp form.** Compute the angle for
**every face of every wedge patch** from `constant/polyMesh`, in a form that never
evaluates `acos` near 1 — `degrees(atan2(hypot(n_x, n_y), |n_z|))` against the
componentwise-snapped cardinal normal — and gate the **relative** deviation
`max |angle/HALF_ANGLE − 1|`. Measured over the three meshes above this is
**1.895413e−10 / 2.449031e−10 / 7.569059e−10**, ten orders below any physically meaningful
mis-build, growing only as an extreme value over more faces.

**(b) IF THE PRINTED ANGLE IS GATED AT ALL, the tolerance MUST carry the summation floor
explicitly**, as a term in the mesh's own face count:

    TOL(level) [deg] = HALF_ANGLE x TOL_REL(level)
                     + K x N_wedge_faces(level) x EPS_MACH / sin(HALF_ANGLE) x 180/pi

`N` is the face count of **ONE** wedge patch — `wedgePolyPatch` means per patch and
`checkMesh` prints per patch — with `K ≥ 1` frozen at registration (`K = 1` is the
worst-case sequential-summation bound, 8.6–14× above what was measured). Applied to the
ladder above this gives **2.874681e−06 / 9.674350e−06 / 3.824547e−05 deg** and occupancies
**0.096 / 0.083 / 0.071 — falling with refinement, where the fixed absolute tolerance's
occupancy rose 0.28 / 0.80 / 2.72.**

**In either form the relative tolerance MUST be derived per level, not inherited**, by
this standard's existing L-346 discipline: tie it to a fraction of **that level's own
predicted discretisation error**, with a registered absolute floor so it cannot fall below
what floating point can deliver.

**AND IT MUST STILL REFUSE A MIS-BUILT WEDGE — SHOWN, NOT ASSERTED.** Any guard landed
under this clause ships a **two-direction** control (standing rule 3, and L-396's mirror),
**driven through the real producer** — a plant authored as a perturbed half angle in
`blockMeshDict` and meshed by the real `blockMesh`, not injected downstream of it: one
plant it MUST refuse, and a real correct mesh at the ladder's FINEST level it MUST NOT.
**A guard relaxed after a refusal, with no control showing it can still refuse, is a rubber
stamp and this clause does not authorise one.**

### 13.5 THE WORKED NEGATIVE — `analyse_t17.py:344` is CLEARED, and its tolerance is 1e-15

**A rule that only ever fires is not a rule.** The clause is therefore shipped with the
case it must NOT flag, traced end to end in this invocation.

`verification/runs/T-family/T17_runs/analyse_t17.py:344` reads:

    if abs(float(m["wedge_deg"]) - reg["physics"]["wedge_deg"]) > 1e-15:
        refuse("level %s wedge angle %s is not the registered %g" % ...)

**The refusal string is the same shape as F23's and the tolerance is 1e-15 — the tightest
wedge-angle tolerance in the lab, 1e9 times tighter than the one that failed. It is
CORRECT.** Provenance of the compared quantity, traced to its producer:

| step | artifact | what happens |
|---|---|---|
| 1 | `build_t17.py:60` | `WEDGE_DEG = 1.0` — a **module constant** |
| 2 | `build_t17.py:201,205` | writes `wedge_deg=%.17g` from that constant into the case's `CASE.txt` |
| 3 | `analyse_t17.py:70-72` | reads that `CASE.txt` |
| 4 | `analyse_t17.py:344` | compares the parsed value with `reg["physics"]["wedge_deg"]` |

**Apply the discriminator: does the compared quantity ever touch `wedgePolyPatch`'s summed
normal? NO.** `blockMesh` is not in that chain, `checkMesh` is not in that chain, and no
mesh reading of any kind enters it. **The proposition the instrument actually evaluates is
"does the registered value survive a `%.17g` round-trip?" — register against register —
not "is the mesh built correctly?"** `%.17g` is round-trip-exact for IEEE-754 double, so
the difference is identically zero; **measured in this invocation on five values including
hostile ones (1.0, 0.04, 1/3, 5.0, 0.0024937655860349127): every difference is exactly
`0.0`.** A `1e-15` tolerance is not merely adequate there, it is roughly `1e15` times
looser than the quantity requires. **CLEARED.**

**And note what would have mis-flagged it.** T17 **does** mesh: `build_t17.py:216` runs
`blockMesh`, `:229` refuses without `Mesh OK`, and `:104` checks analytic volumes against
*"checkMesh's own three numbers"*. So a screen keyed on *"uses a wedge"*, *"runs
checkMesh"*, *"gates a wedge angle"* or *"has a tight tolerance"* flags T17 and is **wrong
about the tree**. Only the provenance question clears it. **That is why §13.3 is phrased as
it is and why no proxy for it is admitted.**

### 13.6 The population and the result

Swept by the verification team at `83cb13da` over **1,084 `checkMesh` logs across 7
campaigns**, of which **206 carry a printed wedge angle**. Margins were taken as
`(printed − nominal)` **straight from each log**, so they are **measured, not predicted**,
and the face count `N` does not enter them.

- **EXPOSED: 1 site lab-wide — `cases/F23_HP_WEDGE/build_f23.py:129`**, a literal `1e-6`,
  N-independent, **REALISED** (it has already fired, on F23's fine level).
- **Relative-form sites: ZERO.**
- The verification team **back-solved the constant `1e-6` from the three anchors above
  BEFORE looking for it**, then found it at that line — an independently derived constant
  landing on the literal.

`F23_HP_WEDGE`'s successor `F23b_HP_WEDGE` is registered under form (a) with form (b) as a
cross-check (`verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md` §4.3, frozen at
`57d31dde`, Amendment 1 at `440aca3d`).

### 13.7 What this section does NOT do

- It **sets no threshold**. `TOL_REL`, `K` and the absolute floor are registered per case,
  at that case's freeze, from that case's own predicted error.
- It **amends no existing gate**: §3's non-orthogonality 70°, skewness 4 and aspect-ratio
  advisory 1000 are untouched, as are §7, §8, §9, §10, §11 and §12. It retires nothing.
- It **makes no claim about other OpenFOAM versions.** Every reading is `OPENFOAM=2606`,
  build `_481094f-20260618`, on this box.
- It is **not an upstream defect report and not a defect claim against OpenFOAM.**
  `checkMesh` printed `Mesh OK.` and was right to; the printed angle is a diagnostic and
  the lab gated it as if it were a measurement. **The defect was ours.** Nothing is sent,
  filed, uploaded, posted or submitted (standing rule 7).

| amendment record | **v1.8** |
|---|---|
| clauses added | 1 (§13) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** |
| worked negative examples shipped | **1** (`analyse_t17.py:344`, CLEARED) |
| exposed sites in the swept population | **1** of 206 angle-carrying logs (1,084 swept) |
| **lines whose number changed above this section** | **0** |
| md5 of this file's HEAD blob before the append | `6eaf23d2304fbd52e79c7356dcf94dd9` |
| md5 of this file's first 1,223 lines after the append | `6eaf23d2304fbd52e79c7356dcf94dd9` |
| the two digests | `**EQUAL — assertion MEASURED**` |

---

## 14. READING THE NON-ORTHOGONALITY GATE — the reported maximum, never `checkMesh`'s verdict line (v1.9, 2026-09-01)

**ORDINAL CORRECTED 2026-09-01, disclosed rather than silently renumbered.** This section
**landed as `## 10.` at commit `afedaadc` and is corrected to `## 14.` here**, because the
file already carried a §10 (`High_order_grid_convergence.pdf` provenance, v1.5) and the
section sequence runs to **13**. **The cause was conflating the section VERSION with the
section ORDINAL**: `v1.9` was derived correctly from the highest section version `v1.8` and
is unchanged, but the two counters diverged at §11/v1.6 and the version is not the ordinal.
**A section ordinal is derived from the MAXIMUM EXISTING ORDINAL in the file, in the same
invocation as the commit — never from a version, never from a count.** The heading and its
six subsection numbers are the only things this correction touches; no gate, threshold,
clause or measured value moves.

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered,
inserted or deleted. Verified by digest, not by assertion — see the closing table.

**This section changes NO gate value.** The 70° hard gate of §3.1, its 65–70 warning band and
its action clause are untouched, in either direction. Retiring, widening or narrowing a gate
threshold is reserved to Sanaa. **What this section fixes is WHERE the existing gate is read
from.**

### 14.1 The finding, in the form that settles it: the verdict line CANNOT DISCRIMINATE

Two meshes from the 2026-08-25 ONERA M6 topology study, one **admissible** under §3.1 and one
**inadmissible by 11.6°**, produce the **identical** `checkMesh` verdict line:

| mesh | reported max non-orthogonality | §3.1 verdict | `checkMesh` prints |
|---|---|---|---|
| `CONTROL_nofill_L1` | **51.2554°** | admissible | `Non-orthogonality check OK.` |
| `t1_SHELL` | **81.5834°** | **inadmissible** | `Non-orthogonality check OK.` |

> **The line reads the same on the mesh that passes and the mesh that fails. It carries no
> information about this lab's gate, and a check built on it cannot fail.**

That is the whole argument, and it is a **discrimination test** rather than a claim about
OpenFOAM's internals: a reader that returns the same answer for a known pass and a known fail
has been shown unable to see the difference, which is the planted-control standard this lab
already applies to every comparator (CLAUDE.md rule 3). **Here the reader is the instrument
itself.**

*Artifacts:*
`verification/runs/F13_ONERA_M6_runs/mesh/CONTROL_nofill_L1_checkMesh.log:97-98`;
`verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/t1_SHELL/log.checkMesh:96-98`.

### 14.2 Three consecutive lines, the third contradicting the first two

`t1_SHELL/log.checkMesh`, lines 96–98, **verbatim**:

```
    Mesh non-orthogonality Max: 81.5834 average: 15.5977
   *Number of severely non-orthogonal (> 70 degrees) faces: 516.
    Non-orthogonality check OK.
```

A maximum of **81.5834°** against a 70° gate, **516 faces** flagged severe with OpenFOAM's `*`
warning marker — and then **`OK`**, three lines apart. The `70` in `nonOrthThreshold_` that
§3.1 cites drives the *severe-face warning list*; the **verdict** line is decided against a
separate and far higher internal error limit. **The tool is answering its own question
correctly. It is not answering ours.**

### 14.3 The file-level verdict does not merely stay silent — ON THIS PAIR IT RUNS THE WRONG WAY

| mesh | reported max non-orthogonality | §3.1 verdict | closing line | which checks actually failed |
|---|---|---|---|---|
| `CONTROL_nofill_L1` | 51.2554° | **admissible** | **`Failed 2 mesh checks.`** | unused points (3,542) + aspect ratio (5934.1) |
| `t1_SHELL` | 81.5834° | **inadmissible by 11.6°** | **`Failed 1 mesh checks.`** | aspect ratio (5622.42) |

> **The ADMISSIBLE mesh fails MORE checks than the inadmissible one.** A gate reading the
> closing line is therefore not merely uninformed — on this pair it is **anti-correlated with
> §3.1**, and a lane ranking two meshes by that line would pick the worse one.

**This is not a paradox, and the reason is the point.** The two counts are sums over
**different metrics**, and **non-orthogonality is in neither**: the control fails on unused
points (an artifact of omitting the tip fill) and on aspect ratio; `t1_SHELL` fails on aspect
ratio alone. Aspect ratio is **advisory** under §3.3 and never a lone rejection, so **every
failure in both counts is a metric this standard declines to reject on**, while the one
breach that *is* a hard gate — 11.6° over — appears in no verdict string at all. The aspect
ratio even runs the same way (5934.1 on the admissible mesh against 5622.42 on the
inadmissible one).

**A scalar verdict cannot stand in for a named measurement.** That is the general statement;
the table is the measured instance.

### 14.4 THE CLAUSE

> **The §3.1 gate is read off the reported maximum — `Mesh non-orthogonality Max:` — together
> with the count of severely non-orthogonal faces where `checkMesh` reports one.**
>
> **It is NEVER read off `checkMesh`'s `Non-orthogonality check OK.` line, and never off the
> file's closing `Mesh OK.` / `Failed N mesh checks.` line.** Those strings are decided
> against OpenFOAM's internal error limits, which sit far above this gate. They have been
> **measured unable to discriminate** an admissible mesh from one 11.6° outside the gate
> (§14.1), and the closing line has been **measured anti-correlated** with §3.1 on that same
> pair (§14.3). **A tool's pass is not this lab's pass, and a tool's failure count is not this
> lab's ranking.**
>
> **Any comparator, admission check, gate script or lane report that greps a verdict string
> instead of parsing the reported maximum is reading the wrong instrument, and its clean
> result is not evidence.**
>
> **Report the severe-face count beside the maximum.** The maximum can asymptote and look
> stable under refinement while the severe-face *fraction* rises an order of magnitude — the
> measured signature at `N-C6` in `docs/NUMERICS_KNOWLEDGE.md` (516 → 7,200 severe faces,
> 0.158 % → 1.694 %, while cell count rose only 1.31×). **The maximum alone hides that
> propagation.**

### 14.5 A version discrepancy NAMED, and deliberately NOT resolved here

This file's header (line 3) reads `Version 1.2, dated 2026-08-11`, while the highest section
version is **`v1.8`** before this block and **`v1.9`** with it. **The header has been stale
since §8 landed and is recorded as such at line 441.** It is **not** repaired here, and not
merely because editing line 3 would move every line number above — **a version bump that
quietly resolves a pre-existing inconsistency is a second, undisclosed change riding inside a
disclosed one.** The authoritative version of this document remains the **highest section
version**. Repairing the header stays a separate, disclosed edit for whoever takes it.

### 14.6 What this section does NOT do

- It does **not** change the 70° threshold, the 65–70 warning band, or §3.1's action clause.
- It does **not** touch §3.3's aspect-ratio advisory, which remains advisory and never a lone
  rejection.
- It proposes **no new gate** and moves no existing one.
- It does **not** claim `checkMesh` is defective. `checkMesh` is correct about its own
  thresholds; the defect is in reading its answer as though it were ours.

| assertion | value |
|---|---|
| gate values changed by this section | **0** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's HEAD blob before the append | `434b6ebec1b8f09e4ea276d71456796e` |
| md5 of this file's first 1,436 lines after the append | `434b6ebec1b8f09e4ea276d71456796e` |
| the two digests | `**EQUAL — assertion MEASURED**` |

---

## 15. TWO-TIER MESH ADMISSIBILITY — THE 70° GATE IS THE GENERATION STANDARD AND IS UNCHANGED; A WORKSHOP COMMITTEE GRID IS A DIFFERENT OBJECT AND IS ADMISSIBLE FOR VALIDATION-AGAINST-WORKSHOP-DATA WITHOUT MEETING IT (v1.10, 2026-09-03) [SANAA-RULED]

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered,
inserted or deleted — §3.1's 70° hard gate and its 65–70 warning band are not touched in
either direction, and §3.2, §3.3, §6, §7, §8, §9, §10, §11, §12, §13 and §14 are untouched.
Verified by digest, not by assertion — see the closing table.

**This section is [SANAA-RULED] and not this lab's own reading.** Retiring, widening or
narrowing a gate threshold is reserved to Sanaa (CLAUDE.md, FIRST-ACTION RULE). **She does
not widen the 70° gate here and neither does this section.** What she rules is that a
committee grid is a *different object* from a mesh the lab builds, and that the gate which
governs the second does not govern the first.

### 15.1 THE RULING, IN HER OWN WORDS

Sanaa, 2026-09-03 ~17:30Z, verbatim, from
`etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md:5-20`:

> **Two-tier mesh standard — this resolves the R12 question. The 70° gate
> is our generation standard: every mesh the lab builds must meet it,
> unchanged. Committee grids are a different object: they exist for
> comparability with the workshop's own results, where every participant
> used the same grids. Ruling: committee grids are admissible for
> validation-against-workshop-data cases without meeting the 70° gate,
> under these conditions: (a) their measured quality (max
> non-orthogonality, skewness, the works) is reported on the certificate,
> not gated; (b) solver-side mitigations (non-orthogonal corrector counts,
> relaxation) are registered before running; (c) the numerical-uncertainty
> band still comes from the grid family; (d) the certificate names the
> grid as "workshop committee family, quality as published" in the
> what-was-checked section. A full certificate IS reachable this way — a
> certificate's honesty is disclosure and verification, not our internal
> birth standard. What committee grids can never do is certify our meshing
> capability — that stays on in-house grids under 70°.**

Everything below is mechanics for that text. **Where any sentence below and her text
disagree, her text governs and the sentence below is the defect.**

### 15.2 TIER 1 — THE GENERATION STANDARD. UNCHANGED, AND IT IS THE DEFAULT

> **§3.1's 70° hard gate is the GENERATION standard. Every mesh the lab builds must meet
> it, unchanged.** *(Her words: "The 70° gate is our generation standard: every mesh the
> lab builds must meet it, unchanged.")*

- "The lab builds" means the mesh was produced on this box, or by this lab's invocation of
  any generator — `blockMesh`, `snappyHexMesh`, `pyHyp`, a hand-written `blockMeshDict`, or
  a public generator driven from a namelist **this lab wrote or modified**.
- **Tier 1 is the default.** A mesh is Tier 2 only if it is *declared* Tier 2 at
  pre-registration under §15.3 and meets every condition there. **There is no implicit
  Tier 2, and no mesh becomes Tier 2 after its quality is measured.** A grid promoted to
  Tier 2 after a Tier-1 reading came back over 70° is the shape rule 2 exists to forbid.
- **A modified namelist does not make a committee grid.** This is the point on which M6I
  already failed R12, measured and on record: M6I was produced by invoking the public
  generator once with `target_y_plus` moved 1.0 → 0.25 and three counts doubled
  (`docs/LAB_STATE.md:21964`). Under §15.3(0) it is Tier 1 and its L1/L2/L3 readings of
  **87.7462° / 86.4646° / 87.6620°** (`verification/runs/M6I_runs/{L1,L2,L3}/log.checkMesh:91`)
  are **breaches of §3.1**, not disclosures under §15.3.

### 15.3 TIER 2 — WORKSHOP COMMITTEE GRIDS. A DIFFERENT OBJECT, WITH ITS OWN ADMISSION TEST

> **A workshop committee grid is admissible for a validation-against-workshop-data case
> without meeting the 70° gate**, when **all five** of (0) and (a)–(d) hold.

**WHAT HAPPENS WHEN A LIMB FAILS — governed by `VERIFICATION_CHARTER` §2r.2, not by this
section, and quoted here so the two documents cannot drift:**

> **A TIER-2 LIMB FAILURE REFUSES THE CERTIFICATE. IT DOES NOT VOID THE PHYSICS.** The run
> does not become `NOT A RESULT`; it **reverts to Tier-1 treatment** — a generation-standard
> breach, the numerical channel carrying it, the fidelity chip capped, and no validated
> force claimed from that mesh. **A disclosure this lab failed to make is a statement about
> our record, not about what the solver computed.**

That is Sanaa's universal rule *bookkeeping never voids physics* (2026-08-26) applied where
it points. **A missing registration heading, an absent substring, a sha never recorded —
these are bookkeeping.** No §2n cause class arises, because no `NOT A RESULT` arises.

**(0) THE OBJECT TEST — what actually is a committee grid.** *(Her ground: "they exist for
comparability with the workshop's own results, where every participant used the same
grids.")* All four:

1. The grid was **published and distributed by the workshop committee itself** — named
   body, named workshop, named grid family, named level, with the URL or the archive it
   came from.
2. It is **byte-unmodified from what was distributed**, apart from format conversion. The
   pre-registration records the sha-256 of the distributed file and of the converted
   `polyMesh`, and states the converter and its version.
3. **Other participants ran this same grid** — that is the comparability the exemption
   buys. A grid nobody else used buys nothing and is Tier 1.
4. The **case is a validation against that workshop's own data.** *(Her scope:
   "admissible for validation-against-workshop-data cases".)* This exemption does not
   travel to any other case type — and note it is a **narrower** grant than R12's on this
   axis and a **wider** one on the certificate axis; see §15.8.

**(a) MEASURED QUALITY REPORTED, NOT GATED.** *(Her words: "their measured quality (max
non-orthogonality, skewness, the works) is reported on the certificate, not gated".)*
The certificate carries, as measured numbers with the artifact each is read from:
max non-orthogonality; the **count of severely non-orthogonal (>70°) faces** and that count
as a fraction of total faces (§14's clause — the maximum alone hides the propagation);
max skewness and its highly-skew face count; max aspect ratio; cell count; face count; and
every other quantity `checkMesh` reported. Read per §14.4: **off the reported maxima,
never off `Non-orthogonality check OK.` and never off `Mesh OK.` / `Failed N mesh checks.`**
**"Not gated" means the row carries no pass/fail verdict and no gate comparison** — not
that a comparison is made and hidden, and not that the gate is moved to make it pass. A
certificate that prints `89.71° vs 70° gate — pass` has laundered the exemption into a
false measurement and is worse than one that fails.

**(b) SOLVER-SIDE MITIGATIONS REGISTERED BEFORE RUNNING.** *(Her words: "solver-side
mitigations (non-orthogonal corrector counts, relaxation) are registered before running".)*
Operational form in §15.4 — that subsection is what a grader checks.

**(c) THE NUMERICAL-UNCERTAINTY BAND STILL COMES FROM THE GRID FAMILY.** *(Her words: "the
numerical-uncertainty band still comes from the grid family".)* Operationally:

- The band is a **Roache triple over three levels of the SAME committee family**, graded
  under CLAUDE.md rule 5 in full. **Rule 5 is not relaxed by one word here:** a triple that
  is not `CONVERGING` is `NOT A RESULT`, whatever the value; no GCI is quoted on
  non-monotone values; GCI at Fs = 1.25. §9.1's three-level requirement stands.
- **The band may NOT be imported from the workshop's published scatter, from another
  family, or from a single level.** A published scatter is other people's result, not this
  lab's measurement, and substituting it is exactly the "reference caps the tier" confusion
  §2n class 6 names.
- **A committee family that does not publish three levels cannot satisfy (c) and therefore
  cannot reach a full certificate.** That is a real and expected outcome, and it is stated
  here so nobody discovers it after the compute is spent.

**(d) THE CERTIFICATE NAMES THE GRID.** *(Her words: 'the certificate names the grid as
"workshop committee family, quality as published" in the what-was-checked section'.)*
Operational form, including the literal string, in §15.5.

### 15.4 CONDITION (b), MADE OPERATIONAL — WHERE THE REGISTRATION LIVES AND WHAT IT NAMES

> **THE HOME.** The registration lives in **the case's own pre-registration**, the one
> named by `prereg_path` in the queue entry and frozen at `prereg_commit`, under a section
> whose heading is **exactly**:
>
> ```
> ## SOLVER-SIDE MITIGATIONS REGISTERED FOR A COMMITTEE GRID (MESH_STANDARD §15.4)
> ```
>
> It lives **nowhere else**. Not in the queue entry's free-text annotations, not in a
> RESULTS file, not in a lane report, not in `docs/LAB_STATE.md`, and **never in the
> scratchpad** (CLAUDE.md rule 13). Rule 2 governs it in full: it is written **before the
> solver starts**, frozen by sha, and after first compute it can be corrected only by a
> dated addendum that alters no gate, threshold, cap or label.

**WHAT IT MUST NAME — one row per mitigation, all six columns, no blanks:**

| # | column | what it must carry |
|---|---|---|
| 1 | **dictionary file** | path relative to the case root, e.g. `system/fvSolution` |
| 2 | **keyword** | the exact keyword, e.g. `nNonOrthogonalCorrectors` |
| 3 | **registered value** | the exact value that will run |
| 4 | **counterfactual** | the value this lab would use on a §3.1-compliant grid — so the SIZE of the mitigation is on the record, not just its existence |
| 5 | **what it mitigates** | which measured quality number (from (a)) it answers, by value |
| 6 | **blob sha at freeze** | `git rev-parse <prereg_commit>:<path>` for the file in column 1 |

**THE MINIMUM SET, because "registered" must not mean "whatever we happened to write
down".** A Tier-2 registration is incomplete unless it carries a row — a row stating the
default and *why no change was needed* is a legitimate row — for **each** of:

- `nNonOrthogonalCorrectors` (or the solver's equivalent corrector count);
- the surface-normal-gradient scheme in `system/fvSchemes` (`corrected` /
  `limited <c>` / `uncorrected`) **and its coefficient**;
- the Laplacian scheme and its non-orthogonal treatment;
- every entry under `relaxationFactors` that differs from the case's own compliant-grid
  baseline;
- any wall-treatment or limiter switched on because of this grid.

**WHY (b) IS THE CONDITION THAT WILL ACTUALLY BITE, and it is not a hypothetical.** This
lab has already measured what a committee grid does to a solver: on the HLPW6 coarse grid,
**twenty second-order configurations all diverged inside 29 iterations** and only first
order completed (`docs/DOCKET.md:618`, D253; corroborated at
`docs/inventory/2026-08-24/LAB_INVENTORY.md:57`, *"second-order diverges at iteration 16,
only first order completes"*). That record's own conclusion is the point: it hardened
*"a numerics problem"* into **a discretisation problem**. **Solver-side mitigation is not a
formality on these grids — it is the whole of what makes them solvable, which is exactly
why Sanaa requires it registered BEFORE the run rather than described after it.**

**AND IT MUST BE PROVEN ACTIVE, NOT MERELY PRESENT.** Charter §9's lever-activity clause
(v1.5, L-40) applies with full force and is the half that makes this checkable: **each
registered mitigation must be shown ACTIVE in the runtime log of the run being graded**,
not merely present in the input dictionary. A registered corrector count that the solver
never exercised is not a mitigation; it is a sentence.

**HOW A GRADER CHECKS IT — five mechanical steps, no judgement:**

1. `git show <prereg_commit>:<prereg_path>` contains the §15.4 heading **verbatim**.
2. The table under it has **≥ 1 row** and **no blank cell**, and covers the minimum set.
3. For every row, `git rev-parse <prereg_commit>:<column-1 path>` **equals column 6**.
4. For every row, the dictionary file **as it ran** carries column 2 = column 3.
5. For every row, the runtime log shows the lever **active** (§9 lever-activity).

**Any step failing → the grid was not admitted → the CERTIFICATE is refused and the run
reverts to Tier-1 treatment** (`VERIFICATION_CHARTER` §2r.2, quoted at §15.3). **The
physics is not voided and no §2n cause class arises.**

**PLANTED CONTROL.** The §15.4 check is a reader and CLAUDE.md rule 3 binds it: it must be
shown, in the same run, able to see a **non**-compliant registration — plant a row with a
wrong blob sha, or a lever the log does not show active, and prove the check refuses.
**A check that has only ever returned "registered" is not evidence that anything was.**

### 15.5 CONDITION (d), MADE OPERATIONAL — THE LITERAL STRING, AND WHERE IT GOES

> **THE LITERAL STRING, to be carried verbatim, case-sensitive, as a contiguous substring:**
>
> ```
> workshop committee family, quality as published
> ```
>
> **THE FIELD.** It goes in the certificate's **what-was-checked section**. In the lab's
> current generator that is the **`scope` field** — `sdk/chief_engineer/certificate.py`,
> the `scope` parameter of `build_certificate_v2` (documented at :1032 as *"a labelled
> field, not fine print: it states what was actually [checked]"*, rendered as the **Scope**
> row at :1188-1189 and sealed with the run at :603-604). If a future certificate form
> renames that field, the string moves with the *function*, never off the page.

**THE FULL SENTENCE THE STRING SITS IN — the required form:**

```
Grid: workshop committee family, quality as published — <BODY> <WORKSHOP> <FAMILY>
level <LEVEL>, distributed <URL-or-archive>, sha-256 <DIGEST>. Measured quality is
reported, not gated, under MESH_STANDARD §15.3(a); this grid was not built by this lab
and is not evidence of this lab's meshing capability (§15.7).
```

**A grader checks (d) by substring.** The literal string is present in the certificate's
scope field, or condition (d) fails and the certificate does not issue. **It is a
substring test, not a paraphrase test**, precisely so that no lane has to decide whether
its own wording was close enough.

**"Quality as published" is a claim and it is checkable.** The pre-registration cites the
committee's own published quality figures for that grid, and the certificate reports this
lab's measured figures beside them. **Where they disagree, both are printed and the
disagreement is named.** A grid whose measured quality does not match its published
quality is a **finding**, not a rounding note — and it is the one thing that could show the
distributed file and the converted mesh are not the same object.

### 15.6 A FULL CERTIFICATE IS REACHABLE THIS WAY — AND THIS IS THE PART THAT CHANGES

> **Her ruling, verbatim: "A full certificate IS reachable this way — a certificate's
> honesty is disclosure and verification, not our internal birth standard."**

That sentence is the operative change and it is stated plainly rather than buried:
**a Tier-2 grid meeting (0) and (a)–(d) is not capped, not chipped down, and not confined
to a model-form band.** It can carry a `PASS`, a full certificate, and the lab's ordinary
verdict vocabulary, on the same terms as any other admissible mesh.

**And the reason matters more than the permission**, because it is what stops the next
lane reading this as a loophole: *a certificate's honesty is disclosure and verification,
not our internal birth standard.* Tier 2 does not lower the evidence bar — it **relocates**
it. Where Tier 1 buys confidence by controlling how the mesh was born, Tier 2 buys it by
**disclosing exactly what the mesh is** (condition a), **registering in advance what was
done about it** (condition b), **measuring the numerical band on that same family**
(condition c), and **naming the object on the certificate's face** (condition d). Four
disclosures replace one birth standard. **A Tier-2 certificate that is missing any of the
four is not a weaker certificate; it is not a certificate.**

### 15.7 THE HARD LIMIT — A COMMITTEE GRID CAN NEVER CERTIFY THIS LAB'S MESHING CAPABILITY

> **Her words, verbatim: "What committee grids can never do is certify our meshing
> capability — that stays on in-house grids under 70°."**

> **CLAUSE. No Tier-2 grid, and no result obtained on one, may be cited as evidence of this
> lab's meshing capability** — not in `docs/CAPABILITY_GRID.md`, not in a credentials-wall
> entry, not in the capability register, not in a certificate's capability claim, and not
> in a report upward. **Meshing capability is certified on in-house grids meeting §3.1,
> and on nothing else.** *"Never" is her word and it takes no exception.*

The distinction is exact and is worth stating in one line: **a Tier-2 certificate certifies
the PHYSICS this lab computed; it certifies nothing about the MESH this lab did not
build.** Importing a grid faithfully is an import capability (that is what the mesh-import
register row certifies — fidelity), and it is not a meshing capability.

### 15.8 SUPERSESSION — THIS RESOLVES THE R12 QUESTION AS PUT, AND THE QUESTION IS QUOTED

> **Her words, verbatim: "Two-tier mesh standard — this resolves the R12 question."**

**THE QUESTION AS PUT.** It was put by the cfd-supervisor in board 47 of
`docs/LAB_STATE.md`, section heading at **:21961**, under a heading that is itself the
claim:

> **`### 🔴 R12 DOES NOT REACH A CERTIFICATE, AND M6I DOES NOT EVEN QUALIFY FOR R12`**

and, verbatim, at **`docs/LAB_STATE.md:21963-21966`**:

> - `MESH_STANDARD.md:73-82` and ruling R12: *"physics gates and credential verdicts still
>   require compliant meshes -- this exemption never travels to them."* Rung 1's deliverable
>   is pressures against tunnel data = a physics gate. **R12 buys a MODEL-FORM BAND ONLY.
>   Sanaa's "full certificate" is NOT reachable on an R12-exempted grid.**
> - **M6I does not qualify:** R12 covers *"the reference community's OWN CANONICAL
>   verification grid"*. M6I was produced by invoking the public generator ONCE with a
>   namelist **this lab modified** (`target_y_plus` 1.0 -> 0.25, three counts doubled).
>   Reaching R12 needs an actually-distributed canonical family — **a NEW import, gated by
>   Rung 0.**
> - **A band costs MORE, not less, and inverts the shape:** [...] **Three models on one
>   grid, not one model on three grids.**
> - **This is verification's call to confirm or overturn, not cfd's.**

It stands on that board's own measured exhibit at **`docs/LAB_STATE.md:21918-21932`** —
*"FIVE OF FIVE COMMITTEE GRIDS EVER IMPORTED ON THIS BOX BREACH SECTION 3.1 BY 17-20
DEGREES"* — and it was carried to Sanaa's desk as item 3, **`docs/LAB_STATE.md:22006`**:
*"**The committee-grid admissibility wall** — governs Rungs 1, 2 and 3 together."*

**HOW IT IS RESOLVED — and it is resolved by SUPERSESSION, not by an answer.** cfd asked
whether R12 reaches a certificate. **Sanaa did not answer that question; she replaced the
instrument.** R12 is a *narrow exemption to a gate*; §15 is a *two-tier standard* in which
the gate never applied to the object in the first place. The consequences, stated so nobody
has to infer them:

| the question as put | how §15 disposes of it |
|---|---|
| *"R12 buys a MODEL-FORM BAND ONLY"* | **CORRECT ABOUT R12, and R12 is no longer the governing instrument.** §15.6 makes a full certificate reachable on a Tier-2 grid. cfd's reading of R12 is not overturned — it is superseded. |
| *"Sanaa's 'full certificate' is NOT reachable on an R12-exempted grid"* | **True of an R12 exemption; false of a §15 Tier-2 grid.** The two are different objects with different conditions. |
| *"M6I does not qualify"* | **UPHELD, and on stronger ground.** §15.3(0)(2) requires byte-unmodified distribution; M6I's namelist was modified by this lab. M6I is **Tier 1** and its 87.7462° L1 reading is a §3.1 breach. |
| *"a band costs MORE ... three models on one grid, not one model on three grids"* | **MOOT under §15, and inverted.** §15.3(c) requires the numerical band from **the grid family** — three levels of one family. The band-of-models route was R12's shape; it is not §15's. |
| *"This is verification's call to confirm or overturn, not cfd's"* | **Neither. Sanaa ruled it.** It was above both teams, and §15 records it as hers. |

**R12 IS NOT RETIRED BY THIS SECTION AND ITS TEXT IS NOT EDITED.** Retiring a standard or a
ruling is reserved to Sanaa (CLAUDE.md, FIRST-ACTION RULE) and she did not retire it. R12
continues to govern the object it names — *model-form banding on a reference community's own
canonical verification grid* — and its three mandatory conditions are unchanged.
**§3.1's R12 pointer at lines 73–82 is likewise NOT edited**, because editing it would move
every line number below and this section asserts that none moved. **A reader arriving at
§3.1:73-82 must read §15 with it**, and every future citation of R12 in a
validation-against-workshop-data context is **non-conforming** and must cite §15 instead.
⚠ Where R12 and §15 could both be read to reach the same grid, **the overlap is flagged in
§15.9 item 1 and not resolved here.**

### 15.9 WHAT THIS SECTION DOES NOT DO — AND FOUR COLLISIONS FLAGGED, NOT DECIDED

- It **changes no gate value**. §3.1's 70°, its 65–70 band and its action clause are
  untouched; §3.2's skewness 4 and §3.3's aspect-ratio advisory are untouched. Nothing is
  written to `docs/physics_rules.yaml` and §5's change control is not invoked, **because no
  gate value changes.**
- It **retires nothing** and **re-grades nothing**. No existing verdict moves.
- It creates **no** general exemption. Tier 2 reaches **validation-against-workshop-data
  cases on distributed committee grids** and nothing else.
- It does **not** make any grid currently on this box Tier 2. **No grid has been declared
  Tier 2, because a declaration is made at pre-registration and none exists.**

**⚠ FOUR COLLISIONS, NAMED AND REFERRED — this section decides none of them.** *(A fifth, the §2n cause class for a limb failure, was DISSOLVED rather than answered by `VERIFICATION_CHARTER` §2r.2: there is no `NOT A RESULT` to classify.)*

1. **R12's scope overlaps §15's.** A distributed canonical committee grid used for
   model-form banding satisfies R12; the same grid used for validation-against-workshop-data
   satisfies §15. **Which instrument governs a case that is both is not ruled here.**
2. **The birth-certificate machinery does not implement §3.1 at all, and it will
   quarantine Tier-2 grids on SKEWNESS.** Measured, not asserted:
   `sdk/chief_engineer/mesh_certificate.py:44` sets `ACCEPTED_VERDICTS = ("clean",
   "flagged")` and `:47-57`'s `_HARD_ERRORS` fires on the literal `***Max skewness`. Every
   DPW5 committee grid prints it —
   `cases/committee-grids/logs/DPW5_hex_checkMesh.log:109` (`***Max skewness = 14.0594`),
   `DPW5_prism_checkMesh.log:107` and `DPW5_hybrid_checkMesh.log:107` (both
   `***Max skewness = 6.31513`) — so all three are born **`broken`** and
   `certificate_admits()` (:249-274) refuses them entry to a case. **Sanaa's (a) says
   quality is reported "not gated"** and names skewness in her own parenthesis, **but she
   did not name this machinery**, and reading her ruling onto a code path she did not
   mention is the permission laundering rule 9 forbids. **Referred.**
   *(The same measurement shows the converse hazard: these logs print
   `Non-orthogonality check OK.` at 89.71°, 89.94° and 89.9985° — §14.4's finding, live on
   the exact grids this section governs.)*
3. **`_mesh_rows()` has no "reported, not gated" mode.**
   `sdk/chief_engineer/certificate.py:936-999` renders max non-orthogonality as
   `"{v}° vs {gate}° gate"` with a `pass`/`caveat` verdict and no way to suppress it. The
   only lever is the `non_orthogonality_gate` key, and **raising it to force a `pass` would
   print a false measurement** — worse than the breach. **Condition (a) is not satisfiable
   by the current generator without a code change in `sdk/`, which is outside this team's
   folder scope.** Specced, not written. **Referred.**
4. **THE CAPABILITY GRID CARRIES A `CAN NOT DO` WHOSE STATED CAUSE IS THIS GATE, AND IT IS
   A GENERATED FILE.** `docs/CAPABILITY_GRID.md:75` and `docs/capability/cfd_GRID.md:74`
   and `:200` record **3D · steady · transonic** as *"**CAN NOT DO** — attempted 2 cases,
   both `GATE FAIL` at mesh admission on the 70° non-orthogonality gate"*, and the same
   cell names the CRM committee grids (DPW5 / HLPW6) among its evidence. **The verdict
   itself appears to survive §15 on its own facts** — F13 and F1 are in-house Tier-1 builds
   (84.64 / 86.02 / 86.78° and 81.94 / 83.88 / 83.64°, genuine §3.1 breaches) and the
   committee grids in that cell were *"conversion and feasibility probes only, no solve
   graded"* — **but its stated CAUSE is now partly superseded**, since a committee grid is
   no longer barred from that cell by the 70° gate alone. **Two reasons this section does
   not touch it:** the file is **GENERATED** (`scripts/assemble_capability_grid.py`; a hand
   edit is overwritten — `VERIFICATION_CHARTER` §2n.12), and **§15.7 makes the capability
   surface the one place a Tier-2 grid may NEVER be cited**, so an edit there is exactly
   the move that needs a ruler rather than a lane. **Referred.**
   *(Found in the same sweep and NOT a collision, recorded because it is the waiting
   customer: `verification/campaign/NEXT_CASES_SLATE.md:62` slates
   `w1-dpw5-hex-three-level-ladder` at 400 core-min, and `:263` states its mesh source as
   **"committee grids, not ours — which is the whole point"**. A three-level ladder on one
   committee family is §15.3(c)'s exact shape. **No grid is declared Tier 2 by this
   section, that one included.**)*

| assertion | value |
|---|---|
| ruling authority | **[SANAA-RULED]**, 2026-09-03 ~17:30Z, quoted verbatim at §15.1 |
| gate values changed by this section | **0** |
| gates · thresholds · bands · caps · labels created, moved or retired | **0 · 0 · 0 · 0 · 0** |
| rulings retired | **0** (R12 is superseded in scope, not retired; its text is not edited) |
| results re-graded | **0** |
| grids declared Tier 2 by this section | **0** |
| solver compute | **0 core-min, $0.00** |
| collisions flagged and NOT decided | **4** (§15.9); a fifth DISSOLVED by `VERIFICATION_CHARTER` §2r.2 |
| **lines whose number changed above this section** | **0** |
| md5 of this file's HEAD blob before the append | `72cb037d3e2e0224694e102f7a9c0cc8` |
| md5 of this file's first 1,571 lines after the append | `72cb037d3e2e0224694e102f7a9c0cc8` |
| the two digests | `**EQUAL — assertion MEASURED**` (72cb037d3e2e0224694e102f7a9c0cc8, both sides, in the landing commit's own shell invocation) |

### 15.10 CORRECTION, 2026-09-03 — §15.1's QUOTATION IS RESTORED TO STRICT VERBATIM: THE ENUMERATOR IS PUT BACK AND THE EMPHASIS IS TAKEN OFF (v1.11) [SANAA-RULED TEXT; cfd's OWN CORRECTION OF ITS OWN LANDING]

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered,
inserted or deleted. §15.1's rendering is **superseded by this subsection and is NOT rewritten**
— CLAUDE.md rule 6: a frozen file is corrected by a dated amendment at the foot, never by an
edit in place. That is also why this subsection sits **below §15's closing assertion table**
rather than beside §15.1 where a reader would rather find it: putting it there would move every
line after it and break the assertion this file has now made twice. **Disclosed, not tidied.**

**WHAT WAS WRONG.** §15 landed at `d23c08b2` with Sanaa's ruling quoted at §15.1 in a form that
departed from the capture in exactly two ways, both found and reported by the landing lane's own
character comparison rather than discovered later:

1. the capture's own list enumerator **`1. `** was dropped from the head of the quoted span;
2. the whole quotation was wrapped in **one bold-marker pair**.

**Neither altered a word of hers.** The word sequence landed at `d23c08b2` was already
character-identical to the capture — 1,083 characters, degree signs and em dashes included.
**Both are nonetheless departures, and this is the one text in this document that is not the
lab's to shape.**

**THE RULING THAT THESE ARE DEPARTURES** — cfd-supervisor, 2026-09-03, on their own read of
verification's constraint that *"the text quoting Sanaa's ruling must stay verbatim"*:

> **The dropped `1. ` enumerator: RESTORE it.** It is a character of hers. Stopping the quote
> at *"…that stays on in-house grids under 70°"* is correct scoping — item 2 is a different
> subject and does not belong — but where her text is reproduced, it is reproduced.
> **Trimming to the item boundary is scoping; dropping a character inside the retained span is
> editing.**
>
> **The whole-quote bold wrap: REMOVE it. Emphasis is a rhetorical act.** The blockquote already
> marks the text as hers; bolding it is the lab deciding how loudly she said something. It cuts
> the same way whether it amplifies or softens — the point is that it is *our* choice applied to
> *her* words. **A quoted ruling is reproduced, not styled.**

**THE OPERATIVE RENDERING. This supersedes §15.1's.** Sanaa, 2026-09-03 ~17:30Z, from
`etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md:5-20`, item 1 in full and nothing else — no emphasis
added, no enumerator dropped, no character changed. It was extracted from the capture file's own
bytes by the landing script and never retyped:

> 1. Two-tier mesh standard — this resolves the R12 question. The 70° gate
> is our generation standard: every mesh the lab builds must meet it,
> unchanged. Committee grids are a different object: they exist for
> comparability with the workshop's own results, where every participant
> used the same grids. Ruling: committee grids are admissible for
> validation-against-workshop-data cases without meeting the 70° gate,
> under these conditions: (a) their measured quality (max
> non-orthogonality, skewness, the works) is reported on the certificate,
> not gated; (b) solver-side mitigations (non-orthogonal corrector counts,
> relaxation) are registered before running; (c) the numerical-uncertainty
> band still comes from the grid family; (d) the certificate names the
> grid as "workshop committee family, quality as published" in the
> what-was-checked section. A full certificate IS reachable this way — a
> certificate's honesty is disclosure and verification, not our internal
> birth standard. What committee grids can never do is certify our meshing
> capability — that stays on in-house grids under 70°.

**THE SCOPE OF THE TRIM, STATED SO IT CANNOT BE MISTAKEN FOR A CUT.** The quoted span ends where
her item 1 ends. Capture line 20 continues, on the same line, with `2. Rung 0 wording` — the
opening of item 2, the Rung 0 rewording, a different subject that §15 does not govern. **That
text is not omitted because it was inconvenient; it is omitted because it is about something
else.** Item 2 is on the record in the capture and is quoted where it belongs.

**MEASURED, NOT ASSERTED.** The rendering above and the capture span were compared
character-by-character in the correction commit's own shell invocation, after stripping only the
blockquote `> ` prefix that markdown requires on both sides and normalising whitespace:

| reading | value |
|---|---|
| characters, this subsection's rendering | **1,086** |
| characters, `etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md:5-20` item 1 | **1,086** |
| the two strings | **IDENTICAL — measured** |
| characters at `d23c08b2` (enumerator dropped) | 1,083 |
| words altered, then or now | **0** |
| non-ascii characters, both sides | `°` DEGREE SIGN, `—` EM DASH — present and matching |

**WHAT THIS CORRECTION DOES NOT DO.** It changes **no gate value** — §3.1's 70° and its 65–70
band, §3.2's skewness 4 and §3.3's aspect-ratio advisory are untouched, nothing is written to
`docs/physics_rules.yaml`, and §5's change control is not invoked. It creates **no new top-level
section**: the maximum section ordinal in this file remains **15**, and only the section VERSION
moves, **v1.10 → v1.11**. It re-grades nothing, retires nothing, and declares no grid Tier 2. It
does not touch `docs/charters/SUPERVISOR_RULINGS.md`, which is a different file with a different
owner.

| assertion | value |
|---|---|
| ruling authority for the quoted text | **[SANAA-RULED]**, 2026-09-03 ~17:30Z |
| authority for the correction itself | cfd-supervisor, 2026-09-03, quoted above |
| max section ORDINAL in this file | **15** — unchanged by this subsection |
| section VERSION | **v1.10 → v1.11** |
| gate values changed | **0** |
| gates · thresholds · bands · caps · labels created, moved or retired | **0 · 0 · 0 · 0 · 0** |
| results re-graded | **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's first 1,976 lines before the append | `976955e58fbad295e648d17f24cc4934` |
| md5 of this file's first 1,976 lines after the append | `976955e58fbad295e648d17f24cc4934` |
| the two digests | **EQUAL — assertion MEASURED, in the correction commit's own shell invocation** |
# DRAFT for `docs/standards/MESH_STANDARD.md` — Section 11

**Status: DRAFT, handed to the cfd supervisor. NOT COMMITTED TO THE STANDARD.**
`docs/standards/MESH_STANDARD.md` is his territory; this lane drafts, he appends
and commits. To adopt: append §16 verbatim at the foot of that file under
standing rule 6, bump **v1.6 → v1.7**, and carry the assertion line. This draft
file is then superseded and may be deleted.

Every number below is cited. Numbers marked **[VERIFIED HERE]** were
re-derived or re-read by this lane in this session against the artifact named.
Numbers marked **[CITED]** are read from another lane's committed record and are
attributed to it rather than re-measured.

---

## 16. SNAPPYHEXMESH LAYER SPECIFICATION: ABSOLUTE IS THE DEFAULT (v1.11, 2026-09-13)

### 16.0 Why this section exists, and why no published source will ever supply it

Three public cases were taken to their published setups under Sanaa's
section-G rule in September 2026. **None of them uses snappyHexMesh:**

| Case | Published setup | Mesher | Can it express our failure? |
|---|---|---|---|
| DrivAer | Ashton, West, Lardeau & Revell (2016), *Computers & Fluids* 128:1-15 | **STAR-CCM+ v9.04** — prism layer is an independently extruded region with its own total thickness | **No** |
| PPTC VP1304 | Sikirica et al. (2019); smp'11 participants | **block-structured** — no octree, **no level-0 cell** | **No** |
| DrivAer | Ashton et al. (2024/2025), DrivAerML, arXiv:2408.11969v2 | OpenFOAM v2212 solver, meshed in **ANSA 24.1.0 HeXtreme** | **No** |

**Three for three. No published source is going to warn this lab about a
snappyHexMesh relative-thickness defect, because none of them has a relative
thickness to get wrong.** Retrieval cannot close this gap. A lab-side rule can.

This section is **house practice with its evidence attached**, at the maturity of
§7: **nothing here is written to `docs/physics_rules.yaml` and no code enforces
it yet.** It binds by being quoted, not by being checked, until §16.8 is built.

---

### 16.1 RULE L1 — ABSOLUTE SIZING IS THE DEFAULT. RELATIVE IS THE EXCEPTION.

> **`relativeSizes true` is REFUSED for any snappyHexMesh layer specification in
> this lab unless the background mesh's minimum level-0 edge has been MEASURED
> and DECLARED in the registration.**
>
> Absolute sizing (`relativeSizes false`, thicknesses in metres) is the default
> and needs no declaration. A relative specification without a declared,
> measured `level0Edge` is **not a layer specification**; it is a layer
> specification multiplied by an unknown.

**Declaration format** (goes in the pre-registration, beside the dictionary):

```
level0Edge_declared   = <value> m
level0Edge_source     = constant/polyMesh/level0Edge   (read from disk, not assumed)
level0Edge_expected   = <the base cell you intended> m
ratio_actual_expected = <expected/actual>          # MUST be 1.00 +- 0.01, or L1 refuses
smallest_feature      = <what sets the global minimum, and where it is>
```

If `ratio_actual_expected` is not 1, **the mesh does not mean what the dictionary
says** and the specification is converted to absolute before the run.

---

### 16.2 THE MECHANISM — why one small feature anywhere rescales layers everywhere

Under `relativeSizes true`, every layer thickness is a multiple of
`level0EdgeLength()`. **That function returns the GLOBAL MINIMUM level-0 edge in
the entire mesh**, and OpenFOAM's own source says so in its own comment.

**[VERIFIED HERE]** — read directly from this box's
`/usr/lib/openfoam/openfoam2606/src/dynamicMesh/polyTopoChange/polyTopoChange/hexRef8/hexRef8.C`
(OpenFOAM **api=2606, patch=0**, `META-INFO/api-info`):

| Line | Source text |
|---|---|
| **357** | `// Bit complex way to determine the unrefined edge length.` |
| **436** | `typEdgeLenSqr[eLevel] = min(typEdgeLenSqr[eLevel], edgeLenSqr);` |
| **441-442** | `// Get the minimum per level over all processors. Note minimum so if`<br>`// cells are not cubic we use the smallest edge side.` |
| **443** | `Pstream::listReduce(typEdgeLenSqr, minOp<scalar>());` |
| **505** | `// Find lowest level present` |
| **514** | `level0Size = Foam::sqrt(lenSqr)*(1<<levelI);` |

`min` at the edge, `minOp` across ranks, then the lowest level present scaled up
by `2^level`. **There is no averaging and no locality anywhere in that path.**
The single smallest level-0 edge in the mesh — wherever it is, however irrelevant
to the surface being layered — sets the scale for every relative thickness on
every patch.

**The measured case. [CITED]** — `verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:83-85`
and `cases/PPTC_VP1304/PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md:223-226`. On the
PPTC wedge the global minimum is the **azimuthal chord of the 2 mm axis rod**:

**[VERIFIED HERE]** the arithmetic reproduces exactly —
`2 · 0.002 · sin(pi/60) = 2.09343825e-04 m` (a 6-degree segment, 60 around the
circle), agreeing with `constant/polyMesh/level0Edge` to **eight significant
figures**, against an intended base cell of 0.020 m:

    0.020 / 2.09343825e-04 = 95.54

**Every relative layer thickness on that mesh was 95.5x too small**, and the rod
is not part of the propeller. **A 2 mm feature on the axis rescaled the layer
growth on the blades.**

---

### 16.3 RULE L2 — THE ONE-LOCAL-CELL RULE

> **A layer stack that asks for more than ONE local cell of total thickness is
> asking the mesher for room it does not have.** Compute the requested stack in
> local cells before the run and record it. Above 1.0, expect collapse; the
> registration must either reduce the stack or state why it expects the
> exception.

Stack in local cells, for `relativeSizes true` with `finalLayerThickness t_f`,
`expansionRatio r`, `nSurfaceLayers N`:

    S = t_f * sum_{i=0}^{N-1} r^(-i)          [multiply by the local cell to get metres]

and for `relativeSizes false`, divide the absolute `thickness` by the local cell
(base cell / 2^refinement level).

**Both sides of the rule are now measured.**

| | **DrivAerML (published, OpenFOAM)** | **Certonomous DrivAer** |
|---|---|---|
| Total stack | **12 mm** absolute | **42.0 mm** |
| Local surface cell | 25 mm (our level-4 equivalent) | **25.0 mm** |
| **STACK IN LOCAL CELLS** | **0.480** | **1.6808** |
| First layer | **0.75 mm** | **5.12 mm** |
| Layers requested | 7 | 5 |
| **Outcome** | **EXTRUDES** | **COLLAPSES — 2.50 of 5 (coarse), 2.89 of 5 (medium)** |

**[VERIFIED HERE]** all six of our values. Our stack:
`0.5 * sum(1.25^-i, i=0..4) = 0.5 * 3.3616 = 1.6808` local cells, from
`verification/runs/navier_class/DRIVAER/r2_medium/system/snappyHexMeshDict:194-197`
(`relativeSizes true; finalLayerThickness 0.5; expansionRatio 1.25;
minThickness 0.02`) with `nSurfaceLayers 5`. Local cell 25.0 mm = blockMesh base
0.400 m (`r2_medium/system/blockMeshDict`, hex `(30 50 30)` over a 12 m block)
divided by `2^4` at surface `level (4 4)`. Achieved coverage from
`verification/runs/navier_class/DRIVAER/LAYERS_ACHIEVED_MEASURED.json`
(post-extrusion, per L-590).
**[CITED]** DrivAerML from `cases/navier_class/DRIVAER/PUBLISHED_SETUP_INGEST_drivaerml_2024.md`
§3.2, quoting arXiv:2408.11969v2 sidecar L269-275.

**Why the failure is total rather than patchy: the margin is of order one.**
**[CITED]** `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:56-70`. On PPTC the blade
prisms' collapsed side faces produced a pyramid volume
`w^2 t / 6 = 8.558e-14` against `minVol 1e-13` — **failing by 1.17x**, i.e.
**2.448 sub-`minVol` faces per blade prism cell** (`:65`). A defect whose margin
is 1.17x does not degrade gracefully; it takes the whole extrusion. **Do not
expect a too-thick stack to give you fewer layers. Expect it to give you none.**

---

### 16.4 RULE L3 — UNDER `relativeSizes true`, ACHIEVED THICKNESS IS A FUNCTION OF REFINEMENT LEVEL

> **The same relative dictionary produces different layers on different patches.**
> A relative specification is therefore not a specification of the boundary
> layer; it is a specification of a *ratio to whatever cell happens to be there*.
> **An absolute specification is uniform by construction.**

**[VERIFIED HERE]**, our own dictionary, same four numbers, two refinement levels:

| Patch refinement | Local cell | **Our stack** | **Our first layer** | DrivAerML absolute |
|---|---|---|---|---|
| `level (4 4)` | 25.0 mm | **42.0 mm** | **5.12 mm** | 12 mm / 0.75 mm |
| `level (5 5)` | 12.5 mm | **21.0 mm** | **2.56 mm** | 12 mm / 0.75 mm |

Our `BodyDoorhandles` and `BodyHeadlamps` sit at `level (5 5)` while
`BodyHood`, `BodyFender` and `BodyRear` sit at `level (4 4)`
(`r2_medium/system/snappyHexMeshDict:201-208`). **Under one dictionary those
patches get boundary layers differing by a factor of two, and nothing in the
dictionary says so.** Under DrivAerML's absolute recipe every patch gets
12 mm / 0.75 mm.

This is also why y+ cannot be reasoned about from a relative dictionary: y+ is
set by the first cell in metres, and a relative dictionary does not state one.

---

### 16.5 RULE L4 — `minThickness` CONVERTS IN THE SAME EDIT, OR THE MESH REFUSES EVERY LAYER

> **Converting `relativeSizes true` to `false` converts EVERY thickness field in
> the same edit, `minThickness` included.** A converted dictionary that leaves
> `minThickness` at its relative value is worse than the unconverted one: the
> floor is then read as metres and rejects every layer that was going to work.

**[CITED]** `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:120-129`, whose own
dictionary comment registers the trap in situ:

```
    relativeSizes   false;                      // was true
    minThickness        3.125e-5;               // m  (MUST convert: 0.05 absolute = 50 mm)
```

`minThickness 0.05` left unconverted is read as **0.05 m = 50 mm** — on a case
whose intended blade first layer is `3.125e-4 m`, a floor **160x** above the
layer it is meant to protect. **[VERIFIED HERE]:** the same trap is armed in our
DrivAer dictionary today — `minThickness 0.02` at
`r2_medium/system/snappyHexMeshDict:197` would become **20 mm** absolute against
a target first layer of 0.75 mm.

**[CITED]** `PRISM_A2:132-135` also records that per-patch `finalLayerThickness`
and `minThickness` are honoured under the global switch (`minThickness` is read
after the switch, outside the `thicknessModel` branch), so the conversion is
per-patch as well as global.

---

### 16.6 RULE L5 — READ THE POST-EXTRUSION TABLE. AN ABSENT TABLE MEANS ACHIEVED = 0, NEVER "UNKNOWN".

> **The per-patch layer table printed by snappyHexMesh before extrusion is the
> REQUEST. Coverage is read only from the POST-EXTRUSION table** (L-590).
> **And a run that extrudes nothing prints NO post-extrusion table at all** — so
> the absence of the table is a positive finding of zero, not missing data. A
> reader that reports "unknown" on an absent table will report the request table
> as the achievement.

**[VERIFIED HERE]** — the control flow, read from this box's
`/usr/lib/openfoam/openfoam2606/src/mesh/snappyHexMesh/snappyHexMeshDriver/snappyLayerDriver.C`:

| Line | Source text | Brace depth |
|---|---|---|
| **4958** | `for (label layeri = 0; layeri < layerParams.nOuterIter(); layeri++)` | loop opens, depth 1 |
| **5097** | `// Exit if nothing added` | |
| **5098** | `const label nTotalAdded = gSum(patchNLayers);` | |
| **5104** | `if (nTotalAdded == 0)` | |
| **5106** | **`break;`** | depth 3 |
| **5211** | **`printLayerData`** | **depth 3 — INSIDE the same loop** |
| **5369** | loop closes | |

**`printLayerData` at 5211 is inside the loop that the `break` at 5106 exits.**
If the first outer iteration adds zero layers, the break fires and
`printLayerData` is **never reached**. The log then contains the request table
and nothing else, and the request table looks authoritative.

**[VERIFIED HERE]** the empirical counterpart, from our own
`LAYERS_ACHIEVED_MEASURED.json`, case `DIAG_v5_coarse_layersON_mergeTol1e-8`:
`achieved_table_line: null`, `request_table_line: 3600`, `request_table_rows: 50`,
`extruding_faces: 0`, `added_cells: 0`, `cell_delta: 0`, `no_layer_exists: true`.
**Fifty request rows, zero achievement rows, zero layers.** L-590 is the lesson
that a parser reading the request column would have reported
"blades 6.00 of 6 nominal, coverage 100.0 %, SPECIFICATION MET".

**Required reader behaviour:** a layer reader must cross-check the request table
against **at least one independent extrusion witness** — `added_cells`,
`cell_delta`, or `extruding_faces` — and report **achieved = 0** when the
achievement table is absent. It must never emit "unknown".

---

### 16.7 THE COST OF THE FIX, STATED BECAUSE THE FIX IS NOT FREE

> **`relativeSizes false` on ANY ONE PATCH disables the warped-face extrusion
> check for the WHOLE MESH.** This is a real quality safeguard that absolute
> sizing gives up, and §16.1 requires it to be disclosed on the certificate, not
> discovered later.

**[VERIFIED HERE]**, `snappyLayerDriver.C` (v2606), read directly:

```
3785     // Disable extrusion on warped faces
3786     // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
3787     // It is hard to calculate some length scale if not in relative
3788     // mode so disable this check.
3789     if (!layerParams.relativeSizes().found(false))
3790     {
3792         const scalar edge0Len =
3793             meshRefiner_.meshCutter().level0EdgeLength();
3796         handleWarpedFaces
```

`relativeSizes()` is a `boolList`, so `found(false)` is **true as soon as one
patch is absolute**, and the guard fails mesh-wide. `handleWarpedFaces`
(defined `:817`) is the check that disables extrusion on faces too warped to
carry a layer; it is skipped entirely. **[CITED]** the same reading is the cfd
supervisor's ruling on W1 at `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:6-8`.

Note the irony and record it: `handleWarpedFaces` itself consumes
`level0EdgeLength()` (`:3792-3793`), the same global minimum §16.2 indicts. **On a
mesh with a small stray feature the warped-face check was being fed a wrong
length scale anyway.** That is a reason to declare `level0Edge` under §16.1, not
a reason to keep relative sizing.

**Required disclosure** on any birth certificate for a mesh with an absolute
layer spec: `handleWarpedFaces: DISABLED (relativeSizes false on >=1 patch,
snappyLayerDriver.C:3789)` plus the checkMesh face-warpage metrics, so the reader
knows which safeguard was traded for which.

---

### 16.8 THE CHECKLIST — what a registration must carry before a layered snappy run

1. `relativeSizes` stated. If `true`: the §16.1 declaration block, with
   `level0Edge` **read from `constant/polyMesh/level0Edge`**, not assumed.
2. **Requested stack in local cells**, computed per §16.3 and printed. `> 1.0`
   requires a stated exception.
3. **First layer in METRES**, per patch refinement level, for every distinct
   level in the layer spec (§16.4).
4. `minThickness` in the same units as the rest of the spec, checked against the
   first layer it must not exceed (§16.5).
5. The layer reader's **planted control**: plant a known coverage, read it back
   from the post-extrusion table, refuse if unseen (standing rule 3).
6. Post-run: achieved coverage from the **post-extrusion** table; **absent table
   recorded as achieved = 0** (§16.6).
7. If absolute: the **`handleWarpedFaces: DISABLED`** disclosure (§16.7).

**Nothing here is enforced by code yet.** Building the check into the birth
certificate (§6) is the natural next step and is not done; until then this is a
reviewer's checklist, and a registration that omits an item is incomplete rather
than refused.

---

### 16.9 SCOPE, AND WHAT THIS SECTION DOES NOT CLAIM

- Binds **snappyHexMesh layer specifications** only. Silent on block-structured,
  ANSA, STAR-CCM+ or any other mesher — §16.0 is precisely the observation that
  those cannot express this failure.
- **Not retroactive.** No frozen ladder is re-opened, no closed verdict moves, no
  existing gate value in §3 changes. It governs **how the next layer spec is
  written**, not what any past one was.
- **Changes no gate in `docs/physics_rules.yaml`** and adds no enforced
  threshold. The one-local-cell rule of §16.2 is a **design rule with two
  measured points** (0.480 extrudes, 1.6808 collapses), not a calibrated
  threshold — the lab has not bracketed where between them the transition sits,
  and this section does not pretend otherwise.
- The 1.17x `minVol` margin and the 95.5x `level0Edge` factor are **[CITED]** from
  the PPTC lane's frozen record, not re-measured here. The arithmetic
  `2*0.002*sin(pi/60) = 2.09343825e-04` and `0.020/2.09343825e-04 = 95.54` **was**
  re-derived here and reproduces.

### 16.10 Sources

| Source | Used for |
|---|---|
| `/usr/lib/openfoam/openfoam2606/.../hexRef8/hexRef8.C:357,436,441-443,505,514` | §16.2, the global-minimum mechanism |
| `/usr/lib/openfoam/openfoam2606/.../snappyLayerDriver.C:817,3785-3796,4958,5097-5107,5211,5369` | §16.6 control flow, §16.7 warped-face guard |
| OpenFOAM `META-INFO/api-info` — `api=2606, patch=0` | the version all line numbers refer to |
| `verification/runs/navier_class/DRIVAER/r2_medium/system/snappyHexMeshDict:194-197,201-208` | §16.3, §16.4, §16.5 our values |
| `verification/runs/navier_class/DRIVAER/r2_medium/system/blockMeshDict` | §16.3 base cell 0.400 m |
| `verification/runs/navier_class/DRIVAER/LAYERS_ACHIEVED_MEASURED.json` | §16.3 achieved 2.50/2.89, §16.6 absent-table case |
| `cases/navier_class/DRIVAER/PUBLISHED_SETUP_INGEST_drivaerml_2024.md` §3.2 | §16.3 DrivAerML 12 mm / 0.75 mm / 7 layers |
| `cases/navier_class/DRIVAER/PUBLISHED_SETUP_INGEST_ashton_2016.md` | §16.0 STAR-CCM+ row |
| `cases/PPTC_VP1304/PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md:223-226` | §16.2 level0Edge diagnosis |
| `verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:6-8,56-70,83-85,120-135` | §16.2, §16.3 minVol, §16.5 minThickness, §16.7 W1 ruling |
| `docs/LESSONS.md` L-590 | §16.6, request vs achievement |

---

**Appended at the foot under standing rule 6. Version 1.6 → 1.7. Lines whose
number changed above this section: 0.** Nothing above §16 is edited, and no gate
value anywhere in this standard moves.

# DRAFT for `docs/standards/MESH_STANDARD.md` — Section 17

**Status: DRAFT, handed to the cfd supervisor. NOT COMMITTED TO THE STANDARD.**
This lane drafts; he appends and commits. To adopt: append §17 verbatim at the foot
of that file under standing rule 6 and carry the assertion line, **measured, not
asserted** (md5 of the first 2,429 lines before and after the append).

**The ordinal and the version were derived from the document's own tail in the same
shell invocation as this write**, per the §14 lesson that the two counters diverged
once already and that neither may be read off a neighbouring section:

```
max section ordinal present = 16   (ordinals run 1..16, contiguous, no gaps)  -> THIS IS SECTION 17
max section version present = v1.11 (v1.1..v1.11, and v1.11 is used TWICE)    -> THIS IS v1.12
md5 of MESH_STANDARD.md at draft time = 2ee7cf76f8c8c10adfc465885a04df1c, 2429 lines
```

Numbers marked **[VERIFIED HERE]** were read by this lane from the named file on
disk in this session. Numbers marked **[CITED]** come from another record and are
attributed to it.

---

## 17. PUBLISHED SNAPPYHEXMESH LAYER PRACTICE — SIX DICTIONARIES ON DISK, WHAT THEY SETTLE, AND WHAT THEY DO NOT (v1.12, 2026-09-13)

### 17.0 THIS SECTION EXISTS BECAUSE §16.0's CENTRAL EMPIRICAL CLAIM IS NOW FALSE

§16.0, committed at `50ce30f5` at 17:37 on 2026-09-13, says — and the claim is
load-bearing, because it is the argument for why §16 had to be house practice
rather than published practice:

> **Three for three. No published source is going to warn this lab about a
> snappyHexMesh relative-thickness defect, because none of them has a relative
> thickness to get wrong.** Retrieval cannot close this gap. A lab-side rule can.

**Retrieval closed the gap eighteen minutes later.** Under Sanaa's §J and §K
case-file instruction, three trees of *actual OpenFOAM case files* were retrieved,
hashed and parse-verified (`docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`,
committed `799c88e7`). They contain **six snappyHexMesh layer dictionaries**, every
one of which states `relativeSizes`, `nSurfaceLayers`, `expansionRatio`, a first- or
final-layer thickness, `minThickness` and `featureAngle` explicitly.

**§16.0's table is not wrong; its generalisation is.** The three sources §16.0 names
— Ashton et al. 2016 (STAR-CCM+), Sikirica et al. 2019 (block-structured),
DrivAerML 2024 (ANSA HeXtreme) — genuinely have no relative thickness to get wrong,
and they were *papers*. The error was concluding from three papers that **no**
published source could speak to this, when the objects that speak to it are **case
files, not papers** — and papers publish what a mesher produced, never its
dictionary. That distinction is the whole content of Sanaa's §G rule.

**§16's RULES L1 through L5 are untouched by this section and remain in force.**
What changes is §16.0's claim that published practice is unavailable, and one
numeric reading inside §16.3, narrowly, at §17.4.

---

### 17.1 THE SIX POINTS, WITH PROVENANCE

**[VERIFIED HERE]** — every row read from the file named, in a tree whose per-file
sha256 manifest is recorded in `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md` §1.

| Case | Dictionary | `relativeSizes` | N | r | thickness as written | Background block | Base cell | Wall level | **S, local cells** |
|---|---|---|---|---|---|---|---|---|---|
| Wolf Dynamics DrivAer **coarse** | `drivaer_coarse/system/snappyHexMeshDict` | `true` | 3 | 1.2 | `finalLayerThickness 0.3` | uniform hex, `deltax=deltay=deltaz=0.2` | **0.2 m** | `body2 (3 3)` | **0.758333** |
| Wolf Dynamics DrivAer **fine** | `drivaer_fine/system/snappyHexMeshDict` | `true` | 6 | 1.2 | `finalLayerThickness 0.3` | same deltas | **0.2 m** | `body2 (4 4)` | **1.197184** |
| occDrivAer rotating mesh (Upstream CFD) | `occDrivAerRotMesh.orig/system/snappyHexMeshDict.full:512-516` | `true` | 2 | 1.2 | `finalLayerThickness 0.5` | 120×44×20 over 120×44×20 m | **1.0 m** | L9 body | **0.916667** |
| ONERA M6 (Alletto) | `OneraM6Wing/system/snappyHexMeshDict` | `true` | 5 | 1.5 | `finalLayerThickness 0.5` | 30×15×30 over ±18000 | **1200 units** | `wing (8 9)` | **1.302469** |
| ESI marine propeller (MB13) | `marinePropeller/system/snappyHexMeshDict:265-280` | **`false`** | 5 | 1.20 | `firstLayerThickness 1.0e-04 m` (tip), `2.0e-04 m` (stem) | 40×80×40 over 1.2×2.4×1.2 m | **0.03 m** | tip (4 5), stem (4 4) | **0.79377** (both) |
| High-lift CRM ONERA | `highLiftCommonResearchModelONERA_LRM-LDG-HV/system/snappyHexMeshDict:2075-2095` | `true` | 2 | **1** | `finalLayerThickness 0.8` | not extracted | — | — | **1.600** |

Arithmetic, so every S is re-derivable without opening a file:
`S = t_f · Σ_{i=0}^{N-1} r^(-i)` for a relative *final* thickness, and
`S = t_1 · (r^N − 1)/(r − 1) ÷ local cell` for an absolute *first* thickness.
Local cell = base cell ÷ 2^level.

**Set against §16.3's two measured points — 0.480 EXTRUDED, 1.6808 COLLAPSED — every
one of the six published requests falls between them**, clustering 0.76–1.30, with a
single outlier at 1.600 whose mechanism is §17.5.

---

### 17.2 THE LIMIT OF THIS EVIDENCE, STATED BEFORE ANY USE IS MADE OF IT

> **A published dictionary is a REQUEST. It is not an ACHIEVEMENT.**
> None of the six may be cited as a stack that extruded.

**No retrieved tree ships a `snappyHexMesh` log or a layer-coverage table for any of
these six cases.** [VERIFIED HERE] The only solver logs in the Wolf Dynamics tree are
`sol_logs/{coarse,fine}/log.solver`, which are `simpleFoam` runs; the string `layer`
occurs in `sol_logs/coarse/log.solver` **zero times**.

**PLANTED CONTROL, because a zero from a reader not shown able to see a non-zero is
not evidence** (standing rule 3). The same sweep, over the same three trees, with the
same pattern, **did** return `log.snappyHexMesh` files — in
`alletto-openfoamtutorials/membranBCSend/.../circularMembrane230Pa/` and
`circularMembrane230PaFine/`. **The reader can see a snappyHexMesh log when one
exists. It found none for any of the six.** The zero is therefore evidence.

**Worse for the Wolf Dynamics rows specifically: its shipped results cannot be
attributed to its snappy mesh at all.** [VERIFIED HERE] The tree ships *two mutually
exclusive* mesh routes — `run_mesh_shm.sh` (blockMesh + snappyHexMesh) and
`run_mesh_fluent.sh` (`fluent3DMeshToFoam mesh/mesh_coarse.msh`) — and its own
`README.TXT` recommends the second: *"Generating the mesh with SHM is time consuming
so better use the pre-generated mesh."* The shipped `log.solver` records
`Case : /home/joegi/OF_training/UNISA/COURSE/session2/Xdrivaer`, `Date : Apr 20
2022`, `nProcs : 4`, and names no mesher. **Which of the two meshes produced the
distributed `Cd` and `y+` is not recoverable from the tree.**

**Consequence for every use below.** These six points are evidence of what expert
practitioners *request* on this mesher — real evidence, and the lab had none of it an
hour ago. They are **not** evidence that any of those requests was granted. No rule
in this section converts a published S into a demonstrated-safe S.

---

### 17.3 RULE L6 — `relativeSizes` IS TOPOLOGY-CONDITIONAL, AND THAT IS WHY §16's L1 IS RIGHT FOR THIS LAB AND WRONG AS A DESCRIPTION OF THE WORLD

> **`relativeSizes true` is correct practice on a uniform Cartesian background block
> and catastrophic on a graded or wedge background.** The discriminator is not the
> flag; it is whether `hexRef8::getLevel0EdgeLength()` — the **global minimum**
> level-0 edge in the whole mesh — equals the base cell the author had in mind.
> **A registration that sets `relativeSizes true` must state the background topology,
> not merely the measured `level0Edge`.**

**[VERIFIED HERE]** Four of six use `true`, two use `false` — **and all six mesh a
body inside a uniform Cartesian block**, in which the global minimum level-0 edge
*is* the base cell and relative sizing means exactly what it says. **No retrieved
case uses `relativeSizes true` on a non-uniform background.**

The two that turn it off are the two whose thicknesses are physically pinned — the
ESI marine propeller (acoustics, absolute metres) and the aeroacoustic DrivAer
(33 body patches at `firstLayerThickness` 5.25e-06 to 1.17e-05 m). **Neither turns it
off to escape a topology defect.** They turn it off because they want a stated y+.

**This strengthens §16.1 rather than weakening it, and it changes its reasoning.**
L1 refuses `relativeSizes true` without a declared, measured `level0Edge`. The
published population shows *why* that refusal is right **here specifically**: this
lab's PPTC background is a **72° wedge**, whose global minimum level-0 edge is a 2 mm
axis rod's azimuthal chord, **2.09343825e-04 m**, poisoning every thickness by
**95.5×** [CITED, `docs/standards/MESH_STANDARD.md` §16.2]. Nobody in the published
set meshes on a wedge. **The world does not warn about this defect because the world
does not build the topology that has it.**

**Corollary, and it is the PPTC design decision.** Published propeller practice is
`relativeSizes false` **together with** a full-360° Cartesian box — the ESI case is
both at once. **The two choices travel together and neither alone is the published
practice.** A registration that adopts the absolute thicknesses but keeps the wedge
has adopted half of it.

---

### 17.4 SUPERSESSION, NARROW: §16.3's "ABOVE 1.0, EXPECT COLLAPSE" IS NOT SUPPORTED AS A NUMERIC THRESHOLD, AND ITS REGISTRATION DISCIPLINE IS UNAFFECTED

§16.3 rule L2 reads, in part:

> **A layer stack that asks for more than ONE local cell of total thickness is asking
> the mesher for room it does not have.** [...] **Above 1.0, expect collapse**

**[VERIFIED HERE]** Three of the six published requests sit above 1.0 — 1.197184,
1.302469 and 1.600 — and a fourth sits at 0.917. **Expert practitioners on this
mesher routinely request above 1.0.** §16.3 itself is explicit that it rests on
**"two measured points and only two"**, and the lower of those two (0.480) is now
shown to be **below every published request**, i.e. it was never near the transition.

**What is superseded:** the reading of **1.0** as a physical threshold at which
collapse begins. It is not one. The lab's own collapse at **1.6808** remains a
measurement and is not disturbed; what the six points show is that the transition
lies **somewhere above 1.30 and at or below 1.6808**, not at 1.0.

**What is NOT superseded, and is the part that matters:**
1. **Compute S before the run and record it in the registration.** Unchanged, and
   §17.2 makes it more necessary, not less: since no published case evidences
   achievement, S is a design number that must be declared and then *measured against
   the post-extrusion table* (§16.6 rule L5).
2. **§16.3's failure-mode warning is untouched and was never about the threshold:**
   *"Do not expect a too-thick stack to give you fewer layers. Expect it to give you
   none."* The mechanism cited for it — a pyramid volume failing `minVol` by 1.17×
   [CITED, `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:56-70`] — is a margin-of-order-one
   argument that does not depend on where the threshold sits.
3. **The lab's own 1.6808 collapse** [CITED, §16.3], which is a measurement on this
   box and outranks any published request.

**Restated clause, for L2:**

> Compute the stack in local cells, `S`, and record it in the registration.
> **Published snappyHexMesh practice spans S = 0.76 to 1.60** (§17.1), so a value in
> that band is not by itself a defect and needs no exception. **This lab has measured
> a collapse at S = 1.6808 and an extrusion at S = 0.480**; between 1.30 and 1.68 is
> unbracketed. **Above 1.60, a registration states its expectation explicitly and
> cites the post-extrusion table that will test it.** No value of S is
> demonstrated-safe on this box above 0.480 until a run measures it here.

---

### 17.5 THE 1.600 CASE BUYS ITS HEIGHT WITH TWO SETTINGS, AND THAT IS A MECHANISM, NOT A COINCIDENCE

**[VERIFIED HERE]** The high-lift CRM ONERA case is the only published request near
the lab's collapse point, and it differs from the other five in exactly two fields:

| Field | High-lift CRM | Other five |
|---|---|---|
| `expansionRatio` | **1** | 1.2 (four), 1.5 (one) |
| `maxThicknessToMedialRatio` | **3** | **0.3** (Wolf Dynamics, occDrivAerRotMesh, M6 Alletto, ESI propeller — all four) |
| `nGrow` | **−1** | 0 (all five) |

`maxThicknessToMedialRatio` is the field that reduces layer growth where the stack is
large relative to the distance to the medial axis — i.e. **the field that decides
whether a tall stack is thinned or kept**. Ten times the value every other case uses,
paired with a *uniform* layer stack (`expansionRatio 1`, so no geometric growth to
amplify), is a coherent way to ask for 1.6 local cells and expect to keep it.

**Registration consequence.** A registration asking for `S > 1.30` **states its
`maxThicknessToMedialRatio` and `expansionRatio` beside the S**, because at 0.3 and
1.2 — this lab's values, and four of the five others' — there is no published case
above 1.302 to point at. **[VERIFIED HERE]** the lab's collapsed DrivAer ran
`expansionRatio 1.25` at S = 1.6808 [CITED, §16.3], i.e. **the high-ratio, high-S
combination that no published case uses.**

---

### 17.6 PRISM-A2 IS NOW REGISTERED AT S = 0.794, AND HALF OF THE REASONING THAT MOVED IT THERE IS WITHDRAWN BY §17.2

**The sequence, because the record has to carry it.** PPTC PRISM-A2 Amendment 1 registered
**S = 1.000** under an explicit hedge: *"`S = 1.00` is NOT in the demonstrated-safe region.
§16.3's rule rests on two measured points and only two."* Amendment 2, committed
**`b3deca9b3` at 18:23:56Z on 2026-09-13**, struck that and moved the target to
**S = 0.794**, giving as its reason:

> *"That hedge is now superseded by evidence. Six published OpenFOAM cases report stacks of
> 0.758, 0.794, 0.917, 1.197, 1.302, 1.600 local cells."*
> — `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md`, Amendment 2

**§17.2 withdraws half of that reason, and the half it withdraws is the load-bearing half.**
Those six numbers are what those cases **ask for**. **No retrieved tree ships a
snappyHexMesh log or a layer-coverage table, so not one of the six is evidence that the
layers appeared.** A band populated by people willing to ship those numbers is not a band
demonstrated to extrude. **"Published practice achieves 0.794" is not a supported
statement and must not be made.**

**THE RULING SURVIVES ON A DIFFERENT AND WEAKER BASIS, AND THE WEAKER BASIS IS THIS LAB'S
OWN MEASUREMENTS:**

> **0.794 is nearer to the only stack this lab has measured EXTRUDING — our own 0.480 —
> and further from the 1.6808 we measured COLLAPSING, than 1.000 is.** That is the whole
> of the support, it comes from two measurements on this box, and it is enough to prefer
> 0.794 over 1.000 without being enough to call either safe.

**What the six published values DO still establish, stated at its real strength:** that
expert practitioners on this mesher are willing to ship stacks across 0.758–1.600, so a
value inside that band is **not anomalous** and needs no special pleading in a
registration. That is a statement about what is unremarkable to request. **It is not a
statement about what extrudes**, and §17.4's restated L2 clause is worded to claim only
the former.

**Recorded as a method point, because it is why this correction exists at all.** The
absence was found by **planting a control on the claim rather than asserting it**: the
same sweep that returned zero snappyHexMesh logs for the six cases **did** return
`log.snappyHexMesh` files elsewhere in the same trees (§17.2). Had the sweep simply
reported "none found", the absence would have been indistinguishable from a broken reader,
and Amendment 2's reasoning would have stood uncorrected.

### 17.7 THE PER-PATCH PATTERN WAS INDEPENDENTLY REPRODUCED, AND THAT IS THE STRONGEST SINGLE RESULT HERE

**[VERIFIED HERE]** The ESI marine propeller sets `firstLayerThickness 1.0e-04 m` on
`propellerTip` at refinement level 5 and `2.0e-04 m` on `propellerStem1/2` at level 4
— **a factor of two, exactly tracking the factor of two in local cell size**. Both
patches therefore land on the **same S = 0.79377**.

**[CITED]** `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md`, A1.2, arrived at the same
construction without having seen that file: `blades` (level 5) 3.4091e-4 m, `hub` and
`cap` (level 4) 6.8182e-4 m, `shaft` (level 3) 1.3636e-3 m — **each a factor of two
apart, every patch on the SAME S.** (A1.2 set that common S to 1.000; Amendment 2
`b3deca9b3` moved it to 0.794 — **the per-patch PATTERN is unchanged by the move, which is
precisely what makes it a pattern and not a value.**)

> **RULE L7 — Under `relativeSizes false`, set each patch's absolute thickness in
> proportion to its own local cell, so that every layered patch lands on the SAME S.**
> This is what §16.4's rule L3 asks for stated forward: L3 observes that a *relative*
> dictionary gives different physical layers on different patches; L7 is the absolute
> dictionary's answer, and it is published practice, not a lab invention.

Two independent constructions reaching the same design pattern is the nearest thing
to external corroboration this section contains — **and it corroborates the pattern,
not the value.** Neither construction is evidenced as achieved (§17.2), and the pattern
would be the same at any common S.

---

### 17.8 SCOPE, AND WHAT THIS SECTION DOES NOT CLAIM

- It **does not claim any published stack extruded.** §17.2. No achievement record
  exists in any retrieved tree, and the zero carries a planted control.
- It **does not re-grade anything**, retire any gate, or touch §16's rules L1, L3, L4
  or L5. Its only supersession is the numeric reading inside §16.3, at §17.4, and it
  is bounded there.
- It **does not bracket the collapse transition.** It narrows the open interval from
  (0.480, 1.6808) to roughly (1.302, 1.6808) *as a statement about published requests*,
  which is weaker than a measurement. **A real threshold is still a separate
  measurement campaign on this box**, exactly as §16.3 said.
- It **does not claim that published practice ACHIEVES any value**, and it withdraws that
  claim where another record has already relied on it (§17.6). The six values bound what is
  unremarkable to REQUEST; the lab's own 0.480 and 1.6808 are the only extrusion evidence
  that exists anywhere in this section.
- It **does not claim the six cases are comparable to each other.** They span steady
  RANS, DDES and LES, three solvers, and length scales from a 0.224 m propeller to a
  44 m-wide car domain. What is comparable is the one dimensionless quantity S.
- It **makes no claim about OpenFOAM versions other than those the sources declare** —
  v2412, v2206, v2006, and OpenFOAM 9. The lab's own readings remain `OPENFOAM=2606`.
- The high-lift CRM row's background mesh and refinement levels were **not extracted**;
  its S is computed from its layer block alone and its base cell is unknown.
- **occDrivAer's static/HPC-Challenge case ships no mesher dictionary at all**; the
  row used here is its *rotating-mesh sibling*. The four agreeing numbers linking them
  are an **inference, not a proof** [CITED, `PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`
  F-1a].

---

### 17.9 A DEFECT IN §16's OWN AMENDMENT RECORD, NAMED AND NOT FIXED

**[VERIFIED HERE]** §16 is committed and rule 6 binds it, so this is disclosed rather
than corrected:

- §16's heading declares **`(v1.11, 2026-09-13)`**, but **§15.10 already declares
  `(v1.11)`**. Two sections claim the same version.
- §16's own amendment record at the file's foot reads **"Version 1.6 → 1.7"**, which
  matches neither its heading nor any neighbouring section. It appears to be the
  *draft's* intended bump carried through unedited — the same draft whose title line,
  still present in the committed file, reads **"# DRAFT for
  `docs/standards/MESH_STANDARD.md` — Section 11"** for what was adopted as §16.
- §14.5 already names a related, deliberately unresolved discrepancy: the file header
  at line 3 reads `Version 1.2, dated 2026-08-11` while the highest section version is
  far above it, and §14.5 rules that **the authoritative version is the highest
  section version**. This draft follows that ruling, which is why it is v1.12 and not
  v1.8.

**Recommended disposition: a separate, disclosed housekeeping amendment**, not folded
into this one, and not by this lane. Repairing it inside §17 would make §17 a document
about two unrelated things.

---

### 17.10 Sources

| Artifact | Used for |
|---|---|
| `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md` (committed `799c88e7`) | provenance, hashes and parse checks for all three trees; F-1a; F-2; F-3 |
| `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.*.txt` (365 files) | per-file sha256 of every dictionary cited in §17.1 |
| `wolfdynamics-drivaer/drivaer_{coarse,fine}/system/snappyHexMeshDict` | §17.1 rows 1-2, §17.3, §17.4 |
| `wolfdynamics-drivaer/drivaer_coarse/{README.TXT,run_mesh_shm.sh,run_mesh_fluent.sh,sol_logs/coarse/log.solver}` | §17.2, the two mesh routes and the unattributable result |
| `openfoam-hpc-tc/.../occDrivAerRotMesh.orig/system/snappyHexMeshDict.full:512-516` | §17.1 row 3 |
| `openfoam-hpc-tc/.../marinePropeller/system/snappyHexMeshDict:265-280` | §17.1 row 5, §17.3, §17.7 |
| `openfoam-hpc-tc/.../highLiftCommonResearchModelONERA_LRM-LDG-HV/system/snappyHexMeshDict:2075-2095` | §17.1 row 6, §17.5 |
| `alletto-openfoamtutorials/OneraM6Wing/system/snappyHexMeshDict` | §17.1 row 4 |
| `alletto-openfoamtutorials/membranBCSend/.../log.snappyHexMesh` (×2) | §17.2 **planted control** — proof the sweep can see a snappy log |
| `docs/standards/MESH_STANDARD.md` §16.0, §16.1, §16.2, §16.3, §16.4, §16.6, §14.5, §15.10 | what is quoted, what is superseded, what is named |
| `verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md` A1.2, A1.3, :56-70 | §17.7, §17.4 point 2 |
| the same file, **Amendment 2, committed `b3deca9b3` 2026-09-13T18:23:56Z** | §17.6 — the S = 1.000 -> 0.794 reversal whose stated basis §17.2 half-withdraws |

---

### AMENDMENT RECORD — to be completed BY THE APPENDING COMMIT, measured not asserted

| | |
|---|---|
| section ORDINAL | **17** (derived from the tail: max present = 16, contiguous 1..16) |
| section VERSION | **v1.11 → v1.12** (derived from the tail: max present = v1.11, claimed twice) |
| gates changed | **0** |
| thresholds changed | **0** |
| results re-graded | **0** |
| solver compute | **0 core-min, $0.00** |
| retrieval compute | **~15 core-min**, single core, download + untar + sha256; no pre-registered estimate existed for a retrieval, so **no calibration ratio is claimable** |
| rules superseded | **one numeric reading only** — §16.3's "above 1.0, expect collapse"; §16 rules L1, L3, L4, L5 untouched |
| rules added | **L6** (§17.3), **L7** (§17.7) |
| **lines whose number changed above this section** | **0** — *to be MEASURED by the appending commit:* md5 of this file's first 2,429 lines before the append and after it must be **EQUAL**; at draft time that md5 is `2ee7cf76f8c8c10adfc465885a04df1c` |
| nothing written to `docs/physics_rules.yaml` | correct — §17 binds by being quoted, at §16's maturity |

---

## 18. §16 AND §17 REST ON TWO "MEASURED POINTS" AND **BOTH ARE WRONG** (v1.13, 2026-09-13)

**Lines whose number changed above this section: 0** — measured, not asserted. This
section **corrects the empirical basis of §16.3 and §17**, which are committed and which
rule 6 forbids editing. It changes no gate: §16's rules L1–L5 and §17's L6–L7 stand on
their mechanisms, not on these two numbers.

### 18.1 The claim, as it stands in §16.3 and is repeated in §17.6

> *"two measured points, 0.480 extrudes, 1.6808 collapses"*, and
> *"0.794 is nearer to the only stack this lab has measured EXTRUDING — our own 0.480"*.

**Both halves are false, and both fail in the direction that flatters this lab's
reasoning.**

### 18.2 **"1.6808 collapses" — MEASURED, AND IT DOES NOT COLLAPSE. IT PARTIALLY EXTRUDES.**

| case | achieved | layers |
|---|---|---|
| `r2_medium/log.snappyHexMesh` | **`Extruding 64470 out of 80974 faces (79.618149%)`** | 2.895 of 5 |
| `r2_coarse/log.snappyHexMesh` | **`Extruding 16887 out of 23365 faces (72.27477%)`** | 2.503 of 5 |

**A 1.68-cell stack gives 72–80 % coverage and roughly half the requested layers. That is
partial delivery, not collapse.**

### 18.3 **The zero belongs to a different case AND a different cause**

`F360_coarse/log.snappyHexMesh` reads **`Extruding 0 out of 724711 faces (0%)`** — PPTC,
not DrivAer. **And its stack was not 1.68 cells: its requested thickness was poisoned
95.53× by `getLevel0EdgeLength()` returning a 2 mm axis rod's azimuthal chord** (§16.2).
**Those layers were degenerate, not too thick.** **It is not a data point about stack
thickness at all**, and using it as one conflated two unrelated failures.

### 18.4 **"Our 0.480" is not ours and was never built here**

0.480 is **DrivAerML's 12 mm stack expressed on our 25 mm cell** — a conversion, not a
measurement. **This lab has never built it.** R5's registered 0.474 has never been built
either: the sizing probe ran **`addLayers false` by design**, and the layered build has
not reached the layer phase.

### 18.5 **THE CORRECTED EMPIRICAL BASIS, which is thinner than either section implies**

**This lab has ONE measured stack-versus-coverage point: 1.6808 → 72–80 % coverage.**
There is **no measured extruding point below it**, and **no measured collapse at any
thickness.** **The one-local-cell rule is a DESIGN RULE imported from published practice
and a mechanism, with a single supporting measurement that is a partial success.** §16.9
already forbade calling it a calibrated threshold; **this section states that even its two
anchors were not what they claimed.**

### 18.6 Consequences that do **not** follow, stated so nobody draws them

**PRISM-A2's S = 0.794 is unaffected as a registered value** — it was chosen to sit low in
published practice and further from our only measured point, and **that reasoning survives
intact**; only the word "extruding" attached to 0.480 was wrong. **No gate, threshold, cap
or label moves in any registration.** And **§17.2's finding stands in its narrow form**:
none of the six cases behind the stack table ships a `snappyHexMesh` log — **though six
Alletto membrane test cases elsewhere in the same tree do, so the blanket claim "no
retrieved tree ships a log" is false and must not be repeated.**

### 18.7 How it happened

**Three claims were handed to a lane for inclusion in a Sanaa-facing document. The lane
checked all three instead of writing them, and all three were wrong in the flattering
direction.** They originated with this supervisor, who **conflated PPTC's poisoned-length
zero with DrivAer's partial coverage**, and **carried a converted figure as a measurement
because a registration's own prose called it one.** The standard was written twice tonight
on that basis.

**The rule: a number that has travelled through two documents is not a measurement. Read
the log.**
