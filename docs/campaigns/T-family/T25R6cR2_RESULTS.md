# T25R6c-R2 — RESULTS

**Rung:** T25R6c-R2 — G-R2-1 (PLATEAU) and G-R2-2 (DIRECTION), leg A / leg B within one run
**Case:** `W1150_C4_L1`
**Registration:** `docs/campaigns/T-family/T25R6cR2_PREREGISTRATION.md`, frozen at `f67ade8d`
**Grading path:** `verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py`
**Team:** heat-transfer

---

## VERDICT

> ## GATE FAIL — `rho = 1.103859`
>
> **G-R2-2 DIRECTION is falsified.** The registered prediction was `rho < 1.0`; the measured
> ratio is `1.103859 >= 1.0`. A1.2's direction does not hold on this rung.
>
> **The verdict of record is the frozen grader's own stdout**, landed at `286276a1` as
> `verification/runs/T-family/T25R6cR2_LEGAB_runs/T25R6cR2_GRADE_STDOUT.txt`, **with its
> traceback intact** — sha256 `d672c647cad49b30ddafeded80b0b912fbf621da240e0a7ded04fd197ef6509f`.
> That file has never been edited and is not edited by anything in this record.

> ### ⚠ THE CAVEAT A READER NEEDS BEFORE ANY NUMBER BELOW, AND IT IS IN THE HEAD BECAUSE IT BELONGS THERE
>
> **The grader that produced this verdict CRASHED after grading and before recording.** Every
> gate above was computed and printed; the registered artifact `T25R6cR2_VERDICT.json` was
> never written, and the registered exit code `3` left the interpreter as `1`. The verdict
> stands — under Sanaa's 2026-08-26 universal rule that **bookkeeping never voids physics** —
> and the defect is disclosed in full below rather than tidied away. **The repair has since
> been applied under `VERIFICATION_CHARTER.md §2ah` and the artifact now exists; the gate
> numbers did not move by one digit, and that is measured, not asserted.**
>
> **This rung is NOT a licence to launch.** T25R5 5.1 is carried in force: no ladder launches
> on this result, whatever it says. And this rung consumes no output of T25R6a or T25R6c —
> T25R6c's `rho = 1.063997` remains a diagnostic and may not be quoted as a verdict.

---

## THE MEASUREMENT

All values below are read from the landed stdout named above, and every one of them is
byte-identical in the post-repair re-run.

### Rule 3 — planted-zero control on the `ExecutionTime` reader, BOTH legs

`1.23 s` planted at step 7 of a **copy** of each real log, read back **from disk** through the
same reader that grades: it moved that delta by `1.230000 s` **and no other delta moved**, in
both leg A and leg B. The reader's zeros are therefore evidence.

### Rule 4 — completion

`W1150_C4_L1` **COMPLETE** — all conjuncts, both legs, age guard against `0/module/T`.
Registered steps 40 (leg A) + 1110 (leg B); `endTime` 0.8 s and 111.8 s; `ExecutionTime`
14.35 s and 438.63 s, **CPU time (user+system, rank 0), not wall** — established from this
build's source, `OpenFOAM-v2606 TimeIO.C:631` → `cpuTimePosix` → `times(2)`, not assumed from
convention. Marker: `verification/runs/T-family/T25R6cR2_LEGAB_runs/DONE.W1150_C4_L1`.

### C-R2-1 — the transient control, measured by the run's own solver work

| | |
|---|---|
| the run's own transient ends at | **leg-B step 27** |
| registered exclusion | **40 steps** (`D_EXCL`) |
| settled work | **92..94 iterations/step** over the graded 1070 steps |
| P-R2-5 predicted | 92..94 — **WINS** |

**The control passes with margin:** the registered exclusion of 40 steps is 13 steps beyond
where the run's own transient actually ends, so leg B's graded window is not contaminated by
the restart. This is the control that stands between `rho` and the objection that leg B is
still settling.

### G-R2-1 — PLATEAU. Evaluated FIRST, before `rho` is consulted

