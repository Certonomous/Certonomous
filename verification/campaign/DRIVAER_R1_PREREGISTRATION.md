# DRIVAER R1 — DrivAer notchback (DrivAerML run_466), Cd/Cl parity — PRE-REGISTRATION

<!-- ============================ STATUS BANNER ============================ -->
<!-- ONE BLOCK.  It is the ONLY status claim in this file.  To freeze, strike  -->
<!-- this whole block and fill §13.  Nothing outside it asserts a status, so   -->
<!-- striking it cannot leave a stale banner contradicting a later freeze.     -->
> ## STATUS — DRAFT, UNFROZEN, NO SHA. NO COMPUTE HAS RUN AGAINST THIS FILE.
> **NOT FREEZE-READY**, and the blocker is named: **§6, the wall treatment.**
> The geometry is on disk, the three-level mesh family is **BUILT AND MEASURED**,
> and every number in §4 cites a mesh on disk. What is *not* settled is the
> near-wall discretisation: snappyHexMesh's layer-addition phase is defective on
> this geometry (§12.1, measured), so the family carries **no prism layers** and
> its y+ is both far too high and **not constant across the triple** (§6). A
> Roache triple whose wall model changes between levels measures the wall model,
> not the grid.
> Drafted by a cfd lab-lane. **The freeze (sha) is the supervisor's check-4; the
> grader diff-read is the supervisor's check-1.** This lane froze nothing,
> launched nothing and committed nothing.
<!-- ========================== END STATUS BANNER ========================== -->

Case family: Navier-class parity, `navier_class` convention.

| | |
|---|---|
| Case inputs / grader | `cases/navier_class/DRIVAER/` |
| Mesh generator | `cases/navier_class/DRIVAER/mesh/build_drivaer_level.py` |
| Mesh family (built) | `verification/runs/navier_class/DRIVAER/r1_{coarse,medium,fine}` |
| Measured family record | `verification/runs/navier_class/DRIVAER/MESH_FAMILY_MEASURED.json` |
| Per-feature limb record | `verification/runs/navier_class/DRIVAER/PATCH_LIMB_MEASURED.json` |
| Geometry + provenance | `cases/navier_class/DRIVAER/DATA_PROVENANCE_drivaerml.md` |

**Rule-2 pre-compute condition, and how it was checked.** Amendments before first
compute are legal. The condition is that no graded run exists. Checked 2026-09-10
by naming the directories and reading them: `r1_coarse`, `r1_medium` and `r1_fine`
each contain **0 time directories, no `0/`, no `postProcessing/` and no
`log.simpleFoam`**. They hold `constant/polyMesh` and mesh-build logs only. This
file therefore **supersedes** the 2026-09-09 draft rather than amending it; §1.4
records why that draft could not stand.

---

## 1. THE REFERENCE DATA — READ FIRST, AND IT CHANGED THE REGISTRATION

### 1.1 What is actually on disk

Geometry, verified by opening it (rule 15): `drivaer_466.stl`, 142,346,740 B,
ASCII, `solid BodyA-Pillar` … `endsolid WheelSupportrear`, **753,238 facets, 49
named solids**, sha256 `9fd0eec1f436e336…`. Dataset `neashton/drivaerml`, revision
`7a5c0948ce27be709b1116a3a190f806e7a8f79f`, CC-BY-SA-4.0.

`surfaceCheck` on that file (own run, 39.5 s, rc=0): **"Surface is closed. All
edges connected to two faces."**, unconnected parts **1**, zones **1**, 0 nearby
points. It also reports the dirt: minimum triangle quality **2.16e-11** and
minimum edge length **1.22e-05 m**.

### 1.2 THE COEFFICIENTS COME IN TWO CONVENTIONS AND THEY DIFFER BY 5.57 %

The dataset ships **two** force files for run_466, and they are not alternatives
to be picked casually — they are the *same forces* on *different reference areas*.

| file | Cd | Cl | Clf | Clr | Cs |
|---|---|---|---|---|---|
| `force_mom_466.csv` (per-geometry ref) | **2.758368e-01** | **−5.357145e-02** | −1.803103e-01 | 1.267388e-01 | 2.565178e-02 |
| `force_mom_constref_466.csv` (nominal ref) | **2.921074e-01** | −5.673143e-02 | −1.911301e-01 | 1.343987e-01 | 2.716488e-02 |

`geo_ref_466.csv`, quoted verbatim:

```
lRef,aRef,forcesCoR,lRefRef,aRefRef,forcesCoRRef
2.79,2.298,(1.402 0 -0.3176),2.78618,2.17,(1.40009 0 -0.3176)
```

The two files are related exactly by the area ratio: measured
`Cd_constref / Cd = 1.05898633` against `aRef/aRefRef = 2.298/2.17 = 1.05898618`.
**The Cd difference is 5.57 % of the value — more than half the ±10 % half-band
this rung gates on.** Choosing the wrong pairing does not fail loudly; it moves
the target by more than half the tolerance.

