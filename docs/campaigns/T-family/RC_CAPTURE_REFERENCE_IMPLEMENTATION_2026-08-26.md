# The lab's reference **rc-capture** launcher — `run_one_t8.sh`, written up **with its repair**

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26, at the
supervisor's instruction to surface this for adoption rather than let other teams
reinvent it. ZERO COMPUTE.** **Nothing has been sent, filed, submitted,
uploaded, registered or posted outside this box (`CLAUDE.md` rule 7).**

**Reference:** `verification/runs/T-family/T8_runs/run_one_t8.sh` (78 lines),
frozen in `T8_PREREGISTRATION.md` §11 at blob `70a37aa634d6`. **It is not edited
by this file.** The repair below is specified **for adopters**, and lands in the
frozen original only through its own rung's amendment route.

---

> # ⛔ **NOT ADOPTABLE AS IT STANDS. TWO REPAIRS ARE MANDATORY BEFORE ANY TEAM COPIES THIS SCRIPT.**
>
> **Escalated by the heat-transfer supervisor, 2026-08-26**, who was on the point of
> handing this script to cfd as the lab's reference rc-capture implementation for
> Sanaa's detached queue. **A reference implementation that reports success on a
> crashed solve would have propagated the exact failure it was being adopted to
> prevent.**
>
> ### REPAIR 1 — `exit "$RC"`, or document loudly that `$?` MEANS NOTHING
> The script's last line is an unconditional **`exit 0`**. **The launcher returns
> success even when the solver died.** A queue driver chaining on `&&` marches
> straight past a SIGFPE. On T8 that is not hypothetical: `m` returned **136** and
> the launcher still exited **0**.
>
> ### REPAIR 2 — `capped = (wall_s >= timeout_s)`, never an rc lookup
> `run_one_t8.sh:71` decides "was I stopped by my budget?" from `rc` alone. **`137`
> is SIGKILL — produced by `timeout --kill-after` on expiry AND by the OOM killer**;
> `124` is `timeout`'s expiry code **and** a legal exit status for any child. **As
> written the script would silently relabel an OOM KILL as a BUDGET STOP** — recorded
> as `PENDING`, right-censored, *not a failure* — and the real defect would never be
> triaged.
>
> **Both repairs are detailed at §3 and §4. Neither is optional. The strengths
> catalogued at §2 are real and are why the script is worth adopting AT ALL — but they
> are not a reason to adopt it unrepaired.**

## 1. Why this matters now

Sanaa's directive, relayed via the chief: *"All the runs that need to happen get
queued… I dont want to have idle compute anytmore."* A detached queue means
**nobody is watching the terminal when a case dies**, so the launcher's record is
the only witness. **A launcher that captures nothing turns every failure into a
silence, and a silence into an assumption that it worked.**

## 2. What `run_one_t8.sh` does that other launchers do not

For every case it writes `STATUS.<case>` beside the run tree, containing:

```
case=        rc=         wall_s=      ranks=
core_min=    cap_core_min=            timeout_s=
```

**Three things in that list are the design, and each has a reason.**

### 2.1 `rc` is captured from the solver, not from the script

```
timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" buoyantBoussinesqSimpleFoam ...
RC=$?
```

`$?` is taken **on the line after** the solver, before anything else can clobber
it. The K0d launcher that captured nothing could not distinguish any failure from
any other.

### 2.2 THE CORE-MINUTE CAP IS ENFORCED AS WALL TIME — the budget is not advisory

```
TIMEOUT_S=$(( CAP_CORE_MIN * 60 / RANKS ))
```

**`CLAUDE.md` rule 12 says an overrun stops the run.** Here the pre-registered
core-minute cap is **converted into the `timeout` argument**, so the rule is
enforced by the kernel rather than by an agent remembering to check. **A cap that
lives only in a document is a wish.** This is the single most copyable line in
the script.

### 2.3 `wall_s` AND `timeout_s` TOGETHER — the pair is the insight

**Two states with opposite meanings for the completion rule:**

| state | signature | what it means |
|---|---|---|
| **cap-stop** | `wall_s ≈ timeout_s` | right-censored. The run was **stopped by the budget**, not by the physics. `PENDING`, never `GATE FAIL`. |
| **crash** | `wall_s ≪ timeout_s` | the solver **died**. A finding until triage says otherwise (`SUPERVISION_CHARTER.md` §3 check 2). |

**Neither is readable from `rc` alone. The pair makes both readable, and the pair
costs two `echo` lines.** Demonstrated on T8's own three cases:

| level | rc | `wall_s` | `timeout_s` | `wall_s / timeout_s` | reading |
|---|---:|---:|---:|---:|---|
| `c` | 0 | 229 | 900 | 25 % | ran to `endTime` |
| `m` | **136** | **150** | **4800** | **3.1 %** | **unambiguously a crash** — SIGFPE, nowhere near the cap |
| `f` | 0 | 13,101 | 30,000 | 44 % | ran to `endTime` |

`m`'s `rc = 136` = 128 + 8 = **SIGFPE**. Without `timeout_s` beside it, a reader
must *know* that 136 is not a timeout code. **With the pair, they do not have to
know anything: 150 against 4800 settles it.**

## 3. THE REPAIR — and it is not optional for an adopter