| | |
|---|---|
| r(steps 41..575) | **0.396710 s/step** |
| r(steps 576..1110) | **0.395308 s/step** |
| \|d\|/second | 0.3546 % |
| \|d\|/first | 0.3534 % |
| **GRADED** | **0.3546 %** |
| **threshold** | **5.0 %** |
| **outcome** | **PASS — the plateau clause holds, by a factor of 14** |

The plateau is what licenses reading `rho` beyond the sampled steps, and it is evaluated
before the direction gate precisely so that a failed plateau cannot be rescued by a liked
`rho`. Reported beside it, gating nothing: **R-R2-1**, the T25R6c-form statistic on the same
series is **5.5168 %** (P-R2-1 predicted 10.427 %, > 5 %: WINS) — the half-split statistic and
the R6c-form statistic disagree by an order of magnitude on the same data, which is the whole
reason R2 exists. **R-R2-2**: 27 leg-B windows of 40 steps, `rho` per window **1.0383 .. 1.1498**.
**R-R2-3**: settled-work spread **2.150 %**; the drift floor is tabulated at W = 40, 90, 180,
267, 535.

### G-R2-2 — DIRECTION. The gate that fails

| | |
|---|---|
| r(leg A) | **0.358750 s/step** over 40 steps at deltaT 0.02 |
| r(leg B, post-transient) | **0.396009 s/step** over 1070 steps at deltaT 0.10 |
| **rho** | **1.103859** |
| registered prediction | `rho < 1.0` (P-R2-3 predicted 1.075209) |
| 1-sd band | [1.0439, 1.1066] |
| **outcome** | **GATE FAIL — `rho >= 1.0`, A1.2's DIRECTION IS FALSIFIED** |

Reported beside it, gating nothing: **R-R2-4**, `rho_work = 0.804976` and
`rho_throughput = 1.371294`; and `rho` over **all** leg-B steps — the figure comparable to
T25R6c's 1.063997 — is **1.101497**.

### B-R2 — ceiling relief. REPORTED, NEVER GATED

`rho_blend` (ladder 3500A + 8300B) = **1.073053** → Σ CAP(C4) × blend = **26514.4 core-min**
against the ceiling of 20000. Relief threshold 0.809412. **This grants no widening**, and the
A1.3 ceiling of 20,000 core-min is not this team's to move.

### Rule 5 — Roache. NOT INVOKED, and that is a registered decision

There is no grid family here and no functional at convergence: this is a **wall-cost
measurement inside one transient at one mesh**. No observed order and no GCI is computed,
quoted or derivable. **A successor reading a grid-convergence claim off these numbers gets
`NOT A RESULT`.**

### Rule 12 — predicted versus actual

| | |
|---|---|
| pre-registered cost point | **14.707 core-min** |
| actual | **15.0993 core-min** |
| **ratio actual/predicted** | **1.0267** |
| per-run cap | 45.0 core-min (3.06×) — not approached |
| P-R2-4 | **WINS** |

Attribution: the 2.67 % overshoot is within the box-contention floor this rung measured for
itself as R-R2-3 (settled-work spread 2.150 %) and is not attributed to waste or to
misprediction. `cost_basis`: **REPORTED-BY-OWNER**; dollars are **derived, not measured**, at
the recorded $0.0513/core-h — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

---

## RECORD-EMISSION REPAIR — DATED DISCLOSURE UNDER `§2ah`, 2026-09-03

**No gate, threshold, band, cap or label is created, moved or retired by this section, and
nothing is re-graded by it.**

**ROUTE, AND WHY IT IS THIS ONE.** `VERIFICATION_CHARTER.md §2ah` (v1.53) ruled that `§2d.1`
does not reach a post-compute change off the grading path: no exception, no petition and no
ruling was needed. **That is not "nothing was owed."** `CLAUDE.md` rule 6 supplies the form
and `§2d:1842-1845` supplies the content, and both are discharged — the form in the dated
amendment at `verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py:1108-1236`,
the content here. Landed at commit **`001fc082d4e5b612247cb888a94045c9a7fd0e09`**.

