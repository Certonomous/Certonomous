# K0eR2. Forced-convection flat plate, Bahrami (2005): PRE-REGISTRATION

**Registered 2026-09-03T19:3xZ, BEFORE ANY K0eR2 COMPUTE.** Zero core-minutes
have ever been spent against K0eR2.
`verification/runs/F14-cooling-ladder/K0eR2_runs/` does not exist at this write,
and this document does not create it.

**The absence was CHECKED, not asserted, and under a planted control** (standing
rule 3): a reader returned **ABSENT** on `K0eR2_runs` while the **same reader**
returned **PRESENT** on `K0f_runs`, which does exist.

**This document SUPERSEDES `K0e_PREREGISTRATION.md`**, which is marked superseded
by its own `AMENDMENT 1` and is **not edited** (standing rule 6). K0e is the
predecessor; **the physics problem is identical and the gate structure is not.**

---

## 0. WHAT VERDICTS THIS RUNG CAN REACH — stated first

**Exactly one row is GATED: `M4b`, the same-solver neutralisation control.
Threshold `0` ULP.**

| | |
| --- | --- |
| **Reachable rung verdicts** | **`PASS`** (M4b at 0 ULP) or **`NOT A RESULT`** (M4b non-zero, or a completion clause failed on either arm) |
| **Not reachable, by construction** | **`GATE FAIL`** — no band is armed anywhere in this rung (§3) |
| **Not reachable, by construction** | a `PASS` **on the Stanton comparison** — REPORTED, never graded |
| **Changed from K0e** | **`M4` is now REPORTED, NOT GATED** (§5.1) |

**A `PASS` here means `beta` and `g` were demonstrated neutral, so a Stanton
error on this rung is attributable to the thermal closure alone. It does not
mean the thermal closure was validated** — §2.1.3's circularity caution is why.

---

## 1. WHY THIS RUNG

**It breaks the confound `THERMAL_CAPABILITY_STATE.md` §5 names as binding.**
Every graded thermal result this lab owns is a buoyant cavity in which momentum
and thermal fields are **both wrong and coupled through buoyancy**, so no error
is attributable. **`K0cR` is the proof**: fixing the stress closure moved
velocity **19 points TOWARD** experiment and wall heat flux **30 points AWAY**,
in the same solves.

With `beta = 0` and `g = (0 0 0)` there is no buoyancy coupling, so any
Stanton-number error is attributable to the thermal closure **alone**.
**Attribution — not validation — is what this rung buys.**

---

## 2. THE REFERENCE, ITS TIER, AND ITS TITLE-PAGE VERIFICATION

**Bahrami, P. A. (2005). *Heat Transfer on a Flat Plate with Uniform and Step
Temperature Distributions.* NASA/TM–2005-212841. May 2005.** Tier **READ IN
FULL** (D430).

| check | result |
| --- | --- |
| Path | `docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf` |
| sha256 recomputed on disk | `0cd29adb20c0f6c21c07f37f101f0f8d3f3a7f85a81a95abc023da25a66f8be6` — **MATCHES** the recorded digest |
| **Title page, standing rule 15** | **page 1 of the PDF rendered and READ**, not inferred from filename or hash: `NASA/TM–2005-212841`; "Heat Transfer on a Flat Plate with Uniform and Step Temperature Distributions"; "Parviz A. Bahrami"; "May 2005". **VERIFIED.** |

**Equation (1), as printed** (`.txt` sidecar line 353):

    St = 0.0296 Re^-0.2 (Pr Tw / T_inf)^-0.4

with `St = q / (Cp_inf rho_inf U_inf dT)` (line 441).

### 2.1 Three limits carried into the design

1. **The primary is NOT OBTAINED.** Moretti & Kays (1965) exists here only as
   figures inside this secondary. **No row grades against their data.**
2. **Equation (1) is a correlation, not a measurement.**
3. **Circularity, the load-bearing caution.** Eq. (1) is Colburn-type and sits in
   the family of the Reynolds and Von Karman analogies. **The Reynolds analogy is
   close to what a constant-`Prt` gradient-diffusion closure asserts**, so
   agreement between a `Prt = 0.85` RANS solve and eq. (1) is **partly structural
   rather than evidential**. `Pr^-0.4` against `Pr^-2/3` is the only genuinely
   testing part, **and at `Pr = 0.71` that gap is small.**

---

## 3. NO BAND IS ARMED ON THE CORRELATION

