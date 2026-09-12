# M6H1 — ONERA M6 at M∞ = 0.8395, **HYPERBOLIC (C/O) MESH CLASS**, AGARD AR-138 TEST 2308

<!-- ============================ DRAFT BANNER — STRIKE THIS ONE BLOCK ============================ -->
> ## 🟠 DRAFT. **NOT FROZEN. NOT AUTHORISED. NO COMPUTE HAS RUN UNDER IT.** §12's freeze block is BLANK.
> Drafted by a cfd `lab-lane`, 2026-09-12, on the cfd-supervisor's brief. **Check 4 — pre-registration
> COMMITTED before compute — is the supervisor's, is personal, and is not delegated to this lane.**
> **THIS BANNER IS A SINGLE BLOCK BOUNDED BY THE TWO COMMENT RULES ABOVE AND BELOW IT, SO IT CAN BE
> STRUCK AT FREEZE IN ONE EDIT.**
> **SUBMISSIONS PARKED (rule 7). No agent's message is Sanaa's consent (rule 9).**
<!-- ========================== END DRAFT BANNER — STRIKE TO HERE ================================= -->

---

## 0. WHAT SANAA ASKED FOR, AND WHAT THE PAPER ACTUALLY SAYS

**Sanaa, 2026-09-10T20:20Z:** *"for M6 just have the cfd team re read the onera m6 paper and take the
same mesh class."*
**Sanaa, 2026-09-10T20:57Z:** *"sound sgood then onera M6 can get the c mesh and snappy hex or whatever
it needs"*
**Sanaa, 2026-09-10T20:40Z:** *"M6 other families, I want info on the run where the physics is good."*

**The paper has been re-read. §1 records what it says, including the answer to the mesh-class question
— which is not the answer the instruction anticipates, and is reported as measured rather than as
asked.**

---

## 1. THE PAPER — RULE 15, VERIFIED BY TITLE PAGE, NOT BY FILENAME

`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`, **opened and read at
its title page** (PDF page 1): *AGARD-AR-138, NORTH ATLANTIC TREATY ORGANIZATION, ADVISORY GROUP FOR
AEROSPACE RESEARCH AND DEVELOPMENT, AGARD Advisory Report No.138,* **EXPERIMENTAL DATA BASE FOR
COMPUTER PROGRAM ASSESSMENT**, *REPORT OF THE FLUID DYNAMICS PANEL WORKING GROUP 04*; PDF page 2:
**Published May 1979, ISBN 92-835-1323-1**; PDF page 3 cataloguing block: **642 pages**.
**Appendix B, 3-D configurations, item B1:** *PRESSURE DISTRIBUTIONS ON THE ONERA-M6-WING AT TRANSONIC
MACH NUMBERS, by V. Schmitt and F. Charpin, ONERA, 92320 Châtillon, France.*

**Not verified by the `.txt` sidecar.** The sidecar is a lossy OCR of this scan and §1.3 records a
place where it is wrong by a factor of 13.8.

### 1.1 🔴 THE MESH-CLASS QUESTION HAS AN HONEST ANSWER AND IT IS "THE PAPER SPECIFIES NO MESH"

**AGARD AR-138 is an EXPERIMENTAL data base.** Appendix B1 is a wind-tunnel report: model geometry,
tunnel calibration, test conditions, and tabulated surface pressures. **It contains no computational
grid, no grid topology and no grid-generation procedure. There is no "mesh class" in it to take.**

**Saying so is the finding, not a refusal to answer.** What B1 *does* specify — geometry to seven
decimal places and a Reynolds number — determines completely what a mesh must deliver, and §2–§4
derive that. **The one sense in which the paper does carry a discretisation is Table B1-1's own
surface point distribution**, and §1.3 shows the lab's working copy of that table deleted exactly the
points that matter most. **Taking "the same mesh class" therefore means, concretely: take Table B1-1's
own clustering, all 72 rows, including the eight the lab dropped.**

### 1.2 THE CONFIGURATION AND THE TEST POINT — READ OFF THE PAGES, NOT INHERITED

| quantity | value | where read |
|---|---|---|
| designation | **ONERA Wing M6**, semi-span wing, **no body** | B1 §1.2 1.1/1.2, 2.2 |
| aspect ratio | **3.8** | B1 §2.1.2 |
| leading-edge sweep | **30°** | B1 §2.1.3 |
| trailing-edge sweep | **15.8°** | B1 §2.1.4 |
| taper ratio | **0.562** | B1 §2.1.5 |
| twist | **none** | B1 §2.1.6 |
| **mean aerodynamic chord** | **c = 0.64607 m** | B1 §2.1.7 |
| **semispan** | **b = 1.1963 m** | B1 §2.1.8 |
| airfoil | **ONERA D**, symmetrical, **one section**, conical generation | B1 §2.1.9–2.1.11 |
| wing tip | **truncation parallel to the root + a half body of revolution** (rounded, NOT a flat cut) | B1 §2.1.13 |
| fabrication tolerance | **0.15 mm** | B1 §2.3 |
| tunnel | ONERA **S2MA**, Modane; square section 1.170 × 1.150 m | B1 §3.1, 3.3.2 |
| **TEST 2308** | **M₀ = 0.8395, α = 3.06°, Re_c = 11.72 × 10⁶** | **PDF page B1-20, read from the page** |
| pressure sections | **seven** spanwise stations, SECTION 1…7 | Table B1-14 column headers |

**TEST 2308 is the registered condition.** It is the canonical M6 transonic point and it is read from
the printed page, not recalled.

### 1.3 🔴 THE TRAILING EDGE IS **BLUNT**, AND THE LAB'S WORKING GEOMETRY FILE CLOSED IT SHARP

**Table B1-1 (PDF page B1-7), read from the page image**, ends:

| x/l | z/l |
|---:|---:|
| 0.9885252 | 0.0021257 |
| 0.9921438 | 0.0016778 |
| 0.9952080 | 0.0012985 |
| 0.9978030 | 0.0009773 |
| **1.0000000** | **0.0007052** |

**z/l at x/l = 1.0 is NOT ZERO. The ONERA D section closes on a finite base.**

- **TE base thickness = 2 × 0.0007052 = 0.0014104 chord = 0.1410 % of local chord.**
- At the root chord 0.8059 m that is **1.1366 × 10⁻³ m**; at the MAC, 9.1122 × 10⁻⁴ m.
- Upper-surface taper over the last four tabulated panels is **constant**: dz/dx = −0.1238, −0.1202,
  −0.1234 → **7.03°**, i.e. an included TE wedge of **14.06°**. *(M6CP1 Addendum 7 measured 7.06° from
  the committed reference file; dafoam measured 7.05° independently. Three routes, three digits.)*
- Maximum z/l = 0.0489296 → **t/c = 9.79 %**.

