# K2h — the rack-row module graded TRANSIENT, because the physics voted unsteady: PRE-REGISTRATION

**Rung:** `K2h`. **Family:** F14 cooling ladder. **Successor to:** `K2g`, whose L3
is `NOT A RESULT`. **Status:** frozen at its commit; nothing below may change
afterwards except as a dated addendum that cannot alter a gate, threshold, cap or
label (`CLAUDE.md` rule 2).

**No compute has been spent against this document.**
`verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3` does not exist at the
moment of this freeze, and that is the condition under which amendments to this
draft were legal (rule 2, first bullet). The condition was checked by listing
`verification/runs/F14-cooling-ladder/` and finding no `K2h_runs`.

---

## 1. WHY THIS RUNG EXISTS — A STOP RULE FIRED AND IT WAS RIGHT

K2g's L3 ran 303 iterations from its t=500 checkpoint and was stopped at
iteration 802 by its own registered stop rule R4, through OpenFOAM's `abort`
function object with `action writeNow` — a clean stop, `rc=0`, no rank killed,
23.431 core-min spent. The recorded reason, from
`K2f_L3/STOP_RULE_FIRED.R4.txt`:

> COHERENT OSCILLATION in the graded quantity: 7 sign changes over 300
> iterations, peak-to-peak 0.02802 m²/s². PHYSICS VOTING UNSTEADY — a steady
> SIMPLE solve is the wrong instrument for this state.

K2g's L3 is `NOT A RESULT`: the frozen comparator refused at exit 2 on rule 4
clauses 3 and 5 (`last written time 803 != endTime 2000`; `803 ExecutionTime
lines, expected 2000`). **That refusal is not repaired here and is not appealed.**
This document registers the successor the stop rule's own text names: the same
module, solved with an instrument that can represent the state.

---

## 2. THE MEASUREMENT THAT DECIDES THE FAMILY, MADE BEFORE THIS FREEZE

My supervisor raised a live possibility that would make a mixed triple worse than
inelegant: **that L1 and L2 are "steady" only because they are too coarse to
resolve the unsteadiness.** It was tested rather than assumed, on the two
levels' own artifacts, against the same tests R4 applied to L3.

**(a) Per-iteration initial residuals, final 300 iterations — NOT aliased:**

| level | `Ux` sign changes / p2p | `p_rgh` sign changes / p2p | reading |
|---|---|---|---|
| `K2f_L1` | 296 / **5.05e-11** | 289 / **6.43e-09** | flips are *jitter at 1e-11*; the solve is dead flat |
| `K2f_L2` | **8** / 6.69e-05 | **19** / 6.55e-04 | a genuine LOW-FREQUENCY LIMIT CYCLE at a 1e-4 floor |
| `K2f_L3` | — | — | R4: 7 sign changes / **2.80e-02** in Δp over 300 iterations |

**(b) `DP_module` at every checkpoint, through the frozen
`foam_patch_reader.area_average`:**

| level | t=500 | t=1000 | t=1500 | t=2000 | t=2500 | t=3000 | sign changes | p2p |
|---|---|---|---|---|---|---|---|---|
| `K2f_L1` | 27.189431 | 27.189120 | 27.189119 | 27.189119 | 27.189119 | 27.189119 | **0** | **3.11e-04** |
| `K2f_L2` | 27.732036 | 27.729909 | 27.729578 | 27.728333 | 27.728510 | 27.729680 | **1** | **3.70e-03** |

**THE ANSWER, AND IT IS SPLIT.** `K2f_L1` is **genuinely stationary** — its
residuals sit at 1e-10 and its Δp is monotone to 3e-04. `K2f_L2` is **NOT**: its
residuals limit-cycle at a 1e-4 floor (which K2g §4.2 already recorded in the
word "limit-cycles" and admitted deliberately), and its Δp **turns**, one sign
change with p2p 3.70e-03. The Δp amplitude grows **3.11e-04 → 3.70e-03 →
2.80e-02**, roughly an order of magnitude per level, which is the signature of an
unsteadiness being **progressively resolved by refinement** rather than created
by it.

**THE LIMIT ON (b), STATED BECAUSE IT CUTS AGAINST THE COMFORTABLE READING.** L1
and L2 carry no Δp monitor, so their only Δp series is six checkpoints 500
iterations apart. L3's oscillation shows ~7 sign changes per 300 iterations —
a period near 85 iterations. **A 500-iteration sample aliases that completely.**
Table (b) therefore cannot exclude an L3-like oscillation at L1 or L2; only the
un-aliased residual series in (a) can, and it excludes it at L1 and finds it at
L2.

---

## 3. THE DISCLOSURE THAT GOVERNS EVERY REPORT OF THIS RUNG

> **A triple whose L1 and L2 are STEADY `DP_module` and whose L3 is
> TIME-AVERAGED `DP_module` IS NOT A ROACHE TRIPLE OF ONE DISCRETISATION.** It is
> two different quantities on one axis: a fixed point of a steady operator, and a
> time mean of an unsteady one. **No observed order and no GCI may be quoted from
> such a mixture, ever, in any record, figure or narration** — not with a caveat,
> not with a footnote. Disclosure does not convert it into a refinement study; it
> only tells the reader what they are looking at.

