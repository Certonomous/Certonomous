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

## 1. 🔴 F3 IS NOT A ONE-CASE ANOMALY. IT IS THE SAME DEFECT M6CP1 MEASURED TONIGHT, ON A DIFFERENT GEOMETRY AND A DIFFERENT GRID FAMILY

This is the most transferable thing in this document and it is registered before any compute.

| | DPW5 CRM wing-body | ONERA M6 (M6CP1 §4.1) |
|---|---|---|
| grid family | DPW5 committee hex/prism/hybrid, 660,177 points | own-family hex, independently built |
| geometry | wing-body transport | swept wing |
| solver | `rhoSimpleFoam` | `rhoSimpleFoam` |
| condition | M 0.850, 295 m/s, 300 K, α 2.11° | M 0.8395 |
| failure | **dies at iteration 2**, inside `libfluidThermophysicalModels.so` | **SIGFPE rc = 136 in the FIRST thermo update**, inside `Foam::hePsiThermo<...>::calculate` from `::correct()` |
| `transonic yes` tried? | **yes — still dies** (iteration 2, and iteration 1 in a second variant) | registered pullable; the N1 rung ran and did **not** repair the case |
| variants | all three topologies | **24 diagnostic solves, every one rc = 136** |
| what survived | *(not tried at M 0.85 here)* | **`rhoPimpleFoam` LTS — every variant exited rc = 0** |

**Two independent geometries, two independent grid families, two independent lanes, one solver, one
library, one failure mode.** `COMMITTEE_GRID_NUMERICS.md` §4 called it *"a solver-configuration defect
in this lab's `rhoSimpleFoam` setup, it is independent of the grid, and it is unresolved."* **M6CP1
reached the same attribution from the other side and found the escape.** The pattern is now
two-case and reproducible.

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

### 3.2 THE REGISTERED CONDITION

| quantity | value | provenance / status |
|---|---|---|
| M∞ | **0.850** | Sanaa's instruction; DPW5/DPW-VI case condition |
| Re(cref) | **5.0 × 10⁶** | `docs/DPW-CRM-SCOPING.md` §1 — **a lab scoping report citing URLs, NOT a title-page-verified primary source (rule 15)**. §6.1 requires the primary. |
| target CL | **0.500** | as above. DPW case 1 is a **fixed-CL** case. |
| α | **≈ 2.5° to trim to CL 0.500**, and **2.11° is the lab's own archived CRM angle** | **NOT reconciled. Registered as an open question, not as a number.** §6.1. |
| cref | **275.8 in** | scoping report; **to be confirmed against the grid** |
| Sref (semispan) | **to be measured, NOT 1.0** | §6.1 |
| MRC | **to be read from the primary reference** | §6.1 |
| grid units | **inches (inferred from the bounding box, §3.1)** | **to be confirmed, §6.1** |

**A fixed-CL case cannot be run at a guessed α, and a guessed α is how a drag number becomes
fiction.** **CRM-M085 registers α as a MEASURED input, not an assumed one**, and §6.1's limb refuses
the case rather than picking a value.

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
