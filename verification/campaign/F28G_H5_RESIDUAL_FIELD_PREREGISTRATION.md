# 🔴 DRAFT — NOT AUTHORISED TO LAUNCH. SUPERVISOR CHECK 4 HAS NOT BEEN PERFORMED.

**Nothing in this document may be launched.** It is a lane's draft, brought to
`cfd-supervisor` for his personal and undelegable check 4 (standing rule 2;
`SUPERVISION_CHARTER.md` §3). **No compute has been spent against it and none is
authorised by it.** The run directories it names —
`verification/runs/F28_runs/H5P_C_L1_dp1000_U20`,
`verification/runs/F28_runs/H5P_T_L1_dp1000_U20`,
`verification/runs/F28_runs/H5A_L1_dp1000_U20` — **do not exist**, and their
non-existence was checked when this draft was written (§11.1).

**This draft is not yet freezable.** Two named artifacts it depends on do not
exist yet: the launcher `run_f28_h5.sh` and the comparator `analyse_f28_h5.py`
(§9). Standing rule 2 fixes the grading path **at the pre-registration commit**,
so this document cannot be frozen until those two files are committed and their
blob hashes recorded in §9.3. **Freezing this document as it stands would breach
rule 2.** That gap is stated here rather than left for the supervisor to find.

**Date:** 2026-09-04 (box clock) · **Team:** cfd · **Lane:** `lab-lane`
**Parent rung:** `F28G_L1_dp1000_U20`, graded **`NOT A RESULT`** at `23eeff7e`
**Ordering document:** `verification/campaign/F28G_L1_RESIDUAL_RECONCILIATION.md`,
Addendum 1 §A1.2 / §A1.4 item 2 (`25aeb131`), Addenda 2–3 (`260d8e50`, `336de278`)
**Compute spent producing this draft: 0.000 core-minutes.** Artifact reads, source
reads and arithmetic. No solver, no queue row, no daemon contact.

---

## 0. What this registers, and the one thing it must not be read as

It registers **two runs and one arm**:

| | id | what it is | may a physics verdict be read off it? |
|---|---|---|---|
| **Pilot, control limb** | `H5P_C` | 72 iterations, `writeResidualFields false` | **No** |
| **Pilot, treatment limb** | `H5P_T` | 72 iterations, `writeResidualFields true`, **one** snapshot | **No** |
| **Arm** | `H5A` | 200 iterations, `writeResidualFields true`, **five** snapshots | Yes — §5's gates only |

**THE PILOT IS A COST-MEASUREMENT INSTRUMENT AND NOTHING ELSE.** It exists to
measure what §A2.4 of the ordering document named as the two costs its own table
did **not** carry: the extra write cost of `writeResidualFields true`, and
`decomposePar`/`reconstructPar`. **No physics verdict may be read off the pilot**,
and that prohibition is not left to good intentions — §5.4 makes it
**structural**: the arm's localisation gate requires agreement across **five**
decorrelated snapshots, and the pilot writes **one**. The pilot cannot satisfy
the arm's gate no matter what its field contains.

**It also is not a re-grading of the parent.** `F28G_L1_dp1000_U20` remains
**`NOT A RESULT`** on the two registered grounds of `23eeff7e`. Nothing here
disturbs that, and §A1.2's bar is carried forward verbatim: **the arm may not
reuse the parent's verdict, and a `NOT A RESULT` is not a baseline.**

---

## 1. FIXED BY THE SUPERVISOR — registered as given, not widened or reinterpreted

These five are `cfd-supervisor`'s, issued in the brief that commissioned this
draft. They are recorded here so that a later reader can see which clauses the
lane did **not** choose.

1. **Label on failure.** The arm produces **`GATE FAIL`** when its threshold is
   missed, and **`NOT A RESULT`** when the run is not strictly complete
   (standing rule 4, §7) or its grid triple is not `CONVERGING` (standing rule 5,
   §5.5). **It never produces a softened `PENDING`.**
2. **No reuse of the parent's verdict.** The arm may not reuse
   `F28G_L1_dp1000_U20`'s verdict. That rung is graded `NOT A RESULT` on HIT-CAP
   at endTime 15000, and **a `NOT A RESULT` is not a baseline.**
3. **The grading path is frozen at the pre-registration commit**, and the frozen
   file is verified to **be** the file that ran by hashing it against the
   committed blob before the arm runs (§9.3).
4. **The iteration cap is a REGISTERED GATE, not a convenience.** If the arm hits
   it, the label is **`NOT A RESULT`** on the HIT-CAP ground, exactly as the
   parent rung was (§5.5).
5. **The cap is not derived from the existing rate.** The full arm's cost cap is
   derived from the **pilot's measured** rate, never from the parent's
   1.581523e-06 s/cell/iteration alone — because that rate excludes the dominant
   new cost, and a cap derived from it is a cap engineered to be breached (§6.4).

---

## 2. THE FALSIFIABLE PROPOSITION — and the proof that `solverInfo.dat` cannot settle it

### 2.1 The proposition

> **P.** At the plateau state of `F28G_L1_dp1000_U20`, the cell-wise **gating**
> initial residual of `p` is **spatially concentrated** — the 355 cells (1%)
> carrying the largest `|r|` account for **at least half** of the domain-summed
> `|r|` — **and** that concentration sits in a **single one** of the five frozen
> geometric zones of §5.3, **stably across five decorrelated snapshots**.

P is falsifiable in three independent ways, each of which is a registered
outcome and not a disappointment: the residual may be **diffuse** (§5.2 fails),
or concentrated but **smeared across zones** (§5.3 fails), or **unstable
between snapshots** (§5.4 fails).

### 2.2 Why `solverInfo.dat` cannot settle it — read from the source, not assumed

`postProcessing/residuals/0/solverInfo.dat` records, per iteration, **exactly one
scalar per field**. From
`/usr/lib/openfoam/openfoam2606/src/OpenFOAM/matrices/lduMatrix/solvers/GAMG/GAMGSolverSolve.C`,
the value written for `p` is

```
solverPerf.initialResidual() = gSumMag(finestResidual, comm)/normFactor;
```

— a **global sum of magnitudes**, divided by a normalisation factor. It is
precisely the **denominator** of the concentration ratio P asserts, and nothing
else. The **numerator** — the partial sum of `|r|` over any subset of cells — is
not a function of any sequence of those global totals. **No history of scalar
norms, of any length, recovers a spatial partition of a single iteration's
residual.**

