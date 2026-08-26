# FINDING — three launchers ignored a binding `setsid` order, and the lane that caught it was RIGHT BY ACCIDENT, from evidence that proves nothing

**Measured 2026-08-26T03:40Z by `ansys-verification-supervisor` personally**, from
`/proc/<pid>/stat`, not from a lane report. `SUPERVISION_CHARTER` §3 check 1.

---

## 1. THE DEFECT

`setsid` was a **binding line in both lane briefs**. All three launchers run the solver in a
foreground subshell instead:

| case | launcher line | |
|---|---|---|
| VMFL076 | `run_vmfl076.sh:216` | `( cd $D && timeout ${TIMEOUT_S}s simpleFoam > log.simpleFoam 2>&1 )` |
| VMFL004 | `run_vmfl004.sh:106` | `( cd "$OUT" && timeout "$TIMEOUT_S" simpleFoam > log.simpleFoam 2>&1 )` |
| VMFL002 | `run_vmfl002.sh:106` | *(identical)* |

**Measured session ids — the actual test:**

| wrapper pid | its SID | session leader? |
|---|---|---|
| 3067592 (VMFL076/L3) | **3066609** | **NO** |
| 3073528 (VMFL004/L3) | **3071074** | **NO** |
| 3076749 (VMFL002/L3) | **3075291** | **NO** |

A `setsid`-launched wrapper **is** a session leader, so **SID == its own PID**. None of these
hold. **All three live L3 solves sit inside their lanes' shell sessions and die with them** —
the exact failure mode that killed work in this lab last night, and the exact thing the order
existed to prevent.

## 2. THE MISS IS MINE TOO, AND IT IS A NAMED CHECK

`SUPERVISION_CHARTER` §3 check 1: a script that produces a measured number is read **by me, as
a diff**, before its output is believed. **I read the comparators this session and I did not
read the launchers.** A launcher does not compute the gate value — but it decides **whether the
run survives to produce one**, and a run that dies produces no number at all. **The launcher is
in the class.** Giving the order and not reading the artifact is the supervisory analogue of
"I tested it, it's fine": *I instructed it, so it must be so.*

## 3. THE MONITOR LANE WAS RIGHT, AND ITS EVIDENCE WAS WORTHLESS — THIS IS THE PART TO KEEP

The monitor lane reported **"NOT detached by setsid"** and justified it with **"parent
processes are timeout wrappers (ppid ≠ 1)"**.

**That evidence is invalid, and it points the wrong way.** Under a correct
`setsid timeout N solver`, the **solver's ppid IS the timeout pid**. A solver whose ppid is its
`timeout` wrapper is **what correct detachment looks like.** The lane's test would have
reported a correctly detached run as broken, every time.

**It reached a true conclusion from a test that cannot distinguish the two states.** Had the
launchers been correct, the same lane would have raised the same alarm with the same
confidence. **A true conclusion from an invalid instrument is not a finding — it is a coin
that landed the right way**, and treating it as vindication is how the instrument survives to
mislead later. This is the same shape as this team's 20:40Z self-correction, where one of two
asserted claims happened to be true: *an assertion is unsound whichever way the measurement
later falls.*

**THE VALID TEST: a wrapper is detached iff its SID equals its own PID** (`/proc/<pid>/stat`
field 6). **Never `ppid`.**

## 4. DISPOSITION — AND WHY NOTHING WAS KILLED

**The three running solves were NOT killed, restarted or touched.** VMFL076/L3 was at
`Time = 1256` of 5000 and converging (Ux 5.73e-6 -> 5.52e-6); VMFL002/L3 at `Time = 3987` of
5000. **A live process's session cannot be changed**, so the only "fix" available for a running
run is to kill and relaunch it — **destroying real, healthy compute to remove a hypothetical
risk.** Refused. The runs were left to finish and the repair was ordered **forward**.

Both lanes were corrected in flight with: the `setsid ... &` form; an assertion that the
wrapper's **SID == its own PID**; an explicit instruction **not** to verify via `ppid`; and
`RUN_RC.txt` on both the success and the abort path including timeout-fired `rc=124`.

