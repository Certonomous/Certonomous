# Curriculum D6R2C — PRE-REGISTRATION for Sanaa's AFTER-ITEMS 8 and 9

**Item id:** `D6R2C-AFTER`. Successor records to `D6R2C` arm `O_mp`, which is **closed at `GATE FAIL`**.
**Version 1.0 — DRAFT, NOT YET FROZEN.** Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`.
**This item has burned 0 core-min, started 0 containers and generated 0 meshes at the time of writing.**
It is frozen by the commit that introduces this file **together with its four instruments** (section 11).
**No container starts until that commit exists** (`CLAUDE.md` rule 2), and the supervisor's
non-delegable check is the commit, not this sentence.
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
**No frozen file is edited** (rule 6).

---

## 0. WHY THIS IS A NEW FILE AND NOT AN ADDENDUM TO `PREREGISTRATION.md`

`PREREGISTRATION.md` is frozen and **post-compute**. Rule 2: *"After first compute gates are closed;
changes land only as dated addenda that cannot alter a gate, threshold, cap or label."* Items 8 and 9
require **new gates with new thresholds**. An addendum introducing them would be exactly the move rule 2
forbids, whatever it called itself.

The frozen document says so itself. `PREREGISTRATION.md` section 10, last bullet:

> **Sanaa's D6R2 items 8, 9 and 10** — the shape/twist/trim decomposition, the fresh-mesh
> confirmation and the report — are **after** `O_mp` and are **registered separately**.

This file is that separate registration. It **cites** the frozen document and **changes nothing in it**:
`G1`–`G5`, the `G2` band, the `G3` tolerance `1.0e-3`, `KR-G1`–`KR-G4`, the section 5a tolerances and
every cap in section 8 stand exactly as frozen at `7f685867d`. The `O_mp` verdict of `GATE FAIL`
(ADDENDUM 3, A3.7) stands and **nothing in this item can move it**.

---

## 0a. THE INSTRUCTION, BYTE-EXACT

From `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`, Sanaa's own words:

> 8. Decomposition, two extra solves at matched lift: twist-only re-trimmed, and the full optimum;
>    table shows shape vs twist vs trim contributions before any percentage is quoted.
> 9. Fresh mesh on the final shape from the family script, re-solve at every condition, confirm the
>    weighted drag within band of the deformed-mesh value.

---

## 0b. THE INHERITED STATE, WITH ITS ARTEFACTS AND HASHES

Every number this item starts from, its artefact, and the hash that pins it. **A number whose artefact
is gone is not a result**, so the hashes are here and are checked by the instruments at run time.

| quantity | value | artefact | md5 of artefact |
|---|---|---|---|
| `J0` — baseline weighted mean `CD` | **`0.0306416314389976151`** | `O_mp/d6r2c_evals.jsonl`, `F` record `n = 2` | `2c0b8143caad198cd2e21d8047986aa3` |
| `Jf` — final weighted mean `CD`, as optimised | **`0.0230632595286777639`** | same file, `F` record `n = 88`, `fail = 0` | same |
| headline reduction as graded | **24.732273 %** | derived from the two above | — |
| final CL misses (`cl04`/`cl05`/`cl06`) | `5.539e-04` / **`1.210e-03`** / **`2.787e-03`** | `O_mp_GRADE.json` | `462e394b64825a8af719ac7a1645115b` |
| **baseline** CL misses | `1.814e-10` / `8.395e-12` / **`4.208e-08`** | `d6r2c_evals.jsonl` `n = 2` | `2c0b8143caad198cd2e21d8047986aa3` |
| x0 design vector, both spaces + scalers | `shape` ≡ 0 (96), `twist` ≡ 0 (7), `AoA` = 2.930384 / 4.326127 / 5.941267 deg | `O_mp/d6r2c_x0.json` | `b225fe7fdbd12eaa8a9b8a70835849c8` |
| base mesh | **38,304 cells**, 40,209 points, 1 wall patch `wing` of **1008 faces** | `base/constant/polyMesh` | see section 9a |
| FFD lattice | 6 × 2 × 8 | `base/FFD/wingFFD.xyz` | `f9435ee2ef54df0b08feae6e5127125d` |
| optimiser exit | `Number of Iterations....: 25`, `EXIT: Maximum Number of Iterations Exceeded.` | `O_mp/opt_IPOPT.txt` | `8673898b3e7794fc68f7c3689984b691` |
| `O_mp` spend | **672.933 core-min** at 4 ranks, 25 majors = **26.917 core-min/major** | `O_mp_GRADE.json` | `462e394b64825a8af719ac7a1645115b` |

### 0b.1 A CORRECTION TO A DESCRIPTIVE ROW OF THE FROZEN DOCUMENT — MEASURED, NOT ASSUMED

`PREREGISTRATION.md` section 1 records the mesh as **"9,504 cells, single grid"**. **That is the cell
count of ONE of four MPI subdomains, not of the mesh.** Measured 2026-09-13 by reading the mesh headers:

```
base/constant/polyMesh/owner.gz   nPoints:40209  nCells:38304
O_mp/mp04/processor0  9504   processor1  9600   processor2  9608   processor3  9592
9504 + 9600 + 9608 + 9592 = 38304   (exactly)
```

**The global mesh is 38,304 cells.** This is recorded here because item 9 registers a mesh and a
registration that named the wrong cell count would be unauditable. **It alters no gate, no threshold,
no cap and no label of `D6R2C`** — section 1's mesh row is descriptive, the mesh itself never changed,
and every `O_mp` number stands. It is reported to `dafoam-supervisor` as a defect in the frozen
document's prose, to be disclosed there by that document's own amendment discipline, **not by this
file**, which has no authority over it.

---

## 1. THE DECOMPOSITION — WHAT IS BEING SEPARATED, AND FROM WHAT

Write `J(s, t, a)` for the weighted mean drag coefficient at shape DVs `s` (96), twist DVs `t` (7) and
the angle-of-attack trim vector `a` (the second component of `patchV_cl04/05/06`; the first, `U`, is
pinned at `U0 = 100 m/s` and is never a free variable). Write `A(s, t)` for **the AoA vector that holds
`CL_i = target_i` at geometry `(s, t)`** — the trim operator, realised by `optFuncs.findFeasibleDesign`,
the same routine that produced `x0`.

| symbol | state | `shape` | `twist` | `AoA` | measured how |
|---|---|---|---|---|---|
| `J_B` | baseline, trimmed | `0` (96) | `0` (7) | `A(0, 0)` | **arm `DEC`, step 1** |
| `J_T` | **twist-only, re-trimmed** | `0` (96) | `t*` | `A(0, t*)` | **arm `DEC`, step 2** |
| `J_S` | shape-only, re-trimmed | `s*` | `0` (7) | `A(s*, 0)` | **arm `DEC`, step 3** |
| `J_F` | **the full optimum, re-trimmed** | `s*` | `t*` | `A(s*, t*)` | **arm `DEC`, step 4** |
| `J_opt` | the optimiser's own final state | `s*` | `t*` | `a*` | **arm `DEC`, step 5**, against `Jf` |

`s*`, `t*` and `a*` are read from `O_mp/d6r2c_evals.jsonl`, `F` record `n = 88`, **in the
driver-scaled space that file records**, and set through the driver in that same space. ADDENDUM 1 of
the frozen document is the reason this sentence names a space: comparing a driver-scaled vector against
a physical one is the defect that produced `worst_abs_diff = 90.0` and cost a `NOT A RESULT`.
`d6r2c_decomp.py` prints the space it set and the scalers it read from OpenMDAO's own metadata, never
re-typed. Their values, for the record:

- `t*` (physical, degrees): `-3.496918108, -1.673467014, 0.854001249, 2.755442752, -1.931901985, -2.604705886, -2.603267647`
- `a*` (physical, degrees): `cl04 0.577498771`, `cl05 1.771663378`, `cl06 3.038318150`
  (baseline `A(0,0)`: `2.930383372`, `4.326126896`, `5.941267044`)
- `s*` (physical FFD displacement): 96 components, `min -0.278571135343`, `max +0.278571135343`,
  bounds `[-1, 1]`. **Not transcribed here** — a 96-number transcription is a second copy that can
  drift (L-221/L-222). The vector is read from the md5-pinned artefact and the instrument refuses
  (exit 2) if that md5 does not match `2c0b8143caad198cd2e21d8047986aa3`.

### 1a. WHY THERE ARE FIVE STEPS WHEN SANAA NAMED TWO SOLVES

Her two are `J_T` (twist-only re-trimmed) and `J_F` (the full optimum, **also at matched lift** — the
phrase "at matched lift" governs both items in her sentence). `J_B`, `J_S` and `J_opt` are added, and
each earns its place:

- **`J_B`** because the decomposition is a difference from the baseline and the baseline's
  **per-condition `CD`** does not exist anywhere on disk. `d6r2c_evals.jsonl` records `obj.J`, the three
  `CL`s, `thickcon` and `volcon` — **it does not record `CD04`, `CD05`, `CD06`**. Sanaa's table is a
  per-condition drag table, so those three numbers must be produced, and the only honest way to produce
  them is to re-solve the state that produced `J0` **and prove it reproduces `J0`**.
- **`J_S`** because without it the "shape vs twist" split is **an ordering, not a measurement** — see
  section 3 (`D4`) and the interaction term.
- **`J_opt`** because it is the **reproduction control** that makes every other number in the table
  trustworthy, and because `Δ_trim` cannot be computed without it.

**`J_B` and `J_opt` are therefore both reproduction controls and both are gated** (`D2`). They sit at
the two ends of the sequence, which is deliberate: see section 4a.

### 1b. THE UN-HELD LIFT AT THE OPTIMUM, AND HOW IT IS HANDLED — STATED BEFORE THE TABLE EXISTS

**The optimiser's final state is NOT at matched lift.** `O_mp` finished with CL misses
`5.539e-04 / 1.210e-03 / 2.787e-03` against the registered `1.0e-3`. **That is why `G3` missed and why
the item is `GATE FAIL`.** A decomposition that silently compared `J_opt` against `J_B` would be
comparing a state that holds lift against one that does not, and would charge the resulting drag credit
to the wing's geometry. **It is not a geometric gain. It is lift the optimiser did not deliver.**

It is therefore given its own named term and is never folded into shape or twist:

```
Δ_trim   ≡  J_opt − J_F        the drag credit taken by NOT holding lift
Δ_shape  +  Δ_twist            the geometric gain AT MATCHED LIFT  ( = J_F − J_B )
Δ_shape  +  Δ_twist + Δ_trim   =  J_opt − J_B  =  Jf − J0          (identity; gate D3)
```

**AND THE CONSEQUENCE, REGISTERED IN ADVANCE SO IT CANNOT BE ARGUED ABOUT AFTERWARDS:**

> **The 24.732 % is NOT the number the shape/twist split applies to.** It is the reduction at *unmatched*
> lift. The number the split applies to is the **matched-lift reduction `(J_B − J_F) / J_B`**, which is
> not yet measured. Every percentage this item emits states which of the two it is a percentage of, and
> `d6r2c_after_grade.py` **refuses (exit 2)** to write a share field whose denominator is not named in
> the same record.

`Δ_trim` may come out either sign and both are registered outcomes: negative (the optimiser gained drag
by shedding lift, the expected case) or positive (holding lift at the optimum *reduces* drag, which
would be a finding about the constraint, reported as one).

### 1c. "BEFORE ANY PERCENTAGE IS QUOTED" — MECHANICAL, NOT PROSE

Sanaa's clause is binding and is enforced by the instrument, not by discipline:

- `d6r2c_after_grade.py` writes the **absolute table first** — per condition `CD` (and in drag counts,
  `1 count = 1.0e-4`), `CL`, `CL` miss, `AoA`, and the weighted `J`, for all five states — into
  `DECOMP_TABLE.json` and `DECOMP_TABLE.md`.
- **No percentage field is written at all** unless every cell of that table is present and finite and
  every arm passed `D1`. If any cell is missing, the percentage fields are **absent from the record**
  (not null, not zero — **absent**) and the grader exits 2 with `REFUSE_NO_TABLE`.
- A selftest control drives exactly this: a table with one hole must produce a record with **no**
  percentage keys. Rule 3's discipline applied to a clause instead of a number.

---

## 2. ITEM 9 — THE FRESH MESH

### 2a. THE FAMILY SCRIPT, NAMED BY ABSOLUTE PATH, AND ITS IDENTITY PROVED RATHER THAN ASSERTED

**The family script is `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing/preProcessing.sh`**
(md5 `8ab23290ae618ff6f8233c428ad7e980`), whose mesh step is
**`/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing/genWingMesh.py`**
(md5 `dab5e959187ab2e2bfb4e2c0ded0feb6`) — a **pyHyp hyperbolic extrusion** from a CGNS surface mesh,
`N = 39` layers, `s0 = 1.0e-3`, `marchDist = 300.0`, `cMax = 0.1`, followed by `plot3dToFoam -noBlank`,
`autoPatch 60`, `createPatch -overwrite`, `renumberMesh -overwrite`.

**This is not an inference from a filename.** It is proved bitwise. The script was executed on
2026-07-28 in `/home/ubuntu/certonomous-runs/A2-mach-wing/` (its `logMeshGeneration.txt` and
`preproc_stdout.log` are on disk), and every `polyMesh` file it produced is **byte-identical** to this
item's `base/constant/polyMesh`:

| file | md5 (both) |
|---|---|
| `points.gz` | `0fb1935a9b8781b73ac4ccb136e3ec68` |
| `faces.gz` | `0a94bba01e37c8587676b056c7a2bb05` |
| `owner.gz` | `16febaf5dfa4137ef7fb1ec4a3659ec5` |
| `neighbour.gz` | `803a7546fd09fcbd673ef1ed52b4fcd6` |
| `boundary` | `c8d1891562dc7a1d5822cd6b94c2c2d4` |

**Its inputs are on the box and NOTHING IS DOWNLOADED.** `preProcessing.sh` carries a `wget` branch
guarded by `if [ -f "mdolab_wing_surface_mesh.cgns.tar.gz" ]`. The file is present at
`/home/ubuntu/certonomous-runs/A2-mach-wing/mdolab_wing_surface_mesh.cgns.tar.gz`, the extracted
`mdolab_wing_surface_mesh.cgns` is present (md5 `3fad5f009b427cd8cd6fa13e979bf033`) and the once-coarsened
`surfaceMesh.cgns` is present (md5 `3050ea454c2d0304bafa2c1a80c53b76`, 114,688 bytes, **1008 faces,
1031 unique nodes**). `d6r2c_freshmesh.py` **stages these as inputs and asserts the wget branch did not
fire** — it refuses (exit 2) if any network fetch is attempted or if the staged md5 does not match.

**The toolchain exists in the pinned image — measured, not assumed.** Probed 2026-09-13 by listing
`site-packages` inside `dafoam-idwarp-rot:v1@sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`
(a `ls` with no solver and no compute): `pyhyp`, `pygeo`, `idwarp`, `cgnsutilities`, `prefoil`,
`baseclasses`, `pyspline` all **PRESENT**, and the `cgns_utils` CLI is on `PATH`. **Item 9 is not
`BLOCKED`.** Had any of these been absent, this section would have said so and the item would have been
registered `BLOCKED` rather than improvised around.

### 2b. HOW THE FINAL SHAPE GETS ONTO A FRESHLY GENERATED MESH — NOT THE WARPED ONE

The optimiser's mesh is the **base volume mesh warped by IDWarp**. A fresh mesh must be **extruded**,
not warped, and it must be extruded from the **deformed surface**. The registered procedure, in order:

1. Stage `surfaceMesh.cgns` (the family script's own once-coarsened surface) as an **input**, before the
   age datum, md5-asserted.
2. Build a `pygeo.DVGeometry` on **`FFD/wingFFD.xyz`** with **exactly** the run script's DV definitions —
   `nom_addRefAxis(xFraction=0.25, alignIndex="k")`, the same `twist` function over `nRefAxPts − 1`
   points with the root twist not free, the same local `shape` DV over the same `pointSelect` — and add
   the CGNS surface nodes as a point set.
3. Set `shape = s*` and `twist = t*` **in the driver-scaled space, converted by the scalers recorded in
   `d6r2c_x0.json`**, and update the point set.
4. Write the deformed nodes back into a copy of the CGNS file (`cgnsutilities`), producing
   `surfaceMesh_final.cgns`.
5. Run **the family script's own `genWingMesh.py` unmodified** on that file, then `plot3dToFoam -noBlank`,
   `autoPatch 60`, `createPatch -overwrite`, `renumberMesh -overwrite` — the family script's own sequence.
6. `checkMesh` on the result; the report is captured whole and **is not a gate** (see `H2`).

**`genWingMesh.py` is executed as the family's own bytes**, md5-asserted before it runs. Its hard-coded
`fileName = "surfaceMesh.cgns"` is satisfied by staging `surfaceMesh_final.cgns` **under that name in the
mesh working directory**, so the script itself is never edited (rule 6) and never sees a modified
option. The instrument prints the md5 of the file it staged under that name, so a reader can tell which
surface was extruded.

### 2c. THE CHECK THAT THE FRESH MESH IS ACTUALLY THE FINAL SHAPE — GATE `H1`

Everything above could run end to end and produce a beautiful mesh **of the wrong wing**. `H1` is the
check that it did not, and it is falsifiable:

- The deformed CGNS surface nodes (step 3) and the **IDWarp-deformed OpenFOAM `wing` wall-patch points
  at the final design** are the same physical surface reached by two independent deformation paths.
- `H1` requires a **bijection**: every deformed CGNS node has exactly one deformed OpenFOAM wall point
  within `SHAPE_MATCH_TOL = 1.0e-8` (absolute, metres) and the matching is one-to-one.
- **The counts are measured in advance**: the `wing` patch has **1008 faces** and the CGNS surface has
  **1008 faces / 1031 unique nodes**, so the comparison is known to be possible before the run. A count
  mismatch at run time is `NOT A RESULT` with both counts printed — **never** a silent fallback to a
  Hausdorff distance.
- **Basis for `1.0e-8`:** coordinates on this wing are `O(10)` (the FFD spans `x ∈ [1.48, 9.20]`), so
  double-precision round-off through two deformation paths is `O(1e-11)` absolute — three decades below
  the tolerance. The physical scale it must catch is the shape change itself, `max|s*| = 0.2786` in FFD
  displacement units — **seven decades above** the tolerance. There is no ambiguous middle.

### 2d. THE BAND — REGISTERED FIRST, AND WHAT IT RESTS ON, STATED PLAINLY

**THERE IS NO PRIOR MESH-SENSITIVITY EVIDENCE IN THIS FAMILY.** Searched and not found: no grid triple,
no grid pair, no observed order, no GCI anywhere in the A2 MACH-wing line. The frozen document says as
much and says it twice — section 4 (*"A Roache triple is NOT claimed and no GCI is quoted. Single grid"*)
and section 10 (*"It is not a grid study. Single mesh, disclosed."*). **So the band cannot be justified
from a measured mesh sensitivity, and this registration does not pretend it can.**

**THE BAND RESTS ON DECISION RELEVANCE, AND ITS DERIVATION IS EXACT ARITHMETIC ON TWO MEASURED NUMBERS.**

> The claim at risk is *"a 24.732 % reduction in the weighted mean drag coefficient"*. The fresh-mesh
> confirmation is worth running only if it can move that claim. **One percentage point of reduction** is
> the smallest movement that changes what may be said about it (24.7 % → 23.7 % or 25.7 % is a different
> sentence; 24.73 % → 24.70 % is not).
>
> ```
> FM_BAND_ABS = 0.01 × J0 = 0.01 × 0.0306416314389976151 = 3.064163144e-04   (absolute, on J)
>             = 1.328591e-02 relative to Jf = 0.0230632595286777639
> ```
>
> **`FM_BAND_ABS = 3.064163144e-04` is the gate.** The relative form is printed beside it and is not the
> gate — the absolute form is primary because *its derivation is exact*, not rounded.

**This is a DECLARED decision-relevance band, and it is labelled as such everywhere it appears.** It is
**not** a measured discretisation uncertainty, it is **not** a GCI, and no reader may present it as one.
Registering a number honestly labelled is the alternative to registering a number chosen after seeing
the answer, which is the only thing a band is for.

**The evidence the lab lacks is scheduled, not hand-waved.** Arm `FM_L2` (section 5, **registered, NOT
run by this registration**) generates one further `cgns_utils coarsen` level from the same family script
and solves it, giving this family its **first** level-to-level drag sensitivity. It is **REPORTED, NEVER
GATED**, it is **not** a Roache triple, no GCI is quoted from it and no observed order is claimed
(rule 5, and section 10 of the frozen document). **It cannot be used to widen `FM_BAND_ABS`** — that
prohibition is registered here, before either number exists.

### 2e. WHICH "DEFORMED-MESH VALUE", AND WHY — REGISTERED BEFORE THE SOLVE

Her phrase is *"within band of the deformed-mesh value"*. Two comparisons are available and they answer
different questions:

- **(i) SAME DVs, INCLUDING `a*` — NO RE-TRIM.** `J_fresh(s*, t*, a*)` against `Jf = 0.0230632595286777639`.
  Identical design vector, identical flow conditions; **the only thing that differs is the mesh.**
- **(ii) Re-trimmed on the fresh mesh** against `J_F` from item 8.

**(i) IS THE GATED COMPARISON.** Item 9 is a question about the *mesh*; re-trimming would let a lift
change ride along inside the answer and there would be no way afterwards to say which part was mesh.
**(ii) is solved and REPORTED beside it** — it is needed anyway to connect item 9's arm to item 8's
table, and a disagreement between (i) and (ii) is itself informative.

The three `CL`s on the fresh mesh at `a*` will not equal the targets; they did not on the deformed mesh
either. They are **REPORTED against the deformed-mesh `CL`s, not gated**, with one registered trigger:
`|CL_fresh,i − CL_deformed,i| > 5.0e-3` for any `i` is **named in the record as a finding** (5.0e-3 is
five times the `G3` tolerance the optimiser was working against — declared, not measured).

### 2f. WHAT A MISS MEANS — DECIDED IN ADVANCE

**A fresh-mesh weighted drag outside the band is a `GATE FAIL` on item 9. It does NOT invalidate the
24.732 %.** The reasons are registered now, so they cannot be assembled later to suit the number:

1. The 24.732 % is a **measurement on the deformed mesh, already graded** against a gate (`G2`) frozen
   before that run started. Item 9 is a **separate registered gate** with its own band. A `GATE FAIL`
   here is a finding about **discretisation**, which the frozen document already discloses as an
   **unquantified** channel (*"single mesh, disclosed"*). A miss **quantifies** a disclosed uncertainty;
   it does not retract a measurement.
2. **But it binds what may be said, and that is registered too.** On a `GATE FAIL` at `H3`:
   - the 24.732 % **may not be quoted anywhere without the fresh-mesh number and the measured
     discrepancy printed beside it** — `d6r2c_after_grade.py` writes
     `headline_quotation_constraint: "MUST_CITE_FRESH_MESH_DISCREPANCY"` into the record, and
   - the certificate's discretisation channel carries **the measured discrepancy** instead of
     "band pending" (Sanaa's item 10: *"certificate slot honest (single grid, band pending)"* — a miss
     is how "band pending" becomes a number).
3. **The ONE case where it does bite the headline, registered explicitly.** If
   **`J_fresh ≥ 0.90 × J0 = 2.757747e-02`** — i.e. the fresh mesh does not clear the frozen `G2` bar of a
   10 % reduction — then the `G2` conclusion is **contradicted on a fresh mesh**. That is not absorbed:
   `d6r2c_after_grade.py` writes `g2_contradicted_on_fresh_mesh: true`, the item is `GATE FAIL`, **and
   it is escalated to `dafoam-supervisor` as a defect against the `O_mp` record.** Retiring or moving
   `G2` is not this lane's call and is not this item's call (`CLAUDE.md`, Reserved to Sanaa).

---

## 3. THE GATES FOR ITEM 8, FROZEN (arm `DEC`)

Graded by **`d6r2c_after_grade.py --item 8`**, reading `DEC/d6r2c_decomp.jsonl`, `DEC/`'s own log, the
arm directory and the md5-pinned inherited artefacts of section 0b — **all after the container exits.**

- **`D1` — EVERY ARM IS AT MATCHED LIFT.** For each of `J_B`, `J_T`, `J_S`, `J_F`:
  **`max_i |CL_i − target_i| ≤ TRIM_TOL = 1.0e-6`** over `cl04 / cl05 / cl06`.
  `J_opt` is **exempt by construction** — it is the un-trimmed control and its misses are the inherited
  `5.539e-04 / 1.210e-03 / 2.787e-03`, reproduced under `D2`.
- **`D2` — THE INSTRUMENT REPRODUCES THE RUN IT IS DECOMPOSING.** Both ends of the sequence:
  - `|J_B − J0| / J0 ≤ REPRO_TOL = 1.0e-5` **and** `max_i |CL_i(J_B) − target_i| ≤ 1.0e-6`;
  - `|J_opt − Jf| / Jf ≤ REPRO_TOL = 1.0e-5` **and** each `CL_i(J_opt)` within `1.0e-6` **absolute** of
    the inherited `n = 88` value.
- **`D3` — THE ACCOUNTING CLOSES.**
  `|(Δ_shape + Δ_twist + Δ_trim) − (J_opt − J_B)| ≤ CLOSE_TOL = 1.0e-12` (absolute, on `J`).
  **This is an arithmetic identity and its band is a floating-point band. It is registered as such and
  is NOT presented as a physics test.** What it tests is that every term in the table came from the same
  instrument, the same weights and the same records — a term computed from a stale or differently
  weighted `J` breaks it.
- **`D4` — THE SPLIT IS ORDER-INDEPENDENT ENOUGH TO BE CALLED A SPLIT.** With
  ```
  Δ_twist⁽¹⁾ = J_T − J_B     Δ_shape⁽¹⁾ = J_F − J_T      (order: twist first)
  Δ_shape⁽²⁾ = J_S − J_B     Δ_twist⁽²⁾ = J_F − J_S      (order: shape first)
  I = Δ_shape⁽¹⁾ − Δ_shape⁽²⁾ = J_F + J_B − J_T − J_S = −(Δ_twist⁽¹⁾ − Δ_twist⁽²⁾)
  ```
  **`D4` PASSES iff `|I| ≤ INTERACT_TOL × |J_F − J_B|` with `INTERACT_TOL = 0.10`.**
  - **PASS** → the symmetric split `Δ_shape = ½(Δ_shape⁽¹⁾+Δ_shape⁽²⁾)`,
    `Δ_twist = ½(Δ_twist⁽¹⁾+Δ_twist⁽²⁾)` (which sums to `J_F − J_B` exactly) **may be quoted as a split**,
    with both orderings and `I` printed beside it.
  - **FAIL** → **`GATE FAIL`**, and the percentages are emitted **only as order-dependent pairs**, both
    orderings printed, `I` named, and the record carries
    `split_is_order_dependent: true`. **The percentages are not suppressed — they are qualified**, because
    Sanaa asked for the contributions and an honest order-dependent answer is an answer.
  - **Basis for `0.10`: DECLARED, NOT MEASURED**, and labelled so in the record. It is the level at which
    *"shape contributed X and twist contributed Y"* stops describing the wing and starts describing the
    order the analyst chose. No measurement in this family bounds it, and inventing one would be worse
    than declaring this.
- **`D5` — THE TABLE EXISTS BEFORE ANY PERCENTAGE.** Section 1c, enforced mechanically. `D5` is a
  **refusal, not a gate**: a violation exits 2 with `REFUSE_NO_TABLE` and no verdict is written at all.
- **`D6` — COMPLETION AND HYGIENE.** `rc = 0`; every one of the five steps present in
  `d6r2c_decomp.jsonl` with `fail = 0` and finite `obj.J` and finite `CL`s; each condition's primal
  converged to `primalMinResTol = 1.0e-8` or its residual recorded and the step graded `NOT A RESULT`;
  every artefact strictly newer than the arm's own age datum (`0/U`); **zero** files under the arm
  directory newer than the datum owned by uid 0 or gid 0.

**LABELS (item 8).** `PASS` = `D1∧D2∧D3∧D4∧D6`. `GATE FAIL` = `D1∧D2∧D3∧D6` hold and `D4` misses, with
`I`, both orderings and every absolute number printed beside it. `NOT A RESULT` = `D1`, `D2`, `D3` or
`D6` fails, or the section 8 cap is crossed. `D5` produces a refusal (exit 2), not a label.
**No other label, no synonyms** (rule 1). **No Roache triple is claimed and no GCI is quoted** — single
grid throughout item 8 (rule 5 does not apply and nothing here will be dressed as grid convergence).

### 3a. IF AN ARM CANNOT BE TRIMMED TO `TRIM_TOL`

`findFeasibleDesign` gets at most **`TRIM_MAX_EVALS = 40`** primal evaluations per state. If a state has
not reached `TRIM_TOL` by then, **that state is `NOT A RESULT`, the whole decomposition table is
`NOT A RESULT`, and the achieved misses and the evaluation count are printed.**

**`TRIM_TOL` IS NEVER WIDENED. THAT IS A REGISTERED PROHIBITION, NOT A PREFERENCE.** Widening the trim
tolerance after seeing a miss would be choosing the comparison to fit the answer, on an item whose whole
subject is that the optimiser did not hold lift.

### 3b. WHY `TRIM_TOL = 1.0e-6` AND NOT `1.0e-3`, AND NOT `1.0e-8`

- **Not `1.0e-3`** (the `G3` gate): that is the slop the optimiser itself left, and it is exactly the
  quantity being separated out as `Δ_trim`. Allowing the same slop *inside* the matched-lift arms would
  let a piece of `Δ_trim` leak into `Δ_shape` and `Δ_twist` — it would defeat the item.
- **Not `1.0e-8`**: that is below what the machinery has been shown to reach.
- **`1.0e-6` is a bar this exact instrument is MEASURED to clear.** `findFeasibleDesign`, on this case, on
  this mesh, at `x0`, achieved **`max miss = 4.208e-08`** (`d6r2c_evals.jsonl` `n = 2`, cl06) — **24×
  tighter than the tolerance registered here.** It is two decades looser than the achieved value (so it
  is not a bar written to be failed) and three decades tighter than `G3` (so it cannot hide trim slack).
- **Verified how:** `d6r2c_after_grade.py` re-reads each arm's converged `CL`s **from the arm's own
  record on disk**, computes the misses itself, and refuses to take the producer's word for them. The
  producer's own claimed miss is read too and a disagreement between the two is a refusal (exit 2).

### 3c. THE `TRIM_TOL` BAND EDGE IS NOT REPRESENTABLE — FOUND BY THE CONTROLS, NOT ACCOMMODATED

Driving the `D1` boundary control produced a property of the **registration**, not of the instrument,
and it is recorded because a reader is entitled to it:

> For the registered targets there is **no IEEE double `v` with `|v − target| == 1.0e-6` exactly.** The
> attainable misses step by ~`1.1e-16` and straddle the literal without landing on it — **and they do
> so differently per target.** `target + 1.0e-6` evaluates to a miss of `9.999999999732e-07` at
> `target = 0.4` (**inside** the band) but `1.000000000029e-06` at `0.5` and `0.6` (**outside** it, and
> correctly `NOT A RESULT` under `D1`'s `≤`).

**No tolerance was added to `D1` to make the edge reachable.** The control was rewritten to drive the
boundary from the **attainable** values on both sides, one ulp apart, on the coarsest-ulp target
(`cl06`). This is the same property `PREREGISTRATION.md` ADDENDUM 3 §A3.2 item 1 recorded for `G3`'s
`1.0e-3` edge, and it is handled the same way here: **the band is not moved to suit the arithmetic.**

The second control finding, recorded rather than quietly fixed: the `J` cross-check threshold is
`1.0e-12` **absolute**, and a first-draft control perturbed the producer's `J` by `1e-14` **relative**
— on `J ≈ 0.025` that is `2.5e-16` absolute, **below** the threshold, so the control correctly did not
fire. **A control that fires for the wrong reason is worse than no control**, so both sides of the
absolute threshold are now driven (`1e-11` must refuse, `1e-13` must not).


---

## 4. THE GATES FOR ITEM 9, FROZEN (arm `FM`)

Graded by **`d6r2c_after_grade.py --item 9`**, reading `FM/d6r2c_freshmesh.json`, `FM/`'s own log, the
generated mesh and `checkMesh` report, and the md5-pinned inherited artefacts — all after the container
exits.

- **`H1` — THE FRESH MESH IS THE FINAL SHAPE.** Section 2c: a bijection between the deformed CGNS surface
  nodes and the IDWarp-deformed OpenFOAM `wing` wall points within `SHAPE_MATCH_TOL = 1.0e-8` absolute.
  Node/face count mismatch, a non-bijective matching, or any node unmatched → **`NOT A RESULT`**, both
  counts and the worst distance printed.
- **`H2` — THE MESH IS FRESH, AND FROM THE FAMILY SCRIPT.** `rc = 0` for the mesh step; `genWingMesh.py`
  executed at md5 `dab5e959187ab2e2bfb4e2c0ded0feb6` **and the md5 asserted before it ran**; the staged
  surface md5 printed; the generated `constant/polyMesh` strictly newer than the arm's age datum;
  `FM/constant/polyMesh/points.gz` **differs from** `base/constant/polyMesh/points.gz`
  (`0fb1935a9b8781b73ac4ccb136e3ec68`) — *a "fresh" mesh identical to the base mesh means the deformation
  never reached the mesher*; the global cell count recorded; `checkMesh` run and its report captured whole.
  **`checkMesh` output is RECORDED, NOT GATED** — this registration fixes no mesh-quality threshold and
  will not invent one after the fact. `checkMesh`'s own trip levels are `checkMesh`'s, not this item's.
- **`H3` — THE BAND.** **`|J_fresh(s*, t*, a*) − Jf| ≤ FM_BAND_ABS = 3.064163144e-04`**, with
  `Jf = 0.0230632595286777639`. Comparison (i) of section 2e. The relative form `1.328591e-02` is printed
  beside it and is not the gate. **Reported, not gated:** per-condition `CD`, `CL` and `CL` miss on the
  fresh mesh against the deformed mesh; the re-trimmed fresh-mesh value against `J_F`; and the
  `|ΔCL| > 5.0e-3` finding trigger of section 2e.
- **`H4` — COMPLETION AND HYGIENE.** `rc = 0` for the mesh step and for all three conditions' primals;
  each primal converged to `primalMinResTol = 1.0e-8` or its final residual recorded and the arm graded
  `NOT A RESULT`; all artefacts strictly newer than the arm's own age datum (`0/U`); **zero** files under
  the arm directory newer than the datum owned by uid 0 or gid 0; the container ran as uid 1000.

**LABELS (item 9).** `PASS` = `H1∧H2∧H3∧H4`. `GATE FAIL` = `H1∧H2∧H4` hold and `H3` misses, with
`J_fresh`, `Jf`, the difference, the band and the per-condition table printed beside it.
`NOT A RESULT` = `H1`, `H2` or `H4` fails, or the section 8 cap is crossed.
**`H3` is a two-mesh comparison and is NOT a grid convergence study.** No Roache triple, no GCI, no
observed order, at any point, from anything in item 9.

### 4a. THE ARMS RUN AS ONE SEQUENCE IN ONE CONTAINER, AND WHY THAT IS SAFE — REGISTERED IN ADVANCE

`DEC`'s five states run **in one container, in the registered order `B → T → S → F → O`**, cold from
`0.orig`, because the cold preamble (container start, three case copies, three `decomposePar`, the first
primal from uniform fields) is **measured at 2990.166 s wall** (`d6r2c_evals.jsonl` `n = 2`,
`wall_since_start_s`) and paying it five times would cost ~800 core-min to buy nothing.

**The consequence, named rather than hidden:** each state after the first is warm-started from the
previous state's converged fields, so its primal reaches `primalMinResTol = 1.0e-8` **from a different
initial state** than a cold solve would. This is the same reasoning the frozen document registered in
section 5a (*"Both are converged to `primalMinResTol = 1.0e-8`, so they agree to that residual level and
not to the last bit"*), and it is the reason `D2` exists **at both ends of the sequence**:

- `J_B` is step **1** — the *coldest* state, closest to how `J0` was produced.
- `J_opt` is step **5** — the state with the *most* warm-start drift behind it.

**If warm starting mattered at the `1.0e-5` level, `D2` would fail at the far end.** A `D2` pass is
therefore a measurement that it does not, not an assumption that it does not. **A `D2` failure is
`NOT A RESULT` and the fallback — five cold arms — is a NEW registration, not a silent re-run.**

---

## 5. ARMS

| arm | what it is | ranks | run under this registration? |
|---|---|---|---|
| `DEC` | the five decomposition states in one container, order `B → T → S → F → O` | 4 | **YES** |
| `FM` | fresh mesh from the family script on the final shape, then all three conditions | 4 | **YES** |
| `FM_L2` | one further `cgns_utils coarsen` level, same script, same three conditions — **REPORTED, NEVER GATED**, no triple, no GCI, no observed order | 4 | **registered, NOT run by this registration** |

**Run root, NEW and separate:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh`

