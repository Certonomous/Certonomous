# PRE-REGISTRATION — VMFL069: Two Phase Poiseuille Flow

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — printed
page 205 (Test Case, Materials/Geometry/Boundary Conditions table and Analysis
Assumptions), printed page 206 (Figure .69.2, the only Results Comparison this case
carries).** The printed page maps to **PDF page 219** (offset 14), verified here by
`pdftotext -f 219 -l 219`, whose first line is *"VMFL069: Two Phase Poiseulle Flow"*
— the manual's own spelling, reproduced.

Sidecar title-page verified against the PDF beside it under `CLAUDE.md` rule 15 on
2026-08-28: the sidecar's first page reads *"Ansys Fluid Dynamics Verification Manual
/ ANSYS, Inc. / Southpointe / 2600 Ansys Drive / Canonsburg, PA 15317 / Release 2026
R1 / March 2026"*, and `pdfinfo` reports `Title: Fluid Dynamics Verification Manual`,
`Pages: 290`, `Creator: DocBook XSL Stylesheets V1.76.1`, `Producer: XEP 4.22`.
**Not by filename, file type or hash.** For the record and not as the verification:
PDF sha256 `ee1bf7ce8a7913b276b4a2b2cae020983b205f2f199a1f2301b8b7dd6b1f5511`,
sidecar sha256 `577659469a30e0f318b026545ad45e1efe2276fc0719404689db8c5a78f9c922`.

Drafted by `ansys-lane-opus`, **2026-08-28**, for the supervisor to freeze. This file
is a frozen file under `CLAUDE.md` rule 6 from the moment its commit lands: departures
are dated addenda at the foot, never edits above.

**FIRST REGISTRATION OF THIS CASE.** VMFL069 has **no** row in
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (`grep -c VMFL069`
returns **0** at 2026-08-28T17:37:08Z) and no prior VMFL069 case directory, comparator,
launcher or run root has ever existed. It is not a re-registration and it supersedes
nothing.

---

## 0. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**NOT YET RUN. NO VMFL069 SOLVER HAS EVER STARTED, ANYWHERE ON THIS BOX.** The gate,
the bands, the ceilings, the mesh family, the cap and the named outcomes below are
therefore **predictions**, which is the entire evidentiary content of this document.

Checked at **2026-08-28T17:37:08Z**, stated so a reader can re-run each check rather
than take it on trust:

| condition | how it was checked | result |
|---|---|---|
| the run root does not exist | `test -e verification/runs/ansys_verification/VMFL069` | **false** |
| it is absent from the runs tree | `ls verification/runs/ansys_verification/` — 47 entries, none `VMFL069` | **absent** |
| no VMFL069 artefact exists anywhere under the repository or `/home/ubuntu/certonomous-runs/` | `find … -iname '*VMFL069*'` outside the new case directory | **zero hits** |
| the register carries no VMFL069 row | `grep -c VMFL069` on the register | **0** |
| this case directory holds no `0/` and no numeric time directory | it contains only `case/`, this file, the comparator and the launcher | **no answer on disk** |

**There is no VMFL069 number on this box for any band, ceiling or window in this
document to have been fitted to.**

**Amendments before first compute are legal and must restate this condition and how it
was checked, naming the run directory that does not exist. After first compute the
gates close: dated addenda only, and no addendum may alter a gate, threshold, band,
cap, level or ceiling.**

**ONE FILE IS WRITTEN AFTER THIS FREEZE AND IT CHANGES NOTHING GATED.**
`PREFLIGHT_SMOKE_RECORD.txt` records a post-freeze **toolchain** smoke: the launcher's
own `VMFL_SMOKE` mode, which refuses any run root outside a scratch area, runs **L1 for
3 time steps** — about 1/600 of the slowest mode's settling time — and computes **no
gate quantity**. It exists to prove the launcher's pass path executes end to end after
the freeze check can succeed, which is only after this commit. It lands as a **separate
commit** and is a **record, not an amendment**: it alters no gate, band, ceiling, cap,
level, tolerance or verdict path, and the graded run root
`verification/runs/ansys_verification/VMFL069/` still does not exist when it is written.

---

## 1. THE TEN-LINE FORM

