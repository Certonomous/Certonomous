# T23 — Case 3 motor-in-duct CHT: the RESCALED P_loss × U_inf map: pre-registration

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

Sanaa's **CASE 3** (`etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md`
§§3.1–3.7), **variant (b)**: motor-in-duct conjugate heat transfer, actuator disk
absent, annulus velocity imposed by `U_inf`. The subject is the directive's
**"can I hold this power at this airspeed" map** — `T_max` on the aluminium
housing as a function of dissipated power and airspeed — at mesh level **L1**.

**This rung exists because Sanaa ruled the map's power levels RESCALED.** Her
answer, captured verbatim by the chief at receipt
(`etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md`, answer 5): **"5. Rescale"**,
against the question *"Case 3 P_loss sweep is RESCALED (pre-compute registration
change, heat-transfer chooses honest levels and states them as assumptions)"*.
**§2 of this document is that rescale, and §2.6 states the levels as assumptions
exactly as she required.**

### 0.2 What this rung is NOT — stated first

> **T23 registers the PHYSICALITY TIER of the map and NOTHING ELSE.** It earns
> nothing about the Nusselt correlation tier, nothing about the map's Roache
> triple, nothing about grid convergence, and nothing about the heat-balance
> instrument. Those are separate rungs with separate registrations, and this
> document may not be cited as covering them. §4 lists each deferral with its
> reason.