### 1.3 Reference quantities, quoted from the paper

Ashton et al. 2024, arXiv:2408.11969v2 (title-page verified; PDF at
`/home/ubuntu/certonomous-runs/reference_pdfs/benchmark_test_cases/ashton_2024_drivaerml.pdf`,
pointer `docs/papers/benchmark_test_cases/ashton_2024_drivaerml.POINTER.md`).

Paper lines 225–228, verbatim: *"The CFD setup assumes incompressible flow with a
freestream velocity of U∞ = 38.889 m/s, ambient temperature of T = 293.15 K and
kinematic viscosity of ν = 1.507 × 10−5 m2/s. The Reynolds number of ReL = U∞ L/ν
= 7.19 × 106 based on the wheelbase L = 2.786 m is large enough to assume
turbulent flow over most of the car. The reference frontal area A = 2.17 m2 is
used for force and moment coefficients."*

Paper **Table 3**, "Reference quantities used for normalisation of force and
moment coefficients", is the authority on the two conventions:

| | `force_mom_i.csv` | `force_mom_constref_i.csv` |
|---|---|---|
| U∞ | 38.889 m/s | 38.889 m/s |
| **ρ∞** | **1 kg/m³** | **1 kg/m³** |
| Aref | 1.779 – 2.636 m² (per geometry) | 2.17 m² |
| Lref | 2.636 – 3.035 m (per geometry) | 2.78618 m |
| x_ref | per geometry | (1.40009, 0, −0.3176) m |

Coefficient definitions, paper eq. (30): `Cd = Fx/(p_dyn,ref · Aref)`,
`Cl = Fz/(p_dyn,ref · Aref)`, `Cs = Fy/(p_dyn,ref · Aref)`; moments additionally
divided by `lref`. Positive z is up, so the negative `Cl_ref` is downforce.

### 1.4 WHY THE 2026-09-09 DRAFT COULD NOT BE AMENDED — three defects

1. **Mixed conventions.** It registered `Aref = 2.17 m²`, `lRef = 2.786 m` — the
   *nominal* basis — while the provenance record pinned `Cd_ref = 0.2758368` from
   `force_mom_466.csv`, the *per-geometry* basis. That pairing is wrong by 5.57 %.
2. **`rhoInf = 1.225 kg/m³`** was registered "air — confirm at freeze". Table 3
   says **ρ∞ = 1 kg/m³**. (In incompressible OpenFOAM `rhoInf` cancels between
   force and dynamic pressure, so this does not move Cd — but the grader asserts
   the on-disk constants against the registered ones and would have refused, or
   worse, been "fixed" to the wrong number.)
3. **The mesh plan was unbuildable as a family.** It registered ~3M/6M/12M at
   `r ≈ 2^{1/3} ≈ 1.26`. The Case Protocol stage-1 exit condition requires a
   refinement ratio in **[1.5, 2.0]**; `r = 1.26` is refused *after* the compute
   is spent. §4 registers a measured ratio instead.

Its §1 ("No DrivAer STL is on disk") was already withdrawn by the supervisor.

### 1.5 REGISTERED REFERENCE — the per-geometry convention

**Registered, and one-way:** the gate uses `force_mom_466.csv` with the
**per-geometry** reference quantities from `geo_ref_466.csv`.

| quantity | registered value | source |
|---|---|---|
| `Cd_ref` | **0.2758368** | `force_mom_466.csv` |
| `Cl_ref` | **−0.05357145** | `force_mom_466.csv` |
| `magUInf` | **38.889 m/s** | paper l.225, Table 3 |
| `Aref` | **2.298 m²** | `geo_ref_466.csv` (`aRef`) |
| `lRef` | **2.79 m** | `geo_ref_466.csv` (`lRef`) |
| `CofR` | **(1.402, 0, −0.3176) m** | `geo_ref_466.csv` (`forcesCoR`) |
| `rhoInf` | **1.0 kg/m³** | paper Table 3 (ρ∞) |
| `ν` | **1.507e-05 m²/s** | paper l.226 |
| `Re_L` | 7.19e6 on L = 2.786 m | paper l.227 |

**Why the per-geometry convention, on measurement not preference.** run_466 is a
*morphed* variant; 2.17 m² is the *nominal baseline's* frontal area, not this
car's. An independent measurement of the STL settles it: rasterising the y–z
silhouette of all 753,238 facets at 2 mm gives a frontal area of
**2.3184 m²**, against `aRef = 2.298 m²` (**+0.87 %**, and the raster is a
bbox-fill **upper bound**) and against `aRefRef = 2.17 m²` (**+6.8 %**). The
STL's own silhouette confirms 2.298 and refutes 2.17 for this geometry.
*(The closed-surface projection formula `½Σ|A·n_x|` returns 5.045 m² here and is
**not** usable: the body carries interior surfaces — wheel wells, brake discs,
closed grill inserts — so the silhouette raster is the only correct estimator.)*

---

