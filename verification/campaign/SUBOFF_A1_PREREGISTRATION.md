# SUBOFF A1 — DARPA SUBOFF hull + fairwater, zero incidence, GENUINELY 3-D: L0 DIAGNOSE, THEN A MESH FAMILY — PRE-REGISTRATION

> ## 🔴 DRAFT — UNFROZEN. NO COMPUTE HAS RUN UNDER THIS DOCUMENT. NOT A GATE YET.
>
> **HOW TO STRIKE THIS BANNER AT FREEZE:** delete the whole blockquote from the line
> `> ## 🔴 DRAFT` down to and including `> — END DRAFT BANNER —`, and nothing else. One
> contiguous block, the only blockquote before §0, nothing depends on it. *A stale DRAFT
> banner on a frozen document has already cost this lab two amendments in one evening
> (`MRF_R1` Amendment 2, `M6CP1` Amendment 1 §A1.1). This one is built to be cut once.*
>
> Authored by a cfd `lab-lane`. **The FREEZE (sha) and the graded launch are the
> cfd-supervisor's `SUPERVISION_CHARTER` §3 check-4, personal and undelegated.** Until
> the freeze commit every gate, threshold, band, cap and label is amendable and carries
> no evidentiary weight (CLAUDE.md rule 2). Nothing here is graded.
>
> — END DRAFT BANNER —

- **A1 is a NEW LADDER LETTER, deliberately.** `SUBOFF_R1_PREREGISTRATION.md` §8 is
  **frozen** and already assigns meanings to R2, R3 and R4 — R3 being "bare-hull at
  incidence", its named 3-D rung. **A1 does not redefine any of them.** A = *appended*.
  A1 is the hull **with the fairwater**, at zero incidence: 3-D by geometry rather than
  3-D by angle of attack. Its relation to R3 is stated in §9.
- **Prose:** `docs/campaigns/navier_class/SUBOFF/`
- **Inputs / builder / grader:** `cases/navier_class/SUBOFF_A1/` (does not exist yet)
- **Outputs (none yet — the rule-2 pre-compute condition):**
  `verification/runs/navier_class/SUBOFF_A1/` — **this directory does not exist on
  disk at the time of writing**, checked by `ls`, not asserted.
- **Authority:** Sanaa, 2026-09-10, verbatim: *"3D SUBOFF. Papers read and mesh selected
  accordingly. Also must run asap."*

---

## 0. 🔴 THE FIRST REGISTERED RUNG IS A DIAGNOSIS, NOT A MESH FAMILY

**A1 does not inherit the R1b setup, and §1 is why.** R1b's `CT` ran
**0.011283 / 0.339200 / 4.732715** against a registered band of **[0.00324, 0.00396]**
— the fine level roughly **1,300× the band** — with worst residuals **rising** under
refinement (`1.3e-05 → 5.5e-04 → 9.6e-04`). `SUBOFF_R1b_RESULTS.md` §4 records that
anomaly as **OPEN and deliberately not diagnosed**, and says: *"This is the FIRST thing
a successor must resolve."*

**Building three levels of that setup would be the most expensive mistake available.**
It is exactly the M6CP1 pattern — rungs spent on a case whose gate could never have
refused it. So **rung A1-L0 is a diagnosis with zero further solver compute**, and it is
registered as a rung with its own gate. **The mesh family in §4 is not launched until
A1-L0 closes.**

**Most of A1-L0 is already discharged.** §1 reports what this lane measured tonight on
the R1b artifacts, at a cost of **~9 core-min** and **no solver iterations**.

---

## 1. A1-L0 — THE DIAGNOSIS, MEASURED ON THE R1b ARTIFACTS

### 1.1 🔴 FINDING 1 — THE MESHES ARE **NOT** INNOCENT, AND PLAIN `checkMesh` CERTIFIED THEM

Run by this lane on **copies** of the three R1b meshes in scratch (never in the graded
tree — commit `0bdf38639` established that a post-processor writing into a graded tree
is invisible to the rule-4 age guard):

| R1b level | cells | plain `checkMesh` | rc | `-allGeometry -allTopology` | rc | small-determinant cells | min cell determinant | max aspect ratio |
|---|---|---|---|---|---|---|---|---|
| coarse | 39,904 | **`Mesh OK.`** | **0** | **`Failed 1 mesh checks`** | **0** | **1,531** (3.84 %) | **3.526225e-05** | **236.1509114** |
| medium | 89,784 | **`Mesh OK.`** | **0** | **`Failed 2 mesh checks`** | **0** | **3,240** (3.61 %) | **3.526225e-05** | **236.1509094** |
| fine | 202,014 | **`Mesh OK.`** | **0** | **`Failed 2 mesh checks`** | **0** | **7,125** (3.53 %) | **3.526225e-05** | **236.1509070** |

*(medium and fine additionally fail `Faces with small volume ratio (< 0.01)`, 1 face — a
check coarse passes. A new failure mode appears under refinement.)*

**Three things, each independently important:**

1. **Plain `checkMesh` prints `Mesh OK.` on all three, and the full check set fails all
   three.** A verdict of the form `("Mesh OK." in out) and rc == 0` passes every one.
2. **`checkMesh` returns rc = 0 EVEN WHEN CHECKS FAIL** — `Failed 2 mesh checks`,
   exit 0. rc carries no information here.
3. **🔴 THE DEGENERACY IS SCALE-INVARIANT.** Minimum cell determinant is
   **3.526225e-05 at all three levels — identical to seven significant figures** — and
   maximum aspect ratio is **236.15 at all three levels**, likewise. **Refinement does
   not improve the worst cell in this family; it multiplies the number of bad cells
   (1,531 → 3,240 → 7,125) while leaving their badness untouched.** This is the same
   signature as M6CP1's cusp half-angle of 60.9° holding across three levels: the
   defect is a **shape** property, and refinement preserves shape.

**🔴 THIS CORRECTS A CLAIM ON RECORD.** The verification team's reading, relayed to this
lane, was *"the meshes are innocent; the setup is not."* **On this measurement the first
half is wrong.** The meshes carry a scale-invariant geometric degeneracy that plain
`checkMesh` certified as `Mesh OK.` at every level. **This is referred to the
cfd-supervisor and the verification supervisor as a correction; it is not ruled on here.**

### 1.2 🔴 FINDING 2 — A WALL-TREATMENT INVERSION: THE FAMILY REFINES ITSELF OUT OF VALIDITY

`SUBOFF_R1b_RESULTS.md` §4 candidate 4 records *"whether the `nut` wall function remains
inside its valid `y+` range at the fine level was not measured by this rung and no `y+`
figure is on record. **Stated as absent, not approximated.**"* **It is now measured.**

Wall-normal first-cell thickness `y1`, computed from each built mesh (owner-cell volume
÷ hull face area, exact for a prism), and the solver's own `yPlus` on the stored
solutions:

| level | hull faces | `y1` median (m) | **solver `y+` on hull: min / avg / max** |
|---|---|---|---|
| coarse | **60** | 1.0020e-03 | **25.33 / 55.78 / 90.71** |
| medium | **90** | 6.6754e-04 | *(not computed — solution unconverged)* |
| fine | **135** | 4.4483e-04 | 55.87 / 693.75 / 1081.31 — **see the caveat below** |

The wall treatment is **`nutkWallFunction` + `omegaWallFunction`** (`build_suboff.py`
lines 388, 399) — **standard high-Reynolds wall functions, valid only with the first
cell centre in the log layer, y⁺ ≳ 30.**

- **The coarse level's measured minimum y⁺ is already 25.3 — below 30.**
- `y1` falls by **2.25×** across the family (1.0020e-03 → 4.4483e-04). Scaling the
  coarse level's *measured* minimum by the family's own geometric refinement gives a
  fine-level minimum **y⁺ ≈ 11.2 at equal wall stress — squarely in the buffer layer,
  where `nutkWallFunction` is invalid.**
- **So the family starts marginal and refines into invalidity, in exactly the order of
  the CT blow-up.** Coarse (valid-ish y⁺) settled at CT = 0.011283; medium and fine did
  not.

**🔴 THE CAVEAT, AND IT IS NOT SMALL.** The fine level's *solver-reported* y⁺ is
**693.75 average**, not 11 — because that solution **diverged**, so `u_τ` is enormous.
**Cause and effect cannot be separated from these artifacts:** a broken wall treatment
would produce a diverged solution, and a diverged solution produces a meaningless y⁺.
**Finding 2 is therefore a STRONG CANDIDATE with a measured geometric basis, not an
established diagnosis.** It is registered as a candidate and A1's design refuses it on
both readings (§5).

### 1.3 FINDING 3 — SIXTY HULL FACES

The `hull` patch carries **60 / 90 / 135 faces** at the three levels, for a **4.356 m**
body: **7.3 cm axial spacing at coarse, 3.2 cm at fine.** The 202,014-cell fine mesh
spends **135 faces** on the body whose drag it is computing and the rest on a 3 m-radius
far field. **The entire drag integrand lives on those 135 faces.** Whatever else is
true, this family could not resolve boundary-layer development along the hull.

