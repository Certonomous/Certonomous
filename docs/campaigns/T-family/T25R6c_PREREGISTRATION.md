# T25R6c — BOUNDING the ramp→soak bias across BOTH its components, by comparing LEG A to LEG B on the same run. Supersedes T25R6b.

> **STATUS: FROZEN BY COMMIT. NOT ENQUEUED.**
> Frozen by the commit that first lands it, per standing rule 2 — gate, threshold,
> cap and label committed **before any compute**. **No `T25R6c` case directory exists
> at the moment of this freeze**, verified, so the freeze is true by construction.
> Enqueueing is the supervisor's separate act. This lane does not launch.
>
> **SUPERSEDES `T25R6b_PREREGISTRATION.md`** (frozen `edacba99`), which is **not
> rewritten and not deleted** — rule 6 — and carries a dated amendment recording the
> supersession and its ground. T25R6b had **no compute, no case directory and no
> enqueued row**, so nothing is withdrawn but the design itself.

---

## 0. WHY THE PREDECESSOR WAS WITHDRAWN — the defect was in the DESIGN, not the case source

T25R6b registered `ρ` over **400 steps at `deltaT 0.02`**. Reading the case family before
binding to it — the check that produced this document — established that **that design
measures the smaller half of the bias it exists to bound.**

**A ladder run is TWO LEGS in one runner invocation** (`run_one_t25R4.sh:111-127`): leg A
runs the active `controlDict`; the script copies it to `controlDict.legA.used`, copies
`controlDict.legB` over `controlDict`, and runs leg B from `latestTime`; then
`reconstructPar -allRegions -newTimes`.

| leg | `startFrom` | `endTime` | `deltaT` | log |
|---|---|---|---|---|
| **A** | `startTime` | 70 (ladder) / 0.8 (`C4_L1`) | **0.02** | `log.solve.legA` |
| **B** | `latestTime` | 900 | **0.1** | `log.solve.legB` |

**The registered ladder step count resolves EXACTLY, and it is a mixture of two timestep
regimes:**

> **S1: leg A `70 / 0.02` = 3,500 steps + leg B `830 / 0.1` = 8,300 steps = 11,800 —
> matching the registered `N steps` (`T25R5_PREREGISTRATION.md:58-66`) TO THE DIGIT.**

**70.3 % of ladder steps are leg-B steps at a 5× larger timestep.** So A1.2's ramp→soak
bias has **two components** — window position (transient vs cruise) **and the `deltaT`
regime change 0.02 → 0.1** — and T25R6b's instrument contained only the first. **A
registration that measures 29.7 % of a bias and is read as bounding all of it is worse
than no registration**, because it would produce a confident number wrong in a direction
nobody would check. T25R6b also priced 400 steps at `deltaT 0.02` to `t = 8 s`, which is
**leg A of nothing registered**: `C4_L1`'s leg A ends at 0.8 s and the ladder's at 70 s.

**Mechanically it could not have been an amendment either:** a corrected `ρ` needs a new
cap, and rule 2 forbids an amendment that alters a cap.

## 1. ⚡ THE CORRECTION TO THE PREDECESSOR'S COST BASIS — A TAUTOLOGY, STRUCK

T25R6b §6 claimed its per-step rate was *"derived two independent ways and agreeing to six
significant figures"* — `1,881.6 / 11,800 = 0.1594576` from the frozen price table, and
`(229.62/48) × 2 / 60 = 0.1594583` from the measured `s_per_step`.

