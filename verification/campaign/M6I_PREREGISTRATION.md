# M6I pre-registration — ONERA M6 transonic, IMPORTED published grid family

**FROZEN by the commit that lands this file.** Written 2026-09-01, **before any solver has been
launched under this registration** and before the mesh instrument it registers exists on disk.
Team: cfd. v1.0.

**Authority:** Sanaa's directive `etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`
(`f4c8e466`) **§6 option 1** and **§0** in full. **§0 governs every clause below.**

**Case id `M6I`.** It is **NOT** `F13`/`F1`. `F13` is a different ladder on a different,
in-house mesh; its verdicts (`R0 GATE FAIL`, case `BLOCKED`) are untouched by this document and
are **not** revisited, reopened or superseded here.

**Companion record:** `verification/campaign/M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md`
carries the provenance, the AGARD title-page verification and the geometry comparison. **All of
that is already measured and is therefore NOT a gate in this file.** Nothing already known is
registered here as a prediction.

---

## 0. REGISTER SEARCH BEFORE THE FREEZE (L-427)

**Searched:** `docs/NUMERICS_KNOWLEDGE.md`, `docs/LESSONS.md`, `docs/standards/MESH_STANDARD.md`,
`docs/MESH_STANDARD.md`, `verification/campaign/` for `onera`, `m6`, `agard`, `butterfly`,
`tip cap`, `su2`, `plot3d`, `cgns`, `import`, `external mesh`.

**It returned:** `N-C6`; `F13` (`F13_ONERA_M6_PREREGISTRATION.md`, `F13_RESULTS.md`,
`F13_TIP_TOPOLOGY_PROBE_PREREGISTRATION.md`); `L-427`; **`L-430`** (landed the same day);
`MESH_STANDARD.md` §3.1 and §8.1; `F1_M6_TOPOLOGY_RULING_2026-08-25.md` and its amendment;
`F1_M6_CORRECTION2_2026-08-25.md`. **It returned NOTHING for `su2`, `plot3d`, `cgns`, `import`
or `external mesh` in either register — this is the lab's first imported external grid family.**
Full readings and their effect on this design are in the companion record §0.

**The single most consequential return, stated here because it changes a premise:** `N-C6`
requires the section half-thickness to go to **zero** at the trailing edge. **AGARD AR-138
Table B1-1 gives `z/l = 0.0007052` at `x/l = 1.0`** — the M6's design trailing edge is
**blunt, 0.14104 % chord**. `N-C6` is correct about sharp trailing edges; **the M6 is not one.**

---

## 1. CASE

ONERA M6 semi-span wing, transonic, **AGARD AR-138 test 2308**.

**Conditions, from the `case_2308.dat` zone headers** (byte-identical to NASA TMR's published
copy, sha256 `020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0`):
**`M∞ = 0.8395`, `α = 3.06°`, `Re = 11.72 × 10⁶`**.

**`Re` IS FORMED ON THE MEAN AERODYNAMIC CHORD `c = 0.64607 m`** (AGARD AR-138 B1-4 §4.7:
*"Areas and lengths used to form coefficients: S = 0.7532 m², c = 0.64607 m"*; B1-6 symbol list:
`Re_c` = *"Reynolds number based on c"*, `c` = *"mean aerodynamic chord"*). **NASA TMR's page for
this case instead specifies `Re_c_root = 14.6e6` "based on root chord with sharp trailing edge".
The two are the same physical Reynolds number under different reference lengths and
`14.6e6 × 0.64607/0.810491 = 11.64e6`. REGISTERED SO IT CANNOT BE CONFUSED LATER: this ladder
uses `Re = 11.72e6` on the MAC. Applying 14.6e6 to the MAC would be wrong by 25 %.**

**Reference quantities for the force coefficients: `S_ref = 0.7532 m²` (the semi-span model
area, AGARD B1-4 §4.7), `L_ref = c = 0.64607 m`.** `S_ref` is checked, not asserted: AGARD's own
`b`, `λ` and `S` reproduce its printed MAC to `+3.99e-05 m` and its printed aspect ratio to
`3.7999` against `3.8`.

