# VMFL051 — Isentropic Expansion of Supersonic Flow Over a Convex Corner: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NOT YET RUN. ZERO SOLVER EXECUTION OF ANY KIND.** This file is frozen **before any
solver starts** (CLAUDE.md rule 2; `SUPERVISION_CHARTER.md` §3 check 4).

**The condition, CHECKED and not asserted** (`VERIFICATION_CHARTER.md` §2b.1): at
2026-08-25T00:15:28Z, read with `date -u` in the same invocation,
**`verification/runs/ansys_verification/VMFL051/` does not exist** — `ls -d` returned
*No such file or directory* and `find` beneath it returned **0 files**. Its parent
`verification/runs/ansys_verification/` holds exactly `VMFL001` and `VMFL005` and
nothing else. **No `blockMesh`, no `topoSet` and no `rhoCentralFoam` has been run
for this case** — no mesh exists, so the "mesh generated before the freeze" option
was declined and there is no `checkMesh` summary to declare. `pgrep -a
rhoCentralFoam` returned nothing. The only thing that has executed is the
comparator's own `--selftest` (43 checks, no run tree touched, §11).

**Launch authorisation comes from the `ansys-verification-supervisor`** after its own
personal freeze verification and its own read of the comparator as a diff, **and no
agent message is Sanaa's consent** (CLAUDE.md rule 9).

**Drafted 2026-08-25 by `ansys-lane-opus` (Opus 5) for the `ansys-verification`
team**, under `ANSYS_VERIFICATION_CHARTER.md` §5 and `VERIFICATION_CHARTER.md` §6.
This is **run 1 of VMFL051** — a fresh case, not a re-run. `RESULTS.md` is written
afterwards in this directory and **does not revise this file**; departures land as
dated addenda at the foot, never by editing above.

---

## 0. What this case is, and why it is worth running

**VMFL051: Isentropic Expansion of Supersonic Flow Over a Convex Corner** — Ansys
Fluid Dynamics Verification Manual, Release 2026 R1, **pp. 165–166** (sidecar lines
4268–4327; title page verified against the PDF per CLAUDE.md rule 15 and
`ANSYS_VERIFICATION_CHARTER.md` §4.2). Inviscid, compressible, ideal-gas supersonic
flow turns around a convex corner through a **centred Prandtl-Meyer expansion fan**.
The manual's target is the post-expansion Mach number.

**This is the ansys-verification team's FIRST compressible/supersonic case** and the
lab's declared coverage gap: VMFL001 (rotating annulus) and VMFL005 (Poiseuille pipe)
are both incompressible and both `simpleFoam`. This case is `rhoCentralFoam`, a
density-based shock-capturing solver, on a perfect gas.

**Two things make it unusually valuable, and both are exploited below:**

1. **The target is a CLOSED-FORM EXACT solution**, not an experiment and not a
   benchmark computation. The Prandtl-Meyer function is analytic, so the reference
   contributes *zero* uncertainty of its own and the whole error budget is the lab's.
   This pre-registration therefore computes its own reference to full double
   precision (§2) instead of taking the manual's four printed decimals on trust.
2. **The solution is SMOOTH.** A centred expansion fan contains **no shock**. Every
   other supersonic case this lab has run (the F3 wedge/cone/diamond suite) carries a
   discontinuity, and a shock-capturing scheme is only first-order near a
   discontinuity whatever its nominal order — so an *observed order of accuracy*
   there measures the smearing, not the scheme. Here the flow is smooth everywhere
   except at the corner point itself and along the two bounding Mach lines, and the
   frozen sampling zone (§5) excludes both by more than four coarse cells. **The
   Roache triple of §6 therefore measures something real, and this is stated before
   the answer is known so it cannot be claimed afterwards.**

**This is a statement about this lab's solver against the manual's reference result.
It is NOT a statement about Ansys** (`ANSYS_VERIFICATION_CHARTER.md` §2). This box has
no Fluent and no CFX; `VMFL051_FLUENT.cas` and `VMFL051_CFX.def` were not run, and
**no VM2026R1 archive was opened to write this file** — every number below comes from
the manual's own text or from arithmetic shown here.

**Setup knowledge, and its boundary.** The solver, flux scheme, reconstruction,
thermophysical model and inviscid slip-wall idiom are taken from the **cfd team's
proven compressible toolchain on this box** (`verification/campaign/F3_CONVERSION_PREREGISTRATION.md`
and `verification/runs/F3_runs/`), read for **setup knowledge only**. **None of F3's
gates, bands, reference values or cost figures is reused, and no F3 file is touched
by this case.** Their cases are wedge/cone/diamond **compressions**; this is an
**expansion**, which is exactly why it is worth running.

## 1. The manual, quoted verbatim (pp. 165–166)

**Reference** (p. 165): *"John Anderson. Modern Compressible Flow: With Historical
Perspective. McGraw-Hill Science/Engineering/Math, 2002"*.
**Solver** (p. 165): *"Ansys Fluent, Ansys CFX"*.
**Physics/Models** (p. 165): *"Compressible, inviscid flow"*.

**Test Case** (p. 165), verbatim: *"Centered expansion of inviscid supersonic flow
around a corner is modeled. The expansion results in a change in direction of the
flow, a drop in static pressure, and increase in Mach number. The approaching flow is
supersonic, with a Mach number of 2.5. The expansion process is reversible and
adiabatic."*

**Material Properties** (p. 165): *Density: Ideal Gas law*; *Specific Heat = 1006.43
J/kg-K*; *Molecular weight = 28.966*.
**Geometry** (p. 165): *"Angle round the corner = 195°"* — the interior angle is 195°,
so **the wall turns AWAY from the flow by 15°**.
**Boundary Conditions** (p. 165): *Inlet: Pressure = 202636.9 Pa; Mach number = 2.5;
Static temperature = 300 K (In CFX, the corresponding velocity is specified).*;
*"Wall is adiabatic."*

**Analysis Assumptions and Modeling Notes** (p. 165), verbatim: *"The flow is steady,
inviscid, and incompressible. Analytic expressions for isentropic expansion can be
used to calculate the Mach number downstream of the corner."*

**Results Comparison for Ansys Fluent, Table .51.1** (p. 166) — Mach Number Downstream
of the Corner, after Expansion:

| | Target | Ansys Fluent | Ratio |
|---|---|---|---|
| Mach number after expansion | **3.2370** | 3.2316 | 0.9980 |

**Results Comparison for Ansys CFX, Table .51.2** (p. 166):

