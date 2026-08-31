# OPEN INSTRUMENT DEFECTS — T-family, boarded 2026-08-31

**Status: OPEN. This document RECORDS; it REPAIRS NOTHING.** No frozen file was
edited to produce it, no rung was re-graded, no verdict is asserted wrong. Its
whole purpose is that a successor can pick these three up **without re-deriving
them**, and that nobody has to rediscover the retraction in the closing
paragraph.

**Disposition is not this lane's and not this document's.** Findings 1 and 3 both
touch records that carry, or are blocked from carrying, graded verdicts; where a
ruling is owed it is owed by heat-transfer's supervisor and by verification, not
by the record below.

**Verification standard used here.** Every claim below was checked at its own
source in this session. Where a claim is **cited** from an earlier artifact
rather than re-measured, it says so in those words. Nothing cited has been
promoted to a measurement.

---

## FINDING 1 — A REGISTERED ARTIFACT THAT NO CODE EVER WRITES

**Class:** dead lever — a registered instrument connected to nothing. The class
`DEAD_LEVER_AUDIT.md` is named for.
**Rung:** T23, `T23_P305_U{10,20,30,40}`.
**Reproduced at source this session: YES, all three limbs.**

### The registered text

`docs/campaigns/T-family/T23_PREREGISTRATION.md` §5.4, lines 665–670, verbatim:

> **REGISTERED, one-way and before the fact: a run whose recorded load average at
> launch shows a saturated box produces a COST but NOT a calibration row.** After
> the fact a contended number is indistinguishable from a mispredicted one, and
> the temptation is then to attribute the whole gap to whichever term is under
> discussion. Each launcher writes a `START.<case>` file **before** the solver
> starts, carrying `start_utc`, all three `/proc/loadavg` windows and `nproc`.

### What is actually there

1. **No launcher writes one.** The four `run_t23.sh` copies
   (`verification/runs/T-family/T23_runs/T23_P305_U{10,20,30,40}/run_t23.sh`; four
   distinct md5s, checked individually, not assumed identical) contain **no**
   `START`-writing code, no `/proc/loadavg` read, no `nproc` call, and no
   `start_utc` capture. The **only** occurrence of the string `START` in any of
   the four is at **line 86**, inside the `STATUS.$NAME` here-block written
   **after** the solver returns:

   `echo "note=core_min is CONTENDED -- see the load average recorded in START.$NAME"`

   That is a **pointer to a file the same script never creates** — the sharpest
   form of the defect, because the record it produces cites the missing artifact
   by name.
2. **No such file exists on disk.** `find` over
   `verification/runs/T-family/T23_runs` returns **zero** `START.*` entries.
   Directory listings of all four case directories confirm it case by case.
3. **The lever was later wired, in the successor rung.** `START.<case>` files
   **do** exist under `verification/runs/T-family/T24_runs/` (e.g.
   `T24_P080_U20/START.T24_P080_U20`, `T24_P155_U30/START.T24_P155_U30`,
   `T24_P230_U40/START.T24_P230_U40` and their siblings). This is stated because it
   bounds the defect — **T23's launcher, not the family's convention** — and
   because it means a successor comparing the two rungs will find the wiring, not
   a design gap.

**Planted-zero discipline on limb 2.** The `find` that returns zero `START.*`
under `T23_runs` is the *same* invocation, same pattern, same tree root, that
returns the non-empty `T24_runs` list quoted above. The reader was therefore
shown able to see a non-zero before its zero was believed.

### What rests on it, stated precisely

`docs/campaigns/T-family/T23_RESULTS.md` carries **four PASS verdicts** (§ the
verdict table, rows `T23_P305_U10` … `U40`, at 103.6078 / 69.0098 / 55.4389 /
47.8448 °C), and §6 of that record discharges rule 12's cost calibration. §5.4's
saturation clause is a **one-way precondition on the calibration row** — a
saturated box yields a cost but no calibration row. That precondition could not be
evaluated from the instrument the registration named.

**The substitution, recorded plainly.** The contention reading the graded record
actually rests on came from a **different artifact**: the queue runner's own
`verification/queue/runner.log`, lines **8476–8483**, which record box state at
each of the four launch instants —