The same reasoning retired T26's mixed-topology triple and is not abandoned
because a mixed version would be quicker to film. §2 makes it sharper than a
matter of taste: **L2's steady value is already a single time-slice of a
non-stationary state**, so the mixed triple's middle point is not a converged
fixed point at all.

**THE PREFERRED FAMILY IS ALL THREE LEVELS TRANSIENT AND TIME-AVERAGED, and it is
affordable.** L1 and L2 cost 13.267 and 64.000 core-min steady, so their
transient cost is bounded by the same ratio this document registers for L3.
**`K2h_L3` is registered here and launched first; `K2h_L1` and `K2h_L2` are
registered as the completion of the family and are sequenced behind it.** Until
all three exist, this rung reports **one level and no triple.**

---

## 4. THE CASE

**Solver: `buoyantBoussinesqPimpleFoam`.** It is the transient sibling of
`buoyantBoussinesqSimpleFoam` — same Boussinesq buoyancy, same `kOmegaSST`, same
equation set — so the *only* thing that changes between K2g and K2h is the time
treatment, which is the one thing that must change. **It is also proven on this
exact module**: `K2b_runs/K2bU3R3_D59` ran it on the identical
`(0 0 0)-(3.6 3.5 2.7)` domain (verified from both cases' `log.checkMesh`). No
other solver was considered a better fit and none is available that keeps the
equation set fixed.

**Mesh: the 664,848-cell L3 mesh, REUSED BIT FOR BIT** — `constant/polyMesh`
copied from `K2g_runs/K2f_L3`, which the frozen `build_k2f.py` built and whose
cell count and every patch face count `M-REPRO` already checked against the
independently built retired K2d_L3 mesh. Nothing is re-meshed.

**Initial fields: the `803` checkpoint**, `K2g_runs/K2f_L3/processor*/803`,
verified intact on all four ranks. They are copied into the new case's
`processor*/0`, preserving the decomposition, so no `reconstructPar` runs and no
interpolation touches the field. The steady solve's 803 iterations are therefore
**spent, not wasted**: they are this run's initial condition.

**Boundary conditions, properties and schemes** are inherited unchanged from
K2g/K2f by citation, except `ddtSchemes`, which becomes `Euler` (first-order
implicit, the scheme K2b used on this module).

---

## 5. THE SETTLING PERIOD AND THE AVERAGING WINDOW — FROZEN, WITH WHAT SETS THEM

Both are fixed here, before the run. **A window chosen after seeing the answer is
not a window.**

**The timescale, from two independent anchors that agree.** The module's
own convective time is `L/U` = 3.6 m / 0.524 m/s = **6.9 s**, taking `U_ha`
= 0.5242578 m/s from K2g §2's measured table. Independently, `K2bU3R3_GRADE.txt`
records the 2D limit-cycle period on this module as **6.000 s**. The two agree
to 15 %, and the registered characteristic period is **T\* = 7.0 s**, the larger
and therefore the conservative one.

> **`S-SETTLE` — settling period: 0 → 42 s** (= 6 T\*). The initial condition is
> a steady fixed point, not an arbitrary field, so the transient has only to
> shed the steady operator's artefacts, not develop the flow from rest. Six
> characteristic periods is the interval over which `K2bU3R3`'s own preceding
> window (40–60 s) had already reached its final-window behaviour.
>
> **`S-WINDOW` — averaging window: 42 → 112 s** (= 10 T\*, 70 s).
> **Why ten and not three:** the quantity being averaged has a measured
> peak-to-peak of 2.80e-02 m²/s². Averaging a periodic signal over N whole
> periods leaves a residual bias of order p2p/(2πN); at N = 10 that is
> **4.5e-04 m²/s²**, which is **1.5 % of the ±0.030 prediction tolerance in §7**
> and so cannot decide the gate. At N = 3 it would be 1.5e-03, five times
> larger and still small — ten is chosen to make the window's own contribution
> negligible rather than merely acceptable, and because a non-integer number of
> periods is the realistic case.
>
> **`E-ENDTIME` — `endTime` 112 s.** The graded value is read at `endTime`.

**`S-ACCUM` — the accumulator is checkpointed with the fields** (Sanaa's item 3).
`fieldAverage` is declared with `restartOnRestart false` — OpenFOAM's default,
declared explicitly so a reader does not have to infer it — and
`writeControl writeTime`, so the running means are written into every time
directory and a restart resumes the average instead of discarding it. **A
`restartOnRestart true` anywhere in `system/` refuses the launch** (it is also
`queue_runner.py` gate A limb (iv)).

---

## 6. THE GATE

> **`G-DPBAR`.** `DPbar` = the time average over `S-WINDOW` of
> `DP_module` = areaAvg(`p_rgh`, `tile`) − areaAvg(`p_rgh`, `return`),
> read at `endTime` from the `fieldAverage` output through the **frozen**
> `foam_patch_reader.area_average`.
>
> **`DPbar` ∈ [27.9699, 28.0901] m²/s² → `PASS`; outside → `GATE FAIL`;**
> a level failing `D-COMPLETE` or `D-STATIONARY` → **`NOT A RESULT`.**

**The band is K2g §5's `G-DP` band, carried over UNCHANGED and not re-derived.**
It is the interval implied by an observed order in [1.0, 2.0] on the existing
f1 and f2, and re-deriving a band on a new document would be choosing one after
seeing 28.0521 — which §7 registers as a losable prediction instead.

**`D-STATIONARY` — the window must be a window, not a trend.** The mean over the
first half of `S-WINDOW` and the mean over the second half must differ by
≤ **5.0e-03 m²/s²** (= 0.18 × the measured p2p). A run still drifting across its
own averaging window has not reached a statistically stationary state and its
mean is `NOT A RESULT`.

**`D-COMPLETE`** — rule 4, adapted to a transient and stated so no reader has to
guess which reading applies: `rc = 0`; one `End`; **last written time ==
`endTime` 112**; fields `T U p_rgh alphat nut k omega phi` present at `endTime`
**plus the `fieldAverage` means**; and **every field at `endTime` newer than the
case's own `0/T`** (the age guard). The `ExecutionTime`-count clause of the
steady rule **does not apply**: `deltaT` is adaptive, so the registered form is
`n_exec == number of time steps written to the log`, per `CLAUDE.md` rule 4's
own adaptive-`deltaT` clause.

---

## 7. REGISTERED PREDICTIONS — LOSABLE, AND SCORED EITHER WAY

* **`P-K2h-1` — the value.** `DPbar` = **28.052 m²/s²**, ±0.030. It is the
  steady solve's last instantaneous value at iteration 803 (28.0521393, from
  `MONITOR.K2f_L3.tsv` col 15), predicted to survive time-averaging because the
  oscillation is symmetric about its mean. **This can lose**: if the oscillation
  is asymmetric the mean will sit away from that instant, and the 300-iteration
  window's own mean was 28.0625 — 0.010 higher, a third of the tolerance.
* **`P-K2h-2` — stationarity.** `D-STATIONARY` **passes**; half-window means
  differ by < 5.0e-03.
* **`P-K2h-3` — the verdict.** **`PASS`** (28.052 is inside [27.9699, 28.0901]).
* **`P-K2h-4` — the period.** A dominant period is extractable from the `DPbar`
  series and lies in **[4, 12] s**, bracketing both anchors in §5.
* **`P-K2h-5` — the cost.** **420 core-min ± 50 %**, i.e. 210–630.

---

## 8. COST — RULE 12, COSTED BEFORE COMPUTE

**Measured basis, from this rung's own predecessor on the same mesh and the same
box:** K2g's L3 ran **303 iterations in `ExecutionTime` 342.18 s at 4 ranks**
(`STATUS.K2f_L3`) = **1.129 s per SIMPLE iteration**, on an uncontended box.
That is a far better anchor than K2g §8's 17.944 core-s/iteration, which was
measured at load 68, and it is reported as superseding it **for this rung only**.

| term | value | basis |
|---|---|---|
| steady iteration | 1.129 s | **measured**, `STATUS.K2f_L3` |
| PIMPLE step / SIMPLE iteration | ×2.5 | **estimated** — outer correctors; not measured on this mesh |
| mean `deltaT` | 0.0475 s | **estimated** — K2b's measured 0.0804 s at 137k cells, scaled by the linear refinement ratio (664848/137000)^(1/3) = 1.69 |
| steps to 112 s | 2358 | derived |
| wall | ~6650 s | derived |

**POINT: 420 core-min.** **Registered cap: 1260 core-min (3×).** **PER SANAA'S
2026-09-12 04:20Z DIRECTIVE #17 THE CAP IS A FLAG AND NOT A STOP** — no wrapper
kills this run on it; a crossing writes `CAP_FLAG.txt` and the verdict
consequence is decided at grade time. Raising or retiring a cap is Sanaa's alone.
**$0.36 at POINT** (7.0 core-h × $0.0513/core-h), **derived at an owner-stated
rate, reported-by-owner and NOT MEASURED** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). Under $25.