### 1.4 WHAT WAS EXCLUDED, AND BY WHOM

`SUBOFF_R1b_RESULTS.md` §4 already excluded, by direct measurement: the `Aref`
normalisation (the 5° sector value `0.0831703362813915 m²` = analytic ÷ 72, matching to
`1.673e-11`), `magUInf`/`lRef`/`rhoInf`, a wrong mesh (15/15 sha256 pins), incomplete
fields (rule 4 passes all six clauses at all three levels), and a misreading comparator
(both planted-zero controls passed). **This lane re-read those exclusions and does not
disturb them.** In particular **the wedge sector accounting is correct** — the drag is
not being integrated as if the wedge were a full body.

### 1.5 GATE L0 — THE DIAGNOSIS GATE

> **Gate L0 is `GATE REACHED` iff §1.1, §1.2 and §1.3 are on record with their measured
> figures and the cfd-supervisor has read them as a check-1 diff-read.** It is not a
> physics gate and it produces no `CT`. Its function is to make §4's family conditional
> on a diagnosis rather than on hope.

**Cost of A1-L0: ~9 core-min, zero solver iterations** (§8).

---

## 2. THE SOURCES, TITLE-PAGE VERIFIED (rule 15)

### 2.1 ✅ ON DISK AND VERIFIED

**`docs/papers/benchmark_test_cases/groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf`**

Verified by reading the document's own title page with `pdftotext`, **independently of
the sidecar and of the filename**:

| field | as printed on the document | filename claims | match |
|---|---|---|---|
| institution | **David Taylor Research Center**, Bethesda, MD 20084-5000, Ship Hydromechanics Department | `dtrc` | ✅ |
| report number | **DTRC/SHD-1298-01** | `dtrc_shd1298` | ✅ |
| date | **March 1989** | `1989` | ✅ |
| title | **GEOMETRIC CHARACTERISTICS OF DARPA SUBOFF MODELS (DTRC MODEL NOS. 5470 and 5471)** | `darpa_suboff_geometry` | ✅ |
| authors | **Nancy C. Groves, Thomas T. Huang, Ming S. Chang** | `groves` (first author) | ✅ |
| distribution | Approved for public release; distribution unlimited | — | — |
| pages | 82 | — | — |

**The filename is accurate in every component.** No finding against it.

### 2.2 🔴 NOT ON DISK — AND THIS BOUNDS WHAT A1 CAN GATE

| wanted | status |
|---|---|
| **Huang, T. T., Liu, H.-L., Groves, N. C., Forlini, T. J., Blanton, J. N., Gowing, S. (1992)** — the DARPA SUBOFF **experimental programme** | **NOT OBTAINED.** Present only as a **`.url` link stub** at `/home/ubuntu/paper-incoming/CERTONOMOUS_REFERENCE_PACKS_BOTH/.../Links/CASE_1_DARPA_SUBOFF/02_Huang...url` — **outside this repository, no PDF behind it.** |
| **Liu & Huang 1998** — the CFD validation database | **NOT OBTAINED.** Not present in any form, not even a stub under that name. |
| Crook 1990 — resistance for model 5470 | **NOT OBTAINED.** `.url` stub only (`05_Resistance for DARPA SUBOFF...url`). |
| Roddy 1990 — stability and control | **NOT OBTAINED.** `.url` stub only. |
| any **CFD grid-topology** source for SUBOFF | **NOT OBTAINED.** The `.url` stubs at 06–10 name DES/LES and self-propulsion studies; **no PDF is behind any of them.** |

**Nothing was fetched from outside this box and nothing will be (rule 8). No content
from any of the above is used, quoted or paraphrased anywhere in this document.**

**Three consequences, and they are not cosmetic:**

1. **The `AFF-1` / `AFF-8` configuration nomenclature is NOT in the lab's holdings.**
   Searching the title-verified Groves report for `AFF-` returns **zero hits**
   (measured). Those designations come from Huang et al. 1992, which is not on disk.
   **This document therefore identifies configurations by Groves's own numbering
   (§3.1), not by AFF labels**, and a reader wanting AFF-8 should know the lab cannot
   currently define it from a source it holds.
2. **The Reynolds number and reference test conditions are NOT in the lab's holdings.**
   The Groves report is a **geometry** report; searching it for `Reynolds`, `knots`,
   `ft/sec` returns one hit, in a sentence about a Reynolds *stress* measurement
   station. **`Re_L = 1.2×10⁷` is the lab's own inherited working condition
   (`SUBOFF_R1_PREREGISTRATION.md` §2), not a value read from a source on disk.**
3. **The reference tier cannot rise.** Per §6.

---

## 3. THE MESH CLASS, QUOTED FROM THE SOURCE — AND WHAT MAKES IT 3-D

### 3.1 What the source says the configurations are (Introduction, PDF pages 8–9)

Groves/Huang/Chang list **five** configurations, verbatim:

> *"(1) axisymmetric body at zero angle of attack and drift, (2) axisymmetric body with
> fairwater at several angles of attack and zero drift, (3) axisymmetric body with
> symmetric stern appendages at several angles of attack and zero drift, (4)
> axisymmetric body with two different ring wings at zero angle of attack and drift, and
> (5) cambered body of circular cross section in a uniform stream with fairwater.
> **Configuration 1 will serve as a baseline geometry for the numerical evaluations.
> Configurations 2, 3, and 5 will evaluate the non-axisymmetric properties of the
> numerical codes.**"*

**That last sentence is the answer to "what makes it 3-D", in the source's own words.**
The lab's current SUBOFF is **Configuration 1** — and Configuration 1 is, by the
source's own description, the *axisymmetric baseline*. The `constant/polyMesh/boundary`
of the R1b levels carries **2 `wedge` patches and 1 `empty`**, and `checkMesh` reads
**`Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)`**. It is not 3-D and the
source never claimed it would be.

**A1 targets Configuration 2 at zero incidence: the axisymmetric hull WITH THE
FAIRWATER (sail).** Reasons, in order:

- It is the **minimal** step that makes the case genuinely 3-D, by geometry rather than
  by angle of attack — the sail breaks axisymmetry on its own at α = 0.
- Its geometry is **completely defined in the title-verified report on disk** (Table 2,
  four analytic segments + cap), so nothing is invented.
- At zero drift the **x–y plane is a symmetry plane** (the sail sits at top dead
  centre), so a half-model halves the cell count. This is a real saving and it is used.
- **Configuration 3's stern appendages are deferred for a measured reason — §3.3.**

### 3.2 The geometry, quoted

**Axisymmetric hull (Table 1, PDF page 17):**

| item | source value |
|---|---|
| overall length | **14.291667 ft (4.356 m)** |
| maximum diameter | **1.666667 ft (0.508 m)** — hence **L/D = 8.575** (derived) |
| forebody length | 3.333333 ft (1.016 m) |
| parallel middle body | 7.3125 ft (2.229 m) |
| afterbody length | 3.645833 ft (1.111 m) |
| aft perpendicular | x = 13.979167 ft |
| full/model scale ratio λ | 24 |

Bow, parallel-middle-body, afterbody and afterbody-cap equations are given analytically
in Table 1 and are regenerable exactly. **The afterbody cap
`R = 0.1175 R_max [1 − (3.2x − 44.733333)²]^(1/2)`** runs from R = 0.097917 ft at the
aft perpendicular to **R = 0 at x = 14.291667 ft** (verified numerically). **The hull
tail therefore closes to a point** — but as an *ellipse quadrant with a locally radial
tangent*, i.e. a body-of-revolution apex, **not a cusp**. That is the reference
geometry and A1 does not depart from it; §5's feature limb treats it as an apex (§5.1
M-b-1) and not as a trailing edge.

**Fairwater / sail (Table 2, PDF pages 18–19):**

| item | source value |
|---|---|
| LE at | x = 3.032986 ft (0.924 m) |
| TE at | x = 4.241319 ft (1.293 m) |
| total sail length (chord) | **1.208333 ft (0.368 m)** |
| forebody / parallel / afterbody | 0.325521 / 0.200521 / 0.682292 ft |
| span with uniform profile | 0.674479 ft (0.206 m) |
| **half maximum thickness `z_max`** | **0.109375 ft (0.033 m)** ⇒ t/c = **18.1 %** (derived) |
| cap | ellipsoid, `z₂ = [z₁² − (2(y−1.507813))²]^(1/2)`, above y = 1.507813 ft (0.460 m) |
| hull/sail intersection | `[R_BH(x)]² = y² + z₁²` |

### 3.3 🔴 THE TRAILING EDGES CLOSE TO A MATHEMATICAL POINT — MEASURED FROM THE EQUATIONS

