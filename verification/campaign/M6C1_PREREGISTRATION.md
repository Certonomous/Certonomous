# M6C1 — ONERA M6, source-faithful blunt-trailing-edge C-grid: MESH + MARCH rung — PRE-REGISTRATION

> ## 🔴 DRAFT — UNFROZEN. NO COMPUTE HAS RUN UNDER THIS DOCUMENT. NOT A GATE YET.
>
> **HOW TO STRIKE THIS BANNER AT FREEZE:** delete the whole blockquote from the line
> `> ## 🔴 DRAFT` down to and including the line `> — END DRAFT BANNER —`, and nothing
> else. It is one contiguous block, it is the only blockquote before §0, and no other
> text in this file depends on it. *A stale DRAFT banner left on a frozen document has
> already caused a problem in this lab twice in one evening —
> `MRF_R1_PREREGISTRATION.md` Amendment 2 and `M6CP1_PREREGISTRATION.md` Amendment 1
> §A1.1 both exist to strike a banner that had become false. This banner is written to
> be deleted in one cut so that it is never the thing that is forgotten.*
>
> Authored by a cfd `lab-lane`. **The FREEZE (sha) and the graded launch are the
> cfd-supervisor's `SUPERVISION_CHARTER` §3 check-4, personal and undelegated. The
> grader diff-read is the supervisor's check-1.** Neither has been done. Until the
> freeze commit every gate, threshold, band, cap and label below is amendable and
> carries no evidentiary weight (CLAUDE.md rule 2). Nothing here is graded and no
> number below §2 is a result.
>
> — END DRAFT BANNER —

- **Case family:** ONERA M6 transonic half-wing. **Successor to `M6CP1`**, which is
  parked `NOT A RESULT` (`M6CP1_PREREGISTRATION.md` Amendment 2 §A2.1).
- **Prose:** `docs/campaigns/ONERA-M6/M6_PHYSICS_AND_GEOMETRY_STATUS_2026-09-10.md`
- **Inputs / builder / grader:** `cases/ONERA_M6_C1/` (does not exist yet)
- **Outputs (none yet, and this is the rule-2 pre-compute condition):**
  `verification/runs/M6C1_runs/` — **this directory does not exist on disk at the time
  of writing.** That is the checkable statement rule 2 requires: the condition is "no
  run directory", and it was checked by `ls`, not asserted.
- **Authority for the mesh route:** Sanaa, 2026-09-10, verbatim: *"sound sgood then
  onera M6 can get the c mesh and snappy hex or whatever it needs"*, relayed by the
  cfd-supervisor. Read as: the route is the team's to choose **and to defend from the
  source**. §3 below is that defence.

---

## 0. THE ONE-SENTENCE REASON THIS RUNG EXISTS, AND IT IS AN UNCOMFORTABLE ONE

**M6CP1 did not fail at a wing with a difficult trailing edge. It failed at a wing
whose trailing edge the lab had already digitised, correctly, into a file in this
repository — and then did not build.**

`models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` has been on disk with
72 rows, and its last row reads:

```
1.0000000  0.0007052
```

The ONERA M6 reference section **does not close to a point**. It closes to a finite
half-thickness of `z/l = 0.0007052` at `x/l = 1.0`. M6CP1 built a trailing edge that
closes to a single point with **zero cells across it** and a cusp half-angle of
**60.9°, scale-invariant across three levels**. **That is an unregistered departure
from the reference geometry, not a meshing infelicity**, and it is the whole content
of this rung's §3.

---

## 1. THE SOURCE, TITLE-PAGE VERIFIED (rule 15)

**`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`**

Verified by rendering and reading the document's own title page with `pdftotext`,
**independently of the `.txt` sidecar and independently of the filename** (rule 15
forbids verification by filename, file type or hash):

| field | as printed on the document | filename claims | match |
|---|---|---|---|
| issuing body | NORTH ATLANTIC TREATY ORGANIZATION / ADVISORY GROUP FOR AEROSPACE RESEARCH AND DEVELOPMENT | `agard` | ✅ |
| report number | **AGARD Advisory Report No. 138** | `1979_ar138` | ✅ |
| title | **EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT** — Report of the Fluid Dynamics Panel Working Group 04 | `experimental_data_base` | ✅ |
| published | **May 1979**, ISBN 92-835-1323-1 | `1979` | ✅ |

**The M6 chapter is present and is the expected one.** Appendix B, test case **B1**:
*"PRESSURE DISTRIBUTIONS ON THE ONERA-M6-WING AT TRANSONIC MACH NUMBERS", by V. Schmitt
and F. Charpin*, ONERA, 92320 Châtillon, France (contents page; chapter body from PDF
page 327). This **is** the Schmitt & Charpin 1979 M6 reference.

### 1.1 🔴 A DEFECT IN THE LAB'S COPY, DISCLOSED BECAUSE A GATE WAS BUILT ON IT

**The PDF is a 1979 paper scan run through Acrobat Paper Capture in 2007. The prose
OCR'd; the NUMERIC TABLES DID NOT.** Table B1-1 (section coordinates) and Tables
B1-2 onward (the surface Cp distributions, tests 2308–2583) survive in the sidecar as
their captions only — the digits are page images.

