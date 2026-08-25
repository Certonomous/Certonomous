# F12 RUNG 1 — THE FIELD OBSERVATION ARM

**cfd lane, 2026-08-25.** Commissioned by the cfd supervisor's triage
`verification/runs/F12_runs/RUNG2_DISPOSITION_AND_CRASH_TRIAGE_2026-08-25.md` §3.4:
*"Stop asking why the linear solve traps. Establish WHERE IN THE DOMAIN the field
first goes wrong, and WHEN."*

**THIS ARM GRADES NOTHING.** No gate, threshold, cap or label moves. Rung 1 stands
**`NOT A RESULT`** and is not regraded here. Rung 2 stands **`BLOCKED`** and its
interlock was not touched. No verdict from the fixed vocabulary is due to this arm
and none is issued.

Pre-registration, frozen before compute: `PROBE_PREREGISTRATION.md` beside this file.

---

## 0. THE HEADLINE, AND IT CORRECTS THE TRIAGE IT WAS COMMISSIONED BY

**1. The departure is AEROFOIL-ANCHORED AND STARTS AT ITERATION 1 — not iteration 5.**
At iteration 1, **6,914 of 23,040 cells (30.0 %) are already pinned at the
`pressureControl` bounds**, simultaneously at the floor (3,628) and the ceiling
(3,286). They occupy the near field around the aerofoil,
`x ∈ [-0.104, 1.076]`, `y ∈ [-0.270, 0.388]` (chord is `x ∈ [0, 1]`).
The unclipped extremes the solver itself printed at iteration 1 are
**`p max 2,974,458.981 Pa` and `p min −411,376.774 Pa`** — 29× freestream and a
**negative absolute pressure** — from a uniform `101,325 Pa` start, in one iteration.

**2. It is NEITHER of the supervisor's two boxes, and the picture is DEFINITE, not
ambiguous.** See §3. It is not a boundary defect: at iteration 1 the mid, outer,
far, inflow and outflow regions are at **exactly 300.000000 K**, undeparted, and the
front reaches the inflow patch only at **iteration 13** and the outflow at
**iteration 15**. The boundary is the *last* place to depart, not the first. Nor is
it the whole field drifting together.

**3. rung 1 DID NOT DIE OF A FLOATING-POINT EXCEPTION, AND NOTHING IN ITS LIFE
INVOLVED A GAMG TRAP.** The triage §3 reads `rc = 134` as *"`SIGABRT`, consistent
with a floating-point trap raising `abort()`"*. It is not. Rung 1's log ends:

> `--> FOAM FATAL ERROR: Negative initial temperature T0: -2.384321367`
> `in file ./src/thermophysicalModels/specie/lnInclude/thermoI.H at line 57`

Verified at source, `/usr/lib/openfoam/openfoam2606/src/thermophysicalModels/specie/thermo/thermo/thermoI.H`:
`if (T0 < 0) { FatalErrorInFunction << "Negative initial temperature T0: " << T0 << abort(FatalError); }`
— an **explicit range check**, reaching `std::abort()` via `error::simpleExit`
(`src/OpenFOAM/db/error/error.C:437`). `trapFpe` was enabled (log line 448) and
**never fired**; the log contains no FPE, no NaN and no Inf line. The abort occurs
in the **energy equation's `thermo.correct()`**, immediately after
`Solving for e` at `Time = 148` and **before the pressure equation ran that
iteration** — GAMG was not on the stack.
The GAMG/FPE result is arm B's, on a **different case** carrying `transonic yes`,
which exited `rc = 136` (`SIGFPE`) — ledger row `C-74`. It never described rung 1.

**4. THE RESIDUAL WAS BLIND BY CONSTRUCTION, WHICH IS WHY NO ARM SAW THIS.**
`pressureControl::limit()` clips `p` to `[10132.5, 202650] Pa` and the **written
field is censored** — every `p` file on disk reports exactly those bounds and never
the true excursion. The initial residual of iteration *n* is computed from the `p`
field already clipped at iteration *n−1*. **A residual monitor could not have seen
the departure, and neither can a field monitor that reads `p` alone.** The
supervisor's reading that rung 1 "never descended" is refined: first-solve `p` *did*
descend, 1 → 4.43e-2 → … → 9.5548e-03 by iteration 5, then rose — but it descended
on an already-censored field, three iterations after the field had departed.

