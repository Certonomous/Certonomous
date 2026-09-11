# PERMISSION: NOT_FROZEN — DRAFT, awaiting supervisor check

> **THIS DOCUMENT IS A DRAFT. IT IS NOT FROZEN, IT IS NOT COMMITTED, AND NO ARM MAY LAUNCH AGAINST IT.**
> Freezing is the `dafoam-supervisor`'s act and is not delegated (`CLAUDE.md` rule 2;
> `SUPERVISION_CHARTER.md` §3). Launching is the supervisor's act. The lane that wrote this file ran
> **zero solver compute**; the compute it did run is a pre-compute feasibility probe, itemised and
> priced in §9, and is disclosed rather than hidden because it measured facts that appear as
> registered predictions below.
>
> **Nothing in this item is filed, sent, uploaded, posted, registered or pushed anywhere.
> SUBMISSIONS ARE PARKED and sending is Sanaa's decision alone** (`CLAUDE.md` rule 7;
> `DAFOAM_CHARTER.md` §10).

---

# CURRICULUM D8G — A6 CRM **WING-ALONE**, a three-level **GRID-CONVERGENCE TRIPLE** at **r = 2 exactly**, on **TWO TOOLCHAIN ROWS**, with an adjoint **FD table at the finest adjoint-capable level** — PRE-REGISTRATION

**Draft v0.1, dated 2026-09-10.** Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
Repository HEAD at drafting: `206f7910a`. Drafting timestamp `2026-09-10T20:22:19Z` (`date -u`).

**Case class:** 3D, steady, transonic, external, wall-resolved, RANS (Spalart–Allmaras),
`DARhoSimpleCFoam`. Governed by `CASE_PROTOCOL_CHARTER.md` (3D scope) and `DAFOAM_CHARTER.md`.

---

## 0. WHY THIS ITEM EXISTS, AND WHAT IT IS NOT

**Sanaa, ~19:45Z 2026-09-10, byte-exact:** *"GOOD. ALL teams remmeber the goal: we want to have all
these complicated cases run and complete, and wit their mes convergence ASAAAP. THIS is the priority
in the coming days. More than anything else"*

The dafoam ladder holds **no valid three-level grid family on any 3D case**. A6 has two levels
(41,760 and 579,072) and the fine one is `BLOCKED` twice over; A3's four levels share a
**byte-identical surface mesh** and refine only pyHyp's wall-normal marching count, so they cannot
carry a GCI. **Two levels is not a triple, and a one-directional family is not a refinement family.**
D8G buys the first A6 grid triple that has ever existed.

### 0.1 THE CASE IS THE CRM **WING-ALONE**, AND THIS IS NOT THE WING-BODY

Stated first because the two are routinely conflated in this lab's prose.

| | CRM **wing-alone** (this item, and D8/D8R) | CRM **wing-body** (a different case) |
|---|---|---|
| patches | exactly **3**: `wing` (wall), `inout` (patch), `sym` (symmetry) — no body patch | includes a fuselage patch |
| graded predecessor | **D8R**, `PASS`, two rows, closed 2026-08-28 | none |
| adjoint | run, converged, FD-verified at 41,760 cells | **never attempted** |
| status at full size | `BLOCKED` (memory 94.7–116.0 GiB vs a 30 GiB box; and independently conditioning) | — |

**Read first-hand by this lane:** `/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/base/constant/polyMesh/boundary`
declares `3` patches and exactly the three named above, with `nFaces` 2,784 / 2,784 / 1,020.
`cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/PREREGISTRATION.md:1` reads
*"A6 CRM wing-alone, rung N=16 (41,760 cells), np=1"*. **No sentence of this document is about the
wing-body, and the 579,072-cell figure that appears below is the wing-alone at the archived recipe's
own coarsening, not the wing-body.**

### 0.2 WHAT D8G IS NOT

* **It is not a validation against experiment.** No external reference value for CD or CL is
  registered, and none is reachable from this box's records for this geometry at these conditions.
  **The item therefore can never return a PASS against a measurement, only against a convergence
  criterion**, and that is registered here so it cannot later be presented as validation.
* **It is not an optimisation.** The design is held at the baseline (`twist = 0`, the archived
  `aoa0`) at every level. No IPOPT, no trim.
* **It does not carry a triple on the gradient.** §7 registers why, before the run.

---

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple` DOES NOT EXIST,
> and the case directory `cases/dafoam/ladder-a/A6/curriculum_D8G/` contained no file before this one.**

`test -e` on the run root returned **NO** at **2026-09-10T20:22:19Z**, in the same shell invocation
that stamped the date and read `HEAD = 206f7910a`. **Zero solver core-min have been spent against
this item; no arm container has started.** Amendments before first compute are legal and must state
their condition (`CLAUDE.md` rule 2); after the first arm container, gates are **CLOSED** and changes
land only as dated addenda that cannot move a gate, threshold, cap or label.

**Disclosed, because it is the honest boundary of the sentence above:** this lane spent
**≈ 12 core-min of NON-SOLVER compute** before writing this file — CGNS coarsening, three pyHyp mesh
generations and `checkMesh` — itemised in §9.4. Mesh generation is deterministic case construction,
not a measurement, and the A6 family has made this disclosure before
(`rung_n16_np1/PREREGISTRATION.md`, "Ordering disclosure"). **Every number that probe produced
appears below as a registered PREDICTION that the item must reproduce under its own launcher, not as
a result.** No primal, no adjoint and no gradient has been run.

---

## 2. THE GRID FAMILY — MEASURED, NOT PROPOSED

### 2.1 The refinement operator, and the arithmetic that makes it systematic

The archived A6 recipe (`/home/ubuntu/certonomous-runs/A6-crm-wing/preProcessing.sh`, `genWingMesh.py`)
is: `tar -xvf CRM_surfMesh.cgns.tar.gz` → `cgns_utils coarsen surfMesh.cgns` → `python genWingMesh.py`
(pyHyp) → `plot3dToFoam -noBlank` → `autoPatch 45 -overwrite` → `createPatch -overwrite` →
`renumberMesh -overwrite`. Volume cells `= wing_faces × (N − 1)`.

`cgns_utils coarsen` divides the surface quad count by **exactly 4** (r = 2 in both surface
directions). Halving the pyHyp node count `N − 1` gives r = 2 in the third. **Cells therefore scale as
r³ = 8, not as r** — which is the discriminator A3's family fails.

**Measured by this lane on the archived tarball, 2026-09-10** (surface quad faces after each
successive `cgns_utils coarsen`):

| coarsen count | surface quad faces | ratio to previous | surface points |
|---|---|---|---|
| c0 (as shipped in the tarball) | **44,544** | — | 46,762 |
| c1 | **11,136** | **4.000** | 12,258 |
| c2 | **2,784** | **4.000** | 3,358 |
| c3 | **696** | **4.000** | 996 |
| c4 | 188 | **3.702** ← **BREAKS** | 356 |

**c4 is excluded from the family and the reason is registered:** the ratio is 3.702, not 4, because
several blocks of this 26-block surface reach a 2-node dimension that cannot be coarsened again.
**A level at c4 would not be a factor-2 coarsening of c3 and must never be used as one.**

Two independent confirmations that this operator is the one the archive used:
`11,136 × 52 = 579,072` — the archived recipe's own measured cell count
(`A6-crm-wing/logMeshGeneration.txt:478`, `Mesh region0 size: 579072`, at c1 and `N = 53`); and
`2,784 × 15 = 41,760` — the graded D8/D8R mesh, at c2 and `N = 16`.

### 2.2 The three registered levels

| level | surface | pyHyp `N` | layers `N−1` | `s0` | **cells** | ratio | pyHyp `Grid Ratio` |
|---|---|---|---|---|---|---|---|
| **L1** coarse | c3 (696 faces) | 9 | 8 | 4.0e-4 | **5,568** | — | **4.0000** |
| **L2** medium | c2 (2,784) | 17 | 16 | 2.0e-4 | **44,544** | **8.000** | **2.2993** |
| **L3** fine | c1 (11,136) | 33 | 32 | 1.0e-4 | **356,352** | **8.000** | **1.5044** |

`marchDist = 25 × 3.758151` and every other pyHyp option unchanged from the archived
`genWingMesh.py` at all three levels. **`r = 2.000 exactly in all three directions**, and both cell
ratios are the exact integer 8.