**Solver:** `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST**, fully turbulent, with
**`nutUSpaldingWallFunction`** — a continuous wall function valid across the whole `y⁺` range.
Chosen for the same reason `F13` chose it: a switching wall function would change the discrete
operator part-way along a triple.

**Closed non-dimensionally**, because the tunnel stagnation conditions vary run to run
(AR-138 B1-3 §3.7: `To = 292 K ± 5` to `315 K ± 5`, *"cannot be controlled"*):
`T∞ = 288.15 K`, `p∞ = 101 325 Pa` (ISA, **chosen not measured**), `U∞` from `M∞`, and **`μ∞`
back-solved to deliver `Re = 11.72e6` on the MAC. `μ` is set to reproduce `Re`; it is not a
physical property of air at 288.15 K.**

**Geometry: the published NASA TMR / TMBWG sharp-trailing-edge ONERA M6.** Its one substantive
departure from the AGARD definition is **registered on the face of this document**: the AGARD
design TE is **0.14104 % chord thick** and the imported geometry's is **0.000 %**, measured under
a planted control. All seven other planform quantities agree with AGARD to better than 1 %,
and MAC to 45 µm (companion record §4). **A gate below turns on this, and no gate is claimed
that this departure would invalidate.**

---

## 2. WHAT IS ALREADY MEASURED, AND IS THEREFORE NOT A GATE

Rule 2's freeze has evidentiary force only over things not yet known. **These are known, were
measured before this file was written, and are recorded here so they cannot later be mistaken
for predictions this registration got right:**

- the AGARD title-page verification and the seven spanwise stations `y/b = 0.20/0.44/0.65/0.80/0.90/0.96/0.99`;
- the geometry comparison of §1 (six of seven planform quantities within 1 %, MAC to 45 µm,
  TE sharp vs 0.14104 % chord, rounded tip confirmed to 0.36 %);
- that the coarsening chain yields `r = 2.000000` exactly with cell-count ratio `8.0000`;
- that the **demo** namelist family fails `MESH_STANDARD` §3.1 at 88.93 / 88.39 / **86.59°**,
  severe fraction 8.884 / 8.641 / **7.305 %**, **falling** with refinement.

---

## 3. THE LADDER — three geometrically similar levels, §0 step 1

**ONE generator call, then TWO coarsenings.** `hcf_wing_v5p0.f90` is invoked **once**;
`hcf_coarsening_v3p9.f90` produces L2 from L1 and L3 from L2 by removing every other node.

**This is the design's answer to `L-430`, and it is structural, not procedural: no generator
parameter can fail to scale with the ladder, because the generator is invoked once.** Three
`--scale` calls are **explicitly rejected** for this ladder for that reason.

| level | cells | ratio to next coarser | `r` | ranks | target `y⁺` |
|---|---|---|---|---|---|
| **L3** coarse | **15,360** | — | — | 4 | **≈ 1.0** |
| **L2** medium | **122,880** | **8** | **2.000000** | 8 | **≈ 0.5** |
| **L1** fine | **983,040** | **8** | **2.000000** | 8 | **≈ 0.25** |

**`r = 2.000000` in every direction, exactly, by construction.** §0 step 1 admits `1.5 ≤ r ≤ 2.0`;
this sits at the top of the band.

**§0's `y⁺ < 1` on EVERY level is met, and the way it is met is the design decision.** A nested
family cannot hold `y⁺` fixed — coarsening doubles the wall spacing, so `y⁺` doubles per level.
**The single generator call is therefore set to `target_y_plus = 0.25` on the FINE level**, so
the family lands at ≈ 0.25 / 0.5 / 1.0 and **every level is under 1**. `y⁺` is **measured and
reported from the solution on all three levels**, never taken from the generator's target.

**Registered in advance so it is not later read as a defect:** `nr_gs`,
`stretching_tanh_towards_lete` and `R_outer` are **shape parameters, held FIXED** across the
family — they are the analogue of `F13` §5's fixed `β`, and holding them fixed is what makes the
levels similar. Only the counts and the wall spacing change, and they change only through the
coarsener.

**Similarity is CHECKED, not asserted, at every level, from the built meshes:**
cell-count ratio `= 8.0000 ± 0.0001` on both pairs (`L-430`'s `r³` check); node nesting
`L1 ⊃ L2 ⊃ L3` read from the built `polyMesh` to `1e-12` root chords under a live planted
control; the coarsening program's own two assertions (*"Exactly twice as many f-cells as c-cells
in a line"*, *"nested nodes = ncnodes"*) captured from its log.

---

## 4. GATES, THRESHOLDS, CAPS AND LABELS — frozen

### Gate A — mesh admission. **R0. Everything else is gated behind it.**

Per level, from **three real `checkMesh` logs**:

| check | threshold | source |
|---|---|---|
| max non-orthogonality | **≤ 70°** | `MESH_STANDARD.md` §3.1, hard gate |
| max skewness | **≤ 4** | `MESH_STANDARD.md` |
| `checkMesh` prints `Mesh OK` | required | |
| cell-count ratio | **8.0000 ± 0.0001** both pairs | `L-430` |
| node nesting L1 ⊃ L2 ⊃ L3 | **≤ 1e-12 root chords** | |

**Read off the reported MAXIMUM, never off `checkMesh`'s own "Non-orthogonality check OK" line**
— which `N-C6` item 5 recorded printing at 81.58°, and which this lane observed printing
`Mesh OK` at **88.93°** on the demo L3.

**AN ABSENT `checkMesh` LOG READS `ABSENT`. IT NEVER READS CLEAN.** The comparator `test -e`s
each of the three paths, emits `ABSENT` — not silence, not a pass — for any missing one, and
**refuses to grade on that level**.

**If Gate A fails, R0 is `GATE FAIL`, the case is `BLOCKED`, and NO SOLVER RUNS.** Firing an
inadmissible ladder is the `F12` failure and `F13` declined to repeat it; this registration
declines too.

### Gate G — grid convergence, §0 steps 2–4. **The graded quantities.**

**Primary graded quantity: `C_D` at the registered `α = 3.06°`.** Companion smooth quantity per
§0 step 4: **`C_L`**. Both are **integrated forces**, not single-cell samples, so §0's
"smoother companion quantity" caveat does not bite; both are reported with the band.

| gate | threshold | basis |
|---|---|---|
| **G1** iterative convergence | **iterative change in `C_D` ≤ 1/10 of the L1–L2 difference**, on every level | **§0 step 2, verbatim** |
| **G2** residuals | all scaled residuals **≤ 1e-8**, and `C_D` stationary over the last 2,000 iterations to **≤ 1/10** of the L1–L2 difference | §0 step 2 |
| **G3** observed order | **`p` in 1.5 – 2.5** | **§0 step 3**, second-order scheme ± 0.5 |
| **G4** GCI | `GCI_fine` on `C_D` **reported at `Fs = 1.25`**, and **printed on every number** | §0 step 5; rule 5 |

**`p` and the Richardson extrapolate are REPORTED. The verdict grades the FINE value, never the
extrapolate.**

**Rule 5 ordering, unmodified:** (1) any level not iteratively converged or not plateaued →
**`NOT A RESULT`**; (2) triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` →
**`NOT A RESULT`**, with the value, both triples and both orders printed beside it;
(3) `CONVERGING` → `PASS` inside the band else `GATE FAIL`, GCI printed. **The gate can only
turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the reverse. NEVER QUOTE A GCI WHEN THE
THREE VALUES ARE NOT MONOTONE.** Grading by `scripts/roache_triple.py --dim 3`, equal-ratio,
`Fs = 1.25`.

