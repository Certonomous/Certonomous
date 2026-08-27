# F21-WOMERSLEY — Womersley pulsatile channel flow (`pimpleFoam`, 128²/256²/512²) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F21_WOMERSLEY_PREREGISTRATION.md`
frozen at **`448756a540b86dc4dc94ed094cc93db3284e5928`**. **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3): counts toward no challenge column, not filmed.
The three levels were launched by the queue runner with no agent attached and the
launcher's `STATUS.F21_WOMERSLEY` reads `launcher_rc=0 end=2026-08-27T13:36:48Z`.
Graded **2026-08-27T16:33Z** by cfd lane R at **zero new compute**.

Grader run exactly as the launcher printed it, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F21_womersley/grade_f21.py --prereg-commit=448756a540b86dc4dc94ed094cc93db3284e5928`
— **rc 0**. Stdout `verification/runs/F21_runs/F21_GRADED.out`; record
`verification/runs/F21_runs/F21_GRADED.json`. Gated by
`scripts/roache_triple.py::grade_ladder`, **one** AST call node (line 670); 0
`assert` nodes across 4 files, planted assert seen.

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p | GCI | verdict |
|---|---|---|---|---|---|---|
| G-F21-1 `E2_velocity_locked_phase` | **56.08858769671483** | [2.571078e−05, 2.313970e−04] | **OSCILLATORY** (dim 2, r = 2.000, monotone **False**; e21 −5.608828e+01, e32 +9.308726e−04) — printed beside, not a result | none (undefined on an oscillatory triple) | **not quoted** — the three values are not monotone | **NOT A RESULT** |
| G-F21-2 `u_centreline_locked_phase` | **1.074655151729998** | [1.053476994, 1.054131256], reference 1.0538041252522687 (same-stencil) | **DIVERGENT** (dim 2, r = 2.000, monotone True; e21 −2.128328e−02, e32 −1.290677e−03) | **−4.0435** — printed beside, not a result | **not quoted** | **NOT A RESULT** |

The grader's tally, verbatim:

    G-F21-1_E2_velocity_locked_phase         NOT A RESULT
        levels fine are not iteratively converged or not plateaued; no grid claim can be made from this triple
    G-F21-2_u_centreline_locked_phase        NOT A RESULT
        levels fine are not iteratively converged or not plateaued; no grid claim can be made from this triple

**Rule 5 applied in order, and the order matters here.** Limb (1) fired first: the
**fine** level is not plateaued, so both gates are `NOT A RESULT` before any triple
is consulted. Both band verdicts computed underneath read **GATE FAIL** and both
triples are non-CONVERGING (OSCILLATORY, DIVERGENT); the gate can only turn a
PASS or GATE FAIL **into** NOT A RESULT, never the reverse, so `NOT A RESULT` is
the verdict on both and the `GATE FAIL` cells are recorded here as the underlying
band reading, **not** as the verdict.

Level values, read from `<level>/12.25/U` by the frozen reader:

| level | cells | h | Δt | E2 (locked phase) | u_centreline |
|---|---|---|---|---|---|
| coarse | 16,384 | 0.015625 | 0.01041667 | 1.240156e−03 | 1.0520811927 |
| medium | 65,536 | 0.0078125 | 0.00520833 | 3.092833e−04 | 1.0533718699 |
| fine | 262,144 | 0.00390625 | 0.00260417 | **5.608859e+01** | **1.0746551517** |

Coarse → medium is textbook second order (ratio 4.01 on E2, and the probe walks
toward the same-stencil reference 1.05380413). **The fine level is not a refinement
of that trend; it is a different solution.**

## 2. THE FINE LEVEL DIVERGED — triage, because a bad number is a finding

The fine level satisfies rule 4 completely (§3) and **every linear solve in it
converged** — the grader's iterative census reads `CONVERGED` at all three levels,
0 readings above tolerance out of 9,408 p and 4,704 Ux readings at fine, worst p
9.99e−10 against 1e−9 and worst Ux 9.90e−13 against 1e−12. What failed is the
**periodicity (plateau) element**: ‖U(T) − U(T − PERIOD)‖₂/U_ref = **38.53**
against the registered tolerance 1e−5 (coarse 4.07e−08, medium 4.07e−08 — both
`PLATEAUED`).

Measured from `verification/runs/F21_runs/fine/log.pimpleFoam`:

| reading | coarse | medium | **fine** |
|---|---|---|---|
| Courant max, first step | 0.0342 | 0.0342 | 0.0342 |
| Courant max, last step | 0.1132 | 0.1133 | **68.4071** |
| Courant mean, last step | 0.0918 | 0.0915 | **3.2845** |
| max abs Ux at `12.25/U` | — | — | **102.29** (exact peak ≈ 1.05) |
| DIC-PCG iterations per p corrector, last step | — | — | **892–903** |

**h and Δt refine together by 2, so the Courant number is a ladder invariant** —
all three levels start at Co_max 0.0342. The fine level's Co_max is not a CFL
limit reached by refinement; it is the signature of a solution that grew. First
Co_max > 0.2 at **t = 0.7865**, > 1 at **t = 0.8229**, > 10 at **t = 0.8750** —
i.e. within the first 7 % of the 12.25 s integration, at step ≈ 302 of 4,704 —
after which it saturates near 68 and stays there for the remaining 11.4 s without
ever producing a NaN. That is why the run exited rc 0 with `End`: **OpenFOAM
completed a perfectly well-posed integration of a solution that is not the case's
physics.** The ~900 DIC-PCG iterations per corrector at the end (against ≈ 238 at
the registered coarse-grid probe) is the same event seen from the pressure system.

**What this lane does NOT claim.** No mechanism is named. The registered numerics
(`pimpleFoam`, `backward`, PISO-shaped, fixed Δt, no `residualControl`) are
identical at all three levels and worked at two of them; whether the fine level's
failure is odd–even pressure decoupling, the wall stencil at h = 0.0039, or the
`fvOptions` cosine drive interacting with `backward` at Δt = 0.0026 is **not
determined by anything this lane measured**, and diagnosing it costs compute that
is not registered. **The gates are CLOSED (rule 2, first compute is spent), so
this cannot be repaired inside F21.** A successor registration is the supervisor's
call, not this lane's.

## 3. RULE 4 — strict completion, re-read from the run root by this lane

Every clause, at every level, re-read independently of the grader:

| clause | coarse | medium | fine |
|---|---|---|---|
| `RC.txt` == 0 | 0 | 0 | 0 |
| `End` line | 1 | 1 | 1 |
| last `Time =` == endTime 12.25 | 12.25 | 12.25 | 12.25 |
| `Time` line count == endTime/Δt | 1176 == 1176 | 2352 == 2352 | 4704 == 4704 |
| `ExecutionTime` count == `Time` count | 1176 | 2352 | 4704 |
| fields at endTime | U, U_0, p, phi, phi_0 | same | same |
| **age guard**: endTime field newer than the case's own `0/U` | 1787781308 > 1787781122 | 1787784436 > 1787781311 | 1787837808 > 1787784447 |
| `<endTime − PERIOD>/U` present (11.25) | yes | yes | yes |

**All three levels are COMPLETE under rule 4.** The verdict is not a completion
failure.

**L-342 split, as the grader declares it.** PHYSICS-CRITICAL: the `End` line and
`Time` count, `RC.txt`, the endTime `U`/`p` and their age guard, the previous-period
`U`, `0/C`, and every step's final p and Ux residual. INFRASTRUCTURE: `ClockTime`,
`box_before/after.txt`, `MESH_LINE.txt`, the runner's `STATUS.*` /
`launcher.queue.out` / `LAUNCH_LOG` rows, and every calibration figure derived from
them. **`cost_claim.defects` is empty — no infrastructure field is missing**, so
the cost claim below stands. No infrastructure reading touches either verdict.

## 4. PLANTED-ZERO CONTROLS — fired, and read back through the real reader

Both gates, on the **real fine-level artifact** `fine/12.25/U`:

| gate | reader | planted | read back | reader delta |
|---|---|---|---|---|
| G-F21-1 | `e2_from_files` | −6.444314408327045e−06 | −6.444314408327045e−06 | −6.444314408327045e−06 |
| G-F21-2 | `u_probe_from_files` | +7.75345066905961e−03 | +7.753450669059747e−03 | +7.753450669059747e−03 |

Both `passed: true`. Ten controls in total are green in the JSON, including the
symbolic substitution (numeric residual max 2.22e−16 and a planted 1.1k that must
be non-zero), the constant-ratio refinement control (h ratios [2, 2], Δt ratios
[2, 2]), the L-342 both-ways control, the iterative-census control (one bad p and
one bad Ux reading each flagged), the periodicity control (planted 7.75e−03 read
back, identical files → 0.0, tolerance 1e−5 against a model worst predicted change
of 4.07e−08) and the real-solver-output reader pin
(`verification/runs/ansys_verification/VMFL019/L1_30/5/U`, 120 cells).

## 5. COST — rule 12, estimate versus actual

**Measured, from the three `log.pimpleFoam` ClockTimes × 1 rank ÷ 60:**

| level | cells | steps | cell-steps | ClockTime | core-min | µs/cell-step | predicted core-min | ratio |
|---|---|---|---|---|---|---|---|---|
| coarse | 16,384 | 1,176 | 19.3 M | 186 s | 3.100 | 9.65 | 3.4 | 0.91 |
| medium | 65,536 | 2,352 | 154.1 M | 3,125 s | 52.083 | 20.28 | 47.3 | 1.10 |
| fine | 262,144 | 4,704 | 1,233.1 M | 53,361 s | 889.350 | 43.27 | 662.5 | 1.34 |
| **total** | | | **1,406.5 M** | **56,672 s** | **944.533** | | **713** | **1.325** |

- **944.533 core-min of the registered CAP 1500 = 63.0 %.** No overrun; the cap
  was not approached and was never raised.
- **Dollars: $0.808 — DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot read its own billing). Registered
  estimate $0.61 derived; cap $1.28 derived.
- **Actual/predicted = 1.325.** Attribution:
  - **Misprediction, the whole of it.** The registered basis was the measured
    10.71 µs/cell-step at 128² grown +72 %/+75 % per doubling. The **measured**
    growth is +110 % then +113 % (9.65 → 20.28 → 43.27 µs/cell-step), i.e. the
    p-solve's DIC-PCG iteration count grows essentially **∝ N** here, faster than
    the +75 % F18 basis borrowed from a different solver. The coarse level itself
    came in 10 % **under** (9.65 measured against 10.71 registered), so the miss is
    entirely in the growth exponent, not in the base rate.
  - **Contention: not separable, and not claimed.** All three levels ran serial on
    1 rank on a box that was 85–100 % busy throughout; no per-level free-core
    reading was taken beside the ClockTime, so no contention share is attributable
    from the record and none is asserted.
  - **Waste, named separately and NOT absorbed into the ratio (charter §6):**
    **889.350 core-min — the entire fine level — bought no result.** It is not a
    stall (no row exceeds 3,600 s of idle; the solver worked the whole time) and
    it is not double-spend, so the gross and cleaned figures are the same 944.533;
    but the honest split of this rung is **55.183 core-min useful (the two levels
    that graded) and 889.350 core-min spent on a level that produced NOT A RESULT.**
    A future estimate for this case must price the fine level as unbought.

## 6. WHAT THIS RUNG SETTLED, AND WHAT IT DID NOT

- **Settled:** the discretisation is second order between 128² and 256² on both
  gate quantities (E2 ratio 4.01; the probe converging on the same-stencil
  reference), the instrument is sound (ten controls green, both planted zeros read
  back through the real readers on the real artifact), and rule 4 holds at all
  three levels.
- **Not settled:** the asymptotic claim the ladder was registered to make. It
  needs a third level that stays on the branch, and F21's fine level did not.
- **Open, for the supervisor's desk, not decided here:** whether a successor
  registration buys a stable third level (a different pressure treatment, an
  outer-corrector count above 1, or a smaller Δt at the same h — each of which
  changes the case definition and therefore is a NEW pre-registration, never an
  addendum to this closed one).

## 7. NOT REGISTERED, NOT SENT

No amendment to F21's pre-registration (gates closed at first compute), no
re-grade of any other rung, no claim about Womersley flow beyond the two
registered gate quantities. **Nothing was sent, filed, uploaded or submitted**
(rule 7).
