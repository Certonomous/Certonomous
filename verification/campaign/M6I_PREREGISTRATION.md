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

---

## AMENDMENT 2 — 2026-09-01, BEFORE FIRST COMPUTE: G2 reads the FIRST solve of each iteration, not the last

**Pre-compute amendment under CLAUDE.md rule 2.** Appended at the foot under rule 6; nothing
above is edited, reordered, inserted or deleted. v1.2.

### The condition, and how it was checked

**NO COMPUTE HAS OCCURRED.** `test -e` at the moment of writing: `verification/runs/M6I_runs/L0`,
`L1`, `L2`, `L3` — **all four ABSENT.** `verification/runs/M6I_runs/` contains `analyse_m6i.py`
and nothing else. No mesh, no solution, no solver log exists for M6I.

### What is amended

§4's Gate G2 registers **"all scaled residuals ≤ 1e-8"**. **That threshold is unchanged.**
What is registered here is **which residual the threshold is applied to**, which §4 left
implicit and which materially decides the verdict:

> **G2 is applied to the initial residual of the FIRST solve of each field in the final
> iteration — the value OpenFOAM's own `residualControl` tests. Not the last solve.**

### Why — verified in the installed source, not from memory

With `nNonOrthogonalCorrectors ≥ 1` a field, in practice `p`, is solved **more than once per
outer iteration**. OpenFOAM's convergence control tests the **first** of those solves.
From `/usr/lib/openfoam/openfoam2606/src/finiteVolume/cfdTools/general/solutionControl/`:

```
solutionControl/solutionControl.C:231-232
    residuals.first() = cmptMax(sp.first().initialResidual());
    residuals.last()  = cmptMax(sp.last().initialResidual());

simpleControl/simpleControl.C:71
    const bool absCheck = (residuals.first() < residualControl_[fieldi].absTol);
```

`sp` is the solver-performance pair for that field in that time step, so `.first()` is the
first solve. **A reader keeping the last match returns the final corrector pass — the smallest
residual of the set.**

### The direction of the error, and the size of it

**It errs in the FLATTERING direction: it understates the residual and admits levels that
should fail.** Measured on the comparator's planted two-corrector control, where the two solves
differ by a factor of 1,000:

| reader | value | against G2's registered 1e-8 |
|---|---|---|
| **first solve** (what `residualControl` tests) | **4.0e-07** | **FAILS G2** |
| last solve (what a `tail -1` reader returns) | 4.0e-10 | **PASSES G2** |

> **The verdict flips at the registered threshold. This is not a cosmetic difference.**

**This amendment therefore STRICTLY NARROWS G2** — the first-solve residual is never smaller
than the last-solve residual — and can only turn a `PASS` into a `GATE FAIL`.

### Why it matters most on THIS campaign

**Non-orthogonal correctors are exactly what one reaches for on a highly non-orthogonal mesh,
and this campaign's meshes measure 86–89°.** The reader would have been most wrong precisely on
the geometry M6I is about. `nNonOrthogonalCorrectors 1` is live in this repository now —
`cases/JF1_JET_FLAP/case/system/fvSolution` and 15+ `cases/mega-batch/` cases — so the setting
is not hypothetical.

**This is `L-419`'s shape** — a partial sample reported as the whole — and this team has already
published a wrong `p`-residual column through `grep … | tail -1` on a case with that setting.

### Disclosure

**This was found by the cfd supervisor reading the comparator as a diff, not by its selftest.**
Every other reader in that file carried a planted control; **the residual reader did not, and
that is why it survived.** It was the one reader whose correctness looked too obvious to doubt.
It now carries a control that synthesises a two-corrector log, asserts the reader returns the
**first** solve, asserts the defective form reproduces the **last**, asserts the two **differ**,
and asserts that on a single-solve log they **agree** — so the fix is shown not to have broken
the ordinary case.

### Assertions, MEASURED after the write

| assertion | value |
|---|---|
| threshold, band, cap or label changed | **none — 1e-8 is unchanged; only its operand is fixed, and strictly narrowing** |
| lines edited, reordered, inserted or deleted above this section | **none** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's first 429 lines BEFORE the append | `add11e978be5cda184adf4fc40955e55` |
| md5 of this file's first 429 lines AFTER the append | `add11e978be5cda184adf4fc40955e55` |
| the two digests | **EQUAL — assertion MEASURED, verified after the write** |

