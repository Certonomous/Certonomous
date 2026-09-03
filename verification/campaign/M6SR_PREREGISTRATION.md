# M6SR pre-registration — ONERA M6 surface pressures against AGARD AR-138, on a SURFACE-REFINEMENT family

**Team: cfd. Case id `M6-SR`. v0.1 DRAFT, drafted 2026-09-03 by a cfd lab-lane.**

> ## ⚠ THIS FILE IS A **DRAFT**. IT IS **NOT FROZEN**. NO GATE IN IT IS IN FORCE.
>
> **Nothing here authorises compute.** No run root named below may be created, and no solver
> may start, until the cfd supervisor has performed the `SUPERVISION_CHARTER.md` §3 **check 4**
> (pre-registration committed before compute) **personally** and landed a freeze commit that is
> a status flip and nothing else.
>
> **The lane that wrote this text did not check it.** Authorship is this lane's; the check is
> the supervisor's and is not delegated. No message from this lane, or from any agent, is
> Sanaa's consent or the supervisor's check (standing rule 9).
>
> **Run-root absence, checked at drafting and to be RE-CHECKED at freeze.** At 2026-09-03,
> `ls -d verification/runs/M6SR*` and `ls -d cases/M6SR` both returned *No such file or
> directory*. Rule 2 requires the condition **and how it was checked**; the freeze block must
> re-state it against the freeze timestamp, not against this one.

---

## 0. THIS IS A SUCCESSOR. IT AMENDS NOTHING. THREE PREDECESSORS STAND AS COMMITTED.

| predecessor | frozen at | status under this document |
|---|---|---|
| `verification/campaign/RUNG1_M6_PREREGISTRATION.md` | `c7f99bb1` | **NOT edited, NOT amended, NOT reinterpreted.** Its §5 outcome stands as committed. |
| `verification/campaign/RUNG1_M6_R2_PREREGISTRATION.md` | `3126345f` (freeze), `7260f6c9` (Addendum 1) | **NOT edited, NOT amended, NOT reinterpreted.** Its gates, its post-freeze-parameter disclosure and its Addendum 1 stand exactly as committed, **errors included.** |
| `verification/campaign/M6I_PREREGISTRATION.md` | `73148a9c` | **NOT edited, NOT amended, NOT reinterpreted.** |

**Why a successor and not an amendment, stated once and not repeated.** The finding that closes
`RUNG1_M6_R2`'s route (§1.1 below) arrived **after** that registration's first compute. Reviving
or re-routing a design **by editing the registration that fixed it** is precisely the shape
standing rule 2 exists to forbid: it lets the gate be chosen to fit the answer. A successor at a
**new path**, frozen before **its own** compute, is the only clean instrument. This document
therefore **cites** its predecessors and **changes none of them.**

> **Nothing below grades, re-grades, promotes or demotes any verdict of any predecessor.**

---

## 1. CONSTRAINTS — PHYSICS FINDINGS, REPORTED NOT GATED, EACH WITH ITS MEASUREMENT

These four are **measurements and algebra**, not gates. They carry no verdict of the fixed
vocabulary. They bound every option in §2 and they are the reason this document exists.

### 1.1 THE OVER-DETERMINATION THEOREM — pyHyp HAS NO FREE GROWTH RATIO

pyHyp's hyperbolic march distributes `N−1` cell layers whose spacings must **sum to
`marchDist`**. For the geometric distribution it uses, the growth ratio `r` is therefore the
root of

```
    s0 · (r^(N−1) − 1) / (r − 1)  =  marchDist
```

**`r` is DETERMINED by `(s0, N, marchDist)`. It is not available to be chosen and it is not
available to be held constant.**