**🔴 THE LOAD-BEARING DIGIT, AND HOW IT WAS SETTLED.** The scan is poor and the final z/l can be read
as `0.0007052` or `0.0097052`. **It was not settled by eye.** The three preceding panels give a stable
slope of −0.1234; linear extrapolation to x/l = 1.0 predicts **0.0007186**. Residual against
`0.0007052` is **1.34 × 10⁻⁵**; against `0.0097052`, **8.99 × 10⁻³` — **669× worse**. **The digit is a
zero.** Independently, `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` (72 rows,
title-page verified, committed 2026-09-03) carries `1.0000000  0.0007052` literally. **Two independent
routes, one arithmetic and one archival, agree.**

**AND THE DEFECT THIS EXPOSES.** `verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat` — the
file whose name says `sharp` — holds **63 points, not 72**. Parsed:

- it reproduces the reference to point 61, **`x = 1.0000000, z = 0.0007052`**, correctly;
- it **deletes the reference's eight aft points** between x/l = 0.9578511 and 1.0 — the densest
  clustering in the whole table, exactly where the section is thinnest;
- it **appends a synthetic 63rd point at `x = 1.0055000, z = 0.0000000`** — **0.55 % of chord BEYOND
  the trailing edge** — forcing a sharp closure the reference does not have.

**That is an unregistered departure from the reference geometry, and it is upstream of every M6 route
built from that file.** *(It is recorded here, not repaired here: repairing another campaign's
committed input is not this registration's business. M6H1 simply does not use it — see §3.)*

---

## 2. y⁺ AND THE BOUNDARY LAYER, STATED **BEFORE** A CORE-MINUTE IS SPENT

**Derived from M, Re and chord alone, as required — and deliberately by a route that needs no
temperature**, so no thermodynamic assumption enters:

> Cf = 0.0576 · Re_c^(−1/5) and u_τ = U√(Cf/2), so
> **y = y⁺ · c / (Re_c · √(Cf/2))** — U and ν cancel.
> δ/c = 0.37 · Re_c^(−1/5), likewise.

At **Re_c = 11.72 × 10⁶, c = 0.64607 m**:

| quantity | value |
|---|---|
| **Cf** | **0.002221** |
| **δ at the MAC** | **9.2193 × 10⁻³ m = 1.4270 % of MAC** |
| **first-layer height per unit y⁺** | **1.6540 × 10⁻⁶ m** |

| target y⁺ | **required first layer (m)** |
|---:|---:|
| **1** | **1.6540 × 10⁻⁶** |
| 5 | 8.2702 × 10⁻⁶ |
| **30** | **4.9621 × 10⁻⁵** |
| 100 | 1.6540 × 10⁻⁴ |
| 300 | 4.9621 × 10⁻⁴ |

**THE CLAIM LICENCE IS FIXED HERE, IN ADVANCE, AND IS NOT REOPENED AFTER THE RUN (§5, H-G3).**

---

## 3. 🔴 WHY THE MESH CLASS IS **HYPERBOLIC / C-TYPE** AND NOT AN OCTREE — THE ARITHMETIC

Two requirements sit on the same wall, and they differ by **three orders of magnitude**:

| requirement | length |
|---|---|
| resolve the **TE base** with ≥ 8 cells | **1.4208 × 10⁻⁴ m** (root) |
| resolve the **wall layer** at y⁺ = 1 | **1.6540 × 10⁻⁶ m** |
| span the **boundary layer** | 9.2193 × 10⁻³ m |
| reach the **farfield** at 25 MAC | 16.152 m |

**A snappyHexMesh octree cell is ISOTROPIC.** Route (d)'s base cell is 0.5 m (level 4 = 0.03125 m, as
built), so:

| snappy level | cell (m) | **cells across the root TE base** |
|---:|---:|---:|
| **4 (as built)** | 3.1250 × 10⁻² | **0.04** |
| 6 | 7.8125 × 10⁻³ | 0.15 |
| 8 | 1.9531 × 10⁻³ | 0.58 |
| 10 | 4.8828 × 10⁻⁴ | 2.33 |
| **12** | **1.2207 × 10⁻⁴** | **9.31** |

> **Level 12 is the first level that puts ≥ 8 cells across the trailing-edge base — 256× finer than
> the mesh route (d) actually built.** And that cell is isotropic: 1.22 × 10⁻⁴ m **chordwise and
> spanwise too**, over a surface that is ~1.2 m². Even used only in a narrow TE band it forces four
> further levels of 2:1 buffering outward.
> **At level 4, as built, the trailing-edge base is 0.04 cells wide. snappy cannot represent it at
> all.**

**A hyperbolic C/O mesh decouples the three lengths by construction, because its cells are
ANISOTROPIC** — chordwise clustering at the TE, wall-normal clustering in the layer, spanwise coarse.
Marching from the surface with r = 1.15:

| y⁺ target | s₀ (m) | **layers to march 16.152 m** | layers inside δ |
|---:|---:|---:|---:|
| **1** | 1.6540 × 10⁻⁶ | **101.6** | 48.2 |
| 30 | 4.9621 × 10⁻⁵ | 77.2 | 24.1 |
| 100 | 1.6540 × 10⁻⁴ | 68.6 | — |

> **A fully wall-resolved M6 is ~102 normal layers and ≈ 1.65 M cells.** That is the whole case for
> the mesh class, and it is why **Sanaa's instinct — "onera M6 can get the c mesh" — is correct and
> now has a number behind it.**

**THE CAPABILITY EXISTS ON THIS BOX AND HAS BEEN EXERCISED.** `pyHyp` runs inside
`dafoam-subpclu:v1`: `verification/runs/CRM_M085_runs/PYHYP_ROUTE_PROBE/PROBE_RESULT.md` records
**53 of 53 layers marched, Min Quality 0.08110 and Min Volume 9.49 × 10⁻¹³ — positive at EVERY layer**;
`verification/runs/M6SR_runs/L1/work/volumeMesh.xyz` is a 111 MB M6 hyperbolic volume mesh already on
disk. **That probe cleared the TOOLCHAIN, not this configuration**, and is cited as capability only.

### 3.1 THE SURFACE THIS REGISTRATION USES, AND WHY

**Source of truth: `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`, all 72 rows,
with the base left BLUNT at z/l = 0.0007052.** Not the 63-row `_sharp` file (§1.3).

**Measured corroboration that a faithful M6 surface already exists on this box.** Route (d)'s
`verification/runs/M6C2_runs/ROUTE_D/L1/constant/triSurface/m6_mp_L1.stl` carries a **`wing_base`
solid, 5,376 vertices**, and its base thickness measured in nine spanwise bands is:

| y/b | 0.054 | 0.272 | 0.489 | 0.706 | 0.924 |
|---|---:|---:|---:|---:|---:|
| base dz (m) | 1.1366e-03 | 1.0236e-03 | 9.1926e-04 | 8.0622e-04 | 7.0188e-04 |
| **% local chord** | **0.1382** | **0.1367** | **0.1349** | **0.1353** | **0.1328** |

**Against the reference's 0.1410 % that is agreement to 2.0–5.8 %. Route (d)'s SURFACE is faithful at
the trailing edge; it was its VOLUME discretisation that could not see it (0.04 cells).** Bounding box
semispan **1.196300 m**, identical to B1 §2.1.8's 1.1963 m.

### 3.2 🔴 DISCLOSURE — HOW H-G0's ±10 % TOLERANCE WAS CHOSEN, AND WHY THAT IS NOT GATE-FITTING

**Stated plainly because the alternative is to let a reader discover it.** The measurements in §3.1
were taken **before** §7's H-G0 threshold was written, and they show a 2.0–5.8 % deviation. **A reader
is entitled to ask whether ±10 % was reverse-engineered from them.**

**Two reasons it is not, and one concession.**

1. **H-G0 does not grade the surface measured in §3.1.** It grades **M6H1's own surface**, which does
   not exist and will be generated from `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`
   by a different path. The threshold was not set against the object it will judge.
2. **±10 % has an independent basis:** AGARD B1 §2.3 records the model's own **fabrication tolerance
   as 0.15 mm**. Against a root base of 1.1366 mm that is **±13.2 %** — so a tolerance tighter than the
   physical wing was built to would fail real geometry for being real. **±10 % sits just inside the
   manufacturing tolerance of the actual wind-tunnel model**, which is a defensible floor and is
   independent of any measurement taken on this box.
3. **The concession:** had §3.1 measured 30 % deviation, this lane cannot honestly claim it would have
   written ±10 % anyway. **The order of events is disclosed so the freeze carries it.**

**Pre-compute amendment condition (rule 2):** this section was added **before any compute under this
document**. The condition and how it was checked: **`verification/runs/M6H1_runs/` DOES NOT EXIST** —
verified by a reader first SHOWN ABLE to see a populated directory (`verification/runs/M6C2_runs`,
non-empty) before its absence was believed (rule 3).

---

## 4. THE MESH FAMILY

Three levels, nested, so a Roache triple is **possible** — never assumed. **Refinement is applied in
all three structured directions so the ratio is uniform; the DELIVERED ratio is computed from measured
cell counts and a nominal ratio is never quoted** (rule 5).

| level | chordwise × spanwise × normal | surface cells | **volume cells (predicted)** | cells across TE base |
|---|---|---:|---:|---:|
| **H-L1** | 201 × 65 × 97 | 12,800 | **1,241,600** | 9 |
| **H-L2** | 301 × 97 × 129 | 28,800 | **2,793,600** | 13 |
| **H-L3** | 401 × 129 × 161 | 51,200 | **4,966,400** | 17 |

**These are PREDICTIONS from the dictionaries, registered before the build, and §7's H-G1 grades the
ACHIEVED counts against them. A number computed from the input dict is not an observation of the
output** — the achieved counts come from `checkMesh`'s own `cells:` line.

**s₀ = 1.6540 × 10⁻⁶ m at every level** (y⁺ = 1 target), **r = 1.15**, march 16.152 m = 25 MAC.
**The first layer is NOT refined with the level.** Refining s₀ alongside the surface would change the
wall treatment between levels and make the triple a comparison of two different physics; holding it
fixed is what makes the triple a discretisation study.

---

## 5. THE CLAIM LICENCE, FIXED BEFORE THE RUN

**M6's most valuable output to date cost nothing and came first: route (d)'s registration forbade
every aerodynamic claim in advance on a y⁺ of 9,447. This registration does the same thing, in
advance, against the ACHIEVED y⁺ measured on the solved field.**

| achieved y⁺ max on the wing | Cp at the 7 sections | shock position | CL / CD / CM | Cf |
|---|---|---|---|---|
| **≤ 5** | **LICENSED** | **LICENSED** | **LICENSED** | **LICENSED** |
| 5 – 30 | **FORBIDDEN** — the buffer layer is modelled by neither branch | FORBIDDEN | FORBIDDEN | FORBIDDEN |
| 30 – 300 (wall functions consistently applied) | LICENSED | LICENSED | LICENSED | **FORBIDDEN** |
| **> 300** | **FORBIDDEN** | **FORBIDDEN** | **FORBIDDEN** | **FORBIDDEN** |

**This table is a gate (H-G3) and is not reopened after the run.** *What result would have failed this
test?* **Any achieved y⁺ max above 5 with s₀ registered at the y⁺ = 1 value would fail it** — and that
is a live possibility, not a formality: it is exactly what happens if the extrusion does not deliver
the requested first layer, which is the DrivAer thread's entire subject matter.

---

## 6. WHAT THIS REGISTRATION DOES NOT DO

- **It does not lift M6CP1's park, M6C1's `BLOCKED`, or M6C2's `GATE FAIL` / `NOT A RESULT`.** Those
  are other documents' verdicts on other meshes.
- **It does not repair `om6_wing_section_sharp.dat`.** §1.3 records the defect; repair is that
  campaign's.
- **It does not claim the octree route is wrong in general** — only that, measured, it needs level 12
  at this trailing edge.
- **It does not decide whether M6's earlier failures are mesh or solver.** M6CP1 Addendum 7 §A7.4
  referred that upward and it stays referred.

---

## 7. GATES

**All gates are `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`. No other word.**
**Every gate below is followed by the sentence "what result would have failed this test?", because a
criterion with no failing branch is empty however clean its arithmetic.**

| id | gate | threshold | label if not met |
|---|---|---|---|
| **H-G0** | **Reference admission of the surface** | TE base thickness within **±10 %** of 0.1410 % local chord at **every** one of ≥ 9 spanwise stations; max t/c within ±2 % of 9.79 %; semispan within ±0.5 % of 1.1963 m | **BLOCKED** — the geometry is not the M6 |
| **H-G1** | **Mesh admission**, per level, own `checkMesh -allGeometry -allTopology` in this tree | max non-orthogonality **≤ 70**, max skewness **≤ 4**, **zero** negative-volume cells, and pyHyp **Min Quality > 0 at every layer**; achieved cell count within ±2 % of §4 | **NOT A RESULT** for that level |
| **H-G2** | **TE resolution** | **≥ 8 cells across the TE base at every spanwise station**, and non-decreasing under refinement | **NOT A RESULT** for that level, and every §5 claim FORBIDDEN |
| **H-G3** | **y⁺ admission**, measured on the solved field | §5's table, applied to the achieved y⁺ max on the wing patch | the claims §5 forbids are **FORBIDDEN**; the run is not thereby `NOT A RESULT` |
| **H-G4** | **Completion**, rule 4 in full | rc = 0; `End`; last time == `endTime`; fields present; `ExecutionTime` count consistent; **every field at `endTime` newer than the case's own `0/U`** (age guard) | **NOT A RESULT** |
| **H-G5** | **Iterative convergence** | initial residuals for `Ux Uy Uz e p k omega` **all ≤ 1e-4**, AND max \|ΔCD\| over the **last 500 iterations ≤ 1.0 drag count** | **GATE FAIL** |
| **H-G6** | **Cp against AGARD Table B1-14**, the seven sections | **RMS ΔCp ≤ 0.05** at each section, upper and lower surface separately, **excluding** the four points nearest the shock at each section *(the shock is a discontinuity and a pointwise RMS there measures grid alignment, not physics)* | **GATE FAIL** |
| **H-G7** | **Roache triple**, only if three levels clear H-G1 and H-G2 | rule 5's order unaltered, on the **delivered** ratio from measured cell counts; GCI at Fs = 1.25; **no GCI quoted when the three values are not monotone** | **NOT A RESULT** |

**Gate order:** H-G0 → H-G1 → H-G2 → H-G3 → H-G4 → H-G5 → H-G6 → H-G7.
**A gate can only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the reverse.**

### 7.1 WHAT RESULT WOULD HAVE FAILED EACH TEST

- **H-G0.** A surface built from `om6_wing_section_sharp.dat` fails outright: its base is **0.0000**
  at x/l = 1.0055, i.e. **0 % against a 0.1410 % threshold**. M6CP1's capped surface fails likewise.
  **The gate has a measured failing example already on disk, which is the strongest form of this
  answer.**
- **H-G1.** `CRM_WINGALONE` L1 failed this exact gate at **min quality −0.05046 at layer 3**, and L3
  at **non-orthogonality 79.3672 > 70**. Two measured failures of the same instrument class.
- **H-G2.** Route (d) L1 gives **0.04 cells** across the base. Fails by 200×.
- **H-G3.** Route (d)'s solve measured **y⁺ ≈ 9,447**, which the table forbids everything at.
- **H-G4.** M6C2's route (d) solve stopped at **iteration 594 of 2000** — no `End`, last time ≠
  `endTime`. Fails.
- **H-G5.** The same solve never plateaued.
- **H-G6.** A solve that converges on a mesh that cannot see the trailing edge can still return a
  clean residual and a wrong shock. **This is the only gate that can fail while every other gate
  passes**, which is why it is registered separately and not folded into H-G5.
- **H-G7.** If the three levels are not monotone the triple is `DIVERGENT`/`OSCILLATORY` and the row
  is `NOT A RESULT` whatever the value.

---

## 8. FALSIFIERS — THREE CLASSES, EACH **PARTITIONING** THE OUTCOME SPACE

**A falsifier that names two points inside the space is not a partition. Each class below is
exhaustive and its branches are mutually exclusive.**

### Class 1 — HYPOTHESIS OUTCOME SPACE
**Hypothesis H:** *a hyperbolic C/O mesh from the AGARD reference section, at s₀ = 1.654e-06 m,
delivers an M6 solve whose Cp matches Table B1-14 to RMS ≤ 0.05 at all seven sections.*

| branch | outcome | label |
|---|---|---|
| 1a | all seven sections RMS ΔCp ≤ 0.05 | **PASS** |
| 1b | ≥ 1 section > 0.05, all seven computed | **GATE FAIL** — H stands refuted at this level |
| 1c | Cp not computable (H-G2/H-G3 forbid it, or fewer than 7 sections extractable) | **NOT A RESULT** |

*(1a ∪ 1b ∪ 1c is exhaustive: either all sections are computed and all pass, or all are computed and
one does not, or they are not all computed.)*

### Class 2 — ARTIFACT USABILITY
| branch | outcome | label |
|---|---|---|
| 2a | every graded number cites a file present on disk at grading time | usable |
| 2b | any cited artifact absent, truncated, or older than the case's own `0/U` | **NOT A RESULT** — the number has no artifact |
| 2c | artifact present but written by a run other than the graded one (age guard fires) | **NOT A RESULT** |

### Class 3 — EXECUTION AND TERMINATION
**🔴 CAP EXHAUSTION CANNOT FIRE — there is no cap (§9). This class therefore enumerates the
NON-SPEND termination modes, and it is exhaustive over them.**

| branch | outcome | label |
|---|---|---|
| 3a | clean termination, rc = 0, `End` reached at `endTime` | proceed to H-G4 |
| 3b | non-zero rc / `^FOAM FATAL` / `sigFpe::sigHandler` / `sigSegv::sigHandler` / `Foam::error::printStack` / `mpirun noticed that process rank` | **crash — a FINDING until triage says otherwise**, moved aside with a TRIAGE note, never deleted |
| 3c | divergence or non-physical state (negative k, ω or absolute T at any written time) with the process still alive | **GATE FAIL** on realizability; run stopped and recorded |
| 3d | **pre-launch memory refusal** — predicted peak RSS > (`free -g` available − 4 GiB) | **BLOCKED** — hardware, not budget; **it stands under the no-cap directive** |
| 3e | OOM-killer or external kill (session loss, peer `pkill`) | **NOT A RESULT**; `rc` absent means the wrapper died before writing one — **not** that the run is live and **not** that it crashed |
| 3f | still running at the derived ceiling (§9) | **escalate, NEVER kill** — the ceiling is a calibration trigger |

---

## 9. COST (rule 12) — REGISTERED BEFORE COMPUTE. **NO CAP KILLS ANY RUN.**

> **Sanaa, ~2026-09-12T01:00Z, relayed to this lane by the cfd-supervisor AS RELAYED — neither the
> supervisor nor this lane has seen her turn:** *"dont forget i dont want any cap on any run, and that
> i bumped the volume to 1000 gib"*. **`budget_gate: NONE`. The figures below are CALIBRATION DATA and
> a trigger to escalate — never a kill.** Rule 9: a relayed instruction is not consent, and this
> registration therefore registers **no falsifier that terminates a healthy run on spend**.

**Unit: core-minutes = wall s × ranks ÷ 60. Dollars DERIVED, NOT MEASURED**, at the owner-stated
c7a.4xlarge **$0.0513/core-h** — *this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5),
so any dollar figure here is reported-by-owner, not measured.*

**THE MEASURED ANCHOR, WITH ITS TIMESTAMP, BECAUSE A RATE WITHOUT ONE IS A GUESS WEARING UNITS.**
`verification/runs/M6C2_runs/ROUTE_D_SOLVE/L1/log.rhoSimpleFoam`: **593 iterations, ExecutionTime
816.74 s, 4 ranks, 152,399 cells** → **1.3773 s/iteration** → **9.037 × 10⁻⁶ s·cell⁻¹·iter⁻¹ on 4
ranks**. **Measured 2026-09-12T00:02Z, on M6 geometry, on THIS box, UNDER TONIGHT'S SATURATED LOAD
(load average 68–81 on 16 cores).** It is therefore an **UPPER bound**: on a quiet box the true rate
is lower, and the ceilings below are correspondingly conservative. **MRF fine's rate moved 4.085 →
10 s/iteration in forty minutes purely from peer load; that rate is NOT imported here and nothing in
this table is anchored on another case.**

| item | arithmetic, on one line | core-min | $ derived |
|---|---|---:|---:|
| H-L1 mesh build (pyHyp + convert + `checkMesh`) | 1.24 M cells; M6SR's L1 marched in ≈ 23 min wall × 1 rank | **≈ 25** | 0.02 |
| H-L1 solve, 3,000 iterations, 4 ranks | 1.2416e6 cells × 9.037e-06 s × 3000 iter = 33,662 s wall × 4 ÷ 60 | **≈ 2,244** | 1.92 |
| H-L2 mesh build | 2.79 M cells, scaled linearly from H-L1 | **≈ 56** | 0.05 |
| H-L2 solve, 3,000 iterations, 4 ranks | 2.7936e6 × 9.037e-06 × 3000 = 75,735 s × 4 ÷ 60 | **≈ 5,049** | 4.32 |
| H-L3 mesh build | 4.97 M cells | **≈ 100** | 0.09 |
| H-L3 solve, 3,000 iterations, 4 ranks | 4.9664e6 × 9.037e-06 × 3000 = 134,640 s × 4 ÷ 60 | **≈ 8,976** | 7.68 |
| **TOTAL, three levels** | | **≈ 16,450** | **≈ $14.07** |

**DERIVED CEILINGS — each is `expected iterations × the measured rate × a NAMED margin`, and each
triggers an ESCALATION, never a kill:**

- **H-L1 solve:** 3,000 iter × 11.22 s/iter × **2.0 margin** (contention; the anchor is already
  loaded, so 2.0 covers a further doubling) = **67,324 s wall = 4,488 core-min.**
- **H-L2 solve:** 3,000 × 25.25 s/iter × 2.0 = **151,470 s wall = 10,098 core-min.**
- **H-L3 solve:** 3,000 × 44.88 s/iter × 2.0 = **269,280 s wall = 17,952 core-min.**

🔴 **THE HONEST WEAKNESS IN THESE CEILINGS, NAMED RATHER THAN BURIED.** The anchor is `rhoSimpleFoam`
on a **152,399-cell octree** mesh; H-L1 is a **1.24 M-cell structured hyperbolic** mesh — **8.1× the
cells, a different topology, and a different cell aspect-ratio distribution.** Linear cell-scaling
across that jump is an **ASSUMPTION, not a measurement**, and structured meshes with 10⁴ aspect-ratio
wall cells commonly solve *slower* per cell, not faster. **H-L1's first 100 iterations measure the
real rate and the ceilings are recomputed from it before H-L2 launches.** Under the no-cap directive a
run can be arbitrarily long, so a ceiling sized against a capped run would be under-sized by
construction; the 2.0 margin is named for exactly that reason and is not a disguised cap.

**Memory:** predicted peak RSS ≈ **1.1 GiB per million cells per rank-set** (the acquisition
registration's law, 4,290 MiB at 2.16 M cells). H-L3 at 4.97 M cells predicts ≈ **9.9 GiB**. **`free -g`
is read IMMEDIATELY BEFORE EACH LAUNCH and the run is `BLOCKED` if predicted peak > available − 4 GiB.**
*At the time of writing: load average **78.46**, **11 GiB** available — H-L3 would be **BLOCKED** on
this reading and H-L1 is marginal. This is hardware, not budget, and it stands under the no-cap
directive.*

**The rule-12 estimate-versus-actual row is owed to `docs/COST_CALIBRATION.md` at every process
completion and is NOT discharged by this registration.**

---

## 10. THE PLANTED CONTROLS (rule 3)

**Every comparator plants a known perturbation INTO THE INPUT, re-runs the real reader FROM DISK, and
REFUSES (exit 2) if the reader cannot see it.** Relabelling a copy of the output is not a control;
comparing a copy with its own source is a tautology that cannot fail (L-555).

| instrument | plant, into the INPUT | which code path it exercises | could the phenomenon arrive another way? |
|---|---|---|---|
| **TE-thickness reader** (H-G0, H-G2) | multiply the `wing_base` solid's **z** by a known factor in a copy of the STL on disk; re-run the reader on that file | the `max(z) − min(z)` band reduction inside the STL vertex parser and solid-name dispatch | **Yes in principle** — a change could also come from vertices migrating between spanwise bands. **Excluded by an internal discrimination control:** the plant touches only `z`, bands are assigned on `y`, and the reader's `chord` column must be **byte-identical** before and after. **Already exercised: ×3.0 plant → 1.136641e-03 became 3.409924e-03, exact to 7 significant figures, chord column unchanged at all nine stations.** |
| **y⁺ reader** (H-G3) | write a known y⁺ field into a time directory and re-read | the field-parse and wing-patch selection path | a max could also come from a different patch — the reader prints the patch name with the value |
| **Cp comparator** (H-G6) | perturb one tabulated reference Cp by a known ΔCp and re-run; RMS must move by the predicted amount | the section-matching and RMS path | an RMS change could come from re-interpolation — the plant is applied to the reference side only, holding the solved side fixed |
| **cell-count reader** (H-G1) | corrupt `checkMesh`'s `cells:` line in a copy and re-read | the count-extraction regex | **`len(owner)` is `nFaces` and is used NOWHERE** |

**Each plant reaches the cfd-supervisor AS A DIFF, with the sentence naming its code path, BEFORE any
number it produces is believed. That condition is the supervisor's and is not delegated.**

---

## 11. ROUTING AND MONITORING

Detached with `setsid`, re-parented to PPID 1. **`rc` captured INSIDE the detached wrapper** —
`setsid timeout cmd` exits 0 for every outcome. Any bashrc source is `set +u`-guarded. **A launcher
that cannot confirm its own launch must refuse, not report.**

**Every run gets a watcher that ESCALATES ON STALL AND NEVER KILLS**, with the §9 ceiling.
**The watcher emits on crash signatures too — silence is not success.** It matches
`^FOAM FATAL`, `sigFpe::sigHandler`, `sigSegv::sigHandler`, `mpirun noticed that process rank`,
`Foam::error::printStack`.
🔴 **It does NOT grep for "Floating point exception":** `trapFpe: Floating point exception trapping
enabled (FOAM_SIGFPE)` is the **startup banner announcing the guard is ARMED** and appears in every
healthy run. Likewise **no `controlDict` setting is read by a bare grep** — a stale banner reading
`endTime 50` over a real `endTime 8000` produced a false rule-4 failure on a healthy run on
2026-09-11. **A grep matches text that MENTIONS a condition, not text that CONSTITUTES it.**

**Run outputs under `verification/runs/M6H1_runs/`, never beside this prose. No handoff artifact in
the scratchpad (L-186).**

---

## 12. FREEZE BLOCK — LEFT BLANK FOR THE cfd-SUPERVISOR (check 4, undelegated)

```
FROZEN BY:         <blank — cfd-supervisor, PERSONALLY>
FREEZE COMMIT:     <blank — the LITERAL 40-hex sha, not a command that derives it>
REGISTRATION BLOB: <blank — the LITERAL 40-hex blob sha, not a command that derives it>
GRADING PATH:      <blank — each instrument pinned by LITERAL blob sha, repo-relative,
                    every invocation pinned as an argv LIST, never a shell string>