## 2. THE GATE — declared now, one-way

> **Gate V1 (PRIMARY).** `Cd` at `Re_L = 7.19e6`, from the **finest** grid of a
> **CONVERGING** Roache triple, is **PASS** iff
> `|Cd_cfd − 0.2758368| ≤ 0.10 × 0.2758368`, i.e. `Cd_cfd ∈ [0.2482531, 0.3034205]`.
> Otherwise **GATE FAIL**.
>
> **Gate V2 (SECONDARY).** `Cl` is **PASS** iff `|Cl_cfd − (−0.05357145)| ≤ 0.05`
> (**absolute** band; Cl is small and sign-sensitive), i.e.
> `Cl_cfd ∈ [−0.10357145, −0.00357145]`. Otherwise **GATE FAIL**.
>
> A non-CONVERGING triple is **NOT A RESULT** whatever the value (rule 5). The
> gate can only turn a PASS or GATE FAIL **into** NOT A RESULT, never the reverse.

**Band rationale, recorded before any run.** DrivAerML's own per-run statistical
accuracy is ΔCd = ±0.001 (≈1 drag count), so the reference is ~28× tighter than
this band. ±10 % is sized for a **steady-RANS vs scale-resolving-HRLES** parity
comparison, where model-form error dominates numerical error. It will not be
tightened or widened after the run.

**Recorded now so it cannot be claimed later:** the *nominal-reference* value
0.2921074 lies **inside** the registered band. The convention choice therefore
does not by itself decide the verdict — but it moves the band centre by 5.57 %,
more than half the half-band, and a result near either edge would be decided by it.

**Cs is NOT gated.** The reference `Cs = 2.565e-02` is non-zero, and §4.2 shows
that is genuine geometric asymmetry, not statistical noise. It is recorded, not gated.

---

## 3. REFERENCE TIER

**CODE-VERIFIED (rank 2)** per `verification/credibility/REFERENCE_TIER_STANDARD.md`.
DrivAerML is a scale-resolving CFD dataset (HRLES), a **CODE reference — NOT
experiment**. Mandatory disavowal, to appear beside every result:
**"reproduces the DrivAerML CFD dataset; NOT experiment-validated."**
Registry entry is deferred to completion (adding it now would be registry drift).

---

## 4. THE MESH FAMILY — BUILT AND MEASURED, NOT PLANNED

Generator `cases/navier_class/DRIVAER/mesh/build_drivaer_level.py`
(sha256 `7eaff652307537dc…`), runner `mesh/run_build.sh` (`7577f707d17e0718…`).
**The only parameter that changes between levels is `h_bg`, which is halved
exactly.** Every refinement level, refinement box, absolute size and the whole
domain are identical across the family.

### 4.1 Domain, and the ground plane

Full domain, **no symmetry plane** (see §4.2). x ∈ [−14.339, 37.661],
y ∈ [−10, 10], z ∈ [−0.319, 11.681] m. The floor is split at
**x_BL = −2.339 m** into `floorSlip` (upstream, inviscid) and `floorNoSlip`
(downstream, no-slip), reproducing the DrivAerML ground-boundary-layer treatment
(paper l.230–232). Sides and top are inviscid walls, as in the reference.

**Blockage = 0.9575 %** (`Aref` 2.298 m² over the 20 × 12 m cross-section),
below the registered 1 %. The reference's own blockage is 0.25 %; ours is larger
and is registered as a departure, not hidden. Free-air, so **no wind-tunnel
blockage correction is applied.**

**Ground plane at z = −0.319 m**, which is **0.633 mm above the STL minimum**
(−0.319633) and **2.325 mm below the tyre bottom** (−0.316675). The tyre contact
is therefore a **finite cut**, never a tangent cusp. Consequence, measured and
registered in §5.2: the two `TirePlinth*` pads (3.05 / 3.08 mm thick) are consumed
by the floor and produce **no patch at any level** — 47 of the 49 named features
appear in the mesh.

### 4.2 The half-model is REFUSED, on measurement

A y = 0 symmetry plane would have halved every count. It is refused because the
geometry is **not** symmetric. Per-solid y-bounding-box asymmetry `|y_lo + y_hi|`:
**44 of 49 solids are symmetric to < 0.1 mm**; the exceptions are the exhaust
system and the two wheelhouse control planes:

| solid | y_lo | y_hi | asymmetry |
|---|---|---|---|
| `ExhaustSystem3` | −0.58073 | −0.43483 | **1.01556 m** (one side only) |
| `ExhaustSystem1` | +0.24080 | +0.30266 | **0.54346 m** (other side) |
| `ExhaustSystem2` | −0.42580 | +0.32731 | **0.09848 m** (crosses y = 0) |
| `CTRL_SURFACE_Wheelhouse_LHS` / `_RHS` | ∓0.4674 | ∓0.4558 | 0.92324 m each (a mirrored *pair*) |

