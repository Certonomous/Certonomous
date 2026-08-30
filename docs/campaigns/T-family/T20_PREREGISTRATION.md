# T20 — lumped-capacitance transient control with internal generation, EXACT tier: pre-registration

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
RUN TREE.** Read in full by the supervisor before the freeze, per
`SUPERVISION_CHARTER.md` §3 (pre-registration committed before compute is a
personal, non-delegable check); their check 4 is discharged and recorded in §16.
**This document authorises no solve.** Every gate, threshold, band, cap and label
below is fixed at this commit and may afterwards change only as a dated addendum
that alters none of them.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE
FAIL / NOT A RESULT / BLOCKED / PENDING.** No other word appears as a verdict in
this rung.

---

## 0. WHAT THIS RUNG IS, WHAT IT IS NOT, AND WHY IT IS CALLED T20

### 0.1 What it is

The **V exact tier of Sanaa's CASE 4** (battery-module transient, directive
`etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md` §4.6, first
bullet): **one** battery cell, a **uniform volumetric heat source applied as a
step at t = 0**, conductivity raised so the body is thermally lumped, and an
**imposed** convective coefficient through
`externalWallHeatFluxTemperature` **instead of a coupled fluid**. The graded
comparison is against the closed-form lumped-capacitance solution.

**There is no fluid region, no channel, no turbulence model, no CHT coupling and
no mesh-motion in this rung.** It gates the **transient solid machinery** of the
solver Case 4's module rungs will use — the `ddt` discretisation, the
`fvOptions` volumetric source, the solid thermophysical path and the convective
boundary condition — and nothing else.

### 0.2 What it is NOT — stated first, not in a footnote

> **T20 earns `V` for TRANSIENT SOLID CONDUCTION WITH INTERNAL GENERATION AND A
> CONVECTIVE BOUNDARY, and for NOTHING conjugate.** It does not earn conjugate
> heat transfer, does not earn anything about the cooling channel, does not earn
> anything about a turbulence model, and does not earn a spatial GCI. Case 4's
> `G` gates (spatial triple on peak cell temperature, temporal triple on
> time-to-peak) are separate rungs with their own registrations and this
> document may not be cited as covering them.

This is the same boundary T11 drew for itself (`T11_PREREGISTRATION.md` §0) and
it is drawn for the same reason: **a tier overclaim is the one error that becomes
a credential.**

### 0.3 Why the id is `T20` and the path is `docs/campaigns/T-family/`

The supervisor's brief proposed `docs/campaigns/T-family/K4a_PREREGISTRATION.md`
and asked that the naming be checked rather than accepted. It was checked, and
**both halves of the proposal are wrong**; the reasoning is recorded here because
a filing decision that is not reasoned in writing is drift (`FILING_CHARTER.md`
§3).

**`K4a` is wrong.** `K*` is the rung prefix of campaign **F14** (the DC-cooling
ladder): `docs/campaigns/F14-cooling-ladder/` holds `K0b`, `K0c`, `K0cG`, `K0cP`,
`K0cQ`, `K0cR`, `K0cS`, `K0cT`, `K0cX`, `K0d`, `K0e`, `K0f`, `K2a`. Filing a
battery-module rung as `K4a` inside the T-family directory would put an F14-shaped
id in a T-family folder and would collide with F14's own numbering the first time
that campaign reaches `K4`. Rejected.

**A new campaign folder under `docs/campaigns/` is wrong for THIS rung.**
`FILING_CHARTER.md` §5 is explicit: *"Before writing any durable file, find the
nearest existing sibling and copy its pattern. If no sibling exists, the file
probably belongs in a directory that already has one."* The nearest sibling is
not close, it is **exact**: `T11_PREREGISTRATION.md` is transient conduction on
an analytic referent with a convective boundary, and T11's own text names this
rung in advance —

> *"True transient conjugate requires `chtMultiRegionFoam` — present on this box,
> unused by this family — and is a separate rung with its own registration."*
> — `T11_PREREGISTRATION.md` §0

That sentence is a written invitation for exactly this document. Three further
siblings confirm the pattern: `T14` is titled *"2-D transient conduction in a
square (**T11b**)"*, `T18` is *"(**T11c**)"*, `T17` is *"(**T11d**)"*. **The
family's established practice is that a new transient-conduction subject takes
the next free top-level `T` number and carries its T11 lineage in the title**, in
one folder, so that `T_FAMILY_INDEX.md` — the register that classifies every rung
as EXACT / FORMULA / ACQUIRE — can see it. A rung filed outside that folder is a
rung the tier register cannot classify.

**The number is 20, taken from the maximum, never from a count** (`CLAUDE.md`
rule 11, applied by analogy to rung ids). The maximum existing `T`-number across
`docs/campaigns/T-family/` and `verification/runs/T-family/` is **19**
(`T19_PREREGISTRATION.md`, `verification/runs/T-family/T19_runs/`), re-derived at
HEAD in the committing invocation.

**One `T20` token exists elsewhere and it is NOT a claim on this id — corrected
here rather than left as a false sentence.** An earlier draft of this section
asserted *"a search for the token `T20` returns zero hits"*. **That was wrong
twice over.** A naive `grep -rl "T20"` returns **93 files**, because every ISO
timestamp in the twenty-hundred hour matches (`2026-08-26T20:42Z`); and a search
restricted to `T20` as a *token* returns exactly **one** real hit —
`verification/campaign/LADDER_V_V15_LADDER_TEXT_CLAIMS.md:170`, where `T1`…`T28`
are **text-claim identifiers in a closure-challenge audit**, a different namespace
entirely with no T-family rung behind it. **The id is unclaimed in this family's
namespace; it is not unmentioned in the repository, and the distinction is
recorded because the first search this lane ran could not tell the two apart.**
That is the same detector failure §10.1 records against this lane, caught a second
time and fixed before the freeze rather than after it.

**No sub-letter.** `T9aD`, `T10aR`, `T1b` are follow-on *arms of an existing
rung*; a new subject with its own registration takes a plain number (`T14`…`T19`).
This is a new subject.

**Recorded for the supervisor, not decided by this lane:** whether the *rest* of
Case 4 — the 8-cell module, the cooling channel, the spatial and temporal `G`
triples — should open a new campaign folder is a **structural question for the
supervisor and ultimately Sanaa**, and this document does not answer it. It
matters not at all to T20, because **T20 contains no battery-module geometry**:
one rectangle, one imposed `h`, one source. Wherever the module rungs land, this
rung belongs on the T ladder.

**`scripts/check_filing.py` result on the chosen path** is recorded in §14.

---

## 1. THE TEMPLATE — the ten registered lines

Sanaa's 10-line form, recorded at `docs/LAB_STATE.md:653-655`: *"case, reference,
quantities, bands, ladder, decomposition seed, criteria"*, plus the cost
registration rule 12 makes non-optional and the ABSENT registry rule 2 requires.
Everything after this section is the derivation that produced these lines; **the
ten lines are the frozen content and nothing below may widen them.**

**1. CASE.** Solid-only transient conduction with a uniform internal source in a
single 2-D planar rectangle 100 mm (x) × 30 mm (y) × 1.000 m (z, `empty`),
representing ONE battery cell of Case 4 §4.2. Solver
**`chtMultiRegionFoam`** (OpenFOAM **v2606**, api `2606` patch `0`, read from
`/usr/lib/openfoam/openfoam2606/META-INFO/api-info`), run with
`regionProperties` = `fluid ()` / `solid (cellRegion)` — **zero fluid regions**.
Run root `verification/runs/T-family/T20_runs/`; seven cases named in §9.

**2. REFERENCE.** The closed-form lumped-capacitance solution with internal
generation, **derived in this document (§3) and re-derived independently in the
comparator, never transcribed from a page.** No paper is required and none is
cited as a source of constants. Precedent for deriving rather than retrieving an
EXACT referent: `T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md` §2.1, and
`exact_laminar_pipe.py` / `exact_t9a.py` / `exact_t10a.py` on disk. Rule 15
governs *retrieved* documents; a derivation transcribes nothing and so can
inherit no transcription error.

**3. QUANTITIES.** Two independent readers of the same solution, with **different
pre-derived systematic biases** (§4.4), plus one balance instrument:

| id | quantity | read from |
|---|---|---|
| **Q1** | volume-mean temperature of the solid region, `T_mean(t)` | `internalField` of `<t>/cellRegion/T`, cell-volume weighted |
| **Q2** | area-mean temperature on the two convecting patches, `T_surf(t)` | `boundaryField` entries of `<t>/cellRegion/T` on `channelFaceLo`, `channelFaceHi`, face-area weighted |
| **Q3** | cumulative energy-balance closure ratio `C(t)` | `Q1`, `Q2` and the registered source; definition in §7.2 |

Sample times **t = τ, 2τ, 3τ = 1500, 3000, 4500 s exactly**, each an exact integer
multiple of every registered time step (§6.3).

**4. BANDS.** All bands are **1 % of the ANALYTIC RISE `(T_exact − T_inf)`, not
of absolute `T`** — the directive's *"within 1 %"* is meaningless read against a
293 K absolute temperature, and the difference is a factor of ~100. In Kelvin,
frozen:

