# PPTC VP1304 — mesh pipeline record

Measurements from building the meshing path. The frozen gates live in
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` (v1.3, commit `09396b48` plus
amendments 1–3); nothing here alters any of them. No solver has run for this act.

---

## 1. Surface tessellation — which one was used, and why

Two tessellations of the admitted CAD (`case2-1_PPTC_geo_no_gap.stp`, sha256
`d08aaf690b…`), both with OpenCASCADE healing on, healing having been measured
invariant at the root to 0.0150% against a registered 2.0% threshold
(`GEOMETRY_ADMISSION_RECORD.md` §1).

| | curvature 12, min 0.40 mm, max 2.0 mm | curvature 16, min 0.15 mm, max 1.5 mm |
|---|---|---|
| status | **complete, USED** | did not complete in time |
| triangles | 140,114 | — |
| surface area | 163,382.4 mm² | — |
| edge length, blade region | median 0.539 mm, 1st percentile 0.061 mm | — |
| edge length, tip region | median 0.367 mm | — |

**Why the fallback is a measured choice and not a compromise.** Its total surface area
reproduces an independent uniform-0.8 mm tessellation's 163,546.0 mm² to **0.10%**; its
curvature refinement carries facets down to **0.061 mm** at the leading and trailing edges,
which is where SVA's own annotation warns the representation depends on tolerance
(`sva_2011_smp11_pptc_propeller_geometry_annotation.pdf`, which illustrates 0.001, 0.01 and
0.1 mm); and it passes the independent area check of §2 below. **Registered tessellation
tolerance is therefore the curvature-12 / min-0.40 mm setting, disclosed, not the finer one.**

*Honest note on why the finer one did not land:* gmsh's Frontal-Delaunay algorithm fails on
roughly ten of the CAD's thirty-five faces and falls back to `MeshAdapt`, which is serial
inside a single surface. `Mesh.MaxNumThreads2D = 16` and `-nt 16` **were** applied — they took
the run from 6 of 35 surfaces in 11 minutes to all 35 started in 60 seconds — but they
parallelise *across* surfaces, not within one, so a single hard surface still blocks. That is
a gmsh limitation, not an allocation one, and it is recorded as such rather than as a fix.

---

## 2. Patch split — and the classifier that failed first

Five patches are required by pre-registration amendments 2 and 3: `blades`, `hub`, `cap`,
`shaft`, `shaftExtension`.

### 2.1 THE FIRST CLASSIFIER WAS WRONG, AND THE WAY IT WAS WRONG IS THE REASON THE FINAL ONE HAS THREE LIMBS

The hub, cap and shaft are bodies of revolution about x, so their normals carry no
circumferential component. The first classifier used that alone:

    axisymmetric  <=>  |n · e_theta| < 0.15

**It failed. The `hub` patch came back with a maximum radius of 124.990 mm — the blade tip.**
The narrow strips along the blade tip and along the leading and trailing edges face
**radially**, and a radial normal has no circumferential component either, so those blade
faces carry the exact signature the test was built to detect bodies of revolution by. The test
was right about surfaces of revolution and blind to the one family of blade faces that shares
their signature.

A purely positional classifier fails in the opposite place: at the blade **root**, where blade
and hub surfaces occupy the same radii and the same axial band.

> **Neither limb is sufficient. The registered classifier is: axisymmetric normal AND radius
> ≤ 45 mm AND axial position.** The radius bound is safe because every body of revolution here
> is measured: hub 37.60 mm, cap base 36.23 mm, aft fairing 33.25 mm
> (`GEOMETRY_ADMISSION_RECORD.md` §3).

### 2.2 Result

| patch | triangles | area mm² | x range mm | r max mm |
|---|---|---|---|---|
| `blades` | 126,190 | 80,570.7 | −24.60 … +45.56 | 124.990 |
| `hub` | 4,809 | 21,421.5 | −52.28 … +25.72 | 45.121 |
| `cap` | 2,707 | 17,723.1 | +24.62 … +133.69 | 45.270 |
| `shaft` | 6,408 | 43,667.1 | −356.00 … −47.83 | 33.252 |
| `shaftExtension` (generated) | 38,520 | 144,998.9 | −1600.00 … −356.00 | 20.000 |
| CAD body total | | 163,382.4 | | |

The extension is carried **100 mm past the outlet** (to x = −1600 mm, outlet at −1500 mm) so
it cuts that plane cleanly; a surface terminating exactly on a boundary leaves snappyHexMesh
deciding a coincident intersection, which is a silent source of ragged cells.

### 2.3 The split is checked against Report 3752, not against itself

Blade wetted area **80,570.7 mm²** against **2·AE = 76,474.2 mm²**, computed from the
report's own AE/A0 = 0.77896 and D = 250 mm. **Ratio 1.0536.** The check is inside
`make_stl.py` and **fails the run** (exit 2) rather than printing a warning.

### 2.4 ATTRIBUTING THE 5.36% — because that number would look identical if the classifier were over-grabbing

A ratio slightly above 1 is what edge strips and section curvature must give. It is *also*
exactly what a classifier sweeping a few percent of hub or fillet into the blade set would
give. The two are separated by **where the excess sits**: misclassification concentrates at
small radius; geometry does not.

Measured blade area per radial band against the expanded (flat) area 2·c(r)·Δr·Z, with c(r)
and t(r) from the twelve-radius section sweep of `compare_sections.py`:

| r/R | measured mm² | expanded mm² | ratio | t/c | 1+(t/c)² |
|---|---|---|---|---|---|
| 0.340 | 3,007.3 | 2,723.8 | 1.1041 | 0.229 | 1.0523 |
| 0.380 | 3,369.7 | 3,103.8 | 1.0857 | 0.183 | 1.0334 |
| 0.425 | 4,589.3 | 4,358.4 | 1.0530 | 0.146 | 1.0212 |
| 0.475 | 5,074.1 | 4,844.4 | 1.0474 | 0.115 | 1.0132 |
| 0.550 | 11,301.2 | 10,960.0 | 1.0311 | 0.086 | 1.0074 |
| 0.650 | 12,682.9 | 12,355.0 | 1.0265 | 0.063 | 1.0040 |
| 0.750 | 13,326.6 | 13,160.6 | 1.0126 | 0.051 | 1.0026 |
| 0.850 | 13,661.5 | 13,195.6 | 1.0353 | 0.044 | 1.0020 |
| 0.925 | 6,513.6 | 6,220.9 | 1.0470 | 0.040 | 1.0016 |
| 0.965 | 3,435.2 | 3,195.9 | 1.0748 | 0.038 | 1.0014 |
| 0.990 | 1,916.4 | 1,965.9 | **0.9748** | 0.037 | 1.0014 |
| **band sum** | **78,877.7** | **76,084.4** | **1.0367** | | |

**Reading.** The excess is **distributed, not lumped.** It falls from 1.104 inboard to 1.013
at mid-span and rises again at the tip — the inboard rise tracking the measured (t/c)² term
and the tip rise being the tip edge strip, which the expanded-area definition excludes
entirely. The outermost band drops **below** 1 (0.9748), which a misclassification error
cannot produce and interpolation of a steeply falling c(r) near the tip can.

**The bound.** The innermost band's excess over its own curvature prediction is
(1.1041 − 1.0523) × 2,723.8 = **141 mm²**, which is **0.18% of blade area**. Even taking that
entire excess as misclassified hub or fillet — the most pessimistic reading available — it
sits at r ≈ 42.5 mm against the blades' area-weighted radius of roughly 85 mm, so its share of
torque is under **0.09%**, against an 8.10% band half-width. **The classifier is exonerated by
a number, not by a plausible sentence.**

Separately, only **2.10%** of the blade patch (1,693.0 mm²) lies inboard of r = 40 mm, the
region where the expanded-area definition itself stops applying — AE is defined *outside the
boss* (Report 3752 annex A1.1: "Expanded blade area of a screw propeller outside the boss or
hub").

### 2.5 The reverse ambiguity, already bounded

Area assigned to a body-of-revolution patch above the true hub radius of 37.60 mm — blade-root
fillet facets given to `hub` or `cap`:

| threshold | hub | cap | as % of blade area |
|---|---|---|---|
| r > 38 mm | 63.33 mm² | 8.75 mm² | 0.090% |
| r > 40 mm | 38.67 mm² | 8.75 mm² | 0.059% |
| r > 42 mm | 16.97 mm² | 8.75 mm² | 0.032% |

These sit in the KT integration (correct — the comparator retains the hub assembly's thrust)
and outside the KQ integration. At a 40 mm lever arm their torque share is under **0.05%**.

---

## 3. Background sector mesh

`make_blockmesh.py`, family-ratio parameterised so all three levels come from one script.
Domain per §6.1: inlet +3D = +0.750 m, outlet −6D = −1.500 m, outer radius 4D = 1.000 m,
72° passage with cyclic periodics.

**The axis is in the fluid and had to be meshed.** Upstream of the nose-cap tip at
x = +0.1337 m nothing sits on the centreline, so an annular background with a hollow core
would leave an unphysical hole there. The inner radial block is a **pie slice with its inner
edge collapsed onto the axis**. snappyHexMesh removes the axis cells the body occupies —
everything from the shaft extension forward to the cap tip — leaving only far-field cells
ahead of the cap.

**The background is graded because it must be.** The domain is 2.25 m long and 1.0 m in radius
around a 0.25 m propeller; a uniform 25 mm background would be **90 million cells before a
single refinement**.

Coarse level (ratio 1.0): 19,032 background cells; near-field cell at the blade tip
21.4 × 20.0 × 13.1 mm, **aspect 1.64** — near-isotropic, which is what castellation wants.

`checkMesh -allGeometry -allTopology`:

| metric | value | gate | |
|---|---|---|---|
| max non-orthogonality | **1.7075e-06** | < 70° | OK |
| max skewness | **0.32968** | < 4 | OK |
| max aspect ratio | 103.95 | 1000 advisory | OK |
| cells with small determinant | 252 | — | **all on the collapsed axis, disclosed** |

**CORRECTNESS CHECK, not a quality disclosure — keep it separate on the certificate:**

> **Coupled point location match: 1.1445812e-09.** The cyclic periodics pair correctly.
> This is the one thing a 72° sector mesh can get wrong *silently*: a mismatched pair runs,
> converges and returns a confidently wrong KT with no residual signature to warn anyone.

---

## 4. Instruments

`cases/PPTC_VP1304/mesh/make_stl.py`, `make_blockmesh.py`, and
`cases/PPTC_VP1304/tools/{stl_metrics,compare_sections}.py`. The registered import scale of
exactly 1e-3 (mm → m, §2.3) is applied when the OpenFOAM input STL is written, and the scaled
extent is printed and checked: max radius 0.124990 m against R = 0.125 m.

---

## CORRECTION 1 — 2026-09-12, before the family is built. §1's TESSELLATION IS REJECTED, AND I REPORTED IT ADEQUATE USING THE WRONG STATISTIC

*lines whose number changed above this section: 0*

§1 above calls the curvature-12 / min-0.40 / **max-2.0 mm** tessellation "complete, USED" and
"a measured choice and not a compromise", citing "edge length, blade region: median
0.539 mm". **That median is COUNT-WEIGHTED. The AREA-weighted median facet size on the blades
is 2.995 mm** — a factor of 5.6, in the direction that made a badly coarse tessellation look
adequate. §1's verdict is struck. The tessellation is **REJECTED**.

### C1.1 The measurement

`check_tessellation_adequacy.py`, run against that tessellation:

| patch | area-weighted p50 | p90 | p99 | max |
|---|---|---|---|---|
| `blades` | **2.995 mm** | 4.153 | 4.714 | 5.444 |
| `hub` | 3.872 | 4.200 | 4.593 | 4.890 |
| `cap` | 3.977 | 4.016 | 4.350 | 4.621 |
| `shaft` | 4.000 | 4.069 | 4.352 | 4.781 |

Percentage of each patch's **area** carried by facets larger than that level's surface cell:

| level | surface cell | blades | hub | cap | shaft | verdict |
|---|---|---|---|---|---|---|
| coarse | 0.625 mm | 96.3% | 99.9% | 100.0% | 100.0% | **TESSELLATION-LIMITED** |
| medium | 0.417 mm | 98.3% | 99.9% | 100.0% | 100.0% | **TESSELLATION-LIMITED** |
| fine | 0.278 mm | 99.3% | 100.0% | 100.0% | 100.0% | **TESSELLATION-LIMITED** |

**Not marginal at the fine level — inadequate at the coarse one.** The check exits 2.

### C1.2 Why the error happened, and it is the error this act had already registered a prediction about

Curvature-driven refinement puts thousands of tiny facets along the leading and trailing
edges. They are **numerous** and carry **almost no area**. The flat panels in the middle of a
blade are **few** and carry nearly all of it. A count-weighted median therefore reports the
edges and says nothing about the panels — and `MeshSizeMax = 2.0 mm`, which governs those
panels, was never the number being looked at. **MeshSizeMax is the binding constraint;
curvature refinement never governs a flat panel.**

This is precisely `docs/NUMERICS_KNOWLEDGE.md` **N-X5**: *a cell-count share OVERSTATES the
area- or volume-weighted share of any population concentrated in refined regions.* This act
registered seven predictions about that mechanism in
`CONCAVE_CELL_PREDICTION_REGISTRATION.md`, including §4's instruction that *"the AREA share …
is what is reported"* and that *"the cell share is reported too, and explicitly labelled a
locator"* — and then, in the next report, a count-weighted statistic was offered as evidence
of geometric adequacy. **Registering a lesson is not the same as having learned it.**

### C1.3 What survives

The three checks run on that tessellation were real and they still hold:

- total surface area reproduces an independent uniform-0.8 mm tessellation to **0.10%**;
- the AE/A0 split check passes at **1.0536**, with the excess attributed by radial band;
- healing invariance passes all five registered thresholds.

**None of them is sensitive to facet size.** A coarse tessellation of a smooth body gets the
integrated area right while representing that body with panels. Those checks were valid for
what they measured and were then generalised to a property they do not test. The word
"validated" in §1 was doing work it had not earned.

### C1.4 The replacement, and the check that now gates it

A tessellation is running with **`MeshSizeMax` cut from 2.0 mm to 0.30 mm**, min 0.12 mm,
curvature 12, healing on, 16 threads, **binary** output (at this resolution an ASCII STL would
exceed a gigabyte). It is sized by the **finest surface cell the family will achieve**, not by
curvature.

> **REGISTERED, BEFORE THE FAMILY IS BUILT: no level is meshed until
> `check_tessellation_adequacy.py` returns PASS or MARGINAL for it. A level it calls
> TESSELLATION-LIMITED is either not built or is disclosed as limited above a stated surface
> cell size, on the certificate, with the percentage.** Thresholds: PASS ≤ 5% of patch area on
> oversized facets, MARGINAL ≤ 20%, TESSELLATION-LIMITED above that. The check **refuses with
> exit 2**; it does not warn.

### C1.5 Why this mattered more than a quality gate would have

A family whose refinement stops buying geometric fidelity does not fail loudly. Residuals fall,
forces go stationary, `checkMesh` reports a clean mesh, and the Roache triple can even look
CONVERGING — converging on the tessellation's geometry rather than the propeller's. **There is
no residual signature for this failure.** It is caught by measuring the input, before the
solve, or it is not caught.

---

## CORRECTION 1 — ADDENDUM A, 2026-09-12. THE REPLACEMENT TESSELLATION IS PREDICTED TO FAIL THE FINE LEVEL, AND IS KILLED ON THAT PREDICTION RATHER THAN ON ITS RESULT

*lines whose number changed above this section: 0*

Written **while the job is still running**, before its STL exists. The prediction below is
therefore falsifiable against a result nobody has seen.

### A.1 Calibration — turning a gmsh knob into the quantity the gate measures

Two tessellations already on disk are uniform (curvature off), so the size setting is the only
control and the mapping can be measured rather than assumed:

| gmsh setting | blades, area-weighted p50 | p90 | p99 | max |
|---|---|---|---|---|
| 3.0 mm | 2.7895 | 3.2204 | 3.5502 | 3.9082 |
| 0.8 mm | 0.7580 | 0.8667 | 0.9562 | 1.0845 |

**achieved / setting: p50 = 0.930 and 0.947 (mean 0.939); p90 = 1.073 and 1.083 (mean 1.078).**
The ratio is stable across a factor of 3.75 in setting, so it extrapolates. The achieved
distribution clusters *tightly around* the setting — which is exactly why a cap just above a
threshold is the worst place to sit.

### A.2 The prediction

Applying the calibrated shape at each candidate setting, against the derived surface cell
sizes (coarse 0.625 mm, medium 0.417 mm, **fine 0.278 mm**):

| setting | coarse | medium | **fine** | verdict at fine |
|---|---|---|---|---|
| **0.30 mm (the RUNNING job)** | 0.0% | 0.0% | **58.1%** | **TESSELLATION-LIMITED** |
| 0.25 mm | 0.0% | 0.0% | 6.2% | MARGINAL |
| **0.20 mm** | 0.0% | 0.0% | **0.0%** | **PASS** |
| 0.15 mm | 0.0% | 0.0% | 0.0% | PASS |

**The running job cannot deliver the fine level.** Not marginally — 58.1% of blade area would
sit on oversized facets, because a 0.30 mm cap puts the bulk of the distribution at
0.28–0.32 mm, straddling the 0.278 mm threshold. My earlier expectation that 0.30 would
"clear comfortably" was wrong for the same reason the original error was wrong: the
distribution's *shape* matters, not a single representative number.

**And fine is the level that carries the act.** Pre-registration §4.8: *"the act's headline
gate is the design point J = 1.2021 on the FINE level of the family."*

### A.3 Action — killed on the prediction

The job is stopped now rather than in three hours. A run that cannot produce the level the
headline gate sits on has no expected value, and stopping it is not waste.

### A.4 The replacement — resolution follows the geometry, not one global knob

Driving `MeshSizeMax` globally tessellates the hub, cap and shaft at blade resolution for no
benefit: they are **smooth bodies of revolution**, which is precisely what this case's own
patch classifier established about them (§2.1), and a cylinder does not need 0.2 mm panels.
The replacement uses a **radial size field**:

    size(r) = 0.6 - 0.4 * tanh((r - 38) / 2)      [mm, r = sqrt(y^2 + z^2)]

giving ≈1.0 mm on the axis, cap and shaft, ≈0.6 mm at the hub radius, and **0.20 mm on the
blades beyond r ≈ 43 mm**, with curvature refinement still active below it at the leading and
trailing edges (`MeshSizeMin` 0.08 mm). This is the only route that gets **fine to PASS rather
than scrape**, and it *reduces* total facet count and wall time rather than increasing them.

Estimated ≈5.3 M facets on the blades and ≈0.24 M elsewhere; written **binary**.

### A.5 The gate becomes per-level AND per-patch

`check_tessellation_adequacy.py` already reports per patch; the registered verdict is now
taken **per level per patch**, because the blades carry KQ and the graded blade loading while
the hub, cap and shaft carry only thrust and are geometrically trivial. A patch may be
disclosed MARGINAL where a blade may not.
