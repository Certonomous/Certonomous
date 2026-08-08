# S1 — weighted reinversion arm: pre-registration, staged per the d1b2c117 gate order

Item `s1-cbfs-weighted-reinversion-arm`, approved by chief ruling d1b2c117 at
**250 core-min hard cap**, gated in order: (A) masked-beta nonlocality control with a
stop-and-report trigger, (B) FD gate on the new objective configuration, (C)
pre-registered optimization. **Each part commits before its own solves run**; this
file grows by dated parts, never edited silently. Run root:
`/home/ubuntu/certonomous-runs/S1-cbfs-weighted-arm/` (own `ledger.csv`; case is a
copy of the REPAIRED reinversion case — benchmark inlet, `-primalTol 1e-8` protocol
throughout, `--cpus=2`, 4 ranks, strict queueing, setsid, per the standing
discipline).

## Part A — masked-beta nonlocality control (committed before the solve)

**Question:** does the achieved in-window fix ride on out-of-window beta through the
flow? Offline analysis could not rule it out (beta acts nonlocally); this is the one
solve that answers it, and per d1b2c117 it guards the remaining ~242 core-min.

**Construction, already on disk and verified:** `beta_masked.npy` = eval-16
`beta_final` where the serial cell (via the exact DV→serial permutation) lies in the
W2 support (window 0≤x/h≤6, 0≤y/h≤2, or y<0.5 anywhere), 1.0 elsewhere. 2,970 of
21,000 DVs keep their achieved values; 2,188 reset-to-1 cells had deviated by more
than 0.05 — the masked field is a real amputation, not a no-op.

**Protocol:** one fresh-container cold `run_model` at `-betafile beta_masked.npy
-primalTol 1e-8` (~8 core-min), fields written at 2500, reconstructed; R_W1 and R_W2
recomputed host-side against the repaired baseline (340 fields), identical arithmetic
to the offline variant.

**Prediction, stated now:** the window fix is mostly local — masked beta retains
**R_W1 ≥ 0.80** (achieved value to beat: 0.9494 with full beta; equal-weight varU will
of course regress toward baseline in y>2, which is expected and not the metric).

**Stop trigger, fixed now (d1b2c117 clause a):** proceed to Part B only if
**R_W1(masked) ≥ 0.70 AND R_W2(masked) ≥ 0.70**. Below either bar, the arm's premise
is weakened — the in-window fix rides on out-of-window beta — and the item STOPS with
the measurement reported to the chief before any further spend.

*Committed before the control solve runs. Parts B and C do not exist yet; they are
written only after the control verdict, each before its own solves.*

---

## Part A result (dated 2026-08-08 ~03:1x UTC) — control PASS, arm proceeds

One cold `run_model` at `beta_masked.npy`, 7.80 core-min (`log.maskctl`, converged
protocol as registered): **R_W1(masked) = 0.9458** against full-beta 0.9494 — the
window fix retains 99.6% of its reduction with every out-of-window deviation
amputated. R_W2(masked) = 0.9283 (vs 0.9468). Both far above the 0.70 stop trigger;
the prediction (≥ 0.80) is exceeded. Confirmatory detail: the y>2 error reverts
toward baseline (9.448 vs baseline 9.914; full beta had pushed it to 7.774) — the
out-of-window beta was serving the free channel and only the free channel. W2 hurt
census under masked beta: 1.01%. **The nonlocality concern is measured dead; the
optimization will warm-start from `beta_masked` (disclosed: L-BFGS-B curvature starts
cold — scipy carries no cross-process Hessian state).**

## Part B — FD gate on the weighted objective configuration (committed before its solves)

**The new objective, exactly:**

```
Jw_raw = 5319 * varUwin + 3591 * varUrec        (= sum of |U-UData|^2 over the W2 support)
```

- `varUwin`: DAFoam `variance`, mode=field, **source=boxToCell**, box min (0, 0, −1),
  max (6, 2, 1) — the G2 window, 1,773 cells (no cell centre sits on any box face;
  verified against the centres field).
- `varUrec`: same, box min (6, −1, −1), max (16, 0.5, 1) — the recovery-floor strip,
  1,197 cells. The two boxes are disjoint and their union is cell-for-cell the
  2,970-cell W2 support the masked control validated.
- Coefficients 5319/3591 = 3 x cell-count (the variance function divides by its
  nRefPoints = 3 per cell for a 3-component vector; the printed "Find N reference
  points" must show 5319 and 3591 or the item stops).
- Composition: an `om.ExecComp` sums the two function outputs into the single
  objective `Jw`; reverse mode seeds both partials into **one** state-adjoint RHS, so
  the per-eval cost stays one adjoint. This claim is not assumed — it is exactly what
  the FD gate verifies end-to-end, and the anchor's wall time is reported against the
  one-adjoint ~20 core-min basis.
- **Cross-check, fixed now:** the anchor's Jw_raw at beta=1 must reproduce the
  offline W2 baseline **27.4659** (host arithmetic on the same fields) to ~4 digits.

**FD protocol (the established discipline, unchanged):** anchor `compute_totals` of
Jw at beta=1, `-primalTol 1e-8` (~20 core-min); central differences h=0.05, fresh
container + cold reset per point, 3 components from the top of the weighted
gradient's |g| distribution, serial locations reported **via the exact permutation**
this time. **Bar: all three rel errs < 1%, zero sign flips; a miss stops the item
before the optimization spends anything.** Est: anchor ~20 + 6 primals ~48.

*Committed before any Part B solve. Part C is written after the FD verdict, before
any optimization eval.*
