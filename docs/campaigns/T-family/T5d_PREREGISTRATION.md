# T5d — the Meinders cube ladder with the near-wall mesh REPAIRED, graded on T5b's gate, unmoved: pre-registration (FROZEN)

**Version 1.0. Rung `T5d`. Family: T. Team: heat-transfer.**
**Status: FROZEN at this commit. No T5d case has been built and no T5d case has run.**

> **THE BOUNDARY THIS DOCUMENT IS WRITTEN INSIDE, STATED FIRST BECAUSE IT IS WHAT
> MAKES THE RUNG LAWFUL.** T5b returned `0 of 6`, every row `NOT A RESULT`, at the
> first clause of its admission order, on **one statistic on one wall of one
> level**. There are two ways to make that go away and only one of them is
> allowed. The forbidden way is to move the gate — relax the `2.0 ×` ladder
> tolerance, move the fine level's target off `1.00`, drop `cube_front` from the
> registered wall set, or re-scope the ladder to two levels so the failing one is
> not graded. **None of those happens here. T5d changes the MESH and carries
> T5b's gate to it, unmoved and byte-identical.** §5 states that in terms and
> makes it checkable by hash rather than by assertion.

---

## 1. WHAT T5b MEASURED, RE-VERIFIED AT SOURCE BY THIS LANE

Every figure in this section was re-read from the artifacts, not taken on relay.
**T5b is not re-graded, not re-opened and not disturbed by this document.** Its
`NOT A RESULT` stands and this rung supersedes rather than overturns it.

### 1.1 The verdict and the single failing statistic — CONFIRMED

From `verification/runs/T-family/T5b_runs/T5B_GRADE_OUTPUT.txt`:

| what | reading | line |
|---|---|---|
| level `c` | `completion: COMPLETE  y+: MET` | `:4` |
| level `m` | `completion: COMPLETE  y+: MET` | `:5` |
| level `f` | `completion: COMPLETE  y+: NOT A RESULT` | `:6` |
| the ground, identical on all six rows | `y+ exceeds 2.0x the level target 1.00 on: cube_front=2.310 -- the ladder is not the registered ladder` | `:11`–`:16` |
| tally | `0 of 6 graded rows PASS`, 7 REPORTED rows excluded by name (D534) | `:18` |

**Confirmed:** it is the **ladder** clause that fires, not the sublayer clause —
`2.310` is inside `y+_max ≤ 5.0` with room to spare. **Confirmed:** the bound is
`2.00` = the fine level's registered target `1.00` at the registered `2.0 ×`
tolerance (`T5b_PREREGISTRATION.md` §5). **Confirmed:** prediction P2 is
FALSIFIED on the fine level and `T5b_PREREGISTRATION.md` §6 and §12 named that
risk in advance.

### 1.2 Rule 4 and rule 3 — CONFIRMED, and this is why the failure is a mesh finding

All three arms completed cleanly, `rc = 0`, `capped = 0`, `note = clean`, age
guard PASS on all three (`T5b_RESULTS.md` §2, §76–§83), and the planted-zero
control was exercised and passed (§4, `T5B_GRADE_OUTPUT.txt:8`). Re-read from
`verification/runs/T-family/T5b_runs/STATUS.T5_CUBE_{c,m,f}`:

| level | wall s | core-min | cap core-min | capped | note |
|---|---:|---:|---:|---:|---|
| `c` | 1,007 | **16.783** | 32.8 | 0 | clean |
| `m` | 5,252 | **87.533** | 154.4 | 0 | clean |
| `f` | 20,851 | **347.517** | 651.2 | 0 | clean |

**So the instrument worked and the compute worked.** What did not work is the
mesh's claim to be a refinement family in the near-wall sense the rung
registered. That is the defect T5d repairs.

### 1.3 ONE CORRECTION TO THE BRIEF THIS LANE WAS GIVEN, MADE BY NAME

The brief describes the cause as *"a MESH defect on one face of the fine grid"*.
**That is right in its conclusion and wrong in its mechanism, and the difference
changes the repair.** Measured from each level's own
`constant/air/polyMesh/points` (this lane, 2026-09-04):

| level | `cube_front` | `cube_rear` | `floor` | `cube_top` | `roof` | `cube_side_n` |
|---|---:|---:|---:|---:|---:|---:|
| `c` | 128.000 µm | 128.000 µm | 128.000 µm | 128.000 µm | 128.000 µm | 128.000 µm |
| `m` | 80.000 µm | 80.000 µm | 80.000 µm | 80.000 µm | 80.000 µm | 80.000 µm |
| `f` | 50.000 µm | 50.000 µm | 50.000 µm | 50.000 µm | 50.000 µm | 50.000 µm |

**The fine grid's first cell at `cube_front` is not wrong relative to the
ladder.** All six graded walls carry the same first-cell height on each level, and
the ladder refines it by **exactly `R = 1.6` per level**, to five significant
figures, which is precisely what `build_t5.py`'s own docstring registers ("ONE
refinement factor R = 1.6 applied to EVERY direction INCLUDING the first wall
layer, so the three levels are geometrically similar"). Nothing was built wrong on
one face.

**The real mechanism.** `y+ = (h/2)·u_τ/ν`. Taking `ν = 1.510e-05 m²/s` and the
measured `y+_max` on `cube_front` at `Time = 5000`, the implied peak friction
velocity is:

| level | first cell `h` | `y+_max` cube_front | implied `u_τ` at the peak | ratio to level target |
|---|---:|---:|---:|---:|
| `c` | 128.0 µm | 3.8043 | 0.8976 m/s | 3.8043 / 2.6 = **1.4632** |
| `m` | 80.0 µm | 2.9610 | 1.1178 m/s | 2.9610 / 1.6 = **1.8506** |
| `f` | 50.0 µm | 2.3100 | 1.3953 m/s | 2.3100 / 1.0 = **2.3100** |

