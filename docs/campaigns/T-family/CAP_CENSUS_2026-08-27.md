# Cap census — has any heat-transfer case ever exceeded a registered cap?

**Answer: no. Not once, in 252 cases, across the whole territory.**
**And the lab's first cap-stop is projected for roughly 32 hours from now.**

Dated 2026-08-27. Ordered by the heat-transfer supervisor after a `CAP_OVERRUN.txt`
miscitation made three completed runs *look* like cap breaches. Territory:
`verification/runs/T-family/`, `verification/runs/THERMAL_K0_runs/`,
`verification/runs/F14-cooling-ladder/`.

**Instrument of record:** `verification/runs/T-family/cap_census_audit.py`.
Every number below is its output. It is not a comparator and grades no row.

---

## 1. The counting rule, stated before the counts

A **case** is a run with a recoverable **measured** cost. Cost is `core_min` from the
record, else `wall × ranks ÷ 60`. **Never a monitor label.**

A **cap** is taken from exactly three places:

1. `<rung>/*_registered.json` → `cases.<case>.cap_core_min`;
2. a launcher-written `cap_core_min` inside the run record;
3. a **per-case** figure transcribed from a pre-registration, each carrying the
   document and line it was read from.

**`CAP_OVERRUN.txt` is never a cap source, and this is the census's founding
measurement.** On 2026-08-27 it was measured quoting a case's **point estimate**
under the word *"registered"* — `T4b_IJ_c`, 710 s = the 11.84 core-min POINT, against
an actual registered cap of **25**. A census built on that label manufactures breaches
out of mispredictions. A queue entry's `cost_core_min_estimate` is excluded for the
same reason.

**Segments sum, they do not max.** A cap binds cumulative spend, so a base run and a
registered extension are added. Within one segment, duplicate records are maxed.

**Aliases fold.** Some rungs record one run twice — at rung level as `STATUS.<case>`,
and inside the case directory under the launcher's internal id. The alias copies carry
no cost. Counting them separately inflated the denominator by 18 and dropped ten real
K0f cases and eight real T5 cases into "no budget instrument at all" — the first draft
of this census got that wrong, and the aliases are folded here.

---

## 2. The zero is controlled

A no-breach finding from a reader never shown able to see a breach is not evidence
(`CLAUDE.md` rule 3). `--selftest` plants known values and refuses unless the reader
discriminates:

| arm | planted | reader | required |
|---|---|---|---|
| control | none | **0 breaches** | 0 |
| breach | `T16_MC_m` ×2.0 → 446.834 vs cap 300 | **FIRED** | FIRED |
| sub-cap | `T16_MC_m` ×1.2 → 268.100 vs cap 300 | **SILENT** | SILENT |

**SELFTEST PASS.** The zero in §3 is a reading, not an absence.

---

## 3. Result

| | cases |
|---|---|
| total | **252** |
| with a registered cap | **52** |
| with none | **200** |
| **breaches** | **0** |
| **timeout-frame breaches** | **0** |
| **source disagreements** | **0** |

**Exceptions table: EMPTY.** Where both a `registered.json` cap and a launcher-written
cap exist they agree exactly, and every cap-to-timeout conversion is exact
(`cap × 60 ÷ ranks`).

### Closest approaches — nothing above 0.84×

| case | actual (core-min) | cap | fraction |
|---|---:|---:|---:|
| `T13_VS_f` | 420.100 | 500.00 | **0.840×** |
| `T16_MC_m` | 223.417 | 300.00 | 0.745× |
| `T4b_IJ_f` | 629.267 | 860.00 | 0.732× |
| `T4b_IJ_m` | 86.300 | 150.00 | 0.575× |
| `T4b_IJ_c` | 14.100 | 25.00 | 0.564× |
| `T8_MTT_f` | 218.350 | 500.00 | 0.437× |

K0f is capped at **rung** level as well: total **2 124.050 core-min** (segment 1
1 378.383 + ext1 745.667) against the registered **CEILING 2 750.70** and the
segment-1 cap 1 745.40 — inside both. The 1 378.383 reproduces the
pre-registration's own stated figure to the digit.

---

## 4. The 200 uncapped, split three ways

