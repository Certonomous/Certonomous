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

---

## CORRECTION 1 — ADDENDUM B, 2026-09-12. THE GATE IS PER-PATCH, AND THAT KILLED A SECOND TESSELLATION BEFORE ITS RESULT TOO

*lines whose number changed above this section: 0*

Addendum A fixed the blades and left the rest on one number. Making the gate **per-patch**, as
the resolution itself now is, immediately showed that the replacement launched under A would
fail on two other patches.

### B.1 Per-patch surface cells — one source of truth

The surface cell a patch achieves is `background / 2^level`, with the background from
`make_blockmesh.py` and the level from `make_snappy.py`. The gate **imports** those levels
rather than restating them, so it cannot drift away from the dictionary it gates.

| patch | level | coarse | medium | **fine** |
|---|---|---|---|---|
| `blades` | 5 | 0.6250 | 0.4167 | **0.2778 mm** |
| `hub` | 4 | 1.2500 | 0.8333 | **0.5556 mm** |
| `cap` | 4 | 1.2500 | 0.8333 | **0.5556 mm** |
| `shaft` | 3 | 2.5000 | 1.6667 | **1.1111 mm** |
| `shaftExtension` | 2 | 5.0000 | 3.3333 | **2.2222 mm** |

### B.2 The second prediction, and the second kill

The tessellation launched under addendum A used a radial field giving **0.20 mm on the blades
and 1.00 mm inboard**. Against the table above:

| patch | facets it would produce | fine cell | verdict at fine |
|---|---|---|---|
| `blades` | 0.20 mm | 0.2778 | PASS |
| `hub` | 1.00 mm | 0.5556 | **TESSELLATION-LIMITED** |
| `cap` | 1.00 mm | 0.5556 | **TESSELLATION-LIMITED** |
| `shaft` | 1.00 mm | 1.1111 | PASS |
| `shaftExtension` | 3.07 mm | 2.2222 | **TESSELLATION-LIMITED** |

**Killed on the prediction, again, before its STL existed.** Two of the five patches would have
been limited at the level the headline gate sits on.

The `shaftExtension` failure is the worst of the three because **we generate that surface
ourselves.** At `n_ax = 160` its facets are 7.8 × 1.05 mm slivers of equivalent size 3.07 mm
against a 2.22 mm cell — an entirely self-inflicted defect, in a surface where nothing but our
own choice of divisions set the resolution.

### B.3 The fix, chosen by physics and not by tessellation convenience

There were two ways to make `hub` and `cap` pass: coarsen their refinement to level 3, or
tessellate them finer. **Level 4 is kept.** 0.556 mm at the fine level is a reasonable
resolution for a 75 mm hub carrying the blade roots, and choosing a coarser *mesh* to fit a
coarse *tessellation* would be backwards — the tessellation is an input we control, the
resolution requirement is physics.

- radial size field **`size(r) = 0.3 − 0.1·tanh((r − 38)/2)`** → **0.40 mm inboard**,
  **0.20 mm on the blades**, `MeshSizeMax` 0.4, `MeshSizeMin` 0.08 with curvature refinement
  still active at the leading and trailing edges;
- `shaftExtension` axial divisions **160 → 800**, giving 1.55 × 1.05 mm facets of equivalent
  size ≈ 1.37 mm against its 2.22 mm cell. The default is now set **by the gate, not by eye**,
  and the reason is written at the function that owns it.

Estimated ≈4.65 M facets on the blades and ≈1.18 M on the inner bodies.

### B.4 The gate authorises the mesh; the probe only authorised the tessellation

The radial size field was verified on a **probe disc**. A disc is flat: the real blade surfaces
are curved, twisted and thin at the edges, and curvature interacts with a size field in ways a
flat probe cannot show.

> **REGISTERED: the family is authorised by `check_tessellation_adequacy.py` run against the
> PRODUCED STL, per level and per patch — not by the probe, and not by this prediction.** The
> probe justified launching a long job; the gate authorises meshing on its output. Those are
> different decisions and a good prediction must not be allowed to stand in for the second.

---

## CORRECTION 1 — ADDENDUM C, 2026-09-12. "STALLED" WAS THE WRONG WORD, AND THE SPLIT THAT WOULD HAVE FIXED IT IS ALREADY HAPPENING

*lines whose number changed above this section: 0*

### C.1 A mechanism I reported four times and never measured

Addenda A and B, and four reports, describe tessellation runs as **"STALLED"**. That is wrong.

The one uniform run that **completed** — `tq_no_gap`, uniform 0.8 mm, curvature off, 368 s —
carries **7 `MeshAdapt` lines on surfaces 6, 10, 14, 25 and 29**: the *exact same five
surfaces* every "stalled" run sits on. **`MeshAdapt` is not a hang.** It is gmsh's fallback
path when Frontal-Delaunay fails on a surface, and its cost grows steeply with element count.
Those runs were **slow, not stuck**, and a rate was reported as a failure mode.

**The kills themselves remain justified** — every one was ordered by an *adequacy prediction*
showing the tessellation could not deliver a level the headline gate sits on, and those
predictions were independently measured and stand. But two claims were conflated: *"it cannot
deliver"* and *"it is hung"*, and **only the first was ever measured.** Recorded because a
wrong mechanism in the record is worse than no mechanism.

### C.2 Why per-patch tessellation jobs would not help

A proposal to tessellate each patch in its own concurrent gmsh invocation rests on gmsh
parallelising across surfaces and then **blocking on the single hardest one**. Two measurements
answer it.

**(i) It is already happening.** The running log shows surfaces **6, 10, 14, 25 and 29 in
`MeshAdapt` at the same instant**, in one process under `-nt 16`. The wall time is already the
cost of the worst single surface, which is precisely what the split was meant to buy.

**(ii) The input is not decomposed, whatever the output is.** STEP topology, measured:

| entity | count |
|---|---|
| `MANIFOLD_SOLID_BREP` | **1** |
| `ADVANCED_FACE` | 35 |
| `EDGE_CURVE` | **81** |

One solid whose faces share 81 edges. And the patches are **neither distinct solids nor
distinct faces**: they are a **post-tessellation classification of triangles** by normal and
radius (§2.1). There is no `blades` face-set in the STEP to hand to a separate job. A per-face
split into 35 jobs would need all 81 shared edges verified for identical discretisation — and
that verification is the entire risk, for a gain (i) says is already banked.

