# K0h. Blay–Mergui–Niculae ventilated cavity, transient statistically-stationary state: STAGED RE-COST SUCCESSOR TO K0g — PRE-REGISTRATION

> # DRAFT — NOT FROZEN. NO COMPUTE UNDER THIS DOCUMENT.
>
> **Status: DRAFT, 2026-09-10, written by a heat-transfer lab-lane at ZERO
> COMPUTE.** No gate, threshold, band, cap or label in this file is frozen; no
> `GRADING_PATH_FREEZE_COMMIT` is set (every pin below reads
> **`PIN-AT-FREEZE`**); **no K0h run directory exists and none may be created
> until the heat-transfer supervisor freezes this document by sha** (standing
> rule 2). Until that freeze this file is amendable **and every amendment must
> state its condition and how it was checked** — the condition is *"no
> `verification/runs/F14-cooling-ladder/K0h_runs/` exists"*, checked by its
> absence on disk.
>
> **Section 11 lists the decisions this draft does NOT take.** They are the
> supervisor's, and two of them are jointly the supervisor's and
> verification's. A lane does not rule on them and this draft does not
> pre-empt them.
>
> **`docs/campaigns/F14-cooling-ladder/K0g_PREREGISTRATION.md` IS FROZEN AND IS
> NOT EDITED BY THIS DOCUMENT** (standing rule 6). Nothing here amends it; a
> departure from K0g would be a dated amendment appended at ITS foot, written
> by the supervisor, and this draft writes none.

**Predecessor: `K0g` (explicit, for §2ay linkage).** K0g ran five arms, reached
its own frozen §8 CEILING of **915.58 core-min** at a measured spend of
**888.12 core-min**, and the supervisor executed K0g §8's pre-registered stop —
verbatim, *"Reaching the CEILING STOPS THE RUN with unrun arms named; an
overrun does not get a new budget (rule 12)"* — on the three live L2 arms at
2026-09-10T03:47Z. Whole-rung state: **PENDING**. `mark_done_k0g.py` rc=1 (2 of
5 arms meet the strict completion rule); the frozen comparator `analyse_k0g.py`
**REFUSED (exit 2)** rather than grade a partial rung. **No K0g gate has ever
been evaluated and no graded G-row value has ever been produced.**

---

## 0. WHY K0h EXISTS, AND WHAT IT IS NOT

### 0.1 K0g's STOP WAS A BUDGET OUTCOME. IT WAS NOT A PHYSICS FINDING.

**Stated on this document's face, because the distinction is the whole reason
K0h is state (b) and not state (a):**

**Nothing in K0g measured a limit on the lab's ability to compute this flow.**
Two arms — `M1_c` and `M2_c`, both L1 — ran to `endTime = 60 s`, returned
`rc = 0`, wrote an `End` line, wrote `TMean`/`UMean` in the `20`, `40` and `60`
directories exactly as §7.1' registered, and **met the strict completion rule on
all clauses** (`DONE.M1_c`, `DONE.M2_c`). The transient method *worked*. The
three L2 arms were **stopped by the budget rule while making normal monotone
progress** — `rc = 143` is a SIGTERM the supervisor sent, not a crash, a
divergence or a stall (`ExecutionTime/ClockTime` = 0.9966–0.9977 on all three;
`Time` advanced monotonically to the last written step).

**What K0g actually measured is a COST MODEL that was wrong before the first
time step, and it was wrong on two independent axes, of which the larger was not
the one first suspected** (§8.1). K0g's §8 could never have bought five completed
arms: the completion cost is **2194.99 core-min**, which is **2.40× K0g's own
CEILING**. The stop was the budget rule catching a mis-costed campaign, exactly
as rule 12 intends.

> **§2ay MAPPING: K0g `PENDING` (budget stop + comparator refusal) → STATE (b),
> A DATED SUCCESSOR — this document. NOT state (a), a capability gap.** No agent
> and no record may read K0g's stop as evidence that the lab cannot compute the
> Blay cavity to a statistically stationary state. It has not been tried at L2 to
> `endTime`, because the budget stopped before it could be.

### 0.2 K0g HAD **TWO** INDEPENDENT BLOCKERS, AND A RE-COST ALONE WOULD HIT THE SECOND

A successor that only re-registers §8 would spend its whole new budget and then
**refuse at exactly the same place**, because the second blocker is not a budget
matter at all:

**`check_k0g_extraction_equivalence.py` REFUSED (exit 2) on `M1_c` and `M2_c` —
the two arms that COMPLETED CLEANLY.** Verbatim from `K0g_VERDICT.txt`:

> `REFUSE: .../M1_c/60/TMean: patch 'outlet' carries a NONUNIFORM value. This
> reader refuses rather than guess the patch face ORDER. `T` and `U` -- the only
> fields the registered A1.3a extraction samples -- cannot carry one.`

**The registered A1.3a extraction path would have refused on those arms under an
unlimited budget.** §4 of this draft diagnoses it, and **does not relax the
reader**.

---

## 4. THE EXTRACTION-EQUIVALENCE REFUSAL — DIAGNOSED, NOT PAPERED OVER

*(Numbered 4 because K0g's §§1, 2, 3, 5 are carried by citation below and this
is the one genuinely new section. It is placed first because §0.2 says it
outranks the re-cost.)*

### 4.1 THE MECHANISM, MEASURED ON THE ACTUAL FIELD FILES

The hypothesis handed to this lane was *"`fieldAverage` writing a
calculated/averaged patch value where the base field carries a uniform BC"*. It
was **tested against disk, not asserted**, and it is **confirmed with one
correction**: the trigger is not a uniform BC at all — it is an **evaluated**
one.

Read from `verification/runs/F14-cooling-ladder/K0g_runs/M1_c/60/`:

| patch | `T` (base field) | `TMean` (`fieldAverage` output) |
| --- | --- | --- |
| `inlet` | `fixedValue`, `uniform 288.15` | `calculated`, **uniform** 288.1499999999996 |
| `floor` | `fixedValue`, `uniform 308.15` | `calculated`, **uniform** 308.1499999999997 |
| `ceiling`, `leftWall`, `rightWall` | `fixedValue`, `uniform 288.15` | `calculated`, **uniform** |
| **`outlet`** | **`zeroGradient`** (type only, no `value`) | `calculated`, **`nonuniform List<scalar>` of 12** |
| `frontAndBack` | `empty` | `empty` |

`U`/`UMean` behave identically (`noSlip` walls → uniform; `outlet`
`zeroGradient` → `nonuniform List<vector>` of 12).

**Therefore:** `fieldAverage` writes EVERY patch of its output field as
`type calculated` **with an explicit `value` entry**. A patch whose base-field
condition is a *constant* (`fixedValue uniform`, `noSlip`) averages to that same
constant and stays `uniform`. A patch whose base-field condition is *evaluated
per face* — here `outlet`'s `zeroGradient`, and it is the **only** such patch in
this case — averages to a per-face list and is written `nonuniform`. **The
outlet's 12 faces are the 12 y-cells of the bottom mesh block**
(`system/blockMeshDict`: `hex (0 1 3 2 8 9 11 10) (160 12 1)`).

### 4.2 THE READER IS RIGHT TO REFUSE, AND ITS REFUSAL EXPOSES A MIS-SPECIFICATION ONE LAYER UP

`scripts/analyse_k0g.py:672` (`read_boundary_values`) resolves patch types
explicitly and refuses anything it cannot place. Its own docstring states the
invariant the refusal rests on:

> *"A NONUNIFORM patch value REFUSES. Neither `T` nor `U` — the only fields the
> registered extraction of A1.3a samples — can carry one."*

**That invariant is TRUE of `T` and `U`. It is FALSE of `TMean` and `UMean`.**
K0g §7.1'/§7.4/§7.5 pointed a reader inherited from K0f — where the graded field
*was* the instantaneous `T`/`U` — at a **new class of field**, `fieldAverage`
output, whose patch representation the invariant was never written against. The
grading-path blob freeze (`check_comparator_freeze` PASS 8/8) cannot see this:
it proves the bytes are the frozen bytes, not that the frozen bytes suit the
field they will be aimed at.

> **This is a mis-specification of the registered A1.3a extraction for a
> `fieldAverage` output — NOT a case defect, NOT a reader bug, and NOT something
> a lane rewrites. It is routed to the supervisor as §11 item 2.** The reader's
> refuse-rather-than-guess behaviour is the lab's instrument standard working,
> and **this draft proposes no relaxation of it.**

### 4.3 THE CASE-SIDE FIX IS AVAILABLE AND THIS DRAFT REJECTS IT

The only case-side change that would make `TMean`'s outlet patch uniform is to
replace the outlet's `zeroGradient` condition with a uniform-valued one. **That
is a PHYSICS change to a boundary-condition set that K0g §1 carries
BYTE-UNCHANGED by citation from `K0f_PREREGISTRATION.md` §1 and through it
`K0d_REREGISTRATION.md` §§1–1.3.** Changing an outflow BC to buy an instrument a
pass is exactly the move the lab forbids. **REJECTED. Not proposed. Named here
so that no later reader has to rediscover that it was considered.**

Likewise rejected: sampling only interior quantities to dodge the patch. K0g §V
records that the boundary half of the reader **is** the K0d defect repair — a
`cellPoint` reader that cannot see a boundary condition was measured wrong by
1.209843 K at the floor. Dropping it back out is a regression to a known defect.

### 4.4 THE MEASURED FACT THAT MAKES THE REPAIR CHEAP — AND VERIFIABLE PRE-COMPUTE

**The 12 nonuniform `outlet` face values are BIT-IDENTICAL to the 12 adjacent
last-column cell values of the internal field.**

Measured, `max|diff| = 0.0` exactly, on **both** completed arms and **both**
fields:

| field | arm | faces | `max |face − adjacent cell|` |
| --- | --- | ---: | ---: |
| `TMean` | `M1_c` | 12 | **0.0** (all 12 faces, e.g. 303.179200857 vs 303.179200857) |
| `TMean` | `M2_c` | 12 | **0.0** |
| `UMean` | `M2_c` | 12 | **0.0** (all three components) |

Mapping used: cell index `cj*nx + (nx-1)`, `nx = 160`, `cj = 0…11` — i.e. the
last column, ascending `j`. The profile is strongly non-constant
(303.18 K → 288.46 K across the 12 faces), so bit-exact agreement on all 12 in
that order is not a coincidence of a flat field.

**Consequence, and it is the load-bearing one:** the value `fieldAverage` writes
on this patch is **exactly the `zeroGradient` reading `read_boundary_values`
already implements for `T` and `U`** (`val = None`, resolved by the caller from
the adjacent cell). Resolving it that way is **not an approximation, not a
guess at face order, and not a relaxation** — it is bit-exact agreement with
what OpenFOAM wrote, and it moves **no graded number by any amount**.

### 4.5 WHAT K0h REGISTERS, IF THE SUPERVISOR RULES THE REPAIR IN (§11 item 2)

**Registered form — narrow, asserted, and refusing by default:**

> On a `fieldAverage` output field, a patch of `type calculated` carrying a
> `nonuniform` value list is resolved **only** when (a) the corresponding patch
> of the **base field at the same time directory** is `zeroGradient`, **and**
> (b) the written list is **verified equal, element-wise and exactly, to the
> adjacent-cell values of the averaged field's internal field** in mesh patch
> face order. If (a) fails, or if (b) fails by any amount, the reader
> **REFUSES (exit 2)** exactly as it does today. The equality in (b) is a
> **run-time ASSERT executed on every read, never a pre-compute belief**
> (`CLAUDE.md` rule 14: a lesson is not applied until every call site asserts
> it).

This is a **capability addition guarded by an assert**, not a weakening: a
nonuniform patch the reader cannot place still refuses.

**It lands in a NEW instrument, `scripts/analyse_k0h.py`, derived from
`analyse_k0g.py`. `scripts/analyse_k0g.py` IS FROZEN AND IS NOT EDITED**
(standing rule 6). Same for every other instrument in §7.7.

**A FOURTH PLANT, `P4`, is registered on the new path** (standing rule 3): a
`1.234e-03 K` perturbation planted into **one interior outlet-adjacent cell** of
a COPY of `TMean(avg2)`, read back through the production boundary path — **must
be SEEN**, and if the reader cannot see it the comparator **REFUSES**. Without
`P4` the repaired path would be the one channel in this comparator with no
planted-zero control, which is the defect standing rule 3 exists to prevent.