- **Consequence, stated plainly: there is no machine-readable AGARD Cp dataset in this
  repository.** `git ls-files` for AGARD/M6 reference data returns the section
  coordinates and two verification scripts, and **no Cp table**.
- **M6CP1's Gate P — "surface Cp against AGARD AR-138 at seven span stations, band
  ±0.02 in Cp" (`M6CP1_PREREGISTRATION.md:184-186`) — could not have been graded from
  the lab's holdings.** This is recorded here as a finding about the lab's evidence
  base. It is not a criticism of M6CP1's authors and it changes nothing about M6CP1's
  parked verdict, which rests on other grounds.
- **Therefore M6C1 does not register a Cp gate.** §5 gates the mesh and the march;
  the physics is **REPORTED, NOT GATED**, and §5.3 names digitisation as the
  precondition for a physics gate in a successor.
- The pages are legible and renderable — Table B1-1 is PDF page 333 (printed B1-7) —
  so digitisation is **feasible work, not a blocker**. It is simply not done, and this
  document will not pretend otherwise.

### 1.2 WHAT IS **NOT** ON DISK — stated so nobody looks for it twice

- **No NASA Turbulence Modeling Resource (turbmodels.larc.nasa.gov) M6 grid
  description.** `/home/ubuntu/paper-incoming/.../Links/ONERA_M6_TMR_test_case.url` and
  `ONERA_M6_NASA_validation.url` are **URL stubs**, outside the repository, with no PDF
  behind them. **NOT OBTAINED.** No content from TMR is used, quoted or paraphrased
  anywhere in this document.
- **No AIAA M6 grid-convergence or validation paper.** **NOT OBTAINED.**
- Nothing was fetched from outside this box, and nothing will be (rule 8).

**Consequence for §3:** the mesh class below is derived from **the geometry the source
defines**, not from any CFD topology paper — because the lab holds no such paper. That
is a weaker provenance than a grid paper would give and it is labelled as such.

---

## 2. THE MESH CLASS, QUOTED FROM THE SOURCE

### 2.1 What AR-138 B1 states about the model (§1.2 of the chapter, PDF pages 327–329)

| item | source text | value |
|---|---|---|
| model type | "semi-span wing" | half model, no body |
| planform | "swept back" | — |
| aspect ratio | §2.1.2 | **3.8** |
| leading-edge sweep | §2.1.3 | **30°** |
| trailing-edge sweep | §2.1.4 | **15.8°** |
| taper ratio | §2.1.5 | **0.562** |
| twist | §2.1.6 | **"without twist"** |
| mean aerodynamic chord | §2.1.7 | **c̄ = 0.64607 m** |
| semispan | §2.1.8 | **b = 1.1963 m** |
| airfoil sections defining the wing | §2.1.9 | **1** |
| section | §2.1.10 | **"section coordinates of the symmetrical profile (design values): see table B1-1. The section is ONERA D"**, normal to the generator at 40.18 % of chord |
| lofting | §2.1.11 | **"conical generation"** |
| wing tip | §2.1.13 | **"truncation parallel to wing root and addition of a half body of revolution"** |
| fabrication tolerance | §2.3 | **0.15 mm** |
| tunnel | §3.1 | ONERA S2MA, Modane |
| test conditions | §1.1 | M = 0.7, 0.84, 0.88, 0.92; α up to 6°; **Re ≈ 12 × 10⁶** |

**Root chord is DERIVED, not quoted:** from c̄ = 0.64607 m and λ = 0.562 via
c̄ = (2/3)c_r(1+λ+λ²)/(1+λ), **c_r = 0.8059 m**, hence **c_t = 0.4529 m**. Labelled
derived because the source states c̄ and λ, not c_r.

### 2.2 🔴 THE TRAILING EDGE — THE WHOLE POINT OF THE EXERCISE

**Table B1-1, page B1-7 (PDF page 333), read from the rendered page image and
independently confirmed against the lab's own digitisation** in
`models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` (72 rows; the two
agree at every digit of the last four rows):

```
x/l          z/l
0.9952080    0.0012985
0.9978030    0.0009773
1.0000000    0.0007052     <-- the trailing edge
```

**THE ONERA M6 REFERENCE TRAILING EDGE IS BLUNT.** The section is symmetric (§2.1.10,
"the symmetrical profile"), so `z/l` is a half-thickness and:

| quantity | value | basis |
|---|---|---|
| TE half-thickness | `z/l = 7.052e-4` | Table B1-1, last row, source |
| **TE total thickness** | **`t_TE/c = 1.4104e-3` = 0.141 % of local chord** | 2 × above |
| TE thickness at root (c = 0.8059 m) | **1.137 mm** | derived |
| TE thickness at tip (c = 0.4529 m) | **0.639 mm** | derived |
| fabrication tolerance | 0.15 mm | source §2.3 |
| **TE thickness / tolerance, at root** | **7.6×** | derived |
| surface slope at TE, per surface | **7.39°** | `atan((0.0007052−0.0009773)/(1.0−0.9978030))` |
| **included wedge angle at TE** | **14.8°** | 2 × above |

