# Chief rulings on the four costed calls — 2026-08-16

**Costed at `9ea438fb` (`campaign/FOUR_CHIEF_CALLS_COSTED_2026-08-16.md`, D260/D261) with options,
consequences and failure modes and no recommendation. Ruled 2026-08-16. This document records the
rulings and what was executed under them.**

**Zero solver core-min, zero scoring calls; the ledger stood at 6 and was not touched. Nothing was
sent, posted, registered, emailed or created; no organiser, workshop or maintainer was contacted.**

---

## Ruling 1 — W1-only arm: KILL RATIFIED, and the dispatch surface CLEARED

**Ground, as ruled:** D213's deliverable-level ground, which holds *independently of whether the
trigger fired*. The arm's first deliverable is a G2 verdict, and G2 is invalidated six independent
ways, so a PASS establishes nothing and neither does a FAIL — **an arm that cannot produce
information in either direction is not underfunded, it is undefined.** The trigger firing on
2026-08-11 released the question; D213 answered it.

**Executed.** `demo-output/website/agenda/proposals/s1-cbfs-w1-only-arm.json` was moved from
`"status": "proposed"` to **`"dismissed"`**, with `decided_at` and a `dismiss_reason` carrying the
ground, the trigger record, and the instruction **not** to recite *"FAIL by construction"* — which
D213 records as refuted by execution, and which is why the deliverable-level kill is the one that
survives. The original `decision_note` was **retained unedited per L-44**, prefixed only with a
SUPERSEDED marker, because it is the record of what was decided on 2026-08-08 and on what grounds.
`est_core_min`, `objective`, `rationale` and `gate` were not touched.

**Verified after the edit:** `proposal_violations()` returns **NONE**, the file is still read by
`read_inbox()` and does **not** appear in `refused_inbox()` — so clearing the surface did not create
a third BLOCKED item.

**ONE CONSEQUENCE, STATED PLAINLY BECAUSE IT LOOKS LIKE A REGRESSION AND IS NOT.** The coverage
check's LOST count moved **7 → 8** and PENDING **46 → 45**. That is correct behaviour, not damage:
LOST is defined as *a decision recorded only in the file*, and recording the decision only in the
file is exactly what was possible here, because writing `docket.json` was forbidden to this pass.
The arm was a non-fault PENDING while it carried no decision; it becomes a fault the moment it
carries one that the docket has not absorbed. **It joins the same single `refresh_docket()` call
already routed to the owner for the other seven — it adds one id to that batch and no new kind of
work.** The alternative was to leave the expired justification standing, which is what the ruling
directed be cleared.

## Ruling 2 — Capability-strategy §2: LEAVE THE CLAUSE, BOX STAYS UNMARKED

**Ruled:** the refuted PROOF clause stays unedited at `docs/CAPABILITY_STRATEGY.md:37-39` **per
L-44** — that is what L-44 is for, and rewriting it would destroy the record of what was claimed.
The dated refutation and chief re-phrasing at `:141-173` are the **operative text**.

**The box stays UNMARKED**, on the ground surfaced in the costing: marking it would claim a
completion that an **unfiled external report is holding open**, and that report is Katie's to file.
**Its state is recorded as BLOCKED-ON-OWNER, not incomplete**, so that no reader takes it for work
outstanding in this lab. Nothing was edited in that file under this ruling.

## Ruling 3 — pydafoam regrades: NO REGRADE. CLOSED.

**Ruled on the finding itself:** a regrade **cannot move any verdict**, which makes this not a
decision about effort but about whether the question exists. It does not.