So P is not decidable from `solverInfo.dat` at any price. **The arm is not
redundant with the artifact the parent already wrote**, and §A1.1's finding —
that the FO "wrote the per-timestep scalar norms, which is the very series §3
already mines" — is confirmed and sharpened here: those norms are the
denominator, and the arm exists to obtain the numerator.

### 2.3 The arm measures the RIGHT quantity — the gating solve, not the corrector

This needed checking, because §4 of the ordering document catalogues the `res p`
defect — **taking the last `p` solve instead of the first** — as a hazard this
team has both quantified and then performed. A spatial instrument that recorded
the **corrector's** residual would re-commit that defect in field form, and it
would look completely plausible.

**It does not.** Traced through the v2606 source on this box:

| step | file:line | what it establishes |
|---|---|---|
| the field is created empty, one scalar per cell | `functionObjects/utilities/solverInfo/solverInfo.C:79-117` | name is `IOobject::scopedName("initialResidual", fieldName)`; `Field<scalar>(mesh_.nCells(), Zero)` |
| **`solverInfo` never fills it** | `solverInfo.C:161-198`, `solverInfoTemplates.C:109-162` | `updateSolverInfo` writes only to the `.dat` and to `setResult`; it never touches the `IOField` |
| the **linear solver** fills it | `lduMatrix/lduMatrix.C:463-503` | `setResidualField(residual, fieldName, initial=true)` assigns **only** `if (initial && dataPtr->isFirstIteration())` |
| `isFirstIteration()` is the guard | `meshState/meshState.C:143-146` | reads the `firstIteration` entry in the mesh controls dict |
| `simpleControl` **forces it true** at the top of every time step | `simpleControl/simpleControl.C:136-138` | `solutionControl::setFirstIterFlag(true, true)` — `force = true` |
| the **non-orthogonal corrector clears it** | `solutionControl/solutionControlI.H:76-101` and `solutionControl.C:180-203` | `correctNonOrthogonal()` calls `setFirstIterFlag()` **before** incrementing; the flag survives only while `corrNonOrtho_ == 0` |

**Sequence for this case (`nNonOrthogonalCorrectors 1`), step by step:**

| call | `corrNonOrtho_` on entry | flag after `setFirstIterFlag()` | the solve that follows |
|---|---|---|---|
| `loop()` | — | **true** (forced) | `U` — captured |
| `correctNonOrthogonal()` #1 | 0 | **true** | **`p` gating solve — CAPTURED** |
| `correctNonOrthogonal()` #2 | 1 | **false** | `p` corrector — **not** captured |
| `correctNonOrthogonal()` #3 | 2 → reset to 0 | **true** (loop exits) | `k`, `omega` — captured |

**Therefore `initialResidual:p` holds the cell-wise residual of the FIRST `p`
solve — the one §2.3 of the ordering document established that `residualControl`
actually tests, and the one whose global norm is the challenged-and-upheld
`0.1578798513`.** The instrument encodes the rule that the hand-read bypassed.
This is registered as a **finding**, because it is the reason the arm is worth
running rather than a detail of how it runs.

### 2.4 The field name is `initialResidual:p`, NOT `pResidual` — and this has a consequence

`IOobject::scopeSeparator` is **`':'`** on this box —
`OpenFOAM/db/IOobject/IOobject.C:43-50`, where the `'_'` value is inside the
`#ifdef _WIN32` limb and the `':'` value is the Linux limb. So the files the arm
will produce are

```
<time>/initialResidual:p   initialResidual:Ux   initialResidual:Uy
                            initialResidual:Uz   initialResidual:k    initialResidual:omega
```

**Six fields.** All six are solved every iteration in this case (measured on the
parent's log: `Solving for Ux`, `Uy`, `Uz`, `k`, `omega` each appear **15,000**
times; `Solving for p` appears **30,000**).

⚠ **Consequence for `f28_residual_field_census.py`, flagged and NOT acted on
here.** That reader's comment at lines 30–31 asserts *"v2606: solverInfo.C writes
`residualFieldName = fieldName + \"Residual\"`"* and its matcher is
`^[A-Za-z][A-Za-z0-9_.]*Residual$`. **That pattern cannot match
`initialResidual:p`** — the name ends in `:p`, and `:` is not in its character
class. Its planted control plants a file named `15000/pResidual`, i.e. **a plant
shaped like the reader's own assumption rather than like the artifact the solver
actually writes**. This is stated here for `cfd-supervisor` because the ordering
document is his and another lane's addenda are recent in it; §12 names what is
owed there. **It does not overturn Addendum 2's conclusion** — see §12.1.

---

## 3. THE DESIGN DEPARTURE: the arm RESTARTS from the plateau instead of cold-starting

§A2.4 costed item 2 as a **2,000-iteration** arm at **7.50 core-min**. This draft
registers something different, and the difference is the substance of the draft.

**The problem with a cold start.** H5 asks where the residual lives **at the
plateau the parent reached at iteration 15,000**. A 2,000-iteration cold restart
from `0/` gives the spatial residual at *its own* iteration 2,000 — a different
state, and one whose membership in the parent's plateau would itself have to be
argued.

**The parent's own plateau state is on disk, decomposed, at 35,544 cells.**
`verification/runs/F28_runs/F28G_L1_dp1000_U20/processor{0,1,2,3}/15000/` carry
`U k nut omega p phi` — everything a SIMPLE restart needs. So the arm restarts at
`startTime 15000` and runs to `endTime 15200`.

**Three things this buys, each checkable:**

