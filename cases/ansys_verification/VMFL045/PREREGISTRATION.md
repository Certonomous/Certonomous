# VMFL045 — Oblique Shock Over an Inclined Ramp: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NOT YET RUN. ZERO SOLVER EXECUTION OF ANY KIND.** This file is frozen **before any
solver starts** (CLAUDE.md rule 2; `SUPERVISION_CHARTER.md` §3 check 4).

**The condition, CHECKED and not asserted** (`VERIFICATION_CHARTER.md` §2b.1): at
2026-08-25T01:15:42Z, read with `date -u` in the same invocation,
**`verification/runs/ansys_verification/VMFL045/` does not exist** — `ls -d` returned
*No such file or directory* and its parent `verification/runs/ansys_verification/`
holds exactly `VMFL001`, `VMFL005` and `VMFL051` and nothing beginning `VMFL045`. **No
`blockMesh`, no `topoSet` and no `rhoCentralFoam` has been run for this case** — no
mesh exists, so the "mesh generated before the freeze" option was declined and there
is no `checkMesh` summary to declare. `pgrep -a rhoCentralFoam` returned nothing (the
fleet is invisible to `pgrep`, L-41; the run tree's absence is the load-bearing
check). The only thing that has executed is the comparator's own `--selftest` (45
checks, 0 failures, no run tree touched, §11).

**Launch authorisation comes from the `ansys-verification-supervisor`** after its own
personal freeze verification and its own read of the comparator as a diff, **and no
agent message is Sanaa's consent** (CLAUDE.md rule 9).

**Drafted 2026-08-25 by `ansys-lane-opus48` (Opus 4.8) for the `ansys-verification`
team**, under `ANSYS_VERIFICATION_CHARTER.md` §5 and `VERIFICATION_CHARTER.md` §6.
This is **run 1 of VMFL045** — a fresh case, never run in this lab before.
`RESULTS.md` is written afterwards in this directory and **does not revise this
file**; departures land as dated addenda at the foot, never by editing above.

**Precedent.** The structure, the comparator idiom (a `refuse()` that exits 2, three
planted-zero controls against the real artifacts, a Roache that returns a STATE, a
`grade()` implementing rule 5 in order), and the strict-completion departures are
taken from VMFL051, which the supervisor personally audited and accepted. VMFL051 came
back `NOT A RESULT` (its coarse levels did not plateau); §7 here is written expressly
to avoid that outcome.

---

## 0. What this case is, and why it is worth running

**VMFL045: Oblique Shock Over an Inclined Ramp** — Ansys Fluid Dynamics Verification
Manual, Release 2026 R1, **pp. 153–154** (sidecar lines 3924–3987; title page verified
against the PDF per CLAUDE.md rule 15 and `ANSYS_VERIFICATION_CHARTER.md` §4.2).
Supersonic laminar flow (inlet Mach ≈ 2.5) over a 15° compression ramp forms an
**attached weak oblique shock**; the manual's targets are the Mach number,
temperature and density **downstream of the shock**.

**This closes two of the lab's declared coverage gaps at once:**

1. **The first SHOCK-capturing case the team grades.** VMFL001 and VMFL005 are
   incompressible `simpleFoam`; VMFL051 is compressible but its solution is a **smooth**
   expansion fan with no discontinuity. VMFL045 is the team's first genuine
   **discontinuity** — an oblique compression shock — so it exercises the
   shock-capturing behaviour of the toolchain, not just its smooth-flow accuracy.
2. **The first EXACT analytic compression target.** The reference is the closed-form
   oblique-shock solution (theta–beta–M relation for the weak root, plus the
   normal-shock jump relations on the shock-normal Mach component), so the target
   contributes *zero* uncertainty of its own and the whole error budget is the lab's.
   This file computes that reference to full double precision (§2) rather than taking
   the manual's four printed digits on trust.

**Toolchain reuse.** The solver (`rhoCentralFoam`, OpenFOAM v2606), the Kurganov flux
with vanLeer reconstruction, the perfect-gas `hePsiThermo` model and the age-guard /
sampling idiom are taken from the team's VMFL051 case and the cfd team's F3 supersonic
suite, read **for setup knowledge only**. **None of those cases' gates, bands,
reference values or cost figures is reused, and no VMFL051 or F3 file is touched.**

**This is a statement about this lab's solver against the manual's reference result. It
is NOT a statement about Ansys** (`ANSYS_VERIFICATION_CHARTER.md` §2). This box has no
Fluent and no CFX; `VMFL045_obliqueshock.cas` and `ramp_supersonic_tet.def` were not
run, and **no VM2026R1 archive was opened to write this file** — every number below
comes from the manual's own text or from arithmetic shown here.

## 1. The manual, quoted verbatim (pp. 153–154)

**Reference** (p. 153): *"F. M. White. Fluid Mechanics. 3rd Edition. McGraw-Hill Book
Co., New York, NY. 560–567. 1994."*
**Solver** (p. 153): *"Ansys Fluent, Ansys CFX"*.
**Physics/Models** (p. 153): *"Compressible flow in supersonic regime, Oblique
shock"*.

**Test Case** (p. 153), verbatim: *"Supersonic flow over a 15° ramp is modeled. The
ramp leads to the formation of an oblique shock. Inlet Mach number is about 2.5. The
flow is laminar. Inlet density is 1.22 kg/m3 and inlet temperature is 289 K. The
simulation values are taken at a Point 1 (x=0.38 m, y=0.14 m)."*