A single "UNCAPPED-LEGACY" label would not have been truthful: some of these
registrations carry a real enforcement lever in a vocabulary a `cap_core_min` sweep
cannot see. Measured, not assumed:

| class | meaning | cases |
|---|---|---:|
| **A** | no budget instrument at all — no cost, no cap, no stop threshold | **42** |
| **B** | costed, but nothing that would ever halt a run | **122** |
| **C** | costed **with a stop threshold in non-cap vocabulary** — functionally a cap | **36** |

**Class A (42):** `T1_runs` T1c arm 27 (no cost registration and no pre-registration),
`T9a_runs` 15 (zero cost-bearing lines).

**Class B (122):** `T10aVF` 34, `K0cX` 22, `T1_runs` T1b arm 23, `K0cS` 10, `T3` 9,
`K0cQ` 6, `K0cP` 4, `K0cR` 4, `T10aR2` 3, `K0b_D403_rerun` 3, `K0cG` 2,
`K0b_D406_repair` 2.

**Class C (36)** — each with the line it was read from:

| rung | cases | registered stop |
|---|---:|---|
| `T10a_runs` | 13 | `T10a_PREREGISTRATION.md:375` — *"prediction by more than 10× is stopped and investigated, not waited out"* |
| `T9aH_runs` | 10 | `T9aH_PREREGISTRATION.md:543` — REGISTERED CAP, 3.3× the prediction, **5.00 core-min**, a **rung total** |
| `E4_runs` | 5 | `E4a_PREREGISTRATION.md:337` — *"10× stop-and-investigate threshold: 6.35 core-h"*, per case 10× its predicted |
| `E4a2_runs` | 5 | `E4a2_PREREGISTRATION.md:484` — *"10× stop-and-investigate threshold: 1.8472 core-h"* |
| `T10aR_runs` | 3 | `T10aR_PREREGISTRATION.md:346` — *"The 10× stop-and-investigate threshold is 24.0 core-hours"* |

**C is 36, not a rounding error, and that changes the headline.** "A pre-cap era" is
only half right. There was a real transition around 2026-08-23 — registrations added
before it are uncapped, after it cap-bearing — but **18 % of the uncapped population
already carried a stop threshold**, written as a multiple of the prediction rather
than as a `cap_core_min` field. The finding is better stated as **a pre-cap
vocabulary as much as a pre-cap era**: the enforcement idea existed before the field
did, and a sweep that greps for the word rather than the pattern will under-count the
lab's own governance.

---

## 5. Caveats, stated as caveats

1. **Records with no recoverable cost are excluded from the 252.** Chiefly the
   T10aVF view-factor generator records, written in a one-line format with no `ranks`,
   and `DONE` markers whose whole content is `strict rule met`. All are sub-minute or
   costless; none is capped or gradeable. They are not counted as cases and are not
   claimed as compliant.
2. **The sweep reads RECORDS, not SOLVERS.** A run that has produced no `STATUS` and
   no `DONE` is invisible to it by construction — which is exactly why the two live
   solvers, `T3_R_ff` and `T15_UP_f`, appear nowhere in the 252.
3. **K0f is compared at rung level** where its cap is registered at rung level, and
   per case where the pre-registration gives per-case figures. Both are reported;
   neither is derived from the other.

---

## 6. The first cap-stop is ahead of us, not behind

`T3_R_ff` — 8 ranks, cap **27 400 core-min**, timeout 205 500 s. At 21:37Z on
2026-08-27 it stood at **11 886 core-min** and iteration **50 529 of 118 000**. It
needs **1.7245 s/iteration** to finish inside the cap and is measuring **1.76–1.85**
across every window. It is projected to be **stopped by the cap at ~97–99 % of
`endTime`**, around **2026-08-29T05:56Z**, and the row would then be
**`NOT A RESULT` on a registered cap**.

So the honest form of this census's answer is: **a registered cap has never yet bitten
in this territory — and one is about to.**

---

*Instrument: `verification/runs/T-family/cap_census_audit.py` (`--selftest` before
belief). No ledger row is written from this census; a breach row, had there been one,
would need the supervisor's ruling first. No legacy case is re-registered: rule 12
binds from registration forward.*

---

# ADDENDUM 1 — 2026-08-27. Supervisor rulings; two defects the next auditor inherits.

