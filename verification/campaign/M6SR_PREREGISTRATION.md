# M6SR pre-registration — ONERA M6 surface pressures against AGARD AR-138, on a SURFACE-REFINEMENT family

**Team: cfd. Case id `M6-SR`. v1.0 — FROZEN 2026-09-04 by cfd-supervisor. Drafted 2026-09-03 by a cfd lab-lane; amendments 2-8 pre-compute.**

> ## ✅ THIS FILE IS **FROZEN**. EVERY GATE, THRESHOLD, CAP AND LABEL IN IT IS IN FORCE.
>
> **CHECK 4 IS DISCHARGED. THIS COMMIT IS THE FREEZE, AND IT IS A STATUS FLIP AND NOTHING ELSE
> — THE DIFF IS THE EVIDENCE.** The `SUPERVISION_CHARTER.md` §3 check 4 was performed
> **personally by cfd-supervisor**, at the artifacts, not on any lane's report:
>
> - **No compute has occurred under this document**, verified **with a live planted control**
>   (rule 3): `verification/runs/M6SR_runs` **ABSENT** and `cases/M6SR` **ABSENT**, while the
>   identical reader in the same invocation returned **PRESENT** on `verification/runs/M6I_runs`
>   and `verification/runs/RUNG1_M6_R2_runs`. **The zero has a non-zero beside it.**
> - **No gate, threshold, cap or label moved anywhere in amendments 2–8.** Diffed
>   `d554e3a7 →` this commit: **585 insertions, 10 deletions**, and every one of the ten removed
>   lines is a strike-with-replacement at an intended site. **`B5c` = 543.13, cap 1,630.0,
>   TOTAL 615.24 / 1,903.0 are unchanged in value.**
> - **The solve rate's rank basis was verified at the log banner**, not at `decomposeParDict`:
>   the rate is a **four-rank** measurement (`nProcs : 4`), so `B5a` sits on basis, `B5b` is 2×
>   off it and `B5c` is 4× off it. §1273's trap fired in that very file — the **first**
>   `nProcs` match is `nProcs : 1`, and `decomposeParDict` says 2 and post-dates the run.
>
> **AFTER THIS COMMIT THE GATES ARE CLOSED.** Changes land only as **dated addenda that cannot
> alter a gate, threshold, cap or label**; originals are struck, never rewritten (rule 2, rule 6).
>
> ⚠ **In-body references to "DRAFT" inside the dated amendment condition blocks (§211, §417,
> §815 and their siblings) are HISTORICAL STATEMENTS of the condition at that amendment's own
> timestamp, and are deliberately not rewritten.** They are the evidence that each amendment was
> pre-compute. **They are not the current status; this banner is.**
>
> 🔴 **WHAT THIS FREEZE DOES NOT DO.** It does **not** make this document Sanaa's named
> deliverable. `L-HONEST` (§6) stands unaltered: the family refines **2 of 3 directions**, the
> wall-normal discretisation is **identical across levels**, so `GCI_fine` is a **LOWER BOUND**
> on discretisation uncertainty and `p_s` is **NOT an observed order**. She asked for M6 `Cp`
> **with a family band**; this delivers a `Cp` comparison with a **surface-refinement** band.
> **That gap is measured, it is on her desk, and freezing this document does not close it.**
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

> 🔴 **BEFORE PROPOSING TO REVIVE BRANCH (a1) OR (a2) ON THE 2026-09-03 GATE RECLASSIFICATION,
> READ §14.1.** The family this theorem kills **is** branch (a1) — `RUNG1_M6_R2` registers the
> identical triple, was frozen at `3126345f`, and **has already run**. There is a **second wall**
> and it is in **Sanaa's own words**: her ill-posedness exception names *"no outlet"* explicitly,
> and the mesh that carried the 88.889° was a **closed all-wall box** with a single `defaultFaces`
> wall patch. **The reclassification removed a mesh-quality block; it did not remove that one.**

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
> GROUNDS.** The mechanical import prices at ~~**≈ 0.7 core-min**~~ **≈ 0.045 core-min**
> (**STRUCK — see §14 AMENDMENT 5**: at this registration's own §2.4 rates on Route A's own
> 185,664 cells, `0.1786 × 0.185664 + 0.0661 × 0.185664 = 0.045432`; the 0.7 was **15.4× too
> high**) — genuinely negligible, and **the
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
| `checkMesh` | **0.0661 core-min/Mcell** | **MEASURED**, same line — 30 wall s over the same 4 grids. ⚠ **A RECONCILIATION, stated so nobody re-derives it wrongly:** that line's prose says `checkMesh` "measured 0.33×" the converter, but its own measured pair gives **0.0661 / 0.1786 = 0.3701×**. ~~records the 11 % discrepancy in the source~~ **CHARACTERISATION STRUCK — see §14 AMENDMENT 2: `RUNG0b:222` attributes the `0.33×` to ITS OWN PREDECESSOR, a different document measuring different grids. It is a PRIOR MEASUREMENT reported beside a current one, NOT an inconsistency, and nothing in the frozen file needs touching.** **This registration uses the measured 0.0661 — RUNG0b's own measurement on RUNG0b's own four grids.** |
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

~~**All-in: 615.1 core-min estimated, 1,902.0 core-min capped, $1.63 DERIVED at cap.**~~
**STRUCK — WRONG IN BOTH FIGURES. See §14 AMENDMENT 3.** **All-in: 615.24 core-min estimated,
1,903.0 core-min capped, $1.6270 DERIVED at cap** — re-derived from the table's own nine step rows.
**The TABLE above governs (rule 12 makes it frozen content); this prose was the error.** Under the
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
`c = 0.64607 m`**, `S_ref = 0.7532 m²`. ~~Read from the machine file's own zone title, never from
the OCR sidecar (§4.1).~~ **CITATION STRUCK AS FALSE — see §14 AMENDMENT 4.** **`M∞`, `α` and `Re`
ARE read from the machine file's own zone title** at sha256 `020c5fcc…f0d0` (verified: the title
reads `Run= 308, Mach= 0.8395, Alpha=  3.06, Re= 11.72x10**6, Section 1`), never from the OCR
sidecar (§4.1). **`c` and `S_ref` are NOT in that file** — a controlled search returns zero — and
are **REGISTERED CHOICES** motivated by AGARD AR-138 §2.1.7 / §4.7 (printed page), under §3(a)'s
existing choice-not-measurement label. **`c` is consumed only by `μ∞` and `omega_inf`; `S_ref` is
consumed by nothing; NO GATE CONSUMES EITHER** (§14 AMENDMENT 4a/4b/4c).

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
the mechanical import that will never happen prices at ~~≈ 0.7~~ **≈ 0.045 core-min** (**STRUCK —
§14 AMENDMENT 5**) and is not the obstacle.**

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
| P4 | **`B5c` will overrun its 543.13 core-min estimate** | **INFERENCE** from `docs/COST_CALIBRATION.md`'s JF1 **cell-count** superlinear finding. Direction known (**upward**); the ×2.0 allowance is the correction, and P4 predicts the allowance is **too small**. 🔴 **THIS PREDICTION IS RANK-DEPENDENT — SEE §14 AMENDMENT 8c.** It stands as written **at the registered 16 ranks**, where two independent upward terms act; **at 8 ranks it may REVERSE** (the allowance too LARGE), and **at 4 ranks it rests solely on the cell-count finding**. **P4 is graded against the rank count the run actually used, read from its own solver-log banner (§1273), and a miss in the DOWNWARD direction is a genuine miss.** |
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
2. ✅ **CLOSED 2026-09-04 — §14 AMENDMENT 2. THE ITEM WAS MIS-STATED AND IS WITHDRAWN.**
   ~~`RUNG0b:222`'s prose says 0.33× and its own measured pair gives 0.370×. This draft uses the
   measured 0.0661 and flags the source's internal inconsistency. That inconsistency is in a frozen
   file and this lane did not touch it.~~ **There is NO inconsistency.** `RUNG0b:222` attributes the
   `0.33×` to **its own predecessor** — a different document, a different run, a different grid
   set — beside its own fresh measurement of `0.0661` on its own four grids. **That is a
   calibration remark, which is what `docs/COST_CALIBRATION.md` exists to make possible, not a
   contradiction.** Nothing in the frozen file needs touching and nothing needs supervisor
   adjudication. **The registration's choice of 0.0661 is unchanged and re-affirmed.**
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

---

## 14. PRE-COMPUTE AMENDMENTS 2–8 — 2026-09-04T0120Z / T0128Z / T0133Z

**Drafted by a cfd lab-lane. NOT a freeze. This section authorises no compute and the supervisor's
`SUPERVISION_CHARTER.md` §3 check 4 is undischarged.**

> ### THE CONDITION, STATED ONCE FOR AMENDMENTS 2–6 BELOW, AND HOW IT WAS CHECKED
>
> *(**Amendments 7 and 8** were ruled later the same night and each carries **its own** condition
> statement, at its own timestamp, in its own block — neither inherits this one.)*
>
> **Condition (rule 2's before-first-compute clause):** this document is a **DRAFT**, is **NOT
> frozen**, and **no compute has occurred under it**.
>
> **How checked, at 2026-09-04T0120Z, at the moment of this edit:** the two run roots this
> registration names in §12 — **`verification/runs/M6SR_runs`** and **`cases/M6SR`** — were tested
> for existence and **both returned absent**. ⚠ **The absence is evidence, not blindness (rule 3):
> the identical test, in the same invocation, was pointed at
> `verification/runs/RUNG1_M6_R2_runs` and `verification/runs/M6I_runs` and returned
> `PRESENT` on both.** A reader that could not see a directory could not have produced those two
> rows. This lane created neither run root and launched nothing.
>
> **NONE of the amendments in this section — 2 through 7 — alters ANY gate, threshold, cap or
> label.** Amendments 2, 3
> and 5 correct **characterisations and prose arithmetic**; amendment 4 corrects a **citation** and
> registers an **invariance that was already true**; amendment 6 adds a **disambiguation** and no
> number. The registered cost **table** at §2.4 is unchanged in every cell.

---

### AMENDMENT 2 — the `checkMesh` 0.33× figure is a PRIOR MEASUREMENT, not an inconsistency

**§13 item 2 characterises `RUNG0b:222` as carrying an "internal inconsistency", and §2.4's rate
table calls the gap an "11 % discrepancy in the source". BOTH CHARACTERISATIONS ARE WITHDRAWN AS
WRONG. The NUMBER THIS REGISTRATION USES IS UNCHANGED and remains correct.**

**Read at source before writing this amendment.** `RUNG0b_MESH_IMPORT_PREREGISTRATION.md:222`
reads, in full:

> `checkMesh` on 4 meshes | **30 wall s** = **0.0661 core-min/Mcell** — **NOT the converter rate**;
> **the predecessor priced this at 1× and measured 0.33×**

**There is no contradiction in that line, and the reason is grammatical as much as numerical.**
The `0.0661` is **RUNG0b's own measurement, on RUNG0b's own four grids**. The `0.33×` is
attributed by RUNG0b, in its own words, to **its predecessor** — a *third* document, a *different*
run, a *different* grid set. The line is a **calibration remark**: it says the predecessor priced
`checkMesh` at 1× and measured 0.33×, and that RUNG0b has now measured it again and got 0.0661.
**A document reporting what an earlier document measured, beside what it measured itself, is doing
exactly what `docs/COST_CALIBRATION.md` exists to make possible.** It is not disagreeing with
itself.

⚠ **This is a sharper correction than the one this lane was briefed to make.** The brief described
0.33× as *RUNG0b's own separate measurement*. It is not RUNG0b's measurement at all — RUNG0b
attributes it to **its** predecessor. The two figures are therefore **two documents apart**, not
one, and the case for calling them inconsistent is weaker still.

| | was | is |
|---|---|---|
| §2.4 rate table, `checkMesh` row | *"records the 11 % discrepancy in the source"* | **"records that `RUNG0b:222` also reports its OWN predecessor's `0.33×`, measured on different grids — a prior measurement, not a contradiction"** |
| §13 item 2 | *"flags the source's internal inconsistency… That inconsistency is in a frozen file"* | **"cites the source's own predecessor-calibration remark. There is no inconsistency and nothing in the frozen file needs touching."** |

**THE CHOICE IS UNAFFECTED AND IS RE-AFFIRMED.** `0.0661 core-min/Mcell` is the measurement taken
on the grids nearest this registration's own work, and `0.0661 / 0.1786 = 0.3701` is its ratio to
the converter rate on the **same** four grids. **Re-derived by this lane: `0.0661 / 0.1786 =
0.370100…`.** No cost-table cell moves.

---

### AMENDMENT 3 — the §2.4 PROSE total is wrong in both figures; the TABLE is right

**§2.4's prose at `:472` reads *"All-in: 615.1 core-min estimated, 1,902.0 core-min capped."*
Both numbers are wrong. The table at `:456` reads `≈ 615.2` and `1,903.0` and is right.**

**Re-derived by this lane from the table's own nine step rows, not copied from either statement:**

| | steps summed | result |
|---|---|---|
| estimate | `0.10 + 0.05 + 7.04 + 0.29 + 0.14 + 10.18 + 54.31 + 543.13 + 0` | **615.24 core-min** |
| cap | `1.0 + 1.0 + 70.0 + 3.0 + 2.0 + 31.0 + 163.0 + 1630.0 + 2.0` | **1,903.0 core-min** |

**And the three solve rows re-derived from the registered rate rather than trusted**, at
`3.40e-8 core-min/cell/iteration` on the registered `3,000 / 4,000 / 5,000` schedule:
`B5a = 99,840 × 3,000 × 3.40e-8 = 10.1837`; `B5b = 399,360 × 4,000 × 3.40e-8 = 54.3130`;
`B5c = 1,597,440 × 5,000 × 3.40e-8 × 2.0 = 543.1296`. **All three reproduce the table to the digit
printed.**

> **THE PROSE AT `:472` IS STRUCK AND REPLACED BY: "All-in: 615.24 core-min estimated, 1,903.0
> core-min capped, $1.6270 DERIVED at cap."** The table is unchanged; the prose is corrected **to
> the table**, never the reverse. **Rule 12 makes the cost table frozen content**, so it is the
> table that governs and the prose that was in error.

**The `≈ 615.2` in the table's TOTAL cell is a rounding of 615.24 and is not itself wrong**; this
amendment registers **615.24** as the exact figure so that §9.3's estimate-versus-actual
calibration row has an unrounded denominator to divide by.

---

### AMENDMENT 4 — `c` and `S_ref` are MIS-CITED. The citation is corrected; no gate moves; and `S_ref` is registered as UNUSED

**§3's opening at `:488` registers `c = 0.64607 m` and `S_ref = 0.7532 m²` and states they were
*"Read from the machine file's own zone title."* **THEY WERE NOT. THE CITATION IS FALSE AND IS
CORRECTED HERE.**

**Measured by this lane at the pinned hash, not relayed.** `cases/dafoam/ladder-a/logs_A3/case_2308.dat`,
sha256 `020c5fcc…f0d0` — re-verified by this lane, matching §4.1. Its zone title, read verbatim:

```
ZONE T=",Run= 308, Mach= 0.8395, Alpha=  3.06, Re= 11.72x10**6, Section 1", I=  34, F=POINT
```

**It carries Run, Mach, Alpha, Re and Section. It carries NO chord and NO reference area.** A
search of the whole file for `0.64607`, `0.7532`, `64607`, `7532`, `chord`, `area` and `ref`
returns **zero hits on every one**. ⚠ **The zero is controlled: the same file, read by the same
instrument in the same invocation, yielded the title line and the first data rows above** — the
reader demonstrably sees this file's contents.

**The true source of both constants is the printed AGARD AR-138 page (§2.1.7 and §4.7) — the
document §4.1 forbids as a source of numbers.**

#### 4a. THE INVARIANCE, CHECKED GATE BY GATE RATHER THAN ASSERTED — AND IT HOLDS

| gate | does it consume `c` or `S_ref`? | why |
|---|---|---|
| **A1–A9** | **NO** | angles, skewness, aspect ratio, integer cell-count ratios, sha256 identity, `cells/wing_faces`, patch types. No length normalisation anywhere. |
| **GF1–GF4** | **NO** | measured on **each level's own surface**: `t_TE/c` and `max │Δz│/c` normalise by the **root section chord measured on that surface**, not by the MAC; `GF4` compares sweep and semispan to AGARD directly. |
| **G1** | **NO** | `ΔC_D` over 500 iterations **≤ 1/10 of the `L3–L2` difference in `C_D`**. Both sides are `C_D`; `S_ref` scales both identically and cancels. |
| **G2c** | **NO** | identical form to `G1`. |
| **G3 (`p_s`)** | **NO** | an exponent from a **ratio of differences** of `C_D`. Any constant multiplier cancels in numerator and denominator. |
| **G4 (`GCI_fine`)** | **NO** | a **relative** error at `Fs = 1.25`. A constant multiplier cancels. |
| **Gate P** | **NO** | `C_p = (p − p∞)/(½ρU²)` — no area, no chord. The abscissa is the data file's own `X/L`, normalised by the **local section chord**, not the MAC. |
| **Gate R** | **NO** | `GATE FAIL` on level count and topology. No number of this kind appears. |

> ✅ **NO REGISTERED GATE QUOTES AN ABSOLUTE `C_D`.** Every `C_D` appearance in §5 — `G1`, `G2c`,
> `G3`, `G4` — is a **difference, a ratio of differences, or a relative error.** The invariance is
> therefore not a convenience; it is a property of how the gates were written. **Had any gate
> carried an absolute `C_D` threshold, `S_ref` would have been load-bearing and this amendment
> could not have been written.** It does not.

#### 4b. `S_ref` IS DISSOLVED. IT IS CONSUMED BY NOTHING IN THIS DOCUMENT.

**Measured, not assumed:** `S_ref` (in any spelling) occurs **exactly once** in this
registration — the §3 line being corrected. **No gate, no `0/` field, no derived quantity in §8,
and no comparator input uses it.**

> **REGISTERED: `S_ref = 0.7532 m²` is recorded for COMPLETENESS ONLY and is CONSUMED BY NOTHING.
> Its citation is corrected to "AGARD AR-138 §4.7, printed page — motivation, not a gate value."
> If it is wrong, NOTHING IN THIS REGISTRATION CHANGES.** §4.1's bar is not crossed, because
> §4.1 forbids the PDF as a source of **numbers the gates consume**, and this is not one.

#### 4c. 🔴 `c` IS **NOT** INERT, AND THE BRIEF'S "INVARIANT TO BOTH" IS TRUE OF THE GATES BUT NOT OF THE STATE

**This lane was briefed that both constants are dissolvable. `S_ref` is. `c` IS NOT, and saying so
is the point of checking rather than asserting.** `c = 0.64607` is consumed in **two** places, both
found by search and both named here:

1. **`:510` — the back-solve `μ∞ = ρ U c / Re`.** Re-derived by this lane:
   `1.224978126 × 285.679356 × 0.64607 / 11.72e6 = 1.9291196e-05` — reproduces the registered
   `1.929120e-05` exactly. **`c` sets the Reynolds number the solve actually runs at**: the
   simulation's Reynolds number with respect to the meshed geometry's true MAC is
   `11.72e6 × (c_true / 0.64607)`.
2. **`:1066` — `L_ref = MAC = 0.64607` in `omega_inf = 5 U∞ / L_ref`.** Re-derived: `5 × 285.679356
   / 0.64607 = 2210.9010`, reproducing the registered `2210.901 1/s`. A freestream turbulence
   length scale — a registered **choice**, and mild.

**THE RESOLUTION, WHICH DISSOLVES `S_ref` AND RE-CLASSIFIES `c` RATHER THAN CARVING AN EXCEPTION.**
`c` is not a **reference value being compared against** — the class §4.1 protects. It is a
**registered choice of the state pair's length scale**, in exactly the class §3 already assigns to
`T∞` and `p∞`, which §3(a) labels *"IT IS A CHOICE, NOT A MEASUREMENT FROM AR-138. In those
words."* **`c` joins them under that existing label. §4.1 is not amended, weakened or excepted.**

> **REGISTERED, REPLACING `:488`'s FALSE CITATION:**
>
> **`M∞ = 0.8395`, `α = 3.06°`, `Re = 11.72 × 10⁶` are READ FROM THE MACHINE FILE'S OWN ZONE TITLE
> at sha256 `020c5fcc…f0d0`** — that part of the original sentence is TRUE and is verified above.
>
> **`c = 0.64607 m` and `S_ref = 0.7532 m²` are NOT in that file. They are REGISTERED CHOICES,
> motivated by AGARD AR-138 §2.1.7 and §4.7 (printed page), carried under §3(a)'s existing
> choice-not-measurement label. `c` is consumed only by `μ∞` and `omega_inf`; `S_ref` is consumed
> by nothing. NO GATE CONSUMES EITHER.**

**AND AN INDEPENDENT CORROBORATION ON THE BOX'S OWN GEOMETRY, computed by this lane, offered as
support and NOT as a replacement.** For a linearly tapered planform,
`MAC = (2/3)·c_r·(1+λ+λ²)/(1+λ)`. At the standard M6 planform (`c_r = 0.8059`, `c_t = 0.4589`,
`b_semi = 1.1963`) this gives **MAC = 0.648267 m**, **+0.340 %** against the registered `0.64607`;
the semispan planform area gives **0.756540 m²**, **+0.443 %** against `0.7532`. ⚠ **Neither
reproduces the registered value exactly, and this lane does NOT claim they do** — they agree to
about half a percent, which corroborates that the registered constants describe *this* wing and
does not establish them to the five figures printed. **The registered values stand as choices; this
is a sanity check, and it is labelled as one.**

> **THE OPEN ITEM THIS LEAVES ON THE SUPERVISOR'S DESK, stated rather than buried:** if the
> supervisor prefers `c` to be a **measurement** rather than a registered choice, the instrument
> already exists — **`GF4` measures sweep and semispan on each level's own surface at `B0`**, and
> the MAC is the same class of planform arithmetic on the same surface, at no additional cap. This
> lane does **not** register that, because it would add a measurement to `Gate GF` and this
> amendment is forbidden to touch a gate.

---

### AMENDMENT 5 — Route A's import cost does not reconcile at this registration's own rates

**§2.1 (`:286`) and Gate R (`:970`) both price the mechanical import of the Route A CGNS at
*"≈ 0.7 core-min."* At this registration's OWN §2.4 rates, on Route A's OWN measured 185,664
cells, the figure is 15× smaller.**

**Re-derived by this lane from §2.4's two registered rates and §2.1's measured cell count:**

| term | rate (§2.4) | × 0.185664 Mcell | core-min |
|---|---|---|---|
| convert | 0.1786 core-min/Mcell | | **0.033160** |
| `checkMesh` | 0.0661 core-min/Mcell | | **0.012272** |
| **total** | | | **0.045432** |

`0.7 / 0.045432 = ` **15.4×**.

> **BOTH OCCURRENCES ARE STRUCK AND REPLACED BY "≈ 0.045 core-min."**

**THIS CHANGES NOTHING AND IS FIXED ANYWAY.** Route A is closed on **structure** — `A-F1`, one
level against `MESH_STANDARD.md` §9.1's three, and `A-F2`, overset topology — and §2.1 says in
terms that *"no amount of budget buys a second and third level out of a one-level file."* **The
0.7 was never load-bearing and the correction does not reopen the route.** It is corrected because
a document about to be frozen should not carry a figure that its own registered rates contradict
by an order of magnitude, and because `Gate R`'s cell is the one a future lane will read.

---

### AMENDMENT 6 — the `24,960` COLLISION, DISAMBIGUATED

**`24,960` denotes two different things in this document and they are distinguished only by the
surrounding prose, which a `grep` does not read:**

| occurrence | meaning | where |
|---|---|---|
| **24,960 FACES** | the new `L1` level's **surface**, the tutorial's own first-`coarsen` intermediate off the pinned master `197efa09…3327` | §2.2 (`:357`, `:360`, `:370`, `:382`, `:384`), §2.4 (`:430`, `:434`, `:448`, `:449`) |
| **24,960 CELLS** | the **CONDEMNED** `A3-onera-m6-adjoint-vcoarse` volume build on the 390-face surface `aab44d41…2326` — **23 negative-volume cells**, max AR **2.07741e+95**, max non-orth **135.318**, max skew **55.378** | §1.3 (`:115`) |

> 🔴 **THESE TWO OBJECTS SHARE NO ANCESTOR AND MUST NEVER BE CONFLATED.** The `L1` surface descends
> from the **99,840-face master by ONE `cgns_utils coarsen` call**; the condemned build descends
> from the **390-face surface, the master coarsened FOUR times**. **Gate `A8` exists precisely to
> keep `aab44d41…2326` out of every level**, and it is an `A8` failure — labelled **`NOT A
> RESULT`** — if the condemned surface ever appears.
>
> **REGISTERED CONVENTION, binding on every script, log line, JSON key and figure caption this
> registration produces:** the new level's surface is written **`24,960 faces`** or
> **`24960_faces`**, **never the bare integer**; the condemned build is referred to by its
> **surface hash `aab44d41…2326`** and never by its cell count. **A bare `24,960` in any artifact
> of this ladder is a defect to be reported, not interpreted.**
>
> **No gate, threshold, cap or label changes.** `A8`'s threshold was already the **hash**, not any
> count — which is why the collision was never able to defeat it, and why this is a naming repair
> rather than a gate repair.

---

### WHAT AMENDMENTS 2–6 DO NOT TOUCH

*(**Amendments 7 and 8** and **§14.1** follow this block — appended after it, and bound by every
line of it. Amendment 7 adds no gate, no threshold and does not touch `GF4`; Amendment 8 registers
a condition of the cost basis and changes no cost-table cell, no gate and no allowance; §14.1
registers no number of its own and is a pointer, not a gate.)*

- **No gate, threshold, cap or label moves.** The §2.4 cost **table** is unchanged in every cell.
- **Clause `L-HONEST` (§6) is UNCHANGED, and is re-affirmed rather than merely left alone.** The
  family refines **2 of 3 directions**; `GCI_fine` is a **LOWER BOUND**; `p_s` is **NOT an observed
  order**; and §6's consequence 3 — **"Sanaa's named first deliverable — M6 `Cp` WITH the family
  band — is NOT delivered by this registration. It remains owed."** — stands verbatim. **That is a
  measured finding and it travels upward. It is never a reason to widen a gate.**
- **`Gate P`'s `x/c ≤ 0.90` restriction is UNCHANGED**, on both of its independent justifications:
  the sharp trailing edge against AGARD's 0.14104 %-chord design TE, and the wall-interference
  systematic that **AR-138 B1-4 §6.2 itself declines to correct** at a semispan-to-tunnel-width
  ratio of 0.7.
- **§4.1's ruling is UNCHANGED**: the AR-138 PDF is provenance and is never a source of numbers the
  gates consume.
- **No predecessor is edited, amended or reinterpreted** (§0).

---

### AMENDMENT 7 — the `c` / planform-MAC discrepancy, REGISTERED AND **REPORTED, NOT GATED**

**Ruled by the cfd supervisor, 2026-09-04, inside their own territory. Implemented here by a cfd
lab-lane. This amendment ADDS NO GATE, ADDS NO THRESHOLD, AND DOES NOT TOUCH `GF4`.**

> **Condition and how it was checked, re-stated for THIS amendment at its own timestamp
> (2026-09-04T0128Z), not inherited from the block above:** this document is a **DRAFT**, is **NOT
> frozen**, and **no compute has occurred under it**. **`verification/runs/M6SR_runs`** and
> **`cases/M6SR`** were tested for existence and **both returned absent**; ⚠ **the same test, in
> the same invocation, returned `PRESENT` on `verification/runs/RUNG1_M6_R2_runs` and
> `verification/runs/M6I_runs`** (rule 3 — the reader is shown able to see a directory that
> exists). This lane created neither run root and launched nothing.

**WHY THIS IS REGISTERED RATHER THAN LEFT IMPLICIT.** Amendment 4c establishes that `c` is **not**
inert: it is consumed by `μ∞` (`:510`) and `omega_inf` (`:1066`), and therefore **it sets the
Reynolds number the solve actually runs at.** A registered choice may be a choice, but a choice
that sets `Re` **must not be silent about how far it sits from the geometry this ladder will
actually mesh.** This lab has a standing finding that a printed discrepancy labelled non-binding
beats one never computed.

**THE DISCREPANCY, STATED WITH ITS ARITHMETIC:**

| quantity | value | how obtained |
|---|---|---|
| **registered `c` (MAC)** | **0.64607 m** | **REGISTERED CHOICE**, motivated by AGARD AR-138 §2.1.7 (printed page). **Not** in `case_2308.dat` — see Amendment 4. |
| planform MAC, computed here | **0.648267 m** | `MAC = (2/3)·c_r·(1+λ+λ²)/(1+λ)` at the standard M6 planform `c_r = 0.8059`, `c_t = 0.4589` |
| **difference** | **+0.340 %** | `(0.648267 − 0.64607)/0.64607` |
| registered `S_ref` | 0.7532 m² | **REGISTERED CHOICE**, and **consumed by nothing** (Amendment 4b) |
| semispan planform area, computed here | 0.756540 m² | `½(c_r + c_t)·b_semi`, `b_semi = 1.1963` |
| **difference** | **+0.443 %** | — |
| **implied `Re` w.r.t. the planform MAC** | **11.7599 × 10⁶** | `11.72e6 × (0.648267 / 0.64607)` — a **+0.340 %** shift against the registered `11.72 × 10⁶` |

⚠ **THE CAVEAT FROM AMENDMENT 4, CARRIED HERE VERBATIM AND NOT SOFTENED:** *"Neither reproduces the
registered value exactly, and this lane does NOT claim they do — they agree to about half a
percent, which corroborates that the registered constants describe **this** wing and does not
establish them to the five figures printed. The registered values stand as choices; this is a
sanity check, and it is labelled as one."*

> ## **REGISTERED: `REPORTED, NOT GATED`.**
>
> **The `+0.340 %` MAC discrepancy and the implied `Re = 11.7599 × 10⁶` are RECORDED and TRAVEL
> ONTO THE CERTIFICATE beside the registered `Re = 11.72 × 10⁶`. They gate NOTHING.**
>
> **NO gate, NO threshold, NO cap and NO label is created, moved or widened by this amendment.
> `GF4` is UNTOUCHED — it continues to measure leading-edge sweep and semispan only, at its
> registered `±0.01°` and `±0.1 %` and its 0.1 core-min cap, and it acquires no MAC measurement.**
>
> **`μ∞ = 1.929120e-05` and `omega_inf = 2210.901 1/s` are UNCHANGED.** The solve runs at the
> registered state pair. This amendment changes what is **disclosed**, never what is **computed**.

**THE SYSTEMATIC IS SMALL AND IS EXPECTED TO STAY SMALL — AND THAT IS NOT A REASON TO OMIT IT.**
A **+0.34 %** shift in `Re` on a transonic wing is far below the band Gate P will carry
(`ΔCp = ±0.02` from AR-138 alone) and far below the discretisation term `L-HONEST` already labels a
**lower bound**. It is registered because a systematic that is invisible cannot be reasoned about
later, not because it is expected to matter.

---

### 14.1 🔴 THE SECOND WALL — WHY BRANCHES (a1)/(a2) DO NOT COME BACK, IN SANAA'S OWN WORDS

**Written here, and pointed to from §1.1, because this is the paragraph a future lane proposing to
revive (a1) or (a2) needs to hit before it spends anything.**

**FIRST, THE FACT THAT IS EASIEST TO MISS: (a1) IS `RUNG1_M6_R2`, AND IT ALREADY RAN.**
`RUNG1_M6_R2_PREREGISTRATION.md:311` registers step `S3` as the nested pyHyp triple
**8,970 / 71,760 / 574,080** — **byte-for-byte (a1)'s triple** from `RUNG1_M6_PREREGISTRATION.md:326`.
That registration was **FROZEN at `3126345f`**, it **ran** (`verification/runs/RUNG1_M6_R2_runs/{L1,L2,L3}`,
verified present), and it carries a **post-compute Addendum 1** at `7260f6c9`. **The revival is not
a live option to be re-taken. It happened, and it ended.**

**AND (a1)'s COST IS NOT AN UNSOURCED FIGURE — a claim that has circulated and is wrong.** It is
derived and reproducible: `8,970×2,000 + 71,760×3,000 + 574,080×4,000 = 2,529,540,000`
cell-iterations × **4.02e-08** (that registration's conservative rate) = **101.6875 core-min**.
The same triple at that document's *point-estimate* **3.3977e-08** gives **85.946** — which is the
`85.9` that appears elsewhere. **One triple, two rates, both stated in the same file.**

**THE TWO WALLS, AND THE SECOND IS THE STRONGER.**

**WALL 1 — the over-determination theorem (§1.1).** Structural, not empirical. `r` moved
**1.6329 → 1.2739** across the two levels actually built. The family cannot produce a Roache
triple. **Killed at the algebra.** And (a1)'s coarse level is `390 × 23 = 8,970` — **the CONDEMNED
390-face surface `aab44d41…2326`** of §1.3, which produced negative-volume cells and an `e+95`
aspect ratio under two completely different parameter sets. Gate `A8` refuses it by hash.

**WALL 2 — SANAA'S OWN ILL-POSEDNESS EXCEPTION, WHICH THE 2026-09-03 RULINGS DID NOT REMOVE.**
The rulings `d8d04b06` / `825285bb` / `43b7196e` moved **mesh-quality gates** — skewness,
non-orthogonality, aspect ratio, `y⁺` — into the **record-as-prediction** class. That is her own
enumerated list and it is not in dispute. **But the same ruling carries its own exception, in her
words** (`etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md`):

> *"Exceptions where 'launch anyway' is wrong: a setup that's physically ill-posed (**no outlet**,
> inconsistent boundary conditions, geometry with leaks) will diverge and teach nothing — that's a
> **blocking physics fix**, not a pre-registration mismatch."*

**And the object that carried the 88.88926674° was a CLOSED ALL-WALL BOX** — its
`constant/polyMesh/boundary` held **one patch, `defaultFaces`, type `wall`, 9,376 faces**: no
inlet, **no outlet**, no symmetry (recorded on the cfd board against `0a7562c3`).

> **SO THE 88.889° WAS MEASURED ON AN OBJECT THAT HER SURVIVING BLOCKING CLASS ALREADY COVERS.**
> **A reviver arguing that the gate reclassification lets (a1)/(a2) back in hits this second wall,
> and it is in HER words rather than ours.** The reclassification removed a **mesh-quality** block;
> it did not — and by its own text could not — remove the **ill-posedness** block. **That mesh
> could never have been solved.**
>
> ⚠ **AND THE RECLASSIFICATION IS NOT A CLAIM THAT THE MESH IS GOOD.** *A gate moving from BLOCKING
> to RECORD-AS-PREDICTION changes what the number stops, never what the number is.* The
> **88.88926674°**, the **206 severely non-orthogonal faces** and the **AR 35,820.56** stand
> exactly as measured. §7 of this registration is the only thing that blocks a launch, and it
> blocks on precisely this ground.

**FOR COMPLETENESS, AND BECAUSE THIS REGISTRATION'S OWN ROUTE IS A DIFFERENT OBJECT:** Route B's two
existing levels measure **61.4938°** and **61.1581°** max non-orthogonality — **under** the 70°
threshold as it stood before any reclassification — on meshes with **three correctly typed patches**
(`wing` wall / `inout` patch / `sym` symmetry, §2.2). **Route B does not carry the 88.889°, and
neither wall above applies to it.**

**⚠ AN UNRESOLVED FIGURE, NAMED RATHER THAN TIDIED AWAY.** A **third** (a1) cost, **103.6 core-min
(cap 443.6)**, appears on the cfd board and this lane **could not reproduce it**. Its provenance
is found — it entered at `de1bc520` (2026-09-02, the board write that corrected the M6 cost basis
by 100×) — but **its arithmetic is not recoverable**: the implied rate is **4.0956e-08
core-min/cell/iteration**, which matches **none** of the rates any registration names
(`3.3560e-08`, `3.3977e-08`, `4.02e-08`), and the sibling rows of that table do not scale against
the later table by any single factor (`a1` 0.9817, `a2` 1.0343, `b` 1.0125). The implied rate does
fall inside the **2.69e-08–4.72e-08** eight-run band — **the band `RUNG1_M6_PREREGISTRATION.md` §6
explicitly REJECTED because five of its eight runs were never re-derived.**
**VERDICT: PROVENANCE FOUND, ARITHMETIC UNSOURCED — and superseded either way.** The figures to
use are **101.7** (conservative rate) and **85.9** (point-estimate rate), both derived above.

---

### AMENDMENT 8 — THE RANK COUNT IS A **CONDITION OF THE COST BASIS**, NOT AN IMPLICIT ASSUMPTION

**Ruled by the cfd supervisor, 2026-09-04, inside their own territory. Implemented by a cfd
lab-lane. NO gate, threshold, cap or label is created, moved or widened. The ×2.0 superlinear
allowance is NOT changed. `GF4` is untouched. No cost-table CELL changes.**

> **Condition and how it was checked, at this amendment's own timestamp (2026-09-04T0133Z):** this
> document is a **DRAFT**, is **NOT frozen**, and **no compute has occurred under it**.
> **`verification/runs/M6SR_runs`** and **`cases/M6SR`** both **absent**; ⚠ **the same test in the
> same invocation returned `PRESENT` on `verification/runs/RUNG1_M6_R2_runs` and
> `verification/runs/M6I_runs`** (rule 3). This lane created neither run root and launched nothing.

#### 8a. 🔴 THE FACT THAT WAS NOT REGISTERED ANYWHERE: **THE RATE'S OWN BASIS IS 4 RANKS**

**Measured by this lane, from the solver log's own banner, per §1273's rule and not from
`decomposeParDict`:** the registered solve rate **3.40e-8 core-min/cell/iteration** comes from
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/run_model_run3.log`, whose primal banner reads
**`nProcs : 4`**.

⚠ **AND THE TRAP §1273 WARNS OF FIRED IN THIS VERY FILE, WHICH IS WHY THE RULE IS KEPT:** that
log's **first** `nProcs` match is **`nProcs : 1`** (line 30); the primal banner is at **line 63**.
**Taking the first match would have quartered the rate.** The case's own
`system/decomposeParDict` reads `numberOfSubdomains 2` and **post-dates the run** — a third,
different, wrong answer. **Three candidate values, one instrument, and only the banner is right.**

> **REGISTERED, AND IT WAS PREVIOUSLY IMPLICIT: `3.40e-8 core-min/cell/iteration` IS A 4-RANK
> MEASUREMENT.** The registered decompositions are `B5a` **(4 1 1) = 4 ranks**, `B5b`
> **(8 1 1) = 8**, `B5c` **(16 1 1) = 16**. **`B5a` sits ON the rank basis; `B5b` is 2× off it;
> `B5c` is 4× off it.**

#### 8b. WHAT THE RANK COUNT DOES AND DOES NOT MOVE — STATED EXACTLY, BECAUSE IT IS EASY TO GET BACKWARDS

**Core-minutes are `wall s × ranks ÷ 60`. The registered rate is already expressed in
core-minutes. Therefore the CORE-MINUTE ESTIMATE IS IDENTICAL AT EVERY RANK COUNT — by the rate's
own construction — and what the rank count changes is (1) the WALL time and (2) the SIZE AND SIGN
OF THE PARALLEL-EFFICIENCY ERROR against the 4-rank basis.**

> **THE ASSUMPTION THIS MAKES EXPLICIT, AND IT WAS NEVER WRITTEN DOWN BEFORE:** applying a
> **4-rank** core-minute rate at **8** or **16** ranks assumes **PERFECT STRONG SCALING**. Real
> parallel efficiency is below 1, so core-minutes **RISE** with rank count at fixed work. **The
> registered estimates therefore carry an unregistered upward bias that grows with the rank
> extrapolation, and this clause registers it.**
>
> ⚠ **NO EFFICIENCY MODEL IS ADOPTED AND NO CORRECTION IS APPLIED.** This lab has **no measured
> strong-scaling curve for `rhoSimpleFoam` on this box at any mesh size.** The direction is
> known; the magnitude is **NOT** estimated here, and inventing one would be exactly the
> laundering this registration exists to avoid.

**REGISTERED, BOTH RANK COUNTS, EACH DERIVED — so whichever the launch gets has a denominator
waiting for it (§9.3):**

| step | core-min est. | cap | ranks | **est. WALL (min)** | **cap WALL (min)** | rank extrapolation from the 4-rank basis |
|---|---|---|---|---|---|---|
| `B5a` | 10.1837 | 31.0 | **4** | **2.546** | 7.750 | **1× — ON BASIS** |
| `B5b` | 54.3130 | 163.0 | **8** | **6.789** | 20.375 | **2×** |
| `B5c` **as registered** | 543.1296 | 1630.0 | **16** | **33.946** | 101.875 | **4×** |
| `B5c` **at 8 ranks** | **543.1296 — UNCHANGED** | 1630.0 | **8** | **67.891** | 203.750 | **2×** |
| `B5c` **at 4 ranks** | **543.1296 — UNCHANGED** | 1630.0 | **4** | **135.782** | 407.500 | **1× — ON BASIS** |

**The fleet safety ceiling (§2.5) is 4,890 core-min and is likewise rank-invariant in core-minutes,
but its WALL horizon is not** — and a monitor watching a clock needs it: **305.6 min (5.09 h) at
16 ranks, 611.3 min (10.19 h) at 8, 1,222.5 min (20.38 h) at 4.** Registered so the monitor's
deadline is derived rather than guessed at launch.

#### 8c. P4's DIRECTION UNDER EACH RANK COUNT — AND IT NAMES THE PARAMETER

**`P4` (§11) predicts `B5c` will overrun 543.13 core-min and that the ×2.0 allowance is TOO SMALL.
That prediction is UNCHANGED. It now names the parameter it depends on:**

| rank count | pressures on `B5c`'s core-minutes | **P4's direction** |
|---|---|---|
| **16 (registered)** | **TWO** upward terms: the 4× cell extrapolation, **and** a 4× rank extrapolation with efficiency < 1 | **UP — P4 stands as written**, and is supported by two independent mechanisms rather than one |
| **8** | cell extrapolation unchanged; rank extrapolation only **2×**, so less inflation | **WEAKENED. P4 may REVERSE** — with a smaller total error, the ×2.0 allowance may prove **too LARGE** |
| **4** | rank term **vanishes** (on basis); the **only** error is cell-count | **P4 rests SOLELY on the cell-count finding**, and is the cleanest test of it available |

> **`P4` IS GRADED AGAINST THE RANK COUNT THE RUN ACTUALLY USED, READ FROM ITS OWN SOLVER-LOG
> BANNER (§1273), AND THE CERTIFICATE STATES THAT COUNT BESIDE THE VERDICT.** A prediction that
> reverses with an operational parameter is still falsifiable — **but only if it names the
> parameter, and now it does.** **If `B5c` runs at 8 or 4 ranks, a P4 miss in the DOWNWARD
> direction is a genuine miss and is graded as one; it is not re-read as a hit.**

#### 8d. THE BOX CANNOT SUPPLY 16 RANKS RIGHT NOW — MEASURED, AND NOT A REASON TO CHANGE A NUMBER

**Measured by this lane at 2026-09-04T0133Z:** `nproc` = **16**; `/proc/loadavg` = **20.47 / 22.71 /
23.32**, i.e. the box is **oversubscribed at every averaging window** by foreign work
(heat-transfer's T-family solve is live). **`hierarchical (16 1 1)` is not currently available.**

> **THIS IS A RESOURCE GATE, AND UNDER SANAA'S 2026-09-03 RULING (`825285bb`) A RESOURCE GATE
> **QUEUES**, IT DOES NOT BLOCK** — her words: *"Resource gates (box busy, memory): these are real
> physical limits, not predictions — queue, don't launch. But queueing is not blocking; the run
> stays scheduled."* **Nothing here blocks this registration, and NO RUNNING SOLVER IS TOUCHED.**
>
> **AND THE NUMBER IS NOT MOVED TO FIT THE BOX.** The registered decomposition stays
> `(16 1 1)`. If the launch takes 8 ranks instead, **that is recorded as the condition it ran
> under and graded against this table** — not retro-fitted into the registration.

#### 8e. ⚠ A CORRECTION TO THE INSTRUCTION THIS LANE WAS GIVEN, MADE AT SOURCE

**This lane was briefed that a prior pass had "re-attributed the ×2.0 allowance away from cache to
16-rank parallel inefficiency." IT HAS NOT. That re-attribution IS NOT IN THIS DOCUMENT.**

**Read at source:** §2.4 (`:479`) still states the mechanism as **"working set outgrowing
cache"**, labelled **INFERRED, not instrumented — no PMU counter is collected here and none is
claimed** — and its cited basis is `docs/COST_CALIBRATION.md`'s JF1 finding, which is a
**CELL-COUNT** result (1.448× optimistic at 90k cells, 5.84× at 455k, from a 40k-cell basis).
**Nothing in the registration ties the ×2.0 to ranks.**

> **THE AMENDMENT IS WRITTEN SO THAT IT DOES NOT DEPEND ON THAT CLAIM.** The rank dependence
> registered above is a **SEPARATE, NEWLY NAMED CONDITION** of the cost basis — it arises from the
> rate being a **4-rank measurement**, which is a fact of the log — and it is **NOT** a
> re-attribution of the ×2.0 allowance, whose stated mechanism and stated basis are **left exactly
> as they are.** **The ×2.0 is not changed, not re-justified, and not re-explained.**
>
> **This matters beyond bookkeeping:** had the amendment been written on the relayed premise, the
> registration would have carried a mechanism claim **no artifact supports**, and §9.3's
> calibration row would later have attributed a cost miss to the wrong cause. **The two mechanisms
> are now separable in the record, which is the only way the calibration can ever tell them apart.**

---

### 14.2 THE SUPERVISOR'S RULINGS ON §13's OPEN ITEMS — RECORDED AS **THEIRS**, WITH AN OWNER

**These are the cfd supervisor's judgements, ruled 2026-09-04, recorded here so each has a named
owner rather than sitting as an unattributed lane opinion. NO threshold, gate, cap or label is
changed by any of them — each either ENDORSES a value already registered or ACCEPTS a labelled
basis already in force.**

| §13 item | ruling | the supervisor's stated reasoning |
|---|---|---|
| **10 — `GF1`'s ±10 % band** | ✅ **SET AND SIGNED BY THE SUPERVISOR. Band UNCHANGED at ±10 %.** | `t_TE/c = 0.0014104` puts the band at **`[0.00127, 0.00155]`**; a sharpened surface reads **0.0** and the independent W5 CGNS reads 0.0014104 to seven figures. **The gate must separate "sharpened" from "true TE" and there is nothing whatever in the gap**, so the band's exact width is not load-bearing. ±10 % is **honest about being a round number** rather than pretending to a precision the discrimination does not need. 🔴 **"A band chosen where nothing can land is not a band chosen to fit an answer."** |
| **1 — off-basis converter rate** | ✅ **ACCEPT as labelled.** | It prices `B3` at **0.2853 against a 3.0 cap — 10.5× margin**; the `ugrid_to_foam.py` → `plot3dToFoam` transfer cannot move the total by anything that matters, and disqualifying it would cost more than it buys. **The honesty label stays; the label is the point.** |
| **4 — `D1`'s 0.75 margin** | ✅ **ENDORSED.** | 25 % is far above trapezoidal error over 34–45 taps, and the "anything else" branch **fails safe to `NOT A RESULT` rather than to a guess.** A judgement that fails safe is one the supervisor will own. |
| **6 — `b_semi = 1.19676 m`** | ✅ **ACCEPT — it self-closes at `B0`.** | `GF4` measures semispan on each level's own surface against AGARD's printed **1.1963 m**, and the carried value differs by **0.039 %**, inside `GF4`'s **±0.1 %** band — **so the gate is not pre-decided by the choice.** |
| **11 — §1.5's relayed CGNS figures** | ✅ **ACCEPT behind their fence**, with one enforcement. | Motivation for `Gate GF`, **never a gate value**. **ENFORCED: they must NEVER be re-quoted downstream as measurements.** |
| **3 — the ×2.0 allowance** | ⏳ **OPEN, and it is what held the freeze.** | See **Amendment 8**. The allowance itself is **unchanged**; what was missing was that the cost basis's **rank count was never registered**. ⚠ **And see §14 Amendment 8e: the re-attribution of this allowance from cache to rank scaling, which the ruling assumed had happened, HAS NOT happened in this document — the two mechanisms are kept separable so §9.3 can tell them apart.** |

> **NONE OF THESE RULINGS MOVES A NUMBER.** Every one endorses a value that was already registered
> or accepts a basis already labelled. **§13 items 1, 4, 6, 10 and 11 are hereby CLOSED with an
> owner; item 3 is closed by Amendment 8 as to its BASIS and remains open as to its MAGNITUDE**,
> which only the `B5c` run and §9.3's calibration row can settle.

---

## 15. AMENDMENT 9 — 2026-09-04T0422Z. THE §9.1 GRADING PATH NOW EXISTS AND IS PINNED BY BLOB SHA

**Drafted by a cfd lab-lane on the cfd supervisor's instruction. THIS IS NOT A FREEZE AND NOT A
RE-FREEZE.** The `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's, is not delegated, and is
**undischarged as this section is written**. **No compute was launched by the lane that wrote it.**

### 15.1 THE CONDITION, AND HOW IT WAS CHECKED — RULE 2 REQUIRES BOTH

> **Rule 2's window is keyed to FIRST COMPUTE, not to the freeze flag:** *"Before first compute,
> amendments are legal and must state the condition and how it was checked (name the run directory
> that does not exist)."*

**THE RUN DIRECTORY THAT DOES NOT EXIST — NAMED, AS RULE 2 REQUIRES:**
**`verification/runs/M6SR_runs/`**, and with it `verification/runs/M6SR_runs/{L1,L2,L3}/`.

**How checked, at 2026-09-04T0422Z, in one invocation, WITH A LIVE PLANTED CONTROL (rule 3):**

| path | reader's answer | role |
|---|---|---|
| `verification/runs/M6SR_runs` | **ABSENT** | the run root — **the zero** |
| `verification/runs/M6I_runs` | **PRESENT** | **the planted non-zero** |
| `verification/runs/RUNG1_M6_R2_runs` | **PRESENT** | **the planted non-zero** |

**The same reader, in the same invocation, returned PRESENT on two directories and ABSENT on the
third. The zero has a non-zero beside it.** Corroborated against the tree rather than the disk
alone: `git ls-tree -r --name-only HEAD -- verification/runs/M6SR_runs` returns **0 files**, while
the identical command on `verification/runs/M6I_runs` returns **14**.

⚠ **AND ONE THING HAS CHANGED SINCE THE FREEZE BLOCK, STATED PLAINLY RATHER THAN GLOSSED.**
`cases/M6SR` now **EXISTS** — this amendment created it. That is not a defect and not compute: it
is **§9.1's own requirement**, which rules that the comparator and driver *"are written and
committed **before** the freeze, so the freeze can pin their blob shas."* It holds **exactly two
files, both listed in §9's frozen path table, and nothing else**: no `0/`, no time directory, no
`log.*`, no `postProcessing`, no mesh. **The no-compute assertion is therefore made about the RUN
ROOT, which does not exist, and not about `cases/`, which is the grading path and is supposed to.**

### 15.2 WHAT THIS AMENDMENT DOES **NOT** DO

**It moves NO gate, NO threshold, NO cap and NO label.** Not one number in §5, §5.1, §2.4 or §10
is touched. It adds two blob shas to §9's already-registered paths, records a defect repair in a
loader §5 already registered, and lists — **without repairing any of them** — items that cannot be
satisfied as the document stands. **Every one of those is left for the supervisor.**

### 15.3 THE TWO FILES, PINNED BY BLOB SHA AS §9.1 REQUIRES

| §9 registered path | git blob sha | sha256 of the file | lines |
|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`97cbe0390318f010f7d1dd8ebe4e870fd72c5e68`** | `168fd0896a4055e1106a1ba0eaaf00e6eca1851109a6aa9b60ebcbde32891f75` | 2,106 |
| **`cases/M6SR/build_m6sr_l1.sh`** (build driver) | **`04ae9d58220a55fa900b02f77424bb7687da0de1`** | `6459428b4c283c597e72e08f7c7ded3c454cfb8efd0facbbc8b178b42e5abc35` | 304 |

**`scripts/check_comparator_freeze.py` can now do at grading what §9.1 says it must: verify that
the frozen file IS the file that ran.** Before this amendment it could not, because there was no
file and no sha to verify against.

**Sections implemented, so the mapping is auditable rather than asserted.** The comparator
implements §1.3 (A8), §1.4 (A5, C5/C6), §2.2 (A4/A6/A7), §4.1 (Gate P's pinned-hash refusal, C11),
§4.3 (`D1`, C12/C13), §4.5 (the order-independent channel), §5 (Gates A / GF / G / P / R), §5.1
(G2a/G2b/G2c), §6 (clause `L-HONEST`, quoted **verbatim** on every output), §7 (A9), §8.6 (rule-4
strict completion), §9.2 (the exit vocabulary and the no-bare-`assert` rule), §10 (C1–C20) and §12
(printed with every verdict). The driver implements §2.2 (one `coarsen` call on the pinned master;
`s0`/`N`/`marchDist` unchanged), §2.4 (the `B1`/`B2`/`B3` caps, enforced **structurally** by
`timeout`), §7 (it REFUSES a level whose patch names it did not expect), §8.5, §8.6 (it REFUSES a
case where `0` or any time directory exists), §9.2 and §9.3.

**Exit vocabulary, fixed at `0` / `2` / `70`, because a crash is not a refusal.** `0` = the
instrument ran (a *verdict* may still be `GATE FAIL` or `NOT A RESULT`); `2` = **REFUSAL**; `70` =
an internal defect of the comparator, which is never a finding about the M6. **Verified by AST
parse rather than by grep** — `ast.Assert` node count is **0** in both the comparator and the
repaired loader, against **43** and **5** explicit `raise` nodes; `python3 -O` therefore deletes
nothing, and control `C16` measured **identical rc and identical control verdicts** under
`python3` and `python3 -O`.

### 15.4 THE §10 CONTROLS — MEASURED, AND ONE OF THEM DOES NOT FIRE

**19 of the 20 registered controls FIRE. `C12` does not, and it is reported rather than loosened.**
`C1`–`C11`, `C13`–`C15`, `C17`–`C20` and `C16` all fired; a targeted **mutation control** replaced
the shipped statistic behind each of eighteen of them in turn and **each mutation flipped exactly
its own control to red**, so no control in this suite is decorative.

**`C17` is the one worth quoting, because it is this ladder's most load-bearing zero.** As read,
the 1,560-face level's root section returns **`t_TE/c = 0.000000`**. With a **2.000e-04 m** trailing-edge
split planted into a scratch copy and **read back from disk**, the same reader returns
**`t_TE/c = 2.4807e-04` on 2 nodes** — against the worked precedent's `2.48170e-04`, agreeing to
four significant figures. **The zero is therefore evidence, and `GF1`'s predicted `GATE FAIL` on a
sharp trailing edge is corroborated by a reader that has been shown able to say otherwise.**

### 15.5 THE `C19` DEFECT — REPAIRED, AND A FILED RECORD CORRECTED AT SOURCE

**§10's `C19` and §5 both register `REFUSAL (exit 2)` on limb (a),
`verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat`. Measured before repair: `rc = 1`
with an `IndexError`.** That file is **single-column** — its first content line is the bare count
header `63` — so the loader's two-column `parse()` returned **zero rows, not 63**, and the planted-
control block indexed `rows[-1]` on an empty list. The resulting `IndexError` is **neither**
`ReferenceStructureError` **nor** `SharpenedReferenceError`, so it **escaped both catch limbs**.
The loader's own comment claimed this bug class fixed; **that fix treated the wrong site** — the
file died in the plant block before reaching the structure check the fix guards.

**Repaired:** the count check now runs **before** the plant, with an explicit zero-row refusal that
names the count-header shape. **Measured after repair — `rc = 2` on limb (a), unchanged `rc = 2` on
limb (b), unchanged `rc = 0` on limb (c), identical under `python3 -O`.** A new control **`C19b`**
feeds a synthetic count-header lookalike yielding zero two-column rows and requires `rc = 2`, so
the defect cannot return silently.

🔴 **`models/onera_m6/PROVENANCE.md:190` filed that fixture as "REFUSED … rc=2", and it does not
reproduce. It has been corrected by STRIKE-AND-QUOTE, never by rewriting, and the correction says
what is true: the row was WRONG WHEN WRITTEN, not drifted.** Verified rather than assumed — the
loader and `PROVENANCE.md` landed in the **same commit `d554e3a7`** and the loader's blob is
**byte-identical** at `d554e3a7` and at the HEAD preceding the repair.

✅ **AND THE SCOPE, NEITHER INFLATED NOR MINIMISED: THE LOADER DID NOT FAIL OPEN.** `rc = 1` is not
`rc = 0`; it failed **noisily**, wrote no verdict, and would have stopped any caller checking its
exit code. **No sharpened file was ever accepted as Table B1-1 and no graded number rests on this.**
Exactly two things were broken: an **unmet `C19` contract** (a crash is not a refusal), and an
**overstated filed record** — the second being the worse, because a filed measurement is what a
later reader trusts *instead of* re-running.

### 15.6 🔴 FOUR THINGS THAT CANNOT BE SATISFIED AS THIS DOCUMENT IS FROZEN

**Recorded, NOT repaired. Every one is a threshold-, instrument- or control-level question, and
this lane is not entitled to any of them. They are on the supervisor's desk.**

| # | what cannot be satisfied | measured basis | what the comparator does about it |
|---|---|---|---|
| **1** | **§5's `G3`/`G4` consume a REFINEMENT RATIO `r` that no section of this document registers.** `G3` says *"from the three-level ratio"*, `G4` says *"`GCI_fine` … at `Fs = 1.25`"*, and Gate P's numerical band channel consumes `GCI_fine` **directly**. | Three defensible conventions exist and give three different bands: `r = 2.000` (linear, in the two refined surface directions), `r = 4^(1/3) = 1.5874` (the conventional 3D cell-count ratio), `r = 4.000` (the raw face/cell ratio). | **REFUSES (exit 2)** at Gate G, prints `p_s` and `GCI_fine` for **all three** candidates, and adopts **none**. Choosing one after the freeze would be choosing a gate parameter to fit an answer. |
| **2** | **`D1`, evaluated on the pinned experimental bytes, returns `INDETERMINATE` — so §4.3's own consequence fires and Gate P's PER-STATION channel is `NOT A RESULT` before any compute.** | `Cn` = **0.2396, 0.2785, 0.2947, 0.2638, 0.2230, 0.1784, 0.2105** — **non-monotone**, and `Cn(7)/Cn(1) = 0.8787`, inside §4.3's registered indeterminate band `(0.75, 1.333)`. Computed by §4.3's own recipe on `case_2308.dat` at the pinned sha256, **with no CFD in existence**, so it cannot have been chosen to fit an answer. | Reports it. **This is not a defect — it is §4.3 working**, and it means **615 core-min of ladder cannot produce a per-station Gate P verdict as registered.** |
| **3** | **§10's `C12` registers its must-see as `FALSIFIED` and CANNOT FIRE on this data.** | Reversing a **non-monotone** `Cn` series leaves it non-monotone: as-read `INDETERMINATE`, reversed `INDETERMINATE`. | Implemented **to the letter**, allowed to fail, and the whole suite **REFUSES (exit 2)** as a result. **A registered control is not loosened to its purpose clause so that it passes.** Reported separately, and never substituted for `C12`: all three `D1` branches **are** reachable on synthetic fixtures, so this is a **fixture limit, not a one-answer discriminator**. |
| **4** | **§5's `GF4` says "semispan of each level's surface" and the surface has TWO semispans that straddle the ±0.1 % tolerance.** | The wing tip is a **ROUNDED CAP**. The wall patch's **span extent** measures **1.216405 m** (**+1.68 %** on AGARD's 1.1963 m — outside the band); the **planform semispan**, from where the straight leading edge ends, measures **≈1.1953 m** (**−0.08 %** — inside it). ⚠ **This also undercuts §14.2's ruling on §13 item 6**, which accepted `b_semi` on the reasoning that the difference was *"0.039 %, inside `GF4`'s ±0.1 % band — so the gate is not pre-decided by the choice."* **Measured, the choice of instrument decides the verdict.** | Reports **both**, labels the semispan limb **`NOT A RESULT`** — which under standing rule 5 can only make a gate worse, never better — and takes no gate decision. |

**A fifth item, resolved rather than escalated, recorded because a successor will hit it:** §5
writes the root section as *"`y = 0` exactly"*. **Measured, this box's M6 meshes span along `z`**
(root plane `z = 0`, thickness along `y`, chord along `x`). That is the **registration's notation**,
not a defect in it, and no gate depends on the letter — so the comparator **derives** the three axes
from the symmetry patch rather than hardcoding either convention, and **REFUSES** on a mesh where
they cannot be derived.

### 15.7 THE FIRST FREEZE WAS PREMATURE. THAT RECORD STANDS AND IS NOT TIDIED AWAY

**Recorded by the cfd supervisor at commit `009885a5`, in their own words, and preserved here by
quote rather than absorbed:**

> *"MY OWN FREEZE WAS PREMATURE — I discharged check 4 against a list I composed rather than the
> list section 9.1 specified, and M6SR is BLOCKED on its own grading path."*

**The mechanism, stated once so it is not softened.** §9.1 RULES that the comparator and driver
*"are written and committed **before** the freeze, so the freeze can pin their blob shas."* At the
freeze commit `40f2d9b9` **neither file existed** — measured: files under `cases/M6SR/` = **0** at
`40f2d9b9`, **0** at the HEAD preceding this amendment, **0** on disk — and **no blob sha was
pinned for either**. §9.1 was therefore unsatisfiable at the moment it was declared satisfied, and
`B0` and `B1` both route through those files, so the ladder could not start.

⚠ **The freeze banner at the head of this file is NOT struck and NOT rewritten.** Its planted-
control measurement — `verification/runs/M6SR_runs` and `cases/M6SR` both ABSENT, beside two
PRESENT controls — **was true when it was made**, and it remains the evidence that no compute had
occurred. **What was wrong was not that measurement but the CHECKLIST it was checked against.**
Rewriting the banner would destroy the record of the error; **this section is the disclosure, and
the banner is the artifact it discloses.**

### 15.8 COST — RULE 12, AND NONE OF IT IS LADDER COMPUTE

**No step of §2.4's cost table was run. `B0`–`B6` remain unspent and `verification/runs/M6SR_runs`
does not exist.** What this amendment spent is **comparator development and its control suite**,
which §2.4 does not cost and which produces no graded number: **≈ 5 core-min at 1 rank**, of which
the only exactly-timed figure is the full selftest at **103.5 wall s = 1.725 core-min**. **The rest
is a wall-clock estimate of this session's own runs and is labelled an ESTIMATE, not a measurement
read from a log** — no run-log exists for it, and inventing one would be worse than saying so.
**Derived at the owner-stated `c7a.4xlarge` $0.0513/core-h: ≈ $0.0043 — DERIVED, REPORTED-BY-OWNER,
never measured, because the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5).

**§9.3's estimate-versus-actual row is NOT owed yet**, because no `B` step has completed. It falls
due at `B1`'s completion and the driver already emits it into `BUILD_RESULT.json`.

### 15.9 WHAT HAPPENS NEXT, AND WHO MAY DO IT

**The re-freeze is `SUPERVISION_CHARTER.md` §3 check 4 and it belongs to the cfd supervisor. This
lane did not re-freeze, has launched no compute, and claims no verdict of the fixed vocabulary for
any gate of this registration.** The four items in §15.6 are **not** for a lane to rule: item 1 is a
gate parameter, item 4 is a gate instrument, and items 2 and 3 are findings that bear on whether
this ladder can deliver what §12.2 already says it does not.

> **`L-HONEST` (§6) is unaltered by this amendment, as it is by every other.** The family refines
> **2 of 3 directions**, `GCI_fine` is a **LOWER BOUND**, `p_s` is **NOT an observed order**, and
> **Sanaa's named first deliverable remains owed.**

**SUBMISSIONS REMAIN PARKED (rule 7). Nothing left the box (rule 8).**

### 15.10 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.0 → v1.1 (amendment 9, pre-compute). The frozen file was NOT edited; this section is
APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED.** Editing it would change
a line above this section and would falsify the assertion below, which other records depend on.
**The bump is recorded HERE, which is where rule 6 puts it** — *"a departure is disclosed in a
dated amendment appended at the foot, with a version bump"* — and a reader who reaches line 3
without reaching §15 has not read the document. **The supervisor may restate the version in the
header at the re-freeze, which is a status flip they own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines 1–2022 of this file are **byte-identical** to the same range at
commit `40f2d9b9` — both render to sha256
**`d4a485d2f52c55adbdd0e8103dd60fd13c1e0ec257362e6d76fd1e83039f72bb`**. Other records cite this
document **by line**, and at least one such citation sits inside an executable check, so this is a
guarantee and not a courtesy.

---

## 16. AMENDMENT 10 — 2026-09-04T1513Z. THE FOUR UNSATISFIABLE ITEMS ARE REGISTERED AS **PREDICTIONS**, AND SIX MORE ARE REPORTED

**Drafted by a cfd lab-lane on the cfd supervisor's instruction, under Sanaa's route ruling of
2026-09-04 ~15:00Z. THIS IS NOT A FREEZE AND NOT A RE-FREEZE.** The `SUPERVISION_CHARTER.md` §3
check 4 is the supervisor's, is not delegated, and is **undischarged as this section is written.**
**No compute was launched by the lane that wrote it, and no step of §2.4's cost table was run.**

> **`L-HONEST` (§6) IS CARRIED UNALTERED BY THIS AMENDMENT.** The family refines **2 of 3
> directions**, the wall-normal discretisation is **identical across levels**, `GCI_fine` is a
> **LOWER BOUND** on discretisation uncertainty, `p_s` is **NOT an observed order**, and **Sanaa's
> named first deliverable remains owed.**
>
> **THIS AMENDMENT MOVES NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Not one number in §2.4,
> §5, §5.1, §7 or §10 is touched. Sanaa's ruling of 2026-09-04 states in terms: *"Nothing in this
> order widens a gate or relabels a bound."* **That line is held here absolutely.**

### 16.0 THE AUTHORITY, AND WHAT IT DOES AND DOES NOT SETTLE

**Sanaa's words, verbatim, captured at `etc/sessions/2026-09-04T1500Z_sanaa_m6_route_ruling.md`
(commit `70d12a46`, 2026-09-04T15:00:46Z):**

> *"M6SR launches now on the committee family; the third-direction family builds in parallel as
> the standing capability. Both inside the $1,000 ladder envelope. First physics I want to see:
> M6 surface Cp at the AGARD span stations against tunnel data, with the family band."*

⚠ **THAT BLOCKQUOTE IS THE WHOLE OF HER ORDER.** The capture's *"Context (chief's reading)"*
section beneath it is **the chief's reading and is not her instruction**, and it is not relied on
here as authority. In particular, the reading's assertion that *"none of the four is in the
ill-posed (blocking) class"* is **the chief's classification, not hers**; this amendment reaches
the same place by a different route — **§7 is the only thing in this registration that blocks a
launch, and none of the ten items below is a §7 item.**

**HER RULING SETTLES THE ROUTE. IT DOES NOT REPEAL RULE 2.** Under her standing launch law of
2026-09-03 ~21:00Z (`etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md`), a non-ill-posed
unsatisfiable gate is **recorded as a prediction and judged by the frozen grader afterwards**,
rather than blocking the run. **That is the whole mechanism this section uses.** A prediction is
not a repair, and recording one confers nothing on the thing predicted.

### 16.1 THE CONDITION, AND HOW IT WAS CHECKED — RULE 2 REQUIRES BOTH

> **Rule 2's window is keyed to FIRST COMPUTE, not to the freeze flag:** *"Before first compute,
> amendments are legal and must state the condition and how it was checked (name the run directory
> that does not exist)."*

**THE RUN DIRECTORY THAT DOES NOT EXIST — NAMED, AS RULE 2 REQUIRES:**
**`verification/runs/M6SR_runs/`**, and with it `verification/runs/M6SR_runs/{L1,L2,L3}/`.

**How checked, at 2026-09-04T1503Z, in ONE invocation, WITH A LIVE PLANTED CONTROL (rule 3):**

| path | reader's answer | role |
|---|---|---|
| `verification/runs/M6SR_runs` | **ABSENT** | the run root — **the zero** |
| `verification/runs/M6SR_runs/L1` | **ABSENT** | the zero |
| `verification/runs/M6SR_runs/L2` | **ABSENT** | the zero |
| `verification/runs/M6SR_runs/L3` | **ABSENT** | the zero |
| `verification/runs/M6I_runs` | **PRESENT** | **the planted non-zero** |
| `verification/runs/RUNG1_M6_R2_runs` | **PRESENT** | **the planted non-zero** |
| `cases/M6SR` | **PRESENT** | the §9.1 grading path, which is **supposed** to exist (§15.1) |

**The same reader, in the same invocation, returned PRESENT on three paths and ABSENT on four.
The zero has a non-zero beside it.** Corroborated against the tree rather than the disk alone:
`git ls-tree -r --name-only HEAD -- verification/runs/M6SR_runs` returns **0 files**, while the
identical command on `verification/runs/M6I_runs` returns **14**. **`cases/M6SR` holds exactly the
two files §9's frozen path table names and nothing else** — no `0/`, no time directory, no
`log.*`, no `postProcessing`, no mesh. **This lane created no run root and launched nothing.**

### 16.2 THE FOUR §15.6 ITEMS, REGISTERED AS FALSIFIABLE PREDICTIONS

**Each states what the frozen grader is PREDICTED TO RETURN, and why. None is a repair. None
moves a gate.** Every measurement below was taken by this lane on the pinned artifacts, before any
compute, so none can have been chosen to fit an answer that does not exist.

---

#### PREDICTION `X1` — `D1` is INDETERMINATE, and Gate P's per-station channel returns **`NOT A RESULT`**

**Measured by this lane, independently of the comparator, by §4.3's own recipe on
`cases/dafoam/ladder-a/logs_A3/case_2308.dat` at the pinned sha256
`020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0` (hash re-verified in the
reading invocation):**

| section | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| taps | 34 | 34 | 34 | 34 | 45 | 45 | 45 |
| `Cn` | **0.239559** | **0.278490** | **0.294704** | **0.263810** | **0.222974** | **0.178438** | **0.210512** |

- `Cn` **strictly increasing: FALSE.** `Cn` **strictly decreasing: FALSE.**
- **`Cn(7)/Cn(1) = 0.878747`**, which lies **INSIDE** §4.3's registered indeterminate band
  `(0.75, 1.333)`. (`Cn(1)/Cn(7) = 1.137984`.)
- **PLANTED CONTROL (rule 3), fired in the same invocation:** `+1.000000` added to one tap's `CP`
  in section 1 moved that section's `Cn` by **`+0.100100`** and left the other six **unchanged to
  1e-15**. **The reader is shown able to see a non-zero, and to see it in the right place.**

> **REGISTERED PREDICTION `X1`: `D1` returns `INDETERMINATE`, and §4.3's own registered
> consequence therefore fires — Gate P's PER-STATION channel is `NOT A RESULT`.**

⚠ **THIS RECORDING LAUNDERS NOTHING, AND THE REASON IS STATED SO NO READER CAN MISTAKE IT.**
The per-station channel **is already `NOT A RESULT` by construction**, by the operation of §4.3's
own falsification table, on experimental bytes, **with no CFD in existence.** Registering the
prediction does not downgrade a result obtained later; **there is nothing to downgrade, and there
never will be, because the outcome is fixed by data that predate the ladder.** The prediction
exists so the record shows the outcome was known **before** 615 core-min were committed — not so
that a post-hoc `NOT A RESULT` can be presented as anticipated.

⚠ **AND A DISCREPANCY IN THE FIGURE THIS LANE WAS BRIEFED WITH, RECORDED RATHER THAN ADOPTED.**
The brief carried `Cn(7)/Cn(1) = 0.8785`. **This lane measures 0.878747 → 0.8787**, agreeing with
§15.6 item 2's filed `0.8787` and **not** with `0.8785`. Three recipe variants were tried to see
whether any defensible reading gives `0.8785` — closed-contour trapezoid **0.878747** (§4.3's
registered recipe), open trapezoid **0.907941**, sorted-by-`x/c` trapezoid **1.023332**. **None
reproduces 0.8785.** The registered figure is **0.878747**; the `0.8785` is a transcription slip
and is corrected here rather than propagated. **The verdict is unchanged either way — both sit
inside `(0.75, 1.333)`.**

---

#### PREDICTION `X2` — `GF4`'s semispan limb: **the instrument is REGISTERED, and it is the WALL-PATCH SPAN EXTENT**

**§5's `GF4` says *"semispan of each level's surface"* and does not say which semispan. §15.6 item
4 measured that the surface has two, straddling the ±0.1 % tolerance. RULE 2 REQUIRES THE
INSTRUMENT TO BE FIXED BEFORE THE RUN, SO IT IS FIXED HERE, WITH ITS REASON.**

**Measured by this lane on both existing levels, through the frozen comparator's own
`planform()` reader (`cases/M6SR/analyse_m6sr.py` at blob `97cbe039…`, §15.3) and independently
re-derived by a second reader written for this amendment:**

| level | surface faces | **wall-patch span extent** | vs AGARD 1.1963 m | **planform semispan (LE-line)** | vs AGARD 1.1963 m |
|---|---|---|---|---|---|
| **L3** `A3-onera-m6-adjoint-coarse` | 1,560 | **1.2164045761791 m** | **+1.6806 % — OUTSIDE ±0.1 %** | **1.1888852562842 m** | **−0.6198 % — OUTSIDE ±0.1 %** |
| **L2** `.mesh-cache/onera_m6` | 6,240 | **1.2164045761791 m** | **+1.6806 % — OUTSIDE ±0.1 %** | **1.1952992527948 m** | **−0.0837 % — INSIDE ±0.1 %** |

> ### **REGISTERED: `GF4`'s SEMISPAN LIMB IS MEASURED AS THE WALL-PATCH SPAN EXTENT.**
> **The planform semispan from the leading-edge line is REPORTED BESIDE IT, on every level, and
> gates nothing.**

**THE FIVE REASONS, EVERY ONE INDEPENDENT OF — AND FOUR OF THEM ADVERSE TO — THE ANSWER IT
PRODUCES:**

1. **It is the only limb that is a property of the SURFACE FAMILY rather than of a level's
   discretisation.** Measured: **1.2164045761791 m at BOTH levels — identical to thirteen
   significant figures** across surfaces that differ by **×4 in face count**. It is the tip cap's
   outermost node, inherited from the pinned master `197efa09…3327`, and coarsening cannot move it.
2. **The planform limb is discretisation-dependent and MOVES ACROSS THIS VERY FAMILY.**
   **1.188885 → 1.195299 m between L3 and L2 — a 0.540 % swing against a ±0.1 % band, 5.4× the
   tolerance width** — and it therefore returns **GATE FAIL on L3 and PASS on L2 for the same
   wing**. §5 grades `GF4` **per level**. A per-level gate whose instrument moves with the level's
   resolution grades the mesh, not the geometry.
3. **The new L1 has never been built, so the planform limb's value there is UNKNOWN**, and its
   direction (toward the true tip, as node density rises) is predictable while its magnitude is
   not. Registering an instrument whose reading on one of the three levels cannot even be bounded
   would be registering a gate whose outcome nobody can predict for a reason that has nothing to
   do with the wing.
4. **AGARD's 1.1963 m is the wing's physical span.** The wall-patch span extent is the same
   quantity measured on our surface. The **+1.6806 %** it reports is a **real geometry statement**
   — the ×4 family carries a **rounded tip cap** that extends 2.11 cm beyond AGARD's semispan —
   and that is exactly the class of finding `Gate GF` was created (§1.5) to surface.
5. 🔴 **DECISIVELY FOR RULE 2: THE REGISTERED INSTRUMENT PREDICTS `GATE FAIL`. THE ONE REFUSED
   WOULD HAVE PASSED ON L2.** A reason that selects the instrument which **fails** cannot be a
   reason chosen to fit an answer. Had this lane wanted a passing gate, the planform limb on L2
   was sitting there.

> **REGISTERED PREDICTION `X2`: `GF4`'s semispan limb returns `GATE FAIL` on all three levels
> (L3 and L2 measured at +1.6806 %; L1 predicted in family, since the tip cap is inherited from
> the pinned master and coarsening does not move it). `GF4`'s SWEEP limb is predicted `PASS` —
> measured `29.999984266°` (L3) and `29.999984251°` (L2), deviations `−1.573e-05°` and
> `−1.575e-05°`, both inside the registered `±0.01°`.**

**⚠ AND THE §14.2 RULING THIS REFUTES, STRUCK BY QUOTE AND NOT QUIETLY DROPPED.** §14.2's row on
§13 item 6 reads, verbatim:

> ~~*"✅ **ACCEPT — it self-closes at `B0`.** `GF4` measures semispan on each level's own surface
> against AGARD's printed **1.1963 m**, and the carried value differs by **0.039 %**, inside
> `GF4`'s **±0.1 %** band — **so the gate is not pre-decided by the choice.**"*~~

**STRUCK.** The reasoning is refuted by measurement in **two** places, and the second is new to
this amendment:

- **The choice of INSTRUMENT decides the verdict** (§15.6 item 4): +1.6806 % against −0.0837 %,
  on the same surface, against a ±0.1 % band. **The gate WAS pre-decided by the choice.**
- **AND THE CHOICE OF LEVEL DECIDES IT TOO.** Even holding the instrument fixed at the planform
  limb — the reading §14.2's `0.039 %` belongs to — the verdict is **PASS on L2 and GATE FAIL on
  L3.** §14.2's endorsement rested on a single number carried from another document
  (`b_semi = 1.19676 m`, §8.5) that was never measured on more than one level. **It is the
  supervisor's own ruling, it is this lane's own §13 item, and it is wrong.**

**Nothing about `§8.5`'s `b_semi = 1.19676 m` changes.** It is consumed only by the `sampleDict`
cutting-plane stations, gates nothing, and is not touched by this amendment.

---

#### PREDICTION `X3` — Gate G **REFUSES (exit 2)** for want of a registered `r`; and the refusal's own stated basis is **REFUTED BY MEASUREMENT**

**§5's `G3` consumes *"the three-level ratio"* and `G4` consumes *"`GCI_fine` … at `Fs = 1.25`"*.
**No section of this registration registers the refinement ratio `r`.** §15.6 item 1 records this
and states that the comparator refuses and prints all three candidates.

> **REGISTERED PREDICTION `X3`: on a family that reaches `CONVERGING` with `G1` and `G2` passed,
> the frozen comparator raises `Unregistered` and `--grade` exits **`2` (REFUSED)**, having
> emitted **nothing on stdout**. On any other family it returns `NOT A RESULT` under standing
> rule 5 clause (1) or (2), with the candidate triples printed.**

**THIS LANE DOES NOT REGISTER `r`, AND SAYS WHY RATHER THAN LEAVING IT IMPLICIT.** `r` is a **gate
parameter**; §15.9 already rules it is not for a lane to take; and — see below — **no registered
gate consumes it.** The choice remains entirely the supervisor's.

🔴 **AND TWO MEASURED FINDINGS THAT THE SUPERVISOR NEEDS BEFORE RULING ON IT. BOTH REFUTE
STATEMENTS THIS DOCUMENT AND ITS COMPARATOR ALREADY CARRY.**

**(a) `GCI_fine` IS `r`-INVARIANT. THE THREE CONVENTIONS GIVE THREE EXPONENTS AND *ONE* BAND.**
§15.6 item 1's basis reads *"Three defensible conventions exist and give three different bands"*,
and the comparator's own refusal text repeats *"three different `p_s` and three different
`GCI_fine`."* **Both are wrong, at the algebra.** The comparator fits `p_s` from the same triple
it then bands: `p_s = ln|d32/d21| / ln r`, so `r^{p_s} ≡ |d32/d21|` **identically**, and

```
    GCI_fine  =  Fs · |d21/f1| / (r^{p_s} − 1)  =  Fs · |d21/f1| / (|d32/d21| − 1)
```

**contains no `r` at all.** Measured by this lane through the comparator's own `roache_triple()`
on a non-2:1 converging triple `(f3, f2, f1) = (0.017, 0.0131, 0.01177)`:

| `r` | 1.10 | 1.5874 | 2.000 | 4.000 | 7.77 |
|---|---|---|---|---|---|
| `p_s` | 11.287332 | 2.328072 | 1.552048 | 0.776024 | 0.524710 |
| **`GCI_fine`** | **0.07309769942047496** | **0.07309769942047496** | **0.07309769942047496** | **0.07309769942047496** | 0.07309769942047498 |

**`p_s` moves by a factor of 21.5 across that range. `GCI_fine` is identical to fifteen
significant figures.**

> **THE CONSEQUENCE, STATED AND NOT ACTED ON.** Gate P's numerical band channel consumes
> **`GCI_fine`**, which the missing `r` **does not affect**. The only registered quantity `r`
> moves is **`G3`'s `p_s`** — on which §5 registers, in its own words, *"**NO acceptance band …
> because a band would assert it is an order of accuracy and §6 rules it is not**."* **So the
> unregistered `r` is load-bearing on nothing that is graded.** **This lane takes no action on
> that.** Acting on it means either registering `r` or changing the comparator, and **both are the
> supervisor's**, both after this document's freeze, and neither is a lane's to take. It is
> registered here so the supervisor rules on the true fact rather than on the filed one.

**(b) THE REFUSAL DOES NOT PRINT THE THREE CANDIDATES IT PROMISES. MEASURED.** §15.6 item 1 files
that the comparator *"REFUSES (exit 2) at Gate G, prints `p_s` and `GCI_fine` for **all three**
candidates."* **Measured by this lane, by driving the frozen `gate_g()` to its refusal on a
synthetic converging, plateaued triple: the `G3_G4_all_candidate_ratios` dict is built into a
local that the `raise` discards, `_emit()` is never reached, and STDOUT IS EMPTY.** The
exception's message names the three **conventions** (`r = 2.000, 1.5874, 4.000`) and carries **no
`p_s` value and no `GCI_fine` value**. **The filed row is WRONG AS FILED, not drifted** — the same
defect class §15.5 corrected in `PROVENANCE.md:190`, and it is recorded here by the same method:
**strike-and-quote, never rewriting.** ⚠ **The candidates ARE printed on the non-refusing paths**
(rule 5 clauses (1) and (2), where `gate_g()` returns rather than raises), which this lane
confirmed on a synthetic non-plateaued triple — so the claim is right for every family except the
one it was written for.

**No repair is made.** Repairing it edits the frozen §9.1 grading path (§16.5).

---

#### PREDICTION `X4` — `C12` cannot fire, and the control suite therefore **REFUSES (exit 2)**

**§10's `C12` plants a scratch reference whose seven sections are REVERSED and registers its
must-see as `FALSIFIED`.** Measured by this lane on the pinned bytes: the as-read `Cn` series is
**non-monotone** (`X1` above), and **reversing a non-monotone series leaves it non-monotone** —
as-read `INDETERMINATE`, reversed `INDETERMINATE`, reversed ratio `1.137984`, also inside
`(0.75, 1.333)`.

> **REGISTERED PREDICTION `X4`: `C12` DOES NOT FIRE. §10's own rule — *"A `PASS` reported by a
> reader whose plant did not fire is `NOT A RESULT`, not a pass"* — therefore applies, and the
> comparator's `--controls` / `--selftest` invocation REFUSES (exit 2).**

⚠ **`C12` IS NOT LOOSENED TO ITS PURPOSE CLAUSE, AND THIS IS THE WHOLE POINT OF REGISTERING IT.**
The tempting repair — reading `C12`'s intent (*"proving `D1` can return a verdict other than the
one `A-MAP` predicts"*) and satisfying it with a synthetic fixture — **is refused.** A registered
control is a registered control. The separate demonstration that **all three `D1` branches are
reachable on synthetic fixtures** already exists in the comparator as
`d1_branch_reachability()`, is printed under its own heading, and is **explicitly NOT a registered
control and never a substitute for `C12`.** **This is a FIXTURE LIMIT, not a one-answer
discriminator** — and the honest consequence of a fixture limit on a registered control is a
refusal, not a pass.

---

### 16.3 CARRIED FORWARD UNALTERED — `L-HONEST`, AND THE `c` DISCREPANCY

**`L-HONEST` (§6), quoted by reference and never paraphrased, and re-affirmed rather than merely
left alone:** the family refines **2 of 3 directions**; `s0 = 1.0e-4`, `N = 65` and
`marchDist = 12.0` are **identical at all three levels**, so `r_normal = 1.167442` and
`cells / wing_faces = 64` everywhere and **the wall-normal discretisation is IDENTICAL across the
family**; therefore **`GCI_fine` is a LOWER BOUND on total discretisation uncertainty and `p_s` is
NOT an observed order**; therefore **Sanaa's named first deliverable — M6 `Cp` WITH the family
band — is NOT delivered by this registration and REMAINS OWED.** **Every figure, table, plot, JSON
record and certificate cell derived from this family carries clause `L-HONEST` verbatim.**

**The `c` / planform-MAC discrepancy stays `REPORTED, NOT GATED`** exactly as Amendment 7
registers it: registered `c = 0.64607 m` against a planform MAC of `0.648267 m`, **+0.340 %**,
implying `Re = 11.7599 × 10⁶` w.r.t. the planform MAC against the registered `11.72 × 10⁶`. **It
travels onto the certificate beside the registered `Re`. It gates nothing. `μ∞ = 1.929120e-05` and
`omega_inf = 2210.901 1/s` are unchanged and the solve runs at the registered state pair.**

### 16.4 THE `A-MAP` STATION SET — A DISCLOSURE, `REPORTED, NOT GATED`

**§4's `A-MAP` registers `y/b = 0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99`, and the
comparator's `A_MAP_YB` constant carries the same seven values. Read at source by this lane** in
`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt`, **lines
13728–13729**, verbatim:

> *"271 pressure orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96 and 0.99)"*

> **REGISTERED DISCLOSURE:** AGARD AR-138 §5.1.1's printed sixth station is **`0.96`**. **NASA
> TMR's widely circulated M6 station set carries `0.95` at that position.** On a wing swept 30° at
> `M∞ = 0.8395`, a 1 % semispan error at the sixth station is **1.2 cm of span and ~0.7 cm of
> chordwise shock displacement**, so the divergence is **load-bearing on any `Cp` comparison** and
> is named here rather than discovered in a figure. **This registration uses `0.96`, which is what
> its own cited source prints.** ⚠ **This disclosure changes NO gate:** `A-MAP` was already
> registered as an **ASSUMPTION, not measured, not confirmed by any artifact this lab holds**
> (§4.1), the seven values were already fixed at the freeze, and Gate P's per-station channel is
> `NOT A RESULT` under `X1` regardless. **`REPORTED, NOT GATED`.**

**And the honest-labelling law that rides with every figure this ladder can produce, restated
because Sanaa's order names the figure:** the band M6SR itself can produce is the
**SURFACE-REFINEMENT sensitivity band, a LOWER BOUND on discretisation uncertainty** — **not** the
family band. **Every figure carrying it says so, verbatim, by clause `L-HONEST`.** The full family
band comes from the third-direction family when it lands.

### 16.5 🔴 SIX FURTHER ITEMS THAT CANNOT BE SATISFIED AS THIS DOCUMENT AND ITS GRADING PATH STAND

**Found by this lane on the supervisor's explicit instruction to assume a fifth exists. Recorded,
NOT repaired. Every one is a threshold-, instrument-, control- or grading-path question, and this
lane is not entitled to any of them. THEY ARE ON THE SUPERVISOR'S DESK.** Item **5** is
structural, is the most serious thing in this document, and **bears directly on Sanaa's named
deliverable**.

| # | what cannot be satisfied | measured basis | consequence |
|---|---|---|---|
| **5** | 🔴 **`Gate P` — registered in §5 as "SANAA'S DELIVERABLE" — HAS NO INVOCATION PATH IN THE FROZEN §9.1 GRADING PATH.** | **AST call-graph over `cases/M6SR/analyse_m6sr.py` at blob `97cbe039…`, with a planted control** (a function known to be called reads REACHABLE; a name that does not exist reads unreachable): **48 functions are reachable from `main()`. `gate_p()` is NOT. `set_to_set_assignment()` is NOT.** `gate_p` is defined at line 1338 and has **zero call sites** outside the module docstring; `set_to_set_assignment` is called **only from inside `gate_p`**. `--grade` computes `gate_g()` and `gate_r()` and returns 0. **There is additionally NO producer of `cfd_sections` anywhere** — no reader samples CFD `Cp` at the seven registered `y/b` stations, and the build driver writes no `sampleDict`. | **BOTH Gate P channels are dead — the per-station channel AND §4.5's order-independent channel.** `X1` kills the first on the data; **this kills both on the code.** **615.24 core-min of registered ladder cannot produce Sanaa's named first-physics figure at all**, and making it able to means **writing new grading code into a frozen grading path** — which rule 2 fixes at the pre-registration commit. **NOT a lane's call, and arguably not an addendum's.** |
| **6** | **§15.6 item 4's "planform semispan … inside the band" holds ON L2 ONLY.** | L3 **1.188885 m = −0.6198 % (OUTSIDE)**; L2 **1.195299 m = −0.0837 % (INSIDE)**. The two levels of one family differ by **0.540 %** on the same instrument, **5.4× the ±0.1 % tolerance**, because the instrument's reach is set by leading-edge **node density**. | **The natural repair to item 4 — adopt the planform limb — FAILS ANYWAY, on L3.** Handled by `X2`, which registers the wall-patch span extent for reasons that include this one. |
| **7** | **§15.6 item 1's basis and the comparator's refusal text both assert three different `GCI_fine`.** | Measured across `r ∈ {1.10, 1.5874, 2.000, 4.000, 7.77}`: **`GCI_fine` identical to 15 significant figures; `p_s` spans a factor of 21.5.** `r` cancels identically because `p_s` is fitted from the same triple. **And the refusal's promise that "all three are printed" is FALSE on the refusing path — measured, stdout is EMPTY.** | Recorded in `X3`. **Two filed statements are wrong as filed, not drifted.** The `r` question is smaller than the record says; the missing print is a real defect. |
| **8** | **`GF2` is registered as a GEOMETRY-FIDELITY gate but measures SURFACE RESOLUTION, and its single threshold is applied per level to a family whose purpose is to vary resolution.** | Measured through the frozen readers against the pinned Table B1-1 (`66b2a7bc…4ab7`, 72 points, final ordinate `0.0007052`): **L3 max │Δz│/c = 3.4265e-03 at `x/c = 0.0018364` → OUTSIDE the ≤1.0e-03 threshold; L2 = 9.9259e-04 at `x/c = 0.0012868` → INSIDE, at 0.99× the threshold.** Both maxima sit **at the leading edge**, where a ×4-coarser surface simply has fewer points to resolve LE curvature; the two levels differ by **3.45×**. | **The coarsest level of ANY converging surface family must fail `GF2` as registered**, and the failure says nothing about whether the wing is the right wing. L2 passes by **1 %**. **Predicted: `GF2` → `GATE FAIL` on the family** (the comparator requires every level ≤ threshold), driven by L3's resolution, not by geometry. |
| **9** | **§2.4 registers *"`B0` runs FIRST"*, and `gate_gf()` cannot run first.** | `gate_gf()` grades **all three levels in one call**; `_discover_levels()` sets L1's mesh to `<run_root>/L1/constant/polyMesh`, which does not exist until **`B3`** completes; `read_boundary()` on an absent mesh **raises `Refusal` → exit 2**. There is no per-level or two-level mode. | **`B0` can only run AFTER `B1`–`B3`.** §2.4's stated purpose — *"so that the finding exists before the spend, not after"* — is **98.8 % preserved** (`B1`–`B3` are 7.38 of 615.24 core-min; `B5` is 607.63) but **the registered ORDER is not satisfiable.** Reported, not repaired. |
| **10** | **NO REGISTERED ARTIFACT RUNS `B5a`, `B5b` OR `B5c` — 607.63 of 615.24 core-min, 98.8 % of the ladder — AND NONE OF §8's CASE FILES EXISTS.** | §9's frozen path table registers exactly two executables. `build_m6sr_l1.sh` (blob `04ae9d58…`) covers **`B1`, `B2`, `B3` only**; its own closing line reads *"NEXT: B4 is Gate A and B0 is Gate GF … THIS DRIVER GRADES NOTHING."* **Nothing anywhere writes §8.1's seven `0/` fields, §8.2's `fvSchemes`, §8.3's `fvSolution`, §8.4's `constant/`, §8.5's `controlDict` / `decomposeParDict` / `sampleDict`, or launches `rhoSimpleFoam`.** §8's own opening concedes *"Measured: no runnable case exists at any M6 level in any tree on this box."* | **A queue row cannot be written today: its `launch_cmd` has no target for `B5`.** ⚠ **This is NOT necessarily a rule-2 violation** — §8's case files are solver **INPUTS**, not graders, and rule 2 fixes the **grading** path; writing them pre-compute is legal. **It is a LAUNCH-READINESS fact**, and it is stated so the supervisor learns it before ordering a launch rather than at the drop path. |

> **WHAT M6SR CAN AND CANNOT DO TODAY, STATED ONCE, PLAINLY.**
> **CAN:** run `B1`–`B3` (**7.38 core-min estimated**, caps 1.0 / 70.0 / 3.0) through the
> registered driver; then grade **`Gate GF`** (`B0`) and **`Gate A`** (`B4`) through the
> registered comparator.
> **CANNOT:** run `B5` — no launcher, no case files (item 10). **CANNOT:** grade `Gate P` in any
> channel — no invocation path, no `Cp` sampler (item 5).
> **`Gate G` will REFUSE (exit 2) on a converging family** (`X3`), and the control suite will
> **REFUSE (exit 2)** on `C12` (`X4`).
> **None of these is a §7 ill-posedness item, so under Sanaa's launch law none of them BLOCKS.
> They are recorded as predictions and the frozen grader judges after. But a run that cannot
> reach 98.8 % of its own cost table is a launch-readiness question, not a prediction, and it is
> the supervisor's.**

### 16.6 COST — RULE 12, AND NONE OF IT IS LADDER COMPUTE

**No step of §2.4's cost table was run. `B0`–`B6` remain unspent and `verification/runs/M6SR_runs`
does not exist.** What this amendment spent is **read-only measurement on already-existing
artifacts** — the `case_2308.dat` `Cn` series and its planted control, the two levels' polyMesh
surfaces through the frozen readers, an AST call-graph, and two synthetic `gate_g()` probes:
**≈ 6 core-min at 1 rank, and it is an ESTIMATE from this session's own wall clock, NOT a
measurement read from a run log** — no run log exists for it and inventing one would be worse than
saying so. **Derived at the owner-stated `c7a.4xlarge` $0.0513/core-h: ≈ $0.0051 — DERIVED,
REPORTED-BY-OWNER, never measured, because the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5).

**§9.3's estimate-versus-actual row is NOT owed yet**, because no `B` step has completed. It falls
due at `B1`'s completion and the driver already emits it into `BUILD_RESULT.json`.

**`est ≤ cap` RE-VERIFIED ON EVERY ROW OF §2.4's COST TABLE, AT THE SUPERVISOR'S STANDING RULING
THAT A ROW WHOSE ESTIMATE EXCEEDS ITS OWN CAP MAY NOT LAUNCH. Re-derived here, not assumed:**

| row | est (core-min) | cap (core-min) | est/cap | |
|---|---|---|---|---|
| `B0` | 0.1000 | 1.0 | 0.1000 | OK |
| `B1` | 0.0500 | 1.0 | 0.0500 | OK |
| `B2` | 7.0400 | 70.0 | 0.1006 | OK |
| `B3` | 0.2900 | 3.0 | 0.0967 | OK |
| `B4` | 0.1400 | 2.0 | 0.0700 | OK |
| `B5a` | 10.1837 | 31.0 | 0.3285 | OK |
| **`B5b`** | **54.3130** | **163.0** | **0.3332** | **OK — the LARGEST ratio** |
| `B5c` | 543.1296 | 1630.0 | 0.3332 | OK |
| `B6` | 0.0000 | 2.0 | 0.0000 | OK |
| **TOTAL** | **615.24** | **1,903.0** | **0.3233** | **NO ROW EXCEEDS ITS OWN CAP** |

**`B5b` at 0.33321 is the largest ratio, by a hair over `B5c`'s 0.33321 at the fourth decimal
(54.3130/163 = 0.3332086; 543.1296/1630 = 0.3332083).** ⚠ **A bookkeeping note, recorded so
nobody "discovers" it later:** summing the table's **printed** cells gives **615.24** (Amendment
3's figure, and §9.3's calibration denominator); summing the **unrounded** solve figures gives
**615.2463**. The difference is **0.0004 %** and is immaterial, but the denominator §9.3 divides by
is **615.24**, the sum of the printed cells, exactly as Amendment 3 registers it.

**Sanaa's envelope.** At the recorded $0.0513/core-h the **$1,000 ladder envelope is 1,169,591
core-min**; this registration's **cap of 1,903.0 core-min is 0.1627 % of it**, and its estimate
615.24 is **0.0526 %**. **Derived $1.6271 at cap, $0.5260 at estimate — DERIVED, NOT MEASURED.**
Her order requires this ladder inside that envelope; **an envelope-ledger row is owed at launch**
to `docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md`, per §9.3.

### 16.7 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** Not one number in §2.4, §5, §5.1, §7
   or §10 is touched. `X2` **fixes an instrument the frozen text left ambiguous**; it does not
   move `GF4`'s registered `±0.1 %` band, its `±0.01°` sweep band, or its 0.1 core-min cap.
2. **It does NOT register `r`**, and it takes no position on which convention is right.
3. **It does NOT repair the comparator or the driver.** Not `gate_p`'s missing invocation, not the
   discarded candidate print, not `C12`, not `B0`'s ordering. **Any change to a script that
   produces or grades a measured number goes to the supervisor as a DIFF, and this lane made
   none** — `cases/M6SR/analyse_m6sr.py` and `cases/M6SR/build_m6sr_l1.sh` are **byte-unchanged**
   at the blob shas §15.3 pins.
4. **It does NOT loosen `C12` to its purpose clause**, and it does not substitute
   `d1_branch_reachability()` for it.
5. **It does NOT claim `A-MAP` is confirmed**, and it does not adjudicate `0.96` against `0.95`
   beyond recording that this registration uses what its own cited source prints.
6. **It does NOT re-freeze.** `SUPERVISION_CHARTER.md` §3 check 4 belongs to the cfd supervisor
   and is **undischarged**.
7. **It does NOT enqueue anything.** `verification/queue/cfd/` is a **live launch path** — the
   daemon was verified running (pid in `verification/queue/runner.pid`, 60 s tick) at the time of
   writing — and **this lane wrote nothing into it.**
8. **It changes nothing in `/home/ubuntu/certonomous-runs/`**, which was read only.
9. **It claims no verdict of the fixed vocabulary for any gate of this registration.** Every
   `PASS` / `GATE FAIL` / `NOT A RESULT` word above is inside a **registered PREDICTION**, and a
   prediction is not a verdict.
10. **SUBMISSIONS REMAIN PARKED (rule 7). Nothing left the box (rule 8).**

### 16.8 WHAT HAPPENS NEXT, AND WHO MAY DO IT

**The re-freeze is `SUPERVISION_CHARTER.md` §3 check 4 and it belongs to the cfd supervisor.**
This lane did not re-freeze, launched no compute, wrote nothing into the queue, and changed no
script that produces or grades a measured number.

**The four §15.6 items are now registered as predictions `X1`–`X4` and are, in this lane's
reading, launch-compatible under Sanaa's launch law.** **Items 5 through 10 of §16.5 are not
predictions and are not for a lane:** items 5 and 10 are **launch-readiness facts** about
executables that do not exist, item 8 is a **gate-design** question, item 9 is an **ordering**
question, and items 6 and 7 are **corrections to filed statements** in §15.6 and in the
comparator's own text.

> **`L-HONEST` (§6) is unaltered by this amendment, as it is by every other.** The family refines
> **2 of 3 directions**, `GCI_fine` is a **LOWER BOUND**, `p_s` is **NOT an observed order**, and
> **Sanaa's named first deliverable remains owed** — and item 5 establishes that, as the grading
> path stands, **this ladder has no code path by which to deliver it even in its lower-bound
> form.**

### 16.9 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.1 → v1.2 (amendment 10, pre-compute). The frozen file was NOT edited; this section
is APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10
gives: editing it would change a line above §15 and falsify that section's own assertion, on which
other records depend. **The bump is recorded HERE, which is where rule 6 puts it.** **The
supervisor may restate the version in the header at the re-freeze, which is a status flip they
own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–2229** of this file — the whole of it up to and including
§15.10's closing line, and therefore the whole of §15's own guaranteed range 1–2022 — are
**byte-identical** before and after this append, both rendering to sha256
**`c8b28d88ced04f6238e50c4f7b9f36e4ff98d8e728d6ebd23535fd883a4ddc6b`**. Other records cite this
document **by line**, and at least one such citation sits inside an executable check, so this is a
guarantee and not a courtesy.

---

## 17. AMENDMENT 11 — 2026-09-04T1613Z. THE SUPERVISOR'S FOUR RULINGS ARE IMPLEMENTED, AND A FIFTEENTH PASS FINDS THREE MORE

**Drafted and applied by a cfd lab-lane on the cfd supervisor's four explicit rulings of
2026-09-04. THIS IS NOT A FREEZE AND NOT A RE-FREEZE.** `SUPERVISION_CHARTER.md` §3 check 4 is
the supervisor's, is not delegated, and is **undischarged as this section is written.** **No
compute was launched by the lane that wrote it, no step of §2.4's cost table was run, and no
queue row was written.**

> **THE DIVISION OF LABOUR, STATED SO NO READER MISTAKES IT.** The four rulings below are the
> **supervisor's**, taken on the fourteen items §17 of the working draft
> (`verification/campaign/M6SR_AMENDMENT_11_DRAFT.md`) recorded. **This lane implemented them
> and did not re-decide any of them.** Where implementing a ruling forced a choice the ruling
> did not settle, the choice is **named as such, quantified, and handed back** — it is not
> taken silently (§17.3.3, §17.9 item 26).
>
> **`L-HONEST` (§6) IS CARRIED UNALTERED.** The family refines **2 of 3 directions**, the
> wall-normal discretisation is **identical across levels**, `GCI_fine` is a **LOWER BOUND**,
> `p_s` is **NOT an observed order**, and **Sanaa's named first deliverable remains owed.**
>
> **THIS AMENDMENT MOVES NO GATE, NO THRESHOLD, NO CAP AND NO LABEL** — with the two
> exceptions the supervisor's rulings expressly authorise, each of which states its reason and
> its predicted consequence: **Ruling 1 registers a DIVERGENCE SCHEME** (§17.2) and **Ruling 2
> registers the STATION REFERENCE SEMISPAN** (§17.3). Not one number in §2.4, §5, §5.1, §7 or
> §10 is touched, and `X1`–`X4` stand exactly as Amendment 10 registered them.

### 17.1 THE CONDITION, AND HOW IT WAS CHECKED — RULE 2 REQUIRES BOTH

> **Rule 2's window is keyed to FIRST COMPUTE:** *"Before first compute, amendments are legal
> and must state the condition and how it was checked (name the run directory that does not
> exist)."*

**THE RUN DIRECTORY THAT DOES NOT EXIST — NAMED, AS RULE 2 REQUIRES:**
**`verification/runs/M6SR_runs/`**, and with it `verification/runs/M6SR_runs/{L1,L2,L3}/`.

**How checked, at 2026-09-04T1613Z, WITH A LIVE PLANTED CONTROL (rule 3), on the DISK and then
corroborated against the tree:**

| path | reader's answer | role |
|---|---|---|
| `verification/runs/M6SR_runs` | **ABSENT** | the run root — **the zero** |
| `verification/runs/M6I_runs` | **PRESENT** | **the planted non-zero** |
| `cases/M6SR` | **PRESENT** | the §9.1 grading path, which is **supposed** to exist |

`git ls-tree -r --name-only HEAD -- verification/runs/M6SR_runs` returns **0 files**; the
identical command on `verification/runs/M6I_runs` returns **14**. **The same reader, in the
same act, returned PRESENT beside the zero.** A bare "absent" would not have been evidence.

**Independently: §8's case files and the `B5` launcher are solver INPUTS, not graders.** Rule 2
fixes the **grading** path at the pre-registration commit; Amendment 10 item 10 already records
in terms that writing case inputs pre-compute is legal.

### 17.2 RULING 1 — `div(phi,Ekp)` IS REGISTERED, AND §8.2's SMOOTHNESS JUSTIFICATION IS **STRUCK BY QUOTE**

**THE RULING, THE SUPERVISOR'S:** *"Register `div(phi,Ekp)`, and change the REASON, not just
the name … A scheme carried across with a reason that belongs to a different quantity is
exactly the 'silent no-op' family this team convicted twice."*

**THE MEASUREMENT, RE-VERIFIED BY THIS LANE INSIDE THE CONTAINER THAT WILL RUN THE SOLVE**, not
taken from the draft and not from the box's native tree:
`OpenFOAM-v2506/applications/solvers/compressible/rhoSimpleFoam/EEqn.H` reads

```
    fvm::div(phi, he)
  + ( he.name() == "e" ? fvc::div(phi, volScalarField("Ekp", 0.5*magSqr(U) + p/rho))
                       : fvc::div(phi, volScalarField("K",   0.5*magSqr(U))) )
```

§8.4 registers **`sensibleInternalEnergy`**, so `he.name() == "e"` and the solver requests
**`div(phi,Ekp)`** and **never** `div(phi,K)`. Under §8.2's `default none;` — which §8.2 itself
says *"makes an unruled term a hard solver abort rather than a silent default"* — **the frozen
`fvSchemes` cannot start the solver.**

> ### **REGISTERED, AMENDMENT 11 RULING 1:**
> ```
>     div(phi,Ekp)   bounded Gauss upwind;
> ```

**⚠ THE SCHEME IS NOT CARRIED ACROSS FROM `div(phi,K)`, AND THE JUSTIFICATION THAT WOULD HAVE
COME WITH IT IS STRUCK BY QUOTE.** §8.2's third bullet reads, verbatim:

> ~~*"**`div(phi,K)` — `bounded Gauss linear`.** `K = |U|²/2` is a **smooth, non-shock-bearing**
> kinematic quantity reconstructed from `U`; upwinding it would add dissipation to the energy
> balance that the momentum equation is not seeing, which is inconsistent. Second-order
> linear."*~~

**STRUCK, AS A JUSTIFICATION FOR THE TERM THE SOLVER ACTUALLY REQUESTS.** `Ekp = |U|²/2 + p/ρ`,
and **the `p/ρ` part jumps across the shock** — it is, up to normalisation, the very quantity
Gate P grades. **A smoothness argument about `K` is not an argument about `Ekp`.** The bullet
stands unaltered **as a ruling about `div(phi,K)`**, which remains written in the dictionary and
is **never requested** under `sensibleInternalEnergy`; it would govern only the counterfactual
`sensibleEnthalpy` configuration this registration does not use.

**THE REASON REGISTERED FOR `bounded Gauss upwind`, STATED IN TERMS OF `Ekp`, IN THREE MEASURED
LIMBS:**

1. **It is the other half of ONE flux.** `div(phi,he) + div(phi,Ekp) = div(phi,h₀)`: with
   `he = e`, `e + p/ρ = h` and `h + |U|²/2 = h₀`. §8.2 already ruled **`bounded Gauss upwind`**
   for `div(phi,e)` on the ground that it is *"internal energy transport across a **transonic
   shock**"*. **Two different schemes on the two halves of one total-enthalpy flux is
   inconsistent**, and the inconsistency is not cosmetic: it is a mismatch in the numerical
   dissipation applied to the two additive parts of the same physical transport.
2. **`Ekp` enters EXPLICITLY.** Measured in `EEqn.H` above: `he` is `fvm::` (implicit) and `Ekp`
   is `fvc::` (explicit). An unbounded second-order reconstruction of a shock-bearing quantity
   in an **explicit source** feeds an unbounded contribution into the implicit `he` equation —
   **the negative-temperature-and-solver-death route §8.2 already names for `div(phi,e)`**, and
   it applies with more force to a term that carries no implicit diagonal to damp it.
3. **The shipped v2506 tree never splits them, and its only transonic case uses exactly this
   scheme.** Measured across the 17 `fvSchemes` in the v2506 tutorial tree carrying
   `div(phi,Ekp)`: of the **8** under a **steady compressible** solver family (`rhoSimpleFoam`,
   `rhoPorousSimpleFoam`, `overRhoSimpleFoam`) that carry a `div(phi,e)` entry too, **8 of 8
   give `e` and `Ekp` the IDENTICAL scheme and none splits them.** The only case in the tree
   that differs is the low-Mach buoyant family (`buoyantPimpleFoam`, `Gauss linear` on `Ekp`) —
   **no shock.** And **`tutorials/compressible/rhoSimpleFoam/squareBend`, the one tutorial in
   the family carrying `transonic yes;`, uses `bounded Gauss upwind` for both.**

**⚠ THE PREDICTED CONSEQUENCE, REGISTERED AND NOT HIDDEN.** Relative to a second-order
reconstruction, a bounded first-order upwind on the explicit `Ekp` term adds **numerical
dissipation to the total-energy flux**. Gate P grades **surface `Cp`**, which is set by the
momentum solution; the same reasoning §8.2 gives for accepting first order on `div(phi,e)`
applies here. ⚠ **The magnitude of any resulting `Cp` bias is NOT estimated.** Naming a
numerical choice is honest; inventing the size of its effect would not be — the same discipline
§5's `GF1` ruling already imposes.

> **REGISTERED PREDICTION `X5`: with `div(phi,Ekp)` registered, `rhoSimpleFoam` does not abort
> at iteration zero on an unruled divergence term. With §8.2's frozen `fvSchemes` as written —
> `default none;` and no `div(phi,Ekp)` entry — it does.** ⚠ **This is a PREDICTION, not a
> measurement: no solver has been launched under either dictionary. The abort mechanism is
> §8.2's own stated one, and the term the solver requests is measured from `EEqn.H`; the abort
> itself is an inference and is labelled one.**

**Implemented in `cases/M6SR/write_m6sr_case.py` as CHOICE `CH2`, whose recorded basis now
carries this reason and not the struck one.** Verified by emitting the dictionary and reading
it back: the written `system/fvSchemes` carries `div(phi,Ekp)  bounded Gauss upwind;`.

### 17.3 RULING 2 — **ONE** REFERENCE SEMISPAN FOR THE STATIONS, WITH ITS SOURCE, AND THE SHIFT AS A PREDICTION

**THE RULING, THE SUPERVISOR'S:** *"three semispans in one document is itself the defect.
Register ONE, with its source, and register the shift as a PREDICTION … the stations are
defined by the EXPERIMENT — AGARD's taps sit at `y/b` of the REAL wing — so the reference
semispan is the AGARD/experimental one, and the mesh's 1.216405 m is a MESH property to be
REPORTED, not one that redefines where the stations are."*

#### 17.3.1 THE THREE SEMISPANS, AND WHAT EACH ONE IS

| value | where it lives | what it actually is |
|---|---|---|
| **1.19676 m** | **§8.5**, `sampleDict` cutting planes; comparator constant `B_SEMI_M` | the **station reference** — the semispan the seven `y/b` are multiplied by |
| **1.1963 m** | **§5, `GF4`** | **AGARD's printed physical semispan**, a **gate reference** for `GF4` |
| **1.2164045761791 m** | **`X2`**, measured on both levels' wall patch | the **solved wing's** span extent — a **MESH property** |

**Re-measured by this lane: `1.216405 m` on L3 and on L2, identical.** §8.5's `1.19676` is
**+0.038452 %** from AGARD's `1.1963` and **−1.614971 %** from the wing this ladder will solve.

#### 17.3.2 THE REGISTRATION — ONE VALUE, WITH ITS SOURCE AND ITS REASON

> ### **REGISTERED, AMENDMENT 11 RULING 2: the STATION REFERENCE SEMISPAN is `b_semi = 1.19676 m`, and it is the EXPERIMENTAL/AGARD-side reading, not the solved wing's.**
> **Source, as §8.5 states it: measured independently from the registered STL master, and
> corroborated to `+0.038452 %` against AGARD AR-138's printed `1.1963 m` — the one import
> corroborated on this box.** **The value is UNCHANGED from §8.5. What changes is that it is
> now REGISTERED AS A CHOICE, with its reason, rather than carried as an unexamined constant.**
>
> **THE REASON.** AGARD's taps are at `y/b` of the **REAL** wing: `y/b` is an experimental
> coordinate and the seven values `0.20 … 0.99` mean nothing except against the wing the taps
> were drilled into. **The solved wing's `1.216405 m` is a property of OUR MESH** — `X2`
> reason 4 measures the ×4 family's inherited **rounded tip cap** extending **0.020105 m**
> beyond AGARD's semispan — **and a mesh artefact may not redefine where an experimental
> station is.** `1.216405 m` is therefore **REPORTED** — it is `GF4`'s registered instrument
> and it rides in every `GATE_P_FIGURE_DATA.json` under `sampled_span_extent_m` — and it
> **does not place a station.**

**⚠ AND WHAT THIS REGISTRATION DOES NOT SETTLE, HANDED BACK RATHER THAN TAKEN.** The ruling
names *"the AGARD/experimental one"*, and **the document holds TWO values on that side**:
§8.5's STL-measured `1.19676 m` and `GF4`'s AGARD-printed `1.1963 m`. **This lane registers the
one already in force (`1.19676`) and did NOT move the number**, because moving it moves every
station and that is a gate parameter. **The alternative is quantified so the supervisor rules
on a measured thing:** adopting AGARD's printed `1.1963 m` instead would move station 7 inboard
by **0.0004554 m = 0.03805 % of semispan ≈ 0.027 cm** of chordwise shock displacement at
§16.4's rate — **an order of magnitude below the 0.96-vs-0.95 divergence §16.4 already calls
load-bearing**, and every station stays inside the wall patch. **It is the supervisor's, and it
is small.**

#### 17.3.3 THE SHIFT, REGISTERED AS A FALSIFIABLE PREDICTION WITH ITS MAGNITUDE

**Every station of the registered set sits INBOARD of the same nominal `y/b` on the solved
wing, by ~1.6 % of semispan. Re-derived by this lane:**

| station | `y/b` | registered span coord (m) | its `y/b` **of the solved wing** | if placed at `y/b` of the solved wing (m) | shift (m) | shift, % of `b_semi` |
|---|---|---|---|---|---|---|
| 1 | 0.20 | 0.2393520 | **0.196770** | 0.2432809 | 0.0039289 | 0.32830 |
| 2 | 0.44 | 0.5265744 | 0.432894 | 0.5352180 | 0.0086436 | 0.72225 |
| 3 | 0.65 | 0.7778940 | 0.639503 | 0.7906630 | 0.0127690 | 1.06696 |
| 4 | 0.80 | 0.9574080 | 0.787080 | 0.9731237 | 0.0157157 | 1.31318 |
| 5 | 0.90 | 1.0770840 | 0.885465 | 1.0947641 | 0.0176801 | 1.47733 |
| 6 | 0.96 | 1.1488896 | **0.944496** | 1.1677484 | 0.0188588 | 1.57582 |
| 7 | 0.99 | 1.1847924 | **0.974012** | 1.2042405 | **0.0194481** | **1.62507** |

> **REGISTERED PREDICTION `X6`: the seven graded stations are placed at `y/b` of the
> EXPERIMENTAL semispan, so on the SOLVED wing they sit at `y/b` = 0.196770, 0.432894,
> 0.639503, 0.787080, 0.885465, 0.944496 and 0.974012 — each ~1.6 % of semispan INBOARD of its
> nominal ring. Placing station 7 at 0.99 of the SOLVED wing instead would move it
> `0.0194481 m` outboard = `1.62507 %` of semispan ≈ `1.14 cm` of chordwise shock displacement
> at §16.4's own exchange rate (1 % of semispan ≈ 0.7 cm at `M∞ = 0.8395` on a 30°-swept
> wing).**
>
> **THAT IS LARGER THAN THE `0.96`-vs-`0.95` DIVERGENCE §16.4 ALREADY REGISTERS AS
> LOAD-BEARING (≈ 0.7 cm), AND IT POINTS THE SAME WAY — inboard-versus-outboard on the same
> stations.** **It is `REPORTED, NOT GATED`**, exactly as §16.4's is, and it travels on every
> Gate P figure and certificate cell.

**⚠ BOTH READINGS ARE DEFENSIBLE, AND WHICH ONE THIS REGISTRATION USES IS STATED SO NO READER
HAS TO INFER IT.** *Experimental-referenced* (registered here) matches the physical coordinate
the taps were drilled at and is right for the inboard stations. *Solved-wing-referenced* would
match the aerodynamic place — the outer stations of a wing with a rounded tip cap are not the
outer stations of AGARD's wing. **This registration uses the EXPERIMENTAL reference, for the
reason in §17.3.2, and predicts the size of what it thereby gives up in `X6`.**

**✅ AND SO THAT NOBODY READS THE RULING AS A SAFETY CLAIM: all seven registered stations fall
INSIDE both meshes' wall-patch extent `[0, 1.216405] m`** — station 7 clears the tip by
**0.031612 m** — **so the comparator will not refuse on span.** That is a statement about the
reader's refusal condition (`C22`), **not** a statement that the stations are in the right
place; `X6` is the statement about that, and it is a disclosure of a **1.6 %** displacement.

**Nothing in the comparator changes for this ruling.** `B_SEMI_M = 1.19676` is byte-unchanged.

### 17.4 RULING 3 — SANAA'S FIGURE IS **SPLIT** INTO UPPER AND LOWER CURVES

**THE RULING, THE SUPERVISOR'S:** *"her figure cannot be plotted from an interleaved curve.
Split it … a `Cp` vs `x/c` figure REQUIRES upper and lower as SEPARATE curves. Sanaa's named
deliverable is the figure. This is a comparator change: hand me the DIFF, check 1 is mine."*

**THE DEFECT, AS MEASURED (draft item 21):** §4.5's channel builds **both** curves as
`sorted((x, cp))` and interpolates with `_interp()`, which is **single-valued in `x`**. At any
`x/c` a wing section carries **two** `Cp` values.

**AND A MEASUREMENT THIS LANE ADDS, WHICH SHARPENS THE ITEM RATHER THAN REPEATING IT.** The
draft recorded the interleaving as *"symmetric between experiment and CFD so not a bias."* That
is true of the **comparison**. It is **not** true of the **curve**: measured on the pinned
`case_2308.dat`, the taps are **not evenly split between the surfaces** —

| sections | upper taps | lower taps |
|---|---|---|
| 1–4 | **23** each | **11** each |
| 5–7 | **31** each | **14** each |
| **total** | **185** | **86** |

**185 of 271 taps — 68.27 % — are upper-surface taps**, so an interleaved curve is implicitly
weighted about **2:1 toward the upper surface**. (185 + 86 = 271, AR-138 §5.1.1's own total.)
**Reported. §4.5's RMS is a graded channel and this amendment does not touch it.**

#### THE CHANGE, AND EXACTLY WHAT IT DOES AND DOES NOT TOUCH

**The DIFF is filed at `cases/M6SR/AMENDMENT_11_RULING_3_FIGURE_SPLIT.diff`** and is to be read
as a diff. **`SUPERVISION_CHARTER.md` §3 check 1 is the supervisor's and is not delegated.**
121 insertions, 5 deletions, in `cases/M6SR/analyse_m6sr.py`:

- **NEW `split_curve_upper_lower(rows)`** — rows are `(x_over_c, thickness_coord, value)`;
  returns sorted `upper` and `lower` curves and their counts. **Convention: `thickness >= 0` is
  UPPER — the SAME convention the frozen `section_upper_lower()` already uses for `GF2`'s root
  section.** There is one reader in this repository for what "upper" means and this is not a
  second one. A point at exactly zero thickness lands in UPPER **deterministically**, and the
  count of such points is **REPORTED, not hidden** (measured: section 4 of `case_2308.dat`
  carries exactly one). **It REFUSES if either side carries fewer than 2 points**, because a
  one-sided section would **plot as a perfect absence of the missing surface rather than as a
  disagreement** — the false zero rule 3 exists for, and the same reason `C22` refuses an
  out-of-span station rather than returning an empty curve.
- **`cfd_sections_from_surface()`** — derives the thickness axis as the remaining one of the
  three (never assumed; draft item 20 records that §8.5's "constant-`y`" names the wrong axis)
  and builds the split **from the SAME `cross` list**, so there is one source of truth for what
  a station's points are and no second cut. It rides in `meta["split_by_station"]`, **so the
  `(sections, meta)` tuple §4.5's `set_to_set_assignment()` consumes is SHAPE-UNCHANGED.**
- **`gate_p_figure_data()`** — the experimental record now carries
  `curve_upper_x_over_c_Cp` / `curve_lower_x_over_c_Cp` with their counts; the interleaved list
  is retained under the name **`curve_x_over_c_Cp_INTERLEAVED_NOT_PLOTTABLE`** so the two
  readings can be compared and nobody plots the wrong one; and `cfd_split_by_level` carries the
  CFD side. A `FIGURE_CURVES` note states the 185/86 asymmetry in the record itself.
- **NEW PLANTED CONTROL `C24`** (rule 3, on the two curves the figure is plotted from), added
  to the `--selftest` mutation loop; and `split_curve_upper_lower` added to `C23`'s
  must-be-reachable set.

> 🔴 **§4.5's GRADED CHANNEL IS BYTE-UNCHANGED. `set_to_set_assignment()` STILL INTERLEAVES.**
> The supervisor's ruling names **the figure**. §4.5's RMS matrix is a **graded** channel whose
> force is one-directional under standing rule 5, and **changing what a graded channel measures
> is a gate question and is not a lane's.** It is recorded here that the RMS is computed on
> interleaved curves weighted ~2:1 to the upper surface, **and it is left exactly as frozen.**

#### `C24` — THE CONTROL, AND WHY IT DISCRIMINATES RATHER THAN MERELY PASSING

**Planted on the PINNED experimental bytes, not on a fixture:** `+0.3579` in `Cp` on the
**upper-surface taps of section 1 only** (23 upper, 11 lower of 34).

| limb | measured |
|---|---|
| upper curve moves by exactly the plant | worst deviation **0.0** |
| lower curve does not move at all | **0.0** |
| counts preserved (`n_upper + n_lower == n_taps`) | **23 + 11 = 34** |
| **the SAME plant read through the INTERLEAVED curve** | shifts its mean by **0.2421088235294118**, only **0.6765** of the plant |

**A one-sided plant is the point.** A reader that still interleaved would report the smeared
`0.242…` rather than the planted `0.3579`, so **this control discriminates the very defect item
21 named** instead of merely proving arithmetic works.

**Measured on the suite as a whole:** `C24` **FIRES**; its targeted mutation **FLIPS EXACTLY
`C24` TO RED** and nothing else; every other mutation still flips exactly its own control;
`--controls` returns **rc 2** under `python3` **and** under `python3 -O` with **identical
control verdicts**; `--gate-p` and `--grade` on an absent run root return **2** under both.
**Zero `ast.Assert` nodes in the comparator, established by AST parse and not by `grep`, with a
synthetic one-`assert` file reading `1` so the checker is shown to discriminate.** **The only
control not firing is `C12`** — **that is prediction `X4`, registered by Amendment 10, and this
amendment does not loosen it.**

### 17.5 RULING 4 — ITEMS 12 AND 14, CORRECTED

**THE RULING, THE SUPERVISOR'S:** *"correct both, they are unambiguous."*

#### 17.5.1 ITEM 12 — THE FORK IS NAMED, AND THE ESI SPELLING IS REGISTERED

§8.4 registers **`momentumTransport`** with `RAS { model kOmegaSST; … }`. **That is the
OpenFOAM FOUNDATION spelling.** **This box's solver is ESI OpenFOAM `v2506`**, which reads
`constant/turbulenceProperties` with the key **`RASModel`**.

**Measured by this lane inside the container that will run the solve:** in the v2506 tutorial
tree, **`momentumTransport` files: 0. `turbulenceProperties` files: 437.** The nearest analogue
(`tutorials/compressible/rhoSimpleFoam/aerofoilNACA0012`, external aerofoil, steady RAS) reads
`RAS { RASModel kOmegaSST; turbulence on; printCoeffs on; }`.

> ### **REGISTERED, AMENDMENT 11 RULING 4: the turbulence dictionary is `constant/turbulenceProperties`, and the key is `RASModel`.**
> **THE FORK AND VERSION THIS BOX RUNS: ESI OpenFOAM `v2506`, at
> `/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506` inside the container image
> `dafoam-idwarp-rot:v1`, which is what `cases/M6SR/run_m6sr_b5.sh` invokes.**
> **THE MODEL, THE SWITCHES AND THEIR VALUES ARE UNCHANGED** — `kOmegaSST`, `turbulence on`,
> `printCoeffs on`. **No gate, threshold, cap or label moves.** Without this, the solver runs
> with **no turbulence-model dictionary at all.**

#### 17.5.2 ITEM 14 — §8.1's TABLE IS STRUCK BY QUOTE, AND THE **FORMULA** IS REGISTERED

**RE-DERIVED BY THIS LANE, AS THE RULING REQUIRED, AND NOT TAKEN FROM THE BRIEF'S
TRANSCRIPTION.** At the registered `R = 287.058`, `γ = 1.4`, `T∞ = 288.15 K`:
`a∞ = √(γRT) = 340.2970287557621 m/s`, and `|U∞| = 285.679356 m/s` gives
**`M = 0.8395000010565409`** — the registered `0.8395`.

| reading | `U_x` | `U_y` | `|U|` (m/s) | **M** |
|---|---|---|---|---|
| §8.1's **TABLE** cell `(285.221 15.249 0)` | 285.221 | 15.249 | 285.6283439051524 | **0.8393500964422276** |
| §8.1's **PROSE** figures | 285.2721 | 15.2494 | 285.67939239428875 | 0.8395001080051349 |
| **§8.1's FORMULA `U∞·(cos 3.06°, sin 3.06°, 0)`** | **285.2720289804489** | **15.250046752474487** | **285.679356** | **0.8395000010565409** |

> ~~*"| `U` | m/s | `(285.221 15.249 0)` = `U∞·(cos3.06°, sin3.06°, 0)` | …"*~~

**STRUCK.** The table's vector gives **`M = 0.839350`**, not the registered `0.8395`, and a
`Re` **0.01786 %** off the registered `11.72 × 10⁶`.

> ### **REGISTERED, AMENDMENT 11 RULING 4: the freestream vector is the one §8.1's own FORMULA gives — `(285.2720289804489, 15.250046752474487, 0)` m/s — reproducing `|U| = 285.679356 m/s`, `M = 0.8395000` and `Re = 1.1720e7` on the MAC.**
> **The formula is the content the table cell and the prose sentence AGREE on; only the
> transcribed digits differ. Nothing about the registered state pair of §3 moves.**

**⚠ AND A FINDING THE RULING DID NOT ANTICIPATE, BECAUSE THE RE-DERIVATION WAS DONE RATHER THAN
COPIED.** §8.1's **PROSE** does not reproduce the formula either. It reads *"`285.679356 ×
cos(3.06°) = 285.2721`, `285.679356 × sin(3.06°) = 15.2494`"*; the formula gives
**285.2720290** and **15.2500468**. So **§8.1 carries four numerals for a two-component vector
and NOT ONE of the four is the formula's value.** The `U_x` prose slip is **+7.1e-05** (7th
significant figure, immaterial: `ΔM = +2.1e-07`); **the `U_y` prose slip is −6.5e-04 and the
table's is −1.05e-03**, neither of which the draft or the ruling names. **The registered vector
above is the FORMULA's, computed at full precision, and this is recorded as draft item 25
(§17.9) so the slip is struck rather than propagated.** Verified end to end: the case writer
emits `internalField uniform (285.2720289804489 15.250046752474487 0.0)`, read back from disk
by control `W3`.

### 17.6 ITEM 17 — GATE A WAS AS UNRUNNABLE AS GATE P, ONE GATE FURTHER BACK. FOUND AND FIXED

**Amendment 10 item 10 found that nothing ran `B5`. Measured by this lane: nothing ran `B4`
either.** `cases/M6SR/build_m6sr_l1.sh` contains **zero** occurrences of `checkMesh`, and §9's
frozen path table registers no other executable — while Gate A reads its named numeric maxima
off `<run_root>/<L>/log.checkMesh` and §5 rules that **"an absent `checkMesh` log reads
`ABSENT`. It never reads clean."**

**FIXED, in `cases/M6SR/run_m6sr_b5.sh`'s `stage` phase**, which runs `checkMesh` per level.
§2.4 gives **ONE** `B4` row (cap **2.0 core-min**) for *"checkMesh ×3"*, so the driver treats it
as a **running budget across the three levels**, ledgered at
`<run_root>/B4_SPENT_COREMIN.txt` and **refused when exhausted** — an overrun stops the run and
does not get a new budget (rule 12). **The cap is not moved.**

### 17.7 THE TWELVE WRITER CHOICES `CH1`–`CH12`, REGISTERED **HERE** AND NOT ONLY IN AN OUTPUT ARTIFACT

**They are already reproduced verbatim into every case's `CASE_PROVENANCE.json`. A choice made
pre-compute must be recorded where the FREEZE can see it, not only where a reader of a run tree
can.** They are registered here for that reason. **Each is a solver INPUT; none grades
anything; none moves a gate.**

| id | the choice | why §8 did not settle it |
|---|---|---|
| `CH1` | boundary conditions attached **by patch TYPE, never by name** | §7's screen does not predict the patch names |
| `CH2` | **`div(phi,Ekp)  bounded Gauss upwind`** | **§17.2, Ruling 1** |
| `CH3` | **`turbulenceProperties` / `RASModel`** | **§17.5.1, Ruling 4** |
| `CH4` | `lRef = 0.64607` (MAC), `Aref = 0.7532` (`S_ref`) | `forceCoeffs` requires both; draft item 19. Amendment 4a's gate-by-gate invariance holds — G1's and G2c's thresholds are **ratios in which any constant `Aref` cancels** — **the PRINTED `C_D` is not invariant** |
| `CH5` | `forceCoeffs` writes **every time step** | G1 needs a 500-iteration tail and G2c a 2,000-iteration tail; §8.5's `writeInterval = endTime` would leave **one** sample |
| `CH6` | **no `Pr` key** | `sutherlandTransport` reads only `As` and `Ts`; **derived `Pr_achieved = 0.6903229`, 4.122 % below §3's registered 0.72** — DERIVED, not measured in a solver run (draft item 13) |
| `CH7` | **`solverInfo`** | v2506 ships no function object named `residuals` (draft item 15). **Nothing grades on it** — §5.1 names `scripts/residual_max_over_equations.py` as G2's only instrument |
| `CH8` | freestream built from the **DERIVED** axes, refusing on an unexpected frame | draft item 20: §8.5's "constant-`y` planes" names the wrong axis; the span runs along `z` |
| `CH9` | **`U∞` from §8.1's FORMULA** | **§17.5.2, Ruling 4** |
| `CH10` | **`transonic` NOT set** | §8.3 registers it nowhere, so OpenFOAM's default `no` is what runs; registration by omission is still registration (draft item 18) |
| `CH11` | the **wing patch** is sampled and the seven planes are cut **by the comparator** | an OpenFOAM `cuttingPlane` cuts the **volume** and cannot isolate the wing **surface**; cutting the point-interpolated patch is exact linear interpolation along triangle edges and **introduces no spanwise binning tolerance** |
| `CH12` | the mesh is **copied** into the run root | `/home/ubuntu/certonomous-runs/` is **READ ONLY** |

**SPECIFIED BY §8 AND TAKEN VERBATIM, CHOSEN IN NOTHING:** all seven `0/` internal values and
BC types; the whole of `fvSchemes` bar `CH2`; the whole of `fvSolution`, including
`residualControl` **zero on every equation**; `molWeight 28.964425`, `As 1.571860616e-06`,
`Ts 110.4`, `Cp 1004.5`; `endTime` 3000/4000/5000; `writeControl timeStep` with
`writeInterval = endTime`; `hierarchical` with `scotch` **not used**; ranks 4/8/16; caps
31.0/163.0/1630.0 core-min; the seven `y/b`; and `b_semi = 1.19676 m` (§17.3).

### 17.8 🔴 `X1` STANDS. NOTHING IN THIS AMENDMENT REVIVES IT

**Re-measured by this lane through the frozen reader on the pinned `case_2308.dat`, after every
change above:**

> **`D1` = `INDETERMINATE`. `Cn(7)/Cn(1) = 0.8787468156097933` → `0.878747`**, inside §4.3's
> registered indeterminate band `(0.75, 1.333)`; the `Cn` series is **non-monotone**.
> **Gate P's PER-STATION channel is therefore `NOT A RESULT`, exactly as `X1` predicts.**

**NOTHING HERE TOUCHES THAT.** Ruling 1 is a divergence scheme. Ruling 2 is where a station
sits, not which experimental section it is. Ruling 3 splits a **figure** and leaves §4.5's
graded RMS byte-unchanged. Ruling 4 is a dictionary spelling and a freestream transcription.
**The per-station channel is `NOT A RESULT` by the operation of §4.3's own falsification table,
on experimental bytes that predate this ladder, with no CFD in existence** — and `X2`, `X3` and
`X4` likewise stand exactly as Amendment 10 registered them.

### 17.9 🔴 THREE FURTHER ITEMS — THE FIFTEENTH PASS

**The supervisor instructed this lane to assume a fifteenth item existed and to look for it.
There are three. Recorded, NOT repaired. Item 26 is the serious one.**

| # | what cannot be satisfied | measured basis | consequence |
|---|---|---|---|
| **25** | **§8.1's PROSE does not reproduce §8.1's FORMULA EITHER — the defect is wider than Ruling 4 names.** | Formula: `285.679356·cos(3.06°) = 285.2720289804489`, `·sin(3.06°) = 15.250046752474487`. §8.1's prose prints **285.2721** and **15.2494**; its table prints **285.221** and **15.249**. **Four numerals for a two-component vector; none of the four is the formula's value.** `U_x` prose slip +7.1e-05 (`ΔM = +2.1e-07`, immaterial); **`U_y` prose slip −6.5e-04, table slip −1.05e-03.** | Handled **in the same direction as Ruling 4** — the FORMULA is registered (§17.5.2) and reproduces `M = 0.8395000` and `Re = 1.1720e7`. **Recorded so the `U_y` slips are struck too and not left to be discovered in a case file.** |
| **26** 🔴 | **NO OPENFOAM VERSION AND NO CONTAINER IMAGE IS REGISTERED ANYWHERE IN THIS DOCUMENT — AND THE BOX CARRIES TWO ESI TREES.** | **Measured with a discriminating reader:** a sweep of this file for any version token `v2[0-9]{3}` returns **0**, while `rhoSimpleFoam` returns **4** — the reader can see what is there. On the box: native **`/usr/lib/openfoam/openfoam2606`**; in the solve container `dafoam-idwarp-rot:v1`, **`OpenFOAM-v2506`** *and* **`OpenFOAM-AD`**. And `cases/M6SR/run_m6sr_b5.sh:78` reads **`IMG=${M6SR_IMAGE:-dafoam-idwarp-rot:v1}`** — **an environment variable can change the solver binary between the freeze and the run, silently.** | 🔴 **Every one of items 11, 12, 15 and 18 — and therefore Ruling 1 and Ruling 4 — is a VERSION-DEPENDENT finding.** `momentumTransport` is right for one fork and wrong for the other; `residuals`-vs-`solverInfo` moved at v1912. **A registration that pins `case_2308.dat` and a points-file sha256 but not the solver binary is pinning the data and not the instrument.** **Registering a version, an image and a digest is a grading-path/freeze question and is the supervisor's**; a lane may not pin it. **Stated before a launch is ordered, not at the drop path.** |
| **27** | **§4.5's RMS is weighted ~2:1 toward the upper surface, and the "symmetric, so not a bias" reading is right about the COMPARISON and silent about the CURVE.** | Measured on the pinned bytes: **185 of 271 taps (68.27 %) are upper-surface** — 23/11 on sections 1–4, 31/14 on 5–7. Both curves interleave, so the comparison is symmetric; but the RMS a section contributes is **two-thirds an upper-surface statistic**. | **NOT REPAIRED.** §4.5's channel is **graded** and its force is one-directional under rule 5; changing what it measures is a gate question. **Reported so the supervisor rules on a measured weighting rather than on the word "symmetric".** The **figure** is split (§17.4) and is unaffected. |

> **WHAT M6SR CAN AND CANNOT DO AFTER THIS AMENDMENT, STATED ONCE, PLAINLY.**
> **CAN:** run `B1`–`B3`; **stage** L3/L2/L1 and run `B4`'s `checkMesh` (§17.6); grade
> **`Gate GF`** and **`Gate A`**; write §8's case files with a `div(phi,Ekp)` entry the solver
> asks for (§17.2) and a turbulence dictionary it reads (§17.5.1); run `B5a`/`B5b`/`B5c`; and
> **produce Sanaa's named first-physics figure DATA at `<run_root>/GATE_P_FIGURE_DATA.json`
> with upper and lower surfaces as SEPARATE curves** (§17.4), every level, carrying clause
> `L-HONEST` verbatim.
> **CANNOT:** grade Gate P's **per-station** channel — **`X1`**, unchanged.
> **CANNOT:** print a Gate P **verdict** beside a Gate G band while **`X3`** stands.
> **`Gate GF`'s `GF2` and `GF4`-semispan limbs are still predicted `GATE FAIL`** (Amendment 10
> item 8, `X2`); **the control suite still REFUSES (exit 2) on `C12`** (`X4`).
> **AND THE SOLVER BINARY IS STILL UNPINNED (item 26).**

### 17.10 COST — RULE 12, AND NONE OF IT IS LADDER COMPUTE

**No step of §2.4's cost table was run and `verification/runs/M6SR_runs` does not exist.** What
this amendment spent is host arithmetic, read-only inspection of already-existing artifacts
(the pinned `case_2308.dat`, this file, two scripts), **read-only `grep` and `sed` inside the
solve container** (three `docker run --rm` invocations, no solver, no mesh), the comparator's
own control suite and its 22-target mutation loop, and the case writer's suite under both
interpreters: **≈ 11 core-min at 1 rank, and it is an ESTIMATE from this session's own wall
clock, NOT a measurement read from a run log** — no run log exists for it and inventing one
would be worse than saying so. **Derived at the owner-stated `c7a.4xlarge` $0.0513/core-h:
≈ $0.0094 — DERIVED, REPORTED-BY-OWNER, never measured, because the box cannot read its own
billing** (`COMPUTE_BUDGET_CHARTER.md` §5).

**§9.3's estimate-versus-actual row is NOT owed yet**, because no `B` step has completed. It
falls due at `B1`'s completion. **§2.4's `est ≤ cap` table is untouched by this amendment** —
Amendment 10 §16.6 re-derived every row and no row of it moves here.

### 17.11 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves no gate, no threshold, no cap and no label**, with the two exceptions the
   supervisor's rulings expressly authorise — the **`div(phi,Ekp)` scheme** (§17.2) and the
   **station reference semispan** (§17.3, whose registered VALUE is unchanged from §8.5) —
   each stating its reason and its predicted consequence. Not one number in §2.4, §5, §5.1, §7
   or §10 is touched.
2. **It does NOT re-freeze.** `SUPERVISION_CHARTER.md` §3 check 4 belongs to the cfd supervisor
   and is **undischarged**. **Check 1 — the comparator diff, read as a diff — is likewise the
   supervisor's**, and the diff is filed at
   `cases/M6SR/AMENDMENT_11_RULING_3_FIGURE_SPLIT.diff`.
3. **It does NOT re-pin the §9 path table.** `cases/M6SR/analyse_m6sr.py` and
   `cases/M6SR/write_m6sr_case.py` changed in this amendment and **their blob shas must be
   re-pinned at the freeze**; a lane may not pin a grading path.
4. **It does NOT enqueue anything.** `verification/queue/cfd/` is a live launch path and this
   lane wrote nothing into it. **No compute was launched.**
5. **It does NOT touch §4.5's graded channel.** `set_to_set_assignment()` is byte-unchanged and
   still interleaves (§17.4, item 27).
6. **It does NOT revive Gate P's per-station channel. `X1` stands** (§17.8), and `X2`, `X3`,
   `X4` stand with it. **It does not loosen `C12`.**
7. **It does NOT register an OpenFOAM version, image or digest** (item 26). It **names** what
   the driver invokes today and records that nothing pins it.
8. **It does NOT change `/home/ubuntu/certonomous-runs/`**, which was read only, nor
   `docs/LAB_STATE.md`.
9. **It claims no verdict of the fixed vocabulary for any gate.** Every `PASS` / `GATE FAIL` /
   `NOT A RESULT` above is inside a registered **PREDICTION** or a **quotation**, and a
   prediction is not a verdict. **No solver has run.**
10. **SUBMISSIONS REMAIN PARKED (rule 7). Nothing left the box (rule 8).**

### 17.12 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.2 → v1.3 (amendment 11, pre-compute). The frozen file was NOT edited; this
section is APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason
§15.10 and §16.9 give: editing it would change a line above §15 and falsify that section's own
assertion, on which other records depend. **The bump is recorded HERE, which is where rule 6
puts it. The supervisor may restate the version in the header at the re-freeze, which is a
status flip they own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–2690** of this file — the whole of it up to and including
§16.9's closing line, and therefore the whole of §15's guaranteed range 1–2022 and §16's
guaranteed range 1–2229 — are **byte-identical** before and after this append, both rendering
to sha256 **`ddc16dc72104fc04400b65b7b7904a86c8013ca5fac70a86c1b415a83b0d4f13`**. Other records
cite this document **by line**, and at least one such citation sits inside an executable check,
so this is a guarantee and not a courtesy.

---

## 18. AMENDMENT 12 — 2026-09-04T1631Z. **THE INSTRUMENT IS PINNED**, §9's EXECUTABLES ARE PINNED BY BLOB SHA, AND THE SIXTEENTH PASS FINDS FIVE MORE

**Drafted and applied by a cfd lab-lane on the cfd supervisor's three rulings of 2026-09-04 and
their same-day addition. THIS IS NOT A FREEZE AND NOT A RE-FREEZE.**
`SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's, is not delegated, and is **undischarged
as this section is written.** **Check 1 — the producer diff, read as a diff — is likewise the
supervisor's.** **No compute was launched by the lane that wrote it, no step of §2.4's cost table
was run, no queue row was written, and `verification/runs/M6SR_runs/` still does not exist.**

> **THE DIVISION OF LABOUR.** The three rulings below are the **supervisor's**, taken on the
> sixteen items §17.9 and its predecessors recorded. **This lane implemented them and did not
> re-decide any of them.** Where implementing a ruling forced a choice the ruling did not settle,
> the choice is **named as such, quantified, and handed back**.
>
> **`L-HONEST` (§6) IS CARRIED UNALTERED.** The family refines **2 of 3 directions**, the
> wall-normal discretisation is **identical across levels**, `GCI_fine` is a **LOWER BOUND**,
> `p_s` is **NOT an observed order**, and **Sanaa's named first deliverable remains owed.**
>
> **THIS AMENDMENT MOVES NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** It registers **pins** and
> **refusals**, and a pin is not a gate. Not one number in §2.4, §5, §5.1, §7 or §10 is touched,
> and `X1`–`X6` stand exactly as Amendments 10 and 11 registered them.

### 18.1 THE CONDITION, AND HOW IT WAS CHECKED — RULE 2 REQUIRES BOTH

**THE RUN DIRECTORY THAT DOES NOT EXIST — NAMED, AS RULE 2 REQUIRES:**
**`verification/runs/M6SR_runs/`**, and with it `verification/runs/M6SR_runs/{L1,L2,L3}/`.

**How checked, at 2026-09-04T1631Z, WITH A LIVE PLANTED CONTROL (rule 3), AFTER every rehearsal
this amendment ran:**

| path | reader's answer | role |
|---|---|---|
| `verification/runs/M6SR_runs` | **ABSENT** on disk; `git ls-tree -r HEAD` returns **0 files** | the run root — **the zero** |
| `verification/runs/M6I_runs` | `git ls-tree -r HEAD` returns **14 files** | **the planted non-zero**, same reader, same act |

⚠ **AND THE ZERO WAS AT RISK, WHICH IS WHY IT IS RE-CHECKED HERE RATHER THAN CARRIED FROM §17.1.**
This amendment **rehearsed the driver end to end six times** to measure the refusals it registers.
`run_m6sr_b5.sh` creates its case directory before any refusal fires, so every rehearsal was run
with `M6SR_RUN_ROOT` pointed at a scratch tree, and §18.6's new run-root refusal is **deliberately
ordered LAST of the three** for exactly this reason — placed first it would make the other two
unrehearsable anywhere except inside the directory whose absence is this document's freeze proof.
**The reader above was run after all six and still returns ABSENT beside a PRESENT.**

### 18.2 RULING 1 — **THE SOLVER IS PINNED.** FORK, VERSION, IMAGE, DIGEST AND BINARY

**THE RULING, THE SUPERVISOR'S:** *"A registration that pins the data and not the instrument is
pinning half … Register the OpenFOAM fork, version, image name AND image digest, plus the resolved
solver binary path. Verify the digest yourself and record HOW you obtained it. And register a
refusal — the launch aborts at zero solver cost if the running image's digest does not match the
pinned one."*

#### 18.2.1 THE REGISTRATION

> ### **REGISTERED, AMENDMENT 12 RULING 1 — THE INSTRUMENT.**
>
> | what | registered value |
> |---|---|
> | **fork** | **ESI OpenFOAM** (openfoam.com). **NOT the OpenFOAM Foundation fork.** |
> | **version** | **`v2506`**, corroborated by `META-INFO/api-info` reading `api=2506`, `patch=0` |
> | **image reference** | **`dafoam-idwarp-rot:v1`** |
> | **image digest** | **`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`** |
> | **resolved solver binary** | **`/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/rhoSimpleFoam`** |
> | **binary sha256** | **`d9a2a45664f519e9f6b4c34741a4c414517889b4cfbe7764b2237ebf9a01369c`** |
> | **container run target** | **the DIGEST, never the tag** |
>
> **The four values live in `cases/M6SR/run_m6sr_b5.sh` as PLAIN ASSIGNMENTS — not
> `${VAR:-default}` forms — so nothing in the environment can change them.**

#### 18.2.2 HOW THE DIGEST WAS OBTAINED — STATED, BECAUSE A PIN WHOSE PROVENANCE IS NOT STATED IS A NUMBER SOMEBODY TYPED

**Obtained by this lane, on this box, at 2026-09-04T1620Z**, with `docker inspect
dafoam-idwarp-rot:v1` read through a JSON parser rather than through a format template, because a
template that mis-maps a field is exactly the silent-wrong-answer family this campaign convicts:

- **`.Id`** = `sha256:2927768a…6d35`.
- **`.Descriptor`** = `{"mediaType": "application/vnd.oci.image.manifest.v1+json", "size": 2301,
  "digest": "sha256:2927768a…6d35"}`. **The digest is therefore an OCI IMAGE MANIFEST digest**,
  not merely a legacy config id: on this daemon (**docker 29.1.3, storage driver `overlayfs`**)
  `.Id` and the manifest descriptor carry the same content address.
- **`.RepoDigests`** = `["dafoam-idwarp-rot@sha256:2927768a…6d35"]` — the same value again.
- **`.Created`** = `2026-08-21T16:09:52.14997014Z`; **`.RootFS.Layers`** = 9 layers, top layer
  `sha256:55e79185ac255844b71ad1952a68d6db7d31b186b0e6bcb02a996281681c3874`.

⚠ **THE CAVEAT, STATED RATHER THAN LEFT TO BE INFERRED. The digest is NOT corroborated against a
registry.** The image was built on this box and no registry copy was consulted, so this is a
**local content address, not a third-party attestation**. It is nevertheless the strongest
available pin: it changes if any layer changes, and the launch refuses on any change.

**THE READER WAS SHOWN ABLE TO SAY OTHERWISE (rule 3).** `docker run` against the pinned digest
returns **rc 0**; against
`sha256:0000000000000000000000000000000000000000000000000000000000000000` it returns **rc 125**,
`No such image`. A resolver that accepts everything is not a pin.

#### 18.2.3 THE REFUSAL — MEASURED, ON FOUR LIMBS, AT ZERO SOLVER COST

**Implemented in `cases/M6SR/run_m6sr_b5.sh` §1b, which runs BEFORE `stage` and therefore before
any core-minute of §2.4's table is spent.** New exit code **`7`**. Five clauses: the image must
resolve; its digest must equal the pinned one; `WM_PROJECT_VERSION` inside it must read `v2506`;
`command -v rhoSimpleFoam` must resolve to the pinned path; and that binary's sha256 must equal
the pinned one. The result is written to `<case>/SOLVER_PIN.json`.

| limb | `M6SR_IMAGE` | measured rc | reader's answer |
|---|---|---|---|
| **known-positive** | *(unset → the pinned image)* | reaches §18.6's later check | `solver pin VERIFIED: v2506 at …/OpenFOAM-v2506/…/rhoSimpleFoam` |
| a **sibling DAFoam image** | `dafoam-team:v1` | **7** | `IMAGE DIGEST MISMATCH` |
| an unrelated image | `alpine:latest` | **7** | `IMAGE DIGEST MISMATCH` |
| a name that resolves to nothing | `no-such-image:v0` | **7** | `does not resolve to a digest` |

**The positive limb is what licenses the three negatives.** A refusal from a check never shown able
to accept is not evidence, and the sibling-image limb is the discriminating one: `dafoam-team:v1`
is a real DAFoam container on this box and would have been an entirely plausible accident.

#### 18.2.4 ⚠ CAN `M6SR_IMAGE` STILL OVERRIDE? — ANSWERED DIRECTLY, AS THE RULING DEMANDED

**NO. `M6SR_IMAGE` can still NAME an image; it can no longer SELECT one.** Measured above: every
non-pinned name aborts at **exit 7** before the driver stages a mesh, runs `checkMesh` or starts a
solver. **And the container is thereafter addressed BY DIGEST, not by the tag** — `run_in_container`
now passes `$IMG_PINNED`, the digest — so a tag re-pointed between the check and the run cannot
substitute an image either. That time-of-check/time-of-use hole was open in the naive form of this
fix and is closed.

**What the pin does NOT defend against, stated plainly:** anyone who can edit
`cases/M6SR/run_m6sr_b5.sh` can change the pinned constant. That is not an environment-variable
hole; it is a file whose blob sha is pinned by §18.3 below and which
`scripts/check_comparator_freeze.py` can verify at grading.

#### 18.2.5 🔴 THE VERSION-DEPENDENCE AUDIT THE RULING ORDERED — AND WHAT IT ACTUALLY FOUND

**The ruling states, correctly, that items 11, 12, 15 and 18 — and therefore Amendment 11's
Rulings 1 and 4 — are version-dependent findings measured inside a container that could change.
This lane re-measured all four against the box's OTHER ESI tree, native
`/usr/lib/openfoam/openfoam2606` (`api=2606`, `patch=0`), rather than asserting the exposure:**

| finding | measured in the pinned `v2506` | measured in native `openfoam2606` | verdict |
|---|---|---|---|
| item 11 / Ruling 1 — `EEqn.H` requests `div(phi,Ekp)` under `sensibleInternalEnergy` | `fvc::div(phi, volScalarField("Ekp", 0.5*magSqr(U) + p/rho))` | **identical ternary, same two lines** | **SURVIVES** |
| item 12 / Ruling 4 — `turbulenceProperties` / `RASModel`, not `momentumTransport` | tutorials: `momentumTransport` **0**, `turbulenceProperties` **437** | tutorials: `momentumTransport` **0**, `turbulenceProperties` **439** | **SURVIVES** |
| item 15 — `solverInfo`, not `residuals` | `solverInfo` ships; `residuals` does not | `etc/caseDicts/postProcessing/numerical/solverInfo` **PRESENT**, `…/residuals` **ABSENT** | **SURVIVES** |
| item 18 — `transonic` defaults to `no` when unregistered | registration by omission | unchanged across both | **SURVIVES** |

> **✅ SO THE HONEST FINDING IS NARROWER AND SHARPER THAN THE EXPOSURE.** **None of the four flips
> between the box's two ESI trees.** They would flip against the **OpenFOAM Foundation** fork
> (`momentumTransport` is that fork's spelling) and against an **algorithmic-differentiation**
> build. **And that is exactly what `M6SR_IMAGE` could have selected**: the pinned image carries
> **`OpenFOAM-AD`** alongside `OpenFOAM-v2506`, with **its own `rhoSimpleFoam` binaries** under
> `platforms/linux64GccDPInt32OptADF` and `…ADR`. **The pin's value is not that the two ESI trees
> disagree — measured, they do not. It is that nothing prevented a THIRD tree from running under
> the same command, and the path-and-sha256 limbs of §18.2.3 are what catch that.**

### 18.3 RULING 2 — §9's PATH TABLE IS PINNED BY BLOB SHA, AND §15.3's PIN IS **STRUCK BY QUOTE**

**THE RULING, THE SUPERVISOR'S:** *"Pin every executable in §9 by blob sha, verified at the moment
you write it, and say which commit each blob comes from … Re-hash immediately before committing."*
**AND ITS ADDITION:** *"So pin THREE, not two … `cases/M6SR/run_m6sr_b5.sh` — the SOLE PRODUCER of
`SOLVER_RC.txt` — is not in it. Neither is `write_m6sr_case.py`."*

#### 18.3.1 THE PINS

**Every blob below was re-derived by this lane with `git hash-object` on the working tree, checked
against `git rev-parse HEAD:<path>`, and re-verified in the same shell invocation as the commit
that carries this section. Every one read CLEAN — working tree identical to HEAD — before the
pin was written.**

| §9 registered path | git blob sha | sha256 of the file | lines | blob first appears at |
|---|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`9b963ad48e016fe2177553507006915e52b4ef98`** | `9042cdf22ff948f8df48d846495ccb0d05e5130d19a0572b6020b728507d9394` | 2,742 | **`8c0ab7a8`** (Amendment 11) |
| **`cases/M6SR/build_m6sr_l1.sh`** (build driver) | **`04ae9d58220a55fa900b02f77424bb7687da0de1`** | `6459428b4c283c597e72e08f7c7ded3c454cfb8efd0facbbc8b178b42e5abc35` | 304 | **`c1625208`** (Amendment 9) |
| **`scripts/residual_max_over_equations.py`** (G2's only instrument, §5.1) | **`b5eee67d594c04df90a2201b003039d5959c6eb4`** | `39a5e0d4b19ab5aa9313888e86297e7ff8c0bb7dc0c2e8628479b561d1c0bbd7` | 433 | **`184c00af`** |
| **`scripts/verify_agard_ar138_table_b1_1.py`** (the `GF2` reference loader) | **`6cc89ced4cbd54e3b6b57403fe7224e6e08a83ab`** | `ee62a6ac6cb8cb6b19cc6cad7f742c8fcf0e434f3ec272449aaa7f38b9c96bde` | 222 | **`96e08380`** (the `C19` repair) |
| **`scripts/check_comparator_freeze.py`** (named by §9.1 as the verifier) | **`dabd740e56a017edbc04b9c2b866c93c661ce0ab`** | `2871fabbab2bf8a126af49d4cdf6c7c6cb3a7ef9fd107b2afa4e942771b54709` | 904 | **`5c31a23c`** |

**AND THE TWO EXECUTABLES §9's TABLE DOES NOT REGISTER, PINNED HERE AND FLAGGED AS THE GAP THEY
ARE:**

| path | git blob sha | sha256 of the file | lines | status |
|---|---|---|---|---|
| **`cases/M6SR/write_m6sr_case.py`** (§8's sole writer) | **`f2e8f3bc5982e92b9f5697e568c0f31f3c17d0a5`** | `eb8abf930e999ab2af2eac74793229df0ddd096a34f41756a378627ce15c360c` | 1,059 | **NOT in §9's table** |
| **`cases/M6SR/run_m6sr_b5.sh`** (the sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam` and `log.checkMesh`) | **`44fae79bbae918ae101d7d4a9b8ad96bdef66734`** | `5d0bc9df92f272a5d1a22e43708b8cd386f08e352fa282993e65c7d5072bd579` | 561 | **NOT in §9's table**; **CHANGED BY THIS AMENDMENT** (§18.2.3, §18.5, §18.5.1, §18.6) |

⚠ **AND A PIN THAT MOVED WHILE THIS SECTION WAS BEING WRITTEN — RECORDED, BECAUSE IT IS THE
EXACT ROT RULING 2 EXISTS TO CATCH.** `run_m6sr_b5.sh` hashed to `0b3b73bb…` at 547 lines when the
first draft of this table was written; the re-hash **immediately before the commit REFUSED**, the
file having moved to `44fae79b…` at 561 lines. **Inspected, never reverted** (rule 10): the 14 new
lines are a second lane's `SOLVER_RC.txt` assert, described in §18.5.1, accepted by the supervisor
and carried in this commit. **The pin above is the re-hashed value and the refusal is why it is
right.** A table written once and committed later would have pinned a file that no longer existed.

⚠ **THE HOLE, NAMED.** §9.2 states the rule — *"`rc` is captured **inside** the detached wrapper
and written to `SOLVER_RC.txt`"* — and **pins no artifact that implements it**. §17.11 item 3 named
only the comparator and the case writer as needing re-pinning; **the producer was not even on that
list.** **Adding a path to §9's frozen table is a freeze question and is the supervisor's**; this
lane pins the shas and reports the gap.

#### 18.3.2 §15.3's PIN IS SUPERSEDED AND IS STRUCK BY QUOTE

> ~~*"| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`97cbe0390318f010f7d1dd8ebe4e870fd72c5e68`** | `168fd0896a4055e1106a1ba0eaaf00e6eca1851109a6aa9b60ebcbde32891f75` | 2,106 |"*~~

**STRUCK.** Amendment 11's Ruling 3 added 121 lines to that file (`split_curve_upper_lower`,
`C24`, the figure split). The comparator now hashes to `9b963ad4…` at 2,742 lines. **The §15.3 row
is not edited in place** — rule 6 — **and the current pin is the §18.3.1 table.**
**`cases/M6SR/build_m6sr_l1.sh`'s §15.3 pin `04ae9d58…` is RE-VERIFIED UNMOVED**, which is the
control that shows the strike above is a real change and not a re-hashing artefact: **one pin moved
and one did not, read by the same command in the same act.**

### 18.4 RULING 3 — THE SEMISPAN: `1.19676` IS KEPT, `1.1963` IS REGISTERED BESIDE IT, THE DELTA IS REPORTED

**THE RULING, THE SUPERVISOR'S:** *"KEEP `1.19676`, and register `1.1963` beside it as the
AGARD-printed alternative with its delta REPORTED … Moving a number that is in force, for an effect
40× below the one I have already registered as the load-bearing prediction, is churn … Register
both, use the one in force, report the delta, and name this as a choice that a successor may
reverse with a reason."*

> ### **REGISTERED, AMENDMENT 12 RULING 3.**
> **THE STATION REFERENCE SEMISPAN IN FORCE IS `b_semi = 1.19676 m`** — §8.5's STL-measured value,
> registered by Amendment 11 Ruling 2, and **BYTE-UNCHANGED**: the comparator's `B_SEMI_M` is not
> touched and the seven station coordinates of §17.3.3 are not touched.
>
> **REGISTERED BESIDE IT, AS THE ALTERNATIVE READING ON THE SAME EXPERIMENTAL SIDE:**
> **`b_semi_AGARD_printed = 1.1963 m`**, AGARD AR-138's printed physical semispan, already carried
> by §5's `GF4` as a gate reference.

**THE DELTA, RE-DERIVED BY THIS LANE AT FULL PRECISION AND NOT COPIED FROM THE RULING:**

| quantity | value |
|---|---|
| `b_semi` in force − AGARD printed | **`0.000460000000000127 m`** (`0.038437 %` of the value in force) |
| station 7 (`y/b = 0.99`) in force | `0.99 × 1.19676` = **`1.1847924 m`** |
| station 7 under the AGARD-printed value | `0.99 × 1.1963` = **`1.184337 m`** |
| **station 7 shift if `1.1963` were adopted** | **`0.0004554000000001057 m`** |
| the same shift, % of `b_semi` | **`0.03805274240450096 %`** |
| the same shift, as chordwise shock displacement at §16.4's own rate (1 % of semispan ≈ 0.7 cm) | **`0.0266 cm`** |
| **prediction `X6`'s registered shift, for comparison** | **`1.62507 %` ≈ `1.1375 cm`** |
| **ratio `X6` / this** | **`42.71 ×`** |

**✅ The supervisor's "roughly FORTY TIMES SMALLER" is measured at `42.71 ×`, and every station
stays inside both meshes' wall-patch extent `[0, 1.216405] m` under either value**, so `C22`
cannot refuse on span either way.

> **REGISTERED AS A REVERSIBLE CHOICE, IN THE SUPERVISOR'S OWN TERMS.** This registration uses
> `1.19676 m` because it is the value **already in force** and because the effect of moving it is
> **42.71 × smaller** than the displacement `X6` already registers as load-bearing. **A successor
> may reverse this with a reason**, and the number they would need — `0.0004554 m` at station 7 —
> is registered above so the reversal argues against a measurement rather than against a habit.
> **Churn on a registered number is how a document acquires a fourth semispan**; the document now
> holds **three, each with its role stated** (§17.3.1), and this amendment adds **none**.

### 18.5 THE PRE-LAUNCH GRADING-PATH GATE — THE `SOLVER_RC` CLASS AGAIN, AND THE SAME FIX

**THE OPERATIONAL FACT THE SUPERVISOR MOST WANTED REGISTERED, RE-MEASURED HERE:**
`cases/M6SR/run_m6sr_b5.sh` gated on **the WRITER's `--selftest`** and on nothing else. It never
ran **the COMPARATOR's `--controls`**. So `X4`'s `C12` refusal blocked **GRADING**, not the
**LAUNCH** — and `B5a`+`B5b`+`B5c`, **607.63 of §2.4's 615.24 core-min, 98.8 % of the ladder**,
could have been spent in full and then been **ungradable**.

> ### **REGISTERED, AMENDMENT 12: A PRE-LAUNCH GATE ON THE GRADING PATH.**
> Before the `solve` and `all` phases reach `stage` — and therefore before **any** core-minute of
> §2.4's table is spent — the driver runs `cases/M6SR/analyse_m6sr.py --controls` under
> **`python3` AND `python3 -O`**, and **REFUSES (new exit code `8`)** unless both return **rc 0**
> and the two rc values agree. §9.2 binds every comparator to `-O` parity; **a gate that only
> holds under one interpreter flag is one flag from absent** (L-475, L-332).
>
> **SCOPE, NAMED SO NO READER HAS TO INFER IT.** Phase **`stage` alone is NOT gated.** It runs
> `checkMesh`, which is not a solver, and gating it would leave Gate A with **no log at all** to
> read — §5 rules that an absent `checkMesh` log reads `ABSENT` and *"never reads clean"*, so
> gating `stage` would convert a missing gate into a permanently missing gate. **That is this
> lane's reading of "at zero SOLVER cost", it is named as a choice, and the supervisor may
> narrow or widen it.**

**MEASURED, END TO END, ON THE DRIVER ITSELF** (scratch run root, pinned image, level L3, phase
`solve`): `analyse_m6sr.py --controls` returns **rc 2 under `python3` and rc 2 under `python3 -O`**
— identical — and the driver **aborts with exit 8** naming `C12`, having started **no container and
no solver**. Cost of the rehearsal itself: **10 wall s at 1 rank = 0.167 core-min.**

> **REGISTERED PREDICTION `X7`: while `X4` stands — `C12` cannot fire on a non-monotone as-read
> `Cn` series — `run_m6sr_b5.sh <LEVEL> solve` and `<LEVEL> all` REFUSE at exit 8, at ZERO solver
> cost. `<LEVEL> stage` is unaffected and still reaches `B4`.** ⚠ **THIS IS A REAL NARROWING OF
> WHAT THE LADDER CAN DO TODAY AND IT IS NOT HIDDEN: the gate does not loosen `C12` and it does
> not move a threshold — it moves the moment of the refusal from AFTER 607.63 core-min to
> BEFORE zero.** **A refusal is not a gate; but a refusal that blocks every solve is a fact the
> supervisor must see before ordering a launch, and it is stated here rather than at the drop
> path.**

### 18.5.1 A SECOND LANE'S `SOLVER_RC.txt` ASSERT — CARRIED IN THIS COMMIT, AND ITS MECHANISM IS SHARPER THAN THE ONE THIS LANE WOULD HAVE WRITTEN

**AUTHORSHIP, STATED SO THE RECORD IS NOT THIS LANE'S BY DEFAULT.** Fourteen lines at
`run_m6sr_b5.sh:440–453` were written by **a different cfd lane**, which found the defect, made the
change in the shared working tree, **correctly refused to commit it** — the file already carried
this amendment's uncommitted work and the private-index protocol stages whole files — and handed it
up. **The supervisor accepted it and directed this lane to carry it.** It is carried unaltered.

**THE DEFECT, AS THAT LANE STATED IT.** §8.6's completion clauses `rc_zero` and
`rc_read_from_SOLVER_RC_not_around_setsid` read **`<case>/SOLVER_RC.txt`**. `run_in_container()`
asserts the **wrapper's** rc from **`RC_<STEP>.txt`** — *a different file, written by a different
`echo`*. The inner command reads
`… SOLVER_RC=$?; echo $SOLVER_RC > SOLVER_RC.txt; reconstructPar …; exit $SOLVER_RC`, so **it exits
with `$SOLVER_RC` whether or not the `echo` before it succeeded.**

> 🔴 **A full-cap solve can therefore land with `log.rhoSimpleFoam` present, the wrapper rc 0, and
> `SOLVER_RC.txt` ABSENT — and be found ungradable only at GRADING TIME, after the entire spend:
> up to `163` core-min at L2 and `1630` at L1.** **This is the same class as §18.5 and the same
> loss**, one artifact further down.

**WHAT IT ADDS: two clauses, both exit 6, both after the solve step and at zero further solver
cost.** An **existence** clause on `SOLVER_RC.txt`, and — beyond what was asked, and endorsed — an
**emptiness (`-s`)** clause, because a write interrupted mid-flight leaves a **0-byte** file that
`completion_clauses` reads as **no rc at all** rather than as a bad one. **It does NOT create the
file and does NOT synthesise an rc**: a fabricated rc would convert an unrecorded crash into a
silent `rc_zero`, and **a fabricated rc is worse than an absent one.**

**THE PATTERN IS CITED HONESTLY AND NOT OVERSOLD.** `cases/F23b_HP_WEDGE/run_f23b.sh:490` is
`[ -f "$CD/0/U" ]` — a post-step existence assert on **a downstream reader's artifact**. It is the
right pattern **in kind**; it is **not** an rc-file assert, and F23b has no equivalent gap because
it writes `RC.txt` in the shell itself. **Cited as the pattern, not as a precedent for this assert.**

### 18.6 THE RUN ROOT IS PINNED TOO — ITEM 29, THE SECOND ENV-VAR DIVERGENCE

**MEASURED, and independently found by this lane and by the supervisor's rehearsal lane:**
`run_m6sr_b5.sh` honours **`M6SR_RUN_ROOT`**, while **`cases/M6SR/analyse_m6sr.py` reads NO
environment at all** — its `REPO` is derived from `__file__` and its run root comes from
`--run-root`. **`os.environ`/`getenv` occurrences: 0 in the comparator, 0 in the case writer.**
*(The zero is planted: the identical reader returns **1** on a `scripts/*.py` file that does read
the environment, so it is not a blind zero.)*

**An operator who exports `M6SR_RUN_ROOT` without passing a matching `--run-root` sends the
PRODUCER and the READER to different trees.** It fails closed — the comparator finds no case and
refuses — **but a pin that holds only because the other side happens to refuse is not a pin.**

> ### **REGISTERED, AMENDMENT 12: the run root is `verification/runs/M6SR_runs/` and an export that changes it is a REFUSAL, not a grade.**
> New exit code **`9`**. The driver writes `<case>/RUN_ROOT_USED.txt` and aborts if `$RR` is not
> §9's registered path. **Measured: rc 9, with the mismatching path and the registered path both
> printed.**
>
> ⚠ **ORDERED LAST OF THE THREE NEW REFUSALS, AS A NAMED CHOICE (§18.1).** All three are at zero
> solver cost and precede `stage`, so their order is free; placed first, this one would make
> §18.2's and §18.5's refusals **unrehearsable outside the very directory whose absence is this
> registration's rule-2 freeze proof.**

**AND A CONTROL REGISTERED, NOT IMPLEMENTED — SAID PLAINLY RATHER THAN IMPLIED.**

> ### **REGISTERED CONTROL `C25` (§10, `SOLVER_RC` producer):**
> plant `0`, then `1`, then **delete the file**, through the shipped producer statement.
> **MUST SEE:** `rc_zero` **True**, then **False**, then **False with the EXISTENCE clause also
> False → REFUSAL**. **Two clauses, not one: absent must not launder into zero.** **Its positive
> limb — rc 0 with every other clause perfect — is what licenses its negatives**; a control with
> only negative limbs proves a reader can refuse and nothing about what it can accept.
>
> ⚠ **`C25` IS REGISTERED HERE AND IS NOT IMPLEMENTED IN `controls()`.** The behaviour was measured
> by the supervisor's rehearsal lane across eight scenarios and found **SOUND**; implementing it
> would edit `cases/M6SR/analyse_m6sr.py`, **whose blob sha this same amendment pins in §18.3.1.**
> **A document cannot pin a blob and change it in the same breath** — that is the rot Ruling 2
> exists to stop. **The implementation is the supervisor's to order, in an amendment that re-pins.**

### 18.7 CARRIED FORWARD, **NOT REPAIRED** — ITEMS 25 AND 27, ON THE SUPERVISOR'S EXPRESS INSTRUCTION

- **ITEM 25.** §8.1 carries **four numerals for a two-component vector and none of the four is the
  formula's value**: table `285.221` / `15.249`, prose `285.2721` / `15.2494`, formula
  **`285.2720289804489`** / **`15.250046752474487`**. **The prose misses too** —
  `285.679356·sin(3.06°) = 15.2500468`, not `15.2494`. **RECORDED, NOT REPAIRED.** The writer
  already emits the formula's vector — `internalField uniform (285.2720289804489
  15.250046752474487 0.0)` — read back from disk by control `W3` (§17.5.2, `CH9`).
- **ITEM 27.** §4.5's RMS is **185 of 271 taps = 68.27 % upper-surface** (23/11 on sections 1–4,
  31/14 on 5–7). *"Symmetric, so not a bias"* is **right about the COMPARISON and silent about the
  CURVE**: the RMS a section contributes is **two-thirds an upper-surface statistic**.
  **GRADED CHANNEL. RECORDED. NOT TOUCHED.** `set_to_set_assignment()` is byte-unchanged.

### 18.8 🔴 FIVE FURTHER ITEMS — THE SIXTEENTH PASS. **ITEMS 28 AND 30 ARE UNRUNNABILITIES, AND 30 IS HIDDEN BEHIND 28**

**The supervisor instructed this lane to assume a sixteenth item existed and to look for it. There
are five. Recorded, NOT repaired.**

| # | what cannot be satisfied | measured basis | consequence |
|---|---|---|---|
| **28** 🔴 | **`run_in_container()`'s docker invocation is BROKEN on exactly the branch this box takes.** | `run_m6sr_b5.sh` selects `DRUN="docker"` when bare docker works and `DRUN="sg docker -c"` otherwise, then writes `$DRUN "docker run --rm … "`. On the **bare** branch that expands to `docker "docker run --rm …"` — one argument. **Reproduced with the exact expansion and a harmless container: `rc=1`, `docker: unknown command: docker docker run --rm …`. CONTROL: the identical string through the `sg docker -c` branch returns `rc=0` and `INSIDE_OK`.** On this box `BARE_RC=0`, so the broken branch is the one taken. | **The driver is correct only on a box where docker is NOT directly reachable.** It **fails closed** — `inner` reads `ABSENT` and the driver aborts at exit 6 with no spend — so this is an **unrunnability, not a wrong answer.** **NOT REPAIRED: changing how the solve step invokes docker is a change to the launch path and is the supervisor's.** This amendment's own new code deliberately uses a different helper (`docker_q`, argv-passing with `printf %q` on the `sg` branch) and says so in the file. |
| **29** | **`M6SR_RUN_ROOT` is a second, independent env-var divergence of item 26's class, and it appears NOWHERE in this registration.** | `run_m6sr_b5.sh:87` honours it; the comparator reads **0** `os.environ`/`getenv` (planted control: the same reader returns 1 elsewhere). | **REGISTERED AND REFUSED (§18.6, exit 9).** Recorded as an item because the class — *an environment variable can change what the freeze pinned* — was found **twice**, and finding it twice is the finding. |
| **30** 🔴 | **`B4`'s `checkMesh` CANNOT WRITE ITS LOG, and the defect is HIDDEN BEHIND ITEM 28.** | The driver creates `$CASE` as the host user (**measured `775 ubuntu:ubuntu`**) and runs the container as **`-u 1002:1002`**. Measured on the pinned image with the driver's own mount and workdir: `echo … > RC_probe.txt` in `/case` returns **`Permission denied`, inner rc 1**. **CONTROL: the identical write after `chmod 777` returns inner rc 0 and leaves a file owned by `1002:1002`.** The driver's `chmod -R 777 "$CASE"` runs **in the `solve` phase only**, *after* `stage`. | **In the `stage` phase the container can write neither `log.checkMesh` nor `RC_checkMesh.txt`**, so `inner` reads `ABSENT` and the driver aborts at exit 6. **Gate A reads its named numeric maxima off `log.checkMesh` and §5 rules that an absent log "never reads clean" — so Gate A is unreachable.** 🔴 **This is INDEPENDENT of item 28 and is MASKED by it: fixing 28 does not fix 30, and today 28 fails first so 30 has never been observed.** **NOT REPAIRED.** |
| **31** | **The container carries MORE `rhoSimpleFoam` binaries than item 26 counted, and one more OpenFOAM-family tree.** | Item 26 recorded *"`OpenFOAM-v2506` **and** `OpenFOAM-AD`"*. Measured inside the pinned image: `/home/dafoamuser/dafoam/OpenFOAM/` holds **`OpenFOAM-v2506`, `OpenFOAM-AD`, `Hisa4DAFoam`, `ThirdParty-v2506`, `sharedBins`, `sharedLibs`**, and `OpenFOAM-AD` ships **`platforms/linux64GccDPInt32OptADF/bin/rhoSimpleFoam` AND `platforms/linux64GccDPInt32OptADR/bin/rhoSimpleFoam`**. With the box's native `openfoam2606` binary that is **four `rhoSimpleFoam` executables reachable from this box, three of them inside the pinned image.** | **A digest pin alone would NOT have separated them — all three live in the pinned image.** This is why §18.2's refusal also pins the **resolved path** and the **binary's sha256**, and why `PATH` resolution is measured rather than assumed. **Recorded so item 26's "two trees" is not carried forward as the count.** |
| **32** | **§9's frozen path table registers TWO executables and the ladder now runs SEVEN.** | §9's table names `analyse_m6sr.py` and `build_m6sr_l1.sh`. Also executed or depended on: `write_m6sr_case.py`, `run_m6sr_b5.sh`, `scripts/residual_max_over_equations.py`, `scripts/verify_agard_ar138_table_b1_1.py`, `scripts/check_comparator_freeze.py`. **All seven are pinned by blob sha in §18.3.1 — five as registered §9 paths, two as the gap.** | **Adding a path to §9's frozen table is a FREEZE question and is the supervisor's.** A lane pins shas and reports; it may not extend the grading-path table. |

**AND ONE THING CHECKED AND FOUND SOUND, REPORTED BECAUSE A PASS THAT IS NEVER STATED IS
INDISTINGUISHABLE FROM A CHECK NEVER MADE.** Standing rule 4 names **`0/T`** as the age-guard datum
for the *thermal* family; this ladder uses **`0/U`**. Measured: `analyse_m6sr.py:1311` documents
`0/U` as the datum, and `write_m6sr_case.py:502` writes the seven `0/` fields in the order
`p, T, nut, k, omega, alphat, U` — **`U` last, with an explicit `InternalDefect` raise if that
order does not cover the field set.** **Producer and reader agree, and the datum is written last.
No defect.**

### 18.9 COST — RULE 12, AND NONE OF IT IS LADDER COMPUTE

**No step of §2.4's cost table was run and `verification/runs/M6SR_runs` does not exist.** What this
amendment spent: host arithmetic and read-only inspection of already-existing artifacts; **five
read-only `docker run --rm` probes** on the pinned image and on `alpine:latest` (no solver, no
mesh, no solve); **six end-to-end rehearsals of `run_m6sr_b5.sh` into a SCRATCH run root**, each of
which refused at exit 7, 8 or 9 before staging a mesh; and **two runs of the comparator's
`--controls`** (10 wall s the pair). **≈ 6 core-min at 1 rank, and it is an ESTIMATE from this
session's own wall clock, NOT a measurement read from a run log** — no run log exists for it and
inventing one would be worse than saying so. **Derived at the owner-stated `c7a.4xlarge`
$0.0513/core-h: ≈ $0.0051 — DERIVED, REPORTED-BY-OWNER, never measured, because the box cannot read
its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5).

**TWO NEW UNBUDGETED STEPS, NAMED ON THEIR OWN LINES AND NOT FOLDED INTO ANY REGISTERED ROW**
(§9.3, `COMPUTE_BUDGET_CHARTER.md` §6), exactly as the driver already treats `B3s`:

| step | what | measured | status |
|---|---|---|---|
| **`B5p`** | the solver-pin preflight (`docker inspect` + one probe container) | **1 wall s at 1 rank ≈ 0.017 core-min** per level | **UNBUDGETED** — §2.4 has no row |
| **`B5g`** | the grading-path rehearsal (`--controls` under both interpreters) | **10 wall s at 1 rank ≈ 0.167 core-min** per level | **UNBUDGETED** — §2.4 has no row |

**Together ≤ 0.19 core-min per level, ≤ 0.55 core-min across the ladder — 0.09 % of §2.4's 615.24
— against the 607.63 core-min an ungradable solve would have wasted.** **§2.4's `est ≤ cap` table
is untouched; no cap is raised to accommodate these and they are not absorbed into any ratio.**

**§9.3's estimate-versus-actual row is NOT owed yet**, because no `B` step has completed. It falls
due at `B1`'s completion.

### 18.10 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves no gate, no threshold, no cap and no label.** Every change is a **pin** or a
   **refusal**, and neither is a gate. Not one number in §2.4, §5, §5.1, §7 or §10 is touched.
   **`X1`–`X6` stand**; `X7` is added as a **prediction**, which is not a verdict.
2. **It does NOT re-freeze.** `SUPERVISION_CHARTER.md` §3 check 4 belongs to the cfd supervisor and
   is **undischarged**. **Check 1 — the producer diff, read as a diff — is likewise the
   supervisor's**, and the diff is filed at
   **`cases/M6SR/AMENDMENT_12_SOLVER_PIN_AND_GRADING_GATE.diff`**.
3. **It does NOT add a path to §9's frozen table** (item 32). It pins the shas of all seven
   executables and reports which two are unregistered.
4. **It does NOT move the semispan.** `B_SEMI_M = 1.19676` is byte-unchanged and the seven station
   coordinates of §17.3.3 are byte-unchanged. `1.1963` is registered **beside** it, not instead.
5. **It does NOT touch `cases/M6SR/analyse_m6sr.py` or `cases/M6SR/write_m6sr_case.py`** — both are
   pinned here and neither is edited. **`C25` is registered and NOT implemented, and says so.**
6. **It does NOT repair items 25, 27, 28, 30, 31 or 32.** Two are the supervisor's express "carry,
   do not repair"; the rest are new and a lane records rather than repairs.
7. **It does NOT loosen `C12`.** `X4` stands; the new gate refuses **because** `C12` does not fire.
8. **It does NOT enqueue anything and launched NO compute.** `verification/queue/cfd/` is a live
   launch path and this lane wrote nothing into it. No `B` step of §2.4 ran.
9. **It does NOT change `/home/ubuntu/certonomous-runs/`**, which was read only — verified, nothing
   under it has an mtime inside this session — nor `docs/LAB_STATE.md`.
10. **It claims no verdict of the fixed vocabulary for any gate.** Every `PASS` / `GATE FAIL` /
    `NOT A RESULT` above is inside a registered **PREDICTION** or a **quotation**. **No solver has
    run.**
11. **SUBMISSIONS REMAIN PARKED (rule 7). Nothing left the box (rule 8).**

> **WHAT M6SR CAN AND CANNOT DO AFTER THIS AMENDMENT, STATED ONCE, PLAINLY.**
> **CAN:** run `B1`–`B3`; refuse at zero solver cost on a wrong image, a wrong solver binary, a
> failing grading path or a wrong run root; and produce, once `X4` and items 28 and 30 are
> resolved, everything §17.9's closing block lists.
> **CANNOT:** launch `B5` at all while **`X7`** stands — the pre-launch gate refuses on `C12`.
> **CANNOT:** reach `B4`'s `log.checkMesh`, and therefore Gate A, while **item 28** stands
> (docker invocation) — and **item 30** (container cannot write the case directory in `stage`)
> waits behind it.
> **CANNOT:** grade Gate P's per-station channel — **`X1`**; print a Gate P verdict beside a Gate G
> band — **`X3`**; `GF2` and `GF4`-semispan are still predicted `GATE FAIL` — **`X2`**.
> **THE SOLVER BINARY IS NO LONGER UNPINNED. Item 26 is CLOSED by §18.2.**

### 18.11 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.3 → v1.4 (amendment 12, pre-compute). The frozen file was NOT edited; this section is
APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10,
§16.9 and §17.12 give: editing it would change a line above §15 and falsify those sections' own
assertions, on which other records depend. **The bump is recorded HERE, which is where rule 6 puts
it. The supervisor may restate the version in the header at the re-freeze, which is a status flip
they own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–3208** of this file — the whole of it up to and including
§17.12's closing line, and therefore the whole of §15's guaranteed range 1–2022, §16's guaranteed
range 1–2229 and §17's guaranteed range 1–2690 — are **byte-identical** before and after this
append, both rendering to sha256
**`20753aff5fb81868ce6d0529aecdf1df63f03f5d037d87bfcd8609071eb4280e`**. Other records cite this
document **by line**, and at least one such citation sits inside an executable check, so this is a
guarantee and not a courtesy.

---

## 19. AMENDMENT 13 — 2026-09-04, **PRE-COMPUTE**. THE ITEM THAT DID **NOT** FAIL CLOSED, THE STEP ORDER, AND THE RE-PIN

**This section is APPENDED AT THE FOOT. No line above it is touched** (rule 6, §18.11's own
pattern). It carries: **item 34**, a silent corruption of a graded artifact, **REPAIRED**;
**item 33**, the step order, **RULED, with no registered number moved**; the **re-pin** of
`run_m6sr_b5.sh`, whose §18.3.1 pin is stale by construction; and **three further items, 35–37,
all in `build_m6sr_l1.sh`, REPORTED AND NOT REPAIRED**.

### 19.0 THE LAWFULNESS CONDITION, AND HOW IT WAS CHECKED — **NOT ASSERTED, PLANTED**

Rule 2 permits amendment **before first compute**, and closes gates after it. The condition is that
**`verification/runs/M6SR_runs` does not exist**, and it is checked with a **plant at the exact
searched path**, because an absence reported by a reader never shown able to report a presence is
not evidence (rule 3):

| # | act | the reader's answer |
|---|---|---|
| 1 | before the plant | `verification/runs/M6SR_runs` reads **ABSENT** |
| 2 | **`mkdir verification/runs/M6SR_runs`** — the plant, at the exact searched path | reads **PRESENT** — *the reader can see a non-absent run root* |
| 3 | `rmdir` the plant | reads **ABSENT** again |

**Corroborated by three further readers at the same path after removal:** `ls -d` →
`No such file or directory`; `find verification/runs -maxdepth 1 -name 'M6SR_runs'` → **empty**;
`git ls-files` → **empty**. ⚠ **The plant is `mkdir`/`rmdir` and `rmdir` REFUSES a non-empty
directory**, so the control cannot destroy content by construction — that is why this shape was
chosen over any that could have removed a tree.

**Therefore: no `B` step of §2.4 has run, `B4`'s running ledger `$RR/B4_SPENT_COREMIN.txt` cannot
exist because its parent does not, and every change below is a PRE-COMPUTE change.**

### 19.1 THE NUMBERING, FIRST, BECAUSE TWO COUNTERS HAD SILENTLY COLLIDED

🔴 **This registration runs ONE GLOBAL item counter and §18.8 already spends 31 and 32.** The
supervisor's board, and the committed comments in `cases/M6SR/run_m6sr_b5.sh`, call the two new
findings "item 31" and "item 32" — **they are not §18.8's 31 and 32.** Numbered from this
document's own tail, as rule 11's discipline requires:

| board number | registration number | the finding |
|---|---|---|
| item 31 | **ITEM 33** | §8's case is written **after** `B4`, so `B4`'s `checkMesh` has no `system/controlDict` |
| item 32 | **ITEM 34** | the wrapper's redirect target **and** `B4`'s output file were the same path |
| — | §18.8's own **31** | the container carries more `rhoSimpleFoam` binaries than item 26 counted |
| — | §18.8's own **32** | §9's frozen path table registers two executables and the ladder runs seven |

**Both numbers are carried in the driver's and the check suite's own headers so neither reader is
stranded.** Everything below uses the **registration** numbering.

### 19.2 🔴 ITEM 34 — A **SILENT CORRUPTION OF A GRADED ARTIFACT**. **REPAIRED.**

#### 19.2.1 THE DEFECT, STATED EXACTLY

`run_in_container()` sent the **outer wrapper's** stdout+stderr to `$CASE/log.$tag`. For the `B5`
steps the tag has a name of its own (`log.B5a`) and the registered artifacts are written separately.
**For `B4` the tag IS `checkMesh`**, so the wrapper's redirect target and the inner command's output
file were **THE SAME PATH — `$CASE/log.checkMesh` — and that is the file Gate A grades.**

The host shell opens it with `O_TRUNC` and **holds the fd at offset 0** for the life of the docker
client, while the container opens the **same inode** through the bind mount with its own fd.
Anything the client then writes — its own diagnostics, or the container's **unredirected stdout,
which the client streams back** — lands **at offset 0** and overwrites the head.

#### 19.2.2 MEASURED, ON THE REAL PINNED DIGEST, NOT ARGUED

| control | what was done | what came back |
|---|---|---|
| synthetic | container wrote 65 bytes to `/case/log.checkMesh` through the mount; the client then emitted a 20-byte line | file **65 bytes**, **first 20 REPLACED**, remainder byte-intact |
| **real `checkMesh`, L3 mesh** | the same shape, `checkMesh -constant > log.checkMesh 2>&1` plus one host-visible line | `log.checkMesh` **3330 bytes** — *the same size a clean run produces* — with the first 20 bytes of the OpenFOAM banner replaced |

🔴 **AND THE CORRUPTED FILE GRADES.** `analyse_m6sr.read_checkmesh()`, the real Gate A reader, run
on that exact file:

| what Gate A reads | value off the CORRUPTED file | Gate A's disposition |
|---|---|---|
| `state` | **`READ`** — not `ABSENT` | §5's *"an absent log never reads clean"* **does not fire** |
| `max_non_orthogonality_deg` | **61.49376508** | `A1` threshold 70 → **inside** |
| `max_skewness` | **2.306553794** | `A2` threshold 4 → **inside** |
| `max_aspect_ratio` | **608.2069422** | `A3` advisory 1000 → **inside** |
| `Mesh OK.` / `End` | **both present** | — |

**`read_checkmesh` sets `state` from file EXISTENCE alone and then whole-file-regex-searches for the
maxima, which live near the END of a `checkMesh` log.** The head overwrite is therefore **invisible
to every check Gate A makes.** ⚠ **Items 28, 30 and 33 all fail closed at exit 6. This one would
have produced a plausible, gradeable, WRONG file and nothing would have announced it.**

✅ **IT NEVER FIRED.** No run root exists; the docker client emitted nothing on the successful
probes taken in Amendment 12. **This is PREVENTION, not the repair of a live corruption**, and it is
recorded as such rather than as a rescue.

#### 19.2.3 THE REPAIR — **IMPOSSIBLE, NOT MERELY UNLIKELY**

The container's **only** view of this filesystem is `-v "$CASE":/case`. A path that is not under
`$CASE` therefore **cannot be opened from inside the container by any name**, whatever a present or
future tag is called. The two writers are separated by **MOUNT TOPOLOGY, not by a naming
convention**:

1. **The wrapper's log leaves the mount**: `$RR/_wrapper_logs/$LEVEL/log.$tag`.
2. **And it is ENFORCED, not intended.** `run_in_container()` now **REFUSES at exit 6, before the
   container starts**, if that target is `$CASE` or anything under it. `$CASE` is the literal `-v`
   source on the next lines, so the guard tests the mount and not a copy of it. **The class is
   closed for every future tag, not just for `checkMesh`.**
3. **A SECOND, INDEPENDENT GUARD at `B4`**: the driver asserts that `log.checkMesh` **begins with
   the OpenFOAM banner** (`/*-`) and refuses otherwise. ⚠ **It reads the HEAD and not the numbers,
   because "the maxima still parse" is exactly what let this through.** It is safe as a check only
   because the image is pinned by digest — the banner is fixed by the pin; under an unpinned image
   it would be a guess, and that is stated in the driver.
4. `STEP_RC.txt` now records **`wrapper_log=<path>`** per step, so the wrapper's output is findable
   and a reader is never left inferring where it went.

**MEASURED AFTER THE REPAIR, same real `checkMesh`:** `log.checkMesh` **3330 bytes with its head
`/*------…` intact**, and the host-side 20-byte line **alone in the wrapper log**, outside the mount.

✅ **`cases/M6SR/build_m6sr_l1.sh` was checked and is ALREADY immune for exactly this reason** — it
mounts `$RR/$LEVEL/work` and writes its wrapper log to `$RR/$LEVEL/log.$tag`, **one level above the
mount**. Reported because a pass that is never stated is indistinguishable from a check never made.

#### 19.2.4 THE CONTROL THAT WOULD HAVE CAUGHT IT — `T5` IN `cases/M6SR/check_m6sr_launch_path.sh`

**Every assertion is on the HEAD.** A control that asked *"do the maxima still parse?"* is precisely
the control this defect passes.

| limb | what it does | what makes it evidence |
|---|---|---|
| **T5a** | deliberately re-creates the **pre-repair** shape on the pinned digest and REQUIRES the head to come back **corrupted** | **the known-positive, and here the known-positive IS the corruption.** If the head comes back intact the suite **REFUSES (exit 2)** — a reader not shown able to see the corruption cannot certify its absence |
| **T5a'** | runs the **real** `analyse_m6sr.read_checkmesh()` on that corrupted file | prints `READ｜61.49376508｜2.306553794` — **the danger is demonstrated with the grading reader, not asserted** |
| **T5b** | runs the driver's **own extracted** `run_in_container` with tag `checkMesh`, inner command writing the log **and** emitting a host-visible line | **non-vacuity first**: the planted host-side line must be **found in the wrapper log** or the suite REFUSES. Without that, *"the head is intact"* is a statement about a collision that never happened |
| **T5b'** | the graded file's head | **FAILS if the first bytes are overwritten** |
| **T5b''** | the planted line must appear **nowhere** in the graded artifact's first 400 bytes | — |
| **T5b'''** | the graded file must still parse as a real `checkMesh` log | stops the head test passing on an empty file |
| **T5b''''** | the wrapper-log path, **read from the driver's own `STEP_RC.txt`**, must be outside `$CASE` | the suite never recomputes that path: a suite that did would stay green after the driver moved it |
| **T5c** | forces the driver's own computed wrapper target back inside the mount and requires **exit 6** and the refusal text | **the guard is EXERCISED, not grepped** |
| **T5d/d'** | the comment-stripped **CODE** must no longer carry `> "$CASE/log.$tag"` and must carry exactly one out-of-mount redirect | — |
| **T5e** | extracts the driver's **own** head-reader line and runs it on **both** files | separates corrupt (`M6S`) from clean (`/*-`) — **non-vacuous in both directions** |

**Suite result: 25 checks, 25 PASS, 0 FAIL, rc 0.**

#### 19.2.5 THE MUTATION BATTERY — **EIGHT MUTATIONS, EIGHT KILLED**

Run against an **isolated copy** of `cases/M6SR/`, so the shared worktree was never mutated. Control
first: the unmutated copy returns **25 PASS / 0 FAIL / rc 0**.

| # | mutation to `run_m6sr_b5.sh` | outcome |
|---|---|---|
| M1 | wrapper redirect reverted to `> "$CASE/log.$tag"` | **KILLED** — rc 2, the planted host-side write is no longer in the wrapper log |
| M2 | the in-mount refusal deleted | **KILLED** — rc 1, `T5c` |
| M3 | the `B4` head guard deleted | **KILLED** — rc 2, *"expected exactly ONE code line matching `CM_HEAD=…`, found 0"* |
| M4 | `wdir` pointed back inside `$CASE` | **KILLED** — rc 2, the guard fires and `T1`'s plant is never written |
| M5 | `head -c 3` weakened to `head -c 0` | **KILLED** — rc 2, by the **coupling** (the driver's line changed), not by the head test's behaviour. **Stated, because the two are different kills** |
| M6 | `wrapper_log=` dropped from `STEP_RC.txt` | **KILLED** — rc 2, `T1e`/`T1f` fail and `T5b` cannot find the plant |
| M7 | `chmod g+rwX "$CASE"` deleted | **KILLED** — rc 2, *"expected exactly ONE code line matching `chmod g+rwX "$CASE"`, found 0"* |
| M8 | `--group-add "$HOST_GID"` deleted | **KILLED** — rc 2, the coupling assertion |

#### 19.2.6 ⚠ AND A DEFECT IN THE CONTROL SUITE'S **OWN REFUSAL MECHANISM**, FOUND BY READING **HOW** THREE OF THEM DIED

**The suite's `refuse()` did not refuse.** `refuse` writes its message and calls `exit 2`; inside a
command substitution — `X=$(extract_line …)` — that exits **only the subshell**, and because the
message went to **stdout** it was **CAPTURED AS X**. **MEASURED:** an unmatchable extraction
returned rc 2 **and** the value `REFUSE: expected exactly ONE code line matching …`, and the parent
carried on.

**CONSEQUENCE, AND IT IS NOT COSMETIC.** Three mutations (M3, M5, M7) that **DELETED** a line from
the driver were still killed — but **downstream**, by an `eval` of that captured refusal text, and
the transcript then read *"the driver's head reader did not separate them"* when the truth was
*"the driver's head reader is **gone**"*. ⚠ **A control that fails for the wrong reason names the
wrong defect, and the next reader debugs the wrong file.** It affected **three call sites**, two of
them written by the previous lane (`HOST_GID_LINE`, `CHMOD_LINE`) and one by this one (`CM_LINE`);
`CHMOD_LINE`'s had **no following guard at all**, so a deleted `chmod` would have surfaced as an
unrelated permission failure two tests later.

**REPAIRED:** refusals go to **stderr**, where they can never become a value; every extraction is
`… || exit 2`; and a new **`T0`** plants an unmatchable extraction and requires **rc 2 AND no
value** before anything rests on the mechanism — **rule 3 applied to the machinery rather than to
the measurement.** **DEMONSTRATED:** after the repair M3, M5 and M7 refuse with the *correct*
diagnosis, naming the deleted line.

🔴 **This is L-478's family — a name is not a control — in a third place: a refusal that is not a
refusal.** §18's record already carries the first two (an assertion satisfied by the driver's own
comment quoting the fix; `timeout … command docker …` returning **rc 127, not 124**, so a cap
overrun would not have read as one). **All three are the same shape: the control existed, was read,
and did not do what its name says.**

### 19.3 ITEM 33 — THE STEP ORDER. **RULED — AND NO REGISTERED NUMBER MOVES.**

#### 19.3.1 THE DEFECT, MEASURED

With items 28 and 30 repaired, `B4`'s `checkMesh` reaches the container and returns **inner rc 1**:
`FOAM FATAL ERROR: cannot find file "/case/system/controlDict"`. §8's case is written by
`cases/M6SR/write_m6sr_case.py`, which the driver invokes in the **solve** phase — **after `B4`**.
✅ **It fails closed at exit 6, and the same step against a case written first returns inner rc 0
with `Mesh OK.` — so nothing else stands behind it.**

#### 19.3.2 🔴 THE REGISTERED TABLE HAS **NO STEP** FOR WRITING §8's CASE — SO THIS IS A **PLACEMENT**, NOT A REORDER

**§2.4's table orders `B0` … `B6` and contains no row for writing the case at all.** §9's frozen
path table registers **paths, not an order**, and does not register `write_m6sr_case.py` (§18.8's
own item 32). The `stage`/`solve` split is the **driver's** structure, not this registration's.
**So there is no registered step to reorder: there is a step that was never placed, and the driver
placed it late.**

> **RULED (pre-compute): §8's case is written BEFORE `B4`, as step `B3c`, ordered
> `B3`/`B3s` → `B3c` → `B4` → `B5`.** `B3c` is **UNBUDGETED and named on its own line**, exactly as
> §18.9 already treats `B3s`, `B5p` and `B5g`. **MEASURED: 1.119 wall s at 1 rank = 0.019 core-min
> per level, ≤ 0.06 core-min across the ladder** — 0.01 % of §2.4's 615.24.

#### 19.3.3 ⚠ **STATED PLAINLY, BECAUSE THE SUPERVISOR ASKED IT DIRECTLY: NOTHING MOVES.**

**No gate, no threshold, no cap, no label and no estimate moves.** §2.4's cost table is unchanged in
**every cell, including the TOTAL row** (est ≈ 615.2, cap 1,903.0). `B4` keeps est **0.14** / cap
**2.0**; `B5a`/`B5b`/`B5c` are untouched; §5's Gate A thresholds (70°, 4, advisory 1000, ratio 4,
64) are untouched; no verdict label changes.

**THE ALTERNATIVE THAT WAS NOT TAKEN, AND WHAT IT WOULD HAVE COST, SO THE CHOICE IS VISIBLE.**
`B3c` could instead be given a *budgeted row* in §2.4. That would move the **TOTAL** row — est
615.2 → 615.3, cap 1,903.0 → 1,904.0. ⚠ **That is a decision, not a consequence of the reorder, and
it is the supervisor's.** This section takes the option that moves nothing.

#### 19.3.4 ⚠ `B4` NEEDS THE **WHOLE** §8 CASE, NOT "a controlDict" — MEASURED BY ABLATION

Three successive refusals on the pinned digest, each naming the next missing file:

| case contents | `checkMesh` result |
|---|---|
| mesh only | `cannot find file "/case/system/controlDict"` |
| mesh + a hand-written minimal `controlDict` | `FOAM FATAL IO ERROR` — the dictionary is not a valid `FoamFile` |
| mesh + §8's `controlDict` alone | `Cannot open include file "/case/system/sampleDict"` — §8's `controlDict` `#include`s the function-object dict |
| mesh + §8's `controlDict` + `sampleDict` | `cannot find file "/case/system/fvSchemes"` |
| **mesh + the full §8 case** | **inner rc 0, 3330 bytes, `Mesh OK.` / `End`** |

**So `B3c` is the complete writer invocation** (`--selftest` then `--case … --level …`), **not a
partial one.** The registration says so here rather than leaving a future lane to rediscover it.

#### 19.3.5 🔴 THE ONE CONSEQUENCE FOR GATE A's NUMBERS — MEASURED, NOT ASSUMED

**§8's `controlDict` sets `writePrecision 10`, and that changes what `checkMesh` PRINTS.** Against
the **independent** prior `checkMesh` of the **same** `polyMesh`, run on 2026-08-08 by a different
campaign with no §8 case —
`verification/runs/MESH_AUDIT_runs/2026-08-08/A3-onera-m6-adjoint-coarse__constant__polyMesh.log.checkMesh`:

| Gate A input | 2026-08-08, **no §8 case** | this lane, **case written first** | max relative difference |
|---|---|---|---|
| `max_non_orthogonality_deg` | 61.4938 | 61.49376508 | 5.68e-07 |
| `max_skewness` | 2.30655 | 2.306553794 | 1.65e-06 |
| `max_aspect_ratio` | 608.207 | 608.2069422 | 9.50e-08 |
| `min_volume` | 1.17547e-10 | 1.175465721e-10 | 3.64e-06 |
| `max_volume` | 0.944185 | 0.9441848797 | 1.27e-07 |
| `boundary_openness_max_abs` | 8.22572e-16 | 8.225723872e-16 | 4.71e-07 |
| `n_cells` / `n_regions` | 99840 / 1 | 99840 / 1 | **exact** |

**Every value agrees to all six significant figures the earlier log printed; the largest relative
difference is 3.64e-06 and is pure print-rounding.** ✅ **No Gate A input moves. `B4`'s log will
simply carry more digits than the 2026-08-08 audit's, and that is recorded here so nobody reads the
extra digits as a different mesh.**

⚠ **AND WHAT COULD NOT BE SHOWN.** The clean ablation — *"the case files do not influence the
metrics"* — **cannot be run by subtraction**, because `checkMesh` refuses to start without §8's
case (§19.3.4). The evidence above is an **independent-instrument agreement**, not an ablation, and
it is labelled as such. The mesh bytes are identical by `cp -a` from one read-only source, and the
driver publishes `points_stream.sha256` at `stage`, **before** the case is written, so `A5`'s
family-identity proof is taken on the mesh independently of the case either way.

#### 19.3.6 THE DRIVER IS **NOT** CHANGED BY THIS SECTION

`cases/M6SR/run_m6sr_b5.sh` still invokes the writer in the `solve` phase, and it still **writes no
case file of its own** — §1's *"there is ONE writer and it is that one"* is byte-unchanged.
**Implementing the order is the supervisor's to authorise**; a lane registers the ruling and reports
the measurement. **Until it is implemented, `B4` fails closed at exit 6 and Gate A is unreachable,
exactly as §18.10's closing block already states.**

### 19.4 THE RE-PIN — §18.3.1's `run_m6sr_b5.sh` ROW IS **STALE BY CONSTRUCTION** AND IS STRUCK BY QUOTE

✅ **The prior lane was right not to re-pin it in the same commit that changed it** — §18.6's own
ruling, *"a document cannot pin a blob and change it in the same breath."* The pin is re-taken here,
in the amendment that the supervisor ordered for the purpose.

#### 19.4.1 STRUCK

> ~~*"| **`cases/M6SR/run_m6sr_b5.sh`** (the sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam` and `log.checkMesh`) | **`44fae79bbae918ae101d7d4a9b8ad96bdef66734`** | `5d0bc9df92f272a5d1a22e43708b8cd386f08e352fa282993e65c7d5072bd579` | 561 | **NOT in §9's table**; **CHANGED BY THIS AMENDMENT** (§18.2.3, §18.5, §18.5.1, §18.6) |"*~~

**STRUCK.** The file moved twice after that pin was written: to **`ab3b1ab2d04dba0bb047c42197aa188a981a570a`**
at commit **`5cf8a009`** (items 28 and 30 repaired), and again here. **§18.3.1's row is not edited in
place** — rule 6 — **and the current pin is the table below.**

#### 19.4.2 THE CURRENT PINS

| path | git blob sha | sha256 of the file | lines | status |
|---|---|---|---|---|
| **`cases/M6SR/run_m6sr_b5.sh`** (sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`) | **`6e12307edfeeabd40effc9a5eedc6176fab99212`** | `a9f1d3765862ea4a9eef09971eab60df5f2a65443e02ac8a182a869fc29eec7d` | **795** | **NOT in §9's table**; **CHANGED BY THIS AMENDMENT** (§19.2.3) |
| **`cases/M6SR/check_m6sr_launch_path.sh`** (the launch-path control suite; **NEW at `5cf8a009`**) | **`9b8d44ce7c68a0728db80cc83fb11dbeb77d945d`** | `0da8aad32983d6b737de346db5b6fd1d71e96c64b014d56a51ce1f495ca9372c` | **367** | **NOT in §9's table** — see §19.4.3 |
| **the superseded intermediate**, recorded so the chain is readable | `ab3b1ab2d04dba0bb047c42197aa188a981a570a` | — | 561 → 631 | **`5cf8a009`**, superseded here |

**Both shas were re-derived with `git hash-object` on the working tree and RE-VERIFIED INSIDE THE
SAME SHELL INVOCATION AS THE COMMIT that carries this section, with the commit ABORTING if either
had moved.** ⚠ **It has moved mid-commit before** — §18.3.1 records `0b3b73bb…` → `44fae79b…` when a
peer's edit landed in the shared worktree — **so the abort is a live guard, not a formality.**
§18.3.1's other five rows are **not** re-taken here and stand as pinned.

#### 19.4.3 SHOULD `check_m6sr_launch_path.sh` GO INTO §9's TABLE? — **THE LANE'S ANSWER IS NO, AND THE RULING IS THE SUPERVISOR'S**

§18.8's own item 32 rules that *"adding a path to §9's frozen table is a FREEZE question and is the
supervisor's. A lane pins shas and reports."* **Reported, with a recommendation and its reason:**

- **§9's table is the GRADING path.** `check_m6sr_launch_path.sh` **grades nothing**, produces no
  artifact any gate reads, and writes only into a `mktemp` scratch tree it deletes. Putting it in
  §9 would make the grading table mean two different things.
- **But it MUST be pinned, and it is, above.** A control suite that can be silently edited is a
  green with no content — and this suite's own history proves the point twice over (§19.2.6, and
  §18's comment-satisfied assertion). **Pinned in the gap table, not in §9.**
- **The lane's recommendation: NO to §9; YES to a standing pin.** The supervisor rules.

### 19.5 🔴 THREE FURTHER ITEMS — **ALL IN `cases/M6SR/build_m6sr_l1.sh`** — ITEMS 35, 36, 37. **REPORTED, NOT REPAIRED.**

**The supervisor asked whether a FIFTH failure sits behind 33 and 34. There is one, and it is not in
the file this pass repaired.** `build_m6sr_l1.sh` is the sole producer of the **L1 mesh** — Gate A's
third level, `A4`'s cell-count ratios, `A7`'s 24,960-face surface, and every `B5c` core-minute.

| # | what cannot be satisfied | measured basis | consequence |
|---|---|---|---|
| **35** 🔴 | **ITEM 28's EXACT DEFECT, UNREPAIRED, IN THE L1 BUILD DRIVER.** `build_m6sr_l1.sh:105` selects `DRUN="docker"` when bare docker works, then line 118 writes `timeout … $DRUN "docker run …"` — the whole command as ONE ARGUMENT. | **Reproduced with the driver's exact expansion on the pinned digest: rc 1, `docker: unknown command: docker docker run --rm --name m6sr_probe_… `, and `RC_probe.txt` ABSENT so `inner` reads ABSENT.** CONTROL: the identical string through `sg docker -c` returns **rc 0 / `INSIDE_OK`**. On this box `BARE_RC=0`, so the broken branch is the one taken. | **`B1`, `B2` and `B3` cannot run**, so the L1 mesh cannot be built, so Gate A has no third level and `B5c` — **543.13 core-min of est, 88 % of the ladder** — is unreachable. **It FAILS CLOSED at exit 6 and has never fired: no run root exists.** **NOT REPAIRED — the same class the supervisor ruled was theirs in §18.8, in a second file, and its blob is pinned by §18.3.1.** |
| **36** | **AMENDMENT 12 RULING 1's IMAGE PIN LIVES ONLY IN `run_m6sr_b5.sh`.** `build_m6sr_l1.sh:53` reads `IMG=${M6SR_IMAGE:-dafoam-idwarp-rot:v1}` and **never resolves or checks a digest**. | Measured by inspection of the whole file: **zero** occurrences of a digest, `RESOLVED_DIGEST` or an image refusal. | **`$M6SR_IMAGE` can still SELECT the image for `B1`–`B3`** — the steps that BUILD the mesh Gate A grades — while §18.2's refusal protects only the solve. **The instrument is pinned for the solver and unpinned for the mesh.** |
| **37** | **ITEM 29's CLASS, UNREPAIRED IN THE BUILDER.** `build_m6sr_l1.sh:49` honours `M6SR_RUN_ROOT`; §18.6's exit-9 run-root refusal exists **only** in `run_m6sr_b5.sh:401`. | Measured by inspection: the builder has no `M6SR_REGISTERED_RUN_ROOT` and no run-root assertion. | **The builder can be pointed at a tree the comparator will never read**, silently — producer and reader in different trees, which is exactly what §18.6 refuses on the solve side. |

✅ **AND ONE THING CHECKED AND FOUND SOUND, REPORTED BECAUSE A PASS NEVER STATED IS
INDISTINGUISHABLE FROM A CHECK NEVER MADE.** **Item 34 does NOT reach `build_m6sr_l1.sh`.** It
mounts `$RR/$LEVEL/work` and writes its wrapper log to `$RR/$LEVEL/log.$tag` — **outside the
mount** — and its one reader of a wrapper log (`grep -m1 'Total Faces:' … log.pyhyp`, line 213) is
reading the container's streamed stdout **by design**, from a file no container can write. **No
shared path exists in that file.**

### 19.6 CARRIED FORWARD FROM THE ITEMS 28/30 PASS, **NOT RE-LITIGATED**

- **Item 30's fix is narrow and correct**: `chmod g+rwX` on the **case directory only** — group
  only, not world, not recursive — plus **`--group-add $HOST_GID`**. `-u 1002:1002` is unchanged, so
  **uid 1002 keeps `dafoamuser` as its PRIMARY identity and every Amendment 12 pin measurement taken
  under that user still describes the running process.** `--user $(id -u):$(id -g)` was **rejected**
  because it changes the pinned invocation's user spec. **Both halves measured as necessary by
  negative controls** (`T3a`, `T3b`, `T3c`), and `T3c` shows the repair does not rest on this box's
  umask.
- ⚠ **A TRAP WORTH REGISTERING: `timeout` execs a *program* and cannot exec the shell builtin
  `command`**, so `timeout …s command docker …` returns **rc 127, NOT 124** — **it would not have
  read as a cap overrun**, and rule 12's *"an overrun stops the run"* would have been enforced by a
  code the driver does not treat as an overrun. The resolved binary is captured into `$DOCKER_BIN`
  and the cap was **re-measured as still biting: rc 124 on both branches** (`T2c`).

### 19.7 PRE-EXISTING, NAMED, AND **NOT ABSORBED BY THIS AMENDMENT**

**Phase `all` aborts at exit 8** because `C12` does not fire in `cases/M6SR/analyse_m6sr.py` at
`HEAD`, under both `python3` and `python3 -O`. **That is `X4` and `X7` working as registered** —
§18's pre-launch grading gate refusing at zero solver cost. **Reported; NOT repaired here.** It is
not a defect of the launch path and it is not this amendment's to close.

### 19.8 COST — RULE 12, AND **NONE OF IT IS LADDER COMPUTE**

**No step of §2.4's cost table was run and `verification/runs/M6SR_runs` does not exist** (§19.0,
planted). What this amendment spent, all at **1 rank**, counted rather than rounded:
**8 direct `docker run --rm` probes** on the pinned digest outside the suite (2 item-35 expansion
probes, 3 real `checkMesh` runs on the already-built L3 mesh, 3 ablation runs that refused);
**17 full runs of the control suite** (2 controls in the worktree, 1 isolated-copy control, and
**14 mutant runs** across two batteries — 6 before the refusal repair and 8 after — at **38 wall s**
measured for a full green run, less for the mutants that refuse early); the mesh copy-outs and
`write_m6sr_case.py` invocations those cases needed; and host arithmetic. **≈ 11 core-min at 1 rank,
and it is an ESTIMATE from this session's own wall clock,
NOT a measurement read from a run log** — no run log exists for it and inventing one would be worse
than saying so. **Derived at the owner-stated `c7a.4xlarge` $0.0513/core-h: ≈ $0.0094 — DERIVED,
REPORTED-BY-OWNER, never measured, because the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5).

**ONE NEW UNBUDGETED STEP, NAMED ON ITS OWN LINE AND NOT FOLDED INTO ANY REGISTERED ROW** (§9.3,
`COMPUTE_BUDGET_CHARTER.md` §6), exactly as §18.9 treats `B3s`, `B5p` and `B5g`:

| step | what | measured | status |
|---|---|---|---|
| **`B3c`** | §8's case written **before** `B4` (`--selftest` + `--case … --level …`) | **1.119 wall s at 1 rank = 0.019 core-min** per level | **UNBUDGETED** — §2.4 has no row, and §19.3.3 does not create one |

**≤ 0.06 core-min across the ladder — 0.01 % of §2.4's 615.24. §2.4's `est ≤ cap` table is untouched
and no cap is raised to accommodate it.**

**§9.3's estimate-versus-actual row is NOT owed yet**, because no `B` step has completed. It falls
due at `B1`'s completion — which **items 35–37 currently prevent**.

### 19.9 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves no gate, no threshold, no cap and no label.** §2.4's cost table is unchanged in every
   cell **including the TOTAL row**; §5's Gate A thresholds are unchanged; `X1`–`X7` stand.
2. **It does NOT re-freeze.** `SUPERVISION_CHARTER.md` §3 check 4 belongs to the cfd supervisor and
   is **undischarged**. **Check 1 — the producer diff, read as a diff — is likewise the
   supervisor's.**
3. **It does NOT add a path to §9's frozen table.** It pins `check_m6sr_launch_path.sh` in the gap
   table and recommends against §9 (§19.4.3). The ruling is the supervisor's.
4. **It does NOT change the driver's step order.** §19.3 RULES the order; implementing it is the
   supervisor's to authorise (§19.3.6).
5. **It does NOT touch `cases/M6SR/analyse_m6sr.py`, `cases/M6SR/write_m6sr_case.py` or
   `cases/M6SR/build_m6sr_l1.sh`** — all three are pinned by §18.3.1 and none is edited. Items 35,
   36 and 37 are **reported and not repaired**.
6. **It does NOT repair `C12`.** `X4` and `X7` stand; phase `all`'s exit 8 is the gate working.
7. **It launched NO ladder compute, enqueued nothing, and wrote nothing into
   `verification/queue/`.** `verification/runs/M6SR_runs` is **ABSENT**, re-verified with the same
   plant at the same path after every act above.
8. **It does NOT change `/home/ubuntu/certonomous-runs/`**, which was read only, nor
   `docs/LAB_STATE.md`.
9. **It claims no verdict of the fixed vocabulary for any gate.** No solver has run.
10. **SUBMISSIONS REMAIN PARKED (rule 7). Nothing left the box (rule 8).**

### 19.10 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.4 → v1.5 (amendment 13, pre-compute). The frozen file was NOT edited; this section is
APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10,
§16.9, §17.12 and §18.11 give: editing it would change a line above §15 and falsify those sections'
own assertions, on which other records depend. **The bump is recorded HERE. The supervisor may
restate the version in the header at the re-freeze, which is a status flip they own; a lane may
not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–3684** of this file — the whole of it up to and including
§18.11's closing line, and therefore the whole of §15's guaranteed range 1–2022, §16's 1–2229,
§17's 1–2690 and §18's 1–3684 — are **byte-identical** before and after this append, both rendering
to sha256 **`0b5ebed70a63647579174009ebe50dfa123940d2ceabcd62335542a1bcffaf45`**. Other records cite
this document **by line**, and at least one such citation sits inside an executable check, so this
is a guarantee and not a courtesy.

---

## 20. AMENDMENT 14 — 2026-09-04T1832Z. **ITEM 38 REPAIRED: THE L1 BUILD CHAIN NOW RUNS END TO END** — AND THE SEVENTEENTH PASS FINDS A DEFECT IN THE *CAP MECHANISM ITSELF*

**Drafted and applied by a cfd `lab-lane` on the cfd supervisor's ruling of 2026-09-04. THIS IS
NOT A FREEZE AND NOT A RE-FREEZE.** `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's and
is **undischarged as this section is written**; **check 1 — the producer diff, read as a diff —
is likewise the supervisor's.** **No ladder compute was launched, no step of §2.4's cost table
was run, no queue row was written, and `verification/runs/M6SR_runs/` still does not exist.**

> **THE SUPERVISOR'S RULING, IMPLEMENTED AS GIVEN:** *"keep the `work` mount. Put the case files
> inside it … make the case land where the container actually looks — `work/system/` — rather
> than beside it … §8 registers exactly ONE case-file writer (`write_m6sr_case.py`) and that
> stays true: this driver still writes no case file of its own."*
> **THE `work` MOUNT SURVIVED. NO REGISTERED STEP SHAPE MOVED. THE DRIVER AUTHORS NOTHING.**
>
> **THIS AMENDMENT MOVES NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** `L-HONEST` (§6) is
> carried unaltered: the family refines **2 of 3 directions**, `GCI_fine` is a **LOWER BOUND**,
> `p_s` is **NOT an observed order**, and Sanaa's named first deliverable remains owed.

### 20.1 THE CONDITION, AND HOW IT WAS CHECKED — RULE 2 REQUIRES BOTH

**THE RUN DIRECTORY THAT DOES NOT EXIST — NAMED, AS RULE 2 REQUIRES:**
**`verification/runs/M6SR_runs/`**, and with it `verification/runs/M6SR_runs/{L1,L2,L3}/`.

**How checked, at 2026-09-04T1832Z, WITH A LIVE PLANTED CONTROL (rule 3), AFTER every probe and
every suite run this amendment records:**

| path | reader's answer | role |
|---|---|---|
| `verification/runs/M6SR_runs` | **ABSENT** on disk; `git ls-tree -r HEAD` returns **0 files** | the run root — **the zero** |
| `verification/runs/M6I_runs` | `git ls-tree -r HEAD` returns **14 files** | **the planted non-zero**, same reader, same act |

⚠ **The zero was at risk and that is why it is re-taken here.** Every container probe below was
run in a `mktemp` scratch tree or in the session scratchpad, never in a run root, and the
control suite's own scratch is `mktemp -d` under a cleanup trap. **The reader above was run
after all of them and still returns ABSENT beside a PRESENT.**

### 20.2 ITEM 38 — B3 COULD NOT START, AND IT IS ITEM 31's EXACT CLASS ONE FILE OVER

#### 20.2.1 THE DEFECT, MEASURED AT THE DRIVER'S OWN MOUNT

`build_m6sr_l1.sh` created `$RR/$LEVEL/system` and then **mounted and worked in
`$RR/$LEVEL/work`, which had no `system/` at all.** A comment-stripped read of the whole file
returned **zero** occurrences of `controlDict`, `fvSchemes` or `fvSolution`. Every one of B3's
four utilities constructs a `Foam::Time` from `<case>/system/controlDict` before doing anything
else. **Measured on the pinned digest at the driver's exact `-v`/`-w` shape, with a real 3×3×3
plot3d block so the failure is the case files and not a missing input:**

> `--> FOAM FATAL ERROR: (openfoam-2506) cannot find file "/home/dafoamuser/mount/system/controlDict"`, **inner rc 1**.

✅ **It FAILS CLOSED** — `run_in_container` aborts at exit 6 on a non-zero inner rc — **and it
has never fired**: no run root exists. **This is prevention, not a live repair.**

#### 20.2.2 🔴 IT IS A CHAIN, NOT ONE FILE — AND THE EARLIER READING WAS **PREEMPTED**, NOT WRONG

The prior pass reported *"one missing file, not a chain"* **as far as it was proved** — and it
was proved only as far as the **first** refusal. **Each absence preempts the next.** One probe
per row, same mount, same digest:

| `system/` holds | what `createPatch` says | inner rc |
|---|---|---|
| *(nothing)* | `cannot find file …/system/controlDict` | 1 |
| `controlDict` | `cannot find file …/system/fvSchemes` | 1 |
| `controlDict` + `fvSchemes` | `cannot find file …/system/fvSolution` | 1 |
| `controlDict` + `fvSchemes` + `fvSolution` | **`cannot find file …/system/createPatchDict`** | 1 |
| **all four** | *(no error)* | **0** |

`plot3dToFoam` and `autoPatch 60` need **`controlDict` alone** (measured: both return inner rc 0
with only that file present). `createPatch` and `renumberMesh` build an `fvMesh`, which reads
`fvSchemes` and `fvSolution`.

> **THE RESIDUAL IS SETTLED: `createPatchDict` IS GENUINELY NEEDED.** The question could only be
> answered by supplying everything ahead of it — the prior lane's missing-mesh error and this
> lane's own first ablation each preempted it, one file further along.

#### 20.2.3 🔴 AND IT IS NOT A FORMALITY — `createPatchDict` IS WHAT MAKES THE LEVEL ADMISSIBLE

Two probes one file apart, on the same mesh:

| | `createPatch` inner rc | resulting boundary | §7's screen |
|---|---|---|---|
| **without** the dict | 1 | unchanged: `auto0…auto5`, **wall 1, symmetry 0** | **would abort at exit 8** — no symmetry plane |
| **with** the dict | **0** | `wing` (wall) / `inout` (patch) / `sym` (symmetry) — **wall 1, symmetry 1, patch 3, empty 0** | **PASSES all four clauses** |

⚠ **THIS TOUCHES §7's OWN WORDING, AND IT IS REPORTED RATHER THAN QUIETLY LEFT.** §7 says the
patch names *"are produced by `autoPatch 60` + `createPatch` and are NOT predicted here."*
**Measured, they are not emergent: they are DICTATED, by a dictionary, and the dictionary was
registered nowhere in this document** — §8.5's `system/` remainder lists `controlDict`,
`decomposeParDict` and `sampleDict` and **no `createPatchDict` at all.** ✅ **No gate moves**:
§7's screen tests patch **types**, not names, and it passes. **But §7's stated reason is
inaccurate and the supervisor should read it as such.** A lane does not edit §7.

#### 20.2.4 THE REPAIR — AND WHY IT IS A **COPY**, NOT A WRITE

**Step `B3d`, new, UNBUDGETED, host-only (no container).** Four dictionaries are copied into
`$RR/$LEVEL/work/system/` under a sha256 pin, each hashed **at the source** against the pin and
then **read back from the destination**:

| file | sha256 | needed by |
|---|---|---|
| `controlDict` | `1cfc194c3599879dced4db5ccc50861bc2bf48001b247176f7ed76ef80fcbf8d` | all four utilities |
| `fvSchemes` | `4a1b9cf10c60e71abcd920da63bd778457bd7da85876e7d1d1d547ce9e78aa8c` | `createPatch`, `renumberMesh` |
| `fvSolution` | `0326bdbfc266615c1fe8e94ec7620edf9d266b22ca8d598d2d6539f303ccb88f` | `createPatch`, `renumberMesh` |
| `createPatchDict` | `846e45d721e8be7567bd46a08ba3ae8e0e577b167b64d5308b886a075677140e` | `createPatch` |

**Source: `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/system/` — READ ONLY, and
nothing under `/home/ubuntu/certonomous-runs/` is written, moved or deleted.**

> **§8's SOLE CASE-FILE WRITER IS UNCHANGED AND STAYS SOLE.** The driver **authors nothing**. It
> copies four hash-pinned artifacts out of a read-only tree — **the same act, from the same
> tree, as the surface-master copy-out this registration already blesses.** §8's case is a
> **SOLVE** case, is written by `cases/M6SR/write_m6sr_case.py`, and lands in `$RR/$LEVEL/` at
> step `B3c`. **These four land in `$RR/$LEVEL/work/`, are read only by B3's mesh utilities, and
> the two sets never meet.** `B3c` is **not moved and not redefined** by this amendment.

**WHY THAT TREE.** It is the source of **this family's own L3 mesh** (`run_m6sr_b5.sh:215`
stages `$CR/A3-onera-m6-adjoint-coarse/constant/polyMesh` for L3), so the dictionaries pinned
here are the ones under which an **existing level of this family** was patched. **Measured:
`createPatchDict`, `fvSchemes` and `fvSolution` are BYTE-IDENTICAL between that tree and
`A3-onera-m6-transonic`** (the surface master's own tree), so for three of the four **the choice
of tree changes nothing whatever.** Only `controlDict` differs — **one line, `endTime` 1000 vs
1500** — and the adjoint-coarse copy is the one untouched since `2026-07-28T00:14`, whereas the
transonic copy was modified at `01:32`, **an hour after its own mesh was built at `00:31`.**
⚠ **mtime is weak evidence and is labelled as such: it is a reason to prefer the untouched file,
NOT proof that this is the file under which L2/L3 were patched.**

**THE MOUNT SURVIVED, AND THAT WAS THE POINT.** Mounting `$RR/$LEVEL` instead would put the
wrapper's own log back inside the bind mount — **item 34's shape, the one defect in this
campaign that did not fail closed**, a 3,330-byte `log.checkMesh` at exactly the clean size that
**graded `PASS`** with its head destroyed. **The `work` mount is immune to that by topology and
the immunity is not traded.** The case files moved to the container; the container did not move
to the case files.

**EXIT CODE.** A dictionary that determines the patch names is part of the **build instrument**,
so a mismatch refuses at **exit 10**, beside the image and binary pins. `mkdir`/`cp` failures
keep **3**. **No new exit code is introduced and this file's exit vocabulary is unchanged.**

**ORDERING.** `B3d` sits **above** item 37's run-root refusal, deliberately and for item 37's own
stated reason: below it, the block would be **unrehearsable anywhere except inside
`verification/runs/M6SR_runs/`**, the directory whose absence is this document's rule-2 freeze
proof.

#### 20.2.5 ⚠ THE ONE THING THE MESH-STAGE `controlDict` MOVES — DISCLOSED, AND IT MOVES NO GATE

It carries `writeFormat ascii; writePrecision 16; writeCompression on`, so **B3 writes
`points.gz` / `faces.gz`** — as **both existing levels already are** (measured: the L3 source
`polyMesh` is `.gz`). **Gate A item `A5` hashes the DECOMPRESSED byte stream**
(`analyse_m6sr.points_stream_sha`, which reads `points` **or** `points.gz`; `analyse_m6sr.py`
lines 285–320), **so no Gate A input and no gate threshold moves.** Stated here so nobody later
reads a `.gz` L1 as a different kind of level.

#### 20.2.6 ✅ CAN `B1` → `B2` → `B3` NOW PRODUCE THE L1 MESH? — YES, STRUCTURALLY, AND ONE THING STANDS IN FRONT OF IT

**The driver's own extracted B3 command chain**, run in the **real pinned container** at the
driver's exact mount with the four staged dictionaries, returns **inner rc 0**, produces a
`constant/polyMesh`, and its boundary **passes §7's screen counted by the driver's own
`N_WALL`/`N_SYMM`/`N_PATCH` lines: wall 1, symmetry 1, patch 3, no `empty`.**
**B1 was proven by the prior pass** (rc 0, surface sha `3b94fd7a…`, not the condemned 390-face
surface) and **B2 confirms the registered number** (pyHyp's own banner: `Total Faces: 24960`).
⚠ **There is no fifth defect behind B3 that this pass can find: the chain completes.**
🔴 **But see §20.3 — the caps do not bind, so B1/B2/B3 must not be launched unattended until the
supervisor has ruled on item 39.**

### 20.3 🔴 ITEM 39 — **AN OUTER `timeout` IS NOT A CAP ON A CONTAINER.** REPORTED, **NOT REPAIRED**

**This is not a defect of this file. It is a defect of the mechanism every containerised step in
this campaign uses to enforce a registered cap.** Measured on the pinned digest:

| probe | measured | reading |
|---|---|---|
| known-positive: a container inside its cap | rc **0**, `INSIDE_OK`, container removed | the reader can see a success |
| `timeout 3s docker run … <60 s payload>` | rc **124** — **after 61 wall s** | `timeout` SIGTERMs the docker **client**, which proxies to the container's `bash -c`; that `bash` is waiting on a foreground child and does not act on it, and `timeout` then **waits for the client**. The container **runs to completion.** |
| **the driver's own shape**: `timeout …; rc=$?; docker rm -f "$NAME"` | **60 wall s under a 3 s cap** | the `rm -f` is real, but **it is not reached until the container has already ended itself**. It cleans up; it does not bound. |
| unbounded payload (busy loop) under a 3 s cap | still `Up` **4 minutes** later at a daemon-reported **100.45 % CPU**, wrapper still blocked | **the wrapper never returns at all.** Ended by `docker rm -f` on the recorded name in **0 wall s**. **284 container-seconds; named as waste in §20.5, never absorbed.** |
| `docker run --stop-timeout 2` with a 30 s payload | ran **31 s** | **`--stop-timeout` does NOT cap runtime.** It is only `docker stop`'s grace period. |
| `timeout -k 5s 3s docker run … <120 s payload>` | returned in **8 s**, **rc 137 — NOT 124**; container still `Up` afterwards, ended by `docker rm -f` in 0 wall s | **this is what bounds it** — kill the client, then kill the container by its recorded name. ⚠ **and rc 137 is the item-35 trap again**: the driver's overrun branch tests `rc -eq 124` and would MISS it, aborting at exit 6 with a misleading cause. |

> **THE MECHANISM THAT ACTUALLY BOUNDS A CONTAINERISED STEP:** `timeout -k <grace> <cap>s` on the
> client **plus an unconditional `docker kill`/`docker rm -f` on the container's recorded name**,
> **plus an overrun branch that accepts `137` as well as `124`.** ✅ The name is already recorded
> per step (`m6sr_<tag>_$$`), so a bounded kill has something to aim at.

**WHETHER THIS FILE'S CAPS BIND: THEY DO NOT.** `CAP_B1 = 1.0`, `CAP_B2 = 70.0` and
`CAP_B3 = 3.0` core-min are **reported** after the fact, not **enforced**. **`B2`'s 70 core-min
cap does not stop `B2`.** Rule 12's *"an overrun stops the run"* **is not delivered by this
mechanism for any containerised step in this campaign** — and the same shape appears in
`run_m6sr_b5.sh`, where `B5c`'s cap is **1,630 core-min**.

**NOT REPAIRED HERE, AND THE REASON IS STATED RATHER THAN ASSUMED.** Changing the cap mechanism
changes the rc semantics (`124` → `137`) **and** falsifies §2.4's own *"enforced structurally"*
reading, which is a registration-facing claim. ⚠ **That is the supervisor's, not a lane's.**
**The driver's two false comments are STRUCK BY QUOTE in the file itself** rather than deleted,
and `cases/M6SR/check_m6sr_build_path.sh` check `C6` keeps the finding **executable** — it goes
RED if the finding ever stops reproducing.

### 20.4 THE CONTROLS — AND **HOW** EACH MUTANT DIED, NOT MERELY THAT IT DID

**New file: `cases/M6SR/check_m6sr_build_path.sh`** (351 lines). It **extracts the driver's own
code and runs that** — `stage_mesh_dict()`, the four pins, the four call sites, B3's command
chain and §7's three counting lines — so a mutation to the driver drives the suite RED. **Every
coupling assertion reads a COMMENT-STRIPPED view**, and `C1''` **measures** that this matters
rather than asserting it: `createPatchDict` appears **9 times in the driver and 5 times in its
code**, so a whole-file grep would be satisfied by the prose describing the fix.

**20 checks pass, 0 fail, exit 0.** The refusal path is planted and read back first (an
unmatchable extraction must return **rc 2 and no value**, because a refusal captured as a value
is not a refusal). **The known-positive that licenses every negative is `C4b`:** the driver's own
B3 chain returning **inner rc 0** in the real pinned container.

| mutant | applied to | **how it died** |
|---|---|---|
| **M-A** a pin is altered | the driver's extracted `stage_mesh_dict()` | **exit 10** on the **source-hash** comparison: `MESH-STAGE DICTIONARY MISMATCH` |
| **M-B** the source tree is gone | same | **exit 10** on the **existence** check (`is ABSENT`) — **not** later on an empty hash |
| **M-C** `cp` made a **no-op** | same | **exit 10** on the **destination read-back** — the only check in the function that could see it |
| **M-D** read-back re-hashes the **source**, copy still a no-op | same | **went GREEN with nothing staged — and that is the finding.** A source-hashing read-back would certify a no-op copy. |
| **M-E** read-back deleted, copy still a no-op | same | **rc 0, nothing staged** — which is what proves **M-C's red was the read-back's doing and nothing else's** |
| **D-1** the `stage_mesh_dict createPatchDict` **call site deleted from the driver** | `build_m6sr_l1.sh` | suite **REFUSED, exit 2**: *"expected exactly ONE code line matching … found 0"* |
| **D-2** a pin's hex altered **in the driver** | `build_m6sr_l1.sh` | suite **REFUSED, exit 2**: *"the driver's four pins do not match the four files on disk … The suite REFUSES rather than test a pin against itself"* |

⚠ **ONE MUTATION WAS A NO-OP AS A CONTROL AND IS RECORDED RATHER THAN HIDDEN.** An earlier `M-D`
renamed `$dst`; the copy and the read-back **share `$dst`** and simply moved together, so the
mutant passed for a reason that said nothing about the check. It was replaced by the
source-hashing form above. **A mutant that dies of the wrong cause names the wrong defect.**

**MECHANICS, CHECKED BEFORE ANY RED WAS TRUSTED (§9.2).** No bare `assert` and no `set -e` in
either file (`grep -nE '^[[:space:]]*(assert|set -e)'` returns **0** in the driver). Every
`abort` call site in the new block is at **function top level**, reached from **top level** —
never inside `$( )`, a pipeline, or a `while read`. **There is no loop**: four explicit calls.
`bash -n` parses both files. **No Python was added or changed**, so §9.2's `python3 -O` parity
requirement is untouched — `write_m6sr_case.py` and `analyse_m6sr.py` are **byte-unchanged**.

### 20.5 COST — RULE 12, AND **NONE OF IT IS LADDER COMPUTE**

**All at 1 rank, counted rather than rounded.** ~30 short container probes on the pinned digest
(the cap battery, two ablation rounds, three full suite runs, one cleanup container) totalling
**≈ 496 container wall s = 8.27 core-min**, plus host arithmetic.

🔴 **WASTE, NAMED SEPARATELY AND NEVER ABSORBED INTO ANY RATIO** (`COMPUTE_BUDGET_CHARTER.md`
§6): **284 container-seconds = 4.73 core-min**, spent by a busy-loop probe that was **unbounded
by construction** — the very defect it was measuring. It was ended by `docker rm -f` in 0 wall s
once noticed. **All orphans stopped; a daemon sweep for this session's container names returns
empty.** This is the **second** instance of this class this week — the prior pass paid **1,618
container-seconds = 26.97 core-min** to it — **and that recurrence is itself the argument for
item 39.**

**Measurement spend excluding that waste: ≈ 212 container wall s = 3.53 core-min.**
**Derived at the owner-stated `c7a.4xlarge` $0.0513/core-h: ≈ $0.0071 — DERIVED,
REPORTED-BY-OWNER, never measured**, because the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**ONE NEW UNBUDGETED STEP, NAMED ON ITS OWN LINE AND NOT FOLDED INTO ANY REGISTERED ROW** (§9.3),
exactly as §18.9 treats `B3s`, `B5p`, `B5g` and §19.8 treats `B3c`:

| step | what | measured | status |
|---|---|---|---|
| **`B3d`** | the four mesh-stage dictionaries staged into `work/system/` (host `cp` + `sha256sum` ×2, **no container**) | **0.022 wall s at 1 rank = 0.000367 core-min** per level (median of 5) | **UNBUDGETED** — §2.4 has no row and this section does not create one |

**≤ 0.0011 core-min across the ladder — 0.0002 % of §2.4's 615.24. §2.4's `est ≤ cap` table is
untouched in every cell including the TOTAL row, and no cap is raised to accommodate it.**

**§9.3's estimate-versus-actual row is NOT owed yet**, because no `B` step of §2.4's table has
completed. It falls due at `B1`'s completion — which **item 39 now stands in front of**.

### 20.6 THE PINS — **STALE BY CONSTRUCTION, AND DELIBERATELY NOT RE-TAKEN HERE**

`cases/M6SR/build_m6sr_l1.sh` moved again in this amendment. **Before and after, reported as the
supervisor asked, and NOT re-pinned:**

| path | blob sha **before** | blob sha **after** | lines |
|---|---|---|---|
| `cases/M6SR/build_m6sr_l1.sh` | `a64bc6b810a79dc0dfc7f4363025910ae86966e3` (at `87504e79`) | **`596e949365ea4ef348f576ab891c2920a119bf37`** | 569 → **762** |
| `cases/M6SR/check_m6sr_build_path.sh` (**NEW**) | — | **`e49ab600c82e8f32ce199c15a3f74063d8284600`** | **351** |

**§9's path table and §18.3.1's row for this file pin `04ae9d58…` and are STALE BY
CONSTRUCTION** — they were already stale before this amendment, since `87504e79` moved the file
to `a64bc6b8…`. ⚠ **This section does NOT re-pin them.** §18.6's own rule stands: *a document
cannot pin a blob and change it in the same breath*, and §19.4 shows the re-pin belongs in the
amendment the supervisor orders **for that purpose**. **The re-pin is the supervisor's.**

**Should `check_m6sr_build_path.sh` go into §9's table? THE LANE'S ANSWER IS NO**, for §19.4.3's
reason: **§9's table is the GRADING path**, and this suite grades nothing, produces no artifact
any gate reads, and writes only into a `mktemp` tree it deletes. **But it MUST be pinned** — a
control suite that can be silently edited is a green with no content. **Recommendation: NO to
§9, YES to a standing pin in the gap table. The supervisor rules.**

#### 20.6.1 ADDENDUM, SAME SESSION — THE FILE MOVED ONCE MORE, AND WHY

**Two of item 39's four false comments were REWRITTEN rather than STRUCK BY QUOTE** in the
commit that carries §20. Measured after that commit: of the four sentences the diff deleted,
two were preserved verbatim inside their replacement and two were not. **This registration's
discipline is that originals are struck, never rewritten**, so the two were restored as
`~~quoted~~` strikes in a follow-up commit. **No code changed; the ten deleted lines in that
commit were ALL comment lines and the non-comment deletion count was ZERO, measured.**

| path | blob sha in §20.6 | blob sha **after this correction** |
|---|---|---|
| `cases/M6SR/build_m6sr_l1.sh` | `596e949365ea4ef348f576ab891c2920a119bf37` | **`cd9daf8609b2ea02cc7977ac58b8f1de140b0dc0`** |

⚠ **Still NOT re-pinned** (§20.6). The chain is now `04ae9d58` → `a64bc6b8` → `596e9493` →
the value above, and **the re-pin remains the supervisor's.**

### 20.7 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves no gate, no threshold, no cap and no label.** §2.4's cost table is unchanged in
   every cell **including the TOTAL row**; §5's Gate A thresholds are unchanged; `X1`–`X7` stand.
2. **It does NOT re-freeze.** `SUPERVISION_CHARTER.md` §3 check 4 belongs to the cfd supervisor
   and is **undischarged**; **check 1 — the producer diff, read as a diff — is likewise theirs.**
3. **It does NOT change the mount, the step shape, or `B3c`.** The `work` mount is kept; §8's
   case is still written by one writer into `$RR/$LEVEL/` before `B4`.
4. **It does NOT widen the driver's authority.** The driver authors no case file. It copies four
   hash-pinned artifacts and refuses on any hash it did not expect.
5. **It does NOT touch `cases/M6SR/analyse_m6sr.py`, `cases/M6SR/write_m6sr_case.py` or
   `cases/M6SR/run_m6sr_b5.sh`** — all three are byte-unchanged.
6. **It does NOT repair item 39**, and it does not change any cap mechanism. It measures, records
   and keeps the finding executable. **The ruling is the supervisor's.**
7. **It does NOT edit §7**, whose stated reason for not predicting patch names is inaccurate
   (§20.2.3). A lane reports; it does not amend a registered section's reasoning.
8. **It does NOT re-pin §9 or §18.3.1** (§20.6).
9. **It launched NO ladder compute, enqueued nothing, and wrote nothing into
   `verification/queue/`.** `verification/runs/M6SR_runs` is **ABSENT**, re-verified with the
   same plant at the same path after every act above.
10. **It does NOT change `/home/ubuntu/certonomous-runs/`**, which was read only, nor
    `docs/LAB_STATE.md`.
11. **It claims no verdict of the fixed vocabulary for any gate.** No solver has run.
12. **SUBMISSIONS REMAIN PARKED (rule 7). Nothing left the box (rule 8).**

### 20.8 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.5 → v1.6 (amendment 14, pre-compute). The frozen file was NOT edited; this section
is APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10,
§16.9, §17.12, §18.11 and §19.10 give: editing it would change a line above §15 and falsify those
sections' own assertions, on which other records depend. **The bump is recorded HERE. The
supervisor may restate the version in the header at the re-freeze, which is a status flip they
own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–4107** of this file — the whole of it up to and including
§19.10's closing line, and therefore the whole of §15's guaranteed range 1–2022, §16's 1–2229,
§17's 1–2690, §18's 1–3684 and §19's 1–4107 — are **byte-identical** before and after this
append, both rendering to sha256
**`e59c6b1eca3b7466664cf2e24ad7001d6d31c96e0289634d9fb27ed2d4538622`**. Other records cite this
document **by line**, and at least one such citation sits inside an executable check, so this is
a guarantee and not a courtesy.

---

## 21. AMENDMENT 15 — 2026-09-04, **PRE-COMPUTE**. **ITEM 39 IS REPAIRED IN BOTH DRIVERS — THE CAPS NOW BIND**, AND §2.4's *"enforced structurally"* IS STRUCK BY QUOTE

**THE PRE-COMPUTE CONDITION, STATED AND CHECKED, NOT ASSUMED.** Rule 2 permits an amendment
before first compute and requires the condition to be named and checked. **The run directory
that does not exist is `verification/runs/M6SR_runs`.** It was checked **with a plant at the
exact searched path**: `check_m6sr_cap_binds.sh` check `K6` creates that directory, confirms the
reader SEES it, removes it, and only then reports it absent — a reader not shown able to see a
present tree cannot be trusted to report an absent one (rule 3). **No ladder compute has been
run; no gate, threshold, cap or label moves in this amendment.**

### 21.1 THE FALSE CLAIM, STRUCK BY QUOTE

§18's implementation list (line 2086) reads that the driver implements *"§2.4 (the `B1`/`B2`/`B3`
caps, enforced **structurally** by `timeout`)"*.

> 🔴 **STRUCK BY QUOTE:** ~~"the `B1`/`B2`/`B3` caps, enforced **structurally** by `timeout`"~~

**MEASURED FALSE AS WRITTEN, and it stays struck even now that the caps bind** — because the
enforcement is real but it is **not `timeout`**, and it is not any one mechanism alone. §20.3's
measurement stands unchanged and is the reason the repair has the shape it has.

### 21.2 THE REPAIR — THREE LIMBS THAT ARE ONLY A CAP TOGETHER

Applied to **both** `cases/M6SR/build_m6sr_l1.sh` and `cases/M6SR/run_m6sr_b5.sh`:

| limb | what | what it bounds | measured consequence of dropping it |
|---|---|---|---|
| 1 | `timeout -k ${CAP_KILL_GRACE_S}s <cap>s` on the client, on **both** invocation branches | **the CLIENT** | the wrapper **never returns at all** |
| 2 | an **UNCONDITIONAL** `docker kill` + `rm -f` on the **recorded** container name | **the CONTAINER** | the client returns looking clean; **the container is still `Up`** |
| 3 | an overrun branch accepting **`137` as well as `124`** | **the READING** | the real overrun rc **misses the branch** |

`CAP_KILL_GRACE_S = 5`. The container name is bound to `$cname` and written to disk **before**
the run, so the kill has something to aim at without trusting anything the client returned.

**WHICH rc MEANS WHAT, stated in the code rather than left to a reader:** `124` = `timeout`
reached the cap, sent SIGTERM, and the client **exited on it**. `137` = 128+9 — the client did
**not** exit on SIGTERM and `timeout -k` **SIGKILLed** it at cap+grace. ⚠ **`137` is the NORMAL
rc for a real containerised overrun on this box**, so a branch testing only `124` misses every
one of them — the item-35 trap exactly. ⚠ **Honest ambiguity, not papered over:** `137` can also
be a SIGKILL from elsewhere (an OOM kill of the client). **Both readings stop the run**, so the
branch is safe either way, and `wall` vs `cap` is recorded so a reader can separate them — a cap
overrun has `wall ≥ cap`, a foreign SIGKILL has `wall ≪ cap`.

⚠ **The kill is UNCONDITIONAL and that is the whole point.** It is not guarded by the rc,
because the entire item-39 finding is that **the client's return tells you nothing about the
container.**

### 21.3 THE MEASUREMENT — BEFORE AND AFTER, SAME PAYLOAD, SAME CAP

**New file: `cases/M6SR/check_m6sr_cap_binds.sh`.** It does **not** reimplement the mechanism: it
**extracts the drivers' own lines** — `docker_q()`, `docker_timeout_q()`, the grace constant,
both kill lines and the overrun branch condition — from a **comment-stripped, indentation-
stripped** view and runs **those** against real containers on the pinned digest.

| | unbounded payload under a **3 s** cap | outer rc | containers left `Up` |
|---|---|---|---|
| **BEFORE** (bare `timeout`) | **never returned** — still blocked at the suite's **25 s** deadline (a lower bound: the suite stopped waiting, it did not stop being blocked) | — | **1** |
| **AFTER** (three limbs) | **8 s**, inside cap+grace = 8 s | **137** | **0** |

**`B2`'s 70 core-min cap now stops `B2`; `B5c`'s 1,630 core-min cap now stops `B5c`.** Rule 12's
*"an overrun stops the run"* is delivered for containerised steps in this campaign.

### 21.4 THE CONTROLS — AND **HOW** EACH MUTANT DIED

**26 checks pass, 0 fail, exit 0.** The refusal path is planted and read back first (an
unmatchable extraction must return **rc 2 and no value** — a refusal captured as a value is not
a refusal). **Every mutant is first proved to differ from the control harness**, so no mutation
is a no-op dressed as a test.

**THE KNOWN-POSITIVE THAT LICENSES EVERY NEGATIVE (`K2`):** a 2 s container under a 20 s cap
returns **rc 0 in 2 s**, the overrun branch does **not** fire, and it is **not** killed. Without
it, a mechanism that simply killed everything would pass every "it was stopped" check.

**`K1'` MEASURES that reading a comment-stripped view matters** rather than asserting it:
`timeout -k` appears **11 times in `build_m6sr_l1.sh` but only 3 times in its CODE** — a
whole-file grep would be satisfied by the prose describing the fix.

| mutant | limb dropped | **how it died** |
|---|---|---|
| `M-1` | 1 (`-k`) | the wrapper **NEVER RETURNED** — still blocked at the 14 s deadline with 1 container `Up`, where the real harness returned in 8 s. `K4a`'s wall bound is violated by an unbounded margin. |
| `M-2` | 2 (unconditional kill) | the client returned **rc 137 in 8 s, looking exactly like a clean bounded overrun** — but **1 container was still `Up`**. `K4d` goes RED. |
| `M-3` | 3 (`137`) | the overrun produced **rc 137** and the narrowed branch **did not fire**. `K4c` goes RED; the run would have sailed past its cap and then aborted at exit 6 on the inner rc **with a misleading cause**. |

### 21.5 WHAT THIS AMENDMENT DOES **NOT** DO

- ⚠ **IT DOES NOT RE-PIN.** §9's and §18.3.1's driver blob shas are **stale by construction** —
  this repair moves both driver blobs. **The re-pin is the supervisor's to order, and a lane may
  not take it.**
- It moves **no gate, no threshold, no cap and no label.** The §2.4 cost table is untouched.
- It does **not** alter `check_m6sr_build_path.sh` check `C6`, whose **code is byte-identical**.
  `C6` probes a **bare** `timeout` directly, never the driver's helper, so what it pins is the
  **platform fact that makes this repair necessary** — not the driver's old shape. It still
  passes, and it should: if a bare `timeout` ever begins bounding a container on this daemon,
  the repair's shape must be re-argued from scratch.

### 21.6 COST

**Zero ladder core-minutes.** The suite spent **66 container-seconds**, reported as **WASTE,
separately, never absorbed into a step's cost**. ⚠ **Every container this suite starts is itself
bound by the mechanism under test**, plus a final sweep — two consecutive earlier passes were
bitten by the very unboundedness they were measuring (284 container-seconds in one). The
unbounded payload is `while :; do sleep 1; done`, **not** a busy loop: it is unbounded in exactly
the way that matters (pid 1 is a `bash` blocked on a foreground child, which is the signal-
handling path the whole finding turns on) but it does **not** burn a core. The box was **not**
idle — heat-transfer's T3e held 8 ranks of 16. **This substitution is deliberate and named.**

**Version: v1.6 → v1.7 (amendment 15, pre-compute). The frozen file was NOT edited; this section
is APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10,
§16.9, §17.12, §18.11, §19.10 and §20's closing give: editing it would change a line above §15
and falsify those sections' own assertions, on which other records depend. **The bump is recorded
HERE.**

> **`lines whose number changed above this section: 0`**

---

## 22. AMENDMENT 16 — 2026-09-04, **PRE-COMPUTE**. **THE RE-PIN.** EVERY EXECUTABLE THE LADDER RUNS IS PINNED BY BLOB SHA, THREE SUPERSEDED PINS ARE **STRUCK BY QUOTE**, AND `C6` IS SETTLED BY **MEASUREMENT** RATHER THAN BY REASONING

**WHY THIS AMENDMENT EXISTS, IN THE PRIOR LANE'S OWN WORDS.** §21.5 closed with *"IT DOES NOT
RE-PIN … the re-pin is the supervisor's to order, and a lane may not take it"*, and the lane that
wrote it added that **a launch before the re-pin would run an instrument the registration does not
name.** The supervisor has now ordered it. **This amendment takes the re-pin and nothing else.**

**THE PRE-COMPUTE CONDITION, STATED AND CHECKED, NOT ASSUMED.** Rule 2 permits an amendment before
first compute and requires the condition to be named and how it was checked. **The run directory
that does not exist is `verification/runs/M6SR_runs`.** Checked **with a plant at the exact searched
path**, in one invocation, by the same reader throughout:

| step | reader `[ -d verification/runs/M6SR_runs ]` |
|---|---|
| before the plant | `ABSENT` |
| **with the plant present** | **`PRESENT`** — the reader is shown able to see a present tree |
| plant removed | `ABSENT` |
| independent `find -maxdepth 1 -name 'M6SR_runs'` | **0 hits** |

**No ladder compute has been run.** No gate, threshold, cap or label moves in this amendment.

### 22.1 THE THREE SUPERSEDED PINS, **STRUCK BY QUOTE**

Rule 6: originals are struck, never rewritten. **The three rows below are pin claims that are IN
FORCE and are MEASURED FALSE at this HEAD.**

**(1) §15.3's `build_m6sr_l1.sh` row** — §18.3.2 struck §15.3's *comparator* row and expressly
re-verified this one as unmoved **at that date**. It has moved four times since.

> 🔴 **STRUCK BY QUOTE:** ~~*"| **`cases/M6SR/build_m6sr_l1.sh`** (build driver) | **`04ae9d58220a55fa900b02f77424bb7687da0de1`** | `6459428b4c283c597e72e08f7c7ded3c454cfb8efd0facbbc8b178b42e5abc35` | 304 |"*~~

**(2) §18.3.1's `build_m6sr_l1.sh` row** — the same blob, pinned a second time, with its
first-appearance commit.

> 🔴 **STRUCK BY QUOTE:** ~~*"| **`cases/M6SR/build_m6sr_l1.sh`** (build driver) | **`04ae9d58220a55fa900b02f77424bb7687da0de1`** | `6459428b4c283c597e72e08f7c7ded3c454cfb8efd0facbbc8b178b42e5abc35` | 304 | **`c1625208`** (Amendment 9) |"*~~

**(3) §19.4.2's `run_m6sr_b5.sh` row** — stale by construction exactly as §19.4's own predecessor
row was, and for the same reason: Amendment 15's cap repair moved the file in the commit that
carried it.

> 🔴 **STRUCK BY QUOTE:** ~~*"| **`cases/M6SR/run_m6sr_b5.sh`** (sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`) | **`6e12307edfeeabd40effc9a5eedc6176fab99212`** | `a9f1d3765862ea4a9eef09971eab60df5f2a65443e02ac8a182a869fc29eec7d` | **795** | **NOT in §9's table**; **CHANGED BY THIS AMENDMENT** (§19.2.3) |"*~~

⚠ **§18.3.1's `run_m6sr_b5.sh` row (`44fae79b…`) is NOT struck again here** — §19.4.1 already
struck it, and striking a struck row twice would make the record harder to read, not safer.

### 22.2 THE PINS — **ALL TEN EXECUTABLES THE LADDER RUNS**, RE-HASHED INSIDE THE COMMIT

**Every blob below was re-derived with `git hash-object` on the working tree, checked against
`git rev-parse HEAD:<path>`, and RE-HASHED A SECOND TIME INSIDE THE SAME SHELL INVOCATION AS THE
COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT ABORTING IF ANY ONE OF THE TEN HAD MOVED.**
⚠ This is a live guard, not a formality: §18.3.1 records a file moving between the drafting of its
pin table and the commit (`0b3b73bb…` → `44fae79b…`), and §20.6.1 records a second such move.

**THE SEVEN CODE ARTIFACTS THAT PRODUCE OR GRADE:**

| path | git blob sha | sha256 of the file | lines | blob first appears at | §9 status |
|---|---|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`9b963ad48e016fe2177553507006915e52b4ef98`** | `9042cdf22ff948f8df48d846495ccb0d05e5130d19a0572b6020b728507d9394` | 2,742 | **`8c0ab7a8`** (Amendment 11) | **§9 registered** — pin UNMOVED since §18.3.1 |
| **`cases/M6SR/build_m6sr_l1.sh`** (build driver, `B1`–`B3`) | **`caa7d9de787b1dc8cf5e45935afcc5ef425b85fc`** | `6c6f0a8f7c595d130fcaa75cf953763c78716c80a219a94493df4ae4eaf3eb90` | **828** | **`045a6044`** (Amendment 15, the cap repair) | **§9 registered** — **RE-PINNED HERE**, §22.1(1) and (2) |
| **`scripts/residual_max_over_equations.py`** (`G2`'s only instrument, §5.1) | **`b5eee67d594c04df90a2201b003039d5959c6eb4`** | `39a5e0d4b19ab5aa9313888e86297e7ff8c0bb7dc0c2e8628479b561d1c0bbd7` | 433 | **`184c00af`** | **§9 registered** — pin UNMOVED |
| **`scripts/verify_agard_ar138_table_b1_1.py`** (the `GF2` reference loader) | **`6cc89ced4cbd54e3b6b57403fe7224e6e08a83ab`** | `ee62a6ac6cb8cb6b19cc6cad7f742c8fcf0e434f3ec272449aaa7f38b9c96bde` | 222 | **`96e08380`** (the `C19` repair) | **§9 registered** — pin UNMOVED |
| **`scripts/check_comparator_freeze.py`** (named by §9.1 as the verifier) | **`dabd740e56a017edbc04b9c2b866c93c661ce0ab`** | `2871fabbab2bf8a126af49d4cdf6c7c6cb3a7ef9fd107b2afa4e942771b54709` | 904 | **`5c31a23c`** | **§9 registered** — pin UNMOVED |
| **`cases/M6SR/write_m6sr_case.py`** (§8's sole case-file writer) | **`f2e8f3bc5982e92b9f5697e568c0f31f3c17d0a5`** | `eb8abf930e999ab2af2eac74793229df0ddd096a34f41756a378627ce15c360c` | 1,059 | **`8c0ab7a8`** (Amendment 11) | **NOT in §9's table** — the gap, §18.3.1 |
| **`cases/M6SR/run_m6sr_b5.sh`** (sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`) | **`27996a8dbd31c8edf38923c7ec31924111707f7f`** | `7c51d04f8c34b032430a93a3f64ac0d26d57c3d03a409be919c90fed8f261223` | **850** | **`045a6044`** (Amendment 15, the cap repair) | **NOT in §9's table** — **RE-PINNED HERE**, §22.1(3) |

**AND THE THREE CONTROL SUITES — PINNED FOR THE FIRST TIME AS A COMPLETE SET.** A control suite
that can be silently edited is a green with no content (§19.4.3), and **`check_m6sr_cap_binds.sh`
has never been pinned anywhere in this document until now:**

| path | git blob sha | sha256 of the file | lines | blob first appears at | §9 status |
|---|---|---|---|---|---|
| **`cases/M6SR/check_m6sr_launch_path.sh`** (launch-path controls) | **`9b8d44ce7c68a0728db80cc83fb11dbeb77d945d`** | `0da8aad32983d6b737de346db5b6fd1d71e96c64b014d56a51ce1f495ca9372c` | 367 | **`20aad5c7`** | **NOT in §9's table** — pin UNMOVED since §19.4.2 |
| **`cases/M6SR/check_m6sr_build_path.sh`** (build-path controls, items 38/39) | **`dd9f7c4ab87f2e464e3905cf1037093e8814520c`** | `aa416ff44cb3d8f26873e2a25f5a9db4af925129656f7597f991f6467ecfd9d9` | **360** | **`045a6044`** | **NOT in §9's table** — **FIRST STANDING PIN**; §20.6 reported a sha but expressly declined to pin |
| **`cases/M6SR/check_m6sr_cap_binds.sh`** (the cap-binding controls, `K1`–`K6`) | **`6ea8c368cce364a4f27cbb2e5d37f26680d4b152`** | `8feafa99dc31db987ff246d79c7258d01a472082ccca8e796fed51b36ab647b3` | **358** | **`045a6044`** | **NOT in §9's table** — **NEVER PINNED BEFORE THIS SECTION** |

#### 22.2.1 TEN IS THE WHOLE SET, AND THAT IS MEASURED RATHER THAN ASSERTED

Item 32 recorded *"§9's frozen path table registers TWO executables and the ladder now runs
SEVEN."* **It now runs TEN**, and the closure was re-derived here rather than carried forward:

- The two drivers were read **comment-stripped** and every `.py`/`.sh` name in their **code** was
  enumerated. `build_m6sr_l1.sh` invokes `analyse_m6sr.py` and `write_m6sr_case.py`;
  `run_m6sr_b5.sh` invokes the same two. **Neither driver invokes a script outside this set.**
- The comparator's own dependency edges are **imports and one subprocess**, not shell calls, which
  a driver-only sweep would have missed: `analyse_m6sr.py:645/649` imports
  `verify_agard_ar138_table_b1_1`, `:1153/1157` imports `residual_max_over_equations`, and
  `:2182–2208` shells out to `scripts/verify_agard_ar138_table_b1_1.py` for `C19`.
  `write_m6sr_case.py:330` imports `analyse_m6sr`. **The closure is exactly the ten above.**
- ⚠ **Read comment-stripped for the same reason `C1''` exists**: these filenames appear far more
  often in the drivers' prose than in their code.

### 22.3 THE MOVEMENT CHAIN — **HISTORY, DELIBERATELY NOT STRUCK**, AND THE JUDGEMENT IS NAMED

§19.4.2 set the precedent by recording `ab3b1ab2…` as *"the superseded intermediate, recorded so
the chain is readable"* — a history row, not a strike. §20.6 and §20.6.1 are of that kind: they
carry blob shas under headings that read **"STALE BY CONSTRUCTION, AND DELIBERATELY NOT RE-TAKEN
HERE"** and **"Still NOT re-pinned"**. **They are movement reports, not pins in force, so they are
NOT struck.** The full chains, so no reader can mistake an intermediate for a current value:

| file | chain, oldest → **current** |
|---|---|
| `cases/M6SR/build_m6sr_l1.sh` | `04ae9d58` (§15.3, §18.3.1 — **struck, §22.1**) → `a64bc6b8` (`87504e79`) → `596e9493` (§20.6) → `cd9daf86` (§20.6.1) → **`caa7d9de`** |
| `cases/M6SR/run_m6sr_b5.sh` | `0b3b73bb` (drafted, never committed as a pin) → `44fae79b` (§18.3.1 — struck at §19.4.1) → `ab3b1ab2` (`5cf8a009`) → `6e12307e` (§19.4.2 — **struck, §22.1**) → **`27996a8d`** |
| `cases/M6SR/check_m6sr_build_path.sh` | `e49ab600` (§20.6, reported not pinned) → **`dd9f7c4a`** |
| `cases/M6SR/analyse_m6sr.py` | `97cbe039` (§15.3 — struck at §18.3.2) → **`9b963ad4`** |

⚠ **THIS JUDGEMENT IS THE LANE'S AND IS FLAGGED FOR THE SUPERVISOR TO OVERRULE.** If the
supervisor reads §20.6's *"blob sha **after**"* column or §20.6.1's *"blob sha **after this
correction**"* column as pin claims in force rather than as dated movement reports, then
`596e9493`, `cd9daf86` and `e49ab600` require strikes too. **The lane's reading is that they are
history and that their own headings say so. The lane did not strike them, and says so here rather
than leaving the decision invisible.**

### 22.4 `C6` — **REASONED BEFORE, MEASURED NOW.** IT PASSES.

**THE GAP THE PRIOR LANE NAMED AGAINST ITSELF.** §21.5 asserted that
`check_m6sr_build_path.sh` check `C6` still passes after the cap repair, on the argument that `C6`
probes a **bare `timeout`** directly rather than the drivers' helper, and therefore pins the
**platform fact the repair works around** rather than the drivers' old shape. **That lane did not
run the suite and said so.** An argument that a check still passes is not the check passing.

**RUN. MEASURED. THE SUITE EXITS 0: 20 checks passed, 0 failed, and the refusal path is planted
and read back before anything rests on it.**

| check | measured |
|---|---|
| **`C6`** | **`PASS`** — a **3 s** `timeout` on a **12 s** container returned **rc 124 after 12 WALL SECONDS**. The bare-`timeout` platform fact **still reproduces**: the cap **reports** the overrun, it does not **stop** it. |
| `C6'` | `PASS` — `docker rm -f` on the recorded name ends the container in **0 wall s**. This is limb 2 of §21.2's repair, measured by the suite that pins the defect. |
| `C4b` | `PASS` — the driver's own extracted `B3` chain returns **inner rc 0** in the real pinned container. **This known-positive is what licenses every refusal beside it** (rule 3). |
| `C4a` / `C5a` | `PASS` — item 38 and the `createPatchDict` limb both still reproduce, failing closed. |
| `SWEEP` | `PASS` — **no container this suite started is left on the daemon.** |

✅ **`C6` IS GREEN, AND THE PRIOR LANE'S REASONING IS VINDICATED BY MEASUREMENT RATHER THAN
ADOPTED ON TRUST.** The finding it keeps executable is intact: if a bare `timeout` ever begins
bounding a container on this daemon, `C6` goes RED and §21.2's repair must be re-argued.

#### 22.4.1 AND THE SUITE'S CODE IS PROVED BYTE-IDENTICAL ACROSS ITS MOVE — WITH A LIVE PLANT

§21.5's claim that the suite's *"code is byte-identical"* across `e49ab600` → `dd9f7c4a` was also
an assertion. **Measured here:** the two blobs differ by **15 lines**, and a **comment-stripped
view of each renders to the same sha256
`b8899667705ea82c1d2511efa506eea12246f6c903d5993ca2dde5c17fbce9fa`**. Every one of the 15 changed
lines is a comment, and both changes are the two `"REPORTED, NOT REPAIRED"` sentences correctly
converted to `~~quoted~~` strikes. ⚠ **PLANTED CONTROL, because an equality is worthless from a
comparator not shown able to report an inequality:** one character appended to a single line of
the new comment-stripped view makes the **same comparison** report a difference. **The plant was
SEEN.**

### 22.5 THE STRIKE AUDIT — MACHINE-VERIFIED, BECAUSE THE EYE HAS ALREADY MISSED THIS ONCE

§20.6.1 records a prior lane catching **itself** deleting a four-line block and striking only the
fourth line — *"that audit is what caught it, not my eye."* **The same audit was run on this
section before it was committed.** Its subjects are the **four shas this amendment declares FALSE
IN FORCE**: the two blob shas and the two file sha256s **quoted inside §22.1's three strike
spans** — named structurally here, and deliberately not re-typed, for the reason the audit itself
discovered below. Every occurrence of each of them in the text this amendment adds was located and
classified, and **each one sits either inside a `~~…~~` strike span in §22.1 or on a line of
§22.3's explicitly-labelled history chain.** The result is printed in the commit that carries this
section.

⚠ **THE AUDIT WENT RED ON THIS SECTION'S OWN FIRST DRAFT, AND THAT IS WHY IT IS WORTH RUNNING.**
The first draft of this very paragraph listed the four shas literally, in plain prose, outside any
strike span. **The auditor classified all four as `UNCLASSIFIED` and refused the commit.** The
values were **not** wrapped in a strike to silence it — a strike would have been a lie, since the
paragraph is describing them rather than quoting a superseded row — they were **removed**, and the
paragraph now names them by reference. **Machine-caught, not eye-caught, exactly as §20.6.1
predicted.**

⚠ **RULE 3, ON THE AUDITOR ITSELF.** A clean audit from a reader never shown able to report a
violation is not evidence. **The audit plants one:** a false sha is injected on a plain, unstruck,
non-chain prose line and the auditor must report it `UNCLASSIFIED`. **The plant was SEEN**, and
the audit **refuses (exit 2)** rather than reporting a pass if it is not.

⚠ **The audit's scope is those four shas and nothing wider**; a sha this amendment treats as
history (§22.3) is by construction outside it, which is exactly why §22.3 names that judgement
instead of burying it.

### 22.6 §9's FROZEN TABLE — **STILL THE SUPERVISOR'S.** THIS AMENDMENT DOES NOT EXTEND IT.

Item 32's ruling stands: *"adding a path to §9's frozen table is a FREEZE question and is the
supervisor's. A lane pins shas and reports."* **Five of the ten above are §9-registered paths and
five are not.** The recommendations of §19.4.3 and §20.6 are restated unchanged and a third is
added, all three for the same reason — **§9's table is the GRADING path, and a control suite
grades nothing, produces no artifact any gate reads, and writes only into a `mktemp` tree it
deletes:**

| file | lane's recommendation |
|---|---|
| `check_m6sr_launch_path.sh` | **NO** to §9; **YES** to a standing pin (given, §22.2) |
| `check_m6sr_build_path.sh` | **NO** to §9; **YES** to a standing pin (given, §22.2) |
| `check_m6sr_cap_binds.sh` | **NO** to §9; **YES** to a standing pin (given, §22.2) |

⚠ **`write_m6sr_case.py` and `run_m6sr_b5.sh` are a DIFFERENT question and the lane makes no
recommendation on them.** They are **producers on the graded path** — one writes §8's case, the
other is the sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam` and `log.checkMesh`, which
Gate A and rule 4's completion check both read. **§18.3.1 named that as a hole and it is still
open.** It is a freeze question, it is the supervisor's, and **this section does not answer it.**

### 22.7 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** Not one number in §5, §5.1, §2.4 or
   §10 is touched. **Pins and refusals are not gates**, and a strike of a superseded hash changes
   what a comparator must match, never what a gate must beat.
2. **It does NOT add a path to §9's frozen table** (§22.6).
3. **It touches NO code.** Not one of the ten pinned files is edited by this amendment — that is
   the precondition for pinning them at all, §18.6's *"a document cannot pin a blob and change it
   in the same breath."*
4. **It runs NO ladder compute.** No `B2` march, no `B5` solve, no queue row.
   **`verification/runs/M6SR_runs` does not exist**, verified with a plant at the exact searched
   path both before this work and after it.
5. **It does NOT freeze and it does NOT launch.** Rule 2's freeze and the launch decision are the
   supervisor's; a lane may not take either.
6. **It does NOT re-litigate items 25, 27, 28, 30, 33, 35, 36, 37** or any other carried-forward
   finding. **Items 35, 36 and 37 remain OPEN in `build_m6sr_l1.sh`**, and re-pinning that file
   pins the defects along with the repairs — **which is what a pin is for.**

### 22.8 COST — RULE 12, AND **NONE OF IT IS LADDER COMPUTE**

| item | predicted | **actual** | ratio | attribution |
|---|---|---|---|---|
| `check_m6sr_build_path.sh`, whole suite | cap **420 s** wall at 1 rank = **7.0 core-min** ceiling | **14 s** wall at 1 rank = **0.233 core-min** | **0.033** | the cap was set as a **ceiling**, not an estimate — the suite's containers are seconds-long by design (§ the file's own header: *"no solver runs here, and no pyHyp march"*). **Misprediction, not contention.** |
| hashing, diffing, document work | — | **host arithmetic, ~0** | — | — |

**Container-seconds, reported as WASTE and SEPARATELY, never absorbed into a step's cost: 14 s at
1 rank = 0.233 core-min**, of which the suite's own counter attributes **12 s** to `C6`'s
deliberately-overrunning container. ⚠ **Honest caveat on that counter:** it is second-granular, so
`C4`/`C5`'s sub-second containers round to **0** and the 12 s is a **lower bound** on container
time, not a total; **14 s of harness wall is the upper bound and is what is charged.**

⚠ **EVERY CONTAINER THIS PASS STARTED WAS BOUND BY THE MECHANISM UNDER TEST.** The suite is
**pinned and was NOT edited** to add a bound; the bound was applied **around** it, with §21.2's
three limbs: `timeout -k 15s 420s`, an **UNCONDITIONAL** `docker rm -f` sweep of the suite's own
`m6bc_` name prefix that runs on **every** outcome and not only on the cap, and a **124/137**
branch. **Measured: harness rc 0 in 14 s; containers left before the sweep — NONE; after — NONE.**
The suite's own `SWEEP` check agrees independently.

⚠ **The box was NOT idle.** Heat-transfer's `T3e` held **8 ranks of 16** (load average 8.04 at
launch). This pass took **1 rank for 14 s** and did not saturate.

### 22.9 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.7 → v1.8 (amendment 16, pre-compute). The frozen file was NOT edited; this section
is APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10,
§16.9, §17.12, §18.11, §19.10, §20.8 and §21.6 give: editing it would change a line above §15 and
falsify those sections' own assertions, on which other records depend. **The bump is recorded
HERE. The supervisor may restate the version in the header at the re-freeze, which is a status
flip they own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–4573** of this file — the whole of it up to and including
§21.6's closing line, and therefore the whole of §15's guaranteed range 1–2022, §16's 1–2229,
§17's 1–2690, §18's 1–3684, §19's 1–4107 and §20's 1–4107 — are **byte-identical** before and
after this append, both rendering to sha256
**`70e7b821bf15678891c8e4b235d5d6e6f5c4348142daba6107844691a72b2a2d`**. Other records cite this
document **by line**, and at least one such citation sits inside an executable check, so this is a
guarantee and not a courtesy.

### 22.10 ADDENDUM, SAME SESSION — **A CLAIM THIS AMENDMENT ITSELF MADE IS MEASURED FALSE AND IS STRUCK BY QUOTE**, AND THE EIGHTEENTH PASS FINDS **ITEM 40**

**Same session, same pre-compute condition** (`verification/runs/M6SR_runs` still absent, re-checked
with the plant at the exact searched path after §22 was committed). **No gate, threshold, cap or
label moves.** §20.6.1 set the precedent for a same-session addendum; **no version bump is taken
here** because §22.9's bump already covers this amendment.

#### 22.10.1 🔴 **THE LANE'S OWN FALSE CLAIM, STRUCK BY QUOTE. IT WAS RELAYED, NOT MEASURED.**

§22.7 clause 6 asserts, in the present tense, about the file this amendment re-pins:

> 🔴 **STRUCK BY QUOTE:** ~~*"**Items 35, 36 and 37 remain OPEN in `build_m6sr_l1.sh`**"*~~

**MEASURED FALSE. All three were repaired before this amendment was written**, and the lane carried
the sentence forward from §19.5's heading instead of reading the file it had just hashed. ⚠ **That
is precisely the failure this campaign's own discipline exists to prevent, committed inside the
amendment whose entire purpose is to stop the registration naming an instrument it has not
verified.** It is disclosed here rather than quietly dropped.

**THE MEASUREMENT — the driver's whole blob lineage, comment-stripped, one reader throughout:**

| blob | `$DRUN "docker run …"` one-arg form (item 35) | `docker_q()` argv helper | `IMAGE DIGEST MISMATCH` refusal (item 36) | `M6SR_REGISTERED_RUN_ROOT` assertion (item 37) | lines |
|---|---|---|---|---|---|
| `04ae9d58` | **1** | 0 | **0** | **0** | 304 |
| `a64bc6b8` | **0** | 1 | **1** | **3** | 569 |
| `596e9493` | 0 | 1 | 1 | 3 | 762 |
| `cd9daf86` | 0 | 1 | 1 | 3 | 766 |
| **`caa7d9de`** (pinned, §22.2) | **0** | **1** | **1** | **3** | **828** |

**THE REPAIR LANDED AT `a64bc6b8`, IN COMMIT `87504e79` (2026-09-04T18:00:22Z)**, whose subject
says so in as many words: *"cfd M6SR ITEMS 35, 36, 37 REPAIRED in `build_m6sr_l1.sh`."* **The
current sites, read at the pinned blob:** `docker_q()` at `:399` and `docker_timeout_q()` at `:414`
(argv-passing, used at `:432`, `:447`, `:625`, `:636`, `:637` — **no `$DRUN "…"` one-argument form
survives anywhere in the code**); the digest pinned at `:298`, resolved at `:432` and **refused at
`:435–436`, exit 10**, with the message *"a pin on the solver alone pins half the instrument"*; and
the run root asserted at `:586–589`, **refused at exit 9**.

⚠ **§19.5's HEADING IS *NOT* STRUCK, AND THE DISTINCTION IS THE WHOLE POINT.** *"REPORTED, NOT
REPAIRED"* was **true of the 304-line blob** — the first row of the table above, the one §22.1
struck as a pin — when Amendment 13 wrote it, and it cites `:105`, `:53` and `:49`, which are line
numbers of that 304-line file and of no later one. A dated finding about a blob that no longer
exists is **history and stands**. What was false is **this lane's restatement of it as a present-tense fact
about `caa7d9de`.** ⚠ **Amendments 14 and 15 both moved this file and neither recorded the closure**,
so the registration has carried three closed items as open since `87504e79`. **The supervisor's
board should be corrected: items 35, 36 and 37 are CLOSED, and the closure is `87504e79`.**

⚠ **THE PIN IS UNAFFECTED AND IS NOT RE-TAKEN.** `caa7d9de787b1dc8cf5e45935afcc5ef425b85fc` is the
blob either way; **what changes is what the document says is IN it**, not which blob is pinned.
§22.7 clause 6's remaining sentence — *"re-pinning that file pins the defects along with the
repairs, which is what a pin is for"* — **stands, and is now a statement about items 25 and 27**,
which are carried forward unrepaired on the supervisor's express instruction (§18.7).

#### 22.10.2 🔴 ITEM 40 — **NINE OF THE TEN PINS HAVE NO EXECUTABLE ENFORCEMENT AT GRADING TIME**

| # | the finding | how it was measured | consequence |
|---|---|---|---|
| **40** 🔴 | **§9.1 names `scripts/check_comparator_freeze.py` as THE verifier, and §22.2 pins TEN executables — but that verifier's POPULATION is `analyse_*.py`, `grade_*.py` and `score_*.py` only. Exactly ONE of the ten matches.** | The verifier's own documented population (its docstring, and its `:821` self-test string) is those three patterns under `verification/`, `cases/` and `docs/campaigns/`. **Run at this HEAD: 207 graders in the population; `cases/M6SR/analyse_m6sr.py` appears and reads `NO-MARKERS`** — *correct* pre-compute, since no completion marker can exist while the run root does not. **None of the other nine appears at all**, and none can: `run_m6sr_b5.sh`, `build_m6sr_l1.sh` and the three suites are shell; `write_m6sr_case.py`, `residual_max_over_equations.py` and `verify_agard_ar138_table_b1_1.py` match no pattern. | ⚠ **This is NOT a defect in the verifier.** Its hash-identity limb (`:367`, `:391–395`) compares **worktree bytes against the HEAD blob**, index-independently, and asks *"is the file that ran the file that was frozen?"* — **exactly what §9.1 requires.** The gap is one of **REACH**: after a launch it will answer that question for the comparator and **for nothing else**, so nine pins — including **the sole producer of `SOLVER_RC.txt`, which rule 4's completion check reads** — are enforced by **prose alone**. **NOT REPAIRED: widening a named verifier's population is a grading-path question and is the supervisor's**, and it is a change to a `scripts/` artifact this document pins. **Stated before a launch is ordered, not at the drop path.** |

⚠ **AN HONEST BOUNDARY ON THAT MEASUREMENT.** The verifier's repo-wide run returned **rc 3
(`EXIT_VIOLATION`)** on a summary of **5 `AMBIGUOUS-SCOPE`, 4 `AMENDED_AFTER`, 28 `FROZEN`, 158
`NO-MARKERS`, 12 `UNFROZEN`**. **The 12 violating rows are OTHER campaigns' graders, not M6SR's**
— M6SR's single row is `NO-MARKERS`. **This lane did not adjudicate them**: they are outside this
registration and outside this team's territory, and a repo-wide `FAIL` is reported here only so
that nobody later reads *"the freeze checker passes"* into a run it never made.

#### 22.10.3 WHAT THIS ADDENDUM DOES **NOT** DO

- **It moves NO gate, NO threshold, NO cap and NO label**, and it **does not re-take a single pin**
  — every sha in §22.2 was re-verified unmoved at this commit and stands.
- **It touches NO code**, adds **no path to §9's table**, runs **no ladder compute**, and neither
  freezes nor launches.
- **It does not repair item 40**, and it does not repair items 25 or 27.

**Cost: host arithmetic and git reads. ZERO container-seconds and zero ladder core-minutes.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–4835** of this file — the whole of it up to and including
§22.9's closing line, and therefore every guaranteed range §15.10 through §22.9 asserts — are
**byte-identical** before and after this append, both rendering to sha256
**`5a1287f312cbd93cda84da33991e265e35ba5029d0f4a1086ca0fbd6e336ee4f`** *(the value asserted and
re-derived inside the commit invocation that carries this section; the commit ABORTS if it moves)*.

#### 22.10.4 ⚠ **ITEM 5's CODE LIMB APPEARS CLOSED AT THE PINNED BLOB — REPORTED IN OUR FAVOUR, AND THEREFORE HELD TO A HIGHER STANDARD, NOT A LOWER ONE**

**WHY THIS IS STATED AT ALL.** §22 exists so that no launch runs an instrument the registration
does not name. **The reverse error is also live:** a supervisor deciding whether to launch reads
item 5 as 🔴 *"BOTH Gate P channels are dead … 615.24 core-min of registered ladder cannot produce
Sanaa's named first-physics figure at all."* **That is a claim about a blob this amendment has just
struck as a pin**, and it was never re-measured against the blob the ladder will actually run.

⚠ **A FINDING THAT FAVOURS US IS THE EASIEST ONE TO GET WRONG**, so it is stated with the control
first and the result second, and it is **REPORTED, NOT RULED.**

**THE CONTROL — THE SAME READER REPRODUCES ITEM 5 EXACTLY ON ITEM 5's OWN SUBJECT.** An AST call
graph over the module (edges from every `ast.Call` inside a `FunctionDef`, by `Name.id` or
`Attribute.attr`; reachability by transitive closure from `main`) was run on **both** blobs:

| blob | functions defined | reachable from `main()` | **defined but UNREACHABLE** | `cfd_sections` occurrences |
|---|---|---|---|---|
| `97cbe039` — **item 5's own subject**, struck as a pin at §18.3.2 | 50 | **48** | **exactly two: `gate_p`, `set_to_set_assignment`** | 6 |
| **`9b963ad4`** — **the blob pinned by §22.2, the one that will run** | 66 | **62** | four: `__init__`, `_control_unreachable_sentinel`, `_fn`, `visit_Call` | **15** |

**The top row REPRODUCES ITEM 5 TO THE FUNCTION NAME AND THE COUNT** — item 5 recorded *"48
functions are reachable from `main()`. `gate_p()` is NOT. `set_to_set_assignment()` is NOT."*
**A reader that reproduces the historical NO is licensed to report the current YES**, which is the
only reason the bottom row is stated at all. ⚠ **The bottom row's own control is stronger than a
missing-name plant:** the reader still reports **four** defined-but-unreachable functions on the
pinned blob — one of them named **`_control_unreachable_sentinel`**, which the comparator appears
to carry for exactly this purpose. **A reachability reader that finds nothing unreachable is a
fail-open wearing a pass; this one does not.**

**AT THE PINNED BLOB, `gate_p` AND `set_to_set_assignment` ARE BOTH REACHABLE FROM `main()`**, and
`cfd_sections` occurrences have gone **6 → 15**. **`sampleDict` appears 9 times** across
`write_m6sr_case.py`, `build_m6sr_l1.sh` and `run_m6sr_b5.sh`, where item 5 recorded that *"the
build driver writes no `sampleDict`."*

#### WHAT THIS DOES **NOT** ESTABLISH — AND THE LIMITS ARE THE POINT

1. ⚠ **REACHABILITY IS NOT EXECUTION.** The call graph resolves an attribute call by its
   **attribute name alone**, so it **over-approximates**: it proves `gate_p` is no longer
   orphaned, **not** that a `--grade` run reaches it, nor that it returns a value. **Item 5's
   claim is contradicted on its own instrument; it is not disproved on the physics.**
2. ⚠ **IT SAYS NOTHING ABOUT `X1`.** §17.8 rules that *"`X1` STANDS"* — the prediction that `D1`
   is indeterminate and Gate P's per-station channel returns **`NOT A RESULT`**. That is the
   **DATA** limb and it is **untouched here**; item 5 was the **CODE** limb. **A live invocation
   path for a channel predicted to return `NOT A RESULT` is not a deliverable.**
3. ⚠ **THE READER IS NOT A FILED ARTIFACT.** It is a throwaway AST walk, fully described above so
   it is reproducible, but **it is not a pinned control suite and this document does not cite
   it.** A finding that moves a 🔴 item in the lab's favour deserves an executable control, and
   **that control does not exist yet.**

🔴 **THEREFORE: REPORTED, NOT RULED. THIS LANE DOES NOT DECLARE ITEM 5 CLOSED.** Item 5 was
authored by another pass, it is registered 🔴, and re-grading another lane's finding on a
favourable measurement is exactly the move the supervision charter reserves as **check 3 —
big-claim verification before belief, done personally and never delegated.** **The measurement is
handed up; the ruling is the supervisor's.**

---

## 23. AMENDMENT 17 — 2026-09-04, **PRE-COMPUTE**. **ITEM 40 IS REPAIRED IN THE INSTRUMENT**: THE NAMED VERIFIER'S REACH GOES FROM **1 OF 10 TO 10 OF 10**, A **PARTIAL** POPULATION NOW REFUSES THE WAY AN EMPTY ONE ALREADY DID, AND §9's TABLE IS EXTENDED TO THE FULL PINNED SET

**WHY THIS AMENDMENT EXISTS.** §22.10.2 registered item 40 and expressly declined to repair it:
*"widening a named verifier's population is a grading-path question and is the supervisor's."*
**The supervisor has now ruled it**, in two parts — widen the verifier's reach, and extend §9's
table to the full pinned set — and this amendment takes those two and nothing else.

**THE PRE-COMPUTE CONDITION, STATED AND CHECKED, NOT ASSUMED.** Rule 2 requires the condition and
how it was checked. **The run directory that does not exist is `verification/runs/M6SR_runs`.**
Checked **with a plant at the exact searched path**, in one invocation, by the same reader
throughout:

| step | reader `[ -d verification/runs/M6SR_runs ]` |
|---|---|
| before the plant | `ABSENT` |
| **with the plant present** | **`PRESENT`** — the reader is shown able to see a present tree |
| plant removed | `ABSENT` |
| independent `find verification/runs -maxdepth 1 -name 'M6SR_runs'` | **0 hits** |

**No ladder compute has been run. No gate, threshold, cap or label moves in this amendment.**

### 23.1 ITEM 40, RE-MEASURED AT SOURCE BEFORE ANYTHING WAS TOUCHED

§22.10.2's finding is not carried forward on trust; it was re-derived at this HEAD, from the
verifier's own source and from a live repo-wide run:

| what | measured |
|---|---|
| the verifier's population patterns | `analyse_*.py`, `grade_*.py`, `score_*.py` over roots `verification/`, `cases/`, `docs/campaigns/` |
| pinned executables (§22.2) matched | **1 of 10** — `cases/M6SR/analyse_m6sr.py`, reading `NO-MARKERS` |
| why the other nine cannot match | **three live under `scripts/`, which is outside every walk root**; **six are `.sh`**, which no pattern can match |
| repo-wide run | **207 graders, rc 3**, of which the 12 violating rows are **other campaigns'** |

⚠ **AND THE SHARPEST PART, WHICH IS THE VERIFIER'S OWN.** Its docstring already carried the clause
**`EMPTY POPULATION IS A REFUSAL, NOT A CLEAN BILL` (charter 2p.2)**. The tool therefore *already
understood the population-scope hazard* — **for the EMPTY case** — and was **silent on the PARTIAL
one**. *"I checked 1 of 10"* returned exactly what *"I checked 10 of 10"* returns. **This is the
campaign's recurring shape one more time: a checker whose scope excludes most of what it exists to
check, reporting success on the fraction it looked at.**

### 23.2 THE REPAIR — **NOT MORE GLOBS.** THE REGISTRATION NAMES ITS PINNED SET; THE VERIFIER NOW READS IT

**A longer pattern list reproduces the defect with a longer list**, because it still decides the
population from **file names**, which are a property of nobody's registration. The new
`--registration <path>` flag makes the check read the set **this document pins by blob sha** and
judge exactly that. Three limbs, each able to fail on its own:

| limb | question | failure | exit |
|---|---|---|---|
| **COVERAGE** | is every pinned path judged? A pinned path the walk does not reach is **injected by explicit path**, whatever it is called and wherever it lives. | a pinned path that gets **no row at all** | **REFUSE, 2** |
| **IDENTITY** | do the worktree bytes equal the HEAD blob? **Marker- and scope-independent on purpose**, because the per-row identity test is skipped for any row that is `NO-MARKERS` or `AMBIGUOUS-SCOPE` — which is every M6SR row. | `PIN-DRIFT` | **3** |
| **CURRENCY** | is the HEAD blob one of the blob shas this document **records unstruck** for that path? A file that moved and whose new blob nobody wrote down is unpinned in fact, however many pin tables the document carries. | `PIN-STALE` | **3** |

**A pin inside a `~~strike span~~` is dropped before parsing**, so a pin this document has formally
superseded cannot satisfy CURRENCY. **A registration from which ZERO pins are readable REFUSES** —
the 2p.2 principle one level up: a parser that read a document and found no pin has failed to reach
a pin set, not verified an empty one.

⚠ **WHAT THE PIN LIMBS DELIBERATELY DO NOT DECIDE, stated because a check that overstates its reach
is worse than none:** this document records **several** blob shas for some paths across successive
amendments, and not every superseded row is struck (§22.3 flags that judgement as open and
unruled). **Which recorded sha is IN FORCE is a reading of the strike record, not of the file
system**, and CURRENCY does not take it. It asks only the unambiguous question — **is the current
blob recorded anywhere unstruck** — and prints the count of recorded shas beside every row so the
ambiguity is visible rather than hidden.

### 23.3 THE MEASUREMENT — **1 OF 10 → 10 OF 10**, AND **NO OTHER TEAM'S ROW MOVED**

`scripts/check_comparator_freeze.py` is shared, cross-team instrumentation. **The supervisor's
boundary was explicit: do not adjudicate other campaigns' rows and do not change behaviour for
them.** That is not asserted here, it is measured:

| measurement | before | after | how read |
|---|---|---|---|
| pinned executables in the population | **1 of 10** | **10 of 10** | the tool's own `PIN COVERAGE` line |
| rows in the repo-wide population, **no flag** | 207 | **207** | the summary line |
| rows **with** `--registration` | — | **216** | **exactly +9**, the nine that were prose-enforced |
| repo-wide stdout, **no flag** | — | **BYTE-IDENTICAL to the pre-edit run** | `diff` of the full stdout, rc **3** both sides |
| rows lost, or re-judged, by the widening | — | **0 and 0** | set difference on `(tree, comparator, status)` |
| other campaigns' violating rows | 12 | **12** | unchanged in both runs |
| foreign graders conscripted from `scripts/` | — | **0 of 4** | `analyse_k0d/k0e/k0er3/k0f.py` share `scripts/` and **none is judged** |
| `python3 -O` (§9.2) | — | **byte-identical output** | same run under `-O` |

⚠ **PLANTED CONTROL ON THE BYTE-IDENTICAL CLAIM**, because an equality is worthless from a
comparator not shown able to report an inequality: **one character appended to a single line of the
post-edit output makes the same `diff` report a difference. The plant was SEEN.**

⚠ **THE `scripts/` CONSCRIPTION TRAP WAS REAL AND IS CLOSED BY CONSTRUCTION.** Three pins live in
`scripts/`, a directory the walk roots never reach — and **four heat-transfer graders live there
too**. Following a pin into an out-of-root directory therefore judges **only the pinned names**
(the `restrict` path), never the directory. Had it walked the directory, this repair would have
silently annexed another team's four graders on the strength of a CFD registration.

### 23.4 THE PLANTED CONTROLS — **ELEVEN NEW SELFTEST ARMS, FOUR OF THEM ADVERSE**

Rule 3, and 2p.3(d)'s requirement that a control exercise the **production** path. The selftest
builds a repository in the item-40 shape — one grader the patterns match, one `.sh` inside a walk
root they cannot match, one file outside every root, and **a foreign grader sharing that outside
directory** — and runs **this file as a subprocess** for every exit-code arm.

| arm | must show |
|---|---|
| **adverse** ×3 | the OLD walk **finds** the pattern-matching grader and **MISSES** both the `.sh` and the out-of-root file |
| coverage | both missed files are **IN** the population once the registration is read |
| **adverse** | following the pin into the shared directory **does NOT** conscript the foreign grader |
| additive | the widening **loses no** previously-walked grader and **changes no** previously-returned verdict |
| opt-in | with **no** `--registration`, the population is **unchanged** |
| **partial refusal** | a pinned path with no row → **exit 2**, and the refusal **names** the uncovered path |
| **positive control on that refusal** (2p.3(e)) | the **complete** pin set does **not** refuse — **exit 0**, `PIN COVERAGE: 3 of 3`. *A refusal that fires on everything proves nothing.* |
| strike | a **struck** pin row naming a non-existent path is **not** a live pin and does **not** make the run refuse |
| `PIN-DRIFT` | uncommitted drift on a pinned file → **exit 3** |
| `PIN-STALE` | the file moves and the pin does not → **exit 3**; **and re-pinning it clears the status**, so PIN-STALE is shown to track the *pin* and not merely the *edit* |
| zero pins | a registration pinning nothing **REFUSES** |

**Measured: the whole selftest exits 0 — every pre-existing arm (D471.1–D471.4, 2q, 2p.2, 2p.3(e))
still passes, and every new arm above fires as written.**

### 23.5 §9's FROZEN TABLE, **EXTENDED TO THE FULL PINNED SET** — THE SUPERVISOR'S RULING, IMPLEMENTED

§22.6 recorded that *"adding a path to §9's frozen table is a FREEZE question and is the
supervisor's"* and that **five of the ten were §9-registered and five were not**. **The supervisor
has ruled the extension.** §9's table is **not edited in place** — that would move line numbers
above §15 and falsify seven sections' own assertions — so **§9 is to be read WITH the table below,
which is a registration of paths and nothing else.**

**⚠ THIS MOVES NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Not one number in §5, §5.1, §2.4 or
§10 is touched. **Checked, not asserted: §9 contains no gate, threshold, cap or label** — those
live in §5 and §5.1 — so a registration of paths cannot move one.

| # | path | **what it PRODUCES or GRADES** | role | §9 before |
|---|---|---|---|---|
| 1 | `cases/M6SR/analyse_m6sr.py` | **grades every gate**; the sole producer of the grading record | **graded path** | registered ("comparator") |
| 2 | `cases/M6SR/build_m6sr_l1.sh` | produces the **L1 mesh** and `log.checkMesh` for `B1`–`B3` | **graded path** | registered ("build driver") |
| 3 | `cases/M6SR/write_m6sr_case.py` | **§8's sole case-file writer** — produces `0/`, `system/`, `constant/`, and the `sampleDict` every surface reading is taken through | **graded path** | 🔴 **NOT registered** — §18.3.1's hole, **CLOSED HERE** |
| 4 | `cases/M6SR/run_m6sr_b5.sh` | **sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`** — read by Gate A **and by rule 4's strict completion check** | **graded path** | 🔴 **NOT registered** — §18.3.1's hole, **CLOSED HERE** |
| 5 | `scripts/residual_max_over_equations.py` | **`G2`'s only instrument** (§5.1) — reduces the per-equation residuals `G2` gates on | **graded path** | registered ("residual reducer") |
| 6 | `scripts/verify_agard_ar138_table_b1_1.py` | the **`GF2` reference loader** — produces the AGARD Table B1-1 ordinates every surface comparison is graded against | **graded path** | registered inside the AGARD row, **not as its own row** |
| 7 | `scripts/check_comparator_freeze.py` | **grades the grading path itself** — §9.1 names it as *the* verifier | **the verifier** | named in **§9.1 prose only**, never in the table |
| 8 | `cases/M6SR/check_m6sr_launch_path.sh` | **grades nothing and produces no artifact any gate reads** — launch-path controls, writing only into a `mktemp` tree it deletes | control suite | not registered |
| 9 | `cases/M6SR/check_m6sr_build_path.sh` | **grades nothing** — build-path controls, items 38/39 | control suite | not registered |
| 10 | `cases/M6SR/check_m6sr_cap_binds.sh` | **grades nothing** — the cap-binding controls `K1`–`K6` | control suite | not registered |

⚠ **A TENSION THIS LANE NAMES RATHER THAN BURIES.** §22.6's lane recommended **NO** to §9 for rows
8–10, on the ground that *"a control suite grades nothing, produces no artifact any gate reads, and
writes only into a `mktemp` tree it deletes."* **The supervisor's ruling was the FULL pinned set**,
so all ten are registered here — and the `role` column preserves the distinction rather than
erasing it, so a reader can see that rows 8–10 are registered **as pinned instruments, not as
graded-path producers.** **If the ruling meant only the seven, rows 8–10 come out and the pins in
§22.2 still stand; that is the supervisor's to say.**

#### 23.5.1 🔴 **THE INVOCATION IS REGISTERED, NOT LEFT TO THE OPERATOR** — BECAUSE THAT IS ITEM 40's WHOLE LESSON

A repair that must be *remembered* at grading time is enforced by prose, which is the defect this
amendment exists to close. **The verifier's M6SR invocation is therefore registered here, verbatim:**

```
python3 scripts/check_comparator_freeze.py --repo . \
    --registration verification/campaign/M6SR_PREREGISTRATION.md
```

**Without `--registration`, the check reaches ONE of the ten and reports a clean bill on the other
nine by silence.** The flag is not an option on this ladder; it is the check.

### 23.6 🔴 **THE INSTRUMENT'S OWN PIN MOVED, IN THIS AMENDMENT, AND IS RE-TAKEN IN THE SAME BREATH**

**This amendment edits one of the ten pinned executables** — the verifier itself, row 7 above.
§22.2's pin for it is therefore **FALSE IN FORCE at this commit** and is struck, rule 6, by quote:

> 🔴 **STRUCK BY QUOTE:** ~~*"| **`scripts/check_comparator_freeze.py`** (named by §9.1 as the verifier) | **`dabd740e56a017edbc04b9c2b866c93c661ce0ab`** | `2871fabbab2bf8a126af49d4cdf6c7c6cb3a7ef9fd107b2afa4e942771b54709` | 904 | **`5c31a23c`** | **§9 registered** — pin UNMOVED |"*~~

**THE NEW STANDING PIN**, re-derived with `git hash-object` on the working tree and
**RE-HASHED A SECOND TIME INSIDE THE SAME SHELL INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION,
WITH THE COMMIT ABORTING IF IT HAD MOVED** — §22.2's own guard, kept:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`scripts/check_comparator_freeze.py`** (the verifier, §9.1 and §23.5 row 7) | **`d7a8b0856454bf0a0bd8e151af056c52131935d6`** | `653dab8eae6028dd0038d4dd7d44bd5b665ae4e52b77ef0149e2af6389fbd075` | **1,297** | **§9 registered**, §23.5 — **RE-PINNED HERE** |

⚠ **THE OTHER NINE PINS ARE UNMOVED AND WERE RE-VERIFIED, NOT ASSUMED.** Every one of the nine was
re-hashed at this HEAD and matches §22.2 exactly; **this amendment touches no code but the
verifier.** The tool's own run says so: **9 `PIN-OK` before this section was committed, with the
verifier alone reading `PIN-DRIFT`** — the instrument convicting its own stale pin, on a plant
nobody had to fabricate.

⚠ **AND THE JUDGEMENT IS FLAGGED FOR THE SUPERVISOR.** A lane may pin shas and report (§22.6, item
32) and the supervisor ordered the edit that moved this blob, so leaving the pin stale would make
the registration name an instrument that no longer exists. **The re-pin is taken for that reason
and for no other. It is the supervisor's to overrule.**

### 23.7 🔴 **ITEM 41 — NEW. THE LADDER WRITES NO COMPLETION MARKER, SO THE VERIFIER'S FREEZE-MARGIN LIMB IS UNREACHABLE FOR THIS CAMPAIGN BY CONSTRUCTION**

| # | the finding | how it was measured | consequence |
|---|---|---|---|
| **41** 🔴 | **Every one of the ten rows reads `NO-MARKERS`, and will still read `NO-MARKERS` AFTER a launch.** The verifier dates a freeze by comparing a comparator's commit against the earliest `DONE.<CASE>` marker **in the comparator's own tree**. **The M6SR chain writes no `DONE.` marker at all** — and §9.1 rules that the executables live under `cases/M6SR/` while any marker would be produced into `verification/runs/M6SR_runs/`, a different tree. | The string `DONE.` occurs **zero** times in `run_m6sr_b5.sh`, `build_m6sr_l1.sh` and `analyse_m6sr.py` — all three read at their pinned blobs. Live run: **all ten rows `NO-MARKERS`**, which the tool reports as *"out of evidence reach"* rather than as a pass. | ⚠ **§9.1's claim that the verifier *"can verify at grading that the frozen file IS the file that ran"* is TRUE ONLY THROUGH THE IDENTITY LIMB ADDED HERE**, which is marker-independent for exactly this reason. The **freeze-margin** half of the check — *did the comparator's commit precede the first case?* — **cannot fire for this ladder, before or after a launch.** **This is not a hole in the freeze:** M6SR's freeze proof is the **pre-registration commit ordering** plus the run root's plant-verified absence, which is a valid and independent proof. **What is false is any reading of a green from this tool as a marker-dated freeze margin for M6SR.** **NOT REPAIRED:** whether the chain should emit `DONE.` markers, and into which tree, is a §9/§10 mechanics question and is the supervisor's. |

### 23.8 🔴 **ITEM 42 — NEW. THE REGISTERED INVOCATION CANNOT BE GATED ON `exit 0`, BECAUSE TWELVE FOREIGN ROWS HOLD THE REPO-WIDE EXIT CODE AT 3**

| # | the finding | consequence |
|---|---|---|
| **42** 🔴 | The invocation registered at §23.5.1 is **repo-wide**, and **12 `UNFROZEN` rows belonging to other campaigns** hold its exit code at **3** regardless of M6SR's state. **A grading gate written as *"the freeze check exits 0"* would be UNSATISFIABLE for this ladder no matter how clean M6SR is.** | The M6SR-side criterion must therefore be read from the **`PIN COVERAGE` line and the M6SR rows**, not from the process exit code: **`10 of 10` covered, `10 PIN-OK`, `0 violating`, and no M6SR row in a `VIOLATING` status.** ⚠ **A criterion read as a substring of stdout is weaker than an exit code, and this lane says so plainly.** The clean fix is a mode that restricts the population to the registered pin set, so the exit code becomes M6SR's own. **NOT TAKEN: that is a grading-criterion design decision, it is the supervisor's, and this amendment does not pre-empt it.** ⚠ **The 12 foreign rows are NOT adjudicated here** — outside this registration and outside this team. |

### 23.9 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** Nothing in §5, §5.1, §2.4 or §10 is touched.
2. **It does NOT adjudicate another campaign's row**, and it changes **no** behaviour for one — measured byte-for-byte, §23.3.
3. **It touches exactly ONE code artifact**, the verifier, and re-pins it in the same breath (§23.6). **The other nine pinned files are unmodified**, re-verified at this HEAD.
4. **It runs NO ladder compute.** No `B2` march, no `B5` solve, no queue row, **no container**. **`verification/runs/M6SR_runs` does not exist**, verified with a plant at the exact searched path both before this work and after it.
5. **It does NOT freeze and it does NOT launch.** Rule 2's freeze and the launch decision are the supervisor's; a lane may not take either.
6. **It does not repair items 41 or 42**, which it raises, nor items 25 or 27, which are carried forward unrepaired on the supervisor's express instruction (§18.7).
7. **It does not re-open items 35, 36 and 37**, which §22.10.1 measured **CLOSED** at `87504e79`, nor item 5, whose **CODE** limb §22.10.4 reported closed and whose **DATA** limb (`X1`) stands untouched — **reachability is not execution.**

### 23.10 THE STRIKE AUDIT — RUN ON THIS SECTION'S OWN DIFF

The subjects are the **two values this amendment declares FALSE IN FORCE**: the blob sha and the
file sha256 quoted inside §23.6's single strike span. **Named structurally and deliberately not
re-typed**, for the reason §22.5's audit discovered when it went red on its own first draft. Every
occurrence of each of them in the text this amendment adds was located and classified, and **each
one sits inside the `~~…~~` strike span in §23.6.** ⚠ **Rule 3 on the auditor itself:** a false sha
was planted on a plain, unstruck prose line and the auditor **must** report it `UNCLASSIFIED`; the
audit **refuses** rather than passing if the plant is not seen. **The plant was SEEN.** The result
is printed in the commit that carries this section.

### 23.11 COST — RULE 12

| item | predicted | **actual** | ratio | attribution |
|---|---|---|---|---|
| repo-wide verifier runs ×4 (baseline, no-flag, flagged, `-O`) | ~90 s wall at 1 rank = **1.50 core-min** | **284 s** wall at 1 rank = **4.73 core-min** | **3.15** | **misprediction, not contention.** The walk runs a `git log`/`git grep` **per row** over 207–216 rows; the estimate treated the whole walk as one git pass. |
| selftest, code and document work | — | **host arithmetic, ~0.5 core-min** | — | — |

⚠ **`cost_basis` HONESTY, rule 12.** **One run was timed directly — the baseline, at 71 s wall,
1 rank.** The other three are of the same two shapes and are **CHARGED AT THAT MEASURED RATE**,
not separately measured; `4 × 71 s` is the figure above. **It is a charge at a measured rate, not
four measurements, and is labelled so rather than presented as four.** The flagged run walks 9 more
rows than the baseline, so the true figure is **slightly higher** than charged — the charge is
stated as a floor, not a ceiling.

**Container-seconds, reported as WASTE and SEPARATELY, never absorbed into a step's cost:
ZERO — this pass started no container and ran no solver.** **Ladder core-minutes: ZERO.**

⚠ **The box was NOT idle.** Heat-transfer's `T3e` held **8 ranks of 16**. This pass took **1 rank**
and did not saturate.

### 23.12 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.8 → v1.9 (amendment 17, pre-compute). The frozen file was NOT edited; this section is
APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10
through §22.9 give: editing it would change a line above §15 and falsify those sections' own
assertions, on which other records depend — **and at least one such citation sits inside an
executable check.** **The bump is recorded HERE. The supervisor may restate the version in the
header at the re-freeze, which is a status flip they own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–4973** of this file — the whole of it up to and including
§22.10.4's closing line, and therefore every guaranteed range §15.10 through §22.10 asserts — are
**byte-identical** before and after this append, both rendering to sha256
**`629b1fdabdf26f29b9aa439f9c23649e1e0bf33753fa6294d84eca4418ebe190`** *(asserted here and
re-derived inside the commit invocation that carries this section; the commit ABORTS if it moves)*.

### 23.13 THE STANDING QUESTION — **ANYTHING ELSE BETWEEN THIS DOCUMENT AND A LAWFUL LAUNCH?**

**YES. Two, both raised above, both the supervisor's:**

1. **Item 41** — the freeze-margin limb of the named verifier is **structurally unreachable** for
   this ladder, before and after a launch, because the chain writes no completion marker. **The
   identity limb added here is what makes §9.1's promise deliverable at all.**
2. **Item 42** — the registered invocation's **exit code is not M6SR's to earn**; twelve foreign
   rows hold it at 3. A gate phrased as *"the freeze check passes"* is unsatisfiable as written.

**Neither blocks a launch on the physics. Both are defects in what a green from the named verifier
would MEAN**, and both would have been discovered after the fact rather than before it.

## 24. AMENDMENT 18 — 2026-09-04, **PRE-COMPUTE**. **ITEMS 41 AND 42 ARE RULED AND CLOSED.** THE VERIFIER GAINS A **REGISTRATION-RESTRICTED MODE** WHOSE EXIT CODE M6SR CAN EARN, THE GRADING CRITERION IS REGISTERED **AS AN EXIT CODE** RATHER THAN AS A SUBSTRING, AND ITEM 41's UNREACHABLE LIMB IS REGISTERED AS A **STANDING CAVEAT ON THE CRITERION ITSELF**

**Both items were raised by §23.7 and §23.8 as the supervisor's to rule. The supervisor has
ruled both.** This section implements the two rulings, in the instrument and in the registration,
and takes nothing that was not ruled.

### 24.0 THE LAWFULNESS CONDITION, AND HOW IT WAS CHECKED — **NOT ASSERTED, PLANTED**

Rule 2 permits amendment **before first compute** and requires the condition to be stated **and how
it was checked**. The condition is that **no M6SR compute has happened**, and the check is that the
run root §18.6 pins does not exist.

**Checked by execution, with a live plant, at the exact searched path.** The searcher was run
three times in one shell invocation: it reported **0** matches for `verification/runs/M6SR*`; a
probe directory was then created **at that path** and the same searcher reported **1**; the probe
was removed and the searcher reported **0** again. **A zero from a reader shown able to see a
non-zero.** ⚠ **The plant was SEEN.** No `B2` march, no `B5` solve, no container, no queue row.

### 24.1 🔴 ITEM 42, RULED — **A GATE WHOSE PASS CONDITION DEPENDS ON ANOTHER TEAM'S STATE IS NOT A GATE THIS CAMPAIGN CAN PASS**

§23.8 measured the defect and recommended a **substring** reading. **The supervisor declined that
reading and ruled the structural fix.** §23.8's recommendation is therefore **FALSE IN FORCE** and
is struck, rule 6, by quote:

> 🔴 **STRUCK BY QUOTE:** ~~*"The M6SR-side criterion must therefore be read from the **`PIN COVERAGE` line and the M6SR rows**, not from the process exit code: **`10 of 10` covered, `10 PIN-OK`, `0 violating`, and no M6SR row in a `VIOLATING` status.**"*~~

⚠ **THE REST OF §23.8 STANDS AND IS NOT STRUCK** — its measurement, its warning that a substring
criterion is weaker than an exit code, its naming of the restricted mode as the clean fix, and its
refusal to adjudicate the twelve foreign rows. **Only the recommended READING is superseded.**
**The finding was right; the remedy it proposed was the weaker of the two available, and the lane
said so itself.**

⚠ **THE TWELVE FOREIGN ROWS ARE STILL NOT ADJUDICATED HERE.** They belong to other campaigns,
they are outside this registration and outside this team, and **nothing in this amendment changes,
suppresses, re-judges or even reads a verdict on one.** §24.3 proves that byte-for-byte.

### 24.2 THE REPAIR — `--restrict-to-registration`, AND THE FOUR THINGS IT IS **NOT**

`scripts/check_comparator_freeze.py` gains one flag. With it, the **population IS the pinned set**:
each directory a registration pins a file in is visited once, restricted to the pinned basenames,
and the `analyse_*/grade_*/score_*` name patterns **never run**. The exit code is then earned by
that set alone.

| the property | how it is held |
|---|---|
| **it JUDGES ONLY the registered set** | `walk_registered()` builds the population from the pin map and nothing else. A foreign file cannot enter it, because entry is by registration and not by name or by directory. |
| **it CHANGES NOTHING outside that set** | The mode is a new branch behind a flag that defaults off. **The unrestricted invocation's walk is untouched** — proved byte-identically in §24.3, not argued. A foreign row is **not silenced by this mode; it was never in it.** |
| **it is NOT LENIENT** | Every refusal and every violation that could fire unrestricted still fires here on a pinned path: an **uncovered pin REFUSES** (exit 2), **PIN-DRIFT** and **PIN-STALE** are **violations** (exit 3), an **empty restricted population REFUSES**, and a pinned comparator that is itself `UNFROZEN`, `UNCOMMITTED` or `MODIFIED_AFTER_COMMIT` **still exits 3**. Rows are produced by the **same** `check_tree()` as the unrestricted walk, so a pinned path is judged **identically** in both; only the population differs. |
| **it is NOT a way to restrict to nothing** | The flag **requires** `--registration` and refuses without it (exit 2). A restriction with no registered set is not a narrower population, it is an empty one, and 2p.2 already rules on that. |

⚠ **THE NEAR-MISS §23's LANE NAMED IS HELD, AND MEASURED.** Three of the ten pins live in
`scripts/`, which also holds **four `analyse_k0*.py` graders belonging to heat-transfer**. Under
restriction the tool judges **only the pinned names** in that directory. **Measured on this
repository: zero of those four appear in the restricted output**, and the same reader **does** see
`scripts/verify_agard_ar138_table_b1_1.py`, which is pinned — **so the zero is a reading, not a
blindness.** Following a registration into a shared directory must never annex another team's rows.

### 24.3 THE MEASUREMENT — **THE RESTRICTED EXIT CODE IS M6SR's**, AND THE UNRESTRICTED RUN IS **BYTE-IDENTICAL**

**The defect, restated as a measurement at the commit this work began from (`6b7a71e8`):** the
repo-wide invocation reported **`PIN COVERAGE: 10 of 10 … 10 PIN-OK, 0 violating`** — a perfectly
clean registered set — **and exited 3 anyway**, on **12 `UNFROZEN` rows out of 216 graders**, none
of them M6SR's. **That is item 42 in one line: the criterion was unsatisfiable while the campaign
was already correct.**

| what was run | result |
|---|---|
| unrestricted, at `6b7a71e8`, twice | **deterministic** — the two runs are byte-identical; **exit 3**; 216 graders, **12 violating**; **10 of 10 pinned, 10 PIN-OK, 0 violating** |
| **restricted**, same registration | **population = the 10 pinned executables**, **zero** foreign rows, **0 violating** |
| unrestricted, after the change | **exit 3**, 216 graders, **12 violating** — unchanged |

🔴 **THE NON-INTERFERENCE PROOF, BYTE-FOR-BYTE.** The freeze-walk section of the unrestricted
output — the header through the `CANNOT SEE:` line, **every one of the 216 rows and all 12 foreign
violations** — renders to sha256
**`dab68a6130e67bd7214d6a223a147e387ddef8975a4cb2a14b6066fc5ffccdc2`** **before this change and
after it. Identical.**

⚠ **RULE 3 ON THAT COMPARISON.** A byte comparison that cannot report a difference is not evidence
of sameness. **Two plants, both SEEN:** the same comparator was run against a copy of the baseline
with **one byte** altered and reported **DIFFER**; and against the restricted output and reported
**DIFFER**. **A comparison shown able to say "different" said "identical".**

⚠ **AND THE ONE THING THAT DID CHANGE IS NAMED, NOT BURIED.** In the **pin** section — not the
walk — exactly one row moved, and only while this amendment was in flight: the verifier's own row,
`PIN-OK` → `PIN-DRIFT`, because the file being edited **is** one of the ten pinned executables.
**That is the instrument convicting the very edit that created it, on a plant nobody had to
fabricate**, and it is resolved by the re-pin at §24.7. **No other pin row moved; no walk row
moved; the exit code did not move.**

### 24.4 🔴 **THE REGISTERED GRADING CRITERION — VERBATIM, AND AS AN EXIT CODE**

§23.5.1's principle, which the supervisor endorsed and which this section obeys: **a repair that
must be REMEMBERED at grading time is enforced by prose, which is the defect itself.** The
criterion is therefore registered here as the exact command line, and the pass condition is the
process exit code:

```
python3 scripts/check_comparator_freeze.py --repo . \
    --registration verification/campaign/M6SR_PREREGISTRATION.md \
    --restrict-to-registration
```

> **CRITERION `FZ1` — PASS if and only if that invocation exits `0`.**
> **Exit `2` is a REFUSAL and is NOT A RESULT. Exit `3` is a GATE FAIL. No other exit code is a
> pass, and no reading of stdout may substitute for the exit code.**

⚠ **`--restrict-to-registration` IS NOT AN OPTION ON THIS LADDER; IT IS PART OF THE CRITERION.**
Without it the exit code is not M6SR's to earn (§24.1). Without `--registration` the check reaches
**one** of the ten and the restricted flag refuses outright.

⚠ **§23.5.1's REPO-WIDE INVOCATION IS RETAINED AND IS NOT STRUCK.** It remains registered as the
**cross-team diagnostic** — the run that shows M6SR's rows in their true repository context and
that is the only one able to report a foreign regression. **It is a diagnostic. `FZ1` is the
criterion.** The two are different questions and this registration now says which is which.

### 24.5 🔴 **ITEM 41, RULED — THE STANDING CAVEAT, ON THE CRITERION ITSELF**

**The supervisor's ruling, adopted in terms:** the freeze-margin limb is **structurally
unreachable** for this ladder. The verifier dates a freeze from `DONE.<CASE>` markers **in the
comparator's own tree**; §9.1 puts the executables under `cases/M6SR/` while any marker would be
produced into `verification/runs/M6SR_runs/`, a different tree; and the string `DONE.` occurs
**zero** times in all three pinned drivers. **All ten rows read `NO-MARKERS` and always will,
before and after a launch.**

> 🔴 **STANDING CAVEAT ON CRITERION `FZ1`, WHICH IS PART OF THE CRITERION AND NOT A FOOTNOTE TO IT.**
> **A PASS on `FZ1` IS NOT A MARKER-DATED FREEZE MARGIN AND MUST NOT BE READ AS ONE.** What `FZ1`
> tests is **COVERAGE, IDENTITY and CURRENCY** — that every pinned executable is judged, is the
> file that was committed, and is pinned at a sha this registration records unstruck. It does
> **not** test *"was the comparator committed before the first case finished"*, because for this
> ladder that limb cannot fire. **M6SR's freeze proof is the pre-registration commit ordering plus
> the plant-verified absence of the run root (§24.0), which is a valid and independent proof —
> this is NOT a hole in the freeze.** A grader who reads a green here as a dated margin has read
> something the tool did not say.

⚠ **AND THE CAVEAT IS CARRIED IN THE OUTPUT, NOT ONLY HERE.** The restricted mode **prints it
beside the verdict** whenever any row in the registered set is `NO-MARKERS`, counting them — for
exactly the reason §23.5.1 gives about prose. **On this repository it prints `10 of 10`.** A
negative control shows the caveat is **conditional and not boilerplate**: a registered set with no
`NO-MARKERS` row does not get it (§24.6).

⚠ **NO `DONE.` MARKER WAS ADDED TO MAKE THE LIMB REACHABLE**, on the supervisor's express
instruction and this lane's agreement. **A marker written to satisfy a checker, rather than because
a step completed, is a fabricated completion.** Whether the chain should emit markers at all, and
into which tree, remains a §9/§10 mechanics question and remains the supervisor's.

### 24.6 THE CONTROLS — **HOW EACH MUTANT DIED, NOT MERELY THAT IT DID**

**Thirty new selftest arms**, all inside `--selftest`, all driving **this file as a subprocess** so
what is exercised is the command line the criterion is written against. Total **87 arms, 0 FAIL**,
rc `0`. Every arm below states the **mechanism** of death, because three suites this campaign
killed mutants for the wrong reason and only *how* exposed it.

| the plant | how it died | why that is the right death |
|---|---|---|
| **the defect itself**, reproduced: a clean registered set beside two late foreign graders | unrestricted run printed `PIN COVERAGE: 2 of 2 … 2 PIN-OK, 0 violating` **and exited 3** | the synthetic repo reproduces the measured shape, so the fix is tested against the disease |
| the same repo, one flag added | **exit 0**, `2 grader(s) in the population, 0 violating` | the exit code became the registration's to earn — the whole ruling, in one arm |
| foreign grader in an **unrelated tree** | its name is **absent** from restricted stdout and **present** in unrestricted stdout | the second half is what makes the first half mean something: *silence, not suppression* |
| foreign grader **inside a pinned directory**, name-pattern matching | same — absent restricted, present unrestricted | exclusion is **by registration**, not by directory. This is §24.2's near-miss, planted |
| non-interference | unrestricted stdout **byte-identical** across runs either side of a restricted run | — |
| **PLANT on that comparison** | the same equality test reported **DIFFER** against the restricted output | a byte comparison that cannot see a difference proves nothing |
| a pinned path that is not on disk | **exit 2**, refusal **names the path** | coverage short of the pinned set is a check that did not reach its subject |
| worktree drift on a pinned file | **exit 3**, stdout says **`PIN-DRIFT`** | restricted is not lenient about identity |
| the drift committed, pin not moved | **exit 3**, stdout says **`PIN-STALE`** | restricted is not lenient about currency |
| **adverse pair** for that | re-pinning the moved file returns **exit 0** | the failure tracked the **pin**, not merely the edit |
| **a pinned comparator that is itself `UNFROZEN`** (separate repo; pins deliberately clean) | **exit 3**, and the pin section reads **`1 PIN-OK, 0 violating`** | **the ROW earned the failure, not the pin limbs.** Restricting the population does not restrict the standard applied to what is in it — the single most important arm here |
| `--restrict-to-registration` with no `--registration` | **exit 2** | a restriction to nothing is an empty population |
| item 41's caveat | printed, and **counts** the rows: `1 of 2 restricted row(s) are NO-MARKERS` | — |
| **negative control** on the caveat | a registered set with **no** `NO-MARKERS` row does **not** print it, and still **exits 0** | the caveat is conditional, not boilerplate. **Reported as a control that is deliberately a no-op on its subject** |
| **is the plant even adverse?** | measured at source before any arm ran: foreign rows are genuinely `UNFROZEN`, the registered row genuinely `FROZEN` | a control that fires on a tree that was never guilty proves nothing |

⚠ **`rc` PARITY.** `--selftest` returns **`0` under both `python3` and `python3 -O`**, and the two
runs' stdout is **byte-identical** — so no arm rests on an assertion the optimiser removes.
⚠ **NO BARE `assert` ANYWHERE IN THE FILE.** Verified by **AST parse**, not by grep: the file
contains **zero** `ast.Assert` nodes, and **the detector was planted** — one `assert` appended to a
copy of the source **was seen**. Every arm goes through the `check()` helper, which prints and
records rather than raising.

### 24.7 🔴 **THE INSTRUMENT'S OWN PIN MOVED AGAIN, AND IS RE-TAKEN IN THE SAME COMMIT**

**This amendment edits one of the ten pinned executables** — the verifier itself, §23.5 row 7.
§23.6's pin is **FALSE IN FORCE** at this commit and is struck, rule 6, by quote:

> 🔴 **STRUCK BY QUOTE:** ~~*"| **`scripts/check_comparator_freeze.py`** (the verifier, §9.1 and §23.5 row 7) | **`d7a8b0856454bf0a0bd8e151af056c52131935d6`** | `653dab8eae6028dd0038d4dd7d44bd5b665ae4e52b77ef0149e2af6389fbd075` | **1,297** | **§9 registered**, §23.5 — **RE-PINNED HERE** |"*~~

**THE NEW STANDING PIN**, derived with `git hash-object` on the working tree and **RE-DERIVED
INSIDE THE SAME SHELL INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT ABORTING
IF IT HAD MOVED** — §22.2's guard, kept:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`scripts/check_comparator_freeze.py`** (the verifier, §9.1 and §23.5 row 7) | **`38ea39e843d2f316c9dab36a27c0c3654cf9d0d1`** | `6954cc6d9b663175146853c3db3e7e2e3bd0fdc4bc04c4cc553028642cf6d207` | **1,622** | **§9 registered**, §23.5 — **RE-PINNED HERE** |

⚠ **THE OTHER NINE PINS ARE UNMOVED AND WERE RE-VERIFIED, NOT ASSUMED** — every one read `PIN-OK`
at this HEAD in the run reported at §24.3, while the verifier alone read `PIN-DRIFT`. **This
amendment touches no code but the verifier.**

⚠ **AN HONEST LIMITATION OF THE STRIKE-BY-QUOTE CONVENTION, NAMED RATHER THAN GLOSSED.** Striking a
row **by quote in a later section does not remove the original row from the file**, so the parser
still reads §22.2's and §23.6's superseded rows as live and reports **more than one recorded sha**
for this path. **CURRENCY is satisfied by the new sha above**, and the tool's own docstring already
declares that deciding *which* recorded sha is IN FORCE is a reading of the strike record and not
something it takes. **The registration is the authority on which pin is in force, and it is the one
in the table immediately above.**

### 24.8 ⚠ **A JUDGEMENT THIS LANE TOOK, FLAGGED FOR THE SUPERVISOR RATHER THAN BURIED**

The ruling said the restricted mode *"must still REFUSE on a missing pin, on `PIN-DRIFT` and on
`PIN-STALE`."* **It does not go green on any of the three.** But the lab's exit codes distinguish a
**refusal** (`2`, NOT A RESULT) from a **violation** (`3`, GATE FAIL), and the unrestricted mode
already classifies these three as **refusal, violation, violation** respectively.

**This lane kept that classification identical under restriction** rather than promoting the two
pin violations to refusals, on the ground that **the same condition must not carry two different
verdict labels depending on a flag** — that would make the restricted mode a different instrument
rather than a narrower one. **So: a missing pin exits 2; `PIN-DRIFT` and `PIN-STALE` exit 3; none
of the three passes.** ⚠ **If the ruling meant literal exit 2 for all three, this is one line to
change and it is the supervisor's to say.** It is flagged here because reading "REFUSE" as "must
not pass" rather than as "exit 2" is a lane's interpretation of a supervisor's word, and an
interpretation is not an instruction.

### 24.9 §9's ROWS 8–10 — **THE SUPERVISOR HAS RULED; THE RECORD IS CLOSED**

§23.5 registered all ten pinned executables and asked whether rows 8–10, the three control suites,
belonged there. **The supervisor ruled KEEP**, on the reasoning §23.5 itself gave: they are
**pinned instruments, not graded-path producers**, and the `role` column is the correct way to say
so. **The two PRODUCERS the ruling required — `write_m6sr_case.py` and `run_m6sr_b5.sh` — are IN,
and the suites were never required OUT.** **§22.6's contrary recommendation stays NAMED and is not
erased**, so a reader can see the question was contested and how it was settled. **§23.5's table
stands unamended.**

### 24.10 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** Nothing in §5, §5.1, §2.4 or §10 is touched. `FZ1` is a **grading-path criterion registered pre-compute**, not a physics gate, and it constrains only how the freeze check is read.
2. **It does NOT adjudicate, change, suppress or re-judge another campaign's row.** The twelve foreign rows report exactly what they reported, at exactly the same exit code — proved byte-identically, with two plants, §24.3.
3. **It touches exactly ONE code artifact**, the verifier, and re-pins it in the same commit (§24.7). The other nine pinned files are unmodified and were re-verified at this HEAD.
4. **It adds NO completion marker**, and does not make item 41's limb reachable by writing one. **A marker written to satisfy a checker is a fabricated completion.**
5. **It runs NO ladder compute.** No `B2` march, no `B5` solve, no queue row, **no container**. **`verification/runs/M6SR_runs` does not exist**, plant-verified at the exact searched path before this work and after it.
6. **It does NOT freeze and it does NOT launch.** Rule 2's freeze and the launch decision are the supervisor's; a lane may not take either.
7. **It does not re-open** items 25 and 27 (carried forward unrepaired on the supervisor's express instruction, §18.7), items 35–37 (measured CLOSED at `87504e79`), or item 5's `X1` DATA limb, which stands untouched.

### 24.11 THE STRIKE AUDIT — RUN ON THIS SECTION'S OWN DIFF

The subjects are the values this amendment declares **FALSE IN FORCE**: §23.6's blob sha and file
sha256 for the verifier, quoted inside §24.7's single strike span, and §23.8's superseded reading,
quoted inside §24.1's. **Every occurrence of each in the text this amendment adds was located and
classified, and each sits inside a `~~…~~` span.**

⚠ **RULE 3 ON THE AUDITOR ITSELF.** A false sha was planted on a plain, unstruck prose line and the
auditor **must** report it `UNCLASSIFIED`; the audit **refuses** rather than passing if the plant
is not seen. **The plant was SEEN.** The result is printed in the commit that carries this section.

### 24.12 COST — RULE 12

| item | predicted | **actual** | ratio | attribution |
|---|---|---|---|---|
| repo-wide verifier runs ×4 (2 baseline, 2 after) | 4 × 71 s at 1 rank = **4.73 core-min** (charged at §23.11's measured rate) | **4.73 core-min** | **1.00** | §23.11's re-based estimate held. The correction it made — that the walk runs a `git log`/`git grep` **per row** over 216 rows — is the reason this prediction was right |
| **restricted** verifier runs ×4 | none predicted; a new shape | **~4 s wall total at 1 rank ≈ 0.07 core-min** | — | the restricted walk visits **2 directories and 10 files** instead of 216 rows. **This is the mode's incidental second benefit and is reported, not claimed as a design goal** |
| selftest runs ×4 (incl. `-O`) and document work | — | **host arithmetic, ~1.5 core-min** | — | 30 new arms, each spawning subprocesses in throwaway repositories |

⚠ **`cost_basis` HONESTY, rule 12.** The repo-wide figure is a **charge at §23.11's measured rate,
not four fresh measurements**, and is labelled so rather than presented as four. The restricted and
selftest figures are **wall-clock observations on this box, not billing**; the box cannot read its
own billing, so **any dollar figure derived from these is reported-by-owner, not measured**.

**Container-seconds, reported as WASTE and SEPARATELY, never absorbed into a step's cost: ZERO —
this pass started no container and ran no solver. Ladder core-minutes: ZERO.**

⚠ **NO ROW WAS ADDED TO `docs/COST_CALIBRATION.md`, AND THE REASON IS NAMED.** Rule 12's
calibration ledger takes a row at a **process completion** — a rung graded, a case closed, a
curriculum item finished. **Nothing completed here**: this is a pre-compute amendment with zero
ladder compute, and the estimate-versus-actual comparison above is recorded in the amendment as
§17.10 through §23.11 have all recorded theirs. **If the supervisor reads a pre-compute pass as a
completion, that row is one line and is theirs to direct.**

⚠ **The box was NOT idle.** Heat-transfer's `T3e` held **8 ranks of 16**. This pass took **1 rank**
and did not saturate.

### 24.13 RULE 6's AMENDMENT ASSERTIONS

**Version: v1.9 → v1.10 (amendment 18, pre-compute). The frozen file was NOT edited; this section
is APPENDED AT THE FOOT.**

⚠ **The header line 3 still reads `v1.0` and is DELIBERATELY NOT EDITED**, for the reason §15.10
through §23.12 give: editing it would change a line above §15 and falsify those sections' own
assertions, on which other records depend — **and at least one such citation sits inside an
executable check.** **The bump is recorded HERE. The supervisor may restate the version in the
header at the re-freeze, which is a status flip they own; a lane may not.**

> **`lines whose number changed above this section: 0`**

**Verified, not asserted:** lines **1–5249** of this file — the whole of it up to and including
§23.13's closing line, and therefore **every** guaranteed range §15.10 through §23.12 asserts — are
**byte-identical** before and after this append, both rendering to sha256
**`d74ee5689e96a4fb47faa5f46a798214d34b33e7a908a7f1c187d1d6f152f66d`** *(asserted here and
re-derived inside the commit invocation that carries this section; the commit ABORTS if it moves)*.

### 24.14 THE STANDING QUESTION — **ANYTHING ELSE BETWEEN THIS DOCUMENT AND A LAWFUL LAUNCH?**

**NO. This lane finds nothing further, and states what it checked in order to be able to say so.**

1. **Every item this campaign has raised is closed or is explicitly parked by the supervisor.** Items 41 and 42 are ruled and implemented here. Items 35–37 were measured closed. Items 38, 39 and 40 were repaired in the instruments. Items 25, 27 and item 5's `X1` DATA limb are **carried forward unrepaired on express instruction**, which is a decision on the record and not an open finding.
2. **The registered grading criterion is now an EXIT CODE the campaign can earn** (§24.4), it is registered **verbatim as a command line** rather than as remembered prose, and it **refuses** rather than passing when it cannot reach its subject.
3. **All ten pinned executables are covered, identity-checked and currency-checked** — measured `10 of 10`, and the one drift in flight was the verifier's own edit, resolved by the re-pin in this commit.
4. **The freeze is provable without the unreachable limb**, and the caveat saying so is registered **on the criterion** and **printed by the tool**, so a future grader meets it rather than having to remember it.
5. **No compute has occurred**: the run root is plant-verified absent at the exact searched path.

⚠ **WHAT THIS LANE CANNOT SAY, AND DOES NOT.** It has **not** re-derived the physics, the gates in
§5/§5.1, the mesh standard compliance or the solver pin from first principles this pass; those were
settled in earlier amendments and are **relied on, not re-verified here**. **Check 1 on this diff,
check 4, the freeze and the launch are the supervisor's**, and this lane takes none of them.
**Subject to those four, this lane knows of nothing between this document and a lawful launch.**

---

## 25. AMENDMENT 19 — 2026-09-04, **PRE-COMPUTE**. **§7 DECLARED ITSELF THE SOLE BLOCKING AUTHORITY FOR ELEVEN ADVERSARIAL PASSES WHILE FOUR OF ITS FIVE CONDITIONS WERE WIRED TO NOTHING.** ITEMS **43–46** WIRE ALL FOUR AT §7's OWN STATED THRESHOLDS, EACH UNDER A PLANTED CONTROL THAT FIRES — AND ITEM **47** IS RAISED: **NOTHING ON THE LAUNCH PATH CONSULTS GATE A AT ALL**

**Version 1.19. Lines whose number changed above this section: 0.** This amendment is **appended
at the foot** and edits nothing above it. **Verified, not asserted:** lines **1–5561** of this
file — the whole of it up to and including §24.14's closing line, and therefore **every**
guaranteed range §15.10 through §24.13 asserts — are **byte-identical** before and after this
append, rendering to sha256
**`5a166ce54f562e934b79c445aa106ef60e569004a710d00500f281e95276b6d6`** *(asserted here and
**re-derived inside the commit invocation that carries this section**, with the commit
**ABORTING** if it moved)*.

### 25.1 🔴 THE FINDING, STATED WITHOUT SOFTENING

**§5 line 796 reads *"Only §7 blocks a launch."* §7 line 1058 reads *"Checked per level BEFORE
launch. A failure here `BLOCKED`s the level. Nothing else blocks."* It lists FIVE conditions.
FOUR OF THE FIVE WERE WIRED TO NOTHING.**

| §7 condition | its stated threshold | wiring **before** this amendment |
|---|---|---|
| **1** ≥ 3 patches; `wing` wall; symmetry typed `symmetry`; farfield `patch` | — | ✅ **WIRED TWICE** — `build_m6sr_l1.sh:763-767` aborts at exit 8, `analyse_m6sr.py` A9 labels `BLOCKED`, and `write_m6sr_case.py`'s CH1 refuses. **Nothing to do.** |
| **2** `Boundary openness` ≤ 1e-12 | 1e-12 | 🔴 **NOT GATED.** Extracted at `analyse_m6sr.py:232` into `out["boundary_openness_max_abs"]`. That key occurred **exactly twice in the file — both of them the assignment** (`:230`, `:232`). **ZERO readers.** The threshold `1e-12` appeared **nowhere** against it. |
| **3** `Number of regions: 1` | 1 | 🔴 **NOT GATED.** Parsed at `:209`, int-coerced at `:227`, **never compared to 1.** |
| **4** Min cell volume > 0 | > 0 | 🔴 **NOT GATED.** Parsed at `:207`, used **only as the denominator** of `cell_volume_ratio` at `:238-239`. **A NEGATIVE minimum — an inverted cell, the exact hazard — yielded a negative ratio and failed nothing.** |
| **5** patch **NAMES** matched against the level's own expected set, refusing on mismatch | — | 🔴 **NOT IMPLEMENTED AT ALL.** A9 tests **TYPES** and a count ≥ 3. **No expected-NAME set existed anywhere in `cases/M6SR/`.** |

**AND THE SCOPE IS WIDER THAN THE COMPARATOR.** A grep for `openness`, `number of regions`,
`min volume` and `1e-12` across **every** `.sh` and the case writer in `cases/M6SR/` returns
**ZERO hits**. Conditions 2, 3 and 4 were unwired **in every artifact of this campaign**, not
merely in the grading path.

🔴 **AND THE CONTROLS COULD NOT HAVE CAUGHT IT — THE F5b PATTERN OVER AN UNGATED FIELD.** Both
checkMesh fixtures in `analyse_m6sr.py` (`_CM_EQ_FORM`, `_CM_COLON_FORM`) carried **CLEAN VALUES
ONLY**: openness ~1e-17 and ~1e-18, `Number of regions: 1`, a **positive** `Min volume`. There was
**no fixture anywhere in the file** with a failing openness, with regions ≠ 1, or with a negative
minimum volume. **The reader was never shown able to see the failure it exists to catch**, so a
green from it would not have been evidence even after the gate was wired (rule 3).

🔴 **HOW IT WAS FOUND, AND HOW IT WAS NOT.** **This was found by a supervisor's personal check-4
read of the document's OWN STATED PRECONDITIONS — and by none of the eleven adversarial passes
that preceded it.** Each of those eleven closed on the sentence *"nothing else between this
document and a lawful launch."* **The document had been asserting for eleven passes that §7 was
the one thing that blocks, while four fifths of §7 blocked nothing.** That is recorded here in
those terms and is not softened: **a screen that is declared and not wired is worse than one never
declared**, because every later pass reads the declaration and moves on. The supervisor's own note
that the premature freeze at `40f2d9b9` skipped exactly this check is what put the check back.

### 25.2 THE CONDITION UNDER RULE 2, AND HOW IT WAS CHECKED

**These are PRE-COMPUTE REPAIRS.** Standing rule 2 permits amendment before first compute **and
requires the condition to be stated with how it was checked, naming the run directory that does not
exist.** The run directory is **`verification/runs/M6SR_runs`**.

**IT IS PLANT-VERIFIED ABSENT, NOT MERELY REPORTED ABSENT** — a zero from a searcher not shown able
to see a non-zero is not evidence (rule 3):

| step | searcher `find verification/runs -maxdepth 1 -name M6SR_runs -print \| wc -l` |
|---|---|
| **before** | **0** |
| **with a probe created at that exact path** | **1** — the searcher is SHOWN able to see it |
| **after `rmdir`** | **0** |

The probe was removed with **`rmdir`**, which **refuses a non-empty directory**, so the removal
cannot have deleted a run. Corroborated independently: `test -e` reads ABSENT and `git ls-files`
returns **0 rows**. **NO COMPUTE HAS OCCURRED UNDER THIS REGISTRATION.**

### 25.3 ITEM 43 — CONDITION 2 IS GATED AT **1e-12**

`A10_S7_C2_boundary_openness_le_1e-12`, per level, label **`BLOCKED`** on failure — §7's own label.
The reading is the **maximum of the absolute values of the three printed components**, which is
what `read_checkmesh` already extracted and nothing read. **The threshold is §7's, verbatim, and is
not widened, softened or reinterpreted.**

### 25.4 ITEM 44 — CONDITION 3 IS GATED AT **EXACTLY 1**, AND IT IS A **REGRESSION**, NOT A FIRST-TIME OMISSION

`A11_S7_C3_number_of_regions_equals_1`, per level, label **`BLOCKED`** on failure.

🔴 **THE LAB ALREADY HAD THIS GATE AND M6SR LOST IT.** `cases/RUNG1_M6/run_r1m0.sh:360` — the
predecessor campaign M6SR supersedes — reads `"single_connected_region": cm.get("n_regions") == 1`.
**A capability the lab built, and then lost, is a worse finding than one it never built**, and it is
recorded here as the worse thing rather than the milder one.

🔴 **AND CONDITION 3 IS A PRECONDITION FOR BELIEVING GATE A1, NOT ONLY A BLOCKING SCREEN.**
`cases/RUNG1_M6/read_checkmesh.py:56` and `run_r1m0.sh:358-359` record the mechanism, measured on
this box: if a multi-block conversion fails to merge coincident block-interface points, **those
interfaces become BOUNDARY faces**, and checkMesh computes non-orthogonality **over internal faces
only** — so every block interface **drops out of the statistic entirely and the reported maximum is
FALSELY OPTIMISTIC**. Gate **A1** reads exactly that maximum off exactly that file. **An unmerged
multi-region mesh therefore does not merely slip past §7; it makes Gate A's own number
unfalsifiable.** That consequence is stated here so a future reader does not treat condition 3 as
a formality.

### 25.5 ITEM 45 — CONDITION 4 IS GATED **STRICTLY ABOVE ZERO, SIGNED** — AND A LATENT CRASH THAT PRE-EMPTED IT IS REPAIRED

`A12_S7_C4_min_cell_volume_strictly_positive`, per level, label **`BLOCKED`** on failure.

**THE TEST IS `value > 0.0`. IT IS NOT `!= 0` AND IT IS NOT `abs(value) > 0`** — both of those admit
a **negative** minimum volume, which **is** an inverted cell and **is** the hazard §7 condition 4
names. The sign is the whole content of the condition, and the pre-amendment code's only use of the
reading was as a **denominator**, where a negative value merely produced a negative ratio.

🔴 **45b — A LATENT UNCAUGHT CRASH ON THE SAME READING, DISCLOSED RATHER THAN SMUGGLED IN.** The
ratio guard at `:238` tested `max_volume not in (None, 0.0)` **while dividing by `min_volume`**.
**Measured:** a log reading `Min volume = 0` — a fully degenerate cell, condition 4's hazard **at its
boundary** — raised an **uncaught `ZeroDivisionError`**. The module docstring already rules that **a
crash is NOT a refusal**, and that crash **pre-empted condition 4**: the screen could never have
reported on the very reading that killed the reader. The guard now tests the **denominator**, which
is what it was always for. **`max_volume` keeps its exact previous condition, so the ONLY behaviour
that changes is `min_volume == 0`, which goes from a crash to `None`. No clean reading moves** —
measured in §25.9.

### 25.6 ITEM 46 — CONDITION 5, THE PATCH-**NAME** SCREEN, AND THE REFUSAL THAT IS THE FEATURE

`A13_patch_names_match_the_registered_per_level_set`, per level.

**THE EXPECTED SET IS READ FROM THIS REGISTRATION, PER LEVEL, AND IS NEVER DERIVED FROM THE MESH
BEING SCREENED.** The supervisor's ruling, applied literally: *"A screen that reads its expectation
off the thing it is screening is not a screen."*

| level | expected patch names | basis | behaviour |
|---|---|---|---|
| **L2** (399,360) | **`wing` / `inout` / `sym`** | **§2.2 line 363**, recorded pre-compute, read from that level's **own** `constant/polyMesh/boundary` | graded; **`BLOCKED`** on mismatch |
| **L3** (99,840) | 🔴 **NOT REGISTERED** | §2.2's table carries L3's numerics but states patch identity **for the 399,360 level only**. No line of this document records L3's names. | **REFUSAL (exit 2)** |
| **L1** (1,597,440) | 🔴 **NOT REGISTERED** | **§7 says so in terms**: the new L1's names *"are produced by `autoPatch 60` + `createPatch` and are NOT predicted here."* | **REFUSAL (exit 2)** |

⚠ **AND §20.2.3's MEASUREMENT IS DELIBERATELY NOT USED AS L1's SET, WITH THE REASON GIVEN.**
§20.2.3 measured a `createPatch` probe reading *"`wing` (wall) / `inout` (patch) / `sym`
(symmetry) — **wall 1, symmetry 1, patch 3, empty 0**"*. **THAT IS NOT A COMPLETE NAME SET AND IS
NOT TREATED AS ONE: three names are given while the counts total FIVE patches, so two patch-typed
names are unaccounted for.** Registering the three would be **inventing the missing two**. **This
lane does not do that, and flags the discrepancy to the supervisor rather than resolving it** — it
is precisely the case where §7's wording and checkMesh's output shape disagree.

🔴 **THE REFUSAL IS THE FEATURE, AND IT IS THE LAWFUL DIRECTION.** An unregistered level raises
`Unregistered` — the comparator's existing rc-2 class, whose docstring already reads *"A parameter
the frozen registration does not register. Picking one here would be choosing a gate parameter
AFTER the freeze, which is exactly what standing rule 2 forbids."* **The comparator names the gap
and refuses. The fix is an AMENDMENT recording the set, which is pre-compute and lawful.**

⚠ **A CONSEQUENCE STATED PLAINLY: GATE A CANNOT BE GRADED TODAY** on the real ids, because two of
three levels have no registered name set. **That is the honest state of the campaign and it is not
a reason to weaken the screen.**

⚠ **AND THE CASE WRITER MAKES CONDITION 5 MORE NECESSARY, NOT LESS.** `write_m6sr_case.py`'s CH1
attaches boundary conditions **by TYPE**, and its own control at `:913` states that *"if the writer
attached by NAME rather than by TYPE (CH1) this control could not pass."* **A name-agnostic writer
will attach freestream conditions to ANY patch typed `patch`, whatever it is called** — which is
exactly the silent mis-application §7 and prediction P7 warn of.

⚠ **A SECOND FALSE ATTRIBUTION IN THIS DOCUMENT, NAMED.** **Prediction `P7` at line 1371** ends
*"The launcher **refuses** a level whose patch names it did not expect **(A9)**."* **A9 does not and
never did check names.** §7's closing sentence makes the same claim without the cross-reference.
**Both were false when written**; A13 is what makes them true.

### 25.7 THE ABSENT-AND-UNPARSEABLE RULING, AND WHICH LABEL WAS CHOSEN

**AN ABSENT OR UNPARSEABLE READING NEVER READS CLEAN.** §5's Gate A already fixes the principle in
terms — *"An absent checkMesh log reads ABSENT. It never reads clean."* — and it is applied to all
three of conditions 2/3/4 without softening: an ABSENT log, and a log that was READ but out of
which the named value did not parse, both fail the clause.

**THE LABEL CHOSEN IS `BLOCKED`, NOT A REFUSAL, AND THE REASONING IS GIVEN SO IT CAN BE OVERRULED.**
The finding is about **the LEVEL, not the instrument**: the instrument ran correctly, and what it
found is that the level **cannot be shown well-posed**. `BLOCKED` is §7's own word for exactly that,
it is the strictly conservative direction, and it keeps the per-level record readable instead of
aborting a whole grade on one missing file. **A REFUSAL is reserved for condition 5's unregistered
case**, which is a statement about **this document** and not about any mesh. ⚠ **If the supervisor
reads §5's ABSENT rule as requiring exit 2 for conditions 2/3/4 as well, that is one label to
change and it is the supervisor's to say.**

### 25.8 THE FOUR PLANTED CONTROLS — **`C25`–`C28`**, AND EACH IS A **DELTA**, NOT A COLOUR

**Each control drives the REAL `gate_a()` TWICE on a synthetic three-level tree written to disk and
read back through the REAL readers: once CLEAN, once with ONE value planted.** It requires **(a)**
the clean twin to grade `PASS`, **(b)** the mutant to grade `BLOCKED`, and **(c)** **EXACTLY the
clause under test to flip.** **The negative twin is what makes the positive one mean anything**, and
the confinement requirement is what stops these four gates from being indistinguishable from each
other.

| control | the plant | **how the mutant died** |
|---|---|---|
| **`C25`** | boundary openness **1e-09** on the middle level — **three orders ABOVE §7's 1e-12** | clean twin `A10 = PASS`, Gate A `PASS`; planted `A10 = BLOCKED`, **Gate A `BLOCKED`**; **clauses that MOVED = `['A10_…']` — exactly one.** Before this amendment the key had **zero readers**, so this exact plant would have changed **nothing**. |
| **`C26`** | **`Number of regions: 9`** on the finest level | clean twin `A11 = PASS`, Gate A `PASS`; planted `A11 = BLOCKED`, **Gate A `BLOCKED`**; **MOVED = `['A11_…']`.** **`9` is not an invented number**: it is the value **this box has observed** from the exact defect (`cases/RUNG1_M6/read_checkmesh.py:56`, an unmerged nine-block PLOT3D conversion). **A representative fixture is the entire point — an unrepresentative one is the defect this amendment repairs.** |
| **`C27`** | **`Min volume = -4.2e-11`** — a **NEGATIVE** minimum, an inverted cell — on the coarsest level | clean twin `A12 = PASS`, Gate A `PASS`; planted `A12 = BLOCKED`, **Gate A `BLOCKED`**; **MOVED = `['A12_…']`.** **AND THE CONTROL SHOWS THE OLD BLINDNESS DIRECTLY:** read back from disk the value is `-4.2e-11` and the old path's only use of it, `cell_volume_ratio`, is **`-22480595238.09524`** — **a negative ratio, which failed no check whatsoever.** |
| **`C28`** | **`('WING3D', 'FARFIELD', 'SYMMETRY')`** on the middle level — **CORRECT TYPES, WRONG NAMES** | clean twin `A13 = PASS`, Gate A `PASS`; planted `A13 = BLOCKED`, **Gate A `BLOCKED`**; **MOVED = `['A13_…']`.** **THE INDEPENDENCE PROOF THE SUPERVISOR REQUIRED: `A9` reads `PASS` on the clean twin and STILL reads `PASS` on the mutant** — the mutant is **invisible to the type screen** and dies **only** at the name screen. **PLUS THE REFUSAL LIMB:** the real ids `('L3','L2','L1')` **REFUSE**, naming `['L3','L1']`. |

**THE `C28` PLANT IS NOT INVENTED EITHER.** It is prediction **`P7`'s MEASURED PRECEDENT** on this
box: an hcf-generated family produced `wing/symmetry/farfield` on the generator level and
**`WING3D/SYMMETRY/FARFIELD`** on the coarsened levels.

**EACH OF THE FOUR IS ALSO PROVED BREAKABLE.** `C25`–`C28` are added to `--selftest`'s **mutation
control**, which corrupts each shipped statistic in turn and requires **exactly that control** to
flip from FIRED to red. **A control that cannot be broken is not a control.**

**AND THEY ARE PROTECTED FROM SILENT ORPHANING.** `section7_conditions_2_3_4` and
`section7_condition_5` are added to control **`C23`'s** `must_reach` set, so an AST call-graph walk
over this file **goes RED** if a future edit orphans them the way item 5's finding recorded
`gate_p()` being orphaned. **The defect this amendment repairs is exactly "declared but not
reached", and the repair is defended by the instrument that detects that.**

### 25.9 🔴 **NO EXISTING READING MOVED — MEASURED, NOT ASSERTED**

The supervisor required immediately that **no repair of a blocking screen may move a graded value.**
It moved none, and that is measured three ways against the **committed `HEAD` blob** of the
comparator run side by side with the edited file:

1. **`read_checkmesh()` output on BOTH clean fixtures is IDENTICAL** — full-dict equality, old
   versus new, on `_CM_EQ_FORM` and `_CM_COLON_FORM`. **Both fixture texts are byte-unchanged.**
2. **NO pre-existing control changed status.** The FIRED / DID-NOT-FIRE status of every control
   `C1`–`C24` is identical before and after; the only rows that differ are the four new ones.
3. **`--gate-a` on the REAL levels produces the IDENTICAL refusal** before and after — it refuses
   on L1's missing points file, which precedes `A13`. **The real grading path's observable output
   is unchanged.**

⚠ **ONE PRE-EXISTING RED, NAMED SO IT IS NOT MISREAD AS MINE.** `--controls` exits **2** both before
and after, on **`C12`**, whose own message records that it *"CANNOT fire as written"* against
non-monotone as-read data and was **"Reported, NOT loosened."** **It is red at `HEAD` too, verbatim.
This amendment neither caused it nor touched it.** It is already on the record as **`X7`**, and
§18.5's pre-launch grading gate (`run_m6sr_b5.sh:436`, `[ "$CRC" -eq 0 ]`) **already refuses the
launch at exit 8 because of it.**

### 25.10 `rc` PARITY, BYTE-IDENTICAL STDOUT, AND **ZERO** `ast.Assert`

⚠ **`rc` PARITY.** `--controls` returns **`2` under `python3` and `2` under `python3 -O`** — the
same pair as at `HEAD` — and the two runs' stdout is **byte-identical** once the scratch path is
normalised. **No arm rests on an assertion the optimiser removes.**

⚠ **NO BARE `assert` ANYWHERE IN THE FILE. Verified by AST parse, not by grep, WITH THE DETECTOR
PLANTED AND SEEN**: the shipped file contains **0** `ast.Assert` nodes, and a copy with **one**
`assert` appended reads **1**. **The detector was proved able to see one before its zero was
believed** (rule 3). Every new guard added here is an explicit `raise` or a recorded boolean.

### 25.11 ⚠ **A GREP TRAP, RECORDED SO THE NEXT AUDIT DOES NOT CLEAR THIS ON A FALSE HIT**

A **tree-wide** grep for `Number of regions` returns hits in
`cases/RUNG1_M6/{run_r1m0.sh,read_checkmesh.py,build_r2_triple.py}` and
`cases/committee-grids/read_ugrid_identity.py`. **An auditor who greps the TREE rather than THE
CAMPAIGN will find a gate and conclude condition 3 was enforced for M6SR. IT WAS NOT.** M6SR's
chain **invokes none of them**; the only `RUNG1_M6` references inside `cases/M6SR/` are **prose in
comments and abort strings** citing the M0 all-wall-box lesson. **The scoped sweep that found this
defect was correct for the claim it made, and would have been wrong for a claim about the tree.**

### 25.12 THE COMPARATOR IS A REFERENCE, NOT AN IMPORT — DIVERGENCES DECLARED

`cases/RUNG1_M6/read_checkmesh.py` was read as a reference implementation. **Nothing is imported
from it** — that would be a cross-campaign dependency and this comparator takes none. Where the two
differ, and why:

- its `RE_REGIONS` matches the **`:` form only**; this file's `n_regions` pattern matches **`[=:]`**
  and so also sees the `=` form. **Broader, in the safe direction.**
- its `NUM` has no `[Dd]` exponent; this file's does. **Broader, same direction.**
- it gates regions as a **driver completion clause**; this file gates it inside **Gate A**. **That
  placement difference is a real residual and it is item 47 below, not a detail.**

### 25.13 🔴 **THE INSTRUMENT'S OWN PIN MOVED, AND IS RE-TAKEN IN THE SAME COMMIT**

**This amendment edits one of the ten pinned executables** — the comparator, §23.5 row 1. §22.2's
pin for it is **FALSE IN FORCE** at this commit and is struck, rule 6, **by quote**:

🔴 **TWO LIVE TABLE ROWS RECORD THE SUPERSEDED BLOB, NOT ONE — AND BOTH ARE STRUCK.** A search of
this file for `9b963ad4` returns **two table rows** (§18.3.1's and §22.2's) and **three prose
mentions**. Striking only the most recent would leave a reader who finds the earlier row with an
unstruck, false pin. **Both rows are struck, rule 6, by VERBATIM quote — each checked character
for character against the line it strikes, not retyped from memory:**

> 🔴 **STRUCK BY QUOTE** *(§22.2's row — the pin that was IN FORCE)*: ~~*"| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`9b963ad48e016fe2177553507006915e52b4ef98`** | `9042cdf22ff948f8df48d846495ccb0d05e5130d19a0572b6020b728507d9394` | 2,742 | **`8c0ab7a8`** (Amendment 11) | **§9 registered** — pin UNMOVED since §18.3.1 |"*~~

> 🔴 **STRUCK BY QUOTE** *(§18.3.1's earlier row, carrying the SAME now-superseded blob)*: ~~*"| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`9b963ad48e016fe2177553507006915e52b4ef98`** | `9042cdf22ff948f8df48d846495ccb0d05e5130d19a0572b6020b728507d9394` | 2,742 | **`8c0ab7a8`** (Amendment 11) |"*~~

⚠ **THE THREE PROSE MENTIONS ARE NAMED, NOT STRUCK** — striking narrative sentences is not this
convention's purpose and a lane does not rewrite them: **line 3410** (*"The comparator now hashes
to `9b963ad4…` at 2,742 lines"*), **line 4681** (§22's supersession chain) and **line 4938**
(*"the blob pinned by §22.2, the one that will run"*) all describe the superseded blob. **Each is
true of the moment it was written and false in force now**, and this sentence is the notice.

**THE NEW STANDING PIN**, derived with `git hash-object` on the working tree and **RE-DERIVED
INSIDE THE SAME SHELL INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT ABORTING
IF IT HAD MOVED** — §22.2's guard, kept:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator, §9 and §23.5 row 1) | **`1ed1cee48bb945926cb23832eb3bed6669d53add`** | `efe6aa53bdd7d1b1bf3a365b99a4a0fa166dfdbf58d075d2ad6c557d032b0ec4` | **3,200** | **§9 registered** — **RE-PINNED HERE** |

⚠ **THE OTHER NINE PINS ARE UNMOVED AND WERE RE-VERIFIED, NOT ASSUMED** — every one read **`PIN-OK`**
at this HEAD in the verifier's own run, while the **comparator alone** read `PIN-DRIFT`: measured
**`10 of 10` covered, `9 PIN-OK`, `1 violating`**, the instrument convicting this amendment's own
stale pin on a plant nobody had to fabricate. **This amendment touches no code but the comparator.**

⚠ **THE STRIKE-BY-QUOTE LIMITATION, RESTATED RATHER THAN GLOSSED.** Striking a row by quote in a
later section **does not remove the original row from the file**, so the parser still reads §22.2's
superseded row as live and may report more than one recorded sha for this path. **CURRENCY is
satisfied by the new sha above**, and **the registration is the authority on which pin is in force:
it is the one in the table immediately above.**

### 25.14 🔴 **ITEM 47 — NEW, AND IT OUTRANKS THESE FOUR REPAIRS: NOTHING ON M6SR's LAUNCH PATH CONSULTS GATE A AT ALL**

| # | the finding | how it was measured | consequence |
|---|---|---|---|
| **47** 🔴 | **§7 says its conditions are *"Checked per level BEFORE launch"* and that a failure *"`BLOCKED`s the level"* — but the solve driver never asks Gate A anything.** `run_m6sr_b5.sh` invokes the comparator **exactly twice**, at `:429` and `:430`, **both times as `--controls`**. **It never invokes `--gate-a`.** Its own closing line (`:848`) says *"B4 is Gate A … in `cases/M6SR/analyse_m6sr.py`"* — i.e. Gate A is a **separate, manually-invoked grading step**, and **no refusal anywhere in the driver reads a `BLOCKED` Gate A.** | Measured by enumerating every `analyse_m6sr` reference in `run_m6sr_b5.sh` (7 in comments, 2 executions, 2 `import`s for `points_stream_sha` and a reporting helper) — **none is `--gate-a`.** | ⚠ **WIRING CONDITIONS 2–5 INTO `gate_a()` MAKES THEM GRADEABLE. IT DOES NOT YET MAKE THEM BLOCK A LAUNCH.** Condition 1 is the only §7 condition enforced **on the launch path**, and it is enforced by the **builder** (`build_m6sr_l1.sh` exit 8) and the **case writer** (CH1), **not by Gate A**. **A supervisor ordering a launch on the strength of §7 would be relying on a screen the launcher does not run.** **NOT REPAIRED HERE:** making the driver refuse on a `BLOCKED` Gate A changes **when a launch is permitted** and is a §9/§2.4 step-order question. **Per §22.6 item 32 that is the supervisor's and not a lane's.** |

### 25.15 COST — RULE 12

**No ladder compute was authorised or spent. `B0`–`B6` are untouched and the run root remains
plant-verified absent.** The only compute is the comparator's own control suite and this document
work, at **1 rank**:

| activity | wall s | ranks | **core-min (MEASURED from the clock)** |
|---|---|---|---|
| `--controls`, `python3` and `python3 -O`, plus the `HEAD` baselines and fixture diffs | 49 | 1 | **0.8167** |
| `--selftest` (controls ×1 + `C16` + **26** mutation re-runs) | 229 | 1 | **3.8167** |
| **TOTAL** | | | **4.6334** |

**CHARGED VERSUS MEASURED:** the core-minutes above are **MEASURED** — wall seconds × ranks ÷ 60,
read off the clock. Any dollar figure is **derived at the recorded $0.0513/core-h and is
reported-by-owner, never measured**: this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

⚠ **NO `docs/COST_CALIBRATION.md` ROW IS FILED, AND THAT IS DELIBERATE.** Rule 12's
estimate-versus-actual is owed **at a PROCESS COMPLETION** — a rung graded, a case closed, a
curriculum item finished. **Nothing completed here**: no gate was graded, no rung ran, and §2.4's
`B0`–`B6` estimates have no actuals to compare against. **Inventing a calibration row for a
document edit would put a fabricated actual beside a real estimate**, which is worse than the
absent row. **The row is owed at `B4`, and `B4` has not run.**

### 25.16 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** Every threshold wired here — `1e-12`,
   `1`, `> 0`, and the per-level name set — **is quoted from §7 and §2.2 and not one of them is
   chosen, widened, softened or reinterpreted here.** §5, §5.1, §2.4 and §10's registered numbers
   are untouched.
2. **It does not freeze and it does not launch.** Both are the supervisor's.
3. **It does not register L1's or L3's patch names.** It **refuses** for want of them, and says so.
4. **It does not touch `run_m6sr_b5.sh`, `build_m6sr_l1.sh` or `write_m6sr_case.py`** — item 47 is
   raised, not repaired.
5. **It does not re-derive** the physics, §5/§5.1's gates, mesh-standard compliance or the solver
   pin. Those were settled in earlier amendments and are **relied on, not re-verified here.**

### 25.17 THE STANDING QUESTION — **ANYTHING ELSE BETWEEN THIS DOCUMENT AND A LAWFUL LAUNCH?**

🔴 **YES. TWO THINGS, AND THIS LANE WILL NOT REPEAT THE ELEVENTH PASS'S "NO."**

1. **ITEM 47 (§25.14): nothing on the launch path consults Gate A**, so §7's *"checked per level
   before launch"* is still not true of conditions 2–5 even after this amendment wires them.
2. **ITEM 46's REFUSAL (§25.6): Gate A cannot be graded at all on the real level ids** until this
   registration records L3's and L1's expected patch-name sets. **That is by design and it is the
   lawful direction**, but it is squarely between this document and a launch.

⚠ **AND ONE PRE-EXISTING BLOCKER, RESTATED:** `X7` / **`C12`** holds `--controls` at rc 2, and
§18.5's pre-launch grading gate refuses at exit 8 on exactly that. **The launch was already blocked
before this amendment; it is blocked for three reasons now, and all three are on the record.**

⚠ **WHAT THIS LANE CANNOT SAY, AND DOES NOT.** It checked the document's stated preconditions and
their wiring; it did **not** re-derive the physics or the gates. **Check 1 on this diff, check 4,
the freeze and the launch are the supervisor's, and this lane takes none of them.**

---

## 26. AMENDMENT 20 — 2026-09-04, **PRE-COMPUTE**. **ITEM 47 IS REPAIRED: THE LAUNCH PATH NOW RUNS §7's SCREEN ITSELF AND A BLOCKED LEVEL REFUSES THE SOLVE AT A DISTINCT EXIT CODE.** ITEM 46's CIRCULARITY IS BROKEN AT ITS NON-CIRCULAR SOURCE — **`createPatchDict`** — AND ALL THREE LEVELS' NAME SETS ARE REGISTERED WITH THAT DICT'S PATH AND SHA. §20.2.3's **3-vs-5** DISCREPANCY IS RESOLVED. **AND THE NINETEENTH PASS FINDS ITEM 48: AMENDMENT 13's OWN RULED STEP `B3c` HAS NO IMPLEMENTATION IN ANY EXECUTABLE.**

**This amendment is written by a lane under the cfd supervisor's two express rulings on items 47
and 46, quoted where each is applied. It moves NO gate, NO threshold, NO cap and NO label. It does
not freeze and it does not launch; both are the supervisor's.**

### 26.0 THE LAWFULNESS CONDITION, AND HOW IT WAS CHECKED — **NOT ASSERTED, PLANTED**

**These are PRE-COMPUTE repairs.** Standing rule 2 permits amendment before first compute **and
requires the condition to be stated with how it was checked, naming the run directory that does not
exist.** The run directory is **`verification/runs/M6SR_runs`**, and it is **plant-verified absent**
— a zero from a searcher not shown able to see a non-zero is not evidence (rule 3):

| step | `find verification/runs -maxdepth 1 -name M6SR_runs -print \| wc -l` |
|---|---|
| **before** | **0** |
| **with a probe created at that exact path** | **1** — the searcher is SHOWN able to see it |
| **after `rmdir`** | **0** |

The probe was removed with **`rmdir`**, which **refuses a non-empty directory**, so the removal
cannot have deleted a run. Corroborated independently: `test -e` reads **ABSENT** and
`git ls-files verification/runs/M6SR_runs` returns **0 rows**. **NO COMPUTE HAS OCCURRED UNDER THIS
REGISTRATION**, and none was authorised or spent by this amendment.

---

### 26.1 ITEM 47 — **THE SUPERVISOR'S RULING, AND THE REPAIR**

> **RULED (supervisor, verbatim):** *"§7's screen must be consulted BY THE LAUNCH PATH, and a
> BLOCKED Gate A must REFUSE the solve. §7's own words are 'Checked per level BEFORE launch' and
> 'A failure here BLOCKEDs the level' — a screen the launcher never runs does not satisfy its own
> text, and I will not order a launch on a screen that does not run."*

**THE DEFECT, RESTATED WITHOUT SOFTENING.** §7 calls itself *"THE ONE THING THAT BLOCKS"* and §5
says *"Only Section 7 blocks a launch."* For **eleven adversarial passes** the solve driver
`cases/M6SR/run_m6sr_b5.sh` invoked the comparator **exactly twice**, both times as `--controls`,
and **never once as `--gate-a`**. Amendment 19 wired conditions 2–5 into `gate_a()` and made them
**gradeable**. **It did not make them block a launch.**

#### 26.1.1 THE NEW STEP `B4s`, AND WHY IT SITS EXACTLY WHERE IT SITS

> **REGISTERED (pre-compute): step `B4s` — §7's five conditions, PER LEVEL, on the launch path,
> ordered `B4` → `B4s` → `B5`.** It is `cases/M6SR/analyse_m6sr.py --section7-screen --level <id>
> --case <dir>`, invoked by `run_m6sr_b5.sh` once at top level. **`B4s` is UNBUDGETED and named on
> its own line, exactly as §18.9 treats `B3s`/`B5p`/`B5g` and §19.8 treats `B3c`.**

- **It cannot run earlier.** §7's conditions 2/3/4 are read from **checkMesh output** and condition
  5 from the **boundary file**, so the screen can only run **after `B4`** has produced
  `log.checkMesh`. Phase `stage` alone is deliberately **not** gated: gating it would leave the
  screen with no log to read — the same reasoning §18.5 already recorded for the grading rehearsal.
- **It runs before the case writer**, so a `BLOCKED` level costs not even §8's case files.
- **It is a PER-LEVEL entry point and NOT `--gate-a`, and the reason is stated so it does not read
  as an evasion.** `--gate-a` grades the **family**: `A4` requires the exact registered cell triple,
  `A5` three distinct points streams, `A6` the ratio at every level. **The driver runs ONE LEVEL AT
  A TIME**, so `--gate-a` there would fail family clauses that say nothing about well-posedness and
  would refuse a **lawful** launch. §7's own words are *"Checked **per level**"*.
- **It is NOT a second implementation.** Every clause calls the same function `gate_a()` calls —
  `section7_condition_1` / `section7_conditions_2_3_4` / `section7_condition_5`. Condition 1's
  predicate was **factored out of `A9`** in this amendment so that one body serves both callers;
  **control `C30` drives both paths on one synthetic level and requires them to agree clause for
  clause, in both directions.**

#### 26.1.2 THE EXIT CODES — **DISTINCT, AND THE TWO FINDINGS ARE NOT CONFLATED**

| rc | meaning | what it is a statement about |
|---|---|---|
| **0** | `PASS` — all five conditions hold | the mesh |
| **11** | **`BLOCKED`** — the level cannot be shown well-posed. **The message names WHICH clause blocked and its MEASURED VALUE AGAINST ITS THRESHOLD**, built from the clause details and never from the label; it is never a bare verdict string | **the mesh** |
| **12** | **REFUSAL** — the comparator returned its rc 2 (an unregistered level, a `createPatchDict` off its pin, an absent mesh), **or** was killed by its own cap (124/137), **or** returned an rc this driver does not recognise | **this document, or the instrument** |

> **A REFUSAL IS REPORTED AS A REFUSAL AND IS NEVER CONVERTED INTO `BLOCKED`.** The supervisor's
> ruling is explicit that the two are different findings. `BLOCKED` says *this mesh is not
> well-posed*; a refusal says *this document does not register what the screen needs*, or *the
> instrument cannot be trusted*. **Both stop the launch. Neither is softened into the other.**

**STANDING RULE 5's ONE-WAY DOOR.** There is **no branch** in which the screen lets the solve
proceed on anything but rc 0. An unrecognised rc, a crash and a timeout all fall to a refusal.
**This gate may only turn a launch OFF; it can never manufacture a pass.**

#### 26.1.3 🔴 **THE CONTAINER-CAP CLASS (ITEM 39) CANNOT DEFEAT THIS REFUSAL, AND THE BOUND IS MACHINE-CHECKED**

§20.3 / §21 measured that **an outer `timeout` does not bound a container**: the docker client
returns while dockerd keeps the container running outside the timeout's process group (a 3 s cap on
a 60 s container returned rc 124 after **61 wall seconds**; an unbounded payload never returned).
**That class does not reach `B4s`, and the reason is structural rather than a promise:**

1. **`B4s` starts no container.** It is a host `python3` reading two files, so it is an ordinary
   child of the driver's own process group and `timeout -k 5 120` does bind it.
2. **That is asserted on the EXTRACTED, COMMENT-STRIPPED text of the driver's own screen function**
   — `check_m6sr_launch_path.sh` limb `T6a` requires it to contain neither `docker` nor
   `run_in_container`. A comment could not satisfy it; comments are stripped for exactly that
   reason. **Mutation `MUT3`, which inserts one `run_in_container` call into the screen, drives
   `T6a` RED.**
3. **And the failure direction is closed either way.** A capped screen returns 124/137, which is an
   **explicit refusal branch** (`T6a''` asserts the branch exists), not a fall-through.

---

### 26.2 ITEM 46 — **THE EXPECTED NAME SETS, DERIVED FROM `createPatchDict`**

> **RULED (supervisor, verbatim):** *"the expected patch-name set is derived from `createPatchDict`,
> not from the mesh and not from a measurement of the mesh … The dict is authored in advance,
> committed, and causally UPSTREAM of the mesh, so reading the expectation from it is not a screen
> reading its own subject."*

`build_m6sr_l1.sh:215` already stated the principle in terms: *"A dictionary that determines the
patch names is part of the BUILD INSTRUMENT."*

#### 26.2.1 WHAT THE DICT SPECIFIES — **READ OUT OF THE FILE, NOT SUMMARISED FROM MEMORY**

The pinned `createPatchDict` declares exactly **three** `patches` entries:

| `name` | `patchInfo` type | `constructFrom` | source patches it consumes |
|---|---|---|---|
| `wing` | **`wall`** | `patches` | `"wing_.*"`, **`auto0`**, **`auto3`** |
| `inout` | **`patch`** | `patches` | `"farfield_.*"`, **`auto2`** |
| `sym` | **`symmetry`** | `patches` | **`auto1`**, `sym` |

**So the set the dict SPECIFIES is exactly `{wing, inout, sym}`, carrying the three types §7
condition 1 demands.** **ANY OTHER NAME IN THE BOUNDARY IS A SOURCE PATCH THE DICT DID NOT CONSUME**
— a `createPatch` that did not fully do its job — **and that is precisely what this screen must
catch.** A survivor is a **MISMATCH** and is **`BLOCKED`**, never quietly admitted.

#### 26.2.2 🔴 **THE 3-vs-5 DISCREPANCY, RESOLVED FROM THE DICT. NEITHER RECORD IS WRONG.**

§25.6 flagged, and refused to paper over, that §20.2.3 reports **three names** beside counts
totalling **five patches**. **The dict settles it, and the arithmetic closes exactly:**

- The **three** are the names the dict **CREATES**.
- The **five** are the patches the **RESULTING** boundary carries.
- The dict consumes **four** source patches by name — `auto0`, `auto1`, `auto2`, `auto3` — and
  **§20.2.3's own "without the dict" row states the pre-`createPatch` set on that probe as
  `auto0…auto5`.**
- **6 source − 4 consumed + 3 created = 5.** The survivors `auto4` and `auto5` are typed `patch`,
  giving **wall 1, symmetry 1, patch 3, empty 0** — **§20.2.3's counts, exactly, including
  `empty 0`.**

⚠ **AND THE RESIDUE IS AN ARTIFACT OF THE PROBE, NOT A PROPERTY OF THE M6.** §20.2.1 states that
those probes ran *"with a real 3×3×3 plot3d block"*; a block has six flat faces, which `autoPatch
60` splits into six patches, two of which the dict does not name. **This is a reading of §20.2.1's
own words about which mesh those probes used, and it is labelled as such rather than as a new
measurement.** ✅ **Corroborated independently, and NOT used as the registration's source:** both
existing levels' own `constant/polyMesh/boundary` files carry **exactly three patches**,
`wing`(wall) / `inout`(patch) / `sym`(symmetry) — L3 `1560 / 1560 / 4352`, L2 `6240 / 6240 / 8704`.
**The registered expectation is taken from the DICT; those two files are named here only as the
corroboration that the chain leaves no residue on this geometry.**

#### 26.2.3 THE THREE CHAINS — **NAMED SEPARATELY, BECAUSE THE RULING FORBADE ASSUMING ONE MECHANISM**

> *"do not assume all three levels share a mechanism"* — the ruling. They are enumerated, and the
> measurement that ties L2 in is stated rather than inferred.

| level | the artifact that DETERMINES its names | how the chain reaches that dict |
|---|---|---|
| **L1** (1,597,440) | `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/system/createPatchDict` | **`cases/M6SR/build_m6sr_l1.sh` B3** stages that exact file under a sha256 pin — **`:527`** (`MS_SHA_CREATEPATCHDICT`), **`:558`** (`stage_mesh_dict`), refusing at exit 10 on a mismatch (`:544`) — and then runs `createPatch -overwrite` (**`:748`**). **THE PIN IS IN COMMITTED CODE.** |
| **L3** (99,840) | the **same file**, in its own tree | `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/preProcessing.sh` runs `plot3dToFoam -noBlank volumeMesh.xyz` → `autoPatch 60 -overwrite` → `createPatch -overwrite` → `renumberMesh -overwrite` against that tree's own `system/createPatchDict` — **the very file `build_m6sr_l1.sh` pins.** |
| **L2** (399,360) | `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/system/createPatchDict` | `.mesh-cache/onera_m6/polyMesh` is a **MIRROR**: **all five** of its polyMesh files are **byte-identical** to `A3-onera-m6-transonic/constant/polyMesh` (measured, sha256 per file: `points.gz`, `faces.gz`, `owner.gz`, `neighbour.gz`, `boundary`). That tree's `preProcessing.sh` runs the same four-utility chain against its own `createPatchDict`. |

**AND THE THREE DICTS ARE ONE FILE BY CONTENT.** Measured: `A3-onera-m6-adjoint-coarse/system/
createPatchDict` and `A3-onera-m6-transonic/system/createPatchDict` both hash
**`846e45d721e8be7567bd46a08ba3ae8e0e577b167b64d5308b886a075677140e`** — the sha256
`build_m6sr_l1.sh:527` already pinned. **One dictionary determines all three levels' patch names.**

#### 26.2.4 THE REGISTERED SETS

| level | **expected patch-name set** | dict path | dict sha256 | behaviour on mismatch |
|---|---|---|---|---|
| **L1** | **`{wing, inout, sym}`** | `…/A3-onera-m6-adjoint-coarse/system/createPatchDict` | `846e45d7…140e` | **`BLOCKED`**, naming both sets |
| **L2** | **`{wing, inout, sym}`** | `…/A3-onera-m6-transonic/system/createPatchDict` | `846e45d7…140e` | **`BLOCKED`**, naming both sets |
| **L3** | **`{wing, inout, sym}`** | `…/A3-onera-m6-adjoint-coarse/system/createPatchDict` | `846e45d7…140e` | **`BLOCKED`**, naming both sets |

⚠ **THERE IS NO GIT BLOB SHA FOR THESE DICTS, AND THE RULING ASKED FOR ONE. THE GAP IS NAMED, NOT
PAPERED OVER.** The dictionaries live **outside version control**, under
`/home/ubuntu/certonomous-runs/`, so a git blob cannot be quoted for them. **What IS committed is
the pin**: `build_m6sr_l1.sh:527` carries that sha256 in tracked code, and `:544`/`:550` refuse at
build time on any other file. **For L2 and L3 no committed line pinned their trees' dicts at all**
— so the comparator now takes that job: **`verify_patch_name_source()` re-hashes the dict every time
the screen runs and REFUSES (rc 2) if it is absent or has moved.** An expectation resting on an
unversioned file is only as good as a check on that file, and the check runs at screen time rather
than once at authorship. **Control `C29` plants a one-character edit of the real dict and requires
the pin to reject it.**

⚠ **WHAT THE DICT ALONE CANNOT SAY, STATED BECAUSE THE RULING INVITED A "STOP" IF SO.** The dict
determines the three names it **creates**. It does **not** determine how many `autoN` patches
`autoPatch 60` will produce on a mesh it has not seen, and therefore **cannot by itself exclude a
survivor.** **That is not a reason to leave the level unregistered — it is the reason the screen is
falsifiable.** The registered expectation is *what the dict specifies*; a survivor is a **mismatch**
and is **`BLOCKED`**, which is exactly the failure the ruling names (*"createPatch can fail and
leave `auto0..auto5`"*). **The registration predicts; the screen catches the miss.**

⚠ **THIS DOES NOT OVERTURN §7's SENTENCE THAT L1's NAMES *"are NOT predicted here"*.** That sentence
is true of **§7**, which declined to predict them, and it is left standing. **This amendment does not
predict them either — it DERIVES them from the instrument that dictates them**, an instrument §7 did
not know about and §20.2.3 only discovered later.

---

### 26.3 🔴 **PREDICTION `P7`'s FALSE ATTRIBUTION — STRUCK BY QUOTE (rule 6)**

§25.6 named it and did not strike it. It is struck here. **`P7` at line 1371** ends by crediting a
check to a clause that has never performed it:

> 🔴 **STRUCK BY QUOTE** *(the closing sentence of §11's `P7` row, line 1371)*: ~~*"The launcher **refuses** a level whose patch names it did not expect (A9)."*~~

**`A9` GRADES TYPES AND A COUNT. IT HAS NEVER GRADED NAMES**, and `gate_a()`'s own A9 detail now says
so in terms. The name screen is **`A13`** (Amendment 19) and its launch-path limb is **`B4s`
condition 5** (this amendment). **The sentence was false when written, false when Amendment 19
made the check exist, and is true of nothing until `B4s` runs.**

⚠ **§7's OWN CLOSING SENTENCE IS *NOT* STRUCK, AND THE DIFFERENCE IS THE POINT.** §7 line 1081 reads
*"The launcher REFUSES a level whose patch names it did not expect"* — **with no false
cross-reference.** It named a thing the launcher did not do. **After this amendment the launcher
does it.** A sentence that was ahead of its implementation is made true by the implementation; a
sentence that credits the wrong clause stays wrong however much code is written, and is struck.

---

### 26.4 THE CONTROLS — **AND HOW EACH MUTANT DIED, NOT MERELY THAT IT DID**

#### 26.4.1 `T6` — **THE LAUNCH PATH ITSELF, DRIVEN.** `cases/M6SR/check_m6sr_launch_path.sh`

**WHAT WOULD NOT HAVE BEEN ENOUGH.** Amendment 19's `C25`–`C28` already prove `gate_a()` **returns**
`BLOCKED` for each condition. **That is not this.** `T6` extracts the driver's own
`section7_launch_screen()` from `run_m6sr_b5.sh`, drives it against a level planted to fail **each**
clause, and requires that **the solve does not start** — observed as the **absence of a marker** that
stands for the solver invocation.

| limb | what was planted | **how the mutant died** |
|---|---|---|
| **T6b** | *(nothing — the CLEAN TWIN, run FIRST)* | **it did not die: rc 0 and the solver marker WAS written.** Without this the four below prove only that something failed |
| **T6c/a10** | boundary openness `1e-09`, three orders above §7's `1e-12` | **exit 11, no solver marker**, message names `S7_C2_boundary_openness_le_1e-12` with `value=1e-09 threshold=1e-12` |
| **T6c/a11** | `Number of regions: 9` | **exit 11, no solver marker**, message names `S7_C3_number_of_regions_equals_1` with the value against the required `1` |
| **T6c/a12** | `Min volume = -4.2e-11` — an inverted cell | **exit 11, no solver marker**, message names `S7_C4_min_cell_volume_strictly_positive` with the signed value |
| **T6c/a13** | `WING3D / FARFIELD / SYMMETRY` — **correct types, wrong names** (the measured P7 precedent) | **exit 11, no solver marker**, message names `S7_C5_patch_names_match_…` with **both** sets, `expected=` and `actual=` |
| **T6d** | the level id `L0_NOT_A_REGISTERED_LEVEL` on the **clean** fixture | **exit 12 — a DIFFERENT code from 11 — no solver marker**, and the message says in terms that a refusal is not a `BLOCKED` |
| **T6e** | *(the clean twin AGAIN, after all five refusals)* | **rc 0 and the marker written again** — the harness did not simply stop working |
| **T6a / T6a′ / T6a″** | — | the extracted screen contains no `docker` and no `run_in_container`; it carries `timeout -k 5 120 python3`; and 124/137 is an explicit refusal branch |
| **T6f** | — | **the step order, on the driver's own comment-stripped code**: `checkMesh` at code line **250** < the screen at **294** < the **earliest** of **two** `mpirun … rhoSimpleFoam` lines, at **312** |
| **T6g** | — | the screen is called **exactly once at top level** — item 47 was a screen that existed and was never invoked, so *defined* is not the test |

**MEASURED: `check_m6sr_launch_path.sh --section7-only` → 12 checks passed, 0 failed, exit 0.**

⚠ **THE MARKER IS A STAND-IN AND IS LABELLED AS ONE.** It is not `rhoSimpleFoam`; **no solver runs
in this suite, and none ran in this amendment.** What makes the stand-in load-bearing is **`T6f`**,
which asserts on the **real driver's own code** that the screen sits after `B4`'s `checkMesh` and
before the earliest solver line. **Position in the real file plus behaviour in the harness is the
pair; neither alone would do, and that is said rather than left to be noticed.**

⚠ **AND `--section7-only` IS A NEW MODE THAT NAMES WHAT IT SKIPS.** `T1`–`T5` (items 28/30/31/32)
start a **real container** on the pinned digest; item 47's repair needs none. The mode prints, on
stdout, the five tests it did **not** run and why, is **never the default**, and **cannot report a
pass for anything it skipped.**

#### 26.4.2 THREE MUTATIONS OF THE DRIVER — **EACH DROVE `T6` RED, IN ITS OWN WAY**

Run against a **scratch copy** of `cases/M6SR/`; the tracked files were not touched.

| mutation | **how it died** |
|---|---|
| **`MUT1`** — the screen is defined but **never called** (**item 47's exact original defect**) | `T6f` FAILED (*"could not locate … the screen call ('none')"*) and `T6g` FAILED (*"found 0"*). 10 passed, **2 failed**, exit 1 |
| **`MUT2`** — the `BLOCKED` branch `say`s instead of `abort`ing | **all four `T6c` limbs FAILED, and the tell is the marker: `rc '0', marker PRESENT`.** **THE SOLVE STARTED.** 8 passed, **4 failed**, exit 1. *This is the mutation that proves the marker discriminates.* |
| **`MUT3`** — one `run_in_container` call inserted into the screen | `T6a` FAILED on the extracted text (*"the screen's code mentions docker or run_in_container"*), and `T6b`/`T6e` FAILED because the clean twin stopped reaching the solver line. 4 passed, **8 failed**, exit 1 |

#### 26.4.3 `C29` AND `C30` — **THE COMPARATOR'S OWN NEW PLANTED CONTROLS**

| control | the plant | **how it died** |
|---|---|---|
| **`C29`** | the real `createPatchDict` copied with **one character changed** (`name wing;` → `name WING;`) | the live file hashes `846e45d721e8be75…` and the screen accepts it; the one-character copy hashes `cd4173207a096a61…` and **would be REFUSED**. The same reader **also** refuses an unregistered level. **A pin never shown rejecting a wrong file is not a pin.** |
| **`C30`** | one synthetic level driven through **both** readers, clean and with the condition-2 plant | the launch screen reads `PASS` clean and `BLOCKED` planted, failing **exactly** `['S7_C2_boundary_openness_le_1e-12']`, while `gate_a()` on the same tree reads `A10 = BLOCKED` and `A9 = PASS`. **They agree in both directions** — the only thing that makes a second entry point safe. It also asserts the driver's refusal line **names the clause and the value against the threshold**, and that **the clean twin emits no such line.** |

#### 26.4.4 🔴 **`C28`'s REFUSAL LIMB WAS BROKEN BY THIS AMENDMENT AND IS RE-POINTED, NOT DELETED**

**Registering all three real levels made `C28`'s refusal limb unreachable**: it drove the real ids
`('L3','L2','L1')` and required `Unregistered`, which they no longer raise. **A limb that can no
longer reach its own failure is not a control.** It is re-pointed at `L0_NOT_A_REGISTERED_LEVEL`,
an id this registration deliberately does not record, so the unregistered branch stays exercised —
**and a POSITIVE TWIN is added that the old limb did not need: the three real ids must now be
registered and must grade `PASS`.** Without it, a mapping accidentally emptied would make the
refusal limb pass for the wrong reason. **The property under test is unchanged.**

---

### 26.5 🔴 **NO EXISTING READING MOVED — MEASURED, NOT ASSERTED**

Both module versions were loaded **in one process** and driven on **identical inputs**:

| measurement | HEAD (`5917bc9a`) | this amendment |
|---|---|---|
| controls defined | **28** | **30** (`C29`, `C30` new) |
| **existing controls whose state MOVED** | — | **NONE** |
| reds | `['C12']` | `['C12']` — the pre-existing `X7` blocker, unchanged |
| `gate_a()` on the identical synthetic clean tree, **every clause label** | 12 clauses + `_GATE_A`, all `PASS` | **byte-identical dict — `IDENTICAL: True`** |
| `--gate-a --run-root <absent>` | `REFUSED: … no points file to hash` | **the same refusal, same text** |

⚠ **ONE SHAPE CHANGED AND IT IS DISCLOSED RATHER THAN LEFT TO BE FOUND.** `A9`'s `detail.per_level`
now carries the per-level **detail dicts** returned by `section7_condition_1()` instead of raw patch
tuples. **The patch tuples are still in every one of those dicts under the key `patches`, no label
moves, and no threshold moves** — but a reader parsing `A9`'s detail positionally would see a
different shape, so it is named here.

### 26.6 `rc` PARITY, BYTE-IDENTICAL STDOUT, **ZERO** `ast.Assert`, AND THE REACH LIST

| check | measured |
|---|---|
| `--controls` under `python3` / `python3 -O` | **rc 2 / rc 2 — parity holds** (rc 2 is `X7`/`C12`, pre-existing) |
| stdout | **byte-identical, 8,937 bytes** (`cmp`) |
| stderr | **byte-identical** (`cmp`) |
| `ast.Assert` nodes in `analyse_m6sr.py` | **0** — and the detector was **planted with one `assert` appended and SEEN**: count went `0 → 1`. A zero from a detector not shown able to see a non-zero is not evidence |
| `C23`'s `must_reach` | extended by **`section7_screen`, `section7_condition_1`, `verify_patch_name_source`, `_section7_screen_summary_lines`** — so a future edit cannot orphan the launch screen the way item 5 orphaned `gate_p`. `C23` remains discriminating: `_control_unreachable_sentinel` still reads unreachable |

---

### 26.7 🔴 **ITEM 48 — NEW, THE NINETEENTH PASS. AMENDMENT 13's OWN RULED STEP `B3c` HAS NO IMPLEMENTATION IN ANY EXECUTABLE, AND IT SITS DIRECTLY IN FRONT OF `B4` AND `B4s`.**

| # | the finding | how it was measured | consequence |
|---|---|---|---|
| **48** 🔴 | **§19.3 RULED, pre-compute: *"§8's case is written BEFORE `B4`, as step `B3c`, ordered `B3`/`B3s` → `B3c` → `B4` → `B5`."*** §19.8 costs `B3c` at **0.019 core-min per level**; §20.2.4 says *"`B3c` is **not moved and not redefined** by this amendment"*; §20.7 says the same. **`B3c` EXISTS IN THIS REGISTRATION, IN ITS COST TABLE, AND IN TWO LATER AMENDMENTS' DISCLAIMERS — AND IN NO EXECUTABLE.** `cases/M6SR/write_m6sr_case.py` is invoked by `run_m6sr_b5.sh` at **`:781`** and **`:786`**, **both AFTER the `stage` exit at `:688`**, and therefore **AFTER `B4`'s `checkMesh` at `:666`**. | **`grep -c 'B3c' cases/M6SR/run_m6sr_b5.sh` = 0**, PLANT-VERIFIED: `0` → a probe line added → **`1`** (the searcher is shown able to see one) → probe removed → `0`. In `build_m6sr_l1.sh`, `B3c` occurs **3 times, all in comments; 0 times in comment-stripped code**, and its single comment-stripped `write_m6sr_case` line is **a JSON string in an `echo`, not an invocation**. | 🔴 **THE CONSEQUENCE IS ALREADY MEASURED, BY §19.3.1 ITSELF:** with the case written after `B4`, `checkMesh` returns **inner rc 1** — `cannot find file "/case/system/controlDict"` — and the driver **aborts at exit 6** with **no `log.checkMesh`**. **So `B4` cannot produce the artifact Gate A grades, and `B4s` — the screen this amendment just wired — can never run on the real ladder either.** It fails **closed** (exit 6) and has never fired, since no run root exists: **this is a live unrunnability, not a live corruption.** **NOT REPAIRED HERE, and the reason is stated:** placing `B3c` moves §8's case write across the driver's `stage`/`solve` phase boundary, which changes what phase `stage` alone does — **a step-order change of exactly the class §22.6 item 32 reserves to the supervisor** — and folding an unrequested repair into this diff would put it in front of check 1 unannounced. |

---

### 26.8 COST — RULE 12, AND **NONE OF IT IS LADDER COMPUTE**

**No ladder compute was authorised or spent. `B0`–`B6` are untouched and the run root remains
plant-verified absent.** All work was at **1 rank**:

| activity | wall s | ranks | **core-min (MEASURED from the clock)** |
|---|---|---|---|
| `--controls` under `python3` **and** `python3 -O` | 10 | 1 | **0.1667** |
| the HEAD-vs-worktree in-process control diff, the `gate_a` fixture diff, the `ast.Assert` census, and the five timed `B4s` invocations | 11 | 1 | **0.1833** |
| `check_m6sr_launch_path.sh --section7-only` — ×1 clean + ×3 driver mutations | 2 | 1 | **0.0333** |
| `--selftest` (controls + `C16` + the mutation loop over **28** targets) | 155 | 1 | **2.5833** |
| **TOTAL** | **178** | 1 | **2.9666** |

⚠ **THIS IS THE COST OF ONE RUN OF EACH ACTIVITY, AND THAT IS SAID RATHER THAN LEFT TO BE ASSUMED.**
While developing the repair this lane ran several of these repeatedly — the launch-path suite and
`--controls` more than once each. **That development compute is NOT separately metered and is
therefore NOT estimated here**: an invented figure beside these measured ones would be worse than
the honest gap. **Every number in the table above is a clock reading of a single run.**

#### 26.8.1 `B4s`'s OWN COST — **MEASURED, AND THE NUMBER IS GIVEN RATHER THAN THE WORD "NEGLIGIBLE"**

The supervisor's ruling: *"State the added core-minutes honestly; if the added cost is negligible,
say the measured number rather than calling it negligible."*

| | measured |
|---|---|
| five timed invocations, host `python3`, 1 rank, **no container** | **60 / 59 / 59 / 59 / 60 ms** |
| worst case, per level | **0.060 wall s × 1 rank ÷ 60 = 0.0010 core-min** |
| **across all three levels** | **0.0030 core-min** |
| against §2.4's registered ladder estimate of **615.24 core-min** | **4.9 × 10⁻⁶ of it** |

> **`B4s` is UNBUDGETED and reported on its own line**, exactly as §18.9 treats `B3s`/`B5p`/`B5g`
> and §19.8 treats `B3c`. **§2.4's cost table is unchanged in every cell, including the TOTAL row**
> (est ≈ 615.2, cap 1,903.0). **The alternative — a budgeted row — would move the TOTAL, and that
> is a decision, not a consequence of this repair, and it is the supervisor's.** This section takes
> the option that moves nothing.

**CHARGED VERSUS MEASURED:** every core-minute above is **MEASURED** — wall seconds × ranks ÷ 60,
read off the clock. Any dollar figure is **derived** at the recorded **$0.0513/core-h** and is
**reported-by-owner, never measured**: this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

⚠ **NO `docs/COST_CALIBRATION.md` ROW IS FILED, AND THAT IS DELIBERATE.** Rule 12's
estimate-versus-actual is owed at a **process completion** — a rung graded, a case closed. **Nothing
completed here**: no gate was graded and no rung ran. **Inventing a calibration row for a document
and instrument edit would put a fabricated actual beside a real estimate**, which is worse than the
absent row. **The row is owed at `B4`, and `B4` has not run** — and per item 48 it cannot yet.

---

### 26.9 🔴 **THE RE-PIN — THREE PINNED EXECUTABLES MOVED, AND EVERY LIVE ROW CARRYING A SUPERSEDED BLOB IS STRUCK**

**This amendment edits THREE of the ten pinned executables.** A search of this file for each
superseded blob was run **and its count reported** rather than assumed, because §25.13 already
found **two** live rows where a reader would have expected one.

**`cases/M6SR/analyse_m6sr.py` — ONE live row carried `1ed1cee4`:**

> 🔴 **STRUCK BY QUOTE** *(§25.13's row — the pin that was IN FORCE)*: ~~*"| **`cases/M6SR/analyse_m6sr.py`** (comparator, §9 and §23.5 row 1) | **`1ed1cee48bb945926cb23832eb3bed6669d53add`** | `efe6aa53bdd7d1b1bf3a365b99a4a0fa166dfdbf58d075d2ad6c557d032b0ec4` | **3,200** | **§9 registered** — **RE-PINNED HERE** |"*~~

**`cases/M6SR/run_m6sr_b5.sh` — ONE live row carried `27996a8d`:**

> 🔴 **STRUCK BY QUOTE** *(§22.2's row)*: ~~*"| **`cases/M6SR/run_m6sr_b5.sh`** (sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`) | **`27996a8dbd31c8edf38923c7ec31924111707f7f`** | `7c51d04f8c34b032430a93a3f64ac0d26d57c3d03a409be919c90fed8f261223` | **850** | **`045a6044`** (Amendment 15, the cap repair) | **NOT in §9's table** — **RE-PINNED HERE**, §22.1(3) |"*~~

**`cases/M6SR/check_m6sr_launch_path.sh` — 🔴 TWO live rows carried `9b8d44ce`, NOT ONE, AND BOTH ARE
STRUCK.** §19.4's row and §22.2's row both record it; striking only the later would leave a reader
who finds the earlier one with an unstruck, false pin — **§25.13's lesson, applied by enumeration
rather than by memory:**

> 🔴 **STRUCK BY QUOTE** *(§22.2's row)*: ~~*"| **`cases/M6SR/check_m6sr_launch_path.sh`** (launch-path controls) | **`9b8d44ce7c68a0728db80cc83fb11dbeb77d945d`** | `0da8aad32983d6b737de346db5b6fd1d71e96c64b014d56a51ce1f495ca9372c` | 367 | **`20aad5c7`** | **NOT in §9's table** — pin UNMOVED since §19.4.2 |"*~~

> 🔴 **STRUCK BY QUOTE** *(§19.4's earlier row, carrying the SAME now-superseded blob)*: ~~*"| **`cases/M6SR/check_m6sr_launch_path.sh`** (the launch-path control suite; **NEW at `5cf8a009`**) | **`9b8d44ce7c68a0728db80cc83fb11dbeb77d945d`** | `0da8aad32983d6b737de346db5b6fd1d71e96c64b014d56a51ce1f495ca9372c` | **367** | **NOT in §9's table** — see §19.4.3 |"*~~

**THE NEW STANDING PINS**, derived with `git hash-object` on the working tree and **RE-DERIVED INSIDE
THE SAME SHELL INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT ABORTING IF ANY
HAD MOVED** — §22.2's guard, kept:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`0526991a37a8bb690b21f480864c56ca9e1508c6`** | `73819ba380e72fd6f72e37f47a626e912e10f8ba7032d31db3e5eb89bae03da2` | **3545** | **§9 registered** — **RE-PINNED HERE** |
| **`cases/M6SR/run_m6sr_b5.sh`** (sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`) | **`eab4f187f868881ba880cda53a5470f6726eb2ee`** | `ebc23b710c9daa7743a04375ad4677346be507ed44d476af2e0127ef52833d86` | **942** | **§9 registered** — **RE-PINNED HERE** |
| **`cases/M6SR/check_m6sr_launch_path.sh`** (launch-path controls) | **`ca0e980d3eaf8bd0145e81b4e5fa5ea0527c8582`** | `c33e7b14c08273cf6c564d4899288f0aaf6d3e3be4f7ba41cd20cda68cad279d` | **591** | **NOT in §9's table** — **RE-PINNED HERE** |

⚠ **THE OTHER SEVEN PINS ARE UNMOVED AND WERE RE-VERIFIED AT THIS HEAD, NOT ASSUMED** — see §26.11
for the verifier's measured exit code and its `PIN-OK` count.

⚠ **THE STRIKE-BY-QUOTE LIMITATION, RESTATED RATHER THAN GLOSSED.** Striking a row by quote in a
later section **does not remove the original row from the file**, so `check_comparator_freeze.py`
still reads the superseded rows as live and may report more than one recorded sha per path.
**CURRENCY is satisfied by the new shas above, and the registration is the authority on which pin is
in force: it is the one in the table immediately above.**

---

### 26.10 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** Every threshold the screen applies —
   `1e-12`, `1`, `> 0`, the type/count rule, and the per-level name set — **is §7's, quoted, or is
   the dict's own content.** §2.4's cost table is unchanged in every cell including the TOTAL.
2. **It does not freeze and it does not launch.** Both are the supervisor's.
3. **It does not repair item 48**, and §26.7 says why in terms.
4. **It does not touch `write_m6sr_case.py` or `build_m6sr_l1.sh`.**
5. **It does not re-derive** the physics, §5/§5.1's gates, mesh-standard compliance or the solver
   pin. Those were settled in earlier amendments and are **relied on, not re-verified here.**
6. **It does not claim `B4s` has ever run on a real level.** It has not, and per item 48 it cannot
   until `B3c` is placed. **Everything above was driven on synthetic levels written to disk and read
   back through the real readers.**
7. **SUBMISSIONS REMAIN PARKED.** Nothing was sent, filed, uploaded or registered outside this box.

### 26.11 RULE 6's AMENDMENT ASSERTIONS

- **This section is APPENDED AT THE FOOT.** **Lines whose number changed above this section: 0.**
- **Version bump:** M6SR pre-registration **v1.19 → v1.20** (Amendment 20).
- **Frozen rows are STRUCK BY QUOTE, never rewritten** — §26.3's `P7` sentence and §26.9's four pin
  rows. Each strike was checked character for character against the line it strikes.
- **The unchanged-prefix sha of this file at `5917bc9a`** — the whole file as committed, before this
  section — is **`0b293aea1b4be0081b9ee1250d2df24ba382adaaac35a415bdfc4f6cbefb7fcd`**, re-derived
  **inside the commit invocation** with the commit aborting if it had moved.
- **`FZ1` exit code at this commit:** see §26.12.

### 26.12 `FZ1` — THE REGISTERED VERIFIER, RUN AT THIS COMMIT

`python3 scripts/check_comparator_freeze.py --repo . --registration
verification/campaign/M6SR_PREREGISTRATION.md --restrict-to-registration`

⚠ **IT CANNOT BE RUN BEFORE THE COMMIT IT VERIFIES, AND THAT IS A PROPERTY OF THE VERIFIER, NOT AN
EVASION.** `check_comparator_freeze.py` compares each pinned path's **HEAD blob** against its
**worktree blob**; before the commit those differ by construction for the three files §26.9
re-pins, so a pre-commit run would read `PIN-DRIFT` on exactly the rows this amendment is fixing.
**Its exit code is therefore taken immediately AFTER this commit and recorded in §26.14**, which is
committed together with the check-1 diff artifact. **This section is a forward reference, not a
claim.**

### 26.13 THE STANDING QUESTION — **ANYTHING ELSE BETWEEN THIS DOCUMENT AND A LAWFUL LAUNCH?**

🔴 **YES. THIS LANE WILL NOT WRITE A TWELFTH "NO".**

1. 🔴 **ITEM 48 (§26.7): `B3c` has no implementation.** §19.3's own ruling is unexecuted, so `B4`
   returns inner rc 1 and aborts at exit 6 with no `log.checkMesh` — **which means `B4s`, the screen
   this amendment just wired, cannot run on the real ladder either.** **This is the blocker that
   sits in front of item 47's repair, and it is one file's placement away from being closed.**
2. ⚠ **`X7` / `C12` holds `--controls` at rc 2**, and §18.5's pre-launch grading gate refuses at
   exit 8 on exactly that. **Pre-existing, unchanged by this amendment, and still on the record.**

✅ **CLOSED BY THIS AMENDMENT, and named so the list is a difference and not a repetition:** item 47
(the launch path now runs the screen and refuses at 11/12) and item 46 (all three levels' name sets
are registered from `createPatchDict`, so Gate A can be graded on the real ids for the first time).

⚠ **WHAT THIS LANE CANNOT SAY, AND DOES NOT.** It drove the screen on **synthetic** levels only; it
has never seen a real M6 `log.checkMesh` and did not produce one. It did **not** re-derive the
physics or the gates. **Check 1 on this diff, check 4, the freeze and the launch are the
supervisor's, and this lane takes none of them.**

---

### 26.14 ADDENDUM, SAME SESSION — **`FZ1`'s EXIT CODE AT AMENDMENT 20's COMMIT, AND THE CHECK-1 DIFF ARTIFACT**

§26.12 forward-referenced this section because `check_comparator_freeze.py` compares HEAD blobs
against worktree blobs and therefore cannot be run before the commit it verifies. **It was run
immediately after commit `26f47940`:**

`python3 scripts/check_comparator_freeze.py --repo . --registration
verification/campaign/M6SR_PREREGISTRATION.md --restrict-to-registration`

> **EXIT CODE `0`. `VERDICT: PASS`. `PIN COVERAGE: 10 of 10 pinned executable(s) judged in the
> population; 10 PIN-OK, 0 violating.`**

✅ **All three re-pinned executables read `PIN-OK` at their new shas** — `analyse_m6sr.py`,
`run_m6sr_b5.sh`, `check_m6sr_launch_path.sh` — **and the other seven were RE-VERIFIED at this HEAD
rather than assumed**, each reading `PIN-OK` in the same run.

⚠ **THE VERIFIER'S OWN CAVEAT IS CARRIED, NOT DROPPED.** As at every prior amendment, all ten rows
are **NO-MARKERS**: the freeze-margin limb did not fire and cannot while this tree carries no
completion marker (§23.7, item 41). **What was tested is IDENTITY and CURRENCY. A `PASS` from this
mode is not a marker-dated freeze margin and must not be read as one.**

**THE CHECK-1 ARTIFACT.** The whole of Amendment 20's commit is on disk as one file for the
supervisor's first check:

| | |
|---|---|
| path | **`cases/M6SR/AMENDMENT_20_ITEM_47_LAUNCH_PATH.diff`** |
| content | the **unmodified stdout** of `git --no-pager show 26f47940fba7d6c13bb019cb4c92cbb7d9600820` |
| size | **106,419 bytes, 1,489 lines** |
| sha256 | `08f3dc52bcf30dc199a014607c28714a48df08e2e56de84fac12e6973cc2f8b6` |
| equality | **`cmp` against a FRESHLY RECOMPUTED `git show` of the same sha: BYTE-IDENTICAL** |

**AND THE COMPARISON IS PLANT-VERIFIED (rule 3):** the same `cmp`, run against a copy of the fresh
output with **one line appended**, **DOES report a difference** — so the equality above is evidence
and not a comparator that cannot see one.

---

## 27. AMENDMENT 21 — 2026-09-04, **PRE-COMPUTE**. **ITEM 48 IS REPAIRED: §19.3's OWN RULED STEP `B3c` NOW EXISTS IN AN EXECUTABLE — AND IT IS *SPLIT*, BECAUSE THE OBVIOUS FIX WOULD HAVE MADE STANDING RULE 4's AGE GUARD *VACUOUS*.** `B3c` WRITES `constant/` + `system/` BEFORE `B4`; NEW STEP `B3z` WRITES `0/` AT SOLVE TIME SO THE ANCHOR STILL DATES THE LAUNCH BEING GRADED. **RULE 4's AGE GUARD GETS ITS FIRST CONTROL EVER.** AND THE `c1625208` GATING LEAD IS **SETTLED: NOT A REGRESSION.**

**Written by a lane under the cfd supervisor's express ruling on item 48, quoted where applied.
It moves NO gate, NO threshold, NO cap and NO label. It does not freeze and it does not launch.**

### 27.0 THE LAWFULNESS CONDITION, AND HOW IT WAS CHECKED — **NOT ASSERTED, PLANTED**

Run directory: **`verification/runs/M6SR_runs`**, **plant-verified absent** — `find` returns **0**,
a probe created at that exact path returns **1** (the searcher is shown able to see it), and after
`rmdir` — which **refuses a non-empty directory** — **0**. `test -e` reads **ABSENT**;
`git ls-files` returns **0 rows**. **NO COMPUTE HAS OCCURRED UNDER THIS REGISTRATION.**

---

### 27.1 ITEM 48 — THE RULING, AND WHY THE OBVIOUS REPAIR WAS REFUSED

> **RULED (supervisor, verbatim):** *"IMPLEMENTING A STANDING PRE-COMPUTE RULING IS NOT A NEW GATE,
> so the direction is settled: B3c goes into the executable, ahead of B4's checkMesh. BUT DO NOT
> SIMPLY MOVE THE `:786` CALL ABOVE `:666` … `write_m6sr_case.py` writes the initial fields as well
> as `system/`. Rule 4's age guard requires every field at endTime to be NEWER THAN THE CASE'S OWN
> `0/` ANCHOR, because that anchor is touched LAST AT LAUNCH and therefore DATES THE RUN ALLOWED TO
> PRODUCE THE ANSWER. If `0/` is written at STAGE time … THE AGE GUARD WOULD PASS UNCONDITIONALLY.
> It would be VACUOUS, and a vacuous guard that reports green is worse than an absent one, because
> it CERTIFIES."*

#### 27.1.1 STEP 1 OF THE RULING — **THE CONFLICT, MEASURED BEFORE ANYTHING WAS CHOSEN**

| question | **measured answer** |
|---|---|
| Does `write_m6sr_case.py` create `0/`, or only `system/` and `constant/`? | **It creates `0/`.** `:507` writes each of the seven fields into `os.path.join(case, "0", name)`. **So the supervisor's branch (2) applies, not branch (3).** |
| Does the solve phase run a pre-existing-`0/` guard, and would `B3c` trip it? | **Yes, and yes.** The guard is at `run_m6sr_b5.sh:263`, inside section 1 *"REFUSALS BEFORE ANY WORK"* — it runs on **every invocation, before any phase branch**. A `stage` run that wrote `0/` would make the **next** `solve` invocation abort at **exit 4**. `write_m6sr_case.py:780` carries the same refusal independently. **The conflict is real and is not hypothetical.** |
| Is the age guard's anchor really `0/U`'s mtime? | **Yes** — `analyse_m6sr.py` `completion_clauses()`: `t0 = os.path.getmtime(case/0/U)`, then every field at `endTime` must satisfy `getmtime(field) > t0`. |

#### 27.1.2 STEP 2 OF THE RULING — **WHAT `checkMesh` ACTUALLY REQUIRES, BY MEASUREMENT**

> *"Establish what checkMesh requires BY MEASUREMENT, not by assumption: run it against a case with
> `system/` and no `0/` and see whether it completes. §19.3.1 already measured the converse case, so
> this is the same experiment run the other way."*

**Three arms, one experiment, on the pinned digest `sha256:2927768a…`, the same L3 mesh, the
driver's own `-v`/`-w`/`-u 1002:1002 --group-add` shape, in a scratch tree — NOT in the run root:**

| arm | case contents | **inner rc** | `log.checkMesh` | last matched line |
|---|---|---|---|---|
| **known negative** | mesh only | **1** | 1,545 b | `cannot find file "/case/system/controlDict"` |
| **known positive** | mesh + `constant/` + `system/` + `0/` | **0** | **3,330 b** | **`Mesh OK.`** |
| 🔴 **THE EXPERIMENT** | mesh + `constant/` + `system/`, **`0/` REMOVED** | **0** | **3,330 b** | **`Mesh OK.`** |

> **`checkMesh -constant` NEEDS `system/` AND DOES NOT NEED `0/`.** The reader is calibrated in
> **both** directions by the first and second arms, so the third is not a lone green (rule 3), and
> the two passing arms produce logs of **the same 3,330 bytes**.

#### 27.1.3 THE REPAIR — **THE WRITE IS SPLIT, AND THERE IS STILL EXACTLY ONE WRITER**

`write_m6sr_case.py` gains **`--phase`**, and §8's single-writer rule is untouched — this is **one
file with two phases, not a second writer**, and the driver still authors no case file of its own.

| phase | writes | when | why there and nowhere else |
|---|---|---|---|
| **`pre-check`** → step **`B3c`** | `constant/` + `system/` + a mesh identity token | **stage, before `B4`** | `checkMesh` cannot construct a `Foam::Time` without `system/controlDict` |
| **`zero`** → step **`B3z`** | **`0/` only, `0/U` last** | **solve, immediately before the solver** | **the age-guard anchor must be touched at the launch being graded** |
| `all` *(default)* | everything, unchanged | — | kept so every existing invocation and control still behaves exactly as before |

**THE TWO HALVES ARE TIED TO ONE MESH, NOT ASSUMED TO BE.** `B3c` records a **mesh identity
token** — `sha256` over the raw bytes of `boundary` and the points file, the two files *both*
phases read — and `zero` re-hashes and **REFUSES** on a mismatch, and **REFUSES** if `system/` is
absent at all. ⚠ **The token is NOT `points_stream_sha` and is not offered as one**: that function
hashes the *decompressed* stream and belongs to Gate A item A5. This is a plain hash of two named
files whose only job is to stop one case describing two meshes. It is deliberately **not** an
import of the grading path (§9.1: the writer is a solver **input**).

**AND THE DRIVER REFUSES IF `B3c` EVER WRITES `0/`** — a new exit code **13**, with the reason in
the refusal text. The anti-vacuity property is enforced in **code**, not promised in a comment.

#### 27.1.4 THE REGISTERED STEP ORDER, AND ITS COST

> **REGISTERED (pre-compute): `B3`/`B3s` → `B3c` → `B4` → `B4s` → `B3z` → `B5`.**
> **MEASURED in the driver's own comment-stripped code:** `B3c` at line **230** < `B4`'s
> `checkMesh` at **268** < `B4s` at **312** < `B3z` at **319** < `mpirun … rhoSimpleFoam` at
> **331**. §19.3's ruled order is now true of an executable for the first time.

| step | wall s at 1 rank (5 runs) | **core-min per level** | across 3 levels | status |
|---|---|---|---|---|
| **`B3c`** | 1.174 / 1.100 / 1.106 / 1.105 / 1.107 | **0.0196** (worst case) | **0.0587** | **UNBUDGETED**, own line — §19.8 already carried `B3c` at **0.019**, and **that figure is unchanged and still describes `B3c`** |
| **`B3z`** | 1.093 / 1.103 / 1.103 / 1.104 / 1.108 | **0.0185** (worst case) | **0.0554** | **UNBUDGETED, NEW** |
| **both** | ≈ 2.21 | **0.0380** | **0.1141** | **1.9 × 10⁻⁴ of §2.4's 615.24** |

⚠ **THE SPLIT ROUGHLY DOUBLES THE CASE-WRITE COST AND THAT IS SAID, NOT BURIED.** A single-shot
`--phase all` measures **1.102 s**; the two phases together measure **≈ 2.21 s**, because the mesh
is read and its patches classified **twice, once per phase**. **That is the price of keeping rule
4's age guard non-vacuous, and at 0.038 core-min per level it is a price worth paying for a guard
that would otherwise certify.**

> **§2.4's cost table is unchanged in every cell, including the TOTAL** (est ≈ 615.2, cap 1,903.0).
> ⚠ **A BUDGETED ROW FOR `B3c` + `B3z` WOULD MOVE THE TOTAL, AND PER THE SUPERVISOR'S INSTRUCTION
> THAT DECISION IS EXPLICITLY LEFT TO THE SUPERVISOR AND IS NOT TAKEN HERE.**

---

### 27.2 STEP 4 OF THE RULING — 🔴 **RULE 4's AGE GUARD HAD NEVER BEEN SHOWN ABLE TO FAIL. NOW IT HAS.**

> *"EITHER WAY, the age guard gets a planted control proving it can still FAIL … If the guard
> cannot be shown able to fail after this change, the change is not finished."*

🔴 **A FINDING IN ITS OWN RIGHT, FOUND WHILE BUILDING THAT CONTROL: `completion_clauses()` — rule
4's strict all-or-nothing completion, INCLUDING the age guard — was called from EXACTLY ONE PLACE
IN THE COMPARATOR, the grade path, AND BY NO CONTROL AT ALL.** The single most load-bearing guard
in the campaign had no plant, in twenty amendments. **New control `C31`:**

| | measured |
|---|---|
| clean twin | `age_guard_every_field_newer_than_0_over_U` = **True**, `ALL` = **True** |
| **the plant** — ONE `endTime` field (`5/p`) pushed **3,600 s older** than the case's own `0/U` | guard = **False**, `ALL` = **False** |
| **clauses that MOVED** | **exactly `['age_guard_every_field_newer_than_0_over_U']`** — the flip is confined |
| absent-anchor limb — `0/U` removed | guard = **False**, never clean |
| the mutation control | **`C31` FLIPPED TO RED** when mutated |

**`completion_clauses` is added to `C23`'s `must_reach`**, so it cannot be orphaned the way `gate_p`
was.

---

### 27.3 THE CONTROLS ON THE SPLIT ITSELF

| control | where | **how it dies** |
|---|---|---|
| **`W6`** | `write_m6sr_case.py --selftest` | drives BOTH phases on a **real** polyMesh: `pre-check` wrote `system/controlDict` and the token and **did NOT write `0/`**; `zero` then wrote `0/` with **`0/U` newer than `system/controlDict`**. **The anchor is laid at solve time.** |
| **`W7`** | same | plants a `zero` phase with **no `system/`** → REFUSED; plants a **moved mesh identity token** on an otherwise complete case → **`MESH IDENTITY MISMATCH`**, REFUSED |
| **`T7a`** | `check_m6sr_launch_path.sh` | the five-step order on the driver's **comment-stripped code** |
| **`T7b`** | same | the driver's own **exit-13** refusal against `B3c` writing `0/` is present **in the code**, not only in a comment |
| **`T7c`** | same | **exactly one `--phase pre-check`, exactly one `--phase zero`, and NO `--phase all`** on the launch path — the phase **names** are checked, because `--phase all` at `B3c` is precisely the vacuity substitution and would satisfy a test that only counted `--phase` |
| **`MUT4`** — `B3c` deleted (item 48's original state) | driver mutation | `T7a` FAILED (`B3c='none'`), `T7c` FAILED (`pre-check=0`). 13 passed, **2 failed**, exit 1 |
| **`MUT5`** — `--phase pre-check` → **`--phase all`** (the age-guard vacuity substitution) | driver mutation | `T7a` and `T7c` FAILED, `T7c` naming `all=1`. 13 passed, **2 failed**, exit 1 |

⚠ **`W6`/`W7` NEED A REAL `polyMesh` AND THAT DEPENDENCY IS DECLARED, NOT HIDDEN.** The W1/W3
fixture is a **boundary file only** — W3's own comment says `mesh_axes` needs points and faces —
so the phase controls use this family's L3 polyMesh, and **if it is absent they go RED WITH A
REASON rather than being skipped**, the shape `C29` already takes. **A control that quietly does
not run is worse than one that fails.**

**MEASURED: `check_m6sr_launch_path.sh --section7-only` → 15 checks passed, 0 failed, exit 0;
`write_m6sr_case.py --selftest` → 8 of 8 writer controls FIRED, rc 0.**

---

### 27.4 🔴 **THE `c1625208` LEAD, SETTLED — IT IS *NOT* A REGRESSION**

> The supervisor's lead, recorded as a lead and not a finding: *"at `analyse_m6sr.py`'s first commit
> my pattern for openness/regions/min-volume GATING returned 2 hits, against 7 for merely parsing
> them — whereas immediately before your Amendment 19 it returned 0 gating hits. That MIGHT mean §7
> gating existed at birth and was lost, which would make items 43-45 a regression."*

**IT IS SETTLED, AND THE ANSWER IS NO.** Read at source in the birth blob:

| the three `1e-12` occurrences at `c1625208` | its actual role |
|---|---|
| `:616` `hull if s <= s1 + 1e-12` | a **geometric hull tolerance** in the planform reader |
| `:1715` `abs((after14 - before14) - PLANT_CD) < 1e-12` | **control `C14`'s** plant tolerance |
| `:1867` `(r_synth < 1.0e-12) and (r_bulge > 1.0e-12)` | **control `C20`'s** residual tolerance |

**NONE is boundary openness.** Likewise `n_regions` appears in exactly one comparison,
`key in ('n_regions', 'n_cells')` — an **int-coercion dispatch on the KEY NAME**, not on the value
— and `min_volume` in exactly one, `out['min_volume'] is not None`, a **None-check guarding a
division**. **There is no threshold comparison on any of the three at birth.**

> **VERDICT ON THE LEAD: items 43–45 are an OMISSION FROM BIRTH, NOT A REGRESSION INSIDE M6SR.**
> The two counts differed because the number of **unrelated** `1e-12` uses grew from **3** at
> `c1625208` to **6** at `07dbc3ea^` (GCI agreement, `C14`, `C20`, `C24` and the same hull
> tolerance) — **not because gating appeared or vanished.** The lead was a false positive and the
> supervisor was right not to report it as fact.

---

### 27.5 ⚠ **A METHOD FINDING THE CENSUS NEEDS BEFORE IT RUNS: THE PRODUCER-KEYED TRANSITIVE CLOSURE DOES *NOT* TERMINATE USEFULLY IN THIS FILE**

While settling the lead this lane built the census key the supervisor endorsed — *"searching
outward from every expression that PRODUCES THE QUANTITY"* — as an AST fixpoint over **variable
names**: seed on the three quantity keys, add any variable assigned from a seed, repeat, then
report every comparison touching a seed. **MEASURED, and it fails:**

| commit | comparisons the transitive key reports | its own **planted** instance |
|---|---|---|
| `c1625208` (birth) | **10** | **SEEN** |
| `07dbc3ea^` | **10** | 🔴 **186 after the plant — NOT SEEN as +1** |
| now | 🔴 **243** — effectively the whole file | SEEN |

**The seed set leaks through generic local names (`v`, `key`, `m`, `got`, `out`) and swallows
everything.** 🔴 **THIS LANE THEREFORE DOES NOT USE ANY NUMBER FROM IT**, and reports it because
the same key is about to be applied to mechanisms M1–M4: **keyed on variable-name dataflow it
over-collects to uselessness, and at one commit its own plant went unseen — the census would have
been a reader that could not see what it was given.** The narrow, per-construct reading in §27.4
is what settled the lead, and a census will need a key bounded by **enumerable members** — step
ids, read sites, gate rows, cap rows — **not by dataflow closure over names.**

---

### 27.6 🔴 **NO EXISTING READING MOVED — MEASURED**

| measurement | before | after |
|---|---|---|
| comparator controls | 30 | **31** (`C31` new) |
| **existing controls whose state MOVED** | — | **NONE** |
| comparator reds | `['C12']` | `['C12']` — the pre-existing `X7` blocker, unchanged |
| writer controls | 6 | **8** (`W6`, `W7` new), all FIRED, rc 0 |
| `check_m6sr_launch_path.sh --section7-only` | 12 passed / 0 failed | **15 passed / 0 failed** |
| `--controls` rc under `python3` / `python3 -O` | 2 / 2 | **2 / 2**, stdout and stderr **byte-identical** |
| `ast.Assert` in `analyse_m6sr.py` | 0 | **0**, detector planted and **SEEN** (0 → 1) |

---

### 27.7 COST — RULE 12, AND **NONE OF IT IS LADDER COMPUTE**

**No ladder compute was authorised or spent; `B0`–`B6` are untouched and the run root remains
plant-verified absent.** The three `checkMesh` probes of §27.1.2 are **container** compute in a
**scratch tree**, of exactly the class §20.2's ablation probes already are, and are named on their
own line rather than folded into any registered row.

| activity | wall s | ranks | **core-min (MEASURED from the clock)** |
|---|---|---|---|
| the three `checkMesh` ablation probes (§27.1.2), pinned digest, scratch tree | 39 | 1 | **0.6500** |
| `--controls` under `python3` and `python3 -O`; the writer `--selftest`; the phase smoke test and its three refusal limbs | 34 | 1 | **0.5667** |
| `check_m6sr_launch_path.sh --section7-only` ×1 + two driver mutations; the `B3c`/`B3z` timing runs | 21 | 1 | **0.3500** |
| the `c1625208` lead: birth-blob extraction and the AST readings across three commits | 8 | 1 | **0.1333** |
| `--selftest` (controls + `C16` + the mutation loop over **29** targets) | see §27.10 | 1 | see §27.10 |

**CHARGED VERSUS MEASURED:** every figure is **MEASURED** — wall seconds × ranks ÷ 60, off the
clock. Dollars are **derived** at the recorded **$0.0513/core-h** and are **reported-by-owner,
never measured** (`COMPUTE_BUDGET_CHARTER.md` §5). ⚠ **This is one run of each activity; the
development re-runs are NOT metered and are NOT estimated.** ⚠ **No `docs/COST_CALIBRATION.md` row
is filed: nothing completed — no gate graded, no rung run.**

---

### 27.8 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** §2.4's table is unchanged in every cell
   including the TOTAL; `B3c` and `B3z` are UNBUDGETED and on their own lines.
2. **It does not freeze and it does not launch.** Both are the supervisor's.
3. **It does not decide the budget line.** Whether `B3c` + `B3z` earn a budgeted row in §2.4 — which
   would move the TOTAL — is **explicitly left to the supervisor**.
4. **It has never run `B3c`, `B4` or `B4s` on a real level in the registered run root.** Everything
   above was driven in scratch. **`verification/runs/M6SR_runs` is still absent.**
5. **It does not run the M1–M4 census**, which the supervisor ordered for after this lands — and
   §27.5 is this lane's input to how that census must be keyed.
6. **SUBMISSIONS REMAIN PARKED.**

### 27.9 RULE 6's AMENDMENT ASSERTIONS

- **Appended at the foot. Lines whose number changed above this section: 0**, verified by
  byte-comparing the prefix against HEAD's blob.
- **Version bump:** **v1.20 → v1.21** (Amendment 21).
- **Frozen rows are STRUCK BY QUOTE, never rewritten** — §27.11's pin rows, each machine-verified
  character for character against the line it strikes.
- **The unchanged-prefix sha of this file at `619296bc`** is
  **`9042767d4f4de1050ceb7c9c9ca675f757d7c428d55b581a8d240efb14194aa5`**, re-derived **inside the
  commit invocation** with the commit aborting if it had moved.

### 27.10 `--selftest` — **ALL 29 MUTATION TARGETS FLIPPED TO RED**

`python3 cases/M6SR/analyse_m6sr.py --selftest` — **159 wall s at 1 rank = 2.6500 core-min,
MEASURED.** **All 29 mutation targets FLIPPED TO RED**, `C29`, `C30` and `C31` included: a
control that cannot be broken is not a control. `C16` FIRED — *python3 vs python3 -O -> rc 2 /
2, identical control verdicts True*. The suite's rc 2 is the standing `X7`/`C12` red, unchanged.

**TOTAL for this amendment: 0.6500 + 0.5667 + 0.3500 + 0.1333 + 2.6500 = 4.3500 core-min.**

### 27.11 🔴 **THE RE-PIN — FOUR PINNED EXECUTABLES MOVED, AND `write_m6sr_case.py` CARRIED *TWO* LIVE ROWS**

**Four of the ten pinned executables are edited by this amendment.** Every live row carrying a
superseded blob was **ENUMERATED BY SEARCH, NOT ASSUMED** — §25.13's lesson, and it earned its
keep again: `write_m6sr_case.py` has **TWO** live rows (§18.3.1's and §22.2's), so striking only
the later would leave a reader who finds the earlier one with an unstruck, false pin.
**All five strikes are VERBATIM QUOTES, machine-verified character for character:**

> 🔴 **STRUCK BY QUOTE** *(§26.9's row — the pin that was IN FORCE)*: ~~*"| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`0526991a37a8bb690b21f480864c56ca9e1508c6`** | `73819ba380e72fd6f72e37f47a626e912e10f8ba7032d31db3e5eb89bae03da2` | **3545** | **§9 registered** — **RE-PINNED HERE** |"*~~

> 🔴 **STRUCK BY QUOTE** *(§26.9's row)*: ~~*"| **`cases/M6SR/run_m6sr_b5.sh`** (sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`) | **`eab4f187f868881ba880cda53a5470f6726eb2ee`** | `ebc23b710c9daa7743a04375ad4677346be507ed44d476af2e0127ef52833d86` | **942** | **§9 registered** — **RE-PINNED HERE** |"*~~

> 🔴 **STRUCK BY QUOTE** *(§26.9's row)*: ~~*"| **`cases/M6SR/check_m6sr_launch_path.sh`** (launch-path controls) | **`ca0e980d3eaf8bd0145e81b4e5fa5ea0527c8582`** | `c33e7b14c08273cf6c564d4899288f0aaf6d3e3be4f7ba41cd20cda68cad279d` | **591** | **NOT in §9's table** — **RE-PINNED HERE** |"*~~

> 🔴 **STRUCK BY QUOTE** *(§18.3.1's row)*: ~~*"| **`cases/M6SR/write_m6sr_case.py`** (§8's sole writer) | **`f2e8f3bc5982e92b9f5697e568c0f31f3c17d0a5`** | `eb8abf930e999ab2af2eac74793229df0ddd096a34f41756a378627ce15c360c` | 1,059 | **NOT in §9's table** |"*~~

> 🔴 **STRUCK BY QUOTE** *(§22.2's row, carrying the SAME now-superseded blob)*: ~~*"| **`cases/M6SR/write_m6sr_case.py`** (§8's sole case-file writer) | **`f2e8f3bc5982e92b9f5697e568c0f31f3c17d0a5`** | `eb8abf930e999ab2af2eac74793229df0ddd096a34f41756a378627ce15c360c` | 1,059 | **`8c0ab7a8`** (Amendment 11) | **NOT in §9's table** — the gap, §18.3.1 |"*~~

**THE NEW STANDING PINS**, derived with `git hash-object` on the working tree and **RE-DERIVED
INSIDE THE SAME SHELL INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT
ABORTING IF ANY HAD MOVED**:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`ee95e7dc340fcfac7f69387803aa827b5b0577dc`** | `021b072eda5a8c5da3a7e83e5e418481c8605bb5935448ca9e8f79a8a4b5497c` | **3618** | **§9 registered** — **RE-PINNED HERE** |
| **`cases/M6SR/run_m6sr_b5.sh`** (sole producer of `SOLVER_RC.txt`, `log.rhoSimpleFoam`, `log.checkMesh`) | **`21028b4ca05e11263cb5b38b23261a5265ebd5c4`** | `16eb4068a2c5fc50c7a4cb281810d1a95adbadc661103ea3e2e420529d1fdc1c` | **1011** | **§9 registered** — **RE-PINNED HERE** |
| **`cases/M6SR/check_m6sr_launch_path.sh`** (launch-path controls) | **`7f53ccb53ede7ab280b752cee5651a060be41280`** | `105edb01adc97cd42975b046dcb71cc0e941693d0ccd404e9e2914a227910b81` | **654** | **NOT in §9's table** — **RE-PINNED HERE** |
| **`cases/M6SR/write_m6sr_case.py`** (§8's sole case-file writer) | **`24dd3be7864603bd0fa770dfc9e006e5148416e4`** | `ccc9421ae1f083344bda29972a2a20ba4fe7fb18d680030a83d43e3c2e424543` | **1241** | **NOT in §9's table** — **RE-PINNED HERE** |

⚠ **THE OTHER SIX PINS ARE UNMOVED AND ARE RE-VERIFIED AT THIS HEAD, NOT ASSUMED** — see §27.12.

⚠ **THE STRIKE-BY-QUOTE LIMITATION, RESTATED.** Striking a row by quote in a later section does
**not** remove the original from the file, so the verifier may still report more than one
recorded sha per path. **The registration is the authority on which pin is in force: the one in
the table immediately above.**

### 27.12 `FZ1` — RUN IMMEDIATELY **AFTER** THIS COMMIT

`check_comparator_freeze.py` compares each pinned path's **HEAD blob** against its **worktree
blob**, so before the commit those differ by construction for the four files re-pinned above and
a pre-commit run would read `PIN-DRIFT` on exactly the rows this amendment fixes. **Its exit code
is taken immediately after this commit and recorded in §27.14**, alongside the check-1 diff
artifact. **This is a forward reference, not a claim.**

### 27.13 THE STANDING QUESTION — **ANYTHING ELSE BETWEEN THIS DOCUMENT AND A LAWFUL LAUNCH?**

🔴 **THIS LANE WILL NOT ANSWER "NO", AND WILL NOT GUESS A COUNT EITHER.**

1. ⚠ **`X7` / `C12` holds `--controls` at rc 2**, and §18.5's pre-launch grading gate refuses at
   exit 8 on exactly that. **Pre-existing, unchanged, still on the record.**
2. 🔴 **NOTHING HAS EVER BEEN RUN IN THE REGISTERED RUN ROOT.** `B3c`, `B4` and `B4s` have been
   driven only in scratch and only on synthetic or copied inputs. **Until the stage phase is
   driven for real, every statement here about what the launch path *will* do is a statement
   about code, not about a run.** The supervisor has ordered that drive, after a census.
3. 🔴 **AND THIS LANE DECLINES TO PUT A NUMBER ON WHAT REMAINS.** §27.5 measured that the census
   key proposed for M1–M4 **over-collects to uselessness in this file and at one commit could
   not see its own planted instance.** A remaining-count from a reader in that state would be
   worth nothing, and the honest position is that the count is **unknown and bounded only by
   the census that has not yet run.**

✅ **CLOSED BY THIS AMENDMENT:** item 48 (`B3c` exists, split, with `B3z` keeping the age guard
non-vacuous), and the `c1625208` lead (settled: **omission, not regression**).

⚠ **WHAT THIS LANE CANNOT SAY, AND DOES NOT.** It has never seen a real M6 `log.checkMesh`
produced by the registered driver in the registered run root. It did **not** re-derive the
physics or the gates. **Check 1 on this diff, check 4, the freeze and the launch are the
supervisor's, and this lane takes none of them.**

---

### 27.14 ADDENDUM, SAME SESSION — **`FZ1`'s EXIT CODE AT AMENDMENT 21's COMMIT, AND THE CHECK-1 DIFF ARTIFACT**

§27.12 forward-referenced this section. `check_comparator_freeze.py` was run **immediately after
commit `81d58a43`**:

> **EXIT CODE `0`. `VERDICT: PASS`. `PIN COVERAGE: 10 of 10 pinned executable(s) judged in the
> population; 10 PIN-OK, 0 violating.`**

✅ **All four re-pinned executables read `PIN-OK` at their new shas** — `analyse_m6sr.py`,
`run_m6sr_b5.sh`, `check_m6sr_launch_path.sh`, `write_m6sr_case.py` — **and the other six were
RE-VERIFIED at this HEAD rather than assumed.**

⚠ **THE VERIFIER'S OWN CAVEAT IS CARRIED, NOT DROPPED.** All ten rows are **NO-MARKERS**: the
freeze-margin limb did not fire and cannot while this tree carries no completion marker (§23.7,
item 41). **What was tested is IDENTITY and CURRENCY, not a marker-dated freeze margin.**

| | |
|---|---|
| path | **`cases/M6SR/AMENDMENT_21_ITEM_48_B3C_SPLIT.diff`** |
| content | the **unmodified stdout** of `git --no-pager show 81d58a43166ba6cadf2cb42b485afcc3efbcfbd8` |
| size | **71,535 bytes, 1,049 lines** |
| sha256 | `69fe82df85d316041c2c4cd37fafaefda58233c7814512f69976383c4e08f4dc` |
| equality | **`cmp` against a FRESHLY RECOMPUTED `git show`: BYTE-IDENTICAL** |
| the comparison itself | **PLANT-VERIFIED**: the same `cmp` against a copy with one line appended **DOES** report a difference (rule 3) |

---

## 28. AMENDMENT 22 — 2026-09-04, **PRE-COMPUTE**. **THE M1–M4 CENSUS, CLOSED, WITH BOTH SETS AND THEIR REASONS.** **ITEM 49** PORTS ITEM 34's REFUSAL INTO THE BUILD DRIVER; **ITEM 50** MAKES THE ENFORCED BOUND A FUNCTION OF THE REGISTERED CAP — *"ITEM 39 WAS 'THE MECHANISM DOES NOT BIND'; ITEM 50 IS 'THE MECHANISM BINDS A NUMBER THAT IS NOT THE REGISTERED CAP.'"* **B0, B6 AND GATE A ARE REGISTERED AS VERBATIM COMMAND LINES WITH EXPECTED EXIT CODES.** AND **THE CENSUS MACHINERY WAS WRONG FOUR TIMES; EACH FAULT IS RECORDED AHEAD OF ITS RESULTS.**

**Written by a lane under the cfd supervisor's rulings on items 49 and 50 and on the census,
quoted where applied. It moves NO gate, NO threshold, NO cap and NO label. It does not freeze
and it does not launch. NOTHING HAS BEEN RUN IN `verification/runs/M6SR_runs`.**

### 28.0 THE LAWFULNESS CONDITION, AND WHY IT IS THE POINT OF THIS AMENDMENT'S TIMING

Run directory **`verification/runs/M6SR_runs`**, **plant-verified absent**: `find` → **0**, a probe
at that exact path → **1**, after `rmdir` (which refuses a non-empty directory) → **0**; `test -e`
**ABSENT**; `git ls-files` **0 rows**. Re-verified after this amendment's four manual grader
invocations: **still ABSENT** — reading a gate does not create a run root.

> 🔴 **THE SUPERVISOR'S RULING ON WHY THIS CENSUS HAD TO PRECEDE THE STAGE DRIVE, AND IT IS
> RECORDED BECAUSE THIS LANE HAD NOT WEIGHED IT:** *"B3, B3c, B4 and B4s are REGISTERED, CAPPED
> STEPS. Running them is COMPUTE UNDER THIS REGISTRATION. And rule 2 says: after first compute,
> THE GATES ARE CLOSED … the stage drive does not merely spend an absence I have been citing. IT
> PERMANENTLY ENDS THIS DOCUMENT'S ABILITY TO BE AMENDED PRE-COMPUTE."* **The lane had proposed
> the drive with the census unclosed. The drive is held.**

---

### 28.1 🔴 **THE CENSUS MACHINERY WAS WRONG FOUR TIMES, AND THE FAULTS ARE REPORTED AHEAD OF THE RESULTS**

> **RULED (supervisor):** *"a census that does not print whether its plant discriminated has not
> reported a zero, it has reported a hope."* **THE `DISCRIMINATES` LINE IS NOW A STANDING
> REQUIREMENT for anything accepted as a census in this territory. THREE OF THE FOUR FAULTS BELOW
> WERE CAUGHT BY THAT LINE ALONE.**

| # | the fault | how it was caught | what it would have shipped |
|---|---|---|---|
| **1** | **MISCALIBRATED PLANT.** The plant was `echo B3c_PLANTED` against a `\b`-anchored reader; `\b` cannot match between `c` and `_`, so the plant read **ABSENT** | `DISCRIMINATES = False` | **a clean `0 affected` this lane would have believed.** The plant was wrong, not the reader |
| **2** | **ARGPARSE-DEFINITION FALSE CLEAN.** Keyed on the action, **B0 and B6 read NOT AFFECTED because `--gate-gf` and `--grade` appear in the comparator — as OPTION DEFINITIONS.** Defining an option counted as performing the action | the M3 re-key on **invocation** | **item 47's exact shape, reappearing inside the audit built to find it** |
| **3** | 🔴 **NEW CLASS — DEFINITION POSITION vs CALL SITE.** M2's ordering used line order, but `run_in_container()` is **defined early and called late**, so every read in its body took the *definition's* position. It reported `log.checkMesh` as *"read before written"* | the **negative twin** — an artifact that IS written — came back AFFECTED | **23 false orphans** |
| **4** | 🔴 **NEW CLASS — PARAMETERISED WRITER vs LITERAL READER.** The chain writes `WALL_${tag}.txt`, `RC_${tag}.txt`, `log.$tag`; consumers name them **literally** (`WALL_checkMesh.txt`, `log.pyhyp`). **THE FILE HAS TWO NAMES**, so string-matching producer to consumer orphans every one of them | reading each flagged artifact **at source** instead of re-running the reader | **every parameterised artifact in the chain, reported as having no producer** |

> 🔴 **FAULT 4 GENERALISES PAST THIS CAMPAIGN, AND THE SUPERVISOR ASKED FOR IT IN THESE TERMS:**
> verification's transferable finding was that *"a census keyed on what a defect is CALLED finds
> only the instances that name themselves."* **Fault 4 is one level down: this key failed not
> because it searched for what the DEFECT is called, but because it searched for what the FILE is
> called — and the file has two names, one at the writer and one at the reader.**

#### 28.1.1 🔴 **A FINDING THIS LANE WITHDREW BEFORE IT LEFT ITS HANDS**

> **RULED (supervisor):** *"Record the withdrawal in the amendment, not just the finding. A census
> that shows what it retracted is worth more than one that shows only what survived."*

**`$RR/$LEVEL/log.pyhyp` was written up as a real orphan** — consumed at `build_m6sr_l1.sh:305` to
read the `Total Faces:` banner, with no producer the reader could see, and about to be reported as
a launch-blocking break in the B2→B3 chain. **It IS produced, at `:235`, as `log.$tag`** (fault 4).
**Withdrawn before it was sent.** ⚠ **That is the second time in one day a reader of this lane's
would have named the wrong defect** — the first being `check_m6sr_launch_path.sh`'s own recorded
case where a refusal captured as a value made three mutations die of the wrong cause.

---

### 28.2 THE CENSUS — **BOTH SETS, WITH REASONS. PER §2an.6 THE NOT-AFFECTED HALF CARRIES THE CLAIM.**

#### 28.2.1 `M1` — UNIMPLEMENTED RULED STEPS. **Enumeration: 17 step ids from the registration's own tables.**

**AFFECTED: 0.** **NOT AFFECTED: 17**, each with the executable that performs its registered action:

| step | action | performed by |
|---|---|---|
| `B0` | Gate GF graded | ⚠ **see `M3` — this row is a FALSE CLEAN of fault 2 and is superseded there** |
| `B1` | `cgns_utils coarsen` | `build_m6sr_l1.sh` |
| `B2` | pyHyp march | `build_m6sr_l1.sh` |
| `B3` | `plot3dToFoam`+`autoPatch`+`createPatch`+`renumberMesh` | `build_m6sr_l1.sh` |
| `B3c` | `constant/`+`system/` before B4 | `run_m6sr_b5.sh` (Amendment 21) |
| `B3d` | the four mesh-stage dicts staged | `build_m6sr_l1.sh` |
| `B3s` | mesh copied into the run root | `run_m6sr_b5.sh` |
| `B3z` | `0/` written at solve time | `run_m6sr_b5.sh` (Amendment 21) |
| `B4` | `checkMesh` | `run_m6sr_b5.sh` |
| `B4s` | §7's screen | `run_m6sr_b5.sh` (Amendment 20) |
| `B5` | — | **N/A — parent id of B5a/b/c, not a step of its own** |
| `B5a`/`B5b`/`B5c` | the solves | `run_m6sr_b5.sh` |
| `B5g` | grading-path rehearsal | `run_m6sr_b5.sh` |
| `B5p` | solver pin preflight | `run_m6sr_b5.sh` |
| `B6` | Gate G + Gate P graded | ⚠ **see `M3` — FALSE CLEAN of fault 2** |

**SUMS: 0 + 17 = 17 of 17 — COMPLETE.** Plant discriminates.

#### 28.2.2 `M2` — PATHS CONSUMED BUT NOT PRODUCED. **Enumeration: 25 artifacts read by the chain.**

**AFFECTED: 0 genuine orphans.** All 14 the widened reader flagged resolve to fault 3 or fault 4,
**each verified at source rather than by re-running the reader**: `COMPLETION_CLAUSES.json` written
by an embedded-python `json.dump`; `volumeMesh.xyz` and `surfaceMesh.cgns` by container-relative
writes inside the mount; `RC_*`, `WALL_*` and `log.pyhyp` by parameterised writers.
**NOT AFFECTED: 25**, each with its producer. **SUMS: 0 + 25 = 25 of 25 — COMPLETE.** Both plant
limbs printed.

#### 28.2.3 `M3` — SCREENS REGISTERED BUT NOT RUN. **Enumeration: the 12 modes the comparator's own argparse defines.**

Keyed on **INVOCATION** — a body other than the comparator that PASSES the flag. Plant discriminates.

| set | members |
|---|---|
| **NOT AFFECTED (2)** | `--controls` ← `run_m6sr_b5.sh` (B5g); `--section7-screen` ← `run_m6sr_b5.sh` (B4s, Amendment 20) |
| 🔴 **AFFECTED (4)** | **`--gate-a`, `--gate-gf`, `--gate-p`, `--grade` — DEFINED, INVOKED BY NO EXECUTABLE** |
| **NOT A RESULT (6)** | `--case`, `--level`, `--run-root`, `--scratch`, `--mutate`, `--selftest` — these are **option PARAMETERS, not modes**, and the reader's one-line regex cannot see the ones passed on continuation lines. **Reported as NOT A RESULT, not as findings.** |

**SUMS: 4 + 2 + 6 = 12 of 12 — COMPLETE.**

#### 28.2.4 `M4` — CAPS REGISTERED BUT NOT ENFORCED. **Enumeration: the 9 cap rows in §2.4.**

⚠ **THE FIRST `M4` KEY MATCHED BARE NUMERIC LITERALS, RETURNED 0 AFFECTED, AND WAS REPORTED AS
`NOT A RESULT` RATHER THAN AS A CLEAN** — `1.0` and `2.0` match everywhere in both drivers.
Rebuilt on the cap's **dataflow into an enforcement limb**, with a plant **and** a negative twin,
both printed: **DISCRIMINATES True.**

| set | members | reason |
|---|---|---|
| 🔴 **AFFECTED (3)** | **`B1`, `B2`, `B3`** | the registered cap is **decoupled** from the enforced bound — **item 50** |
| **NOT AFFECTED (4)** | `B4`, `B5a`, `B5b`, `B5c` | the bound is **DERIVED** from the registered cap: `TMO_B4` from `$CAP_B4_TOTAL`, `TMO_B5` from `$CAP_B5` and `$RANKS`; and item 39's three limbs are present in both drivers (`timeout -k`, an unconditional `docker kill`, a 124/137 overrun branch) |
| **CARRIED TO M3 (2)** | `B0`, `B6` | **no producer at all**, so no cap enforcement can exist for them; counted once, in M3, not double-counted here |

**SUMS: 3 + 4 + 2 = 9 of 9 — COMPLETE.**

---

### 28.3 🔴 **ITEM 50 — "THE MECHANISM BINDS A NUMBER THAT IS NOT THE REGISTERED CAP." REPAIRED.**

**THE DEFECT, MEASURED AND PLANT-VERIFIED.** `build_m6sr_l1.sh` carried three lines, each **two
independent literals**, now **STRUCK BY QUOTE** in the file itself:

> ~~*"`CAP_B1_COREMIN=1.0    ; TMO_B1=60`"*~~ ~~*"`CAP_B2_COREMIN=70.0   ; TMO_B2=4200`"*~~ ~~*"`CAP_B3_COREMIN=3.0    ; TMO_B3=180`"*~~

**Each `CAP_B*_COREMIN` was used in EXACTLY ONE PLACE besides its own declaration — a `say`
string.** The number that actually reached `run_in_container`, and therefore `timeout -k`, was the
separate literal `TMO_B*`. **This file contained ZERO derived bounds; `run_m6sr_b5.sh` contains
two.** They agreed by arithmetic — 70.0 × 60 = 4200 at 1 rank — **and nothing asserted it.**

> **THE SUPERVISOR'S FRAMING, ADOPTED VERBATIM:** *"ITEM 39 WAS 'THE MECHANISM DOES NOT BIND';
> ITEM 50 IS 'THE MECHANISM BINDS A NUMBER THAT IS NOT THE REGISTERED CAP.' A cap that reads right
> in the log and binds wrong in the timeout is worse than an unenforced one, because the log
> certifies it."*

**THE REPAIR.** `TMO_B1/B2/B3` are now derived by `cap_to_wall_s <core-min> <ranks>` from
`CAP_B*_COREMIN` and an explicit per-step rank count (all three are serial per §2.4, and the rank
is written out so a future multi-rank step cannot inherit a 1-rank conversion silently). A
derivation that yielded an empty or zero bound **REFUSES at exit 3** — a `timeout -k 5s s` would
lose the bound while the log still printed the cap.

> ✅ **NO CAP MOVES. MEASURED: the derivation reproduces the struck literals EXACTLY — 1.0 / 70.0 /
> 3.0 core-min at 1 rank → 60 / 4200 / 180 wall s.**

**THE CONTROL IS THE REPAIR** — the supervisor's ruling: *"Deriving the bounds is easy; what makes
it stick is your proposed test that A MUTATED CAP MOVES THE BOUND … Without that control you have
replaced one pair of numbers that happen to agree with another pair that happen to agree."*

| limb | measured |
|---|---|
| `C8a` | the bound-setting block contains a **derivation**, not three literals |
| `C8a'` | **no** `TMO_B1/B2/B3` is assigned a bare integer literal anywhere in the driver's comment-stripped code |
| `C8b` **(negative twin)** | unmutated, the bounds reproduce §2.4's registered caps **exactly**: `60 4200 180` |
| `C8c` **(the plant)** | halving `CAP_B2_COREMIN` **70.0 → 35.0** moved `TMO_B2` **4200 → 2100 s**, **and B1's and B3's bounds did not move.** **Before this repair the same mutation would have moved NOTHING.** |

### 28.4 🔴 **ITEM 49 — ITEM 34's REFUSAL, PORTED INTO THE BUILD DRIVER. IT WAS SAFE BY ARITHMETIC, NOT BY ASSERTION.**

`run_m6sr_b5.sh` refuses at exit 6 if its wrapper log is ever inside its bind mount.
`build_m6sr_l1.sh` mounts `$RR/$LEVEL/work` and logs to `$RR/$LEVEL/log.$tag` — the mount's
**parent**, so outside it, so safe. **MEASURED: `INSIDE the bind mount` occurred ONE time in
`run_m6sr_b5.sh`'s comment-stripped code and ZERO times in this driver's.**

**WHY IT MATTERS MORE THAN THE OTHER GUARDS.** **Item 34 is the one defect in this campaign that
did NOT fail closed** — a 3,330-byte `log.checkMesh` with its banner overwritten still returned
`state=READ` with every maximum Gate A reads and **graded CLEAN**. Everything else here fails
closed and is self-announcing; **that one issued a certificate.** And **§20.2.4 records that
mounting `$RR/$LEVEL` instead was ACTIVELY CONSIDERED AND REJECTED for exactly this reason** — so
the unsafe shape is **one edit away, in the file that had no guard against it.**

| limb | measured |
|---|---|
| `C7a` | the refusal is in the driver's **CODE**, not only in a comment (full-comment lines are stripped, so the sentence describing the fix cannot satisfy it) |
| `C7b` **(the plant)** | with the mount mutated to `$RR/$LEVEL` — §20.2.4's rejected alternative — the driver **REFUSES at exit 6 before starting a container**, naming the collision |
| `C7c` **(negative twin)** | unmutated, the **mount guard does not fire**. ⚠ **This limb's first version tested for the mere EXISTENCE of an abort and FAILED**, because the unmutated run aborts *later*, at the inner-rc check, since the harness stubs the container away. **A control keyed on "something failed" cannot tell the guard under test from an unrelated refusal downstream, and would have named the wrong defect.** Re-keyed on the guard's own message |

**MEASURED: `check_m6sr_build_path.sh` → 27 checks passed, 0 failed, exit 0, 12 s container wall
(0.2 core-min).**

### 28.5 RULING (a) — **B0, B6 AND GATE A ARE REGISTERED AS VERBATIM COMMAND LINES WITH EXPECTED EXIT CODES**

> **RULED (supervisor):** *"I will not manufacture a launch blocker: §2.4 says in terms that B0's
> result 'does not gate the launch' … But 'no producer' is not harmless … What IS the defect is
> the DEGREE OF FREEDOM: a step invoked by a human is invoked with whatever arguments that human
> types … A frozen grader called with unfrozen arguments is only half a freeze."*

**MANUALLY INVOKED BY DESIGN — no runner is written for them here, because that would move the
step order again in front of a census that has only just closed.** The pass condition is **the
exit code**, never a reading of stdout — criterion `FZ1`'s shape, and item 42's ruling.

| step | **THE REGISTERED INVOCATION, VERBATIM** | expected exit, **on a completed ladder** |
|---|---|---|
| **`B0`** | `python3 cases/M6SR/analyse_m6sr.py --gate-gf --run-root verification/runs/M6SR_runs` | **0** |
| **`B4` Gate A** | `python3 cases/M6SR/analyse_m6sr.py --gate-a --run-root verification/runs/M6SR_runs` | **0** — and **2** is a REFUSAL, not a failure: A13 refuses for an unregistered patch-name set (Amendment 20 registered all three, so 2 would mean the set moved) |
| **`B6`** | `python3 cases/M6SR/analyse_m6sr.py --grade --run-root verification/runs/M6SR_runs` | 🔴 **2, NOT 0** — Gate G's registered refusal (Amendment 10, prediction `X3`, no registered refinement ratio) **is deliberately not caught**. Gate P's figure data is persisted to disk **before** Gate G runs. **A reader treating exit 2 here as failure would be wrong.** |
| *(aux)* | `python3 cases/M6SR/analyse_m6sr.py --gate-p --run-root verification/runs/M6SR_runs` | **0**, and **this mode can never produce a PASS** (§ the standalone-Gate-P note) |

⚠ **MEASURED TODAY, WITH NO RUN IN EXISTENCE: all four return exit 2**, refusing for want of
inputs — `--gate-gf` *"no boundary file"*, `--gate-a` *"no points file to hash"*, `--grade` and
`--gate-p` *"rule-4 strict completion FAILED"*. **They fail closed, and running them did NOT create
the run root** (re-verified ABSENT afterwards).

### 28.6 RULING (c) — **`B3c`/`B3z` STAY UNBUDGETED, AND THE DISTINCTION IS SAID IN ONE SENTENCE**

> **UNBUDGETED HERE MEANS "NOT FOLDED INTO §2.4's TOTAL". IT DOES NOT MEAN "UNCOSTED": rule 12
> requires every run to be costed, and `B3c` and `B3z` are costed, at 0.0196 and 0.0185 core-min
> per level, measured from the clock and recorded on their own lines in §27.1.4.**

0.1141 core-min across three levels against §2.4's **615.24** is **0.019 %** — a budgeted row would
move the TOTAL for noise. **And the doubling is recorded as a decision, not a surprise: 1.102 s
single-shot against 2.21 s split, because the mesh is read and its patches classified twice, once
per phase. That cost was accepted deliberately to keep rule 4's age guard non-vacuous.**

### 28.7 🔴 **`C31` — A FINDING IN ITS OWN LINE, NOT A CONTROL OF ITEM 48's**

> **RULED (supervisor):** *"Report it to me as a finding in its own line, not folded into item 48's
> controls."*

**`completion_clauses()` — standing rule 4's strict all-or-nothing completion, INCLUDING THE AGE
GUARD — was called from exactly ONE place in the comparator, the grade path, AND BY NO CONTROL AT
ALL, THROUGH TWENTY AMENDMENTS.** The most load-bearing guard in the campaign had never been shown
able to fail. It is now `C31`, and it is a delta: clean → guard True/`ALL` True; one `endTime` field
pushed 3,600 s older than the case's own `0/U` → guard False, `ALL` False, **and the clauses that
moved are exactly the age guard**; absent-anchor limb reads False, never clean.

### 28.8 ⚠ **AN OBSERVATION ON ITEM 39, REPORTED AND NOT REPAIRED**

`check_m6sr_build_path.sh`'s `C6` — which probes a **bare** `timeout` against a real container, and
is the executable record of item 39's platform fact — **failed once and passed on re-run.**
Investigated rather than re-run until green:

| probe | result |
|---|---|
| three deliberate re-probes at C6's exact shape | **rc 124 after 12, 13 and 12 wall seconds** on a 3 s cap — **item 39 reproduces, 3 of 3** |
| the one failing run | `docker inspect` showed the container **`created` but NEVER STARTED** (`StartedAt: 0001-01-01`), so it never ran the 12 s payload; `timeout` killed the client at 3 s and the suite's own `SWEEP` limb then found the container **left behind** |

> **ITEM 39's PREMISE IS INTACT.** The single failure and the leaked container are **one event with
> two symptoms**: a container that was created but never started, which the immediate `kill`/`rm -f`
> did not reap. ⚠ **Observed ONCE, in five runs. It is reported as an observation with its evidence
> and is NOT characterised as a mechanism**, and no repair is made to `C6` — a control that is
> re-run until green is not a control. The stray container was removed by this lane; `m6bc_`
> containers on the daemon afterwards: **0**.

### 28.9 COST — RULE 12

| activity | wall s | ranks | **core-min (MEASURED)** |
|---|---|---|---|
| the M1–M4 census readers, all keys and re-keys, across three commits | 46 | 1 | **0.7667** |
| `check_m6sr_build_path.sh` ×3 (incl. 12 s container wall) | 47 | 1 | **0.7833** |
| the four manual grader invocations of §28.5, and the item-39 re-probes | 51 | 1 | **0.8500** |
| **TOTAL** | **144** | 1 | **2.4000** |

**All MEASURED from the clock; one run of each activity, with development re-runs NOT metered and
NOT estimated.** Dollars are **derived** at $0.0513/core-h and **reported-by-owner**. **No
`COST_CALIBRATION.md` row: nothing completed — no gate graded, no rung run.**

### 28.10 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** Item 50's derivation reproduces the
   struck literals exactly; §2.4's table is unchanged in every cell including the TOTAL.
2. **It does not freeze and it does not launch**, and **it does not drive the stage** — that is a
   separate confirmation after the supervisor's check 1.
3. **It writes no runner for B0, B6 or Gate A**, and says so: that would move the step order again.
4. **It does not repair `C6`** (§28.8) and does not re-run it until green.
5. **SUBMISSIONS REMAIN PARKED.**

### 28.11 RULE 6's AMENDMENT ASSERTIONS

- **Appended at the foot. Lines whose number changed above this section: 0**, verified by
  byte-comparing the prefix against HEAD's blob.
- **Version bump: v1.21 → v1.22** (Amendment 22).
- **Frozen rows are STRUCK BY QUOTE, never rewritten** — §28.13's pin rows, machine-verified
  character for character.
- **The unchanged-prefix sha of this file at `6c1a39d4`** is
  **`2859c7b61e4244762221b1cbb5d5215abfa9bc9b10e4ac99e0397b3140dc11d6`**, re-derived **inside the
  commit invocation** with the commit aborting if it had moved.

### 28.12 THE STANDING QUESTION — **ANYTHING ELSE BETWEEN THIS DOCUMENT AND A LAWFUL LAUNCH?**

**THE CENSUS IS CLOSED AND ITS LIST IS REPAIRED.** What remains is not a count this lane invented:

1. ⚠ **`X7` / `C12` holds `--controls` at rc 2**, and §18.5's pre-launch grading gate refuses at
   exit 8 on exactly that. **Pre-existing, unchanged, still on the record.**
2. 🔴 **NOTHING HAS EVER RUN IN THE REGISTERED RUN ROOT.** Every statement in Amendments 20–22
   about what the launch path *will* do is a statement about **code**, not about a run. **The stage
   drive is the empirical check on this census, and the supervisor has ordered it held until after
   check 1.**
3. ⚠ **THE CENSUS IS BOUNDED BY ITS OWN KEYS.** M1–M4 terminate because they enumerate members —
   a step table, a read-site set, a gate table, a cap table. **A defect of a MECHANISM NOT AMONG
   THOSE FOUR would not be found by it**, and the supervisor's own instruction anticipates that:
   *"IF THE STAGE HITS SOMETHING THE CENSUS MISSED, THAT IS THE MOST VALUABLE RESULT."*

⚠ **WHAT THIS LANE CANNOT SAY, AND DOES NOT.** It has never seen a real M6 `log.checkMesh` produced
by the registered driver in the registered run root. It did not re-derive the physics or the gates.
**Check 1 on this diff, check 4, the freeze, the stage drive and the launch are the supervisor's,
and this lane takes none of them.**

### 28.13 🔴 **THE RE-PIN — TWO PINNED EXECUTABLES MOVED, EVERY LIVE ROW ENUMERATED BY SEARCH**

**Two of the ten pinned executables are edited by this amendment.** Every live row carrying a
superseded blob was **ENUMERATED BY SEARCH, NOT ASSUMED** — this campaign has now found **two**
live rows where one was expected on two separate occasions (§25.13's `analyse_m6sr.py`, §27.11's
`write_m6sr_case.py`). **Here the search returns exactly one row each, and that is a MEASUREMENT,**
**not an assumption.** Both strikes are verbatim quotes, machine-verified character for character:

> 🔴 **STRUCK BY QUOTE** *(§22.2's row for the build driver)*: ~~*"| **`cases/M6SR/build_m6sr_l1.sh`** (build driver, `B1`–`B3`) | **`caa7d9de787b1dc8cf5e45935afcc5ef425b85fc`** | `6c6f0a8f7c595d130fcaa75cf953763c78716c80a219a94493df4ae4eaf3eb90` | **828** | **`045a6044`** (Amendment 15, the cap repair) | **§9 registered** — **RE-PINNED HERE**, §22.1(1) and (2) |"*~~

> 🔴 **STRUCK BY QUOTE** *(§22.2's row for the build-path control suite)*: ~~*"| **`cases/M6SR/check_m6sr_build_path.sh`** (build-path controls, items 38/39) | **`dd9f7c4ab87f2e464e3905cf1037093e8814520c`** | `aa416ff44cb3d8f26873e2a25f5a9db4af925129656f7597f991f6467ecfd9d9` | **360** | **`045a6044`** | **NOT in §9's table** — **FIRST STANDING PIN**; §20.6 reported a sha but expressly declined to pin |"*~~

**THE NEW STANDING PINS**, derived with `git hash-object` on the working tree and **RE-DERIVED
INSIDE THE SAME SHELL INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT ABORTING
IF EITHER HAD MOVED**:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`cases/M6SR/build_m6sr_l1.sh`** (build driver, `B1`–`B3`) | **`c5fd6b297a38f5dfb445e21bf26ac6ecb2503fee`** | `d2d32bb177d782ea70397473450a377ea4dbd716901564501a302ce9dbd4635c` | **901** | **§9 registered** — **RE-PINNED HERE** |
| **`cases/M6SR/check_m6sr_build_path.sh`** (build-path controls, items 38/39/49/50) | **`d36e52f5914d9d3699639c368af5c06778068bde`** | `670fc3013e4eae193c53bde526ff4afefd1431dca7e04ef1e0353c26a954d969` | **461** | **§9 registered** — **RE-PINNED HERE** |

⚠ **THE OTHER EIGHT PINS ARE UNMOVED AND ARE RE-VERIFIED AT THIS HEAD, NOT ASSUMED** — see §28.14.

⚠ **THE STRIKE-BY-QUOTE LIMITATION, RESTATED.** Striking a row by quote in a later section does not
remove the original from the file, so the verifier may still report more than one recorded sha per
path. **The registration is the authority on which pin is in force: the one in the table above.**

### 28.14 `FZ1` — RUN IMMEDIATELY **AFTER** THIS COMMIT

`check_comparator_freeze.py` compares each pinned path's HEAD blob against its worktree blob, so a
pre-commit run would read `PIN-DRIFT` on exactly the two rows this amendment re-pins. **Its exit
code is taken immediately after this commit and recorded in §28.15**, alongside the check-1 diff
artifact. **This is a forward reference, not a claim.**

---

### 28.15 ADDENDUM, SAME SESSION — **`FZ1`'s EXIT CODE AT AMENDMENT 22's COMMIT, AND THE CHECK-1 DIFF ARTIFACT**

§28.14 forward-referenced this section. `check_comparator_freeze.py` was run **immediately after
commit `57ffbe5a`**:

> **EXIT CODE `0`. `VERDICT: PASS`. `PIN COVERAGE: 10 of 10 pinned executable(s) judged in the
> population; 10 PIN-OK, 0 violating.`**

✅ **Both re-pinned executables read `PIN-OK` at their new shas** — `build_m6sr_l1.sh`,
`check_m6sr_build_path.sh` — **and the other eight were RE-VERIFIED at this HEAD rather than
assumed.**

⚠ **THE VERIFIER'S NO-MARKERS CAVEAT IS CARRIED, NOT DROPPED.** All ten rows are NO-MARKERS: the
freeze-margin limb did not fire and cannot while this tree carries no completion marker (§23.7,
item 41). **What was tested is IDENTITY and CURRENCY.**

| | |
|---|---|
| path | **`cases/M6SR/AMENDMENT_22_ITEMS_49_50_CENSUS.diff`** |
| content | the **unmodified stdout** of `git --no-pager show 57ffbe5a0c3ca93d6a872bf69d986292ac40332c` |
| size | **50,542 bytes, 678 lines** |
| sha256 | `c4eafb74aa2ff624ebf33974b27fb710a871414281ead0d4a5bc12be3f69b8cc` |
| equality | **`cmp` against a FRESHLY RECOMPUTED `git show`: BYTE-IDENTICAL** |
| the comparison itself | **PLANT-VERIFIED**: the same `cmp` against a copy with one line appended **DOES** report a difference (rule 3) |

**AND `verification/runs/M6SR_runs` IS STILL ABSENT AT THIS COMMIT.** The stage drive is held for
the supervisor's separate confirmation after check 1.

---

## 29. AMENDMENT 23 — 2026-09-04, **PRE-COMPUTE**. 🔴 **THE FINDING UNDER `C12`: `D1` IS `INDETERMINATE` ON THE REGISTERED REFERENCE, SO THE A-MAP STATION ORDERING IS UNRESOLVED — AND SANAA'S NAMED DELIVERABLE IS A `Cp`-VERSUS-STATION FIGURE.** `C12`'s FIXTURE MOVES AND ITS MUST-SEE DOES NOT; THE OLD FIXTURE IS **KEPT AS `C12b`** ASSERTING THE VERDICT THAT IS **TRUE**. §18.5's GATE IS **NOT** NARROWED — AND `--controls` NOW EXITS **0**.

**Written by a lane under the cfd supervisor's four-part ruling, quoted where applied. It moves
NO gate, NO threshold, NO cap and NO label. It does not freeze, does not launch and does not
drive. `verification/runs/M6SR_runs` remains ABSENT.**

### 29.0 THE LAWFULNESS CONDITION — **PLANTED, NOT ASSERTED**

Run directory **`verification/runs/M6SR_runs`**: `find` → **0**; a probe at that exact path → **1**
(the searcher is shown able to see it); after `rmdir` (which refuses a non-empty directory) → **0**.
`test -e` **ABSENT**; `git ls-files` **0 rows**. **NO COMPUTE HAS OCCURRED UNDER THIS REGISTRATION.**

---

### 29.1 🔴 **THE FINDING UNDER THE FINDING — `D1` CANNOT SETTLE THE STATION ORDERING**

> **RULED (supervisor, verbatim):** *"D1's whole premise is that the series is MONOTONE, so that
> reversing it flips the direction and reveals the ordering. IT IS NOT MONOTONE. So D1 RETURNS
> INDETERMINATE ON THE REAL DATA AND CANNOT SETTLE THE A-MAP STATION ORDERING AT ALL. C12's
> unsatisfiability is the SYMPTOM; this is the disease, and it has been sitting under a red tick
> that everyone learned to step around."*

**MEASURED, on the registered reference `case_2308.dat`.** Section normal force
`Cn(s) = −(closed-loop trapezoidal integral of Cp over d(x/c))`, sections 1…7:

| section | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| `Cn` | 0.239559 | 0.278490 | 0.294704 | 0.263810 | 0.222974 | 0.178438 | 0.210512 |

**It RISES 1→3, FALLS 3→6, and RISES 6→7 — TWO TURNING POINTS, at sections 3 and 6.**
`strictly_decreasing = False`, `strictly_increasing = False` → **verdict `INDETERMINATE`**
(`Cn_last_over_first` 0.878747, `Cn_first_over_last` 1.137984, registered margin 0.75).
**Reversing a non-monotone series leaves it non-monotone, so the reversal is `INDETERMINATE` too.**

> 🔴 **REGISTERED, IN TERMS: `D1` IS `INDETERMINATE` ON THE REGISTERED REFERENCE. THE A-MAP STATION
> ORDERING IS THEREFORE *UNRESOLVED BY `D1`*, AND EVERY `Cp`-VERSUS-STATION FIGURE THIS CAMPAIGN
> PRODUCES CARRIES THAT DISCLOSURE BESIDE IT.**

**WHY THIS BEARS ON SANAA'S NAMED DELIVERABLE, stated rather than left to be inferred.** Her first
physics is *M6 surface `Cp` at the AGARD span stations* with the family band. **If the ordering is
unknown, the `Cp` comparison can be plotted against the wrong stations and still look entirely
plausible — a mislabelled span station produces a smooth, believable, WRONG figure.** §16.4 keeps
A-MAP **REPORTED, NOT GATED**, which is correct as a *gate* decision and **is not a licence to
present the deliverable as if the ordering were known.**

**THE DISCLOSURE TRAVELS WITH THE DATA, NOT ONLY WITH THIS DOCUMENT.** `gate_p_figure_data()` now
emits `A_MAP_STATION_ORDERING_DISCLOSURE`, **built from the `D1` record that call just computed**
— never asserted as a constant — carrying the verdict, the seven `Cn` values, both monotonicity
flags and `ordering_resolved_by_D1`. **Measured live: `INDETERMINATE`, `False`.** If a future
reference *is* monotone, the text changes with the data **and control `C12b` goes red in the same
breath.**

⚠ **A SECOND DISCRIMINATOR IS NAMED AND DELIBERATELY NOT BUILT**, on the supervisor's express
instruction *"do NOT build it in this pass and do not let it become a fifth thing between us and a
run."* Candidates: **local chord length**, which falls monotonically root-to-tip on a tapered wing,
and **leading-edge x-station**, which advances monotonically with span under this wing's sweep.
**Both are GEOMETRIC and therefore independent of the `Cp` column `D1` shares with Gate P** — which
is the circularity `D1` already discloses. **Neither is implemented, neither is registered as a
discriminator, and nothing here claims the ordering is settled.**

---

### 29.2 `C12` — **THE FIXTURE MOVES, THE MUST-SEE DOES NOT**

> **RULED (supervisor, verbatim):** *"I am not amending C12's must-see to its purpose clause. The
> comparator's own comment is right — 'loosening a registered control so that it passes is how a
> fail-open gets a green tick' — and I will not be the supervisor who overrides a warning the code
> left for exactly this moment. … KEEP THE MUST-SEE AS `FALSIFIED`. REPLACE THE FIXTURE."*

**THE NEW FIXTURE IS SYNTHETIC AND ITS SERIES IS EXACT BY CONSTRUCTION, NOT BY FITTING.** Each of
seven sections is a closed rectangular `Cp` loop — `Cp = −A` along the upper leg (`x` 0→1), `Cp = 0`
along the lower (1→0). The closed-loop trapezoidal integral is then **exactly `−A`**, so
`Cn = −(−A) = A` and **the series IS the `A` list**: `[0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10]`.
**A reader can check that arithmetic without running anything.**

| limb | requirement | measured |
|---|---|---|
| **`C12` must-see — UNCHANGED** | the reversed synthetic reference → **`FALSIFIED`** | **`FALSIFIED`** |
| **`C12` positive twin — NEW** | the SAME data **unreversed** → **`CORROBORATED`** | **`CORROBORATED`** |
| **`C12b` — the old fixture, KEPT** | the REAL reference, reversed → **`INDETERMINATE`** | **`INDETERMINATE`**, and as-read **`INDETERMINATE`** |
| **`C13` — unchanged** | seven identical sections → `INDETERMINATE` | `INDETERMINATE` |

**NOTHING WAS LOOSENED: the control demands the same verdict and was given data capable of
producing it.** **AND THE POSITIVE TWIN IS WHAT MAKES THE MUST-SEE MEAN ANYTHING** — a fixture that
could only ever produce `FALSIFIED` would prove nothing about the discriminator, so the same data
is required to produce **both** directed verdicts.

**`C12b` IS THE CONTROL THAT PINS THE §29.1 FINDING.** It asserts the verdict that is **true** for
the registered reference, prints the seven `Cn` values and the turning points, and states the
consequence. **If the reference ever changes to a monotone one, `C12b` goes red and the campaign is
told — rather than discovering it at Gate P.** `C12b` is added to the mutation target list.

---

### 29.3 §18.5's GATE IS **NOT** NARROWED — AND `--controls` NOW EXITS **0**

> **RULED (supervisor, verbatim):** *"the gate's logic — a solve that cannot be graded afterwards
> wastes 607 of 615 core-min — is SOUND, and 'any control red' is the right key for it. The defect
> was never the gate; it was a control that could not go green. FIX THE CONTROL AND THE GATE IS
> CORRECT AS WRITTEN. Narrowing a launch gate to accommodate a broken fixture would be the
> fail-open by a longer route."*

**§18.5's gate is BYTE-UNCHANGED by this amendment.**

> 🔴 **MEASURED CONSEQUENCE: `python3 cases/M6SR/analyse_m6sr.py --controls` NOW RETURNS `rc 0`,
> WITH ALL 32 CONTROLS FIRED — under `python3` AND `python3 -O`, with BYTE-IDENTICAL stdout
> (11,184 bytes) and stderr.** **`X7` / `C12` no longer holds the suite red.** This is the first
> time in this campaign that `--controls` has exited 0, and it was achieved by **repairing a
> fixture, not by weakening a gate or a must-see.**

⚠ **WHAT THAT DOES AND DOES NOT UNBLOCK.** §18.5's gate would now pass, so `PHASE=solve` and
`PHASE=all` are no longer refused at exit 8 for this reason. **It unblocks nothing else**: the
launch remains the supervisor's, and §29.4 records why the drive still does not use `PHASE=all`.

---

### 29.4 `B4s`'s REGISTERED INVOCATION — **THE DRIVER'S PHASE VOCABULARY CANNOT EXPRESS THE ORDERED DRIVE**

**THE STRUCTURAL FINDING, MEASURED FROM THE DRIVER'S OWN GUARD EXPRESSIONS**, extracted from its
comment-stripped code and evaluated per phase:

| guard, verbatim | line |
|---|---|
| `if [ "$PHASE" = "solve" ] \|\| [ "$PHASE" = "all" ]; then` — §18.5's gate | **436**, closing `fi` **448** |
| `if [ "$PHASE" = "stage" ] \|\| [ "$PHASE" = "all" ]; then` — the stage block | **571**, closing `fi` **739** |
| `[ "$PHASE" = "stage" ] && { … exit 0; }` | **741** |

`B3c` **637** and `B4` **719** are **inside** the stage block. **`B4s` 805, `B3z` 854 and
`mpirun … rhoSimpleFoam` 877 are all AFTER the stage exit.**

| phase | §18.5 gate | stage block | outcome |
|---|---|---|---|
| **`stage`** | **SKIPPED** — its own guard excludes stage | RUNS | `B3c` and `B4` execute, **exit 0 at 741. `B4s` NEVER REACHED.** |
| **`solve`** | evaluates | skipped | `B4s` reached, but `B3c`/`B4` are not run in this invocation |
| **`all`** | evaluates | RUNS | reaches `B4s` — **and then falls straight through to `B3z` and the SOLVER with no stop between** |

> 🔴 **SO THE ORDERED SCOPE — `B3c`+`B4`+`B4s`, HALTING BEFORE `rhoSimpleFoam` — HAS NO PHASE.**
> **RULED (supervisor):** *"I specified a run the driver cannot express."*

**THE ACCEPTED SOLUTION USES THE MECHANISM ALREADY RULED FOR `B0`/`B6`/GATE A — a registered
verbatim command line, no code change and no step-order change**, and it stops before the solver
**by construction rather than by intention**:

| step | **THE REGISTERED INVOCATION, VERBATIM** | expected exit |
|---|---|---|
| **stage** | `bash cases/M6SR/run_m6sr_b5.sh L3 stage` | **0** — runs `B3s`, `B3c`, `B4`; `B4s` is NOT reached |
| **`B4s`** | `python3 cases/M6SR/analyse_m6sr.py --section7-screen --level L3 --case verification/runs/M6SR_runs/L3` | **0** = `PASS` · **11** = `BLOCKED` · **2** = REFUSAL |

**This is the identical comparator invocation the driver makes at `:805`.** The pass condition is
**the exit code**, never a reading of stdout — `FZ1`'s shape and item 42's ruling.

---

### 29.5 THE THROUGH-LINE — **ONE FINDING, NOT FIVE. AND `C12` IS A SIXTH OF A DIFFERENT SPECIES.**

> **RULED (supervisor):** *"I want it as ONE finding, not five."*

🔴 **ALL FIVE CENSUS-MACHINERY FAULTS WERE READERS THAT COULD NOT DISTINGUISH THEIR SUBJECT FROM
SOMETHING ADJACENT TO IT.** Same sentence, five times:

| fault | the subject | the adjacent thing it was confused with |
|---|---|---|
| 1 | a planted instance | a near-miss string the anchor could not match |
| 2 | an **invocation** of a mode | the mode's **argparse definition** |
| 3 | a function's **call site** | the function's **definition site** |
| 4 | the file's name **at its writer** | the file's name **at its reader** |
| 5 | **the guard's own refusal** | an unrelated refusal **downstream in the same function** |

**The repair for all five is the same: sharpen the key until it separates the subject from its
neighbour.** ⚠ **AND `C12` IS A SIXTH OF A DIFFERENT SPECIES, WHICH IS WHY IT IS DRAWN OUT
SEPARATELY: a reader that CAN distinguish perfectly, asked a question its data cannot answer.** No
sharpening of the key would ever have fixed it — only changing the data, or accepting the answer.
**Its repair was to do both: a fixture that can answer (`C12`), and the honest answer recorded for
the data that cannot (`C12b`).**

---

### 29.6 ⚠ **A NUMBER THIS LANE GAVE THE SUPERVISOR WAS WRONG, AND IT IS CORRECTED HERE**

**This lane reported the `Cn` series as having *"direction changes at 3, 4 and 5"*, and the
supervisor repeated that figure back in his ruling.** **IT IS WRONG.** `[3, 4, 5]` was the set of
**steps whose direction differs from the FIRST step** — i.e. the falling steps — **not turning
points.** **The correct statistic is TWO TURNING POINTS, at sections 3 and 6**, which is exactly
what *"rises 1→3, falls 3→6, rises 6→7"* describes.

✅ **NOTHING DOWNSTREAM MOVES.** The series is non-monotone in both directions under either
statistic, `D1` returns `INDETERMINATE` either way, and every conclusion in §29.1 stands. **The
correction is recorded because a figure this lane put in a supervisor's hands was wrong, and a
wrong number that changes no conclusion is still a wrong number.**

---

### 29.7 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO gate, NO threshold, NO cap and NO label.** `C12`'s must-see is unchanged at
   `FALSIFIED`; §18.5's gate is byte-unchanged; `D1`'s margin, branches and logic are untouched.
2. **It does not build a second discriminator.** Two candidates are named and neither is
   implemented or registered.
3. **It does not freeze, does not launch and DOES NOT DRIVE THE STAGE.**
4. **It does not claim the A-MAP ordering is settled.** It registers that it is **not**.
5. **SUBMISSIONS REMAIN PARKED.**

### 29.8 RULE 6's AMENDMENT ASSERTIONS

- **Appended at the foot. Lines whose number changed above this section: 0**, verified by
  byte-comparing the prefix against HEAD's blob.
- **Version bump: v1.22 → v1.23** (Amendment 23).
- **The unchanged-prefix sha of this file at `e8ccd0e9`** is
  **`d5503913df5c30be843249b71df5cdc7e2061e0910127ed496f8c9d5fbd571ee`**, re-derived **inside the
  commit invocation** with the commit aborting if it had moved.

### 29.9 🔴 **THE RE-PIN — ONE PINNED EXECUTABLE MOVED, THE LIVE ROW ENUMERATED BY SEARCH**

**This amendment edits ONE of the ten pinned executables, the comparator.** The live row carrying
the superseded blob was **ENUMERATED BY SEARCH, NOT ASSUMED** — this campaign has three times found
more rows than expected (§25.13, §27.11) — and the search returns **exactly one**, which is a
**measurement, not a relief**. Struck, rule 6, by verbatim quote, machine-verified character for
character against the line it strikes:

> 🔴 **STRUCK BY QUOTE** *(§27.11's row — the pin that was IN FORCE)*: ~~*"| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`ee95e7dc340fcfac7f69387803aa827b5b0577dc`** | `021b072eda5a8c5da3a7e83e5e418481c8605bb5935448ca9e8f79a8a4b5497c` | **3618** | **§9 registered** — **RE-PINNED HERE** |"*~~

**THE NEW STANDING PIN**, derived with `git hash-object` on the working tree and **RE-DERIVED
INSIDE THE SAME SHELL INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT ABORTING
IF IT HAD MOVED**:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`6a59443ee053db22cd829f1fb7200dd46cdb413d`** | `f323ad42bb9f2b8e845ab789af5bb76644cbf8eff5516d97b78a0056a2bc5aec` | **3730** | **§9 registered** — **RE-PINNED HERE** |

⚠ **THE OTHER NINE PINS ARE UNMOVED AND ARE RE-VERIFIED AT THIS HEAD, NOT ASSUMED** — see §29.11.

### 29.10 COST — RULE 12

| activity | wall s | ranks | **core-min (MEASURED)** |
|---|---|---|---|
| the `D1` readings on the real reference and its reversal, and the branch-reachability walk | 9 | 1 | **0.1500** |
| `--controls` under `python3` and `python3 -O`, and the live figure-disclosure read | 14 | 1 | **0.2333** |
| `--selftest` (controls + `C16` + the mutation loop) | 173 | 1 | **2.8833** |
| **TOTAL** | 196 | 1 | **3.2667** |

**All MEASURED from the clock; one run of each activity, with development re-runs NOT metered and
NOT estimated.** Dollars are **derived** at $0.0513/core-h and **reported-by-owner**. **No
`COST_CALIBRATION.md` row: nothing completed — no gate graded, no rung run, no compute under the
registration.**

### 29.11 `FZ1` — RUN IMMEDIATELY **AFTER** THIS COMMIT

`check_comparator_freeze.py` compares HEAD blobs against worktree blobs, so a pre-commit run would
read `PIN-DRIFT` on the row this amendment re-pins. **Its exit code is taken immediately after this
commit and recorded in §29.13**, alongside the check-1 diff artifact. **A forward reference, not a
claim.**

### 29.12 THE STANDING QUESTION — **ANYTHING ELSE BETWEEN THIS DOCUMENT AND A LAWFUL LAUNCH?**

🔴 **THE FIRST RESIDUAL OF EVERY PRIOR AMENDMENT IS NOW CLOSED: `X7`/`C12` NO LONGER HOLDS
`--controls` RED. `--controls` EXITS 0 WITH ALL 32 CONTROLS FIRED.** What remains:

1. 🔴 **NOTHING HAS EVER RUN IN THE REGISTERED RUN ROOT.** Every statement in Amendments 20–23
   about what the launch path *will* do is a statement about **code**, not about a run.
2. 🔴 **THE A-MAP STATION ORDERING IS UNRESOLVED** (§29.1). It does **not** block a launch — §16.4
   keeps it REPORTED, NOT GATED — but it **qualifies the deliverable**, and the disclosure now
   travels with the figure data so it cannot be lost between here and a plot.
3. ⚠ **THE CENSUS IS BOUNDED BY ITS OWN FOUR KEYS.** A defect of a mechanism outside M1–M4 would
   not have been found by it, and the stage drive is the empirical check on that.

⚠ **WHAT THIS LANE CANNOT SAY, AND DOES NOT.** It has never seen a real M6 `log.checkMesh` produced
by the registered driver in the registered run root. It did not re-derive the physics or the gates.
**Check 1 on this diff, check 4, the freeze, the stage drive and the launch are the supervisor's,
and this lane takes none of them.**

---

### 29.13 ADDENDUM, SAME SESSION — **`FZ1`'s EXIT CODE, THE CHECK-1 ARTIFACT, AND THE THREE CONDITIONS THE SUPERVISOR NAMED FOR THE DRIVE**

§29.11 forward-referenced this section. Run **immediately after commit `92a73349`**:

> **`FZ1` EXIT CODE `0`. `VERDICT: PASS`. `10 of 10 PIN-OK, 0 violating`** — the re-pinned
> comparator at its new sha, and the other nine **re-verified at this HEAD, not assumed**. The
> verifier's **NO-MARKERS** caveat is carried, not dropped (§23.7, item 41): what was tested is
> **identity and currency**, not a marker-dated freeze margin.

| | |
|---|---|
| path | **`cases/M6SR/AMENDMENT_23_D1_INDETERMINATE_C12_FIXTURE.diff`** |
| content | the **unmodified stdout** of `git --no-pager show 92a73349d49d7a0c57c001afa263cb68f5a2f405` |
| size | **37,982 bytes, 558 lines** |
| sha256 | `1b0fd67a43b8ff3b9b41ceb9a02005faf4d180aa4be5a2bb34b14bcae22ae0ce` |
| equality | **`cmp` against a freshly recomputed `git show`: BYTE-IDENTICAL** |
| the comparison itself | **PLANT-VERIFIED**: the same `cmp` against a copy with one line appended **DOES** report a difference (rule 3) |

**THE THREE CONDITIONS THE SUPERVISOR NAMED AS UNLOCKING THE DRIVE, EACH MEASURED:**

| # | condition | measured |
|---|---|---|
| 1 | the `C12` fixture repair and the `D1` disclosure land, pre-compute, with controls | ✅ commit `92a73349`; `--controls` **rc 0, all 32 fired**; `--selftest` **rc 0, all 30 mutation targets flipped red**, `C16` fired at rc 0/0 |
| 2 | `B4s`'s command line registered with its expected outcome | ✅ §29.4, two verbatim lines with expected exit codes |
| 3 | `FZ1` still exits 0 and the run root is still absent | ✅ **`FZ1` = 0**; **`verification/runs/M6SR_runs` ABSENT**, re-verified at this commit |

🔴 **THE DRIVE IS STILL NOT TAKEN.** All three conditions are met and **the confirmation is the
supervisor's alone.** The run root remains absent until he gives it. **This lane does not read
"what will unlock it" as "it is unlocked".**

---

## 30. AMENDMENT 24 — 2026-09-04, **PRE-COMPUTE, AND THE LAST ACT BEFORE THE WINDOW CLOSES**. 🔴 **THE REFINEMENT RATIO `r` WAS NEVER A FREE PARAMETER: A4 AND A6 ALREADY DETERMINED IT. `r = 2.000` IS *DERIVED*, NOT CHOSEN — AND `GCI_fine` IS *ALGEBRAICALLY INVARIANT* UNDER `r` ANYWAY, SO THE BAND IS SAFE TWICE OVER.** GATE G STOPS REFUSING **BECAUSE THE PARAMETER IT NAMED IS NOW REGISTERED** — THE ONLY LEGITIMATE WAY FOR A REFUSAL TO END.

**Written by a lane under the cfd supervisor's ruling, quoted where applied. It moves NO
threshold, NO cap and NO label; it REGISTERS A PARAMETER THAT TWO FROZEN CLAUSES ALREADY FORCED.
It does not freeze and it does not launch. `verification/runs/M6SR_runs` remains ABSENT.**

### 30.0 🔴 **HOW THIS AMENDMENT CAME TO EXIST: A CONFIRMED DRIVE WAS STOPPED**

**The supervisor had CONFIRMED the stage drive.** His confirmation carried one condition — *"as
your last act before launching, re-confirm that NOTHING is pending that would need a gate,
threshold, cap or label to move … If ANYTHING is pending, say so and do not start; that window
will not come back."*

**The re-check found `r`, and the lane did not start.** Gate G's own refusal text named it: *"NO
SECTION OF THE FROZEN REGISTRATION REGISTERS THE REFINEMENT RATIO r … Choosing one HERE would be
choosing a gate parameter AFTER the freeze."* **`r` is a gate parameter, it was unregistered, and
rule 2's window — which shuts on the first byte `B3c` writes — is the only place it could ever be
registered.** Had the drive proceeded, **Gate G would have refused for the life of the campaign,
Gate P would never have received a band, and `B6` — the step carrying Sanaa's named deliverable —
could never have produced a graded result.**

> **The supervisor's words on the stop:** *"You stopped a drive I had already confirmed, because my
> own instruction told you to check with the window closing. That was the right call and it saved
> the campaign's deliverable."* **It is recorded here because the check was HIS, and because a
> campaign that only records what it found is worth less than one that records what nearly went
> unfound.**

### 30.1 THE LAWFULNESS CONDITION — **PLANTED, NOT ASSERTED**

`find verification/runs -maxdepth 1 -name M6SR_runs | wc -l` → **0**; a probe at that exact path
→ **1**; after `rmdir` (which refuses a non-empty directory) → **0**. `test -e` **ABSENT**;
`git ls-files` **0 rows**. **NO COMPUTE HAS OCCURRED UNDER THIS REGISTRATION.**

---

### 30.2 🔴 **THE `r` AMBIGUITY TRAP — CLEARED FIRST, AND IT DID NOT RESOLVE THE WAY THE RULING ALLOWED FOR**

> **The supervisor's warning, verbatim:** *"THERE ARE TWO QUANTITIES CALLED `r` IN THIS DOCUMENT …
> ESTABLISH WHICH `r` LINE 425 MEANS BEFORE YOU WRITE ANYTHING. … DO NOT let one letter standing
> for two quantities carry a gate parameter — that is the same defect as `log.$tag` versus
> `log.pyhyp`, one level up and with a gate hanging on it."*

**MEASURED, at source, in full context:**

| line | the sentence | which `r` |
|---|---|---|
| **425** | *"`r = 1.167442` and `cells / wing_faces = 64` at **all three** levels **by construction**, so `r` cannot move."* — followed immediately by *"There is no parameter this registration varies **in the normal direction**"* | 🔴 **the pyHyp WALL-NORMAL GROWTH RATIO** |
| **1025** | *"the three levels share `s0 = 1.0e-4`, `N = 65` and `marchDist = 12.0` **identically**; therefore `r = 1.167442` … therefore **the wall-normal discretisation is IDENTICAL**"* | 🔴 **the same growth ratio** |

> 🔴 **BOTH LINES ARE ABOUT THE GROWTH RATIO. NEITHER IS ABOUT THE GRID REFINEMENT RATIO.** The
> ruling allowed for the other outcome — *"If it means the refinement ratio, the registration
> already says r cannot move and your amendment merely computes what it fixed"* — **and that is NOT
> what the document says. §425 IS NOT CITED AS SUPPORT ANYWHERE IN THIS AMENDMENT**, and the
> comparator's derivation record says so in terms. **The derivation below rests on A4 and A6
> ALONE.**

**THIS IS THE FIFTH FAULT'S FAMILY AGAIN** (§29.5): a reader that cannot distinguish its subject
from something adjacent to it — here, one letter standing for two physical quantities, **with a
gate parameter hanging on it.** It was caught because the supervisor named the trap before the
lane wrote a line.

---

### 30.3 **THE DERIVATION — `r = 2.000` EXACTLY, FORCED BY TWO ALREADY-FROZEN CLAUSES**

| frozen clause | what it fixes |
|---|---|
| **`A4`** | cell counts **99,840 : 399,360 : 1,597,440**, ratios **EXACTLY 4.000 on integers** |
| **`A6`** | **`cells / wing_faces == 64` EXACTLY**, at every level |

**Therefore the SURFACE FACE COUNTS are forced**, and they are checkable by hand:

| level | cells | ÷ 64 | surface faces |
|---|---|---|---|
| L3 | 99,840 | exact | **1,560** |
| L2 | 399,360 | exact | **6,240** |
| L1 | 1,597,440 | exact | **24,960** |

**Surface-face ratios 6,240 / 1,560 = 4 and 24,960 / 6,240 = 4, EXACTLY, on integers.**
**A SURFACE FACE COUNT IS TWO-DIMENSIONAL**, so a linear refinement `r` scales it by `r²`:

> 🔴 **`r = √4.000 = 2.000`, EXACTLY. DERIVED, NOT CHOSEN.**

**AND `24,960` IS THIS REGISTRATION'S OWN SURFACE** — it appears **21 times** in this document and
`build_m6sr_l1.sh` marches *"24,960 × 64"*.

⚠ **WHY NOT `1.5874 = 4^(1/3)`.** That is the right ratio for a **three**-dimensional refinement.
**`A6` holds the wall-normal direction at 64 layers at EVERY level, so this family refines TWO of
three directions BY CONSTRUCTION** — clause **`L-HONEST`** says exactly that, and it is why this
document calls itself a **SURFACE**-refinement study and registers its GCI as a surface-refinement
band and a **LOWER BOUND** on total. **The cube root would attribute to the mesh a refinement the
mesh does not have.**

> 🔴 **WHY THIS IS NOT RULE-2 FITTING.** **A value FORCED by two already-frozen clauses cannot have
> been selected to fit an answer: it was fixed the moment `A4` and `A6` were frozen, and any reader
> could have computed it then. WHAT WAS MISSING WAS THE DERIVATION, NOT THE FREEDOM.**

**IT IS COMPUTED, NOT STORED.** `refinement_ratio_from_registered_counts()` derives `r` from
`A4_CELLS`, `A4_RATIO_EXACT` and `A6_CELLS_PER_WING_FACE` **at call time**. Storing `2.0` as a
literal would be **item 50's defect one document up** — a number that agrees with its basis until
somebody changes the basis. It **REFUSES** as an `InternalDefect` if a cell count is not divisible
by 64, or if the surface ratios are not exactly `A4_RATIO_EXACT`: **this comparator will not take a
square root of an approximate ratio.**

---

### 30.4 **THE SECOND PROTECTION — `GCI_fine` IS ALGEBRAICALLY INVARIANT UNDER `r`**

Registered as a **FACT**, separately from the derivation, because **it protects a different thing**.

`p_s` is **DEFINED** as `ln(d32/d21) / ln(r)`. Therefore `r**p_s ≡ d32/d21` **for any `r`**, and
`r` **CANCELS** from `GCI = Fs·|d21/f1| / (r**p_s − 1)`.

**MEASURED, on one CONVERGING triple (0.0300 / 0.0280 / 0.0272), across five candidate ratios:**

| `r` | 1.10 | 1.5874 | 2.000 | 4.000 | 7.77 |
|---|---|---|---|---|---|
| `p_s` | 9.613776 | 1.982895 | 1.321928 | 0.660964 | 0.446912 |
| `GCI_fine` | **0.02450980392156884** | ← | ← | ← | ← |

**ONE distinct value, BIT-IDENTICAL, while `p_s` spans a factor of 21.5116.** **THE HAND CHECK,
computed from `d32/d21` WITHOUT going through `r` at all:** `r**p_s = 2.499999999999991 = d32/d21`
exactly, and `1.25·|0.0008…/0.0272| / (2.5 − 1) = 0.02450980392156884` — **matching to the last
bit.**

> 🔴 **SO THE BAND IS SAFE TWICE OVER: once because `r` is DERIVED rather than chosen, and again
> because the quantity Gate P's band consumes DOES NOT DEPEND ON `r` AT ALL. If the derivation were
> ever disputed, the band still stands on the identity.**

---

### 30.5 **WHAT CHANGES IN THE COMPARATOR — AND WHAT EXPRESSLY DOES NOT**

Gate G's refusal is **STRUCK BY QUOTE in the file itself**, with the full text preserved. **IT WAS
FORMALLY CORRECT AND IT IS NOT WEAKENED.**

> **RULED (supervisor, verbatim):** *"I am not weakening Gate G. Its refusal was FORMALLY CORRECT
> and I am not touching it — the refusal disappears because the parameter becomes registered, which
> is the only legitimate way for a refusal to stop firing."*

**Gate G now returns `GATE REACHED` on a `CONVERGING` triple at the registered `r`**, with
`G3_G4_registered_ratio` (the full derivation record) and
`G3_G4_roache_triple_at_registered_r` beside it. **`G3_G4_all_candidate_ratios` is KEPT**, so every
reader still sees all five. **MEASURED on a forced-`G1`/`G2` probe: `GATE REACHED`, `CONVERGING`,
`p_s = 1.321928095`, `GCI_fine = 0.02450980392156884`.**

**AND `r = 2` BUYS SOMETHING BEYOND THE BAND:** with `r` fixed, `p_s = log₂(d32/d21)` is a genuine
**observed order of convergence** rather than an artifact of an arbitrary ratio — **so `G3` grades
something meaningful instead of refusing forever.**

**EXPRESSLY NOT DONE:** no threshold moves; `G4_FS` stays 1.25; `G3`'s `p_s` is not retired; standing
rule 5's ordering is untouched; and items **25, 27, 8 and 6 are not touched**.

---

### 30.6 THE CONTROLS — **`C32` AND `C33`, EACH A DELTA**

| control | the plant | **how it dies** |
|---|---|---|
| **`C32`** | **the BASIS is mutated**, not the value: `A4_RATIO_EXACT` set to 9 and the cell counts to match | the derived `r` **MOVED to 3.0** — so the value is **computed from the basis, not stored**. Clean twin: `r = 2.0` with faces `[1560, 6240, 24960]` and ratios `[4, 4]`. **Negative twin:** a cell count not divisible by 64 **REFUSES as an `InternalDefect`** rather than rounding — `A6` is an EXACT clause. The basis is restored and `r` reads 2.0 again |
| **`C33`** | five candidate ratios spanning 1.10 → 7.77 | **one bit-identical `GCI_fine`** while `p_s` spans **21.5116×**, plus **the hand check** computed from `d32/d21` without `r`, matching to the last bit |

**`refinement_ratio_from_registered_counts` is added to `C23`'s `must_reach`**, so orphaning the
derivation cannot silently restore Gate G's refusal.

**MEASURED: `--controls` → rc 0, ALL 34 CONTROLS FIRED, under `python3` and `python3 -O`, stdout
BYTE-IDENTICAL (12,402 bytes) and stderr byte-identical. `ast.Assert` = 0 with the detector planted
and SEEN.**

---

### 30.7 SANAA'S DESK — **A DISCLOSURE, NOT A REQUEST**

> **The supervisor's words, recorded as his:** *"deriving a value that two frozen clauses already
> determine is not setting a gate threshold and not retiring one, so it is mine. If she disagrees,
> THE DERIVATION IS THE THING TO DISPUTE — and the invariance means her answer cannot change the
> band either way. I would rather she saw it stated plainly than discovered it in a figure
> caption."*

**SUBMISSIONS REMAIN PARKED. Nothing is sent. This is a record on the desk, not a message off the
box.**

### 30.8 WHAT THIS AMENDMENT DOES **NOT** DO

1. **It moves NO threshold, NO cap and NO label.** It registers a parameter two frozen clauses
   already forced.
2. **It does not weaken Gate G**, retire `G3`'s `p_s`, or touch items 25, 27, 8 or 6.
3. **It does not cite line 425**, whose `r` is the wall-normal growth ratio (§30.2).
4. **It does not freeze, does not launch, and has not driven the stage.**
5. **SUBMISSIONS REMAIN PARKED.**

### 30.9 RULE 6's AMENDMENT ASSERTIONS

- **Appended at the foot. Lines whose number changed above this section: 0**, verified by
  byte-comparing the prefix against HEAD's blob.
- **Version bump: v1.23 → v1.24** (Amendment 24).
- **The unchanged-prefix sha of this file at `86033e48`** is
  **`93b2c88cc273382c362319e4bbb9b00c2f487fc85de34058b528ec8cbed37c14`**, re-derived **inside the
  commit invocation** with the commit aborting if it had moved.

### 30.10 🔴 **THE RE-PIN — ONE PINNED EXECUTABLE MOVED, THE LIVE ROW ENUMERATED BY SEARCH**

**The comparator is the only executable this amendment edits.** The live row carrying the
superseded blob was **ENUMERATED BY SEARCH, NOT ASSUMED** — this campaign has three times found
more rows than a reader would have expected (§25.13, §27.11) — and the search returns **exactly
one**, reported as a **measurement, not a relief**. Struck, rule 6, by verbatim quote,
machine-verified character for character against the line it strikes:

> 🔴 **STRUCK BY QUOTE** *(§29.9's row — the pin that was IN FORCE)*: ~~*"| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`6a59443ee053db22cd829f1fb7200dd46cdb413d`** | `f323ad42bb9f2b8e845ab789af5bb76644cbf8eff5516d97b78a0056a2bc5aec` | **3730** | **§9 registered** — **RE-PINNED HERE** |"*~~

**THE NEW STANDING PIN**, derived with `git hash-object` and **RE-DERIVED INSIDE THE SAME SHELL
INVOCATION AS THE COMMIT THAT CARRIES THIS SECTION, WITH THE COMMIT ABORTING IF IT HAD MOVED**:

| path | git blob sha | sha256 of the file | lines | §9 status |
|---|---|---|---|---|
| **`cases/M6SR/analyse_m6sr.py`** (comparator) | **`e4f991c05990bb52ce30e793f29d1a1927d2b428`** | `44a1d342e11f99f7c3cbb3a4bee837443f39281757ad796190b7b061986ce22e` | **3925** | **§9 registered** — **RE-PINNED HERE** |

⚠ **THE OTHER NINE PINS ARE UNMOVED AND ARE RE-VERIFIED AT THIS HEAD, NOT ASSUMED** — §30.12.

### 30.11 COST — RULE 12

| activity | wall s | ranks | **core-min (MEASURED)** |
|---|---|---|---|
| the `r` derivation from the frozen constants, the `GCI_fine` invariance across five ratios, and the by-hand algebra check | 12 | 1 | **0.2000** |
| `--controls` under `python3` and `python3 -O`; the Gate G branch probes | 19 | 1 | **0.3167** |
| `--selftest` (controls + `C16` + the mutation loop over 32 targets) | 177 | 1 | **2.9500** |
| **TOTAL** | 208 | 1 | **3.4667** |

**All MEASURED from the clock; one run of each activity, development re-runs NOT metered and NOT
estimated.** Dollars are **derived** at $0.0513/core-h and **reported-by-owner**. **No
`COST_CALIBRATION.md` row: nothing completed, and no compute has occurred under the registration.**

### 30.12 `FZ1` — RUN IMMEDIATELY **AFTER** THIS COMMIT

`check_comparator_freeze.py` compares HEAD blobs against worktree blobs, so a pre-commit run would
read `PIN-DRIFT` on the row this amendment re-pins. **Its exit code is taken immediately after the
commit and recorded in §30.13.** A forward reference, not a claim.
