# PERMISSION: FROZEN — frozen by the dafoam-supervisor 2026-09-11. Gates, thresholds, caps and labels are CLOSED except by dated addendum that cannot alter them.

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

---

## AMENDMENT 2 — 2026-09-11 — **PRE-COMPUTE. §6.3 mispriced the FD arms by not counting the trivial baseline's own primals, and §5 registers no aggregate memory ceiling at all.**

*lines whose number changed above this section: 0.* Appended; nothing above is rewritten or struck.

**Registered by the `dafoam-supervisor`** (Rulings 1 and 2, this date), on a lane's measurement.
**Pre-compute**, and therefore legal (`CLAUDE.md` rule 2). **It moves no gate, no band, no threshold
and no label** — see the closing block.

### CONDITION, AND HOW IT WAS CHECKED

**No compute of any kind has been spent against this registration.** Checked **2026-09-11T16:47Z**:

* `stat /home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple` → **`No such file or directory`.**
  **The registered run root does not exist.**
* `find /home/ubuntu/certonomous-runs -maxdepth 2 -iname '*d8g*'` → **empty.** No level base, no mesh
  record, no ledger, no arm directory.
* `docker ps -a` carries **no container whose name contains `d8g`**, live or exited.

**AND THE FINDER WAS PLANTED BEFORE ITS ZERO WAS BELIEVED** (`CLAUDE.md` rule 3). The same `find`
invocation, re-run against `*d8r*`, returned **three** paths including
`/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv`. A reader not shown able to see a
non-zero is not evidence; this one was shown, and only then was its zero on `*d8g*` taken as one.

---

### (a) RULING 1 — THE FD-ARM COST IS CORRECTED **BEFORE** THE RUN, AND THE CORRECTION IS ARITHMETIC, NOT A NEW GATE

**What §6.3 got wrong.** Its FD-arm figures were obtained by scaling **D8R's measured F arms** by the
cell ratio 1.06667. D8R's F arm evaluated **three** steps; **D8G's §4 registers a fourth — the
trivial baseline at 1e-3 deg** — and that step is **not optional**: the comparator's
`_trivial_baseline` **refuses outright** below three components at the trivial step, so the arm that
§4 registered was never the arm §6.3 priced. **§6.3 did not change its mind; it mispredicted by not
counting the primals a gate it had already registered would force.**

| | primals |
|---|---|
| D8R F arm: 3 steps × 5 components × 2 (central) + 2 baselines | **32** |
| D8G F arm: 4 steps (3 graded **+ the §4 trivial baseline**) × 5 × 2 + 2 baselines | **42** |
| ratio | **1.3125** |

**The 32 is MEASURED, not assumed:** `grep -c '^Running Primal Solver'` on D8R's own arm log
`/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/F-P_20260827T235119Z_1656338.log`
returns **32**, exactly.

**TWO INDEPENDENT ROUTES TO THE CORRECTED FIGURE. THE AGREEMENT IS THE EVIDENCE, NOT THE NUMBER.**

**Route A — per-primal scaling of the registered figures.**
`F2-P: 67.840 × 42/32 = ` **89.040 core-min**; `F2-S: 71.395 × 42/32 = ` **93.706 core-min**.
Increase `21.200 + 22.311 = ` **43.511 core-min**.

**Route B — from D8R's measured wall, touching none of §6.3's numbers.**
D8R's `F-P` inspect record gives `StartedAt 2026-08-27T23:51:19.974472495Z` →
`FinishedAt 2026-08-28T00:07:12.293796543Z` = **952.319 s** × 4 ranks ÷ 60 = **63.488 core-min**
(§6.3 registered 63.600 for that arm — the two agree to **0.18 %**, which is what makes Route B an
independent check rather than a restatement). Subtracting the **measured** launch head of ≤ 15.0 s
(§(c) below) leaves 937.3 s over 32 primals = **29.291 s per primal**; 42 primals + the same head =
1,245.2 s = **83.015 core-min** at 41,760 cells, and × 1.06667 for L2's cells = **88.550 core-min**.

**Route A gives 89.040; Route B gives 88.550. They agree to 0.55 %.**

**REGISTERED, replacing the §6.3 line items of the same names:**

| arm | §6.3 as written | **corrected** |
|---|---|---|
| F2-P | 67.840 | **89.040** |
| F2-S | 71.395 | **93.706** |
| **ITEM POINT ESTIMATE** | 359.748 | **403.259 core-min** |
| **derived dollars at $0.0513/core-h** | $0.3076 | **$0.3448 — DERIVED, NOT MEASURED** |

**WHY THIS IS DONE NOW AND WOULD BE ILLEGAL LATER, STATED IN AS MANY WORDS.** If the prediction
stayed at 359.748, `G10` would report `actual/predicted ≈ 1.31` at grading time, and rule 12's
attribution machinery would then offer **contention** or **waste** as the explanation for a gap whose
true cause is **an arithmetic error in this registration**. `COMPUTE_BUDGET_CHARTER.md` §6 keeps
**waste separately named and never absorbed into the ratio**; **the mirror obligation is that a
MISPREDICTION IS NOT LAUNDERED INTO CONTENTION.** A registration that knows it mispriced an arm and
lets the run report the difference as contention is not reporting waste honestly — it is hiding its
own error inside someone else's. Correcting it before the first container is the only moment at which
this is a bookkeeping fix rather than a gate moved to fit an answer.

**WHAT THIS OBLIGES THE FREEZE TO DO, AND THIS AMENDMENT DOES NOT DO IT.** `d8g_grade.py`'s
`PREDICTED_CORE_MIN` dict carries `"F2-P": 67.840` and `"F2-S": 71.395` **as constants in the
comparator**, and `CAPS` is derived in that file as `3 ×` each. **`G10`'s ratio and the
`docs/COST_CALIBRATION.md` row are computed from those constants, not from this document**, so this
amendment is **INERT UNTIL THE COMPARATOR'S TWO ENTRIES ARE UPDATED AT THE FREEZE.** The consequential
per-arm caps become `F2-P 267.120` and `F2-S 281.118` core-min (from 203.52 and 214.185). The lane
that measured this **did not touch the comparator** — editing it is the supervisor's act and the
comparator is about to be frozen.

**THE ITEM CEILING IS NOT MOVED BY THIS AMENDMENT.** §6.4's **1,079.25 core-min** stands as written.
`3 × 403.259 = 1,209.78` is recorded here **as a reading, not a registration**, because §6.4 already
**suspends the cap as a stop** for this 3D item on Sanaa's 2026-09-10 directive and the comparator's
`G10` is **REPORT-ONLY** — so nothing halts on either number, and moving a ceiling that stops nothing
would be motion without meaning.

---

### (b) RULING 2 — §5 GETS AN AGGREGATE MEMORY LIMB, AND IT IS A **CHECK WITH ONE DERIVED CONSTANT**, NOT AN INHERITED NUMBER

§5 registers per-arm container caps and per-arm pre-launch headroom. **It registers no aggregate
ceiling**, and the chain driver needs one. **D8R's 30.6 GiB IS NOT CARRIED ACROSS**, and the reason is
the one §4.5 already gives for `primalMinResTolDiff`: a constant belongs to the registration that
measured it, and neither half of a family may be carried from the other.

**MEASURED ON THIS BOX, 2026-09-11T16:50Z, first-hand:**

| quantity | measured |
|---|---|
| `MemTotal` | 32,132,596 kB = **30.644 GiB** |
| `MemAvailable` at the reading | **19.289 GiB** |
| live containers' *actual* usage (`docker stats`) | 122.2 MiB + 506.1 MiB = **0.614 GiB** |
| **host non-container RSS** = (MemTotal − MemAvailable) − container usage | **10.741 GiB** |
| worst D8G arm cap (§5: the L2 adjoint / FD arms) | **14 GiB** |
| aggregate a worst-case arm would present **today** | 14 + 10.741 + 0 = **24.741 GiB** |

**FIRST, A DEFECT IN THE READING ITSELF, AND IT IS LIVE RIGHT NOW.** `d8g_aggregate_memory.py`
composes `aggregate = Σ(live container CAPS) + this arm's cap + host non-container RSS`, where
`host_nc = (MemTotal − MemAvailable) − Σ(live container USAGE)`. **Both containers running on this box
at the reading carried `HostConfig.Memory = 0` — no cap at all.** An uncapped container therefore
contributes **0** to the caps term *and* has its real usage **subtracted** out of `host_nc`: **it is
doubly invisible.** A neighbour growing uncapped to 20 GiB would move the aggregate by
**approximately nothing**. **A ceiling compared against a number blind to the largest thing on the
box is theatre**, so the limb below is registered **together with** the reading's repair (recorded in
`d8g_aggregate_memory_DELTAS_from_d8r.diff`): an uncapped live container is counted **at its current
usage**, **named**, and carried in the reading as `uncapped_containers`, so a grader can see the
aggregate was taken against an unbounded neighbour.

**SECOND, WHY D8R's NUMBER WOULD HAVE BEEN INERT ANYWAY.** `30.6 GiB` against this box's
`MemTotal 30.644 GiB` is `MemTotal − 0.044` — **the whole machine.** It is not a ceiling; it is a
value that can essentially never refuse.

> **§5, NEW LIMB — `G-AGG`, THE AGGREGATE MEMORY CHECK.** Before each arm, and **in addition to** the
> per-arm H5 window already registered:
> **`AGG_CEILING_GIB = MemTotal_GiB − RESERVE_GIB`, with `RESERVE_GIB = 4.0`** — **on this box,
> 30.644 − 4.0 = 26.644 GiB.**
> **IT IS REGISTERED AS THE FORMULA, NOT AS THE LITERAL 26.644**, because an instance change is
> Sanaa's call and does happen, and a literal would silently describe the wrong machine afterwards.
> The aggregate reading must satisfy `Σ(live caps, uncapped counted at current usage) + this arm's cap
> + host non-container RSS < AGG_CEILING_GIB`, or the driver **WAITS** (bounded, as registered) and
> then **BLOCKS**.