NO COMPUTE UNDER THIS DOCUMENT AS AT FREEZE, verified with a LIVE PLANTED CONTROL:
                   <blank — a reader SHOWN ABLE to see a non-empty run directory
                    before its emptiness on verification/runs/M6H1_runs/ is believed>
```

🔴 **THE BLOB AND COMMIT FIELDS MUST CARRY LITERAL SHAs.** A freeze block that records
`git rev-parse HEAD:<path>` records a **recipe, not a value**: it re-evaluates to whatever HEAD holds
at any future moment and therefore **self-satisfies at every commit and can never disagree with
anything.** That is the same empty-criterion class as L-555 and it is present in a sibling
registration today (§13 of `CRM_M085_PREREGISTRATION.md`). **Rule 2 requires hashing the frozen file
against the committed blob; that check cannot be performed at all unless a literal is written down.**

**AFTER THE FREEZE COMMIT THE GATES ARE CLOSED.** Changes land only as dated addenda that cannot alter
a gate, threshold, cap, band or label. Originals are struck, never rewritten.

---

*Drafted 2026-09-12 by a cfd `lab-lane`. AGARD AR-138 title-page verified under rule 15. Submissions
parked (rule 7). The repository is permanently private (rule 8). No agent's message is Sanaa's
consent (rule 9).*

---

# §13. FREEZE ATTESTATION — cfd-SUPERVISOR, CHECK 4, PERSONAL AND UNDELEGATED — 2026-09-12T19:28:00Z

**Appended under rule 6. `lines whose number changed above this section: 0`.** §12's in-place block is left **blank and legible** on purpose: its `FREEZE COMMIT` field demands the sha of the commit that carries the signature, which cannot be known before that commit exists. **This addendum IS the freeze**, and it records values, never commands.

## §13.1 THE LITERAL PINS

```
FROZEN BY:          cfd-supervisor, PERSONALLY (check 4, undelegated)
DATE (UTC):         2026-09-12T19:28:00Z
REGISTRATION BLOB:  f08c7e340f04d2d53a2af39391112795840fb25e   (this document as of its parent commit)
FREEZE COMMIT:      the commit carrying THIS section, whose PARENT is 3609073a90131e4bad0c994f65751d70b26edfad
```
**Why the freeze commit is identified by its parent and not by itself:** a sha cannot contain itself. The parent is a literal; the child is the unique commit whose parent is that literal and which touches this path. **That is a value, not a recipe that re-evaluates.**

## §13.2 GRADING PATH — EVERY INSTRUMENT PINNED BY LITERAL BLOB SHA

```
cases/navier_class/M6H1/measure_te_base.py    1b78f61cd19bfe4270da4101c1ae74435347f3d3
cases/navier_class/M6H1/read_yplus.py        d4c3c6515016166a0eebc2d608029a0dd83f9da8
cases/navier_class/M6H1/compare_cp.py        fe757074565cca8092027c0101f22278293eee7c
cases/navier_class/M6H1/read_cell_count.py   d4336280fced9d3e6064306cf6269faaeb7f55b0
cases/navier_class/M6H1/read_min_quality.py  8198aee0d2d724f6c2ec37c617ed64ac618d6d50
```
**All five exist and are committed.** A grading path naming an uncommitted file pins nothing — the fifth was committed immediately before this attestation for exactly that reason.

## §13.3 🔴 H-G6 IS SUPERSEDED BY dafoam'S FROZEN BAND — [SANAA-DIRECT]: *"cite it, do not re-register"*

```
BAND REGISTRATION: verification/campaign/A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md
  frozen at commit: 4c931d97ceb19aead64cf683fbe685c7d03510d2