**Why a new root.** The `D6R2C` root holds the **graded** `O_mp` artefacts that `O_mp_GRADE.json` cites
by path. `G4` and `G5` are age-datum and file-ownership gates over that directory; writing new arms into
it puts a graded verdict's evidence under a new run's feet. `d6r2c_after_run_arm.sh` carries the parent's
`G-ROOT.1/2/3` design with **the `D6R2C` root itself added to `FORBIDDEN_ROOTS`** — the same move the
parent made for `D6R2`, for the same reason.

**Seeding.** `base/` (case, mesh, FFD) is copied **read-only and hashed at seed** from
`CURRICULUM-D6R2C-…-restartable/base/`, and the five polyMesh md5s of section 2a are asserted after the
copy. The final design vector is staged from `O_mp/d6r2c_evals.jsonl` **as an input, before the age
datum is set** (the parent's `L4` pattern), so the age guard dates it as an input and not as an output.

**Ranks 4**, per Sanaa's §A allocation for D6R2 and per section 9 of the frozen document.
**`--user 1000:1000 --group-add 1002`, `-e HOME=/tmp`, never root**, per her Launch item 6 and the
parent's `L1` — whose measured justification (uid 1000 is `ubuntu` inside the image; `/home/dafoamuser`
is `0750` owned by uid 1002) is carried unchanged.
**Checkpoints (her items 1–5):** the parent's `L6` rotator design is carried — every **1800 s wall**, the
per-step record, the design vector and the latest primal time from every `mp0*/processor*` are copied to
`ckpt/<UTC>/`, **the last two kept, older purged**. The `DEC` arm's predicted wall is ~4840 s, so it
crosses that cadence twice; `FM`'s is ~3090 s and crosses it once. **The kill-and-resume proof of her
item 5 is not re-run**: `PREREGISTRATION.md` section 5 is the once-per-solver-class proof for DAFoam
optimisation and its status there is what it is — **this item adds no claim about restartability and
quotes no number from it.**

