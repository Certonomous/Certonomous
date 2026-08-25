# F1 / ONERA M6 — TOPOLOGY STUDY: the >70° breach is TWO mechanisms, and only ONE of them is in the outer blocks

**cfd lane, 2026-08-25.** MESH_STANDARD §8.1 build trial. **NOTHING HERE IS PRE-REGISTERED** and no
verdict below is scored against a registration of this study's own. The only gate applied is
`docs/standards/MESH_STANDARD.md` §3.1's **standing** hard threshold of **70°** max non-orthogonality,
which pre-dates this work — it was not chosen to fit an answer.

Every number cites a file still on disk under
`/home/ubuntu/Certonomous/verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/`.

---

## 1. THE SUPERVISOR'S RULING, TESTED AS ASKED — HALF CONFIRMED, HALF FALSIFIED

The ruling was: *the 38-variant sweep is a finding about the TOPOLOGY, not the dials*, and the
cheapest test of it is *"replacing only the outer blocks with an orthogonal far-field shell — if the
maximum drops below 70° it proves the near-body butterfly was never the problem, and if it does not,
my ruling is wrong and I want to know that."*

**That variant was built. It is `t1_SHELL`.** rc 0/0/0, 111,872 cells (identical to the control),
max skewness **1.443 OK**.

| | control `t0_REPRO` | `t1_SHELL` |
|---|---|---|
| max non-orthogonality, whole mesh | **81.9396°** | **81.5834°** |
| max non-orthogonality **excluding the 8 tip-cap blocks** | **81.9396°** | **47.9767°** |
| faces > 70° | 598 | 516 |
| max skewness | 1.4431 | 1.4430 |
| cells | 111,872 | 111,872 |

*(`SUMMARY.txt`; `evidence/NONORTHO_t0_REPRO.txt`, `evidence/NONORTHO_t1_SHELL.txt`.)*

**CONFIRMED:** the far-field breach IS a topology defect and IS repairable in the outer blocks alone.
It falls **81.9396° → 47.9767°** — comfortably inside the gate — **without touching `F1_BETA` or
`F1_RFAC`**, without moving the outlet plane, at an identical cell count, and with skewness unchanged.

**FALSIFIED:** the ruling's corollary that *"the near-body butterfly was never the problem."* After
the outer blocks are repaired, **the near-body tip-cap butterfly is the ONLY thing left above 70°**,
and the whole-mesh maximum lands on **81.5834° — the tip-cap floor, to four decimal places.**
`GATE FAIL` against §3.1's 70°.

---

## 2. THE INSTRUMENT, AND ITS CONTROLS

`outer_face_geom.py` **imports** `../te_study/worst_nonortho.py` and uses its cell-centre, face-centre
and area-vector routines unchanged — OpenFOAM's pyramid-weighted form. It adds only what was missing
to attach a mechanism to the number: the **face normal**, the owner→neighbour vector **resolved into
face-normal and face-tangential parts**, the four corner points, and the structured `(block, i, j, k)`
address of the offending pair.

Both of `worst_nonortho.py`'s planted controls are carried and both must pass or it exits 2 **without
printing a result** (CLAUDE.md rule 3):

- **(a) AGREEMENT** — the recomputed maximum must match `log.checkMesh` to < 0.05°. Measured across
  all 13 meshes: worst disagreement **0.00005°**.
- **(b) DISPLACEMENT** — one point of the winning face is moved 1.234e-04 in y and its angle must
  move by > 1e-6°. Seen on every mesh, e.g. `81.583413 → 83.723223` on `t1_SHELL`.

The **generator** carries its own control. `gen_topo.py` with `F1_SHELL=0 F1_SIMCORE=0` must reproduce
the 38-variant generator exactly, and that is **checked, not asserted**:
`cmp t0_REPRO/system/blockMeshDict ../te_study/b1_CTRL/system/blockMeshDict` is **byte-identical**,
re-checked after every one of the four generator edits.

