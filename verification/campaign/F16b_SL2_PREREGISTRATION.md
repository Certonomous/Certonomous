# F16b — PRE-REGISTRATION: Stokes' second problem, ±x CYCLIC (successor to F16)

**Team:** cfd. **Written 2026-08-26, before any compute of this case. ZERO
CORE-MINUTES SPENT ON F16b** (one 4-step smoke arm ran in the scratchpad, §9).
**Status at freeze: ARMED — never run.** Frozen by the commit that carries this
file together with `cases/F16b_stokes_second_problem/` (grader `grade_f16b.py`
blob `a7d14ed93c051f73d4315b171900471a4ba80e34`, launcher `run_f16b.sh` blob `89bd60d90a5d585055fd6df1fd5043c59c582c9e`,
`blockMeshDict.template` blob `4bcf8ed540e523404003cd734287f6f3379eb91f`, `0/U.template` blob `6a5c0b8810eac1373620a78636fe7084e7880f99`,
`0/p` blob `57a10277f691ed69a5673ddc0653e284834975a9`, `exact_stokes.py` blob `78bd3342` byte-identical to F16's).
After first compute the gates, thresholds, cap and labels below are **closed**.

## 1. WHY F16b EXISTS — F16's Finding B, disclosed

F16 (`F16_SL2_PREREGISTRATION.md` at `2aea29d9`; run complete, STATUS.F16
`rc=0 end=2026-08-26T16:13:02Z`, 0.4167 core-min, calibration row C-123)
produced **identically zero fields at every level**: `40/U` `uniform (0 0 0)`,
0 non-zero rows in every sampled profile, 0 `Solving for Ux` lines in every
log. Cause: the registered `blockMeshDict` declares **both ±x (`sides`) and ±z
(`frontAndBack`) as `empty`**. In OpenFOAM an `empty` patch removes its normal
direction from the solved set, so the x-component the oscillating wall drives is
never solved. Recorded in `verification/runs/F16_runs/RESULTS_R2.md` §3
Finding B; cfd-supervisor closed the F16 row as **NOT A RESULT on physics** on
2026-08-26. This is a case-definition defect, not a solver, scheme or grader one.

Two reader defects were found on the same artefacts and are also disclosed:
(A) the F16 grader's `^`-anchored `TIME_RE` without `re.MULTILINE` read 0 of
16000 `Time =` lines (repaired in `grade_f16_r2.py` at `ebe1b893`, L-342);
(B) `read_xy_u` pinned six columns from F6b's `axis xyz` sets while this
case's `axis y` set writes **four** (y Ux Uy Uz) — measured on the real F16
samples (56/112/224 rows) and re-measured on the smoke arm of THIS case's
dictionaries (§9). Both are repaired in `grade_f16b.py`.

## 2. THE CASE — F16 with ONE change

`cases/F16b_stokes_second_problem/case/` is a copy of F16's `case/`.
**The only change: ±x is a `cyclic` pair** (`left`/`right`, `neighbourPatch`
each other, one cell wide, in `blockMeshDict.template`, `0/U.template` and
`0/p`); ±z stays `empty`. Periodicity in x with one cell enforces ∂/∂x = 0
exactly, which is the 1-D problem. `diff -r` against F16's `case/`: the three
patch declarations and nothing else (14 changed lines, all patch entries and
their comments). Solver `icoFoam`, `ddtSchemes backward`, `nu`, H = 0.14 m,
the `sine` wall BC, the exact initial condition written by the launcher, the
phase-locked `sets` sampler — all as F16 registered them
(`F16_SL2_PREREGISTRATION.md` §2, lines 25–44).

## 3. THE REFERENCE — inherited by quotation

F16 §3 (lines 45–80): the reference is not a paper but a symbolic substitution
of `u(y, t) = U0·exp(−k y)·sin(ω t − k y)` into the Navier–Stokes residuals,
verified on this box by `exact_stokes.py --selftest` (rc 0 today on the
byte-identical copy). Nothing changes.

## 4. THE LADDER — inherited

F16 §4 (lines 81–107): three levels, 1×56×1 / 1×112×1 / 1×224×1 cells, Δt =
1/400, 1/800, 1/1600 s, r = 2 in Δy and Δt, endTime 40 periods, serial at every
level, decomposePar never invoked. `exact_stokes.LEVELS` byte-identical.

## 5. THE GATES AND THEIR BANDS — inherited VERBATIM, quoted with line numbers

From `F16_SL2_PREREGISTRATION.md` at `2aea29d9` (blob `514d91ea`):

- line 110–111: *"Both bands descend from ONE declared parameter, `BAND_FACTOR
  = 3`, applied to an analytic truncation-error prediction."*
- line 126: **G-F16-1 — normalised L2 velocity-profile error**; line 131–132:
  *"At Δy_fine = 6.25e−04 that is 1.230353102e−04. Band = [prediction/3,
  prediction×3] = [4.101177007e−05, 3.691059307e−04]."*
- line 134: **G-F16-2 — u(δ)/U0 at the graded phase ωt = 0 (mod 2π)**; line
  136: *"Exact value −0.309559875653112"*; lines 143–144: *"Band = exact ± 3 ×
  the same amplitude at y = δ = ±7.185145335e−04 = [−0.310278390187,
  −0.308841361120]."*

Gate ids are kept (`G-F16-1_E2_velocity_profile_L2`, `G-F16-2_u_at_delta`) so
the F16b row is read beside the F16 row. `grade_f16b.py`'s `bands()`,
`BAND_FACTOR = 3.0`, `P_SOLVER_TOL = 1.0e-9` and `CLASS_C` are unchanged lines
from `grade_f16.py` (grep-diff on band/threshold lines: 0 deleted or changed).

**Prediction (F16 §1 lines 17–20, quoted):** *"This solution is smooth and
transcendental, so a second-order scheme must recover its design order"* —
**observed order p ≈ 2**; and with F15 (p ≈ 1 predicted) the ladder instrument
is shown to distinguish the two regimes.

## 6. CRITERIA — inherited, plus the L-342 field classes

F16 §6 (lines 153–203) applies unchanged: verdict vocabulary; rule 5 through
`grade_ladder` only (one AST call node); Class C on the phase-locked series,
12-period window, element 4 exits 2; iterative census over every step's final p
residual at 1e−09; completion by rule 4 with the fixed-Δt count identity and the
age guard against `0/U`; planted-zero controls into the real artefact with the
real parser (E2 predicted to 1e−14, u(δ) to 1e−12); 0 `assert` nodes; hard
`-O` refusal. Added (from `grade_f16_r2.py`): PHYSICS_CRITICAL vs
INFRASTRUCTURE field classes; ClockTime, `RC.txt` and `STATUS.F16b` are
infrastructure and print `BOOKKEEPING DEFECT ... NOT MEASURED` beside the
verdict, never a refusal. Instrument state at freeze: `grade_f16b.py --selftest`
rc 0 (9 controls, incl. the real-log completion control and the real-4-column
sample control with the 6-column layout refused); `python3 -O` rc 2; 0 assert
nodes; `run_f16b.sh --preflight` rc 0; `scripts/check_launcher_can_launch.py
--worktree` rc 0 on the launcher.

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING AND A PASSING VALUE

Through the real reader on the real **4-column** write format (`synth_xy` now
writes y Ux Uy Uz), at freeze:

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F16-1 | exact + 1× predicted truncation amplitude profile | 1.193460e−04 | [4.101e−05, 3.691e−04] | inside |
| G-F16-1 | exact + 40× the same | 4.773100e−03 | same | outside |
| G-F16-2 | exact + 1× the same | −0.309126097 | [−0.310278, −0.308841] | inside |
| G-F16-2 | exact + 40× the same | −0.299780847 | same | outside |

(identical to F16 §7 lines 210–215 — the demonstration values do not depend on
the column layout, which is the point of driving it through the reader.)

## 8. COST — NOW PRICED FROM A MEASUREMENT

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** Basis: F16 run `2aea29d9`,
the same dictionaries and step counts on this box, ClockTime **3 / 7 / 15 s**
(`verification/runs/F16_runs/{coarse,medium,fine}/log.icoFoam`) = **0.4167
core-min MEASURED** for F16. F16b solves one more velocity component (Ux) per
step; predicted **~0.5 core-min** (0.4167 × ~1.2), i.e. ~30 s of serial wall.
**REGISTERED CAP: 5 core-minutes** (10× the measured basis; the previous 20 was
priced with no history). Derived dollars: /bin/bash.0004 predicted, /bin/bash.0043 at the cap
— **DERIVED, NOT MEASURED** (/bin/bash.0513/core-h reported-by-owner; the box cannot
read its own billing). `cost_basis`: **derived from measured F16 ClockTimes,
not measured for this run.** Cap checked incrementally per level by the
launcher (projections 3/7/15 s, the measured figures); launcher and grader
refuse to start if their caps disagree (checked: both 5). Actual/predicted
lands in `docs/COST_CALIBRATION.md` at completion.

## 9. NEVER RUN — THE EVIDENCE, AND THE ONE SMOKE ARM

`verification/runs/F16b_runs` is **ABSENT** at the time of writing
(`test -e`). No `0/`, `RC.txt`, `log.*` or numeric time directory exists
under `cases/F16b_stokes_second_problem/case/`.

One **smoke arm** ran under the supervisor's explicit allowance, **in the
scratchpad only** (not a repository path; not citable; deleted with the
session): coarse mesh (56 cells), endTime 0.01 s = 4 steps, sampler set to
write every step. Result: blockMesh and checkMesh OK with the cyclic pair,
icoFoam rc 0, **`Solving for Ux` at all 4 steps**, Courant max 0.077,
**profile_U.xy = 4 columns, 56 rows, 56 non-zero** — the layout `grade_f16b.py`
pins and the proof the x-component is now solved. Cost: ClockTime 0 s (integer
read-out), bounded above by 1 s = **< 0.017 core-min**, named here and charged
nowhere else. No F16b registered level has run.

## 10. WHAT IS NOT REGISTERED HERE

No change to any band, threshold or label of F16; no change to
`exact_stokes.py`; no change to F16's frozen files (`grade_f16.py`,
`grade_f16_r2.py`, `run_f16.sh`, `F16_SL2_PREREGISTRATION.md`,
`F16_SL2_R2_PREREGISTRATION.md` all untouched). Output paths:
`verification/runs/F16b_runs/{coarse,medium,fine}`, `STATUS.F16b`,
`F16b_GRADED.json`, `RESULTS.md`. Queue entry: `verification/queue/cfd/F16b.json`
naming this commit's full sha — dropped only after the supervisor's reply.