### (i) WHAT CHANGED

**One character**, at `grade_t25R6cR2.py:863`, inside `finish()`. Struck, quoted verbatim and
never rewritten:

```
        "advance as an irreducible ~3 % floor; (b) leg B's restart coupling to "
```

replaced by:

```
        "advance as an irreducible ~3 %% floor; (b) leg B's restart coupling to "
```

The literal at `:856-868` is an implicit concatenation closed by `% D_EXCL` at `:868`. In the
frozen text the `% f` of `"% floor"` parses as a **valid conversion** — space flag, `f` float
— and consumes `D_EXCL`, leaving the real `%d` at `:865` with no argument:
`TypeError: not enough arguments for format string`. Escaping to `%%` restores the literal
per-cent sign, and the emitted prose is byte-for-byte what the frozen file intended to emit.
**Nothing else changed:** no refactor, no added field, no exit code, no reformatting.

*Two citations pinned per `§2d.5`, corrected by verification against the petition's originals:
the crashing literal is at `:863`, not `:857` — the traceback prints `:857` because CPython
attributes the frame to the first physical line of the implicit concatenation, which opens at
`:856` — and `json.dump` is at `:870`, not `:869`.*

### (ii) WHEN

**2026-09-03**, after the graded solve and after the pre-repair stdout was landed at
`286276a1` with its traceback intact. That file is not edited.

### (iii) WHAT WAS READABLE AT THAT MOMENT

**Every gate line.** The crash is at `:863` inside `finish()`, which is called at `:826`,
after all grading. All **43** printed lines up to the traceback were already on stdout and are
landed — the rule-3 planted-zero control on both legs, the rule-4 completion line, C-R2-1,
both plateau halves and their two normalisations, the graded statistic, `rho`, R-R2-1 through
R-R2-4, the B-R2 block, the rule-12 line and the G-R2 verdict line. **What was NOT readable:
the registered artifact `T25R6cR2_VERDICT.json`, which `json.dump` at `:870` never reached.**

### (iv) WHICH FINDINGS REST ON IT AND WHICH DO NOT

**No gate finding rests on it, and this is measured rather than asserted.** The `§2ah.1`
T25R6cR2 probe was re-run on the repaired file, driven through the **production** path against
the **real** case directory: all **43** landed gate lines are **byte-identical** (`cmp` clean;
prefix sha256 `979e3572e2d8e0ca63f5f6c5fd3114545cf7e9581fc59cd1638114a254a3d5d4`). Not one
digit of one gate moved. **What rests on the repair is exactly two things: the existence of
`T25R6cR2_VERDICT.json`, and the process exit code.**

### (v) THE REGISTERED CHANNELS THAT MOVED — `§2ah.3`'s FIFTH DISCLOSURE CONTENT

| registered channel | registered | actual, pre-repair | post-repair |
|---|---|---|---|
| process exit code | **3** (`EXIT_GATE_FAIL`, `grade_t25R6cR2.py:117-120`) | **1** — an unhandled `TypeError` through the unguarded `__main__`, a value outside the registered vocabulary | **3** |
| verdict artifact (`T25R6cR2_PREREGISTRATION.md:532`) | present at grade time | **ABSENT** | **PRESENT** |

**No other registered channel moved.**

### (vi) WHICH OFF-PATH CLAIM THIS RECORD STANDS ON — `§2ah.3`'s CLOSING NARROWING

**It is split, and that is said rather than averaged.**

- **On the gate values — the STRUCTURAL claim, "nothing downstream COMPUTES it."** Every
  `out["verdict"]` assignment is at `:551`, `:583`, `:702`, `:800` and `:808`, all inside
  `grade()` and all above the `finish()` call at `:826`; `rho` is computed at `:719`;
  `finish()` opens at `:829` by storing the `rc` it was handed. **Nothing at or after `:829`
  computes a gate value. This claim does not expire.**
