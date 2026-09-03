# T25R6a C5 RE-GRADE — the measured `Σ CAP(C5)`, and the unsatisfiable equivalence predicate that hid it

> **NO GRADER WAS CHANGED BY THIS RECORD, NO VERDICT WAS ISSUED, AND
> `T25R6a_VERDICT.json` IS NOT REWRITTEN.** The repair below is stated as a
> **DIFF FOR THE SUPERVISOR TO READ PERSONALLY** — reading a measurement-script
> diff is `SUPERVISION_CHARTER.md` §3's check and is not delegable to a lane.
> Every number in §3 was produced by calling the **frozen** `grade_t25R6a.py`'s
> own unmodified functions and constants from a read-only driver that wrote
> nothing into the repository.
>
> **NO NEW INSTRUMENT WAS BUILT.** Sanaa's 2026-09-03 ~22:00Z ruling names the
> instrumentalisation of instruments as a thing she must not see again.
> `cap_census_audit.py` was read first, as ordered, and is **the wrong
> instrument for this number** — §5 says why — and it was **not extended**.

Written 2026-09-03 by a heat-transfer `lab-lane`. Repository HEAD at drafting:
`0047fcaa`.

---

## 1. THE HEADLINE NUMBER

> ### **`Σ CAP(C5) = 20,006.80 core-minutes`**
> ### **ceiling `20,000` — it BREACHES, by `+6.80` core-min, a `×1.00034` breach (0.034 %)**
> ### **and the breach is ~200× SMALLER than the measurement's own registered resolution of ±1,340 core-min.**

**The measurement cannot resolve which side of 20,000 the ladder falls on.** That
sentence is the finding, and it is worth more than the point estimate. Sanaa's
2026-09-03 16:00Z ruling asked for *"a measurement, not a hope"*; this is the
measurement, and its honest width is part of it.

**No recommendation is attached. The ceiling is Sanaa's to rule on.**

## 2. WHAT WAS WRONG — an equivalence predicate NO RUN COULD EVER SATISFY

`T25R6a_VERDICT.json` as published carries `"verdict": "NOT A RESULT"`, `"exit": 4`,
ground **`"the equivalence control FIRED (prereg 6.4)"`** — and, in the same file,
**`'fired': []` at both levels**. The published artifact contradicts itself on its
own face.

The cause is a **return-value contract mismatch**, at `grade_t25R6a.py:438-439`:

```python
r = cmp_mod.compare(os.path.join(HERE, "C5_%s" % lvl),
                    os.path.join(HERE, "B0_%s" % lvl))
equiv["C5_%s" % lvl] = str(r)
if r is not True and r != 0:          # <-- TAUTOLOGY
    equiv_ok = False
```

`compare_arms_t25R5.py:compare()` **always returns a `dict`** — its own frozen
body ends `res["fired"] = fired` … `return res` (lines 282, 292). It has no
branch that returns `True` and none that returns `0`.

**A `dict` is never `True` and never `== 0`.** So `r is not True and r != 0`
evaluates **True for every possible input**, `equiv_ok` becomes `False` on
**every possible run**, and the grader returns `NOT A RESULT` at step [5] before
it ever reaches the wall factors at [6] or `G-T6a` at [7].

> **THE GATE IS UNSATISFIABLE. NO RUN, OF ANY QUALITY, COULD HAVE PASSED IT.**
> The four cases beneath it are complete, rule-4 clean, and their equivalence
> channels sit three to five orders inside their registered thresholds. The rung
> was refused by its own arithmetic, not by its physics.

### 2.1 The equivalence data the predicate never consulted, against its registered thresholds

Registered in `T25R6a_PREREGISTRATION.md` §6.4, carried unchanged from T25R5 §4:

| channel | registered DISQUALIFYING threshold | `C5_L1` measured | `C5_L3` measured | margin |
|---|---|---|---|---|
| `max\|ΔT\|`, coolant **and** module | **1.000e-03 K** | 9.000019e-09 | 4.210000e-07 | ×1.1e5 / ×2.4e3 |
| `max\|Δp_rgh\|` | **1.0 Pa** | 1.000008e-06 | 3.000008e-06 | ×1.0e6 / ×3.3e5 |
| `max\|ΔU\|` | **1.0e-03 m/s** | 2.139000e-08 | 2.780000e-09 | ×4.7e4 / ×3.6e5 |
| `k`, `omega`, `nut`, `alphat`, `p` | reported, **gating nothing** | — | — | — |
| **`fired`** | — | **`[]`** | **`[]`** | — |

