# T25R6b — BOUNDING the ramp→soak bias whose DIRECTION is registered and whose MAGNITUDE nothing in this lab measures

> **STATUS: FROZEN BY COMMIT. NOT ENQUEUED.**
> Frozen by the commit that first lands it, per standing rule 2: the gate,
> threshold, cap and label are committed **before any compute**, and **no
> `T25R6b` case directory exists at the moment of this freeze** — verified, so the
> freeze is true by construction rather than by assertion. **Enqueueing is the
> heat-transfer supervisor's separate act** and is withheld from the lane that
> wrote this. This lane does not launch; the daemon launches. Nothing is sent
> anywhere (rule 7).
>
> **THE QUESTION THIS ANSWERS WAS DEFERRED, NOT ANSWERED.**
> `T25R6a_PREREGISTRATION.md` §4.2: *"The window-position question — does the
> factor measured on steps 1–40 survive a 10× longer window — is DEFERRED to a
> separate registration (`T25R6b`) with its own gate, its own falsifiers and its
> own cap. It is deferred, not answered, and a reader must not convert this rung's
> silence into a settled answer."* This is that registration.

---

## 1. The gap, stated exactly

**The DIRECTION of the bias is established from frozen text. Its MAGNITUDE is not,
and nothing in this lab currently bounds it.**

`T25R4_PREREGISTRATION.md:443-452` (A1.2), verbatim:

> *"The probe measures `t ∈ [0, 2] s` — which contains the t = 0→1 s ramp and the
> start-up transient, the most expensive 2 seconds of the whole 900 s run. Cruise
> steps are cheaper. **So `r(L)` OVER-estimates the ladder's mean per-step cost,
> `POINT` over-estimates the ladder's cost, and `CAP` is conservative in the safe
> direction.** … The actual/predicted ratio at completion will therefore read
> BELOW 1.0 for a reason that is registered here and must not be reported as
> efficiency."*

`T25R6a_PREREGISTRATION.md:761-763` states the gap in its own words: §2.3(b)
*"establishes the **direction** of the bias from frozen text (A1.2) but **not its
magnitude**, which no measurement in this lab currently bounds."*

**Everything downstream inherits it.** Every wall factor in the C4/C5 line is
measured over **40 steps at `deltaT 0.02`** (`t = 0 → 0.8 s`) while the ladder runs
**11,800–47,200 steps** (`t → 900 s`) — **0.34 % of the shortest ladder run, and it
is the ramp, not the soak** (`T25R6a` §4.2). `Σ CAP(C4) = 24,709.3` core-min and
its **×1.24 breach** of the A1.3 ceiling of 20,000 rest entirely on the assumption
that a 40-step ramp rate holds for the whole run.

**That assumption has never been tested. This rung tests it.**

## 2. ⚡ THE PREDICTION — registered before any arm exists, and it can lose

**`ρ` is the quantity.** Define the per-step wall rate over a window of steps
`r(W) = Δ ExecutionTime(W) / (steps in W)`, and

> **`ρ = r(W_late) / r(W_ramp)`**, where `W_ramp` = steps **1–40** (the exact window
> every C4/C5 factor was measured on) and `W_late` = steps **361–400**.

| | prediction | what it would mean |
|---|---|---|
| **REGISTERED PREDICTION** | **`ρ < 1.0`** | A1.2's registered direction is confirmed: cruise steps are cheaper than ramp steps, and every `POINT`/`CAP` in the C4/C5 line is conservative in the safe direction. |
| **THE FALSIFIER, and it is a real one** | **`ρ ≥ 1.0`** | **A1.2's registered direction is WRONG.** Every `CAP` in the line would then be conservative in the *unsafe* direction, and the ×1.24 breach would be an under-statement rather than an over-statement. **This outcome is publishable and this rung is designed to be able to produce it.** |

**`ρ` is a ratio of two windows of the SAME run**, so the mesh, the arm, the ranks,
the `0/` and the solver are identical between numerator and denominator by
construction. Nothing about `ρ` depends on a second run being comparable to a first.

## 3. THE GATE

