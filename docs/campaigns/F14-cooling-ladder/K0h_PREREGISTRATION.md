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