**Two of the four terms above are estimates, not measurements**, and the ±50 %
band exists because of them. The first completed run replaces both, and the
estimate-versus-actual row lands in `docs/COST_CALIBRATION.md` per rule 12.

---

## 9. CHECKPOINTS — SANAA'S ITEMS 1–3, SIZED FOR THIS RUN AND NOT INHERITED

`writeControl adjustableRunTime; writeInterval 5;` — every **5 s** of simulated
time. At the projected 2.82 s wall per step and 0.0475 s mean `deltaT`, 5 s is
~105 steps ≈ **296 s ≈ 5.0 minutes** of wall, inside the 30-minute bound with a
6× margin, and the bound still holds if the projection is wrong by 5×.
`endTime` 112 is **not** a multiple of 5, so `E-ENDTIME` also registers
`writeInterval 5` **with `endTime` 112 reached by `adjustableRunTime`, which
writes at `endTime` regardless** — and the launcher asserts a time directory at
112 exists before grading, refusing otherwise.

`purgeWrite 16`. **The trap this rung already paid for:** a retention that
deletes a registered grading input refuses the comparator *after* the spend.
`D-STATIONARY` needs the window's two halves, so the run must retain from
**t = 42** to **t = 112** = (112−42)/5 + 1 = **15 writes**; 16 is that with one
slot of margin, at ~122 MB per write ≈ **2.0 GB**.

---

## 10. ORDER OF OPERATIONS — BINDING ONCE FROZEN