**The 7.6× line is load-bearing.** A blunt TE 7.6 times the model's own build tolerance
is a **design feature**, not scan noise and not a digitisation artifact. The lofting is
**conical** (§2.1.11) between one section, so `t_TE/c = 0.141 %` holds at **every**
spanwise station — the TE is blunt from root to tip.

**And the contrast with what M6CP1 built is total:**

| | AR-138 source geometry | M6CP1 as built |
|---|---|---|
| TE thickness | 0.141 % c (1.14 mm at root) | **0** — closes to a single point |
| cells across TE | (a real thickness to mesh) | **0** |
| included angle at TE | **14.8°** | **121.8°** (cusp half-angle 60.9°) |
| behaviour under refinement | — | **scale-invariant across three levels** |

### 2.3 THE MESH CLASS THIS IMPLIES, AND THE ROUTE REGISTERED

**A blunt trailing edge with a 0.141 %-chord base is served by a C-grid with a wake
cut** — the C wraps the leading edge, runs aft along both surfaces, turns around the
**finite** base, and the two branches leave the base as a wake cut carried downstream.
That topology exists *because* the body has a base to wrap. An O-grid closes the
section and is wrong for a wake; an H-grid puts a singular line at the TE and is
exactly the failure M6CP1 suffered.

**HONEST LIMIT ON THIS CLAIM.** AR-138 is an **experiment** report. It specifies **no
CFD grid**, and the lab holds **no** M6 grid paper (§1.2). So "C-grid with a wake cut"
is **this lane's inference from the geometry the source defines**, not a topology
quoted from a validation source. It is labelled `[INFERRED]` wherever it is relied on.
What is **quoted from the source** is the geometry: blunt TE, 0.141 % c, conical loft,
symmetric ONERA D section, values in §2.1–§2.2 above.

**REGISTERED ROUTE — `snappyHexMesh` onto a source-faithful blunt-TE STL, with a
C-shaped refinement wake region.** Chosen over a `blockMesh` C-grid on one ground
that is not aesthetic: **it is the route this lab can build three levels of tonight.**
`snappyHexMesh` is in service in this lab this evening (the MRF R1 build); a
hand-written multi-block C-grid generator for a swept tapered wing is not, and a
defensible mesh we can generate beats an ideal one we cannot. Sanaa's words name
`snappyHexMesh` explicitly.

**🔴 THE `nCellsBetweenLevels` TRAP, REGISTERED BEFORE IT BITES.** Tonight's MRF R1
build measured that `nCellsBetweenLevels` is a buffer counted **in cells, not in
physical thickness**, so a background block scaled by exactly 1.5 delivered ratios of
**1.4157 / 1.4264** against a registered 1.5 — which would have made `roache_triple`
refuse the family **after the compute was spent**. Therefore M6C1 registers the
**delivered** ratio, not the nominal one: §4's `r` is **verified from the built cell
counts before the freeze**, and if the delivered ratios are unequal the family is
registered on the **unequal-r path (`form="auto"`)** deliberately. **No nominal ratio
is registered and hoped for.**

---

## 3. GEOMETRY — ADMITTED ON THE SOURCE, WITH ONE REGISTERED DEPARTURE

**Built from `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`**, all 72
rows, symmetric about z = 0, conically lofted root→tip, LE sweep 30°, semispan
1.1963 m, root chord 0.8059 m, tip truncated parallel to the root per §2.1.13.

**REGISTERED DEPARTURE 1 — the tip half-body of revolution is replaced by a flat
truncation.** Source §2.1.13 specifies "truncation parallel to wing root **and addition
of a half body of revolution**". M6C1 builds the truncation and **omits the half body
of revolution**. Disclosed, not hidden. Basis: the tip cap affects the tip vortex and
the outermost span station; the gates in §5 are a mesh gate and a march gate, neither
of which reads the tip. **A successor that gates on Cp at y/b = 0.99 must build the tip
body**, and this departure is inherited by nothing.

**NO DEPARTURE AT THE TRAILING EDGE.** The blunt TE is built at its source thickness,
0.141 % of local chord. This is the point of the rung.

---

## 4. THE FAMILY — THREE LEVELS, RATIO DELIVERED NOT NOMINAL

| level | target cells | nominal ratio to next |
|---|---|---|
| **L1** (coarse) | 0.90 M | — |
| **L2** (medium) | 3.04 M | 3.375× cells ⇒ r = 1.5 per direction |
| **L3** (fine) | 10.25 M | 3.375× cells ⇒ r = 1.5 per direction |

Sizing anchored on a **measured lab precedent**, not on a rate guess: the
heat-transfer **T26** 3-D rung ran **885 k / 2.99 M / 10.09 M** cells (commit
`f386be2fb`), which is the same family shape at the same scale on this box.