| clause | statistic | threshold | verdict on breach |
|---|---|---|---|
| **G-T6b-1 PLATEAU** *(evaluated FIRST)* | `\|r(W_late) − r(W_mid)\| / r(W_late)`, with `W_mid` = steps **321–360** | **≤ 5 %** | **`NOT A RESULT`** — a rate still changing at step 400 cannot bound the rate at step 11,800, and a bound quoted off a moving rate is a false bound. |
| **G-T6b-2 DIRECTION** | `ρ` | **`ρ < 1.0`** | **`GATE FAIL`** — A1.2's registered direction is falsified. |
| **B-T6b CEILING RELIEF** | `Σ CAP(C4) × ρ` vs the A1.3 ceiling **20,000** | `ρ < ρ* =` **0.809412** (`= 20,000 / 24,709.3`) | **REPORTED, NEVER GATED** — see §4. |
| **R-T6b** | `r(W)` for **every** 40-step window across the run, and `ρ(W)` for each | — | **REPORTED, never gated** — the whole trajectory, so a reader can see the shape rather than two endpoints. |

**Ordering is rule-5-shaped and deliberate:** the plateau clause is step (a). A
non-plateaued rate makes the row `NOT A RESULT` **before `ρ` is consulted**, exactly
as rule 5 step (1) refuses a level that has not converged before any triple is read.
**The gate can only turn a PASS or GATE FAIL into NOT A RESULT, never the reverse.**

## 4. ⛔ WHAT THIS RUNG DOES **NOT** DO

- **It does NOT authorise a ladder launch.** `T25R5` §5.1 is carried into this
  document **in force**, exactly as `T25R6a` §4.2 carried it: **no ladder launches on
  this result, whatever it says.** A `ρ` that erases the ×1.24 breach on paper is a
  *bound on a bias*, not a licence to spend 20,000 core-minutes.
- **It does NOT measure the soak rate at step 11,800.** It measures the rate at
  **step 400** and, via the plateau clause, whether that rate has stopped moving.
  **A plateau at step 400 is evidence about steps 361–400 and an EXTRAPOLATION
  beyond them** — a weaker claim than "the soak rate is X", and it is registered
  here as the weaker claim on purpose. `B-T6b` is REPORTED for precisely this
  reason: it would be dishonest to gate a ladder-ceiling decision on a 400-step
  probe when the object of the extrapolation is a 47,200-step run.
- **It does NOT consume `C5`'s wall factor, or any output of `T25R6a`.** See §5.
- **It does NOT re-open, widen or retire the A1.3 ceiling of 20,000 core-min**,
  which is not this team's to move.

## 5. ⚡ IT STANDS WHICHEVER WAY `T25R6a` FALLS — and here is why, not merely that

`T25R6a` grades `G-T6a`: whether `C5`'s **40-step wall factor** prices the ladder
inside the ceiling. `T25R6b` measures `ρ`: the **ratio of two per-step rates inside
its own run**. The two consume disjoint inputs — `T25R6b` reads only
`ExecutionTime` deltas from a log it produces itself, and reads **no** `C4`/`C5`
factor, no `GT5_VERDICT.json`, no `P3_SCORE.json`.

| if `T25R6a` returns | `T25R6b` is | because |
|---|---|---|
| **`G-T6a PASS`** (C5 prices inside the ceiling on ramp arithmetic) | **still decision-relevant** | `ρ` quantifies **how much conservatism sits inside that pass**. A pass built on a rate biased high by an unknown factor is a pass whose margin is unknown. |
| **`G-T6a GATE FAIL`** | **still decision-relevant, and more so** | `ρ` says whether the failure is **an artifact of the ramp bias**. `ρ < 0.809412` would mean the ×1.24 breach is a property of the *measurement window*, not of the ladder. |
| **`NOT A RESULT`** | **unaffected** | `ρ` needs no verdict from `T25R6a`, only a running solver of the same arm. |

**The one dependency, disclosed:** `T25R6b` runs the **same arm and level (L1)** so
that `W_ramp` is the *same window on the same configuration* the C4/C5 factors were
measured on. If `T25R6a` were to establish that the L1 arm is misconfigured, that
would invalidate the arm for both rungs alike — a shared premise, not a dependency of
`T25R6b` on `T25R6a`'s **verdict**.

## 6. COST — rule 12, and the CAP is priced at the FALSIFIER

**The rate, derived two independent ways and agreeing to six significant figures:**

| route | arithmetic | core-min/step |
|---|---|---|
| from the frozen price table | `POINT(S1) / N(S1) = 1,881.6 / 11,800` | **0.1594576** |
| from the measured `s_per_step` | `(229.62 / 48) s × 2 ranks ÷ 60` | **0.1594583** |

*(`T25R5_PREREGISTRATION.md:58-66` for the table; `:72-73` for `s_per_step` at 2
ranks. The agreement is a check, not a coincidence, and it is why this cap is not
quoted from a single source.)*