1. This document is committed. **Nothing is staged or run before the commit
   exists.**
2. `K2h_L3` is staged: `constant/polyMesh` copied from `K2g_runs/K2f_L3`,
   `system/` written with the transient dictionaries, `processor*/0` copied from
   `K2g_runs/K2f_L3/processor*/803`, `0.orig/` from K2f_L3's `0.orig`. **No `0/`
   is created at staging** — it is armed at launch, so it dates the run for the
   age guard.
3. The queue entry is validated read-only and handed to the supervisor.
   **Placing it in `verification/queue/heat-transfer/` is the launch and is not
   this lane's act.**
4. The runner launches it. Monitor and autograder detached, parented to init.
5. Grading: `D-COMPLETE`, then `D-STATIONARY`, then `G-DPBAR`.

**Exit map:** 0 OK, 1 GATE FAIL, 2 REFUSE, 3 NOT A RESULT. **No verdict may be
read from an exit code**; the verdict is the word the comparator prints.

*Nothing in this rung is sent, filed, uploaded, registered, posted or commented
outside this box (rule 7).*

---

## 11. FREEZE BLOCK — sha256 OF THE DISK BYTES OF EVERY FILE ON THE GRADING PATH

The comparator re-reads this block at grade time and **refuses if any file on
disk is not the file pinned here**. This document's own hash is not in the table:
it is the table.

```json FREEZE
{
 "verification/runs/F14-cooling-ladder/K2g_runs/foam_patch_reader.py": "f3ee1fcf6d971724613a899d90b8cc654bf5d341794ae00a042193e678d06e03",
 "scripts/roache_triple.py": "fcae041ffb22c48735cbd6b045507818802f504eda503adf612ae2a581aa79d8"
}
```

**`foam_patch_reader.py` is REUSED UNCHANGED from K2g**, at the identical
sha256 — the same reader that produced f1 and f2 reads this level, so the
"one reader, every level" discipline of K2g §4 survives the change of solver.
`roache_triple.py` is pinned because it will grade the completed transient
family; **it is not used on a mixed triple, which §3 forbids outright.**
`analyse_k2h.py` and the launcher are written against this document after the
freeze and are pinned by the commit that adds them, in the manner of K2g's
`launch_k2g.sh`.

---

## AMENDMENT 1 — 2026-09-12, PRE-COMPUTE: R4 SUSPENDED FOR TRANSIENT LEVELS, BECAUSE IT WOULD STOP THIS RUN FOR DOING EXACTLY WHAT IT IS FOR

**Version 1.0 → 1.1. This is a PRE-COMPUTE AMENDMENT under `CLAUDE.md` rule 2,
first bullet — not a post-freeze addendum.** Appended at the foot so that **lines
whose number changed above this section: 0**.

**THE CONDITION, AND HOW IT WAS CHECKED.** No compute has been spent against this
document. Checked by listing
`verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3`, which contains **only
`system/`** (four dictionaries). **ABSENT, each named and each verified absent:**
`K2h_L3/0`, `K2h_L3/log.solve`, `K2h_L3/processor0`, `K2h_L3/postProcessing`,
`K2h_L3/PIDS.solver` and `K2h_runs/STATUS.K2h_L3`. No solver has started, so
amendments are legal and gates are still open.

**NOTHING BELOW ALTERS A GATE, A THRESHOLD, A BAND OR A LABEL.** §5's
`S-SETTLE` 0–42 s and `S-WINDOW` 42–112 s stand; §6's `G-DPBAR` band
[27.9699, 28.0901] m²/s² stands; §6's `D-STATIONARY` 5.0e-03 m²/s² and
`D-COMPLETE` stand; §7's five predictions stand; §8's POINT 420 / cap 1260 stand.
Only the **run-control stop rules** change.

### A1.1 The defect being repaired, stated as physics

Monitor rule **R4 fires on coherent oscillation in the graded quantity and stops
the run.** On K2g's steady L3 that was correct and it is why this rung exists. **On
a transient level it would be a FALSE STOP: a coherently oscillating `DP_module`
is the signal this rung is built to measure, not a fault.** R4 would very likely
fire inside the settling period and end the run before `S-WINDOW` opened.

> **R4 IS SUSPENDED FOR TRANSIENT LEVELS ONLY. IT REMAINS IN FULL FORCE FOR
> STEADY LEVELS.** Nothing here retires the rule that produced tonight's finding;
> a steady solve whose graded quantity oscillates coherently is still being
> measured by the wrong instrument and still stops.

### A1.2 What stops this run instead — replaced, not removed

A level with no stop rule is worse than one with a wrong rule. **Armed for
`K2h_L3`, all three detectable by `monitor_k2g.py` as written:**

| rule | condition | detectable? |
|---|---|---|
| **R1** residual growth | mean(last 100)/min(last 400) > 2.0 on `Ux`, `T` or `p_rgh` | **YES** — per-step initial residuals, and a diverging transient rises exactly as a diverging steady solve does |
| **R2** field out of bounds | any non-finite (NaN/inf) residual, or \|`DP_module`\| > 1000 m²/s² | **YES** |
| **R3** dead linear solver | `DP_module` drift < 1e-5 over 500 steps **while** the `p_rgh` solver is at its iteration cap in ≥ 90 of the last 100 | **YES** — and on a transient it means the oscillation died *while* the pressure solve stalled, which is a fault and not settling |

