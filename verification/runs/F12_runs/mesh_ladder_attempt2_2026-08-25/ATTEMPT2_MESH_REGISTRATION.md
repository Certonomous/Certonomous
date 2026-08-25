# F12 attempt 2 — mesh-instrument registration

**Committed BEFORE the ladder was built.** This document registers the
replacement mesh instrument and the run root. It **registers no gate, no
threshold, no cap and no label**: every one of those is as frozen 2026-07-30 in
`verification/campaign/F12_PREREGISTRATION.md`, blob
`080303c57aee52849bb625579565a84ca5469717`, and this attempt grades against that
document unchanged. The frozen file is **not edited** and
`sdk/workflows/rae2822_case9.py` is **not edited**.

**Run root, registered by name and asserted ABSENT before the build:**
`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/{coarse,medium,fine,control_attempt1_correspondence}`

**Builder:** `build_ladder_attempt2.py`, beside this file. It refuses to run
unless it hashes equal to its own HEAD blob, unless the frozen pre-registration
on disk hashes equal to the blob above, unless six frozen gate sentences are
found verbatim in that blob, unless the attempt-1 trees still exist, and unless
all four target directories are ABSENT.

---

## 1. Why attempt 1's ladder was inadmissible, stated as a mechanism

Attempt 1's O-grid mapped the aerofoil surface onto the far-field circle by
**proportional arc length inside four quarter blocks**. Inside a block the inner
(polyLine) and outer (arc) edges carry the same grading and the same cell count,
so the surface station at arc-fraction *f* is joined by a straight line to the
far-field point at arc-fraction *f*. **The angle between that line and the
outward surface normal IS the near-wall non-orthogonality.**

Measured on the actual section spline, that angle for attempt 1's corner
placement is:

| x/c (lower surface) | outward normal | attempt 1's far-field angle | misalignment |
| --- | --- | --- | --- |
| 0.005 | 229.3° | 180.9° | 48.4° |
| 0.020 | 246.4° | 182.4° | 64.0° |
| **0.070** | **~256°** | **~186°** | **~70.6°** |
| 0.200 | 264.7° | 198.6° | 66.1° |
| 0.500 | 276.2° | 225.0° | 51.2° |

A predictor built from exactly this returns **70.608°** for attempt 1's coarse
mesh, against the **70.646°** its `checkMesh` measured — 0.038° apart. The
mechanism is a property of the **correspondence**, not of the spacing, which is
why refinement moved it the wrong way and why the over-70 face count scaled ×4.

## 2. The replacement, and why orthogonality is decoupled from resolution

Attempt 2 sets each block corner's far-field point from **that station's own
surface-normal direction**. Because the correspondence inside a block is
proportional arc length *whatever the grading is*, the near-wall misalignment
depends only on **where the corners are** and **what outer angle each is given**
— never on the cell counts or gradings, which are therefore free to serve
resolution and **cannot move the gate**. That decoupling is the design's whole
point and it is what makes the recipe honest.

**Recipe, level-independent:**

- Corner stations, both sides: `x/c = 0, 0.0025, 0.01, 0.03, 0.08, 0.18, 0.35,
  0.55, 1.0` — 8 blocks per side, 16 surface blocks plus 2 wake blocks.
- Far-field angle at each corner: the outward surface-normal angle, made
  strictly monotone (the RAE 2822 lower surface is **concave** aft of x/c ≈ 0.7,
  so its normal angle is not monotone and a bare running-max saturates into
  degenerate zero-arc blocks), then rescaled so the endpoints land on 180°/90°
  (upper) and 270°/180° (lower). Monotonising blend **0.30**.
- Surface spacing target, fixed across the ladder:
  `ds(x) = ds_mid + (ds_le − ds_mid)·e^(−x/0.03) + (ds_te − ds_mid)·e^(−(1−x)/0.10)`
  with `ds_le = 8.0e-4`, `ds_mid = 0.012610`, `ds_te = 8.0e-3`. `ds_mid` is not a
  free knob: it is solved so the surface cell demand comes to 192, which is what
  holds the frozen cell counts.
- Per-block cell counts double with the level; per-block gradings are held
  **fixed**, so every surface spacing halves exactly — a geometrically similar
  family in the azimuthal direction by construction.
- Wall-normal: unchanged from the frozen anchoring — 2.0e-6 / 1.0e-6 / 5.0e-7
  chord, ny = 80 / 160 / 320.
- **Wake outlet: UNIFORM at every level** (see §4).
- Far-field radius 50, wake length 50, patch names and patch face assignment
  reproduced from attempt 1 **face for face**.

## 3. The design criterion, declared before the design was evaluated

**≤ 55° predicted at all three levels**, on both modelled mechanisms — stricter
than the 70° gate, which is not touched. The builder **refuses to build** if the
recipe misses it. Selection among the configurations meeting it was made on
**resolution** — the finest trailing-edge spacing — and **not** on gate margin.

Search space fixed in advance: `ds_te ∈ {0.006, 0.008, 0.010, 0.012, 0.014}` ×
`blend ∈ {0.20, 0.25, 0.30}`. **9 of 15 met the criterion.** Predicted maxima
(coarse / medium / fine):