### 4.6 mark_done_k0g's M1_m FLAG IS THE INSTRUMENT WORKING, NOT A DEFECT

`mark_done_k0g.py` reported on `M1_m`: *"10690 ExecutionTime lines != 10691
'Time =' lines (a truncated or duplicated solver log)"*. That is the **expected
signature of SIGTERM landing between a step header and its `ExecutionTime`
line** — the strict completion rule's log-consistency clause behaving exactly as
designed on a signal stop. **Recorded as instrument-correct. No repair is
registered for it and none is needed.** K0h carries the clause unchanged.

---

## 1, 2, 3, 5. CASE, REFERENCE, QUANTITIES, LADDER — CARRIED FROM K0g UNCHANGED

**Adopted BY CITATION, byte-unchanged, from `K0g_PREREGISTRATION.md` §§1, 2, 3
and 5** (and through them `K0f_PREREGISTRATION.md` and `K0d_REREGISTRATION.md`):

- **§1 CASE** — Blay–Mergui–Niculae ventilated cavity; 2D `x, y ∈ [0, 1.04]`;
  inlet `x = 0, y ∈ [1.022, 1.040]`; outlet `x = 1.04, y ∈ [0, 0.024]`;
  `T_ref 298.00 K`, `β 3.3557047e-03 K⁻¹`, `ν 1.569e-5 m²/s`, `Pr 0.71`,
  `Pr_t 0.85` (never tuned), `ΔT 20.0 K`, **`Ra 2.135970e9` DERIVED, REPORTED,
  NEVER A TARGET**. Solver `buoyantBoussinesqPimpleFoam`. **No boundary
  condition is changed — see §4.3.**
- **§2 REFERENCE** — Blay, Mergui & Niculae (1992), ASME HTD-213,
  **`NOT OBTAINED`**; obtaining it is outside the box and **Sanaa's alone**
  (standing rules 7, 8). **K0h grades NO row against `P`.** Not worked around.
- **§3 QUANTITIES AND BANDS** — rows `G1 G2 G3 G4 G5a G5b G6 G7 G8 S1`; thirteen
  graded stations; reported rows `M0`, `R1`; the five guards `HB B I DC MB`; the
  bands **`±1.00 K`, `±0.0570 m/s`, `±0.0208 m`, `±0.104 m`, `±10 % of |q_ref|`,
  `EXACT MATCH REQUIRED`**; `y⁺` windows **`≤ 5.0` on L1**, **`≤ 3.3` on L2**.
  **NO BAND IS SET, WIDENED, NARROWED OR REINTERPRETED BY THIS DOCUMENT.**
- **§5 LADDER** — serial, **`nProcs = 1`, no decomposition**; **L1 (25 600
  cells) and L2 (50 176) authorised, L3 (98 596) DEFINED AND NOT AUTHORISED**;
  the same **five arms** `M1_c` `M2_c` `M1_m` `M2_m` `C_lam`; `B_hi`, `I_hi`,
  `M1_m_seed`, `M1_f`, `M2_f` **defined and NOT authorised**. Fresh case
  directories under a distinct `K0h_runs/` root; the age guard refuses any case
  whose `0/` or a time directory already exists.

## 7.1', 7.1'', 7.2, 7.3, 7.4, 7.6 — THE PHYSICS AND STATIONARITY MACHINERY, CARRIED UNCHANGED

**Adopted BY CITATION, byte-unchanged, from `K0g_PREREGISTRATION.md`:**

- **§7.1' STATIONARITY** — `U_b = 0.8275 m/s`, `τ = 1.257 s`; `ddtScheme Euler`;
  `adjustTimeStep` with **`maxCo = 2.0`**, **`maxDeltaT = 0.05 s`**,
  `deltaT₀ = 1e-3 s`; PIMPLE `nOuterCorrectors 2`, `nCorrectors 2`,
  `nNonOrthogonalCorrectors 1`, outer `residualControl 1e-4` on `p_rgh` and `U`;
  **`endTime = 60.0 s`**; the SINGLE `fieldAverage` FO `windowAvg` with
  `restartOnOutput true`, `timeStart 20`, `writeInterval 20 s`; spin-up
  `[0, 20]` **discarded**, `avg1 = [20, 40]` at dir `40`, **`avg2 = [40, 60]` at
  dir `60` (the GRADED window)**; and the criterion
  **`max_cell |TMean(avg2) − TMean(avg1)| ≤ tol_T = 0.020 K`**,
  **`max_cell |UMean(avg2) − UMean(avg1)| ≤ tol_U = 0.005 m/s` per component**.
  **`tol_T` AND `tol_U` ARE BYTE-UNCHANGED AND ARE NEVER WIDENED TO ADMIT A
  CASE.**
- **§7.1'' THE ONE REGISTERED EXTENSION** — `endTime 60 → 120 s` from the 60 s
  field, `avg1' = [80, 100]`, `avg2' = [100, 120]`. **A second is not
  authorised.** The decision is taken **on the stationarity-drift numbers alone,
  never with a graded G-row value in view**. An arm still failing at 120 s is a
  finding of genuine RANS-mean unsteadiness and its successor is a
  re-registration, **not** a `tol` relaxation.
- **§7.2 STRICT COMPLETION RULE (transient-adapted) + the age guard** — carried
  in full, including the per-closure field sets, `TMean`/`UMean` from `avg2`,
  the `ExecutionTime`-count clause (§4.6) and **every field at `endTime` newer
  than the case's own `0/T`**. `mark_done_k0h.py` **refuses (exit 2)** rather
  than infer any exemption.
- **§7.3 ROACHE TRIPLE GATING** — standing rule 5, `Fs = 1.25`, carried and, as
  at K0g, **UNREACHABLE** under L1+L2 only.
- **§7.4 PLANTED-ZERO CONTROL** — `P1`, `P2`, `P3` carried unchanged, **plus the
  new `P4` of §4.5**.
- **§7.6 NO SELF-GRADING** — no verdict is assigned by the lane that runs this.

### 0.3 THE CEILING K0h STATES ON ITS OWN FACE

**Unchanged from K0g §0.1: `HOLDS` is unreachable; the `G` (GCI) ground is
unreachable (L1+L2 only, no triple, no observed order); the `P` ground is
unreachable (Blay `NOT OBTAINED`). THE BEST VERDICT K0h CAN REACH IS
`GATE REACHED`, naming both `P` and `G` unreached.** No band is widened and no
reference is worked around to manufacture a pass.

---

## 8. COST, RE-REGISTERED ON A MEASURED BASIS (standing rule 12)

**K0g's §8 is FROZEN and is not edited. This section re-registers the cost line
for K0h from K0g's MEASURED artifacts. Re-registering a cost line is
legitimate; re-registering a physics threshold is not, and §11 item 4 records
that no physics threshold was touched.**

### 8.1 WHY THE K0g COST MODEL MISSED — TWO AXES, AND THE LARGER IS NOT `Δt`

K0g §8 priced an arm as `cells × (60/Δt_mean) × nOuterCorrectors × rate`, with
**`Δt_mean = 5e-3 s`** and **`rate = 4.8e-6 s`** per cell-effective-iteration
(K0f's measured SIMPLE rate **× an ASSUMED 1.5 transient overhead**). §8 named
both as calibration items: *"none is called measured."* Both were wrong.

**AXIS 1 — `Δt_mean`, and it differs BY LEVEL, which one registered figure could
not express.** Measured as last `Time` ÷ count of `^Time = ` lines in
`verification/runs/F14-cooling-ladder/K0g_runs/<case>/log.solve`:

| arm | level | sim t reached | steps | **`Δt_mean` measured** | steps vs registered 5e-3 |
| --- | --- | ---: | ---: | ---: | ---: |
| `M1_c` | L1 | 60.0000 | 16 012 | **3.7472e-03 s** | ×1.334 |
| `M2_c` | L1 | 60.0000 | 15 956 | **3.7603e-03 s** | ×1.330 |
| `M1_m` | L2 | 27.6883 | 10 691 | **2.5899e-03 s** | ×1.931 |
| `M2_m` | L2 | 12.9489 | 4 978 | **2.6012e-03 s** | ×1.922 |
| `C_lam` | L2 | 14.2073 | 5 496 | **2.5850e-03 s** | ×1.934 |

`Δt` is **quartile-flat** (M1_c 3.7104 / 3.7534 / 3.7620 / 3.7629e-3 across
quartiles; M1_m 2.5917 / 2.5715 / 2.5980 / 2.5983e-3), so it is a **mesh
property under `maxCo = 2.0`, not a transient-development property**. K0g §8's
"+0.5S contingency for `Δt_mean` proving smaller than estimated" was aimed at a
risk that is real but **stable and measurable in minutes on a pilot**.

**AXIS 2 — the per-cell-step rate, and this is the DOMINANT miss.** Registered
`4.8e-6 s` per cell-effective-iteration × 2 outer correctors = **9.6e-6 s per
cell-step**. Measured `wall_s ÷ steps ÷ cells`:

| arm | measured s/cell/step | vs registered 9.6e-6 |
| --- | ---: | ---: |
| `M1_c` L1 | 2.2717e-05 | **×2.37** |
| `M2_c` L1 | 2.2993e-05 | **×2.40** |
| `M1_m` L2 | 3.3113e-05 | **×3.45** |
| `M2_m` L2 | 3.3846e-05 | **×3.53** |
| `C_lam` L2 | 3.0337e-05 | **×3.16** |

Against K0f's SIMPLE per-cell-iteration rate, the **actual transient overhead is
×3.59 (L1) and ×4.77 (L2)** — the registered figure was **×1.5**.

**MECHANISM, MEASURED not assumed.** From
`K0g_runs/M1_c/system/fvSolution` and ~1400 consecutive steps in each
`log.solve` tail: the solver performs **exactly 8.00 `p_rgh` solves per time
step** (`nOuterCorrectors` 2 × `nCorrectors` 2 × (1 + `nNonOrthogonalCorrectors`
1)), at **1159.2 (M1_c) / 1904.8 (M1_m) / 1598.1 (M2_m) / 1513.4 (C_lam) DICPCG
iterations per time step**; the two `p_rghFinal` solves per corrector carry
`relTol 0` to `tolerance 1e-10` and cost 222–310 PCG sweeps each. **A PIMPLE
step here is 7–10 SIMPLE-equivalent pressure solves, not the 3 the ×1.5 factor
assumed.**

**The axes multiply and reconstruct the measured ratio exactly:** L1
1.334 × 2.366 = **3.158** = `M1_c`'s measured ratio. **`P-K0g-3` (cost ratio
actual/POINT within `[0.8, 1.6]` per arm) is FALSIFIED on both completed arms,
at 3.158 and 3.185.** Stated plainly, not softened.

**Also mispredicted: the ×0.75 laminar factor — measured 0.896**
(`C_lam` 3.0337e-05 vs `M2_m` 3.3846e-05 s/cell/step).

**CONTENTION IS NOT NAMED AS A SEPARATE FIGURE, AND THAT IS THE HONEST
ANSWER.** ~11 concurrent 1-rank solvers on 16 vCPU cannot deschedule a 1-rank
job, and the artifacts measure it: `ExecutionTime/ClockTime` = **0.99886,
0.99905, 0.99773, 0.99671, 0.99657** across the five arms. The descheduling
channel is measurably ≈ 0. A shared-memory-bandwidth/L3 channel remains possible
but is **not separable from the per-cell-step rate with these artifacts**, so it
is carried *inside* the measured rate below and **no contention number is
invented**. `COMPUTE_BUDGET_CHARTER` §6 requires waste to be *named separately*,
not that an unmeasurable quantity be estimated and called one.

### 8.2 THE K0h COST BASIS — SHOW THE ARITHMETIC

Per-arm cost to `endTime = 60 s`, at `ranks = 1` (so core-min = wall s ÷ 60):

```
  cost(arm)  =  (60 s / Δt_mean(arm))  ×  s_per_step(arm)  /  60
  s_per_step =  wall_s / steps                       [measured, K0g log.solve]
```