---

## 6. THE MONITOR

**`d6r2c_monitor.py` (md5 `fd927f36ee47acef09fc8a08b790ccbe`) is NOT used by this item and no stop rule
is registered here.** The honest reason: ADDENDUM 3 §A3.5 measured that it *"was never started"* for
`O_mp`, and section 6 of the frozen document was recorded as **unsatisfied for that run**. Registering it
again here without changing what invokes it would repeat the defect in a new document.

**What replaces it, and it is weaker on purpose rather than stronger by assertion:** these arms are
**primal-only** — no adjoint, no IPOPT, no design iteration — so her item-7 stop rules (*objective rises
three consecutive iterations*; *resume from the last good iterate with the step halved*) **have no
iterate to act on and no step to halve.** There is no objective trajectory here to diverge. What *can*
go wrong is a primal that fails to converge, and that is covered by `D6`/`H4` as a **completion** gate
(`NOT A RESULT`, not a stop rule) and by the `TRIM_MAX_EVALS = 40` bound of section 3a.
`d6r2c_decomp.py` and `d6r2c_freshmesh.py` each append a per-step line to their own `.jsonl` **as the run
proceeds**, so the run is readable while it runs without a separate monitor process.

---

## 7. THE PLANTED CONTROL (rule 3)

`d6r2c_after_grade.py` plants **`PLANT = 1.234e-03`** into values it **read back from disk** and
**REFUSES (exit 2)** if any plant leaves the verdict at `PASS`:

- item 8: into `J_B`, into `J_T`, into `J_F`, into `J_opt`, and into one `CL` of one matched-lift arm;
- item 9: into `J_fresh`, into `Jf` as read from the inherited record, and into one deformed wall
  coordinate feeding `H1`.

**A comparator that cannot see a disagreement of that size in these artefacts cannot certify an
agreement, and its zero is not evidence.**

`--selftest` drives controls **in both directions** on synthetic trees in a temporary directory,
touching no run directory: the clean case must reach the unmutated label; each planted defect must flip
the label to the registered one; a table with one hole must produce a record carrying **no percentage
keys at all**; and a value perturbed by one part in `1e14` inside `D3`'s `1.0e-12` identity band must
reach `NOT A RESULT`. **The selftest exits non-zero if any control fails.**
**Driven at this draft: `D6R2C_AFTER_GRADE SELFTEST PASS n=51`, exit 0.**

---

## 8. COST, IN CORE-MINUTES, BEFORE THE RUN (rule 12)

**Measured anchors, both from this item's own artefacts, both at 4 ranks:**

| anchor | value | where measured |
|---|---|---|
| one primal evaluation of **all three** conditions | **48.081 s wall = 3.205 core-min** | `O_mp/d6r2c_evals.jsonl`, `F` record `n = 2`, `eval_wall_s` (records `n = 2..7` read 48.1, 48.9, 49.7, 49.4, 49.8, 49.3 s) |
| cold preamble: container + 3 case copies + 3 `decomposePar` + first primal + `findFeasibleDesign` | **2990.166 s wall = 199.344 core-min** | same file, `F` record `n = 2`, `wall_since_start_s`, against the `HEADER` at 0.0 |
| an IPOPT major (context only; **not used below** — these arms run no adjoint) | 26.917 core-min | `O_mp_GRADE.json`: 672.933 core-min / 25 majors |