**`h` falls by 0.625 per level; `y+_max` falls by only 0.780; the peak `u_τ`
GROWS by 1.248 per level.** The point maximum sits on the front-face leading
edge, where the wall shear is not mesh-converged, so the **ratio to the level
target drifts UP the ladder by ≈ 1.25 per level** and the tightest level — the
fine one, whose target is `1.00` — is the first to cross `2.0 ×`. Level `m` was
already at `1.8506`, i.e. **92.5 % of its own bound**: T5b did not fail by an
isolated accident on one grid, it failed because the drift ran out of room.

**Why this correction matters operationally.** If the mechanism were a one-face
build error, the repair would be to fix the fine level. It is not, so **repairing
only the fine level would break the geometric similarity that makes the three
meshes a Roache triple at all** — it would trade a `y+` refusal for an
inconsistent refinement family, which is a worse defect and a silent one. The
repair therefore has to move all three levels together. That is §3.

`T5c` reached the same physical diagnosis independently from the same artifacts
(`T5c_PREREGISTRATION.md` §3: *"THE GATE FIRES BECAUSE IT IS WRITTEN ON A POINT
MAXIMUM OVER A FIELD THAT …"*, and §148 on the sharp local maximum a point
statistic latches onto) and took the **other** route: it moved the statistic off
the point maximum onto an area-weighted mean. **T5d does not adopt T5c's
statistic, does not depend on T5c, and does not cite T5c's verdicts as support.**
T5d keeps T5b's point maximum and repairs the mesh under it. The two rungs are
independent tests of the same diagnosis, and that is deliberate.

---

## 2. THE PHYSICS OF THE RUNG — carried from T5b's registration, not from imagination

Every item below is registered **unchanged** from `T5b_PREREGISTRATION.md` §4,
which carries it unchanged from `T5_PREREGISTRATION.md`.

- **Case:** Meinders (1998) heated wall-mounted cube in a developing channel,
  **conjugate**, solved with `chtMultiRegionSimpleFoam` (OpenFOAM v2606,
  `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/`).
- **Geometry:** `H = 15 mm`; **half domain** with a `symmetryPlane` at `z/H = 0`;
  `x/H ∈ [−8, 20]`, `y/H ∈ [0, 3.4]`, `z/H ∈ [0, 5]`. Cube front face at `x = 0`,
  floor at `y = 0`.
- **Conjugate setup:** an epoxy shell `d = 1.5 mm` (`k = 0.24 W/mK`) on the five
  exposed cube faces and its bottom; the **copper core is NOT meshed** — its
  boundary is patch `core` held at `T = 348.15 K`. Two regions, `air` and
  `epoxy`, cut by `splitMeshRegions -cellZonesOnly -useFaceZones`; the four cube
  faces are `mappedWall` (they **are** the conjugate interface), `floor` and
  `roof` are `wall`.
- **Flow:** `U_B = 4.47 m/s`, `ν = 1.510e-05 m²/s`, `Pr = 0.71`, inlet air at
  `T = 293.65 K`. **`Re_H = U_B·H/ν = 4,440`** (derived from the three registered
  constants, not typed). Inflow from the `X_2d` 2-D developing-channel precursor
  map, **copied and digest-verified**, never re-derived — digest
  `b1741eb9ae4288e1f8e8bfaba3fad43fba422b872f2d761602b6724197b0e103`, 4 files,
  83,071 bytes; the builder **refuses** if it moves.
- **Closure:** `kOmegaSST` at `Pr_t = 0.85`; `Gauss harmonic corrected` on the
  solid laplacian; every scheme and relaxation factor as registered.
- **Control:** `endTime 5000`, `deltaT 1`, `writeControl timeStep`,
  `writeInterval 1000`, `purgeWrite 3`, **1 rank**.
- **Function objects:** T5b's repair, unchanged and applied by **T5b's own frozen
  patcher** — `executeControl timeStep; executeInterval 1; writeControl timeStep;
  writeInterval 1000;` on both `yPlus` and `wallHeatFlux`. T5d inherits this and
  the launcher refuses any case whose `controlDict` still carries a `writeTime`
  control.
- **The six graded walls:** `cube_front`, `cube_top`, `cube_rear`,
  `cube_side_n`, `floor`, `roof`. `cube_side_s` does not exist on a half domain
  and is not named. Checked in **both** directions against
  `constant/air/polyMesh/boundary` — a registered wall absent from the mesh, or a
  mesh wall the gate does not name, is a **refusal (exit 2)**.
- **Reference:** `verification/runs/T-family/T5_runs/T5_reference_primary.json`,
  blob `04dfd7e2e56adf1cd0924046500904af2243b747`, digitised 2026-08-26 under T5
  AMENDMENT 7 from Meinders (1998) Figs 5.45 and 5.37. **T5d re-digitises
  nothing.**
- **Model-form limitations inherited in full** (`T5b_PREREGISTRATION.md` §12):
  the roof boundary layer is modelled fully turbulent against a thesis that
  describes it as developing laminar; the copper core is not meshed; radiation is
  off; the base plate does not conduct.

---

## 3. WHAT CHANGED, AND ONLY THIS — the mesh repair, with the numbers

### 3.1 The one change

```
build_t5.FIRST_LAYER_C :   0.128e-3 m   ->   0.080e-3 m       (scale 0.625 = 1/R)
```

applied through the **frozen** `verification/runs/T-family/T5_runs/build_t5.py`
arithmetic — the module constant is overridden, `build_cube_case()` is then called
unmodified, and the constant is restored in a `finally` so it cannot leak. The
factor is `1/R`, **one rung of the ladder's own refinement ratio**, chosen so the
repair is expressed in the ladder's own currency rather than in a number invented
for this rung.

### 3.2 Measured before, registered after

| level | first cell BEFORE (T5b, measured from `polyMesh/points`) | first cell AFTER (T5d, registered) |
|---|---:|---:|
| `c` | **128.000 µm** | **80.000 µm** |
| `m` | **80.000 µm** | **50.000 µm** |
| `f` | **50.000 µm** | **31.250 µm** |

The "before" column is a **disk measurement** on all six graded walls of all
three built T5b meshes, not a builder input read back to itself. The "after"
column is written out as literals in `build_t5d.py` (`FIRST_LAYER_LEVEL`) and
cross-checked against `0.080e-3 / 1.6^lvl` by a guard that refuses on
disagreement.

