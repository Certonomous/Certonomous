# M6CP1 L2 STAGE 4 — STOPPED BY SUPERVISOR DECISION AT 759 STEPS. **NOT A COMPLETED RUN.**

**Drafted by a cfd `lab-lane`, 2026-09-10, UNCOMMITTED. Not a grading record and not a verdict.**
**No gate, threshold, cap, band or label is touched by this file.** Gate P and Gate G were never
evaluated. Amendment 2's `NOT A RESULT` park is not lifted by anything here.

## 1. 🔴 `RC.txt` READS `RC=143` AND THAT IS A DECISION, NOT A CRASH

`RC=143` is 128+15, **SIGTERM**, sent deliberately to solver pid 1597168 at **21:37:56Z** by the lane
on the cfd-supervisor's registered early-stop condition. It is written by the wrapper, from the
solver process, exactly as §8 requires. **A later reader must not triage it as a failure.**

**This run does NOT satisfy standing rule 4 and no part of this file claims it does.** There is **no
`End` line**, the last time is **759 against `endTime` 5000**, and the autograder did **not** run —
the wrapper grades only on `RC=0`, so no verdict was produced. **It was stopped; it did not finish.**

| field | value |
|---|---|
| solver pid | 1597168 |
| wrapper pid / PPID | 1596907 / **1** (re-parented to init) |
| cwd | `verification/runs/M6CP1_runs/L2/case` (read from `/proc/1597168/cwd`) |
| ranks | 1, serial (`nProcs : 1` in the log banner) |
| registration | commit `f10240915`, blob `8967bf016088baf82ceecf3312549ea55a50ffcf` |
| launcher | `scripts/case_protocol_stage4_run.py` blob `ce70fa814e2fe59a6630839fb408fc145e788bf6` (commit `7d7fcebf`) |
| launched / finished | 21:30:28Z / 21:37:56Z |
| steps / wall / cost | 759 / 448 s / **7.467 core-min** (from `STATUS.stage4`) |
| time directories written | 100 200 300 400 500 600 700 |

## 2. THE PREDICTIONS REGISTERED IN ADDENDUM 3, GRADED AGAINST WHAT RAN

### P1 — BIT-IDENTITY THROUGH STEP 400. **CONFIRMED, AND NOT BY SPOT CHECK.**

Both logs were parsed by **the same code** and compared step by step. **400 common steps. The
smoothed flow time scale maximum and BOTH `limitTemperature` counts are identical at every
comparable step.**

| step | live smoothed max | M0 smoothed max | live lo/up | M0 lo/up |
|---:|---|---|---|---|
| 1 | 9.119010831e-05 | 9.119010831e-05 | 0/0 | 0/0 |
| 50 | 1.251459718e-05 | 1.251459718e-05 | 93/57 | 93/57 |
| 100 | 9.600337404e-05 | 9.600337404e-05 | 47/2 | 47/2 |
| 200 | 2.72679683e-05 | 2.72679683e-05 | 535/44 | 535/44 |
| 300 | 1.344690795e-05 | 1.344690795e-05 | 601/106 | 601/106 |
| 398 | 6.22050046e-06 | 6.22050046e-06 | 699/145 | 699/145 |
| **399** | **7.121542696e-06** | **7.121542696e-06** | **703/143** | **703/143** |
| 400 | 7.99434746e-06 | *(none — see below)* | **704/142** | **704/142** |

**The registered target `7.121542696e-06 s / 704 lower / 142 upper` is reproduced exactly.** The
figures come from two different steps of the M0 log — the smoothed value is the last LTS block M0
printed (step 399) and the clamp counts are its last clamp pair (step 400) — and **both reproduce to
every digit.**

**The one apparent mismatch is an artifact and is disclosed rather than swept up:** at step 400 the
M0 log has no LTS block at all, because M0's `endTime` is 400 and the solver writes and stops before
printing one. It is a **missing datum in the reference, not a difference in the trajectory** — the
clamp pair at that same step matches.

**A caveat on step LABELS, not on the comparison:** the parser attributes each LTS block to the
preceding `Time =` header, which offsets the index by one against a raw line-order reading. It cannot
affect the result, because both logs are parsed identically; only the absolute label is ambiguous by
one.

### P2 — COLLAPSE BELOW 1e-10 s. **NOT CONFIRMED. The threshold was reached and measured; the CLAIM was not verified, and the model behind it is FALSIFIED.**

| step | smoothed max | raw max |
|---:|---|---|
| 399 | 7.121542696e-06 s | 5.513522401e-03 s |
| 515 | first sample below 1e-10 s | 5.513522401e-03 s |
| 600 | 1.847168e-17 s | 5.513522401e-03 s |
| 758 (stop) | **1.553170667e-30 s** | **5.513522401e-03 s** |

**P2 asserts a state AT step 5000. THE RUN WAS STOPPED AT 759, SO THAT STATE WAS NEVER OBSERVED
AND P2 IS NOT CONFIRMED.** What was measured, precisely:

- **The threshold WAS reached: the first sample below 1e-10 s is at step 515**, and the value at the
  stop is 1.553170667e-30 s. That is a measurement and it is not withheld.
- **But it did not stay below. The trace re-crossed ABOVE 1e-10 s twice after step 515**, reaching
  1.713395e-10 s. A single crossing of this threshold is not a stable state, so "it was below at
  515" does not license "it is below at 5000".
