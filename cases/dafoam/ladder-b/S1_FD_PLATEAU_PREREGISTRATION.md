# S1 / W4 CBFS field-inversion FD — the plateau step that was never bought: pre-registration

> # ⚠ DRAFT — UNFROZEN, NOT QUEUED, NOT ARMED
>
> **This document is a DRAFT at this commit.** It is **not frozen**, **nothing is
> queued**, **no launcher is armed**, and **no solver may run against it in this
> state**. Freezing it is the `dafoam-supervisor`'s act, and
> `SUPERVISION_CHARTER.md` §3 check 4 — *pre-registration committed before compute* —
> is that supervisor's personally and is **not delegable to the lane that drafted
> this**. The gates, thresholds, steps, caps and labels below become binding only at
> the freeze commit, and this banner is struck by dated addendum at that commit.

**Drafted 2026-09-04 by a dafoam lane. Zero compute spent to produce it.**

---

## 0. Why this is a NEW registration and not an amendment

The measurement registered here re-opens an FD table that lives in a **frozen**
document, `S1_CBFS_REINVERSION_PREREGISTRATION.md` (frozen at `commit 289a9e03`,
2026-08-07 20:14:45 +0000). **It cannot be bolted onto that document**, on two
independent grounds:

- **`CLAUDE.md` rule 2** — after first compute, gates are closed; changes land only as
  dated addenda *"that cannot alter a gate, threshold, cap or label"*. Registering a
  new step, a new bar and a new budget is precisely altering those.
- **`VERIFICATION_CHARTER.md` §2h.6** — *"Every §2h benefit requires a **NEW
  registration**, frozen after §2h, carrying the [conditions] on its face. There is no
  citation path, no addendum route and no supervisory instruction that creates one."*
  The clause is written about §2h; **its principle is general and is applied here
  against this lane's own convenience**, which is the direction in which it is worth
  something.

The frozen document therefore carries only a **disclosure** (its Amendment 2,
2026-09-04, foot-appended, no gate moved). **This file carries the compute.**

## 1. The defect being repaired, stated as a fact and not as a criticism

**Six FD numbers across three lab records rest on a single step each:**

| record | cells | values | steps run |
|---|---|---|---|
| `S1_CBFS_REINVERSION_PREREGISTRATION.md:207-211` (Amendment 1 §C) | 5363 / 5428 / 5491 | 0.032 % / 0.115 % / 0.009 % | **`h = 0.05` only**, 6 primals total |
| `W4_ADJOINT_PC_UNBLOCK.md:317-322` (§5d) | 6740 / 12486 | 0.059 % / 0.199 % | **`h = 0.05` only** |
| `W4_ADJOINT_PC_UNBLOCK.md:317-322` (§5d) | 5491 | 0.085 % | `h = 0.05` **and** `h = 0.1` — **the only two-step cell in the family** |
| `VERIFICATION_cbfs_unblock_supervisor_sweep.md:99-107` (§3) | 6490 | 0.0211 % | **`h = 0.05` only** |

`VERIFICATION_CHARTER.md` §7, reporting protocol step 1: *"Confirm the step sits in the
well-converged plateau with a two or three point mini-sweep. **Not assumed.**"* That
clause entered the charter at **`commit ea53c110`, 2026-07-30 18:53:17 +0000** — the
commit that ADDED `docs/charters/VERIFICATION_CHARTER.md`, the sentence at line 208 of
its blob, absent from its parent. **Every one of the six numbers postdates it.** There
is no retroactivity defence.

**`DAFOAM_CHARTER.md` §3 is NOT cited against any of the six.** It is the sharper
clause — it forbids *"Quoting an FD number from a single step"* in those words — but it
landed at **`35e06e85`, 2026-08-21 17:42:57 +0000**, after all six runs, and its own
text cites S1's Amendment 1 §B as the incident that earned it. §2h.6's non-retroactivity
runs both ways and is honoured in both directions here. **§3 binds THIS registration in
full**, which is why the design below satisfies it.

**What is NOT asserted.** No value above is shown to be wrong. What is unverified is the
**precondition** §7 places ahead of reading a value at all. **This registration exists to
buy the evidence, not to move a label**: under Sanaa's 2026-09-04 standing order that
assigned cases be *"worked and fixed and solutioned"*, buying the missing evidence **is**
the fix.

