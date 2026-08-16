# The four chief calls, plus the un-implemented EIG recommendation — costed, not decided

**2026-08-16. Zero solver core-min, zero scoring calls; the ledger stood at 6 and was not touched.
Nothing was sent, registered, posted or created. No proposal was launched and no status was written.**

**What this document is.** Five decisions were surfaced by the agenda finalization at `b0f9ec7c`
(`campaign/AGENDA_LOST_CLOSURES_FINALIZED_2026-08-16.md`, D253) and named but not taken. They are
costed here in the docket-costing shape: **options, measured consequences, failure modes, and no
recommendation as to which to pick.** Every status below was established by execution against HEAD,
not read from the row that named it.

**Three corrections to D253's own Owner column, found while costing it.** They are stated first
because two of them change who decides:

1. **W4's upstream addendum was routed to the chief and it is NOT the chief's.** Filing it means
   opening an issue against `mdolab/dafoam` — an external post. It is Katie's alone, in writing, in
   three separate charters. Re-routed in §4.
2. **`pydafoam`'s regrades were listed as open and are all but closed.** Row 6 of the audit was
   already ruled on 2026-08-10 (retired as superseded, scope B, 0 core-min). Only row 7 remains and
   it cannot move a verdict. §3.
3. **The W1-only arm was listed as a plain "go/no-go" and the shape is different.** It was ruled
   `NO-GO for now` at `7b758783` with a **named trigger**; the trigger **fired** on 2026-08-11 and
   released the question back. D213 then killed the arm on grounds that are not the ones on its
   dispatch surface. §1.

---

## 1. The W1-only arm — `s1-cbfs-w1-only-arm`, 150 core-min, still `proposed`

### What was measured
The parent weighted arm ran and **both pre-registered Gate-C gates failed** (G1w 0.05713 against
≤0.05320; G2 42.7% against >50%), with the eval-8 completion grading G1w a failure **on the original
bar** and recording the budget-limited hypothesis **UNRESOLVABLE as posed** (`7b758783`, `d932d007`,
`b0e31fa5`). The arm's sharpened question is whether matching **loss support** to **metric support**
closes G2 — the weighted arm split effort 42.7% window / 37.0% recovery strip because both sat in
the loss.

### The decision chain, established by execution
* `7b758783` (2026-08-08 22:57Z) ruled **NO-GO for now**, approved-in-principle, with a named
  trigger: the S1-with-priors design phase, *"Do not claim, price, or launch before that phase opens."*
* **The trigger fired.** `ladder-b/S1_PRIORS_PREREGISTRATION.md:7-9` (2026-08-11) names itself *"the
  named TRIGGER that unblocks `s1-cbfs-w1-only-arm`"*, and at `:208-214` **decided loss support
  without the arm** — equal-weight, all cells, argued before any compute — and **released the arm
  back to the chief as a separate go/no-go.**
* **D213 then killed it on two legs, neither of which is the reason on its own surface**, the load-
  bearing one being that its first deliverable is a **G2 verdict and G2 is invalidated six
  independent ways**, so a PASS on it establishes nothing and so does a FAIL.
* **Verified at HEAD:** the dispatch surface still reads `"status": "proposed"`,
  `"est_core_min": 150.0`, last touched `b4fd62e7` (2026-08-10 15:43:18Z) — **before the trigger
  fired** — and still carries the pre-trigger NO-GO note. No commit has touched it since.

### The options

| | option | measured consequence | failure mode |
|---|---|---|---|
| **1a** | **Ratify D213's kill onto the dispatch surface** (write `dismissed` + the deliverable-level reason) | 150 core-min never spent on a verdict against an invalid gate. The loss-support datum the arm existed to produce was already supplied by the priors phase at `:208-214`. Zero compute to execute. | If G2 is later revalidated, the question reopens and the arm has to be re-filed. D213 is explicit that the surviving kill is deliverable-level and does **not** depend on any prediction about the arm's beta field, so this failure mode is narrow. |
| **1b** | **Overrule and run it** (owner authorises compute) | Buys an apples-to-apples G2 test at matched support: ~150 core-min on a measured basis (~19–20 core-min per eval at 1e-8 uncontended, ~5 evals, plus controls and write-out). | **The deliverable is a verdict on a gate invalidated six ways.** Spending 150 core-min to learn something that establishes nothing either way is the exact failure this costing exists to expose. |
| **1c** | **Leave it as is** | Zero action. | **This is the live risk and it is not neutral.** A priced, dispatchable 150-core-min item sits behind an eleven-day-stale note that says NO-GO for a reason that has expired. Any agent reading the dispatch surface sees an item awaiting a trigger that already fired. D213 calls this *"a release event is a second detector nobody has"*. |