| sample | analytic rise (K) | **band, ±K** | **band, ±mK** |
|---|---:|---:|---:|
| t = τ | 1.896361676 | 0.0189636 | **±18.9636** |
| t = 2τ | 2.593994150 | 0.0259399 | **±25.9399** |
| t = 3τ | 2.850638795 | 0.0285064 | **±28.5064** |

Applied to **Q1 and Q2 separately**, on the finest temporal level only.
Additional frozen bands: temporal observed order **p ∈ [0.85, 1.15]**; temporal
**GCI_fine < 0.5 %** of the rise; spatial invariance **≤ 0.1 × band**; lumped
validity **(T_max − T_min)/(T_mean − T_inf) ≤ 0.01** at 3τ; unplanted balance
closure **|C − 1| ≤ 0.02**; planted balance response **C_planted − C_unplanted ∈
[0.095, 0.105]**.

**5. LADDER.** The refined dimension of this rung is **TIME**, not space.
Temporal triple **Δt = 6.0 / 3.0 / 1.5 s**, refinement ratio **r = 2**, on the
fixed 240-cell mesh, `endTime` 4500 s = 3τ. Spatial dimension held at one level
and checked for **invariance** rather than refined, with the reason derived in
§5.2 and the rule-5 consequence registered in §5.3. One additional level at the
**module's own step**, Δt = 0.01 s (§6.4).

**6. DECOMPOSITION SEED.** **Serial, 1 rank. `numberOfSubdomains 1`, no
`decomposeParDict`, `decomposePar` is not run, the solver is invoked directly and
not through `mpirun`.** There is no partitioner, therefore no seed. *This line is
filled because the form requires it, not because the value is in doubt* — at 240
cells decomposition would cost more than it saves and would introduce a
determinism question this rung has no need to answer. `ranks = 1` is the multiplier
used in every core-minute figure in §11.

**7. CRITERIA.** In this order, and the order is one-way:
(i) **strict completion** (`CLAUDE.md` rule 4, transient form in §8) — any case
failing any conjunct gets no marker and **the whole rung is `NOT A RESULT`**, the
comparator refusing to grade a partial rung;
(ii) **instrument admission** — the planted-zero control of §7.1 must PASS on
every reader, and a refusal is `exit 2`, never a degraded grade;
(iii) **temporal triple classification** (`CLAUDE.md` rule 5) — non-`CONVERGING`
⇒ `NOT A RESULT` whatever the value says;
(iv) **band** — inside ⇒ `PASS`, outside ⇒ `GATE FAIL`, GCI printed beside every
row.
No verdict is assigned by this document and none may be assigned by the lane that
runs it.

**8. COST.** POINT **1.956 core-min**, CAP **16.0 core-min** (hard; an overrun
**stops the run** and does not get a new budget). USD **$0.00167 point /
$0.01368 cap, DERIVED NOT MEASURED**. Rate provenance, the two-term model and the
per-case caps are in §11.

**9. ABSENT REGISTRY** (rule 2's freeze condition, **measured in the writing
invocation at 2026-08-30T23:26:41Z, under a live planted control**):
`verification/runs/T-family/T20_runs/` **does not exist**, and each of the seven
registered case directories `T20_LC_c`, `T20_LC_m`, `T20_LC_f`, `T20_LC_Sc`,
`T20_LC_Sf`, `T20_LC_D`, `T20_LC_P10` returned **ABSENT**. **The zero was
planted** (`CLAUDE.md` rule 3): the same reader, in the same invocation, returned
**non-ABSENT** on a scratch directory created for the purpose and on the existing
`verification/runs/T-family/T17_runs/`, and **ABSENT** on a sibling of the
scratch directory that was not created. **Zero core-minutes have been spent on
this rung.** This measurement must be **re-taken in the committing invocation**;
the reading above is 23:26:41Z evidence and is not transferable to a later commit.

**10. AUTHORISATION.** This document authorises **no solve**. It becomes binding
only on the supervisor's freeze commit, and the comparator is hashed against its
committed blob before any grading (`VERIFICATION_CHARTER.md` §2d,
`scripts/check_comparator_freeze.py`).

---

## 2. THE FINDING THIS RUNG WAS WRITTEN TO RESOLVE

The supervisor's brief carried a defect in the directive's own gate and asked
that it be re-derived rather than inherited. **It reproduces exactly, and a
second and more binding defect was found underneath it.**

### 2.1 The supervisor's finding reproduces, every figure

With the directive's cell (`ρ` 2500, `c_p` 1000, 100 mm × 30 mm × unit depth) and
both 100 mm faces convecting:

`V` = 3.000e-03 m³/m, `A` = 0.2 m²/m, `L_c` = `V/A` = 0.015 m, `ρ c_p V` = 7500
J/K per metre depth, so **`τ` = `ρ c_p V/(h A)` = 37500/h s** — the supervisor's
figure, reproduced.

| h (W/m²K) | τ (s) | **3τ (s)** | over 900 s? |
|---:|---:|---:|---|
| 10 | 3750.0 | **11250.0** | yes, 12.5× |
| 25 | 1500.0 | **4500.0** | yes, 5.0× |
| 50 | 750.0 | **2250.0** | yes, 2.5× |
| 100 | 375.0 | **1125.0** | yes, 1.25× |

**Every one of the four reproduces to the digit.** The directive's gate
(agreement at τ, 2τ, 3τ) is **not evaluable inside its own 900 s duration for any
realistic air-side `h`.** The two-sided window also reproduces exactly:
`3τ ≤ 900 s` ⇒ **h ≥ 125.0**; `Bi = h L_c/k < 0.1` at `k` = 200 ⇒
**h < 1333.33**. And at h = 125 the steady rise `P/(hA)` = 15/(125 × 0.2) =
**0.600 K** with a 1 % gate of **6.0 mK** — the supervisor's figure, reproduced.

Sample fractions, reproduced: `1 − e⁻¹` = **0.632120559**, `1 − e⁻²` =
**0.864664717**, `1 − e⁻³` = **0.950212932**.

**Nothing of the supervisor's did not reproduce.** One clarification is recorded
rather than a correction: at h = 125 the Biot number is **0.009375**, an order
*below* the 0.1 ceiling — the lower end of the window is set by the clock, not by
`Bi`, and `Bi` is nowhere near binding there. That matters for §2.2.

### 2.2 The second defect: **`Bi < 0.1` is too loose for a 1 % gate, and the
directive's two constraints are inconsistent with each other**

`Bi < 0.1` is the textbook lumped-validity rule of thumb. It is a **~5 %**
criterion. **The directive gates at 1 %.** Derived, not asserted:

For a plane wall of half-thickness `L`, uniform generation `q'''`, symmetric
convection, the steady profile is
`T(y) − T_surf = (q'''/2k)(L² − y²)`, whose **volume mean exceeds the surface
value by exactly `q'''L²/(3k)`**, while the lumped model's surface excess is
`q'''L/h`. Their ratio is

    (T_mean − T_surf)/(T_surf − T_inf) = h L/(3k) = **Bi/3**

so **the lumped referent under-predicts the volume-mean rise by a fraction Bi/3**.
Against a 1 % band:

| Bi | Bi/3 | fraction of the 1 % band consumed by model bias alone |
|---:|---:|---:|
| 0.100 (the directive's ceiling) | 3.33 % | **333 % — the gate cannot pass** |
| 0.030 | 1.00 % | 100 % — exactly at the band |
| 0.009375 (h = 125, the 900 s point) | 0.3125 % | 31.3 % |
| **0.001875 (h = 25, registered)** | **0.0625 %** | **6.25 %** |

**A referent whose own modelling error is three times the band is not an exact
referent.** Registering h anywhere near the directive's `Bi` ceiling would have
produced a `GATE FAIL` caused entirely by the choice of `h`, and the failure would
have looked like a solver defect. **This is the substantive repair, and it is a
registration choice, not a physics change**, exactly as the supervisor framed it:
`h` is *imposed* in this control and the directive never pins it.

### 2.2a **THE SUPERVISOR'S WINDOW IS WITHDRAWN AS UNSAFE — recorded at their
instruction, because the next reader needs to know**

The brief that commissioned this rung carried the feasible window
**`125 ≤ h ≤ 1333 W/m²K`**, derived from `3τ ≤ 900 s` and `Bi < 0.1`. **That
window is wrong, and wrong in the dangerous direction.** The supervisor
re-derived the §2.2 result independently in sympy rather than accept it —
`T(y) = (L²q + 2T_s k − q y²)/(2k)`, giving `T_mean − T_surf = qL²/(3k)`,
**difference from this document's claim identically 0**, and
`bias/rise = Lh/(3k) = Bi/3` exactly — and **withdrew their own window**:

> *"So my `125 <= h <= 1333` window was wrong, and wrong in the dangerous
> direction: it would have produced a GATE FAIL caused entirely by my choice of
> `h`, presenting as a solver defect. Record that plainly in the document as the
> supervisor's corrected figure — not as a courtesy, because the next reader
> needs to know the window in my brief is unsafe."*

**`Bi = 0.030` is where the model bias exactly equals the band.** Any registration
of this control that takes `h` from the withdrawn window without also shortening
the band or raising `k` is **unsafe and must not be built.** The window as
corrected is bounded above by accuracy (`h ≤ 400` for `Bi ≤ 0.03`, and far lower
for real margin), not by `Bi < 0.1`; T20 registers **h = 25** and buys a 16×
margin.

### 2.3 The tension the supervisor flagged, and why it decomposes into two
independent knobs

The brief warned that *"raising `h` shortens τ AND shrinks ΔT simultaneously"*.
That is true of the **absolute** band and false of the **model-bias fraction**,
and separating the two is what makes the registration close:

- **`h` alone sets the model-bias fraction.** `bias/band = (Bi/3)/0.01 = 2.5e-3 h`
  — **independent of `q'''`**, because bias `= q'''L²/(3k)` and band
  `= 0.01 q'''L_c/h × f(t)` both scale linearly in `q'''`, so `q'''` cancels.
- **`q'''` alone sets the band in Kelvin.** It moves the absolute tolerance
  against the numerical noise floor and the field write precision, and moves
  nothing else.
- **`h` alone sets the clock**, `3τ = 112500/h` s.

So `h` is pinned by the *accuracy* requirement and the *duration* requirement
together, and `q'''` is then free to buy absolute margin. That decomposition is
the reason the registered point below is comfortable in both directions at once.

---

## 3. THE EXACT SOLUTION, AND ITS VERIFICATION

### 3.1 The statement

Lumped body, volume `V`, surface `A` exchanging with an ambient at `T_inf`
through a constant coefficient `h`, uniform volumetric generation `q'''` switched
on as a step at `t = 0`, initial temperature `T(0) = T_inf`:

    ρ c_p V dT/dt = q''' V − h A (T − T_inf)

    **T(t) = T_inf + (q''' V/(h A)) (1 − exp(−t/τ)),   τ = ρ c_p V/(h A)**

