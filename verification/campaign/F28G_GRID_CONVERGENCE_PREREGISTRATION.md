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

---

## ADDENDUM 1 — 2026-09-01 — A "PREDICTED" FIGURE THAT WAS RIGHT BY CANCELLATION, AND A PRE-COMPUTE CAP AMENDMENT

**Version 1.1. Lines whose number changed above this section: 0.** A pure append.
Raised by `cfd-supervisor` on the check-4 read, not found by this lane.

### A1.1 THE CONDITION RULE 2 REQUIRES, AND HOW IT WAS CHECKED

Rule 2 permits amendment **before first compute** only. **Condition: no F28G solve has
run.** Checked, not asserted: `ls -d verification/runs/F28G*` and
`verification/runs/F28_runs/F28G*` return **0 directories** — *the run directory that
does not exist is `verification/runs/F28_runs/F28G_L1_dp1000_U20/`*. Independently
verified by the supervisor on the same check. `mesh_A4/` holds meshes and `checkMesh`
logs only; no solver has been launched.

**A1.3 below amends A CAP AND NOTHING ELSE.** No gate, threshold or label moves. A1.2
and A1.4 correct prose and add a disclosure; neither touches a gate.

### A1.2 §2's "33.9 PREDICTED" IS STRUCK — IT WAS RIGHT BY THE CANCELLATION OF TWO ERRORS

§2 asserts *"33.9 predicted against 33.4911 measured"*. **The measurement stands. The word
"predicted" does not, in the form it was written, and it is struck.** The substitution
behind it does not reproduce from the two radii §2 quotes: those are **volume centroids**,
not the `r_hub` and `h` the relation takes.

Re-derived from `constant/polyMesh/points` by
`cases/F28_DUCTED_ACTUATOR_DISK/f28_apex_mechanism_check.py` (planted control and negative
limb passing), on the superseded L1 mesh, worst internal face 23775:

- the upstream cell's **left** face spans `r in [4.437551e-04, 4.571292e-04]` at
  `x = 0.198817`; its **right** face spans `r in [0, 1.342577e-05]` at `x = 0.200000`.
  **THE APEX IS INSIDE THE CELL** — its inner edge runs `4.437551e-04 -> 0` within its own
  axial extent. §2's picture of an annulus `[r_hub, r_hub + h]` at constant `r` is wrong
  for this cell, and a min/max over its vertices turns a thin slanted quad into a fat
  rectangle **34x too large in volume**;
- the downstream cell spans `[0, 1.342577e-05]` at both faces.

**WHAT DOES REPRODUCE, to four significant figures.** The exact linearly-varying wedge
sector, `V = (theta/2) dx INT_0^1 [r_out(t)^2 - r_in(t)^2] dt` with `r_in`, `r_out` linear
and `INT_0^1 (A+Bt)^2 dt = A^2 + AB + B^2/3`, from vertex radii only:

| | computed | solver-reported | apart |
|---|---|---|---|
| `V_up` | 3.161008e-13 | 3.156857e-13 | 0.131 % |
| `V_down` | 9.437935e-15 | 9.425960e-15 | 0.127 % |
| **ratio** | **33.492578** | **33.491088 (measured)** | **0.004 %** |

**The mechanism is confirmed. The arithmetic that was published for it was not.**

**The simplified form, substituted correctly**, is `1 + 2 r_in_mean / h` where `r_in_mean`
is the **axial mean** of the cone edge over the apex cell — `TAIL_SLOPE * dx_up / 2 =
2.218775e-04`, **not** `r_hub` evaluated at the cell centre — and `h = 1.342577e-05` is
the **vertex** radial extent of the axis cell, **not** twice its reported centre. That
gives **34.052487 against 33.491088 measured, 1.676 % apart.** Its two approximations are
priced rather than assumed: `h_up/h_down = 0.998077`, `dx_up/dx_down = 0.986123`.

**THE TWO ERRORS IN THE PUBLISHED FIGURE, EACH PRICED:**

| substituted | value used | correct value | error |
|---|---|---|---|
| `r_hub` at the reported cell centre `x = 0.199217` | 2.935650e-04 | 2.218775e-04 (axial mean) | **+32.3 %** |
| `h` as twice the reported centre | 1.788399e-05 | 1.342577e-05 (vertex) | **+33.2 %** |