```
1.  CASE       : VMFL069 -- Two Phase Poiseuille Flow, manual p.205.
                 Solver = interFoam (OpenFOAM v2606), laminar, two incompressible
                 phases of EQUAL density with a FLAT, NON-DEFORMING interface at
                 mid-height; 2-D; streamwise CYCLIC pair driven by a constant
                 -dp/dx = 0.5 Pa/m applied as an fvOptions body force.
2.  REFERENCE  : THE EXACT SOLUTION OF THE SAME CONTINUUM MODEL, derived in this
                 document and re-derived independently inside the comparator:
                   lower-layer volume-mean u_x = 10           m/s   (EXACT)
                   upper-layer volume-mean u_x = 50/3         m/s   (EXACT)
                   whole-channel  volume-mean = 40/3          m/s   (EXACT)
                 The manual prints FIGURE .69.2 ONLY -- there is NO Target table
                 for this case and no number of Ansys's is used anywhere.
3.  CONTEXT    : Ansys Fluent's own curve, and Marchandise & Remacle (2006), are
                 in the manual as figures. NEITHER is read, digitised or used.
                 There is no "Ansys value" quoted in this document for context,
                 because none is legible from a figure.
4.  CEILINGS   : limb A (lower-layer mean)  -> PASS
                 limb B (upper-layer mean)  -> PASS
                 limb C (L2 profile error)  -> PASS
                 ALL THREE are CONTINUUM-EXACT limbs on a Roache triple, so this
                 row CAN be a credential -- and only if every triple is
                 CONVERGING and every limb is inside its band. Ground in sec.3.
5.  GATE       : |lab - exact| / |exact| <= 0.01 at the FINEST level L3 for limbs
                 A and B; normalised L2 profile error <= 0.01 at L3 for limb C;
                 AND a CONVERGING Roache triple on EACH limb (CLAUDE.md rule 5).
6.  CONTROLS   : planted zero in TWO stages on TWO independent channels
                 (velocity, alpha), each with a BLIND-WRITER negative arm;
                 cardinality guard on every file read; interface-stationarity,
                 streamwise-invariance, mesh-structure and plateau clauses; the
                 fvOptions-was-actually-read clause. Details in sec.8.
7.  FAMILY     : three levels, r = 2 in BOTH directions, cells 256 / 1 024 /
                 4 096 (8x32, 16x64, 32x128). Uniform; NY even at every level so
                 the interface lies on a cell FACE, never a cell centre.
8.  COMPLETION : CLAUDE.md rule 4 in full, LITERALLY -- deltaT is 1 s, so the
                 step count and the numeric endTime are the same number and no
                 clause needs adapting. Plus this case's own clauses (sec.6).
                 The comparator REFUSES (exit 2) rather than grade a partial run.
9.  COST       : ESTIMATE 8 core-min, RANKS = 1. CAP 45 core-min, RUNNING TOTAL
                 across all three solves. An overrun STOPS the run (rule 12);
                 endTime is never reduced to fit a cap. cost_basis $0.0513/core-h,
                 REPORTED-BY-OWNER, not measured.
10. PREDICTION : the observed order will be near ONE, not near two, because the
                 face interpolation of viscosity at the single interface face is
                 ARITHMETIC where the exact series resistance is HARMONIC. This
                 is a falsifiable mechanism claim registered BEFORE the run; if
                 p comes out near 2 the claim is WRONG and says so. Sec.9.
```

---

## 2. THE CASE, EXACTLY AS THE MANUAL STATES IT — AND THE THREE THINGS IT DOES NOT STATE

Manual p.205, quoted for the load-bearing sentences and reproduced without adjustment:

> *"This test case considers the horizontal stratified Poiseulle flow of two fluids
> between parallel walls. The interface between the two phases is located at half of
> the height of the channel."*
>
> *"The flow is steady. Deformation of the interface is not modeled."*

| quantity | manual p.205 | in the frozen case files |
|---|---|---|
| domain | "Dimensions of the domain: 2m X 4m" | `Lx = 2 m` (streamwise, **cyclic**), `H = 4 m` — see the ambiguity below |
| interface | "at half of the height of the channel" | `y = 2 m`, on a cell **face** at every level |
| kinematic viscosity, Fluid-1 | 0.1 | `nu 0.1` — declared the **LOWER** layer |
| kinematic viscosity, Fluid-2 | 0.02 | `nu 0.02` — the **UPPER** layer |
| density | "The two fluids have the same density" — **no value printed** | `rho 1` kg/m³ for both, **this lab's choice** |
| forcing | "Periodic Boundary is used with a Pressure Gradient = -0.5 Pa/m" | cyclic x-pair + `vectorSemiImplicitSource` of `(0.5 0 0)` N/m³ |
| surface tension | not stated; the interface is declared non-deforming | `sigma 0` |
| gravity | not stated; equal densities make buoyancy identically absent | `g (0 0 0)` |
| flow regime | "The flow is steady", laminar | `simulationType laminar` |

### 2.1 THE THREE UNDERSPECIFICATIONS, AND WHY NONE OF THEM MOVES THE GATE

**(a) Which of "2m X 4m" is the height.** The manual does not say. Resolved on the
manual's **own internal formatting precedent**: VMFL070 (p.207) writes *"Dimensions of
the domain: 2.5 m X 0.5 m"* for a case whose prose gives *"a length-to-gap aspect ratio
of 5"* and *"gap thickness … 0.5 m"* — **length first, height second**. VMFL069 is read
the same way: `Lx = 2 m`, `H = 4 m`. **This is evidence, not a coin toss, and it is
still a reading.**

**(b) The density value.** Not printed. Declared `rho = 1 kg/m³`. With equal densities
the momentum balance is `d/dy(mu du/dy) = dp/dx` with `mu = rho*nu`, so the velocity
scales as `1/rho`: a different density would give a different velocity field.

**(c) Which layer is which.** Not printed. Declared: Fluid-1 (`nu = 0.1`) is the
**lower** layer. With equal densities and no gravity the problem is exactly symmetric
under `y -> H - y` with the layers swapped, so the alternative reading gives the mirror
solution and swaps limbs A and B.

