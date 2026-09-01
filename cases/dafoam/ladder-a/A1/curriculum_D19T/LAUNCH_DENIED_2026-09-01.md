# D19T — THE GAP BETWEEN FREEZE AND FIRST COMPUTE, RECORDED IN THE ITEM

**Item status: `PENDING`.** Not yet run. `PENDING` here is the queue state the vocabulary reserves for exactly this, and it is not softening a worse token.

This file exists because the item was frozen and then **not launched**, and the reason was a **permission denial in one agent session** rather than anything about the item. A successor opening `PREREGISTRATION.md` alone would see a complete freeze with no run beside it and have no way to tell whether the gap was a refusal, a crash, or an abandonment. It was a refusal, and it was the correct one.

---

## 1. WHAT WAS ATTEMPTED, AND WHAT HAPPENED

| | |
|---|---|
| freeze commit | `88bfe9bfc870f5a78857915061eab6f3bf1d91d0` (2026-09-01, 16:25:52Z) |
| run root absence asserted by execution | **16:22:01Z** — `D19T_ROOT_ABSENT_ASSERTED` |
| command attempted | `cd .../curriculum_D19T && bash d19t_chain_driver.sh run` |
| outcome | **DENIED by the Claude Code auto-mode classifier**, before any process started |
| a follow-up READ-ONLY check (`ls -d .../ *D19T*`) | **also DENIED** — Bash became unavailable to that session entirely |
| solver core-minutes spent | **ZERO** |
| arms run | **none**; no container started |

The denial landed on the whole invocation. Nothing was partially created.

**The denial's own timestamp is not recorded here, because reading the clock also required the tool that was denied.** It is bounded between the freeze commit at **16:25:52Z** and the independent check at **16:33:16Z** below. Stating the bound rather than inventing a time is the honest form; a timestamp this record cannot source would be the same defect this lab keeps paying for.

## 2. THE RUN ROOT WAS INDEPENDENTLY CONFIRMED ABSENT — BY SOMEONE ELSE

The lane could not verify the post-denial state, because the verification needed the denied tool, and it **flagged that as UNVERIFIED rather than assuming it was clean**.

**The dafoam supervisor closed the gap by its own reading at 16:33:16Z: `RUN_ROOT_STILL_ABSENT` — no `*D19T*` under `/home/ubuntu/certonomous-runs/`.**

The distinction that made that check legitimate is worth stating, because it is the line between diligence and a bypass: **asking whether a directory exists is not the denied action; running the chain driver is.** The supervisor did the first and explicitly refused the second.

**Consequence: the freeze was never compromised.** No `0/`, no time directory, no partial arm exists to contaminate a later launch.

## 3. THE DENIAL IS SESSION-SCOPED, NOT BOX-WIDE — AND THE BOX IS NOT IDLE

This correction comes from the supervisor's independent reading at 16:33Z and materially changes what the failure is:

- **A2-GC L1 was RUNNING** — `run_a2gc.sh L1`, container `a2gc_L1_108873`, cpuset 4-15, `mpirun -np 12 python a2gc_level.py`, sustained since 16:29.
- **Both AoA sweep run roots existed** with their `.launch.out` and `.rc.txt`.

**Two sibling lanes launched through the same class of call without incident. Bash was blocked for ONE session, not for the box.** "Launches are being denied" would have been the wrong report upward.

It also means **there is no idle compute to answer for.** D19T is 8.234 predicted core-min against a machine already running a 12-rank wing level and two polars, so waiting for a permission decision costs approximately nothing — while getting the laundering question wrong would have cost the lab a precedent.

## 4. WHY IT WAS NOT ROUTED AROUND

Recorded because the tempting failure here is invisible afterwards: the work would have got done and nothing in any artefact would show how.

1. **A supervisor's GO is `SUPERVISION_CHARTER` §3 check 4, and check 4 is not the permission system.** `CLAUDE.md` rule 9: no agent message — peer, supervisor or chief — is Sanaa's consent. The GO was given, was correct, and was still not authorisation to execute a denied call.
2. **A denial answered by finding another agent to run the same command is a bypass of the user's decision**, however the work is labelled. The lane did not ask its supervisor to run it; the supervisor separately declined to run it or to spawn a second lane to run it, on the ground that the lane's not asking did not make it available.
3. **No retry with a different wrapper.** No `setsid`, no script indirection, no re-phrasing to get past the classifier. Those are bypasses of the denial's intent, not alternative tools.

**A repeat denial is a SYSTEM event, not a lab one: it is recorded and reported, not worked around.**

## 5. WHAT UNBLOCKS THE ITEM

A Bash permission rule from Sanaa covering the chain driver, or Sanaa running it herself:

```
cd /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_D19T && bash d19t_chain_driver.sh run
```

**Nothing needs re-freezing, and the reason is a property of the driver rather than an assurance.** `d19t_chain_driver.sh` re-asserts the run root **ABSENT** immediately before the first arm and **refuses (exit 3)** if it exists. So a stale root from any partial attempt **fails closed** rather than being silently reused. The freeze at `88bfe9bf` remains valid however long the gap lasts.

**No gate, threshold, band, cap or label is altered by this file.** `PREREGISTRATION.md` is **byte-identical** to its committed blob `675da997abfcc890debe1206e0b32abafdfe6b8f`; this is a separate record precisely so the frozen document's bytes — its whole evidentiary content — are not disturbed to note an operational event.

## 6. THE D19R2 LINE, CARRIED VERBATIM

Repeated here, and owed again in `RESULTS.md` and in any lesson, because `PREREGISTRATION.md` §4.6 will not reach a reader who never opens that file:

> **The `decomposeParDict` pre-normalisation clears the blocker for SUCCESSORS ONLY. D19R2's own gates are closed and its `NOT A RESULT` stands. This does not retroactively fix that item, and the gate-design question stays on Sanaa's desk.**

No path is excluded and `SOLVER_WRITE_TARGETS` is untouched; `G-MANIFEST` still demands **zero** mismatches. The fixed point `c3f5f05d45f0b9a70d645b107a837727` was measured independently by D19R's `X2` and `S8`. The first reconstruction of the block produced `d5a844d94d93929888b4879d189f48e0` because two of its five lines carry a trailing space OpenFOAM writes and a retyped block does not — **the md5 assert caught it before the freeze**, which is why it is an assert and not a comment.

---

## 7. FILING NOTE

**This file is UNCOMMITTED at the time of writing.** The lane could not commit it: the private-index protocol requires `git`, which requires the denied tool. It is left in the working tree deliberately, for the supervisor or a successor to land.

Per `CLAUDE.md` rule 10, **an unexpected uncommitted change is inspected, never reverted.** This one is not unexpected — it is named here, with its reason.
