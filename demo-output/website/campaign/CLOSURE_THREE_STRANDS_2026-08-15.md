# Closure challenge — the three open strands re-established by execution, 2026-08-15

**Executed 2026-08-15, 23:14–00:0x UTC (`date -u`, run). Repo anchor at start: `54a562a3`.**
**Compute spent: zero.** No solver, no container, no inversion, **no scoring call — the ledger
stands at 6** — no network read, no fetch. Every number below is arithmetic over files written
before this document was opened. **Nothing was sent, uploaded, emailed, filed or registered;
submission remains PARKED and every send is Katie's.** The scoring pin `deb91557` was not moved.

Brief: establish the real state of the three long-open strands — **submission policy research**,
**Stage 1 FIML**, **C2 decomposition** — *by execution rather than by reading the task list*; kill
what can be killed at zero compute; apply the W-2 identity test to every gate on the line; price
what genuinely needs compute with its discriminating outcome; and report, never silently repair,
any claim stale against the live board.

**Live board, used as reference throughout and not re-derived here:** six published entrants plus
our own row = **seven positions**, retrieved **2026-08-11T23:33Z**, re-verified unchanged
**2026-08-14T21:01Z**. Rank **1 of 7**; best-on-board **2 of 8** with **zero of 8 earned by our
own model** (both survivors are decline-gate pass-throughs of the organisers' own unmodified RANS
field); P(rank 1) **50.2%**, interval **0–97% at 95%**; Yang margin **0.001365** on the
mean-of-eight basis; seed bound **0.002419**, i.e. **177%** of the margin. **A commit anchor is
not an admissible board identifier** — `deb91557` scores, it does not rank.

---

## 0. Headline, in the order the evidence forces

1. **A 150 core-min proposal is live, its named release trigger has FIRED, and its dispatch
   surface carries no record of the two documents that killed it.** `s1-cbfs-w1-only-arm.json`
   still reads `"status": "proposed"` with a 2026-08-10 `decision_note` saying *NO-GO FOR NOW*
   pending a trigger that fired on 2026-08-11 and was re-affirmed on 2026-08-14 — the S1-priors
   pre-registration, which **explicitly releases the arm back to the chief** (§1). Killed here on
   two independent legs, neither of which is the reason on the record.
2. **The published reason for that kill is REFUTED by execution, and the kill survives anyway.**
   *"It would score 8.4% and FAIL by construction"* assumes a window-only loss confines the
   deviating β set to the window. The one executed restricted-support arm on disk says otherwise:
   a loss supported on **14.14%** of cells produced a β field deviating from 1 in **94.49%** of
   them (§1.2). The `np.quantile` degeneracy the reason invokes needs the deviating set below
   10%. The document that gives the reason contradicts it four sections earlier in its own text.
3. **A NEW non-discriminating gate clause, on the entry of record's own validation control.**
   R5's gate clause **V3** — *"both arms converge on their own `residualControl` within the cap"*
   — is decided entirely by `k` and `omega`, the **only** two entries in `residualControl` in all
   five arms. Neither pressure nor any velocity component appears. Measured: in the SST validation
   control, whose in-plane field is V1's denominator and one side of V2's correlation, the initial
   residuals of `Uy`, `Uz` and `p` **never fall below 0.110, 0.158 and 0.280 across all 4,652
   iterations** while the solver prints *"SIMPLE solution converged"* and V3 reads pass (§3).
4. **C2's central statistic could not have failed, and the audit that cleared it checked the
   arithmetic instead.** Pearson r(floor, delta) = −0.9418 puts the floor on both sides. The exact
   permutation null over all **120** pairings runs **[−0.9940, −0.9418]** with mean **−0.9583**;
   the observed value is the *least negative the null can take*, one-sided p = **0.983**, and
   **100% of permutations give r ≤ −0.90**. The un-confounded statistic is r = **+0.3259**
   (Spearman +0.3000, p = 0.625) — nothing. Second kill (§4.1).
5. **C2's targeting instruction is now exactly backwards, and no surface says so.** C2 directs
   effort at the `alpha_05` regime *"and nothing else"* and dismisses the NASA hump as *"at most 2%
   of the available term"*. On the live board the hump is **43.6%** of remaining headroom
   (0.033798), larger than `AR_1` + `AR_3` combined (32.5%) (§4.2).
6. **"Four of the five open policy questions bind a first send" has never been enumerated
   anywhere, in any arm.** The phrase occurs in exactly two places in the corpus and D31, its
   source, lists **five** and names **none** of the four. The count has no referent (§2).
7. **No new stale board claim was found by the count-of-eight sweep, and it nearly manufactured
   two — but reading C2 line by line found nine.** 78 candidate lines swept and every one resolved;
   both near-misses came from my own line-wise strike detector, which cannot see a multi-line `~~`
   span (§5). The nine that are real are all in C2 and in the audit that cleared it (§4.5), and
   they were invisible to that sweep because C2 states its counts in words, not in the `n of 8`
   form any denominator predicate matches.

---

## 1. KILLED AT ZERO COMPUTE — `s1-cbfs-w1-only-arm`, 150 core-min

### 1.1 The live hazard, established by execution

| fact | value | how established |
|---|---|---|
| proposal status at HEAD | `"status": "proposed"` | `json.load` of `demo-output/website/agenda/proposals/s1-cbfs-w1-only-arm.json` |
| price | `"est_core_min": 150.0` | same |
| last touched | `b4fd62e7`, **2026-08-10 15:43:18** | `git log --format='%h %ci %s' -3 -- <path>` |
| its whole standing decision | `decision_note`: *"NO-GO FOR NOW by chief ruling at entry-12 close (commit `7b758783`): approved in principle with a **NAMED TRIGGER** — the S1-with-priors design phase … Do not claim, price, or launch **before that phase opens**"* | same file |

**The trigger fired, and the item that fired it says so in its own words.**
`demo-output/website/dafoam/ladder-b/S1_PRIORS_PREREGISTRATION.md:7-9` opens by naming itself
*"the named TRIGGER that unblocks `s1-cbfs-w1-only-arm` (that proposal's `decision_note`, chief
ruling `7b758783`)"*. That file was written 2026-08-11 (`ecbdc288`) and last amended 2026-08-14
22:42 (`f1cec9d3`). Its `:208-214` reads:

> **Loss support (the decision the W1-only arm is waiting on): equal-weight, all cells.** … The
> W1-only arm's question is therefore **not** consumed by this item and is **released back to the
> chief** as a separate go/no-go, with this item's reason recorded.

So at HEAD the arm is **released, unpriced-against, and dispatchable in principle**, and its
dispatch surface is eleven days old and says only *"NO-GO FOR NOW"*. This is D41's class —
a proposal JSON is a dispatch surface, not a narrative record — on a live 150 core-min purchase.

### 1.2 The kill, on two legs, neither of them the one on the record

**Leg 1 — its first deliverable is a G2 verdict, and G2 cannot carry one.**
The proposal's `expected_knowledge_gain` reads *"Whether the window-only bar is passable when the
loss support equals the metric support"*, and its `gate` field reads *"G1 re-based to the W1
baseline, **G2 unchanged**"*. G2 is invalidated six independent ways on the record
(`campaign/CLOSURE_STAGE1_AND_C2_STATUS.md` §1.7 gives three; `dafoam/S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md`
§1c adds three more): bar set above the loss's own ceiling; pure noise passes at 60.8% while a
strict amputation containing strictly less information passes at 53.7%; non-monotone in
localisation (D29); it scores the adjoint rather than the closure; it is objective-invariant; and
it is numerically exact, so none of the spread between published G2 values is noise. **A PASS on
an invalid gate establishes nothing and a FAIL on an invalid gate establishes nothing.** The
co-deliverable G1 does not rescue it: G1 is a bar on the training objective the optimizer directly
minimises with 21,000 free parameters, which the same record calls *"a capability verdict … not a
correctness verdict"*.

