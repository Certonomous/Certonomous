# REFERRAL TO THE VERIFICATION TEAM — SUB-SECOND TIMESTAMP TRUNCATION IN dafoam AGE GUARDS

**From:** dafoam (lane, on the dafoam-supervisor's brief) · **To:** verification-supervisor
**Date:** 2026-09-06 · **Status:** REFERRED, not ruled. Nothing here is a verdict.
**Internal to the box.** SUBMISSIONS ARE PARKED (`CLAUDE.md` rule 7); this document is a
referral between two lab teams and is neither a filing nor a send.

**Two petitions, and they are separable.** Petition 1 asks for one narrowly-scoped
`§2d.1` grant on a repair that has already been made and that costs nothing to hold.
Petition 2 asks a question about a population of 75 comparisons that dafoam cannot answer
on its own authority. **Petition 2 is the one that matters.** If verification reads only
one, read the second.

---

## 0. THE SHORTEST STATEMENT OF THE PROBLEM

`CLAUDE.md` rule 4's age guard exists so that a field the run did not produce cannot be
graded as one it did. The guard compares two file modification times. **The Linux kernel
records mtime to the nanosecond. Every dafoam age datum is taken to the whole second.**

The two predicates therefore disagree inside a window up to **1.000 s** wide, and which
way they disagree depends on **which side was truncated** and on **whether the predicate
being true means ACCEPT or REFUSE** — not on the comparison operator, which is what a
reviewer's eye goes to.

Both directions have now been **measured on the same real run**, four seconds of wall
clock apart:

| | site | direction | consequence |
|---|---|---|---|
| the launcher | `w3s_stage_and_run.sh` (pre-repair) | **FAIL-CLOSED** | a false **refusal** — loud, cheap, self-announcing |
| the recorder | `w3s_stage_record.py:411` | **FAIL-OPEN** | a false **acceptance** — silent, and the record looks right |

**A guard that fails open is worse than no guard, because the record then carries a claim
that a check was performed.**

---

# PETITION 1 — A `§2d.1` EXCEPTION FOR THE W3S LAUNCHER REPAIR

## 1.1 What happened, measured

W3S launched **2026-09-06T02:50:52Z** and refused with `launcher_rc=2`.

- **Cost: 0.9000 core-min, 54 wall s, ZERO solver iterations.** Ledger line, at
  `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3S-GSCAN-cylinder-unsteady/ledger.txt`:
  `LEG=SETUP rc=2 wall_s=54 ranks=1 core_min=0.9 declared=4 executed=3 blocked=0`.
  The three executed stages cost 0.0667 + 0.2833 + 0.5500 = **0.9000 core-min**, all on
  the `SETUP` leg.
  *(The brief that dispatched this lane said 57 s; the ledger and the manifest both say
  54. The ledger is the artefact and it is what this document quotes.)*
- The refusal named `S2a/system/controlDict` as **post-dating** the age sentinel.

**The refusal is false, and the arithmetic is not arguable.** Full-precision mtimes, read
off disk with `stat -c '%.9Y'` on 2026-09-06:

```
.w3s_age_ref.SETUP_S2a    1788663109.804247776    <- the sentinel
S2a/system/controlDict    1788663109.683474790    <- the accused file
```

**The accused file is 120.772986 ms OLDER than the sentinel that accused it.**

## 1.2 The mechanism

`run_stage` took its age datum with `stat -c %Y` — **whole seconds** — and then tested with
`find -newermt "@$AGE_DATUM"`, which means *strictly after `N.000000000`*. So every file
staged in the **same wall-clock second** as its sentinel was accused of post-dating a
sentinel it precedes. **The two predicates differ over a window 804.247776 ms wide** on
this stage — the sentinel's own sub-second offset.

S0, S1a and S1b passed only because their sentinels happened to straddle a second
boundary (`.080769`, `.187812`, `.109963`). S2a's did not. **This was a race, and
re-firing unrepaired would have been a lottery** at whichever stage next landed inside
one second of its sentinel.

## 1.3 The repair, and how it was driven

Committed at **`5d5c3281`** (`cases/dafoam/curriculum_D12R2/w3s_stage_and_run.sh`,
25 insertions / 3 deletions, one file):

```
POSTDATING="$(find "$D" -type f -newer "$SENTINEL" 2>/dev/null | head -5)"
```

`-newer FILE` compares full-precision mtimes directly and truncates nothing. It is
**strictly more faithful** to the condition the launcher **registered** at `:125-126` and
`:1190` — *"NOTHING STAGED MAY POST-DATE THE DATUM"* — than the condition it
**implemented**, *"nothing staged may fall in the same second as the datum or later."*

Driven **both ways** through the production text, on a replica whose nanosecond mtimes
were first proven identical to the real ones:

- **LIMB 1** — the real staged S2a tree → `rc=0`, **passes**. The false accusation is gone.
- **LIMB 2** — a plant at sentinel **+1 ns** → `rc=2`, **refuses**. Also caught at +100 ms
  (same second) and at +10 s.

Launcher selftest **53/53 before and after** (`w3s_chain_driver.sh:292` names the 53
controls). **A repair that cannot be shown to fail is not shown to work**, and this repair
is permissive in direction — it turns a REFUSE into a RUN — so the refusing limb is the
one that carries the weight.

## 1.4 The four conditions of `§2d.1`, answered

`§2d.1` (`VERIFICATION_CHARTER.md:1936-1942`) permits a change on the grading path after
the first graded solve when, and only when, all four hold.

**A lane has already answered these and found all four met. This lane reproduces that
analysis, including the correction it made to the supervisor's own framing.**

**(1) A DEMONSTRABLE ERROR, not a preference — HOLDS.** The guard does not test the
condition it registered. The registered condition is *post-dates*; the implemented
condition was *falls in the same second or later*. A file 120.772986 ms older than the
sentinel was refused for being newer. That is not a preference between two defensible
readings; it is one reading and one arithmetic mistake.

> **THE CORRECTION.** The supervisor's framing grounded the petition on condition (1),
> and condition (1) does hold. **But the weight-bearing limb is not (1) — it is the
> zero-graded-solves narrowing, and without it conditions (3) and (4) have no object.**

**W3S produced ZERO graded solves.** Verified on disk and at HEAD:
`manifest.jsonl` holds **exactly 3 rows** — S0, S1a, S1b — and **all three carry
`cost_leg=SETUP`**. There is no grader output, no results file, and no graded row anywhere
in the run tree or at HEAD. The single JSON artefact in the tree, `S1b/d12y_S1b.json`, is
a SETUP-leg staging product, not a graded solve.

This is the shape verification has already ruled on twice, and the ruling is quotable:
`§2d.3` (v1.36, 2026-08-31, `VERIFICATION_CHARTER.md:4391`) — *"Conditions (3) and (4)
PRESUPPOSE PUBLISHED NUMBERS. §2d.1 was cut for K0cS, where a wall integral had been
published and was wrong by 10–27 %; 'quantify what moved' and 'record the pre-repair
values' both assume values exist. T20 has NONE — zero graded solves, nothing published."*

**(2) AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS, one that grades nothing — HOLDS, and
this is the load-bearing condition `§2d.1` itself names.** The instrument here is **the
filesystem's own nanosecond mtime field**. It is a kernel clock reading. It is not written
by anyone being audited, it grades nothing, it carries no verdict, and **it cannot have
been selected to move a verdict in a wanted direction because it does not know which
direction that is.** `§2d.1:1944-1946` is explicit that this is the property the exception
is cut around.

**(3) DISCLOSURE, NAMING THE INSTRUMENT, QUANTIFYING WHAT MOVED — HOLDS, NARROWED.**
The repair commit discloses the defect, names the instrument, and quantifies the
discrepancy to the nanosecond. **What moved is a refusal, not a number**, because there is
no number: zero graded solves.

**(4) PRE-REPAIR VALUES RECORDED BESIDE THE PUBLISHED ONES — HOLDS VACUOUSLY, NARROWED.**
**The pre-repair state is a refusal, not a value.** Nothing was published, so nothing
published can move. The refusal itself is recorded verbatim, with its cost and its rc, in
the run's own ledger and in `5d5c3281`.

## 1.5 THE SECOND, INDEPENDENT GROUND — which may be cleaner than the exception

**The repaired value may not be on the grading path at all.** `POSTDATING` is read at the
two lines immediately below its assignment and **nowhere else**. It feeds **no manifest
row** and **produces no number**. The row's own field, `age_staged_postdating`, is
**recomputed independently** by `w3s_stage_record.py:529` from the stage directory and the
datum, and is **not touched** by this repair.

If verification takes that view, `§2d` never engaged and no exception is needed. **dafoam
does not assert this; it offers it.** It is the ground `§2d.11.2` was granted on for T5c —
*"GRANTED, ON A GROUND THE PETITION DID NOT LEAD WITH"* (`VERIFICATION_CHARTER.md:5219`).

## 1.6 WHY THIS IS REFERRED AND NOT RULED

**A lane cannot grant itself a `§2d.1` exception.** Both standing precedents — **T20**
(`§2d.3`, v1.36) and **T5c** (`§2d.11`, v1.45) — were **ruled by verification on
referral**, and in the T5c ruling verification recorded that reading the source itself
rather than the petition's summary **changed the ruling twice**, once against the
petitioner. **The dafoam-supervisor declines to be the first to skip that step.**

**And it costs nothing to wait.** This session is **denied queue access**, so the W3S
re-fire is blocked on permission regardless of how this petition is ruled. There is no
compute waiting on the answer.

**What is asked:** a ruling that the `5d5c3281` repair is legal — either as a `§2d.1`
grant on the narrowed conditions, or on the §1.5 ground that it was never on the grading
path. **No compute is requested and no budget is sought.** Per `§2d.3.5`: *"A `§2d.1`
grant removes a legal obstacle; it is not a budget, not a launch order, and not a verdict."*

---

# PETITION 2 — THE CENSUS. THIS IS THE ONE THAT MATTERS.

## 2.1 LEAD WITH THE MEASURED SPECIMEN: A FALSE NEGATIVE IN A LANDED RECORD

Not a hypothetical. On the **real W3S run**, in the **manifest row that was written and
kept**:

Stage **S1a**, sentinel `.w3s_age_ref.SETUP_S1a` at `1788663058.187812489`, recorded
datum `1788663058`.

| file | mtime | delta vs sentinel | in the row's `age_staged_postdating`? |
|---|---|---|---|
| `system/fvSolution` | `1788663058.546232099` | **+0.358420 s** | **ABSENT** |
| `system/fvSchemes` | `1788663058.544477064` | **+0.356665 s** | **ABSENT** |

Both files **genuinely post-date the datum**. The row lists 12 post-dating files and
**misses these two**. Re-derived independently by this lane by walking the stage directory
and comparing full-precision mtimes against the sentinel: **14 files truly post-date, 12
are listed, 2 are missed.** S0 (10/10) and S1b (24/24) are complete; only S1a's sentinel
fell such that the window bit.

The mechanism is two lines of `w3s_stage_record.py`:

```
406:    datum = int(datum)
411:            if int(os.path.getmtime(p)) > datum:
```

**Both sides floored, and the predicate is `>` with TRUE meaning "post-dating, flag it".**
A file inside the same second as the sentinel floors onto the datum, `>` is false, and the
file is silently not flagged.

**The record carries a claim that a check was performed. The check missed two files.**

## 2.2 THE POPULATION

**75 material truncated timestamp comparisons across 39 dafoam files — 55 fail-open, 20
fail-closed. 35 of the 39 files have their current bytes md5-pinned in a committed
pre-registration.**

Derived by this lane from its own instrument, not transcribed:

| quantity | count |
|---|---|
| tracked `.py`/`.sh` files at HEAD scanned | **2,361** |
| genuine file-mtime comparisons found | **355** in **235** files |
| truncated on at least one side | **89** in **45** files |
| — of those, in `cases/dafoam/` | **80** in **40** files |
| — of those, **material** (see §2.6) | **75** in **39** files |
| direction: **FAIL-OPEN** | **55** |
| direction: **FAIL-CLOSED** | **20** |
| `round()` or `ceil()` on a timestamp anywhere in the tree | **0** |

**Every dafoam file carrying a truncated comparison is a grading-path file** — a
`*_grade.py`, a stage/run launcher, a reader, or a datum control. There are no test
fixtures or utilities in the 39.

## 2.3 THE MECHANISM — THE TRANSFERABLE PART

**The datum is FLOORED in every instance found. Never rounded, never ceiled.** Three
idioms, all producing a floor:

1. `AGE_DATUM=$(stat -c '%Y' "$REF")` in the launcher — integer seconds by construction.
2. `datum = int(open(p).read().strip())` in the grader — reading back what the launcher
   wrote.
3. `fh.write("%d\n" % datum)` — the floor at the serialisation step.

Worked end to end on one arm, and it crosses a file boundary:

```
so1a_run_arm.sh:317    AGE_DATUM=$(stat -c '%Y' "$WORK/$DATUM_NAME")   <- THE FLOOR
so1a_run_arm.sh:318    echo "$AGE_DATUM" > "$WORK/.so1a_age_datum"
so1a_grade.py:346      datum = int(open(p).read().strip())             <- THE READ
so1a_grade.py:326      if on_disk < datum:  refuse(...)                <- THE COMPARISON
```

**Flooring moves the datum EARLIER.** Every guard in the family reads some form of *"the
artefact must be newer than the datum."* **An earlier datum relaxes it.** The widest
admitted staleness is the sentinel's own sub-second offset — **up to 0.999 s**.

## 2.4 THE COROLLARY VERIFICATION WILL CARE ABOUT MOST: **OPERATOR POLARITY DOES NOT GIVE THE DIRECTION**

This lane did not argue this. It **swept it**: for each operator and each combination of
truncated sides, sub-second offsets were enumerated and the truncated predicate compared
against the exact one, recording whether a **false positive** (predicate true when it
should be false) or a **false negative** is possible.

**With the datum floored — which is every dafoam instance:**

| operator | artefact side | can produce FALSE POSITIVE | can produce FALSE NEGATIVE |
|---|---|---|---|
| `a >  d` | exact | **yes** | no |
| `a >  d` | **floored** | no | **yes** |
| `a >= d` | exact | **yes** | no |
| `a >= d` | **floored** | **yes** | no |
| `a <  d` | exact | no | **yes** |
| `a <  d` | **floored** | no | **yes** |
| `a <= d` | exact | no | **yes** |
| `a <= d` | **floored** | **yes** | no |
| `a == d` | exact | **yes** | **yes** |
| `a == d` | **floored** | **yes** | no |
| `a != d` | exact | **yes** | **yes** |
| `a != d` | **floored** | no | **yes** |

Read together with whether TRUE means ACCEPT or REFUSE, this table gives the direction.
**Two sites in this tree use the same operator and fail in opposite directions:**

- `so3_grade.py:1104` — `if amt <= datum: refuse(...)`. `amt = int(getmtime(art))`, datum
  floored. **Both sides floored, `<=`, TRUE = REFUSE** → can only over-refuse →
  **FAIL-CLOSED**. An artefact 0.3 s genuinely newer than its sentinel floors onto it and
  is refused as stale.
- `so1a_grade.py:326` — `if on_disk < datum: refuse(...)`. Both sides floored, **`<`**,
  TRUE = REFUSE → can only under-refuse → **FAIL-OPEN**. An artefact 0.3 s genuinely
  *older* floors onto the datum and escapes the refusal.

**Same shape, same both-floored operands, adjacent ladders — opposite failure directions,
and the only difference is the `=` in the operator.** And the launcher/recorder pair in
§0 differ on the *other* axis: same `>` sense, opposite direction, because one floors the
artefact and the other does not.

**A reviewer checking these by eye will get it wrong.** You must know which side was
truncated, and you must know what TRUE means.

## 2.5 THE 35 FILES WHOSE CURRENT BYTES ARE md5-PINNED IN A PRE-REGISTRATION

Derived by hashing each file's current bytes and matching against every 32-hex token in
the **247** committed documents under `cases/dafoam/`, `docs/dafoam/` and
`verification/campaign/` whose filename contains `PREREGISTRATION` (776 distinct tokens).
A match means the frozen registration pins **exactly these bytes**, truncation included.

| md5 | file |
|---|---|
| `a940b0ee51c9102bb27dd6aa4516f366` | `cases/dafoam/curriculum_D17_cone_supersonic/d17_grade.py` |
| `e4ade11ed9e3db18d2c4988b30e929b4` | `cases/dafoam/curriculum_D18_cone_hypersonic/d18_grade.py` |
| `87f15e05130cfdb3cbf195d1daba6154` | `cases/dafoam/ladder-a/A1/curriculum_AV1/av1_grade.py` |
| `5e714767e65ea93b893f44f6d7381274` | `cases/dafoam/ladder-a/A1/curriculum_AV1R/av1r_datum_control.py` |
| `b5c1d0092c6d2a2608ad3cc0899ed0fd` | `cases/dafoam/ladder-a/A1/curriculum_AV1R/av1r_grade.py` |
| `4bde0ad7dbdd3e460dcef1fe6d063979` | `cases/dafoam/ladder-a/A1/curriculum_AV2/av2_grade.py` |
| `b272e8f48d9ca01e4261745ed8d28354` | `cases/dafoam/ladder-a/A1/curriculum_AV2R/av2r_datum_control.py` |
| `8a2dcebd954f56d9970601fc7761787a` | `cases/dafoam/ladder-a/A1/curriculum_AV2R/av2r_grade.py` |
| `1a7f3f211f44c7b67b4f8f2d4c65bf4a` | `cases/dafoam/ladder-a/A1/curriculum_AVWC/avwc_reader.py` |
| `b429ec89e7a738647081783b8b755711` | `cases/dafoam/ladder-a/A1/curriculum_D15/d15_grade.py` |
| `0b8338b3e483548da3515e79da28762a` | `cases/dafoam/ladder-a/A1/curriculum_D16/d16_grade.py` |
| `6966d19eeccd275b45fe9a5492eef6d2` | `cases/dafoam/ladder-a/A1/curriculum_SO1a/so1a_grade.py` |
| `d2051f59089f3e71ae0fbfa315c3b784` | `cases/dafoam/ladder-a/A1/curriculum_SO1aR/so1ar_grade.py` |
| `88157ca3c04798750e97b87ca3d02a15` | `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_grade.py` |
| `367f9fc25b3b34535cb2cddfafdc06b1` | `cases/dafoam/ladder-a/A1/curriculum_SO1c/so1c_grade.py` |
| `a13cd4e7b53c5051abe697da485c3433` | `cases/dafoam/ladder-a/A1/curriculum_SO1cR/so1cr_grade.py` |
| `4f625c58c1c5f7b9a9c8f6cdda9c530c` | `cases/dafoam/ladder-a/A1/curriculum_SO2MR/so2mr_grade.py` |
| `65b2115e90b050d8e752103a26c43204` | `cases/dafoam/ladder-a/A1/curriculum_SO2a/so2a_grade.py` |
| `0ac111ef144a62111e36f676e8114af1` | `cases/dafoam/ladder-a/A1/curriculum_SO3/so3_grade.py` |
| `c5ccf28138caccd6eac1ad02cb13fa9a` | `cases/dafoam/ladder-a/A1/curriculum_SO3a/so3a_grade.py` |
| `67c386b4548825361418f757f653b9fa` | `cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_grade.py` |
| `c81a09a90950cb1610f40a91b29cdabe` | `cases/dafoam/ladder-a/A1/curriculum_SO3aR2/so3ar2_grade.py` |
| `f162ef69a7385e5d0586ef5f27657cbb` | `cases/dafoam/ladder-a/A2/curriculum_D4/d4_grade.py` |
| `f825c2cd81631b83b7d0954981540c15` | `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED/d4s_grade.py` |
| `2ed0651c786cb5bd8832f8660ba6c670` | `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_F3S/d4s_f3s_grade.py` |
| `9596c7bf711a934313a9b4d5801481c6` | `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_F3SR/d4s_f3sr_grade.py` |
| `ae13edeae807be82269de2fa5c5dc488` | `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_F3SR/d4s_f3sr_run_arm.sh` |
| `39a01c8d76d3cd27285ff1fb754bf12b` | `cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_F3SR/d4s_f3sr_stage_arm.sh` |
| `c87c7a64657107dec4f5b7d1e634ffe6` | `cases/dafoam/ladder-a/A2/curriculum_D5/d5_grade.py` |
| `a76a7d5e298a6ba719143f14e10c89bf` | `cases/dafoam/ladder-a/A2/curriculum_D6/d6_grade.py` |
| `bc8e9fec48b3f58ce7a96f4b9549590b` | `cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_grade.py` |
| `10eb6d0928addc56272854f017e01538` | `cases/dafoam/ladder-a/A3/curriculum_D7/d7_grade.py` |
| `923662ef398ca229cc3734699670418a` | `cases/dafoam/ladder-a/A3/curriculum_D7F/d7f_grade.py` |
| `4303704523de7e1c8fa6d6a34a858ded` | `cases/dafoam/ladder-a/A3/curriculum_D7FR/d7fr_grade.py` |
| `3f6eafac2ad4897417521d00c1cc5f3e` | `cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_grade.py` |

**The four material files NOT pinned:** `curriculum_D12R2/w3s_stage_record.py`,
`curriculum_SO2M/so2m_grade.py`, `wall_resolved_alpha_tail/a1wrt2_stage.py`,
`curriculum_D4/d4_grade_SUPPLEMENT.py`.

**Why the pin matters.** These are not files that can be quietly edited. A pinned file is
frozen by `CLAUDE.md` rule 2 and checked by `scripts/check_comparator_freeze.py`; changing
one after first compute is exactly the act `§2d` forbids and `§2d.1` narrowly excepts.
**That is the whole reason Petition 2 is a question and not a repair plan.**

## 2.6 THE CENSUS INSTRUMENT, AND ITS OWN THREE FAILURES

**This is recorded because it is why the number is credible, not in spite of it.** The
instrument is `ts_census3.py`, an `ast`-based pass over Python plus a lexical pass over
shell. It reached its final form only after a planted control and a manual audit each
caught it being wrong.

**FAILURE 1 — the line-level pass cannot see the floor.** A first pass classified sites by
looking for `int(`/`floor` **on the comparison line**. **Of the 89 truncated comparisons,
only 28 carry the floor on the line. 60 do not** — the floor sits on a different line, and
in the `so1a` chain above **in a different file entirely**. Had this lane trusted the
line-level count it would have reported **28** and missed two thirds of the population,
including every `on_disk < datum` and every `"ok": (mt >= datum)` site.

**FAILURE 2 — the planted control caught a miss the tree would never have revealed.**
Thirteen fixtures: eight positives (each a different route to a floor) and five negatives.
The first run scored **6/8 positives, 0/5 false positives** — it missed the two pure
read-back forms, because the only thing marking those values as timestamps is **the name
they are bound to**. After the fix: **8/8 positives, 0/5 false positives.** The two
fixtures it had missed are the exact shape of the 22 real `datum = int(open(p).read())`
sites. **Without the plant this census would have under-reported by roughly a quarter.**
(`CLAUDE.md` rule 3: a reader not shown able to see a non-zero is not evidence.)

**FAILURE 3 — two false-positive modes, found by reading the hits rather than counting
them.** An earlier version classed `st_mtime_ns` as truncated. It is the **opposite** —
integer nanoseconds, the most precise form the kernel offers. And it resolved variable
names **module-wide**, so a local `mt` in one function inherited the provenance of an
unrelated `mt` in another. Between them these two defects accused
`cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` of **six** truncations. **It has none —
it is clean, full precision on both sides, and it prints `%.6f`.** Both defects are fixed
and the fix is documented in the instrument's own docstring.

**Residual false positives, disclosed.** Five of the 80 raw dafoam hits were audited to be
immaterial and are excluded from the 75:
- `av1r_grade.py:257`, `av2r_grade.py:245` — `abs(self_mtime - datum) > DATUM_SELF_TOL_S`
  where `DATUM_SELF_TOL_S = 5`. A sub-second floor cannot move a 5 s tolerance.
- `a1wrt2_stage.py:758`, `d4s_f3sr_grade.py:360` — comparisons of two **already-integer
  recorded** values across a JSON round trip. No mtime precision is lost.
- `d6rf3_chain_watch.sh:53` — `-newermt '@0'` is "every file since the epoch", a listing
  idiom, followed by full-precision `%T@` arithmetic. Not a guard.

## 2.7 THE POPULATION IS **UNVERIFIED**, AND THAT IS THE HONEST STATE

**Whether any landed verdict in the other 38 files was changed by the truncation HAS NOT
BEEN CHECKED.** Establishing that requires, per item, comparing each artefact's
full-precision mtime against its own sentinel's fraction, on that item's own run tree.
**That was done for W3S only** — and on W3S it found a real false negative on the first
stage where the window bit.

What is established: the truncation is present, its direction per site is derived from a
swept table, and 35 of the files are byte-pinned in frozen registrations. What is **not**
established: whether any published dafoam number moved. **dafoam states this as NOT
CHECKED, not as "probably fine."**

## 2.8 WHY THIS IS RULE 4 AND NOT A STYLE NOTE

`CLAUDE.md` rule 4's age guard exists **so that a field the run did not produce cannot be
graded as one it did**. That is the whole function. A truncation that relaxes the guard
does not make it noisier; **it makes it answer the wrong question while reporting that it
answered the right one.**

The asymmetry is the argument:

- The **launcher's** half failed **closed**. It cost 0.9000 core-min, it printed its own
  refusal, and it was diagnosed and repaired within thirty minutes. **A fail-closed guard
  announces itself.**
- The **recorder's** half fails **open**. It cost nothing, printed nothing, and produced a
  manifest row that lists 12 of 14 post-dating files while carrying the field name
  `age_staged_postdating` — a positive claim that the check ran. **Nobody would have found
  it by watching.**

## 2.9 THE FACT THAT SHOULD DECIDE THE PRIORITY

**The repair commit that fixed the loud half had already read the silent half, named it,
and left it in place.** `w3s_stage_and_run.sh:1204-1207`, inside `5d5c3281`:

> *"No gate, band, threshold, cap or label moves: this variable is read at the two lines
> below and NOWHERE else, feeds no manifest row, and produces no number. **The row's own
> `age_staged_postdating` is recomputed independently by `w3s_stage_record.py` and is NOT
> touched by this repair.**"*

That sentence is true, and it is also the sentence that walked past the false negative
measured in §2.1 — which was, at that moment, already on disk.

> **A CORRECTION TO THE BRIEF THAT DISPATCHED THIS LANE, ON PROVENANCE.** The brief stated
> that `w3s_stage_and_run.sh:1193-1194` **already carried** a repair note tagged
> `W3S-DEF-AGE-1` before tonight, and drew from that a two-commit story: the loud half
> found and written down, the silent half left. **That is not what the tree says.**
> `git grep W3S-DEF-AGE-1 5d5c3281^` returns **nothing**; the parent commit carries the
> bare `-newermt` line at `:1193` with **no note at all**. The tag and the entire
> diagnosis are **new in `5d5c3281`**.
>
> **The substance survives, in a sharper form.** It is not that one commit found the
> defect and a later one ignored it. It is that **a single commit diagnosed the truncation
> class in prose, looked directly at the second instance of that same class, named it by
> file, and repaired only the half that had already announced itself.** The record is
> tighter than the brief made it, not weaker — but it is a different record, and it is
> stated here as this lane measured it.

## 2.10 BOUNDING IT HONESTLY — THIS IS NOT A FLEET ALARM

**The idiom is dafoam-local.** Of the 89 truncated comparisons repo-wide, **80 are in
`cases/dafoam/`**. The other **9 are not on any grading path**:

- `scripts/auto-stop.sh:73,198` and `scripts/auto_stop_patched.sh:302,427` — an idle scan
  with thresholds in **minutes and hours**; a one-second floor is immaterial against
  `IDLE_MINUTES`, and the file grades nothing.
- The two `verification/runs/AUTOSTOP_LIVENESS/isolation/*.NOT_FOR_INSTALL.sh` copies of
  the same code.
- `verification/runs/JF1_jet_flap/watch_jf1_runs.sh:191` — `age -gt 180`, a watcher.

**Checked and clean, with full precision on both sides:** the whole T-family, M6I, F5b,
`cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` (which an earlier version of this
instrument wrongly accused — see §2.6), `a2b2r_age_guard.py` and `so3_age_guard.py`. The
clean idiom is `t0 = os.path.getmtime(ref)` with no `int()` anywhere near it.

**dafoam recommends nothing about other teams' files and does not claim a repo-wide
defect.**

## 2.11 WHAT dafoam IS ASKING, AND WHAT IT IS NOT

**NOT asking:** for verification to repair 38 files. **NOT asking:** for a blanket
`§2d.1` exception covering the population. **NOT recommending** anything about any other
team's code.

**ASKING, and only this:**

1. **Does the unverified population in §2.7 need checking before any further dafoam
   verdict is quoted from those graders?** Every one of the 39 is a grading-path file and
   35 are md5-pinned in frozen registrations, so dafoam cannot answer this on its own
   authority in either direction — declaring them sound would be as much a self-grant as
   declaring them void.
2. **If so, what form should that check take?** dafoam can execute whatever verification
   specifies. The one form this lane can vouch for, having run it once, is the §2.1
   procedure: walk each item's run tree, compare full-precision artefact mtimes against
   that item's own sentinel fraction, and report the artefacts that fall inside the
   window. It is cheap — no solver runs — and on W3S it took minutes and found a real
   miss.
3. **A ruling on Petition 1**, which is separable from both of the above and blocks
   nothing while it waits.

---

## 3. WHERE THE DISAGREEMENTS WITH THE DISPATCHING BRIEF ARE

Recorded because a referral that quietly reconciles its own numbers is worth less than one
that shows where they moved.

| item | the brief | this lane, re-derived | why |
|---|---|---|---|
| scripts scanned | 1,557 | **2,361** | scope stated: every `.py`/`.sh` tracked at HEAD |
| genuine mtime comparisons | 144 in 103 files | **355 in 235 files** | `ast`-resolved; excludes `time.time()` deadline loops by construction |
| truncated | 39 in 25 files | **89 in 45 files**; **80 in 40** dafoam; **75 in 39** material | broader: includes recorded diagnostic fields and fixture-integrity checks |
| fail-open / fail-closed | 37 / 2 | **55 / 20** | direction taken from an exhaustive sub-second sweep (§2.4), not from operator polarity |
| md5-pinned files | 20 | **35** of 39 | current bytes matched against 776 md5 tokens in 247 committed `*PREREGISTRATION*.md` |
| line-level blind spot | 10 of 37 invisible | **60 of 89** carry the floor off the line | the read-back idiom is more common than the inline one |
| launcher wall time | 57 s | **54 s** | the run's own ledger line |
| `W3S-DEF-AGE-1` note | pre-existed the repair | **new in `5d5c3281`** | `git grep` at the parent returns nothing (§2.9) |

**Every headline claim of the brief that this lane could test held**: the measured
specimen at S1a (+0.358 s / +0.357 s, both absent from the row), the 120.772986 ms
inversion at S2a, zero graded solves, the floor-never-round finding (**0** rounds or ceils
in 355 comparisons repo-wide), the same-operator-opposite-direction corollary, and the
dafoam-local bound. **The counts are larger and one provenance claim is wrong.** The
direction of the finding is unchanged.

---

## 4. ARTEFACTS THIS DOCUMENT CITES

- `cases/dafoam/curriculum_D12R2/w3s_stage_and_run.sh` — the repaired launcher; note at
  `:1192-1207`, guard at `:1208`.
- `cases/dafoam/curriculum_D12R2/w3s_stage_record.py` — the recorder;
  `staged_files_postdating` at `:401-415`, the floors at `:406` and `:411`; `age_guard` at
  `:324-398` with further floors at `:349`, `:352`, `:373`, `:392`.
- Commit **`5d5c3281`** — the launcher repair, one file, 25 insertions / 3 deletions.
- `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3S-GSCAN-cylinder-unsteady/` —
  `manifest.jsonl` (3 rows, all `cost_leg=SETUP`), `ledger.txt` (the rc=2 / 0.9 core-min
  line and the four `AGE_DATUM` lines), and the four `.w3s_age_ref.SETUP_*` sentinels
  whose nanosecond mtimes are quoted throughout. **All still on disk as of 2026-09-06.**
- `docs/charters/VERIFICATION_CHARTER.md` — `§2d.1` at `:1936-1942`, the load-bearing
  reading of condition (2) at `:1944-1946`, the T20 ruling `§2d.3` at `:4363-4407`, the
  T5c ruling `§2d.11` at `:5171-5246`.
- The 35 pinned files and their md5s, §2.5 above.

**The census instrument and its planted fixture are working files and are deliberately not
cited by path** — `CLAUDE.md` rule 13: a repository document never cites a scratch path.
Every number in §2.2, §2.4, §2.5 and §2.6 is reproducible from the tree by the procedure
each section states, and this lane will re-run any of them on request.