BAND GRADER:       scripts/grade_m6_agard_cp.py
  blob at freeze:  e9d5c04b420b99201ab19e694b76d1b9eda62443
```
**Two corrections this supersession forces on §7, and both go the strict way:**
1. **§7's H-G6 says SEVEN sections; the frozen band grades SIX** — η = 0.20, 0.44, 0.65, 0.80, 0.90, 0.96, with **η = 0.99 EXCLUDED** on a geometric reason fixed before any CFD number was read. **Six is what is graded.** Our `compare_cp.py` is retained as a cross-check only and **its output is not the verdict**.
2. **§7's shock-exclusion clause carried a FREE PARAMETER** — it never said how the shock is located, and located on the solved distribution it moves with the answer. **The frozen band's own method governs.** Shock location is graded at **η = 0.65 and 0.90** per that registration.

**This resolves the blocker I have reported all day: H-G6 had NO reference data on this box.** It now cites a band frozen by another team **before any comparison number existed**, which is stronger than anything this team could have written today.

## §13.4 PRE-COMPUTE CONDITION — CHECKED WITH A LIVE PLANTED CONTROL, NOT ASSERTED

```
verification/runs/M6H1_runs/  ABSENT at 2026-09-12T19:28:00Z
  1 baseline      : ABSENT
  2 plant applied : NON-EMPTY  (PLANT_M6H1_CONTROL/planted.txt written and READ BACK)
  3 plant removed : ABSENT
