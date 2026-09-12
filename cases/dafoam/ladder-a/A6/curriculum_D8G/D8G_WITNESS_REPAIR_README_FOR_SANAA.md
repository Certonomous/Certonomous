# D8G launch-witness repair — PREPARED FOR SANAA. **INERT UNTIL SHE APPLIES IT.**

**This changes nothing until the one command below is run in Sanaa's own session.** It was prepared by
the `dafoam-supervisor` because **the auto-mode classifier denied the write twice (`[Security Weaken]`)
and nothing routes around that denial.** No agent's word — not a lane's, not the chief's, not mine —
is consent for it. **Sanaa lifts it herself or it stays unapplied.**

## THE ONE COMMAND

```
cd /home/ubuntu/Certonomous && git apply cases/dafoam/ladder-a/A6/curriculum_D8G/D8G_WITNESS_REPAIR_FOR_SANAA.patch
```

`git apply --check` on this patch **passes** as of preparation. It touches **exactly three files** and
nothing else.

## THE SIX CHECKSUMS, AS LITERALS

Recorded as **values, never as a command** — a freeze block that stores `git rev-parse …` re-evaluates
against whatever `HEAD` holds and self-satisfies at every commit (cfd's CRM finding, 2026-09-12).

| file | BEFORE (md5) | AFTER (md5) |
|---|---|---|
| `d8g_run_arm.sh` | `7ce53b9242ac6e850cc330712d93d5b0` | `6808ce9fc68a9224205ae88454d70675` |
| `d8g_launch_assert_selftest.sh` | `6ca42aa09e01b4727458e79fb82e5a9c` | `bcfeab8c08d047f571002ee5d7db3b91` |
| `d8g_chain_driver.sh` | `1cfc0f17e0d7dfaf3d711b690446860b` | `0a06e0b18b9b981a6c4211a756e49474` |

Verify after applying with `md5sum` on those three paths. **If any BEFORE hash does not match before you
apply, STOP — the files have moved since preparation and this patch is stale.**

## WHAT IT DOES

**It retires one kill and replaces it with a record.** `d8g_run_arm.sh` refused a run when a
**cap-derived clock** elapsed (`rc=89`) and killed the container. The patch deletes that branch and
replaces it with an escalation that writes `verdict=NONE killed=nothing` to a file and to `ledger.txt`,
**and keeps waiting**. The budget figure becomes `ceil(2.0 × (255.93 + 3.0e-5 × cells))`, derived from
measurement rather than from a cap, with two fail-closed guards — inputs-all-positive, and `if b <
fixed: abort` so no figure below the measured import floor can ever be set.

**The third file change is the one that makes it safe to apply:** `d8g_chain_driver.sh` pins
`MD5_LAUNCHER` and checks it **twice** (`:112` and again before every arm). **Applying the launcher
change without re-pinning would abort the chain with `ABORT launcher md5 drifted`, and the ledger would
gain a row that looks like a launch failure and is actually a stale pin.** The patch re-pins it in the
same operation.

## WHAT IT DOES **NOT** DO

`rc=88` (container exited) and `rc=90` (reader unreadable) are **untouched and still real refusals**, so
a genuinely dead container is still caught — **only the clock stops killing.** No gate, band, threshold,
cap or label moves. `d8g_grade.py` is **not** in this patch and stays at
`12688063e20cbb6fa79cf08d0996d4e1`. It does **not** touch the in-container `timeout -k 60 786`, which is
a separate, still-denied question.

## BOTH COSTS, SO THE DECISION IS MADE WITH THEM VISIBLE

**Cost of applying.** Read as a diff, this **is a safety guard being removed from a process launcher on a
shared box** — the classifier is not wrong on its face. And two things are unverified: the repaired
assertion **has never watched a real DAFoam container** (docker is a stub in all 56 selftest checks), and
the 255.93 s figure is **single-process on two cores, not four MPI ranks under contention**.

**Cost of not applying.** D8G's next arm stays blocked behind an instrument that will refuse a **working**
solver. L2-P's budget is **392 s** against a **measured 255.9 s startup that does not scale with mesh at
all**: `decomposePar` took **1.337 s at 44,544 cells against 7.074 s at 5,568 cells** — eight times the
cells, **faster** — which refutes the linear-in-cells scaling two earlier lab records assumed.

## PROVENANCE OF THE BYTES

The launcher candidate was read **as a diff** by the `dafoam-supervisor` at check-1 (`SUPERVISION_CHARTER`
§3, non-delegable) at blob md5 `d7ac583b9c03bb9de639ed3761ed29ca`. It then drifted to
`6808ce9fc68a9224205ae88454d70675`; that drift was **re-read as a diff and is 11 added lines, all comment
text, zero executable change** — it strikes a now-false identity claim in the file's own header and
records the correct hash. Selftest evidence on the repaired bytes: **56 pass / 0 fail**
(`d8g_launch_assert_selftest_evidence_20260912.txt`), including a control in which a healthy-but-slow
solver escalates and is then launched rather than killed.

**D8G is memory-blocked regardless** — `MemAvailable` ~11 GiB against a 14 GiB launch bar — so nothing
is waiting on an urgent answer.

**SUBMISSIONS PARKED.** This file is prepared in the box and sent nowhere.
