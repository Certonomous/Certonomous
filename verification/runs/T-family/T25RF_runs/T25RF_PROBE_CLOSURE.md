# T25RF — PROBE CLOSED. Dated disposition record. NO VERDICT EXISTS AND NONE MAY BE QUOTED.

**Date:** 2026-09-03. **Author:** heat-transfer `lab-lane`, on the
heat-transfer-supervisor's dispatch. **Zero new compute.** Every clause and every
figure below was re-measured from the artifacts in this tree today; none was
carried from the note it points at.

---

## 0. Why this file exists, and what it corrects

`CLAUDE.md` rule 2 exists to prevent an unregistered run tree that implies a
result. This tree holds four solved arms — `A0 A1 A2 A2T` — with fields on disk,
a `COST_LEDGER.txt`, and three scripts, and **nothing on its own face saying that
none of it is gradeable.** The reader who opens `A2/30/` finds a converged
temperature field and no warning attached to it. **This file closes the tree.**

**The premise that T25RF is undisposed is FALSE, and correcting it is part of the
disposition.** The probe's observations, cost calibration and no-verdict
declaration were written before and after the arms ran and are committed at
`docs/campaigns/T-family/T25RF_FEASIBILITY_NOTE.md` (Addendum A1 registering arm
A2T before it ran; Addendum A2 carrying the observations). Verified today:
that file is **byte-identical to its committed blob**. What was genuinely missing
is (i) any marker on the run tree itself and (ii) the `docs/COST_CALIBRATION.md`
row that `CLAUDE.md` rule 12 requires at process completion. Both are supplied —
(i) here, (ii) as row `C-20260903T185443.680924Z-b22cc77f` of that ledger.

**Disposition chosen: RECORD AS A CLOSED, UNGATED FEASIBILITY PROBE.**
Prospective registration was considered and **refused**: T25RF is a *numerics*
probe of a case whose own graded registration is `T25R`/`T25R2`, and registering
the probe would create a second registration over the same physics. The right
consumer of these observations is a future `T25R2` pre-registration, which
freezes its own gates and **runs again**.

---

## 1. What T25RF is, restated so this file stands alone

**THERE IS NO `T25RF_PREREGISTRATION.md`, IN THE WORKING TREE OR AT ANY COMMIT.**
`docs/campaigns/T-family/T25RF_FEASIBILITY_NOTE.md` is **a feasibility note and
not a pre-registration**, states so on its own first line, and does not become
one by being cited. `VERIFICATION_CHARTER.md` §2m applies in its exact terms:

> A feasibility rung's output is not a verdict and may not be reported as one. It
> may emit **no** word from the fixed vocabulary — not `PASS`, not
> `GATE REACHED`, not `GATE FAIL`. Its numbers are reportable as **observations**
> and **nothing may be cited from it as a result.**

The arms' own `STATUS.<ARM>` files carry `gated=no` and
`verdict=NONE_THIS_RUNG_IS_UNGATED`, written at run time. **Nothing here reaches
a demo screen, a certificate or a table cell; nothing closes any gate of `T25R`;
nothing carries into a future `T25R2` as that registration's answer.**

---

## 2. What was tried

One case — the already-built `T25R_L1` two-region conjugate mesh, 16 608 cells,
copied rather than rebuilt — run under `chtMultiRegionFoam`, 1 rank, `deltaT`
0.5, `endTime` 30 s (60 steps), under Sanaa's 2026-09-01 04:20Z volumetric loads
(1.0e5 W/m3 takeoff branch). Four arms, sequential, cheapest first:

| arm | numerics | rc | steps | `End` | core-min |
|---|---|---:|---:|---|---:|
| `A0` | as registered in `T25R` (relaxation on outer sweeps 1–4 only, `nOuterCorrectors 5`) | **134** | 3 of 60 | no | 0.083 |
| `A1` | + `UFinal`/`hFinal`/`p_rghFinal`/`kFinal`/`omegaFinal` relaxation keys | 0 | 60 | yes | 3.650 |
| `A2` | `A1` + `nOuterCorrectors 10` | 0 | 60 | yes | 7.967 |
| `A2T` | `A2` + coolant `p_rgh` absolute tolerance 1e-9 → 1e-8 | 0 | 60 | yes | 0.517 |
| `A3` | `frozenFlow` | — | **NOT REACHED, NOT RUN** | — | 0 |

**No departure was taken.** `A3`'s registered trigger was "A1 and A2 both fail";
both advanced to `endTime`, so `T25R` §3.3's refusal of `frozenFlow` stands
untouched.

### 2.1 Completion, `CLAUDE.md` rule 4, re-measured 2026-09-03

Re-read today from `STATUS.<ARM>`, `.rc.<ARM>` and `log.solve` in each arm
directory. These cases are **single-region-per-`0/` with a `module` region**; the
run wrapper touches `0/module/T` last, and that file — not a bare `0/T` — dates
the run.

| arm | rc | `End` | last time == `endTime` 30 | `ExecutionTime` count == 60 steps | fields at `30/` | age guard |
|---|---:|---|---|---|---|---|
| `A0` | **134** | **absent** | **no — died at `Time = 1.5`** | 2 | **no `30/`** | n/a — the arm did not complete, and that is the arm's point |
| `A1` | 0 | ✔ | ✔ | ✔ 60 | present | **PASS** |
| `A2` | 0 | ✔ | ✔ | ✔ 60 | present | **PASS** |
| `A2T` | 0 | ✔ | ✔ | ✔ 60 | present | **PASS** |

