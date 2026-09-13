# M6I RUNG 6 — `vanLeer` ON THE COMPRESSIBLE PRESSURE-CONVECTION TERM. PRE-REGISTRATION.

**Item:** `M6I_R6_PHIDP_VANLEER`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.
**Predecessor:** `M6I_R5_PRESSURE_TERM_PREREGISTRATION.md`, frozen `27a491e77`, addendum 1
at `1ba860253`. **R5's run `L2_PHIDP` is `NOT A RESULT`** (rc = 136, SIGFPE, `Time = 6290`
of 8000, no `End` line, no `8000/` fields). **R5's D1/D2/D3 were never read** and are
carried into this document unchanged.

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**

Rule 2 freezes by sha at commit. This lane does not commit. **This becomes the grading path
only when `cfd-supervisor` commits it.** Pre-compute condition, checked by this lane and
stated so it can be re-checked: **`verification/runs/M6I_runs/L2_VANLEER/` does not exist.**

---

## 1. THIS IS STOP ONE OF TWO ON THIS CAUSE, AND THE EXIT IS WRITTEN DOWN NOW

Sanaa's rule 13 is two stops on the same cause, then climb. R5 was **stop zero** — it did
not stop on the cause, it stopped on an unusable remedy. **This document is stop one.**
§7 fixes what happens at stop two **before** stop one runs, so that nobody starts a
variant three.

## 2. WHY `vanLeer`, AND THE RE-COUNT THAT REVERSED THIS LANE'S OWN WITHDRAWAL

In the R5 crash report this lane **withdrew** the mechanism that `limitedLinear` on the
implicit `div(phid,p)` costs the pressure matrix its solvability, on the ground that
`limitedLinear` is the tutorial majority (28 against 18). **The supervisor re-counted on
the variable that decides whether `div(phid,p)` is even the implicit compressibility term
— `transonic` — and the withdrawal is itself withdrawn.** Re-counted independently by this
lane over all 49 shipped `fvSchemes` files setting `div(phid,p)`, partitioned by the
sibling `fvSolution`:

| `div(phid,p)` scheme family | `transonic yes` | not `transonic yes` | total |
|---|---:|---:|---:|
| second-order / bounded (non-upwind) | **1** | 29 | 30 |
| upwind | **2** | 17 | 19 |

**Only 3 of 49 files set `transonic yes` — 93.9 % of the population is non-transonic, and
29 of the 30 bounded files (96.7 %) are.** Under `transonic no`, `div(phid,p)` is not the
implicit compressibility term in the pressure equation, so those files do not bear on this
case. **On the population that does bear it is 1 bounded against 2 upwind.** Two small
corrections to the supervisor's figures, neither changing his conclusion: the bounded total
is **30, not 29**, and the whole-population non-transonic share is **93.9 %** (his 96.6 %
is the share *within the bounded family*, which is 96.7 %).

**The three files that bear:**

| tutorial | solver | `div(phid,p)` |
|---|---|---|
| `compressible/rhoSimpleFoam/squareBend` | **rhoSimpleFoam (steady, SIMPLE)** | `Gauss upwind` |
| `compressible/sonicDyMFoam/movingCone` | sonicDyMFoam (**transient**) | **`Gauss vanLeer`** |
| `lagrangian/coalChemistryFoam/simplifiedSiwek` | coalChemistryFoam | `Gauss upwind` |

**`vanLeer` is chosen because it is the only bounded scheme any shipped `transonic yes`
case uses.** 🔴 **Its precedent is n = 1 and it is a TRANSIENT solver, not the steady SIMPLE
one this case runs. That is weak evidence and this document will not call it strong.**
`limitedLinear 1` is already the most limiting member of its own family, so "the same
limiter, gentler" does not exist; the move must be to a different limiter.

## 3. WHY THE PRESSURE LIMITER IS **NOT** IMPLICATED — THE ARITHMETIC, CARRIED IN

R5's run ended with **1,705 of 1,920 wing cells (88.8 %) at one identical value,
`202650.42` Pa** — `pMaxFactor 2.0 × p_inf`. Identical values are a limiter, not physics.
The question that decides whether this is *censorship* or *divergence* is whether valid
physics could ever reach that ceiling. Computed from the case's own `gamma`:

- `gamma = 1.399726300`, `M_inf = 0.8395`, `q_inf = 49,977.11 Pa`, `p_inf = 101,325 Pa`
- `p0/p_inf = (1 + (gamma−1)/2 · M²)^(gamma/(gamma−1))` = **1.5864**
- **`Cp` at stagnation = 1.1888.** The `pMaxFactor 2.0` ceiling is **`Cp` 2.0274**.
- **The ceiling sits 26.1 % ABOVE stagnation pressure.**