### C.3 The configuration now running, and what it gives up

Curvature refinement is the measured discriminator across every attempt on this CAD:

| size control | curvature | outcome |
|---|---|---|
| uniform 3.0 mm | OFF | completed 11 s / 41 s |
| uniform 0.8 mm | OFF | **completed 197 s / 368 s** |
| radial field (probe) | OFF | completed ~3 min, 5.2 M facets |
| curvature 12, 0.4–2.0 mm | ON | completed, ~27 min |
| curvature 16, 0.15–1.5 | ON | killed |
| curvature 12, 0.12–0.30 | ON | killed |
| field + curvature 12 | ON | killed (twice) |

**3 of 3 curvature-off runs completed; 4 of 5 curvature-on runs were killed.** The production
run therefore uses the radial field with **curvature OFF** — 0.40 mm inboard, 0.20 mm on the
blades — which satisfies **every patch at every level** of the per-patch gate.

**WHAT IS GIVEN UP, DISCLOSED:** the leading and trailing edges no longer receive sub-0.2 mm
facets. The adequacy gate is still satisfied, because that gate compares facet size against
*surface cell* size. But SVA's own annotation
(`sva_2011_smp11_pptc_propeller_geometry_annotation.pdf`) warns that leading- and trailing-edge
representation depends on the tessellation tolerance, and a 0.20 mm facet on a leading edge of
order 0.3 mm radius resolves that curve with a handful of facets.

Pre-registration §6.3 requires the LE radius resolved by **at least 8 cells across in the
MESH**, which snappyHexMesh reaches through **feature-edge refinement** from
`surfaceFeatureExtract`, not through facet size. That requirement is therefore not lost — but
it now rests on the extracted feature edge rather than on the surface tessellation.

> **REGISTERED: the leading- and trailing-edge facet count on the PRODUCED STL is MEASURED and
> recorded before the family is built, not asserted.** If the extracted feature edges do not
> reproduce the LE to the resolution §6.3 requires, that is disclosed on the certificate with
> the number.

---

## CORRECTION 1 — ADDENDUM D, 2026-09-12. THE LEADING EDGE IS NOT A CAD FEATURE EDGE, SO NO TESSELLATION CAN MAKE `surfaceFeatureExtract` FIND IT — AND §6.3's LE REQUIREMENT IS NOT MET BY THE REGISTERED FAMILY

*lines whose number changed above this section: 0*

Addendum C argued that turning curvature off was safe for §6.3 because the LE resolution
requirement "rests on the extracted feature edge rather than on the surface tessellation".
**That argument is wrong, and it is wrong for a reason no tessellation setting can fix.**

### D.1 The CAD's own curve topology, meshed independently of any surface

`gmsh -1` on the admitted STEP at 0.02–0.05 mm — curves only, 2.7 s, and completely independent
of the surface tessellation — gives the CAD's true edges:

- **81 curve entities, 4075.07 mm total edge length.**
- **15 curves lie in the blade region** (mean radius > 45 mm), 848.68 mm total, in three
  families: **5 × 114.465 mm** spanning r = 36.91 → 124.99 (root to tip, one per blade), and
  **5 × 27.875 mm** plus **5 × 27.397 mm**, both at r = 124.99 (the tip edges).

**A blade section has two ends. Only ONE root-to-tip curve exists per blade.** The smp'11
geometry sheet says *"The trailing edge for the upper propeller radii is sharp"* — so the
114.465 mm curve is the **trailing** edge, a genuine sharp seam, and **the leading edge is a
smooth rounded region of the surface with no CAD edge at all.**

### D.2 The consequence

> **`surfaceFeatureExtract` cannot extract the leading edge, on any tessellation, at any
> `includedAngle`.** It finds edges by angular discontinuity between adjacent facets, and on a
> smooth rounded LE there is no discontinuity to find — not because the tessellation is too
> coarse, but because the geometry is smooth there. It will extract the trailing edge and the
> tip edges, which are real CAD seams.

So §6.3's requirement — *"leading-edge radius resolved by at least 8 cells across"* — **must be
met by SURFACE refinement, not feature-edge refinement**, and addendum C's fallback does not
exist.

### D.3 The LE radius, measured

Circle fitted to the section within 0.6 mm of the chord end, on the curvature-driven
tessellation (the only one on disk carrying 0.06 mm facets at the edges):

| station | chord | LE fit |
|---|---|---|
| r/R = 0.5 | 62.307 mm | **radius 0.2424 mm**, 77 points, fit residual 0.0338 mm |
| r/R = 0.7 | 81.366 mm | inconclusive — 6–7 points within 0.6 mm at both ends |
| r/R = 0.9 | 112.924 mm | inconclusive — 7–8 points at both ends |

**Stated limitation: this is ONE station with a good fit and two inconclusive ones**, the
outboard sections having too few facets within the fit window because the curvature-driven
refinement does not distribute uniformly along the span. The r/R = 0.5 value is a measurement;
the span-wise variation is not yet characterised, and the other end at r/R = 0.5 returning only
6 points inside 0.6 mm is itself consistent with the sharp trailing edge the geometry sheet
describes.

### D.4 What §6.3 then demands, against what the family delivers

Taking the measured LE radius of 0.2424 mm:

| reading of "8 cells across" | required cell | fine level's blade cell | shortfall |
|---|---|---|---|
| across the radius | 0.030 mm | 0.278 mm | **9.3×** |
| across the LE (diameter) | 0.061 mm | 0.278 mm | **4.6×** |

> **THE REGISTERED FAMILY DOES NOT MEET §6.3's LEADING-EDGE RESOLUTION AT ANY OF ITS THREE
> LEVELS, ON EITHER READING.** This is a property of the registered cell targets
> (0.8 M / 2.7 M / 9 M per passage), not of the tessellation, and no tessellation setting
> changes it.

### D.5 Status — raised, not decided

Two routes exist and both change something registered, so this lane does not pick one:

1. **A local LE refinement region** — a thin band along the LE path at a much higher level
   (8.9 mm background ÷ 2⁸ = 0.035 mm) reaches the requirement locally and affordably, because
   the band is thin. **But the STL must then carry ~0.035 mm facets at the LE**, which requires
   curvature-driven tessellation — the configuration measured to be far slower here — and it
   adds a refinement region not named in §6.3.
2. **Disclose the limitation** — the act reports that the LE is resolved to 0.278 mm against a
   requirement of 0.030–0.061 mm, with these numbers, on the certificate.