> ### ⚡ THE CAP IS COMPUTED AT `ρ = 1` — THE NO-SPEED-UP CASE — **BECAUSE A CAP MUST NEVER CENSOR ITS OWN FALSIFIER.**
>
> This rung's registered prediction is `ρ < 1`: soak steps are **cheaper**. If the
> cap were priced from that prediction, then the world in which the prediction is
> **false** — `ρ ≥ 1`, every step costing what a ramp step costs or more — is
> **exactly the world in which the run exceeds its cap and is stopped before it can
> report the falsification.** A cap built on the hypothesis would delete the
> evidence against the hypothesis.
>
> **So: `CAP` is priced at `ρ = 1.0`, and the optimistic figure is kept only as the
> predicted-vs-actual denominator.** This is the discipline accepted for `T25R6a`
> and it is applied here for the same reason.

| item | figure | basis |
|---|---|---|
| **N steps** | **400** — 10× the 40-step registered window; `t = 0 → 8 s`, past the `t = 0→1 s` ramp | §2 |
| **ESTIMATE, priced at `ρ = 1` (no speed-up)** | `400 × 0.1594576 =` **63.783 core-min** | the CAP basis |
| **hard per-run CAP, ~3× its OWN estimate** | **191.349 core-min** | the 2026-09-03 ~18:00Z envelope: *"a hard per-run cap (set by the team at ~3× its own estimate, not by me)"* |
| **fleet safety ceiling** | `min(3 × 191.349, remaining cycle budget) =` **min(574.047 core-min, remaining)** | the 2026-09-03 ~21:00Z launch rule's one surviving hard stop |
| in dollars | estimate **$0.05453**, cap **$0.16360** | **DERIVED, NOT MEASURED** — `63.783/60 × $0.0513/core-h`; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5). `cost_basis = REPORTED-BY-OWNER`. |
| against the A1.3 ceiling | CAP is **0.957 %** of 20,000 core-min | — |
| escalation triggers | **none met** — far under the $150 single-run trigger; not a rerun of anything | 2026-09-03 ~18:00Z §4 |

**PREDICTED-VS-ACTUAL, AND THE POINT OF IT.** The denominator is the `ρ = 1` figure
**63.783 core-min**. **The ratio actual/predicted IS the measurement**: under the
registered prediction it comes in **below 1.0**, and A1.2 already registered that it
would — *"must not be reported as efficiency."* It is reported here as **the bias
being measured**, which is the one context in which that ratio is not a calibration
artifact. Waste, if any, is **named separately and folded into no ratio**
(`COMPUTE_BUDGET_CHARTER` §6). The rule-12 calibration row is owed to
`docs/COST_CALIBRATION.md` at completion and is **not** discharged by this document.

## 7. LAUNCH DISCIPLINE

Per Sanaa 2026-09-03 ~21:00Z: **a pre-registration mismatch never prevents a
launch.** Any mismatch found at launch is **recorded as a prediction**, the run
launches under the monitor, and the comparison lands on the certificate. Only a
**resource gate** (box busy, memory), a **physically ill-posed setup**, or
**exceeding the remaining cycle budget** holds this row — and a resource gate
**queues** it rather than blocking it.

**This lane does not launch.** The queue entry is validated against the runner's
validator and the daemon launches it. The row carries the fleet ceiling
`min(3 × registered cap, remaining budget)` computed in §6.

## 8. What must be true before a row grades

