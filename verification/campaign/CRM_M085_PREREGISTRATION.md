# CRM-M085 — NASA Common Research Model wing-body at M∞ = 0.85, DPW5 hex refinement family

<!-- ============================ DRAFT BANNER — STRIKE THIS ONE BLOCK ============================ -->
> ## 🟠 DRAFT. **NOT FROZEN. NOT AUTHORISED. NO COMPUTE HAS RUN UNDER IT.** §13's freeze block is BLANK.
> Drafted by a cfd `lab-lane`, 2026-09-10, on the cfd-supervisor's brief. **Check 4 — pre-registration
> COMMITTED before compute — is the supervisor's, is personal, and is not delegated to this lane.**
> **THIS BANNER IS A SINGLE BLOCK BOUNDED BY THE TWO COMMENT RULES ABOVE AND BELOW IT, SO IT CAN BE
> STRUCK AT FREEZE IN ONE EDIT.** A stale banner contradicting a later freeze caused two problems on
> 2026-09-10 (M6CP1 A1.1); it is bounded here so that cannot recur.
> **SUBMISSIONS PARKED (rule 7). No agent's message is Sanaa's consent (rule 9).**
<!-- ========================== END DRAFT BANNER — STRIKE TO HERE ================================= -->

---

## 0. WHAT SANAA ASKED FOR, AND THE THREE THINGS STANDING BETWEEN HER AND IT

**Sanaa, 2026-09-10:** *"NASA CRM run at ma 0.85 launched asap"*, within *"i want to have these 3D
cases (including NAVIER) asap"*. **The instruction is hers and this document exists to execute it
honestly, not to argue with it.**

Three facts are already **measured** on this box and each one changes what "launch asap" can mean.
They are put first, before any gate, because a registration that buries them would be a registration
written to be launched rather than to be true.

| # | finding | status |
|---|---|---|
| **F1** | **The refinement triple does not exist on this box.** `/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid/` holds **L1.T only**, in three *topologies* (hex/prism/hybrid) — **not three levels.** | measured, `ls` |
| **F2** | **L1.T fails both hard mesh gates**: max non-orthogonality **89.7134°** against 70° (`MESH_STANDARD.md` §3.1), max skewness **14.0594** against 4 (§3.2). | measured, archived `checkMesh` log |
| **F3** | **`rhoSimpleFoam` at M = 0.85 DIES AT ITERATION 2 ON THIS EXACT GRID**, and on prism and hybrid too. `transonic yes` with pressure limits does not fix it. | measured, `COMMITTEE_GRID_NUMERICS.md` §4 |

**None of these is a reason not to run. Each is a reason to run something specific.** §2, §4 and §5
say what.

## 1. 🔴 F3 IS A TWO-CASE, **TWO-BUILD** THERMO/`libm` FAILURE — AND THE M6 TREE HOLDS THREE DISTINCT FAILURES, NOT ONE

### 1.1 THE SHARED SIGNATURE, READ FROM BOTH STACKS

| | **DPW5 CRM wing-body** | **ONERA M6, `M6_OWN_FAMILY_runs/L2/solve`** |
|---|---|---|
| build | **openfoam2606** | **OPENFOAM=2506** (the dafoam build) |
| invocation | `rhoSimpleFoam -parallel` | `rhoSimpleFoam -parallel`, 4 ranks |
| dies at | **Time = 2**, signal 8 | signal 8 |
| stack | `libm.so.6` ← `libfluidThermophysicalModels.so` ×2 ← `rhoSimpleFoam` | `libm.so.6` ← **`Foam::hePsiThermo<psiThermo, pureMixture<sutherlandTransport<species::thermo<hConstThermo<perfectGas<specie>>, sensibleInternalEnergy>>>>::calculate`** ← `::correct()` ← `libfluidThermophysicalModels.so` |
| thermo package | `hePsiThermo` / `pureMixture` / `sutherland` / `hConst` / `perfectGas` / `sensibleInternalEnergy` | **identical** |

**THE SAME THERMO PACKAGE, THE SAME `libm` DOMAIN ERROR, ON TWO DIFFERENT OpenFOAM BUILDS, TWO
GEOMETRIES AND TWO INDEPENDENT GRID FAMILIES.** **Two builds showing one signature is a stronger
claim than one build showing it twice**, because a build-specific miscompilation is excluded by
construction. The FPE is raised *inside* `libm` — a domain error on a `pow`/`log`/`sqrt`, consistent
with a non-positive temperature or pressure reaching the equation of state.

**It is still NOT decided here whether that is an OpenFOAM defect or a setup defect.** Two records
agreeing is a coincidence of authorship, not evidence. **The decision requires a minimal reproducer
and the single change that clears it**, which is registered as this campaign's rung 0 and is being
built separately.

### 1.2 THE M6 TREE HOLDS **THREE** DISTINCT FAILURES, WHICH REFINES M6CP1 §4.1

M6CP1 §4.1 says *"every `rhoSimpleFoam` variant across 24 diagnostic solves repeats rc = 136"*, as
though one cause. Measured across all nine `rhoSimpleFoam` logs in
`verification/runs/M6_OWN_FAMILY_runs/`, by a plant-controlled reader:

