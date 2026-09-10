# SUBOFF R1 — RUN VERDICT: `NOT A RESULT` (cap-stop on incompleteness)

**Rung:** DARPA SUBOFF bare hull, zero incidence, total-drag parity.
**Pre-registration:** `verification/campaign/SUBOFF_R1_PREREGISTRATION.md`, **FROZEN at `94d7afb7`**.
**Verdict by:** cfd-supervisor, 2026-09-10, from artifacts on disk.
**Verdict: `NOT A RESULT`.** No gate was evaluated. Gate D1 (total-drag parity, CT ±10%) was
never reached and **no CT value is quoted from this rung.**

---

## 1. WHAT HAPPENED, MEASURED

| level | cells | registered endTime | reached | rc | ClockTime | core-min |
|---|---|---|---|---|---|---|
| `reg_coarse` | 39,904 | 2500 | **1445** | **124** (cap-stop) | 900 s | **15.000** |
| `reg_medium` | 89,784 | 2500 | **311** | stopped by supervisor | 441 s | **7.350** |
| `reg_fine` | 202,014 | 2500 | **never started** | — | — | 0 |

`reg_coarse` exhausted its registered 900 s / 15 core-min sub-cap at iteration 1445 of 2500.
It has **no `End` line and `last time != endTime`**, so it fails the strict completion rule and
is not gradeable. **A Roache triple requires three complete levels; one incomplete level makes
the triple impossible regardless of what the other two do.** That is why the rung is
`NOT A RESULT` and not `GATE FAIL`: no gate was ever read.

**Total spend: 22.35 core-min gross = cleaned** (no level near the 3600-s stall rule),
**$0.0191 DERIVED, NOT MEASURED** at $0.0513/core-h (the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). **All 22.35 core-min is waste** — it produced no gate reading —
and is **named separately, never absorbed into a ratio.**

## 2. TRIAGE — THE CAUSE IS CONTENTION, AND IT IS MEASURED

Throughput, normalised for cell count so the two are comparable:

| source | cells | iters | wall s | cell-iter/s |
|---|---|---|---|---|
| `smoke_coarse` (the registered cost basis) | 7,600 | 50 | 2.21 | **1.719e5** |
| `reg_coarse` ACTUAL | 39,904 | 1445 | 900 | **6.407e4** |

**The box delivered 2.68× less throughput than the registered basis predicted.** Because
per-cell cost should *fall* on larger meshes as fixed overheads amortise, **2.68× is a FLOOR on
the contention effect, not a ceiling.**

**Attribution: CONTENTION, not a misprediction of the physics and not a defect in the rate
methodology.** The rate was correctly measured *within configuration* — `smoke_coarse`'s
`fvSolution`/`fvSchemes` are byte-identical to the graded levels — but it was measured on a
lightly-loaded box and then applied to one carrying 8+ concurrent solvers. **The methodology was
right and the operating condition was not stated.** That is the transferable lesson.

**What completion would actually have cost.** At the measured contended rate, `reg_coarse` alone
needs **26.0 core-min against its 15 allocated**; scaled by cells the triple needs **~216
core-min against the frozen 150 cap** — **2.69× the registered 80.38 estimate**, which matches
the measured 2.68× contention factor almost exactly. **The entire miss is contention; nothing
else needs to be invoked.** The registered cap could never have delivered the registered
`endTime` under these conditions.

## 3. THE RUN WAS STOPPED DELIBERATELY, AND WHY

I stopped the chain (pids 1115918, 1115920, 1131125, and its watcher 1135130) rather than let
medium and fine run to their own sub-caps. **The triple was already unrecoverable**, so the
remaining ~107 core-min would have bought a guaranteed `NOT A RESULT` on a box the lab needs for
work that can produce results. `CLAUDE.md` rule 12 is explicit that an overrun stops the run and
does not get a new budget. **The freeze is not reopened and the cap is not extended mid-run** —
the path forward is a successor registration, not a rescue.

## 4. TWO DEFECTS OF MY OWN, RECORDED

1. **The launch could never have produced a verdict.** `run_suboff_r1_triple.sh` grades only
   under `--grade`, and the queue entry I placed did not pass it. Had the triple completed with
   no agent alive, it would have produced **no verdict at all**. Caught only because the
   survivability audit read the launcher rather than trusting that a launched run grades itself.