1. **Strict completion (rule 4)** including the age guard, on the probe run.
2. **Mesh identity** — the L1 arm's registered cell count, asserted, not assumed
   (gating by derivation from rule 5, per this team's 2026-09-03 classification).
3. **A planted-zero control on the `ExecutionTime` reader**, and it must **read back
   the plant AT THE PLANTED STEP**, never a maximum or a total over all steps — the
   defect `VERIFICATION_CHARTER` §2d.11.1 found in the T3 control. Its tolerance is
   **relative to the operands it differences**, never a bare absolute below the
   arithmetic noise floor.
4. **The comparator REFUSES (exit 2) rather than degrades**, and is **committed
   before it is first run**.
5. **No control is a bare `assert`** — `python3 -O` strips them.

---

*Drafted and frozen 2026-09-03 by a heat-transfer `lab-lane`. Every figure above was
re-derived by this lane from the frozen artifacts named beside it — the price table
at `T25R5_PREREGISTRATION.md:58-66`, `s_per_step` at `:72-73`, A1.2 at
`T25R4_PREREGISTRATION.md:443-452`, the deferral at `T25R6a_PREREGISTRATION.md`
§4.2 — and never from a summary handed down. No case directory exists.*

---

## AMENDMENT v1.1 — 2026-09-03 — **THIS REGISTRATION IS SUPERSEDED BY `T25R6c` AND WITHDRAWN BEFORE ANY COMPUTE. THE DEFECT IS IN ITS DESIGN, NOT ITS CASE SOURCE.**

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered,
inserted or deleted (rule 6). **Zero solver compute; 0 core-min; $0.00.** **No gate,
threshold, cap or label above is altered by this amendment** — the design they belong to
is withdrawn entire.

**STATE AT WITHDRAWAL: NO COMPUTE, NO CASE DIRECTORY, NO ENQUEUED ROW.**
`verification/runs/T-family/T25R6b_runs/W400_L1` never existed — verified, and its absence
is the same condition rule 2 requires an amendment to state and to say how it was checked.
Nothing is re-graded, no verdict is withdrawn, and no row anywhere depends on this document.

### A1.1 THE GROUND — the instrument contained 29.7 % of the bias it existed to bound

§2 registered `ρ` over **400 steps at `deltaT 0.02`**. Reading the case family *before*
binding a case source to it — the check that produced this amendment — established that a
ladder run is **two legs**: leg A at `deltaT 0.02` and leg B at `deltaT 0.1`
(`run_one_t25R4.sh:111-127`). The registered ladder step count resolves exactly:
**`S1` leg A `70/0.02` = 3,500 + leg B `830/0.1` = 8,300 = 11,800**, matching
`T25R5_PREREGISTRATION.md:58-66` to the digit.

> **70.3 % of ladder steps are leg-B steps at a 5× larger timestep.** A1.2's ramp→soak
> bias therefore has **two components** — window position **and** the `deltaT` regime
> change — and **this document's instrument contained only the first.** A registration
> that measures 29.7 % of a bias and is read as bounding all of it is **worse than no
> registration**: it would have produced a confident number, wrong in a direction nobody
> would have checked.

Compounding it, §6's **400 steps at `deltaT 0.02` to `t = 8 s` is leg A of nothing
registered** — `C4_L1`'s leg A ends at 0.8 s and the ladder's at 70 s. **The span was
invented.**

**AND IT COULD NOT HAVE BEEN REPAIRED BY AMENDMENT.** A corrected `ρ` requires a new cap,
and rule 2 forbids an amendment that alters a cap. Supersession was the only lawful route.

### A1.2 ⚡ §6's "TWO INDEPENDENT ROUTES" CLAIM IS **STRUCK** — it is a tautology

§6 asserted the per-step rate was *"derived two independent ways and agreeing to six
significant figures"*: `1,881.6 / 11,800 = 0.1594576` and `(229.62/48) × 2/60 =
0.1594583`.

> **~~STRUCK.~~** `POINT(S1)` was **built** as `N × r(L1) × 2/60` (A1.1's frozen formula),
> so dividing it back by `N` recovers `r(L1) × 2/60` **by algebra**. The two figures agree
> because **they are the same number**. This was a **false corroboration**, it was carried
> upward before it was caught, and it is struck here rather than rewritten (rule 6).

**The rate's VALUE is unaffected** and remains sound as a conservative cap basis.
**Genuine, independent corroboration exists and points the other way:** `B0_L1`'s own
40-step run measures **0.1094000 core-min/step** against the probe's **0.1594583** —
**the probe rate is 1.4576× the arm rate.** A1.2's bias is already visible on disk. That
measured number is carried into `T25R6c` §1 as evidence.

### A1.3 WHAT SURVIVES INTO `T25R6c`, UNCHANGED

The **same-run construction** (arm, mesh, ranks and `0/` identical between numerator and
denominator), the **falsifier** `ρ ≥ 1.0`, the **plateau clause evaluated first** in
rule-5 shape, the **REPORTED-never-gated** ceiling-relief clause, `T25R5` §5.1 carried in
force, and **the cap priced at `ρ = 1` so it cannot censor its own falsifier**. Only the
windows, the span and the cap change.

### A1.4 DISPOSITION OF THE HELD QUEUE ROW

`verification/queue/heat-transfer/held/T25R6b_W400_L1.json` — which the runner's own
validator **REFUSED** (`EXEC: cwd … does not exist`) and which therefore never entered the
queue path — is **WITHDRAWN**, not re-pointed. A row pointing at a superseded design is
worse than no row.

**Successor:** `docs/campaigns/T-family/T25R6c_PREREGISTRATION.md`.