**This rung REPORTS the Stanton number against equation (1). It does NOT gate on
it. No band is armed, because none can be honestly derived from the source in
hand.**

Bahrami states uncertainties for Moretti & Kays — temperature 3 %, heat flux
2 %, velocity 1 % — **but those belong to their experiment, not to equation (1)**,
and the document states no uncertainty for the correlation itself.
`LITERATURE_CHARTER.md` §2 forbids a fourth tier for *"widely reported"*, **so
the correlation's conventional accuracy may not be invoked to arm a band.**

**And the tempting alternative is the one the discipline exists to prevent.**
Bahrami reports two-equation models at *"deviations of approximately 10
percent"*. **Setting the band to ~10 % would be setting the gate to what we
expect to achieve.** Standing rule 2 is the assertion that the gate could not
have been chosen to fit the answer; **a band chosen from the published
expectation is a band chosen to be met.** Not armed, and this paragraph is why.

**What would arm one later:** a source stating eq. (1)'s own uncertainty, or the
Moretti & Kays primary. Neither is held.

---

## 4. THE CASE

The lab's existing TMR flat plate, `/home/ubuntu/certonomous-runs/tmr-flatplate-finer`.

| item | value | source |
| --- | --- | --- |
| Cells | **52 224** | `log.checkMesh`; `constant/birth_certificate.json` |
| **Max non-orthogonality** | **0** | same — **and this is asserted by the grader before any wall gradient is read** (§8.4) |
| Max skewness | 4.376137948e-14 | same |
| Max aspect ratio | **65 467.84834**, birth-certificate verdict **`flagged`** | same — §6.2 |
| `nu` | 2e-07 m2/s | `constant/transportProperties` |
| `U_inf` | 1.0 m/s | `0/U` |
| Plate | `x = 0` to `2.0 m`, **208 wall faces** (`startFace 104704`) | `constant/polyMesh/boundary` |
| **Plate cell spacing** | **min 4.493756e-04 m**, max 4.394886e-02 m | **MEASURED** on the preflight case (§6.4) |
| `Re_x` range | 0 to 1.0e7 | `U_inf x / nu` |
| `y+` on the plate | min 0.0592, max 0.2088 | `postProcessing/yPlus1/0/yPlus.dat` — **wall-resolved** |
| Momentum reference | `log.simpleFoam`, 9000 iterations, **2 ranks**, ClockTime 840 s | the same case |

**Comparison is at matched `Re_x`, not at matched dimensional velocity.**

### 4.1 Thermal setup

| item | value | reason |
| --- | --- | --- |
| Solver | `buoyantBoussinesqSimpleFoam` (OpenFOAM **v2606**) | the solver the whole thermal ladder uses |
| `beta` | **0** | removes buoyancy exactly |
| `g` | **(0 0 0)** | removes it again, independently |
| `TRef`, `T_inf` | 300 K | |
| `Pr` | 0.71 | air |
| `Prt` | 0.85 | the ladder's value; comparable to K0cS and K0cX |
| **`div(phi,T)`** | **`bounded Gauss limitedLinear 1`** | **NEW, and the defect that killed K0e** — §4.2 |
| `alphat` on the plate | `calculated`, value 0 | wall-resolved: `nutLowReWallFunction` and `y+ <= 0.209` give `nut_wall = 0`, hence `alphat_wall = 0`. **An `alphatJayatillekeWallFunction` would impose a high-Re thermal law on a resolved wall** and is deliberately not used |
| `endTime` | **9000**, `startFrom 0` | identical to the momentum reference |
| Decomposition | **2 ranks, COPIED from the reference**, not re-derived | `scotch` re-derives; a cell-for-cell comparison across two derivations is meaningless. `build_k0e.py` copies `processorN/constant/polyMesh` including `cellProcAddressing` and runs `decomposePar -fields` |

### 4.2 `div(phi,T)` — REGISTERED HERE, AND WHY K0e DIED WITHOUT IT

**K0e's case was built by copying the reference's `system/`. The reference is a
`simpleFoam` case: it solves no energy equation, so its `divSchemes` correctly
carries no `div(phi,T)`, and its `default none;` turns that inherited omission
into a LAUNCH-TIME FATAL rather than a silent default.** `K0e_FP_T10` exited
**rc=1 in 0 wall seconds** on exactly that.