**`r` IS NOT REGISTERED AS 1.5.** Per §2.3, the delivered per-direction ratio is
computed from the **built** cell counts at each level, before the freeze, as
`r_ij = (N_i/N_j)^(1/3)`, and **whichever ratios are delivered are what the freeze
records**. If they are equal to within 2 % the equal-ratio Roache path is registered;
otherwise the unequal-ratio path (`form="auto"`) is registered. This clause exists
because of the MRF measurement in §2.3 and it is not optional.

---

## 5. THE GATES

### 5.1 🔴 GATE M — MESH ADMISSION. FOUR LIMBS. ALL FOUR, AT ALL THREE LEVELS.

> **Gate M is `PASS` iff every one of M-a, M-b, M-c, M-d holds at L1, L2 and L3.
> Any single limb failing at any level ⇒ `GATE FAIL`, and no solver is launched.**

#### M-a. `checkMesh` IS INVOKED WITH `-allGeometry -allTopology`, AND rc IS NOT THE VERDICT

**Registered invocation, exactly:**
```
checkMesh -allGeometry -allTopology -case <level>
```
**Registered verdict rule: the mesh passes M-a iff the output contains
`Failed 0 mesh checks` — equivalently, contains no line beginning `***` — AND the
string `Mesh OK.` is NOT relied upon AND `rc` is NOT relied upon.**

**This limb is not a precaution. It is a MEASURED finding from tonight, taken on the
SUBOFF R1b family, which is the sibling case in this same brief:**

| SUBOFF R1b level | plain `checkMesh` | plain rc | `-allGeometry -allTopology` | full-set rc |
|---|---|---|---|---|
| coarse (39,904) | **`Mesh OK.`** | **0** | **`Failed 1 mesh checks`** — 1,531 cells with small determinant | **0** |
| medium (89,784) | **`Mesh OK.`** | **0** | **`Failed 2 mesh checks`** — 3,240 small-determinant cells + 1 small-volume-ratio face | **0** |
| fine (202,014) | **`Mesh OK.`** | **0** | **`Failed 2 mesh checks`** — 7,125 small-determinant cells + 1 small-volume-ratio face | **0** |

**Two things are established by that table and both are load-bearing:**
1. **Plain `checkMesh` prints `Mesh OK.` on meshes the full check set fails**, at all
   three levels.
2. **`checkMesh` returns rc = 0 EVEN WHEN CHECKS FAIL.** The full-set run reports
   `Failed 2 mesh checks` and exits **0**.

**So a verdict of the form `("Mesh OK." in out) and rc == 0` is a substring test that
passes a failing mesh.** `grep -rn "allGeometry\|allTopology" scripts/` returned **zero
hits lab-wide** before this document. Every M6C1 mesh check reads the `Failed N mesh
checks` line and refuses on `N > 0`.

#### M-b. 🔴 THE GEOMETRY LIMB A CUSP CANNOT PASS

`checkMesh` clears M6CP1's collapsed trailing edge under **both** check sets. So
`checkMesh` — at any flag setting — cannot be the limb that refuses the mesh that
killed this case. **M-b is that limb.** Two independent registered numbers:

**M-b-1 — MINIMUM CELLS ACROSS EVERY NAMED GEOMETRIC FEATURE.**

| feature | registered floor, at L1 | how measured |
|---|---|---|
| **trailing edge**, at **every** spanwise station sampled at 20 equally spaced y/b in [0.05, 0.95] | **≥ 8 cells across the TE base thickness** | count of wall-adjacent cells spanning the base face between the upper and lower surface TE points, from the built `polyMesh` |
| leading edge, same stations | ≥ 12 cells around the LE radius | same |

**and the count is NON-DECREASING with refinement** (L2 ≥ L1, L3 ≥ L2). A family whose
feature resolution is flat under refinement is refused — **that flatness is precisely
the M6CP1 signature** (cusp half-angle 60.9° at all three levels).

**Why 8, and it is not a round number picked for comfort.** The TE base is
1.4104e-3 c. Eight cells across it is a TE cell of 1.76e-4 c, which at the root chord
of 0.8059 m is **1.42e-4 m** — *comparable to the first-cell height M6CP1 already
used and paid for*, `y1 = 2.4271e-04 m` (`M6CP1_PREREGISTRATION.md:556`). So 8 cells
across the base is **not a new order of cost**; it is roughly the wall spacing the case
was already buying, turned through 90°. Below 8 a blunt-base recirculation cannot be
represented at all: two shear layers plus a core needs 3 minimum, and 8 is the smallest
count that leaves any interior once the two near-wall cells on each side are spent.
**8 is a floor, not a target.**

**M-b-2 — WALL-FACE-AREA-RATIO CEILING.**

> **On every wall patch, at every level: `max(face area) / min(face area) ≤ 500`.**

Basis, from measurements, with its weakness stated:

| case | wall patch | measured ratio | health |
|---|---|---|---|
| **M6CP1** wing | `wing` | **7,212 : 1** | the case that died |
| SUBOFF R1b coarse | `hull` | 16.3 : 1 | ran and settled |
| SUBOFF R1b medium | `hull` | 17.2 : 1 | — |
| SUBOFF R1b fine | `hull` | 18.6 : 1 | — |