**The sail.** The afterbody equation with `E = (4.241319 − x)/0.6822917` evaluates at the
TE (`E = 0`) to `z₁ = 0.1093750 × [0 + 0 + (1 − (−1)⁴(1))] = ` **exactly 0**. Verified
numerically. **The sail trailing edge has zero thickness.**

**The stern appendages, and this one is deliberate on the designers' part.** Table 3
(PDF page 21, read from the rendered page image, not from OCR):

```
z(ξ)/c(y) = 0.29690√ξ − 0.12600ξ − 0.35160ξ² + 0.28520ξ³ − 0.10450ξ⁴
for 0 ≤ ξ = (x−h)/c(y) + 1.0 ≤ 1,   h = x of the trailing edge
c(y) = −0.466308y + 0.88859
```

| | value at ξ = 1 (the TE) |
|---|---|
| **SUBOFF stern appendage** | **−0.0000000** — closes to a point |
| standard NACA 4-digit thickness form (`5t = 1`, i.e. NACA 0020) | **+0.0021000** — blunt |

**The SUBOFF coefficients differ from the standard NACA 0020 form in exactly the last
two terms (0.28520 vs 0.2843; 0.10450 vs 0.1015), and the difference is
−0.000905 + 0.003005 → precisely the −0.0021 needed to close the base.** This is not
OCR drift; it is a deliberate modification. The report says the same thing in words for
the ring-wing struts: *"THE BASIC STRUT SHAPE IS A NACA 0012 THICKNESS DISTRIBUTION
MODIFIED TO END AT A POINT."*

**TE included wedge angle: 27.33°** (from `dz/dξ = −0.24315` at ξ = 1).

**🔴 SO THE SUBOFF APPENDAGES CARRY THE M6CP1 PATHOLOGY IN THE REFERENCE GEOMETRY
ITSELF.** A mesh built faithfully on them has **zero cells across the trailing edge**,
by construction, at every refinement level, forever. **That is why Configuration 3 is
deferred** and why §5's feature limb has to be paired with a registered truncation
rather than with fidelity alone.

### 3.4 REGISTERED GEOMETRIC DEPARTURE — THE SAIL TRAILING EDGE IS TRUNCATED

> **The sail is truncated at 99.5 % of its chord**, at x = 4.235277 ft, giving a
> **base half-thickness of 0.002150 ft = 0.655 mm**, i.e. a **base of 1.311 mm =
> 0.356 % of sail chord**.

Disclosed as a departure, not hidden. Basis, with the tradeoff stated:

| truncation | base thickness | base / chord | TE cell at 8 cells across |
|---|---|---|---|
| 0.990 L | 2.601 mm | 0.706 % | 325 µm |
| **0.995 L — REGISTERED** | **1.311 mm** | **0.356 %** | **164 µm** |
| 0.998 L | 0.527 mm | 0.143 % | 66 µm |

**0.998 L would match the ONERA M6's own source blunt TE almost exactly (0.143 % vs
0.141 %) and is the more faithful choice — and it is rejected on cost**, because 66 µm
cells across a 0.368 m sail drive the fine level past this rung's budget. **0.995 L is
the coarsest truncation that removes the cusp while leaving the TE cell at 164 µm,
comparable to the near-wall spacing the family buys anyway.** This is a cost-driven
choice and it is labelled one. A successor with budget should take 0.998 L.

**The hull tail apex is NOT truncated** — it is a body-of-revolution apex, not a cusp
(§3.2), and §5.1 M-b-1 gates it as an apex.

### 3.5 THE MESH CLASS REGISTERED

**`snappyHexMesh` half-model** (symmetry plane at z = 0, valid at zero drift), on an STL
generated from the Groves equations, with surface refinement regions on the hull, the
sail, the sail/hull junction fillet region and the truncated sail base, plus prism
layers on all walls.

**HONEST LIMIT.** As with M6 (§1.2 of `M6C1_PREREGISTRATION.md`), **the lab holds no
SUBOFF CFD grid-topology source** (§2.2). The topology above is **this lane's choice**,
justified by buildability, not quoted from a validation paper. Labelled `[INFERRED]`.

**🔴 THE `nCellsBetweenLevels` TRAP.** Tonight's MRF R1 build measured that
`nCellsBetweenLevels` is a buffer counted **in cells, not physical thickness**, so a
background block scaled by exactly 1.5 delivered **1.4157 / 1.4264** against a
registered 1.5 — which would have made `roache_triple` refuse the family **after the
compute was spent**. **A1 registers the DELIVERED ratio, computed from built cell counts
before the freeze (§4), never a nominal one.**

---

## 4. THE FAMILY — THREE LEVELS, RATIO DELIVERED NOT NOMINAL

| level | target cells (half-model) | nominal ratio |
|---|---|---|
| **L1** | 0.95 M | — |
| **L2** | 3.21 M | 3.375× ⇒ r = 1.5 per direction |
| **L3** | 10.83 M | 3.375× ⇒ r = 1.5 per direction |

Sizing anchored on the **measured** heat-transfer **T26** 3-D precedent, 885 k / 2.99 M
/ 10.09 M cells (commit `f386be2fb`), the same family shape at the same scale on this
box. `r` is **not registered as 1.5**: the delivered `r_ij = (N_i/N_j)^(1/3)` is computed
from the **built** counts before the freeze, and the equal-ratio or `form="auto"` Roache
path is registered according to what is actually delivered.

**WHAT A1 DOES NOT INHERIT FROM R1b, AND WHY** *(required by §0)*:

| R1b item | A1 | why |
|---|---|---|
| the axisymmetric **wedge** topology | **NOT inherited** | it is Configuration 1, the source's own axisymmetric baseline; Sanaa asked for 3-D |
| `nutkWallFunction` + `omegaWallFunction` | **NOT inherited** | §1.2 — high-Re wall functions on a family that refines y⁺ from 25 to ~11. **A1 uses `nutUSpaldingWallFunction` (all-y⁺)**, which is valid across the whole range and is the treatment M6CP1 already used and recorded admissible |
| the 60/90/135-face hull discretisation | **NOT inherited** | §1.3 |
| `Aref` = analytic ÷ 72 (5° sector) | **NOT inherited** | half-model ⇒ `Aref` = analytic ÷ 2, **read back from the built wall patches** and cross-checked against the analytic area |
| the three mesh levels themselves | **NOT inherited** | §1.1 — scale-invariant degeneracy |
| gate D1's **band shape** (±10 % relative) | *inherited as a shape only, and not as a live gate* — §6 | |
| `Re_L = 1.2×10⁷`, `magUInf`, `lRef`, `rhoInf` | **inherited**, and §2.2 records they are the lab's working condition, not a source value | |
| the strict completion rule and the planted-zero discipline | **inherited** | they are standing rules, not R1b's property |

---

## 5. THE GATES

### 5.1 🔴 GATE M — MESH ADMISSION. FOUR LIMBS, ALL THREE LEVELS.

> **`PASS` iff M-a, M-b, M-c and M-d all hold at L1, L2 and L3. Any limb failing at any
> level ⇒ `GATE FAIL`, and no solver is launched.**

#### M-a. `checkMesh -allGeometry -allTopology`, AND rc IS NOT THE VERDICT

Registered invocation, exactly:
```
checkMesh -allGeometry -allTopology -case <level>
```
**Passes iff the output contains `Failed 0 mesh checks` — equivalently, no line begins
`***`. `Mesh OK.` is NOT relied upon. `rc` is NOT relied upon.**
**Measured basis: §1.1, on this case's own predecessor**, where plain `checkMesh` said
`Mesh OK.` with rc = 0 at all three levels while the full set failed 1, 2 and 2 checks
**and also returned rc = 0**. `grep -rn "allGeometry\|allTopology" scripts/` returned
**zero hits lab-wide** before this document.

#### M-b. 🔴 THE GEOMETRY LIMB A CUSP CANNOT PASS

`checkMesh` clears a collapsed trailing edge under **both** check sets, so it cannot be
the limb that refuses one. **M-b is.**

**M-b-1 — MINIMUM CELLS ACROSS EVERY NAMED GEOMETRIC FEATURE**, at L1, **non-decreasing**
with refinement:

| named feature | registered floor at L1 | note |
|---|---|---|
| **sail trailing-edge base** (truncated, 1.311 mm — §3.4), at every spanwise station sampled at 10 equally spaced heights over the sail span | **≥ 8 cells across the base** | the limb this rung exists for |
| sail leading edge, same stations | ≥ 12 cells around the LE radius | |
| **sail/hull junction**, along the full intersection curve | **≥ 6 cells across the junction fillet region** | 3-D corner flow lives here |
| **hull tail apex** (x = 14.291667 ft) | **≥ 10 cells axially over the last 1 % of hull length** | gated as an **apex**, not a TE — the source closes it to a point legitimately (§3.2) and truncating it would be the departure |
| hull, axially | **≥ 400 faces along the hull generator at L1** | against R1b's 60 (§1.3) |