**Measured, and independently re-derived by this lane from the algebra above** — closing the
`VERIFY` item the cfd supervisor left open on board 53 (*"I have not re-derived pyHyp's printed
Grid Ratio from the layer spacings"*):

| level | `s0` | layers `N−1` | `marchDist` | pyHyp's **printed** `Grid Ratio` | **this lane's root-solve of the equation above** |
|---|---|---|---|---|---|
| `RUNG1_M6_R2` L3 | 4.0e-4 | 23 | 50.0 | **1.6329** | **1.632933** |
| `RUNG1_M6_R2` L2 | 2.0e-4 | 46 | 50.0 | **1.2739** | **1.273851** |
| `RUNG1_M6_R2` L1 | 1.0e-4 | 92 | 50.0 | never completed | **1.127805** |

Printed values read from `verification/runs/RUNG1_M6_R2_runs/L3/log.pyhyp` (`Grid Ratio: 1.6329`)
and `.../L2/log.pyhyp` (`Grid Ratio: 1.2739`). The root-solve agrees to **four decimal places on
both**, on parameters read from the levels' own `work/genWingMesh.py`. **The theorem is now
established by two independent instruments — pyHyp's own print and the closed-form algebra — and
not by one.**

> 🔴 **THE CONSEQUENCE, WHICH IS STRUCTURAL AND NOT EMPIRICAL. Any design that holds `marchDist`
> fixed while varying `s0` and `N` to generate the family CANNOT PRODUCE A ROACHE TRIPLE.** Its
> three levels differ in **three** things at once — wall spacing, layer count, and normal growth
> ratio — and the third is a change in the **distribution** of the discretisation, not a
> refinement of it. `r` moved **1.6329 → 1.2739 across the two levels that were built, a factor
> of 1.448.** No amount of re-running changes this. It is killed at the algebra, not at the
> measurement.

**The two admissible alternative shapes, and NEITHER IS FREE** (recorded so a future design does
not rediscover them): (1) hold `r` fixed and let `marchDist` float — a **domain** change across
levels, which must be shown not to matter; (2) hold `r` **and** `marchDist` fixed and let `s0`
float — then wall spacing does **not** refine, `y⁺` moves between levels, and the near-wall
commitment must be re-declared. Each trades one contamination for another. **This registration
takes neither.** It takes §1.2's third road: change **nothing** in the normal direction at all.

### 1.2 THE SAME THEOREM IN ITS FIXED-`s0` FORM — A STRETCHING SWEEP IS NOT REFINEMENT

`A3-onera-m6-sweep-n8_10920`, `…-n15_21840` and `…-n28_42120` share `s0 = 1.0e-4` and
`marchDist = 12.0` **identically** (read from each directory's own `genWingMesh.py`), varying
only `N` = **8 / 15 / 28**. Wall spacing therefore never refines, and the mesh-quality extrema
are **identical to six figures across a 3.86× cell increase**:

- **max aspect ratio 608.215** at all three levels
  (`verification/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md:305-306`, and the same
  608.215 recorded for `W4-m6-reordering/m6_rcm` at :331);
- **max non-orthogonality 61.4935** at the sibling levels recorded in
  `RUNG1_M6_R2_PREREGISTRATION.md` §2.1.

**That set is a STRETCHING-RATIO SWEEP, not a refinement family.** It is named here so it can
never be re-imported as a grid ladder.

### 1.3 THE 390-FACE SURFACE IS CONDEMNED, AND THE MECHANISM IS **NOT** ESTABLISHED

One surface file, sha256 **`aab44d4174d598bf8a9531def9607409099a3711832cac67f9d93538240b2326`**,
underlies two volume meshes built under **completely different** normal-direction parameters. It
produced negative-volume cells and an `e+95` aspect ratio **both times**:

| build | `s0` | `N` | `marchDist` | cells | neg-vol cells | max AR | max non-orth | max skew |
|---|---|---|---|---|---|---|---|---|
| `A3-onera-m6-adjoint-vcoarse` | 1.0e-4 | 65 | 12.0 | 24,960 | **23** (min −3.30275e-09) | **2.07741e+95** | **135.318** | **55.378** |
| `RUNG1_M6_R2_runs/L3` | 4.0e-4 | 24 | 50.0 | 8,970 | **2** (min −4.42594e-09) | **1.25943e+95** | **109.219** | — |

Sources: `verification/runs/MESH_AUDIT_runs/2026-08-08/A3-onera-m6-adjoint-vcoarse__constant__polyMesh.log.checkMesh`;
`verification/runs/RUNG1_M6_R2_runs/L3/log.checkMesh`. Surface identity checked by hash, not by
path: `sha256sum` of `A3-onera-m6-adjoint-vcoarse/surfaceMesh.cgns` and of
`RUNG1_M6_R2_runs/L3/work/surfaceMesh.cgns.sha256`'s recorded value both give `aab44d41…2326`.
A third instrument agrees independently: pyHyp's own march log announced the failure before any
`checkMesh` — `A3-onera-m6-adjoint-vcoarse/logMeshGeneration.txt:19` prints
**`Min Quality = −0.34602` at marching level 2**, falling to `−1.00000` with negative `Min
Volume` at levels 3–9.

> **THE 390-FACE SURFACE CANNOT BE THE COARSE LEVEL OF ANYTHING, AND THIS REGISTRATION DOES NOT
> USE IT.**
>
> ⚠ **THE MECHANISM IS NOT ESTABLISHED AND IS NOT GUESSED AT.** Two measurements are placed side
> by side. **No cause is claimed.** A plausible story (tip-region surface cells too coarse for
> the hyperbolic march to keep convex) exists and is **deliberately not written into this
> document as a finding**, because nothing on this box tests it. What is established is the
> **fact of repetition under two different parameter sets**, and that is sufficient to condemn
> the surface without a mechanism.

### 1.4 A FAMILY IS NOT A FAMILY UNTIL ITS LEVELS ARE HASHED

**Measured hazard on this box:** `DPW5_L1T_{hex,prism,hybrid}` were proved **byte-identical in
`constant/polyMesh/points`** — sha256
`870e6c6fceab6dbeea0d6494793fcbb7dd7f41c8e92056814c5398938d51f7fd`, 24,857,286 bytes each. They
are **one node set in three cell types.** A Roache triple over them would have measured cell-type
sensitivity while calling itself refinement.

> **EVERY LEVEL IN THIS REGISTRATION CARRIES ITS UNCOMPRESSED `constant/polyMesh/points` sha256
> AS A REGISTERED GATE ITEM (Gate A, §5).** The hash is taken on the **decompressed** byte stream,
> because every M6 mesh on this box stores `points.gz` and a gzip hash also encodes the
> compressor's settings and mtime, which are not the mesh.

### 1.5 🔴 THE LAB NOW HOLDS A BLUNT-TRAILING-EDGE M6, AND THE ×4 FAMILY'S OWN GEOMETRY HAS NEVER BEEN CHECKED

**Finding of the cfd supervisor, 2026-09-03, from a concurrent lane's reading of the CGNS grid at
§2.1, with the load-bearing parts verified by the supervisor personally. Relayed here as a
finding with its measurements, not as this lane's own measurement.**

`onera_m6.cgns` is the AGARD M6 to machine epsilon on the load-bearing dimensions — **leading-edge
sweep 30.0000000°** with a straight-edge residual of **3.8e-13**, **semispan exactly 1.1963 m** —
**and it carries the BLUNT trailing edge: `t_TE/c = 0.0014104` at the root**, matching AGARD Table
B1-1's doubled final ordinate to seven significant figures, under a planted control confirming the
reader measures the strip. Its root section matches the published profile about **ten times
tighter** than the SU2 grid `M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` §4.3 measured:
**max │Δz│/c 6.99e-05 against 6.78e-04.** `M6I` §5.6 listed blunt-TE as **open and never
attempted**; the lab now holds one.

> 🔴 **THE QUESTION THIS RAISES SITS DIRECTLY UNDER SANAA'S NAMED DELIVERABLE, AND NOBODY HAS
> ASKED IT: DO THE THREE SURFACES OF THE ×4 FAMILY HAVE A SHARP OR A BLUNT TRAILING EDGE, AND HOW
> CLOSELY DO THEY MATCH THE AGARD SECTION?**
>
> **If our surfaces are sharp-TE while AGARD is blunt, then `Cp` near the trailing edge is
> systematically wrong BY CONSTRUCTION, and a `Cp`-vs-AGARD comparison would be measuring our own
> geometry error and calling it a validation result.** That is a **validation-relevant geometry
> defect that no cost figure and no grid-convergence study would ever surface** — a family can
> converge beautifully onto the wrong wing.

**This registration therefore adds a GEOMETRY-FIDELITY GATE (`Gate GF`, §5), graded BEFORE any
solve.** Its outcome is not predicted here.

**⚠ AND THE SHORTCUT THAT IS EXPLICITLY REFUSED, recorded as a standing prohibition on this
ladder.** The CGNS surface is **NOT** a drop-in replacement for a level of the ×4 family. That
family's validity rests entirely on its three surfaces being **×4 coarsenings of one another from
ONE generator** (§2.2). **Substituting a differently-sourced surface at any level breaks exactly
the property the family exists to have** — it would reintroduce, in the surface direction, the
same "levels that differ in more than resolution" defect that §1.1 and §1.4 condemn.

> **RULED: `onera_m6.cgns` is used as an INDEPENDENT GEOMETRY REFERENCE, and as a candidate source
> for future from-scratch surface generation. NEVER AS A LEVEL OF THIS FAMILY.**

### 1.6 🔴 THE AGARD SECTION TABLE IS **NOT ON THIS BOX**, AND THE NEAREST FILE IS THE SHARPENED ONE

> ### ⚠ CORRECTED 2026-09-03 — THE HEADING ABOVE IS **WRONG** AND IS LEFT STANDING ON PURPOSE.
>
> **The MACHINE COPY was absent; TABLE B1-1 ITSELF WAS ON THIS BOX THE WHOLE TIME**, printed at
> **PDF page 333 / printed page `B1-7`** of
> `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`. The `find`
> below was **correct**; the inference drawn from it was **too wide**, because the table's numeric
> body never reached the PDF's OCR text layer and **no filename search or text grep can see a
> table that exists only as page pixels.**
>
> **The reasoning below is NOT deleted, because it is still the whole motivation for control
> C19** — the sharpened-lookalike trap it identifies is real, and the acquisition made it
> **worse** (§5: two distinct sharpened derivatives, one of them at a URL adjacent to the true
> table). **`GF2` is now GRADEABLE against a pinned reference; see §5.**
>
> This is a **pre-compute amendment** under rule 2: the document is an unfrozen DRAFT and both
> registered run roots were confirmed absent at the moment of the edit (§5).

**Measured by this lane while building `Gate GF`, and it is a trap that would have fired.**

`M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` §4.3 graded its root section against a machine
copy of Table B1-1 named `profile_M6_streamwise_alongy=0.dat`, **72 points, verified row-by-row
against the printed page before use.** **A `find` over all of `/home/ubuntu` returns ZERO copies
of that file.** It was read during a network-egress session and **not retained.**

**The only M6 section table on this box is
`verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat`** (sha256
`0a60e747a0a7b747cc52b7937c4f1e347e66f04e51a9e61bd5eb2bbe3d90eebc`), and this lane read its
structure rather than its name: a `63` header, then 63 `x/c` values, then 63 `z/c` values. Its
last three `(x/c, z/c)` pairs are

```
    (0.9578511, 0.0059224)     (1.0000000, 0.0007052)     (1.0055000, 0.0000000)
```

> **It carries AGARD's exact final design ordinate `0.0007052` at `x/c = 1.0` — and then appends
> an extra point at `x/c = 1.0055`, `z/c = 0` that SHARPENS IT.** `t_TE/c = 0.000000` on this
> file. **It is the SHARPENED section, not Table B1-1**, exactly as its own filename says and
> exactly as a hurried reader would miss.
>
> 🔴 **A LANE THAT GRABBED THE NEAREST-LOOKING SECTION FILE WOULD GRADE A SHARP SURFACE AGAINST A
> SHARP REFERENCE AND REPORT PERFECT AGREEMENT.** That is the reference-side twin of the
> instrument-rejection discipline `Gate GF` inherits, and it is why `GF2` below is registered
> **`BLOCKED`** rather than assumed gradeable.

**A corroboration worth keeping, because two independent artifacts agree on the mechanism.** The
appended point sits at `x/c = 1.0055` — a **+0.55 %** chord extension. `M6I` §4.2 independently
measured the sharpened-geometry root chord as **810.491484086 mm** against AGARD's derived
**806.156 mm**, **+0.538 %**. **The two agree to within 0.01 % of chord.** The sharpening is a
**chordwise extension of both surfaces to a point**, and this is now established by the section
file's own coordinates as well as by the planform arithmetic.

---

## 2. THE TWO ROUTES, COSTED FROM MEASURED RATES

**The measurement picked, and it picked Route B.** Route A was investigated by a concurrent lane
while this document was in draft; **it is now CLOSED as a volume-grid family on two independent
measured grounds, and its closure is written below as a finding rather than left open as though
more work would settle it.** Route B's cost basis is measured and complete.

### 2.1 ROUTE A — THE PUBLISHED CGNS. **CLOSED. `GATE FAIL` ON THE THREE-LEVEL REQUIREMENT.**

| what | value |
|---|---|
| path | `/home/ubuntu/certonomous-runs/W5-idwarp-source/input_files/onera_m6.cgns` |
| size | **5,345,280 B** |
| sha256 | **`e4257acfc851509982614138c9cab7e7873bf04b239691858d624e0d55e54c98`** |
| container format | **ADF, not HDF5** — the file's own header reads `ADF Database Version A02011>`, stamped `AdF0 Tue Jan 18 16:25:03 2022` |
| mtime | 2022-01-18 |

**THE READER IS NOT THE OBSTACLE, AND THAT WAS CHECKED BEFORE ANYTHING WAS CONCLUDED FROM A
FAILURE TO READ.** The ADF container was the suspected blocker — many current CGNS builds ship
**HDF5-only**. It is not: ParaView ships the vendored CGNS mid-level library with the ADF layer
compiled in, and **`vtkcgns_ADF_Database_Open`, `vtkcgns_cgio_open_file` and
`vtkcgns_cgio_get_file_type` are exported from `libvtkcgns-pv5.13.so`.** **The file was read.**

**Route A fails on two independent grounds instead. Both are measurements.**

| # | ground | measurement |
|---|---|---|
| **A-F1** | **IT IS ONE GRID, NOT A FAMILY** | Every zone carries a single **`_L3`** tag; **no `_L1` or `_L2` exists anywhere in the tree.** A `find` over `/home/ubuntu` returns **exactly two** `onera_m6*.cgns` files and they are **byte-identical** (sha256 `e4257acf…4c98`, 5,345,280 B). ⚠ **The negative is evidence, not blindness: that search carried a planted control which fired on 12 level-named directories** (rule 3). |
| **A-F2** | **IT IS AN OVERSET (CHIMERA) GRID** | **20 structured zones in three spatially overlapping components** — `far_L3` 6 zones, `near_wing_vol_L3` 3, `near_tip_vol_L3` 11 — **185,664 cells INCLUDING OVERLAP**, joined only by **20 `UserDefined` BCs under `FamilyName Overset`**, with **no 1-to-1 connectivity between components.** |

> ## **ROUTE A: `GATE FAIL` on `MESH_STANDARD.md` §9.1's three-level requirement.**
>
> **A-F1 alone is decisive**: §9.1 fixes three levels as both the minimum and the sufficient count
> for a gate, and this artifact supplies **one**. A one-level artifact cannot produce an observed
> order, a GCI, or a band, whatever its quality.

**A-F2 is recorded because it closes the route a second way and because a future lane will
otherwise propose importing it.** `plot3dToFoam` on this grid would yield **three topologically
disconnected, spatially overlapping regions.** Solving it needs OpenFOAM's **overset machinery**
and a solver from the **overset family**, which this ladder does not use and this registration
does not adopt. **That is an engineering change, not a line item.**

> 🔴 **THE IMPORT COST IS NOT THE OBSTACLE, AND IT IS NAMED SO NOBODY RE-OPENS THE ROUTE ON COST
> GROUNDS.** The mechanical import prices at **≈ 0.7 core-min** — genuinely negligible, and **the
> least important number in this analysis.** Route A is closed on **structure**, not on spend.
> **No amount of budget buys a second and third level out of a one-level file.**

**Recorded plainly, because it is the strategic disappointment of this ladder.** Sanaa's own
enumerated list (`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md` §6,
lines 118–126) names *"use a published M6 grid family"* as **option 1, "option 1 this week"**, and
this ladder's budget has been spent several times over on her option 3 while option 1 sat unused.
**Option 1 has now been reached, and the artifact this box holds is not a family.** That is worth
stating without softening: **the cheapest route to Sanaa's named deliverable has been tested and
is not available from what is on disk.** A genuinely published multi-level M6 family, if one can
be obtained, remains a better instrument than anything this lab builds — but obtaining one is
network egress and is **not** authorised by this registration.

**What Route A DID buy, and it is not nothing:** an **independent geometry reference** of
exceptional quality (§1.5) and the geometry-fidelity gate that reference makes possible (§5,
`Gate GF`). **That is a larger contribution to the validity of Sanaa's deliverable than a third
grid level would have been**, because it tests whether this ladder is solving the right wing at
all.

**A DISCLOSURE ABOUT THIS LANE'S OWN PREDICTION.** Before the concurrent lane reported, this
draft carried a speculation that the file would prove to be *"a SINGLE grid, not a family."*
**That speculation was half right and it is NOT scored as a hit**: it named `A-F1` and **entirely
failed to anticipate `A-F2`**, the overset topology, which is the ground with the larger
engineering consequence. **It is recorded here as a superseded speculation rather than kept in
§11 as a prediction**, because a prediction cannot be graded against a measurement that arrived
before the freeze.

### 2.2 ROUTE B — EXTEND THE SURFACE-×4 FAMILY UPWARD. **COMMITTED. COST BASIS MEASURED.**

**Two admissible levels already exist on disk, and they are a demonstrated ×4 pair.**

| existing level | surface faces | cells | `s0` | `N` | `marchDist` | max non-orth | max skew | max AR | regions | boundary openness |
|---|---|---|---|---|---|---|---|---|---|---|
| `A3-onera-m6-adjoint-coarse` | 1,560 | **99,840** | 1.0e-4 | 65 | 12.0 | **61.4938** | 2.30655 | 608.207 | 1 | 4.32e-16 |
| `.mesh-cache/onera_m6` | 6,240 | **399,360** | 1.0e-4 | 65 | 12.0 | **61.1581** | 1.44081 | 222.355 | 1 | 4.66e-17 |

Sources: `verification/runs/MESH_AUDIT_runs/2026-08-08/A3-onera-m6-adjoint-coarse__constant__polyMesh.log.checkMesh`
and `.../mesh-cache__onera_m6__polyMesh.log.checkMesh`. Build parameters read from each
directory's own `genWingMesh.py`. Patch identity on the 399,360 level read from its own
`constant/polyMesh/boundary`: **`wing`(wall) / `inout`(patch) 6240 / `sym`(symmetry)** — three
correctly typed patches, so §7's ill-posedness screen is already satisfied there.

**The three parameters that set the normal direction — `s0 = 1.0e-4`, `N = 65`, `marchDist =
12.0` — are IDENTICAL at both levels. Only the surface differs.** By §1.1's equation with
`N−1 = 64` layers, this lane's root-solve gives

```
    r  =  1.167442      at BOTH levels, exactly, because (s0, N, marchDist) are identical
```

and the layer count is identical, so **`cells / wing_faces = 64` at both levels** (99,840/1,560 =
64.0; 399,360/6,240 = 64.0). **The wall-normal discretisation is not merely similar between these
levels. It is the same.** That is §6's honest label, and it is also §1.1's theorem being
*satisfied by construction* rather than fought.

**THE NEW LEVEL, AND WHY IT IS NOT A NEW MESH RECIPE.** The published DAFoam tutorial's own
`preProcessing.sh` (`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/preProcessing.sh`,
lines 21-23, read verbatim) does this:

```
    # coarsen the surface mesh two times
    cgns_utils coarsen m6_surfaceMesh_fine.cgns surfaceMesh.cgns
    cgns_utils coarsen surfaceMesh.cgns
```

The master `m6_surfaceMesh_fine.cgns` — **sha256
`197efa09d838b276a8967da9532d9c4d57edca18cb777bd640257606d2d83327`**, 2,535,424 B, mtime
2020-06-28, downloaded from `github.com/dafoam/files` releases v1.0.0 and unmodified — carries
**99,840 faces** (measured: `RUNG1_M6_R2_runs/L1/log.pyhyp:6` reads `Total Faces: 99840` on a file
whose recorded sha256 is exactly `197efa09…`). The tutorial's **first** `coarsen` therefore emits
**24,960 faces**, and its **second** emits the 6,240 that the 399,360-cell mesh was built on
(sha256 `818e8307ae8299af7a04e10b8b4c7dc6fe299a8c280717502c1c8a6ff1caea2d`).

> 🔴 **THE 24,960-FACE SURFACE IS NOT INVENTED BY THIS LAB. IT IS THE PUBLISHED TUTORIAL'S OWN
> INTERMEDIATE, discarded by its second `coarsen` call.** Route B produces it with **one**
> invocation of the tutorial's own first line, on the tutorial's own master file at a pinned hash.
> **Nothing is interpolated, refined, or synthesised.**

The full ×4 surface lineage on this box, every member hash-pinned:

| faces | sha256 (full) | provenance |
|---|---|---|
| **99,840** | `197efa09d838b276a8967da9532d9c4d57edca18cb777bd640257606d2d83327` | downloaded master, unmodified |
| **24,960** | *to be produced by `cgns_utils coarsen` from the master; its hash is a registered Gate A output* | **the new level's surface** |
| **6,240** | `818e8307ae8299af7a04e10b8b4c7dc6fe299a8c280717502c1c8a6ff1caea2d` | master, coarsened ×2 |
| **1,560** | `1e11aae4e0e5a4caaffeb63f98a2626734075fb486de8dca93e32f554d143921` | master, coarsened ×3 |
| **390** | `aab44d4174d598bf8a9531def9607409099a3711832cac67f9d93538240b2326` | master, coarsened ×4 — **CONDEMNED, §1.3, NOT USED** |

**THE REGISTERED FAMILY.** Route B builds **exactly one** new level, at `s0 = 1.0e-4`, `N = 65`,
`marchDist = 12.0` **unchanged**:

| level | surface faces | cells | status |
|---|---|---|---|
| **L3** (coarse) | 1,560 | **99,840** | **exists**, re-checked by this registration, not rebuilt |
| **L2** (medium) | 6,240 | **399,360** | **exists**, re-checked by this registration, not rebuilt |
| **L1** (fine) | **24,960** | **1,597,440** | **BUILT BY THIS REGISTRATION — one generator call** |

`24,960 × 64 = 1,597,440`. Cell ratios **exactly 4.000 and 4.000** on integers.

> **CONSTRAINT 1 IS SATISFIED STRUCTURALLY, NOT ARGUMENTATIVELY.** One generator call, at three
> normal-direction parameters that are byte-identical to the two existing levels'. `r = 1.167442`
> and `cells / wing_faces = 64` at **all three** levels **by construction**, so `r` cannot move.
> There is no parameter this registration varies in the normal direction, and therefore no
> distribution change for §1.1's theorem to bite on.

### 2.3 THE RULING BETWEEN A AND B — RESOLVED, AND THE RESOLUTION PATH IS SHOWN

**The condition was written into this draft BEFORE the concurrent lane reported, in three cases,
so it could not be chosen to fit the report.** It is reproduced here with its outcome marked,
rather than deleted, so a reader can see the ruling was not reverse-engineered:

| case, as registered before the report | outcome |
|---|---|
| **(1)** readable **and** a multi-level family that refines in all three directions → Route A is the better instrument, **this registration is SUPERSEDED by a further successor at a new path**, never amended into Route A | **DID NOT FIRE** — `A-F1`: one level |
| **(2)** a single grid, or a surface, or unreadable → Route A cannot supply a family, **Route B proceeds as registered** | ✅ **FIRED** — `A-F1` and `A-F2`, §2.1 |
| **(3)** ambiguous or incomplete → Route B proceeds, Route A stays **`PENDING`** | did not fire; the lane completed with a planted control |

> **CASE 2 FIRED. ROUTE B PROCEEDS AS REGISTERED, AND NOTHING IN THIS DOCUMENT CHANGED AS A
> RESULT OF THE REPORT** except the addition of `Gate GF` (§5) and constraints §1.5–§1.6, **none
> of which alters a Route B gate, threshold, cap or label.** Route A's certificate cell reads
> **`GATE FAIL`**, not `PENDING`. ⚠ **This document is still a DRAFT and unfrozen, so these are
> pre-freeze amendments, legal under rule 2's before-first-compute clause — the condition is
> stated above and the way it was checked is §2.1's two measured grounds.**

### 2.4 COST — BOTH ROUTES, FROM MEASURED RATES

**Unit: core-minutes** (wall s × ranks ÷ 60). **Dollars are DERIVED, NOT MEASURED**, at
`c7a.4xlarge` **$0.0513/core-h**, owner-stated 2026-08-21/22 — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so any dollar figure originating on this box is
**reported-by-owner**.

**Rate basis, and the honesty label each one carries:**

| rate | value | basis, and what is wrong with it |
|---|---|---|
| converter | **0.1786 core-min/Mcell** | **MEASURED**, `verification/campaign/RUNG0b_MESH_IMPORT_PREREGISTRATION.md:222` — 81 wall s over 7.560154 Mcell. ⚠ **It is a `ugrid_to_foam.py` rate applied to a `plot3dToFoam` conversion. Different program, different input format.** Registered as the best available basis and labelled as an off-basis transfer, not as a measurement of `plot3dToFoam`. |
| `checkMesh` | **0.0661 core-min/Mcell** | **MEASURED**, same line — 30 wall s over the same 4 grids. ⚠ **A RECONCILIATION, stated so nobody re-derives it wrongly:** that line's prose says `checkMesh` "measured 0.33×" the converter, but its own measured pair gives **0.0661 / 0.1786 = 0.370×**, not 0.33×. **This registration uses the measured 0.0661, the larger and more conservative of the two, and records the 11 % discrepancy in the source rather than silently picking.** |
| pyHyp march | **three measured bases, all reported** | see below |
| solve | **3.40e-8 core-min/cell/iteration** | **MEASURED on this exact geometry and solver class**: `A3-onera-m6-transonic/run_model_run3.log`, 399,360 cells, `Time` 1 → 6000, recorded at `M6I_PREREGISTRATION.md:698` as 3.36e-8 span / **3.40e-8 whole-run**. The whole-run figure is used. |

**pyHyp march — three measured bases, and the estimate is the central one, not the flattering
one.** Rates derived by this lane from the `CPU` column of the R2 logs, per face per layer:

| basis | measured rate | implied cost at 24,960 faces × 64 layers |
|---|---|---|
| L3 average (390 faces, 24 steps, 1.0 s) | 1.068e-4 s/face-layer | 2.84 core-min |
| L2 average (1,560 faces, 47 steps, 9.4 s) | 1.282e-4 s/face-layer | 3.41 core-min |
| **log-interpolated to 24,960 faces** | **2.644e-4 s/face-layer** | **7.04 core-min ← REGISTERED ESTIMATE** |
| L1 average (99,840 faces, 54 steps, 2046.4 s) | 3.796e-4 s/face-layer | 10.11 core-min |
| **L1 marginal (last 10 steps, 86.62 s/step)** | **8.676e-4 s/face-layer** | **23.10 core-min ← the CAP's basis** |

**pyHyp cost is strongly superlinear in face count and rises within a single march** (the L1
marginal rate is 2.3× its own running average at step 54). The registered estimate uses the
log-interpolated rate at the actual face count; **the cap is 3× the most pessimistic measured
basis.** Both are stated so the calibration row in §9.3 can attribute a miss to the right one.

**THE REGISTERED COST TABLE.** Iteration schedule **3,000 / 4,000 / 5,000** at L3 / L2 / L1.

| step | what | est. core-min | **cap (core-min)** | derived $ at cap | ranks / decomposition |
|---|---|---|---|---|---|
| `B0` | **`Gate GF` geometry fidelity** (§5): `t_TE/c`, root section, sweep, semispan, on three surfaces + controls C17–C19. Host arithmetic on surface files. | **0.10** | **1.0** | $0.00086 | serial |
| `B1` | `cgns_utils coarsen` master → 24,960-face surface, one call | **0.05** | **1.0** | $0.00086 | serial |
| `B2` | pyHyp march, 24,960 × 64 | **7.04** | **70.0** | $0.05985 | serial (pyHyp runs 1 rank) |
| `B3` | `plot3dToFoam` + `autoPatch 60` + `createPatch` + `renumberMesh` on 1.59744 Mcell | **0.29** | **3.0** | $0.00257 | serial |
| `B4` | `checkMesh` ×3 (2.09664 Mcell total) + points-hash family proof + planted controls | **0.14** | **2.0** | $0.00171 | serial |
| `B5a` | solve L3, 99,840 cells × 3,000 it | **10.18** | **31.0** | $0.02651 | `hierarchical (4 1 1)` |
| `B5b` | solve L2, 399,360 cells × 4,000 it | **54.31** | **163.0** | $0.13937 | `hierarchical (8 1 1)` |
| `B5c` | solve L1, 1,597,440 cells × 5,000 it, **incl. a named ×2.0 superlinear allowance** | **543.13** | **1,630.0** | $1.39365 | `hierarchical (16 1 1)` |
| `B6` | grade: family proof → Roache-shaped analysis → Gate P. Host arithmetic. | **~0** | **2.0** | $0.00171 | serial |
| | **TOTAL** | **≈ 615.2** | **1,903.0** | **≈ $1.6270 DERIVED** | |

**`B0` runs FIRST and its result does not gate the launch** — `GF1` failing is governed by the
§5 ruling, not by a stop. **It runs first so that the finding exists before the spend, not
after.**

**THE ×2.0 SUPERLINEAR ALLOWANCE ON `B5c`, NAMED RATHER THAN BURIED.** The 3.40e-8 rate's own
basis **is** the 399,360-cell mesh, so `B5b` sits exactly on its basis and `B5a` extrapolates
**downward** (the safe direction). `B5c` extrapolates **upward by 4×** in cell count, and this
box has a measured record of a bare per-cell rate failing in exactly that direction:
`docs/COST_CALIBRATION.md:408` records the JF1 unit rate as **1.448× optimistic at 90k cells and
5.84× optimistic at 455k**, from a 40k-cell basis. **A ×2.0 allowance for a 4× extrapolation is
therefore an allowance, not a prediction of contention, and it is stated as such.** ⚠ **The
mechanism (working set outgrowing cache) is INFERRED, not instrumented — no PMU counter is
collected here and none is claimed.**

**All-in: 615.1 core-min estimated, 1,902.0 core-min capped, $1.63 DERIVED at cap.** Under the
$25 pre-authorisation, and **still costed**, because a blanket is not a per-item reading (rule 9).

### 2.5 THE FLEET SAFETY CEILING

> **CEILING FOR `B5c` = min(3 × 1,630.0, remaining envelope) = 4,890 core-min = $4.181 DERIVED.**
> The $1,000 standing envelope is 1,169,591 core-min at the recorded rate, so **3× the cap is the
> binding term.** At the ceiling the monitor stops the run **gracefully, regardless of residual
> trend.** The ceiling is protection against the box being eaten; it is not a second budget, and
> **an overrun of the CAP stops the run** (rule 12) well before the ceiling is reached.

---

## 3. THE STATE PAIR — RULED, WITH ITS FULL RATIONALE

**AGARD AR-138 test 2308** fixes **M∞ = 0.8395**, **α = 3.06°**, **Re = 11.72 × 10⁶ on the MAC
`c = 0.64607 m`**, `S_ref = 0.7532 m²`. Read from the machine file's own zone title, never from
the OCR sidecar (§4.1).

**Those two dimensionless numbers fix only a PRODUCT.** `Re = ρ U c / μ` with `U = M·√(γRT)`
constrains `ρ√T/μ`; it does not determine `T∞` and `p∞` separately. **That gap is why this is
registered rather than left to whoever writes the case files.**

### THE RULING — ISA SEA LEVEL, WITH `μ` BACK-SOLVED

**Ruled by the cfd supervisor.** Registered values, and the arithmetic shown so a reader can
reproduce every one:

| quantity | value | how obtained |
|---|---|---|
| `T∞` | **288.15 K** | **REGISTERED CHOICE** (ISA sea level) |
| `p∞` | **101 325 Pa** | **REGISTERED CHOICE** (ISA sea level) |
| `γ` | **1.4** | registered |
| `R` | **287.058 J/(kg·K)** | registered — **the value matters**; `287.0` would shift `μ` in the fifth figure |
| `Pr` | **0.72** | registered |
| `a∞ = √(γRT)` | **340.297029 m/s** | derived: `√(1.4 × 287.058 × 288.15)` |
| `U∞ = M·a∞` | **285.679356 m/s** | derived |
| `ρ∞ = p/(RT)` | **1.224978126 kg/m³** | derived |
| **`μ∞`** | **1.929120e-05 Pa·s** | **BACK-SOLVED**: `μ = ρUc/Re = 1.224978126 × 285.679356 × 0.64607 / 11.72e6` |
| `ν∞ = μ/ρ` | **1.574820e-05 m²/s** | derived |

**Re check, closing the loop:** `1.224978126 × 285.679356 × 0.64607 / 1.929120e-05 = 1.1720e7`
**exactly, by construction.**

**Three justifications, and the third is what makes this honest rather than arbitrary.**

**(a) IT IS A CHOICE, NOT A MEASUREMENT FROM AR-138. In those words.** AR-138 B1-3 §3.7 records
the tunnel stagnation temperature as **292–315 K** and states it *"cannot be controlled"*. **No
`T∞` or `p∞` for run 308 is recoverable from the report.** The pair below is **selected by this
lab**, and any document that cites it as an AR-138 measurement is wrong.

**(b) IT HAS PRECEDENT IN THIS LAB'S OWN FROZEN TEXT.** `RUNG1_M6_R2_PREREGISTRATION.md` §3
already registered exactly this pair, in exactly this form, with `μ` back-solved and labelled:
*"`T∞ = 288.15 K`, `p∞ = 101 325 Pa` (ISA, **chosen not measured**) … **`μ∞` back-solved to
deliver Re = 11.72e6 — `μ` reproduces `Re`; it is not a physical property of air at 288.15 K.**"*
That file is **cited, not amended.** Using the same pair keeps this ladder comparable to
anything the predecessor produced, at zero cost.

**(c) IT IS A GAUGE CHOICE THAT CANNOT CONTAMINATE THE ANSWER — and this is why registering it
explicitly costs nothing in generality.** For a **perfect gas** at matched `M`, `Re`, `γ` and
`Pr`, over a **fixed geometry**, the non-dimensional governing equations and boundary conditions
are identical for every `(T∞, p∞)` pair satisfying that `Re`. **The `Cp` distribution is
therefore invariant to the state pair.** Choosing ISA does not select an answer; it selects
**units**. What it *buys* is **exact reproducibility** — a second party can regenerate every `0/`
field byte-for-byte from the six registered numbers above, which is impossible from `M` and `Re`
alone.

> ⚠ **THE BACK-SOLVED `μ` IS NOT A PHYSICAL AIR VISCOSITY AT 288.15 K, AND THIS REGISTRATION
> LABELS IT SO ON ITS FACE.**
>
> **Measured comparison, computed by this lane:** Sutherland's law at 288.15 K
> (`μ₀ = 1.716e-5`, `T₀ = 273.15`, `S = 110.4`) gives **μ_phys = 1.789298e-05 Pa·s**. The
> registered back-solved value is **1.929120e-05 Pa·s** — **1.078144×, i.e. 7.81 % HIGH.**
>
> **`μ∞ = 1.929120e-05` is a NUMBER CHOSEN TO REPRODUCE `Re = 11.72e6` AT THE REGISTERED STATE
> PAIR. It is not a property of air. Any document, figure, table or certificate that cites it as
> an air viscosity is citing it wrongly**, and the 7.81 % gap above is the size of that error.
> **This paragraph travels onto the certificate.**

**Solver and closure.** `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST**, fully
turbulent, **`nutUSpaldingWallFunction`** — continuous across the whole `y⁺` range, so the
discrete wall operator cannot change part-way along the family.

**Carried forward so it cannot be re-confused:** NASA TMR's page gives `Re_c_root = 14.6e6` on the
**root** chord; `14.6e6 × 0.64607/0.810491 = 11.64e6`. **This ladder uses Re = 11.72e6 on the
MAC. Applying 14.6e6 to the MAC would be wrong by 25 %.**

### 3.1 `y⁺` — A PREDICTION FROM A CORRELATION, NEVER A MEASUREMENT

`s0 = 1.0e-4 m` is the first **layer thickness**, so the first cell **centre** sits at 5.0e-5 m.
Flat-plate correlation `c_f = 0.026/Re^(1/7)` gives `c_f = 0.002542`, `u_τ = 10.1842 m/s`, hence

> **`y⁺` ≈ 32.3 at the first cell centre** (and 64.7 at the first layer top).

**DERIVED FROM A FLAT-PLATE CORRELATION, NOT MEASURED.** It corroborates the lab's standing
statement that *"every existing pyHyp M6 mesh was extruded at `s0 = 1.0e-4` and sits at `y⁺ ≈
33`"* (`M6S_P_PYHYP_WALL_RESOLVED_PROBE_PREREGISTRATION.md` §1). **The only honest `y⁺` is the one
the solver prints from the converged field, and it does not exist yet.**

**`y⁺` IS THE SAME AT ALL THREE LEVELS, BY CONSTRUCTION, AND THAT IS THE POINT** — it is the
direct consequence of §2.2's identical normal-direction parameters, and it is the reason §6's
honest label is what it is. **A `y⁺` in the tens is this route working as designed, not failing.**

### 3.2 NUMERICAL SETTINGS — REGISTERED, NOT SILENTLY PICKED

| setting | value | why |
|---|---|---|
| `snGradSchemes default` | `limited corrected 0.5` | bounds the explicit non-orthogonal correction so it cannot destroy diagonal dominance where the correction is large |
| `laplacianSchemes default` | `Gauss linear limited corrected 0.5` | same correction, same limiter, consistently applied |
| `nNonOrthogonalCorrectors` | **2** | at a predicted ~61.5° the explicit correction is not small; 0 correctors loses diffusion accuracy first and boundedness second |
| `divSchemes div(phi,U)` | **`bounded Gauss linearUpwind grad(U)`** | second order with a gradient limiter; first order would not resolve the shock position Gate P is graded on |
| `divSchemes div(phi,k)`, `div(phi,omega)` | **`bounded Gauss upwind`** | boundedness of `k`/`ω` bought deliberately at first order |
| `divSchemes div(phi,e)` | **`bounded Gauss upwind`** | **RULED HERE — see §8.2. In no prior M6 registration.** |
| `divSchemes div(phi,K)` | **`bounded Gauss linear`** | **RULED HERE — see §8.2. In no prior M6 registration.** |
| `divSchemes div(((rho*nuEff)*dev2(T(grad(U)))))` | **`Gauss linear`** | **RULED HERE — see §8.2. In no prior M6 registration.** |
| `decomposition method` | **`hierarchical`**, coeffs per level in §2.4 | **the decomposition seed, satisfied by construction.** `hierarchical` is pure geometric bisection with **no RNG**, so the partition is a deterministic function of the recorded coefficient triple and the cell centres. **`scotch` is not reproducible run-to-run and is NOT used.** |

---

## 4. GATE P'S MAPPING DEFECT — A NAMED ASSUMPTION WITH A FALSIFIABLE DISCRIMINATOR

### 4.1 THE DEFECT, STATED EXACTLY

The reference file is `case_2308.dat`, sha256
**`020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0`**, 22,695 B, held at
`cases/dafoam/ladder-a/logs_A3/case_2308.dat` and byte-identical to NASA TMR's published copy
(`M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` §3.4). Its header, read verbatim:

```
    VARIABLES = "Section", "Tap", "X/L", "Z/L", "CP"
```

> 🔴 **THERE IS NO `Y` COLUMN AND NO `y/b` COLUMN. THE FILE CARRIES NO SPANWISE COORDINATE AT
> ALL.**

The mapping **section 1–7 → y/b 0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99** rests entirely on
**AGARD AR-138 §5.1.1 prose**, quoted at `M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md:210`:

> *"271 pressure orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96 and 0.99)"*

**That prose gives a SET of seven values. It does not state that data-file section 1 is the
y/b = 0.20 one.** **NO ARTIFACT ON THIS BOX CONFIRMS THE SECTIONS ARE ORDERED ROOT-TO-TIP.**

**REGISTERED ASSUMPTION `A-MAP`, with its source and its exact scope:**

> **`A-MAP`: data-file sections 1…7 correspond to `y/b` = 0.20, 0.44, 0.65, 0.80, 0.90, 0.96,
> 0.99 respectively — i.e. ROOT TO TIP in increasing section index.**
> **Source: AGARD AR-138 §5.1.1 prose, quoted above, PLUS an unstated ordering convention.**
> **Status: ASSUMED. Not measured. Not confirmed by any artifact this lab holds.**

**And the reason no better source can be reached, measured rather than asserted.** The AR-138 OCR
sidecar `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt` is
**unusable for this**: a targeted sweep for section-to-station ordering prose returns only the
§5.1.1 sentence already quoted, and **the numeric body of the report's tables is absent from the
text layer**. The sidecar's reliability on numerics is separately convicted — it renders this very
case's Mach as **`.9395`** against the machine file's **`0.8395`**, an 8 read as a 9, **12 % in
the freestream Mach of a transonic case**. 🔴 **THE AR-138 PDF IS PROVENANCE AND IS NEVER A SOURCE
OF NUMBERS.** Every Gate P reference value comes from `case_2308.dat` at the pinned sha256, and
**the comparator REFUSES if that hash does not match.**

### 4.2 🔴 THE DISCRIMINATOR THE BRIEF PROPOSED IS **MEASURED DEAD**, AND IS NOT REGISTERED

**The natural discriminator — that on a swept, tapered, twisted wing the per-section chordwise
extent and thickness distribution should vary monotonically with span, so the sections order
themselves — was tested by this lane against the file, BEFORE registering anything.** It fails,
and registering it would have registered a **vacuous** test.

**Measured, all seven sections, from `case_2308.dat` at the pinned hash:**

| section | taps | `X/L` extent (max − min) | `Z/L` thickness (max − min) |
|---|---|---|---|
| 1 | 34 | 0.98484 | 0.09775 |
| 2 | 34 | 0.98356 | 0.09775 |
| 3 | 34 | 0.98569 | 0.09776 |
| 4 | 34 | 0.98498 | 0.09776 |
| 5 | 45 | 0.98449 | 0.09772 |
| 6 | 45 | 0.98394 | 0.09771 |
| 7 | 45 | 0.98405 | 0.09771 |

> **Chordwise extent spans 0.98356 – 0.98569 — a total range of 0.22 %, NON-MONOTONE in section
> index. Thickness spans 0.09771 – 0.09776 — a total range of 0.05 %, and monotone only inside
> the noise.** There is **no span signal whatever**.

**And the reason is structural, not a data defect.** The ONERA M6 carries a **constant ONERA D
airfoil section with no twist**, and `X/L` / `Z/L` in this file are normalised by the **LOCAL**
chord. A geometry that is self-similar in span, expressed in locally-normalised coordinates,
**cannot** encode span. **The proposed discriminator is not weak here; it is empty.** It is
recorded as tested-and-rejected so that nobody proposes it again.

### 4.3 THE REGISTERED DISCRIMINATOR `D1` — SECTION NORMAL-FORCE ORDERING

**Registered, specified in full, and DELIBERATELY NOT EVALUATED BY THIS LANE.** Evaluating a
discriminator in the same act as registering it would let the rule be chosen to fit its own
answer. `D1` is evaluated **by the frozen comparator, at grading, and its result is printed
whichever way it comes out.**

**The quantity.** For each section `s`, from the **experimental** data alone:

```
    Cn(s)  =  −  ∮  CP  d(x/c)          around the closed tap loop of that section,
                                        trapezoidally, in the file's own tap ordering,
                                        closing the contour from the last tap to the first.
```

**The physical basis, and why it is robust rather than decorative.** A wing with a **free tip**
must carry a spanwise load that falls toward zero at the tip: there is no mechanism to sustain a
pressure difference across a surface that is open to the flow on three sides. Section 7 sits at
`y/b = 0.99` — **one hundredth of a semispan from the tip** — and section 1 at `y/b = 0.20`, deep
in the inboard, root-influenced region. **`Cn` at the tip station must be substantially below
`Cn` at the inboard station, and no plausible transonic mechanism reverses that ordering on this
wing at this incidence.**

**The falsification rule, fixed here, before evaluation:**

| measured outcome | verdict on `A-MAP` | consequence for Gate P |
|---|---|---|
| `Cn` **strictly decreasing** in section index **AND** `Cn(7)/Cn(1) ≤ 0.75` | **CORROBORATED** | Gate P grades under `A-MAP` as registered |
| `Cn` **strictly increasing** in section index **AND** `Cn(1)/Cn(7) ≤ 0.75` | **FALSIFIED** | **`A-MAP` IS REVERSED.** Gate P grades against the reversed mapping (section 1 → y/b 0.99 … section 7 → y/b 0.20), and the reversal is printed on the certificate as a registered finding, not as a repair |
| **anything else** — non-monotone, or a ratio inside (0.75, 1.333) | **INDETERMINATE** | **Gate P's PER-STATION channel is `NOT A RESULT`.** §4.5's order-independent channel is the only Gate P output |

**`Cn(7)/Cn(1) ≤ 0.75` is the registered threshold.** It is a **margin requirement**, not a mere
sign test: a 25 % drop is far larger than any plausible integration error over 34–45 taps, and
demanding it prevents a near-flat load distribution from being read as an ordering.

**⚠ THE CIRCULARITY DISCLOSURE, WHICH IS THE PART THAT MAKES `D1` MORE THAN A DISCLAIMER.**
`D1` uses the **same `CP` column that Gate P grades on.** It is **NOT independent of Gate P's
data**. It **IS** independent of Gate P's **CFD** — and that is the direction rule 2 cares about,
because the hazard rule 2 guards is a comparison chosen to fit **the answer the solver
produced**. `D1` is fixed here, before any solver runs, and is evaluated on experimental bytes at
a pinned hash. **That is the whole of its independence and this registration claims no more.**

**⚠ AND WHAT `D1` CANNOT DO.** It distinguishes **ordering**, not **assignment**. If the seven
sections were, say, a permutation that is neither the identity nor the reversal, `D1`'s
"anything else" branch fires and Gate P's per-station channel is `NOT A RESULT` — **it does not
attempt to recover the true permutation**, and this registration does not pretend it could.

### 4.4 `D2` — THE TAP-COUNT PARTITION, RECORDED AS AN OBSERVATION AND **NOT** A DISCRIMINATOR

Sections 1–4 carry **34** taps; sections 5–7 carry **45** (measured above; consistent with the
zone headers `I = 34/34/34/34/45/45/45` and with §5.1.1's total of 271). **This is a real
structural asymmetry and it is deliberately NOT registered as a discriminator**, because:

1. AR-138's usable text does **not** state which spanwise stations carry which tap count, and its
   OCR sidecar is convicted on numerics (§4.1);
2. the physical argument runs **both ways** — one instruments more densely outboard for the tip
   flow, or more densely inboard for the root double-shock — so it discriminates nothing.

**Named here so it cannot later be re-imported as evidence.** An asymmetry that admits two
opposite readings is not a test.

### 4.5 THE ORDER-INDEPENDENT CHANNEL — REPORTED, AND BINDING IN ONE DIRECTION ONLY

**So that an INDETERMINATE `D1` does not silently lose the whole deliverable**, the comparator
additionally computes the **set-to-set** assignment: the seven **experimental** section curves
against the seven **CFD** curves cut at the seven registered `y/b`, matched by minimum RMS `Cp`
difference over `x/c ≤ 0.90`, with the **optimal assignment printed in full**.

🔴 **THIS CHANNEL USES THE CFD, AND IS THEREFORE NEVER ALLOWED TO SET THE MAPPING FOR A GRADED
GATE.** Letting it do so would be exactly the "gate chosen to fit the answer" that rule 2 forbids.
Its registered force is **one-directional, and is stated precisely so it is not "evidence
annotated as non-binding"** — a printed discrepancy labelled diagnostic-only is worse than one
never computed:

> **If `D1` returns CORROBORATED but the set-to-set optimal assignment is NOT the identity, Gate
> P's per-station channel is `NOT A RESULT`.**
> **If `D1` returns FALSIFIED but the optimal assignment is NOT the reversal, Gate P's per-station
> channel is `NOT A RESULT`.**
> **This channel can only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`. It can never promote
> anything, and it can never repair a mapping.** That is standing rule 5's single permitted
> direction, applied here.

---

## 5. GATES, THRESHOLDS, CAPS, LABELS

**Every gate below carries a pre-registered threshold, a cap in core-minutes, and a label from
the fixed vocabulary — `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` /
`PENDING`.** `PENDING` is a queue/display state for "not yet run" and is **never** a softened
`GATE FAIL`. Only §7 blocks a launch.

### Gate A — mesh admission and family identity. Cap **2.0 core-min** (`B4`).

Read off the **named numeric maxima, never off a verdict string** — L-459: on this box
`checkMesh` prints `Non-orthogonality check OK.` at 88.889°, and its closing `Failed N mesh
checks` counts a different check entirely. **An absent `checkMesh` log reads `ABSENT`. It never
reads clean.**

| # | check | threshold | source | label on failure |
|---|---|---|---|---|
| A1 | max non-orthogonality, every level | **≤ 70°** | `MESH_STANDARD.md` §3.1 | `GATE FAIL`, reported, **non-blocking** |
| A2 | max skewness, every level | **≤ 4** | §3.2 | `GATE FAIL`, reported, **non-blocking** |
| A3 | max aspect ratio | **advisory 1000, never a lone rejection** | §3.3 | advisory only |
| A4 | cell-count ratios, both pairs | **exactly 4.000 on integers** (99,840 : 399,360 : 1,597,440) | §2.2 | `GATE FAIL` |
| A5 | **uncompressed `constant/polyMesh/points` sha256, all three DISTINCT** | **required** | §1.4 | **`NOT A RESULT`** — a family that is not a family is worse than no band |
| A6 | `cells / wing_faces == 64` exactly, every level | **required** | §2.2 | `GATE FAIL` — the identical-normal-direction claim is falsified |
| A7 | surface sha256 of every level's input recorded, and the 24,960 surface's hash **published** | **required** | §2.2 | `GATE FAIL` |
| A8 | **the condemned surface `aab44d41…2326` appears in NO level** | **required** | §1.3 | **`NOT A RESULT`** |
| A9 | patch identity per level: `wing`(wall), a symmetry plane typed `symmetry`, a farfield typed `patch` | **required** | §7 | **`BLOCKED`** — see §7 |

**A5's mechanics, because gzip would silently defeat it.** Every M6 mesh on this box stores
`points.gz`. The hash is taken on the **decompressed byte stream**; a gzip hash also encodes the
compressor's settings and mtime, which are not the mesh, and two identical node sets compressed
differently would report as distinct. **A5 fails open if this is got wrong, so the comparator's
planted control (§10) plants a single node perturbation and asserts the hash moves.**

### Gate GF — GEOMETRY FIDELITY. Graded **BEFORE any solve**. Cap **1.0 core-min** (new step `B0`).

**Why this gate exists, in one sentence:** a family can converge beautifully onto the wrong wing,
and no cost figure and no grid-convergence study would ever surface it (§1.5).

**Measured on each level's OWN surface** — `constant/polyMesh` for the two existing levels, and
the 24,960-face CGNS for the new one — at the root section (`y = 0` exactly), by the method
`M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` §4.2–§4.3 established.

| # | check | threshold | cap | label |
|---|---|---|---|---|
| **GF1** | **`t_TE/c` at the root, measured on the surface**, reported per level, against **AGARD Table B1-1's `0.0014104`** | **the value is REPORTED with its AGARD target; a level whose `t_TE/c` is within `±10 %` of 0.0014104 is `PASS`, and `t_TE/c < 1.0e-05` is `GATE FAIL` (sharp)** | 0.3 | `PASS` / `GATE FAIL` |
| **GF2** | **max │Δz│/c of the root section against Table B1-1**, over `0.001 ≤ x/c ≤ 0.999` | **≤ 1.0e-03** | 0.4 | `PASS` / `GATE FAIL` |
| **GF3** | **`t_TE/c` IDENTICAL across all three levels** to 1e-06 | required — the three surfaces are ×4 coarsenings of one generator (§2.2) and **must not differ in TE topology** | 0.2 | `GATE FAIL` |
| **GF4** | leading-edge sweep and semispan of each level's surface, against AGARD's **30.0000000°** and **1.1963 m** | reported; sweep within `±0.01°`, semispan within `±0.1 %` | 0.1 | `PASS` / `GATE FAIL` |

#### GF2 WAS REGISTERED **`BLOCKED`**. IT IS NOW GRADEABLE. THE REFERENCE IS PINNED.

> **PRE-COMPUTE AMENDMENT, 2026-09-03, and rule 2 requires the condition AND how it was checked.**
> **Condition:** this document is still a **DRAFT**, is **NOT frozen**, and **no compute has
> occurred under it**. **How checked, at the moment of this edit:** `ls -d
> verification/runs/M6SR_runs` and `ls -d cases/M6SR` **both return *No such file or directory***
> — the two registered run roots named in §12 do not exist, and this lane created neither.
> **No gate, threshold, cap or label of any OTHER gate is altered by this amendment.** `GF2`'s
> **threshold (`≤ 1.0e-03`) and cap (0.4 core-min) are UNCHANGED**; only its label moves from
> `BLOCKED` to a gradeable `PASS` / `GATE FAIL`, because the instrument now exists.

**THE REFERENCE, PINNED BY PATH AND SHA256:**

| | |
|---|---|
| **path** | **`models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`** |
| **sha256** | **`66b2a7bcd5a0cab274396de1c5c55d0f5cad90911a1e19ddae4e77db16834ab7`** |
| bytes / points | **1,512 B / 72 points** — the count this registration expected, **not rounded to** |
| final ordinate | **`z/l = 0.0007052`** at `x/l = 1.0`, giving **`t_TE/c = 0.0014104`** |
| provenance + L-144 record | **`models/onera_m6/PROVENANCE.md`** |
| loader / verifier | **`scripts/verify_agard_ar138_table_b1_1.py`** |

**THE COMPARATOR LOADS `GF2`'s REFERENCE ONLY THROUGH THAT PATH AT THAT HASH, AND REFUSES (exit 2)
IF THE HASH DOES NOT MATCH** — the same discipline §4.1 already fixes for `case_2308.dat`.

🔴 **AND THE CORRECTION THAT MATTERS MORE THAN THE UNBLOCKING, because a recorded measurement was
right and the conclusion drawn from it was too wide.** §1.6 measured that the *machine copy* was
absent and concluded that **"THE AGARD SECTION TABLE IS NOT ON THIS BOX."** **The table was on the
box the entire time** — printed in the AR-138 PDF this lab already holds, at **PDF page 333 /
printed page `B1-7`**, under the title **`M6 WING STREAMWISE SECTION COORDINATES (DESIGN VALUES)`**
and the caption **`TABLE B1-1`**. It was invisible to `find` and to `grep` because **the table's
numeric body never reached the PDF's OCR text layer** — the identical defect §4.1 had already
convicted the sidecar of. **A zero from a text search over a scanned document is not evidence of
absence, because the search instrument cannot see the pages.** That is standing rule 3's principle
applied to a document instead of to a solver field, and it is registered here as such.

> **AND THIS DOES NOT REOPEN §4.1'S RULING, WHICH STANDS UNCHANGED.** §4.1 fixes that **the AR-138
> PDF is provenance and is NEVER a source of numbers**, because its OCR is convicted (it renders
> this case's Mach `.9395` for `0.8395`). **Nothing in `GF2` takes a number from that PDF.** The
> printed page is used for **IDENTITY ONLY** — the caption, the title, the column layout, the
> point count and the endpoints — and every graded ordinate comes from the pinned machine copy.
> **No hand transcription of the scan was made, and none is filed**, precisely because at 1979
> print resolution individual digits are ambiguous (this lane misread two before a cleaner scan
> resolved them; `PROVENANCE.md` §3 names them). **The distinction is: the page establishes WHAT
> the file is; the file supplies the NUMBERS.**

🔴 **THE SPECIFIC TRAP REMAINS FORBIDDEN — AND THE FETCH MADE IT WORSE, NOT BETTER, SO C19 IS
STRENGTHENED RATHER THAN RETIRED.** The acquisition established that the true table and a
sharpened derivative sit **at adjacent URLs on the same page of the same archive**, sharing all 72
abscissae and every forward ordinate, differing **only in the last 14 ordinates**. **No filename,
hash or file-type check separates them** — which is exactly why L-144 forbids verifying by any of
those three. There are **at least TWO distinct sharpened derivatives**, and neither is a subset of
the other:

| derivative | points | ends at | mechanism |
|---|---|---|---|
| `models/onera_m6/quarantine/nasa_foilmod_SHARPENED_NOT_TABLE_B1_1.dat` (sha256 `915dee1b…1094`) | **72** | `x/c = 1.0`, `z = 0` | rescales `z` over rows 59–71; forces `z(72) = 0` |
| `verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat` (sha256 `0a60e747…eebc`) | **63** | **`x/c = 1.0055`**, `z = 0` | decimates to 63 points, keeps AGARD's `0.0007052` at `x/c = 1.0`, then **appends a point 0.55 % beyond chord** |

**THE REGISTERED REFUSAL, `C19`, THEREFORE TESTS THREE CONDITIONS AND NOT ONE.** The comparator
**REFUSES (exit 2)** if its reference table (i) has a **final ordinate below `1.0e-05`**, or
(ii) does **not carry exactly 72 points**, or (iii) has any **abscissa beyond `x/c = 1.0`**. The
first catches `foilmod`; the second and third catch the box's own lookalike; **a control tuned to
only the first would have passed the second file straight through.** Both refusals are
demonstrated, with both limbs of a planted control, in `PROVENANCE.md` §4. **These refusals are
registered gate items, not courtesies.**

⚠ **AND THE REFUSAL IS `raise`-BASED, NOT `assert`-BASED, AND THAT WAS CONTROLLED FOR** (L-475: a
guard set that is entirely assert-based is one interpreter flag from absent). Under `python3 -O`
the sharpened file still returns **`rc=2`**. **A run of the loader under `-O` returning `rc=0` on a
sharpened file is a registered defect, not a curiosity.**

#### THE INSTRUMENT-REJECTION DISCIPLINE — INHERITED, AND IT IS NOT OPTIONAL

`M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` establishes it and the concurrent lane exercised
it: **it rejected two readers before quoting its third.** Its first two returned straight-edge
residuals of **5.27e-01 m** and **1.236e-02 m** against the **2.22e-16 m** the corrected
instrument gives. **An unrejected instrument here would have manufactured a geometry defect that
is not there.**

> **REGISTERED: no `Gate GF` number is quoted until its reader has been shown correct on a case
> whose answer is known independently** — the straight leading edge must return a residual at
> machine epsilon, and the planted controls C17–C19 (§10) must all fire. **A reader that has not
> been rejected on something is not an instrument; it is a hope.**

#### WHAT FOLLOWS IF `GF1` FAILS — RULED NOW, BEFORE THE MEASUREMENT

**Ruling of the cfd supervisor, registered before `GF1` is evaluated:**

> **A sharp-TE family may still run the surface-refinement sensitivity study. Its `Cp`-vs-AGARD
> comparison must then carry the trailing-edge geometry mismatch as a NAMED, QUANTIFIED bias —
> never as an unstated one.**

Operationally, on a `GF1` `GATE FAIL`: (i) the measured `t_TE/c` of every level and AGARD's
0.0014104 are printed **on every Gate P figure**; (ii) `Gate P`'s already-registered restriction
to **`x/c ≤ 0.90`** stands and its justification is **strengthened**, not created, by this finding
— the rear 10 % of chord is plotted and reported, **never graded**; (iii) the certificate carries
the sentence **"this family's trailing edge is sharp; AGARD's is 0.14104 % chord thick; the `Cp`
disagreement in the rear chord is at least partly OUR GEOMETRY and is not attributed to the
solver."** ⚠ **The magnitude of the resulting `Cp` bias is NOT estimated here.** Naming a bias is
honest; inventing its size would not be.

**Predicted, and it is a prediction and not a measurement:** the ×4 family descends from
`m6_surfaceMesh_fine.cgns`, which is the DAFoam tutorial's surface, and `M6I` §4.2 measured the
comparable TMR-distributed geometry as **sharp** (`t_TE/c = 0.000000000`, under a planted control
that returned `2.48170e-04` on a split TE). **`GF1` is therefore predicted to FAIL on all three
levels.** If it does, that is a recorded miss of nothing — the ruling above already governs — and
**it is exactly why the gate is graded before the solve rather than discovered after it.**

### Gate G — grid behaviour on the surface-refinement family. Cap **0 (host arithmetic, in `B6`).**

🔴 **READ §6 BEFORE READING THIS GATE. Gate G here is NOT an observed order of accuracy.**

| # | gate | threshold | label |
|---|---|---|---|
| G1 | iterative convergence, every level | change in `C_D` over the last 500 iterations **≤ 1/10 of the L3–L2 difference** | fail → **`NOT A RESULT`** |
| G2 | residual behaviour | §5.1 | fail → **`NOT A RESULT`** |
| G3 | **surface-refinement exponent `p_s`** on `C_D`, from the three-level ratio | **printed, with its label from §6. NO acceptance band is registered on `p_s`, because a band would assert it is an order of accuracy and §6 rules it is not.** | reported |
| G4 | **surface-refinement band** `GCI_fine` on `C_D` at **`Fs = 1.25`** | printed; **NEVER quoted when the three values are not monotone** | reported, **as a LOWER BOUND** (§6) |

**Standing rule 5's ordering applies unmodified.** (1) any level not iteratively converged or not
plateaued → **`NOT A RESULT`**; (2) the triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT`
→ **`NOT A RESULT`**, with the value, both triples and both exponents printed beside it;
(3) `CONVERGING` → the band is reported under §6's label. **The gate can only turn a `PASS` or
`GATE FAIL` INTO `NOT A RESULT`, never the reverse.**

### 5.1 G2 — PLATEAU-AND-STATIONARITY, MACHINE-CHECKED

Executed by `scripts/residual_max_over_equations.py` (**EXISTS**), never by hand.

- **G2a — REDUCTION.** Every scaled initial residual has fallen **≥ 4 orders** from iteration 1.
- **G2b — PLATEAU.** Over the last **1,000 iterations**, the **max-over-equations** initial
  residual drifts **≤ 5 %**, either direction.
- **G2c — STATIONARITY OF THE ANSWER.** `C_D` stationary over the last **2,000 iterations** to
  **≤ 1/10 of the L3–L2 difference.**

> **THE DISCLOSURE THAT TRAVELS ONTO THE CERTIFICATE, AND IT IS NOT OPTIONAL:**
> **The residual reaches a FLOOR and does not converge to machine zero. The plateau value of the
> max-over-equations residual is REPORTED beside the result. A PLATEAU IS NOT CONVERGENCE.**

**Disclosed, and its basis stated honestly:** the 4-order / 5 % / 1,000-iteration numbers were
chosen by `RUNG1_M6_PREREGISTRATION.md` while looking at a **different configuration's** data
(`DARhoSimpleCFoam` / Spalart–Allmaras at `yPlus` mean 33.75). **They are not fitted to this
family's answer.** They are carried forward unchanged. **Newly relevant:** this family sits at
`y⁺ ≈ 32.3` (§3.1), so that reference history is **closer** to this configuration than it was for
the predecessor — recorded as a change in the **basis**, not smuggled in as new data.

### Gate P — surface pressures against AGARD AR-138. **SANAA'S DELIVERABLE.** Cap in `B6`.

`C_p` at the seven published sections against the 271 tapped values, **under `A-MAP` as
adjudicated by `D1` and constrained by §4.5**, with the family band on every station.

| band channel | value | status |
|---|---|---|
| numerical (mesh) | **`GCI_fine` from G4**, `Fs = 1.25` | **measured — but see §6: a LOWER BOUND, not the total** |
| reference accuracy | **`ΔCp = ±0.02` at `Mo = 0.84`** — AR-138 B1-4 §6.1 | published |
| read-off | **ZERO — machine-readable at a pinned hash** | claimed, and defensible |

**Two systematics disclosed and deliberately NOT put in the band, because quantifying them would
be inventing a number:** (1) AR-138 B1-4 §6.2 records *"Wall interference corrections: no
corrections"* at a semispan-to-tunnel-width ratio of 0.7, and the report declines to quantify it;
(2) AGARD's design trailing edge is **0.14104 % chord thick** while the geometry here is
**sharp** — so **Gate P is graded on `x/c ≤ 0.90`, and the rear 10 % is plotted and reported,
never graded.**

**Gate P sits behind Gate G and behind §4.** A `PASS` on a family that is not `CONVERGING` is
**`NOT A RESULT`**. A `PASS` whose mapping is INDETERMINATE under `D1` is **`NOT A RESULT`** on
the per-station channel.

### Gate R — Route A as a grid family. **`GATE FAIL`.** Cap: n/a — the route is closed, not run.

**Threshold: `MESH_STANDARD.md` §9.1's three-level requirement. Measured: one level (`A-F1`),
overset topology (`A-F2`). Label: `GATE FAIL`.** §2.1 carries both grounds and their measurements.

**This cell reads `GATE FAIL`, NOT `PENDING`.** `PENDING` would say "not yet run" and would be a
softened `GATE FAIL` — the exact misuse standing rule 1 forbids. The route was run, it was
measured, and it failed on structure. **No cap is registered because no compute is spent on it;
the mechanical import that will never happen prices at ≈ 0.7 core-min and is not the obstacle.**

---

## 6. THE HONEST LABEL — RATIFIED BY THE CHIEF, NOT NEGOTIABLE, AND WRITTEN ONCE

**THE FACTS THAT FORCE IT**, all established in §2.2 and none of them in dispute: the three
levels share `s0 = 1.0e-4`, `N = 65` and `marchDist = 12.0` **identically**; therefore
`r = 1.167442` and `cells / wing_faces = 64` at **every** level; therefore **the wall-normal
discretisation is IDENTICAL across the family — not merely similar, not merely coarse.** The
family refines **2 of 3 directions.**

**CLAUSE `L-HONEST`. This is a registered clause. It is quoted by reference and never
paraphrased:**

> **This is a SURFACE-REFINEMENT SENSITIVITY STUDY. Its `GCI` is a SURFACE-REFINEMENT BAND and a
> LOWER BOUND on total discretisation uncertainty. It is NOT an observed order of accuracy, and
> it is NOT the family band Sanaa named as her first deliverable.**

**EVERY FIGURE, TABLE, PLOT, JSON RECORD AND CERTIFICATE CELL DERIVED FROM THIS FAMILY CARRIES
CLAUSE `L-HONEST` VERBATIM.** It is registered here **once**, with an id, precisely so that it is
**referenced and not restated** — a paraphrase is how a caveat gets lost, and this one is
load-bearing.

**Three consequences, spelled out so nobody has to derive them:**

1. **`p_s` from G3 is a surface-refinement exponent.** Calling it an observed order of accuracy
   would assert that all discretisation error is refining, and the wall-normal error is **not
   refining at all**.
2. **`GCI_fine` from G4 UNDERSTATES the true numerical uncertainty**, by an amount this study
   **cannot measure**, because the unrefined direction's error contributes a term that the
   three-level ratio cannot see. **The direction of the error is known — the band is too narrow.
   Its magnitude is unknown and is NOT estimated here.**
3. **Sanaa's named first deliverable — M6 `Cp` WITH the family band — is NOT delivered by this
   registration.** It remains owed. This study is a **lower bound and a step toward it**, and
   saying otherwise would be the exact laundering §4.5 and rule 5 exist to prevent.

---

## 7. THE ONE THING THAT BLOCKS: PHYSICAL ILL-POSEDNESS

Checked per level **before** launch. A failure here **`BLOCKED`s** the level. Nothing else blocks.

1. **≥ 3 patches present**, with `wing` typed `wall`, a symmetry plane typed `symmetry` (**never
   `empty`, never `wall`**), and a farfield typed `patch` carrying a freestream in/out condition.
2. **`Boundary openness` ≤ 1e-12** — no leaks.
3. **`Number of regions: 1`.**
4. **Min cell volume > 0** — no inverted cells.
5. **Patch names matched against the level's own expected set, refusing on a mismatch.**

**High non-orthogonality is NOT ill-posedness. It is a quality miss and it launches** (Sanaa's
2026-09-03 ~21:00Z ruling, `etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md`, which places mesh
quality in the record-as-prediction class). **The gate did not move; when it applies moved.**

**Measured hazard this screen exists for, carried forward and not softened:** `RUNG1_M6`'s M0
mesh was a **closed all-wall box** — one patch `defaultFaces`, type `wall`, 9,376 faces, no inlet,
no outlet, no symmetry — and a branch-killing decision was taken off an 88.889° reading on a mesh
that **could never have been solved at all.** **We measured admissibility without asking whether
the object could be run.** Hence A9 and this section.

**Predicted status, from measurement:** the 399,360 level's own `boundary` file already reads
`wing`(wall) / `inout`(patch, 6240 faces) / `sym`(symmetry), so it is predicted to pass. **The
new L1's patch names are produced by `autoPatch 60` + `createPatch` and are NOT predicted here** —
a driver assuming one name set across levels would silently mis-apply boundary conditions.
**The launcher REFUSES a level whose patch names it did not expect.**

---

## 8. WHAT A RUNNABLE CASE NEEDS — ENUMERATED, BECAUSE NONE EXISTS

**Measured: no runnable case exists at any M6 level in any tree on this box.** `0/` is absent;
`fvSolution` is an empty `solvers{}`; `fvSchemes` carries `divSchemes{default none;}`;
`constant/` holds only `polyMesh`. **Every artifact below is a thing this registration commits to
producing, per level, before `B5` starts.**

### 8.1 THE `0/` FIELDS — SEVEN, WITH BOUNDARY CONDITIONS

| field | dimensions | internal | `wing` (wall) | farfield (patch) | symmetry |
|---|---|---|---|---|---|
| `U` | m/s | `(285.221 15.249 0)` = `U∞·(cos3.06°, sin3.06°, 0)` | `noSlip` | `freestreamVelocity`, `freestreamValue` = internal | `symmetry` |
| `p` | Pa | `101325` | `zeroGradient` | `freestreamPressure`, `freestreamValue uniform 101325` | `symmetry` |
| `T` | K | `288.15` | `zeroGradient` (adiabatic) | `inletOutlet`, `inletValue uniform 288.15` | `symmetry` |
| `nut` | m²/s | `1.574820e-07` | **`nutUSpaldingWallFunction`**, `value uniform 0` | `calculated` | `symmetry` |
| `k` | m²/s² | **`3.481770e-04`** | `kqRWallFunction`, `value $internalField` | `inletOutlet`, `inletValue $internalField` | `symmetry` |
| `omega` | 1/s | **`2210.901`** | `omegaWallFunction`, `value $internalField` | `inletOutlet`, `inletValue $internalField` | `symmetry` |
| `alphat` | kg/(m·s) | `0` | `compressible::alphatWallFunction`, `Prt 0.85` | `calculated` | `symmetry` |

`U∞` components: `285.679356 × cos(3.06°) = 285.2721`, `285.679356 × sin(3.06°) = 15.2494`. The
angle is imposed on the **freestream vector**, not by rotating the mesh.

**🔴 FREESTREAM `k` AND `omega` — UNREGISTERED IN EVERY PRIOR M6 DOCUMENT, AND RULED HERE.**

Registered as a **CHOICE**, with the formulae written out so the values are reproducible and so
nobody mistakes them for a tunnel measurement:

```
    L_ref     = MAC = 0.64607 m                          (REGISTERED: the MAC, not the semispan)
    omega_inf = 5 · U∞ / L_ref = 5 × 285.679356 / 0.64607   = 2210.901  1/s
    nut_inf   = 0.01 · ν∞      = 0.01 × 1.574820e-05        = 1.574820e-07 m²/s
    k_inf     = nut_inf · omega_inf                         = 3.481770e-04 m²/s²
```

**The eddy-viscosity ratio is the registered primitive: `μt∞/μ∞ = 0.01`.** The derived freestream
turbulence intensity is `√(2k/3)/U∞ = ` **0.0053 %**.

> ⚠ **THIS IS A NUMERICAL FREESTREAM CONDITION, NOT A MODEL OF THE S2MA TUNNEL.** It is chosen so
> that freestream turbulence **decay** cannot contaminate the boundary layer over the domain — the
> standard external-aerodynamics practice. **AR-138 gives no usable freestream turbulence level
> for run 308**, and 0.0053 % is **far below** any real tunnel. **No claim is made that it matches
> the experiment.**
>
> ⚠ **AND WHY MENTER 1994 IS NOT CITED FOR IT, THOUGH THE PAPER IS HELD.**
> `docs/papers/closure/Menter1994_sst_two_equation.pdf` is on this box, and its text sidecar at
> line 995 reads *"The following choice of freestream values is recommended:"* followed by the
> bare token **`(A16)`** — **the equation body is ABSENT from the OCR text layer**, the same
> defect class as AR-138's missing table numerics. **This registration therefore does not cite
> Menter's recommendation, because it cannot read it from the artifact this lab holds** (rule 15:
> never by file type, filename or hash). The values above are a **lab choice**. If a reader
> extracts (A16) from the PDF page itself, that lands as a dated addendum altering no gate.

### 8.2 `system/fvSchemes` — INCLUDING THE THREE TERMS NO PRIOR REGISTRATION RULED

```
    ddtSchemes        { default steadyState; }
    gradSchemes       { default Gauss linear; }
    divSchemes
    {
        default                                       none;
        div(phi,U)                                    bounded Gauss linearUpwind grad(U);
        div(phi,k)                                    bounded Gauss upwind;
        div(phi,omega)                                bounded Gauss upwind;
        div(phi,e)                                    bounded Gauss upwind;        // RULED HERE
        div(phi,K)                                    bounded Gauss linear;        // RULED HERE
        div(((rho*nuEff)*dev2(T(grad(U)))))           Gauss linear;                // RULED HERE
    }
    laplacianSchemes  { default Gauss linear limited corrected 0.5; }
    interpolationSchemes { default linear; }
    snGradSchemes     { default limited corrected 0.5; }
    wallDist          { method meshWave; }
```

**The three rulings, each with its reason, because `default none;` makes an unruled term a hard
solver abort rather than a silent default:**

- **`div(phi,e)` — `bounded Gauss upwind`.** Internal energy transport across a **transonic
  shock**. Boundedness is bought at first order deliberately: an unbounded second-order scheme on
  `e` across the shock is a documented route to negative temperature and solver death, and the
  quantity Gate P grades is **surface `Cp`**, which is set by the momentum solution, not by the
  formal order of the energy convection term. **Registered as a deliberate first-order term, not
  as an oversight.**
- **`div(phi,K)` — `bounded Gauss linear`.** `K = |U|²/2` is a **smooth, non-shock-bearing**
  kinematic quantity reconstructed from `U`; upwinding it would add dissipation to the energy
  balance that the momentum equation is not seeing, which is inconsistent. Second-order linear.
- **`div(((rho*nuEff)*dev2(T(grad(U)))))` — `Gauss linear`.** The deviatoric viscous stress
  divergence: an **elliptic** term, not a transport term, with no upwind direction to choose.
  Unbounded second-order linear is the only consistent choice; `bounded` is **not** applied,
  because the `bounded` prefix subtracts a `div(phi)·φ` term whose presence on a stress divergence
  would be meaningless.

### 8.3 `system/fvSolution`

```
    solvers
    {
        p       { solver GAMG; smoother GaussSeidel; tolerance 1e-8;  relTol 0.01; }
        "(U|e|k|omega)"
                { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.1; }
        rho     { solver diagonal; }
    }
    SIMPLE
    {
        nNonOrthogonalCorrectors 2;
        consistent               no;
        residualControl { p 0; U 0; e 0; k 0; omega 0; }   // ZERO: never stop on residualControl
    }
    relaxationFactors
    { fields { p 0.3; rho 0.05; }  equations { U 0.7; e 0.7; "(k|omega)" 0.7; } }
```

🔴 **`residualControl` IS SET TO ZERO ON EVERY EQUATION, DELIBERATELY.** A non-zero
`residualControl` makes `simpleFoam` write `End` and exit **before `endTime`**, which silently
breaks standing rule 4's **`last time == endTime`** clause and turns a legitimate run into an
un-gradeable one. **Convergence is judged by G2's instrument on the log, never by the solver's
own early exit.**

### 8.4 `constant/`

- **`thermophysicalProperties`**: `hePsiThermo` / `pureMixture` / `sutherland` transport /
  `hConst` thermo / `perfectGas` / `sensibleInternalEnergy`; `Cp 1004.5`; `Pr 0.72`; and:

  | constant | **registered value** | derivation |
  |---|---|---|
  | `molWeight` | **28.964425** | **NOT OpenFOAM's default 28.9647.** Set so that `R = 8314.47/molWeight = 287.058` exactly, matching §3. The default gives `R = 287.0553`, a 9e-6 relative shift that moves `ρ∞` in the sixth figure — below every threshold here, but the registration and the case files must agree **exactly** or a reader cannot reproduce `Re`. |
  | `As` | **1.571860616e-06** kg/(m·s·√K) | **BACK-SOLVED**, `As = μ(T)(T+Ts)/T^1.5 = 1.929119606e-05 × 398.55 / 288.15^1.5`, with `Ts = 110.4` |
  | `Ts` | **110.4 K** | registered |

  **Round-trip verified by this lane:** `As·T^1.5/(T+Ts)` at `T = 288.15` returns
  **1.929119606e-05 Pa·s**, the §3 value, to all quoted digits.

  🔴 **THE SUTHERLAND COEFFICIENTS ARE BACK-SOLVED, NOT PHYSICAL, AND THE FILE CARRIES A COMMENT
  SAYING SO.** OpenFOAM's own default air pair (`As = 1.4792e-06`, `Ts = 116`) gives
  **μ(288.15) = 1.790244e-05 Pa·s**; the registered pair gives **1.929120e-05**, **7.76 % higher**
  — the same departure §3 records against Sutherland's classical constants (7.81 %). **The
  departure is intentional and is the price of holding `Re = 11.72e6` at the registered state
  pair.** The alternative — physical `As` with a rescaled `Re` — would break the registered
  Reynolds number, which is a published condition of AR-138 test 2308 and is not this lab's to
  move.
- **`momentumTransport`**: `simulationType RAS`; `RAS { model kOmegaSST; turbulence on;
  printCoeffs on; }`.

### 8.5 `system/` remainder

- **`controlDict`**: `application rhoSimpleFoam`; `startFrom startTime`; `startTime 0`;
  `stopAt endTime`; `endTime` = 3000 / 4000 / 5000 per level; `deltaT 1`;
  **`writeControl timeStep`, `writeInterval` = `endTime`** — 🔴 **`endTime` MUST be an exact
  multiple of `writeInterval` or NO FIELDS ARE WRITTEN AT `endTime` and rule 4's fields-present
  clause fails on a run that otherwise succeeded**; `writeCompression off`;
  `functions { forceCoeffs; yPlus; residuals; }` writing `C_D`/`C_L`, the printed `y⁺` (§3.1's
  only honest source), and per-equation initial residuals.
- **`decomposeParDict`**: `method hierarchical;` `coeffs { n (4 1 1) / (8 1 1) / (16 1 1); order
  xyz; }` per level. **`scotch` is NOT used** (§3.2).
- **`sampleDict` / `cuttingPlane`**: seven constant-`y` planes at the registered `y/b` × semispan,
  `b_semi = 1.19676 m` **measured independently from the registered STL** (0.039 % from the
  imported 1.1963 — the one import that is corroborated on this box).

### 8.6 COMPLETION — RULE 4, STRICT, ALL-OR-NOTHING

A level is done only if **all** of it holds: `rc = 0`; an `End` line; **last time == `endTime`**;
fields **`U p T rho nut k omega alphat`** present at `endTime`; `ExecutionTime` count ==
`endTime`; and **every field at `endTime` NEWER than the case's own `0/U`** — the age guard.
**The launcher REFUSES a case where `0` or any time directory already exists.** **The comparator
REFUSES (exit 2) rather than degrade** on any failed clause.

---

## 9. FROZEN PATHS, AND THE PREDECESSOR'S STRUCTURAL DEFECT THAT IS FIXED HERE

| what | path |
|---|---|
| this registration | `verification/campaign/M6SR_PREREGISTRATION.md` |
| predecessors, **NOT MODIFIED** | `verification/campaign/RUNG1_M6_PREREGISTRATION.md` @ `c7f99bb1`; `RUNG1_M6_R2_PREREGISTRATION.md` @ `3126345f`; `M6I_PREREGISTRATION.md` @ `73148a9c` |
| run root (**ABSENT at drafting; RE-VERIFY AT FREEZE**) | `verification/runs/M6SR_runs/` |
| level roots (**ABSENT at drafting**) | `verification/runs/M6SR_runs/{L1,L2,L3}/` |
| **comparator** (does not exist; to be written) | **`cases/M6SR/analyse_m6sr.py`** |
| **build driver** (does not exist; to be written) | **`cases/M6SR/build_m6sr_l1.sh`** |
| reference data, hash-pinned | `cases/dafoam/ladder-a/logs_A3/case_2308.dat` sha256 `020c5fcc…f0d0` |
| surface master, hash-pinned | `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/m6_surfaceMesh_fine.cgns` sha256 `197efa09…3327` |
| **independent geometry reference**, hash-pinned — **NEVER a level** (§1.5) | `/home/ubuntu/certonomous-runs/W5-idwarp-source/input_files/onera_m6.cgns` sha256 `e4257acfc851509982614138c9cab7e7873bf04b239691858d624e0d55e54c98` |
| **🔴 the SHARPENED section — a REFUSAL trigger, never a reference** (§1.6) | `verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat` sha256 `0a60e747a0a7b747cc52b7937c4f1e347e66f04e51a9e61bd5eb2bbe3d90eebc` |
| **AGARD Table B1-1 machine copy — ACQUIRED 2026-09-03, hash-pinned** (§5) | `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` sha256 `66b2a7bcd5a0cab274396de1c5c55d0f5cad90911a1e19ddae4e77db16834ab7` — 72 points, final ordinate `0.0007052`. **`GF2` is GRADEABLE.** Provenance + L-144 record: `models/onera_m6/PROVENANCE.md`; loader: `scripts/verify_agard_ar138_table_b1_1.py` |
| **🔴 a SECOND sharpened derivative — a REFUSAL trigger, never a reference** (§5) | `models/onera_m6/quarantine/nasa_foilmod_SHARPENED_NOT_TABLE_B1_1.dat` sha256 `915dee1b2d97166886a075aef59ac9e928f637965da1fbaf4b8bfb8272f81094` |
| the AR-138 printed source (**provenance only — NEVER a source of numbers**, §4.1) | `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`, Table B1-1 at **PDF page 333 / printed page `B1-7`** |
| the geometry method this gate inherits | `verification/campaign/M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` §4.2–§4.3, **cited, not amended** |
| residual reducer (**EXISTS**) | `scripts/residual_max_over_equations.py` |
| calibration ledger | `docs/COST_CALIBRATION.md` |
| envelope ledger | `docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md` |

### 9.1 🔴 THE COMPARATOR LIVES UNDER `cases/`, NOT IN THE RUN TREE — AND THIS IS A REPAIR

**The predecessor filed its comparator INSIDE the run root whose absence was its own freeze
proof.** `RUNG1_M6_R2_PREREGISTRATION.md` §11 registers the comparator at
`verification/runs/RUNG1_M6_R2_runs/analyse_rung1_m6_r2.py` while the same document's freeze block
asserts that **`verification/runs/RUNG1_M6_R2_runs/` did not exist**. **A grading path that
cannot exist until compute begins is not a frozen grading path.** Rule 2 requires the grading path
to be fixed **at the pre-registration commit** and the frozen file to be hashable against the
committed blob — impossible for a file inside a directory the freeze proves absent.

> **RULED: this registration's comparator and build driver live under `cases/M6SR/`. NOTHING that
> grades is ever filed inside a run root.** Both are written and committed **before** the freeze,
> so the freeze can pin their blob shas, and `scripts/check_comparator_freeze.py` can verify at
> grading that the frozen file **is** the file that ran.

### 9.2 EXECUTION AND ASSERTION MECHANICS — BINDING ON EVERY SCRIPT THIS REGISTRATION PRODUCES

- **Assertions do not gate.** No bare `assert` anywhere. Every check is
  `... || { echo "ABORT: <what>"; exit 1; }` in shell, and an explicit `raise` in Python.
  **Basis: a guard set that is entirely assert-based is one interpreter flag (`python3 -O`) from
  absent** — L-475, and the measured control in `463de30e` in which the old converter **wrote a
  mesh from a malformed file and exited 0** under `-O`. **Every comparator and driver is run once
  under `python3 -O` and must produce byte-identical refusals** (L-332).
- **Shas are read back by subject line**, never by position in a `sha256sum` batch (L-479).
- **`setsid timeout cmd` exits 0 for every outcome.** `rc` is captured **inside** the detached
  wrapper and written to `SOLVER_RC.txt`; it is never taken from around the `setsid` line.
- **Ranks are taken from the SOLVER LOG's own banner**, never from `system/decomposeParDict` —
  that file can post-date the run, and the banner's **first** occurrence is not necessarily the
  primal's.
- **`grep … log.* | tail -1` is a coin flip** under multi-file output; every reading names **one**
  artifact by explicit path.

### 9.3 CALIBRATION — RULE 12's ESTIMATE-VERSUS-ACTUAL, OWED AT EVERY STEP

At **every** step's completion (`B1`…`B6`), actual core-minutes are read **from the logs**, the
ratio actual/predicted is stated, the gap is attributed (contention / **waste, named separately
and never absorbed into the ratio** / misprediction), and a row is filed to
`docs/COST_CALIBRATION.md` and to
`docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md`. **A completion
report without that comparison is incomplete.**

**Two calibration questions this ladder is specifically instrumented to answer**, registered now
so the answer is not chosen later:

1. **Which pyHyp basis was right** — the log-interpolated 2.644e-4, L1's average 3.796e-4, or L1's
   marginal 8.676e-4 s/face-layer (§2.4)? The row states which, and by how much.
2. **Was the ×2.0 superlinear allowance on `B5c` too small, right, or too large?** A 4× cell-count
   extrapolation is exactly the regime `docs/COST_CALIBRATION.md:408` convicts a bare per-cell
   rate in, and **this is the first M6-family measurement of it on this box.**

---

## 10. PLANTED CONTROLS — RULE 3, ON EVERY ZERO THIS LADDER CAN REPORT

**A zero from a reader not shown able to see a non-zero is not evidence. A `PASS` reported by a
reader whose plant did not fire is `NOT A RESULT`, not a pass.** Every control below plants into a
**scratch copy**, reads it back **from disk**, and the comparator **REFUSES** if the reader cannot
see it.

| # | reader | plant | must see |
|---|---|---|---|
| C1 | `checkMesh` quality reader | a log of the **`=`** label form **and** one of the **`:`** form | a non-null max aspect ratio from **each** |
| C2 | `checkMesh` quality reader | `Min volume` ≠ `Max volume` | a non-trivial derived cell-volume ratio, **never 1** |
| C3 | `checkMesh` quality reader | replace one log's non-orthogonality maximum with a known value | **that value** read back |
| C4 | `checkMesh` quality reader | a log in which `Non-orthogonality check OK.` sits beside a maximum **above 70°** | **`GATE FAIL`**, proving the reader reads the **number** and not the verdict string (L-459) |
| C5 | **points-hash family reader** | perturb **one node** of one level's decompressed `points` | **the hash moves**, and A5 reports the levels distinct/identical correctly |
| C6 | **points-hash family reader** | feed it **two byte-identical `points` files** (the measured DPW5 shape, §1.4) | **`NOT A RESULT`** — a reader that cannot fail A5 is a fail-open wearing a pass |
| C7 | residual reducer | a log of the **stock OpenFOAM** print form and one of the **DAFoam** form | the same reduction from each. **Measured trap: a real DAFoam log contains ZERO occurrences of `Initial residual`.** |
| C8 | residual reducer | a synthetic falling, rising and flat series | **all three classes reachable** — a classifier that can only say one thing is not evidence for the thing it says |
| C9 | residual reducer | a step whose max is carried by a **different field** than the previous step's | the max **moves between fields** |
| C10 | `C_p` comparator | perturb one tap's `CP` in a **scratch copy** of `case_2308.dat` | the station deviation moves by the planted amount |
| C11 | `C_p` comparator | corrupt the reference file's sha256 | **REFUSAL**, not a silent fallback |
| C12 | **`D1` discriminator** | a scratch reference whose seven sections are **reversed** | **`FALSIFIED`** — proving `D1` can return a verdict other than the one `A-MAP` predicts |
| C13 | **`D1` discriminator** | a scratch reference whose seven sections all carry the **same** `CP` block | **`INDETERMINATE`** — proving the third branch is reachable |
| C14 | force reader | perturb `C_D` in a scratch `postProcessing` file | the deviation moves |
| C15 | family/ratio reader | a triple whose cell counts are **not** exactly 4:4 | **`GATE FAIL`** on A4 |
| C17 | **`Gate GF` TE reader** | a copy of a level's surface in which the root TE node is **split by 2.000e-04 m** in the thickness axis | a **non-zero `t_TE/c` on 2 nodes** — the worked precedent returned `2.48170e-04`. **A `t_TE/c = 0` from a reader not shown able to report a non-zero is NOT evidence of a sharp trailing edge.** |
| C18 | **`Gate GF` section reader** | **`+5.000e-04 c` added to every reference ordinate** | max │Δz│/c moves by the planted amount — the worked precedent returned `1.178e-03` against an as-read `6.783e-04` |
| C19 | **`Gate GF` reference loader** | **THREE fixtures, not one** (§5): (a) the box's `om6_wing_section_sharp.dat` — 63 points, `x/c` to 1.0055; (b) `quarantine/nasa_foilmod_SHARPENED_NOT_TABLE_B1_1.dat` — 72 points, zero final ordinate; (c) a **planted** final ordinate of `3.21e-04` on the true table | **REFUSAL (exit 2) on (a) and (b)**; **ACCEPTANCE of (c)**. A refusal from a loader never shown able to accept is not evidence, and an acceptance from one never shown able to refuse is not evidence either — **both limbs must fire**. ⚠ **A control tuned only to the zero final ordinate PASSES fixture (a) straight through**, which is why the loader tests point count and beyond-chord abscissa as well. Demonstrated, with rc values, in `models/onera_m6/PROVENANCE.md` §4. **Re-run under `python3 -O` (L-475): still `rc=2`.** |
| C20 | **`Gate GF` planform reader** | the straight leading edge, whose answer is known independently | a straight-edge residual **at machine epsilon** (~2.22e-16 m). **Two readers were rejected on exactly this before a third was quoted (5.27e-01 m and 1.236e-02 m); a reader that has not been rejected on something is not an instrument.** |
| C16 | every script above | run once under **`python3 -O`** | **byte-identical refusals** (L-475, L-332) |

**C12 and C13 exist because §4.3's discriminator is worthless if it can only return one answer.**
A discriminator that structurally cannot falsify is a disclaimer, not a test.

---

## 11. PREDICTIONS — RECORDED NOW, GRADED AFTERWARD, NONE LAUNDERED

| # | prediction | basis, and its honesty label |
|---|---|---|
| P1 | **The new L1 will land near 61° max non-orthogonality**, in family with 61.4938 and 61.1581 | **INFERENCE**, not measurement. The strongest inference available on this box: the two existing levels differ **only** in surface, and surface refinement alone moved non-orthogonality 61.4938 → 61.1581 — slightly **better**. **If L1 exceeds 70°, that is a recorded miss and the run still launches.** |
| P2 | **Max aspect ratio will FALL again**, continuing 608.207 → 222.355 → ? | **INFERENCE** from the same two-point trend. ⚠ **A two-point trend is not a law**, and `docs/COST_CALIBRATION.md:408` records a measured case where max aspect ratio was **non-monotone** across a four-level ladder while non-orthogonality rose monotonically. **Low confidence, stated.** |
| P3 | **`y⁺` will be in the TENS, ≈ 32.3, and IDENTICAL at all three levels** | **DERIVED FROM A FLAT-PLATE CORRELATION** (§3.1), not measured. The *identical-across-levels* half is **structural** (§2.2) and is the stronger claim. |
| P4 | **`B5c` will overrun its 543.13 core-min estimate** | **INFERENCE** from `docs/COST_CALIBRATION.md:408`'s superlinear finding. Direction known (**upward**); the ×2.0 allowance is the correction, and P4 predicts the allowance is **too small**. |
| P5 | **`D1` will return CORROBORATED** | **PREDICTION, and deliberately NOT tested by the drafting lane** (§4.3). If it returns FALSIFIED, `A-MAP` is reversed and every prior M6 `Cp` comparison on this box that assumed root-to-tip is called into question — **which is exactly why `D1` is registered rather than assumed.** |
| P6 | **The `.mesh-cache` topology's farfield is only ~12.7 chords** — bounding box `(−10.51, −12.69, 0)` to `(12.90, 12.69, 11.97)` | **MEASURED** from its checkMesh log. `marchDist = 12.0` is **tight for a transonic case; expect a blockage-like `Cp` bias, direction and magnitude UNKNOWN and NOT quantified here.** ⚠ **It is IDENTICAL at all three levels — which is required for a family (a moving farfield would be three different problems) and is also this family's largest un-quantified systematic.** |
| P7 | **Patch names may differ between the existing levels and the newly built L1** | **MEASURED PRECEDENT**: an hcf-generated family on this box produced `wing/symmetry/farfield` on the generator level and `WING3D/SYMMETRY/FARFIELD` on coarsened levels. **A driver assuming one name set would silently mis-apply boundary conditions.** The launcher **refuses** a level whose patch names it did not expect (A9). |
| P8 | **`Gate GF1` will FAIL on all three levels — the ×4 family will prove SHARP-TE against AGARD's blunt 0.14104 % chord** | **INFERENCE from a measurement of a SIBLING artifact, not of these surfaces.** `M6I` §4.2 measured the TMR-distributed M6 as `t_TE/c = 0.000000000` under a planted control, and the ×4 family descends from the DAFoam tutorial's surface, which is of the same sharpened lineage. ⚠ **No surface of this family has been measured.** The §5 ruling already governs the failure, so this prediction changes no outcome — it exists so that a `PASS` would be a genuine surprise on the record. |
| P9 | **`GF3` will PASS — `t_TE/c` will be IDENTICAL across the three levels** | **STRUCTURAL INFERENCE**, the strongest kind available here: all three surfaces are `cgns_utils coarsen` outputs of one master (§2.2), and coarsening removes nodes rather than changing TE topology. **A `GF3` failure would falsify the one-generator claim the whole family rests on**, and would be a far more serious finding than `GF1` failing. |

*(A ninth row, predicting Route A would prove a single grid, stood in this table while the route
was open. It has been removed rather than scored: the finding arrived before the freeze, the
speculation was only half right, and §2.1 records it there as superseded. **A prediction cannot be
graded against a measurement that arrived before the freeze**, and keeping it here would have
banked a hit this lane did not earn.)*

---

## 12. WHAT THIS REGISTRATION DOES NOT CLAIM

1. **It does not claim an observed order of accuracy.** Clause `L-HONEST`, §6.
2. **It does not deliver Sanaa's named first deliverable.** §6 consequence 3.
3. **It does not modify, amend or reinterpret `c7f99bb1`, `3126345f` or `73148a9c`.**
4. **It does not claim a mechanism for the 390-face surface's failure.** §1.3.
5. **It does not claim `μ∞ = 1.929120e-05 Pa·s` is a physical air viscosity.** §3, 7.81 % high.
6. **It does not claim the registered freestream `k`/`omega` model the S2MA tunnel.** §8.1.
7. **It does not cite Menter 1994 (A16)**, because that equation is not readable from the artifact
   this lab holds. §8.1.
8. **It does not claim a measured `y⁺`.** §3.1 is a correlation.
9. **It does not quantify the uncorrected wall interference or the ~12.7-chord farfield bias.**
10. **It does not claim `Cp` agreement in the rear 10 % of chord means anything.** Gate P grades
    `x/c ≤ 0.90`.
11. **It does not claim `A-MAP` is confirmed.** It is an assumption with a registered, unevaluated
    discriminator.
12. **It does not claim `onera_m6.cgns` is unusable for anything** — it is closed as a *family*
    (§2.1) and adopted as an **independent geometry reference** (§1.5). It is **never** used as a
    level of this family.
13. **It does not grade `GF2` — it only makes `GF2` GRADEABLE.** The reference now exists and is
    pinned (§5), but **no surface of the ×4 family has been compared against it.** An acquired
    instrument is not a measurement, and `GF2`'s outcome is **not predicted here**.
14. **It does not estimate the magnitude of the trailing-edge `Cp` bias** if `GF1` fails. Naming a
    bias is honest; inventing its size is not. §5.
15. **It does not adopt OpenFOAM's overset machinery** and takes no position on whether the
    Route A grid could be solved that way by some other campaign.
16. **It claims no rented-instance dollar figure and proposes no instance change** — reserved to
    Sanaa.
17. **It authorises no network egress.** Obtaining a genuinely published M6 family, or a fresh
    Table B1-1, is egress and is **not** covered here.
18. **Nothing is sent, filed, submitted, uploaded, posted or registered outside this box**
    (standing rule 7). **SUBMISSIONS ARE PARKED.**

---

## 13. WHAT THE SUPERVISOR MUST CHECK BEFORE FREEZING — THE DRAFTING LANE'S OWN OPEN ITEMS

**Listed by the lane that wrote this file, because an honest gap is worth more than a confident
guess.**

1. **`§2.4`'s converter rate is an off-basis transfer** — a `ugrid_to_foam.py` measurement applied
   to `plot3dToFoam`. Accept, replace, or widen.
2. **`§2.4`'s `checkMesh` reconciliation**: `RUNG0b:222`'s prose says 0.33× and its own measured
   pair gives 0.370×. This draft uses the measured 0.0661 and flags the source's internal
   inconsistency. **That inconsistency is in a frozen file and this lane did not touch it.**
3. **The ×2.0 superlinear allowance on `B5c` is a judgement**, not a measurement. It is the single
   largest number in the cost table.
4. **`D1`'s 0.75 margin threshold is a judgement.** It is defensible but it is not derived.
5. ✅ **CLOSED by this lane:** `§8.4`'s Sutherland `As = 1.571860616e-06` and `molWeight
   28.964425` are computed and round-trip verified. **Both differ from OpenFOAM's defaults and
   the difference is deliberate.**
6. **`§8.5`'s `b_semi = 1.19676 m`** is carried from another document's measurement, not
   re-measured here. **`GF4` will now measure the semispan on each level's own surface, so this
   item closes itself at `B0`.**
7. ✅ **CLOSED by this lane:** `molWeight` set to **28.964425** so the case files reproduce §3's
   registered `R = 287.058` exactly rather than OpenFOAM's default `287.0553`.
8. ✅ **CLOSED:** Route A is `GATE FAIL`, §2.1, on the supervisor's ruling and the concurrent
   lane's two measured grounds. §2.3's case 2 fired.
9. ✅ **CLOSED 2026-09-03 — `GF2` IS NO LONGER `BLOCKED`.** The 72-point Table B1-1 machine copy
   was re-acquired **inbound** under Sanaa's item-5 GO
   (`etc/sessions/2026-09-03T2250Z_sanaa_go_all_asks.md`, `fbab523b`) and is pinned at
   `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`
   sha256 `66b2a7bc…4ab7` — **72 points, final ordinate `0.0007052`, `t_TE/c = 0.0014104`**,
   agreeing with the W5 CGNS grid to seven significant figures. §5, and
   `models/onera_m6/PROVENANCE.md` for the L-144 record.
   **Two things this closure does NOT mean, stated because both are easy to assume:**
   (a) **`GF2` has not been graded** — no surface of the family has been compared against the
   reference, and its outcome is not predicted; (b) **the §1.6 belief that the table was absent
   from the box was WRONG, not merely superseded** — Table B1-1 was printed in the AR-138 PDF
   this lab already held, invisible to `find` and `grep` because its numeric body never reached
   the OCR text layer. **A zero from a text search over a scanned document is not evidence of
   absence.** ⚠ **Nothing left the box:** anonymous GETs of public files only; no account, login,
   email or form; SUBMISSIONS REMAIN PARKED (rule 7) and the box remains private (rule 8).
10. 🔴 **`GF1`'s ±10 % band around `t_TE/c = 0.0014104` is a judgement of this lane, not a derived
    tolerance.** It is wide enough that no plausible measurement noise crosses it and narrow
    enough that a sharpened surface cannot pass, which is what it is for — but it is not
    principled and the supervisor should set it or endorse it explicitly.
11. **`§1.5`'s CGNS geometry figures — 30.0000000° sweep, 3.8e-13 residual, 1.1963 m semispan,
    `t_TE/c = 0.0014104`, max │Δz│/c 6.99e-05 — are RELAYED from the supervisor's message, not
    measured by this lane.** The supervisor states they verified the load-bearing parts
    personally. **This lane verified the *method* they rest on** (`M6I` §4.2–§4.3, read) **and
    the reference-side trap** (§1.6, measured here), **not the CGNS numbers themselves.** They are
    used in this document as **motivation for `Gate GF`**, never as a gate value, so nothing here
    breaks if one of them is off — but they should not be re-quoted downstream as this lane's
    measurements.
