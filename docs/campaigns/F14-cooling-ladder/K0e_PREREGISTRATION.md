# K0e. Forced-convection flat plate, Bahrami (2005): PRE-REGISTRATION

**Registered 2026-09-03T19:2xZ, BEFORE ANY K0e COMPUTE.** Zero core-minutes have
ever been spent against K0e.

**The absence was CHECKED, not asserted, and under a planted control** (standing
rule 3): in the invocation that wrote this section a reader returned **ABSENT**
on `verification/runs/F14-cooling-ladder/K0e_runs` while the **same reader**
returned **PRESENT** on `verification/runs/F14-cooling-ladder/K0f_runs`, which
does exist. A zero from a reader not shown able to see a non-zero is not
evidence.

This document **adopts** the 2026-08-19 specification
`K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` and **does not edit it** (standing
rule 6). Where this registration departs from that specification the departure
is named in §11, with its reason, and the specification's own wording is quoted
rather than replaced.

---

## 0. WHAT VERDICTS THIS RUNG CAN REACH — stated first, so no reader discovers it late

**Exactly one row is GATED: `M4`, the momentum control. Its threshold is `0`
ULP.**

| | |
| --- | --- |
| **Reachable rung verdicts** | **`PASS`** (M4 at 0 ULP) or **`NOT A RESULT`** (M4 non-zero, or a completion clause failed) |
| **Not reachable, by construction** | **`GATE FAIL`** — no band is armed anywhere in this rung (§3), so there is no band to fall outside of |
| **Not reachable, by construction** | a `PASS` **on the Stanton comparison** — that row is REPORTED, never graded |

**A `PASS` here means the momentum field was demonstrated invariant. It does not
mean the thermal closure was validated, and §2.1.3's circularity caution is the
reason.** Every other row on this rung — the Stanton comparison against eq. (1),
`Prt_eff`, the skin friction, the thermal boundary layer, the zero-`dT` control —
is **REPORTED, NOT GATED**, which is the lab default since Sanaa's 2026-09-03
20:00Z ruling.

---

## 1. WHY THIS RUNG, AND WHAT IT BUYS

**It breaks the confound that `THERMAL_CAPABILITY_STATE.md` §5 names as binding.**
Every graded thermal result this lab owns is a buoyant cavity in which the
momentum field and the thermal field are **both wrong and coupled through
buoyancy**, so no error can be attributed to either closure.

**`K0cR` is the proof, and it is quoted here rather than summarised**: fixing the
stress closure moved the velocity field **19 points TOWARD** the experiment and
the wall heat flux **30 points AWAY**, in the same solves
(`THERMAL_CAPABILITY_STATE.md` §5; `K0cR_RESULTS.md`).

With `beta = 0` and `g = (0 0 0)` there is **no buoyancy coupling at all**, so any
Stanton-number error is attributable to the thermal closure **alone**.

**That attribution — not a validation — is what this rung buys.** It is worth
saying the negative too: this rung does not make the thermal closure right, does
not make it wrong, and does not transfer any cavity finding to any other flow.
It makes one thermal error *attributable*, on one flow, for the first time.

---

## 2. THE REFERENCE, ITS TIER, AND ITS TITLE-PAGE VERIFICATION

**Bahrami, P. A. (2005). *Heat Transfer on a Flat Plate with Uniform and Step
Temperature Distributions.* NASA/TM–2005-212841. May 2005.**
Tier **READ IN FULL** (D430).

| check | result |
| --- | --- |
| Path | `docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf` |
| sha256 **on disk, recomputed for this registration** | `0cd29adb20c0f6c21c07f37f101f0f8d3f3a7f85a81a95abc023da25a66f8be6` — **MATCHES** the digest recorded in `THERMAL_CAPABILITY_STATE.md` addendum 2 |
| **Title page read, standing rule 15** | page 1 of the PDF **rendered and read**, not inferred from the filename or the hash: report number **`NASA/TM–2005-212841`**, title **"Heat Transfer on a Flat Plate with Uniform and Step Temperature Distributions"**, author **"Parviz A. Bahrami"**, date **"May 2005"**, NASA insignia present. **VERIFIED — the title page is the document the citation claims.** |