**Material Properties** (p. 153): *Density: Ideal Gas*; *Viscosity: 1 × 10⁻⁸
kg/m-s*; *MW: 0.02896 kg/mol*. **No specific heat is given** (see §1a).
**Geometry** (p. 153): *Angle of the ramp = 15°*; *Length = 0.4572 m*.
**Boundary Conditions** (p. 153): *Inlet velocity = 852.68 m/s*; *Inlet temperature =
289 K*; *Inlet pressure = 101226.4 Pa*; *Wall: Adiabatic*.

**Analysis Assumptions and Modeling Notes** (p. 153), verbatim: *"The flow is steady
and laminar. The walls are assumed to be adiabatic."*

**Results Comparison, Table .45.1 (Ansys Fluent)** and **Table .45.2 (Ansys CFX)**,
*"Comparison of Properties Downstream of the Oblique Shock"* (p. 154):

| quantity | **Target** | Ansys Fluent | Fluent ratio | Ansys CFX | CFX ratio |
|---|---|---|---|---|---|
| **Mach Number** | **1.874** | 1.902 | 1.015 | 1.871 | 0.9984 |
| Temperature, K | **382.0** | 377.6 | 0.9885 | 382.8 | 1.002 |
| Density, kg/m³ | **2.277** | 2.233 | 0.9807 | 2.278 | 1.000 |

The manual's stated accuracy goal (**§1.3, p. 5**, verbatim): *"The goal for the test
cases contained in this manual was to have results accuracy within 3% of the target
solution."*

### 1a. FINDINGS IN THE MANUAL — recorded here, before any compute

