# 🔴 DRAFT — NOT AUTHORISED TO LAUNCH. SUPERVISOR CHECK 4 HAS NOT BEEN PERFORMED.

**Nothing in this document may be launched.** It is a lane's draft, brought to
`cfd-supervisor` for his personal and undelegable check 4 (standing rule 2;
`SUPERVISION_CHARTER.md` §3). **No compute has been spent against it and none is
authorised by it.** The run directories it names —
`verification/runs/F28_runs/H5P_C_L1_dp1000_U20`,
`verification/runs/F28_runs/H5P_T_L1_dp1000_U20`,
`verification/runs/F28_runs/H5A_L1_dp1000_U20` — **do not exist**, and their
non-existence was checked when this draft was written (§11.1).

**REVISION 2, 2026-09-04 — the grading path now exists.** Revision 1 of this
draft recorded that it was **not freezable**, because the launcher and the
comparator did not exist and rule 2 fixes the grading path at the
pre-registration commit. `cfd-supervisor` ruled (ruling 3) that the gap was
correctly self-reported and ordered both files written. **They are now written,
selftested and committed, and their blob hashes are recorded in §9.3.** This
revision also carries his rulings 1, 2a, 2b and 4, each marked where it lands.

**It is still a DRAFT and still may not launch.** Check 4 has not been
performed.

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
(§9.1). That is real work and real risk, and it was the strongest argument for
running the 2,000-iteration cold-start arm instead.

### 3.1 RULING 1 — the restart is APPROVED, and the parent's run root is IMMUTABLE

`cfd-supervisor`, 2026-09-04: the restart design is approved. **Condition, not
negotiable: `F28G_L1_dp1000_U20` is a graded artifact carrying a `NOT A RESULT`
verdict, and a restart that wrote into its `processor*` directories would mutate
the evidence for a verdict already on the record.** The lab closed nineteen
data-destruction sites across nine run trees on the day this was ruled.

**How the launcher discharges it — proved per run, not promised in a comment:**

1. **It copies OUT of the parent and never writes INTO it.** The arm's run root
   is its own; the parent is opened read-only.
2. **It fingerprints the parent before and after.** `find -printf '%P %s %T@'`
   over every file under the parent, sorted, captured **before** the copy,
   compared **after the copy** and again **after the solve**. Either diff
   non-empty ⇒ **abort**, with the diff printed. Immutability is a measurement
   per run, not an assurance.
3. **It asserts that `scripts/solve_evidence_guard.py` REFUSES the parent.**
   The parent is a completed solve, so `refuse_if_solve_evidence` **must**
   raise; if it returns cleanly the launcher stops. **That assertion is a
   planted control on the guard itself:** if the guard ever stops recognising a
   completed solve as evidence, this launcher stops rather than proceeding on a
   protection that has silently lapsed.

**The copy is cheap, and this was measured rather than feared.** The supervisor
raised the possibility that copying 15,000 time directories would be too
expensive. **The parent holds ONE time directory per processor, not 15,000** —
its `writeInterval` equalled its `endTime`, so it wrote fields once. Measured
2026-09-04:

| what is copied | size |
|---|---|
| `processor0..3` (each `constant` + `0` + `15000`) | 3.7 + 3.8 + 3.8 + 3.8 = **15.1 MB** |
| `constant/` | 7.9 MB |
| `system/` + `0/` | 24 KB + 24 KB |
| **total per run root** | **≈ 23 MB** |

No alternative to the copy is needed, and none is proposed.

### 3.2 WHAT THE RESTART INHERITS — named, because an inherited state is a shared assumption

A cold start would inherit none of this. The restart inherits **all** of it, and
each item is an assumption the arm's result rests on:

- **The parent's decomposition** — `scotch`, 4 subdomains, and the *specific*
  partition scotch produced for this mesh. The arm does **not** re-run
  `decomposePar`, so the cell-to-rank map is the parent's exactly.
- **The parent's `processor*` layout** — including its processor-boundary
  patches. A residual concentrated **on a processor boundary** would be a
  decomposition artifact rather than a flow feature; §5.3's zones are geometric
  and do not test for this, so it is named here as an **uncontrolled**
  alternative explanation for a Z-ELSEWHERE outcome.
- **Whatever state the parent's `15000` fields carry** — including the
  cumulative continuity error that §6.2 H3 measures growing monotonically to
  0.27796, and the still-drifting operating point. The arm samples that state; it
  does not correct it and must not be read as independent of it.
- **The parent's mesh**, whose provenance is an open defect (§12.2).

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

### 5.5a 🔴 NAMED LIMITATION — SINGLE-GRID. NO ROACHE VERDICT IS POSSIBLE FROM THIS ARM

**RULED by `cfd-supervisor`, 2026-09-04.** Recorded as a **named limitation**, not
as a caveat in passing.

> **THIS ARM IS A SINGLE-GRID SPATIAL DIAGNOSTIC AND MAY NEVER PRODUCE A
> ROACHE-GATED VERDICT.** Standing rule 5 gates on a grid triple. **There is no
> triple.** A triple that does not exist cannot be `CONVERGING`. Therefore: **no
> GCI may be computed from this arm, none may be quoted, and no result from it
> may be labelled grid-converged.**

**Its verdict vocabulary is `PASS` / `GATE FAIL` / `NOT A RESULT` on the spatial
concentration proposition ALONE.**

**And the proposition must be read for what it is.** §2.1's P asserts **WHERE the
residual sits on ONE mesh**. It asserts **nothing** about whether that location is
**mesh-independent**. A `PASS` naming `Z-AXIS` says the residual is concentrated
near the axis *on the 35,544-cell mesh the parent ran*; it does **not** say the
concentration would survive refinement, and it may not be quoted as though it
did. H4 in particular — extreme aspect ratio — is a hypothesis **about** the mesh,
so a single-mesh result can implicate it but can never confirm it, since the
confirming experiment is precisely the refinement this arm does not perform.

**THE SAME STRUCTURAL GAP AS RUNG 2.** `cfd-supervisor` directs that this be
recognisable beside Rung 2's, where only one refinement level exists on the box.
**Same shape, stated the same way:** a gate that would otherwise be Roache-gated
is run at one level, so the verdict is sound *about what it measures* and silent
about mesh convergence — and the silence is declared in the registration rather
than discovered by a reader. Anyone reading the two side by side should see one
class, not two coincidences.

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
| 5 | `ExecutionTime` count | **SUBSTITUTED — APPROVED by `cfd-supervisor`, ruling 2a.** The standing form is `count == endTime`, which assumes `startTime = 0`. **These are restarts.** The registered form is `count == endTime − startTime` = **72** (pilot) / **200** (arm). Ruled *"a faithful adaptation of the clause, not a weakening of it"* — it fails on exactly the same defect the original catches, and the original is its `startTime = 0` case. |
| 6 | **age guard** | **SUBSTITUTED — my `0/p` proposal was REFUSED; see §7.1 for what replaces it.** |
| 7 | virgin-directory guard | the launcher **refuses** if the run directory already exists, or if any time directory `> startTime` exists in it |

### 7.1 RULING 2b — the `0/p` anchor was REFUSED AS VACUOUS, and it deserved to be

**My proposal was to move the age-guard anchor from `0/T` to `0/p`. It is
refused, and the reasoning is worth more than the substitution.**

Standing rule 4 anchors on `0/T` **because that file is touched LAST AT LAUNCH
and therefore DATES THE RUN ALLOWED TO PRODUCE THE ANSWER.** In a restart, `0/p`
is copied in from the parent and carries the **parent's** launch time — hours or
days earlier. Every field the restart writes is *necessarily* newer than it.

> **The guard would have passed unconditionally. It would have been VACUOUS —
> and a vacuous guard that reports green is worse than an absent one, because it
> certifies.**

That is the same family as §5's silent no-op and L-478's *a name is not a
control*: the mechanism is present, the name is right, and no input exists that
makes it announce its own uselessness. I proposed it, and I did not see it.

**REGISTERED ANCHOR: `RESTART_SENTINEL`**, written by `run_f28_h5.sh` as its
**last action before the solver line**, after a `sleep 1` so that it is strictly
older than any field written afterwards even at 1-second filesystem timestamp
granularity. Every residual field at every snapshot must be **strictly newer**
than it. A **missing** sentinel is a **refusal**, not a default to green.

**The guard carries a planted control, and the vacuity is DEMONSTRATED rather
than asserted.** `analyse_f28_h5.py --selftest`, limb 6, has four sides:

1. a field written **before** the sentinel is **REFUSED** *(the negative side —
   without it, the guard's green is my word)*;
2. a field written **after** it **passes**;
3. a **missing** sentinel is **REFUSED**;
4. **the refused design is built and shown to pass unconditionally** — a
   fixture with an inherited `0/p` anchor and a field written later, proving
   the `0/p` guard would have certified anything. The reason the anchor moved
   is in the test suite, not only in this paragraph.

A **mutation control** confirms the suite can go red: neutering the staleness
comparison (`if os.path.getmtime(p) <= t_anchor:` → `if False:`) turns limb 6's
negative side red and the suite exits 2. A control that cannot fail is not a
control.

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

## 9. THE GRADING PATH — written, selftested, committed and hashed

### 9.1 `cases/F28_DUCTED_ACTUATOR_DISK/run_f28_h5.sh`

Copies the parent's `system/`, `constant/`, `0/` and
`processor*/{constant,0,15000}/` into a **new, virgin** run root; applies exactly
the §8 dictionary difference; **runs no `decomposePar`**; writes
`RESTART_SENTINEL` as the last action before the solver line (§7.1); captures
`rc` **inside** this process **on** the solver line, with no `setsid` near it;
`reconstructPar -time '15040,15080,15120,15160,15200'` for the arm (**not**
`-latestTime`, which reconstructs one of five and would make the missing four
look like a physics absence). Discharges ruling 1 as §3.1 sets out. `--dry-run`
assembles and runs every guard, then **stops before the solver**.

**The dictionary surgery is done in python with count assertions, not `sed`.**
`controlDict` carries `writeControl timeStep;` **five** times — once at top level
and once per function object — and `writeInterval` likewise, so a bare `sed`
would silently rewrite all of them. Each substitution asserts **exactly one**
occurrence and refuses otherwise.

**Verified without creating any run root** (2026-09-04): `bash -n` clean; the
rewrite block driven against a **copy** of the parent's real `controlDict` for
all three modes produces exactly and only the intended changes — top-level
`startTime`/`endTime`/`writeInterval` and, on treatment limbs, the `residuals`
function object; **the four function-object `writeInterval 1;` lines are
untouched**. Re-running a rewrite on an already-rewritten dictionary **refuses**
(`expected exactly 1 occurrence of 'startTime       0;', found 0`), which is the
count assertion firing.

### 9.2 `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28_h5.py`

§5's gates on the frozen thresholds; §5.8's three planted limbs; §7's seven
completion clauses and §7.1's sentinel guard; §5.7's plateau refusal.
**It refuses (exit 2) rather than degrades**, everywhere.

`--selftest` runs **eight limbs, 22 checks, each with a positive AND a negative
side**, and all fire. **Mutation control:** two independent mutations — neutering
the age-guard comparison, and making the reader accept the suffix form
`pResidual` — each turn the suite **red** (exit 2). A suite that cannot fail is
not a suite.

### 9.3 THE FREEZE — blob hashes

Standing rule 2 fixes the grading path **at the pre-registration commit**, and
the frozen file is verified to **be** the file that ran by hashing it against the
committed blob before the arm runs.

```
run_f28_h5.sh         blob f3534f1be02768a35b9449ef8ed38b171560a034
analyse_f28_h5.py     blob f49805eb6c0d85421dad7a0ee1344409e87922c4
f28_zone_geometry.py  blob 98863fc92f041799dac443a44d86fff3ac24b930
```

#### 9.3a ⚠ THREE AMENDMENTS TO THE GRADING PATH — TWO BEFORE FIRST COMPUTE, ONE AFTER THE PILOT

**AMENDMENT 3 landed after the pilot ran and before any ARM compute**, and is
recorded in full at §15A.3: the top-level `writeInterval` was compared against
the continuing `timeIndex` rather than the iteration count, so no solution
fields were written at `endTime` and both pilot limbs failed rule 4 clause 4.
The launcher blob above is the amended one; the blob the pilot actually ran was
`929dba146bf3d0746e247c0a94aad2774fa1237b`. **The condition rule 2 requires: no
arm compute has occurred — `verification/runs/F28_runs/H5A_L1_dp1000_U20` does
not exist, checked by directory listing immediately before amending.** No gate,
threshold, cap or label is touched.

**The first two hashes MOVED after check 4 passed on them.** They were
`d6d381de…` and `d00e2876…` at check 4, and `cfd-supervisor` verified those two
blobs against the worktree personally. **They are superseded**, and the reason is
recorded here rather than left for the next hash comparison to discover.

**The condition standing rule 2 requires, and how it was checked.** Rule 2 permits
amendment **before first compute** and requires the condition to be stated with
the check that established it. **The condition is that no compute has occurred
against this registration.** Checked by directory listing of
`verification/runs/F28_runs/` immediately before amending: **zero** entries
beginning `H5` — `H5P_C_L1_dp1000_U20`, `H5P_T_L1_dp1000_U20` and
`H5A_L1_dp1000_U20` **do not exist**, no solver has run, and no `--dry-run` had
yet been performed. **Neither amendment touches a gate, a threshold, a cap or a
label**; both are defects in the path that would have prevented the registered
gates from being evaluated at all.

**AMENDMENT 1 — `run_f28_h5.sh`: `--dry-run` must not consume the real run root
name.** As written, the dry run assembled into `$RUNS/$NAME` and stopped before
the solver. Two consequences, both bad: the virgin-directory guard would then
have **REFUSED the real pilot run that followed**, and §11.1's freshness claim —
that the three named run directories do not exist — would have been **falsified
by the act of testing it**. `cfd-supervisor` has been citing absences as evidence
all day; a test must not manufacture a presence. A dry run now assembles into
`<NAME>_DRYRUN` and leaves the registered names untouched.

**AMENDMENT 2 — `analyse_f28_h5.py`: `solverInfo.dat` lives under the RESTART
time, not under `0`.** The comparator hardcoded
`postProcessing/residuals/0/solverInfo.dat`. **That is the PARENT'S directory
name, because the parent started at time 0.** A restart from 15000 writes
`postProcessing/residuals/15000/`. **The hardcoded path would have been missing
on every single run this comparator exists to grade, and it would have refused
every arm for a reason that was its own** — a comparator manufacturing its own
`NOT A RESULT`. It now scans every time-named subdirectory and merges their rows.

**Both defects are now pinned by executable checks, not by these paragraphs.**
`--selftest` limb 9 requires the reader to find `solverInfo.dat` under
`postProcessing/residuals/15000`, requires the column selector to pick
`Uy_initial` rather than the first numeric column, and requires a **refusal**
when no `.dat` exists anywhere. The suite is now **9 limbs / 25 checks**, all
firing on both sides.

**How this was found:** by reading the parent's own `postProcessing/` layout and
`solverInfo.dat` header before launching anything, rather than after. The header
read also confirmed the column names the comparator assumes (`p_initial`,
`Uy_initial`) and their positions.

**These three hashes are the freeze.** Before either run launches, each file is
re-hashed with `git hash-object` and compared against the line above; a mismatch
means the file that would run is not the file that was registered, and the run
does not start.

⚠ **HOW TO TEST TRACKEDNESS UNDER THIS LAB'S GIT PROTOCOL — a trap
`cfd-supervisor` hit while performing check 4, recorded because it will recur.**
`git ls-files --error-unmatch <path>` reported **both** of these files as **NOT
TRACKED**, while `git rev-parse HEAD:<path>` resolved both to blobs matching the
worktree. **Both readings are correct.** `ls-files` reads the **SHARED INDEX**,
and the rule-10 private-index protocol commits **without ever touching it** — so
a file can be **fully committed at HEAD and invisible to `ls-files`**.

> **Under this lab's git protocol `git ls-files` UNDER-REPORTS and is the WRONG
> trackedness test. The authoritative test is the blob at HEAD.** He nearly
> recorded a false "not tracked" finding; the blob check caught it.

Any check of this document's freeze — check 4's, or a later audit's — must use
`git rev-parse HEAD:<path>` or `git cat-file`, never `git ls-files`.

### 9.4 THE PILOT'S FIRST JOB — ruling 3

`cfd-supervisor`: *"Include the §5.8 observation as the FIRST thing the pilot
does."* Registered accordingly, and it is the first thing the comparator prints:

> **No `initialResidual:*` file has ever been produced on this box.** That it is
> written, is non-empty, carries 35,544 values, and is readable and
> reconstructable **with a colon in its filename** is **inferred from
> `IOobject.C:43-50` and never observed**. The comparator reports the separator
> it actually found, and says so explicitly when the `':'` form was not seen.
>
> **If the colon breaks `reconstructPar` or any downstream reader, the arm does
> not run — and that is a finding worth more than the arm**, because every
> function object in this repository that writes a scoped field name shares it.

The comparator's reader accepts `':'` **and** `'_'`, so a platform or
`InfoSwitch` change is a **diagnosed miss** naming both candidates, never a
silent zero. It **refuses** the suffix form `pResidual` outright — the shape the
census hunted (§12.1) — so that this file cannot repeat that defect.

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
  `<name>Residual`". **Void, and void for a deeper reason than a wrong
  separator.**

**IT IS A SHAPE DEFECT, NOT A PLATFORM DEFECT** — sharpened by `cfd-supervisor`,
2026-09-04, and the sharper statement is the one to register. The census pattern
`^[A-Za-z][A-Za-z0-9_.]*Residual$` is a **SUFFIX** matcher: it requires the name
to **end** in `Residual`. OpenFOAM writes a **PREFIX** name. **So the limb fails
under every separator, and the question of which separator is live never
arises.** Measured, not argued — the pattern run against every candidate:

| candidate | matches? | is it what v2606 writes? |
|---|---|---|
| `initialResidual:p` | **False** | **yes**, on this box |
| `initialResidual_p` | **False** | yes, on a `_WIN32` build |
| `initialResidualp` | **False** | (separator removed entirely) |
| `pResidual` | **True** | **no — the solver never writes this** |

**And the part that matters most.** The census's planted control planted
`15000/pResidual` — **a string that matches the reader's own pattern.**

> **THE PLANT WAS SHAPED LIKE THE BUG.** It therefore fired, satisfied standing
> rule 3's letter, and confirmed only that the reader can see what the reader
> expects. **That is worse than no control, because it converts an untested
> reader into one carrying a certificate.**

**A2.3's conclusion — "ITEM 2 IS A PAID RE-RUN AND CANNOT BE MADE CHEAPER BY
BORROWING A SIBLING'S FIELDS" — STANDS.** Limb 1 carries it alone: a family
whose 12 solve roots all read `writeResidualFields false` writes no spatial
field **whatever it would have been called**. `cfd-supervisor` has said he is
relying on that judgement and is carrying the correction himself, having relayed
the census upward as a measured negative.

**RULED (`cfd-supervisor`):** strike the field-name limb of §A2.3 **by quote**,
and re-run the census with `initialResidual:` **and** `initialResidual_` as both
the **pattern** and the **plant**. **Say both halves** — the conclusion survives;
its second leg does not.

**This document's own comparator is built to not repeat it**: it matches on the
prefix form, accepts both separators so a miss is *diagnosed* rather than silent,
**refuses** `pResidual` outright, and its selftest limb 2 asserts the suffix
pattern's failure against all three real candidates and its success against
`pResidual` — so the defect is pinned by an executable check, not by a paragraph.

### 12.2 🔴 OPEN PROVENANCE DEFECT — the graded rung's mesh has no build root on disk

**RULING 4, `cfd-supervisor`, 2026-09-04: this is NOT sidestepped, it is
ESCALATED. It is a finding about an ALREADY-GRADED rung, not about this arm, and
it OUTRANKS this arm.** It is recorded here so the restart's convenience cannot
bury it, and he has taken it to his own desk.

§7 of the ordering document records that the FEAS arms' mesh directory was never
identified. The same question, asked of the **graded** rung, has a worse answer.
**Measured cell counts, 2026-09-04:**

| mesh root | cells | matches the graded rung's 35,544? |
|---|---|---|
| `mesh_L1`, `mesh_L1_A1` | **31,752** | no |
| `mesh_L2`, `mesh_L2_A1` | **58,292** | no |
| `mesh_L3` | **105,712** | no |
| `mesh_A2/L1` (per §7) | **33,864** | no |
| `F28G_L1_dp1000_U20/constant/polyMesh` | **35,544** | — it is the only root carrying it |

> **THE GRADED RUNG'S MESH CANNOT BE TRACED TO ANY BUILD ROOT ON DISK.** A
> `NOT A RESULT` verdict issued at `23eeff7e` therefore rests on an object this
> lab cannot presently identify.

**What this arm does and does not do about it.** The restart inherits the rung's
**own** `constant/polyMesh` (§3.2), so the arm and the parent are guaranteed to
be talking about the same mesh — which makes the arm *internally* consistent and
**does nothing whatever to identify that mesh**. **The question is OPEN, it is
not this arm's to answer, and this arm's result inherits the defect.**

Any verdict this arm produces must carry the same qualification the parent's
does: it is a statement about a mesh whose build provenance is unestablished.

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
- **VERIFY — `run_f28_h5.sh` HAS NEVER BEEN EXECUTED, not even `--dry-run`.**
  A dry run would create a run root, and §11.1's freshness claim — that the three
  run directories do not exist — is evidence this draft depends on. So the
  launcher is verified by `bash -n`, by driving its dictionary-rewrite block
  against a **copy** of the real `controlDict` for all three modes, and by
  driving its count assertions to a refusal (§9.1). **Its guard limbs — the
  parent fingerprint, the `solve_evidence_guard` control, the virgin-directory
  refusal, the sentinel write — are verified by reading, not by running.** The
  first `--dry-run` is the right first act after check 4 and before any solver.
- **VERIFY:** `analyse_f28_h5.py` has been selftested and mutation-controlled,
  but has **never been run against a real F28 run root**, because none carrying
  residual fields exists (§12.1). Its mesh reader has not been exercised on the
  35,544-cell `polyMesh`; only on selftest fixtures.
- **VERIFY:** The cell-centre calculation is the mean of each cell's **distinct
  vertices**, not OpenFOAM's volume-weighted centroid. They agree exactly for
  hexes and differ by a fraction of a cell for the wedge and prism cells here.
  Stated in the comparator's own docstring as a bound on what the zone gate can
  claim.

**Put to `cfd-supervisor`, and RULED 2026-09-04 — recorded with the outcomes so
the questions carry their own answers:**

| # | question | ruling |
|---|---|---|
| 1 | **The restart design** (§3) — cheaper and more faithful, costs a new launcher | **APPROVED**, with the parent-immutability condition. §3.1, §3.2. |
| 2a | `ExecutionTime count == endTime − startTime` (§7 clause 5) | **APPROVED** — *"a faithful adaptation of the clause, not a weakening of it"* |
| 2b | age-guard anchor `0/T` → `0/p` (§7 clause 6) | **REFUSED AS VACUOUS.** Replaced by `RESTART_SENTINEL` with a four-sided planted control. §7.1. |
| 3 | the draft is not freezable, the grading path does not exist (§9) | **Correctly self-reported; both files ordered written.** Done, selftested, hashed. §9.1–9.4. |
| 4 | the 35,544 mesh provenance gap (§12.2) | **ESCALATED to the supervisor's own desk**, and it **outranks this arm**. |

**Still open and still not this lane's:**

- **The absence of a grid triple** (§5.5). This arm is a single-level
  localisation and issues no GCI. Not yet ruled.
- **Whether the arm runs at all** — see §14. The cost argument is spent; the
  question is now only whether the two new files are sound, which is check 4's
  business and not this lane's to certify.

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

**What would have made me cancel it — and it did not happen.** If the restart
design had been declined, the arm would have reverted to a 2,000-iteration cold
start whose relationship to the parent's plateau is an argument rather than a
construction, at roughly three times the cost, to answer a question that only
re-ranks hypotheses. **At that price and that fidelity I would have run H1's two
arms first and revisited H5 after.** The restart was approved (§13, ruling 1),
so that branch is closed.

**What would still stop it now:** the pilot failing §9.4 — if the colon in
`initialResidual:p` breaks `reconstructPar` or any downstream reader, **the arm
does not run**, and the finding is worth more than the arm, because every
function object in this repository that writes a scoped field name shares the
exposure.

---

## 15A. PILOT RESULTS — 2026-09-04. AUTHORISED BY CHECK 4; THE ARM STILL HAS NOT RUN

**Authorisation, precisely:** `cfd-supervisor` performed check 4, it passed, and
he authorised **`--dry-run` and THE PILOT ONLY**, explicitly **not the arm**,
whose cap he reserved to himself pending these numbers. **The arm has not run.
`verification/runs/F28_runs/H5A_L1_dp1000_U20` does not exist.**

### 15A.1 THE DRY RUNS — the gap between "verified by reading" and "verified by running" is closed

All three modes ran `--dry-run`, and every guard fired: the
`solve_evidence_guard` control **refused the parent as it must**, the parent
fingerprint captured **157 files**, the `controlDict` rewrite reported its
substitutions, immutability check 1/2 passed, and each stopped **before the
solver**. **The three registered run-root names remained absent** — amendment 1
did its job; only `*_DRYRUN` roots were created, and §11.1's freshness claim
survived being tested.

### 15A.2 🟢 §9.4 IS ANSWERED BY OBSERVATION. THE COLON WORKS

The registration recorded that no `initialResidual:*` file had ever been produced
on this box and that everything about it was **inferred from `IOobject.C:43-50`**.
**It is now observed:**

```
H5P_T_L1_dp1000_U20/15072/   initialResidual:Ux  :Uy  :Uz  :k  :omega  :p
```

- **All six fields written**, with a **literal colon** in the filename, exactly as
  the source predicted. `Ux`, `Uy` and `Uz` are separate fields — the wedge drops
  none, as §11.3 measured.
- **`reconstructPar` handled them**: the serial `15072/` carries all six
  reconstructed from `processor*/15072/`. **The colon breaks nothing.**
- **The comparator reported the separator it actually found:
  `residual field separator observed: [':']`** — an observation, not the
  expectation.
- **Content, read independently:** each field carries exactly **35,544** values.
  `sum|r|` = **3.546043e+01** for `p` and **7.967183e+02** for `Uy`; range
  1.251e-17 to 3.919e+00 for `p`. **Not zeros.**

**The arm's stop-condition is therefore not triggered.** Had the colon broken
`reconstructPar`, the arm would not run and that would have outranked the arm.

### 15A.3 🔴 BOTH LIMBS ARE `NOT A RESULT` — AND THE PILOT FOUND THE DEFECT THAT DID IT

**Standing rule 4 clause 4 failed on both limbs: the solution fields are absent
at `endTime`.** The comparator refused, naming all six — `U p k omega nut phi` —
and that refusal is the comparator working, not failing.

**The defect is mine, in the launcher, and it is subtle.** The top-level
`writeInterval` is compared against the **continuing `timeIndex`**, not against
the iteration count. I set it to `NITER` (72), which is correct **only when
`startTime` is 0**. On a restart the counter runs 15001…15072, and
**`15072 % 72 = 24`**, so the write **never fired at `endTime`**. Measured on
both limbs: the solution fields landed at **`15048`** — `15048 % 72 == 0`, the
one multiple in range — while `endTime` carried only the function object's
`onEnd` residual fields.

**AMENDMENT 3, before any arm compute:** top-level `writeInterval = endTime`, so
`endTime % writeInterval == 0` for any `endTime`. Verified on both modes against
a copy of the real dictionary: pilot `15072 % 15072 = 0`, arm `15200 % 15200 = 0`,
and the arm's five snapshot times remain exact (`15040/15080/15120/15160/15200`,
all divisible by 40 because 15000 is).