The registration predicted *"four to five orders of margin"*. It got four to six.

### 2.2 The planted-zero control, ARMED AND PASSING — so `fired == []` is evidence

A zero from a reader not shown able to see a non-zero is not evidence
(standing rule 3). The frozen comparator's `planted_control()` was **driven on
all four case directories** on 2026-09-03:

- `PLANT = 1.234e-03 K`, planted **by line index** into cell 0 and cell n−1 of
  **both** regions, on a copy, read back **from disk**, `PLANT_TOL_K = 1e-9`.
- **Recovered `1.234000e-03` exactly, 4 plants × 4 cases = 16/16 SEEN.**
- `PLANT` is **ABOVE** the `E1` threshold `1.000e-03 K` **on purpose**, so the
  control proves **the gate can FIRE**, not merely that the reader can read.
- The control works in `.plantwork` and removes it; **no case field was
  modified** and no residue remained.

## 3. THE MEASUREMENT — produced by the FROZEN grader's own functions

**Frozen path verified before anything was read:** the delegated comparator
`T25R5_LINSOLVER_runs/compare_arms_t25R5.py` hashes to the registered blob
`736bd0d9e03c898c1ca991cfc1b8fec8e0058b39` (`check_comparator_freeze()`
returned `True`).

**Rule 4, via the frozen `rule4()`:** `B0_L1`, `C5_L1`, `B0_L3`, `C5_L3` all
`ok=True`, `bad=[]`. Their `DONE.*` markers independently record *"strict rule
met (all conjuncts, including the age guard against the case's own
`0/module/T`)"*.

### 3.1 Inputs — `ExecutionTime` from `log.solve.legA`, the file the frozen grader reads

| case | artifact | `exec_s` | corroboration |
|---|---|---|---|
| `B0_L1` | `T25R6a_C5_OUTER_runs/B0_L1/log.solve.legA` | **131.87** | `DONE.B0_L1`; target 131.28, band [118.15, 144.41] — **in band** |
| `C5_L1` | `T25R6a_C5_OUTER_runs/C5_L1/log.solve.legA` | **12.38** | `DONE.C5_L1` |
| `B0_L3` | `T25R6a_C5_OUTER_runs/B0_L3/log.solve.legA` | **956.97** | `DONE.B0_L3`; target 989.39, band [890.45, 1088.33] — **in band** |
| `C5_L3` | `T25R6a_C5_OUTER_runs/C5_L3/log.solve.legA` | **135.56** | `DONE.C5_L3` |

Both baselines reproduced inside their registered ±10 % `ExecutionTime` band,
and the `P-4` integer reproduction control read **EXACT** on both.

### 3.2 Wall factors

| level | `f_C5` | basis |
|---|---|---|
| **L1** | **10.651858** | `131.87 / 12.38` — MEASURED here |
| **L2** | **13.557920** | `516.15 / 38.07` — **FROZEN from T25R5**, not re-measured (prereg §7.1) |
| **L3** | **7.059383** | `956.97 / 135.56` — MEASURED here |

### 3.3 `Σ CAP(C5)` — term by term, re-derivable by hand from frozen constants

`Σ CAP = Σ over the six ladder runs of CAP(run) ÷ f_C5(level(run))`, with the
price table frozen at `T25R5_PREREGISTRATION.md:58-66`:

| run | level | `CAP` | `÷ f` | core-min |
|---|---|---:|---:|---:|
| `S1` | L1 | 7,526.4 | 10.6519 | **706.58** |
| `S2` | L2 | 20,151.3 | 13.5579 | **1,486.31** |
| `S3` | L3 | 41,815.5 | 7.0594 | **5,923.39** |
| `T2` | L2 | 40,302.7 | 13.5579 | **2,972.63** |
| `T4` | L2 | 80,605.3 | 13.5579 | **5,945.26** |
| `W30` | L2 | 40,302.7 | 13.5579 | **2,972.63** |
| | | | **SUM** | **20,006.80** |

- **`Σ CAP(C5)` = 20,006.80 core-min**; ceiling **20,000**; ratio **×1.00034**;
  **breach +6.80 core-min**.