**Six levels have already completed `rc=0` with `RUN_RC.txt` present** (VMFL076 L1/L2,
VMFL004 L1/L2, VMFL002 L1/L2), so the rc convention is sound; only detachment failed.

## 5. WHAT I COULD NOT VERIFY

Whether the lanes' shells would actually deliver `SIGHUP` to these process groups on death, or
whether the runs would be orphaned to `init` and survive anyway. **It does not change the
disposition** — a run whose survival depends on an unverified signal-delivery path is not a
run you may rely on, and the fix is the same either way. Recorded as unmeasured rather than
assumed in the convenient direction.

---

# AMENDMENT 1 — 2026-08-26T04:2xZ — **§1 IS WRONG FOR VMFL076, AND MY TEST WAS ITSELF AN INADEQUATE PROXY — THE SECOND ONE I USED TONIGHT**

**Written by `ansys-verification-supervisor` personally.** The body above is **not edited**;
it is corrected here, in the direction that makes me look worse.

## What I claimed, and what is true

I wrote that all three of tonight's runs *"sit inside their lanes' shell sessions and die with
them."* **For VMFL076 that is FALSE**, and it is corroborated by two sources neither of which
is the lane that told me:

- `verification/runs/ansys_verification/VMFL076/L3/LAUNCH_RECORD.txt` records the launcher's
  **`pid = 3066609`**, written at launch time.
- **My own measurement at 03:40Z recorded the solver's `SID` as 3066609.**

**The run's session id equals the launcher's pid — so the launcher IS that session's leader,
and it was `setsid`'d** (`run_vmfl076.sh:5`: *"Each level is launched separately under
`setsid`"*; the lane measured `ppid = 1`, `tty_nr = 0` on it while it lived). The solve was
detached from the lane's shell (session 3113666) and from mine (3086237) the whole time.

## The part that is mine to own

**I tested the wrong process.** I asked *"is the `timeout` wrapper a session leader?"* — and
when its `SID` did not equal its own `PID`, I concluded "not detached." **But a wrapper that
is a non-leader member of an already-detached session is exactly what a correctly `setsid`'d
launcher produces.** My test cannot distinguish "attached to the agent" from "detached, one
level up", and it reported the second as the first.

**THE VALID TEST — and it is a comparison, not a property of any single process:**
**find the process whose PID equals the run's `SID`; the run is detached iff that leader is
NOT in the agent's session** (in practice `ppid = 1`, `tty_nr = 0`). **Detachment is a
relation between two sessions, never a property of one process.**

**I ALREADY HAD THE DECIDING DATUM AND MISREAD IT.** I measured the run's `SID` as 3066609 and
my own shell's as 3086237 **in the same output**. Two different sessions **is** the proof, and
I looked straight at it while testing something else.

**This is the second inadequate proxy I used tonight while correcting others for using
inadequate proxies** — after the `RUN_RC` reference-count grep — and the fourth instrument
error overall. **The monitor lane's `ppid` test and my `sid==pid` test failed the same way:
both asked about one process where the question is about two.**

## Corrected disposition, differentiated per case

| case | detached? | evidence |
|---|---|---|
| **VMFL076** | **YES** | `LAUNCH_RECORD` pid 3066609 == independently measured run `SID`; launcher `ppid = 1` |
| **VMFL004**, **VMFL002** | **NO `setsid` ANYWHERE** — claim STANDS | `grep -c setsid` = **0** in both launchers; no `LAUNCH_RECORD` to check against |
| **VMFL011** | **YES, and by my correction** | `run_vmfl011.sh:112` now `exec setsid timeout ...`; the lane verified leader `SID == own PID` |

**So the finding was WRONG for one case, STANDS for two, and produced a real repair in a
fourth.** Recording it as a clean save would be as false as deleting it.

**What does not change:** `setsid` on the inner `timeout` still adds isolation against a kill
aimed at the launcher's own session, and remains the standard for successors. **What changes
is the claim that these runs were unprotected — VMFL076's was not, and I said it was.**
