# M6J_L1 — GRADING NOTE. READ BEFORE GRADING THIS RUN.

This run was **stopped, re-ranked 4 → 16 and resumed** on 2026-09-13 under
`M6J_TRANSONIC_FAMILY_PREREGISTRATION.md` **ADDENDUM 2** (committed `69bee3f2c`, in HEAD's
history). Nothing below changes a gate, threshold, cap or label. It exists so the grader
recognises four artifacts that look like defects and are not, and one that **is** a hazard.

---

## 1. THREE LOG SEGMENTS, AND THE STEP COUNT MUST BE A UNION

| segment | file | ranks | steps |
|---|---|---:|---|
| 1 — first-order ramp | `log.rhoSimpleFoam.startup` | 4 | `{1..200}` |
| 2 — registered schemes | `log.rhoSimpleFoam` | 4 | `{201..3886}` |
| 3 — resume | `log.rhoSimpleFoam.resume.1` | **16** | `{3801..8000}` |

**Count DISTINCT physics steps unioned across all three, never a line count.** Iterations
**3801–3886 appear in BOTH segment 2 and segment 3** — segment 2 ran them at 4 ranks before
the stop, segment 3 recomputed them at 16 after it. They are **one physics step each and are
counted once**. `scripts/solver_log_set.py:51-57` defines `log.<solver>.<anything>` as a
continuation and implements exactly this union; segments 1+2 were measured contiguous with
**zero gaps and zero overlap** before the resume, and the resume closes the set to `{1..8000}`.

Call the scanner with solver name **`rhoSimpleFoam`**, not `simpleFoam`.

## 2. `RANKS.txt` SAYS 16 AND IS TRUE ONLY OF THE LAST SEGMENT

`RANKS.txt` is **overwritten** at every launch, while `CORE_MINUTES.txt` and
`WALL_SECONDS_SOLVE.txt` **append one row per segment**. A cost reader that pairs every row
with `RANKS.txt` will cost segments 1 and 2 at 16 ranks and overstate them 4×.
**Use `RANKS_BY_SEGMENT.tsv`**, which pins the rank count per row.

## 3. `RC.txt = 1` AND `FAILURE_CONTEXT.1.txt` ARE THE DELIBERATE STOP, NOT A CRASH

The launcher writes `FAILURE_CONTEXT.<n>.txt` on **any** non-zero stage rc, and a `SIGTERM` is
one. `log.rhoSimpleFoam.stderr` is **0 bytes** — no MPI message, no `FOAM FATAL`, no signal
report. See `DELIBERATE_STOP_2026-09-13.txt`. **Do not spend a crash-triage check on it.`RC.txt`
is overwritten by the resume when it finishes.**

## 4. `postProcessing/forceCoeffs/` HOLDS A DESIGNED CONFLICT — DO NOT SUPPRESS IT

Directories `0/`, `200/` and `3800/`. Rows for iterations **3801–3885 exist in both `200/` and
`3800/`** and **disagree**, because they are the same iterations computed under two different
partitions. This is not corruption:

- `fo_series` (`cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py:171`) unions by start time,
  **the largest start time wins** — here `3800/`, the 16-rank run that produced the final
  answer — and **reports every competing value** so a reader SEES the disagreement.
- **That reporting is the designed path firing, not a defect.** Expect ~85 conflicting rows.
  Record them; do not silence them.

Those same 85 rows were used to bound the re-partition on the force coefficients:
**max |rel diff| Cd 1.62e-04, Cl 1.10e-04, CmPitch 1.77e-04**; mean ≈ 3.6e-05. Agreement is to
six decimals at `t=3801`, separating to ~1e-4 by `t=3885`. **That is round-off amplified by the
iteration — it is NOT machine round-off and must not be described as such.**

## 5. 🔴 THE HAZARD: `purgeWrite 2` DELETES TIME DIRECTORIES AND WILL DELETE YOURS

`writeInterval 200; purgeWrite 2` — the run keeps only the **last two** written times in
`processor*/`. **`t = 4000` was already destroyed** before it could be reconstructed; at
`Time = 4474` only `3800 4200 4400` remained.

Times rescued to the **top level**, where `purgeWrite` does not reach (the solver writes only
`processor*/`): **`3800/`, `4200/`, `4400/`**, each with the full field set
`{T U alphat nuTilda nut p phi rho}` + `uniform/` + `yPlus`. `4200/` was ~5 minutes from
deletion when it was rescued.

**If you need a time directory for any comparison, reconstruct it to the top level
immediately — within N write intervals of it being written, or it is gone, with no warning
and no error.** Draft lesson:
`verification/runs/M6J_runs/LESSON_DRAFT_purgewrite_deletes_the_comparand.md`.

## 6. THE RE-PARTITION IS A PERTURBATION, AND IT IS BOUNDED

`decomposeParDict` is now `numberOfSubdomains 16; n (2 2 4)`; the registered 4-rank file is
kept verbatim as `system/decomposeParDict.4rank.registered` (`n (2 2 1)`).

**The new partition is strictly NESTED in the registered one**, verified from
`cellProcAddressing` rather than asserted: each 16-rank subdomain lies wholly inside exactly
one 4-rank subdomain — old 0 = {0,4,8,12}, 1 = {1,5,9,13}, 2 = {2,6,10,14}, 3 = {3,7,11,15},
unions exact, global cell set identical at 983,040. **No registered cut plane moved; three
z-planes were added inside each.**

**Residual seam at the resume: no detectable jump.** The step ratio across `3800 → 3801` was
located inside the run's own scatter (300 consecutive-step log-ratios, iterations 3500–3800):
Ux, Uy, Uz, e, p all at **|z| < 0.8, percentiles 26–69%** — dead centre.

**§3 of the registration is weakened for L1 and ADDENDUM 2 §A2.2 says so:** §3 chose 4 ranks so
that L1's decomposition was byte-identical to its graded `transonic yes` counterpart, making
`transonic no` the only difference. At 16 ranks the L1 comparison differs in **two** ways. The
force bound above and the Cp bound below are what quantify the second one.

## 7. Cp BOUND — the graded read

The force bound in §4 is an **integral** of surface pressure; the gate reads Cp **locally** at
η = 0.65 and 0.90, and cancellation can hide a local difference inside an integral. The
overlap window of §4 **cannot** supply a local bound: it holds only per-iteration integrals,
residuals and clip counts — **no field data at all**.

Measured instead by `verification/runs/M6J_runs/M6J_L1_CP_CONTROL_4RANK/`: the preserved
4-rank state advanced `3800 → 4200` at `n (2 2 1)` against this run's `3800 → 4200` at
`n (2 2 4)` — one segment each, no intermediate restart, identical schemes, solvers,
relaxation and model. Compared point-for-point by
`verification/runs/M6J_runs/compare_cp_partition.py` using the family's **own**
`extract_cp_m6i.py`, so the number measures the partition and not two extractors.

**Result: see `CP_PARTITION_BOUND.txt` in this directory.**
