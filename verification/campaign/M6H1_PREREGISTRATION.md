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