## 2. Arm P — the plateau step for the three S1 §C cells

### 2.1 The step is fixed by the family's own registered rule, not by this lane's taste

The lab already owns a mechanical step rule — **`N-D21`**
(`docs/NUMERICS_KNOWLEDGE.md:3439`), operationalised at
`docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md` §4.1 and executed on A6. **It is used here
rather than re-derived.** One thing about its use is stated plainly, because it is the
part that could be got wrong:

> **N-D21's SELECTION limbs (its rules 5 and 6) are deliberately NOT re-run.** Those
> choose a graded step *before* a value exists. Here the graded step already exists and
> is frozen at `h = 0.05`, and re-selecting it now — after the answers are known —
> would be exactly what `DAFOAM_CHARTER.md` §3 forbids as *"Selecting the step after
> seeing which one agrees."* **What is executed is N-D21's PLATEAU limb (rule 7) and
> its CLEARANCE arithmetic (rules 1–3), around the step that is already graded.**

The second step therefore follows mechanically from N-D21's own pair constraint
`s_hi ≥ 2·s_lo` with `s_hi` fixed at the graded 0.05:

> **`s_lo = 0.025`. Registered now, before any run, and the largest admissible value —
> chosen by the constraint, not by agreement.**

Two further reasons it is the right side to buy, recorded so the choice is auditable:
the **upward** limb is already characterised (W4's cell 5491 pair, 0.05 → 0.1, shows the
FD moving away from the adjoint as O(h²) predicts), whereas the **downward** limb is
entirely unmeasured; and the contamination mechanism this family actually suffered —
primal state error entering the difference — **bites hardest at small steps**, where the
signal is smallest. A plateau demonstrated only upward would not exclude that 0.05
already sits on the noise-dominated shoulder.

### 2.2 The noise floor η — registered NOW, from an existing log, and never moved

N-D21 rule 1: register `η` before the run and never move it afterwards. `η` is taken
from a log that **already exists**, so no compute is required to fix it:

> **`η = 3.907091e-12`** — the peak-to-peak of `varianceU` over the **last 200
> iterations** of the 1e-8 baseline, i.e. the samples printed at `Time = 2400`
> (`6.1509016719211399e-04`) and `Time = 2500` (`6.1509017109920500e-04`)
> `[MEASURED, /home/ubuntu/certonomous-runs/S1-cbfs-reinversion/log.anchor8]`.
>
> **`η_cons = 2.751958e-11`** — the same quantity over the **last 500 iterations**
> (samples `Time = 2000 … 2500`), registered as a **conservative alternative**.

**Disclosed limitation, stated now rather than discovered later:** the objective is
printed every 100 iterations in that log, so a 200-iteration window holds only **two**
samples. That is thin, and it is the reason `η_cons` is registered alongside. **Every
clearance below is reported at BOTH values, so no verdict in this item can turn on the
window choice.** Neither number may move after this document freezes.

### 2.3 Clearance — computed now, and it is registered as NON-BINDING with the reason

`C(s) := |J_adj| · 2s / η` (N-D21 rule 3), on the frozen anchor8 gradient values:

| cell | `|J_adj|` | `C` at `s = 0.025`, η | `C` at `s = 0.025`, η_cons | N-D21 bar |
|---|---|---|---|---|
| 5363 | 4.077412370787e-05 | 5.218e+05 | 7.408e+04 | `C ≥ 5` |
| 5428 | 2.676772294906e-05 | 3.426e+05 | 4.863e+04 | `C ≥ 5` |
| 5491 | 2.824832243684e-05 | 3.615e+05 | 5.132e+04 | `C ≥ 5` |

> **Registered reading: the clearance criterion is satisfied by four to five orders of
> magnitude and is therefore NOT the discriminating test on this case.** It is reported
> because N-D21 requires it and because a criterion that cannot fail must be *said* to
> be unable to fail rather than quoted as if it had passed something. **The plateau test
> in §2.4 does all the work here**, and the honest reason the clearance is so large is
> that a primal run to the 2500-iteration cap at `1e-8` leaves an exceptionally quiet
> objective.

### 2.4 The gate — registered before any run