The exhaust is 0.575 m² of 35.210 m² wetted area (1.6 %), single-sided, and
`ExhaustSystem2` **crosses the centreline**, so a half-model would have to cut a
component in half. This also explains the reference's `Cs = 2.565e-02`: real
asymmetry, not incomplete averaging.
*(A whole-point-cloud mirror test gave 23.9 % of points > 1 mm from their mirror,
but that test is dominated by asymmetric triangulation of symmetric panels — p90
= 21 mm is the triangle scale. The per-solid bbox test above is
triangulation-independent and is the one relied on.)*

### 4.3 Delivered cell counts — from `checkMesh` stdout, cross-checked

Counts are read from the `checkMesh` stdout **and** cross-checked against the
`owner`/`neighbour` topology by an independent reader; a mismatch is a refusal
(`analyse_mesh_family.py`). Never from a target, a filename or a dict.

| level | `h_bg` (m) | **cells** | faces | points | `Mesh has N geometric (non-empty/wedge) directions` |
|---|---|---|---|---|---|
| coarse | 0.8 | **128,230** | 412,424 | 157,874 | **3** `(1 1 1)` |
| medium | 0.4 | **748,658** | 2,339,051 | 847,844 | **3** `(1 1 1)` |
| fine | 0.2 | **5,025,587** | 15,428,919 | 5,399,493 | **3** `(1 1 1)` |

Dimensionality is matched **literally** against
`Mesh has N geometric (non-empty/wedge) directions`. The `solution (non-empty)`
line is **never** read: it counts a wedge direction as present and would certify
a wedge case as 3-D. Both lines are recorded above only so the difference is on
the record; the gate reads the first.

### 4.4 DELIVERED RATIOS — and why this family is deliberately UNEQUAL-r

| step | cell ratio | `r_effective = ratio^(1/3)` |
|---|---|---|
| coarse → medium | **5.8384** | **1.8007** |
| medium → fine | **6.7128** | **1.8864** |

**Both inside the Case Protocol stage-1 band [1.5, 2.0].**

`h_bg` is halved exactly, so a purely volume-filled mesh would deliver **8×**
(r = 2) and a purely surface-banded mesh **4×** (r ≈ 1.587): a refinement shell of
thickness `k·h` around area `A` holds `A·k/h²` cells and so scales as `r²`, not
`r³`. A real external-aero mesh is a mixture, so the delivered ratio must land
**between 4 and 8** — measured 5.84 and 6.71, exactly as predicted.

**This is why the nominal scaling is 2 and not 1.5.** At a nominal 1.5 the same
dilution lands the delivered `r_effective` between 1.31 and 1.5 — below the band
floor, refused *after* the compute is spent. (The MRF build delivered 1.4157 /
1.4264 against a registered 1.5 for exactly this reason.) A nominal 2 cannot
fall below 1.587 whatever the mix.

**Registered as an UNEQUAL ladder, deliberately.** `scripts/roache_triple.py`
sets `EQUAL_RATIO_TOL = 1.0e-9`; the measured gap `|r21 − r32| / mean = 0.0465`
is seven orders of magnitude above it. `grade_ladder` is invoked with
**`form="unequal"`**, stated explicitly rather than left to `form="auto"` —
auto would resolve to the same branch, but a registered path is not a defaulted one.
The registered ratios are **r21 = 1.8007** and **r32 = 1.8864**, `dim = 3`.

### 4.5 `checkMesh` quality — OUR OWN run, full flag set

`checkMesh -allGeometry -allTopology -constant`, run by `mesh/run_build.sh` on
each level. Stage 1 as written substring-matches a pre-existing log it did not
produce; these are our own runs, and the plain run is recorded beside the full one.

| | coarse | medium | fine | admission |
|---|---|---|---|---|
| max non-orthogonality | 64.76 | 64.41 | 64.94 | ≤ 70 — **PASS** |
| average non-orthogonality | 10.03 | 7.35 | 5.45 | (recorded) |
| severely non-orthogonal (>70°) faces | 0 | 0 | 0 | **PASS** |
| max skewness | **6.33** | **18.06** | **10.32** | ≤ 4 — **FAIL**, see below |
| faces above the skewness limit | 7 | 29 | 16 | of 0.41M / 2.34M / 15.4M |
| max aspect ratio | 15.35 | 12.99 | 8.86 | `OK` |
| min face area (m²) | 2.31e-05 | 3.30e-06 | 3.17e-07 | `OK` |
| cells, determinant < 0.001 | 15 | 36 | 87 | (recorded) |
| concave cells | 6,345 | 20,482 | 78,465 | (recorded) |
| **negative-volume cells** | **0** | **0** | **0** | **PASS** |
| **`Failed N mesh checks` — FULL** | **3** | **3** | **3** | |
| **`Failed N mesh checks` — PLAIN** | **1** | **1** | **1** | |

**Negative-volume counts are independently confirmed.** An independent reader
(`analyse_mesh_family.py`) recomputes every face area and every cell volume from
`points`/`faces`/`owner`/`neighbour` by the divergence theorem and finds
**0 non-positive cells on all three levels**.

