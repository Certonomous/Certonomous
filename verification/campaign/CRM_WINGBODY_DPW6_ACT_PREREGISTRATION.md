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