| case | launch (UTC) | box busy | cores busy |
|---|---|---:|---:|
| `T23_P305_U10` | 2026-08-31T17:33:02Z | 11.9 % | ~1.9/16 |
| `T23_P305_U20` | 2026-08-31T17:34:07Z | 12.7 % | ~2.0/16 |
| `T23_P305_U30` | 2026-08-31T17:35:12Z | 22.3 % | ~3.6/16 |
| `T23_P305_U40` | 2026-08-31T17:36:17Z | 25.7 % | ~4.1/16 |

Read at source in `verification/queue/runner.log` this session; the same lines
carry `prereg=fe666fd5` against each launch.

**The substitution is already disclosed by the graded record itself.**
`T23_RESULTS.md` §5.2 (lines 302–330) states the absence, states that
`run_t23.sh` contains no code to write one, names the substitute artifact, and
reproduces the same four readings. **This finding is therefore not a concealment
and is not reported as one.** What remains open is the **instrument**: a frozen
registration names a file that no code in the lab writes for that rung, and the
rung it sits in carries PASS verdicts.

### What this finding does NOT say

It does **not** say the four PASS verdicts are wrong — the substitute reading is
recorded, is well under saturation at its worst (25.7 % of 16 cores), and the
verdicts may well be entirely fine. It does not re-grade. It does not propose a
retro-fit of the launcher (rule 6: the frozen document is not edited, and the
launcher that ran is the launcher that ran). **The disposition — whether a dead
registered lever in a rung carrying PASS verdicts needs anything beyond the §5.2
disclosure already on record — belongs to heat-transfer's supervisor and to
verification.**

---

## FINDING 2 — T15's SELFTEST ARM IS GREEN FOR THE WRONG REASON

**Class:** a green limb that proves nothing — the class T16c's L30 repair was
made for.
**Rung:** T15.
**Status: mechanism REPRODUCED at source by reading. The printed `ok` string is
CITED-NOT-REPRODUCED — the comparator was NOT run.**

### Why the comparator was not run

Running a selftest in this family produces side-effect artifacts (T18 has a whole
incident record and two `..._SIDE_EFFECT_NOT_A_GRADE_...` files to prove it), and
**T15 has never been graded**. This lane did not run `analyse_t15.py`. Everything
below is read from source text and from the one grading output already on disk.

### The arm

`verification/runs/T-family/T15_runs/analyse_t15.py`, unit (vii), lines 915–923:

```
    # (vii) the live tree without a DONE marker refuses
    fired = False
    try:
        grade(HERE, os.path.join(tempfile.gettempdir(), "t15_never.json"), reg)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] live tree, no DONE marker -> exit 2 REFUSE" % ("ok " if fired else "FAIL"))
```

Line 918 is the `grade(HERE, ...)` call. `HERE` is
`os.path.dirname(os.path.abspath(__file__))` (line 43) — the **live**
`T15_runs` directory.

### Why it cannot be testing what it names

The clause the arm names is `grade()`'s first act,
`analyse_t15.py:548–549`:

```
    if not os.path.isfile(os.path.join(root, "DONE.%s" % CASE)):
        refuse("no DONE.%s -- mark_done_t15.py rules and the rung is graded only after it" % CASE)
```

**`DONE.T15_UP_f` EXISTS in that directory** — `verification/runs/T-family/T15_runs/DONE.T15_UP_f`, 5 bytes, mtime 2026-08-28 16:03 [MEASURED, directory listing this session]. The
live tree therefore **has** a DONE marker, and the clause at :549 **cannot**
fire. The arm's stated precondition — "the live tree **without** a DONE marker" —
is false of the tree it is pointed at.

`grade()` proceeds past :549 to the planted-zero control block (S1 at
`analyse_t15.py:706`), and **that** is where the refusal comes from — see
Finding 3, whose refusal line is on disk and dated the same minute as the DONE
marker. The arm sets `fired = True` on any `EXIT_REFUSE` (`EXIT_REFUSE = 2`, line
51) **without discriminating which conjunct raised it**, so it prints `ok` on a
refusal it did not cause and does not name.

**What is measured vs cited, exactly.** The DONE marker's existence, the :548
clause, the :918 call, the undiscriminating `fired` assignment and the S1 refusal
on disk are all **measured** this session. The claim that T15's arm **printed
`ok`** in an earlier run this session is **cited from that earlier reading, not
reproduced here** — reproducing it would require running the comparator, which
this lane declined for the reason above. The mechanism does not depend on that
citation: given a DONE marker present and a refusal firing downstream, `ok` is the
only string the code can print.