**500 sits an order of magnitude below the measured failure and more than an order of
magnitude above every healthy measured value in this lab.** **Its weakness, stated:**
the SUBOFF hull is an axisymmetric **wedge**, one cell wide in azimuth, so its
face-area ratio is not a fair comparator for a 3-D swept wing, where spanwise stretching
alone will exceed it. 500 is therefore anchored **firmly** on the failure side (7,212)
and **loosely** on the healthy side. It is registered as a **ceiling that M6CP1 fails by
14×** — which is the property that matters — and a successor with 3-D healthy-case data
may tighten it. **It will not be loosened after the run.**

#### M-c. DIMENSIONALITY — READ FROM THE `geometric` LINE, EXPLICITLY

> **Registered: the mesh passes M-c iff `checkMesh` output contains
> `Mesh has 3 geometric (non-empty/wedge) directions`.**

**The `solution (non-empty)` line is REGISTERED AS NOT THE TEST**, and here is why, in
one measurement taken on the SUBOFF wedge tonight — four lines apart in the same
output:

```
Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)
Mesh has 3 solution (non-empty) directions (1 1 1)
```

**A dimensionality check that reads the second line certifies an axisymmetric wedge as
3-D.** Any M6C1 instrument reading `solution (non-empty)` for this purpose is a defect.

#### M-d. THE STANDARD QUALITY GATES

Per `docs/standards/MESH_STANDARD.md` §3: max non-orthogonality **≤ 70°**, max skewness
**≤ 4**. Max aspect ratio and whole-mesh cell-volume ratio are **recorded** in each
level's `birth_certificate.json`, not gated. **Aspect ratio is recorded and not gated
deliberately**: the SUBOFF family carries a max aspect ratio of **236.15 at all three
levels — identical to seven significant figures** — which is informative about
scale-invariance but is not by itself a refusal criterion.

### 5.2 🔴 GATE T — THE MARCH. THE DIRECT FALSIFIER OF THE M6CP1 MECHANISM.

> **Gate T is `PASS` iff, at `endTime`, the minimum flow time scale over the domain
> is `> 1.0e-06 s` at every write, at every level, AND the solve reaches `endTime`
> under the rule-4 completion rule. Otherwise `GATE FAIL`.**

M6CP1 died when its LTS time-scale field collapsed to **1e-16 s** over 400 steps,
from a healthy 1.486e-07 s at t = 1 (`M6CP1_PREREGISTRATION.md` §A2.3). The threshold
`1e-06 s` is taken from that document's own registered falsifier F1
(`M6CP1_PREREGISTRATION.md:815`: *"stays above 1e-06 s"*), so the two rungs are
comparable on one number. **Gate T is the whole question this rung asks of the
physics: can a source-faithful mesh march at all, where the cusped mesh could not.**

### 5.3 PHYSICS — REPORTED, EXPLICITLY NOT GATED

At `endTime`, at M∞ = 0.8395, α = 3.06°, Re(c̄) = 11.72e6, the following are computed
and written into the results record, and **none of them is a gate**:

- **pressure** and **viscous** lift and drag coefficients, **separately** — see §6.1;
- surface Cp at the seven AR-138 span stations y/b = 0.20, 0.44, 0.65, 0.80, 0.90,
  0.96, 0.99, written as a table.

**Why not gated: §1.1.** There is no machine-readable AGARD Cp dataset in this
repository, so a Cp band would be graded against nothing. **A physics gate is
registered in a successor (M6C2) once Tables B1-2 onward are digitised from the page
images**, which is feasible work on a legible scan and is named here as that rung's
precondition. **This document does not register a physics band it cannot grade, and it
does not inherit one.**

**🔴 AND IT DOES NOT INHERIT M6CP1's `[0.15, 0.45]` PRESSURE-Cl BAND, FOR A REASON.**
That band is quoted twice in `M6CP1_PREREGISTRATION.md`, at lines **554 and 805**, both
times as *"this registration's own band"*. **Both occurrences are inside Amendment 2,
which is post-compute.** Searching that document for `0.45`, `Cl_p`, `pressure lift`
and `lift coefficient` returns those two lines and nothing else: **this lane could not
locate a pre-compute registration of that band anywhere in the document.** It is not
in §5 GATES. Under rule 2 a band whose freeze cannot be verified is not a band, so
**M6C1 neither inherits it nor re-states it as authority.** The +0.1915 figure is used
in this lab's records as *evidence about M6CP1*, which is legitimate and is what
`docs/campaigns/ONERA-M6/M6_PHYSICS_AND_GEOMETRY_STATUS_2026-09-10.md` does with it.
**This is referred to the cfd-supervisor as a finding about M6CP1, not ruled on here.**

---

## 6. CLOSURE AND NUMERICS

- **Solver: `rhoSimpleFoam`** (steady compressible), **not** `rhoPimpleFoam` + LTS.
- **Turbulence: `kOmegaSST`**, wall treatment **`nutUSpaldingWallFunction`** (all-y⁺),
  as M6CP1 used and as `M6CP1_PREREGISTRATION.md:557` records admissible.
