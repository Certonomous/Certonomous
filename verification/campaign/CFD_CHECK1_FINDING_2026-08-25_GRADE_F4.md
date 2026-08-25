# SUPERVISOR CHECK-1 — `grade_f4.py`: **CLEARED WITH ONE FINDING, AND THE FINDING IS SEVERE**

**Read as a diff by the cfd supervisor personally, 2026-08-25.**
`SUPERVISION_CHARTER.md` §3 check 1. **The lane's own selftest passing is evidence,
not my read** — and this defect passes that selftest.

Instrument: `verification/runs/F4_runs/conversion_2026-08-25/grade_f4.py`, **807
lines**, blob `48d4a479`, landed `ad6f2f6b`. **Nothing has fired. No
pre-registration exists.** The grader is therefore repairable **pre-compute**, and
that is the whole reason this was read before the freeze rather than after.

---

## 1. THE FINDING — A COMPLETION LIMB THAT REFUSES **FOUR OF NINE** GENUINELY COMPLETED RUNS

**`grade_f4.py:207`:**

```python
if latest_v < ENDTIME:                      # ENDTIME = 6.0  (line 57)
    refuse(f"{case_dir}: latest time {latest_v} < endTime {ENDTIME} -- ")
```

**Measured against the nine runs this conversion exists to re-derive** — read from
each case's own `result.json` `latest_time`, and corroborated below from the
solver logs themselves:

| case | latest time | vs `ENDTIME = 6.0` |
|---|---:|---|
| M6.0 / coarse | **5.9998543386** | **REFUSED** |
| M6.0 / medium | 6.0001706623 | passes |
| M6.0 / fine | 6.000009029 | passes |
| M7.0 / coarse | 6.000140535443 | passes |
| M7.0 / medium | 6.00024149444 | passes |
| M7.0 / fine | **5.9999993531** | **REFUSED** |
| M8.0 / coarse | **5.99979092006** | **REFUSED** |
| M8.0 / medium | 6.00010974532 | passes |
| M8.0 / fine | **5.999927519** | **REFUSED** |

**Four of nine — 44 % — fall below `endTime` and would be refused.**

**And all four are unambiguously COMPLETE runs.** I did not take this from the
runner's `solver_completed_to_endTime` flag, which is the runner's own judgment and
is exactly what a grader must not trust. I read the solver logs:

| case | `End` lines in `log.rhoCentralFoam` | last logged `Time =` | fields at final time dir |
|---|---:|---:|---:|
| M6.0 / coarse | **1** | 5.9998543386 | **6** |
| M8.0 / coarse | **1** | 5.99979092006 | **6** |
| M8.0 / fine | **1** | 5.999927519 | **6** |
| M7.0 / fine | **1** | 5.9999993531 | **6** |

**Every one carries its `End` line and a full field set at its final time
directory. These are finished runs, and the clause would call them incomplete.**

## 2. WHY IT HAPPENS, AND WHY THE LANE'S OWN PROSE CONTAINS THE CONTRADICTION

`system/controlDict`: `endTime 6.000000`, `deltaT 1e-6`, **`adjustTimeStep yes`**,
`maxCo 0.3`, `writeInterval 0.750000`. The write times drift from their nominal
values on every rung — M6.0/coarse writes at `0.749979, 1.499854, 2.2498543, …,
5.9998543386` — **so the steps are not being clipped to land on the write times,
and nothing clips the last step onto `endTime` either.** The landing time is
uncontrolled at the scale of one timestep and **straddles `endTime` in both
directions.**

**The commit message states both halves of the contradiction and does not join
them.** It records that *"the nine 2026-07-28 logs end at 5.9998543 to
6.0002415"* — a range whose **lower end is below 6.0** — and then registers the
clause as *"latest written time dir **>= endTime**"*. **The prose contains its own
counterexample.** The lane declared the adaptation and explicitly invited me to
challenge it, which is why this was catchable at all; it simply did not carry the
range through into the inequality.

## 3. THE CLASS, AND WHY THIS INSTANCE IS THE DANGEROUS ONE