> **~~That claim is STRUCK. It is a TAUTOLOGY, not a corroboration.~~** `POINT(S1)` was
> **built** as `N × r(L1) × 2 / 60` (A1.1's frozen formula), so dividing it back by `N`
> recovers `r(L1) × 2 / 60` **by algebra**. The two figures agree to six significant
> figures because **they are the same number**. Struck rather than rewritten, per rule 6.

**The rate's VALUE is unaffected** and remains sound as a conservative cap basis. **Real,
independent corroboration exists and points the other way — and it is the first
quantitative sighting of A1.2's bias in this lab:**

| rate | value (core-min/step, 2 ranks) | source |
|---|---:|---|
| `r_C` — the T25R4 probe rate | **0.1594583** | `229.62 s / 48 steps` — the `t ∈ [0,2] s` probe A1.2 registers as biased high |
| `r_M` — `B0_L1`'s own 40-step arm | **0.1094000** | `131.28 exec s / 40 steps`, `T25R5` stage 2 |
| | **`r_C / r_M` = 1.4576** | **the probe rate is 1.46× the arm rate** |

**A1.2's bias is already visible on disk — unmeasured, but not invisible.** This document
uses `r_C` for the **cap** (conservative) and `r_M` for the **ratio denominator**.

## 2. THE MEASUREMENT

> **`ρ = r(leg B) / r(leg A)`**, both per-step wall rates from `ExecutionTime` deltas
> **within the SAME run**, so the arm, mesh, ranks, `0/` and solver are identical between
> numerator and denominator **by construction**. This is the property that made the
> predecessor's design attractive and **it survives intact** — what changes is that the
> two windows now straddle the `deltaT` boundary the ladder actually crosses.

- **Leg A** = `C4_L1`'s registered leg A: `endTime 0.8`, `deltaT 0.02`, **40 steps**.
  **This is `W_ramp` exactly** — the window every `C4`/`C5` wall factor was measured on,
  which is why it and not the ladder's 70 s leg A is the right denominator: the bias being
  bounded is the bias *of those factors*.
- **Leg B** = `startFrom latestTime`, `deltaT 0.1`, **400 steps**, `t = 0.8 → 40.8 s`.
  A **bounded** sample of the ladder's own soak regime, not an invented span.

**DISCLOSED SCOPE:** leg B here samples `t ≤ 40.8 s` of a soak that runs to `t = 900 s`.
`ρ` bounds the bias **relative to the measurement window**, and the plateau clause of §3
is what licenses reading it beyond the sampled steps. **It is not a measurement at step
11,800 and this document never calls it one.**

## 3. THE GATE

| clause | statistic | threshold | verdict on breach |
|---|---|---|---|
| **G-T6c-1 PLATEAU** *(evaluated FIRST)* | `\|r(last 40 leg-B steps) − r(first 40 leg-B steps)\| / r(last 40)` | **≤ 5 %** | **`NOT A RESULT`** — a leg-B rate still moving cannot bound the rate at step 11,800, and a bound quoted off a moving rate is a false bound. |
| **G-T6c-2 DIRECTION** | `ρ` | **`ρ < 1.0`** | **`GATE FAIL`** — **A1.2's registered direction is FALSIFIED**, and every `CAP` in the C4/C5 line is conservative in the **UNSAFE** direction rather than the safe one. |
| **B-T6c CEILING RELIEF** | `Σ CAP(C4) × ρ_blend` vs the A1.3 ceiling **20,000** | `ρ_blend < 0.809412` (`= 20,000 / 24,709.3`) | **REPORTED, NEVER GATED** — §5. |
| **X-T6c CONSISTENCY** | cost ratio vs `ρ` through the closed form below | — | **REPORTED** — a cross-check, never a gate. |
| **R-T6c** | `r` for every 40-step window of both legs, and `ρ(W)` for each | — | **REPORTED, never gated** — the trajectory, so a reader sees the shape and not two endpoints. |

**Ordering is rule-5-shaped and deliberate:** the plateau clause is step (a); a
non-plateaued rate makes the row `NOT A RESULT` **before `ρ` is consulted**, exactly as
rule 5 step (1) refuses a level that has not converged before any triple is read. **The
gate can only turn a PASS or GATE FAIL into NOT A RESULT, never the reverse.**

**The closed form, registered in advance so the cross-check cannot be fitted after:**
with `N_A = 40`, `N_B = 400`, expected cost ratio against a `ρ = 1` point estimate is
`(N_A + N_B·ρ) / (N_A + N_B)`, so `ρ = ((N_A + N_B)·ratio − N_A) / N_B`. At `ρ = 1` the
ratio is **1.0000**; at `ρ = 0.6861` it is **0.7146**; at `ρ = 0.5`, **0.5455**.

## 4. ⛔ THE AGE GUARD — the region is `module`, and the file that dates the run is `0/module/T`, NOT `0/T`

**Stated in the registration and not in a code comment, because a successor that gets this
wrong produces a rule-4 defect that is SILENT.**

This case family is **`chtMultiRegionFoam`** and the region is **`module`**. The runner
creates `0/` from `0.orig` at launch and then
**`sleep 1; touch "$CASE/0/module/T"`** — **touched LAST, because it dates the run allowed
to produce the answer** (`run_one_t25R5.sh`).

> **A comparator or `mark_done` asserting `0/T` on this family would assert A FILE THAT
> DOES NOT EXIST. The age guard would then never evaluate, and would never say so.**
> Every T25R6c instrument asserts **`0/module/T`**, and asserts that it EXISTS before
> using it as the age datum.

**The stager MUST NOT pre-create `0/`.** `stage_t25R6a.py:21-22` is the authority: a
stager that pre-creates `0/` makes rule 4's age guard **unevaluable for every arm**. The
runner refuses if `0/` exists (**exit 92**) or if any numeric time directory exists
(**exit 93**), and those refusals are load-bearing, not hygiene. **A successor may not
relax this for convenience.**

**Case provenance, named because the predecessor's omission of it is what started this:**
source `verification/runs/T-family/T25R5_LINSOLVER_runs/C4_L1` — `constant/`, `system/`
and `0.orig/` copied; `system/controlDict` = C4_L1's leg A **unchanged**;
`system/controlDict.legB` set to `startFrom latestTime`, `deltaT 0.1`, `endTime 40.8`.
Solver `chtMultiRegionFoam`, **2 ranks**, `mpirun --bind-to none`,
`decomposePar -allRegions`.

## 5. ⛔ WHAT THIS RUNG DOES NOT DO

- **It does NOT authorise a ladder launch.** `T25R5` §5.1 is carried **in force**, exactly
  as `T25R6a` §4.2 carried it: **no ladder launches on this result, whatever it says.**
- **It does NOT measure the soak rate at step 11,800.** It samples `t ≤ 40.8 s` and lets
  the plateau clause license the extrapolation — a weaker claim, registered as the weaker
  claim. `B-T6c` is **REPORTED** precisely because gating a 20,000 core-min decision on a
  440-step probe would misrepresent what the probe can see.
- **It does NOT re-open, widen or retire the A1.3 ceiling of 20,000 core-min**, which is
  not this team's to move.
- **It does NOT consume any output of `T25R6a`.** It reads only `ExecutionTime` deltas
  from logs it produces itself.

## 6. COST — the cap is priced at the FALSIFIER, in two registered brackets

> ### ⚡ THE CAP IS COMPUTED AT `ρ = 1` AND AT THE CONSERVATIVE RATE `r_C`, BECAUSE A CAP MUST NEVER CENSOR ITS OWN FALSIFIER.
>
> The registered prediction is `ρ < 1`: leg-B steps are **cheaper**. A cap priced from
> that prediction would be exceeded **precisely in the world where the prediction is
> false** — `ρ ≥ 1` — so the run would be stopped **exactly when it was about to report
> the falsification.** The optimistic figure is kept **only** as the ratio denominator.
> This is the discipline `T25R6a` §8.2 accepted and it is applied here unchanged.

| bracket | arithmetic | figure |
|---|---|---|
| **CAP bracket** — `ρ = 1` at `r_C` | `(40 + 400) × 0.1594583` | **70.162 core-min** |
| **hard per-run CAP, ~3× its own estimate** | `3 × 70.162` | **210.485 core-min** |
| **fleet safety ceiling** | `min(3 × 210.485, remaining cycle budget)` | **min(631.455, NULL)** |
| **POINT bracket** — `ρ = 1` at `r_M` — **THE RATIO DENOMINATOR** | `440 × 0.1094` | **48.136 core-min** |
| in dollars | estimate **$0.05999**, cap **$0.17996** | **DERIVED, NOT MEASURED**, `$0.0513/core-h`, `cost_basis = REPORTED-BY-OWNER` |
| against the A1.3 ceiling | `210.485 / 20,000` | **1.052 %** |
| escalation triggers | none met — far under the $150 single-run trigger; not a rerun | 2026-09-03 ~18:00Z §4 |

**The `NULL` is deliberate.** The remaining-budget term of the fleet ceiling is **not a
quantity this box can evaluate** — it cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5) — so it is recorded `NULL` rather than filled with a guess,
and the 631.455 term is the one that binds.