**WHY NONE OF THE THREE MOVES THE GATE, stated plainly.** The reference is **not** a
number of Ansys's; it is **the exact solution of the case as this document defines it**,
derived at exactly the declared `H`, `rho` and layer order. The gate therefore measures
**discretisation error and nothing else**, and it would measure the same thing under any
of the alternative readings — with different reference numbers, derived the same way.
**What this registration consequently does NOT claim is that its numbers can be compared
with Figure .69.2 or with Ansys's result**, and sec.12 says so again.

### 2.2 THE ARCHIVE WAS NOT OPENED

`VMFL069_WB.wbpz` exists at
`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/VMFL069_WB.wbpz`
(7 573 436 bytes) and was **not opened, extracted, listed or read** for this
registration. Everything above comes from the manual's own printed page. Neither
VM2026R1 archive copy is written to, moved or deleted by this case.

---

## 3. THE REFERENCE TIER, AND THE GROUND FOR A `PASS` CEILING

**Reference kind: THE EXACT SOLUTION OF THE SAME CONTINUUM MODEL THE SOLVER
DISCRETISES.** Not an experiment. Not a correlation. Not another code's curve.

The manual declares the model itself: steady, laminar, two incompressible phases,
**"Deformation of the interface is not modeled"**. With a flat interface that does not
move, equal densities and zero surface tension, that model **is** the steady
incompressible Navier–Stokes system with a piecewise-constant viscosity — and its
solution is a closed form. The convective term vanishes identically (`U = (u(y),0,0)`,
so `U·grad U = u du/dx = 0`), so the exact solution of the **Stokes** problem is also
the exact solution of the **Navier–Stokes** problem, at any Reynolds number.

**Model-form error is therefore ZERO BY CONSTRUCTION and the residual is discretisation
error.** That is the whole ground for the ceiling.

### 3.1 What §2f.3 caps, and what it does not

`VERIFICATION_CHARTER.md` §2f.3's classification table is headed
***"ceiling WITHOUT a triple"***, and its CONTINUUM row — which expressly includes
*"exact or manufactured solution"* — reads *"`GATE REACHED` maximum. `PASS` is
unavailable."* **That cap is the NO-TRIPLE ceiling**; the whole amendment (v1.14) is
titled *"§2f: A REGISTRATION THAT DECLARES NO ROACHE TRIPLE"*. **This registration
declares a triple**, so §2f.3 does not reach it and the ceiling reverts to
`CLAUDE.md` rule 5 step 3: *"`CONVERGING` → `PASS` inside the pre-registered band else
`GATE FAIL`"*.

**Two register precedents, both of this team's own, both exact-solution references
graded `PASS` on `CONVERGING` triples:**

- **row #2, VMFL001-R2** — Taylor–Couette against White §3-2.3, triple `CONVERGING`,
  observed order 2.0102 → **`PASS`**.
- **row #3, VMFL005** — Hagen–Poiseuille, triple `CONVERGING`, observed order 1.9341,
  0.4979 % inside a frozen 2 % → **`PASS`**.

**And the contrast that shows the rule is not being stretched: VMFL063's limb A is
capped at `GATE REACHED` even with a converging triple**, because its reference is
**experimental** (Lane & Loehrke). A converging triple bounds discretisation error and
says nothing about model-form error, so an experimental reference stays capped whatever
the triple does. **VMFL069 is on the other side of that line, and the reason it is on
the other side is that its reference is the exact solution of the model being solved.**

### 3.2 §2h is NOT invoked, and is named here so nobody reads it in

`VERIFICATION_CHARTER.md` §2h is the **floor-demonstration** clause for registrations
that carry **no triple**. **This registration does not invoke §2h, does not need it, and
claims no benefit under it.** It carries a triple and is graded under rule 5.

### 3.3 The one interpretive call, flagged for the supervisor

The `PASS` ceiling rests on reading §2f.3's cap as the **no-triple** ceiling, which is
what its own column heading and its amendment title say and what register rows #2 and #3
did. **If the supervisor reads §2f.3 as an absolute cap on every continuum limb, then
all three ceilings here become `GATE REACHED` and the case still runs and still grades —
only the best available row changes.** That is a one-line change to `TIER_CEILING` in the
comparator and must be made **before** the freeze commit, never after. It is written down
here so the call is made deliberately at the freeze and not discovered at the grade.

---

## 4. THE MESH FAMILY AND THE ROACHE TRIPLE

Single Cartesian block built by `blockMesh` from `case/system/blockMeshDict.template`:
`x ∈ [0, 2]` (streamwise, **cyclic pair** `periodicIn`/`periodicOut`), `y ∈ [0, 4]`
(walls `lowerWall`, `upperWall`, `noSlip`), one cell in `z` with `frontAndBack` `empty`.
Uniform grading `(1 1 1)` in every direction at every level.

| level | NX | NY | **cells** | Δx (m) | Δy (m) |
|---|---|---|---|---|---|
| **L1** | 8 | 32 | **256** | 0.250 | 0.125 |
| **L2** | 16 | 64 | **1 024** | 0.125 | 0.0625 |
| **L3** | 32 | 128 | **4 096** | 0.0625 | 0.03125 |