**The scheme registered here is the LADDER'S OWN, not this document's
invention**: `bounded Gauss limitedLinear 1` is what **K0f**
(`K0f_runs/M1_c/system/fvSchemes:22`) and **K0cS**
(`K0cS_runs/S_SST_c/system/fvSchemes:28`) register for `div(phi,T)`. K0eR2 exists
to be comparable to those rungs, so it adopts their scheme.

**It touches no momentum-relevant scheme.** `div(phi,U)`, `gradSchemes`,
`laplacianSchemes`, `snGradSchemes` and `interpolationSchemes` are copied
byte-unchanged, so **the momentum rows are unaffected by this addition.**
`build_k0e.py` carries three refusals around the edit: refuse if the reference
already has `div(phi,T)`; refuse if the edit did not take; refuse if the
`div(phi,U)` entry count moved.

### 4.3 The two arms

| arm | `T_wall` | `dT` | purpose |
| --- | --- | --- | --- |
| **`FP_T10`** | 310 K | **10 K** | the thermal arm; `Tw/T_inf = 1.033333`, so eq. (1)'s temperature-ratio factor is **applied, not neglected** |
| **`FP_T00`** | 300 K | **0 K exactly** | the zero-`dT` control **and the second operand of the gated row** |

**`dT = 10 K` is small on purpose**: large enough that Stanton is well
conditioned, small enough that constant properties hold and a Boussinesq solver
with `beta = 0` is not asked to represent variable-density physics.

---

## 5. WHAT IS MEASURED, AND WHICH ROW IS GATED

| # | quantity | against | status |
| --- | --- | --- | --- |
| **M1** | `St(Re_x)` at six stations | eq. (1) | **REPORTED, NO BAND** (§3) |
| **M2** | `Cf(Re_x)` | the reference's own field, same reader | **REPORTED** (control) |
| **M3** | `Prt_eff = nut/alphat` | — | **REPORTED**, and read as a CONVERGENCE diagnostic (§6.5) |
| **M4** | cross-solver ULP distance, `FP_T10` vs recorded `simpleFoam` | 0 ULP | **REPORTED, NOT GATED** — §5.1 |
| **M4b** | same-solver ULP distance, `FP_T10` vs `FP_T00` | **0 ULP** | **GATED. Non-zero → `NOT A RESULT`.** |
| **M5** | thermal BL thickness, near-wall `alphat` | — | **REPORTED** |
| **M6** | zero-`dT` wall heat flux | identically zero | **REPORTED** |

**Reported stations, fixed before any compute:**
`Re_x = 1.0e6, 2.0e6, 3.0e6, 5.0e6, 7.0e6, 1.0e7` — nearest plate face to each
target, with the actual `Re_x` printed beside the value.

**Eq. (1) at those stations (`Pr = 0.71`, `Tw/T_inf = 310/300`), computed and
committed before any K0eR2 case directory exists:**

| `Re_x` | `St` from eq. (1) |
| ---: | ---: |
| 1.0e6 | **2.113938e-03** |
| 2.0e6 | **1.840290e-03** |
| 3.0e6 | **1.696946e-03** |
| 5.0e6 | **1.532139e-03** |
| 7.0e6 | **1.432427e-03** |
| 1.0e7 | **1.333805e-03** |

### 5.1 THE GATE IS `M4b`, AND `M4` CANNOT CARRY IT

**THE THRESHOLD IS ZERO, EXPRESSED IN ULP OF THE OPERANDS.** `analyse_k0e.py`
maps each IEEE-754 binary64 to a monotone signed-magnitude integer key and
reports `|k(a) - k(b)|`, the number of representable doubles between them. **The
registered threshold is `0` ULP on every component of every cell,
processor-local.** `+0.0` and `-0.0` are one value; a `NaN` refuses.

**There is no tolerance constant anywhere in the comparator, and there must never
be one.** A hardcoded "equivalent" epsilon is a band nobody registered, arrived
at after the fact. **This ULP condition is the one verification attached to the
spine §2d.1 grant, and it binds this rung.**

**THE GATING REASON, in the form Sanaa's 2026-09-03 20:00Z ruling requires:**

> **Without `M4b`, the verdict on the Stanton attribution cannot be trusted,
> because a momentum field that moved WHEN ONLY THE WALL TEMPERATURE CHANGED
> means `beta` and `g` were not actually neutralised, and the attribution of any
> Stanton-number error to the thermal closure is void.**

**WHY `M4` IS DEMOTED, and it is a source finding rather than a preference.**
Read from the installed v2606 source:

- `simpleFoam/UEqn.H`: `solve(UEqn == -fvc::grad(p));`
- `buoyantBoussinesqSimpleFoam/UEqn.H`:
  `solve(UEqn == fvc::reconstruct((-ghf*fvc::snGrad(rhok) - fvc::snGrad(p_rgh))*mesh.magSf()));`

With `g = 0` the `ghf*snGrad(rhok)` term is an exact-zero field and adding it
changes no bit. **But `fvc::grad` and `fvc::reconstruct(snGrad(...)*magSf)` are
DIFFERENT DISCRETE OPERATORS, and they differ INDEPENDENTLY of `beta` and `g`.**
A non-zero `M4` therefore **conflates "`beta`/`g` leaked" with "the two operators
are not identical" and cannot separate them. A gate that cannot answer its own
gating question is not a gate**, so `M4` is REPORTED and `M4b` is gated.

**`M4b` has no such confound**: one binary, one operator set, two wall
temperatures. With `beta = 0` the thermal field cannot enter the momentum
equation at all, so a moved momentum field means one thing only.

**THE PAIR IS DIAGNOSTIC, and this is registered so the reading is not invented
afterwards:** `M4b` at 0 ULP with `M4` non-zero is **the signature of the
operator difference and of nothing else.** `M4b` non-zero is a `beta`/`g` leak,
whatever `M4` reads.

**THE SECONDARY LIMIT, carried forward from K0e §6.1.** Both fields are written
`writeFormat ascii; writePrecision 10`. Every ULP comparison here is therefore
bit-for-bit **on the recorded artifact**, which carries ten significant decimal
digits. **0 ULP means the two agreed to at least the written precision and
rounded identically; it does not by itself prove agreement in the unwritten
low-order bits. The gate is a NECESSARY condition, not a sufficient one.**

---

## 6. PREDICTIONS AND PREFLIGHT FINDINGS REGISTERED BEFORE COMPUTE

### 6.1 PREDICTION 1 — `M4` will very likely be non-zero, and that is now REPORTED rather than fatal

On the §5.1 mechanism. **Under K0e this prediction would have made the rung
`NOT A RESULT`; under K0eR2 it is a reported number**, and the gate is carried by
the row that can actually answer the question. **`M4b` is predicted 0 ULP.**

### 6.2 PREDICTION 2 — a mesh-standard mismatch, recorded and launched

Max aspect ratio **65 467.85**, birth-certificate verdict `flagged`. Under the
21:00Z ruling a mesh-quality mismatch is a **prediction, not a blocker**.
**Predicted benign:** a wall-resolved zero-pressure-gradient boundary-layer mesh
is *supposed* to be extreme in aspect ratio, and this same mesh produced the
momentum solution the lab records. Predicted-versus-actual on the certificate.

### 6.3 PREDICTION 3 — where the Stanton comparison lands, and this is NOT a band

**Predicted `|St - St_eq1|/St_eq1` of order 10 % or less**, from Bahrami's own
statement. **THIS IS A PREDICTION AND NOT A BAND, NOT A THRESHOLD, NOT A GATE.**
It cannot produce `PASS` and cannot produce `GATE FAIL`. §3 is unaffected.

### 6.4 PREFLIGHT, RUN BEFORE THIS DOCUMENT WAS FROZEN — three findings

A **5-iteration** smoke case was built with the fixed builder and run at 2 ranks
(`K0e_runs/PREFLIGHT/FP_T10/log.smoke`, `ClockTime 3 s`, **rc = 0**). It was run
**because the supervisor required the function-object question answered before
queueing**, not to produce a number, and **it grades nothing**.

1. **FUNCTION OBJECTS: PASS.** The `functions` block inherited from the reference
   — `forceCoeffs1`, `yPlus1`, `wallShearStress1` and a `surfaces` object —
   **all executed and wrote under `buoyantBoussinesqSimpleFoam`, with no error.**
   `reconstructPar -latestTime` rc=0 and `postProcess -func writeCellCentres`
   rc=0, producing every field the grader reads including `C`, `T` and `alphat`.
   **There is no second blocking physics fix.**
2. **THE ORTHOGONALITY ASSERTION WAS WRONG AND IS FIXED** — §8.4.
3. **`Prt_eff` MEASURES CONVERGENCE, NOT PHYSICS** — §6.5.

### 6.5 `M3` IS A CONVERGENCE DIAGNOSTIC — registered so it is not misread as physics