**PREDICTED-VS-ACTUAL.** Denominator **48.136 core-min** (`ρ = 1` at the measured arm
rate), fixed here in advance so a successor cannot choose the flattering one. **The ratio
IS the measurement** via §3's closed form: under the registered prediction it lands below
1.0, and A1.2 registered in advance that it would — *"must not be reported as
efficiency."* Waste, if any, is **named separately and folded into no ratio**
(`COMPUTE_BUDGET_CHARTER` §6). The rule-12 calibration row is owed to
`docs/COST_CALIBRATION.md` at completion and is **not** discharged here. **L-463 applies
to this document's own estimate: both brackets above are POINT estimates, not
inequalities.**

## 7. ⚠ OPEN QUESTION, RECORDED SO THE NEXT READER INHERITS IT RATHER THAN RE-FINDING IT

**`T2` and `T4` carry `controlDict` and `controlDict.legB` IDENTICAL to `S1`'s** — leg A
`endTime 70`, leg B `endTime 900` — **yet their registered step counts are exactly 2× and
4× S1's**: 23,600 and 47,200 against 11,800 (`T25R5_PREREGISTRATION.md:58-66`).

**No mechanism for that multiplier was identified by this lane, and none is guessed at
here.** *"Exactly 2× and 4×"* is too clean to be coincidence. If the multiplier is a
multi-arm, multi-design-point or multi-region factor rather than a longer integration, it
**may bear on how any of these step counts should be priced**, including the `11,800` this
document's `r_C` derivation divides into. **Flagged, not resolved. It is not a blocker for
T25R6c**, whose `ρ` is a ratio of two windows inside one run and consumes no ladder step
count.