Recorded now so they cannot be presented later as discoveries that followed a number.
None changes the physics modelled below. All are drafted for `docs/LESSONS.md` /
`docs/NUMERICS_KNOWLEDGE.md` (family `N-AV`) for the supervisor's read, and are **`NOT
FILED`** — contacting Ansys is Sanaa's alone (`ANSYS_VERIFICATION_CHARTER.md` §8).

**Finding 1 — UNDER-SPECIFICATION: no specific heat is given, so γ cannot be derived
as VMFL051's was.** VMFL051 gave Cp and MW and γ was *derived*; VMFL045's Material
Properties list gives only density law, viscosity and molecular weight. γ is therefore
not determinable from the manual's own VMFL045 data. **How it is resolved (§2):** the
case's over-determined inlet data pins γ = 1.4. The ideal-gas identity ρ₁ = p₁/(R·T₁)
with R = RR/MW = 287.1018669 J/kg·K reproduces the stated inlet density 1.22 kg/m³ to
**2.3×10⁻⁵ relative**, and the oblique-shock relations at **γ = 1.4** reproduce all
three downstream targets (Mach, T, ρ) to **better than 0.03 %** (§2.2). No other γ
does. γ is fixed at 1.4 as a declared modelling choice and Cp is set to realise it.

**Finding 2 — INTERNAL INCONSISTENCY: the velocity BC implies M₁ = 2.5018, but the
target table was computed at M₁ = 2.5 exactly.** With γ = 1.4, R = 287.1019 and
T₁ = 289 K, the stated inlet velocity 852.68 m/s gives
**M₁ = 852.68/340.82461 = 2.501814636762496**, not 2.5. The Test Case text hedges
("about 2.5"), but the *target table* fits M₁ = 2.5 **exactly** roughly three times
better than it fits 2.5018:

| basis | M₂ | dev vs 1.874 | T₂ | dev vs 382.0 | ρ₂ | dev vs 2.277 |
|---|---|---|---|---|---|---|
| **M₁ = 2.5 exactly** | 1.8735260 | −0.0253 % | 382.0461 | +0.0121 % | 2.277189 | +0.0083 % |
| **M₁ = 2.5018 (velocity BC)** | 1.8749770 | +0.0521 % | 382.1101 | +0.0288 % | 2.277884 | +0.0388 % |

So the manual computed its targets at a round M₁ = 2.5 while stating a velocity BC
that gives 2.5018. **This case honours the stated velocity BC** (it is the
unambiguous boundary condition), so the solver sees M₁ = 2.5018 and its exact answer
is the second row. The **0.0521 %** gap between the as-modelled exact Mach and the
printed target is a deterministic term budgeted in §3.3, not noise.

**Finding 3 — UNDER-SPECIFIED GEOMETRY.** The manual gives the ramp angle (15°), the
ramp length (0.4572 m) and the sample point (0.38, 0.14) but **not** the domain
extent, the inlet-to-corner distance, or the top height (its "Figure .45.1: Flow
Domain" is a figure, absent from the text sidecar). §4 reconstructs a domain that
places the sample point in the uniform post-shock region, keeps the frozen sampling
zone > 6 coarse cells clear of both the shock and the wall, and lets the shock leave
through the supersonic outlet without reflecting off the top. This is stated so a
`PASS` cannot later be read as confirming a geometry the manual never fixed.

## 2. THE GAS, THE REFERENCE VALUES, AND WHICH ONE THE GATE IS AGAINST

### 2.1 γ is FIXED at 1.4 (a declared choice — the manual gives no Cp), Cp derived to realise it

- **Universal gas constant**, OpenFOAM v2606's own, because that is what the solver
  will use: `RR = 1e3·N_A·k = 1e3·6.0221417930e+23·1.38065e-23 = 8314.47006650545`
  J/(kmol·K) — `N_A` from `fundamentalConstants.C:121`, `k` from `etc/controlDict:1125`,
  composition from `thermodynamicConstants.C:46`. Read off the installed tree.
- **Specific gas constant:** `R = RR/28.96 = 287.1018669373429` J/(kg·K).
- **γ = 1.4** (declared; justified by the inlet-data consistency of Finding 1).
- **Cp set to realise γ:** `Cp = γ·R/(γ−1) = 1.4·287.1018669373429/0.4 =
  1004.8565342807003` J/(kg·K), so the solver's γ = Cp/(Cp−R) = **1.4 exactly**.

This is the **inverse** of VMFL051's derivation (there Cp was given and γ derived);
here Cp is absent and is chosen to pin the γ the case implies. Stating the arithmetic
is how a reference avoids silently acquiring a bias.

### 2.2 The reference values, to full double precision (weak-shock root)

The oblique-shock solution is the closed form of the reference (White 1994, 560–567):
solve the theta–beta–M relation for the **weak** shock angle β, take the shock-normal
Mach M₁ₙ = M₁·sin β, apply the normal-shock jump relations to M₁ₙ, and rotate back with
M₂ = M₂ₙ/sin(β−θ). The **weak root is selected** by bracketing β between the Mach angle
μ = asin(1/M₁) and the β at which the deflection is maximum (detachment); it is the
attached-shock, **supersonic-downstream** root. **How the weak root was determined for
THIS case:** the solved M₂ = 1.875 > 1 (supersonic) is the weak-root signature — the
strong root would give a subsonic M₂ — and 15° is far below the detachment deflection
θ_max = 29.82° at this M₁, so an attached weak shock exists. The comparator asserts
M₂ > 1 and refuses if the strong root was returned.

| symbol | value | what it is |
|---|---|---|
| **R_MANUAL_MACH** | **1.874** | **the manual's printed target Mach, Tables .45.1/.45.2. THE GATE IS AGAINST THIS.** |
| R_MANUAL_T | 382.0 K | the manual's printed target temperature (declared diagnostic) |
| R_MANUAL_RHO | 2.277 kg/m³ | the manual's printed target density (declared diagnostic) |
| M₁ (as modelled) | 2.501814636762496 | = U₁/√(γR T₁), from the velocity BC 852.68 m/s |
| β (weak) | 36.92317760072534° | detachment θ_max = 29.816737657279° |
| M₁ₙ = M₁ sin β | 1.5029493040042183 | shock-normal upstream Mach |
| **M₂_EXACT** | **1.8749769576810524** | **as-modelled exact post-shock Mach. The exact-value diagnostic (§3.2) is against this.** |
| T₂_EXACT | 382.1100763833985 K | as-modelled exact post-shock temperature |
| ρ₂_EXACT | 2.2778835945694422 kg/m³ | as-modelled exact post-shock density |
| p₂_EXACT | 249894.17658562586 Pa | as-modelled exact post-shock pressure |
| M₂ at M₁ = 2.5 exactly | 1.8735260067502537 | the value the manual's printed target was computed from |

**Verification of the reference machinery against a published table** (`--selftest`,
zero compute): the in-module weak-β at γ = 1.4 reproduces NACA Report 1135 to 0.02° —
β(M=2, θ=10°) = 39.31393° vs 39.314, β(M=2, θ=20°) = 53.42294° vs 53.423, β(M=3,
θ=20°) = 37.76363° vs 37.764 — and the normal-shock relations at M = 2 give exactly
ρ₂/ρ₁ = 8/3, p₂/p₁ = 4.5, T₂/T₁ = 1.6875, M₂ = 1/√3.

### 2.3 Which reference the gate is against, and why

**THE GATE IS AGAINST THE MANUAL'S PRINTED TARGET MACH, 1.874.**
`ANSYS_VERIFICATION_CHARTER.md` §5.1 requires the gate to be *"the reference result as
the manual states it"*; the manual states the target as its own analytic answer.
Gating against the lab's own recomputed value would let the lab choose its reference.

**M₂_EXACT = 1.8749769576810524 is registered as a tighter DIAGNOSTIC (§3.2), printed
beside the gate and never able to overturn it.** It is the exact answer for the
inlet actually modelled, so it is the honest yardstick for the solver's own
discretisation error once the manual's M₁-rounding is set aside.

**Ansys's own numbers (Fluent 1.902/377.6/2.233; CFX 1.871/382.8/2.278) are CONTEXT
ONLY** — held in the comparator as `ANSYS_CONTEXT`, printed in the report, never a
gate, never a band, never a reference.

## 3. THE GATE AND ITS TOLERANCE, WITH THE DERIVATION

### 3.1 The gate

> **G-VMFL045:** at the finest level **L3_360x304**,
> **|M_lab − 1.874| / 1.874 ≤ 0.010 (1.0 %)**.
> Inside ⇒ gate met; outside ⇒ **`GATE FAIL`**.

`M_lab` is the volume-average of the `Ma` field over the frozen cell zone `gateZone`
at `endTime`, read from the `gateMach` `volFieldValue` function object (§5).

### 3.2 The exact-solution and target diagnostics — NOT the gate

- **Exact Mach:** against **M₂_EXACT = 1.8749769576810524**, band **0.5 %**, printed
  beside the gate. A row that meets the 1 % gate but misses the 0.5 % exact diagnostic
  is a **`PASS`** with the diagnostic printed beside it (the VMFL005/VMFL051 posture).
- **Temperature:** |T_lab − 382.0|/382.0 ≤ **1 %**, and printed against T₂_EXACT.
- **Density:** |ρ_lab − 2.277|/2.277 ≤ **1 %**, and printed against ρ₂_EXACT.

The T and ρ diagnostics guard against a wrong post-shock **state** that happens to
land the Mach right; they can never turn a gate PASS/FAIL into anything (they are
printed, not gated).

### 3.3 WHERE 1.0 % COMES FROM — the derivation, not a round number

Three independent requirements, each computed here before any solver runs.

**(i) It must CONTAIN the declared systematic terms, or the gate is unfair:**

| term | size | why the lab carries it |
|---|---|---|
| **inlet-Mach term** | **0.0521 %** | the target was computed at M₁ = 2.5 (Finding 2); the faithfully-modelled velocity BC gives M₁ = 2.5018, whose exact M₂ = 1.874977 sits 0.0521 % above the printed 1.874 |
| **target-print rounding** | **0.0267 %** | the target 1.874 is printed to 4 s.f.; half-width ±0.0005 = ±0.0267 % |
| **sum** | **0.079 %** | |

So the band must exceed **0.079 %**. A band tighter than about 0.1 % would be gating
the manual's own printing and M₁-rounding rather than the lab's solver.

**(ii) It must be a BAR — capable of failing a plausible-but-wrong treatment:**

| wrong treatment | value | 1 % gate |
|---|---|---|
| **no shock / freestream sampling** (M unchanged at 2.5018) — the failure the frozen §5 zone exists to prevent | 2.5018 | **FAILS by 33.5×** (+33.50 %) |
| **strong-shock root** instead of weak | subsonic M₂ | **FAILS** massively |
| **an under-resolved, first-order-behaving shock** — the realistic numerical failure here | O(1 %) undershoot | **at or over the boundary — this is what the bar is for** |
| **Ansys Fluent's own reported value** (1.902) | 1.902 | **FAILS** (+1.49 %) — see the declared note below |

**Declared: this 1 % gate FAILS Ansys Fluent's own reported Mach (1.902, +1.49 %) and
PASSES Ansys CFX's (1.871, −0.16 %).** This is stated before any compute. Fluent's
value is a **point** reading at (0.38, 0.14); a point near a smeared shock foot is
biased toward the freestream, which is exactly the error the frozen §5 **volume
average over a zone inset > 6 coarse cells from the shock** is designed to remove. The
gate is therefore a genuine bar: a lab result no better than Fluent's point sample
would fail it, while a conservative shock-capturing scheme sampling the uniform
post-shock zone is expected to clear it comfortably (see the order discussion in §6).
**If the supervisor judges that failing the manual's own reference solver is too
aggressive for a first shock case, the band may be loosened to 1.5 % at the freeze —
that is a supervisor call, made before commit; this lane's justified recommendation is
1.0 %.**

**(iii) It must be TIGHTER than the manual's own stated goal, because this target is
exact.** The manual's 3 % goal (§1.3, p. 5) covers cases whose targets are
experimental or benchmark computations. VMFL045's target is closed-form analytic, so
the lab holds itself to **1.0 % = the manual's goal ÷ 3**. This is looser than
VMFL051's 0.5 % **deliberately**: VMFL051 is a smooth expansion; VMFL045 contains a
discontinuity, and a shock-capturing scheme carries a first-order shock-position error
that pollutes the downstream field (§6). Setting VMFL051's 0.5 % here would be gating
against an accuracy the physics of shock capturing does not promise.

**The band sits between (i) and (ii):** an order of magnitude above the 0.079 %
bookkeeping floor, and at the boundary of the O(1 %) numerical failure mode it must
catch. Both arms of the gate — the exact value passes, a 1.5 %-off value fails, the
freestream treatment fails, Fluent fails, CFX passes — are exercised by `--selftest`
with zero compute.

## 4. Geometry, mesh levels, and the physical endTime

### 4.1 Geometry (frozen, `case/system/blockMeshDict.template`; reconstructed — Finding 3)

Two-dimensional, one cell thick in z (`empty`), z ∈ [−0.01, +0.01] m. A single
trapezoidal block whose entire bottom edge is the ramp:

- ramp apex (compression corner) at the **origin**; the wall is y = x·tan 15°,
  tan 15° = 0.2679491924311227; at the outlet x = 0.6, y = 0.16076951545867362
- inlet plane **x = 0** (height 0 → 0.5); outlet plane **x = +0.6 m**; top **y = +0.5 m**
- the sample point (0.38, 0.14) lies between the wall (y = 0.1018 at x = 0.38) and the
  shock (y = 0.2855 at x = 0.38) — i.e. in the uniform post-shock region

**Why the top is at 0.5 and the outlet at 0.6 — no wave is reflected, by
construction.** The shock leaves the corner at β = 36.923°; at the outlet x = 0.6 it
stands at y = 0.6·tan β = 0.45087 < 0.5, so the **entire shock leaves through the
supersonic (zeroGradient) OUTLET** and would reach the top only at x = 0.5/tan β =
0.6654 > 0.6. The top boundary sees undisturbed M = 2.5018 freestream along its whole
length and cannot reflect anything, because nothing arrives at it.

### 4.2 Mesh levels — refinement ratio 2 BY CONSTRUCTION

| level | nx × ny | cells | h_x (m) |
|---|---|---|---|
| `L1_90x76` | 90 × 76 | **6,840** | 0.006667 |
| `L2_180x152` | 180 × 152 | **27,360** | 0.003333 |
| `L3_360x304` | 360 × 304 | **109,440** | 0.001667 |

Every level **doubles both counts**, so **h halves exactly and r = 2 by
construction** — never inferred from a cell count (`VERIFICATION_CHARTER.md` §3.1). The
block is sheared (its bottom edge follows the ramp), so cells stretch in y with x; the
§5 insets are sized against the coarse-level cell size. The finest level (109,440
cells) is comparable to VMFL051's proven 99,840.

### 4.3 endTime — the same PHYSICAL TIME at every level, and the plateau hazard

**endTime = 7.0e−3 s at all three levels**, so the Roache triple compares the same
physical state. That is **8.6 flow-throughs** of the 0.6 m domain at the **slowest**
speed anywhere in it — the post-shock stream U₂ = 734.81 m/s (the inlet stream is
faster at 852.68, so this count is the conservative one). **This is more than double
VMFL051's 4 flow-throughs**, and is the primary mitigation of the hazard set out in
§7. It is an **estimate, fixed before any run**; the plateau clause of §6/§8 is the
actual arbiter. `deltaT 1e−8` is only a seed; `adjustTimeStep` raises it to the CFL
limit (maxCo 0.4), and `maxDeltaT 1e−5` is above the L1 CFL step (~2.9e−6 s) so it
never binds.

## 5. THE FROZEN SAMPLING RULE — where the answer is read, fixed before any answer exists

Frozen in `case/system/topoSetDict` in **absolute physical coordinates, identical at
every mesh level**. The uniform post-shock region is the wedge between the ramp wall
(y = x·tan 15°) and the shock (y = x·tan β, tan β = 0.7514539998584236); between those
rays the exact solution is **exactly uniform at M₂** (flow parallel to the ramp), so
any volume weighting returns M₂ exactly.

**x window: [0.34, 0.46] m.** It contains the sample point (0.38, 0.14), stops 0.14 m
short of the outlet (so outflow cells are excluded), and starts 0.34 m from the corner
(clear of the shock-formation near-field).

**INSETS DERIVED PER BOUNDARY at the WORST x, so the box is strictly inside the wedge
for every x in the window** — the wall rises with x so its inset is taken at x = 0.46,
the shock rises with x so its inset is taken at x = 0.34; δ = 0.030 m off both. At L1
the block cell dy ≈ 0.00517 m at mid-window, so 0.030 m ≈ 5.8 coarse cells: even at
the coarsest level the zone edge stands clear of the numerically smeared shock and of
the wall. At L3 the same 0.030 m is ≈ 23 fine cells.

> **`gateZone` (THE GATE):** x ∈ [0.34, 0.46], y ∈ [**0.15325662851831645**,
> **0.22549435995186401**], band height 0.072238 m, z ∈ [−1, 1].
>
> **`gateZoneInner` (DIAGNOSTIC ONLY):** x ∈ [0.34, 0.46], y ∈ [0.16825662851831645,
> 0.21049435995186401] (δ = 0.045 m). If the two averages disagree by more than
> **1e−2** at L3, the row is **`NOT A RESULT`** — a one-way clause (rule 5) that can
> never produce a PASS.

**The instrument.** `Ma` is the v2606 `MachNo` object (stored as `Ma`,
`mag(U)/sqrt(γ·p/ρ)`), placed **first** in `functions` so it is in the registry before
`gateMach` reads it. `gateMach` writes `volAverage(Ma, T, rho, p)` over `gateZone`
**every timestep**, so the plateau clause has a dense series. The reader is built
against the v2606 writer source (path `postProcessing/gateMach/0/volFieldValue.dat`;
`# Region`/`# Cells`/`# Volume` header; columns located **by header name, never by
position**), not a belief about it (N-AV4 / L-286). The `# Cells` line is a control:
the comparator **refuses (exit 2)** if it is absent or 0, and `run_vmfl045.sh` refuses
before the solver starts if `topoSet` left either zone empty.