**DESIRABLE AND NOT DETECTABLE by the monitor as written, named rather than
implied:** the `fieldAverage` accumulator failing to advance, and the window
average failing to stabilise. **The monitor reads the `dp_tile`/`dp_return`
function-object output and does not read the `fieldAverage` fields at all**, so
neither can be a run-time stop without editing the instrument, and the instrument
is not edited to make a rule true. **Both are covered at GRADE time instead, and
the coverage already exists:** §6's `D-STATIONARY` compares the two halves of
`S-WINDOW` and returns **`NOT A RESULT`** if they differ by more than 5.0e-03
m²/s², and §6's `D-COMPLETE` requires the `fieldAverage` means present at
`endTime`. The cost of that placement is honest and is stated: a non-stabilising
average is caught **after** the spend rather than during it.

### A1.3 How the suspension is delivered — additively, with the absence visible

`monitor_k2g.py` takes a new **optional 5th argument**, a comma-separated list of
rule ids to suspend, **defaulting to suspending nothing**. Every existing call
site, `resume_k2g.sh` included, keeps every rule with no change, and **nothing
about the K2g run this instrument already stopped is altered** — its
`ACTION_HISTORY.K2f_L3.tsv`, `STOP_RULE_FIRED.R4.txt` and `MONITOR.K2f_L3.tsv`
are on disk and untouched. `stage_and_run_k2h.sh` passes `R4`. The monitor writes
**`RULES_SUSPENDED.txt`** beside the case, so a reader sees the absence on disk
rather than inferring from silence that every rule was armed and none fired.
**The instrument is extended, never edited to say something different.**

### A1.4 Amending §3 with the sharper reason, in the words the measurement earns

§3's clause stands unchanged. **Its ground is strengthened, and §2's measurement
is what strengthens it:**

> **The Δp amplitude grows 3.11e-04 → 3.70e-03 → 2.80e-02 m²/s², roughly an
> order of magnitude per level. THE UNSTEADINESS IS BEING RESOLVED BY
> REFINEMENT, NOT CREATED BY IT** — a physics result about this module, and the
> honest headline of this rung.
>
> Therefore: **`K2f_L2`'s steady value is already a time-slice of a
> non-stationary state, so a mixed triple's MIDDLE point is not a converged
> fixed point either** — not only its finest. That is a stronger reason for the
> all-transient family than §3's original one and it replaces it as the
> governing reason.

**AND THE LIMIT, CARRIED WITH EQUAL WEIGHT BECAUSE SOMEONE WILL OTHERWISE QUOTE
THE SIX Δp SAMPLES AS EVIDENCE OF STEADINESS:** `K2f_L1` and `K2f_L2` carry no Δp
monitor. Their only Δp series is **six checkpoints 500 iterations apart**, against
an oscillation whose period is **~85 iterations**. That sampling **aliases the
signal completely.** The checkpoint table in §2(b) therefore cannot demonstrate
steadiness at either level and must never be cited as if it could; **only the
un-aliased per-iteration residual series in §2(a) can speak**, and it finds L1
dead flat at 5.05e-11 and L2 limit-cycling at a 1e-4 floor.

*Nothing in this rung is sent, filed, uploaded, registered, posted or commented
outside this box (rule 7).*

---

## ADDENDUM 1 — 2026-09-12, POST-COMPUTE, PRE-RESUME: `startFrom latestTime` FOR THE RESUME, AND WHY NO GATE MOVES

**Version 1.1 → 1.2. This is a DATED POST-FREEZE ADDENDUM under `CLAUDE.md`
rule 2, second bullet — NOT a pre-compute amendment, and the difference is the
whole reason this section exists.** Appended at the foot so that **lines whose
number changed above this section: 0.**

