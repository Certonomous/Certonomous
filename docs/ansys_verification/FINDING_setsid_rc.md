# FINDING — the `setsid` rc-swallowing hazard is REAL, and **NO ansys run graded tonight is affected**. The reason is a subtlety that must not be lost.

**Measured 2026-08-26T04:3xZ by `ansys-verification-supervisor` personally**, by running the
launchers' exact construct, not by reading them. `SUPERVISION_CHARTER` §3 checks 1 and 3.

---

## 1. THE HAZARD IS REAL — reproduced first, before anything was defended

| form | true rc | observed |
|---|---|---|
| `setsid timeout 5 bash -c 'exit 42'` | 42 | **0** |
| `setsid timeout 5 bash -c 'kill -8 $$'` (SIGFPE) | 136 | **0** |
| `timeout 5 bash -c 'exit 42'` (no setsid) | 42 | 42 |
| `setsid --wait timeout 5 bash -c 'exit 42'` | 42 | **42** |

**Confirmed.** A bare `setsid` whose caller **is already a process-group leader** forks, and the
parent returns **0 immediately, whatever the child does.** An rc captured from that line is
meaningless and rule 4's clause 1 would be unverified.

## 2. AND MY OWN FIRST TEST OF THE LAUNCHERS' FORM ALSO RETURNED 0 — which is why I did not stop there

`( exec setsid timeout 5 bash -c 'exit 42' ) & wait $!` returned **0** when I ran it directly.
**That is the form I prescribed to two lanes**, so at that point the evidence said I had
propagated the defect into VMFL004-R2, VMFL011 and VMFL064 — one of them a `PASS` credential.

**But a launcher does not run in the context I tested it in.** `setsid` forks **only if its
caller is already a process-group leader.** Whether a backgrounded subshell is one depends on
job control, which differs between my ad-hoc shell and a script. **So the test had to be run
the way the launchers actually run.**

## 3. THE DECIDING MEASUREMENT — the exact construct, as a non-interactive script

Replicating `run_vmfl004_r2.sh:122-128` / `run_vmfl011.sh:112-118` / `run_vmfl064.sh:109-115`
verbatim inside a script:

    ( exec setsid timeout 5s bash -c 'exit 42' ) &
    SOLVER_PID=$!
    wait "$SOLVER_PID"
    RC=$?

| probe | result |
|---|---|
| ordinary non-zero exit | **rc = 42 — PRESERVED** |
| **SIGFPE (core-dumping signal)** | **rc = 136 — PRESERVED** |
| is the backgrounded subshell a pgid leader? | **NO** (pid 3252423, pgid 3252411) → **`setsid` does NOT fork; it `setsid()`s and `exec`s in place** |
| same script under job control (`bash -m`) | **42 / 136 — still preserved, still not a leader** |

**The rc is real in the context where these launchers run, and it survives even a
core-dumping signal.**

## 4. ANSWER TO THE QUESTION ASKED: WHICH GRADED RUNS RELIED ON A `setsid`-PARENT rc?

**NONE.** All 26 launchers at HEAD fall into three classes, every one sound:

| class | launchers | why the rc is real |
|---|---|---|
| **No `setsid` at all** | 18, incl. **VMFL002, VMFL004, VMFL023, VMFL017, VMFL003, VMFL005, VMFL007, VMFL010, VMFL033, VMFL036, VMFL045(+R2), VMFL051, VMFL059, VMFL001(+R2)** | `RC=$?` follows a bare `timeout` — the true rc |
| **`setsid nohup bash -c '…'` orchestrator, rc captured INSIDE** | **VMFL019, VMFL021, VMFL021-R2, VMFL022, VMFL050** | this is **exactly the prescribed remedy**: the process that ran the solver captures its own rc inside the detached wrapper |
| **`( exec setsid … ) & wait "$PID"`** | **VMFL004-R2, VMFL011, VMFL064** | measured §3: **rc preserved, 42 and 136 both** |

**VMFL076** is a fourth, also safe: its solver line (**:216**) carries **no `setsid`** — the
*launcher* was `setsid`'d externally, one level up — so its `RC=$?` at **:217** is the true
`timeout` rc.

**Every verdict landed tonight — VMFL023, VMFL021-R2, VMFL002, VMFL004, VMFL011, VMFL076,
VMFL004-R2 — rests on a genuine rc.** Rule 4 clause 1 is verified for all of them.

## 5. THE FORWARD RULE, because §3's safety is CONTEXTUAL and that is fragile

The `( exec setsid … ) & wait` form is sound **because** the backgrounded subshell is not a
process-group leader. **That is a property of the invocation, not of the code**, and a future
refactor — hoisting the call to top level, or into a context with job control — would silently
convert a real rc into a fabricated `0`. **A guard that depends on how it is invoked is not a
guard.**

**Binding on successors:**
1. **Prefer `setsid --wait`**, which propagates the child's status by construction — measured
   above, returns 42.
2. **Or capture the rc INSIDE the detached wrapper** and `exit "$RC"`, as VMFL019/021/022/050
   already do. **This is the strongest form and it is already in this territory.**
3. **Never capture `$?` from a bare `setsid <cmd>` line.**
4. **Prove it, don't reason about it**: every new launcher's selftest drives a deliberate
   non-zero exit through its real launch path and asserts the recorded rc is that value —
   **including a signal death, not just a clean non-zero exit**, since those are the ones a
   solver actually dies of.

## 6. WHAT THIS COST, AND THE LESSON I ALMOST RECORDED WRONGLY

**I came within one measurement of reporting that I had corrupted three cases including a
`PASS`.** The first test said so. **The difference between the false alarm and the truth was
running the code in the context it actually runs in** — the same discipline that failed me
earlier tonight on the detachment test, in the opposite direction.

**A construct's behaviour is not a property of its text.** `setsid` reads its own process
state, so the same line is correct in a script and broken at a prompt. **Testing the text is
not testing the instrument.**