## 6. THE VERDICT ORDER (CLAUDE.md rule 5), in its stated order — with Roache meanings

1. **any level not plateaued** — peak-to-peak of the `volAverage(Ma)` gate series over
   its **last 20 %** exceeding **1.0e−3 in Mach** (= 5.3e−4 relative, ~19× tighter
   than the gate, and by design far below the expected level-to-level difference) — or
   failing any completion clause of §8 ⇒ **`NOT A RESULT`**; **and** the inner-zone
   clause of §5 at L3 ⇒ **`NOT A RESULT`**;
2. **Roache triple** on the post-shock Mach number `DIVERGENT` / `STAGNANT` /
   `OSCILLATORY` / `EXACT` ⇒ **`NOT A RESULT`**, with the three values, R, the
   increments and the observed order printed beside it, and **no GCI quoted**;
3. **`CONVERGING`** ⇒ **`PASS`** inside the 1 % band else **`GATE FAIL`**, with **GCI
   at Fs = 1.25** printed and the Richardson extrapolation beside it.

Thresholds fixed in the comparator before any run: `EPS_ABS = 1e−12`, `STAG_TOL =
1e−3`, `RATIO = 2.0`, `FS = 1.25`. **The gate can only turn a `PASS`/`GATE FAIL` INTO
`NOT A RESULT`, never the reverse.**