**`s0` is scaled with `r`, and the choice is registered with its cost.** A family that refines the
surface and the outer marching but holds the first cell height fixed does **not** refine the
wall-normal direction where it matters, so `s0` halves with the level. The consequence, stated
because it is a real confound and not a detail: **y⁺ changes by a factor of 2 per level**, so the
SA model's near-wall treatment is not identical across the family. The alternative (fixed
`s0 = 1e-4`) was rejected because it makes the near-wall spacing non-systematic; it is registered as
the **first escalation action** in §8 if the triple fails on L1.

### 2.3 **This family's fine level is NOT the D8R mesh, and D8R's PASS does not transfer**

L2 (44,544 cells, c2, `N = 17`, `s0 = 2e-4`) sits beside the graded D8R mesh (41,760 cells, c2,
`N = 16`, `s0 = 1e-4`) — same surface, different marching. They are **6.7 % apart in cells and are
different meshes**. D8R's two-row `PASS` is a statement about `points.gz` md5
`11b84f0de5fdf2d3e947fee8cea412a9` and about nothing else. **D8G's L2 must earn its own primal and
its own FD table.** The D8R mesh is used in this document only as a **measured reference point** for
the mesh-quality gate (§4.2) and for cost.

---

## 3. TOOLCHAIN IDENTITY — TWO ROWS, BY SHA256

`DAFOAM_CHARTER.md` §6: *"a version string is not an identity."* Both image IDs were read from this
box with `docker images --digests --no-trunc` on 2026-09-10, not copied from a record.

| row | image | **image ID (the identity)** | IDWarp `.so` md5 |
|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |

**PATCHED runs first**, as in D8R. Both `.so` md5s are printed by the container and read in-process;
**a row whose printed md5 is not its registered md5 is `GATE FAIL` on that row** (D8R's G9, cited not
re-derived, `curriculum_D8R/RESULTS.md` §0).

**`cgns_utils` and `pyhyp` are present in BOTH images**, verified first-hand 2026-09-10:
`cgns_utils` at `/home/dafoamuser/dafoam/packages/miniconda3/bin/cgns_utils` with a live
`coarsen` subcommand in each; `import pyhyp` succeeds in each; `checkMesh` is the OpenFOAM-**v2506**
binary in each. **The mesh family is therefore generatable inside the graded toolchain and not only
on the host.** (`cgns_utils refine --axes` also exists and is **not** used by this item.)

**Decomposition, disclosed in the same place as the numbers (`DAFOAM_CHARTER.md` §5):**
every arm `np = 4`, `scotch`, cpuset assigned by the launcher. **A gradient verified at one `np` is a
statement about that `np`** and is never carried.

---

## 4. THE GATES

All thresholds below are fixed **before** any arm runs. Verdict vocabulary is the six tokens and
nothing else (`CLAUDE.md` rule 1).

### 4.1 G-MESH — construction, per level, before any solver

Each level must satisfy **all** of:

1. **Cell count exactly** 5,568 / 44,544 / 356,352. Integer equality. Anything else → `GATE FAIL`.
2. **Exactly 3 patches**, `wing` (`wall`), `inout` (`patch`), `sym` (`symmetry`), with `nFaces`
   696/696/272 · 2,784/2,784/1,088 · 11,136/11,136/4,352. **Zero patches of type `empty` and zero of
   type `wedge`**, read from `constant/polyMesh/boundary` and enumerated by name in the record.
3. **DIMENSIONALITY, and the authoritative line is named.** The record cites
   **`Mesh has N geometric (non-empty/wedge) directions`** and requires **N = 3** on every occurrence
   in the level's own `checkMesh` output. **`Mesh has 3 solution (non-empty) directions` sits four
   lines away and A WEDGE READS 3 ON THAT LINE** — it is recorded beside the geometric line and never
   instead of it. A level reading `N < 3` on the geometric line → `GATE FAIL`, and the item is
   `NOT A RESULT` (a one-cell-thick or wedge mesh is not the 3D case this item claims).
4. **BOTH `checkMesh` and `checkMesh -allGeometry -allTopology` are run, both logs retained.**
   `Mesh OK.` from plain `checkMesh` is **not** sufficient evidence of mesh health anywhere in this
   team's tree.

### 4.2 The strict-checkMesh gate is a **CONSISTENCY** gate, and here is why — measured

**Measured by this lane 2026-09-10 on all three generated levels AND on the graded D8R mesh:**

| mesh | cells | plain `checkMesh` | `-allGeometry -allTopology` | bad face tets | small-determinant cells | fraction |
|---|---|---|---|---|---|---|
| **L1** | 5,568 | `Mesh OK.` | **Failed 2 mesh checks** | 34 | 1,284 | **0.2306** |
| **L2** | 44,544 | `Mesh OK.` | **Failed 2 mesh checks** | 100 | 8,505 | **0.1909** |
| **L3** | 356,352 | `Mesh OK.` | **Failed 2 mesh checks** | 159 | 73,232 | **0.2055** |
| **D8R graded reference** | 41,760 | `Mesh OK.` | **Failed 2 mesh checks** | 243 | 9,735 | **0.2331** |

The two failing checks are, verbatim on every one of the four meshes:
`***Error in face tets: <n> faces with low quality or negative volume decomposition tets.` and
`***Cells with small determinant (< 0.001) found, number of cells: <n>`.

**Three things follow, and they are registered as findings, not as excuses.**

* **This is not a coarsening artefact.** It is present on the mesh that already carries D8R's
  two-row `PASS`, at the **highest** small-determinant fraction of the four. It is a property of the
  archived pyHyp hyperbolic extrusion — a wall-resolved O-grid whose near-wall cells have aspect
  ratios in the thousands scores a small determinant by construction.
* **`Mesh OK.` was never sufficient evidence on this case**, and a pre-registration that had gated on
  plain `checkMesh` would have passed all four meshes while the strict run failed all four.
* **Therefore a "strict checkMesh must pass" gate would fail every level of a family whose finest
  member is already graded, and registering one would be theatre.** The gate is instead:

> **G-MESH-STRICT.** `checkMesh -allGeometry -allTopology` on each level must fail **exactly** the
> two checks named above and **no others**, and the small-determinant fraction must lie in the
> registered band **[0.15, 0.28]** on every level. **A third failing check, a different failing
> check, or a fraction outside the band is `GATE FAIL`** — not a note, not a caveat. Every failing
> check is enumerated **by name** in the record, per level, together with what plain `checkMesh`
> said on the same mesh.

### 4.3 G-SYS — the refinement is systematic (the discriminator A3 fails)

