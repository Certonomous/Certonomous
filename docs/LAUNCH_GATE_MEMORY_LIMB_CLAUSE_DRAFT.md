# The launch-gate memory limb — DRAFT of a `VERIFICATION_CHARTER.md` §2e-sibling clause

**DRAFT — AWAITING SANAA. NOT IN FORCE. This document changes no charter.**
Nothing here is adopted, and nothing here may be cited as binding. Retiring,
widening or adopting a gate threshold or a charter clause is Sanaa's decision
alone (`CLAUDE.md` FIRST-ACTION RULE, *"Reserved to Sanaa"*;
`ESCALATION_CHARTER.md` §2, *"Drafting proposals. Initiative is the lab's.
Drafting is not deciding."*). `VERIFICATION_CHARTER.md` is untouched by this
lane: no line of it was edited, and rule 6 forbids editing a frozen file in any
case. If ratified, the clause below would be **appended at the foot** of that
charter as **§2f**, in the manner §2c, §2d, §2d.1 and §2e were appended, each
carrying *"Lines whose number changed above this section: 0."*

Written by a `lab-lane` of the verification team, 2026-08-24, on the
verification supervisor's dispatch. **Zero solver compute.** The cost of the
draft itself is in §8.

**Provenance of the proposal, and it is not this team's.** The rule is
**dafoam's**, proposed by that team out of its own kill: `docs/LESSONS.md`
**L-262** and the calibration row **C-10** in `docs/COST_CALIBRATION.md`. This
team's contribution is an evaluation, three refinements, a boundary, an
instrument spec and a second worked instance. **What this document recommends
is that Sanaa decide; it does not decide.**

---

## 1. The proposal as dafoam stated it, quoted rather than restated

`docs/LESSONS.md:9807` — L-262's title:

> A memory launch gate must exceed the floor PLUS the arm's own measured peak —
> a gate that admits an arm whose consumption drives the host under the mid-run
> floor is a registration that kills itself

and its binding sentence, same block:

> the launch gate is derived as **floor + the largest measured (or explicitly
> estimated, labelled so) own-peak among the arms + margin**, and a registration
> whose gate cannot satisfy its own floor at the registered peaks is refused at
> review, not discovered at kill time.

The same finding, reached independently in the calibration ledger, at
`docs/COST_CALIBRATION.md:70` (row **C-10**, in the HEAD blob — see the
disclosure in §9):

> **Rule to carry forward: a launch gate's memory limb must be at least (the
> arm's predicted peak + the neighbourliness floor).**

**Verification's evaluation, recorded on this team's board at commit
`f536b114` (`docs/LAB_STATE.md`, 2026-08-24T16:15:20Z):** the rule is **SOUND as
a necessary condition and arithmetically forced** — *"a gate at 16 GiB with an
8 GiB floor admits a 9.2 GiB arm that breaches the floor before any co-tenant
moves."* It is **not sufficient**, and the three refinements in §2 are the gap
between the two.

---

## 2. The three refinements, quoted from the board that recorded them

Recorded at `f536b114` and carried forward at `9d1d348a`
(`docs/LAB_STATE.md`, verification section, 2026-08-24):

> **(i)** *"predicted peak" must be the arm's REGISTERED UPPER band, not its
> point estimate, and the memory band must be priced from a measured fill on
> the same operator class (C-15's lesson) — an under-predicted peak defeats the
> rule silently;
>
> **(ii)** the limb must also reserve co-tenant growth: floor + peak + the
> registered growth allowance of the live solvers at launch (four
> `buoyantBoussinesqSimpleFoam` arms grow at write intervals), else the rule
> protects the floor only at t = 0;
>
> **(iii)** the guard's floor limb must sample `MemAvailable`, not `MemFree`, at
> the same cadence the launch gate polled, and the launch gate must record the
> margin it opened on (C-10 opened at 0.02 GiB) — a gate that opens on poll 2
> with 0.02 GiB margin is a gate that will fail the floor.

**Why each refinement is load-bearing and not decoration.**

- **(i) closes the silent-defeat path.** A limb built from a point estimate is
  arithmetically valid and epistemically empty: the rule then holds against a
  number the registration chose, not against the number the arm will reach.
  Attempt 2's point was **11.65 GiB** and its measured peak **11.680 GiB**
  (+0.2575 %) — the point was very nearly right, and that is exactly the case in
  which a lab learns nothing about what happens when it is not. The upper
  endpoint is the only one the registration is scored against under a band.
- **(ii) closes the t = 0 path.** L-262's arithmetic is evaluated at the instant
  the gate opens. Every co-tenant on this box is free to grow afterwards, and
  the named growth mechanism is real: OpenFOAM arms allocate at write intervals.
  A limb that reserves nothing for co-tenant growth protects the floor for one
  sample.
- **(iii) closes the instrument path, and it is two separate requirements.**
  `MemFree` excludes reclaimable page cache and therefore **understates**
  available memory, so a floor limb read on `MemFree` fires early and a *gate*
  limb read on `MemFree` refuses to open on a box that is in fact free — the
  quantity the floor is about is `MemAvailable`. And the **recorded margin** is
  what converts a gate from a boolean into evidence: attempt 1's gate returned
  *true* at **+0.02 GiB** of margin, which is indistinguishable from *false* in
  every way that matters and was recoverable only because the poll value was
  written down.

**One honest amendment this lane makes to (iii), from the measured instance.**
The board wrote *"at the same cadence the launch gate polled."* In the instance
that actually ran, the launch gate polled at **60 s** and the guard sampled at
**5 s** — twelve times denser, and correct. The requirement that the instance
supports is therefore **"at a cadence at least as dense as the launch gate's
poll interval, with the achieved cadence measured from the guard trace and
recorded"** — attempt 2's trace gives 87 samples over 521 s with a **maximum
observed inter-sample gap of 7 s** against a 5 s armed cadence, which is the
form the record should carry. Equal cadence is a floor on density, not a target.

---

## 3. The clause, DRAFT

> **THE LAUNCH-GATE MEMORY LIMB (DRAFT, not in force).**
>
> **A pre-registration that gates a run on host memory registers a launch-gate
> memory limb of at least `neighbourliness floor + the registered UPPER endpoint
> of the arm's own peak band + the registered co-tenant growth allowance`, and
> shows that arithmetic in the document. The upper endpoint is priced from a
> measured fill on the same operator class, cited by path and line; a point
> estimate does not price it. The growth allowance names the co-tenants live at
> launch and the mechanism by which they grow. The guard samples
> `MemAvailable`, never `MemFree`, at a cadence at least as dense as the launch
> gate's poll interval, and the gate records to an artifact the margin it opened
> on. A registration whose limb cannot satisfy its own floor at its own
> registered peaks is REFUSED AT REVIEW, before compute — a gate discovered to
> be self-defeating at kill time has already been paid for. On a strike the
> guard stops the arm; the arm is `NOT A RESULT`, its spend is reported gross
> and its waste is named; it does not get a new budget.**

**Placement, if ratified.** At the foot of `VERIFICATION_CHARTER.md`, numbered
**§2f**, read with §2b (freeze), §2d/§2d.1 (the comparator freeze and its repair
exception) and §2e (what a band may contain) — §2e is the nearest sibling
because both clauses govern **what a pre-registered band must cite before it may
be armed**, and this one extends that from a *graded* band to a *gating* one.
The insertion carries the same assertion those four carry: *"Lines whose number
changed above this section: 0."* **Sanaa's ratification is the only thing that
would put it in force.**

---

## 4. The four conditions a pre-registration must carry

Each is a thing a reviewer can check on the document alone, before any compute.

### 4.1 The limb arithmetic, shown

The limb is written as a **sum with named terms**, not as a single number:

```
limb = floor + upper(own-peak band) + growth allowance
```

with every term and the total in GiB, and the inequality
`limb − upper(own-peak band) ≥ floor` stated and evaluated in the document.
Attempt 2 does exactly this at `PREREGISTRATION.md:1146` —
`8.0` floor `+ 15.0` (R3-P11 registered UPPER) `+ 2.0` co-tenant `= 25.0 GiB` —
and that line is what makes the registration reviewable in one reading.

**A single number satisfies no part of this condition.** Attempt 1's
`MemAvailable ≥ 16 GiB` (`PREREGISTRATION.md:423`, restated at `:428`) is
arithmetically indistinguishable from a correct limb until the terms are named,
which is why it survived review.

### 4.2 The upper band, and the measured fill that priced it

The pre-registration cites, **by path and line**, the measurement the peak band
was priced from, and states that it was taken on the **same operator class** —
same solver, same operator, same rank count, comparable mesh. The **UPPER**
endpoint is the number that enters the limb. A point estimate may be reported
beside it and may not replace it.

The band must also carry a **completeness clause**, because an incomplete peak
is not a peak. Attempt 2 registered one, at `PREREGISTRATION.md:539`:

> If the arm is stopped before the preconditioner assembly completes, the peak
> is **INCOMPLETE** and R3-P11 is scored `NOT A RESULT`, never as a HIT inside a
> band it never approached.

That clause is what makes attempt 2's 11.680 GiB scoreable and attempt 1's
9.202 GiB not — attempt 1 died at roughly **7 % of preconditioner assembly**
(`rung3_patched_idwarp_np4/RESULTS.md:108`), so its peak is a lower bound
wearing a peak's clothes, and it is the number a limb must **not** be built
from.

### 4.3 The co-tenant growth allowance, and its source

The pre-registration **enumerates the co-tenants live at launch** — solver
family and count — names the **mechanism** by which each grows (for OpenFOAM
arms, allocation at write intervals), and states the allowance in GiB with the
registration or measurement it comes from. An allowance of zero is permitted and
must be **stated as zero with its reason**, never left absent: an absent
allowance and a zero allowance read identically in the document and differ
entirely in what the author checked.

**This is the condition the measured evidence supports least, and the draft says
so rather than hiding it — see §6.3.**

### 4.4 The guard's cadence, its quantity, and the margin recorded at open

Three sub-conditions, all checkable on the frozen document:

1. The guard reads **`MemAvailable`** from `/proc/meminfo`. Not `MemFree`.
2. Its **armed cadence** is at least as dense as the launch gate's poll
   interval, and the **achieved** cadence — sample count, span, and maximum
   observed inter-sample gap — is measured from the trace and recorded at
   close-out. Attempt 2: 87 samples, 521 s span, 5 s armed, **max gap 7 s**.
3. The gate **writes the margin it opened on** to an artifact named in the
   pre-registration. Attempt 2 wrote it to `launch_condition.txt`; attempt 1's
   `+0.02 GiB` survived only in the run record. A gate that records only
   *opened* has destroyed the evidence that would have condemned it.

---

## 5. What the guard does on a strike

Unchanged from the law already in force; restated so the clause is
self-contained and so nothing here reads as a new allowance.

- **It stops the arm.** Stopping a run is the lab's own call and needs no
  permission (`ESCALATION_CHARTER.md` §2, *"Stopping a run. Always."*).
- **The arm is `NOT A RESULT`** — the fixed vocabulary of `CLAUDE.md` rule 1 and
  `VERIFICATION_CHARTER.md` §2, no synonym, and specifically **not** `GATE FAIL`:
  nothing was graded, the measurement never happened.
- **The spend is reported gross and the waste is named separately**
  (`COMPUTE_BUDGET_CHARTER.md` §6; `CLAUDE.md` rule 12). C-10 is the worked
  form: **6.80 core-min measured** against **52.5 core-min registered**, with
  **5.667 core-min named as WASTE** — the whole solver arm, returning none of
  the 11-checkpoint identity the item was bought for. By-products that *were*
  returned are **not netted off**.
- **It does not get a new budget.** Rule 12: an overrun stops the run. A stop
  under this clause is not an overrun — the arm was well inside its own budget,
  at 85 s of 2600 s — and the successor is a **new registration**, costed afresh,
  not a continuation.
- **The frozen numbers are not touched.** Gates close after first compute
  (rule 2), and §2d.1's closing sentence governs: *"Nothing a verdict depends on
  may be repaired on the authority of the verdict it produces."* Attempt 1 left
  both registered numbers untouched and re-registered; that is the pattern this
  clause endorses, and it is the reason attempt 2 exists as a separate item.

---

## 6. What this clause does NOT reach

Written in §2c's form, and for §2c's reason: `VERIFICATION_CHARTER.md` §17a
records that **a rule over-reaches as easily as it under-reaches**, and the
boundary is the load-bearing half. Stated here so nobody re-derives it by
spending.

### 6.1 A de minimis single-rank run

The clause does not reach a run whose registered upper own-peak is at or below
a **de minimis threshold X**, proposed here at **X = 1.0 GiB at np = 1**.

**X is a JUDGEMENT, not a measurement, and this draft refuses to disguise it as
one.** The mechanism the clause defends against requires
`limb − upper_peak < floor`; below some peak the term is dominated by ordinary
box noise and the limb reduces to the floor plus rounding. Where that crossover
sits was **not measured** — it would take the distribution of own-peak RSS over
the lab's np = 1 runs, and no such distribution exists on disk. Until it does,
**1.0 GiB is a proposal**, and the clause's requirement is not that small runs be
exempt silently but that the pre-registration **state** `de minimis, limb not
derived, registered upper peak <= 1.0 GiB at np = 1` — an exemption claimed is
reviewable, an exemption assumed is not.

### 6.2 A run on an otherwise idle box — and idleness is EVIDENCED, not asserted

The clause does not reach a run launched onto a box with no co-tenants. But
**"the box was idle" is a claim of the same class as a zero**, and `CLAUDE.md`
rule 3 governs claims of that class: a zero from a reader not shown able to see
a non-zero is not evidence.

**A process sweep does not evidence idleness on this box.** L-41 is explicit
that **fleet agents are invisible to `pgrep`**, so an empty `pgrep` is exactly
the unsupported zero rule 3 refuses. Idleness is evidenced instead by
**quantities that cannot hide**:

1. The gate's own reading at open — `MemAvailable` and free cores — **written to
   an artifact**, with the margin (§4.4.3). Attempt 2: 27.19 GiB and 13 free
   cores, margin +2.19 GiB and +9 cores.
2. The **guard trace over the whole run**: minimum `MemAvailable`, sample count
   and maximum inter-sample gap. Attempt 2's minimum of **15.2871 GiB** against
   an 8.0 floor is what evidences a quiet box; the process table is not.
3. A **co-tenant census** at launch, recorded — and recorded as *what the
   census could see*, since (1) is what covers what it could not.

An idleness exemption resting on (1) and (2) is evidenced. One resting on a
process sweep alone is refused, and the clause should say so in those words.

### 6.3 It does not certify that any particular allowance is sufficient

**The clause is a NECESSARY condition and this draft claims nothing more.**
Attempt 2 is one draw. Its 2.0 GiB co-tenant allowance was never tested: the
**A1.2 co-tenant gap — 4.0 GiB between arm O's registered 2.0 GiB ceiling and
its enforced 6.0 GiB cap — was not realised on that day**, so a 2.0 GiB
allowance stands unproved against a 4.0 GiB exposure. The audit says so itself
(`docs/CROSS_TEAM_GATE_AUDIT.md` §76, *"one draw is not a calibration"*), the
item says so at its own `RESULTS.md` §5.2, and this draft carries it forward
rather than letting a passing run read as a validated allowance.

### 6.4 It withdraws no published verdict and moves no number

It is prospective. It does not reopen a graded rung, it does not license
widening a registered band, and it does not convert a run that survived its
guard into a validated one.

### 6.5 It does not reach the guard's own correctness

The guard is a separate instrument with a separate control — attempt 1's guard
was **proved able to kill by its own selftest three minutes before it killed**,
and it was right. L-262's closing sentence is the boundary: *"The instrument was
right; the registration design was wrong — spend the review on the pair, not the
guard."*

---

## 7. The two instances, worked

Both are on disk. Every figure below cites the artifact it came from.

### 7.1 Instance A — the kill. A3 rung 3, patched-IDWarp, np = 4, ATTEMPT 1

Pre-registration frozen at **`97a54c07`**; record committed at **`67edcc19`**;
calibration row **C-10**; run root
`/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/`.

| quantity | registered | measured | artifact |
|---|---|---|---|
| Launch-gate memory limb | **`MemAvailable ≥ 16.0 GiB`**, single term, 60 s poll, ≤ 240 polls | — | `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4/PREREGISTRATION.md:423`, `:428` |
| Neighbourliness floor | host `MemAvailable` **< 8.0 GiB**, 3 consecutive 5 s samples → kill | — | same file, `:342`, `:410` |
| Own-peak band (R3-P7) | **9.0 – 14.0 GiB** vs a 16 GiB container cap | — | same file, `:331` |
| RSS guard ceiling | **15.0 GiB** | 0 samples above it | same file, `:342` |
| Gate open | — | **poll 2**, `MemAvailable` **16.02 GiB**, margin **+0.02 GiB** | `.../rung3_patched_idwarp_np4/RESULTS.md:73` |
| Own peak RSS | — | **9.202 GiB**, and **INCOMPLETE** — 7 % of preconditioner assembly | `RESULTS.md:45`, `:108` |
| Host floor | — | **BREACHED at 7.3944 GiB**, 3 strikes at 5 s = 15 s | `RESULTS.md:56-61` |
| Outcome | 757 s / 50.5 core-min expected, 2600 s timeout | **killed at 85 s**, `rc=137`, **0 of 11 checkpoints** | `RESULTS.md:24`, `:92`, `:194` |
| Cost | **52.5 core-min** (band 32.0 – 79.1, ceiling 176.0) | **6.80 core-min**, **WASTE 5.667 core-min named** | `docs/COST_CALIBRATION.md` **C-10** |

**The arithmetic, and it needed no run to see.** `16.0 − 9.2 = 6.8 GiB`, against
a registered floor of `8.0`. The registration was **self-defeating for any arm
peaking above `limb − floor = 8.0 GiB`**, and the arm's own registered band
started at **9.0**. The pair was inconsistent **in the frozen document**, and the
review that would have caught it costs one subtraction. What it cost instead was
6.80 core-min, 5.667 of them waste, and the entire finding the item was bought
for.

**Under the draft clause this pre-registration is REFUSED at review**, on §4.1:
required limb `8.0 + 14.0 + 0.0 = 22.0 GiB`, registered `16.0 GiB`, deficit
**6.0 GiB**.

### 7.2 Instance B — the survival. Same rung, ATTEMPT 2

Pre-registration frozen at **`606930b4`** (2026-08-24T16:17:01Z), **Amendment 1**
at **`8a0b440d`** (16:26:12Z, **before first compute**), graded at **`8871acf3`**;
audited as cross-team gate audit **pass 10** at **`d74a36c2`**,
`docs/CROSS_TEAM_GATE_AUDIT.md` **§73–§81**; calibration row **C-35**; run root
`/home/ubuntu/certonomous-runs/P5-a3-rung3-patched-attempt2/`.

| quantity | registered | measured (re-derived by the audit lane from all 87 guard samples) | reading |
|---|---|---|---|
| Launch limb (Amendment 1) | **25.0 GiB** = floor **8.0** + R3-P11 registered **UPPER 15.0** + co-tenant **2.0** | gate opened **poll 1 of ≤ 360** at `MemAvailable` **27.19 GiB** | margin **+2.19 GiB**, written to `launch_condition.txt`; the limb is **81.6 % of `MemTotal` 30.64 GiB** |
| Free-cores limb | ≥ 4 (unchanged) | **13** | margin **+9** |
| Own peak vs R3-P11 | point **11.65**, band **[9.2, 15.0] GiB** | **11.680 GiB** | **inside the band. HIT.** **+0.2575 %** off the point |
| Own peak vs R3-P7 | **9.0 – 14.0 GiB** vs a 16 GiB cap | **11.680 GiB** | **inside. HIT.** 73.0 % of the cap; the two bands scored separately and agree |
| RSS guard ceiling | 15.0 GiB, 3 × 5 s | **0 of 87 samples above 15.0** | guard exit **0** |
| Host floor | **8.0 GiB**, 3 × 5 s | **min `MemAvailable` 15.2871 GiB**, **0 strikes** | **7.29 GiB of headroom at the tightest sample** |
| Guard trace | every sample logged, 5 s armed | **87 samples, span 521 s, max inter-sample gap 7 s** | dense enough that a 3-strike / 15 s breach could not have been missed between samples |

**Amendment 1 is the clause working before it exists.** It moved the memory limb
**19.65 → 25.0 GiB** in `drive.sh` only — 3 lines replaced, 9 added, two hunks —
and left `mem_guard.sh` byte-identical, so the RSS ceiling and host floor the arm
ran under are the same ones attempt 1 ran under. It landed **before first
compute**, proved not by its own assertion but by an **independent clock**: the
run root's filesystem birth time is **2026-08-24 16:27:59.296995 UTC**, **107 s
after** the amendment and **121 s before** the gate opened
(`docs/CROSS_TEAM_GATE_AUDIT.md` §73). That is rule 2's amendment path used
exactly as written.

**What the instance shows, and what it does not.**

- **Shows:** a limb built from the registered **UPPER** (15.0) rather than the
  point (11.65) **over-provisioned the host by 3.32 GiB** against the measured
  peak, and the run's tightest host reading still left **7.29 GiB** above the
  floor. The upper-band construction was not merely safe — it was **not close to
  binding**.
- **Does not show:** that 2.0 GiB of co-tenant allowance is enough. See §6.3.
- **Costs something structural, and the clause should say so.** A limb at
  **81.6 % of `MemTotal`** **selects for a quiet box by construction**. That is
  the mechanism behind this item's cost miss: a wall estimate carrying a
  *contended-box* multiplier is systematically high behind such a gate — the
  registered contention factor was **1.7×** and the measured **532/445 =
  1.1955×**. **Recommendation carried into §4: the pre-registration records the
  gate's own memory limb beside any contention multiplier, and states which side
  of the gate the multiplier was measured on.**

---

## 8. Instrument spec — `scripts/check_launch_gate_memory_limb.py`

Proposed, **not written by this lane**. `CLAUDE.md` rule 14's provenance and
`FILING_CHARTER.md` §1 both say it: **a rule nobody can fail is a preference**,
and a defect class that has bitten gets an assert, not prose.

**Unit of analysis.** One frozen `*PREREGISTRATION*.md`.

**What it extracts,** each with the document line it came from: the launch-gate
memory limb; the neighbourliness floor; the own-peak band and its UPPER
endpoint; the co-tenant growth allowance; the guard's sampled quantity; the
guard's armed cadence and the gate's poll interval; whether an artifact is named
for the opening margin.

**What it refuses.** `limb < floor + upper + growth` ⇒ **REFUSE**, printing all
four terms, the required limb, the registered limb and the deficit. Missing
terms ⇒ **UNPARSED**, never PASS — a document the reader could not parse has not
passed, it has not been read (`VERIFICATION_CHARTER.md` §2c boundary item 1:
*"A check reporting no violations over a population it could not evaluate has
not passed; it has not run."*).

**Adoption path, D473's, because that precedent is already walked.**
`docs/REGISTERED_DELIVERABLES_CHECK_PROPOSAL.md` and docket **D473** set the
shape: **binding prospectively, report-only on a replay over existing
pre-registrations**, with the **fire rate published** before adoption, and
`VERIFICATION_CHARTER.md` §5's archive-replay requirement satisfied on the
record rather than asserted.

**The discrimination requirement, which is the whole test of the instrument.**
A rule that cannot discriminate its motivating case is withdrawn. This one has
**two** motivating cases and must separate them:

| case | required limb | registered limb | required outcome |
|---|---|---|---|
| Attempt 1, `97a54c07` | `8.0 + 14.0 + 0.0 = 22.0` | **16.0** | **FIRES**, deficit 6.0 GiB |
| Attempt 2 amended, `8a0b440d` | `8.0 + 15.0 + 2.0 = 25.0` | **25.0** | **DOES NOT FIRE**, margin 0.0 |

A check that fires on both is a check that condemns the tree and will be
scrolled past; a check that fires on neither has not run.

**Planted controls, rule 3, non-negotiable.** At minimum: a limb mutated below
the sum must fire; a limb mutated to exactly the sum must survive; a deleted
growth-allowance line must return UNPARSED and not PASS; a `MemFree` guard must
be flagged where a `MemAvailable` guard is not; and a document with no memory
gate at all must return **NOT APPLICABLE**, distinct from both PASS and
UNPARSED. **The zero this check will most often print — "no violations" over
pre-registrations that register no memory gate — is worthless without the
non-applicable class being counted separately and published.**

---

## 9. Cost of this draft, and the disclosures it owes

**Registered before the work, in the dispatching brief:** **two components, point
and ceiling.** (a) **lane wall: point 8 core-min, ceiling 15 core-min**
(1 lane × wall minutes, np = 1). (b) **executed compute: registered as
`< 0.2 core-min`** — a **ceiling with no separate point**, and it is recorded
here in the form it was given rather than back-filled with a point the brief did
not carry. **Zero solver, zero container, zero GPU.**

Actual against predicted is recorded in `docs/COST_CALIBRATION.md` at the row
this document lands with, per `CLAUDE.md` rule 12's calibration duty. Dollars
are **derived at $0.0513/core-h, c7a.4xlarge, reported-by-owner — never
measured**; the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**Worktree-staleness disclosure (D486 class), because two of this document's
citations depend on it.** At the time of writing,
`scripts/check_record_reconciliation.py` reported the worktree copies of the
records to be behind HEAD: **`docs/DOCKET.md` — 21 committed ids (D485–D505)
present in HEAD and absent from the worktree**; **`docs/COST_CALIBRATION.md` —
22 committed ids (C-15–C-36) likewise**, including **C-35**, which §7.2 cites.
Every calibration and docket citation in this document was therefore read from
the **HEAD blob**, never from the worktree copy, and the rows this document
lands with are merged onto the HEAD blob by `scripts/append_record.py` with
their ids re-derived as max+1 over that blob in the commit invocation itself
(rule 11).

**And the honest half of that disclosure.** That check's own planted controls
returned **BROKEN** for both of those files — its plants are `N-*` forms and do
not match the `D`/`C-` id patterns — so **its zero half is unsupported under
rule 3**. What this disclosure rests on is its **non-zero** half: 21 and 22
divergent ids, which the check did see and which a broken plant cannot
manufacture.

---

## 10. What is on Sanaa's desk

**One decision, stated as a choice between named options** — `ESCALATION_CHARTER.md`
§7 requires that shape, and requires the lab's recommendation with it.

| option | what it costs | what stays unmeasured |
|---|---|---|
| **A. Ratify §2f as drafted** and commission the §8 instrument | one lane to write the check + a report-only replay over existing pre-registrations; no solver compute | whether any particular growth allowance is sufficient (§6.3); the de minimis X (§6.1) |
| **B. Ratify the clause, defer the instrument** | nothing now | everything in A, plus: the clause becomes prose nobody can fail (`FILING_CHARTER.md` §1) |
| **C. Commission the instrument report-only, defer the clause** | one lane; the replay's fire rate becomes evidence for a later decision | the clause binds nothing in the interim, and the next memory-gated registration is reviewed by eye |
| **D. Neither** | nothing | the attempt-1 failure mode remains uncaught by construction; it cost 6.80 core-min and one whole finding once already |

**The lab's recommendation: A, with §6.1's `X` stated in the clause as a
JUDGEMENT and re-derived once the np = 1 peak distribution exists.** The clause
is a necessary condition, it is checkable on the frozen document with one
subtraction, it has one case that must fire and one that must not, and the
review it replaces costs less than the run it saves.

**What proceeds regardless:** nothing waits on this. No run is blocked, no
verdict is held, and dafoam's attempt-2 item is closed on its own evidence. This
document is a recommendation and a draft; **adoption is Sanaa's alone.**

---

**DRAFT — AWAITING SANAA. Recommendation only. Not in force. No charter was
edited to produce it.**