| ds_te \ blend | 0.20 | 0.25 | 0.30 |
| --- | --- | --- | --- |
| 0.006 | 65.7 | 61.6 | 57.8 |
| **0.008** | 60.6 | 56.0 | **51.8** ← selected |
| 0.010 | 56.6 | 51.7 | 47.4 |
| 0.012 | 53.2 | 48.2 | 43.8 |
| 0.014 | 50.8 | 45.7 | 41.4 |

(worst of the three levels shown; the selected point predicts 51.8 / 35.3 / 35.3)

## 4. The third mechanism, found by measurement and not modelled by either predictor

Building the selected recipe with attempt 1's wake-outlet anchor of 0.3 chord
measured **64.10 / 65.65 / 67.12°** — passing, but on a margin that *worsened*
under refinement, which is attempt 1's own signature. An exact non-orthogonality
calculator written from the `polyMesh` and validated against `checkMesh` to the
fourth decimal (51.1237 against 51.1237; 64.0958 against 64.0958) put the maximum
**inside the first wake column immediately behind the trailing edge**, not at the
wall.

Mechanism: the wake block's wall-normal distribution is graded `r_y` at the
trailing-edge end and by a separate anchor at the outlet. With a 2e-6 first cell
at one end and 0.3 chord at the other, the layer heights taper strongly along the
first streamwise cells, shifting each cell's centroid in x by a different amount
and tilting the centre-to-centre vector off the face normal.

Declared five-point sweep of that anchor, max non-orthogonality coarse/medium/fine:

| anchor | coarse | medium | fine | max aspect ratio |
| --- | --- | --- | --- | --- |
| 1.0e-4 | 85.6 | 73.5 | 40.4 | 1.3e5 |
| 3.0e-4 | 80.9 | 58.3 | 37.2 | 4.4e4 |
| 1.0e-3 | 77.5 | 51.6 | 37.2 | 1.3e4 |
| 3.0e-3 | 85.3 | 75.5 | 47.8 | 7.0e3 |
| 3.0e-2 | 86.8 | 85.7 | 81.6 | 2.4e3 |
| 1.0e-1 | 79.8 | 81.3 | 80.7 | 2.8e3 |
| 3.0e-1 (attempt 1's) | 64.1 | 65.7 | 67.1 | 2.8e3 |
| **UNIFORM** | **51.1** | **51.5** | **51.9** | **≤2.8e3** |
| equal to the wall value | 50.1 | 36.1 | 37.2 | 6.8e6 (rejected) |

**A uniform wake outlet is adopted.** It is the same KIND of distribution at
every level and it halves with the ladder like every other spacing, so the family
stays similar; what the frozen module's guard refuses is a **silent flip** to
uniform at one level only, which is not what this is. It is the only setting
measured whose margin does not degrade under refinement, and the equal-to-the-wall
alternative is rejected on aspect ratio (6.8e6), not on its gate number.

## 5. Honest limits, stated before the result

- **Neither predictor bounds the measured maximum.** They model two mechanisms;
  a third lives in the wake block and is bounded only empirically. Gate A is
  decided by a real `checkMesh` log and by nothing else. An ABSENT log reads
  **ABSENT**, never clean.
- **The residual maximum still rises slightly with refinement** — +0.40° per
  level — and this document says so in advance rather than after.
- **The polygon is finer than attempt 1's** (160 points per block edge, 16 block
  edges per side, against attempt 1's 240 per quarter), so the geometric error
  floor is not the same number as attempt 1's. It is identical across the three
  levels, which is what a ladder requires, and that identity is checked with its
  own planted control.
- **Reported, not repaired:** attempt 1's patch assignment is asymmetric — the
  upper wake block's far boundary is `outflow` while the lower wake block's is
  `inflow`. It is reproduced face for face here rather than silently corrected,
  because it is a boundary-condition question and belongs to gate B.
- **Reported, not repaired:** `_wake_ratio` sizes the wake's streamwise grading
  for a length of 50 while the block edge is 99 long, so the first wake cell comes
  out 1.98× the trailing-edge spacing the code's own docstring says it should
  match. Fixing it was measured and made the maximum *worse* (65.6 / 67.1 / 68.2),
  so it is left as attempt 1 had it and recorded here.

## 6. Cost, registered before the build

Meshing is priced on this team's measured fit `t ≈ 0.930 s × (N/23,040)^0.72`
(**a measured fit** to attempt 1's own mesh-audit timings; the frozen §4's linear
model over-predicted by 8.18× like-for-like), plus ~1.5 s per-process startup.
Predicted `blockMesh` + `checkMesh`: **0.93 / 2.49 / 6.64 s**. With two
`decomposePar` runs per level, a control mesh and the geometry work, the whole
mesh phase is registered at **≤ 5 core-min at ranks = 1**, inside the frozen §4
meshing allowance and the §5 headroom. **It is given no new cap and it does not
create one.** An overrun stops the work; it does not get a new budget.

Dollars are **derived at $0.0513/core-h and reported-by-owner, never measured** —
this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

## 7. Deterministic decomposition

Method **`hierarchical`**, `n (2 2 1)`, 4 subdomains. `hierarchical` is
**seed-free**: the partition is a pure function of the cell centres, so identical
input gives identical partitions **by construction**. `scotch` is not used — this
team measured it return 12777/12906/12965 and then 12974/12870/12865 on a
byte-identical mesh, and that alone decided a convergence verdict. The builder
runs the decomposition **twice** at every level and asserts the partition cell
counts identical; the counts are recorded in the birth certificates.