### 3.3 What does NOT change, and this is load-bearing

- **The cell counts do not move.** `build_t5.counts(lvl)` depends only on the
  level index, never on the first-layer height, so the three meshes remain
  **52,684 / 212,942 / 882,024** cells. Therefore the **measured refinement
  ratios `r21 = 1.6060` and `r32 = 1.5929` are unchanged**, the GCI arithmetic is
  unchanged, and the frozen comparator's `CELLS_REGISTERED` check (which refuses
  on a mismatch, `analyse_t5b.py:757`) still passes. This is verified in the
  builder's selftest, not asserted.
- **The ladder stays geometrically similar in the first wall layer**, because all
  three levels are scaled by the same factor. The property `build_t5.py`'s
  docstring registers — *"so the three levels are geometrically similar and the
  triple is a true refinement"* — is preserved exactly, and that is the whole
  reason the repair is global rather than applied to level `f` alone.
- **Every gate value.** See §5.

### 3.4 Mesh quality — checked before the mesh is built, not after it fails

`checkMesh` on T5b's three air meshes: max aspect ratio **133.2 / 135.2 / 140.4**,
max skewness `≤ 7.3e-13`, non-orthogonality check OK, `Mesh OK` on all three and
on both regions. The mesh is a Cartesian `blockMesh` lattice, so non-orthogonality
and skewness are at machine precision **by construction** and cannot be degraded
by a first-layer change. Scaling the first layer by 0.625 at fixed cell count
raises the near-wall cell aspect ratio by ≈ 1.6 ×, to an expected **≈ 213–225** —
well inside `MESH_STANDARD.md` §3.3, which makes aspect ratio **advisory at
1,000** and explicitly defensible where the anisotropy is wall-aligned and
non-orthogonality and skew are near zero, which is this case exactly.

The maximum **cell-to-cell growth ratio** rises with the change. Computed from the
frozen grading helpers (this lane, before any mesh was built):

| level | max growth ratio, T5b | max growth ratio, T5d | where |
|---|---:|---:|---|
| `c` | 2.906 | **5.250** | the 2-cell floor sub-station `y ∈ [0, 0.5 mm]` |
| `m` | 1.845 | **2.541** | same block |
| `f` | 1.352 | **1.607** | same block |

The worst figure, 5.250, is confined to the **coarse** level's two-cell floor
sub-station. It implies an adjacent-cell volume ratio of ≈ 0.19, comfortably
above `MESH_STANDARD.md` §3.4's proposed 0.01 warning. **It is registered here
rather than discovered later**, and it is a named risk in §6.

### 3.5 Four repairs CONSIDERED AND REFUSED, recorded so nobody proposes them again

Each of these would have made the refusal disappear. Each is **gate-widening**
and is refused on Sanaa's standing ruling that gates are never widened to fit
(session record `etc/sessions/2026-09-04T0050Z_sanaa_all_cases_mandatory.md`,
addendum: *"gates and thresholds are NEVER widened to manufacture a pass"*).

| refused repair | why it is gate-widening |
|---|---|
| relax `YPLUS_TARGET_TOL` from `2.0` | moves the registered tolerance |
| move `YPLUS_TARGET["f"]` off `1.00`, or let the targets drift at the measured 1.25/level | moves the registered level target — and would be chosen **because** it fits the answer |
| drop `cube_front` from `YPLUS_WALLS` | drops the failing wall; this is T4's control-C1 shape verbatim |
| grade only `c` and `m` | re-scopes the ladder to dodge the failing level, and destroys the triple |

---

## 4. PREDICTIONS, WITH NUMBERS, AND WHAT WOULD FALSIFY EACH

Registered **before** any T5d mesh is built and before any solver starts.

### P1 — the instrument still fires

All three levels produce `postProcessing/air/yPlus/0/yPlus.dat` with **6 data rows
at `Time = 5000`**, one per registered wall, plus a `yPlus` field and a
`wallHeatFlux` field at `5000/air`.
**Falsifier:** fewer than 6 rows on any level, or an absent field.
*This is the prediction most likely to hold: T5b measured exactly 30 rows (5 write
times × 6 walls) on every level and T5d changes nothing about the function
objects.*

### P2 — the `y+` gate returns MET on all three levels

**The full predicted table**, first-order at frozen `u_τ`: every wall's T5b
measured `y+_max` at `Time = 5000`, multiplied by **0.625**. Registered here for
**every graded wall on every level**, because tightening one wall must not push
another off the ladder and a successor that trades one failing wall for a
different one has learned nothing.

**Level `c` — target 2.60, ladder bound 5.20, sublayer bound 5.00**

| wall | T5b measured | **T5d predicted** | predicted ÷ target |
|---|---:|---:|---:|
| `cube_front` | 3.8043 | **2.3777** | 0.9145 |
| `floor` | 3.4469 | **2.1543** | 0.8286 |
| `cube_top` | 2.4216 | **1.5135** | 0.5821 |
| `cube_side_n` | 2.4050 | **1.5031** | 0.5781 |
| `cube_rear` | 1.6742 | **1.0464** | 0.4024 |
| `roof` | 1.1714 | **0.7321** | 0.2816 |

**Level `m` — target 1.60, ladder bound 3.20, sublayer bound 5.00**

| wall | T5b measured | **T5d predicted** | predicted ÷ target |
|---|---:|---:|---:|
| `cube_front` | 2.9610 | **1.8506** | 1.1566 |
| `floor` | 2.3894 | **1.4934** | 0.9334 |
| `cube_top` | 1.9031 | **1.1894** | 0.7434 |
| `cube_side_n` | 1.7324 | **1.0827** | 0.6767 |
| `cube_rear` | 1.4435 | **0.9022** | 0.5639 |
| `roof` | 1.2126 | **0.7579** | 0.4737 |

**Level `f` — target 1.00, ladder bound 2.00, sublayer bound 5.00**

