# G1 — GRID-CONVERGENCE TRIPLE ON `Parm_PH_29/alpha_10_9000_3036`

**Rung:** `G1_grid_triple`
**Team:** closure
**Status:** **FROZEN.** Frozen by the closure supervisor on 2026-08-27 in a
commit of its own, with the sha256 of this document and of all three instruments
recorded in that commit message. `SUPERVISION_CHARTER.md` §3 check 4 (the
pre-registration is committed before compute) was performed personally and was
not delegated. Standing rule 2 now applies in full: **the gates, thresholds, cap
and label below are closed.** After first compute nothing here may be edited;
departures land only as dated addenda at the foot that cannot alter a gate, a
threshold, a cap or a label.
**Drafted:** 2026-08-27, by a closure drafting lane on the closure supervisor's
dispatch.

**Naming.** This is **G1**, not R7. `docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md`
defines R1-R6 and R6 is unstarted, awaiting Sanaa's own phrasing; inventing an
R7 would claim a ladder rung she has not authorised. `G1` names the **G column**
of `cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md` -- grid convergence --
and claims nothing about the R ladder.

---

## 1. The question, and the three things this rung does not claim

**Question.** Does the shipped k-omega SST solution of the ERCOFTAC periodic
hill, held completely fixed, converge under systematic grid refinement; and what
observed order and fine-grid GCI does it deliver?

**Why this rung exists.** Closure ruled `G = NO` on every row of its
capability-matrix contribution, and verification's independent audit agreed:
`GCI`, `Roache` and `CONVERGING` appear in **zero** files under
`cases/RANS_LES_closure_models/`. The measured reason is that the disk holds
**266 `polyMesh` directories across 40 geometries and not one geometry at more
than one cell count** -- it cannot supply a *pair*, let alone a triple. Closure
has never offered one row at `HOLDS`. This rung closes that gap, and it is the
cheapest high-value CPU work the family has: **320 core-minutes registered,
$0.274 derived.**

**This rung grades NUMERICAL CONVERGENCE ONLY.** It offers **nothing whatever**
about agreement with LES or DNS truth. No reference field is read; none exists
on the L1 or L3 meshes; none is needed. A Roache triple compares one fixed
model's numerical solution **against itself at three resolutions**.

**It is not a closure result.** `CLOSURE_MODELLING_CHARTER.md` §2 (a-priori
scores are NOT A RESULT without a-posteriori propagation) is **not engaged**:
G1 scores no model, predicts no `b_ij`, and applies no correction. It is a
verification of the *baseline solver on the baseline geometry*. §3's train-mean
baseline clause is likewise not engaged -- there is no model to baseline.

**It is not a validation of the geometry, the model or the Reynolds number.**
A CONVERGING triple with a small GCI says the discrete equations are being
solved consistently. It says nothing about whether k-omega SST is right.

### 1.1 A correction to the dispatch, on record

The dispatching brief listed "pressure drop across the periodic pair" as a
functional candidate. **It is not measurable on this case.** The inlet and
outlet patches are `cyclic` (`system/blockMeshDict:1876-1901`), so `p` is the
*periodic component* and the pressure difference across the pair is identically
zero by construction. The physically equivalent quantity is carried instead by
the `meanVelocityForce` fvOption as the mean streamwise momentum source, and
that is what this pre-registration adopts as the PRIMARY functional (§4.1).

The brief's fourth candidate, "`U_x` at a fixed physical probe", is **rejected**
and not registered. OpenFOAM's `probes` function object reports the value of
the **cell containing** the point unless `interpolationScheme cellPoint` is set
-- a fixed-cell-index read wearing a physical coordinate, which the brief itself
disqualifies. A point value inside a recirculation is also the least likely of
the candidates to give a monotone triple.

---

## 2. Substrate, and every number in this section was measured on this box

**Source case (read-only, never modified):**

    /home/ubuntu/closure-challenge-benchmark/data/Parm_PH_29/alpha_10/alpha_10_9000_3036

This is the only closure geometry on disk that ships a **parameterisable mesh
dictionary**. An inventory lane established that `CBFS`, `PH_Breuer` and every
`DUCT` case ship as frozen `polyMesh` only (`find` for `blockMeshDict*`, `*.m4`
and `mesh*.py` returns empty in each). `Parm_PH_29` is therefore the substrate,
and it is a good one: it is the standard ERCOFTAC periodic hill, `Lx = 9h`,
`Ly = 3.036h`, hill base `1.929h`, `Re_H = 5600`.

| item | value | how established |
|---|---|---|
| `system/blockMeshDict` sha256 | `d177974d830bd45b21f64377a1d382c664b044e0f0f6553058d7fb9750537fca` | `sha256sum` |
| bytes outside the two `hex` lines, sha256 | `33e8d48f1e8d2436bf75f886fe1243b200bb85b7ca06e97e07ac3990c248567e` | `sha256sum` |
| `vertices` block, sha256 | `8d051162cdd020a7c32cc48cb7a1e16a404bf3abb3c257078e8271225dff708d` | `sha256sum` |
| shipped resolution literal | `(120 65 1)`, on `blockMeshDict:38` and `:39`, twice, both on `hex` lines | counted |
| shipped mesh, rebuilt from that dictionary | **`nCells 15600`**, matching the shipped `constant/polyMesh/owner` note byte for byte | `blockMesh` rc 0 in a throwaway scratch directory |
| hill profile | `y = 1` at `x = 0`, flat floor `x` in `[1.93, 7.07]`, `y = 1` again at `x = 8.99` | 900-point spline read from `blockMeshDict:53-954` |
| turbulence model | `kOmegaSST`, `constant/turbulenceProperties:22` | read |
| driving force | `meanVelocityForce`, `Ubar (0.72 0 0)`, `selectionMode all`, `system/fvOptions:18-25` | read |
| viscosity | `nu = 1.786e-4` | `constant/transportProperties` |
| wall treatment | `nutLowReWallFunction` + `omegaWallFunction`, i.e. wall-resolved | `0/nut`, `0/omega` |
| all five staged initial fields | `internalField uniform`, and every one of the ten patches present in every `boundaryField` | parsed |
| OpenFOAM | **v2606 (ESI)**, `/usr/lib/openfoam/openfoam2606` | `blockMesh` run |