`run_one_t8.sh:71-73`:

```
  if [ "$RC" -eq 124 ] || [ "$RC" -eq 137 ]; then
    echo "verdict=PENDING (killed by the registered cap; right-censored, NOT GATE FAIL)"
  fi
```

**This decides "capped" from `rc` alone — the one input §2.3 has just shown to be
insufficient.** Measured on this box (**GNU coreutils 9.4**):

- **`137` = 128 + 9 = SIGKILL.** It is what `timeout --kill-after` produces on
  expiry **and what the OOM killer produces.** The two are indistinguishable by
  `rc`.
- **`124` is `timeout`'s own expiry code — and it is also a perfectly legal exit
  status for a child process.** A solver that genuinely exits 124 is
  indistinguishable from a wall-clock expiry.

> **AS WRITTEN, THE SCRIPT WOULD SILENTLY RELABEL AN **OOM KILL** AS A **BUDGET
> STOP** — and a budget stop is recorded as `PENDING`, right-censored, *not a
> failure*. An out-of-memory death would be filed as "we simply ran out of
> allowance", and the real defect would never be triaged.**

**The repair, and the inputs are already in the file:**

```
CAPPED=0
[ "$WALL" -ge "$TIMEOUT_S" ] && CAPPED=1        # an INDEPENDENT witness
...
if [ "$CAPPED" -eq 1 ]; then
  echo "capped=1"
  echo "verdict=PENDING (killed by the registered cap; right-censored, NOT GATE FAIL)"
else
  echo "capped=0"
fi
```

**`wall_s >= timeout_s` is an independent witness**: it comes from the clock, not
from the dying process, so a process cannot fake it by choosing its exit status.
**The `STATUS` file already records both inputs — it simply does not use them.**

> **THE GENERAL RULE: DECIDE "WAS I STOPPED BY MY OWN BUDGET?" FROM AN
> INDEPENDENT WITNESS, NEVER FROM A NUMBER THE STOPPED PROCESS CHOSE.**

**Honest scope: this defect did NOT bite on T8.** `m` returned 136, which is
neither 124 nor 137, so the branch never fired and no T8 `STATUS` file carries a
false `PENDING`. **It is latent, exactly like the `-O` exposure**, and it is
repaired in the adopter's copy rather than retrofitted into a frozen file.

## 4. A SECOND DEFECT, FOUND WHILE WRITING THIS UP — the launcher's own rc is always 0

The script's last line is an unconditional **`exit 0`**. **The launcher returns
success even when the solver died.** On T8 that means a queue driver running
`run_one_t8.sh m && next_thing` would have proceeded **as though `m` succeeded**,
while `m` was dumping core.

This is defensible **as a design** — the rc is deliberately carried in the
`STATUS` file so that a `timeout`-wrapped background launch cannot lose it — **but
it is a trap for exactly the detached-queue use Sanaa has just asked for**, where
the natural driver is a shell `&&` chain.

**For an adopter, one of two, and it must be chosen deliberately:**

- **`exit "$RC"`**, so the launcher's own status carries the solver's; or
- **keep `exit 0` and document loudly that `$?` MEANS NOTHING** — the queue driver
  must read `STATUS.<case>` and must never branch on the launcher's rc.

**Either is fine. Not choosing is not**, because a queue built on `&&` around a
launcher that always exits 0 marches straight past every crash.

## 5. The adoption checklist, for a launcher in any campaign

1. Capture `$?` on the line **immediately after** the solver.
2. Derive the `timeout` argument **from the pre-registered core-minute cap**, so
   the cap is enforced by the kernel.
3. Write **`rc`, `wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`** to a
   `STATUS.<case>` file beside the run tree.
4. Decide `capped` from **`wall_s >= timeout_s`**, never from the rc lookup, and
   record `capped=0|1` explicitly.
5. Decide and **document** whether the launcher's own rc carries the solver's.
6. Keep the **arming guard** (`run_one_t8.sh:38-41`): refuse if `0/` or any time
   directory already exists, and **`touch 0/T` LAST** at arming so it dates the
   run the age guard measures against (`CLAUDE.md` rule 4).

**Items 1–3 and 6 are already in `run_one_t8.sh` and are the reason it is the
reference. Items 4 and 5 are what an adopter must add.**

## 6. Cost

**Zero core-minutes.** Reading a shell script and three `STATUS` files.

---

## 7. DISCLOSURE — this file was edited above the foot, 2026-08-26, and why

**This document is a lane's write-up from today. It is NOT frozen, is named in no
freeze set, and is cited by no record by line number.** On 2026-08-26 the
heat-transfer supervisor ruled that it *"must never present the script as adoptable
without both repairs"*, and a warning that a reader reaches only at §3 does not
discharge that.

**The edit, stated exactly:** a blocking banner was inserted **above §1**, carrying
both repairs. **No existing section was reworded, struck or removed** — §1–§6 stand
verbatim and the banner is additive. Line numbers below the insertion point **have
moved**, which is why this disclosure exists rather than a silent edit.

**Rule 6 is not engaged** — that rule governs **frozen** files, and this is not one.
**The disclosure is made anyway**, because the reason to disclose a moved line is that
somebody may be citing it, and that reason does not check whether a file is frozen
first.
