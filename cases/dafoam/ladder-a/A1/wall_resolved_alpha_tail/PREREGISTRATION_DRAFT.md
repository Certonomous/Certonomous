# A1WRT — WALL-RESOLVED α-TAIL, INCOMPRESSIBLE ONLY — PRE-REGISTRATION **DRAFT**

> ## ⚠ THIS IS A DRAFT. IT IS NOT FROZEN.
>
> **NOT FROZEN. NOT ENQUEUED. NOT LAUNCHED. ZERO COMPUTE SPENT.**
> No md5 manifest is pinned by this file, no queue entry exists, and no solver,
> container or queue release was performed by the lane that wrote it. The
> supervisor's §3 check 4 — cap arithmetic and the reproduction-control
> threshold read personally — is owed **before** this becomes a freeze, and is
> not delegable. Until then nothing here binds anything.
>
> **The successor is a NEW ITEM on a FRESH RUN ROOT with its OWN budget** —
> a fresh pre-registration under `VERIFICATION_CHARTER` §2b limb 1.
> **It is NOT a restart of A1WR Stage 2**, which is closed
> (`A1WR_STAGE12_RESULTS.md`, `NOT A RESULT`), whose freeze contains no restart
> rule, whose in-memory continuation state died with the process, and whose
> registered per-arm budget is 79.37 % spent with 165.03 core-min remaining
> against a 186.02 core-min need.

**Item:** `A1WRT` — NACA0012 α-tail 12…18° on the A1WR wall-resolved L3 mesh,
**incompressible only** (`DASimpleFoam`), run on a **REPAIRED patch identity
(`empty`, not `symmetry`)** with a one-variable pair at α = 12 that measures the
repair itself. **Eight points, three units.**
**Team:** dafoam **Lane:** lab-lane **Drafted:** 2026-09-03
**Status:** NO COMPUTE HAS BEEN SPENT ON THIS ITEM. Run root
`/home/ubuntu/certonomous-runs/A1WRT/` **does not exist** — checked, not
asserted, at draft time; the freeze must re-check it in its own shell.
**Verdict class:** `FEASIBILITY`. **Verdict ceiling:** `GATE REACHED`.

---

## 0. WHAT THIS ITEM IS FOR, AND WHAT IT INHERITS

A1WR Stage 2 measured a clean incompressible polar at α 0…12 on the
wall-resolved L3 mesh — CL strictly increasing, dCL/dα strictly decreasing, no
break, no kink — and was killed by a `shutdown -h now` at 02:25:05Z with α = 13
in flight at 2,500 of 4,000 iterations. **The tail α 13…18 is the part of the
registered polar that does not exist, and this item gets it legally.**

Inherited unchanged, by md5, from the A1WR freeze:

| instrument | md5 | role |
|---|---|---|
| `a1wr_runScript_incomp.py` | `d48f48c5e2e41e86981acbf6feccb3c4` | producer |
| `a1wr_cmd.sh` | `eba014f2c538611d2249c3fcf9b3ddd7` | in-container unit program |
| mesh | A1WR L3, **130,304 cells**, `/home/ubuntu/certonomous-runs/A1WR/L3/` | subject |
| image | `dafoam-idwarp-rot:v1`, `sha256:2927768a16ac…`, `libidwarp` md5 `85f59e87253e0a71a813f64ca6e4c425` | PATCHED build |

Frozen numerics carried unchanged: `primalMinResTol = 1.0e-8`, `endTime = 4000`,
SA, `useWallFunction: False`, **np = 1**, `OMP_NUM_THREADS=1`, one-core cpuset.
**Nothing about the discretisation, the numerics or the build moves.** Changing
any of them would make the tail non-comparable to the α 0…12 body it extends —
the two-variable trap A1WR refused four times.

---

## 1. THE COMPRESSIBLE ARM IS ABSENT, AND HERE IS ITS REASON ON THE RECORD

**A missing arm needs its reason on the record, the same way a missing point on
a polar does.** The compressible arm is **not run by this item**, and this is
why, measured:

- **11 of 11 compressible wall-resolved solves have failed** — A1WR's 9 sweep
  points (α 0…8) and MAAOA's 6 points collapse to the same outcome
  (`LAB_STATE` S-27), at every Mach and **including α = 0**.
- **It is not a near miss.** Across 409 print steps A1WR's arm C bound `U`
  659 + 507 times, `p` 385 + 385, `e` 383 + 384, `rho` 383 + 371. It produced
  **negative CD at five angles** (to −10.1252) and CL swinging +79.8907 to
  −80.4237. Arm I's entire census over the same run is `Bounding nuTilda>` ×
  559 — one per print step, the ordinary SA clip.
- **The setup defect is not identified.** Re-running it now would be a third
  attempt at something that has failed twice — Sanaa's 2026-09-03 envelope law
  item 4 names exactly that as an escalation trigger
  (`etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md`, read for this
  draft, not relayed).

**Registered position: the compressible arm returns as its own item behind a
DIAGNOSIS, not behind a retry.** Its absence here is a decision on evidence, and
this item may not be read as evidence about it either way.

---

## 2. THE DESIGN — A BLOCKING PHYSICS FIX, AND THE PAIR THAT MEASURES IT

### 2.0 The patch identity is repaired, under Sanaa's own classification

Sanaa, 2026-09-03 ~20:00Z, verbatim
(`etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md`, **read at source for
this draft, not relayed**):

> *Blocking physics fixes — a result can't be produced or trusted without them
> (**wrong patch identity on a mesh**, a residual print that isn't the max over
> equations, a boundary condition set wrong, a linear solver failing). These jump
> every queue, need no petition, and the team fixes them and records a lesson
> afterward, not before.*

**That names this defect exactly.** The A1WR L3 mesh's two bounding planes are
`type symmetry`, not `empty`; OpenFOAM therefore assembles a z-momentum equation
on a mesh one cell thick (§7). **Running the tail on the defective identity would
knowingly spend ~256 core-min producing seven numbers that cannot be trusted and
then say so on the certificate.** Under her classification the fix jumps the
queue, needs no petition, and the lesson is recorded afterward.

**REGISTERED: the tail runs on `empty`.**