**Raised to the cfd supervisor. No mesh is built on either route until it is settled**, because
the choice changes the cell count, the tessellation configuration and possibly the registered
cell targets.

---

## CORRECTION 1 — ADDENDUM E, 2026-09-13. ADDENDUM D's SHORTFALL FACTORS ARE WITHDRAWN. THE STRUCTURAL FINDING STANDS; THE RADIUS DOES NOT

*lines whose number changed above this section: 0*

### E.1 What is withdrawn

Addendum D reported the registered family as short of §6.3's LE resolution by **9.3× or 4.6×**,
from a measured LE radius of 0.2424 mm at r/R = 0.5. **Those factors are withdrawn.** The
radius they rest on is not established.

An attempt to characterise the span by widening the radial shell from ±0.25 to ±1.0 mm and
fitting both chord ends at eight stations:

| r/R | section points | end A | end B |
|---|---|---|---|
| 0.30 | 5473 | no fit (6 pts) | no fit (6 pts) |
| 0.40 | 558 | 0.2420 mm, 253 pts, **residual 0.0975** | no fit (6 pts) |
| 0.50 | 625 | no fit (6 pts) | no fit (8 pts) |
| 0.60 | 1159 | no fit (6 pts) | no fit (7 pts) |
| 0.70 | 1474 | no fit (6 pts) | no fit (5 pts) |
| 0.80 | 2182 | no fit (6 pts) | no fit (6 pts) |
| 0.90 | 6114 | no fit (6 pts) | no fit (6 pts) |
| 0.95 | 1556 | 0.1724 mm, 193 pts, **residual 0.0787** | no fit (12 pts) |

**Six of eight stations refuse to fit at both ends**, even with thousands of section points. The
two that fit carry residuals of **40% and 46% of the fitted radius**. And the diagnosis applies
backwards: addendum D's r/R = 0.5 fit had a 0.0338 mm residual on a 0.2424 mm radius — **14%** —
reported as a measurement when it should have been reported as weak. The chord-extremum search
is separately unreliable: widening the shell moved the r/R = 0.5 chord from 62.307 to 67.88 mm,
so the "ends" it locates are not stably the LE and the TE.

### E.2 Why that data could never have given the number — the real reason

gmsh's curvature-driven sizing sets element size **h = 2πR_curv / N**. On `tc_no_gap`, N = 12
with a **floor of 0.40 mm**, so LE facets sit on the floor and the data yields only a **bound**:

    R_curv  <=  N h / (2 pi)  =  12 x 0.40 / (2 pi)  =  0.764 mm

The floor, not the LE, set the facet size there. That is why six stations had exactly 5–8 points
inside the fit window: **there was no local refinement at the LE to fit to.** The instrument was
reading its own clamp.

### E.3 What still stands, and it needs no radius

**The structural finding of addendum D is untouched** and depends on no fitted quantity: the CAD
carries **one** root-to-tip curve per blade, the smp'11 sheet says the trailing edge is sharp,
therefore **the leading edge has no CAD edge**, and `surfaceFeatureExtract` cannot extract it on
any tessellation at any `includedAngle`.

> **REGISTERED, and to be stated in the snappy dictionary so no reader infers otherwise: LE
> resolution in this family comes from SURFACE REFINEMENT LEVEL ALONE. There is no
> feature-edge contribution at the leading edge, and there cannot be.**

What is **not** established is whether, or by how much, the family falls short of §6.3.

### E.4 The instrument that can settle it

Not a finer circle fit — the tessellation itself. With the curvature floor dropped to 0.02 mm,
**facet size becomes a direct readout of local curvature**, R = N·h/(2π), along the whole span,
with no fitting at all. That run is queued behind `prod6` rather than launched beside it, so two
heavy meshers do not contend.

### E.5 Which reading of §6.3 governs — raised, not assumed

Sanaa's byte-exact wording: *"leading-edge radius resolved by at least 8 cells across, tip
resolved by at least 6 cells across the tip chord"*.

The **parallel clause names its extent explicitly** — "across the tip **chord**". The LE clause
does not, so "across" takes the noun it modifies, **"the leading-edge radius"**: 8 cells across
the *radius*, cell ≤ R/8. The conventional reading for a rounded nose is across the *diameter*,
cell ≤ R/4 — a **factor of two**, and probably what was meant.

**The literal parse is registered as governing and the conventional one disclosed beside it**,
because adopting the gentler reading merely because it is gentler is the error this record
exists to prevent. Raised to the cfd supervisor to rule.

### E.6 Consequence for the accepted route

Route 2 — build as registered, disclose the limitation — is accepted. **It is blocked on the
same measurement the withdrawn claim was**: no certificate will carry "not achieved by a factor
of N" while N is unestablished.

---

## CORRECTION 1 — ADDENDUM F, 2026-09-13. THE LE RADIUS IS ~1.4–1.8 mm, NOT 0.24 mm, AND §6.3's SHORTFALL IS UNDER 1.6× WHERE IT WAS MEASURED AT ALL

*lines whose number changed above this section: 0*

### F.1 The instrument, and the guard that makes it trustworthy

`measure_le_radius.py`. gmsh's curvature sizing gives **h = 2πR_curv/N**, so on a
curvature-bound facet the size is a **direct readout**: R = N·h/(2π). No circle fit, no
chord-extremum search — the two things that failed in addendum E.

**The guard:** every facet is classified **CURVATURE-bound / FLOOR-bound / MAX-bound**, and a
station where the clamp binds on more than 20 % of its LE facets is **REFUSED, not averaged**.
A facet sized by a clamp reports the clamp as a confident number, which is worse than an honest
bound.

**Leading edge separated from trailing by PROVENANCE, not curvature.** Both are high-curvature
bands and the TE is the sharper. Facets within 1.5 mm of a CAD curve are TE or tip *by
construction* (addendum D: the TE is one of the five 114.465 mm root-to-tip curves; **the LE has
none**). The CAD curves come from `gmsh -1`, independent of any surface.

### F.2 Validated by refusing on the case that caused the error

Run against the very tessellation that produced the withdrawn claim (N = 12, floor 0.40 mm):
blade facets **42.2 % curvature-bound, 48.6 % FLOOR-bound, 9.2 % max-bound**. It **REFUSED at
r/R 0.70, 0.80, 0.90 and 0.95** — 100 % clamp-bound at three — which are *exactly* the stations
the circle fits failed at. **The guard names the cause where the fit merely failed.**

