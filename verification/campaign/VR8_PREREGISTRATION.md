# VR8 — SELFTEST TRIGGER REACHABILITY

**Repair-registration. Frozen before any work under it. Written 2026-08-31.**

## 1. The finding this measures

`DEAD_LEVER_AUDIT` §20 (2026-08-31T00:40Z) names the shape for **one** instrument: a control that
is *"fired only when a human or agent types it"* has **no call sites, so it cannot be applied, only
remembered.** §20 deliberately declines to generalise. Generalising it is verification's own work.

The question this item asks of every `--selftest` in `scripts/` is not *"does something call it"*
but **"is it reachable from something that runs BY ITSELF"** — a crontab line or a `.claude` hook.
**A chain of hand-only callers is still hand-only**, so reachability, not adjacency, is the honest
test.

## 2. WHAT IS MINE

The **census** is mine. The scripts belong to five other teams and **wiring a trigger is each
owner's act.** This item wires nothing and edits nothing.

### 2a. Rule-2 condition, and how it was checked

No compute has been spent under this document. The run artefacts this item will create —
`STATUS.VR8_SELFTEST_TRIGGER_REACHABILITY` and `launcher.queue.out` under the registered cwd
`/home/ubuntu/Certonomous/verification/runs/verification/VR8_SELFTEST_TRIGGER_REACHABILITY/` —
**do not exist**, checked by direct `ls` before this file was written.

### 2b. Disclosed: the driver was DRIVEN before enqueue, and its FIRST FORM WAS WRONG

`verification/credibility/vr8_selftest_trigger_census.py` was driven with `--selftest` before
enqueue: **8 cases, 0 failures, rc 0**. It reached that state by failing first, twice, and both
failures are disclosed because they shaped the gate:

- **DEFECT 1 — file-level co-occurrence is not an invocation.** The first matcher asked whether
  another file contained both the definer's basename and `--selftest` anywhere in it. That admits
  `scripts/queue_entry_check.py`, which names `queue_runner.py` at line 159 and carries its own
  `--selftest` at line 36 — **sixty lines apart and unrelated.**
- **DEFECT 2 — prose lives inside `.py` too.** Excluding `.md` is insufficient: a docstring is
  prose in an executable carrier, and **the driver's own docstring** names `queue_runner.py`
  beside `--selftest`. Comment and docstring lines are now stripped before matching.

### 2c. ⚠ §20's RULING IS STALE, AND THIS ITEM IS NOT ANCHORED ON IT

**Established during drafting and stated here because a rung anchored on §20 would have graded a
stale audit section.** §20 ruled `queue_runner.py --selftest` HAND-ONLY: *"the wrapper launched
`--daemon`, `check_harness.py` never called `--selftest`, and no hook or cron ran it."*

**That is no longer true.** cfd landed a **fail-closed selftest gate** in `scripts/queue_runner.sh`
on 2026-08-31, citing verification's own audit finding 5. The live chain, re-derived from the
**running crontab** and the **real wrapper** rather than cited:

```
crontab   * * * * * /bin/bash /home/ubuntu/Certonomous/scripts/queue_runner.sh
  -> scripts/queue_runner.sh:91   python3 "$REPO/scripts/queue_runner.py" --selftest
```

The driver's ground-truth limb X1 asserts **this chain**, verified today. §20 is **not amended by
this item** — that is the audit's own section and not this document's to touch — but the staleness
is on the record here.

## 3. Gate (frozen)

A committed driver under `verification/credibility/` that:

- **G1** enumerates every `scripts/` file defining `--selftest`. **SCOPE IS `scripts/` ONLY.**
  Selftests under `cases/` and `verification/` are **out of scope** and nothing is claimed about
  them; a wider sweep is a different rung with a different cap.
- **G2** reads the **automatic roots** — the live crontab and the `.claude` hook commands, written
  by the box's owner and the lab's configuration, the real producers.
- **G3** classifies each definer **TRIGGERED** (an automatic root reaches a
  `<definer> --selftest` **invocation** — same non-comment line, prose stripped) or **HAND-ONLY**.
- **G4** controls, both limbs, **on real bytes** (§2j): the reader must return TRIGGERED on the
  real cron→wrapper→selftest chain **and** HAND-ONLY on a real unwired instrument; the same-line
  matcher must be shown **silent** on the real `queue_entry_check.py` co-occurrence that the loose
  matcher fires on; and prose stripping must be shown removing a **real docstring mention**.
- **G5** **REFUSES (exit 2)** rather than degrading when the crontab or `scripts/` cannot be read
  — with no automatic roots **every** instrument reads HAND-ONLY, which is parser blindness, not a
  finding.

## 4. Threshold / label

- **PASS** = every `scripts/` `--selftest` is reachable from an automatic root.
- **GATE FAIL** = any is not.
- **NOT A RESULT** = a control limb misbehaves.
- **BLOCKED** = the crontab or `scripts/` cannot be read.

Only `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` may be emitted.

## 5. PREDICTED OUTCOME — stated as a prediction, before the run

**I predict GATE FAIL.** Measured during drafting and disclosed under §2b: **54** definers in
`scripts/`, of which **1** (`queue_runner.py`, via cfd's fail-closed gate) is reachable and **53**
are not.

**A GATE FAIL here is a finding about the LAB'S CONTROLS and not a failure of any instrument.** A
selftest with no trigger is not a broken test; it is a working test nothing fires.

## 6. Cap and cost

**Registered estimate: 0.05 core-minutes. Cap: 0.5 core-minutes.**

Arithmetic, **costed on the CONTENDED box** (load average 7.8–15.0 over 16 cores at drafting;
the quiet-box figure is the flattering one and is not used):

```
selftest drive, measured on the contended box : 0.120 s wall x 1 rank / 60 = 0.00200 core-min
registered estimate, with contention headroom :   3    s wall x 1 rank / 60 = 0.05    core-min
cap, ~10x the registered estimate             :  30    s wall x 1 rank / 60 = 0.50    core-min
```

Dollars **DERIVED, NOT MEASURED** at $0.0513/core-h, itself **reported-by-owner**
(`COMPUTE_BUDGET_CHARTER` §5):

```
estimate : 0.05 core-min / 60 x $0.0513 = $0.0000428   DERIVED-NOT-MEASURED
cap      : 0.50 core-min / 60 x $0.0513 = $0.000428    DERIVED-NOT-MEASURED
```

**Zero solver compute.** An overrun **stops the run** (rule 12).

## 7. Not claimed

No instrument is called defective by this item, and no verdict is withdrawn. A HAND-ONLY selftest
may be perfectly correct — the finding is about **what fires it**, not about what it checks.
Nothing here obliges any team to wire a trigger, and this item wires none. §20 is **not amended**.
