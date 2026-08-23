# DOCKET_DRAFT — D-14, the late COVERAGE.md delivery, and the FS5 clip defect

> **FILED — DO NOT APPEND AGAIN.** These two rows were committed to
> `docs/DOCKET.md` as **D475** and **D476**, the numbers taken from the tail
> (D474) at commit time and asserted as max+1 by `scripts/append_record.py`.
>
> **They were BLOCKED for about an hour first, and the blocker is kept below
> rather than deleted**, because the record of why a row could not land is worth
> more than a tidy file: `docs/DOCKET.md` refused twice, neither refusal was
> this lane's to clear, and both cleared on their own when a peer landed and
> renumbered their in-flight tail (`fe065ca6`, board correction `504f25ae` — the
> curriculum row is **D474**, not D471). `scripts/check_docket_reconciliation.py`
> then returned **PASS**: no duplicate ids, no worktree-only rows. The
> **`D468` duplicate in `HEAD`** described below was part of the same in-flight
> repair and is likewise resolved.
>
> This file is the durable draft (`CLAUDE.md` rule 13: a draft another agent
> must read lives under the case directory it belongs to, never in a
> scratchpad). The sibling `DOCKET_DRAFT.md` is stamped FILED and was **not**
> appended to.

**Rows owed to:** the `RESULTS.md` §12 addendum (D-14), `COVERAGE.md`, and
`docs/closure/R5_CONSTRAINTS_DISCHARGE_RECORD.md`, all committed 2026-08-23 at
`918e8fe7` and `9f0210dd`.

---

## Why these rows are not in `docs/DOCKET.md`

`scripts/append_record.py` **REFUSED**, twice, for two independent reasons.
Both were reproduced with `--dry-run`; nothing was written and nothing was
reverted (`ESCALATION_CHARTER.md` §3 — an unexpected change is inspected, never
reverted).

**1. The prefix test fails: the worktree disagrees with HEAD inside HEAD's own
bytes.**

```
REFUSED: the worktree disagrees with the committed blob inside the committed
blob's own bytes, first at byte 1767972 of 1769934
```