| | Target | Ansys *(column header reads "Fluent" — see §1a)* | Ratio |
|---|---|---|---|
| Mach number after expansion | **3.237** | 3.2354 | 0.9995 |

The manual's stated accuracy goal (**§1.3, p. 5**, verbatim): *"The goal for the test
cases contained in this manual was to have results accuracy within 3% of the target
solution."*

### 1a. THREE DEFECTS FOUND IN THE MANUAL — recorded here, before any compute

Recorded now so they cannot be presented later as discoveries that followed a number.
None of them changes the physics modelled below. All three are drafted for
`docs/LESSONS.md` / `docs/NUMERICS_KNOWLEDGE.md` (family `N-AV`) for the
supervisor's read, per `ANSYS_VERIFICATION_CHARTER.md` §7, and are **`NOT FILED`** —
contacting Ansys is Sanaa's alone (§8 of that charter).

**Defect 1 — the manual contradicts itself on compressibility, in the same case.**
"Analysis Assumptions and Modeling Notes" (p. 165) says the flow is *"steady,
inviscid, and **incompressible**"*. Its own "Physics/Models" line on the **same page**
says *"**Compressible**, inviscid flow"*, its Material Properties line specifies
*"Density: Ideal Gas law"*, and the case is a Mach-2.5 isentropic expansion whose
entire content is a compressible one. The word "incompressible" is wrong.
**How wrong, quantified:** an incompressible treatment produces **no Mach change at
all** across the corner — M stays 2.5 against a target of 3.2370, a deviation of
**−22.77 %**. The comparator's `--selftest` fires exactly this arm and confirms it
fails the gate by a factor of 45. *This pre-registration models the flow as
compressible, per the Physics/Models line and the case itself.*

**Defect 2 — the printed target 3.2370 is not the exact Prandtl-Meyer value at any γ
consistent with the case.** Computed in §2 to full double precision:

| γ | ν(2.5), deg | exact M₂ after 15° | vs the printed 3.2370 |
|---|---|---|---|
| **1.3990093734749485** (from the manual's OWN Cp and MW) | 39.160263203801104 | **3.2355411372251863** | **−0.04507 %** |
| 1.4 (the textbook air value the manual does not state) | 39.1235638278973 | **3.2368431056638845** | −0.004847 % |

Neither equals 3.2370. **What 3.2370 is consistent with:** a lookup in a
Prandtl-Meyer table printed to two decimals of ν. At γ = 1.4, ν(2.5) rounds to 39.12°,
so ν₂ = 54.12°, and solving for M at ν₂ = 54.12° / 54.13° gives **3.23664** /
**3.23721** — the printed 3.2370 sits between those two table lines. Equivalently,
3.2370 at γ = 1.4 corresponds to a turn of **15.00276°**, not 15°. The manual's target
therefore carries roughly **0.005 % of table-rounding error** on top of its printed
precision. *This is budgeted explicitly in §3 and is not treated as noise.*

**Defect 3 — Table .51.2's value column is mislabelled.** The section heading on
p. 166 reads *"Results Comparison for Ansys CFX"* and the table caption *"Table .51.2:
Comparison of Mach Number Downstream of the Corner, after Expansion"*, but the value
column header reads **"Ansys Fluent"**. Since Table .51.1 already reports Fluent's
3.2316 and this table reports 3.2354, the column is CFX's and the header is a
copy-paste error. Typographic, no numerical consequence — recorded because the
register's audit trail must be able to say which solver a quoted number came from.

## 2. THE GAS, THE REFERENCE VALUES, AND WHICH ONE THE GATE IS AGAINST

### 2.1 γ is DERIVED from the manual's own Cp and molecular weight — it is not 1.4

The manual gives Cp and the molecular weight and does **not** give γ. Deriving it,
with the arithmetic shown rather than assumed:

- **Universal gas constant.** The value used is **OpenFOAM v2606's own**, because that
  is what the solver will use:
  `RR = 1e3 · N_A · k = 1e3 · 6.0221417930e+23 · 1.38065e-23 = **8314.47006650545** J/(kmol·K)`
  — `N_A` from `src/OpenFOAM/global/constants/fundamental/fundamentalConstants.C:121`,
  `k` from `etc/controlDict:1125` (`SICoeffs/physicoChemical`), and the composition
  `RR = 1e3·physicoChemical::R` with `R = N_A·k` from
  `src/OpenFOAM/global/constants/thermodynamic/thermodynamicConstants.C:46`. All three
  read off the installed tree, not recalled.
- **Specific gas constant.** `R = RR / 28.966 = **287.04239682750293** J/(kg·K)`.
- **γ.** `γ = Cp / (Cp − R) = 1006.43 / (1006.43 − 287.04239682750293)
  = 1006.43 / 719.38760317249707 = **1.3990093734749485**.`

**γ is 1.3990094, not 1.4.** It is stated here, with the arithmetic, precisely because
assuming 1.4 without saying so is how a reference silently acquires a 0.04 % bias.

*Sensitivity of this choice, computed before the freeze:* using the CODATA-2018
constant 8314.46261815324 instead gives γ = 1.3990088734067945 and M₂ =
3.2355404802507177 — a shift of **−6.57e−7 in Mach = 2.03e−5 %**, four orders of
magnitude inside the gate. The comparator's `--selftest` computes and prints this.

### 2.2 The reference values, to full double precision

The Prandtl-Meyer function, and the equation solved:

> ν(M) = √((γ+1)/(γ−1))·atan(√((γ−1)/(γ+1)·(M²−1))) − atan(√(M²−1))
>
> solve **ν(M₂) = ν(2.5) + 15°** for M₂

Solved in `grade_vmfl051.py` by **bracketed bisection** on [1+1e−7, 60] — ν is
strictly monotone increasing for M > 1, so the bracket is guaranteed and the root
unique — to a bracket width below 1e−14, and asserted against frozen literals so a
later edit to the arithmetic cannot silently move the reference.

| symbol | value | what it is |
|---|---|---|
| **R_MANUAL** | **3.2370** | **the manual's printed target, Table .51.1. THE GATE IS AGAINST THIS.** |
| R_MANUAL_CFX | 3.237 | the same target, Table .51.2, printed to one digit fewer |
| ν(2.5), manual's gas | 39.160263203801104° | |
| **M₂_EXACT_GAS** | **3.2355411372251863** | **the closed-form exact answer for the gas the manual specifies (γ = 1.3990093734749485). The DIAGNOSTIC of §3.2 is against this.** |
| M₂_EXACT_γ=1.4 | 3.2368431056638845 | the same solve at γ = 1.4, registered for completeness |
| U₁ | 867.7287202948199 m/s | = 2.5·√(γ·R·300), the inlet velocity the case prescribes |
| p₀ (inlet stagnation) | 3462954.234 Pa | used only by the §5 diagnostics |
| T₀ (inlet stagnation) | 674.0712876 K | used only by the §5 diagnostics |
| μ₁ = asin(1/2.5) | 23.57817847820183° | leading Mach line of the fan |
| μ₂ = asin(1/M₂) | 18.00303133857135° | |
| trailing Mach line, from +x | **3.003031338571351°** | = μ₂ − 15°; **bounds the sampling zone (§5)** |

**Verification of the reference machinery against a published table** (`--selftest`,
already fired, zero compute): the in-module ν at γ = 1.4 reproduces Anderson's
Appendix C to within 5e−5° at M = 1.5, 2.0, 3.0 and 5.0 — 11.905209 vs 11.9052,
26.379761 vs 26.3798, 49.757347 vs 49.7573, 76.920216 vs 76.9202 — and ν(1) = 0.

### 2.3 Which reference the gate is against, and why

**THE GATE IS AGAINST THE MANUAL'S PRINTED TARGET, 3.2370.** `ANSYS_VERIFICATION_CHARTER.md`
§5.1 requires the gate to be *"the reference result as the manual states it"*, and the
manual states the target as its own analytic answer (p. 165: *"Analytic expressions
for isentropic expansion can be used to calculate the Mach number downstream of the
corner"*). Gating against the lab's own recomputed value instead would let the lab
choose its own reference and would make a `PASS` a statement about this lab's
arithmetic rather than about the manual's case.

**M₂_EXACT_GAS = 3.2355411372251863 is registered as a tighter DIAGNOSTIC (§3.2),
printed beside the gate and never able to overturn it.** It is the exact answer for
the gas actually modelled, so it is the honest yardstick for the solver's own
discretisation error once the manual's table-rounding is set aside.

**One property of this case worth stating before it is measured:** the gated quantity
is **independent of p₁ and T₁**. ν depends only on M₁ and γ, so the inlet pressure
202636.9 Pa and temperature 300 K set the scale of the solution and not the answer.
They are used verbatim as the manual states them; a `PASS` here is not evidence that
they were transcribed correctly, and that is declared, not hidden.

**Ansys's own numbers (Fluent 3.2316, ratio 0.9980; CFX 3.2354, ratio 0.9995) are
CONTEXT ONLY** — held in the comparator as `ANSYS_CONTEXT`, printed in the report,
never a gate, never a band, never a reference.

## 3. THE GATE AND ITS TOLERANCE, WITH THE DERIVATION

### 3.1 The gate

> **G-VMFL051:** at the finest level **L3_480x208**,
> **|M_lab − 3.2370| / 3.2370 ≤ 0.005 (0.5 %)**.
> Inside ⇒ gate met; outside ⇒ **`GATE FAIL`**.

`M_lab` is the volume-average of the `Ma` field over the frozen cell zone `gateZone`
at `endTime`, read from the `gateMach` `volFieldValue` function object (§5).

### 3.2 The exact-solution diagnostic — NOT the gate

Against **M₂_EXACT_GAS = 3.2355411372251863**, at L3:
**|M_lab − M₂_EXACT_GAS| / M₂_EXACT_GAS ≤ 0.0025 (0.25 %)**, printed beside the gate.
A row that meets the 0.5 % gate but misses this 0.25 % diagnostic is a **`PASS`** with
the diagnostic printed beside it (the VMFL005 §3 posture). It catches a value that
clears the loose gate while being physically off.

### 3.3 WHERE 0.5 % COMES FROM — the derivation, not a round number

The band must satisfy three independent requirements. Each is computed here, before
any solver has run.

**(i) It must CONTAIN the two declared systematic terms, or the gate is unfair.**
Both are deterministic and computable in advance:

| term | size | why the lab carries it |
|---|---|---|
| **gas-model bias** | **0.04507 %** | modelling the manual's OWN Cp and MW gives γ = 1.3990094, whose exact answer 3.2355411 sits 0.04507 % *below* the printed 3.2370. Using γ = 1.4 instead would halve nothing useful and would depart from the manual's stated properties. |
| **target-print rounding** | **0.01545 %** | the coarser of the manual's two printings of its own target is Table .51.2's `3.237` (4 s.f.), half-width ±0.0005. (Table .51.1's `3.2370` is ±0.00005 = ±0.001545 %; the honest bound is the coarser one.) |
| **sum** | **0.0605 %** | |

So the band must exceed **0.0605 %**. A band tighter than about 0.1 % would be gating
the manual's own printing and its own gas constants rather than the lab's solver.

**(ii) It must be a BAR — capable of failing a plausible-but-wrong treatment.**
Four candidate wrong treatments, and what each would give:

| wrong treatment | value | 0.5 % gate |
|---|---|---|
| **incompressible**, as the manual's own Analysis Assumptions sentence literally instructs (Defect 1) | M unchanged at 2.5 | **FAILS by 45×** (−22.77 %) |
| **sampling inside the fan** instead of clear of it — the failure the frozen §5 rule exists to prevent | anywhere in (2.5, 3.2355) | **FAILS**, by up to 22 % |
| **an under-resolved / first-order-behaving fan** — the realistic numerical failure on this class of problem | O(1 %) undershoot | **FAILS** |
| **γ = 1.4 with the manual's Cp** (ignoring the stated MW) | 3.2368431 | **PASSES** — 0.005 % out. **Declared blind spot: this gate cannot distinguish the two γ.** Stated now, not discovered later. |

**(iii) It must be TIGHTER than the manual's own stated goal, because this target is
exact.** The manual's 3 % goal (§1.3, p. 5) is a single figure covering cases whose
targets are experimental or benchmark computations. VMFL051's target is closed-form
analytic and contributes zero uncertainty of its own, so the lab holds itself to a
tighter class: **0.5 % is the manual's goal divided by 6.**

**The band sits between (i) and (ii):** an order of magnitude above the 0.0605 %
bookkeeping floor, and a factor ≈2 below the O(1 %) failure mode it must catch.

**Cross-check that it is not a formality.** Ansys Fluent's own reported deviation on
this case is **−0.1668 %** and CFX's **−0.0494 %**; both would pass with 3× and 10×
margin. But a lab result merely **three times worse than Fluent's** would **fail**.
That is the definition of a bar, and it is why the band is not set at 0.2 % — setting
it at exactly the deviation a competitor achieved would be choosing a band from an
observed value, which is the thing rule 2 exists to prevent.

**Both arms of the gate are exercised by `--selftest`, with zero compute:** the exact
value for the manual's gas passes (−0.04507 %); a value 0.75 % off fails; the
incompressible treatment fails; Fluent's own value passes.

## 4. Geometry, mesh levels, and the physical endTime

### 4.1 Geometry (frozen, `case/system/blockMeshDict.template`)

Two-dimensional, one cell thick in z (`empty`), z ∈ [−0.01, +0.01] m.

- corner at the **origin**; the wall turns away by **15°** ("Angle round the corner =
  195°")
- inlet plane **x = −0.3 m**; outlet plane **x = +1.2 m**; top **y = +0.65 m**
- upstream wall **y = 0** for x ∈ [−0.3, 0]
- downstream wall **y = −x·tan 15°**, tan 15° = 0.26794919243112271; at x = 1.2,
  y = −0.3215390309173472

**Why the top is at 0.65 m — no wave is reflected, by construction.** The **leading**
Mach line leaves the corner at μ₁ = 23.57817847820183°, so at the outlet plane it
stands at y = 1.2·tan μ₁ = **0.5237229** < 0.65. The **entire fan therefore leaves
through the supersonic (zeroGradient) OUTLET** and never reaches the top boundary,
which sees undisturbed M = 2.5 freestream along its whole length. The top BC cannot
reflect anything because nothing arrives at it.

### 4.2 Mesh levels — refinement ratio 2 BY CONSTRUCTION

| level | upstream × downstream × vertical cells | cells | h (m) |
|---|---|---|---|
| `L1_120x52` | 24 × 96 × 52 | **6,240** | 0.0125 |
| `L2_240x104` | 48 × 192 × 104 | **24,960** | 0.00625 |
| `L3_480x208` | 96 × 384 × 208 | **99,840** | 0.003125 |

Every level **doubles all three counts**, and the block map is linear, so **h halves
exactly and r = 2 by construction** — the refinement ratio is never inferred from a
cell count, so `VERIFICATION_CHARTER.md` §3.1's dimensionality assumption cannot
corrupt it. The downstream block is sheared (its bottom edge follows the inclined
wall), so cells stretch in y with x: dy at x = 1.0 is 0.017653 m at L1, and this
figure is what the §5 inset is sized against.

### 4.3 endTime — the same PHYSICAL TIME at every level

**endTime = 7.0e−3 s at all three levels**, so the Roache triple compares the same
physical state and not three different ones. That is **4.049 flow-throughs** of the
1.5 m domain at the **inlet** speed U₁ = 867.72872 m/s — the slowest speed anywhere in
the domain, so the count is the conservative one (the post-expansion stream runs at
957.87 m/s). The flow is **everywhere supersonic**, so no information travels
upstream and the steady state is established in roughly **one** flow-through; four is
deliberately generous.

**This is an ESTIMATE, fixed before any run and stated as an estimate.** The
**plateau clause of §8 is the actual arbiter**: if a level's gate series has not
plateaued at endTime the rung is **`NOT A RESULT`** and re-runs as a **new rung**
(exactly as VMFL001 R1 → R2), never re-graded in place. Over-budgeting only costs
compute — the solver has no early-exit criterion, so an already-steady level keeps
stepping and stays steady — and that is the safe direction, chosen deliberately.

`deltaT 1e-8` is only a seed; `adjustTimeStep` raises it (capped at 1.2× per step) to
the Courant limit within ~40 steps at every level. `maxDeltaT 1e-5` is **above** the
L1 CFL step of 3.99e−6 s, so it never binds and `maxCo 0.4` governs.

## 5. THE FROZEN SAMPLING RULE — where the answer is read, fixed before any answer exists

**Sampling-location freedom after seeing the answer is how a gate gets chosen to fit.**
This section is the defence against that, and it is frozen in
`case/system/topoSetDict` in **absolute physical coordinates, identical at every mesh
level**.

### 5.1 The region, and why it is where it is

The post-expansion **uniform** region is the wedge between

- the downstream **wall**, y = −x·tan 15°, tan = 0.26794919243112271, and
- the **trailing Mach line**, y = +x·tan(μ₂ − 15°), tan = 0.05246083158162142,

where μ₂ = 18.00303133857135° follows from the frozen M₂_EXACT_GAS. Between those two
rays the exact solution is **exactly uniform at M₂**, so any volume weighting returns
M₂ exactly and the choice of weighting cannot bias the answer.

**x window: [1.00, 1.15] m.** The wedge is narrowest at its upstream face, so both
insets are computed **at x₁ = 1.00 m**, which makes the zone strictly inside the wedge
for every x in the window. The window stops at 1.15 m, 0.05 m clear of the outlet, so
the outflow boundary's own cells are excluded.

**INSET δ = 0.075 m off BOTH bounding rays — derived, not chosen.** At L1 the cells in
the downstream block at x = 1.00 have dy = (0.65 + 1.00·0.26794919)/52 = **0.017653 m**.
δ = 0.075 m = **4.25 × dy(L1)** = 6.0 × h(L1). So **even at the coarsest level the zone
edge stands more than four coarse cells clear** of both the exact trailing Mach line
and the wall, and the numerically smeared C¹ kink at the fan's tail cannot reach into
the average. At L3 the same 0.075 m is **17 fine cells**.

> **`gateZone` (THE GATE):** x ∈ [1.00, 1.15], y ∈ [**−0.1929491924311227**,
> **−0.02253916841837858**], band height 0.170410024013 m, z unbounded.

### 5.2 The instrument

`Ma` is computed by the v2606 **`MachNo`** function object, which stores its result
under the name **`Ma`** as `mag(U)/sqrt(γ·p/ρ)`
(`src/functionObjects/field/MachNo/MachNo.C`: `setResultName("Ma","U")` and the
`store(...)` call). It is placed **first** in the `functions` dictionary because
`functionObjectList::execute()` calls `execute()` then `write()` for each object **in
dictionary order** (`functionObjectList.C:615`), so `Ma` is in the registry before the
averaging object reads it.

The gated value is `volAverage(Ma)` over `gateZone`, written **every timestep** by a
`volFieldValue` function object named `gateMach`, so the plateau clause of §8 has a
dense series. The reader is built directly against the **v2606 writer source**, not a
belief about it — the lesson of VMFL001 run 1 (N-AV4 / L-286):

- path `postProcessing/gateMach/0/volFieldValue.dat` — `writeFile.C` `baseFileDir()`
  (`globalPath()/"postProcessing"`) and `baseTimeDir()` (= `prefix_/timeName`), with
  `fieldValue.C:56` passing the object **name** as `prefix_` and the valueType
  `"volFieldValue"` as the base file name;
- header `# Region : cellZone gateZone`, `# Cells  : N`, `# Volume : V` from
  `volRegion.C:133–144`, then `# Time` followed by `<tab>volAverage(<field>)` per
  requested field from `volFieldValue.C:106–133`;
- data `writeCurrentTime` then `file() << tab << sresult` per field
  (`volFieldValueTemplates.C:314`), at the object's `writePrecision` (12, set in
  `controlDict`).

**Columns are located BY HEADER NAME, never by position.** The `# Cells` line is a
control in its own right: the comparator **refuses (exit 2)** if it is absent or
reports **0** — *an empty sampling zone reads as a number and must never be graded* —
and `run_vmfl051.sh` refuses before the solver even starts if `topoSet` put zero cells
into either zone.

### 5.3 Declared diagnostics, which are NEVER the gate

1. **`gateZoneInner`** — the same average over a **strictly smaller** zone at inset
   δ = 0.110 m: x ∈ [1.00, 1.15], y ∈ [−0.1579491924311227, −0.05753916841837858].
   If the gate zone were being contaminated from an edge, the two averages would
   diverge. Printed beside the gate. **It carries one declared clause that can only
   produce `NOT A RESULT`, never a `PASS`** (§6): a relative disagreement above
   **1e−2** at L3 makes the row `NOT A RESULT`.
2. **Two independent re-derivations of the Mach number from scalar averages**, using
   only the frozen inlet stagnation state and the isentropic relations:
   `M = √( 2/(γ−1)·((p₀/⟨p⟩)^((γ−1)/γ) − 1) )` and `M = √( 2/(γ−1)·(T₀/⟨T⟩ − 1) )`.
   These test the `MachNo` object against the primitive fields and test the isentropy
   of the expansion — the physics of the case. **Printed, never gated.**

## 6. THE VERDICT ORDER (CLAUDE.md rule 5), in its stated order

1. **any level not plateaued** — peak-to-peak of the `volAverage(Ma)` gate series over
   its **last 20 %** exceeding **1.0e−3 in Mach** (= 3.1e−4 relative, 16× tighter than
   the gate) — or failing any completion clause of §8 ⇒ **`NOT A RESULT`**;
   **and** the declared inner-zone clause: |⟨Ma⟩_gate − ⟨Ma⟩_inner| / ⟨Ma⟩_gate >
   **1e−2** at L3 ⇒ **`NOT A RESULT`**;
2. **Roache triple** on the post-expansion Mach number `DIVERGENT` / `STAGNANT` /
   `OSCILLATORY` / `EXACT` ⇒ **`NOT A RESULT`**, with the three values, R, the
   increments and the observed order printed beside it, and **no GCI quoted**;
3. **`CONVERGING`** ⇒ **`PASS`** inside the 0.5 % band else **`GATE FAIL`**, with
   **GCI at Fs = 1.25** printed and the Richardson extrapolation beside it.

**The gate can only turn a `PASS` or a `GATE FAIL` INTO `NOT A RESULT`, never the
reverse.** Classification thresholds are fixed in the comparator before any run:
`EPS_ABS = 1e−12` (a level-to-level difference below this is zero), `STAG_TOL = 1e−3`
(|R − 1| within this is `STAGNANT`), `RATIO = 2.0`, `FS = 1.25`. All five states are
exercised by `--selftest`.

**Expected order, stated before it is measured.** `rhoCentralFoam` is nominally
second-order in smooth flow; the zone excludes the corner singularity and both
bounding Mach lines by more than four coarse cells (§5.1), so the observed order
should be near 2. **A first-order or fractional observed order is a real finding
about the scheme on a centred fan and will be reported as measured, whatever it is** —
it is not a reason to move a band.

## 7. Planted-zero controls (CLAUDE.md rule 3) — three, none optional, none skippable

The comparator **exits 2** if any fails. None can be disabled by a flag. The run tree
is **never modified** — every plant is written into a temporary copy.

| id | reader under test | plant | refusal condition |
|---|---|---|---|
| **PZ-1** | the **gated `.dat` reader** | **+1.234e−03 Mach** added to the `volAverage(Ma)` column of a **copy** of the real `volFieldValue.dat`, read back from disk by the same extraction function | the read-back offset differs from the plant by > 1e−12 |
| **PZ-2** | the **`Ma` FIELD reader** | **+7.77e−02 Mach** added to every internal value of a **copy** of the real `<endTime>/Ma` volScalarField, read back from disk | the read-back mean shift differs from the plant by > 1e−9 |
| **PZ-3** | the **reference computation itself** | **+5°** added to the turn angle | the solved M₂ fails its own identity ν(M₂) − ν(M₁) = 15° to 1e−9°, **or** a 5° change of turn moves M₂ by less than 1e−6 — i.e. the root finder is returning a constant |

**Each control has BOTH arms.** The negative arm re-reads an *unplanted* copy and
requires **no** signal; the positive arm requires **exactly** the plant. Both arms of
all three fire in `--selftest` on fixtures written in the real file formats.

**PZ-2 is the control the brief asks for and the one this case most needs**: it is the
only one that demonstrates the comparator can read a **non-zero out of the Mach field
on disk**. PZ-2 additionally refuses if the `Ma` field at endTime is `uniform` — *a
uniform Mach field after an expansion fan is not a solution* — and reports the field's
min, max and mean as diagnostics.

## 8. Strict completion (CLAUDE.md rule 4), with TWO DEPARTURES DECLARED ON THE FACE

The comparator refuses (exit 2) on any failed clause and **never grades a partial run**.

| clause | as checked here |
|---|---|
| **C1** `rc = 0` | `RUN_RC.txt`, written by the launcher, reads `rc=0` |
| **C2** an `End` line | `^End$` present in `log.rhoCentralFoam` |
| **C3** last time == `endTime` | **DEPARTURE 1, below** |
| **C4** fields present at endTime | **`T U p rho Ma`** — this case's own declared list, not the thermal family's |
| **C5** `ExecutionTime` count == `endTime` | **DEPARTURE 2, below** |
| **C6** age guard | **STRICTER than the rule** |

**DEPARTURE 1 (C3).** `rhoCentralFoam` runs with `adjustTimeStep yes`, so the rule's
literal equality is not the right test for an adaptive-step solver. It is replaced by
**|t_last − endTime| ≤ maxDeltaT (1e−5 s against an endTime of 7e−3 s)** *and* the
log's own final `Time =` agreeing with the last time directory to 1e−12 relative. The
same departure was declared by the cfd team's F3 conversion for the same solver and
the same reason; it is restated here rather than inherited silently.

**DEPARTURE 2 (C5).** The rule's literal clause is a **steady-iteration** clause: it
holds when one iteration is one time unit. This solver is transient with an adaptive
step, so its step count (~1,800 at L1) is not `endTime` (7e−3) and never can be. The
invariant the clause exists to protect — *the log is not truncated mid-step* — is
checked **directly** instead: `count(^ExecutionTime = ) == count(^Time = )`, and > 0.

**C6 is STRICTER than the rule, not looser.** The rule dates the run from `0/T`; this
check dates it from the **latest mtime anywhere in the case's own `0/`**, and
`run_vmfl051.sh` touches **every file in `0/`** as the last action before the solver
launches. Every field at endTime must be **strictly newer** than that datum.

**The launcher enforces the rule's own guard**: `run_vmfl051.sh` **refuses to start
into any pre-existing level directory** (rule 4's "a guard refuses a case where `0` or
a time dir already exists"), refuses unless this pre-registration is **committed at
HEAD**, refuses if `topoSet` left either sampling zone empty, and enforces the cap
with `timeout`.

## 9. Cost (CLAUDE.md rule 12, and L-291's four numbers)

**L-291 requires a POINT ESTIMATE and a CEILING for EACH of two components** —
executed compute and lane wall — and a "≤ N" in a predicted column is not a forecast.
All four are registered here.

### 9.1 Executed compute

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × 1 / 60 |
| **basis** | the cfd team's F3 **measured** `rhoCentralFoam` throughput on this box: 18.7 s for 7,200 cells × 3,900 steps and 146.4 s for 28,800 cells × 7,016 steps ⇒ **6.65e−7 and 7.24e−7 s per cell-step**; the **higher** figure, 7.24e−7, is used. This is a measurement of the *solver on this hardware*, borrowed as setup knowledge; **no F3 gate, band or reference is borrowed.** |
| step counts | dt = 0.4·h/(U₂+a₂) = 0.4·0.0125/1253.9 = 3.988e−6 s at L1 ⇒ 1,755 steps; doubling the mesh halves dt, so 3,510 and 7,020 at L2, L3 |
| solver estimate | L1 6,240×1,755 = 1.095e7 cell-steps → **7.9 s**; L2 8× → **63.4 s**; L3 8× → **507.5 s**; subtotal **579 s** |
| + `blockMesh` + `checkMesh` + `topoSet`, three levels | ~**40 s** (an estimate) |
| + `MachNo` and two `volFieldValue` objects evaluated **every** timestep | ~10 % of solver ≈ **58 s** (an estimate) |
| **POINT ESTIMATE** | **677 s = 11.3 core-minutes** |
| **CEILING (the enforced cap)** | **28 core-minutes** = 2.48 × the point estimate, enforced by `timeout` inside `run_vmfl051.sh`; **an overrun STOPS the run and it does not get a new budget** |
| authorised for this case | **30 core-minutes** by the supervisor; the cap is set **under** it, and the authorisation is a per-item cost, **not a new ceiling** (rule 9) |
| dollars at the point estimate | **$0.00966** |
| dollars at the ceiling | **$0.02394** |
| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). The per-cell-step rate is F3's **measurement**; the VMFL051 step counts, the meshing time and the function-object margin are **ESTIMATES**. |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; a blanket is not a per-item read (rule 9) |

### 9.2 Lane wall, priced separately (L-291)

| component | point estimate | ceiling |
|---|---|---|
| **this drafting lane** (read the manual; four charters; two precedents; verify the OpenFOAM writer, `MachNo`, `topoSet` and gas-constant sources against the installed tree; build the case tree; write and selftest the comparator; write and commit this freeze) | **35 lane-minutes** | **60 lane-minutes** |
| **the later run-and-grade lane** (launch, monitor, grade, draft `RESULTS.md`, the register row and the calibration row) | **20 lane-minutes** | **40 lane-minutes** |

### 9.3 Calibration at completion

At completion the team compares **each component against its own pair**: actual
core-minutes from `RUN_RC.txt`/`COST.txt` against the 11.3 point estimate, and actual
lane wall against the figures above; ratio, attribution (contention, waste,
misprediction — waste named separately, never absorbed into the ratio); dollars
derived at $0.0513/core-h and labelled **derived, not measured**; **one row appended
to `docs/COST_CALIBRATION.md`** under its append rules and the rule-10 private-index
protocol. **A completion report without that row is incomplete** (rule 12).

## 10. The grading path, frozen (VERIFICATION_CHARTER §2d)

The comparator, the run script and the whole case tree were committed **BEFORE this
file**, at commit **`dd49dcee476be1b92d48c86155f9f7311aa29427`**
("VMFL051 case inputs and comparator — NO COMPUTE, pre-registration not yet frozen"),
and that commit precedes any solver. At analysis time the grading path is re-hashed
against these blob shas; a freeze that is claimed and not checked is a claim about
intent.

| what | path under `cases/ansys_verification/VMFL051/` | committed blob sha |
|---|---|---|
| **comparator (THE GRADING PATH)** | `grade_vmfl051.py` | **`acad1aff71da4a960045484f9e6f8470f8beccb7`** |
| run script | `run_vmfl051.sh` | `b531b9c08f1b59c54c3b50f58a84b9feac92a7e8` |
| **the frozen sampling rule** | `case/system/topoSetDict` | **`e594d35fe9aa8accb77bde4a8f3fd335ec2e31d8`** |
| blockMeshDict template | `case/system/blockMeshDict.template` | `7557bfec1e18f6956e3ed09185f45627af4c32a0` |
| controlDict template (endTime + the three function objects) | `case/system/controlDict.template` | `48607d91d9c79fda5988430e766a663b5a6d7b4f` |
| fvSchemes | `case/system/fvSchemes` | `25d6f166ffae418d428473f5aeae2e17e8d0bfc6` |
| fvSolution | `case/system/fvSolution` | `885bb5f6ddccc67376a3171ace339bc476f5302b` |
| `0/U` (inlet velocity + age-guard datum) | `case/0/U` | `9d8f63f1ffcb7d5fb652542cd0050261aef963b9` |
| `0/T` | `case/0/T` | `84d6430dc9f32f458141d3dcf2335b98418beca3` |
| `0/p` | `case/0/p` | `3da7331987499f8863e4a7667fd09dec87c4f428` |
| thermophysicalProperties (the manual's own Cp and MW) | `case/constant/thermophysicalProperties` | `3734a5a0d9967cff4b1411b359e8ed59d17ae9f6` |
| turbulenceProperties | `case/constant/turbulenceProperties` | `5459d691884eeba27e9759a8bc32871ea262edab` |

**Verified at grade time, not merely recorded.** `grade_vmfl051.py --verify-frozen
<commit>` reads its own bytes, compares them against `git cat-file blob
<commit>:cases/ansys_verification/VMFL051/grade_vmfl051.py`, and **REFUSES (exit 2)**
if the file on disk is not byte-identical to the committed blob. **No threshold, band,
reference value or plant constant in the comparator is settable from the command
line**; every one is a module-level constant fixed by commit `dd49dcee`.

**Run outputs go to `verification/runs/ansys_verification/VMFL051/<level>/`**, never
beside this prose (`FILING_CHARTER.md` R6). **The grading JSON is
`verification/runs/ansys_verification/VMFL051/GRADING_VMFL051.json`.**

## 11. What CANNOT be verified before the freeze — stated plainly

**No VMFL051 solver has run, and no mesh exists.** What *has* fired, with **zero
solver compute**: the comparator's `--selftest`, **43 checks, 0 failures** — the gas
derived from the manual's own Cp and MW; the CODATA sensitivity; the Prandtl-Meyer
function against Anderson's Appendix C at four Mach numbers; every frozen reference
literal; the reader on the real `volFieldValue.dat` format including its two refusal
arms (a short data row, and a zero-cell region); both arms of all three planted-zero
controls on fixtures in the real formats; all five Roache states; and both arms of the
gate including the incompressible treatment and Fluent's own value.

Four things this lab has **not** seen, each of which the first cheap step would
settle, and **each of which the supervisor must authorise separately — even
`blockMesh` alone is not covered by this freeze**:

1. **That the mesh builds.** No `blockMesh` has run, so no `checkMesh` summary can be
   quoted here. The declaration is therefore the strong one: **the mesh did not exist
   when this gate was frozen.**
2. **That `topoSet` puts cells into both frozen zones.** The box coordinates are
   derived arithmetic (§5.1), not a measurement. If either zone comes out empty the
   run script **refuses before the solver starts** — that is a finding, and it would be
   repaired by a dated addendum that cannot move a gate, threshold, cap or label.
3. **The live `volFieldValue.dat` and `Ma` field on disk.** The readers are built from
   the v2606 writer **source** (§5.2), which is stronger than VMFL001 run 1's
   belief-based reader, but no VMFL051 run has produced either file. The cheap,
   decisive check after the first coarse level is
   `python3 cases/ansys_verification/VMFL051/grade_vmfl051.py --dryrun-reader
   verification/runs/ansys_verification/VMFL051/L1_120x52/postProcessing/gateMach/0/volFieldValue.dat`,
   which prints **only** `parsed, N rows, ...` and **never a value** — the exact
   pre-freeze external-reader check L-286 names, built so it cannot leak the answer.
4. **That L3 plateaus within 7.0e−3 s** (§4.3 is an estimate). If it does not, the
   comparator returns **`NOT A RESULT`** and the rung re-runs as a **new row** — no
   gate, threshold, cap or label moves.

Any change to the comparator after the first VMFL051 solve is a **dated addendum**
disclosing exactly what changed and whether it could move a number, read by the
supervisor before any re-grade.

## 12. Verdict vocabulary, and what this rung will NOT claim

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (CLAUDE.md rule 1). `PENDING` here means **not yet run** and is never
used to soften a `GATE FAIL`.

**Nothing about Ansys.** Fluent's 3.2316 and CFX's 3.2354 are context (§1), never the
gate; this box has no Fluent and no CFX and neither archive was opened.

**Nothing about the manual's own correctness beyond what §1a records.** The three
defects are findings about the document, drafted for the lessons and numerics files
and stamped `NOT FILED`; they are not verdicts and they are not sent anywhere.

**Nothing about p₁ or T₁.** The gated quantity is independent of both (§2.3), so a
`PASS` is not evidence that they were transcribed correctly.

**Nothing about the γ = 1.4 alternative.** §3.3 declares that this gate cannot
distinguish γ = 1.3990094 from γ = 1.4; it is a blind spot, stated before the answer.

The verdict is a statement about this lab's `rhoCentralFoam` against the manual's
Prandtl-Meyer reference, and **only a `PASS` is a credential**; a `GATE FAIL` is a
finding that is never removed, never re-labelled and never softened.

---

## Amendment 1 — 2026-08-25, BEFORE FIRST COMPUTE. Version 1.1.

**Lines whose number changed above this section: 0.** Nothing above is edited;
this section is appended at the foot (CLAUDE.md rule 6).

**Legality, and the condition CHECKED not asserted** (CLAUDE.md rule 2;
`VERIFICATION_CHARTER.md` §2b.1). Amendments before first compute are legal and must
name the run directory that does not exist. At **2026-08-25T00:22:35Z**, read with
`date -u` in the same invocation, **`verification/runs/ansys_verification/VMFL051/`
does not exist** — `ls -d` returned *No such file or directory* and `find` beneath it
returned **0 files**. No `blockMesh`, no `topoSet`, no `rhoCentralFoam` has run and no
mesh exists. **This amendment therefore precedes all compute.**

**It changes NO gate, NO threshold, NO cap and NO label.** The gate stays
|M_lab − 3.2370| / 3.2370 ≤ 0.005 at L3; the exact-value diagnostic stays 0.25 %; the
cap stays 28 core-minutes; the verdict vocabulary is untouched. What it adds is
(A) a **reading rule** — what each Roache outcome will be taken to MEAN — registered
before the answer exists, and (B) a **modelling-bias declaration** that §9's error
budget did not address. Both are additions to the *interpretation and the budget*,
never to the gate.

**Occasion.** Two team facts landed in `docs/NUMERICS_KNOWLEDGE.md` after this
document was drafted and were relayed by the `ansys-verification-supervisor`:
**N-AV7** (a small GCI licenses no claim that a residual deviation is numerical) and
**N-AV9** (an axisymmetric wedge carries a `sin(t)/t` modelling bias refinement never
removes). Both bear directly on this case, which is the cleanest exact-target case
this team has attempted.

### A1.1 What each Roache outcome will MEAN — registered in advance, and NOT a prediction

**No prediction of which outcome will occur is registered here, and none may be
inferred from the order below.** What is registered is the *reading*, so that the
interpretation cannot be chosen to fit the number once it exists. This is the
VMFL051 form of the error N-AV7 names.

**The comparison that matters is against `M₂_EXACT_GAS = 3.2355411372251863`, NOT
against the printed 3.2370.** This is the load-bearing point and it is stated before
any compute: the printed target sits **0.04507 % above** the exact answer for the gas
actually modelled (§1a Defect 2, §3.3), and that offset is a **bookkeeping term of the
manual's own table, not a property of the solver**. Comparing a Richardson extrapolate
against 3.2370 would silently attribute that 0.04507 % to discretisation error — which
is precisely N-AV7's failure in this case's clothing. The extrapolate is therefore read
against the exact value only.

Two quantities, both **already computed and printed by the frozen comparator** and
neither of them a gate — `triple.f_extrapolated` and `triple.gci_fine` are in the
grading JSON at blob `acad1aff…`, so nothing new is being added to the grading path:

- **ρ ≡ |dev of the fine level vs `M₂_EXACT_GAS`| / GCI_fine** — how many times the
  fine-grid discretisation uncertainty the residual deviation is. (N-AV7's own column:
  VMFL001-R2 = 0.79; VMFL005 = 9.92.)
- **dev_extrap ≡ |M_extrapolated − `M₂_EXACT_GAS`| / `M₂_EXACT_GAS`** — whether
  refinement closes the gap or not.

**The threshold on dev_extrap is SELF-SCALING and carries no chosen constant.** A
Richardson extrapolate's own uncertainty is of the order of the GCI that produced it,
so the criterion is **dev_extrap ≤ GCI_fine** — the extrapolate lands on the exact
value *within its own convergence uncertainty*. There is no arbitrary number to
choose, and the two precedents sit three orders of magnitude apart on it
(VMFL001-R2 landed at 3.7 ppm; VMFL005 landed 0.5383 % away against a 0.0502 % GCI),
so it separates them robustly.

| reading | condition | what it will be taken to mean |
|---|---|---|
| **(a) the VMFL001-R2 pattern** | triple `CONVERGING` **and** dev_extrap ≤ GCI_fine **and** ρ ≤ 1 | The residual deviation from the closed-form answer is **consistent with discretisation error**, and refinement carries the solution ONTO the exact Prandtl-Meyer value. On a smooth, shock-free, exactly-solvable target this is the strongest code-verification evidence this team can produce, and it is what would be put forward for a V-column hold. **Putting it forward is a recommendation to the supervisor, not a verdict this lane may issue.** |
| **(b) the VMFL005 pattern** | triple `CONVERGING` **and** dev_extrap > GCI_fine | Grid refinement does **not** close the gap: a **modelling or setup bias the grid cannot remove** is present, and ρ quantifies how much of the residual is not discretisation. The row may still be a `PASS` on the gate — the two are independent — but **it is NOT evidence of convergence to the exact solution and will not be presented as such**, and the open mechanism goes to the docket as VMFL005's did (`D512`). |
| **(c) indeterminate** | triple `CONVERGING` **and** dev_extrap ≤ GCI_fine **but** ρ > 1 | Recorded as **indeterminate**, with both numbers printed and **neither (a) nor (b) claimed**. An honest third cell exists precisely so a borderline row cannot be rounded into the flattering one. |
| **(d)** | triple not `CONVERGING` | Rule 5 step 2 already governs: **`NOT A RESULT`**, no GCI quoted, and none of the readings above is available at all. |

**None of (a)–(d) can change the verdict**, which comes only from §6 in rule 5's stated
order. They fix what `RESULTS.md` may claim about the number, not what the number is.

### A1.2 N-AV9 does not apply to this case, and what stands in its place

**This case is a PLANAR 2-D slab, NOT an axisymmetric wedge.** Verified against the
committed dictionary (`case/system/blockMeshDict.template`, blob
`7557bfec1e18f6956e3ed09185f45627af4c32a0`): every vertex sits at z = −0.01 or
z = +0.01 exactly, the front and back faces are a single `defaultFaces` patch of
**`type empty`**, and the word `wedge` appears nowhere in the dictionary — there is no
`wedge1`/`wedge2` pair and no included angle `t`. The mesh is one cell thick between
two parallel planes.

**Therefore the `sin(t)/t` area deficit of N-AV9 is EXACTLY ZERO here and is absent
from this case's error budget** — the term arises from representing a circular sector
by a flat-sided triangle, and there is no sector. This is stated explicitly rather than
left unaddressed, as the supervisor's relay requires, because every axisymmetric case
this team runs from now on carries that term.

**What stands in its place — the analogous "modelling error the grid cannot remove"
for VMFL051, declared now.** N-AV9's real lesson is structural: *an error living in a
direction the Roache triple does not refine is carried to the extrapolate rather than
removed by it.* Its VMFL051 counterparts are two, and both are already quantified above:

1. **The gas-model term, 0.04507 %.** γ = 1.3990094 from the manual's own Cp and MW
   against the γ = 1.4 the manual's printed target implies (§1a Defect 2). It is
   **invariant under mesh refinement** and is carried straight to the extrapolate.
   Against the **printed target** it is a real 0.04507 % offset; against
   **`M₂_EXACT_GAS` it is zero by construction**, which is exactly why A1.1 reads the
   extrapolate against the exact value and not against 3.2370.
2. **The corner singularity.** The expansion is centred on a single point at which the
   exact solution is not differentiable. Refinement moves the singular cell but never
   removes it, so any error it injects into the far field is a candidate for surviving
   to the extrapolate. It is **not** quantified in advance — no honest pre-compute
   bound exists for it — and saying so now is the point: if reading (b) occurs, this is
   a named candidate mechanism and not a mechanism invented afterwards.

**Neither term moves the gate, the band or the cap.** Both are recorded so that a
converging-triple `PASS` cannot be mistaken for convergence to the exact value — the
mistake N-AV7 exists to prevent.

### A1.3 What this amendment does NOT do

It registers **no prediction** of which reading will occur; it adds **no clause** that
can turn a `GATE FAIL` into a `PASS`; it touches **no** frozen blob — the comparator,
the sampling rule and every case dictionary remain exactly as committed at
`dd49dcee476be1b92d48c86155f9f7311aa29427`, and `--verify-frozen` still passes against
that commit. The grading path is unchanged and unchanged-able.