| arm | level | s/step measured | `Δt` measured | steps to 60 s | **core-min to 60 s** | basis |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `M1_c` | L1 | 0.58156 | 3.7472e-03 | 16 012 | **155.20** | **MEASURED (ran to 60 s)** |
| `M2_c` | L1 | 0.58862 | 3.7603e-03 | 15 956 | **156.53** | **MEASURED (ran to 60 s)** |
| `M1_m` | L2 | 1.66149 | 2.5899e-03 | 23 167 | **641.5** | PROJECTED |
| `M2_m` | L2 | 1.69827 | 2.6012e-03 | 23 066 | **652.9** | PROJECTED |
| `C_lam` | L2 | 1.52220 | 2.5850e-03 | 23 211 | **588.9** | PROJECTED |
| **SOLVER SUBTOTAL `S`** | | | | | **2 194.99** | 2 measured + 3 projected |

Worked example, `M1_m`: `60 / 2.5899e-03 = 23 166.9` steps
× `1.66149 s` = `38 492 s` = **641.5 core-min**; equivalently
`296.05 × (60 / 27.6883) = 641.5`.

| instruments, bounded | core-min |
| --- | ---: |
| meshing (L1 + L2) | 2.00 |
| `check_k0h_mesh.py` | 0.50 |
| `mark_done` + `analyse` + `fieldAverage` extraction + the four plants + selftests | 3.50 |
| extraction-equivalence gate + instrument-standard + launcher selftest | ≤ 2.00 |
| **`I` = instruments, bounded** | **≤ 8.00** |