**WHAT EACH ROACHE OUTCOME MEANS FOR THIS CASE — registered before the answer exists:**

- **CONVERGING with observed p ≈ 1:** the **expected** outcome. The scheme is
  converging at the first-order rate that shock capturing imposes; the GCI is
  meaningful and the gate applies. This is the normal, correct result for a captured
  shock, not a defect.
- **CONVERGING with p ≈ 2:** surprising but valid — it would mean the sampling zone is
  far enough from the shock that the smooth second-order behaviour of the interior
  dominates the residual shock-position error. Reported as measured; a genuine finding.
- **OSCILLATORY (R < 0):** the level-to-level Mach differences change sign. The likely
  causes here are (a) a coarse level not yet plateaued (VMFL051's exact failure mode),
  or (b) the captured shock **position** jumping between meshes so the fixed zone catches
  slightly different flow. ⇒ **`NOT A RESULT`**; §7's mitigations exist to prevent (a),
  and the inset of §5 to bound (b). If it still occurs it is diagnosed, not graded.
- **DIVERGENT (R > 1):** differences **grow** with refinement — the meshes are not in
  the asymptotic range, or shock–zone interaction worsens as the shock sharpens.
  ⇒ **`NOT A RESULT`**.
- **STAGNANT (R ≈ 1):** differences do not shrink under refinement — no extractable
  order. ⇒ **`NOT A RESULT`**.
- **EXACT (all three equal to 1e−12):** the zone average is mesh-independent. For a
  captured shock this would actually be *plausible* — a conservative scheme gives the
  exact Rankine–Hugoniot jump at any resolution — but rule 5 still classes it
  **`NOT A RESULT`** (no order can be formed from zero differences); the three equal
  values are printed and the interpretation noted, and the case would re-run with a
  wider refinement ratio as a new rung to obtain a gradable triple.

**EXPECTED OBSERVED ORDER, stated before it is measured (task requirement).** Because
this case contains a **shock**, the observed order is **expected to smear toward first
order, p ≈ 1** — a conservative shock-capturing scheme is only first-order near the
discontinuity whatever its nominal order, and the O(h) shock-position/strength error
pollutes the downstream field even where the flow is smooth. This is the **opposite**
of VMFL051's smooth expansion, where p ≈ 2 was expected. **A p ≈ 2 here would be
surprising and reported as a finding; a p ≈ 1 is the expected, physically-correct
outcome and is not grounds to move any band.** Stated now so the order cannot be
rationalised after the fact.

## 7. THE KNOWN HAZARD: how VMFL045 avoids VMFL051's plateau failure

**VMFL051 came back `NOT A RESULT`:** its grid triple was OSCILLATORY (R = −1.3486)
and its two coarser levels had not reached a steady plateau at endTime (peak-to-peak
6.2e−3 and 3.5e−3 against a 1.0e−3 tolerance) while only the finest had. The diagnosis
was that the coarse levels' residual unsteadiness was the **same order** as the
level-to-level differences, so the triple measured transient noise rather than
discretisation error. **VMFL045 addresses this on the face of the pre-registration,
before compute, in four ways:**

1. **A longer endTime.** 7.0e−3 s here is **8.6 flow-throughs** at the slowest speed,
   vs VMFL051's 4 — because the domain is shorter (0.6 m vs 1.5 m) at the same
   wall-clock endTime. The flow is everywhere supersonic and the shock is **attached
   and unconditionally stable** (deflection 15° ≪ detachment 29.82°), so there is no
   physical unsteadiness: the startup transient simply convects out through the
   supersonic outlet, and its residual decays as it does so. Doubling the
   flow-throughs is expected to cut a convecting transient's residual by more than an
   order of magnitude — from VMFL051's ~6e−3 to well below the 1e−3 plateau tolerance.

2. **A plateau criterion checked PER LEVEL before the triple is formed** (§6 step 1).
   This is rule 5 step 1, but the point VMFL051 taught is that the *endTime* must be
   long enough for the coarse levels to reach it; (1) supplies that. A level that
   still fails plateau at endTime is **`NOT A RESULT`** and re-runs at a longer
   endTime as a **NEW rung** — never re-graded in place (the VMFL001 R1→R2 protocol).

3. **The plateau tolerance is deliberately far below the expected discretisation
   signal.** 1.0e−3 in Mach (5.3e−4 relative) is ~19× tighter than the 1 % gate and,
   for a first-order shock case whose coarse–medium difference is expected to be
   O(0.5–1 %) of M₂ ≈ 0.01–0.02 in Mach, is **10–20× smaller than the level-to-level
   difference** — exactly the separation VMFL051's failure showed to be necessary, so
   the triple measures discretisation error and not plateau noise.

4. **The gate is a VOLUME AVERAGE, not a point probe.** Averaging over ~250 (L1) to
   ~4000 (L3) cells suppresses the single-cell jitter that a point probe at (0.38,
   0.14) would inherit — and is also why Fluent's point value (§3.3) is not the yardstick.

**A steady solver was considered and declined.** The case is genuinely steady, so
`rhoSimpleFoam` was an option; it was declined because pressure-based SIMPLE is less
robust for a strong supersonic shock than the density-based, shock-capturing
`rhoCentralFoam` the team has proven on this box (F3, VMFL051). The transient solver
run to a generous endTime with the plateau clause as arbiter is the more defensible
route to a steady state for a shock case.

## 8. Strict completion (CLAUDE.md rule 4), with TWO DEPARTURES DECLARED ON THE FACE

The comparator refuses (exit 2) on any failed clause and **never grades a partial
run**. The departures are identical in kind to VMFL051's (same solver, same reasons),
restated here rather than inherited silently.

| clause | as checked here |
|---|---|
| **C1** `rc = 0` | `RUN_RC.txt`, written by the launcher, reads `rc=0` |
| **C2** an `End` line | `^End$` present in `log.rhoCentralFoam` |
| **C3** last time == `endTime` | **DEPARTURE 1** |
| **C4** fields present at endTime | **`T U p rho Ma`** — this case's own declared list |
| **C5** `ExecutionTime` count == `endTime` | **DEPARTURE 2** |
| **C6** age guard | **STRICTER than the rule** |

**DEPARTURE 1 (C3).** `rhoCentralFoam` runs `adjustTimeStep yes`, so the rule's
literal equality is wrong for an adaptive-step solver. It is replaced by **|t_last −
endTime| ≤ maxDeltaT (1e−5 s against an endTime of 7e−3 s)** *and* the log's own final
`Time =` agreeing with the last time directory to 1e−12 relative. **Tighter or equal,
never looser.**

**DEPARTURE 2 (C5).** The rule's literal clause is a **steady-iteration** clause (one
iteration = one time unit). This solver is transient with an adaptive step, so its
step count is not `endTime`. The invariant the clause protects — *the log is not
truncated mid-step* — is checked **directly**: `count(^ExecutionTime = ) == count(^Time
= )`, and > 0.