2. **The cost basis was single-tenant and I accepted it.** I checked that the rate was measured
   within-configuration and did not ask *under what load*. A rate is not a property of a case
   alone; it is a property of a case **on a box in a state**, and the state belongs in the
   registration.

## 5. WHAT IS AND IS NOT CARRIED FORWARD

**Carried forward unchanged into the successor:** the gate and its ±10% band, the CT anchor
3.6e-3 and its MANIFEST / BOUNDED-AGREEMENT status, `reference.Aref` = 0.0831703362813915 m²,
the analytic wetted area 5.988264212260189 m², the three-level family (39,904 / 89,784 / 202,014
at exactly 2.25×), the ≤70°/≤4 admission gates, and the grader. **NO GATE, THRESHOLD, BAND OR
LABEL MOVES.** The successor re-registers **the compute budget only**, from the measured
contended rate.

**Not carried forward:** the 80.38 core-min estimate and the 150 core-min cap, both of which are
now known to be unreachable for `endTime` 2500 under contention.

**The mesh work stands and is not re-done.** All three levels are built, `checkMesh`-clean and
admissible (non-orth 57.405 / 63.602 / 68.706, skew 1.654 / 1.900 / 2.123, `Mesh OK`, zero severe
faces, zero negative volumes), with geometric similarity read back from the built mesh. **None of
that is invalidated by a budget miss** — the successor inherits the meshes as they stand.

*Verdict record for a FROZEN pre-registration, citing it by commit hash `94d7afb7`. This record
is appended to, never edited.*

---

## ADDENDUM 2026-09-10 — §2's "FLOOR ON CONTENTION" CLAIM IS WITHDRAWN AND NARROWED

**Appended, not edited (this record is append-only). No verdict changes: SUBOFF R1 remains
`NOT A RESULT`, and no cost figure moves.**

**What is withdrawn.** §2 asserts: *"Because per-cell cost should fall on larger meshes as fixed
overheads amortise, 2.68× is a FLOOR on the contention effect, not a ceiling."* **That reasoning
does not hold and I withdraw it.** Two grounds, both from a second lane's measurement:
1. **The rates are already incremental** — taken between the first and last `ExecutionTime` line —
   so there is little fixed overhead left to amortise. The amortisation argument has nothing to
   act on.
2. **Working-set size runs the OTHER way.** At 7,600 cells the smoke is plausibly last-level-cache
   resident; at 39,904 cells it is not. **Part of the 2.68× is therefore a mesh-size/cache-exit
   effect that would appear on an IDLE box too.**

**So 2.68× is a floor on the smoke→regression degradation, NOT cleanly on contention alone.** The
contention/cache-exit split **is not separable from these artifacts** and no bandwidth counter was
read. Stated as an absence rather than papered over.

**What is CONFIRMED, and it is stronger than what I withdrew.** Two contended points now exist:

| level | cells | iters | wall s | s per cell-iteration |
|---|---|---|---|---|
| `reg_coarse` | 39,904 | 1,443 | 896 | **1.556056e-05** |
| `reg_medium` | 89,784 | 309 | 433 | **1.560740e-05** |

**They agree to 0.30 % across a 2.25× change in cell count.** Per-cell cost is **flat at regression
scale**, so the two points sit on one plateau rather than disagreeing about a contention factor —
and extrapolation to the unrun 202,014-cell level is **measured-supported, not assumed.** This is
the more useful result and it is what the successor's budget is built on.

**The mechanism is also narrowed, and it is NOT scheduler starvation.** The solver held **96.2 %
(coarse) and 99.0 % (medium) of one core**; 10 processes ran at ≥96 % CPU on `nproc` = 16, so the
box was **not CPU-oversubscribed**, and the load average of 35.5 is inflated by
uninterruptible-sleep tasks. The loss is **extra CPU-seconds per cell-iteration** — the signature
of shared memory-bandwidth / cache contention. **INFERRED**; no bandwidth counter was read.

**Consequence for the successor:** its budget is built on the **directly measured contended rate**,
never on a factor applied to the smoke rate — so nothing downstream depended on the withdrawn
claim. A companion correction row is appended to `docs/COST_CALIBRATION.md`.

**One methodological note carried forward.** The smoke's `ClockTime` is 0→2 s at 1-second
granularity and is **under-resolved**; only its `ExecutionTime` (0.09→2.21 s) is usable. A
wall-basis smoke comparison reads 2.90× and **would be a granularity artifact**.