**UNRESOLVED, and referred to the supervisor: the skewness admission gate.**
`docs/standards/MESH_STANDARD.md` acceptance is ≤ 4 skewness. All three levels
exceed it, on 7 / 29 / 16 faces respectively (1.7e-5, 1.2e-5, 1.0e-6 of faces).
Taken literally, **all three levels are inadmissible and this family cannot be
frozen.** This lane does not have the authority to retire or reword a standard's
threshold (that is reserved), and does not quietly accept it. It is named here as
a decision the supervisor must take before §13 is filled.

---

## 5. THE TWO MANDATORY GATE LIMBS

### 5.1 LIMB A — full-flag `checkMesh`, and never from rc or a substring

> **Registered:** a level is admitted only if its own
> `checkMesh -allGeometry -allTopology` run reports **no `Failed N mesh checks`
> line** and **0 negative-volume cells**, the latter independently confirmed by
> the divergence-theorem reader. The verdict is parsed from the
> `Failed N mesh checks` line. It is **never** taken from `checkMesh`'s exit code
> and **never** from the substring `"Mesh OK."`.

**Measured on this very case, which is why the limb is written this way:**

- `checkMesh` returned **rc = 1** on the broken layer mesh (52,165 negative-volume
  cells) and **rc = 0** on all three delivered levels **while each printed
  `Failed 3 mesh checks.`** The exit code is unreliable in **both** directions.
- The full flag set found **3** failing checks per level where **plain `checkMesh`
  found 1** — it misses `Cells with small determinant` and
  `Concave cells (using face planes)`, both `-allGeometry` checks. Plain
  `checkMesh` under-reports this family by two checks on every level.

### 5.2 LIMB B — the geometry limb a cusp cannot pass

A cusp — a feature that closes to a point with zero cells across it — passes
`checkMesh` under both flag sets. It cannot pass this.

> **Registered, per level, over the 47 named wall features that the mesh can carry:**
> **(B1)** every one of the 47 named wall patches exists and has
> **`nFaces ≥ 20`**;
> **(B2)** for every one, the **wall-face-area ratio** `A_mesh / A_STL` lies in
> **[0.70, 1.15]** — a floor because a crushed or cusped feature loses area, and a
> **ceiling** because a feature smeared across neighbouring cells gains it;
> **(B3)** the two `TirePlinth*` pads are registered as **KNOWN ABSENT** at every
> level (§4.1) and are excluded from B1/B2 by name — never by silence.
> Any level failing B1 or B2 is **dropped from the family**; if fewer than three
> levels survive, **stage 2 must not run**.

**Measured now, against the built family** (`PATCH_LIMB_MEASURED.json`):

| | coarse | medium | fine |
|---|---|---|---|
| named wall patches present | 47 / 49 | 47 / 49 | 47 / 49 |
| patches with **zero** faces | 0 | 0 | 0 |
| **min `nFaces` on a patch** | **6** | **30** | **135** |
| **min area ratio** `A_mesh/A_STL` | **0.0974** | **0.5989** | **0.7689** |
| max area ratio | 1.2078 | 1.0746 | 1.0232 |
| worst feature | `NotchbackWindowrearframe` | `BrakeDiscrear` | `NotchbackWindowrearframe` |

The limb converges monotonically toward 1 (0.0974 → 0.5989 → 0.7689) — the
family is resolving the geometry, which is what a grid family must do.

**Consequence, stated plainly and not softened: on the registered thresholds the
COARSE LEVEL FAILS LIMB B** — `nFaces = 6` against B1's 20, and area ratio 0.0974
against B2's 0.70. `NotchbackWindowrearframe` (0.0244 m²) survives as 6 faces
carrying 9.7 % of its area, and `BrakeDiscfront` as 11 faces carrying 23 %. The
coarse level is dropped, which leaves **two** levels, which is **not a triple**.

This is the second thing the supervisor must settle before freezing, and the
honest options are: (a) coarsen the family by one step (build a level between
coarse and medium and drop coarse), (b) raise surface refinement so the coarse
level carries its small features, or (c) register B1/B2 thresholds the coarse
level can meet — which this lane will not do, because a threshold chosen to admit
the level in hand is the thing pre-registration exists to prevent.

---

## 6. WALL TREATMENT — THE BLOCKER, WITH THE COUNTER-EXAMPLE MEASURED

The family carries **no prism layers**: snappyHexMesh's layer-addition phase is
defective on this geometry (§12.1) and was disabled to obtain a valid mesh.

**Consequence, measured.** Without layers, the first cell centre is `h_surf/2`,
and `h_surf` halves with `h_bg`. With `u_τ = U∞ √(Cf/2) = 1.4116 m/s`
(`Cf = 0.058·Re_x^{-0.2}` at `Re_x = 5.16e6`) and `ν = 1.507e-05`:

| level | `h_surf` (m) | first-cell centre (m) | **y⁺** |
|---|---|---|---|
| coarse | 0.0500 | 0.0250 | **≈ 2342** |
| medium | 0.0250 | 0.0125 | **≈ 1171** |
| fine | 0.0125 | 0.00625 | **≈ 585** |

Two things are wrong, and the second is the disqualifying one:

1. y⁺ is far above the 30–100 target and above the ~300 where standard wall
   functions stay defensible.
2. **y⁺ changes by 4× across the triple.** The wall model is therefore a
   *different model* on each level, and the Roache order would be measuring the
   closure changing with the grid rather than the grid converging. **That is the
   measured counter-example** that justifies the class-default departure the
   generator implements — `relativeSizes false` with an absolute 0.75 mm first
   layer, matching DrivAerML's own near-wall spacing (paper l.272: 7 layers,
   0.75 mm first layer, 12 mm total, growth 1.2–1.4), which would hold y⁺ ≈ 35
   constant on all three levels. That setting is **written into the generator and
   currently unreachable**, because layer addition does not work (§12.1).

**This rung is not freeze-ready until §6 is resolved.** Registering a ±10 % Cd
gate on a triple whose wall model varies 4× across it would be a gate that cannot
mean what it says.

---

## 7. CLOSURE AND NUMERICS

`simpleFoam`, incompressible, steady. **kOmegaSST** with wall functions
(`nutkWallFunction`, `kqRWallFunction`, `omegaWallFunction`) — the class default
for external automotive aero; DrivAerML itself is wall-modelled scale-resolving,
and a wall-function RANS rung is the cheapest defensible parity check.

Schemes: `steadyState`; `cellLimited Gauss linear 1` gradients;
`bounded Gauss linearUpwind grad(U)` for momentum; `bounded Gauss limitedLinear 1`
for k and ω; `Gauss linear corrected` Laplacians; `corrected` surface-normal
gradients; `meshWave` wall distance. `SIMPLE` with `consistent yes`,
`nNonOrthogonalCorrectors 0`, relaxation 0.9.

**Class-default departures, each named:** (i) `relativeSizes false` on layers —
justified by the measured 4× y⁺ sweep in §6, currently unreachable; (ii) no
symmetry plane where the class default for a road car is a half-model — justified
by the measured asymmetry in §4.2.

**Solver-config requirement, a freeze precondition.** Fixed iteration count
`endTime`, `deltaT = 1`, **hard stop, NO `residualControl` early exit**, so
`last == endTime` is reachable and the `ExecutionTime` count equals
`round(endTime/deltaT)`. Iterative convergence is judged by the grader from final
Initial residuals, not by a solver stop.

**Solver-tolerance vs gate.** The loosest solver tolerance must be strictly
tighter than the tightest gate: `p` 1e-8, `U/k/ω` 1e-9, against a gate band of
2.76e-02 in Cd. Satisfied by six orders of magnitude.

---

## 8. COMPLETION RULE (rule 4, all clauses, all-or-nothing)

A level is **done** only if **all** hold, and a comparator **refuses (exit 2)
rather than degrades** if any is missing:

1. `rc == 0`, read from an **rc sidecar written INSIDE the detached wrapper** —
   never inferred from an `End` line (`setsid timeout cmd` exits 0 for every
   outcome);
2. an `End` line in `log.simpleFoam`;
3. **last time == `endTime`**;
4. incompressible-RANS field set **`p U k omega nut phi`** present at `endTime`;
5. `ExecutionTime` count == `round(endTime/deltaT)` (clause 5; `deltaT = 1` here);
6. **every field at `endTime` NEWER than the case's own `0/T`** — the age guard.

**Age-guard precondition, registered because it bites this case.** The mesh
directories already exist and are dated 2026-09-10. The launcher must create
`0/` by copying `0.orig/` **at launch** so the age guard dates the run, and must
refuse a case in which a time directory already exists. The generator writes no
`0/` for exactly this reason.
*Recorded honestly:* the age guard cannot distinguish a solver-written field from
a post-processor-written one (the F25 finding, 2026-09-10). It is necessary here,
not sufficient.

---

## 9. THE GRADER AND THE GRADING PATH — pinned by blob

| role | path | sha256 (16) | git blob (16) |
|---|---|---|---|
| comparator | `cases/navier_class/DRIVAER/grade_drivaer.py` | `f461cb05fc1dda41` | `d33f4fa1e2bb1cc0` |
| shared triple | `scripts/roache_triple.py` | `6dddbb87c4c9a429` | `78e56a3bc2c2a075` |
| mesh generator | `cases/navier_class/DRIVAER/mesh/build_drivaer_level.py` | `7eaff652307537dc` | `d93a6715d62f28fc` |
| mesh analyser | `cases/navier_class/DRIVAER/mesh/analyse_mesh_family.py` | `54b5dde3a82664ca` | `060ca2a18a828c86` |
| build runner | `cases/navier_class/DRIVAER/mesh/run_build.sh` | `7577f707d17e0718` | `f4bf95a57df340ce` |
| STL | `…/drivaerml_r7a5c094/run_466/drivaer_466.stl` | `9fd0eec1f436e336` | (outside git) |