---

## 1. WHAT WAS RUN, AND WHAT WAS NOT CHANGED

Executing copy outside the repository at
`/home/ubuntu/certonomous-runs/F12_field_observation_2026-08-25/obs_case`.

**The entire delta from the registered rung-1 case is three output-control lines**
(`evidence/controlDict_THE_ENTIRE_DELTA.diff`):
`endTime 6000 → 15`, `writeInterval 6000 → 1`, `purgeWrite 1 → 0`.

**Asserted byte-identical to the registered case before the run**, all 18 of them:
`system/{fvSolution,fvSchemes,blockMeshDict,decomposeParDict}`,
`0/{T,U,p,k,omega,nut,alphat}`,
`constant/{thermophysicalProperties,turbulenceProperties}`,
`constant/polyMesh/{points,faces,owner,neighbour,boundary}`.
**No solver, smoother, preconditioner, tolerance, `relTol`, `residualControl`
entry, corrector count, `pMinFactor`, `pMaxFactor`, relaxation factor, scheme or
boundary condition was touched.** Ranks = 1, which is what the **registered rung 1
itself ran** (`log.rhoSimpleFoam:447`, `nProcs : 1`) — the rank count is unchanged too.

**FAITHFULNESS, PROVEN NOT ASSUMED.** The observation run's first-solve residuals are
**bit-identical to the registered rung 1 for all 15 iterations**, every field
(`evidence/obs_first_solve.json` vs `evidence/rung1_first_solve_recheck.json`).
This is a reproduction, not an analogue.

**Frozen instruments untouched.** `launch_f12_rung.py` reads
`24c6a6332be3b9068697f6756cd5394faced804c21a90917e791a26b372f9506`, equal to the
`grade.json` frozen-evidence record. `first_solve_residuals.py` reads
`a5c9d60a782248809877f0164a553676f11121b663f1dab4de06eaa7c9bed05b` at use and was
**reused unmodified** — its S17 selftest was re-run on this arm's log and passed 5/5.

---

## 2. THE NUMBERS

### 2.1 `p` — the unclipped extremes, from the solver's own print
`evidence/rung1_pressureControl_series.json`, extracted from the **registered**
rung-1 log at zero compute. Verified at source that `pressureControl::limit` prints
the **pre-clip** extreme and only when the bound is exceeded
(`src/finiteVolume/cfdTools/general/pressureControl/pressureControl.C`).

| iteration | `p min` (Pa) | `p max` (Pa) |
|---|---|---|
| 1 | **−411,376.774** | **2,974,458.981** |
| 2 | −167,638.117 | 658,689.606 |
| 3 | −31,076.5 | 543,587 |
| 5 | −9,958 | 257,631 |
| 7 | −191,573 | — |
| 13 | −195,956 | — |
| 14 | −273,396 | — |

**56 of the 61 iterations that printed a `p min` printed a NEGATIVE ABSOLUTE
PRESSURE**, beginning at iteration 1 and recurring through iteration 143.

### 2.2 Clipped-cell census — the spatial discriminator
`evidence/clip_map.txt`. Bounds `[10132.5, 202650] Pa` = `101325 × {0.1, 2}`.

| it | at floor | at ceiling | total | % of domain | where |
|---|---|---|---|---|---|
| 1 | 3,628 | 3,286 | 6,914 | **30.0 %** | near field 6,772 + **wall 142**; nothing beyond `r = 1.5c` |
| 6 | 7,163 | 0 | 7,163 | 31.1 % | first appearance in the **mid field** (434) |
| 9 | 0 | 3,840 | 3,840 | 16.7 % | first appearance in the **outer field** (444) |
| 10 | 0 | 16,800 | 16,800 | 72.9 % | first appearance in the **far field** (69) |
| 13 | 11,156 | 0 | 11,156 | 48.4 % | **first appearance on the INFLOW patch (15 cells)** |
| 15 | 21,201 | 0 | 21,201 | **92.0 %** | inflow 176, **first appearance on the OUTFLOW patch (6)** |

**The front moves strictly outward: wall/near → mid (it 6) → outer (it 9) → far
(it 10) → inflow (it 13) → outflow (it 15).**