`1 + 2 x 2.935650e-04 / 1.788399e-05 = 33.8299`, published as "33.9". **Right to 2 % by
the cancellation of two ~+33 % errors, not by substitution.** The supervisor's diagnosis
of the second error is exact: the volume centroid of a wedge sector spanning `[0, h]` sits
at `2h/3`, and `2/3 x 1.342577e-05 = 8.950513e-06` against the reported centre
`8.941994e-06`.

**A SECOND, INDEPENDENT CONFIRMATION — of §3's algebra, on the REBUILT mesh.** On
`mesh_A4/L1` the worst internal face is no longer the apex but the **axis floor**, cells
`[0, 1.342577e-05]` and `[1.342577e-05, 3.008910e-05]`. §3's relation `(1+q)^2 - 1` with
`q = 1.6663e-05 / 1.3426e-05 = 1.2411` gives **4.0225** against **4.022753 measured** —
and `q = 1.2411` is `ROW_I`'s own `q1` at L1, **1.24115**, read back independently in
§5.3. **The exact wedge relation reproduces that face to 0.000 %.** *(The
`1 + 2 r_in_mean / h` form printed by the checker does not apply at an axis floor; the
governing relation there is `(1+q)^2 - 1`, and the checker's `(S)` line is to be read only
for an apex face.)*

**What this changes in the record:** §2's mechanism claim is **retained and strengthened**
— it now reproduces to 0.004 % instead of to a hand-waved 1 % — and its published
arithmetic is **struck**. §2's *location* finding (the jump is on the axis, 400 radii from
the graded quantity) rests on the per-face measurement and is **untouched by this
correction**.

### A1.3 THE COST CAP IS AMENDED FROM 900 TO 3,000 CORE-MINUTES — CAP ONLY

**Why the 900 cap was wrong to register.** §8's own projection was **2,446 core-min**
against it. A cap a registration already projects to exceed guarantees the ladder stops
before L3, and **Sanaa's §0 requires three levels for an observed order**; her ruling is
that cost is not a constraint and that "tens of core-minutes to a few core-hours ... is
never a reason to skip it". Registering an unmeetable cap is not conservatism — it is a
pre-registered failure.

**A SECOND DEFECT IN §8, SELF-REPORTED: the stated derivation does not produce the number
that was used.** §8 writes the exponent as `log(1.82)/log(2.25) = 0.548`. That quotient is
**0.7385**, not 0.548, and the projections in §8's table were computed with an implied
**0.5547**. **Neither the stated derivation nor the stated value is what the table used.**
Struck.

**The basis is also corrected, and it is BORROWED AND PROVISIONAL.** The jet-flap lane's
1.82x-per-cell figure was **contention-blind and has been withdrawn**; the surviving
measurement is **1.473x per cell at 2.25x cells**. Re-derived:
`log(1.473)/log(2.25) = 0.47760`, i.e. per-cell `t ~ N^0.4776` and total `t ~ N^1.4776`.
Anchored on the jet-flap L2 point `4.27e-6 s` per cell per iteration at 39,984 cells —
**only the RATIO was corrected upstream, and this lane has not re-verified the anchor**:

| level | cells | `t_cell` [s] | wall [s] | ranks | core-min |
|---|---|---|---|---|---|
| L1 | 35,544 | 4.037e-06 | 2,152 | 4 | **143.5** |
| L2 | 79,974 | 5.946e-06 | 7,133 | 4 | **475.5** |
| L3 | 180,256 | 8.766e-06 | 23,701 | 4 | **1,580.0** |
| | | | | | **2,199 total** |

> **AMENDED CAP: 3,000 core-minutes for the three-level triple**, giving 36 % headroom over
> a projection whose rate model is borrowed from another case and another lane. **Dollars
> DERIVED, NOT MEASURED: 50.0 core-h at the owner-stated $0.0513/core-h = $2.56.**

**THE PER-LEVEL STOP ORDER OF §8 IS RETAINED IN FULL AND IS NOT WHAT IS RELAXED:** L1
first; L2 only if L1 satisfies every parent-§8 convergence criterion; L3 only if L2 does;
a level hitting the 15,000-iteration cap is `NOT A RESULT` and the ladder stops there. **An
overrun stops the run; it does not get a new budget.** If the actual L1 spend implies a
three-level total above 3,000, the run stops and the case is `PENDING` on a cap raise,
which is Sanaa's to grant.

