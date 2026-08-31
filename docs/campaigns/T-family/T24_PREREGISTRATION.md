# T24 — Case 3 motor-in-duct CHT: THE TWELVE POINTS T23 DEFERRED — pre-registration

> **THIS DOCUMENT IS FROZEN BY THE COMMIT THAT LANDS IT** (`CLAUDE.md` rule 2).
> After that commit no gate, threshold, cap or label below may change. A
> departure lands only as a dated addendum appended at the foot; originals are
> struck, never rewritten.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE
FAIL / NOT A RESULT / BLOCKED / PENDING.** No other word appears as a verdict
here, and **this document assigns no verdict** — it registers the gates a later
grading pass will assign one against.

---

## 0. WHAT THIS RUNG IS, THE ID, AND THE RULE-2 PRE-COMPUTE CONDITION

### 0.1 What it is

**T24 is the successor registration `T23_PREREGISTRATION.md` §6.4 names**, and it
registers exactly the twelve points that section deferred:

> **REGISTERED: P_loss ∈ {80, 155, 230} W × U_inf ∈ {10, 20, 30, 40} m/s —
> TWELVE POINTS, at mesh level L1, 1 rank, `endTime` 10000.**

Together with the four points T23 already graded (P_loss = 305 W × the same four
airspeeds), these complete the **16-point `P_loss × U_inf` map** of Sanaa's
**CASE 3** directive
(`etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md` §§3.1–3.7),
**variant (b)**: motor-in-duct conjugate heat transfer, actuator disk absent,
annulus velocity imposed by `U_inf`.

**The power levels are INHERITED, NOT RE-CHOSEN.** `T23_PREREGISTRATION.md` §2.6
registered `P_loss ∈ {80, 155, 230, 305} W` under Sanaa's ruling **"5. Rescale"**
(`etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md`, answer 5, the chief's
verbatim capture read at source). That registration is **frozen at
`fe666fd5d3cf148b1266bf693d1199cec3c7d607`** and is not reopened here. §2 below
records, at length and on this document's face, that **the instrument which
originally chose those levels has since been falsified by the solved physics** —
and that this changes the levels not at all, because they are Sanaa's ruling as
carried into a frozen document, not this lane's to re-pick.

### 0.2 **§6.4's TWO NAMED PRECONDITIONS — both discharged, and named as discharged**

`T23_PREREGISTRATION.md` §6.4 named exactly two things a successor registration
needs, *"so the deferral is actionable rather than decorative"*. Both are met,
and each is met by a MEASURED artifact rather than by an assertion:

| §6.4 precondition | discharged by | tag |
|---|---|---|
| **1. a measured per-case cost for this geometry** | **30.032125 core-min per case**, the mean of the four `T23_P305_U*` figures read from each case's own `log.solve` `ExecutionTime` line at 1 rank (29.7337 / 30.2190 / 30.4898 / 29.6860), recorded at `T23_RESULTS.md` §6 and in `docs/COST_CALIBRATION.md` row `C-20260831T183346.079343Z-d971eca8` | **MEASURED** |
| **2. a demonstrated completion at this geometry BY A CASE THAT RAN UNDER A FROZEN REGISTRATION** (expressly not by T22) | **four cases**, all six `CLAUDE.md` rule-4 conjuncts, under `fe666fd5`, markers `verification/runs/T-family/T23_runs/DONE.T23_P305_U{10,20,30,40}` | **MEASURED** |

**This is the whole of what unlocks the twelve points, and nothing else is
claimed as unlocking them.** In particular T22 remains an unregistered
feasibility rung whose prohibition
(`verification/runs/T-family/T22_runs/T22_FEASIBILITY_NOTE.md`) is honoured here
in its strongest form: **no number T22 emits enters any gate, band, threshold,
referent or cost figure in this document.** T22 appears exactly once below, in
§5.1, as one of two *rate measurements corroborating a bracket* — and that
citation is struck out of the cost basis in the same paragraph, so that the
registered POINT rests on the T23 measurement alone.

### 0.3 What this rung is NOT — stated first

> **T24 registers the PHYSICALITY TIER of the map and NOTHING ELSE**, on exactly
> the tier T23 registered and with exactly T23's three bands. It earns nothing
> about the Nusselt correlation tier, nothing about the map's Roache triple,
> nothing about grid convergence, nothing about the heat-balance instrument and
> nothing about the radiative upper bound. §4 lists each deferral with its
> reason, and every one of them is inherited from T23 §4 with **at least one
> reason strengthened by what T23 measured**.

**NO ROACHE TRIPLE, NO GCI, NO OBSERVED ORDER, NO NUSSELT NUMBER, NO
HEAT-BALANCE CLOSURE.** Every point runs at **L1 only**.

> **A SINGLE MESH LEVEL ADMITS NO TRIPLE.** Any Roache classification, GCI or
> observed order quoted from a T24 artifact is a **CATEGORY ERROR**.
> `CLAUDE.md` rule 5 governs a triple this rung does not produce, and the
> grading pass must emit none. **`CLAUDE.md` rule 5 is not weakened by this:
> there is no row here whose grid triple could be non-`CONVERGING`, because
> there is no grid triple.**

**T24 does not amend, supersede or re-grade T23.** T23's four PASS rows stand as
they are; its frozen numbers — including §2.5's "9 of 16 / 2 of 16" flag
arithmetic — are **not rewritten** (`CLAUDE.md` rule 6). Where this document
disagrees with a T23 figure, it says so **as a new measurement or a new
prediction of its own**, never as an edit to T23.

### 0.4 The id — taken from the MAXIMUM, never from a count

`CLAUDE.md` rule 11, by the analogy this family has used since T20. Re-derived
over `docs/campaigns/T-family/` ∪ `verification/runs/T-family/`, the maximum
existing top-level `T`-number is **23**, so this rung is **T24**. The set present
on disk is **{1, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21,
22, 23}** — **twenty ids with a maximum of 23, which is exactly why a count is
not the rule** (the set skips 2, 7 and 12).

**The tracked-only derivation returns the same maximum, 23**, and this is
re-checked rather than assumed: T23 §0.3 recorded that a tracked-only reading
returned a *different count* from the on-disk reading, because
`T21_PREREGISTRATION.md` was untracked. That divergence is re-measured here and
the two readings agree on the **maximum**, which is the only figure the rule
uses.

**This derivation is RE-TAKEN in the committing invocation**, in the same shell
invocation as the write, because peers take numbers constantly and a derivation
taken minutes earlier is a fact about a different tree.

**A PRECISION THE RE-DERIVATION ITSELF TURNED UP, RECORDED RATHER THAN SMOOTHED
OVER.** The first re-derivation in the committing invocation **ABORTED**, because
by then **this file itself was on disk** and the on-disk reading returned a
maximum of **24** against a tracked maximum of **23**. That is the derivation
working, not failing: **the maximum must be taken over the tree EXCLUDING the
document being written**, or every rung claims the id it just invented. The
derivation that commits this file therefore excludes
`docs/campaigns/T-family/T24_PREREGISTRATION.md` by name and **additionally
asserts that no OTHER `T24` artifact exists anywhere in either tree** — so the
exclusion cannot mask a real collision. Under that reading the maximum is **23**
on disk and **23** tracked, and the id is **T24**.

Run root **`verification/runs/T-family/T24_runs/`** per the filing charter's R6.
`scripts/check_filing.py` accepts `T24_PREREGISTRATION.md` under
`docs/campaigns/T-family/` on the same basename pattern that accepts
`T20_`, `T21_` and `T23_PREREGISTRATION.md`.

### 0.5 **THE RULE-2 PRE-COMPUTE CONDITION, STATED BY NAMING THE RUN DIRECTORIES THAT DO NOT EXIST**

`CLAUDE.md` rule 2: *before first compute, amendments are legal and must state
the condition and how it was checked (name the run directory that does not
exist).*

**THE CONDITION:** *no compute has run under any registration of these twelve
points.*

**HOW IT IS CHECKED — by naming the directories that must be ABSENT:**

| directory that must be ABSENT | why it is the right directory to name |
|---|---|
| `verification/runs/T-family/T24_runs/` | **this rung's own run root.** If it exists, this document is being written after its own compute and §1–§6 are closed to change. |
| `verification/runs/T-family/CASE3_MAP_runs/` | the name a full-map sweep filed outside the `T` numbering would have taken. Naming only the `T` root would leave a directory this condition is about unchecked. |
| `verification/runs/T-family/T23_runs/T24_*` | a twelve-point sweep smuggled into T23's run root under T24 case names. This is the one path by which the condition could be false while both roots above were absent, and it is named for exactly that reason. |

