# JF1E RUNG E1 — GRADING RECORD

**Ladder:** JF1E turbulence-stall escalation.
**Registration:** `verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md`,
frozen at commit `6e83157c112cdf606094f88ff0592bf1b02bc4b3`, blob
`800944bcfeb591973ca8830ae6c8ec6787ce730c`.
**Freeze verified at grading time:** the working-tree copy and `HEAD`'s blob both
hash to `800944bc…`. The frozen file **is** the file that ran (CLAUDE.md rule 2),
and each row's own `RUN_STATUS` carries the same assertion made *before* its solve.

**Graded:** 2026-09-01, by the frozen comparator
`verification/runs/JF1_jet_flap/analyse_jf1_ladders.py gateE --rung E1`.
**LABEL, from registration §0: numerics-diagnostic.** No physics verdict, no lift
claim, no observed order, no GCI and no band comes off this rung. The `CL` column
below is reported because Gate E's clauses are read beside it, not because it is a
result.

---

## 1. WHY THIS RECORD EXISTS AT ALL

Rows 1 and 2 were graded when they finished. **Rows 3 and 4 completed at
17:23:26Z and 17:42:14Z and sat ungraded** — the lane that ran them completed its
report before grading them. A completed run that nobody graded is not a result and
is not a null; it is an unclosed obligation, and this record closes it.

---

## 2. THE FOUR ROWS, GRADED

Comparator output, per row. `bk/500` and `bo/500` are `bounding k` and
`bounding omega` events in the **final 500 iterations** — Gate E clauses E-1 and
E-2, which the registration names as the load-bearing ones. Residuals are the
initial residuals at `endTime`, clauses E-3 to E-5, threshold `< 1e-6`.

| row | verdict | bk/500 | bo/500 | res k | res omega | res p | CL |
|---|---|---|---|---|---|---|---|
| `JF1E_E1_CMU005_A0` | **`GATE FAIL`** | 415 | 167 | 6.231e-06 | 2.405e-08 | 3.540e-07 | 0.40571058 |
| `JF1E_E1_CMU010_A0` | **`GATE FAIL`** | 495 | 167 | 2.634e-05 | 1.692e-08 | 6.176e-07 | 0.54881567 |
| `JF1E_E1_CMU020_A0` | **`GATE FAIL`** | 466 | 125 | 4.484e-05 | 3.526e-08 | 9.833e-07 | 0.74404339 |
| `JF1E_E1_CMU040_A0` | **`GATE FAIL`** | 481 | 125 | 1.360e-04 | 8.548e-08 | 1.642e-06 | 1.00997154 |

**RUNG E1: `GATE FAIL`.** The ladder escalates to E2a in the frozen §3 order.

### 2.1 Which clause failed, on every row

**E-1 fails on all four** — `k` is clipped between 415 and 495 times in the final
500 iterations, i.e. **on 83 % to 99 % of the last five hundred iterations of every
row.** **E-2 fails on all four** — `omega` clipped 125 to 167 times.
**E-3 fails on all four**: the `k` residual is 6.2e-06 to 1.4e-04 against a `1e-6`
threshold, and it is the only residual clause that fails — `omega` (E-4) and `p`
(E-5) clear their thresholds by one to two orders of magnitude on every row.
**E-6, the strict completion rule, PASSES on all four**: `rc = 0`, an `End` line,
last time `== endTime == 8000`, fields present, and every field newer than the
case's own `0/T`. That matters for the label: a rung failing E-6 alone would be
`NOT A RESULT`, not `GATE FAIL`. This one failed on physics-side clauses with its
bookkeeping intact, so `GATE FAIL` is the correct verdict and not a euphemism.

### 2.2 L-235 IS BINDING ON HOW THESE NUMBERS MAY BE READ

**`k` is clipping through the FINAL iteration of every row. No agreement in `CL`,
between rows or against anything else, may be reported as convergence.** The `CL`
column is stationary to within 1e-06 on three of the four rows (§2.3), and that
stationarity is exactly what L-235 warns about: **the forces are flat because the
turbulence field is being held by its bound, not because the solve reached a fixed
point.** The registration says this in §4 in advance — *"a rung that clears E-3 to
E-5 but not E-1/E-2 is `GATE FAIL`, and no report of it may use the word
converged"* — and the phrasing here is written to that instruction.

**The residual clauses alone would have passed rows whose `k` field was flat
because it had been clipped.** E-1 and E-2 are the instrument that catches it.

### 2.3 The §5 E4 trigger, evaluated and NOT fired

