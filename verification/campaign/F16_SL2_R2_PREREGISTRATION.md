# F16-R2 — COMPARATOR RE-REGISTRATION under L-342: Stokes' second problem

**Team:** cfd. **Written 2026-08-26. ZERO CORE-MINUTES OF NEW COMPUTE.**
**Status at freeze: REGISTERED — grades the PRESERVED artefacts of run
`2aea29d9` (`verification/runs/F16_runs/STATUS.F16` = `rc=0 end=2026-08-26T16:13:02Z`).**
Frozen by the commit that carries this file together with
`cases/F16_stokes_second_problem/grade_f16_r2.py` (blob `8037cbefaca97bb7fad53be4f0c87b336871e6ac`).

## 1. INHERITANCE — BY REFERENCE, NOT BY COPY

This document inherits **`verification/campaign/F16_SL2_PREREGISTRATION.md` at
commit `2aea29d97c74f54183c1d99a28d86568ee254815`** (blob `514d91ea`, identical on
disk and at HEAD), in full: the case (§2), the reference-by-substitution (§3), the
three-level ladder (§4), **the gates and their bands (§5)**, the criteria (§6), the
gate demonstration (§7) and the cost basis (§8). Nothing in that document is
struck, amended or re-stated with a different number here.

| gate | band (inherited verbatim, prereg §5) | reference |
|---|---|---|
| G-F16-1 normalised L2 velocity-profile error | [4.101177007e−05, 3.691059307e−04] | 0 |
| G-F16-2 u(δ)/U0 at ωt = 0 (mod 2π) | [−0.31027839, −0.30884136] | −0.309559875 (exact) |

**Prediction (inherited, prereg §1/§8): observed order p ≈ 2** — the smooth
transcendental solution under a second-order scheme must recover design order.
Registered cap: 20 core-minutes (inherited; already spent 0.4167 of it by the
parent run, charged to calibration row C-123). **Cost of this registration: 0
core-minutes, $0** — the grader opens files already on disk and launches nothing.

## 2. THE DEFECT (measured, not inferred)

`cases/F16_stokes_second_problem/grade_f16.py:352` compiles
`TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$")` **without `re.MULTILINE`**
and line 369 applies it with `.finditer(text)` to the whole log. `^` therefore
matches at byte 0 only, and a real OpenFOAM log opens with the banner, so the
reader returns **0 hits on `verification/runs/F16_runs/coarse/log.icoFoam`, which
carries 16000 `Time =` lines** (`grep -c '^Time = '` = 16000 / 32000 / 64000 at
coarse / medium / fine). Consequence at commit `6f8048b9`: both gates
**PENDING** — "level 'coarse' is not complete: no `Time =` lines in the log" — on
a run that is complete by rule 4 (rc 0 in every `RC.txt`, `End` present, last
`Time = 40` = endTime, step counts 16000/32000/64000 = endTime/Δt, `40/U` and
`40/p` newer than each case's own `0/U`; the table in
`verification/runs/F16_runs/RESULTS.md` §2).

The parent selftest was green at freeze and at both launches because it never
drove `completion()` on a real log. That is the omission this registration adds.

## 3. GROUND — L-342 and the precedent

Sanaa's universal rule (`docs/LESSONS.md` L-342; boarded verbatim in the CHIEF
addendum at `d4d0c29d`): *"a bookkeeping failure invalidates the bookkeeping,
never the physics artifacts — and graders must separate physics-critical fields
from infrastructure fields so a dead poller can never void a run again."* The
comparator's own regex is bookkeeping; the solver logs, fields and sampled
profiles are physics artefacts, intact on disk. Precedent: D4-SHIPPED arm O,
re-graded on its preserved artefacts under a repaired grader (same addendum).

**Rule 2 is honoured, not bent:** `grade_f16.py` is NOT edited. The corrected
comparator is a NEW registration (this file + `grade_f16_r2.py`), committed
BEFORE it is run, and it grades the preserved artefacts at zero compute. The
original PENDING x2 at `6f8048b9` stands as the record of what the frozen
instrument printed; this row is a second, separately registered grade of the same
artefacts.

## 4. DIFF SCOPE — `grade_f16_r2.py` against its parent (blob `679823ff`)

Unified diff hunks (`diff -u grade_f16.py grade_f16_r2.py`), seven, and nothing
outside them:

| parent lines | R2 lines | content |
|---|---|---|
| 1–5 | 1–36 | header docstring: parent blob, defect, diff scope, byte-identity statement |
| 51–56 | 82–145 | L-342 field-class declaration (`PHYSICS_CRITICAL`, `INFRASTRUCTURE`), `CLOCK_RE`, `infrastructure_census()` — prints `BOOKKEEPING DEFECT` lines, never refuses |
| 290 | 379 | class-C exit-2 probe imports THIS module by basename (parent imported `grade_f16`) |
| 349 | 441 | **`TIME_RE` compiled with `re.MULTILINE`** — the repair; the only change inside `completion()`'s reach |
| 412 | 501–568 | `REAL_LOG_EXCERPT` (verbatim from the coarse log) and `control_completion_reads_a_real_log()` |
| 696 | 847 | the new control appended to the controls list |
| 719–740 | 871–899 | `rung` label `F16-SL2-R2`, parent blob, field classes and infrastructure census written to the JSON; default output `F16_R2_GRADED.json`; tally title; defect lines beside the tally |