1. **It samples the state the record actually gates on**, not a proxy for it.
2. **It is roughly an order of magnitude cheaper** — 200 iterations, not 2,000
   (§6.3: **2.55 core-min expected** against §A2.4's 7.50).
3. **It sidesteps a provenance gap.** §7 of the ordering document records that the
   FEAS arms' mesh directory was never identified. Reading the mesh census the
   same way for the graded rung: **no `mesh_*` root in `F28_runs` has 35,544
   cells** — `mesh_L1` and `mesh_L1_A1` have 31,752, `mesh_L2`/`mesh_L2_A1`
   58,292, `mesh_L3` 105,712, and §7 gives `mesh_A2/L1` as 33,864. The graded
   rung's mesh is unmatched among them. A restart from the rung's **own**
   `processor*/constant/polyMesh` inherits the exact mesh and makes the question
   moot for this arm. **It does not answer the question**, which stays open and
   is named in §12.

**What it costs, and it is not nothing.** `run_f28.sh` builds every case from
templates at time 0, always runs `decomposePar -force`, and reconstructs with
`reconstructPar -latestTime` (lines 426–543). **It cannot restart, and it cannot
reconstruct five intermediate snapshots.** So the arm requires a **new launcher**
(§9.1). That is real work and real risk, and it is the strongest argument for
running the 2,000-iteration cold-start arm instead. The trade is put to the
supervisor in §13, not decided here.

---

## 4. THE `relaxationFactors` DICTIONARY IS NOT CARRIED FORWARD UNEXAMINED

§A1.2 makes this binding on this registration and not re-litigable. Examined:

`system/fvSolution` carries `relaxationFactors { equations { p 0.3; U 0.7; k 0.7;
omega 0.7; } }` with **no `fields` sub-dictionary**, and §5 of the ordering
document traced through the v2606 source that this makes `p` run **unrelaxed at
`alpha_p = 1.0`** — the `p 0.3` entry is parsed into the equation dictionary and
never read by `simpleFoam`.

**Ruling for this arm: the dictionary is carried forward UNCHANGED, deliberately,
and the reason is registered.** The arm's purpose is to localise the residual of
**the state the parent reached**. Changing the relaxation would change that state
and would make the arm a test of H1 rather than a localisation of H5. **The arm
therefore runs at `alpha_p = 1.0` exactly as the parent did, and this document
records that `alpha_p = 1.0` is what runs, so that no later reader can mistake
the dictionary's `p 0.3` for the numerics in force.**

**Caveat carried forward unsoftened**, from §5: under `consistent yes` (SIMPLEC),
which this case sets, `alpha_p = 1.0` is the *recommended* setting, so this is
**not automatically an error and not automatically the cause of the plateau**. It
is a mismatch between the numerics the dictionary appears to specify and the
numerics that ran. **H1's arms, not this one, are where it gets tested.**

**VERIFY:** `alpha_p = 1.0` is established by source trace (§5 of the ordering
document), **not** by instrumenting a run. This arm does not instrument it either.

---

## 5. THE ARM'S GATES — frozen

All thresholds below are fixed at this commit and may not move afterwards.
`N_top = floor(0.01 × 35544) = 355` cells; the uniform-spread value of the
concentration ratio is `355/35544 = 0.0099876`.

### 5.1 The quantity gated

For each snapshot `t` and each of the six fields `f`, let `r_f,t[c]` be the value
in cell `c` of `<t>/initialResidual:f`. Define

```
f1%(f,t) = ( sum of |r| over the N_top cells of largest |r| ) / ( sum of |r| over all 35,544 cells )
```

**The gates below are stated for `f = p`.** The other five fields are computed and
reported by the same comparator, and are **reported, not gated** — with the
exception of `Uy`, which §6.2 H5 names as the second equation far from criterion
and which is gated identically in §5.6.

### 5.2 GATE G1 — CONCENTRATION

| | |
|---|---|
| **statement** | `f1%(p,t) ≥ 0.50` in **at least 4 of the 5** snapshots |
| **PASS** | the plateau residual is **localised** |
| **GATE FAIL** | the plateau residual is **diffuse** |

**A `GATE FAIL` here is an informative negative and is registered as such.** A
diffuse residual is not a null result: it means the plateau has **no local
source**, which is evidence **against** H4 (near-axis aspect ratio) and against a
disk-edge or duct-edge origin, and leaves the **global** hypotheses H1
(relaxation/coupling) and H3 (operating point still drifting) standing. The
vocabulary carries the verdict; this paragraph carries the meaning. Under
standing rule 1 the label is `GATE FAIL` and **not** a softened word.

**Why 0.50 and not something knife-edge.** Uniform spread gives 0.0099876. The
threshold sits a factor of **50.06** above it. The test is therefore not
sensitive to the exact choice: any threshold between roughly 0.05 and 0.8 would
separate the same two worlds. 0.50 is chosen as "the minority of cells carries
the majority of the residual", which is a statement with a plain meaning rather
than a tuned number.

### 5.3 GATE G2 — LOCATION (evaluated only if G1 PASSES)

Each of the `N_top` cells is assigned to exactly one zone, by **cell centre**
`(x, r)` with `r = sqrt(y² + z²)`, **in this precedence order** (first match
wins; the order makes the zones disjoint and exhaustive without tuning their
bounds):

| # | zone | definition | frozen from |
|---|---|---|---|
| 1 | **Z-DISK** | `0.0590 ≤ x ≤ 0.0740` and `0.0325 ≤ r ≤ 0.1275` | the `disk` cellZone `[0.0640, 0.0690] × [0.0375, 0.1225]` plus a one-thickness (0.005) collar |
| 2 | **Z-DUCT** | `0.0000 ≤ x ≤ 0.2500` and `0.1000 ≤ r ≤ 0.1800` | `ductInner` `x∈[0,0.20], r∈[0.1166190,0.1400000]`; `ductOuter` `x∈[0,0.20], r∈[0.1166190,0.1519988]`; extended to `x = 0.25` to include the trailing-edge wake |
| 3 | **Z-HUB** | `-0.0300 ≤ x ≤ 0.2500` and `r ≤ 0.0450` | `hub` `x∈[-0.03,0.20], r∈[0,0.0375]`, plus near wake |
| 4 | **Z-AXIS** | `r ≤ 0.0375` and (`x < -0.0300` or `x > 0.2500`) | the exposed near-axis region, where the sliver cells live |
| 5 | **Z-ELSEWHERE** | everything else | — |

All patch extents above are **measured**, not assumed: they are the output of
`cases/F28_DUCTED_ACTUATOR_DISK/f28_zone_geometry.py` run against the parent
rung's own `constant/polyMesh`, reproduced in §11.2. That reader carries a
**planted control** with a positive and a negative limb (standing rule 3) and
refuses rather than reporting an empty geometry.

| | |
|---|---|
| **threshold** | one zone carries `≥ 0.60` of the top-`N_top` `|r|` mass |
| **PASS** | that zone is **named** as the localisation |
| **GATE FAIL** | **MULTI-ZONE** — concentrated but not attributable to one feature |

**What each PASS outcome implicates**, registered before the run so that the
mapping cannot be chosen to fit the answer:

- **Z-AXIS** ⇒ supports **H4** (extreme aspect ratio; checkMesh reports max
  53,458.4 on this geometry, and the smallest strictly-positive point radius in
  this mesh is **2.592e-06 m**, §11.2).
- **Z-DUCT** ⇒ supports a genuine flow feature — trailing-edge or inner-surface
  separation — and so points at **H2** (unsteadiness) rather than at numerics.
- **Z-DISK** ⇒ implicates the actuator-disk source discretisation. **Note the
  prior:** §6.1 of the ordering document **exonerates the disk by measurement** —
  `FEAS_L1_dp0_U20_A2` has a source of exactly zero and plateaus **highest** of
  the four configurations. A Z-DISK result would therefore **contradict a standing
  measured finding**, and is registered as such so that it cannot be quietly
  absorbed if it happens.
- **Z-HUB** ⇒ centrebody or its near wake; no current hypothesis claims it, and
  it would be a new one.
- **Z-ELSEWHERE** ⇒ no current hypothesis claims it.

### 5.4 GATE G3 — STABILITY, and the structural bar on the pilot

Five snapshots at **15040, 15080, 15120, 15160, 15200**.

- **G1** requires `f1% ≥ 0.50` in **≥ 4 of 5**.
- **G2** requires the **same** zone to win in **≥ 4 of 5**.

**Why the spacing is 40.** §6.2 H2 reports the gating-residual autocorrelation
peaking at only `r = 0.207` at **lag 10** and decaying to `r ≈ 0.006` by **lag
400**. Lag 40 is four times past the peak. **VERIFY — this is an interpolation
between two reported points, not a measurement:** the autocorrelation at lag 40
is **not** stated in any artifact and was **not** re-derived for this draft. The
`≥ 4 of 5` rule is chosen to tolerate one outlier precisely because the
independence of the snapshots is argued rather than measured.

**THE STRUCTURAL BAR.** G1, G2 and G3 each require **five** snapshots. **The
pilot writes one** (§6.2, `writeControl onEnd`). **The pilot therefore cannot
satisfy any gate in this document, whatever its field contains.** The prohibition
on reading physics off the pilot is enforced by the gate's own arithmetic and not
by a promise.

### 5.5 `NOT A RESULT` — the two grounds, fixed by the supervisor

1. **Strict completion (standing rule 4).** Any clause of §7 failing ⇒
   **`NOT A RESULT`**, whatever the gates say.
2. **HIT-CAP.** If the arm reaches its iteration cap without reaching `endTime`
   as specified, the label is **`NOT A RESULT`** on the HIT-CAP ground, **exactly
   as the parent rung was**. The iteration cap is a registered gate, not a
   convenience.

**Standing rule 5 direction-of-travel clause, recorded because it binds the
comparator:** the gate can only turn a PASS or GATE FAIL **into** `NOT A RESULT`,
never the reverse.

**On Roache triple gating (standing rule 5):** this arm is a **single-level
localisation**, not a grid-convergence study. **It has no grid triple, so it
issues no GCI and quotes none**, and §5.5 ground 1 plus the plateau check of §5.7
are what stand in for it. **This is a departure from the shape of a graded rung
and is flagged for the supervisor in §13.**

### 5.6 The `Uy` limb

§6.2 H5 names `Uy` as the **only** other equation far from criterion at iteration
15,000 (`1.021e-2`, last-4,000 mean `1.32e-2`), and in this wedge `y` is radial.
`f1%(Uy,t)` is gated by G1/G2/G3 on the **same thresholds**, reported beside
`p`. **Agreement or disagreement between the `p` and `Uy` localisations is
reported as a named outcome** and is not permitted to be dropped if it is
inconvenient.

### 5.7 THE PLATEAU CHECK — a registered refusal, not a diagnostic

The arm restarts from fields written at `writePrecision 10`, so it is **not**
bit-identical to a continuation. It must therefore prove it is sampling the
parent's plateau and not some other state.

> **REFUSAL:** if the gating initial residual of `p` at **any** of the five
> snapshot iterations falls outside the parent's measured last-4,000 band
> **[0.1171, 0.5132]**, the arm is **`NOT A RESULT`** — it did not sample the
> plateau, and its localisation is of a state the record does not gate on.

**VERIFY:** that band is quoted from §3 of the ordering document and was **not**
re-derived for this draft.

### 5.8 THE PLANTED CONTROL — standing rule 3

A residual field of all zeros would read as a perfectly clean, perfectly
concentrated-nowhere answer. **The comparator refuses unless the reader is shown
able to see a non-zero, and unless the field it reads is connected to a quantity
already known independently:**

1. **Non-zero limb.** `sum(|r|) > 0` over the 35,544 cells, for every gated field
   and every snapshot. A zero sum ⇒ **refuse (exit 2)**, never a verdict.
2. **Connection limb — the strong one.** From `GAMGSolverSolve.C:79-83`, the
   scalar in `solverInfo.dat` **is** `gSumMag(finestResidual)/normFactor`. So for
   each snapshot the comparator computes `sum(|r|)` from the field and requires
   it to equal `normFactor × (the .dat scalar at that iteration)` to within
   **1 part in 10³**. This ties the field to a number the parent's own artifact
   already carries. **A field that is stale, zeroed, written from the corrector
   solve, or read with a wrong cell count fails this check.**
   **VERIFY — an honest limitation:** `normFactor` is **not** written to any
   artifact by OpenFOAM. The comparator therefore checks the ratio
   `sum(|r|)/(.dat scalar)` is **the same constant across all five snapshots to
   within 1 part in 10³**, rather than checking an absolute value. That is a
   weaker check than an absolute one and it is stated as weaker.
3. **Injected-perturbation limb.** Before grading, the comparator writes a known
   value `PLANT = 1.234e-03` into a known cell index of a **scratch copy** of one
   snapshot, re-reads it through the same code path, and **refuses** unless it
   reads `PLANT` back at that index. A reader that cannot see a planted value has
   not earned its zeros.

---

## 6. COST — core-minutes, and which figures are measured and which derived

### 6.1 The measured anchors, each with its artifact

| # | quantity | value | artifact |
|---|---|---|---|
| A1 | cells / points / faces | **35,544** / 71,914 / 142,514 | `F28G_L1_dp1000_U20/constant/polyMesh/owner` note |
| A2 | total run wall | **843.21 s** | `_launch.started_epoch` `1788472680.7950` (= `2026-09-03T21:58:00.795Z`) in `verification/queue/cfd/launched/F28G_L1_dp1000_U20.json`, to `end=2026-09-03T22:12:04Z` in `RUN_STATUS.F28.F28G_L1_dp1000_U20.txt` |
| A3 | **per-iteration wall** | **0.056214 s/iter** | A2 ÷ 15,000 |
| A4 | per-cell-iteration rate | **1.581523e-06 s/cell/iter** | A3 ÷ A1 — matches §6.2 and §A2.4 |
| A5 | solver startup + iteration 1 | **≤ 0.20 s** | first `ExecutionTime = 0.2 s`, `log.simpleFoam:8638` |
| A6 | solver non-CPU tail | **9.1 s** | final `ClockTime = 841 s` − `ExecutionTime = 831.9 s`; upper-bounds **all** of the parent's field-write and I/O wait |
| A7 | `decomposePar` | **≤ 1.320 s** | launch epoch `21:58:00.795` → `log.decomposePar` mtime `21:58:02.115` |
| A8 | `reconstructPar` | **≤ 0.683 s** | `log.simpleFoam` mtime `22:12:03.609` → `log.reconstructPar` mtime `22:12:04.292` |
| A9 | parent's full field write | **5,755,528 B** | `15000/` serial: `U` 1,604,162 + `k` 439,920 + `nut` 513,726 + `omega` 434,615 + `p` 458,447 + `phi` 2,304,658 |
| A10 | ranks | **4** | `system/decomposeParDict`, `numberOfSubdomains 4; method scotch;` |

### 6.2 The two costs §A2.4 named and did not carry — how this registration carries them

**(i) The extra write cost.** Six dimensionless scalar fields per snapshot.
Sizing from A9's measured `p` (458,447 B for 35,544 ASCII scalars at
`writePrecision 10`) as the per-field proxy:

```
bytes per snapshot   = 6 × 458,447            = 2,750,682 B  (2.62 MiB)
ratio to A9          = 2,750,682 / 5,755,528  = 0.47793
write cost bound     = 0.47793 × A6 (9.1 s)   = 4.349 s per snapshot
```

That bound is deliberately crude in the safe direction: it attributes **the whole
of the parent's 9.1 s non-CPU tail** to its single field write. **It is a bound
to be replaced by the pilot's measurement, not a prediction.**

⚠ **AND THE TRAP THAT WOULD HAVE BEEN WALKED INTO.** The parent's `residuals`
function object carries `writeControl timeStep; writeInterval 1`
(`system/controlDict:58-61`). **Simply setting `writeResidualFields true` and
changing nothing else calls `solverInfo::write()` on every single time step** —
confirmed at `timeControlFunctionObject.C:531-533`. Over the parent's 15,000
iterations that is **15,000 × 2.62 MiB ≈ 39 GB in 15,000 time directories**, on a
volume with 147 GB free, and a `reconstructPar` over 15,000 time directories.
**The arm therefore sets `writeControl onEnd` (pilot) or `writeInterval 40`
(arm), and this is the single most important line in its dictionary.**

**And it costs nothing to do so**, which had to be checked rather than hoped:
`timeControl::read` defaults `executeControl` to `timeStep` with interval 0
(`timeControl.C:110-141`), and `ocTimeStep` with `intInterval_ ≤ 1` fires on
**every** step (`timeControl.C:186-194`). **So changing `writeControl` does NOT
change the `.dat` cadence**, and the control limb's `solverInfo.dat` remains the
per-iteration series the parent produced. Without that, the pilot's control would
not have been a control.