**No valid physics on this case can reach that limiter.** The clamp is correctly placed and
is not inside the solution's real range; the pressure genuinely left the physically
admissible set and then met a correctly-placed ceiling. **This is unambiguous divergence,
not clamp censorship**, and `pMaxFactor` is therefore **not** changed by this document.

🔴 **This is also the second time this family has been asked to merge with CRM and the
second time it declines.** CRM's failure is the *other* kind — cells pinned at clamps that
sit *inside* the physics. Same-looking numbers, different failures. Not merged.

## 4. THE ONE CHANGE — AND THE TWO LISTS ARE WRITTEN SEPARATELY ON PURPOSE

**Baseline: `L2` as it stands, converged at `t = 5000`. NOT the dead `L2_PHIDP` tree.**
A fresh copy is staged so the change is single *against the baseline*, not cumulative on a
diverged case.

**WHAT CHANGES — this is the complete list:**

| file | from (L2's value) | to |
|---|---|---|
| `system/fvSchemes` | `div(phid,p)     Gauss upwind;` | `div(phid,p)     Gauss vanLeer;` |
| `system/fvSchemes` | `div((phi\|interpolate(rho)),p) bounded Gauss upwind;` | `div((phi\|interpolate(rho)),p) bounded Gauss vanLeer;` |
| `system/controlDict` | `endTime 5000;` | **`endTime 8000;`** — the 3,000 further iterations §8 prices |

**WHAT DOES NOT CHANGE — and `endTime` is deliberately ABSENT from this list, because R5's
addendum 1 exists precisely because it was wrongly placed here:**
grid and `constant/` in its entirety; `nNonOrthogonalCorrectors 2`; `limited corrected 0.33`
on `laplacianSchemes` and `snGradSchemes`; every `relaxationFactors` entry; `transonic yes`;
`pMinFactor 0.2` and `pMaxFactor 2.0`; `SpalartAllmaras`; `writeInterval 200`;
`purgeWrite 2`; `decomposeParDict`; `constant/fvOptions` including `limitTemperature`;
and **every `div(phi,*)` scheme**.

**Verification required before launch, and it is an assertion not an intention:**
`diff -r` over `constant/` returns empty, and a file-by-file `cmp` over `system/` returns
**exactly two differing files** — `fvSchemes` and `controlDict` — containing **exactly the
three line changes tabled above**. Each scheme anchor must match **exactly once** before
replacement. If any assertion fails, **nothing is launched.**

## 5. THE PREDICTION — D1, D2 AND D3 ARE R5's, TRANSCRIBED UNCHANGED

These are **not re-derived and not re-tuned.** They are R5 §4.2's values, carried verbatim,
and they remain **kill-only: a row they fail is `GATE FAIL`; a row they pass is not thereby
a `PASS`.** §6 is the only cure gate.

- **D1 — `cfd_cp_rise_at_shock` at η = 0.65 must reach ≥ 0.1401.** (L2 baseline: 0.1031.
  Floor = 0.1031 + 2 × 0.0185, where 0.0185 is the largest movement any prior registered
  numerics change produced on a fixed grid — L3_TVD − L3 — and it was in the wrong
  direction.)
- **D2 — CFD `Cp` rise across the experiment's own shock interval at η = 0.65 must reach
  ≥ 0.0880** (= 5.0 × L2's current 0.0176; ≥ 20.8 % of the experimental 0.4240). A full
  grid level buys ×1.50 (L2 → L1: 0.0176 → 0.0264); **this demands ×5.0 on the same grid,
  so a pass cannot be attributed to refinement.**
- **D3 — `x_shock_cfd` at η = 0.65 must leave 0.8851** for a strictly more forward member
  of that station's 14 admissible orifice midpoints.

## 6. THE CURE GATE — FROZEN ELSEWHERE, RE-INVENTED NOWHERE

Unchanged from `M6I_R1_SOLVE_PREREGISTRATION.md` ADDENDUM 8 §A8.2/§A3.1 and
`A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md` §5:
**S1** `cfd_cp_rise_at_shock ≥ 0.212` (η 0.65) and `≥ 0.320` (η 0.90); **S2** `x_shock_cfd
< 0.85 c`; **B1** `RMS ≤ 0.050` on each of 12 rows; **B2** `|x_shock_cfd − x_shock_exp| ≤
Δ_local`.

## 7. 🔴 THE REFUTATION CONDITION — WRITTEN BEFORE THE RUN, WITH THE LADDER'S NEXT STEP FIXED

**THE DIVERGENCE SIGNATURE, DEFINED NUMERICALLY FROM R5's MEASURED VALUES so that "the same
signature" is not a matter of opinion.** It is met when **all three** hold:

1. the run terminates with `rc ≠ 0`; **and**
2. at the last written time, **≥ 50 %** of `wing` patch cells carry the **identical** value
   `pMaxFactor × p_inf`; **and**
3. the upper/lower split of those cells satisfies **|n_upper − n_lower| / (n_upper +
   n_lower) ≤ 0.10.**

*(R5's `L2_PHIDP` measured 88.8 %, and 854 upper against 851 lower — a split of 0.002.
A shock forming and being lost is an overwhelmingly upper-surface event; a symmetric aft
runaway is the pressure equation losing its own solvability.)*

**IF THE SIGNATURE IS MET: the pressure-term rung is `SPENT`. This is stop two. The ladder
climbs to the MODEL rung — SA versus SST — and NO THIRD VARIANT OF `div(phid,p)` IS
REGISTERED OR RUN BY ANYONE.** That is stated here so it cannot be relitigated after the
fact.

**IF THE RUN DIVERGES WITH A DIFFERENT SIGNATURE** (for example upper-surface dominated,
or below the 50 % threshold), **that is a different finding, it does NOT spend the rung,
and it returns to the supervisor undecided.** This document does not pre-authorise a
reading of an outcome it did not anticipate.

**IF THE RUN COMPLETES:** the strict completion rule is applied in full, then D1/D2/D3 and
§6 are read as written. **A completed run that fails D1 and D2 also spends the rung** — it
is stop two by the other road — and the ladder climbs identically.

## 8. COST (rule 12)

**Measured basis, from R5's own run of the same configuration** (L2 grid, resumed from
5000, a limited scheme on `div(phid,p)`): `L2_PHIDP` ran **1,290 iterations in 193 s at 4
ranks = 12.87 core-minutes = 0.009977 core-min/iteration.**

- **Predicted: 3,000 iterations → 29.9 core-minutes, ≈ 7.5 min wall at 4 ranks.**
- **Cap: 131.1 core-minutes.** 🔴 **This cap is deliberately NOT 3 × 29.9.** It is 3 × 43.7,
  where 43.7 is the *slower* L2-baseline rate (0.014567 core-min/iteration), because a
  converging `vanLeer` run may legitimately take more solver iterations per outer iteration
  than a diverging `limitedLinear` one. **A run that is merely slow must not be graded
  `NOT A RESULT` on cost.** A crossing grades the row `NOT A RESULT`; the cap is never
  raised; **nothing is killed on spend or clock** (Sanaa directive #17, 2026-09-12).
- `cost_basis`: **MEASURED** in core-minutes from the run's own logs. Dollars **DERIVED,
  NOT MEASURED** at the owner-stated $0.0513/core-h → ≈ $0.026. The box cannot read its own
  billing (`COMPUTE_BUDGET_CHARTER.md` §5).
- Estimate-vs-actual lands in `docs/COST_CALIBRATION.md` at completion, waste named
  separately and never absorbed.

## 9. PRECONDITIONS AND CONTROLS

Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, unchanged,
**hash-verified against the committed blob in the same shell invocation as the run.** Its
§7 planted control must print `reader_saw_the_plant: true` or the result is
**`NOT A RESULT`**. The strict completion rule applies in full **including the age guard**,
and P4's `End` line is read from **the terminating stage log** via the driver fix landed at
`0bc8fd09d`.

## 10. WHAT THIS DOCUMENT DOES NOT DO

1. **No grid triple, no observed order, no GCI.** One grid, one change.
2. **Does not change `pMaxFactor`, `pMinFactor`, `fvOptions` bounds or any relaxation
   factor.** §3 shows the pressure ceiling is above stagnation and therefore not implicated.
3. **Does not register SA-versus-SST.** §7 makes that the *consequence* of an outcome, not a
   parallel item. Registering it now would invite a concurrent run that confounds the
   one-change rule.
4. **Does not claim the `vanLeer` precedent is strong.** §2 records it as n = 1, transient.
5. **Does not merge M6I's failure with CRM's.** §3.

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
Alters no existing gate, threshold, band, cap or label. No agent's message is Sanaa's
consent. Submissions parked.*