**Leg 2 — its second deliverable was declined by the only consumer named for it.** The
`expected_knowledge_gain` continues *"— and the loss-support design datum the S1-with-priors phase
needs either way"*. That phase **decided loss support without it** (`S1_PRIORS_PREREGISTRATION.md:208`,
equal-weight all cells), **gave its reason in advance of any compute**, and **explicitly recorded
that the W1 question is not consumed**. The datum has no consumer at HEAD.

Both deliverables are dead, so **every outcome of the arm leaves belief unmoved**. It must not be
proposed.

### 1.3 The refutation of the published reason — executed, and it matters

`CLOSURE_STAGE1_AND_C2_STATUS.md` §5 request #2 declines the arm on the ground that *"a window-only
loss makes the deviating set ≈ the window ≈ 8.44% < a decile, landing squarely in the threshold
degeneracy. **It would score 8.4% and FAIL by construction**"*, and
`S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md:89` carries that reason forward verbatim as *"arithmetic, not
judgement"*.

**The premise is that a restricted loss support confines the deviating β set to that support. The
one executed instance of that class on disk refutes it.** Measured on the archived arrays (arm:
run tree, `/home/ubuntu/certonomous-runs/`, outside the repo):

| field | loss support | cells with \|β−1\| > 1e-12 | as % of domain | 90th pct of \|β−1\| |
|---|---|---|---|---|
| `S1-cbfs-weighted-arm/cbfs_inv/beta_final.npy` | **W2, 2,970 of 21,000 cells = 14.14%** | **19,842** | **94.49%** | 2.555e-02 |
| `S1-cbfs-reinversion/cbfs_inv/beta_final.npy` | allCells, 21,000 | 20,142 | 95.91% | 1.216e-01 |
| `S1-cbfs-weighted-arm/cbfs_inv/beta_masked.npy` (constructed amputation, positive control) | n/a — built by masking | 2,875 | 13.69% | 7.548e-03 |

Evidence count: 3 arrays, 21,000 cells each, all read directly. **The positive control fires**: the
one field that *was* constructed by confining deviations does show a confined deviating set
(13.69%), so the measurement can see confinement when it exists. The inverted field cannot — a
14.14% support gave a 94.49% deviating set, because β outside the loss support still carries
adjoint sensitivity through the flow.

The `np.quantile(dev, 0.9)` degeneracy (`S1-cbfs-reinversion/audit_final.py:56-57`, `thr =
np.quantile(dev, 0.9); top = dev >= thr`) requires the deviating set to be **below 10%** of the
domain. Nothing on disk suggests a W1-only inversion would land there.

**The status document contradicts itself on this, and its §1.5 caveat is the half the data
supports.** §1.5 states plainly: *"this degeneracy is not what produced 26.9%. **Both real β fields
deviate in essentially every cell**, so both sit far from the threshold collapse."* §1.5's table
row 1 (1,773 cells → 8.4% FAIL) is a *synthetic* construction and is correct as such; §5's
recommendation extrapolates it to what a real inversion would produce, which §1.5 had already ruled
out four sections earlier.