1. **Cell-count ratios are the exact integers `8` and `8`**, i.e. r³ at r = 2. A ratio of ≈ 2 means
   the family is refining one direction whatever its cell count looks like → `GATE FAIL`.
2. **The three surface CGNS files are pairwise DISTINCT in their coordinate arrays.** Point counts
   12,258 / 3,358 / 996 (measured); `max |ΔX|` between successive levels' point sets > 1e-6.
   **A trap this lane hit and registers so nobody else does: file md5 is NOT the right instrument
   here.** Re-running `cgns_utils coarsen` on the same input produced a file byte-different from the
   archived one at identical size (`552,960` bytes both ways, different md5), so **CGNS file bytes are
   not reproducible** and md5 equality across a regeneration proves nothing. Compare coordinates.
3. **Patch face counts scale by exactly 4 per level** on all three patches, including `sym`
   (272 → 1,088 → 4,352). Measured.

### 4.4 G-BODY — the family must refine the discretisation, not change the body

Coarsening a curved surface changes the discrete body. Measured bounding boxes of the surface point
sets:

| surface | x range | y range | z range |
|---|---|---|---|
| c1 (L3) | [-0.0000, 3.2474] | [0.0000, 3.7667] | [-0.2029, 0.3461] |
| c2 (L2) | [-0.0000, 3.2474] | [0.0000, 3.7667] | [-0.2029, 0.3461] |
| c3 (L1) | [ 0.0071, 3.2471] | [0.0000, 3.7659] | [-0.2017, 0.3456] |

**L3 and L2 are identical in the discrete body to four decimals. L1 is not:** its leading edge is
truncated by **7.1e-3** length units — 0.41 % of the 1.746 root chord, 0.22 % of the 3.2474 body
length. **This is disclosed BEFORE the run because it is a named non-similarity in the family and a
plausible cause of a non-CONVERGING triple** (§8, P3).

> **G-BODY.** `|Δbbox|` L3↔L2 ≤ **1.0e-4** in every coordinate; L2↔L1 ≤ **1.0e-2** in every
> coordinate. Exceeding either → `GATE FAIL`.

**Trailing edge, measured, because coarsening is exactly the operation that would collapse it.**
Per spanwise band (10 bands), points within 0.5 % chord of the trailing edge, and the TE z-spread as
a fraction of local chord:

| surface | points within 0.5 %c of TE (min–max over bands) | TE z-spread / chord (min–max) |
|---|---|---|
| c1 (L3) | 13 – 80 | 2.099e-3 – 3.953e-3 |
| c2 (L2) | 7 – 25 | 1.725e-3 – 3.369e-3 |
| c3 (L1) | 4 – 12 | 1.797e-3 – 3.285e-3 |
| *(c4, excluded)* | *4 – 8* | *8.441e-4 – 3.625e-3* ← **degrades** |

**The trailing edge does NOT collapse down to c3.** It stays blunt with essentially unchanged
relative thickness, and the point count per band never falls below 4. **It DOES start to degrade at
c4** (the tip band drops to 8.4e-4), which is a second, independent reason c4 is out of the family.

> **G-TE.** Per level, per spanwise band: ≥ **4** surface points within 0.5 % chord of the TE, and
> TE z-spread / chord ∈ **[1.0e-3, 5.0e-3]**. **A level that closes the TE where a finer level does
> not is not the same body and KILLS THE TRIPLE** → `NOT A RESULT`, not `GATE FAIL`.

### 4.5 G-PRIMAL — primal acceptance, and this is where items get destroyed

**The quantity read is the printed `Primal min residual` where it prints, and OTHERWISE the MAXIMUM
over the per-equation INITIAL residuals of the FINAL outer iteration**, read from the printed
`initRes` block. For `DARhoSimpleCFoam` the equation set is **{U (median of U0,U1,U2), `he`, `p`,
`nuTilda`}** (`N-D44`). **`finalRes` IS NEVER READ.** A comparator built on `finalRes` is
**structurally blind** to the condition DAFoam fails on: on one lab case every per-equation
`finalRes` read ≤ 1e-6 on the exact iteration DAFoam declared the primal failed.

**This is not hypothetical on A6 — measured by this lane on all four D8R logs:** the string
`Primal min residual` occurs **0 times** and the success banner `Minimal residual` occurs **0 times**,
while the per-equation `initRes` block **does** print (`printInterval 10`). **On this case the
banner route reads nothing and the `initRes` route is the only one that reads anything.** A gate built
on the banner alone would silently measure nothing.

**The accept floor is the PRODUCT `primalMinResTol × primalMinResTolDiff`** (`N-D43`, confirmed at
source by `N-D44`), and **`primalMinResTolDiff` is not universally 1000 — and it is not even constant
inside A6.** Both values read first-hand from A6's own files:

| source | `primalMinResTol` | `primalMinResTolDiff` | accept floor |
|---|---|---|---|
| **D8R producer, script** — `/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/d8r_runScript.py:36` and **`:37`** (`1.0e-8`, `1.0e4`) | 1e-08 | **10000** | **1.0e-4** |
| **D8R producer, as it actually ran** — `O-P_20260827T223101Z_1595223.log:373` / **`:544`** (and `:374`/`:545` in `O-S`, `F-S`; `:373`/`:544` in `F-P`) | `1e-08` | **`10000`** | **1.0e-4** |
| **A6 archived tutorial at full size, as it actually ran** — `/home/ubuntu/certonomous-runs/A6-crm-wing/run_model_run1.log:348` / **`:519`** | `1e-08` | **`100`** | **1.0e-6** |

**runScript and log AGREE for the D8R producer** (`1.0e4` written, `10000` printed). **Two different
`primalMinResTolDiff` values live inside A6**, 10000 and 100, and neither may be carried from another
family or from the other half of this one.

> **G-PRIMAL, registered.** D8G inherits the **D8R producer's** values — `primalMinResTol 1e-08`,
> `primalMinResTolDiff 10000`, **accept floor 1.0e-4** — because D8G's producer is D8R's and a family
> whose acceptance rule changes between levels is not a family. Both values are **read back from each
> arm's own log at grade time and asserted equal to the registered pair; a mismatch is a grader
> REFUSAL (exit 2), not a soft note.** The measured max-initRes at `endTime` is **additionally
> reported against the 1.0e-6 tutorial floor, per level, as a diagnostic** — reported, never graded,
> so the looser registered floor cannot quietly become a claim about the tighter one.
>
> A level whose max-initRes at `endTime` exceeds **1.0e-4** → that level is **`NOT A RESULT`**, and
> per standing rule 5 **the whole triple is then `NOT A RESULT` whatever its value**.

**Iterative error, per `CASE_PROTOCOL_CHARTER.md` §5:** the iterative error in CD at each level must
be **at least ten times smaller** than the level-to-level difference in CD, computed from the last
10 % of the run's CD history. Not satisfied → the triple is `NOT A RESULT` (standing rule 5 clause 1:
"any level not iteratively converged or not plateaued").