`buoyantBoussinesqSimpleFoam` sets `alphat = nut/Prt` in `TEqn.H` and then
updates `nut` in `turbulence->correct()` **later in the same outer iteration**,
so the two written fields are **one turbulence correction apart**. **Any spread in
`nut/alphat` is the residual change in `nut` over one outer iteration — never a
physical variation of the turbulent Prandtl number, which is a constant in this
solver.**

**MEASURED on the 5-iteration preflight: min 0.4391, max 1.5470, zero cells at
exactly 0.85**, on a field nowhere near converged. A converged solve should drive
the spread toward zero.

**This CONFIRMS D424's transmission finding rather than weakening it:** `alphat`
is slaved to `nut` by a constant, so **this quantity cannot report on the physics
at all.** That is the finding.

---

## 7. COST — A POINT ESTIMATE, WITH THE CAP IN A SEPARATE COLUMN

### 7.1 The basis, measured

| quantity | value | source |
| --- | --- | --- |
| Reference `simpleFoam` solve, this exact mesh | **28.00 core-min** = 840 wall s × 2 ranks ÷ 60 | `log.simpleFoam`: `ExecutionTime = 639.56 s  ClockTime = 840 s`, 9000 iterations |
| Measured rate | **3.5747e-06 core-s per cell-iteration** | 840 × 2 ÷ (52 224 × 9000) |
| Solver factor | **1.25**, an **ESTIMATE, not a measurement** | segregated solves per outer iteration 6 → 7 (`+T`), i.e. **1.167**, rounded up for the `alphaEff` assembly and `alphat` update |
| Comparator, measured | **0.29 wall s** per 52 224-cell vector field pair, ~20 reads per grade | measured through the production reader |

**The preflight's own rate is NOT used and must not be**: 5 iterations at
`ClockTime 3 s` is **2.30e-05 core-s/cell-iteration**, six times the reference
rate, because solver startup dominates a 5-iteration run. **A rate measured over
a startup-dominated run is not a rate.**

### 7.2 The registered figures

| | POINT (the prediction) | CAP (the guard) |
| --- | ---: | ---: |
| `FP_T10` | **35.00 core-min** | **105.00 core-min** (3× POINT; `--timeout 3150` s at 2 ranks) |
| `FP_T00` | **35.00 core-min** | **105.00 core-min** (`--timeout 3150` s at 2 ranks) |
| grader, one invocation | **0.10 core-min** | **0.30 core-min** |
| **RUNG** | **70.10 core-min** | **CEILING 210.30 core-min** |

**Derived dollars at $0.0513/core-h: POINT `$0.0599`, ceiling `$0.1798`.**
**DERIVED, NOT MEASURED.** `cost_basis`: **reported-by-owner** — this box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**The two columns are different instruments and are not collapsed** (L-463): the
POINT is the prediction rule 12's ratio divides by; the CAP is the guard that
stops a runaway. **An overrun stops the run; it does not get a new budget.**

**The momentum reference solve is NOT re-run.**

### 7.3 ALREADY SPENT AGAINST THE PREDECESSOR, NAMED SEPARATELY AND NOT ABSORBED

**Per `COMPUTE_BUDGET_CHARTER.md` §6, waste is reported, never folded into a
ratio.**

| item | core-min | class |
| --- | ---: | --- |
| K0e attempt 1 (`FP_T10`, rc=1, `wall=0`) | **0.00** solver time; one mesh copy + `decomposePar` | **WASTE** — it bought nothing |
| K0eR2 preflight (5 iterations, 2 ranks, `ClockTime 3 s`) | **0.10** | **PREFLIGHT, not waste** — it answered the function-object question the supervisor required and found two instrument defects (§6.4) |

**Neither figure enters the §7.2 POINT and neither may be absorbed into the
rung's actual/predicted ratio.** Both are carried into the `COST_CALIBRATION.md`
row when this rung completes.

---

## 8. THE CONTROLS, ARMED HERE

### 8.1 Planted-zero control (standing rule 3) — three plants, P2 separate on purpose

| plant | what | into | must |
| --- | --- | --- | --- |
| **P1** | `1.234e-03` K | a **copy** of `FP_T10`'s `endTime` `T`, **BY LINE INDEX** | be **SEEN** by the production scalar reader, else REFUSE |
| **P2** | `1.234e-03` m/s into the **X-COMPONENT** | a **copy** of `FP_T10`'s `endTime` `U`, by line index | be **SEEN** by the production **VECTOR** reader, else REFUSE |
| **P3** | exactly `0.0` | a copy of the same `T` | **NOT fire**, else REFUSE |