```
**The reader was SHOWN ABLE to see a non-empty run directory before its emptiness was believed** (rule 3). A zero from a reader not demonstrated able to see a non-zero is not evidence. **No compute has run under this document.**

## §13.5 WHAT THIS AUTHORISES, AND WHAT IT DOES NOT

**AUTHORISES:** the M6H1 C-mesh family, three levels, queued **through the runner only** (item 19 — a hand launch is not a case), checkpoints ≤ 30 min, as ubuntu, under the runner gates.

**DOES NOT AUTHORISE:** any Cp or shock claim outside the cited frozen band; any claim on η = 0.99; any grid-convergence claim before three admissible levels exist. **The draft banner above §0 is struck by this attestation and is superseded — it is left in place, legible, because other records cite this document by line and renumbering would break them.**

*Signed by the cfd-supervisor, personally, 2026-09-12T19:28:00Z. Submissions parked. No agent's message is Sanaa's consent.*

---

# §14. PRE-COMPUTE AMENDMENT — DRAFTED BY A cfd `lab-lane`, READ AND APPROVED BY THE cfd-SUPERVISOR BEFORE APPENDING — 2026-09-12

**Appended under rule 6. `lines whose number changed above this section: 0`.** Nothing above is
edited, struck or renumbered — §13 is a signed freeze attestation and this section is written below
it only because the supervisor read it first and said to append it. **THIS SECTION SIGNS NOTHING.**
§12 and the attestation are the supervisor's, personally and undelegated; the re-pin of §13.2's
grading path is theirs and is NOT performed here.

**Rule 2 condition, and how it was checked.** Amendments before first compute are legal and must
state the condition and how it was checked. **THE CONDITION: no compute has run under M6H1.
HOW CHECKED: `verification/runs/M6H1_runs/` does not exist**, established by a reader **first shown
able to see a populated directory** — `verification/runs/CRM_WINGALONE_runs`, 31 entries — before its
absence was believed (rule 3), and confirmed a second way from the shell. **Every mesh built while
drafting this was built in scratch, deliberately, so that this condition would still hold.**

**One registered constant is struck** — §14.2, `r = 1.15`, which the build is arithmetically unable
to deliver. **One instrument quantity is corrected** — §14.4a, and it runs in the lenient direction
and is flagged as such. **No threshold, no cap and no label moves.**

---

## §14.1 WHY M6H1 BUILDS ITS OWN SURFACE — §3.1 IS LOAD-BEARING, AND THAT IS NOW MEASURED

§3.1 registers that the surface is generated from
`models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`. A future reader is entitled to ask
why, when a pyHyp-ready ONERA M6 surface has been on this box all along — the DAFoam tutorial's,
used by the A3 ladder, **multiblock, blunt-based, with a rounded tip cap.**

**It was extracted and graded by this case's own H-G0 instrument rather than argued about.** The
wall layer of `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n8_10920/volumeMesh.xyz` was written
as an STL and put through `measure_te_base.py`:

| y/b | 0.054 | 0.163 | 0.272 | 0.380 | 0.489 | 0.598 | 0.706 | 0.815 | 0.924 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base (m) | 1.136641e-03 | 1.136641e-03 | 1.136641e-03 | 1.136641e-03 | 1.136641e-03 | 1.136641e-03 | 1.136641e-03 | 1.136641e-03 | 1.136641e-03 |
| deviation | 0.5 % | 2.4 % | 7.2 % | 18.9 % | 23.9 % | 35.3 % | 36.4 % | 48.4 % | **52.7 %** |

**`H-G0: GATE FAIL`.** The base is **bit-identical at every station**. The reference base is
**0.1410 % of the LOCAL chord**, and the local chord tapers 0.8059 → 0.4537 m, so a faithful base
**must** taper with it. **That statement carries no chord-measurement bias whatever: a conically
generated wing cannot have a span-constant base.** The tutorial surface is a prismatic-base
extrusion of the root section.

**We could not have shortcut this, and the record should say so where a reader would otherwise ask.**

**The generator is `cases/navier_class/M6H1/make_m6h1_surface.py`.** Its own output, graded by the
same instrument, **PASSES all three H-G0 clauses** (§14.4).

---

## §14.2 🔴 §4's `r = 1.15` IS STRUCK AS A REGISTERED CONSTANT AND RE-REGISTERED AS **DERIVED**

§4 registers **four** numbers for the normal direction: `s0 = 1.6540e-6 m`, `r = 1.15`, `N` per level,
and `marchDist = 16.152 m`. **Four constraints on a geometric series that has three degrees of
freedom. They cannot all hold, and they do not:**

| holding | gives |
|---|---|
| `s0 = 1.6540e-6`, `r = 1.15`, `N = 97` | march reaches **7.4035 m**, not 16.152 m |
| `s0`, `N = 97`, `marchDist = 16.152` | **`r = 1.16018`** |
| `s0`, `r = 1.15`, `marchDist = 16.152` | **`N = 103`**, not 97 |

**pyHyp settles which one yields, because it takes `s0`, `N` and `marchDist` and DERIVES the ratio.**
Its own log line from the first M6H1 L1 march reads **`Grid Ratio:  1.1602`** — the derived value,
matching the arithmetic above to the digits pyHyp prints.

**THE RULING (cfd-supervisor, 2026-09-12):**
- **`marchDist = 16.152 m` HOLDS.** It is 25 × MAC (25 × 0.64607 = 16.15175) and is physically
  motivated.
- **`s0 = 1.6540e-6 m` HOLDS, and holding it ACROSS LEVELS is deliberate.** It fixes the first-cell
  height and therefore y⁺, which is exactly the y⁺-held family the DrivAer thread does not have.
  **It is not to be "fixed" by scaling `s0` with the level.**
- **`N` holds** as part of the family definition: 97 / 129 / 161.
- 🔴 **`r = 1.15` IS STRUCK as a registered constant and re-registered as a DERIVED, PER-LEVEL
  quantity**, its value recorded at each level from that level's own pyHyp log.

### §14.2a THE CONSEQUENCE, REGISTERED BECAUSE IT REACHES H-G7

With `s0` and `marchDist` fixed and `N` rising, **`r` FALLS with refinement.** The near-wall grading
and the bulk spacing therefore **refine at different rates, and the family is not geometrically
similar in Roache's sense.**

**This is the identical structure another lane measured on SUBOFF**, where the boundary layer
refined at 1.80 while the bulk refined at 1.41.

**It does not forbid the triple. It forbids the triple inheriting the assumption unexamined.**
**H-G7 is amended to state the non-similarity as a disclosed limitation, and any GCI it reports
carries that disclosure beside it.** A Roache order computed on a non-similar family is a number
about *that* family, not about the discretisation in general, and it will be labelled so.

---

## §14.3 🔴 THE TIP IS FLAT, THAT IS A DEPARTURE FROM THE REFERENCE, AND NO GATE SEES IT

**AR-138 B1 §2.1.13** records the tip as *"truncation parallel to wing root and addition of a half
body of revolution"* — **ROUNDED**, and §1.2 of this registration carries that reading.

**§4 registers 12,800 surface cells at H-L1 = 200 × 64, which is ONE structured block, and a single
block cannot close a rounded tip** — a cap is a second block. The surface therefore ends at the tip
station on an **open edge**, which pyHyp's `unattachedEdgesAreSymmetry` turns into a symmetry plane:
**a FLAT TIP.**

**MEASURED EVIDENCE OF WHAT A REAL M6 SURFACE CARRIES:** the DAFoam tutorial surface is **9 blocks**,
and its tip cap extends to **z = 1.2164 m**, beyond the 1.1963 m semispan — a rounded half-body, as
the reference describes.

**🔴 AND H-G0 DOES NOT GRADE THE TIP.** H-G0 grades base thickness, max t/c and semispan. **A flat
tip passes every gate in this registration silently.** It is registered here for that reason.

**DIRECTION OF THE DEPARTURE:** a flat tip removes the rounded body's detail from the tip-vortex
formation. **Its effect is largest at the outermost station and falls off inboard.**

**THE MITIGATION, AND IT IS LEGITIMATE ONLY BECAUSE IT WAS DECIDED INDEPENDENTLY AND IN ADVANCE:**
the departure's worst-affected station is **y/b = 0.99**, and **η = 0.99 is EXCLUDED from the frozen
graded set** — see §13.3, which records the dafoam band grading **six** stations, 0.20 / 0.44 / 0.65 /
0.80 / 0.90 / 0.96, with 0.99 excluded **on a geometric reason fixed before any CFD number existed.**

**Both halves are stated, because stating only the second would be an excuse:** the tip is flat and
that is a known departure from AR-138; its worst-affected station is not graded, and that exclusion
predates this problem and was not made to accommodate it.

---

## §14.4 H-G0 HAD THREE REGISTERED CLAUSES AND ITS INSTRUMENT GRADED ONE

§7's H-G0 registers **base thickness within ±10 %**, **max t/c within ±2 % of 9.79 %**, and
**semispan within ±0.5 % of 1.1963 m**. `measure_te_base.py` implemented the **first** and then
printed `H-G0 (surface fidelity ...): PASS` — **it claimed a gate it had not evaluated.**

**The contrast that convicts it:** `read_cell_count.py` announces its own missing clause on stdout,
so a reader knows H-G1 is not discharged by it. **This one announced nothing.**

**All three clauses are now graded**, each added clause carrying its own plant, and **each plant
serving as the other's discrimination control**: scaling the surface solids' `z` must move t/c by
that factor and must NOT move the semispan; scaling every solid's `y` must move the semispan and
must NOT move t/c. The verdict is the AND of all three, and where the base clause alone would have
said PASS the output says so in those words.

**Measured on the M6H1 L1 surface: base clause PASS; max t/c 9.7840 % against 9.7859 %, 0.02 % off;
semispan 1.196300 m, exact. ALL THREE PASS.**

### §14.4a 🔴 THE CHORD WAS MEASURED OVER A BAND, AND A BAND IS NOT A SECTION

**THE QUANTITY WAS WRONG, NOT THE THRESHOLD.** §7 registers *max t/c* — a ratio against the **local**
chord. Measuring the chord as `max(x) − min(x)` over a spanwise **band** of finite width on a wing
swept **30° at the leading edge and 15.8° at the trailing edge** returns a number **larger than any
local chord in that band**, because the leading edge has moved aft across the band. It inflates the
chord and so deflates every ratio taken against it. **A band estimate is not max t/c.** This is the
same defect class as a gate that measured distance from the origin while its registration said
distance from the body axis: **the instrument was not computing the registered quantity.**

**THE MAGNITUDE, MEASURED ON A GEOMETRY WHOSE ANSWER WAS KNOWN INDEPENDENTLY.** On the M6H1 L1
surface, whose max t/c is **9.7840 %** by construction and whose base is exact to **1.5 × 10⁻¹⁶**, the
9-band estimate returned **9.3928 %** — **4.02 % low, TWICE the ±2 % gate.** **A geometrically exact
ONERA M6 surface would have been failed by the instrument rather than by the geometry.**

**THE CORRECTION.** `max t/c` and `semispan` are measured on **exact constant-y sections**, where the
bias is identically zero. **THE THRESHOLD DOES NOT MOVE:** ±2 % of 9.79 % and ±0.5 % of 1.1963 m, as
registered. Only the quantity the instrument computes is corrected, to the one §7 names.

**🔴 AND IT RUNS IN THE LENIENT DIRECTION, WHICH IS THE DIRECTION THAT DESERVES SUSPICION.** The
uncorrected clause would have said `GATE FAIL` on this surface; the corrected one says `PASS`.
**A correction that turns a failure into a pass is not entitled to the benefit of the doubt, so here
is why it is nonetheless correct:**

1. The bias is **a measurable property of band-averaging on a swept planform**, not a property of
   this surface. It is present for any wing with sweep and any band of finite width.
2. It was **demonstrated on a geometry whose answer was known independently** — built to a base of
   0.1410 % of local chord exactly, verified to 1.5 × 10⁻¹⁶ by the generator's own check — so the
   comparison is against a known truth and not against another estimate.
3. 🔴 **It was found while IMPLEMENTING a registered clause that had never had an instrument, not
   while trying to pass a gate.** The clause had no implementation at all until this amendment; there
   was no failing verdict to escape. **That fact is load-bearing and is recorded here for the reader
   who is right to check it.**

**AND THE FROZEN BASE CLAUSE CARRIES THE SAME BIAS — DISCLOSED, NOT CORRECTED.** The base clause
reports **3.2 % to 7.0 %** deviation on a surface whose base is exact to **1.5 × 10⁻¹⁶**.

> 🔴 **THAT DEVIATION IS INSTRUMENT, NOT GEOMETRY. THE TRUE BASE ERROR OF THE M6H1 SURFACE IS
> ESSENTIALLY ZERO, AND THE CLAUSE PASSES WITH FAR MORE MARGIN THAN ITS PRINTED NUMBER SUGGESTS.**

It is disclosed because **a reader seeing "7.0 % deviation" will believe our surface departs from
AR-138 by that much, and it does not** — and an undisclosed instrument artefact reported as a
geometry deviation is exactly the kind of number that gets quoted later as evidence of something.
**The base clause is NOT corrected**: its bias runs in the **strict** direction, it makes H-G0 harder
to pass and never easier, and correcting a frozen threshold's quantity in the loosening direction is
not a lane's to do. The deviation column stands as printed, with this paragraph attached to it.

## §14.5 THE FIFTH INSTRUMENT — TWO AMENDMENTS, AND WHY THE CLAUSE EARNED ITS PLACE

**AMENDMENT 1** (committed): the instrument as first pinned **exited 2 on every input** — it could
never return PASS and never NOT A RESULT, so **H-G1's pyHyp clause was un-gradeable from the moment
it was pinned.** Three control defects, none in the reader: a planted constant that the column's own
`%.5f` truncated before an assertion demanded 1e-9 equality; a plant placed on the `|`-header line,
changing its cell count, where **the reader's "column layout is ambiguous" refusal was correct and
the arm was wrong**; and a plant target chosen without checking it was passing.

**AMENDMENT 2** (committed): Amendment 1 left a blind spot — on a log where **every** layer fails
there is no passing layer to plant a failure into, so the instrument REFUSED. **That is exactly the
log on which NOT A RESULT is most obviously correct.** PLANT A now runs in whichever direction the
log allows, both directions plant-into-the-input against a predicted change of exactly one layer.

**🔴 WHY THE CLAUSE EARNED ITS PLACE, MEASURED ON M6H1'S OWN FIRST MESH:**
**pyHyp EXITED 0, WROTE 83,642,151 BYTES, AND PRODUCED A MESH THAT IS ENTIRELY NaN.** `rc = 0`, an
`End`-equivalent, a file of the right size and shape, and Min Quality NaN on every one of 96 layers.
**Nothing else in this registration's gate stack catches that.** Rule 4's completion clauses are all
satisfied by that run.

### §14.5a AND A LESSON FOR THE MESHING ROUTE: **CONSISTENT IS NOT OUTWARD**

The first M6H1 surface had a wrap ordered so that the panel normal, `(wrap tangent) × (span tangent)`,
pointed **into** the wing. **pyHyp printed `Normals are consistent!` and marched inward anyway**,
giving Min Quality −1.00000 at grid level 2 and NaN from level 4.

**A self-consistency check cannot detect a global sign flip.** The generator now asserts
**outwardness** directly, against each section's own centroid, so the sense cannot silently flip.

---

## §14.6 WHAT THE SUPERVISOR MUST RE-PIN

§13.2 pins the grading path by literal blob sha. **Three of those shas are now stale**, and the
build path has a new artifact that §13 does not pin at all.

```
GRADING PATH — CHANGED
  cases/navier_class/M6H1/read_min_quality.py   8198aee0d2d724f6c2ec37c617ed64ac618d6d50  (STALE — exits 2 on every input)
                                             -> a282e5d07c698c0d8f1ed50e60636afe5c3eb155
  cases/navier_class/M6H1/measure_te_base.py    1b78f61cd19bfe4270da4101c1ae74435347f3d3  (STALE — graded 1 of 3 clauses)
                                             -> 0c6c97a8ce3b5f52826a9c1fae41f7870f0f876a