| failure | logs | frame |
|---|---:|---|
| **thermo / `libm`** | 1 (`L2/solve`) | `hePsiThermo::calculate` ← `libm` |
| **wall function** | 2 (`smoke_diag_fo`, `smoke_potentialfoam2`) | `nutUSpaldingWallFunctionFvPatchScalarField::calcUTau` |
| **linear solver** | 2 (`smoke_simplec`, `smoke_stabilized`) | `GAMGSolver::scale` |
| no SIGFPE stack at all | 4 | — |

**Only the graded attempt (`L2/solve`) carries the thermo abort. The smoke variants do not.** The
`calcUTau` failures are a **downstream** consequence of the 60.9° cusp M6CP1 A2.2 measured — a
Spalding wall function iterating on a collapsed trailing edge, on the same cells where A2.4 recorded
a y⁺ maximum of **1.886e10**. **Those are setup/mesh. The thermo abort is a separate question.**

### 1.3 🔴 A READER DEFECT OF THIS LANE'S OWN, RECORDED BECAUSE IT IS THE LESSON

An earlier version of this section asserted **"ZERO of the nine logs carry a `hePsiThermo` frame"**.
**That was FALSE**, and it was produced by this lane's own reader, twice over:

1. **A 4-line window.** `grep -A4 "sigFpe::sigHandler"` — in `L2/solve` the handler line and the
   `hePsiThermo` frame are **eight lines apart**, because a 4-rank parallel backtrace interleaves
   `[0] [1] [2]` prefixes and shreds single frames across several lines.
2. **A regex that could not match the symbol.** `Foam::[A-Za-z_]\w*(?:::[A-Za-z_~]\w*)+` requires
   `::` directly after the class name. `Foam::hePsiThermo<...>::calculate` has `<` there, so the
   pattern could **never** match it and silently matched `Foam::species::thermo` from inside the
   **template arguments** instead.

**A universal negative from a reader never shown able to see a positive is not evidence (rule 3), and
this lane published one.** The census above was re-taken with a reader carrying three planted
controls — a known-positive `hePsiThermo`, a known-positive `GAMGSolver`, and a discrimination check
that the first log does **not** report the second's frame — and **it REFUSED on its first run**,
catching defect 2 before any absence was reported. Instrument and controls:
`verification/runs/M6_OWN_FAMILY_runs/STACK_CENSUS/stack_census.py`.

