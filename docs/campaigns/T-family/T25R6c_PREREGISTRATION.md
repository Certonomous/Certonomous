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