**Why 8 across the base.** The base is 1.311 mm; 8 cells gives 164 µm, comparable to the
near-wall spacing this family buys anyway, so it is not a new order of cost. Below 8 a
blunt-base recirculation cannot be represented: two shear layers plus a core needs 3
minimum, and 8 is the smallest count leaving any interior once two near-wall cells on
each side are spent. **8 is a floor, not a target.**

**Non-decreasing is the M6CP1 limb.** A feature count flat under refinement is the exact
signature of M6CP1's 60.9° cusp holding across three levels, and of §1.1's determinant
holding at 3.526225e-05 across three levels. **Flat ⇒ `GATE FAIL`.**

**M-b-2 — WALL-FACE-AREA-RATIO CEILING.**

> **On every wall patch, at every level: `max(face area) / min(face area) ≤ 500`.**

| case | patch | measured ratio | outcome |
|---|---|---|---|
| **M6CP1** | `wing` | **7,212 : 1** | the case that died |
| SUBOFF R1b coarse / medium / fine | `hull` | 16.3 / 17.2 / 18.6 : 1 | coarse ran and settled |

500 sits an order of magnitude below the measured failure and above every healthy
measured value here. **Weakness stated:** the R1b hull is a 1-cell-wide **wedge**, so its
ratio is not a fair comparator for a 3-D appended body where spanwise and junction
stretching will exceed it. 500 is anchored **firmly** on the failure side and **loosely**
on the healthy side. **It is registered as a ceiling M6CP1 fails by 14×**, which is the
property that matters, and **it will not be loosened after the run.**

#### M-c. 🔴 DIMENSIONALITY — AND THIS RUNG IS THE REASON THE LIMB EXISTS

> **Passes iff `checkMesh` output contains
> `Mesh has 3 geometric (non-empty/wedge) directions`.**

**The `solution (non-empty)` line is REGISTERED AS NOT THE TEST.** Measured on this
case's own predecessor tonight, four lines apart in one output:

```
Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)
Mesh has 3 solution (non-empty) directions (1 1 1)
```

**A check reading the second line certifies the R1b axisymmetric wedge as 3-D.** Since
the whole point of A1 is that the lab's SUBOFF was not 3-D, **reading the wrong line
here would defeat the rung entirely.**

#### M-d. STANDARD QUALITY GATES

`docs/standards/MESH_STANDARD.md` §3: max non-orthogonality **≤ 70°**, max skewness
**≤ 4**. **Additionally gated here, because §1.1 measured it:
minimum cell determinant `≥ 1.0e-03`** — the threshold `checkMesh` itself uses for
`Cells with small determinant`, at which R1b scored `3.526e-05`, **28× below it, at
every level**. Max aspect ratio and cell-volume ratio are **recorded**, not gated.

### 5.2 GATE W — THE WALL TREATMENT MUST BE VALID WHERE IT IS USED

> **`PASS` iff, at `endTime`, at every level, the solver-reported hull-patch `y+`
> satisfies `y+ < 300` everywhere AND the wall treatment is `nutUSpaldingWallFunction`
> (all-y⁺) on every wall patch. `y+` is REPORTED per level in the results record
> regardless of outcome.**

This is §1.2's repair, and it is deliberately shaped so it cannot be dodged either way:
`nutUSpaldingWallFunction` is valid from the viscous sublayer through the log layer, so
refinement **cannot** walk this family out of validity the way R1b's did. The `y+ < 300`
ceiling catches the opposite failure — an under-resolved wall — and the `y+` report at
every level makes the trend visible whatever it is.

### 5.3 PHYSICS — `CT`, REPORTED, WITH A BOUNDED-AGREEMENT BAND, BEHIND THE ROACHE GATE

> **Gate D2.** `CT = R_T / (½ ρ U² S_wetted)` at `Re_L = 1.2×10⁷` on the hull+sail
> half-model, taken from the finest grid of a **CONVERGING** Roache triple, is **`PASS`
> iff `|CT_cfd − CT_ref| ≤ 0.15 · CT_ref` (±15 %)**, else **`GATE FAIL`**. **A
> non-CONVERGING triple is `NOT A RESULT` whatever the value (rule 5).**

- **`CT_ref` is a MANIFEST / ENGINEERING ANCHOR and stays one.** It is R1's ITTC-1957
  friction-line + form-factor anchor of **3.6×10⁻³** on wetted area, **plus a sail
  increment computed by the same engineering method and recorded in the reference JSON
  before the freeze**. **There is no title-verified SUBOFF force measurement on disk**
  (§2.2), so this gate is **BOUNDED-AGREEMENT against a manifest anchor** and is **NOT
  experiment-validated.**
- **The band is ±15 %, not R1's ±10 %, and the widening is registered with its reason
  before compute:** the sail increment is an engineering estimate stacked on an
  engineering estimate, so the anchor is weaker than R1's bare-hull anchor. **Widening a
  band because the *reference* is weaker is legitimate; widening it because the *answer*
  disagreed is not, and after the freeze it cannot be widened at all** (rule 2).
- Gate D2 sits **behind** the rule-5 Roache gate, which sits **behind** Gates M and W.
  The gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the
  reverse.

---

## 6. REFERENCE TIER

Per `verification/credibility/REFERENCE_TIER_STANDARD.md`:

- **Tier: CODE-VERIFIED (rank 2), with the disavowal "NOT experiment-validated",**
  rising to **BOUNDED-AGREEMENT (rank 3)** only against the manifest anchor.
- **It cannot rise further from the lab's current holdings.** Huang et al. 1992, Liu &
  Huang 1998 and Crook 1990 are **NOT OBTAINED** (§2.2). **Rule 15 forbids treating a
  `.url` stub as a source.** Any page showing D2 must carry the ±15 % band and the
  disavowal.
- **Unlike R1, A1 IS 3-D and IS a registry candidate at completion** — under the
  dimension axis it is `3-D` on the strength of Gate M-c, not on assertion. **Registry
  action is still deferred to completion** and is the verification team's, not this
  document's.

---

## 7. COMPLETION RULE (rule 4) AND MONITOR STOPS

**Complete iff all hold; the comparator refuses (exit 2) rather than degrade:**
`rc = 0`; an `End` line; last time `== endTime`; fields present at `endTime` —
**`p U k omega nut phi`**, the **incompressible** `simpleFoam` set, enumerated from what
the solver writes and **not** the thermal family's list; `ExecutionTime` count
`== round(endTime/deltaT)`; and **the age guard** — every field at `endTime` strictly
newer than the case's own `0/` — with the disclosed weakness that the age guard cannot
distinguish a solver-written field from a post-processor-written one (commit
`0bdf38639`), so **grading runs on a copy, never in place.** A guard refuses a case
where `0/` or a time directory already exists.

| # | state | **the one registered action** |
|---|---|---|
| S1 | any level's worst residual **rises** over 500 consecutive iterations | **STOP the level.** Record. Do **not** re-run with different relaxation — that is a second action on the same state. This is R1b's signature and it is the answer, not an obstacle. |
| S2 | hull-patch `y+` exceeds 300 at any write | **STOP the level; record `GATE FAIL` on Gate W.** |
| S3 | `CT` changes by more than 5 % over the final 100 iterations at `endTime` | **STOP and record NOT PLATEAUED.** R1b's medium was moving −10.02 % per hundred iterations at its cut and its comparator still flagged it `PLATEAUED` (`SUBOFF_R1b_RESULTS.md` §3a: the plateau test is a two-point test and cannot see a drift). **A1's plateau test is a regression over the final 500 iterations, not a two-point difference.** |
| S4 | wall time exceeds a §8 sub-cap | **Record the spend and continue** — Sanaa's 3-D exemption (§8). |
| S5 | `0/` or a time dir exists at launch | **REFUSE to launch.** Never clear the directory. |

---

## 8. COST (rule 12)

**A1-L0 (the diagnosis): ~9 core-min actual, zero solver iterations** — six `checkMesh`
invocations, two `simpleFoam -postProcess -func yPlus` invocations and four Python mesh
reads, all at rank 1, on copies in scratch. **Labelled ESTIMATED, not measured**: no
per-command timing record was kept, and rule 12 forbids calling a cost measured without
a record backing it.

**A1 mesh family**, anchored on the **measured** T26 precedent (13.97 M cells →
**23,794 core-min**, $20.344 derived, commit `f386be2fb`), scaled by cell count:

| level | cells | **estimated core-min** |
|---|---|---|
| L1 | 0.95 M | 1,620 |
| L2 | 3.21 M | 5,470 |
| L3 | 10.83 M | 18,440 |
| **triple** | **14.99 M** | **25,530 core-min** |

**Derived USD: 25,530 ÷ 60 × $0.0513/core-h = $21.83.**
**`cost_basis`: DERIVED, NOT MEASURED.** Rate $0.0513/core-h is **owner-stated** (Sanaa
2026-08-21/22; corroborated `Xiao2016_EnKF/PREREGISTRATION.md:197`); **the box cannot
read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5).

