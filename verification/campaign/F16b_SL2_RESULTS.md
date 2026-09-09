# F16b-SL2 — Stokes' second problem (±x CYCLIC), `icoFoam` — RESULTS

**Team cfd.** Pre-registration `verification/campaign/F16b_SL2_PREREGISTRATION.md`,
**frozen at `cadb4887b505af082c63e977fd4fdf73e9878b46`**, inheriting F16's gates,
bands and three-level ladder verbatim (`F16_SL2_PREREGISTRATION.md` at `2aea29d9`).
F16b is the successor to F16, whose ±x `empty` patches left Ux a non-solved
component (identically-zero fields, closed **NOT A RESULT** on physics, calibration
row C-123); F16b is the same case with a one-cell CYCLIC pair in x. Graded
2026-08-26 at **zero new compute** by a cfd lab-lane; check-1 (grader diff) and
check-3 (verdict) cleared by the cfd-supervisor before filing.

## 0. VERDICTS — fixed vocabulary

| gate | fine value | registered band (inherited verbatim) | triple (coarse, medium, fine) | observed p | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F16-1 `E2_velocity_profile_L2` | **1.319909e−04** | [4.101177e−05, 3.691059e−04] | **CONVERGING**, monotone, r = 2.000 (dim 1) | **1.8252** | 137.1876 % = 1.810751e−04 absolute | **PASS** |
| G-F16-2 `u_at_delta` (ωt = 0 mod 2π) | **−0.309394169** | [−0.310278390, −0.308841361]; exact −0.309559876 | **CONVERGING**, monotone, r = 2.000 (dim 1) | **1.9930** | 0.0673 % = 2.082305e−04 absolute | **PASS** |

The 137 % relative GCI on G-F16-1 is the relative form on a quantity whose
Richardson extrapolant is near zero (−1.29e−05); the **absolute GCI 1.81e−04**
carries the meaning. Both printed exactly as the grader printed them (rule 1: the
value and interval carry the honesty, never adjectives).

## 1. PROVENANCE RECONCILIATION

The 2026-08-26 launch record `verification/campaign/F15_F16_LAUNCH_RECORD_2026-08-26.md`
records a **`BLOCKED` verdict, 0 core-min**: it documents ONE *direct* launch of
`run_f16.sh` that the auto-mode classifier DENIED, correctly not routed around, at
a moment when both run roots were ABSENT. **The completed F16b runs came from a
LATER, legitimate launch:** the queue daemon, launched **2026-08-26T16:42:02Z**
(`verification/queue/LAUNCH_LOG.tsv`, pid **189904**, ranks 1, prereg `cadb4887`,
status `cases/F16b_stokes_second_problem/STATUS.F16b_SL2`). This is the detached
OS-daemon path (independent of any agent) that does not present to the auto-mode
gate. Corroboration: `cases/F16b_stokes_second_problem/launcher.queue.out` shows all
three levels COMPLETE (1.25 core-min of cap 5); `STATUS.F16b_SL2` reads
`launcher_rc=0 end=2026-08-26T16:43:19Z`. The field mtimes (§3) fall inside this
16:42:02–16:43:19Z window. Graded PASS×2 at commit `49c95cc7` (17:05Z).

## 2. FROZEN FILES — disk == blob at the pre-registration commit

The grader that produced these verdicts is
`cases/F16b_stokes_second_problem/grade_f16b.py`, working-tree hash
**`a7d14ed9`**, byte-identical to `HEAD:cases/F16b_stokes_second_problem/grade_f16b.py`
and tracked/git-clean (check-1 clear). (The `F16b_GRADED.json` field
`parent_grader_blob = 8037cbef` records the R2 *lineage* the grader was derived
from, not the file that ran.) The pre-registration §0 records 11 of 11 frozen paths
disk == blob at `cadb4887`, re-verified before grading. Gated by
`scripts/roache_triple.py::grade_ladder` — exactly one call node, 0 `assert` nodes
across 2 files. Run under plain `python3` (the grader exits 2 under `-O`).

## 3. RULE 4 — strict completion, re-read at the run root by this lane

| level | cells | `RC.txt` | `End` | `Time =` lines == endTime/Δt | last Time == endTime | fields at `40/` | age guard: `0/U` → `40/U`, `40/p` (UTC 2026-08-26) |
|---|---|---|---|---|---|---|---|
| coarse | 56 | 0 | 1 | 16000 == 16000 | 40 == 40 | U p | 16:42:04.968 → 16:42:11.071 / .071 — **NEWER-OK** |
| medium | 112 | 0 | 1 | 32000 == 32000 | 40 == 40 | U p | 16:42:11.411 → 16:42:26.582 / .582 — **NEWER-OK** |
| fine | 224 | 0 | 1 | 64000 == 64000 | 40 == 40 | U p | 16:42:26.940 → 16:43:19.156 / .157 — **NEWER-OK** |

Age guard PASSES at every level: each field at `endTime` is strictly newer than that
case's own `0/U`. Serial, 1 rank, `decomposePar` never invoked. The grader's
`completion()` agrees (`done: True`, `n_times` 16000/32000/64000, `latest` 40.0).

## 4. RULE 5 — the limbs, in order