| wall | T5b measured | **T5d predicted** | predicted ÷ target |
|---|---:|---:|---:|
| `cube_front` | 2.3100 | **1.4438** | **1.4438** ← the binding wall |
| `floor` | 1.6067 | **1.0042** | 1.0042 |
| `cube_side_n` | 1.2960 | **0.8100** | 0.8100 |
| `cube_top` | 1.2708 | **0.7942** | 0.7942 |
| `cube_rear` | 1.0865 | **0.6791** | 0.6791 |
| `roof` | 0.6349 | **0.3968** | 0.3968 |

**No wall on any level is pushed up**, because the scaling is global and downward:
to first order every `y+` moves by the same factor 0.625, so the repair cannot
trade `cube_front` for another wall. The binding wall stays `cube_front` on level
`f` at **1.4438 against 2.00 — headroom ×1.385**, which absorbs a `u_τ` rise of up
to 38.5 % before the gate fires again.

**Falsifier:** any wall on any level above `5.0`, or above `2.0 ×` its level
target — which returns `NOT A RESULT` and takes every graded row with it.

**A SECOND, SHARPER FALSIFIER, ON THE MODEL RATHER THAN THE GATE.** The table
above is a **first-order estimate at frozen `u_τ`, not a solved value**, and this
document says so rather than dressing it as a solve. It assumes `y+ ∝ h` with the
flow field unchanged — defensible because both `2.31` and `1.44` sit deep inside
the viscous sublayer where `u⁺ = y⁺`, but **untested**: the lab has no measurement
isolating wall-normal-only refinement on this case, and thinning the first cell
also raises the near-wall growth ratio (§3.4), which can move `u_τ` on its own.
**Registered falsifier of the model:** if any wall's measured `y+_max` differs
from its predicted value above by more than **±25 %**, the first-order scaling
model is recorded as **FALSIFIED**, in the results record, **even if the gate
returns MET**. A gate that passes for a reason the registration did not predict is
not a validated prediction and will not be reported as one.

### P3 — the rows advance past clause 1

With the gate MET on all three levels, **all six graded rows reach clause 2** of
the §7 order and receive a grid-triple classification.
**Falsifier:** any row still refused at clause 1.

### P4 — the triples, and this is the prediction most likely to fail

**At least one of `G1a`, `G2a`, `G3a` returns a `CONVERGING` triple.**
**Falsifier:** none of the three does.

**The prior is registered against this prediction, in advance, rather than
discovered afterwards.** `T5c` re-graded T5b's *same three solves* on an
area-weighted `y+` statistic that let all three levels pass, and the rows were
then refused on their **triples**: `G1a` `OSCILLATORY`, `G3a` `OSCILLATORY`,
`G5a/b/c` `DIVERGENT`, with only `G2a` producing a usable triple (GCI 4.355 %,
`GATE FAIL` at 39.4023 against a reference 55.224 ± 5.66404). **So the honest
expectation is that T5d also finishes with `NOT A RESULT` on several rows, on
clause 2 instead of clause 1.** T5d's meshes are not T5b's — the near-wall stack
is different on every level, which is exactly the intervention that could change
an oscillatory triple — but this registration does **not** predict a clean sweep
and will not be read as having done so.

### P5 — the census, predicted explicitly so it cannot be claimed afterwards

**Fewer than 4 of the 6 graded rows PASS.**
**Falsifier:** 4 or more PASS. *Registered because a rung that predicts only
success has registered nothing.*

---

## 5. THE GATE — FROZEN, AND IDENTICAL TO T5b's, AND THE CLAIM IS CHECKABLE

**NO GATE, THRESHOLD, BAND, TARGET, TOLERANCE, FLOOR, LABEL, ROW CLASS,
STATISTIC OR REFERENCE MOVED BETWEEN T5b AND T5d.**

That sentence is not asserted here. It is **checkable by hash**, because T5d
introduces **no grading code at all**:

> **T5d's grading path IS the frozen `verification/runs/T-family/T5b_runs/analyse_t5b.py`,
> blob `552f7472f3ded7575256f877867cb076c6aab2e3`, byte-identical, invoked as**
> ```
> analyse_t5b.py --root verification/runs/T-family/T5d_runs
> ```
> **The comparator that graded T5b is the comparator that grades T5d. Anyone can
> verify that no gate moved with one `git hash-object`.**

The `--root` argument is the comparator's own registered interface
(`analyse_t5b.py:103`, `:1053`), not a new capability added for this rung, and the
case names are unchanged (`T5_CUBE_c/m/f`), so `CASE_OF` resolves without
modification. `REFERENCE` resolves relative to the comparator's own location, so
it still reads the same frozen reference JSON.

The gate that file carries, restated here for the reader and **not re-declared**
— these are its values, not new ones:

| clause | registered value | failure |
|---|---|---|
| sublayer bound, every wall | `y+_max ≤ 5.0` | `NOT A RESULT` |
| level target | `c` 2.6 / `m` 1.6 / `f` 1.0 | — |
| ladder tolerance | achieved ≤ **2.0 ×** the level target | `NOT A RESULT` |
| the statistic | the **point maximum** from `yPlus.dat` (T5b's; **not** T5c's area-weighted mean) | — |
| a wall not reported | — | `NOT A RESULT` |
| `yPlus.dat` absent or zero data rows | — | `NOT A RESULT` |
| a registered wall absent from the mesh | — | **REFUSAL (exit 2)** |
| a mesh wall the gate does not name | — | **REFUSAL (exit 2)** |
| graded `h` rows | `G1a` front, `G2a` top, `G3a` rear | band = `sqrt(stated² + digitisation²)`, Fig. 5.45, 10 % stated |
| graded `T_sur` rows | `G5a/b/c` front / top / rear | 0.4 °C stated ⊕ digitisation of Fig. 5.37 |
| intrinsic floor | deviation below **1.7 %** → `GATE REACHED`, not `PASS` | — |
| `G5` identity guard | reference `T_sur` within **5.0 K** of 20.5 °C or 75.0 °C → `NOT A RESULT — identity` | — |
| REPORTED rows | `G1 G2 G3 G4 R1 R2 R3` — a **ROW CLASS, not a verdict**, excluded from the census by name (D534) | — |

