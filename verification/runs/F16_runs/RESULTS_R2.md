CERTONOMOUS MORNING REPORT
Date:       2026-08-26
Assembled:  2026-08-26T16:30:00Z
Sections:   6 of 6
Missing:    none

# F16-SL2-R2 — Stokes' second problem, comparator re-registration under L-342 — GRADED RECORD

Team cfd. Re-registration `verification/campaign/F16_SL2_R2_PREREGISTRATION.md`
frozen at commit `ebe1b89334f0eabc9b0702822f61ac44f8d1fe86` (grader blob `8037cbef`,
verified identical on disk at grade time), inheriting
`F16_SL2_PREREGISTRATION.md` at `2aea29d9` by reference. Grader run:
`python3 cases/F16_stokes_second_problem/grade_f16_r2.py --prereg-commit=ebe1b89334f0eabc9b0702822f61ac44f8d1fe86`,
**rc 2 (REFUSED)**, stdout empty (`GRADE_F16_R2.out`), refusal in `GRADE_F16_R2.err`.
**No `F16_R2_GRADED.json` was written** — the comparator exits before the record.

## 1. SPEND

- This row: **0 core-minutes, $0** — registered cost 0, actual 0, ratio not
  defined (0/0), waste 0. No solver was launched; the grader opened files already
  on disk. The compute it grades was charged to run `2aea29d9` (0.416667 core-min
  MEASURED from the three `log.icoFoam` ClockTime lines: 3 + 7 + 15 s, ranks 1),
  calibration row C-123 in `docs/COST_CALIBRATION.md`. No new calibration row is
  landed for a zero-cost grade; the supervisor may direct one.
- Left running: nothing. No F16 process exists.

Source: `GRADE_F16_R2.err`; `coarse/log.icoFoam`, `medium/log.icoFoam`,
`fine/log.icoFoam` (ClockTime lines); `STATUS.F16`; prereg-R2 §1.

## 2. LADDER POSITIONS

