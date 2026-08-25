# VMFL003 — Pressure Drop in Turbulent Flow Through a Pipe: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NOT YET RUN. ZERO SOLVER EXECUTION OF ANY KIND.** This file is frozen **before any
solver starts** (CLAUDE.md rule 2; `SUPERVISION_CHARTER.md` §3 check 4).

**The condition, CHECKED and not asserted** (`VERIFICATION_CHARTER.md` §2b.1): at
**2026-08-25T01:59:15Z**, read with `date -u` in the same invocation,
**`verification/runs/ansys_verification/VMFL003/` does not exist** — `ls -d` returned
*No such file or directory*, and its parent `verification/runs/ansys_verification/`
holds exactly `VMFL001`, `VMFL005`, `VMFL045` and `VMFL051` and nothing beginning
`VMFL003`. **No `blockMesh`, no `checkMesh`, no `topoSet` and no `simpleFoam` has been
run for this case** — no mesh exists, so there is no `checkMesh` summary to declare.
The only thing that has executed is the comparator's own `--selftest` (**60 checks, 0
failures**, no run tree touched, §11). The fleet is invisible to `pgrep` (L-41); the
run tree's absence is the load-bearing check.

**Launch authorisation comes from the `ansys-verification-supervisor`** after its own
personal freeze verification and its own read of the comparator as a diff, **and no
agent message is Sanaa's consent** (CLAUDE.md rule 9).

**Drafted 2026-08-25 by `ansys-lane-opus` (Opus 5) for the `ansys-verification`
team**, under `ANSYS_VERIFICATION_CHARTER.md` §5 and `VERIFICATION_CHARTER.md` §6.
This is **run 1 of VMFL003** — a fresh case, never run in this lab before.
`RESULTS.md` is written afterwards in this directory and **does not revise this
file**; departures land as dated addenda at the foot, never by editing above.

**Precedent.** The structure (§7's named hazards, §8's declared rule-4 departures,
§9's costing), the comparator idiom (a `refuse()` that exits 2, planted-zero controls
against the real artifacts, a `roache()` that returns a STATE, a `grade()`
implementing rule 5 in order, a `--selftest` with negative controls that prove the
gate can fail) and the axisymmetric-wedge pipeline are taken from **VMFL045** and
**VMFL005**, both of which the supervisor personally audited and accepted. **No
VMFL005 or VMFL045 gate, band, reference value or cost figure is reused, and no file
of either case is touched.**

---

## 0. What this case is, and why it is worth running

**VMFL003: Pressure Drop in Turbulent Flow Through a Pipe** — Ansys Fluid Dynamics
Verification Manual, Release 2026 R1, **pp. 19–20**. Air at Re = 1.37 × 10⁴ through a
2 m smooth pipe of radius 2 mm; the manual's target is the **pressure drop, 21744 Pa**.

**Title-page verification, CLAUDE.md rule 15, done and not assumed.** The `.txt`
sidecar was verified against the PDF beside it — **not** by filename, file type or
hash. PDF page 1 reads *"Ansys Fluid Dynamics Verification Manual / Release 2026 R1 /
ANSYS, Inc. / March 2026 / Southpointe, 2600 Ansys Drive, Canonsburg, PA 15317"*, and
the VMFL003 section itself was re-extracted **from the PDF** (pages 33 and 34 of 290,
carrying the printed page numbers 19 and 20) and compared with sidecar lines
1039–1112. Every number quoted in §1 below was read from **both**.

**This is the campaign's FIRST TURBULENT CASE.** Of Sanaa's 73 in-scope cases, 3 are
run and 70 are not; **30 of the 70 are turbulent**. Everything §4 and §7a establish —
the wall-treatment choice, the y+ validity band, the R⁺ constraint on grid
refinement, the code-to-code spread of "standard k-ε" — is machinery the other 29
inherit. **Getting the turbulent toolchain pre-registered properly here is the point
of choosing this case, more than the credential itself.**

