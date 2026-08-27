# F22-LAMB-OSEEN — 2-D decaying Lamb–Oseen vortex (`icoFoam`, 192²/384²/768²) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F22_LAMB_OSEEN_PREREGISTRATION.md`
frozen at **`29a47d994c708fddd856506fdaeea6025b44a166`**. **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3): counts toward no challenge column, not filmed.
Launched by the queue runner with no agent attached; `STATUS.F22_LAMB_OSEEN` reads
`launcher_rc=0 end=2026-08-27T13:10:07Z`. Graded **2026-08-27T16:38Z** by cfd lane R
at **zero new compute**.

Grader run exactly as the launcher printed it, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F22_lamb_oseen/grade_f22.py --prereg-commit=29a47d994c708fddd856506fdaeea6025b44a166`
— **rc 0**. Stdout `verification/runs/F22_LAMB_OSEEN_runs/F22_GRADED.out`; record
`verification/runs/F22_LAMB_OSEEN_runs/F22_GRADED.json`. Gated by
`scripts/roache_triple.py::grade_ladder`, **one** AST call node (line 585); 0
`assert` nodes across 4 files, planted assert seen.

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F22-1 `E2_velocity_L2_at_T` | **3.682601646252679e−06** | [1.172716e−06, 1.055445e−05] | **CONVERGING** (dim 2, r = 2.000, monotone True; e21 1.089631e−05, e32 4.199286e−05) | **1.9463** | **129.5992 % = 4.77262e−06 absolute** | **PASS** |
| G-F22-2 `peak_vorticity_at_T` | **1.326137342509056** | [1.3257157465, 1.3263982409], reference **1.3260569937248692** | **CONVERGING** (dim 2, r = 2.000, monotone True; e21 −4.753515e−04, e32 −2.064616e−03) | **2.1188** | **0.0134 % = 1.77723e−04 absolute** | **PASS** |

The grader's tally, verbatim:

    G-F22-1_E2_velocity_L2_at_T              PASS
        finest triple ('coarse', 'medium', 'fine') CONVERGING at dim = 2, observed order 1.9463, GCI 129.5992 % = 4.77262e-06 absolute at Fs = 1.25
    G-F22-2_peak_vorticity_at_T              PASS
        finest triple ('coarse', 'medium', 'fine') CONVERGING at dim = 2, observed order 2.1188, GCI 0.0134 % = 0.000177723 absolute at Fs = 1.25

**Rule 5 applied in order.** Limb (1): every level is iteratively `CONVERGED` (below)
and F22 registers **no plateau gate** — the graded quantities are values at the
fixed instant t = T of a decaying transient, so `plateau` is `None` and recorded
ABSENT at every level, exactly as registered. Limb (2): both triples are
`CONVERGING` and monotone, so neither gate is forced to NOT A RESULT. Limb (3):
both fine values lie inside their pre-registered bands → **PASS**, GCI printed.

**On the 129.6 % GCI, stated rather than buried.** G-F22-1's graded quantity is an
error norm whose exact value is zero, so the GCI's *relative* form divides an error
estimate by an error — it is large by construction and is not a statement that the
value is uncertain by 130 %. The absolute figure is the readable one: **4.77e−06**,
on a value of 3.68e−06, at observed order 1.9463 with a monotone triple. F17b's
record carries the same structural artefact (227.6 %). No claim rests on the
percentage.

Level values, read from `<level>/4/U` by the frozen readers:

| level | N | cells | h | Δt | E2(T) | peak vorticity(T) |
|---|---|---|---|---|---|---|
| coarse | 192 | 36,864 | 0.026041667 | 0.01 | 5.657177e−05 | 1.3235973752 |
| medium | 384 | 147,456 | 0.013020833 | 0.005 | 1.457891e−05 | 1.3256619910 |
| fine | 768 | 589,824 | 0.006510417 | 0.0025 | 3.682602e−06 | 1.3261373425 |

Both quantities march monotonically toward their targets; the E2 ratios are 3.88
then 3.96, converging on the second-order 4.

## 2. THE SECOND GATE'S REFERENCE SHARES A STENCIL WITH THE MEASUREMENT — BY DESIGN

G-F22-2 is graded on **peak vorticity through the grader's own central-difference
curl**, not on peak u_θ, and its reference is the **exact velocity field evaluated
at the fine level's own cell centres and passed through that same curl**:
**1.3260569937248692**, against the pointwise exact Γ/(4πνt′) = **1.326291192432**.
The stencil under-reads the Gaussian peak by **−2.342e−04**, and that bias is
**removed from the reference** rather than left in the measurement. This is the
F17b Amendment-1 lesson applied *at registration* instead of after first compute,
and it is deliberate: comparing a discrete curl against a pointwise analytic peak
would charge the discretisation with a stencil bias it cannot remove by refinement.
The control `PZ-F22-PEAK_reference_same_stencil_zero_error_and_ramp_read_back`
drives it: the exact field through the real reader returns the reference with
**zero** error, and a planted ramp is read back at −2.468e−04. **This lane changed
nothing about it.**

## 3. RULE 4 — strict completion, re-read from the run root by this lane

| clause | coarse | medium | fine |
|---|---|---|---|
| `RC.txt` == 0 | 0 | 0 | 0 |
| `End` line | 1 | 1 | 1 |
| last `Time =` == endTime 4 | 4.0 | 4.0 | 4.0 |
| `Time` line count == endTime/Δt | 400 == 400 | 800 == 800 | 1600 == 1600 |
| `ExecutionTime` count == `Time` count | 400 | 800 | 1600 |
| fields at endTime | U, U_0, p, phi, phi_0 | same | same |
| **age guard**: endTime field newer than the case's own `0/U` | 1787787535 > 1787787398 | 1787790124 > 1787787541 | 1787836206 > 1787790144 |

**All three levels COMPLETE.** Rule 5 limb 1 census, over **every** time step's
final p residual against the solver's own 1e−9: **0 readings above tolerance** at
every level (800 / 1,600 / 3,200 readings; worst 9.99883e−10, 9.99974e−10,
9.99997e−10).

**L-342 split, as the grader declares it.** PHYSICS-CRITICAL: `End` line and `Time`
count, `RC.txt`, endTime `U`/`p` and their age guard, `0/C`, every step's final p
residual. INFRASTRUCTURE: `ClockTime`, `box_before/after.txt`, `MESH_LINE.txt`,
runner `STATUS.*` / `launcher.queue.out` / `LAUNCH_LOG` rows, calibration figures.
**`cost_claim.defects` is empty** — no infrastructure field missing, so the cost
claim below stands; and no infrastructure reading touches either verdict.

## 4. PLANTED-ZERO CONTROLS — fired, through the real readers on the real artifact

Both on `verification/runs/F22_LAMB_OSEEN_runs/fine/4/U`:

| gate | reader | planted | read back | reader delta |
|---|---|---|---|---|
| G-F22-1 | `e2_from_files` | +2.18932750863457e−03 | +2.1893275086345703e−03 | +2.1893275086345703e−03 |
| G-F22-2 | `peak_vorticity_from_files` | −2.4680000000000004e−04 | −2.467999999995474e−04 | −2.467999999995474e−04 |

Both `passed: true`. Nine controls green in total, including the four-way symbolic
substitution (vorticity transport, curl u = ω, continuity and radial momentum all
identically 0, far-field datum relative error 4.90e−12), a planted 1.1 t′ decay that
must be non-zero, the constant-ratio refinement control (h [2, 2], Δt [2, 2]), the
L-342 both-ways control, and the real-solver-output reader pin
(`verification/runs/ansys_verification/VMFL019/L1_30/5/U`, 120 cells).

## 5. COST — rule 12, estimate versus actual

**Measured, from the three `log.icoFoam` ClockTimes × 1 rank ÷ 60:**

| level | cells | steps | cell-steps | ClockTime | core-min | µs/cell-step | predicted core-min | ratio |
|---|---|---|---|---|---|---|---|---|
| coarse | 36,864 | 400 | 14.75 M | 137 s | 2.283 | 9.29 | 2.5 | 0.913 |
| medium | 147,456 | 800 | 117.96 M | 2,583 s | 43.050 | 21.90 | 34.4 | 1.251 |
| fine | 589,824 | 1,600 | 943.72 M | 46,062 s | 767.700 | 48.81 | 495.5 | 1.549 |
| **total** | | | **1,076.4 M** | **48,782 s** | **813.033** | | **532.3** | **1.528** |

- **813.033 core-min of the registered CAP 1100 = 73.9 %.** No overrun; the cap was
  never raised. It also exceeds the pre-registration's own *asymptotic* bound of
  ≈ 666 core-min by 1.22×, which is the honest headline: the width of the cap, not
  the estimate, is what carried this run.
- **Dollars: $0.695 — DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5). Registered estimate $0.46 derived; cap $0.94.
- **Actual/predicted = 1.528.** Attribution:
  - **Misprediction, and again it is the GROWTH EXPONENT, not the base rate.** The
    registered basis was 10.00 µs/cell-step measured on this case's own coarse grid,
    grown +75 % then +80 % per doubling. Measured: 9.29 → 21.90 → 48.81 µs/cell-step
    = **+136 % then +123 %**. The coarse level came in **7 % UNDER** its registered
    rate, so the base measurement was good and the growth law was not — the
    pre-registration itself flagged "+100 %/doubling" as the asymptotic bound and
    **the measurement exceeded even that.** For `icoFoam` with DIC-PCG at 1e−9 and
    relTol 0, serial, the per-cell-step rate on this box grows FASTER than ∝ N per
    side. **This is the second cfd rung today to miss in exactly this way** (F21,
    row C-152, measured +110 %/+113 % against a registered +72 %/+75 %); two
    independent cases now say the lab's per-doubling growth factor is too small.
  - **Contention: not separable, and not claimed.** All three levels serial on 1
    rank on a box at 85–100 % busy; the pre-registration's own note that its base
    rate was measured "at load 26.6" so contention "can only inflate it" is borne
    out in direction but no per-level free-core reading was recorded beside the
    ClockTime, so no share is attributable and none is asserted.
  - **Waste: NONE.** No level failed, no attempt was repeated, no row exceeds the
    3,600-s stall rule as an idle row (the solver worked continuously), and every
    core-minute bought a graded result. Gross == cleaned == 813.033.

## 6. WHAT THIS RUNG SETTLED

- A three-level Roache triple, **CONVERGING on both gates**, observed orders
  **1.9463** and **2.1188** against a design order of 2, with both fine values
  inside pre-registered bands: **PASS × 2**.
- The same-stencil reference construction works and is now demonstrated on a second
  cfd case at registration time rather than by amendment.
- The lab's `icoFoam` cost model is measurably optimistic in its growth exponent;
  §5 gives the number a successor estimate should use.

## 7. NOT REGISTERED, NOT SENT

No amendment to F22's pre-registration (gates closed at first compute); no re-grade
of any other rung; no claim about Lamb–Oseen decay beyond the two registered gate
quantities. **Nothing was sent, filed, uploaded or submitted** (rule 7).