- **`Σ POINT` equivalent** = `Σ CAP / M`, `M = 4.0` = **5,001.70 core-min**
  = 83.36 core-h = **$4.28 — DERIVED, NOT MEASURED**, at the owner-stated
  $0.0513/core-h. This box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).

### 3.4 UNCERTAINTY — and it is larger than the breach by ~200×

The registered reproducibility interval is `EXEC_BAND = 0.10` — ±10 % on a
single run's `ExecutionTime`, set in the pre-registration from the **measured**
contended/alone ratio 1.085 with margin.

A wall factor is a **ratio** of two such times. If both endpoints may move
independently inside ±10 %, then `f ∈ [0.8182 f, 1.2222 f]`. `Σ CAP` is
monotone decreasing in each `f`, so with `f(L2)` held frozen as registered:

> ### **`Σ CAP(C5) ∈ [18,801.4 , 21,480.1] core-min`**
> ### **= 20,006.8 −1,205.4 / +1,473.3, i.e. −6.02 % / +7.36 %**

*(If `f(L2)` is allowed to move too — it is a frozen constant, so this is
disclosed, not adopted — the interval widens to [16,369.2 , 24,452.8].)*

**THE INTERVAL STRADDLES THE CEILING COMFORTABLY.** The point estimate breaches
by 0.034 %; the instrument's own registered resolution is ±~6.7 %.

**Disclosed against the width, in the conservative direction:** the four arms ran
**sequentially inside one 21-minute window** (16:42:28Z → 17:03:33Z, from the
`DONE.*` stamps), so contention is largely **common-mode** between a factor's
numerator and denominator and partly cancels in the ratio. The
independent-endpoint interval above is therefore an **upper bound** on the
uncertainty, not a best estimate. **The lab has no measurement of the residual
after cancellation, so the wider interval is what is quoted.**

### 3.5 The registered predictions — ALL THREE WIN

| prediction | registered before any arm existed | measured | verdict |
|---|---|---|---|
| `P-1` decay is a property of the mesh, not the arm | `f(L3) < f(L2)` | 7.0594 < 13.5579 | **WINS** |
| `P-2` `C5`'s decay is milder than `C4`'s | `f(L3)/f(L2) > 0.4606` | **0.5207** | **WINS** |
| `P-3` | `f(L3) ≥ 7.0029` | **7.0594** | **WINS** |

The registered bracketing hypotheses were **H1 = 17,016.2** (fits) and
**H2 = 20,724.9** (breaches). **The measured 20,006.8 lands between them**, nearer
H2 — the registration's claim that the measurement was genuinely decisive and
could land on either side is borne out.

**`P-3` wins and `Σ CAP` still breaches, and that is not a contradiction.** The
registered `f(L3) = 7.0029` pivot was computed holding L1 **at H2's 11.5370**.
`f(L1)` measured **10.6519**, lower, so `S1` costs **706.58** rather than 652.37
— **+54.21 core-min** — and the pivot moves up to **`f(L3) = 7.06750`**. Measured
`f(L3)` is **7.05938**, short by **0.00812 — 0.115 %**. `P-3` was registered
against the old pivot and wins against it; the gate is on `Σ CAP` from all three
factors, and it does not.

*Noted in passing, gating nothing:* the pre-registration's illustrative pivot
arithmetic writes the L2 block as `181,362.0 / 13.5579 = 13,376.44`; the frozen
`sigma_cap()` returns **13,376.83** for that block at the exact factor
`516.15/38.07` (and 13,376.85 at the 4-dp factor as literally written). A
**0.39-core-min transcription slip in an illustrative line** that §5 of that
document already labels *"illustrative … the gate is on `Σ CAP` computed from all
three factors, not on this single number."* **It moves no gate, no threshold and
no verdict**, and it is recorded here rather than corrected, because the
registration is frozen (rule 6).

## 4. THE §2d.1 REPAIR EXCEPTION — all four conditions, named

`VERIFICATION_CHARTER.md` §2d.1 permits a change on the grading path after the
first graded solve **when, and only when, all four hold.**