**§0 step 4 is registered NOW, as an obligation, not as an option.** If `p` lands outside
1.5–2.5 this ladder does **not** stop. In order: **(a)** re-check G1/G2 on L1; **(b)** re-verify
similarity (cell-count ratios, the coarsener's nesting assertions, `y⁺` per level); **(c)** add
**L0, a fourth level at the same `r = 2`, 7,864,320 cells**, and recompute `p` on the finest
three. **L0's cost is registered in §5 and its cap is separate.** Up to two further levels are
permitted by §0; **beyond L0 this registration requires a fresh cost registration**, because a
cap is not a ceiling that grows on its own (rule 9).

### Gate P — comparison against the AGARD tap data. **NOT CLAIMED IN THIS REGISTRATION.**

`PENDING` in its charter sense — a queue state for *not yet run*
(`VERIFICATION` §9, `REPORTING` §2 rule 5). **P has not failed. It is not attempted here.**

**It is now COMPUTABLE, which it was not before**, and the reason is recorded so a successor
does not have to rediscover it: the seven stations `y/b = 0.20/0.44/0.65/0.80/0.90/0.96/0.99`
are printed at AR-138 B1-4 §5.1.1 and the report is now on this box and title-page verified.
**Two reasons it is still not claimed here.** First, the reference accuracy AR-138 B1-4 §6.1
prints is **`ΔCp = ±0.02` at `Mo = 0.84`**, and §6.2 records **"Wall interference corrections:
no corrections"** with a semispan-to-tunnel-width ratio of **0.7** (§4.2) — an uncorrected
systematic the report declines to quantify. Second, **the imported geometry's trailing edge is
sharp where AGARD's is 0.14104 % chord thick**, and a `Cp` comparison in the rear 10 % of chord
would be reading that difference, not the model. **A V+G `PASS` here is NOT an M6 validation,
and this document does not let one be read as one.**

---

## 5. COST — rule 12

**Unit: core-minutes. Dollars DERIVED at the recorded c7a.4xlarge rate of $0.0513/core-h and
labelled derived-not-measured; the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).**