**T23 does not supersede or amend T21.** `T21_PREREGISTRATION.md` is the
flow-off EXACT-tier solid-conduction rung and is **an uncommitted DRAFT that
freezes nothing** (its own header: *"DRAFT. NOT FROZEN. NOT COMMITTED.
AUTHORISES NOTHING."*). T21 §0.2 states in terms that it registers *"nothing
about the 16-point P_loss × U_inf map. Those are separate rungs with separate
registrations and this document may not be cited as covering them."* **T23 is
that separate registration.** Nothing in T21 is relied on here, and freezing
T21 later changes nothing in this document.

**T23 does not grade T22.** `T22_CHTb_L1` is an UNREGISTERED **FEASIBILITY**
rung under Sanaa's 2026-08-31T15:51Z queue ruling; its own note
(`verification/runs/T-family/T22_runs/T22_FEASIBILITY_NOTE.md`) states that it
produces no graded value, reaches no band, and that **nothing it produces may be
carried into a future graded T22 rung**. That prohibition is honoured here in
its strongest form: **no number T22 emits enters any gate, band, threshold or
referent in this document.** T22 appears below in exactly two roles, both
non-evidentiary: as the **launch precondition** of §6.3 (a statement about
whether the solver runs at all, not about any value it produces), and as the
**geometry and case-construction pattern** the T23 cases are built from.

### 0.3 The id — taken from the MAXIMUM, never from a count

`CLAUDE.md` rule 11 by analogy. Re-derived over
`docs/campaigns/T-family/` ∪ `verification/runs/T-family/`, the maximum existing
top-level `T`-number is **22**, so this rung is **T23**. The set present is
{1,3,4,5,6,8,9,10,11,13,14,15,16,17,18,19,20,21,22} — **nineteen ids with a
maximum of 22, which is exactly why a count is not the rule.**

**A precision the derivation itself turned up, recorded rather than smoothed
over:** that set is taken **over files on disk**. A **tracked-only** derivation
returns **eighteen** ids, not nineteen, because **`T21_PREREGISTRATION.md` is
untracked** — it is the uncommitted draft of §0.2. **The maximum is 22 under
both readings**, so the id is unaffected; the two counts are recorded because
they differ, and a reader who re-derives by the other path must not think the
number moved.

**This derivation is re-taken in the committing invocation**, in the same shell
invocation as the write, because peers take numbers constantly and a derivation
taken minutes earlier is a fact about a different tree.

Run root **`verification/runs/T-family/T23_runs/`** per the filing charter's
R6. `scripts/check_filing.py` accepts `T23_PREREGISTRATION.md` under
`docs/campaigns/T-family/` on the same basename pattern that accepts
`T20_PREREGISTRATION.md` and `T21_PREREGISTRATION.md`.

### 0.4 **THE RULE-2 PRE-COMPUTE CONDITION, STATED BY NAMING THE RUN DIRECTORIES THAT DO NOT EXIST**

`CLAUDE.md` rule 2: *before first compute, amendments are legal and must state
the condition and how it was checked (name the run directory that does not
exist).* The condition is stated here, and **re-verified in the committing
invocation**, because a condition measured minutes earlier is a fact about a
different tree.

**THE CONDITION:** *no compute has run under any Case 3 sweep registration.*

**HOW IT IS CHECKED — by naming the three directories that do not exist:**

| directory that must be ABSENT | why it is the right directory to name |
|---|---|
| `verification/runs/T-family/T23_runs/` | **this rung's own run root.** If it exists, this document is being written after its own compute and §1–§6 are closed to change. |
| `verification/runs/T-family/T21_runs/` | T21's run root. T21 is the only other document in the tree that mentions the map, and it disclaims it; if T21 had run, a Case 3 registration would exist with compute behind it. |
| `verification/runs/T-family/CASE3_SWEEP_runs/` | the name a sweep filed outside the `T` numbering would have taken. Naming only the two `T` roots would leave a directory this condition is about unchecked. |

**MEASURED 2026-08-31, and RE-MEASURED in the committing invocation, under a
LIVE PLANTED CONTROL** (`CLAUDE.md` rule 3): all three **ABSENT**. The identical
predicate was run against a synthetic directory that **does** exist and returned
PRESENT, so the reader was **shown able to see a non-zero before its zero was
believed.** A zero from a reader not shown able to see a non-zero is not
evidence.

**A CORRECTION CARRIED FORWARD RATHER THAN REPEATED.** The commit that landed
the level-rescale generator (`173d797c`) asserted as its rule-2 evidence that
*"a grep for the 16-point map returns zero files"*. **That sentence is false**;
it was corrected at `b87eb07d` and in the generator's own docstring
(`rescale_case3_sweep_levels.py:19-42`). The grep returns **11 files**: nine are
`snappyHexMesh` logs containing the literal string `"16 points"`; one is
`build_t22.py:6` naming a single benign point; and two are
`T21_PREREGISTRATION.md:51` and `:106`, **both of which disclaim the map**. The
conclusion was unchanged and is now better supported, which is exactly why the
false evidence had to be struck rather than left standing. **The condition this
document registers is the ABSENT-RUN-DIRECTORY condition above, which is a
direct `ls`, not a grep, and is unaffected by that error.**

---

## 1. THE TEMPLATE — the ten registered lines

**1. CASE.** Case 3 variant (b), L1. Three regions: `fluid` (duct annulus, air),
`housing` (aluminium hollow cylinder r_i = 0.0335 m → r_o = 0.0375 m,
L = 0.125 m), `core` (representative winding/lamination pack, k 40 W/mK, with a
uniform volumetric source). **2-D axisymmetric wedge, θ = 5.0°**, one cell
circumferentially. Two conjugate `mappedWall` interfaces (fluid/housing and
housing/core). Solver **`chtMultiRegionSimpleFoam`**, OpenFOAM **v2606**.
`kOmegaSST` in the fluid (directive §3.4). Run root
`verification/runs/T-family/T23_runs/`.

**Declared scope limits, carried from the case construction and repeated here so
the registration carries them on its own face:** the **nose and tail cones of
directive §3.2 are REMOVED** — the centrebody is a constant-radius tube and only
its middle 0.125 m is conjugate; the **duct wall is adiabatic** (directive §3.3);
**radiation is OFF** and is a disclosed omission; **g = (0 0 0)** — see §3.4,
which is not a convenience but the fact that voids one of the directive's own
checks.

**2. REFERENCE.** **NONE, and that is the point of this tier.** The physicality
tier has **no external referent**: it compares the solved `T_max` against a
**registered engineering bound** (200 °C) and a **registered isotherm** (120 °C),
both of which are Sanaa's own numbers from directive §3.6 and neither of which is
a measurement of anything. **No paper is cited as a source of constants and none
is required.** The two closed-form correlations of §2 are used **only to choose
the levels before compute** and are **NOT referents**: nothing is graded against
them, and §2.7 registers in advance that they may be wrong.

**3. QUANTITIES.**

| id | quantity | read from |
|---|---|---|
| **Q1** | `T_max` = max(T) over the whole `housing` region, °C | `internalField` of `<endTime>/housing/T` |
| **Q2** | `T_iface` = areaAvg(T on the `housing`-side of the fluid/housing interface), °C | `boundaryField` of `<endTime>/housing/T` |

Q1 and Q2 are **two readers of the same solution on different code paths**
(`internalField` vs `boundaryField`) with **different pre-derived extents**, the
anti-degeneracy control this family established at T20 §4.4 and T21 §4.4.
**REGISTERED PREDICTION: Q1 ≥ Q2, and the two must DIFFER.** The housing's
hottest cell is on its inner surface, adjacent to the core; the fluid interface
is its outer surface. **If Q1 and Q2 return identical values the two readers are
reading the same object twice**, and that is a finding about the instrument, not
about the solver, and makes the affected rows **NOT A RESULT**.

**4. BANDS — and this tier's gate is a BOUND, not a band.** The physicality gate
of directive §3.6 is a one-sided sanity bound with an explicitly named
consequence, and it is registered in the directive's own words:

> *"T_max < 200 C sanity (else the point is flagged as 'beyond assumption range'
> — a real finding)."*

**REGISTERED, and this is the clause that must not be engineered against:**

| # | registered threshold | label if met | label if not met |
|---|---|---|---|
| **B1** | Q1 < **200.0 °C** | **PASS** for that point | **PASS, FLAGGED "beyond assumption range"** |
| **B2** | Q1 > 0.0 °C (no negative temperatures, directive §3.6) | PASS | **GATE FAIL** |
| **B3** | Q1 ≥ Q2, and Q1 ≠ Q2 (§1 line 3 anti-degeneracy) | PASS | **NOT A RESULT** |

**B1's "not met" branch is a FLAGGED PASS and NOT a GATE FAIL, and that is
registered here before compute so it cannot be re-read afterwards.** Directive
§3.6 makes an over-bound point *"a real finding"*, not a failure — the physics is
being reported, not the model being falsified. **Zero flags was never the
requirement of this tier and must not be engineered for.** §2.5 records that the
directive's own original levels flag **9 of 16** under one estimator, that the
rescale reduces this to **2 of 16**, and that reducing it to zero is
**impossible** while still bracketing the 120 °C isotherm (§2.3).