> **This is the pilot doing precisely what a pilot is for: it spent 0.479
> core-minutes to find a defect that would have made the arm `NOT A RESULT`.**
> **⚠ The fix is UNTESTED against a real run** — a `--dry-run` cannot exercise
> it, because the defect is in solver write behaviour, not in assembly. See
> §15A.7.

### 15A.4 🟢 THE PLATEAU CHECK PASSES — the restart design is validated by measurement

§5.7 registered a refusal: the gating `p` residual must land inside the parent's
measured last-4,000 band **[0.1171, 0.5132]** or the run did not sample the
plateau.

> **Measured: `p_initial` at iteration 15072 = `0.193576`. INSIDE the band.**

**The central claim of the restart design — that it samples the state the record
gates on rather than a proxy — is now measured rather than argued.** It was the
one thing §13's "not verified" list said was asserted "by construction".

**And amendment 2 is vindicated by a real artifact:** `solverInfo.dat` was
written to **`postProcessing/residuals/15000/`**, exactly where the original
hardcoded `/0/` would have missed it on every run.

### 15A.5 THE COST MEASUREMENT — what the pilot existed to produce

| quantity | registered estimate | **measured** | note |
|---|---|---|---|
| per-iteration rate, control | 0.056214 s/it (parent's) | **0.043111** s/it | OLS on the `ExecutionTime` series |
| per-iteration rate, treatment | — | **0.042206** s/it | |
| **`writeResidualFields` per-iteration surcharge** | allowance 2× | **NOT RESOLVABLE** | **T ran 2.1 % FASTER than C** — the effect is below run-to-run noise on a shared box |
| one-snapshot write cost | bound 4.349 s | **≈ 0.035 s** | difference of the two limbs' `ExecutionTime` tails; **the bound was ~124× conservative** |
| bytes per snapshot | 2,750,682 B | **3,595,819 B** | ratio **1.307** — the prediction was **31 % LOW** |
| `decomposePar` | 0.000 s (structural) | **0.000 s** | correctly predicted; it does not run |
| **pilot total** | **0.970** core-min | **0.479** core-min | ratio **0.494**; **10.4 % of the 4.600 cap** |

**The honest reading of the surcharge row.** The treatment limb measuring
*faster* than the control does not mean the surcharge is negative or zero. It
means **the pilot yields an UPPER BOUND, not a value** — the effect is smaller
than the noise floor of a two-run comparison on a contended box. That was
anticipated in §8's attribution rule and is recorded as the outcome, **not
rewritten as a measurement of zero.**

**A cost the pre-registration did not carry, named rather than absorbed:** case
assembly — the 23 MB copy plus **two** 157-file parent fingerprints — ≈2.4 s
single-core per limb, **17 % of actual spend**. §6.2 called it "shell" and never
costed it. The next estimate must.

**Waste: 0.000 core-min.** No run killed, none overran, none re-run.
**Calibration row landed:** `docs/COST_CALIBRATION.md`, id
`C-20260904T220239.662101Z-b467175e`.

### 15A.6 AN INSTRUMENT READING THAT IS NOT A VERDICT, AND MAY NOT BECOME ONE

Computing the concentration ratio was necessary to prove the reader works
end-to-end. It returned **f1% = 0.9979 for `p`** and **0.9719 for `Uy`**, against
a uniform-spread value of 0.0099876.

> **THIS IS NOT A RESULT AND MAY NOT BE CITED AS ONE.** It is disqualified
> **three** times over, each independently sufficient: **(1)** the run it comes
> from is **`NOT A RESULT`** on rule 4 clause 4 (§15A.3); **(2)** §5.4's
> structural bar — G1/G2/G3 each require agreement across **4 of 5** snapshots
> and this is **one**; **(3)** §5.5a — single grid, so no Roache-gated verdict is
> possible from this arm at all.

It is recorded because concealing an instrument reading is worse than stating it
with its disqualifications — and because a reader who later finds this number in
a log must find it already labelled. **The proposition P is tested by the arm,
under its five-snapshot gates, or it is not tested.**

### 15A.7 WHAT THE PILOT DID NOT ESTABLISH

- **VERIFY: amendment 3 is untested against a real run.** A `--dry-run` cannot
  exercise it. **Recommendation, and it is the supervisor's to rule:** one
  verification re-run of a single limb before the arm, ≈0.24 core-min, well
  inside the pilot's unspent 4.121 core-min. I did not do it: it would run
  compute against a grading path he has not seen, and he has already had two of
  these blobs superseded under him.
- **VERIFY: `T_rec` could not be separated from assembly.** Both sit inside the
  same 2.31 s of non-solver launcher wall. The arm's cap arithmetic below uses
  the whole 2.31 s for `T_rec`, which is conservative.
- **VERIFY: the connection limb (§5.8 limb 2) could not run.** It checks the
  **constancy** of `sum|r| / (.dat scalar)` across snapshots, and one snapshot
  has no constancy to check. Single-snapshot ratios were computed and are
  recorded for the arm to compare against — `p`: **1.831866e+02**, `Uy`:
  **7.660881e+04** — but **no constancy check was performed.**
- **VERIFY: the comparator never reached its gates**, because completion refused
  first. G1/G2/G3, the zone assignment and the cell-centre reader have still
  **never run against the 35,544-cell mesh**.

### 15A.8 THE ARM'S CAP — the formula's inputs are now measured. THE RULING IS THE SUPERVISOR'S

§6.4 registered the cap as a formula whose only free inputs are the pilot's
measurements. Substituting them, **as input to his ruling and not as a cap I am
setting**:

```
cap_wall = 200 × 0.042206 × 2.0 × 1.5   = 25.324 s   (solve, measured R_p)
         + 5 × 0.035 × 3.0              =  0.525 s   (five writes, measured W_p)
         + 5 × 2.31                     = 11.550 s   (reconstruct; T_rec NOT separable from assembly, so the whole non-solver wall is used)
         + 10 × 0.20                    =  2.000 s   (startup allowance)
                                        = 39.40 s  →  2.63 core-min at 4 ranks
```

**Plus case assembly**, which the formula omits and §15A.5 names: ≈2.4 s
single-core, **0.04 core-min**. **Arm cap ≈ 2.67 core-min**, against an expected
spend the measured rate now puts near **1.0 core-min**.

**I am not setting this cap.** `cfd-supervisor` reserved it. The arithmetic is
here so his ruling has its inputs on the record beside it.

---

## 15B. ADDENDUM — 2026-09-04. THE POST-COMPUTE GRADING-PATH AMENDMENT, PUT ON THE RECORD FOR JUDGEMENT

**This addendum alters no gate, no threshold, no cap and no label.** It exists
because `cfd-supervisor` ruled that a grading-path change made *after* the run
**"is the single highest-risk amendment there is, because it is the exact shape
of choosing the instrument to fit the answer"**, and set five things that must be
shown for it to be lawful. Each is answered below, with the check, not the claim.

**On the state he read.** He read HEAD `967e46ef`, where the registration was
uncommitted and `bf9d5899…` existed nowhere. **That was a real transient window
in my working tree and he was right to stop on it.** It is closed at `0b8696f8`.

### 15B.1 DEMAND 1 — NAME THE CHANGE EXACTLY, AS A DIFF

The pilot ran between commit `915ab504` (the pre-compute freeze) and `0b8696f8`.

**The GRADER did not move. `git diff 915ab504 HEAD -- analyse_f28_h5.py` is
EMPTY — not one byte.**

**The LAUNCHER moved by one functional line:**

```diff
 src = sub_once(src, "writeInterval   15000;",
-                    "writeInterval   %s;" % niter, "top-level writeInterval")
+                    "writeInterval   %s;" % t1, "top-level writeInterval")
```

plus the comment block recording why. **That is the entire post-compute change to
the frozen set.**

### 15B.2 DEMAND 2 — WAS IT FORCED BY A MECHANICAL FACT, NOT BY A NUMBER?

**Yes, and it is checkable in two independent ways.**

**(a) The fact that forced it is arithmetic, not a measurement.** The top-level
`writeInterval` is compared against the **continuing `timeIndex`**. On a restart
that counter runs 15001…15072, and **`15072 % 72 = 24 ≠ 0`**, so the write never
fired at `endTime`. `15072 % 72` is not an observation about the flow, about a
residual, or about anything a choice could favour. The corrected form,
`writeInterval = endTime`, gives `endTime % endTime == 0` for **every** endTime —
it is the unique fix that is independent of the iteration count.

**(b) The change CANNOT move any gate, and this is verifiable by inspection.**
Amendment 3 changes only **when the solution fields `U p k omega nut phi` are
written**. In `analyse_f28_h5.py` those six fields are read at **exactly one
line** — inside `completion()` — and **nowhere else**. Every gate path
(`age_guard`, the separator report, and the grading loop) reads only
`residual_field_path(...)`, i.e. `initialResidual:*`. **The residual fields were
already written correctly at `endTime` by the function object's own `onEnd`,
which amendment 3 does not touch.**

> **So the amendment can move a run from FAILING rule 4 clause 4 to SATISFYING
> it, and it can do nothing else. It cannot move `f1%`, cannot move a zone
> assignment, cannot change which cells count, and cannot change a threshold.**

**And the thresholds are demonstrably unmoved.** Byte-identical at the
comparator's birth commit `ecc2dec9`, at the pre-compute freeze `915ab504`, and
at HEAD:

```
N_CELLS = 35544 · N_TOP = int(0.01 * N_CELLS) = 355
G1_CONCENTRATION = 0.50 · G2_ZONE_MASS = 0.60 · G3_MIN_SNAPSHOTS = 4
PLATEAU_LO, PLATEAU_HI = 0.1171, 0.5132
ARM_SNAPSHOTS = [15040, 15080, 15120, 15160, 15200]
```

`zone_of()` diffs **IDENTICAL** between `915ab504` and HEAD — **no zone boundary
moved.** Nothing in his forbidden list — a threshold, a zone definition, a mass
fraction, the 0.50, the 0.60, which cells count — changed at any point after
first compute. **Nothing needs striking.**

**(c) The answer-fitting worry is RETIRED, not argued — `cfd-supervisor`'s
formulation, which is stronger than either of ours and belongs on the record.**

> **The observed `f1%` for `p` was 0.9979 against a threshold of 0.50**, with
> uniform spread at 0.0099876. §5.2 already committed, before any compute, that
> **any threshold between roughly 0.05 and 0.8 separates the same two worlds.**
> **So the measurement is not a close call at ANY threshold in that range, and
> no post-hoc choice of threshold could have changed the G1 outcome.**

That is what makes the freeze unfalsifiable here: **not our assurances about it,
but the distance between the reading and every threshold we could have chosen.**
A registration whose gate survives this test is one a reader need not take on
trust. *(Note that this concerns the G1 threshold only. §15C.2 records a defect
in what the gate MEASURES, which no choice of threshold repairs.)*

### 15B.3 DEMAND 3 — WAS THE PILOT'S OUTPUT VISIBLE WHEN I MADE THE CHANGE?

> **YES. And more than the output he had in mind: I had ALREADY COMPUTED
> `f1% = 0.9979` for `p` and `0.9719` for `Uy` before I wrote amendment 3.**

The order of my actions, stated so a reader can judge rather than take my word:

| # | action |
|---|---|
| 1 | ran the pilot control limb |
| 2 | ran the pilot treatment limb; saw `15072/` held only residual fields |
| 3 | diagnosed the `15072 % 72 = 24` defect; saw solution fields at `15048` |
| 4 | ran the comparator — `NOT A RESULT`, six solution fields missing |
| 5 | **read the residual field content directly, computing `f1% = 0.9979`** |
| 6 | **wrote amendment 3** |

**I made the change with the concentration number in view.** §15B.2 is why it is
nonetheless lawful — the change cannot reach that number by any path — but the
disclosure is owed regardless of the defence, and the defence is worth nothing
without it. Had I written amendment 3 at step 3, before step 5, the disclosure
would have been cleaner; **I did not, and I am not going to describe the sequence
as though I had.**

### 15B.4 DEMAND 4 — THE FROZEN BLOB MUST BE COMMITTED

**Discharged.** `git cat-file -t bf9d5899148d6af88c8544c4844169f7b45b4f7d` →
`blob`. The registration is committed and clean (`9d84a9bd`).

**And the stronger property, checked rather than assumed: no commit in this
document's history has ever named a blob it did not contain.**

| commit | §9.3 names | actual blob in that commit |
|---|---|---|
| `915ab504` | `929dba14…` | `929dba14…` ✓ |
| `0b8696f8` | `bf9d5899…` | `bf9d5899…` ✓ |

### 15B.5 DEMAND 5 — THE ORDERING, DISCLOSED

**What I did, both times:** edited the file → hashed the worktree file → wrote
that hash into §9.3 → **committed the file and the registration together in one
commit**.

**So:** at every *committed* state the freeze can fire, because the blob and the
registration naming it enter the tree in the same commit. **But in the working
tree, between the hash being written and the commit landing, the registration
named an object that did not yet exist** — the exact window he observed. His
observation was correct and my workflow produced it.

**The weakness is real and is not defended.** A registration is only checkable at
commit granularity under this workflow, and "checkable only at commit
granularity" is precisely the property that let an unverifiable state exist and
be read. **The ordering he prescribes — commit the file FIRST, then record the
blob in a SECOND commit — removes the window entirely and is what I will use for
any further change to this document's frozen set.** It costs one extra commit and
buys a freeze that is checkable continuously rather than only at landing.

### 15B.6 CONTENTION — asked for explicitly, and reported rather than buried

He recorded three foreign `rhoPimpleFoam` ranks at 99.9 % under `timeout 900` at
**22:00Z**, load 3.33 on 16 vCPUs, in ansys-verification's lane trees.

**My pilot did not overlap them, on the evidence available — and I cannot prove
a negative about processes I never saw.**

| fact | value |
|---|---|
| my box reading before launching | **21:55:03Z**, load **1.49** on 16 cores, **no** foreign solver in `pgrep` |
| control limb finished | **21:58:28Z** |
| treatment limb finished | **21:58:47Z** |
| his observation | **22:00Z** — **73 s after my pilot ended** |
| nearest ansys VMFL034-R2 artifacts on disk | **22:04:12Z**, **22:05:50Z** — over 5 minutes later |

**Positive internal evidence against overlap:** both limbs measured **~25 %
FASTER** per iteration than the parent (0.043111 and 0.042206 s/it against
0.056214). **Contention slows a run; it does not speed one.** A limb sharing the
box with three ranks at 99.9 % would show the opposite sign.

**VERIFY — the honest limit:** no `log.rhoPimpleFoam` was found under
`verification/runs/ansys_verification/`, so I could not read that run's own start
time; and **fleet agents are invisible to `pgrep` (L-41)**, so my 21:55 sweep
cannot prove nothing was running. **The attribution therefore records contention
as NOT DETECTED AND NOT EXCLUDED**, and the calibration ledger carries that in
those words rather than resolving it in the ratio.

---

## 15C. VERIFICATION LIMB — 2026-09-04. AMENDMENT 3 IS PROVED, AND THE PILOT FOUND A DEFECT IN THE GATE ITSELF

**Authorised by `cfd-supervisor` ruling 1 after check 1 passed on amendment 3.**
Run root `H5P_V_L1_dp1000_U20`, mode `pilot-verify` (amendment 4, additive only:
byte-for-byte the `pilot-treatment` configuration, differing only in run-root
name because `H5P_T` is spent and the virgin guard refuses an existing root).
**Write cadence only; no physics claim. The arm has not run.**

**The ordering `cfd-supervisor` prescribed at §15B.5 was used for the first time
here: the launcher was committed ALONE, and its blob `f3534f1b…` was recorded in
§9.3 in a LATER commit.** There was no window in which this registration named an
object that did not exist.

### 15C.1 🟢 AMENDMENT 3 IS VERIFIED BY RUNNING, NOT BY READING

**The solution fields land at `endTime`.** `H5P_V_L1_dp1000_U20/15072/` now holds
`U p k omega nut phi uniform` **together with** all six `initialResidual:*`
fields, and `processor0/` holds **`0`, `15000`, `15072` and nothing else** — the
stray `15048` write is gone, so the write fires **once, at endTime**.

**The comparator cleared strict completion for the first time**, reached and
passed the sentinel age guard, and ran the gates. Every clause of §7 that failed
on the two spent limbs now passes. **The fix that "a dry run structurally cannot
test" is tested.**

**Contention, measured rather than assumed.** This limb ran at 22:10Z **alongside
one to two foreign `rhoPimpleFoam` ranks at ~100 %** (ansys-verification's L2/L3
probes under `timeout 3000`), load 2.83 on 16 cores — against the two spent limbs
which ran at 21:57–21:58Z on an idle box. Measured per-iteration rates:

| limb | box | slope |
|---|---|---|
| `H5P_C` | idle | 0.043111 s/it |
| `H5P_T` | idle | 0.042206 s/it |
| `H5P_V` | **2 foreign ranks at ~100 %** | **0.042399 s/it** |

**Contention cost: not detectable at 4 ranks against 2 foreign ranks on a
16-core box** — `V` sits between the two idle-box limbs. Recorded as a
measurement, not as an absence of concern.

### 15C.2 🔴 THE GATE AS FROZEN CANNOT DISCRIMINATE. THE RESIDUAL RANKING IS DOMINATED BY CELL VOLUME

**This is the finding, and it outranks the arm.**

The comparator reached G2 and returned **`Z-ELSEWHERE` at 1.000 — all 355 top
cells, for both `p` and `Uy`.** The top cells sit at **x ∈ [−2.295, 6.271],
r ∈ [0.445, 3.562]**, with the argmax at **x = −2.295, r = 3.562** — the outer
corner of the farfield. The domain runs to r = 3.75; **the duct sits at
r ≈ 0.117–0.152.** The residual is concentrated **20–30× further out in radius
than any named feature**, and **none of Z-DISK / Z-DUCT / Z-HUB / Z-AXIS covers
where it lives.**

**The mechanism, and it is in the source I already quoted.** `GAMGSolverSolve.C`
sets `finestResidual = tsource() - Apsi` — the **un-normalised** residual of the
discretised equation. In a finite-volume discretisation each cell's equation is
integrated over its own volume, **so `|r|` scales with cell volume.** Ranking
cells by `|r|` therefore ranks them substantially **by size**.

**Measured on this mesh, from the artifacts:**

| check | value |
|---|---|
| Spearman rank correlation, `abs(residual)` vs cell size | **ρ = +0.8034** |
| median cell size of the top-355 by residual | 6.683549e-03 |
| median cell size, all 35,544 cells | 3.796746e-08 |
| **ratio** | **176,034×** |
| overlap: top-355-by-residual ∩ top-355-by-size | **248 of 355** |

**And normalising by cell size moves the answer to a completely different
place:** `f1%` becomes **0.7175** and the zone tally becomes **Z-DUCT 189,
Z-HUB 147, Z-ELSEWHERE 16, Z-DISK 3** — the duct and the centrebody, which are
the physically meaningful regions H5 was built to discriminate among.

> **CONSEQUENCE FOR THE ARM: as frozen, G2 would have returned `Z-ELSEWHERE`
> with near-certainty, and that answer would have been an artifact of cell
> volume rather than a statement about the flow. H5's entire purpose is to
> discriminate among H1–H4, and the frozen gate is structurally incapable of
> it.** The pilot cost **0.24 core-minutes** and found this **before** the arm
> spent its 2.67.

**I HAVE CHANGED NOTHING.** Normalising the residual, or reweighting which cells
count, is squarely inside `cfd-supervisor`'s forbidden list — *"a threshold, a
zone definition, a mass fraction, the 0.50 or the 0.60, or which cells count"* —
and this is **after first compute**, with the output in view. **It is referred,
not fixed.** The normalised figures above are recorded as a **diagnostic from a
`NOT A RESULT` run**, triple-disqualified exactly as §15A.6 requires, and they
are **not** a proposed new gate; they are the evidence that the frozen one is
broken.

**VERIFY — what this does NOT establish.** That the volume-normalised residual is
the *right* quantity is **not** established here. It is one obvious candidate;
`|r|` per unit volume, `|r|` scaled by the diagonal, and a normalisation matching
`normFactor` are others, and choosing among them **after seeing which zones each
favours is precisely the answer-fitting the freeze exists to prevent.** Any
replacement gate must be registered before the run that tests it.

### 15C.3 🔴 A SECOND DEFECT: THE COMPARATOR EMITS A FALSE PHYSICS CLAIM FROM A COUNTING SHORTFALL

Also referred, also not fixed. On this limb the comparator printed:

> `G1 GATE FAIL: concentrated in 1 of 1 snapshots, threshold 4. The plateau
> residual is DIFFUSE.` … `evidence AGAINST H4`

**`f1%` was 0.9979.** The residual is the *most concentrated reading possible* —
and the comparator called it **DIFFUSE** and turned that into **evidence against
a hypothesis**, because the *snapshot count* fell short of four.

**The verdict `GATE FAIL` is correct** — the gate genuinely is not satisfied. **The
attributed reason and the physics gloss are false.** The code conflates three
distinct outcomes: *diffuse*, *concentrated but unstable across snapshots*, and
*too few snapshots to judge*. Only the first supports the H4 gloss.

This is the shape this lab hunts in the opposite direction from usual: not
bookkeeping voiding physics, but **bookkeeping MANUFACTURING a physics
statement.** It is live on the arm's path too — 3-of-5 concentrated snapshots
would print "DIFFUSE" and "evidence against H4" for a residual that is anything
but. **Referred to `cfd-supervisor` with §15C.2; a grader change post-compute is
his ruling, not mine.**

### 15C.4 THE ARM'S CAP — SET BY THE SUPERVISOR AT 2.67 CORE-MIN

**RULED (ruling 2):** the arm's cap is **2.67 core-min**, at the §15A.8 figure,
unpadded. **An overrun stops the arm; it does not get a new budget.**

> **REGISTERED IN TERMS, as he required: THE PER-ITERATION SURCHARGE IS AN UPPER
> BOUND AND NOT A VALUE.** The treatment limb measured **2.1 % faster** than the
> control, which is below run-to-run noise. **This cap therefore rests on a
> bound, and it may never later be cited as though it rested on a measured
> surcharge.**

**But the arm does not run on this cap yet:** §15C.2 must be settled first, or the
2.67 core-min buys an answer that is an artifact of the mesh.

### 15C.5 RUN ROOTS — WHAT IS ON DISK AND UNTRACKED (ruling 3)

`cfd-supervisor` ruled: commit the evidentiary artifacts, not the bulk, and
**record the exact paths of the bulk and state plainly that they are on disk and
untracked**, so that no citation points at a path a reader cannot find and cannot
tell was never tracked.

**ON DISK AND DELIBERATELY UNTRACKED — the duplicated mesh and `processor*`
trees:**

```
verification/runs/F28_runs/H5P_C_L1_dp1000_U20/processor{0,1,2,3}/     ~15 MB
verification/runs/F28_runs/H5P_T_L1_dp1000_U20/processor{0,1,2,3}/     ~15 MB
verification/runs/F28_runs/H5P_V_L1_dp1000_U20/processor{0,1,2,3}/     ~15 MB
verification/runs/F28_runs/H5P_C_L1_dp1000_U20_DRYRUN/                  23 MB
verification/runs/F28_runs/H5P_T_L1_dp1000_U20_DRYRUN/                  23 MB
verification/runs/F28_runs/H5A_L1_dp1000_U20_DRYRUN/                    23 MB
```

These are **copies of `F28G_L1_dp1000_U20`'s mesh and 15000 state** and carry no
information the parent does not already carry in git. `CLAUDE.md` already puts
data too large for git outside it; the lab's rule is that a number cites an
artifact **still on disk**, not that every byte enters git. **Every number in
§15A and §15C cites a path in this list or a committed one.**

---

## 15D. 🔴 DISPOSITION — 2026-09-04. THE H5 ARM AS FROZEN IS `NOT A RESULT`: ITS MEASURAND IS CONFOUNDED

**RULED by `cfd-supervisor`, 2026-09-04, in these words. The arm does not run.**

> **THE H5 ARM AS FROZEN IS `NOT A RESULT` — ITS MEASURAND IS CONFOUNDED,
> ESTABLISHED PRE-ARM.**

**The basis, and it is three mutually corroborating measurements rather than one
statistic wearing three hats** (§15C.2):

| # | measurement | value |
|---|---|---|
| 1 | Spearman ρ, `abs(residual)` vs cell size | **+0.8034** |
| 2 | median cell size of the top-355 ÷ median of all 35,544 | **176,034×** |
| 3 | overlap, top-355-by-residual ∩ top-355-**by size** | **248 of 355** |

with the top cells at **r ∈ [0.445, 3.562]** — the farfield — against a duct at
**r ≈ 0.117–0.152**.

**Why it is confounded, from the source and not from the statistics.**
`GAMGSolverSolve.C` sets `finestResidual = tsource() - Apsi`, **un-normalised**;
in a finite-volume discretisation each cell's equation is integrated over its own
volume, so `|r|` **carries cell volume**. *A gate whose outcome is determined by
cell volume is not measuring where the residual lives; it is measuring where the
big cells are.* **No threshold on that quantity can rescue it.**

### 15D.1 THIS DISPOSITION IS NOT A GATE CHANGE, AND IT IS NOT A `GATE FAIL`

**It is not a gate change.** Rule 2 closed these gates at first compute; neither
the supervisor nor this lane may alter G2, and normalising the residual is
*"which cells count"* — inside the forbidden list, after first compute, with the
output in view. **Nothing here alters a threshold, and nothing manufactures a
pass.** Declining to *spend compute on an instrument already shown to be
confounded* changes no gate: it withholds a run.

**It is not a `GATE FAIL`, and must never be recorded as one.** **The gate never
ran.** Nothing about H5's actual proposition — where the residual sits — was
tested. Running the arm as frozen would have burned 2.67 core-min to obtain a
`Z-ELSEWHERE` that was already predictable and already known to be an artifact,
and would have placed that answer on the record where a later reader might cite
it. *"I would rather have no number than that number."*

### 15D.2 WHAT §2.1's PROPOSITION P NOW STANDS AT

**P is UNTESTED.** Not refuted, not supported. The instrument built to test it
was found, before it was used, to measure a quantity that answers a different
question. §5.2's G1 threshold was never the weak point — §15B.2(c) shows the
reading clears it by a factor that no threshold choice could reverse. **The weak
point was the measurand**, and it was invisible until a real field existed on
disk to look at.

**The cost of finding out: 0.245 core-minutes**, against the 2.67 the arm would
have spent. **That is the pilot doing exactly what a pilot is for, and it is a
better outcome than the arm passing.**

### 15D.3 THE SUCCESSOR IS A NEW PRE-REGISTRATION, NOT AN ADDENDUM TO THIS ONE

**This document's gates are closed and stay closed.** The replacement
discriminator is registered in a **new** document, frozen **before** the run that
tests it. **No part of it may be smuggled in here as an addendum.** §15E records
why that document has not yet been written.

---

## 15E. 🔴 REFERRAL — THE RULED REPLACEMENT IS PROVABLY INERT AGAINST THE DEFECT IT WAS CHOSEN TO CURE

**No gate, threshold, cap or label is altered by this section. It reports a
measurement and refers a decision. The successor pre-registration is HELD.**

`cfd-supervisor` ruled the replacement discriminator to be the
**`normFactor`-matched normalisation**, on the principle — correct, and not in
question here — that the choice must be **forced by the arm's founding argument
rather than selected from candidates by inspecting which zones each favours.**

**I checked the ruled quantity before building an instrument around it. It does
not do what it was chosen to do.**

### 15E.1 THE MEASUREMENT

`lduMatrix::normFactor` is a **single global scalar per solve** — a `gSum`, not a
field. Implied on this limb: `sum|r| / (.dat scalar) = 183.186560`.

| quantity | value |
|---|---|
| `f1%`, RAW field | **0.9979393588** |
| `f1%`, `normFactor`-MATCHED field | **0.9979393588** |
| difference | **0.000e+00** |
| same 355 cells selected? | **True** |
| sum of the matched field | 0.1935755234 |
| the `solverInfo.dat` scalar | **0.1935755234** ← commensurability restored exactly |

> **Dividing every cell by one global scalar is a uniform rescale. `f1%` is
> scale-invariant and the cell ranking is unchanged. `normFactor`-matching
> RESTORES COMMENSURABILITY EXACTLY AND REMOVES NONE OF THE CELL-VOLUME
> CONFOUND. G2 would still return `Z-ELSEWHERE`.**

### 15E.2 WHY — TWO DIFFERENT PROBLEMS WERE BEING SOLVED BY ONE CHOICE

- **Commensurability** — *does the field tie to the number the record already
  carries?* `normFactor`-matching answers this, exactly, and it is what §5.8's
  connection limb tests.
- **Confounding** — *does the ranking reflect the physics or the cell sizes?*
  `normFactor`-matching cannot touch this, because a global scalar cannot
  reorder cells.

**The founding argument compels the first and is silent on the second.** It
justifies **reading the field** — `solverInfo.dat` holds the global sum and
nothing on disk supplies the spatial numerator. It does not, by itself, select a
**ranking** quantity.

### 15E.3 THE RESOLUTION I PROPOSE — AND THE DISCLOSURE THAT MUST TRAVEL WITH IT

**The two roles need not use the same quantity, and separating them keeps the
founding argument intact:**

1. **The CONTROL keeps the RAW field**, `normFactor`-matched — its constancy
   across snapshots is the falsifier `cfd-supervisor` identified, and it remains
   exactly as ruled. If `sum|r|/(.dat scalar)` is not constant, the
   commensurability claim is false and the arm's founding argument fails with it.
2. **The GATE quantity becomes the residual DENSITY, `r_c / V_c`**, on a **real**
   cell volume.

**The principle that forces (2), stated without reference to any outcome:** `r_c`
is the residual of the cell's equation **integrated over that cell's volume**, so
it carries units of [equation × volume]. `r_c / V_c` is the residual **density** —
the quantity whose spatial distribution is a property of the solution rather than
of the discretisation, and the only one of the two whose ranking is meaningful
across cells of different size. **That is dimensional reasoning, available before
any run and independent of which zones it favours.**

> ⚠ **DISCLOSURE, owed and given: I HAVE SEEN THE OUTCOME OF (2).** §15C.2 records
> that volume normalisation moves the zone tally to Z-DUCT 189, Z-HUB 147,
> Z-ELSEWHERE 16, Z-DISK 3. **So this proposal is NOT outcome-blind, whatever its
> principled motivation, and `cfd-supervisor` must weigh it knowing that.** I
> state the principle because I believe it would have forced the same choice
> before any run — **not as a claim that it did.**

### 15E.4 WHY THE SUCCESSOR PRE-REGISTRATION IS HELD RATHER THAN WRITTEN

`cfd-supervisor` directed that a new pre-registration be written and frozen
before the run that tests it. **I have not written it, and the reason is §15E.1:
building an instrument around a quantity I can demonstrate is inert against the
defect it exists to cure would be building a known-broken instrument** — the same
error as the arm, repeated one level up, at greater cost because a frozen
document is harder to retire than a draft.

**What the successor needs before it can be written, and none of it is mine to
decide:**

- **the ranking quantity** — `r_c/V_c`, or another, ruled on the principle, not
  on the tally;
- **a real cell volume.** His condition, and my own VERIFY: the vertex
  bounding-box proxy is adequate to establish ρ = +0.8034 and a 176,034× ratio,
  and **inadequate as a gate quantity**. OpenFOAM's own `V()` via
  `postProcess -func writeCellVolumes` is the obvious source and costs seconds;
- **whether the zone envelopes survive.** They were drawn around the duct, disk,
  hub and axis. If the successor's residual density concentrates elsewhere, the
  same coverage failure recurs in a new document — **the zones must be shown to
  cover where the successor's quantity actually lives, before that gate is
  frozen, not after.**

---

## 15F. PREREQUISITES 2 AND 3, MEASURED — 2026-09-04. THE SUCCESSOR IS STILL NOT WRITTEN

**No gate, threshold, cap or label is altered.** `cfd-supervisor` accepted the
§15E refutation **as his error, not as a refinement**, ruled the role separation,
and directed that prerequisites 2 and 3 be established **as measurements** before
any successor is drafted. They are below. **Instrument:**
`cases/F28_DUCTED_ACTUATOR_DISK/f28_h5_coverage_probe.py`, blob
`a34be22ed89ea8f9db606f0eaee8d7ee5981df17`, committed before this record.

**Compute: 0.25 s single-core `postProcess` = 0.004 core-min**, run in the
already-scratch `H5A_L1_dp1000_U20_DRYRUN` root so that **no evidence-bearing run
root was touched.**

### 15F.1 PREREQUISITE 2 — REAL CELL VOLUMES, AND HOW WRONG THE PROXY WAS

From `postProcess -func writeCellVolumes` (artifact
`verification/runs/F28_runs/H5A_L1_dp1000_U20_DRYRUN/0/V`, **on disk and
untracked** — it is derived from the tracked parent mesh and regenerates in
0.25 s by that command):

| | |
|---|---|
| real cell volume, min / median / max | 1.406118e-16 / 2.870220e-08 / **4.687060e-02** |
| **max / min ratio** | **3.333e+14 — fourteen orders of magnitude** |

**That is far past the 176,034× the bounding-box proxy showed**, and it makes the
dimensional argument stronger than when it was made: raw `r_c` compares
quantities integrated over cells differing by 10¹⁴ in volume.

**The proxy, quantified against real `V`:** Spearman **+0.9843**, but the
`proxy/real` ratio ranges **1.000 → 416.544**. **It ranks well and scales
badly** — exactly adequate for the rank correlation that convicted the frozen
gate, and exactly inadequate as a gate quantity. **Not carried forward**, as
ruled. Both halves of my own VERIFY are now measured rather than asserted.

### 15F.2 PREREQUISITE 3 — COVERAGE. SATISFIED FOR `p`, FAILED FOR `Uy`

All three candidates reported together, which is how the supervisor ruled the
non-blindness of the density proposal is discharged: **a selection made with the
outcome in view is laundered by hiding the alternatives and discharged by
publishing them.**

| field | candidate | `f1%` | **covered by named zones** | top zones |
|---|---|---|---|---|
| `p` | raw | 0.9979 | **0.0000 — UNCOVERED** | Z-ELSEWHERE 1.000 |
| `p` | `normFactor`-matched | 0.9979 | **0.0000 — UNCOVERED** | Z-ELSEWHERE 1.000 |
| `p` | **density `r_c/V_c`** | 0.6496 | **0.9970 — COVERED** | Z-DUCT 0.526, Z-HUB 0.471 |
| `Uy` | raw | 0.9719 | **0.0000 — UNCOVERED** | Z-ELSEWHERE 1.000 |
| `Uy` | `normFactor`-matched | 0.9719 | **0.0000 — UNCOVERED** | Z-ELSEWHERE 1.000 |
| `Uy` | **density `r_c/V_c`** | 0.3537 | **0.2492 — UNCOVERED** | Z-ELSEWHERE 0.751, Z-DUCT 0.234 |

**Three things follow, and the second is the one that justifies the whole
prerequisite.**

1. **The inertness of `normFactor`-matching is confirmed a second time and
   independently** — identical `f1%` and identical coverage to raw, on both
   fields.
2. **🔴 PREREQUISITE 3 IS SATISFIED FOR `p` AND FAILS FOR `Uy`.** The named zones
   cover where `p`'s residual density lives (99.70 %). They do **not** cover
   `Uy`'s: **258 of 355 top cells and 75.1 % of the mass fall outside every
   envelope**, spread over x ∈ [−0.030, 2.513], r ∈ [0.116, 3.213], with the
   largest at x = 0.19999, **r = 2.898**. That is **real spread, not a boundary
   artifact**. **Freezing a successor gate on `Uy` with these zones would
   reproduce the identical defect in a new document** — which is precisely what
   the coverage prerequisite exists to prevent, and it caught it before the
   document existed.
3. **A smaller finding worth an envelope fix.** `p`'s only **2** uncovered cells
   sit at **x = −0.0000, r = 0.13973** — the **duct leading edge**. `Z-DUCT`
   starts at exactly `x ≥ 0.0000` and those centroids round a hair negative, so
   they are clipped by **boundary precision, not by physics**. A successor
   envelope should begin slightly upstream of the duct.

### 15F.3 A CONSEQUENCE FOR THE SUCCESSOR'S THRESHOLDS, FLAGGED AND NOT ACTED ON

Under density, `p` splits **Z-DUCT 0.526 / Z-HUB 0.471**, so **no single zone
reaches the frozen G2 threshold of 0.60** — the frozen rule would return
`MULTI-ZONE`. And `Uy`'s density `f1%` of **0.3537** falls **below** the frozen
G1 threshold of 0.50.

**Whether that means the threshold, the zones, or the H1–H4 mapping needs
rework is `cfd-supervisor`'s ruling. I have touched none of them**, and I record
the numbers here so that whatever he rules is ruled against facts. **Note that
these figures come from a single snapshot on a `NOT A RESULT` run** and cannot
support a physics conclusion; they bear on instrument design only.

### 15F.4 THE PLANTED CONTROL ON THE COVERAGE TEST ITSELF

A coverage test that could not report **uncovered** would certify the exact
failure it exists to catch. `--selftest`, all eight fired:

- a concentration placed **outside every named envelope** is reported
  **UNCOVERED** and attributed to `Z-ELSEWHERE` — **not silently binned as
  though that were an answer**;
- the **same** concentration moved **inside `Z-DUCT`** is reported **COVERED**;
- the two limbs must **differ** by more than 0.98;
- a **half-in/half-out** plant reports ≈0.5, not 0 or 1;
- an **all-zero** field is **REFUSED**, not reported as zero coverage.

### 15F.5 WHAT IS STILL NOT ESTABLISHED

- **VERIFY:** all coverage figures come from **one snapshot** of a `NOT A RESULT`
  run. Whether `p`'s density coverage or `Uy`'s failure is **stable across
  snapshots** is untested — and stability is exactly what G3 exists to test.
- **VERIFY:** cell **centres** are still the vertex mean, not OpenFOAM's
  volume-weighted centroid. Real volumes are now used for the *quantity*; the
  *zone assignment* still uses the approximate centre. `postProcess -func
  writeCellCentres` would close it and has not been run.
- **VERIFY:** no alternative zone set has been tested for `Uy`. Whether **any**
  envelope covers `Uy`'s density is open, and a zone set drawn to cover it
  **after** seeing where it lies would be the fitting this campaign has twice
  now avoided.
- **A judgement flagged for ruling rather than made silently:** I did **not**
  file a `COST_CALIBRATION.md` row for the 0.004 core-min, judging a prerequisite
  measurement not to be a rung, case or curriculum item completing. If that
  reading of rule 12 is wrong, the row is owed.

---

## 15G. PART 4 DISCHARGED, AND BOTH HALVES CAME BACK DIFFERENT FROM THE RULING — 2026-09-04

**No gate, threshold, cap or label altered. The successor is still not drafted;
§15G.4 says why, and it is a different reason from last time.** Compute: two
`postProcess` calls, **0.54 s total = 0.009 core-min**, in the already-scratch
DRYRUN root.

### 15G.1 PART 4(b) — `writeCellCentres` RUN. THE APPROXIMATE CENTRE CHANGED NOTHING

`postProcess -func writeCellCentres`, 0.29 s. Comparing OpenFOAM's real
volume-weighted centres against my vertex-mean approximation:

| | |
|---|---|
| centre displacement, max / median | 3.165971e-03 / 6.349223e-06 |
| **cells whose ZONE ASSIGNMENT changes** | **0 of 35,544** |
| coverage, `p` density, with REAL centres | **0.9970** — Z-DUCT 0.5262, Z-HUB 0.4707 |

**Identical to the approximate-centre figure to four decimals.** His concern was
exactly right in principle — *"a coverage figure computed from approximate
centres cannot certify an envelope"* — and the answer is that this one happens to
be unaffected. **That is now measured rather than assumed**, which is the whole
point of running it, and the VERIFY is discharged rather than argued away.

### 15G.2 🔴 PART 4(a) — NO EPSILON IS WARRANTED. MY OWN CHARACTERISATION WAS WRONG

He ruled the leading-edge clip *"allowed, as a precision tolerance and not a
boundary move"*, with the epsilon *"derived from the coordinate precision"*. **He
ruled that on my words — I wrote that the centroids "round a hair negative" — and
those words were wrong.**

**Measured.** The two clipped cells sit at real centres

```
x = -2.513737320e-06     and     x = -1.526503059e-05     (both at r = 0.139729)
```

and the `Cx` values straddling the duct leading edge form a **continuum**:
`+7.136e-07, -2.514e-06, +2.771e-06, -4.802e-06, +4.843e-06, +5.147e-06 …`

**These cells do not round negative. They ARE negative.** The mesh resolves the
leading edge at ~10⁻⁶ m and there is a real, ordered sequence of cells on both
sides of `x = 0`. Double-precision resolution at that magnitude is **5.50e-22**;
the clipped cells sit **10¹⁵–10¹⁶ times** coarser than that. **There is no
precision ambiguity to absorb.**

> **So an "epsilon justified by centroid precision" would be a FICTION — it would
> be a boundary move wearing arithmetic's clothes, which is precisely the
> distinction he drew when he said the two "would look identical in a diff".**
> The honest disposition is the third option neither of us listed: **change
> nothing.** `Z-DUCT` is defined from `x ≥ 0`, the duct leading edge; two cells
> immediately upstream of it carry **0.3 %** of the top-1 % mass and are
> **correctly** reported as outside. 0.3 % is immaterial to any gate, and the
> zone definition is right as it stands.

**Recorded as my error propagating into a ruling.** He authorised a repair on a
description I gave him, and checking the coordinates rather than re-reading my
own sentence is what caught it.

### 15G.3 THE NULLS — AND THE TWO NULLS DIFFER BY FOUR ORDERS OF MAGNITUDE

He directed that the null be *"what each zone would carry under uniform density —
its VOLUME FRACTION"*. **There are two distinct nulls and they belong to
different statistics**, so both are published:

| zone | cells | **count fraction** | **volume fraction** |
|---|---|---|---|
| Z-DISK | 700 | 0.019694 | 1.663321e-06 |
| Z-DUCT | 8,923 | 0.251041 | 3.767350e-05 |
| Z-HUB | 4,405 | 0.123931 | 3.115737e-06 |
| Z-AXIS | 3,350 | 0.094249 | 9.009345e-05 |
| **Z-ELSEWHERE** | 18,166 | 0.511085 | **0.9998675** |

- **Volume fraction** is the null for a share of **total residual mass** — and it
  independently re-explains the original failure: **Z-ELSEWHERE is 51 % of the
  cells and 99.99 % of the volume**, so a volume-carrying quantity lands there by
  construction.
- **Count fraction** is the null for the successor's actual statistic — a share
  of the **top-N-by-density** mass — because under uniform density every cell
  ties and the top-N is an arbitrary subset, so each zone's expected share is its
  share of **cells**.

**The gate statistic needs the count null, not the volume null.** Flagged rather
than silently substituted.

### 15G.4 🔴 THE MEASUREMENT THAT CHANGES THE SUCCESSOR'S FEASIBILITY

Observed against null, `p` density, real centres:

| statistic | observed | null | **× null** |
|---|---|---|---|
| **f1% (concentration)** | 0.6496 | 0.009988 | **65.04×** |
| Z-DUCT share | 0.5262 | 0.251041 | **2.10×** |
| Z-HUB share | 0.4707 | 0.123931 | **3.80×** |
| NAMED union (coverage) | 0.9970 | 0.488915 | **2.04×** |
| DUCT+HUB together | 0.9970 | 0.374972 | **2.66×** |
| **Z-DISK share** | **0.0000** | 0.019694 | **0.00×** |
| **Z-AXIS share** | **0.0000** | 0.094249 | **0.00×** |

> **The CONCENTRATION gate stays sharp at 65× null. EVERY LOCATION gate is
> 2–4× null.** The original G1 was defensible precisely because it sat **50×**
> above its null, so no threshold choice inside a wide band could change the
> answer (§15B.2c). **No attribution threshold on these zones can have that
> headroom, because the four named zones already occupy 48.9 % of the cells.**
> A "one zone dominates" gate against a 25 % null is knife-edge by construction,
> and his own DUCT+HUB alternative is 2.66× — better, still not sharp.

**The sharp location statements available are the NEGATIVE ones.** Z-DISK and
Z-AXIS carry **0.0000** against nulls of 0.0197 and 0.0942 — the residual density
is **absent** from the disk and the axis. **Exclusion has the headroom that
attribution lacks**, and Z-AXIS at zero bears directly on H4, whose whole content
is the near-axis aspect ratio. *(Z-DISK at zero is independently consistent with
§6.1, which exonerated the actuator disk by measurement.)*

> ⚠ **DISCLOSURE, owed again: I HAVE SEEN THESE NUMBERS.** Proposing an
> exclusion-shaped gate after observing that the exclusions are the sharp
> statistic is outcome-informed, exactly as the density proposal was. I state it
> as a **design option for ruling, not as a choice I have made**, and the
> published-alternatives discipline of §15E applies to it identically.

### 15G.5 WHY THE SUCCESSOR IS HELD ONE MORE TIME

He directed: *"Do prerequisite 4(b) and the epsilon, then bring me the draft
successor."* **4(b) is done. The epsilon proved unwarranted. And §15G.4 changes
the premise of the draft**, because thresholds were to be set as a stated
multiple of the null — and the null measurement shows that **for every location
statistic the observation sits 2–4× above it**, with the observations already in
view.

**Choosing a location threshold now would be choosing between "2× null" and
"3× null" while knowing the answer is 2.10× and 3.80×. That is a threshold set by
eye against a knife-edge, which is what the null-multiple method exists to
prevent — and it would satisfy the letter of his ruling while defeating its
purpose.**

**What I need ruled before drafting, and none of it is mine:**

1. **Whether the successor gates on location at all**, given that no attribution
   threshold on these zones can achieve meaningful headroom.
2. **Or whether the location gate is reposed as EXCLUSION** — with the
   non-blindness discharged by publishing every zone's share beside its null
   every time, as §15E requires.
3. **Or whether the successor gates on CONCENTRATION ONLY** (65× null, sharp,
   and unaffected by all of this), reporting location as measured-but-ungated —
   noting that "reported but not gated" is the shape L-478's family warns about
   and would need care.

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