### 2.3 The uncensored fields — `T`, `|U|`, `rho`
`evidence/uncensored_map.txt`. `p` is censored on disk; these are not.

**`T` minimum (K), by region.** Freestream 300 K.

| it | wall | near <1.5c | mid 1.5–6c | outer 6–20c | far >20c | inflow | outflow | global min at |
|---|---|---|---|---|---|---|---|---|
| 1 | 279.879 | 291.754 | **300.000000** | **300.000000** | **300.000000** | **300.000000** | **300.000000** | (0.9956, 0.0010) — **trailing edge** |
| 3 | 288.178 | 283.405 | 293.43 | 298.656 | 299.69 | 299.981 | 299.956 | (−0.1975, −0.0137) — ahead of LE |
| 9 | 292.56 | 267.625 | 291.61 | 292.986 | 295.748 | 299.582 | 299.46 | (1.051, 0.0089) — wake, just aft of TE |
| 15 | 293.704 | **244.199** | 270.318 | 278.537 | 284.95 | 295.621 | 296.464 | (0.0113, −0.0142) — **leading edge, lower surface** |

At **every** iteration the departure amplitude orders monotonically by distance
from the aerofoil: `near < mid < outer < far < inflow`. `T` min falls
near-monotonically after iteration 2: 285.4 → 283.4 → 276.2 → 271.5 → 269.9 →
271.8 → 270.3 → 267.6 → 266.3 → 264.2 → 256.5 → 251.1 → 246.9 → **244.2** K.
This is divergence, not a decaying start-up transient.

**`|U|` maximum (m/s).** Freestream 254.86. Near field 264 → 280 → 295 → 301 → …
→ **307.31** at it 15, at (0.025, 0.022) — the LE upper suction peak. Wall-adjacent
`|U|` falls 229 → 39.6 as the boundary layer forms — expected, not a defect.

**`rho` minimum (kg/m³).** Freestream 1.1766. Near field 1.1235 → … → **1.0175** at
it 15. Nothing catastrophic by iteration 15; the collapse to `T0 = −2.384` happens
between iteration 15 and 148.

### 2.4 Mesh quality at the departing cells — the "mesh at that location" test
Per-cell `nonOrthoAngle` and `skewness` written by `checkMesh -writeFields`.

- Cells clipped at it 1: median non-orthogonality **22.17°** vs **11.16°** for
  unclipped; 168 of the 200 worst non-orthogonal cells were clipped against a
  30.0 % base rate. **This enrichment is CONFOUNDED and is not offered as
  evidence of cause** — the near field is simultaneously where the mesh is most
  non-orthogonal *and* where the flow physics lives, so the enrichment is
  expected under every hypothesis on the table.
- **Skewness runs the other way**: clipped cells are *less* skewed (median 0.0106
  vs 0.0178), and the 200 most-skewed cells sit at `x ∈ [0.995, 93.667]`,
  `y ∈ [−47.2, 47.2]` — **the far field, where the departure arrives last**.
- **The decisive one: the worst-departing cells are near-perfect cells.** The `T`
  minimum at iterations 3–7 sits on cells with non-orthogonality **0.457°–0.581°**
  and skewness ~0.023. At iterations 11–15 it sits at 20.2°–22.4°, unremarkable
  against a gate-A maximum of 51.12°. **The mesh is not worst where the field is
  worst.**

---

## 3. LOCALISED OR GLOBAL — THE ANSWER IS NEITHER, AND IT IS DEFINITE

The supervisor asked for one of two boxes and said to report ambiguity rather than
force a fit. **The picture is not ambiguous. It is unambiguous and falls in neither box.**

> **AEROFOIL-ANCHORED, NEAR-FIELD, AT ITERATION 1, SPREADING OUTWARD.**
> Location: the near field around the aerofoil, `r < 1.5c`, plus 142 wall-adjacent
> cells — 30.0 % of the domain, both pressure bounds at once.
> Iteration: **1**. Not 5, not 148.

**It is NOT a boundary-condition defect.** The inflow, outflow, mid, outer and far
regions are at exactly freestream at iteration 1 — a zero **planted and validated**,
see §4. The inflow patch does not depart until iteration 13, twelve iterations after
the near field. A boundary defect propagates inward from the boundary; this
propagates outward to it.

**It is NOT the whole field drifting together.** 70 % of the domain is exactly
undeparted at iteration 1.