**Completion, all-or-nothing** (`CLAUDE.md` rule 4, in this family's fields): `rc = 0`; an `End` line;
last time == `endTime`; the field set present; and **every field at `endTime` newer than the case's
own time-0 datum** (the age guard). A guard refuses a case where a time directory already exists
(cold-start proof; pyDAFoam writes the primal end state back into time 0, so a second run of a
directory silently warm-starts).

### 4.6 G-TRIPLE — Roache gating, on CD and on CL separately

`r = 2.000` exactly (from the measured integer cell ratios 8 and 8), `Fs = 1.25`.

Evaluated **in this order** (standing rule 5):

1. Any level not iteratively converged, not plateaued, or failing G-PRIMAL → **`NOT A RESULT`**.
2. Triple classified `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → **`NOT A RESULT`**, with the
   value, **both** triples and **both** observed orders printed beside it.
3. Triple `CONVERGING` → observed order `p = ln|(f_L1 − f_L2)/(f_L2 − f_L3)| / ln 2`.
   **`PASS` if `p` ∈ the pre-registered band [1.0, 3.0]; `GATE FAIL` outside it.** The band is
   centred on 2 because the registered `fvSchemes` are nominally second order, and is one order wide
   either side because the grid is a stretched hyperbolic O-grid with `s0` scaling across levels.
   **GCI at Fs = 1.25 is printed only when the three values are monotone**, and never otherwise.

**The gate can only turn a PASS or GATE FAIL INTO `NOT A RESULT`, never the reverse.**

**Registered now, so it cannot be chosen later:** the graded functionals are **CD** and **CL**, both
at the **fixed baseline design** (`twist = 0`, archived `aoa0`, no CL trim). Fixed-AoA rather than
fixed-CL, because a trim loop would inject its own iteration error into the triple. **CL is a graded
functional here, not a constraint.**

### 4.7 G-FD — the bright line, at L2, on both rows

> *"A DAFoam gradient is not a result until a finite-difference table stands beside it at a step
> proved to lie in the plateau, and a DAFoam verdict is two rows."* (`DAFOAM_CHARTER.md` §1)

* **Where.** At **L2 (44,544 cells)** — the finest level at which the adjoint is not `BLOCKED` (§7).
  **This is not "the finest level of the family", and the document says so rather than implying
  otherwise.**
* **What.** `compute_totals(of=["CD","CL"], wrt=["twist","patchV"])` at the baseline; central FD on the
  registered subset **`twist[0]`, `twist[1]`, `twist[3]`, `twist[4]`, `twist[5]`** (D8R's registered
  subset, cited not re-derived; `twist[6]` is `NOT A RESULT` **by name** from D8 §6 and is untouched)
  plus the **`CTRL` planted component** (§4.8).
* **The step, and the plateau proof.** Steps **{3e-2, 1e-1, 3e-1} degrees**, the middle step the
  reference. **The sweep is run at the primal tolerance the graded run uses** (`DAFOAM_CHARTER.md` §3:
  a sweep at a loose primal tolerance defends nothing — one lab cell moved from 25.9 % to 0.032 % on
  tolerance alone, with the step untouched). **The plateau is read PER COMPONENT, not off the
  vector**: a component is *on plateau* only if its FD estimate varies by ≤ **10 %** across the three
  steps. **A component that does not stabilise anywhere in the sweep is FLAGGED and EXCLUDED BY NAME
  from any aggregate quoted as agreement — never dropped silently and never rescued by a step at
  which it happens to cross.** ≥ 3 graded components or the row is `NOT A RESULT`. The sweep table
  reports **every** step as a row, including the failed ones, in the shape
  `| step | rel err | rel err (excl. flagged) | cosine | status |`.
* **The statistic is named** (`DAFOAM_CHARTER.md` §2): the aggregate is the **vector-relative error
  `‖J_an − J_fd‖ / ‖J_fd‖` as printed**. It is **not** a per-component average and is **never**
  compared against the published per-component averages of the DAFoam/ADflow method papers.
* **The band.** **`PASS` at ≤ 5 % aggregate with zero flagged components; `CONDITIONAL` at 5–15 % and
  then only with a per-component breakdown printed; `FAIL` above 15 % OR on ANY sign-flipped
  component regardless of the aggregate.**
* **§4 TRIVIAL BASELINE, registered before its own run** (`DAFOAM_CHARTER.md` §4): the same probe at
  **1e-3 degrees**, two orders below the registered step and below the bottom of D8's measured
  plateau. **Predicted to give > 15 %.** **If the deliberately-wrong step ALSO passes, the gate is not
  measuring what it claims and the FD verdict it produced is WITHDRAWN.**
* **Not reached for, and stated so** (`DAFOAM_CHARTER.md` §2, second half): a **forward-AD** reference
  is available in both images (`libDASolverADF.so`) and would be a stronger reference than finite
  differences. **D8G does not reach for it**, because no harness for it exists in this tree and
  building one is not what this item buys. **Recorded as a stated omission, not left silent.**

### 4.8 G-PLANT — the planted-zero controls, concretely (standing rule 3)

**Every reader that can return a zero or a pass plants a known perturbation, reads it back from disk,
and REFUSES if it cannot see it.** Three plants, each with its refusal:

1. **The functional reader.** Before grading, the harness copies the level's functional artefact,
   overwrites the CD field with **`CD_PLANT = 1.234e-03`**, and runs the *same* reader on the copy.
   The reader must return `1.234e-03` to within 1e-12. **If it returns the unplanted value, a zero, or
   nothing → exit 2, no verdict is written, the item is `BLOCKED`** (not `GATE FAIL`: nothing was
   measured).
2. **The residual reader, WITH ITS DISCRIMINATING ANTI-PLANT.** This is the reader `N-D44` says is
   easy to get structurally wrong, so the control is built to catch exactly that error.
   * *Must-see plant:* a copy of the log carries a synthetic final outer-iteration block with
     **`nuTilda initRes: 9.876e-03`** (all other equations small). The reader must return
     `9.876e-03`.
   * *Must-NOT-see anti-plant:* a second copy carries **`nuTilda finalRes: 9.876e-03`** with every
     `initRes` left small. **The reader must NOT return `9.876e-03`.** A reader that returns it is
     reading `finalRes` and is structurally blind — **exit 2, item `BLOCKED`.**
   * A reader that passes the must-see plant but fails the anti-plant is the precise failure this
     control exists for, and a reader shown able to see a non-zero on the wrong field is not shown
     able to see the right one.
3. **The FD reader.** A `CTRL` component is carried in the FD design-variable list whose analytic
   derivative is a harness-injected known constant. The grader asserts the reader recovers it to
   1e-9. Miss → exit 2, `BLOCKED`. (Same shape as D8R's `grader_controls/F_P_planted.json` /
   `F_S_planted.json`.)

**The grader carries a selftest that plants every violation shape and asserts each is caught, run
under both `python3` and `python3 -O`, with `ast.Assert` count 0 in the grader** (D8R's shape). The
counter is itself shown to count a planted one.

### 4.9 Verdict composition

* **Level** = `NOT A RESULT` if G-PRIMAL, G-TE or the dimensionality clause of G-MESH fails; else
  `GATE FAIL` if G-MESH-STRICT, G-BODY or G-SYS fails; else `PASS`.
* **Row** = `NOT A RESULT` if any level is, or if G-TRIPLE is; else `GATE FAIL` if G-TRIPLE or G-FD
  is; else `PASS`.
* **Item** = `NOT A RESULT` if either row is; else `GATE FAIL` if either row is; else `PASS`.
* **A `BLOCKED` from any G-PLANT refusal overrides everything and no verdict is written.**
* The **PATCHED** row is the result-bearing row for the capability cell; **a SHIPPED `GATE FAIL`
  still makes the item `GATE FAIL`**, and both sentences appear (D8R/D15/D16 shape). **A patched row
  never replaces a shipped row** (`DAFOAM_CHARTER.md` §6; R11 is Sanaa's call, not a session's).

---

## 5. MEMORY ENVELOPE, PREDICTED BEFORE LAUNCH (`DAFOAM_CHARTER.md` §7)

| arm | model | predicted peak | container cap | pre-launch headroom required |
|---|---|---|---|---|
| L1 primal (5,568) | D8R fd-arm 0.658 GiB at 41,760, linear in cells | **≈ 0.09 GiB** | 6 GiB | `MemAvailable` ≥ 8 GiB |
| L2 primal (44,544) | same | **≈ 0.70 GiB** | 6 GiB | ≥ 8 GiB |
| L3 primal (356,352) | same, ×8.535 | **≈ 5.62 GiB** | 12 GiB | ≥ 14 GiB |
| **L2 adjoint + FD** | A6 model **M2** (affine): 2,048 MiB + 0.16400 MiB/cell → 2,048 + 7,305 = 9,353 MiB = **9.13 GiB**; corrected by M2's measured **1.147×** underprediction against D8R's 9.970 GiB at 41,760 → | **≈ 10.5 GiB** | 14 GiB | ≥ 16 GiB |
| **L3 adjoint** | M2 → 2,048 + 58,442 = 60,490 MiB = **59.1 GiB**; de-biased by the model's measured 1.27× overprediction → **46.5 GiB** | — | — | **NOT ATTEMPTED — see §7** |

**RSS monitoring is record-only and never kills anything.** A sample above the cap is recorded as
over budget and no further arm launches; the running arm meets its own container `--memory`.
**A run that stops because the host ran out of memory is recorded as stopped by memory and is
`NOT A RESULT` about convergence, never a statement about the envelope.**

---

## 6. COST — ARITHMETIC SHOWN (`CLAUDE.md` rule 12; `DAFOAM_CHARTER.md` §12)

**Basis:** cores × wall for the whole clock (this lane's standing convention — a `docker run` holds
its cpuset whether the solver saturates it or not). Unit **core-minutes**. Rate **$0.0513/core-hour**,
owner-stated. **The box cannot read its own billing, so every dollar figure below is DERIVED, not
measured** (`COMPUTE_BUDGET_CHARTER.md` §5).

### 6.1 Measured anchors, each with its artefact

| # | anchor | value | artefact |
|---|---|---|---|
| A1 | D8R total, four arms, 41,760 cells, 4 ranks | **876.867 core-min** | `CURRICULUM-D8R-a6-twist-opt-conv/ledger.txt` |
| A2 | D8R per arm | O-P 4,753 s → **316.867**; O-S 6,442 s → **429.467**; F-P 954 s → **63.600**; F-S 1,004 s → **66.933** core-min | same |
| A3 | D8 components, np = 1, 41,760 cells | container+import+mesh **231 s**; cold primal **61–85 s**; warm primal **78.50 s**; one flow adjoint **≈ 410 s**; one-off colouring **≈ 591 s** | `curriculum_D8R/PREREGISTRATION.md` §0, §4, citing `curriculum_D8/LANE_REPORT.md` §8 |
| A4 | A6 full-size primal, 579,072 cells, np = 4, `endTime 1000` | `ExecutionTime = 403.99 s` → 1,615.96 core-s = **26.933 core-min** | `A6-crm-wing/run_model_run1.log` |
| A5 | D8R calibration | predicted 1,038 / actual 876.867 → **ratio 0.8447** (this family **under-runs by ≈ 15 %**) | `docs/COST_CALIBRATION.md` (D8R row) |
| A6 | L3 mesh generation, measured by this lane 2026-09-10 | 125.47 wall s at 2 cores = **4.183 core-min** | §9.4 probe |

### 6.2 The primal rate, and the exponent is justified

Two independent per-cell rates for a 1,000-iteration primal:

* from **A4**: `1,615.96 core-s ÷ 579,072 cells = 2.7906e-3 core-s/cell`
* from **A3**: `78.50 core-s ÷ 41,760 cells = 1.8798e-3 core-s/cell`

**The exponent on cells is 1, not 3/2 or 2, and this is the justification, not an assumption.**
SIMPLE-family segregated solvers with a fixed outer-iteration count cost `O(cells)` per outer
iteration; the two anchors span a **13.9× range in cell count** and their per-cell rates differ by
only **1.48×**, in the direction cache behaviour predicts (the larger mesh is *less* efficient per
cell). A super-linear exponent would have produced a 3.7× (at 1.5) or 13.9× (at 2) spread between
them and did not. **The conservative (larger) rate 2.7906e-3 is taken as the point estimate**; the
band is [1.88e-3, 2.79e-3].

**Fixed per-arm overhead:** A3's 231 s at np = 1; billed at 4 ranks → `231 × 4 ÷ 60 = 15.400
core-min` per arm.

### 6.3 The build-up

**Primal arms** — 3 levels × 2 rows, one cold primal to `endTime = 1000` each:

| level | cells | `cells × 2.7906e-3` core-s | core-min | + overhead 15.400 | per row |
|---|---|---|---|---|---|
| L1 | 5,568 | 15.54 | 0.259 | | 15.659 |
| L2 | 44,544 | 124.30 | 2.072 | | 17.472 |
| L3 | 356,352 | 994.42 | 16.574 | | 31.974 |
| | | | | **per-row sum** | **65.105** |

`65.105 × 2 rows = ` **130.210 core-min**

**Adjoint gradient at L2** — one `compute_totals` per row:
np = 1 components `231 + 73 + 591 + 820 = 1,715 core-s`; scaled to L2's cells `× 44,544/41,760 =
× 1.06667` → `1,829.3 core-s`; at np = 4 with **75 % parallel efficiency** (D7FR delivered 3.99 of 4
cores on the same solver and cell count; the assumption is stated as one because no np = 4 anchor
exists for A6 specifically): wall `= 1,829.3 ÷ (4 × 0.75) = 609.8 s`, billed `609.8 × 4 ÷ 60 =`
**40.652 core-min per row**.

`40.652 × 2 = ` **81.303 core-min**

**Endpoint-shape FD arms at L2** — D8R's measured F arms scaled by the same 1.06667:
`63.600 × 1.06667 = 67.840` (patched) and `66.933 × 1.06667 = 71.395` (shipped) → **139.235 core-min**

**Mesh generation** — L3 measured at **4.183**; L1 and L2 each completed in under 120 wall s at one
core → bounded at **2.000** each → **8.183**, registered at **9.000 core-min** with rounding.

| item | core-min |
|---|---|
| mesh generation, 3 levels | 9.000 |
| primal arms, 3 levels × 2 rows | 130.210 |
| adjoint gradient at L2 × 2 rows | 81.303 |
| FD arms at L2 × 2 rows | 139.235 |
| **POINT ESTIMATE** | **359.748 core-min** |

**Derived dollars:** `359.748 ÷ 60 = 5.9958 core-h × $0.0513 = ` **$0.3076 — DERIVED, NOT MEASURED.**

**Calibration prediction, separate from the cap** (`CLAUDE.md` rule 12): D8R's family under-ran at
ratio **0.8447**; if D8G behaves the same the actual lands at `359.748 × 0.8447 = ` **303.9
core-min**. Both figures go into the `docs/COST_CALIBRATION.md` row at completion, with the ratio
actual/predicted and the gap attributed (contention / waste / misprediction, waste named separately
and never absorbed into the ratio).

### 6.4 The cap, and what it is for

> **CAP: 1,079.25 core-min** (3 × the point estimate, per `CASE_PROTOCOL_CHARTER.md` §1).
> **Derived dollars at the cap: $0.9228 — DERIVED, NOT MEASURED.**
>
> **This cap is CALIBRATION, NOT A STOP.** Sanaa, 2026-09-10 ~16:50Z, byte-exact: *"and for all these
> 3D cases that still need to run, i dont want to see any budget gates ( time or money). Bc i want to
> shoot them so we at least have hard 3D demos to show and then we can go back to having some
> restraint"*. D8G is a 3D case inside that scope, so **the cap does not stop this run**;
> `CASE_PROTOCOL_CHARTER.md` §4's *"cap reached: stop, NOT A RESULT"* and `CLAUDE.md` rule 12's
> *"an overrun stops the run"* are suspended **for this item only**, and the item records that it ran
> under the exemption. **The estimate is still made, the actual is still measured, and the calibration
> row is still landed** — nothing in her directive withdraws rule 12's estimate-versus-actual duty.
>
> Every per-arm container still carries an explicit `--cpus`, `--memory` and `timeout` for
> *containment*, not for budget. **A `rc = 124` is an over-wall event, `NOT A RESULT` on that arm.**

**Under $25 either way**, so no §12 listing to Sanaa is triggered. **No GPU is used**; the GPU
cost-basis rule is not engaged.

---

## 7. THE GRADIENT DOES **NOT** CARRY A TRIPLE, AND THIS IS REGISTERED BEFORE THE RUN

**The adjoint is not attempted at L3.** Two independent grounds, both from A6's own record
(`ladder-a/A6/adjoint_feasibility/RESULTS.md`):

1. **Memory.** M2 (affine, 2,048 MiB fixed + 0.16400 MiB/cell) gives **59.1 GiB** at 356,352 cells;
   de-biased by the model's measured 1.27× overprediction, **46.5 GiB**. The box is 30 GiB with
   ≈ 27 GiB available.
2. **Conditioning, independently.** `DARhoSimpleCFoam` — the same solver — **stagnates at 79,560
   cells** with memory comfortable (11.65 of 22 GiB), `PetscConvergedReason: -3`. L3 is **4.48×**
   that size. **Naming only the memory blocker would be the L-15 error** (an adjoint bound by
   convergence, not by RAM, once drove a hardware recommendation in the wrong direction).

L2 at 44,544 cells sits **below** the 79,560-cell stagnation point and within the memory envelope, and
its near-neighbour at 41,760 has a measured converged adjoint. L1 at 5,568 likewise.

> **Consequence, stated plainly so it is not discovered afterwards: the adjoint is available at TWO of
> the three levels and blocked at the third. TWO LEVELS IS NOT A TRIPLE. D8G therefore grades a
> Roache triple on the FUNCTIONALS (CD, CL) ONLY, and the gradient carries a two-row FD table at L2
> and no order of accuracy at all.** A gradient triple is `BLOCKED` on this box for A6 and this item
> does not pretend otherwise.

---

## 8. PREDICTIONS, REGISTERED BEFORE THE RUN, AND THE ESCALATION LADDER

**Prediction-first means the likely failure is named here, not explained afterwards.**

* **P1 — construction.** All three levels generate; cell counts are exactly 5,568 / 44,544 / 356,352;
  three patches each with the registered face counts; `Mesh has 3 geometric (non-empty/wedge)
  directions (1 1 1)` on every occurrence; zero `empty` and zero `wedge` patches; plain `checkMesh`
  reads `Mesh OK.` and strict fails **exactly two** checks with the small-determinant fraction in
  [0.15, 0.28]. **This is a REPRODUCTION prediction** — this lane measured all of it in the
  pre-compute probe of §9.4 — and it is registered as a prediction so that a failure to reproduce it
  under the item's own launcher is visible as a defect rather than absorbed.
* **P2 — systematicity.** Cell ratios are the exact integers 8 and 8; the three surface coordinate
  arrays are pairwise distinct; patch face counts scale by exactly 4. **This is the check A3's family
  fails.**
* **P3 — THE MOST LIKELY WAY THIS ITEM DIES.** The CD triple is `CONVERGING` with `p` ∈ [1.0, 3.0] —
  **confidence: moderate only.** The named risk is **L1**: its discrete body differs (leading edge
  truncated 7.1e-3, §4.4) and its pyHyp `Grid Ratio` is **4.0000** against 1.5044 at L3, so L1 is not
  merely a coarser version of the same mesh but a coarser mesh with far steeper wall-normal
  stretching. **The predicted failure mode is a `STAGNANT` or `OSCILLATORY` triple driven by L1, which
  is `NOT A RESULT` whatever the CD value looks like.**
* **P4 — the FD table at L2, and a SPLIT is predicted.** The IDWarp `getRotationMatrix3d`
  degenerate-rotation defect (classes **D-A / D-A2**) has `axisMag = 1e-15 < tol = sqrt(eps)`, which
  **forces branch 0 at every non-corner surface node at the undeformed baseline** — and **D8G's FD is
  AT the baseline**, so the defect's first regime is guaranteed live, unlike an optimiser-endpoint FD.
  **Predicted: PATCHED row `PASS` ≤ 5 %; SHIPPED row `FAIL` above 15 % on one or more `twist`
  components.** **The counter-evidence is stated rather than suppressed:** D8R's SHIPPED row *passed*
  its endpoint FD table, so the shipped row is **not certain** to fail here; the difference between
  the two situations is baseline-versus-endpoint, and the baseline is the regime the defect must run.
  **Registered now so that whichever way it lands it cannot be spun afterwards.**
* **P5 — a free negative control on the two-row machinery.** The IDWarp rotation patch lives in the
  **reverse-mode mesh-warp derivative** and cannot enter a primal at a fixed baseline design.
  **Predicted: shipped and patched CD and CL agree to ≤ 1 η at every level.** A larger disagreement is
  a finding about the images, not about the grid, and is reported as one.
* **P6 — cost.** Actual lands at `0.8447 × 359.748 = 303.9` core-min ± the [1.88e-3, 2.79e-3] rate
  band.

### 8.1 The escalation ladder, fixed in advance (`CASE_PROTOCOL_CHARTER.md` §3, §4)

One change per attempt; never the same action twice on the same state.

1. **L1 causes a non-CONVERGING triple** → **first registered action:** rebuild L1 at `s0 = 1.0e-4`
   (unscaled, matching L3) with everything else held, and re-grade. Recorded with its basis.
2. **Second failure on the same cause** → **climb one rung:** the family **SHIFTS UP** to
   `c2/c1/c0 at N = 17/33/65` → **44,544 / 356,352 / 2,850,816** cells, r = 2 exactly, cell ratios
   8 and 8. The adjoint and FD **stay at 44,544**. **Registered UNKNOWNS for that successor, named
   now:** its L3 primal memory is not on record for this case at 2.85M cells (linear extrapolation
   from D8R's fd-arm rate gives ≈ 45 GiB — *over the box* — so the successor is **not obviously
   affordable and must be re-costed and re-enveloped before it is registered**, not adopted
   automatically).
3. **Third failure on the same cause** → **park as `NOT A RESULT`** with the cause class and the three
   actions tried, write the lesson, move on. **The item does not wait on Sanaa.**

A `GATE FAIL` on G-MESH-STRICT (a third or different failing check) is **not** on this ladder: it is a
finding about the mesh generator and is triaged as one.

---

## 9. SECONDARY — THE `shape` LOCAL FFD DESIGN VARIABLE (retained from the D8S line of enquiry)

This section is **not** part of D8G's gates, cost or verdict. It records what this lane established
about the A6 FFD before the deliverable moved, because the question survives the move.

### 9.1 The FFD supports a local `shape` DV, and the real count is **192**

**Read first-hand from the FFD file** at
`/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/base/FFD/wingFFD.xyz`
(md5 `905ade2c1120aee7e6517432cd8abbaf`, sha256
`367aafcf7bc9265803de1470e8049d834416c35b17b556bc9658164086166ba8`):

* plot3d, **1 block**, header dimensions **`12 8 2`** → **192 control points**;
* the file carries **576 numeric coordinate tokens** after the two header lines = 192 × 3. **Exactly
  consistent — the header is not a claim the body fails to back.**

The archived A6 `runScript.py` (byte-identical copy beside the D8R base) selects **all** of them:

```
pts = self.geometry.DVGeo.getLocalIndex(0)
indexList = pts[:, :, :].flatten()
PS = geo_utils.PointSelect("list", indexList)
nShapes = self.geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)
```

**And the default axis was read from the shipped image, not assumed** —
`pygeo/mphys/mphys_dvgeo.py:222` in
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`:

```
def nom_addLocalDV(self, dvName, axis="y", pointSelect=None, childIdx=None, isComposite=False):
```

**`axis="y"` is a single axis, so one DV per selected control point: `nShapes = 192`.**

> **The survey lane's `UNKNOWN` is resolved: the A6 wing-alone FFD DOES define local control points
> able to carry a `shape` DV, and the count is 192.** **It is NOT 32**, and any item costed on 32 is
> costed on a number six times too small.

Cross-check on the same FFD, independently: `nom_addRefAxis(..., alignIndex="j")` over the FFD's
`j = 8` gives `nRefAxPts = 8` and hence **7** `twist` DVs — and D8R's own optimiser table prints
`dvs.twist_0` … `dvs.twist_6`, exactly 7. **The FFD header is confirmed by a running artefact.**

### 9.2 D8R excluded `shape` deliberately, and named the successor

`d8r_runScript.py:157` adds `twist`; **`:159` carries the comment
`# D8 EDIT 3 (twist-only): the `shape` local FFD DV is NOT added.`**, and `:185` records
`# D8 EDIT 4: LE/TE constraints act on local shape DVs; none exist here.` D8R's own §7 registers
`shape` as excluded — *"`shape` is therefore NOT graded by this rung"* — on cost grounds
(*"of order 10² components and would cost 10× the registered ceiling"*, `rung_n16_np1` §3).
**A shape-DV item is the step D8R itself named, not a new family**, and it is now costable at
192 components rather than guessed.

