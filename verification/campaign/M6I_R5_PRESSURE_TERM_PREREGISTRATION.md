# M6I RUNG 5 — THE COMPRESSIBLE PRESSURE-CONVECTION TERM. PRE-REGISTRATION.

**Item:** `M6I_R5_PHID_P`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**

Rule 2 freezes a pre-registration **by sha, at its commit**. This lane was instructed not
to commit. **This file is therefore not yet frozen, and nothing in it authorises compute.**
It becomes the grading path only when `cfd-supervisor` commits it unchanged; if any
threshold below is edited first, the edit must happen *before* that commit and must name
the run directory that does not yet exist (rule 2, pre-compute amendment).

**Every number below was written before the run it grades exists.** The run directory
`verification/runs/M6I_runs/L2_PHIDP/` **does not exist** at the time of writing; this was
checked, and it is the condition that makes the amendment window legal.

---

## 1. WHY THIS RUNG, AND WHY **NOT** THE ONE THAT WAS ORDERED

The supervisor's dispatch ordered, in order: (1) localise the imported grid's
non-orthogonality; (2) **if the grid test survives**, raise `nNonOrthogonalCorrectors` with
the limited-gradient treatment matched to it; (3) SA vs SST only if (2) fails.

**(1) WAS RUN AND THE GRID HYPOTHESIS IS DEAD.** Measured on L1's own
`checkMesh -writeSets` output (`postProcessing/constant/nonOrthoFaces/nonOrthoFaces.vtp`,
191,794 faces, matching the `log.checkMesh_sets` count exactly):

| where the >70° faces are | count | share of near-wall |
|---|---:|---:|
| within 0.05 c of the wing | 177,976 | 92.80 % of all 191,794 |
| …of those, at **η ≥ 0.99** (tip cap and outboard) | **149,730** | **84.13 %** |
| …at η 0.90–0.99 | 23,796 | 13.37 % |
| …at η 0.65–0.90 | 3,110 | 1.75 % |
| …at η 0.20–0.65 | 954 | 0.54 % |
| …at η 0.00–0.20 | 386 | 0.22 % |
| **inside the x/c 0.30–0.70 UPPER-surface shock window, at ANY of the six graded stations** | **0** | **0.00 %** |

**Zero.** Not few — none. The supervisor's own kill criterion was *"if they are all in the
farfield stretching or at the tip, it is dead and say so."* They are at the tip.
**Rung 2 as ordered is therefore NOT registered and is NOT run.** Raising
`nNonOrthogonalCorrectors` would treat faces that are not where the missing physics is.

**The CRM cross-case pattern is not corroborated by this case and must not lean on it.**
CRM Coarse 88.768° / Medium 89.870° failing to start is a *stability* failure in the
pressure equation. M6I at 87.66° **starts, runs 8,000 iterations and converges to
residuals of 1e-7** — it does not fail, it converges to the wrong answer, and its bad faces
are on a tip cap the grading already excludes. **Two different failures, and this lane
declines to merge them.**

## 2. WHY THE NUMERICS RUNG IS **NOT** SPENT — THE TERM NOBODY HAS TOUCHED

The supervisor ruled the numerics rung spent because L3_TVD and L3_NORAMP both reproduced
L3's shock position. **Read as diffs, those two changes moved the same term-group and left
the load-bearing term untouched at every level of the family:**

| term | L3 / L3_NORAMP | L2 / L1 / L3_TVD | ever changed? |
|---|---|---|---|
| `div(phi,U)` | `linearUpwind limitedGrad` | `limitedLinearV 1` | ✅ twice |
| `div(phi,e)` `div(phi,K)` `div(phi,Ekp)` | `linearUpwind limitedGrad` | `limitedLinear 1` | ✅ twice |
| `div(phi,nuTilda)` | `upwind` | `limitedLinear 1` | ✅ twice |
| **`div(phid,p)`** | **`Gauss upwind`** | **`Gauss upwind`** | 🔴 **NEVER** |
| **`div((phi\|interpolate(rho)),p)`** | **`bounded Gauss upwind`** | **`bounded Gauss upwind`** | 🔴 **NEVER** |