**But the supervisor's *indictment* half is partly right for a reason his spatial
half did not anticipate.** His mapping was: global ⇒ initial state or relaxation.
The signature is not global, yet the initial state is exactly what a
30 %-of-domain, iteration-1, aerofoil-anchored excursion points at: a **uniform
`101,325 Pa` / `(254.56, 12.41) m/s` field imposed impulsively on a body**, from
which the first pressure solve must build the entire stagnation-and-suction field
in one step, and overshoots to 29× freestream and to negative absolute pressure.
**The near field is where a uniform initial condition is most wrong.** Spatial
extent and cause are not the same axis, and conflating them is what the two-box
discriminator did.

**The relaxation half is ALREADY REFUTED and this arm did not need to re-test it.**
Ledger row `C-73`: pressure-probe arm A changed only the relaxation, survived
1,803 iterations against rung 1's 148 — 12.2× — and **still** died on
`Negative initial temperature T0 = −14.4053`. Relaxation is a real lever and is
not sufficient.

---

## 4. THE CONTROLS — every zero in this record is planted

**Standing rule 3 is satisfied for the specific zeros this record asserts**, not
generically.

1. **`pressureControl` reader**, 5/5: plants a distinctive `p min` at a named
   iteration and requires it back at *that* iteration and not a neighbour; and with
   every `pressureControl` line stripped, requires the reader to report **no** `p`
   extremes — so an absent reading is a reading, not a manufactured zero.
2. **Field reader**, 8/8 (`readers/field_probe.py --selftest`): plants
   `−7.654321e+09` into cell **12345** of a real written `5/p` **on disk** and
   requires the value back at exactly that index; plants `−1.357911e+09` on the
   `inflow` patch and requires it reported on *that* patch and **not leaked** into
   another; requires the clean field not to contain the plant; requires the cell
   count unchanged.
3. **THE ZERO ACTUALLY CLAIMED.** §2.3 asserts *exactly 300.000000 K* in five
   regions at iteration 1 — the load-bearing claim of this whole record. A known
   `123.456789` was planted into one cell of **each of those five regions** in turn
   and the region reader was required to see it, localise it to the right cell, and
   **not** leak it into a neighbouring region. **5/5 passed.** The reader is shown
   able to see a non-300 value everywhere I report 300.
4. **S17** (`MONITOR_STANDARD.md`): the case runs `nNonOrthogonalCorrectors 1`, read
   from its own `fvSolution` — **two `p` solves per outer iteration**. Every residual
   in this record is the **FIRST solve**, stated on its face. The existing validated
   reader was **reused unmodified** (sha `a5c9d60a…`) and its selftest re-run on
   this arm's log: 5/5, including the discrimination arm proving first and last are
   distinguishable and that the two series actually differ on the unplanted log
   (15/15 iterations).

---

## 5. A MECHANISM CANDIDATE, OFFERED AS A CANDIDATE AND NOT AS A FINDING

Three of the last four mechanism claims on this line were corrected, twice from
source. **This is not offered as established.** What *is* established is
observational (§2) plus the following, read from source:

`applications/solvers/compressible/rhoSimpleFoam/pEqn.H` runs in this order —
`phi = phiHbyA + pEqn.flux()` (line 76), continuity errors, `p.relax()` (84),
`U = HbyA - rAU*fvc::grad(p)` (86), **`pressureControl.limit(p)` (90)**,
`rho = thermo.rho()` (105).

**`phi` and `U` are formed BEFORE the clip and are never recomputed after it.**
Only `rho` and the boundary conditions see the clipped `p`. So once clipping fires,
the mass flux carries the *unclipped* pressure field and the density carries the
*clipped* one — **on 30 % of cells at iteration 1 and 92 % at iteration 15.** The
run's own reported continuity error rises 14×, from `8.216e-05` at iteration 1 to
`1.149e-03` at iteration 147.

**What this does NOT establish:** whether that inconsistency *drives* the divergence
or merely *records* it. Both readings fit the data I have. Testing it requires
moving `pMinFactor` / `pMaxFactor` — **a registered value, and a lever this arm is
forbidden to touch.** It is named here and left to the supervisor.

---

## 6. IS THE TRIAGE CONCLUSION SUPPORTED? — SPLIT, AND THE SPLIT IS THE POINT

