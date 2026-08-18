# Ten new research directions, ranked — 2026-08-14

**Clock verified before any date or rate in this file was written:** `date -u`
reads `Fri Aug 14 22:13:18 UTC 2026`.

**Commit anchors, and they are plural on purpose.** Other sessions were
committing throughout this work, so HEAD moved under it: `49c8aae4` →
`c966bf7e` → `7009c745`. Each measurement below carries the commit it was taken
at rather than inheriting one. Where a number is a property of the repository
rather than of the world it is written as *"as of `<sha>`, X holds"* and is
expected to move. Nothing here is stated in the present tense about a file.
(This is also why `git status` is not used as evidence anywhere in this file —
under concurrency it has read this session's dirty files as clean before.)

**Frame, stated once and binding on every count in this file.** Repository counts
use `git ls-files` or a direct directory listing, never this shell's `grep -r`,
which is `ugrep --ignore-files` and sees roughly 23% of the tree. Archive counts
are over `/home/ubuntu/certonomous-runs`, which is **outside the repository and
invisible to every repository-scoped search**.

---

## 0. Three corrections to the brief this work was commissioned under

These are reported first because two of them change what a good proposal looks
like, and the third is a defect found while checking the first.

**0.1 — The calibration figures in the commissioning brief are stale, and the
lab is less bad at forecasting than it was told.** The brief states 114
proposals, 3 scoreable pairs and 0 of 3 within 20%. Executed
`scripts/calibration_scorecard.py`, **which self-reported `49c8aae4 +dirty
working tree`**: **121 proposals, 19 done, 11 scoreable pairs, 3 of 11 within
20% (27%)**. (Re-run after this file's ten records landed it reads 131
proposals; `done`, `pairs` and the hit rate are unchanged, because all ten are
`proposed`.) Eight closed records still carry no
measured cost, which the instrument itself calls the binding constraint, and it
is right. The forecasting problem is real; the *record* problem is bigger.

**0.2 — The instrument that measures the lab's forecasting has two measured
defects, one of which fails a perfect forecast.** Reproduced 2026-08-14.
`calibration_scorecard.py:98` divides the absolute error by the measured cost and
substitutes `float("inf")` when the measured cost is zero. Two closed records
(`pydafoam-silent-warmstart-state-hazard`, `s1-cbfs-weighted-loss-offline-variant`)
were forecast at 0 and measured at 0 — **exactly right, printed as `MISS … inf%
off`**. That is defect class B2 arriving in the instrument that grades the lab.
Separately, `:110` evaluates the standing "3 consecutive within 20%" capability
rule over `pairs[-3:]`, and `pairs` is built by iterating `sorted(glob("*.json"))`
— **filename order, not time order**. Measured: the triple the rule inspects
today is `w4-defect-acquisition…`, `w4-three-discriminators…`,
`w4-upstream-report…` — the three names that sort last. Ordered on the records'
own `completed_at`/`executed_at`, the last three are
`s1-cbfs-weighted-loss-offline-variant`, `kfamily-fpe-shared-diagnosis…`,
`pydafoam-silent-warmstart-state-hazard` — a **disjoint set**. A rule written
about time has never once been evaluated about time. Filed as proposal
`the-calibration-instrument-fails-a-perfect-forecast-and-orders-its-streak-alphabetically`.

*Check that the proposed repair is not self-serving:* under **both** fixes the
standing 3-for-3 rule remains **unsatisfied** (the corrected time-ordered triple
reads HIT, MISS, HIT). A repair that had flipped the gate green would have been
the suspicious outcome.

**0.3 — The brief says "about 118 JSON records". There are 121 files. The
difference is three real proposals the intake silently discards.** Invoking
`agenda.read_inbox()` then `agenda.refused_inbox()` **before this file's ten
records were added** (repository head `c966bf7e` era, 2026-08-14): 121 files in,
**118 returned, 3 refused** —
`dafoam-restore-ksp-options-escape-hatch` (15 core-min),
`f5c-unsteady-probe-run`, and
`test-the-solver-default-relaxation-across-the-family` (26 core-min). Two of the
three are solver-and-numerics work, a well the lab is actively trying to fill.
Plus: `queued` is not in `agenda.STATUSES`, so
`tmr-flatplate-finest-grids` and `tmr-naca0012-complete-ladders` — **807 core-min
somebody deliberately queued** — read back as merely `proposed`. And
`refused_inbox()`, written expressly against the principle that *a filter nobody
can see is a filter nobody can question*, has **no caller anywhere outside
`sdk/tests/test_agenda.py`** (frame: `git ls-files`, system `grep`, `dist/`
excluded). The remedy was implemented, tested, and left unwired. Filed as
`three-filed-proposals-are-invisible-to-the-docket-and-nothing-anywhere-says-so`.

---

## 1. What was written

Ten records, all `status: proposed`, all `created_at: 2026-08-14`, all validated
by executing the real loader: **131 files in, 128 loaded, 3 refused — the same
three that were refused before, so these records add zero refusals.**

**All ten are ZERO SOLVER COMPUTE as requested.** Six of them are the
zero-compute first stage of an expensive question and are explicitly permitted to
kill the expensive stage. Compute authorisation is Katie's and nothing here is
authorised.

**Every record forecasts its cost in a unit that can actually be scored.** A zero
core-minute forecast is unscoreable — that is defect 0.2 above — so each record
also carries `est_tool_calls`, placed against this lab's measured base rates
(bounded-question 2–5 calls; build-and-verify 33–72 calls), and states that the
actual will be counted from the executing agent's own transcript and written back
as `measured_tool_calls`. **This is a new field and it is a proposal in itself:
if the lab keeps forecasting solver work in core-minutes and agent work in
nothing, sixteen more records will close unmeasured.**

| # | id | well | forecast tool-calls | hard | what it could kill or unblock |
|---|---|---|---|---|---|
| 1 | `does-the-residual-threshold-that-declares-convergence-bound-the-graded-quantitys-remaining-drift` | numerics | 55 | no-case | every credential resting on a residual convergence declaration |
| 2 | `every-published-zero-in-this-corpus-and-whether-a-control-stood-beside-it` | verification (B1) | 60 | instrument-check | the naval gap map and the 257-request reordering filing both rest on a zero |
| 3 | `is-the-cbfs-correction-even-transplantable-an-out-of-distribution-screen-before-the-cross-case-run` | closure | 50 | no-case | a cross-case arm of the order of 267–425 core-min, before it is proposed |
| 4 | `windsor-squareback-a-road-vehicle-reference-this-lab-can-re-derive` | cases | 45 | 1 | the road-vehicle line's unsourceable reference (docket D15) |
| 5 | `wigley-parabolic-hull-the-free-surface-case-whose-geometry-is-a-formula` | cases / free-surface | 30 | 4 | the naval ladder block that sits under 4,035 filed core-min |
| 6 | `an-external-reproducibility-ensemble-is-this-labs-tolerance-tighter-than-the-communitys-scatter` | statistical / cases | 28 | 3 | ~166 filed core-min of closure-family matrices on unsteady quantities |
| 7 | `price-the-interval-before-buying-the-sample-a-precision-floor-for-every-planned-claim` | statistical | 25 | no-case | any planned success-count claim that cannot move a belief at its planned n |
| 8 | `the-calibration-instrument-fails-a-perfect-forecast-and-orders-its-streak-alphabetically` | infra / verification | 40 | instrument-check | the CAPABILITY_STRATEGY §4 capability rule |
| 9 | `the-wave-boundary-condition-echoes-its-theory-or-the-naval-purchase-is-unprovable` | free-surface | 12 | instrument-check | the 135 core-min seakeeping capability step |
| 10 | `three-filed-proposals-are-invisible-to-the-docket-and-nothing-anywhere-says-so` | infra | 0 | instrument-check | 41 core-min refused + 807 core-min silently de-queued |

---

## 2. The ranking basis

**Ranking without a stated basis is opinion, so here is the basis, and it is
recomputable from the records.** Solver cost does not enter, because every item
is zero-compute; that is deliberate and it means cost cannot do the ranking work.
Three inputs, each a stated fact rather than a score:

1. **Reach** — how many *named* filed items the outcome could cancel, redirect or
   unblock. Counted, and the items are named in each record's citations.
2. **Leverage** — the filed `est_core_min` of that work, summed. Taken from the
   records, not estimated here.
3. **Decidability** — are *both* branches of the verdict reachable with an
   instrument already proven in this lab? Three values: yes / partly / **already
   decided** (the last is a *demerit*, not a merit: an item whose outcome is
   already known is a repair, not an experiment).

Tie-break: fewer forecast tool calls wins.

| rank | id (short) | reach | leverage (filed core-min) | decidability |
|---|---|---|---|---|
| 1 | residual-vs-graded-drift | ~6 named + every residual-gated credential | **877+** (807 TMR, 55 hills, 15 bump) | yes — both controls named and both known to exist |
| 2 | published-zero census | class-wide; 3 named zeros are load-bearing | **4,035** naval rests partly on one zero | yes — planted control makes both branches reachable |
| 3 | transplantability screen | the cross-case direction + 160 | **~427–585** (unfiled arm + band validation 160) | yes — within-case held-out control is executable |
| 4 | Windsor squareback | road-vehicle family, 2 named + D15 | **124** filed, unbounded future | yes — both halves fetched 2026-08-14 |
| 5 | Wigley hull | 4 named naval items behind one block | **4,035** | **partly** — scan legibility is a real risk, stated |
| 6 | BARC external ensemble | 6 named unsteady/scatter items | **~166** | yes |
| 7 | precision floor | every success-count claim; 4 named | **160+** | yes, but see §4 |
| 8 | calibration instrument | the §4 capability rule + all future costing | 0 direct | **already decided** on 2 of 3 deliverables |
| 9 | wave lever echo | exactly 1 filed purchase | **135** | yes |
| 10 | inbox filing | 5 named records | **848** | **already decided**, and gated |

---

## 3. The discriminating outcome of each, in one line

Stated as *what moves belief* and *what leaves it unmoved*, because a proposal
whose every outcome leaves belief unmoved must not be written.

1. **Residual vs graded drift.** *Moves:* a material unbounded fraction means
   residual-threshold convergence is not a sufficient gate anywhere in this lab
   and every gate needs a graded-quantity plateau criterion beside it. *Also
   moves:* a near-zero fraction with both controls recovered vindicates the
   practice on evidence. *Unmoved:* a no-verdict count that swamps the other two
   — reported as a **records** defect, not as a result about convergence.
2. **Published-zero census.** *Moves:* one re-derived zero coming back different
   means the sanctioned sweep helper's landing did **not** close the
   highest-priority defect class. *Unmoved:* the proportion of uncontrolled zeros
   on its own — reported, never gated on.
3. **Transplantability screen.** *Moves:* out-of-support targets cancel their
   cross-case runs for zero compute and yield a bounded published statement about
   where the correction's support reaches. *Unmoved:* a within-case control that
   fails to score near its ceiling — that is a finding about the statistic.
4. **Windsor.** *Moves:* the lab gains a road-vehicle reference it can re-derive
   from raw measurement; **or**, for zero compute, learns that no sourceable
   road-vehicle reference exists at all. *Unmoved:* a missing column → gap-map row.
5. **Wigley.** *Moves:* geosim agreement gives a hull case with an *algebraic*
   geometry and a primary **tabulated** reference; disagreement is a citable
   result that classical hull wave-profile data carries scale effect at the
   graded quantity. *Unmoved:* an illegible scan → gap-map row naming the lost
   stations.
6. **BARC.** *Moves:* a lab tolerance tighter than the published community
   dispersion means the gate measures set-up luck, not model quality. *Unmoved:*
   lab bands already wider — the doubt is removed and the item closes cheap.
7. **Precision floor.** *Moves:* an underpowered planned claim grows or dies.
   *Unmoved:* the width table itself (see §4).
8. **Calibration instrument.** *Moves:* deliverable three only — other
   consecutive-event criteria with unstated ordering keys would generalise the
   defect past one script. *Already decided:* deliverables one and two.
9. **Wave lever echo.** *Moves:* "unprovable" means the 135 core-min purchase
   would produce a capability claim with no activity proof, caught **before** the
   spend rather than years after, as the 257-request reordering lever was not.
10. **Inbox filing.** *Moves:* the general point — this lab has at least one
    measured case of a remedy implemented, tested and never wired to a surface.

---

## 4. The identity test (owner rule W-2), answered for every gate

The lab has been burned by a correlation of **+0.9742** that carried no
information because its null sat pinned at **+1.0000** and the accepted iterate
satisfied the constraint to **1.11e-16**. Every record answers W-2 explicitly.
Three answers are worth pulling out here because they *changed the design*:

- **Residual vs graded drift — the obvious formulation was REFUSED.**
  Correlating residual level against remaining drift would be *near-identity*:
  both come from the same iteration history and both decay, so a strong positive
  correlation is guaranteed by construction. The gate is instead an **absolute**
  comparison against an externally set number — the pre-registered grading
  tolerance, written by a different person at a different time for a different
  purpose.
- **Precision floor — the central quantity IS an identity, and it is therefore
  not gated on.** An exact binomial interval width is derived by construction
  from `(n, k)` and nothing else. It is **reported as a design calculation**, the
  way a cell count is reported. What is gated on is a *procedural* fact that
  cannot be computed from the width: whether a planned claim's record carries its
  achievable width before the sample is bought.
- **Calibration instrument — the zero-zero pairs are an identity and are NOT
  reclassified as hits.** A task with no solver in it was always going to cost no
  core-minutes; counting those as hits would inflate the rate from 3/11 to 5/11
  on two records that tested nothing. They go into a named **third class**,
  excluded from the rate, printed with their count. Neither a false fail nor
  false credit.

Two further W-2 answers worth recording: the Windsor gate's file-integrity
recomputation (`Cd = F / (q·A)`) **is** an identity if the file was written that
way, so it gates only *file usability* and is explicitly not the scientific gate;
and taking a blockage correction from the same file that supplies the reference
drag **would** make the comparison an identity, so it is forbidden in advance and
the computation must reproduce the tunnel walls instead (the dataset README states
that no corrections of any kind were applied).

---

## 5. New test cases — both halves verified, and one gap-map row

The naval line learned that reference data being excellent does not mean the
geometry is obtainable (DTMB 5415: navy host DNS-dead, simman2014
registration-walled, simman2008 TLS cert mismatch). Every case below was
verified **in both halves, separately, by machine fetch on 2026-08-14**.

| case | geometry half | data half | verdict |
|---|---|---|---|
| **Windsor squareback** | Figshare `10.17028/rd.lboro.13161284`, `Geometry.zip` 175,806,555 B, STEP + STL, body + mounting + tunnel. Ranged GET → **HTTP 206**, `application/zip`, **no credential** | Same record, **not embargoed**, **CC BY-NC 4.0**. `Set A` 3,872,216,377 B: force means (300 s @ 300 Hz, with frontal area, wheelbase, density), **128 pressure tappings + tapping map**, tomo + planar PIV with mean and RMS. README fetched and read end to end | **BOTH HALVES OPEN.** One owner decision: the licence is **non-commercial** and this lab is a company. Flagged, not assumed |
| **Wigley parabolic hull** | **An algebraic expression.** Half-breadth = parabola in x × parabola in z. Nothing to download, no host, no certificate, no registration | Cooperative experiment summary, 17th ITTC Resistance Committee 1983, open Internet Archive mirror of DTIC `ADP003037`. GET → **HTTP 200, 2,376,271 B, no login**. Text-converted here: 10,520 lines; CT/Cf/Cw/Cwp for four geosim models (6.0, 4.0, 2.5, 2.0 m); an explicit numbered **table** of nondimensional wave elevation | **BOTH HALVES OPEN, WITH ONE STATED DEFECT.** It is a 1983 scan and the table's numerals come out of the text layer **garbled**. The data is a *table*, not a figure — strictly better than the dam-break reference — but it must be read off the page image, not scraped. Said before anyone budgets for scraping it |
| **BARC 5:1 rectangular cylinder** | **Two numbers.** Chord-to-depth 5, sharp edges. Setup section fixes Re_D range, caps blockage at 5%, bounds edge radius | Overview preprint openly downloadable: GET → **HTTP 200, 4,682,968 B, `application/pdf`, no credential**; converted to 2,294 lines and read here. Carries ~70 realisations' inter-contributor ranges | **PARTIAL — and the gap-map row is the deliverable.** The **member contribution database is registration-walled** (login + registration link on the front page). No account was created and none will be. The usable reference is the published overview, not the raw contributions |

**What BARC's numbers are, and why they matter more than the case does.** Read
out of the fetched text: time-averaged C_D across the LES contributions spans
**0.96 to 1.39**; across URANS and hybrid, **0.965 to 1.295**; wind tunnel values
sit between **0.94 and 1.05**. The paper's own conclusions: the near wake, base
pressure and hence drag agree well, while the side-surface flow and hence lift
are strongly sensitive to set-up and modelling; and **"none of the approaches to
turbulence seem to reduce the result dispersion"**. That last sentence is a
published prior that any model-form matrix on an unsteady bluff-body quantity is
implicitly betting against. Betting against a published prior knowingly is
science. Doing it unknowingly is not.

**A case NOT proposed, and why it is worth saying.** The 2026-08-02 challenge
sweep mapped **AutoCFD5** as *preparable, not sendable* behind three forbidden
gates with a 37M-cell minimum entry grid (~58 GiB against a 30.6 GiB host). That
verdict is about the **submission**. The Windsor body and its measurements are
separately and openly licensed by the university that took them and are subject
to **none** of those gates. The lab appears to have dropped the case together
with the workshop. **The case is the part that was never walled off.**

---

## 6. What should be CANCELLED, on the evidence

### 6.1 CANCEL — `hlpw6-testcase1-coarse-grid-entry`, **6,390 core-min**

The single largest item on the docket, and **every outcome leaves belief
unmoved.** Four independent reasons, each from a lab record rather than from
judgement:

1. **Its `gate` field is literally `None`.** It states no criterion, so no
   outcome can be a verdict.
2. **It is a *blind* case.** By construction the lab has no reference data to
   grade against. A "good" number cannot be shown to be good.
3. **The only route to a score is forbidden.** The lab's own challenge sweep
   records HLPW-6 as *"PREPARABLE, NOT SENDABLE — all three forbidden gates"*
   (GitHub account, organiser-issued identifier, pull request), independently
   re-confirming `hlpw6/SUBMISSION_GATE.md`. External interaction is PARKED and
   reserved to Katie. Its stated objective — *"assess whether the result is
   strong enough to be worth Katie approving an approach to the workshop
   organisers"* — is a decision Katie can make **now, for free**, and the 6,390
   core-min does not inform it, because point 2 means the run cannot tell her
   whether the result is strong.
4. **Its own cost basis concedes the configuration is indefensible.** In the
   proposal's own words, the configuration measured as stable *"uses first order
   convection, which is not a defensible submission; a second order entry is
   dearer and less robust."* Plus an unpriced 8-view rendering deliverable.

**Recommendation:** dismiss with a `dismiss_reason`, not delete. If the
submission gate ever lifts, the 2,661,338-cell grid import and the format reader
that were already built are the reusable part and should be cited from the
dismissal so that work is not repeated.

### 6.2 SECONDARY cancel candidate — `probability-of-rank-a-posterior-over-our-score-against-the-board` (approved, 0 core-min)

A bootstrap posterior over the lab's rank against a board, explicitly *"internal
only, never attached to a submission"*. No decision in the lab depends on
predicted rank, and the record itself forecloses the one use that would create
such a decision. Argued as a candidate rather than asserted as a cancel, because
it costs no compute — but it does cost an agent mission (88–160k tokens on this
lab's own measured band), and the standing refill doctrine makes agent time the
scarce resource, not core-minutes.

### 6.3 RESEQUENCE, not cancel — `f7-kcs-container-ship-calm-water-resistance-gate` (3,000 core-min) behind Wigley

Same physics class (steady calm-water free-surface hull resistance). KCS costs
3,000 core-min on an explicitly unanchored basis, in a lab where **no ship case
has ever run**, against a geometry that must be downloaded. Wigley is the same
capability question with a geometry that is generated by arithmetic. Buying KCS
first is buying the expensive instance of an untested capability. The KCS record
already recommends a 450 core-min feasibility slice first; **a hull whose
geometry costs nothing to obtain is the cheaper feasibility slice.**

---

## 7. Why the bottom-ranked items are worth less

Required, because a ranking that will not say what its own tail is for is a
ranking that ranked nothing.

**#8, calibration instrument repair — worth less because the experiment is
already over.** Two of its three deliverables have *no* discriminating outcome
left: the `inf%` fail-false and the alphabetical streak ordering were both
reproduced during the drafting of this file, at 2 tool calls. What remains is a
repair, and repairs are necessary but they are not research. Only deliverable
three — the sweep for *other* consecutive-event criteria with unstated ordering
keys — is still open, and it is the only part that could generalise. It is ranked
8 rather than lower because the instrument it repairs is the one every future
cost forecast is scored on, so leaving it broken taxes everything above it.

**#9, wave lever echo probe — worth less because its reach is exactly one
purchase.** It is the best cost-to-leverage ratio on the page (12 forecast tool
calls against a 135 core-min purchase) and it will probably be the cheapest thing
the lab runs this week. But it touches **one** filed item and one capability
claim. Compare #2, whose single planted control speaks to every zero the corpus
has ever published. Breadth beat ratio here, and that is the ranking rule
working, not being overridden.

**#10, inbox filing — worth least on three counts at once, and it is still worth
writing.** (a) It is a **filing, not a start**: repo/infrastructure work is gated
until Ladder V converges, so its value is realised later or not at all. (b) It is
**already fully decided** — all four of its assertions are measured, so nothing
remains to learn from executing it. (c) Its residual question is a **ruling, not
a task**: whether a style rail should refuse a whole record or name the offending
phrase and pass the rest is Katie's call, and no amount of agent work produces
it. It is written down anyway because the alternative is that the next person to
count this corpus counts 121, or 118, and cannot tell which number they have —
which is exactly what happened to the brief that commissioned this work (§0.3).

---

## 8. What was deliberately NOT written, and why

Recorded so the same ground is not re-covered. Checked against all 121
pre-existing records before drafting.

- **A regular-wave generation and absorption run.** Already filed at 135
  core-min. Proposal #9 is the zero-compute *provability* question underneath it,
  which is a different question, and it says so on its face.
- **A dam-break reference triangulation.** Already filed at zero compute. Wigley
  is a *second, better-sourced case*, not a re-audit of the first, and the two
  are complementary: one asks whether the current reference is right, the other
  whether a better one exists.
- **A `jacMatReOrdering` readback arm.** Already filed at 8 core-min (docket D10).
- **A tensor-basis rank measurement on the ducts.** Already filed at zero
  compute. Proposal #3 asks a related question on a different family with a
  different statistic and a within-case control.
- **A band-containment census.** Already filed. Proposal #7 is its
  forward-looking complement and attaches a number to purchases not yet made.
- **Anything requiring an account, a registration, an email, a pull request or a
  submission.** All external interaction is PARKED and reserved to the owner. The
  BARC member database was found walled and was left walled; the row it produced
  is a gap-map entry, which is itself a product.

---

*Filed by the research-direction agent, session `64b13819`. Ten records written
to `demo-output/website/agenda/proposals/`, all ten validated through
`agenda.read_inbox()` at `7009c745`: 131 files in, 128 loaded, 3 refused, and the
three refused are the same three that were refused before these records existed.
Zero solver compute was spent and none is authorised by anything in this file.*