Written with `L_c = V/A` the amplitude is `q''' L_c/h` and `τ = ρ c_p L_c/h`;
both forms are used below and they are identical.

### 3.2 Verification — the supervisor's own symbolic check, cited, not redone

`SUPERVISION_CHARTER.md` §3 makes big-claim verification the supervisor's
personal, non-delegable act; the check below **was done by the supervisor and is
cited here as theirs**, not re-derived by this lane:

> Solving `rho*cp*V dT/dt = q'''*V - h*A*(T - T_inf)` with `T(0) = T_inf` in
> sympy returns **exactly** the directive's claimed form. **Difference
> identically 0.** The decay constant is exactly `tau = rho*cp*V/(h*A)` as
> claimed. **The directive's formula is CORRECT.**

The gate sample fractions, from the same check and re-evaluated independently in
the derivation of §2.1:

| n | `1 − e⁻ⁿ` |
|---|---|
| 1 | **0.632120558829** |
| 2 | **0.864664716763** |
| 3 | **0.950212931632** |

### 3.3 Under exactly what assumptions it is exact

Uniform and constant `h` and `T_inf`; constant `ρ`, `c_p`; spatially uniform,
time-constant `q'''`; no radiation; no phase change; uniform initial temperature
equal to `T_inf`; **and a spatially uniform body temperature, which is the
approximation the whole rung is built to keep small.** The departure from the
last assumption is not waved at — it is **derived, signed and predicted** in §4.4
and it is the discriminating structure of the gate.

**Geometric exactness.** With the two 30 mm end faces adiabatic, the two 100 mm
faces carrying identical uniform `h`, the source uniform and the front/back
patches `empty`, the solution of the *full* PDE is **exactly one-dimensional in
y** and uniform in x. The 1-D analysis of §4.4 is therefore not an approximation
of the registered geometry; it is that geometry's exact solution.

---

## 4. THE REGISTERED POINT — h, q''', k, duration, with the arithmetic

### 4.1 What is kept from the directive and what is chosen

| symbol | value | source |
|---|---:|---|
| ρ | 2500 kg/m³ | directive §4.2, **kept** |
| c_p | 1000 J/kgK | directive §4.2, **kept** |
| k | **200 W/mK**, isotropic | directive §4.6, **kept** — see §4.2 |
| q''' | **5000 W/m³** | directive §4.3's takeoff value, **kept**: `P_takeoff` 15 W per cell ÷ `V` 3.000e-03 m³/m = 5000 W/m³ exactly |
| T_inf, T(0) | **293 K** | directive §4.3, **kept** |
| geometry | 100 × 30 mm × 1.000 m | directive §4.2, **kept** |
| **h** | **25 W/m²K** | **CHOSEN HERE.** The directive imposes `h` and never pins it |
| **endTime** | **4500 s** | **CHOSEN HERE**, = 3τ exactly. The control's duration need not be the module's 900 s; it is a separate one-cell configuration |

### 4.2 Why `k` is kept at 200 rather than raised

Raising `k` is the other way to shrink `Bi`, and it would let h = 125 and a 900 s
run coexist with a small bias. It is **rejected** because the directive states
`k = 200` explicitly and gives its *reason* (`Bi < 0.1`); the reason is what
proved insufficient, not the value. Keeping the one number the directive pinned
and moving the two it left free (`h`, duration) is the narrower change and the one
easier to audit. **Recorded as a rejected alternative, not omitted.**

### 4.3 The arithmetic that pins h = 25, q''' = 5000, endTime = 4500 s

    L_c = V/A = 3.000e-03/0.2                       = 0.015 m
    L    = half-thickness = 0.030/2                 = 0.015 m   (equals L_c, as it must for a slab)
    τ    = ρ c_p L_c/h = 2500·1000·0.015/25         = **1500.0 s**
    3τ   = **4500.0 s**  ⇒ endTime = 4500 s, and t = τ, 2τ, 3τ all land inside the run
    Bi   = h L_c/k = 25·0.015/200                   = **1.875e-03**
    Bi/3                                            = **6.25e-04**  (0.0625 % model bias)
    ΔT_ss = q''' L_c/h = 5000·0.015/25              = **3.000 K**
    α    = k/(ρ c_p) = 200/2.5e6                    = 8.0e-05 m²/s
    t_cond = L²/α = 2.25e-04/8.0e-05                = **2.8125 s**   (τ/t_cond = 533×)

Constraint check, both sides:

- **Duration**: 3τ = 4500 s ≤ endTime 4500 s. **Met with equality by construction.**
- **Lumped validity against the 1 % band**: bias/band = 2.5e-3 × 25 = **0.0625**,
  i.e. the model bias eats **6.25 % of the band** at 3τ (6.6 % by the exact
  table in §4.5). **Met with 16× margin.**
- **`Bi` against the directive's own ceiling**: 1.875e-03 ≪ 0.1. **Met with 53×
  margin.**
- **Physical plausibility, a bonus and not a constraint**: 25 W/m²K is a
  perfectly ordinary forced-air coefficient, so the control sits inside the range
  the module's channel will actually produce rather than at a numerically
  convenient fiction.

### 4.4 The resolution consequence, in Kelvin — and the discriminating structure

**The 1 % band is 19–29 millikelvin.** That is the number the brief demanded be
stated absolutely rather than as a percentage, and it drives three registered
consequences:

| sample time | analytic rise | **band ±** | in mK |
|---|---:|---:|---:|
| τ = 1500 s | 1.896361676 K | 0.018964 K | **±18.96 mK** |
| 2τ = 3000 s | 2.593994150 K | 0.025940 K | **±25.94 mK** |
| 3τ = 4500 s | 2.850638795 K | 0.028506 K | **±28.51 mK** |

1. **`writePrecision 12` is REGISTERED, `writeFormat ascii`.** OpenFOAM's default
   `writePrecision 6` is **significant figures**, so a 295 K field carries three
   decimals — **1 mK exactly**, which is **5.27 % of the TIGHTEST band**
   (1 mK / 18.9636 mK at τ). *The tightest band is the one that can be lost, so
   it is the one quoted; against the 3τ band the same 1 mK reads a more
   comfortable 3.5 %, and quoting that instead would understate the hazard.* At
   12 significant figures the write resolution is ~1e-10 K and contributes
   nothing. **A gate this tight can be lost in the file format, and this is the
   line that prevents it.**
2. **Solid energy residual `1e-10`** per outer iteration (tighter than the
   directive's `1e-8` for the module), so the iterative contribution sits three
   orders below the band.
3. **The two readers Q1 and Q2 carry DIFFERENT pre-derived biases**, and this is
   the rung's anti-degeneracy control:

       T_surf(t) follows the lumped solution EXACTLY (bias ≈ 0)
       T_mean(t) = T_lumped(t) + q'''L²/(3k) = T_lumped(t) + **1.875 mK**, constant

   Derivation: with the internal parabola quasi-steady (established in
   ~3 t_cond ≈ 8 s, against τ = 1500 s), the exact energy balance
   `ρ c_p V dT_mean/dt = q'''V − hA(T_surf − T_inf)` combined with
   `T_mean = T_surf + q'''L²/(3k)` — a **constant** offset because `q'''` is
   constant — gives `ρ c_p V dT_surf/dt = q'''V − hA(T_surf − T_inf)`, which *is*
   the lumped equation. So **Q2 is unbiased and Q1 carries a constant +1.875 mK,
   independent of time after the first ~8 s.**

   **REGISTERED PREDICTION, before any solve:** the Q1 residual is **positive**
   and the Q2 residual is **negative** (Euler lag only), and **they must differ**.
   *If Q1 and Q2 return the same bias, the derivation is wrong or the two readers
   are reading the same object twice*, and that is a finding about the instrument,
   not about the solver.