**A directory that must be PRESENT and is deliberately NOT in the table above:**
`verification/runs/T-family/T23_runs/` **EXISTS, and its existence is a
precondition of this rung rather than a violation of the condition.** T23's four
cases are the discharge of §6.4 precondition 2 (§0.2). The condition this
document registers is about **these twelve points**, not about the family, and
stating that distinction here is what stops a later reader reading T23's presence
as a breach.

**MEASURED 2026-08-31, and RE-MEASURED in the committing invocation itself,
under a LIVE PLANTED CONTROL** (`CLAUDE.md` rule 3): the three rows above
**ABSENT**, `T23_runs/` **PRESENT**. The identical predicate that returned ABSENT
for the three was run against `T23_runs/`, which **does** exist, and returned
PRESENT — so the reader was **shown able to see a non-zero before its zero was
believed.** A zero from a reader not shown able to see a non-zero is not
evidence, and the positive control here is a **real directory of this same
family**, not a synthetic one.

---

## 1. THE TEMPLATE — the ten registered lines

**1. CASE.** Case 3 variant (b), L1, **identical in construction to the four T23
cases in every respect except the two swept scalars.** Three regions: `fluid`
(duct annulus, air), `housing` (aluminium hollow cylinder r_i = 0.0335 m →
r_o = 0.0375 m, L = 0.125 m), `core` (representative winding/lamination pack,
k 40 W/mK, with a uniform volumetric source). **2-D axisymmetric wedge,
θ = 5.0°**, one cell circumferentially, with a **6 mm shaft bore** on the core's
inner radius. Two conjugate `mappedWall` interfaces (fluid/housing and
housing/core). Solver **`chtMultiRegionSimpleFoam`**, OpenFOAM **v2606**.
`kOmegaSST` in the fluid (directive §3.4). Run root
`verification/runs/T-family/T24_runs/`.

**REGISTERED: `P_loss` enters only `constant/core/fvOptions` (as the sector share
`P_loss·θ/2π`, `volumeMode absolute`, on the field `h`) and `U_inf` enters only
the fluid region's `0.orig` boundary and internal values plus the derived inlet
`k` and `omega`. NEITHER ENTERS `blockMeshDict`.** The mesh is therefore
**identical across all twelve cases and identical to T23's**, by construction and
not by inspection; §3.7 registers the check that proves it.

**Declared scope limits, carried from T23 §1 unchanged and repeated here so this
registration carries them on its own face:** the **nose and tail cones of
directive §3.2 are REMOVED** — the centrebody is a constant-radius tube and only
its middle 0.125 m is conjugate; the **duct wall is adiabatic** (directive §3.3);
**radiation is OFF** and is a disclosed omission; **g = (0 0 0)** — see §3.4,
which is not a convenience but the fact that voids one of the directive's own
checks.

**2. REFERENCE.** **NONE, and that is the point of this tier.** The physicality
tier has **no external referent**: it compares the solved `T_max` against a
**registered engineering bound** (200 °C) and reports it against a **registered
isotherm** (120 °C), both of which are Sanaa's own numbers from directive §3.6
and neither of which is a measurement of anything. **No paper is cited as a
source of constants and none is required.**

> **AND, NEW AT T24 AND REGISTERED IN THE STRONGEST TERMS: THE LUMPED
> SERIES-RESISTANCE MODEL OF `T23_PREREGISTRATION.md` §2 IS NOT USED HERE TO
> CHOOSE, JUSTIFY, BOUND, BRACKET OR PREDICT ANYTHING.** It was falsified by the
> four solved points (§2 below). It is cited in this document only as **the thing
> that was falsified**. **No level, no gate, no threshold, no cap and no
> prediction in this registration is derived from it.**

**3. QUANTITIES.**

| id | quantity | read from |
|---|---|---|
| **Q1** | `T_max` = max(T) over the whole `housing` region, °C | `internalField` of `<endTime>/housing/T` |
| **Q2** | `T_iface` = areaAvg(T on the `housing`-side of the fluid/housing interface), °C | `boundaryField` of `<endTime>/housing/T`, patch `housing_to_fluid`, **`value` entry, never `refValue`**, area-weighted with face areas computed from `constant/housing/polyMesh` and never assumed equal |

Q1 and Q2 are **two readers of the same solution on different code paths**
(`internalField` vs `boundaryField`) with **different pre-derived extents** — the
anti-degeneracy control this family established at T20 §4.4, T21 §4.4 and T23
§1 line 3. **REGISTERED PREDICTION: Q1 ≥ Q2, and the two must DIFFER.** The
housing's hottest cell is on its inner surface, adjacent to the core; the fluid
interface is its outer surface. **If Q1 and Q2 return identical values the two
readers are reading the same object twice**, and that is a finding about the
instrument, not about the solver, and makes the affected rows **NOT A RESULT**.

**4. BANDS — the SAME THREE T23 REGISTERED, on the SAME TIER, and no fourth.**

| # | registered threshold | label if met | label if not met |
|---|---|---|---|
| **B1** | Q1 < **200.0 °C** | **PASS** for that point | **PASS, FLAGGED "beyond assumption range"** |
| **B2** | Q1 > 0.0 °C (no negative temperatures, directive §3.6) | PASS | **GATE FAIL** |
| **B3** | Q1 ≥ Q2, and Q1 ≠ Q2 (§1 line 3 anti-degeneracy) | PASS | **NOT A RESULT** |

**B1's "not met" branch is a FLAGGED PASS and NOT a GATE FAIL**, registered here
before compute exactly as T23 registered it, because directive §3.6 makes an
over-bound point *"a real finding"* and not a failure. **Zero flags was never the
requirement of this tier and must not be engineered for.**

> **AND HERE IS THE HONEST PART, REGISTERED BEFORE COMPUTE RATHER THAN
> DISCOVERED AFTER IT: B1 IS A WEAK DISCRIMINATOR ON THIS ROW SET, AND THIS
> DOCUMENT SAYS SO INSTEAD OF CLAIMING A GATE IT EXPECTS TO CLEAR TRIVIALLY.**
> The four T23 points cleared B1 by margins of **+96.3922 / +130.9902 /
> +144.5611 / +152.1552 K** [MEASURED, `T23_RESULTS.md` §1] — at the **highest**
> power level of the map. The twelve points registered here are all at **LOWER**
> power at the same four airspeeds. §2.4 registers the predicted margins: the
> **smallest** is **+118.2 K**, at (230 W, 10 m/s). **B1 is therefore predicted
> to PASS on all twelve, unflagged, and a clean sweep of twelve B1 passes is
> WEAK EVIDENCE, not a strong result.** It is registered as a gate because the
> tier is the tier T23 registered and consistency across a map matters more than
> novelty; it is **not** registered as though it discriminated. **What this rung
> actually earns is in §6.5: the twelve measured `T_max` values themselves, which
> are the map the directive asked for.**

**5. LADDER.** **NONE IN THIS RUNG. There is no grid triple here and none may be
inferred.** See §0.3 and §4.2.

**6. DECOMPOSITION SEED. Serial, 1 rank.** `numberOfSubdomains 1`, no
`decomposeParDict`, `decomposePar` not run, the solver invoked directly and not
through `mpirun`. There is no partitioner, therefore no seed. `ranks = 1` is the
multiplier in every core-minute figure in §5.

**7. CRITERIA.** In this order, and the order is one-way:

1. **Strict completion** (`CLAUDE.md` rule 4, steady form, §3.5) — any case
   failing any conjunct gets no marker and its row is **NOT A RESULT**; the
   grading pass **refuses (exit 2) rather than degrades**.
2. **Instrument admission** — the planted-zero control of §3.6 must PASS on both
   readers; a refusal is `exit 2`, never a degraded grade.
3. **B3** (anti-degeneracy) — failure ⇒ **NOT A RESULT** whatever the values say.
4. **B2** then **B1** — as tabulated above.

**A gate may only turn a PASS into NOT A RESULT, never the reverse.**

