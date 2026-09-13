# DRIVAER R5 — WALL-FUNCTION RANS, 15–20 M CELLS, ABSOLUTE LAYERS, y⁺ 30–100

**Status: FROZEN 2026-09-13 by cfd-supervisor. THIS COMMIT IS THE FREEZE** and discharges
standing check 4. Gates, thresholds, cap and labels below are closed as of this commit; changes
land only as dated addenda that cannot alter them. No compute has run against this document:
verified at the run root /home/ubuntu/certonomous-runs/, which holds no R5 directory while the
same listing returns the directories that do exist.

**The superseded status line read: "DRAFT. NOT FROZEN. NO COMPUTE HAS RUN, NOTHING IS ARMED, NO
QUEUE ENTRY PLACED."** It is struck, not rewritten, and recorded here because three documents
were frozen earlier today whose status lines still said DRAFT.
Rung id `R5`. Drafted 2026-09-13 by a cfd `lab-lane` on the cfd-supervisor's instruction.
**The rule-2 freeze check is the supervisor's personally and is not delegated to this lane.**

**SUPERSEDES** `DRIVAER_R4L_BLENDED_ON_LAYERFIXED_MESH_PREREGISTRATION_DRAFT.md` (never frozen,
never run, no queue entry). R4L's §1 source findings on the installed build are carried forward
into §2 here; its gate structure is withdrawn. **Nothing is edited in R4L — it stays on disk as
the superseded draft** (rule 6: frozen files are never edited; R4L was never frozen, and is left
intact regardless).

---

## 1. THE SPECIFICATION, AS RELAYED

Relayed to this lane by the cfd-supervisor as Sanaa's own specification. **Recorded as RELAYED,
NOT DIRECTLY OBSERVED BY THIS LANE** — this lane did not receive it from Sanaa and no agent's
message is her consent (rule 9).

| item | specification |
|---|---|
| closure | **wall-function RANS** (wall-resolved recipe deferred) |
| mesh | **15–20 M cells** |
| layers | **tonight's layer fix, ABSOLUTE SIZES, 8 LAYERS** |
| y⁺ | **30–100** |
| schedule | **2,000 steady + 1,000 averaged iterations** |
| band | **AutoCFD RANS scatter** |
| prediction | **Cd within 10 % of the reference** |
| cost | **≈ 50,000 core-min** |

---

## 2. THE SOURCE RECIPE — **VERIFIED BY THIS LANE FROM THE PAPER, NOT TAKEN ON RELAY**

The layer recipe was relayed to this lane. **This lane did not accept it on relay.** It was read
back from the text sidecar
`/home/ubuntu/certonomous-runs/reference_pdfs/benchmark_test_cases/ashton_2024_drivaerml.txt`,
the title-page-verified DrivAerML paper (arXiv:2408.11969v2), at the line numbers given below.
**Every relayed figure reproduced.**

| row | verbatim source | sidecar line |
|---|---|---|
| mesh size & tool | "Approximately 160 million cells" in "ANSA version 24.1.0 using the HeXtreme algorithm" | 269–271 |
| **the layer recipe** | "The boundary layer mesh was optimised for wall functions, with **7 layers, a first layer height of 0.75 mm, a total layer height of 12 mm and a variable growth rate between 1.2 and 1.4**" | **271–273** |
| why high-y⁺ | "The choice of high y⁺ mesh vs. resolving to the wall was based on findings from the 2nd AutoCFD workshop, where direct comparisons by multiple participants found **only a minor difference in results**" | 274–276 |
| **no grid study** | "**refinement study is not undertaken**" | **280** |
| wall model | "formulation based on **Spalding's law of the wall** [22] is used that is **valid for arbitrary values of** [y⁺]" | 1385 |
| cost | "A typical simulation took around **40 hours on 1536 cores** using Amazon EC2 hpc6a.48xlarge" | 326–327 |
| statistical target | "Target statistical accuracy of **±1.5 drag counts** is achieved" | 320 |
| **vs experiment** | CFD **0.274 / 0.267** against Ford experiment **0.255 / 0.242**; "higher than experiment by roughly **20 counts** in both simulations" | 1857–1858, 1887–1888, 1923 |

### 2.1 🔴 THE DIAGNOSIS THIS REVERSES — OUR WALL TREATMENT IS ALREADY THE PUBLISHED ONE

R4L's draft treated the wall treatment as the open question. **It is not.** The source uses a
Spalding-law formulation valid for arbitrary y⁺ (line 1385) — that is
`nutUSpaldingWallFunction`, **which this lab already runs on every DrivAer vehicle patch**, and
their boundary layer was *"optimised for wall functions"* deliberately, on AutoCFD evidence that
wall-resolved buys little.