---

## ADDENDUM A — 2026-09-01, POST-COMPUTE: the cost basis is checked against the concurrent-`mpirun` finding and is UNAFFECTED; `--bind-to none` is required of any launcher

**Dated addendum under CLAUDE.md rule 2. R0 HAS BEEN GRADED (`GATE FAIL`, see
`verification/runs/M6I_runs/R0_RESULTS.md`), so first compute has occurred and pre-compute
amendment is NO LONGER AVAILABLE to this registration.** This addendum therefore **alters no
gate, no threshold, no cap and no label**, and nothing in it makes any gate easier to pass.
Appended at the foot under rule 6. v1.3.

### A.1 The check, and it returns a NEGATIVE RESULT — recorded rather than left unstated

The heat-transfer team measured, with `taskset`/`mpstat`, that **concurrent independent `mpirun`
invocations each number from core 0**, so six mpiruns piled twelve ranks onto CPUs 0–1 while 14
cores sat idle. The cfd supervisor asked whether **this registration's cost basis** — §5's
`1.3427 core-min per iteration at 399,360 cells`, from which the whole 14,622 core-min estimate
and the 132,180 core-min L0 contingency descend — was measured under that collision, since it
was taken at 4 ranks under `mpirun`.

**IT WAS NOT. The basis is unaffected, and the discriminator is direct rather than inferential.**