**(ii) `decomposePar` / `reconstructPar`, named and costed SEPARATELY** as
§A2.4 requires — they are **not** folded into any per-iteration rate:

- **`decomposePar`: 0.000 s. It does not run.** The arm restarts from the
  parent's existing `processor*/15000/`, which are copied, not re-decomposed.
  This is a **structural** removal of A7, not an estimate of it.
- **`reconstructPar`: ≤ 0.683 s per time directory** (A8), scaled by the extra
  field volume `(5,755,528 + 2,750,682)/5,755,528 = 1.47793` → **≤ 1.010 s** per
  snapshot on the treatment limbs.

### 6.3 THE PILOT

**Iteration count `N_p = 72`, derived — not chosen round.**

> **Criterion.** The pilot's solve time must be at least **20×** the measured
> solver startup, so that startup contributes **≤ 5%** to the surcharge bound the
> pilot exists to produce.
>
> `N_p = ceil( 20 × A5 / A3 ) = ceil( 20 × 0.20 / 0.056214 ) = ceil(71.157) = 72`
>
> **Check:** `72 × 0.056214 = 4.047 s ≥ 20 × 0.20 = 4.0 s` ✓
> **Second constraint:** the pilot must cost less than the arm it costs, so
> `N_p ≤ N_arm/2 = 100`. `72 ≤ 100` ✓

**Expected cost:**

| limb | startup | solve | write | reconstruct | wall | core-min (×4/60) |
|---|---|---|---|---|---|---|
| `H5P_C` | 0.20 | 4.047 | 0 | 0.683 | **4.93 s** | **0.329** |
| `H5P_T` | 0.20 | 4.047 | 4.349 | 1.010 | **9.61 s** | **0.641** |
| | | | | | | **0.970 total** |

**CAP — derived from measured quantities, term by term, and generous exactly
where the unknown is:**

| term | `H5P_C` | `H5P_T` | ground |
|---|---|---|---|
| solve at **2×** the parent's rate | 8.095 | 8.095 | a 100% per-iteration surcharge allowance on an operation predicted at ~0.3% |
| startup at **10×** A5 | 2.000 | 2.000 | |
| write at **10×** the §6.2 bound | — | 43.492 | **the measurand.** Its allowance is ten times an already-conservative bound, so the quantity the pilot exists to measure can come in **an order of magnitude above** the bound and still not breach the cap |
| reconstruct at **2×** | 1.366 | 2.019 | |
| **total** | 11.46 → **13 s** | 55.61 → **56 s** | |
| **core-min** | **0.867** | **3.733** | **4.600 total** |

**Cap ÷ expected = 4.74×**, and the ratio is dominated entirely by the write
allowance. **That is the point.** A cap set from the parent's rate alone would
have allowed **0** for the write and would have been breached by the measurand
itself — the failure §A2.4 warned of in terms, and the failure the supervisor's
ruling exists to prevent.

### 6.4 THE ARM — cap PENDING the pilot, by construction

**Iteration count `N_arm = 200`**, derived: 5 snapshots × 40-iteration spacing
(§5.4). 200 iterations is **1.33%** of the parent's 15,000 — unambiguously a
localisation, not a physics re-run — and, being a continuation from 15,000, it
stays inside the parent's plateau regime **by construction** rather than by
argument, subject to the §5.7 refusal.