**THE CONDITION, AND HOW IT WAS CHECKED — AND IT IS THE OPPOSITE OF
AMENDMENT 1's.** First compute HAS now been spent against this document.
`verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3` exists and carries
`0/`, `processor0..3/` each holding time directories `0`, `5` **and `10`**, a
`log.solve` and a `STATUS.queue.K2h_L3`; the launch is on the record at
`verification/queue/LAUNCH_LOG.tsv` (`2026-09-12T20:36:38Z heat-transfer
K2h_L3 pid 145826 4 ranks`). The solver's last logged step is **`Time =
10.7388` of 112** and it was killed — not by a stop rule, not by a fault, but
by the **clean stop of the instance for the 16 → 96 core resize** (host booted
2026-09-12 21:32:17 UTC).

**AND THE FIRST THING THIS ADDENDUM CORRECTS IS ITS OWN INHERITED DESCRIPTION.**
The staged resume entry recorded, from a reading taken *before* the stop, that
"processor0..3 each hold exactly time dirs 0 and 5 and AGREE on 5 as latest".
**That is stale and it is wrong.** The solver ran on past it: **`t = 10` is
written on all four ranks and it is the latest**, verified here by reading the
bytes rather than the entry — all **36 field files** (4 ranks ×
`T U p_rgh alphat nut k omega phi p`) carry OpenFOAM's own end-of-file banner,
none is truncated, and `processor*/10/uniform/time` reads **`value 10; index
1692;` on all four ranks, in agreement**. `startFrom latestTime` therefore
resumes at **t = 10, not t = 5**, and **5 further simulated seconds of computed
work are preserved** that the entry would have thrown away. The entry's
`resume_from` field is corrected to `10` in the same commit as this addendum.
A resume declaration that names the wrong time is a false description of what
runs, which is why it is corrected on the record and not quietly.
**GATES ARE THEREFORE CLOSED.** Nothing below alters a gate, a threshold, a
band, a cap or a label, and the originals are struck nowhere.

**WHAT STANDS, EACH NAMED SO THAT NO READER HAS TO INFER IT:** §5's `S-SETTLE`
0–42 s and `S-WINDOW` 42–112 s stand; §6's `G-DPBAR` band
[27.9699, 28.0901] m²/s² stands; §6's `D-STATIONARY` 5.0e-03 m²/s² and
`D-COMPLETE` stand; §7's five predictions stand, losable exactly as frozen;
§8's POINT 420 core-min and cap 1260 stand; §11's FREEZE block stands, both
grading-path files still at their pinned sha256; Amendment 1's R4 suspension
stands. §3's governing disclosure — that this rung reports ONE level and NO
triple until all three levels are transient — stands and is not weakened by a
resume.

### AD1.1 The one substitution, stated exactly

§4 registers the `803` checkpoint copied into `processor*/0` as the initial
condition, i.e. **the run begins at simulated time 0**, and the generated
`controlDict` delivered that as `startFrom startTime; startTime 0;`. §4's own
frozen text carries no `startFrom` line — it registers the *initial condition*,
and the run-control spelling of it lived in the generated dictionary; what is
re-pointed is the delivery of §4's intent, not a frozen line of §4. **That is
correct for the INITIAL launch and wrong for a resume**: re-run as frozen, the
solver would re-read `processor*/0` and **discard the 7.6 s already computed**,
restarting from zero. The resume therefore sets, in the GENERATED (untracked,
non-frozen) `controlDict` only:

> `startFrom latestTime;`

and nothing else. `resume_k2h.sh` makes that one substitution, **reads the file
back from disk**, and **RE-ASSERTS `endTime 112`, `writeInterval 5` and
`purgeWrite 16` AFTER the edit**, so a `sed` that matched too much cannot pass
unnoticed. The frozen document is not edited; the tracked registration is not
edited; this addendum is the disclosure.

### AD1.2 WHY THIS MOVES NO GATE — arithmetic, not assurance

**`S-SETTLE` and `S-WINDOW` are ABSOLUTE SIMULATED TIMES, not elapsed-time
offsets.** Averaging starts at simulated t = 42 s and the graded window is
simulated 42–112 s, whichever wall-clock second the solver happens to be
running in. Resuming at simulated t = 5 reaches t = 42 and t = 112 at exactly
the same simulated times a continuous run would. **The graded quantity is
therefore bit-for-bit the same quantity, computed over the same window.**

**The averaging accumulator cannot be corrupted by this resume, and that is
checked rather than assumed.** `fieldAverageProperties` does not exist anywhere
in the case tree: averaging is not DUE until t = 42 and the run reached ≈ 7.6.
**Nothing partial exists, so nothing partial can be inherited.** `dpAverage`
declares `restartOnRestart false` explicitly, so a later resume — one taken
after t = 42, if one is ever needed — RESUMES the running mean instead of
discarding the window; `resume_k2h.sh` G-02b **REFUSES** if an accumulator
exists on some ranks and not others, and **ALSO REFUSES** if no accumulator
exists while the latest time is at or past `timeStart`, because absence is only
innocent before averaging is due.

**Cost is unchanged and is not re-based.** POINT 420 core-min and cap 1260
stand as frozen; the ≈ 7.6 s already computed is spent against that same POINT,
not added to it. An overrun remains a **flag**, never a stop (directive #17),
and the cap is never raised by any agent.

### AD1.3 RANKS STAY AT 4, AND THE REASON IS THE CHECKPOINT ITSELF

The 96-core allocation table (`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
§A) places "K2 transient" inside the **20-rank finalization lane** alongside M6
on the NASA grid (3 levels × 4 = 12) and D6R2 multipoint (4) — **16 of the 20,
leaving exactly 4.** The allocation and the registration agree without either
being bent to the other.

**And even if ranks were free, they could not be taken here.** The case is
decomposed on disk at `numberOfSubdomains 4` and the ONLY complete checkpoint —
`processor0..3/10` — is written in that decomposition. Raising the rank count
requires `reconstructPar` followed by `decomposePar` at the new count, which
**destroys the resume and restarts this run from zero.** Sanaa's 2026-09-12
21:25Z directive is explicit on that point ("I DON'T want to restart from 0").
**4 ranks is not a default carried forward; it is the number the surviving
checkpoint is written in.**

### AD1.4 WHAT THIS ADDENDUM DOES NOT CLAIM