**Assumption named so the calibration row can attribute a miss:** T26 is scaled by
**cell count alone**; iteration count, solver and per-cell cost are **not** matched, and
A1 is incompressible `simpleFoam` where T26 is not. **If the actual is materially off,
that is the first place to look**, and naming it now stops it being invented later.

**CAP: 32,000 core-min** (25 % headroom), sub-caps 2,000 / 6,800 / 23,000.
**🔴 THE CAP DOES NOT STOP THIS RUN.** Sanaa's 2026-09-10 Case Protocol directive
exempts 3-D runs from cap stops. The cap is **calibration data, not a gate**; a breach
is recorded and reported and the run continues. Rule 12's "an overrun stops the run" is
displaced **only** by Sanaa's own words and **only** for this exemption; **no agent
message widened it** (rule 9).

**Rule-12 calibration is owed at completion** as a row in `docs/COST_CALIBRATION.md`
giving actual/predicted with contention, waste and misprediction attributed separately.

---

## 9. WHAT THIS DOCUMENT DOES NOT CLAIM

- It does **not** claim SUBOFF drag agreement with experiment. §6: no experimental
  source is on disk.
- It does **not** claim the AFF-1/AFF-8 configurations. §2.2: that nomenclature is not
  in any source the lab holds.
- It does **not** supersede or redefine R2, R3 or R4 of the frozen R-ladder. **A1 is a
  3-D appended-geometry rung at zero incidence; R3 remains the bare-hull at-incidence
  rung.** If the cfd-supervisor prefers A1 to *become* R3, that is the supervisor's call
  and requires renaming this document before the freeze, not after.
- It does **not** diagnose R1b's `CT` anomaly to a conclusion. §1 gives two measured
  findings and one strong candidate with a caveat that cause and effect cannot be
  separated from the artifacts. **The anomaly stays OPEN.**
- A `PASS` on Gates M and W means a source-faithful 3-D SUBOFF mesh exists, marches, and
  uses a wall treatment valid where it is applied. It means nothing about experiment.

---

## 10. FREEZE BLOCK — LEFT BLANK FOR THE cfd-SUPERVISOR (check-4, undelegated)

```
FROZEN AT COMMIT: ....................
DOCUMENT BLOB SHA: ....................
DATE (UTC):       ....................
BY:               cfd-supervisor
PRE-COMPUTE CONDITION CHECKED:
   verification/runs/navier_class/SUBOFF_A1/ does not exist               [ ]
   how checked: ....................
GATE L0 READ AS A CHECK-1 DIFF-READ (§1.5):                              [ ]
GRADING PATH PINNED BY BLOB SHA:                                         [ ]
LAUNCHER'S GRADING INVOCATION ASSERTED BEFORE SOLVER START:              [ ]
   (R1b spent 173.23 core-min and its comparator then refused on argv)
DELIVERED REFINEMENT RATIOS VERIFIED FROM BUILT CELL COUNTS (§4):        [ ]
   r(L1->L2) = ........  r(L2->L3) = ........  path: equal / auto
GATE M CLEARED AT ALL THREE LEVELS BEFORE FREEZE (build-before-freeze):  [ ]
DRAFT BANNER STRUCK (the blockquote above §0, in one cut):               [ ]
```

---

# §11. EXTENSION — 2026-09-11 — SOURCE RE-READ FROM RENDERED PAGES, GATE ARMING, THE PLANT, THE AGE-GUARD ANCHOR, AND THE MEASURED COST OF GATE M-b-1

**Written by a second cfd `lab-lane`, 2026-09-11, on `HEAD = cc2a2e039`. The document
is still a DRAFT and still UNFROZEN — the banner at the head stands. Under CLAUDE.md
rule 2 amendments before first compute are legal and must state the condition and how
it was checked; §11.0 does that. Nothing above this section was renumbered, reworded or
deleted: `lines whose number changed above this section: 0`.**

**Authority for the work:** Sanaa, 2026-09-10, verbatim: *"3D SUBOFF. Papers read and
mesh selected accordingly. Also must run asap."*

---

## 11.0 THE RULE-2 PRE-COMPUTE CONDITION, RESTATED SO IT IS STILL CHECKABLE

**§0 asserted that `verification/runs/navier_class/SUBOFF_A1/` did not exist. IT NOW
EXISTS.** This lane built the geometry and the L1 mesh under it. The absence of a
directory was never the thing rule 2 protects; **the absence of a SOLVER RESULT is.**
The condition is therefore restated in a form that survives mesh building and that the
freeze block must check:

> **For every level `L ∈ {L1, L2, L3}` of `verification/runs/navier_class/SUBOFF_A1/`:
> no `0/` directory, no time directory, no `log.simpleFoam`, no `rc`, no `RC.txt`,
> no `postProcessing/`. Checked by `ls`, printed into the freeze block, not asserted.**

**No solver has been invoked under this document. Mesh building is not a graded run and
does not need the freeze; it needs `docs/standards/MESH_STANDARD.md` and a full-flag
`checkMesh`, and it got both.**

---

## 11.1 THE SOURCE, RE-READ FROM **RENDERED PAGES** — TWO CITATION DEFECTS AND ONE CONFIRMATION

Rule 15 forbids verifying a paper by filename, file type or hash. §2.1 verified the
title page with `pdftotext`. **This lane verified it by RENDERING PDF page 1 as an image
and reading it.** What is printed on that page:

| field | as READ FROM THE RENDERED PAGE |
|---|---|
| institution | **David Taylor Research Center**, Bethesda, MD 20084-5000 |
| report / date | **DTRC/SHD-1298-01, March 1989**, Ship Hydromechanics Department |
| title | **GEOMETRIC CHARACTERISTICS OF DARPA SUBOFF MODELS (DTRC MODEL NOS. 5470 and 5471)** |
| authors | **Nancy C. Groves, Thomas T. Huang, Ming S. Chang** |
| accession | **AD-A210 642**, spine; DTIC stamp JUL 31 1989 |
| distribution | Approved for public release; distribution unlimited |

**🔴 DEFECT 1 — THE THIRD AUTHOR.** The report's third author is **Ming S. CHANG**. Any
record naming the third author "Belt" is wrong; the title page says Chang. *(This is
recorded because a briefing this lane received carried "Belt".)*

**🔴 DEFECT 2 — §3.2 CITES TABLE 2 AT THE WRONG PAGES.** §3.2 gives *"Fairwater / sail
(Table 2, PDF pages 18–19)"*. **PDF pages 18–19 are report pages 11–12 and carry FIGURE 5
(stern-appendage locations) and the stern-appendage / ring-wing prose.** Table 2 is at
**PDF pages 14–15 = report pages 7–8**, rendered and read by this lane. The *page
citation* is wrong; **the equations §3.2/§3.3 quote are RIGHT** — re-derived here term by
term from the rendered images and reproduced below so a successor need not re-render.

**✅ CONFIRMATION — THE SAIL TRAILING EDGE CLOSES TO A MATHEMATICAL POINT.** Table 2,
read from the rendered page:

```
SAIL FOREBODY   3.032986 <= x <= 3.358507,  y <= 1.507813
   z1 = Zmax [ 2.094759 A + .2071781 B + C ]^(1/2)
   A = 2D(D-1)^4 ;  B = 1/3 D^2 (D-1)^3 ;  C = 1 - (D-1)^4 (4D+1)
   D = 3.072000 (x - 3.032986)
SAIL PARALLEL MB 3.358507 <= x <= 3.559028 :  z1 = Zmax = .109375 Ft = 1.3125 inch
SAIL AFTERBODY  (Revised 11 January 1989)  3.559028 <= x <= 4.241319, y <= 1.507813
   z1 = .1093750 [ 2.238361 (E(E-1)^4) + 3.106529 (E^2 (E-1)^3) + (1-(E-1)^4 (4E+1)) ]
   E  = (4.241319 - x)/0.6822917
SAIL CAP        z2 = [ z1^2 - (2(y - 1.507813))^2 ]^(1/2),  1.507813 <= y <= z1/2 + 1.507813
HULL/SAIL       [R_HB(x)]^2 = y^2 + z1^2 ,  R_HB = the hull BOW equation (Table 1)
```

> **🔴 THE AFTERBODY EXPRESSION IS *NOT* SQUARE-ROOTED. THE FOREBODY ONE IS.** The two
> equations look alike on the page and differ in exactly that. An implementation that
> carries the `^(1/2)` into the afterbody silently changes the whole aft 56 % of the sail
> and still produces a plausible-looking foil. **This is registered as a named
> implementation hazard**, because it would not be caught by any mesh gate.