**P2 is separate because a scalar plant does not exercise a vector reader**, and
**the gated row reads vectors.** Each plant goes into the **field file the graded
path reads** — never a dict, a spec or a constants table — and is read back
through the **same function the graded path calls**. All three are matched at
**0 ULP**, not at a tolerance.

**All three were EXERCISED on the preflight case before this document was
frozen** and all three behaved: P1 read back `0.001234`, P2 read back `0.001234`
through the vector parser, P3 did not fire, against a live background of
`T = 300.0` and `U = (1.0, 7.691926087e-13, 0.0)`.

### 8.2 Strict completion rule (standing rule 4) — all-or-nothing, both arms

Both arms must satisfy **every** clause: `rc = 0` from `STATUS.<arm>`; an `End`
line; **last time == `endTime` 9000**; fields `T U p_rgh alphat nut k omega`
present at `endTime`; `ExecutionTime` count == 9000; **every field at `endTime`
NEWER than the case's own `0/T`**.

**The gated row needs BOTH arms**, so a `NOT DONE` on either is `NOT A RESULT`
for the rung. **A gated row that cannot be measured cannot yield a `PASS`.**

**The age-guard datum is `<case>/0/T`, verified for this case rather than
assumed.** K0eR2 is **single-region** — one mesh, one case, no regions — so `0/T`
is the correct dating file. It is *valid* only because `scripts/launch_k0e.sh`
**touches `0/T` last, after the build and immediately before the solver**, and
nothing writes it afterwards.

**`build_k0e.py` REFUSES (exit 2) a case already holding `0/` or any numeric time
directory**, on the reconstructed and the decomposed side.

**K0d is why both are spelled out.** K0d had **no launcher**, so no `STATUS` was
written, so **clause 1 was unverifiable on both arms** (`K0d_RESULTS.md` §4.1).

### 8.3 Roache triple gating (standing rule 5) — NO TRIPLE IS FORMED

**Two arms on ONE mesh (52 224 cells). No grid triple exists, rule 5 does not
engage, no GCI is computed and none is printed.** Quoting a GCI where no triple
exists would be inventing a convergence claim, and the comparator cannot.

**This is a registered limitation:** every K0eR2 number carries **no
discretisation bound at all.**

### 8.4 THE ORTHOGONALITY ASSERTION — corrected before compute, and its power measured

The wall gradient is read as `(value_face - value_owner)/d`, which is **exact
only on an orthogonal mesh**.

**K0e's grader asserted this by comparing the owner cell's `x` with the face's
`x` at `1e-12`, and it REFUSED on the preflight case** at plate face 14, where
the two coordinates read `0.007521543256` and `0.007521543255`. **That is one
unit in the TENTH significant digit — exactly the resolution of `writePrecision
10`. The assertion was testing ASCII round-off and calling it
non-orthogonality.**

**Corrected, and the correction is structural rather than a loosened epsilon:**

1. **The orthogonality evidence is now `checkMesh`'s MEASUREMENT.** The grader
   reads `constant/birth_certificate.json` from the case — `build_k0e.py` copies
   it with the mesh so the case is self-describing — and **REFUSES if
   `max_non_orthogonality` is absent or non-zero.** This mesh's measured value is
   **0**.
2. **The per-face check is reduced to what it can honestly be**: a consistency
   bound at the **written precision**, `2e-9 × max(1, |x|)` — one unit in the
   10th significant digit, doubled, because the two coordinates round
   independently and can round in opposite directions. **DERIVED from the write
   format, not chosen.**

**ITS DISCRIMINATING POWER WAS MEASURED, NOT ARGUED**: over all 208 plate faces
the worst `|x_cell - x_face|` is **1.000000e-09** (pure round-off), while the
**smallest plate cell spacing is 4.493756e-04 m**. A genuinely misaligned face
would show a difference of order that spacing — **five orders of magnitude above
the bound.** The bound sits in the gap, not near either edge.

---

## 9. THE FROZEN GRADING PATH — pinned by blob sha, hash function named

**The grading path is fixed at this commit** (standing rule 2). All three files
are committed **in the same commit as this document**, and **every pin is re-cut
here**; K0e's §9 pins are superseded.