### 4.5 The full error budget, derived before the run

Implicit Euler's exact discrete solution of `dT/dt = (T_ss − T)/τ` is
`θ_n = 1 − (1 + Δt/τ)^{−n}`, which **lags** the exact `1 − e^{−nΔt/τ}`. Evaluated
at the registered levels (all figures below are computed, not estimated):

| Δt | θ error at τ | at 2τ | at 3τ | worst, in mK |
|---:|---:|---:|---:|---:|
| 6.0 s | −0.11620 % | −0.06257 % | −0.03145 % | **−2.204 mK** |
| 3.0 s | −0.05815 % | −0.03129 % | −0.01572 % | −1.103 mK |
| **1.5 s (graded)** | **−0.02909 %** | −0.01565 % | −0.00786 % | **−0.552 mK** |
| 0.01 s | −0.00019 % | −0.00010 % | −0.00005 % | −0.004 mK |

**Budget on the graded level Δt = 1.5 s:**

| term | Q1 (mean) | Q2 (surface) |
|---|---:|---:|
| Euler temporal lag at τ | −0.552 mK | −0.552 mK |
| lumped model bias | **+1.875 mK** | **≈ 0** |
| write precision (`writePrecision 12`) | < 1e-7 mK | < 1e-7 mK |
| iterative residual at 1e-10 | ≪ 0.01 mK | ≪ 0.01 mK |
| **predicted net residual at τ** | **+1.323 mK** | **−0.552 mK** |
| **band at τ** | ±18.964 mK | ±18.964 mK |
| **margin** | **14.3×** | **34.4×** |
| **predicted net residual at 3τ** | **+1.651 mK** | −0.224 mK |
| **band at 3τ** | ±28.506 mK | ±28.506 mK |
| **margin** | **17.3×** | 127× |

These six predicted residuals are **registered as predictions**, reported beside
the measured values, and are **not** gates — the gate is the ±1 % band. A measured
residual inside the band but far from its prediction is a **reported finding**
about the derivation, and the results record must say so rather than pass it over.

---

## 5. THE LADDER — why it is temporal, and how rule 5 is applied

### 5.1 The temporal triple

Δt = **6.0 / 3.0 / 1.5 s**, r = 2, on the fixed 240-cell mesh, endTime 4500 s.
Every sample time is an exact integer number of steps at every level: 1500/6 =
250, 1500/3 = 500, 1500/1.5 = 1000. **No interpolation in time is performed at
any level** — a sampled value is a written time, never an interpolant.

Roache classification and GCI at `F_s = 1.25` are applied to this triple, in
`CLAUDE.md` rule 5's order. **Pre-computed from the exact discrete solution, so
the expected outcome is on the record before the run:**

| sample | p (observed) | GCI_fine | GCI in mK | monotone |
|---|---:|---:|---:|---|
| τ | 0.998200 | 0.036430 % | 0.691 | yes |
| 2τ | 0.999278 | 0.019578 % | 0.508 | yes |
| 3τ | 1.000357 | 0.009823 % | 0.280 | yes |

Registered band **p ∈ [0.85, 1.15]**, centred on the **1.0 that `ddtSchemes
default Euler` must give**. Registered **GCI_fine < 0.5 %** of the rise.

**THE DIRECTIVE'S `p ∈ [1.3, 2.5]` IS REJECTED, AND THIS IS THE THIRD OF SANAA'S
CONSTANTS THAT DID NOT SURVIVE CHECKING.** The directive's preamble instructs
that *"the constants written here are to be checked, not trusted"*; three have now
failed that check in this rung alone:

| # | the directive's constant | what checking found |
|---|---|---|
| 1 | the 900 s duration, with a gate at τ, 2τ, 3τ | **3τ exceeds 900 s for every realistic air-side `h`** (§2.1) |
| 2 | `Bi < 0.1` as the lumped-validity criterion | **too loose for its own 1 % band by 3.33×** (§2.2) |
| 3 | **`p ∈ [1.3, 2.5]`** | written for Cases 1–3's **steady spatial** ladders. Applied to a **first-order-in-time** ladder it **fails a correctly working scheme**: `Euler` must give p ≈ 1.0, which is outside [1.3, 2.5]. A band that a correct solver cannot pass is not a gate, it is a trap |

The substitution is deliberate, is stated rather than absorbed, and is exactly
what the directive asked for.

### 5.2 Why space is NOT refined, derived in advance

At `Bi` = 1.875e-03 the steady internal field is a **quadratic in y and uniform
in x**, and the second-order finite-volume Laplacian integrates a quadratic
**exactly** on a uniform mesh. A spatial triple would therefore return three
identical values and classify **`EXACT`** — which under rule 5 is
`NOT A RESULT`, for a reason that is physics rather than a defect. **Registering
that expectation before the run is the whole point; discovering it afterwards
would be indistinguishable from an escape hatch.**

Space is instead checked by **invariance**, which is the stronger statement here:
runs `T20_LC_Sc` (60 cells, 10 × 6) and `T20_LC_Sf` (960 cells, 40 × 24) at the
graded Δt must agree with `T20_LC_f` (240 cells, 20 × 12) at 3τ to within
**0.1 × band = 2.85 mK**, with the **prediction that they agree to < 1e-6 K**.

**And the failure direction is registered one-way:** if spatial invariance fails,
the field is not lumped, therefore **the lumped referent's validity assumption is
violated and Q1/Q2 become `NOT A RESULT`** — not `GATE FAIL`. A gate may only turn
a PASS or GATE FAIL *into* NOT A RESULT, never the reverse.

A direct measurement of the lumped assumption is registered beside it:
**(T_max − T_min)/(T_mean − T_inf) at 3τ ≤ 0.01**, predicted **9.375e-04** (the
centre-to-surface excess is `q'''L²/(2k)` = 2.8125 mK against a 3.0 K rise).

**Why the invariance limb carries a one-way `NOT A RESULT` and not a `GATE FAIL`
— T16 is the precedent, ruled tonight.** Verification ruled **T16
`NOT A RESULT` at commit `df69751b`** on ground **(b), the REFERENT and not the
threshold**, and **refused any relaxation of the 1e-06 tolerance**. The reasoning
transfers directly: T16's departure from linearity **itself mesh-converges, at
p = 1.404, to a NON-ZERO limit of −7.15e-05 — 71× the tolerance** — and *"a
quantity that mesh-converges to a non-zero value is a PHYSICAL FEATURE OF THE
SOLUTION, not numerical error, and refining the mesh will never reduce it."*
**A referent's validity is itself a physical claim that the ladder can falsify.**
T20's lumped referent is valid only while the body is lumped; if the invariance
limb or the `(T_max − T_min)` measurement says it is not, **the referent has been
falsified and no threshold may be moved to rescue the row** — the rows become
`NOT A RESULT`, which is why the consequence is registered here, before the run,
and one-way.

### 5.3 The rule-5 question this rung REFERS and does not rule

`CLAUDE.md` rule 5 says *"a row whose **grid** triple is not `CONVERGING` is
`NOT A RESULT`."* This rung's discretisation error lives in **time**, and its
spatial triple is `EXACT` by construction (§5.2). This lane therefore registers
its reading — *rule 5 is applied in full to the temporal triple, and the spatial
triple is computed, classified and reported* — and **REFERS to verification**,
before the freeze, the question of whether rule 5's "grid triple" reads onto a
temporal ladder for a rung whose spatial discretisation is exact.

**Registered in advance and one-way, so there is no later incentive to re-read
it:** if verification rules that an `EXACT` spatial triple forces the rows to
`NOT A RESULT`, **this rung reports `NOT A RESULT` and that outcome is accepted
without appeal.** The referral is not a request for relief.

**The rung FREEZES WITH THE REFERRAL OPEN, deliberately, on the supervisor's
instruction.** It does not wait for the ruling. *A referral registered before
compute cannot be fitted to an answer afterwards*, and a referral held back until
the ruling is known is worth nothing, because by then the answer is available to
shape it.

---

## 6. CONFIGURATION, AND WHAT WAS VERIFIED ON THIS BOX RATHER THAN RECALLED

Every item below was checked against the installed tree at
`/usr/lib/openfoam/openfoam2606`, not recalled. **All checks are source-tree
presence checks; none is a completed run**, and §13 records that limitation.