**C6 is STRICTER than the rule.** The rule dates the run from `0/T`; this dates it from
the **latest mtime anywhere in the case's own `0/`**, and `run_vmfl045.sh` touches
**every file in `0/`** as the last action before the solver launches. Every field at
endTime must be **strictly newer** than that datum.

**The launcher enforces the rule's own guards**: `run_vmfl045.sh` **refuses to start
into any pre-existing level directory**, refuses unless this pre-registration is
**committed at HEAD**, refuses if `topoSet` left either sampling zone empty, and
enforces the cap with `timeout` (§9).

## 9. Cost (CLAUDE.md rule 12, and L-291's four numbers)

### 9.1 Executed compute

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × 1 / 60 |
| **basis** | the cfd/VMFL051 **measured** `rhoCentralFoam` throughput on this box, **7.24e−7 s per cell-step** (the conservative of the F3 figures). A measurement of the *solver on this hardware*, borrowed as setup knowledge; **no F3/VMFL051 gate, band or reference is borrowed.** |
| step counts | dt = 0.4·h_x/(U₂+a₂) with U₂+a₂ = 1126.7 m/s ⇒ L1 ~2,958 steps; doubling the mesh halves dt, so ~5,915 and ~11,830 at L2, L3 |
| solver estimate | L1 6,840×2,958 → **15 s**; L2 8× → **117 s**; L3 8× → **937 s**; subtotal **~1,069 s** |
| + `blockMesh`+`checkMesh`+`topoSet`, three levels, and function-object overhead (~10 %) | ~**150 s** (estimates) |
| **POINT ESTIMATE** | **~1,220 s = 20.4 core-minutes** |
| **CEILING (the enforced cap)** | **48 core-minutes** = 2.35 × the point estimate, enforced by `timeout` inside `run_vmfl045.sh`; **an overrun STOPS the run and it does not get a new budget** |
| authorised for this case | requested **50 core-minutes** from the supervisor; the cap is set **under** it, and the authorisation is a per-item cost, **not a new ceiling** (rule 9) |
| dollars at the point estimate | **$0.01745** (DERIVED) |
| dollars at the ceiling | **$0.04104** (DERIVED) |
| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). The per-cell-step rate is a **measurement**; the step counts, meshing time and FO margin are **ESTIMATES**. |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; a blanket is not a per-item read (rule 9) |

