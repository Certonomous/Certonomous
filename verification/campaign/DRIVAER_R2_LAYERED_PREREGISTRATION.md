# DRIVAER R2 — LAYERED THREE-LEVEL FAMILY AND SOLVE — PRE-REGISTRATION

    Campaign     : navier_class / DRIVAER
    Rung         : R2 (layered family; successor to R1 Stage A, which had NO wall layers)
    Registered   : 2026-09-12, before any R2 compute
    Author       : cfd-team lab-lane, on the cfd-supervisor's ruling of 2026-09-12
                   ("stop diagnosing and start solving"), recorded [lab-attributed].
    Status at freeze: NO r2_* run directory exists. Verified by the condition below.
    Sanaa        : 2026-09-10T20:44Z "DrivAer: launch."; 2026-09-11 "all teams continue
                   working on the cases, fixing and solving."

    PRE-COMPUTE CONDITION, AND HOW IT WAS CHECKED (rule 2, first bullet).
    At the moment of this freeze the three run directories this document governs
        verification/runs/navier_class/DRIVAER/r2_coarse
        verification/runs/navier_class/DRIVAER/r2_medium
        verification/runs/navier_class/DRIVAER/r2_fine
    DO NOT EXIST. Checked by `ls -d` on each of the three paths, all three reporting
    "No such file or directory", in the same shell invocation that wrote this line.
    Amendments before first compute are therefore legal. After the first `snappyHexMesh`
    of r2_coarse starts, every gate, threshold, band, label and cap below is CLOSED.

    SUBMISSIONS PARKED. Nothing here leaves the box.

---

## 0. WHAT THIS RUNG IS, AND WHAT IT IS NOT

R1 Stage A solved a DrivAer notchback with **no wall layers at all**
(`addLayers false` in every graded R1 dict — verified by diff, §2). Its fine level
ran 3000 iterations at 8 ranks, rc=0, and its own report recorded
`y+ ~ 2342/1171/585` and `GATE FAIL` on "Cd not plateaued".

R2 changes exactly one thing: **wall layers are switched on, with `relativeSizes true`**,
in the configuration that the LAYERFIX A1 arm graded at 50.057 % achieved layer
coverage. Nothing else about the family moves.

R2 is a **wall-resolution family**. It is **NOT a Roache triple** and no grid gate is
registered — see Gate G below, which is registered as ABSENT and gives its reason in
advance.

---

## 1. WHAT IS CARRIED FORWARD AS ESTABLISHED (not re-derived, not re-litigated)

| # | Established fact | Artifact |
|---|---|---|
| E1 | Under `relativeSizes false`, `firstLayerThickness 0.00075`, achieved layer fraction was 0 %; the absolute last layer was 1.831 mm against a 50 mm cell, ratio 27.3x, outside the 2–4x band. | `DRIVAER_LAYERFIX_PREREGISTRATION.md` |
| E2 | Under `relativeSizes true` the same coarse level achieves **50.057 %** (58,479 / 116,825 layer cells), final illegal faces 0, 186,709 cells after layers. **GATE FAIL, MIDDLE band, exactly as frozen** (commit `1aac8f2ec`). | `.../LAYERFIX_A1_coarse_relativeSizes/GUARD_VERDICT.txt` |
| E3 | The 52k negative-volume cells belong to the `addLayers true` DIAGNOSTIC build, not the graded family. The graded R1 family has `n_negative_volume_cells = 0` at all three levels (128,230 / 748,658 / 5,025,587 cells), all three printing `Failed 3 mesh checks`. | `.../MESH_FAMILY_MEASURED.json` |
| E4 | The residual wheel/underbody group has **no surviving explanation**: H1 REFUTED, patch-shape NOT SUPPORTIVE, H2b REFUTED (section-6 enumeration exhausted), H4 NOT A RESULT on an instrument defect, H5 REFUTED on a twice-planted instrument (0.0000 opposition over 52 wall patches / 27,816 wall faces). **A measured open question. NOT reopened here.** | `H2_JUNCTION_PARTITION.md`, `H4_...md`, `H5_...md` |
| E5 | The symmetry plane is planar to 0.066 mm; the 0.48 m alarm was WITHDRAWN; the 14,144 count is confirmed by a third independent route (`a8f419662`). **Not resurrected.** | commit `a8f419662` |
| E6 | `CTRL_SURFACE_Outlet` and `Mirrors2` have appeared as a distinguished pair three times. **Noted if they reappear. No hypothesis is built on them in this registration.** | B1, B2, H4 records |
| E7 | R1 fine solve, MEASURED: 5,025,587 cells, 8 ranks, 3000 iterations, wall 36,496 s → **4,866 core-min**, $4.16 derived. Per-cell-iteration cost **1.9365e-05 core-s**. | `.../r1_fine/log.simpleFoam`, `RUN_META.txt` |
| E8 | R1 fine residuals **stall flat** from iteration 1000 to 3000: `p` 6.341e-03 → 6.939e-03 → 6.594e-03; `Uy` 1.651e-02 → 1.476e-02. 2000 extra iterations moved them by nothing. | `.../r1_fine/log.simpleFoam` |

