# Birth-requirement confirmation — closure's two live comparators

**Status: CONFIRMED for `grade_g2.py` (before G2 is graded) and, retrospectively,
for `grade_g1b.py` (whose verdict is already published).**

Sanaa canonized this on 2026-08-28 (`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md`):

> rule 3's question — *"was this reader ever shown able to see a non-zero through
> the real code path?"* — is now the **birth requirement** for every
> reader/comparator: **no instrument grades anything until that answer is yes,
> demonstrated.**

and, in the same message:

> A control defined in terms of the thing it controls is not a control. A planted
> control must travel the real production path — written by the real producer's
> code, read through the real reader … A control that empties the tuple it tests,
> or **writes a schema the producer never emits**, tests nothing and certifies
> blindness.

**That last clause is the one that bites here, and closure's own L-396 is the
precedent for it.** Both comparators' fatal-channel controls write **real files**
and read them back through the **real `parse_log`** — but the *content* is
synthetic, constructed in the comparator's own source. Under the new rule that is
not sufficient. This document supplies what is: **the frozen readers, imported
unmodified, run over real OpenFOAM logs written by real solver runs.**

**Nothing here edits either comparator.** Both are frozen and G2 is mid-compute,
so a grading-path change is barred (rules 2 and 6). This is an **external
demonstration using the frozen reader as-is** — which is what "demonstrated"
requires and all it requires.

Driver: `artefacts/birth_requirement_demo.py`. It imports each comparator's own
`parse_log` and `FATAL_RE`; it **grades nothing** — no functional, no order, no
GCI, no verdict — and **edits nothing**.

---

## 1. `grade_g2.py` — CONFIRMED, before G2 is graded

`artefacts/g2_birth_requirement_2026-08-28.txt`. **1,200 real solver-produced
logs**, read through the frozen reader:

| | count |
|---|---|
| `fatal=True` — **the non-zero, via the real production path** | **35** |
| `fatal=False` | 1,165 |
| refused | 0 |

**Positive direction — the signatures that actually fired on real artifacts:**
`Foam::sigFpe::sigHandler` **32**, `--> FOAM FATAL ERROR` **2**,
`--> FOAM FATAL IO ERROR` **1**. **34 of the 35 lack a clean `End`** — they
really died.

**The 35th is explained, not waved through.**
`certonomous-runs/S1-cbfs-inversion/log.calib` carries an `End` *and* a genuine
fatal. It is a **three-invocation driver log** — 3 `Create time` banners, 2 `End`
lines — whose **first** run died with `--> FOAM FATAL ERROR` at line 48 and
`FOAM exiting` at line 57, after which two further runs completed. A real fatal
and a later `End` legitimately coexist in one concatenated file, so the reader's
`True` is correct. G2 writes one log per level per invocation, so the shape does
not arise for the rung being graded.

**Negative direction — the direction the old clause failed, now on real
artifacts:** **1,036** real logs that **carry the `trapFpe` banner** read
**`fatal=False`**, **1,019** of them with a clean `End`. **The superseded clause
would have called all 1,036 of them fatal.** That is the averted false-positive
count, measured on reality rather than on a fixture.

**Independent ground truth, from another team's committed record.** The reader
flags `verification/runs/DPW8_V2_runs/run_L4_diagA_relax/log.simpleFoam`. That
log's last `Time` is **182** with **no `End`**, and cfd's calibration row `C-4`
independently records that arm as terminating by **SIGFPE at iteration 182 of
600**. A verdict written by a different team, from a different campaign, agrees
with this reader's non-zero. Nothing in closure's registration could have shaped
that.

**And the three logs the rung will actually be graded on:** G2's `L1`, `L2` and
`L3` `log.run` each read **`fatal=False`** with the banner **present**. So the
clause that voided G1 is confirmed silent on G2's own artifacts *before* the
verdict is taken, not after.

## 2. `grade_g1b.py` — CONFIRMED retrospectively

`../G1b_grid_triple_regrade/artefacts/g1b_birth_requirement_2026-08-28.txt`.
G1b's verdict was published **before** this rule existed; it is checked here
rather than grandfathered.

| | count |
|---|---|
| `fatal=True` — the non-zero, via the real path | **33** |
| `fatal=False` | 721 |
| **REFUSED** (`no Time = block`) | **446** |
| negatives carrying the `trapFpe` banner | 679 (662 with clean `End`) |

**G1's own three logs read `fatal=False`**, each with `legacy_hits=1` and
`banner_hits=1` — the infrastructure clause correctly recording one banner match
per level and gating nothing. **G1b's published `NOT A RESULT` therefore rests on
a reader that meets the birth requirement**, and the `DIVERGENT` triple that
produced that verdict is untouched by any of this.

**The 33-versus-35 difference is explained and is a point in G1b's favour.**
G1b's `parse_log` **refuses** a log with no `Time =` block rather than degrading,
so it declines 446 mesh/utility logs that G2's reader tolerates — including the
two non-solver logs that carry two of G2's 35 positives. **35 − 2 = 33.** A
stricter reader seeing fewer positives because it refused the artifacts it was
not built for is correct behaviour, not a shortfall.

## 3. What this does NOT establish

A corpus demonstration proves a reader sees the non-zeros **this corpus happens
to contain**. It does not prove it would see a failure mode absent from 1,200
logs — a `sigSegv::sigHandler`, a `FOAM exiting` without a preceding `FATAL`
banner, or a solver killed by the OOM killer leaving no marker at all. Those
alternatives are in `FATAL_RE` and were exercised **only** by the synthetic
fixtures. **Measured, per alternative, across the 35 real logs the reader flags — counting
PRESENCE, not just the first match, because `FATAL_RE.search()` returns one hit
and would undercount:**

| registered alternative | real logs carrying it |
|---|---|
| `--> FOAM FATAL [IO] ERROR` | 3 |
| `FOAM exiting` | 3 |
| `Foam::sig\w+::sigHandler` | 32 |
| `Foam::error::printStack` | **0** |
| `^Floating point exception` / `^Segmentation fault` | **0** |

**So three of the five registered alternatives are confirmed on real artifacts,
and two — `Foam::error::printStack` and the line-anchored shell death messages —
are confirmed ONLY synthetically.** This document does not claim otherwise, and a
reader should treat those two as untested against reality. Closing that gap is
part of what `RC1` is being registered for.

**A correction against this document's own first draft, recorded rather than
quietly fixed.** It originally read *"three of the seven registered signatures"*.
There are **five** alternatives, not seven, and I had not measured the split when
I wrote it — the numerator was accidentally right and the denominator invented.
It was corrected before this file was committed. **An unmeasured number in a
confirmation record is the same defect the record exists to close**, and it is
disclosed here because that is the standard this session has been holding others
to.