**Rule 15 exists because a manifest can be internally consistent and externally
false.** The sha256 match above is therefore *not* the verification; the title
page is. Both are recorded because they answer different questions.

**Equation (1), as printed** (`bahrami_2005_nasa_tm_212841.txt` line 353):

    St = 0.0296 Re^-0.2 (Pr Tw / T_inf)^-0.4

with **`St = q / (Cp_inf rho_inf U_inf dT)`** (line 441) and `Re` on distance from
the leading edge and free-stream properties.

### 2.1 Three limits, carried into the design rather than discovered in the results

1. **The primary is NOT OBTAINED.** Moretti & Kays (1965) exists in this library
   only as figures inside this secondary. **No row below grades against their
   data.**
2. **Equation (1) is a correlation, not a measurement.** It is an empirical fit.
3. **Circularity, and it is the load-bearing caution.** Eq. (1) is Colburn-type
   and sits in the family of the Reynolds and Von Karman analogies. **The
   Reynolds analogy is close to what a constant-`Prt` gradient-diffusion closure
   asserts**, so agreement between a `Prt = 0.85` RANS solve and eq. (1) is
   **partly structural rather than evidential**. The `Pr^-0.4` exponent against
   the analogy's `Pr^-2/3` is the only part of the comparison that is genuinely a
   test, **and at `Pr = 0.71` that gap is small.**

---

## 3. NO BAND IS ARMED ON THE CORRELATION, AND THIS IS THE CENTRAL DESIGN DECISION

**This rung REPORTS the Stanton number against equation (1). It does NOT gate on
it. No band is armed, because no band can be honestly derived from the source in
hand.**

Bahrami states measurement uncertainties for Moretti & Kays — temperature 3 %,
heat flux 2 %, velocity 1 % — **but those belong to their step-temperature
experiment, not to equation (1)**, and the document states no uncertainty for the
correlation itself.

`LITERATURE_CHARTER.md` §2 forbids a fourth tier for *"well known"*, *"standard
result"* or *"widely reported"*, **so the correlation's conventional accuracy may
not be invoked to arm a band.**

**And the tempting alternative is the one the whole discipline exists to
prevent.** Bahrami reports two-equation models sitting at *"deviations of
approximately 10 percent"* from the Von Karman analogy. **Setting the band to
~10 % would be setting the gate to what we expect to achieve.** Standing rule 2
is not a procedure about when a file is committed; it is the assertion that the
gate could not have been chosen to fit the answer. **A band chosen from the
published expectation is a band chosen to be met.** It is not armed here, and
this paragraph is the reason.

**What would arm a band later:** a source stating equation (1)'s own uncertainty,
or the Moretti & Kays primary data. Neither is held. **Until one is, this row is a
MEASUREMENT with a reported deviation and nothing more.**

---

## 4. THE CASE

The lab's existing TMR flat plate, `/home/ubuntu/certonomous-runs/tmr-flatplate-finer`.

| item | value | source |
| --- | --- | --- |
| Cells | **52 224** | `log.checkMesh`; `constant/birth_certificate.json` |
| Max non-orthogonality | **0** | same |
| Max skewness | **4.376137948e-14** | same |
| Max aspect ratio | **65 467.84834**, birth-certificate verdict **`flagged`** | same — see §6.2 |
| `nu` | **2e-07 m2/s** | `constant/transportProperties` |
| `U_inf` | **1.0 m/s** | `0/U` |
| Plate | `x = 0` to `x = 2.0 m`, 208 wall faces, symmetry section upstream | `constant/polyMesh/boundary` (`nFaces 208`, `startFace 104704`) |
| `Re_x` range | **0 to 1.0e7** | `U_inf x / nu` |
| `y+` on the plate | **min 0.0592, max 0.2088, mean 0.0729** | `postProcessing/yPlus1/0/yPlus.dat` — **wall-resolved** |
| Momentum reference | `log.simpleFoam`, 9000 iterations, **2 ranks**, `ClockTime 840 s` | the same case |