**8. COST.** Registered in §5. **SUBSET POINT 360.4 core-min, SUBSET CAP 540.0
core-min hard, per-case CAP 45.0 core-min hard, ENACTED as `timeout 2700s` at
1 rank.** An overrun **stops the run**; it does not get a new budget
(`CLAUDE.md` rule 12, `COMPUTE_BUDGET_CHARTER.md`:197).

**9. ABSENT REGISTRY.** §0.5, re-measured under a live planted control in the
committing invocation.

**10. AUTHORISATION.** This document authorises the **twelve cases of §6.2 and no
others**. It authorises no mesh level other than L1, no second grid, no
correlation, no triple and no heat-balance instrument.

---

## 2. **THE LEVEL-SELECTION INSTRUMENT IS FALSIFIED, AND THIS DOCUMENT USES IT FOR NOTHING**

### 2.1 What T23 measured, restated as the ground of a registered prohibition

`T23_PREREGISTRATION.md` §6.2 registered a contingency **one-way and before
compute**: *"if the solved values disagree with **both** closures by more than
the 1.763× spread between them, the **lumped model of §2 is the thing that was
falsified**"*. **THE CONTINGENCY FIRED ON ALL FOUR POINTS**
[`T23_RESULTS.md` §2, MEASURED]:

| case | solved rise above `T_inf`, K | DB rise / solved | FP rise / solved |
|---|---:|---:|---:|
| `T23_P305_U10` | 88.758 | **3.541** | 2.031 |
| `T23_P305_U20` | 54.160 | **3.369** | 1.947 |
| `T23_P305_U30` | 40.589 | **3.280** | 1.911 |
| `T23_P305_U40` | 32.995 | **3.235** | 1.896 |

**The lumped model overpredicts the housing temperature rise by 1.90× to 3.54×,
beyond the 1.763× spread between its own two closures — so it is not an artefact
of choosing between Dittus-Boelter and the flat plate.** Even the optimistic
closure is out by ~1.9×.

**THIS FINDING WAS REPRODUCED ON A SECOND, INDEPENDENT PATH BEFORE IT WAS ACTED
ON.** The heat-transfer supervisor re-derived the total resistances from the
published table by a route not using the grading script — **R(10) = 1.0305,
R(20) = 0.59850, R(40) = 0.34950 K/W** — giving model/solved ratios of **3.541 /
3.370 / 3.231** against the grader's **3.541 / 3.369 / 3.235**. This lane
re-checked that arithmetic independently: `305 × 1.0305 = 314.30 K` against a
solved rise of `88.758 K` gives **3.5411**; `305 × 0.59850 = 182.54 K / 54.160 =
3.3705`; `305 × 0.34950 = 106.60 K / 32.995 = 3.2308`. The residual spread
between the two paths is **≤ 0.13 %** and is table rounding. **A figure that only
one implementation has ever produced is not registered in this document.**

### 2.2 **THE REGISTERED PROHIBITION**

> **REGISTERED, BEFORE COMPUTE AND ONE-WAY: the lumped series-resistance model of
> `T23_PREREGISTRATION.md` §2 MAY NOT BE USED IN THIS RUNG TO CHOOSE A LEVEL,
> JUSTIFY A LEVEL, SET A BAND, SET A CAP, BRACKET AN ISOTHERM, OR PREDICT A
> VALUE.** It is falsified against the solved physics of this exact geometry at
> this exact mesh level, and a falsified instrument does not get to keep its
> advisory role because its output is convenient. **Every prediction in this
> document (§2.4) is derived from the SOLVED T23 field, never from that model.**

### 2.3 **WHAT THAT COSTS, STATED RATHER THAN GLOSSED — three consequences**

**(a) The flag arithmetic of T23 §2.5 is MODEL-derived, not solve-derived.** The
figures **"9 of 16"** (original levels) and **"2 of 16"** (rescaled levels) were
computed from the falsified model. `T23_RESULTS.md` §2 already stated the
consequence and this registration carries it forward verbatim in substance: **on
the solved physics the rescaled levels flag ZERO of 16, not 2.** §2.4's predicted
values are the arithmetic behind that. **T23 §2.5's committed numbers are NOT
rewritten** (`CLAUDE.md` rule 6); they are correct as *what the model said* and
are now known to be wrong as *what the solver says*, and both statements are
true at once.

**(b) The levels were chosen to span two thresholds and, on solved physics, span
neither.** T23 §2.6 selected `{80, 155, 230, 305} W` on the criterion that the
set **bracket the 120 °C isotherm at all four airspeeds**. On the solved field
the **hottest point of the entire 16-point map is 103.6078 °C**, at (305 W,
10 m/s) [MEASURED, `T23_RESULTS.md` §1] — **below the 120 °C isotherm.**

> **REGISTERED CONSEQUENCE, before compute: the 120 °C isotherm is predicted to
> be CROSSED NOWHERE on the rescaled 16-point map, and the 200 °C bound to be
> approached nowhere. §4.5's isotherm trace is therefore NOT delivered by these
> twelve points and REMAINS DEFERRED — not because twelve points are too few,
> which was T23's reason, but because the isotherm is predicted to lie OFF THE
> REGISTERED MAP ENTIRELY.** That is a **finding about the level set**, it
> follows directly from the falsification of the instrument that chose it, and it
> is registered in advance so that it cannot afterwards be read as a defect
> discovered by embarrassment.

**(c) This does not reopen the levels, and this lane does not reopen them.**
Sanaa ruled *"5. Rescale"*; T23 §2.6 froze `{80, 155, 230, 305} W` under that
ruling; §6.4 named **these twelve points** as the deferred remainder. **Choosing
different levels would be re-taking a decision that is Sanaa's and re-opening a
frozen document, and this lane does neither.** The honest course is to run the
twelve registered points, report the map they produce, and report on the face of
the results that the map does not reach the thresholds it was sized against.
**A later registration may propose new levels; that proposal is not this
document's to make** (`ESCALATION_CHARTER` §4.1).

### 2.4 **THE REGISTERED PREDICTIONS — derived from the SOLVED field, REPORTED AND NEVER GATED**

**The prediction instrument is registered here, before compute, together with the
physical argument that licenses it.**

> **THE ENERGY EQUATION OF THIS CASE IS LINEAR IN THE SOURCE POWER, AND THE FLOW
> FIELD IS FULLY DECOUPLED FROM TEMPERATURE.** The fluid uses
> `equationOfState rhoConst` at ρ = 1.2 kg/m³ with **constant** `mu`, `Cp` and
> `Pr`; `g = (0 0 0)`; radiation is OFF; both solids are `constIso` with constant
> `kappa`. Density therefore does not respond to temperature, `nut` is a function
> of the velocity field alone, and `alphat = ρ·nut/Prt` likewise. **So the
> momentum, `k` and `omega` fields do not depend on `P_loss` at all, and the
> temperature field is EXACTLY proportional to the source power at fixed
> `U_inf`.**

**REGISTERED PREDICTION, REPORTED BESIDE EVERY ROW AND USED AS NO GATE:**

    T_max(P, U) − T_inf  =  (P / 305) × [ T_max(305, U) − T_inf ]_MEASURED-AT-T23