**The cost cap is registered as a FORMULA with one free input**, per the
supervisor's ruling that it may not be derived from the existing rate:

```
cap_wall(s) = N_arm × R_p × 2.0 × 1.5            ← solve, from the PILOT's rate
            + 5 × W_p × 3.0                       ← the five snapshot writes
            + 5 × T_rec                           ← reconstruct, NAMED SEPARATELY
            + 10 × A5                             ← startup allowance
```

where, **measured in the pilot and in nothing else**:
- `R_p` = per-iteration wall rate of the **treatment** limb
       = `(H5P_T wall − startup − write − reconstruct) / 72`
- `W_p` = the measured cost of **one** snapshot write
- `T_rec` = the measured `reconstructPar` wall per snapshot time directory

**The two margin factors are named separately rather than multiplied into one
round number:** **2.0** is the per-iteration surcharge allowance carried over from
§6.3; **1.5** is a contention allowance, because this box is shared and
`COMPUTE_BUDGET_CHARTER` §6 names contention as a distinct cost that is
**reported, never absorbed**. **VERIFY: no contention factor has been measured on
this box; 1.5 is a judgement and is labelled one.**

> **The arm's cost cap is `PENDING` until the pilot returns** (standing rule 1:
> `PENDING` is a queue/display state, and it is used here for "not yet
> measured", never to soften a failure). It lands as a **dated addendum** to this
> document, before any arm compute, under standing rule 2's before-first-compute
> clause — which is satisfiable **because no arm compute will have occurred**,
> and which is checked by naming the run directory that does not yet exist
> (§11.1). **Every other gate, threshold, label and the iteration cap in this
> document are frozen NOW and the addendum may not touch them.**

**Planning estimate — NOT a cap and never to be cited as one.** With the §6.2
bounds substituted for the pilot's measurements, the formula gives
`200 × 0.112428 × 1.5 + 5 × 4.349 × 3.0 + 5 × 1.010 + 2.0 = 111.2 s`
→ **7.42 core-min**. Expected arm spend is **2.55 core-min**
(`0.20 + 11.243 + 21.746 + 5.048 = 38.24 s`).

### 6.5 Ladder total, and honesty about dollars

| | core-min |
|---|---|
| pilot, expected | 0.970 |
| arm, expected | 2.549 |
| **ladder expected** | **3.52** |
| pilot cap | 4.600 |
| arm cap | **PENDING** (planning estimate 7.42) |

**Against §A2.4's estimate for item 2 alone — 7.50 core-min — this design is
expected to cost 3.52 core-min for the pilot AND the arm together**, while
sampling the actual plateau state rather than a cold-start proxy.

**Dollars are DERIVED and are never measured.** At the owner-stated `c7a.4xlarge`
rate of **$0.0513/core-h** (2026-08-21/22), 3.52 core-min = 0.0587 core-h =
**$0.0030 derived**. **The box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER` §5), so `cost_basis` for every row produced by these
runs must read **reported-by-owner rate, derived; not measured**.

**Estimate-versus-actual calibration (standing rule 12) is owed** at each of the
three completions — pilot control, pilot treatment, arm — as a row in
`docs/COST_CALIBRATION.md`, stating the ratio actual/predicted and attributing the
gap, with waste named separately and never absorbed into the ratio. **A completion
report without it is incomplete.**

---

## 7. STRICT COMPLETION (standing rule 4) — all six clauses, with the one substitution named

A run is done only if **all** of it holds. Any clause failing ⇒ **`NOT A RESULT`**.
The comparator **refuses (exit 2) rather than degrades**.

| # | clause | as it applies here |
|---|---|---|
| 1 | `rc = 0` | captured **INSIDE** the launcher on the line that runs the solver, **never around a `setsid` line** — `setsid timeout cmd` exits 0 for every outcome |
| 2 | an `End` line | in `log.simpleFoam` |
| 3 | last time == `endTime` | **15072** (pilot) / **15200** (arm) |
| 4 | fields present at `endTime` | `U p k omega nut phi`, **plus** on treatment limbs all six `initialResidual:{p,Ux,Uy,Uz,k,omega}` |
| 5 | `ExecutionTime` count | **⚠ SUBSTITUTED.** The standing form is `count == endTime`, which assumes `startTime = 0`. **These are restarts.** The registered form is `count == endTime − startTime` = **72** (pilot) / **200** (arm). This is a restatement of the clause for a restart, not a relaxation of it, **and it is flagged for the supervisor in §13** because a lane is not entitled to restate a standing completion clause on its own. |
| 6 | **age guard** | **⚠ SUBSTITUTED.** The standing anchor is the case's own `0/T`, touched last at launch. **This family has no `T`.** The registered anchor is the case's own **`0/p`**, which the launcher touches as its **last action before the solver line**; every field at `endTime` must be **strictly newer** than it. Also flagged in §13. |
| 7 | virgin-directory guard | the launcher **refuses** if the run directory already exists, or if any time directory `> startTime` exists in it |

---

## 8. THE DICTIONARY DIFFERENCE — the complete treatment, stated as a diff

Everything else — mesh, `fvSolution`, `fvOptions`, `transportProperties`,
`turbulenceProperties`, `decomposeParDict`, and every other function object — is
**byte-identical** to the parent rung's. The comparator asserts this by hash.

**`H5P_C` (pilot control):** `system/controlDict` differs from the parent's in
`startFrom`/`startTime`/`endTime`/`writeInterval` only. **`writeResidualFields`
stays `false`.**

**`H5P_T` (pilot treatment):** as `H5P_C`, and the `residuals` function object
becomes

```
    residuals
    {
        type            solverInfo;
        libs            ("libutilityFunctionObjects.so");
        fields          (p U k omega);
        writeResidualFields true;      // <-- the treatment
        executeControl  timeStep;      // explicit; equals the default (§6.2)
        executeInterval 1;             // keeps solverInfo.dat per-iteration
        writeControl    onEnd;         // ONE snapshot.  NOT `timeStep 1` (§6.2)
    }