**Planning figure: 50 s per 3-point primal evaluation** — the measured 48.081 rounded **up**, stated as
rounded up so the estimate is conservative rather than flattering.

**THE ADJOINT IS NOT RUN BY EITHER ARM.** Every step here is a primal evaluation plus a trim. `O_mp`'s
26 gradient evaluations cost a measured mean of **174.99 s each** (`d6r2c_evals.jsonl`, `kind = "G"`);
none of that is spent here, and saying so is why the estimate below is as small as it is.

| arm | predicted core-min | basis | **registered cap (3.00×)** |
|---|---|---|---|
| `DEC` | **322.7** | cold preamble 2990 s (**includes state 1's own trim**) + 4 further trims × 8 evals × 50 s + 5 recorded evals × 50 s = 4840 s wall × 4 / 60 | **968.1** |
| `FM` | **206.0** | mesh generation (below) + cold preamble 2990 s + 2 recorded 3-point evaluations × 50 s = 3090 s wall × 4 / 60 | **618.0** |
| `FM` mesh generation | **5.0** *(inside the `FM` figure above, itemised)* | pyHyp extrusion of a 1008-face surface + `plot3dToFoam` + `autoPatch` + `createPatch` + `renumberMesh`; the historical execution completed inside one wall-minute (`A2-mach-wing/preproc_stdout.log`, `logMeshGeneration.txt`). **Serial, but costed at 4 ranks because the 4-core allocation is held throughout** — the honest convention, not the flattering one | **15.0** |
| **TOTAL, THIS REGISTRATION** | **528.7** | | **1586.1** |
| `FM_L2` | 60.0 | one coarsen + cold preamble at ~⅛ the cells + 1 evaluation | 180.0 — **registered, NOT run here** |

**THE NUMBER THIS ESTIMATE IS WEAKEST ON, NAMED:** *how many primal evaluations `findFeasibleDesign`
needs per trim.* **It is not measured.** `findFeasibleDesign` runs *before* the driver, so the `D2`
per-evaluation recorder never sees its calls and no count exists in any artefact on disk. **8 per trim is
an estimate, labelled an estimate**, and it is bounded rather than trusted: `TRIM_MAX_EVALS = 40`
(section 3a) caps the worst case at 4 × 40 × 50 s = 8000 s of trim, giving a worst-case `DEC` of
**732.7 core-min — inside the 968.1 cap.** The cap is therefore reachable only through contention, not
through this misprediction, which is the point of stating it.

**Derived dollars.** `528.7 core-min = 8.812 core-h × $0.0513 = $0.452`.
**DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5);
`cost_basis` class **reported-by-owner** at the owner-stated c7a.4xlarge rate. *(The box is now an
r7a.4xlarge; the rate on record is the c7a.4xlarge figure and is used unchanged rather than invented —
the same substitution the frozen document named in its section 8.)*