### Why this is worse than T18's honest failure

T18's equivalent arm — `analyse_t18.py:509`, same `grade(HERE, ...)` construction
— reports **`16 ok / 1 FAIL (unit (v), live-tree arm, EXPECTED-INVERTED)`**
[CITED, from `verification/runs/T-family/T18_runs/T18_SELFTEST_INCIDENT_RECORD.md:110`,
`T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.txt:39` and
`T18_GRADE_OUTPUT_20260831T151113Z.txt.NOTE.txt:15`; that incident record itself
states at its line 165 that the count was cited from the two 2026-08-31 notes and
not re-measured, and **that chain is passed on unshortened rather than presented
as a fresh measurement**]. T18's limb is **visibly** inverted: it is red, it is
labelled, it has an incident record and a readiness audit beside it. A reader
cannot miss it.

T15's reports **green** and is silently testing nothing. **A red arm that is
wrong costs a reader one minute; a green arm that is wrong costs a reader
nothing, and that is the problem** — it is never read at all.

This is the class T16c's L30 repair exists for, and `analyse_t16c.py:1662–1699`
states the class in its own docstring: L30's original control truncated
`log.solve` instead of removing one line, so the refusal came from the
`ExecutionTime` count conjunct at `:515` while the `End`-line conjunct at `:511`
that **L30 names** was never exercised — *"MEASURED consequence: mutation M31,
which disables :511 exactly, left L30 GREEN — the limb had no control that
reddened it."* The repaired form reads the file back and refuses unless the edit
planted exactly what it claims. **Same class, different rung, still open in
T15.**

---

## FINDING 3 — T15 CARRIES AN OPEN, UNRELATED PLANTED-ZERO DEFECT, AND IT — NOT THE SELFTEST ARM — IS WHAT BLOCKS THE RUNG

**Class:** planted-zero control refusal (standing rule 3).
**Rung:** T15.
**Reproduced at source this session: YES.**

### The refusal

`verification/runs/T-family/T15_runs/T15_GRADE_OUTPUT.txt` (mtime 2026-08-28
16:03) ends with, verbatim:

> `REFUSE: planted-zero control S1(FLUCTUATION): a CONSTANT offset of one mean moved sigma/mean by 9.95e-05 -- a working fluctuation reader must be nearly blind to a constant offset; this one is not`

**9.95e-05** is the measured figure, read from that file this session. The three
controls **above** it in the same file — `w_axis(POINT)`, `T_axis(POINT)`,
`b_th(INTEGRATING)` — all record **PASS** with recovered plants, so the refusal is
not a blanket instrument failure and the reader was demonstrably able to see a
non-zero on three of four channels before refusing on the fourth.

### The consequence

**T15 has therefore NEVER produced a verdict.** The comparator exits at
`EXIT_REFUSE` before grading. Corroborating absence, measured: `T15_runs`
contains **no** `gate_t15.json` — its only `.json` is `T15_registered.json`, the
registration input. (Contrast `T18_runs`, which does carry `gate_t18.json`; the
same listing that shows T15's absence shows T18's presence, so the absence is a
reading, not a blind glob.)

**It is this defect, and not Finding 2's selftest arm, that blocks the rung.**
Repairing the arm would leave T15 exactly as ungraded as it is now. A successor
who fixes Finding 2 first will have fixed the one of the two that changes
nothing.

### The rule-2 consequence, stated honestly — "never graded" is NOT "never ran"

