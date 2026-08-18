# W5 SpaRTA escalations — the gate both items demand was met three days before they were worked

Date: 2026-08-04 (UTC). Docket items: `w5-sparta-frozen-rans-is-the-unblock`
(created 2026-07-31 16:57Z) and `w5-sparta-is-still-the-cheapest-real-result`
(created 2026-07-31 18:18Z), both approved 2026-07-31 22:18Z, both flagged
unclaimed for two passes, both claimed this session per
`w7-claim-an-item-before-working-it` before any work was done. **No solver was
launched under either item, and that is the finding, not a shortfall.**

## The gate, and where it was already met

Both items carry the identical gate:

> Reproduce the published correction-field result on the backward-facing step
> before any cross-validation budget is committed.

The backward-facing step is CBFS13700 (Schmelzer, Dwight & Cinnella 2020,
Table 1 — the curved backward-facing step, a benchmark **training** case). That
reproduction ran on **2026-08-01** under `w2-sparta-frozen-rans-cbfs` (created
2026-07-31 14:52Z — two hours *before* the first of these escalations was
filed) and is recorded in `W2_SPARTA_FROZEN_CBFS.md`:

| Gate clause | Status | Evidence |
| --- | --- | --- |
| CBFS correction-field result reproduced | **MET** — `eps(U)/eps(U_0)` = 0.39753 (primary pre-registered convention; 0.27634 volume-weighted) against the published 0.22703, inside the binding factor-two band [0.1135, 0.4541] and far below the 1.0 hard floor | `W2_SPARTA_FROZEN_CBFS.md` §6, `W2_sparta_runs/cbfs_prop/` |
| No adjoint formed (the premise both rationales lean on) | **CONFIRMED** — the frozen solve is a passive omega equation; extraction settled in 295 iterations, 6.2 s CPU on CBFS, 18 s for both training cases combined. The DIVERGED_NANORINF adjoint blocker never comes near this rung | `W2_SPARTA_FROZEN_CBFS.md` §3 |
| No cross-validation budget committed before the gate | **HELD** — the cross-validation rung has not been run; it stays behind two declared prerequisites (a pre-registered form-pruning rule, and CD12600 data sourcing) | `W2_SPARTA_REGRESSION.md` §10 |

The follow-on rung these items were escalating toward also already ran:
`w2-sparta-regression-discovery` (done 2026-08-01, 137 of 180 core-min)
reproduced the paper's model form exactly and the PH coefficient to 0.66%, and
shipped the coherent CBFS-side discrepancy as its finding
(`W2_SPARTA_REGRESSION.md`).

## Why two approved items pointed at work that was already done

Both W5 escalations were filed on 2026-07-31 while `w2-sparta-frozen-rans-cbfs`
(filed earlier the same day, on the same paper, with the same 60-core-min
budget and materially the same gate) sat approved and unclaimed. The docket had
no claim mechanism, so nothing marked the rung as about-to-be-worked, and the
escalations were the queue's way of shouting about an item it could not see was
moving. When the W2 rung ran the next day, the escalations stayed open because
nothing links a gate to the record that satisfies it. This is precisely the
collision class `w7-claim-an-item-before-working-it` was filed about; the claim
convention was applied to both items this session before this record was
written.

**Wrong intermediate conclusion, recorded:** this session's launch framing
treated the two items as runnable work ("~60 core-min each") whose data was
waiting on disk. Reading the record first — the same discipline
`R4_PREREGISTRATION.md` §1 applied to the B-52 premise — showed the run they
demand is the run that already happened. Re-running the frozen extraction to
"meet" an already-met gate would have spent core-minutes to make the record
worse: two records for one result invites the divergence-by-duplication the
docket has already been burned by.

## What remains genuinely open on the SpaRTA line

Unchanged from `W2_SPARTA_REGRESSION.md` §10, and **not** claimed or advanced
by this record: (1) the cross-validation-in-CFD rung, ~12–20 core-hours
re-priced, gated on a pre-registered form-pruning rule; (2) CD12600 (Laval &
Marquillie) data sourcing; (3) the tau-norm convention decision before any
tau-graded gate is pre-registered again.

## Cost and closure

| Item | Core-min spent under it | Disposition |
| --- | --- | --- |
| `w5-sparta-frozen-rans-is-the-unblock` | **0** (gate met by `w2-sparta-frozen-rans-cbfs`, 27.7 of 60 core-min, 2026-08-01) | closed on the record |
| `w5-sparta-is-still-the-cheapest-real-result` | **0** (same record; "cheapest real result" was confirmed at 18 s of extraction CPU) | closed on the record |

In-sample position unchanged: CBFS13700 and PH10595 are training cases;
`sdk/scripts/closure_in_sample_gate.py` run this session (2026-08-04) before
any closure work: **PASS** — no declared training, fitting, inversion or
calibration set contains a scored case.