**The calibration row owed at completion (rule 12) now has a second thing to say:** the
predicted/actual ratio must be reported **against this borrowed rate model**, and the
model's exponent re-fitted from F28's own three levels — which is the first
in-case measurement of it this lab will have.

### A1.4 L-142 — STATED AS A NON-MEASUREMENT, AS REQUIRED

§5.4 records that the wake row's finest radial cell sits on the centreline. Stated
explicitly, because an unstated gap reads as a cleared one:

> **This lane did NOT measure whether the L-142 property materially affects the integrated
> duct force.** No solve has run. What is established is only that the property is present,
> that it is the root of the reported max aspect ratio and of the axis volume-ratio floor,
> and that it is **common to all three levels and therefore common-mode in the Roache
> triple**. Whether a common-mode geometric error cancels in an observed order is
> **not** established by its being common-mode, and nothing here should be read as
> claiming it does.

### A1.5 NEW REGISTERED ARTIFACT

`cases/F28_DUCTED_ACTUATOR_DISK/f28_apex_mechanism_check.py` — reads `points`, `faces`,
`owner`, `neighbour` and `cellVolume`; plants a x1000 volume perturbation and refuses
unless it reads it back, with a negative limb on the unperturbed field; resolves each cell
into its two faces **at the largest gap in x** rather than assuming two x-stations,
because `blockMesh` blends a block's interior from its edges and the grid lines tilt (the
residual in-face tilt is reported: **2.400e-09 m against `dx_up` 1.183e-03 m** on the face
above). Its sha256 is recorded at the commit that lands this addendum.

*Appended by `lab-lane` for `cfd-supervisor`, 2026-09-01, after the check-4 read. No solve
has been launched at the time of this addendum.*

---

## ADDENDUM 2 — 2026-09-01 — THE COST ANCHOR IS SUPERSEDED TOO, A HEADROOM CONVENTION IS NAMED, AND THE READER ASSUMPTION IS PUT ON THE RECORD

**Version 1.2. Lines whose number changed above this section: 0.** A pure append.
**No cap, gate, threshold or label moves in this addendum** — Addendum 1's amended cap of
3,000 core-minutes stands unchanged; only the projection under it is re-anchored.

### A2.1 THE CONDITION, RE-CHECKED RATHER THAN CARRIED FORWARD

`ls -d verification/runs/F28G* verification/runs/F28_runs/F28G*` returns **0
directories**; `verification/runs/F28_runs/F28G_L1_dp1000_U20/` still does not exist. No
solve has run. Re-checked at the time of this append, **not** inherited from Addendum 1 —
an hour-old condition check is not a condition check.

### A2.2 THE ANCHOR MOVED, NOT ONLY THE RATIO — RE-ANCHORED

Addendum 1 flagged that only the *ratio* had been corrected upstream and that this lane
had **not** re-verified the `4.27e-6 s` per cell per iteration anchor. **Asked, and it had
moved.** The supervisor re-measured it from the raw jet-flap logs independently of that
lane's comparator — 250-iteration windows, median of window medians, first window dropped:

| | superseded | measured replacement |
|---|---|---|
| `C1` at 39,984 cells | 4.27e-06 s | **3.8115e-06 s** (**−10.74 %**) |
| `C2` at 89,964 cells | — | **5.6151e-06 s** |

**Verified here rather than accepted:** `C2/C1 = 1.473200` against the stated 1.473, and
`N2/N1 = 2.250000`. The exponent is taken from **the two measured points**, not from the
rounded ratio: `log(1.4732)/log(2.25) = 0.477768` (the rounded 1.473 gives 0.477601; the
difference is 1.7e-04 and moves no row below).

**RE-ANCHORED PROJECTION** — `t_cell = 3.8115e-06 (N/39984)^0.477768`, 15,000 iterations,
4 ranks:

| level | cells | `t_cell` [s] | wall [s] | core-min |
|---|---|---|---|---|
| L1 | 35,544 | 3.6031e-06 | 1,921 | **128.1** |
| L2 | 79,974 | 5.3080e-06 | 6,368 | **424.5** |
| L3 | 180,256 | 7.8263e-06 | 21,161 | **1,410.7** |
| | | | | **1,963 total** (was 2,199) |