*(`I` is raised from K0g's ≤ 7.50 to ≤ 8.00 for the `P4` plant and the §4.5
assert path. It remains a **bound**, not a measurement — K0g's `I` was never
separately instrumented, so K0h registers §11 item 5: instrument spend is timed
and recorded so the bound becomes measured at K0h's own calibration.)*

```
  REGISTERED POINT   = S + I         = 2194.99 +   8.00 = 2202.99 core-min
  REGISTERED CEILING = 2S + 0.5S + I = 4389.98 + 1097.50 + 8.00 = 5495.48 core-min
```

**CEILING structure, unchanged in FORM from K0g §8 and deliberately so:** `2S` =
base run + the one §7.1'' extension (physical time doubled 60 → 120 s);
`+0.5S` contingency; `+I`. **The contingency is RETAINED at 0.5S and not
tightened**, even though `Δt` is now measured and flat, because §8.3's staged
plan is chosen so that *arms complete* — and a ceiling tightened to look
disciplined that then stops an arm at 55 of 60 s reproduces exactly the K0g
failure mode. The contingency now covers a *different* named risk: the per-step
rate under a different concurrency (§8.3).

**Dollars, DERIVED, NOT MEASURED**, at the owner-reported **$0.0513/core-h**
(`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing):

```
  POINT    2202.99 / 60 = 36.716 core-h × $0.0513 = $1.8836   DERIVED
  CEILING  5495.48 / 60 = 91.591 core-h × $0.0513 = $4.6987   DERIVED
```

Under the $25 per-run pre-authorisation. **A blanket is not a per-item read
(standing rule 9); this section is that per-item read.**

### 8.3 THE STAGED PLAN — THE FIX FOR THE FAILURE MODE K0g HIT

**K0g's structural error was not only the cost model. It was that a
CAMPAIGN-WIDE ceiling was armed over FIVE CONCURRENTLY-LAUNCHED arms, so when
the ceiling bit it killed three arms IN FLIGHT and the campaign finished 2 of 5.
888.12 core-min bought two completed L1 arms and no graded number at all.**

**K0h registers STAGES with PER-STAGE budgets. A stage budget's exhaustion
BLOCKS THE NEXT STAGE FROM LAUNCHING; it does not kill an arm in flight.** An
arm in flight is stopped only by its own per-arm hard stop (§8.4).

| stage | arms | core-min | concurrency | ≈ wall | stage gate before the next stage |
| --- | --- | ---: | ---: | ---: | --- |
| **1** | `M1_c`, `M2_c` (L1) | **311.73** | 2 | ≈ 2.6 h | **Are the L1 arms STATIONARY at 60 s under §7.1'?** |
| **2** | `M1_m`, `M2_m` (L2) | **1 294.4** | 2 | ≈ 10.8 h | Is L2 stationary, and does `C_lam` still need L2? |
| **3** | `C_lam` (L2 control) | **588.9** | 1 | ≈ 9.8 h | — |
| | | **2 194.99 = S** | | ≈ 23 h | |

**THE STAGE-1 GATE IS THE WHOLE POINT.** L1 costs **14 %** of the campaign and
answers the barrier question — *does the transient method reach a stationary
state at all* — before the expensive 88 % is committed. If L1 is **not**
stationary at 60 s, the §7.1'' extension decision fires **at L1**, where it
costs ~155 core-min per arm, **not at L2 where it costs ~640**. K0g launched all
five at once and therefore learned nothing it could act on before its budget
was gone.

**`C_lam` IS NOT DROPPED.** It is the registered discrimination control for
`P-K0h-2` and dropping it to save 588.9 core-min would weaken exactly the
evidence that makes the finding defensible. It is scheduled **last** because it
is the arm whose *predicted* outcome is failure — the one arm whose result the
campaign can afford to be waiting on.

**TRADE-OFF, STATED HONESTLY.** Staging serialises: calendar-to-last-arm is
≈ 23 h against ≈ 11 h for a hypothetical 5-way parallel launch that nothing
stopped. **K0h accepts the longer calendar.** What it buys: (a) every stage
either completes or is stopped *before* it starts, never partway; (b) a
decision point before the expensive stage; (c) the bandwidth-contention channel
of §8.1 reduced by lower concurrency — **unquantified, and claimed only as a
direction, not a number**; (d) a demo-able L1 result in ≈ 2.6 h rather than
nothing in 23 h. **Core-minutes are essentially invariant to concurrency for
CPU-bound 1-rank jobs, so staging does not SAVE budget — it changes what the
budget BUYS.** That is the correction K0g's outcome demands: the lab's priority
is cases that COMPLETE and produce demo-able results, and a plan that spends the
whole budget and completes nothing is the failure mode just measured.

**BOX CAPACITY.** Five 1-rank arms on a 16-vCPU box is not a capacity problem —
K0g proved a 1-rank job is not descheduled at that load (§8.1). It is a
*scheduling* problem, and §8.3 is the schedule. Concurrency 2 is registered
rather than 5 so that a stage's arms finish together and the stage gate can
actually be read.

### 8.4 PER-ARM HARD STOPS — TIGHTENED, ON A MEASURED BASIS

K0g's per-arm stops were **10× POINT**, so loose that they never fired and the
campaign ceiling killed the arms instead. K0h registers **2.5× each arm's
measured/projected §8.2 basis**, enforced as a wall-clock `timeout`
= `cap_core_min × 60 ÷ ranks`, `ranks = 1`:

| arm | §8.2 basis (core-min) | **cap = 2.5× (core-min)** | enforced `timeout` (s) |
| --- | ---: | ---: | ---: |
| `M1_c` | 155.20 | 388.0 | 23 280 |
| `M2_c` | 156.53 | 391.3 | 23 480 |
| `M1_m` | 641.5 | 1 603.8 | 96 230 |
| `M2_m` | 652.9 | 1 632.2 | 97 931 |
| `C_lam` | 588.9 | 1 472.1 | 88 327 |

**Why 2.5× and not tighter:** within-level `s/step` variance in K0g was small
(L2 turbulent arms 1.66149 vs 1.69827, 2.2 %), so 2.5× is not covering noise —
it covers a *different concurrency* and the residual bandwidth channel §8.1
could not measure. **Why not looser:** a cap that never fires is not a cap.

A `timeout` expiry is a **CAP-STOP (rc 124)**, not a crash;
`STATUS.<case>` records `timeout_s` and `wall`. **A cap-stop, like a ceiling
stop, does not get a new budget (rule 12).**

### 8.5 `cost_basis` — WHAT IS MEASURED AND WHAT IS STILL A CALIBRATION ITEM

**MEASURED, on this box, from named K0g artifacts:**
- per-arm `s/step` for all five arms (`STATUS.<case>` wall ÷ `log.solve` step count);
- `Δt_mean` **per level** (3.75e-03 s at L1, 2.59e-03 s at L2), and its
  quartile flatness;
- the completed-arm cost of `M1_c` (155.20) and `M2_c` (156.53) core-min —
  these two are **measured completion costs, not estimates**;
- the pressure-solve count per step (8.00 exactly) and DICPCG iterations/step;
- the laminar factor 0.896;
- `ExecutionTime/ClockTime` ≥ 0.9966 (the no-descheduling finding).

**PROJECTED, and labelled so everywhere it appears:** the three L2 arms'
completion costs (641.5, 652.9, 588.9 core-min). **Assumption:** `Δt` and
`s/step` hold to 60 s. Supported by measured `Δt` flatness and by the L1 arms,
which did run the full 60 s at a stable rate — **but they remain projections and
are never called measured.**

**STILL CALIBRATION ITEMS, none called measured:**
- the per-step rate **at K0h's lower concurrency** — expected to be ≤ K0g's, by
  an amount this document does not predict;
- the §7.1'' extension's cost **from a restart** (K0g never restarted; a restart
  re-reads fields and re-primes the averaging FO). The `2S` limb assumes the
  second 60 s costs the same as the first;
- the `I ≤ 8.00` instrument bound (§11 item 5 makes it measurable at K0h);
- the cost of the §4.5 assert path (bounded inside `I`).

**Estimate-vs-actual is compared at completion into `docs/COST_CALIBRATION.md`**
per rule 12's calibration bullet, per stage as well as per campaign, with
contention and waste named separately per `COMPUTE_BUDGET_CHARTER` §6.

---

## 7.9 REGISTERED PREDICTIONS (prediction-first, before any K0h compute)

**Physics predictions carried from K0g §7.9 UNCHANGED. No failure mode is
softened and no threshold moves.**

- **`P-K0h-1`** *(= K0g `P-K0g-1`, unchanged)* — the four turbulent RANS arms
  (`M1_c M1_m M2_c M2_m`) **REACH stationarity** under §7.1' by `endTime` (or by
  the one §7.1'' extension). *Failure mode named:* drift still above
  `tol_T`/`tol_U` after the extension ⇒ the RANS mean is non-stationary ⇒
  **re-registration, not a `tol` relaxation**.
- **`P-K0h-2`** *(= `P-K0g-2`, unchanged)* — the discrimination control `C_lam`
  **DOES NOT reach stationarity** ⇒ `NOT A RESULT` on stationarity grounds. The
  intended discrimination finding: turbulence closure is *required*.
- **`P-K0h-4`** *(= `P-K0g-4`, unchanged)* — resolved fluctuation
  `sqrt(max TPrime2Mean)` is **non-zero and O(0.1–1 K)** on the turbulent arms.

**Cost predictions — the successor to the falsified `P-K0g-3`:**

- **`P-K0h-3`** — **cost ratio actual/§8.2-basis within `[0.85, 1.35]` per
  arm.** *Justification of the band, from the new basis:* two of the five basis
  figures are **measured completion costs on this box** (`M1_c`, `M2_c`), and
  the other three are projections from measured `s/step` and a measured, flat
  `Δt`. The residual uncertainty is (i) concurrency 2 rather than K0g's ~5+box,
  which should move the rate **down**, and (ii) within-level `s/step` scatter,
  measured at 2.2 %. A band of −15 %/+35 % is asymmetric in the direction the
  named risk points and is **wider than the measured scatter but far narrower
  than the `[0.8, 1.6]` that `P-K0g-3` used on an assumed basis**.
  **Explicit statement of the predecessor's fate, as required:
  `P-K0g-3` predicted `[0.8, 1.6]` and was FALSIFIED at 3.158 (`M1_c`) and
  3.185 (`M2_c`) — the two arms that completed.** If `P-K0h-3` also falsifies,
  the finding is that this lab cannot yet cost a PIMPLE buoyant-cavity transient
  from a predecessor's measurements, and the successor to *that* is a mandatory
  **pilot-measured** cost basis (§11 item 3), not a wider band.
- **`P-K0h-5`** *(new, and it is the §4 prediction)* — with the §4.5 registered
  resolution in place, **`check_k0h_extraction_equivalence.py` returns 0** on
  every completed arm, and the repaired outlet path moves **no graded G-row
  value by more than 0.0** relative to a hypothetical uniform-outlet read,
  because §4.4 measured the substituted values bit-identical. *Failure mode
  named:* if the run-time assert of §4.5(b) fails on any arm, the reader
  **REFUSES** and the affected rows are **`NOT A RESULT`** — the assert is not
  downgraded to a warning.

---

## 7.5 ORDER OF OPERATIONS

`check_k0h_mesh.py` → `build_k0h.py --preflight` → **STAGE 1** `launch_k0h.sh`
→ `mark_done_k0h.py` → `check_k0h_extraction_equivalence.py` →
`analyse_k0h.py` → **STAGE-1 GATE (§8.3), read on stationarity drift alone** →
**STAGE 2** → … → **STAGE 3**. **Every comparator is hashed against its
committed blob before analysis; the grading path is fixed at the freeze
commit.**

## 7.7 THE GRADING PATH — DERIVED FROM K0g's, PINS **OWED**

**The K0g instruments are NOT edited (standing rule 6).** K0h's path is the K0g
path **carried by derivation into `k0h`-named copies**, with **exactly one
registered functional change** — §4.5, in `analyse_k0h.py` alone.

| K0h instrument | derived from (K0g, frozen, unedited) | change |
| --- | --- | --- |
| `scripts/analyse_k0h.py` | `scripts/analyse_k0g.py` (blob `409e403d`) | **§4.5 patch resolution + the `P4` plant. THE ONLY FUNCTIONAL CHANGE IN THE PATH.** |
| `scripts/build_k0h.py` | `scripts/build_k0g.py` (`4dace645`) | names/paths only |
| `scripts/check_k0h_mesh.py` | `scripts/check_k0g_mesh.py` (`39e55f2d`) | names/paths only |
| `scripts/mark_done_k0h.py` | `scripts/mark_done_k0g.py` (`387b8b82`) | names/paths only |
| `scripts/check_k0h_extraction_equivalence.py` | `scripts/check_k0g_extraction_equivalence.py` (`2506603b`) | names/paths only |
| `scripts/check_k0h_instrument_standard.py` | `scripts/check_k0g_instrument_standard.py` (`0196356a`) | names/paths only |
| `scripts/launch_k0h.sh` | `scripts/launch_k0g.sh` (`e14de416`) | **stage support (§8.3), per-arm caps (§8.4)** |
| `scripts/launch_k0h_selftest.sh` | `scripts/launch_k0g_selftest.sh` (`f7594e00`) | names/paths only |

> **`GRADING_PATH_FREEZE_COMMIT: PIN-AT-FREEZE`**
>
> **The freeze/pin section is OWED and is the SUPERVISOR'S at freeze time.** No
> git-blob sha1 is recorded in this draft, because none of these instruments
> exists yet and a pin written before the file is a pin to nothing. At freeze
> the supervisor records all eight blob sha1s here, sets
> `GRADING_PATH_FREEZE_COMMIT` to the commit whose tree holds all eight at those
> blobs, and `scripts/check_comparator_freeze.py` enforces IDENTITY, CURRENCY
> and COVERAGE on the set. **Self-hash:** this document's post-freeze integrity
> is its own committed git-blob sha1, recorded in the freeze commit message.

---

## 9. WHAT K0h DOES NOT ESTABLISH

- **It grades no row against `P`** — Blay is `NOT OBTAINED`; the time-averaged
  `G1…G8` values are **reported, never graded** against a reference.
- **It computes no Roache triple, observed order or GCI** — L1+L2 only. No
  number in a K0h record carries a discretisation bound.
- **It is not a validation of the Blay physics** — it answers the
  stationarity barrier, which K0g's budget stop left unanswered at L2.
- **It does not establish that K0g's cost model was the only thing wrong** —
  §4's extraction defect was independent, and a third defect is not excluded.
- **It does not establish that the §8.3 staging reduces per-step cost.** The
  bandwidth channel is unquantified (§8.1) and staging is claimed as a
  *direction*, never as a measured saving.
- **If the turbulent arms fail stationarity even after the §7.1'' extension**,
  the finding is genuine RANS-mean unsteadiness and the next step is a
  re-registration, **not** a `tol` relaxation.

## 10. §2ay LINKAGE — PREDECESSOR STATE MAPPING

**Predecessor `K0g`: `PENDING` (stopped at its own frozen ceiling with three
arms unfinished; comparator refused to grade a partial rung) → state (b) A DATED
SUCCESSOR (this document, K0h), a registered COST re-basing and a registered
EXTRACTION repair.** This is **NOT state (a), a capability gap**: two L1 arms
ran to completion under the transient method and met the strict completion rule
on every clause. The chain is
`K0f (steady, NOT A RESULT) → K0g (transient, budget stop + extraction refusal, PENDING) → K0h (measured cost basis, staged, repaired extraction)`,
and K0h's own ceiling (`GATE REACHED`, `P` and `G` unreached) is stated on its
face (§0.3).

---

## 11. DECISIONS THIS DRAFT DOES NOT TAKE — FOR THE HEAT-TRANSFER SUPERVISOR

**A lane does not rule on any of these, and this draft has not pre-empted them.**

1. **Whether K0h may GRADE K0g's EXISTING `M1_c`/`M2_c` FIELDS instead of
   re-running them.** This is the single highest-value open question: it is
   worth **311.73 core-min** and, more importantly, it is the fastest route to a
   demo-able result. The case for it, and it is not a lane's to accept:
   - the physics gates are **byte-carried from a pre-compute freeze**
     (`4d0046c1`) and were not chosen to fit any answer;
   - **no graded number has ever been produced** — `analyse_k0g.py` refused, so
     nothing could have been selected;
   - the arms met the strict completion rule on every clause (`DONE.M1_c`,
     `DONE.M2_c`);
   - `VERIFICATION_CHARTER` **§2d.1**'s four repair conditions appear satisfiable
     on measured evidence: **(1)** a demonstrable error, not a preference (§4.2);
     **(2)** — the load-bearing one — established by
     `check_k0g_extraction_equivalence.py`, **an instrument that grades nothing**,
     which is precisely the shape §2d.1 is cut to fit; **(3)** disclosed and
     quantified here, with `max|diff| = 0.0` (§4.4); **(4)** pre-repair values
     recorded as **REFUSED, exit 2, no graded number ever produced**.
   - **AGAINST:** `§2d.2` (v1.32) rules that gates close at **FIRST COMPUTE**,
     and K0g compute has occurred; and K0g §5's own age guard exists precisely
     to refuse inherited fields. **This draft assumes NOTHING and §8.2/§8.3 cost
     Stage 1 as a FULL RE-RUN.** If the ruling goes the other way, Stage 1's
     311.73 core-min is simply not spent.
   - **This is a joint supervisor + verification call. A lane must not decide
     it, and a decision relayed through an agent is not verification's ruling.**
2. **Whether the §4.5 extraction repair is registered at all, and in that
   form.** §4.2 concludes the registered A1.3a extraction is **mis-specified for
   a `fieldAverage` output**. A registered extraction spec is not a lane's to
   rewrite. **Routed to the supervisor as required.** This draft proposes the
   narrowest asserted form it could construct and **relaxes nothing**.
3. **Whether a short PILOT should precede the freeze** — e.g. 200 steps per
   level, ~5 core-min total, measuring `Δt_mean` and `s/step` at K0h's own
   concurrency before the cost line is frozen. K0g's whole cost failure would
   have been visible in that pilot. **A pilot is compute and this draft launches
   none;** and note `§2d.2` — feasibility compute **closes gates**, so a pilot
   must run *before* the freeze or be registered as part of it.
4. **Confirmation that no physics threshold moved.** This draft carries
   `tol_T = 0.020 K`, `tol_U = 0.005 m/s`, every band of §3, both `y⁺` windows,
   the §7.1'' single-extension discipline and the strict completion rule
   **byte-unchanged**. **Two temptations were felt and are FLAGGED RATHER THAN
   ACTED ON**, as instructed:
   - **shortening the averaging windows** from 20 s to reduce `endTime` and
     therefore cost. This would cut the campaign cost roughly in proportion.
     **NOT DONE:** each window is ≈ 15.9 τ and that length is the physical
     basis of the stationarity instrument; shortening it is relaxing the
     instrument to buy a budget.
   - **replacing `DICPCG` with `GAMG` on `p_rgh`** at the same `tolerance
     1e-10`. §8.1 measures 1159–1905 PCG sweeps per step, and this is the single
     largest cost term in the campaign; GAMG could plausibly cut it several-fold.
     **NOT DONE:** it is a registered-numerics change, it is the supervisor's,
     and it must be justified on numerical grounds with its own verification —
     **never adopted because it is cheaper.** Recorded here so the supervisor can
     take it up deliberately.
5. **Whether `I` becomes measured at K0h.** K0g's `I ≤ 7.50` was never
   separately instrumented, so it is a bound that has never been tested.
   Proposed: time each instrument invocation and record the total, so K0h's
   calibration row can state `I` as measured.
6. **Whether the 0.5S contingency is right at 2 194.99 core-min of `S`.**
   `0.5S = 1 097.50` core-min is now a large absolute figure. §8.2 argues for
   retaining it; a supervisor may prefer a smaller contingency plus the §11
   item 3 pilot. **The ceiling is a cap, not a target, and either choice is a
   cost-line decision, not a gate.**

---

## APPENDIX A — FILING AND PROVENANCE

- Filed at `docs/campaigns/F14-cooling-ladder/K0h_PREREGISTRATION.md`, matching
  the family's `<RUNG>_<PURPOSE>.md` convention and its `K0g`/`K0f` siblings
  (`FILING_CHARTER.md`; `scripts/check_filing.py`).
- Run outputs will live at `verification/runs/F14-cooling-ladder/K0h_runs/` —
  **never beside this prose**. No such directory exists at the time of this
  draft, which is the pre-compute condition §0 states.
- The K0g calibration row this draft's §8.1 shares a basis with is drafted at
  `verification/runs/F14-cooling-ladder/K0g_runs/K0g_CALIBRATION_ROW_DRAFT.txt`
  (proposed, not committed; the supervisor lands it into
  `docs/COST_CALIBRATION.md`).
- Every measured figure in §4 and §8 cites a K0g artifact still on disk:
  `verification/runs/F14-cooling-ladder/K0g_runs/{K0g_VERDICT.txt,
  CAMPAIGN_STATE.json, STATUS.*, DONE.*, <case>/log.solve,
  <case>/60/{T,TMean,U,UMean}, <case>/system/{fvSolution,blockMeshDict}}`.
- **SUBMISSIONS PARKED** (standing rule 7): nothing in or derived from this
  document is sent, filed, uploaded or registered outside this box.

## APPENDIX B — A DISAGREEMENT WITH THE FIGURES RELAYED TO THIS LANE

Recorded because a successor's cost basis must cite artifacts, not relays
(`COST_CALIBRATION.md` append rule 2):

| quantity | relayed to the lane | **read from the artifact** | artifact |
| --- | ---: | ---: | --- |
| campaign spend | 883.99 core-min | **888.12** | `CAMPAIGN_STATE.json`, `K0g_VERDICT.txt` |
| `M1_m` spend | 294.73 | **296.05** | `STATUS.M1_m` (wall 17763 s) |
| `M2_m` spend | 139.53 | **140.90** | `STATUS.M2_m` (wall 8454 s) |
| `C_lam` spend | 138.00 | **139.43** | `STATUS.C_lam` (wall 8366 s) |
| `M1_m` sim t | 27.60 s | **27.6883** | last `Time =` in `M1_m/log.solve` |
| `M2_m` sim t | 12.83 s | **12.9489** | last `Time =` in `M2_m/log.solve` |
| `C_lam` sim t | 14.09 s | **14.2073** | last `Time =` in `C_lam/log.solve` |

Reading: the relayed figures were taken at the **03:47Z stop decision**; STATUS
records wall to **signal delivery**, ~79–86 s later per arm. The artifact
figures are the ones this document uses throughout. **The campaign remains
WITHIN the 915.58 ceiling on either reading** (headroom 27.46 core-min on the
artifact figure), so no verdict or budget conclusion changes — but the cost
basis does, and it is stated rather than smoothed.

**A second and larger disagreement is on ATTRIBUTION, and §8.1 carries it:** the
brief named `Δt_mean` as the root cause with contention secondary. Measured,
**`Δt` is the SMALLER of two multiplicative axes at both levels** (×1.33 L1,
×1.93 L2, against a rate axis of ×2.37 and ×3.45), and **contention's
descheduling channel is measurably ≈ 0** (`ExecutionTime/ClockTime` ≥ 0.9966 on
all five arms) so it is not named as a separate figure at all. K0h is costed on
the measured decomposition, not on the relayed one.

---

# AMENDMENT 1 — 2026-09-10. PRE-COMPUTE. THE EXTRACTION DEFECT IS CLOSED AND A SECOND, INDEPENDENT BLOCKER IS FOUND.

> **Written by a heat-transfer lab-lane at ZERO SOLVER COMPUTE. THIS DOCUMENT
> IS STILL NOT FROZEN.** The lane does not freeze it, does not set its gates,
> does not choose its arm set and does not pin its grading path. Those are the
> supervisor's, and §A1.8 lists them.

## A1.0 THE AMENDMENT'S CONDITION, AND HOW IT WAS CHECKED (standing rule 2)

Standing rule 2 permits amendments **before first compute** and requires each
to **state its condition and how it was checked, naming the run directory that
does not exist.** Discharged explicitly, not by assertion:

| | |
| --- | --- |
| **THE CONDITION** | No K0h compute has occurred. Operationally: **`verification/runs/F14-cooling-ladder/K0h_runs/` DOES NOT EXIST** — that is the named directory, and it is named because it is the one directory whose existence would close the gates. |
| **HOW IT WAS CHECKED** | Its absence was read **from disk**, not inferred from a record: `ls -d verification/runs/F14-cooling-ladder/K0h_runs` returns *"No such file or directory"*. The whole of `verification/runs/F14-cooling-ladder/` was enumerated and holds 25 entries, of which none is `K0h_runs`. Independently, `git ls-files | grep -i k0h` returns exactly one path — this document — so no K0h run artifact is tracked either. |
| **WHAT WAS RUN, AND WHY IT IS NOT COMPUTE UNDER THIS DOCUMENT** | Grading-path **instruments only**, on **K0g's** completed arms and on fixtures: **0.317 core-min measured, no solver invoked, no K0h case directory created, no field written anywhere under `verification/runs/`.** `VERIFICATION_CHARTER` §2d.2's "first compute" is the compute **this registration authorises**; reading a predecessor's fields with an instrument that grades nothing is the §2d.1 shape, and §A1.8 item 1 keeps the §11 item 1 ruling untouched. |
| **WHAT THIS AMENDMENT MAY THEREFORE DO** | Everything, because nothing is frozen. **What it nevertheless DOES NOT do:** it moves **no** band, **no** `tol`, **no** `y⁺` window, **no** verdict ladder and **no** completion clause. Every such figure of §3, §7.1', §7.2, §7.3 stands **byte-unchanged**. The changes are to the **cost line**, to the **stop machinery**, and to what the rung **honestly claims it can buy**. |

**Nothing above is struck by rewriting.** Where the body is now contradicted,
§A1.9 names the passage and marks it **SUPERSEDED BY AMENDMENT 1**; the
original text stays where it is, readable.

---

## A1.1 THE EXTRACTION DEFECT IS CLOSED — DEMONSTRATED BEFORE FREEZE, ON THE TWO ARMS THAT COMPLETED

**This is the single most important line in this amendment.** §0.2 named the
extraction refusal as the blocker a re-cost alone would have walked straight
back into: `311.73` core-min reached strict completion and produced **no
graded number**. That is now demonstrated closed, **before** the freeze,
**on the actual arms**, and the full record with every number is at

> **`verification/runs/F14-cooling-ladder/K0g_runs/K0h_PREFREEZE_EXTRACTION_DEMONSTRATION.txt`**

filed under the case directory it reads (never in a scratch path — L-186).
The four results that matter:

| # | what was driven | outcome |
| --- | --- | --- |
| **1** | the **FROZEN** `analyse_k0g.py` reader, on `M1_c/60/{TMean,UMean}` and `M2_c/60/{TMean,UMean}` | **exit 2, four times.** The defect reproduced on demand. `analyse_k0g.py` was **not edited** (rule 6; its blob is still `409e403d`, byte-identical to HEAD). |
| **2** | `analyse_k0h.py`'s reader on the **same four files** | **resolves all four.** `outlet` → `None`, the *same* zeroGradient sentinel; 7 patches each; and the §4.5 path is confirmed **exercised** — the outlet really does carry a `nonuniform` list on disk, so the repair is not bypassed. |
| **3** | `check_k0h_extraction_equivalence.py --case M1_c --case M2_c` — **the instrument whose K0g ancestor produced the refusal quoted in §0.2, and, per `VERIFICATION_CHARTER` §2d.1(2), AN INSTRUMENT THAT GRADES NOTHING** | **rc = 0.** OpenFOAM's own `postProcess -func sample` versus the in-comparator reader at the 2081 registered points: worst \|diff\| **4.114105e-08 K** against the **2.00e-05 K** criterion, and **1.822046e-09 m/s** against **5.70e-07 m/s** — agreement three orders inside the criterion on **all eight** set×field×arm combinations. |
| **4** | the production path `load_case_fields` → `extract_rows`, both registered schemes, both arms | **all ten rows produced, no refusal anywhere.** e.g. `G6` = 167.08233530137952 (`M1_c`), 199.56294869083385 (`M2_c`), identical under both schemes; `G1` a full 2081-point profile; `S1` structurally identical under both schemes. |

**`P-K0h-5` is therefore demonstrated on measured evidence rather than
predicted — and it is left standing as a prediction anyway**, because the
demonstration is on L1 arms of a predecessor and the prediction is over
K0h's own arms at K0h's own `endTime`.

> **THE DEMONSTRATION IS AN INSTRUMENT DEMONSTRATION AND NOTHING MORE.
> NO GATE WAS EVALUATED, NO BAND APPLIED, NO ROW GRADED, NO VERDICT
> ASSIGNED.** The §11 item 1 question — whether K0h may *grade* these
> existing fields instead of re-running them — is **untouched**, and §A1.4
> continues to cost every arm as a **full re-run**.

---

## A1.2 THE PLANTED-ZERO CONTROLS, AND THE SELFTESTS, DRIVEN IN BOTH DIRECTIONS

Standing rule 3 is discharged on **every** reader that can return a zero, and
the control is shown able to **fire** as well as to stay quiet — a probe never
shown able to fire is not evidence.

**On the real arm fields** (into copies; the fields on disk are never
modified), all four plants on **both** arms:

| plant | channel | planted → seen | outcome |
| --- | --- | --- | --- |
| `P1` | `read_scalar_field` (`TMean`) | 1.234e-03 → 1.234e-03 | **SEEN** |
| `P2` | `read_vector_field`, x-component (`UMean`) | 1.234e-03 → 1.234e-03 | **SEEN** (a scalar plant does not exercise the vector parser) |
| `P3` | negative control, 0.0 onto a 0.0 background | 0.0 → 0.0 | **NOT DISTINGUISHABLE — correct.** A negative control that fired would mean `P1`/`P2` prove nothing. |
| `P4` | **the §4.5 repaired boundary path**, `read_boundary_values`+`_vertex_value` | 1.234e-03 → **exactly** 1.234e-03 | **SEEN**, on form `fieldAverage calculated+nonuniform` — i.e. on the channel §4.5 *added*, which would otherwise be the one channel in this comparator with no planted control |

**Selftest results, all runs rc = 0:**

| instrument | result |
| --- | --- |
| `scripts/analyse_k0h.py --selftest` | **95 OK, 0 FAIL.** Includes §4.5 driven **both ways**: a bit-exact list resolves; **one face off by ONE ULP REFUSES**; the same values in the **wrong face order** REFUSE; a **short** list REFUSES; a `fixedValue` base field REFUSES (condition (a) load-bearing alone); an **absent** base field REFUSES rather than reading as satisfied; a non-`Mean` field REFUSES; a non-`calculated` patch REFUSES. And `P4` driven both ways: a boundary reader that cannot place the patch REFUSES, and a boundary path **deaf to the plant** REFUSES. |
| `scripts/check_k0h_extraction_equivalence.py --selftest` | **5 OK, 0 FAIL.** Fires at **1.01×** the criterion (2.020e-05), stays quiet at **0.99×** (1.980e-05). The criterion is bracketed, not merely met. |
| `scripts/mark_done_k0h.py --selftest` | **all clauses both ways.** The **age guard** fires on a stale gzipped case and stays quiet on a clean one; clause 7 fires when `0` exists and when a numeric time dir exists; an **absent STATUS REFUSES (exit 2) rather than inferring rc=0**. |
| `scripts/check_k0h_mesh.py --selftest` | all conditions both ways; the registered-table check fires on a table that does not scale by 1.40. |
| `scripts/check_k0h_instrument_standard.py` | **CLEAN.** No registered refusal is carried by an `assert`; every refusal fires **identically under `python3 -O`**. |
| `scripts/launch_k0h_selftest.sh` | **13 passed, 0 failed.** `ranks != 1` refuses; an unreachable solver refuses and **writes NO STATUS** (never started ≠ ran and failed); a missing environment file refuses rather than launching blind. |
| `scripts/orchestrate_k0h.py --selftest` | **30 passed, 0 failed** — see §A1.5. |

---

## A1.3 THE SECOND, INDEPENDENT BLOCKER: **BOTH COMPLETED K0g ARMS ARE TWO ORDERS OF MAGNITUDE FROM STATIONARITY AT THE REGISTERED `endTime`**

This was **not** the finding the lane was sent for. It surfaced from the same
zero-compute pass and it is reported because a registration that ignores it
spends its whole budget and produces `NOT A RESULT` — **the K0g failure mode
arriving one layer later.**

### A1.3a MEASURED, not projected

The §7.1' stationarity instrument, on the two arms that met the strict
completion rule at `endTime = 60 s`:

| arm | `max_cell |TMean(avg2) − TMean(avg1)|` | `tol_T` | ratio | cells over `tol_T` |
| --- | ---: | ---: | ---: | ---: |
| `M1_c` | **6.133684 K** | 0.020 K | **×306.7** | 24 696 / 25 600 = **96.47 %** |
| `M2_c` | **6.314012 K** | 0.020 K | **×315.7** | 24 815 / 25 600 = **96.93 %** |

| arm | `max |UMean.x|` drift | `max |UMean.y|` drift | `tol_U` | cells over (x / y) |
| --- | ---: | ---: | ---: | ---: |
| `M1_c` | 0.109011 m/s | 0.153332 m/s | 0.005 m/s | 65.13 % / 68.07 % |
| `M2_c` | 0.101422 m/s | 0.125108 m/s | 0.005 m/s | 61.79 % / 57.40 % |

**This is not a localised outlier.** `M1_c`'s drift distribution is median
**0.366064**, p90 **1.169696**, p99 **3.552365**, mean **0.555761 K** — the
*median* cell is 18× over tolerance. The maximum sits at cell (45, 5),
`x = 0.1264 m`, `y = 0.0104 m`: **the first cell row above the heated floor**,
a thermal boundary-layer/bulk-development region, **not** a chaotic jet.

**The cavity is still warming at 60 s.** Volume-mean instantaneous `T`:
`M1_c` 289.187662 → 290.062133 (+0.874471) → 290.376044 (+0.313911) K at
t = 20, 40, 60 s; `M2_c` 289.058599 → 290.380985 (+1.322385) → 290.611942
(+0.230957) K.

**Also measured, so no successor re-derives it:** the `TMean` in the `20`
directory is **DEGENERATE** — `max |TMean(20) − T(20)| = 0.0` exactly on both
arms. Under `timeStart 20` with `restartOnOutput true` the t = 20 write is a
one-step average carrying no window. **Only `40` and `60` are windows.**

### A1.3b PROJECTED — and labelled a projection wherever it appears

Per-cell decay ratio `|T(60)−T(40)| / |T(40)−T(20)|`, over cells whose first
increment exceeds 1e-6 K:

| arm | median ratio | p90 ratio | n |
| --- | ---: | ---: | ---: |
| `M1_c` | 0.4617 | **2.0340** | 25 426 |
| `M2_c` | 0.2404 | 0.9486 | 25 443 |

Applying the **median** ratio per 20 s window to the measured max-cell drift:

| arm | further 20 s windows needed | implied `endTime` | **after the ONE registered §7.1'' extension (`endTime` 120 s, three windows)** |
| --- | ---: | ---: | --- |
| `M1_c` | 7.41 | **≈ 220 s** | projected drift **0.6038 K — OVER `tol_T` by ×30.2** |
| `M2_c` | 4.04 | **≈ 160 s** | projected drift **0.0877 K — OVER `tol_T` by ×4.4** |

**At the p90 ratio `M1_c`'s drift does not decay at all** (ratio > 1) and **no
`endTime` reaches the tolerance.**

**HONEST LIMITS, stated rather than buried.** This is a single-exponential
model fitted to **two** instantaneous-field increments and then applied to a
**max-cell time-average** metric. The max-cell metric's decay ratio need not
equal the median per-cell ratio, and the median-to-p90 spread is wide enough
to change the conclusion's *shape* though not its *sign*. **`≈ 220 s` is a
projection and is never called a measurement.** What is measured is §A1.3a.

### A1.3c THE CONSEQUENCE FOR THE REGISTRATION, STATED WITHOUT SOFTENING

**`P-K0h-1` — the prediction that the four turbulent RANS arms reach
stationarity by `endTime` or by the one extension — is contradicted at L1 by
measured evidence, before any K0h arm runs.** Its own named failure mode
already governs: *"drift still above `tol_T`/`tol_U` after the extension ⇒
the RANS mean is non-stationary ⇒ **re-registration, not a `tol`
relaxation**."*

**`tol_T` STAYS AT 0.020 K AND `tol_U` AT 0.005 m/s.** Widening either to
admit these arms is the one move this finding must not be allowed to
motivate, and §11 item 4 already flagged the temptation. **Not done, and not
proposed.**

**The K0g stop is still a budget outcome and still state (b).** §0.1 stands:
nothing here says the lab cannot compute this flow to a stationary state. It
says the **registered `endTime` was ~3.7× too short**, which is the same
class of error as the cost model — a pre-compute estimate the artifacts now
correct — and it is correctable by a registration, not by a capability.

---

## A1.4 THE COST LINE, RE-STATED **PER LEVEL** WITH THE `endTime` AXIS EXPOSED — AND WHAT THE CEILING HONESTLY BUYS

### A1.4a THE MEASURED INPUTS, PER LEVEL (standing rule 12)

Independently re-read from the artifacts, **not carried from §8**: `wall` from
`STATUS.<arm>`, step count from `grep -c '^Time = ' <arm>/log.solve`, last
`Time` from the same log, cell count from `log.checkMesh`. **Every figure of
§8.1/§8.2 reproduced to the digit**, so §8's basis is confirmed rather than
replaced.

| level | cells | **`Δt_mean` measured** | spread across its arms | **`s/cell/step` measured** | spread |
| --- | ---: | ---: | ---: | ---: | ---: |
| **L1** | 25 600 | **3.753765e-03 s** | 3.747190e-03 … 3.760341e-03 (**0.35 %**) | **2.285513e-05 s** | 2.271734e-05 … 2.299292e-05 |
| **L2** | 50 176 | **2.592040e-03 s** | 2.585025e-03 … 2.601225e-03 (**0.62 %**) | **3.243225e-05 s** | 3.033717e-05 … 3.384631e-05 |

**Both are stated PER LEVEL because K0g proved one global figure cannot
express two levels.** The transient overhead against the SIMPLE
per-cell-iteration rate the registered `4.8e-6` was built on
(`4.8e-6 / 1.5 = 3.2e-6`) measures **×3.55 at L1** and **×5.17 at L2** —
against a registered **×1.5**. Within-level spread is **0.35 %/0.62 %** on
`Δt`; **between** levels it is **44.8 %**. A single registered figure is
therefore wrong by two orders more than the scatter it would have to cover,
which is precisely why §8.1's two-axis decomposition is retained and why this
amendment refuses to collapse it.

### A1.4b THE ARITHMETIC, OPEN FOR CHECKING

```
  cost(arm, E) = ( E / Δt_mean(arm) ) × s_per_step(arm) / 60      [core-min, ranks = 1]
  s_per_step(arm) = wall_s / steps                                [MEASURED, K0g log.solve]
```

| arm | lvl | `s/step` | `Δt_arm` | **E=60 s** | **E=120 s** | **E=160 s** | **E=220 s** | **E=260 s** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M1_c` | L1 | 0.581564 | 3.7472e-03 | **155.20** | 310.40 | 413.87 | 569.07 | 672.53 |
| `M2_c` | L1 | 0.588619 | 3.7603e-03 | **156.53** | 313.07 | 417.42 | 573.96 | 678.31 |
| `M1_m` | L2 | 1.661491 | 2.5899e-03 | 641.53 | 1 283.07 | 1 710.76 | 2 352.29 | 2 779.98 |
| `M2_m` | L2 | 1.698272 | 2.6012e-03 | 652.87 | 1 305.75 | 1 741.00 | 2 393.87 | 2 829.12 |
| `C_lam` | L2 | 1.522198 | 2.5850e-03 | 588.85 | 1 177.70 | 1 570.27 | 2 159.12 | 2 551.69 |
| **L1 pair** | | | | **311.73** | 623.47 | 831.29 | 1 143.02 | **1 350.84** |
| **L2 trio** | | | | 1 883.26 | 3 766.52 | 5 022.03 | 6 905.29 | 8 160.80 |
| **`S` = five arms** | | | | **2 194.99** | **4 389.99** | 5 853.32 | **8 048.31** | **9 511.64** |

Worked, `M1_c` at E = 260 s: `260 / 3.7472e-03 = 69 385.4` steps
× `0.581564 s = 40 351.7 s` = **672.53 core-min**; and
`155.20 × (260/60) = 672.5` — the two routes agree, so the linearity in `E` is
explicit rather than assumed. The **only two figures in the table that are
MEASURED COMPLETION COSTS** are `155.20` and `156.53`; every other cell is a
**projection** linear in `E` resting on the measured quartile-flatness of `Δt`.

### A1.4c **THE DRAFTED §8.2 CEILING OF 5 495.48 core-min CANNOT BUY FIVE STATIONARY ARMS. SAID PLAINLY.**

| `endTime` | five arms need `S + I` | against CEILING 5 495.48 | |
| ---: | ---: | --- | ---: |
| 60 s | 2 202.99 | **FITS** | headroom +3 292.49 |
| 120 s | 4 397.99 | **FITS** | headroom +1 097.49 |
| 160 s | 5 861.32 | **DOES NOT FIT** | **−365.84** |
| 220 s | 8 056.31 | **DOES NOT FIT** | **−2 560.83** |
| 260 s | 9 519.64 | **DOES NOT FIT** | **−4 024.16** |

> **The drafted ceiling buys five arms to exactly `endTime = 150.0 s`.**
> §A1.3b projects the required `endTime` at **≈ 220 s** (`M1_c`) and **≈ 160 s**
> (`M2_c`) at the *median* decay, and at the p90 decay **`M1_c` never
> converges at all**. **The ceiling is therefore refuted by arithmetic for the
> outcome the rung exists to produce.** It is *not* refuted for strict
> completion at 60 s — 2 202.99 fits with room — but an arm that completes and
> is not stationary is **`NOT A RESULT`** under §7.1', and buying five of those
> for 2 195–4 390 core-min is **K0g repeated**. Item (2) of the lane's brief
> said not to register a ceiling arithmetic already refutes. It is not
> registered.

**DOLLARS ARE NOT THE BINDING CONSTRAINT ANYWHERE, AND SAYING SO IS PART OF
THE HONEST ANSWER.** At the owner-reported **$0.0513/core-h**
(`COMPUTE_BUDGET_CHARTER` §5 — **DERIVED, NOT MEASURED**, the box cannot read
its own billing): five arms at 260 s = 9 511.64 core-min = 158.53 core-h =
**$8.13**; with 1.35× caps, **$10.99**. All inside the $25 per-run
pre-authorisation — and **a blanket is not a per-item read (rule 9); this is
that read.** **The binding constraint is CALENDAR:** 9 511.64 core-min at
`ranks = 1`, concurrency 2, is **≈ 79 h wall ≈ 3.3 days**.

### A1.4d THE THREE OPTIONS, AND THE LANE'S PROPOSAL — **FEWER ARMS**

| | arms | `endTime` | `S` | caps at 1.35× | **ceiling needed** | \$ derived | calendar @ conc 2 | verdict on it |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **A** | all five | 260 s | 9 511.64 | 12 840.72 | **12 848.72** | $10.99 | ≈ 107 h (4.5 d) | Affordable in dollars, expensive in calendar, and it registers `endTime` **on a projection** (§A1.3b) — the same species of pre-compute guess that produced §8.1. |
| **B** | **the L1 pair only** | 260 s | **1 350.84** | 1 823.64 | **1 835.00** | **$1.566** | **≈ 15.2 h** | **PROPOSED.** L1 is 14 % of the five-arm cost and answers the barrier question. It turns the required `endTime` from a **projection into a measurement**, which is exactly the number a successor needs to cost L2 honestly. |
| **C** | all five | 60 s, as drafted | 2 194.99 | — | 5 495.48 as drafted | $4.70 | ≈ 23 h | **REFUTED by §A1.3a.** Every arm would complete and every row would be `NOT A RESULT` on the stationarity clause. This is the K0g outcome bought a second time. |

**Why B and not A, stated as an argument and not a preference.** §8.3 already
established the principle — *"L1 costs 14 % of the campaign and answers the
barrier question before the expensive 88 % is committed"* — and §A1.3a is that
argument's vindication: the barrier question **was** the binding one, and K0g
never got to ask it. Option A commits 12 848.72 core-min against an `endTime`
that is a **projection from two increments**; if 260 s is short, A spends
4.5 days and returns `NOT A RESULT` on five arms. B spends 15 hours to
**measure** the stationarity time at L1, and its own worst case is still a
**finding** — genuine RANS-mean unsteadiness at L1 — rather than a
`NOT A RESULT`, *provided* the supervisor makes the stationarity determination
the rung's graded object (§A1.8 item 3, **not a lane's call**).

**`C_lam` IS NOT BEING QUIETLY DROPPED.** §8.3 argued it must not be, and that
argument is not withdrawn: it is the registered discrimination control for
`P-K0h-2`. Under option B it is **deferred and named**, not dropped — the
manifest's `deferred_not_authorised` block carries `M1_m`, `M2_m` and `C_lam`
by name with the reason, so a successor inherits an obligation and not a
silence. **Whether that deferral is acceptable is §A1.8 item 2.**

### A1.4e `cost_basis` — WHAT MOVED FROM CALIBRATION-ITEM TO MEASURED

**Now MEASURED, where §8.5 had a bound:** the instrument spend `I`. §11 item 5
asked for it; the whole pre-freeze pass is timed at **0.317 core-min**, i.e.
**4.0 % of the `I ≤ 8.00` bound**, itemised per instrument in the
demonstration record. **The bound is RETAINED at 8.00** because the graded
pass over two 260 s arms has not been timed, and a bound that has been tested
once at 4 % is still a bound.

**Still calibration items, none called measured:** the per-step rate at K0h's
own concurrency; the §7.1'' extension's cost **from a restart** (K0g never
restarted); the cost of the §4.5 assert path. **Estimate-versus-actual lands
in `docs/COST_CALIBRATION.md`** per stage and per campaign at completion, with
contention and waste named separately (`COMPUTE_BUDGET_CHARTER` §6) — and
**`P-K0h-3`'s ratio is computed against the §A1.4b basis at the `endTime`
actually registered**, not against §8.2's 60 s column.