### 9.3 What a shape item would have to face

The `shape` DV is **precisely the DV whose derivative runs the IDWarp degenerate-rotation branch**
(D-A/D-A2). A shape FD table at an undeformed baseline is the situation in which
`axisMag = 1e-15 < tol = sqrt(eps)` forces branch 0 at every non-corner surface node. **The likely
landing for such an item is a split two-row verdict — shipped `FAIL` above 15 % on shape components,
patched `PASS`** — and that is the shape of P4 above, one level of DV richer.

### 9.4 The pre-compute probe this lane ran, itemised

Disclosed under §1. **Zero solver compute.** Non-solver compute, host-measured:

| probe | what it did | cost |
|---|---|---|
| image inspection | `cgns_utils`, `pyhyp`, `checkMesh` presence in both images; `nom_addLocalDV` signature | < 1 core-min |
| CGNS coarsening chain | c0→c4, face counts, point counts, bounding boxes, TE geometry | ≈ 1 core-min |
| L1 mesh generation + both `checkMesh` runs | 5,568 cells | < 2 core-min |
| L2 mesh generation + both `checkMesh` runs | 44,544 cells | < 2 core-min |
| **L3 mesh generation + both `checkMesh` runs** | 356,352 cells | **4.183 core-min (measured, `/usr/bin/time`)** |
| strict `checkMesh` on a read-only copy of the D8R graded mesh | 41,760 cells | < 1 core-min |
| | **total** | **≈ 12 core-min** |