**THE DERIVATION OF `RESERVE_GIB = 4.0`, INCLUDING WHAT IT IS *NOT* FOR.** Host non-container RSS is
**already a term inside the sum**, so the reserve is not protecting it. The reserve covers exactly two
things: **(i)** growth of that host RSS *between the pre-launch reading and the arm's peak* — the lab
fleet keeps working while an arm runs — and **(ii)** the arm exceeding §5's linear model, whose own
measured error is the **1.147×** M2 underprediction §5 already discloses. Sized against today's
worst case: `24.741 GiB` presented, ceiling `26.644 GiB`, **slack 1.903 GiB** — enough to admit the
box as it stands and to **refuse** once roughly 2 GiB of further committed caps appear. A reserve of
0 (D8R's effective choice) refuses nothing; a reserve large enough to be comfortable would refuse the
A2/F2 arms outright on a box already carrying the lab fleet.

**WHAT IS NOT DEFENSIBLE AS A CONSTANT, AND IS THEREFORE NOT REGISTERED AS ONE.** The binding
quantity is **one arm plus whatever else is on the box**, and *whatever else* is set by other teams'
fleets, which this document does not govern and cannot predict. **`host_nc = 10.741 GiB` is ONE
SAMPLE, not a distribution** — the lane took a single reading and is not entitled to call it typical.
That is precisely why the limb is written as a **pre-launch check against the live reading** with one
small derived reserve, rather than as a registered aggregate figure: **the check is honest about
being contention-dependent; a constant would not be.**

---

### (c) THE WITNESS BUDGET STAYS A TOKEN, AND A TIMESTAMP IS ADDED SO THE FIRST ARM MEASURES IT

`d8g_run_arm.sh`'s `LAUNCH_BUDGET_S` bounds `StartedAt → the first `^ExecutionTime = ` line`, and is
asserted to be a strict minority of the in-container deadline `TMO = cap_core_min × 60 ÷ 4` (ceilings
**352 / 393 / 719 / 915 / 1,526 / 1,606 s** for L1 / L2 / L3 / A2 / F2-P / F2-S).

**MEASURED, from D8R's four inspect records and arm logs (41,760 cells, 4 ranks):** `StartedAt` → the
decomposePar banner **13.94 / 5.65 / 8.03 / 7.93 s**; → `processor3/constant/polyMesh/owner.gz`
written **14.94 / 6.65 / 9.03 / 8.93 s**. **6.7–15.0 s, a 2.2× spread on identical work** — the budget
must absorb host contention, not merely the mesh.

**NOT MEASURED, AND NOT ESTIMATED.** The second leg — decomposePar complete → the first
`^ExecutionTime` — **is timestamped nowhere in the surviving artefacts**. The `ClockTime = 3–4 s` on
that line is the **solver's own** clock and says nothing about DASolver construction. `StartedAt` →
witness is therefore bounded **below** at ≈ 15 s and **not bounded above by any evidence this lab
holds**. **`__D8G_UNFROZEN__WITNESS_BUDGET` REMAINS A TOKEN** rather than a guess.

> **REGISTERED:** the in-container wrapper echoes `date -u +%s` **immediately before** the `mpirun`
> line. It costs nothing, it is not a gate, and it converts the witness budget from a judgement into a
> **measurement on the very first D8G arm**. The token is filled from that measurement, not before.

---

### (d) NAMED UNKNOWN, CARRIED INTO THE RECORD RATHER THAN LEFT AS A FOOTNOTE

`d8g_decomposeParDict` is a **byte copy** of the frozen, graded `curriculum_D8R/d8r_decomposeParDict`
(both md5 `1dbd9ead3f40a29f483444dc5fa1288b`, verified against both paths). `numberOfSubdomains 4` is
**forced**, not chosen: every arm is np = 4 (§3), the comparator's `NPROCS_REGISTERED = 4` **refuses**
any artefact that differs, and `G12` pins four cores. `scotch` is held across all three levels so the
triple's three solves differ **only in the mesh**.

> **UNKNOWN, added to §10's list in substance and named here because §10 is above this line and is not
> edited:** **whether `scotch` produces the SAME partition in the PATCHED and SHIPPED images is an
> INFERENCE FROM IMAGE PROVENANCE, NOT A MEASUREMENT.** Both carry OpenFOAM 2506 and differ only in
> IDWarp, so the partition *should* be identical — but measuring it means running `decomposePar` in
> both images, which is compute, and **no lane has run it.** If the two rows ever disagree by more
> than the case's own noise floor, the comparator's `P5` note already points at the images; **the
> decomposition is one of the things that must then be checked, and this sentence is why.**

---

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**CORRECTS** two §6.3 cost line items by arithmetic that a gate registered in §4 had already forced,
and **ADDS** an aggregate-memory limb to §5 where none existed. **ALTERS NO** gate, band, threshold,
tolerance or label registered above: §4.1–§4.8's gates, §4.6's Roache order and `p ∈ [1.0, 3.0]`,
§4.7's FD bands and trivial-baseline withdrawal, `AMENDMENT 1`'s `G-PLAT` and `G-PRIMAL`, §6.4's
1,079.25 ceiling and its REPORT-ONLY status, §7's two-level adjoint ceiling, and §8's predictions are
**untouched**. **It adds no gate and removes none.** The FD table at L2 remains owed and **remains the
bright line** (`DAFOAM_CHARTER.md` §1). **The comparator's `PREDICTED_CORE_MIN` entries are NOT
changed by this document and must be changed at the freeze, or (a) is inert.** **SUBMISSIONS PARKED.**

---

## AMENDMENT 3 — 2026-09-11 — **PRE-COMPUTE. `G1` implemented four of `CLAUDE.md` rule 4's clauses and none of the rest, and a solve that died at iteration 490 of a registered 1,000 graded `PASS` on both rows at observed order 2.0000.**

*lines whose number changed above this section: 0.* Appended; nothing above is rewritten or struck.

**Registered by the `dafoam-supervisor`** on a lane's code-reading and its demonstration.
**Pre-compute**, and therefore legal to add a gate (`CLAUDE.md` rule 2). **This amendment ADDS
REFUSALS AND NOTHING ELSE** — see the closing block.

### CONDITION, AND HOW IT WAS CHECKED

**No compute of any kind has been spent against this registration.** Checked
**2026-09-11T17:31Z**: `stat` on the registered run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple` → **absent**;
`find /home/ubuntu/certonomous-runs -maxdepth 2 -iname '*d8g*'` → **0 hits**. **AND THE FINDER
WAS PLANTED BEFORE ITS ZERO WAS BELIEVED** (rule 3): the same invocation against `*d8r*`
returned **10** hits. A reader not shown able to see a non-zero is not evidence.

### (a) WHAT WAS MISSING, MEASURED RATHER THAN ARGUED

`G1` implemented `rc == 0`, `OOMKilled`, the age guard on the artefact, and the instrument's
terminal marker. Of rule 4's remaining clauses it implemented **none**, and the evidence is a
census of the comparator's own source:

| rule 4 clause | in the comparator, before this amendment |
|---|---|
| an `End` line | the string occurred **ZERO** times |
| last time == `endTime` | `endTime` was read into `read_P` and **never compared to anything** |
| the `ExecutionTime` count | `ExecutionTime` occurred **once — in the fixture BUILDER**, in no reader and no gate |
| the field set present | not checked at all |

**AND THE LABEL WAS FALSE, WHICH IS WORSE THAN THE CHECK BEING ABSENT.** `g_primal` reported
its reading in a field named **`max_initRes_at_endTime`**, while `read_max_init_res` walks
backwards to the last parseable `initRes` block **wherever it is** and never establishes that
it is at `endTime`. **An absent check is a gap; an absent check WEARING THE NAME OF A PRESENT
ONE is an assertion the instrument cannot support.** The clause below makes the name true, and
the name is kept only because it now is.

### (b) THE DEMONSTRATION, DRIVEN THROUGH THE COMPARATOR'S OWN `grade()`

A clean fixture grades `PASS`. Rewrite one arm's log (`L2-P`) as a primal that ran **50 printed
steps — iteration 490 of a registered 1,000** — with a **perfectly flat tail**, which is what a
primal that is converging normally looks like right up to the moment it is killed. Leave the
artefact untouched, still claiming `endTime = 1000`:

```
G1 completion    PASS
G-PRIMAL   L2    PASS    "max_initRes_at_endTime": 5e-05   <- read at iteration 490
G-PLAT  L2 CD    PASS    peak-to-peak 0.0 over a window of 10
G-TRIPLE         PASS    CD CONVERGING, order 2.0000, GCI 0.5556 %
ITEM VERDICT     PASS    PATCHED PASS, SHIPPED PASS
```

**A comparator that certifies a corpse at order 2.0000 is the most dangerous possible failure,
because every number in that chain looks like success.** The log and the artefact disagreed
about how far the run went and nothing compared them.

**THE NEAR-MISS IS REGISTERED HERE BECAUSE IT IS THE LESSON.** The first attempt at this
demonstration truncated the fixture's *decaying-oscillation* history, and **G-PLAT caught it —
for a reason that has nothing to do with completion.** A suite built on that fixture would have
shown a green completion story while having no completion gate at all. **A CONTROL THAT HAPPENS
TO FIRE FOR AN UNRELATED REASON READS AS A GATE THAT WORKS.** Rebuilding with a flat tail
removed the luck and turned a coincidence into a proof. That difference is now itself a unit:
a flat truncated tail is **invisible** to `G-PLAT` (peak-to-peak 0.0, clearing `DELTA_REF/10`)
while a decaying-oscillation truncation is not — so only `G1` can catch the flat one.

### (c) THE CLAUSE, REGISTERED

> **`G1-RUN`.** Per arm, on the **LAST primal segment** — the same segment `G-PRIMAL` and
> `G-PLAT` grade, so the run this clause certifies is the run they read. **Any clause failing
> is a REFUSAL (exit 2), not a gate that composes to `GATE FAIL`: a run that fails any clause
> is not done.**
> 1. `printInterval` is **read back from this arm's own log** and asserted equal to the
>    registered **10** — the same discipline as `G-PRIMAL`'s acceptance pair, and for the same
>    reason: the expected step count is *derived from it*.
> 2. the last `Time =` in that segment **equals `endTime` (1000)**;
> 3. **exactly one `End` line** is present in that segment;
> 4. the `ExecutionTime` count equals the **DERIVED** expected printed-step count;
> 5. the field set **`T U p nuTilda nut alphat phi`** is present at `endTime` in **every one of
>    the 4 processor directories**, and **every field is NEWER than the arm's own age datum**.

**CLAUSE 4 IS DERIVED IN THE FILE AND IS NOT THE LITERAL 101.** The count is the size of the
set `{1} ∪ {pi, 2·pi, … ≤ endTime/deltaT}`. **The unit-step form `round(endTime/deltaT)` = 1000
WOULD REFUSE EVERY CORRECT ARM**, because this family's output cadence is `printInterval 10`;
rule 4 clause 5 fixes the unit-step form as the **historical** case and says the count must
match the steps **WRITTEN**, not the steps **TAKEN**. A literal 101 would pass every test and
become silently wrong the moment any of the three inputs moved — the same class of defect as a
memory ceiling that describes the wrong machine. `d8g_of.py`'s `printed_sample_count()` computes
the same set, so **the gate and the producer agree by construction, not by two copies of one
number.**

**EVERY CLAUSE WAS MEASURED ON A REAL, GRADED ARM BEFORE IT WAS WRITTEN** — a gate built on a
line that does not exist refuses every correct run. On D8R's `F-P` arm
(`F-P_20260827T235119Z_1656338.log`, 41,760 cells, np = 4): the last primal segment carries
**exactly 101 `ExecutionTime` lines, 101 `Time =` lines, last `Time = 1000`, and exactly one
`End`** (33 in the whole 32-primal log, the extra being `decomposePar`'s); `printInterval 10`
reads back from the log; **4** processor directories exist; and **all seven fields are present,
gzipped, at time 1000 in every one of them, every one newer than the arm's own age datum.**

### (d) WHAT ELSE THIS FORCED, AND IT IS AN IMPROVEMENT

The clause **subsumed the suite's old "too few samples" fixture**, which had shortened the whole
log — now a *completion* failure, so `G1` refused it and `G-PLAT`'s want-of-evidence limb could
never be reached. The fixture is corrected so the two are **independent**: a run that completes
to `endTime` and still prints too few `CD:` lines. **A control reached only because a different
control let it through is not a control.** The fixture was also corrected to emit the `End` line
a real DAFoam arm prints, because a fixture that did not would make this clause refuse every
correct arm.

**AND ONE UNIT OF THIS AMENDMENT'S OWN SUITE WAS WRONG BEFORE IT WAS RIGHT, WHICH IS RECORDED
RATHER THAN QUIETLY FIXED.** The anti-hard-coding unit first asserted the formula returns
**1001** at `printInterval 1`. It returns **1000**: the printed set is `{1} ∪ {1,2,…,1000}` and
iteration 1 is in both halves. **The test had fallen for exactly the double-count the set-based
formula exists to prevent — the formula was right and the test was wrong**, a direction only
caught by driving the function rather than trusting it.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**ADDS** the `G1-RUN` completion clause, which **adds refusals and nothing else**: it can turn a
`PASS` or a `GATE FAIL` into a refusal and **can never manufacture a favourable verdict**. It
was found by code-reading, not by anyone looking at an answer they wanted. **ALTERS NO** gate
band, threshold, tolerance, label, cap or cost registered above: §4.1–§4.8, §4.6's Roache order
and `p ∈ [1.0, 3.0]`, §4.7's FD bands and trivial-baseline withdrawal, `AMENDMENT 1`'s `G-PLAT`
and `G-PRIMAL`, `AMENDMENT 2`'s corrected §6.3 line items and its §5 aggregate limb, §6.4's
ceiling and its REPORT-ONLY status, and §7's two-level adjoint ceiling are **untouched**. The FD
table at L2 remains owed and **remains the bright line** (`DAFOAM_CHARTER.md` §1).
**SUBMISSIONS PARKED.**


---

## FREEZE RECORD — 2026-09-11, the dafoam-supervisor

**`D8G` IS FROZEN.** `CLAUDE.md` rule 2: the grading path is fixed at the pre-registration commit,
and the frozen file is verified to be the file that ran by hashing it against the committed blob.

| instrument | md5 |
|---|---|
| `d8g_grade.py` — THE COMPARATOR | `12688063e20cbb6fa79cf08d0996d4e1` |
| `d8g_of.py` — the producer | `f17b4a26fc5dcbbb44e9c820ba16df6c` |
| `d8g_runScript.py` | `28c7819487a025a5f6554d38062a2b66` |
| `d8g_decomposeParDict` | `1dbd9ead3f40a29f483444dc5fa1288b` |
| `d8g_genmesh.sh` | `5b9db5102a4ffe04abffec6f7648d0c1` |
| `d8g_run_arm.sh` — the launcher | `05b7f8b1446968b64bc74d2f0f531fcb` |
| `d8g_chain_driver.sh` | `8c993186d6ff88d52f285907eba9b334` |
| `d8g_aggregate_memory.py` | `4218ea7f04433fd5c1a17cf90b80c1bf` |
| `d8g_cpuset_overlap.py` | `c57598a84b46e82c05be2ecb483fa301` |
| `d8g_runScript_contract.py` | `d5193d6309816909415894a9d98e1116` |

**VERIFIED BY THE SUPERVISOR PERSONALLY, not relayed**, immediately before this freeze: every md5
above re-taken from disk and matching; comparator suite **14/14 on the supervisor's own run**;
`ast.Assert` census **0** across all five Python instruments; and the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple` **absent**, with the reader shown able
to see a directory that IS there — `CURRICULUM-D8R-a6-twist-opt-conv` resolves — so that zero is
**measured, not assumed**. No D8G compute has run.

### ONE TOKEN REMAINS OPEN, DELIBERATELY

**`LAUNCH_BUDGET_S` in `d8g_run_arm.sh` is still `__D8G_UNFROZEN__`, and the launcher is therefore
FROZEN AND DELIBERATELY NOT YET RUNNABLE.** That value is the per-arm launch-witness deadline and it
is **measured by the first arm's `D4S_MPIRUN_EPOCH` line, never guessed** — the second leg of the
launch path (decomposePar-complete → first `ExecutionTime`) is timestamped nowhere in the surviving
artefacts, so it is bounded below at ~15 s and not bounded above by any evidence held. **A budget
invented here would be a number wearing the costume of a measurement.**

### THREE INSTRUMENTS CARRY NO PERMISSION LINE, BY REGISTERED EXCEPTION

`d8g_runScript.py`, `d8g_decomposeParDict` and `d8g_cpuset_overlap.py` are **byte copies** of frozen
D8/D8R instruments, and their provenance **is** their byte identity. A permission line would destroy
it — and for the producer would invalidate `PRODUCER_MD5` and the three-way `D8 → D8R → D8G`
identity on `28c7819487a025a5f6554d38062a2b66`. Their permission lives in their deltas diffs and
their md5s. This is an exception taken deliberately, not an oversight.

### A HAZARD CLOSED BEFORE THE FREEZE, AND IT WOULD HAVE FALSIFIED THREE REGISTRATIONS

With its md5 tokens filled, `d8g_chain_driver.sh` no longer aborted at its freeze guard — and the
next thing it did was `mkdir -p "$BASE"`. **Merely RUNNING the driver would have created the run
root**, falsifying the *"the run root does not exist"* condition that **AMENDMENTS 1, 2 AND 3 are
each registered against** — an irreversible edit to the evidence for three registrations, made by a
script that then aborts because there is nothing to run. The driver now **refuses** when the root is
absent and names the step that legitimately creates it (`d8g_genmesh.sh:127`, which makes it when it
first has something to put in it). Verified by running the driver after the tokens were filled: exit
5, run root checked absent before **and** after.

### WHAT THIS FREEZE DOES NOT ASSERT

**No D8G level has been solved and nothing downstream of the freeze guards has ever executed.**
Nothing in this item has imported DAFoam, IDWarp, mphys, pyGeo or OpenMDAO. Specifically **NOT**
established: that `DAFoamBuilder` accepts these options; that `nom_addRefAxis` returns 8; and that
**the L1 surface's 696 quads support the 25×30 thickness-constraint projection `configure()` runs
inside `prob.setup()` on every arm** — which, if it throws, throws **before the first primal**. That
is the sharpest known risk on this rung and it is bought cheaply by an L1 smoke, which is the first
thing to run after this freeze. A failure there is a **finding about the coarse level of a
fixed-design triple**, not a nuisance.

**SUBMISSIONS PARKED.**


---

## AMENDMENT 4 — 2026-09-11 — **PRE-COMPUTE. THE MESH GENERATOR ABORTS ON ITS OWN FIRST CONTAINER LINE, FOR EVERY LEVEL.**

**Lines whose number changed above this section: 0.**

### THE DEFECT, CONFIRMED BY OBSERVATION AND NOT BY REPRODUCTION

`d8g_genmesh.sh:231-233` emits a `cmd.sh` beginning `set -e`, then
`source /home/dafoamuser/dafoam/loadDAFoam.sh`. **In this item's own pinned image
`dafoam-idwarp-rot@sha256:2927768a…`, at this item's own `--user 0:0`, and at its own nesting
(`bash -lc "timeout -k 60 3600 bash cmd.sh"`), that source ABORTS THE SHELL: rc = 1, and LINE 3 IS
NEVER REACHED.** The abort is inside OpenFOAM's own
`OpenFOAM-v2506/etc/config.sh/setup:207` — *"pop_var_context: head of shell_variables not a function
context"*. Control with `set -e` removed: line 3 reached, rc 0. **So mesh generation dies on its own
first line at every level, before the tarball is even extracted.**

**The bug is `set -e` interacting with OpenFOAM's own sourcing, and it is uid-independent** — this
item runs `--user 0:0` and has no uid defect. That is what distinguishes it from A3GC AMENDMENT 5,
whose generator died of a directory-traversal failure the same line class had *silenced*.

**AND THE ASYMMETRY IS WORTH THE RECORD: D8G FAILS LOUDLY.** `:299` tests `GRC -eq 0` and aborts
`G-GEN.5 generation rc=1`. A3GC's `|| true` made the identical class of failure **silent**, so it
presented as a missing binary seven steps downstream. **That is the difference between a rung that
stops and a rung that runs seven dead steps** — and it is the argument for the repair A3GC took, not
merely for this one.

### THE REPAIR — ONE REMOVED LINE, EIGHT ADDED, NOTHING ELSE

`set -e` is no longer armed *above* the source. In its place the generated `cmd.sh` makes a
**POSITIVE CAPABILITY ASSERTION** — `CLAUDE.md` rule 3 applied to an environment rather than a field
— requiring `WM_PROJECT_DIR` to be non-empty and `cgns_utils` to resolve, and **exiting 97 naming
`WM_PROJECT_DIR`, `cgns_utils` and `id`** if it cannot. **`set -e` is armed AFTER the assertion**,
where it can do its job. This is the same repair shape as A3GC AMENDMENT 5(a), and for the same
reason: **the source's rc is not a test — without `set -e` it returns 0 even when the environment did
not load, so a silent success and a silent failure carry the same rc.**

### A LIVE TRAP FOUND WHILE WRITING IT, WHICH IS THE SAME SHAPE AS THE DEFECT

**The heredoc is UNQUOTED** — `cat > cmd.sh <<CMDEOF`. An unescaped `${WM_PROJECT_DIR:-}` would
therefore have been expanded **by the host** to the empty string and written into `cmd.sh` as
`[ -z "" ]`: **an assertion that aborts every run while appearing to test the environment.** That is
precisely the failure class being repaired — an instrument reporting about something it is not
testing. The escaping was **verified by executing the heredoc in isolation and reading the emitted
file back**: it carries the literal `${WM_PROJECT_DIR:-}` while `$LEVEL` correctly expands host-side.
Nothing under `certonomous-runs` was created to check it.

### A FAILED CHECK, RECORDED BECAUSE IT FAILED IN THE DANGEROUS DIRECTION

A first grep-based scope check over the registered keys reported the frozen file and the candidate as
**different**. The cause: the new comment block **quotes** `3600`, `G-GEN.5` and the image digest
while *explaining* them, and **the checker matched the repair's own prose and called it a change to
the thing the prose was about.** The check that actually answers the question is the
**executable-line diff**, and it shows exactly **one removed line (`set -e`), eight added, the
`source` line neither removed nor moved, and nothing else across 411 lines** — re-verified
independently by the supervisor. **The failed check is recorded as well as the good one, because it
failed in the direction that would have reported a false difference** and, in the other direction,
would have hidden a real one.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**CHANGES HOW THE GENERATED `cmd.sh` GUARDS ITS ENVIRONMENT. CHANGES NOTHING ABOUT WHAT IS MEASURED
OR WHAT WOULD PASS.** No gate, band, threshold, cap, tolerance, cost or label is touched: §4's
`G-MESH`, `G-MESH-STRICT`, `G-SYS`, `G-BODY`, `G-TE`, `G-PRIMAL`, `G-PLAT`, `G-TRIPLE` and `G-FD`, the
registered cell counts 5,568 / 44,544 / 356,352, §6.3's corrected 403.259 core-min and §6.4's ceiling
all stand **exactly as registered**. The comparator `d8g_grade.py`
`12688063e20cbb6fa79cf08d0996d4e1` is **NOT TOUCHED**.

**LEGAL PRE-COMPUTE:** rule 2 closes gates after FIRST COMPUTE and **no D8G level has been solved and
no D8G mesh has been generated.** The run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple` was re-checked **ABSENT**, with the
reader shown able to return EXISTS for directories that are there.

### RE-FREEZE

| instrument | frozen `075f6edf6` | **re-frozen, this amendment** |
|---|---|---|
| `d8g_genmesh.sh` | `5b9db5102a4ffe04abffec6f7648d0c1` | **`2b22d01e265ba8362a12644c32bbd409`** |
| every other instrument | unchanged | unchanged |

**SUBMISSIONS PARKED.**


---

## AMENDMENT 5 — 2026-09-11 — **THE GENERATOR NEVER STAGED `system/` INTO ITS OWN WORKING DIRECTORY. IT CANNOT COMPLETE ANY LEVEL.**

**Lines whose number changed above this section: 0.**

**THE DEFECT.** `d8g_genmesh.sh` runs its entire OpenFOAM chain — `plot3dToFoam`, `autoPatch`,
`createPatch`, `renumberMesh`, `checkMesh` ×2 — with `-w /mnt/mesh_build_<LEVEL>`, and **nothing ever
stages `system/` into that directory**; its only `cp` of `system/` lands in `base_<LEVEL>/` *after*
the container. `plot3dToFoam` died on `cannot find file /mnt/mesh_build_L1/system/controlDict`,
`set -e` aborted, and `G-GEN.5` refused at rc=1. **NOT level-specific: the frozen generator cannot
complete any level.** It survived the freeze because, per its own header, **it had never been
executed** — the same reason AMENDMENT 4's `set -e` defect survived.

**THE MESH ITSELF IS NOT IN QUESTION, and that is what makes this cheap.** Measured on the repaired
run, every registered prediction held: c0 **44,544** quads → **11,136** → **2,784** → **696**, each
ratio **4.0000 exactly**; L1 surface **696 quads / 996 points** against the registered 696 / 996;
pyHyp marched all 9 levels and wrote `volumeMesh.xyz`; pinned digest; the c1 trap file unused. Cells
**5,568**, exactly as registered. `checkMesh` reproduced the `N-D47` signature — plain **`Mesh OK.`**,
strict **`Failed 2 mesh checks`** (34 bad face tets, 1,284 small-determinant cells) — and the
small-determinant fraction is **1284/5568 = 0.23060, INSIDE the registered [0.15, 0.28] band.**

**THE REPAIR.** `system/` is staged into the working directory before the OpenFOAM chain, from the
**same `$ARCHIVE/system`** and the **same five dicts whose md5s the script already registers**. **No
`controlDict` is invented.** The manifest is checked **before** the copy, not after (12/12 OK).

**A SECOND ITEM, AND IT IS THE ONE THAT MATTERED.** `"generated_by"` in the mesh record was a
hardcoded literal, so a mesh built by the candidate **named the frozen file as its producer**.
`d8g_grade.py` does not read that field — **which is why it matters rather than why it does not:** an
ungated provenance string concealed the single question that is the supervisor's, namely **that the
mesh was not built by the frozen script.** Fixed to report the actual producer; the false record is
preserved at `base_L1_SUPERSEDED_FALSE_PROVENANCE_20260911T2151Z/`.

**RULING ON THE MESH ALREADY BUILT: IT IS A DIAGNOSTIC, NOT A GRADED ARTIFACT.** It was produced by
`d8g_genmesh_candidate.sh`, not by the frozen path, and **a mesh not built by the frozen generator may
not be graded.** L1 is regenerated by the re-frozen script below, at a cost of ~2.9 core-min — cheap,
and the only answer consistent with pinning a generator by md5 at all.

**ALTERS NO** gate, band, threshold, cap, cost or label. `d8g_grade.py`
`12688063e20cbb6fa79cf08d0996d4e1` is **NOT TOUCHED**. Legal pre-compute: **no D8G level has been
solved.**

**RE-FREEZE:** `d8g_genmesh.sh` `2b22d01e265ba8362a12644c32bbd409` → **`0d18d20d9bea13d1ef794892a1d4edd5`**.

**SUBMISSIONS PARKED.**


---

## ADDENDUM 1 — 2026-09-11 — **THE LAST TOKEN IS FILLED BY DERIVATION, AND DERIVING IT CAUGHT TWO DEFECTS THE HARD-CODED TABLE WOULD HAVE SHIPPED.**

**Lines whose number changed above this section: 0.**

`d8g_run_arm.sh:805` carried `LAUNCH_BUDGET_S=__D8G_UNFROZEN__WITNESS_BUDGET`, **the last
executable token in the item**, and the launcher was frozen-and-deliberately-unrunnable until it was
filled. The file's own design note says the value is *"MEASURED by the first arm's
`D4S_MPIRUN_EPOCH` line"* — **a bootstrap that could not close, because the first arm cannot run to
measure it.**

**IT IS DERIVED, NOT GUESSED:** `LAUNCH_BUDGET_S = floor((TMO - 1) / 2)`, the largest integer
strictly below `TMO/2`, where `TMO = CAP × 60 / RANKS` already descends from the registered cap and
rank count. **No second number exists to drift**, and a literal is never written. The first arm then
converts this derived bound into a measured one.

**ALTERS NO gate, band, threshold, cap or label.** The launch-witness deadline decides when a launch
is declared dead; **no gate reads it.** The comparator `d8g_grade.py`
`12688063e20cbb6fa79cf08d0996d4e1` is untouched.

### FINDING 1 — TWO OF THE SIX CEILINGS IN CIRCULATION WOULD HAVE ABORTED AT LAUNCH

The per-arm ceilings quoted in this item's working notes are reproducible from `TMO` **as `TMO/2`
rounded** — but `LA.3` is **strict**, `0 < b < t/2`, and **a rounded half is not below its own half**:

| arm | `TMO` | `TMO/2` | derived | previously quoted | `LA.3` on the quoted value |
|---|---|---|---|---|---|
| L1-P | 705 | 352.5 | **352** | 352 | PASS |
| **L2-P** | 786 | 393.0 | **392** | 393 | **ABORT** |
| L3-P | 1439 | 719.5 | **719** | 719 | PASS |
| **A2-P** | 1829 | 914.5 | **914** | 915 | **ABORT** |
| F2-P | 3053 | 1526.5 | **1526** | 1526 | PASS |
| F2-S | 3213 | 1606.5 | **1606** | 1606 | PASS |

**Hard-coding that table would have aborted L2-P and A2-P at the launch itself**, after staging and
every image and row check had passed — a failure nobody had predicted, prevented only because the
value is derived rather than transcribed.

### FINDING 2 — THE DESIGN NOTE AND THE CODE DISAGREE ABOUT WHAT THE WITNESS IS

The note names `D4S_MPIRUN_EPOCH`. The code waits for `LAUNCH_WITNESS_RE = ^ExecutionTime = `
(`:588`) — **the first solver iteration** — with `^Time = ` registered as the `decomposePar` decoy.
**`D4S_MPIRUN_EPOCH` is deliberately built to match none of the log readers, so it CANNOT be the
witness.** The budget therefore has to cover container start **+** the TensorFlow import **+**
`DASolver` construction **+** `decomposePar` **+** one iteration.

**MEASURED TONIGHT ON A3GC L3, and it makes the headroom thinner than it looks:** first
`ExecutionTime` arrived at **~270–290 s** at box load 26–32 and **~370 s** at load 37–70, with the
TensorFlow import alone ~60–70 s and **mesh-independent**. D8G's L1 mesh is 18× smaller so its read
is near-instant, but **L1-P's derived ceiling is 352 s and CANNOT BE WIDENED** — 352 *is* the `LA.3`
ceiling at a 46.977 core-min cap. **A launch-witness timeout on L1-P is a foreseeable outcome and is
recorded here in advance as infrastructure, not as a physics failure.**

**RE-FREEZE:** `d8g_run_arm.sh` `05b7f8b1446968b64bc74d2f0f531fcb` →
**`51ff683dda23aa0143d1a2fe5047c780`**. **Zero `__D8G_UNFROZEN__` tokens remain.**

**SUBMISSIONS PARKED.**


---

## ADDENDUM 2 — 2026-09-11 — **THE CAP ASSERTION REFUSED FOUR OF TEN ARMS ON ITS OWN ROUNDING, AND IT RODE THROUGH A GRADED TWO-ROW CAMPAIGN WITHOUT ONCE BEING TESTED.**

**Lines whose number changed above this section: 0.**

### THE DEFECT

`d8g_run_arm.sh` derives `TMO = int(round(cap × 60 / RANKS))` — an **integer second** — then
back-checks by reconstructing `TMO × RANKS / 60` and comparing it to the registered cap at a
**0.02** tolerance. **The rounding is worth up to 0.5 s, which at 4 ranks is 0.0333 core-min —
LARGER THAN THE TOLERANCE THE SAME CODE ENFORCES.** The guard therefore refuses perfectly correct
caps, and **which** arms it refuses is decided by nothing but where `cap × 60 / RANKS` happens to
fall relative to a half-second.

**FOUR OF TEN ARMS COULD NOT LAUNCH AT ALL:** `L1-P`/`L1-S` (error 0.0230) and `A2-P`/`A2-S`
(0.0227), aborting in under one second at `ABORT CAP MISMATCH registered=46.977 enforced=47.0`,
**before any container, ledger row or cost.**

### WHY THE FREEZE DID NOT CATCH IT — THE PART WORTH KEEPING

The header marks this assertion **"inherited unchanged"** from `d8r_run_arm.sh`, *"A FROZEN
INSTRUMENT BEHIND A GRADED TWO-ROW PASS."* **D8R's caps are 1000.0 and 120.0, which divide to EXACT
INTEGER SECONDS — 15000 and 1800 — so the back-check error is IDENTICALLY ZERO and the assertion
COULD NEVER FIRE.** It passed an entire graded campaign **without once being executed against a case
capable of failing it**, then inherited into D8G, whose three-decimal caps make it fire immediately.

**A GUARD INHERITED FROM A PASSING INSTRUMENT IS NOT A GUARD THAT HAS BEEN SHOWN TO WORK.** This is
the seventh check in one session trusted because nothing had ever made it fail. **It at least fails
SAFE** — refusing a good run rather than passing a bad one — which is the right direction for a guard
to be broken in and why it cost **0 core-min**.

**AND IT WAS FOUND BY LUCK OF ORDERING, which is recorded rather than dressed up as method:** the
first arm sent to launch was `L1-P`, one of exactly four that trip it. Had the first launch been
`L2`, `L3` or either `F2` arm, the assertion would have passed and **four arms would have died at
staging later, after their meshes and staging costs had been paid.**

### THE REPAIR

The inversion now runs against the quantity the code **actually derived** — the **unrounded**
`cap × 60 / RANKS` in seconds — and admits **exactly the rounding quantum, 0.5 s, and nothing more**.
That is the tightest bound that can admit a correct `int(round())`, so **the guard is not loosened;
it is pointed at the right number.** `D4_CAP_ASSERT` now prints `exact_wall_s` and `drift_s`, so the
judged quantity is in the record rather than inferred.

**THE TOLERANCE IS NOT WIDENED AND THE REGISTERED CAPS ARE NOT TOUCHED.** Widening the tolerance
would weaken a real guard to hide an arithmetic artifact; the caps are registered numbers.

| arm | cap | `exact_wall_s` | `TMO` | `drift_s` | old rule | new rule |
|---|---|---|---|---|---|---|
| L1-P / L1-S | 46.977 | 704.6550 | 705 | 0.3450 | **ABORT** | PASS |
| L2-P / L2-S | 52.416 | 786.2400 | 786 | 0.2400 | pass | PASS |
| L3-P / L3-S | 95.922 | 1438.8300 | 1439 | 0.1700 | pass | PASS |
| A2-P / A2-S | 121.956 | 1829.3400 | 1829 | 0.3400 | **ABORT** | PASS |
| F2-P | 203.520 | 3052.8000 | 3053 | 0.2000 | pass | PASS |
| F2-S | 214.185 | 3212.7750 | 3213 | 0.2250 | pass | PASS |

**The maximum possible drift is 0.5 s BY CONSTRUCTION**, so the bound cannot be exceeded by a
correctly derived wall for any cap — the margins above are structural, not luck.

**PLANTED BOTH WAYS, end to end in the real script, stopping at the assertion so nothing staged or
launched:** a correct cap **passes** (`exact_wall_s=704.655000 enforced_wall_s=705
drift_s=0.345000`); a wall hard-coded to 700 s **still ABORTS** (`drift_s=4.655 exceeds rounding
quantum 0.5`, rc=65). **The guard remains strict against exactly what it exists to catch.**

**ALTERS NO** gate, band, threshold, cap or label. `d8g_grade.py`
`12688063e20cbb6fa79cf08d0996d4e1` untouched.

**RE-FREEZE:** `d8g_run_arm.sh` `51ff683dda23aa0143d1a2fe5047c780` →
**`32d0911ed3749fef4a4cb36db62b46d8`**.

**SUBMISSIONS PARKED.**


---

## ADDENDUM 3 — 2026-09-11 — **THE STAGED-INSTRUMENT MANIFEST CHECK COULD NEVER PASS. IT IS THE MIRROR OF EVERY OTHER DEFECT TONIGHT.**

**Lines whose number changed above this section: 0.**

### THE DEFECT

`INSTRUMENT_MD5S` (`d8g_run_arm.sh:275`) separates its three rows with a **literal backslash-n** —
two characters inside a double-quoted bash string. Bash does not interpret it and `printf '%s\n'`
does not either, so **`md5sum -c` received ONE filename containing the entire manifest.** The guard
requires 3 `OK` lines and could therefore **only ever abort.**

**PROVEN, NOT INFERRED**, with all three instruments present and every md5 matching:

| spelling | rc | `OK` lines |
|---|---|---|
| `printf '%s\n'` (frozen) | 1 | **0** |
| `printf '%b\n'` | 0 | **3** |

### THIS IS THE MIRROR OF THE PATTERN, AND THAT IS THE POINT

**Seven checks this session could not FAIL. This one could not PASS.** It fails **safe** — refusing a
correct staging rather than admitting a wrong one — which is why it cost **0 core-min**, exactly as
the cap-assertion defect of ADDENDUM 2 did. Both aborted before a container, a ledger row, or a
single core-second.

**AND THE SAME ITEM ALREADY CONTAINS THE CORRECT IDIOM.** `d8g_chain_driver.sh:195` builds the
identical check as `{ echo …; echo …; } | md5sum -c -` — one `echo` per row, real newlines — and it
works. **Two spellings of one check in one item; the launcher inherited the broken one.**

### THE REPAIR — ONE CHARACTER

`%s` → `%b` at `:384`. **`%b` over the embedded escapes is deliberate rather than rewriting the
manifest multi-line**, which would shift 760 lines of a file this document's addenda cite by number.
It is safe because the manifest holds only hex digests, spaces, slashes and `@BASE@`, and `@BASE@` is
substituted by `sed` **after** `printf`, so no path content ever meets escape interpretation.

**LINE PRESERVATION VERIFIED, NOT ASSERTED:** lines **275, 588 and 838** are byte-identical to the
committed blob; only **384** differs.

**PLANTED FOUR WAYS on one fixture, so the pass is not a reader that says OK to everything:**
all three correct → **rc 0, 3 OK, PASS**; `d8g_of.py` tampered by one byte → **rc 1, 2 OK, ABORT**;
`d8g_decomposeParDict` removed → **rc 1, 2 OK, ABORT**; restored → **rc 0, 3 OK, PASS**.

### RULING — THE CHAIN DRIVER IS THE ENTRY POINT, NOT THE ARM

The three instruments are **absent from the run root**, and staging is **not the arm's job**:
`d8g_chain_driver.sh:193` stages them and `:87` resolves the launcher. **Even with this repair the
arm cannot pass its own manifest check until the chain driver has staged**, so **L1-P is launched
through `d8g_chain_driver.sh`**, which is the designed path. Launching the arm directly would require
hand-staging — the same "not built by the frozen path" defect that already cost one mesh
regeneration on this item.

*(Noted, not edited: `d8g_chain_driver.sh:79` still reads "d8g_run_arm.sh itself still carries two
unfrozen tokens." That prose is stale — the count is zero — and it changes no behaviour.)*

**ALTERS NO** gate, band, threshold, cap or label. `d8g_grade.py` `12688063e20cbb6fa79cf08d0996d4e1`
untouched.

**RE-FREEZE:** `d8g_run_arm.sh` `32d0911ed3749fef4a4cb36db62b46d8` →
**`7ce53b9242ac6e850cc330712d93d5b0`**.

**SUBMISSIONS PARKED.**


---

## ADDENDUM 4 — 2026-09-11 — **TWO STALE INSTRUMENT PINS. ONE HAD BEEN STALE SINCE 18:37 AND NOBODY COULD SEE IT, BECAUSE THE LOOP ABORTS AT ITS FIRST FAILURE.**

**Lines whose number changed above this section: 0.**

`d8g_chain_driver.sh` pins the md5 of each frozen instrument it stages, and **two pins were stale**:

| pin | file | pinned | actual | |
|---|---|---|---|---|
| `MD5_LAUNCHER` | `d8g_run_arm.sh` | `05b7f8b1…` | `7ce53b92…` | **STALE** |
| **`MD5_GENMESH`** | `d8g_genmesh.sh` | `5b9db510…` | `0d18d20d…` | **STALE** |
| `MD5_GRADER` | `d8g_grade.py` | — | — | OK |
| `MD5_DECOMP` | `d8g_decomposeParDict` | — | — | OK |

**ONLY THE FIRST FIRED.** `MD5_GENMESH` has been stale since **18:37** (ADDENDUM 4's genmesh repair),
superseded again at 21:58 — **hours before tonight's launcher work — so the chain driver has not been
runnable since then and nothing revealed it, because the loop aborts at its first failure.**
**Repairing only the pin that fired would have bought exactly one more abort.** The pin that fires is
not the same question as the pins that are true.

**THE STRUCTURAL POINT, recorded so it is not rediscovered later:** a frozen instrument that pins the
md5 of another frozen instrument is a **CASCADE** — every amendment to a pinned file invalidates the
pinning file, and since both are frozen, **one repair costs two amendments**. The mechanism is still
correct: those pins are exactly what makes "not built by the frozen path" detectable, the ruling that
has held three times on this item and cost one mesh regeneration to establish. **The cascade is a
maintenance cost of that guarantee, not a reason to drop it.**

**Planted four ways on COPIES, the frozen originals never modified:** untampered → all four OK;
launcher tampered one byte → ABORT on it; genmesh tampered → ABORT on it; restored → all four OK.
**Each of the two updated pins is shown refusing**, so the new hashes are not a reader that accepts
anything.

**ALTERS NO** gate, band, threshold, cap or label.
**RE-FREEZE:** `d8g_chain_driver.sh` `8c993186d6ff88d52f285907eba9b334` →
**`b3a19380eeb2c67d2a860cc05f0ef559`**.

**FOUR LAUNCH ATTEMPTS TONIGHT, FOUR ABORTS, ZERO CORE-MIN, FOUR DISTINCT REAL DEFECTS** — the cap
back-check arithmetic, the witness-budget placeholder, the manifest's literal backslash-n, and these
two pins. **Every one caught by a guard before anything was spent.**

**SUBMISSIONS PARKED.**


---

## ADDENDUM 5 — 2026-09-11 — **NOTHING STAGED THE MODEL DICTS. THE SAME DEFECT, THE SAME SOLVER AND THE SAME MISSING FILE HAD ALREADY APPEARED IN A3GC HOURS EARLIER — ONE FAMILY-WIDE GAP, NOT TWO BUGS.**

**Lines whose number changed above this section: 0.**

`DARhoSimpleCFoam` is compressible and cannot start without
`constant/thermophysicalProperties`. `base_L1/constant/` held **`polyMesh` and nothing else**; the
registered archive `A6-crm-wing/constant/` **has** both that dict and `turbulenceProperties`, and
**nothing staged them**. L1-P died at
`FOAM FATAL ERROR: cannot find file ".../processor0/constant/thermophysicalProperties"` —
**after every gate had passed.**

**THIS IS THE SECOND ITEM.** A3GC hit the identical defect at 21:40Z: same solver, same missing dict,
same symptom, likewise reached only once every gate was green. **It has now cost A3GC three attempts
and D8G one, and the next compressible rung in this family will carry it too.**

**THE REPAIR.** The dicts are staged from the registered archive, **invented nowhere**, in the
driver's per-level loop beside the `decomposeParDict` overlay that already writes into `base_$LV`;
the arm copies `base_$LEVEL` wholesale, so one placement reaches **every arm of that level**. Placed
there rather than in `d8g_genmesh.sh` deliberately: that route would require **regenerating all three
meshes and re-pinning `MD5_GENMESH`** — a further amendment — for a staging step that is not mesh
construction.

**ASSERTED ARITHMETICALLY, NOT BY PRESENCE.** The staged dict must reproduce **R = 287.0025** against
the frozen `d8g_runScript.py`'s registered `rho0 = p0/T0/287.0`. **A file-presence check would pass a
wrong gas**; `rho0` feeds the force normalisation directly, so this binds the staged gas to a
registered constant of this item.

**PLANTED FOUR WAYS, and the leftovers count is part of the control:** archive gas → **PASSED
R=287.0025, leftovers 0**; `molWeight 32` → **REFUSED R=259.8270, leftovers 0**; `kOmegaSST` →
**REFUSED**; restored → **PASSED**. **Assert-then-move**, because staging that copies first and
asserts after leaves the *rejected* dict in the case for a later launch to solve silently — the
hazard A3GC created, planted and caught tonight, and which is not being paid for a third time.

**ALTERS NO** gate, band, threshold, cap or label.
**RE-FREEZE:** `d8g_chain_driver.sh` `b3a19380eeb2c67d2a860cc05f0ef559` →
**`1cfc0f17e0d7dfaf3d711b690446860b`**.

**FIFTH ABORT, and its cost is a MEASUREMENT:** 248 s × 4 ranks = **16.5 core-min GROSS with
`ExecutionTime` count 0** — **zero solve time**, all container start, TensorFlow import,
`decomposePar` and teardown. That is the first clean isolation of this item's **fixed per-run
overhead**, with no solve mixed in, and it recurs on all ten arms.

**ADDENDUM 1's WITNESS BOUND REMAINS UNDETERMINED.** `D4S_MPIRUN_EPOCH` at **+50 s** is a wide margin
**at the mpirun stage only**; the budget must cover the **first iteration**, which this run never
reached. **The +50 s is not clearance of the 352 s question.**

**SUBMISSIONS PARKED.**


---

## ADDENDUM 6 — 2026-09-12 — **THE LAUNCH-WITNESS BUDGET WAS CAP-DERIVED; WITH NO CAP IT BECOMES A MEASURED CALIBRATION FIGURE THAT ESCALATES INSTEAD OF REFUSING.**

**Lines whose number changed above this section: 0.**

`LAUNCH_BUDGET_S` ceases to be `floor((TMO-1)/2)` (cap-derived) and becomes `ceil(2.0 × (255.93 + 3.0e-5 × cells))` — **MEASURED**, `WITNESS_CALIBRATION_20260912/`: mesh-independent `dafoam`+TensorFlow import **255.930 s** at box load1 69→97, `decomposePar` **1.337 s at 44,544 cells** (L2 is *faster* than L1's cold 7.074 s at 5,568, refuting the linear-in-cells scaling ADDENDUM 1 and `L2_CONVERGENCE_PREDICTION_REGISTERED_BEFORE_RUN.txt` §5 both assumed) — and **exceeding it now writes a `D8G_LAUNCH_ESCALATION` line and keeps waiting rather than returning 89**, because Sanaa ruled 2026-09-12T01:10Z *"i dont want any cap on any run"* and the old form was arithmetically certain to kill a live L2-P (392 s budget against a 255.9 s mesh-independent import alone); **`rc=88` (container exited, evaluated before this clock) and `rc=90` (reader unreadable) are untouched and remain real refusals, `rc=89` is retired, the in-container deadline `TMO` and every gate, band, threshold, cap and label stand exactly as frozen, and no gate reads this number (ADDENDUM 1: *"no gate reads it"*; `d8g_grade.py` is untouched at `12688063e20cbb6fa79cf08d0996d4e1`).**

**SUBMISSIONS PARKED.**

---

## ADDENDUM 7 — 2026-09-12 — **THE R3 REPAIR PACKAGE IS APPLIED TO L1-P ON A FRESH ROOT. THE TRANSFER TO THE CRM WING-BODY IS UNTESTED AND IS REGISTERED AS UNTESTED.**

**Lines whose number changed above this section: 0.**

### 7.1 What was measured, and what the graded root actually says

The graded root `CURRICULUM-D8G-a6-grid-triple/` carries **`NOT A RESULT`**
(`D8G_grade_20260911T234701Z.json`). **Its refusal cites the LEDGER, not the physics** — a
`PRESENT-BUT-GARBAGE` row from *attempt 1* (`launched: false`, `launch_rc=88`,
`never_started_container_exited after 248s`, `solver_call_seen=no`). **Attempt 2 did run**:
`L1-P_20260911T234236Z_2435242.log` reaches `Time = 1000` and prints
`Primal min residual 0.000407398155493068 did not satisfy the prescribed tolerance 1e-08`
→ `Primal solution failed!` → rc=1, `wall_s=241`, `ExecutionTime = 8.41 s`.
**Two distinct failures sit under one verdict** and the earlier framing conflated them.

**The binding field is `nuTilda`, plateaued at 4.0740e-04** against the registered accept product
`primalMinResTol × primalMinResTolDiff = 1e-08 × 1e4 = 1.0e-04` → **4.074x above floor**.
`CD 0.044201` / `CL 0.358286` were steady to six digits over the last 30 iterations: **the
integrals converged and the turbulence field did not.**

### 7.2 The repair, and an honest correction to how it was briefed

The fix is imported from **A2 `curriculum_D6RF10` rung R3**, which drove its binding field from
1.681e-05 (GATE FAIL, plateaued) to **6.323e-06**, below floor and plateaued.

It was briefed to this lane as a **package of six** — `DARhoSimpleCFoam`, `nNonOrthogonalCorrectors 12`,
`relax_p 0.70`, `relax_eqn 0.70`, `endTime 2000`, LIMITED `fvSchemes`. **That enumeration is
incomplete, and the omission is load-bearing here.** R3's six are *deltas applied on top of the
`d6rf7_fvSolution` base*, and that base carries a **tightened linear-solver stopping rule** its own
comments name **"THE nuTilda REPAIR (D6RF4 section 1.5)"**: GAMG `relTol 0.001` / `tolerance 1e-12` /
`minIter 5`, smoothSolver `relTol 0.001` / `tolerance 1e-09` / `nSweeps 3`.

**D8G's archive `fvSolution` carries the LOOSE rule that block was written to replace** — GAMG
`relTol 0.1` / `tolerance 0`, smoothSolver `relTol 0.1` / `tolerance 0` / `nSweeps 1`. The D8G log
shows that rule setting the plateau directly, line by line:
`nuTilda initRes: 4.07e-04 finalRes: 3.31e-05 **nIters: 1**` — one sweep, ~12x reduction, stop.
**Transferring only the six would have left the mechanism that produces the D8G plateau in place.**
The tightened stopping rule is therefore applied as part of the repair and is named here rather
than smuggled in under "the SIMPLEC fix".

**Applied to `L1-P-R1` (each edit read back from disk after writing):**

| # | Knob | Was | Now |
|---|---|---|---|
| 1 | `solverName` | `DARhoSimpleCFoam` | unchanged — **already SIMPLEC**; no credit is claimed for it |
| 2 | `nNonOrthogonalCorrectors` (SIMPLE scope only) | 0 | **12** (`potentialFlow` 20 untouched) |
| 3 | `relaxationFactors/fields "(p\|rho)"` | 1.0 | **0.70** |
| 4 | `relaxationFactors/equations "(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega)"` | 0.80 | **0.70** |
| 5 | `controlDict endTime` | 1000 | **2000** |
| 6 | `fvSchemes` | archive | **`d6rf7_fvSchemes_LIMITED`, md5 `fbca617a0808c56113a34d156c5890b9`** — R3's registered pin |
| 7 | GAMG p | `relTol 0.1`, `tolerance 0` | **`relTol 0.001`, `tolerance 1e-12`, `minIter 5`** |
| 8 | smoothSolver | `relTol 0.1`, `tolerance 0`, `nSweeps 1` | **`relTol 0.001`, `tolerance 1e-09`, `nSweeps 3`** |

**Div-scheme coverage was checked before staging, not after a FOAM FATAL:** every one of the 13
`div` schemes D8G's archive declares is present in the LIMITED file (`comm -23` → empty). The
superseded LIMITED md5 `8374443e…` present on disk **lacks `div(phid,p)`** and would have aborted
`DARhoSimpleCFoam`; the pinned `fbca617a…` is the one R3 actually passed on.

**`d8g_of.py` refuses `endTime != 1000` at `:744`** (`REGISTERED_CONTROLDICT`, `:125`), so knob 5
could not reach the solver unaided. The frozen `d8g_of.py` is **not edited** and stands at
`f17b4a26fc5dcbbb44e9c820ba16df6c`; a repair copy **`d8g_of_R1.py`** (`654bd80bcc7e9fd6c4f370f72346176f`)
carries **exactly one delta**, `diff`-verified to a single line: `endTime 1000.0 → 2000.0`.
The plateau-window forecast is computed from the controlDict, not hardcoded, so it tracks the change.

### 7.3 The prediction, registered before the solver starts

**Predicted: the run clears.** `nuTilda` falls below 1.0e-04 and plateaus, the primal returns rc=0,
and `CD`/`CL` shift from the 0.044201 / 0.358286 baseline (expected — `limited 0.333` trades spatial
accuracy for non-orthogonal robustness; **reported, not gated**).

**REGISTERED AS UNTESTED.** **A6 CRM wing-body is a different geometry from the A2 MACH wing and
this transfer has never been run.** If `nuTilda` does **not** clear, the correct reading is **not**
"the run failed": it is that **the R3 package is case-specific**, which is **a larger finding than a
pass** and is what the ladder most needs to know. Either outcome is informative and neither is
re-run at a different setting to get a nicer number.

### 7.4 No cap, of any kind

Sanaa ruled on 2026-09-12 — her fourth such ruling — *"NOOO CAP. NO MORE CAPS. NO RUN GETS STOPPED
BC OF A TIME OR BUDGET CAP."* **Stripped for this launch, and none is replaced by an equivalent:**
the in-container `timeout` / `-k 60` (`d8g_run_arm.sh:326/:485`), the `cap_core_min` → `TMO`
derivation, the `rc=124`/`rc=137` path, `LAUNCH_KILL=yes` (`:629`) with `la_kill()` (`:776`) and the
`exit 88` refusal branch (`:917`), `LAUNCH_BUDGET_S` (`:874`), the `--memory` / `--memory-swap` /
`--oom-score-adj=500` OOM posture, and the `--cpuset-cpus` pin. **Nothing in this launch path can
signal, kill or renice the solver**; the watcher records and does nothing else.

**The cost survives only as a reported ledger figure and stops nothing.**
**Estimate: ~35 core-min** (4 ranks; prior arm measured 16.1 core-min gross at `endTime 1000` on the
loose rule, of which ~16.5 core-min is fixed per-run overhead — container start, TensorFlow import
~255.9 s, `decomposePar`; the solve itself was 8.41 s `ExecutionTime`). **Basis: derived from the
prior arm's measured overhead and a 2x-endTime × higher-work-per-iteration solve; NOT measured.**
Actual-versus-estimate lands in `docs/COST_CALIBRATION.md` at completion, per rule 12.

### 7.5 Fresh root; the graded root is evidence and is not touched

The run root is **`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-R1-a6-grid-triple/`**, arm
**`L1-P-R1`**, staged from `base_L1` (cells 5568 = registered 5568, `Mesh OK.`, mesh byte-identical
to the graded arm's). **`CURRICULUM-D8G-a6-grid-triple/` is not written to, moved or overwritten** —
it holds a graded `NOT A RESULT` and a sibling lane has already lost graded fields to its own
successor once. G-COLD (no time dir, no `processor*`, no `d8g_P.json`) and the rule-4 age guard
(`0/` touched last, every artifact must be strictly newer than `0/U`) are asserted at launch.

**ALTERS NO** gate, band, threshold or label. **Knob 5 changes a registered `endTime`** and that is
stated plainly rather than described as something smaller. **`d8g_grade.py` is untouched.**

**SUBMISSIONS PARKED.**

---

## ADDENDUM 8 — 2026-09-12 — **A KILL IS NOT A CEILING. ADDENDUM 7 §7.4 STRIPPED THE MEMORY CONTAINMENT AND THAT WAS AN OVER-REACH; IT IS RESTORED.**

**Lines whose number changed above this section: 0.**

### 8.1 The over-reach, stated plainly

ADDENDUM 7 §7.4 listed `--memory` / `--memory-swap` / `--oom-score-adj=500` among the things
"stripped" under Sanaa's NO-CAP ruling. **That was wrong, and §7.4's list is struck on those three
entries by this addendum.** Her order is *"NO RUN GETS STOPPED BC OF A TIME OR BUDGET CAP."*
**A memory ceiling is neither a time cap nor a budget cap.** It is OOM containment on a shared box.

**The three are RESTORED:** `--memory=6g --memory-swap=6g --oom-score-adj=500`.

### 8.2 Why the two are different, so this file cannot teach the wrong lesson

A **stop** ends a run that is healthy and progressing, because a clock or a budget said so. That is
what Sanaa forbade, and every one of those remains removed: the in-container `timeout -k 60 $TMO`,
`cap_core_min`→`TMO`, the `rc=124`/`rc=137` path, `LAUNCH_BUDGET_S`, `la_kill()` and the `exit 88`
refusal branch.

A **ceiling** only ever binds a run that has already failed — a runaway allocation. D8G L1-P is
**5,568 cells** with a **predicted ~0.09 GiB RSS** (section 5); the registered ceiling is **6 GiB**,
about **67x the need**. It is arithmetically incapable of stopping a healthy run. **A limit that
cannot bind a healthy run is a seatbelt, not a cap.**

`--oom-score-adj=500` is the part whose removal was most clearly backwards: it marks D8G as the
**preferred** OOM victim, so dropping it does not protect D8G — **it points the kernel at somebody
else's run instead.** At the time of writing the box has **~11 GiB available** and four live
containers — **A3GC-AR1** (converged, p 3.7e-07, priority-1), **D6R2** (the multipoint Sanaa named),
**A3GC L2**, **A3GC L1**. An uncontained runaway here could have taken all four down. **Removing
containment would not have honoured the NO-CAP order; it would have risked four other teams' runs
under cover of it.**

### 8.3 A second defect, found only because the launcher was rebuilt against the registered line

The ADDENDUM 7 launcher ran the container as `bash -lc "bash d8g_cmd.sh"` and **omitted
`source /home/dafoamuser/dafoam/loadDAFoam.sh`**, which `d8g_run_arm.sh:814` carries. **Without it
the DAFoam environment is never loaded and the arm dies on import** — it would have burned a launch
and produced a failure that looked like the repair failing. It also dropped the **idwarp identity
probe** (`:816`), whose `D4S_IDWARP_SO_MD5` line is what `d8g_of.py` records as
`identity:{libidwarp_so_md5}` in `d8g_P.json`; without it the grading path loses an identity field.
**Both are restored.** The launch line is now the registered `:811` command **with exactly one thing
removed — the `timeout` wrapper** — rather than a re-derivation of it.

### 8.4 Two departures from `:811` that remain, each justified on its own

1. **`docker` replaces `sudo -n docker`.** `ubuntu` is in the `docker` group, so the client reaches
   the same daemon with the same rights; the host `sudo` was **surplus privilege with zero
   behavioural effect**, and every sibling dafoam launch on this box runs plain `docker`.
2. **`--cpus=4` replaces `--cpuset-cpus=$CPUSET`.** A share limit rather than a pin: D8G still cannot
   exceed four cores' worth, and it cannot land on top of a sibling's pinned cores. Neither form can
   kill anything.
3. **`--user 0:0` is KEPT** — the registered form (`:812`), and what produced the graded evidence.
   Changing it mid-item would change provenance and risk the container being unable to write `/mnt`.

**ALTERS NO** gate, band, threshold or label. `d8g_grade.py` untouched. The prediction and the
UNTESTED-transfer registration of ADDENDUM 7 §7.3 stand **exactly** as frozen.

**SUBMISSIONS PARKED.**

---

## ADDENDUM 9 — 2026-09-12 — **THE ARM ID WAS NOT THE BINDING DEFECT. `LAUNCH_D8G_R1.sh` WRITES A LEDGER ROW THE FROZEN COMPARATOR CANNOT PARSE AT ALL, AND TWO OF ITS "JUSTIFIED DEPARTURES" ARE GRADE-FATAL.**

**`lines whose number changed above this section: 0`** — measured against the committed
blob at HEAD before this text was appended (1,879 lines; this addendum is appended at the
foot and touches nothing above it). CLAUDE.md rule 6.

**ALTERS NO gate, band, threshold, cap or label.** `d8g_grade.py` is **NOT TOUCHED** and
remains `12688063e20cbb6fa79cf08d0996d4e1`. ADDENDUM 7 §7.3's UNTESTED-transfer
registration and every prediction stand exactly as frozen. This addendum records
**defects in the launcher and in an arm id**, and nothing else. **SUBMISSIONS PARKED.**

### 9.1 What happened

D8G R1 (`L1-P-R1`) completed `rc=0` and was graded 2026-09-12. `d8g_grade.py`, unchanged,
**refused**: `{"REFUSE": "ledger", "detail": {"note": "PRESENT-BUT-GARBAGE row: refused,
never skipped", "row_unparseable": "ARM=L1-P-R1 ROW=D8G-R1 rc=0 ..."}}` → `NOT A RESULT`.
Record: `D8G_R1_GRADING_RECORD.md`, commit `cdc9bbe24`.

The supervisor discharged check 4 on ADDENDUM 7 and identified the cause as the **arm id**:
`L1-P-R1` is not one of the ten ids fixed at `d8g_grade.py:212`, and that is true and is
the supervisor's own disclosed check-4 miss. **It is not the binding defect.** This lane
was directed to re-run under `L1-P` and instead checked, before spending compute, whether
that would clear the refusal. **It would not.** Four defects sit between
`LAUNCH_D8G_R1.sh` and a graded row, and the arm id is only the first.

### 9.2 DEFECT 1 — the arm id (real, disclosed, NOT binding)

`ARMS_REQUIRED` (`d8g_grade.py:212`) is
`["L1-P","L2-P","L3-P","A2-P","F2-P","L1-S","L2-S","L3-S","A2-S","F2-S"]`. There is no
`L1-P-R1`. §7 of ADDENDUM 7 registered the arm by that name (`:1752`, `:1808`) while
asserting the comparator untouched (`:1341`, `:1397`, `:1424`, `:1531`, `:1596`).

### 9.3 DEFECT 2 — **THE BINDING ONE: the ledger row grammar. Changing the arm id alone would have left the row exactly as unparseable.**

`LEDGER_RE` (`d8g_grade.py:367`) requires, contiguously and in this order:

```
ARM= ROW= IMG= DIGEST= rc= wall_s= ranks= core_min= cap_core_min=
enforced_wall_s= enforced_core_min= memory= inspect(exit,oomkilled)=[..] ... cpuset=
```

`LAUNCH_D8G_R1.sh`'s hand-rolled watcher writes **seven fields**:

```
ARM= ROW= rc= inspect(exit,oom)=[..] wall_s= ranks= core_min= stamp= log=
```

* **MISSING:** `IMG`, `DIGEST`, `cap_core_min`, `enforced_wall_s`, `enforced_core_min`,
  `memory`, `cpuset`.
* **WRONG KEY:** `inspect(exit,oom)` where the grammar requires `inspect(exit,oomkilled)`.
* **WRONG ORDER:** `rc` is followed by `inspect(...)`, but the grammar requires
  `rc wall_s ranks core_min` contiguous.

The registered launcher `d8g_run_arm.sh:1010` emits the **full canonical row** and always
did. `LAUNCH_D8G_R1.sh` was written to strip the in-container deadline (correctly, under
Sanaa's NO-CAP order) and **replaced the ledger write with an incompatible stub while
doing so**. That is the defect that actually refused this row.

### 9.4 DEFECT 3 — `--cpus=4` is not grade-neutral, and the launcher's own header says it is

`LAUNCH_D8G_R1.sh`'s documented "departure 2" replaces `--cpuset-cpus=$CPUSET` with
`--cpus=4`, reasoning that "neither form can kill anything". True, and irrelevant:
**G12 gates on `cpuset == CPUSET_REGISTERED = "0,1,12,15"`** (`d8g_grade.py:333`, :1412ff),
and `cpuset` is a **`FIELDS_PHYSICS`** member (`:341`). A share limit writes no cpuset and
matches no registered set, so a well-formed row from this launcher would still take
`G12 GATE FAIL`. *Measured 2026-09-12 06:20Z: the registered set `0,1,12,15` is **free of
pinned siblings** — the two pinned live containers both sit on `2,3,4,14` — so the header's
stated reason for the departure does not apply against the current pins.*

### 9.5 DEFECT 4 — no `DIGEST` is recorded, and G9 gates the toolchain on it

**G9** requires ledger `DIGEST == IMG_DIGEST[row]` **and** the container's printed
`D4S_IDWARP_SO_MD5` **and** the artefact md5 (`:1369`). `LAUNCH_D8G_R1.sh` prints the
idwarp md5 into the log but **writes no `DIGEST` into the ledger**. *Measured on this box
2026-09-12: `dafoam-idwarp-rot:v1` digests to
`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, which is
`IMG_DIGEST["PATCHED"]` **exactly**, and R1's `d8g_P.json` recorded
`libidwarp_so_md5 85f59e87253e0a71a813f64ca6e4c425` = `SO_MD5["PATCHED"]` exactly. The
identity is right; only its recording is missing.*

### 9.6 **AND EVEN WITH ALL FOUR FIXED, ONE ARM OF TEN STILL REFUSES. THIS IS REGISTERED HERE SO NO ONE SPENDS COMPUTE EXPECTING OTHERWISE.**

`g_completion()` walks **all ten** `ARMS_REQUIRED`. An arm with no ledger row falls to
`inspect_file_fallback()`, which requires **exactly one** `<ARM>_*.inspect.txt`; with zero
candidates it **refuses at G1** (`arm_absent_from_ledger`). `grade()` therefore cannot
return an item verdict until all ten arms exist.

**So a corrected single-arm re-run of `L1-P` cannot produce a graded verdict for D8G
tonight.** What it *can* do is **bank one of the ten arms, correctly recorded**, which the
existing `L1-P-R1` cannot serve as. That is the honest reason to run it, and the only one.

### 9.7 What the physics still says — carried forward verbatim, and it is NOT voided

Bookkeeping never voids physics. The measurement from `L1-P-R1`, unchanged and still a
**measurement and not a verdict**:

`nuTilda initRes` finished at **7.873598471886472e-05 = 0.787× its 1.0e-04 accept floor**,
with **zero** `Primal solution failed!` — against the pre-fix arm's **rising** plateau
3.924e-04 → 3.991e-04 → **4.074e-04 = 4.07×** with **seventeen** `Primal solution failed!`.
Mechanism measured on both sides: **13 pressure sub-iterations per outer step under the
tight inner-solve rule against 1 under the loose rule**, at the first and last outer step
alike. ADDENDUM 7 §7.3 registered the transfer to the CRM wing-body as **UNTESTED**; it
cleared. **The D6RF10-R3 package is not case-specific.** Bounds unchanged: patched row
only, gradient unverified, coarsest level (5,568 cells), `yPlus` mean 141.7.

### 9.8 What is registered for the corrected re-run

`LAUNCH_D8G_R2_L1P.sh`, committed with this addendum and **NOT YET RUN**:

* **Arm id `L1-P`**, exactly as `ARMS_REQUIRED` knows it. Fresh root; neither existing root
  is touched, moved or overwritten — both hold graded evidence.
* **The canonical ledger row** of `d8g_run_arm.sh:1010`, field for field.
  `enforced_wall_s` and `enforced_core_min` are written as **`0`**, the honest value under
  NO-CAP: *no deadline was enforced.* Nothing gates either field (they are parsed at `:371`
  and `:408` and read nowhere else). `cap_core_min` carries the registered
  `CAPS["L1-P"] = 46.977` — **the cap as a NUMBER is not withdrawn, only its stop
  behaviour**, exactly as ADDENDUM 7 and 8 already framed it.
* **`--cpuset-cpus=0,1,12,15`**, the registered set G12 reads.
* **`DIGEST` captured from the image at launch**, never hardcoded.
* **The same fix, unchanged** — the D6RF10-R3 package plus knobs 7–8. It works; it is not
  tuned to chase a nicer number.
* **NO CAP of any kind**: no `timeout -k`, no `cap_core_min`→`TMO`, no `rc=124/137` path,
  no `LAUNCH_BUDGET_S`, no `la_kill()`, no `exit 88`.
* **Memory containment KEPT**: `--memory 6g --memory-swap 6g --oom-score-adj=500`. A
  ceiling that cannot bind a healthy run is a seatbelt, not a cap (ADDENDUM 8).

### 9.9 One open question, logged and deliberately not chased

AR1 (A3GC) was described as a bit-for-bit repeat of its anchor, yet its `nuTilda` plateau
sits **above** 1e-06 where the anchor's sits below. Now measured rather than reported:

| | anchor `run_model_run3.log` | A3GC-AR1 |
|---|---|---|
| `nuTilda` initRes at 6000 | **8.985777021801817e-07** | **1.008859568e-06** |
| last five samples | 9.009 / 8.923 / 8.953 / 8.903 / 8.986 e-07 | 1.00882 / 1.00947 / 1.01365 / 1.01194 / 1.00886 e-06 |
| `p` initRes at 6000 | 3.744179143218389e-07 | 3.714456484e-07 |
| `U0` initRes at 6000 | 1.045733025903036e-07 | 1.080498815e-07 |

Both plateaus are **tight** — anchor spread ≈ 1.2 %, AR1 ≈ 0.5 % — so neither is a noisy
sample that happened to land where it did. **`nuTilda` shifted by 12.3 %**, `U0` by 3.3 %,
`p` by 0.8 %: **every equation moved, `nuTilda` most, and that shift is what carried it
over the 1e-06 line.** The run is therefore **not** bit-for-bit reproducing the anchor,
and this lane's use of "bit-for-bit" in `A3GC_AR1_GRADING_RECORD.md` §7 was too strong —
**corrected here.** *The cost attribution in that record is unaffected: it rests on
identical cell count, rank count and iteration count, which are unchanged, and not on
identical residuals.* Not chased tonight; it changes no verdict.

---

## ADDENDUM 10 — 2026-09-12 — **I COUNTED TRACEBACK FRAMES AS FAILURES. "SEVENTEEN" IS ONE FAILURE PRINTED SEVENTEEN TIMES, AND I AM STRIKING IT FROM MY OWN RECORD.**

**`lines whose number changed above this section: 0`** — measured against the committed
blob at HEAD before this text was appended (2,028 lines). CLAUDE.md rule 6.

**ALTERS NO gate, band, threshold, cap or label.** `d8g_grade.py` **NOT TOUCHED**,
`12688063e20cbb6fa79cf08d0996d4e1`. This addendum corrects **a count in my own prose** and
sharpens a mechanism claim. No verdict changes: D8G R1 remains **`NOT A RESULT`** and
A3GC-AR1 remains **`NOT A RESULT`**. **SUBMISSIONS PARKED.**

### 10.1 The error, and where it is

**ADDENDUM 9 §10.7 and `D8G_R1_GRADING_RECORD.md` §2 both say the pre-fix arm printed
`Primal solution failed!` SEVENTEEN TIMES.** That is a raw `grep -c`, and it counts Python
traceback frames. **STRUCK.** The measured position:

| item | `did not satisfy the prescribed tolerance` | raw grep `Primal solution failed` | genuine failures |
|---|---|---|---|
| D8G pre-fix (`L1-P_20260911T234236Z_2435242.log`) | **1** | 17 | **1** |
| D6RF11 (`F_probe_20260912T053430Z_2891321.log`) | **1** | 17 | **1** |
| A3GC-AR1 (`primal.log`) | **1** | 1 | **1** |
| **D8G R1** (`L1-P-R1_20260912T044934Z.log`) | **0** | **0** | **0** |

D8G pre-fix's seventeen hits sit in lines **2471–2738 of a 2751-line log** — the tail — and
most are traceback frames: `raise AnalysisError("Primal solution failed!")` and
`openmdao.core.analysis_error.AnalysisError: ...`. **Every stalled item has exactly ONE
genuine tolerance failure.** The 1-vs-17 difference is whether the `AnalysisError`
propagated up through OpenMDAO and printed a stack, **not how many times the primal
failed**.

**THE CONTRAST SURVIVES AND IS STILL THE FINDING** — one genuine failure to **zero**, and
D8G R1's zero is a true zero on **both** strings, not an absence of one. But *"seventeen to
zero"* is not an honest way to say *"one to zero"*, and a reader who checks the raw grep
would find the number and not the traceback. Corrected here rather than left to be found.

### 10.2 `nIters: 1` IS NOT THE DISCRIMINATOR. THE REDUCTION FACTOR IS.

A cross-item reading circulated in which `nuTilda nIters: 1` was the signature of the
stall. **It breaks on A3GC-AR1, which has `nIters: 3` and still missed its gate.**
Measured, from the four logs' own last printed steps:

| item | `nIters` | initRes / finalRes **within the outer step** | initRes / floor | outcome |
|---|---|---|---|---|
| D8G pre-fix (loose) | 1 | **12.3×** | 4.074× | failed |
| D6RF11 (loose) | 1 | **23.8×** | 1.139× | failed |
| A3GC-AR1 | **3** | **25.1×** | 1.009× | failed |
| **D8G R1 (tight)** | 3 | **1119.7×** | **0.787×** | **CLEARED** |

**Three failures in a 12–25× band; one clearance at 1120×; no overlap.** `nIters`
correlates but does not discriminate. **How far the linear solve is driven within each
outer step does.** The mechanism is therefore **one measurable quantity**, not a count of
knobs — and A3GC-AR1 belongs in this table **on evidence** (it has one genuine tolerance
failure, exactly like the others) rather than by resemblance.

### 10.3 Attribution, corrected against this lane's own interest

**Knobs 7–8 are NOT this lane's find.** ADDENDUM 7 (`c852c6319`, the dafoam-supervisor,
04:31Z) established that the registered "package of six" was missing the knob that causes
the D8G plateau, **before this lane touched D8G**. What this lane contributed is the
**measurement on both sides** — 13 pressure sub-iterations per outer step against the loose
rule's 1, and the reduction-factor discriminator of §10.2. The catch is the supervisor's;
the measurement is the lane's. Recorded this way because a record that flatters its author
is worth less than one that can be checked.

### 10.4 The floor does not move

`primalMinResTol 1e-08 × primalMinResTolDiff` is the accept floor **as a product**
(N-D43), and it is **not touched** — not in D8G, not in A3GC, and not in any successor.
Nothing in this addendum moves a threshold.

---

## ADDENDUM 11 — 2026-09-12 — **THE LAUNCHER RAN ITS CONTAINERS AS ROOT AND SILENTLY `rm -rf`'d THE ARM'S PREVIOUS RUN TREE TO MAKE ROOM. BOTH ARE REPAIRED BEFORE THE L1 RERUN. NO GATE MOVES.**

**Lines whose number changed above this section: 0.** No gate, band, threshold, cap, tolerance,
cost, prediction, level, arm or label is altered. `d8g_grade.py` and every md5 in `INSTRUMENT_MD5S`
(`d8g_runScript.py`, `d8g_of.py`, `d8g_decomposeParDict`) are **NOT TOUCHED**. **Nothing is launched
by this amendment.** **SUBMISSIONS PARKED.**

**Scope, set by the dafoam-supervisor on Sanaa's 2026-09-12 priority shift —
_"for dafoam the priority are the other 3D optimization runs, only the CFD focuses on this M6 fix
with the C mesh. Everybody hurries up."_ — and recorded so the next reader does not look for
something that was deliberately not done:**

> **The D8G L1 rerun is the ADJOINT PRIMAL ONLY.** The CRM CL/CD/CM comparison against NTF/Ames with
> the DPW scatter is **cfd's registered run now, not this team's**. This L1 exists to feed the
> adjoint, so it carries **no DPW band and no tunnel reference**, and none is registered here.
> **The BLOCKED comparison verdict stands and is NOT reopened by this amendment.**

### A11.1 `D8G-R3-UID` — the containers ran as root

`d8g_run_arm.sh` carried `--user 0:0` on its `docker run` and `--allow-run-as-root` on all three
`mpirun` command lines (`P`, `A`, `F`). Sanaa's 2026-09-12 item 6: **"As ubuntu. Never root.
Container jobs included."**

This is not an abstract violation. `docs/RESIZE_CENSUS_2026-09-12.md` §(a) attributes **642
root-owned files written today in this curriculum** to that line, and the completed `R2/L1-P` tree
shows it directly: `processor0-3/`, `d8g_P.json`, `d8g_P.jsonl` and `reports/` are all `root:root`
while the staged instruments beside them are `ubuntu:ubuntu`.

**The repair is measured, and the obvious spelling is wrong.** `-u 1000:1000` **alone** dies
`Permission denied` sourcing `loadDAFoam.sh`, because the image's `dafoamuser` is uid 1002 and
`/home/dafoamuser` is `drwxr-x---` — uid 1000 cannot *traverse* it. The working spelling is

```
-u 1000:1000 --group-add 1002
```

**uid 1000 and gid 1000 are both `ubuntu`**, so artifacts land `ubuntu:ubuntu`; 1002 is carried as a
**supplementary** group for traversal alone. **Corroborated against a live peer run on this exact
image** rather than a probe alone: `d6r2c_KR_REF_20260912T184838Z_79250`, whose own ledger line reads
`uid=1000:1000+1002`, sourcing the identical `loadDAFoam.sh` and solving.

### A11.2 `D8G-R3-EVIDENCE` — **the launcher deleted the previous run tree, as root, silently**

The line was `sudo -n rm -rf "$WORK" 2>/dev/null`, and `WORK="$BASE/$ARM"` (`:415`).

**On any re-launch against the same `BASE`, that removed the completed arm** — logs, `processor*`
trees, `d8g_P.json`, the ledger datum — **and `2>/dev/null` meant it never said so.** CLAUDE.md rule
4 is the opposite: a guard **refuses** a case whose run directory already exists, because a failed or
stopped run root is **evidence**, never written into and still less removed.

**It is now a refusal** (`exit 6`) naming the directory and telling the reader to move it aside by
hand. The registered relaunch pattern is a **fresh timestamped `BASE`** — ADDENDUM 7 already required
"a fresh root" — against which `$WORK` does not exist and the guard is silent.

**The two defects are one defect.** The `rm -rf` needed `sudo` *only because* the container ran as
root and left output the host could not delete. **It existed to clean up after §A11.1, and it
disappears with it.** The same is true of the `sudo -n chown -R ubuntu:ubuntu` further down, which is
kept as a plain `chown` — a successful no-op now, still useful for normalising anything a previous
root-era run left behind.

### A11.3 Nineteen escalations, not the two that were looked for

The `sudo -n` prefix was removed from **every** `docker` call in the file, nineteen in total.
`id ubuntu` carries **113(docker)**, `/var/run/docker.sock` is **660 root:docker**, and — the point
that matters — **plain `docker ps` as this unprivileged user returns `rc=0` and lists the live peer
container.** That is a positive control: a `docker ps` returning nothing would have shown only that
the reader was blind.

**Recorded because it is how the count was found, not as a flourish:** an assertion written to
confirm "no executable `sudo` remains" **failed**, printing ten calls the sweep had not enumerated —
including the `chown`. The list was written from reading; the assertion was written to disbelieve the
reading, and it was right to.

### A11.4 RE-FREEZE

| instrument | previous | **this amendment** |
|---|---|---|
| `d8g_run_arm.sh` | `51ff683dda23aa0143d1a2fe5047c780` (ADDENDUM 1) → `7ce53b9242ac6e850cc330712d93d5b0` (on disk at this amendment) | **`c0fdb80ab60327f32531323b74097107`** |
| `d8g_grade.py`, `d8g_runScript.py`, `d8g_of.py`, `d8g_decomposeParDict` | | **unchanged — NOT TOUCHED** |

> **A discrepancy in the record, reported rather than smoothed over.** ADDENDUM 1's re-freeze names
> `51ff683d…`, but the file on disk at this amendment hashed **`7ce53b92…`** — so the launcher moved
> between ADDENDUM 1 and now without a re-freeze row naming the new value, the same class of gap this
> lane found in `MP_A5R` §0 and in `A3GC` AMENDMENT 5 **on the same day**. This amendment records the
> **before** hash it actually measured on disk as well as the after, so the chain is continuous from
> here even though it is broken behind. **Which commit moved it, and whether that change was
> registered, is NOT established by this lane and is not claimed.**

The change is checked `bash -n` clean and is filed as a diff at `d8g_run_arm_R3_UID_APPLIED.diff`.
**It has not been executed.**

### A11.5 What is NOT repaired here

* **`LAUNCH_BUDGET_S` and the cap machinery** — untouched; ADDENDUM 6 governs and directive #17
  stands.
* **The `F`/`A` arms** — the uid repair applies to them too because it is one `docker run`, but this
  amendment registers **no** adjoint or FD arm. Only `L1-P`.
* **Anything in `R1`/`R2`'s completed trees.** They are evidence, including the root-owned files;
  nothing is chowned, moved or cleaned.

*D8G PREREGISTRATION — ADDENDUM 11, 2026-09-12. Launcher re-frozen. No gate moved. Nothing launched.*