**A CONVENTION MISMATCH, NAMED BEFORE IT BECOMES A SPURIOUS DISAGREEMENT.** Addendum 1
wrote "36 % headroom" meaning **the cap as a fraction ABOVE the projection**
(`3000/2199 = 1.364`). The supervisor's reply wrote "35 %" meaning **the fraction of the
cap left UNSPENT** (`(3000−1963)/3000 = 0.346`). Both are correct arithmetic on different
definitions, and neither of us stated which. **Fixed here, for this document and for its
calibration row:**

> **HEADROOM IS REPORTED AS THE FRACTION OF THE CAP LEFT UNSPENT BY THE PROJECTION**,
> `(cap − projection)/cap`. On the re-anchored figures that is **34.6 %**. Under the
> other convention the same pair reads 52.8 %, and a record that does not say which it
> means has not reported a number.

**The rate model remains BORROWED AND PROVISIONAL.** Both `C1` and the exponent now come
from one other case on one other lane; F28 has contributed nothing to it. The calibration
row owed at completion re-fits the exponent from F28's own three levels, which will be
this lab's **second** in-case measurement of it and the first on an axisymmetric wedge.

### A2.3 THE FAULT WORTH REMEMBERING IS A GEOMETRIC ASSUMPTION EMBEDDED IN A READER

Recorded in the terms the supervisor asked for, because the next person to write a
volume-ratio reader on a wedge will make the same assumption:

> **THE APEX IS INSIDE THE CELL.** The first version of
> `f28_apex_mechanism_check.py` took the minimum and maximum radius over a cell's
> vertices and treated the result as the cell's radial span. For the last cell of a cone
> that terminates on the axis, that is false: the cell's inner edge runs from
> `4.437551e-04` to `0` **within its own axial extent**, so a min/max over its vertices
> reports a span of `[0, 4.571292e-04]` and turns a thin slanted quadrilateral into a fat
> rectangle. **It overstated the cell's volume by 34x** — computed `1.078967e-11` against
> the solver's `3.156857e-13` — and returned a face ratio of **1143.22** where the mesh
> measures **33.491088**.
>
> **This is not an arithmetic slip. It is a geometric assumption embedded in a reader:
> that a cell is an annulus at constant `r`.** It is silently true for most of a
> structured wedge mesh and silently false exactly where a body meets the axis — which is
> the one place such a reader is pointed. The repair is to resolve each cell into its two
> faces and integrate `V = (theta/2) dx INT_0^1 [r_out(t)^2 - r_in(t)^2] dt` with `r_in`,
> `r_out` linear, which reproduces both cells to **0.13 %** and their ratio to
> **0.004 %**. **The two faces cannot be found by grouping vertices on `x` either**:
> `blockMesh` blends a block's interior from its four edges, so the grid lines tilt and
> the corners do not share two `x` values. They are separated at the **largest gap in
> `x`**, and the residual in-face tilt is reported rather than assumed away —
> **2.400e-09 m against `dx_up` 1.183e-03 m** on the face above.

A draft register entry carrying this is at Appendix B and is **REFERRED, NOT FILED** —
landing an `N-` entry is the supervisor's call, not this lane's.

### A2.4 §7's COMPARATOR CLAUSE IS DISCLOSED AS NOT YET SATISFIABLE

§7 registers N-T8's value-checking Richardson selftest as a refusal in "the comparator".
**No such comparator exists.** `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` is the
parent's §6.2/§6.3 V-controls comparator and carries no Roache triple, no GCI, no
Richardson extrapolate and no mesh-gate reading — grepped for
`CONVERGING|DIVERGENT|OSCILLATORY|STAGNANT|GCI|observed order|richardson|f_ext|nonOrtho|skewness`,
**zero hits**.

**Consequence, stated plainly:** rule 2 requires the grading path fixed at the
pre-registration commit and verified by hashing the frozen file against the committed
blob. **For §7 that property does not hold at this document's freeze, because the file it
names has never been written.** §7's requirements stand as **binding requirements on a
comparator yet to be written**; they are not, and must not be represented as, a frozen
grading path.

The supervisor has ruled the team-level fix — **a comparator is committed WITH its
registration, or the registration names no comparator clause at all** — after finding the
same defect in JF1G's §11 the same day. That ruling is his to land; it is recorded here
because this document is one of its two occasions. **This lane is released from writing
the comparator and has not started it.**

---

## APPENDIX B — DRAFT `N`-ENTRY — **REFERRED, NOT FILED**