OpenFOAM's `ExecutionTime` is the **CPU time of the master rank**; `ClockTime` is **elapsed
wall**. **If four ranks had been piled onto one core the master would have received about a
quarter of a core and the ratio would read ≈ 0.25.** Measured over all 61 samples of
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/run_model_run3.log`:

| statistic | `ExecutionTime / ClockTime` |
|---|---|
| minimum | **0.9851** |
| median | **0.9896** |
| maximum | **1.0194** |

> **The master rank held essentially a full dedicated core for the entire run. There was no
> core-0 pile-up.**

**Corroborated independently by concurrency evidence**, which is weaker and is offered as
corroboration only: the log's final write is `2026-07-28 01:10:16Z` and it spans ≈ 1,233 s, so
the run occupied ≈ 00:50–01:10Z. The only other entries under `/home/ubuntu/certonomous-runs/`
modified within ±2 h are `credential-repair-naca4412-finer_relayered` (last modified 23:51Z) and
`…_ngrow0` (00:15Z) — **both finished before this run's window opened.**

**Also verified rather than assumed:** the JF1 solvers live on this box while §5 was written are
**single-rank `simpleFoam`, not `mpirun`**, so they could not have triggered the core-0
collision — though they did compete for cores in the ordinary way, which §5 already discloses
by recording the 1-minute load average of **14.30 on 16 cores**. **That disclosure stands and is
not revised.**

**Direction, stated for completeness:** had the basis been inflated by pile-up, the registered
estimate would have been **conservative**, not optimistic, and the cap would not have been
endangered. **It is neither: the basis is sound on this axis.**

### A.2 A REQUIREMENT ON ANY LAUNCHER THIS LADDER EVER USES

**No launcher exists yet — NO SOLVER HAS RUN — so this is registered before the fact rather
than as a repair.**

> **Every `mpirun` invocation under `M6I` MUST carry `--bind-to none`.**

**M6I is the most exposed campaign in this team on this axis, because §3 registers 4, 8 AND 16
ranks.** At 16 ranks on a 16-core box, a single concurrent `mpirun` from any other lane is
exactly the collision the finding describes. `--bind-to none` **changes no computed value, only
wall time** — so it moves no number this registration grades, and §5's core-minute figures
remain the basis they were.

### A.3 What this addendum does not do

1. **It does not alter a gate, threshold, cap or label.** §4's gates, §5's estimates and caps
   and §3's ladder are untouched.
2. **It does not revisit R0.** `GATE FAIL` stands.
3. **It does not authorise a solve.** Gate G remains `PENDING` and unreleased.

### Assertions, MEASURED after the write

| assertion | value |
|---|---|
| gate, threshold, cap or label altered | **none** |
| lines edited, reordered, inserted or deleted above this section | **none** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's first 518 lines BEFORE the append | `30ca7cd62031e5d3e7884ba7c0d66d9b` |
| md5 of this file's first 518 lines AFTER the append | `30ca7cd62031e5d3e7884ba7c0d66d9b` |
| the two digests | **EQUAL — assertion MEASURED, verified after the write** |

---

## ADDENDUM B — 2026-09-02, POST-COMPUTE: §5's measured cost basis is STRUCK — the per-iteration rate was read from prints that are 100 iterations apart, and is 99× too high

**Dated addendum under CLAUDE.md rule 2. R0 HAS BEEN GRADED (`GATE FAIL`, see
`verification/runs/M6I_runs/R0_RESULTS.md`), so first compute has occurred and pre-compute
amendment is NO LONGER AVAILABLE to this registration.** Appended at the foot under rule 6. v1.4.

> **THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** It corrects a **measured
> BASIS used for estimating** — not a registered gate, threshold, cap or label. Every gate in §4
> stands unchanged. **Every estimate in §5.1 and every cap in §5.2 stands exactly as frozen and is
> NOT restated, NOT lowered and NOT raised.** **NO VERDICT CHANGES.** R0's `GATE FAIL` stands;
> Gate G remains `PENDING`; Gate P remains unclaimed. **Nothing here makes any gate easier to
> pass, and nothing here overturns a result.**

### B.0 THE LOAD-BEARING CHECK ON THE CAPS, DONE BEFORE ANYTHING WAS WRITTEN

**The question asked first was whether §5's struck figure is load-bearing for a registered cap**,
because a correction that moved a cap would be forbidden to this addendum and would have to stop.

**It is not, and the reason is structural rather than a judgement.** §5.2's caps are **absolute
core-minute integers** — R0 **180**, R1 **310**, R2 **2,500**, R3 **19,800**, ladder total
**22,790**, L0 contingency **165,000**. **Not one of them is expressed as a function of the
basis.** Correcting the basis moves none of them, and **they are left exactly as frozen.**

**The dependency that DOES exist is disclosed rather than absorbed.** §5.2's *headroom* column is
a ratio over §5.1's estimates, and those estimates descend from the struck figure — Addendum A
§A.1 says so in terms ("from which the whole 14,622 core-min estimate and the 132,180 core-min L0
contingency descend"). **So the printed headroom multiples of 3.0× / 3.0× / 2.0× / 1.5× understate
the true headroom on the three solve rungs by a factor of about 99.** The caps are not thereby
loosened: **a cap that turns out to be generous is still the cap, and rule 12's "an overrun stops
the run" is untouched.**

### B.1 WHAT IS STRUCK

**STRUCK, §5, "COST BASIS — MEASURED ON THIS BOX, ON THIS GEOMETRY":**

> ~~**60 consecutive `ExecutionTime` deltas: median 20.140 s/iteration, mean 20.101, min 15.610,
> max 27.680.** At 4 ranks that is **1.3427 core-min per iteration at 399,360 cells** =
> **3.362e-06 core-min per cell per iteration**.~~

**The struck lines are NOT edited, reordered or deleted.** Under rule 6 the original stands where
it is and the strike is recorded here. Everything else in §5 — the unit, the derived-dollar
labelling, the three disclosures, the identification of the log, the rank count and the cell
count — **survives and is confirmed by the re-derivation below.**

### B.2 THE MECHANISM — MEASURED FROM THE LOG, NOT INFERRED

**The deltas are not per-iteration. They are per HUNDRED iterations.** Read from
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/run_model_run3.log`:

| reading | value |
|---|---|
| `printInterval` in the log's own echoed case setup | **`100`** |
| `Time =` lines in the whole log | **61** |
| the `Time` values they carry | **1, 100, 200, 300, … , 5900, 6000** |
| `ExecutionTime` lines | **61** — one per `Time` line, so **60 deltas** |
| first / last `ExecutionTime` | **15.17 s** / **1221.21 s** |
| median of the 60 deltas | **20.12 s** — the registered 20.140, and it is **seconds per 100 iterations** |

> **A 6,000-iteration run cannot have 61 per-iteration prints.** The registered figure multiplied
> a per-100-iteration delta by one iteration's worth of arithmetic.

**The arithmetic that settles it independently of any delta:** the master rank's total
`ExecutionTime` for the whole 6,000-iteration solve is **1,221.21 s = 20.35 wall-minutes**. The
struck basis claims **1.3427 core-min per iteration**, which over 6,000 iterations would be
**8,056 core-min = 2,014 wall-minutes at 4 ranks**. **The run did not take 34 hours; the log's own
`ClockTime` spans 1,233 s.**