## 8. What must be true before a row grades

1. **Strict completion (rule 4)** on both legs, with the age guard against **`0/module/T`**.
2. **Mesh identity** — the arm's registered cell count asserted, not assumed (gating by
   derivation from rule 5, per this team's 2026-09-03 classification).
3. **A planted-zero control on the `ExecutionTime` reader** that reads the plant back **AT
   THE PLANTED STEP**, never a maximum or a total over all steps — the defect
   `VERIFICATION_CHARTER` §2d.11.1 found in the T3 control. Its tolerance is **relative to
   the operands it differences**, never a bare absolute below the arithmetic noise floor.
4. **The comparator REFUSES (exit 2) rather than degrades**, is **committed before it is
   first run**, and carries a **FULL sha256 of the disk bytes** as its freeze witness
   (L-450; the forward-only rule this team adopted 2026-09-03).
5. **No control is a bare `assert`** — `python3 -O` strips them.

---

*Drafted and frozen 2026-09-03 by a heat-transfer `lab-lane`. Every figure was re-derived
by this lane from the artifacts named beside it — the leg structure from
`run_one_t25R4.sh:111-127` and the two `controlDict`s on disk, the 3,500 + 8,300 = 11,800
resolution from `S1/system/controlDict{,.legB}`, `r_M` from `B0_L1`'s own log, the age-guard
path from `run_one_t25R5.sh` — and never from a summary handed down. No case directory
exists.*

---

## AMENDMENT v1.1 — 2026-09-03 — **THE GRADING PATH IS FIXED AND PINNED, THE LEGS' INDEPENDENCE IS STATED WITH ITS BREAKING CONDITION, AND ONE REGISTERED CROSS-CHECK IS STRUCK AS A TAUTOLOGY BEFORE IT COULD BE QUOTED AS ONE.**

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered,
inserted or deleted (rule 6); this section is appended at the foot and the pre-amendment
region was byte-compared against the frozen blob `23140f80` before it was written.
**No gate, no threshold, no numeric band, no cap and no label above is altered.**
G-T6c-1 (plateau ≤ 5 %), G-T6c-2 (`ρ < 1.0`), B-T6c (reported), X-T6c (reported), R-T6c
(reported), the 70.162 / 210.485 core-min brackets and the 48.136 core-min
predicted-vs-actual denominator all stand exactly as frozen.

**THE CONDITION, AND HOW IT WAS CHECKED.** Rule 2 makes an amendment legal **before first
compute** and requires it to state the condition and how the condition was checked.
**Zero solver compute has occurred: 0 core-min, $0.00.** At the moment this amendment is
written, `verification/runs/T-family/T25R6c_LEGAB_runs/W440_C4_L1` **exists and is
STAGED** — `ls -a` returns exactly `0.orig`, `constant`, `system` and nothing else: **no
`0/`, no numeric time directory, no `processor*`, no `log.solve.legA`, no
`log.solve.legB`.** Staging copies dictionaries; it starts no solver and spends no
core-minutes. §0's closing sentence *"No case directory exists"* was true at the freeze
`5e51676e` and is **superseded as a statement of fact, not as a gate**: the directory now
exists and holds no answer. Rule 4's age guard remains **evaluable**, which is the whole
reason the stager is forbidden to create `0/`.