**The cap-as-timeout instrument trap (measured by the team):** a wall-clock `timeout`
equals a core-minute cap **only for a serial run**; for a parallel run the timeout must
be `cap_core_min·60/ranks`. This run is serial (ranks = 1), so timeout_s =
cap_core_min·60. The launcher writes that formula in its header so a future parallel
variant cannot get it wrong. No single level's wall time (max ~937 s at L3) approaches
the 3600 s stall threshold.

### 9.2 Lane wall, priced separately (L-291)

| component | point estimate | ceiling |
|---|---|---|
| **this drafting lane** (read the manual; the precedent's four files; derive the oblique-shock reference and cross-check it against NACA 1135; build the case tree; write and selftest the comparator; write and commit this freeze) | **40 lane-minutes** | **65 lane-minutes** |
| **the later run-and-grade lane** (launch, monitor, grade, draft `RESULTS.md`, the register row and the calibration row) | **20 lane-minutes** | **40 lane-minutes** |

### 9.3 Calibration at completion

At completion the team compares **each component against its own pair**: actual
core-minutes from `RUN_RC.txt`/`COST.txt` against the 20.4 point estimate, and actual
lane wall against the figures above; ratio, attribution (contention, waste,
misprediction — waste named separately, never absorbed); dollars derived at
$0.0513/core-h and labelled **derived, not measured**; **one row appended to
`docs/COST_CALIBRATION.md`** under its append rules and the rule-10 private-index
protocol. **A completion report without that row is incomplete** (rule 12).

## 10. The grading path, frozen (VERIFICATION_CHARTER §2d)

The comparator, the run script and the whole case tree were committed **BEFORE this
file**, at commit **`2198f9b219b5e14dcedce41239bc258b26174197`** ("VMFL045 case inputs and comparator — NO
COMPUTE HAS RUN, pre-registration not yet frozen"), which precedes any solver. At
analysis time the grading path is re-hashed against these blob shas; a freeze that is
claimed and not checked is a claim about intent.

| what | path under `cases/ansys_verification/VMFL045/` | committed blob sha |
|---|---|---|
| **comparator (THE GRADING PATH)** | `grade_vmfl045.py` | **`0c83eeef1199e1376d7ef400d9e4fb5f3d30e526`** |
| run script | `run_vmfl045.sh` | `db3932616f6643180276b64e5cd7f360b0ba8a9f` |
| **the frozen sampling rule** | `case/system/topoSetDict` | **`ffaeb57898a4db6b6b7465597aaa2bfaa6c0fb0b`** |
| blockMeshDict template | `case/system/blockMeshDict.template` | `62e9487528ac13754744c6c771fcf0ee1d97fb95` |
| controlDict template | `case/system/controlDict.template` | `eed90645a07db50b1bbb99d00943a4a6c8894678` |
| fvSchemes | `case/system/fvSchemes` | `bd0dc8a3a9b823f535905cf403c85f9070e0c4d7` |
| fvSolution | `case/system/fvSolution` | `1e3fb953c7fabb6a9e34ecb52e58286756ebd07a` |
| `0/U` (velocity BC + age-guard datum) | `case/0/U` | `c3210a4519dea115eef2113a9a2cf083321f9a1c` |
| `0/T` | `case/0/T` | `33477f30093395061f57e772c1ffffa0ca6c710b` |
| `0/p` | `case/0/p` | `f8d6a12f6a2c830ff679b468868d5afd472d0e2d` |
| thermophysicalProperties (γ = 1.4 via derived Cp) | `case/constant/thermophysicalProperties` | `f13a67413acd0cd9d17780e965eafabc0249fb82` |
| turbulenceProperties | `case/constant/turbulenceProperties` | `daf86371d952b61b05e7703bc7e20694318076e1` |

**Verified at grade time, not merely recorded.** `grade_vmfl045.py --verify-frozen
<commit>` reads its own bytes and refuses (exit 2) unless byte-identical to the
committed blob. **No threshold, band, reference value or plant constant in the
comparator is settable from the command line**; every one is a module-level constant
fixed by commit `2198f9b219b5e14dcedce41239bc258b26174197`.

**Run outputs go to `verification/runs/ansys_verification/VMFL045/<level>/`**, never
beside this prose (`FILING_CHARTER.md` R6). **The grading JSON is
`verification/runs/ansys_verification/VMFL045/GRADING_VMFL045.json`.**

## 11. What CANNOT be verified before the freeze — stated plainly

**No VMFL045 solver has run, and no mesh exists.** What *has* fired, with **zero solver
compute**: the comparator's `--selftest`, **45 checks, 0 failures** — the gas (γ = 1.4
via derived Cp); M₁ from the velocity BC; the oblique-shock solver against NACA 1135 at
three (M, θ) pairs and the normal-shock relations at M = 2; every frozen reference
literal and the weak-root signature; the reader on the real `volFieldValue.dat` format
including its two refusal arms; both arms of all three planted-zero controls on
fixtures in the real formats; all six Roache states; and both arms of the gate
including the freestream treatment, Fluent's own value (fails) and CFX's (passes).

Five things this lab has **not** seen, each needing separate supervisor authorisation —
**even `blockMesh` alone is not covered by this freeze**:

1. **That the mesh builds** — no `blockMesh` has run, so no `checkMesh` summary can be
   quoted; the declaration is the strong one: the mesh did not exist when the gate was
   frozen.
2. **That `topoSet` puts cells into both frozen zones** — the box coordinates are
   derived arithmetic (§5), not a measurement; if either zone comes out empty the run
   script refuses before the solver starts.
3. **The live `volFieldValue.dat` and `Ma` field on disk** — readers are built from
   the v2606 writer source, but no run has produced either file. The cheap decisive
   check after the first coarse level is `grade_vmfl045.py --dryrun-reader …`, which
   prints structure only and **never a value** (the L-286 check).
4. **That every level plateaus within 7.0e−3 s** (§4.3/§7 is an estimate). If a level
   does not, the comparator returns `NOT A RESULT` and that level re-runs at a longer
   endTime as a **new rung** — no gate, threshold, cap or label moves.
5. **The observed order and the shock position.** §6 states the *expectation* (p ≈ 1);
   the measured order is a finding, whatever it is.

## 12. Verdict vocabulary, and what this rung will NOT claim

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (CLAUDE.md rule 1). `PENDING` here means **not yet run** and is never used
to soften a `GATE FAIL`.

- **Nothing about Ansys.** Fluent's 1.902 and CFX's 1.871 are context (§1), never the
  gate; this box has no Fluent and no CFX and neither archive was opened.
- **Nothing about the manual's correctness beyond §1a.** The three findings are drafted
  for the lessons/numerics files and stamped `NOT FILED`; they are not verdicts.
- **Nothing about a γ the case does not fix.** γ = 1.4 is a declared modelling choice
  forced by the absence of a Cp (Finding 1); a `PASS` is not evidence the manual
  intended any particular γ.
- **Nothing about the domain the manual left open** (Finding 3). A `PASS` is a
  statement about the post-shock state, not about a geometry the manual never fixed.

The verdict is a statement about this lab's `rhoCentralFoam` against the manual's
oblique-shock reference, and **only a `PASS` is a credential**; a `GATE FAIL` is a
finding that is never removed, never re-labelled and never softened.