---

## A1.5 THE PRE-REGISTERED EARLY-TERMINATION / CEILING-STOP RULE, AND THE INSTRUMENT THAT CAN FAIL IT

Standing rule 12: **an overrun stops the run; it does not get a new budget.**
§8.3/§8.4 registered stages and per-arm caps as *prose*. **K0g had a ceiling
and a cap in prose too, and still ended in a supervisor-executed SIGTERM on
three arms in flight.** A rule nobody can fail is a preference
(`FILING_CHARTER` §1), so the rule is now carried by an instrument:

> **`scripts/orchestrate_k0h.py`**, reading
> **`verification/campaign/K0h_STAGE_MANIFEST.json`**. **No gate, threshold,
> band or label lives in the script** — the ceiling, the stages and the caps
> are in the manifest, whose blob is pinned at the freeze. The script cannot
> be used to move a number.

**THE K0g MECHANISM, NAMED FROM ITS OWN SOURCE** so the repair is aimed at a
measured cause. `K0g_runs/orchestrate_k0g.py:113-118` computed
`proj = completed_coremin() + running_pt + pt` where `running_pt` sums each
in-flight arm's **POINT ESTIMATE `p`**, not its **CAP `t`**. The point
estimate was low by **×3.16–3.19** on the two arms that completed, so **the
guard that protected the ceiling was itself computed from the mis-costed
figure the ceiling existed to contain.** It could not fire before the breach,
because its own arithmetic denied the breach was coming.