### A1.1 GRADING PATH — FIXED HERE, BEFORE FIRST COMPUTE, AND THE GAP IS DISCLOSED RATHER THAN BURIED

**The freeze commit `5e51676e` named no grading script.** That is a procedural gap in the
freeze and it is stated plainly rather than left for a reader to notice. Rule 2's window
for repair is exactly this one — before first compute — and Sanaa's 2026-09-03 ~21:00Z
launch rule puts *"Freeze or procedural state — registration not frozen, pin missing,
lesson not filed"* in the **record-and-launch** class, not the blocking class.

> **GRADING_FREEZE: verification/runs/T-family/T25R6c_LEGAB_runs/grade_t25R6c.py**

| instrument | path | git blob sha1 | sha256 of the disk bytes |
|---|---|---|---|
| **comparator / grader** | `verification/runs/T-family/T25R6c_LEGAB_runs/grade_t25R6c.py` | `39726f664685125bb16d89fd1174686b3a1e813f` | `6463e00bebff3a7bdd8395ee53fd3e2995ce4e05041375416e59c872960c94f8` |
| stager | `verification/runs/T-family/T25R6c_LEGAB_runs/stage_t25R6c.py` | `95e0c1cd6ad592b83b5fb52b472c723f13a64766` | `5d1a9f7f383f1a031c74374e8c97bf9f9602f9bfb2da733a6fac86e398457981` |
| runner | `verification/runs/T-family/T25R6c_LEGAB_runs/run_one_t25R6c.sh` | `49d52d7695fca68d43622058222765939dd83432` | `f306f953fc00ebbe0b49b9d1e62918eefe0e85c3e2f48e1675bf71c841fce9ae` |
| completion marker | `verification/runs/T-family/T25R6c_LEGAB_runs/mark_done_t25R6c.py` | `c11945447835307c2580c51e8d2b51c0f981f078` | `7a208d97de3eeeb428a7a1493d6dceb865cd08d05acae6fc36aecc050cf12add` |

**The four files land in the SAME COMMIT as this amendment**, so the pin and the pinned
objects are one atomic fact and neither can be true without the other. §8.4's FULL-sha256
witness (L-450) is discharged in the table above. **The grader cannot carry its own
sha256 as an internal constant** — writing the constant would change the file and
therefore the constant — so it recomputes and reports both hashes into
`T25R6c_VERDICT.json` at grade time, and **this table is what they are checked against.**

### A1.2 ⚡ WHY LEG A AND LEG B ARE INDEPENDENT, AND THE ONE SHARED ASSUMPTION THAT WOULD BREAK IT

**This section exists because the predecessor died of a false independence claim** and a
successor design is entitled to be told, in the document, exactly what its own claim rests
on.

**THEY ARE INDEPENDENT IN THE ONLY SENSE THAT KILLED T25R6b.** `r(leg A)` and `r(leg B)`
are means over **disjoint sets of `ExecutionTime` deltas**, parsed from **two separate
files** — `log.solve.legA` and `log.solve.legB` — written by **two separate `mpirun`
invocations**, each of which starts its own `ExecutionTime` clock at zero. Neither number
is computed from the other; no quantity appears in both but `ranks` and the constant 60,
and those cancel identically in the ratio. **Nothing in the grader divides one leg's
number by the other leg's number to obtain a third and then offers the third back as
corroboration** — which is precisely what §1 struck.

**WHAT WOULD BREAK IT, named so a reader inherits it rather than re-finds it:**

1. **THE SHARED BOX — the live hazard.** The legs run sequentially on one machine that
   other teams also use. If effective per-core throughput differs between leg A's window
   and leg B's window, **`ρ` absorbs contention as though it were the `deltaT` regime
   change**, and the two samples stop being independent of a common cause. This is
   measured history, not a hypothetical: T25R5 disqualified C1, C2 and C3 to exactly this.
   **Mitigated, not eliminated:** `/proc/loadavg` is witnessed at three points —
   `.load.<RUN>.before_legA`, `.load.<RUN>.between_legs`, `.load.<RUN>.after_legB` — and
   is read beside `ρ`. A witness is not a control; it is disclosed as a witness.