### 2.1 Three units, because each comparison must move exactly ONE variable

| unit | patch | start | points | what it isolates |
|---|---|---|---|---|
| **U1** `alpha12_symmetry` | `symmetry` | COLD | α = 12 | **cold-vs-continued**, against A1WR's own continued α = 12 (`CL` 1.19079592024, `CD` 0.030665481166). This is `G-REPRO` exactly as §3 registers it, on A1WR's own configuration, unchanged. |
| **U2** `alpha12_empty` | `empty` | COLD | α = 12 | **`symmetry`-vs-`empty`**, against U1 directly above it. Both COLD, same mesh, same numerics, same operating point, same iteration budget — a true one-variable pair. |
| **U3** `tail_empty` | `empty` | CONTINUED from U2's converged state, **in the same process as U2** | α = 13…18 | the trustworthy tail |

**Eight points, and the eighth is what makes the other seven interpretable.**
Comparing a cold `empty` α = 12 directly against A1WR's *continued* `symmetry`
α = 12 would move cold-vs-continued **and** `symmetry`-vs-`empty` at once and
measure neither. **U1 is bought precisely to remove that confound** (§4.3 prices
it at ~32 core-min), and it is the same one-variable discipline this item has
now applied five times.

U2 and U3 are **one process, one container**: `0/` reset from `0.orig` once
before U2's cold α = 12, then α = 13…18 ascending, each inheriting its
predecessor's converged state **in memory**. U1 is its own container and its own
case tree, because it carries a different mesh boundary file.

**No point is retried, relaxed, re-tuned or dropped**; a point that fails is
recorded with its residual history and the sweep continues, with every subsequent
point flagged `after_exception=TRUE`. **A missing point on a polar is a lie by
omission.**

### 2.2 What "runs on `empty`" actually requires on disk — registered, not waved

`empty` is not a one-word edit. **`G-PATCH` verifies all three by execution
before any primal:**

1. `constant/polyMesh/boundary`: `symmetry1`/`symmetry2` → `type empty;`
   (`inGroups 1(empty)`), 130,304 faces each, unchanged.
2. **Every field in `0.orig/`** — `U p nut nuTilda k omega epsilon` — must carry
   `type empty;` on those two patches. A mesh patch typed `empty` beside a field
   patch typed `symmetry` is a case that will not start, and a field left
   `symmetry` on a mesh patch typed `empty` is the silent-no-op class this lab
   has been bitten by twice.
3. **The solver's own log line is the acceptance test, and it is a measurement,
   not an assertion:** the `empty` units must print
   **`Mesh has 2 solution (non-empty) directions (1 1 0)`** and U1 must print
   **`Mesh has 3 solution (non-empty) directions (1 1 1)`**. `G-PATCH` refuses at
   exit 2 on any other combination. **This is the whole defect reduced to one
   line the solver prints about itself.**