**THE THREE REGISTERED RULES:**

| | rule | why |
| --- | --- | --- |
| **R1** | **A running arm is charged its CAP, never its estimate.** | A cap **bounds** an arm; an estimate is the figure that was wrong. |
| **R2** | **The stage gate is PRE-LAUNCH ONLY.** A stage launches iff `charged + Σ(caps of its unlaunched arms) ≤ CEILING`. Otherwise **BLOCKED**, its arms **named UNRUN**, and the run **STOPS** — recorded in `CEILING_STOP.txt`. | K0g's ceiling bit while three arms were in flight and killed them. A stage that cannot be afforded is **never started**, so nothing is ever killed partway. |
| **R3** | **Nothing in flight is ever signalled.** No `SIGTERM`, `SIGKILL`, `pkill`, `os.kill`, `.terminate()`. An arm is stopped **only** by its own `timeout` cap inside `launch_k0h.sh` (**rc 124, a CAP-STOP**). | This is the K0g stop's *shape* forbidden outright. |

**AND A FOURTH, WHICH IS THE DIRECT ANSWER TO §A1.4c:** the manifest loader
**REFUSES (exit 2) any manifest whose caps sum above its own ceiling**, with
the message *"The ceiling cannot buy the arms it authorises even at the caps
IT registers; the arithmetic refutes it before any solver runs."* **A ceiling
that arithmetic refutes can no longer be registered at all** — it is rejected
by the instrument, not by a reader's diligence. It also refuses a cap **below
its own arm's basis**, a duplicated arm, `ranks ≠ 1`, a foreign rung, and a
`STATUS` with no `wall` (a missing measurement is **not** a zero cost).