At the trailing edge `E = 0`, so `A = B = 0` and `C = 1 − (−1)⁴(4·0+1) = 0`:
**`z1(x = 4.241319 ft) = 0` EXACTLY** — re-evaluated numerically here and returned as
`0.0`, not as a small number. `build_suboff_a1_geometry.py` **REFUSES to build (exit 2)**
if that evaluation is not exactly zero, because the entire justification for the
registered truncation is that premise.

**✅ NEW MEASUREMENT — THE SAIL *LEADING* EDGE IS NOT A CUSP, AND §5.1 M-b-1's LE LIMB
NOW HAS A NUMBER.** Near the LE the forebody bracket behaves as `≈ 4.1895 D`, so
`z1 ∝ √(x − x_LE)` — a **rounded** nose, not a knife edge. The leading-edge radius,
evaluated as `z1²/2s` at `s = 10⁻⁶ … 10⁻⁹ ft` and **converged to six significant figures
at every one of them**:

> **Sail leading-edge radius `r_LE = 0.076982 ft = 23.464 mm`, `r_LE/c = 6.371 %`.**

For context, a NACA 4-digit section of the same thickness (`t/c` measured here as
**18.1035 %**, matching §3.2's 18.1 %) has `r/c = 1.1019 (t/c)² = 3.61 %`. **The SUBOFF
sail leading edge is 1.76× blunter than a NACA section of its own thickness.** §5.1
M-b-1 registers "≥ 12 cells around the LE radius": 12 cells around a quarter-circle of
radius 23.464 mm is a **3.07 mm** cell, and the registered sail surface cell at L1 is
**1.23 mm**, so the limb is met with ~2.5× margin. **This limb is therefore NOT the
binding one — §11.6 identifies the one that is.**

---

## 11.2 GATE ARMING — EVERY GATE NAMES WHAT ARMS IT AND **REFUSES** WHEN UNARMED

**The defect this repairs, stated plainly:** SUBOFF's earlier gate carried
`armed: by_data`. A gate armed *by its own data* **passes when the data is missing**,
because "no disagreement found" and "nothing was compared" read identically. That is a
gate that cannot fail. It is the same family of defect as §5.1 M-a (`Mesh OK.` with
`rc = 0` on a mesh failing three checks) and as §3a of `SUBOFF_R1b_RESULTS.md` (a
two-point plateau test that cannot see a drift).

> **REGISTERED, FOR EVERY GATE IN §5 AND §11: a gate has an ARMING CONDITION and an
> UNARMED VERDICT, and the unarmed verdict is NEVER `PASS`.**

| gate | ARMED BY — and this is read from disk, not from a flag | UNARMED VERDICT |
|---|---|---|
| **M-a** full-flag `checkMesh` | the level's `log.checkMesh.FULLFLAG` exists, contains the literal string `-allGeometry`, contains the literal string `-allTopology`, and contains a line matching `^Failed [0-9]+ mesh checks\.$` **or** `^Mesh OK\.$` | **`BLOCKED`** |
| **M-b-1** feature counts | the built mesh yields a non-empty cell-centre set inside the registered probe box at **every** named feature, **and the probe's planted control (§11.3) fired** | **`BLOCKED`** |
| **M-b-2** wall face-area ratio | both wall patches (`hull`, `sail`) exist in `constant/polyMesh/boundary` with `nFaces > 0` | **`BLOCKED`** |
| **M-c** dimensionality | `log.checkMesh.FULLFLAG` contains a line beginning `Mesh has ` and `geometric (non-empty/wedge) directions` — **the `solution (non-empty)` line is not a substitute and a reader that matches it is a defect** (§5.1 M-c) | **`BLOCKED`** |
| **M-d** quality | the three numeric lines (`non-orthogonality Max`, `Max skewness`, `determinant`) all parse to floats | **`BLOCKED`** |
| **W** wall treatment | `y+` was written at `endTime` **and** every wall patch in `0/nut` carries `nutUSpaldingWallFunction` | **`BLOCKED`** |
| **D2** `CT` | the reference JSON exists, its `CT_ref` parses to a float, and the run cleared §7 completion | **`BLOCKED`** |

**`BLOCKED` is a refusal to read a gate, not a soft pass and not a `NOT A RESULT`.** No
gate in this document may return `PASS` from an empty comparison, and the comparator
**exits 2 rather than degrade** (§7).

---

## 11.3 THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3) — REGISTERED, NOT INHERITED

§4 listed "the planted-zero discipline" as *inherited*. **A discipline is not a control.**
Rule 3 requires a reader to be **shown able to see a non-zero** before its zero is
evidence, and this rung's most dangerous zero is *"zero cells across the trailing-edge
base"* — which is exactly what a probe with a mis-specified box also returns.

> **REGISTERED. The feature probe (`probe_suboff_a1_features.py`) plants a synthetic
> cell-centre set of a KNOWN count `PLANT_N = 13` spanning a segment of known length,
> runs the SAME counting function that grades the mesh over it, and REFUSES (exit 2)
> unless the function returns exactly 13. The plant runs on EVERY invocation, before
> any mesh is read, and its result is printed into the record beside the measured
> counts.**

**Two failure modes this catches and the existing discipline does not:** a probe box in
the wrong units or the wrong coordinate (returns 0 everywhere, reads as "cusp not
resolved"), and an off-by-one that halves every count in a half-model (reads as "family
is half as good as it is"). **The plant is run on the counting function, not on a copy
of the mesh, so it costs no compute and cannot be skipped for cost.**

**A second, independent control, registered because the half-model makes it necessary:**
the probe reports the **full-base-equivalent** count as `2 × (count in z ∈ [0, z_base])`
and **also** reports the raw half-model count. **Both go in the record.** A reader that
sees only one of them cannot tell a factor-of-two convention error from a physical
result.

---

## 11.4 RULE-4 LIMB 6 — THE AGE GUARD IS ANCHORED ON THE **SOLVER-WRITTEN** `processor*/<endTime>/` FIELDS, AND THE ORDERING TEST IS THE OTHER HALF OF IT

§7 states the age guard against `0/` and records the weakness that it "cannot
distinguish a solver-written field from a post-processor-written one (commit
`0bdf38639`)". **`6d264ed1c` closed that weakness for `MRF_R2` and this rung adopts it
verbatim rather than re-deriving it.**

> **REGISTERED LIMB 6, AS IT WILL BE GRADED:**
> 1. Every field at `endTime` in the **reconstructed** `<endTime>/` is strictly newer
>    than the case's own `0/T`. *(the existing §7 limb, retained)*
> 2. **AND** every field at `endTime` in **`processor*/<endTime>/`** is strictly newer
>    than `0/T`, with **none stale, none missing**, across all ranks.
> 3. **AND the ordering test**, read off disk: `log.decomposePar` is **older** than the
>    `processor*/<endTime>/` fields, and `log.reconstructPar` is **newer** than them —
>    the order a solve-then-reconstruct produces and a stray post-processor does not.

**Two limitations, stated because `6d264ed1c` states them and a limb quoted without its
limitations is worse than none:**
- **The anchor is a strong default, NOT an impossibility.** `decomposePar -fields` and
  `redistributePar` both write `processor*/<t>/`. Limb 6.2 alone can be manufactured;
  6.2 **with** 6.3 is what carries.
- **A SERIAL run has no `processor*/` at all.** This rung runs in parallel at every
  level (§8), so the anchor is available; **if any level is ever run serially, limb 6.2
  and 6.3 are `BLOCKED`, not passed** (§11.2's arming rule applies to them too).

---

## 11.5 THE WALL-TREATMENT DECISION, WITH ITS NUMBERS — WHY NOT WALL-RESOLVED

§5.2 registers `nutUSpaldingWallFunction`. **This lane endorses it and adds the
arithmetic that makes the choice a decision rather than a preference**, because §1.2's
finding — *the R1b family refines itself out of `nutkWallFunction` validity* — is only
half an argument until the alternative is costed.

At `Re_L = 1.2×10⁷` on `L = 4.35610 m` with `ν = 1×10⁻⁶ m²/s`: `U = 2.7548 m/s`;
ITTC-1957 `Cf = 0.075/(log₁₀Re − 2)² = 2.907×10⁻³`; `u_τ = 0.10503 m/s`.
**Cross-check, not a coincidence:** `cases/navier_class/SUBOFF/build_suboff.py` carries
`Y1_TARGET = 1.0e-3 m` annotated *"y+ ~ 100"*, and `1×10⁻³ × 0.10503 / 1×10⁻⁶ = 105`.
**The lab's own inherited constant reproduces this `u_τ` to 5 %,** so the numbers below
are not a new calibration.

| route | first-cell height `y₁` | verdict |
|---|---|---|
| **wall-resolved, `y⁺ = 1`** | **9.52 µm** | **REJECTED — and the reason is costed, not asserted.** 9.52 µm first cells over a 2.994 m² half-model wetted area, at a layer expansion of 1.2, need ~28 prism layers to reach the 4.9 mm outer cell. At L1 that is ≈ 1.7×10⁷ layer cells **alone**, ~7× this rung's whole registered L1 budget, before a single off-body cell. |
| **`nutkWallFunction`, `y⁺ ≥ 30`** | 286 µm at L1 | **REJECTED — this is R1b's failure mode.** `y₁` falls by `r = 1.5` per level, so `y⁺` runs **30 → 20 → 13.3** and the family walks out of the model's validity **in the same order as refinement**, which is §1.2's finding exactly. |
| **`nutUSpaldingWallFunction` (all-`y⁺`) — REGISTERED** | 286 / 191 / 127 µm | **Valid from the viscous sublayer through the log layer.** The `y⁺` **30 → 20 → 13.3** walk that kills the high-Re route is inside Spalding's range at every level. |

> **REGISTERED `y⁺` TARGETS, reported per level whatever the outcome (§5.2):
> L1 ≈ 30, L2 ≈ 20, L3 ≈ 13.3, with the Gate-W ceiling `y⁺ < 300` unchanged.**
> **These are PREDICTIONS from the ITTC anchor, not measurements** — the measured `y⁺`
> goes in the results record and §11.7 registers what would falsify them.

---

## 11.6 🔴 THE MEASURED OCTREE COST OF GATE M-b-1 — AND IT CONTRADICTS §4's FAMILY SIZING

**This is the finding of §11 and it was paid for in compute.**

§5.1 M-b-1 registers **≥ 8 cells across the 1.311 mm truncated base**. §4 registers
**L1 = 0.95 M cells**. **A first build of L1 measured that those two numbers cannot both
be true**, and it measured it the expensive way:

| what was built | measured |
|---|---|
| L1 with refinement **boxes** around the near field and a 40 × 271 × 20 mm level-9 box at the trailing edge | **8,740,333 cells at surface-refinement iteration 6, still climbing** when the build was stopped |

**The arithmetic behind it, which is the transferable part.** The gate fixes the cell
size at the base: `1.3109 mm / 8 = 164 µm`. An octree reaches 164 µm from a 78.7 mm base
cell at **level 9** (`78.7/2⁹ = 153.7 µm`). The cost of a level-9 region is its volume
divided by `(153.7 µm)³ = 3.63×10⁻¹² m³` — **2.75×10¹¹ cells per cubic metre.** The
first teBox held 2.17×10⁻⁴ m³ and therefore **~6.0×10⁷ cells on its own.**

**The repair, and it is a geometry decision rather than a tuning one:** the level-9
region was cut to the base itself — **3 mm (x) × 217.7 mm (y) × ±2.62 mm (z)**, i.e.
`1.71×10⁻⁶ m³ ≈ 4.7×10⁵` cells — and every near-field box was replaced by
`mode distance` shells that hug the body. **The registered regions are now:**

```
refinementSurfaces : hull (4 4)    sail (6 7)
refinementRegions  : hull   mode distance ((0.030 3) (0.150 2) (0.500 1))
                     sail   mode distance ((0.006 6) (0.030 5))
                     jctBox mode inside   ((1e15 6))    x[LE-20mm, TE+20mm] y[Rmax-20, Rmax+10] z +/-25mm
                     teBox  mode inside   ((1e15 9))    3mm x 217.7mm x +/-2.62mm at the truncated base
```

> **🔴 REGISTERED CONSEQUENCE, BEFORE THE FREEZE AND BEFORE ANY SOLVER: §4's target cell
> counts (0.95 M / 3.21 M / 10.83 M) ARE NOT ACHIEVABLE UNDER GATE M-b-1 AS REGISTERED.
> The BUILT counts are what §4's delivered ratio is computed from, and they are recorded
> in §11.7 below. The cfd-supervisor's freeze must either (a) accept the built counts and
> re-cost §8 from them, or (b) coarsen the registered truncation — §3.4's own table
> offers 0.990 c, whose 2.601 mm base needs only 325 µm cells and is therefore ~8× cheaper
> in the teBox — or (c) lower the feature floor below 8. THIS LANE DOES NOT CHOOSE
> BETWEEN THEM: a gate threshold is not a lane's to move (CLAUDE.md rule 9).**

**Why this is a finding and not a mishap.** §3.4 chose 0.995 c over 0.998 c *"on cost"*,
and costed it by the **TE cell size** (164 µm) alone. **The TE cell size is not the cost;
the octree volume at that cell size is**, and the two differ by the ratio of the region
volume to the cell volume — here a factor of ~10⁵. **The same error is available to every
future rung that registers a feature floor on a thin base**, which is why it is written
here rather than in a lane's report.

---

## 11.7 REGISTERED PREDICTIONS, AND WHAT WOULD FALSIFY EACH

**Registered BEFORE the solver, and each one names the artifact that settles it. A
prediction with no falsifier is a hope (`INNOVATION_STANDARD`).**

| # | PREDICTION | FALSIFIED BY |
|---|---|---|
| **P1** | Full-flag `checkMesh` **fails at least one check** at **every** level, and the failing check is **`Cells with small determinant`** or **high aspect ratio**, not non-orthogonality or skewness. *(Basis: every `snappyHexMesh` family this lab has measured — M6CP1, MRF, DrivAer — fails on determinant/AR and clears nonOrtho/skew; §1.1 measured R1b's determinant at 3.526225e-05, 28× below `checkMesh`'s own 1e-3.)* | a level printing `Failed 0 mesh checks`, or a level failing on **non-orthogonality or skewness instead** |
| **P2** | Minimum cell determinant is **NOT identical across the three levels** — it varies by more than 1 % between L1 and L3. *(Basis: §1.1 measured 3.526225e-05 at all three R1b levels, identical to 7 s.f., because that family was a scaled wedge. A `snappyHexMesh` family re-snaps at every level, so scale-invariant degeneracy should not survive.)* | the three determinants agreeing to better than 1 % — which would mean **the new family carries R1b's pathology too**, and would make M-d's `≥ 1.0e-03` limb the binding gate |
| **P3** | The delivered refinement ratios computed from **built** cell counts are **not** 1.5 — they differ from the nominal by more than 1 %. *(Basis: MRF delivered 1.4157/1.4264 against a registered 1.5 — `nCellsBetweenLevels` buffers in CELLS, not thickness.)* | both delivered ratios landing within 1 % of 1.5 |
| **P4** | Cells across the truncated TE base are **non-decreasing** L1→L2→L3 and **≥ 8** at L1. *(This is M-b-1; it is registered as a prediction as well as a gate so that a flat count is visible as a failed prediction even if the gate is later argued about.)* | a flat or decreasing count — **the M6CP1 signature**, and it would mean the truncation did not remove the cusp |
| **P5** | Measured hull-patch `y⁺` at `endTime` lands within **±50 %** of the §11.5 predictions (30/20/13.3). | a measured `y⁺` outside that band at any level — which would falsify the ITTC anchor `u_τ` and, with it, **the wall-treatment argument in §11.5**, not merely a number |
| **P6** | **No solver-independent claim is made about `CT`.** | — *(not a prediction; recorded so the list cannot be read as one)* |

**Registered now, before the freeze: P1–P5 are reported in the results record WHETHER OR
NOT they hold, and a falsified prediction is written up as falsified, not quietly
dropped.** §11.6 is what this looks like when it happens to a cost estimate.

---

## 11.8 M3 REPORTING, NOT STOPPING — SANAA'S 3-D EXEMPTION, READ NARROWLY

§8 records that Sanaa's 2026-09-10 Case Protocol exempts 3-D runs from cap **stops**.
§7's monitor table carries that as `S4 → record and continue`. **Registered here as the
explicit reporting rule, and its boundary:**

> **`M3 REPORTING`. On a cap or sub-cap breach at any level: write `CAP_BREACH.txt` into
> that level's directory with the breached figure, the cap, the ratio and the UTC
> timestamp; append the same row to the run record; and **CONTINUE**. The breach is
> reported to the cfd-supervisor at the next report boundary, not at the moment of
> breach, and it is never absorbed into the rule-12 calibration ratio — `COMPUTE_BUDGET
> _CHARTER` §6 keeps waste separately named.**

**THE EXEMPTION IS READ NARROWLY, AND THIS IS THE ONLY THING IT DISPLACES.** It displaces
rule 12's *"an overrun stops the run"* **for cap breaches on 3-D runs, and nothing else.**
It does **not** widen the cap, does not authorise a second run, and does not touch S1, S2,
S3 or S5, **all of which still STOP the level.** It rests on Sanaa's own words and **no
agent message widened it** (CLAUDE.md rule 9).

---

## 11.9 THE GEOMETRY PIPELINE, AND THE THREE DEFECTS IT CAUGHT BEFORE ANY MESH EXISTED

**Registered path**, all three stages required, the later ones REFUSING on the earlier:

```
cases/navier_class/SUBOFF_A1/build_suboff_a1_geometry.py   (Table 1 + Table 2 -> hull.stl, sail.stl)
cases/navier_class/SUBOFF_A1/prepare_geometry.sh           (generate -> surfaceOrient -> surfaceCheck, REFUSES)
cases/navier_class/SUBOFF_A1/build_suboff_a1_mesh.py       (one level; REFUSES over an existing polyMesh)
cases/navier_class/SUBOFF_A1/mesh_level.sh                 (blockMesh -> snappy -> full-flag checkMesh)
```

**`prepare_geometry.sh` REFUSES unless, for BOTH surfaces, `surfaceCheck` prints
`Surface is closed`, `no illegal triangles`, and `consistent normal) : 1`.** Its rc is
**not** consulted — the printed report is.

**What that refusal caught, measured on the first emission:**

| defect | measured | why it matters |
|---|---|---|
| **hull apex fans emitted as zero-area triangles** | `Surface has 256 illegal triangles`, `Number of unconnected parts : 2` — 256 = the azimuthal division count, i.e. one per nose-apex and tail-apex facet | a body of revolution built naively is **OPEN at both ends**, and `snappyHexMesh` then meshes the inside of the hull |
| **knife-edge vertex pairs at ±1.4×10⁻¹⁰ m** on the sail cap near the LE, where the cap ellipse degenerates | `close unconnected points … distance: 2.78e-10` | the two sides of a zero-thickness edge fail to share a vertex, so the surface is **not closed** by a distance 10⁶ times smaller than the finest registered cell |
| **inconsistent surface normals on the sail** | `Number of zones (connected area with consistent normal) : 2` | `snappyHexMesh`'s inside/outside test on an **overlapping-solid union** is unreliable when normals disagree |

**Repairs, all registered in the builder:** proper apex fans oriented upstream at the
nose and downstream at the tail; a coordinate snap at **`SNAP_ABS = 2×10⁻⁷ m = 0.2 µm`**
(**0.13 % of the finest registered cell, 153.7 µm**, so geometrically inert) with
zero-area triangles **dropped and counted, not written**; and `surfaceOrient` against an
external point. **After repair both surfaces measure `Surface is closed`,
`All edges connected to two faces`, `unconnected parts : 1`, `zones … : 1`,
`no illegal triangles`.**

**The union topology, registered so a successor does not "fix" it:** `hull.stl` and
`sail.stl` are **two separately closed solids that overlap** — the sail's lower lid is
buried at `y = 0`, on the hull axis. `snappyHexMesh` keeps only cells reachable from
`locationInMesh`, so **the union is what survives**; no boolean is performed and no
coincident-surface sliver is created. **A successor who "cleans this up" by trimming the
sail to the hull surface will reintroduce exactly the sliver this avoids.**

**Geometry cross-checks, computed and recorded** (`geometry_manifest.json` beside the
STLs): max sail `t/c = 18.1035 %` against §3.2's 18.1 %; hull radius at the sail LE
`0.2536295 m` and at the sail TE `0.2540000 m` (= `R_max`, the sail TE sits on the
parallel middle body); truncated base **full** thickness **1.310895 mm = 0.35592 % of the
368.2999 mm chord**, `1.841 mm` of chord removed. **§3.4's registered 1.311 mm / 0.356 %
is CONFIRMED to 4 significant figures from the rendered equations.**


---

# §12. AMENDMENT — 2026-09-11 — `L1_SHIFT`: A SINGLE-VARIABLE TEST OF ALIGNMENT INVARIANCE, REGISTERED BEFORE IT RUNS

**Written by a cfd `lab-lane`. The document is still a DRAFT and still UNFROZEN; the banner at
the head stands. Nothing above this section was renumbered, reworded or deleted:
`lines whose number changed above this section: 0`.**

**🔴 THE BANNER ABOVE IS STALE AND IS DISCLOSED, NOT EDITED.** It asserts `NO COMPUTE HAS RUN
UNDER THIS DOCUMENT`. **That is no longer true: 372.67 core-min of mesh building has run** —
L1 77.07, L2 228.53, `L1_DECOMP4` 67.07, each from its own `STATUS.mesh`. **The `DRAFT` /
`UNFROZEN` status remains correct** (no solver has been invoked, and §11.0 restates the rule-2
condition as the absence of a *solver result*). It is the compute claim inside the banner that
is false, and it is corrected here rather than silently overwritten.

**WHY THIS IS REGISTERED AT ALL, with no solver involved:** the cfd-supervisor's ruling that
**for a mesh-admission gate, first compute IS the mesh build.** Gate M grades meshes. So a new
mesh built to inform Gate M is compute under this document and gets its prediction and
falsifier written down *before* it runs.

## 12.1 WHAT IS ALREADY MEASURED

| level | cells | min cell determinant | verdict against M-d's floor of `1.0e-03` |
|---|---|---|---|
| **L1** (8 ranks) | 3,268,613 | **8.6227045e-04** | **BELOW — 1 cell** |
| **`L1_DECOMP4`** (4 ranks) | 3,268,643 | **8.6226207e-04** | **BELOW — 1 cell** |
| **L2** | 9,121,237 | **1.5198839e-03** | above |

`L1_DECOMP4` changed the decomposition only — quality controls diffed byte-identical — and
**the mesh genuinely moved**: 30 more cells, 32 fewer layer cells, 85 more faces, 24 more
points, unbalance 0.28860325 vs 0.31631918. **The worst cell did not move**: the determinant
agrees to **five significant figures** (relative difference **9.719e-06**), and max
non-orthogonality (**64.952882**) and max skewness (**2.9132534**) are identical to all eight
digits. **The escaping cell is therefore invariant to PARTITIONING.**

## 12.2 🔴 THE OPEN QUESTION — TWO DIFFERENT INVARIANCES

**Invariance to partitioning is not invariance to alignment**, and conflating them is the same
error §11.7's P2 was written to avoid at the level of refinement. L2 is clean at a finer
resolution, so the geometry admits a clean mesh *somewhere*. What is NOT established is
whether:

- **(A)** ~3.27 M cells is simply a bad **resolution** for this geometry; or
- **(B)** this particular discrete **alignment** of the surface against the octree at 3.27 M
  cells is a bad draw.

## 12.3 THE REGISTERED TEST

> **`L1_SHIFT`: the same nominal refinement as L1, with the background `blockMesh` origin
> shifted by HALF A BASE CELL (39.35 mm, base cell 78.70 mm) in each of x, y and z. The
> surface then intersects the octree at different places at UNCHANGED resolution. ONE
> variable. The generated `meshQualityControls` block is diffed against L1's and the build is
> ABANDONED if it differs. No build script is edited: the case is generated unchanged and only
> that one case's `blockMeshDict` origin is moved. `minDeterminant` is not touched in either
> direction, in either block.**

## 12.4 PREDICTION AND FALSIFIER, BOTH BEFORE THE DATA

| | |
|---|---|
| **PREDICTION (cfd-supervisor's, recorded ahead of the result)** | **The bad cell RETURNS at ≈ 8.6e-04.** Basis: a degeneracy invariant to partitioning to five significant figures reads as the surface and the octree meeting badly at a feature that does not move when the background grid does. |
| **FALSIFIED BY** | the minimum cell determinant at `L1_SHIFT` coming out **≥ 1.0e-03**, i.e. the bad cell gone. |
| **IF FALSIFIED (cell GONE)** | the failure is an **alignment accident**, not a property of the resolution. L1 is recoverable, `L1_SHIFT` replaces it, and the downward triple **{~1.17 M, `L1_SHIFT`, L2}** becomes live with equal delivered ratios of **1.4079**. |
| **IF CONFIRMED (cell RETURNS)** | the **resolution** is the problem, not the draw. **SUBOFF then has no admissible family on this geometry at this mesh class** — a real finding about the case and about `snappyHexMesh`, not a failure of method. |

**Both outcomes are decisive and neither requires moving a threshold.**

## 12.5 🔴 THE LIMIT, REGISTERED BEFORE THE RESULT SO IT CANNOT BE RELAXED AFTER

> **ONE SHIFT. If `L1_SHIFT` also fails, there is NO second shift and no third.**

**Shifting the origin until one cell clears a threshold is fitting a mesh to a gate — the
mirror image of fitting a gate to a mesh, and no better.** The same reasoning already retired
the option of tuning `nSmoothScale` / `errorReduction` until the cell cleared. **One shift is a
test; a series of shifts is a SEARCH, and a search for a passing mesh is not verification.**

This limb is registered **before** the data precisely because a second shift would feel like a
continuation of the same experiment rather than a new one, **which is how a search disguises
itself as a test.**

## 12.6 COST

**~77 core-min estimated**, scaled from L1's measured 77.07 (578 s × 8 ranks) at the same cell
count. Against §8's L1 sub-cap of **2,000 core-min**, with **372.67** spent on mesh building to
date. `cost_basis`: **DERIVED from this case's own measured L1 build, not from a rate card.**

*§12 ends. No gate, threshold, cap or label above is altered. No verdict is issued here.*