Anchored to the audit's own words, `WARMSTART_AUDIT.md:51-55` — *"**No standing record-grade
conclusion is overturned**"* — and `:57-59`, *"Regrade decisions belong to the chief per the
proposal's own terms; **this audit rewrites no conclusion**."* Seven of nine rows COLD-CLEAN.
**Row 6** (D3 n15 variant-lever nulls) had **already been ruled on 2026-08-10**, retired as
superseded at **0 core-min**, and **nothing currently cites those nulls** — verified independently
across `demo-output/` rather than inherited, where every surviving reference is an artifact inventory
or a retraction, `R5_ADJOINT_CONDITIONING.md:300-325` retracting the one causal conclusion they
supported. **Row 7** (R5/M6 matrix dumps) is order-of-magnitude conditioning robust to a ~2% drift,
corroborated at `R5_ADJOINT_CONDITIONING.md:312-314`, and flagged by the audit itself as *"expected
no-action"*.

## Ruling 4 — W4's upstream addendum: NOT THE CHIEF'S. ROUTED TO THE OWNER.

**Ruled:** filing means opening an issue against `mdolab/dafoam`. That is an **external post**,
reserved to Katie in writing in three places — `FAMILY_SUPERVISION_GUIDELINES.md:115` (*"**Nothing is
filed upstream by anyone in this family, ever** … filing is Katie's call alone"*), the report's own
header, and `campaign/COLD_START_TEST_2026-08-11.md:377-384`, which names filing the upstream report
among the **two most dangerous acts an ignorant agent could take**. The chief accepted it into his
queue at `b0f9ec7c` and has recorded that as his error; it routes to the owner.

**Filing READINESS is separate from filing PERMISSION, and both belong in her item.** The report's
own readiness table at `:330-337` carries **two rows NOT DONE**: a reproducer on a stock upstream
tutorial outside this lab's tree, and mechanism-to-a-line. So permission and readiness can be decided
independently, and neither implies the other.

**Nothing was filed, drafted for sending, or transmitted.**

---

## Ruling 5 — EIG recommendation 1: IMPLEMENT was ruled, and it is REPORTED BACK UNEXECUTED

**The ruling was to implement, on the restated ground that ρ = +0.197 (p = 0.035) against the gain
table's +0.12 (n.s.) is a significant ranking against a non-significant one — and explicitly NOT on
the item's own stated rationale, which is dead because the gain-table inversion it argues from was
repaired at `f2689232` on 2026-07-30, eleven days before the lookback that argued from it ran.**

**That restatement stands and is recorded. The implementation was not made, and the reason is that
the premise this pass supplied for calling it cheap does not survive execution.** The costing at
`9ea438fb` quoted the successor item's cost basis — *"verification is a re-run of the published
numbers"* — as evidence the change was cheap. **That clause is false, and it was this pass that put
it in front of the chief.** Measured at HEAD:

1. **The lookback committed no dataset, no scorer and no ground truth.** `git show 99015d92
   --name-only` returns exactly two paths: the prose record and the proposal file. Its statistics are
   correlations against a per-item delivered-value grade **V** that exists in no committed artifact;
   `CALIBRATION_SCORECARD_2026-08.md` carries no V column, and no file in the tree defines one.
   **So ρ = +0.197 cannot be recomputed by anyone, and a reimplementation cannot be checked against
   it.**
2. **The mechanical rule's own tier populations were never published.** §3's `n = 2 / 35 / 7 / 26 /
   44` are the **hand** tiers, which §6 says the mechanical rule replaced precisely to remove
   hindsight, and which it matches only at ρ = +0.70. A faithful reconstruction of §6's abbreviated
   patterns was written and run over the docket here: it returns **A3 n=2** (agreeing) but **A n=15
   against 35** and **B n=13 against 7**. Whether that is a defect in the reconstruction or the
   expected divergence between the two tierings **cannot be determined**, because the mechanical
   rule's populations were never recorded.
3. **The cohort has moved.** The lookback scored **114** `done` items; the docket carries **118**
   today, so even a published population would no longer be a like-for-like check.
4. **Wiring it in force turns a peer-held test file red.** `sdk/tests/test_agenda.py` encodes the
   incumbent as its specification — `test_ranking_is_gain_per_core_min_and_deterministic` asserts a
   gain-table ordering, and `test_grandfathered_rows_are_not_refused_retroactively` asserts
   `rank_value == _GAIN_DEFAULT / 2.0`. Both fail under a faithful numerator swap. `sdk/tests/` is on
   another agent's hold, so this pass could neither update them nor leave the suite red. Baseline
   confirmed green first: **52 passed**.

**What this pass declines to do, and why.** Writing an unverifiable scorer into `gain_points()` —
the function that decides what the fleet works on next — on a rationale already shown dead, with no
way to check it and no ability to update the tests that specify it, is the shape this lab keeps
catching. **The honest report is that the action is not cheap; it is unverifiable, which is a
different thing and a worse one.** `sdk/chief_engineer/agenda.py` was **not modified**.

**What would make it executable, none of which is a research question:** (a) the sdk/tests/ holder
releases the two tests, or agrees the specification changes with them; (b) the mechanical rule is
published as code or its tier populations recorded, so a reimplementation has something to reproduce;
(c) the V grades are committed, so ρ can be recomputed on the current cohort. **(b) and (c) are
recoverable only from the agent that ran the lookback or by re-running it** — the lookback is
reproducible in principle (its inputs are on the docket) but its grading step is not, because the
grading was a judgement that was never written down.

**Recommendation 4 was not touched**; it remains blocked on `pre-registrations-carry-a-confidence-line`,
still `proposed` and undecided.

---

## Corrections to D253's Owner column

All three were identified by this pass against its own prior work and are corrected at the row.
**D253's substance stands; only its routing moved.**

* **W4's upstream addendum** was routed to the chief. It is **Katie's** — filing is an external post
  (Ruling 4).
* **`pydafoam`'s regrades** were listed as an open chief decision. They are **closed, NO REGRADE**
  (Ruling 3).
* **The W1-only arm** was described as a plain go/no-go. It was a **ratify-or-overrule against a
  stale dispatch surface**, now ratified and cleared (Ruling 1).

---

## The two owner routings — unchanged, and repeated here so they travel with the rulings

**Ratification.** `refresh_docket()` clears every LOST id **in one call** — verified read-only in
memory that each is returned by `read_inbox()` with no id and no objective collision, so none hits
the skip that would strand it. **That batch is now eight, not seven**, the eighth being the W1 arm
dismissed under Ruling 1. Then `set_status(<id>, <status>, outcome=…)` for the **two UNABSORBED
only** — `r2-closure-coefficient-uncertainty` and `hlpw6-testcase1-coarse-grid-entry` — whose
evidence lives in an artifact no carry can reach, and whose outcome sentence D219 reserved to the
owner. *(The coverage check's remedy string, which had told the reader to use `set_status` for the
LOST class — a silent no-op there — was repaired by another agent after D261 was filed; the check now
prints the `refresh_docket()`-first order.)*

**HLPW6.** Creating an account, requesting a participant identifier and opening a merge request are
**all three external interactions**, and all three are forbidden to agents by the item's own ABSOLUTE
list. **This is a standing constraint, not a capability gap.** The item was charged *"Prepare, do not
send"* and to return a result plus an honest assessment; **its "cannot be sent" finding IS that
assessment, not a failure.** Approving the approach would **not** by itself make the entry sendable:
twenty second-order configurations all diverged inside 29 iterations, and the mandatory eight-view
deliverable needs a rendering pipeline priced at zero. Both are separate unsolved work.

---

**Compliance.** No solver runs, no scoring calls; ledger at 6, untouched. Nothing sent, uploaded,
posted, emailed, registered or created; no account made; no organiser, workshop or maintainer
contacted. `deb91557` was not moved. `docket.json` was **not** written. `dist/`,
`demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` were not opened or written.
No file on a peer's hold list was edited — `sdk/tests/` and
`scripts/check_proposal_surface_coverage.py` were **read and run, never modified**.