**`--selftest`: 30 passed, 0 failed, every rule driven BOTH WAYS.** The two
that matter most:

- **R3 is asserted on the file's own source**, scoped to the production region
  by a sentinel, with the region asserted **non-trivial** (275 executable
  lines) — **and the same scan is shown to FIRE on a planted
  `os.kill(..., SIGTERM)`.** A scan never shown able to fire is not evidence.
- **R1 and the K0g arithmetic are shown to DIFFER IN OUTCOME on one concrete
  tree**: an arm done at 300.00 against a 250.00 cap plus one in flight ⇒ R1
  charges **550.00**, needs 1 000.00, reaches 1 550.00 > 1 500.00 → **BLOCKED**;
  the K0g arithmetic charges **400.00**, reaches 1 400.00 ≤ 1 500.00 →
  **LAUNCHES the stage R1 blocks.** The repair is measured, not asserted.

**AND THE HONEST LIMIT OF ALL OF THIS, STATED BECAUSE IT IS EASY TO OVERSELL.**
Once the closure check passes, a campaign in which **every arm respects its
cap cannot breach the ceiling**, and R2 can then **never fire**. That is the
point: the K0g failure is **designed out at registration**, not caught at
runtime. R1 is **defence in depth** for the one channel closure cannot bound —
an arm whose *measured* spend exceeds its cap, reachable because `STATUS`
`wall` covers `blockMesh` + `checkMesh` + solver while the cap converts only
the solver `timeout`. **R2 is a backstop, and it is not claimed as the primary
protection.**

**No `--auto`.** Each stage is named on the command line, so **no budget is
ever committed by this script deciding a gate passed.** The §8.3 stage gate is
a stationarity reading and it is the **supervisor's**.

---

## A1.6 RULE 4 AND RULE 5 — CARRIED, AND CONFIRMED FIRING

**Standing rule 4, the strict completion rule with the age guard**, is carried
**byte-unchanged** from §7.2 and is enforced by `mark_done_k0h.py`. Confirmed
by selftest, both directions: five authorised arms (not ten); clause 7 fires
when `0` or a numeric time dir already exists and stays quiet otherwise; the
**age guard fires on a stale gzipped case** — *"time 60 holds fields OLDER
than 0/T (T,U,p_rgh,alphat,phi,TMean,UMean) — not written by this run"* — and
stays quiet on a clean one; an **absent `STATUS` REFUSES (exit 2)** rather
than inferring `rc = 0`; an unregistered closure REFUSES. **`phi` is in the
enforced field set** (Sanaa 2026-09-06).

**Standing rule 5, Roache triple gating**, is carried at `Fs = 1.25` with the
ordering intact — any level not converged/plateaued ⇒ `NOT A RESULT`; a
`DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` triple ⇒ `NOT A RESULT` with
value and both triples printed beside it; `CONVERGING` ⇒ `PASS` inside the
pre-registered band else `GATE FAIL`. The comparator's selftest confirms the
monotone ladder and, in both directions, that **the gate may turn `GATE FAIL`
into `NOT A RESULT` and may NEVER turn `NOT A RESULT` into `GATE FAIL`.**

**AND THE THING THAT MUST BE SAID ON THIS DOCUMENT'S FACE:** the triple is
**UNREACHABLE**, as §7.3 and §0.3 already state, and under option B it is
unreachable **more** strongly — a single level cannot form a triple at all.
**No K0h number carries a discretisation bound**, and no GCI is quoted.
`§0.3`'s ceiling stands unchanged: **the best verdict K0h can reach is
`GATE REACHED`**, naming both `P` (Blay `NOT OBTAINED`) and `G` (no triple)
unreached.

---

## A1.7 THE GRADING PATH — BLOB SHA1s RECORDED, **PIN STILL OWED TO THE SUPERVISOR**

**Standing rule 6 held: every one of the eight K0g ancestors is
byte-identical to HEAD**, verified by `git rev-parse HEAD:<path>` against
`git hash-object <path>` — `409e403d`, `4dace645`, `39e55f2d`, `387b8b82`,
`2506603b`, `0196356a`, `e14de416`, `f7594e00`. **No K0g instrument was
edited.**

**Worktree blob sha1s as demonstrated. THESE ARE RECORDED, NOT PINNED.**

| K0h artifact | blob sha1 | derived from (K0g, frozen, unedited) |
| --- | --- | --- |
| `scripts/analyse_k0h.py` | `3f77477570c80f8be99206825351aff40bbcbd17` | `analyse_k0g.py` `409e403d` — **§4.5 + `P4`, the ONLY functional change** |
| `scripts/build_k0h.py` | `726216ed7e3425ab1cbe01451db9672163d4b800` | `build_k0g.py` `4dace645` |
| `scripts/check_k0h_mesh.py` | `d5d7066ccaaa5c65cb35a045a19e440c5a6c686a` | `check_k0g_mesh.py` `39e55f2d` |
| `scripts/mark_done_k0h.py` | `5f33e94ea15f0ce5e0b095ad7c8dfbc6ef040e14` | `mark_done_k0g.py` `387b8b82` |
| `scripts/check_k0h_extraction_equivalence.py` | `e8f992e7b1eb6ab7fb025029dcfeccd2982b7919` | `check_k0g_extraction_equivalence.py` `2506603b` |
| `scripts/check_k0h_instrument_standard.py` | `77dfb0613c632b4ad050662cbbfaf552c0008ba1` | `check_k0g_instrument_standard.py` `0196356a` |
| `scripts/launch_k0h.sh` | `7c4280bea1bc87bd7b463eb44ffa0fdddae9fc1e` | `launch_k0g.sh` `e14de416` |
| `scripts/launch_k0h_selftest.sh` | `931faf8b382de9d891f63f86b3236534e236f574` | `launch_k0g_selftest.sh` `f7594e00` |
| **`scripts/orchestrate_k0h.py`** | `8c71f840c97e00464f9df88c1a32c755f3a97a1c` | **NEW** (§A1.5); K0g's `orchestrate_k0g.py` is cited as the defect, not derived from |
| **`verification/campaign/K0h_STAGE_MANIFEST.json`** | `8cd45bc9267ee6bba3f5c59750797bbc51f56501` | **NEW** — **carries the ceiling and the caps, so it MUST be pinned with the path** |
| `…/K0g_runs/K0h_PREFREEZE_EXTRACTION_DEMONSTRATION.txt` | `463ba6a8a5f0a6999e55f32fa37ed45a02a9cef6` | the §A1.1 evidence record |

> **`GRADING_PATH_FREEZE_COMMIT: PIN-AT-FREEZE`** — still owed, and still the
> supervisor's. **The freeze set is now ELEVEN paths, not eight:** the eight
> of §7.7, plus `orchestrate_k0h.py`, plus **`K0h_STAGE_MANIFEST.json`**, plus
> the demonstration record. **The manifest is not optional to pin** — it holds
> the ceiling and every cap, so a freeze that pins the code and leaves the
> manifest loose leaves the numbers loose. `scripts/check_comparator_freeze.py`
> enforces IDENTITY, CURRENCY and COVERAGE over the set; **COVERAGE is the
> clause that must be updated from 8 to 11.**
>
> **Every sha above will change if any file is touched after this amendment
> is written.** They are recorded so the supervisor can verify that the file
> read as a diff **is** the file demonstrated; they are **not** a pin, and the
> lane sets no pin.

---

## A1.8 WHAT THIS AMENDMENT DOES **NOT** DECIDE — FOR THE HEAT-TRANSFER SUPERVISOR

§11's six items **all stand open**; a lane has not ruled on any of them.
§A1.1's demonstration **strengthens the evidence** under §11 item 1 without
touching the ruling, and §A1.3 adds these:

1. **§11 item 1 is UNCHANGED and is now worth much more than 311.73 core-min.**
   §A1.1 establishes on measured evidence that the §2d.1(2) instrument — the
   one that grades nothing — **now returns 0** on both completed arms, and
   §A1.1(1) establishes that the pre-repair state was **REFUSED, exit 2, no
   graded number ever produced** (§2d.1(4)). **But §A1.3a also shows those
   arms are not stationary at 60 s**, so grading them would grade a
   non-stationary state — which the §7.1' clause refuses anyway. **The
   material question has therefore shifted:** it is no longer "may K0h grade
   K0g's fields" but **"may K0h RESTART from K0g's 60 s fields"**, which
   would save the entire 60 s prefix of every arm — **311.73 core-min at L1
   alone, and 1 883.26 at L2**. That is a **larger** §2d.1 question than §11
   item 1 posed, it runs straight into §5's age guard (which exists precisely
   to refuse inherited fields), and it is **jointly the supervisor's and
   verification's. A lane must not decide it, and a decision relayed through
   an agent is not verification's ruling.** §A1.4 assumes **NO** restart and
   costs every arm from `t = 0`.
2. **The arm set and the ceiling — option A, B or C of §A1.4d.** The lane
   **proposes B** and has written the manifest for B. **An arm set is not a
   lane's to choose**, and if the supervisor rules A or another shape, the
   manifest is rewritten **before** the freeze (legal: no `K0h_runs` exists)
   and the orchestrator's closure check re-verified.
3. **Whether the STATIONARITY DETERMINATION becomes the rung's graded object.**
   Under option B the honest product is a **measured stationarity time at
   L1** — which would make a non-stationary result a **finding** rather than
   a `NOT A RESULT`. **That is a change to what the rung grades, i.e. a GATE
   change, and it is reserved.** This amendment does **not** make it: as
   written, a non-stationary arm is still `NOT A RESULT` under §7.1'.