**Not filed. Landing it in `docs/NUMERICS_KNOWLEDGE.md` is the supervisor's call.**

> **N-?? . On an axisymmetric wedge, a cell-volume reader that takes min/max over a cell's
> vertices is exactly wrong where a body meets the axis — the apex is INSIDE the cell, and
> the error is a factor of 34.**
>
> **Class: READER-GEOMETRY.** The assumption is that a structured wedge cell is an annulus
> at constant `r`, so its radial span is `[min r, max r]` over its vertices. True for most
> of such a mesh. **False for the last cell of a cone terminating on the axis**, whose
> inner edge sweeps to zero within its own axial extent: measured on F28 L1, a cell whose
> faces span `[4.437551e-04, 4.571292e-04]` and `[0, 1.342577e-05]` is reported by that
> reader as spanning `[0, 4.571292e-04]`, giving `1.078967e-11 m^3` against the solver's
> `3.156857e-13` — **34.2x** — and a face ratio of **1143.22** against a measured
> **33.491088**.
>
> **The exact relation**, from vertex radii only, with `r_in` and `r_out` linear in `t` and
> `INT_0^1 (A+Bt)^2 dt = A^2 + AB + B^2/3`:
> `V = (theta/2) dx INT_0^1 [r_out(t)^2 - r_in(t)^2] dt`. On the pair above it reproduces
> both volumes to **0.13 %** and their ratio to **0.004 %**.
>
> **A SECOND TRAP INSIDE THE FIRST:** the two faces cannot be recovered by grouping the
> cell's vertices on `x`. `blockMesh` blends a block's interior from its four edges, so the
> grid lines TILT and a cell reports **three** distinct `x` stations, not two. Split at the
> largest gap in `x` and **report the residual in-face tilt** — 2.400e-09 m against a
> `dx` of 1.183e-03 m on the F28 face, four orders below the 84.62-degree tilt the same
> generator's header documents, but non-zero and not to be assumed away.
>
> **A THIRD, ON CENTROIDS:** the volume centroid of a wedge sector spanning `[0, h]` sits
> at **`2h/3`**, not `h/2`. Substituting a reported cell centre as `h/2` overstates `h` by
> **4/3**. Measured: `2/3 x 1.342577e-05 = 8.950513e-06` against the reported centre
> `8.941994e-06`.
>
> **How it was caught, because the catching is the lesson.** A published figure read
> *"33.9 predicted against 33.4911 measured"* and was accepted by nobody: a supervisor
> substituted the two radii the record itself printed and got **68.11**, and asked for the
> arithmetic. It turned out the figure was right to 2 % **by the cancellation of two
> ~+33 % errors** — an over-large `r` from evaluating the cone at the cell centre, and an
> over-large `h` from doubling a centroid. **An accidental agreement of that quality
> survives review indefinitely unless someone re-substitutes from the numbers on the page.**
>
> *Source: `verification/campaign/F28G_GRID_CONVERGENCE_PREREGISTRATION.md` Addendum 1
> §A1.2 and Addendum 2 §A2.3; `cases/F28_DUCTED_ACTUATOR_DISK/f28_apex_mechanism_check.py`.*

*Appended by `lab-lane` for `cfd-supervisor`, 2026-09-01. No solve has been launched.*

---

## ADDENDUM 3 — 2026-09-01 — WHO WROTE THE UNSATISFIABLE §7 CLAUSE, RECORDED BECAUSE A MESSAGE THREAD IS NOT THE RECORD

**Version 1.3. Lines whose number changed above this section: 0.** A pure append.
**Nothing here is a gate, threshold, cap or label**, and none moves. Condition re-checked
at the time of this append, not carried forward from Addendum 2: **0 F28G run directories
anywhere**; `verification/runs/F28_runs/F28G_L1_dp1000_U20/` does not exist.

§A2.4 discloses that §7 registers an N-T8 selftest against a comparator that does not
exist. It does not say **who wrote that clause**, and the attribution was settled in
agent messages — which are not this repository's record and do not survive the session.
Landed here so it does.