---

## 2. THE FAMILY — ONE CHANGE, PROVEN BY DIFF

The three R2 level roots are assembled from the three **graded R1 level roots**
`r1_coarse`, `r1_medium`, `r1_fine`. For each level:

* `system/snappyHexMeshDict` is replaced by a **byte-identical copy of the A1 dict**
  `verification/runs/navier_class/DRIVAER/LAYERFIX_A1_coarse_relativeSizes/system/snappyHexMeshDict`.
  This is legitimate at every level because the graded R1 family's
  `snappyHexMeshDict` is **byte-identical across all three levels** — verified: `diff`
  of coarse-vs-medium and medium-vs-fine both empty. The only per-level file is
  `blockMeshDict`.
* `system/{blockMeshDict, controlDict, fvSchemes, fvSolution, meshQualityDict,
  surfaceFeatureExtractDict}` are copied from `r1_<level>` and asserted **byte-identical
  by `cmp`** to their R1 originals.
* `constant/triSurface/drivaer_466.stl` is copied and asserted **byte-identical by `cmp`**
  to the R1 STL. The `.eMesh` is **regenerated** by `surfaceFeatureExtract` inside the
  build and then asserted byte-identical to the R1 `.eMesh` — a stronger check than
  copying it.

The single change, as `diff r1_coarse/system/snappyHexMeshDict → A1` (5 hunks, one
concern):

    addLayers       false  ->  true
    tolerance       1.0    ->  2.0            (snapControls)
    implicitFeatureSnap true -> false ; explicitFeatureSnap false -> true
    relativeSizes   false  ->  true
    firstLayerThickness 0.00075  ->  finalLayerThickness 0.5
    minThickness    0.0003 ->  0.02

**These five hunks are exactly and only the hunks that were graded at A1.** The
build REFUSES (exit 2) if `diff r2_<level>/system/snappyHexMeshDict A1/system/snappyHexMeshDict`
is non-empty, or if any other `system/` file or the STL differs from `r1_<level>`.

Layer stack, for the record (dict-derived, therefore **INPUT, not observation**):
5 layers, expansion 1.25, final layer 0.5 x local cell ⇒ nominal first layer
0.5/1.25^4 = **0.2048 x local cell**, nominal total 1.6808 x local cell. Surface
refinement level 4 ⇒ local cell = h_bg/16 = 50 / 25 / 12.5 mm at coarse / medium / fine.

> **A NUMBER COMPUTED FROM THE INPUT IS NOT AN OBSERVATION OF THE OUTPUT.** Every
> number in the preceding paragraph is dict arithmetic and is registered here as
> such. Under `relativeSizes true` the requested last layer IS 0.5 x the local cell
> **by definition**, so the ratio last-layer/cell is 2.0 at every level, always: it
> is not a cross-check, it cannot fail, and it is **not used as a gate anywhere in
> this document**. This is the precise defect that bit this family on 2026-09-11 and
> it is named here so it cannot recur silently. Every graded number below is read
> from the BUILT mesh or from the solver's own output.

---

## 3. GATES, THRESHOLDS, BANDS, LABELS

For every gate: **WHAT RESULT WOULD HAVE FAILED THIS TEST?**

### Gate M1 — MESH BUILD COMPLETION AND INDEX INTEGRITY (per level)

**PASS** iff all of: every step in `BUILD_RC` has `rc=0`; `ALL_STEPS_OK` present;
`constant/polyMesh/{points,faces,owner,neighbour,boundary}` present; **`0/polyMesh`
ABSENT**; and the index test holds — max vertex index in `faces` < nPoints, zero
unused points, and (nCells, nFaces, nPoints) from `constant/polyMesh/owner`'s
`note:` header **equal** to snappy's own `Layer mesh : cells:N faces:M points:P` line.