**Both counts double at every level**, so the cell count is exactly ×4 per level and the
refinement is systematic in both directions. **The grading ratio is 1 everywhere, so
there is no local-refinement-ratio caveat to make**: every local cell dimension is
exactly halved, `r = 2` is the true local ratio in both directions at every level, and
the honest caveat other cases in this family must write — that fixed grading ratios make
the *nominal* r differ from the *local* one — **does not arise here and is not being
quietly skipped.**

**NY is EVEN at every level**, so the interface at `y = 2` lies on a cell **FACE** and
never on a cell centre. The launcher refuses an odd NY; the comparator refuses if any
cell centre is within 1e-9 of the interface, and refuses if the interface does not halve
the cell count.

### The triple, and rule 5

A triple is formed on **each** limb independently: limb A on the lower-layer volume mean,
limb B on the upper-layer volume mean, limb C on the normalised L2 profile error. Each
limb's verdict is gated by **its own** triple, one-way: a triple that is not `CONVERGING`
makes that limb `NOT A RESULT` **whatever its value**, and the row verdict is the worst
limb. GCI at `Fs = 1.25` is printed **only** on a `CONVERGING` triple; the comparator
returns `gci_fine = None` for `EXACT`, `STAGNANT`, `OSCILLATORY` and `DIVERGENT`, and the
selftest drives all five states. Observed-order floor `P_MIN = 0.05`
(`FINDING_p_floor.md` §4): a triple whose `p` falls below it is `STAGNANT`, not
`CONVERGING`.

---

## 5. THE GATE

**The reference is derived below to double precision and re-derived independently inside
the comparator.** `derive_reference()` solves the three-condition linear system from the
stated problem **without using any of the frozen `REF_*` constants**, and `--selftest`
requires agreement to `1e-12`. The frozen numbers are therefore **checked, not trusted**.

### 5.1 The exact solution

In each layer `mu_i u_i'' = dp/dx = -G` with `G = 0.5 Pa/m`, subject to
`u(0) = 0`, `u(H) = 0`, velocity continuity at `y = Y = 2` and shear-stress continuity
`mu_lo u_lo'(Y) = mu_up u_up'(Y)`. With `mu_lo = 0.1`, `mu_up = 0.02`, `H = 4`:

```
u_lower(y) = -2.5  y^2 + (40/3)  y                          0 <= y <= 2
u_upper(y) = -12.5 y^2 + (200/3) y - 200/3                  2 <= y <= 4
```

| quantity | exact value | role |
|---|---|---|
| volume mean of `u_x` over `0 <= y < 2` | **10** m/s exactly | **limb A reference** |
| volume mean of `u_x` over `2 < y <= 4` | **50/3 = 16.666666666666668** m/s | **limb B reference** |
| volume mean over the whole channel | **40/3 = 13.333333333333334** m/s | limb C normaliser |
| `u_x` at the interface | 50/3 m/s | diagnostic |
| `mu du/dy` at `y = 0` | +4/3 Pa | diagnostic |
| `mu du/dy` at `y = H` | −2/3 Pa | diagnostic |
| `|tau_bottom| + |tau_top|` | **2 = G·H** | **global force balance, checked in `--selftest`** |

The force balance is not decoration: it is an independent identity the derived solution
must satisfy, and the selftest refuses if it does not.

### 5.2 The three limbs

| limb | quantity | reference | band | ceiling |
|---|---|---|---|---|
| **A** | volume-mean `u_x` over the **lower** layer (`nu = 0.1`), at L3 | 10 m/s | `|lab − 10|/10 ≤ 0.01` | `PASS` |
| **B** | volume-mean `u_x` over the **upper** layer (`nu = 0.02`), at L3 | 50/3 m/s | `|lab − 50/3|/(50/3) ≤ 0.01` | `PASS` |
| **C** | normalised L2 error of the whole cell-centre profile against the exact solution, at L3 | 0 | `sqrt(mean((u_i − u_exact(y_i))²)) / (40/3) ≤ 0.01` | `PASS` |

**Why volume means and not a sampled profile.** The mesh is uniform and every cell has
the same volume, so the arithmetic mean over a layer's cells **is** its volume mean,
exactly. No `sample`, no `interpolationScheme`, no `.xy` file, no interpolation error
between the solver and the gate: the comparator reads the raw `U` and `Cy` fields
OpenFOAM wrote and does the arithmetic itself.

**Why limb C exists beside A and B.** A and B are averages, and an average can be right
while the shape is wrong. Limb C is the shape. It also gives the planted-zero control a
functional that **every** cell enters, which is what makes an all-cell plant visible to
it (L-340).

**THE BAND IS ONE NUMBER, 1.0 %, FOR ALL THREE LIMBS**, chosen from the a-priori error
estimate in sec.9 and not from any run. Per-limb bands tuned to per-limb predictions
would look fitted and are refused.

---

## 6. STRICT COMPLETION (`CLAUDE.md` rule 4, IN FULL AND LITERALLY)

`deltaT = 1 s` and `endTime = 2000 s`, so **the number of time steps and the numeric
`endTime` are the same number** and rule 4's clauses hold **literally, with no
adaptation** — unlike a steady solve, which has to adapt them. The comparator
**REFUSES (exit 2)** on any failed clause rather than grading a partial run.