**Gates, bands, thresholds, cap and labels are BYTE-IDENTICAL.** Evidence:
`diff <(grep -E 'BAND|CAP|THRESH|GATE|band|cap|CLASS_C|P_SOLVER_TOL|grade_ladder\(' grade_f16.py) <(same on grade_f16_r2.py)`
reports **0 deleted and 0 changed lines** — only 9 added lines, all inside the
header docstring and the field-class block (they *name* `CAP_CORE_MIN`; none
assigns it). `BAND_FACTOR = 3.0`, `P_SOLVER_TOL = 1.0e-9`, `CAP_CORE_MIN = 20.0`,
`CLASS_C`, `bands()`, `demonstrate()`, `grade_one()` and the single
`RT.grade_ladder(` call are unchanged lines. Still: 0 `ast.Assert` nodes;
`--selftest` rc 0 (8 controls); `python3 -O` rc 2.

**Refusals reclassified under L-342: none.** The parent keys no refusal on an
infrastructure field — `CAP_CORE_MIN` is only written into the record and
ClockTime is not read at all. The R2 census reads ClockTime, `RC.txt` and
`STATUS.F16` as INFRASTRUCTURE; an absent one prints `BOOKKEEPING DEFECT ... NOT
MEASURED` beside the verdict and the grade proceeds.

## 5. THE DRIVEN CONTROL THE PARENT LACKED

`control_completion_reads_a_real_log()` embeds 52 verbatim lines of
`verification/runs/F16_runs/coarse/log.icoFoam` (from `Starting time loop`
through the fifth step, plus the last 14 lines including `Time = 40`,
`ExecutionTime = 3.14 s  ClockTime = 3 s` and `End`): **5 `Time =` lines
planted.** Required: the parent's anchored non-MULTILINE form counts **0** on
that excerpt (the defect reproduced); R2's `TIME_RE` counts **exactly 5**;
`completion()` on a synthetic case around the excerpt counts 5, reads latest =
40 and stops at the fixed-Δt identity limb (5 ≠ 16000) — i.e. it got PAST the
limb that voided the parent grade; and the same excerpt with the `Time =` lines
removed reads `done=False`, why = "no `Time =` lines in the log". Selftest
result at registration: all four held (`direct_count 5`,
`parent_form_without_MULTILINE_count 0`, `completion_count 5`, negative why as
required).

## 6. THE ARTEFACTS THIS ROW GRADES — blob and mtime evidence, read before commit

All under `verification/runs/F16_runs/`; `git hash-object` and epoch mtime
(`stat -c %Y`) at 2026-08-26 ~16:25Z. Run window from `launcher.out` and
`STATUS.F16`: 16:12:36Z → 16:13:02Z.

| artefact | blob | mtime (epoch, UTC) |
|---|---|---|
| coarse/0/U (launch stamp) | 57ad3082 | 1787760756, 16:12:36 |
| coarse/log.icoFoam (16000 Time lines, ClockTime 3 s) | 9a212aaa | 1787760759, 16:12:39 |
| coarse/40/U | 5531f08d | 1787760759, 16:12:39 |
| coarse/RC.txt (= 0) | 573541ac | 1787760759 |
| medium/0/U | f7ce3008 | 1787760759, 16:12:39 |
| medium/log.icoFoam (32000 Time lines, ClockTime 7 s) | 6f141238 | 1787760766, 16:12:46 |
| medium/40/U | e8ec7ab2 | 1787760766, 16:12:46 |
| medium/RC.txt (= 0) | 573541ac | 1787760766 |
| fine/0/U | e555c930 | 1787760766, 16:12:46 |
| fine/log.icoFoam (64000 Time lines, ClockTime 15 s) | ae2f819c | 1787760781, 16:13:01 |
| fine/40/U | 5a54b982 | 1787760781, 16:13:01 |
| fine/RC.txt (= 0) | 573541ac | 1787760782 |
| STATUS.F16 (`rc=0 end=2026-08-26T16:13:02Z`) | f5473158 | 1787760782, 16:13:02 |

Each level's `40/U` is newer than its own `0/U` (age guard); 40 phase-locked
`postProcessing/profile/<t>/profile_U.xy` samples per level. Field data is on
disk, not committed (54 MB). No F16 solver process exists; nothing is launched
by this row.

## 7. WHAT IS REGISTERED HERE, AND WHAT IS NOT

Registered: the grader `grade_f16_r2.py` at the blob above; the output paths
`verification/runs/F16_runs/GRADE_F16_R2.out` and `F16_R2_GRADED.json`; the
record `verification/runs/F16_runs/RESULTS_R2.md`; the prediction p ≈ 2; cost 0.
Not registered: any change to a gate, band, threshold, cap or label (none is
permitted here or anywhere under L-342 clause 4); any new compute; any change to
`grade_f16.py`, `exact_stokes.py`, `run_f16.sh` or the parent pre-registration.