### F.3 The three accepted stations, and why they are believable

| r/R | R_LE (mm) | section t (mm) | R/t |
|---|---|---|---|
| 0.40 | **1.8233** | 10.79 | 0.169 |
| 0.50 | **1.7322** | 8.30 | 0.209 |
| 0.60 | **1.4380** | 6.77 | 0.212 |

**R/t = 0.197 ± 0.020 across three independent stations.** A consistent ratio is what a real
section family produces; it is not what an artefact produces. The thickness values come from a
separate instrument (`compare_sections.py`) on a separate tessellation, so the ratio is not
self-referential.

**Addendum D's 0.2424 mm was not a weak measurement of the LE — it was a measurement of
something else**, most probably the sharp TE or a facet-scale artefact, and the chord-extremum
search could not distinguish them because it never stably located the LE.

### F.4 §6.3 re-assessed — and the parse ruling now carries the whole result

At the fine level's 0.278 mm blade surface cell:

| r/R | R_LE | literal, cell ≤ R/8 | conventional, cell ≤ R/4 |
|---|---|---|---|
| 0.40 | 1.8233 | need 0.2279 → **short 1.22×** | need 0.4558 → **PASSES** |
| 0.50 | 1.7322 | need 0.2165 → **short 1.28×** | need 0.4330 → **PASSES** |
| 0.60 | 1.4380 | need 0.1797 → **short 1.55×** | need 0.3595 → **PASSES** |

**The withdrawn 9.3× was wrong by nearly an order of magnitude.** On the **literal parse ruled
to govern** (addendum E.5) the shortfall is under **1.6×** where measured; on the conventional
parse there is **no shortfall at all**. The parse ruling — made *before* these numbers existed —
is now the entire difference between a disclosed limitation and none.

### F.5 What is still NOT established

**r/R = 0.70 is REFUSED, and 0.70 is the radius the act is referenced to.** The outboard
stations being 100 % floor-bound at a 0.40 mm floor establishes only **R < 0.764 mm** there —
and that bound is **inconsistent** with extrapolating R/t = 0.197, which would predict ≈0.9 mm
at r/R = 0.9. Either the outboard LE sharpens faster than the ratio implies, or something else
binds. **The three-station ratio is not extrapolated across the refusals.**

A measurement run is in progress with the floor dropped **0.40 → 0.05 mm**, resolving radii down
to 0.0955 mm, ceiling 1.0 mm to bound the work.

> **Route 2's disclosure still waits on r/R = 0.70 and outboard. No certificate carries a
> shortfall factor from three inboard stations while the reference radius is refused.**

---

## CORRECTION 1 — ADDENDUM G, 2026-09-13. THE INSTRUMENT'S DESIGNER IS NOT EXEMPT FROM THE INSTRUMENT'S FINDING

*lines whose number changed above this section: 0*

### G.1 What happened

`measure_le_radius.py` exists because a **clamp** was reported as a measurement: leading-edge
facets sat on a 0.40 mm floor, so the data could only yield `R ≤ 0.764 mm`, and circles were
being fitted to points whose spacing was set by that floor (addendum E.2).

**One report later, the measurement run launched to fix it carried the same defect at the other
end.** The readout `R = N·h/(2π)` inherits **both** clamps. At N = 12 a **ceiling of 1.0 mm**
cannot report any radius above **1.910 mm** — and the best station already in hand, r/R = 0.40
at R = 1.8233 mm, needs **h = 0.9547 mm**, which the instrument's own 5 % rule calls
**MAX-BOUND** at h ≥ 0.95.

> **The run in flight would have REFUSED r/R = 0.40 and everything inboard of it — where thicker
> sections give larger radii still — and would have measured LESS than the run it was built to
> improve on.** The ceiling doing at the top precisely what the floor did at the bottom, in an
> instrument built specifically to detect that class of error, by the person who had just
> found it.

Caught on the cfd supervisor's warning, with the job about a minute from the stations it would
have erased.

### G.2 The fix, and which half of it matters

**Raising the ceiling fixed today's run. The preflight fixes the class.**

- **Resolvable window, printed before a single facet is read:** `R ∈ [N·floor/2π, N·ceiling/2π]`.
  For the relaunch (floor 0.05, ceiling 3.0) that is **R ∈ [0.0955, 5.7296] mm**. Nobody starts
  a long job whose answer is bounded out of range by its own settings.
- **Edge warnings on ACCEPTED stations** — p90 within 20 % of the ceiling, or p10 within 25 %
  of the floor. This closes the variant the binary guard misses: **a station inside the window
  but hugging its edge is quietly half-clamped and reports a number anyway.** An in-or-out test
  would have passed r/R = 0.40 at 0.9547 against 1.0 and said nothing.
- Re-run against the old data, the preflight prints `R ∈ [0.7639, 3.8197] mm` — which is by
  itself the explanation of why that tessellation could never have measured the outboard LE.

**And the constraint that was supposed to bound the work was buying nothing while costing the
measurement:** a *higher* ceiling is *cheaper*, because it lets flat regions stay coarse.

### G.3 The generalisation

> **An instrument that reads a physical quantity through a numerical control inherits every
> clamp on that control, at both ends, and a clamped reading is returned as a confident number
> rather than as a refusal.** State the resolvable window before the run; classify every sample
> by which constraint bound it; refuse the clamped ones; and warn on the ones merely crowding a
> limit. Applies to any measurement derived from a mesh-size parameter, not to this case.

---

## CORRECTION 1 — ADDENDUM H, 2026-09-13. THREE DEFECTS FOUND BY BUILDING THE MESH INSTEAD OF REASONING ABOUT IT, AND ONE CLAIM OF THIS RECORD IS STRUCK AS FALSE

*lines whose number changed above this section: 0*

Every addendum from A to G was written from measurement of an *input*. None of them built a
mesh. The first attempt to actually run `snappyHexMesh` found three defects in under twenty
minutes, one of them in this record's own prose. **No solver had run in this act; no gate,
threshold, cap or label is altered by anything below.**

### H.1 §3's CLAIM THAT THE CENTRELINE CELLS ARE "REFINED BY NOTHING" IS FALSE, AND IT IS STRUCK

§3 above says of the collapsed-axis prism cells: *"Those cells sit in the far field ahead of
the cap and are refined by nothing."* **That sentence is struck.**