**5. LADDER.** **NONE IN THIS RUNG. There is no grid triple here and none may be
inferred.** Every point runs at **L1 only**. Any Roache classification, GCI or
observed order quoted from a T23 artifact is a category error: **a single mesh
level admits no triple**, and `CLAUDE.md` rule 5 governs a triple this rung does
not produce. See §4.2.

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
4. **B2** then **B1** — as tabulated in §1 line 4.

**A gate may only turn a PASS into NOT A RESULT, never the reverse.**

**8. COST.** Registered in §5. **SUBSET POINT 123.2 core-min, SUBSET CAP 400.0
core-min hard.** An overrun **stops the run**; it does not get a new budget
(`CLAUDE.md` rule 12, `COMPUTE_BUDGET_CHARTER.md`:197).

**9. ABSENT REGISTRY.** §0.4, re-measured under a live planted control in the
committing invocation.

**10. AUTHORISATION.** This document authorises the **four cases of §6.2 and no
others**, and only once the §6.3 launch precondition is met. It authorises no
point of the twelve deferred in §6.4.

---

## 2. THE RESCALE — Sanaa's answer 5, and the arithmetic behind it

### 2.1 The instrument used to choose the levels, and its standing

Levels were chosen with a **closed-form lumped series-resistance model** —
`docs/campaigns/T-family/rescale_case3_sweep_levels.py`, which **runs no solver**.
Every number in §2 is **DERIVED** from the directive's own `REGISTERED`
material and geometric inputs plus one `ASSUMED` input (`r_bore` = 6 mm, whose
effect is bounded at ±1.4 K over a 150× range and therefore decides no flag).

    R_tot(U) = 1/(h(U)·A_housing) + R_wall + R_core        [K/W, DERIVED]
    T_max(P,U) = T_inf + P·R_tot(U)                        [K, DERIVED]

with `R_wall` = 8.599742e-04 K/W, `R_core` = 1.410124e-02 K/W,
`A_housing` = 0.029452 m², `T_inf` = 288 K, all **DERIVED** from directive
§§3.2–3.3.

**Two convective closures are carried, never one**, because the choice between
them moves `T_max` by tens of kelvin and no single one of them may be allowed to
decide a level:

| closure | form | role |
|---|---|---|
| **Dittus-Boelter** on the annulus hydraulic diameter D_h = 0.175 m | 0.023 Re^0.8 Pr^0.4 k/D_h | **PESSIMISTIC** (low h, hot) |
| **flat-plate average** over the housing length L = 0.125 m | 0.037 Re^0.8 Pr^(1/3) k/L | **OPTIMISTIC** (high h, cool) |

**The two differ by a factor of 1.763 in h at every airspeed** (both scale as
Re^0.8, so the ratio is U-independent) — **DERIVED**. That factor is the single
most important number in this section and §2.7 registers its consequence.

### 2.2 **INDEPENDENT RE-DERIVATION — the figures below are not one script's output**

Every load-bearing figure in §2 has been reproduced by **three separate paths**
before being registered:

1. the generator script above;
2. **the heat-transfer supervisor**, who reproduced the incompatibility factor as
   **1.674×** from the published table by a path not using that script;
3. **this lane**, by an independently typed implementation with the literals
   re-entered from the directive and the algebra ordered differently, returning
   **1.6723× (DB) / 1.6374× (FP)**, `h_FP/h_DB` = **1.7628**, and the flag
   counts of §2.5 exactly.

The 1.672 / 1.674 spread is **table rounding in path 2**, not a disagreement.
**A figure that only one implementation has ever produced is not registered in
this document.**

### 2.3 **THE STRUCTURAL INCOMPATIBILITY — why NO full-factorial rectangle can clear the bound**

This is the finding that forced the rescale, and it is a **measured property of
the directive's own two requirements**, not an opinion:

| closure | to **BRACKET** the 120 °C isotherm at U = 40 m/s, max(P) must be ≥ | to keep **every** point under 200 °C at U = 10 m/s, max(P) must be ≤ | ratio |
|---|---:|---:|---:|
| Dittus-Boelter | **300.5 W** | **179.7 W** | **1.672×** |
| flat plate | **512.9 W** | **313.3 W** | **1.637×** |

All figures **DERIVED**, unit W. **The two requirements are incompatible by a
factor of 1.637–1.672, and the incompatibility holds under BOTH closures, so it
is not an artefact of the h model.** Directive §3.6 asks for *both* the 200 °C
sanity bound *and* the 120 °C hold-this-power isotherm traced across the map;
on a full-factorial `P × U` rectangle, **the top P level required to reach the
isotherm at the fastest airspeed necessarily exceeds the top P level allowed
under the bound at the slowest airspeed.**

**The minimum unavoidable number of flagged points on any bracketing rectangle
is 1 (DB).** Zero is not attainable. This is registered here so that no later
reader can treat a non-zero flag count as a defect in the level choice.

### 2.4 The two isotherms in full, as P at which T_max reaches each threshold

**DERIVED**, unit W:

| | U = 10 | U = 20 | U = 30 | U = 40 |
|---|---:|---:|---:|---:|
| **120 °C isotherm**, DB | 102.0 | 175.8 | 240.8 | **300.5** |
| **120 °C isotherm**, FP | 177.9 | 304.1 | 413.7 | 512.9 |
| **200 °C bound**, DB | **179.7** | 309.5 | 424.0 | 529.1 |
| **200 °C bound**, FP | 313.3 | 535.4 | 728.5 | 903.2 |