**The defect is therefore NOT the wall model. It is the first-cell height** — a layer-thickness
defect that presents as a y⁺ defect. **R4L's gate structure is withdrawn for this reason**, and
the R2c measurement that gate B2 read `INACTIVE` (134× below threshold) is now *explained* rather
than merely recorded: the wall function was never the free variable.

### 2.2 THE MECHANISM, IN OUR OWN DICTIONARY — **RELATIVE SIZING IS THE DEFECT**

Read from `verification/runs/navier_class/DRIVAER/r2_coarse/system/snappyHexMeshDict`:

```
relativeSizes       true;
finalLayerThickness 0.5;
expansionRatio      1.25;
minThickness        0.02;
```

With `relativeSizes true` and `finalLayerThickness 0.5`, the **requested** stack for 5 layers at
r = 1.25 is, in units of the local surface cell `c`:

`0.5c + 0.4c + 0.32c + 0.256c + 0.2048c = **1.6808 c**`, first layer **0.2048 c**.

**Against the source's 12 mm stack on our 25.0 mm level-4 (medium) surface cell — 0.48 c — we ask
for 3.50× more stack than the recipe that works.** Their request extrudes because it asks for
under half a cell; ours collapses because it asks for more than one and a half.

**And it is a function of refinement level, which theirs is not.** `relativeSizes true` scales
every thickness by the local cell, so a level-5 patch silently halves our first layer while the
source's 0.75 mm stays 0.75 mm everywhere. **Absolute metres sidesteps the mechanism entirely.**
This is the PPTC lesson carried across.

🔴 **THE COUPLED TRAP, REGISTERED BEFORE THE EDIT (PPTC PRISM-A2).** `minThickness` is **in the
same units as the sizing switch**. Our current `minThickness 0.02` means *0.02 × local cell*.
Flipping `relativeSizes` to `false` without converting it makes it mean **0.02 metres = 20 mm**,
which **exceeds the entire new stack (§4: 11.86 mm) and would refuse every layer on every patch**
— a clean-exiting mesh with zero layers. **`minThickness` MUST convert in the same edit.**
Registered value: **`minThickness 0.0002`** (0.2 mm = 20 % of the first layer).

### 2.3 THREE CAVEATS ON THE SOURCE ITSELF, CARRIED INTO EVERY DOWNSTREAM CLAIM

1. **The dataset's shipped `run_0` case directories are a mesh-delivery stub, not the production
   setup** — `application UserSolver`, `ddtSchemes steadyState`, `momentumTransport laminar`,
   empty `forceCoeffs` patches with `magUInf 40` and `lRef 1` **contradicting the paper's own
   38.889 and 2.78618**, and no `0/nut`. The production numerics are proprietary and unpublished.
   **No dictionary value may be read out of those files by anyone.** *(Relayed by a sibling lane;
   not independently re-opened by this lane, and labelled accordingly.)*
2. **"A grid refinement study is not undertaken" — their own words, line 280.** This recipe
   carries **no grid-convergence evidence** and must never be cited as if it did.
3. **Their own solve is ~20 drag counts high on experiment** (0.274 vs 0.255; 0.267 vs 0.242).
   **That is the published state of the art for this case**, and §7 gates against it honestly.

### 2.4 TWO NUMBERS THAT ARE **DERIVED**, NOT PUBLISHED — LABELLED SO THEY CANNOT BE MISREAD

- **The source's y⁺ ≈ 22 is LAB-DERIVED**, by linear scaling from our measured median 153.1 at
  our 5.12 mm first layer. **The paper publishes no y⁺ value.**
- **The source's achieved layer coverage is NOT REPORTED.** ANSA HeXtreme writes no
  post-extrusion table, so **there is no published counterpart to our 2.50 / 2.89** (§5).
  **Absence of a reported failure is not evidence of success**, in their mesh or ours.

Also carried: the source meshes with **ANSA HeXtreme, not snappyHexMesh** (`snappy`: 0
occurrences). **The VALUES transfer; the TOOLING does not.**

---

## 3. THE ONE REGISTERED CHANGE

**The mesh.** Specifically: absolute layer sizing at 8 layers on a 15–20 M-cell mesh, replacing
relative sizing at 5 layers on a 0.98 M-cell mesh.

**HELD CONSTANT, and this is what makes the arm readable:** the wall treatment
(`nutUSpaldingWallFunction` on the `".*"` vehicle block, `nutkWallFunction` on `floorNoSlip`),
`k`/`omega` wall functions, the turbulence model, schemes, relaxation, the reference quantities,
the forceCoeffs patch list, and the solver (`simpleFoam`). Proven at stage time by `diff` into
`THE_ONE_CHANGE.diff` in each run root.