Rule 4 completion holds at every level (re-read by this lane; the R2 selftest's
driven control shows the MULTILINE `TIME_RE` reads the real log shape — 5 of 5
planted lines on a verbatim excerpt, 0 of 5 under the parent's form):

| level | rc | End | last Time | `Time =` lines = endTime/Δt | fields at 40/ | age guard |
|---|---|---|---|---|---|---|
| coarse | 0 | yes | 40 | 16000 = 16000 | U p | 0/U 16:12:36 → 40/U 16:12:39 |
| medium | 0 | yes | 40 | 32000 = 32000 | U p | 16:12:39 → 16:12:46 |
| fine   | 0 | yes | 40 | 64000 = 64000 | U p | 16:12:46 → 16:13:01 |

Ladder verdict position: **no verdict produced.** The R2 comparator got past
the completion limb that voided the parent grade and **REFUSED at the next
reader**, `read_xy_u`, on `coarse/postProcessing/profile/1/profile_U.xy`: the
file has **4 columns**, the frozen reader requires exactly 6 (x y z Ux Uy Uz).
No triple, no p, no GCI, no band comparison was reached; none is quoted.

Source: `GRADE_F16_R2.err` (the refusal, verbatim in §3); `*/RC.txt`;
`*/log.icoFoam`; `*/40/`; `*/0/U` mtimes.

## 3. GATES

The comparator's stderr, verbatim (`GRADE_F16_R2.err`, first sentence):

    REFUSED: /home/ubuntu/Certonomous/verification/runs/F16_runs/coarse/postProcessing/profile/1/profile_U.xy has 4 columns; a `sets`/raw sample of one vector has exactly 6 (x y z Ux Uy Uz).

| gate | band (inherited) | coarse | medium | fine | triple | p | GCI | deviation | verdict | what stopped it |
|---|---|---|---|---|---|---|---|---|---|---|
| G-F16-1 E2 velocity-profile L2 | [4.101177e−05, 3.691059e−04] | not computed | not computed | not computed | none | none | none | none | **none — REFUSED (exit 2)** | `read_xy_u` column pin (6 ≠ 4) |
| G-F16-2 u at y = δ | [−0.31027839, −0.30884136] | not computed | not computed | not computed | none | none | none | none | **none — REFUSED (exit 2)** | same |

The gate rows therefore stand where the parent left them: **PENDING x2 at
`6f8048b9`.** This lane assigns no verdict the instrument did not print.

**Finding A — a SECOND bookkeeping defect in the frozen reader (L-342 class).**
`grade_f16.py`/`grade_f16_r2.py` `read_xy_u` pins six columns, measured against
`F6b_runs/.../line_k_nut_omega_p_U.xy`, whose set is `type midPoint; axis xyz`
(F6b `system/controlDict:37`). F16's registered set is `type midPoint; axis y`
(`cases/F16_stokes_second_problem/case/system/controlDict:39`, and on disk at
`coarse/system/controlDict:39`), and OpenFOAM's raw writer emits ONE coordinate
column for a single axis: the real files are **y Ux Uy Uz — 4 columns, 56/112/224
rows** at coarse/medium/fine. The R2 diff scope (regex only) did not cover this
limb; it was not visible until the completion limb was passed. Repair is a
further registration (reader keyed to the layout the registered dictionary
actually produces: `shape[1] == 4`, y = column 0, Ux = column 1), touching no
band, threshold, cap or label — supervisor's call, not this lane's.

**Finding B — the physics artefacts carry an IDENTICALLY ZERO solution (not a
bookkeeping matter).** At every level: `40/U` `internalField uniform (0 0 0)`;
every `profile_U.xy` at t = 1, 20, 40 has **0 non-zero rows**; every
`log.icoFoam` has **0 `Solving for Ux` lines** (only `Solving for Uy`, all
residuals 0) and `Courant Number mean: 0 max: 0` at every step. Cause, read
from the registered case: `blockMeshDict` declares **both `sides` (±x) and
`frontAndBack` (±z) as `empty`**
(`cases/F16_stokes_second_problem/case/system/blockMeshDict:18-19`), so x is a
non-solved direction and icoFoam never solves the Ux component the oscillating
wall drives (`0/U` wall BC `uniformFixedValue sine` in x). The 0/U on disk
carries a non-zero initial profile; the first step zeroes it. A corrected reader
would return E2 = ‖u_exact‖/U0 at every level (identical values → triple
`EXACT`/`STAGNANT` → **NOT A RESULT** under rule 5), and the registered
prediction p ≈ 2 could not be tested on these artefacts. The case needs the
x-direction made a solved direction (e.g. `cyclic` sides on a 1-cell-wide
periodic slab) and a NEW run — new compute, new pre-registration; not this lane's
to do.

Registered prediction p ≈ 2: **NOT TESTED** — no observed order was produced.

Planted-zero and other controls: all 8 green at the selftest that ran inside
the grade invocation before the refusal (symbolic substitution; PZ-F16-EXPONENT;
truncation floor; constant-ratio refinement; PZ-F16-CLASSC; grade_ladder
call-site census; solver tolerance; **PZ-F16-R2-REAL_LOG_EXCERPT**: planted 5,
direct 5, parent-form 0, completion 5, negative "no `Time =` lines").

Freeze verification (rule 2): `grade_f16_r2.py` disk blob `8037cbef` ==
`git rev-parse ebe1b893:cases/F16_stokes_second_problem/grade_f16_r2.py`;
parent `grade_f16.py` `679823ff` unchanged at HEAD; `exact_stokes.py`,
`run_f16.sh` and both pre-registrations untouched.

Source: `GRADE_F16_R2.err`; `coarse/postProcessing/profile/{1,20,40}/profile_U.xy`;
`*/40/U`; `*/log.icoFoam`; `coarse/system/controlDict`; `coarse/0/U`;
`coarse/constant/polyMesh/boundary`; `cases/F16_stokes_second_problem/case/system/blockMeshDict`.

## 4. FD TABLES

nothing

Source: not applicable — no adjoint or finite-difference rung in this campaign.

## 5. REFILLED QUEUE

nothing

Source: no queue refill performed by this lane; ranking is the supervisor's.

## 6. WAITING LIST

- F16 gate rows G-F16-1, G-F16-2: PENDING at `6f8048b9`; R2 REFUSED at the
  column pin. Waits on the supervisor: (i) a reader registration covering the
  single-axis 4-column layout, and (ii) a case repair for the empty-x defect
  (Finding B) with a new costed pre-registration and new compute — without (ii),
  (i) can only return NOT A RESULT on identical zero-field values.
- F15-R2: NOT registered by this lane. The same column-pin defect is measured
  in F15's preserved artefacts (`F15_runs/coarse/postProcessing/lineWall/9.95/lineWall_p.xy`
  is **2 columns** x p from `axis x`; `read_xy_p` pins 4), so a regex-only R2
  would refuse at the same limb. Referred with the F15 scope question.

Source: this file §3; `F15_runs/coarse/postProcessing/lineWall/`; `grade_f15.py:123-136`.