### 2.5 **THE ORIGINAL LEVELS FLAG 9 OF 16, NOT 8 — a board figure corrected on this document's face**

Directive §3.3's original levels are **{100, 300, 600, 1000} W**. Against the
200 °C bound, at the four registered airspeeds:

| level set | flags under **DB** | flags under **FP** |
|---|---:|---:|
| **ORIGINAL {100, 300, 600, 1000}** | **9 of 16** | **6 of 16** |
| **RESCALED {80, 155, 230, 305}** | **2 of 16** | **0 of 16** |

**The lab board's figure of "8 of 16" is WRONG and is corrected here.** The nine
DB-flagged original points, enumerated so the count can be audited rather than
believed: **(300,10), (600,10), (600,20), (600,30), (600,40), (1000,10),
(1000,20), (1000,30), (1000,40)**. The six FP-flagged: **(600,10), (600,20),
(1000,10), (1000,20), (1000,30), (1000,40)**. Both enumerations are **DERIVED**
and both reproduce on the independent path of §2.2.

The two RESCALED DB flags are **(230,10)** and **(305,10)** — both at the slowest
airspeed, which is where §2.3 proves a flag is unavoidable.

### 2.6 **THE REGISTERED LEVELS, STATED AS ASSUMPTIONS — as Sanaa required**

> **REGISTERED: P_loss ∈ {80, 155, 230, 305} W. ASSUMED, not measured, not
> derived from any motor.**
>
> **REGISTERED: U_inf ∈ {10, 20, 30, 40} m/s. UNCHANGED from directive §3.3.**

Directive §3.3's own words about the original levels — *"(Loss levels chosen as
representative of a small EDF motor class; state as assumptions.)"* — bind the
replacements identically, and this is that statement. **These four power levels
are a judgement of this lane. They are not measured, they are not any real
motor's dissipation, and no result graded against them may be reported as
characterising a physical machine.** What they are chosen to do, and the only
thing they are chosen to do, is span the two registered thresholds of §2.4 at
usable resolution:

| property of the set | value | why it was the selection criterion |
|---|---|---|
| DB flags | **2 of 16** | against 9 for the originals; 1 is the proven floor (§2.3) |
| FP flags | **0 of 16** | the optimistic closure clears the bound entirely |
| 120 °C isotherm bracketed at | **all four airspeeds** | directive §3.6 requires the isotherm traced across the map; a set that brackets it at only some airspeeds cannot deliver it |
| widest isotherm-crossing gap | **75 W** | the resolution with which the hold-this-power boundary can be located; the best of the five candidate sets considered |