Else **GATE FAIL**. Cap or memory refusal → §5 Class 3.

*What would have failed this test?* A build whose `snappyHexMesh` rc ≠ 0. A mesh whose
`faces` file references a point index ≥ nPoints (a splice). A mesh whose header counts
disagree with the snappy line — the exact signature the MESH_SPLICE_PROOF record was
written to catch. A level that wrote its mesh to `0/polyMesh` instead of `constant/`.
**The index test runs and its result is printed BEFORE any checkMesh number from that
level is quoted anywhere.**

### Gate M2 — SOLVABILITY (per level)

**PASS** iff `n_negative_volume_cells == 0` **AND** illegal faces == 0 **AND**
`max_non_ortho < 75.0` deg.

**Recorded but NOT gating:** concave cells, skew faces, low-determinant cells,
`max_skewness`. Reason, registered in advance: the graded R1 family prints
`Failed 3 mesh checks` at all three levels with **zero** negative volumes, and
`simpleFoam` ran on the R1 fine mesh for 3000 iterations to rc=0 (E7). Concavity and
skewness degrade accuracy; zero negative volumes and zero illegal faces are the limb
that decides whether the solver can run at all. The report **names which three checks
failed at each level** and says of each whether it is admissible for a solve.

*What would have failed this test?* A level reporting any negative-volume cell — the
`addLayers true` DIAGNOSTIC build reported ~52,000 and this gate would have refused it
outright (E3). A level reporting `***Error in face pyramids`. A level whose max
non-orthogonality reached 75 deg (R1 measured 64.76 / 64.41 / 64.94 — ~10 deg of margin,
so this threshold is not free).

### Gate M2c — MESH-STANDARD CONFORMANCE AND CLAIM CAP (per level)

`docs/standards/MESH_STANDARD.md` sets max skewness 4.0. R1 measured 6.33 / 18.06 /
10.32 and Stage A already declared non-conformance with a claim cap. R2 is
**registered in advance as NON-CONFORMING unless measured otherwise**, and carries the
same cap verbatim: **this result is NOT a credential, MUST NOT be entered in a matrix
as HOLDS or GATE REACHED, and may appear only as a STATED-LIMITATION row carrying the
measured exceedance.**

*What would have failed this test?* Nothing can "fail" a cap — but the cap is
falsifiable in the other direction: if a level measures max skewness < 4.0 it is
CONFORMING and the cap lifts for that level. Predicted: no level conforms.

### Gate M3 — LAYER COVERAGE DELIVERED (per level), three bands

Measured as snappy's own `Layer mesh` cell count minus the snapped cell count, over the
wall-adjacent cell count — the identical quantity and arithmetic A1 used
(58,479 / 116,825 = 50.057 %).

| band | coverage | verdict |
|---|---|---|
| HIGH | ≥ 70.0 % | **PASS** |
| MIDDLE | 40.0 % ≤ c < 70.0 % | **GATE FAIL** (mechanism operating, coverage short) |
| LOW | c < 40.0 % | **GATE FAIL** (fix does not carry to this level) |

**Registered prediction, before the run.** (i) coarse reproduces A1 to within ±2.0
percentage points, i.e. **48.06 % ≤ c_coarse ≤ 52.06 %**; the coarse level is a rebuild
with byte-identical dicts, so anything outside that band falsifies the reproduction.
(ii) **c_medium ≥ c_coarse and c_fine ≥ c_medium** — finer surface cells mean thinner
requested layers, hence less medial-axis truncation. A level landing *below* the level
coarser than it falsifies this monotonicity prediction and is reported as such.

*What would have failed this test?* c_coarse = 0 % would have said `relativeSizes` was
not the mechanism after all. c_coarse outside 48.06–52.06 % falsifies the rebuild.
c_fine < c_coarse falsifies monotonicity. All three are recorded outcomes, not escapes.

### Gate Y1 — y+ ADMISSIBILITY, STATED BEFORE A CORE-MINUTE IS SPENT ON THE SOLVE

Friction velocity from `U_inf`, `Re_L` and the vehicle length **alone**:
U_inf = 38.889 m/s, Re_L = 7.19e6, L = 2.79 m, nu = 1.507e-05 m2/s;
Cf = 0.058 Re^-0.2 = **2.4665e-03**; u_tau = U sqrt(Cf/2) = **1.36569 m/s**;
**y+ = 90,623 per metre of wall distance.**