**A `GATE FAIL` will be reported as a `GATE FAIL`.** Not as "close", not as
"within engineering agreement", not as a `GATE REACHED`. If the repaired ladder
admits the rows and the physics then misses its band, that is a `GATE FAIL`, it is
recorded as one, and — per Sanaa's 2026-09-04 addendum — a measured persistent
`GATE FAIL` after the lab's own defects are exhausted goes to her desk **with the
evidence**, never laundered into a pass and never silently parked.

---

## 6. TRIPLE GATING — rule 5, binding, in the registered order

The order is the frozen comparator's and is not re-declared here; it is restated
so this document can be read alone:

1. any level's `y+` gate not `MET` → **`NOT A RESULT`**;
2. triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → **`NOT A RESULT`**,
   the fine value and both triples printed beside it;
3. reference value absent → **`BLOCKED`**, fine value and triple REPORTED;
4. `G5` only: the identity guard → **`NOT A RESULT — identity`**;
5. deviation below the **1.7 %** intrinsic floor → **`GATE REACHED`**;
6. otherwise **`PASS`** inside the band, else **`GATE FAIL`**, GCI printed.

**A non-`CONVERGING` triple is `NOT A RESULT` whatever the value.** The gate can
turn a `PASS` or a `GATE FAIL` **into** `NOT A RESULT`, never the reverse.
**GCI at `Fs = 1.25`**, unequal-ratio fixed-point form on the **measured**
`r21 = 1.6060` / `r32 = 1.5929` — unchanged, because the cell counts are unchanged
(§3.3). **No GCI is quoted when the three values are not monotone**, and no
observed order is quoted for a row that never reached a triple.

### Named risks, stated rather than hidden

- **The drift is bought off, not cured.** The ratio-to-target still rises ≈ 1.25
  per level (§1.3). T5d buys one ladder rung of headroom; **a fourth, finer level
  would meet the same wall.** Any successor that extends this ladder must expect
  it, and this rung does not pretend to have solved it.
- **The coarse floor sub-station's growth ratio rises to 5.25** (§3.4). No lab
  gate is breached, but if `checkMesh` on the built coarse mesh reports anything
  other than `Mesh OK`, that is a **finding**, the build stops, and it goes to the
  supervisor — it is not worked around.