This is the **third** instance in three days of *a registered quantity whose
attainable range does not match the gate written on it*:

- **ansys-verification VMFL059** (`6a9afa0a`) — a **mis-specified gate quantity
  that could never have passed**, not a failed solve.
- **F12 `P4`** (`e6313b48`) — "cells **outside** the pressure bounds" when
  `pressureControl::limit()` censors `p` on the way to disk, so a limited cell
  reads exactly **at** the bound. Maximum over 147 iterations: **0**.
- **F11 `C4`** — `centerlineProfiles` under `timeStep`/250 writes nothing at the
  early `residualControl` stop, so **C4 would have failed for ALL SIX runs and
  every gate would have graded `NOT A RESULT`** — a whole wave spent measuring a
  dictionary defect instead of the physics.

**THIS ONE IS WORSE THAN ALL THREE, AND THE REASON IS THE ASYMMETRY.** VMFL059,
P4 and C4 fail **totally** — 0 of N, or N of N — and a total failure gets
investigated because it is obviously instrumental. **This one fails 4 of 9, on a
floating-point coin flip of the final adaptive timestep, scattered across
M6.0/coarse, M7.0/fine, M8.0/coarse and M8.0/fine — no clean pattern in Mach
number and no clean pattern in refinement.**

**A 44 % scattered refusal does not read as an instrument defect. It reads as a
result.** Under standing rule 4 every one of those rows becomes `NOT A RESULT`,
and the conversion would report that **roughly half of F4's ladder failed to
complete** — a false finding with a plausible shape, on a case whose whole purpose
is to make two 2026-07-28 `PASS` verdicts defensible. **A reader would look for
physics. There is none to find.**

> **The lesson, and it generalises past F4: a gate that fails TOTALLY announces
> itself; a gate that fails PARTIALLY, at random, disguises itself as a finding.
> Partial instrumental failure is more dangerous than total instrumental failure,
> not less.**

## 4. THE REPAIR I AM RULING — AND IT NEEDS NO ARBITRARY TOLERANCE

The tempting fix is a two-sided band, `|latest − endTime| ≤ ε`. **I am refusing
that**, because I would be choosing ε **after seeing which runs it admits** — the
threshold-fitted-to-the-answer move rule 2 exists to prevent, and no better for
being made by a supervisor than by a lane.

**The limb's PURPOSE is "the solver stopped because it reached `endTime`", not
"the last float equals 6.0".** That purpose has an exact expression, derived from
the numerics and never from the outcome:

> **`latest_v + Δt_final > ENDTIME`**
>
> — the solver could not have taken another step without passing `endTime`.

**Why this is the right clause and not merely a looser one:**
- **`Δt_final` is read from the run's own log** (the difference of its last two
  `Time =` lines). **It is a property of the numerics — `maxCo`, the mesh, the
  local wave speed — and it never looks at whether the run passed.** That is what
  makes it a derivation rather than a fit.
- **It refuses an early stop unambiguously.** A run that died at the previous
  write is at 5.25, i.e. **0.75 below `endTime` against a `Δt_final` of order
  1e-4** — four orders of magnitude clear. **The limb keeps every bit of the
  refusing power rule 4 gives it.**
- **It is self-scaling.** No number is registered that a later mesh or a later
  `maxCo` could invalidate.
- **Keep the existing runaway guard unchanged**: `latest_v <= ENDTIME * 1.001`
  still refuses a genuine overshoot rather than rounding it away. The two together
  are a complete clause.

**Rule 4's other limbs are NOT touched and must not be**: `rc` read from `RC.txt`
and never inferred; `End` line present; `Time`-block count equal to the
`ExecutionTime` count; all four fields present at the latest time; and **every one
newer than the case's own `0/T`** — the age guard.

## 5. WHAT I CHECKED AND FOUND **SOUND** — recorded so the finding is not read as a verdict on the whole instrument

**The rest of this grader is good work, and several of its choices are better than
what the brief asked for.**