Sanity check of the estimator against the record, not against itself: it reproduces
Stage A's own no-layer y+ figures — predicts 2266 / 1133 / 566 against Stage A's
reported 2342 / 1171 / 585, **within 3.3 % at every level.**

The wall distance `y` is the **first-cell-centre distance measured from the BUILT
mesh** (OpenFOAM's own `writeCellCentres` output, owner-cell centre to boundary-face
centre), per wall face — an observation of the output, never dict arithmetic.

**Band.** A level is **WALL-FUNCTION ADMISSIBLE** iff the area-weighted median y+ over
**layered vehicle wall faces** lies in **[30, 300]**.

**Registered prediction, before the run**, from A1's MEASURED achieved overall
thickness (BodyHood: 0.0752 m over 4.14 achieved layers ⇒ first layer 12.38 mm,
centre 6.19 mm, y+ 561 at coarse) scaled by the level's cell size:
median layered y+ **coarse 400–800 (PREDICTED NOT ADMISSIBLE)**, **medium 200–400
(PREDICTED BORDERLINE)**, **fine 100–200 (PREDICTED ADMISSIBLE)**.

*What would have failed this test?* A fine level whose median layered y+ exceeded 300
or fell below 30. Note this registration predicts in advance that **the coarse level
FAILS Y1** — the gate has a failing branch that is expected to fire.

### Gate Y2 — MIXED-WALL-TREATMENT DISCLOSURE (claim cap, not a pass/fail)

A1 measured that roughly half the wall got layers. The report **must** name, for every
solved level, which patches are in the layered group and which are in the unlayered
group, with each group's face count, wall area and median y+ **stated separately**.

**REGISTERED CLAIM CAP.** A Cd produced by this family is a **MIXED-WALL-TREATMENT Cd**.
The wheels, brake discs, wheel supports, powertrain, `Mirrors2` and `CTRL_SURFACE_Outlet`
carry **no prismatic layer** (A1 measured 0.00 layers on each) and are resolved by the
bare snapped cell at y+ ~ 4x the layered group's. **A Cd from this family MUST NOT be
cited as a Cd on a fully layered DrivAer body.** Citing it without this cap is the
failure this clause exists to prevent.

### Gate S1 — SOLVE COMPLETION (per solved level), rule 4, all-or-nothing

rc = 0 (from the sidecar written INSIDE the detached wrapper); an `End` line; last time
== `endTime`; fields `U p k omega nut phi` present at `endTime`; `ExecutionTime` count
== round(endTime/deltaT) = 2000; and the **age guard** — every field at `endTime`
strictly NEWER than the case's own `0/U`. Any clause failing ⇒ **NOT A RESULT**, and no
number from that level is quoted.

*What would have failed this test?* A run stopped by the cap (rc=124) — no `End` line.
A run whose last written time is 1000 because the wall clock ran out. A field older than
`0/U`, meaning the answer predates the run allowed to produce it. A reconstructed `0/`
stamping `0/U` newer than the endTime fields — which is why the launcher reconstructs
with `-newTimes`.

### Gate S2 — ITERATIVE STATIONARITY (the instrument Stage A lacked)

Window **(1000, 2000]**, split into four blocks of 250 iterations.
**STATIONARY** iff **block-mean span < 3.0 %** of the window mean **AND**
**|second-half mean − first-half mean| < 2.0 %** of the window mean.
NOT STATIONARY ⇒ the level's Cd is **NOT A RESULT**.

**Why this instrument and why these numbers.** Stage A's GATE FAIL read "Cd not
plateaued" — a pointwise plateau test applied to a quantity that is physically an
oscillation, not a fixed point. The R1 fine run's residuals stall flat from iteration
1000 (E8) while Cd oscillates about a stationary mean. Measured on that run's own
`coefficient.dat`, **before this registration was frozen and on a different mesh**:

| window | mean Cd | four block means | span | half-to-half drift |
|---|---|---|---|---|
| (0, 1000] | 0.31058 | 0.34669 0.30019 0.29664 0.29881 | **16.116 %** | **−8.280 %** |
| (1000, 2000] | 0.29985 | 0.30185 0.29693 0.30013 0.30048 | 1.640 % | +0.306 % |
| (2000, 3000] | 0.29835 | 0.29823 0.29502 0.29965 0.30051 | 1.840 % | +1.158 % |
| (1000, 3000] | 0.29910 | 0.29939 0.30031 0.29663 0.30008 | 1.230 % | −0.499 % |