| registered feature | verified how | finding |
|---|---|---|
| **OpenFOAM v2606** | `META-INFO/api-info` | `api=2606`, `patch=0`. **CONFIRMED** |
| **`chtMultiRegionFoam`** | binary present in `platforms/*/bin` | **CONFIRMED** (`chtMultiRegionSimpleFoam`, `solidFoam` also present) |
| **solid-only, zero fluid regions** | OpenFOAM's own shipped test case `applications/test/multiWorld/chtMultiRegionSimpleFoam/solid/constant/regionProperties` contains literally `regions ( fluid () solid (bottomSolid) )` | **CONFIRMED as a supported configuration by upstream's own test asset**, not by inference |
| **`externalWallHeatFluxTemperature`, `mode coefficient`** | `src/thermoTools/derivedFvPatchFields/externalWallHeatFluxTemperature/…H`, Usage block: `mode 'power'/'flux'/'coefficient'`, `h [W/m²/K]`, `Ta [K]`, `kappaMethod` inherited from `temperatureCoupledBase` | **CONFIRMED.** `h` accepts a `PatchFunction1`, `Ta` a `Function1` |
| **`scalarSemiImplicitSource`** | `src/fvOptions/sources/general/semiImplicitSource/SemiImplicitSource.H` | **CONFIRMED**, with `volumeMode specific` (values per m³) |
| **`Function1` table source** | `SemiImplicitSource.H` Usage block shows `explicit table ((0 0) (5 30.7))` under the v2206+ `sources` dict, and `Su table (…)` under the legacy `injectionRateSuSp` dict; `src/OpenFOAM/primitives/functions/Function1/` contains `Table`, `TableFile`, `CSV`, `Polynomial`, `step`, ramps | **CONFIRMED both spellings.** T20 uses a **constant** source (a step at t = 0 is the initial condition, not a table); the table path is registered as confirmed **for Case 4's pulse rung**, which needs it |
| **anisotropic solid `kappa`** | `src/thermophysicalModels/solidSpecie/transport/const/constAnIsoSolidTransport.{H,C}`; registered in `solidThermos.C:73-83` as `heSolidThermo + pureMixture + constAnIsoSolidTransport + sensibleEnthalpy + hConstThermo + rhoConst`; consumed by `solidThermo::heatDiffusion()` at `solidThermo.C:299-306`, which branches `isotropic() ? fvm::laplacian(betav*alpha(),h) : fvm::laplacian(betav*aniAlpha(),h)`; `heSolidThermo.H` carries `aniAlpha`, the anisotropic-`Kappa` accessor and a **coordinate system** member | **AVAILABLE at v2606 — see §6.1** |

### 6.1 The anisotropy finding — the directive's escape clause is not needed

Directive §4.2 permits *"if the anisotropic path is not available in the chosen
solver at v2606, run isotropic k = 3 W/mK and DISCLOSE"*. **The condition does not
hold: the anisotropic path IS present at v2606** and is reached by
`chtMultiRegionFoam`'s own solid energy equation — `solveSolid.H` builds
`fvm::ddt(betav*rho,h) − thermo.heatDiffusion(betav,h) == fvOptions(rho,h)`, and
`heatDiffusion` is the function that carries the isotropic/anisotropic branch.
**So Case 4's module rungs should register `constAnIsoSolidTransport` with
`k_in-plane` 25 / `k_through-plane` 1 W/mK and a per-region coordinate system,
and the isotropic k = 3 fallback should NOT be taken on availability grounds.**

**Honest limit on that finding:** this is a **source-tree and registration-table
reading**, not a run. Anisotropic `kappa` additionally requires a coordinate
system in the region's thermophysical properties, and whether that composes
cleanly with `chtMultiRegionFoam`'s region loop on this build is **not
demonstrated here**. The claim registered is *available and reachable*, not
*proven to run*. **T20 itself uses isotropic k = 200 by choice, not by fallback** —
isotropy is the point of a lumped control.

### 6.2 Numerics, frozen

```
ddtSchemes        default Euler;              // first order, unconditionally stable
laplacianSchemes  default Gauss linear corrected;
gradSchemes       default Gauss linear;
solver (h)        PCG + DIC, tolerance 1e-12, relTol 0;
PIMPLE            nOuterCorrectors 2; nNonOrthogonalCorrectors 0;
                  residualControl h 1e-10;
relaxationFactors none (transient, converged per step);
writeControl      runTime;  writeInterval 150;   // 30 writes/run + the sample times
writeFormat       ascii;    writePrecision 12;   writeCompression off;
timeFormat        general;  timePrecision 12;
adjustTimeStep    no;       maxCo (undefined — no fluid region exists)
```

`DIC` is registered rather than `DILU` on T11's measured refusal
(`T11_PREREGISTRATION.md` §3.2); the matrix here is symmetric.
`writeCompression off` is registered so the field files are readable by the
comparator's plain-text reader without a decompression step in the planted-zero
path.

### 6.3 Mesh and boundary conditions

`blockMesh`, one block, uniform grading, one cell in z of thickness **1.000 m
exactly**.

| level | nx × ny | cells | Δy (mm) |
|---|---|---:|---:|
| `Sc` | 10 × 6 | 60 | 5.0 |
| **base (`c`,`m`,`f`,`D`,`P10`)** | **20 × 12** | **240** | **2.5** |
| `Sf` | 40 × 24 | 960 | 1.25 |

| patch | type | condition |
|---|---|---|
| `channelFaceLo`, `channelFaceHi` (the two 100 mm faces, A = 0.2 m²/m total) | wall | `externalWallHeatFluxTemperature`, `mode coefficient`, `h constant 25`, `Ta constant 293`, `kappaMethod solidThermo`, no `thicknessLayers`, `emissivity 0` |
| `endLo`, `endHi` (the two 30 mm faces) | wall | `zeroGradient` — adiabatic, per directive §4.2 "casing walls: adiabatic outer boundary" |
| `front`, `back` | empty | 2-D planar |

`0/cellRegion/T` uniform **293** everywhere. `fvOptions`:
`scalarSemiImplicitSource`, `volumeMode specific`, whole region,
`sources { h { explicit constant 5000; implicit none; } }` — **note the source is
applied to the energy variable `h` that `solveSolid.H` solves, not to `T`**, and
the comparator's balance instrument must use the same convention (§7.2).

### 6.4 The module-step regime row (`T20_LC_D`)

The graded ladder runs at Δt = 1.5 s while Case 4's module runs at **Δt = 0.01 s**
(directive §4.5). A control that never visits the module's step size verifies the
code path but not the regime. `T20_LC_D` closes that: **Δt = 0.01 s, endTime
300 s (= 0.2τ), 30 000 steps**, base mesh, graded on **Q2 only**.

Q2 only, and the reason is arithmetic rather than convenience: at t = 300 s the
analytic rise is `3.0 × (1 − e^{−0.2})` = **0.543808 K**, so the 1 % band is
**5.438 mK** — while Q1's constant model bias is 1.875 mK, i.e. **34 % of that
band**. Q2 is unbiased and its predicted residual there is **−0.0016 mK**. Q1 at
300 s is therefore **reported, not gated**, with its predicted +1.875 mK stated;
the reason it is not gated is written here so that it cannot later be read as a
row quietly dropped.

**This is the row to cut if the supervisor wants the cost down**: it is
**1.134 core-min of the rung's 1.956 POINT — 58 % of it.** Named explicitly so
the trade is visible.

---

## 7. THE INSTRUMENT CONTROLS

### 7.1 The planted-zero control — T17's construction, adopted deliberately

**Two of this lab's own controls have just been measured to be decided by
floating-point rounding:** T3's `passed = (seen >= PLANT − 1e-15)` on a ~300 K
field, where the operative window is **0.2082 ULP** and the outcome turns on the
sign of a ~7-ULP residual wiggle; and T15's `0.5*ref` threshold where `ref` **is
the statistic under test**. **T20 adopts neither.** It adopts
`verification/runs/T-family/T17_runs/analyse_t17.py:244-246` and `:262-270`
verbatim in structure, and the registered properties are:

1. **Copy first, never write into the case.** `shutil.copytree` into a scratch
   directory, and **REFUSE** if `os.path.realpath(dst)` resolves inside
   `os.path.realpath(case_dir)`.
2. **NEGATIVE ARM — the zero is MEASURED, and its threshold is ZERO.** The reader
   is run twice on **identical bytes**; `dneg = max |a − b|` must be **bitwise
   `0.0`**, and the control **REFUSES** ("the reader is NOISY") on anything else.
   *There is no absolute tolerance anywhere in the negative arm.* This is the
   clause T3 lacked.
3. **POSITIVE ARM — a multi-magnitude ladder, so the floor is MEASURED not
   assumed.** Magnitudes **(1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8,
   1e-9)** K are planted in turn, the field re-read through the **real** reader
   each time, `d = |stat(planted) − stat(base)|` recorded, and
   **`floor` = the smallest magnitude with `d > 0.0`**. The comparison against
   zero is `d > 0.0` — exact, no epsilon.
4. **REFUSE if `floor is None`** — no magnitude visible ⇒ the reader is **BLIND**.
5. **The only tolerance is RELATIVE**: **REFUSE if `seen[PLANT] < 0.1 × PLANT`**
   (L-340 sizing), with the message naming both `seen[PLANT]` and the magnitude
   that *was* visible.