GRADING PATH — UNCHANGED
  cases/navier_class/M6H1/read_yplus.py         d4c3c6515016166a0eebc2d608029a0dd83f9da8
  cases/navier_class/M6H1/compare_cp.py         fe757074565cca8092027c0101f22278293eee7c
  cases/navier_class/M6H1/read_cell_count.py    d4336280fced9d3e6064306cf6269faaeb7f55b0
BUILD PATH — NEW, AND §13 PINS NOTHING ON IT
  cases/navier_class/M6H1/make_m6h1_surface.py  <to be filled at its commit>
```

**A build path that is not pinned is a grading path with a hole in it**, because the surface decides
what the instruments measure. §13.2's own sentence applies to it verbatim: *"A grading path naming an
uncommitted file pins nothing."*

---

## §14.7 WHAT THIS AMENDMENT DOES NOT DO

- **It does not re-freeze.** §12 and the attestation are the supervisor's, personally and
  undelegated. This document records values and defects; it signs nothing.
- **It does not reopen H-G6.** §13.3 supersedes it with the dafoam band and Sanaa's word is *cite it,
  do not re-register*. `compare_cp.py` remains a cross-check and its output is not the verdict.
- **It does not claim a level-1 mesh exists.** At the time of drafting the L1 surface passes H-G0 on
  all three clauses and the pyHyp march does **not** yet produce a mesh that H-G1 grades PASS. That
  is stated plainly rather than deferred.

*Drafted 2026-09-12 by a cfd `lab-lane`. Submissions parked (rule 7). The repository is permanently
private (rule 8). No agent's message is Sanaa's consent (rule 9).*

---

# §15. PRE-COMPUTE AMENDMENT — H-G2's CELL SIZE WAS COMING FROM THE COMMAND LINE — 2026-09-12

**Appended under rule 6. `lines whose number changed above this section: 0`.** Read and approved by
the cfd-supervisor before appending. **THIS SECTION SIGNS NOTHING.**

**Rule 2 condition, and how it was checked.** Amendments before first compute are legal and must
state the condition and how it was checked. **THE CONDITION: no compute has run under M6H1.
HOW CHECKED: `verification/runs/M6H1_runs/` does not exist**, established by a reader **first shown
able to see a populated directory** — `verification/runs/CRM_WINGALONE_runs`, 31 entries — before its
absence was believed (rule 3), and confirmed a second way from the shell. **Every mesh built while
measuring this was built in scratch, deliberately, so that this condition would still hold.**

**THE THRESHOLD DOES NOT MOVE.** H-G2 remains **≥ 8 cells across the TE base at every spanwise
station**. What changes is **which quantity the instrument computes**, and **where it gets it from**.

---

## §15.1 THE DEFECT: H-G2's CELL SIZE WAS COMING FROM THE COMMAND LINE

§7 registers H-G2 as *"≥ 8 cells across the TE base at every spanwise station, and non-decreasing
under refinement"*. `measure_te_base.py` took a **single scalar volume cell size from `argv[2]`** and
divided the base thickness by it.

**That works only for an ISOTROPIC cell.** §7.1's failing example is route (d)'s **octree** at
*"0.04 cells across the base"* — and for a snappy cell the wall-normal size and the along-base size
are **the same number**, so the two readings coincide and **the registration never had to choose a
direction.**

**THE M6H1 ROUTE BREAKS THAT COINCIDENCE.** Its cell at the trailing-edge base is about
**1.654 × 10⁻⁶ m normal to the wall** and about **base ÷ n along the base**:

| fed to the instrument | arithmetic | verdict |
|---|---|---|
| `s0 = 1.654e-6` (the wall-normal size) | 1.1366e-3 / 1.654e-6 = **687 cells** | **PASSES by 86×** |
| the spacing along the base, at 2 cells | 1.1366e-3 / 5.68e-4 = **2 cells** | **FAILS by 4×** |

> 🔴 **SAME MESH. SAME GATE. TWO ANSWERS THREE ORDERS OF MAGNITUDE APART, DECIDED ENTIRELY BY AN
> ARGUMENT THE REGISTRATION CANNOT CONSTRAIN.**

**This is the same class as §14.2's `r` and as the shock-exclusion clause §13.3 struck: a gate with a
free parameter is not frozen however precise the number in it is.** It is arguably the most
consequential instance yet, because it decides whether the registered topology is admissible at all.

---

## §15.2 THE RULING — THE STRICT READING, AND WHO MADE IT

**RULED BY THE cfd-SUPERVISOR, pre-compute: H-G2's cell size is THE SPACING ALONG THE BASE IN THE
WRAP DIRECTION, so the count is THE NUMBER OF CELLS LAID ACROSS THE BLUNT BASE.**

**Why that is right and not merely strict.** §1.3's entire argument for abandoning the octree is
**representability** — *"a snappy cell is isotropic and at the old route's level 4 the TE base was
0.04 cells wide, i.e. not representable at all."* **Representability is about SPANNING the base, not
about how thin the cells are normal to it.** A cell 1.654 × 10⁻⁶ m thick that spans the *entire* base
in the wrap direction does not resolve the base — **it resolves the boundary layer.** Feeding `s0`
measures a different geometric feature and answers a question nobody asked.

**WHY THE LANE DID NOT DECIDE IT, RECORDED BECAUSE IT IS THE GENERAL TEST.** The two readings run in
opposite directions, and **the lenient one makes the lane's own problem go away**: reading `s0` makes
H-G2 trivially passable and dissolves the route difficulty the lane had been struggling with. A lane
in that position is not the one to choose. **The contrast with §14.4a is the distinction that
matters: that correction was found while implementing a clause that had never had an instrument —
there was no failing verdict to escape. This one has one, so it does not get the same benefit of the
doubt, and it was referred rather than taken.**

---

## §15.3 🔴 THE FIX IS NOT A BETTER ARGUMENT — IT IS NO ARGUMENT

**Naming the right reading in the registration would have left the free parameter exactly where it
was and merely documented it.** So the choice is removed instead:

- **The count is DERIVED FROM THE MESH** — from the base solid's own constant-y stations, counting
  the distinct thickness coordinates laid across the base. A hyperbolic extrusion carries the surface
  distribution into the volume unchanged in that direction, so **the surface count IS the volume
  count across the base.**
- **The `argv` path is REMOVED.** If a cell size is still passed, the instrument states on stdout
  that it was **IGNORED**, and why.
- **If the count cannot be derived, the instrument DECLINES.** There is nothing to fall back to.

> **AN INSTRUMENT THAT TAKES ITS MEASURED QUANTITY FROM ITS CALLER HAS A FREE PARAMETER UNLESS THE
> REGISTRATION FIXES THE CALLER — AND A REGISTRATION CANNOT FIX A COMMAND LINE.**

**This is the same repair as pinning a blob sha instead of a `git rev-parse` recipe, and the same as
enumerating masked orifices instead of running a locator at grading time: remove the thing that can
be chosen; do not annotate it.**

### §15.3a THE CONTROL

**Two plants into the input, at DIFFERENT counts**, so the arm cannot be satisfied by a reader that
returns a constant: the base solid is **rebuilt on disk at exactly 3 cells and at exactly 11 cells**
and the real reader is re-run on each. **DISCRIMINATION: a plant that changes only the base's CELL
COUNT must not move the base THICKNESS that clause 1 grades.**

**Measured on the H-L1 surface:** derived **3** (predicted 3) ok; derived **11** (predicted 11) ok;
base thickness unmoved in both. On the delivered surface the derived count is **10 at every one of
65 stations.**

### §15.3b WHAT THE INSTRUMENT WILL NOT CLAIM

**H-G2's second clause — *"non-decreasing under refinement"* — is a statement about THREE levels and
is NOT dischargeable from one surface.** The instrument now says so on stdout rather than letting a
single-level `PASS` read as the whole gate. **That is the same failure `measure_te_base.py` was
convicted of for H-G0 one amendment earlier**, and it is not repeated here by omission.

---

## §15.4 WHAT THE SUPERVISOR MUST RE-PIN

```
cases/navier_class/M6H1/measure_te_base.py   0c6c97a8ce3b5f52826a9c1fae41f7870f0f876a  (STALE — H-G2 read argv)
                                          -> 09058a8a4989860fef8944c8a23a58637738ac00