- **On the exit code — a CONSUMER CENSUS ONLY, "nothing READS it."** It is strictly the
  weaker claim and **it expires the moment somebody writes a consumer** of this grader's rc.

### (vii) `§2ah.2`'s CONDITION — DISCHARGED BY RE-RUN, NOT BY THIS TEXT

The repair is not finished when the character changes; it is finished when the file **exists
and parses**.

| | |
|---|---|
| artifact | `verification/runs/T-family/T25R6cR2_LEGAB_runs/T25R6cR2_VERDICT.json` |
| exists / parses | **yes / yes** — 15,145 bytes, 31 top-level keys, valid JSON |
| carries | `verdict = "GATE FAIL"`, `exit = 3`, `rho = 1.103859`, `predicted_verdict = "GATE FAIL"` |
| process exit code | **3**, stderr empty |
| gate lines | byte-identical to the landed stdout, all 43 |
| receipt | `verification/runs/T-family/T25R6cR2_LEGAB_runs/T25R6cR2_GRADE_STDOUT_POSTREPAIR_2026-09-03.txt` |

Compute for the repair and its demonstrations: **zero solver compute**; approximately
**0.06 core-min** of interpreter time across the probe, three production-path grading runs and
two selftests, measured at 0.70 s wall, 1 rank, per grading run.

### (viii) RULE 2's FREEZE VERIFICATION WAS SATISFIED BY HAND AND NOT BY THE REGISTERED PATH

`T25R6cR2_PREREGISTRATION.md:532` registers, inside `GRADING_FREEZE`, that the grader
recomputes and reports **both** its git blob sha1 and the **full sha256 of its disk bytes**
(L-450) **into `T25R6cR2_VERDICT.json` at grade time**. **That artifact was unreachable
through the frozen path.** The verification was therefore performed **by hand, on the
pre-repair bytes**, against blob **`eb363769bb18dd0550b551e6fa5ba457f002cfb9`** — identical on
disk at that moment, at freeze commit `f67ade8d`, and at HEAD — with disk sha256
`421b9cf4e7768b95cb9ca6d5eed1e2c093142a934100f90b0bf39de32d45d07b`. **A reader must not be
left to assume the registered path produced it.**

**And the converse, so the artifact that now exists is not misread:** the
`T25R6cR2_VERDICT.json` emitted after the repair carries sha256
`d0aee9fcf57aaf777286b293629d1a046c97b25be894ecdd10cbd4e4ecf5a02b` and blob
`947df9dfc54157c79e76e2be273fdc73893adef8` — the **amended** file's hashes, **not the frozen
one's**. The frozen blob `eb363769` is what graded the landed stdout. The two are reconciled
only by the amendment, and by this record.

### (ix) THE FREEZE CHECKER, AND A PREDICTION CONVERTED INTO A MEASUREMENT

The amendment block, written before the commit existed, recorded two measured states and one
**reading** — and said so, at that strength, rather than folding all three under a "measured"
banner.

| when | `scripts/check_comparator_freeze.py` status | strength at the time |
|---|---|---|
| before the repair | **FROZEN**, `worktree_differs_from_HEAD` False | measured |
| repair on disk, uncommitted | **MODIFIED_AFTER_COMMIT**, `worktree_differs_from_HEAD` True | measured |
| after commit `001fc082` | **AMENDED_AFTER**, `worktree_differs_from_HEAD` False | **predicted from `check_comparator_freeze.py:404-409`; now MEASURED** |

**The third state is now observed** — first commit 2026-09-03T18:50:53Z (the freeze) precedes
the first marker at 19:01:32Z, and the amendment commit at 20:44:26Z follows it, which is
exactly the shape that checker calls `AMENDED_AFTER`: its own designed state for a rule-6
amendment to a published rung, reported as its own state rather than folded into a violation.
**This observation is recorded here, where it was taken, and is deliberately not retrofitted
into the amendment block, which is frozen prose describing what was known when it was
written.**

### (x) WHAT THIS SECTION DOES NOT DO

