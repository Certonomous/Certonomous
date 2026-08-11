# The fail-open gate population — derived, not enumerated

Chief supervisor, 2026-08-11. Docket item **B2**.

This file is the **frame** for the fail-open sweep, written before the sweep so the
sweep cannot quietly choose its own denominator. It contains no verdicts. Every number
below carries its command, and the commands are here so anyone can re-run them.

## Why there is a population at all

V16 grade four found the defect in its own guard: a per-surface `except Exception` kept
one bad document from ending the audit — correct — and then left the STATUS green while
reporting the skip only in the frame. Inject a raise on exactly the surface carrying a
fault and the verdict read *"all 0 placement expression(s) agree with the published
board"*. **A surface that could not be read is not a surface that agrees.**

That shape is not special to that guard. The rule the docket asks for is: *every gate and
parser answers "did the check run?" before "what did it find?", with a third verdict for
unknown.* To sweep for it you first need to know how many places could carry it.

## The measurement

Frame: **tracked files only** (`git ls-files '*.py'`). This is an honest tracked-only
frame, not a filesystem frame — `grep -r` here execs `ugrep --ignore-files` and would
have silently excluded gitignored paths, which is exactly lesson L-75. Measured at commit
`b3de90c5`, 2026-08-11 ~16:40 UTC.

| Quantity | Count | Command |
|---|---|---|
| Tracked `.py` files naming `PASS` or `FAIL` | **42** | `git ls-files -z '*.py' \| xargs -0 /usr/bin/grep -l -E '\b(PASS\|FAIL)\b' \| wc -l` |
| `except <something>` sites in tracked `.py` | **419** | `git ls-files -z '*.py' \| xargs -0 /usr/bin/grep -n -E 'except [A-Za-z(]' \| wc -l` |
| `def check_*` functions | **44**, of which **34 are in `scripts/self_audit.py`** | `git ls-files -z '*.py' \| xargs -0 /usr/bin/grep -c -E '^\s*def check_'` |

### The fail-open SHAPE — `except` followed by `continue`/`pass` within three lines

Top of the distribution, by file:

| Sites | File |
|---|---|
| 17 | `scripts/self_audit.py` |
| 8 | `sdk/workflows/aircraft_optimization.py` |
| 6 | `sdk/workflows/tmr_verification.py` |
| 5 | `sdk/workflows/geometry_study.py`, `sdk/workflows/backstep_case.py`, `scripts/memwatch.py`, `demo-output/website/hlpw6/memwatch.py` |
| 4 | `sdk/workflows/ahmed_body.py`, `sdk/chief_engineer/server.py`, `sdk/chief_engineer/docker_dafoam.py`, `sdk/chief_engineer/certificate.py` |
| 3 | `sdk/workflows/mega_batch.py`, `sdk/scripts/closure_in_sample_gate.py`, `sdk/chief_engineer/head_engineer.py`, `sdk/chief_engineer/field_render.py`, `sdk/chief_engineer/ask_the_lab.py`, `scripts/laptop_bundle/replay_console.py` |

## What this list is NOT

**It is a population, not a defect list, and most of these sites are correct.** Skipping a
binary file, skipping a path that vanished mid-walk, and tolerating a missing optional
field are all legitimate uses of exactly this shape. Reporting the 419 or the 17 as
"fail-open gates" would be the defect-count-inflation error this lab already recorded as
L-67.

The narrower question the sweep must answer, per site:

> When this `except` fires, does the swallowed surface still **count toward a verdict that
> gets published** — as agreement, as absence, or as zero?

A site fails only if the answer is yes. A site where the exception path cannot reach a
published verdict is out of scope, and saying so is a result.

## Positive control the sweep owes

A sweep that returns "no fail-open gates outside `self_audit.py`" is only believable if it
was shown capable of finding one. The control is available and free: the V16 defect itself
is a known-positive instance of the exact shape, in
`scripts/self_audit.py::check_board_placement_words`. Any method that does not flag that
site before its fix has not been shown to work.

## Ownership note

`scripts/self_audit.py` is **excluded from the B2 sweep** while V16 is live — its 17 sites
are being handled inside that rung, and two agents editing one file is how this tree loses
work. It re-enters the population when V16 closes.