`bladeRegion` and `tipVortex` are `searchableCylinder`s **about the axis** — radius 132.5 mm
and 130.0 mm, centred on the centreline — so they contain the axis cells **by construction**.
Independently, the buffer of `nCellsBetweenLevels 3` down from the shaft surface at
r = 20 mm reaches the centreline whatever the regions do. The claim was never measured; it
was asserted about a mesh nobody had refined.

### H.2 THE COLLAPSED AXIS ABORTS snappyHexMesh, AND IT ABORTS LOUDLY

`snappyHexMesh` refines through `hexRef8`, which requires **eight points per cell**. A
collapsed pie slice is a **prism**:

    cell 192 of level 0 does not seem to have 8 points of equal or lower level
    cellPoints:6(315 316 324 210 211 219)
    pointLevels:6{0}
        From Foam::hexRef8::setRefinement  ...  hexRef8.C at line 3787
    FOAM parallel run aborting  ->  MPI_ABORT on every rank

732 of the background's 19,032 cells were prisms — 12 circumferential × 61 axial × 1 radial.

**THE FIX: the axis becomes a slip cylinder of radius R_AXIS = 2 mm, patch `axisRod`.** The
background is then 100 % hexahedral. The patch is emitted as type `patch`, **not `wall`**,
so it does not enter `wallDist`/`meshWave` and the k-omega SST wall treatment never measures
a distance to a 2 mm numerical rod as though it were a body.

**WHAT IT COSTS, AS NUMBERS:**