It does not claim the resumed trajectory is bit-identical to an unkilled one —
a restart from a written checkpoint re-enters the PIMPLE loop from written
fields and the trajectory of a transient is not guaranteed identical to
round-off. What is claimed is narrower and is the thing the gate rests on: the
**graded quantity is a time average over an absolute simulated window that the
resume does not move**, and the settling period 0–42 s absorbs the restart
transient by construction, since the restart happens at t = 10, **32 simulated
seconds before averaging begins.** The completeness of the checkpoint is not
taken on this addendum's word either: `resume_k2h.sh`'s end-of-banner limb
**REFUSES** rather than degrades and is evaluated at launch against the
post-stop bytes, never against a pre-stop assertion.

*Nothing in this rung is sent, filed, uploaded, registered, posted or commented
outside this box (rule 7).*

---

## ERRATUM TO ADDENDUM 1 — 2026-09-12, same day, POST-LAUNCH OF THE RESUME

**Version 1.2 → 1.2a. Appended at the foot; lines whose number changed above
this section: 0.** Addendum 1 is **struck nowhere and rewritten nowhere**
(rule 2, rule 6); this erratum is how its three wrong numbers are corrected.

**ADDENDUM 1 CARRIES THE FIGURE "≈ 7.6 s" IN THREE PLACES — LINES 468, 491 AND
501 — AND IT IS WRONG IN ALL THREE.** It is the stale figure the addendum was
written to remove, and it survived in the sentences the correction did not
touch. **The measured figures are:** the solver's last logged step was
**`Time = 10.7388`**; the last step to reach disk was the **complete t = 10
checkpoint**; `log.solve` holds **1817 `Time =` lines against 1816
`ExecutionTime` lines**, the missing one being the in-flight step that died
mid-write and never reached disk. Read "≈ 7.6 s" as **10.7388 s logged, 10 s
checkpointed** wherever it appears above. **No gate, threshold, band, cap or
label is touched by this correction, and the direction is in the run's favour:
more computed time survives, not less.**

**AND TWO THINGS ADDENDUM 1 SAID THAT THE DISK CONTRADICTS, RECORDED RATHER
THAN QUIETLY DROPPED:**

1. **`system/controlDict` IS GIT-TRACKED.** The staged entry called it "the
   GENERATED (untracked, non-frozen) `controlDict`" and Addendum 1 repeated
   that description. **`git ls-files` lists it.** The one-line `startFrom`
   re-point is therefore a change to a tracked file and is committed with this
   erratum rather than left dirty in a shared tree. **No physics is touched:**
   `runTimeModifiable false` means the running solver never re-read the file,
   so the whole t = 0 → 10.74 segment ran under the original
   `startFrom startTime`, exactly as registered, and only the resume reads
   `latestTime`.
2. **`log.solve` IS APPENDED TO ON RESUME, AND THAT BREAKS ONE PIECE OF
   COMPLETION ARITHMETIC.** `resume_k2h.sh` redirects with `>>`, so the
   resumed segment concatenates onto the 4.10 MB first segment;
   `NSTEP=$(grep -c '^ExecutionTime = ' log.solve)` then counts **both** runs
   while `ExecutionTime` restarts near zero in the second. **Standing rule 4's
   clause-5 step count cannot be read off the concatenated log** and must be
   evaluated by splitting it at the second `Build :` banner. **This is an
   INFRASTRUCTURE field under this entry's own `_field_classes` rule (L-342):
   it voids the COST claim's arithmetic if unsplit, and it can never void the
   physics.** Recorded here so the grader cannot meet it as a surprise.

*Nothing in this rung is sent, filed, uploaded, registered, posted or commented
outside this box (rule 7).*

---

## ADDENDUM 2 — 2026-09-12 ~22:05Z, MID-RUN AND BEFORE THE CROSSING: §8's COST IS WRONG BY 8.04x, THE CAP WILL BE CROSSED AT ~02:10Z, AND THE CAP IS NOT RAISED

**Version 1.2a → 1.3. Dated post-freeze addendum. Appended at the foot; lines
whose number changed above this section: 0.**

**THIS IS REGISTERED BEFORE THE CROSSING, NOT AFTER IT, AND THAT IS THE POINT.**
At the moment of writing the run is live at simulated **t = 12.49 of 112** and
has spent **250.4 core-min**. §8's POINT is 420 and its cap 1260. **The cap is
NOT raised here and CANNOT be** — rule 2 forbids an addendum to move a cap, and
raising or retiring one is Sanaa's alone. What is registered is the
**measurement**, the **predicted crossing time**, and **what a crossing does and
does not mean** — written down while the answer is still in the future.

### AD2.1 THE MEASUREMENT, AND WHY IT IS NOT A DRIFT