- **CLASS-DEFAULT DEPARTURE, WITH ITS MEASURED COUNTER-EXAMPLE.** The transonic class
  default in this lab has been `rhoPimpleFoam` with **LTS**. M6C1 departs from it. The
  counter-example is **measured, in this family, and is not an argument from taste**:
  M6CP1's LTS field collapsed nine decades over 400 steps
  (1.486e-07 s → 8.584e-13 s on the N1 rung, and to 1e-16 s), producing cell velocities
  of **5.1e10 m/s**, and `M6CP1_PREREGISTRATION.md` §4.4 registered that LTS owed a
  time-step-independence demonstration which **was never paid**. A pseudo-transient
  whose time-scale field is unbounded below is not a defensible march when a steady
  solver is available. **If `rhoSimpleFoam` will not march this case either, that is
  itself the finding**, and Gate T is what reports it.

---

## 7. COMPLETION RULE (rule 4)

A level is complete iff **all** hold — the comparator **refuses (exit 2) rather than
degrade**:

1. `rc = 0`;
2. an `End` line in the solver log;
3. last time `== endTime`;
4. fields present at `endTime`: **`p U T k omega nut alphat rho phi`** — the
   **compressible** set. The thermal family's `T U p_rgh alphat nut k omega phi` list
   **does not apply and is not assumed**; this set is enumerated from what
   `rhoSimpleFoam` writes and is checked against the built case, not recalled.
5. `ExecutionTime` count `== round(endTime/deltaT)`;
6. **the age guard** — every field at `endTime` strictly newer than the case's own
   `0/T`. A guard refuses a case where `0/` or a time directory already exists.

**🔴 A DISCLOSED WEAKNESS IN LIMB 6, INHERITED FROM A FINDING MADE TONIGHT.** Commit
`0bdf38639` (cfd, F25) established that **the age guard cannot distinguish a
solver-written field from a post-processor-written one**. M6C1 does not repair that;
it records that **no post-processing may write into a graded level's time directories**,
and the grading path in §9 runs on a **copy**, never in place.

---

## 8. MONITOR STOPS — ONE REGISTERED ACTION EACH, AND NO ACTION TWICE ON THE SAME STATE

| # | monitored state | detection | **the one registered action** |
|---|---|---|---|
| S1 | minimum flow time scale `< 1e-06 s` at any write | per-write field minimum | **STOP the level. Record `GATE FAIL` on Gate T.** Do not restart, do not relax. This is the M6CP1 mechanism recurring and it is the answer, not an obstacle. |
| S2 | max `mag(U)` `> 5 × U∞` anywhere | per-write field maximum | **STOP the level; preserve the time directory; report as a crash finding for supervisor triage** (crash triage is check-2, undelegated). |
| S3 | any residual rises monotonically over 500 consecutive iterations | `solverInfo` | **STOP the level.** Record. Do **not** re-run with a smaller relaxation — that is the second action on the same state and is forbidden here. |
| S4 | wall time on a level exceeds its §10 sub-cap | wrapper clock | **STOP the level and record the spend.** Under Sanaa's 2026-09-10 3-D exemption this is a *record*, not a verdict (§10). |
| S5 | `0/` or a time dir exists at launch | pre-launch guard | **REFUSE to launch.** Never clear the directory. |

---

## 9. GRADING PATH — PINNED AT THE FREEZE

`cases/ONERA_M6_C1/grade_m6c1.py`, invoked exactly:
```
python3 cases/ONERA_M6_C1/grade_m6c1.py --l1 <dir> --l2 <dir> --l3 <dir> --reference <json>
```
**The invocation is part of the pinned path.** SUBOFF R1b's launcher invoked its
comparator with three of four required arguments and the comparator **refused (exit 2)**
after 173.23 core-min had been spent (`SUBOFF_R1b_RESULTS.md` §1(iii)). **The M6C1
launcher's grading invocation is asserted against this line before the solver starts**,
not after it finishes.

**Planted-zero control (rule 3), and it refuses.** Before grading, the comparator plants
a known perturbation into a copy of the field it reads and **reads it back from disk**;
if the reader cannot see the plant, the comparator **refuses (exit 2)** and grades
nothing. A zero from a reader not shown able to see a non-zero is not evidence.

**Pin table** — every executable in the grading path by git blob sha, filled at freeze:

| path | blob sha |
|---|---|
| `cases/ONERA_M6_C1/build_m6c1.py` | *(freeze)* |
| `cases/ONERA_M6_C1/grade_m6c1.py` | *(freeze)* |
| `cases/ONERA_M6_C1/run_m6c1_triple.sh` | *(freeze)* |
| this document | *(freeze)* |

---

## 10. COST (rule 12) — ESTIMATED HERE; ACTUAL TO `docs/COST_CALIBRATION.md`

**Basis: a MEASURED lab precedent, not a rate recalled or a guess.** The heat-transfer
**T26** rung ran a 3-D triple of **885 k / 2.99 M / 10.09 M** cells (13.97 M total) for
a recorded **$20.344 derived** (commit `f386be2fb`). At $0.0513/core-h that is
**23,794 core-min** for 13.97 M cells.