**THE CAP REPORTS; NOTHING KILLS ON IT.** A crossing writes `D6R2C_AFTER_CAP_CROSSED` to the ledger, the
row is graded **`NOT A RESULT`**, and **the cap is never raised** (Sanaa's item 7 read with her
2026-09-12 directive #17: no run is stopped by a time or budget cap). No wrapper carries a `timeout` and
every container prints `D6R2C_AFTER_DEADLINE_IN_CONTAINER_S: NONE`.

**Contention caveat, registered in advance.** `core_min = wall_s × ranks / 60` inflates with contention
at identical compute work. `O_mp` itself measured **26.917 core-min/major against a 31.258 anchor** — it
ran *cheaper* than predicted, so this family's recent contention has been low. A recorded figure above
the prediction attributable to delivered-core starvation is **REPORTED with the measured
`delivered_cores_mean`** and named as waste, never absorbed into the ratio (rule 12,
`COMPUTE_BUDGET_CHARTER.md` §6).

**Calibration row OWED** to `docs/COST_CALIBRATION.md` at each arm's completion — actual against the
estimate above, the ratio, and contention / waste / misprediction attributed **separately** (rule 12).

---

## 9. PLACEMENT, RANKS, MEMORY, MESH

`RANKS = 4`; `CPUSET = 2,3,4,5`; `--memory=20g --memory-swap=20g`, **declared
`memory_footprint_gb = 17`** and checked against `MemAvailable` before start (the parent's `L2`).
Core guard: 4 solver ranks against `nproc = 16` (Launch item 8). Box hygiene (`L3`, her item 18): the
launcher **refuses to start** if `load1 > nproc` or any swap is in use — **a launch precondition that
refuses to START and never stops anything running** (directive #17). An OOM kill (`rc = 137`) is a
registered outcome and fails `D6`/`H4` as `NOT A RESULT`.

### 9a. THE MESH, STATED CORRECTLY

**38,304 cells, 40,209 points, all hexahedra, 3 patches** — `wing` (wall, 1008 faces), `inout` (patch,
1008 faces), `sym` (symmetry, 1672 faces). Decomposed 4 ways as 9504 / 9600 / 9608 / 9592. See §0b.1 for
why this is stated here rather than copied from the frozen document's section 1.

### 9b. FLOW REGIME

**`M∞ = 0.288`, compressible subsonic**, per `PREREGISTRATION.md` ADDENDUM 2 and Sanaa's own ruling
(*"its fine we can keep the compressible subsnoic"*). The run-root name of the parent item carries the
word "transonic" and is a **known, disclosed misnomer**; **this item's new run root does not carry it.**
**No shock figure can be produced from any artefact of this item** — maximum local Mach in this flow was
independently measured at 0.380.

---

## 10. WHAT THIS ITEM DOES NOT CLAIM

- **It does not re-grade `O_mp`.** That row is closed at **`GATE FAIL`** (ADDENDUM 3 §A3.7) and nothing
  here can move it. The 24.732 % stands as graded against `G2`, with the `G3` miss beside it, as it was.
- **It is not a grid study.** `H3` is a **two-mesh comparison at one nominal resolution** — warped versus
  extruded, same surface, same extrusion parameters. **No Roache triple, no GCI, no observed order**
  (rule 5; section 10 of the frozen document). `FM_L2`, if it is ever run, does not change that sentence.
- **It does not verify the gradient.** That is the `ARM0` / `F_mp` / `D6RF` family. Not one adjoint is
  solved by either arm here.
- **It does not claim the primal reaches the A2 accept floor of `1.0e-5`.** `D6RF10` measured that this
  `DARhoSimpleFoam` configuration does **not** (`p_first_uncorrected = 1.681e-05`, `GATE FAIL`). The
  `DARhoSimpleCFoam` change is `D6R3` and is **deliberately not taken here** — changing the solver
  between `O_mp` and its own decomposition would make the decomposition a statement about the solver.
- **It does not claim the fresh-mesh band is a discretisation uncertainty.** Section 2d: it is a
  **declared decision-relevance band**, and this file says so four times because it will be read by
  someone who wants it to be the other thing.
- **It does not claim `Δ_shape` and `Δ_twist` are independent.** `D4` **measures** whether they are
  near-additive and the record carries the interaction term either way.
- **It does not satisfy Sanaa's item 10.** The report — gradient spot-check table, parallelism-health
  line, convergence history, figures to the figure standard, certificate slot — is a **separate record**
  and is not registered here. It is named so no reader mistakes this freeze for the whole instruction.

---

## 11. THE FROZEN INSTRUMENTS

**Every instrument this document names EXISTS, is in THIS COMMIT, and carries its md5 below.** This
paragraph is here because the defect ADDENDUM 3 discloses — section 4 of the frozen document naming
`d6r2c_grade.py`, an instrument that *"did not exist … absent from every tree in this repository's git
history"* — is the exact defect this table is designed to make impossible. **A table that lists what
exists cannot show what is missing**, so the list is closed: **the four files below are every instrument
named anywhere in this document, and `scripts/check_filing.py` plus the freeze check are run on all of
them before the commit.**

| file | role | md5 at freeze | selftest driven at freeze |
|---|---|---|---|
| `d6r2c_after_grade.py` | **THE GRADING PATH for items 8 and 9** — `D1`–`D6`, `H1`–`H4`, the table, the planted controls | `6c22013af54569ae651f8f23d1088861` | **`D6R2C_AFTER_GRADE SELFTEST PASS n=51`** |
| `d6r2c_decomp.py` | item 8 producer, in-container: the five states, the trims, `d6r2c_decomp.jsonl` | `3089b620587b1c20035f63dc1c8cd175` | **`D6R2C_DECOMP SELFTEST PASS n=32`** |
| `d6r2c_freshmesh.py` | item 9 producer, in-container: deform the CGNS surface, run the family script, solve, `d6r2c_freshmesh.json` | `ad2946f197fefc9cd5829deec1866a57` | **`D6R2C_FRESHMESH SELFTEST PASS n=23`** |
| `d6r2c_after_run_arm.sh` | the launcher: `G-ROOT.1/2/3`, digest pin, `G-COLD`, age datum, md5 pins, ledger, checkpoint rotator | `c83d18547353ef32e4ed960bb6783501` | **`D6R2C_AFTER_LAUNCH SELFTEST PASS n=5`** |

**The grading path is `d6r2c_after_grade.py` and it is in this commit, fixed before any compute, per
rule 2.** The launcher pins **all three** of `d6r2c_after_grade.py`, `d6r2c_decomp.py` and
`d6r2c_freshmesh.py` by md5 and refuses (exit 4) on any difference, so the instruments that run are the
instruments that were frozen — **and the grader is pinned too**, which the parent's launcher did not do
for its own grader because its own grader did not exist.

### 11a. THE HONEST GAP IN THIS FREEZE, NAMED BEFORE IT IS DISCOVERED

**`d6r2c_decomp.py` and `d6r2c_freshmesh.py` have NEVER BEEN EXECUTED AGAINST THE SOLVER.** They cannot
be: they run inside the pinned image, against `DARhoSimpleFoam`, and running them is the compute this
document is registering. What *has* been driven at the freeze is stated per file in the table above —
byte-compilation, and each file's `--selftest`, which exercises the pure logic (DV assembly, space
conversion, scaler handling, record writing, refusal paths) on synthetic inputs and touches no run
directory and no container.

**Registering that they will work would be an assertion, so instead the first compute is cheap and
disposable:**

> **`DEC` runs first. If it has not written its `state = B` record within `TRIM_MAX_EVALS` evaluations,
> it is stopped as a producer defect, graded `NOT A RESULT`, and repaired under
> `VERIFICATION_CHARTER` §2d.1 — the grading path `d6r2c_after_grade.py` is NOT touched by such a
> repair, and if it ever must be, that is a new registration.**

The distinction that keeps this legitimate: **a producer defect is a defect in how a number was made and
is repairable with disclosure; a grader change after seeing data is not.** `d6r2c_after_grade.py` is
frozen at the hash below and its thresholds — `TRIM_TOL`, `REPRO_TOL`, `CLOSE_TOL`, `INTERACT_TOL`,
`SHAPE_MATCH_TOL`, `FM_BAND_ABS`, `PLANT`, and every cap in section 8 — are **copied verbatim from this
document**, each carrying the sentence it was copied from as its comment, exactly as ADDENDUM 3 §A3.2
records for the parent's grader. **Nothing in the grader was chosen by its author.**