**No false-zero path exists in this study.** `run_topo.sh` never writes an RC file for a step it did
not run; it writes `NOT_ATTEMPTED_<step>.txt` instead, because `te_study/run_batch.sh:37` wrote the
single character `-` into `RC_blockMesh.txt`/`RC_checkMesh.txt` and 14 variants' worth of those were
readable as zeros. **A missing RC file cannot be misread as a zero.** Every rc is read back **from
the file**, never inferred, and `SUMMARY.txt` refuses to print a mesh number for any variant whose
`RC_dict.txt` is not `0`. The import path is **asserted**, not `sys.path.insert`-ed blind (rule 14).

**Age guard** (`AGE_GUARD.txt`), the mesh analogue of rule 4: for all nine variants
`log.checkMesh` is newer than the `polyMesh` it grades, which is newer than the `blockMeshDict` it
came from. **9/9 PASS.**

---

## 3. THE TOPOLOGY, STATED PRECISELY (Step 1)

Read from HEAD **and** from disk; the three `cases/` files that the shared index reports DELETED are
in fact intact and **identical to their HEAD blobs** — `make_blockmesh_f1.py` `b56bc157…`,
`m6_section.py` `cbd5edba…`, `make_blockmesh_m6.py` `62e9973d…`. The index lies; the disk does not.

The generator that produced all 38 variants is `../te_study/gen_var.py`. Its topology:

- **24 blocks at m=1** (111,872 cells): **8 wrap blocks × 2 spanwise levels = 16**, plus an **8-block
  butterfly tip fill** outboard of the flat tip.
- The wrap is a **C-grid in the chordwise plane**, not an O-grid: it wraps the section from the
  wake, round the lower surface, round the LE, along the upper surface and back into the wake, with
  the **wake cut** along `y = 0` downstream of the TE. The eight wrap blocks are
  `wake_lo | tail_lo | mid_lo | nose_lo | nose_up | mid_up | tail_up | wake_up`, breaking at
  x/c 0.10 and 0.90 so the shock band x/c 0.18–0.60 lies inside the uniform mid blocks.
- **The far-field boundary is a D-shape, not a circle.** It is the flat plane `y = ±R` for every
  station from x = xa (x/c 0.10) downstream to `XEXIT = R`, closed upstream by a quarter arc of
  radius R about the origin from `(0, −R)` to `(−R, 0)` and its mirror. `R = XEXIT = 20·c_root =
  16.118`.
- The wrap meets the far field through **one block layer of 32 radial cells** graded
  `simpleGrading` at expansion `exp(β(n−1)/n)`, β = 10.575549.
- The tip fill meets the wrap **through the wing surface itself**: its side strips share the surface
  polyLines `le→up10`, `up10→up90`, `up90→te` and their mirrors with the outboard wrap blocks.

### Why the outermost wall-normal cell is non-orthogonal at all — geometrically, with numbers

**It is not because the far field is oblique to the radial lines.** The winning face's unit area
normal is **(−0.962154, 0.000010, 0.272506)** — an x–z normal, i.e. the face contains ŷ; the outer
boundary there is the plane `y = −16.118000` (both far-field corner points read exactly that), and
the radial lines run along ŷ. **The radial lines meet the far field dead normal.** The supervisor's
"most likely reading" — a wrap arriving obliquely at a box far field — is falsified by that normal.

The real cause is an **arc-length mismatch between opposite block edges**:

> In `tail_lo` the **inner** i-edge is the curved wing surface from the TE to x/c 0.90; the **outer**
> i-edge is a straight line at `y = −R` spanning the same two x-stations. Those two curves have
> **different arc lengths**. `blockMesh` distributes i-nodes on both by the **same arc-length
> fractions**, so the i-lines **fan**. The fan makes the outermost radial cell a trapezoid — measured
> **3.2 % wider in x at the far field than at its inner edge**. Three per cent of a cell that is
> **4.536 tall in y** is a centroid shift of **d_y = 1.192988e-02**, while the spacing **through** the
> face is only **1.690823e-03**. `atan(1.193947e-02 / 1.690823e-03) = 81.9396°`.