**The averaging phase (§6) is NOT a second change**: it is a function object writing a derived
quantity, it alters no equation, no boundary condition and no discretisation, and the steady
solve it averages is the same solve. **Stated explicitly so it cannot be read as a bundle later.**

---

## 4. THE LAYER RECIPE — DERIVED, AND 🔴 IT EXPOSES A CONFLICT IN THE SPECIFICATION

### 4.1 The y⁺ arithmetic

y⁺ ∝ first-cell height at fixed `u_tau`. Anchor: **medium's measured area-weighted median y⁺ =
153.1** at a first layer of **0.2048 × 25.0 mm = 5.12 mm**.

| target y⁺ | required first layer |
|---|---|
| 30 (window floor) | **1.003 mm** |
| 100 (window ceiling) | **3.344 mm** |
| *(source's 0.75 mm)* | *(y⁺ ≈ 22.4 — **below Sanaa's window**)* |

🔴 **THE PUBLISHED RECIPE WOULD LAND BELOW THE SPECIFIED WINDOW.** Copying the source's 0.75 mm
gives y⁺ ≈ 22, outside 30–100. **The first layer is therefore set from Sanaa's y⁺ window, not
from the source**, and the divergence is stated here rather than split silently.

### 4.2 🔴 THE CONFLICT: **8 LAYERS, y⁺ ≥ 30 AND A REFINED SURFACE CELL ARE NOT JOINTLY SATISFIABLE**

For 8 layers the stack is `t1 × (r⁸−1)/(r−1)`, and the minimum possible multiplier is **8** (at
r → 1). Extrusion requires the stack to stay under roughly **0.48 c** — the ratio the source's
working recipe exhibits and the ratio ours (1.6808 c) violates.

**If the surface cell is refined to 12.5 mm** (the obvious route to 15–20 M cells), the stack
ceiling is 0.48 × 12.5 = **6.0 mm**, so `t1 ≤ 6.0/8 = 0.75 mm`, giving **y⁺ ≤ 22.4**.
**Sanaa's floor of 30 is unreachable.** The three requirements are mutually exclusive.

**THE RESOLUTION, REGISTERED RATHER THAN DISCOVERED LATER: the surface cell must STAY at 25 mm
(level 4), and the 15–20 M cells must come from VOLUME refinement, not surface refinement.** This
is not a workaround — **it is exactly what the source did**: *"refined using size fields that
follow the geometry and extend downstream"* (lines 276–278). At c = 25 mm the stack ceiling is
**12.0 mm**, and the recipe closes:

| entry | registered value |
|---|---|
| `relativeSizes` | **`false`** |
| `nSurfaceLayers` | **8** *(Sanaa's instruction; the source says **7** — divergence registered, not split)* |
| `firstLayerThickness` | **0.0010 m** |
| `expansionRatio` | **1.11** |
| `minThickness` | **0.0002 m** *(converted in the same edit — §2.2)* |
| resulting stack | 1.0 × (1.11⁸−1)/0.11 = **11.86 mm = 0.474 c** — inside 0.48 |
| **predicted y⁺** | **≈ 30** |

**THE WINDOW HAS NO SLACK AND THIS DOCUMENT SAYS SO.** The recipe sits at the **bottom edge** of
y⁺ 30–100 because the extrusion constraint puts it there. **There is no version of this arm with
8 layers that sits comfortably mid-window.** If the supervisor prefers margin, the lever is
**fewer layers**, not a thinner first cell.

**HONEST CAVEAT ON THE SCALING:** y⁺ ∝ `t1` holds at fixed `u_tau`. The new mesh is ~18× the
medium's cell count, and better-resolved separation can move `u_tau` locally. **The scaling is a
first-order prediction, not a guarantee**, which is precisely why §7's y⁺ gate is a *gate* and
§8's prediction is *falsifiable*.

---

## 5. ACHIEVED COVERAGE — **THE REQUEST TABLE IS NOT EVIDENCE (L-590)**

**8 layers is nearly double our 5, and we do not currently deliver 5.** This gate is registered
on **achievement**, never on request.

### 5.1 What we actually achieve, by L-590's three independent readings, which must AGREE

Read by this lane from each level's own `log.snappyHexMesh`:

| reading | `r2_coarse` | `r2_medium` |
|---|---|---|
| (1) last `Extruding N out of M faces` | 16,887 / 23,365 = **72.27 %** | 64,470 / 80,974 = **79.62 %** |
| (2) last `Added X out of Y cells` | 58,479 / 116,825 = **50.06 %** | 234,448 / 404,870 = **57.91 %** |
| (3) cell delta, snapped → layers | 186,709 − 128,230 = **58,479** | 983,106 − 748,658 = **234,448** |
| **(2) and (3) agree exactly** | ✅ | ✅ |
| **achieved layers = added cells / extrudable faces** | **2.503 of 5** | **2.895 of 5** |

**All three readings agree, so the layers on DrivAer are REAL** — this is not the blades case
where the delta was zero. **What is real is 2.50 and 2.89 of a requested 5.**

### 5.2 🔴 A RECONCILIATION THIS LANE OWED, BECAUSE ITS OWN EARLIER FIGURE DIFFERED

An earlier figure from this lane read **1.850 of 5** on coarse, against the 2.503 above. **Both
are correct and they count different populations**, which is worth more than either alone:

- **2.503** is **global**, including `floorNoSlip` — 5,505 of 23,365 extrudable faces at **4.62**
  layers, the single best-covered patch in the mesh.
- **1.850** is **vehicle patches only**, `floorNoSlip` excluded, face-weighted from the per-patch
  table.
- Check: `(1.850 × 17,860 + 4.62 × 5,505) / 23,365 = **2.5026**` against the global **2.5029**.
  **They reconcile to four significant figures.**

**THE DISTINCTION IS LOAD-BEARING, NOT PEDANTRY.** `floorNoSlip` is the ground plane. It carries
**no vehicle force**, contributes nothing to Cd, and it is the patch that flatters the global
average by 35 %. **The gate below is therefore set on vehicle patches only**, because the car is
what the drag comes from.

### 5.3 Gate L — **ACHIEVED** layer coverage

**L1: achieved layers on vehicle patches ≥ 5.0 of the 8 requested (62.5 %)**, computed as
`added cells attributable to vehicle patches / extrudable vehicle faces`, cross-checked against
the per-patch post-extrusion table and against the cell delta. **A disagreement between the three
readings is a REFUSAL, not an average.**

**L2: ≥ 90 % of vehicle faces extruded** (currently 72.27 % globally).

**Derivation of 5.0:** the current mesh achieves 1.850 of 5 on vehicle patches = 37.0 %. Absolute
sizing removes the level-coupling and cuts the requested stack from 1.6808 c to 0.474 c — a
**3.55× lighter ask**. **If the ask being too large is the mechanism (§2.2), coverage must rise
substantially or the mechanism is wrong.** 5.0 of 8 is 62.5 %, a 1.69× improvement on 37.0 %,
and is deliberately set **below** what the mechanism predicts so that the gate tests the
mechanism rather than flattering it.

**L1 FAIL ⇒ the mesh is not fit for the arm and NO SOLVE IS LAUNCHED.** The cost in §9 is not
spent. A refusal here is the gate working.

---

## 6. THE AVERAGING, DEFINED BEFORE IT RUNS

**An averaging window chosen after seeing the trace is exactly what pre-registration exists to
prevent.** All four answers are fixed here.

1. **What is averaged.** `Cd` and `Cl` from `forceCoeffs`, and the fields `U`, `p` for the
   render. The **graded quantity is the arithmetic mean of the per-iteration `Cd`** over the
   averaging window, read by the frozen grader's own `read_coeff`.
2. **Which window.** Iterations **2001–3000 inclusive**, exactly 1,000 samples. **Fixed by
   schedule, not by a data-dependent trigger.**
3. **Stationarity criterion for entering the averaged phase.** 🔴 **THERE IS NONE, AND THAT IS
   DELIBERATE.** The averaged phase begins **unconditionally at iteration 2001**. A
   stationarity *trigger* would let the run choose its own window from the trace — the precise
   defect this section exists to prevent. **Stationarity is REPORTED, never used to select.**
4. **What is reported beside the mean, mandatorily.** The window's standard deviation; the
   trailing-200 excursion at 3000; the sign-reversal rate over the last 400 samples; and the
   drift across **eight window lengths**. **A mean without these is an incomplete reading**, and
   the parking record's finding stands: every graded DrivAer `Cd` so far was `NOT_PLATEAUED`, and
   R3's excursion ranked at the *median* of its own distribution after 10,000 iterations.

🔴 **WHAT AVERAGING DOES AND DOES NOT FIX.** A time-average of a **steady SIMPLE** iteration
sequence is **not** a time-average of an unsteady flow — the iteration index is not time. **It
reduces the arbitrariness of quoting the last sample of a wandering series. It does not make a
non-converged steady solve converged, and the run is NOT exempt from rule 4 or rule 5 limb 1
because it was averaged.** The parking record's named successor for the physics remains an
unsteady treatment; this arm does not claim to be one.

---

## 7. GATES

| gate | statement | threshold |
|---|---|---|
| **M1** cell count | achieved cells within the specified range | **15–20 M**, reported as achieved, not as targeted |
| **L1** achieved layers (vehicle) | §5.3 | **≥ 5.0 of 8** |
| **L2** extruded fraction (vehicle) | §5.3 | **≥ 90 %** |
| **Y1** achieved y⁺ | area-weighted median over the 47 vehicle patches, **solved**, via `simpleFoam -postProcess -func yPlus` | **30 ≤ median ≤ 100** |
| **C1** completion | rule 4, all clauses, at `endTime` 3000 | all or nothing |
| **C2 (PRIMARY)** Cd agreement | `|Cd_avg − 0.2758368| ≤ 0.10 × 0.2758368` | **[0.24825, 0.30342]** |
| **S1** mesh conformance | `checkMesh -allGeometry -allTopology` max skewness | **< 4.0** (`docs/standards/MESH_STANDARD.md` hard gate) |

**Y1 IS A GATE, NOT A DIAGNOSTIC, AND ITS FAILURE MODE IS REGISTERED NOW.** On current evidence
it may miss: 0 of 47 vehicle patches is presently below y⁺ 30, and §4.2 places the recipe at the
window's bottom edge with no slack. **If achieved y⁺ falls below 30, the arm is reported as
`GATE FAIL` on Y1 and the Cd is reported beside it with the y⁺ miss stated — it is NOT
re-registered to a wider window.** If achieved y⁺ exceeds 100, the same. **The window is Sanaa's
and this lane does not move it.**

🔴 **S1 AND THE CLAIM CAP.** Every DrivAer mesh built so far fails S1 — nine arms, best 4.782
against the gate of 4.0, and the skew-limiting faces were measured to be **outside the layer
region**, so an absolute-sizing layer change is **not expected to fix it**. **If S1 fails, R5
inherits the CLAIM CAP in full: `credential_eligible: false`, matrix status STATED LIMITATION,
never a credential, whatever C2 says.** A Cd inside the band on a non-conforming mesh is not a
validated Cd, and §8's prediction is registered in that knowledge.

### 7.1 🔴 THE BAND — **"AutoCFD RANS SCATTER" COULD NOT BE SOURCED AND IS NOT INVENTED**

The specification names the band as **AutoCFD RANS scatter**. **This lane searched and could not
source a numerical scatter band.** The DrivAerML paper references the AutoCFD workshops (lines
121, 213, 274, 278, 360, and `autocfd.org` at 238) and states its results agree with the "CFD
consensus", **but publishes no scatter band**; the repository's only AutoCFD mention is a
forward-looking rung name in `DRIVAER_R1_notchback_cd.md:21`.

**Registering a number I cannot cite would be the worst thing in this document.** Therefore:

- **The registered band for C2 is ±10 % of the DrivAerML reference Cd 0.2758368 → [0.24825,
  0.30342]**, which is Sanaa's own stated prediction and is fully sourced.
- **An AutoCFD scatter band may be ADDED before the freeze if, and only if, a citable source
  lands.** After the freeze it cannot be added at all (rule 2). **It is not a fallback and not a
  second chance**: if both bands end up registered, C2 is graded against **both**, reported
  separately, and the ±10 % band governs.

### 7.2 THE DISAVOWAL, MANDATORY ON ANY C2 PASS

`Cd_ref = 0.2758368` is **DrivAerML run_466, a CODE reference of rank 2 — hybrid RANS-LES CFD,
NOT experiment.** Its own basis pairing is load-bearing (per-geometry `Aref` 2.298, **not** the
nominal 2.17; the two differ by 5.57 % in Cd and must never be mixed). **And the source's own
solve is ~20 drag counts high on Ford's experiment (§2, line 1923).** So a C2 PASS means *"inside
10 % of a CFD reference that is itself 20 counts high on experiment"* — **it does not mean
agreement with experiment, and any record quoting C2 must carry this sentence.**

---

## 8. FALSIFIABLE PREDICTIONS, WITH NUMBERS, BEFORE THE MESH IS BUILT

**P1 — coverage.** Absolute sizing at 0.474 c will raise achieved vehicle-patch coverage from
**1.850 of 5 (37.0 %)** to **≥ 5.0 of 8 (62.5 %)**, and extruded fraction from 72.27 % to
**≥ 90 %**. *Falsified if achieved vehicle coverage is below 5.0 of 8* — which would mean the
requested-stack-too-large mechanism (§2.2) is **not** what limits our layers, and the defect is
in snapping, as the parking record's skewness evidence already suggests for a different metric.

**P2 — y⁺.** The achieved area-weighted median vehicle y⁺ will land in **[30, 45]** — the bottom
third of Sanaa's window, because §4.2's recipe is pinned to the window floor by the extrusion
constraint. *Falsified if the median lands above 45 or below 30.*

**P3 — Cd.** `Cd_avg` over iterations 2001–3000 will land in **[0.24825, 0.30342]** (C2 PASS).
**Confidence stated honestly: this is the weakest of the three.** Our last three graded runs
returned Cd ≈ 0.315 and 0.355, i.e. **0.315 is already inside the band and 0.355 is outside it**,
and the band is 10 % wide on a quantity our own solves have moved by 12 % between meshes. **A
PASS here is therefore weak evidence and is registered as such in advance**, which is why S1 and
Y1 are gates rather than notes.

**P4 — the one this lane most expects to fire.** **S1 will FAIL**: max skewness will remain above
4.0, because three genuinely different layer specifications previously moved it **not at all**
(4.7820293, bit-identical to eight significant figures), placing the skew-limiting faces outside
the layer region. *Falsified if max skewness < 4.0 on the new mesh* — which would be the single
best outcome available from this arm and would **lift the CLAIM CAP for the first time in this
campaign.**

---

## 9. COST — **BOTH BASES REGISTERED, THE PREDICTION SET AGAINST THE LARGER**

🔴 **THE RELAYED ~50,000 core-min AND OUR MEASURED RATE DISAGREE BY 7×, AND BOTH MAY BE RIGHT.
THIS SECTION RESOLVES IT RATHER THAN PAPERING OVER IT.**

**Basis A — MEASURED, this box.** `DRIVAER-RATE-PROBE-96C`, graded against a registration frozen
at `ab52c0a03` **before** the run: **7.9268e-06 core-s per cell-iteration** on the 96-core box
(median 0.3700 wall s/iteration, n = 99, `exe/clk` = 1.0009, contention clean). That is
**0.13211 core-min per iteration per Mcell**. *(Relayed as 0.13342; this lane's own derivation
from the filed probe gives 0.13211 — a 1 % difference, recorded rather than smoothed.)*

At **17.5 Mcell × 3,000 iterations**: **6,936 core-min.**

**Basis B — DERIVED FROM PUBLISHED PRACTICE.** The source's own run is **1,536 cores × 40 h =
61,440 core-hours** at 160 M cells (lines 326–327). A sibling lane's comparison puts our probe at
**0.43×** the published figure for the same work, i.e. **our probe under-predicts by 2.30×**.
*(This lane verified the 61,440 from the paper; the 26,684-core-hour counterpart and the 2.30×
ratio are the sibling lane's derivation and are labelled as such.)* An earlier independent
comparison against published STAR-CCM+ work put us **4.8×** cheaper per cell-iteration and
**flagged our rate as the optimistic end**.

| basis | core-min | derived $ | status |
|---|---:|---:|---|
| A — our probe, measured on this box | **6,936** | $5.93 | **MEASURED basis**, steady `simpleFoam` |
| A × 2.30 (HRLES-derived correction) | 15,953 | $13.64 | derived |
| A × 4.8 (STAR-CCM+-derived) | 33,293 | $28.46 | derived |
| **Sanaa's figure** | **≈ 50,000** | **$42.75** | **the registered prediction** |

**WHY THE GAP IS REAL AND NOT AN ERROR.** Our probe is calibrated for **steady `simpleFoam`** and
the published figure is **transient hybrid RANS-LES at 160 M cells** — it is being asked about
different work. **Our figure is the optimistic end of our own hardware; hers is consistent with
published practice.** For the second time tonight the lab's own rate has come in optimistic
against a published cross-check.

**THE PREDICTION IS REGISTERED AT 50,000 core-min = $42.75.** **A prediction set from the
optimistic rate is one that fires on the first honest run.** Dollars are **DERIVED, NOT MEASURED**
at the owner-stated **$0.0513/core-h**; this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5).

**NO CAP STOPS THIS RUN** — Sanaa's directive #17, 2026-09-12. The figure is a **rule-12
prediction scored at completion**, not a kill. **The $42.75 exceeds the $25 pre-authorisation
band; larger CPU runs are approved under the 2026-08-21 blanket, and the run is costed here
regardless — a blanket is not a per-item read (rule 9).** Mesh cost is additional and unmeasured
until the build runs; **a row is owed to `docs/COST_CALIBRATION.md`** at landing, stating
actual/predicted against **50,000**, with the gap attributed and waste named separately.

---

## 10. WHAT THIS LANE COULD NOT VERIFY

1. **The AutoCFD RANS scatter band** — searched, not found, **not invented** (§7.1).
2. **The `run_0` stub finding** — relayed by a sibling lane; this lane did not re-open those
   dictionaries.
3. **The 26,684-core-hour probe counterpart and the 2.30× ratio** — a sibling lane's derivation.
   **This lane independently verified the published 1,536 cores × 40 h.**
4. **Whether `u_tau` holds under an 18× cell-count increase**, on which §4's y⁺ scaling rests.
5. **The source's achieved layer coverage** — not reported by their tool, so their recipe's
   *delivery* is unverifiable; only its *request* is published (§2.4).
6. **Whether Sanaa's ≈50,000 core-min was for this arm's size** — it is used as the registered
   prediction because it is the conservative figure, not because its basis was stated.

---

*Drafted by a cfd `lab-lane`, 2026-09-13. **DRAFT — NOT FROZEN, NOT COMMITTED BY ITS AUTHOR,
NOTHING ARMED, NO QUEUE ENTRY PLACED.** The rule-2 pre-registration check is the cfd-supervisor's
personally. Contains no submission, no external communication and no claim outside this box.*

# ADDENDUM A1 — DATED DISCLOSURE — 2026-09-13

**DRAFT, HANDED TO cfd-supervisor FOR LANDING. NOT APPLIED BY THIS LANE.**
This lane's brief forbids it editing frozen files (CLAUDE.md rule 6), so the
text below is delivered as a file under the run directory it concerns and is
**not** appended to the registration by its author. Landing it is the
supervisor's act.

**Target document:** `verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md`
**Frozen at:** `38aab8e78662d574d1b14b61da7efc5898be5c7e`
**Blob at freeze and at HEAD when this was drafted:** `8f0083d195d8bf03c1afa8f87e683c4b4d5a8fcc` (identical)
**Target document length at drafting:** 438 lines.

**On landing, this section is appended AT THE FOOT and the lander asserts:
`lines whose number changed above this section: 0`, verified by
`cmp -n <original byte length>` between the pre- and post-append files.**

---

## WHAT THIS ADDENDUM DOES AND DOES NOT DO

**It alters NO gate, NO threshold, NO cap and NO label.** L1 stays at ≥ 5.0 of
8 on vehicle patches. L2 stays at ≥ 90 %. M1 stays at 15–20 M. S1 stays at
4.0. P1–P4 stand exactly as frozen. First compute against R5 began at
2026-09-13T18:05:35Z, so the gates are closed and nothing here reopens them.

**What it discloses is an UNPRICED CONDITION** — a fact about the mesh the
registration builds on that the registration did not account for, found before
the graded mesh existed and recorded so that the P1 reading is not quoted as
something it is not.

---

## A1.1 — THIRTEEN VEHICLE PATCHES ARE ALREADY AT SURFACE LEVEL 5 = 12.5 mm

The dictionary R5 inherits — `r2_medium/system/snappyHexMeshDict`, whose
`refinementSurfaces` block R5 leaves **byte-identical** — sets thirteen vehicle
patches to `level (5 5)`:

`BodyDoorhandles`, `BodyHeadlamps`, `BodyRocker`, `ClosedGrillLowerInsert`,
`ClosedGrillUpperInsert`, `ExhaustSystem1`, `ExhaustSystem2`, `ExhaustSystem3`,
`Mirrors1`, `Mirrors2`, `TirePlinthfront`, `TirePlinthrear`.

At the R5 background of `h0 = 0.4 m`, level 5 is a **12.5 mm** surface cell.

**On a 12.5 mm cell the registered 11.859 mm stack is 0.949 local cells —
double the 0.48 ceiling §4.2 itself declares necessary for extrusion.**

The affected population is **10,162 of 64,595 vehicle faces = 15.7 %**
(face counts measured from `r2_medium`'s own post-extrusion table via
`cases/navier_class/DRIVAER/mesh/analyse_layers.py`; the remaining 54,433
faces = 84.3 % are at level 4 = 25.0 mm, where the stack is 0.474 c and the
§4.2 constraint is satisfied).

**§4.2 resolved "do not refine the surface further" and did not notice that
part of the surface is already refined.** That is the honest description of how
the gap got there: **a constraint written against the intended mesh rather than
against the actual dictionary.** It is the same shape as the PRISM-A2 defect
one case over.

## A1.2 — WHY THIS CHANGES HOW P1 MUST BE READ, WITHOUT CHANGING P1

If the 84.3 % at 25 mm reach ~6 layers and the 15.7 % at 12.5 mm reach ~0, the
face-weighted result is

    (6 × 54,433 + 0 × 10,162) / 64,595 = 5.06

against a threshold of **5.0**. **P1 would be decided at the third significant
figure by a condition the registration never priced.**

**A gate decided in its third digit by an unpriced condition is not a gate
anybody should quote. A P1 PASS near 5.0 is therefore UNINFORMATIVE and must
not be reported as evidence that the mechanism of §2.2 was confirmed.**

**THE RESULT IS THE TWO POPULATIONS REPORTED SEPARATELY, EACH WITH ITS FACE
COUNT — coverage on the 54,433 faces at 25 mm, and coverage on the 10,162
faces at 12.5 mm. The blended figure is an artefact of mixing two different
geometric situations and is reported only because the frozen gate is defined
on it.**

## A1.3 — THE BUILD IS PARALLEL WHERE THE FAMILY WAS SERIAL

R5 is built with `mpirun -np 16 snappyHexMesh -parallel`. Every graded mesh in
the R1/R2 family was built **serial**. This is not registered either way.

**It is a live confound on exactly the quantity P1 measures:** parallel snappy
can move layer insertion at processor boundaries, and this act has already
observed parallel snappy rebalance at every feature iteration. Recorded in
`r5_wallfunction/RUN_PIN.txt` and here.

## A1.4 — TWO BUILD CONDITIONS, ONE OF WHICH WOULD HAVE DEFEATED M1

1. **`maxLocalCells` was 6,000,000.** In a serial build that is the binding
   cap and it makes the registered 15–20 M gate **unreachable**. Raised to
   40,000,000 to match `maxGlobalCells`. Disclosed as an enabling limit, not a
   physics change.

2. **The first sizing model was wrong and a castellation-only probe refuted
   it.** `R5_SIZING_PROBE` (castellation only, 16 ranks) returned
   **12,541,747 cells** against a 12.96 M estimate — 3.3 % high, tolerable —
   but it killed the layer-gain assumption. The original sizing carried
   `r2_medium`'s **+31 %** layer gain. Measured on that level's own log,
   **snapping adds ZERO cells (748,658 → 748,658 — it moves points, it does
   not add cells)**, and R5's **surface** refinement is identical to medium's,
   so its wall-face count is too (~80,974 extrudable faces). Layers therefore
   add `faces × extruded_fraction × 8 ≈ 0.58 M` cells — **+4.7 %, not +31 %**.
   The final mesh would have landed at **~13.1 M and MISSED M1 LOW**. The
   volume-refinement box was rescaled from the measured point rather than the
   assumed one; predicted final ~16.9 M.

   **The volume-refinement geometry is authored by the building lane.** The
   registration sets the 15–20 M gate and mandates that the cells come from
   volume refinement, but specifies no geometry. The boxes are recorded in
   `cases/navier_class/DRIVAER/mesh/make_r5_dict.py` and the emitted dict's
   sha256 is pinned in `r5_wallfunction/RUN_PIN.txt`.

## A1.5 — WHAT THE SURFACE LEVELS DID NOT DO

**They did not move.** `refinementSurfaces`, `features`, `snapControls` and
`meshQualityControls` are asserted **byte-identical** to `r2_medium`'s by
`make_r5_dict.py`, which exits 2 if any of them differs. §4.2 forbids touching
surface refinement, and **an arm that changes the mesh *and* the layer spec
measures neither.**

---

*Drafted by a cfd `lab-lane`, 2026-09-13, at the direction of the drafting
lane, for the cfd-supervisor to land. Alters no gate, threshold, cap or label.
Contains no submission and no external communication. Nothing leaves the box.*

---

## ADDENDUM A1 — CORRECTION 1 (2026-09-13, cfd-supervisor)

**Version 1.2. Lines whose number changed above this section: 0.** This correction
alters no gate, threshold, cap or label.

**A1 SAYS THIRTEEN PATCHES. THE CORRECT FIGURES ARE TWELVE CONFIGURED AND TEN
CARRYING FACES.** `TirePlinthfront` and `TirePlinthrear` are configured at surface
level 5 but hold **ZERO faces in the mesh**, so they cannot move any coverage figure.

**The ten face-carrying patches are:** `BodyDoorhandles`, `BodyHeadlamps`,
`BodyRocker`, `ClosedGrillLowerInsert`, `ClosedGrillUpperInsert`, `ExhaustSystem1`,
`ExhaustSystem2`, `ExhaustSystem3`, `Mirrors1`, `Mirrors2`.

**EVERY MEASURED QUANTITY IN A1 IS UNCHANGED AND NO RULING DEPENDS ON THE COUNT:**
10,162 of 64,595 vehicle faces = **15.7 %**; stack **0.9488 local cells** against the
**0.48** ceiling; and the **5.06 against 5.0** arithmetic. A1's conclusion — that a P1
PASS near 5.0 is uninformative and the two populations must be reported separately —
stands entirely.

**HOW THE ERROR AROSE, recorded because it is the same shape as the night's other
findings:** the count was taken **by eye off the dictionary** rather than derived from
the dictionary and **intersected with the faces that actually exist**. A configured
patch and a patch with faces are different sets, and only the second can affect a
face-weighted average. **A number read off a configuration is a statement about the
configuration, not about the mesh.**

**Provenance of the correction:** raised by the building lane against its own figure,
unprompted, before the graded coverage was read. The erroneous count also appears in
commits `1bb18559`, `277b9edf` and in this supervisor's commit message at `627eb624`,
**none of which can be edited**; this section is the correction of record for all four.
