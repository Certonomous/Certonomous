# CRM WING-BODY (D8G) — DPW-6 TRANSONIC VALIDATION ACT, PRE-REGISTRATION

**Item:** `CRM_WB_D8G`  **Team:** cfd  **Lane:** `lab-lane` (32 ranks, ≤200 GB)
**Supervisor:** `cfd-supervisor`
**Authority:** Sanaa, `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
§C (byte-exact run instruction, sections 1–10) and §A (32-rank lane); unblocked as a
newly registered run by her ~19:40Z CRM ruling in
`docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`.

**STATUS: FROZEN AT THE COMMIT THAT INTRODUCES THIS FILE.**
No solver has run under this document at the moment of the freeze. No coefficient exists.

**THIS IS NOT THE WING-ALONE CASE.** CRM wing-alone L2R stays `GATE FAIL` as graded and is
not re-queued (Sanaa, ~21:00Z addendum). Nothing here inherits its registration.

---

## 0. WHAT GATES, IN ONE PARAGRAPH

CL, CD (pressure/viscous split) and CM on the CRM **wing-body**, half model, at
**M∞ = 0.85, Re = 5.0×10⁶ on c_ref, fully turbulent**, on the DPW-6 **aeroelastically
deformed ae2.75°** committee geometry, against **NTF Test 197** as primary reference and
**Ames Test 216** as secondary, banded by the **DPW-6 participant scatter** read
numerically from Tinoco et al. Primary gate at **fixed α = 2.75°**; secondary at the
**CL = 0.500 ± 0.001** trimmed point by α-search. Cp at the **nine NTF pressure rows**.
Verdicts are `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` only.

---

## 1. SOURCES — ON DISK, TITLE-PAGE VERIFIED, HASHED

Retrieval into the box only. **Nothing leaves the box** (rule 8). **Submissions are parked**
(rule 7): nothing here is sent, filed, registered or posted, and no steward is contacted.

### 1.1 Experimental data — `/home/ubuntu/crm-data/experimental/`

| artifact | bytes | sha256 |
|---|---|---|
| `NTF197Data.zip` | 5,973,027 | `6f2ef0d10c4e2f1b037461f874ed7f055d39ccab6985e331e45d7146da1ca95d` |
| `CRM-NTF-Test-197-Run-Log1.xls` | 96,256 | `997df0ea3f7a2485598fafe1a27356ff467daa75ce7d74f6f0ad9c42c6fdc34b` |
| `CRM-Ames-Test-216-Run-Log1.xls` | 79,360 | `a908e664b1dd1dc61bc95c33b0a8620e679fc8ab48d0206e6a7f8ee5f3e0dfb5` |
| `T197-Run-Log-final.pdf` | 2,781,360 | `ce5dba0218c116f2eb49cb32bc7beff0e8cc38222404f15c0f2be627f4e8e093` |
| `NTFT197VarNames.v2.xls` | 38,400 | `43bf523dc80dd99d91987e1023b4828bbb4a7e995d7e5ea6e6b587ad26db4978` |

`NTF197Data.zip` unpacks to **196 files in two correction families**: `TWICSCorr/` (98 runs)
and `ClassicalCorr/` (98 runs). Columns include `ALPHA MACH CREYN CL CD CM` and the nine
pressure rows `CPA…CPI` with their `XOC` chord fractions.

### 1.2 Committee grids — `/home/ubuntu/crm-data/grids/`

Retrieved from **`https://dpw.larc.nasa.gov/DPW6/`**. *The host named in Sanaa's §C.1,
`aiaa-dpw.larc.nasa.gov`, is **NXDOMAIN** — the archive moved; the workshop pages survive at
`https://www.aiaa-dpw.org/Workshop6/`.* Both recorded so a later reader is not sent to a dead
host.

### 1.3 Documents

| filed path | identity read from its OWN first page |
|---|---|
| `docs/papers/benchmark_test_cases/tinoco_2017_dpw6_summary_crm_cases_2_to_5.pdf` | "Summary of Data from the Sixth AIAA CFD Drag Prediction Workshop: CRM Cases 2 to 5", Tinoco, Brodersen, Keye, Laflin, Feltrop, Vassberg, Mani, Rider, Wahls, Morrison, Hue, Gariepy, Roy, Mavriplis, Murayama |
| `…/rivers_2011_crm_ntf_ames_experimental_investigations.pdf` | "Experimental Investigations of the NASA Common Research Model in the NASA Langley National Transonic Facility and NASA Ames 11-Ft Transonic Wind Tunnel (Invited)", Rivers & Dittberner |
| `…/rivers_2019_crm_history_and_future_plans.pdf` | "NASA Common Research Model: A History and Future Plans", Rivers |
| `…/rivers_2012_crm_support_system_effects.pdf` | "Support System Effects on the NASA Common Research Model", Rivers & Hunter |
| `…/rivers_2012_crm_support_system_and_wing_twist.pdf` | "Further Investigation of the Support System Effects and Wing Twist on the NASA Common Research Model", Rivers, Hunter & Campbell |
| `/home/ubuntu/crm-data/_fetch/DPW6_gridding_guidelines_2015-08-28.pdf` | "DPW-VI: Baseline Grid Families" / "DPW-VI: Gridding Guidelines" |
| `/home/ubuntu/crm-data/_fetch/DPW6_Test_Cases_2016-04-21.pdf` | "DPW-VI: Requested Test Cases" |

sha256 of the five filed papers: `68a74dc7…1d374`, `2352dda5…b0984a`, `f3621128…52192b`,
`a665693b…10c45a`, `a585c839…f23000` (full values in §12).

**CITATION DELTAS, STATED NOT SMOOTHED.** Sanaa cited Tinoco et al. *J. Aircraft* 55(4)
1352–1379 (2018); `arc.aiaa.org` returns HTTP 403 to this box, so the NASA-hosted manuscript
of the same work (NTRS 20170001397, report NF1676L-26060) is used. She cited Rivers &
Dittberner *J. Aircraft* 51(4) 1183–1193 (2014); the reachable version is **AIAA 2011-1126**
(NTRS 20110003168), same authors, same two tunnel entries. She cited Rivers AIAA **2019-3725**;
the NTRS record for that title is **AIAA 2019-2188** (NTRS 20200002395). Each substitution is
the same work in a reachable venue and is carried onto the certificate.

---

## 2. THE `[verify]` ITEMS — RESOLVED FROM PAGES, INCLUDING THREE THAT CAME OUT AGAINST THE INSTRUCTION

Sanaa marked these `[verify]` because she expected some to be wrong. Three are.

### 2.1 CONFIRMED as written

- **Nine pressure rows.** CRM site, *Model Description*: "291 pressure orifices located in 9
  span-wise wing stations (η = 0.131, 0.201, 0.283, 0.397, 0.502, 0.603, 0.727, 0.846, and
  0.950)". Her list is exact.
- **Reference quantities.** `www.aiaa-dpw.org/Workshop6/DPW6-geom.html`, "CAD Models of Common
  Research Model": S = 594,720.0 in², c = 275.80 in, b = 2,313.50 in, moment reference
  (X,Y,Z) = (1,325.90, 468.75, 177.95) in. All four digit-for-digit as she wrote them.
  **Independent cross-check:** the NTF model-scale values on the CRM site (S = 3.011 ft²,
  b = 62.47 in, c = 7.447 in) imply a scale of **2.700 %** on all three, agreeing to four
  significant figures.
- **Deformed α values.** DPW-6 Case 3: "AoA=[2.50, 2.75, 3.00, 3.25, 3.50, 3.75, 4.00]
  degrees" — 2.50 to 4.00 in 0.25 steps, as she expected. The grid archive carries
  `ae2p50 … ae4p00`.
- **Trip at 10 % chord.** CRM site NTF page: "These trip dots were installed at 10% chord."
- **Grid units inches.** Node coordinates read O(10³) in, e.g. (1432.94, 388.99, 169.92),
  full-scale. Converted by exactly **0.0254**; §4 converts the reference quantities identically.

### 2.2 🔴 CORRECTED — her registered value was wrong, corrected from a page

| item | as registered by Sanaa | what the page says | source |
|---|---|---|---|
| farfield extent | "about 100 c_ref" | **"Farfield Boundary > 100*Semispans. Note: This is Farther than before, which was 100*Crefs"** — i.e. 115,675 in, ≈4.2× farther | DPW-6 gridding guidelines, p.12 |
| grid sizes | "about 2 M, 6 M, 16 M cells" | committee table in **M-DOF**: WB T ≈ 20, C ≈ 30, M ≈ 45, F ≈ 70, X ≈ 100, U ≈ 150, growing ~1.5× per level (~1.15× linear) | DPW-6 gridding guidelines, p.10–11 |
| deflection source | "measured static wing deflection … (from the NTF test)" | **"AoA Sweep with ETW Deflections"** | DPW-6 Case 3 |

Her 2/6/16 M figures correspond to the **DPW-5** family (hex 0.639 / 2.157 / 5.112 / 17.25 M),
which is a **different workshop and the UNDEFORMED wing** — unusable for a gate on the
deformed geometry. Recorded so nobody re-derives the error.

### 2.3 Formats provided

NASA GeoLab supplies **UGRID** (`.lb8.ugrid`) with `.mapbc` patch identity at T/C/M/F/X/U, and
**CGNS** in a parallel tree. Boeing Babcock supplies **UGRID** (`.b8.ugrid`) at T/C/M/F/X/U and
**no `.mapbc`**. CFSE supplies CGNS but for **WBNP**, not WB. Boeing Serrano supplies overset,
unusable here. CARDC supplies a single C-level CGNS, an incomplete family.

---

## 3. THE GRID FAMILY, AND WHY IT IS NOT THE ONE A CELL COUNT WOULD SUGGEST

The committee sizes its family in **M-DOF**. DOF means **nodes** for a node-centred solver and
**cells** for a cell-centred one, and the two submitted families bear this out exactly:

| family | solver convention | "Tiny" |
|---|---|---|
| NASA GeoLab (VGRID, node-centred) | nodes | 20,474,821 **nodes** — but **83,598,506 cells** |
| Boeing Babcock (`Unstructured_CC`, cell-centred) | cells | **20,657,615 cells** |

**OpenFOAM is cell-centred.** Running GeoLab would put us at 83.6 M-DOF at the rung labelled
"Tiny" — between the committee's Fine and Extra-Fine, four levels finer than intended.
**The Boeing Babcock family is therefore the correct committee family for this solver**, and it
is the registered one.

| level | cells | nodes | boundary faces | file sha256 (first 16) |
|---|---|---|---|---|
| T (Tiny) | 20,657,615 | 7,957,700 | 349,856 | see §12 |
| C (Coarse) | 26,271,819 | 10,235,358 | 446,830 | see §12 |
| M (Medium) | 33,683,206 | 13,197,852 | 571,259 | see §12 |
| F (Fine) | 43,126,748 | 17,104,710 | 737,946 | registered successor |

Counts read from each file's own header and **confirmed by byte arithmetic against the
published file size**: GeoLab T and C predict their size **exactly**; every Babcock level comes
out **+4 bytes**, a constant trailing field (value `0x000022d3`) present on all four levels,
with the prism block ending exactly where predicted and the final prism's indices in range —
a writer quirk, diagnosed, not waved off.

### 3.1 🔴 THE REFINEMENT RATIO IS WEAK AND THAT IS REGISTERED **BEFORE** ANY RUN

Babcock grows **1.27–1.28× in cells per level**, not the specified 1.5×. Consecutive levels
therefore give **r = N^(1/3) ratio ≈ 1.086**.

> **REGISTERED CONSEQUENCE.** At r = 1.086 the level-to-level differences may be comparable to
> the iterative error, and the requirement that iterative error be ≥10× smaller than the level
> differences (§7) may not be attainable. **If the triple is not `CONVERGING`, the row is
> `NOT A RESULT` under standing rule 5, whatever its value, and no GCI is quoted.** This is
> written before the first solve precisely so it cannot be discovered afterwards.

- **Registered graded triple: T / C / M**, as Sanaa's §5 wrote it, r ≈ 1.086.
- **Named alternative triple: T / M / X**, N-ratios 1.63 and 1.67, **r ≈ 1.177**, cost in §9.
- **Registered successor: F** (43.1 M cells) if the observed order is out of range.

**Changing which levels constitute the graded family is a change to her run plan and is hers
to make.** Both options are registered here with their ratios and costs; neither is
substituted silently.

### 3.2 PATCH IDENTITY — A METHOD VALIDATED ON A LABELLED CASE, THEN APPLIED

Babcock publishes no `.mapbc`, so patch identity would otherwise be inference. It is not.

1. **The geometric classifier (Sym / Far / WALL) was run blind against the GeoLab Tiny grid,
   where `.mapbc` documents all 45 tags, and scored: 45 correct, 0 mismatched.**
   *On its first run it scored 39 wrong out of 45 — a tuple-unpacking slip thresholded on mean
   radius instead of max|y|, calling every wall patch "symmetry". On Babcock, which has no
   labels to contradict it, that bug would have handed the forces functionObject an **empty
   wall set** and produced a near-zero CD from a cleanly converged run. It was caught only
   because a labelled grid existed to be wrong against. Recorded here and on the certificate.*
2. **The wall tags are then identified by wetted area against GeoLab's documented components**,
   not by geometry:

   | Babcock tag | area (in²) | GeoLab documented component | area (in²) | agreement |
   |---|---|---|---|---|
   | 1 | 825,616.8 | **B** (fuselage), 30 tags | 825,838.8 | 0.027 % |
   | 2 | 534,632.6 | **W** (wing), 9 tags | 534,637.7 | 0.001 % |
   | 3, 4 | farfield | — | — | — |
   | 5 | symmetry | — | — | — |

   **Registered patch names: `body`, `wing`, `farfield`, `symmetry`.**
   The forces functionObject integrates **exactly `body` and `wing`**.

### 3.3 SYMMETRY-PLANE TOLERANCE — SET FROM A MEASUREMENT, NOT A DEFAULT

Measured planarity, max |y| over the symmetry tag's face centroids:

- GeoLab Tiny: **9.80×10⁻¹² in**
- **Babcock Tiny: 4.621×10⁻⁶ in = 1.174×10⁻⁷ m**