**The natural control was already on disk and nobody had read it.** `blk00` (`wake_lo`) has the
**same** radial grading, the **same** aspect ratio and the **same** far-field plane — but **both** its
i-edges are straight lines of **equal** length (the wake cut, and `y = −R`, each running x_te→XEXIT).
It **never appears above 70°**. Same stretching, no mismatch, no breach.

---

## 4. THE TWO MECHANISMS, SEPARATED (Step 2)

The per-block-pair census in `outer_face_geom.py` separates them without building anything:

**Mechanism A — FAR-FIELD FAN, wrap blocks `blk01`/`blk06` (`tail_lo`/`tail_up`, root level).**
81.9396°, 58 faces. Face centroid `(1.134134, −13.850016, 1.166844)`, i.e. `|y| = 13.85` of R = 16.118
— the outermost radial cell, as the brief said. Mechanism as above.
*Cited:* `evidence/NONORTHO_t0_REPRO.txt`.

**Mechanism B — TIP-CAP FAN, butterfly side strips `blk18`/`blk21`, 81.5834°, 444 faces.**
**β-INVARIANT, and therefore the binding floor.** Face centroid **`(1.135483, −0.000732, 1.525873)`**
— `|y| = 7.3e-04`. **That is the sharp TRAILING EDGE of the tip cap, not the far field.** Unit normal
`(−0.013826, −0.999904, 0.000000)`; `d = (−2.089541e-03, −2.797093e-04, 0)`, i.e. the displacement is
**99 % chordwise across a face whose normal is spanwise**; `d_t/d_n = 6.7584`.
*Mechanism:* `blk21 = (mte, clo90, lo90, te)` has **three of its four corners on `x = xb`**. Its
j-edge at i=0 is chordwise (`mte→te`, 0.1 c) and its j-edge at i=3 is vertical
(`clo90→lo90`, `(1−CORE_S)·t2(0.9)·c`). **j turns through 90° across the block and collapses ≈16:1
onto the sharp TE.**
*Cited:* `evidence/NONORTHO_testudy_b3_BETA_1.txt`, `evidence/NONORTHO_testudy_b3_BETA_5.txt`.

**The clean separation, for free, from the existing meshes:**

| mesh | whole-mesh max | max **excluding** the 8 tip-cap blocks |
|---|---|---|
| `b1_CTRL` (β = 10.575549, registered) | 81.9396° | **81.9396°** (A dominates) |
| `b3_BETA_1` (β = 1.0) | 81.5834° | **39.2551°** (A gone, B remains) |
| `t1_SHELL` (β registered, shell repair) | 81.5834° | **47.9767°** (A repaired, B remains) |

**Both mechanisms are the same defect** — a block whose two opposite edges are not similar curves —
and they live in different blocks with disjoint cures. The supervisor's "envelope, two mechanisms,
disjoint dial sets, 0.36° apart" is right in structure; what was missing was **where** the second one
lives, and it is not where the brief placed it.

### Two corrections to the briefed premises, both measured

**(1) "The maximum is NOT at the trailing edge" is true of the registered β and false of the FLOOR.**
The floor at 81.5834 is at the trailing edge — of the tip cap, at `|y| = 7.3e-04`. Since the floor is
what must be cleared, the trailing edge is precisely where the gate is lost.

**(2) The MK test did not falsify the degeneracy hypothesis; it was run against the wrong maximum.**
The brief records *"the `F1_MK` repair removes all four and the maximum does not move one digit
(81.9396 with and without)"*. At β = 10.575549 the maximum is **mechanism A**, which `MK` cannot
touch — so that comparison could not have moved, whatever `MK` did. Measured against **mechanism B**,
at a β where B is the maximum: `b3_BETA_5` **81.5834°** vs `b3_BETA5_MK1` **81.5971°**. **`MK` does
move the floor — by +0.0137°, in the wrong direction.** The degeneracy hypothesis is not falsified;
it is confirmed as the right block, with `MK` confirmed as an ineffective repair, for the reason
`gen_var.py`'s own docstring gives: the two corner deviations sum to exactly 90° for every offset, so
the degeneracy can only be **shared**, never removed. Sharing the *corner angle* does nothing to the
*cell fan*, which is set by the ratio of the block's edge **lengths** — a quantity the `MK` design
never addressed. **This is a difference in what the evidence supports, not a request to re-sweep MK.**