### B.3 THE CORRECTED BASIS

`nProcs = 4` read from the log's own banner (not from the case's present `decomposeParDict`,
which now reads 2 and post-dates the run); `nCells: 399360` from
`constant/polyMesh/owner.gz`'s header note, as §5 already records.

| form | window | core-min | cell-iterations | **core-min per cell per iteration** |
|---|---|---|---|---|
| span (`Time` 1 → 6000, `ExecutionTime` 15.17 → 1221.21 s) | 5,999 iterations, 1,206.04 s | 80.403 | 2.39564e9 | **3.3560e-08** |
| whole run (`ExecutionTime` 1221.21 s over 6,000 iterations) | 6,000 iterations | 81.414 | 2.39616e9 | **3.3977e-08** |

**Registered ÷ corrected = 100.18× (span form), 98.95× (whole-run form).** **The registered figure
is about 99 times too high.**

**Per-iteration, the same correction:** **0.013569 core-min per iteration at 399,360 cells**,
against the struck **1.3427**.

### B.4 CORROBORATION — TWO INDEPENDENT RUNS AT OTHER MESH SIZES, RE-DERIVED HERE

Both are ONERA M6 `DARhoSimpleCFoam` primals under the same driver, at `nProcs = 4` read from each
log's own banner, cell counts from each case's `constant/polyMesh/owner.gz`, and both carry
`printInterval 100` so both were read with the interval in hand:

| run | log | cells | window | **core-min/cell/iteration** |
|---|---|---|---|---|
| `A3-onera-m6-sweep-n28_42120` | `run_opt5_onera_n28_42120.log` | **42,120** | `Time` 1 → 1000, `ExecutionTime` 1.90 → 25.40 s | **3.72e-08** span / **4.02e-08** whole-run |
| `A3-onera-m6-adjoint-probe80k` | `run_opt4_probe80k.log` | **79,560** | `Time` 1 → 1000, `ExecutionTime` 2.67 → 34.70 s | **2.69e-08** span / **2.91e-08** whole-run |
| `A3-onera-m6-transonic` (§B.3) | `run_model_run3.log` | **399,360** | `Time` 1 → 6000 | **3.36e-08** span / **3.40e-08** whole-run |

**Three runs spanning a 9.5× range of mesh size agree to within 1.5× of one another, and all three
sit two orders of magnitude below the struck figure.** **The corrected basis is the one that
reproduces across the family; the struck one reproduces nowhere.**

**Stated as a limit rather than glossed:** these are all `DARhoSimpleCFoam` primals, so §5's
disclosure 1 (driver overhead, direction unknown) **survives unchanged**, and §5's disclosure 2
(per-cell cost is NOT constant with mesh size — super-linear, measured by this team at about
`N^1.46`) **also survives unchanged and still means a linearly scaled fine level is under-priced.**
**Correcting the basis does not repeal either disclosure.**

### B.5 THE DEFECT CLASS, NAMED

**A number that was right when it was written and was never re-derived — and a rate taken from a
log without first reading what that log's own print interval was.**

The figure was not a guess. It was computed from a real log, on the right case, at the right rank
count, with the right cell count, and it was even re-examined once already: **Addendum A §A.1
interrogated this exact basis, over these exact 61 samples, and cleared it.** It cleared it on the
axis it was asked about — `ExecutionTime / ClockTime` ∈ [0.9851, 1.0194], so no core-0 pile-up —
and **that finding stands and is not disturbed here, because a ratio of two quantities printed on
the same line is immune to how often the line is printed.** **What no reading of it ever asked was
what the interval between two consecutive prints actually was.** The setting was in the same file,
seven characters long, and unread.

**This is why a basis is re-derived rather than re-cited.** Every later use of it — §5.1's table,
§5.2's headroom column, §5's L0 contingency, Addendum A's premise — inherited the error intact,
because each one cited the number instead of re-measuring it.

### B.6 DIRECTION — THE ERROR IS CONSERVATIVE, AND NOTHING IS OVERTURNED