**Comparison is made at matched `Re_x`, not at matched dimensional velocity.**
Bahrami's `Re/x = 1 215 400 m^-1` falls inside this plate's first quarter metre.

### 4.1 Thermal setup

| item | value | reason |
| --- | --- | --- |
| Solver | `buoyantBoussinesqSimpleFoam` (OpenFOAM **v2606**) | the solver the whole thermal ladder uses, so the closure is the same object |
| `beta` | **0** | removes buoyancy exactly |
| `g` | **(0 0 0)** | removes it again, independently |
| `TRef` | 300 K | |
| `T_inf` | 300 K | |
| `Pr` | 0.71 | air |
| `Prt` | 0.85 | the ladder's value, so this rung is comparable to K0cS and K0cX |
| `alphat` on the plate | `calculated`, value 0 | **wall-resolved**: `nut` carries `nutLowReWallFunction` and `y+ <= 0.209`, so `nut_wall = 0` and `alphat_wall = nut_wall/Prt = 0`. **An `alphatJayatillekeWallFunction` here would impose a high-Re thermal law on a resolved wall** and is deliberately not used. |
| `endTime` | **9000**, `startFrom 0` | **identical to the momentum reference** — M4 compares the two at the same iteration count from the same initial state |
| Decomposition | **2 ranks, COPIED from the reference**, not re-derived | `method scotch` re-derives; a cell-for-cell comparison across two derivations is meaningless. `build_k0e.py` copies `processorN/constant/polyMesh` including `cellProcAddressing` and runs `decomposePar -fields`, which maps fields onto the existing processor meshes and derives nothing. |

### 4.2 The two arms

| arm | `T_wall` | `dT` | purpose |
| --- | --- | --- | --- |
| **`FP_T10`** | 310 K | **10 K** | the graded arm; `Tw/T_inf = 1.033333`, so eq. (1)'s temperature-ratio factor is near unity and is **applied, not neglected** |
| **`FP_T00`** | 300 K | **0 K exactly** | the zero-`dT` control, and the same-solver discriminator of §5.1 |

**`dT = 10 K` is chosen small on purpose**: large enough that Stanton is well
conditioned, small enough that constant properties hold and that a Boussinesq
solver with `beta = 0` is not being asked to represent variable-density physics.

---

## 5. WHAT IS MEASURED, AND WHICH ROW IS GATED

| # | quantity | against | status |
| --- | --- | --- | --- |
| **M1** | `St(Re_x)` at six stations | eq. (1) | **REPORTED, NO BAND** (§3) |
| **M2** | `Cf(Re_x)` | the reference's own field, through the same reader | **REPORTED** (control) |
| **M3** | `Prt_eff = nut/alphat` through the boundary layer | — | **REPORTED**; this is the quantity D424 found pinned at exactly 0.8500 on the cavity |
| **M4** | momentum control: ULP distance between `FP_T10`'s `U` at `endTime` and the recorded `simpleFoam` `U`, **processor-local, every component of every cell** | **0 ULP** | **GATED. Non-zero → `NOT A RESULT`.** |
| **M4b** | same-solver neutralisation control: ULP distance between `FP_T10` and `FP_T00` | 0 ULP | **REPORTED** — the discriminator, §5.1 |
| **M5** | thermal boundary-layer thickness and the near-wall `alphat` profile | — | **REPORTED** |
| **M6** | zero-`dT` wall heat flux | identically zero | **REPORTED** |

**Reported stations, fixed here before any compute:**
`Re_x = 1.0e6, 2.0e6, 3.0e6, 5.0e6, 7.0e6, 1.0e7` — the plate face whose centre
is nearest each target, with the actual `Re_x` printed beside the value.

**Eq. (1) at those stations, with `Pr = 0.71` and `Tw/T_inf = 310/300`, computed
and committed BEFORE any case directory existed:**