`SIMPLE { transonic yes; }` is set at **every** level, verified. Under `transonic yes`,
`div(phid,p)` **is** the compressibility term in `rhoSimpleFoam`'s pressure equation — it is
the only place the pressure equation learns that the flow is supersonic. It has run
**first-order upwind on every level of this family**, and neither prior numerics change went
near it. *Two stops on the same cause* is satisfied for the momentum/energy convection
group. **The pressure-equation group has had zero stops.**

**The refinement evidence is consistent with a first-order-dissipation-limited shock and is
quantitative.** CFD Cp rise measured across the **experiment's own** shock interval — a
continuous diagnostic, not the quantised argmax:

| level | cells | η0.65 rise | % of exp 0.4240 | η0.90 rise | % of exp 0.6400 |
|---|---:|---:|---:|---:|---:|
| L3_TVD | 15,360 | 0.0113 | 2.7 % | 0.0107 | 1.7 % |
| L2 | 122,880 | 0.0176 | 4.2 % | 0.0186 | 2.9 % |
| L1 | 983,040 | 0.0264 | **6.2 %** | 0.0318 | **5.0 %** |

**×1.528 per grid halving** (geometric mean of the two measured steps, ×1.558 and ×1.500),
scheme-consistent, both stations. Reaching the experimental 0.4240 needs a further **×16.06**,
i.e. **6.54 more halvings ≈ 8.0 × 10¹¹ cells**. That is a *reductio*:
**the shock is not reachable by refinement on this discretisation**, which is what a
first-order term in the pressure equation predicts and what a resolution-limited shock does
not.

## 3. THE ONE CHANGE

**`div(phid,p)`: `Gauss upwind` → `Gauss limitedLinear 1`**, and
**`div((phi|interpolate(rho)),p)`: `bounded Gauss upwind` → `bounded Gauss limitedLinear 1`.**
**Nothing else moves.** Grid, `nNonOrthogonalCorrectors 2`, `limited corrected 0.33`,
relaxation, `transonic yes`, SA, `endTime`, and every `div(phi,*)` scheme stay byte-identical
to L2's. The diff is two lines and is the whole rung.

**Level: L2** (122,880 cells), restarted from L2's converged 5000 field, 3,000 further
iterations. L1 is not used: the answer must come back in minutes and the effect, if real,
is a discretisation effect visible at any resolution.

**Relaxation is deliberately NOT changed, and here is why it is not a candidate:**
`rho 0.05` and `p 0.3` look aggressive, but under-relaxation does not move the converged
fixed point — only the path to it. L1 converged to Ux 2.9e-07 / p 8.5e-06 / nuTilda 8.5e-07.
**Relaxation cannot be the cause of a converged wrong answer and is not registered as one.**

## 4. 🔴 THE PREDICTION — WRITTEN BEFORE THE RUN, AND THE RUN DOES NOT EXIST

### 4.1 THE CURE GATE — **already frozen elsewhere; NOT re-invented here**

From `M6I_R1_SOLVE_PREREGISTRATION.md` ADDENDUM 8 §A8.2 / §A3.1, unchanged:
- **S1:** `cfd_cp_rise_at_shock ≥ 0.212` at η = 0.65 **and** `≥ 0.320` at η = 0.90.
- **S2:** `x_shock_cfd < 0.85 c`.
- **B2** (`A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md` §5, reference-derived):
  `|x_shock_cfd − 0.4752| ≤ 0.0501` at η = 0.65, i.e. **x_shock must land on the admissible
  midpoint 0.4752** (0.4252 and 0.5253 sit exactly on the band edge).

L2 today: **0.1031** and **0.0582**; `x_shock` **0.8851** and **0.9233**.

### 4.2 THE DIAGNOSTIC LIMB — **alive or dead. IT CAN ONLY KILL, NEVER PROMOTE.**

A row it fails becomes `GATE FAIL`; a row it passes is **not** thereby a PASS — §4.1 is the
only gate. The floors are **derived from measured noise in this family**, not chosen:

- Largest movement any prior registered numerics change produced in `cfd_cp_rise` at
  η = 0.65 on a fixed grid: **L3_TVD − L3 = 0.0690 − 0.0875 = −0.0185** (and in the *wrong*
  direction). The ramp change moved it **+0.0002**.