| file | **GIT BLOB SHA-1** |
| --- | --- |
| **`scripts/analyse_k0e.py`** — the grader | **`25ecaa6bca8cd99f4ca1e0a84dba998cde923aaa`** |
| `scripts/build_k0e.py` — the case builder | `ed290d4f94aefb6dce2991d0382152784bb82216` |
| `scripts/launch_k0e.sh` — the launcher | `6479fe4e67a15fd186b7c5afc26f57ae874b4bcc` |

**THE HASH FUNCTION IS NAMED SO THE PIN CANNOT BE CHECKED AGAINST THE WRONG
DIGEST.** These are **git blob SHA-1**:

    sha1( b"blob " + str(len(content)).encode() + b"\0" + content )

**NOT sha256, and NOT a plain sha1 of the file's bytes.** `git hash-object <path>`
reproduces them; `sha1sum` and `sha256sum` do not. `analyse_k0e.py` computes its
own by the same definition and **REFUSES (exit 2)** when invoked as

    python3 scripts/analyse_k0e.py --root <K0eR2_runs> --scratch <dir> \
        --expect-sha 25ecaa6bca8cd99f4ca1e0a84dba998cde923aaa

and is not that blob. **The grade is only valid with `--expect-sha` armed.**

**The script filenames keep the `k0e` stem deliberately.** The physics problem,
the case and the arms are the predecessor's; only the gate structure and one
scheme changed. Renaming three files would have produced a diff nobody could read
as a diff, and the pins above are what identify the version that ran.

---

## 10. WHAT THIS RUNG CANNOT DO

- **It cannot validate a thermal closure** (§2.1.3).
- **It cannot fail a model** — no band is armed (§3).
- **It cannot bound its own discretisation error** — no triple (§8.3).
- **`M4` cannot gate** (§5.1), and a non-zero `M4` is not a defect of this rung.
- **It is not the mixed-convection rung.** K0d is `BLOCKED`; K0f supersedes it.
- **It says nothing about buoyant flows.**
- **Nothing here is sent, filed, uploaded, registered or posted. PARKED.**

---

## 11. WHAT CHANGED FROM `K0e_PREREGISTRATION.md`

| # | change | reason |
| --- | --- | --- |
| 1 | **`div(phi,T) bounded Gauss limitedLinear 1` registered** | K0e inherited the reference's scheme set and `default none;` made the omission a launch-time fatal (§4.2) |
| 2 | **The gate moves `M4` → `M4b`; `M4` becomes REPORTED** | `M4` compares two binaries whose discrete pressure-gradient operators differ independently of `beta`/`g`, so it cannot answer its own gating question (§5.1) |
| 3 | **Orthogonality asserted from `checkMesh`, per-face bound derived from `writePrecision 10`** | the old `1e-12` assertion was testing ASCII round-off (§8.4) |
| 4 | **`M3` registered as a convergence diagnostic** | `alphat` and `nut` are written one turbulence correction apart (§6.5) |
| 5 | **Preflight findings and their spend registered** | §6.4, §7.3 |
| 6 | **All §9 pins re-cut** | the grader and builder both changed |

**Unchanged and carried forward verbatim in substance:** the reference and its
title-page verification; **no band, and §3's reasoning**; the case and its two
arms; the 0-ULP threshold with no tolerance constant; the three planted zeros
including the vector plant; the strict completion rule and age guard; no Roache
triple and no GCI; the `writePrecision 10` secondary limit; **`GATE FAIL`
unreachable**; and the cost POINT-plus-cap shape.

---

## 12. QUEUE AND LAUNCH

Launches are **daemon-only**. Entries are dropped in
`verification/queue/heat-transfer/` and picked up by `scripts/queue_runner.py` on
its one-minute tick. Run root: `verification/runs/F14-cooling-ladder/K0eR2_runs/`.

**If the box is over the runner's busy ceiling the entry QUEUES** — Sanaa's
21:00Z ruling: a resource gate queues and the run stays scheduled. **That is not
a block, not a refusal and not a `BLOCKED` verdict.** The rung's state until the
daemon takes it is **`PENDING`**.

---

*Registered by a heat-transfer lane on the supervisor's ruling of 2026-09-03.
This lane assigns the rung no verdict. Nothing was sent, filed, uploaded,
registered or posted — submissions are PARKED.*

---

# AMENDMENT 1 — 2026-09-03. **§3 CHECK 1 (the grading-path diff-read) IS DISCHARGED.** Version 1.0 → **1.1**

**Appended at the foot. Nothing above is edited** (standing rule 6).
**Lines whose number changed above this section: 0.**