2. **THE RESTART COUPLING.** Leg B starts `latestTime` from leg A's own output, so its
   first steps carry field re-read and matrix re-assembly cost — a genuine leg-A → leg-B
   dependency that is not a `deltaT` effect. **G-T6c-1 is the guard for exactly this**, and
   it is evaluated first: a leg-B rate still moving is `NOT A RESULT` before `ρ` is read.
3. **THE SHARED INSTRUMENT.** Both rates come from one parser. A parser defect cancels in
   the ratio **only if it is multiplicative and identical across the legs**, which restart
   logs do not guarantee. Hence the planted-zero control is planted into **both** leg logs
   and read back **at the planted step** in each.

**THE PLANT'S MAGNITUDE IS A DESIGN DECISION, NOT A COPIED CONSTANT.** OpenFOAM prints
`ExecutionTime` to **two decimals**, so 0.01 s is the smallest perturbation this log can
represent at all. **The T3 constant `1.234e-03` would be annihilated by the print format**
and the control would "pass" by reading a zero it was never able to read. The registered
plant is **`PLANT_S = 1.23 s` at step 7** — exactly representable at the log's own
granularity, 123× it — and the control **refuses (exit 2)** unless the delta at step 7
rose by exactly that and **no other delta moved**. The tolerance is `1e-6 × max(|E[i]|,
|E[i-1]|, PLANT_S)`, **relative to the operands differenced**, never a bare absolute below
the arithmetic noise floor (§8.3).

### A1.3 ⛔ X-T6c AS REGISTERED IS A TAUTOLOGY THROUGH THE RUN'S OWN RATE — STRUCK BEFORE IT COULD BE QUOTED

§3 registers the closed form `ρ = ((N_A + N_B)·ratio − N_A) / N_B`. **Applied to a cost
ratio taken against this run's own `r(leg A)`, it returns `ρ` identically, by algebra:**

> `total = N_A·r_A + N_B·r_B`; `ratio = total / ((N_A+N_B)·r_A) = (N_A + N_B·ρ)/(N_A+N_B)`;
> so `((N_A+N_B)·ratio − N_A)/N_B = ρ`, **exactly, for every input.**

> **~~That route is STRUCK AS A CORROBORATION.~~ It is the same shape §1 struck in the
> predecessor — a number divided back by what built it — and it would have been quoted as
> a cross-check by anyone who did not do the algebra.** It is retained in the grader
> **only** as a parser bookkeeping check, labelled as such in the verdict, and it is
> evidence for nothing about the physics. The grader's selftest **demonstrates the
> identity to 1e-12 rather than asserting it.**

**THE NON-CIRCULAR ROUTE, which is what X-T6c now reports:** actual core-minutes against
the **frozen POINT denominator 48.136 core-min**, whose rate `r_M = 0.1094` was measured on
**`B0_L1` in T25R5 — a different run, on a different arm, before this case existed.**
Nothing this run produces enters it. **No gate, threshold or label moves:** X-T6c was
registered `REPORTED, never a gate` and it remains reported.

### A1.4 B-T6c — THE REGISTRATION FIXES THE THRESHOLD AND NOT THE MIXTURE; BOTH READINGS ARE REPORTED AND NEITHER GATES

§3 fixes `ρ_blend < 0.809412 (= 20,000 / 24,709.3)` and **does not define `ρ_blend`'s step
mixture**. The probe's mixture (40 A + 400 B) and the ladder's (3,500 A + 8,300 B) give
different blends from the same `ρ`, and only the **ladder** mixture means anything for a
statement about the ladder's cost. **This lane resolves nothing and moves nothing.** The
grader prints **both**, labelled, with the ambiguity named in the verdict JSON. B-T6c was
registered `REPORTED, NEVER GATED` and stays so; **the A1.3 ceiling of 20,000 core-min is
not this team's to move and this rung pre-registers no widening and grants none.**

### A1.5 THE CAP IS SPLIT BETWEEN THE LEGS — A DERIVATION FROM THE REGISTERED CAP, NOT A NEW CAP

The registered hard per-run cap is **210.485 core-min at 2 ranks = 6,314.55 wall s**. It is
apportioned **in proportion to the registered step counts, 40 : 400**, so neither leg can
eat the other's budget: **leg A `timeout` 574 s, leg B `timeout` 5,740 s**, and
`(574 + 5,740) × 2 / 60 = 210.4667 core-min ≤ 210.485`. **`run_one_t25R6c.sh` asserts that
inequality at pre-flight and REFUSES (exit 84) if it ever stops holding** — a cap nothing
enforces is not a cap. **The cap's value is unchanged**; only its enforcement is stated.