- **D1 — REGISTERED: `cfd_cp_rise` at η = 0.65 on L2 must reach ≥ 0.1401**
  ( = 0.1031 + 2 × 0.0185 ), upward. Below that, the movement is indistinguishable from a
  prior scheme nudge and **the pressure-term rung is graded spent with the others.**
- **D2 — REGISTERED, and it is the one that matters because it cannot be passed by
  resolution: CFD Cp rise across the experiment's own shock interval at η = 0.65 must reach
  ≥ 0.0880** ( = 5.0 × L2's current 0.0176, i.e. **≥ 20.8 %** of the experimental 0.4240 ).
  **A full grid level buys ×1.50 (L2 → L1: 0.0176 → 0.0264). This limb demands ×5.0 on the
  SAME grid — 3.3× more than ×8 cells buys — so passing it cannot be attributed to
  refinement.**
- **D3 — REGISTERED: `x_shock_cfd` at η = 0.65 must leave 0.8851** and land on a strictly
  more forward admissible midpoint (the admissible set at this station is the 14 midpoints
  0.2253 … 0.9531; `x_shock` is **quantised to these and to nothing else**). Remaining at
  0.8851 → **hypothesis not supported.**

### 4.3 WHAT THIS LANE ACTUALLY EXPECTS, STATED SO IT CAN BE WRONG

**D1 and D2 pass; §4.1's S1 does not; B2 does not.** The prediction is that removing a
first-order term from the pressure equation produces a *visible, sharp* recompression that
is still too weak and too far aft on a 122,880-cell grid — i.e. **`GATE FAIL` with the
hypothesis ALIVE**, and the cure then needing this scheme **on L1**. If D1/D2 fail, this
lane was wrong, the pressure-term rung is spent, and rung 3 (SA vs SST) is next.

## 5. PRECONDITIONS AND CONTROLS

Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, hash-verified
against the committed blob in the same shell invocation as the run, unchanged. Its §7
planted control must print `reader_saw_the_plant: true` or the result is **`NOT A RESULT`**.
The strict completion rule applies in full, **including the age guard**, and P4's `End` line
is read from **the stage log that actually terminates** (see §7).

## 6. COST (rule 12)

Measured basis: L2 ran **4,800 iterations in 1,048 s at 4 ranks = 69.87 core-min**
= 0.01456 core-min/iteration. 
- **Predicted: 3,000 iterations → 43.7 core-minutes, ≈ 11 min wall at 4 ranks.**
- **Cap: 3× = 131.1 core-minutes** — inside L2's already-registered 256 cap. A crossing
  grades the row `NOT A RESULT` on cost; the cap is never raised; **nothing is killed on
  spend or clock** (Sanaa directive #17, 2026-09-12).
- `cost_basis`: **MEASURED** from the run's own logs in core-minutes. Dollars **DERIVED,
  NOT MEASURED** at the owner-stated $0.0513/core-h → ≈ $0.037. The box cannot read its own
  billing (`COMPUTE_BUDGET_CHARTER.md` §5).
- Estimate-vs-actual lands in `docs/COST_CALIBRATION.md` at completion.

## 7. A DEFECT IN THE MEASURING INSTRUMENT THAT MUST BE READ FIRST

`verification/runs/M6I_runs/evaluate_m6i_level.sh` hard-codes `$C/log.rhoSimpleFoam` for
its C1 limbs **and** for the grader's P4 argument. **Any level that finishes on a resume
stage is mis-graded.** The proposed fix is handed to the supervisor as a diff at
`verification/runs/M6I_runs/EVALUATE_M6I_LEVEL_LOGPICK.diff` and is **NOT applied**: it is a
measurement-script change and is his to read as a diff (`SUPERVISION_CHARTER.md` §3).
This run will finish on a resume stage and is affected.

## 8. WHAT THIS DOCUMENT DOES NOT DO

1. **No grid triple, no observed order, no GCI.** One grid, one change.
2. **Does not retire the grid hypothesis for CRM.** §1 declines to merge the two cases; CRM
   is the ansys/cfd CRM act's to settle on its own evidence.
3. **Does not claim `a` (the additive Cp offset, ≤ 0.032) is zero.** Unmeasured, disclosed.
4. **Does not grade force coefficients.**

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
Alters no existing gate, threshold, band, cap or label. No agent's message is Sanaa's
consent. Submissions parked.*