---

## 5. WHAT WAS BUILT (Step 3)

`gen_topo.py`, two switchable structural changes on top of the v2 butterfly. `run_topo.sh`,
`MANIFEST_t1..t4.txt`. Nine variants, all rc 0/0/0.

| variant | dials | cells | max non-orth | skew | max AR |
|---|---|---|---|---|---|
| `t0_REPRO` | — (byte-identical to `b1_CTRL`) | 111,872 | 81.9396 | 1.4431 | 5934.1 |
| **`t1_SHELL`** | `F1_SHELL=1` | 111,872 | **81.5834** | 1.443 | 5622.42 |
| `t2_SIMCORE` | `F1_SIMCORE=1` | 111,872 | 87.0192 | 1.62811 | 5934.1 |
| `t3_SHELL_SIMCORE` | `F1_SHELL=1 F1_SIMCORE=1` | 111,872 | 87.0192 | 1.62811 | 5622.42 |
| `t4_CORE2` | `F1_SIMCORE=2` | 111,872 | 84.875 | 1.4712 | 5934.1 |
| `t5_SHELL_CORE2` | `F1_SHELL=1 F1_SIMCORE=2` | 111,872 | 84.875 | 1.4712 | 5622.42 |
| `t6_SHELL_NR16` | `F1_SHELL=1 F1_NR=16` | 118,784 | 81.9764 | 1.443 | 5622.42 |
| `t7_SHELL_NR32` | `F1_SHELL=1 F1_NR=32` | 128,000 | 82.0355 | 1.443 | 5622.42 |
| `t8_SHELL_NR64` | `F1_SHELL=1 F1_NR=64` | 146,432 | 82.0645 | 1.82473 | 5622.42 |

**`F1_SHELL=1` — the outer-block repair that works.** Every wrap block is split radially into an
inner layer and an **outer shell** whose inner boundary is the far-field shape **at radius `S1·R`
with the x-stations kept**. Along the flat far field the shell's two i-edges are then **parallel
straight lines of equal length**, so their arc-length fractions coincide by construction, the fan is
identically zero, and the outlet plane `x = XEXIT` stays planar. Cell count is preserved
(`NJ1 + NJ2 = 32`) and the registered wall-normal progression is reproduced across the split by
giving each layer the same per-cell ratio `r = exp(β/n_j)`. **`F1_BETA` and `F1_RFAC` are untouched.**

> **The first cut of this got it wrong and the wrongness is kept on the record.** It scaled the whole
> far-field shape about the section mid-chord. That *is* self-similar and the shell's rays did come
> out exact — but it dragged the exit station from x = 16.118 in to x = 1.58 while the wake cut still
> ran to 16.118, shearing the **inner** wake block 13:1: **max skewness 30.0376, 780 highly skew
> faces**, average non-orthogonality 15.91 → 30.23. Worse, and in the layer the change was not aiming
> at. Offsetting rather than scaling is what the mechanism actually asks for.

**`blockMesh` refused the shell on its first build — and it was right, and it was MY defect, not the
topology's.** rc = 1, *"Trying to specify a boundary face … which is either an internal face or
already belongs to the same patch … patch 0 named `wing`"* (`t1_SHELL/log.blockMesh`, captured). I had
handed the shell block the inner block's patch list, so `wing` was claimed on the shell's x2min —
which is the **inner layer's interface**, an internal face. The fix corrects a **patch assignment**;
no block, vertex or edge was changed to make a number appear. **MESH_STANDARD §8.2 is NOT engaged**,
and the `F1_SHELL=0` path stayed byte-identical to v2 through the fix.

**The tip cap: three core placements built, all three fail, in three different blocks, for one reason.**