**(1) IT REPAIRS A DEMONSTRABLE ERROR RATHER THAN A PREFERENCE.** The predicate
`r is not True and r != 0` is **tautologically true** for the only type
`compare()` can return. This is established by reading two frozen files'
contracts against each other, not by preferring a different verdict. A gate no
run can pass is not a strict gate; it is a broken one.

**(2) THE ERROR WAS ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS —
ONE THAT GRADES NOTHING.** This is §2d.1's load-bearing condition. **Two such
instruments, neither of which grades anything in `grade_t25R6a.py`:**

- **The comparator's `fired` list.** The grader computes it, serialises it into
  the verdict JSON, and then **discards it** — it gates nothing. It reads `[]` at
  both levels. **The published artifact already carried, on its own face, the
  evidence that no channel fired while its `ground` field said one had.**
- **The comparator's rule-3 planted-zero control** (§2.2). It grades nothing; its
  sole function is to prove the reader can see a known non-zero **above** the
  disqualifying threshold. It passed 16/16. It is what converts `fired == []`
  from a silent zero into evidence.

**Neither knows anything about `Σ CAP`, the six ladder runs, or the 20,000
ceiling**, so neither can have been selected to move `G-T6a` in a wanted
direction — which is exactly the property §2d.1 is cut to require.

> **AND, AGAINST THIS RECORD'S OWN INTEREST:** the repair moves the verdict from
> `NOT A RESULT` **to `GATE FAIL`** — *away* from a `PASS`, not toward one.
> Nothing here was repaired in the direction anyone wanted.

**(3) THE RECORD DISCLOSES IT, NAMES THAT INSTRUMENT, AND QUANTIFIES WHAT MOVED.**
This document. What moved, quantified:

| | pre-repair (published) | post-repair |
|---|---|---|
| step reached | `[5]` equivalence | `[7]` `G-T6a` |
| `exit` | **4** | **3** |
| verdict | **`NOT A RESULT`** | **`GATE FAIL`** |
| ground | "the equivalence control FIRED (prereg 6.4)" | `Σ CAP(C5) = 20,006.8 > 20,000, a ×1.00034 breach` |
| `Σ CAP(C5)` | **never computed** | **20,006.80** |
| `f_C5(L1)` / `f_C5(L3)` | never computed | 10.6519 / 7.0594 |
| predictions `P-1..P-3` | never evaluated | WINS / WINS / WINS |

**(4) THE PRE-REPAIR VALUES ARE RECORDED BESIDE THE PUBLISHED ONES.**
`T25R6a_C5_OUTER_runs/T25R6a_VERDICT.json` stands on disk **unaltered** and is
cited above verbatim. It is struck by this record, never rewritten (rule 6).

### 4.1 THE DIFF — one line, and it is the supervisor's to read

Proposed, **NOT APPLIED**. `verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py`:

```diff
@@ grade(), step [5] EQUIVALENCE CONTROL @@
         r = cmp_mod.compare(os.path.join(HERE, "C5_%s" % lvl),
                             os.path.join(HERE, "B0_%s" % lvl))
         equiv["C5_%s" % lvl] = str(r)
-        if r is not True and r != 0:
+        if not isinstance(r, dict):
+            refuse("compare() returned %r, not the dict its frozen contract "
+                   "promises; the equivalence limb cannot be read." % type(r))
+        if r["fired"]:
             equiv_ok = False
```

**What the repair does NOT do**, and the contrast is the point of §2d.1: it does
**not** move a threshold, a band, the 20,000 ceiling, the price table, `M = 4.0`,
`f_C5(L2)`, or any label. **Every disqualifying threshold in §6.4 stays exactly
where it was frozen.** It makes the predicate read the channel the registration
says gates the rung, instead of a type check that can only ever be true.

## 5. `cap_census_audit.py` — READ FIRST, AND IT IS THE WRONG INSTRUMENT

Read before anything was written, as ordered.
`verification/runs/T-family/cap_census_audit.py` is the instrument of record for
`docs/campaigns/T-family/CAP_CENSUS_2026-08-27.md`. It answers *"has any
heat-transfer case ever exceeded a REGISTERED CAP?"* by reading **ACTUAL**
core-minutes out of each case's own `STATUS`/`DONE` record and comparing them to
that **case's own** registered cap.

**`Σ CAP(C5)` is not that quantity and shares no arithmetic with it.** It is a
**ladder extrapolation** — `Σ CAP(run) ÷ f(level(run))` over six runs that have
**never been launched** — priced from a frozen table and three wall factors.
There is no actual to census.