**T15's case HAS run.** `verification/runs/T-family/T15_runs/STATUS.T15_UP_f`
records `rc=0`, `wall_s=71749`, `ranks=1`, **`core_min=1195.817`**,
`capped=no`, `note=clean`, `started_utc=2026-08-27T08:57:37Z`,
`ended_utc=2026-08-28T04:53:26Z`, solver `buoyantBoussinesqPimpleFoam`. The case
directory `T15_UP_f/` carries time directories `60 120 180 240` against
`endTime 240` in its own `system/controlDict` — i.e. **240 s of simulated time**,
bought with **1195.817 core-minutes** of wall. (The two numbers are stated apart
deliberately: 240 is the solver's end time, not its cost.)

**First compute therefore happened on 2026-08-27, and gates closed then.** A
change to `analyse_t15.py` to cure the S1 control is a **POST-COMPUTE INSTRUMENT
CHANGE**. It is **not** a free pre-compute fix, and rule 2's pre-compute
amendment limb does **not** apply to it. It takes the route T20's builder repair
took: `VERIFICATION_CHARTER.md` §2d.1's four-condition repair exception, which
for T20 was **granted** at §2d.3 (charter v1.36, 2026-08-31, line 4363).

Two notes for whoever walks that route, both restraints rather than permissions:

* T20's grant turned on `mutation_controls_t20c.py` being an **independent
  instrument that grades nothing**, driven by the ruling supervisor rather than
  trusted from its commit message (charter line 4383). T15 would need its own
  equivalent, not a borrowed one.
* §2d.3 **narrowed** conditions (3) and (4) for T20 because T20 had published no
  numbers; the narrowing permits discharging them by **disclosing a measured,
  named absence**, never an asserted one (charter line 4395). T15 is
  *superficially* similar — it too has published nothing — **but T15 has spent
  1195.817 core-minutes where T20 had zero graded solves**, so the two are not
  the same posture and the narrowing must be argued for T15 on T15's facts, not
  inherited. **That argument is verification's to hear and is not made here.**
  Note also the charter's own closing restraint on the T20 grant (line 4407): *a
  §2d.1 grant removes a legal obstacle; it is not a budget, not a launch order,
  and not a verdict.*

---

## CONTEXT A SUCCESSOR NEEDS — THE `grade(HERE, ...)` CENSUS, AND A RETRACTION THAT MUST TRAVEL WITH IT

The `grade(HERE, ...)` construction across the T-family is **25 textual
occurrences** in Python sources, of which **6 are EXECUTABLE calls** and **1 is
commented out**; the remaining 18 are prose in docstrings, comment blocks and
mutation-control strings that quote the construction rather than perform it
[MEASURED this session, `grep -rn --include=*.py "grade(HERE"` over
`verification/`, `docs/`, `scripts/` — enumerated, not counted from a summary].
The six executable calls are `analyse_t15.py:918`, `analyse_t14.py:468`,
`analyse_t18.py:509`, `analyse_t19.py:691`, `analyse_t17.py:616` and
`analyse_t9aR1b.py:367`; the commented-out one is `analyse_t19b.py:898`. **All six
pass `os.path.join(tempfile.gettempdir(), "<rung>_never.json")` as their
`json_out`** — visible in the call text of each. **An earlier alarm in this lab
described this class as a live-tree WRITE** (the wording survives at
`analyse_t20.py:1435` and `analyse_t16c.py:142`, "fired on its own LIVE tree and
produced a file"); **that characterisation was wrong and was retracted.** The
corrected finding, stated here so the retraction travels with the record: the
**root** argument is the live tree, so these calls **read** live directories, but
the **output** goes to `gettempdir()`, so **no live-tree write occurs**. The
class is a **DEAD CONTROL ARM** — an arm whose named precondition is not true of
the tree it is aimed at, so it passes without testing its clause — and **NOT
live-tree contamination.** Anyone re-raising it as a contamination alarm is
re-raising a retracted claim; the live defect is Finding 2's, and it is about
what the arm proves, not about what it writes.

---

## FOR THE SUCCESSOR — WHAT IS OPEN, IN ONE LINE EACH

| # | Rung | Open item | Blocks | Route |
|---|---|---|---|---|
| 1 | T23 | `START.<case>` registered at §5.4, written by nothing; substitute reading used and disclosed at `T23_RESULTS.md` §5.2 | nothing that is not already disclosed; four PASS rows stand as recorded | supervisor + verification disposition; **no edit to the frozen registration or the launcher** |
| 2 | T15 | selftest unit (vii) at `analyse_t15.py:918` prints `ok` on a refusal from S1, not from the DONE clause it names | nothing — repairing it alone changes no verdict | post-compute instrument change, §2d.1 route; **do this second** |
| 3 | T15 | planted-zero control S1(FLUCTUATION) refuses at 9.95e-05 | **the whole rung — T15 has never produced a verdict** | post-compute instrument change, §2d.1 route, on T15's own facts; **do this first** |

**None of the three was closed in this session, and none is repaired by this
document.**
