# VMFL051-R3 — Isentropic Expansion of Supersonic Flow Over a Convex Corner: PRE-REGISTRATION (DRAFT — UNFROZEN)

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**THIS FILE IS A DRAFT AND IS NOT FROZEN.** It carries no freeze commit and no
committed-blob shas for its grading path, because the comparator
(`grade_vmfl051_r3.py`) and the two changed sampling dictionaries are **not yet
built or committed**. The `ansys-verification-supervisor` freezes; this lane drafts.
Nothing here authorises a run. **NO GRADED SOLVER EXECUTION HAS OCCURRED**, and none
may until the supervisor freezes this file by sha and personally verifies the
comparator as a diff (CLAUDE.md rule 2; `SUPERVISION_CHARTER.md` §3 check 4). **No
agent message is Sanaa's consent** (CLAUDE.md rule 9).

**The condition, CHECKED and not asserted** (`VERIFICATION_CHARTER.md` §2b.1): at
**2026-09-10T05:23:33Z**, read with `date -u` in the same shell invocation,
**`verification/runs/ansys_verification/VMFL051-R3/` does not exist** (`ls -d`
returned *No such file or directory*) and **`cases/ansys_verification/VMFL051-R3/`
contained no case tree** — only this draft. No `blockMesh`, `topoSet` or
`rhoCentralFoam` has run into any R3 run root; no R3 mesh exists.