| level | cells | share | **estimated core-min** |
|---|---|---|---|
| L1 | 0.90 M | 6.3 % | 1,530 |
| L2 | 3.04 M | 21.4 % | 5,180 |
| L3 | 10.25 M | 72.2 % | 17,460 |
| **triple** | **14.19 M** | | **24,170 core-min** |

**Derived USD: 24,170 core-min ÷ 60 × $0.0513/core-h = $20.67.**
**`cost_basis`: DERIVED, NOT MEASURED.** The rate $0.0513/core-h is **owner-stated**
(Sanaa 2026-08-21/22; corroborated `Xiao2016_EnKF/PREREGISTRATION.md:197`). **The box
cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure
from this box is ever measured.

**Assumption stated so the calibration row can attribute the miss:** T26's cost is
scaled by **cell count alone**. Iteration count, solver (`rhoSimpleFoam` vs T26's) and
per-cell cost are **not** matched. If the actual comes in materially off, **that
assumption is the first place to look**, and it is named here so the attribution is not
invented afterwards.

**CAP: 30,000 core-min** (24 % headroom), sub-caps 1,900 / 6,400 / 21,700.
**🔴 THE CAP DOES NOT STOP THIS RUN.** Sanaa's 2026-09-10 Case Protocol directive
exempts 3-D demo runs from cap stops, relayed by the cfd-supervisor. The cap is
therefore registered as **calibration data, not a gate** — a breach is **recorded and
reported**, and the run continues. Rule 12's "an overrun stops the run" is displaced
here **only** by Sanaa's own words and **only** for this 3-D exemption; no agent
message widened it (rule 9).

**Rule-12 calibration is owed at completion**, as a row in `docs/COST_CALIBRATION.md`
stating actual/predicted, with contention, waste and misprediction attributed
separately. **A completion report without that row is incomplete.**

---

## 11. WHAT THIS DOCUMENT DOES NOT CLAIM

- It does **not** claim the M6 physics will be right. §5.3 gates no physics.
- It does **not** claim a C-grid topology from any CFD source. §1.2: none is on disk.
  The topology argument is `[INFERRED]` from the source **geometry**.
- It does **not** claim the +0.1915 pressure Cl as a validated result. See §5.3.
- It does **not** rule on whether M6CP1's `[0.15, 0.45]` band was ever frozen. §5.3
  refers that to the supervisor.
- A `PASS` on Gate M and Gate T means **a source-faithful M6 mesh exists and marches**.
  It means nothing whatsoever about agreement with experiment.

---

## 12. FREEZE BLOCK — LEFT BLANK FOR THE cfd-SUPERVISOR (check-4, undelegated)

```
FROZEN AT COMMIT: ....................
DOCUMENT BLOB SHA: ....................
DATE (UTC):       ....................
BY:               cfd-supervisor
PRE-COMPUTE CONDITION CHECKED: verification/runs/M6C1_runs/ does not exist  [ ]
                               how checked: ....................
GRADING PATH PINNED (§9 table complete):                                   [ ]
DELIVERED REFINEMENT RATIOS VERIFIED FROM BUILT CELL COUNTS (§4):          [ ]
   r(L1→L2) = ........   r(L2→L3) = ........   path: equal / auto
GATE M CLEARED AT ALL THREE LEVELS BEFORE FREEZE (§5.1, build-before-freeze): [ ]
DRAFT BANNER STRUCK (the blockquote above §0, in one cut):                 [ ]
```

---

# 🔴 MESH-FAMILY PARK — 2026-09-11. **M6C1's FILL TOPOLOGY IS PARKED. NO SOLVE WAS LAUNCHED AND NO GATE WAS EVALUATED.**

**This document was never frozen.** No compute ran under it beyond mesh construction, so nothing here
is a graded verdict — it is a **mesh-family park with a measured reason**, in the shape M6CP1's
Amendment 2 used. **Gate P and Gate G were never evaluated.**

## P.1 THE RULE THAT WAS APPLIED, AND IT WAS SET BEFORE THE ATTEMPT

The supervisor time-boxed the fill three times and, on the third, registered the stop condition in
advance: *"One attempt. If the C-H does not clear 70° at all three levels, M6C1's mesh PARKS and we
take the findings. No fourth topology."* **It cleared at L1 and not at L2. The rule is honoured
rather than reinterpreted, and the lane brought the park rather than a fourth topology.**

## P.2 THE MEASUREMENT

| level | cells | max non-orthogonality | max skewness | M-d |
|---|---:|---:|---:|---|
| L1 | 1,313,792 | **66.57** | 1.443 | **PASS** |
| L2 | 4,434,048 | **70.99** | 1.443 | **FAIL by 0.99°** |

**All 72 over-gate faces at L2 are in-plane, on two adjacent quads at the nose lens's C3 corner** —
the same corner that owns the concave cells, the low-weight faces and the face-volume-ratio faces.
**One defect, every failing check.**

## P.3 🔴 WHY IT IS STRUCTURAL AND NOT MARGINAL — IT WORSENS UNDER REFINEMENT

**The false corner's non-orthogonality GROWS with refinement: 63.34 → 70.88 → 76.62°.** A 0.99°
miss at L2 is not a near-pass; **L3 projects to ~76.6° and the trend is monotone.** **This is the
same "worse under refinement" signature as M6CP1's 60.9° cusp, in a different guise** — and **a
family gate exists precisely to catch it, so the gate is working.**

**And the mechanism is isolated, not guessed.** Sweeping `nb` at fixed `ni` moves the corner along
the surface:

| `nb` | corner at x/c | max non-orth |
|---:|---:|---:|
| 16 | 0.0088 | 73.23 |
| 24 | 0.0334 | 84.31 |
| 32 | 0.0752 | 88.30 |
| 48 | 0.2165 | 89.09 |
| 80 | 0.7476 | 89.83 |

**The worst edge sits AT the corner in every case, and moving it aft makes it worse.** The reason is
geometric: **a 90° block corner on a FLAT boundary is maximally false; tucked at the leading edge,
where the boundary genuinely turns through 180°, it is LEAST false. So the best available placement
is the one that already fails.** Removing the lens entirely — putting all four corners on the loop —
is worse still: 73.23 / 78.66 / 82.87.

**THE DEFENSIBLE CONCLUSION: an airfoil section interior cannot be filled by a one- or two-block
structured mesh without a false corner, and that corner exceeds 70° at the refined levels however it
is placed.** Clearing it requires a fill with **no artificial corner at all** — a genuinely
multi-block elliptic construction with free interfaces, or an unstructured cap. **That is the
registered next step and it is new work, not a fourth parameter.**

## P.4 THE FULL LEDGER, SO NOBODY RE-SPENDS THESE HOURS

| variant | ni | 2-D max | > 70 | note |
|---|---:|---:|---:|---|
| butterfly, shrunk-section core | 200 | 84.89 | 7940/8632 | rhombus core, ~15° corners |
| butterfly, **rectangular** core | 200 | 84.04 | 368/8344 | **21× better — corner ANGLE, not elongation** |
| + Winslow interior only | 200 | 83.70 | 152/8344 | area exact; **interfaces frozen** |
| + interface coupling | 200 | **89.77** | 88/8344 | **max WORSE while count fell; area drifted 4.4e-04** |
| **C-H two-block (lens)** | 200 | **63.34** | **0** | the only variant that passes anywhere |
| C-H two-block (lens) | 300 | 70.88 | 2 | |
| C-H two-block (lens) | 450 | 76.62 | 2 | |
| C-H one-block (no lens) | 200 | 73.23 | 4 | |
| C-H one-block (no lens) | 450 | 82.87 | 24 | |

## P.5 WHAT IS BANKED AND MUST NOT BE REBUILT

- **The source-faithful section and conical loft: `t_TE/c = 1.4104000e-03` at every one of 20 stations
  at both built levels**, against AGARD's 1.4104e-03. **The blunt base that M6CP1 built as a cusp is
  built correctly here and verified by measurement at twenty independent stations.**
- **The exact ×1.5 family — 3.375000 delivered**, by construction, with no `nCellsBetweenLevels` trap.
- **The annulus at 60.83° with ZERO severe faces in the wing region.**
- **The capped topology with a real, closed `tipCap` wall patch** — the defect M-b-2 caught when the
  patch was the whole spanwise end plane typed `wall` at 404,011:1.
- **THE REPLACEMENT LIMB WORKED EXACTLY AS DESIGNED.** The `tipCap` exemption was granted only with a
  minimum-face-area limb tied to the registered resolution. Measured: **the minimum face sits at
  x-fraction 1.0000 — the base — with measured/predicted 1.018 at L1 and 1.004 at L2. Resolution, not
  collapse, demonstrated numerically rather than asserted.**

## P.6 THE FINDINGS THAT OUTLIVE THE MESH

1. **It is corner ANGLE, not elongation, that sets non-orthogonality.** A rectangular core beat a
   shrunk-section core **21-fold** while barely moving the maximum. *"Make the core rounder"* is the
   intuitive fix and it is wrong.
2. **Outward-marching normals DIVERGE and the march is stable; inward-marching normals CONVERGE and
   cross at focal points.** This is why the trick that took the annulus from 85.9° to 60.8° **cannot
   be reused inside a closed curve** — and the shoelace area check, reading 1–110 % error, is the
   only thing that caught it.
3. **Optimising a RECORDED metric at a GATED one's expense.** Varying the radial distribution to
   improve aspect ratio tilted every spanwise grid line; removing it cut severe faces **568,440 →
   192,768**, with **zero remaining in the wing region.**
4. **Interior elliptic smoothing cannot fix what sits on a block interface**, because the solve holds
   interfaces fixed — **and freeing them crudely made the MAXIMUM worse (84.04 → 89.77) while the
   COUNT improved (368 → 88).** A statistic moving while the gated quantity degrades.
5. **THREE separate occasions where the shoelace area check or a planted control caught something the
   quality metric was reporting as an improvement.** Every one would have shipped on its quality
   numbers alone.

**Total cost: ~75 core-min, single-rank Python meshing. No solver core-seconds. Nothing deleted.**