**It inflated estimates. It could not have endangered a cap, and no run overran because of it.**
A basis 99× high makes every estimate 99× high, every cap sized off it 99× generous, and every
"can we afford this?" answer more cautious than the truth. **No solve has ever run under this
registration** (Gate G is `PENDING`, §4), so no run was stopped, shortened, re-scoped or lost to
it.

**No verdict changes.** R0 is `GATE FAIL` on mesh admission — non-orthogonality **87.6620 /
86.4646 / 87.7462°** against the §3.1 gate of 70° — **a mesh-quality measurement that has no cost
term in it at all.** **Nobody should read this addendum as a result being overturned. It is an
estimating instrument being corrected, in the direction that costs nothing.**

For completeness: **R0's own 60 core-min estimate is NOT affected**, because it was never built on
this basis — it was built by analogy with `F13`'s in-house `blockMesh` ladder, and it has already
been calibrated against its actual **0.3833 core-min** in `docs/COST_CALIBRATION.md`
(row `C-20260901T173329.123480Z-d483e031`).

### B.7 THE CONSEQUENCE THAT MATTERS — A FUNDING DECISION INFLATED BY TWO ORDERS OF MAGNITUDE

**The cost of a route, not the cost of a run, is what this error actually bought.** The ONERA M6
option-3 route was costed on this basis at **136,469 core-min = $116.68 derived** at the recorded
$0.0513/core-h. **Corrected: ≈ 1,362 – 1,380 core-min ≈ $1.17 derived** (the range is the span vs
whole-run form of §B.3). **A route that reads as a hundred-dollar commitment and is in fact a
one-dollar one is a different decision**, and it was being weighed against alternatives priced by
other means.

Applying the corrected basis to §5.1's own rows, **as an illustration and explicitly NOT as a new
registration** — the same linear model, the same cells and iterations, only the basis replaced:

| rung | registered (STANDS) | on the corrected basis |
|---|---|---|
| R1 L3 primal | 103 core-min | **≈ 1.0** |
| R2 L2 primal | 1,239 core-min | **≈ 12.5** |
| R3 L1 primal | 13,220 core-min | **≈ 134** |
| L0 contingency | 132,180 core-min | **≈ 1,336** |

**These four figures are NOT registered, NOT caps, and NOT a re-estimate of this ladder.** They are
printed so the size of the distortion is visible on the face of the document rather than left to be
recomputed. **§5.1's registered estimates and §5.2's registered caps are the ones in force.** They
are also **lower bounds**, because §5's disclosure 2 (super-linear per-cell cost) still applies and
this table, like §5.1's, scales linearly.

### B.8 WHAT THIS ADDENDUM DOES NOT DO

1. **It does not alter a gate, threshold, cap or label.** §4's gates, §5.1's estimates, §5.2's
   caps and §3's ladder are untouched and remain in force as frozen.
2. **It does not revisit R0.** `GATE FAIL` stands, on a measurement with no cost term.
3. **It does not authorise a solve.** Gate G remains `PENDING` and unreleased.
4. **It does not disturb Addendum A.** A's contention finding is independent of the print interval
   and stands; only its inherited premise about the magnitude of the basis is corrected here.
5. **It does not edit any document outside this file.** Two others carry figures descended from the
   struck basis — `docs/COST_CALIBRATION.md` (row `C-20260901T173329.123480Z-d483e031`, which
   restates `1.3427 core-min/iteration` and the `14,622` total) and `docs/LAB_STATE.md` (which
   compares an option-2 costing against "M6I's registered 14,622"). **Neither is load-bearing for
   any registered cap, neither is this registration's to amend, and both are flagged rather than
   touched.**

### Assertions, MEASURED after the write

| assertion | value |
|---|---|
| gate, threshold, cap or label altered | **none — a measured estimating basis is corrected, and every registered cap is left as frozen** |
| any verdict changed | **none — R0 `GATE FAIL` stands, Gate G `PENDING`, Gate P unclaimed** |
| direction of the corrected error | **CONSERVATIVE — estimates were inflated, no cap endangered, no run overran** |
| lines edited, reordered, inserted or deleted above this section | **none** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's first 600 lines BEFORE the append | `8ac0f4f4b017abc3041accdca0e61158` |
| md5 of this file's first 600 lines AFTER the append | `8ac0f4f4b017abc3041accdca0e61158` |
| the two digests | **EQUAL — assertion MEASURED, verified after the write** |