- **The trace is non-monotone throughout: 320 of 757 step-to-step transitions RISE (42 %).** Over
  steps 1-400 it spans 6.2205e-06 to 1.8772e-04, a factor of 30.2, moving both ways. Forty-three of
  those rises occur after the crossing, the largest a 2.3× jump at step 617.
- **The log-linear model behind P2 is FALSIFIED.** Addendum 3 extrapolated ~1.1 decades per 400
  steps. The measured envelope falls ~24 decades over steps 400 to 758 — 7.994347e-06 at 400,
  5.683405e-09 at 500, 7.966286e-14 at 550, 1.847168e-17 at 600, 1.491850e-21 at 650,
  2.666741e-26 at 700, 1.553171e-30 at 758. **The collapse accelerates; it is not log-linear, and
  the extrapolation that predicted it assumed a monotone decay the trace does not show.**

**So P2 is recorded as NOT CONFIRMED with its threshold-crossing measured, rather than as confirmed
or as merely unverified.** Writing "confirmed" would claim an endpoint never reached; writing a bare
"unverified" would hide a crossing that was measured at step 515. **A prediction registered and then
not verified is a result, and a better one than a prediction quietly dropped.**

**The raw maximum never moves: 5.513522401e-03 s at step 1 and at step 759.** The freestream time
scale is healthy throughout. **Everything that collapsed was put there by `fvc::smooth`**, which is
A2.3's mechanism observed directly rather than inferred: raw min fell to 1.239776355e-34 s and the
smoothing operator propagated it across the field.

### P3 — CLAMPS LIT AT BOTH ENDS. **CONFIRMED.**

`limitTemperature` fires at both ends throughout, and pins **at** its own limits
(`UnlimitedTmin = 100`, `UnlimitedTmax = 1000`) — §9's signature of unbounded, not of a finite hot
value. Against this registration's own prediction of **`max_clamped_cells = 0`**, that is a fail on
the clamp limb.

**A behaviour worth recording because it inverts the naive reading:** the clamp counts **fall** as the
run proceeds — 704/142 at step 400, 128/58 by step 674. **Fewer cells are being clamped because
fewer cells are moving.** A monitor watching clamp counts alone would have read the collapse as
recovery.

## 3. WHAT THIS DOES AND DOES NOT ESTABLISH

**It establishes that the stage-4 graded configuration reproduces the M0 baseline exactly** — the
`endTime 400 → 5000` one-line diff is the only difference, and the trajectory confirms it to every
printed digit — **and that the LTS collapse continues past step 400 to 1.55e-30 s.**

**It establishes nothing about Gate P or Gate G, which were never evaluated**, and nothing about the
cusp's causal role. A2.8's honest limit stands: distinguishing "mesh topology defect" from "unstable
scheme" needs the same numerics on a wake-cut or blunt-TE grid, which is a successor registration.

**It also does not establish that a longer run would have collapsed further**, only that it had
collapsed to 1.55e-30 s when it was stopped.

## 4. COST (rule 12), AND THE ESTIMATE-VERSUS-ACTUAL

**Measured: 448 wall s × 1 rank = 7.467 core-min**, from `STATUS.stage4`, which the wrapper wrote
from the solver process. **$0.00638 DERIVED, NOT MEASURED** at $0.0513/core-h — the box cannot read
its own billing.

| | value |
|---|---|
| predicted rate (M0 smoke, measured) | 0.325 s/step |
| actual rate | 448 / 759 = **0.590 s/step** |
| ratio actual/predicted | **1.82×** |
| attribution | **CONTENTION**, named separately and not absorbed: 12 CPU-bound ranks were already on 16 vCPU at launch (9 `simpleFoam`, 1 `buoyantBoussinesqSimpleFoam`, 1 `rhoCentralFoam`, 1 `snappyHexMesh`); M6CP1 was the 13th core. No waste and no misprediction of the per-step cost is claimed. |

Addendum 3 estimated **27.1 core-min** for the full 5000 steps. **7.467 core-min was spent for 759
steps**, i.e. 15.2 % of the steps for 27.6 % of the budget, the gap being the 1.82× contention factor.
**The remaining ~19.6 core-min was not spent, because the run was stopped once it had answered.**
The rule-12 row for `docs/COST_CALIBRATION.md` is owed and is **not** discharged by this file.

## 5. THE STAGE-4 LAUNCHER'S REPAIR WAS EXERCISED ON A REAL SOLVE

`log.foam_bashrc_source` is present at **0 bytes** — the guarded source ran clean and its stderr is
no longer discarded. The launch verifier recorded `status_file: True`, `age_guard_touched: True`,
`early_rc: None`, `zero_T_mtime_before: 1788915818.5089564`, and `0/T` advanced to
1789075828.807101918. **The strict-increase witness fired on real data, not on a fake solver**, and
`RC=143` proves the wrapper's rc capture propagates a real non-zero from a real solver process.

**One residual labelling defect, disclosed and NOT repaired here:** `STAGE4_MANIFEST_L2.json` records
`launch_pid: 1596906`, which is the **`setsid` parent**, not the solver (1597168) and not the wrapper
(1596907). Nothing depends on it — liveness is asserted from the artifact witness, never from that
pid — but anyone who `ps`-es that number will wrongly conclude the run is dead. The follow-up is to
have the wrapper record the solver's own pid into `STATUS.stage4` and carry it into the manifest.