with `T_inf` = 288.0 K = 14.85 °C (REGISTERED at T23 §2.1 and MEASURED as the
inlet `fixedValue` in each case's own `0.orig/fluid/T`), and the four bracketed
rises taken from `T23_RESULTS.md` §2 [MEASURED]: **88.758 / 54.160 / 40.589 /
32.995 K** at U = 10 / 20 / 30 / 40 m/s.

| P_loss, W | U_inf, m/s | predicted rise, K | **predicted `T_max`, °C** | predicted margin to 200 °C, K |
|---:|---:|---:|---:|---:|
| 80 | 10 | 23.281 | **38.131** | +161.9 |
| 80 | 20 | 14.206 | **29.056** | +170.9 |
| 80 | 30 | 10.646 | **25.496** | +174.5 |
| 80 | 40 | 8.654 | **23.504** | +176.5 |
| 155 | 10 | 45.107 | **59.957** | +140.0 |
| 155 | 20 | 27.524 | **42.374** | +157.6 |
| 155 | 30 | 20.627 | **35.477** | +164.5 |
| 155 | 40 | 16.768 | **31.618** | +168.4 |
| 230 | 10 | 66.932 | **81.782** | **+118.2** |
| 230 | 20 | 40.842 | **55.692** | +144.3 |
| 230 | 30 | 30.608 | **45.458** | +154.5 |
| 230 | 40 | 24.881 | **39.731** | +160.3 |

All **DERIVED** from MEASURED T23 values. **The tightest predicted B1 margin on
the whole set is +118.2 K**, which is §1 line 4's registered statement that B1
does not discriminate here.

**THE REGISTERED CONTINGENCY ON THIS PREDICTION, one-way and stated now — and it
is DELIBERATELY SHARPER THAN T23's, because the instrument is sharper.** T23's
contingency tolerated a **1.763×** disagreement before firing, because its
predictor was a lumped correlation. This predictor is an **exactness claim about
a linear PDE**, and it is registered with a tolerance to match:

> **REGISTERED: if any solved rise departs from its predicted rise by more than
> 2 % of the predicted rise, THE LINEARITY ARGUMENT ABOVE IS THE THING
> FALSIFIED** — a reportable finding about the case construction or the solver
> (a temperature-dependent property that should not be there, an unconverged
> field, a source that is not what was entered, or a mesh that is not the mesh
> assumed) — **and it changes B1, B2 and B3 not at all, because those grade the
> solved temperature and not the predictor.** The 2 % figure is chosen against
> T23's own measured iterative convergence (final asserted residuals ≤ 1.3e-08,
> `T23_RESULTS.md` §3) and is **not** a gate: a departure is REPORTED, and the
> affected row still carries whatever B1/B2/B3 say.

**Why register a falsifiable predictor at all, when the tier requires none:**
because a rung whose only gate is one it expects to clear by 118 K is a rung that
measures nothing about itself. This predictor is the instrument by which the
twelve rows can be wrong in a way anyone would notice.

---

## 3. WHAT THE SOLVED CASES MUST SATISFY

### 3.1 The registered iteration count, and why no `residualControl` is registered

**REGISTERED: `endTime` 10000 SIMPLE iterations** (directive §3.4's
*"iteration cap 10,000"*), `writeInterval` 10000, **no `residualControl`
stopping criterion in any region's `SIMPLE` dict.** Convergence is an
**ASSERTION on the log, never a stopping rule.** The reason is this family's own
post-mortem, carried from T23 §3.1: T19's `P_q_c` and `P_Ts_c` carried
`residualControl` against a registered `endTime` of 30000 and **stopped at 828
and 541 iterations — under 3 % of their registered duration — both reporting
`rc=0`**. They did not crash; they succeeded at the wrong experiment. An early
residual exit leaves the last time directory below `endTime`, so rule 4 conjunct
3 cannot hold.

**REGISTERED, and paid for honestly:** running the full count is not free, every
iteration after convergence is paid for, and that cost is inside the §5 POINT on
every one of the twelve cases.

### 3.2 Registered write precision

**REGISTERED: `writeFormat ascii`, `writePrecision 12`, `writeCompression off`,
`timePrecision 12`.** OpenFOAM's default `writePrecision 6` gives a write quantum
of ~1.0 mK at T ≈ 400 K. **The precision is registered for B3**, the
anti-degeneracy control, whose entire content is that two readers must return
**different** numbers; at `writePrecision 6` two genuinely different values can
round to the same string and B3 fails as a false positive. T23 measured Q1 − Q2
at **+1.499971 K** in its tightest case, so the quantum is far from binding — but
the twelve cases here run at **as little as 26 % of T23's power**, and §2.4
predicts Q1 − Q2 to scale with it, to a smallest predicted value near **0.39 K**.
**Still four orders above the quantum, and the arithmetic is stated so nobody has
to guess.**

### 3.3 `constant/g` is mandatory and its value is a declared decision

`chtMultiRegionSimpleFoam` reads gravity at **file scope** in
`createFluidFields.H`, before the region loop opens, with
`IOobject::READ_MODIFIED`, which requires the file present. **REGISTERED:
`constant/g` present in every T24 case with `value (0 0 0)`.**

### 3.4 **THE DIRECTIVE'S RICHARDSON CHECK IS VACUOUS IN THIS CASE — DISCLOSED, NOT REPORTED AS PASSING**

Directive §3.3 requires *"verify Richardson number Ri = g β ΔT L / U² < 0.1 on
every run"*. **With `g = (0 0 0)` registered in §3.3, Ri ≡ 0 identically, by
construction, at every point of the map.** The check therefore **cannot fail and
cannot inform**.

> **REGISTERED: the Ri < 0.1 criterion is DECLARED VACUOUS for T24 and is NOT
> reported as a passing check.** Reporting `Ri = 0 < 0.1, PASS` would be
> **evidence annotated as non-binding** in its worst form — a criterion satisfied
> by the modelling choice that removed the physics it was meant to police.
> **What is registered instead is the honest statement: buoyancy is switched OFF
> in T24 by the `g = (0 0 0)` choice, its neglect is a declared omission, and
> whether forced convection genuinely dominates is NOT established by this
> rung.**

**AND IT MATTERS MORE HERE THAN IT DID AT T23, WHICH IS WHY IT IS RESTATED RATHER
THAN CROSS-REFERENCED.** T23's least favourable corner was (305 W, 10 m/s). This
rung registers **(80 W, 10 m/s)**, whose predicted rise is **23.3 K** — a
*smaller* driving ΔT, so a *smaller* buoyant term, but also the *lowest* forced
velocity in the set. **The ratio of the two is not established by this rung and
this document does not estimate it**, because an estimate would require a β and a
g this case does not carry, and inventing them for a document that freezes on
commit is exactly what §2.2 prohibits for the lumped model.

### 3.5 Rule 4 completion, in its steady form

`CLAUDE.md` rule 4 is **all-or-nothing**; the grading pass **refuses (exit 2)
rather than degrades**.

| # | conjunct | how it is evaluated here |
|---|---|---|
| 1 | `rc = 0` | **DERIVED-FROM-LOG, never read from `STATUS`** — see §3.5a |
| 2 | an `End` line | `grep -c '^End$' log.solve` == 1 |
| — | **zero `FOAM FATAL`** | `grep -c 'FOAM FATAL' log.solve` == 0 |
| 3 | last time == `endTime` | the numerically greatest time directory equals **10000** |
| 4 | fields present | **`T`, `p` in `<endTime>/core/` and `<endTime>/housing/`; `T U p p_rgh alphat nut k omega` in `<endTime>/fluid/`.** The core and housing are solid regions and the fluid field list does not apply to them |
| 5 | `ExecutionTime` count == `endTime` | evaluated as `count == 10000` at `deltaT 1` |
| 6 | **age guard** | every field at `endTime` **newer** than that case's own `0/housing/T` by `st_mtime`; the launcher touches it last. The launcher **refuses** a case where `0/` or any time directory already exists |

### 3.5a **`rc` IS DERIVED FROM THE LOG BECAUSE THE QUEUE RUNNER DESTROYS `STATUS` — REGISTERED IN ADVANCE, NOT DISCOVERED AFTERWARDS**

**MEASURED, twice, across five cases:** the queue runner overwrites the launcher's
`STATUS.<case>` file after the launcher writes it, leaving three keys and
destroying `rc`, `wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`,
`capped` and `solver`. It happened to `T22_CHTb_L1`
(calibration row `C-20260831T172527.907664Z-b006f781`) and then to all four
`T23_P305_U*` (`T23_RESULTS.md` §5.1). **This registration assumes it will happen
again and registers the derivation up front rather than discovering the loss at
grading time.**

> **REGISTERED: for every T24 case, `rc = 0` is established as
> `rc_source=DERIVED-FROM-LOG` from three conjuncts read off `log.solve` —
> exactly one `End` line, ZERO `FOAM FATAL`, and last time == `endTime` == 10000.
> `launcher_rc` IS NOT `rc` and IS NOT ACCEPTED AS `rc`, even at 0**, because
> `launcher_rc` is the exit status of the launch argv and a zero there is exactly
> the shape of the `setsid` trap the launcher exists to avoid (`setsid timeout
> cmd` exits 0 for every outcome).
>
> **REGISTERED: the derivation must be able to return NOT DONE.** Its selftest
> drives three arms negative — `launcher_rc=0` with a `FOAM FATAL` in the log →
> NOT DONE; with no `End` line → NOT DONE; with last time 9000 → NOT DONE. **A
> derivation that cannot return NOT DONE is not a derivation.**