**Consequence for the record, not for the verdict.** The arm stays dead. But *"FAIL by
construction"* must not be recited again, and the one-line generalisation it rests on —
`S1_PRIORS_PREREGISTRATION.md:211`, *"the weighted arm already demonstrated that localization
follows the loss support **cell-for-cell**"* — is too strong: top-decile *membership* follows the
support (42.7% in-window against 79.7% in-support, that file's `:80-82`), the *deviating set* does
not. Reported to the owners of both documents; not edited here.

---

## 1b. §1 IS NOT AN INSTANCE, IT IS A CLASS — measured

The W1-only arm's defect (a kill that never reached the surface an agent dispatches from) looked
like one stale proposal. It is not. Two more instances on the same line, then the measurement.

**Instance 2, and it is worse: `s1-whitened-reinversion-does-the-correction-move-when-sensitivity-is-divided-out.json`, 340 core-min.**
`"status": "proposed"`. It has **no `decision_note` field at all**, and a
`/usr/bin/grep -c 'D45\|D68\|enabling premise'` over the file returns **0**. Yet **D45 is a docket
row filed about this exact item**, headed *"A filed 340 core-min item's enabling premise is measured
false, and the gate it is filed to cross has a bar above its own ceiling"*, and
`S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md:86` lists it in class (c) with *"§2.1 removes the last route by
which the premise could have been rescued"*. An agent opening that JSON meets a clean, priced,
gated, `proposed` item with a fully specified launch prompt and **nothing anywhere in it saying the
premise it exists to test has been measured false.**

**Instance 3, and it has already run: `w3-qcr-forward-on-the-ducts-is-the-rank-1-route.json`, 95 core-min.**
`"status": "proposed"`, created 2026-08-05T17:35:00Z. **`closure_challenge_round5_qcr.json` names
this id as its own `"item"`** — it is the work that produced the round-5 entry of record at
0.056647, executed 2026-08-05/07, and `agenda/docket.json` carries it as `"status": "done"`,
`"closed_at": "2026-08-07T20:45:02+00:00"`. **The inbox advertises a 95 core-min item that
delivered the entry of record eight days ago.**

### The measurement

`agenda/proposals/*.json` and `agenda/docket.json` are joined on `id` and their `status` fields
compared. Both are tracked; no other arm is involved.

| quantity | value |
|---|---|
| `docket.json` records | **264** |
| proposal files | **131** |
| ids present in **both** | **75** |
| proposals with **no** docket record | **56** |
| docket records with **no** proposal file | **189** |
| **statuses that DISAGREE** | **34 of 75 = 45.3%** |

**The two directions that cost something, separated because they cost different things:**

- **`proposed` on the surface, `done` in the docket — 15 items, 463 core-min advertised as
  available for work already finished.** Largest: `fiml-adjoint-conditioning-unblock` **240**,
  `w3-qcr-forward-on-the-ducts-is-the-rank-1-route` **95**,
  `closure-baseline-error-estimator-gate` **45**.
- **`proposed` on the surface, `approved` in the docket — 10 items, 7,650 core-min that are
  dispatchable and whose surface does not say so.** Largest: `hlpw6-testcase1-coarse-grid-entry`
  **6,390**, `closure-duct-field-inversion` **420**, `dpw8-v1-oat15a-committee-grid-primal` **240**.

**Closure/S1-line subset of those two directions: 6 items, 868 core-min** —
`closure-duct-field-inversion` 420 (approved), `fiml-adjoint-conditioning-unblock` 240 (done),
`w3-qcr-forward-on-the-ducts-is-the-rank-1-route` 95 (done),
`r2-closure-coefficient-uncertainty` 60 (approved), `closure-baseline-error-estimator-gate` 45
(done), `f6a-hump-qcr-arm-on-the-challenge-run` 8 (done).

**Nobody has measured this before and nothing checks it.** `git grep` for any prior statement of a
proposal/docket status divergence returns **one** hit —
`campaign/COLD_START_TEST_2026-08-11.md:36`, which lists both surfaces as things a cold reader
should open, and is a checklist rather than a measurement. No script joins them:
`scripts/calibration_scorecard.py` and `scripts/add_proposals_supervisor_review_2026_08_07.py` read
the inbox and never open `docket.json`.

**This is D38 item (5) made concrete.** That row records that *"two live documents are both 'the
docket', definite article … they overlap on substance, and neither names the collision"*. **Here is
what the collision costs, measured: 45.3% of the overlap disagrees, and the disagreement is on the
one field that decides whether an agent starts work.** D213's W1-only arm is not a rot instance to
be repaired one file at a time; it is the visible corner of a surface that is wrong about a third to
a half of what it advertises.

---

## 2. STRAND 1 — SUBMISSION POLICY: established, with one unbacked count

**PARKED, and nothing was done.** No registration, no email, no issue, no upload, no contact.
Only files already fetched and committed were read.

### 2.1 "Five of eight have no answer in any open source" — RE-VERIFIED by execution

D31's own method, re-run today over the pinned clone
`/home/ubuntu/closure-challenge-benchmark/README.md` (116 lines, mtime 2026-07-26, the read of
record for the procedure and confirmed against Katie's 2026-08-12 live paste on every operative
sentence per `CLOSURE_SUBMISSION_REQUIREMENTS.md` §1):

| positive controls — must be > 0 | count |   | absence terms — must be 0 | count |
|---|---|---|---|---|
| `strictly forbidden` | **1** |  | `registration` | **0** |
| `anytime` | **1** |  | `deadline` | **0** |
| `authors` | **2** |  | `resubmi` | **0** |
| `rmcconke` | **7** |  | `licen` | **0** |
|  |  |  | `per team` | **0** |
|  |  |  | `entries` | **0** |
|  |  |  | `hyperparameter` | **0** |
|  |  |  | `copyright` | **0** |

Four controls fire, eight absence terms return zero over the same 116 lines with the same
instrument (`/usr/bin/grep -ic`). **The zeros are real absences, not a broken search.**
Additionally, `/usr/bin/find /home/ubuntu/closure-challenge-benchmark -maxdepth 2 -iname 'license*'
-o -iname 'copying*'` returns **no file**, corroborating D31(d)'s `license: null` locally without
any network read.

**Verdict: ESTABLISHED.** The five that remain open are (a) entries per team, (b) corrected
resubmission after scoring, (c) hyperparameter-tuning disclosure, (d) licence on submitted
predictions and code, (e) whether a company rather than named individuals may occupy the Authors
row. All five are steward questions; asking is Katie's alone and was not done.

### 2.2 "Four of them bind a first send" — MERELY ASSERTED. The four are enumerated nowhere

Executed sweep for the claim across all four arms:

- **Tracked** (`git grep -a -n -i -E 'bind (a|the) first send|binds a first send|binding a first send'` over the whole repo): **2 hits.**
  `docs/DOCKET.md:224` — D31's headline, *"and four of them are the ones that bind a first send"*, which then enumerates **(a) through (e), five of them, and never says which four**; and
  `demo-output/website/CLOSURE_SUBMISSION_REQUIREMENTS.md:123-124` — *"Five policy questions remain open (§3), **four of which D31 marks as binding a first send**"*, which cites D31 rather than enumerating.
- **Untracked + gitignored + whole working tree** (`/usr/bin/grep -rl --binary-files=text -E 'bind a first send|binds a first send' /home/ubuntu/Certonomous --exclude-dir=.git`): **1 file, `docs/DOCKET.md`** — the same row.
- **Run tree**: out of scope for prose claims; no closure-policy prose lives there.

**So the number four has never had a referent.** The one document that cites it points at the one
document that asserts it, which lists five. **Verdict: MERELY ASSERTED — the count is unbacked.**

### 2.3 The four, derived here under a stated criterion

Criterion, stated before applying it: **a question binds a first send iff its answer changes either
the CONTENT of the package or the legality/reversibility of the act of sending.** A question that
only bounds what may happen *after* the first send does not bind it.

| # | question | binds a first send? | reason |
|---|---|---|---|
| **(e)** | may a company occupy the Authors row? | **BINDS** | Step 3 of the procedure *requires* a list of all authors. The field is literally `[KATIE TO FILL]` at `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md:5` and `CLOSURE_SUBMISSION_REQUIREMENTS.md` §4.2 item 1 already calls it *"Blocking by construction"*. Content. |
| **(c)** | must hyperparameter tuning be disclosed? | **BINDS** | Determines what the DESCRIPTION_DOCUMENT must contain at the moment it is sent, and it is upstream of the single biggest identified risk — the steward's reading of the disclosed adaptive-selection history (§7 of the requirements doc). Content. |
| **(d)** | what licence do submitted predictions and code fall under? | **BINDS** | Accepted submissions are committed into a public repository the GitHub API reports as `license: null`, and the pinned clone carries no licence file. Sending disposes of rights under terms nobody has established, and it cannot be undone. Legality/irreversibility. |
| **(b)** | is a corrected resubmission permitted after scoring? | **BINDS** | Decides whether the first send is one-shot. If it is, the send must be the lab's final entry and the decision to send *now* at 0.056647 rather than after the post-send month's work is a different decision. Reversibility. |
| **(a)** | how many entries may a team make? | **DOES NOT BIND** | A first entry is entry number one. No limit that permits any entry at all can bar it. (a) bounds the number of *future* sends; it is (b) seen from the other side, and (b) is the half that reaches the first send. |

**Stated as a caveat rather than smoothed over:** under a stricter reading — *"must be answered
before the send can be physically executed"* — only **(c), (d), (e)** bind and the count is
**three**, because (b) also concerns a later send. The count of four survives only under the
reversibility limb. **Whichever reading is taken, D31's four should be written down, because a
count that is never enumerated cannot be checked and cannot be discharged one question at a time.**
Reported to D31's owner (Katie); nothing edited.

---

## 3. IDENTITY TEST (owner's rule W-2) — every gate on this line

**Rule applied:** a gate whose quantity is derivable **by construction** from its own inputs is an
identity, not a control — reportable, never gateable.

### 3.1 NEW FINDING — R5 gate clause V3 grades two fields the entry is not scored on

The round-5 entry of record shipped QCR on all three test ducts under a rule frozen before any
solve (`campaign/R5_PREREGISTRATION.md`, `R5_RULE_FREEZE.md` at `0bade54a`), with three clauses on
the benchmark's own suggested validation duct `AR_7_Ret_180`:

> V1 — QCR scaled MAE ≤ 0.70 × SST's; V2 — in-plane Pearson r ≥ 0.85; **V3 — both arms converge on
> their own `residualControl` within the cap.**

**Executed on the archived case directories (arm: run tree, outside the repo).**
`system/fvSolution:49-53` in **all five arms** — `AR_7_Ret_180_sst`, `AR_7_Ret_180_qcr`,
`AR_1_Ret_360_qcr`, `AR_3_Ret_360_qcr`, `AR_14_Ret_180_qcr` — reads, byte-for-byte identical:

```
residualControl
{
    k               5e-6;
    omega           1e-10;
}
```

**Entries for `p`, `U`, `Ux`, `Uy` or `Uz`: zero, in 5 of 5 arms.** Positive control on the same
extractor: it counts **2 of 2** (`k` and `omega`) in 5 of 5 arms, so the zeros are real absences.

**Consequence.** V3's stated quantity is decided entirely by two turbulence residuals. **V1 and V2
grade the in-plane secondary-flow velocity field.** V3 therefore cannot fail for any amount of
residual drift in the quantity the other two clauses measure, and it is not independent of them —
the only way it can fail at all is the iteration cap binding, so it carries the same one bit as
"iters < cap", which the record already prints.

**What the residual histories actually show, over all iterations, not just the last:**

| arm | iters | terminator | `Uy` init-resid | `Uz` | `p` |
|---|---|---|---|---|---|
| `AR_7_Ret_180_sst` **(the validation control; V1's denominator, one side of V2)** | 4,652 | `SIMPLE solution converged in 4652 iterations` | median **0.597**, min **0.110**, last 0.573 | median 0.516, min 0.158, last 0.285 | median 0.360, min **0.280**, last 0.334 |
| `AR_7_Ret_180_qcr` **(positive control)** | 4,660 | `SIMPLE solution converged in 4660 iterations` | median 1.83e-04, min **2.08e-05** | median 1.53e-04, min 1.99e-05 | median 4.08e-05, min **6.74e-06** |

Evidence count: 4,652 and 4,660 residual lines per field, extracted from
`log.simpleFoam` in each arm. **The instrument finds convergence where it exists** — the QCR arm
drives all three to O(1e-5) — so the SST arm's O(1) plateau is a property of that arm, not of the
reader.

**Verdict, stated no stronger than the evidence carries.** V3 is **not** an identity in the strict
sense: it can fail if the cap binds. It is a **non-discriminating clause**: one third of a
three-clause gate that carries no information about the quantity the other two grade, and it read
PASS on an arm whose graded fields never converged below O(0.1). Whether that O(1) plateau is
genuine non-convergence or the residual-normalisation degeneracy of a field that is structurally
machine-zero (`R5_PREREGISTRATION.md` §1 records SST in-plane RMS at **1.2e-15 of bulk**, the
linear-eddy-viscosity duct zero) **is not decidable from the logs — and that ambiguity is the
finding**: V3 was reported as a passed clause with no evidence either way about the graded quantity.

**Not repaired, deliberately.** R5 is frozen and §2b forbids repairing a recorded gate. This is
filed, and it is the first executed instance of the hypothesis in the already-filed 0 core-min
proposal `agenda/proposals/does-the-residual-threshold-that-declares-convergence-bound-the-graded-quantitys-remaining-drift.json`
— see §6 rank 1.

### 3.2 The rest of the line, with what is new since the last census

`CLOSURE_STAGE1_AND_C2_STATUS.md` §2.3 tabulated G1, G2, G1w, A, P1, P2 and C2's sanity check on
2026-08-11 and found **no identity among the six S1 gates**. That verdict still holds *for those
six* and is now **stale as a statement about the line**: two identities have been found on the same
line since, and neither is in the table.

| gate | identity? | status at HEAD |
|---|---|---|
| **G-P1** (λ derived, not matched) | **YES — identity.** λ_LN = λ_QoI·σ_d²/(3N·s²) is a closed form in four numbers the pre-registration supplies itself and already prints. Independently recomputed here: **8.133556871733e-06** against the published 8.1335e-06; band floor **2.033389e-06** against 2.0334e-06. Its stated failure mode cannot occur. | Filed **D76**, flag written in place at `S1_PRIORS_PREREGISTRATION.md:231-237`, gate deliberately NOT changed — the ruling is the owner's. |
| **G-P4** (plateau ratio/cos/rms to 1%) | **YES — identity, withdrawn twice.** All three legs are functions of (β, g_QoI, λ_L2); solving ε² = 1 + r² − 2rc for c returns the measured cosine to **2.2e-16**, so the third leg is the first two rearranged. A treatment reporting **the prior as the posterior** passes all three at **0.0e+00**. | Filed **D67/D75**; replaced by G-P4a (honest gradient-reproduction control) + G-P4b (three legs, negative control fires). |
| **G-P4b leg C** | **PARTIALLY** — the upper bound `s²Σλᵢ/(1+λᵢ)` is derivable from the treatment's own reported spectrum, so that side is a consistency check on its arithmetic and not evidence about nature. The lower side (strictly positive) is not derivable and is what fails the prior-as-posterior treatment. | Scored as such in the pre-registration itself. |
| **G1, G1w** | No — but both are bars on the training objective the optimizer directly minimises with 21,000 free parameters. **PASS is a capability verdict, not a correctness verdict**, and the record says so. | Unchanged. |
| **G2** | No — it can fail. **But invalid six independent ways**; see §1.2. | Unchanged; recorded verdicts stand as failures under §2b. |
| **A** (masked-β nonlocality, re-solve) | No — the only true *intervention* gate in the family: amputate, re-solve, measure effect. R_W1 0.9458 against 0.9494 full, retaining **99.6%** of the window fix. | The publishable localisation result. G2 never was. |
| **C2 sanity check** (8-case means reproduce the published overall) | **YES — identity.** The benchmark's scorer is `np.mean(list(scores.values()))`, so the overall is an unweighted mean of the per-case values by construction. | Already declared *"reportable, never gateable"*; see §4. |
| **R5 V3** | Non-discriminating; see §3.1. **NEW.** | Filed here. |

---

## 4. STRAND 3 — C2 ERROR DECOMPOSITION: a round-2 artifact whose targeting instruction is now backwards, resting on a statistic that could not have failed

### 4.1 SECOND KILL AT ZERO COMPUTE — C2's Pearson r = −0.9418 is inferentially void

C2's framing section (`closure_challenge_C2_error_decomposition.md:63-89`) argues *"the model hurts
where RANS was already good"*, tabulates the five PH-model cases by floor, and offers:

> **Clean separation with no overlap.** … Pearson r between floor and delta is **−0.9418**.
> … **Caveat stated plainly: n = 5.** A correlation of −0.94 on five points is suggestive, not
> established.

**The caveat names the wrong problem. The statistic correlates `floor` against `delta = entry −
floor`, so the floor is on both sides and the correlation is coupled by construction.**

Executed on C2's own five published pairs, host-side arithmetic, no dependency beyond `math` and
`itertools`:

| quantity | value |
|---|---|
| C2's published statistic, reproduced | **−0.9418** (Pearson), −0.9000 (Spearman) |
| **exact permutation null** — all **120** assignments of the same five entry values to the same five floors | mean **−0.9583**, range **[−0.9940, −0.9418]** |
| observed against that null | the **least negative value the null can take**; 118 of 120 permutations are at least as negative; one-sided **p = 0.983** |
| permutations returning r ≤ −0.90 | **120 of 120 = 100%** |
| **analytic independence null**, E[r(F, E−F)] = −sd(F)/√(sd(F)²+sd(E)²) | **−0.9479** — *more* negative than the value offered as evidence |
| **un-confounded statistic** r(floor, entry) | Pearson **+0.3259**, Spearman **+0.3000**, two-sided exact permutation p = **75/120 = 0.625** |
| *"clean separation with no overlap"* base rate under the same null | **102 of 120 = 85%** |

**The null is pinned. The statistic's entire achievable range under the hypothesis of no
relationship is [−0.9940, −0.9418], and the observed value sits at the harmless end of it.** No
outcome of this check could have moved belief — it is the same shape as the ρ = +0.9742 whose null
was pinned at +1.0000. Report Spearman alongside Pearson as the heavy-tailed rule requires: Spearman
is −0.9000, *less* extreme than Pearson, which is the tell that Pearson is being driven by the
coupling and by the 0.2049 leverage point rather than by rank structure. **Spearman carries whatever
claim survives, and it survives no better.**

**What is and is not killed.** The *mechanism* C2 proposes — *"when there is little to fix, a
correction can only add error"* — may well be true, and round 5's decline gate is built on it and
works. **C2 supplies no evidence for it.** And this is the check that
`CLOSURE_STAGE1_AND_C2_STATUS.md:386` marked `| Pearson r(floor, delta) = −0.9418 on n=5 |
**−0.9418** | ✓ |`: the audit verified the *arithmetic* and never asked whether the statistic could
discriminate. **That ✓ should read *arithmetically reproduced, inferentially void*.** Reported to
that document's owner; not edited.

### 4.2 C2's headline is dead at round 5, and its targeting instruction is now exactly backwards

C2 decomposes `closure_challenge_trained_entry_round2.json`. The entry of record has been superseded
twice since (round 3 → 0.0676, round 4 → 0.0654, round 5 → **0.056647191704213645**), and **C2 has
never been recomputed on round 4 or round 5.**

**Recomputed here on round 5, from `closure_challenge_round5_qcr.json`
(`round5_per_case_full` and `rans_identity_floor_per_case`, which sit side by side in that one
file):**

- **C2's headline, *"on 3 of 8 cases our correction is worse than doing nothing"*: DEAD.** At round
  5 it is **1 of 8** on the published four-decimal values. The two `alpha_05` cases now sit
  **exactly on the floor**, because the decline gate ships the organisers' own unmodified RANS
  field there — which is also why the model-earned best-on-board count is zero of eight.
- **C2's *"recoverable term is 1.7× our entire margin"* (0.0066 on the mean): EXHAUSTED.** The
  round-5 floor-relative damage is **0.000138** on the 8-case mean, a **48× reduction**, and the
  margin it was a multiple of no longer exists.

**And the successor quantity inverts C2's advice.** C2:43-44 instructs: *"Effort should target the
alpha_05 periodic-hill regime and nothing else. Chasing the NASA hump would recover at most 2% of
the available term."* Recomputing the live successor — per-case headroom to the six-entrant column
minima, `LIVE_BOARD` read by `ast.literal_eval` off its assignment node in
`sdk/scripts/probability_of_rank.py` and never imported:

| case | ours (round 5) | best other | headroom | share |
|---|---|---|---|---|
| **`NASA_2DWMH`** | 0.063198 | 0.0294 | **0.033798** | **43.6%** |
| `AR_1_Ret_360` | 0.045470 | 0.0291 | 0.016370 | 21.1% |
| `AR_14_Ret_180` | 0.035339 | 0.0250 | 0.010339 | 13.3% |
| `AR_3_Ret_360` | 0.039982 | 0.0311 | 0.008882 | 11.4% |
| `alpha_15_13929_4048` | 0.050105 | 0.0432 | 0.006905 | 8.9% |
| `alpha_15_13929_2024` | 0.101112 | 0.0998 | 0.001312 | 1.7% |
| `alpha_05_4071_4048` | 0.046108 | 0.0569 | **0** | 0.0% |
| `alpha_05_4071_2024` | 0.071863 | 0.0748 | **0** | 0.0% |
|  |  | **total** | **0.077607** |  |

**Cross-check that this derivation is sound: it independently reproduces best-on-board = 2 of 8**
(the two zero-headroom rows), matching the live figure it was not given.

**The NASA hump is the single largest remaining term at 43.6%, larger than `AR_1` + `AR_3` combined
at 32.5%. C2 tells the reader to skip it.** No surface anywhere states this — a `/usr/bin/grep` for
`43\.6` or `0\.0338` over the closure prose corpus returns nothing relevant.

**The scope of C2's existing banner, checked rather than assumed.** C2:142-154 carries a supersession
note added 2026-08-11, and it is explicit about its own reach: *"the label is the only edit made to
it"* — it covers the `ours` row of one table. **It does not reach C2:12 (the 3-of-8 headline),
:30-44 (the recoverable term and the targeting instruction), :169 or :173-187 (the deficit
attribution).** So the document is banner-ed where it was pointed at and unbanner-ed everywhere its
conclusions actually live.

### 4.3 C2's sanity check IS an identity — established, with one correction to its own wording

C2 opens: *"recomputing the 8-case means from the per-case values reproduces the published overall
figures **exactly** … The decomposition is therefore trustworthy."*

The scorer is `return np.mean(list(scores.values()))` — read at **line 17 of
`/home/ubuntu/closure-challenge-pkg/src/closure_challenge/eval.py`**. The overall is an unweighted
mean of the per-case values **by construction**, so recomputing it from those same values is
derivable from its own inputs: an **identity under W-2**, reportable, never gateable. *"Therefore
trustworthy"* does not follow. **Verdict: ESTABLISHED as an identity**, confirmed here by reading
the scorer's own line rather than by citation.

**Two things the 2026-08-11 adjudication of this point does not state, both found by executing it:**

1. **Its repo attribution is wrong.** `CLOSURE_STAGE1_AND_C2_STATUS.md` §3.2 cites *"the benchmark's
   own scorer … `closure_challenge/eval.py:17`"* and cites the benchmark clone two paragraphs later.
   That file does not exist in the clone — `/home/ubuntu/closure-challenge-benchmark/closure_challenge/eval.py`
   is absent; the scorer lives in a **separate package repo**, `/home/ubuntu/closure-challenge-pkg/`.
   The line number is right; the repository is not.
2. **The word "exactly" in C2:7 is false at full precision.** The recomputation agrees only after
   rounding: round-2 entry mean 0.0740625 against the stated 0.0741, and floor mean 0.1036375
   against 0.1036 — |diff| **3.750e-05** in both. (Round 5 does agree exactly: 0.0566471917 against
   0.056647191704213645, |diff| 0.) So the identity's one real failure channel, a transcription
   error, is only detectable above ~4e-4 on a single case. The check is blinder than the word
   "exactly" implies.

### 4.4 C2's recommendation — the fallback ran; the route C2 called "strictly better" ran and was rejected

`CLOSURE_STAGE1_AND_C2_STATUS.md` §3.5 states *"C2's recommendation was executed — and audited for
the leakage it warned about"*. **True of one of C2's two recommendations, and it is the one C2 called
the fallback.**

- **Route (a), the trust/decline gate** (C2:100-110): built and executed.
  `closure_challenge_generalization_criterion.json` records `official_test_cases_touched: false` and
  `closure_challenge_score_call_made: false`; `closure_challenge_decline_gate_audit.json` records
  `official_scoring_calls_made_by_this_script: 0` and verifies that the declined cases ship the
  benchmark's own supplied SST field (residual ~5e-10, the CSV write precision) while the applied
  cases deviate by ~12% of local velocity scale — a discriminating positive control on the audit
  itself. Chronology supports the causal claim: C2 (`b6a7d13e`…`72327806`, 2026-07-28 00:25–00:39)
  → C1 (`5719374e`, 01:01) → criterion (`df036d02`, 07-29) → round 3 gated. **VERIFIED.**
- **Route (b), the section C2 actually titles *"Recommended next action"*** (C2:266-274): *"Train a
  second, alpha_05-regime model… **This is strictly better than gating**."* **It ran too.**
  `demo-output/website/closure_challenge_alpha05_regime_model.json` states its purpose *"per C2's
  recommended next action"* and records
  `go_no_go: {"rule_i_validation_improves": true, "rule_ii_mean_loo_negative": true,
  "rule_iii_hurt_cap": false, "decision": "NO-GO"}` — it failed its own pre-registered hurt cap and
  never reached an entry.

**Verdict: §3.5 is true but materially incomplete.** The recommendation C2 called *strictly better*
ran and was rejected; only the route C2 called the fallback survives in round 5. Reported.

### 4.5 Stale board claims carried by C2 and by its audit — REPORTED, NOTHING REPAIRED

Against the live seven-position board, **Wu & Zhang is position 4 of 7, not rank 2.** All in
`demo-output/website/closure_challenge_C2_error_decomposition.md`:

| line(s) | stale text | why |
|---|---|---|
| 36 | *"Our **current** margin over the **rank-4 target (0.0779)**"* | present tense; 0.0779 is Montoya, position **7 of 7** live |
| 131-137 | the `Rank / Entry / Overall` table | a **five-position** board, undated and unlabelled; live is seven |
| 139 | *"We sit **between rank 3 and rank 4**"* | round-2 statement against the five-position board |
| 156, 175, 234, 253, 258, 264 | six *"rank 2"* / *"rank-2"* identifiers for Wu & Zhang | position 4 of 7 live |
| 158-167 | the *"best on board"* column | column minima over **four** rows; the live board has six |
| 169 | *"**We hold the best score on the entire leaderboard on three of eight cases**"* | against the live board, round 2 is **0 of 8** |
| 281 | `benchmark repo deb91557…` | legitimate as **harness** provenance, but the board table at 131-137 is drawn from that same clone and the document never says so — and a commit anchor is not an admissible board identifier |

**And the audit that cleared it carries the claim onward in its own voice.**
`CLOSURE_STAGE1_AND_C2_STATUS.md:430-434` states: *"I independently confirmed all eight 'best on
board' entries as the column minima across the four ranked rows, and confirmed the claim that the
lab holds the board best on **three of eight** cases … a genuine external referent."* Its staleness
caveat at `:442-447` names the six-row board and the new rank 1 — **and never restates the
best-on-board count**, leaving *three of eight* standing as VERIFIED against a live 2 of 8 with
**zero of 8 earned**.

**No guard sees any of this.** `scripts/self_audit.py`'s `_best_on_board_faults` derives exactly the
right numbers (best = 2, earned = 0), but its **only** caller is fed the credentials-wall string.
C2 is never opened by it. This is D151's gap on a new surface.

---

## 5. STALE-CLAIM SWEEP — one negative, and two near-misses of my own making

**Frame.** Every tracked `.md`, `.html` and `.json` under `demo-output/website/` and `docs/`
(`git ls-files`), matched for best-on-board counts of eight adjacent to a board or best-score word.
**Evidence count: 78 lines matched.** Every one was resolved by hand.

**Result: no new live stale board claim on the closure line.** The corpus is heavily and correctly
repaired: struck-and-kept with dated banners, or quoted inside audit documents reporting the
defect, or already stating the live 2 of 8 / zero of 8.

**Two candidates I nearly reported, and how each was cleared — this is the method note.**

1. `CLOSURE_CHALLENGE_STATUS.md:460`, *"Best-on-board count **5 of 8, unchanged**"*. My detector
   flagged it LIVE. It is not: the `~~` strike **opens at :458 and closes at :461**, spanning four
   lines, and a line-wise detector cannot see a multi-line span. `OWNERSHIP_BOUNDARY_SWEEP_2026-08-15.md:254`
   had already adjudicated it as **correct dated history** inside §0e.
2. `agenda/docket.json:4442`, an outcome field asserting *"the item's title claim is measured true:
   RANK 1 of 5 scored locally at benchmark commit deb91557 … margin 0.002878"*. Flagged LIVE. It is
   not: **`:4441` carries a sibling key `outcome_denominator_superseded_2026_08_15`** placed
   immediately above it, exactly the treatment D175 applied — the dated block is left byte-identical
   on purpose, because a dated record overwritten is a dated record made false of its own date.

**The transferable point.** A line-wise strike detector manufactures stale-claim reports on a
corpus that uses multi-line strike spans and JSON sibling keys, and both false positives here
pointed at the *correctly repaired* surfaces. Any future denominator sweep needs a strike masker
that spans lines and a JSON reader that looks at neighbouring keys, or it will spend its budget
re-reporting repairs.

---

## 6. PRICED COMPUTE — ranked, each with its discriminating outcome

**Nothing below was run. Compute authorisation is Katie's and has not been given.**

### Rank 1 — **0 core-min, already filed, currently unranked anywhere. BUY FIRST (it is free).**

`agenda/proposals/does-the-residual-threshold-that-declares-convergence-bound-the-graded-quantitys-remaining-drift.json`
— *"Test on this lab's own archived run histories whether the residual level at which a run is
declared converged bounds the graded quantity's remaining drift."* **§3.1 above is its first
executed instance, and it fired on the entry of record's own validation control.**

**Discriminating outcome.** Sweep every archived case's `residualControl` block against the fields
its record grades, over the 132,049-file run tree. *If a majority of graded runs declare convergence
on fields they do not grade*, the lab's convergence claims need re-stating class-wide and a standing
rule follows (`residualControl` must list every graded field). *If it is only the R5 ducts*, it is
one gate's defect and §3.1 is the whole of it. **Belief moves either way, and the cost is zero.**

### Rank 2 — **`w3-beta-on-omega-destruction-model-patch`. PRICED HERE FOR THE FIRST TIME AT ~425+ core-min. DO NOT BUY YET — and the reason it is wanted is weaker than the record states.**

The record calls it *"the **only** route to an external referent for the S1 line"*
(`CLOSURE_STAGE1_AND_C2_STATUS.md` §2.5 item 2, §5 row 3; `S1_ZEROCOMPUTE_TRIAGE` §1b), where it is
carried **unpriced**. Confirmed still unrun: `/usr/bin/find /home/ubuntu/certonomous-runs -iname
'*destruction*'` returns **zero results across the whole 132,049-file tree**.

**Price, derived from disk rather than estimated.** The inversion itself is the same case, the same
mesh, the same 21,000 design variables and the same solver build as the equal-weight reinversion,
which billed **424.80 core-min** for 16 evaluations at ~20 core-min/evaluation
(`S1-cbfs-reinversion/ledger.csv`, 36 lines summed to the cent). So **≥425 core-min for the
inversion alone**, plus an unmeasured model-patch, rebuild and FD-verification block that nothing on
disk prices — the honest figure is **425 core-min + an unbounded build term**, which is why it must
be respecified before it is bought.

**The discriminating outcome is weaker than the record claims, and this is the finding.** Term
parity with Wu/Zhang buys comparability *of method*. It does **not** buy an external referent on the
*field*, because — by the same document's §2.5 item 1 — *"There is no published β field, no
independent implementation, and no benchmark distribution anywhere in the chain."* **Recommendation:
before this is priced into any queue, someone must establish at zero compute whether a comparable
published destruction-term β field or its per-case scores exist at all.** If they do not, the item's
stated justification does not hold and its price should not be paid for that reason.

### Rank 3 — **`NASA_2DWMH`, the hump. The one experiment on this line whose outcome can move the standing. COST UNKNOWN — nothing on disk prices it, and that is the first thing to fix.**

**Why it is the top scientific target and why nobody has said so.** §4.2 derives it: the hump is
**43.6%** of all remaining headroom (0.033798 of 0.077607), larger than `AR_1` + `AR_3` combined
(32.5%), and it is our worst row on the whole board (0.063198 against a best-other 0.0294). It is
also the case whose removal the record says raises P(rank 1) to **78.5%** — so it is simultaneously
the largest recoverable term *and* the load-bearing case for the rank claim. **C2:43-44 explicitly
tells the reader not to chase it**, on a calculation that was true of round 2 and is not true now.

**Discriminating outcome, stated as a threshold rather than a hope.** The 8-case overall is an
unweighted mean, so a per-case gain `g` moves the overall by `g/8`.
- Closing **57.3%** of the hump headroom (0.019352 of 0.033798) moves the overall by **0.002419** —
  exactly the seed bound, i.e. it would put the lead outside the one term currently able to reverse
  it. **That result changes what the lab may claim about rank 1.**
- Closing **32.3%** (0.010920) moves the overall by **0.001365**, the Yang margin: it doubles the
  lead but stays inside the seed bound, so **P(rank 1) moves and the rank claim does not become
  safe.**
- Anything below ~0.0109 on the case is inside the seed noise the standing is already measured
  against and **decides nothing.** A proposal that cannot pre-state which side of 0.0109 it expects
  to land should not be bought.

**Cost: UNKNOWN, and the reason is stated rather than a number invented.** A sweep of the tracked
closure JSONs and `demo-output/website/closure_challenge_C6_hump_decision.md` finds **no priced
request for a hump attempt anywhere**. Evidence count for a price: **zero** → UNKNOWN, not "cheap".
**The zero-compute step that must precede any purchase is pricing it**, and the arithmetic above is
the acceptance threshold to pre-register against.

### Rank 4 — **DECLINED, and named because identifying a non-discriminating experiment is itself the deliverable: re-solving the AR_7 SST validation control with `residualControl` extended to `p` and `U`, ~10–20 core-min.**

This is the obvious experiment §3.1 invites and it **must not be proposed.** Arithmetic, done before
proposing rather than after: V1 passed at a ratio of **0.4770 against a 0.70 bar**, so SST's scaled
MAE would have to fall by **32%** for the verdict to move. SST's in-plane RMS is **1.2e-15 of bulk**
— the structural duct zero of the linear eddy-viscosity class — so its MAE against the LES is
bounded below by essentially the whole LES secondary-flow magnitude and cannot fall at all, however
long the solve runs. **V1's verdict cannot flip, V2's correlation is computed against the same
structurally-zero field, and V3's own clause is the thing under suspicion. Every outcome leaves
belief unmoved.** Declined.

### Not proposed, and named so nobody re-proposes them

- **`s1-cbfs-w1-only-arm`, 150 core-min** — killed in §1, on two legs neither of which is the reason
  currently on its dispatch surface.
- **Re-running C2's floor-relative decomposition on round 5 as an *investigation*, 0 core-min but
  not free of attention.** Already done in §4.2: the recoverable term is **0.000138** on the mean,
  ~10% of the Yang margin and ~6% of the seed bound. **Every outcome is below the noise the board
  is already measured against.** It belongs in a supersession note on C2, not in the queue.
- **C2's own cost line, `| Compute cost | none — 0 core-min |` (C2:283), is honest about C2 and
  misleading about C2's consequences.** The duct work C2's targeting pointed at billed **37.0
  measured core-min** (`closure_challenge_round5_qcr.json`,
  `cost.solver_core_min_total_measured`, against a 95 core-min budget — AR_7 SST 5.4 + AR_7 QCR 5.1
  + AR_1 0.2 + AR_3 1.4 + **AR_14 24.8**), plus **2.1 core-min** for the alpha_05 regime model that
  scored NO-GO. **A targeting document whose cost line reads zero hides the price of the thing it
  targets** — and `CLOSURE_STAGE1_AND_C2_STATUS.md` §5, the one section built to price this family,
  contains **no C2 row at all**. Reported.

---

## 7. Per-strand verdicts

| strand | verdict | what carries it |
|---|---|---|
| **Submission policy** — "five of eight unanswerable in any open source" | **ESTABLISHED** | §2.1: four positive controls fire, eight absence terms return zero over the same 116 lines with the same instrument; no licence file in the pinned clone. |
| **Submission policy** — "four of the five bind a first send" | **MERELY ASSERTED** | §2.2: two occurrences in the entire corpus across all four arms, one citing the other, and the source enumerates five and names none of the four. §2.3 derives the four under a stated criterion and names (a) as the one that does not bind. |
| **Submission policy** — package readiness | **ESTABLISHED, and unchanged since 2026-08-12** | The `test/` subdirectory is structurally clean; the two blocking gaps are `[KATIE TO FILL]` in Authors and Reference URL. Not re-executed here; nothing has touched the package since. |
| **Stage 1 FIML** — what ran | **ESTABLISHED** | Three billed items, 335.98 / 424.80 / 267.07 core-min, reproduced from `ledger.csv` to the cent; all three budget-capped, none converged. Nothing anywhere in the 132,049-file run tree is newer than **2026-08-10 19:30**; newest S1 file is **2026-08-08 22:55**. |
| **Stage 1 FIML** — blocked on what | **ESTABLISHED: a decision, not compute** | The 260 core-min priors item is blocked on (i) Katie's send decision opening the post-send month, (ii) compute authorisation, (iii) two W-2 identity rulings reserved to the owner (G-P1/D76, D66). Stage 2 has never run. |
| **Stage 1 FIML** — §2.3's "no identity on the S1 line" | **STALE, reported not repaired** | Two identities found since: G-P1 (D76) and G-P4 (D67/D75). §3.2. |
| **Stage 1 FIML** — the 260 core-min hold | **HALF-DISCHARGED, and nothing records it** | The triage's release condition is *"hold until G-P4 is replaced **and G-P2 re-derived (D69)"*. G-P4 was replaced at `760e7321`. `/usr/bin/grep -n "D69" S1_PRIORS_PREREGISTRATION.md` returns **zero hits**, and its §4a affirms *"What did not [change]: every other gate."* Two docket rows about G-P2 point opposite ways (D76 calls it sound because it bars on a count; D69 objects that the count's stated mechanism is the wrong comparison) with the item still on hold. |
| **C2 decomposition** — what it decomposes | **ESTABLISHED: a round-2-only artifact** | §4.2. Never recomputed on round 4 or round 5. Its 3-of-8 headline is **1 of 8** at round 5; its 0.0066 recoverable term is **0.000138**, a 48× reduction. |
| **C2 decomposition** — its central statistic (r = −0.9418) | **REFUTED as evidence** | §4.1. Exact permutation null over all 120 pairings runs [−0.9940, −0.9418], mean −0.9583; observed is the least-negative value the null can take, one-sided p = 0.983, 100% of permutations ≤ −0.90. Un-confounded r = +0.3259, Spearman +0.3000, p = 0.625. |
| **C2 decomposition** — its targeting instruction | **REFUTED against the live board** | §4.2. C2 says target `alpha_05` *"and nothing else"* and skip the hump as *"at most 2%"*. Live: the hump is **43.6%** of remaining headroom, larger than AR_1 + AR_3 combined (32.5%). The derivation independently reproduces best-on-board = 2 of 8. |
| **C2 decomposition** — its sanity check | **ESTABLISHED as an identity** | §4.3, read off the scorer's own line, `np.mean(list(scores.values()))` at `/home/ubuntu/closure-challenge-pkg/src/closure_challenge/eval.py:17`. Two corrections attached: the prior adjudication's repo attribution is wrong, and C2's word *"exactly"* is false at full precision (|diff| 3.750e-05 on both round-2 means). |
| **C2 decomposition** — "its recommendation was executed" | **PARTIALLY ESTABLISHED, with a named omission** | §4.4. True of the route C2 called the **fallback**. The route C2 titles *"Recommended next action"* and calls *"strictly better than gating"* also ran — `closure_challenge_alpha05_regime_model.json` records `decision: "NO-GO"` on its own pre-registered hurt cap. |
| **C2 decomposition** — board claims | **NINE STALE, reported not repaired** | §4.5, plus the audit at `CLOSURE_STAGE1_AND_C2_STATUS.md:430-434` endorsing *"three of eight"* in its own voice with a staleness caveat that never restates the count. No guard opens C2. |
| **R5 gate clause V3** | **REFUTED as a control** | §3.1. Zero `p`/`U` entries in `residualControl` in 5 of 5 arms with a 2-of-2 positive control; the graded fields in the validation control never fall below O(0.1) across 4,652 iterations. |
| **"W1-only arm fails by construction at 8.4%"** | **REFUTED** | §1.3. A 14.14%-support loss produced a 94.49%-deviating field; the degeneracy needs below 10%. The arm dies anyway, on §1.2. |

---

## 8. What this document does NOT establish

- **It does not decide whether the SST validation control's O(1) `Uy`/`Uz`/`p` plateau is genuine
  non-convergence.** It establishes that V3 carries no evidence either way, which is the claim made.
- **It does not re-derive the live board.** Every board figure is quoted from the retrieval of
  2026-08-11T23:33Z re-verified 2026-08-14T21:01Z, with no fetch.
- **It does not re-run the submission-package conformance checks** of 2026-08-12; it establishes
  that nothing has touched the package since.
- **It repairs nothing.** Every stale or mislabelled item found here belongs to another owner's
  document and is reported.
- **It does not overturn C2's mechanism.** *"When there is little to fix, a correction can only add
  error"* may be true; round 5's decline gate is built on it and works. What §4.1 establishes is
  that C2's correlation is not evidence for it — the hypothesis is untested, not refuted.
- **It does not price the NASA hump.** It establishes that nothing on disk prices it and states the
  threshold any attempt must be pre-registered against.
- **It does not re-derive C2's round-2 arithmetic.** That was reproduced independently on
  2026-08-11 and the reproduction is SELF-REFERENTIAL by its own label (independent implementation,
  same JSON). What is re-derived here is the *round-5* decomposition and the *live* headroom, both
  from primary artifacts.

## 8b. Referent labels for this document's own verdicts (§6a)

- **§1 (the W1-only kill):** EXTERNAL to the item under test — the arm is killed by the state of
  its own consumer and by an archived field it did not produce, not by re-running its own gate.
- **§1.3 (the refutation):** SELF-REFERENTIAL — the lab's own archived β arrays, my arithmetic.
  The positive control (`beta_masked.npy`, a field built by confining deviations) demonstrates the
  measurement can return the confined answer.
- **§2 (policy):** EXTERNAL — the benchmark's own primary sources, with positive controls; five
  points explicitly SOURCE UNAVAILABLE.
- **§3.1 (V3):** SELF-REFERENTIAL on the numbers, EXTERNAL to the gate under test — V3 is falsified
  by its own case's `fvSolution` and by residual histories the gate never reads.
- **§4.1 (the correlation kill):** EXTERNAL to the statistic under test — the null is constructed
  from the same five values by permutation, so it cannot be accused of importing anything.
- **§4.2 (headroom):** EXTERNAL — the benchmark repository's own published table, via `LIVE_BOARD`.
  Cross-checked by independently reproducing best-on-board = 2 of 8.
- **§5 (stale sweep):** SELF-REFERENTIAL — the lab's own corpus, read with my own instrument, whose
  two defects are named.

## 9. Reproduction

```
python3 -c "import numpy as np; b=np.load('/home/ubuntu/certonomous-runs/S1-cbfs-weighted-arm/cbfs_inv/beta_final.npy'); d=abs(b-1); print((d>1e-12).sum(), b.size, np.quantile(d,0.9))"
/usr/bin/grep -c -E '^\s*(p|U[xyz]?)\s' <(sed -n '/residualControl/,/}/p' /home/ubuntu/certonomous-runs/w3-qcr-rank1/AR_7_Ret_180_sst/system/fvSolution)
/usr/bin/grep -oE 'Solving for Uy, Initial residual = [0-9.eE+-]+' /home/ubuntu/certonomous-runs/w3-qcr-rank1/AR_7_Ret_180_sst/log.simpleFoam | wc -l
for t in 'strictly forbidden' registration licen 'per team'; do /usr/bin/grep -ic "$t" /home/ubuntu/closure-challenge-benchmark/README.md; done
git grep -a -n -i -E 'bind (a|the) first send|binds a first send|binding a first send'
```

C2's permutation null, in full — floors and deltas are C2's own five published pairs (C2:66-72):

```python
import itertools, math
floor = [0.0461, 0.0621, 0.0719, 0.1320, 0.2049]
delta = [0.0262, 0.0011, 0.0255, -0.0819, -0.1038]
entry = [f + d for f, d in zip(floor, delta)]
def pear(a, b):
    n = len(a); ma = sum(a)/n; mb = sum(b)/n
    ca = [x-ma for x in a]; cb = [y-mb for y in b]
    return sum(x*y for x, y in zip(ca, cb)) / math.sqrt(
        sum(x*x for x in ca) * sum(y*y for y in cb))
nulls = sorted(pear(floor, [e-f for e, f in zip(p, floor)])
               for p in itertools.permutations(entry))
print(pear(floor, delta), nulls[0], nulls[-1], sum(nulls)/len(nulls))
print(pear(floor, entry))   # the un-confounded statistic
```

The live headroom table, `LIVE_BOARD` read without importing the module:

```python
import ast, json
J = json.load(open('demo-output/website/closure_challenge_round5_qcr.json'))
ours = J['official_test_harness_result']['round5_per_case_full']
LB = next(ast.literal_eval(n.value)
          for n in ast.walk(ast.parse(open('sdk/scripts/probability_of_rank.py').read()))
          if isinstance(n, ast.Assign)
          and any(getattr(t, 'id', '') == 'LIVE_BOARD' for t in n.targets))
for i, c in enumerate(ours):
    print(c, ours[c], min(v[i] for v in LB['entrants'].values()))
```

## 10. Docket rows filed

- **D213** — the released 150 core-min arm whose dispatch surface never learned it was killed, and
  the published reason for the kill refuted by execution.
- **D214** — R5 gate clause V3 grades `k` and `omega`; the entry is scored on in-plane velocity.
- **D215** — C2's central statistic could not have failed, its targeting instruction is now
  backwards, and the audit that cleared it verified the arithmetic instead.
- **D216** — "four of the five policy questions bind a first send" is enumerated nowhere in any arm.
  Owner: Katie.
- **D218** — the two surfaces that both call themselves the docket disagree on 45.3% of what they
  share, and the disagreement is on the field that dispatches work. §1b. This is the class D213 is
  an instance of.

**Allocation notes, because the hazard fired three times in one hour and each time differently.**
Rows 1–4 were drafted as D212–D215; the free-ID assertion, run **inside** the write rather than
before it, refused D212 — another agent had appended it to the working tree, uncommitted, between
drafting and writing. The fifth row was drafted as D217 and the same assertion refused it, because a
second agent had committed D217 in the intervening two minutes. **Neither gap is reused and nothing
was renumbered.** Both writes also asserted, before touching the file, that they contained **no
`<s>` or `</s>` tag**: `docs/DOCKET.md` carries **nine opening strike tags against three closing
ones**, so a balanced pair inside a new row closes the nearest dangling opener above it and blanks
another author's claim. Verified both times: opener/closer counts **9/3 before and 9/3 after**, and
the pre-existing bytes byte-identical.

**And a third thing happened that is worth recording rather than tidying away.** D213–D216 were
written into the shared working tree and then **swept into another session's commit** (`c75f6198`)
before this session committed them. Nothing was lost and the rows are at HEAD — but they travel
under a commit message about a mutation harness, and this is precisely the defect that session's own
D212 describes in its remedy column (*"this pass's own docket commit captured another agent's
row"*). **It is the fourth instance of the same mechanism in one evening, and it happened to the row
that was written after the row that named it.** The transferable point is not "be careful": a
shared, append-only, single-file docket under a live fleet has no way for two authors to commit
disjoint appends, and every mitigation so far has been an instruction rather than a mechanism.

## 11. Findings reported to other owners and NOT repaired here

| finding | surface | owner |
|---|---|---|
| *"FAIL by construction"* as the W1-only arm's reason | `CLOSURE_STAGE1_AND_C2_STATUS.md` §5 #2; `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md:89` | those documents' owners |
| *"localization follows the loss support cell-for-cell"* | `S1_PRIORS_PREREGISTRATION.md:211` | that file's owner |
| §2.3's *"no identity on the S1 line"*, now stale — G-P1 (D76) and G-P4 (D67/D75) are both identities found since | `CLOSURE_STAGE1_AND_C2_STATUS.md` §2.3 | that document's owner |
| the 260 core-min hold's release condition is half-discharged: G-P4 replaced, **G-P2 not re-derived**, and `grep -n "D69" S1_PRIORS_PREREGISTRATION.md` returns **zero hits** while its §4a affirms *"every other gate"* unchanged | `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` §3 / `S1_PRIORS_PREREGISTRATION.md` §4a | chief; that file's owner |
| the ✓ on a statistic whose null is pinned | `CLOSURE_STAGE1_AND_C2_STATUS.md:386` | that document's owner |
| *"three of eight"* endorsed in the audit's own voice, with a staleness caveat that never restates the count | `CLOSURE_STAGE1_AND_C2_STATUS.md:430-434`, `:442-447` | that document's owner |
| `eval.py:17` attributed to the benchmark clone; it lives in `/home/ubuntu/closure-challenge-pkg/` | `CLOSURE_STAGE1_AND_C2_STATUS.md` §3.2 | that document's owner |
| nine stale board ordinals and counts, and a banner that covers one table row | `closure_challenge_C2_error_decomposition.md` | that document's owner |
| *"exactly"* at full precision (|diff| 3.750e-05) | `closure_challenge_C2_error_decomposition.md:7` | same |
| a cost line of `0 core-min` on the document that set the targeting for 37.0 measured core-min of duct work plus 2.1 for a NO-GO arm | `closure_challenge_C2_error_decomposition.md:283`; and §5 of the status doc has no C2 row at all | same; chief |

## Related

- `demo-output/website/campaign/CLOSURE_STAGE1_AND_C2_STATUS.md` (2026-08-11) — the record this
  document re-establishes against HEAD.
- `demo-output/website/dafoam/S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` — the prior zero-compute triage.
- `demo-output/website/CLOSURE_SUBMISSION_REQUIREMENTS.md` (2026-08-12) — the readiness measurement.
- `demo-output/website/closure_challenge_C2_error_decomposition.md` — the round-2 decomposition.
- `demo-output/website/campaign/R5_PREREGISTRATION.md`, `R5_RULE_FREEZE.md` — the frozen round-5 rule.