```

**`H5A` (arm):** as `H5P_T`, but `writeControl timeStep; writeInterval 40;`
→ five snapshots at 15040/15080/15120/15160/15200.

**Registered as a conflation, not hidden:** the treatment limb differs from the
control in **two** ways — the switch **and** the write cadence. That is
deliberate: **the pilot measures the cost of the configuration the arm will
actually run**, not of an abstract switch. The cadence is part of the treatment
by design, and no attempt is made to attribute the measured delta between the two
causes.

**And the attribution rule, chosen in the safe direction and stated:** the pilot's
measured delta is amortised **per-iteration** when it scales to the arm, even
though part of it is a one-time write. Over `N_arm > N_p` that **over**-estimates
the arm's cost, which widens the cap. **A cap that is too generous wastes nothing
unless it is spent; a cap that is too tight kills the run and produces no
verdict.** The over-estimate is deliberate and is not to be "corrected" later.

---

## 9. THE GRADING PATH — and the reason this document cannot yet be frozen

### 9.1 `cases/F28_DUCTED_ACTUATOR_DISK/run_f28_h5.sh` — **DOES NOT EXIST**

Required because `run_f28.sh` cannot restart and cannot reconstruct intermediate
snapshots (§3). Required behaviour: copy the parent's `system/`, `constant/`, `0/`
and `processor*/{constant,15000}/` into a **new, virgin** run directory; apply
exactly the §8 dictionary difference; **run no `decomposePar`**; touch `0/p` as
the last action before the solver line; capture `rc` **inside** the wrapper on the
solver line; `reconstructPar -time '15040,15080,15120,15160,15200'` for the arm
(**not** `-latestTime`, which would reconstruct one of five).

### 9.2 `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28_h5.py` — **DOES NOT EXIST**

Required behaviour: §5's gates on the frozen thresholds; §5.8's three planted
limbs, **refusing (exit 2)** rather than grading if any fails; §7's seven
completion clauses; §5.7's plateau refusal; the §8 byte-identity assertions.

### 9.3 The freeze, and the gap

Standing rule 2 fixes the grading path **at the pre-registration commit**, and the
frozen file is verified to **be** the file that ran by hashing it against the
committed blob. **Neither file exists, so there is nothing to hash, so this
document is NOT FREEZABLE as it stands.** Recorded plainly rather than papered
over. The blob hashes go here:

```
run_f28_h5.sh        blob: ____________________  (PENDING — file does not exist)
analyse_f28_h5.py    blob: ____________________  (PENDING — file does not exist)
```

`f28_zone_geometry.py`, which produced §5.3's frozen zone bounds, **does** exist
and is committed with this draft.

---

## 10. QUEUE, ORDERING AND CONTENTION

- **Ordering.** §A1.4 ranks this **item 2**, behind item 1 (H3's exponential fit,
  discharged at `b209c4f6`/`0e8a3d41` per §A2.2) and ahead of item 3 (H1's two
  arms). This draft does not disturb that ordering.
- **The pilot runs before the arm**, and the arm does not launch until the pilot's
  measurement has landed as the §6.4 addendum.
- **⚠ The queue row is not to be trusted to carry this document's evidence
  contract.** §A2.5 established that the daemon **overwrites** the committed
  `_field_classes.physics_critical` with a template that names a file which does
  not exist. Any queue row for these runs must be **read back after the daemon
  has written it** and compared against the committed blob. This is a known live
  defect and it is not fixed by this document.

---

## 11. WHAT WAS CHECKED WHEN THIS DRAFT WAS WRITTEN

### 11.1 The run directories do not exist

Standing rule 2 requires an amendment before first compute to state the condition
and **how it was checked**, naming the run directory that does not exist. Checked
by directory listing of `verification/runs/F28_runs/` at draft time: it contains
`F28G_L1_dp1000_U20`, the `FEAS_*`, `DIAG_*` and `mesh_*` roots, and **no**
`H5P_C_L1_dp1000_U20`, `H5P_T_L1_dp1000_U20` or `H5A_L1_dp1000_U20`.

### 11.2 The frozen geometry, as measured

Output of `cases/F28_DUCTED_ACTUATOR_DISK/f28_zone_geometry.py` against
`verification/runs/F28_runs/F28G_L1_dp1000_U20`, with `r = sqrt(y² + z²)`:

| patch | nFaces | x_min | x_max | r_min | r_max |
|---|---|---|---|---|---|
| inlet | 96 | -2.5000000 | -2.5000000 | 0.0000000 | 3.7500000 |
| outlet | 140 | 6.4500000 | 6.4500000 | 0.0000000 | 3.7500000 |
| farfield | 274 | -2.5000000 | 6.4500000 | 3.7500000 | 3.7500000 |
| axis | 0 | *(no faces — no bounding box)* | | | |
| hub | 122 | -0.0300000 | 0.2000000 | 0.0000000 | 0.0375000 |
| ductInner | 98 | 0.0000000 | 0.2000000 | 0.1166190 | 0.1400000 |
| ductOuter | 98 | 0.0000000 | 0.2000000 | 0.1166190 | 0.1519988 |
| front | 35544 | -2.5000000 | 6.4500000 | 0.0000000 | 3.7500000 |
| back | 35544 | -2.5000000 | 6.4500000 | 0.0000000 | 3.7500000 |

Smallest strictly-positive **point** radius in the mesh: **2.592e-06 m**
(next: 2.592e-06, 6.621e-06, 6.621e-06). This is the geometric origin of the
max aspect ratio 53,458.4 that §6.2 H4 rests on.

**The reader's planted control fired on both limbs**, and its first draft was
**refused by its own negative control**: the selftest asserted a minimum radius
of 2.0 where the plant's true value is 1.0, because two planted points carry
their radius **entirely in `z`**. The refusal is what established that the
radius formula includes `z` rather than reading `r = |y|`. Recorded because a
control that never fires has not been shown to work.

### 11.3 Six residual fields, not four

`fields (p U k omega)` produces **six** scalar fields, because `U` expands per
component. Confirmed against the parent's log: `Solving for Ux`, `Uy`, `Uz`, `k`
and `omega` each appear **15,000** times, and `Solving for p` **30,000** times
(the gating solve and the non-orthogonal corrector, §2.2 of the ordering
document). All three velocity components are solved; none is dropped by the
wedge.

---

## 12. FOR `cfd-supervisor` — what this draft implies must be recorded in the ordering document, which this lane did NOT touch

**`F28G_L1_RESIDUAL_RECONCILIATION.md` was not edited by this lane**, on the
supervisor's instruction. Two things are owed there and are named rather than
written:

### 12.1 Addendum 2 §A2.3's field-name limb is void; its CONCLUSION stands

A2.3's negative rests on **two** limbs. They do not fare the same:

- **Limb 1 — the switch.** 12 solve roots, **every one** `writeResidualFields
  false`; **0** reading true. **Untouched, and decisive on its own:** a run with
  the switch false writes no spatial residual under **any** naming.
- **Limb 2 — the field names.** "0 roots carrying any field matching
  `<name>Residual`". **Void.** The pattern
  `^[A-Za-z][A-Za-z0-9_.]*Residual$` **cannot match `initialResidual:p`**, which
  is what v2606 actually writes (§2.4). Its zero is a **structural** zero, not a
  measured one — and its planted control planted `pResidual`, i.e. **the reader's
  own assumption rather than the artifact the solver produces**. Standing rule 3
  in its exact failure mode: *a zero from a reader not shown able to see the
  non-zero it would actually meet.*

**A2.3's conclusion — "ITEM 2 IS A PAID RE-RUN AND CANNOT BE MADE CHEAPER BY
BORROWING A SIBLING'S FIELDS" — STANDS**, because limb 1 carries it alone, and
because with 0 roots reading `true` no root could carry the field under any
naming. **What is owed is the strike of limb 2 and a re-run of the census with
`initialResidual:` as the plant**, so that its zero becomes a read zero rather
than a blind one.

### 12.2 The graded rung's mesh provenance is unmatched among the `mesh_*` roots

§7 records that the FEAS arms' mesh directory was never identified. The same
question for the **graded** rung: `mesh_L1`/`mesh_L1_A1` are 31,752 cells,
`mesh_L2`/`mesh_L2_A1` 58,292, `mesh_L3` 105,712, and §7 gives `mesh_A2/L1` as
33,864. **None is 35,544.** This arm sidesteps it by restarting from the rung's
own mesh (§3), but the question is **open** and is not answered here.

---

## 13. WHAT THIS LANE COULD NOT VERIFY, AND WHAT IT IS NOT ENTITLED TO DECIDE

**Not verified (each would change something if it were false):**

- **VERIFY:** No `initialResidual:*` file has ever been produced on this box and
  this lane has not seen one. That the field is written, is non-empty, carries
  35,544 values and is readable by `reconstructPar` **with a `:` in its
  filename** is **inferred from source**, not observed. **It is the pilot's
  first job** (§5.8), and if it fails, the arm does not run.
- **VERIFY:** The plateau band [0.1171, 0.5132], the gating trajectory, and the
  autocorrelation figures are **quoted** from §3 and §6.2 of the ordering
  document and were **not** re-derived here.
- **VERIFY:** The autocorrelation at lag 40 is **interpolated** between the two
  reported points (lag 10, lag 400) and is not measured. §5.4's `≥ 4 of 5` rule
  exists because of this.
- **VERIFY:** `alpha_p = 1.0` is a source trace, not an instrumented run (§4).
- **VERIFY:** The 2.62 MiB-per-snapshot figure uses the parent's measured `p`
  field as a per-field proxy. Residual values are dimensionless and may format to
  a different width; the pilot measures the true figure.
- **VERIFY:** No contention factor has been measured on this box. §6.4's 1.5 is a
  judgement, labelled one.
- **VERIFY:** A 200-iteration continuation is asserted to remain in the parent's
  plateau **by construction**. §5.7's refusal exists because that assertion is
  not itself a measurement.

**Not this lane's to decide — put to `cfd-supervisor`:**

1. **The restart design itself** (§3). It is cheaper and more faithful, and it
   costs a **new launcher**. The alternative is §A2.4's 2,000-iteration
   cold-start arm, which `run_f28.sh` can already run.
2. **The two completion-clause substitutions** (§7 clauses 5 and 6). Restating
   `ExecutionTime count == endTime` as `== endTime − startTime`, and moving the
   age-guard anchor from `0/T` to `0/p`, are restatements for a restart and for a
   non-thermal family. **A lane is not entitled to restate a standing completion
   clause**, however faithful the restatement.
3. **The absence of a grid triple** (§5.5). This arm is a single-level
   localisation and issues no GCI.
4. **Whether the arm runs at all** — see §14.

---

## 14. WOULD I CANCEL THIS ARM? — the honest answer

**No, and the reason is specific rather than deferential.**

**The case for cancelling, stated at its strongest:**
- H5 is, in §6.2's own words, *"a localiser, not a rival"*. It does not explain
  the plateau; it re-ranks H1–H4.
- §6.1 already **exonerates the actuator disk by measurement**, so one of the four
  outcomes is a priori unlikely.
- H3 has **measured support** and is unresolved; H1's arms are cheap. A ladder
  that ran H1's arms and finished H3 and skipped H5 would not be obviously worse.
- The arm needs a **new launcher** that does not exist, and new code is where
  defects come from — this document's own §12.1 is a defect in a reader written
  four days ago.

**Why it still runs:**
1. **It measures something no existing artifact can yield**, and that is proved
   from the source rather than asserted: `solverInfo.dat` holds the
   **denominator** of the concentration ratio and cannot hold the numerator
   (§2.2). This is not a cheaper-way-exists situation.
2. **It measures the RIGHT quantity** — the gating solve, not the corrector
   (§2.3). This had to be checked, because the opposite would have re-committed
   the very defect §4 of the ordering document exists to preserve, in a form that
   would have looked entirely plausible.
3. **It is the ladder's only discriminator.** §A1.2 ruled it **REQUIRED rather
   than optional** on exactly this ground, and nothing found here weakens that.
4. **The price is now small enough that the argument from cost is spent.** At
   **3.52 core-min expected** for pilot and arm together — against §A2.4's 7.50
   for the arm alone — the compute argument no longer decides anything. The
   argument that decides it is whether the launcher is worth writing, and that is
   §13's question 1.

**What would make me cancel it:** if the supervisor declines the restart design
(§13.1), the arm reverts to a 2,000-iteration cold start whose relationship to
the parent's plateau is an argument rather than a construction, at roughly three
times the cost, to answer a question that only re-ranks hypotheses. **At that
price and that fidelity I would run H1's two arms first and revisit H5 after**,
and I would say so rather than run it for form's sake.

---

## 15. VERDICT

**None. This document issues no verdict and is entitled to none.** It is a draft
pre-registration. `F28G_L1_dp1000_U20` remains **`NOT A RESULT`** exactly as
graded at `23eeff7e`.

**Compute spent: 0.000 core-minutes.** No solver was launched, no queue row was
touched, no daemon was contacted. **No `docs/COST_CALIBRATION.md` row is owed**
under the standing zero-compute ruling.

**SUBMISSIONS PARKED** (standing rule 7). Nothing here is sent, filed or
registered anywhere outside this box.
