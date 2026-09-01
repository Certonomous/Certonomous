# F28G — DUCTED ACTUATOR DISK: REGENERATED MESH LADDER AND GRID-CONVERGENCE STUDY — PRE-REGISTRATION

**Version 1.0. Status: FROZEN at the commit that introduces this file.**

Team: `cfd`. Lane: `lab-lane` under `cfd-supervisor`.
Parent (frozen, not altered by this document):
`verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`.

---

## 0. WHAT THIS DOCUMENT IS, AND WHAT IT IS NOT

This registers **the regenerated three-level mesh ladder** and **the grid-convergence
study at `delta_p = 1000 Pa`, `U_inf = 20 m/s`** ordered by Sanaa on 2026-09-01
(`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`, commit
`f4c8e466`, §0 and §4).

**It alters no gate, threshold, cap or label of the parent registration.** The parent's
§9.3 Roache gate on `T_total` (`p` in [1.3, 2.5]`, `GCI_fine < 3 %`, `Fs = 1.25`), its
§8 numerics and convergence criteria, its §9.4 theory gate and its §6 controls are
carried **unchanged and by reference**. The parent had already taken first compute, so
its gates are closed; this document adds a **mesh-admission gate that did not previously
exist** and registers the ladder the parent's §5 describes, rebuilt. Where this document
and the parent differ on a mesh quantity, **the parent's §5 mesh requirements are
superseded only in the direction of being stricter**, and every such change is named in
§4 below.

Sanaa's §4, verbatim:

> - Fix the generator: cap the cell-to-cell volume growth at 1.25 everywhere,
>   especially at the duct trailing edge; regenerate the three levels from
>   the fixed script (similarity now guaranteed); confirm with a cell-volume
>   ratio histogram before solving.
> - Absolute floor beside the relative stationarity criterion is approved and
>   landed; run the map; convergence study at (1000 Pa, 20 m/s).

---

## 1. REGISTER SEARCH BEFORE FREEZE (L-427) — WHAT WAS SEARCHED AND WHAT IT RETURNED

Searched **before** this file was written, over `docs/NUMERICS_KNOWLEDGE.md`,
`docs/LESSONS.md` and `verification/campaign/`, for: `F28`, `ducted`, `volume jump`,
`volume ratio`, `cell volume`, `mesh similar`, `similar family`, `refinement ratio`,
`volume growth`, `expansion ratio`, `Richardson`, `extrapolation`, `aspect ratio`.

**Returned — and each is applied below, not merely cited:**

| entry | what it says | where it is applied here |
|---|---|---|
| **N-C7** | F28's own `fvOptions` `volumeMode` hazard | parent §2.4; unchanged, carried by reference |
| **N-T1** | the shared `gci()` prints the Richardson extrapolate with the **wrong sign on every row** | §7 — the comparator does not use the shared `gci()`'s extrapolate |
| **N-T8** | the Richardson **sign** defect in **four independently written** implementations; invisible to both `p` and `GCI` because both are sign-independent; standing rule: a **value-checking** synthetic-power-law selftest, 1e-12 relative, not a key-presence check | §7 — **adopted verbatim as a registered refusal**, with the free `frozen + corrected == 2 f_fine` identity asserted as well |
| **N-T2** | a `CONVERGING` triple can arm a band **narrower than the fine level's actual error** | §7 — the band is reported with this caveat attached, never as an error bound |
| **N-T7** | a `CONVERGING` triple is a **step-ratio test**; a fine-level deviation smaller than the coarse-to-fine drift passes on a divergent triple | §7 — registered as a disclosure on the triple |
| **N-X1** | a continuity tolerance must be **calibrated** before registration | §7 — the parent's `1e-8` is carried unchanged and is **not** re-derived here |
| **L-142** | `blockMesh` grades from the block's **low face**, so on an **axis-to-wall** block a `simpleGrading` above one puts the **finest cell on the centreline** | **§5.4 — this ladder HAS that property, it is MEASURED, and it is REFERRED, not repaired** |
| **L-130** | a gate's band is part of its referent | §6, §7 — every threshold names its authorising clause |
| **L-132** | amend the run, never the ruling | §0 |
| **L-173** | re-run the generator and diff the artefact; generated prose is not regenerated | §5.1 — the generator's own header carries the sweep table, regenerated with it |
| **L-427** | search the registers **before** the freeze | this section |
| **MESH_STANDARD §8.1** | **BUILD BEFORE YOU FREEZE** — no cfd ladder registration is frozen until a level is built, `checkMesh`'d and **shown admissible against the gates that registration will carry** | §5, §6 — **all three** levels are built and checked below, before this freeze |
| **MESH_STANDARD §9.2** | similarity clause; **read back the ACHIEVED grading**, never the requested one | §5.3 |
| **MESH_STANDARD §11.4, §12.9** | aspect ratio and cell-volume ratio are **reported** mesh-admission evidence and **NO THRESHOLD IS SET** for either; "§11 rejects no mesh" | §6 — this is why the volume-ratio gate below is **case-level and Sanaa-set**, and is **not** claimed as an application of the standard |
| **MESH_STANDARD §12.3** | a mesh with negative/zero/unprinted min volume is recorded with a status, **counted in the census, never dropped**, excluded from ratio percentiles with the exclusion reported as a number | §6.3 |
| **MESH_STANDARD §14.4** | the non-orthogonality gate is read off the **reported maximum**, never off `Non-orthogonality check OK.` and never off `Mesh OK.` / `Failed N mesh checks.` | §6.1 — **and the closing line is explicitly disregarded below, where it reads `Failed 2 mesh checks` on an admissible mesh** |
| **MESH_STANDARD §3.3** | aspect ratio: **advisory at 1000, never a lone rejection**; the lab's own reference-grade NASA TMR grids measure 66,643–74,041 | §6.2 — aspect ratio is **RECORDED AND NEVER GATED** here |

**Searched and returned NOTHING:** no register entry, lesson or campaign record was
found on (a) the cell-volume ratio of an **axisymmetric wedge** and its behaviour at the
axis, (b) a **body apex terminating on the axis** as a source of face-adjacent volume
jump, or (c) a **level-covariant law for a mesh growth cap**. §5.2 and §6.4 are
therefore new ground, and are written to be falsified rather than trusted.

---

## 2. THE MEASUREMENT THAT MOTIVATES THIS DOCUMENT, AND THE ONE CLAIM IT FALSIFIES

**The parent's Addendum 2 §2 names, among the candidate causes of the non-converging
feasibility arms, "the residual face-adjacent volume jump of 33.5 **located at the duct
trailing edge x ≈ 0.1992 — the same patch whose integrated force is the noisy
quantity**". THE AXIAL LOCATION IS RIGHT AND THE RADIAL LOCATION MAKES THE CLAIM FALSE,
AND IT IS STRUCK HERE.**

Measured per-face on the superseded L1 mesh, from `owner`/`neighbour`/`cellVolume`
through a reader carrying a planted control and its negative limb
(`cases/F28_DUCTED_ACTUATOR_DISK/f28_face_volume_ratio.py`):

- the 33.4911 jump is the **AXIAL** face between `(x = 0.199217, r = 3.00041e-04)` and
  `(x = 0.2006, r = 8.94199e-06)`. Both cells are **on the axis**;
- the graded quantity is the integrated force on the **duct**, at `r ≈ 0.125–0.140`.
  Over the whole duct-surface neighbourhood (`0 <= x <= 0.2`, `0.10 <= r <= 0.16`,
  10,536 faces) the superseded L1 mesh measures **max 2.43687, p99 1.3842,
  p99.9 1.5277, and ZERO faces above 3.0**;
- **`r = 0.125` and `r = 3.0e-04` are 400 radii apart.** The jump and the noisy quantity
  are not co-located, and the volume of the cells carrying the jump is `3.16e-13 m^3`.

**Mechanism, derived and then confirmed to three significant figures.** The centrebody
**tail cone** is a STRAIGHT cone (parent §7.1) terminating on the axis at `x = L_DUCT`,
the same axial station as the duct trailing edge. On a wedge the sector volume is
`V = (theta/2)(r_{j+1}^2 - r_j^2) dx`, so the innermost cell just upstream of the apex
has `V ~ (2 r_hub h + h^2) dx` and its downstream neighbour, past the apex, has
`V ~ h^2 dx`. The ratio is `1 + 2 r_hub(x_c)/h`. With `r_hub = 2.94e-04` and
`h = 1.79e-05`: **33.9 predicted against 33.4911 measured.**

**The nose apex is benign and the asymmetry is the whole of it:** the nose is a `C1`
smoothstep with **zero** slope at its apex (`r ~ x^2`), the tail cone's slope at its
apex is **0.375**.

**Consequence for the record:** the mesh-conditioning hypothesis for the noisy duct force
is **weakened, not refuted** — the 33.5 jump is removed by this rebuild (§5.2) and the
force noise can now be re-measured against a mesh that does not carry it. **Nothing here
establishes a cause.** The parent's other candidates — the axis-column aspect ratio, the
farfield pressure anchoring, the wedge non-planarity, the relaxation, and above all the
**`p` residual that did not move in 15,000 iterations** — are untouched by this document.

---

## 3. THE THRESHOLD IN SANAA'S §4 IS NOT ATTAINABLE AS WRITTEN, AND THE PROOF IS GEOMETRIC

**Registered here BEFORE the gate is written, because a gate no admissible mesh can pass
is the failure mode this lab has already paid for once** (`MESH_STANDARD` §3.3: a hard
aspect-ratio gate at 1000 "would reject every reference-grade wall-resolved RANS grid the
lab owns").

On an axisymmetric wedge whose mesh includes cells touching the axis, the first internal
**radial** face separates a cell spanning `[0, h_1]` from one spanning `[h_1, h_1 + h_2]`.
Their sector volumes are `(theta/2) h_1^2 dx` and `(theta/2)((h_1+h_2)^2 - h_1^2) dx`, so
with `q = h_2/h_1` the face-adjacent volume ratio is **exactly**

    (1 + q)^2 - 1

For any **non-contracting** radial distribution (`q >= 1`) this is **>= 3.0 exactly**, and
`3.0` is attained only by a uniform spacing. Requiring `<= 1.25` forces `(1+q)^2 <= 2.25`,
i.e. `q <= 0.5`: **the second radial cell must be at most HALF the first, and the
requirement compounds outward** — a distribution that refines toward the farfield, which
is incompatible with any wall-resolved or farfield-stretched mesh.

**MEASURED against the prediction**, superseded L1, axis band (`r <= 4 x` the smallest
cell-centre radius, 307 faces): **100 % above 2.0**, max **4.27417**, which back-solves to
`q = 1.296` — the row's actual expansion ratio.

> **A cell-to-cell VOLUME growth cap of 1.25 "everywhere" is mathematically unattainable
> on this topology. This is a property of axisymmetric wedges, not of this generator.**

**What is therefore registered instead, and it is not a softening:** Sanaa's 1.25 is
applied **in full** to the quantity a mesh generator actually controls — the **LINEAR
cell-size growth**, per cell within every segment and across every segment junction, in
every direction, at every level. On a wedge the face-adjacent volume ratio **equals** that
linear ratio for **axial** neighbours (same `r`, same `dr`) and differs from it for
**radial** ones by the `r`-weighting above. **The 1.25 number is Sanaa's and is not moved.
Its referent is stated, because a threshold without a stated referent is not a gate**
(L-130).

**This limitation is referred to Sanaa's desk.** Only she may set or retire a threshold.
Nothing in this document treats her §4 sentence as satisfied by the volume ratio; §6.4
reports the volume ratio against the geometric floor and gates nothing on it.

---

## 4. WHAT CHANGED IN THE GENERATOR — `case/mesh/make_mesh.py`

Superseded sha256 `c27bcd73903c5d0dedb3530eb1cc705914adcccdda1db080b0871da623fbac89`
(HEAD at `55c4db56`).
**Frozen sha256 for this ladder: recorded in §9 and in every birth certificate.**

Four repairs. Two of them are the **same defect class the jet-flap lane met
independently on `build_jf1.py`: A PARAMETER HELD CONSTANT ACROSS A FAMILY SILENTLY
MAKES THE FAMILY DISSIMILAR.**

### 4.1 A FIXED GROWTH CAP IS A SIMILARITY DEFECT — the law is the `1/s` exponent

`MAX_GROWTH` was a fixed `1.36` at every level. A geometric segment of `n` cells with
per-cell ratio `q` has total expansion `q^(n-1)`; similarity requires the **total**
expansion of a column to be invariant while `n` scales as `s`, so **`q` must scale as
`q^(1/s)`**. A fixed cap binds at the coarse level and goes slack at the fine one.

**MEASURED on the superseded ladder, read back from the generator, not assumed:** column
`c1`'s per-cell ratio reached **1.35647** against the 1.36 cap at L1, forcing a split
whose internal junction jump was **3.6494**; at L2 and L3 the cap did not bind and the
same junction read **0.9892** and **1.0003**. **A 3.65x size discontinuity present at one
level of three is `MESH_STANDARD` §9.2's branch flip, and the fixed cap caused it.**

Repaired: `MAX_GROWTH = 1.25` at L1, and `growth_caps(level)` returns
`1.25 ** (1/s)` — **1.25000 / 1.16040 / 1.10426** at L1/L2/L3.

*The jet-flap lane's law for a fixed smoothing-pass count was `s^2`, because diffusion
length goes as `sqrt(passes)`. Here it is the `1/s` exponent, because expansion compounds
per cell. Same class, different exponent; the exponent must be derived from the
mechanism each time.*

### 4.2 THE JUNCTION JUMP WAS MINIMISED AND NEVER CAPPED

`distribution()` scored candidate splits by `|log(junction_jump)|` and took the best
available. **A minimum is not a bound.** A `MAX_JUNCTION` cap of 1.25 at L1, scaled by
the same `1/s` law, is now a **refusal**: an inadmissible split is rejected by the search,
and if none is admissible the generator refuses outright rather than returning the least
bad one.

### 4.3 THE SPLIT WAS RE-SEARCHED AT EVERY LEVEL, ON AN OBJECTIVE THAT IS NOT LEVEL-COVARIANT

The discrete search over `(n1, f)` ran independently at each level, so the ladder's three
meshes had **different distribution shapes**. Read back from the superseded generator
(`MESH_STANDARD` §9.2 requires the achieved value):

| distribution | `length_fraction` L1 / L2 / L3 | `junction_jump` L1 / L2 / L3 |
|---|---|---|
| `c1` | 0.81 / 0.56 / 0.45 | **3.6494** / 0.9892 / 1.0003 |
| `c2` | 0.32 / 0.28 / **0.75** | 1.0003 / 0.9930 / 1.0016 |
| `c5` | 0.64 / **0.21** / 0.55 | 1.0012 / 1.0002 / 1.0088 |
| `c6` | 0.43 / 0.76 / **0.13** | 0.9995 / 1.0010 / 1.0001 |
| `ROW_I` | 0.44 / 0.39 / **0.69**, and `q1`,`q2` **swap** which segment is the steeper | 1.0021 / 1.0000 / 0.9988 |

Repaired: the split is chosen **once, at L1**, and inherited. **What is inherited is
`(alpha, rho)`, not `(alpha, f)`**, where `alpha = n1/n` and `rho = f/(n1/n)` — segment
1's mean cell size divided by the column's. `f` is **reconstructed** as `rho * n1/n` at
each level. Inheriting `f` directly is wrong because `n1` must be rounded to an integer,
which moves `n1/n` while leaving `f` fixed: measured while building this repair, the
uniform disk column `c4` (`rho = 1`) then demanded a per-cell ratio of **0.5** at L2, and
the cap correctly refused it. A level that cannot honour L1's shape **refuses**; it does
not re-search.

### 4.4 A FIXED POLYLINE RESOLUTION — A LATENT TRAP THAT ARMS ITSELF AT THE ESCALATION SANAA'S OWN DOCTRINE PRESCRIBES

Every curved wall edge (`r_hub`, `r_in`, `r_out`, `cprime_in`, `cprime_out`) was written
as a `polyLine` of **80 segments at every level**. A fixed segment count represents the
wall to a **fixed** geometric accuracy, so once a column carries more than ~80 cells the
wall's discretisation error stops improving under refinement and becomes a
**level-independent error term inside the graded quantity** — the integrated duct force —
which is precisely the term an observed-order study assumes is absent.

**ON THE SUPERSEDED THREE LEVELS THIS DEFECT DID NOT FIRE**: the largest curved column
carried **66** cells at L3, under 80. **It fires on the FOURTH level Sanaa's §0 step 4(c)
prescribes adding**, where `c5` reaches **121** cells. Stated as a negative because a
latent defect reported as an active one is a false claim.

Repaired: `npts` is a **required argument with no default** (`CLAUDE.md` rule 14 — a
lesson is not applied until every call site asserts it), supplied as
`max(80, 8 * n_cells)`, and the generator refuses a call that omits it.

### 4.5 The tail-apex spacing, and why the target is 1.50 and not 1.25

The apex ratio of §2 is `r`-weighting, not linear growth, so §3 governs it. It is reduced
by prescribing the axial spacing at `x = L_DUCT` from the geometry:
`dx <= (target - 1) * h_axis / TAIL_SLOPE`.

**Target 1.25 was BUILT AND CHECKED and is rejected on measurement.** It drove L1 max
non-orthogonality to **66.1068** — over this case's registered **65** gate — on exactly
**two** cells at `x = 0.199996/0.200004, r = 0.28356`, by the tilt mechanism the
generator's own header documents at 84.62°: a very thin axial column inside a tall block
whose lower edge is the curved `C'_outer`. A sweep at L1, **every arm built and
`checkMesh`'d**:

| apex target | cells | max non-ortho | max skewness |
|---|---|---|---|
| **1.25** | 35,544 | **66.1068** | 1.24132 |
| 1.50 | 35,544 | **57.8773** | 1.24132 |
| 2.00 | 35,544 | 57.8773 | 1.24132 |
| 2.50 | 35,544 | 57.8773 | 1.24132 |
| 3.00 | 35,544 | 57.8773 | 1.24132 |
| 4.00 | 35,544 | 57.8773 | 1.24132 |

**The excursion exists at 1.25 and nowhere else, and the cell count is identical across
the whole sweep.** `APEX_VOL_TARGET = 1.50` is taken: it removes the 33.5x jump, it sits
**below the irreducible axis floor of 3.0** so the apex is no longer the mesh's dominant
volume-ratio feature at any target in this range, and it restores max non-orthogonality
to the value the rest of the ladder carries. **No gate is relaxed by this**: 1.25 remains
the cap on linear growth and is met at every level.

### 4.6 Counts raised so the caps are ADMISSIBLE rather than aspirational

Minimum admissible counts **measured** at L1 under the 1.25 caps, then set with margin.
`ROW_I` 44 -> **48** (min 46); `ROW_O1` 20 -> **22** (min 21); `c1` 18 -> **24** (min 23);
`c5` 36 -> **48** (min 46 with the apex spacing). **Every other row and column is
UNCHANGED, stated because "unchanged" is a result.** Raising a count is the honest
response to a tightened cap; slackening the cap would have been choosing the gate to fit
the mesh.

### 4.7 Refinement ratio raised to `r = 1.5`

Sanaa's §0 step 1 requires `r` in **[1.5, 2.0]** in every direction, with 1.3 as the
floor. The superseded ladder ran at **1.3540 / 1.3484** — above the floor, below the
band. `R_LADDER = 1.5`, applied to **every** direction. `LEVEL_SCALE` now also defines
**L4** (`1.5^3`), because a ladder that cannot express its own escalation will be
hand-edited under time pressure.

---

## 5. THE REBUILT LADDER — BUILT AND CHECKED BEFORE THIS FREEZE (MESH_STANDARD §8.1)

All three levels built with `blockMesh` and checked with
`checkMesh -allGeometry -allTopology -writeAllFields`, OpenFOAM **v2606**, artifacts at
`verification/runs/F28_runs/mesh_A4/L{1,2,3}/`.

### 5.1 Counts and per-direction refinement ratios

| | L1 | L2 | L3 | `r(L2/L1)` | `r(L3/L2)` |
|---|---|---|---|---|---|
| **cells** | **35,544** | **79,974** | **180,256** | **1.5000** | **1.5013** |

Per-direction (the check the jet-flap lane's `--n-rad 0` defect makes mandatory — there,
one direction refined at 1.02 while another refined at 1.5):

| direction | L1 | L2 | L3 | r21 | r32 |
|---|---|---|---|---|---|
| `nr I` | 48 | 72 | 108 | 1.5000 | 1.5000 |
| `nr BI` / `BO` | 22 | 33 | 50 | 1.5000 | 1.5152 |
| `nr O1` | 22 | 33 | 50 | 1.5000 | 1.5152 |
| `nr O2` | 26 | 39 | 58 | 1.5000 | 1.4872 |
| `nx c0` | 40 | 60 | 90 | 1.5000 | 1.5000 |
| `nx c1` | 24 | 36 | 54 | 1.5000 | 1.5000 |
| `nx c2` | 28 | 42 | 63 | 1.5000 | 1.5000 |
| `nx c3` | 18 | 27 | 40 | 1.5000 | 1.4815 |
| `nx c4` | 4 | 6 | 9 | 1.5000 | 1.5000 |
| `nx c5` | 48 | 72 | 108 | 1.5000 | 1.5000 |
| `nx c6` | 70 | 105 | 158 | 1.5000 | 1.5048 |
| `nx c7` | 42 | 63 | 94 | 1.5000 | 1.4921 |
| `y_first` [m] | 1.000e-05 | 6.667e-06 | 4.444e-06 | 1.5000 | 1.5000 |

**Every direction refines at 1.5 to within integer rounding; the full spread is
1.4815–1.5152, i.e. `-1.2 % / +1.0 %`.** The superseded ladder's spread was
1.2500–1.4000 on the same measure.

### 5.2 `checkMesh`, read per `MESH_STANDARD` §14.4 off the reported maximum

| quantity | L1 | L2 | L3 | authority | verdict |
|---|---|---|---|---|---|
| max non-orthogonality | **57.8773** | **57.9264** | **57.9612** | §3.1 hard gate 70; this case's registered 65 | **PASS** |
| max skewness | **1.24132** | **1.27269** | **1.27751** | §3.2 hard gate 4 | **PASS** |
| negative cell volumes | **0** | **0** | **0** | parent §5 | **PASS** |
| min cell volume [m^3] | 1.40612e-16 | 4.16627e-17 | 1.23445e-17 | §12.3 status: all three **POSITIVE**, none excluded from any percentile | recorded |
| max aspect ratio | 53,458.4 | 53,834.0 | 54,483.4 | §3.3 **advisory, never a lone rejection**; NASA TMR references 66,643–74,041 | **RECORDED, NOT GATED** |

**Max non-orthogonality is invariant across the family to 0.145 %** (57.8773 / 57.9264 /
57.9612) — the invariance the jet-flap lane's `s^2` smoothing law was needed to obtain
there, obtained here by construction.

**`checkMesh`'s closing line reads `Failed 2 mesh checks.` on all three levels and IS
DISREGARDED, per `MESH_STANDARD` §14.4.** The two flagged checks are high aspect ratio
(§3.3 advisory) and small cell determinant (§3.5 **informational, not gated**). **A
like-for-like control was run rather than inferred:** the superseded L1 mesh was
re-checked under the same `-allGeometry` flag and **also** reports `Failed 2 mesh checks`,
with **8,729 of 31,752 cells (27.49 %)** carrying a small determinant against the rebuilt
L1's **9,817 of 35,544 (27.62 %)** — a difference of **0.13 percentage points**.
**There is no regression; the earlier log simply never ran the determinant check**, and
the count difference is population size, not mesh quality. Rebuilt L2 and L3 read
22,002 of 79,974 (27.51 %) and 49,430 of 180,256 (27.42 %) — **the fraction is invariant
across the family**, which is the reading that matters for a Roache ladder.

### 5.3 SIMILARITY READ-BACK (`MESH_STANDARD` §9.2) — achieved values, never requested ones

| distribution | `rho` L1/L2/L3 | `junction_jump` L1/L2/L3 | `q1` L1/L2/L3 |
|---|---|---|---|
| `ROW_I` | 0.73500 / 0.73500 / 0.73500 | 0.9945 / 1.0108 / 1.0174 | 1.24115 / 1.15386 / 1.09967 |
| `c1` | 1.06000 (all) | 1.0281 / 1.0242 / 1.0216 | 1.20810 / 1.13116 / 1.08435 |
| `c2` | 0.68923 (all) | 1.0003 / 0.9942 / 1.0274 | 1.17786 / 1.10972 / 1.07350 |
| `c3` | 0.99000 (all) | 0.9939 / 0.9927 / 0.9923 | 1.11569 / 1.07332 / 1.04952 |
| `c4` | 1.00000 (all) | 1.0000 (all) | 1.00000 (all, exactly uniform) |
| `c5` | 1.00174 (all) | 1.0012 / 0.9947 / 0.9923 | 1.08526 / 1.05625 / 1.03613 |
| `c6` | 0.65435 (all) | 0.9995 / 1.0070 / 1.0101 | 1.08217 / 1.05378 / 1.03521 |

**Every junction jump lies in [0.992, 1.028] at every level**, against the superseded
ladder's 3.6494 at L1. **The `1/s` law is confirmed empirically, not assumed:**
`ROW_I` `q1` reads 1.24115 / 1.15386 / 1.09967 against `1.24115^(1/1.5) = 1.1554` and
`1.24115^(1/2.25) = 1.1017`.

### 5.4 L-142 — A PROPERTY OF THIS LADDER, MEASURED, AND REFERRED RATHER THAN REPAIRED

`blockMesh` grades from a block's **low** face. In the **wake** columns `c6`/`c7`, row
`I` spans `r = 0` to `cprime_in(L_DUCT)`, and it inherits the **normalised** radial
grading solved for the **hub-to-`C'`** row, whose fine end is at the **hub wall**. In the
wake the low face is the **axis**, so **the ladder's finest radial cell downstream of the
centrebody sits on the centreline, where there is no boundary layer to resolve.**

This is exactly L-142's shape and it is the root of two reported numbers: the max aspect
ratio (**53,458 at `x = 6.27, r = 8.94e-06`** — on the axis, far downstream) and the axis
volume-ratio floor of §6.4.

**It is NOT repaired here.** Reversing the wake row's grading changes the recipe shared
with the duct columns and would need its own registration and its own build-before-freeze.
**It is registered as a known property of this ladder, it is common to all three levels,
and it is therefore common-mode in the Roache triple.** It is **referred** to the
supervisor as a candidate successor item.

---

## 6. THE MESH-ADMISSION GATE — REGISTERED, WITH EACH THRESHOLD'S AUTHORITY NAMED

**A level failing any clause of §6.1 is `NOT A RESULT` and NO SOLVE IS LAUNCHED ON IT.**

### 6.1 GATED — REJECTIONS, and each is one the standard permits as a rejection

| # | quantity | threshold | authority |
|---|---|---|---|
| M1 | max non-orthogonality, read off `Mesh non-orthogonality Max:` | **< 65** | parent §5 (stricter than `MESH_STANDARD` §3.1's hard gate of 70) |
| M2 | max skewness | **< 4** | `MESH_STANDARD` §3.2 hard gate |
| M3 | negative cell volumes | **zero** | parent §5 |
| M4 | **linear cell-size growth**, per cell within every segment **and** across every segment junction, every direction | **<= 1.25 ** at L1, `1.25^(1/s)` at level `s` | **Sanaa 2026-09-01 §4**, referent stated in §3. Enforced as a generator **refusal**, so an inadmissible mesh is never built |
| M5 | per-direction refinement ratio | **1.5 +/- 5 %** in every direction | Sanaa §0 step 1 |
| M6 | similarity read-back: `rho` identical across levels; every junction jump in **[0.95, 1.05]** at every level | | `MESH_STANDARD` §9.2 |

**M1 is read off the reported maximum and the severe-face count beside it, NEVER off
`Non-orthogonality check OK.` and NEVER off `Mesh OK.` / `Failed N mesh checks.`**
(`MESH_STANDARD` §14.4). Any comparator that greps a verdict string is reading the wrong
instrument and its clean result is not evidence.

### 6.2 RECORDED AND EXPLICITLY NOT GATED

**Max aspect ratio.** `MESH_STANDARD` §3.3 makes it **advisory at 1000 and never a lone
rejection**; §11.4 states that **no value of it makes a mesh inadmissible** and that what
makes a record incomplete is the **absence** of the number, never its size. This ladder
measures **53,458 / 53,834 / 54,483**, below the lab's own reference-grade NASA TMR
calibration of 66,643–74,041. **It is recorded in every birth certificate and gates
nothing.** Also recorded and not gated: whole-mesh cell-volume ratio (§11.4), cell
determinant and face interpolation weight (§3.5).

### 6.3 THE CENSUS RULE (`MESH_STANDARD` §12.3)

A level whose minimum cell volume is negative, zero or unprinted is recorded with an
explicit status (`MIN_NEGATIVE` / `MIN_ZERO` / `MIN_VOLUME_LINE_ABSENT`), carries its
value and its negative-cell count, **is counted in the census and never dropped**, and is
excluded from ratio percentiles **with the exclusion reported as a number beside them**.
**On this ladder all three minima are positive and the exclusion count is 0 at every
level.**

### 6.4 THE VOLUME-RATIO HISTOGRAM — REPORTED AGAINST ITS GEOMETRIC FLOOR, GATING NOTHING

Sanaa's §4 requires the histogram **before solving**; §3 establishes that no threshold on
it is attainable, and `MESH_STANDARD` §11.4/§12.9 set none. **It is therefore a REQUIRED
REPORT and NOT A GATE**, and a record lacking it is incomplete.

Measured per-face on the three rebuilt levels, planted control and negative limb passing
on each (`f28_face_volume_ratio.py`):

| population | L1 | L2 | L3 |
|---|---|---|---|
| **AXIAL max** (the generator-controlled direction) | **2.40069** | **1.95148** | **1.84218** |
| axial p99 / p99.9 | 1.4394 / 1.7549 | 1.2740 / 1.4758 | 1.1759 / 1.2990 |
| **axial faces > 3.0** | **0** | **0** | **0** |
| OFF-AXIS max (all directions) | 2.44445 | 2.46224 | 2.47404 |
| off-axis faces > 3.0 | 0 | 0 | 0 |
| **AXIS-BAND max** (the `(1+q)^2 - 1` floor of §3) | 4.02275 | 3.63911 | 3.40862 |
| axis-band faces, counted not dropped | 314 | 467 | 697 |
| **DUCT-SURFACE max** (the graded patch) | **2.44445** | **2.46224** | **2.47404** |
| duct p99 / p99.9 | 1.3678 / 1.5262 | 1.2412 / 1.3374 | 1.1585 / 1.3299 |
| duct faces > 3.0 | 0 | 0 | 0 |

**Superseded ladder, same reader, same populations: AXIAL max 33.4911 / 33.5288 /
33.5488 and 87 axial faces above 3.0 at L1.** The 33.5 jump is **eliminated at every
level**, the axial maximum now **decreases under refinement**, and the mesh's overall
maximum is the irreducible axis floor of §3, approaching 3.0 from above exactly as the
algebra predicts.

The off-axis maximum is the **duct lip highlight** at `x ~ 0.001, r ~ 0.1345` — a
curvature feature of the blunt lip, invariant across the family at 2.444 / 2.462 / 2.474,
**not** a grading choice.

---

## 7. THE GRID-CONVERGENCE STUDY — GATES

At `delta_p = 1000 Pa`, `U_inf = 20 m/s`, `sigma = 1.0`, on L1/L2/L3 of §5.

**Every gate below is the parent's, carried unchanged and by reference:** graded quantity
`T_total`; `Fs = 1.25`; observed order `p` in **[1.3, 2.5]**; **`GCI_fine < 3 %`**;
rule-5 ordering exactly as parent §9.3 states it, one-way, the gate able to turn a `PASS`
or `GATE FAIL` **into** `NOT A RESULT` and never the reverse; no GCI quoted when the
three values are not monotone. Numerics, residual and stationarity criteria, the 15,000
iteration cap and the `HIT CAP -> NOT A RESULT` rule are the parent's §8, including
Addendum 3's absolute stationarity floor.

**Registered additions, none of which move a parent threshold:**

1. **RICHARDSON SIGN — N-T8's standing rule is adopted as a refusal.** The comparator's
   `--selftest` carries a **value-checking** control: a synthetic power-law triple
   `f_k = f_ex + A (r^p)^k` whose limit is known by construction, asserted to **1e-12
   relative**. A key-presence check is registered as **insufficient** — it is what let the
   defect survive every run of `analyse_t1c.py` and `analyse_t3.py`. The free identity
   `frozen + corrected == 2 * f_fine` is asserted on the real triple as well. **The shared
   `gci()`'s Richardson extrapolate (N-T1) is not used.**
2. **N-T2 caveat, attached to the number, not to a footnote:** a `CONVERGING` triple can
   arm a band narrower than the finest level's actual error. The GCI is reported as a
   grid-convergence index, **never as an error bar on the physics**.
3. **N-T7 disclosure:** a `CONVERGING` triple is a step-ratio test; if the fine-level
   deviation is smaller than the coarse-to-fine drift, that is stated beside the verdict.
4. **Sanaa §0 step 2 — the iterative-versus-discretisation ratio is a REGISTERED
   PRECONDITION, not a diagnostic:** the iterative change in `T_total` over the
   stationarity window must be **at least 10x smaller** than the difference between
   consecutive mesh levels, **on every level**. Failing it, the observed order is noise
   and the row is **`NOT A RESULT`** — registered in those words, before any solve.
5. **Sanaa §0 step 4 escalation, pre-authorised here so it needs no new freeze:** if `p`
   falls outside [1.3, 2.5], the lane (a) re-checks clause 4 on the finest level, (b)
   re-reads the §5.3 similarity table, (c) builds **L4** at the same `r = 1.5`
   (404,632 cells, already expressible — §4.7) and recomputes `p` on the finest three,
   (d) repeats once more at L5 if needed. **This escalation may not alter any gate,
   threshold, cap or label**; it may only add levels.
6. **`y+` is recorded on every level** and the parent's `y+ <= 1` requirement is
   unchanged. **`y+` values in the birth certificates are ESTIMATES until a solve returns;
   they are labelled as such** (parent Addendum 1 §A1.7).

---

## 8. COST — core-minutes, with the cap registered BEFORE the runs

**Rule 12 costing duty stands whether or not a ceiling binds.** Sanaa's "cost is not a
constraint" removes the ceiling as a blocker; it does not remove the costing.

**Mesh stage — ACTUAL, measured, already spent.** All serial, `ranks = 1`. Generate +
`blockMesh` + `checkMesh -allGeometry -allTopology -writeAllFields`, timed end to end on
this box: **L1 3.5 s, L2 5.7 s, L3 8.3 s = 17.5 s** for one ladder, i.e. **0.29
core-minutes**. Four ladders were built (`mesh_A2`, `mesh_A3`, `mesh_A4`, plus the
superseded-mesh re-check) and six single-level sweep arms of §4.5, so the whole mesh
stage is **at most 6 core-minutes**, dominated by generator development rather than by
compute. Registered as **6 core-min** for the calibration row, stated as an upper bound
rather than a point measurement, because the sweep arms were not individually timed.

**Solve stage — REGISTERED CAP: 900 core-minutes for the three-level triple.**

Basis, and the basis is a **warning carried from the jet-flap lane, not an assumption**:
**cost per cell per iteration is NOT constant.** That lane measured **4.27e-6 s** per cell
per iteration at 39,984 cells against **7.79e-6 s** at 89,964 — **1.82x worse per cell at
2.25x the cells.** A cap built by scaling a coarse-level rate linearly under-caps the fine
level and stops it mid-run. The cap below therefore uses a **super-linear** rate model,
`t_cell ~ N^0.55` fitted to those two points (`log(1.82)/log(2.25) = 0.548`), anchored at
this case's own L1:

| level | cells | anchored `t_cell` [s] | iterations | wall [s] | ranks | core-min |
|---|---|---|---|---|---|---|
| L1 | 35,544 | 4.05e-6 | 15,000 | 2,159 | 4 | 144 |
| L2 | 79,974 | 6.35e-6 | 15,000 | 7,617 | 4 | 508 |
| L3 | 180,256 | 9.95e-6 | 15,000 | 26,905 | 4 | 1,794 |

**The unreduced total is 2,446 core-min, which EXCEEDS the 900 cap**, and that is
registered here rather than discovered at hour nine. **Registered stop order, in force
before the first solve:** L1 first; L2 only if L1 satisfies every §8-of-parent
convergence criterion; L3 only if L2 does. **A level that hits the 15,000 cap is
`NOT A RESULT` (parent §8) and the ladder stops there** — the remaining budget is not
spent proving the same thing twice. If L1 and L2 both converge and L3's projected spend
would exceed the cap, **the run stops and the case is `PENDING` on a cap raise, which is
Sanaa's to grant.** An overrun stops the run; it does not get a new budget.

**Dollars: DERIVED, NOT MEASURED.** At the owner-stated `c7a.4xlarge` rate of
**$0.0513/core-h**, the 900 core-min cap is **$0.77**. The box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER` §5), so this figure is **reported-by-owner and derived**,
never measured.

**Owed at completion and not optional (rule 12):** an estimate-versus-actual row in
`docs/COST_CALIBRATION.md`, stating the ratio actual/predicted, attributing the gap
between contention, waste and misprediction, with waste named separately and never
absorbed into the ratio.

---

## 9. FROZEN ARTIFACTS

| artifact | sha256 |
|---|---|
| `cases/F28_DUCTED_ACTUATOR_DISK/case/mesh/make_mesh.py` | `8d7cabeeda2891ff1cd0dae13443cf0a2f28c05713642c0251f79338d8a08a0c` |
| superseded generator (`55c4db56`) | `c27bcd73903c5d0dedb3530eb1cc705914adcccdda1db080b0871da623fbac89` |
| `cases/F28_DUCTED_ACTUATOR_DISK/f28_face_volume_ratio.py` | recorded at commit |

**SUPERSEDED by this document** (numbers retained, never rewritten, per
`VERIFICATION_CHARTER` §2d.1 condition 4): `verification/runs/F28_runs/mesh_L{1,2,3}`,
`mesh_L{1,2,3}_A1`, `DIAG_mesh_L{1,2,3}_A1`, and the birth certificates
`case/mesh/BIRTH_L{1,2,3}{,_A1}.json`. Their measured values are cited throughout this
document as the **before** column and are the evidence for §2 and §4.

Intermediate ladders `mesh_A2` (repairs 4.1–4.4, no apex spacing) and `mesh_A3` (apex
target 1.25) are retained as the **negative arms** of §4.5 and are not the graded ladder.

---

## 10. WHAT THIS REGISTRATION DOES NOT CLAIM

- **It does not claim a cause for the non-converging feasibility arms.** §2 removes one
  candidate's co-location with the graded quantity and removes the jump itself. The `p`
  residual that did not move in 15,000 iterations is **untouched** by anything here.
- **It does not claim Sanaa's §4 sentence is satisfied.** §3 shows the volume-ratio form
  of it is unattainable on this topology and refers that to her desk. The linear-growth
  form is met in full.
- **It does not claim the ladder is in the asymptotic range.** That is what §7 measures.
- **It does not claim the L-142 property of §5.4 is harmless** — only that it is common to
  all three levels and therefore common-mode in the triple.
- **It regrades nothing.** No parent verdict is reopened by this document.

---

*Written by `lab-lane` for `cfd-supervisor`, 2026-09-01, under Sanaa's directive*
*`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md` (`f4c8e466`)*
*§0 and §4. All three levels were BUILT AND CHECKED BEFORE THIS FREEZE*
*(`MESH_STANDARD` §8.1). No solve has been launched at the time of this freeze.*