6. **PLANT SIZED TO THE READER, which is where T3's sizing would have broken
   here.** Q1 is a **volume mean over 240 cells**; planting into one cell moves it
   by `PLANT/240`, which would fail clause 5 for a working reader. **Registered:
   for Q1 the plant goes into EVERY internal cell** so the expected shift is
   exactly `PLANT`; **for Q2 into every face value of both convecting patches** in
   the `boundaryField`, same reason. The number of values planted is recorded in
   the output.
7. **`PLANT = 1.234e-03 K`**, keeping the family's distinctive digits so it can
   never be mistaken for a physical value.
8. **A NEW REFUSAL, TIED TO THE GATE THIS INSTRUMENT SERVES — flagged by the
   supervisor as a LAB STANDARD IN EMBRYO, and recorded as such rather than as a
   local convenience.** In addition to clause 5: **REFUSE if
   `floor > 1.9e-04 K`** — one hundredth of the tightest registered band
   (18.9636 mK). *An instrument whose demonstrated resolution is not at least
   100× finer than the band it decides has no business deciding it.* T3's defect
   was precisely that its resolution was **tied to nothing**: an absolute
   `1e-15` on a ~300 K field, whose operative window is 0.2082 ULP and whose
   outcome turns on the sign of a ~7-ULP wiggle. **The general form — every
   planted-zero control's demonstrated detection floor must be bound to the band
   the instrument decides, by a stated ratio, and refuse otherwise — is proposed
   for the verification charter and is NOT ruled here.** It is registered as
   binding on T20 and offered upward; adopting it lab-wide is verification's
   call, not this rung's. Predicted floor at `writePrecision 12`: **≤ 1e-08 K**.
9. Original bytes restored from the in-memory copy, and the scratch tree removed
   in a `finally`.

### 7.2 The cumulative energy-balance instrument, and the planted +10 % source