The supervisor asked to have his conclusion attacked, not confirmed.

**SUPPORTED, structurally.** *"The abort is a symptom of an already-diverging outer
iteration, not an independent defect of the linear solver."* This arm supports it
and strengthens it. The abort is an explicit **range check on garbage input**, the
field was diverging from iteration 1, and the linear solver is not implicated
anywhere in rung 1's life.

**CONTRADICTED, mechanically, in three places.**
1. **There is no FPE.** `rc = 134` is `std::abort()` from an explicit `T0 < 0`
   range check, not a floating-point trap. The triage's "consistent with an FP trap"
   is wrong for rung 1.
2. **GAMG is not implicated at all** — not merely "wrongly blamed". At the aborting
   iteration the pressure equation had not yet run.
3. **The onset is iteration 1, not ~5**, and "it never descended" is not right
   either: first-solve `p` descended by two orders of magnitude over five
   iterations — **on a field that had already been censored by the clip.**

**AND THE SUPERVISOR'S OWN FALSIFIABLE TEST IS MALFORMED AS WRITTEN.** §3.3 states:
*"if the outer iteration were made to descend, the FPE would not occur — and if it
still occurred on a descending run, my triage is wrong."* **There is no FPE to
occur or not occur**, so the test cannot be run as specified and neither branch can
be reached. Restated so it is testable, it becomes: *if the outer iteration were
made to descend, `T` would not go negative* — and `C-73`'s arm A is already a
partial run of exactly that, returning **NO**: a better-relaxed, 12.2×-longer run
still reached `T0 = −14.4053`.

**UNTESTABLE BY THIS ARM:** whether the clip inconsistency of §5 is cause or
symptom; and whether a ramped or non-uniform initial state removes the iteration-1
excursion. Both need a lever.

---

## 7. ASSERTIONS, AND THE COST

**Fingerprint of the registered rung-1 directory** — sha256 of the sha256-list of
every file under it — **EQUAL before and after**:
`2fb24ff2109188692df3eb62b2ee83f1f9a952c1513f51af49f1b11f78d0a821`
(`rung1_fingerprint_before.txt`, `rung1_fingerprint_after.txt`).
**Rungs 2–5 asserted ABSENT before and after**, and no `attempt3*` root exists.
`launch_f12_rung.py`, `F12_PREREGISTRATION.md` and rung 1's outputs were not edited.
The rung-2 interlock was not approached.

**Cost — measured, per standing rule 12.**

| | |
|---|---|
| Cap, registered **before** the run | **10.0 core-min**, 1 rank |
| Solver, **measured** (`evidence/WALL_S.txt`) | 2.995 s × 1 rank ÷ 60 = **0.0499 core-min** |
| Utility passes (`writeCellCentres`, `checkMesh -writeFields`), measured | 1.133 s per pass × 2 = **0.0378 core-min** |
| **Total measured** | **0.0877 core-min — 0.88 % of cap. NOT breached.** |
| Predicted in the pre-registration | ~1.4 s solve = 0.0233 core-min |
| **Ratio actual/predicted (solve)** | **2.14×** |
| Gap attribution | **Misprediction, mine, and fully accounted.** I costed the solve and not the 15 full ascii field writes at `writePrecision 10`. Registered rung 1: 13.29 s ÷ 148 it = 0.0898 s/it *without* per-iteration writes. This arm: 2.995 ÷ 15 = 0.1997 s/it. The 0.110 s/it delta × 15 = 1.65 s is the entire gap. |
| Contention, named separately | **Not the cause.** `load1 = 9.64` of 16 cores = **60 %**, below Sanaa's 80–90 % target, sampled throughout into `evidence/CONTENTION_field_observation_2026-08-25.txt` (the run was shorter than two sampler periods, so 2 samples). |
| Waste, named separately | **0.0189 core-min** — the second utility pass, re-run solely to obtain an honest timing for this row. It produced no new evidence. Named, not absorbed into the ratio. |
| Dollars | **$0.000075, DERIVED at $0.0513/core-h, reported-by-owner — NEVER measured.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). |

**Verdict vocabulary:** none is due. This arm grades nothing, and rung 1's
`NOT A RESULT` and rung 2's `BLOCKED` are unchanged by it.