Babcock's plane is five and a half orders looser, and sits at the same order as the
**9.49×10⁻⁶** that silently lost **832 root-plane faces** on the CRM wing-alone case under a
1×10⁻⁹ tolerance. **The tolerance is therefore taken from the measurement**
(10× planarity, floored at 10⁻⁹ × model length): **2.349×10⁻⁴ in** on Babcock Tiny. The face
count the tolerance admits and rejects is recorded per level in each level's
`conversion_record.json`.

### 3.4 ADMISSIBILITY — TWO-TIER, QUALITY DISCLOSED NOT GATED

`checkMesh -allGeometry -allTopology` on every level; **max non-orthogonality and max skewness
are DISCLOSED beside the bands**, never used to reject a committee grid. Wall treatment is
**wall-resolved (y⁺ ≈ 1), no wall functions**; y⁺ per patch reported after the first converged
solve. **No in-house mesh is built for this act.**

### 3.5 THE IMPORT PATH IS AN INSTRUMENT AND IS VALIDATED AS ONE

`cases/CRM_wingbody/tools/ugrid_to_gmsh.py` → `gmshToFoam` → `transformPoints` (×0.0254).
Face extraction, internal-face matching, ownership and upper-triangular ordering are delegated
to `gmshToFoam`, a tested OpenFOAM utility; the converter emits only nodes, cells and named
physical surfaces. Cell orientation is **computed, never assumed** (signed volumes; 3,944
pyramids required flipping on Babcock Tiny, tets and prisms none).

#### 🔴 A SILENT DEFECT THE INVARIANTS CAUGHT, RECORDED BECAUSE IT ALMOST SURVIVED

The AFLR3/UGRID pyramid element does **not** store its apex last. Boeing's file stores it in
**slot 3**: `(base, base, APEX, base, base)`. Assuming the Gmsh convention (apex last) produced
a mesh that `gmshToFoam` accepted, that passed *"Cell to face addressing OK"*, *"Upper
triangular ordering OK"* and *"Topological cell zip-up check OK"*, and in which the patch face
counts for `body`, `wing` and `farfield` matched the source **exactly** — while **54,818
interior faces were silently promoted to walls**, located at x ∈ [134, 1660] in, y ∈ [0, 394] in,
i.e. **inside the wing-body junction region whose separation this act predicts on (§6b)**.

It was found by the boundary-face round-trip: OpenFOAM reported 404,672 boundary faces against
the source's 349,856, and the excess decomposed as 18,266 quads and 36,552 triangles = 2 and 4
per pyramid over ~9,133 of the 9,138 pyramids.

**The apex slot was then established from the file, not assumed:** taking the apex as slot 3
leaves a base that matches a neighbouring prism quad face for **9,128 of 9,138** pyramids (2
more on a boundary quad, 4 quads shared between two pyramids), while **every other apex choice
matches zero**; and only that choice leaves the remaining four nodes **planar** (median
out-of-plane 5.3×10⁻³ in, versus 0.42–0.68 in for the alternatives). The base is then ordered
cyclically in its own best-fit plane, giving a convex non-self-intersecting quad on
**9,138/9,138**.

**REGISTERED ACCEPTANCE TEST, every level:** `nFaces` summed over the named patches must equal
the source's boundary-face count **exactly**, and the `defaultFaces` patch must be **empty or
absent**. A non-empty `defaultFaces` refuses the level.

*A second instrument defect was caught the same way: `transformPoints` changed syntax in
v2606 and failed with "Expected 0 arguments but found 1" while the driver recorded only its
return code and carried on, which would have left the mesh in **inches** — a 0.0254³ = 1.6×10⁻⁵
error in every volume and a factor 39.4 in every length. The driver now **fails closed** on it.*

- **PLANTED CONTROL (rule 3) — PASS.** Into a *copy* of Babcock Tiny: a node-coordinate
  perturbation of **1.234×10⁻³ in** on node 4,000,000 and a boundary tag **2 → 99** on face
  123,456. The reader saw the coordinate delta as 1.2340000000108×10⁻³, saw the tag as 99
  against a clean 2, saw tag 99 appear in the tag set, and saw **exactly one** node differing.
  A zero from this reader is therefore evidence.
- **VOLUME BY TWO INDEPENDENT PATHS.** V = ⅓∮x·n dA over the **source file's boundary faces
  alone** (never looks at a cell) vs OpenFOAM's volume **summed over cells** (never looks at
  the source). On the synthetic selftest these agree to **0.000×10⁰** relative, with max cell
  openness 0. Required per level: **relative difference < 1×10⁻⁶**, recorded.
- **BOUNDING BOX.** GeoLab Tiny y-extent = 115,675.00 in = **exactly 100 × semispan**
  (b/2 = 1156.75 in), which confirms units, scale and endianness in one number.
- **CROSS-GRID INVARIANT.** Total wetted area, two independently generated committee grids:
  GeoLab 1,360,476.5 in² vs Babcock 1,360,249.4 in² — **0.017 %**.

### 3.6 ACCEPTANCE TEST — TINY LEVEL, RESULT AS AT THE FREEZE

**No solver has run.** This is mesh preparation, recorded before the freeze so the gate cannot
later be said to have been chosen around it.

`Boeing.Babcock.WB.ae2.75deg.UnstrMixedElement.T.b8.ugrid` → polyMesh, 20,657,615 cells,
48,132,295 faces, scaled by 0.0254 (`transformPoints -scale 0.0254`, "Scaling points uniformly
by 0.0254", End).

| acceptance test | required | measured | verdict |
|---|---|---|---|
| named patches sum to source boundary faces | exactly 349,856 | **349,856** | **PASS** |
| `defaultFaces` | empty or absent | **absent** | **PASS** |
| `body` / `wing` / `farfield` / `symmetry` | 57,656 / 239,437 / 2,480 / 50,283 | **identical** | **PASS** |
| volume, two independent paths | rel. diff < 1×10⁻⁶ | **9.83×10⁻⁷** | **PASS** |

Volumes: source-boundary divergence integral **1.251048770×10¹¹ m³** (never looks at a cell)
against OpenFOAM's sum over 20,657,615 cells **1.251050000×10¹¹ m³** (never looks at the
source). The residual is at the limit of checkMesh's six-figure printing.

**Two-tier quality, DISCLOSED NOT GATED** (committee grid): max non-orthogonality **89.46**
(average 22.80); max skewness **7.96**, 725 highly-skew faces; max aspect ratio **4436.7** over
18,459 cells; min cell volume 2.994×10⁻¹² m³, max 1.999×10⁷ m³. The high aspect ratio and the
5,896,299 small-determinant cells are the expected signature of a **wall-resolved y⁺ ≈ 1 prism
layer** and are **not** grounds to reject a committee grid under the two-tier standard. y⁺ per
patch is reported after the first converged solve.

---

---

## 4. REFERENCE QUANTITIES AND FREESTREAM STATE — COMPUTED, WRITTEN IN, READ BACK

Converted by exactly **0.0254**, identically to the grid.