Directive §4.6 second bullet. Definitions, per metre depth, evaluated at every
written time:

    E_src(t)    = q'''_REGISTERED · V · t                       (the registered rate, never the run's)
    E_stored(t) = ρ c_p V (T_mean(t) − T_mean(0))
    E_conv(t)   = ∫₀ᵗ h A (T_surf(t') − T_inf) dt'              (trapezoid over the written times)
    **C(t)      = (E_stored(t) + E_conv(t)) / E_src(t)**

`E_src` uses the **registered** `q'''` and not the value in the case's
`fvOptions`. That is what makes the planted arm visible: the instrument cannot
compensate for a source it is not told about.

- **Unplanted** (`T20_LC_f`): **|C(3τ) − 1| ≤ 0.02**, the directive's own 2 %
  cumulative-balance criterion. Predicted |C − 1| < 1e-3.
- **Planted** (`T20_LC_P10`): identical case with `fvOptions` explicit source
  `5500` (= 5000 × 1.10) and **nothing else changed**. The instrument, still told
  5000, must report **C_planted(3τ) − C_unplanted(3τ) ∈ [0.095, 0.105]**.
- **Both arms are read by the same instrument on the same code path**, and the
  planted arm is what proves the unplanted `C ≈ 1` is a **measurement and not a
  reader returning unity by construction.**

A `GATE FAIL` on either balance arm makes the balance row `GATE FAIL`; a
**refusal** of the planted arm (the instrument cannot see 10 %) is an
**instrument failure and the whole rung is `NOT A RESULT`** — an instrument that
cannot see a planted 10 % is not entitled to certify a 1 % agreement.

---

## 8. RULE 4 COMPLETION, IN ITS TRANSIENT FORM — and the open referral

`CLAUDE.md` rule 4 is **all-or-nothing**: a run failing any conjunct is not done,
and the comparator **refuses (exit 2) rather than degrades**. The six conjuncts,
and how each is evaluated for a solid-only transient case:

| # | conjunct | how it is evaluated here |
|---|---|---|
| 1 | **`rc = 0`** | captured **inside** the detached wrapper and written to `STATUS.<case>`. **Never around a `setsid` line** — `setsid timeout cmd` exits 0 for every outcome (recorded in this session's memory); the wrapper writes `rc=$?` immediately after the solver call, in the detached shell |
| 2 | **an `End` line** | `grep -c '^End$' log.solve` == 1 |
| 3 | **last time == `endTime`** | the numerically greatest time directory under `<case>/` equals **4500** (**300** for `T20_LC_D`), compared as a float with `timePrecision 12` |
| 4 | **fields present** | **`T` in `<endTime>/cellRegion/`.** The thermal family's list `T U p_rgh alphat nut k omega` **does not apply — there is no fluid region and those fields do not and must not exist.** The registered list for this rung is exactly `{T}`, and the check asserts presence of `T`, not absence of the others |
| 5 | **`ExecutionTime` count == `endTime`** | **evaluated as `count == round(endTime/deltaT)` — see §8.1** |
| 6 | **age guard** | every field at `endTime` **newer** than the case's own `0/cellRegion/T` by `st_mtime`. The launcher touches `0/cellRegion/T` last, so it dates the run that was allowed to produce the answer. A guard refuses a case where `0/` or any time directory already exists |

Registered step counts for conjunct 5, all exact integers:
`T20_LC_c` **750**, `T20_LC_m` **1500**, `T20_LC_f` / `T20_LC_Sc` / `T20_LC_Sf` /
`T20_LC_P10` **3000**, `T20_LC_D` **30000**.

### 8.1 The known hazard, declared and referred — NOT ruled on here

**Ansys measured tonight (commit `c03b6eb8`) that rule 4's `ExecutionTime count
== endTime` clause is satisfiable only with a FIXED time step**, and that VMFL069
fixed `deltaT` *in order to satisfy that bookkeeping clause* under
`adjustTimeStep no`, **guaranteeing divergence**. They have **REFERRED to
verification** whether the clause forbids adaptive time-stepping lab-wide.
**That referral is open and this document does not rule on it.**

**T20 is not in conflict with it, for an independent reason.** Directive §4.5
already requires *"fixed time step per level, no adaptive stepping on gated runs
(reproducibility)"* — so the fixed step here is a **physics-and-reproducibility**
requirement that arrived before the bookkeeping clause was consulted, not a step
chosen to satisfy the clause. Declared:

- **`adjustTimeStep no`, `deltaT` fixed per level at 6.0 / 3.0 / 1.5 / 0.01 s.**
- **Courant consequence: there is none, because there is no fluid.** `Co` is
  undefined in a region with no flux field; the directive's `max Co 1` binds
  Case 4's module rungs and not this one. The stability parameter that *does*
  exist is the cell Fourier number `Fo = α Δt/Δy²` = **19.2** at the graded level
  (α = 8.0e-05, Δy = 2.5 mm) — far above unity and **entirely safe, because
  implicit Euler is unconditionally stable.** It is stated rather than omitted so
  that no reader mistakes its absence for an oversight.
- **The one accuracy consequence of a large `Fo`, disclosed:** the internal
  conduction start-up has timescale `t_cond` = 2.8125 s, so at Δt = 6.0 s the
  **first ~2 steps do not resolve the establishment of the internal parabola.**
  That parabola is worth **1.875 mK in total** and is fully established by
  t ≈ 8 s, which is **0.0053 τ** — 187 times before the first sample. **No sample
  time is affected**, and the claim is quantified rather than waved through.
- **The clause as this rung evaluates it** is `ExecutionTime line count ==
  round(endTime/deltaT)`, which is **well-defined only because `deltaT` is
  fixed**. Under `adjustTimeStep yes` the step count is not predictable in advance
  and the clause **cannot be evaluated at all** — which is ansys's point, and it
  is theirs to press, not this rung's to settle.

---

## 9. THE REGISTERED RUN SET

| case | mesh | cells | Δt (s) | endTime (s) | steps | purpose | graded |
|---|---|---:|---:|---:|---:|---|---|
| `T20_LC_c` | base | 240 | 6.0 | 4500 | 750 | temporal triple — coarse | triple only |
| `T20_LC_m` | base | 240 | 3.0 | 4500 | 1500 | temporal triple — medium | triple only |
| **`T20_LC_f`** | base | 240 | **1.5** | 4500 | 3000 | temporal triple — fine; **the graded level** | **Q1, Q2, Q3** |
| `T20_LC_Sc` | coarse | 60 | 1.5 | 4500 | 3000 | spatial invariance | invariance |
| `T20_LC_Sf` | fine | 960 | 1.5 | 4500 | 3000 | spatial invariance | invariance |
| `T20_LC_D` | base | 240 | **0.01** | 300 | 30000 | module-step regime row | **Q2** (Q1 reported) |
| `T20_LC_P10` | base | 240 | 1.5 | 4500 | 3000 | planted **+10 %** source | **Q3 planted arm** |

Staging per the directive's preamble: **feasibility → physics → gate.** The
feasibility step is `T20_LC_c` alone (750 steps, ~0.08 core-min) and it answers
one question that source inspection cannot: **does `chtMultiRegionFoam` run to
completion with `fluid ()`?** If it does not, **the rung is `BLOCKED` on that
finding and `solidFoam` is registered as the alternative in a re-registration** —
not substituted silently, because `solidFoam` is *not* the solver Case 4's module
rungs use and swapping to it would quietly convert this from a machinery gate into
a different rung.

---

## 10. THE SELFTEST SPECIFICATION

The comparator is not written yet (this document does not authorise it); the
selftest it must carry is registered here so that it cannot be shaped to the
answer later. `python3 analyse_t20.py --selftest` must exercise, on **synthetic
forged trees only**:

**S1 — BOTH SIGNS of every drift.** For each gated row and each sample time, four
forged cases: residual `+1.5 × band`, `−1.5 × band`, `+0.5 × band`, `−0.5 × band`.
Required outcomes: **`GATE FAIL`, `GATE FAIL`, `PASS`, `PASS`.** *A one-sided
threshold passes a two-sided band only by luck; T15's `0.5*ref` is the failure
this limb exists to prevent.*

**S2 — BLIND-reader mutant must REFUSE.** `read_field` is monkey-patched to return
a constant vector independent of the file bytes. The planted-zero control must
**exit 2** with the **BLIND** message, and the selftest **fails if the comparator
produces any verdict at all.**

**S3 — NOISY-reader mutant must REFUSE.** `read_field` is patched to add one ULP
of jitter on the second call. The **negative arm** must fire ("the reader is
NOISY") on a non-zero `dneg`. *This is the limb T3 did not have.*

**S4 — UNDERSIZED-plant mutant must REFUSE.** The Q1 plant is patched to touch one
cell instead of 240. Clause 5 (`seen[PLANT] < 0.1 × PLANT`) must fire. *Proves the
sizing test is live, not decorative.*

**S5 — FLOOR-tied refusal must fire.** A forged field written at
`writePrecision 4` must drive the demonstrated floor above `1.9e-04 K` and
**REFUSE** under §7.1 clause 8.

**S6 — balance instrument sees the plant.** A forged pair of trees differing only
by a +10 % source must return `C_planted − C_unplanted` inside `[0.095, 0.105]`;
a forged pair differing by **0 %** must return a difference **`< 0.005`**. *Both
directions, so the instrument is shown able to report "no plant" as well as
"plant".*

**S7 — completion-rule limbs.** Six forged trees, each violating exactly one
conjunct of §8 (rc≠0; no `End`; last time 4494 ≠ 4500; `T` missing; 2999
`ExecutionTime` lines against a registered 3000; a field older than `0/cellRegion/T`).
Each must produce **`NOT A RESULT`** and no graded value.

### 10.1 **S8 — THE INVARIANCE LIMB. The new requirement, and the most valuable
line in this document.**

**REGISTERED, BINDING: no selftest limb of `analyse_t20.py` may read, `stat`,
`glob` or assert anything whatsoever about `verification/runs/T-family/T20_runs/`
or any other live run tree. Every limb operates on a synthetic tree it forges in
a scratch directory it creates and removes.**

**And the invariance is MEASURED, not promised.** `--selftest` runs its entire
limb set **twice** in one invocation:

- **pass A**, with a synthetic run root that is **empty**;
- **pass B**, with a synthetic run root **fully populated** — all seven case
  directories present, each with `0/`, time directories through `endTime`, `T`
  fields, `log.solve`, `STATUS.<case>` and `DONE.<case>`;

and **asserts the two limb-result structures are byte-identical**, failing with a
diff of the differing limbs if they are not.

**Why this is registered — the family is REAL, and it was demonstrated on a live
control, not counted.** `docs/DOCKET.md` **D574** records the defect class: a
selftest limb **with a built-in expiry keyed to the campaign's own progress**,
asserting that the live run tree holds no `DONE` marker. **A limb of that shape
is true at freeze and FALSE the moment the campaign succeeds.** It is then not a
check on the instrument at all: **it is a check on the calendar, and it passes
for exactly as long as the work has not been done** — worthless precisely when
the campaign's result needs defending, which is after it has run.

**The live control, driven by this lane rather than cited:**
`verification/runs/T-family/T19_runs/analyse_t19.py --selftest` was executed,
returned **rc = 0** and **`SELFTEST PASS (0 failed)`**, and among its passing
limbs printed **`[ok ] live tree, no DONE markers -> exit 2 REFUSE`**
(`analyse_t19.py:694`). `verification/runs/T-family/T19_runs/` currently holds
**zero `DONE` markers**. **So the limb passes today only because T19 has not
run**, and it is a member of the class by demonstration.

**MEMBERSHIP OF THE CLASS IS UNSETTLED, AND NO COUNT IS QUOTED HERE — including
this lane's own.** Three detectors have now produced three different sets:
D574's nine-with-eight-expired, a third reading of twenty-two, and this lane's
grep-based sweep which **found the limb in none of them and was simply blind** —
it searched for phrasings the limb does not use and returned a clean zero. *That
zero was not planted, and `CLAUDE.md` rule 3 is the reason it should never have
been written down as a finding.* **A count from an unproven detector is not a
measurement**, and the correction is recorded against this lane rather than
quietly dropped: the earlier draft of this section reported that the supervisor's
count "did not reproduce", when what had actually happened is that this lane's
detector could not see the thing. **S8 stands on the argument above and on the
one demonstrated member, not on any count.**

---

## 11. COST — rule 12

### 11.1 The rate, and its provenance stated honestly

**No measured rate exists for `chtMultiRegionFoam` on this box.** The nearest
measurement is **T17's**: `T17_CY_c`, 2 500 cells × 20 000 steps in **14 wall s**,
1 rank, and `T17_RESULTS.md` §9 establishes that it **ran alone** — 13 h 50 min
before any other T17 case started — so it is an **uncontended** reading. That
gives **2.80e-07 core-s per cell-step** for `laplacianFoam` on a 2-D structured
mesh, and it is consistent with T14's registered 1.64e-07 scaled by T17's measured
1.701× miss (1.64e-07 × 1.701 = 2.79e-07).

**A single per-cell-step rate is the wrong model at 240 cells**, and this family
has already measured that: `T11_RESULTS.md` records a ladder at **0.41×** its
POINT and attributes it to being *"overhead-dominated below ~1e3 cells"*. So the
registered model is **two-term**:

    cost_core_s = startup + N_steps × (t_overhead + rate × N_cells)

| term | value | provenance |
|---|---:|---|
| `rate` | **2.80e-07 core-s per cell-step** | **BORROWED, NOT MEASURED** — from T17's uncontended `laplacianFoam` reading. A different solver |
| `t_overhead` | **2.1e-03 core-s per step** | **ASSUMED, NOT MEASURED.** Derived as 3× T17's total 0.70 ms/step at 2 500 cells, the 3× being a **declared allowance** for `chtMultiRegionFoam`'s region loop, `thermo.correct()`, PIMPLE outer loop and per-step `Info` output. **This is the weakest figure in the registration and it is named as such** |
| `startup` | **3.0 core-s per case** | **ASSUMED** — mesh read, thermo construction, first write |
| `ranks` | **1** | registered, §1 line 6 |

T17's own lesson is the reason the cap is generous: **a borrowed rate was wrong by
1.70× on an uncontended box**, and that was a smaller extrapolation than this one.

### 11.2 POINT and CAP

| case | cells | steps | **POINT (core-min)** | per-case CAP |
|---|---:|---:|---:|---:|
| `T20_LC_c` | 240 | 750 | 0.0771 | 0.80 |
| `T20_LC_m` | 240 | 1500 | 0.1042 | 1.20 |
| `T20_LC_f` | 240 | 3000 | 0.1584 | 1.80 |
| `T20_LC_Sc` | 60 | 3000 | 0.1558 | 1.80 |
| `T20_LC_Sf` | 960 | 3000 | 0.1684 | 1.80 |
| `T20_LC_D` | 240 | 30000 | 1.1336 | 6.80 |
| `T20_LC_P10` | 240 | 3000 | 0.1584 | 1.80 |
| **TOTAL** | | **44 250 steps** | **1.9559** | **16.0 (hard)** |

**POINT 1.956 core-min. CAP 16.0 core-min = 8.18× POINT.** The **total cap
binds**; per-case caps are stated so a single runaway is stopped without waiting
for the total. **An overrun stops the run; it does not get a new budget**
(`COMPUTE_BUDGET_CHARTER.md`, `CLAUDE.md` rule 12).

**USD, DERIVED NOT MEASURED**, at the owner-stated **$0.0513/core-h**
(c7a.4xlarge, Sanaa 2026-08-21/22):

    POINT: 1.9559 core-min = 0.032598 core-h → **$0.00167**
    CAP:  16.0000 core-min = 0.266667 core-h → **$0.01368**

**`cost_basis`: DERIVED, NOT MEASURED.** `COMPUTE_BUDGET_CHARTER.md` §5 — **the
box cannot read its own billing**, so no dollar figure originating here is a
measurement, and a console figure supersedes it if one is ever obtained.

**Fraction of Case 4's 600 core-min family cap** (directive §4.7):
**POINT 0.326 %, CAP 2.667 %.** This rung costs a third of one percent of the
family's budget at the point estimate, and under three percent even at its hard
cap. It is, as the brief intended, **the cheapest and most independent thing in
Case 4.**

### 11.3 The calibration owed at completion

`CLAUDE.md` rule 12's estimate-versus-actual clause (Sanaa 2026-08-23) binds this
rung. At completion the results record must carry: actual core-minutes from the
`STATUS.*` files as `wall_s × ranks ÷ 60`, the **ratio actual/predicted**, the
attribution split between contention, waste and misprediction with **waste named
separately and never folded into the ratio**, and a row appended to
`docs/COST_CALIBRATION.md`. **`t_overhead` is the figure this rung exists to
calibrate**, and `T20_LC_c` — the feasibility case, running alone — is the clean
reading for it. *A completion report without this comparison is incomplete.*

---

## 12. THE VERDICT MAP

| row | quantity | verdict route |
|---|---|---|
| **V1** | Q1 `T_mean` at τ, 2τ, 3τ, `T20_LC_f` | completion → instrument → temporal triple → band |
| **V2** | Q2 `T_surf` at τ, 2τ, 3τ, `T20_LC_f` | same |
| **V3** | Q2 at t = 300 s, `T20_LC_D` (module step) | completion → instrument → band (no triple; single level, stated) |
| **V4** | Q3 balance, unplanted, `T20_LC_f` | `\|C − 1\| ≤ 0.02` |
| **V5** | Q3 balance, planted +10 %, `T20_LC_P10` | difference ∈ [0.095, 0.105]; a **refusal** here makes the **whole rung** `NOT A RESULT` |
| **P1** | lumped validity `(T_max−T_min)/(T_mean−T_inf)` at 3τ | ≤ 0.01 |
| **P2** | spatial invariance, `Sc`/`Sf` vs `f` | ≤ 0.1 × band; **failure ⇒ V1/V2/V3 become `NOT A RESULT`** |
| **P3** | no temperature below `T_inf` anywhere, any time | directive §4.6 physicality |
| **P4** | monotone rise in every cell under the constant source | directive §4.6 physicality |
| **R1–R6** | the six predicted residuals of §4.5 | **REPORTED beside the measured values, never gated** |

**No row may be re-read after the run.** A row not listed here is not a row.

---

## 13. DECLARED OMISSIONS AND ASSUMPTIONS

Each labelled, per the directive's common deliverable 7 (*"certificate draft per
case listing WHAT WAS NOT CHECKED"*).

1. **REPRESENTATIVE PROPERTIES, NOT A REAL CELL'S.** ρ 2500, c_p 1000 are the
   directive's declared representative values for a prismatic aviation cell. **No
   manufacturer's data was consulted, none is on this box, and nothing here is a
   claim about any real battery.** `k` = 200 W/mK is not a battery property at
   all — it is a **deliberate control value** chosen to make the body lumped.
2. **ISOTROPIC k, BY CHOICE AND NOT BY FALLBACK.** §6.1 records the measured
   finding that v2606 **does** provide anisotropic solid conductivity, so the
   directive's isotropic escape clause is not invoked. **Limit:** that finding is
   a source-tree reading, not a demonstrated run, and the coordinate-system
   composition with `chtMultiRegionFoam`'s region loop is **not verified**.
3. **RADIATION OFF — and the neglected term is NOT small. This is the largest
   declared omission in the rung and it is stated at its true size.**
   `emissivity 0` on the convecting patches; no radiation model. Bound on the
   neglected term at the run's own maximum surface temperature,
   T = 293 + 2.851 = 295.851 K against a 293 K enclosure, taking ε = 0.9:

       εσ(T⁴ − T_inf⁴)A = 0.9 × 5.67e-08 × (295.851⁴ − 293⁴) × 0.2
                        = **2.970 W/m**, against the source's 15 W/m
                        = **19.8 % of the source.**

   Equivalently `h_rad ≈ 4εσT̄³` ≈ **5.2 W/m²K** beside the imposed
   h = 25 W/m²K — **21 %**. **A physically realistic cell radiating to a 293 K
   enclosure at this coefficient would not follow the registered curve.**

   **Why the gate is nevertheless unaffected, stated precisely rather than
   waved:** this is an **EXACT-tier verification of code against the closed-form
   solution of the equations the code is solving**, and radiation is absent from
   **both sides** — from the case and from the referent. It is not an error term
   in the comparison; it is a statement that **T20 makes no validation claim
   about a real battery cell**, which §13.1 and §0.2 already say. **The cost is
   paid in physical realism and not in gate validity**, and it is a cost of
   choosing h = 25: at the 900 s point h = 125 the same bound would be ≈ 4 % of
   the source. **The results record and the Case 4 certificate draft must carry
   this 19.8 % figure**, not a reassuring one.
4. **2-D PLANAR.** `empty` front/back at 1.000 m depth. `V` and `A` both scale
   with depth so `L_c`, `τ` and every graded quantity are depth-invariant; the
   depth is registered only so the core-minute and energy figures reproduce.
5. **NO FLUID, THEREFORE NO CONVECTION MODEL.** `h` is imposed and uniform. **The
   rung says nothing about what `h` the real channel produces** — that is Case 4's
   module physics and this rung deliberately removes it.
6. **THE STEP SOURCE IS NOT THE PULSE.** Constant `q'''`, not the directive's
   60 s takeoff / 840 s cruise profile. The `Function1 table` path is **confirmed
   present** (§6) but is **not exercised here**; Case 4's pulse rung must exercise
   it and may not cite T20 as having done so.
7. **T(0) = T_inf EXACTLY.** The exact solution's amplitude form depends on it.
   A non-zero initial excess would add a decaying homogeneous term and is **not**
   registered.
8. **THE CONTROL'S Δt IS NOT THE MODULE'S, except in `T20_LC_D`.** The graded
   ladder runs 150× the module's step. `T20_LC_D` exists precisely so this
   omission is not total, and §6.4 states what it does and does not close.
9. **SOLVER-CLASS COST EXTRAPOLATION.** The rate is borrowed across solvers and
   `t_overhead` is assumed (§11.1). The cost figures are a **prediction with a
   named weak term**, not a measurement.

---

## 14. FILING

Path: **`docs/campaigns/T-family/T20_PREREGISTRATION.md`**, matching
`FILING_CHARTER.md` **R7** (`<RUNG>_<PURPOSE>.md` in the campaign directory) and
the regex `CAMPAIGN_RECORD_MD` in `scripts/check_filing.py`. Run root
**`verification/runs/T-family/T20_runs/`**, matching **R6** (run outputs under
`verification/runs/<CAMPAIGN>/`, never beside the prose). Comparator
**`verification/runs/T-family/T20_runs/analyse_t20.py`**, matching **R7**'s
`lower_snake.py` for helper code inside a campaign directory.

`python3 scripts/check_filing.py` result is recorded in the lane report
accompanying this draft.

---

## 15. WHAT THIS DOCUMENT DOES NOT DO

- It **does not authorise a solve**, does not enqueue, and does not create a queue
  entry. Freezing the gates and launching them are two separate acts and only the
  first has happened.
- It **does not write the comparator.** §7 and §10 are the specification the
  comparator must meet; the code is a separate act under a separate review, and
  the supervisor reads measurement-script diffs **as diffs**, personally.
- It **does not rule** on the `ExecutionTime`/adaptive-stepping referral (§8.1) or
  on the rule-5 temporal-triple question (§5.3). Both are referred to
  verification, and both registered outcomes are accepted in advance.
- It **does not decide** whether Case 4's module rungs open a new campaign folder
  (§0.3).
- It **files nothing anywhere.** `CLAUDE.md` rule 7 — submissions are parked, and
  nothing in this rung goes outside this box.

---

## 16. THE SUPERVISOR'S CHECK, DISCHARGED — and two corrections against the brief

`SUPERVISION_CHARTER.md` §3 check 4 (pre-registration **committed** before
compute) was discharged **personally** by the supervisor before this freeze:
nothing has run, the run root and all seven case directories are ABSENT under a
live planted control, and **zero core-minutes have been spent.** The registration
goes in **before** compute, which is the whole content of the check.

**Two corrections are recorded here rather than absorbed, both against the brief
that commissioned the rung:**

1. **The supervisor's `125 ≤ h ≤ 1333` window is WITHDRAWN as unsafe** (§2.2a),
   on their own independent sympy re-derivation, which returned this document's
   `Bi/3` result with **difference identically 0**.
2. **This lane's claim that the D574 count "did not reproduce" is WITHDRAWN**
   (§10.1). The count did not fail; **this lane's detector was blind**, and it
   returned an unplanted zero — the exact error `CLAUDE.md` rule 3 exists to
   prevent, committed by the same document that registers a planted-zero control
   with a measured detection floor. It is recorded because a correction against
   oneself in the frozen document is worth more than a clean-looking one.

**One correction the other way, against the supervisor and recorded for
symmetry:** their `writePrecision` estimate of 2.95e-3 K used a relative
`10^-(p-1)`; OpenFOAM's `writePrecision` is **significant figures**, so 295 K at
6 s.f. leaves three decimals = **1 mK exactly**. The `writePrecision 12`
registration is unaffected; the percentage quoted in §4.4 is now taken against the
**tightest** band (5.27 %), which is the one that can be lost.
