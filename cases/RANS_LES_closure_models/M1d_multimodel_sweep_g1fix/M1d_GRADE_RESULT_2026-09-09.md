# M1d MULTI-MODEL SWEEP REGRADE (G1 FIX) — GRADE RESULT, 2026-09-09

## VERDICT: GATE FAIL (governed by G0 — harness 72/78 complete). G1 PASS: the arms ARE correctly applied.

This is the **first believable verdict** on the M1 multi-model sweep. Both prior
frozen comparators refused before producing one: `grade_m1.py` at the C1
planted-zero round-off false-positive (L-508), and `grade_m1b.py` at the G1
arm-application false-fail (L-509). M1d repairs the G1 log-reader; C1 (the L-508
repair) is inherited byte-identical. With the reader fixed, **G1 PASS (n_bad=0)**
— the arm was applied correctly on every complete row. The sweep as a whole is
**GATE FAIL, governed by G0**: 6 of 78 arms are incomplete (wall-timeout), and a
full result is not reachable until those are re-run (the compute-gated completion
rung).

## BIRTH RECORD (rule 2 / prereg §6, supervisor-verified)

* **Instrument sha256 executed:** `a1ee190550e94be13fb2fc678379e1c23275b9fd4f002905073776d263628790`
  — re-hashed at run time, **byte-identical** to the freeze pin (`PREREGISTRATION.md`
  §7, freeze commit `13f1f4d6`).
* **§2j birth demonstration: VERIFIED, all three limbs on real producer bytes** —
  fatal positive 3/3, fatal negative 4/4, **MODEL 4/4** (the fixed MODEL_RE reads a
  genuine model name on 4 real logs where the defective predecessor pattern read
  the literal `type`). Record at `/home/ubuntu/closure-data/m1d_birth/`.
* **Data snapshot:** `/home/ubuntu/closure-data/multimodel_sweep/`; **no solver,
  no staging ran** (zero-compute regrade).

## GATE-BY-GATE

| gate | verdict | key numbers |
|---|---|---|
| **C1** planted zero | **PASS** (L-508 repair, inherited) | `passed=True`, read-back 0.0012339999999966267 on the O(47) donor |
| **G0** completion + age guard | **GATE FAIL** | 72/78 complete; 6 incomplete named below |
| **G1** arm application | **PASS** (L-509 repair) | n_bad=0 — dict model and the solver's own `Selecting RAS turbulence model …` line agree on every complete row |
| **G2** null-arm identity | GATE FAIL | 29 matched hills all in band (matched_out_of_band=[]); all_rows_max 0.02419 > ceiling 0.01 (duct cases, unknown-provenance references); 2 rows missing (incomplete) |
| **G3** arm separation | GATE FAIL | GATE FAILs because 4 cases are missing (incomplete pair); of 35 evaluable, all 35 separate (>1e-2), max spread 0.101 |
| **G4** cap-bound census | GATE REACHED | 0 cap-bound (≤ 8) |

Standing rule 5 (Roache triple gating) **does not apply** — one mesh per case, no
triple; the comparator prints that sentence.

### G0 — the 6 incomplete arms (rc=124 wall-timeout, no `20000/` dir)

    kOmega/AR_14_Ret_180, kOmega/AR_1_Ret_180, kOmega/AR_7_Ret_180,
    kOmega/PH_Breuer, kOmegaSST_null/AR_1_Ret_180, kOmegaSST_null/PH_Breuer

### Reading the verdict honestly

* **G1 PASS and G4 GATE REACHED are the clean results.** The arms are the models
  we think they are, and nothing ran cap-bound.
* **G2 and G3 GATE FAIL are dominated by the incomplete arms** (missing rows —
  a gate that cannot see all its rows fails rather than passes). For G2 there is
  additionally a real signal: 2 duct cases exceed the 0.01 convergence-level
  ceiling (max 0.024) — but these are exactly the cases the frozen G2 label
  flagged as having references of **unknown provenance** (334–7,009 iterations
  under a criterion this sweep does not use), and the 29 iteration-matched hills
  all sit in the 1e-3 band. G2 is a gross-harness-error detector, not a precision
  claim.
* **The arm spread is real but is NOT model-form uncertainty.** On the 35
  evaluable cases the two arms separate on all 35 (max rel-L2 0.101). The frozen
  label governs: both arms are linear eddy-viscosity models sharing the Boussinesq
  assumption, so their errors are CORRELATED, and this spread **systematically
  understates** true model-form uncertainty. No interval is calibrated from it.
* **A full sweep result awaits the 6-arm completion re-run** (compute-gated). M1d
  does not pretend the sweep is complete; it establishes that the harness and arms
  are sound on the 72 complete runs.

## COST — CALIBRATION (rule 12)

* **Grade:** 75.9 s wall × 1 rank ÷ 60 = **1.265 core-min** MEASURED (reads all 78
  logs, some 280k lines, for the fatal / non-finite censuses). Birth demonstration
  read-only, a few seconds, negligible. No separate registered grading estimate —
  grading a populated sweep is a small read.
* **Solve phase (unchanged from M1b):** 781.4 core-min MEASURED vs 1298.1
  registered = **0.602**; waste 133.03 core-min on the 6 timeout arms = **$0.114
  DERIVED** at $0.0513/core-h, named not absorbed.
* **$0.00 send.** SUBMISSIONS PARKED.

## NEXT

The believable verdict is established. A full sweep result (a possible G0 PASS)
requires re-running the 6 incomplete arms — the compute-gated completion rung
(M1c / M1-C on the board). No comparator change is needed: `grade_m1d.py` is the
sound instrument. M2 (error against LES/DNS truth) remains a separate, later
registration.

*Recorded by the closure supervisor, 2026-09-09, after a personal §3 check-1
diff-read of `grade_m1d.py`. Frozen `grade_m1b.py`/`grade_m1.py` NOT edited
(rule 6).*