> **The lane wrote an unsatisfiable clause. The supervisor did not catch it. Both are
> real and the record carries both.**
>
> The clause was written by this lane, in a document this lane drafted, **naming a file it
> had not checked existed**. `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` was present in
> the case directory and was assumed to be the grading comparator; it is the parent's
> §6.2/§6.3 V-controls comparator and carries no Roache triple, no GCI, no Richardson and
> no mesh-gate reading. **Disproving the assumption took one `grep` and about eleven
> seconds, and it was run only after the supervisor's check-4 read prompted it.**
>
> **THE CHEAPEST LESSON OF THE DAY, AND IT IS THE LANE'S: GREP THE FILE YOU ARE ABOUT TO
> NAME IN A FREEZE.** A pre-registration's authority rests on the grading path being fixed
> at its commit and hashable against the committed blob (rule 2). A clause naming a file
> that has never been written cannot be satisfied by anyone, and it fails silently — it
> reads exactly like a clause that will be satisfied.

The supervisor initially recorded the defect as entirely his, on the grounds that he
approved the freeze, and has since corrected that to the version above. **Recorded in that
direction deliberately:** taking a lane's authorship onto the supervisor would have hidden
the one lesson that costs eleven seconds to apply.

The team-level rule that follows — **a comparator is committed WITH its registration, or
the registration names no comparator clause at all** — is the supervisor's and is his to
land. It was occasioned by two documents on one day, this one and JF1G's §11.

*Appended by `lab-lane` for `cfd-supervisor`, 2026-09-01, after release. No solve has been
launched, and this lane has not begun the comparator.*

---

## AMENDMENT 4 — THE GRADING PATH IS NAMED AND FROZEN HERE, BEFORE ANY SOLVE; AND A SECOND HOLE OF THE SAME SHAPE IS DISCLOSED: THIS REGISTRATION NAMES NO LAUNCHER EITHER

**Version 1.4. Lines whose number changed above this section: 0.** A pure append.
Dated 2026-09-03, by the `cfd` lab-lane, on `cfd-supervisor`'s ruling of the same day.
**PRE-COMPUTE.** No F28G solve has ever run and none is launched by this amendment.

### A4.1 The condition, and how it was checked — rule 2's requirement, discharged by naming the directory that does not exist

`verification/runs/F28_runs/F28G_L1_dp1000_U20/` **does not exist.** Checked three ways in
the same shell invocation that wrote this section, not recalled from §12:

| check | result |
|---|---|
| `ls -d verification/runs/F28G*` | **0 directories** |
| `ls -d verification/runs/F28_runs/F28G*` | **0 directories** |
| `test -e verification/runs/F28_runs/F28G_L1_dp1000_U20` | **non-zero** (absent) |

The full listing of `verification/runs/F28_runs/` at this moment carries `DIAG_*`, `FEAS_*`,
`mesh_*` and `_*launch*` entries and **no `F28G` entry of any kind**. The mesh stage of §8
is spent; the **solve stage has produced nothing**, so gates are open and a pre-compute
amendment is legal under rule 2.

### A4.2 THE GRADING PATH, FIXED HERE WITH ITS BLOBS

| file | blob (worktree == this commit) | state at the original freeze `00188f82` |
|---|---|---|
| `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28g.py` | `8c17fdd55b9606ebf115f3442678fecc74152887` | **DID NOT EXIST** |
| `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` | `5aff1614aff38ccdad0c33a0be9fb17b313fc167` | present, **byte-identical** |
| `cases/F28_DUCTED_ACTUATOR_DISK/f28_apex_mechanism_check.py` | `dfa795092bf8eef0b54e450beac5144b04e7a1dc` | present, **byte-identical** |

`analyse_f28g.py` is the grading comparator. The other two are named because §7 and the
parent's §6.2/§6.3 refer to them; they are **not** the Roache/GCI grader and never were —
that misidentification is §A2.4's own finding and is not re-litigated here.

### A4.3 THE THIRTY MINUTES, STATED RATHER THAN BURIED — it is the fact that makes this bookkeeping and not fitting

`analyse_f28g.py` was introduced by commit `a09376a9f636088b534d2b5e480151cf20328314` at
**2026-09-01 17:48:37 +0000**. This registration froze at `00188f8266d10c333bb45974dd88fc4d54ee8d0e`
at **2026-09-01 17:18:16 +0000**. **The comparator post-dates its own registration's freeze
by 30 minutes and 21 seconds.**