1. **Iterative convergence:** census of every step's final p residual against
   1e−09 — **0 above tolerance at every level** (32,000 / 64,000 / 128,000 readings;
   worst 9.99953e−10 / 9.99983e−10 / 9.99987e−10). Class C on the phase-locked
   series, 40 samples, 12-period window: **PLATEAUED** at every level (relative
   drift over the window ≤ 7.32e−08).
2. **Triple:** CONVERGING, monotone on both rows (r21 = r32 = 2.000).
3. **Band:** both fine values inside the registered band → **PASS**.

**Registered prediction (prereg §5) — MET:** observed order p ≈ 2 (1.83 on the L2
profile error, 1.99 at the point value); E2_fine measured / analytic prediction =
1.319909e−04 / 1.230353e−04 = **1.07**. F16's Finding B is closed on the artefacts:
`Solving for Ux` appears at every step (16,000 / 32,000 / 64,000 lines; F16: 0/0/0).

**Planted-zero control (rule 3): PASS on both gates**, into the real fine artefact
`verification/runs/F16b_runs/fine/postProcessing/profile/40/profile_U.xy` through
the real 4-column reader — `e2_from_xy` planted 1.085209e−03 / read back 1.085209e−03;
`u_at_delta_from_xy` planted 1.234e−03 / read back 1.234e−03. A zero here would be
trustworthy because each reader was shown seeing the non-zero perturbation. All 9
registered controls passed. **Independently reproduced live** by this lane
(re-graded with the frozen `grade_f16b.py`, rc 0, verdicts and values identical to
`F16b_GRADED.json`).

## 5. COST — rule 12 (calibration row C-127 already landed)

| item | value |
|---|---|
| predicted (prereg §8 at `cadb4887`) | **~0.5 core-min** = F16's measured 0.4167 × ~1.2; registered cap **5** |
| actual, MEASURED (ClockTime × ranks ÷ 60) | coarse 7 s → 0.1167; medium 15 s → 0.2500; fine 53 s → 0.8833; **1.2500 core-min gross** |
| cleaned | 1.2500 (== gross; longest level 53 wall s, nothing matches the 3600-s stall rule); 25.0 % of cap |
| waste, named separately | 0.000 core-min |
| quantisation | ± 0.0083 core-min per level (integer-second ClockTime) |
| derived dollars | 1.25/60 × $0.0513 = **$0.00107 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **2.50** — MISPREDICTION OF THE BASIS (F16's basis was the degenerate zero-field run: all 128,000 fine p-solves at 0 iterations, no Ux; F16b's fine level does 128,000 p-solves at 19–21 iterations + 64,000 Ux solves). Contention negligible (ExecutionTime 50.87 s vs ClockTime 53 s at fine). |

The estimate-vs-actual comparison is recorded in `docs/COST_CALIBRATION.md` **row
C-127** (landed at commit `49c95cc7`; a second launch-to-STATUS-wall basis for the
same run is added, non-duplicatively, by correction row **C-186**). **No new
calibration row is written for this filing** — the process's row already exists;
adding another would duplicate in an append-only ledger (the failure C-186 records).

## 6. DISCLOSURES — known items, not edits (rule 6: frozen files untouched)

- **Frozen pre-registration §8 textual defect, disclosed not edited:** the dollar
  figures were written with an unquoted `$0`, which the writing shell expanded to
  its own name (e.g. "`/bin/bash.0004`"). The intended figures reconstruct from the
  stated core-minutes: 0.5 × $0.0513/60 = $0.0004 predicted, 5 × $0.0513/60 =
  $0.0043 at the cap. **No figure in core-minutes, and no band, cap or label, is
  affected.** The frozen prereg is not edited (rule 6); whether a dated addendum is
  wanted is the supervisor's call.
- **`CAP_OVERRUN.txt` on disk (`cases/F16b_stokes_second_problem/`):** it recorded
  wall 60 s > 1.10 × a per-level queue *projection* of 30 s and states "**CAP
  OVERRUN REPORTED, NOT ENFORCED … the run was NOT killed (caps report)**". The
  binding pre-registered gate cap is **5.0 core-min**, and actual spend 1.25 is well
  under it — **no rule-12 pre-registered budget breach.** This file is a fossil of
  the old estimate-trigger (fixed at HEAD by `117bf190`); it predates the fix and
  will not regenerate (see C-186).
- **L-342 bookkeeping defect:** the grader flagged `STATUS.F16b absent under the run
  root` (the queue wrote `STATUS.F16b_SL2` in the case dir, an infrastructure field);
  the grade proceeded and the cost was read from the logs. Physics verdicts
  unaffected.

## 7. NOT SENT

No change to any F16 band or label; F16's row stands NOT A RESULT on physics.
**Nothing is sent, filed, uploaded or submitted outside the box** (rule 7). Field
data stays on disk under `verification/runs/F16b_runs/`.

**Artifacts (absolute under `/home/ubuntu/Certonomous`):**
`verification/runs/F16b_runs/{coarse,medium,fine}`;
`verification/runs/F16b_runs/{F16b_GRADED.json,F16b_GRADED.out,RESULTS.md}`;
`cases/F16b_stokes_second_problem/{grade_f16b.py,run_f16b.sh,launcher.queue.out,STATUS.F16b_SL2,CAP_OVERRUN.txt}`;
`verification/campaign/F16b_SL2_PREREGISTRATION.md` (frozen `cadb4887`);
`verification/queue/LAUNCH_LOG.tsv`; `docs/COST_CALIBRATION.md` rows C-127, C-186.