| | |
|---|---|
| rod diameter | **4 mm = 1.6 % of D** |
| blockage of the propeller disc | **0.026 %** |
| where it exists at all | **only ahead of x ≈ +127 mm** — inboard of that the rod lies inside the cap, hub, shaft and extension, and snappyHexMesh deletes those cells |
| boundary condition | `slip` — zero shear, no penetration |
| in the graded integrations | **in NEITHER** (amendment 2's thrust or torque patch lists) |

In an aligned uniform stream a slip cylinder **is a stream surface**, so the ideal-flow
disturbance is *identically* zero and the real disturbance vanishes as R_AXIS → 0. This is a
**mesh implementation** change, recorded here in the section that owns the original
collapsed-axis decision, and disclosed on the certificate.

### H.3 THE END-CAP REMOVAL GUARD FIRED, AND WHAT IT CAUGHT WAS ITS OWN SELECTOR

`make_stl.py` removes the disc capping the CAD's aft termination and **verifies the discarded
area against π r²**. On the production-resolution tessellation it **REFUSED**:

> `*** ABORT: the facets removed at the CAD aft termination total 1323.32 mm2 but the shaft
> end disc should be 1256.64 mm2.`

**Cause:** the selector was **purely positional** — a 0.5 mm axial window. Once the shaft's
side-wall facets shrank to ≈0.95 mm, a **0.53 mm band of side wall** fell inside that window.
2πr × 0.53 mm = 66.6 mm², which is exactly the 66.7 mm² excess.

**Fix: position AND normal.** The disc's normal is axial, the side wall's is radial, and
`|n·x̂| > 0.9` separates them at **any** tessellation. Result: **3,292 facets, 1256.18 mm²
against 1256.64, −0.04 %.**

> **THIS IS THE L-221/L-222 SHAPE.** §2.1 of this record already established, for the patch
> classifier, that *position alone misclassifies and the normal is the discriminator* — and
> then a selector fifty lines further down used position alone. **A lesson written in one
> section and not applied in the next is not a lesson that has been learned.** §2.1's own
> words were "Neither limb is sufficient."

### H.4 OpenFOAM's `etc/bashrc` EXECUTES THE CALLING SCRIPT'S FIRST ARGUMENT

`openfoam2606/etc/bashrc:204` forwards `"$@"` to `etc/config.sh/setup`, which loops over
those arguments. **Sourced from a script, `"$@"` is the calling script's own arguments.**
`build_level.sh` is called with the STL path first, so bash **sourced and executed the STL** —
140,114 facets' worth of `vertex: command not found`.

**Which argument shapes actually fire** — measured with a planted `export PLANTED_EXEC=YES`,
by the cfd supervisor rather than assumed by this lane, and it **narrows** the first reading
recorded here:

| argv[1] | fires? | |
|---|---|---|
| a **readable file** | **YES** | sourced and executed — arbitrary code execution |
| **`name=value`** | **YES** | silently eval-exported into the solver's environment, no log line |
| a **directory** | no | `[ -f "$x" ]` is false; falls through |
| a plain number | no | |

So a solver launcher passing a case **directory** first is on the safe shape; a **file path**
or a `name=value` token is not. Guard: **`set --` before sourcing**, the named variables
having been captured first. Proven both ways: without it `FOAM_SETTINGS=[/tmp/somefile.stl]`,
with it `FOAM_SETTINGS=[]`. Applied to `build_level.sh`, `launch_pptc.sh` and
`dead_lever_audit.sh`. The exposure beyond this act is the cfd supervisor's to report.

### H.5 THE TESSELLATION ACTUALLY IN USE FOR THE COARSE LEVEL

`c1.stl` — radial field `size(r) = 0.75 − 0.20·tanh((r−38)/2)`, curvature OFF, 0.55 mm on the
blades and 0.95 mm inboard. **rc = 0, 525 s wall, 941,004 triangles.** Adequacy gate, per
patch, at the coarse level:

| patch | area oversized | verdict |
|---|---|---|
| `blades` | **5.2 %** | **MARGINAL** |
| `hub` | 0.0 % | PASS |
| `cap` | 0.0 % | PASS |
| `shaft` | 0.0 % | PASS |

**5.2 % is MARGINAL and is recorded as MARGINAL.** It is not rounded to the 5.0 % PASS line,
and no later reader may read it as PASS. **`c1` CANNOT serve medium or fine** — 97.2 % and
99.7 % of blade area oversized — and is **not offered for them**. The fine-capable production
tessellation (`prod7`, the registered 0.20/0.40 radial field) and the medium-capable `cm1`
were still running when this was written.

---

## CORRECTION 1 — ADDENDUM I, 2026-09-13. THE LEADING-EDGE RADIUS FALLS FROM 1.91 mm TO 0.06 mm ACROSS THE SPAN AND HAS NOT CONVERGED; §6.3's 8-CELL CLAUSE HAS NO ESTABLISHED SATISFYING CELL SIZE, AND THE ONE IT WOULD NEED AT r/R 0.90 IS NOT BUILDABLE ON THIS BOX

*lines whose number changed above this section: 0*

**No gate, threshold, cap or label is altered by anything below.** No solver has run in this
act. Addendum F's three-station figure of R_LE ≈ 1.44–1.82 mm is **withdrawn**, for a reason
that also applies to the first form of this addendum's own instrument.

### I.1 UNITS, ASSERTED BEFORE ANY DIMENSIONAL SELECTOR

`prod7.stl`, maximum radius about x = **124.990477** in file units. Against the known VP1304
diameter D = 0.250 m (Report 3752 Table 1):

| reading | implied D | ratio to known |
|---|---|---|
| **millimetres** | **0.249981 m** | **0.999924** |
| centimetres | 2.499810 m | 9.999238 |
| metres | 249.980953 m | 999.923812 |
| inches | 6.349516 m | 25.398065 |

**The file is in MILLIMETRES**, to 76 ppm. Every selector below is mm. The instrument
**refuses to run** unless millimetres is the reading that agrees — this lab has already applied
a metres selector to a millimetre STL and selected **1 facet out of 7,230,286**.

### I.2 THE INSTRUMENT, AND THE TWO FORMS OF IT THAT WERE WRONG FIRST

`cases/PPTC_VP1304/mesh/measure_le_curvature.py`. A **discrete curvature** read off the
tessellation itself: R_LE = 1/κ_max. It replaces `measure_le_radius.py` because that
instrument reads R = N·h/(2π) off gmsh's **curvature-driven** sizing, and **every production
tessellation on disk — `prod7`, `cm1`, `c1` — sets `Mesh.MeshSizeFromCurvature = 0`**. Applied
to `prod7` it would report the radial MathEval background field as a radius.

Two forms were built and both were killed by their own controls, which is the point of having
them:

1. **Facet normals, κ = angle(n₁,n₂)/|c₁−c₂| across a shared edge.** Recovered **0.6639 mm for
   a cylinder of radius 1.000 mm** — not scattered, *tight*, and biased by exactly **3/2** in
   curvature. A flat facet's normal belongs at the MIDPOINT OF THE ARC IT SPANS, not at its
   centroid; on a structured quad-split cylinder the centroids sit 2/3 of an arc apart while
   the normals sit a full arc apart. The error depends on the **triangulation pattern**, which
   is why it read 2 mm and above correctly and everything below it wrongly.
2. **Vertex normals, κ = max over incident edges.** Removed the 3/2 bias and still read
   **1.1501 mm for 1.000 mm, +15.0 %** — an edge leaving a vertex at angle α from the direction
   of maximum curvature sees only κ·cos α, so a max over the six directions a triangulation
   happens to offer is a maximum over a **sample**. Biased LOW in curvature, i.e. **HIGH in
   radius — the flattering direction.**

**The form that stands** fits the **shape operator** by least squares over every incident edge
at each vertex (2 × valence equations, three unknowns), takes the principal curvatures as its
eigenvalues, and gives a facet the median of its three vertices.

### I.3 THREE CONTROLS, TWO OF WHICH COULD HAVE FAILED AND ARE REPORTED EITHER WAY

**(a) IN-FILE CONTROL — the shaft.** A cylinder of registered radius **20.000 mm**
(`make_stl.py:R_SHAFT`, measured in `GEOMETRY_ADMISSION_RECORD.md` §3), read from the SAME
file through the SAME reader and the SAME classifier as the blade: **398,380 wall facets,
R recovered 20.0001 mm, error 0.00 %.** A reader that cannot see a known radius in the file it
is grading is not evidence about an unknown one.

**(b) SYNTHETIC LADDERS — and the second one governs.** Cylinders at the blade facet size
h = 0.19 mm are recovered to ≤ 1.2 % from R = 0.125 to 8 mm. **But a cylinder is not a leading
edge.** A nose is a semicylinder of radius R closing a nearly flat slab, and the vertex normals
at the apex average the flank in. The **nose ladder**:

| R true | R/h | R recovered | error |
|---|---|---|---|
| 0.125 | 0.66 | 0.1573 | **+25.9 %** OUTSIDE WINDOW |
| 0.250 | 1.32 | 0.2717 | +8.7 % MARGINAL |
| 0.500 | 2.63 | 0.5040 | +0.8 % OK |
| 1.000 | 5.26 | 1.0000 | 0.0 % OK |
| 2.000 | 10.53 | 2.0000 | 0.0 % OK |

> **The resolvable window is MEASURED, not asserted: R/h ≥ 2.6 for ≤ 1 %, R/h ≥ 1.3 for
> ≤ 10 %, and the error is always in the BLUNT direction.** A station below R/h = 1.5 is
> **REFUSED**; between 1.5 and 3.0 it is reported with the facet count across the nose stated
> on its face. **Every marginal reading in §I.5 is therefore an UPPER BOUND on R_LE.**

**(c) PUBLISHED-GEOMETRY CONTROL — the section extraction, against SVA's own table.** Three
independent published quantities, reproduced by the same section machinery that locates the
edge:

| quantity | SVA `sva_2011_smp11_case2_pptc_geometry_table` | measured | error |
|---|---|---|---|
| C0.70 | 104.1670 mm | 104.258 mm | **+0.09 %** |
| C0.75 | 106.3476 mm | 106.754 mm | **+0.38 %** |
| t0.75 | 3.7916 mm | 3.817 mm | **+0.67 %** |

### I.4 THE LEADING EDGE IS LOCATED BY SECTION GEOMETRY — AND A PERCENTILE SELECTOR IS WHY ADDENDUM F WAS WRONG

The first form of this instrument took the **top decile of curvature** in a radial band as "the
leading edge". It reported **R_LE = 24.4 mm at r/R = 0.50 on a section 8.2 mm thick** — an
impossible answer, **tight to 1.0 % across five blades.** The nose carries a few hundred facets
out of ~21,000 in the band, so a decile is ~90 % ordinary surface and its MEDIAN is the
surface. **Five blades agreeing is not correctness: all five were diluted identically.**

> **ADDENDUM F's INSTRUMENT CARRIES THE SAME DEFECT.** `measure_le_radius.py:~150` selects the
> leading edge as `thr = np.percentile(h[idx], 10); le = idx[h[idx] <= thr]` — the smallest
> DECILE of facets in the band. Same dilution, same direction: non-nose facets are larger, so
> R = N·h/(2π) comes out **blunter**. F's 1.8233 / 1.7322 / 1.4380 mm at r/R 0.40 / 0.50 / 0.60
> are **1.7× / 2.4× / 4.2×** the values measured here. **F's R/t = 0.197 ± 0.020 "consistent
> across three independent stations" was the consistency of a shared defect**, which is exactly
> the argument F used to call the numbers believable. Those three figures are **withdrawn**.

The form that stands extracts the **section** — a ±0.25 mm radial shell, one blade, unrolled to
(r·Δθ, x) — takes the chord as its principal axis, measures **both** ends, and identifies the
leading edge by **CAD provenance** (the trailing edge IS a CAD curve; the leading edge has none
— addendum D), with the **point of maximum thickness** reported beside it as an independent
check. **Addendum D's structural finding is CONFIRMED, not assumed:** at every station where
the thickness test decides, it names the same end as the CAD test. Where they disagree
(r/R 0.30, in the hub-gap region) the station is **REFUSED**, and where the thickness profile
ties at x_t = 0.50 the tie is printed as `undecided` rather than silently broken — an earlier
form broke it silently, picked the TRAILING edge on two blades of five at r/R 0.80 and 0.90,
and averaged the two edges into one number.

### I.5 THE MEASURED SPAN DISTRIBUTION — `prod7`, five blades per station

| r/R | chord mm | R_LE mm | sd over 5 blades | facets across nose | cell for R/8 |
|---|---|---|---|---|---|
| 0.30 | — | **REFUSED** — CAD and thickness name different ends | | | |
| 0.35 | 56.639 | **1.9068** | 0.0032 | 27.7 | 0.2384 |
| 0.40 | 65.705 | **1.0728** | 0.0191 | 14.8 | 0.1341 |
| 0.45 | 73.917 | **0.9366** | 0.0328 | 13.9 | 0.1171 |
| 0.50 | 81.328 | **0.7162** | 0.0411 | 10.4 | 0.0895 |
| 0.55 | 88.014 | **0.4733** | 0.0377 | 9.1 | 0.0592 |
| 0.60 | 94.148 | **0.3408** | 0.0244 | 9.0 | 0.0426 |
| 0.65 | 99.758 | **0.2542** | 0.0053 | 10.6 | 0.0318 |
| **0.70** | **104.258** | **0.1938** | **0.0168** | **8.4** | **0.0242** |
| 0.75 | 106.754 | **0.1446** | 0.0060 | 6.8 | 0.0181 |
| 0.80 | 107.333 | **0.1062** | 0.0090 | 9.1 | 0.0133 |
| 0.85 | 106.929 | **0.0836** | 0.0031 | 5.7 | 0.0104 |
| 0.90 | 104.632 | **0.0562** | 0.0064 | 5.3 | 0.0070 |
| 0.95 | 94.931 | **0.0723** | 0.0034 | 5.9 | 0.0090 |
| 0.98 | 75.585 | **REFUSED** — R/h = 0.83, below the measured window | | | |

**The leading edge is not one radius. It falls by a factor of 34 across the span**, from
1.91 mm at r/R 0.35 to 0.056 mm at r/R 0.90 — consistent with a propeller SVA states "was
designed to generate a tip vortex". Artifact: `certonomous-runs/PPTC_VP1304/le_band/LE_SPAN_prod7.txt`.

### I.6 AND IT HAS NOT CONVERGED — THE TESSELLATION-REFINEMENT STUDY THAT SETTLES IT

The same instrument on the three tessellations already on disk, which differ only in blade
facet size:

| r/R | `c1` 0.55 mm | `cm1` 0.35 mm | `prod7` 0.20 mm | cm1 / prod7 |
|---|---|---|---|---|
| 0.35 | REFUSED | 1.8665 | 1.9068 | 0.98 |
| 0.40 | REFUSED | 1.3459 | 1.0728 | **1.25** |
| 0.50 | REFUSED | 0.9610 | 0.7162 | **1.34** |
| 0.60 | REFUSED | 0.5038 | 0.3408 | **1.48** |
| 0.70 | REFUSED | 0.2875 | 0.1938 | **1.48** |
| 0.80, 0.90 | REFUSED | REFUSED | 0.1062, 0.0562 | — |

**`c1` cannot see the leading edge at any station on any blade.** `cm1` sees it only inboard.
And where both see it, **the measured radius FALLS as the tessellation is refined, at every
station outboard of r/R 0.35, and it has not stopped falling.** At r/R 0.35 — the one station
where `prod7` spans the nose with 27.7 facets, comfortably inside the measured window — the two
tessellations agree to **2.1 %**, which shows the instrument IS convergent where the geometry is
resolved.

> **THEREFORE: every R_LE outboard of r/R 0.35 in §I.5 is an UPPER BOUND, from two independent
> directions — the nose ladder over-reports a nose it cannot span, and refinement is still
> reducing the value. §6.3's required cell, R_LE/8, is correspondingly an upper bound.
> THE CLAUSE HAS NO ESTABLISHED SATISFYING CELL SIZE, because the quantity it is written in
> terms of has not converged on this geometry.**

### I.7 THE TESSELLATION CANNOT CARRY THE BAND — AND THIS HAS NOTHING TO DO WITH THE MESH

`snappyHexMesh` snaps to the STL, so **below the facet size the surface IS flat** and
refinement past it resolves a polyhedron rather than a propeller — with no residual signature
and nothing for `checkMesh` to report. Against `prod7`'s own facets at the leading edge:

| r/R | cell the clause demands | `prod7` facet at the LE | facet ÷ cell |
|---|---|---|---|
| 0.35 | 0.2384 | 0.2163 | **1.6×** |
| 0.50 | 0.0895 | 0.2101 | **3.0×** |
| **0.70** | **0.0242** | **0.0722** | **4.2×** |
| 0.85 | 0.0104 | 0.0451 | **5.2×** |
| 0.90 | 0.0070 | 0.0374 | **8.6×** |

> **AT ALL THIRTEEN MEASURED STATIONS THE PRODUCTION TRIANGULATION IS COARSER THAN THE CELL
> §6.3 DEMANDS — by 1.6× to 8.6×. The 8-cell clause is unsatisfiable on this geometry file for
> a reason that is not about the mesh at all.** No refinement level fixes it; only a new
> tessellation can, and §I.8 prices one.

Recorded because it inverts an assumption: the leading-edge facets are **not** the coarse
0.19 mm background. `prod7` already carries **674,295 blade facets below its own
`MeshSizeMin` of 0.08 mm** — genuinely isotropic (aspect ratio p50 **1.31–1.39**, longest edge
0.019–0.063 mm), **not slivers** — concentrated at r/R 0.82–0.92. They are **11.34 % of blade
facet COUNT but 0.759 % of blade AREA**, which is `docs/NUMERICS_KNOWLEDGE.md` N-X5 again: a
count is a locator, never a magnitude.

### I.8 THE BAND AS A BUILDABLE SPECIFICATION, AND WHERE IT STOPS BEING ONE

**The specification.** Surface/region name **`leadingEdgeBand`**, a `triSurfaceMesh` tube of
radius **1.0 mm** about the leading-edge path, entered in `snappyHexMeshDict` under
`refinementRegions` as `{ mode inside; levels ((1e15 N)); }`. The path is **measured, not
assumed: 131.389 mm per blade**, from the leading-edge facets across 70 stations from r/R 0.30
to 0.99 with the blade pinned by angle (the CAD trailing-edge curve is 114.465 mm, for scale).
1.0 mm is not cosmetic: `nCellsBetweenLevels 3` down from level N to the registered blade
level 5 needs ≈ 0.8 mm of buffer, so a tighter tube would be widened by snappy anyway.

**The cost, on rates measured on this case, this CAD, this box.** Meshing **10.61 core-min per
million cells** (F360_coarse: 19,700,035 cells, 12,538.33 s, 1 rank). Tessellation **1.582 ms
per facet** (prod7: 7,230,286 facets, gmsh CPU 11,439.9 s). Storage **217 bytes per cell**
(F360_coarse polyMesh, 4,275,145,191 bytes ÷ 19,700,035 cells).

| level | cell mm | clause met out to | band cells/blade | passage total | mesh core-min | STL facets needed | tess core-min | polyMesh |
|---|---|---|---|---|---|---|---|---|
| 6 | 0.139 | r/R 0.35 | 0.20 M | 9.20 M | 98 | 0.2 M | 195 | 2.0 GB |
| 7 | 0.070 | r/R 0.50 | 1.44 M | 10.44 M | 111 | 0.6 M | 207 | 2.3 GB |
| 8 | 0.035 | r/R 0.60 | 10.64 M | 19.64 M | 208 | 2.5 M | 257 | 4.3 GB |
| **9** | **0.0174** | **r/R 0.75** | **81.63 M** | **90.63 M** | **961** | **10.0 M** | **455** | **19.7 GB** |
| 10 | 0.0087 | r/R 0.95 | 640.28 M | 649.28 M | 6,887 | 40.2 M | 1,250 | 141 GB |
| 11 | 0.0044 | every station | 5,074.64 M | 5,083.64 M | 53,926 | 160.7 M | 4,428 | **1,103 GB** |

**BUILDABLE: level 9.** It is the rung that reaches **the reference radius r/R = 0.70**, at
**90.63 M cells per 72° passage, 961 core-min of meshing plus 455 core-min of tessellation =
1,416 core-min**, $1.21 **derived, not measured**, at the reported-by-owner $0.0513/core-h. It
needs a new tessellation carrying ~0.017 mm facets in the leading-edge band — **a `Distance` +
`Threshold` field on the measured leading-edge polyline, with curvature OFF**, which is the
configuration with a 3-of-3 completion record on this CAD; addendum C records **4 of 5
curvature-driven runs KILLED**, so curvature-driven sizing is not proposed.

**NOT BUILDABLE: full compliance.** Level 11 is what the measured radius at r/R 0.90 demands.
**5,083.64 M cells in one 72° passage is 1,103 GB of polyMesh alone — against 268 GB free on
this filesystem and 739 GB of RAM in the whole box.** It is not a budget number and no ruling
about caps reaches it: **it does not fit.** And because §I.6 shows R_LE still falling with
tessellation refinement, **level 11 is itself a floor, not a sufficient level.**

Both rates are **FLOORS**: snappyHexMesh cost per cell rises with refinement depth, and 90.63 M
cells is **10× the registered fine target** of ~9 M per passage, so level 9 changes a
registered cell target and is **not this lane's to adopt.**

### I.9 WHAT IS RAISED, AND WHAT IS NOT DECIDED HERE

1. **§6.3's leading-edge clause is unsatisfiable as written at every level of the registered
   family, and unsatisfiable at ANY level on the present tessellation.** Route 2 of addendum
   D.5 — build as registered and disclose — is now supported by a converged-where-resolved,
   controlled measurement instead of by a withdrawn one.
2. **The disclosure figure the birth certificate should carry.** `birth_certificate.py`
   currently prints `cells across LE radius 2.301` from addendum F's withdrawn R_LE = 1.438 mm
   at r/R 0.60. On the measurement here, at r/R 0.60 R_LE = **0.3408 mm**, so the coarse
   level's 0.6250 mm cell spans **0.55 cells** across the radius, and at r/R 0.70 it spans
   **0.31**. **The shortfall is 14.7× at r/R 0.60 and 25.8× at r/R 0.70, not 3.48×** — and both
   are LOWER bounds. Changing that printed figure touches a certificate and is the cfd
   supervisor's call, not this lane's.
3. **Whether the act proceeds on a leading edge whose radius is not converged.** Nothing here
   rules on it.

### I.10 COST OF THIS ADDENDUM

| item | core-min | basis |
|---|---|---|
| `gmsh -1` CAD curve extraction | 0.05 | MEASURED, CPU 3.02 s |
| curvature on `prod7`, brute-force provenance test | **3.2 WASTE** | abandoned at 3 m 13 s, 1 core; 1.7e10 distance evaluations with a 7.7 GB temporary per chunk. Replaced by a KD-tree. **Named, not absorbed.** |
| curvature on `prod7`, KD-tree | 1.26 | MEASURED, CPU 75.57 s |
| ladder controls (both) | 1.19 | MEASURED, CPU 71.50 s |
| span sweeps (`prod7` ×3, `cm1`, `c1`), section diagnostics, band spec | ~14 | ESTIMATED from wall clock at 1 rank; not separately instrumented |
| **total** | **≈ 20 core-min**, of which **3.2 waste** | $0.017 derived, not measured |

**No solver ran. No mesh was built. No queue was touched.**