**Compute authorisation is the owner's, so 1b is a proposal and nothing here launches it.**

---

## 2. Capability strategy §2 phrasing

### What the current phrasing claims
`docs/CAPABILITY_STRATEGY.md:37-39`, still an unchecked box and unedited in place:

> *Linear solvers & preconditioning: Saad … working group → PROOF: A3's transonic adjoint
> conditioned deliberately (diagonal-spread diagnosis → chosen preconditioner → converged), not by
> knob-luck.*

### What is true
The A3 arm ran (prereg `a9bb202d`, choice `dda82819`, outcome `368996c3`) and **the diagnosis route
the clause names is a measured dead end for this case**: rung 2 spreads 14.40 decades and converges,
rung 3 spreads 14.47 and cannot. Seven hundredths of a decade separate a working rung from a walled
one, so diagonal spread does not discriminate and no preconditioner choice can be derived from it.
The surviving characterization is κ ≈ 10¹¹, insensitive to every preconditioner parameter the build
exposes.

### The correction already exists, and that changes the decision
`CAPABILITY_STRATEGY.md:141-173` already carries a **fourth dated correction (2026-08-10 night)**
that quotes the clause, states it *"refuted BY EXECUTION"*, and supplies a chief re-phrasing at
`:169-173`:

> *conditioning diagnosed to a stated mechanism and the chosen remedy either applied or shown
> unreachable, with the elimination table published either way.*

with *"The original clause is retained above, unedited, per L-44."* **So the substantive rewrite has
been made.** What is open is narrower than "rewrite §2".

### The options

| | option | what it concedes | failure mode |
|---|---|---|---|
| **2a** | **Leave as is** — retraction lives at `:141-173`, §2's bullet unedited per L-44 | Concedes nothing new; L-44's supersede-don't-delete convention is honoured. | A reader of §2 alone sees a live PROOF clause with no marker that it was refuted 104 lines below. This is the same read-the-section-not-the-file failure that produced the V10 blockers. |
| **2b** | **Add a pointer at `:37-39`** — leave the clause, append a marker to the dated correction | Concedes that L-44 preserves text but does not by itself protect a sectional reader. Cheap, no text destroyed. | A pointer is not a strike; a fast reader may still take the clause as live. |
| **2c** | **Strike the clause in place and carry the re-phrasing into §2** | Concedes that a refuted PROOF clause should not stand unmarked in the proven-by list. | Strike-and-keep leaves the refuted wording legible in the same span, which is what `\sout{}`/`<s>` does everywhere in this lab; a careless strike can also unbalance the span. |
| **2d** | **Adopt the re-phrasing as the clause and mark the box** | Concedes the box was never earned under the original wording, and asserts it is earned under the new one — *"we know what it is and what it would take"*. | The re-phrasing says the arm **half-delivered** it and that the upstream-reachability question completes it — and that question routes to §4, which is Katie's. Marking the box now would claim a completion that an unfiled external report is holding open. |

---

## 3. pydafoam's regrades — the answer is that a regrade cannot move any verdict

**Stated plainly, as asked.** `WARMSTART_AUDIT.md:51-55`: *"**No standing record-grade conclusion is
overturned.**"* and `:57-59`: *"Regrade decisions belong to the chief per the proposal's own terms;
**this audit rewrites no conclusion.**"* Seven of nine rows are COLD-CLEAN. The two WARM rows:

* **Row 6 — D3 n15 variant-lever nulls. ALREADY RULED, and not by this pass.** Closed in place
  **2026-08-10** by chief ruling, scope B, **0 core-min**: retired as superseded. The `-5` story had
  moved entirely to the `transonicPCOption` dead-code finding and a cold control reproduced the `-5`
  bit-identically. **Nothing currently cites the nulls** — verified independently across
  `demo-output/`: every surviving reference is an artifact inventory or a *retraction*, and
  `R5_ADJOINT_CONDITIONING.md:300-325` retracts the one causal conclusion they supported. The audit's
  *"cold rerun before any future citation"* requirement is satisfied **structurally, by never citing
  them** — the stricter option, not the lazier one.
