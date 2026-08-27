# G2 — GRID-CONVERGENCE TRIPLE ON `DUCT/AR_1_Ret_360`

**Rung:** `G2_grid_triple_duct`
**Team:** closure
**Status:** `prereg_commit: PENDING_SUPERVISOR_FREEZE`. The gates, thresholds,
cap and label below are drafted and are not yet closed; the freeze is the
supervisor's act, performed personally under `SUPERVISION_CHARTER.md` §3 check 4,
and it is a commit whose message carries the sha256 of this document and of all
three instruments. Nothing has been staged into the run root, no queue entry has
been filed, and no compute has been spent. **Standing rule 2 closes these gates
at the freeze; before it, amendments are legal and must state the condition and
how it was checked.**
**Drafted:** 2026-08-27, by a closure drafting lane on the closure supervisor's
dispatch.

**Naming.** This is **G2**: the second entry in the **G column** of
`cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md` — grid convergence. It
claims nothing about the R ladder (`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md`
defines R1–R6; R6 is unstarted and awaits Sanaa's own phrasing).

---

## 1. The question, what it does not claim, and a correction to the record

**Question.** Does the shipped k-omega SST solution of the square duct at
`Re_tau = 342`, held completely fixed, converge under systematic grid
refinement; and what observed order and fine-grid GCI does it deliver?

**Why this rung exists.** G1 is closure's first refinement family, and it stands
on **one** geometry. Verification's audit records closure's `G` column as `NO` on
every capability row, on the ground that the family has fixed benchmark meshes
throughout. G1 closes that for the periodic hill and, by its own §10 item 8,
**leaves every other geometry exactly where it was**. G2 closes it for a second,
structurally different geometry — a straight duct rather than a separated hill.

### 1.1 The corpus claim, corrected, and this is the wording that is true

The claim on the board and in verification's file — *"40 geometries, ZERO at
more than one cell count"* — is **FALSE as literally worded**, and the closure
supervisor re-measured it (D542, L-355): **344 `polyMesh` directories, 38
distinct bounding boxes, and TWO boxes carry two cell counts** —
`AR_1_Ret_180` (2,209 = 47²) with `AR_1_Ret_360` (3,025 = 55²), and
`AR_3_Ret_180` (6,627 = 3·47²) with `AR_3_Ret_360` (8,748 = 3·54²).

**Those are not refinement families.** The counts differ because `Re_tau` goes
180 → 360, so they are two discretisations of **two different continuum
problems**, which Roache forbids comparing; and two levels is not a triple.

> **The correct statement is: zero geometries at more than one cell count AT
> FIXED PHYSICS.** This pre-registration uses that wording and no other.

### 1.2 What this rung does NOT claim

* **It grades NUMERICAL CONVERGENCE ONLY.** No reference field is read; the
  shipped `0/U_LES`, `0/k_LES` and `0/tauij_LES` exist only on the 3,025-cell
  mesh and are **not staged**. A Roache triple compares one fixed model's
  numerical solution against itself at three resolutions.
* **It is not a closure result.** `CLOSURE_MODELLING_CHARTER.md` §2 is not
  engaged: G2 scores no model, predicts no `b_ij`, applies no correction.
* **It is not a validation.** A CONVERGING triple with a small GCI says the
  discrete equations are being solved consistently. It says nothing about
  whether k-omega SST is right — and on this case §4.1 records precisely the
  place where it is known to be wrong.

---

## 2. Substrate, and every number in this section was measured on this box

**Source case (read-only, never modified):**

    /home/ubuntu/closure-challenge-benchmark/data/DUCT/AR_1_Ret_360

A quarter of a square duct: streamwise-periodic, `h = 1 mm` channel half-height,
`AR = 1`, `Re_b = 5693`, `Re_tau = 341.9805`, `nu = 1.5e-5 m²/s` (`caseDef`).
`u_tau = Re_tau · nu / h = 5.12971 m/s`, derived.

### 2.1 The candidate survey, and why the duct and not something else

Measured, not believed. `find` for `blockMeshDict*`, `*.m4`, `mesh*.py`, `*.geo`
and `snappyHexMeshDict*` over the whole benchmark returns **29 hits, every one of
them under `Parm_PH_29`**. `CBFS`, `PH_Breuer`, `NASA_2DWMH` and all eight
`DUCT` cases ship a frozen `constant/polyMesh` and **no mesh dictionary at all**.
The board's statement is therefore confirmed from disk.

The question the board did not ask is whether a dictionary can be written **from
the geometry** rather than recovered. For the duct the answer is yes, and §6.1
turns that answer into an executable control rather than a claim.

### 2.2 What is DERIVABLE and what would have been a CHOICE

| element | derivable from the shipped `polyMesh`? | how |
|---|---|---|
| **vertices** | **DERIVED, exactly** | the mesh is a box; `min`/`max` per axis give `Lx = Ly = Lz = 1.000000 mm`. No interior vertex exists to guess. |
| **block resolution** | **DERIVED, exactly** | 2 distinct `x` planes (one cell), 56 distinct `y` and 56 distinct `z` planes → `1 x 55 x 55` |
| **grading law** | **DERIVED, exactly** | the `y` and `z` spacings are a geometric progression with per-cell ratio **0.909090908698 ± 3.8e-08** across all 54 ratios — that is `1/1.1` to **2.4e-10 relative**. `blockMesh`'s `simpleGrading` *is* a geometric progression, so the law is not approximated: it is recovered. |
| **grading VALUE carried into the family** | **a registered CHOICE between two derivations** | the measured total ratio is `0.0058182850083`; the closed form `1.1^-54` is `0.00581828514412`; they differ by **2.3e-08 relative**. The closed form is registered (§3.4 gives the reason, which does not mention any answer). |
| **patch assignment** | **DERIVED, exactly** | each of the six patches is one face of the box on a distinct constant-coordinate plane, measured face by face: `inflow` `x=0`, `outflow` `x=Lx`, `wallTop` `y=Ly`, `wallSide` `z=Lz`, `symmetryBottom` `y=0`, `symmetrySide` `z=0`. Nothing is ambiguous and nothing is inferred from a name. |
| **patch TYPES** | **DERIVED, exactly** | read from the shipped `constant/polyMesh/boundary`: `cyclic` / `cyclic` / `wall` / `wall` / `symmetry` / `symmetry`, with `neighbourPatch` given. |
| **the cyclic pairing direction** | **DERIVED** | the shipped `boundary` names `outflow` as `inflow`'s `neighbourPatch` and vice versa. |
| **the streamwise cell count** | **DERIVED** | 1, from the two distinct `x` planes. It is held at 1 across the family (§3.3), which is a registered choice with a stated reason. |

**No element of the geometry is a free choice.** The two registered choices are
the grading value's derivation route (§3.4) and the level anchor (§3.2), and both
carry reasons in §13 that do not mention any answer.

### 2.3 The reconstruction, executed

The constructed dictionary at the **shipped** resolution was meshed under
OpenFOAM **v2606** and compared against the shipped `constant/polyMesh`:

| quantity | shipped | regenerated |
|---|---|---|
| `nPoints` | 6,272 | **6,272** |
| `nCells` | 3,025 | **3,025** |
| `nFaces` | 12,210 | **12,210** |
| `nInternalFaces` | 5,940 | **5,940** |
| patch types | cyclic ×2, wall ×2, symmetry ×2 | **identical** |

**Maximum point deviation: `4.800e-14 m`, i.e. `4.8e-11` of the 1 mm side** —
and in the shipped point ORDERING, not merely as a set, which is itself evidence
that the shipped mesh was produced by `blockMesh` from an equivalent dictionary.
The deviation is at the shipped ASCII file's own write precision. `build_g2.py`
re-runs this comparison at stage time and **refuses (`sys.exit(2)`)** above
`1e-9 m` (§6.1).

### 2.4 Everything else the levels inherit, and it is mesh-independent

| item | value | how established |
|---|---|---|
| turbulence model | `kOmegaSST`, `constant/turbulenceProperties:22` | read |
| driving force | `meanVelocityForce`, name **`meanVelocity1`**, `Ubar = (Re_b·nu/h, 0, 0)`, `selectionMode all` | `system/fvOptions` |
| wall treatment | `nutLowReWallFunction` + `omegaWallFunction` — wall-resolved | `0/nut`, `0/omega` |
| convection | `div(phi,U)`, `div(phi,k)`, `div(phi,omega)` **all** `bounded Gauss linearUpwind` | `system/fvSchemes` |
| gradients | `grad(k)` and `grad(omega)` **`cellLimited Gauss linear 1`**; `grad(U)` unlimited | `system/fvSchemes` (the limiter is a registered risk, §10 item 5) |
| laplacians | `Gauss linear corrected` | `system/fvSchemes` |
| all five staged initial fields | `internalField uniform <symbolic>`, boundary entries naming only the six patches | parsed: **every one is mesh-independent and stages onto any of the three meshes unchanged** |
| `libs` line | `libs ( "libfrozenIncompressibleTurbulenceModels.so" );` | `system/controlDict:18` |
| OpenFOAM | **v2606 (ESI)**, `/usr/lib/openfoam/openfoam2606` | `blockMesh`, `checkMesh` run |

**The named library is NOT on this box** (`find /` returns nothing;
`$FOAM_USER_LIBBIN` holds four other closure libraries). Standing rule 14 and
M1 §5.6 forbid deleting a `libs` entry to tidy a case, so it is **kept**. The
consequence was measured rather than assumed: a `controlDict` carrying that
exact line was fed to `checkMesh` under v2606 and the loader emitted
`Could not load "libfrozenIncompressibleTurbulenceModels.so"` and **returned
rc = 0**. The comparator records the warning as `I5`, an INFRASTRUCTURE defect
that voids nothing. *This lane tested the loader through `checkMesh`, not
through `simpleFoam`; the loader is the same `dlLibraryTable`, but that is an
inference and L1 is the fail-fast.*

**What this substrate section cannot establish.** `blockMesh` and `checkMesh`
prove the constructed dictionaries mesh under v2606. They do **not** prove
`simpleFoam` will run this case under v2606; this lane launched no solver. The
fail-fast is **L1 itself**, at a registered `92 s` (§7).

---

## 3. The three levels, and the arithmetic

### 3.1 The registered triple

| level | role | `N` per cross-plane direction | cells | `endTime` | `timeout` (s) |
|---|---|---|---|---|---|
| **L1** | coarse | 32 | **1,024** | 20,000 | 300 |
| **L2** | medium | 64 | **4,096** | 30,000 | 1,500 |
| **L3** | fine | 128 | **16,384** | 40,000 | 5,400 |

Cells `= 1 · N · N`. **These counts were measured, not computed**: `blockMesh`
rc 0 at all three under v2606, `nCells` read back from each
`constant/polyMesh/owner` note as 1,024 / 4,096 / 16,384.
`4096 = 4 · 1024` and `16384 = 4 · 4096`, **exactly**.

### 3.2 The anchor is 32, and the reason names no answer

`r` must be exactly 2 at both steps: a non-constant `r` is legal under ASME
V&V20 but replaces the closed form for `p` with a fixed-point iteration that can
itself fail to converge, on a rung whose entire product is a defensible `p`. So
`N` must double twice, which the shipped 55 cannot do.

**32 is registered because it is the largest power of two below the shipped 55.**
The family therefore spans `[32, 128]` and the shipped resolution lies **inside**
that span rather than outside it. No other property of 32 was considered and no
candidate anchor was tried and compared.

### 3.3 `D` is 2, and the reason here is not G1's reason

G1's `D = 2` rests on an `empty` direction. **This mesh has no `empty`
patch**: the streamwise direction is one cell between **matched `cyclic`**
patches. The argument must be made afresh and it is:

* refinement is applied in `y` and `z` only; the cell count scales as `N²`;
* over a single cell between matched cyclic patches, periodicity makes the
  streamwise gradient identically zero and the two cyclic face fluxes equal and
  opposite by construction, so the `x` direction carries **no discretisation
  error to refine away**.

`D = 2`, the representative cell size is `h = (A/N)^(1/2)` with
`A = Ly·Lz = 1e-06 m²` identical at every level, and

    r21 = h(L2)/h(L3) = (16384/4096)^(1/2) = 2.0000
    r32 = h(L1)/h(L2) = ( 4096/1024)^(1/2) = 2.0000

Using `D = 3` with `N_x` held at 1 would give `r = 4^(1/3) = 1.5874`, a **26 %
understatement of the refinement**, which inflates the apparent order by
`ln2/ln1.5874 = 1.50x`. `D = 3` is registered as **wrong for this mesh** and the
comparator hard-codes `D_SPATIAL = 2`.

**The streamwise cell count is held at 1 across the family**, and this is a
registered choice: halving it is impossible, and doubling it would add cost
while adding no discretisation to a direction whose gradient is identically
zero — and would destroy the exactness of the argument above.

### 3.4 The grading is held at a FIXED TOTAL RATIO, which is what makes the three meshes one family

The shipped mesh is `simpleGrading` with per-cell expansion `1.1` toward each
wall, measured constant to `2.4e-10` relative. Registered:

    simpleGrading (1 R R),  R = 1.1^-54 = 0.00581828514411625,  IDENTICAL at all three levels

For `simpleGrading` with total ratio `R` over `N` cells, face positions satisfy
`x_j/L = (q^j - 1)/(q^N - 1)` with `q = R^(1/(N-1))`. As `N` grows at fixed `R`
this tends to the `N`-independent stretching function `x(s)/L = (R^s-1)/(R-1)`.
**Holding `R` fixed and changing `N` is exactly the operation that makes the
three meshes three discretisations of one continuous mapping** — which is what
systematic refinement means. Holding the *per-cell* ratio at `1.1` instead and
changing `N` changes the mapping itself and would give three different
geometries' meshes, not a family; every Roache formula below would be void.

**`R` is taken from the closed form `1.1^-54`, not from the measured
`last/first = 0.0058182850083`**, because the per-cell ratio is `1/1.1` to
`2.4e-10` while the endpoint ratio accumulates 54 rounds of the shipped file's
ASCII write precision. The two differ by `2.3e-08` relative. This is registered
as a derivation-route choice and it is made on precision grounds alone.

**The finite-`N` departure from exact self-similarity, MEASURED, and it is larger
than G1's.** From `checkMesh` on the three constructed meshes:

| level | wall cell height (m) | min cell volume (m³) | linear ratio to next coarser | volume ratio |
|---|---|---|---|---|
| L1 | 8.944559e-07 | 8.00051e-16 | | |
| L2 | 4.588845e-07 | 2.10575e-16 | **1.9492** (ideal 2, −2.5 %) | 3.7994 (ideal 4) |
| L3 | 2.323739e-07 | 5.39976e-17 | **1.9748** (ideal 2, −1.3 %) | 3.8997 (ideal 4) |

G1 registered the same idealisation at 0.33 % in area; **G2's is 15x larger**,
because this mesh's stretch (`R = 1/171.9`) is far stronger than G1's (`R = 10`).
It is registered here, quantified, and repeated in §10. Two honest observations
that are part of the registration and not a defence: the departure **halves from
level to level** (2.5 % → 1.3 %), which is the first-order decay the `1/N` limit
predicts; and it is a *local* departure at the smallest cell, while the GCI's
`r = 2` rests on `h = (A/N)^(1/2)`, which is exactly 2 by construction because
`A` is identical and `N` quadruples exactly.

### 3.5 Mesh quality does not change regime, and one number does change

Measured by `checkMesh` under v2606 on all three constructed meshes:

| level | max non-orthogonality | max skewness | total volume (m³) | max aspect ratio |
|---|---|---|---|---|
| L1 | **0** | 5.36e-13 | 1e-09 | 1,118 (63 cells) |
| L2 | **0** | 8.71e-13 | 1e-09 | 2,179.2 (1,180 cells) |
| L3 | **0** | 2.60e-12 | 1e-09 | 4,303.41 (8,103 cells) |
| *shipped, for reference* | 0 | 7.41e-13 | 1e-09 | 1,880.59 (721 cells) |

The mesh is **exactly orthogonal** at every level (a Cartesian box), skewness is
at machine zero, and the total volume is `1e-09 m³` at every level — identical to
the closed form `Lx·Ly·Lz` and to the shipped mesh. The `corrected` term in
`Gauss linear corrected` is therefore inactive and identical across the family.

**The aspect ratio does change, by 2x per level, and it is registered as a
non-issue with a mechanism rather than waved past.** It grows because the wall
cell shrinks in `y`/`z` while the streamwise cell stays `1 mm`. That direction
carries no gradient (§3.3), so the `x`-face contributions to every discrete
operator cancel identically; a large aspect ratio in a direction with an exactly
zero gradient has no discretisation consequence. `checkMesh` flags it as
`***High aspect ratio cells found` at every level, **including the shipped mesh**,
and still returns `Mesh OK` — the shipped benchmark case has always been in this
regime. The comparator records the numbers as a diagnostic and gates nothing on
them.

**Wall resolution does not change regime.** `y+` at the wall-cell centre,
derived at `u_tau = 5.12971 m/s`: **0.15294 / 0.07846 / 0.03973** across L1/L2/L3
(shipped: 0.09092). It falls monotonically and never approaches the `y+ ~ 1`
edge of the wall-resolved regime `nutLowReWallFunction` requires. `yPlus` is
written at every level as a recorded **diagnostic**, not a gate, so a regime
change would be visible in the record rather than inferred.

### 3.6 Iteration counts are NOT part of the refinement family

`endTime` is 20,000 / 30,000 / 40,000. SIMPLE's outer-iteration count to a given
convergence scales roughly with the linear mesh dimension, and each level is 2x
the previous linearly. The three levels are compared as **converged solutions**,
not equal-iteration solutions, and §6.4's plateau gate is what makes them
comparable.

**The margin is measured, on this box, on this archetype.** In
`/home/ubuntu/closure-data/aposteriori/kaandorp/AR_1_Ret_360__NULL/log.run`
(v2606, `nProcs 1`, 3,025 cells, 30,000 iterations, `residualControl` removed):

| channel | behaviour |
|---|---|
| `gradP` | within `1e-6` relative of its final value from **iteration 340** onward |
| `Ux` | 1.34e-13 at 5,000; **7.343e-16** at 30,000 |
| `k` | floor **9.577e-09**, reached by 5,000 and flat to 30,000 |
| `omega` | floor **9.770e-16**, reached by 5,000 |

Scaling by linear dimension, L3 (`N=128`, 2.33x the measured level) reaches the
`gradP` plateau near iteration 790 and the `k` floor near 11,600. **`endTime`
40,000 is 3.4x the scaled `k` floor and 50x the scaled `gradP` plateau.**

**`residualControl` is EMPTIED in all three runs** and this is forced, not
chosen: the shipped `fvSolution` carries `residualControl { k 5e-6; omega
1e-10; }`, and a solver-enforced early stop makes `last time == endTime` false
on **every** row, violating standing rule 4 universally. `build_g2.py` empties
every `residualControl` sub-dictionary with a cursor-walking scanner (the
defect M1 found and repaired: a scanner that re-searches from position 0 empties
at most one block while claiming to empty them all) and **refuses** if any body
survives or if the source held none at all.

---

## 4. Functionals. One primary, two secondaries, none needing reference data

### 4.0 THE PHYSICS OBJECTION, CONFRONTED BEFORE ANY FUNCTIONAL IS REGISTERED

**The objection.** M1 measured that on all eight ducts the `p`, `Uy` and `Uz`
initial residuals **never decrease**. Re-measured here on this box, at 30,000
iterations, `AR_1_Ret_360__NULL`:

| channel | it 1 | it 5,000 | it 30,000 | max over the final 10 % |
|---|---|---|---|---|
| `p` | — | — | **0.144** | 0.293 |
| `Uy` | 0.306 | 0.243 | **0.289** | 0.739 |
| `Uz` | 0.414 | 0.244 | **0.190** | 0.623 |

A linear eddy-viscosity model produces **no secondary flow** in a straight duct.
The in-plane velocity and pressure variation is at machine noise, OpenFOAM
normalises the residual by that noise, and the ratio is `O(0.1–0.7)` forever.
Whoever built the benchmark had already found this: the shipped duct
`residualControl` names `k` and `omega` and **not** `p`.

**The consequence, accepted in full: any functional built on an in-plane quantity
would be a Roache triple over noise, and a triple over noise is worse than no
triple.** No such functional is registered, and `p`, `Uy` and `Uz` carry **no
iterative-convergence threshold** in this pre-registration (§6.4). They are
recorded.

**Why a functional nevertheless survives.** The streamwise direction is not in
that regime. `Ux` converges to **machine zero** (7.343e-16) and `k` and `omega`
to their floors. The streamwise momentum balance — the quantity the model
genuinely produces — is a real, non-degenerate elliptic solution of
`div((nu+nut) grad Ux) + gradP = 0` coupled to k-omega SST, with `nut(y,z)` a
genuine two-dimensional field.

**And the objection was pushed one level further, because `gradP` is computed by
the fvOption twice per outer iteration from a volume average that the pressure
correction updates — so it could in principle carry the in-plane noise.** It
does not, and this was measured rather than argued. In the shipped OpenFOAM-7
log (`log.run`, 334 iterations, stopped early by `residualControl`) `gradP`
still wobbles by `1.05e-04` half-spread over its final 10 %. In the
**this-box, v2606, 30,000-iteration run with `residualControl` removed**,
`gradP` is **flat at 53007.9 over the final 15,000 iterations**: half-spread
`0.000e+00` at the log's six-significant-figure print resolution, and the
IC2 statistic `max|gradP − gradP_end|/|gradP_end|` over the final 10 % is
**exactly 0**. The 1e-4 wobble in the shipped log was the transient, cut short
at iteration 334.

*Honest bound:* "flat" there means flat to the log's print resolution, `1.9e-06`
relative. That is an **upper bound** on the plateau, not a measurement of the
true noise floor. §5.3's floor and §6.4's IC2 are both set **5x above that
bound**, and §6.2 raises the staged `writePrecision` to 12 so the same statistic
is a genuine measurement at grade time.

*Second honest gap:* the 30,000-iteration run used `kOmegaSSTCorrected` with a
null correction, not stock `kOmegaSST`. It is a linear-eddy-viscosity-class model
in the identical regime and its extra field solves make its rate an upper bound
(§7), but it is not the same binary. **No stock-`kOmegaSST` duct run of more than
200 iterations exists on this box.**

### 4.1 PRIMARY — `gradP`, the mean streamwise momentum source [m/s²]

The scalar the `meanVelocityForce` fvOption must supply to hold the
volume-averaged `Ux` at `Ubar = Re_b·nu/h`. The solver writes it to disk itself,
at every write time, as `gradient` in

    <endTime>/uniform/meanVelocity1Properties

**Confirmed present under v2606 by reading a file this box actually produced**,
not by assuming: `AR_1_Ret_360__NULL/30000/uniform/meanVelocity1Properties`
holds `gradient        53007.9;`. The filename follows the fvOption's own name,
which in this case is `meanVelocity1` (G1's is `momentumSource`).

**Why this is the primary.**

1. It is a **global integral of the direction the model actually solves**. By
   the streamwise momentum balance `gradP · V` equals the total wall shear
   force. Integral functionals converge monotonically far more often than local
   ones. It is not an in-plane quantity and §4.0 measures that it does not carry
   the in-plane noise.
2. It needs **no post-processing at all** — no `-postProcess` call, no
   interpolation, no probe. It is the one functional that survives a total
   post-processing failure, which is exactly the L-342 split (§6.5).
3. The solver writes it **twice by two paths** — to disk and to the log — so the
   comparator cross-checks two independent reads of one quantity (IC3).

### 4.2 SECONDARY-A — `Kint`, volume-integrated turbulent kinetic energy [m⁵/s²]

    Kint = sum_i k_i V_i

from `<endTime>/k` and `<endTime>/V` (`-postProcess -func writeCellVolumes`).
Global integral, no probe, no interpolation. The comparator **refuses** if
`sum(V)` does not match the closed-form domain volume `1e-09 m³` to `1e-6`
relative — a closed-form check that the volume field belongs to this mesh.

### 4.3 SECONDARY-B — `tauwint`, integrated streamwise wall shear [m⁴/s²]

    tauwint = sum over wallTop and wallSide of |tau_wx| * |Sf|

`tau_wx` from the `wallTop` and `wallSide` `boundaryField` entries of
`<endTime>/wallShearStress`; **the face areas `|Sf|` are computed by the
comparator directly from `constant/polyMesh`**, by the centroid-fan
decomposition, so the measure needs no post-processing artefact and the reader
is exact. The comparator **refuses** if either patch's summed area misses its
closed form `Lx·Lz = Lx·Ly = 1e-06 m²` by more than `1e-6` relative — verified
on the shipped 3,025-cell mesh at `1.000000000e-06 m²` on both patches.

**This is deliberately a second, INDEPENDENT PATH to the same physics as the
primary**, computed from completely different artifacts by completely different
readers. That is a virtue, and it is why the pair is registered rather than a
single functional plus padding.

#### 4.3.1 The momentum-balance identity, and its REGISTERED ALARM LEVEL

The streamwise momentum balance makes `gradP * V` equal the total wall shear
force, so the two quantities above should agree. The comparator prints the
relative disagreement at every level and compares it against a registered
**ALARM LEVEL of 5 %**:

    momentum-balance disagreement = |gradP * V - tauwint| / |gradP * V|
    REGISTERED ALARM LEVEL: 5.0 %

**This is an ALARM and it is NOT A GATE.** It cannot turn any functional or the
rung into a `GATE FAIL`, it cannot change the headline verdict, and it appears in
no verdict mapping in section 5.4. If it fires, the record carries
**`MOMENTUM-BALANCE ALARM`** beside the verdict and **the rung is NOT BELIEVED
pending supervisor triage** -- the verdict stands as computed and is read as
unconfirmed until the cause is found.

**Why an alarm, and why 5 %.** A *tolerance* here cannot honestly be justified:
the discrete balance closes only up to the `Ux` residual and the convection of
the in-plane noise field, and **this lane has measured neither**. But an
unbounded printed discrepancy is worse than one never computed, because a real
disagreement gets read past -- a printed figure labelled diagnostic-only is a
standing lesson in this lab, not a hypothetical. The level is therefore set as an
**order of magnitude, not a precision**. Every plausible defect mode in this pair
-- an incomplete or wrong face-area set, a dropped patch (a factor of 2 on a
two-wall quarter duct), a sign-convention slip, a units slip, a shear field read
off the wrong patch -- produces a disagreement of order 10 % or larger. The
legitimate slack is residual-driven and, for a solve whose `Ux` residual reaches
1e-15, is many orders below a percent. **5 % sits below every plausible defect
mode and, on that reasoning, above the legitimate slack -- but the second half of
that sentence is an expectation, not a measurement, and that is exactly why this
is an alarm and not a gate.**

**Measuring the true agreement is part of the first G2 run's purpose**, so that a
successor rung can register a real threshold from a reading instead of from this
argument. The measured disagreement is printed at every level whether the alarm
fires or not.

*`tauwint` is ALREADY fully gated as SECONDARY-B, with its own band [0.5, 3.0],
its 10 % GCI ceiling and its 1e-5 floor. The identity print therefore carries no
evidential weight the registered functional does not already carry -- only the
risk of being read past, which is what the alarm removes.*

### 4.4 Registered expectation, on record before the run

**Most likely monotone:** `gradP` — global, integral, in the direction the model
solves, and measured flat at the plateau. **Next:** `tauwint` — the same
physics but assembled from a wall-normal gradient of `Ux` at the wall cell on a
strongly stretched mesh, which has a documented tendency to sub-first-order
behaviour. **Least likely:** `Kint` — global and integral, but dominated by the
near-corner region where `k` is largest and where refinement changes most.

### 4.5 What was considered and REJECTED, and why

* **Anything built on `Uy`, `Uz` or `p`** — secondary-flow strength, in-plane
  kinetic energy, corner vortex position, cross-plane pressure difference:
  **rejected outright** under §4.0. These are the quantities a duct is famous
  for and they are exactly the ones a linear model does not produce.
* **`Ux` at the duct centreline** — a fixed-cell read wearing a physical
  coordinate unless interpolated; G1 disqualified that class and G2 does not
  re-open it.
* **A reattachment length** — the duct has no separation.

---

## 5. Gate, threshold, cap and label

### 5.1 Ordering, from standing rule 5, and it is not negotiable

1. Any level not complete (§6.3) or not iteratively converged (§6.4) → the
   **rung** is `NOT A RESULT`, whatever any number says. **`grade_g2.py` returns
   at this point, before any Roache arithmetic runs at all.**
2. A triple that is `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → that
   functional is `NOT A RESULT`, with the value and `R` printed beside it.
3. Only a `CONVERGING` triple reaches a band. The gate can turn a `PASS` or a
   `GATE FAIL` **into** `NOT A RESULT`, never the reverse.

Classification, with `eps21 = f1 − f2`, `eps32 = f2 − f3` (`1` = fine = L3):

| condition | label |
|---|---|
| both `\|eps\|` below the floor | `EXACT` |
| one `\|eps\|` below the floor | `STAGNANT` |
| `R = eps21/eps32 < 0` | `OSCILLATORY` |
| `R >= 1` | `DIVERGENT` |
| `0 < R < 1` | `CONVERGING` |

`0 < R < 1` requires `eps21` and `eps32` to share a sign, so **the `CONVERGING`
branch is exactly the monotone branch**. `p`, `f_ext` and the GCI are computed
and printed **only inside it** — `roache()` returns with all three still `None`
on every other branch, which is how "never quote a GCI when the three values are
not monotone" is enforced rather than remembered.

### 5.2 Order and GCI, closed form, because `r` is exactly 2

    p        = ln|eps32/eps21| / ln(r),   r = r21 = r32 = 2
    f_ext    = f1 + eps21/(r^p - 1)
    GCI_fine = Fs * |eps21/f1| / (r^p - 1),   **Fs = 1.25**

### 5.3 The registered bands and floors

| functional | `p` band | GCI_fine ceiling | floor (EXACT/STAGNANT) |
|---|---|---|---|
| **PRIMARY `gradP`** | **[1.0, 3.0]** | **5.0 %** | `1e-5 · \|f1\|` |
| SECONDARY-A `Kint` | [0.5, 3.0] | 10.0 % | `1e-5 · \|f1\|` |
| SECONDARY-B `tauwint` | [0.5, 3.0] | 10.0 % | `1e-5 · \|f1\|` |

**Why [1.0, 3.0] on the primary.** The laplacians are `Gauss linear corrected`
on a mesh whose non-orthogonality is measured at **exactly 0** at every level, so
the correction term is inactive and the scheme is formally second order on
uniform spacing. All three convective terms are `bounded Gauss linearUpwind`,
and on this case convection is in any event nearly absent (`Uy, Uz ≈ 0`,
`d/dx ≡ 0`). The **geometric stretching** — per-cell ratio `q` running 0.847 /
0.922 / 0.960 across the family — is what reduces the formal order of a
cell-centred laplacian toward 1 on the graded directions. `p < 1` means the
discretisation is below the floor its own stretched laplacian sets; `p > 3` is
superconvergence or noise, not asymptotic behaviour. The secondaries get
[0.5, 3.0] because a wall-gradient-derived integral and a near-corner-dominated
integral have a documented tendency to sub-first-order behaviour.

#### 5.3.1 REGISTERED CANDIDATE CAUSES for a `p` outside the band — named in advance

If the observed `p` falls outside its band, there are **two registered candidate
causes and the record must carry both**, side by side:

1. **the scheme** — the stretched cell-centred laplacian's degraded order, the
   `cellLimited` gradient limiter on `k` and `omega` (§10 item 5), or L1 lying
   outside the asymptotic range (§10 item 10); and
2. **the non-systematic wall-cell refinement** — the measured local linear ratios
   **1.9492 and 1.9748 against an ideal 2** (§3.4), a 2.5 % and 1.3 % departure
   that the GCI's exact `r = 2` does not carry.

**Neither may be presented as the explanation without the other standing beside
it**, and in particular the scheme is not the default explanation. This is
registered now, before any value exists, and the reason is the anti-gaming clause
read in its second direction: a rung that discovers cause 2 only *after* seeing a
bad `p` has chosen its explanation to fit the answer, which is the same failure
as choosing a scheme to fit a reference. Registering it costs nothing here and is
worth everything if `p` comes out at 0.8.

The registration does **not** soften the verdict. A `CONVERGING` triple with `p`
outside the band is a **`GATE FAIL`**, reported as one, with both candidate
causes named as an attribution and neither offered as an excuse. Deciding which
of the two dominates is **not** work this rung can do on three grids; it needs a
fourth level or a family at a different anchor, and that is a SEPARATE rung,
separately pre-registered.

**Why the floor is `1e-5` relative and not G1's `1e-4`.** The floor's job is to
say when a level-to-level difference is smaller than the iterative noise and
therefore not a discretisation signal. G1 set it at its own plateau tolerance.
Here the plateau was measured (§4.0) at **≤ 1.9e-06** relative on this box on
this archetype, so `1e-4` would discard real signal. `1e-5` sits **5x above the
measured bound** and is set from that measurement, not from a borrowed number.

### 5.4 Verdict mapping, and the rung's headline

`CONVERGING` + `p` in band + GCI within ceiling → **`PASS`**.
`CONVERGING` + either outside → **`GATE FAIL`**.
Not `CONVERGING` → **`NOT A RESULT`**.

**The rung's headline verdict is the PRIMARY's.** The secondaries are reported
with their own verdicts and **never change it**. The vocabulary is
`PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING`, and
`grade_g2.py` passes every verdict through a checker that **refuses** on a
synonym, a hedge or a lower-case variant before it is printed.

### 5.5 The registered falsifier (`CLOSURE_MODELLING_CHARTER.md` §12)

G2 is falsified if the `gradP` triple is `CONVERGING` and either `p` falls
outside [1.0, 3.0] or GCI_fine exceeds 5.0 %. That is a `GATE FAIL` and it is a
publishable finding about this solver setup, not a failure of the rung.

---

## 6. Controls. Each is a standing rule, not a nicety

### 6.1 THE RECONSTRUCTION CONTROL — the control this rung exists to carry

G1's family control could compare **dictionary bytes**, because its substrate
ships a dictionary. G2's substrate ships none, so the equivalent evidence is
stronger and different: **the constructed dictionary, at the shipped resolution,
must regenerate the shipped `polyMesh`.**

`build_g2.py` executes this before staging any level: it writes the dictionary
at `N = 55`, runs `blockMesh`, and compares the regenerated points against
`SRC_CASE/constant/polyMesh/points` **point by point**, refusing above `1e-9 m`.
Measured: **4.800e-14 m** (§2.3). It also refuses if any of the six patches is
absent from the regenerated boundary or carries a type other than the shipped
one. The result is recorded in `STAGING_MANIFEST_G2.json` and `grade_g2.py`
**re-checks it at grade time**, so a post-stage edit cannot slip through.

`build_g2.py` additionally **re-derives** `Lx`, `Ly`, `Lz`, `N`, the per-cell
grading ratio and the total ratio from the shipped points at stage time and
refuses if any disagrees with the frozen registry — and refuses outright if the
shipped spacings are **not** a geometric progression, because in that case
`simpleGrading` could not reproduce them and the dictionary would be a choice
rather than a derivation.

### 6.2 THE REFINEMENT-FAMILY CONTROL — closure's own scar, made executable

The lab was nearly fooled by `alpha_10_9000_{2024,3036,4048}`: three sibling
directories that look like a refinement family and are not — **`nCells 15600`
for all three, three different `vertices` sha256**; the suffix is the domain
height, not a grid level. A length check passes on all three, which is exactly
how this class of defect is missed. The control has two clauses, either of which
alone rejects that set:

1. The three levels' `vertices` blocks are **byte-identical**, and every byte of
   the dictionary outside the single `hex` line is byte-identical, compared by
   **bytes** — never by line count, never by file size.
2. The three `nCells`, read from each `constant/polyMesh/owner` note, are
   **distinct** and in the registered ratio `1 : 4 : 16`.

Additionally every other staged file — the five `0/` fields, `caseDef`,
`fieldDef`, both `constant/` property files, `fvSchemes`, `fvOptions` and
`fvSolution` — must be **byte-identical across the three levels** by sha256; the
three `controlDict`s must be identical outside `endTime` and `writeInterval`,
each must carry **its own** registered `endTime`, and the shipped `libs` line
must be present in all three. **Any failure is a refusal (`sys.exit(2)`), not a
warning.** The control is enforced twice: in `build_g2.py` at stage time and
again in `grade_g2.py` at grade time.

**Two registered departures from the shipped `system/`, both stated here.**
(a) `residualControl` is emptied (§3.6), forced by standing rule 4.
(b) The staged `controlDict` sets `writePrecision 12` against the shipped 6.
Six significant figures quantise the disk `gradient` at `1.9e-06` relative —
**the same order as the level-to-level differences this rung measures**. Raising
the output precision changes what is written, not what is solved: these runs
start from `0` and never restart from a written field. All function objects are
dropped, as in G1, because the shipped ones resolve `#includeEtc` paths that do
not exist under v2606; nothing this rung needs depends on them.

### 6.3 STRICT COMPLETION + AGE GUARD (standing rule 4), all-or-nothing

Per level, every clause. **PHYSICS clauses refuse. INFRASTRUCTURE clauses are
named and recorded (L-342, §6.5).**

| # | class | clause |
|---|---|---|
| P1 | PHYSICS | `rc.txt` holds `0` |
| P2 | PHYSICS | `log.run` exists and holds an `End` line |
| P3 | PHYSICS | `log.run` holds no `FOAM FATAL` / FPE / signal line |
| P4 | PHYSICS | the last numeric time directory **is** `endTime` |
| P5 | PHYSICS | `U p k omega nut` and `uniform/meanVelocity1Properties` present at `endTime` |
| P6 | PHYSICS | **age guard** — every one of those is **strictly newer** than the case's own `0/U` |
| P7 | PHYSICS | `ExecutionTime` line count `== endTime`, a **HARD EQUALITY** |
| I1 | INFRA | `log.checkMesh` exists and says `Mesh OK` |
| I2 | INFRA | `mem_time.txt` holds a `/usr/bin/time -v` MaxRSS reading |
| I3 | INFRA | `wall_s.txt` recorded (the cost calibration's actual) |
| I4 | INFRA | `V`, `wallShearStress`, `yPlus` present at `endTime` |
| I5 | INFRA | the `libs` load warning, if the loader emitted one (§2.4) |

**The age marker is `0/U`, and `run_g2.sh` touches it LAST, immediately before
the solver launch** — exactly as the T-family touches `0/T`, and for the same
reason: it dates the run that was allowed to produce the answer.
`build_g2.py` **refuses to stage into a level directory that already exists**,
so no level can start in a tree that already holds an answer.

**P7 carries NO TOLERANCE.** Standing rule 4 says `== endTime`. A sibling rung
was ruled against today for grading `ExecutionTime` with a 50 % tolerance; this
comparator does not do that and does not pre-authorise its own degradation. If
P7 fires, the pre-registered remedy is **supervisor triage of the cause**, never
a silent reclassification by the comparator.

**One declared departure from `grade_g1.py`'s shape, and it is deliberate.**
G1's `parse_log` refuses on an absent `log.run`. G2's **reports it as a P2
PHYSICS failure** instead, so a level with no solver log produces the registered
`NOT A RESULT` under rule 5 step 1 rather than an instrument error. An absent
solver log **is incompleteness, not an instrument malfunction**, and rule 5
step 1 already has the right answer for incompleteness; refusing there yields
`rc 2` with no verdict at all, which tells a reader less. Exercised: on a
staged-but-unrun tree the comparator prints `RUNG VERDICT: NOT A RESULT` and
returns 2, with no Roache arithmetic performed.

**`grade_g1.py` is FROZEN and stays exactly as it is.** This divergence is a
decision taken at this rung and endorsed by the closure supervisor, recorded here
so that a later reader who compares the two comparators finds a ruling rather
than drift. G1's shape is the one being departed from; nothing about G1
changes.

### 6.4 ITERATIVE CONVERGENCE, per level

| # | clause |
|---|---|
| IC1 | final initial-residual, first solve of the last `Time =` block: `Ux <= 1e-6`; `k <= 5e-6`; `omega <= 5e-6` |
| IC2 | **plateau on the primary functional itself**: over the final 10 % of `gradP` prints, `max\|gradP − gradP_end\| / \|gradP_end\| <= 1e-5` |
| IC3 | the disk `gradP` and the last log `gradP` agree to `1e-6` relative — two independent reads of one quantity |

**`p`, `Uy` and `Uz` carry NO threshold and this is FORCED, not chosen** (§4.0).
Their final values are printed at every level as recorded diagnostics, beside the
sentence that says why they are ungated, so a reader of the record sees the
degenerate normalisation rather than an unexplained omission. This is precisely
M1 §4.1's ruling, applied.

**Thresholds and where they come from.** `k` and `omega` at `5e-6` are M1's
registered, measured values — themselves the ducts' own shipped `k` threshold,
and **520x above the measured duct `k` floor** of 9.577e-09. `Ux` at `1e-6` sits
**10 orders above the measured floor** (7.343e-16) rather than at it, because
the floor is mesh-dependent and only one mesh has been measured. IC3's `1e-6`
allows for the fvOption printing twice per outer iteration while writing once;
at a genuine plateau — which IC2 has already required — the two prints were
measured identical.

**No re-run with a longer `endTime` is permitted under this pre-registration.**
Lengthening a run after seeing that it did not plateau is tuning against the
answer. That is why the iteration budgets carry the margin §3.6 measures.

### 6.5 PLANTED-DISK CONTROLS (standing rule 3) — round-tripping real files

**An in-memory plant does not satisfy rule 3.** Closure was already caught on
exactly that (`score_gpu_ling.py:85-88` plants a perturbation that never
round-trips a file). All three controls here **write a real file and read it back
through the same function used on the real data**, and each **refuses
(`sys.exit(2)`)** if the reader cannot see the plant. **Each plant goes in
through the data path the instrument consumes** — an OpenFOAM ASCII file parsed
by the production reader — never by searching for a format string this
instrument itself wrote.

1. **`gradP`.** The real `meanVelocity1Properties` is copied, its `gradient`
   value rewritten **on disk** to `1.234567e-03`, and read back through
   `read_gradP_disk`. Refuses if the reader does not return the plant; refuses if
   the substitution changed no bytes; and then the **inverse** — the same reader
   on the unplanted file must **not** return the plant, or it is a constant, not
   a reader. Both branches were exercised and both fire.
2. **`Kint`.** (a) `k` is rewritten on disk to a uniform `2.0` and the integrator
   must return `2.0 · sum(V)` to `1e-9` relative — a **closed-form** answer.
   (b) a **single cell at a known index** is rewritten to `9.876543e+02` and the
   integral must move by exactly `delta · V[index]`, proving the reader reads
   per-cell values at the right index and not a bulk average.
3. **`tauwint`.** (a) a uniform wall-shear field is written on disk in OpenFOAM
   ASCII and the integral must equal `tau · A_patch` against the area computed
   **independently from the polyMesh** — verified on the real shipped mesh at
   `1.000000000e-06 m²` per patch. (b) a **single face at a known index** is
   rewritten and the integral must move by exactly `delta · A[index]`. (c) a
   shear field one face SHORT of the patch must **refuse**, not be padded.
4. **The blind control.** A reader that returns `0.0` for every face is run
   against the same planted closed form, and the control **fires** — so the
   zero the real reader would give on a real absence is a reading and not a
   blind spot.

### 6.6 L-342 — physics against infrastructure

Sanaa's universal rule: bookkeeping never voids physics. Here the split is
concrete: a lost `V` field makes SECONDARY-A `NOT A RESULT` while the PRIMARY
still returns its verdict, because `gradP` needs no post-processing artefact; a
lost `wallShearStress` does the same to SECONDARY-B; a lost `mem_time.txt`,
`wall_s.txt` or `log.checkMesh`, or a `libs` load warning, is printed as
`INFRASTRUCTURE DEFECT`, carried into the record, and voids nothing.

### 6.7 L-332 — no refusal may be an `assert`

`python3 -O` deletes every `assert` from the compiled code. **Every refusal in
both instruments is a `raise` or a `sys.exit(2)`**, and each instrument parses
**its own AST** and refuses if a single `ast.Assert` node exists — with the
counter first shown able to count a **planted** assert, so its zero is a reading
and not a blind spot.

**Both selftests were run under `python3` and under `python3 -O`, with
`__pycache__` cleared before each run, and every registered refusal fired
identically under both. `rc = 0` in all four runs.**

---

## 7. Cost. Measured basis, and the box cannot read its own billing

**Rate: `4.5e-06` s per cell-iteration, serial.** Deliberately conservative. The
two long duct runs on this box, both v2606, both `nProcs 1`, both 30,000
iterations with `residualControl` removed:

| log | cells | `ExecutionTime` | s / cell-iteration |
|---|---|---|---|
| `aposteriori/kaandorp/AR_1_Ret_360__NULL/log.run` | 3,025 | 324.41 s | **3.5748e-06** |
| `aposteriori/kaandorp/AR_3_Ret_360__NULL/log.run` | 8,748 | 1052.38 s | **4.0100e-06** |

Both are `kOmegaSSTCorrected` runs, which solve extra fields, so both are
**upper bounds** on stock `kOmegaSST` on the same meshes. G1's registered
`4.5e-06` sits above both and above the largest calibration point on record
(4.138e-06 at 21,000 cells); it is reused unchanged. *A stock-`kOmegaSST` duct
row exists (`AR_1_Ret_360__G0_stock`, 2.63 s / 200 iterations) and is
**deliberately NOT used as a basis**: at 200 iterations the startup cost is not
amortised.*

**Runs are SERIAL, 1 rank.** No `mpirun`, no `decomposePar`, no `processor*`.
With `ranks = 1`, core-minutes equal wall-minutes.

| level | cells | `endTime` | cell-iterations | wall s @ 4.5e-06 | core-min |
|---|---|---|---|---|---|
| L1 | 1,024 | 20,000 | 2.0480e07 | 92.2 | **1.54** |
| L2 | 4,096 | 30,000 | 1.2288e08 | 553.0 | **9.22** |
| L3 | 16,384 | 40,000 | 6.5536e08 | 2,949.1 | **49.15** |
| solver subtotal | | | 7.9872e08 | 3,594.2 | **59.90** |
| `blockMesh` + `checkMesh` ×3 | | | | **1.62 (MEASURED)** | 0.03 |
| `-postProcess`, 3 funcs ×3 | | | | 45 (estimated) | 0.75 |

**REGISTERED ESTIMATE: 61.0 core-minutes.**
Derived: 1.017 core-h × $0.0513/core-h = **$0.052 — derived at the owner-stated
rate, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5: this box cannot read its
own billing).

**REGISTERED CAP: 120.0 core-minutes** = 7,200 s, allocated as per-level
`timeout` values 300 / 1,500 / 5,400 s summing to **exactly** the cap.
Derived: 2.0 core-h × $0.0513 = **$0.103 — derived, NOT MEASURED.**

**The cap is the runaway guard, not a target.** Its 1.98x ratio to the estimate
is justified rather than rounded, and G2 is in a better position than G1 here:
**L3 at 16,384 cells sits INSIDE the measured calibration range** (the largest
point on record is 21,000 cells), where G1's L3 at 61,440 was 2.9x beyond it. The
per-level margins over the estimate are 3.26x / 2.71x / 1.83x. **An overrun stops
the run; it does not get a new budget** (standing rule 12), and `run_g2.sh`
enforces this twice — a per-level `timeout`, and a cumulative watch that refuses
to start a level whose budget would breach the cap.

Both figures are far under $25 and so sit inside the 2026-08-21 blanket, and
inside `CLOSURE_MODELLING_CHARTER.md` §18's 487 pre-authorised core-hours. **A
blanket is not a per-item read** (standing rule 9); the cost is registered here
regardless.

**Estimate-versus-actual calibration is owed at completion** (standing rule 12).
`run_g2.sh` records `wall_s.txt` per level for exactly this, and `grade_g2.py`
prints the three actuals beside the obligation. The comparison — ratio
actual/predicted, gap attributed to contention, waste or misprediction, waste
named separately and never absorbed into the ratio — lands as a row in
`docs/COST_CALIBRATION.md`. **A completion report without it is incomplete.**

---

## 8. `memory_floor_gb` — an allowance, and it says so

**Derived term.** At L3, 16,384 cells: fields, the `fvMatrix` diagonal / upper /
lower / source for `U p k omega`, and Krylov workspace come to roughly 60 doubles
per cell = 7.9 MB, plus about 7 MB of mesh addressing — **circa 15 MB of solution
data, derived, not measured.**

**Measured anchors, taken by this lane at each level with `/usr/bin/time -v`:**
`checkMesh` MaxRSS **39,096 kB / 44,780 kB / 69,004 kB** at L1 / L2 / L3
(67.4 MiB at the finest). These bound the OpenFOAM runtime plus mesh footprint
and are readings, not estimates.

**`simpleFoam`'s own footprint is NOT measured and this lane could not measure
it**, being forbidden to launch a solver. Adding the derived solution term to the
measured runtime anchor gives an estimate near 90–150 MB.

**Registered: `memory_floor_gb = 0.5`, an ALLOWANCE**, roughly 3.5x that
estimate and 7x the largest measurement — **explicitly not a measurement.**
`run_g2.sh` wraps every solver invocation in `/usr/bin/time -v -o mem_time.txt`
and the comparator records the recovered MaxRSS per level, **converting this
allowance into a reading for the next pre-registration.** Its absence is an
INFRASTRUCTURE defect (I2), not a physics refusal.

---

## 9. Queue entry

`QUEUE_ENTRY_DRAFT.json` sits **beside this document, in the case directory**,
and is **not** in the drop path. That is deliberate and it is a safety property:
`crontab` runs `scripts/queue_runner.sh` every minute, so a valid entry in
`verification/queue/closure/` is launched by a cron-restarted daemon within about
60 seconds — **the drop path is a launch button, not a passive list** (D535,
L-348), and a copy FIRES.

**Two independent things stop this draft from launching anything:**

1. It is not in a drop path.
2. `prereg_commit` is the literal string `PENDING_SUPERVISOR_FREEZE`, which fails
   the validator's full-sha schema check and can never validate until the
   supervisor replaces it with the real freeze sha.

**It carries no banner.** L-354, landed today: a freeze updates a sha and never
the prose that says "NOT FROZEN", so a draft banner outlives the draft and
becomes a false provenance line at the head of the record — and in a `.json` a
banner makes the file unparseable, which is a defect dressed as a safety
feature. The file says what it **is**; `prereg_commit: PENDING_SUPERVISOR_FREEZE`
renders the lifecycle state by itself. For the same reason **no `.json` here and
no line 1 of `run_g2.sh` carries a banner**; the driver has a real shebang.

**`cwd` is the RUN ROOT `/home/ubuntu/closure-data/g2/`, pre-created empty by the
supervisor at enqueue**, not the repository case directory — with the case
directory as `cwd` every launch would drop `launcher.queue.out` and
`STATUS.<case_id>` inside the tracked repository, which `FILING_CHARTER.md`
forbids. Pre-creating the root is safe and it is verified in the builder rather
than assumed: `guard_dest` is called on `dest_root/<LEVEL>` and on
`dest_root/_recon_shipped_N`, **not on `dest_root` itself**, so an empty `g2/`
does not trip the age guard while a re-stage over an existing level still refuses
exactly as registered.

**A green verdict from the validator is not an approval.** The supervisor's
personal check 4 happens at enqueue and is not delegable to a machine or to this
lane.

---

## 10. What it cannot see

`CLOSURE_MODELLING_CHARTER.md` §16 makes this section mandatory.

1. **It cannot see whether k-omega SST is right — and on this case it is known
   not to be.** The duct's headline physics is the secondary flow, and a linear
   eddy-viscosity model produces none (§4.0). G2 grades the numerical
   convergence of a model that is wrong about this flow in a specific, named,
   measured way. **A consistent scheme converging is not a correct scheme.**
2. **It cannot see agreement with DNS or LES.** No reference field is read; the
   shipped `*_LES` fields exist only on the 3,025-cell mesh and are not staged.
3. **It cannot see anything about `Uy`, `Uz` or `p`.** They are not gated, not
   graded, and not claimed. Any statement about in-plane convergence on this
   rung would be a statement about machine noise.
4. **It cannot see the 2.5 % / 1.3 % departure from exactly systematic
   refinement as an error bar.** §3.4 measured the wall-cell linear ratio at
   1.9492 and 1.9748 against an ideal 2, and the GCI uses `r = 2` exactly. The
   resulting bias on `p` is not quantified here and no attempt is made to correct
   for it. **This departure is 15x G1's.** It is registered in section 5.3.1 as
   one of two candidate causes for a `p` outside the band, named before any value
   exists precisely so that it cannot be reached for afterwards.
5. **It cannot see whether the `cellLimited` gradient limiter on `k` and
   `omega` behaves across the family.** A limiter activates on different cells at
   different resolutions; that is a live and registered risk to a monotone
   triple. The shipped `fvSchemes` is nevertheless kept byte-identical, because
   provenance to the shipped case is the rung's evidentiary content. If the
   triple comes out non-monotone, the pre-registered next step is a **SEPARATE
   rung, separately pre-registered**, repeating the triple with the limiter
   removed — never an edit to this one.
6. **It cannot see whether `simpleFoam` runs this case under v2606.** This lane
   proved that `blockMesh` and `checkMesh` do, and that the loader warns rather
   than fails on the missing `libs` entry **under `checkMesh`**. The solver was
   never launched, by design. L1 is the fail-fast at 92 s.
7. **It cannot see whether the measured `gradP` plateau holds at other
   resolutions.** §4.0's flat plateau is one run, at `N = 55`, with
   `kOmegaSSTCorrected`. IC2 re-measures it at every level and refuses if it does
   not hold, so this is a gap the instrument closes rather than assumes — but it
   is a gap at freeze time.
8. **It cannot see a defect in the shipped source case.** All three levels
   inherit whatever the shipped `fvSchemes`, `fvSolution`, `transportProperties`
   and boundary conditions contain. If the shipped setup is wrong, all three are
   wrong the same way and the triple will converge beautifully to the wrong
   answer.
9. **It cannot see unsteadiness.** `ddtSchemes default steadyState`.
10. **It cannot see error at the coarse end if L1 is outside the asymptotic
    range.** 32×32 over a quarter duct may simply be too coarse, in which case
    the triple comes out non-monotone and the rung is `NOT A RESULT`. That is a
    real and registered possibility, not a defect of the instrument.
11. **It cannot see the other 36 geometries.** G2 gives `G = HOLDS` for a second
    geometry and leaves the rest exactly where they were. The corrected corpus
    statement (§1.1) — *zero geometries at more than one cell count at fixed
    physics* — describes the shipped disk, and G1 and G2 change it only for the
    two geometries they build.

---

## 11. The grading path is fixed at the freeze

The comparator is `grade_g2.py` **as it exists at the pre-registration commit**,
and the stager is `build_g2.py` at the same commit. Before grading, the frozen
files must be hashed against the committed blobs to verify that the frozen file
**is** the file that ran (standing rule 2;
`scripts/check_comparator_freeze.py`).

**After first compute, gates are closed.** Changes land only as dated addenda
that cannot alter a gate, a threshold, a cap or a label; originals are struck,
never rewritten. **Before first compute, amendments are legal and must state the
condition and how it was checked** — for this rung, that the run root
`/home/ubuntu/closure-data/g2/` does not exist and holds 0 core-minutes.

---

## 12. Files

| file | role |
|---|---|
| `PREREGISTRATION.md` | this document |
| `build_g2.py` | derives the geometry, runs the reconstruction control, stages the three case trees; refuses over an existing tree; enforces the family control at stage time |
| `run_g2.sh` | the driver the queue entry names; stages, meshes all three, then solves ascending, rc captured in its own foreground |
| `grade_g2.py` | the comparator: reconstruction re-check, family control, strict completion, planted-disk controls, plateau, Roache, GCI, vocabulary refusal |
| `QUEUE_ENTRY_DRAFT.json` | the queue entry, unvalidatable until the supervisor freezes |

---

## 13. ANTI-GAMING REGISTER (`docs/standards/NONCONVERGENCE_STANDARD.md`)

**The standard is cited by its FILE DIGEST, sha256
`14d72954cbe853ae859c083417963758985181391484fd5da08b3ded86e08885`, disk equal
to HEAD.** The dispatching brief cited it as "sha 7ffd6c73"; that is the
**commit** that landed the standard, not the file's digest. **The commit/digest
confusion was caught here, at this rung**, and the correction was verified
independently by the closure supervisor. It is exactly the failure
`VERIFICATION_CHARTER.md` v1.12 names — *a freeze sha is never derived from a
commit subject* — and it had already propagated into a sibling rung's freeze
commit message, where it cannot be rewritten. Recorded so the next reader of this
line does not repeat it.

The clause is absolute: *"Answer-changing choices (model, scheme class,
formulation) are never selected by agreement with the reference."* A refinement
family involves many choices, and **none below was picked by trying candidates
and seeing which converged nicely.** No G2 run exists; nothing has been solved on
any of these three meshes by anyone.

| choice | registered reason, which names no answer |
|---|---|
| **geometry = `DUCT/AR_1_Ret_360`** | it is not G1's geometry; it is the only non-hill archetype whose mesh proved reconstructible from its own geometry (§2.2); and it is the one geometry on this box with a 30,000-iteration v2606 run available as a cost and plateau basis (§7, §3.6). |
| **refinement ratio `r = 2` exactly** | a non-constant `r` replaces the closed form for `p` with a fixed-point iteration that can itself fail to converge, on a rung whose product is a defensible `p` (§3.2). |
| **anchor `N = 32`** | the largest power of two below the shipped 55, so the shipped resolution lies inside the family's span (§3.2). No other anchor was meshed or compared. |
| **grading held at fixed TOTAL ratio `R`** | it is the only operation that makes three meshes three discretisations of one continuous mapping (§3.4). |
| **`R` from the closed form `1.1^-54`** | the per-cell ratio is `1/1.1` to 2.4e-10 while the endpoint ratio accumulates 54 rounds of the shipped file's ASCII write precision (§3.4). A precision argument, not an outcome argument. |
| **`D = 2`** | `D = 3` with `N_x` held at 1 would understate the refinement by 26 % and inflate `p` by 1.50x (§3.3). Arithmetic, fixed before any value exists. |
| **PRIMARY = `gradP`, not an in-plane quantity** | a linear eddy-viscosity model produces no secondary flow, so an in-plane functional would be a triple over noise (§4.0). This is a **mechanism** measured in the shipped benchmark's own design (its `residualControl` names `k` and `omega`, not `p`) and in this box's own logs — not a comparison of candidate triples. |
| **`gradP` read from disk rather than trusted from the log alone** | the fvOption prints twice per outer iteration and writes once; two independent reads of one quantity is a control (IC3). |
| **band `[1.0, 3.0]` on the primary** | bounded below by the stretched cell-centred laplacian's degraded order and above by the point past which a three-point estimate is noise, not asymptotics (§5.3). Set from the scheme, not from a value. |
| **floor `1e-5` relative** | 5x above the *measured* plateau bound of 1.9e-06 on this archetype on this box (§4.0, §5.3). Set from a measurement of the noise, not from a measurement of the signal. |
| **IC1 thresholds on `Ux`, `k`, `omega` only** | forced by the degenerate residual normalisation (§4.0, §6.4); `k`/`omega` at `5e-6` are M1's already-registered measured values. |
| **`endTime` 20,000 / 30,000 / 40,000** | SIMPLE's iteration count scales with linear mesh dimension; the budgets are 3.4x the scaled measured `k` floor (§3.6). |

Two disclosures that belong in this register rather than in a footnote:

* **This lane read the shipped and the on-box duct logs before registering the
  primary.** That reading established a *contamination mechanism* and a *noise
  floor* — properties of the instrument, not of any answer. It did not compare
  candidate triples, because no triple exists. The full basis is written into
  §4.0 so a reader can judge that for themselves rather than take this
  paragraph's word for it.
* **`gradP` is registered as primary even though `tauwint` measures the same
  physics by an independent path.** Neither was chosen by outcome; `gradP` is
  primary because it needs no post-processing artefact and so survives the L-342
  split, and `tauwint` is registered anyway, with its own band and its own
  verdict, rather than being held in reserve.