**No artefact of that probe is a handoff channel and none is cited by path in this document**
(`CLAUDE.md` rule 13, L-186). **The item regenerates every mesh under its own launcher, into its own
run root, and re-measures everything above.** The probe's outputs are predictions here, not results.

---

## 10. WHAT THIS ITEM CANNOT ESTABLISH — named UNKNOWN, not inferred

1. **Whether the CD triple converges at all.** Unmeasured; P3 names the likely failure.
2. **Whether L2's adjoint converges.** Its near-neighbour at 41,760 did, and 44,544 is below the
   79,560-cell stagnation point, **but no adjoint has ever been run on a 44,544-cell A6 mesh.**
3. **The gradient's order of accuracy.** `BLOCKED` — §7. Two levels is not a triple.
4. **Any validation claim.** No external reference for CD or CL is registered — §0.2.
5. **The primal RSS at L3.** Extrapolated linearly from D8R's fd-arm 0.658 GiB; **no A6 primal RSS at
   any size is on record**, so the ≈ 5.62 GiB figure is a model, not a measurement.
6. **Whether `autoPatch 45` yields the registered 3-patch topology under the item's own launcher.**
   It did in the probe at all three levels; it is nevertheless a G-MESH gate, because a feature-angle
   split is not guaranteed to be stable across regeneration.
7. **Whether the small-determinant cells affect the solution.** The strict-check finding of §4.2 is a
   statement about mesh geometry. **Whether it moves CD, and by how much, is NOT measured by this
   item and is not claimed either way.** It is a candidate lesson and a candidate docket row.
8. **Whether the pyHyp `Grid Ratio` disparity (4.0000 at L1 vs 1.5044 at L3) is benign.** Unmeasured.
   It is the mechanism P3 names and the reason the first escalation action is an `s0` change.

---

## 11. PROVENANCE

* Standing rules: `CLAUDE.md` (1 verdicts, 2 pre-registration, 3 planted zero, 4 completion,
  5 Roache, 7 parked, 12 compute, 13 scratchpad).
* Charters: `DAFOAM_CHARTER.md` §1–§7, §9, §10, §12; `VERIFICATION_CHARTER.md` §2b–§2d, §4, §7;
  `CASE_PROTOCOL_CHARTER.md` §1–§5, §8, §9 and its closing 3D budget clause;
  `COMPUTE_BUDGET_CHARTER.md` §4, §5, §6.
* Numerics: **`N-D43`** and its 2026-09-06 correction (the accept floor is the product; the
  multiplier is not universally 1000), **`N-D44`** and its evidence addendum (`Primal min residual`
  is a max over per-equation `initRes`; a `finalRes` comparator is structurally blind).
* Predecessor: `cases/dafoam/ladder-a/A6/curriculum_D8R/{PREREGISTRATION,RESULTS}.md`;
  `cases/dafoam/ladder-a/A6/rung_n16_np1/PREREGISTRATION.md`;
  `cases/dafoam/ladder-a/A6/adjoint_feasibility/RESULTS.md`.
* All measurements in §2, §3, §4.2, §4.4, §4.5 and §9.1 were read first-hand by the drafting lane on
  2026-09-10 from the artefacts named beside them.