| quantity | inches | metres |
|---|---|---|
| c_ref | 275.80 | **7.00532** |
| b | 2313.50 | **58.7629** (semispan 29.38145) |
| S_ref full-span | 594,720.0 in² | 383.6895552 m² |
| **S_ref half-model (the solver's value)** | 297,360.0 in² | **191.8447776 m²** |
| moment reference | (1325.90, 468.75, 177.95) | **(33.67786, 11.90625, 4.51993)** |

Freestream, γ = 1.4, R = 287.058 J kg⁻¹K⁻¹, **T∞ = 310 K [registered by Sanaa]**
*(DPW-6 states T = 100 °F = 310.93 K; her registered value stands and the difference is
recorded)*:

| quantity | formula | value |
|---|---|---|
| a | √(γRT) | **352.9634145 m s⁻¹** |
| U∞ | 0.85 a | **300.0189024 m s⁻¹** |
| μ | Sutherland(T∞) | **1.892942218×10⁻⁵ Pa s** |
| ρ | Re μ /(U∞ c_ref) | **0.04503298815 kg m⁻³** |
| p∞ | ρ R T∞ | **4007.394649 Pa** |
| ν | μ/ρ | **4.203456834×10⁻⁴ m² s⁻¹** |

**Closure checks:** ρU c_ref/μ = **5,000,000** (target 5.0×10⁶); U/a = **0.85** (target 0.85).
All four values are written into the case files and **read back onto the screen** before the
first iteration, per her §3.

---

## 5. THE GATES AND BANDS — FROZEN, WITH THE WIDTH CONVENTION STATED AND CONVERTED ONCE

**Every published figure below is labelled FULL WIDTH or HALF WIDTH and converted once,
visibly.** A band whose width convention is unstated can be halved or doubled after the answer
arrives.

### 5.1 CD — from the paper

Tinoco p.13, parsed by grid family: *"The solutions based on the unstructured grids show a
**6 to 8 count spread**"* — a **SPREAD, i.e. FULL WIDTH**. Our family is unstructured.

> Taking the worst case, **8 counts full width → HALF WIDTH ±4 counts = ±0.0004 in CD.**
> **REGISTERED CD BAND: ±0.0004.**
> *(Sanaa's fallback ±0.0006 is a HALF width, i.e. 12 counts full width. The paper-derived
> band is tighter, and per her §4 the paper governs where a number can be read.)*

Context recorded, not used as the gate: p.12, *"the bulk of the results converge to a band
about 5-10 counts wide"* across all families.

### 5.2 CL and CM — 🔴 THE PAPER'S NUMBER IS DECLINED, AND WHY

Tinoco p.14 gives spreads only at the **worst** angle: *"At 4° angle-of-attack the value of
lift coefficient varies by **0.063** and the spread in pitching moment coefficient is
**0.045**"* (21 solutions, outliers removed). Both are **FULL WIDTHS** → half widths ±0.0315
and ±0.0225.

> **THESE ARE NOT USED.** Our gate is at **2.75°**, and the paper states explicitly that the
> spread **grows** with angle of attack. Importing the 4° spread would hand this act a band
> roughly three times wider than the condition has earned, **in our favour**. Declining a
> tolerance that would help us is the point.
>
> The per-α statistics live in the paper's Figs. 22 and 30 (images, not text). The proper
> source is its **Ref. 74, Derlaga & Morrison**, cited as **"AIAA-2017-XXX"** — the number was
> unassigned at print and the paper is not on NTRS. **Pending** at the freeze.
>
> **REGISTERED CL BAND: ±0.01. REGISTERED CM BAND: ±0.01.**
> **Both LABELLED A LAB JUDGEMENT** (Sanaa's declared fallback), with the 4° figures printed
> beside them on the certificate and one sentence saying they were available and were not used.
> If Derlaga & Morrison is obtained before the first graded row, it supersedes by dated
> addendum; it cannot be substituted after a row is graded.

### 5.3 Cp at the nine rows — 🔴 TWO DIFFERENT QUANTITIES, ONLY ONE GATES

- **THE DATA'S OWN ERROR BAR: ±0.0026.** CRM site, *Model Description*: ESP modules accurate to
  "+/- 0.015 psi … no more than +/- 0.0026 in terms of Cp". This is the **instrument's
  uncertainty on a single orifice** — how well the tunnel knows its own number. **It is drawn
  on every Cp plot and stated on the certificate. IT DOES NOT GATE.**
- **THE GATE BAND: the DPW-6 participant scatter on Cp at each row**, which is a
  CFD-versus-experiment comparison tolerance and must also carry closure choice, grid level,
  the deformed-geometry mismatch and the trip. **Fallback, if no number can be read from the
  pages: ±0.05 away from the shock and shock position ±0.03 c, LABELLED A LAB JUDGEMENT.**

> Grading nine rows against ±0.0026 would manufacture a `GATE FAIL` from a millimetre of shock
> position and would report a failure of the tolerance rather than a result about the flow.
> **±0.0026 is the data's error bar; the participant scatter is the gate.**

### 5.4 🔴 A DISCLOSED WEAKNESS IN THE BAND'S CONSTRUCTION

The registered construction (Sanaa's §4) centres the band on the **tunnel** value but takes its
width from the **participant scatter**, which measures **code-to-code** disagreement, not
CFD-versus-tunnel disagreement. These are different populations. **The gate is hers and stands
as written; the mismatch is recorded here and on the certificate** so no reader mistakes the
band for an experimental uncertainty.

### 5.5 Verdict rule

For Q ∈ {CL, CD, CM}: `PASS` iff |Q_cfd − Q_NTF| ≤ band; else `GATE FAIL`.
**Any §7 precondition failing, or a non-`CONVERGING` triple, makes the row `NOT A RESULT`,
which overrides both** (rule 5). CD is reported in counts (1 count = 1.0×10⁻⁴) with the
pressure/viscous split. Ames Test 216 is reported as secondary with the tunnel-to-tunnel
difference disclosed.

---

## 6. THE THREE REGISTERED PREDICTIONS — EACH ABLE TO FAIL

**(a) CM sits nose-down of the tunnel by roughly 0.03, because the NTF data are not
support-corrected.**
**The check Sanaa asked for is done.** The CRM site's NTF page lists the corrections applied:
upflow 0.092°–0.173° and *"Classical wall corrections accounting for model blockage, wake
blockage, tunnel buoyancy, and lift interference"*. **Support interference is not among them**,
and the model is **blade-sting mounted**. Independently, Tinoco p.13: *"the solutions are
indicating … a more negative (nose down) pitching moment at a given lift coefficient than
indicated by the test data. Some of this level difference could be due to the lack of mounting
system corrections to the wind tunnel data."* Magnitude quantified in the two 2012 Rivers
support-system papers.
**FAILS IF** the measured ΔCM is outside 0.03 ± 0.02 nose-down, or has the opposite sign.

**(b) The wing-body junction separation bubble at the trailing edge depends on the closure.**
**FAILS IF** the SA and SST bubble streamwise extents at α = 2.75° on Coarse and Medium agree
within 5 % of local chord, i.e. the closure does not move it.

**(c) Fully turbulent CFD gives higher viscous drag than the tripped model.**
**FAILS IF** the computed viscous CD is at or below the tunnel-implied value.

---

## 7. COMPLETION, CONVERGENCE AND STOP RULES

**Convergence:** residuals below 1×10⁻⁶ on density and momentum **or** five orders from
initial; **CL stationary within 0.0002 and CD within 0.00002** (two tenths of a count) over the
last 500 iterations; cap **6,000 iterations per level**; linear-solver tolerance strictly
tighter than the stationarity gate.

**Iterative-vs-discretisation:** iterative error must be **≥10× smaller** than the level
differences, else the triple is not `CONVERGING` → `NOT A RESULT` (§3.1).

**Initialisation:** freestream on Tiny; every finer level from the **interpolated coarser
solution** (`mapFields`), registered as continuation.

**Stop rules (hers, §7.7):** CL oscillating with a fixed period on Medium → **mark,
time-average, disclose**, not a silent average. A **junction-region residual plateau is a known
feature, not a stop**, provided CL and CD are stationary. From the general rules: an
**18-iterations-in-6-hours stall is a MESH DEFECT signature → stop and fix, never wait.**
One registered change per run; two stops on one cause → climb mesh → numerics → model.

**Checkpointing:** every **30 minutes**, `purgeWrite 2`; `writeInterval` in iterations set so it
never exceeds 30 min at the measured rate, **every 200 iterations until the rate is measured**.

**Launch:** through the **runner only** — a hand launch is not a case (her item 19). Detached,
parented to init, **as `ubuntu`, never root**. Declared ranks and declared memory footprint
checked against `MemAvailable`. A MemAvailable guard is a physics guard and is permitted.

**NO CAP KILLS ANYTHING** (Sanaa's directive #17, ruled four times). The cap is **registered**;
if crossed the run is graded **`NOT A RESULT`** and the cap is never raised.

---

## 8. RUN PLAN

1. **Bug check**, all levels: `checkMesh` with two-tier disclosure; dictionaries; patch and
   reference quantities read back; dead-lever audit; forces functionObject reading **exactly**
   `wing` and `body` with the registered S_ref (half-model), c_ref and moment centre; **planted
   force perturbation detected, comparator refuses if it cannot see it**.
2. **Smoke:** Tiny, α = 2.75°, **300 iterations**. Registered predictions: CL rising toward
   0.45–0.55; CD falling toward 0.02–0.03; **no negative densities**; cost per iteration in
   band. *The smoke's measured rate replaces the §9 estimate before the ladder launches.*
3. **Ladder:** Tiny → Coarse → Medium, each from the interpolated coarser solution; observed
   order and family band on CL, CD, CM.
4. **Second closure:** SST on Coarse and Medium at α = 2.75°; junction bubble compared;
   difference recorded as **model-form spread**, not as error.
5. **Trim:** α = 2.5° and 3.0° on Coarse, linear interpolation to CL = 0.500, one Medium solve
   at the interpolated α; CD and CM at CL 0.5 reported with the trim disclosed.

**Rank allocation departs from her §7 and the reason is registered.** Her 8/16/32 ranks assumed
2/6/16 M cells. The committee grids are 20.7/26.3/33.7 M, so Tiny at 8 ranks would be
2.58 M cells/rank. **All levels run at the lane's 32 ranks**, giving 0.65/0.82/1.05 M
cells/rank.

---

## 9. COST — REGISTERED BEFORE THE RUN

Unit: **core-minutes** = wall s × ranks ÷ 60. Rate **$0.0513/core-h**, c7a.4xlarge.
**`cost_basis`: REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5).

Estimate at 32 ranks, 6,000 iterations, from a nominal 10–20 s/iteration at ~0.65–1.05 M
cells/rank (**an estimate, not a measurement — superseded by the smoke's measured rate**):

| level | cells | est. wall | est. core-min | est. $ (derived) |
|---|---|---|---|---|
| T | 20.66 M | 17–33 h | 32,600–63,400 | $28–54 |
| C | 26.27 M | 21–42 h | 40,300–80,600 | $34–69 |
| M | 33.68 M | 27–53 h | 51,800–101,800 | $44–87 |
| **primary ladder** | | | **124,700–245,800** | **$107–210** |
| SST on C+M | | | 92,100–182,400 | $79–156 |
| trim (2×C, 1×M) | | | 132,400–262,000 | $113–224 |
| T/M/X alternative triple (X = 56.4 M) | | | +86,800–170,600 | +$74–146 |

**Registered cap: 3× the estimate**, i.e. 1,048,500 core-minutes for the full act. Crossing it
grades the affected row `NOT A RESULT`; **nothing is killed on a cap.** Estimate-versus-actual
lands in `docs/COST_CALIBRATION.md` at every process completion (rule 12).

Memory: declared **≤200 GB** for the lane; measured footprint per level recorded and checked
against `MemAvailable − 4 GB` before each launch.

---

## 10. DELIVERABLES

Forces table (CL, CD pressure/viscous/total, CM) on three levels with the family band against
NTF primary and Ames secondary, DPW scatter drawn as the band, trimmed CL = 0.5 point
alongside; Cp overlays at the nine rows vs NTF taps at α = 2.75° on Medium **with the ±0.0026
data error bar drawn**; shock position per row with measured value and band; family figure vs
N^(−2/3) with observed order and GCI **only if the triple is `CONVERGING`**; fields (upper-surface
Cp shock line, junction region SA vs SST side by side, skin-friction lines, symmetry-plane Mach,
wing-tip vortex); convergence histories with the stationarity window; mesh figures at the
**Tiny** level with the two-tier caption; y⁺ map on the wing; compute table; certificate.

**ParaView at every completion** (her ~20:30Z addendum): saved beside the run as each run
completes, never batched — the **Coarse** level's mesh (Medium if Coarse has not converged)
carrying the **fields from the finest completed level available at that time**.

---

## 11. WHAT THIS ACT DOES NOT CLAIM

A trimmed aircraft (no tail), transition, flutter or buffet onset, the Fine/Extra-fine/Ultra-fine
levels, DPW-7 conditions, agreement with any participant's result other than through the scatter
band, aeroelastic deflection at any α other than 2.75°, unsteadiness, or support interference
beyond what the file header's corrections cover.

---

## 12. HASHES

Grid files, `/home/ubuntu/crm-data/grids/` — recorded per level in each level's
`conversion_record.json` alongside cells, nodes, boundary faces, byte-arithmetic difference,
symmetry planarity and tolerance, per-patch source area, and the two independent volumes.

Papers, `docs/papers/benchmark_test_cases/`:

```
68a74dc76d4328ee34883285a1c697b854e35e6eeb742efd28ebadb4b731d374  tinoco_2017_dpw6_summary_crm_cases_2_to_5.pdf
2352dda58912bb71894fce7b93de7d4b44f3e3282cb50bc8c53ca3365fb0984a  rivers_2011_crm_ntf_ames_experimental_investigations.pdf
a585c83970ee015fde421516c42c39be56c96267af452245c12a2ed725f23000  rivers_2012_crm_support_system_and_wing_twist.pdf
a665693bc70308deb1577d4d1087656e4cec00a647b56ba937be08bb4d10c45a  rivers_2012_crm_support_system_effects.pdf
f3621128c354805996b04a74020365fc7470e1ff991fc0c0a0ac3d78cc52192b  rivers_2019_crm_history_and_future_plans.pdf
```

Comparator and converter, graded at the commit that freezes this file:
`cases/CRM_wingbody/tools/ugrid_to_gmsh.py`, `…/convert_level.py`,
`…/selftest_ugrid_to_gmsh.py`.

---

# ADDENDUM 1 — 2026-09-12, RATE PROBES. Version 1.1.

**lines whose number changed above this section: 0**

**This addendum alters no gate, no threshold, no cap and no label.** It records a measurement
taken after first compute and registers three diagnostic probes that grade nothing. Every gate
and band in §5, every prediction in §6, and the cost cap in §9 stand exactly as frozen at
`6165680b`.

## A1.1 MEASURED BASELINE RATE — the §9 estimate is superseded by measurement

Tiny (20,657,615 cells), 32 ranks, SA, α = 2.75°, from uniform freestream:

| | |
|---|---|
| ExecutionTime, iteration 1 | 267.81 s |
| ExecutionTime, iteration 2 | 548.50 s |
| **measured rate** | **280.7 s/iteration = 149.7 core-min/iteration** |

Against the §9 nominal of 10–20 s/iteration. **Reported GROSS, not cleaned:** host load average
was 76.8 on 96 cores with 35 foreign solver ranks live, so contention inflates the wall figure.

**Consequences, stated rather than absorbed.** The 300-iteration smoke is ~22 wall-hours and
~44,900 core-minutes, which is **above its own registered cap of 9,600** — that run is therefore
`NOT A RESULT` if executed as registered, and the cap is not raised (§7). Tiny to the 6,000
iteration cap is ~19 days, not the 17–33 hours on which the grid level was ruled.

## A1.2 THE CAUSE IS A STALLED LINEAR SOLVER, NOT THE CELL COUNT

Momentum, enthalpy and nuTilda each converge in **one** linear iteration. GAMG runs to its
**1000-iteration ceiling on both pressure solves of every SIMPLE step** and reduces the initial
residual only **7.60×10⁻⁴ → 5.49×10⁻⁴**, a factor of 1.4 against the `relTol 0.01` it never
reaches. The pressure solve is the entire cost. This is the registered stop signature of Sanaa's
run instructions item 12, *"plateau with a stalled linear solver → stop, mesh fix > if doesnt
work > model fix"*, on a mesh whose max aspect ratio is 4437 and max non-orthogonality 89.46 —
the known hard case for GAMG agglomeration.

## A1.3 THREE RATE PROBES — DIAGNOSTICS, NOT RUNS OF THE ACT

Each probe is **30 iterations**: enough to clear startup and read a steady per-iteration cost.

> **A PROBE IS NOT A SMOKE AND ITS OUTPUT IS NOT A RESULT.** It reports one number, the measured
> per-iteration cost. **No force, coefficient or field from a rate probe is graded, quoted as a
> result, or compared to any band.** The registered smoke of §8.2 and its predictions are
> untouched and still to be run.

**One registered change per probe** (Sanaa, item 13), so these are three runs, not one:

| probe | the single change | why |
|---|---|---|
| **P3** | `maxIter 50` on the pressure solve | 1000 iterations are bought and ~nothing delivered; SIMPLE needs progress, not a converged inner solve. Cheapest to test and the most diagnostic: if cost falls proportionally the solve really is all in the linear solver; if it does not, the fault is elsewhere and P1/P2 are better aimed. **Run first.** |
| **P1** | tuned agglomeration — `faceAreaPair`, `nCellsInCoarsestLevel 2000`, `nPreSweeps 0` | at aspect ratio 4437 GAMG builds a poor coarse hierarchy |
| **P2** | `PBiCGStab` + `DIC` for p | does not agglomerate at all; often correct on wall-resolved prism layers |

**Checkpointing under the measured rate:** `writeInterval` 6 iterations, `purgeWrite 2` —
1800 s / 280.7 s = 6.4 is now the binding bound, replacing the "every 200 until the rate is
known" fallback of §7. Safe in both directions: if a probe lowers the rate, 6 iterations remains
well inside 30 minutes.

## A1.4 COMPARATOR PIN — why graded entries cite a later commit than the freeze

The runner recorded `ABSENT-AT-FREEZE` for 2 of 5 comparators on the smoke entry. **Checked by
content, the runner is right and the entry was wrong:** `cases/CRM_wingbody/tools/planted_force_check.py`
and `cases/CRM_wingbody/system/forces` are genuinely absent at `6165680b` (`git cat-file -e`
fails on both); they were written after the freeze. The other three are present with sha256
identical to disk.

**The registration document is byte-identical at `6165680b` and at every later commit** (sha256
prefix `425fb3a6012a1c36` at both). Graded entries therefore cite a commit at which **all five
comparators exist**, carrying the same registration bytes, and the certificate records that the
gate was frozen at `6165680b` and that the document has not moved since. No gate, threshold, cap
or label is affected by the change of cited sha.

---

# ADDENDUM 2 — 2026-09-12, THE PRESSURE EQUATION WAS INERT. Version 1.2.

**lines whose number changed above this section: 0**

**Alters no gate, no threshold, no cap and no label.** It records a negative finding and
registers one further diagnostic probe.

## A2.1 🔴 RATE PROBE P3 IS `NOT A RESULT`, AND SO IS THE BASELINE IT WAS COMPARED WITH

P3 measured a steady **21.41 s/iteration** (12 iterations, from differences; min 20.60, max
22.40) against the baseline's 280.7 s — a factor of 13.1. **The speedup is real and the run was
not solving.**

Evidence, from the probe's own written checkpoint and force output:

| check | value | meaning |
|---|---|---|
| p over 5,133,588 cells at iteration 12 | min **4007.394649000** Pa, max **4007.394649000** Pa, spread 6.8×10⁻¹⁰ Pa (rel 1.7×10⁻¹³) | the pressure field is **exactly freestream everywhere** |
| Cd pressure component | **4.71×10⁻¹⁶** | no pressure drag exists |
| Cl pressure component | **−3.06×10⁻¹⁵** | no pressure lift exists |
| `Cd(f)` pressure and `CmRoll` pressure | both **0.60792** | the identical value is the p·ΣSf signature of a **uniform** pressure on the half-model's open symmetry cut — not aerodynamics |
| p initial residual, iterations 1→15 | 7.15e‑04 → 8.23e‑04, **rising** | the pressure equation never converges and is getting worse |
| Ux initial residual | falls to 1.7×10⁻⁷ | the velocity field is **frozen**, not converged |
| exit | **rc = 136 (SIGFPE) at iteration 15** | it did not reach its registered 30 |

**Therefore the 50-vs-1000 `maxIter` equivalence proves nothing.** Per-solve reduction was
×1.31/×1.01/×1.38/×1.01 at 1000 and ×1.30/×1.01/×1.41/×1.00 at 50: **fifty equals a thousand
because both achieve essentially nothing on an inert equation.** `maxIter 50` is **NOT**
registered as a settled choice; any setting justified on this evidence would be justified by a
measurement of nothing. The `maxIter` ladder is re-run only against a pressure solve shown to be
live.

**And 21.41 s/iteration MUST NOT be multiplied by 6,000 to cost a converged run.** The cost of
an iteration that does nothing is 21.41 s. **The cost of a converging iteration on this grid
remains UNKNOWN** and will be higher. The §9 estimate stands; the A1.1 baseline stands as the
cost of a non-solving iteration; **no wall-clock figure for Tiny is registered.**

## A2.2 THE CAUSE IS A SCHEME ENTRY IN THIS LAB'S OWN DICTIONARY, NOT GAMG

`system/fvSchemes` carried `div(phid,p)  bounded Gauss upwind;`. **`bounded` subtracts an
`Sp(div(phi), p)` term.** `div(phid,p)` appears only in the **transonic** pressure equation —
the branch `transonic yes` selects — and that subtraction removes the convective contribution
the equation is built on, leaving an equation whose solution is the uniform field. OpenFOAM's
own transonic `rhoSimpleFoam` tutorial (`squareBend`) writes it **without** `bounded`; this is
the only `div` entry in the case where `bounded` is wrong, and it was applied mechanically
across all of them.

**This is a defect in the lab's dictionary, not in the solver or the grid.** A2.1's earlier
framing — "the blocker is a stalled linear solver" — was half right: the linear solver does not
converge, but the reason is upstream of it.

## A2.3 PROBE P4 — one registered change

`div(phid,p)  Gauss upwind;`, `bounded` removed. Nothing else differs. 30 iterations.
`maxIter 50` is carried **only** to keep the diagnostic affordable and is explicitly not
registered by doing so.

**ACCEPTANCE TEST FOR P4, AND IT IS NOT A TIMING:** a pressure field must **develop** —
`max(p) − min(p)` over the domain must exceed **1 %** of p∞, and the **pressure** components of
Cd and Cl must be non-negligible. A probe that is fast and leaves p uniform is `NOT A RESULT`,
exactly as P3 was. **`P1` (tuned agglomeration) and `P2` (PBiCGStab/DIC) stay queued behind P4**,
because an agglomeration measured against an inert equation is not a measurement.

## A2.4 WHAT THIS NEAR-MISS ESTABLISHES FOR THE ACT

**A pressure solve that is not reducing its residual looks exactly like a converging run in the
timings and in the momentum, enthalpy and turbulence residuals. Only the PRESSURE COMPONENT of
the forces, and the spread of p over the domain, give it away.** Both are now permanent
acceptance checks on every level of this family, ahead of any timing.

---

# ADDENDUM 3 — 2026-09-12, THE STARTUP RAMP AND ITS SUCCESSOR RUNGS. Version 1.3.

**lines whose number changed above this section: 0**

**Alters no gate, threshold, cap or label.**

## A3.1 PROBE P4 — THE PREDICTION HELD; THE ACCEPTANCE TEST IS UNRUN

The A2.3 prediction was: *p departs from freestream within the first few iterations and the
PRESSURE component of Cd becomes non-zero and of the right order.*

| channel | P3 (`bounded`) | P4 (`bounded` removed) |
|---|---|---|
| Cd **pressure** | 4.71×10⁻¹⁶ | **0.474386** |
| Cl **pressure** | −3.06×10⁻¹⁵ | **1.151377** |
| p initial residual | **rose** 7.15e‑04 → 8.23e‑04 over 15 iterations | **fell 0.999993 → 4.17×10⁻⁷ in one iteration** |

**The prediction passed on the force channel. One token — `bounded` — was the whole of it.**

🔴 **THE A2.3 ACCEPTANCE TEST IS NOT SATISFIED AND IS NOT CLAIMED.** It requires
`max(p) − min(p) > 1 %` of p∞ **read off a written checkpoint**; P4 died at iteration 2, before
`writeInterval 6` wrote anything. **P4 is `NOT A RESULT`** and no number from it is graded.

## A3.2 WHY P4 DIED — THE INERT EQUATION WAS MASKING THE REGISTERED TRANSIENT

```
pressureControl: p max 11727427.7398 Pa      p min -7487.10566461 Pa
first pressure solve:  Initial residual 0.999993  ->  FINAL RESIDUAL 1.611   (it DIVERGED)
```

**11.7 MPa against a freestream of 4007.394649 Pa — 2,926× — with a negative minimum.**
Correcting the scheme did not create a fault; it **revealed** the one §C.6 already prescribes
the remedy for. The transient could not occur while the pressure equation did nothing.

For scale, the M6I lane's equivalent excursion was 417,018 Pa, **4.1×** freestream, and a ramp
cured it. **Ours is two orders worse**, so the ramp is registered as the next change *and its
successor is registered now rather than improvised if it does not hold.*

## A3.3 THE REGISTERED CHANGE — THE §C.6 STARTUP RAMP

`verification/runs/CRM_WB_D8G_runs/launch_crm_wb_v2.sh`, built on the M6I two-stage pattern
rather than invented:

- **Stage 1**, 200 iterations, `fvSchemes.startup` (every convective term first-order) and
  `fvSolution.startup` (p 0.1, rho 0.01, U/e/h/nuTilda 0.3, p bounded to ±50 %).
  **Produces no graded answer.**
- **Stage 2**, the **registered** schemes and solution restored and **asserted md5-identical on
  both sides** before it begins. **The graded answer comes only from the registered schemes.**
- `system/controlDict.registered` kept pristine and asserted md5-identical at the end, so a
  crash between stages cannot leave a truncated budget committed. `endTime` moves **only**
  between stages, by `sed` on one line — never by `foamDictionary`, which inlines every
  `#include` and froze a stale forces dictionary into this case once already.
- `constant/fvOptions` carries `limitTemperature` [100, 1000] K as a **SAFETY NET, EXPLICITLY
  NOT CREDITED WITH THE FIX**: on M6I the equivalent limiter did nothing on 5,968 of 5,997
  iterations. **THE RAMP IS THE MECHANISM.** The count of limited cells is reported so its
  contribution can never be silently assumed.
- The algorithm is **unchanged**: `consistent yes` and `transonic yes` are **not touched**, and
  no `equations p` entry is added or removed. M6I measured what happens when those are altered
  casually — pressure went from 417,018 Pa to 22,368,256 Pa.

## A3.4 🔴 NAMED SUCCESSOR RUNG, REGISTERED **BEFORE** IT IS NEEDED: `potentialFoam` INITIALISATION

**Firing condition, declared now:** *if stage 1 of the ramp still produces a pressure excursion
of the same order — `p max` above ~10× p∞ — the initial field is the problem and this rung
fires.*

**Mechanism:** the violence comes from solving a pressure equation on a uniform freestream **with
a wing-body sitting in it**. That initial field is not merely inaccurate, it is *inconsistent
with the geometry*, and the first solve must invent the entire flow at once. `potentialFoam`
produces a divergence-free velocity field that already goes **around** the aircraft, so the first
RANS pressure solve starts from something the geometry admits. Standard registered practice for
transonic external aero, and cheap on 20.7 M cells against the ladder it protects.
`potentialFoam` is present in this installation.

## A3.5 🔴 THE DISCRIMINATOR — WHICH FAILURE HAPPENED, DECIDED IN ADVANCE

| observation | diagnosis | rung |
|---|---|---|
| stage 1 excursion **of the same order** (p max ≳ 10 p∞) | the **initial field** is inconsistent with the geometry | **A3.4 `potentialFoam`** |
| stage 1 **bounded**, excursion **returns when stage 2 restores the registered schemes** | **scheme-plus-shock interaction** — the M6I failure, a *different* rung | second-order/shock rung, registered when reached |
| stage 1 and stage 2 both bounded, death later at a **fixed-period CL oscillation** | buffet-like unsteadiness | §7 stop rule: mark, time-average, disclose |

**Pre-declared from the M6 lane's ladder rather than rediscovered:** M6I's L1 and L2 both died in
**stage 2**, after the ramp lifted, when a shock formed. **If this act survives startup, a second
death after iteration 200 is the shock and not the startup**, and it is the middle row above.

## A3.6 THE MONITORING RULE THIS EPISODE ESTABLISHES — THREE GREEN CHANNELS, ONE TELLING CHANNEL

An inert pressure solve looks like a converging run in **three** channels an experienced reader
trusts:

1. **timings** — 21.41 s/iteration, perfectly steady;
2. **momentum, enthalpy and turbulence residuals** — Ux fell to 1.7×10⁻⁷, which reads as
   convergence and is a **frozen** field;
3. 🔴 **continuity errors — 9.3×10⁻⁹, beautifully small, BECAUSE A UNIFORM FIELD SATISFIES
   CONTINUITY PERFECTLY.** This is the check a careful person reaches for when residuals look
   suspicious, and **it is trivially satisfied by precisely the failure mode it would be used to
   exclude.**

**Only the PRESSURE COMPONENT of the forces and the SPREAD of p over the domain give it away.**
Both are permanent acceptance checks on every level of this family, **read before any timing**.

---

# ADDENDUM 4 — 2026-09-13, THE FIRST RAMP ATTEMPT IS VOID. Version 1.4.

**lines whose number changed above this section: 0**

**Alters no gate, threshold, cap or label.**

## A4.1 🔴 THE A3.5 DISCRIMINATOR READING IS VOID — STAGE 1 CARRIED A CONFOUND

`CRM-WB-D8G-SMOKE-T-V2-RAMP` (launched 23:58:37Z, pid 151199) produced a stage-1 excursion of
**p max 4.41×10²⁴ Pa** — which under A3.5 would fire the `potentialFoam` rung.

**IT DOES NOT FIRE IT, BECAUSE THE OBSERVATION IS NOT A CLEAN TEST OF THE RAMP.**
`fvSolution.startup` carried `maxIter 50` on the pressure solve — carried over from the P3/P4
probes "to keep the diagnostic affordable", and **never part of the registered ramp**. Stage 1
therefore tested *ramp + cap*, not *ramp*. A discriminator is only as good as the single change
it discriminates, and this one had two.

## A4.2 THE CAP IS THE CULPRIT, AND THE SAME RUN CONTAINS ITS OWN CONTROL

Both stages ran in one job, on one mesh, one iteration apart:

| | pressure solve | outcome |
|---|---|---|
| **stage 1**, `maxIter 50` | initial 0.999995 → **FINAL 5.127×10⁸** | **DIVERGED**; p max 4.41×10²⁴ Pa |
| **stage 2**, **uncapped** | initial 0.999993 → **final 9.947×10⁻³ in 231 iterations** | **CONVERGED**, ×100 reduction, relTol met |

**A cap that was harmless on an inert equation is destructive on a live one**, and 231 iterations
is simply what this pressure equation costs on this mesh — the cap truncated it mid-solve and
returned a divergent field as though it were an answer. This retrospectively vindicates A2.1's
refusal to register `maxIter 50`: had it been registered on the P3 "equivalence", it would now be
frozen into every level of the family.

**`maxIter 50` is removed from `fvSolution.startup`.** This restores the registered configuration
rather than introducing a change: the stage-2 (graded) solution never carried a cap.

## A4.3 A DEFECT IN THE LAUNCHER — A FAILED STAGE 1 FELL THROUGH INTO STAGE 2

`launch_crm_wb_v2.sh` captured the stage rc as `RC=$(run_solver …)`, and `run_solver` echoed a
progress line **to stdout**, so `RC` became a multi-line string. `[ "$RC" -ne 0 ]` cannot compare
that, the guard silently did not fire, **and the graded stage 2 ran on top of a failed ramp.**
Fixed: the progress line goes to **stderr**, and the guard now **refuses a non-numeric rc** rather
than comparing it. The rule it breaks is the lab's own — a wrapper must capture the rc *of the
process*, and anything else on stdout is not the rc.

## A4.4 WHAT IS AND IS NOT ESTABLISHED

- **Established:** the pressure equation is live (A3.1); uncapped GAMG converges it in ~231
  iterations at ×100 reduction; a `maxIter` cap must never be registered for this family.
- **NOT established, and not claimed:** whether the §C.6 ramp bounds the startup transient. That
  test has not yet been run without a confound. **The `potentialFoam` rung of A3.4 stays
  registered and unfired**, and its firing condition is unchanged.
- The run is `NOT A RESULT`. No force, coefficient or field from it is graded.

---

# ADDENDUM 5 — 2026-09-13, THE A3.4 TRIGGER IS AMENDED AND THE RUNG FIRES. Version 1.5.

**lines whose number changed above this section: 0**

**Alters no gate, no threshold on a graded quantity, no cap and no label.** A3.4 is a
**LADDER-RUNG TRIGGER, not a grading gate**: it decides which remedy is tried next. Rule 2 closes
gates after first compute; it does not freeze the ladder.

## A5.1 🔴 WHY THE ORIGINAL TRIGGER COULD NOT BE READ — A NEW FAILURE CLASS

A3.4 fired on *"a pressure excursion of the same order — `p max` above ~10× p∞"*. Run
`CRM-WB-D8G-SMOKE-T-V3-RAMP` (00:02:49Z, pid 154457), the first ramp attempt without the `maxIter`
confound, produced **zero `Solving for p` lines and zero `pressureControl: p max` readings**: it
faulted *inside* the first pressure solve, and `pressureControl` reports only *after* a solve
returns.

> **THE THRESHOLD WAS WRITTEN ON A QUANTITY THAT THE FAILURE MODE IT WAS MEANT TO DETECT
> DESTROYS. The more severe the fault, the less readable the trigger.**

This is a distinct failure class from the three inert-instrument episodes already recorded
(A2.1, A3.2, A4.1): those were instruments reporting a *proxy*; this is **a registered threshold
aimed at a reading the fault suppresses.** Pre-registration was the protection, and the
protection was pointed at something the failure removes.

**RULE ESTABLISHED: when registering a trigger, ask what the failure mode does to the quantity
being triggered on. A threshold that degrades gracefully as the fault worsens is usable; one that
vanishes at the moment it is needed is not.**

## A5.2 THE AMENDED TRIGGER, AND THE GROUND FOR FIRING

> **A3.4 TRIGGER, AMENDED:** the rung fires if **stage 1's first pressure solve fails to
> complete**, *or* if it reports `p max` above 10× p∞.

The registered *question* was always *"is the initial field the problem?"*; `p max` was one
readable symptom of a yes. That symptom is unavailable, and the question is answered by a
different channel, **measured not inferred** — in the **same iteration**:

| equation | initial → final residual | outcome |
|---|---|---|
| Ux | 0.99935 → 2.74×10⁻⁴ | converged |
| Uy | 1.00000 → 3.36×10⁻⁴ | converged |
| Uz | 0.99892 → 2.97×10⁻⁴ | converged |
| h | 0.99915 → 3.37×10⁻⁴ | converged |
| **p** | **no line emitted** | **faulted before starting** |

**Three equations converge three orders and the fourth cannot start.** That localises the fault
to the pressure equation exclusively — the one equation that must reconcile a uniform initial
field with a geometry it does not fit.

*Ruled by `cfd-supervisor`. The lane referred it rather than deciding: a lane ruling that its own
unreadable threshold should be read as satisfied is the move the freeze exists to prevent,
and it matters most exactly when the merits are good.*

## A5.3 THE RUNG — `potentialFoam` INITIALISATION AS STAGE 0

`potentialFoam -parallel -writePhi` runs before the ramp, on `system/{fvSchemes,fvSolution}.potential`
(solves for the velocity potential only; sets no thermodynamic state and grades nothing;
`nNonOrthogonalCorrectors 10` for a family whose max non-orthogonality is 89.5°). It writes a
**divergence-free velocity field that already goes around the aircraft**, so the first RANS
pressure solve starts from a field the geometry admits. Stage 0 **fails closed**: a non-zero rc,
a non-numeric rc, or a `log.potentialFoam` without an `End` line stops the run before the ramp.

## A5.4 🔴 REGISTERED PREDICTION — IT CAN REFUTE THE REASON FOR FIRING

> **If the initial field is the problem, a `potentialFoam`-initialised stage 1 will COMPLETE ITS
> FIRST PRESSURE SOLVE.**
>
> **If it still faults before emitting a line, the hypothesis is WRONG, the rung was mis-aimed,
> and the ladder climbs elsewhere.** This is what makes A5.2 a rung rather than a judgement: the
> next run can overturn the ruling that fired it.

## A5.5 THE ONE REAL RESULT OF THE FIVE RUNS SO FAR

Promoted out of the incident narrative because it stands on its own. **Within one run, on one
mesh, one minute apart, as a single-variable controlled comparison:**

| stage | pressure solve | outcome |
|---|---|---|
| 1, `maxIter 50` | 0.999995 → **5.127×10⁸** | diverged |
| 2, **uncapped** | 0.999993 → **9.947×10⁻³ in 231 iterations** | converged, ×100 |

**For this family, a `maxIter` cap on the pressure solve must NEVER be registered.** 231
iterations is simply what this pressure equation costs on this mesh.

**And the honest ledger: the ramp has still never been tested. Every run before V3 measured
something other than the question; V3 is the first that got far enough to fail in the right
place.**

---

# ADDENDUM 6 — 2026-09-13, THE A5.4 PREDICTION HELD. Version 1.6.

**lines whose number changed above this section: 0**

**Alters no gate, threshold, cap or label.** It records the outcome of a registered prediction.

## A6.1 THE PREDICTION, AND WHAT IT RETURNED

A5.4, written **before** the run: *if the initial field is the problem, a `potentialFoam`-initialised
stage 1 will **COMPLETE ITS FIRST PRESSURE SOLVE**; if it still faults before emitting a line, the
hypothesis is wrong, the rung was mis-aimed, and the ladder climbs elsewhere.*

`CRM-WB-D8G-SMOKE-T-V4-POTENTIAL`, runner-launched 00:09:55Z, stage 0 rc=0
(`log.potentialFoam`: continuity error 3.36×10⁻⁸, `End`):

| | first pressure solve of stage 1 |
|---|---|
| V3, uniform start | **zero** `Solving for p` lines — faulted *inside* the solve |
| **V4, potentialFoam** | **0.999999889 → 0.00877 in 14 iterations — COMPLETED** |

**THE PREDICTION HELD.** It could have refuted the ground on which the rung was fired; it did not.

## A6.2 🔴 THE NUMBER FOR THE CERTIFICATE — A FINDING ABOUT THIS GRID FAMILY, NOT ABOUT THIS RUN

First-iteration pressure excursion, same mesh, same solver, same schemes, same relaxation — **only
the field the solver starts from differs**:

| configuration | `p max` | × freestream |
|---|---|---|
| P4, no ramp, uniform start | 11,727,428 Pa | **2,926×** |
| V2 stage 2, uniform start | 11,694,309 Pa | 2,918× |
| V2 stage 1, ramp **+ `maxIter` cap** | 4.41×10²⁴ Pa | — |
| V3, ramp, uniform start | *never reported — faulted inside the solve* | — |
| **V4, `potentialFoam` + ramp** | **8,811 Pa** | **2.20×** |

**A reduction of three orders of magnitude, and far below the 40,074 Pa (10×) trigger of A5.2.**
The solve also became *ordinary*: **14 iterations**, against the 231 that uncapped GAMG needed from
a uniform start and against the fault that no iteration count could get past.

**THE REGISTERED QUESTION IS ANSWERED: THE INITIAL FIELD WAS THE PROBLEM.** A uniform freestream
with a wing-body in it is not an inaccurate guess — it is *inconsistent with the geometry*, and the
first pressure solve had to invent the entire flow at once.

**This and the `bounded`/`div(phid,p)` finding of A2.2 belong together on the certificate: the two
of them are the whole reason five runs measured something other than the question.**

## A6.3 WHAT IS STILL NOT ESTABLISHED

- 🔴 **Nothing from stage 1 is a result.** It is first-order with heavy relaxation. **The graded
  answer comes from stage 2 only.**
- 🔴 **No cost figure may be taken from stage 1.** Its per-iteration cost says nothing about the
  registered schemes — the same error as the `maxIter` probe (A2.1). **The cost of Tiny remains
  UNKNOWN** and is measured on stage 2, at steady state, from differences.
- 🔴 **The M6I warning is now the live risk.** M6I's L1 and L2 both cleared startup and then died
  in **stage 2**, at iterations 296 and 668, when a shock formed. That is the **middle row of the
  A3.5 table — a different rung**, not a startup failure. The handover assertion proves stage 2
  inherited a real field; it cannot prove the registered schemes survive a shock on this grid.

## A6.4 THE TEMPERATURE LIMITER IS DOING WORK HERE, UNLIKE ON M6I

At stage-1 iteration 2: `LimitedCells=18` (lower) and `2` (upper), of 20,657,615. On M6I the
equivalent limiter reported zero limited cells on 5,968 of 5,997 iterations. **It is still not
credited with the fix** — the excursion fell three orders before the limiter touched anything — but
its activity is recorded rather than assumed idle, and the count is reported every iteration.

---

# ADDENDUM 7 — 2026-09-13, SELF-CONSISTENT INITIAL STATE. Version 1.7.

**lines whose number changed above this section: 0**

**Alters no gate, threshold, cap or label.** A ladder rung with a refutable prediction.

## A7.1 🔴 THE PATTERN, NAMED, BECAUSE IT HAS NOW RECURRED THREE TIMES

> **AN INITIAL CONDITION MUST BE SELF-CONSISTENT ACROSS ALL FIELDS, NOT JUST THE ONE THAT FAILED
> LAST. Fixing one field's inconsistency reveals the next.**

- `bounded` on `div(phid,p)` made the pressure equation inert → fixing it exposed the startup
  transient (A2.2 → A3.2).
- A uniform velocity field inconsistent with the geometry → `potentialFoam` fixed it, 2,926× →
  2.20× (A6.2), **and the failure moved to the energy equation.**
- A developed velocity field on a **uniform 310 K** temperature → this addendum.

Not three incidents. **One defect seen three times, one field along each time.**

## A7.2 THE EVIDENCE — THE LIMITER'S OWN REPORT

| stage-1 iteration | `UnlimitedTmin` / `UnlimitedTmax` | reading |
|---|---|---|
| 1 | **310 / 310** | temperature field still **uniform** before limiting |
| 2 | **100 / 1000** | driven clean through **both** limiter bounds |

With the enthalpy initial residual at **0.999999999957**, the energy equation had to invent the
entire thermal field at once. `potentialFoam` sets **U** and `phi` and **no thermodynamic state**,
so stagnation regions that should sit near 355 K and accelerated regions that should be cooler
were all still at freestream.

## A7.3 THE RUNG — ISENTROPIC T, p AND rho FROM THE POTENTIAL-FLOW VELOCITY

`cases/CRM_wingbody/tools/isentropic_init.py`, run as **stage 0b**, immediately after
`potentialFoam` and before the ramp. **The EXACT isentropic relations, not the linearised form:**

```
T0 = T_inf (1 + (g-1)/2 M_inf^2)         (total temperature is constant)
x  = |U|^2 / (g R T0 - (g-1)/2 |U|^2)    (closed form for M^2; M = |U|/sqrt(gRT) is implicit in T)
T  = T0 / (1 + (g-1)/2 x)
p  = p_inf (T/T_inf)^(g/(g-1))           rho = p/(R T)
```

**Why exact and not linearised:** the two agree at M = M∞ and at stagnation and diverge in
between — at |U| = 1.2 a∞ (local M 1.297) they differ by **5.63 %**, which is *inside a supersonic
pocket on a transonic wing*, precisely where the initial state most needs not to be wrong.
**rho is set from the chosen p and T** rather than derived from a state nobody chose.

**Self-check, asserted before anything is written:** at |U| = U∞ the closed form must reproduce
M = 0.85, T = 310.000000000 K and p = 4007.394649 Pa. Verified: M = 0.850000000, T = 310.000000000,
p = 4007.394649.

### 🔴 THE APPROXIMATION KNOWINGLY ACCEPTED, STATED SO NO READER MISTAKES IT

`potentialFoam` solves **INCOMPRESSIBLE** potential flow. At M∞ = 0.85 its velocity field is **not**
the compressible one, particularly near the shock. **THE PURPOSE OF THIS INITIALISATION IS TO BE
SELF-CONSISTENT, NOT CORRECT** — a thermodynamic state consistent with the velocity field it is
given, so that no equation has to invent everything at once. **It is not an attempt at the answer,
and nothing from it is a result.**

## A7.4 🔴 REGISTERED PREDICTION — IT CAN REFUTE THE REASON FOR FIRING

> With a self-consistent initial state, stage 1 completes its **first twenty iterations** with the
> limiter's **`LimitedCells` at ZERO throughout** and the **unlimited** temperature staying inside
> **[200, 500] K**.
>
> **If the temperature still leaves those bounds, the hypothesis is WRONG — the initial state was
> not the problem, the ramp's relaxation is — and the ladder climbs to that branch instead.**

The limiter firing *at all* is the signal; a prediction phrased only on the unlimited bounds would
leave a reader to derive that.

## A7.5 WHAT ITERATION 1 OF V4 ESTABLISHED, AND WHAT IT DID NOT

The first structurally real iteration this act has produced: pressure solve converging in **14**
iterations, `p max` at **2.20×** freestream, continuity error **1.43×10⁻⁵**, and forces with a
**live pressure component** — Cd 0.0120408 = 9.68×10⁻⁵ pressure + 0.0119440 viscous, Cl −0.000303.

**It is not converged, it is not a result, and it is not quoted as one.** What it does establish is
that **A3.6's check passes**: the pressure component is non-zero and of plausible order. The
instrument built after being fooled by an inert equation now confirms the equation is live.

**Ledger, unchanged: six runs, three findings, zero results.**

---

# ADDENDUM 8 — 2026-09-13, A FIELD-BASED DIVERGENCE CRITERION. Version 1.8.

**lines whose number changed above this section: 0**

**Alters no gate, threshold, cap or label.** Registered **before** anything is extracted from the
run it governs.

## A8.1 🔴 WHY THE EXISTING CRITERIA COULD NOT SEE IT — THE FIFTH INSTANCE

Probe P2's branch 3 was registered as *"runs, does not fault, does not converge in a stated
iteration count"*, and the count was set at 2000 linear iterations. **Both the supervisor's
wording and the lane's number aimed at the LINEAR SOLVER'S ITERATION COUNT while the divergence
lives in the FIELD.**

Observed in V12: linear solves converge cleanly — 0.9939 → 6.08×10⁻³ in **2** iterations,
0.00454 → 3.06×10⁻⁵ in **6**, 0.9672 → 6.36×10⁻³ in **3** — while `p max` goes
**3.76×10¹⁵ → 1.93×10¹⁶ Pa** against a freestream of 4007.39. Largest single solve: 1000, which is
PBiCGStab's own default, well under the registered 2000.

> **"THE SOLVER IS ITERATING FINE" AND "THE ANSWER IS DIVERGING" ARE INDEPENDENT FACTS, AND ONLY
> ONE OF THEM WAS BEING WATCHED.**

This is the **fifth** time in this act a registered criterion has been aimed at a quantity the
failure does not move (A2.1, A3.2, A4.1, A5.1, and now this).

## A8.2 THE REGISTERED CRITERION — ON THE FIELD, NOT ON THE SOLVER

> **DIVERGENT** iff `p max` exceeds **100 × p∞ = 400,739 Pa**, *or* `p max` grows by more than a
> factor of **10 between consecutive checkpoints**.
> **BOUNDED** iff `p max` stays under 10 × p∞ = 40,074 Pa for 20 consecutive iterations.
> Between the two: **UNDECIDED**, and reported as such rather than resolved by preference.

Read from the written checkpoints, **before** any timing and **before** any linear-solver
diagnostic. A run may satisfy every residual criterion and be `DIVERGENT` by this one; that is the
point.

## A8.3 WHAT IS EXTRACTED FROM A DIVERGING RUN, AND WHAT EACH ANSWER MEANS

`p max` location per checkpoint, and — decisively — **whether that location is STABLE**:

| observation | diagnosis | rung |
|---|---|---|
| runaway **stays in one place** and grows | that place is defective | **mesh-quality rung** — wing-body junction or tip |
| runaway **at the farfield** | boundary treatment | **boundary-condition rung** |
| runaway **MOVES or SPREADS** | **a local mesh defect does not migrate** | **scheme or boundary treatment**, not the mesh |
| runaway **everywhere at once** | the ramp is not holding | **A7.4's named branch: the ramp's relaxation** |

**Stability across checkpoints is the discriminator**, because a mesh defect is fixed in space and
a scheme or boundary fault is not.

## A8.4 🔴 WHEN THE INFORMATION IS EXHAUSTED — AN EXPECTED-VALUE DECISION, **NOT A CAP**

**Sanaa's ruling stands in full: nothing stops on time or on budget** (directive #17). This is not
a cap and must not become one.

> **Once THREE consecutive checkpoints show a consistent `p max` location, the information this
> run can produce has been extracted and further iterations buy nothing.** Stopping there is an
> expected-value judgement about what the next iteration would tell us — the same judgement as
> declining a fine mesh whose answer is already known — and it is recorded with the three
> checkpoints that support it.

**Registered now so that "enough" is not decided later by fatigue.**

---

# ADDENDUM 9 — 2026-09-13, THE PRESSURE CLAMPS WERE INSIDE THE PHYSICAL RANGE. Version 1.9.

**lines whose number changed above this section: 0**

**Alters no gate, threshold, cap or label.**

## A9.1 🔴 THE CLAMP SAT BELOW STAGNATION — AND THIS ACT'S OWN INITIALISER PROVED IT

At the registered M∞ = 0.85, the **true** stagnation pressure is

```
p0/p_inf = (1 + 0.2 M^2)^3.5 = 1.603819      p0 = 6427.135 Pa
```

| | Pa | × p∞ |
|---|---|---|
| `pMaxFactor 1.5` (as registered) | 6011.092 | 1.5000 |
| **true stagnation p0** | **6427.135** | **1.6038** |
| `pMinFactor 0.5` (as registered) | 2003.697 | 0.5000 |
| **lowest attainable at local M = 1.5** | **1750.771** | **0.4369** |

**The clamps sat INSIDE the physically attainable range at BOTH ends.** The upper clamp was
**6.5 % below stagnation**; the lower clamp was **above** the pressure in the supersonic pocket.

🔴 **THE PROOF IS THIS ACT'S OWN ISENTROPIC INITIALISER.** A7.3's tool reported its range as
**`p [1750.771, 6427.135] Pa`** — its maximum **is** p0 to six figures, and its minimum is the
pocket pressure at its own M = 1.5 cap. **The initial field lay outside the clamp at both ends
before a single iteration ran.** The number was printed in the log of every run from V5 onward and
neither the lane nor the supervisor read it against the clamp.

## A9.2 WHAT THIS INVALIDATES — STATED, NOT CARRIED FORWARD

A clamp inside the physical range is **a persistent non-physical forcing**, not a safety net: every
cell at or near stagnation was clamped every iteration, from iteration 1, in a region that was not
excursing.

> 🔴 **EVERY CLAMPED-CELL FOOTPRINT IN A8/A9 WAS MEASURED AGAINST A PHYSICALLY WRONG THRESHOLD.**
> The global 7.4768 % → 3.7068 % recession, processor29's 32.820 % → 59.898 %, the chord-fraction
> medians of 0.884 and 0.924, and the 42 % below-surface figure **cannot be read as absolute
> statements about divergence.** A cell "at the clamp" may simply be a cell whose **correct**
> pressure exceeds 1.5 p∞ — the stagnation region, and the pressure side near the trailing edge,
> **which is exactly where 42 % of them were found.**
>
> **Relative trends may survive a common wrong threshold; no absolute reading does.** The
> blunt-base and steady-RANS readings both sit downstream of this and **neither may be registered
> until the footprint is re-measured against derived clamps.**

## A9.3 THE REGISTERED CHANGE — CLAMPS DERIVED, NOT CHOSEN

```
pMaxFactor 2.0    above stagnation 1.6038, margin x1.25
pMinFactor 0.1    below the pocket minimum: at local M 2.6, p/p_inf = 0.0804
```

**Both derived from the registered freestream Mach and recorded with their derivation**, so the
next reader can check them the way this one was checked. **A clamp must sit above every physically
attainable value; where it does not, it is a boundary condition masquerading as a guard.**

## A9.4 WHAT SURVIVES UNTOUCHED

The A8.4 TE-base measurement: **13–22 cells across the blunt base in η 0.58–0.88** against a
DPW-6 requirement of "≫ 8", anchored to NASA's stated 0.48 % TE base by the measured 0.45–0.71 %.
It is a mesh property and no clamp touches it. **Under-resolution remains excluded.**

And the cross-act framing stands: the eight-cell requirement **discriminated, in opposite
directions, on two aircraft in one night** — M6 failing it by two orders, the CRM passing it by
nearly three. **A test that only ever returns one answer is not a test.**

---

# ADDENDUM 10 — 2026-09-13, FINDING 8 IS RETRACTED. `transonic no`. COST. Version 1.10.

**lines whose number changed above this section: 0**

## A10.1 🔴 FINDING 8 — "THE RUNAWAY ORIGINATES IN THE FARFIELD" — IS **RETRACTED**

Refuted by one read of the subdomains' own boundary files, verified by this lane:

| | `body` faces | `wing` | **`farfield`** | `symmetry` |
|---|---|---|---|---|
| processor0 | **11,040** | 0 | **0** | 11,733 |
| processor1 | **10,342** | 0 | **0** | 6,902 |

**Both subdomains own thousands of AIRCRAFT WALL FACES AND NOT ONE FARFIELD FACE.** The farfield
boundary is not present in either, so the runaway cannot begin at it. Patch extents from the mesh
that ran: `body` x[2.352, 65.087] m, `wing` x[25.218, 47.978] m, `farfield` x[−2943.860, 3022.600] m.

🔴 **THE ERROR: I placed the fuselage nose at x ≈ 22 m from memory. It is at x = 2.352 m.** 22 m is
near the **wing root leading edge** (25.218 m) — I read the wing and called it the fuselage, then
concluded that subdomains upstream of *that* contained no aircraft.

> **A REMEMBERED GEOMETRY IS NOT A MEASURED ONE.** The mesh's own boundary file answers *"is the
> aircraft in this subdomain"* directly, exactly, and for free — one grep from a file already open.
> I answered it from a bounding box plus a recalled coordinate.

## A10.2 🔴 THE LOCATION CHANNEL IS NULL AND MUST STOP BEING MINED

`p max` sits in the **nose region — which is where maximum pressure BELONGS.** This act's own
initialiser says so: its maximum is stagnation, 6427.135 Pa, to six figures. **The location is
exactly as expected, so it discriminates NOTHING.**

**THREE LOCATION STORIES IN ONE ACT, ALL THREE WRONG:** the outboard shock (refuted by chord
fraction and surface side), the blunt trailing edge (invalidated by the wrong clamps), the farfield
(refuted above). Each was a null or corrupted channel converted into a mechanism.

> **THE ANOMALY IS THE MAGNITUDE AT A CORRECT LOCATION, NOT THE LOCATION.** No further rung is
> derived from where `p max` sits. **A null result is not a pointer.**

## A10.3 WHAT IS EXCLUDED, AND WHAT HONESTLY IS NOT

**Excluded by measurement:** the mesh (13–22 cells across the TE base vs a requirement of ≫8);
agglomeration (convicted of the `sumProd` fault only, and removed); the initial field
(self-consistent, its maximum *is* stagnation); the clamps (corrected, and iteration 1 still
overshoots them); **the farfield (A10.1)**.

**NOT excluded:** the transonic pressure equation's `div(phid,p)` term; the compressibility
coupling at a stagnation point; **and things neither reader has named.** The blunt-TE and
steady-RANS footprints remain invalidated by the wrong clamps — A10.1 neither revives nor further
kills them.

## A10.4 THE REGISTERED CHANGE — `transonic no`, AS A DIAGNOSTIC

`div(phid,p)` is the **only** term that exists on the transonic branch, and it has never been
tested. `transonic no` is **not the right physics at M 0.85** and **its answer is never graded**;
§C.6's registered transonic option stands unchanged.

**THREE BRANCHES, FIELD-BASED CRITERION (A8.2), NO LOCATION CHANNEL:**

| outcome | diagnosis |
|---|---|
| `p max` stays **BOUNDED** (< 10 × p∞ for 20 iterations) | the transonic pressure equation on this mesh is **convicted**; the rung is its discretisation |
| `p max` **DIVERGENT** (> 100 × p∞, or ×10 between checkpoints) | the transonic branch is **exonerated**; the cause is upstream of the pressure equation |
| neither, at 30 iterations | **UNDECIDED**, reported as such |

*A location channel was drafted and is **deleted**: "informative only if the runaway begins
upstream" can never fire, because it never began upstream.*

## A10.5 COST — RULE 12, OWED AND PAID

Core-minutes = wall s × ranks ÷ 60, from each run's own `ExecutionTime`, 32 ranks throughout:

| run | wall s | core-min |
|---|---|---|
| SMOKE_T (baseline) | 548.5 | 292.5 |
| PROBE_P3_MAXITER | 323.5 | 172.6 |
| PROBE_P4_UNBOUNDED | 23.3 | 12.4 |
| SMOKE_V2_RAMP | 43.8 | 23.4 |
| V4 / V5 / V7 / V8 / V9 / V10 / V11 | 88.2 total | 47.0 |
| SMOKE_V12_NOGAMG | 1057.2 | 563.9 |
| DIAG_EARLY | 592.6 | 316.1 |
| **TOTAL (solver wall only)** | | **1,427.9 core-minutes** |

**= 23.80 core-hours → $1.22 DERIVED** at $0.0513/core-h.
**`cost_basis`: REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5).

**Named, not folded in:** mesh conversion, `decomposePar`, and the `potentialFoam`/isentropic
stage-0 work are **excluded** from this figure and remain unmeasured. Against the §9 registered
ladder estimate of 124,700–245,800 core-minutes, thirteen runs have consumed **1.1 %** of the
lower bound and produced **zero graded rows** — the spend is in diagnosis, not in solving.

## A10.6 THE `purgeWrite` GUARD, HOLE CLOSED

`purgeWrite 0` means **keep every time directory** — maximum retention, not minimum. The numeric
and semantic orderings disagree at exactly that one value, and it is the value a diagnostic run is
most likely to use; `-ge 2` refused it. Now accepted: **0 (keep all) or ≥ 2.** The previous fix's
own commit message described this hole and left it.

---

# ADDENDUM 11 — 2026-09-13, THREE CORRECTIONS AND A PARTITION. Version 1.11.

**lines whose number changed above this section: 0**

## A11.1 🔴 "EXONERATED" IS WITHDRAWN — THE CORRECT CLAIM IS WEAKER

A10.4 branch 2 fired and the DIVERGENT verdict stands. **The word attached to it does not.**

> *"It still diverges without X"* proves **X IS NOT NECESSARY**. It does **not** prove X is not a
> cause. If two independent mechanisms are each sufficient to diverge this case, removing either
> leaves it diverging — and each would then "exonerate" the other.

**REGISTERED CLAIM, REPLACING THE EXONERATION: the transonic branch is NOT SOLELY RESPONSIBLE.**

## A11.2 🔴 THE 34.6× I DECLINED TO READ — RECORDED, ON THE GRADED CHANNEL

| | iteration-1 `p max` | × p∞ |
|---|---|---|
| `transonic yes` | 10,364.11 Pa | **2.59** |
| `transonic no` | 358,971.90 Pa | **89.58** |
| | | **ratio 34.6×** |

This is **the same channel A8.2 grades** — `p max`, iteration 1 — not a qualitative aside.
**Removing the term made the first iteration 34.6 times WORSE**, which points the opposite way
from the label I attached: that is what one sees if the term had been *suppressing* the runaway.

**The A10.4 branch does not turn on it, and it is UNEXPLAINED. It is recorded anyway.**
Declining to read a number on the graded channel is not discipline; it was over-correction from
having been wrong three times. **Unexplained and recorded beats unread.**

## A11.3 🔴 THE EXCLUSION LIST, SPLIT BY STRENGTH OF EVIDENCE

Flattened into one list, six items read as equally excluded. They are not.

**MEASURED CLEAN — the suspect itself was measured:**
- **mesh**: 13–22 cells across the TE base in η 0.58–0.88 vs a requirement of ≫8
- **farfield**: processor0 and processor1 own 11,040 and 10,342 *body* faces and **zero** farfield faces
- **initial field**: self-consistent; its maximum **is** stagnation, 6427.135 Pa, to six figures
- **clamps**: derived from the registered Mach; iteration 1 still overshoots them
- **energy relaxation**: the dictionary that ran carries **both** `e 0.3` and `h 0.3`; the energy
  equation **is** relaxed. *(Checked by the supervisor from the dictionary, not by a run.)*

**NOT SOLELY RESPONSIBLE — removing it did not cure it:**
- **the transonic branch / `div(phid,p)`**

## A11.4 WHAT IS ACTUALLY EARNED, AND IT DOES NOT DEPEND ON A11.1

**The divergence survives two different pressure-equation formulations, two preconditioners and
two Krylov solvers** — PCG/DIC on a symmetric matrix and PBiCGStab/DILU on an asymmetric one.
That is real support for *the cause is upstream of the pressure solve*, and it stands whatever
A11.1 says.

*And the DIC/DILU mirror is a structural confirmation in its own right: DIC was refused as
asymmetric with transonic ON, DILU refused as symmetric with it OFF. Two refusals, opposite
directions, same term — OpenFOAM confirming by construction that `div(phid,p)` is the asymmetry
source.*

## A11.5 🔴 STOP ELIMINATING SUSPECTS — PARTITION THE REMAINING SPACE IN ONE RUN

Fourteen runs have eliminated one suspect at a time and the list is not empty. Everything upstream
of the pressure solve is **U, h, nuTilda, the psi/rho closure and phi** — and every one is already
written beside `p` on every write.

> **REGISTERED CRITERION: WHICHEVER FIELD LEAVES ITS PHYSICAL RANGE FIRST IS UPSTREAM OF THE REST.**
> Reported per iteration, each against its own physical scale: `max|U|` vs U∞ = 300.019 m/s;
> `T` min/max vs T∞ = 310 K and T₀ = 354.795 K; `max nuTilda` vs the SA freestream 1.261×10⁻³;
> `max|phi|`; `rho` min/max vs ρ∞ = 0.04503 kg/m³; and `p max` alongside.
> **No mechanism is named in advance. This is a partition, not a guess.**

## A11.6 🔴 `purgeWrite N` KEEPS THE MOST RECENT N — AND IT COST THIS ACT ITS BEGINNING TWICE

Measured on this act's own runs:

| run | `purgeWrite` | `writeInterval` | times retained |
|---|---|---|---|
| `DIAG_EARLY_T` | 20 | 1 | 0, **62 … 81** |
| `PROBE_NOTRANSONIC_T` | **0** | 3 | 0, 3, 6, … 33 — **everything** |

**The run built to capture the beginning does not contain the beginning.** `purgeWrite 20` kept the
LAST twenty. **The value that works is `purgeWrite 0` — the exact value the launcher's guard
refused until an hour ago**, which is now the second time that one number has cost this act its
early evidence.

**The partition run therefore uses `purgeWrite 0`, `writeInterval 1`, three to five iterations.**

---

# ADDENDUM 12 — 2026-09-13, A11.5 IS ANSWERED FROM THE LOGS, AND THE ALGORITHM CHANGES. Version 1.12.

**lines whose number changed above this section: 0**

This addendum registers **one change to the solution algorithm** and the run that carries it,
`CRM-WB-D8G-SOLVE-T-R1`. **It alters no gate, no threshold, no band, no cap and no label.**
Sections 0–10 above stand unamended. No solver has run under this addendum at the moment of
the freeze.

## A12.1 🔴 A11.5's REGISTERED CRITERION IS ANSWERED — AND IT DID NOT NEED THE PARTITION RUN

A11.5 registered: *"whichever field leaves its physical range first is upstream of the rest."*
`PARTITION_T` was built to answer it and SIGFPE'd at iteration 1 before writing a field.
**The answer was already in the logs of runs 15 and 16.** Reading them in the order A11.5
prescribes — each field against its own physical scale, no mechanism named in advance:

| iteration | what the logs show | source |
|---|---|---|
| **1** | `h` initial residual **0.999999999656**; `T` still inside its own initialised range (`UnlimitedTmin 244.686`, `UnlimitedTmax 354.795` — the isentropic initialiser's own bounds); `p` corrector solve healthy at **6** linear iterations | `DIAG_EARLY_T/log.rhoSimpleFoam` |
| **2** | `T` **leaves its physical range first** — 145 cells below 100 K and 388 above 1000 K (0.003 %); `p` corrector solve rises to **79** | same |
| **3** | `p` corrector solve **760** linear iterations; ExecutionTime for one outer iteration **11.62 s → 106.92 s** | same |
| **49** | **12,410,571 cells (60.08 %) at Tmin = 100 K and 6,632,438 (32.11 %) at Tmax = 1000 K — 92.19 % of 20,657,615 cells pinned at BOTH clamps at once**; 97.2 % by iteration 197 | `PROBE_NOTRANSONIC_T/log.rhoSimpleFoam` |

**REGISTERED FINDING, under A11.5's own criterion: the ENERGY channel is upstream.** `h`'s initial
residual is pinned at ~1 from iteration 1 and never falls one digit in 200 iterations (still
**0.999578** at iteration 100) while `Ux` falls 0.281 → 0.0257 and `nuTilda` 0.257 → 0.0443 over
the same span — the solver is not globally stalled; only the energy equation is. The pressure
solve's collapse follows the temperature excursion by one iteration; it does not lead it.

**And the destruction is BIMODAL, which is the discriminating fact.** A mesh defect, a shock or a
bad patch drives a *one-sided* excursion outward from a local seed. Both bounds saturated across
92 % of the domain is a source term that is wrong by a large factor with a sign that varies
cell to cell — not a geometric fault.

## A12.2 🔴 TWENTY ATTEMPTS, ONE CAUSE, AND THE ALGORITHM WAS NEVER TOUCHED

Every surviving attempt dictionary was read and diffed (twelve trees carrying a complete
`system/fvSolution`; ~24 attempts once the in-tree probes of `SMOKE_T` and the four
`PROBE_NOTRANSONIC` launch rounds are counted).

| rung | attempts | what was varied |
|---|---|---|
| **MESH** | **0** | nothing: no level, no family, no mesh treatment |
| **NUMERICS** | ~24 | initialisation route (V2–V7); linear solver / preconditioner / maxIter (`SMOKE_T` tune1, P3, V10–V12); clamp factors (V8, P4, `test.norho`, `test.rhoInf`); relaxation **values** (V2, V3); `bounded`→unbounded `div(phid,p)` (A2/A3); `transonic no` in a **non-graded** diagnostic stage only (NOTRANSONIC R1–R4); decomposition (PARTITION) |
| **MODEL** | 1, unregistered | `SMOKE_T/log.test.sst`, an in-tree probe, never a registered run |

**Identical in all twelve dictionaries, first attempt to last:** `consistent yes`,
`transonic yes`, `nNonOrthogonalCorrectors 1`, and `div(phi,U) bounded Gauss linearUpwind grad(U)`.
**`SMOKE_T` (attempt 1) and `PARTITION_T` (attempt 20) carry byte-equivalent registered
configurations** — `consistent yes, transonic yes, nNonOrth 1, p 0.3, rho 0.05, U 0.5,
pMinFactor 0.1, pMaxFactor 2.0, rhoMin 0.005, rhoMax 1.0, GAMG, linearUpwind`. Twenty attempts and
the registered state is back where it started.

The act recorded this about itself and then did not act on it. `system/fvSolution.startup`
line 3, verbatim: *"the ALGORITHM is unchanged (consistent yes, transonic yes) because changing
it is a different registered change."*

**Sanaa's rule 13 — *never the same action twice on the same state; two stops on the same cause →
climb the ladder*.** Counted honestly: ~20 stops, one cause, and **zero distinct actions on the
pressure–velocity coupling algorithm.** Twenty repetitions of one state do not earn a climb.
This addendum takes the numerics action that has never been taken, with a refutation condition
(A12.6) so it cannot become variant 22.

## A12.3 🔴 THE ONE REGISTERED CHANGE

| dictionary | key | old | new |
|---|---|---|---|
| `system/fvSolution` (graded) **and** `system/fvSolution.startup` (ramp) | `SIMPLE/consistent` | `yes` | `no` |

SIMPLEC → SIMPLE. **The graded dictionary's diff against its pre-registration baseline is this
one key and nothing else** (baselines retained as `system/*.PREREG_BASELINE` in the run tree).

**Mechanism, stated so it can be attacked.** SIMPLEC's momentum corrector
`U = HbyA − rAtU·grad(p)` with `rAtU = 1/(1/rAU − UEqn.H1())` presumes the **full** pressure
update. Every prior attempt ran it against a pressure field explicitly under-relaxed to 0.1–0.3,
so the velocity correction was 3–10× larger than the pressure change that justified it. The
surplus reaches the energy equation through its `Ekp = ½|U|² + p/ρ` source, where `ρ` is relaxed
**10× slower still** (0.01–0.05) and therefore lags the pressure it is divided into. A11.2's
unexplained 34.6× belongs here: at `p max` = 358,971.90 Pa against ρ held near ρ∞ = 0.04503,
`p/ρ` is ~90× its correct value, and `T` — the slave of that source — saturates at 1000 K where
the pressure runs ahead and at 100 K where it lags. **That is the bimodal signature of A12.1,
predicted by the mechanism rather than fitted to it.**

**Chosen over** the first-order-upwind startup leg (already present since V2 — the ramp *is*
first-order and dies the same way), over the SA→SST swap (that is the MODEL rung, not available
while the numerics rung has had zero distinct actions), and over the initialisation route (four
attempts already spent: freestream, potentialFoam, isentropic, ramp).

## A12.4 DISCLOSED DEFECT REPAIR — NOT A SECOND REGISTERED CHANGE

`system/fvSolution.startup` carried `rhoMin 0.02 / rhoMax 0.12`, a **stale copy** from before
**A9** widened the graded clamps to `0.005 / 1.0`. The isentropic initialiser's own minimum
density — its M = 1.5 cap — is ≈ **0.0108 kg/m³**, **below the stale `rhoMin`**. The ramp
therefore began every prior run with its initial field already outside the clamp: precisely the
defect A9 names for pressure, left standing in the ramp for ten rungs. Restored to the values
A9 already registered. **Restoring a stale copy to the registered value is a repair, not a new
change** (standing rule 2, §2d.1).

**Checkpoint policy, not a gate** (Sanaa run-rules 1–3): `endTime 5 → 6000` (§6's cap),
`writeInterval 1 → 6`, `purgeWrite 0 → 2` (last two kept — A11.6's reading applied:
`purgeWrite N` keeps the most recent N, and this is a production run, not a beginning-capture
run). **`writeInterval 6` is bound by the SLOW rate, not the fast one**, for the reason A12.8
gives: 1800 s / 280.7 s = 6.4, so 6 holds the loss under 30 minutes at any rate up to 300
s/iteration. A first draft of this run used `writeInterval 150`, which is inside the 30-minute
rule only at 9.25 s/iteration — a rate measured on a branch this run does not use. **Corrected
before the freeze; recorded because the error is instructive: a checkpoint interval inherits the
honesty of the rate it was divided by.**

## A12.5 A11.3's EXCLUSION LIST — THE MESH ENTRY IS NARROWED, NOT WITHDRAWN

A11.3 lists **mesh** under MEASURED CLEAN on the evidence of trailing-edge base resolution
(13–22 cells across η 0.58–0.88). That measurement stands and is not disturbed. **The entry is
narrowed to what it measured**: TE base resolution is clean; the mesh as a whole is not.
`mesh_T/log.checkMesh` reports **`Mesh OK = false`** — max non-orthogonality **89.4641°**
(average 22.80) with **740,519 faces above 70°**; max skewness **7.9622**; max aspect ratio
**4436.7**; minimum cell determinant **0**, with **5,896,299 cells (28.5 %) below 0.001**.
Coarse reads 88.768 / 6.223 and Medium 89.870 / 12.542 — **identical in kind at every level**,
so this is a property of the VGRID/AFLR3 committee grid as OpenFOAM measures it, not of
resolution. Under §5's two-tier standard it is **disclosed, not gated**, and these numbers are
carried onto the certificate beside the bands as §5 requires.

**It is not the first-failing channel** (A12.1): the `snGrad` and `laplacian` schemes already run
`limited corrected 0.33`, bounding the explicit non-orthogonal correction to 0.49× the orthogonal
part, and the corrector solve is healthy at 6 linear iterations at iteration 1. **The mesh sets
the stiffness; it did not fire the first shot.** If A12.6 refutes the algorithm hypothesis, the
mesh's `nNonOrthogonalCorrectors 1` becomes the next registered candidate.

## A12.6 🔴 PREDICTIONS — REFUTABLE, FROZEN BEFORE THE SOLVER STARTS

| # | channel | twenty prior attempts, measured | R1 predicts |
|---|---|---|---|
| **P1** | `h` initial residual | 0.999999999656 at it 1; **0.999578** at it 100; never fell one digit in 200 iterations | **below 0.99 by iteration 20** |
| **P2** | `limitTemperature` clamped fraction | **92.19 %** at it 49 (60.08 % low + 32.11 % high) | **below 1 % at iteration 50** |
| **P3** | forces | Cd swung −1.77 … **+2.92**; Cl **5.27** at it 198 | Cd in [0, 0.2] and Cl in [0, 1.0] through iteration 300 |
| **P4** | Sanaa §C.7.2 smoke gate | never reached in twenty attempts | CL rising toward 0.45–0.55, CD falling toward 0.02–0.03, no negative density |

> **🔴 REGISTERED EXHAUSTION CLAUSE. If P1 AND P2 both fail, the NUMERICS rung is EXHAUSTED.**
> The ladder then climbs to **MODEL** — §6's registered second closure, k-ω SST — and **no
> further variant of relaxation, clamp, linear solver or initialisation may be registered on
> this act.** Written here so that nobody starts variant 22.

**Advancement is asserted from the force and pressure channels only.** A run that iterates
quickly on a uniform-freestream pressure field is not advancing (the block-195 reading: a
13× speed-up at doing nothing). The first artifacts to read are `limitTemperature` at iteration
50 and `postProcessing/forceCoeffs/0/coefficient.dat`, never ExecutionTime.

## A12.7 RANKS, AND A GRID-FAMILY FINDING FOR SANAA'S DESK

**Verified from the files on disk, against §5's `[verify from the grid page]` flag.** §5 estimated
the committee Tiny/Coarse/Medium at *"about 2 M, 6 M, 16 M cells for the half model"*. The
Boeing/Babcock cell-centred family actually holds:

| level | cells | ratio to previous | linear *r* |
|---|---|---|---|
| Tiny | **20,657,615** | — | — |
| Coarse | **26,271,819** | 1.272 | **1.084** |
| Medium | **33,683,206** | 1.282 | **1.086** |

**Tiny is 10× the §5 estimate**, and **a Roache triple at r ≈ 1.08 cannot carry a defensible
GCI** — §8's family band is at risk on this family, and §7's 8/16/32 rank ladder was sized for a
grid 10× smaller. **Recorded as a finding for Sanaa's desk; the levels are NOT re-labelled and no
gate is altered here.** Retrieval is not a blocker: both committee families are on disk
(`/home/ubuntu/crm-data/grids/DPW6_Boeing_Babcock_WB_ae2.75_CC/*.b8.ugrid`, T/C/M/F, and the NASA
GeoLab VGRID set), and the cell-centred family is the correct one for a cell-centred solver.

**R1 therefore runs on the 32 ranks §A allocates to this lane, not §7's 8.** Stated as a
deviation with its reason, not taken quietly. It is a resource decision and changes no gate.

## A12.8 🔴 COST — AND A CORRECTION TO WHICH RATE MAY BE QUOTED (standing rule 12)

**This act holds two measured iteration rates and they differ by 30×. Only one of them belongs
to the registered physics, and it is the slow one.**

| rate | where it was measured | what was running |
|---|---|---|
| **9.25 s/it** | `PROBE_NOTRANSONIC_T` stage 1, board 200 | `transonic no`, symmetric `DICPCG` pressure matrix — **the A10.4 diagnostic branch, which §C.6 does not register and which produces no graded answer** |
| **280.7 s/it** | the `CRM-WB-D8G-PARTITION` cost basis | the **registered** branch: `transonic yes`, uncapped GAMG — but measured **while the pressure equation was diverging** (760 linear iterations by outer iteration 3, `DIAG_EARLY_T`) |

**A first draft of this addendum costed R1 at 9.25 s/it. That was wrong and is struck
pre-compute**: it quoted the rate of a branch this run does not use. The correction is recorded
rather than silently swapped, because it is the same class of error as A11.6's — a number
carried across from a run that was not the run.

**Registered basis: the SLOW rate, deliberately**, exactly as `PARTITION` reasoned. 6,000 × 280.7
× 32 / 60 = **898,240 core-minutes** = 14,971 core-h = **$768 derived**; ramp 200 iterations =
**29,941 core-min**. Cap registered at **3× = 2,694,720 core-minutes.**

> **P5, a REGISTERED RATE PREDICTION and a second refutation channel.** 280.7 s/iteration is the
> rate of a *sick* pressure equation — a healthy compressible SIMPLE solve on this grid should
> need tens of linear iterations per solve, not 760. **R1 predicts the rate falls below
> 30 s/iteration by iteration 100.** If it is still above 100 s/iteration at iteration 100, the
> pressure equation is still ill-conditioned, which is independent evidence against A12.3's
> mechanism and counts alongside P1/P2 toward the A12.6 exhaustion clause. **The cost band is
> therefore itself a measurement, not an allowance** — and the true spend is expected near the
> 29,600 core-minute (9.25 s/it) end, which is why the pessimistic figure is registered and the
> optimistic one is not.

`cost_basis`: wall time from the solver's own `ExecutionTime`; the $0.0513/core-h rate is
**reported-by-owner, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). Directive #17: **no cap kills this run**; the cap is registered,
and a run that crosses it is graded `NOT A RESULT` and the cap is never raised. The
estimate-versus-actual row is owed to `docs/COST_CALIBRATION.md` at completion, and must score
the actual against **898,240** while recording that **29,600 was struck pre-compute and why**.

## A12.9 THE RUN THIS ADDENDUM REGISTERS

**`CRM-WB-D8G-SOLVE-T-R1`**, case `/home/ubuntu/certonomous-runs/CRM_WB_D8G/SOLVE_T_R1`,
32 ranks, `rhoSimpleFoam`, Spalart–Allmaras, `transonic yes`, launched by the runner and by
nothing else (Sanaa item 19), as `ubuntu`, `STARTUP_ITERS=200`, from the `potentialFoam` +
isentropic initialisation of §C.6. **This addendum is the registration of record**; the
case-local `REGISTRATION_R1.md` is a working copy and is not authoritative where the two differ.

---

# ADDENDUM 14 — 2026-09-13, R1 IS REFUTED, THE EXHAUSTION CLAUSE FIRES, AND SST IS REGISTERED AS A TEST OF A DIAGNOSIS RATHER THAN AS AN ATTEMPT. Version 1.13.

**lines whose number changed above this section: 0**

## A14.1 R1's RESULT — `GATE FAIL`, AND A12.6 FIRES ON ITS OWN TERMS

`CRM-WB-D8G-SOLVE-T-R1` launched 2026-09-13T06:59:48Z (pid 1403615, 32 ranks, freeze
`300080d0`, grading freeze stamped `PINNED`), reached both registered reading points, and was
stopped at iteration 102.

| | A12.6 predicted | measured | |
|---|---|---|---|
| **P1** | `h` initial residual **< 0.99 by it 20** | **exactly 1** at it 20, 30, 50 and 70 | **FAIL** |
| **P2** | clamped fraction **< 1 % at it 50** | **99.60 %** at it 50; **99.84 %** at it 90 | **FAIL** |
| **P3** | Cd ∈ [0, 0.2], Cl ∈ [0, 1.0] | **Cd −4.100835176057e+15, Cl −1.592849706116e+16** | **FAIL** |

A12.6: *"If P1 AND P2 both fail, the NUMERICS rung is EXHAUSTED."* **It does.**

**A12.3's mechanism is REFUTED.** `consistent yes → no` was applied correctly to both
dictionaries — the graded diff was that one key — and the failure is **unchanged in kind and
worse in degree**: 99.84 % clamped against the 92.19 % baseline, forces at 1e16 against order 1.
**The pressure–velocity coupling algorithm is not the cause.** One further suspect eliminated,
which is the twenty-first elimination this act has performed.

**A real difference the successor must not average away: the clamp split INVERTED.** The
baseline ran 60.08 % low / 32.11 % high; R1 ran 37.59 % low / 62.25 % high.

**STOPPED ON SANAA'S ITEM 12** — *"residual growth or a field outside bounds → stop"* — a
**physics** rule, **not a cap; directive #17 untouched**: 519 core-minutes against a registered
898,240. SIGTERM to the `mpirun` alone so the launcher's own failed-ramp path ran:
`STAGE 1 rc=1`, registered dictionaries restored md5-identically, **stage 2 never entered**,
saving 6,000 iterations of garbage. Record: `SOLVE_T_R1/STOP_RECORD_R1.md`.

## A14.2 🔴 TWO INSTRUMENT FAILURES THAT OUTLIVE THIS ACT

**(a) A residual is a ratio, and a ratio whose denominator is diverging is not a convergence
measurement.** At iteration 70 the pressure equation reported an initial residual of
**5.7e-29** while Cd sat at **−3.7e15**; `Ux` fell to 0.013 alongside. **Every residual channel
reported convergence while the field was garbage** — the normalisation denominator diverges with
the field, so the *normalised* residual collapses. **Successor rungs gate on the FIELD, never on
the normalised residual.** This belongs with the act's other instrument failures and is in the
channel this lab trusts most.

**(b) A rate is not a health channel.** A12.8's P5 predicted the iteration rate would fall below
30 s/it, on the reasoning that a healthy pressure equation solves faster than a sick one. **It
came true — 10.81 s/it against a 280.7 s/it basis — while the run destroyed itself.** That is
exactly the block-195 trap the entry's own advancement rule warns about, and the predictor was
walked into it by its author. **A predictor that a dying run satisfies is worse than no
predictor, because it reads as corroboration.** P5 is struck as a health channel and retained
only as a cost input.

## A14.3 DATED REPAIR — THE CLOSURE GUARD, LANDED AT `0abc91e9`

`launch_crm_wb_v2.sh:84` carried `grep -qE 'RASModel +SpalartAllmaras;' … || fail`, a **hard
refusal of every closure but Spalart–Allmaras**. §C.6 registers SST as the second closure, §C.7.4
requires it on Coarse and Medium for the junction bubble, and A12.6 climbs to it: **the launcher
would have refused the successor its own act registers**, with a message pointing the reader at
the case dictionary rather than at the guard. **Widened to a closed registered set, never
deleted** — defaulted to the primary so R1-style runs are unchanged, checked against
`{SpalartAllmaras, kOmegaSST}`, asserted against the dictionary that will run, and **logged**, so
`LAUNCH.log` names the closure it never previously carried. Launcher sha256 after repair:
`1947e507bcb4477fca7d60aa76c203bcc496e41f44d905bb72e21212869ee0f4`.

## A14.4 🔴 THE DIAGNOSIS, REGISTERED AS A FALSIFIABLE PREDICTION **BEFORE** SST RUNS

This is the point of the run and the reason it is not attempt twenty-two.

> **REGISTERED DIAGNOSIS (chief's, recorded here before its test):** an `h` residual pinned at 1
> with two-thirds of cells clamped from iteration ~40, on a wall-resolved high-aspect-ratio
> committee grid, is **the classic segregated-steady-solver startup failure — not a closure
> one.** R1 is evidence for it: changing the coupling algorithm moved nothing.
>
> **REGISTERED PREDICTION D:** if the diagnosis is right, **SST pins the same way** — S1 and S2
> below both fail, with a clamped fraction above 90 % by time step 50.
>
> **BOTH OUTCOMES ARE INFORMATIVE, WHICH IS NEW ON THIS ACT.** An SST that **pins** is
> **positive evidence** for the solver-path diagnosis and the LTS rung is entered with support
> rather than as a guess. An SST that **clears** **refutes the diagnosis outright**, is the
> larger finding of the two, and makes the junction-bubble comparison of §C.7.4 available at the
> same time.
>
> **What SST does NOT test:** the mesh. Rung 1 is untouched either way.

## A14.5 THE SST RUN — ONE REGISTERED CHANGE AGAINST THE R1 BASELINE

**Baseline:** R1 exactly as it ran — same mesh, BCs, schemes, freestream, clamps, 32 ranks, same
two-stage ramp, `consistent no` retained (A12's change stands; it is the baseline now, not the
variable).

| file | key | R1 | SST rung |
|---|---|---|---|
| `constant/turbulenceProperties` | `RASModel` | `SpalartAllmaras` | `kOmegaSST` |
| launcher argv | `CLOSURE` | *(default)* | `kOmegaSST` |

**FIELDS THAT MUST BE BUILT, AND THEIR REGISTERED FREESTREAM VALUES.** SA carries `nuTilda`;
SST carries `k` and `omega`, which do not exist in `0.orig`. Derived from the §3 registered
state (ρ∞ = 0.04503298815, U∞ = 300.019 m/s, c_ref = 7.00532 m, Re = 5×10⁶), **not chosen by
eye**: μ = ρUc/Re = **1.89298×10⁻⁵ Pa·s**, ν = **4.20346×10⁻⁴ m²/s**, a∞ = U/0.85 =
**352.96 m/s**. NASA TMR freestream convention for SST:

- **k∞ = 9×10⁻⁹ a∞² = 1.1212×10⁻³ m²/s²**
- **ω∞ = 10⁻⁶ ρ∞ a∞² / μ = 296.38 s⁻¹**

**Self-check, and it is the reason these values are trusted:** ν_t∞ = k∞/ω∞ = 3.783×10⁻⁶ m²/s,
so **ν_t∞/ν∞ = 0.0090** — TMR's stated SST freestream ratio to two figures, reproduced from an
independent path. The same state also reproduces SA's registered `nuTilda` = 3ν =
1.26104×10⁻³ against the 0.0012610370502 already in `0.orig`.

**Wall treatment (registered, and to be confirmed by the y+ readback, not assumed):** the
committee grid is wall-resolved, so **no wall functions on the velocity scale** — `k`
`fixedValue 1e-12` at `wing`/`body`, `omega` `omegaWallFunction` (its viscous-sublayer limit is
the wall-resolved form), `nut` `nutLowReWallFunction`. `symmetry` symmetric, `farfield`
inletOutlet on the freestream values above.

## A14.6 SST's REFUTATION CONDITIONS — NUMERIC, WRITTEN FIRST

| # | channel | threshold |
|---|---|---|
| **S1** | `h` initial residual | **< 0.99 by iteration 20** |
| **S2** | `limitTemperature` clamped fraction | **< 1 % at iteration 50** |
| **S3** | forces | Cd ∈ [0, 0.2] and Cl ∈ [0, 1.0] through iteration 300 |
| **S4** | field gate, replacing P5 | `p` **absolute** max < 2 × p₀ = 12,854 Pa and `max\|U\|` < 2 U∞. **Read from the field, never from a normalised residual (A14.2a).** |

> **If S1 and S2 both fail, PREDICTION D IS CONFIRMED**, the closure is eliminated, and the act
> proceeds to the **pseudo-transient (LTS) rung** — drafted at
> `verification/campaign/CRM_WB_D8G_ADDENDUM_13_LTS_RUNG_DRAFT.md`, to be folded in as its own
> addendum. **No further steady-`rhoSimpleFoam` variant may be registered on this act**, of any
> closure, relaxation, clamp, linear solver or initialisation.

## A14.7 COST

Measured R1 rate on this mesh at 32 ranks, same solver and ramp: **10.81 s/iteration** (from
R1's own `ExecutionTime`, 973.28 s over 90 iterations) — **a measured rate from the run
immediately preceding, not carried across from another branch.** SST adds a second turbulence
transport equation, so the honest expectation is dearer per iteration, and the **cap is taken
from the worst case rather than the prediction**, as M6I's ×2.65-against-a-×1.6-estimate
requires: worst case remains `rhoSimpleFoam` at **280.7 s/it**.

- Reading points (300 iterations) at the measured rate: **1,730 core-minutes**.
- To the §6 cap of 6,000 iterations at the measured rate: **34,592 core-minutes** (~$29.6 derived).
- **Cap registered at the worst case × 3 = 2,694,720 core-minutes.**

`cost_basis`: wall from the solver's own `ExecutionTime`; $0.0513/core-h **reported-by-owner, not
measured** (`COMPUTE_BUDGET_CHARTER` §5). Directive #17: no cap kills the run. Calibration row
owed to `docs/COST_CALIBRATION.md`, and it must score **R1 as a stopped run** rather than as a
ratio against a length never attempted.

## A14.8 🔴 A STRUCTURAL DEFECT IN HOW THIS ACT PINS ITSELF — AND THE ONE-LINE REPAIR

R1's queue entry named **this pre-registration as comparator #1** in `grading_freeze`.
`grader_freeze_gate.py:575–587` computes `disk = blob_sha(disk_p.read_bytes())` and awards
`PINNED` **only if `disk == frozen`**. **So appending any addendum to this file flips a live
run's freeze to `MISMATCH` on a registration that never changed** — bookkeeping corrupting a
physics verdict. ADDENDUM 13 was therefore held out of this file while R1 was live, and this
addendum was written only after R1 stopped.

**There is no commit-only mode in that field** — every state it can report is computed from the
disk read. But **the repair needs no tooling change, because the conflict is self-inflicted**:

- `prereg_commit` + `prereg_path` is **already a pure commit pin**. `check_prereg_at_commit` runs
  `git cat-file -e <sha>:<path>` and **never reads the disk**, so it is stable under every future
  addendum. Nothing needs to change there.
- `grading_freeze` is for **comparators** — the instruments that turn fields into verdicts. Those
  do not grow addenda and *should* be byte-compared to disk.

> **REGISTERED FROM HERE ON: this pre-registration is NOT named in `grading_freeze`.** It is
> pinned by `prereg_commit`, by the field designed for it. **The two pins have different jobs and
> want different semantics — a registration asks "did this text exist at this commit", a
> comparator asks "is the file about to run byte-identical to the frozen one" — and conflating
> them put a deliberately growing document under a byte-identity rule.**
