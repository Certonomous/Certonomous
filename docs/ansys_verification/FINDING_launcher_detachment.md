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