* **Row 7 — R5/M6 conditioning matrix dumps.** WARM in state (~2% drift), **conclusion-class
  robust**: the cited figures are order-of-magnitude conditioning measurements (14 decades),
  insensitive to a 2% drift, and linearizing about a converged state was the dumps' intent.
  Corroborated downstream at `R5_ADJOINT_CONDITIONING.md:312-314`. The audit's own words:
  *"Flagged for the chief's regrade discretion, **expected no-action**."*

### The options

| | option | measured consequence | failure mode |
|---|---|---|---|
| **3a** | **Record no-action on row 7 and close the item** | Zero compute. Matches the audit's own expectation and the downstream corroboration. | If a future claim ever needs those dumps at better than order-of-magnitude precision, the 2% drift becomes live and the dumps must be redone. Nothing currently makes such a claim. |
| **3b** | **Order a cold re-dump of R5/M6** | Would remove the only remaining WARM flag. | Buys precision no standing conclusion uses. The audit priced the analogous D3 scope A at 80–110 core-min and it was **declined**; scope C's 3-lever triage (35–45 core-min) was approved separately and is a different question. |

**No option changes a verdict.** That is the finding, and it is why this is a bookkeeping call
rather than a scientific one.

---

## 4. W4's upstream addendum — RE-ROUTED: this is external, and it is Katie's

**Filing is external interaction, unambiguously.** The report is
`demo-output/website/dafoam/UPSTREAM_BUG_REPORT_decomposition_adjoint.md` (591 lines), destined for
the **`mdolab/dafoam` GitHub issue tracker**. Its own header, `:3-7`:

> ***Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been contacted, nothing
> has been posted.*** *This document is prepared to be filed against `mdolab/dafoam` … **Whether it
> is sent is Katie's call, not the lab's.***

Reserved to her in writing in three places: `FAMILY_SUPERVISION_GUIDELINES.md:115` — *"**Nothing is
filed upstream by anyone in this family, ever** … filing is Katie's call alone"*; the report header
above; and `campaign/COLD_START_TEST_2026-08-11.md:377-384`, which names filing the upstream report
as one of the two **most dangerous** acts an ignorant agent could take, *"explicitly reserved to
Katie in two charters"*. **So it does not route to the chief, and D253's Owner column is corrected
here.**

**What it would say.** The defect: on a 2,777-cell Ahmed-body `DASimpleFoam` case, varying **only**
the decomposition moves `check_totals` from 0.34% (np=1) to **8.95%** (np=4 default scotch), because
DAFoam v5's parallel reverse-AD transposed-Jacobian product is not the transpose Jacobian — the
mapped scotch adjoint vector leaves a true residual of **329× ‖b‖** under the serial operator while
its own KSP reports convergence. **The W4 addendum** (`:551-591`) adds the null — both ingredients
installed on the clean structured NACA0012 gave decomposition-invariance to 3.9e-04, so the trigger
conjunction is **insufficient off the Ahmed family** — and the serial finding: `check_totals` reads
**92.8%** against its own step-stable FD, and the one-word lever `limited → default` takes it to
**0.121%**, *"a single-process reproducer with a one-word on/off switch, no MPI in the loop"*, which
the report calls the better entry point for a maintainer. Four corrections are carried: the 719 KSP
erratum (corrected from a mis-transcribed 590; the collapse is 17.5×, **larger** than first claimed),
the 163,548 precision figure, the disclosed crossres2 control gap, and floor-unit banding (carried as
a lesson, codified at `FAMILY_SUPERVISION_GUIDELINES.md:67-71`).

### The options — all Katie's

