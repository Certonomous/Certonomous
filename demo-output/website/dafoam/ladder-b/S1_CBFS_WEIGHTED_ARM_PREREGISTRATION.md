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