4. **`endTime`.** §A1.3b projects ≈ 220 s (`M1_c`) / ≈ 160 s (`M2_c`) at the
   median decay and **never** at `M1_c`'s p90. The manifest proposes **260 s**.
   **`endTime` is a registered physics parameter and it is the supervisor's**;
   the lane records that any value chosen now rests on a **projection from two
   increments**, which is the same species of pre-compute guess that produced
   §8.1's ×3.5 miss.
5. **Whether §7.1''s single-extension discipline survives contact with
   §A1.3b.** §7.1'' authorises **ONE** extension and says *"a second is not
   authorised"*. §A1.3b projects that even the one extension leaves `M1_c`
   **×30.2 over `tol_T`**. Either `endTime` is registered long enough at the
   outset (the manifest's approach) **or** §7.1''s discipline is
   re-registered. **Both are the supervisor's; the lane relaxes neither.**
6. **Whether the §4.5 repair is registered at all** — §11 item 2, unchanged
   and still open. §A1.1 shows it **works**; it does not show it is
   **authorised**. A registered extraction spec is not a lane's to rewrite.
7. **`check_comparator_freeze.py`'s COVERAGE clause, 8 → 11** (§A1.7). A
   freeze-instrument change is the supervisor's, and it is **jointly
   verification's** since that instrument is theirs.
8. **The filing of `orchestrate_k0h.py`.** K0g's orchestrator lives at
   `verification/runs/F14-cooling-ladder/K0g_runs/orchestrate_k0g.py` — inside
   the run tree. K0h's is at `scripts/orchestrate_k0h.py`, because
   `K0h_runs/` **must not exist before the freeze** and because `FILING_CHARTER`
   R3 puts executables in `scripts/` as `lower_snake.py`, which is where the
   other eight instruments already are. `scripts/check_filing.py` passes on
   both. **The departure from the K0g precedent is disclosed rather than
   quietly taken.**

---

## A1.9 PASSAGES OF THE BODY THIS AMENDMENT SUPERSEDES — ORIGINALS STRUCK, NOT REWRITTEN

Standing rule 6's discipline is applied even though this document is not yet
frozen, because it is the discipline that keeps a record honest:

| passage | status | superseded by |
| --- | --- | --- |
| **§8.2's `REGISTERED CEILING = 5 495.48 core-min`** and the `POINT = 2 202.99` beside it | **SUPERSEDED BY AMENDMENT 1.** Not deleted. It is arithmetically sound for `endTime = 60 s` and is **refuted for the outcome the rung exists to produce** (§A1.4c). | §A1.4c, §A1.4d |
| **§8.3's three-stage table** (311.73 / 1 294.4 / 588.9 core-min over five arms) | **SUPERSEDED BY AMENDMENT 1** as a *schedule*. Its **argument** — L1 first, at 14 % of the cost, to answer the barrier question — is **not** superseded and is **vindicated** by §A1.3a. | §A1.4d, and the manifest |
| **§8.4's per-arm caps** (2.5× the 60 s basis) | **SUPERSEDED** as figures; the **2.5× reasoning** is replaced by **1.35×**, the upper edge of `P-K0h-3`'s own registered band, which is tighter and is tied to a registered prediction rather than chosen. | manifest `cap_rule` |
| **§7.9's `P-K0h-1`** | **NOT superseded. CONTRADICTED AT L1 BY MEASURED EVIDENCE before any K0h compute** (§A1.3c). Its own named failure mode governs. Left standing, unsoftened, so the record shows a prediction that was made and then met contrary evidence. | §A1.3c |
| **§8.2's `I ≤ 8.00 core-min`** | **RETAINED as a bound**, now **tested once at 0.317 core-min (4.0 %)**. §11 item 5 is discharged for the pre-freeze pass and open for the graded pass. | §A1.4e |
| **§7.7's eight-instrument freeze set** | **EXTENDED to eleven** (§A1.7). Nothing removed. | §A1.7 |
| **NOTHING ELSE.** §1, §2, §3, §5, §7.1', §7.1'', §7.2, §7.3, §7.4, §7.5, §7.6, §0.3, §9, §10 | **UNCHANGED, byte for byte.** No band, no `tol`, no `y⁺` window, no completion clause, no verdict-ladder ordering and no reference is touched. | — |

**Version: DRAFT + AMENDMENT 1.**
**Lines whose number changed above this section: 0.**

**SUBMISSIONS PARKED** (standing rule 7): nothing in or derived from this
document or its amendment is sent, filed, uploaded, registered or posted
outside this box.

---

## AMENDMENT 2 — 2026-09-10T16:25:44Z — **A CLAIM THIS DOCUMENT MADE ABOUT VERIFICATION'S INSTRUMENT IS FALSE, AND THE REAL DEFECT IS UPSTREAM OF THE CLAUSE I BLAMED.** Appended by heat-transfer-supervisor personally

**CONDITION FOR A LEGAL PRE-FIRST-COMPUTE AMENDMENT, STATED AND CHECKED (standing rule 2).** No K0h solver has run. **Checked, not assumed:** `verification/runs/F14-cooling-ladder/K0h_runs` **DOES NOT EXIST** on disk (`ls` returns "No such file or directory"), and a `find` over `verification/runs` for `K0h*` returns nothing. Zero K0h solver core-minutes have been spent. Gates are therefore still open and this amendment is legal rather than an addendum. **It moves no gate, threshold, cap or label**; it corrects a factual claim about a third party's instrument and adds a disclosure.

### 1. WHAT THIS DOCUMENT GOT WRONG, at §7.7's follow-on (the passage beginning *"The freeze set is now ELEVEN paths, not eight"*)

That passage asserts that **`scripts/check_comparator_freeze.py`'s COVERAGE clause "must be updated from 8 to 11."** **That is FALSE, and the verification team refuted it at source rather than declining it.** I have re-verified their refutation against the instrument myself rather than accepting the relay:

- **There is no literal 8 in COVERAGE, and the clause is already size-agnostic.** `pin_rows()` iterates `for rel in sorted(pins)`, and the printed figure at `:1560` is `{len(prows) - len(uncovered)} of {len(prows)}` — where `len(prows)` **is this registration's own pin count**. An eleven-path registration prints "11 of 11" with no code change. The only literal `8` in the file is the status sort key `"NO-MARKERS": 8` at `:1485`.
- **No code change is owed to COVERAGE.** The clause's own text further states that a pinned path the walk misses is *"INJECTED into the population by explicit path, whatever it is called and wherever it lives."*

**So this document's claim was wrong in a way that mattered: it aimed a referral at a clause that needed nothing, and would have left the actual defect unrepaired while reporting the matter closed.**

### 2. THE REAL DEFECT IS TWO LINES ABOVE, AND IT IS A FAIL-OPEN ON *THIS* FREEZE

`PIN_PATH` at `:261` is `re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./+-]*\.(?:py|sh))`")` — **it recognises a pin only if the path ends `.py` or `.sh`** — and `registered_pins()` (`:384-409`) builds the pin dictionary from that regex **alone** (`:403`). A registered pin with any other suffix therefore **never enters `pins`, never reaches `pin_rows()`, and is INVISIBLE**: COVERAGE cannot report it missing because COVERAGE never hears of it.

**Applied to this registration's own eleven paths:** nine are `.py`/`.sh` (the eight of §7.7 plus `orchestrate_k0h.py`). The other two — **`K0h_STAGE_MANIFEST.json`** and the demonstration record **`K0h_PREFREEZE_EXTRACTION_DEMONSTRATION.txt`** — are **exactly the two the regex cannot see.** Had this rung been frozen on the plan as written, the instrument would have printed a clean **"PIN COVERAGE: 9 of 9"** while the manifest that holds **the ceiling and every per-arm cap** sat unpinned. **This document's own §7.7 states what that leaves loose, and the statement stands: a freeze that pins the code and leaves the manifest loose leaves the numbers loose.**

**One observation of my own, not in the ruling.** The instrument's printed noun is *"pinned **executable**(s)"*. The narrowing is therefore **disclosed in the output STRING and invisible in the output COUNT** — a caveat present in the prose and absent from the number, which is the failure mode this lab has named before. A reader who knew to weigh the word "executable" could have caught it; no reader does.

**The repair is NOT mine and is NOT taken here.** Verification refuses it to every agent including itself under D539, and it is on Sanaa's desk: of the 138 paths the defect exposes lab-wide, only **29 are INPUTS that decide a verdict** while **102 (74 %) are OUTPUTS the run produces** — and pinning an output is incoherent, since IDENTITY demands worktree == HEAD blob while an output changes when the run runs. A blanket suffix widening would `PIN-DRIFT`-refuse the majority of the cases the check exists to certify. **The question is WHICH paths a registration may pin, not how many.** Nothing in this amendment anticipates that ruling. **Recorded per L-221/L-222: any eventual repair EXTENDS the alternation and never rewrites the pattern, and is not applied until a control fires BOTH WAYS IN THE SAME RUN** — a newly-recognised path must pin **and** a `.py`/`.sh` path must still pin — at the single call site `registered_pins()`, because a one-directional control would certify the widening while a silent narrowing went unmeasured.

### 3. THE DISCLOSURE, PLACED HERE ON THE FACE OF THE REGISTRATION BECAUSE A COMMIT MESSAGE IS NOT THE RIGHT LOCATION

**When this rung is frozen — and it is NOT frozen by this amendment (see §4) — the freeze will be recorded as `PIN COVERAGE: 9 of 11`, NOT `9 of 9`.** The two uncovered paths are `verification/campaign/K0h_STAGE_MANIFEST.json` and `verification/runs/F14-cooling-ladder/K0g_runs/K0h_PREFREEZE_EXTRACTION_DEMONSTRATION.txt`. They are pinned **BY COMMIT ORDERING** — the route the instrument itself prescribes for a limb it cannot reach (`:1590-1600`, *"proves its freeze by commit ordering"*) — and the coverage figure **EXCLUDES them and says so**.

**Why this disclosure is on the document and not only in a commit message:** rule 6 requires a departure to be disclosed **in the document**, and this team raised precisely this location defect against another team at **D591**. A **"9 of 11" that says why is honest; a "9 of 9" that says nothing is the fail-open** — and it would be this team's own fail-open, in the same shape as the one we reported.

### 4. **THIS AMENDMENT DOES NOT FREEZE K0h, AND THE COVERAGE QUESTION WAS NEVER WHAT HELD IT**

Verification's ruling notes that this team's FREEZE-AHEAD *"was never held by"* the coverage clause. **That is correct, and it is recorded here so no successor reads §1-§3 as a clearance.** K0h remains unfrozen on **three grounds, none of which is the pin-coverage question, and any one of which is sufficient**:

1. **`P-K0h-1` is CONTRADICTED BY MEASUREMENT before freeze.** Both completed K0g L1 arms sit **×306.7 and ×315.7 over `tol_T`** (6.133684 K and 6.314012 K against 0.020), with 96.5–96.9 % of cells over tolerance and the **median** cell 18× over. Freezing a registration whose central prediction is already measured false registers a rung **to fail**.
2. **The drafted ceiling cannot buy a graded number.** 5,495.48 core-min buys five arms to `endTime = 150.0 s`; measurement puts the required `endTime` at ≈220 s. An arm that completes non-stationary is `NOT A RESULT` — K0g's lesson verbatim.
3. **The supervisor's `SUPERVISION_CHARTER` §3.1 read is NOT DONE and is NOT DELEGABLE.** The eight carried `k0h` instruments, including **~150 KB of `analyse_k0h.py`**, were staged by an earlier lane and no supervisor has read them as a diff. **A selftest written by the instrument's own author is evidence, not the supervisor's read.**

**Consequence, stated rather than hidden: FREEZE-AHEAD remains 1, below the §2 floor of 3.** That is preferred to restoring the count with a rung registered to fail.

**Rule 6 compliance:** *lines whose number changed above this section: 0* — **verified byte-for-byte against the HEAD blob in Python**, not by `git diff` or `git status`, which read against the permanently stale shared index in this repository. **Item (2) of the referral — whether K0h may restart from K0g's 60 s fields, and rule 4's age guard — is PENDING with verification and is NOT ruled. Nothing here reads as permission on it.**

**SUBMISSIONS PARKED** (rule 7): nothing in or derived from this amendment is sent, filed, uploaded, registered or posted outside this box.