**CRM-M085 THEREFORE REGISTERS `rhoPimpleFoam` AS ITS SOLVER, WITH `rhoSimpleFoam` AS A MEASURED
TWO-CASE COUNTER-EXAMPLE — recorded, not quietly substituted** (the `CASE_PROTOCOL` "class default,
first use" rule). **A `rhoSimpleFoam` arm is registered anyway, as rung 0, precisely so the defect is
reproduced under a frozen registration rather than remembered** — Sanaa's standing directive is that
OpenFOAM issues reach her *with the run*, not worked around. **Whether it is an OpenFOAM defect or a
setup defect is NOT decided here**; M6CP1 §4.2 ruled *setup* on its own evidence and nothing was
referred upstream, and that ruling is not extended to this case without its own evidence.

## 2. THE MESH FAMILY — WHAT IT CAN ACTUALLY BE, AND THE PREREQUISITE THAT IS ALREADY REGISTERED

**What is on the box:** `L1.T.rev01.p3d.hex.r8.ugrid` — **638,976 cells, 660,177 points, all
hexahedra**, converted at `/home/ubuntu/certonomous-runs/dpw5-committee-probe/case_hex/constant/polyMesh`,
three patches: `symmetry` (15,360 faces), `wall` (13,312), `farfield` (13,312).

**The prism (1,277,952) and hybrid (2,981,888) files are the SAME LEVEL in different element
topologies. They are not a refinement family and must never be used as one** — and
`COMMITTEE_GRID_NUMERICS.md` §5 measured that neither of them solves here under any configuration
tried, at second order.

**The triple that CAN exist** is the DPW5 hex family, and it is already scoped:

| level | hex cells | h ratio to next coarser | on box? |
|---|---:|---:|---|
| L1.T | 638,976 | — | **YES** |
| L2.C | 2,156,544 | **1.500000** (2,156,544 / 638,976 = 3.375 exactly) | **NO — upstream, HTTP 200, 123,796,868 B** |
| L3.M | 5,111,808 | **1.333333** (5,111,808 / 2,156,544 = 64/27 exactly) | **NO — upstream, HTTP 200, 291,645,252 B** |

**🔴 r IS NOT CONSTANT: 1.5 then 4/3.** Any Roache/GCI treatment must use the **non-uniform-ratio**
form, and the **DELIVERED** ratio computed from measured cell counts, never a nominal one. The
Roache parameter is **`form`, not `mode`**, default `"auto"`. (MRF delivered 1.4157/1.4264 against a
registered 1.5 — a nominal ratio is a claim, not a measurement.)

**THE PREREQUISITE ALREADY EXISTS AND IS UNEXECUTED.**
`verification/campaign/RUNG2_CRM_GRID_ACQUISITION_PREREGISTRATION.md` registers exactly this fetch,
with gates G-A0…G-A3, a **30.0 core-min cap**, a title-page limb (L-144) and a comparator
`cases/committee-grids/grade_grid_acq.py` whose 10/10 selftest controls fire. **It is blocked on the
cfd-supervisor's check 1 — the non-delegable measurement-script diff — which has NOT been taken.**
Nothing was fetched.

**So CRM-M085 is registered in two stages and the dependency is explicit, not implied:**

- **STAGE A — single level, L1.T, M 0.85. NO Gate G. No grid-convergence claim of any kind.** This is
  what can launch tonight. It answers F3 under a frozen registration and produces the first M 0.85
  CRM iteration this lab has ever completed.
- **STAGE B — the triple.** Requires the acquisition registration to execute first. **STAGE B DOES NOT
  BECOME AUTHORISED BY A GOOD STAGE-A RESULT.** It is gated on the fetch, on check 1, and on the
  supervisor.

**And the honest caveat that the acquisition registration already states and this one inherits: the
strong prior is that L2.C and L3.M FAIL the same hard mesh gates L1.T fails** (aspect ratio *grows*
with refinement in this family — L1.T 14,426.8 → published L4 131,000). **A triple of gate-failing
grids can carry a numerical-uncertainty statement; it cannot carry a credential drag figure.**

## 3. THE REFERENCE CONDITION — READ, NOT INHERITED

### 3.1 🔴 THE EXISTING `forceCoeffs` BLOCK IS CONTRADICTORY AND IS NOT INHERITED

`RUNG2_CRM_M2` ran at **M 0.196** — `0/U` freestream `(68.013854 0 2.505842)`, α 2.11°, `transonic no`
— while its `forceCoeffs` block carried **`magUInf 295.0`** (= M 0.85) with **`Aref 1.0`**. **A
normalisation that names a velocity the field never had produces coefficients that mean nothing.**
**Every reference quantity in this registration is re-derived and none is carried over.**

**And `Aref 1.0` is worse than merely wrong here, for a reason that is measured:** the grid's own
overall bounding box is **(-30328.2, 0, -31438.1) to (32996.6, 31664.3, 31866)**. At a CRM `cref` of
275.8 **inches** that is a farfield at ≈110 `cref` — consistent with DPW5's ~100-`cref` specification.
**At any metre interpretation the domain would be 63 km across.** So **the grid is in INCHES**, and a
unit-area `Aref` against an inch-based mesh is off by the reference area itself.

**This is an INFERENCE from the bounding box, not a measurement of the model.** §6.1 registers the
measurement that settles it and the refusal if it disagrees.

### 3.2 THE REGISTERED CONDITION — MEASURED AND DERIVED, NOT TYPED

**The mesh has been scaled.** `transformPoints -scale (0.0254 0.0254 0.0254)` was run — nothing had
run it, and every reference quantity depends on it. Proof on the face of the logs: overall bounding
box **(-30328.2 0 -31438.1) (32996.6 31664.3 31866)** before, **(-770.336 0 -798.527) (838.113
804.273 809.396)** after. The domain is ≈110 `cref`, matching DPW5's ~100-`cref` specification.

**THE ADMISSION LIMB IS MEASURED, NOT ASSUMED.** The `wall` patch's own extent, parsed from the
polyMesh: x 2.349500…65.097228, **y 0…29.460136**, z 2.310308…8.715974 m; the `symmetry` patch is
planar at exactly y = 0. **Measured semispan 29.460136 m against the published 1156.75 in =
29.381450 m — agreement +0.268 %, inside the 1 % band. ADMITTED.** That agreement is what licenses
using the published `Sref`, `cref` and MRC; without it this registration refuses rather than picks.
Axes confirmed from the measurement: **x streamwise, y spanwise, z vertical.**

| quantity | value | how obtained |
|---|---|---|
| M∞ | **0.850000** | Sanaa's instruction; verified `U/a` = 0.850000 |
| T∞ | **300 K** | the archived CRM condition |
| a(300 K) | **347.238 m/s** | `sqrt(γRT)`, γ = 1.40011 and R = 287.0580 from the case's **own** `thermophysicalProperties` (`Cp 1004.5`, `molWeight 28.964425`) |
| U∞ | **295.1522 m/s** | `M·a` |
| α | **2.11°**, a **FIXED-α PROBE** | §6.1 limb 4, second branch: registered *as* a fixed-α probe with **NO CL claim**. It is the lab's own archived CRM angle. **This is NOT the DPW fixed-CL 0.500 case and must never be reported as one.** |
| U vector | **(294.952035 0 10.866949)** | `U(cos α, 0, sin α)` |
| μ(300 K) | **1.990163e-05 Pa·s** | Sutherland from the case's own `As 1.571860616e-06`, `Ts 110.4` |
| ρ∞ | **0.048127 kg/m³** | **derived** from Re(cref) = 5.0e6: `ρ = Re·μ/(U·cref)`; verified Re = 5.0000e+06 |
| p∞ | **4144.53 Pa** | `ρRT` |
| cref / lRef | **7.005320 m** | 275.8 in × 0.0254 |
| **Sref / Aref** | **191.8448 m²** | 297,360 in² × 0.0254². **`Aref 1.0` is forbidden and is not used.** |
| MRC / CofR | **(33.67786 0 4.51993) m** | (1325.9 0 177.95) in × 0.0254 |
| k∞ / ω∞ | **0.1306722 / 9.421130** | I = 0.1 %, ℓt = 0.01·cref |

**`forceCoeffs` carries `rho rho;`** — the field, not a typed density — plus `rhoInf 0.048127`, which
this build requires as the coefficient **denominator**. Every one of these is consistent with the
field that actually runs. **The `RUNG2_CRM_M2` defect was the opposite: a `magUInf 295.0` naming a
velocity its M 0.196 field never had, with `Aref 1.0`. Nothing from that block is inherited.**

### 3.3 DECLARED NON-CONFORMANCE, ON THE FACE OF THIS DOCUMENT

**L1.T FAILS BOTH HARD MESH GATES AND IS RUN ANYWAY, KNOWINGLY.** Measured by this campaign's own
`checkMesh -allGeometry -allTopology`, post-scale: **max non-orthogonality 89.7134° against the 70°
gate; max skewness 14.0593 against the gate of 4; max aspect ratio 14,426.8 on 10,799 cells;
`Failed 7 mesh checks`.** 638,976 cells, all hexahedra, 3 geometric (non-empty/wedge) directions.

**And `checkMesh` returned rc = 0 while printing `Failed 7 mesh checks`** — so rc is not evidence and
is not used as evidence anywhere here.

**CONSEQUENCE, CARRIED IN THE GRADER'S JSON AND NOT ONLY IN PROSE: NO CREDENTIAL. NO VALIDATED FORCE.
NO DRAG CLAIM.** Stage A is a probe of whether a M 0.85 CRM case runs at all.

## 4. THE MANDATORY LIMBS — FROM TONIGHT'S FINDINGS, IN THE REGISTRATION AND NOT IN A LANE'S HEAD

### 4.1 `checkMesh` MUST RUN `-allGeometry -allTopology`, AND ITS rc IS NOT EVIDENCE

**Plain `checkMesh` prints `Mesh OK.` with rc = 0 on meshes the full set fails** — measured on two
independent case families on 2026-09-10 (M6CP1 A2.7). **`checkMesh` returns rc = 0 even when it
prints `Failed N mesh checks`**, so any verdict of the form `ok = ("Mesh OK." in out) and rc == 0`
rests entirely on the substring and the rc clause contributes nothing.

**Registered:** stage 1 runs **its own** `checkMesh -allGeometry -allTopology` per level, in this
campaign's tree, and **never substring-matches a foreign log it did not produce.** M6CP1's stage 1
read the *mesher's* log from a *different campaign*, from a bare invocation — a well-designed
instrument fed a blind input. The `***` line collection is kept; it is the right idea.

### 4.2 A GEOMETRY LIMB A CUSP CANNOT PASS

M6CP1 died on a trailing edge that closed to a single point — **zero cells across it**, half-angle
60.9°, **scale-invariant**, and `checkMesh` cleared it under **both** check sets. **Quality metrics
did not see it; direct geometry did.**

**Registered thresholds, before any measurement:**

| limb | threshold | on failure |
|---|---|---|
| cells across every named trailing edge | **≥ 8** | **`NOT A RESULT` for that level** |
| that count under refinement | **non-decreasing** | `NOT A RESULT` for the family |
| wall-face-area ratio (max/min on the wall patch) | **≤ 1,000:1** | `NOT A RESULT` for that level |

*(M6CP1 ran 7,212:1 and a 47.07× area jump aft of 0.995c.)*

**🔴 WHAT THE CRM's TRAILING EDGE ACTUALLY IS HAS NOT BEEN MEASURED AND IS NOT ASSERTED HERE.** Two
things are known and neither is a measurement of this grid: the CRM wing is **designed with a blunt
trailing edge**, and DPW5's structured-derived hex grids are built to resolve it — so the *prior* is
that this family passes where M6CP1 failed. Against that, **the whole wing-body wall patch carries
only 13,312 faces at L1.T**, which is coarse enough that **≥ 8 cells across the TE may not be
achievable at the coarsest level at all.**

**REGISTERED PREDICTION, FALSIFIABLE:** L1.T **fails** the ≥ 8 limb; L2.C and L3.M pass it. **If L1.T
fails, that is a finding about the level and not a defect in the limb**, and Stage A proceeds
`NOT A RESULT`-labelled on the geometry limb while still answering F3. **The limb is measured in
stage 1 and its number is not written into this document in advance.**

### 4.3 DIMENSIONALITY FROM THE `geometric (non-empty/wedge)` LINE, EXPLICITLY, PER LEVEL

Read from `checkMesh`'s own line, per level, and recorded per level. Not inferred from patch types
and not assumed from the campaign's name.

### 4.4 THE DELIVERED REFINEMENT RATIO, NEVER A NOMINAL ONE

Computed from **measured** cell counts per level (from a source that counts **cells** —
`checkMesh`'s `cells:`, cross-checked against owner/neighbour topology; **`len(owner)` is `nFaces` and
is used nowhere**). `nCellsBetweenLevels` is measured in cells, not thickness. Roache parameter is
**`form`**, default `"auto"`.

### 4.5 `transonic` IS CONSIDERED EXPLICITLY, AND ANY DEPARTURE IS JUSTIFIED AGAINST A MEASURED COUNTER-EXAMPLE

At M 0.85 the pressure equation's transonic form is the default expectation. **Registered: `transonic
yes` is the baseline for CRM-M085**, and `div(phid,p)` is supplied in `divSchemes` so it is
*assemblable* — M6CP1's diagnostic registered to test that switch **died in dictionary lookup**
(`Entry 'div(phid,p)' not found`, because `default none;` makes an unruled term a hard abort) and **a
numerics rung stood recorded as climbed that was never once climbed.** Any departure from `transonic
yes` is registered here as a **measured** counter-example on this grid, or it is not taken.

## 5. STAGE A — WHAT CAN LAUNCH, AND WHAT IT MAY CLAIM

**Level L1.T. Solver `rhoPimpleFoam`. `transonic yes`. Closure `kOmegaSST`.** Two rungs:

| rung | purpose | expected |
|---|---|---|
| **rung 0 — `rhoSimpleFoam` at M 0.85** | **reproduce F3 under a frozen registration**, so the defect is a run and not a memory | **dies at ≈ iteration 2**; rc and the aborting library recorded |
| **rung 1 — `rhoPimpleFoam` at M 0.85** | the actual probe | unknown; this is the question |

**WHAT STAGE A MAY CLAIM: that a M 0.85 CRM case ran or did not, with its rc, its residual history and
its LTS field if LTS is used.**

**WHAT STAGE A MAY NOT CLAIM, AND THIS IS NOT NEGOTIABLE:**
- **No drag, lift or moment figure.** One level, no Roache triple, gate-failing mesh, and reference
  quantities unconfirmed until §6.1 clears.
- **No comparison against DPW published data or against A6's CD = 0.020901 / CL = 0.500015.** A6 is
  **dafoam territory**, its solver is not this one, and `COMMITTEE_GRID_NUMERICS.md` §4 already ruled
  that the comparison must be made at A6's condition and this toolchain could not reach it.
- **No credential.** The mesh-gate ruling stands.
- **rc = 0 at `endTime` is not a converged solution and is not a graded result.**

## 6. GATES

**All gates are `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`. No other word.**

| id | gate | threshold | label if not met |
|---|---|---|---|
| **C-G0** | **Reference condition settled** (§6.1) | primary source located and title-page verified (L-144); grid units, `cref`, `Sref`, MRC and α all confirmed against the grid's own measured wall-patch extent | **BLOCKED** — no run |
| **C-G1** | **Mesh admission** | own `checkMesh -allGeometry -allTopology` per level, in this tree; every `***` line recorded; the §3.1/§3.2 values recorded as the finding | **NOT A RESULT** for that level |
| **C-G2** | **Geometry limb** (§4.2) | ≥ 8 cells across every named TE; non-decreasing under refinement; wall-face-area ratio ≤ 1,000:1 | **NOT A RESULT** for that level |
| **C-G3** | **F3 reproduction** (rung 0) | `rhoSimpleFoam` at M 0.85 aborts, with rc and aborting library captured from the process | **a genuine finding either way** — an abort confirms the two-case pattern; a clean run **falsifies** it and is more interesting |
| **C-G4** | **Stage-A completion** (rung 1) | standing rule 4 in full: rc = 0, `End`, last time == `endTime`, fields present, `ExecutionTime` count consistent, **every field newer than the case's own `0/T`** | **NOT A RESULT** |
| **C-G5** | **STAGE B ONLY — Roache triple** | rule 5's order, unaltered, on delivered non-uniform r; GCI at Fs = 1.25; **no GCI quoted when the three values are not monotone** | **NOT A RESULT** |

**Gate order:** C-G0 → C-G1 → C-G2 → C-G3/C-G4 → C-G5. **A gate can only turn a `PASS` or `GATE FAIL`
INTO `NOT A RESULT`, never the reverse.**

### 6.1 THE REFERENCE-CONDITION LIMB, DECLARED BEFORE THE RUN

1. **Locate and title-page-verify a primary CRM/DPW source** (rule 15 — never by filename, file type
   or hash). `docs/DPW-CRM-SCOPING.md` is a **lab scoping report citing URLs** and is **not** that
   source. **If no primary source is on the box, C-G0 is `BLOCKED` and says so** rather than
   proceeding on a secondary.
2. **Measure the `wall` patch's own bounding box** from the polyMesh and derive the semispan; confirm
   against the published CRM value (nominally 1156.75 in). **A disagreement REFUSES the case; it does
   not pick a winner.**
3. **Derive `Sref`, `cref`, `lRef` and MRC in the grid's own units** and write them into
   `forceCoeffs`. **`Aref 1.0` is forbidden.**
4. **Reconcile α.** DPW case 1 is fixed-CL at 0.500; the lab's archive carries 2.11°. **These are not
   the same specification and the difference is not split.** Either a trim procedure is registered,
   or a fixed-α probe is registered *as* a fixed-α probe with no CL claim.

## 7. THE PLANT (rule 3)

Every absence asserted in this document is measured by a reader **shown able to see a hit at the exact
path it searches**, then shown the absence again, **in one invocation each**, before the freeze. The
readers to be planted: the `grid/` directory listing that reports L2.C/L3.M absent; the
`verification/runs/CRM_M085_runs/` listing that reports no run output. **A reader that returns empty
without having been shown a non-empty REFUSES rather than reports.**

## 8. COST (rule 12) — ESTIMATED BEFORE COMPUTE

Basis: **core-minutes = wall s × ranks / 60**. Dollars **DERIVED, NOT MEASURED**, at the owner-stated
c7a.4xlarge **$0.0513/core-h** — this box cannot read its own billing.

**Cap-exempt as a 3D case under Sanaa's 2026-09-10 exemption — *"for all these 3D cases that still
need to run, i dont want to see any budget gates ( time or money)"*. `budget_gate: NONE — Sanaa
2026-09-10`. IT IS STILL COSTED, and the estimate is calibration data, not a gate.**

| item | basis | core-min (est.) | $ derived |
|---|---|---:|---:|
| C-G0/C-G1/C-G2 stage-1 measurement, L1.T | `checkMesh -allGeometry -allTopology` + geometry limb; acquisition prereg measured **0.905 core-min per Mcell** for convert+`checkMesh` | **≈ 1.2** | 0.001 |
| rung 0 — `rhoSimpleFoam`, aborts ≈ iteration 2 | measured behaviour: it does not survive | **≈ 0.5** | 0.000 |
| rung 1 — `rhoPimpleFoam`, L1.T, 5,000 steps, 4 ranks | **🔴 NO MEASURED RATE EXISTS for `rhoPimpleFoam` on this grid.** Anchored on M6CP1's measured 0.325 s/step at 71,760 cells, scaled linearly to 638,976 cells = 2.89 s/step serial, ÷ 3.2 four-rank speedup (**ASSUMED, not measured**) × 4 ranks | **≈ 301** | 0.257 |
| **STAGE A TOTAL** | | **≈ 303** | **≈ $0.26** |
| STAGE B — fetch + screen L2.C/L3.M | the acquisition registration's own cap, **not re-registered here** | *(30.0, that document's)* | 0.026 |
| STAGE B — solves L2.C + L3.M | **NOT ESTIMATED. No rate, no mesh, no admission.** An estimate here would be a number invented to fill a cell. | **PENDING** | — |

**The two largest uncertainties are named rather than buried:** the **3.2× four-rank speedup is an
ASSUMPTION** (M6CP1 registered it and, having run serial, **never measured it — it is still owed**),
and **linear cell-scaling of the per-step rate across a 8.9× cell-count jump and a different grid
family is an assumption too.** Stage A's first checkpoint measures both. Memory: the acquisition
registration's law predicts **4,290 MiB** peak RSS for a 2.16M-cell solve; L1.T at 638,976 cells sits
far inside the box, and stage 1 measures it rather than trusting the law.

**The rule-12 estimate-versus-actual row is owed to `docs/COST_CALIBRATION.md` at every process
completion and is not discharged by this registration.**

## 9. ROUTING

Detached under the stage-4 launcher, re-parented to **PPID 1**. **rc captured INSIDE the wrapper from
the solver process into `RC.txt`** — `setsid timeout cmd` exits 0 for every outcome including SIGFPE.
**Any bashrc source is `set +u`-guarded**: on 2026-09-10 two independent launchers in two teams died
on `set -u` + OpenFOAM's `etc/bashrc` dereferencing `WM_PROJECT_DIR` unset, and one of them **printed
`LAUNCHED` for a wrapper that was already dead.** The canonical guard is in
`scripts/case_protocol_stage4_run.py`. **A launcher that cannot confirm its own launch must refuse,
not report.**

## 10. WHAT THIS REGISTRATION DOES NOT DO

It does not authorise the grid fetch — that is the acquisition registration's, and it is blocked on
check 1. It does not lift the mesh-gate ruling. It does not rule on whether the `rhoSimpleFoam` M 0.85
abort is an OpenFOAM defect or a setup defect. It does not inherit `RUNG2_CRM_M2`'s `forceCoeffs`
block, its Mach number, or its `PASS`. It makes no drag claim of any kind.

## 11. AN HONEST NOTE ON `RUNG2_CRM_M2`'s RECORDED `PASS`

`R2M2-G4` passes but **is never written to `STATUS.R2_M2`** — it is printed only on the `--selftest`
branch. So "PASS on four gates" in a five-gate registration is a **recording artifact**, not a
narrower result. Noted because CRM-M085 must not inherit a status it did not earn. **It is disclosed,
not repaired: that registration is frozen and compute has occurred under it.**

## 12. GRADING PATH

**NOT YET WRITTEN.** It will be pinned by **git blob sha, repo-relative**, with **every invocation
pinned as an argv LIST, not a shell string**. Guards will report `armed_by_pin`,
`arming_datum_present` and `arming_value`. The freeze checker is invoked with
`--restrict-to-registration` and that flag is part of the pinned argv; **`pins_unseen` is read and
reported — an exit 0 with unseen pins is not a clean result.**

## 13. FREEZE BLOCK — LEFT BLANK FOR THE cfd-SUPERVISOR (check 4, undelegated)

```
FROZEN BY:        <blank — cfd-supervisor>
FREEZE COMMIT:    <blank>
REGISTRATION BLOB:<blank>
NO COMPUTE UNDER THIS DOCUMENT AS AT FREEZE, verified with a live planted control:
                  <blank — §7's readers, run in one invocation each at freeze time>
```

**AFTER THE FREEZE COMMIT THE GATES ARE CLOSED.** Changes land only as dated addenda that cannot alter
a gate, threshold, cap or label. Originals are struck, never rewritten.

---

## §13 FREEZE BLOCK — cfd-SUPERVISOR, CHECK 4, UNDELEGATED

```
FROZEN BY:        cfd-supervisor (Opus 5), 2026-09-11, check 4 undelegated
FREEZE COMMIT:    the commit carrying this block; verify with
                  git log -1 --format=%H -- verification/campaign/CRM_M085_PREREGISTRATION.md
REGISTRATION BLOB:git rev-parse HEAD:verification/campaign/CRM_M085_PREREGISTRATION.md
STAGE A:          L1.T SINGLE LEVEL, 638,976 hex. GATE G NOT REGISTERED -- no triple.
MESH SCALED:      transformPoints -scale (0.0254 ...) RUN. Nothing had run it, and
                  the grids ship in INCHES. Provable on the logs' face: bbox
                  (-30328.2 0 -31438.1)(32996.6 31664.3 31866) BEFORE,
                  (-770.336 0 -798.527)(838.113 804.273 809.396) AFTER. ~110 cref.
REFERENCE ADMITTED BY MEASUREMENT, NOT ASSUMED: the `wall` patch's own measured
                  extent gives semispan y = 29.460136 m against the published
                  1156.75 in = 29.381450 m -- +0.268 %, inside the 1 % band.
                  THAT AGREEMENT IS WHAT LICENSES the published Sref/cref/MRC;
                  without it this registration REFUSES rather than picks.
                  Aref 191.8448 m2 -- NOT 1.0. lRef 7.005320. rhoInf 0.048127
                  DERIVED from Re(cref)=5e6 with Sutherland mu, round-trip
                  verified at Re = 5.0000e+06, M = 0.850000.
ALPHA:            FIXED-ALPHA PROBE at 2.11 deg, the lab's archived CRM angle,
                  with NO CL CLAIM. Explicitly NOT the DPW fixed-CL 0.500 case.
DECLARED NON-CONFORMANCE (ruled 2026-09-10, Sanaa may overrule): L1.T FAILS BOTH
                  HARD GATES AND IS RUN ANYWAY, KNOWINGLY -- max non-orthogonality
                  89.7134 (gate 70), max skewness 14.0593 (gate 4), max aspect
                  ratio 14,426.8 on 10,799 cells, "Failed 7 mesh checks", measured
                  post-scale by this campaign's OWN -allGeometry -allTopology run.
                  checkMesh RETURNED rc = 0 while printing that, so rc is used as
                  evidence NOWHERE. The standard is NOT touched; no threshold moves.
                  CAP: NO CREDENTIAL, NO VALIDATED FORCE, NO DRAG CLAIM -- emitted
                  in the GRADER'S JSON, not only in prose.
BUDGET GATE:      NONE -- Sanaa 2026-09-10 (3D exemption). NOTE: the registered
                  ~301 core-min may be LOW BY 2-3x; see the addendum-free note below.
NO COMPUTE UNDER THIS DOCUMENT AS AT FREEZE, verified by a LIVE PLANTED CONTROL:
  the time-directory reader returned 2 on verification/runs/navier_class/MRF/coarse
    -- SHOWN ABLE to see a time directory before an absence is believed (rule 3);
  the same reader returned ZERO on verification/runs/CRM_M085_runs/L1T/case, whose
    contents are `0.orig constant system` only -- no 0/, no time dir, no rc, no log.
  The graded case and the dry run differ by EXACTLY ONE LINE: endTime 5000 vs 1.
COST HONESTY AT FREEZE: the dry run's first iteration took 13.41 s serial against
  the 2.89 s/step this registration assumed. That step includes wallDist and field
  init so it is an UPPER bound, not a steady rate -- but if the steady rate lands
  near it the real figure is 600-900 core-min, not 301. Recorded HERE, before
  compute, so the estimate is never quoted as though it held.
```

**AFTER THIS FREEZE THE GATES ARE CLOSED.** Changes land only as dated addenda that cannot alter a
gate, threshold, cap, band or label.

---

## ADDENDUM 1 — 2026-09-11 — **STAGE A PARKED `NOT A RESULT`. THE LADDER IS EXHAUSTED AND THE REASON IS MEASURED.**

**lines whose number changed above this section: 0.** No gate, threshold, cap, band or label is altered.
**Gate P and Gate G were never evaluated.** No credential, no validated force, no drag claim.

### A1.1 VERDICT — `NOT A RESULT`

Stage A is parked under the pre-registered exhaustion rule. **The ladder was declared short BEFORE it was
climbed** — three rungs, no rung 3 — and it is being honoured rather than extended.

### A1.2 THE MECHANISM, MEASURED END TO END

**seed → local collapse → spread → global freeze → SIGFPE.** Each link measured, not inferred:
- **The seed is 9,158 cells — 1.4 % of the mesh — on measurably bad geometry.** At t=10 the collapsed
  set is enriched **10.16×** in `nonOrtho>70` and **11.28×** in `skew>4`, median cell angle 38.53°
  against a global 21.58°. Five planted controls passed before any count was believed, and the
  high-aspect-ratio confound runs the *other* way (**0.00×**), so these are not boundary-layer cells.
- **The enrichment DECAYS as the collapse spreads — 10.16× → 5.35× → 0.14×** — the signature of a
  diffusive operator smearing a seed until the spatial correlation is destroyed. **The first graded
  write at `writeInterval 100` is already post-spread and cannot see the seed**; a separate short
  diagnostic at `writeInterval 5`, in a sibling directory and never the graded tree, recovered it.
- **The blow-up starts COLD.** At t=5 the **floor** clamp fires alone — 1,381 cells at 100 K, **zero at
  the ceiling**, T max only 530.98. The ceiling engages only by t=10. **Anyone tuning an upper
  temperature bound would be treating the symptom that appears second.**
- **The raw flow time-scale maximum is BIT-CONSTANT at 3.490203e-01 s for all 323 iterations.** Nothing
  else moved it: everything that collapsed was put there by `fvc::smooth`.
- **The terminal SIGFPE is a symptom, not a cause** — `PBiCGStab::scalarSolve` on a dot product over an
  already non-finite field (and `Foam::divide` in the diagnostic: a different frame, the same class).

### A1.3 🔴 THE DOSE-RESPONSE — `fvc::smooth` IS BOTH THE AMPLIFIER AND THE STABILISER

| smoothing | `rDeltaTSmoothingCoeff` | LTS collapse rate | early clamps | died |
|---|---|---|---|---|
| most | 0.01 | **+0.3927 dec/iter** | — | stopped it 33 |
| baseline | 0.1 | **+0.0870 dec/iter** | 1,381 lo / 0 hi | it 324 |
| **none** | 1 (disabled) | **ZERO — smoothed ≡ raw** | **18,600 lo / 9,729 hi** | **it 6** |

**Turn the smoothing UP and the LTS collapse accelerates 4.5×. Turn it OFF and the collapse stops
entirely while the temperature field blows up about 13× faster. THERE IS NO SETTING OF THIS OPERATOR
THAT SAVES THE CASE — both directions fail, for different reasons.** That is a stronger ground for the
park than a single disable would have been.

**Direction confirmed at source by the supervisor, because the whole reading depends on it:**
`fvcSmooth.C:50` sets `maxRatio = 1 + coeff` and smooths wherever a neighbour ratio exceeds it, **so a
SMALLER coefficient means MORE smoothing**; `setRDeltaT.H:63` guards `if (rDeltaTSmoothingCoeff < 1.0)`,
so **1 disables it**. **The supervisor's instruction "reduce `rDeltaTSmoothingCoeff`" meant reduce the
smoothing and in fact increased it — the lane disclosed the inversion rather than presenting the
high-dose arm as intent, and the accident is why a three-point dose-response exists at all.**

### A1.4 THE RUNGS, EACH WITH THE WINDOW IT WAS JUDGED ON

| rung | change | window | rate (dec/iter) | verdict |
|---|---|---|---|---|
| R1 | baseline, coeff 0.1, nnoc 2 | it 10→74 | +0.0870 | reference; SIGFPE at it 324 |
| 1 | `nNonOrthogonalCorrectors` 2→6 | it 10→74 | +0.1567 | **NO BENEFIT**, 1.08×, at 2.4× cost/step |
| 2a | coeff 0.1→0.01 (more smoothing) | it 10→26 | +0.3927 | **4.5× WORSE** |
| 2b | coeff→1 (smoothing OFF) | it 1→6 | **0.0000** | collapse stops; case dies at it 6 |

**🔴 EVERY VERDICT HERE IS MEANINGLESS WITHOUT ITS WINDOW, AND THAT IS NOT A FORMALITY.** Two rules were
established the hard way on this case:
1. **"Rung N survived M iterations" is NOT a measurement of rung N.** The seed diagnostic and R1 are the
   **same configuration** and died at **iteration 20 and iteration 324 — a 16× spread** — near
   bit-identical to it 10 and then separating. MPI reduction-order non-determinism amplified by an
   exponentially diverging field. **Survival count cannot discriminate rungs at all.**
2. **A metric is only as good as the window it is evaluated on.** Rung 1 was first reported as "65×
   healthier" from **two samples of a non-monotone trace**; over matched windows it is 1.08× — no
   benefit. **The rate metric was adopted precisely because survival count failed, and was then
   misapplied the same way one level down.** A reader who lifts a verdict from this table without its
   window will repeat exactly that error.

### A1.5 WHAT THE CASE IS WAITING ON — AND WHAT IT IS NOT

**It waits on a CONFORMING GRID, not on a numerics rung.** This mesh runs **max non-orthogonality
89.7134° against a gate of 70** and **max skewness 14.0593 against a gate of 4**, declared as a
non-conformance at the freeze and **run anyway, knowingly. The non-conformance collected.**

**And `COMMITTEE_GRID_NUMERICS.md` §4's "Relaxation buys iterations, not stability" is now MEASURED on
this hex family rather than inherited from the tet families.** Three rungs, none of which helped.

**What this is NOT:** not the `rhoSimpleFoam` thermo defect — a different stack and a different failure.
And **the registered solver choice was vindicated rather than undermined: `rhoPimpleFoam` with
`transonic yes` reached 324 iterations on the grid where `rhoSimpleFoam` reached 2.**

### A1.6 COST — MEASURED

R1 61.53 + rung 1 37.90 + seed diagnostic 9.40 + 2a 19.80 + 2b 3.53 = **132.2 core-min, $0.113 DERIVED,
NOT MEASURED** at $0.0513/core-h. **A fraction of the ~846 core-min a full 5000-step run would have
cost, and it bought a mechanism rather than a failed solve.** Rung 1's 37.90 has **no `rc` on disk**:
its wrapper was killed by a `pgrep -f` pattern that matched the killing shell, so **an absent `rc` there
means the wrapper died before writing one — not that the run is live and not that it crashed.** The
safe procedure, demonstrated on 2a and recorded for reuse: **`pgrep -x <solver>` filtered by
`/proc/PID/cwd`, killing only solver ranks and never the wrapper, which recorded `rc=143` correctly.**