**No count, class, verdict or figure in §1–§6 changes.** The body above already
carries the corrected **252**, the A/B/C counts **42 / 122 / 36**, and the
*"pre-cap vocabulary as much as a pre-cap era"* headline; that was verified against
this file's HEAD blob before this addendum was written, rather than assumed.
**Lines whose number changed above this section: 0**, verified by byte-prefix in the
commit's own invocation.

## A1.1 The headline is adopted, and the earlier figure is withdrawn

The supervisor predicted class C would be small and class A the core of the finding,
**and recorded that he was wrong by a wide margin.** The governance gap is
**A = 42**, not 200 and not the ~208 first reported upward — an overstatement of
**4.8×**. That figure is withdrawn here so a later reader cannot cite it. A census
whose own headline overstates the gap flatters nobody and is still wrong.

`T10a_PREREGISTRATION.md:375` — *"prediction by more than 10× is stopped and
investigated, not waited out"* — is the stop threshold neither the lane nor the
supervisor had seen, and it covers **13 cases on its own**.

## A1.2 Two defects that corrupted the first pass — inherit these before re-running

Both were found by **reading the residual class-A membership instead of trusting the
count.** That is the method; the counts themselves looked entirely plausible while
both defects were live.

**1. Segments were maxed, not summed — the more dangerous of the two.** A cap binds
**cumulative** spend, so a base run and a registered extension must be **added**.
Taking the maximum understated `K0f/M1_f` as 290.800 core-min when it is
290.800 + 167.133 = **457.933**. On this corpus nothing was near a cap either way, so
the error changed no verdict — **but on a corpus where something was, this defect
hides a real breach and reports a clean census.**

**2. Aliases were counted as cases — the more generalisable.** Some rungs record one
run **twice**: at rung level as `STATUS.<case>`, and again inside the case directory
under the launcher's internal id (`T5_C`, `K0f_EXT_M1_c`). The alias copies carry no
cost. **A single defect corrupts numerator and denominator in opposite directions:**
it inflated the total by 18 *and* dropped ten real K0f and eight real T5 cases into
"no budget instrument at all". The first draft's A = 70 was wrong for that reason.

> **Standing rule for any future census over this corpus: DE-ALIAS FIRST, and SUM
> SEGMENTS, before any count is read.** `cap_census_audit.py` does both; a
> hand-rolled sweep will do neither.

A third, smaller defect is recorded for the same reason: ten K0f citation line numbers
were off by one (fixed at `9c4ed59a`). It was caught by **generating** the
side-by-side evidence from the module and re-reading each cited line **from disk**,
rather than typing it. A landed instrument whose citation points one line off its
number is the `CAP_OVERRUN.txt` failure in miniature — which is why this census exists.

## A1.3 The prose-only caps are now machine-readable

The 28 caps that existed only as prose have been transcribed into sidecars beside
their runs, each stating **that the prose is authoritative and the sidecar is a
derived transcription — if they ever disagree, the prose wins**:

| rung | sidecar | entries |
|---|---|---|
| K0f | `verification/runs/F14-cooling-ladder/K0f_runs/K0f_CAPS_TRANSCRIBED_2026-08-27.json` | 10, `scope: case` |
| T5 | `verification/runs/T-family/T5_runs/T5_CAPS_TRANSCRIBED_2026-08-27.json` | 8, `scope: case` |
| T9aH | `verification/runs/T-family/T9aH_runs/T9aH_CAPS_TRANSCRIBED_2026-08-27.json` | **1, `scope: rung`** |

**T9aH is transcribed at RUNG scope and was neither split nor dropped.** Its 5.00
core-min is registered directly under `REGISTERED TOTAL PREDICTION`, so it governs the
rung total; dividing it across ten cases would be a guess, and a guessed cap is worse
than a missing one. Dropping it, which this lane first proposed, would have left a
rung that *is* budgeted indistinguishable from one with no budget instrument at all —
the exact confusion this census exists to remove. **No count in §3 or §4 moves:** K0f
and T5 were already counted capped through the same prose figures, and T9aH remains
class C.

*Ruled by the heat-transfer supervisor `[lab-attributed]` 2026-08-27; drafted by a lab
lane. Sidecars at `e31d3d77`, `d57fa35e`, `2a90d2c8`.*