The thresholds are set **above the largest stationary value actually observed**
(span 1.840 %, drift 1.158 %) and **far below the transient's** (16.116 %, 8.280 %) —
3.0 % is 1.63x the largest observed stationary span and 5.4x below the transient;
2.0 % is 1.73x the largest observed stationary drift and 4.1x below the transient.
Recorded honestly: a 1.0 % drift threshold would have failed the R1 (2000, 3000]
window, which is stationary; it is therefore not used.

*What would have failed this test?* The R1 fine window (0, 1000] fails it on both limbs
by a factor of 4–5. Any run still descending out of its initial transient at iteration
1000 fails it. A run whose oscillation amplitude is growing fails the span limb. A run
drifting monotonically fails the drift limb. **If a level fails S2 at endTime = 2000,
that is the reported outcome. There is no extension under this registration: a longer
run is a NEW registration.** (Rule 2 — a gate is not re-opened after seeing the answer.)

### Gate S3 — Cd DIAGNOSTIC BAND — **NOT A VALIDATION GATE, NOT A CREDENTIAL**

Window-mean Cd over (1000, 2000] **in band** iff 0.20 ≤ Cd ≤ 0.40.
The DrivAerML reference **Cd_ref = 0.2758368** is **REPORTED BESIDE, NOT GATED AGAINST**.
**An in-band value is NOT agreement with the reference and MUST NOT be cited as
agreement** (carried verbatim from the Stage A scope statement). The reference is a
CODE reference (hybrid RANS-LES), not experiment; the disavowal in
`drivaer_reference_notchback.json` applies unchanged.

*What would have failed this test?* A window-mean Cd outside 0.20–0.40 — e.g. the
gross-error signatures this band exists to catch: Cd ~ 5.7 (the run's own iteration-1
value, before the field develops), or a Cd near zero from a forceCoeffs block pointed at
the wrong patch set.

### Gate G — GRID CONVERGENCE — **REGISTERED AS ABSENT, AND FORBIDDEN**