| # | clause | class |
|---|---|---|
| 1 | `rc = 0` from `RUN_RC.<level>` | **INFRASTRUCTURE** (L-342): absent → `rc NOT MEASURED`, disclosed, grading proceeds; present and non-zero → **REFUSE** |
| 2 | an `End` line in `log.interFoam` | physics-critical |
| 3 | **the fvOptions markers are in the log** — see sec.6.1 | physics-critical |
| 4 | last `Time` **==** `endTime` (2000) | physics-critical |
| 5 | `ExecutionTime` count **==** `endTime` (2000) | physics-critical |
| 6 | `controlDict` carries the registered `endTime` **and** `deltaT` | physics-critical |
| 7 | `U`, `p_rgh`, `alpha.fluid1`, `Cx`, `Cy` all present at `endTime`; `U` present at `t = 1500` | physics-critical |
| 8 | the **numerically**-latest time directory (`key=float`) == the log's last `Time` | physics-critical |
| 9 | **AGE GUARD**: every field at `endTime` strictly **newer** than the case's own `0/U`, which the launcher touches LAST, after `setFields` and immediately before the solver | physics-critical |
| 10 | **PLATEAU**: the two layer means at `t = 1500` and `t = 2000` agree to `1e-6` relative (rule 5 limb 1) | physics-critical |
| 11 | **INTERFACE STATIONARITY**: `max |alpha − alpha_0| ≤ 1e-9` over every cell | physics-critical |
| 12 | **STREAMWISE INVARIANCE**: the widest spread of `u_x` within any single y-row `≤ 1e-6` of the reference mean | physics-critical |
| 13 | **MESH STRUCTURE**: NX distinct x-columns, NY distinct y-rows, `NX*NY` cells, no cell centre on the interface, the interface halves the cell count | physics-critical |

### 6.1 Clause 3 exists because of a silent-failure hazard measured in the v2606 source

`src/finiteVolume/cfdTools/general/fvOptions/fvOptions.C:50-93` looks for
`constant/fvOptions` **first** and `system/fvOptions` **second**, and **if neither
exists it sets `NO_READ` and applies nothing — without an error.** The body force is the
**only** forcing in this case, so a misplaced or misnamed `fvOptions` gives a quiet
**zero-velocity** run that completes cleanly and looks like physics. That is L-339's
*"a fix that appears applied and does nothing"* in a different organ.

The defence is the line `fvOptions.C:86-91` prints **only when the file was actually
read**. Both the launcher and the frozen comparator require **all four** of:

```
Creating finite-volume options from
constant/fvOptions
Source: streamwisePressureGradient
State: active
```

**The exact rendering was MEASURED, not recalled** — the log line carries quotes around
the path (`from "constant/fvOptions"`), which a guard matching the unquoted whole line
would have missed. It was found in the pre-flight toolchain smoke, which is why the two
fragments are matched separately.

### 6.2 Clauses 11 and 12 are physics claims about the registered case, not tidiness

With equal densities, zero surface tension, a flat interface and `U` parallel to it, the
alpha field is an **exact steady state** of the VOF system: the wall-normal volumetric
flux is identically zero and alpha is uniform in `x`, so both the advective and the
compression fluxes across the interface vanish. **A run whose interface moved did not
solve the registered case**, and the comparator refuses rather than grade it. The same
holds for streamwise invariance: cyclic streamwise patches plus a uniform body force
admit nothing else, so any x-variation is a defect — a broken cyclic pair, a misapplied
source, or a transitional instability (sec.10, outcome 5).

---

## 7. COST (`CLAUDE.md` rule 12)

| | |
|---|---|
| **unit** | core-minutes = wall_s × RANKS / 60 |
| **RANKS** | **1** (serial; the largest level is 4 096 cells — decomposition would cost more than it saves) |
| **ESTIMATE** | **8 core-min** for all three levels together |
| **CAP** | **45 core-min**, and **the cap's SHAPE is a RUNNING TOTAL across all three solves**, not a per-solve cap. Each level's `timeout_s` is `(CAP − spent) × 60 / RANKS`, computed in the launcher's executable path immediately before that level starts. |
| **overrun** | **STOPS the run** (rc 124). The run does not get a new budget and `endTime` is NEVER reduced to fit a cap. |
| **cost_basis** | `$0.0513/core-h`, c7a.4xlarge, **owner-stated 2026-08-21/22 — REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **derived**. |
| **derived dollars at the estimate** | 8 core-min = 0.1333 core-h × $0.0513 = **$0.0068** — derived, not measured |
| **derived dollars at the cap** | 45 core-min = 0.75 core-h × $0.0513 = **$0.0385** — derived, not measured |
| **GPU** | **none. This is a CPU case.** No GPU is attached and none is requested, so the GPU carve-out of rule 12 does not apply. |