| `Re_x` | `St` from eq. (1) |
| ---: | ---: |
| 1.0e6 | **2.113938e-03** |
| 2.0e6 | **1.840290e-03** |
| 3.0e6 | **1.696946e-03** |
| 5.0e6 | **1.532139e-03** |
| 7.0e6 | **1.432427e-03** |
| 1.0e7 | **1.333805e-03** |

### 5.1 M4 — THE THRESHOLD, THE GATING REASON, AND THE DISCRIMINATOR

**THE THRESHOLD IS ZERO, EXPRESSED IN ULP OF THE OPERANDS.**

`analyse_k0e.py` maps each IEEE-754 binary64 to a monotone signed-magnitude
integer key and reports `|k(a) - k(b)|`, the number of representable doubles
between the two operands. **The registered threshold is `0` ULP on every
component of every cell.** `+0.0` and `-0.0` are one value; a `NaN` refuses.

**There is no tolerance constant anywhere in the comparator, and there must
never be one.** A hardcoded "equivalent" epsilon — `1e-12`, `1e-15`, machine
epsilon times anything — is a band nobody registered, arrived at after the fact,
and it would convert this gate into exactly the kind of chosen-to-be-met band §3
refuses. **This ULP condition is the one verification attached to the spine
§2d.1 grant, and it binds this rung.**

**THE GATING REASON, in the form Sanaa's 2026-09-03 20:00Z ruling requires:**

> **Without M4, the verdict on the Stanton attribution cannot be trusted, because
> a momentum field that moved means `beta` and `g` were not actually neutralised,
> and the attribution of any Stanton-number error to the thermal closure is
> void.**

That sentence is why M4 survives the reported-not-gated default while every other
row on this rung drops to reporting: **no other row on this rung can produce it.**
`Prt_eff` cannot — nothing downstream depends on it. The Stanton comparison
cannot — it has no band to be trusted or distrusted against.

**M4b, THE DISCRIMINATOR, AND WHY IT IS REPORTED RATHER THAN GATED.**
M4 compares **two different solver binaries**. M4b compares **the same binary
with itself** at two wall temperatures. With `beta = 0` the thermal field cannot
enter the momentum equation at all, so M4b must read 0 ULP on physics grounds
alone, and it isolates a `beta`/`g` leak from a solver-identity difference —
which M4, on its own, cannot separate. **It is registered as REPORTED because the
gate structure of this rung is the supervisor's call and this document does not
add a gate; it is registered at all because if M4 fails, M4b is the row that says
whether the cause is the physics or the binary.**

---

## 6. PREDICTIONS REGISTERED BEFORE COMPUTE

Under Sanaa's 2026-09-03 21:00Z ruling a standard-mismatch is **recorded as a
prediction and the run launches**; only ill-posed physics or a resource gate
stops one, and a resource gate **queues**. Three predictions are registered here
and each will be compared against the outcome on the certificate.

### 6.1 PREDICTION 1 — M4 will very likely be NON-ZERO, and the mechanism is named from the source

**Read from the installed source, not from memory:**

- `applications/solvers/incompressible/simpleFoam/UEqn.H` solves
  `solve(UEqn == -fvc::grad(p));`
- `applications/solvers/heatTransfer/buoyantBoussinesqSimpleFoam/UEqn.H` solves
  `solve(UEqn == fvc::reconstruct((-ghf*fvc::snGrad(rhok) - fvc::snGrad(p_rgh))*mesh.magSf()));`

With `g = 0` the `ghf*snGrad(rhok)` term is an exact-zero field and adding it
changes no bit. **But `fvc::grad` and `fvc::reconstruct(snGrad(...)*magSf)` are
DIFFERENT DISCRETE OPERATORS.** They agree in the continuum limit and are not
required to agree bit-for-bit, or even to agree at all, on a given mesh. **So the
2026-08-19 specification's assertion that "the velocity field must reproduce the
recorded `simpleFoam` solution to machine zero" rests on an identity the two
solvers do not have**, independently of `beta` and `g`.