### A1.6 ⚡ PREDICTION P-C1 — THE FROZEN POINT DENOMINATOR IS PRICED OFF THE WRONG ARM, AND THAT IS RECORDED AS A PREDICTION RATHER THAN REPAIRED

Under Sanaa's 2026-09-03 ~21:00Z rule — *"A pre-registration mismatch never prevents a
launch. It's recorded as a prediction, the run launches under the monitor, and the outcome
is compared to the prediction on the certificate"* — this mismatch is **registered, not
fixed**, because fixing it would move a frozen cost figure.

**The mismatch:** §6's POINT denominator `48.136 = 440 × r_M` uses `r_M = 0.1094`
core-min/step, measured on **`B0_L1`** — the **GAMG baseline**. The case this rung actually
runs is **`C4_L1`**, the PCG arm, which T25R5 measured **13.56× faster at L2**. `C4_L1`'s
own leg A is on disk and took **13.57 ExecutionTime s over 40 steps**.

> **P-C1, A POINT ESTIMATE WITH A STATED BASIS, NEVER AN INEQUALITY (L-463):** at `ρ = 1`,
> the actual will be **`440 × (13.57 s / 40) × 2 / 60 = 4.976 core-min`**, i.e. a
> predicted-vs-actual ratio of **`4.976 / 48.136 = 0.1034`**. **Attribution: MISPREDICTION
> of the arm — not contention and not waste**, which stay separately named
> (`COMPUTE_BUDGET_CHARTER` §6). The grader scores P-C1 `WINS` inside ±50 % of that ratio
> and `LOSES` outside it, and the rule-12 calibration row is owed to
> `docs/COST_CALIBRATION.md` at completion.

**The CAP is untouched and remains priced at the falsifier**, which is the point of §6: the
cap must never censor `ρ ≥ 1`. Being ~10× conservative on the estimate is the **safe**
direction and it is disclosed here rather than discovered in the calibration ledger.

### A1.7 THE STANDING RULES THIS RUNG RUNS UNDER, RESTATED SO THE GRADER'S REFUSALS ARE READABLE

- **Rule 4, strict completion, ALL conjuncts, BOTH legs:** `rc = 0` for each leg from a
  file written **inside** the runner immediately after each `mpirun`; an `End` line;
  **last time == `endTime`** (0.8 for leg A, 40.8 for leg B); the eight fields present in
  every `processor*` directory at `t = 40.8`; `ExecutionTime` count == the registered step
  count (40 and 400 — a **step-count** identity, never a time-value identity); and the
  **AGE GUARD against `0/module/T`**, whose **existence is checked before it is used as a
  datum** (§4). **The comparator REFUSES (exit 2) rather than degrades.**
- **Rule 5, Roache:** **NOT INVOKED, and that is a registered decision.** There is no grid
  family and no functional at convergence here — this is a wall-cost measurement inside one
  transient at one mesh. **No observed order and no GCI is computed, quoted or derivable.**
  A successor reading a grid-convergence claim off these numbers gets `NOT A RESULT`.
- **Verdict vocabulary (rule 1):** `PASS` (`ρ < 1.0`, plateau held), `GATE FAIL`
  (`ρ ≥ 1.0`, plateau held), `NOT A RESULT` (plateau failed, or rule 4 incomplete),
  refusal (exit 2) on a failed planted-zero control — **which issues no verdict at all.**

### A1.8 QUEUE STATE

The queue entry is filed at **`verification/queue/heat-transfer/T25R6c.json`**, naming
`prereg_commit` = the commit that carries **this amendment**, `grading_freeze` = the
grader above, `cwd` = the staged case, `ranks` 2, `cost_core_min_estimate` 48.136 (the
frozen denominator, not a flattering one), `cap_core_min_registered` 210.485.
**ENQUEUEING IS NOT AUTHORISATION** and this lane launches nothing: the daemon launches.
Nothing is sent anywhere (rule 7).

---

*Amendment written 2026-09-03 by a heat-transfer `lab-lane`. Every sha in A1.1 was computed
from the disk bytes by this lane in the same shell invocation that wrote them here; the
tautology in A1.3 was derived on paper and then demonstrated in the grader's selftest; the
13.57 s in A1.6 was read from `T25R5_LINSOLVER_runs/C4_L1/log.solve.legA`. No solver has
run for this rung.*