**`queue_runner.py` IS CFD'S INSTRUMENT.** The clobber is **ESCALATED, NOT
REPAIRED BY THIS TEAM**, and this document proposes no repair and no replacement
tool. **Sanaa's universal rule of 2026-08-26 governs the choice not to refuse:
bookkeeping never voids physics.** The destroyed INFRASTRUCTURE fields are
reported **NOT MEASURED** and void only the cost claim's ledger path; the
PHYSICS-CRITICAL conjuncts are evaluated on the log, and each says which.

**AND ONE INFRASTRUCTURE FIGURE IS THEREFORE SOURCED TWICE, DELIBERATELY.** The
per-case wall time — which is the whole of the §5.4 calibration — is taken from
each case's **own `log.solve` `ExecutionTime` line**, not from `STATUS`, for the
same reason. That is the path T23's calibration actually used.

### 3.5b **THE `START.<case>` FILE IS REGISTERED AND IS ACTUALLY WRITTEN — a T23 divergence not repeated**

`T23_PREREGISTRATION.md` §5.4 registered that *"each launcher writes a
`START.<case>` file before the solver starts, carrying `start_utc`, all three
`/proc/loadavg` windows and `nproc`"*. **`run_t23.sh` contained no code to write
one, and no `START.T23_P305_U*` file exists** [MEASURED; `T23_RESULTS.md` §5.2
reported the divergence rather than smoothing it over, and the frozen document
was correctly not edited].

> **REGISTERED FOR T24, and this time the launcher carries the code: `run_t24.sh`
> writes `START.<case>` BEFORE the solver line**, carrying `start_utc`, the three
> `/proc/loadavg` windows, `nproc`, and the count of `chtMultiRegionSimpleFoam`
> processes already running. **This is not a new tool and not a new rule** — it
> is T23 §5.4's own registered text, implemented in the launcher that runs under
> the registration that requires it (Sanaa's 14-day plumbing freeze,
> `etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`).

The §5.4 refusal condition it feeds is registered unchanged at §5.4 below.

### 3.6 The planted-zero control — `CLAUDE.md` rule 3

**REGISTERED, and binding on both readers before any row is graded:**

1. **Copy first, never write into the case.** `copytree` into a scratch
   directory; **REFUSE** if the destination realpath resolves inside the case
   realpath.
2. **NEGATIVE ARM, threshold exactly ZERO.** The reader is run twice on identical
   bytes; the difference must be **bitwise `0.0`**, else REFUSE "the reader is
   NOISY". **No absolute tolerance anywhere in the negative arm.**
3. **POSITIVE ARM, a measured magnitude ladder** in K:
   **(10.0, 1.0, 1e-1, 1e-2, `PLANT`, 1e-3, 1e-4, 1e-5, 1e-6)**, `floor` = the
   smallest magnitude with a strictly non-zero read, the comparison **exact and
   epsilon-free**.
4. **REFUSE if `floor is None`** — the reader is **BLIND**.
5. **THE ONLY SIZING TOLERANCE IS RELATIVE, AND THE PREDICATE IS REGISTERED
   LITERALLY:** `got >= PLANT * (1.0 - 1e-9)`. This is the form used at
   `verification/runs/T-family/T1_runs/analyse_pesweep.py:141`,
   `analyse_dts.py:594` and `analyse_dts_p.py:226`. **`analyse_t3.py:327`'s
   absolute `seen >= PLANT - 1e-15` is EXPRESSLY NOT ADOPTED**: on a ~300 K field
   that window is **0.0176 of one ULP**, i.e. narrower than the smallest
   representable step, so the outcome would be decided by a rounding wiggle
   rather than by whether the reader saw the plant.
6. **`PLANT = 1.234e-03 K`, IMPORTED from `scripts/roache_triple.py`**, never
   redefined locally.
7. **The plant is located STRUCTURALLY, by LINE INDEX from the field's own
   header, never by value.** Q1 takes the plant in the hottest `internalField`
   cell; Q2 takes it in every face of the target patch, so Q2's expected shift is
   exactly `PLANT` and not `PLANT/N`. The number of values planted is recorded
   in the output.
8. Original bytes restored from the in-memory copy; the scratch tree removed in
   a `finally`.
9. **`__pycache__` is cleared before every control run**, and the selftest runs
   under both `python3` and `python3 -O`. A stale bytecode cache inverts a
   mutation control — the clean arm fails and the mutated arm passes — and
   `PYTHONDONTWRITEBYTECODE` does not fix it.

**A refusal here makes the WHOLE RUNG `NOT A RESULT`.** An instrument that
cannot see a planted perturbation is not entitled to certify a bound.

### 3.7 **THE MESH IDENTITY CHECK — registered, because §1 line 1 asserts it**

§1 line 1 registers that the mesh is identical across all twelve cases and
identical to T23's, *by construction*. A construction claim that is never checked
is an assumption.

> **REGISTERED: before grading, the twelve cases' `constant/{fluid,housing,core}/polyMesh/points`
> files are hashed and asserted BYTE-IDENTICAL to one another AND to
> `T23_P305_U10`'s.** A mismatch is a finding about the build and makes the
> affected rows **NOT A RESULT** — not because the mesh is bad, but because §1
> line 1's registered claim would then be false and §2.4's prediction rests on
> it.

**And the mesh gates themselves, against `docs/standards/MESH_STANDARD.md`:**
§3.1 max non-orthogonality **hard gate 70°**; §3.2 max skewness **hard gate 4**;
§3.3 aspect ratio **advisory at 1000**, never a lone rejection, with a compound
flag at AR > 1000 together with non-ortho > 60° or skew > 2. **REGISTERED: every
region of every case must show `Mesh OK` in its own `checkMesh` log and ZERO
negative-volume cells read as the DIRECT quantity — a strictly positive reported
minimum cell volume — and not as the absence of a warning.** A mesh that cannot
pass its own gate is a **finding to report, never a thing to build over.**

---

## 4. WHAT IS DEFERRED, AND WHY — each with its reason

**Every deferral below is a scope limit registered before compute, not a result
that came out badly.** All are inherited from T23 §4; each carries at least one
reason that T23's measurements **strengthened**.

### 4.1 The Nusselt correlation tier — DEFERRED

Directive §3.6's second bullet grades mean Nusselt on the housing at (300 W,
20 m/s) against an annular-flow correlation to 25 %. **Deferred**, four reasons,
each independently sufficient: (a) **its registered operating point, 300 W, is
not a level of the rescaled set** and its re-registration is a decision, not a
formality; (b) directive §3.6 requires *"verify applicability range on the
page"*, i.e. a **title-page-verified paper** (`CLAUDE.md` rule 15) that this lab
does not hold for annular flow; (c) it needs a wall-Nusselt instrument that does
not exist; **(d) NEW, and MEASURED at T23: max y+ on the housing EXCEEDS 1 at
U ≥ 30 m/s** (§4.4), and directive §3.4 states in terms that *"wall functions are
NOT acceptable on the gated levels"*. **Half the airspeeds of this map cannot
carry a heat-transfer-coefficient claim at L1 as built.**

### 4.2 The map's Roache triple — DEFERRED, and it is BLOCKED