**Verified, not assumed:** the grader on disk hashes to `f461cb05fc1dda41…`, and
`git cat-file -p c17e03c37:cases/navier_class/DRIVAER/grade_drivaer.py` hashes to
the **same** value. The frozen file *is* the committed file.

Registered invocation (a list, so an omission is a diff and not a parse):

```
python3 {GRADER} --coarse {CASE[coarse]} --medium {CASE[medium]} --fine {CASE[fine]} \
                 --reference {REFERENCE}
```

`--reference` is **mandatory and pinned here verbatim**: SUBOFF R1b produced no
graded number because its frozen launcher omitted exactly this flag.

The grader must, and its diff-read by the supervisor must confirm it does:
plant a live control into the **gate reader itself** (`read_coeff` on a copy of
the finest `coefficient.dat`, for Cd and Cl separately) and refuse unless the
value moves by the plant; plant a second control into the `p` field and refuse
unless the body mean surface pressure moves by `PLANT/n_body`; assert
`magUInf / lRef / Aref / rhoInf / CofR` **on disk** equal §1.5 or refuse; read
iterative convergence rather than defaulting it; and call `grade_ladder` with
`dim = 3`, `form = "unequal"`, redefining no `P_MIN` or `STAGNANT_FLOOR`.

### 9.1 THE GRADER AND ITS REFERENCE FILE BOTH CONTRADICT §1.5 TODAY

Not a suspicion — read off the files, with lines, so check-1 starts from evidence:

`cases/navier_class/DRIVAER/grade_drivaer.py` **hard-codes the superseded
constants** and then asserts them on disk:

```
65: L_REF           = 2.786      # m    (wheelbase; DrivAerML characteristic length)
66: A_REF           = 2.17       # m2   (DrivAerML reference frontal area)
67: RHO_INF         = 1.225      # kg/m3 (air; CONFIRM against DrivAerML rho at freeze)
...
240:    got  = {k: _get(k) for k in ("magUInf", "lRef", "Aref", "rhoInf")}
241:    want = {"magUInf": MAG_U_INF, "lRef": L_REF, "Aref": A_REF, "rhoInf": RHO_INF}
```

Against §1.5 (`lRef 2.79`, `Aref 2.298`, `rhoInf 1.0`) **all three differ**, so
the grader as committed would refuse a correctly-configured case — the assertion
working exactly as designed, against the wrong target.

`verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json` carries
`"Aref_m2": 2.17`, `"rho_kg_m3": 1.225`, `"L_ref_m": 2.786`, a **placeholder**
`"Cd": 0.28` ("PROVISIONAL: mid-scatter placeholder") and **`"Cl": null`**.

**The `null` Cl is the dangerous one.** Its own note says *"Leave null to skip
gate V2 until pinned"* — so gate V2 would be **skipped silently** and the run
would still return a verdict. That is the SUBOFF `armed: by_data` failure mode
exactly: a limb that disarms itself on missing data and reports nothing about it.
§2 registers `Cl_ref = −0.05357145`, so V2 is armed and must not be skippable.

**Required before freeze, and it is check-1, the supervisor's, undelegated:**
update lines 65–67 and the reference JSON to §1.5, and make a `null` `Cl`
a **refusal** rather than a silent skip. This lane has changed neither file:
altering a comparator is not a drafting lane's call.

---

## 10. MONITORS — one registered action each

| id | condition | **the one action** |
|---|---|---|
| M1 | `p` Initial residual has not fallen below 1e-3 by iteration 1500 | **STOP that level**; label `BLOCKED-numerics` |
| M2 | any written `Cd` outside [−1, 1] | **STOP that level**; label `NOT A RESULT` |
| M3 | a level exceeds its per-level cap in core-minutes (§11) | **STOP the run** — an overrun does not get a new budget (rule 12) |
| M4 | `log.simpleFoam` contains > 200 `bounding omega` lines | **STOP that level**; label `BLOCKED-numerics` |
| M5 | a level's wall-clock row exceeds 3600 s with no new write | **STOP that level**; record the row as a stall, gross not cleaned |

---

## 11. COST (rule 12 — core-minutes; c7a.4xlarge $0.0513/core-h)

**Already spent, MEASURED from `/usr/bin/time -v` in each build's `BUILD_RC`,
serial (1 rank):**

| build | wall s | core-min | peak RSS |
|---|---|---|---|
| `r1_coarse` | 74.3 | 1.238 | 368 MB |
| `r1_medium` | 387.3 | 6.454 | 1,107 MB |
| `r1_fine` | 2,498.3 | 41.639 | **6,568 MB** |
| 3 diagnostic builds (§12) | 370.4 | 6.173 | 484 MB |
| **TOTAL MESHING** | **3,330.3** | **55.505** | |