**No Roache triple, no order, no GCI may be computed or quoted from this family.**
Reason, registered in advance and *not* discovered afterwards: under `relativeSizes true`
the first-layer thickness scales with h, so the first-cell y+ changes by ~2x per level
(predicted 561 / 280 / 140). The wall model is therefore a **different model on each
level**, and a Roache order built from that measures the closure changing, not the grid.
This is the R1 builder's own documented reason for choosing `relativeSizes false`
(`cases/navier_class/DRIVAER/mesh/build_drivaer_level.py`, docstring "WHY THE NEAR-WALL
LAYER IS ABSOLUTE AND NOT RELATIVE") and it now applies **against** us. Stage A reached
the same conclusion from the other direction.

The delivered refinement ratio is still **measured and reported, from BUILT cell counts,
never from the nominal**: R1 measured r_eff = 1.8007 (coarse→medium) and 1.8864
(medium→fine) against a nominal 2.0 — the family delivers ~1.8, not 2.0, because
`nCellsBetweenLevels` buffers in CELLS and the refinement is surface-banded, not
volume-filling. **Registered prediction: both R2 steps land in 1.75 ≤ r_eff ≤ 1.95.**

---

## 4. COMPUTE CAPS AND COST BASIS

**Rate: c7a.4xlarge at $0.0513/core-h — owner-stated 2026-08-21/22. The box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure in this
document and in every report against it is DERIVED, NOT MEASURED.**
Unit of record is **core-minutes** = wall s x ranks / 60.

### Mesh build (serial, 1 rank ⇒ core-min == wall-min)

| level | basis (MEASURED, R1/A1) | predicted | **CAP** |
|---|---|---|---|
| coarse | A1 full build 2.52 core-min | ~6 | **20 core-min** |
| medium | R1 snappy 364 s x 1.81 layer factor | ~15 | **90 core-min** |
| fine | R1 snappy 2,359 s x 1.81 + checkMesh at ~7.3 M | ~90 | **300 core-min** |

Layer factor 1.81 = A1 coarse snappy wall 122.6 s / R1 coarse 67.6 s, MEASURED.
**Mesh total cap 410 core-min = 6.83 core-h = $0.35 derived.**

### Solve

Basis, MEASURED (E7): **1.9365e-05 core-s per cell-iteration**, from R1 fine
36,496 s x 8 ranks / (5,025,587 cells x 3000 iterations).

| level | predicted cells | predicted core-min @2000 it | ranks | **CAP core-min** | cap wall s |
|---|---|---|---|---|---|
| coarse | 186,709 (A1 measured) | 121 | 4 | **400** | 6,000 |
| medium | 1.05–1.30 M | 704 | 4 | **2,200** | 33,000 |
| fine | 7.3–8.7 M | 4,712 | 8 | **5,000** | 37,500 |

**TOTAL REGISTERED CAP: 8,010 core-min = 133.5 core-h = $6.85 DERIVED.**
Under $25 ⇒ inside the 2026-08-21 pre-authorisation. A blanket is not a per-item read
(rule 9): this is the cap for **these** runs and is not a ceiling for anything else.

**An overrun STOPS THE RUN; it does not get a new budget.** A cap is a ceiling, not a
quota: if at any checkpoint the remaining budget cannot reach `endTime`, the run is
STOPPED and reported **NOT A RESULT** rather than spent to arrive short. 3-D runs are
cap-stop exempt per Sanaa 2026-09-10, but an overrun still stops the run and is still
reported.

### Launch order and the fine-level condition, fixed NOW

Levels are built **coarse → medium → fine**, so the cheap levels land even if the
finest is held. Solves are launched **medium first**, then **coarse**, then **fine**.

> Medium before coarse is deliberate and is registered here rather than chosen later:
> Gate Y1 predicts coarse is NOT wall-function admissible (y+ 400–800) while medium is
> borderline and fine is admissible. Spending the first solve slot on the level this
> registration predicts to fail Y1 would be spending it on the least informative level.

**The fine solve launches if and only if, at the moment the fine mesh passes M1 and M2:**
(i) `free -g` reports `available` − 4 GiB **greater than** the predicted solver peak, and
(ii) 8 ranks are free without displacing another team's job.
If either fails, the fine solve is reported **PENDING** with the measured `free -g`
figure beside it — capacity exists, it is queue order, so it is not `BLOCKED`.

### Box conditions and the fleet headroom rule

Read at 00:48Z 2026-09-12: load average 55.88 on 16 cores (~3.5x oversubscribed),
`free -g` total 30, available **17**, swap 1 GiB in use, no OOM kill. Ceiling therefore
**~13 GiB** at that moment; **re-derived immediately before every launch, because
`available` moves, and the measured number is reported beside the prediction.**

Predicted peaks: coarse snappy 0.47 GiB, medium snappy 1.63 GiB, **fine snappy 8.49 GiB**
(R1 fine measured 5,900,544 KiB = 5.63 GiB, x the A1/R1 coarse layer memory factor
487,820/323,460 = 1.508). **If the fine snappy prediction exceeds `available` − 4 GiB at
launch time, the fine mesh is `BLOCKED` with the measured figure beside it. It is not
attempted and hoped for.**

**Never touched, in either direction:** ansys `rhoCentralFoam` pid 316601;
heat-transfer `buoyantBoussinesqSimpleFoam` pid 1233987 and its `splitMeshRegions`;
dafoam 8-rank A3GC; cfd MRF fine mpirun 2200471 and ranks 2200481–2200486; the
concurrent cfd SUBOFF lane.

### Rule-12 calibration

At completion of each level a row lands in `docs/COST_CALIBRATION.md` giving
actual/predicted in core-minutes, with **CPU CONTENTION ATTRIBUTED AS ITS OWN NAMED
LINE** and **never absorbed into the ratio** — a gap from contention and a gap from
misprediction are two different facts about the estimator and merging them destroys both.

---

## 5. FALSIFIERS — THREE CLASSES, EACH PARTITIONING ITS OUTCOME SPACE

> Each class below is a **partition**: the branches are mutually exclusive and jointly
> exhaustive over the space named. Naming two points inside a space is not a falsifier.

### Class 1 — HYPOTHESIS OUTCOME SPACE

**Hypothesis H(R2):** *`relativeSizes true` is the mechanism that restores wall layers on
this geometry, and it carries to every level of the graded family.*

Partition over achieved layer coverage `c` at a level, `c ∈ [0,100] ∪ {undefined}`:

| branch | c | reading |
|---|---|---|
| 1a | c ≥ 70.0 % | **PASS** — H(R2) holds at this level and the gate is met |
| 1b | 52.06 % < c < 70.0 % | **GATE FAIL** — mechanism carries *further* than at A1, still short |
| 1c | 48.06 % ≤ c ≤ 52.06 % | **GATE FAIL** — **A1 REPRODUCED** at this level |
| 1d | 40.0 % ≤ c < 48.06 % | **GATE FAIL** — mechanism carries *less* than at A1 |
| 1e | 0 % ≤ c < 40.0 % | **GATE FAIL LOW** — H(R2) does **not** carry to this level |
| 1f | undefined (no layer mesh produced) | **NOT A RESULT** — Gate M1 has already failed |

Branches 1a–1e are disjoint and cover the whole of [0,100]; 1f covers the only way `c`
can fail to exist. Across levels, the monotonicity limb (c_coarse ≤ c_medium ≤ c_fine)
is separately reported as HELD or FALSIFIED; falsification does not change any level's
own band, it is recorded as its own finding.

### Class 2 — ARTIFACT USABILITY

Partition over the state of the artifacts a gate cites:

| branch | state | reading |
|---|---|---|
| 2a | every cited artifact present and readable, **and every planted control passes** | the numbers stand |
| 2b | an artifact is present but its reader's **planted control REFUSES** — the reader cannot see a perturbation planted into that artifact on disk | **NOT A RESULT** for every number that reader produces. Nothing is degraded to "best effort"; the comparator exits 2. |
| 2c | an artifact a gate cites is **absent or unreadable** (log truncated, `polyMesh` missing, `coefficient.dat` renamed by a restart collision) | **NOT A RESULT** for the gates citing it; **BLOCKED** for the rest |
| 2d | artifacts present and readable but **proven internally inconsistent** — the index test finds an out-of-range vertex index, an unused point, or counts disagreeing with the snappy `Layer mesh` line | **NOT A RESULT** for every mesh number at that level, and **the level is not solved** |

Exhaustive: the artifact is either there and verified (2a), there but the verification
refuses (2b), not there (2c), or there and demonstrably wrong (2d).

**A zero from a reader not shown able to see a non-zero is not evidence.** Every
comparator plants a known perturbation, **reads it back FROM DISK**, and **REFUSES
(exit 2)** if the reader cannot see it. The plants are listed in §6.

### Class 3 — EXECUTION AND TERMINATION (cap exhaustion FIRST)

> This class has bitten this family twice in one evening. Partition over every way a
> launched process can end:

| branch | condition | what is reported |
|---|---|---|
| **3a CAP EXHAUSTION** | `timeout` fires; rc **124** captured **inside** the detached wrapper | `CAP_BREACH.txt` is written naming the cap, the step, the elapsed wall seconds and the core-minutes spent. The level is **NOT A RESULT** (a mesh build that did not finish; a solve that did not reach `endTime`). **The run is STOPPED and does NOT get a new budget.** The spend is reported, not absorbed. |
| **3b PRE-LAUNCH MEMORY REFUSAL** | `free -g` read immediately before launch; predicted peak > `available` − 4 GiB | **exit 3, nothing is launched.** Reported **BLOCKED** with the measured `available` and the prediction printed beside it. Not attempted and hoped for. |
| **3c NON-ZERO rc, not 124 and not 3** | any step exits non-zero | the build/solve **STOPS at that step**; step name and rc recorded in `BUILD_RC`/`RUN_META.txt`; the level is **NOT A RESULT**. **A crash is a FINDING until triage says otherwise** and is never silently retried. |
| **3d EXTERNAL TERMINATION** | wrapper started, but no `rc` sidecar **and** no `End` line (session limit, OOM kill, reboot, operator kill) | **NOT A RESULT**, reported with the last written time, the last `ExecutionTime`, and the surviving time directories named. **Never reported as a converged short run.** |
| **3e CLEAN TERMINATION** | rc = 0, `End` line present, last time == `endTime` | Gate S1 evaluates; the level proceeds to S2/S3. |

3a–3e are mutually exclusive and cover every termination: the cap fires, the launch is
refused before it starts, the process exits non-zero, it is killed from outside, or it
finishes. `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)` is the
**startup banner saying trapping is ARMED** — it appears on every healthy run and is
**not** a defect signature under any branch here.

---

## 6. INSTRUMENTS AND THEIR PLANTED CONTROLS

Grading instrument, fixed at this commit:
`cases/navier_class/DRIVAER/mesh/stage_r2_measure.py`.
The graded path is fixed here; the frozen file is verified to BE the file that ran by
hashing it against the committed blob at grading time.

Every plant operates on a **copy on disk**, is **read back from disk**, and the
instrument **exits 2** if the reader cannot see it.

| plant | what is planted | which code path it exercises | could the phenomenon arrive by another path? |
|---|---|---|---|
| **P1 checkMesh reader** | into a copy of `log.checkMeshFull`: `Failed 3 mesh checks` → `Failed 7`, and the negative-volume count 0 → 13 | the `Failed N mesh checks` regex and the negative-volume regex, the two limbs Gate M2 turns on | A zero negative-volume count could also arrive from a log that never ran the check. P1 does not distinguish those, so M1 separately asserts the checkMesh step's `rc=0` and `ALL_STEPS_OK` before M2 reads any number. |
| **P2 layer-table SCOPE plant** | two-sided, into copies of `log.snappyHexMesh`. (a) the **requested** table (`avg thickness[m]`, the FIRST table) BodyHood row is altered — the reader's y+ **MUST NOT move**. (b) the **achieved** table (`overall thickness`, target/mesh/[m]/[%], the SECOND table) BodyHood row is altered — the reader's y+ for BodyHood **MUST move**, and no other patch's may. | discriminates reading the ACHIEVED table from reading the REQUESTED table. **These two tables carry the same patch labels**, so a reader pointed at the wrong one produces plausible numbers with no other symptom. This is the scope defect the supervisor's standing condition names: the plant is into a *different table with the same label*, not a duplicate of the thing being measured. | The requested and achieved tables are the only two sources of a per-patch thickness in that log; a third path (reading the dict) is excluded because the dict carries no per-patch thickness under `relativeSizes true`. |
| **P3 mesh index reader** | into a copy of `constant/polyMesh/faces`: one vertex index → nPoints+5; and separately, one point made unreferenced | the index test of Gate M1 — out-of-range index and unused-point limbs | A splice could also present as a count mismatch with no bad index; M1 therefore ALSO cross-checks the header counts against snappy's `Layer mesh :` line, and P3 plants a count mismatch into a copy of the `owner` header as a third limb. |
| **P4 y+ / wall-distance reader** | into a copy of `constant/C`: one owner cell centre displaced by a known 0.00137 m along the wall normal | the owner-cell-centre → boundary-face-centre distance, per face, and the area-weighted median over the layered group | The median could also move because the *face* changed group; P4 therefore asserts the displaced face's y+ moves by exactly the planted amount **and** that the layered/unlayered face partition is unchanged. |
| **P5 Cd window reader** | into a copy of `coefficient.dat`: a known offset added to Cd over the second half of the window | the S2 half-to-half drift limb and the S3 window mean | A drift could also arrive from a restart collision renaming `coefficient.dat` (a known trap); S1 separately asserts a single unbroken `coefficient.dat` covering 1..endTime, and the reader refuses if the time column has a gap or a repeat. |

**`medialAxisMeshMover` walks the whole adapt-patch point set and has no notion of solid
names.** Every layer measurement here is therefore scoped **the way the solver scopes its
own computation** — over the mesh's boundary patches as `constant/polyMesh/boundary`
defines them — and **not** the way the STL's solids or the dict's `layers{}` block are
organised.

---

## 7. WHAT IS NOT IN THIS REGISTRATION

* The residual wheel/underbody group (E4). **Not reopened. No sixth diagnostic arm.**
  Its non-layered patches are DISCLOSED under Gate Y2 and carried as a stated limitation.
* `CTRL_SURFACE_Outlet` / `Mirrors2` (E6). **Noted if they reappear; no hypothesis.**
* The symmetry-plane alarm (E5). **Withdrawn and not resurrected.**
* Any grid-convergence claim (Gate G). **Forbidden.**
* Any claim of agreement with DrivAerML (Gate S3). **Forbidden.**

---

## 8. FREEZE

Every gate, threshold, band, label and cap above is fixed at the commit that lands this
file. After the first `snappyHexMesh` of `r2_coarse` starts, changes land only as dated
addenda that cannot alter a gate, a threshold, a cap or a label. Originals are struck,
never rewritten.