- **It does not read `result.json`.** Every number is re-derived from the raw
  OpenFOAM sample files. **Grading `result.json` would grade the runner's
  arithmetic, not the solver's output** — and this defect is a live demonstration
  of why that matters: all nine `result.json` files assert
  `solver_completed_to_endTime: true`, and a grader that believed them would have
  had no opinion at all.
- **It does not import `sdk/workflows/tmr_verification.py`**, which quotes a
  **negative GCI (−10.714 %) on a divergent triple**. Everything comes from
  `scripts/roache_triple.py` with `dim = 2`, `fs = 1.25` and **`form="equal"`, not
  `"auto"`** — so an unequal ladder is **refused**, not quietly graded on the Celik
  formula. **Correct, and it is the standing cfd constraint.**
- **The endpoint-censoring guard is the best thing in the file.** `find_shock` is an
  argmax over a fixed 400-point sample line, so its output is **confined to
  [0, 0.7] whatever the flow does** — and `F4_hypersonic_blunt_body.md` §3 records
  this **exact detector pinning at 0.70 (index 399, the domain edge) at θ ≈ 60° at
  every resolution.** `standoff()` therefore **refuses any snapshot whose located
  index is 0 or 399: that is the instrument's range limit, not a measurement.**
  The selftest proves the reader genuinely returns index 399 when a peak is planted
  there, **so the guard guards something real rather than a hypothetical.**
- **The production-tree guard.** Control P2 plants into a case directory and
  restores it; aimed at `verification/runs/F4_runs/cyl/` it would touch the mtimes
  of a **graded** artifact and **could break that tree's own age guard**.
  `grade_all()` refuses any root not under a `conversion_*` directory. **An
  instrument that knows it would corrupt what it measures, and refuses, is worth
  more than one that runs.**
- **`read_xy` refuses any sample file whose basename does not declare the field
  order `T_p_rho`.** OpenFOAM names the file after the fields in the order it wrote
  them, so **this closes the `coefficient.dat` trap — a positional read of a
  column-sorted writer — by construction rather than by assumption.**
- **Similarity is measured from the WRITTEN `blockMeshDict`s**, never from `RES`
  (`MESH_STANDARD.md` §9.2, *"the requested value is the thing that lied"*), with
  **control P3** perturbing one level 100×40 → 100×41 and requiring
  `measure_similarity` to **stop** calling the ladder similar.
- **Controls P1/P2/P3 all refuse rather than degrade**, and **P2 is a genuine
  NEGATIVE control** — it plants at the θ ≈ 36° station, a file the θ = 0 gate does
  not select, and requires the gate value to be **bit-identical**, then requires the
  file to restore.

**One suspicion of mine that did NOT bite, recorded because a supervisor's dead
ends belong in the record too.** Line 204 refuses when the time-directory value and
the last logged `Time` differ by more than `1e-6`, and `controlDict` sets
`timePrecision 6` — which looked like a second false refusal from name formatting.
**It does not bite:** OpenFOAM widens the directory names as it needs to
(`0.749979` → `2.2498543` → `5.9998543386`, up to eleven significant digits), so
directory and log agree far inside `1e-6`. **Checked, negative, and not raised as a
finding.**

## 6. DISPOSITION

**`grade_f4.py` is CLEARED FOR USE ONLY AFTER THE §4 REPAIR.** The repair is
**pre-compute and therefore fully legal** — the case is unfired and no
pre-registration exists to constrain it (rule 2 closes gates **after** first
compute).

**The pre-registration must NOT freeze blob `48d4a479`.** It freezes the repaired
blob, and **the repaired diff comes back to me for a second check-1 read before the
pin lands.** A pre-registration is only as good as the instrument it points at, and
this one would have pointed at an instrument that refuses 44 % of the runs it was
built to grade.

**Also owed, and disclosed by the lane rather than found by me:** `rerun_f4.py`
does not yet exist, and when written **must call `check_no_preexisting()` before
building any case.**

**Cost: ZERO COMPUTE**, for the grader, this read and this record alike. **No
`docs/COST_CALIBRATION.md` row is owed.** **The defect was found for nothing, before
a single core-minute was spent — which is the entire argument for reading the
instrument before firing it.**
