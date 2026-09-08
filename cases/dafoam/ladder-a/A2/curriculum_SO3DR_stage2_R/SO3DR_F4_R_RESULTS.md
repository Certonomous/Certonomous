# SO3DR-F4-R — RESULTS. **`NOT A RESULT | HIGH-CONFOUNDED`.** The clean 36-leg F4 record the parent (Stage-2) could not produce, recovered by an INVOCATION-ONLY, VALUE-INVARIANT re-grade (verification ruling b44a0376). Structured on the REPORTING_CHARTER §2 six-heading frame.

    SO3DR-F4-R RESULTS
    Date:       2026-09-08
    Assembled:  2026-09-08T21:00:22Z
    Sections:   6 of 6
    Missing:    none

## 1. SPEND

The 36-leg campaign is INTACT and was NOT re-solved — only re-graded (invocation-only). The solve
cost is the measured campaign actual.

- **Actual: 74.8666 core-min** (36 legs, `np = 4`), measured from the run logs. cost_basis = **measured**
  (core-minutes from logs).
- Pre-registered estimate: **66 core-min** (PREREGISTRATION.md §5). **Ratio actual/predicted = 1.134.**
- Cap **198 core-min NOT hit** (74.8666 << 198). **No waste** — no stall, no infra kill.
- Dollars **DERIVED, NOT MEASURED, reported-by-owner** at $0.0513/core-h (COMPUTE_BUDGET_CHARTER §5;
  the box cannot read its own billing): 74.8666 core-min = 1.2478 core-h → **$0.0640**. Under $25.
- The re-grade itself is a host-only reader (seconds of a single core); not separately costed.
- Rule-12 calibration row filed in `docs/COST_CALIBRATION.md`.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-SO3DR-STAGE2R-a2-cl04-standalone-20260908T181559Z/`; `cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R/PREREGISTRATION.md`; `docs/COST_CALIBRATION.md`

## 2. LADDER POSITIONS

Ladder A, rung **A2** — the cl04-standalone discrimination experiment, SO3DR Stage-2 successor "R"
(SO3DR-F4-R). This item exists because Stage-2's F4 echo-check hard-REFUSED (exit 2) on **32 of 36**
legs whose `injected_dv.json` sidecar was absent (the frozen Stage-2 rig wrote the echo AFTER
`prob.run_model()`, so the write was never reached on the 32 primal-raised legs). The successor "R"
moved the sidecar write to BEFORE `run_model` (ordering-only, zero physics), giving a clean F4 record
on all 36 legs. **This is that clean record.** The A2 item is now GRADED, not owed.

Source: `cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R/PREREGISTRATION.md` §0, §2

## 3. GATES

**G-SA-DISCRIM → `NOT A RESULT` | discrimination `HIGH-CONFOUNDED`.** Verdict from the fixed six-token
vocabulary; the discrimination direction is the separate `discrimination` channel, never a verdict token.

- `r_sa = 32/36 = 0.8889` (fraction of the 36 completed legs carrying the `Primal solution failed!`
  banner).
- `r_fail = 24/24 = 1.0000` (FAILED stratum, diagnostic — NEVER gated).
- `r_succ = 8/12 = 0.6667` (SUCCEEDED stratum, diagnostic — feeds F3).
- **F3 fired**: `r_succ 0.6667 > 0.10` with `r_sa ≥ 0.50`, so the nominal HIGH reading (`r_sa ≥ 50 %`)
  is **downgraded to `NOT A RESULT | HIGH-CONFOUNDED`** — a HIGH reading cannot be attributed to
  intrinsic cl04 primal pathology while the SUCCEEDED stratum is itself unstable. The gate can only turn
  a PASS/GATE REACHED **into** NOT A RESULT, never the reverse (rule 5); that is exactly what happened.
- **All 36 legs completed to rule 4** (0 incomplete); banners per leg ∈ {0,1} (F2 clean).

**The finding is defect-robust — it is F3-borne, not F4-borne.** The parent Stage-2 could not emit any
F4 record (F4 refused on 32 absent sidecars). Here F4 grades cleanly on all 36 legs AND the answer is
still `NOT A RESULT | HIGH-CONFOUNDED` — carried by the F3 rig-confound arm, independent of the F4
repair. This reproduces the PREREGISTRATION §2 registered expectation (`r_succ = 66.7 %`, F3-borne)
exactly; it does not manufacture a new answer.

**All three controls fired and PASSED** (run WITHOUT `--skip-freeze`):
- `freeze_check`: 6 instruments extracted from the grader's own source (`control_planted_zero`,
  `count_banners`, `falsifier_f4_echo`, `falsifier_f6_sample`, `g_sa_discrim`, `leg_completed`),
  0 assert nodes.
- planted-zero control (rule 3): PLANT-SA-BANNER PASS (honest reader +1), blinded reader **caught**,
  PLANT-SA-DECOY PASS (a non-banner "failed" line NOT counted).
- **F6** (anti-gaming lock for the `--sample` override): sample **verified** — the with-`R` registered
  file was found and its **md5 == 55bf8e2d** confirmed against the frozen `SAMPLE_MD5`; strata 36/24/12
  and D6R log sha256 confirmed. F6 REFUSES on any mismatch, so a passing run proves the correct sample
  ran.

Grade json: `/home/ubuntu/certonomous-runs/CURRICULUM-SO3DR-STAGE2R-a2-cl04-standalone-20260908T181559Z/so3dr_stage2R_grade.json`

RULING 2's bar preserved: no `r_sa`/ratio is a verdict; the 39.7× is never computed.

Source: `.../so3dr_stage2R_grade.json`; `cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R/so3dr_stage2R_grade.py`; `cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R/PREREGISTRATION.md` §2, ADDENDUM §2d.1

## 4. FD TABLES

nothing

Source: this item is a primal-only banner-discrimination experiment (no adjoint, no `compute_totals`, no finite-difference step); there is no FD table to report.

## 5. REFILLED QUEUE

nothing

Source: no new run was enqueued by this re-grade (invocation-only; the 36-leg campaign is intact and was not re-solved).

## 6. WAITING LIST

The A2 SO3DR discrimination item is now GRADED. Because the answer is `NOT A RESULT | HIGH-CONFOUNDED`
(F3 rig-confound), the SUCCEEDED-stratum instability is NOT resolved: the experiment did not
discriminate "cl04's own primal pathology" from "multipoint aborted-trial coupling". Per
PREREGISTRATION §6 this item **may not** conclude a D6RF5-class primal fix is warranted. What remains
owed is the separate question the confound points to (the SUCCEEDED-stratum instability itself) — for
the supervisor to route; this record does not open it.

Source: `cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R/PREREGISTRATION.md` §6

---

*SUBMISSIONS PARKED. Prepared by dafoam lab-lane, 2026-09-08. The frozen grader was NOT edited; the
repair is invocation-only and value-invariant (grader md5 2d32ec9b, sample md5 55bf8e2d, gate
G-SA-DISCRIM byte-identical).*