| | option | consequence | failure mode |
|---|---|---|---|
| **4a** | **Do not file** | Status quo. Nothing leaves the machine. | A real, reproduced upstream defect stays unreported; maintainers have twice told other users the parallel case *"has issues"* (#946, #379) without a mechanism. |
| **4b** | **File as is** | Puts a 329×‖b‖ mechanism and a one-word serial reproducer in front of maintainers. | **The report's own readiness table (`:330-337`) has two rows NOT DONE**: a reproducer on a stock upstream tutorial outside this lab's tree, and mechanism-to-a-line. Filing before those are closed risks a report that cannot be reproduced by the maintainer on their own tree. |
| **4c** | **Close the two readiness rows first, then decide** | Removes 4b's failure mode. | Costs work nobody has priced; and the sibling `idwarp` report has a different destination (a comment on `mdolab/idwarp#57`), so a decision here does not settle that one. |

**Nothing in this document files, drafts a message to, or contacts anyone.**

---

## 5. The EIG recommendation, never implemented

### What was found
`campaign/EIG_RANKING_LOOKBACK_2026-08-10.md` (`99015d92`): the claim as filed — *EIG per core-min
beats the heuristic* — was **NOT established**; both rankings came out anti-correlated with delivered
value. Two results survived:
* **The numerator won.** De-confounded to a **mechanical keyword rule** that reads only
  `expected_knowledge_gain` and `gate` and cannot see an outcome: ρ = **+0.197 (p = 0.035)** against
  the gain table's +0.12 (p = 0.21), and top-20 precision **0.70** — higher than the hand-scored
  version's 0.65 and roughly double the gain table's. The document reports the head-to-head margin
  thinning from 424:241 to **357:312** under de-confounding and says so against its own metric.
* **The denominator is the broken half of both rankings** — 52 of 114 closed items filed at
  `est_core_min = 0` and **54 sit at or below the 1.0-core-min floor**, so the division does nothing
  for roughly half the docket, and where it is live it points the wrong way (ρ(cost, value) = +0.28).

### Cheap to act on, or wrong? — Measured: the numerator half is cheap; the denominator half is the real work
* **Implementing recommendation 1 costs zero compute.** The successor item
  `eig-bits-as-a-ranking-input-mechanically-scored` carries `est_core_min: 0` and a cost basis
  reading *"the lookback is already computed and on disk, the rule is a regular-expression scorer
  over two fields the docket already carries, and verification is a re-run of the published
  numbers."* Verified at HEAD: it is still `proposed`, `decided_at: None`.
* **Verified at HEAD: `_GAIN_POINTS` still stands** in `sdk/chief_engineer/agenda.py:115`.
* **The standing cost of non-implementation is lower than the rationale implies, and this is the
  finding that changes the price.** The successor's rationale argues from the gain table *"inverting
  the priority order it existed to serve"* — challenge work falling through to 2.0 so ladder work
  outranked it by 50% on every tie. **That specific defect was already repaired at `f2689232` on
  2026-07-30, eleven days before the lookback ran**: the table now scores `challenge` 4.0 above
  `gate` 3.0. So the motivating harm is gone; what remains is a measured but modest ranking
  improvement, not a live inversion.
* **Recommendation 4 is blocked on a second undecided item.** Its dependency
  `pre-registrations-carry-a-confidence-line` is also still `proposed`, undecided — so the strict
  retest cannot be scheduled by ruling on this item alone.

### The options

| | option | measured consequence | failure mode |
|---|---|---|---|
| **5a** | **Adopt recommendation 1 only** — swap the numerator for the mechanical rule | Zero compute. Ranking quality moves from ρ +0.12 (n.s.) to ρ +0.197 (p = 0.035); top-20 precision roughly doubles. | The head-to-head margin is thin (357:312) and the document says roughly half the original headline was hindsight. A regex over prose is brittle: a proposal worded outside the four patterns scores the 0.141-bit floor regardless of merit. |
| **5b** | **Adopt 1 and 3** — swap the numerator *and* fix or retire the denominator | Removes the inert division on ~half the docket; the control room's label *"expected knowledge gain per core minute"* stops describing a quantity that is, for those items, just the numerator. | Pricing zero-cost items honestly is real work nobody has costed; the alternative (declaring it a numerator ranking for report-shaped work) is a labelling change that concedes the ranking is two rankings. |
| **5c** | **Decline and close** | Zero action; the un-implemented recommendation stops being an open loop. | Discards a measured, de-confounded, zero-compute improvement — and leaves the lookback's own §5 mis-ranking analysis unactioned. |
| **5d** | **Leave as is** | Zero action, loop stays open. | This is the current state and it is the one with no argument behind it: a recommendation whose author explicitly said *"Do not change the ranking in force on this document alone … recommendation 1 belongs to the chief"* has been waiting since 2026-08-10 without a ruling either way. |

---

## 6. Owner-facing routing — two items, both decidable in one sitting

### 6a. Ratify the nine outcome sentences into `docket.json`
The sentences are drafted in `campaign/AGENDA_LOST_CLOSURES_FINALIZED_2026-08-16.md` (`b0f9ec7c`);
**five of the nine were recovered from what the doing agent had already written**, not authored, and
carry their anchors. **The mechanism was established by execution and it is two steps, not one:**

1. **`refresh_docket()` clears all seven LOST in a single call.** Verified read-only against HEAD:
   all seven are returned by `read_inbox()`, none is present in `docket.json` by id, and **none has
   an objective collision**, so none hits the `by_objective` skip that would strand it forever. The
   merge adds each whole record, carrying the file's status and the outcome already written.
2. **The two UNABSORBED need the sentence, and only they do.** `r2-closure-coefficient-uncertainty`
   and `hlpw6-testcase1-coarse-grid-entry` are already in the docket at `approved` with no outcome in
   *either* surface — the evidence lives in an artifact, so no carry can supply it. Each takes
   `set_status(id, "done", outcome=…)`, which is the step D219 reserved to the owner in writing.

**A defect in the check's own remedy, found while verifying this and reported rather than repaired:**
`scripts/check_proposal_surface_coverage.py:163-164` tells the reader to fix a LOST id *"via
`set_status`"*. **`set_status` is a silent no-op for all seven** — it iterates `load_docket()` and
returns `None` for an id the docket does not contain, so following the remedy literally would appear
to succeed and change nothing. The working order is `refresh_docket()` **first**.

### 6b. The HLPW6 workshop account — a standing constraint, not a capability gap
**Creating an account, requesting a participant identifier, and opening a merge request are all
three external interactions, and all three are forbidden to agents by the item's own charter.**
Verbatim, from `hlpw6-testcase1-coarse-grid-entry`'s `launch_prompt`:

> *ABSOLUTE: do not contact the workshop organisers, do not join a technology focus group
> distribution list, do not request a participant identifier, do not open a merge request against the
> submission repository, and do not create any account. **Katie decides whether this lab approaches
> this workshop at all, and she proofreads anything that would be sent.** The deliverable here is a
> result plus an honest assessment of whether it is worth her approving that approach.*

**The item did exactly what it was told to do.** It was charged *"Prepare, do not send"* and to
return a result plus an honest assessment; it returned both. Its "cannot be sent" finding is **the
requested assessment, not a failure** — the entry is unsendable **by construction and not by
capability**.

**What the assessment says, so the decision needs no further research:** the case is feasible on this
hardware (peak 4,548 MiB, 14.5% of host, headroom 6.7×; the binding limit is not memory). Against
that: **twenty second-order configurations were tried on an independent committee grid worse than
this one and all twenty diverged inside 29 iterations**, so the only configuration measured stable is
first-order upwind, which the probe itself calls *"not a defensible workshop submission"*; and the
mandatory eight-view Tecplot deliverable needs a rendering pipeline the lab does not have, priced at
zero. **Independent of the decision, the work already paid for itself**: `ugrid_to_foam.py` gave the
lab its first read path into committee grids at all, validated to an exact boundary-face match on a
2.66M-cell production grid.

**The decision is binary and it is hers alone: approve the approach to this workshop, or decline it.**
Nothing further is owed before it can be taken. **Approving the approach would not by itself make
the entry sendable** — the second-order numerics and the rendering pipeline are both unsolved, and
both are separate work.

---

**Compliance.** No solver runs, no scoring calls; the ledger stood at 6 and was not touched. Nothing
sent, uploaded, emailed, posted, registered or created — and §4 and §6b both turn on exactly that
constraint, which was observed rather than worked around. No account was made and no organiser,
workshop or maintainer was contacted. `deb91557` was not moved. `dist/`,
`demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` were not opened or written.
No proposal file, `docket.json`, or file on a peer's hold list was edited. **No decision in this
document was taken.**