**`0/` MUST be reset from `0.orig` for a genuinely cold start** — pyDAFoam
renames a converged solution back into `0/`, so a "cold" start that does not
reset is not cold. **`G-COLDSTART` verifies the reset ON DISK before the first
primal** (every field's `internalField` read back and asserted `uniform`), not
from the driver's own claim. A1WR's forensics are the reason this is a gate and
not a comment: its killed `sweep_I/case/0/` was left carrying a **nonuniform
130,304-cell `U`** under an α = 13 inlet beside a **uniform** `p`, `nut` and
`nuTilda` — a mixed state that a naive restart would have consumed silently.

### 2.1 Why the tail cannot simply be restarted from A1WR's disk — settled, not assumed

Measured (`A1WR_STAGE12_RESULTS.md` §8): no `processor*` directory exists
anywhere under the A1WR run root; no time directory other than `0` and `0.orig`
exists in either sweep; no `.bin`, restart or pickle file exists. The only
surviving converged data is the α = 12 velocity field, already stamped with the
α = 13 inlet, with the pressure and the entire SA turbulence state at their
uniform freestream values. **There is no checkpoint. The continuation state was
in memory and died with the process.**

---

## 3. ⚠ `G-REPRO` — THE REPRODUCTION CONTROL, AND A CORRECTION TO ITS PREMISE

This is the best part of the item and it is **registered as a gate, not as a
remark.** But the premise it was handed down with is **false for this data**,
and registering it unexamined would have produced a control nobody could read.

### 3.1 The premise as stated, and why it does not hold here

> *"A converged steady solution should be history-independent, so agreement
> corroborates that the continuation label was live."*

**A1WR's α = 12 point is NOT CONVERGED.** The frozen reader
`a1wr_read.py` grades all 13 arm-I points `NOT CONVERGED`; DAFoam's success
string `Minimal residual … satisfied the prescribed tolerance 1e-08` appears
**zero times** in `sweep_I/out/sweep.log`; every point ran the full 4,000
iterations; and at α = 12's last print the initial residuals were U0 1.18e-08,
p 1.66e-08, nuTilda 2.80e-08 — **above** the registered 1e-8 and still falling.

So the comparison this control performs is **not** "two roads to the same fixed
point". It is **"two roads to iteration 4,000"**, which is a *stronger and
rarer* property that no theory guarantees. **Registered consequence:
disagreement at iteration 4,000 would NOT by itself impeach the continuation
label**, and a band sized on converged-solution anchors would be far too tight.

### 3.2 The anchors, MEASURED, and what they do and do not bound

Converged cold-vs-continued pairs on the **coarse** mesh, α = 4, both regimes,
both sides reaching the 1e-8 tolerance:

| | continued CL | cold CL | relative |
|---|---|---|---|
| AOAI (incompressible) | 0.394096562948 | 0.394096584258 | **+5.407e-08** |
| AOAC (compressible) | 0.422884513911 | 0.422884515661 | **+4.140e-09** |

CD relative: AOAI **−8.781e-08**, AOAC **−4.10e-09**. Read from
`/home/ubuntu/certonomous-runs/CURRICULUM-AOA{I,C}-…/out/LEDGER.tsv`.

**These bound history-dependence of a CONVERGED solution at ≲ 1e-7 relative,
and they bound nothing else.** They are the anchor for §3.3's *plateau* limb and
are explicitly **not** the anchor for its *iteration-4,000* limb.

### 3.3 The residual-state term, MEASURED and EXTRAPOLATED, and the registered band

A1WR's α = 12 CL was still drifting monotonically at the cap. Measured from the
last 12 prints of that segment: increments per 100 iterations
−6.096e-05, −5.337e-05, −4.660e-05, −4.057e-05, **−3.522e-05**, decaying with a
geometric ratio of **0.8681**. Geometric-sum remaining drift to plateau:
**−2.319e-04 absolute = −1.947e-04 relative** — **EXTRAPOLATED, and labelled
so.** CD's tail gives ratio 0.9440 and remaining **+1.78e-04 relative**, more
sensitive to the ratio and therefore the weaker of the two.

**So the reported CL = 1.19079592024 sits roughly 2e-4 relative above its own
plateau, and two solves stopped at the same cap from different histories can
legitimately differ by that order.**

**REGISTERED, BEFORE THE RUN:**

| limb | quantity compared | band | basis |
|---|---|---|---|
| **R1** | CL and CD **at iteration 4,000**, cold α = 12 vs A1WR's continued α = 12 | **\|Δ/x\| ≤ 1.0e-3** | ≈ 5× the MEASURED-and-EXTRAPOLATED 1.95e-4 (CL) / 1.78e-4 (CD) residual-state head-room of §3.3 |
| **R2** | the **geometric-extrapolated plateau** of each series, computed by the identical frozen routine on both | **\|Δ/x\| ≤ 1.0e-4** | the §3.2 converged anchors (≲ 1e-7) widened ~1,000× for the extrapolation's own error, which is the term that dominates |

**Both limbs are published whichever way they fall. R2 is the limb that tests
the property that matters** — history-independence of the fixed point — and is
the reason the cold α = 12 is run to the **identical `endTime` 4,000 and the
identical `primalMinResTol` 1e-8**, so that the only thing differing between the
two series is the starting state.

### 3.4 What each outcome means — registered before the answer exists

- **R1 and R2 both inside band → `CORROBORATED`.** The continuation label on
  A1WR's α ≤ 12 body was live, and this item's tail is a faithful continuation
  of that body. The tail may be reported beside it.
- **R2 inside, R1 outside → the fixed point agrees and the iteration-4,000
  states do not.** That is a statement about *iterative history at a fixed
  budget*, not about the polar; the tail stands and the discrepancy is
  published with both series.
- **R2 outside band → THE FINDING, AND IT IS WORTH MORE THAN THE TAIL.** Two
  starting states reach different plateaus on the same mesh at the same α. The
  item reports that, the tail's `CONTINUED` labels are **withdrawn**, and the
  successor is a diagnosis, not more points. **Registered in advance so this
  cannot be narrated afterwards.**
- **The cold α = 12 fails outright** → `NOT A RESULT` on `G-REPRO`; the tail is
  still run and reported, with the control's absence named, never papered over.

**`G-REPRO` may only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the
reverse** (`CLAUDE.md` rule 5's permitted direction).

### 3.5 `G-PATCHPAIR` — THE SECOND COMPARISON, AND ITS THRESHOLDS ANCHORED ON MEASURED DRIFT

U1 (`symmetry`, cold) against U2 (`empty`, cold). **The like-for-like quantities
are not the two values at iteration 4,000**, because U1 stops at the cap still
drifting while U2 is expected to converge and stop early (§7). Comparing those
two directly would fold U1's own residual-state head-room into the answer and
call it contamination.

**REGISTERED: the comparison is U1's EXTRAPOLATED PLATEAU against U2's CONVERGED
VALUE** — each solve's own best estimate of its own fixed point. U1's series and
its geometric fit are published whole so the extrapolation can be checked.

**The registered prediction, written before the run — and it is the boring one:**
CL and CD are **unchanged** between `symmetry` and `empty` to within the
extrapolation's own error, and **the only change is that the `empty` solve
converges**, because with two solution directions there is no z-momentum equation
to assemble and therefore no `U2` residual to floor. **It converges because the
equation that floored is gone, not because anything was tuned. No tolerance is
relaxed and `endTime` is not raised.**

**The thresholds, anchored on measurement rather than on round numbers:**

| band | verdict | anchor |
|---|---|---|
| **\|Δ/x\| ≤ 1.0e-4** | **NOISE** — the repair does not move the coefficients | the plateau extrapolation's own sensitivity: CL's geometric ratio is 0.8681 and CD's is 0.9440, so a ±0.02 error in r moves the remaining term by ≈ ±25 %, i.e. **≈ ±4.9e-05 relative** on CL. The band is that, doubled. |
| **1.0e-4 < \|Δ/x\| ≤ 1.0e-3** | **INDETERMINATE** — reported, neither cleared nor called contamination | between the extrapolation's error and the residual-state head-room; the instrument cannot separate them |
| **\|Δ/x\| > 1.0e-3** | **⚠ CONTAMINATION, AND IT IS THE FINDING** | **5.1× the MEASURED residual-state head-room of 1.947e-04** (§3.3), so larger than any iteration-state effect can explain |

**If it lands in the third band the finding is large and its reach is stated in
advance: it would touch every incompressible number this ladder has produced on
a `symmetry`-bounded 2-D mesh**, not merely this item. That is registered here so
it cannot be discovered and then minimised.

**A cheaper coarse-mesh anchor of the same pair is registered separately on
D19T's 4,032-cell grid**, which also tests the mesh-scaling half of the account
(floor ~1.7e-10 there against the measured 3.238e-08 here). **Different mesh,
different item. This item does not register the coarse pair and must not.**

---

## 4. COST — REGISTERED BEFORE COMPUTE, FROM MEASURED WALLS

### 4.1 Which ledger this draws on — say it so nobody charges the wrong one

**This is Ladder A, not the industrial ladder.** It draws on `CLAUDE.md`
rule 12's under-$25 pre-authorisation and rule 12's bookkeeping. **It does NOT
draw on the $1,000 Rungs 0–3 benchmark envelope** of Sanaa's 2026-09-03 law,
which is a *ladder* budget for the industrial benchmark family. Nothing in this
item is charged against that envelope and it does not move its 80 % trigger.

### 4.2 The anchor — MEASURED on this exact mesh, image and solver

Every A1WR arm-I point ran **exactly 4,000 iterations**, so per-point cost is
essentially fixed and this is a measurement, not a model.

| basis | s/iteration | window |
|---|---|---|
| α = 9, 10, 11 | 0.41930 | quiet box (after 21:58Z) |
| **α = 12** | **0.46155** | quiet box |
| **α = 13, in flight when killed** (1,153.35 s / 2,500 it) | **0.46134** | quiet box |
| α = 0 | 1.15400 | **14 containers live** |
| `cold_I_4/14/17` | 1.781 / 1.810 / 1.784 | **14 containers live** |

**α = 11 → α = 12 rose 10.2 %; α = 12 → α = 13 was flat.** The rise is real but
did **not** compound, so the tail is priced at the α = 12/13 rate with an
explicit allowance rather than at a compounding trend. **Do not average blindly
across the trend** — the α = 0 and cold rows above are contention, not α.

### 4.3 The estimate

**Eight points across two containers.** Priced per unit, because each carries its
own deadline (§4.4).

| unit | term | arithmetic | core-min |
|---|---|---|---|
| **U1** | 1 point × 4,000 it × **0.4615 s/it** (MEASURED) | 1,846.0 s | 30.77 |
| **U1** | container start + import | 93.85 s (MEASURED on `a1wr_sweep_I`: container wall 28,146.98 s − last `ExecutionTime` 28,053.13 s) | 1.56 |
| | **U1 ESTIMATE** | | **≈ 32.33** |
| **U2+U3** | 7 points × 4,000 it × 0.4615 s/it | 12,922 s | 215.37 |
| **U2+U3** | container start + import | 93.85 s | 1.56 |
| **U2+U3** | tail-stiffening allowance on α 14–18, **EXTRAPOLATED** | 5 × 4,000 × 0.4615 × 0.25 = 2,307.5 s | 38.46 |
| | **U2+U3 ESTIMATE** | | **≈ 255.39** |
| | **ITEM ESTIMATE** | 32.33 + 255.39 | **≈ 288 core-min** |

= 4.800 core-h ≈ **$0.2462 DERIVED, NOT MEASURED** at the owner-stated
$0.0513/core-h; `cost_basis` **REPORTED-BY-OWNER** — the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Every point is priced at the FULL 4,000 iterations, which is deliberately
conservative for the `empty` units.** §7 registers that they are expected to
*converge* and therefore to stop early — possibly well before 4,000. **That
saving is NOT taken in advance**: an estimate that banks a predicted improvement
is an estimate arguing for its own hypothesis. If the `empty` units do stop
early, the actual/predicted ratio comes in low and **that is reported at
calibration as a favourable misprediction with its cause named**, not quietly
absorbed. The `empty` solve also drops one momentum equation per iteration, which
should make it cheaper per iteration; **that is UNMEASURED on this mesh and no
credit is taken for it either.**

**The term most likely to carry the error is the tail-stiffening allowance**, and
it is named in advance, exactly as A1WR §7.5 named its own iteration-scaling
assumption.

### 4.4 The cap, and the deadline arithmetic **EXECUTED AND EVALUATED AT DRAFT TIME**

Sanaa, 2026-09-03, verbatim: *"still carries a hard per-run cap (set by the team
at ~3× its own estimate, not by me) … The estimate is an instrument, not a
permission slip."*

**⚠ THE ESTIMATE AND THE CAP ARE SPLIT, BECAUSE CONFLATING THEM IS WHAT PRODUCED
THE CONFLICT.** A single figure that assumes a quiet box is the A1WR error; a
single figure that assumes a full one would report a ~0.26 ratio on a quiet night
and corrupt the calibration dataset. So:

**THE ESTIMATE IS A PREDICTION AND IS REPORTED AS A FUNCTION OF OCCUPANCY**
(solve time and the stiffening allowance scale with occupancy; the two container
starts do not):

| occupancy | item estimate |
|---|---|
| solo | **287.7 core-min** |
| 2× | **572.3 core-min** |
| **14-way, the MEASURED saturation (3.85915× solo)** | **1,101.4 core-min** |

**THE DEADLINE AND CAP ARE PROTECTION AND ARE SIZED ON THE WORST REGISTERED
CASE — the 14-way end:**

> **U1 = 361 core-min** (3.00 × 120.30) · **U2+U3 = 2,943 core-min**
> (3.00 × 981.11) · **ITEM CEILING = 3,304 core-min** = 3.00 × the 14-way
> estimate. = 55.07 core-h ≈ **$2.825 DERIVED** — under the $25
> pre-authorisation and far under the $150 escalation trigger.

**THE CERTIFICATE COMPARES ACTUAL AGAINST THE ESTIMATE AT THE MEASURED
OCCUPANCY**, using the occupancy `G-CONCURRENCY-PRECOND` records at launch and at
every point boundary. Like against like — that is the calibration payoff, and it
exists only because the occupancy recording is in the instrument.

**D19T was frozen, md5-pinned, gate-checked and launched TWICE with a deadline
of exactly 0 s because nobody ever executed the arithmetic at freeze. It is
executed here, in this document, and its result is evaluated:**

```
ranks         = 1                        (np = 1, registered)
CAP_MARGIN_S  = 300                      (3.2x the MEASURED 93.85 s container start)

TMO_U1        = int(  361 * 60 / 1) - 300 =  21660 - 300 =  21360 s
TMO_U2U3      = int( 2943 * 60 / 1) - 300 = 176580 - 300 = 176280 s
```

**EVALUATED, both of them, here, in this document:**

| unit | `TMO` | `> 0` ? | `TMO/60` core-min | ≤ its cap ? |
|---|---|---|---|---|
| U1 | **21,360 s** | ✓ | 356.00 | ≤ 361 ✓ |
| U2+U3 | **176,280 s** | ✓ | 2,938.00 | ≤ 2,943 ✓ |

Back-checks exact. Effective budget `356.00 / 120.30 = 2.96×` (U1) and
`2938.00 / 981.11 = 2.99×` (U2+U3), both against the **14-way** estimate.

**⚠ AND AN HONEST LIMIT ON WHAT THAT DEADLINE PROTECTS.** `TMO_U2U3` is
**176,280 s ≈ 49 hours**. **This box was powered off after 7 h 49 m on the night
this item's predecessor ran**, and its longest recorded uptime this week is
under 23 h. **A 49-hour in-container deadline is therefore not the binding
protection — the box's own uptime is**, and a poweroff is an infrastructure kill
that no cap can convert into a cap-stop. The deadline is sized correctly for the
registered worst case and is stated here as **necessary but not sufficient**;
the real protection against an over-long run on a busy box is the per-point
ledger row, which lands after every point and survives the kill.

**A freeze that cannot print a positive evaluated integer in this table does not
launch.** D19T was frozen, md5-pinned, gate-checked and launched **twice** with a
deadline of exactly 0 s because nobody ever executed this arithmetic.

### 4.5 The deadline against a BUSY box — the 331.7 core-min lesson, applied

A1WR lost **all six** cold controls and 331.6667 core-min for **zero physics** to
a 3,300 s deadline sized from a quiet-box rate and spent on a box the same item
had just filled 14-deep. Registered here rather than repeated:

**U2+U3**, 7 points × 4,000 it = 28,000 iterations against a 45,720 s deadline:

| box state | s/iteration (MEASURED) | 28,000 it | vs the 45,720 s deadline |
|---|---|---|---|
| quiet | 0.4615 | 12,922 s + 94 s = **13,016 s** | **28.5 % — finishes comfortably** |
| moderate contention, 2× | 0.923 | 25,938 s | 56.7 % — finishes |
| **break-even** | **1.63286** | 45,720 s | **100 % — the ceiling** |
| A1WR's measured 14-way saturation | 1.781 | 49,868 s | **109.1 % — CAP-STOPPED at ~6.4 of 7 points** |

**U2+U3 survives contention up to 3.538× the solo rate** —
`45,720 / 28,000 = 1.63286 s/it`, and `1.63286 / 0.4615 = ` **3.53816**.

**U1**, 1 point × 4,000 it against a 5,520 s deadline: break-even
`5,520 / 4,000 = 1.38000 s/it`, i.e. **2.990× solo**. **U1 therefore has
MATERIALLY LESS headroom than U2+U3 and is the unit that will cap-stop first
under load.** That is stated because the two units are not interchangeable and
the §4.6 arithmetic must be evaluated **per unit**, not once for the item.

**⚠ AND A1WR'S OWN MEASURED WORST CONTENTION IS 1.781 s/it = 3.85915× SOLO,
WHICH IS ABOVE THAT CEILING. THE ITEM DOES NOT SURVIVE IT.** *(An earlier draft
of this section claimed 3.90× headroom. That was arithmetically wrong, it
contradicted this very table's 108.9 % row, and it overstated the real headroom
by 10 % — on the one number a reader would use to decide whether to launch
beside other work. Corrected by the supervisor's §3 check 4, and the error is
recorded rather than silently fixed.)*

Beyond the ceiling the item cap-stops, and **that outcome is registered in
advance: a cap-stop is `NOT A RESULT` on the unfinished points; points already
in the ledger stand.** No new budget is granted on an overrun.

**THIS IS WHY §4.6'S CONCURRENCY PRECONDITION IS A LAUNCH GATE AND NOT ADVICE.**
The margin between "finishes comfortably" and "cap-stops having bought nothing"
is a box-occupancy condition that no gate in this lab currently reads.

**AND THE MECHANISM IS MEASURED, NOT GUESSED:** A1WR's cpusets were all disjoint
(A1WR 8–15, MAAOA 2–7, verified by `docker inspect`) and per-core throughput
still degraded 2.75–4.77×. **A one-core cpuset isolates a core, not memory
bandwidth.** The driver therefore **records box occupancy and MemAvailable at
launch and at every point boundary into the ledger row**, so contention is
attributed from measurement at calibration time instead of argued.

**This item is at most TWO np = 1 processes on two cores** (U1 may run beside
U2+U3 or before it; U3 is serial with U2 by construction). It consumes 2 of 16
cores, so it is a legal filler under the never-idle rule without itself creating
the saturation that killed A1WR's controls.

### 4.6 `G-CONCURRENCY-PRECOND` — A LAUNCH GATE, BECAUSE §4.5's MARGIN IS NEGATIVE AGAINST MEASURED SATURATION

**THE DEFECT WAS NEVER CONCURRENCY. IT WAS A COST BASIS THAT ASSUMED A QUIET BOX
WHILE NOTHING CHECKED.** An earlier form of this clause demanded an empty
machine; that would fight Sanaa's standing order that the box is never idle, and
it would refuse launches the arithmetic says are perfectly safe.

**REGISTERED: the launcher records measured occupancy and `MemAvailable` at
launch AND at every point boundary into the ledger row, and REFUSES only if the
registered deadline does not cover the predicted rate AT THE MEASURED
OCCUPANCY.** The census must itself be shown able to return a NON-EMPTY answer
before an empty one is accepted (rule 3, applied to a census rather than to a
field reader — a census that cannot see a running container is not evidence that
none is running), but an empty census is **not** a launch condition.

**The test is the arithmetic, not an empty machine.**

**REFUSAL POINT, RE-DERIVED AGAINST THE NEW DEADLINES:**

| unit | deadline | iterations | break-even s/it | = × solo | refuses at |
|---|---|---|---|---|---|
| U1 | 21,360 s | 4,000 | 5.3400 | **11.57×** | occupancy > 11.57× |
| U2+U3 | 176,280 s | 28,000 | 6.2957 | **13.64×** | occupancy > 13.64× |

**The measured 14-way saturation is 3.859× solo, so both deadlines cover the
worst occupancy this box has ever exhibited with 3.0–3.5× margin, and this gate
NEVER REFUSES at any occupancy on record — n = 7 and n = 8 included.** It records
and it queues; it does not block. That is the correct outcome under
"reported, not gated" and under *"I prefer something to be running and watched
than too much governance and no run."*

**It is not decorative, and here is the condition that would still fire it:** an
occupancy above ~11.6× solo, i.e. roughly three times worse than anything
measured on this box. If that is ever recorded, the arithmetic refuses and the
refusal is the finding. Contention is otherwise attributed from measurement at
calibration time instead of argued.

**THE LAB-WIDE FINDING THIS GATE RESTS ON, STATED IN ITS GENERAL FORM BECAUSE IT
IS NOT AN A1WR FACT:**

> **A one-core cpuset isolates a core. It does not isolate memory bandwidth.**
> A1WR's cpusets were all disjoint — A1WR on cores 8–15, MAAOA on 2–7, **verified
> by `docker inspect` and not assumed** — and per-core throughput of a
> 130,304-cell OpenFOAM SIMPLE solve still degraded **2.75× to 4.77×** under
> 14-way concurrency. **No gate in this lab reads this**, every in-container
> deadline in the lab is sized on a solo rate, and **331.6667 core-min bought
> zero physics learning it** when all six of A1WR's cold controls timed out.

`G-PLACEMENT`'s cpuset-disjointness reading is **necessary and not sufficient**,
and this item registers that distinction on its face rather than discovering it
again.

### 4.7 Calibration at completion

Per rule 12 and `docs/COST_CALIBRATION.md`'s append rules: at completion the
estimate above is compared against the actual in core-minutes from logs, dollars
derived and labelled, the ratio stated, and the gap attributed with
**contention, waste and misprediction named separately** and waste never
absorbed into the ratio.

---

## 5. GATES

| gate | subject | verdict rule |
|---|---|---|
| `G-COLDSTART` | every field of `0/` read back from disk and asserted `uniform` **before** the first primal | refuse (exit 2) on any nonuniform field — A1WR's mixed `0/` is the precedent |
| `G-PATCH` | §2.2 — the patch identity ACTUALLY IN FORCE: mesh `boundary` types, every `0.orig/` field's entry on those patches, and the solver's own `Mesh has N solution (non-empty) directions` line | refuse (exit 2) unless U1 prints **3 (1 1 1)** and U2/U3 print **2 (1 1 0)**. **The defect reduced to one line the solver prints about itself** |
| `G-PATCHPAIR` | §3.5 — U1's extrapolated plateau vs U2's converged value, CL and CD | ≤ 1.0e-4 NOISE; ≤ 1.0e-3 INDETERMINATE, reported; > 1.0e-3 **CONTAMINATION and it is the finding** |
| `G-REPRO` | §3, both limbs R1 and R2, bands registered above | inside → `CORROBORATED`; R2 outside → tail labels withdrawn, `NOT A RESULT`; control absent → `NOT A RESULT` on the control |
| `G-COMPLETE` | rule 4, **all** clauses: rc 0, `End` line, last time == `endTime`, fields present, `ExecutionTime` count == `endTime`, every field newer than the case's own datum | refuse (exit 2) rather than degrade, and **the distinction is registered**: a clause the reader CAN evaluate and that fails is a `GATE FAIL`; a clause it CANNOT evaluate is a REFUSAL. *(An earlier draft justified this gate by claiming A1WR had never implemented `G-COMPLETE`. **That claim was FALSE and is withdrawn** — see §5.1. The gate is implemented here because a single grading path is easier to audit than two, not because A1WR lacked one.)* |
| `G-CAPS` | **arithmetic, not prose**: measured core-min per unit against the 768 cap, computed by the reader and printed | cap-stop ⇒ `NOT A RESULT` on the affected points. *(The same withdrawn claim applied here; A1WR enforces its cap in `a1wr_chain_driver.sh`. See §5.1.)* |
| `G-CONCURRENCY-PRECOND` | §4.6 — measured occupancy and MemAvailable recorded at launch and at every point boundary, from a census PROVED able to return non-empty | **refuse to launch only if the registered deadline does not cover the predicted rate AT THE MEASURED OCCUPANCY.** An empty box is NOT a launch condition — this item survives 3.543x solo and must not block the box. The test is arithmetic |
| `G-YPLUS` | measured y+ min/mean/max on the wall patch, every α | `GATE FAIL` if y+max ≥ 1.0 anywhere; refuse (exit 2) on a blind channel for a point that ran ≥ 200 iterations. **The mesh is NOT re-cut** (A1WR §3.4) — an overshoot is a registered outcome |
| `G-WALLTREAT` | `useWallFunction: False` in the staged script **and** `BCType=nutLowReWallFunction` in the solver log for the `wing` patch | refuse (exit 2) if the log does not confirm the BC that actually ran |
| `G-FIXTURE` | **every planted control's fixture is STATIC and independent of the run being graded** | refuse (exit 2) if any fixture is read from this item's own run root. **THE L-435 REPAIR** — see §6 |
| `G-STALL` | no output binds a stall word to a numeric angle | refuse (exit 2) on a planted claim; must NOT fire on the honest caveat |
| `G-NOBAND` | no output presents a value as grid-converged or inside a band | refuse (exit 2) — the L3 family still has no Roache triple |
| `G-IMG` / `G-FREEZE` | image id and `libidwarp` md5 exact; every instrument md5 checked at launch | refuse (exit 4) on any mismatch |

**Composition:** D19M's repaired `compose_item` from `verdict_before_ceiling`,
hard-gate list tested for **both** `GATE FAIL` and `NOT A RESULT`. Ceiling
`GATE REACHED`.

### 5.1 ⚠ A WITHDRAWN ACCUSATION — `G-COMPLETE` AND `G-CAPS` **ARE** IMPLEMENTED IN A1WR

An earlier draft of this document, and this lane's census, recorded that A1WR
registers `G-COMPLETE` and `G-CAPS` and never implemented them, on the evidence
that `grep -c 'G-COMPLETE' a1wr_read.py` returns 0. **That inference was wrong
and is withdrawn in full.**

Verification's §2v ruling is the standard, and it refused a specimen of exactly
this shape: *"a gate is implemented where it must be, not where the reader is —
the grading path is every frozen instrument the registration names, not the one
file with `analyse_` in its name."* Checked against every frozen A1WR instrument:

| gate | implemented at | the line |
|---|---|---|
| `G-COMPLETE` | `a1wr_runScript_incomp.py:357-362` | `AOA_SWEEP_TRUNCATED n_declared=%d n_executed=%d -- NOT a completion` then `exit(97)` |
| `G-COMPLETE` | `a1wr_cmd.sh:68-71` | counts `AOA_POINT_END` markers, `A1WR_COUNTS declared=… point_end_markers=…`; the PROBE branch exits 97 on a missing endTime state |
| `G-CAPS` | `a1wr_chain_driver.sh:251-257` | `CAN_DUP = 'YES' if I_SPEND + 55.0 <= ARM_CAP_MIN`, else `A1WR_DUP_CAPSTOP … A cap-stop is NOT A RESULT on that control.` |

**And it fired LIVE.** All six A1WR cold controls carry the truncation marker in
their docker logs and exited **97** on it. It did **not** fire for the two
sweeps — because the 02:25:05Z SIGTERM killed the containers before the unit-end
block ran (no `sweep_*.docker.log` exists; `AOA_SWEEP_END` appears **0** times in
either sweep log). **A gate whose host process was killed is not an unimplemented
gate**, and conflating the two is how a false accusation gets made.

**What survives, narrowly:** `a1wr_read.py` does not itself name or adjudicate
either gate — it prints a bare `COUNT MISMATCH` and returns 0. That is an
observation about one instrument's division of labour. Under §2v it is reported
**CLEAN**, not as a suspicion.

---

## 6. `G-FIXTURE` — THE L-435 REPAIR, AND WHY IT IS A GATE HERE

MAAOA's entire grading was voided because a control's fixture was a live
artifact of the run it was grading. **A1WR came within one converged point of
the same fate and nobody knew.** `a1wr_read.py:447-457` *prefers* a live
artifact: it scans the run's own `sweep.log`, takes the first segment
classifying `CONVERGED` **and** carrying a y+ line, and uses it as the control
base. It fell back to its synthetic fixture **only because no point in either
arm converged**. Had one converged, the grading would have carried the defect.

*(A second, smaller defect in the same path, reported for the successor's
reader: A1WR's provenance line prints `source: no sweep log on disk yet` while
parsing a 520,063-byte sweep log four lines later — the `not is_file()` branch's
note reused for the "log present, nothing converged" case.)*

**REGISTERED: this item's reader takes its control fixtures ONLY from static
bytes committed with the reader, and refuses at exit 2 if any fixture path
resolves inside this item's run root.** The provenance line must state the
fixture's origin and its sha256, and must be true about the disk.

Per `CLAUDE.md` rule 3, every reader that can return a zero or an absence is
driven with a live planted perturbation on the static fixture, read back through
the **real** reader function, refusing at exit 2 if the reader cannot see it —
and **every control reads the target bytes before mutating, asserts the bytes
actually changed, drives the real reader, asserts the verdict flipped, restores,
and re-asserts the restore landed.** A no-op mutation followed by a passing check
is a control that proves nothing (A1WR §10).

**And the control that this item's own §3.2 anchor demands:** the convergence
channel must be shown able to read a **real** `Minimal residual … satisfied the
prescribed tolerance 1e-08` off real bytes, not only off a fixture. Three such
logs exist on this box and are named in `A1WR_STAGE12_RESULTS.md` §3.2, one of
them on this very mesh, image and solver.

---

## 7. WHAT THIS ITEM MAY NOT CONCLUDE

- **`FEASIBILITY`.** The L3 family has no Roache triple. **No value carries a
  band, none is grid-converged, and `PASS` against a threshold is unavailable**
  on any physical quantity. Ceiling `GATE REACHED`.
- **NO STALL ANGLE IS REPORTED AND NONE MAY BE DERIVED.** `G-STALL` refuses at
  exit 2 on any output binding such a word to a numeric angle. **The tail is
  exactly where that temptation lives**, which is why the gate is carried here
  unweakened.
- **A non-converged point is not evidence of separation** — it is evidence that
  the steady solver stopped converging, reported with its residual history.
- **A converged high-α point is not evidence of attached flow.** 2-D steady RANS
  with SA past the onset of significant separation is not a valid model of the
  flow at **any** resolution.
- **⚠ REGISTERED AS A KNOWN PROPERTY OF THE `symmetry` CONFIGURATION, NOT AS AN
  EXPECTATION — AND IT IS WHY THE PATCH IS REPAIRED. U1 (`symmetry`) WILL READ
  `NOT CONVERGED`. U2 AND U3 (`empty`) ARE EXPECTED TO CONVERGE.**

  The mesh's two bounding planes are **`type symmetry`, not `empty`** — measured
  in `constant/polyMesh/boundary`, 130,304 faces each — so OpenFOAM reports
  **`Mesh has 3 solution (non-empty) directions (1 1 1)`** and assembles a
  **z-momentum equation on a mesh one cell thick**. `U2` therefore floors instead
  of converging. Measured on `A1WR sweep_I` across all 559 print steps:

  | channel | minimum `initRes` reached, whole run |
  |---|---|
  | U0 | 1.429824e-09 |
  | U1 | 1.738461e-09 |
  | p | 2.589369e-09 |
  | nuTilda | 8.288244e-09 |
  | **U2** | **3.238410e-08** |

  **Every channel but `U2` gets below 1e-8. `U2` never does.** It is the largest
  last-iteration residual at **12 of the 14** points, and its floor of
  **3.238e-08 sits ABOVE the registered `primalMinResTol = 1.0e-8`.**

  **So A1WR's thirteen points could never have converged, and neither can U1's.
  That is arithmetic, not a forecast.** Corroborated on `MAAOA INCOMP`
  (`U2` 2.48e-08) and on the coarse 4,032-cell mesh (~1.7e-10, i.e. the floor
  scales with the mesh); killed for the compressible arm, where `p` at 9.29e-01
  dominates and the mechanism is the separate one N-C9 documents.

  **AND THE OTHER HALF OF THE MECHANISM, READ FROM THE INSTALLED SOURCE RATHER
  THAN INFERRED — IT IS WHY THE LEDGER SAID `err=NONE` WITH ZERO CONVERGENCES.**
  `DASolver.C:188` stops early only when `primalMaxRes < primalMinResTol`
  (1.0e-8). `DASolver.C:2745` raises `Primal solution failed!` only when
  `primalMaxRes / primalMinResTol > primalMinResTolDiff`, and this item's
  registered `primalMinResTolDiff` is **100** — i.e. only above **1.0e-6**.
  **There is a deliberate 100× DEAD BAND between the two thresholds, and the
  measured floor of 3.238e-08 sits inside it** — 3.24× the tolerance, 0.0324× the
  failure threshold. **A1WR's arm I could neither converge nor be flagged as
  failed. That is the whole explanation of the "13 clean rows, all `error NONE`"
  that had zero convergences**, and it is registered here so this item's reader
  cannot repeat the misreading.

  **⚠ WITHDRAWN, AND THIS WOULD HAVE COST 288 CORE-MIN TO LEARN THE OTHER WAY.**
  An earlier version of this clause registered that the `empty` units are
  *expected to converge*, because removing the z-momentum equation removes the
  `U2` residual that floors. **That premise is FALSE, and the source says so.**

  `primalMaxRes` is **not** the max over the velocity components. For vector
  fields `DAUtility.C:762-790` **sorts the three components and takes the
  MEDIAN**, and the source comment says it exists precisely *"because we often
  need to run 2D simulations with symmetry BC, so one component of the residual
  vector … may be high while the other two components' residuals are low."*
  So `primalMaxRes` = max( **MEDIAN**(U0,U1,U2), p, nuTilda ), and **`U2` never
  entered the convergence criterion at all** — from α = 2 upward it is the
  *largest* of the three and the median discards it.

  **MEASURED on A1WR, the binding channel is `nuTilda` at 8 of 14 points and the
  median-of-`U` at 6. `U2` binds at NONE.** Projecting the `empty` case by
  removing `U2` from the median gives `primalMaxRes` of **1.02e-08 … 2.80e-07
  across α 1…13 — every value still ABOVE 1.0e-8**, the closest being α = 1 at
  1.0182e-08, a factor of 1.02.

  **REGISTERED, THEREFORE: U2 AND U3 ARE EXPECTED *NOT* TO CONVERGE EITHER.**
  The patch repair is still correct — a `symmetry` bounding plane on a one-cell
  mesh is a genuine defect and assembling a spurious equation is wrong whatever
  the residual bookkeeping does with it — **but it must NOT be sold as the thing
  that makes the solve converge.** It is not.

  **The honest projection is registered as a projection**: it assumes the other
  channels are unchanged by the patch swap, which they will not be exactly, since
  removing an equation changes the coupled system. The margins are factors of
  1.02–28, not orders, so the swap alone is very unlikely to drop every channel
  below 1e-8. **If the `empty` units DO converge, that is a finding about the
  coupling and is reported as one** — it is not the outcome this document
  predicts.

  **AND THE CLAUSE THAT MATTERS MOST: none of this licenses relaxing anything.**
  It does not license raising `endTime`, **it does not license relaxing 1.0e-8 to
  1e-7 to manufacture a convergence**, it does not license widening
  `primalMinResTolDiff`, and it does not license re-tuning. A successor reading
  this page will reach for exactly one of those; each is result-shopping, all are
  forbidden on this item, and a different tolerance or iteration budget is a
  **NEW rung with its own pre-registration.** **The repair is to the mesh's patch
  identity — a defect — and to nothing else.**

- **`G-REPRO` KEEPS ITS VALIDITY BECAUSE U1 KEEPS A1WR's CONFIGURATION.** U1 runs
  on `symmetry`, cold, with the frozen numerics unchanged, so the cold-vs-
  continued comparison against A1WR's own continued α = 12 moves exactly one
  variable. **The patch repair does not contaminate it, because the repair lives
  in U2, and U1-vs-U2 is the separate one-variable pair that measures the repair
  itself** (§3.5). That is what the eighth point buys.

- **REGISTERED CONSEQUENCE, NOW SPLIT BY UNIT BECAUSE THE UNITS DIFFER:**
  **U1's** coefficients are an iteration-4,000 state on a configuration with a
  measured residual floor of 3.238e-08 and **may not be presented as a converged
  value** — only its extrapolated plateau, labelled EXTRAPOLATED, enters §3.5.
  **U2 and U3's** coefficients may be presented as converged **only if the solver
  actually printed its own `Minimal residual … satisfied the prescribed
  tolerance 1e-08` line for that point**; a point that instead ran to the cap is
  `NOT CONVERGED` like any other, expectation notwithstanding. **`G-NOBAND`
  independently forbids presenting ANY value of this item as grid-converged or
  inside a band** — the L3 family still has no Roache triple. **The two
  prohibitions are separate and both bind.**
- **No adjoint claim.** Primal only, undeformed geometry, no optimiser, no trim.
- **The build confound stands and is restated:** the coarse sweeps ran the
  SHIPPED image, this and A1WR run the PATCHED `dafoam-idwarp-rot:v1`.

---

## 8. OWED BEFORE FREEZE

1. **Supervisor's §3 check 4, personally**: the §4.3/§4.4 cap arithmetic and the
   §3.3 reproduction-control bands, read as arithmetic and not as a summary.
2. The driver, run-script staging and **reader** written, with `G-COMPLETE` and
   `G-CAPS` implemented **in this item's reader** (§5) and `G-FIXTURE` enforced
   (§6), every control driven and its selftest passing, then md5-pinned by the
   freeze. *(Implemented in the reader for auditability, NOT because A1WR lacked
   them — §5.1 withdraws that claim.)*
3. Run root `/home/ubuntu/certonomous-runs/A1WRT/` re-checked absent **in the
   freezing shell**.
4. Mesh, image and instrument md5s re-verified against the A1WR manifest in that
   same shell.
5. Queue entry drafted so the run is durable by construction — the deadline lives
   **inside the container**, so the cap stops the run even if the driver, the
   daemon and every agent die. **A1WR's own kill is the argument: the driver was
   polling healthily at 02:24:58Z and the box went down seven seconds later.**

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---

**Drafted 2026-09-03 by lab-lane (dafoam). No solver, container or queue entry
was launched, released or moved. Every figure above is read from an artifact
named beside it.**