**Measured incompatibilities with the shipped `.org` case, and what is done
about each.** The shipped case was authored under OpenFOAM 7 (.org). Under
v2606, `blockMesh` emitted, at every level:

* `Cannot find functionObject file residuals` and `... singleGraph_x0` -- the
  `.org` `#includeFunc` etc-paths do **not** resolve. **All function objects are
  therefore dropped from `controlDict`.** Residual and momentum-source histories
  are parsed from `log.run`, which the solver prints unconditionally, and the
  post-processing fields are produced by explicit `-postProcess -func` calls
  after the solve. Nothing needed by this rung depends on an etc-path.
* `Unknown compression specifier 'uncompressed'` -- rewritten as
  `writeCompression off`.
* `Found [v1012] 'convertToMeters' entry instead of 'scale'` -- an accepted
  deprecation IOWarning, value `1`, **deliberately left alone**: editing it would
  break the byte-identity of the dictionary against the shipped source, which is
  the entire content of the refinement-family control (§6.1).

**What this substrate section cannot establish.** `blockMesh` proves the mesh
dictionary parses under v2606. It does **not** prove `simpleFoam` will run this
case under v2606 -- this lane is forbidden to launch a solver and did not. The
residual risks are the legacy `nu nu [0 2 -1 ...] value` form in
`transportProperties` and the flat `relaxationFactors` form (the latter is
carried by an explicit backwards-compatibility branch at
`src/OpenFOAM/matrices/solution/solution.C:66-98`, read, not run; this
pre-registration rewrites it into the modern `fields{}/equations{}` form anyway,
with identical numbers). **The fail-fast for both is L1 itself**: `run_g1.sh`
meshes all three levels first, then solves in ascending cost order and stops the
chain on any non-zero rc, so a v2606 incompatibility costs **5.76 core-minutes**
to discover, not 277.

---

## 3. The three levels, and the arithmetic

### 3.1 The registered triple

Every level is the shipped dictionary with **one literal changed**.

| level | role | resolution literal | cells | `endTime` | `timeout` (s) |
|---|---|---|---|---|---|
| **L1** | coarse | `(60 32 1)` | **3,840** | 20,000 | 900 |
| **L2** | medium | `(120 64 1)` | **15,360** | 30,000 | 5,400 |
| **L3** | fine | `(240 128 1)` | **61,440** | 60,000 | 29,700 |

Two `hex` blocks per dictionary, so cells = `2 * nx * ny`. **These cell counts
were measured, not computed**: `blockMesh` rc 0 at all three, `nCells` read back
from each `constant/polyMesh/owner` note as 3,840 / 15,360 / 61,440. The
`y`-resolution counts 32/64/128 are **per block**; the two stacked blocks give
64/128/256 cells across the channel height, so L2 is a `120 x 128` mesh -- the
standard periodic-hill RANS resolution.

`15360 = 4 * 3840` and `61440 = 4 * 15360`, **exactly**.

### 3.2 Where the dispatch's arithmetic is wrong, and by how much

The brief proposed `(60 33 1)` / `(120 65 1)` / `(240 130 1)` = 3,960 / 15,600 /
62,400, keeping the shipped mesh as the medium level. **65 is odd**, so the
coarse level is not an exact halving:

* `r21 = (62400/15600)^(1/2) = 2.00000`
* `r32 = (15600/3960)^(1/2) = 1.98479`  -- **not 2**

A non-constant `r` is legal (ASME V&V20 / Celik's procedure solves a
transcendental equation for `p` by fixed-point iteration) but it replaces a
closed form with an iteration that can itself fail to converge, on a rung whose
entire product is a defensible `p`. The deviation is only 0.76 %, so the cost of
the brief's triple is small -- but it is a cost paid for nothing.

**The registered triple takes the exact-`r` option instead**, and pays for it by
giving up the shipped `polyMesh`. That loss is smaller than it looks: the
provenance to the shipped case is carried by the **dictionary**, and all three
registered dictionaries are byte-identical to it outside the two `hex` lines.
The shipped-mesh reproduction is retained as a **separate, non-gating,
already-completed measurement**: rebuilding `(120 65 1)` from the same
dictionary gives `nCells 15600`, matching the shipped owner note exactly.

### 3.3 `D` is 2, and using 3 would be a 26 % error in the refinement ratio

The mesh is **one cell thick in `z`, between `empty` patches**
(`blockMeshDict:1904-1930`). An `empty` direction carries no flux, no gradient
and no discretisation; refinement is applied in `x` and `y` only, and the cell
count scales as `nx * ny`. **`D = 2`**, and the representative cell size is

    h = (A/N)^(1/2),   A = V / 0.2 = 25.4131 m^2   (V = 5.0826 m^3, checkMesh)

| level | `h` | |
|---|---|---|
| L3 (fine) | `h1 = 0.020338` | |
| L2 | `h2 = 0.040676` | `r21 = h2/h1 = ` **2.0000** |
| L1 (coarse) | `h3 = 0.081352` | `r32 = h3/h2 = ` **2.0000** |

Using `D = 3` with `N_z` held at 1 would give `r = 4^(1/3) = 1.5874` -- a **26 %
understatement of the refinement**, which inflates the apparent order by
`ln 2 / ln 1.5874 = 1.50x` and understates the GCI by the same construction.
`D = 3` is registered as **wrong for this mesh** and the comparator hard-codes
`D_SPATIAL = 2`.

### 3.4 `simpleGrading` is nonuniform, and it must be held fixed