- **The first-order `y+` model may be wrong** (§4, P2's second falsifier).
- **`u_τ` at the peak may itself move** when the near-wall stack changes; the
  headroom of ×1.385 is sized for that and the falsifier is registered.

---

## 7. RULE 4 — THE SIX-CLAUSE COMPLETION RULE, WRITTEN OUT, WITH THE MULTI-REGION AGE GUARD

A T5d case is **done** only if **all six** hold. Any one failing means the case is
not done; the comparator **refuses (exit 2) rather than degrades**.

1. **`rc = 0`** — the solver's own return code, the **value** being
   PHYSICS-CRITICAL and the **record** INFRASTRUCTURE (ruling R-RC, Sanaa
   APPROVED 2026-08-27). A `FOAM FATAL` or a signal token in `log.solve` refuses
   regardless.
2. **exactly one `End` line** in `log.solve`.
3. **last `Time =` equals `endTime`**, i.e. `5000 == 5000`.
4. **`ExecutionTime` iteration count equals `endTime`** — the iteration count, not
   the line count; the line count is INFRASTRUCTURE.
5. **all seven fields present at `5000/air`**: `T U p_rgh alphat nut k omega`.
6. **THE AGE GUARD.** Every field at `endTime` must be **NEWER** than the case's
   own initial-condition `T`.

**The dating file for THIS case is not `0/T`, because this case is
MULTI-REGION**, and that claim was verified on disk rather than assumed. Measured
on `verification/runs/T-family/T5b_runs/T5_CUBE_c` (this lane, 2026-09-04):

| file | mtime |
|---|---|
| `0/air/T` | 2026-08-27T22:31:09Z |
| `0/epoxy/T` | 2026-08-27T22:31:10Z |
| `0.orig/air/T`, `0.orig/epoxy/T` | 2026-08-27T17:15:16Z |
| earliest `5000/air` field | 2026-08-27T22:47:57Z |

**Measured, not assumed:** the launcher touches the file
`find "$CASE_DIR/0" -name T -type f | head -1` returns, and the comparator reads
the first `0/**/T` that `os.walk` returns. On this box **both return
`0/epoxy/T`** — verified by running both orderings against the case directory —
and `0/epoxy/T` is also the **later** of the two, so the launcher and the
comparator agree on the datum and it is the stricter one. **That agreement is
filesystem-ordering-dependent and is therefore not relied on.**

**REGISTERED for T5d:** the age-guard datum is **the LATER of `0/air/T` and
`0/epoxy/T`**, and the results record must **print both** mtimes beside the
earliest `endTime` field mtime on every level, as `T5b_RESULTS.md` §2 did. The
solid region is dated too: `5000/epoxy/T` must be present and newer than the
datum on all three levels.

**The arming guard, unchanged:** the launcher **refuses** if `0/` already exists
or if any numeric time directory is present before the run, so a case cannot be
armed twice and cannot inherit a stale answer.

---

## 8. RULE 3 — THE PLANTED-ZERO CONTROL

**T5d inherits the frozen comparator's control unchanged, because T5d does not
write a comparator.** It is stated here in full because a registration that
points at a control without naming it has registered nothing.

Two plants, because **a constant offset cannot test a range reader** (L-340) — add
the same number to every face value and the maximum moves by exactly that number,
so a broken max reader and a perfect one are indistinguishable under a uniform
shift:

| plant | magnitude | field | reader proved | acceptance |
|---|---|---|---|---|
| **constant offset** | `PLANT_OFFSET = 1.234e-03` | `endTime/air/T` on `cube_front` | the **area-mean** reader `face_mean_T_C` | the mean must move by the plant to within 10 % |
| **single-cell spike** | `PLANT_SPIKE = 9.876e+02` | `endTime/air/T` on `cube_front` | the **range/max** reader `read_patch_field` | the maximum must move by at least `0.9 ×` the plant |

The plants go into a **temp copy** (`tempfile.mkdtemp` / `shutil.copy2` /
`shutil.rmtree` in a `finally`), are read back **through the production readers**,
and run on the **fine level on a real graded patch, before any value is graded**.
**A failure of either arm is a REFUSAL, exit 2, not a degraded run**
(`analyse_t5b.py:781-788`, refusal at `:786`; constants frozen at `:163-164`).

**Every reader that can emit a zero on this rung is covered by one of these two
arms**, and the `y+` gate input itself is classified **GATE INPUT, never
infrastructure** — reclassifying it would convert a registered `NOT A RESULT` into
a bookkeeping note, which is the gaming shape, and negative control **N4** mutates
exactly that classification and makes the selftest fail.

---

## 9. THE BUILDER, AND ITS PROOF — driven BEFORE the freeze, with no mesh and no solver

`verification/runs/T-family/T5d_runs/build_t5d.py` is a **wrapper, not a fork**:
it imports the frozen `build_t5.py` and the frozen `build_t5b.py` as modules,
overrides one constant, calls `build_t5.build_cube_case()` unmodified, reuses
`build_t5b.dir_digest` and `build_t5b.patch_control_dict` verbatim, and restores
the constant in a `finally`. **A supervisor's check-1 is a short diff.**

**`--selftest`: 21 arms, 0 failed, and its output is BYTE-IDENTICAL under
`python3` and `python3 -O`. `0 ast.Assert` in the file (L-332).** No mesh was
written, no `blockMesh` was run and no solver was started to produce it. The arms:

- the one change reaches `block_mesh_3d` on all three levels, and the grading
  string blockMesh will actually read is **re-derived independently** of the
  helper that wrote it, implying **80.000 / 50.000 / 31.250 µm** at `cube_front`
  (agreement to < 5e-3 relative);
- the override **does not leak**: `build_t5.FIRST_LAYER_C` is back at `0.000128`
  after every build;
- `counts()` is independent of the first-layer constant, so the cell counts do
  not move;
- **the planted-failure pair, driven against a REAL mesh whose first layer is
  known by independent measurement.** CONTROL: `verify_first_layer` on T5b's
  coarse mesh against `128.0 µm` **accepts (exit 0)**. MUTANT: the **same mesh**
  against T5d's `80.0 µm` **REFUSES (exit 2)**. The guard is shown able to fail
  before it is believed when it passes. Absence of that mesh is a selftest
  **FAILURE, not a skip** — the proof is required, not optional;
- an unregistered case name refuses (exit 2);
- a binary `points` file **refuses** rather than reporting a mesh it cannot see.

**The build-time guard that makes an unlaunched builder safe.** After every build,
`build_t5d.py` **measures the first-cell height on all six graded walls from the
built mesh's own `constant/air/polyMesh/points`** and **refuses (exit 2)** unless
each is within `1e-3` relative of the registered value for that level. A mesh that
is not the registered mesh cannot reach a solver.

---

## 10. THE CAP IS ENFORCED, AND THE PROOF IS DRIVEN

`verification/runs/T-family/T5d_runs/run_one_t5d.sh` is
`../T5b_runs/run_one_t5b.sh` — the launcher whose cap enforcement was driven and
proven pre-freeze — with **exactly three mechanical substitutions** and a 20-line
provenance comment, and nothing else:

```
T5B_CAPS.txt   -> T5D_CAPS.txt        T5B_DETACHED -> T5D_DETACHED
run_one_t5b.sh -> run_one_t5d.sh
```

**MEASURED, not claimed:** reversing those substitutions and dropping the 20
inserted comment lines yields **0 differing lines** against the frozen T5b
launcher across all 215 body lines. No guard, refusal, cap arithmetic, timeout,
age-guard line or `STATUS` field was altered.

**PROVEN 2026-09-04 by `run_one_t5d.sh --drive-cap-kill`** — the same enforcement
line the solver runs under, driven against known children (`sleep`; **no solver
and no mesh**):

| arm | child | cap | wall | rc | outcome |
|---|---|---:|---:|---:|---|
| 1 | well-behaved `sleep 600` | 5 s | **5 s** | 124 | **STOPPED at the cap** by SIGTERM |
| 2 | **SIGTERM-ignoring** `sleep 600` | 5 s (grace 3 s) | **8 s** | 137 | **KILLED** by SIGKILL after the grace |
| 3 | `sleep 2` — the negative half | 30 s | 2 s | 0 | **untouched**, ran to completion |

`CAP-KILL PROOF PASS`. Arm 3 is not decoration: a killer that kills everything is
not a cap either.

**Three refusals driven, each exit 2, each leaving no `STATUS` file and no `0/`:**
a case directory that does not exist; a case with no row in `T5D_CAPS.txt`; and —
the one that matters — **an argv carrying T5b's cap `651.2` against T5d's
registered `38.6`, refused.** An argv cannot widen a T5d cap, and it cannot import
another rung's cap either.

Cost of this launcher proof: **0.25 core-minutes** (15 s wall at 1 rank), spent on
`sleep` children, on no registered case, producing no graded value.
USD 0.00021 **derived at $0.0513/core-h, not measured** — this box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 11. COST — rule 12, MEASURED basis, POINT and CAP

**The basis is T5b's own triple**, which is the ideal calibration: the **same cell
counts**, the same solver, the same `endTime`, the same ranks, on this box, **with
the repaired function objects already running**. From
`verification/runs/T-family/T5b_runs/STATUS.T5_CUBE_{c,m,f}` (all `rc = 0`,
`capped = 0`, `note = clean`):

| level | cells | wall s | **measured core-min** |
|---|---:|---:|---:|
| `c` | 52,684 | 1,007 | **16.783** |
| `m` | 212,942 | 5,252 | **87.533** |
| `f` | 882,024 | 20,851 | **347.517** |
| **total** | | | **451.833** |

**POINT = measured × 1.15.** The 15 % is an **ALLOWANCE for near-wall stiffening**
and it is **NOT measured**: T5d's first cell is `0.625 ×` T5b's at the **same cell
count**, so the near-wall aspect ratio rises ≈ 1.6 × (133–140 → ≈ 213–225) and the
near-wall growth ratios rise with it (§3.4), which can cost extra inner
linear-solver sweeps at a **fixed 5000 outer iterations**. This box holds no
measurement isolating first-layer thinning at fixed cell count, so the figure is
declared an allowance and not dressed up as a measurement. **The direction is
honest:** a finer near-wall mesh cannot be cheaper, so T5b's numbers are **not**
re-registered unchanged.

**T5b's separate 2 % function-object allowance is NOT carried**, because T5b's
**actuals already include** those field writes. Carrying it would double-count.

**CAP = 2.0 × POINT.** Contention headroom on a saturated box, not model
uncertainty; the POINT is a same-case measurement whose expected actual/predicted
ratio is ≈ 1.00 before the allowance. Corroborated: **T5b used 53.9 % of its cap**,
worst level `m` at 56.7 %. The cap is a runaway guard, never a target.

| level | **POINT core-min** | **CAP core-min** | derived timeout s at 1 rank |
|---|---:|---:|---:|
| `c` | **19.3** | **38.6** | 2,316 |
| `m` | **100.7** | **201.4** | 12,084 |
| `f` | **399.7** | **799.4** | 47,964 |
| **total** | **519.7** | **1,039.4** | — |

(Unrounded POINT total `519.608`; the registered rows sum to `519.7`. The timeout
is derived **by the launcher itself** as `int(cap × 60 / ranks)` — truncated, the
safe direction: a cap can only come out smaller than registered, never larger.)

**1,039.4 core-min = 17.323 core-hours. USD 0.4443 at the POINT and USD 0.8887 at
the CAP**, derived at the owner-stated **$0.0513/core-h** — **derived, not
measured**: the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
Under the $25 pre-authorisation by a factor of ≈ 28; **still costed, because a
blanket is not a per-item read** (rule 9).

**An overrun stops the run; it does not get a new budget** (rule 12). §10 proves
the mechanism.

**Estimate-versus-actual calibration** (rule 12, Sanaa 2026-08-23) will be filed as
a row in `docs/COST_CALIBRATION.md` at each level's completion, stating the
actual/predicted ratio, attributing the gap, and naming waste separately rather
than absorbing it into the ratio.

---

## 12. THE FREEZE SET

Frozen at this commit. The grading path is fixed here, and every file is verified
by hashing it against the committed blob before it is believed.

| file | role | blob at freeze |
|---|---|---|
| `docs/campaigns/T-family/T5d_PREREGISTRATION.md` | this document | — |
| `verification/runs/T-family/T5d_runs/build_t5d.py` | the builder — **the only new instrument** | `78074c7dad30` |
| `verification/runs/T-family/T5d_runs/run_one_t5d.sh` | the launcher, cap enforced and driven | `54be3a700f2b` |
| `verification/runs/T-family/T5d_runs/T5D_CAPS.txt` | the cap table the launcher checks against | `ef5fc334d981` |
| `verification/runs/T-family/T5b_runs/analyse_t5b.py` | **THE GRADING PATH — frozen, unchanged, unforked** | `552f7472f3ded7575256f877867cb076c6aab2e3` |
| `verification/runs/T-family/T5_runs/build_t5.py` | the frozen recipe this builder drives | `9d7be1cb9b5e206c9bccbe610f7b24427b7f8e99` |
| `verification/runs/T-family/T5b_runs/build_t5b.py` | the frozen patcher and digest constants reused verbatim | `af6c6ebf54f34bfefdb964bc5036ba30a0357203` |
| `verification/runs/T-family/T5_runs/T5_reference_primary.json` | the reference, unchanged and not re-digitised | `04dfd7e2e56adf1cd0924046500904af2243b747` |

Every blob above was read at HEAD by this lane with `git rev-parse HEAD:<path>`
and cross-checked against `git hash-object` of the working file; the reference
blob also matches the one `T5b_PREREGISTRATION.md` §6 and `T5b_RESULTS.md` §5
cite, which is the check that the reference did not move between the rungs.

**Rule 6: no frozen file was edited.** `T5_PREREGISTRATION.md`, `T5_RESULTS.md`,
`T5b_PREREGISTRATION.md`, `T5b_RESULTS.md`, `analyse_t5b.py`, `build_t5b.py`,
`build_t5.py`, `T5B_CAPS.txt`, `run_one_t5b.sh`, `T5c_PREREGISTRATION.md` and
`T5c_RESULTS.md` were **read only** to write this. Note that
`T5b_PREREGISTRATION.md` sits at HEAD blob `e403b11ff630`, not at its freeze blob
`e57ce5803f8a`, because AMENDMENT 1 was lawfully appended on 2026-09-03; that
append is a dated addendum that altered no gate.

**Rule 14** does not bite: no `libs` entry, no arms table and no level table in
any builder was replaced or edited. `build_t5.install_libs`, which carries the
rule-14 re-verification, is driven unchanged.

---

## 13. WHAT THIS RUNG CANNOT SEE

- **It does not re-open or re-grade T5, T5b or T5c.** T5b's `0 of 6 NOT A RESULT`
  stands and is correct. The successor supersedes; it does not overturn.
- **It does not cure the ratio-to-target drift** (§1.3, §6). It buys one ladder
  rung of headroom and says so.
- **Its `y+` predictions are first-order, not solved** (§4, P2).
- **It inherits every model-form limitation of T5 and T5b** (§2), the digitised
  reference and its band, and T5 §16.4's finding on the digitisation increment.
- **The comparator's author has read the reference values** — T5b §8.5's broken
  ordering is inherited in full and is not repaired by anything written here. The
  one auditable mitigation is inherited too and is enforced rather than promised:
  `--selftest` scans the comparator's own bytes for every reference `value`,
  `uncertainty` and `digitisation_increment` and **fails if one appears**.
- **It has not been built and has not run.** `N of M` is **`0 of 6`** until it
  has. A plan is not a capability.

---

## 14. STATUS

**FROZEN. NOTHING BUILT, NOTHING ARMED, NOTHING LAUNCHED.**
`verification/runs/T-family/T5d_runs/` holds the three frozen instrument files and
**no case directory, no `0/`, no `0.orig/` and no numeric time directory.**

The launch is the supervisor's §3 check-4 decision and is not taken by this
document.

**Nothing in this rung was sent, filed, uploaded, posted, registered or commented
outside this box (`CLAUDE.md` rule 7).**

---

## DATED ADDENDUM 1 — 2026-09-10, heat-transfer supervisor

*Appended at the foot of a FROZEN registration. **This addendum alters no gate,
threshold, band, cap or label.** It records facts discovered after the freeze and
one supervisor decision. **Lines whose number changed above this section: 0** —
asserted mechanically against the HEAD blob, not claimed.*

### 1. THE REGISTERED PRIOR IN §P4 RESTS ON A VERDICT THAT HAS BEEN WITHDRAWN

§P4 registers its prior as *"registered against this prediction, in advance,
rather than discovered afterwards"*, and the evidentiary work of that sentence is
the claim that T5c produced **one usable triple**: *"…with only `G2a` producing a
usable triple (GCI 4.355 %, `GATE FAIL` at 39.4023 against a reference 55.224 ±
5.66404)."*

**That verdict was withdrawn on 2026-09-10** (`T5c_RESULTS.md` AMENDMENT 1):
`G2a` is now **`NOT A RESULT`** and its **GCI is withdrawn**, because all three
T5 ladder levels fail **T5's own registered convergence criterion**
(`T5_PREREGISTRATION.md:469-472`) by **7,124× / 608,063× / 549,839×** — measured
on the same artifacts, supervisor-computed. **T5c therefore contains ZERO usable
triples, not one.** The registered prior does not merely go stale: **it inverts.**
P4's registered prediction and its falsifier are untouched and stand; what is
recorded here is that **the prior offered in their support no longer holds**.

### 2. AN INTERNAL CONTRADICTION, NOW VISIBLE BECAUSE THE VERDICT MOVED

Lines 111-112 of this document state: *"**T5d does not adopt T5c's statistic,
does not depend on T5c, and does not cite T5c's verdicts as support.**"* §P4 at
line 346 **does** cite T5c's verdict as support, in terms. Both sentences were
frozen together. The disclaimer is the one that fails. Recorded, not repaired —
neither line may be edited.

### 3. THE OPERATIONAL HAZARD — THIS RUNG IS REGISTERED TO REPRODUCE THE DEFECT

**§12 fixes T5d's grading path as the frozen `analyse_t5b.py`, blob
`552f7472f3ded7575256f877867cb076c6aab2e3`, byte-identical** (lines 369-372, and
the freeze table at line 676). **That file is the one that dropped registered
step 1 of its own six-step order and reused its number** —
`analyse_t5b.py:654` carries the docstring *"THE REGISTERED ORDER (T5 S7.5, rule
5), evaluated top to bottom"* while its step `(1)` at line 657 is the y+ gate and
the triple is at `(2)`. `T5_PREREGISTRATION.md:646` registers step 1 as *"any
ladder level NOT CONVERGED → `NOT A RESULT`"*, and §5.5 (466-472) registers its
instrument as a **checkpoint delta**, explicitly refusing the residual (*"L-141:
in T1c a genuinely unconverged case sat at residual 4e-05"*).

**So if T5d ever solves and is graded on its registered path, it reproduces
exactly the defect that produced the withdrawn `G2a`.** This is not a citation
problem; it is a live hazard in the rung's frozen instrument.

### 4. THE STATUS LINE AT LINE 4 IS STALE AS A MATTER OF FACT

Line 4 reads *"No T5d case has been built and no T5d case has run."* **The coarse
case IS built:** `verification/runs/T-family/T5d_runs/T5_CUBE_c/` carries
`log.blockMesh`, `log.topoSet`, `log.splitMeshRegions`, `log.checkMesh`,
`constant/` and `0.orig/`, dated 2026-09-04. There is **no `log.solve`**, so the
rung is **post-first-mesh-compute and pre-solve**. Recorded so that no reader
takes line 4 as current, and so the rule-2 boundary is not mistaken: **no solver
compute has occurred under this registration.**

### 5. DECISION — T5d REMAINS STOPPED [lab-attributed]

T5d was already stopped on 2026-09-10 when its own §"Named risks" pre-flight
condition fired (`checkMesh` on the built coarse mesh reporting other than `Mesh
OK`). That determinant finding was subsequently **diagnosed and cleared** — the
7,658 flagged cells are far-field extrusion, fully explained by an aspect-ratio
bar at AR 29.22 plus a boundary-face-exclusion artifact, with **zero** flagged
cells adjacent to the four cube patches. **T5d nonetheless remains stopped, for
the stronger reason in §3 above**: its frozen grading path cannot enforce rule 5
clause (1), and the ladder it would grade is measured non-convergent with **no
finite `endTime` that fixes it** (the medium's turbulence has collapsed — `k`
residual 8.033e-09 at iteration 500 and 8.032e-09 at 5,000, `bounding k, min: 0`;
the fine's `omega` swings eleven orders in a limit cycle).

**Condition to lift:** a grading path that enforces clause (1) by T5's own §5.5
criterion, and a ladder that can actually converge — which the measurements say
needs a **setup change** (turbulence initialisation / wall treatment;
`nNonOrthogonalCorrectors` is 0), i.e. **a new rung with its own registration and
budget, not an extension of this one.** A successor must not "repair" this
addendum away.

Three measured departures from §3.4 are recorded separately and remain owed as a
further dated amendment: built max aspect ratio **233.52** against §3.4's forecast
of ≈ 213-225; worst adjacent-cell size jump **9.375** against a registered 5.250
(the same measurement on T5b gives 5.859 against 2.906, so the method
under-predicts ~2× where it can be checked); and **18 flagged floor and 18
flagged roof cells inside the cube neighbourhood where T5b had zero.**

— heat-transfer supervisor, 2026-09-10, [lab-attributed]