`rc` was captured **inside** the detached wrapper on the line after the solver,
never around the `setsid` line — the `STATUS` files say so in their own `note=`
field, and `.rc.<ARM>` carries the same integer independently.

**Rule 4 completion is a statement about the run, not about the answer. These
three arms completed; they still grade nothing, because there is no gate.**

---

## 3. What was learned — observations, not results

1. **The divergence is numerical, not load-driven.** `A0` reproduced the
   2026-09-01 04:09Z `T25R_L1` failure under the *new* loads to the same three
   timesteps and `T0 = -14.458` against the reference run's `-14.459`.
2. **Final-sweep relaxation is what separates diverging from advancing.** Adding
   the `*Final` relaxation keys and nothing else carried the identical case to
   `Time = 30` with continuity `sum local` falling 2.45e-3 → 4.57e-8 instead of
   climbing to 125.93.
3. **Five outer sweeps is not enough at this Courant number.** `A1` and `A2`
   differ only in sweep count and their max-T trajectories keep separating:
   1.05e-3 K at 1 s, 3.47e-3 K at 10 s, **6.02e-3 K at 30 s and still growing** —
   already half the `T25R` `controlDict`'s 10 × PLANT = 1.234e-02 K scale after
   30 s of a 900 s case.
4. **The registered `p_rgh` tolerance of 1e-9 is unreachable on this system and
   buys nothing.** GAMG stalls at ~4.4e-9; relaxing one digit gave identical
   `Min/max T` at `Time = 30` — **agreeing to 0.000e+00 K** against a criterion
   of 1e-4 K registered in Addendum A1 *before* the arm ran.
5. **Adopting final-sweep relaxation costs the `T25R` §3.5 convergence measure**,
   and any registration that takes these numerics owes a replacement measure.
   **This probe does not supply one.**

---

## 4. What it cost, and the waste, named separately

**Unit: core-minutes, RANKS = 1 throughout.** Figures re-read today from
`COST_LEDGER.txt` and each arm's `STATUS.<ARM>`; the two agree exactly.

| | core-min |
|---|---:|
| predicted, §5 of the note, for `A0 + A1 + A2` | **1.9** |
| actual, `A0 + A1 + A2` | **11.700** |
| ratio for those three arms | **6.16** |
| predicted, Addendum A1, for `A2T` | **~4** |
| actual, `A2T` | **0.517** |
| ratio for `A2T` | **0.129** |
| **probe total predicted** | **5.9** |
| **probe total actual** | **12.217** |
| **probe total ratio** | **2.07** |
| probe CAP | **30.0** — utilisation **40.7 %**, no arm cap-stopped |

**GAP ATTRIBUTION: the whole of it is the `p_rgh` GAMG stall, and it is named as
WASTE rather than absorbed into the ratio** (rule 12,
`COMPUTE_BUDGET_CHARTER.md` §6). **266 of 600 `p_rgh` solves in `A1` and 608 of
1200 in `A2` terminated at `maxIter` 1000** without reaching the registered 1e-9.
Total GAMG iterations fell **627 533 → 25 770 (24.4×)** when the tolerance was
relaxed one digit, and **those 601 763 discarded iterations changed no digit of
the answer** — max/min T identical to 0.000e+00 K.

**Removable waste, MEASURED: 7.450 core-min** — `A2` 7.967 minus `A2T` 0.517,
the same physics with the stall removed. **`A1`'s stall fraction is NOT
separately measured**, because no `A1T` arm was run; it is left stated as absent
rather than estimated.

**Contention is NOT available as an excuse here and is not offered as one:** the
GAMG iteration counts above are read from the logs and are independent of machine
load, and they alone account for the gap.

**One defect in the prediction itself, named because it is the kind that
repeats:** §5 of the note priced arm `A0` as **"≤ 0.5"** — an inequality, not a
point estimate. L-463 forbids that: a cost prediction is a point. The `1.9`
denominator above treats it as `0.5`, which is the most favourable reading
available to the predictor, and the ratio is reported against that.

**Dollars: 12.217 core-min = 0.20362 core-h ≈ $0.010446, DERIVED — NOT
MEASURED**, at the owner-stated c7a.4xlarge $0.0513/core-h (REPORTED-BY-OWNER
2026-08-21/22). The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 5. What is NOT settled

1. **No verdict, and no rung is graded. T25RF closes nothing.**
2. **The extrapolation to 1 800 steps in the note's §6 (A2T ≈ 8.3 core-min) is an
   extrapolation from 60 steps inside one load branch**, taken on a shared box,
   and the note says it must be priced with margin. Nothing here raises its
   status.
3. **`build_t25R.py`'s rule-6 referral is untouched**; the probe case was built by
   copying the already-built `T25R_L1` mesh. `T25R_L1`, `T25R_L2` and
   `T25R_L2_DT025` were not written to.

---

## 6. Authority

Filed by a heat-transfer `lab-lane` at the heat-transfer-supervisor's dispatch;
decisions `[lab-attributed]`. **Nothing here has been sent, filed, submitted,
uploaded, registered or posted outside this box** (`CLAUDE.md` rule 7). No
agent's message is Sanaa's consent (rule 9).