| core placement | max | where |
|---|---|---|
| v2 — core corners at the **surface** break stations `xa`, `xb` | 81.5834° | side strips `blk18/blk21` |
| `SIMCORE=1` — core an exact `CORE_S`-scale copy of the section about O(z) | 87.0192° | **core** blocks `blk22/blk23` |
| `SIMCORE=2` — chordwise stations pulled in, `mle`/`mte` on the core's own 10/90 stations | 84.875° | side strips again, `blk34` |

`SIMCORE=1` fixes the strips and breaks the core: the chord-line edge `mle→mte` then spans 0.50 c
while the scaled-surface edge `clo10→clo90` spans 0.40 c — a 25 % arc-length mismatch across a
j-extent of ~0.003 c, giving `d_t/d_n = 19.2042` and 87.0192° at `blk23 i=31 j=0`
(`evidence/NONORTHO_t2_SIMCORE.txt`). `SIMCORE=2` restores the core and the strips fail again:
`blk34 = (cup90, mte, te, up90)` has i-edges of 0.0027 (core, vertical) against 0.045 (the surface arc
from x/c 0.9 to 1.0) — **16:1 again**, `d_t/d_n = 11.1499` (`evidence/NONORTHO_t5_SHELL_CORE2.txt`).

> **The irreducible quantity.** Whatever the core's shape, the O-grid strip facing the trailing edge
> must join a **surface arc of length ≈ (1−U2)·c** to a **core edge of length ≈ CORE_S·t2(U2)·c**.
> Their ratio is **≈ 16** at the registered break `U2 = 0.90`, and it is set by the section's own
> **half-thickness at the break station**, which → 0 as the sharp trailing edge is approached. It is a
> property of the AEROFOIL, not of any dial, corner placement or grading.

**And it does not refine away.** Radial refinement of the cap — a question the brief's `NR` evidence
could not answer, because `NR` was swept at a β where mechanism A masked it — gives
**81.5834 (nr=4) → 81.9764 (nr=16) → 82.0355 (nr=32) → 82.0645 (nr=64)**. The breach **rises** and
asymptotes near **82.07°**. This is `MESH_STANDARD` §8.1's own signature: *"a fixed fraction of the
mesh, not a marginal miss — so no finer level could ever have cleared it."*

---

## 6. WHERE THAT LEAVES THE TIP CAP — the option that is already closed

The classical alternative to an O-grid cap on a sharp-TE section is an **H-block lens fill**. That is
**not open**: the pre-registration's own **Amendment 2 §A2.2(2)** records that `blockMesh` v2606
**cannot express it** — `rc = 134` on a repeated-vertex prism block, and 48 zero-area faces with
`Failed 2 mesh checks` written with coincident distinct vertices — and it was previously **routed
around by hand-writing `polyMesh`**, which the same document's **Correction C1.3** and
`MESH_STANDARD` §8.2 now forbid. **The butterfly exists because the H-cap was refused.**

So the cap is genuinely cornered, and the choice is a **standards** question, not a lane's:

1. **Round the tip cap to the STL's own closure.** Amendment 2 §A2.2(1) already discloses that the
   registered STL **closes over a rounded cap** from z = 1.19676 to z = 1.21640 (2.44 % c_root) and
   that this mesh **cuts it flat** and does not reproduce it. A rounded closure removes the sharp-TE ×
   flat-tip corner that both cap mechanisms live on. **This is the only route I can see that leaves
   both `blockMesh` and §3.1 intact, and it makes the mesh MORE faithful to the registered geometry,
   not less.** Untested — I did not build it, and I am not entitled to assume it works.
2. **Gate the wing and the cap separately** — §3.1 applied to the mesh excluding the 8 cap blocks
   (`t1_SHELL`: **47.9767°**, a clean pass), with the cap's breach carried explicitly in the numerical
   channel. **Retiring or scoping a gate threshold is reserved to Sanaa** (CLAUDE.md FIRST-ACTION
   RULE); this is named as an option, not proposed as one.