Directive §3.6's third bullet requires a grid triple on `T_max` at (300 W,
20 m/s) with p ∈ [1.3, 2.5] and GCI_fine < 2 %. **Deferred, and recorded as
`BLOCKED`.** Three reasons: (a) `T21_PREREGISTRATION.md:54-57` records a
cross-team dependency, **`CASE3-DEP-1` (cfd's Case 2 centerbody)**, as `PENDING`
and as gating *"the correlation tier and the Roache triple of the map"* — and
**T23 §4.2 disclosed that `CASE3-DEP-1` IS NOT REGISTERED ANYWHERE, being
asserted only in an uncommitted draft that freezes nothing.** That defect in the
dependency's filing is **re-reported here and again not resolved here**, because
resolving it is a cross-team question (`ESCALATION_CHARTER` §4.1). (b) §1 line 5
registers no ladder in this rung, for the independent reason that **a single mesh
level admits no triple at all.** (c) **NEW, MEASURED at T23:** the y+ finding of
§4.4 blocks it independently.

### 4.3 The heat-balance gate — DEFERRED

Directive §3.4 requires closure to 1 % via *"the mutation-tested heat-balance
instrument"*. **Deferred: that instrument does not exist for this case.** The
general reason such an instrument belongs **downstream** of the solve, registered
at T21 §5.2a and honoured at T23: an inline function object that fails does so at
**construction**, before the first iteration, and takes the entire solve with it,
whereas a `postProcess` pass that fails costs nothing because the fields are
already on disk. **REGISTERED: no `wallHeatFlux` function object is placed in any
T24 `controlDict`.** The `surfaceFieldValue` monitors T23 carried are carried
unchanged and are **monitors, not gates.**

### 4.4 The y+ ≤ 1 requirement — MEASURED AND REPORTED, NEVER GATED, AND ITS BREACH IS ALREADY KNOWN

Directive §3.4 requires y+ ≤ 1 on the housing surface. **REGISTERED: max y+ on
the housing is MEASURED and REPORTED beside every row, and is NOT a gate in this
rung.**

> **THE BREACH IS NOT A DISCOVERY THIS RUNG WILL MAKE — IT IS A MEASUREMENT THIS
> RUNG CARRIES FORWARD.** T23 measured max y+ on `fluid_to_housing` at
> **0.4037 / 0.7515 / 1.079 / 1.397** for U = 10 / 20 / 30 / 40 m/s [MEASURED,
> `T23_RESULTS.md` §4], i.e. **above 1 at U ≥ 30 m/s**, on the identical mesh at
> the identical airspeeds. **Since the flow field is independent of `P_loss`
> (§2.4), the twelve cases registered here will reproduce those four values, one
> per airspeed, to solver precision.** They are therefore **not new information**,
> and this registration says so in advance so that a later reader does not read a
> re-measurement as a fresh finding.
>
> **REGISTERED CONSEQUENCE, unchanged from T23 §4.4: the y+ breach BLOCKS the
> correlation tier and the triple — neither of which this rung claims — and it
> DOES NOT VOID THE PHYSICALITY ROWS**, whose content is a temperature bound and
> not a heat-transfer coefficient. **It is a known limitation carried forward,
> not a gate and not a defect discovered here.**

**AND THE INSTRUMENT TRAP IS REGISTERED WITH IT, because rediscovering it would
cost a false zero.** The **generic** utility `postProcess -func yPlus -region
fluid` **exits rc 0**, prints *"Unable to find turbulence model in the database:
yPlus will not be calculated"*, and then prints `y+ : min = 0, max = 0, average
= 0` on every patch [MEASURED at T23 §4.1]. **A reader parsing only the second
line reports y+ = 0 on every case in this family — a perfect zero from a reader
the tool has ALREADY SAID cannot see a non-zero.**

> **REGISTERED: y+ is measured through the SOLVER'S OWN route,
> `chtMultiRegionSimpleFoam -postProcess -func yPlus -region fluid -time 10000`,
> run in a SCRATCH COPY of each case so no graded artifact is written. The
> BLIND-log guard is carried with BOTH LIMBS DRIVEN in the grader's selftest: a
> blind log returns a SENTINEL and its zeros never reach a value slot, and the
> same reader on a good log returns a real non-zero value — so the BLIND result
> is a reading and not blindness.**

### 4.5 The 120 °C isotherm trace — DEFERRED, and now for a STRONGER reason than T23's

Directive §3.6's report bullet asks the 120 °C isotherm traced across the map.
T23 deferred it because four points on one power level cannot trace an isotherm.
**T24 completes the map to sixteen points and STILL cannot trace it**, for the
reason registered at §2.3(b): **the isotherm is predicted to lie entirely OFF the
rescaled map, whose hottest point is the already-measured 103.6078 °C.** **This
is registered before compute as a prediction of this rung, and reporting the
absence of a crossing is the honest deliverable.**

### 4.6 The radiation upper bound — DEFERRED

Directive §3.6 asks for a per-point ε σ (T⁴ − T_inf⁴) A upper bound on the
neglected radiative term. **Deferred: it needs a registered emissivity, which the
directive does not supply and which this lane will not invent for a document that
freezes on commit.** Radiation OFF remains a **disclosed omission** (§1 line 1).
**It is worth one honest sentence that the deferral does not hide: the predicted
temperatures here are LOWER than T23's, so the neglected radiative term is
SMALLER than at the point where it was already not bounded — the omission does
not grow.**

---

## 5. COST — `CLAUDE.md` rule 12

### 5.1 The basis — and it is MEASURED ON THIS GEOMETRY, which no previous Case 3 registration could say

> **THE REGISTERED RATE IS `4.541148e-06` s PER CELL-ITERATION, MEASURED ON THIS
> EXACT GEOMETRY AT THIS EXACT MESH LEVEL AND ITERATION COUNT**, from the four
> `T23_P305_U*` cases' own `log.solve` `ExecutionTime` lines at 1 rank
> [`T23_RESULTS.md` §6, MEASURED].

**This is the change that licenses the headroom decision of §5.2, and the reason
is a measured one rather than a preference.** The previous Case 3 registration
sized its cap at **3.25× headroom**, and the 3.25 came from **T19b, where a rate
was borrowed ACROSS A GEOMETRY CHANGE** — T1c, a **pipe**, lending its rate to a
**plane channel** — and missed by that factor. **T24 borrows across no geometry
change at all: the rate is this geometry's own.**

**AND THE CARTESIAN ANCHOR IS NOW A BRACKET, NOT A LOWER BOUND — measured, not
argued.** T23 §5.1 registered the two Cartesian anchors (`T5_CUBE_m`
**4.1541e-06**, `T5_CUBE_f` **4.6476e-06** s/cell-iter) as *"a LOWER BOUND on the
per-cell rate, not a bracket around it"*, on the reasoning that a three-region
wedge with two conjugate interfaces and a `kOmegaSST` fluid must cost more per
cell than a Cartesian single-solid sourceless case. **The reasoning was wrong and
the measurement says so:** T23's **4.541148e-06** lands **inside** that bracket,
near its upper end. A second same-geometry measurement — T22's **4.22999e-06**,
at half the iteration count — also lands inside it.

> **AND THAT SECOND MEASUREMENT IS STRUCK FROM THE COST BASIS IN THE SAME BREATH
> IT IS CITED.** `T22_CHTb_L1` is an **unregistered feasibility rung** whose own
> note forbids carrying any number it produces into a graded rung (§0.2).
> **T22's rate is named here as corroboration of a QUALITATIVE claim — that the
> Cartesian bracket contains this geometry's rate — and the REGISTERED POINT of
> §5.2 is computed from the T23 measurement ALONE.** Deleting the T22 sentence
> would change no figure in this document. That is the test of whether a citation
> is load-bearing, and it is stated so a reader can apply it.

**Honest weakness of the basis, named and not absorbed:** the rate rests on
**n = 4 cases of a single rung**, all launched inside four minutes on a box
measured at **11.9–25.7 % busy**. §5.3 registers what that does not cover.

### 5.2 POINT and CAP

Cell count **39,680** per case (35,200 fluid + 3,360 core + 1,120 housing) at
`endTime` **10,000**, 1 rank:

    39,680 cells x 10,000 iterations = 3.968e08 cell-iterations
    at 4.541148e-06 s/cell-iter  ->  1,801.93 s = 30.0321 core-min per case

which reproduces the measured per-case mean **30.032125 core-min** exactly, as it
must, the rate having been derived from it.

| figure | value | tag |
|---|---:|---|
| **per case POINT** | **30.0321 core-min** | **MEASURED** (mean of four T23 cases) |
| **per case CAP** | **45.0 core-min** | **REGISTERED**, hard |
| **TWELVE-CASE POINT** | **360.4 core-min** | **DERIVED** (12 × 30.0321 = 360.3855) |
| **TWELVE-CASE CAP** | **540.0 core-min** | **REGISTERED**, hard (12 × 45.0) |
| **cap headroom** | **1.4984 ×** POINT | **DERIVED** |
| USD at POINT | **$0.3082** | **DERIVED, NOT MEASURED** |
| USD at CAP | **$0.4617** | **DERIVED, NOT MEASURED** |

USD at the owner-stated **c7a.4xlarge $0.0513/core-h** (**REPORTED-BY-OWNER**,
2026-08-21/22). **The box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure here is measured. Both are
far under the $25 pre-authorisation, **and a blanket authorisation is not a
per-item reading** (`CLAUDE.md` rule 9).

> **AN ARITHMETIC PRECISION STATED RATHER THAN ROUNDED AWAY: THE HEADROOM IS
> 1.4984×, NOT 1.5×.** 1.5 × 360.3855 = **540.578** core-min. The registered CAP
> is **540.0**, which is **12 × 45.0** exactly and is the figure the launcher can
> actually enact; **45.0 / 30.032125 = 1.49839**. The registered cap is therefore
> **very slightly TIGHTER than 1.5×**, which is the conservative direction, and
> the exact ratio is stated so that no later reader reconstructs 1.5 and finds a
> 0.578 core-min discrepancy they cannot place.

**The cap is ENACTED, not merely written**: **`timeout 2700s` at 1 rank inside
each case's own launcher** (`cap_core_min = TIMEOUT_S × RANKS / 60` = 45.0). The
queue runner's `CAP_OVERRUN.txt` only **reports** and never kills; the wrapper's
own `timeout` is what stops the run, as rule 12 requires. **An overrun stops the
run; it does not get a new budget** — and it stops **that case only**, leaving the
other eleven rows untouched.

### 5.3 **THE RESIDUAL COST RISK IS CONTENTION, AND IT IS REGISTERED BEFORE THE FACT**

**This is the one place where the §5.1 basis does not cover the run it is being
used to size, and saying so before compute is the whole point of registering a
cap.**

T23's four cases ran **four-concurrent** on a 16-core box measured at
**11.9 % / 12.7 % / 22.3 % / 25.7 %** busy at their four launch instants, and
their four `ExecutionTime` figures spanned only **1781.16–1829.39 s, a 2.7 %
spread** — a low-contention sequence [MEASURED, `T23_RESULTS.md` §5.2, §6].
**These twelve cases will run TWELVE-concurrent on the same 16-core box**, under
Sanaa's 2026-08-31T15:45Z standing order that the box must be full. That is a
different contention regime from the one the rate was measured in.

**The arithmetic, stated so the risk is sized rather than gestured at:** the
longest T23 case ran **1829.39 s**; the registered timeout is **2700 s**;
**wall-time headroom is therefore 1.476×.** A twelve-concurrent contention
penalty **above ~48 %** caps a case.

> **REGISTERED, one-way and before compute: if a case is capped at 2700 s it is
> STOPPED and it does not get a new budget** (`CLAUDE.md` rule 12). Its row is
> **NOT A RESULT** under §3.5 conjunct 3 (last time < `endTime`), the
> remaining rows are unaffected, **and the capping is reported as a CONTENTION
> finding and NOT folded into the actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER.md`
> §6 — waste and contention are named separately, never absorbed).
>
> **AND THE GENERAL FORM IS REGISTERED WITH IT, because it is the same lesson
> T23 §6 drew in a different dimension:** T23 measured that *"a borrowed
> per-cell-iteration rate survives a change of dimensionality and does not
> survive a change of geometry family"*. **This rung borrows across NO geometry
> change but across a THREEFOLD change in concurrency, and whether a rate
> survives that is NOT established by anything the lab has measured.** It is
> stated here as the named risk of this cap rather than claimed as covered.