The two blocks carry `simpleGrading (1 10 1)` and `(1 .1 1)`: expansion away
from the lower wall by a factor 10 across the block, contraction toward the
upper wall by the same factor. **The dispatch's belief that the grading must be
held fixed across levels is correct, and here is why.**

For `blockMesh`'s `simpleGrading` with total ratio `R` over `N` cells, the face
positions satisfy `x_j / L = (r^j - 1)/(r^N - 1)` with `r = R^(1/(N-1))`. As `N`
grows at fixed `R`, this tends to the `N`-independent stretching function
`x(s)/L = (R^s - 1)/(R - 1)`, `s = j/N`. **Holding `R` fixed and changing `N` is
therefore exactly the operation that makes the three meshes three
discretisations of one continuous mapping** -- which is what "systematic
refinement" means. Local spacing is `h(s) ∝ 1/N` in the limit, so `h` halves
everywhere, not only in the uniform direction. Changing the grading would give
three *different* meshes, not a refinement family, and every Roache formula
below would be void.

**The finite-`N` deviation, measured, not assumed.** The mapping is only
exactly self-similar as `N -> infinity`. The most demanding place is the
smallest cell. From `checkMesh`:

| level | min cell volume (m^3) | ratio to next coarser |
|---|---|---|
| L1 | 2.32597e-04 | |
| L2 | 5.79570e-05 | 4.0133 (ideal 4.0000, **+0.33 %**) |
| L3 | 1.45017e-05 | 3.9966 (ideal 4.0000, **-0.08 %**) |

So at the smallest cell the family is systematic to better than 0.33 %, against
a `r = 2` used exactly in the GCI. **This is registered as a known,
quantified idealisation** and repeated in §10.

### 3.5 Mesh quality does not change regime across the family

A quality regime change across levels would corrupt a triple silently. Measured
by `checkMesh`, `Mesh OK` at all three:

| level | max non-orthogonality | avg non-orth | max skewness | max aspect ratio | total volume |
|---|---|---|---|---|---|
| L1 | 38.789 | 9.723 | 0.4089 | 18.35 | 5.0826041 |
| L2 | 39.079 | 9.770 | 0.2267 | 20.16 | 5.0826243 |
| L3 | 39.193 | 9.780 | 0.1188 | 20.10 | 5.0826231 |

Non-orthogonality is constant to 1 %; skewness **falls** by 1.80x then 1.91x,
approaching the `h`-proportional 2.00 a smooth mapping requires; the domain
volume is converged to 4e-6 relative already at L1, so the spline geometry is
not a source of error at the level of any registered functional.

**Wall resolution does not change regime either.** With grading held at 10, the
first-cell height scales as 1.987 then 1.994, so `y+` falls monotonically across
the family and never crosses out of the wall-resolved regime that
`nutLowReWallFunction` requires. `yPlus` is written at every level as a recorded
**diagnostic** -- not a gate -- precisely so a regime change would be visible in
the record rather than inferred.

### 3.6 Iteration counts are NOT part of the refinement family

`endTime` is 20,000 / 30,000 / 60,000 and this is deliberate. SIMPLE's outer
iteration count to a given convergence scales roughly with the linear mesh
dimension; L3 is 2x L2 in each direction. The three levels are compared as
**converged solutions**, not as equal-iteration solutions, and §6.4's plateau
gate is what makes them comparable. There is no `residualControl` in
`fvSolution` -- the stager **refuses** if one survives -- so every run goes to
its `endTime` and `last time == endTime` is satisfiable.

---

## 4. Functionals. One primary, two secondaries, none needing reference data

Each is computable from the solver's own output. **None is read at a fixed cell
index.**

### 4.1 PRIMARY -- `gradP`, the mean streamwise momentum source [m/s^2]

The scalar the `meanVelocityForce` fvOption must supply to hold the
volume-averaged `U_x` at `Ubar = 0.72`. The solver writes it to disk itself, at
every write time, as `gradient` in

    <endTime>/uniform/momentumSourceProperties

**Confirmed present in v2606 by reading the source, not by assuming**:
`src/fvOptions/sources/derived/meanVelocityForce/meanVelocityForce.C:49-71`
writes `<name>Properties` into `time().timePath()/"uniform"` with a `gradient`
entry, and `:183-184` prints the same value to the log **every iteration**.

**Why this is the primary.**

1. It is a **global integral**: by the streamwise momentum balance,
   `gradP * V` equals the total wall shear plus the pressure drag on the hill.
   Integral functionals converge monotonically far more often than local ones,
   because errors of opposite sign cancel in the integral. This is the triple
   most likely to come out `CONVERGING`.
2. It needs **no post-processing at all** -- no `-postProcess` call, no
   interpolation, no probe, no wall-shear field. It is the one functional that
   survives a total post-processing failure, which is exactly the L-342 split
   (§6.5).
3. The solver writes it **twice by two paths** -- to disk and to the log -- so
   the comparator can cross-check two independent reads of one quantity and
   refuse if they disagree by more than 1e-9 relative.

### 4.2 SECONDARY-A -- `Kint`, volume-integrated turbulent kinetic energy [m^5/s^2]

    Kint = sum_i k_i V_i

from `<endTime>/k` and `<endTime>/V` (`-postProcess -func writeCellVolumes`).
Global integral, no probe, no interpolation. The comparator **refuses** if
`sum(V)` does not match the measured domain volume 5.0826 m^3 to 1e-4 relative
-- a closed-form check that the volume field belongs to this mesh.

Honest risk: `k` in a periodic-hill k-omega SST solution is dominated by the
separated shear layer, and refinement sharpens that layer while moving the
separation point. `Kint` may well come out non-monotone. It is registered
anyway.

### 4.3 SECONDARY-B -- `xr`, lower-wall reattachment length [h]

The **physical `x`** at which the lower-wall shear changes sign from
recirculating to attached, by linear interpolation between the two face centres
straddling the crossing:

* `tau_wx` from the `bottomWall` `boundaryField` of `<endTime>/wallShearStress`;
* face centres from the `bottomWall` `boundaryField` of `<endTime>/C`.
* **The "attached" sign is taken from the flow itself**, as the sign of `tau_wx`
  at the face nearest `x = 6.5` -- deep in the attached flat floor
  (`x` in `[1.93, 7.07]`), well downstream of reattachment and upstream of the
  windward foot. This makes the functional independent of OpenFOAM's wall-shear
  sign convention. The comparator refuses if `|tau_wx|` there is below 1e-8.
* **`xr` is the first** such crossing at `x >= 0.5`. The number of qualifying
  crossings is counted and printed at every level; **if the counts differ across
  the three levels the three values are not the same quantity and SECONDARY-B is
  `NOT A RESULT`.** If there is no crossing at all the comparator refuses rather
  than manufacture one.

This is the canonical periodic-hill functional and the one everyone reports.
**It is also the one most likely to fail.** It is a location derived from where a
near-zero quantity crosses zero: highly sensitive, and quantised by the face
spacing (`0.15h` at L1 against `0.0375h` at L3). **`OSCILLATORY` is a realistic
outcome and would be reported as `NOT A RESULT` without apology.** Registering a
functional that may fail to converge is honest; swapping it after seeing the
numbers is what standing rule 2 exists to prevent.

### 4.4 Registered expectation, on record before the run

**Most likely monotone:** `gradP` -- global, integral, first-order-smooth in the
solution. **Next:** `Kint` -- global and integral, but dominated by a shear layer
whose position moves. **Least likely:** `xr` -- local, derived from a zero
crossing, and the standard case in the literature where grid triples on
separated flows go non-monotone.

---

## 5. Gate, threshold, cap and label. Frozen before any run

### 5.1 Ordering, from standing rule 5, and it is not negotiable

1. Any level not complete (§6.3) or not iteratively converged (§6.4) -> the
   **rung** is `NOT A RESULT`, whatever any number says.
2. A triple that is `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` -> that
   functional is `NOT A RESULT`, with the value and `R` printed beside it.
3. Only a `CONVERGING` triple reaches a band. The gate can turn a `PASS` or a
   `GATE FAIL` **into** `NOT A RESULT`, never the reverse.

Classification, with `eps21 = f1 - f2`, `eps32 = f2 - f3` (`1` = fine = L3):

| condition | label |
|---|---|
| both `\|eps\|` below the floor | `EXACT` |
| one `\|eps\|` below the floor | `STAGNANT` |
| `R = eps21/eps32 < 0` | `OSCILLATORY` |
| `R >= 1` | `DIVERGENT` |
| `0 < R < 1` | `CONVERGING` |

Floors, registered: `1e-4 * \|f1\|` for `gradP` and `Kint`; `1e-3` absolute (in
`h`) for `xr`. The relative floor is set at the iterative-plateau tolerance for
a reason: **a level-to-level difference smaller than the iterative noise is not
a discretisation signal.**

`0 < R < 1` requires `eps21` and `eps32` to share a sign, so **the `CONVERGING`
branch is exactly the monotone branch**. `p` and the GCI are computed and
printed **only inside it**, which is how "never quote a GCI when the three
values are not monotone" is enforced rather than remembered.

### 5.2 Order and GCI, closed form, because `r` is exactly 2

    p     = ln|eps32/eps21| / ln(r),      r = r21 = r32 = 2
    f_ext = f1 + eps21/(r^p - 1)
    GCI_fine = Fs * |eps21/f1| / (r^p - 1),   **Fs = 1.25**

### 5.3 The registered bands

| functional | `p` band | GCI_fine ceiling |
|---|---|---|
| **PRIMARY `gradP`** | **[1.0, 3.0]** | **5.0 %** |
| SECONDARY-A `Kint` | [0.5, 3.0] | 10.0 % |
| SECONDARY-B `xr` | [0.5, 3.0] | 10.0 % |

**Why [1.0, 3.0] on the primary.** The momentum discretisation is formally
second order (`Gauss linear` laplacians with `corrected`, `linearUpwind` for
`div(phi,U)`, `system/fvSchemes:33`) but **`div(phi,k)` is first-order upwind**
(`system/fvSchemes:34`). The coupled system's formal order is therefore bounded
below by 1 and above by 2. **`div(phi,omega)` is not specified at all** and
falls through to `default Gauss linear` (`system/fvSchemes:32`) -- unbounded
central differencing; see §10 item 11. `p < 1` means the discretisation is not
delivering even the floor its own upwind turbulence convection sets; `p > 3` is
superconvergence or noise, not asymptotic behaviour. The secondaries get [0.5,
3.0] because a wall-shear-derived location and a shear-layer-dominated integral
have a documented tendency to sub-first-order behaviour on separated flows.

### 5.4 Verdict mapping, and the rung's headline

`CONVERGING` + `p` in band + GCI within ceiling -> **`PASS`**.
`CONVERGING` + either outside -> **`GATE FAIL`**.
Not `CONVERGING` -> **`NOT A RESULT`**.

