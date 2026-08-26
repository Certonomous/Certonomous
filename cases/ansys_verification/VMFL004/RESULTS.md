# VMFL004 — Plain Couette Flow with Pressure Gradient: `NOT A RESULT`

## VERDICT: `NOT A RESULT` — a frozen-instrument block, NOT a physics failure

The verdict is `NOT A RESULT` because the frozen iterative-convergence check (rule 5
step 1) refused all three levels. **The gate physics is a textbook PASS** and is
recorded here beside the verdict so the finding is not lost. Drafted by
`ansys-lane-opus48` (Opus 4.8), 2026-08-26, for the supervisor's triage.

### The physics (would be a PASS)

Gate quantity `volAverage(U)_x` against the exact lab-evaluated section mean
⟨u⟩ = ∫₀¹(9y−6y²)dy = **2.5 m/s**:

| level | volAverage(U)_x | rel_dev (band 1e-3) |
|---|---|---|
| L1 (15×40) | 2.50125 | 5.0e-4 |
| L2 (30×80) | 2.5003125 | 1.25e-4 |
| L3 (60×160) | 2.50007812 | 3.1e-5 |

Triple **CONVERGING**, observed order **p = 1.99999997**, extrapolated
**2.4999999993** (2.5 to 9 digits). Fine-grid rel_dev 3.1e-5 is ~30× inside the
0.1 % band. Planted-zero fired on all levels. **The EXACT-collapse risk named in the
prereg did NOT fire** — gating on the volAverage (whose cell-midpoint-quadrature error
is O(h²) and non-zero) gave a clean CONVERGING triple, exactly as designed; central
differencing being exact for the quadratic did not defeat the gate.

### Why the verdict is nonetheless NOT A RESULT

The inherited-and-frozen `iterative_convergence` check requires `Ux_initial`,
`Uy_initial`, `p_initial` all < 1e-7. In this 1-D fully-developed flow **Uy and p are
physically ~zero fields**, so their NORMALIZED residuals are pure normalization noise:
at endTime Ux_initial = 3.2e-13 (converged), but Uy_initial = 4.9e-2 and p_initial =
9.2e-2 (they even ROSE from ~8e-4 at iter 10001 — bouncing, not converging). Per rule
2 the frozen comparator is not edited after compute, so the honest verdict stands.

### Recommendation (a NEW row, charter §6)

A corrected re-run that gates iterative convergence on the DRIVEN channel (`Ux_initial`)
only — or on a physically-meaningful convergence measure for a degenerate transverse
field — would deliver the `PASS` the physics supports. That is a new pre-registration
and a new register row citing this one; it does not alter this frozen row.

### The lesson (→ LESSONS L-338, for the supervisor to land)

**A 1-D fully-developed flow has degenerate transverse-momentum and pressure fields
whose normalized residuals are noise, not a convergence signal; an iterative-convergence
gate must not require them below a floor.** Gate convergence on the driven channel, or
on a residual normalized against a non-degenerate reference. Cost of the miss: one
PASS-quality run graded NOT A RESULT. I froze an inherited grader without catching this
(I named the EXACT-collapse risk but missed the degenerate-residual risk). Corroborated
same session by VMFL011's contrast: its genuinely 2-D cavity drove Uy/p to 1.2e-13 /
8.9e-13, so the same check is harmless there.

### Provenance
- **Prereg sha:** `0e61889534d0e7180a105190f7ead06e3c00b432`.
  **Comparator sha:** `ddea9d473b6d6092427d29c5997c25af956a7fb6`.
  **Grading:** `verification/runs/ansys_verification/VMFL004/GRADING_VMFL004.json`.
- **Ceiling:** PASS/HOLDS (Ruling 2; VMFL019 precedent verified — a category-V closed
  form earned a rule-1 PASS). The block is the convergence instrument, not the ceiling.
- **Comparator `--selftest`:** 19/19 exit 0, IDENTICAL under `python3` and `python3 -O`;
  `mutation_test_vmfl004.py` 6/6 exit 0 under both. No `assert` carries any control.
- **0/ reconciliation:** the 03:10Z dead-lane fields used inlet/outlet/topWall/bottomWall
  (absent from the mesh); reconciled to movingWall/fixedWall/left/right before any run.

## COST (rule 12 calibration — actual vs pre-registered)

- **Measured actual:** 11.4 core-min total (L1 0.35 + L2 1.667 + L3 9.4; ranks=1), from
  `RUN_RC.txt`/`COST.txt`. Cap 30 (0.38 of cap; no overrun).
- **Pre-registered estimate:** clean ~2–3 core-min (prereg §7), slack ×~10 → cap 30.
- **Ratio actual/clean-estimate ≈ 4.6** — the clean estimate was too low: L3 alone was
  9.4 core-min (564 s for 20000 SIMPLE iters on 9600 cells = 28 ms/iter). The
  degenerate Uy/p never converge, so the run used the full 20000-iter budget rather than
  stopping early. No waste (rc=0 throughout); slack absorbed the miss.
- **$ derived (not measured):** 11.4 core-min × $0.0513/core-h ÷ 60 = **$0.0097**.

**Ledger follow-up (for the supervisor):** register row (verdict NOT A RESULT),
LESSONS L-338, and COST_CALIBRATION C-109 (re-derive numbers at commit, rule 11) are
owed; the content is above.