**PREDICTED OUTCOME: `M4` non-zero, therefore rung `NOT A RESULT`.** The
threshold is not weakened by this prediction — that would be the rescue standing
rule 2 forbids. **The prediction is registered so that the outcome is a
calibration of the gate rather than a surprise**, and M4b is registered so that,
if the prediction holds, the lab learns which of the two mechanisms produced it.

**A second, smaller limit on M4, registered rather than discovered.** Both fields
are written `writeFormat ascii; writePrecision 10`. The comparison is therefore
bit-for-bit **on the recorded artifact**, which carries ten significant decimal
digits. **0 ULP there means the two solvers agreed to at least the written
precision and rounded identically; it does not by itself prove agreement in the
unwritten low-order bits.** M4 is a NECESSARY condition, not a sufficient one,
and it is registered as such.

### 6.2 PREDICTION 2 — a mesh-standard mismatch, recorded and launched

The mesh's **max aspect ratio is 65 467.85** and its birth certificate reads
`"verdict": "flagged"`. Under the 21:00Z ruling a mesh-quality mismatch is a
**prediction, not a blocker**: it is recorded here and the run launches.
**Predicted:** the flag is benign for this rung, because a wall-resolved
zero-pressure-gradient boundary-layer mesh is *supposed* to be extreme in aspect
ratio, and the same mesh already produced the momentum solution this lab
records. **Predicted-versus-actual goes on the certificate.**

### 6.3 PREDICTION 3 — where the Stanton comparison will land, and this is NOT a band

Bahrami reports two-equation models at *"deviations of approximately 10
percent"*. **Predicted: `|St - St_eq1|/St_eq1` of order 10 % or less at the
reported stations.**

**THIS IS A PREDICTION AND IT IS NOT A BAND, NOT A THRESHOLD AND NOT A GATE.** It
cannot produce `PASS` and it cannot produce `GATE FAIL`. It exists so the
certificate can say whether the published expectation held, which is a different
claim from saying the model was validated. §3 is unaffected by it.

---

## 7. COST — A POINT ESTIMATE, WITH THE CAP IN A SEPARATE COLUMN

**The 2026-08-19 specification priced this rung at *"of order 0.5-1.5
core-hours"*. That is a RANGE, and a range is forbidden (L-463): an inequality or
an interval supplies no denominator, so the rule-12 calibration row can only ever
report a bound on a ratio rather than a ratio, and the prediction becomes
unfalsifiable.** It is converted here to a POINT, with the cap kept in its own
column — the shape L-463 requires.

### 7.1 The basis, measured

| quantity | value | source |
| --- | --- | --- |
| Reference `simpleFoam` solve, this exact mesh | **28.00 core-min** = 840 wall s × 2 ranks ÷ 60 | `log.simpleFoam` last line: `ExecutionTime = 639.56 s  ClockTime = 840 s`, 9000 iterations |
| Measured rate | **3.5747e-06 core-s per cell-iteration** | 840 × 2 ÷ (52 224 × 9000) |
| Solver factor, `buoyantBoussinesqSimpleFoam` / `simpleFoam` | **1.25**, an **ESTIMATE, not a measurement** | segregated linear solves per outer iteration go from 6 (`U`×3, `p`, `k`, `omega`) to 7 (`+T`), i.e. **1.167**, rounded up to 1.25 to cover the `alphaEff` assembly and the `alphat` update |
| Comparator, measured | **0.29 wall s** to read a 52 224-cell vector field pair through the production reader; ~20 such reads per grade | measured in this registration's own invocation |

### 7.2 The registered figures

| | POINT (the prediction) | CAP (the guard) |
| --- | ---: | ---: |
| `FP_T10` | **35.00 core-min** | **105.00 core-min** (3× POINT; `--timeout 3150` s at 2 ranks) |
| `FP_T00` | **35.00 core-min** | **105.00 core-min** (`--timeout 3150` s at 2 ranks) |
| grader, one invocation | **0.10 core-min** (6.0 wall s × 1 rank ÷ 60) | **0.30 core-min** |
| **RUNG** | **70.10 core-min** | **CEILING 210.30 core-min** |