**The rung's headline verdict is the PRIMARY's.** The secondaries are reported
with their own verdicts and **never change it**. Vocabulary is
`PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and the
comparator refuses if it is about to print anything else.

### 5.5 The registered falsifier (`CLOSURE_MODELLING_CHARTER.md` §12)

G1 is falsified if the `gradP` triple is `CONVERGING` and either `p` falls
outside [1.0, 3.0] or GCI_fine exceeds 5.0 %. That is a `GATE FAIL` and it is a
publishable finding about this solver setup, not a failure of the rung.

---

## 6. Controls. Each is a standing rule, not a nicety

### 6.1 THE REFINEMENT-FAMILY CONTROL -- closure's own scar, made executable

The lab was nearly fooled by `alpha_10_9000_{2024,3036,4048}`: three sibling
directories that look like a refinement family and are not. **Measured, for this
pre-registration:**

| directory | `nCells` | `vertices` block sha256 (first 16) |
|---|---|---|
| `alpha_10_9000_2024` | **15600** | `4d09cc454bf5ca3c` |
| `alpha_10_9000_3036` | **15600** | `8d051162cdd020a7` |
| `alpha_10_9000_4048` | **15600** | `6a21a51d0d057b09` |

Identical cell counts, three different geometries. The suffix is the **domain
height**, not a grid level. The control has two clauses, either of which alone
rejects that set:

1. The three levels' `vertices` blocks are **byte-identical**, and every byte of
   the dictionary outside the two `hex` block lines is byte-identical, compared
   by **sha256 of the bytes** -- never by line count, never by file size. A
   length check passes on all three of the directories above; that is exactly
   how this class of defect is missed.
2. The three `nCells`, read from each `constant/polyMesh/owner` note, are
   **distinct** and in the registered ratio `1 : 4 : 16`.

Additionally each level's dictionary must reduce to the source **byte for byte**
under back-substitution of its own resolution literal, and every other staged
file must be byte-identical across the three levels. **Any failure is a refusal
(`sys.exit(2)`), not a warning.** The control is enforced twice: in
`build_g1.py` at stage time and again in `grade_g1.py` at grade time, so a
post-stage edit cannot slip through.

### 6.2 PLANTED-ZERO CONTROL (standing rule 3) -- round-tripping real files

**An in-memory plant does not satisfy rule 3.** Closure was already caught on
exactly that: `score_gpu_ling.py:85-88` plants a perturbation that never
round-trips a file. All three controls here **write a real file and read it back
through the same function used on the real data**, and each **refuses
(`sys.exit(2)`)** if the reader cannot see the plant.

1. **`gradP`.** The real `momentumSourceProperties` is copied, its `gradient`
   value rewritten on disk to `1.234567e-03`, and read back through
   `read_gradP_disk`. Refuses if the reader does not return the plant. Then the
   **inverse**: the same reader on the unplanted file must **not** return the
   plant -- otherwise it is a constant, not a reader.
2. **`Kint`.** (a) `k` is rewritten on disk to a uniform `2.0` and the integrator
   must return `2.0 * sum(V)` to 1e-9 relative -- a **closed-form** answer.
   (b) a **single cell at a known index** is rewritten to `9.876543e+02` and the
   integral must move by exactly `delta * V_index` -- proving the reader reads
   per-cell values at the right index, not a bulk average.
3. **`xr`.** A wall-shear profile with a crossing at exactly `x = 4.2345` is
   **synthesised on disk in OpenFOAM ASCII** with matching face centres, and the
   crossing finder must recover `4.2345` to 1e-9. Then a profile with **no**
   crossing is written and the finder must **refuse** rather than return a
   number.

Each control was mutation-tested: with the `gradP` reader replaced by one that
returns `0.0`, the control **fires**.

### 6.3 STRICT COMPLETION + AGE GUARD (standing rule 4), all-or-nothing

Per level, every clause. **PHYSICS clauses refuse. INFRASTRUCTURE clauses are
named and recorded (L-342, §6.5).**

| # | class | clause |
|---|---|---|
| P1 | PHYSICS | `rc.txt` holds `0` |
| P2 | PHYSICS | `log.run` holds an `End` line |
| P3 | PHYSICS | `log.run` holds no `FOAM FATAL` / FPE / signal line |
| P4 | PHYSICS | the last numeric time directory **is** `endTime` |
| P5 | PHYSICS | `U p k omega nut` and `uniform/momentumSourceProperties` present at `endTime` |
| P6 | PHYSICS | **age guard** -- every one of those is strictly newer than the case's own `0/U` |
| P7 | PHYSICS | `ExecutionTime` line count `== endTime` |
| I1 | INFRA | `log.checkMesh` exists and says `Mesh OK` |
| I2 | INFRA | `mem_time.txt` holds a `/usr/bin/time -v` MaxRSS reading |
| I3 | INFRA | `wall_s.txt` recorded (the cost calibration's actual) |
| I4 | INFRA | `V`, `C`, `wallShearStress`, `yPlus` present at `endTime` |

**The age marker is `0/U`, and `run_g1.sh` touches it LAST, immediately before
the solver launch** -- exactly as the T-family touches `0/T`, and for the same
reason: it dates the run that was allowed to produce the answer. `build_g1.py`
**refuses to stage into a directory that already exists**, so no level can start
in a tree that already holds an answer.

**P7 and L-342, stated in advance.** P7 is the clause that was reclassified as
infrastructure on VMFLGPU001 when `petsc4Foam` printed `endTime + 2` lines. Here
it **refuses**, because standing rule 4 says `== endTime` and this lane does not
pre-authorise its own degradation. If it fires, the pre-registered remedy is
**supervisor triage of the cause**, never a silent reclassification by the
comparator.

### 6.4 ITERATIVE CONVERGENCE, per level

| # | clause |
|---|---|
| IC1 | final initial-residual, first solve of the last `Time =` block: `Ux, Uy, k, omega <= 1e-5`; `p <= 1e-4` |
| IC2 | **plateau on the primary functional itself**: over the final 10 % of iterations, `max\|gradP - gradP_end\| / \|gradP_end\| <= 1e-4` |
| IC3 | the disk `gradP` and the last log `gradP` agree to 1e-9 relative -- two independent reads of one quantity |

IC2 is the physically meaningful test and it is deliberately three orders
tighter than the level-to-level differences the rung is trying to measure. A
level failing any of these makes the **rung** `NOT A RESULT` under rule 5 step 1.

**No re-run with a longer `endTime` is permitted under this pre-registration.**
Lengthening a run after seeing that it did not plateau is tuning against the
answer. That is why the iteration budgets carry a 1.5x-2x margin up front (§3.6).

### 6.5 L-342 -- physics against infrastructure, and it is demonstrated

Sanaa's universal rule: bookkeeping never voids physics. Here the split is
concrete and was **exercised end-to-end**, not merely asserted:

* corrupting the `V` field makes SECONDARY-A `NOT A RESULT` while the PRIMARY
  still returns `PASS` -- `gradP` needs no post-processing artefact;
* changing the wall-shear crossing topology at one level makes SECONDARY-B
  `NOT A RESULT` while the PRIMARY stands;
* a lost `mem_time.txt` or `wall_s.txt` is printed as `INFRASTRUCTURE DEFECT`,
  carried into the record, and voids nothing.

### 6.6 L-332 -- no refusal may be an `assert`

`python3 -O` deletes every `assert` from the compiled code. **Every refusal in
both instruments is a `raise` or a `sys.exit(2)`**, and each instrument parses
**its own AST** and refuses if a single `ast.Assert` node exists -- with the
counter first shown able to count a **planted** assert, so its zero is a reading
and not a blind spot.

**Both selftests were run under `python3` and under `python3 -O`, with
`__pycache__` cleared between, and every registered refusal fired identically
under both. `rc = 0` in all four runs.**

---

## 7. Cost. Measured basis, and the box cannot read its own billing

**Rate.** `4.5e-06 s per cell-iteration, serial`. This is **deliberately
conservative**: it sits 8.7 % **above** the highest of five corroborating
measurements on this box -- 3.575e-06 at 3,025 cells, 4.010e-06 at 8,748,
3.084e-06 at 15,600, **4.138e-06 at 21,000** (five capped CBFS rows: 13,033.59 s
over 150,000 iterations = 0.0868906 s/iteration).

**Runs are SERIAL, 1 rank.** Closure launches `simpleFoam -case .` with no
`mpirun`, no `decomposePar` and no `processor*` directories
(`Kaandorp2020_TBRF/aposteriori/run_lane.py:157`). With `ranks = 1`,
core-minutes equal wall-minutes.

| level | cells | `endTime` | cell-iterations | wall s @ 4.5e-06 | core-min |
|---|---|---|---|---|---|
| L1 | 3,840 | 20,000 | 7.680e07 | 345.6 | **5.76** |
| L2 | 15,360 | 30,000 | 4.608e08 | 2,073.6 | **34.56** |
| L3 | 61,440 | 60,000 | 3.6864e09 | 16,588.8 | **276.48** |
| solver subtotal | | | 4.2240e09 | 19,008.0 | **316.80** |
| `blockMesh` + `checkMesh` x3 | | | | **1.99 (MEASURED)** | 0.03 |
| `-postProcess`, 4 funcs x3 | | | | 60 (estimated) | 1.00 |

**REGISTERED ESTIMATE: 320.0 core-minutes.**
Derived: 5.333 core-h x $0.0513/core-h = **$0.274 -- derived at the
owner-stated rate, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5: this box
cannot read its own billing).

**REGISTERED CAP: 600.0 core-minutes** = 36,000 s, allocated as per-level
`timeout` values 900 / 5,400 / 29,700 s summing to exactly the cap.
Derived: 10.0 core-h x $0.0513 = **$0.513 -- derived, NOT MEASURED.**

**The cap is the runaway guard, not a target**, and its 1.875x ratio to the
estimate is justified, not rounded: the largest calibration point on record is
21,000 cells, and **L3 at 61,440 is 2.9x beyond any measured point**, where
per-cell cost typically rises with `N` through cache pressure (the cfd team
modelled +30 % per doubling on F25_DUCT3D). A worst case of 6.0e-06 s per
cell-iteration gives 25,344 s = 422.4 core-min; a 1.4x allowance for contention
on a box that has been running near 89 % busy gives 591. **An overrun stops the
run; it does not get a new budget** (standing rule 12), and `run_g1.sh` enforces
this twice -- a per-level `timeout`, and a cumulative watch that refuses to
start a level whose budget would breach the cap.

Both figures are far under $25 and so sit inside the 2026-08-21 blanket, and
inside `CLOSURE_MODELLING_CHARTER.md` §18's 487 pre-authorised core-hours. **A
blanket is not a per-item read** (standing rule 9); the cost is registered here
regardless.

**Estimate-versus-actual calibration is owed at completion** (standing rule 12).
`run_g1.sh` records `wall_s.txt` per level for exactly this. The comparison --
ratio actual/predicted, gap attributed to contention, waste or misprediction,
waste named separately and never absorbed into the ratio -- lands as a row in
`docs/COST_CALIBRATION.md`. **A completion report without it is incomplete.**

---

## 8. `memory_floor_gb` -- an allowance, and it says so

A previous lane rightly refused to invent one: there is no memory
instrumentation here, and OpenFOAM's `memory pool : not available` banner is a
capability notice, not a reading. **Both routes the brief offered are taken.**

**Derived term.** At L3, 61,440 cells: fields, the `fvMatrix` diagonal/upper/
lower/source for `U p k omega`, and Krylov workspace come to roughly 60 doubles
per cell = 29.5 MB, plus about 25 MB of mesh addressing -- **circa 55 MB of
solution data, derived, not measured.**

**Measured anchors, taken by this lane at L3 with `/usr/bin/time -v`:**
`blockMesh` MaxRSS **123,644 kB (120.7 MiB)**; `checkMesh` MaxRSS **177,692 kB
(173.5 MiB)**. These bound the OpenFOAM runtime plus mesh footprint at the
finest level and are readings, not estimates.

**`simpleFoam`'s own footprint is NOT measured and this lane could not measure
it**, being forbidden to launch a solver. Adding the derived solution term to
the measured runtime anchor gives an estimate near 250-350 MB.

**Registered: `memory_floor_gb = 1.0`, an ALLOWANCE**, roughly 3x that estimate
and 6x the largest measurement -- **explicitly not a measurement.**
`run_g1.sh` wraps every solver invocation in `/usr/bin/time -v -o mem_time.txt`
and the comparator prints the recovered MaxRSS per level, **converting this
allowance into a reading for the next pre-registration.** Its absence is an
INFRASTRUCTURE defect (I2), not a physics refusal.

---

## 9. Queue entry

`QUEUE_ENTRY_DRAFT.json` sits **beside this document, in the case directory**,
and is **not** in the drop path. That is deliberate and it is a safety property,
not an oversight: `crontab` runs `scripts/queue_runner.sh` **every minute**, so a
valid entry in `verification/queue/closure/` is launched by a cron-restarted
daemon within about 60 seconds.

**Two independent things stop this draft from launching anything:**

1. It is not in a drop path.
2. `prereg_commit` is the literal string `PENDING_SUPERVISOR_FREEZE`, which
   fails the validator's `SCHEMA` check (`FULL_SHA = ^[0-9a-f]{40}$`,
   `scripts/queue_entry_check.py:97`) and can never validate until the
   supervisor replaces it with the real freeze sha.

**`cwd` is the RUN ROOT `/home/ubuntu/closure-data/g1/`, pre-created empty by the
supervisor at enqueue, and NOT the repository case directory.**

*Supervisor's correction, made before the freeze and recorded because the
drafting brief carried the error.* The brief asserted that "closure cases build
their run directory at launch, so the run directory can never be a legal `cwd`".
That is a false constraint: nothing prevents the run root being **created empty
before enqueue**, and `AGE-GUARD` asks only that `cwd` exist and hold no `0/` or
numeric time directory (`scripts/queue_entry_check.py:277-283` iterates
`target.iterdir()` -- **immediate children only**).

**Why the case directory is the wrong `cwd`, and this is the load-bearing
reason:** the runner launches as `cd <cwd> && <argv> > <cwd>/launcher.queue.out
2>&1` and then writes `<cwd>/STATUS.<case_id>` (`scripts/queue_runner.py:280-281`).
With the case directory as `cwd`, **every launch drops run output inside the
tracked repository** -- run outputs living beside the prose that describes them,
which `FILING_CHARTER.md` forbids, and a dirty worktree on the case directory
after every launch.

**Why pre-creating the root is safe, verified in the builder rather than
assumed:** `build_g1.py`'s `guard_dest` is called on `dest_root / <LEVEL>` --
`g1/L1`, `g1/L2`, `g1/L3` -- and **not on `dest_root` itself**
(`build_g1.py:275-289`). An empty `g1/` therefore does not trip the builder's own
age guard, while a re-stage over an existing level still refuses exactly as
registered. `run_g1.sh` is fully path-independent: it uses absolute `CASE_DIR`
and `RUN_ROOT` and reads nothing from its working directory, and `launch_cmd`
names the driver by absolute path.

**Run outputs go to `/home/ubuntu/closure-data/g1/`, never beside the prose** --
and with this correction the launcher's own two artifacts go there too.

`cap_core_min_registered` is carried as an optional field for the runner's cap
watch. So is `memory_floor_basis`, because §8's honesty belongs where the number
is read, not only in a document.

**A green verdict from the validator is not an approval**
(`QUEUE_ENTRY_STANDARD.md` §1). The supervisor's personal check 4 happens at
enqueue and is not delegable to a machine or to this lane.

---

## 10. What it cannot see

`CLOSURE_MODELLING_CHARTER.md` §16 makes this section mandatory.

1. **It cannot see whether k-omega SST is right.** A `CONVERGING` triple with a
   1 % GCI says the discrete equations are being solved consistently and that
   the answer is converging to *something*. It says nothing about whether that
   something is the flow. Grid convergence and validation are different
   columns; this rung fills only `G`.
2. **It cannot see agreement with LES or DNS.** No reference field is read. The
   shipped `0/U_LES`, `0/k_LES` and `0/tauij_LES` exist only on the 15,600-cell
   mesh and are **not** staged; interpolating them onto L1 and L3 would be
   validation work, and this rung does none.
3. **It cannot see error at the coarse end if L1 is outside the asymptotic
   range.** 60x64 cells over `9h x 3.036h` may simply be too coarse for the
   separated shear layer, in which case the triple will come out non-monotone
   and the rung will be `NOT A RESULT`. That is a real and registered
   possibility, not a defect of the instrument.
4. **It cannot see the 0.33 % departure from exactly systematic refinement as
   an error bar.** §3.4 measured the smallest cell's area ratio at 4.0133 and
   3.9966 against an ideal 4.0000, and the GCI uses `r = 2` exactly. The
   resulting bias on `p` is not quantified here and no attempt is made to
   correct for it.
5. **It cannot see whether `simpleFoam` runs this case under v2606.** This lane
   proved only that `blockMesh` parses the dictionary. The solver was never
   launched, by design. L1 is the fail-fast.
6. **It cannot see a defect in the shipped source case.** The three levels
   inherit whatever the shipped `fvSchemes`, `fvSolution`, `transportProperties`
   and boundary conditions contain. If the shipped setup is wrong, all three
   levels are wrong the same way and the triple will converge beautifully to the
   wrong answer. **A consistent scheme converging is not a correct scheme.**
7. **It cannot see unsteadiness.** `ddtSchemes default steadyState`. If the true
   flow at `Re_H = 5600` on this geometry is not steady, the plateau gate will
   either refuse or will certify a converged steady state that does not exist
   physically.
8. **It cannot see anything about the other 39 closure geometries.** `CBFS`,
   `PH_Breuer` and every `DUCT` case ship as frozen `polyMesh` with no
   dictionary, so **G1 gives `G = HOLDS` for one geometry and leaves the rest
   exactly where they were.** Claiming otherwise would be the whole point of the
   matrix misread.
9. **It cannot see its own cost accurately at L3.** Every rate calibration on
   record is at 21,000 cells or fewer; L3 is 2.9x beyond the largest. The
   estimate may be wrong by tens of percent in either direction, which is what
   the cap and the §7 calibration obligation exist for.
11. **It cannot see whether unbounded central convection of `omega` will
    behave.** `divSchemes` specifies `div(phi,U)`, `div(phi,k)`,
    `div(phi,epsilon)` and `div(phi,R)` but **not `div(phi,omega)`**, which
    therefore falls through to `default Gauss linear` -- pure central
    differencing on a transported turbulence scalar. Refinement changes the
    cell Peclet number, so the effective boundedness of that scheme changes
    across the family. This is a live risk to a monotone triple and it is
    registered before the run, not discovered after. **The shipped `fvSchemes`
    is nevertheless kept byte-identical**, because the family control and the
    provenance to the shipped case are the rung's whole evidentiary content. If
    the triple comes out non-monotone, the pre-registered next step is a
    SEPARATE rung, separately pre-registered, repeating the triple with
    `div(phi,omega) Gauss upwind` -- never an edit to this one.

10. **It cannot see whether the ordering `p` it reports is the true asymptotic
    order** on three grids alone. Three points give one estimate of `p` with no
    residual degrees of freedom; the GCI's `Fs = 1.25` is Roache's allowance for
    exactly that, and it is an allowance, not a bound.

---

## 11. The grading path is fixed at the freeze

The comparator is `grade_g1.py` **as it exists at the pre-registration commit**,
and the stager is `build_g1.py` at the same commit. Before grading, the frozen
files must be hashed against the committed blobs to verify that the frozen file
**is** the file that ran (standing rule 2;
`scripts/check_comparator_freeze.py`).

**After first compute, gates are closed.** Changes land only as dated addenda
that cannot alter a gate, a threshold, a cap or a label; originals are struck,
never rewritten. **Before first compute, amendments are legal and must state the
condition and how it was checked** -- for this rung, that the run root
`/home/ubuntu/closure-data/g1/` does not exist and holds 0 core-minutes.

---

## 12. Files

| file | role |
|---|---|
| `PREREGISTRATION.md` | this document |
| `build_g1.py` | stages the three case trees; refuses over an existing tree; enforces the family control at stage time |
| `run_g1.sh` | the driver the queue entry names; meshes all three, then solves ascending, rc captured in its own foreground |
| `grade_g1.py` | the comparator: family control, strict completion, planted-disk controls, plateau, Roache, GCI |
| `QUEUE_ENTRY_DRAFT.json` | the queue entry, deliberately unvalidatable until the supervisor freezes |

**Every one of them carries the draft banner on line 1**, including the JSON,
where it makes the file deliberately unparseable as a second, independent block
on any accidental launch. **The supervisor strips line 1 of the JSON at freeze
time**, together with replacing `prereg_commit`.

---

## AMENDMENT 1 — 2026-08-27, closure supervisor: the driver's environment step, repaired PRE-COMPUTE

**Appended at the foot. Lines whose number changed above this section: 0** — the
795-line body above is byte-for-byte the text frozen at `03be2015`,
sha256 `d61a6704cd2ea64cca4eba8da11557487727a1ef9f48648987978b223ca49a3f`, re-hashed in the same shell invocation as this append.
**No gate, threshold, band, cap or label is altered by this amendment.** §5's
bands, §5.4's verdict mapping, §5.5's falsifier, §7's ESTIMATE 320.0 and CAP
600.0 core-min all stand exactly as frozen.

### The condition under which this amendment is legal, and how it was checked

Standing rule 2 permits amendment **before first compute** and requires the
condition to be stated and checked. **Checked in the invocation that wrote this
section, on the run root itself:**

| probe | count |
|---|---|
| staged levels `g1/L1`, `g1/L2`, `g1/L3` | **0** |
| `log.run` anywhere under the run root | **0** |
| numeric time directories anywhere under the run root | **0** |
| field files (`U`, `p`, `k`, `omega`) anywhere under the run root | **0** |

The run root holds exactly three files — `CHAIN.log`, `STATUS.G1_grid_triple`,
`launcher.queue.out` — and **all three are INFRASTRUCTURE records under L-342**.
**No solver ran. No mesh was built. No field was written. No gate fired and no
number exists that any band could have been fitted to.**

### What happened

The runner launched G1 at **2026-08-27T17:28:58Z**, pid 1109265, against this
pre-registration at `03be2015` (`verification/queue/LAUNCH_LOG.tsv`). The driver
wrote its `CHAIN START` line and **exited rc 1 within the same second**, with
**no `CHAIN ABORT` line** — that is, it terminated *outside its own error
handling*, which is what made the failure worth triaging rather than retrying.

**Cause, established by reproduction with a fired control, not by inspection:**

* `bash -c 'set -u; source /usr/lib/openfoam/openfoam2606/etc/bashrc'` →
  **`bashrc: line 184: WM_PROJECT_DIR: unbound variable`**, and the shell
  **terminates immediately**. Under `set -u` a non-interactive shell treats an
  unbound expansion as fatal, so the shell died *before* `die` could log.
* **Control:** the identical source **without** `set -u` returns **0** with
  `simpleFoam` on `PATH`.

The original line also redirected the source to `/dev/null 2>&1`, so **the single
message that named the cause was discarded** — the failure presented as a silent
rc 1. That is the same shape as a zero from a reader that was never shown able to
see a non-zero: a diagnostic thrown away is a diagnostic that cannot testify.

### The repair, and its scope

`run_g1.sh` only. Nounset is lifted **for the source alone** and restored
immediately after; the source's own output is **kept in `log.foamenv`** instead of
being discarded; and its rc is logged as **INFRASTRUCTURE**, explicitly *not* as a
gate — the binding checks remain the two `command -v` tests that follow, which
`die` on failure exactly as frozen. Five functional lines. The supervisor read the
patch **as a patch** (`SUPERVISION_CHARTER.md` §3 check 1) before it landed.

### What this amendment does NOT do

It re-grades nothing, because nothing was graded. It relaxes no threshold. It does
not touch `build_g1.py` or `grade_g1.py`, whose sha256 stand as frozen at
`03be2015`. **A launcher that never reached physics is an infrastructure failure,
and L-342 is explicit that a bookkeeping failure invalidates the bookkeeping and
never the physics — here there is no physics yet to protect.**