It adopts **no exit-code contract**. `§2ak` (v1.54) is **forward-only**, this comparator is
explicitly outside its scope, no `EXIT_INSTRUMENT_ERROR` is introduced, and **Defect B — the
unguarded `__main__` — is NOT repaired.** It re-grades nothing, moves no gate, and leaves
`T25R6cR2_GRADE_STDOUT.txt` byte-untouched.

**One honest qualification on rule 6's form**, carried here as it is carried in the amendment:
rule 6's canonical amendment is a **pure append**, which preserves line numbering *and* the
byte prefix. This one preserves numbering — verified by diff, the whole change being a 1-for-1
replacement at `:863` plus an append at `:1108`, so **lines whose number changed above the
amendment: 0** — but **not** the prefix, because one line's content changed in place. A
prefix-form freeze check (the `verify_freeze_prefix` form at
`cases/F23b_HP_WEDGE/grade_f23b.py`) would flag this file and **would be right to**.

---

## FORWARD OBLIGATION — `analyse_t25.py:363-365`, NAMED, DATED, AND DELIBERATELY NOT REPAIRED

`VERIFICATION_CHARTER.md §2ak.4` names one item as heat-transfer's and expressly does **not**
order it. **Confirmed at source, 2026-09-03:**
`verification/runs/T-family/T25_MODULE_runs/analyse_t25.py:363-365` refuses with
`sys.exit("REFUSE: planted control failed; this reader's numbers are not admissible")` — and
`sys.exit()` with a **string** argument prints to stderr and exits **1**, which this lane
measured directly. **So `CLAUDE.md` rule 3's own planted-control refusal, in the file that is
rule 3's binding artifact, is indistinguishable by exit code from a crash** — the exact
confusion the T25R6cR2 defect above made concrete.

**It is not repaired today, and the decision is the heat-transfer supervisor's, taken on
2026-09-03 on three grounds.** First, `§2ak` is **forward-only**: an existing comparator that
does not conform is explicitly **not a defect** under the clause that named it. Second, **no
result is blocked** — nothing gates on that exit code, so the `§2d.1`/`§2ah` machinery has no
work to do, and editing a frozen instrument with no finding behind it spends the freeze's
credibility to buy nothing. Third, instrument work while cases wait is capped, and this one is
blocking no case.

**The obligation this record creates instead, and it is dated:** the **next comparator this
team registers** gives an internal error **its own exit value, distinct from a refusal** —
`EXIT_INSTRUMENT_ERROR = 70` per `§2ak.2`, with the reference form already on this lab's disk
at `verification/runs/T-family/T25R2_MODULE_runs/analyse_t25R2.py:2729-2751`, written by this
team weeks earlier. And `analyse_t25.py:363-365`'s rc-1 refusal is disclosed **here** so that
**no future reader takes its exit 1 for a crash**, and no future reader takes this team's
silence for ignorance of it.

---

## ARTIFACTS

| what | where |
|---|---|
| verdict of record (pre-repair stdout, traceback intact) | `verification/runs/T-family/T25R6cR2_LEGAB_runs/T25R6cR2_GRADE_STDOUT.txt` |
| registered verdict artifact | `verification/runs/T-family/T25R6cR2_LEGAB_runs/T25R6cR2_VERDICT.json` |
| `§2ah.2` condition receipt (post-repair stdout) | `verification/runs/T-family/T25R6cR2_LEGAB_runs/T25R6cR2_GRADE_STDOUT_POSTREPAIR_2026-09-03.txt` |
| grader, with the dated amendment at `:1108-1236` | `verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py` |
| completion marker | `verification/runs/T-family/T25R6cR2_LEGAB_runs/DONE.W1150_C4_L1` |
| registration | `docs/campaigns/T-family/T25R6cR2_PREREGISTRATION.md` |
| the petition that produced the ruling | `docs/campaigns/T-family/T25R6cR2_2D1_RECORD_EMISSION_PETITION.md` |
| the ruling | `docs/charters/VERIFICATION_CHARTER.md` §2ah, §2ah.1, §2ah.2, §2ah.3 |