**END OF DRAFT — NOT FROZEN.**

---

## AMENDMENT 1 — 2026-09-11 — **PRE-COMPUTE. The iterative-error rule names no statistic, no source, no minimum sample count, and only one of the two graded functionals. And the graded residual threshold equals the solver's own acceptance product.**

*lines whose number changed above this section: 0.* Appended; nothing above is rewritten or struck.

**Written and registered by the dafoam-supervisor** (§3 check-4, read personally). **Pre-compute**, and
therefore legal to add a gate (`CLAUDE.md` rule 2).

### CONDITION, AND HOW IT WAS CHECKED

**No compute of any kind has been spent against this registration.** Checked 2026-09-11: the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple` **does not exist**, and no `*D8G*` or
`*d8g*` directory exists anywhere under `/home/ubuntu` except the case directory itself. **None of the
three registered volume meshes exists.** (§9.4's pre-compute feasibility probe is separately itemised
and priced in §9 and retained no artefact, per rule 13.)

### (a) `G-PLAT` — the iterative-error rule, COMPLETED. Four things it left unnamed.

The rule as drafted (§4.5) reads: *"the iterative error in CD at each level must be at least ten times
smaller than the level-to-level difference in CD, computed from the last 10 % of the run's CD history."*
**That is the right rule and it is the charter's own (`CASE_PROTOCOL_CHARTER.md` §5). Four things in it
are not decidable as written**, and a grader that must guess is not a pinned grader:

**1. THE STATISTIC IS NOT NAMED.** *"The iterative error in CD"* could be a peak-to-peak excursion, a
standard deviation, or an adjacent-sample delta, and they differ by orders of magnitude on a drifting
signal. **Registered: the PEAK-TO-PEAK excursion `max − min` over the window.** **An adjacent-sample
delta is REFUSED BY NAME.** An adjacent difference is an *increment*, not an *excursion*: a signal
drifting steadily in one direction has a small increment at every step and never plateaus at all.
**This is the defect the cfd team's DrivAer Gate A1 plateau limb carried and that this lab caught on
2026-09-10** — an adjacent-iteration delta passing by 120× while the signal's own excursion over 500
iterations was 8.35 %. It is not repeated here.

**2. THE SOURCE OF THE HISTORY IS NOT NAMED — and on this case it is not the obvious one.** Registered:
the **solver's own log**, the `CD:` and `CL:` lines emitted by `calcAllFunctions` at `printInterval`.
**Measured first-hand by this supervisor on the D8R producer's own arm**
(`/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/F-P_20260827T235119Z_1656338.log`):
`printInterval 10` at `:542`, giving **3,232 `CD:` lines and 3,232 `CL:` lines against 3,233 `Time = `
lines** — one functional sample per printed step, cadence 10. This is the same shape of finding as §4.5's
own `Primal min residual` result: **the obvious artifact does not exist on this case and a reader built
on it would silently measure nothing.**

**3. NO MINIMUM SAMPLE COUNT.** *"The last 10 %"* is a fraction, and a fraction of a short or
early-stopping history can be two samples. **Registered: the window is the last 10 % of printed samples
OR the last 10 samples, WHICHEVER IS LARGER, and a window holding fewer than 10 samples makes that level
`NOT A RESULT` for want of evidence.** A window that cannot exhibit an excursion cannot prove a plateau,
and a level that printed too rarely to be judged is not thereby judged converged. (At `printInterval 10`
on the D8R arm the 10 % window is ~323 samples, so this clause binds only a degenerate run — which is
exactly when it is needed.)

**4. IT COVERS CD ONLY, WHILE §4.6 GRADES CD *AND* CL.** §4.6 registers, verbatim, *"the graded
functionals are **CD** and **CL**"* and *"CL is a graded functional here, not a constraint."* A plateau
rule that reads only CD leaves the second graded row ungated. **Registered: `G-PLAT` applies
independently to CD and to CL, and a failure on either makes that level `NOT A RESULT`** — and by
standing rule 5 clause 1 the whole triple with it.

### (b) THE GRADED RESIDUAL THRESHOLD EQUALS THE SOLVER'S OWN ACCEPTANCE PRODUCT — disclosed

`G-PRIMAL` registers `primalMinResTol 1e-08` × `primalMinResTolDiff 10000` → **accept floor 1.0e-4**,
and then grades: *"A level whose max-initRes at `endTime` exceeds **1.0e-4** → that level is `NOT A
RESULT`."* **Same residual family, same number.** DAFoam's `checkPrimalFailure()` tests
`primalMaxRes / primalMinResTol_ > primalMinResTolDiff` (`N-D44`), so a primal handed back without an
`AnalysisError` has already satisfied approximately what the gate asks. Under
`CASE_PROTOCOL_CHARTER.md` §1 — *"a tolerance equal to a gate voids the rung"* — this is the
configuration the charter forbids. **The identical coincidence was found the same day in `A3GC`
(accept floor 1e-06, gate 1e-06) and was recorded against the D6 family on 2026-09-10. It is a
FAMILY-WIDE pattern in this territory, not a slip in one document.**

**What is registered:**

1. **`G-PRIMAL`'s residual threshold is RETAINED as a completion PRECONDITION and is explicitly NOT a
   discriminating gate.** It is never quoted, alone, as evidence that a level converged.
2. **The discriminating limb of standing rule 5 clause 1 on this item is `G-PLAT` above** — it reads the
   *functional's own history* against a threshold *derived from the family* (the level-to-level
   difference), which the solver's acceptance test knows nothing about and cannot pre-satisfy.
3. **The already-registered 1.0e-6 tutorial-floor diagnostic is RETAINED** — reported per level, never
   graded. It is what makes the coincidence visible in the record instead of inferred later.

**The registered tolerances are NOT changed.** `primalMinResTol 1e-08` and `primalMinResTolDiff 10000`
stand: they are the D8R producer's own values, read back per arm and asserted at grade time, and *"a
family whose acceptance rule changes between levels is not a family."* The repair is not a different
number on the same quantity — it is a gate that reads a different quantity, which is (a).

### (c) WHY THIS DOCUMENT IS STILL NOT FROZEN, STATED PLAINLY

**Its grading path does not exist.** `CLAUDE.md` rule 2: *"The grading path is fixed at the
pre-registration commit; verify the frozen file **is** the file that ran by hashing it against the
committed blob."* This directory holds `PREREGISTRATION.md` and two `.DRAFT` shell files. There is **no
comparator, no chain driver, no `of.py`, no `decomposeParDict`, and no mesh generator** — against the
D8R producer's shipped set of eleven instruments including `d8r_grade.py` (49,371 B) with its deltas
diff and selftest evidence. **A registration whose comparator does not exist cannot be frozen, because
there is nothing to pin.** The freeze is blocked on building that path, and the launcher's five
`__D8G_UNFROZEN__` tokens and the unmeasured witness budget are smaller items behind it.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**COMPLETES** the iterative-error rule into `G-PLAT` (statistic, source, minimum window, both graded
functionals) and **DISCLOSES** the threshold coincidence. **ALTERS NO** gate band, cap, tolerance,
cost or label registered above: §4.6's Roache order and `p` band, §4.7's FD bands and trivial-baseline
control, §6.3's 359.748 core-min estimate and 1,079.25 cap, and §7's two-level adjoint ceiling are
untouched. **The FD table at L2 remains owed and remains the bright line** (`DAFOAM_CHARTER.md` §1).
**SUBMISSIONS PARKED.**