### 5.4 **THE DIRECTIVE'S 700 core-min CAP — WHAT DISSOLVES AND WHAT DOES NOT**

Directive §3.7 sets *"cap 700 core-min"* for Case 3 and estimates *"~15-40
core-min (L1)"* per solve and *"16 points ~8 core-h at L1"*. T23 §5.3 registered
that those three figures were **not mutually consistent**, because 16 points at
that rung's **3.25× headroom** came to **1,600 core-min**, i.e. **2.29× the
directive's cap** — and expressly reserved the resolution to this registration.

**THE RESOLUTION, WITH BOTH READINGS STATED, BECAUSE ONLY ONE OF THEM DISSOLVES:**

| reading of "the 16-point map costs …" | figure | against the directive's 700 |
|---|---:|---|
| **EXPECTED SPEND** — 16 × 30.0321 measured | **480.5 core-min** | **INSIDE**, and within **0.1 %** of the directive's own *"~8 core-h"* = 480 core-min |
| **ACTUAL (4 done) + POINT (12 to run)** — 120.1285 + 360.3855 | **480.5 core-min** | **INSIDE** |
| **SUM OF REGISTERED POINTS** — T23's 123.2 + T24's 360.4 | **483.6 core-min** | **INSIDE** |
| **SUM OF REGISTERED CAPS** — T23's frozen 400.0 + T24's 540.0 | **940.0 core-min** | **OVER, by 1.34×** |
| **16 points at this rung's own 45.0 core-min per-case cap** | **720.0 core-min** | **OVER, by 1.029×** |

> **REGISTERED FINDING, and it is a correction to the convenient version of this
> story: measuring the rate DISSOLVES the inconsistency ON THE EXPECTED-SPEND
> READING AND NOT ON THE CAP READING.** T23 §5.3's tension was an artefact of the
> **borrowed 3.25× headroom** in the sense that it shrank from **2.29×** to
> **1.03×** when the rate stopped being borrowed — **but it did not vanish.** A
> per-case cap that is meaningful at all must exceed the per-case expectation,
> and sixteen such caps necessarily exceed sixteen expectations; **700 core-min
> sits between the two.**
>
> **WHICH READING THIS DOCUMENT ADOPTS, stated so it cannot be read either way
> afterwards: the EXPECTED-SPEND reading.** A cap is a **stop**, not a
> **reservation** — its purpose is that an overrun stops a run, and a cap that is
> never reached costs nothing. The lab expects to spend **480.5 core-min** on the
> full map, inside the directive's 700; it registers a stop at **540.0** for the
> twelve, and the only world in which the sum of caps is actually spent is one in
> which every case runs 1.5× long, which is itself the reportable finding of
> §5.3. **This is a judgement of this lane, it is registered before compute so it
> cannot be chosen to fit the outcome, and a supervisor or Sanaa is entitled to
> overrule it — in which case the twelve points must be re-registered at a
> per-case cap of 25.0 core-min, which is BELOW the measured 30.03 per-case cost
> and therefore caps every case before it finishes.** That arithmetic is stated
> precisely because it shows the alternative is not available, rather than merely
> asserting that it is not.

### 5.5 The calibration owed at completion

Rule 12's estimate-versus-actual clause (Sanaa 2026-08-23) binds this rung. At
completion the results record must carry **actual core-minutes** from each case's
own `log.solve` `ExecutionTime` line as `wall_s × ranks ÷ 60` (**not** from
`STATUS`, per §3.5a), the **ratio actual/predicted against the REGISTERED 360.4
and 30.0321**, the attribution split between **contention, waste and
misprediction with waste named separately and never folded into the ratio**, and
a row appended to `docs/COST_CALIBRATION.md`. **The figure this rung exists to
calibrate is no longer the per-cell rate — T23 measured that — but whether that
rate SURVIVES A THREEFOLD INCREASE IN CONCURRENCY** (§5.3). *A completion report
without this comparison is incomplete.*

**REGISTERED, one-way and before the fact, carried unchanged from T23 §5.4: a run
whose recorded load average at launch shows a saturated box produces a COST but
NOT a calibration row.** After the fact a contended number is indistinguishable
from a mispredicted one. **The instrument is `START.<case>`, and this time the
launcher writes it** (§3.5b): `start_utc`, all three `/proc/loadavg` windows,
`nproc`, and the count of solver processes already running.

> **AND THE SATURATION THRESHOLD IS REGISTERED AS A NUMBER, not left to
> judgement: a case whose `START.<case>` records a 1-minute load average above
> `nproc` (16) at its own launch instant produces a COST but NOT a calibration
> row of its own**, and is named in the completion report as excluded and why.
> **This is expected to exclude some of the twelve by construction** — the later
> launches in a twelve-deep queue see the earlier ones running — and registering
> that expectation in advance is what stops it being read afterwards as a defect.

---

## 6. THE REGISTERED RUN SET

### 6.1 Why all twelve, and why now

1. **Both of `T23_PREREGISTRATION.md` §6.4's named preconditions are
   discharged** (§0.2), by MEASURED artifacts, and §6.4 registered that
   discharging them is what makes the twelve writable.
2. **The cost is measured on this geometry** (§5.1), so the map can be capped
   honestly for the first time — which §5.4 shows was the blocking question.
3. **Sanaa's 2026-08-31T15:45Z standing order that the box must be full**
   (`etc/sessions/2026-08-31T1545Z_sanaa_box_full.md`). At the time this document
   is written the box carries **zero solvers and a 1-minute load average of
   0.21 on 16 cores, with all six team queues at depth 0** [MEASURED]. **Idle
   compute is the failure.**