**How the estimate was reached, honestly.** 2 000 time steps at each of 256, 1 024 and
4 096 cells, plus `blockMesh`, `checkMesh`, `setFields` and one `postProcess` pass per
level. The estimate is **not** measured — it is a projection from the cell counts and the
step count, and it is deliberately generous because the per-step cost of interFoam's
PIMPLE loop on this box has not been measured for this case. **The cap is ~5.6× the
estimate**, the same ratio VMFL063 registered, and it exists to stop a stall, not to
license one.

**Estimate-versus-actual calibration is owed at completion** (rule 12, Sanaa's directive
of 2026-08-23): actual core-minutes from `RUN_RC.*` against the 8 core-min above, the
ratio, the attribution, and one row in `docs/COST_CALIBRATION.md`. A completion report
without that row is incomplete.

---

## 8. THE PLANTED-ZERO CONTROL (`CLAUDE.md` rule 3)

**TWO STAGES ON TWO INDEPENDENT CHANNELS, EACH WITH A NEGATIVE ARM.** This family has
lost two rungs to one-stage plants and the design here is shaped by both.

### Channel 1 — VELOCITY (`U`)

- **P1a — reader sensitivity.** A **sized** plant `0.05 × 40/3 = 0.6667 m/s` is added to
  the x-component of **every internal cell** of a **copy of the real solver file**, on
  the real bytes, and read back **from disk** through the real reader. Every value must
  have moved by exactly the plant. **Sized**, because an averaging reader dilutes a fixed
  single-point plant by ~`1/sqrt(N)` and the control then refuses a working reader
  (L-340, register row #26). **Every cell**, because a correctly sized point plant can
  land outside the reader's support (L-347, register row #31).
- **P1b — GATE-FUNCTIONAL sensitivity.** The **same planted file** is pushed through the
  **full gate functional**. Three things must happen or the control refuses: the
  lower-layer mean must move by **exactly** the plant; the planted mean must fall
  **OUTSIDE** the frozen 1 % band (0.6667 m/s on a 10 m/s reference is 6.67 %, so the
  gate must flip from inside to outside); and the limb-C profile error must **rise**.
  **A plant the raw reader sees but the gate does not is the row-#31 failure and it
  refuses here.**

### Channel 2 — VOLUME FRACTION (`alpha.fluid1`)

- **P1a** as above, `+0.05` into every cell of a copy.
- **P1b** — the gate functional here is the **interface-stationarity clause**, and the
  planted file must make it **REFUSE**. This is a genuinely different decider from
  channel 1's, not the same one in another costume.

### The negative arms — L-314, applied to the control itself

For **both** channels the selftest runs the control with a **blind writer** — a writer
that does not write — and requires the control to **REFUSE**. A control that passes when
the plant never reaches disk is measuring itself. **And the two arms are checked to
refuse for DIFFERENT REASONS**: L-314 addendum 2 records that two arms failing with the
same message are one arm, so the selftest compares the blind-writer refusal text against
the cardinality-guard refusal text and requires them to differ and to name their own
clause.

### Everything else the comparator refuses on

Every file is opened through `one_match()`, which **refuses unless exactly one path
matches**. **No `sorted(glob.glob(...))[-1]` appears in this comparator** — verified by a
token-level scan, not by eye: zero occurrences outside comments and strings. This
matters more here than in most cases, because **this case writes time directories 500,
1000, 1500 and 2000, whose LEXICOGRAPHIC maximum is `500` and whose NUMERIC maximum is
`2000`.** The hazard is **live in this very case**, the comparator sorts `key=float`,
cross-checks against the log's own last `Time`, and **records in the grading JSON that
the lexicographic reading would have been wrong**. The selftest drives the exact
`0 / 950 / 2000` case the supervisor named.

**No `assert` statement appears in the comparator.** `python3 -O` deletes every assert,
so a control written as one is not a control (L-332). `_ast_guard()` walks the file's own
AST and refuses if the `ast.Assert` count is not 0; it runs on the **grading** path as
well as in `--selftest`.

---

## 9. ERROR BUDGET AND THE PRE-REGISTERED MECHANISM CLAIM — disclosed BEFORE the freeze

### 9.1 Where the discretisation error comes from, and why it is FIRST order

interFoam's viscous term is `fvm::laplacian(rho*nuEff, U)`, whose face coefficient comes
from `interpolate((rho*nuEff))` and so from `fvSchemes`'
`interpolationSchemes { default linear; }`. On a uniform mesh `linear` is the
**arithmetic** mean. At the one face where `mu` jumps from 0.1 to 0.02 the discrete face
conductance is `(mu1+mu2)/2 = 0.06`, while the exact two-half-cell series resistance
requires the **harmonic** mean `2 mu1 mu2/(mu1+mu2) = 0.0333…` — **too large by
`(mu1+mu2)²/(4 mu1 mu2) = 1.8`.**

That is an **O(1)** error in one face's **conductance**. It does not destroy consistency,
because the face **resistance** and its error both vanish like `h`; but it demotes the
scheme from second order to **first order** at the interface while everything away from
it stays second order. Away from the interface the scheme is in fact **exact** for this
problem — the FV Laplacian is exact on a quadratic, and the wall treatment shifts the
whole discrete profile by a constant `G h²/(8 mu)`, which is `O(h²)`.

> **THE PRE-REGISTERED PREDICTION: the observed order will be near ONE, not near two.
> If the run returns `p ≈ 2`, this mechanism claim is WRONG and the record will say so.**

`harmonic` interpolation is available in OpenFOAM and would restore second order. **It is
deliberately NOT chosen here**, because choosing it after seeing a result would be
selection by outcome. It is named in sec.12 as the successor rung's single change.

### 9.2 The a-priori error estimate the band was set from

**Disclosed in full, because a band has to come from somewhere and it must not come from
a run.** An **independent one-dimensional finite-volume model** of the same
discretisation — same uniform mesh, same arithmetic face viscosity, same wall treatment —
was solved in Python before the freeze. **It is not this lab's solver, it is not the
registered case, and it produced no gate value.** Its purpose was to size the band.

| level (NY) | limb A rel. error | limb B rel. error | limb C norm |
|---|---|---|---|
| L1 (32) | 0.600 % | 1.018 % | 1.264 % |
| L2 (64) | 0.266 % | 0.602 % | 0.676 % |
| L3 (128) | **0.124 %** | **0.324 %** | **0.350 %** |
| implied observed order (L2→L3) | 1.10 | 0.89 | 0.95 |

Counterfactual, same model with **harmonic** face viscosity: 0.0081 % / 0.0244 % /
0.0165 % at L3 and `p = 2.000` exactly — which is the evidence for the sec.9.1 mechanism
claim.

**The frozen band of 1.0 % gives margins of 8.1× (A), 3.1× (B) and 2.9× (C) against this
estimate.** Note that **limb B's estimated error at L1 already exceeds the band** — the
gate is on **L3**, and the coarse level is expected to be outside it.

**THE GATE CAN FAIL, and the estimate is not a promise.** The 1-D model omits everything
the real run adds: the PIMPLE pressure–velocity coupling, the cyclic pair, MULES, the
transient approach, and any 2-D effect. Any of them, and any defect in the case files,
would move the answer far past 1 %.

### 9.3 The transient, and why 2 000 steps

The slowest eigenvalue of the discrete two-layer diffusion operator gives a time constant
of **33.4 / 33.6 / 33.7 s** at L1 / L2 / L3. With implicit Euler at `deltaT = 1 s` the
slowest mode's per-step amplification is 0.9711, so the discrete steady state is reached
to `1e-9` in about **708 steps**. `endTime = 2000` is **~60 τ** and about 2.8× the steps
needed. The **plateau clause** (sec.6 clause 10) is what actually checks this, by
comparing `t = 1500` with `t = 2000`; it is not left to the estimate.

The convective Courant number is large (of order 350 at L3) and that is **deliberate and
harmless**: `ddt`, the Laplacian and `div(rhoPhi,U)` are all implicit, the wall-normal
convective flux is identically zero, and alpha is x-uniform so its flux differences
cancel — the pre-flight toolchain smoke recorded `Interface Courant Number max: 0`.
**The interface-stationarity clause is what makes that reasoning checkable rather than
merely asserted.**

### 9.4 Round-off

Fields are written `ascii` at `writePrecision 12`. The gate quantities are means over
256–4 096 doubles of magnitude ~10 m/s; accumulated round-off is of order
`1e-12 × sqrt(N) ≈ 1e-10` relative, **eight orders of magnitude below the 1 % band**.
Round-off is not a limiting error here.

---

## 10. NAMED LIVE OUTCOMES — every one can happen, and each is written down now

1. **Any limb's triple is not `CONVERGING`.** That limb is `NOT A RESULT` whatever its
   value; the row is `NOT A RESULT`. Most likely on limb B, whose predicted `p` is 0.89
   and whose error sequence is the shallowest.
2. **A limb's `p` falls below `P_MIN = 0.05`.** `STAGNANT`, `NOT A RESULT`, and **no GCI
   is quoted**.
3. **The finest level is outside the 1 % band.** `GATE FAIL` on that limb, honestly, and
   the row is `GATE FAIL`. Predicted margins are 2.9–8.1×, and a prediction is not a
   result.
4. **The interface moves.** MULES at a large Courant number is the plausible mechanism.
   The comparator **REFUSES**; `NOT A RESULT`.
5. **The solution loses streamwise invariance.** The upper layer's Reynolds number on the
   exact solution is of order 4 000, below plane-Poiseuille's linear critical value but
   not trivially so; a broken cyclic pair would do it too. The comparator **REFUSES**;
   `NOT A RESULT`.
6. **fvOptions is not read.** An unforced, zero-velocity run. Both the launcher and the
   comparator **ABORT/REFUSE** on the log markers; `NOT A RESULT`, and loudly.
7. **The solve has not plateaued at `t = 2000`.** **REFUSE**; `NOT A RESULT`.
8. **`rc != 0`, including 124.** The running-total cap fired or the solver died. The
   launcher **stops at the first non-zero rc and does not launch later levels**; the
   comparator refuses on a recorded non-zero rc. `NOT A RESULT`, and the spend is
   reported.
9. **`p ≈ 2` instead of `p ≈ 1`.** The sec.9.1 **mechanism claim is falsified**. The
   verdict is unaffected — a converging triple is a converging triple — and the record
   must say the prediction was wrong.
10. **The interpretive call in sec.3.3 goes the other way.** All three ceilings become
    `GATE REACHED` and the row cannot be a credential. Decided at the freeze, never after.

---

## 11. THE GRADING PATH, FROZEN

| artefact | path |
|---|---|
| pre-registration | `cases/ansys_verification/VMFL069/PREREGISTRATION.md` (this file) |
| comparator | `cases/ansys_verification/VMFL069/grade_vmfl069.py` |
| launcher | `cases/ansys_verification/VMFL069/run_vmfl069.sh` |
| case inputs | `cases/ansys_verification/VMFL069/case/` — **12 files**, each hashed against its own HEAD blob at launch |
| run root | `verification/runs/ansys_verification/VMFL069/` — **does not exist** |
| grading record | `verification/runs/ansys_verification/VMFL069/GRADING_VMFL069.json` |

**The grading path is fixed at this commit.** The launcher hashes this file and the
comparator against their HEAD blobs before it does anything else and **aborts** if either
differs; `grade_vmfl069.py --verify-frozen` does the same on demand, deriving the
repository root from `git rev-parse --show-toplevel` rather than by counting `dirname`s
(L-314 addendum 2). **Verify the frozen file IS the file that ran by hashing it against
the committed blob** — that is what both do.

**Launch:** `bash cases/ansys_verification/VMFL069/run_vmfl069.sh verification/runs/ansys_verification/VMFL069`
**Grade:** `python3 cases/ansys_verification/VMFL069/grade_vmfl069.py --run-root verification/runs/ansys_verification/VMFL069 --out verification/runs/ansys_verification/VMFL069/GRADING_VMFL069.json`

**QUEUE NOTE, and it is a filing requirement, not a preference.** `scripts/queue_runner.py`
writes `STATUS.<case_id>`, the wrapper's stdout and `CAP_OVERRUN.txt` into the entry's
**`cwd`**. The entry for this case must set **`cwd` to the run root**
`verification/runs/ansys_verification/VMFL069`, **never** to the case directory — runtime
artefacts beside frozen files is exactly what `FILING_CHARTER` R6 forbids, and it would
also put unhashed files next to the twelve this launcher hashes.

### 11.1 The launcher's own guards, and both outcomes driven

`run_vmfl069.sh` gates with explicit `|| { echo ABORT…; exit 2; }` on every check. **`set
-e` is not relied on** — at agent-tool top level it is suppressed because the command is a
non-final `&&` member (L-314 addendum 3) — and **`set -u` is categorically absent**,
because sourcing the v2606 bashrc dereferences `WM_PROJECT_DIR` before assigning it.

**The selftest gate is the AMENDED, SATISFIABLE form from birth.** VMFL063's original
gate required **byte-identical** `--selftest` output under both interpreters, which is
**unsatisfiable by construction**: the sandbox is a `tempfile.mkdtemp()` whose random
absolute path is quoted in the output, so **two runs of the same interpreter also
differ**. **A guard that cannot pass is as broken as one that cannot fail.** This
launcher compares **PASS count, FAIL count and exit rc**, requires the **AST-guard marker
under BOTH** interpreters, and greps for **22 named control markers** that must each have
been **driven**.

**No shim is installed by this launcher.** Sourcing the OpenFOAM bashrc **prepends**
OpenFOAM's own `bin` to `PATH`, so a `blockMesh`/`checkMesh` shim placed on `PATH` earlier
would be **silently overridden**. The launcher records the binary it actually resolved.

---

## 12. WHAT THIS REGISTRATION DOES NOT CLAIM

- **It does not claim to reproduce Ansys's result.** The manual prints Figure .69.2 and
  no numeric Target for this case. **No curve is digitised, no figure is read, and no
  Ansys number appears anywhere in this document, in the comparator or in the case
  files.** This is the deliberate opposite of VMFL011, whose reference existed only as a
  figure and which consumed three rungs before terminating.
- **It does not claim to reproduce Marchandise & Remacle (2006).** That paper is not on
  this box and was not read. It is the manual's cited reference and is named for
  provenance only.
- **It does not claim the manual's geometry, density or layer order have been
  established.** Three quantities are underspecified (sec.2.1); this document *declares*
  them and derives its reference at the declared values.
- **It does not claim the answer is mesh-independent.** It claims what three levels
  measure and nothing about meshes not run.
- **It does not claim a validated physical model.** There is no experiment here. This is
  **verification** — code and solution verification against an exact solution — and
  nothing in it speaks to whether the model describes a real stratified flow.
- **It does not claim that OpenFOAM's default `linear` viscosity interpolation is
  wrong.** It claims that on this problem it is first order at the interface, and it
  predicts the number before measuring it.

### The named successor, registered now so it cannot be chosen by outcome

**VMFL069-R2, if it is ever run, changes ONE line**: `fvSchemes`'
`interpolationSchemes` gains `interpolate((rho*nuEff)) harmonic;`. Everything else — the
mesh family, the bands, the ceilings, the cap, the controls — is unchanged. Its purpose
is to test whether the observed order returns to 2, and **it is registered here, before
this rung runs, precisely so that running it later cannot be a reaction to an
unwelcome result.**