Derived: 55.505/60 × $0.0513 = **$0.0475, DERIVED NOT MEASURED** (the box cannot
read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5).

Peak RSS is the fine level's **`checkMesh -allGeometry -allTopology` at 6,568 MB
(6.41 GB)**, *above* snappyHexMesh's own 5,762 MB (5.63 GB) — the check, not the
mesher, is the memory high-water mark, and on a 30 GB box with concurrent solvers
that is the number that matters.

**Solve, ESTIMATED — no DrivAer precedent exists in this lab, so this is an
estimate and is labelled one.** Basis: 3,000 SIMPLE iterations per level at an
assumed 30,000 cell-iterations per core-second.

| level | cells | estimated core-min |
|---|---|---|
| coarse | 128,230 | 214 |
| medium | 748,658 | 1,248 |
| fine | 5,025,587 | 8,376 |
| exercise smoke | — | 50 |
| **point estimate** | | **9,888** |

> **CAP, to be frozen: 16,000 core-minutes** for the whole rung.
> Derived: 16,000/60 × $0.0513 = **$13.68, DERIVED NOT MEASURED.**

**Cap-exempt as a 3-D case** under Sanaa's 2026-09-10 words — **still costed; the
estimate is calibration data, not a gate.** Estimate-vs-actual lands in
`docs/COST_CALIBRATION.md` at completion (rule 12).

---

## 12. FINDINGS SURFACED, NOT WORKED AROUND

### 12.1 snappyHexMesh layer addition corrupts the mesh, adds no cells, and reports success

Measured on the coarse level, three configurations
(`DIAG_v1_…`, `DIAG_v2_…_BROKEN`, `DIAG_v3_…` beside the family):

- With `addLayers true`, the delivered mesh has **52,165 negative-volume cells of
  128,230 (40.7 %)**, minimum cell volume **−25.19 m³**, maximum face area
  **54.24 m²** where the largest legal face is 0.64 m², max non-orthogonality
  **179.7°** and **average 79.9°** on a mesh that is 88 % hexahedra.
- **Cell count is IDENTICAL to the no-layer build (128,230 both).** Zero layer
  cells were added. Face count *fell* (411,124 vs 412,424): the phase **merged**
  4,001 + 1,197 sets of faces, producing self-intersecting faces — which is what
  a 54 m² face and a negative cell volume are.
- snappyHexMesh's own final check printed **all zeros** ("non-orthogonality > 65 :
  0", "face pyramid volume < 1e-13 : 0", …) and **"Finished meshing without any
  errors"**, having logged `Detected 52226 illegal faces` mid-phase.
- Its layer table simultaneously claims **5 layers, 0.75 mm near-wall, ~6.2 mm
  overall on 47 of 49 patches** — on a mesh to which it added no cells.
- The same three numbers were reproduced with explicit feature snapping, implicit
  feature snapping, and snap tolerances 2.0 and 1.0: **the feature-snap
  configuration is not the cause.** Turning layers off alone fixes it
  (0 negative cells, non-orthogonality max 64.8, average 10.0).

Independently confirmed by a reader that does not use OpenFOAM and is planted
against a pure `blockMesh` control (`PLANT_blockMesh_control`): on 24,375 cubes of
side 0.8 m it returns every volume 0.512 m³ and every face area 0.64 m² to
**7.4e-15** worst error. A reader not shown able to read a mesh it knows the
answer to is not evidence.

**This is a defect note and it is `NOT FILED` (rule 7).** Nothing is sent.

### 12.2 `checkMesh`'s exit code is unreliable in both directions

rc = 1 on the broken mesh; **rc = 0 on all three delivered levels while each
printed `Failed 3 mesh checks.`** Any verdict of the form
`("Mesh OK." in out) and rc == 0` is worthless in both directions. §5.1 is
written from this measurement.

### 12.3 The `-allGeometry -allTopology` flags are load-bearing

Plain `checkMesh` reports `Failed 1 mesh checks` on every level where the full
set reports 3, missing `Cells with small determinant` and `Concave cells (using
face planes)`. A `grep` for these flags across `scripts/` returned **zero hits
lab-wide** before this rung.

---

## 13. FREEZE BLOCK — LEFT DELIBERATELY BLANK

Check 4 is the supervisor's, personal, and may not be delegated. This lane
neither froze, launched nor committed anything.

| field | value |
|---|---|
| frozen at commit | |
| freeze sha | |
| frozen by | |
| date (UTC) | |
| §4.5 skewness admission decision | |
| §5.2 coarse-level Limb-B decision | |
| §6 wall-treatment resolution | |
| §9 grader re-diff-read against §1.5 | |

**Three things must be settled before this block can honestly be filled:** the
skewness admission conflict (§4.5), the coarse level's Limb-B failure and the
two-level family it would leave (§5.2), and the wall treatment (§6). Results,
when they exist, land in `verification/campaign/DRIVAER_R1_RESULTS.md` citing this
file by commit hash.