> **GATE `P1` — the plateau holds per component.** For **each** of cells 5363, 5428 and
> 5491, with `d(s)` the central-difference estimate at step `s`:
>
> **`|d(0.05) − d(0.025)| / |d(0.05)| ≤ 10 %`**
>
> the bar N-D21 rule 7 registers verbatim (*"two steps agree if
> `|d(s_hi) − d(s_lo)| / |d(s_hi)| ≤ 10%`"*). **Read PER COMPONENT and never off the
> vector** (`DAFOAM_CHARTER.md` §3). A component that misses is **FLAGGED and excluded
> by name** from any aggregate, never dropped silently and never rescued by a step at
> which it happens to cross.
>
> - **All three inside 10 %** → §C's row is reported as **plateau-verified**, and the
>   `PASS` at `S1_CBFS_REINVERSION_RESULT.md:92` is **defended at §7 step 1** by dated
>   addendum to that record.
> - **Any component outside 10 %** → **that component is `NOT A RESULT`**, by
>   `CLAUDE.md` rule 1's vocabulary and for the reason §7 step 1 gives: the value was
>   read before its precondition was met. **Not `GATE FAIL`** — a failed plateau does not
>   show the adjoint wrong, it shows the FD estimate not to be a measurement of the
>   derivative.
> - **Reported with no gate attached:** each `d(0.025)` and its rel. err against the
>   frozen anchor8 gradient; each component's sign; the stopping iteration of all six
>   new primals.

**Sign-flip duty, registered separately because §7 step 3 makes it separate:** any
component whose FD value **changes sign**, or **moves by more than 50 % of its own
magnitude across one decade of step**, is flagged as *"a real defect signature, not
noise"* — reported in the sign-match column of §2.6's table whatever `P1` says.

### 2.5 Arm F — the registered trivial baseline (the falsifier), per `DAFOAM_CHARTER.md` §4

§4 requires a DAFoam FD gate to name its trivial baseline **in the pre-registration,
before its own run**, as *"the same probe at a step chosen to be wrong — an order of
magnitude off the registered one"*, and to **withdraw the verdict if the wrong step also
passes**.

> **Registered falsifier: cell 5363 at `h = 0.5`**, ten times the graded step, same
> protocol, same tolerance, 2 primals. Precedent and shape:
> `cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/PREREGISTRATION.md`, which
> registered cell 5491 at `h = 0.5` predicting `> 2 %` and measured **5.3686 %**.
>
> **PREDICTION, fixed now: rel. err against the anchor8 gradient `> 2 %`, and the
> `h = 0.5` estimate FAILS `P1`'s 10 % plateau bar against `d(0.05)`.**
>
> **Basis of the prediction, so it is falsifiable rather than safe:** central-difference
> truncation is O(h²); 0.05 → 0.5 is 10× in `h`, so ~100× in truncation error, and
> 5363's 0.032 % scales to ≈ 3.2 %. W4's measured 0.05 → 0.1 pair on cell 5491 moved
> 0.085 % → 0.460 %, a factor 5.4 for a 2× step against O(h²)'s ideal 4, i.e. slightly
> **steeper** than the ideal — which makes `> 2 %` a conservative floor rather than a
> generous one. `β = 1 ± 0.5` stays inside this item's registered `[0.2, 4.0]` bounds.
>
> **REGISTERED CONSEQUENCE:** if the deliberately wrong step **passes** `P1`'s bar,
> **`P1`'s verdict is WITHDRAWN for every component**, because the gate would then be
> shown not to discriminate step quality at all. This consequence is registered now so
> it cannot be argued away later.

### 2.6 The table shape, fixed now — including the two columns the original lacked

**Both `VERIFICATION_CHARTER.md` §7 shapes are produced, and neither is optional.**

Per-component, with the **step column and the sign-match column the original §C table
did not carry**:

    | idx | analytic | FD (step) | rel. err % | sign match |

Step sweep, with **failed steps as rows** — *"a sweep that hides its failed steps is
reporting a plateau it did not measure"*:

    | step | rel err | rel err (excl. flagged) | cosine | status |

A `status` cell for a step that did not produce a usable primal reads, in §7's own
form, e.g. `FAILED: primal did not converge for idx<n> (+step); residual stalled at
<value> vs 1e-8 tolerance`. **A step that fails is a row, not an omission.**

Also registered per `DAFOAM_CHARTER.md` §5: every number states its decomposition and
`np`; and per that charter's §18.6, every figure in the completion report carries a
provenance tag with an artefact path.

### 2.7 The planted-zero control — `CLAUDE.md` rule 3

**A comparator that reports agreement must first be shown able to report disagreement.**
Registered mechanically, before the run:

> Before grading, the comparator re-reads the six new perturbed objectives from their
> `log.*` files on disk, and is run **twice**:
>
> 1. **Clean pass** — the objectives as written.
> 2. **Planted pass** — a known perturbation `PLANT = 1.234e-03` **relative** is added
>    to the `+` leg of cell **5428** only, **by line index in the parsed objective
>    list**, and the file is re-read from disk. The comparator **MUST** report cell
>    5428's rel. err changed by the amount that plant implies, and **MUST** report cells
>    5363 and 5491 unchanged to the last digit.
>
> **If the planted pass does not move 5428, or moves any other cell, the comparator
> REFUSES with exit 2 and NOTHING IS GRADED.** A zero from a reader not shown able to
> see a non-zero is not evidence. The refusal is a hard exit, not a warning, and the
> comparator **refuses rather than degrades**.
>
> **The plant is applied to a COPY**; the run artefacts are never modified.

### 2.8 Cost — `CLAUDE.md` rule 12, per arm, before the run

Basis, and it is measured rather than estimated: the six existing `fd8_*` rows in
`/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/ledger.csv` total **1366 s wall at
`--cpus=2` = 45.533 core-min**, i.e. **7.5889 core-min per perturbed primal at
`primalMinResTol 1e-8`** on this exact case, mesh and container `[MEASURED, that
ledger]`.

| arm | what | primals | core-min | derived $ |
|---|---|---|---|---|
| **P** | plateau, 3 cells × 2 sides at `h = 0.025` | 6 | **45.533** | $0.0389 |
| **F** | §4 trivial baseline, cell 5363 × 2 sides at `h = 0.5` | 2 | **15.178** | $0.0130 |
| | **predicted total** | **8** | **60.711** | **$0.0519** |
| | **HARD CAP — an overrun STOPS the item** | | **75.0** | |

**No new adjoint anchor and no new baseline primal are budgeted**, and the reason is
stated so a reviewer can refuse it if it is wrong: the analytic gradient is the frozen
`grad_anchor8.npy` at the identical tolerance and baseline, and this item changes only
the FD step. **If any new primal's unperturbed control does not reproduce
`6.1509017109920479e-04` bit-identically, that assumption has failed and the item stops
there** — that check is itself a registered gate limb, not a courtesy.

**`cost_basis`: the core-minute figures are MEASURED from this item's own ledger. The
dollar figures are DERIVED at the owner-stated c7a.4xlarge rate of $0.0513/core-h and
are NOT MEASURED — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md`
§5).** Under $25, so inside the 2026-08-21 blanket; costed anyway, because a blanket is
not a per-item read (`CLAUDE.md` rule 9).

**Rule 12 calibration duty, registered now:** at completion this item files an
estimate-versus-actual row in `docs/COST_CALIBRATION.md` — ratio actual/predicted, gap
attributed, waste named separately and never absorbed into the ratio.

### 2.9 Resource guard and completion accounting — `DAFOAM_CHARTER.md` §18.7

Registered explicitly, because §18.7 makes each of these a stated refusal ground:

- **Guard response: STOP, not block-and-continue.** A memory or aggregate breach
  **terminates this item with a non-zero rc** and the label `BLOCKED`. It never
  discards one primal and proceeds.
- **Discard fraction, since the guard stops:** a single breach discards **0 %** of the
  declared program and terminates it; a sustained condition discards **0 %** and
  terminates it. **No partial-program path exists in this item.**
- **The condition guarded is transient**, so it gets a **bounded wait**: poll 30 s,
  bound 3600 s, every wait a line in the status file; **at the bound the item stops with
  a non-zero rc**, it does not buy a smaller program.
- **Aggregate admission**: before release, `live sibling caps + this item's cap + host
  NON-CONTAINER RSS` is checked against the registered ceiling by the reading
  `cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_aggregate_memory.py` implements —
  **the third term included**, which is the term `W3`'s arithmetic lacked.
- **Declared and executed counts are BOTH reported**, and **a gate limb reads the
  blocked count in**: `declared(8) == executed + blocked`, and any `blocked > 0` forces
  the item's token to `NOT A RESULT` or `BLOCKED`. **No success-reading token is emitted
  over a short program.**

## 3. Arm W4 — registered SEPARATELY, and priced BOTH ways WITHOUT a choice

**This arm is registered as its own arm and is not bundled with Arm P**, because it runs
on a different case state, a different objective and a different tolerance, and bundling
would let one arm's outcome carry the other's.

### 3.1 The trap, stated first

`DAFOAM_CHARTER.md` §3 requires the sweep be run **at the primal tolerance the graded run
uses**. **W4's graded run used `primalMinResTol 1e-06`** `[MEASURED,
/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/cbfs_beta_computetotals.log:371` —
read from W4's own run artefact, not inferred from S1's record]`. And 1e-6 is the
tolerance S1 later measured as **itself polluting FD**: 25.9 % → 0.032 % on the same
cell, on the tolerance change alone. **So a limb bought at 1e-6 risks measuring the
plateau of a protocol since shown defective.**

### 3.2 The measurement that materially weakens that trap — taken at zero compute

| protocol | stopping iteration of every FD primal | rel err |
|---|---|---|
| **W4 §5d at 1e-6** | **1578 – 1582**, spread **4 iterations across 9 runs** | 0.085 / 0.059 / 0.199 % |
| S1 at 1e-6 (the recorded miss) | **383 – 458**, spread 75 across 6 runs | 25.9 / 32.0 / 32.2 % |
| S1 at 1e-8 (the clean sweep) | **2500** on all six — the endTime cap | 0.032 / 0.115 / 0.009 % |

`[MEASURED, W4-adjoint-pc-unblock/cbfs_beta/fdlogs/*.log and S1-cbfs-reinversion/log.fd_*
and log.fd8_*]`.

**The pollution S1 diagnosed is a property of stopping EARLY, not of the tolerance
label** — S1's own words are that the cold primal *"stops at the first 1e-6 crossing"*
because it starts far from its solution. **W4 did not stop early**: its primals ran ~4×
further and stopped at essentially the same iteration regardless of the perturbation,
which is consistent with §5d's own account that its case's initial condition already
matched its (defective) BCs. **Measured in iterations actually taken, W4's 1e-6 primals
sit far closer to S1's clean 1e-8 sweep than to S1's polluted 1e-6 one.**

**This was not on the record before this drafting and it runs in W4's favour.** It is
stated here because a fact that helps the record under audit is exactly the one an
auditor may not sit on.

### 3.3 The two options, both priced

**Option 1 — the 1e-6 limb (minimal, and §3-compliant on tolerance).** Add the second
step to the two single-step cells at W4's own graded tolerance, matching the step cell
5491 already carries.

- Cells **6740** and **12486** at **`h = 0.1`**, `primalMinResTol 1e-6`, W4's protocol.
- **4 perturbed primals.** No new anchor (the archived gradient is at this tolerance and
  is unchanged), no new base (§5d's unperturbed control is on the record at exactly zero
  difference).
- Basis: W4 §7's measured FD sweep row — 9 primals, 642 s wall, 4 cores, 42.8 core-min →
  **4.7556 core-min/primal** `[DERIVED from that MEASURED row]`.
- **19.022 core-min; derived $0.0163.**

**Option 2 — the 1e-8 re-anchor.** Rebuild §5d at the tolerance S1 established, with the
N-D21 pair `{0.025, 0.05}` on all three cells.

- New 1e-8 adjoint anchor, new 1e-8 base control, **12 perturbed primals**.
- Basis: S1's measured 1e-8 rows on the same mesh and case — `anchor8` 19.967,
  `fd8_base` 5.367, mean perturbed primal 7.5889, all at `--cpus=2` `[MEASURED, S1
  ledger.csv]`.
- **116.400 core-min; derived $0.0995. 6.1× Option 1.**
- **Option 2b, recorded because it is the tempting shortcut and it is not sound:**
  reusing the archived 1e-6 adjoint gradient as the reference costs **96.433 core-min /
  $0.0825** — but **the adjoint at 1e-8 is not established to equal the adjoint at 1e-6
  on this case**, and S1's own experience is that the deeper state changes the adjoint's
  convergence (reason 2, 675 iterations at 1e-8). **2b is priced so it can be refused
  knowingly, and this registration does not recommend it.**

### 3.4 Recommendation — reasons on both sides, and the choice is NOT taken here

**My brief instructs me to recommend and not to choose, and I am not choosing.**

**For Option 1.** It is the literally-compliant repair for W4's own row: §3 asks for the
sweep at the tolerance the graded run used, and that tolerance is 1e-6. It is 6.1×
cheaper. It preserves W4's record as a statement about the protocol that actually
produced it, rather than replacing the published number with a different one. And §3 did
not exist when W4 ran — the live duty was §7 step 1, which asks for *a* mini-sweep at the
graded step and does not ask for a tolerance change.

**Against Option 1.** If §3.2's reading is wrong, a 1e-6 plateau discharges §7 step 1
formally while telling a reader nothing about whether 0.059 % and 0.199 % are right.

**For Option 2.** It yields numbers defensible under §7 step 1 **and** §3 as they now
stand, and it puts W4 and S1 on the same protocol — today they are not comparable, and
the family's own standard `V_STANDARD_FD_VS_ADJOINT.md:163-169` tabulates all six
together as though they were.

**Against Option 2.** It does not verify what W4 published; it **replaces** it. W4's
0.085 / 0.059 / 0.199 % would remain single-step-at-1e-6 for ever, with a different
number beside them. And W4's own budget is closed at 185.0 of 240 core-min — a re-anchor
is a new item, not a top-up.

> **The decision rule I recommend, rather than a preference.** §3.2 is a genuine but
> **circumstantial** defence: it shows W4's primals ran deep and symmetrically, which
> removes the *stopping-point* channel of S1's contamination. It does **not** show they
> were converged to the same *depth* as S1's 1e-8 runs, and that is the load-bearing
> question. **It is settleable at zero compute** from artefacts already on disk —
> the final residual levels in `cbfs_beta/fdlogs/*.log`, compared against the
> `U ~1e-10, p ~2e-8, omega ~1e-9, k ~3.7e-7` that S1's Amendment 1 §B records for its
> 1e-8 runs.
>
> **If W4's final residuals sit near S1's 1e-8 levels → Option 1**, at $0.016: the
> tolerance label is then not the risk, and 19 core-min discharges the duty.
> **If they sit near the 1e-6 threshold → Option 2**, at $0.100: the protocol is then
> genuinely the one S1 condemned and only a re-anchor produces a defensible number.
>
> **That residual comparison is not registered here and costs nothing; it should be run
> before this arm is priced into a queue.**

### 3.5 What Arm W4 does NOT cover, named rather than quietly carried

**No second step is registered for cell 6490**, the supervisor sweep's independently
derived 0.0211 %. Re-opening an independent adversarial audit's own probe is the
auditor's call, not the audited party's. The gap is real and is named so it is visible.

## 4. What this registration does NOT do

- **It moves no existing verdict.** `S1_CBFS_REINVERSION_RESULT.md:92`'s `PASS` is not
  relabelled by this document; its disposition waits on Arm P's outcome and is the
  supervisor's.
- **`G1` (−74.2 %) and `G2` (26.9 %) are untouched and are NOT in scope.** They require
  only a **usable** gradient, established independently of any FD magnitude by the
  eval-1 control (bit-identical `varianceU`, gradient max abs diff exactly 0) and the
  cold final-state reproduction. **They have been read as one object with the FD row;
  they are not one object, and nothing in this item can move them.**
- **It re-opens no frozen gate, threshold, cap or label** in
  `S1_CBFS_REINVERSION_PREREGISTRATION.md` or in `W4_ADJOINT_PC_UNBLOCK.md`.
- **It claims no clause that postdates the records it examines.**
- **Nothing is sent, filed, uploaded or registered outside this box** (`CLAUDE.md`
  rule 7).

## 5. Freeze checklist — for the supervisor, whose act this is

1. Strike the DRAFT banner by dated addendum at the freeze commit.
2. Confirm `η`, `η_cons`, `s_lo = 0.025`, `P1`'s 10 % bar, the `h = 0.5` falsifier and
   its `> 2 %` prediction, and both cost lines are the numbers being frozen.
3. Name the run root, and confirm **it does not yet exist** (`CLAUDE.md` rule 2:
   pre-first-compute amendments must state the condition and how it was checked).
4. Decide Arm W4 — after the zero-compute residual comparison of §3.4.
5. Verify the frozen file **is** the file that runs, by hashing it against the committed
   blob.

---

*Nothing below this line existed when this file was drafted. **No solver may run against
this document until it is frozen, and freezing it is not this lane's act.***