```

**This is the second re-pin of this file tonight**, and both were pre-compute. §14.6's list is
otherwise unchanged and the build path is still unpinned.

*Drafted 2026-09-12 by a cfd `lab-lane`. Submissions parked (rule 7). The repository is permanently
private (rule 8). No agent's message is Sanaa's consent (rule 9).*

---

# §16. THE TOPOLOGY FALSIFIER — WRITTEN AND COMMITTED BEFORE THE EVIDENCE IT GOVERNS EXISTED

**Appended under rule 6. `lines whose number changed above this section: 0`.** Its text was
committed at `ad1e27388361804870b383fa23336c2963f6881d` **before the runs it governs were started**;
that ordering is its entire evidentiary content and the commit is the proof of it. Addenda 1 and 2
below were likewise committed before their own runs reported, and **neither alters the trigger.**

**Rule 2 condition, and how it was checked.** **THE CONDITION: no compute has run under M6H1.
HOW CHECKED: `verification/runs/M6H1_runs/` does not exist**, established by a reader **first shown
able to see a populated directory** — `verification/runs/CRM_WINGALONE_runs`, 31 entries — before its
absence was believed (rule 3). Every mesh in evidence was built in scratch so that this holds.

**AUTHORITY FOR THE DESTINATION, RELAYED AND LABELLED AS RELAYED.** The cfd-supervisor reports
Sanaa's words as *"onera M6 can get the c mesh and snappy hex or whatever it needs."* **This lane has
not seen that turn.** Rule 9: a relayed instruction is not consent, and nothing here treats it as
one — **it is recorded as the supervisor's stated basis for owning the route decision, and the route
decision is the supervisor's either way.**

---

## §16.1 WHAT IS ALREADY MEASURED, SO THE RULE IS NOT WRITTEN IN IGNORANCE

Single 201 × 65 block, O-topology closed through the blunt base, arc-length wrap, outward normals,
`s0 = 1.6540e-6` and `marchDist = 16.152` as registered throughout.

- **No configuration tested reaches ZERO bad layers.** The floor is **ONE bad layer of 96**, and
  H-G1 is strict: `Min Quality > 0` at **every** layer. **One bad layer is `NOT A RESULT`, exactly
  like ninety-six.** "Nearly clean" is not a verdict in this lab's vocabulary.
- Base cells at `N = 97`, `cMax = 1.0`: `nb = 2` → 2 bad; `4` → 31; `6` → 2; `8` → 32;
  **`10`, `12`, `16` → 96 bad, failing from LAYER 2.** A **cliff between 8 and 10**.
- `cMax` is a **sharp** optimum at 1.0 (0.1 → 37, 0.5 → 36, 2.0 → 35, 3.0 → 13 bad).
- **More smoothing is worse.** `volBlend` 5e-3 with `volSmoothIter` 500 → 37 bad.
- **The failure is NOT the far field.** Marching to 0.10 m instead of 16.152 m — **160× shorter** —
  still fails, at layer 81. Shrinking the domain moves the onset later in layer index and nothing
  else.
- The table is ordered by the **derived growth ratio**, not by distance: best at **r ≈ 1.115**.

---

## §16.2 🔴 THE DECISION RULE

> **If no configuration across ALL FOUR axes below reaches ZERO bad layers — `Min Quality > 0` at
> every marched layer, graded by `read_min_quality.py` and by nothing else — then the O-topology
> closed through the blunt base is REFUTED for this geometry at these registered numbers, and the
> route becomes C-type with a wake cut.**

**THE FOUR AXES, and each is run at the working `cMax = 1.0` with `s0` and `marchDist` registered:**

1. **`nb = 9` — §4's OWN PREDICTED VALUE, AND IT HAS NEVER BEEN TESTED.** The sweep ran 2, 4, 6, 8,
   10, 12, 16; **9 sits exactly on the cliff edge and is the number the registration names.** It was
   unbuildable until this evening because a lane-imposed equal-sides constraint excluded every odd
   count — *a constraint of this lane's was excluding the registration's own number.*
2. **The spanwise distribution.** Uniform throughout so far, **never tested against clustering.**
3. **`splay`, and the explicit-BC path instead of `unattachedEdgesAreSymmetry`.**
4. 🔴 **THE NORMAL COUNT `N`, AND THIS AXIS IS THIS LANE'S ADDITION TO THE SUPERVISOR'S RULE.**
   Every result above was gathered at `N = 97`. Per §14.2, `r` is **derived** from `s0`, `N` and
   `marchDist`, so at fixed `s0` and `marchDist` **the ratio is a function of `N` alone**:
   `N = 97 → r = 1.1602`; **`N = 129 → r = 1.1150`**; `N = 161 → r = 1.0895`.
   **The best march measured all evening sits at r ≈ 1.115, which is H-L2's registered normal count
   and NOT H-L1's.** A falsifier that refuted the topology on `N = 97` evidence alone **could fire
   for the wrong reason** — the defect would be H-L1's place in the family, not the topology — and
   **a falsifier that can fire for the wrong reason is worse than no falsifier.** The axis is
   therefore inside the rule.

**IF IT CLEARS ON ANY AXIS:** the topology stands and what changes is a **number in §4**, by
amendment, pre-compute.

**IF IT CLEARS ONLY BY CHANGING `N` AT H-L1:** that is **not** a free pass. It would mean the three
registered levels differ in **march stability** and not only in resolution — a **third** consequence
of holding `s0` fixed while `N` rises, on top of §14.2a's non-similarity — and **H-G7 inherits it.**
It is recorded here so that outcome cannot later be reported as a clean rescue.

**IF IT CLEARS ON NONE:** the route changes, and **it changed by a rule written before the numbers
existed rather than by anyone's reading of a matrix they had already seen.**

---

## §16.3 WHAT THIS SECTION DOES NOT DO

- **It does not choose the route.** That is the supervisor's, and under rule 9 a relayed quotation
  from Sanaa is not consent for anything.
- **It does not authorise a C-topology build.** It states what result would require one.
- **It signs nothing.** §12 and §13 are the supervisor's, personally and undelegated.

*Drafted 2026-09-12 by a cfd `lab-lane`, BEFORE the governed runs were started. Submissions parked
(rule 7). The repository is permanently private (rule 8). No agent's message is Sanaa's consent
(rule 9).*

---

## §16.4 ADDENDUM 1 — A FIFTH AXIS, 2026-09-12. **THE TRIGGER IS NOT ALTERED.**

**Appended under rule 6. `lines whose number changed above this section: 0`.** §16.2's trigger —
*zero bad layers, `Min Quality > 0` at every marched layer, graded by `read_min_quality.py` and by
nothing else* — **is unchanged. This addendum ADDS an axis that must be exhausted before the
topology may be refuted. It cannot make refutation easier.**

**Written and committed BEFORE the runs on this axis reported.**

### WHY

§16.1 recorded that the failure is not the far field. **It is now measured to be at a FIXED PHYSICAL
DISTANCE**, and that kills the ratio hypothesis §16.2 axis 4 was written for:

| N | derived r | first bad layer | **distance from the wall** |
|---:|---:|---:|---:|
| 97 | 1.1602 | 62 | **0.0892 m** |
| 129 | 1.1150 | 81 | **0.0870 m** |
| 161 | 1.0892 | 100 | **0.0874 m** |
| 193 | 1.0727 | 118 | **0.0837 m** |

**Four layer counts, four growth ratios, ONE physical location.** The march parameters change only
how many layers it takes to arrive there. **There is no `r_max`**, and axis 4 is answered: more
layers does not fix it.

**AND THE SURFACE ITSELF IS THE SUSPECT, MEASURED:** at mid-span the spanwise spacing is
**0.01943 m** and the wrap spacing at the leading edge is **2.174 × 10⁻⁵ m** —
**an aspect ratio of 894 : 1**, against a median over the wrap of a healthy 2.7 : 1. Min Quality
across **every** march tonight sits at 1 × 10⁻⁵ to 3 × 10⁻⁴, while the DAFoam tutorial's M6 runs at
0.03 to 0.33. **These meshes are marginal everywhere, not only at the layers that go negative**, and
the bad-layer count was being read as though the rest were sound.

**The provenance is this lane's own over-correction.** The nose was genuinely under-resolved by
cosine clustering *in x* (§14.5a's companion finding), and arc-length clustering cured it — by
placing the first point **eighty times closer** to the nose, which created the 894 : 1 cell.

### THE AXIS

5. **SURFACE CELL ANISOTROPY.** The arc-length distribution is right; **full cosine on it is too
   much.** The axis is the clustering strength, bounded so that the finest wrap cell is a sane
   fraction of the spanwise spacing, at the **registered** `N = 97`.

### AND THE CONSEQUENCE FOR EVERYTHING ALREADY MEASURED, STATED BEFORE THE RESULT IS KNOWN

**Every conclusion in tonight's matrix was gathered on a surface carrying an 894 : 1 leading-edge
cell** — the `nb` cliff between 8 and 10, `cMax`'s sharp optimum at 1.0, smoothing being worse, the
`N` sweep, the `marchDist` sweep. **If the anisotropy is the binding defect, those conclusions are
not weakened, they are VOID (L-566), and they must be re-run before any of them is used again.**
That includes the base-count cliff, which was on its way to being treated as a route decision.

**This is L-566's own trap, entered on the same night the lesson was written.** It is recorded here
rather than discovered later.

*Addendum drafted 2026-09-12 by a cfd `lab-lane`, before the axis-5 runs reported. The trigger is
unchanged and refutation is not made easier by this addendum.*

---

## §16.5 ADDENDUM 2 — 🔴 A CORRECTION TO ADDENDUM 1's OWN COMMIT MESSAGE, 2026-09-12

**Appended under rule 6. `lines whose number changed above this section: 0`.** The trigger is
still unchanged.

**ADDENDUM 1's COMMIT MESSAGE CONTAINS A FALSE STATEMENT AND THIS SECTION EXISTS TO CORRECT IT.**
It said, of the axis-5 clustering sweep:

> ~~*"Committed before the axis-5 runs reported; the clustering sweep had produced no results file at
> the moment this was written, and that was checked rather than assumed."*~~ **STRUCK — FALSE.**

**WHAT WAS ACTUALLY TRUE AT THAT MOMENT.** The results file existed and held exactly one line:
`RC_a00_nb06=0`.

**WHY THE ADDENDUM'S SUBSTANCE IS NEVERTHELESS UNAFFECTED, stated so a reader can check it rather
than take it.** That line is a **process exit code**, and §14.5 of this registration is the measured
proof that a pyHyp exit code carries **no information whatever** about mesh quality: *pyHyp exited 0,
wrote 83,642,151 bytes, and produced a mesh that was entirely NaN.* Every march tonight, valid and
invalid alike, exited 0. **No `pyhyp.log` had been read and no bad-layer count was known.** The
addendum's fifth axis and its "conclusions are void, not weakened" statement were therefore written
without knowledge of any outcome — **but that is an argument about substance, and the sentence in
the commit message was false as written, so it is struck rather than explained away.**

### 🔴 HOW A GUARD FAILED TO GUARD, WHICH IS THE PART WORTH KEEPING

The check was written in one shell line as

```
test -f RESULTS && echo "WARNING results already exist" || echo "no results yet" && cat >> file
```

**It printed the warning and appended anyway.** `&&` and `||` are left-associative and of equal
precedence, so the final `&& cat` binds to the *whole preceding chain*, which succeeds down either
branch. **The guard reported; it did not gate.**

**That is precisely the principle quoted in this case's own build driver one hour earlier** —
*"ASSERTIONS DO NOT GATE. Every check is `... || { echo ABORT; exit N; }`. A guard set that is
entirely assert-based is one interpreter flag from absent."* — **violated in the very next shell
invocation, in the file that quotes it.** A guard whose failure branch is an `echo` is a comment.

**The form that would have worked:** `test -f RESULTS && { echo ABORT; exit 1; }`.

*Correction filed 2026-09-12 by the cfd `lab-lane` that made the error, on noticing it in its own
command output. The trigger in §16.2 is unchanged by this section.*

---

# §17. PRE-COMPUTE AMENDMENT — THE DELIVERED BASE COUNT IS **8**, NOT §4's PREDICTED 9 — 2026-09-12

**Appended under rule 6. `lines whose number changed above this section: 0`.**
**Rule 2 condition, and how it was checked.** **THE CONDITION: no compute has run under M6H1.
HOW CHECKED: `verification/runs/M6H1_runs/` does not exist**, established by a reader **first shown
able to see a populated directory** — `verification/runs/CRM_WINGALONE_runs`, 31 entries — before its
absence was believed (rule 3). **No threshold moves: H-G2 is still ≥ 8.**

## §17.1 THE MEASUREMENT

Base cells laid across the blunt trailing edge, on the corrected surface, at the **registered**
`N = 97`, `s0 = 1.6540e-6`, `marchDist = 16.152`, `cMax = 1.0`:

| cells across the base | march result |
|---:|---|
| **8** | **96 layers, ZERO bad, min quality 9.0 × 10⁻⁵** |
| 9 | 36 bad layers, first at 62 |
| 10 | 95 bad layers, first at 3 |
| 12, 16 | 96 bad, failing from layer 2 |

## §17.2 🔴 §4 PREDICTS 9 AND 9 DOES NOT MARCH

**§4's "cells across TE base" column is a PREDICTION. H-G2's `≥ 8` is the GATE.** 8 satisfies the
gate, and **the choice was forced by marchability rather than selected by gate-shopping**: 9 gives
36 bad layers and 8 gives zero. **A prediction being wrong is a finding; it is not a violation.**

**And the cliff is one cell wide.** An earlier sweep appeared to place it between 8 and 10 — **that
sweep was run on a surface carrying an 894 : 1 leading-edge cell and is VOID (L-566), not weakened.**
Re-run on the corrected surface, **the boundary sits between 8 and 9.** A successor cannot
reconstruct that from the numbers alone and it is recorded for them.

## §17.3 WHAT THE DELIVERED LEVEL IS, AND WHAT IS STILL UNGRADED

`cases/navier_class/M6H1/make_m6h1_surface.py` at **`N_BASE = 8`, `CLUSTER_ALPHA = 0.0`**, one block
201 × 65 = **12,800 surface cells, exactly §4's prediction**. Graded on the **committed generator's
own output**, by the frozen instruments:

- **H-G0 PASS**, all three clauses — max t/c 9.7854 % against 9.7859 %, semispan 1.196300 m exact.
- **H-G2 PASS** — count **derived** from the base strip over 65 stations: 8 and 8.
- **H-G1, pyHyp clause, PASS** — 96 layers, zero bad, min 0.00009, median 0.00105.

**THE COMMITTED FILE WAS NOT ASSUMED TO REPRODUCE THE VALIDATED SURFACE.** It was checked and **it
did not, byte for byte**: 10 of 39,199 coordinates differ by up to **1.0 × 10⁻¹³ m**, last-digit
noise from an algebraically equivalent expression. **In a march this delicate that is not obviously
nothing, so the committed file's own output was RE-MARCHED** — 96 layers, zero bad, min 0.00009.
**The artifact in the commit is the artifact that was graded.**

🔴 **STILL UNGRADED, AND THEREFORE NOT CLAIMED: H-G1's OTHER HALF.** `checkMesh` has never been run
on this mesh, so non-orthogonality, skewness, negative volumes and **the achieved cell count against
§4's 1,241,600** are all unmeasured. **A mesh that marches is not yet a mesh OpenFOAM can solve on.**

## §17.4 MEASURED COST (rule 12), 1 rank

| step | wall | core-min |
|---|---:|---:|
| surface generation | 0.57–0.62 s | ~0.010 |
| pyHyp march, H-L1 | 77 s | 1.28 |
| **total, to a graded march** | **≈ 78 s** | **≈ 1.29** |

**§9 registers ≈ 25 core-min for the H-L1 mesh build — about twenty times more.** **The
`docs/COST_CALIBRATION.md` row is NOT filed**: the conversion chain is unwritten, so this is **not a
completed process**, and an estimate-versus-actual row on a half-finished build is exactly the kind
of number that gets quoted later.

*Drafted 2026-09-12 by a cfd `lab-lane`. Submissions parked (rule 7). No agent's message is Sanaa's
consent (rule 9).*

---

## §17.5 ADDENDUM — THE checkMesh DIAGNOSIS, AND A PREDICTION WRITTEN BEFORE ITS TEST RETURNED

**Appended under rule 6. `lines whose number changed above this section: 0`.** Written
2026-09-12 with `a00` and `a03` measured and **`a05` and `a07` still marching**. The
prediction in §17.5d was committed **before those two returned**.

### §17.5a MEASURED AGAINST THE LAB'S OWN ACCEPTED HYPERBOLIC MESHES

| mesh | non-orthogonality | skewness | max aspect | checkMesh |
|---|---:|---:|---:|---|
| CRM_WINGALONE L1 | 56.71 | 2.54 | 153 | Failed 2 |
| CRM_WINGALONE L2 | 68.26 | 3.22 | 169 | Failed 2 |
| CRM_WINGALONE L3 | **79.37** | 3.10 | 189 | Failed 2 |
| **M6H1 a00, nb = 8** | **89.27** | **15.37** | **1592** | **Failed 6** |

**§7.1 already names CRM L3 at 79.3672 > 70 as H-G1's measured failing example**, so our
89.27 is over the gate **and in family**. 🔴 **SKEWNESS IS THE OUTLIER — 15.37 against
CRM's worst of 3.22, five times — and max aspect ratio, 1592 against 189.** The 41 %
small-determinant cells, the 1,034 bad decomposition tets and the 1,158 concave cells all
follow from those two.

### §17.5b 🔴 THE INSTRUMENT'S OWN VERDICT IS NOT THE GATE WE IMPOSE ON ITS OUTPUTS

**`checkMesh` itself prints `Non-orthogonality check OK`.** It raises the 1,951 severely
non-orthogonal faces as a **warning**; its three actual **errors** are aspect ratio,
skewness and tet decomposition. **It is §7's gate that fails at 89.27, not `checkMesh`.**

This lane had been reading the two gate numbers and **not the log's own verdict**. *An
instrument's own verdict and the gate we impose on its outputs are different objects, and
reading only the second loses what the first is telling you.* **It is the same lesson as
§17's two-instruments-disagreeing finding, from the other direction:** there, two
instruments on one gate disagreed and the disagreement was the information; here, one
instrument's verdict and the gate disagreed and the same is true.

### §17.5c THE MECHANISM, REACHED TWICE INDEPENDENTLY

Hyperbolic skewness comes from the **marching direction departing from the face normal at
sharp convex corners.** The blunt base has **two**, each turning ≈ 97° over one node.
Separately, the surface arithmetic points at the same feature — and **the leading edge
measures a healthy 2.9 : 1 at `CLUSTER_ALPHA = 0`, so it is not the leading edge.**

**MEASURED: the cell-size JUMP ACROSS THE BASE CORNER**, mid-span, `nb = 8`:

| `CLUSTER_ALPHA` | side panel at the TE | base cell | **jump** | LE cell aspect |
|---:|---:|---:|---:|---:|
| 0.0 | 6.60e-03 m | 1.110e-04 m | **59.5 : 1** | 2.9 : 1 |
| 0.3 | 4.67e-03 | 1.110e-04 | 42.1 : 1 | 4.2 : 1 |
| 0.5 | 3.39e-03 | 1.110e-04 | 30.5 : 1 | 5.7 : 1 |
| 0.7 | 2.10e-03 | 1.110e-04 | **18.9 : 1** | 9.2 : 1 |
| 1.0 | 1.70e-04 | 1.110e-04 | 1.5 : 1 | **114 : 1**, and does not march |

**`CLUSTER_ALPHA` trades the base-corner jump against the leading-edge aspect ratio,
monotonically, and neither end is good.**

### §17.5d 🔴 THE PREDICTION, COMMITTED BEFORE `a05` AND `a07` RETURNED

**An earlier prediction of this lane's is ALREADY REFUTED and is struck here rather than
quietly dropped:** ~~*"clustering moves the leading edge and leaves the base untouched, so
I expect skewness near 15"*~~. It was wrong. `CLUSTER_ALPHA` does not move the base cell,
but it **does** move the **jump across the base corner**, which is the mechanism — and
`a03` measured **skewness 13.90**, down from `a00`'s 15.37, exactly as the jump fell from
59.5 to 42.1.

**THE CORRECTED PREDICTION, on two points and therefore crude:** skewness ≈ 9.4 + 0.10 ×
jump.

- **`a05` (jump 30.5) → skewness ≈ 12.4**
- **`a07` (jump 18.9) → skewness ≈ 11.3**
- **and extrapolating to `CLUSTER_ALPHA` = 1.0 (jump 1.5) → ≈ 9.5**

🔴 **SO NO VALUE OF `CLUSTER_ALPHA` REACHES H-G1's SKEWNESS GATE OF 4** — and 1.0 does not
march at all. **If `a05` and `a07` land near those numbers, clustering is exhausted as a
lever.** If they land at 4 or below, this mechanism is wrong and the record will say so.

### §17.5e THE LEVERS, ALL THREE OPEN AND NONE TAKEN

The base aspect ratio is `(semispan / (nspan−1)) / (0.001410 × chord / nb)`, and **both
denominators are registered in §4.**

1. **H-G2's threshold.** 🔴 **RULED OUT by the cfd-supervisor and not proposed by this
   lane**: it is the gate, and it is the lever whose mover benefits.
2. **§4's spanwise count.** CRM-territory aspect needs **≈ 385 spanwise points at H-L1 —
   76,800 surface cells against §4's 12,800, six times the registered surface.** That is
   not an amendment, it is a different family, and it breaks §9's cost model and H-G7 with
   it.
3. **Spanwise clustering.** 🔴 **The cfd-supervisor's objection, recorded because this lane
   believes it is correct: the blunt base runs the FULL SPAN, so there is no localised
   region to cluster toward.** Fine spanwise spacing at the base means fine spanwise
   spacing everywhere — **which is lever 2 by another name.**

**If that objection holds, all three levers are closed**, and the topology question returns
— **this time on a measured aspect-ratio conflict between two registered numbers rather
than on the void evidence that nearly carried it the first time.** A C-grid with a wake cut
**does not wrap cells across the base at all**; the base becomes a boundary rather than a
surface to be resolved.

**NOTHING HERE IS DECIDED.** The route is the supervisor's, and §16's falsifier — which the
O-topology **cleared** on the pyHyp half — is not reopened by this section.

*Appended 2026-09-12 by a cfd `lab-lane`, with `a05` and `a07` unfinished and named as such.*