Inspected, not reverted: the difference is a **peer's in-place renumber of
their own row**, disclosed in the row itself — *"[id corrected 2026-08-23, same
day: appended as D468 in commit `450735c1` while a peer's unlanded D468–D470
tail (F14 VERIFY sweep) was preserved ahead of it by the append_record merge
and landed in the same commit; per check_docket_reconciliation's rule the later
writer takes the next free id. Content unchanged.]"* That is legitimate repair
work in flight. It is simply not an *append*, so the merge helper stops rather
than guessing whose edit it is — which is the helper working as designed
(D369's repair).

**2. Even if it merged, the only id it will accept is already taken.** The
helper asserts the first appended id is max+1 **in HEAD's blob**, and HEAD's
maximum is `D470`, so it demands `D471`:

```
REFUSED: first appended id 'D474' is not max+1 (D471) for its series in HEAD:docs/DOCKET.md
  series 'D': maximum existing number in the committed blob = 470
```

But the worktree already holds **`D471` twice**, unlanded, along with `D472` and
`D473` (`scripts/check_docket_reconciliation.py`, run before touching the file
as `CLAUDE.md` rule 11 requires: *"IN THE WORKTREE, NOT IN HEAD (3): D471, D472,
D473"*, and *"DUPLICATE IDS IN THE WORKTREE (1): D471"*). Appending a **third**
`D471` is exactly the collision that check exists to prevent, and its own ruling
is that **renumbering another agent's row is that agent's call — ASK, never
renumber for them.**

**Also on record and not this lane's to fix:** `HEAD` itself carries a duplicate
**`D468`** (two rows wearing one name — the K0cQ planted-control row and the
expertise-curriculum row). The docket is append-only, so per the check *"the
ambiguity does not expire"*. The peer's renumber above is the in-flight fix.

**A defect shape worth the supervisor's eye, reported and not filed as a
lesson.** The two refusals interact: `append_record.py` **preserves the
worktree tail ahead of the appended rows**, so a peer's unlanded row lands in
*your* commit — while its id assertion reads **HEAD only**, by explicit design
(*"Not from the worktree, which may carry a peer's unlanded row"*). When the
peer's tail happens to hold the very next id, those two rules produce a
duplicate inside the file the helper itself writes. **That is precisely what
happened to the peer above today** — their own correction note names the
mechanism verbatim. It is the third bite of the D369 family (D369, D461/D-13,
this). Whether it earns an assert at the call site, per the standing rule that a
twice-bitten defect class gets an assert rather than a paragraph, is the
supervisor's call and not this lane's.

## What must happen before these rows land

1. The peer lands or abandons the unlanded `D471`–`D473` tail, and resolves the
   in-worktree `D471` duplicate.
2. `scripts/check_docket_reconciliation.py` returns without a duplicate and
   without a worktree-only set.
3. The ids below are re-derived **at commit time, in the same shell
   invocation**, from the maximum existing number — never a count, never a
   number remembered from this file (`CLAUDE.md` rule 11). At the time of
   writing the maximum across `HEAD` and the worktree is **`D473`**, so the
   next free pair is **`D474` / `D475`** — *stated as the reading of the moment,
   not as an assignment.*

---

## Row 1 — of two, filed as D475

| D&lt;n&gt; | **A REGISTERED DELIVERABLE WAS NEVER DELIVERED, THE NON-DELIVERY WENT UNDISCLOSED THROUGH THIRTEEN DEPARTURES, AND IT SHIPPED A DAY LATE.** R4's frozen `PREREGISTRATION.md` §7 (sha256 `058444…cbbe8`, never edited) registered `COVERAGE.md` to ship with `MODEL.md`, and Addendum A1 confined its own consequence to that file. **It was never written.** The strings `FS5` and `coverage` appear **zero times** in the 1,313-line `RESULTS.md` (control: `FS2` appears six times under the same grep); **none of departures D-1…D-13** discloses it — D-13 sits at line 1010 at the foot of §10, not in §9 — and it is not among §7's ten "cannot see" bullets, a section that does record the unrun `b^Δ` static-injection arm, the absent shelf-D band and the missing realisability threshold. Found 2026-08-23 by the R5 discharge-record lane tracing the R5 rung's `Re_y` constraint; **verified personally by the closure supervisor** the same day. Disclosed as **departure D-14** in a dated addendum at `RESULTS.md` §12 (version 1.0 → 1.1, *lines whose number changed above this section: 0*, v1.0 blob `90457f4f` verified byte-identical after appending). **Supervisor's ruling, quoted:** *"FS5's per-build discharge for R4 WAS NOT MET — the standing gate re-arms. The late delivery discharges the deliverable, not the disclosure duty, which stays on record as breached."* **The deliverable now exists**, computed on the **realised 12-case** training set and the **frozen** fields the regression actually fitted (not the baseline RANS fields the FS1/FS2 library is built on): the selected tensor set `{T1,T2,T3}` is **rank 3 in 172,106 of 172,106 fitted cells**, at a pooled per-cell `σ1/σ3` of **20.81 / 1.634e+04 / 4.430e+07** (p50/p99/max, ducts p99 **5.113e+04**) — the half that must never be quoted without the rank; leave-one-family-out coverage on the six selected columns loses only **0.0011 % / 0.0905 % / 0.0000 % / 0.2238 %** of held-out cells (hills / ducts / `PHLL10595` / `CBFS13700`), **so R4's GATE FAIL was not a training-set coverage failure** — one candidate explanation removed, none established; and its independent reproduction of the fit mask returns **172,106 of 172,171, 65 dropped, all hills**, matching `RESULTS.md` §3.3. **Recorded as not delivered rather than approximated:** FS5's *"declared factor"* (`CLOSURE_LINE_RESTART_DOCTRINE.md`:252, `CLOSURE_MODELLING_CHARTER.md`:822/:827) **has never been declared by any build — stated three times, met zero times** — and `COVERAGE.md` refuses to invent one post-hoc (rule 2); the per-component reading of "every selected term" (27 columns) is uncomputed; the ranges inherit D-1's biased 12-of-27 sample. **A second correction of record in the same addendum, moving no verdict:** `RESULTS.md`:678–679 and :1128 state the frozen-field ceiling recovers the duct secondary vortex "to **0.4–0.6 %** of the DNS value"; the same table divides to **0.6126 / 0.3878 / 0.3283 / 0.0899 %** — range **0.09–0.61 %**, wrong for three of four aspect ratios, **error in the ceiling's favour**. No verdict moves: gate **G5 carries no registered bar** (the same defect §11.7 item 1 records for G4 and did not say of G5), and the **GATE FAIL** rests on G1 and G2. **R4 remains CLOSED at GATE FAIL; `PREREGISTRATION.md` is untouched and re-verified at `058444…cbbe8`; `MODEL.md`'s FS4 freeze is final; no solver ran.** Compute for the delivery: **30.6 core-seconds**, numpy reads only, against a 0.1 core-h cap. `cases/RANS_LES_closure_models/R4_sparta_build/COVERAGE.md`, `…/RESULTS.md` §12, `docs/closure/R5_CONSTRAINTS_DISCHARGE_RECORD.md`; commits `918e8fe7`, `9f0210dd`. |

## Row 2 — of two, filed as D476

| D&lt;n&gt; | **THE FS5 COVERAGE INSTRUMENT IS BLIND ABOVE A CLIP, ON THE EXACT AXIS THAT NAMED THE `Re_y` CONSTRAINT — REPAIR DECISION OWED BEFORE THE NEXT BUILD.** The FS1 library defines its wall-distance Reynolds number as **`q1_wallRe = min(sqrt(k) d / (50 nu), 2)`** (`_common/features/FEATURE_LIBRARY.md:178`; `:174` before `01430485`), and it **saturates**: over the 40-case, 641,652-cell library the pooled statistics are `max = 2.0`, `p99 = 2.0`, **`p50 = 2.0`** — more than half of all cells sit exactly on the bound (`/home/ubuntu/closure-data/features/fs2_audit.json`, key `per_feature`). An FS5 test-vs-training range check on that column therefore **cannot report an above-maximum excursion for any test cell**, because the training maximum **is** the clip; only below-minimum excursions remain visible. **This is the axis the R5 rung's second constraint is named after**: the round-5 diagnostic measured the trap on the **unclipped** `sqrt(k) d/(50 nu)` at **1.85× and 2.07×** its trained maximum on the two ducts the entry was losing, against 0.90× on the one it won (`research/closure/md/CLOSURE_CHALLENGE_STATUS.md`:418–423), and **the FS5 sweep as built would not have seen it.** Bounded by construction is not bounded by the data, and a coverage instrument reports the second while a clip supplies the first. **No R4 number is affected** — `q1_wallRe` is not among `MODEL.md`'s selected features — and this is filed as an **instrument** defect, not a result. **Unmeasured, and stated as such:** whether the library's other bounded features (the Wu/Kaandorp `q = q_raw/(|q_raw|+|q_norm|)` block, bounded in `[-1,1]`) also saturate on training data; saturation, not boundedness, is what destroys visibility, and only `q1_wallRe` was measured. **Owed before the next build's FS5 discharge:** a decision between an unclipped companion column and a declared exemption for clipped features — **neither is taken here**, and neither is a threshold this lane may set. Recorded as `N-B38`. `cases/RANS_LES_closure_models/R4_sparta_build/COVERAGE.md` §6; `docs/closure/R5_CONSTRAINTS_DISCHARGE_RECORD.md` §3.3. |