**Why that is bookkeeping and not post-hoc fitting, stated as a checkable fact rather than
as an assurance:** the comparator was written **before any F28G solve produced a number**,
and no F28G solve has produced a number to this day — §A4.1's three absence checks are the
evidence. A grader written before the first datum cannot have been shaped to the answer,
because there was no answer to shape it to. **The freeze's evidentiary content — that the
gate could not have been chosen to fit the result — is therefore intact in substance, and
what was missing was the record of it.** This amendment supplies the record.

It **does not** repair rule 2's hashability retroactively: the grading path is fixed **at
this amendment's commit**, not at `00188f82`, and any reader must hash against this
amendment's commit. That is a weaker guarantee than a grading path frozen with its
registration, and it is stated as weaker rather than presented as equivalent.

### A4.4 THE CHECK-1 TOKEN, AND THE BASIS ON WHICH IT WAS ISSUED

`cfd-supervisor` issued the SUPERVISION_CHARTER §3 check-1 token on **2026-09-03**, from a
**personal read of `analyse_f28g.py` (2,705 lines)**, and recorded the scope of that read as
six items, reproduced here so a later reader knows what the token does and does not cover:

1. **Zero bare `assert` statements** — L-332 honoured in fact, not cited.
2. **`--selftest` run under `python3 -O`** by the supervisor: `limbs_failed: 0`, `pass: true`,
   rc 0. Under `-O` is the only run that proves the guards survive optimisation.
3. **Rule 5's Roache gating** implemented in the correct order and in the one permitted
   direction, with `assert_one_way` proving the one-wayness on synthetic rows.
4. **GCI at Fs = 1.25**, with a separate guard refusing to quote a GCI on a non-monotone triple.
5. **Aspect ratio provably never gates** — an absurd `1e9` is planted and the row must still
   not be rejected on it alone.
6. **Verdict vocabulary tuple matches rule 1 exactly**, with `assert_verdict_strings_are_inert`,
   and one plant per number-producing reader, each read back from disk and refusing if unseen.

**A SCOPE MISMATCH IS RAISED HERE RATHER THAN PAPERED OVER, AND IT IS NOT THIS LANE'S TO
RESOLVE.** `cases/F28_DUCTED_ACTUATOR_DISK/run_f28.sh` states at its own usage block that
`--check1-token` attests to a read of **`analyse_f28.py`**. The supervisor's read was of
**`analyse_f28g.py`** — a different file. The read that was performed is the more relevant
one (it is the actual grader), but the token's registered referent is the other file, and a
token supplied against a file its holder did not say they read would be exactly the
laundering rule 9 forbids. **No token string has been supplied by this lane.**

### A4.5 THE SECOND HOLE: THIS REGISTRATION NAMES NO LAUNCHER, AND ITS ONLY CANDIDATE BINDS TO A DIFFERENT REGISTRATION

Found while preparing the launch this amendment was written to enable. **F28G CANNOT LAUNCH
TODAY, and the reason is not the grading path.**

1. **This document names no launcher script at all.** Population searched: every string
   matching `[A-Za-z0-9_./-]+\.sh` in this file. **Zero matches.** Same shape as §A2.4's
   missing comparator, in the other half of the run.
2. **`run_f28.sh` cannot serve, because it is bound to the PARENT registration.** It sets
   `PREREG=verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md` and refuses
   unless `--prereg-commit`'s blob for **that** file equals the parent's blob on disk.
   Measured: the parent's blob on disk is `198a76445ed2eb59bf5afb08b0487708fc8b1340`; the
   parent's blob at F28G's freeze `00188f82` is `c482dd09e6f66fa7c57ca34263b6f18b73c4af21`.
   **They differ**, so `--prereg-commit=00188f82` ABORTS. The only commit that satisfies the
   check is the parent's own `b50cd1cadc9350228d35a8c86ff683df6e94a17b` — which would launch
   an F28G rung **against the parent's freeze, gates and grading path, not this study's**.

**VERDICT ON LAUNCHABILITY: `BLOCKED`** — and on the launcher, with the grading path now
fixed. Not `PENDING`, which would say only "not yet run", and not softened: there is no
registered path by which an F28G rung can start under this registration's own freeze.
Writing or registering that launcher shapes what the study measures and is above a lane;
it is referred to `cfd-supervisor` with the arithmetic above already done.

*Appended by `lab-lane` for `cfd-supervisor`, 2026-09-03. Zero compute. No solve launched,
no gate, threshold, cap or label altered.*