**So it was not extended, not adapted, and not called.** Nothing beyond the
frozen `grade_t25R6a.py` was needed, and nothing beyond it was built.

## 6. WHAT THIS ENTAILS FOR THE CEILING — entailment only; the ruling is Sanaa's

Sanaa, 2026-09-03 16:00Z, verbatim: *"If the measured best configuration still
breaches the ceiling, bring the widening request back with that number and I'll
rule on a measurement, not a hope."*

**The number is 20,006.8 core-min against 20,000. It breaches, by 6.8 core-min.**

What follows from it, and nothing more:

1. **The breach is real at the point estimate and unresolvable at the
   measurement's own resolution.** ±1,340 core-min against a 6.8 core-min
   breach. **A ruling that the ladder fits and a ruling that it does not are both
   consistent with this measurement.** No further arithmetic on these four runs
   changes that.
2. **What IS firmly resolved is the size of the move.** `C4` — the previous `G-T5`
   winner — gave `Σ CAP = 24,709.3`, a **×1.2355** breach of **4,709.3** core-min.
   `C5` gives **20,006.8**, a breach of **6.8**. **`C5` removes 4,702.5 of the
   4,709.3 core-min breach — 99.86 % of it.** Whatever is ruled about the
   ceiling, the linear-solver line has closed essentially the whole gap.
3. **A widening, if one were ever granted, would be 6.8 core-min — 0.034 %.**
   Stated as arithmetic so the size of the thing being ruled on is visible. **This
   lane requests nothing.** A widening is a desk item for Sanaa and
   `T25R6a_PREREGISTRATION.md` §7.4 pre-registers **none**.
4. **The alternative to a widening is a correction nobody has measured yet.** The
   ramp→soak blend `ρ_blend` would need to be **< 0.99966** (`= 20,000 / 20,006.8`)
   to bring `C5` inside the ceiling **without touching it at all** — against the
   **0.809412** that `C4` would have needed. `T25R6c` is the registration that
   would measure `ρ`; **it has not run.** This is arithmetic on an unmeasured
   quantity and **is not evidence**.

### 6.1 THE QUALIFICATION THAT TRAVELS WITH THE NUMBER, IN FORCE

Carried unaltered from `T25R6a_PREREGISTRATION.md` §4.2 and `T25R5` §5.1, because
a reader who takes 20,006.8 for a ladder price has been misled by this document:

> **`Σ CAP` is the ladder's ×4 TIMEOUT ALLOWANCE under the assumption that each
> arm's 40-step RAMP wall factor holds for the whole run. 40 steps is 0.34 % of
> the shortest ladder run and it is the RAMP, not the SOAK. It is NOT a
> prediction of ladder cost, not an expected spend, and not a measurement of
> anything at step 11,800. The assumption is UNMEASURED and this rung does not
> test it.**
>
> **NO LADDER LAUNCHES ON THIS RESULT, WHATEVER IT SAYS.**

`T25R6c_PREREGISTRATION.md` §1 records the first quantitative sighting of that
bias on disk: the T25R4 probe rate `r_C = 0.1594583` core-min/step against
`B0_L1`'s own arm rate `r_M = 0.1094000`, a ratio of **1.4576**. **The probe rate
is 1.46× the arm rate — the bias is visible and still unmeasured.**

### 6.2 Roache (rule 5) — NOT INVOKED, and that is registered

No grid triple is formed, no observed order and no GCI is computed, quoted or
derivable from these levels. They carry **wall-cost** measurements of a transient
at 40 steps, not a solution functional at convergence (prereg §6.5). **A successor
reading a grid-convergence claim off them gets `NOT A RESULT`.**

## 7. What this record does not do

- It does **not** edit `grade_t25R6a.py`, `compare_arms_t25R5.py`, or any other
  script that produces, grades or aggregates a measured number.
- It does **not** issue a verdict, write a verdict JSON, or withdraw the
  published `NOT A RESULT`. `T25R6a_VERDICT.json` stands.
- It does **not** move a gate, threshold, band, cap, ceiling or label.
- It does **not** launch, authorise, or request a ladder run.
- It does **not** recommend a ruling on the 20,000 ceiling.
- It does **not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).