3. **Accept `GATE FAIL` and hold M6 at its admission gate**, which is where it stands today.

---

## 7. STEP 4 — THE AMENDMENT IS NOT DRAFTED, AND THE BRIEF'S PREMISE NEEDS CORRECTING

The brief made the amendment conditional: *"if and only if a topology clears 70°."* **No topology
built here clears 70°.** The best whole-mesh maximum is `t1_SHELL`'s **81.5834°**. **The condition is
not met and no amendment is owed.**

**Separately, the premise that the registration is "UNFIRED, so under rule 2 an amendment is still
legal" does not survive reading the document from HEAD.** The frozen file
(`verification/campaign/F13_ONERA_M6_PREREGISTRATION.md`, blob **`7456a7b3dc62`**, disk hash-matched)
already carries **CORRECTION C1**, whose **§C1.5** reads:

> *"`GATE FAIL` on §5 admission at all three levels; tier `NOT HELD`; V, G and P `PENDING` with no
> value computed."*

and whose §C1.3 says of the standing constraints: *"Moot for this ladder, **which is dead**; binding
for **its successor**."* **§5's admission gate has already been graded.** Amending §5 now — the
section that fixes β and the far-field radius, and the section a topology change touches — would
alter a gate **after** its verdict, which rule 2 closes. The lawful route is a **new pre-registration
for a successor ladder**, not an amendment to this one. That call is the supervisor's and I have not
taken it.

---

## 8. COST — pre-registered estimate vs actual (CLAUDE.md rule 12)

**There is no pre-registration for this study, so there is no pre-registered estimate to compare
against, and I will not invent one retrospectively.** What is stated is measured, and the ratio row is
recorded as **N/A — no registered estimate exists** rather than as a number with no basis.

- **Builds** (generator + `blockMesh` + `checkMesh`, 1 core each, from each variant's `WALL_S.txt`):
  **13 s → 0.217 core-min**.
- **Diagnostics** (`outer_face_geom.py` over 13 built meshes, 1 core, batch clocks):
  **369 s → 6.150 core-min**.
- **Total measured: 6.367 core-min = 0.1061 core-h → $0.0054, DERIVED at the owner-reported
  $0.0513/core-h, NOT MEASURED** (the box cannot read its own billing,
  `COMPUTE_BUDGET_CHARTER.md` §5).
- **WASTE, named separately and not absorbed** (`COST_MEASURED.txt`): two refused first cuts of the
  shell (a patch-assignment defect of mine) ≈ 4 s; three rebuilds of `t0_REPRO` to re-check
  byte-identity after each generator edit ≈ 4 s. **≈ 0.13 core-min, ≈ 2 % of the total.** No mesh was
  diagnosed twice — the tool-timeout batch's four completed files were kept.

Well under the $25 pre-authorisation. Peak concurrency 3 processes; the 5-core ceiling was never
approached and no process I did not start was touched.

---

## 9. VERDICTS

Against `MESH_STANDARD.md` §3.1's standing hard gate of **70°**:

- **`GATE FAIL` — every one of the nine variants built.** Best **81.5834°** (`t1_SHELL`).
- **`GATE FAIL` — the tip-cap floor, and it does not refine away:** 81.5834° at nr=4 rising to
  **82.0645°** at nr=64, asymptotic near 82.07°.
- **The outer-block repair is a measured success on its own terms and is NOT a gate verdict:** the
  mesh excluding the 8 cap blocks falls **81.9396° → 47.9767°**, at identical cell count, unchanged
  skewness, and with `F1_BETA`/`F1_RFAC` untouched.
- **`BLOCKED` — the tip cap.** The O-grid cap cannot clear 70° for a reason that is a property of the
  section; the H-block cap is refused by `blockMesh` and the `polyMesh` bypass is closed by
  §8.2/C1.3. **Unblocking needs either the rounded tip closure (§6 option 1, untested) or a scoping
  decision on §3.1 that is reserved to Sanaa.**
- **`PENDING` — F1/M6 admission.** Unchanged from `C1.5`: tier `NOT HELD`.