**Derived dollars at $0.0513/core-h: POINT `$0.0599`, ceiling `$0.1798`.**
**DERIVED, NOT MEASURED.** `cost_basis`: **reported-by-owner** — this box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**The two columns are different instruments and are not collapsed** (L-463): the
POINT is the prediction rule 12's ratio divides by; the CAP is the guard that
stops a runaway. **An overrun stops the run; it does not get a new budget.**

**The momentum reference solve is NOT re-run.** It exists, it is the M4 datum,
and re-running it would both cost 28.00 core-min for nothing and destroy the
comparison's premise.

**Rule 12's calibration is owed at completion**: actual core-minutes from the
`STATUS.*` files against the 70.10 POINT, the ratio, the attribution, and a row
in `docs/COST_CALIBRATION.md`.

---

## 8. THE CONTROLS, ARMED HERE

### 8.1 Planted-zero control (standing rule 3) — three plants, and P2 is separate on purpose

| plant | what | into | must |
| --- | --- | --- | --- |
| **P1** | `1.234e-03` K | a **copy** of `FP_T10`'s `endTime` `T`, **BY LINE INDEX** | be **SEEN** by the production scalar reader, else REFUSE |
| **P2** | `1.234e-03` m/s into the **X-COMPONENT** | a **copy** of `FP_T10`'s `endTime` `U`, by line index | be **SEEN** by the production **VECTOR** reader, else REFUSE |
| **P3** | exactly `0.0` | a copy of the same `T` | **NOT fire**, else REFUSE |

**P2 is registered separately because a scalar plant does not exercise a vector
reader**, and **M4 — the only gated row — reads vectors**. Each plant goes into
the **field file the graded path reads**, never into a dict, a spec or a
constants table, and each is read back through the **same function the graded
path calls**. All three are matched at **0 ULP**, not at a tolerance.

### 8.2 Strict completion rule (standing rule 4) — all-or-nothing, and the age-guard datum is verified rather than assumed

Both arms must satisfy **every** clause: `rc = 0` from `STATUS.<arm>`; an `End`
line; **last time == `endTime` 9000**; the fields `T U p_rgh alphat nut k omega`
present at `endTime`; `ExecutionTime` count == 9000; and **every field at
`endTime` NEWER than the case's own `0/T`**.

**The age-guard datum is `<case>/0/T`, and this was verified for K0e's own case
rather than assumed.** K0e is **single-region** — one mesh, one case, no regions
— so `0/T` is the correct dating file. It is a *valid* datum only because
`scripts/launch_k0e.sh` **touches `0/T` last, immediately after the build and
immediately before the solver starts**, and nothing writes it afterwards. That
ordering is the guard's whole content and is registered here as part of the
launcher's frozen behaviour.

**`build_k0e.py` REFUSES (exit 2) a case that already holds `0/` or any numeric
time directory**, on the reconstructed side and on the decomposed side.

**K0d is the reason both of these are spelled out.** K0d had **no launcher at
all**, so no `STATUS` file was ever written, so **clause 1 was unverifiable for
both of its arms** and both are `NOT DONE` with every other clause passing
(`K0d_FORENSICS_2026-08-25.md` ADDENDUM 4 §D2, lines 952-991).

### 8.3 Roache triple gating (standing rule 5) — NO TRIPLE IS FORMED

**K0e runs two arms on ONE mesh (52 224 cells). No grid triple exists, standing
rule 5 does not engage, no GCI is computed and none is printed.** Quoting a GCI
where no triple exists would be inventing a convergence claim, and the comparator
is written so that it cannot.

**This is a registered limitation, not an omission:** every K0e number carries
**no discretisation bound at all**. A single-mesh result is a measurement on that
mesh.

---

## 9. THE FROZEN GRADING PATH — pinned by blob sha, with the hash function named

**The grading path is fixed at this commit** (standing rule 2). These three files
are committed **in the same commit as this document**.