Four candidate sets were evaluated and rejected, and they are recorded so the
choice is auditable rather than asserted: `{100,300,600,1000}` (9 DB flags);
`{50,100,200,300}` (2 flags but brackets the isotherm at only three of four
airspeeds — **it cannot deliver directive §3.6's isotherm at U = 40**);
`{60,120,200,320}` (3 flags, 120 W gap); `{80,130,175,305}` (**1** flag — the
minimum — but a **130 W** isotherm gap, i.e. it buys the proven-minimum flag
count by halving the resolution of the very boundary the map exists to locate).
**`{80,155,230,305}` was chosen over the min-flag set deliberately**, because
§1 line 4 registers a flag as a finding rather than a failure, and trading the
map's resolution for a cosmetically lower flag count would be engineering
against the gate.

### 2.7 **(305 W, 20 m/s) IS UNDECIDED BY THIS INSTRUMENT — REGISTERED IN ADVANCE**

**DERIVED margins to the 200 °C bound at that point:**

| closure | T_max at (305 W, 20 m/s) | margin to 200 °C |
|---|---:|---:|
| Dittus-Boelter | **197.3 °C** | **+2.70 K** |
| flat plate | 120.3 °C | +79.67 K |

> **REGISTERED, BEFORE COMPUTE: the point (305 W, 20 m/s) is UNDECIDED by the
> level-selection instrument, and it MAY LEGITIMATELY FLAG UNDER B1 WHEN
> SOLVED.** A **+2.70 K** margin on a model whose two closures disagree by
> **1.763× in h** — tens of kelvin in `T_max` — is not a prediction. **If that
> point returns above 200 °C it is a FLAGGED PASS under §1 line 4 and a real
> finding, and it is NOT evidence that the levels were chosen badly.**

This is registered in advance for one reason: **after the fact, a +2.7 K miss is
indistinguishable from a level-selection error**, and the temptation would be to
read it as one. Two further points sit within 50 K of the bound under DB and are
named for the same reason: **(155, 10) at +25.4 K** and **(230, 20) at +47.6 K**.

---

## 3. WHAT THE SOLVED CASES MUST SATISFY

### 3.1 The registered iteration count, and why no `residualControl` is registered

**REGISTERED: `endTime` 10000 SIMPLE iterations** (directive §3.4's
*"iteration cap 10,000"*), `writeInterval` 10000, **no `residualControl`
stopping criterion in any region's `SIMPLE` dict.** Convergence is an
**ASSERTION on the log**, never a stopping rule.

**This is a post-mortem, not a precaution, and the corpse is this family's own.**
T19's `P_q_c` and `P_Ts_c` carried `residualControl { p_rgh 1e-9; U 1e-9;
T 1e-9; }` against a registered `endTime` of 30000 and **stopped at 828 and 541
iterations — under 3 % of their registered duration — both reporting `rc=0` and
`note=clean`.** They did not crash; **they succeeded at the wrong experiment.**
An early residual exit leaves the last time directory below `endTime`, so rule 4
conjunct 3 cannot hold, and any control comparing two late writes loses its pair
and becomes **unevaluable, which is worse than failing** — a failing control is
a finding and an unevaluable one is a silence.

**REGISTERED, and paid for honestly:** running the full count is not free. Every
iteration after convergence is paid for, that cost is inside the §5 POINT, and
a padded `endTime` is paid for in full on every one of the four cases.

### 3.2 Registered write precision

**REGISTERED: `writeFormat ascii`, `writePrecision 12`, `writeCompression off`,
`timePrecision 12`.** OpenFOAM's default `writePrecision 6` gives a write quantum
of **1.0 mK** at T ≈ 400 K. This tier's bound is 200 °C and its margins are tens
of kelvin, so the quantum is **not** binding on B1 — but it **is** binding on
**B3**, the anti-degeneracy control, whose entire content is that two readers of
the same field must return **different** numbers. At `writePrecision 6` two
genuinely different values can round to the same string and B3 fails as a
false positive. **The precision is registered for B3, and the reason is recorded
here rather than left in a comment.**

### 3.3 `constant/g` is mandatory and its value is a declared decision

`chtMultiRegionSimpleFoam` reads gravity at **file scope** in
`createFluidFields.H:26`, before the region loop opens at `:29`, with
`IOobject::READ_MODIFIED`, which requires the file present. **REGISTERED:
`constant/g` present in every T23 case with `value (0 0 0)`.**

### 3.4 **THE DIRECTIVE'S RICHARDSON CHECK IS VACUOUS IN THIS CASE — DISCLOSED, NOT REPORTED AS PASSING**

Directive §3.3 requires *"verify Richardson number Ri = g β ΔT L / U² < 0.1 on
every run; if Ri > 0.1 anywhere, the buoyant solver variant is required and the
run is re-registered."*

**With `g = (0 0 0)` registered in §3.3, Ri ≡ 0 identically, by construction, at
every point of the map.** The check therefore **cannot fail and cannot inform**.

> **REGISTERED: the Ri < 0.1 criterion is DECLARED VACUOUS for T23 and is NOT
> reported as a passing check.** Reporting `Ri = 0 < 0.1, PASS` would be
> `EVIDENCE ANNOTATED AS NON-BINDING` in its worst form — a criterion satisfied
> by the modelling choice that removed the physics it was meant to police.
> **What is registered instead is the honest statement: buoyancy is switched OFF
> in T23 by the `g = (0 0 0)` choice, its neglect is a declared omission, and
> whether forced convection genuinely dominates at (80 W, 10 m/s) — the
> lowest-power, lowest-airspeed corner, where the ratio is least favourable —
> is NOT established by this rung.**

### 3.5 Rule 4 completion, in its steady form

`CLAUDE.md` rule 4 is **all-or-nothing**; the grading pass **refuses (exit 2)
rather than degrades**.

| # | conjunct | how it is evaluated here |
|---|---|---|
| 1 | `rc = 0` | captured **inside** the detached wrapper on the line immediately after the solver call and written to `STATUS.<case>`. **Never around a `setsid` line** — `setsid timeout cmd` exits 0 for every outcome |
| 2 | an `End` line | `grep -c '^End$' log.solve` == 1 |
| 3 | last time == `endTime` | the numerically greatest time directory equals **10000** |
| 4 | fields present | **`T`, `p` in `<endTime>/core/` and `<endTime>/housing/`; `T U p p_rgh alphat nut k omega` in `<endTime>/fluid/`.** The core and housing are solid regions and the fluid field list does not apply to them |
| 5 | `ExecutionTime` count == `endTime` | evaluated as `count == 10000` at `deltaT 1` |
| 6 | **age guard** | every field at `endTime` **newer** than that case's own `0/housing/T` by `st_mtime`; the launcher touches it last. The launcher **refuses** a case where `0/` or any time directory already exists |

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
5. **The only sizing tolerance is RELATIVE:** REFUSE if the read at `PLANT` is
   below `0.1 × PLANT`. T3's absolute `PLANT − 1e-15` is **NOT adopted**: on a
   ~400 K field that window is a fraction of one ULP and the outcome would be
   decided by a rounding wiggle.
6. **`PLANT = 1.234e-03 K`, IMPORTED from `scripts/roache_triple.py`**, never
   redefined locally.
7. **The plant is located STRUCTURALLY, by line index from the field's own
   header, never by value.** Q1 takes the plant in the hottest `internalField`
   cell; Q2 takes it in every face of the target patch, so Q2's expected shift is
   exactly `PLANT` and not `PLANT/N`. The number of values planted is recorded
   in the output.
8. Original bytes restored from the in-memory copy; the scratch tree removed in
   a `finally`.

**A refusal here makes the WHOLE RUNG `NOT A RESULT`.** An instrument that
cannot see a planted perturbation is not entitled to certify a bound.

---

## 4. WHAT IS DEFERRED, AND WHY — each with its reason

**Every deferral below is a scope limit registered before compute, not a result
that came out badly.**

### 4.1 The Nusselt correlation tier — DEFERRED

Directive §3.6's second bullet grades mean Nusselt on the housing at (300 W,
20 m/s) against an annular-flow correlation to 25 %. **Deferred**, three
reasons, each independently sufficient: (a) **its registered operating point,
300 W, is not a level of the rescaled set** — the rescale moved the top level to
305 W, so the correlation tier's own point must be re-registered against the new
levels and that is a decision, not a formality; (b) directive §3.6 requires
*"verify applicability range on the page"*, i.e. a **title-page-verified paper**
(`CLAUDE.md` rule 15) that this lab does not hold for annular flow; (c) it needs
a wall-Nusselt instrument that does not exist.

### 4.2 The map's Roache triple — DEFERRED, and it is BLOCKED

Directive §3.6's third bullet requires a grid triple on `T_max` at (300 W,
20 m/s) with p ∈ [1.3, 2.5] and GCI_fine < 2 %. **Deferred, and recorded as
`BLOCKED`**: `T21_PREREGISTRATION.md:54-57` records a cross-team dependency,
**`CASE3-DEP-1` (cfd's Case 2 centerbody)**, as `PENDING` and as gating *"the
correlation tier and the Roache triple of the map"*.

> **A DISCLOSURE THIS LANE MAKES RATHER THAN HIDES: `CASE3-DEP-1` IS NOT
> REGISTERED ANYWHERE THIS LANE CAN FIND.** A search for that identifier across
> `docs/` and `verification/` returns **zero files** other than the T21 draft
> that names it. So the dependency is asserted in an **uncommitted draft that
> freezes nothing** and has no registered existence of its own. **That is a
> defect in the dependency's filing, and it is reported rather than resolved
> here** — resolving it is a cross-team question and, under
> `ESCALATION_CHARTER` §4.1, not this lane's to settle. Its practical effect on
> T23 is nil, because §1 line 5 registers no ladder in this rung for the
> independent reason that a single mesh level admits no triple at all.

### 4.3 The heat-balance gate — DEFERRED

Directive §3.4 requires closure to 1 % via *"the mutation-tested heat-balance
instrument"*. **Deferred: that instrument does not exist for this case.** T21
§5.2a registers the general reason such an instrument belongs **downstream** of
the solve until one run has demonstrated it: an inline function object that fails
does so at **construction**, before the first iteration, and takes the entire
solve with it, whereas a `postProcess` pass that fails costs nothing because the
fields are already on disk. **REGISTERED: no `wallHeatFlux` function object is
placed in any T23 `controlDict`.**

### 4.4 The y+ ≤ 1 requirement — REPORTED, NOT GATED

Directive §3.4 requires y+ ≤ 1 on the housing surface and states that *"wall
functions are NOT acceptable on the gated levels"*. **The T23 cases carry the
L1 near-wall grading intended to deliver it, but y+ is a SOLVED quantity: it
cannot be known before the run.** **REGISTERED: max y+ on the housing is
MEASURED and REPORTED beside every row, and is NOT a gate in this rung.** A
quantity whose value is unknown at registration cannot honestly carry a
pre-registered threshold in the same document that first measures it. **If the
measured y+ exceeds 1, that is a reportable finding that BLOCKS the correlation
tier and the triple — neither of which this rung claims — and it does not void
the physicality rows**, whose content is a temperature bound and not a
heat-transfer coefficient.

### 4.5 The 120 °C isotherm trace — DEFERRED to the full map

Directive §3.6's report bullet asks the 120 °C isotherm traced across the map.
**Four points on one power level cannot trace an isotherm across a map.** The
subset of §6.2 is registered to **bracket** the isotherm at U = 40 m/s (§6.2),
which is a single crossing, not a trace. **Deferred to the twelve points of
§6.4.**

### 4.6 The radiation upper bound — DEFERRED

Directive §3.6 asks for a per-point ε σ (T⁴ − T_inf⁴) A upper bound on the
neglected radiative term. **Deferred: it needs a registered emissivity, which
the directive does not supply and which this lane will not invent for a document
that freezes on commit.** Radiation OFF remains a **disclosed omission** (§1
line 1).

---

## 5. COST — `CLAUDE.md` rule 12

### 5.1 The basis, at its true strength and its true weakness

**MEASURED anchors**, both `chtMultiRegionSimpleFoam` at 1 rank, 5,000
iterations, read from their own `log.solve` `ExecutionTime` lines:

| anchor | cells | ExecutionTime | s per cell-iteration |
|---|---:|---:|---:|
| `T5_runs/T5_CUBE_m` | 216,214 | 4,490.88 s | **4.1541e-06** |
| `T5b_runs/T5_CUBE_f` | 896,531 | 20,833.54 s | **4.6476e-06** |

**NAMED MISMATCHES, disclosed and not absorbed:** both anchors are **Cartesian,
single-solid and sourceless**; T23 is a **5° wedge with two solids, two conjugate
interfaces and a sector-scaled source**, and it additionally carries a **fluid
region with `kOmegaSST`** that neither anchor's cost includes. **The anchors are
therefore a LOWER BOUND on the per-cell rate, not a bracket around it**, and the
cap headroom of §5.2 is sized for that asymmetry rather than for symmetric error.

**A cost this lane does NOT claim:** `T22_CHTb_L1` is in flight as this document
is written, and **its measured cost is not used here**. Under the T22 feasibility
note's own prohibition (§0.2), no number T22 emits enters this registration.
When T22 completes, its actual cost becomes the **first same-geometry measured
anchor this family has ever had**, and it belongs in the calibration ledger and
in any later registration — **not retroactively in this one.**

### 5.2 POINT and CAP

Cell count **39,680** per case (35,200 fluid + 3,360 core + 1,120 housing) at
`endTime` **10,000**:

    39,680 cells × 10,000 iterations = 3.968e08 cell-iterations
    at 4.6476e-06 s/cell-iter  ->  1,844 s = 30.7 core-min per case

| figure | value | tag |
|---|---:|---|
| **per case POINT** | **30.8 core-min** | **DERIVED** from the measured anchors above |
| **per case CAP** | **100.0 core-min** | **REGISTERED**, hard, = 3.25 × POINT |
| **SUBSET (4 cases) POINT** | **123.2 core-min** | **DERIVED** |
| **SUBSET (4 cases) CAP** | **400.0 core-min** | **REGISTERED**, hard |
| USD at POINT | **$0.1053** | **DERIVED, NOT MEASURED** |
| USD at CAP | **$0.3420** | **DERIVED, NOT MEASURED** |

USD at the owner-stated **c7a.4xlarge $0.0513/core-h**
(**REPORTED-BY-OWNER**, 2026-08-21/22). **The box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure here is measured. Both are
far under the $25 pre-authorisation, **and a blanket authorisation is not a
per-item reading** (`CLAUDE.md` rule 9).

**The cap is ENACTED, not merely written**: `timeout 6000s` at 1 rank inside each
case's own launcher (`cap_core_min = TIMEOUT_S × RANKS / 60` = 100.0). The queue
runner's `CAP_OVERRUN.txt` only **reports** and never kills; the wrapper's own
`timeout` is what stops the run, as rule 12 requires. **An overrun stops the run;
it does not get a new budget.**

### 5.3 **A COST FINDING AGAINST THE DIRECTIVE'S OWN CAP, REGISTERED HERE**

Directive §3.7 sets *"cap 700 core-min"* for Case 3 and estimates
*"~15-40 core-min (L1)"* per solve and *"16 points ~8 core-h at L1"*.

**Those three figures are not mutually consistent, and the arithmetic is stated
so the inconsistency is on the record before anyone spends against it:**

- 16 points × 30.8 core-min = **492.8 core-min POINT**, which fits inside 700 and
  agrees well with the directive's own "~8 core-h" (480 core-min);
- but 16 points at this rung's registered **3.25× cap headroom** = **1,600
  core-min**, which is **2.29× the directive's 700 core-min cap.**

> **REGISTERED CONSEQUENCE: the full 16-point map CANNOT be registered at both
> the directive's 700 core-min cap and this rung's 3.25× per-case headroom.**
> One of the two must move, and **this document moves neither** — it registers
> four cases whose cap of 400 core-min fits inside 700 with room to spare. **The
> resolution belongs to the later registration of §6.4, informed by the ACTUAL
> per-case cost the four cases of §6.2 will measure** — which is precisely the
> calibration §5.4 requires and precisely why a subset is run first.

### 5.4 The calibration owed at completion

Rule 12's estimate-versus-actual clause (Sanaa 2026-08-23) binds this rung. At
completion the results record must carry **actual core-minutes** from the
`STATUS.*` files as `wall_s × ranks ÷ 60`, the **ratio actual/predicted**, the
attribution split between **contention, waste and misprediction with waste named
separately and never folded into the ratio**, and a row appended to
`docs/COST_CALIBRATION.md`. **The figure this rung exists to calibrate is the
per-cell rate for a three-region wedge with a fluid region — a regime for which
the lab has never had a measured anchor.** *A completion report without this
comparison is incomplete.*

**REGISTERED, one-way and before the fact: a run whose recorded load average at
launch shows a saturated box produces a COST but NOT a calibration row.** After
the fact a contended number is indistinguishable from a mispredicted one, and
the temptation is then to attribute the whole gap to whichever term is under
discussion. Each launcher writes a `START.<case>` file **before** the solver
starts, carrying `start_utc`, all three `/proc/loadavg` windows and `nproc`.

---

## 6. THE REGISTERED RUN SET

### 6.1 Why a subset, stated plainly

Three independent reasons, any one of which would be sufficient:

1. **§5.3's cost finding.** The full map cannot be capped consistently with the
   directive until a same-geometry per-case cost has been **measured**. Four
   cases measure it.
2. **This geometry has never completed a solve.** `T22_CHTb_L1` is the first
   execution of this three-region wedge and is in flight as this is written.
   Launching sixteen copies of a case whose completion is unestablished is
   exactly the waste rule 12 forbids.
3. **An honest partial beats a padded whole.** Twelve of the sixteen points are
   deferred with reasons in §6.4, not silently dropped.

### 6.2 **THE REGISTERED SUBSET — the P = 305 W row, all four airspeeds**

> **REGISTERED: four cases, `T23_P305_U10`, `T23_P305_U20`, `T23_P305_U30`,
> `T23_P305_U40`, at P_loss = 305 W and U_inf ∈ {10, 20, 30, 40} m/s,
> L1, 1 rank, `endTime` 10000, per-case cap 100.0 core-min.**

**This row is the single most load-bearing row of the whole map, and it was
chosen for that and not for cheapness.** It carries, uniquely among the four
power levels, **both** of the decisions the map exists to make:

| what the row carries | which point carries it |
|---|---|
| the **UNDECIDED** bound point of §2.7, +2.70 K under DB | **(305, 20)** |
| a point the model **predicts will flag** — the B1 "beyond assumption range" branch exercised deliberately | **(305, 10)**, DB margin −129.1 K |
| the **120 °C isotherm bracket at U = 40 m/s**, the crossing §2.3 proves no lower top level can reach (DB isotherm at U=40 = 300.5 W; 305 W sits just above it) | **(305, 40)**, DB `T_max` 121.6 °C |
| a **comfortably-clear** point, so the row is not all boundary | **(305, 30)**, DB margin +52.0 K |

**REGISTERED PREDICTIONS for this row, reported beside the measured values and
NEVER used as gates** (they are a lumped 1-D model's output, and §2.7 registers
that it may be wrong):

| case | DB `T_max` | FP `T_max` | model's B1 call |
|---|---:|---:|---|
| `T23_P305_U10` | 329.1 °C | 195.1 °C | **flag** under DB, clear under FP |
| `T23_P305_U20` | 197.3 °C | 120.3 °C | **UNDECIDED**, +2.70 K |
| `T23_P305_U30` | 148.0 °C | 92.4 °C | clear |
| `T23_P305_U40` | 121.6 °C | 77.4 °C | clear |

**The registered contingency, one-way and stated now:** if the solved values
disagree with **both** closures by more than the 1.763× spread between them, the
**lumped model of §2 is the thing that was falsified** — a reportable finding
about the level-selection instrument — and **that does not change B1, B2 or B3,
which grade the solved temperature and not the model.**

### 6.3 **THE LAUNCH PRECONDITION — a precondition, not a gate**

> **REGISTERED: no T23 case is launched until `T22_CHTb_L1` has reached its
> registered `endTime` of 5000 with `rc = 0` and an `End` line.**

This is a **launch precondition on a feasibility question** — *does this
three-region wedge complete under this solver at all* — and it is **not a gate,
not a band, and not a threshold**. It imports **no value** from T22 and honours
the T22 note's prohibition in full: what is read from T22 is whether it
**finished**, never what it **measured**.

**If T22 does not complete, T23 is `BLOCKED`** and this registration stands
unrun until the feasibility question is answered by some later run. **A BLOCKED
T23 is not a failure of this registration**; the freeze remains valid and the
gates remain unchosen-to-fit precisely because they were fixed before anything
ran.

### 6.4 **THE TWELVE DEFERRED POINTS, AND WHY**

**Deferred: P_loss ∈ {80, 155, 230} W × U_inf ∈ {10, 20, 30, 40} m/s — twelve
points.** They are **not cancelled and not dropped**; they are the subject of a
later registration, and the two things that later registration needs are named
here so the deferral is actionable rather than decorative:

1. **A measured per-case cost** for this geometry, which the four cases of §6.2
   produce and which §5.3 shows the full map cannot be honestly capped without.
2. **A demonstrated completion** at this geometry — the same precondition as
   §6.3, but discharged by a T23 case rather than by T22, i.e. by a case that
   ran under a frozen registration.

**What is lost by deferring them, stated rather than glossed:** the 120 °C
isotherm can be **bracketed at U = 40 m/s** by the §6.2 row but **cannot be
traced across the map** (§4.5), and the two DB-flagged rescaled points are
**(230,10)** and **(305,10)** — of which only **(305,10)** is in the subset, so
the rescale's flag count of **2 of 16** is **registered arithmetic and is not
measured by this rung.**

---

## 7. AUTHORITY, AND WHAT IS NOT CLAIMED

Filed by a heat-transfer `lab-lane` at the heat-transfer-supervisor's dispatch,
under **Sanaa's ruling "5. Rescale"**
(`etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md`, the chief's verbatim
capture of her own words, read at source) and her 2026-08-31T15:45Z standing
order that the box must be full
(`etc/sessions/2026-08-31T1545Z_sanaa_box_full.md`).

**Sanaa's 14-day rule freeze is honoured** (`etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`,
read at source): **this document proposes NO new procedural or bookkeeping rule
and creates NO new tool.** Every instrument it registers is an existing lab
pattern applied to a new case — the planted-zero control of §3.6, the completion
rule of §3.5, the private-index commit protocol. The findings of §2.5 (the "8 of
16" correction), §3.4 (the vacuous Ri check), §4.2 (`CASE3-DEP-1` unregistered)
and §5.3 (the directive's inconsistent cap) are **recorded as findings and spawn
no rule and no tool.**

**A supervisor's check is not claimed as performed here.**
`SUPERVISION_CHARTER.md` §3 check 4 — pre-registration **committed** before
compute — is the supervisor's own and is **not claimed by this lane**. What this
lane asserts is narrower and is checkable: **the run directories of §0.4 were
measured absent under a live planted control in the invocation that commits this
file**, and no compute has been launched against these gates.

**No agent's message is Sanaa's consent** (`CLAUDE.md` rule 9). The session files
cited above are the chief's verbatim capture of her own words and are cited as
such, and nothing in them is read as widening any authorisation beyond the item
it names.