### 6.2 **THE REGISTERED RUN SET — twelve cases, named**

> **REGISTERED: twelve cases, `T24_P<P>_U<U>` for
> P ∈ {80, 155, 230} W × U ∈ {10, 20, 30, 40} m/s —
> `T24_P080_U10`, `T24_P080_U20`, `T24_P080_U30`, `T24_P080_U40`,
> `T24_P155_U10`, `T24_P155_U20`, `T24_P155_U30`, `T24_P155_U40`,
> `T24_P230_U10`, `T24_P230_U20`, `T24_P230_U30`, `T24_P230_U40` —
> at L1, 1 rank, `endTime` 10000, per-case cap 45.0 core-min enacted as
> `timeout 2700s`.**

The naming pads the power to three digits (`P080`) so that a lexical sort of the
twelve case directories is also a numerical sort of the power levels; T23's
`T23_P305_U*` needed no padding because it carried one level.

### 6.3 **THERE IS NO LAUNCH PRECONDITION, AND THAT IS ITSELF REGISTERED**

T23 §6.3 registered a launch precondition — *no T23 case is launched until
`T22_CHTb_L1` has reached its registered `endTime` with `rc = 0` and an `End`
line* — because **this geometry had never completed a solve.**

> **REGISTERED: T24 carries NO launch precondition, because the feasibility
> question that precondition existed to answer is ANSWERED.** Four cases of this
> exact geometry, mesh and solver completed all six rule-4 conjuncts under a
> frozen registration [MEASURED, §0.2]. **Registering a fresh precondition here
> would be ceremony, and dropping one silently would be worse; so the drop is
> registered with its reason.**

### 6.4 What the twelve points are FOR — and it is not B1

**REGISTERED, and this is the honest statement of what this rung earns:**

| what the twelve points deliver | status |
|---|---|
| **the twelve missing `T_max` values of the 16-point map** — the directive's *"can I hold this power at this airspeed"* surface, at L1, on solved physics | **THE DELIVERABLE** |
| twelve B1/B2/B3 verdicts on the registered physicality tier | delivered, and **B1 is predicted to be uninformative** (§1 line 4) |
| a **falsifiable test of the linear-source prediction** of §2.4 at twelve points and three power levels | delivered — **the only thing in this rung that can be surprised** |
| the measured answer to whether the T23 per-cell rate survives twelve-concurrent contention (§5.3, §5.5) | delivered as a **calibration**, subject to §5.5's saturation exclusion |
| the 120 °C isotherm traced across the map | **NOT delivered** — §2.3(b), §4.5: predicted to lie off the map entirely |
| Nusselt, Roache triple, GCI, observed order, heat balance, radiative bound | **NOT delivered** — §4.1–§4.3, §4.6 |

### 6.5 The registered report

**REGISTERED: the results record must carry, for each of the twelve rows:** Q1,
Q2, Q1 − Q2, the B3/B2/B1 verdicts with B1's margin, the §2.4 predicted `T_max`
and the measured-minus-predicted departure as a percentage of the predicted rise,
the measured max y+ on `fluid_to_housing` (reported, never gated), the final
asserted residuals with `Ux` printed and excluded per §7.1, the per-case
core-minutes derived from `log.solve`, and the `START.<case>` load reading.
**And it must carry the full 16-point map assembled from T23's four rows and
these twelve, with each row's provenance rung named**, because a map that does
not say which rung measured which row is not auditable.

---

## 7. **TWO INSTRUMENT TRAPS ARE CARRIED AS REGISTERED GUARDS, NOT REDISCOVERED**

### 7.1 **`Ux` IS EXCLUDED FROM THE CONVERGENCE ASSERTION, AND THE GROUND IS MEASURED PER CASE**

**In this 5° wedge `x` is the CIRCUMFERENTIAL direction, the mesh is one cell
thick with `wedge` patches front and back, and `Ux` is identically zero BY
GEOMETRY.** Its linear-solver residual is normalised by its own field scale, and
when that scale is machine zero the ratio is noise of order one. T23 measured
**max|Ux|/max|Uz| between 1.561e-16 and 2.189e-16** across its four cases while
the final `Ux` initial residual read between **3.10e-02 and 1.40e-01**
[MEASURED, `T23_RESULTS.md` §3].

**A reader who greps the last `Ux` residual and stops there reports EVERY run of
this family as unconverged.**

> **REGISTERED, before compute: the convergence assertion is taken over `Uy`,
> `Uz`, `h`, `p_rgh`, `k` and `omega` at 1e-06 on the last `Time = 10000` block
> of each case's own `log.solve`. `Ux` IS EXCLUDED, and the exclusion is
> justified PER CASE by that case's OWN measured max|Ux|/max|Uz| ratio, never
> recited from T23 — a ratio above 1e-12 REFUSES the exclusion for that case and
> the row reports `Ux` asserted.**
>
> **THE EXCLUDED VALUE IS PRINTED, NEVER SUPPRESSED**, beside the ratio that
> justifies it. **THE EXCLUSION CHANGES NO GATE, BECAUSE T24 REGISTERS NO
> RESIDUAL GATE AT ALL** — §3.1 registers convergence as an assertion on the log
> and never as a stopping rule, and no band in §1 line 4 reads a residual.
> **A control confirming that, had `Ux` been asserted, a forged case would report
> NOT converged is driven in the grader's selftest**, so the exclusion is shown to
> be load-bearing rather than assumed to be.

### 7.2 The `yPlus` false zero

Registered in full at §4.4: the generic `postProcess -func yPlus` route returns
**rc 0 and an all-zero y+** after printing that it cannot see the turbulence
model. **The solver's own `-postProcess` route is registered instead, with the
BLIND-log guard carried and BOTH LIMBS DRIVEN** in the grader's selftest.

---

## 8. AUTHORITY, AND WHAT IS NOT CLAIMED

Filed by a heat-transfer `lab-lane` at the heat-transfer-supervisor's dispatch,
under **Sanaa's ruling "5. Rescale"**
(`etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md`, the chief's verbatim
capture of her own words, read at source), her **2026-08-31T15:45Z standing order
that the box must be full** (`etc/sessions/2026-08-31T1545Z_sanaa_box_full.md`),
and her **2026-08-26 universal rule that bookkeeping never voids physics**.

**Sanaa's 14-day rule freeze is honoured**
(`etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`, read at source):
**this document proposes NO new procedural or bookkeeping rule and creates NO new
tool.** Every instrument it registers is an existing lab pattern applied to a new
rung — the planted-zero control of §3.6, the completion rule of §3.5, the
`DERIVED-FROM-LOG` rc derivation T23 already used, the mesh gates of
`MESH_STANDARD.md`, the private-index commit protocol. The `START.<case>` write
of §3.5b is **T23 §5.4's own registered text implemented**, not a new mechanism.
The findings of §2.3 (the level set spans neither threshold on solved physics),
§4.2 (`CASE3-DEP-1` still unregistered), §5.1 (the Cartesian anchor is a bracket
and not a lower bound), §5.3 (the concurrency risk) and §5.4 (the cap reading
that does not dissolve) are **recorded as findings and spawn no rule and no
tool.**

**A supervisor's check is not claimed as performed here.**
`SUPERVISION_CHARTER.md` §3 check 4 — pre-registration **committed** before
compute — is the supervisor's own and is **NOT claimed by this lane.** What this
lane asserts is narrower and is checkable: **the run directories of §0.5 were
measured absent under a live planted control in the invocation that commits this
file**, and no compute has been launched against these gates.

**ENQUEUEING IS NOT AUTHORISATION**, and neither is this document's existence.

**No agent's message is Sanaa's consent** (`CLAUDE.md` rule 9). The session files
cited above are the chief's verbatim capture of her own words and are cited as
such, and nothing in them is read as widening any authorisation beyond the item
it names. **The supervisor's four registration decisions that this document
implements are a SUPERVISOR's decisions, recorded as such — they are not Sanaa's
consent and are not represented as such**, and where one of them did not survive
contact with the arithmetic it is corrected on this document's face rather than
implemented as stated: **§5.2 registers a headroom of 1.4984×, not 1.5×, and
§5.4 registers that the directive's cap inconsistency dissolves on the
expected-spend reading and NOT on the cap reading.**