| file | **GIT BLOB SHA-1** |
| --- | --- |
| **`scripts/analyse_k0e.py`** — the grader | **`695becd6f8bae04dcf0f7154ea13d57e371c0584`** |
| `scripts/build_k0e.py` — the case builder | `4a6b1fc0f8469e66f2716431a26bede20eaea730` |
| `scripts/launch_k0e.sh` — the launcher | `6479fe4e67a15fd186b7c5afc26f57ae874b4bcc` |

**THE HASH FUNCTION IS NAMED SO THE PIN CANNOT BE COMPARED AGAINST THE WRONG
DIGEST.** These are **git blob SHA-1** values:

    sha1( b"blob " + str(len(content)).encode() + b"\0" + content )

**They are NOT sha256, and they are NOT a plain sha1 of the file's bytes.**
`git hash-object <path>` reproduces them; `sha1sum` and `sha256sum` do not.
`analyse_k0e.py` computes its own by the same definition and **REFUSES (exit 2)**
when invoked as

    python3 scripts/analyse_k0e.py --root <K0e_runs> --scratch <dir> \
        --expect-sha 695becd6f8bae04dcf0f7154ea13d57e371c0584

and the file it is running from is not that blob. **The grade is only valid when
run with `--expect-sha` armed.**

---

## 10. WHAT THIS RUNG CANNOT DO

- **It cannot validate a thermal closure**, for the circularity reason in §2.1.3.
- **It cannot fail a model**, because no band is armed (§3).
- **It cannot bound its own discretisation error**, because no triple is formed
  (§8.3).
- **It is not the mixed-convection rung.** K0d is `BLOCKED`; K0f supersedes it.
- **It says nothing about buoyant flows.** A plate with `beta = 0` has no
  buoyancy production of anything.
- **Nothing here is sent, filed, uploaded, registered or posted. Submissions are
  PARKED.**

---

## 11. RELATION TO THE 2026-08-19 SPECIFICATION, AND THE FOUR DEPARTURES

`K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` is **not edited** and stays on disk
byte-unchanged (standing rule 6). It was written **zero-compute, specification
only**, and this document is the registration that authorises the run. Four
departures, each named with its reason:

1. **§3 of the specification says the rung's *"verdict vocabulary is limited to
   NOT A RESULT, BLOCKED and PENDING"* and that *"it cannot PASS."*** That was
   written before M4 was separated out as a gated row with a real threshold. **It
   can PASS on M4**, and §0 above states the reachable set. **The correlation
   still cannot PASS, which is what that sentence was protecting**, and §3 above
   keeps it protected.
2. **§4.2 control 1 asserts the momentum field *"must reproduce the recorded
   `simpleFoam` solution to machine zero."*** The threshold is unchanged at zero.
   **What is added is §6.1: the two solvers do not share a discrete
   pressure-gradient operator, read from the source**, so the assertion is
   recorded as a prediction that may well fail.
3. **§7's cost is a RANGE.** Converted to a POINT with a separate cap (§7),
   because a range makes its own calibration row meaningless (L-463).
4. **M4b is added** as a REPORTED row (§5.1). It adds no gate. It costs nothing —
   the zero-`dT` control the specification already registers is its second arm.

---

## 12. QUEUE AND LAUNCH

Launches are **daemon-only**. The entries are dropped in
`verification/queue/heat-transfer/` and are picked up by `scripts/queue_runner.py`
on its one-minute tick.

**The box is oversubscribed at this write — load average 39.06 on 16 cores.**
Under Sanaa's 21:00Z ruling that is a **resource gate**, and a resource gate
**QUEUES**: the runner's busy ceiling holds the entry until the box is under it,
and the entry stays scheduled. **That is not a block, not a refusal and not a
`BLOCKED` verdict.** The rung's state until the daemon takes it is **`PENDING`**.

---

*Registered by a heat-transfer lane on the supervisor's decision, 2026-09-03.
This lane assigns the rung no verdict. Nothing was sent, filed, uploaded,
registered or posted — submissions are PARKED.*