**Toolchain reuse.** The axisymmetric wedge, the `surfaceFieldValue` patch-average
instrument, the age-guard idiom and the fixed-iteration-count `simpleFoam` posture
come from **VMFL005** (the team's other axisymmetric pipe), read for setup knowledge
only. The `topoSet`-cellZone sampling idiom and the `# Cells` refusal control come
from **VMFL045**.

**This is a statement about this lab's OpenFOAM v2606 against the manual's reference
result. It is NOT a statement about Ansys** (`ANSYS_VERIFICATION_CHARTER.md` §2).
This box has no Fluent and no CFX; `turb_pipe_flow.cas` and `VMFL003B_VV003CFX.def`
were not run, and **no VM2026R1 archive was opened to write this file** — every
number below comes from the manual's own text or from arithmetic shown here.

## 1. The manual, quoted verbatim (pp. 19–20)

**Reference** (p. 19): *"F.M. White. Fluid Mechanics. 3rd Edition. McGraw-Hill Co.,
New York, NY. 1994."*
**Solver** (p. 19): *"Ansys Fluent, Ansys CFX"*.
**Physics/Models** (p. 19): *"Turbulent flow, standard k-ε Model"*.
**Input File** (p. 19): *"turb_pipe_flow.cas for Ansys Fluent"*,
*"VMFL003B_VV003CFX.def for Ansys CFX"*. **Neither was opened.**

**Test Case** (p. 19), verbatim: *"Air flows through a horizontal pipe with smooth
walls. The flow Reynolds number is 1.37 X 10⁴. Only half of the axisymmetrical domain
is modeled."*

**Material Properties** (p. 19): *Density = 1.225 kg/m³*; *Viscosity = 1.7894 × 10⁻⁵
kg/m-s*.
**Geometry** (p. 19): *Length of the pipe = 2 m*; *Radius of the pipe = 0.002 m*.
**Boundary Conditions** (p. 19): *Inlet velocity = 50 m/s*; *Outlet pressure = 0 Pa*.

**Analysis Assumptions and Modeling Notes** (p. 19), verbatim: *"The flow is steady.
Pressure drop can be calculated from analytical formula using friction factor f which
can be determined for the given Reynolds number from Moody chart. The calculated
pressure drop is compared with the simulation results (pressure difference between
inlet and outlet)."*

**Results Comparison, Table .03.1 (Ansys Fluent) and Table .03.2 (Ansys CFX)**, both
titled *"Comparison of Pressure Drop in the Pipe"* (p. 20):

| quantity | **Target** | Ansys Fluent | Fluent ratio | Ansys CFX | CFX ratio |
|---|---|---|---|---|---|
| **Pressure Drop, Pa** | **21744** | 21480 | 0.988 | 21740 | 1.000 |

**Dimensionality** (manual §1.8 index, p. 7): VMFL003 is **`A` — 2D axisymmetric**,
and it is in the CFX-supported subset (§1.7, p. 6).

The manual's stated accuracy goal (**§1.3, p. 5**): *"The goal for the test cases
contained in this manual was to have results accuracy within 3% of the target
solution."*

### 1a. FINDINGS IN THE MANUAL — recorded here, BEFORE any compute

Recorded now so they cannot be presented later as discoveries that followed a number.
None changes the physics modelled below. All are drafted for `docs/LESSONS.md` /
`docs/NUMERICS_KNOWLEDGE.md` (family `N-AV`) for the supervisor's read, and are **`NOT
FILED`** — contacting Ansys is Sanaa's alone (`ANSYS_VERIFICATION_CHARTER.md` §8).

**Finding 1 — CONSISTENT, and stated so the consistency is on record.** The Material
Properties, Geometry and Boundary Conditions blocks over-determine the Reynolds
number: Re = ρUD/μ = 1.225·50·0.004/1.7894e−5 = **13691.740248127866**, which the
manual states as *"1.37 X 10⁴"* — agreement to **0.06 %**. Every derived quantity in
§2 rests on this and on nothing assumed.

**Finding 2 — UNDER-SPECIFICATION, and the largest single uncertainty in the target:
the friction factor is never printed, and the target is a THREE-SIGNIFICANT-FIGURE
MOODY-CHART READ.** The Analysis Notes say f *"can be determined … from Moody chart"*
but the manual prints no f. It is nevertheless recoverable exactly: the target
implies f = 21744/(500·1531.25) = **0.02840032653061224**, and

> **0.0284 × 500 × 1531.25 = 21743.750000000004 → 21744**

reproduces the printed target to **six significant figures**. So the manual read
**f = 0.0284** off the chart, to 3 s.f. **The consequences are quantified and they
matter:**

- A chart read to 3 s.f. carries a half-width of ±0.00005 in f, i.e. **±0.176 % in the
  target**. The target's own uncertainty is therefore ~±0.18 %, and the manual does
  not say so.
- The **exact** smooth-pipe correlation (Colebrook / Prandtl–von Kármán, ε/D → 0) at
  the stated Re gives **f = 0.028464169573919965**, hence **Δp = 21792.879830032474 Pa
  — 0.224797 % above the printed target.** The manual's "Target" is *not* the exact
  analytic answer; it is 0.22 % away from it.
- Therefore **CFX's printed ratio of 1.000 (deviation −0.018396 %) is a coincidence at
  a precision the target does not support.** A reader would take "1.000" as evidence
  of agreement to 0.1 %; the target is not known to 0.1 %.
- **Blasius is NOT the correlation used.** f_Blasius = 0.316·Re^(−1/4) =
  0.029212748500739585 gives 22366.01057087875 Pa, **+2.860608 %** from the target —
  far outside any reading of a chart at this Re. The manual's own word ("Moody") is
  confirmed arithmetically, not merely taken. The comparator's `--selftest` asserts
  both facts.

**Finding 3 — INTERNAL INCONSISTENCY: the analytical target and the compared quantity
are not the same quantity.** The Analysis Notes derive the target from the
**fully-developed** formula Δp = f (L/D) ρU²/2 and then compare it against *"the
simulation results (pressure difference between inlet and outlet)"* — with a
**uniform** 50 m/s inlet (the only inlet condition the manual gives). A uniform inlet
has a developing region of length ≈ 4.4·Re^(1/6)·D = **0.08608400083579049 m = 21.52 D
= 4.304 % of the pipe**, over which the wall shear exceeds its developed value and the
momentum flux rises from β = 1 toward β ≈ 1.02. That adds an excess of K·ρU²/2 with
K ≈ 0.04–0.10, i.e. **+0.28 % to +0.70 % of the target** (the β = 1.02 momentum-flux
term alone is 61.25 Pa = **+0.2817 %**). The manual states no inlet profile, does not
mention the entrance, and does not budget it. **The mismatch is larger than the CFX
ratio's implied precision** and is carried explicitly in this lab's error budget
(§3.4). It is also the reason §3.3 registers a separate developed-region diagnostic
that removes it.

**Finding 4 — UNDER-SPECIFICATION: no inlet turbulence boundary condition is given at
all.** VMFL003's Overview, Test Case, Material Properties and Boundary Conditions
blocks give density, viscosity, geometry, inlet velocity and outlet pressure — and
**nothing about turbulence intensity, length scale, k or ε**. A standard k-ε run
cannot start without them. **How it is resolved (§2.3):** I = 5 %, l = 0.07 D — the
fully-developed-pipe defaults of *both* Fluent and CFX, hence the most likely reading
of what the manual's own runs used. The choice is declared on the face; **a `PASS` is
not evidence that the manual intended these values.**

**Finding 5 — a 1.21 % SPREAD BETWEEN THE MANUAL'S OWN TWO IMPLEMENTATIONS OF THE SAME
MODEL, printed and never remarked on.** Tables .03.1 and .03.2 give Fluent 21480 Pa
(**−1.214128 %**) and CFX 21740 Pa (**−0.018396 %**) for the identical case with the
identical stated model. **21740/21480 = 1.012104 — a 1.210428 % code-to-code spread in
"standard k-ε".** That is not a discretisation error and does not shrink with grid
refinement; it is the wall treatment and the near-wall implementation. **It is the
single most important number in this file for §3.4 and §7a**, because it is the
manual's own measurement of the quantity this lab is about to add a third sample to.

**Finding 6 — GEOMETRY UNDER-SPECIFIED IN ONE RESPECT.** *"Only half of the
axisymmetrical domain is modeled"* (p. 19) describes a 2-D axisymmetric half-plane,
and *"Figure .03.1: Flow Domain"* is a figure, absent from the text sidecar. The
manual gives no wedge angle, no mesh and no inlet-plane treatment. §4 fixes all three
and says so, so a `PASS` cannot later be read as confirming a discretisation the
manual never specified.

## 2. THE FLUID, THE REFERENCE, AND WHICH ONE THE GATE IS AGAINST

### 2.1 Everything derived from the manual's own Material Properties block

Nothing is assumed. From ρ = 1.225 kg/m³ and μ = 1.7894 × 10⁻⁵ kg/m-s:

| symbol | value | how |
|---|---|---|
| **ν = μ/ρ** | **1.4607346938775508e-05 m²/s** | the kinematic viscosity `simpleFoam` reads (`constant/transportProperties`) |
| D = 2R | 0.004 m | manual: radius 0.002 m |
| L/D | 500.0 | manual: length 2 m |
| **Re = ρUD/μ** | **13691.740248127866** | manual states 1.37 × 10⁴ (Finding 1) |
| **q = ½ρU²** | **1531.2500000000002 Pa** | |
| (L/D)·q | 765625.0000000001 Pa | Δp = f × this |

**Incompressibility is a declared modelling choice.** U = 50 m/s in air is Ma ≈ 0.147,
and Δp ≈ 21.7 kPa is ~21 % of an atmosphere, so an ideal-gas treatment would show a
few per cent density variation along the pipe. The manual gives a **constant** density
in its own Material Properties block and its own target formula Δp = f(L/D)ρU²/2 is a
constant-density formula, so a constant-density solver is the **faithful** reading of
the case as specified.

### 2.2 The reference correlation, to full double precision — a DIAGNOSTIC, never the gate

The manual names the **Moody chart**, i.e. the smooth-pipe branch, so the exact
reference is the implicit **Colebrook / Prandtl–von Kármán** relation
1/√f = 2 log₁₀(Re √f) − 0.8, solved to convergence at the Re above:

| symbol | value | what it is |
|---|---|---|
| **R_MANUAL_DP** | **21744 Pa** | **the manual's printed target, Tables .03.1/.03.2. THE GATE IS AGAINST THIS.** |
| **F_COLEBROOK** | **0.028464169573919965** | exact smooth-pipe friction factor at Re = 13691.740248127866 |
| **DP_COLEBROOK** | **21792.879830032474 Pa** | the exact correlation's Δp. **+0.224797 %** vs the printed target. The exact-value diagnostic (§3.2) is against this. |
| F_CHART | 0.0284 | the 3-s.f. chart read the target implies (Finding 2) |
| Δp at F_CHART | 21743.750000000004 Pa | reproduces the printed 21744 to 6 s.f. |
| F_IMPLIED | 0.02840032653061224 | = 21744/(500·1531.25) |
| **DP_BLASIUS** | **22366.01057087875 Pa** | **NEGATIVE CONTROL. +2.860608 %; the comparator asserts it GATE FAILs.** |
| **DP_LAMINAR** | **3578.7999999999997 Pa** | 32μLU/D². **NEGATIVE CONTROL. −83.5412 %; asserted to GATE FAIL.** |
| **u_τ = U√(f/8)** | **2.9824575423381954 m/s** | at F_COLEBROOK |
| ν/u_τ | 4.897755200673737e-06 m | one wall unit |
| **R⁺ = R u_τ/ν** | **408.3503397076439** | **the whole pipe radius is 408 wall units. §4.2 turns on this.** |

All of these are module-level constants in `grade_vmfl003.py` and every one is
re-derived and asserted by its `--selftest`, with zero compute.

### 2.3 The inlet turbulence state, chosen because the manual gives none (Finding 4)

**I = 5 %, l = 0.07 D** — the Fluent and CFX fully-developed-pipe defaults:

- **k_in = 1.5 (U·I)² = 1.5 × (50 × 0.05)² = 9.375 m²/s²**
- l = 0.07 × 0.004 = **0.00028 m**
- **ε_in = C_μ^0.75 k^1.5 / l = 0.16431676725154984 × 28.704959… / 0.00028 =
  16845.37817870935 m²/s³**
- ⇒ ν_t,in = C_μ k²/ε = 4.6957427527495593e-04 m²/s, i.e. ν_t/ν = 32.15

The pipe is 500 D long and its entrance region is 21.5 D, so **95.7 %** of the gate
quantity accumulates in flow that has forgotten the inlet turbulence state. The
sensitivity is expected to be small — **but it is not zero and it is not the manual's
number.**

### 2.4 Which reference the gate is against, and why

**THE GATE IS AGAINST THE MANUAL'S PRINTED TARGET, 21744 Pa.**
`ANSYS_VERIFICATION_CHARTER.md` §5.1 requires the gate to be *"the reference result as
the manual states it"*. Gating against the lab's own recomputed Colebrook value would
let the lab choose its own reference — and, per Finding 2, would also be gating
against a number **0.22 % away from what the manual actually printed**.

**DP_COLEBROOK = 21792.879830032474 Pa is registered as a tighter DIAGNOSTIC (§3.2),
printed beside the gate and never able to overturn it.**

**Ansys's own numbers (Fluent 21480, CFX 21740) are CONTEXT ONLY** — held in the
comparator as `ANSYS_CONTEXT`, printed in the report, never a gate, never a band,
never a reference.

## 3. THE GATE, ITS TOLERANCE, AND THE DERIVATION OF BOTH

### 3.1 The gate

> **G-VMFL003:** at the finest level **`L3_1000x5`**,
> **|Δp_lab − 21744| / 21744 ≤ 0.025 (2.5 %)**.
> Inside ⇒ gate met; outside ⇒ **`GATE FAIL`**.

**Δp_lab is the pressure difference between the INLET and the OUTLET** — the manual's
own definition of the compared quantity (p. 19) — measured at `endTime` as

> **Δp_lab [Pa] = ρ · ( areaAverage(p)_inlet − areaAverage(p)_outlet ),  ρ = 1.225**

from the `pInletMonitor` and `pOutletMonitor` `surfaceFieldValue` function objects
(§5). **The ρ factor is a real trap here and was not one on VMFL005**, whose ρ = 1
made kinematic pressure numerically equal to Pa. Planted-zero control 1 (§5a) is
constructed so that a reader which forgot ρ is **refused**, not merely wrong.

### 3.2 The exact-correlation diagnostic — NOT the gate

|Δp_lab − 21792.879830032474| / 21792.879830032474 ≤ **2.0 %**, printed beside the
gate. A row that meets the 2.5 % gate but misses this 2 % diagnostic is a **`PASS`**
with the diagnostic printed beside it (the VMFL005/VMFL045 posture). It can never turn
a PASS into a FAIL or the reverse.

### 3.3 The DEVELOPED-REGION FRICTION FACTOR — the diagnostic that isolates the model

The gate quantity contains three things mixed together: the turbulence model's wall
friction, the entrance excess of Finding 3, and the wedge bias of §7b. **This
diagnostic removes the last two.** From the two frozen slabs (§5),

> **f_dev = (dp/dx)|_developed · D / (½ρU²)**, with dp/dx = ρ(p_A − p_B)/0.80 m,
> p_A at x = 1.00 m and p_B at x = 1.80 m, both far downstream of the 0.086 m
> entrance and 50 D upstream of the outlet BC.

Reported against **F_COLEBROOK = 0.028464169573919965** and against the chart read
0.0284, with a **2.0 %** declared band. **This is the number that says what this
lab's `kEpsilon` + `nutkWallFunction` actually does to wall friction**, free of the
BC-faithfulness term. It is **printed, never gated**: it cannot change the verdict.

### 3.4 WHERE 2.5 % COMES FROM — the error budget, computed before any solver runs

**(i) The band must CONTAIN the declared systematics, or the gate is unfair.** Each
term below is one this lab knowingly carries by modelling the case as the manual
specifies it:

| term | size | sign | why the lab carries it |
|---|---|---|---|
| **target chart-read (Finding 2)** | **±0.176 %** | ± | the target is f = 0.0284 to 3 s.f.; ±0.00005 in f |
| **target print rounding** | ±0.0023 % | ± | 21744 printed as an integer, ±0.5 Pa |
| **entrance excess (Finding 3)** | **+0.28 % … +0.70 %** | **+** | uniform inlet BC vs a fully-developed target formula |
| **wedge azimuthal bias (`N-AV9`, §7b)** | **+0.0952685 %** | **+** | sec(2.5°) − 1; **does not refine away** |
| **linear worst case** | **≈ 0.98 %** | | |

**A band below ~1 % would be gating the manual's chart read and this case's own
boundary-condition faithfulness rather than the lab's solver.**

**(ii) The band cannot be tighter than the spread the manual itself displays.**
Finding 5: the manual's own two implementations of "standard k-ε" differ by
**1.210428 %** on this exact case. **A band tighter than 1.21 % would fail Ansys's own
Fluent result** while passing its own CFX result — i.e. it would be a statement about
which commercial code the lab happened to resemble, not about the lab. Adding (i) and
(ii) linearly gives **≈ 2.2 %**.

**(iii) The band must still be TIGHTER than the manual's own goal.** The manual claims
3 % (§1.3, p. 5). The lab holds itself to **2.5 %** — inside the manual's own goal,
above the 2.2 % floor of (i)+(ii), with a small margin and no more.

**(iv) It must be a BAR — capable of failing a plausible-but-wrong treatment.** Every
row is asserted in `--selftest`, with zero compute:

| treatment | Δp | deviation | at 2.5 % |
|---|---|---|---|
| **LAMINAR / turbulence off** (32μLU/D²) | 3578.80 Pa | **−83.54 %** | **FAILS by 33×** |
| **inviscid / zero wall shear** | 0 Pa | −100 % | **FAILS** |
| **Blasius instead of Moody** | 22366.01 Pa | **+2.8606 %** | **FAILS** |
| a +2.6 % answer | 22309.3 Pa | +2.6 % | **FAILS** |
| a −2.6 % answer | 21178.7 Pa | −2.6 % | **FAILS** |
| exact Colebrook | 21792.88 Pa | +0.2248 % | PASSES |
| **Ansys Fluent's own value** | 21480 Pa | −1.2141 % | **PASSES** |
| **Ansys CFX's own value** | 21740 Pa | −0.0184 % | **PASSES** |

**Declared before compute: this band passes BOTH Ansys solvers.** That is deliberate
and is the opposite of VMFL045's posture — and the reason is Finding 5. On VMFL045 the
target was a closed-form shock solution carrying no uncertainty of its own, so failing
a point-sampled Fluent value was defensible. Here the target is a chart read, the two
Ansys codes disagree with each other by 1.21 %, and **a band that failed one of them
would be asserting a resolution the reference does not have.** The bar this gate
enforces is against *wrong physics* — laminar, inviscid, the wrong correlation — not
against the residual spread of correctly-implemented k-ε variants. §3.3's f_dev
diagnostic is what carries the finer statement.

**If the supervisor judges 2.5 % too loose for a first turbulent case, the band may be
tightened to 2.0 % at the freeze — that is a supervisor call, made before commit, and
it still contains (i)+(ii) at 2.2 %… marginally. This lane's justified recommendation
is 2.5 %.**

## 4. Geometry, the mesh family, and THE y+ CONSTRAINT THAT SHAPES THIS WHOLE CASE

### 4.1 Geometry (frozen, `case/system/blockMeshDict.template`)

Axisymmetric **wedge**, one cell thick, `wedge` front/back patches. Axis is +x,
0 ≤ x ≤ L = 2 m; radial 0 ≤ r ≤ R = 0.002 m. **Wedge half-angle 2.5° (5° total)** —
the standard OpenFOAM idiom and the same angle VMFL005 used, chosen deliberately so
the two axisymmetric cases are directly comparable on `N-AV9` (§7b).

Wall vertices sit at **exact radius R**: y_w = R cos 2.5° = **0.0019980964431637158**,
z_w = ± R sin 2.5° = **± 8.7238774730672e-05**, so |(y_w, z_w)| = 0.002 m to machine
precision — **not** y = R, z = R tan α, which would place the wall at R/cos α.

### 4.2 THE CONSTRAINT: R⁺ = 408, AND WHY A RATIO-2 *RADIAL* TRIPLE IS IMPOSSIBLE HERE

This is the finding that shapes the mesh family, and it is derived **before** any run.

`nutkWallFunction` — the OpenFOAM analogue of Fluent's and CFX's **standard** wall
function, and therefore the faithful reading of the manual's "standard k-ε" — is valid
only where the **first cell centre lies in the log layer**: y⁺ ≳ 30 at the bottom, and
y/R ≲ 0.2 at the top. For this case:

- **R⁺ = R u_τ/ν = 408.3503397076439.** The entire pipe radius is 408 wall units.
- The log-layer top is therefore y⁺ ≈ 0.2 × 408.35 = **81.67**.
- **The admissible first-cell window is y⁺ ∈ [30, 81.67] — a factor of 2.72.**
- With a uniform radial mesh of N_r cells the first cell centre is at r = R/(2N_r), so
  y⁺ = R⁺/(2N_r) and the window maps to **N_r ∈ [2.50, 6.81]**.

**A three-level family refined by 2 spans a factor of 4 in y⁺. 4 > 2.72. It does not
fit.** No grading rescues it: adding radial cells can only make the wall cell
*smaller* (δ₁ < R/N_r always), so more radial resolution always means lower y⁺.

**The general form of the constraint, for the other 29 turbulent cases.** A three-level
ratio-2 family fits inside [30, 0.2 R⁺] only if 0.2R⁺/30 ≥ 4, i.e. **R⁺ ≥ 600**. For a
pipe R⁺ = (Re/2)√(f/8), so the threshold is **Re ≈ 21252** (f = 0.02551 there).
**VMFL003 at Re = 13692 is below it.** This is registered now, before any result, and
is drafted for `docs/NUMERICS_KNOWLEDGE.md`.

**THE CONSEQUENCE, AND IT IS THE DESIGN DECISION OF THIS CASE:** the radial mesh is
**HELD FIXED at N_r = 5 across the entire Roache triple**, at a predicted first-cell
**y⁺ = 40.835033970764385** — mid-window, the wall-function optimum — and the triple
refines **axially** by 2. The wall treatment is then **identical at every level**, so
the triple measures discretisation error and **not** a wall-function regime change.

**A continuous all-y⁺ wall function (`nutUSpaldingWallFunction`) was considered and
DECLINED.** It would permit a 2-D ratio-2 family, but it is **a different wall
treatment from the one the manual ran**, and this case exists to measure the lab's
reproduction of the manual's stated model. The choice is declared, not defaulted, and
is written into `case/0/nut`.

**THE HONEST COST OF THAT DECISION, STATED HERE AND NOT LATER:** the GCI this family
produces bounds the **AXIAL** discretisation uncertainty **only**. It says nothing
about the radial/wall-treatment channel. **A small GCI will therefore NOT license
calling the remaining deviation numerical** — that is `N-AV7` (VMFL005: a genuinely
`CONVERGING` triple, p = 1.93, GCI_fine 0.0502 %, and a deviation from the exact
reference 9.92× the GCI, with Richardson extrapolation moving *away* from exact). §4.4
exists so that the channel the GCI cannot see is **measured**, in advance of the
claim, rather than speculated about afterwards.

### 4.3 The Roache triple — ratio 2 BY CONSTRUCTION, axial

| level | N_x × N_r | cells | h = Δx (m) | endTime (SIMPLE iters) | predicted first-cell y⁺ |
|---|---|---|---|---|---|
| `L1_250x5` | 250 × 5 | **1250** | 0.008 | 6000 | **40.835033970764385** |
| `L2_500x5` | 500 × 5 | **2500** | 0.004 | 8000 | **40.835033970764385** |
| `L3_1000x5` | 1000 × 5 | **5000** | 0.002 | 12000 | **40.835033970764385** |

Each level **doubles N_x**, so **h halves exactly and r = 2 by construction** — never
inferred from a cell count (`VERIFICATION_CHARTER.md` §3.1). N_r is identical at all
three, so the y⁺ prediction is identical at all three.

**The axial triple is not vacuous.** Over ~95.7 % of the pipe the flow is fully
developed and the axial pressure variation is **linear**, hence represented exactly by
any of these meshes; the axial discretisation error of the gate quantity therefore
lives almost entirely in the **entrance region**, 0.086 m = 21.52 D, resolved by
**10.8 / 21.5 / 43.0 cells** at L1/L2/L3. That region carries the +0.28…0.70 %
entrance excess, so a 10–30 % error in it is 0.03–0.2 % of Δp — **6 to 45 Pa of
level-to-level difference**, far above both the plateau tolerance (0.01 Pa) and the
EPS_ABS floor (1e−9 Pa). The triple has real signal.

### 4.4 The WALL-TREATMENT SENSITIVITY LADDER — a DECLARED DIAGNOSTIC, not a Roache triple

Four meshes at fixed N_x = 500 and endTime 8000, spanning the whole admissible y⁺
window of §4.2:

| level | N_x × N_r | cells | predicted first-cell y⁺ | y/R |
|---|---|---|---|---|
| `D_500x3` | 500 × 3 | 1500 | **68.05838995127397** | 0.1667 |
| `D_500x4` | 500 × 4 | 2000 | **51.04379246345549** | 0.1250 |
| `L2_500x5` | 500 × 5 | 2500 | **40.835033970764385** | 0.1000 | *(reused, not re-run)* |
| `D_500x6` | 500 × 6 | 3000 | **34.02919497563698** | 0.0833 |

**This is NOT a Roache triple and is never Richardson-extrapolated** — its levels are
not in ratio 2 and its refinement changes the wall model's operating point on purpose.
It exists to put a **measured number** on the channel a GCI structurally cannot see.
Its output is the **relative spread of Δp across the four**, printed beside the GCI.

**One-way clause, frozen now:** if that spread exceeds **5.0 %** (twice the gate band),
the row is **`NOT A RESULT`** — the answer would then be a property of the wall-cell
placement rather than of the case. This can only turn a `PASS`/`GATE FAIL` **into**
`NOT A RESULT`, never the reverse (CLAUDE.md rule 5).

### 4.5 endTime — a fixed iteration count, and it is an ESTIMATE

There is **no `residualControl`** (`case/system/fvSolution`), so SIMPLE always runs to
`endTime` and rule 4's "last time == endTime" and "ExecutionTime count == endTime"
clauses stay meaningful (the VMFL005 idiom). The counts 6000/8000/12000 are **scaled
from VMFL005's measured convergence behaviour and increased for the two extra
transport equations**; they are **estimates, fixed before any run**, and the §6/§8
convergence clauses are the actual arbiter. Over-budgeting only costs compute; a level
that misses its clause is **`NOT A RESULT`** and re-runs at a longer endTime as a
**NEW RUNG**, never re-graded in place (§7c).

## 5. THE FROZEN SAMPLING RULE — where every number is read, fixed before any exists

**THE GATE** is read from two patch monitors, in absolute terms identical at every
level (`case/system/controlDict.template`):

- `pInletMonitor` — `surfaceFieldValue`, `regionType patch`, `name inlet`,
  `operation areaAverage`, `fields (p)`, **every iteration**.
- `pOutletMonitor` — the same on `outlet`. The outlet is a `fixedValue 0` BC, so this
  leg is **measured, not assumed**, and subtracted.

Writing every iteration means the same series is also the **plateau leg** of §6 step 1.

**THE DEVELOPED-REGION DIAGNOSTIC** is read from two frozen cell zones
(`case/system/topoSetDict`), in **absolute physical coordinates identical at every
level**:

> **`slabA`:** x ∈ [0.98, 1.02] m (centred x = 1.00 m = 250 D), y ∈ [−1, 1], z ∈ [−1, 1]
> **`slabB`:** x ∈ [1.78, 1.82] m (centred x = 1.80 m), same y, z

Each slab is 0.04 m = 10 D long and **symmetric about its station**, so a volume
average of a locally linear p returns the station-centre value to second order.
`slabA` is more than **11 entrance lengths** downstream of the developing region;
`slabB` is **50 D upstream** of the outlet BC so the fixed-pressure plane cannot
contaminate it. At L1 each slab holds 5 × N_r cells; at L3, 20 × N_r. Neither can be
empty — **`run_vmfl003.sh` refuses before the solver starts if `topoSet` leaves either
zone empty, and `grade_vmfl003.py` refuses (exit 2) if the `# Cells` header of either
output is absent or 0.**

**THE WALL-FUNCTION VALIDITY INSTRUMENT** is the v2606 `yPlus` function object on the
`walls` patch, writing `# Time patch min max average` rows. Its **average at endTime**
is compared against the predicted **40.835033970764385**, with the one-way clause of
§6.

**The readers.** Every column is located **by header name, never by position**
(`N-AV4`/`L-286`): `areaAverage(p)`, `volAverage(p)`, `average`. The `# Faces` and
`# Cells` header values are **controls**, not decoration — a zero or missing count is a
**refusal (exit 2)**, not a degradation. Both refusal arms are exercised by
`--selftest` on fixtures written in the real v2606 formats.

### 5a. Planted-zero controls (CLAUDE.md rule 3) — three, against the REAL artifacts

Each control copies the real file to a **temp tree** (the run tree is never modified),
adds a known perturbation to the last data row, **reads it back from disk**, and
**refuses (exit 2)** if the reader cannot see it. Each also has a **negative arm**: an
unplanted copy must move the answer by exactly zero.

| # | plant | into | must move | why this plant |
|---|---|---|---|---|
| **1** | **PLANT_DP = 1.234** | `pInletMonitor` `areaAverage(p)` — the **KINEMATIC** column | the graded value by **PLANT × ρ = 1.5116500000000002 Pa** | **this control is simultaneously a live test that the ρ = 1.225 conversion is applied.** A reader that forgot ρ would see 1.234 and is REFUSED. |
| **2** | **PLANT_YPLUS = 7.77** | `yPlus` `average` column | the extracted mean y⁺ by exactly 7.77 | proves the y⁺ clause reads a live number, not a default |
| **3** | **PLANT_SLAB = 2.345** | `pSlabA` `volAverage(p)` | f_dev by **PLANT·ρ·D/(0.80·q)**, in closed form | proves the f_dev diagnostic is wired to disk |

Agreement is demanded to **1e−9** absolute. `--selftest` exercises both arms of all
three on fixtures in the real formats, **and separately asserts that a simulated
ρ-blind reader IS refused by control 1.**

## 6. THE VERDICT ORDER (CLAUDE.md rule 5), in its stated order — with Roache meanings

1. **Any level not iteratively converged, not plateaued, outside the wall-function
   validity band, or failing any completion clause of §8 ⇒ `NOT A RESULT`;** and the
   §4.4 ladder-spread clause ⇒ `NOT A RESULT`. Specifically, **per level and BEFORE
   the triple is formed**:
   - final **initial** residuals of **p, Ux, k, ε** each **< 1.0e−8**
     (Uy, Uz are **printed, not gated**: on a wedge their normalisation is degenerate
     in the developed region, so gating them would be a hair trigger, not a check);
   - **plateau**: peak-to-peak of the Δp series over its **last 20 %** ≤ **1.0e−2 Pa**;
   - **wall-function validity**: mean wall y⁺ at endTime within **[25, 65]**;
   - **ladder spread** ≤ **5.0 %**.
2. **Roache triple** on Δp `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` ⇒
   **`NOT A RESULT`**, with the three values, R, the increments and the observed order
   printed beside it, and **NO GCI QUOTED** (the comparator sets it to `null`; asserted
   by `--selftest` for all four states).
3. **`CONVERGING`** ⇒ **`PASS`** inside the 2.5 % band else **`GATE FAIL`**, with
   **GCI at Fs = 1.25** printed and the Richardson extrapolation beside it. A GCI is
   never quoted when the three values are not monotone (the flag is printed).

Thresholds fixed in the comparator before any run: `EPS_ABS = 1e−9` Pa,
`STAG_TOL = 1e−3`, `RATIO = 2.0`, `FS = 1.25`. **The gate can only turn a `PASS` or
`GATE FAIL` INTO `NOT A RESULT`, never the reverse.**

**WHY THOSE THRESHOLDS ARE THE RIGHT SIZE — the arithmetic, before the run.** §4.3
predicts level-to-level Δp differences of **6–45 Pa**. The plateau tolerance of
**0.01 Pa** is therefore **600× to 4500× below the signal the triple must measure** —
exactly the separation VMFL051's failure showed to be necessary (§7c). `EPS_ABS` at
1e−9 Pa is 4.6e−14 relative, far below any real difference.

**WHAT EACH ROACHE OUTCOME MEANS FOR THIS CASE — registered before the answer exists:**

- **`CONVERGING` with observed p ≈ 1:** the **expected** outcome (see below). The axial
  error is dominated by the limited (`limitedLinear`) turbulence transport in the
  entrance region, where the limiter degrades locally to upwind. The GCI is meaningful
  **for the axial channel only** and the gate applies.
- **`CONVERGING` with p ≈ 2:** possible if the entrance is already well enough resolved
  at L1 that the smooth second-order interior dominates. Reported as measured — **and
  see the warning below.**
- **`OSCILLATORY` (R < 0):** the level-to-level differences change sign. Likeliest
  causes here: a level not plateaued (VMFL051's exact failure mode, §7c), or an
  entrance-region error that is non-monotone in Δx. ⇒ **`NOT A RESULT`**; diagnosed,
  not graded.
- **`DIVERGENT` (R > 1):** differences **grow** with refinement — the meshes are not in
  the asymptotic range. ⇒ **`NOT A RESULT`**.
- **`STAGNANT` (R ≈ 1):** differences do not shrink — no extractable order. Here this
  would most likely mean the axial error has hit a **floor set by the fixed radial
  mesh**, which would itself be an informative measurement of §4.2's cost.
  ⇒ **`NOT A RESULT`**, with that reading stated.
- **`EXACT` (all three differences below 1e−9 Pa):** would mean the gate quantity is
  axially mesh-independent to 14 significant figures. Given §4.3's prediction this is
  not expected; rule 5 still classes it **`NOT A RESULT`** (no order can be formed from
  zero differences), the three equal values are printed, and the case would re-run with
  a wider refinement ratio as a **new rung**.

**EXPECTED OBSERVED ORDER, STATED BEFORE IT IS MEASURED.** **p ≈ 1 is expected**, and
the reason is specific: the gate quantity's axial error is concentrated in the
entrance region, where `bounded Gauss limitedLinear 1` on k and ε has its limiter
active and behaves first-order, while the ~96 % of the pipe that is fully developed
contributes an axial error of essentially zero (linear p is exact on every level). A
formally second-order scheme whose error lives entirely in its limited region does not
deliver p = 2.

**AND THE WARNING, WHICH IS THE POINT OF STATING THIS AT ALL: a suspiciously *good*
order is the failure mode nobody reports.** If this triple returns p in **[1.90,
2.10]** on a quantity whose error budget says the second-order region contributes
almost nothing, that is **not** a confirmation — it is a coincidence to be reported
and interrogated, and `RESULTS.md` must say so in those terms rather than presenting it
as evidence the numerics are healthy. Registered here so it cannot be rationalised
after the fact.

## 7. THE THREE NAMED HAZARDS — all three measured facts from this team's own cases

### 7a. THE TURBULENCE-MODEL DIFFERENCE IS THE REAL RISK, AND IT IS NOT A DISCRETISATION ERROR

The manual ran Fluent/CFX **standard k-ε**; this lab runs OpenFOAM `kEpsilon`. The
**coefficients are identical** — C_μ 0.09, C₁ 1.44, C₂ 1.92, σ_k 1.0, σ_ε 1.3 — and
`case/constant/turbulenceProperties` writes them out explicitly rather than defaulting
them, so "the coefficients match" is an assertion this case makes, not a belief about a
default. **That is exactly why the remaining difference is the WALL TREATMENT**, and
wall functions, near-wall damping and the ε boundary condition differ between codes.

**This is not a worry, it is a measurement — and the manual made it.** Finding 5:
Fluent 21480 Pa and CFX 21740 Pa on the identical case with the identical stated model,
a **1.210428 %** spread. **That difference does not shrink with grid refinement.**
Moreover Fluent's −1.214 % is a *low* answer despite also carrying the +0.28…0.70 %
entrance excess of Finding 3, so its k-ε wall friction is roughly **1.5–1.9 % below**
the Moody value.

**The team has already measured this shape of failure in its own work.** `N-AV7`
(VMFL005): a genuinely `CONVERGING` triple at p = 1.9341 with **GCI_fine = 0.0502 %**,
and a deviation from the exact reference of **0.4979 % — 9.92× the GCI** — with
Richardson extrapolation moving the answer **further from** exact. About 90 % of that
residual was modelling, not discretisation.

**What is fixed before the run, in consequence:**
- **Wall treatment: `nutkWallFunction`** (nut from k via the log law) + `kqRWallFunction`
  + `epsilonWallFunction`. Declared in `case/0/nut`, chosen as the OpenFOAM analogue of
  the *standard* wall function the manual names. `nutUSpaldingWallFunction` was
  considered and declined (§4.2).
- **y⁺ target: 40.835033970764385**, mid-log-layer, **identical at every level of the
  triple**, with a one-way `NOT A RESULT` band of **[25, 65]**.
- **Stated on the face: a small GCI will NOT license calling the remaining deviation
  numerical.** The GCI here bounds the **axial** channel only (§4.2). The
  wall-treatment channel is measured separately by the §4.4 ladder and the §3.3 f_dev
  diagnostic, and `RESULTS.md` must report the ratio deviation/GCI explicitly, as
  VMFL005's §5 did.

### 7b. THE AXISYMMETRIC WEDGE AREA DEFICIT (`N-AV9`) — with this case's own arithmetic

A 5° OpenFOAM wedge is a **flat-sided triangle**, not a circular sector. **Wedge
half-angle here: 2.5° (5° total).** The arithmetic, reproduced independently in
`grade_vmfl003.py --selftest`:

- **cross-sectional area ratio** = sin(2α)/(2α) = **0.9987312439537492** ⇒ deficit
  **0.1268756046250763 %** — which reproduces `N-AV9`'s recorded constant **exactly**,
  an independent confirmation of the team's own number;
- **wetted (wall) area ratio** = sin(α)/α = **0.9996827203920081** ⇒ deficit
  **0.03172796079918827 %**;
- their ratio is **exactly sec α**, since sin(2α)/2 = sin α cos α. Hence, for a fixed
  wall shear stress, the streamwise force balance Δp·A_cross = τ_w·A_wall gives

> **Δp_modelled / Δp_true = 1/cos(2.5°) ⇒ the modelled pressure drop is HIGH by
> sec(2.5°) − 1 = +0.09526851633199218 %.**

**It is AZIMUTHAL: no axial or radial refinement removes it**, and it is carried in
§3.4's budget as a one-sided **+0.0953 %**.

**A CORRECTION TO HOW `N-AV9` TRANSFERS, recorded before the run.** `N-AV9`'s
consequence figure of ≈ **+0.25 %** in Δp was derived for **VMFL005**: laminar flow at
**fixed volumetric Q**, where Hagen–Poiseuille's R⁻⁴ scaling amplifies the area
deficit. **VMFL003 is neither.** Its inlet fixes a **velocity** (50 m/s uniform), not a
flow rate, and its friction is turbulent (τ_w ∝ U^1.75, not R⁻⁴). **The +0.25 % figure
does not transfer, and using it here would over-state the term by 2.6×.** The correct
transfer is the geometric force balance above, **+0.0953 %**. Drafted as an addendum to
`N-AV9` for the supervisor's read.

The angle is kept at 5° deliberately, for direct comparability with VMFL005 on this
term, and because +0.095 % is **26× smaller** than the gate band. The error scales as
α²/2, so a future rung could quarter it by halving the angle; that is noted, not done.

### 7c. THE PLATEAU / ITERATIVE-CONVERGENCE HAZARD

**VMFL051 came back `NOT A RESULT`** because two of its three levels had not plateaued
at endTime and the triple went **`OSCILLATORY` (R = −1.3486)**: the coarse levels'
residual unsteadiness was the **same order** as the level-to-level differences, so the
triple measured noise rather than discretisation error.

VMFL003 uses a **steady** solver, so the analogous clause is **iterative convergence
checked PER LEVEL, BEFORE the triple is formed**, and it is frozen now, in two
independent legs:

1. **Residual leg** — final **initial** residuals of p, Ux, k, ε each **< 1.0e−8**.
2. **Plateau leg** — peak-to-peak of the **gate quantity itself** over the last 20 % of
   its iteration series ≤ **1.0e−2 Pa**. This is the physically decisive test: it asks
   whether the number being graded has stopped moving, not whether a normalised
   residual has.

**Separation, computed in advance:** 0.01 Pa against an expected level-to-level
difference of 6–45 Pa is a **600–4500× margin** — the separation VMFL051 showed to be
necessary. **A level that fails either leg is `NOT A RESULT` and re-runs at a longer
endTime as a NEW RUNG, never re-graded in place** (the VMFL001 R1→R2 protocol). No
gate, threshold, cap or label moves when that happens.

## 8. Strict completion (CLAUDE.md rule 4), with ONE DEPARTURE DECLARED ON THE FACE

The comparator refuses (exit 2) on any failed clause and **never grades a partial run**.

| clause | as checked here |
|---|---|
| **C1** `rc = 0` | `RUN_RC.txt`, written by the launcher, reads `rc=0` — **literal** |
| **C2** an `End` line | `^End$` present in `log.simpleFoam` — **literal** |
| **C3** last time == `endTime` | **literal.** There is no `residualControl`, so SIMPLE always reaches endTime and the equality is exact, not approximate |
| **C4** fields present at `endTime` | **DEPARTURE 1** |
| **C5** `ExecutionTime` count == `endTime` | **literal.** Steady SIMPLE: one iteration = one time unit |
| **C6** age guard | **STRICTER than the rule** |

**DEPARTURE 1 (C4) — the field list.** The rule's literal list `T U p_rgh alphat nut k
omega` is the **thermal family's** list. VMFL003 is isothermal, incompressible and
k-ε: it has no `T`, no `p_rgh`, no `alphat`, and `omega` is not solved by k-ε.
This case's declared list is **`U p k epsilon nut`** — **every field this case
actually solves or forms, with nothing dropped**. It is therefore **tighter or equal,
never looser**: it adds `epsilon` (absent from the rule's list) and drops only fields
that do not exist here. Naming a field the case does not have would make the clause
unfalsifiable, not stricter.

**C6 IS STRICTER THAN THE RULE.** The rule dates the run from the case's own `0/T`;
there is no `T` here, and this clause dates it from the **latest mtime anywhere in the
level's own `0/`**. `run_vmfl003.sh` touches **every file in `0/`** as its last action
before the solver launches. Every field at endTime must be **strictly newer** than that
datum, or the comparator refuses.

**Clauses BEYOND rule 4, all tighter, none looser** (§6 step 1): the residual leg, the
plateau leg, the y⁺ validity band, the ladder-spread clause, the non-empty
patch/cellZone controls, and the three planted-zero controls.

**The launcher enforces the rule's own guards.** `run_vmfl003.sh` refuses to start into
**any** pre-existing level directory; refuses unless **this pre-registration is
committed at HEAD and byte-identical to the committed blob**; refuses unless the
comparator passes `--verify-frozen HEAD`; refuses if `topoSet` left either frozen zone
empty; and enforces the cap with `timeout` against a **running total** (§9).

**`set -e` is deliberately not relied on anywhere in the launcher.** It was measured
**not** to be in force in this lab's agent execution context (`set -e; python3 -c
"raise SystemExit(1)"; echo REACHED` prints REACHED), so every check gates with an
explicit `|| { echo ABORT…; exit 1; }`. **A check that only prints is not a check.**

**And a PRE-FLIGHT SMOKE TEST runs before any level.** One iteration on the coarsest
mesh, in a scratch directory **outside `verification/runs/`**, aborting the whole run
on failure. The reason is measured, not precautionary: **a comparator `--selftest`
proves the GRADER, not the CASE.** VMFL045 passed 45/45 selftest checks and still died
on its first timestep on a missing `fvSolution` entry that no selftest could see.
Accordingly `case/system/fvSolution` here carries an entry for **every** variable
`simpleFoam` + `kEpsilon` actually solves — p, and the regex `"(U|k|epsilon)"` as a
**class** rather than three named instances (the L-221/L-222 posture: fix the class,
not the instance). `nut` is algebraic and correctly has no entry.

## 9. Cost (CLAUDE.md rule 12, and L-291's four numbers)

### 9.1 Executed compute

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × RANKS / 60 |
| **basis** | VMFL005's **measured** aggregate throughput on this box: 240 s for 1.1 × 10⁸ cell-iterations = **2.18e−6 s per cell-iteration** (laminar `simpleFoam`, wedge, including meshing and runtime-compile overhead). Corroborated by VMFL001's measured per-level rates 6.51e−7 / 1.06e−6 / 2.12e−6 s/(cell·iter). **A measurement of this solver on this hardware, borrowed as setup knowledge; no VMFL005/VMFL001 gate, band or reference is borrowed.** |
| k-ε multiplier | **× 1.6** for the two extra transport equations, `nut` and `wallDist`. **This factor is an ESTIMATE, not a measurement** — it is the single largest uncertainty in this budget. ⇒ **3.5e−6 s/(cell·iter)** |
| cell-iterations | L1 7.5e6 + L2 2.0e7 + L3 6.0e7 + D_500x3 1.2e7 + D_500x4 1.6e7 + D_500x6 2.4e7 = **1.395e8** |
| solver estimate | 1.395e8 × 3.5e−6 = **488 s** |
| + `blockMesh`+`checkMesh`+`topoSet` × 6, and the smoke test | ~**40 s** (estimate) |
| + five per-iteration function objects, ~10 % of solver | ~**49 s** (estimate) |
| **POINT ESTIMATE** | **≈ 577 s = 9.6 core-minutes** |
| *(the optimistic end, for honesty)* | using VMFL001's **small-mesh** rate 1.06e−6 × 1.6 instead — closer to these 1250–5000-cell levels — gives **≈ 5.0 core-min**. The point estimate is deliberately taken at the **pessimistic** end because the k-ε multiplier is unmeasured. |
| **CEILING (the enforced cap)** | **24 core-minutes** = 2.5 × the point estimate, enforced by `timeout` inside `run_vmfl003.sh` **against a running total across all six meshes**; **an overrun STOPS the run and it does not get a new budget** |
| authorised for this case | requested **25 core-minutes** from the supervisor; the cap is set **under** it, and the authorisation is a per-item cost, **not a new ceiling** (rule 9) |
| dollars at the point estimate | **$0.008208** (DERIVED) |
| dollars at the ceiling | **$0.020520** (DERIVED) |
| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). The per-cell-iteration rate is a **measurement**; the k-ε multiplier, the iteration counts, the meshing time and the FO margin are **ESTIMATES**. |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; **a blanket is not a per-item read** (rule 9) |

**The cap-as-timeout instrument, in its general form.** A wall-clock `timeout` equals a
core-minute cap **only for a serial run**; for a parallel run it must be
`cap_core_min · 60 / ranks`. `run_vmfl003.sh` computes **`TIMEOUT_S = REMAINING_CORE_MIN
* 60 / RANKS`** and **`CORE_MIN = WALL_S * RANKS / 60`** — the general formulae, with
`RANKS` in them — so a future parallel copy inherits a correct cap instead of a
silently broken one. No single level's estimated wall time (max ~210 s at L3)
approaches the 3600 s stall threshold.

### 9.2 Lane wall, priced separately (L-291)

| component | point estimate | ceiling |
|---|---|---|
| **this drafting lane** (read the manual; title-page verify against the PDF; read the VMFL045/VMFL005 precedents; derive the reference, the R⁺ constraint, the wedge budget and the entrance budget; build the case tree; write and selftest the comparator; write the launcher; two commits) | **60 lane-minutes** | **90 lane-minutes** |
| **the later run-and-grade lane** (launch, monitor, grade, draft `RESULTS.md`, the register row and the calibration row) | **25 lane-minutes** | **45 lane-minutes** |

### 9.3 Calibration at completion (CLAUDE.md rule 12, Sanaa's 2026-08-23 directive)

At completion the team compares **each component against its own pair**: actual
core-minutes from `RUN_RC.txt`/`COST.txt` against the 9.6 point estimate, and actual
lane wall against §9.2; the **ratio actual/predicted**, with the gap attributed
(contention, waste, misprediction — **waste named separately, never absorbed into the
ratio**); dollars derived at $0.0513/core-h and labelled **derived, not measured**; and
**one row appended to `docs/COST_CALIBRATION.md`** under its append rules and the
rule-10 private-index protocol. **A completion report without that row is incomplete.**

**The k-ε multiplier of 1.6 is the specific figure this calibration should test**, and
its measured value is reusable across the other 29 turbulent cases — which is a second
reason this case is worth running first.

## 10. The grading path, frozen (`VERIFICATION_CHARTER.md` §2d)

The comparator, the launcher and the whole case tree were committed **BEFORE this
file**, at commit **`9fea6a65fc294ff8e8f2d83c0db89f7496581932`** ("VMFL003 case inputs,
launcher and comparator — NO COMPUTE HAS RUN, pre-registration NOT YET FROZEN"), which
precedes any solver. At analysis time the grading path is re-hashed against these blob
shas; a freeze that is claimed and not checked is a claim about intent.

| what | path under `cases/ansys_verification/VMFL003/` | committed blob sha |
|---|---|---|
| **comparator (THE GRADING PATH)** | `grade_vmfl003.py` | **`15b14d40f166cc31770ead452c27905332670c97`** |
| launcher | `run_vmfl003.sh` | `5ed5ff81d41322d3b482ac911a6219952c57957a` |
| **the frozen sampling rule** | `case/system/topoSetDict` | **`a8929705e8ede13228c9a114cf029c55ee88347d`** |
| blockMeshDict template (the wedge) | `case/system/blockMeshDict.template` | `4df3d373018be1b6e280a08f25fa770d39ba4214` |
| controlDict template (endTime + the five monitors) | `case/system/controlDict.template` | `e589a0f767b24c7e348c9855ef22b5ff4f081350` |
| fvSchemes | `case/system/fvSchemes` | `8712f15add61a99b9f0c91e9a15f76cc495f8c36` |
| fvSolution | `case/system/fvSolution` | `65d8a0e0c96719ed936c816363764f075be8cb18` |
| `0/U` (the uniform 50 m/s inlet BC) | `case/0/U` | `60cf293a9f5a7407e52e8c50e97a16b7d33fd1f9` |
| `0/p` | `case/0/p` | `13d7c73f4ba6f20db38d7c02151db78a2f171731` |
| `0/k` (the chosen inlet turbulence, Finding 4) | `case/0/k` | `19459c446b1e7ac1433758a46e58839d09dc5e6c` |
| `0/epsilon` | `case/0/epsilon` | `d4b6a4766ba35468b7e77a48d90d4ccae609fa26` |
| **`0/nut` (THE WALL TREATMENT)** | `case/0/nut` | **`f0690c75acb8c21407f34d88431d33b0f1813ae8`** |
| transportProperties (ν derived) | `case/constant/transportProperties` | `0b4aeebac697bebd48f70947cbe415facb4fa3ed` |
| turbulenceProperties (k-ε coefficients explicit) | `case/constant/turbulenceProperties` | `426ef329b3f52bdca1988e28385e72c072773030` |

**Verified at grade time, not merely recorded.** `grade_vmfl003.py --verify-frozen
<commit>` reads its own bytes, recomputes its git blob sha and refuses (exit 2) unless
byte-identical to the committed blob; `run_vmfl003.sh` calls it **before the smoke test
and before any level**. **No threshold, band, reference value or plant constant in the
comparator is settable from the command line** — every one is a module-level constant
fixed by commit `9fea6a65`.

**Run outputs go to `verification/runs/ansys_verification/VMFL003/<level>/`**, never
beside this prose (`FILING_CHARTER.md` R6). **The grading JSON is
`verification/runs/ansys_verification/VMFL003/GRADING_VMFL003.json`.** `scripts/check_filing.py`
was run and reports **zero violations on any VMFL003 path** (the 26 violations it
reports repo-wide are pre-existing and are not this case's).

## 11. What CANNOT be verified before the freeze — stated plainly

**No VMFL003 solver has run, and no mesh exists.** What *has* fired, with **zero solver
compute**: the comparator's `--selftest`, **60 checks, 0 failures** — every derived
constant of §2 re-derived from the manual's raw properties; the Colebrook, chart,
Blasius and laminar references; R⁺ and the y⁺ predictions; the wedge arithmetic
including `N-AV9`'s 0.1268756 % and this case's sec(2.5°) − 1; all six Roache states
with **no GCI produced for any of the five non-CONVERGING ones**; the readers on the
real v2606 formats plus four refusal arms; both arms of all three planted-zero
controls; the ρ-blind-reader refusal; the plateau clause both ways; and every negative
control of §3.4 including laminar, inviscid and Blasius.

**Six things this lab has NOT seen, each needing separate supervisor authorisation —
even `blockMesh` alone is not covered by this freeze:**

1. **That the mesh builds.** No `blockMesh` has run, so no `checkMesh` summary can be
   quoted. The declaration is the strong one: the mesh did not exist when the gate was
   frozen. A 5° wedge 500 D long with aspect ratio Δx/Δr = 20 (L1) to 5 (L3) is
   unremarkable, but that is a judgement, not a measurement.
2. **That `topoSet` puts cells into both frozen zones.** The box coordinates are derived
   arithmetic (§5); if either comes out empty the launcher refuses before the solver.
3. **The live `.dat` files.** The readers are built from the v2606 writer sources
   (`surfaceFieldValue.C:719-745`, `volRegion.C:133-143`, `yPlus.C:50-60`), but no run
   has produced one. The cheap decisive check after the smoke test is
   `grade_vmfl003.py --dryrun-reader <path>`, which prints **structure only and never a
   value** (the L-286 check).
4. **THE PREDICTED y⁺ IS A PREDICTION.** 40.835 rests on u_τ from the *Colebrook*
   friction factor. If this lab's k-ε delivers f 10 % low, y⁺ lands near 39, still well
   inside [25, 65]; but the band is a **clause**, not a forecast, and if it fires the
   row is `NOT A RESULT` and the mesh is redesigned as a new rung.
5. **That every level converges within 6000/8000/12000 iterations** (§4.5 is an
   estimate). If a level misses either convergence leg it is `NOT A RESULT` and re-runs
   at a longer endTime as a **new rung** — no gate, threshold, cap or label moves.
6. **The observed order, the GCI, the ladder spread and f_dev.** §6 states the
   *expectation* (p ≈ 1) and the warning about a suspiciously good order; the measured
   values are findings, whatever they are.

**One thing this lane could not verify at all:** whether the manual's own Fluent and
CFX runs used I = 5 % / l = 0.07 D at the inlet (Finding 4), what wedge or 2-D
axisymmetric discretisation they used (Finding 6), or what their near-wall y⁺ was.
Those archives were not opened and this box cannot run either code. **The 1.21 %
Fluent–CFX spread of Finding 5 is therefore a measurement of *something*, and this lane
cannot say how much of it is wall treatment and how much is mesh.**

## 12. Verdict vocabulary, and what this rung will NOT claim

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (CLAUDE.md rule 1). `PENDING` here means **not yet run** and is never used
to soften a `GATE FAIL`.

- **Nothing about Ansys.** Fluent's 21480 and CFX's 21740 are context (§1), never the
  gate; this box has no Fluent and no CFX and neither archive was opened.
- **Nothing about the manual's correctness beyond §1a.** The six findings are drafted
  for the lessons/numerics files and stamped `NOT FILED`; they are not verdicts.
- **Nothing about grid independence in the radial direction.** §4.2 is explicit: the
  GCI bounds the **axial** channel only. **A `PASS` with a small GCI is NOT a claim
  that the answer is grid-converged**, and `RESULTS.md` must report deviation/GCI and
  the ladder spread beside the verdict, as VMFL005's §5 did (`N-AV7`).
- **Nothing about an inlet turbulence state the manual never fixed** (Finding 4), and
  nothing about the entrance treatment it never budgeted (Finding 3).
- **Nothing about wall roughness.** The manual says "smooth walls"; this case models
  smooth walls; a `PASS` says nothing about rough-pipe behaviour.

The verdict is a statement about **this lab's OpenFOAM v2606 `simpleFoam` + `kEpsilon`
with `nutkWallFunction`, against the manual's Moody-chart reference**, and **only a
`PASS` is a credential**; a `GATE FAIL` is a finding that is never removed, never
re-labelled and never softened.