**COST BASIS — MEASURED ON THIS BOX, ON THIS GEOMETRY.** Not a 2-D rate scaled up, and not
recall. `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/run_model_run3.log`, ONERA M6
transonic primal, `nProcs = 4`, mesh `nCells: 399360` (read from
`constant/polyMesh/owner.gz`'s header note, `nPoints:410085 nCells:399360 nFaces:1208672`).
**60 consecutive `ExecutionTime` deltas: median 20.140 s/iteration, mean 20.101, min 15.610,
max 27.680.** At 4 ranks that is **1.3427 core-min per iteration at 399,360 cells** =
**3.362e-06 core-min per cell per iteration**.

**THREE DISCLOSURES ON THAT BASIS, none of which is absorbed into the estimate:**
1. **It is a `DARhoSimpleCFoam` primal under a DAFoam optimisation driver, not `rhoSimpleFoam`
   standalone.** The per-iteration cost may include driver overhead. **Direction of the error is
   not known**, so no correction is applied.
2. **Per-cell cost is NOT constant with mesh size** — this team landed exactly that
   (`5d53328c`: *"a cap scaled linearly from a coarse level under-caps the fine one"*).
   **The linear scaling below therefore UNDER-estimates L1.** The cap in §5.2 carries the
   headroom for it explicitly rather than silently.
3. **The reference log was recorded under unknown contention.** This estimate is **gross**.

### 5.1 The estimate

| rung | cells | iterations | ranks | **core-min (est.)** | derived $ |
|---|---|---|---|---|---|
| **R0** generate + coarsen + 3 × `plot3dToFoam` + 3 × `checkMesh` | — | — | 1 | **60** | $0.05 |
| **R1** L3 primal | 15,360 | 2,000 | 4 | **103** | $0.09 |
| **R2** L2 primal | 122,880 | 3,000 | 8 | **1,239** | $1.06 |
| **R3** L1 primal | 983,040 | 4,000 | 8 | **13,220** | $11.30 |
| | | | | **TOTAL 14,622 core-min** | **$12.50 (derived)** |

= **243.7 core-hours**. Wall-clock at 8 ranks ≈ **30 h**, and **the box is shared** — sister
lanes were at a 1-minute load average of 14.30 on 16 cores while this was written. **R1–R3 run
`nice`d and are expected to take longer in wall time than that; wall time is not the budget and
is not what stops the run.**

**REGISTERED CONTINGENCY — L0, §0 step 4(c), fires ONLY if `p` lands outside 1.5–2.5:**
7,864,320 cells, 5,000 iterations, 16 ranks = **132,180 core-min = 2,203 core-h = $113 derived**,
**its own separate cap of 165,000 core-min.** It is registered now so that firing it later is
not a new decision taken to rescue a bad `p`.

### 5.2 Caps — **an overrun STOPS the run; it does not get a new budget**

| rung | cap (core-min) | headroom over estimate |
|---|---|---|
| R0 | **180** | 3.0× |
| R1 | **310** | 3.0× |
| R2 | **2,500** | 2.0× |
| R3 | **19,800** | 1.5× |
| **ladder total R0–R3** | **22,790** | 1.56× |
| L0 contingency (separate) | **165,000** | 1.25× |

**The 1.5× on R3 is deliberate and is the disclosure of point 2 above**: linear per-cell scaling
is known to under-estimate the fine level, so the fine level carries the headroom. **A row over
3,600 wall s is recorded as a stall and reported as waste, separately named, never absorbed into
the actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

**Authority:** Sanaa's 2026-08-21 blanket covers CPU runs of this size, and her §6 directive
states *"Cost is not a constraint."* **Neither is read as removing the obligation to cost the
run, and a blanket is not a per-item reading (rule 9).**

### 5.3 Calibration — rule 12's estimate-versus-actual

**At the completion of every rung**, the actual core-minutes are read from the logs and compared
against the estimate above; the ratio actual/predicted is stated, the gap attributed
(contention / waste / misprediction, **waste named separately, never absorbed**), and **a row is
filed to `docs/COST_CALIBRATION.md`** under that file's append rules and the rule-10
private-index protocol. **A completion report without that comparison is incomplete.**

---

## 6. COMPLETION — rule 4, strict, all-or-nothing

A level is done only if **all** of it holds: `rc = 0`; an `End` line; **last time == `endTime`**;
fields `U p T rho nut k omega` present at `endTime`; `ExecutionTime` count == `endTime`; and
**every field at `endTime` NEWER than the case's own `0/U`** — the age guard. **The launcher
refuses a case where `0` or a time directory already exists.** The comparator **refuses
(exit 2) rather than degrade** on any failed clause.

---

## 7. PLANTED CONTROLS — rule 3, on every zero this ladder can report

**A zero from a reader not shown able to see a non-zero is not evidence.** Each comparator
plants, reads back from disk, and **refuses if the plant is invisible**:

| reader | plant | must see |
|---|---|---|
| node-nesting comparator | 1e-9 root-chord displacement of one nested node | the displacement |
| cell-count-ratio check | one cell added to a level | ratio ≠ 8.0000 |
| `checkMesh` admission reader | a `checkMesh` log path removed | **`ABSENT`, not a pass** |
| force-coefficient reader | a known offset added to the force file | the offset |
| `y⁺` reader | a scaled `nut` field | the scaled value |

**This is not a promise to be careful.** The planted-control refusal is in the comparator, and a
comparator that cannot see its plant **exits 2 and grades nothing** — which is exactly how this
lane's own first geometry reader was caught and discarded before it reported a number
(companion record §4).

---

## 8. WHAT THIS REGISTRATION DOES NOT CLAIM

1. **It does not claim the family will clear Gate A.** The demo family did not, at
   88.93 / 88.39 / 86.59°. The production namelist has never been run. **Gate A is a real gate
   whose outcome is unknown, and R0 may well be `GATE FAIL`.**
2. **It does not claim an M6 validation.** Gate P is not attempted (§4).
3. **It does not claim the imported geometry is the AGARD geometry.** It is the AGARD geometry
   with the trailing edge sharpened, and the size of that departure is registered in §1.
4. **It does not touch `F13`, `F1`, `N-C6` or any dafoam artifact.** `N-C6`'s premise is
   recorded as inapplicable to the real M6; **`N-C6` itself stands and is correct about sharp
   trailing edges.**
5. **It does not register the blunt-TE build.** AGARD Table B1-1 and TMR's
   `AileM6_with_thick_TE.igs` are both held, and the generator ships blunt-section inputs, so
   the route exists — **but it is not registered here and no claim is made that it clears any
   gate.** It is named so a successor knows the door was seen and left shut deliberately.

## 9. FROZEN PATHS

- generator + coarsener sources, namelists and section file: from `wing-release-072319.zip`,
  sha256 `b8005774fff3bcf2c86…`, provenance in the companion record §1.2
- primary reference: `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`,
  sha256 `a96a73304c8328bd97c828cead2df9326675fd2340230d7e81fcf9f8191e7ffb`
- tap data: `cases/dafoam/ladder-a/logs_A3/case_2308.dat`, sha256
  `020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0` — **read-only; this ladder
  writes nothing under `cases/dafoam/`**
- run outputs: `verification/runs/M6I_runs/`
- **NOTHING is written under `/home/ubuntu/certonomous-runs/`.** It sits outside git and one of
  its entries holds the only surviving copy of a transonic M6 solution. **It is read from and
  never written to, meshed into, pruned or repointed at.**

---

## AMENDMENT 1 — 2026-09-01, BEFORE FIRST COMPUTE: Gate A's cell-count clause is NARROWED, because its registered tolerance cannot see a one-cell perturbation

**Pre-compute amendment under CLAUDE.md rule 2**, which permits amendment before first
compute **and requires the condition to be stated and how it was checked.** Appended at the
foot under rule 6; nothing above is edited, reordered, inserted or deleted. v1.1.

### The condition, and how it was checked — NAMED DIRECTORIES THAT DO NOT EXIST

**NO COMPUTE HAS OCCURRED UNDER THIS REGISTRATION.** Checked by `test -e` on each of the four
run directories this ladder would write, at the moment of writing:

| path | state |
|---|---|
| `verification/runs/M6I_runs/L1` | **ABSENT** |
| `verification/runs/M6I_runs/L2` | **ABSENT** |
| `verification/runs/M6I_runs/L3` | **ABSENT** |
| `verification/runs/M6I_runs/L0` | **ABSENT** |

`verification/runs/M6I_runs/` contains exactly one entry, `analyse_m6i.py`, the comparator.
**No mesh, no solution, no `checkMesh` log and no force coefficient exists for M6I.**

### What is amended, and in which direction

§4's Gate A registers the cell-count check as **"cell-count ratio `8.0000 ± 0.0001` both
pairs (`L-430`)"**. That clause is **retained and still applied**. **A second clause is added
in front of it:**

> **(i) EXACT INTEGER: `cells_fine == 8 × cells_mid`, as integers, on both pairs.**
> **(ii) the registered float band `8.0000 ± 0.0001`, unchanged.**

**This STRICTLY NARROWS Gate A. It can only turn a `PASS` into a `GATE FAIL`, never the
reverse.** No threshold is loosened, no band widened, no cap raised, and no label changed.

### Why — and the reason is a defect the comparator's own selftest found in this gate

The comparator's planted control added **one cell** to the fine level and required the gate to
see it. **The gate admitted it.** The arithmetic:

> `983041 / 122880 = 8.0000081380`. Deviation from 8 is **8.138e-06**, against a registered
> tolerance of **1.0e-04**. **A one-cell perturbation is 12.3× INSIDE the gate's own
> tolerance.**

**The registered float band was the wrong instrument for this ladder, not merely a loose one.**
The family is produced by one generator call plus a coarsening program that removes every other
node, so the ratio is **exactly 8 by construction, on integers**. Any departure — of even one
cell — means a level was **regenerated rather than coarsened**, which is precisely the
similarity failure `L-430` exists to catch and precisely what a float tolerance sized for
approximate-`r` families cannot see.

**The float band is kept rather than replaced** because it is the registered clause and because
it remains the correct check for any future level not produced by the coarsener.

### Measured, after the change

From the comparator's selftest, which gates every grading path:

| case | cells (coarse first) | clause (i) exact | clause (ii) band | verdict |
|---|---|---|---|---|
| exact family | 15,360 / 122,880 / 983,040 | **True** | **True** | **PASS** |
| **one cell added** | 15,360 / 122,880 / **983,041** | **False** | **True** | **GATE FAIL** |
| gross non-similarity | 15,360 / 122,880 / 188,006 | False | False | **GATE FAIL** |

> **The one-cell case is caught by clause (i) ALONE. Clause (ii) reads it as passing.** That
> row is the whole justification for this amendment and it is a measurement, not an argument.

### Disclosure

**This amendment was forced by a control that failed, not by foresight.** The gate as frozen at
`73148a9c` would have admitted a family whose fine level was not an exact coarsening of the
medium one. **It was caught before any compute only because the comparator's selftest plants
into every gate it grades and refuses when the plant is invisible** — CLAUDE.md rule 3 applied
to this comparator's own thresholds rather than only to its readers.

### Assertions, MEASURED after the write

| assertion | value |
|---|---|
| gate loosened, band widened, cap raised or label changed | **none — the change is strictly narrowing** |
| lines edited, reordered, inserted or deleted above this section | **none** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's first 343 lines BEFORE the append | `d7d3530e4b03c95ae6bed892fa5f09d2` |
| md5 of this file's first 343 lines AFTER the append | `d7d3530e4b03c95ae6bed892fa5f09d2` |
| the two digests | **EQUAL — assertion MEASURED, verified after the write** |