**Measured mean `deltaT` = 0.0059102 s. §8 registered 0.0475 s. The ratio is
8.04x.** The figure is not a transient and not a sample artefact: `deltaT` is
**identical to nine significant figures across all 2,238 steps of both log
segments**, because it is **pinned at the Courant ceiling** — the log reads
`Courant Number max: 1.99989` against the case's `maxCo 2.0`, and `maxDeltaT
0.25` never binds. Measured over **54.5 minutes** of running, not over thirty
seconds.

**THE CAUSE IS A BAD SCALING LAW IN §8, NAMED PLAINLY BECAUSE IT IS THE LAB'S
OWN ERROR AND NOT THE BOX'S.** §8 took K2b's measured `deltaT` 0.0804 s at
137,000 cells and divided it by the **LINEAR** refinement ratio
(664848/137000)^(1/3) = 1.69. **The true ratio is 0.0804 / 0.005910 = 13.6x.**
The mesh is not uniformly refined: its finest cells are roughly 8x smaller than
a uniform 1.69x refinement implies, and an explicit Courant limit is set by the
**smallest** cell, never by the mean. **A per-cell-count scaling of a Courant
limited time step is the wrong law on a locally refined mesh.**

**AND THE OTHER TERM WAS CONSERVATIVE, WHICH IS RECORDED BECAUSE A HALF-TOLD
CALIBRATION IS WORSE THAN NONE.** §8's `x2.5` PIMPLE-over-SIMPLE cost factor
predicted 2.82 s/step; the measured rate is **1.1516 s/step** uncontended. That
term was conservative by **2.45x** and partly offsets the `deltaT` error.

### AD2.2 THE PROJECTION, AND THE CROSSING TIME, WHICH IS RATE-INDEPENDENT

Steps to t = 112 at the measured `deltaT`: **18,950**, against §8's registered
**2,358** — the same 8.04x. Remaining at the time of writing: **16,842**.

| rate | remaining wall | total core-min | vs POINT 420 | vs cap 1260 |
|---|---|---|---|---|
| 1.1516 s/step (measured, uncontended) | 5.39 h | **1,543** | 3.67x | **1.22x** |
| 1.7998 s/step (segment-1 rate, if load returns) | 8.42 h | **2,272** | 5.41x | **1.80x** |

**THE CROSSING TIME DOES NOT DEPEND ON THE STEP RATE, and that is worth stating
because it looks as though it should.** Core-minutes are `wall s x ranks / 60`,
so the cap converts to a **fixed wall figure**: 1,260 core-min = **18,900
solver wall-seconds**. **POINT 420 is crossed at ~22:40Z tonight; cap 1260 is
crossed at approximately 02:10Z on 2026-09-13**, whatever the rate does.
Completion at t = 112 lands ~03:20Z at the measured rate, ~06:25Z at the
segment-1 rate.

### AD2.3 WHAT THE CROSSING DOES NOT DO — AND THE ONE QUESTION THAT IS ABOVE ME

**NOTHING STOPS THE RUN.** Sanaa's directive #17 of 2026-09-12 is explicit that
no run is stopped by a time or budget cap, by any team. §8 already registered
the cap as **a flag and not a stop**. No `timeout` is armed, no guard is added,
and the crossing writes `CAP_FLAG.txt` and changes nothing else.

**NO GATE, THRESHOLD, BAND OR LABEL MOVES.** `S-SETTLE` 0–42 s, `S-WINDOW`
42–112 s, `G-DPBAR` [27.9699, 28.0901] m²/s², `D-STATIONARY` 5.0e-03 and
`D-COMPLETE` are untouched. **A smaller `deltaT` is MORE temporal resolution of
the averaging window, not less** — the misprediction makes the physics better
resolved and the bill larger, and those are opposite directions.

**AND HERE IS THE CONFLICT, STATED RATHER THAN RESOLVED LOCALLY.** Sanaa's
2026-09-12 run instructions, item 7, read "cap → NOT A RESULT, never raised".
Her universal rule of 2026-08-26 reads that **bookkeeping never voids physics**,
and this entry's own `_field_classes` (L-342) places cost among the
**INFRASTRUCTURE** fields, which "void only the cost claim" and may "never
produce NOT A RESULT". **Applied literally to this run, item 7 would grade a
physically complete, in-window, in-band transient `NOT A RESULT` on the strength
of a scaling-law error in its own cost estimate.** I do not believe that is what
item 7 is for, and **I am not ruling it myself**: whether a cap crossing forces
`NOT A RESULT` touches the verdict vocabulary across every team and is
**escalated to the chief, and through the chief to Sanaa**. Until it is ruled,
**the run continues, the flag is recorded, and this rung's verdict is `PENDING`.**

### AD2.4 TWO §9 SUB-CLAIMS RE-CHECKED AGAINST THE MEASURED RATE, BECAUSE THEY RESTED ON IT

- **Checkpoint interval.** 5 simulated s = 846 steps x 1.1516 s = **974 s =
  16.2 min** of wall per write. §9 projected 5.0 min and claimed the 30-minute
  bound survived a 5x error. **The projection is wrong by 3.25x and the
  30-minute bound HOLDS.** Not a defect; Sanaa's checkpoint items 1–3 are met.
- **`purgeWrite 16` retention.** Writes land at 5, 10, …, 110 and then at 112;
  the last 16 are t = 45 … 110 and 112, so **t = 45 through t = 112 are
  retained** and `D-STATIONARY`'s two halves survive. Measured write size 31 MB
  per rank x 4 = **124 MB**, against §9's 122 MB estimate; 16 writes ≈ 2.0 GB
  against 491 GB free. **Not a defect.**
- **One correction to the watch plan, from the dictionary rather than from
  taste:** `fieldAverage` carries `timeStart 42` with `writeControl writeTime`,
  so `uniform/fieldAverageProperties` **cannot appear at t = 42** — the first
  write at or past the start is **t = 45**. A four-rank agreement check at t = 42
  would manufacture a false mismatch by construction; it is made at t = 45.

*Nothing in this rung is sent, filed, uploaded, registered, posted or commented
outside this box (rule 7).*