§5 registers that E4 (true transient) runs on a row only if that row shows `CL`
peak-to-peak over its final 2,000 iterations **> 1.0e-03 absolute**. Measured on
the E1 rows, from each run's own `postProcessing/forceCoeffs*/*/coefficient*.dat`
with the `Cl` column located by the file's own header:

| row | CL peak-to-peak, final 2,000 iterations | trigger |
|---|---|---|
| CMU005 | 7.4336e-07 | no |
| CMU010 | 1.5341e-06 | no |
| CMU020 | 6.6930e-05 | no |
| CMU040 | 8.2081e-06 | no |

**The trigger fires on no row**, three orders of magnitude clear of its threshold.
Registered at a level the E0 baseline already cleared, it has now also been cleared
by E1. **Read with §2.2, this is the stationary-and-clipping-held signature, not
evidence of a settled solve** — a field pinned at its lower bound does not
oscillate.

### 2.4 The departure that travels with every number here

**D-1, disclosed in the registration and in every row's `RUN_STATUS`: no link in
this chain was seeded from a converged field.** This lab has no converged JF1
solution at any `C_mu`. The chain's first link was seeded from the slot-closed
reference row's final field, which was itself stationary-but-clipping-held.

---

## 3. COST — CLAUDE.md RULE 12

**Per-row measured core-minutes**, each read from that row's own
`RUN_STATUS.<case_id>.txt`, written by the wrapper's `EXIT` trap. Serial,
`ranks = 1` throughout, so core-min = wall-min.

| row | wall s | ranks | core-min MEASURED | per-row cap | $ DERIVED |
|---|---|---|---|---|---|
| CMU005 | 1,428 | 1 | 23.8000 | 40.0 | $0.02035 |
| CMU010 | 1,519 | 1 | 25.3167 | 40.0 | $0.02165 |
| CMU020 | 1,178 | 1 | 19.6333 | 40.0 | $0.01679 |
| CMU040 | 1,128 | 1 | 18.8000 | 40.0 | $0.01607 |
| **rung total** | **5,253** | | **87.5500** | **150 registered** | **$0.07486** |

**Dollars are DERIVED, NOT MEASURED**, at the recorded `c7a.4xlarge` rate of
`$0.0513/core-h` (reported-by-owner) — this box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5. 87.5500 core-min = 1.45917 core-h.

**No cap was struck.** The highest row reached 63 % of its own 40-core-min cap and
the rung reached 58 % of its registered 150. **Waste: 0 core-min** — four links,
four completed solves, no re-runs, no stalls, and the longest row at 1,519 wall s
is nowhere near the `COMPUTE_BUDGET_CHARTER` §2 3,600-s stall rule, so gross =
cleaned.

**Estimate versus actual is filed as a row in `docs/COST_CALIBRATION.md`** per rule
12's calibration bullet, and is not repeated here.

---

## 4. WHAT THIS RUNG SETTLED, AND WHAT IT DID NOT

**Settled:** continuation seeding is **not** sufficient. The registration's own
§8 prediction — *"the honest pre-registered expectation is that E1 alone is
insufficient"* — **held.** The reasoning it was made on also held: the clipping was
predicted to be a property of the stationary state rather than of the transient
from freestream, and a chain that removed the freestream transient entirely left
`k` clipping on 83–99 % of its final five hundred iterations.

**Not settled:** *why* `k` is at its bound. This rung moved the starting point and
changed nothing about the mechanism, so it discriminates between "transient
artefact" and "everything else" and no further. The escalation to E2a is the
frozen next step, not a diagnosis.

**Not touched:** JF1G, the lift band, the grid family, and gate 6 of `12b1bd84`.
§8 reserves all of them.

---

## 5. THE STANDING PREDICTION AGAINST E2a, RECORDED BEFORE E2a WAS GRADED

A previous lane put a prediction on the record from a `k_min` diagnostic — worst
`k_min = -2.14e-03` against a mean `k` of `1.33e-01`, a **1.6 % undershoot**,
decaying only weakly and barely moved by continuation — that **E2a will NOT clear
the stall, and that E2c (`limitedLinear 1 → 0.5`) is the likelier fix**, on the
grounds that an undershoot of that shape points at the convection limiter rather
than at relaxation.

It is recorded here, before E2a's rows exist, so that it can be graded rather than
remembered. **If E2a reaches Gate E, that prediction is WRONG and will be reported
in those words.**

---

**SUBMISSIONS PARKED.** Nothing in or derived from this record is sent, filed,
uploaded, registered, posted or commented outside this box.