**Drafted 2026-09-10 by `ansys-lane-opus48` (Opus 4.8) for the `ansys-verification`
team**, under `ANSYS_VERIFICATION_CHARTER.md` §5, §6, §11.1, §12.2 and
`VERIFICATION_CHARTER.md` §2, §2b, §2d. This is the **successor to VMFL051-R2**
(register **Row #73**, `NOT A RESULT`), itself the successor to VMFL051 run 1
(register #4, `NOT A RESULT`). It is a **re-run under one changed lever**, not a
fresh case. `RESULTS.md` is written afterwards and does not revise this file;
departures land as dated addenda at the foot, never by editing above (CLAUDE.md
rule 6).

---

## 0. What this successor is, and the ONE thing it changes

**VMFL051: Isentropic Expansion of Supersonic Flow Over a Convex Corner** — Ansys
Fluid Dynamics Verification Manual, Release 2026 R1, **pp. 165–166** (sidecar lines
4268–4335; title page verified against the PDF per CLAUDE.md rule 15: PDF p. 1 and
the `.txt` sidecar both read *"Ansys Fluid Dynamics Verification Manual … Release
2026 R1"*, and the VMFL051 header, reference, properties and Table .51.1 were read
directly from the sidecar this session). Inviscid, compressible, ideal-gas
supersonic flow (M₁ = 2.5) turns around a convex corner (interior angle 195° ⇒ a 15°
turn) through a **centred Prandtl–Meyer expansion fan**. The manual's Target
post-expansion Mach number is **3.2370** (Table .51.1).

**The chain of findings this successor inherits.** Run 1 (`NOT A RESULT`): snapshot
triple `OSCILLATORY`, and two of three levels failed the snapshot-plateau clause.
**R2 (Row #73, `NOT A RESULT`)** changed one lever — snapshot → **time-mean** — and
that lever *worked for what it targeted*: per-level settledness (window-length
insensitivity) is now **7.4e-5 / 8.1e-6 / 6.4e-6** against `TOL_STAT` = 5.0e-4, so
the **temporal** axis is fixed. But the **spatial** non-monotonicity survived: the
Roache triple on the three time-means **3.2285395408 / 3.2236362823 / 3.2294426470**
(L1/L2/L3) is `OSCILLATORY`, **R = −1.1841848972** (d21 = −5.8064e-3, d32 =
+4.9033e-3 — the increment changes sign), so `NOT A RESULT` whatever the value
(CLAUDE.md rule 5). All three levels already land within the ±0.5 % band on value —
**−0.261 % / −0.413 % / −0.234 %** from 3.2370 (per the supervisor's reading,
≈−0.263 / −0.414 / −0.234 %). **The physics is reproduced; only the triple stands
between this case and a verdict.** (All R2 figures cited from
`verification/runs/ansys_verification/VMFL051-R2/GRADING_VMFL051_R2.json` and
`COST.txt`.)

**THE ONE LEVER THIS SUCCESSOR CHANGES — the SPATIAL reduction.** Replace R2's
unweighted **`volAverage(Ma)` over a volume zone** with a **mass-flux-weighted
(conservative) reduction on a downstream cross-plane inside the uniform
post-expansion wedge, clear of the fan**, from which **one self-consistent Mach** is
derived through the isentropic relation. R2 fixed the *temporal* axis; **R3 fixes
the *spatial* axis, which is where the surviving non-monotonicity lives.** The
**temporal reduction of R2 is KEPT unchanged** and stacks on top: the graded
observable is the **time-mean, over the same settled window, of the flux-weighted
cross-plane Mach**.

**Everything the SOLVE consists of is IDENTICAL to run 1 / R2** — the same solver
(`rhoCentralFoam`), the same Kurganov–Tadmor flux + vanLeer reconstruction, the same
three-level r = 2 mesh family, the **same `endTime` 7.0e-3 s**, the same grid family,
the same `0/` fields, thermophysical and turbulence dictionaries. **The gate does
not move** (reference 3.2370, band ±0.5 % relative at the finest converged level;
L-487: match the reduction, do not widen a gate; a successor does not touch the
gate). The only changed inputs are the two **sampling** dictionaries (a new
cross-plane face zone and its per-timestep flux-weighted function object) and the
**comparator**. §2 lists exactly which solve blobs stay byte-identical and which
sampling blobs change.

**Why this lever, and why it is defensible.** A flux-weighted average of conserved
quantities is **constrained by the governing equations** and is far less sensitive
to weak dispersive waves than a pointwise-nonlinear volume average. It collapses the
current internal inconsistency: at L3, R2's Mach re-derived from ⟨p⟩ is **3.2346390**
while from ⟨T⟩ it is **3.2289239**, a **0.0057 spread that is the same order as the
grid signal itself** (|d32| = 4.9e-3). A single flux-weighted, isentropically-derived
Mach removes that spread from the functional.

**THE HONEST RISK, PRE-REGISTERED, NOT HIDDEN (per the supervisor's ruling).** The
evidence does **not** guarantee this converts the triple. R2's **strictly-inner
diagnostic zone is ALSO non-monotone** — inner-zone time-means **3.2262894 /
3.2223717 / 3.2302636** (L1/L2/L3), down then up, same signature as the gate zone.
That warns the corner-seeded entropy floor may be **irreducible by any spatial
re-reduction**. **§7 pre-registers that outcome explicitly as a legitimate result**:
if a flux-conservative reduction still gives a non-monotone triple, the finding is
that the **corner-entropy floor sits at the functional's own magnitude and this case
is not cleanly reachable with this solver** — a real result, not a disappointment.

**This is a statement about this lab's `rhoCentralFoam` against the manual's
analytic Prandtl–Meyer Target. It is NOT a statement about Ansys** — this box has no
Fluent and no CFX; the Fluent/CFX archives were not opened. The vendor solver
numbers (Fluent 3.2316, CFX 3.2354) are context, never the gate (§2, §3).

## 1. The manual, the gas, and the still-standing findings — carried from R2/run 1

The manual quotes, the derived gas (γ = 1.3990093734749485 from the manual's own
Cp = 1006.43 J/kg-K and MW = 28.966), the closed-form reference, and the **three
manual defects** (Defect 1: the "steady, inviscid, **and incompressible**"
contradiction, p. 165 — a supersonic M = 2.5 expansion is not incompressible;
Defect 2: 3.2370 is not the exact PM value at any consistent γ, carrying ≈0.005 %
table rounding; Defect 3: Table .51.2's mislabelled column, headed "Ansys Fluent"
over CFX data) are **carried verbatim from run 1's frozen `PREREGISTRATION.md` §1–§2
and §1a** and are **not re-derived here**. All three remain **`NOT FILED`**
(contacting Ansys is Sanaa's alone). None of the three changes model-sameness or the
reference kind (§3).

**Defect 1 re-confirmed at source this session (supervisor's ruling 1).** The
`ansys-verification-supervisor` independently read, on p. 165, that the manual's
**Analysis Assumptions** call the flow *"steady, inviscid, and **incompressible**"*
while the same page's **Physics/Models** line calls it *"Compressible, inviscid
flow"* — for a Mach 2.5 expansion. **A verification manual contradicting itself on
one page belongs in our record.** It changes nothing about the ceiling or the gate;
it is recorded here as a source-document defect, `NOT FILED`.

The gate is against the manual's printed Target **3.2370** (Table .51.1). The
closed-form exact Prandtl–Meyer value for the manual's gas,
**M₂_EXACT_GAS = 3.2355411372251863**, stays a **printed DIAGNOSTIC, never the
gate**, exactly as in R2 — printed beside the gate and never able to overturn it. The
comparator recomputes the Prandtl–Meyer reference by bracketed bisection and
**asserts it against the frozen literals** so a later edit cannot move it.

## 2. Byte-identical carry-over — quoted from R2's frozen file; the gate does not move

Quoted from `cases/ansys_verification/VMFL051-R2/PREREGISTRATION.md` (frozen):

- **Reference (gate): 3.2370** (Table .51.1). **UNCHANGED.**
- **Band: ±0.5 % relative** at the finest converged level. **UNCHANGED** (L-487).
- **Mesh family, r = 2, exact by construction:**

  | level | cells | h (m) |
  |---|---|---|
  | `L1_120x52` | 6,240 | 0.0125 |
  | `L2_240x104` | 24,960 | 0.00625 |
  | `L3_480x208` | 99,840 | 0.003125 |

- **`endTime` = 7.0e-3 s** at every level (4.049 flow-throughs at U₁ = 867.72872 m/s).
  **UNCHANGED.**
- **Solver `rhoCentralFoam`; flux Kurganov (KT); reconstruct vanLeer / vanLeerV.**
  **UNCHANGED.**
- **Temporal reduction: time-mean over the last `WINDOW_FRAC` = 0.50 of the settled
  window; settledness `TOL_STAT` = 5.0e-4 in Mach** (|mean(last 50 %) − mean(last
  25 %)| ≤ `TOL_STAT`, per level). **KEPT from R2, unchanged** — it stacks under the
  new spatial reduction (§5).

**THE GATE DOES NOT MOVE.** Reference 3.2370, band ±0.5 % relative. L-487: a
successor matches the reduction and does not widen or move the gate.

**Which SOLVE inputs stay byte-identical to run 1 / R2, and which SAMPLING inputs
change.** The freeze must verify each of these blobs at the R3 freeze commit; the
"UNCHANGED" rows must hash **equal** to R2's committed blobs (§10 of R2), and the two
"CHANGED" rows must be the new R3 files:

| case input | status vs R2 | why |
|---|---|---|
| `blockMeshDict.template` | **UNCHANGED (byte-identical)** | same grid family; the cross-plane lives inside the existing mesh |
| `fvSchemes`, `fvSolution` | **UNCHANGED** | same KT + vanLeer solver being verified |
| `0/U`, `0/T`, `0/p` | **UNCHANGED** | same initial/boundary state |
| `thermophysicalProperties` | **UNCHANGED** | μ = 0 inviscid, perfectGas, hConst, Pr = 1 |
| `turbulenceProperties` | **UNCHANGED** | `simulationType laminar` |
| `system/topoSetDict` | **CHANGED** | adds the two answer-blind cross-plane `faceZone`s — `postExpPlane` (gate, §3.2) and `postExpPlane2` (diagnostic, §3.4) |
| `system/controlDict.template` | **CHANGED** | adds the per-timestep flux-weighted `surfaceFieldValue` FOs on both cross-planes; the temporal window write cadence is unchanged |
| `grade_vmfl051_r3.py` (comparator) | **NEW** | the changed spatial reduction and its planted controls (§5, §7) |

## 3. THE NEW REDUCTION — exact, answer-blind, buildable without a grading-time judgement

### 3.1 The continuum model, the reference model, and model-sameness (§12.2) — the ceiling derivation

**The solver's continuum model, named as equations.** With μ = 0 (verified in
`thermophysicalProperties`: `transport const`, `mu 0`, `Pr 1`; `turbulenceProperties`:
`laminar`; `equationOfState perfectGas`, `thermo hConst`), `rhoCentralFoam`
discretises the **2-D unsteady compressible Euler equations** for an ideal gas —
conservation of mass, momentum and total energy with **zero viscous and zero
conductive flux**, closed by the perfect-gas equation of state. At steady state the
solution is the **steady 2-D compressible Euler** field.

**The model the manual's reference is the exact solution of.** The manual's Target
3.2370 is the **centred Prandtl–Meyer expansion-fan** value (reference: **John
Anderson, *Modern Compressible Flow: With Historical Perspective*, McGraw-Hill,
2002**; the manual states, p. 165, *"Analytic expressions for isentropic expansion
can be used to calculate the Mach number downstream of the corner"*). The centred
Prandtl–Meyer expansion fan is the **exact, self-similar, isentropic, irrotational
solution of the 2-D steady compressible Euler equations** for supersonic flow
turning around a convex corner. It is **not** a quasi-1-D reduction: the
Prandtl–Meyer function ν(M) is derived directly from the 2-D steady Euler system by
the method of characteristics.

**Answer to §12.2 question (3): `SAME`.** Both objects are the **2-D compressible
Euler equations**. This is expressly distinct from the capped example in
`VERIFICATION_CHARTER §2h.8.2` — *"a closed-form isentropic **nozzle** relation …
solves quasi-1-D isentropic flow; the solver discretises 2D/3D"* — because a
Prandtl–Meyer fan is a genuine **2-D exact Euler solution**, not a quasi-1-D
relation. The residual between the graded field and the reference is therefore
**discretisation error by construction**, which a Roache triple bounds; **model-form
error is zero by construction.**

**The reference kind, and §33.2 (circularity / independence).** 3.2370 is the
manual's **analytic Target** (Anderson, isentropic algebra). Table .51.1 lists it in
a column **separate** from the "Ansys Fluent" solver column (3.2316, ratio 0.9980),
and Table .51.2 from "Ansys CFX" (3.2354, ratio 0.9995). **3.2370 is NOT a vendor
solver number**; it is independent of the code under comparison and of its vendor.
Under `VERIFICATION_CHARTER §33.2` (RULED: the cap turns on **independence** of the
reference, not on whether it is numerical), an **independent analytical reference is
`PASS`-capable** and the circularity cap does **not** apply.

**THE TWO-TABLE ARGUMENT (supervisor's, and decisive).** The **same Target 3.237** is
the yardstick in **both** Table .51.1 (against Fluent) **and** Table .51.2 (against
CFX). A vendor-solver number cannot be a target shared across two *different* vendor
solvers — if 3.2370 were a solver result it would be one code's number and could not
also be the yardstick for the other. **A Target common to both codes is only
consistent with an external, analytic reference.** This is the clean contrast with
**VMFL035**, whose text explicitly compared the pressure-based run to *"the steady
state solution from the density-based solver"* — there the Target **was** a vendor
number and §33.2 bit; here it is not.

**THE CEILING — RATIFIED BY THE SUPERVISOR, NOT A LANE DERIVATION, AND EXPLICITLY
AGAINST THE PRIOR LANE'S BLANKET.** A prior reading held *"the ANSYS team ceiling is
GATE REACHED"* as a blanket. **That is wrong as a blanket** and is not applied here:
the chief's standing relay of Sanaa's ruling is that **`GATE REACHED` is her
EXPECTATION, not a cap — each case is graded on what it actually holds.** The
`ansys-verification-supervisor` **verified this at source in the manual body**
(Anderson textbook reference; the "analytic expressions" sentence; the two separate
Target columns; the two-table argument above) and **read §2h.8.1 verbatim**, then
**RATIFIED** the classification:

> **VMFL051-R3 is `PASS`-CAPABLE — it is NOT capped at `GATE REACHED`** — because
> (a) the reference is the manual's **independent analytical** Prandtl–Meyer Target
> (§33.2: independent ⇒ not circular ⇒ `PASS` available; two-table argument above),
> and (b) that reference is the **exact self-similar solution of the same 2-D steady
> compressible Euler model** `rhoCentralFoam` discretises with μ = 0 — a genuine 2-D
> exact solution, **not** a reduced-dimension relation, which is exactly why
> VMFL046's quasi-1-D nozzle reference caps and this one does not (§12.2 answer
> `SAME`) — so under **`VERIFICATION_CHARTER §2h.8.1` (v1.28, 2026-08-31, the
> exact-PDE rule)** — *"a reference that is the exact or manufactured solution of the
> same continuum PDE the solver discretises is `PASS`-capable under §2h.4's five
> conditions declared before compute; a reference from a different model — nozzle
> relations, shock tables, lumped or series-resistance paths, correlations,
> experiment — caps at `GATE REACHED`, however exact its own algebra. The test is
> sameness of model, never exactness of algebra."* — `PASS` is available, subject to
> **§2h.4's five conditions declared before compute (below)**.
>
> **Recorded as ratified by the `ansys-verification-supervisor`** on the evidence
> above, this session (2026-09-10), **not as this lane's derivation**.

If this case yields a `CONVERGING` in-band triple it would be this team's **first
credential from the manual's never-run set** via an analytical-reference `PASS` — the
reason the classification was verified at source and not ratified on a lane's word.

**Do-not-over-claim.** `PASS`-capable is a **ceiling**, not a verdict. `PASS`
requires, on top of the five conditions, a **`CONVERGING`** Roache triple inside the
±0.5 % band (CLAUDE.md rule 5 step 3; `ANSYS_VERIFICATION_CHARTER §11.1` point 3: the
cap still binds on any limb whose triple is not `CONVERGING`). If the R3 triple is
again non-monotone, the verdict is **`NOT A RESULT`** — no gate, band or cap moves
(§6, §7). **Do-not-under-claim.** Because the reference is analytical and the model
is `SAME`, refusing to declare the five conditions would forfeit a credential the
case has actually earned; the five conditions are declared here precisely so that a
`CONVERGING` in-band triple **can** be graded `PASS`.

**§2h.4's five conditions, declared before compute:**

1. **Reference is the exact solution of the SAME continuum model.** MET — the
   Prandtl–Meyer fan is the exact 2-D steady compressible Euler solution;
   `rhoCentralFoam` (μ = 0) discretises the 2-D compressible Euler equations. Model-
   form error zero by construction; residual is discretisation error.
2. **Iterative error separately gated by rule 5 limb (1), one-way.** MET by design —
   the settledness clause (§5) refuses any level whose time-mean is not window-
   insensitive as `NOT A RESULT`, and no verdict path turns that into `PASS`
   ("no triple" never means "no rule 5").
3. **Round-off stated with magnitude, shown negligible against the band.** The
   reference's own table rounding (Defect 2, ≈0.005 % of Mach ≈ 1.6e-4) and
   double-precision round-off in the flux-weighted reduction (≤ ~1e-12 relative) are
   both **orders below the 0.5 % = 0.0162-Mach band**. Stated as numbers, not
   assurances.
4. **The wording makes no continuum claim.** The graded claim reads *"the
   discretisation error of the flux-weighted post-expansion Mach is below X at N
   cells"* — **never** *"the solution is correct to X"*. A `PASS` certifies agreement
   with the analytical Prandtl–Meyer value at the ±0.5 % band on the meshes run,
   nothing about finer meshes.
5. **The claim is bounded by the levels actually run.** *"In-band at every level
   run,"* never *"so the answer is mesh-independent."*

**The §12.2 `SAME` ruling and the `PASS`-capable ceiling are RATIFIED by the
`ansys-verification-supervisor`** (§3.1 ceiling block above), a gate-affecting
classification the supervisor verified at source rather than on this lane's word
(CLAUDE.md rule 9). **The five conditions above will be checked PERSONALLY by the
supervisor at the freeze** (supervisor's ruling 1). **This is a NEW registration,
frozen after §2h.8**, carrying the five conditions on its face before compute, as
§2h.4's chapeau requires. **`PASS` remains conditional:** a `CONVERGING` in-band
triple is still required, and a non-monotone triple is `NOT A RESULT` whatever the
value (§4, §6, §7) — the ceiling is a ceiling, not a verdict.

### 3.2 The cross-plane — fixed by geometry, answer-blind

The graded quantity is sampled on a **vertical cross-plane at a fixed streamwise
station `x_p`**, over a **y-band lying strictly inside the uniform post-expansion
wedge, clear of the expansion fan**. Every number below is derived from the case
**inputs** — M₁ = 2.5, the 15° turn, γ = 1.3990093734749485, and the domain bounds —
and from a **conservative Mach bound M_cons = 3.5** chosen larger than any plausible
answer. **None is derived from a solved output**, which is what makes the plane
answer-blind.

Geometry (from R2 §4, unchanged): corner at the origin O; upstream wall on y = 0 for
x < 0; downstream wall deflects the flow 15° **downward** for x > 0
(y_wall(x) = −x·tan 15°); inlet x = −0.3, outlet x = +1.2, top y = +0.65. The fan is
centred at O; its characteristics are straight rays from O:

- **Leading Mach ray** at +μ₁ = +arcsin(1/2.5) = **+23.578°** from horizontal.
- **Trailing Mach ray** at (−15° + μ₂). Using the **analytical** M₂ ≈ 3.2355:
  μ₂ = arcsin(1/3.2355) = 18.007°, trailing ray = **+3.007°**. Using the
  **conservative** M_cons = 3.5: μ = arcsin(1/3.5) = 16.601°, trailing ray =
  **+1.601°** (a ray that lies **below** the true trailing ray for any M₂ < 3.5, so a
  band under it is inside the true uniform region regardless of the answer).

**Station.** `x_p` = **0.6 m** — the geometric midpoint of the downstream domain
[0, 1.2]: 0.6 m clear of the corner and 0.6 m clear of the outlet, so it is
maximally clear of both the fan's origin and the outlet BC. (Domain geometry only.)

**y-band.** At `x_p` = 0.6:
- wall: y_wall = −0.6·tan 15° = **−0.160770 m**;
- conservative trailing ray (M_cons = 3.5): y_tr_cons = +0.6·tan 1.601° =
  **+0.016770 m** (the true trailing ray at analytical M₂ sits higher, at
  +0.6·tan 3.007° = +0.031516 m; the leading ray sits far higher at +0.6·tan 23.578°
  = +0.2619 m, so the whole band is well below the fan and below the top boundary —
  no reflection, consistent with R2);
- band `H_cons` = y_tr_cons − y_wall = **0.177540 m**;
- **sampling band = middle 50 % of the conservative wedge:**
  **y ∈ [y_wall + 0.25·H_cons, y_wall + 0.75·H_cons] = [−0.116385 m, −0.027615 m]**.

**Why this is answer-blind.** The band's every bound is computed from M₁, the turn,
γ, M_cons and the domain — all **inputs**. The top of the band (−0.0276) is a 25 %
margin below the **conservative** trailing ray (+0.0168), which is itself below the
**true** trailing ray (+0.0315) for any M₂ < 3.5; the bottom is a 25 % margin above
the wall. **The entire band therefore lies inside the true uniform post-expansion
wedge for every physically possible answer**, so the plane cannot have been chosen to
make a number come out — it is fixed before any answer exists.

**ACCEPTED by the supervisor (ruling 3): `x_p` = 0.6 m, M_cons = 3.5, middle-50 %
band.** Why each literal follows from geometry and inputs alone: **`x_p` = 0.6 m** is
the arithmetic midpoint of the downstream domain [0, 1.2] — equidistant from the
corner (fan origin) and the outlet BC, a pure domain-geometry choice; **M_cons = 3.5**
is a round Mach chosen strictly larger than any physically plausible post-15°-turn
value (the analytic M₂ ≈ 3.2355), so the conservative trailing ray it defines lies
below the true one for every possible answer — a bound, not a fit; **middle-50 %**
places symmetric 25 % margins between the band and both the wall and the conservative
trailing ray, referencing neither the solved field nor the gate value. Because a
frozen literal that could defensibly have been another literal deserves to be *shown*
not to matter, §3.4 pre-registers a plane-sensitivity diagnostic at a **second**
geometry-fixed station that **gates nothing**.

**The face zone.** `topoSetDict` selects the single column of internal faces whose
face centres lie in the thin slab
{ x ∈ [x_p − δ, x_p + δ], y ∈ [−0.116385, −0.027615], all z }, with δ < half the
finest cell width so exactly one column of faces is captured at every level, into a
`faceZone` `postExpPlane`. **A second `faceZone` `postExpPlane2`** is defined the same
way at `x_p2` = 0.9 m over its band (§3.4), for the plane-sensitivity diagnostic
only. The comparator **refuses (exit 2)** if either zone is empty at any level or if
either captures more than one face column (a mesh-dependent double count).

### 3.3 The flux weighting and the single derived Mach

On `postExpPlane`, per timestep, an OpenFOAM `surfaceFieldValue` function object with
**`weightField phi`** (phi = the face mass flux ρU·n·A that `rhoCentralFoam` writes)
and **`operation weightedAverage`** forms, for each quantity q:

  **⟨q⟩_ṁ = Σ_f (ρU·n·A)_f · q_f / Σ_f (ρU·n·A)_f**

(all plane faces carry positive phi in the supersonic downstream flow, so there is no
sign cancellation across the plane). The FO writes ⟨p⟩_ṁ, ⟨T⟩_ṁ, ⟨Ma⟩_ṁ and the
flux-weighted total pressure ⟨p₀⟩_ṁ (p₀,f = p_f·(1 + ½(γ−1)Ma_f²)^{γ/(γ−1)}) every
timestep, into `postProcessing/postExpPlane/…/surfaceFieldValue.dat`.

**The single self-consistent Mach (the gated observable) — RULED (supervisor's
ruling 2): the isentropic p₀/p Mach.** In isentropic flow the stagnation pressure is
the conserved quantity, so the gate uses **one** isentropic relation on the
flux-weighted pressures, removing the R2 p-vs-T ambiguity:

  **M_lab(t) = sqrt( (2/(γ−1)) · [ (⟨p₀⟩_ṁ / ⟨p⟩_ṁ)^{(γ−1)/γ} − 1 ] )**

evaluated per timestep, then **time-averaged over the R2 settled window** (last 50 %
of rows). The three-level triple is built on these three time-means.

**Why p₀/p is the ruled primary, not mass-averaged Ma (supervisor's reasons).**
(i) Total pressure is the conserved quantity of isentropic flow, so p₀/p is the
**most physically constrained** reduction available; (ii) it cures the R2 p-vs-T
inconsistency (0.0057 at L3, same order as |d32|) **by construction**; (iii) the
reference itself is an isentropic relation, so the reduction is **model-consistent**.
There is **no circularity** — the solver produces p and p₀ independently, and the
isentropic relation is only the *definition* of Mach from a pressure ratio, not a
fit. **(iv) A DELIBERATE PROPERTY: if the KT scheme generates entropy at the corner
singularity, p₀ falls and this reduction reads LOW rather than hiding it** — the
suspected corner-entropy floor becomes **visible in the gate quantity itself**
instead of lurking in a masked average.

**DIAGNOSTICS, printed BESIDE M_lab, gating nothing (supervisor's ruling 2):** the
flux-weighted mass-averaged **⟨Ma⟩_ṁ** (time-mean) and the T-based Mach from ⟨T⟩_ṁ
and the conserved ⟨p₀⟩/⟨p⟩ temperature ratio. **A disagreement between M_lab and
⟨Ma⟩_ṁ is itself informative** (it would localise entropy generation) and is reported
whatever it shows; it never moves the gate. The primary M_lab and both diagnostics
are fixed in the frozen comparator and are not settable at grading time.

### 3.4 PLANE-SENSITIVITY DIAGNOSTIC — a second geometry-fixed station, GATING NOTHING (supervisor's ruling 3)

The identical p₀/p reduction (§3.3) is computed a second time on a **second
cross-plane at `x_p2` = 0.9 m**, with its answer-blind band built by the **same rule**
as §3.2. **This diagnostic GATES NOTHING and is reported whatever it shows.**

**Why `x_p2` = 0.9 m follows from geometry and inputs alone.** It is the arithmetic
midpoint of [`x_p`, outlet] = [0.6, 1.2] — the geometry-fixed downstream check
maximally separated from the primary plane while remaining upstream of the outlet BC.
Its band, by the §3.2 construction at `x_p2` = 0.9, M_cons = 3.5:
- y_wall = −0.9·tan 15° = **−0.241154 m**;
- conservative trailing ray = +0.9·tan 1.601° = **+0.025155 m** (true trailing ray
  at analytic M₂ = +0.9·tan 3.007° = +0.047274 m, higher — band clear of the fan);
- `H_cons` = 0.266309 m; **band = [−0.174577 m, −0.041422 m]** (middle 50 %).

Every bound is input-derived; none is a solved output. **Purpose (stated so it is not
over-read):** in ideal Prandtl–Meyer flow the post-expansion wedge is streamwise-
uniform, so the two stations' M_lab should agree. **If they agree, the choice of
`x_p` is vindicated on the record; if they disagree, that is itself a finding about
the uniformity of the wedge** (e.g., residual fan tail or outlet influence) — far
better printed than argued afterwards. The comparator reports the two stations' M_lab
per level and their difference; **it never lets the second station move a verdict.**

## 4. THE ROACHE GATING (CLAUDE.md rule 5), in its stated order

A row whose grid triple is not `CONVERGING` is **`NOT A RESULT`**, whatever its
value. The comparator applies, in this order:

1. **any level not iteratively/temporally converged** — here, any level whose
   time-mean M_lab fails window-length insensitivity (|mean(last 50 %) − mean(last
   25 %)| > `TOL_STAT` = 5.0e-4), or failing any completion clause of §8, **or** the
   cross-plane face zone empty/double ⇒ **`NOT A RESULT`**;
2. the Roache triple on the three time-mean M_lab values being **`DIVERGENT`,
   `STAGNANT`, `OSCILLATORY` or `EXACT`** ⇒ **`NOT A RESULT`**, with the value, both
   the value and the triple, R, the increments and the order printed beside it, and
   **no GCI quoted**;
3. **`CONVERGING`** ⇒ **`PASS`** inside the ±0.5 % band else **`GATE FAIL`**, with GCI
   at Fs = 1.25 and the Richardson extrapolation printed.

**GCI is NEVER quoted on a non-monotone triple.** The gate can only turn a `PASS` or
`GATE FAIL` **into** `NOT A RESULT`, never the reverse. A **gate-blind physical-range
refusal** (referencing neither the band nor 3.2370): each level's time-mean M_lab
must be finite and in the physical supersonic range **(1.0, 20.0)** or the comparator
**refuses (exit 2)**. All classifier states and both settledness outcomes are
exercised by `--selftest`.

## 5. Live planted-zero control (CLAUDE.md rule 3; L-487) — designed against the FLUX-WEIGHTED reduction

Because the gate reduction is a **mass-flux-weighted mean** (a weighted mean), the
plant is designed **against that weighted statistic**, not against the field
(L-487: two of this team's plant designs died for exactly this). Every plant is
written into a **temporary COPY**; the run tree is **never modified**; the comparator
**exits 2** if any control fails. Modelled on R2's control, which planted
**1.234e-3** into **1679 of 3357** rows of a copy and recovered it to **2.9e-16**,
and which was shown able to **FAIL** by a mutation test — **the fail arm is
required here.**

| id | reader under test | plant (PROPER SUBSET) | expected & refusal |
|---|---|---|---|
| **PZ-1** | the flux-weighted plane reader (the gate reduction) | +1.234e-3 Mach onto a **proper subset** of the plane's faces — the **lower half of the y-band faces** — in a COPY | the flux-weighted mean must shift by **plant × (Σ_planted ṁ_f / Σ_all ṁ_f)** — the **mass-flux-weighted** fraction, NOT the count fraction — to ≤ 1e-12; **refuse** if the observed shift differs, or if the planted subset is the **whole plane** (the inert whole-set config, refused so it cannot be silently reintroduced) |
| **PZ-2** | the `Ma`/field reader on disk | +7.77e-2 Mach on the **first half** of the field cells of a copy | field mean must shift by plant × (n_planted/n_total) to 1e-9; **refuse** if the field is `uniform` or if the subset is the whole field; report field min/max/mean (proof it reads a non-zero off disk) |
| **PZ-3** | the reference (Prandtl–Meyer) computation | **+5° turn** | solved M₂ must satisfy ν(M₂) − ν(M₁) = turn to 1e-9° and move by > 1e-6 |

**THE FAIL ARM (mutation test), required.** `--selftest` must include a mutation in
which the reader **ignores the mass-flux weights** (uses a plain arithmetic mean, or
a uniform weight field): with PZ-1's proper-subset plant, a weight-ignoring reader
recovers a **different** shift (the count fraction, not the flux fraction) and the
comparator must then **REFUSE (exit 2)**. A second fail arm: a **drifting** time-mean
series is correctly judged NOT settled (window-insensitivity > `TOL_STAT`); a third:
a **subsonic/absurd** M_lab triggers the gate-blind physical-range refusal. Each fail
arm asserts the **actual rc is 2** (not merely a printed message — the "refusal that
announces one code and returns another" defect, §12.2 lineage / evidence-annotated-
as-non-binding). The known-good arm plants on the real reduction of a scratch smoke
`.dat` (value-blind) and recovers the plant to machine precision. **PZ-1 tests the
flux-weighted reader itself, which is the same code path the §3.4 diagnostic plane
uses**, so the diagnostic reader is covered by the same control even though it gates
nothing.

## 6. Cost (CLAUDE.md rule 12) — anchored on R2's MEASURED 9.8 core-min

| item | value | measured or assumption |
|---|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × 1 / 60 | fixed |
| **basis** | **R2 total 9.8 core-min** (588 wall s serial; `verification/runs/ansys_verification/VMFL051-R2/COST.txt`) for the **identical solve** | **MEASURED**, this exact solve, this box |
| added cost of the new flux-weighted FO(s) | **negligible** — one per-timestep `surfaceFieldValue` reduction over a **single face column**; no extra fields solved, no extra timesteps | **ASSUMPTION** (the solve is byte-identical; only sampling FOs are added) |
| point estimate (total) | **≈ 9.8 core-min** | measured basis + negligible-FO assumption |

**Per-level caps (core-min), carried from R2 unchanged (the case/gate does not
move):**

| level | R2 measured wall (core-min) | per-level ceiling |
|---|---|---|
| L1 | (in R2's 9.8 total) | 2 |
| L2 | " | 8 |
| L3 | " | 26 |
| **total (the ENFORCED running cap)** | **9.8 measured** | **28** |

The **enforced cap is a running total of 28 core-min** (`timeout` = 28 × 60 / ranks
s), UNCHANGED from R2. R2 used **9.8 / 28 = 35 %** of it. An overrun **stops the run**
(rc 124) and gets no new budget; a re-run is a new rung, moving no gate.

**Contention allowance, named separately, never netted.** R2's own point estimate
was 23.32 core-min (run 1 wall, which carried ~14.4 core-min of contention); R2 then
came in at 9.8 core-min on a quiet box. If contention returns, the actual can rise
toward the 28-core-min cap **as contention, reported separately** — it is not folded
into the 9.8 point estimate, and waste (if any) is named per
`COMPUTE_BUDGET_CHARTER.md` §6, never absorbed into the ratio.

| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). Core-min are R2's **measurement** of the identical solve. |
|---|---|
| dollars at the point estimate (9.8 core-min = 0.16333 core-h) | **$0.00838 DERIVED, NOT MEASURED** |
| dollars at the cap (28 core-min = 0.46667 core-h) | **$0.02394 DERIVED, NOT MEASURED** |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; a blanket is not a per-item read (rule 9) |

**Calibration at completion (rule 12).** The run-and-grade lane compares actual
core-min (from `RUN_RC.txt`/`COST.txt`) against the 9.8 point estimate, attributes
the gap (contention/waste/misprediction, waste named separately), states the ratio
actual/predicted, and appends one row to `docs/COST_CALIBRATION.md`. A completion
report without that row is incomplete.

## 7. Failure modes — with the corner-entropy-floor outcome named as legitimate

1. **The flux-weighted triple is still non-monotone** (`OSCILLATORY`/`DIVERGENT`/
   `STAGNANT`) ⇒ **`NOT A RESULT`** (rule 5 step 2). **This is a legitimate,
   pre-registered result, per the supervisor's ruling:** the finding is that the
   **corner-seeded entropy floor sits at the functional's own magnitude and VMFL051
   is not cleanly reachable with this solver** by a spatial re-reduction. R2's inner
   diagnostic zone was already non-monotone (§0), so this outcome is **named in
   advance as informative, not a disappointment**, and it moves no gate, band or cap.
2. **A level's time-mean M_lab not settled** (window-insensitivity > `TOL_STAT`) ⇒
   **`NOT A RESULT`** (rule 5 step 1). R2's settledness was 7.4e-5 / 8.1e-6 / 6.4e-6
   for the volume observable; the flux-weighted observable's settledness is
   **re-tested at grade time, not assumed here.**
3. **The cross-plane face zone empty or multi-column at any level** ⇒ comparator
   **refuses (exit 2)** (§3.2).
4. **Non-physical M_lab** (outside (1.0, 20.0)) ⇒ gate-blind physical-range refusal
   (exit 2) (§4).
5. **Persistent flux-weighted p-vs-T inconsistency** (the R2 pathology not cured) ⇒
   reported as a **diagnostic**; it does not change the gate, but it is flagged as
   evidence the lever did not achieve its stated purpose.
6. **`CONVERGING` triple in the ±0.5 % band** ⇒ **`PASS`** — **AVAILABLE** per the
   §3.1 ceiling **ratified by the supervisor**, subject to §2h.4's five conditions
   (met/declared, checked personally by the supervisor at freeze) — this team's route
   to its **first credential from the manual's never-run set** via an analytical-
   reference `PASS`. **`CONVERGING` outside the band** ⇒ **`GATE FAIL`**, a finding,
   never softened.
7. **The plane-sensitivity diagnostic (§3.4)** — whatever the two stations show, it
   **never moves a verdict**; agreement vindicates `x_p`, disagreement is a printed
   finding about wedge uniformity.

## 8. Strict completion (CLAUDE.md rule 4) — carried from R2

The comparator refuses (exit 2) on any failed clause and never grades a partial run.
Carried verbatim from R2 §8 (declared, tighter-or-equal), because the SOLVE is
identical: **C1** `rc = 0` (solver's own rc in `RUN_RC.txt`); **C2** `^End$` in
`log.rhoCentralFoam`; **C3** last time == `endTime` in DEPARTURE-1 form
(|t_last − endTime| ≤ maxDeltaT 1e-5 s, adaptive-step overshoot); **C4** fields
present at `endTime` (`T U p rho Ma` + phi for the flux weighting); **C5**
`ExecutionTime` per `Time` line, > 0 (DEPARTURE-2, adaptive-step transient); **C6**
age guard — every `endTime` field newer than the newest file in the case's own `0/`,
and the driver refuses into any pre-existing level directory. The driver also refuses
unless this pre-registration **and** the comparator on disk are **byte-identical to
their HEAD blobs** at the R3 freeze commit (freeze-pin, rule 2), and refuses if
`topoSet` left the cross-plane face zone empty (§3.2).

## 9. Verdict vocabulary, and what this rung will NOT claim

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (rule 1). `PENDING` means **not yet run** and never softens a
`GATE FAIL`. Nothing about Ansys, Fluent or CFX (the vendor numbers 3.2316 / 3.2354
are context, never the gate). Nothing about p₁ or T₁ (the gated quantity is derived
from ratios on the plane). Nothing about the γ = 1.4 alternative (run 1's declared
blind spot). Only a **`PASS`** is a credential; a `GATE FAIL` or `NOT A RESULT` is a
finding, never softened. **The lever is the flux-weighted cross-plane spatial
reduction and nothing else; the gate is 3.2370 ± 0.5 %, unchanged and
unchanged-able at this freeze.**

## 10. The grading path — TO BE FROZEN (not yet committed)

At the R3 freeze the supervisor commits `grade_vmfl051_r3.py`, `run_vmfl051_r3.sh`,
the case tree (with the CHANGED `topoSetDict` and `controlDict.template` and the
UNCHANGED solve blobs of §2), and records each committed blob sha here. At analysis
time the grading path is re-hashed against these blobs and
`grade_vmfl051_r3.py --verify-frozen <commit>` **REFUSES (exit 2)** if the file on
disk is not byte-identical. **No threshold, band, reference value, plane location,
window fraction or plant constant is settable from the command line.** Run outputs go
to `verification/runs/ansys_verification/VMFL051-R3/<level>/`; the grading JSON is
`verification/runs/ansys_verification/VMFL051-R3/GRADING_VMFL051_R3.json`.

**Blob shas: OWED at freeze — this file is a draft and carries none.**

## 11. What CANNOT be verified before the freeze — stated plainly

- **The three levels' flux-weighted time-mean triple** — computed only at the graded
  run; **not read here** (choosing the lever from it would be fitting — L-500). The
  lever was chosen from the *structure* of R2's finding (spatial non-monotonicity
  surviving a working temporal fix; the internal p-vs-T inconsistency at grid-signal
  magnitude), not from any R3 output.
- **That the flux-weighted observable is settled at 7e-3 s** at every level — judged
  by the frozen settledness clause at grade time, not asserted here.
- **Whether the flux-weighted triple is `CONVERGING`** — if not, `NOT A RESULT`, and
  no gate/band/cap moves (§7 mode 1).
- **The comparator, driver and the two changed dictionaries do not yet exist** — they
  are built and committed at the freeze; their `--selftest` (planted controls, all
  classifier states, the fail arms of §5) must fire green, zero solver compute,
  **before** the supervisor freezes.

---

## Amendment 1 — 2026-09-10, BEFORE FIRST COMPUTE. Draft v1.1 (still UNFROZEN).

**Lines whose number changed above this section: 0.** Nothing above is edited;
this section is appended at the foot (CLAUDE.md rule 6).

**Legality, and the condition CHECKED not asserted** (CLAUDE.md rule 2;
`VERIFICATION_CHARTER.md` §2b.1). This file is still a draft and is not frozen,
so amendments are legal; the condition is checked, not asserted. At
**2026-09-10T16:05:10Z**, read with `date -u` in the same shell invocation,
**`verification/runs/ansys_verification/VMFL051-R3/` does not exist** (`ls -d`
returned *No such file or directory*) and `find` beneath it returned **0 files**.
No `blockMesh`, `topoSet` or `rhoCentralFoam` has run into any R3 run root; no R3
mesh exists. **This amendment therefore precedes all compute.**

**It changes NO gate, NO threshold, NO cap and NO label.** The gate stays
|M_lab − 3.2370| / 3.2370 ≤ 0.005 at the finest converging level; the exact-value
diagnostic stays 0.25 %; the cap stays 28 core-minutes; the verdict vocabulary is
untouched; the lever stays the flux-weighted cross-plane spatial reduction. What
it does is (A) record that the grading path was BUILT and its `--selftest` fired
green, and (B) disclose two corrections to the drafting text of §5 and §8 that the
build proved necessary — corrections to the INSTRUMENT DESCRIPTION, never to the
gate.

### A1.1 The grading path now exists (untracked) and `--selftest` is green

Built by `ansys-lane-opus48`, all with **ZERO solver compute**, verified against
the installed OpenFOAM v2606 tree (N-AV4 / L-286 — the reader is built against
the writer SOURCE, not a belief):

- `case/system/topoSetDict` (**CHANGED**): keeps R2's two cellZones and ADDS the
  two cross-plane faceZones via the v2606 idiom `boxToFace` (faceSet) →
  `setToFaceZone` (faceZone). `postExpPlane` at x_p = 0.60 m, `postExpPlane2` at
  x_p2 = 0.90 m, with the §3.2 / §3.4 y-bands. **x_p = 0.60 and x_p2 = 0.90 land
  EXACTLY on the downstream-block face grid at every level** (0.6/dx and 0.9/dx
  are integers for nxB ∈ {96,192,384}), and the x-slab half-width δ = 5.0e−4 m is
  **below half the finest cell dx** (L3 half-dx = 1.5625e−3 m), so exactly one
  x-face column is captured per plane (a geometric guarantee).
- `case/system/controlDict.template` (**CHANGED**): keeps R2's FOs and adds
  (i) the **`exprField`** (v2606 `fvExpressionField`, runtime type `exprField`,
  confirmed in `tutorials/compressible/rhoSimpleFoam/squareBend/system/derivedFields`)
  building `pStag = p·(1 + 0.19950468673747423·Ma²)^3.5062067873019136` — the
  isentropic stagnation pressure for the frozen gas — placed AFTER `MachNo` so the
  stored `Ma` exists in the registry; (ii) two `surfaceFieldValue` FOs on the two
  faceZones, `operation weightedAverage`, `weightField phi`, `fields (p T Ma
  pStag)`, written every timestep.
- `grade_vmfl051_r3.py` (**NEW**, the grading path): reads the v2606
  `surfaceFieldValue.dat`, derives the per-row isentropic p0/p Mach, time-means it
  over the settled window, runs the Roache triple, planted-zero controls and
  strict-completion checks, and **REFUSES (exit 2)** rather than degrades.
  `--selftest`: **49 checks, 0 failures**; `--verify-frozen` and `--dryrun-reader`
  (prints no value) present; every threshold, band, plane location, window
  fraction and plant constant is a module-level constant, none settable from the
  command line.
- `run_vmfl051_r3.sh` (**NEW**): freeze-pin (prereg AND comparator byte-identical
  to HEAD blobs), age guard (refuses into any pre-existing level dir), refuses if
  the GATE faceZone is empty or holds more faces than ny (multi-column catch), and
  enforces the 28 core-min running cap with `timeout`.
- Solve blobs `blockMeshDict.template`, `fvSchemes`, `fvSolution`, `0/{U,T,p}`,
  `thermophysicalProperties`, `turbulenceProperties` copied **byte-identical** to
  R2 (git hash-object equal: `7557bfec`, `25d6f166`, `885bb5f6`, `9d8f63f1`,
  `84d6430d`, `3da73319`, `3734a5a0`, `5459d691`).

### A1.2 CORRECTION to §5 (PZ-1): the flux weighting is done inside OpenFOAM, so the plant is temporal, not per-face

§5 designed PZ-1 as a plant **onto a proper subset of the plane's FACES** with the
shift scaled by the **mass-flux-weighted fraction**, plus a fail arm in which a
**weight-ignoring reader** recovers a different shift. **That is not implementable
against what the comparator reads**, and this is disclosed here so the supervisor
sees it before the freeze: the `surfaceFieldValue` FO performs the mass-flux
weighting **live inside OpenFOAM** and writes **one weighted value per field per
timestep**, so the `.dat` carries **no per-face values and no per-face fluxes**.
The flux weighting therefore rests on the **verified v2606 source** — the weight
is `mag(phi)` (`surfaceFieldValue.C:50`) and `weightedAverage` returns
`gSum(mag(phi)·q)/gSum(mag(phi))` (`surfaceFieldValueTemplates.C:182`), with face
orientation handled by `faceFlip_` and scalar averages orientation-independent —
**not on a comparator plant**.

**PZ-1 as built** is therefore the R2-form control on the **same temporal
reduction the gate reads**: it plants +1.234e−3 onto a **proper time-subset** of
the settled-window rows of the plane `.dat`'s `weightedAverage(Ma)` column, in a
COPY, reads it back **from disk**, and requires the window-mean to move by
plant × (planted-rows / window-rows); it **refuses** if the reader cannot see the
plant, and the whole-window plant is refused as the inert configuration. The
weight-ignoring mutation of §5 is replaced by three **implementable** fail arms,
each asserting the **actual rc is 2**: (a) a drifting series is judged NOT settled;
(b) a subsonic/absurd M triggers the gate-blind physical-range refusal; (c) an
empty faceZone (`# Faces : 0`) refuses. **PZ-2** (plant into the `Ma` field on
disk) is unchanged and remains the control that proves a non-zero is read off
disk; **PZ-3** (the reference computation) is unchanged.

### A1.3 CORRECTION to §8 (C4): phi is not written to disk

§8 listed the C4 completion fields as `T U p rho Ma + phi`. **`phi` is created by
`rhoCentralFoam` (`createFields.H:90`, `phi = fvc::flux(rhoU)`) but is NOT
`AUTO_WRITE`**, so it never lands on disk; it is a live registry field consumed by
the FO during the run. **C4 as built requires `(T U p rho Ma)`, exactly as R2**;
`phi`'s presence is proven by the flux-weighted columns existing in the `.dat`, not
by a file on disk. This removes an unsatisfiable clause; it does not loosen the
completion rule.

### A1.4 What this amendment does NOT do, and what is still owed at the freeze

It registers **no prediction** of the R3 triple's outcome; it adds **no clause**
that can turn a `GATE FAIL` into a `PASS`; the gate, band, cap, label and lever are
untouched. **Owed at the freeze (the supervisor's):** the committed-blob shas of
every grading-path file (§10's table), obtained at the freeze commit, and the
supervisor's personal read of `grade_vmfl051_r3.py` as a diff and of §2h.4's five
conditions. **Still unverifiable before the freeze** (§11 stands): that the mesh
builds, that `topoSet` puts one face column into each plane, and that the live
`surfaceFieldValue.dat` matches the source-derived reader — the last closed cheaply
after the first coarse level by `grade_vmfl051_r3.py --dryrun-reader <L1 .dat>`,
which prints only `parsed, N rows, ...` and never a value.