**MEASURED, not asserted.** In the invocation that wrote this amendment: lines
above, before the append **529**; sha256 before
`3fcdc00b07b8a34d800166b1c06a1f395d39241b05acebf3f9487beca7c8389a`; the sha256 of the first **529** lines after the append is **recomputed
and required to equal it, else the write is abandoned**; and `git diff --numstat`
on the landing commit is required to read **`<additions> 0`** — zero deletions.

**THE PRE-COMPUTE CONDITION, and how it was checked.** Standing rule 2 permits
amendment **before first compute**, and requires the condition be stated with the
method: **`verification/runs/F14-cooling-ladder/K0eR2_runs/FP_T10` and
`.../FP_T00` DO NOT EXIST, and no `K0eR2_runs/STATUS.*` file exists.** Checked
under a planted control (rule 3): the same reader returned **20** `STATUS.*`
files for `K0f_runs`, so it is demonstrably able to see a non-zero.
**Zero core-minutes have been spent against K0eR2.**

**This amendment alters no gate, no threshold, no cap and no label**, and re-cuts
no pin. It records the status of a check.

---

## A1.1 THE CHECK, AND WHAT WAS ACTUALLY DONE

`SUPERVISION_CHARTER.md` §3 check 1 — **measurement-script diffs read as diffs** —
is the supervisor's own and may never be delegated. The grader
`scripts/analyse_k0e.py` changed between the superseded `K0e` freeze (blob
`695becd6…`) and this document's §9 pin (blob `25ecaa6b…`), so the check was
owed. The diff is filed at
`docs/campaigns/F14-cooling-ladder/K0e_DIFF_2_GATE_TO_M4b.diff`, **267 lines**.

**DISCHARGED 2026-09-03, and the account is the supervisor's own correction
rather than their first description of it.** Recorded in the order it happened,
because the sequence is the point:

1. The supervisor first reported the diff **"read and approved — all 267 lines"**.
2. **The supervisor then corrected that themselves, unprompted.** What had
   actually been read at that moment was a **filtered extraction** — a grep of
   the `+`/`-` lines with comment-only and blank lines excluded — **not the file
   end to end.**
3. The supervisor then **read the file end to end, all 267 lines**, and issued
   the correction naming the first description as false.

**The approval is unchanged and was not weakened by the correction. Only the
description of the read was wrong, and it was the supervisor who found it.**

**THE DATE OF THE FULL READ IS THE CORRECTION, NOT THE FIRST REPORT**, and this
record is written that way deliberately.

## A1.2 WHY THIS IS RECORDED RATHER THAN QUIETLY FIXED

**Approving a measurement-script diff from a filtered view and calling it a full
read is the same failure the graded rows on this rung exist to catch**: a summary
statistic standing in for the underlying values. This registration already
carries two instances of it found in this lane's own work — a `1e-12` assertion
that was measuring ASCII round-off (§8.4) and a `Prt_eff` spread that reads like
physics and is a convergence residual (§6.5).

**The correction is therefore evidence that the check works, not evidence
against it**, and burying it would have cost more than it saved.

## A1.3 WHAT THE FULL READ ADDED — none of it changing the verdict

Recorded because a check that produced findings is worth more on the record than
one that produced only an approval:

- **The removed `UNMEASURED` branch is stricter than the filtered view showed.**
  The old grader could reach `m4b = None` and print an `UNMEASURED` row when the
  control arm was `NOT DONE`. The new grader **cannot reach that state at all** —
  §8.2's both-arms requirement returns `NOT A RESULT` before the comparison.
- **The verdict block is correct in both branches**, and the `NOT A RESULT`
  branch ends *"The reported rows above stand as measurements and as NOTHING
  MORE."*
- **`float(bc["max_non_orthogonality"]) != 0.0` is an exact comparison against
  zero** — any non-zero refuses, which is the strict direction.
- **`import json` sits inside the function rather than at module scope.**
  Harmless, and **deliberately not fixed**: this file is pinned by §9, and
  re-cutting a frozen pin for style would be the tail wagging the dog.

## A1.4 WHAT IS NOW OWED ON K0eR2

**Nothing, until the daemon launches it.** Both queue entries were held on the
runner's busy ceiling at every tick from 19:40:20Z. **That is a resource gate
queueing — `PENDING`, not blocked.**

*Amendment by a heat-transfer lane, 2026-09-03. No verdict is assigned by this
amendment. Nothing sent — submissions are PARKED.*
