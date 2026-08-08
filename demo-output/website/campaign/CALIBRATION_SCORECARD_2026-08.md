# Calibration scorecard — 2026-08 (first cohort)

First concrete cut of the §1 calibration scorecard from
`docs/CAPABILITY_STRATEGY.md` ("every prediction the lab makes logged
prediction-vs-outcome"). Cohort: **every graded prediction in the records
from 2026-08-01 through 2026-08-08** — a prediction counts only if it was
written down before the outcome and the record itself grades it. Compiled
2026-08-08 (UTC); read-only sweep, zero solver core-min. All paths under
`/home/ubuntu/Certonomous/`.

**Headline. Base cohort (the sweep's window, closed before 22:32Z):
N = 93 graded predictions across 25 records — 52 held, 33 failed, 4
partial (SpaRTA G2/G4/G5-V2, DEFECT_REACH N7), 4 not evaluable (hills P3,
extension P3, F8 step-1, A4 coloring-off) → 61% of decisively-graded
predictions held (52/85). A dated 5-row addendum (the weighted arm,
landed 22:32Z, `91fe03b3`) brings the running total to N = 98: 55 held /
35 failed / 4 / 4 — hit rate 61% either way (55/90). Cost forecasts: 32
record-level pairs, median measured/estimated ≈ 0.77, exactly 2 factor-3
breaches, one each direction; 26 docket-level pairs, aggregate 1.79,
median 0.77. Stated numeric confidence: zero of 98 — the single clearest
gap, and the proposal filed with this scorecard (`agenda/proposals/
pre-registrations-carry-a-confidence-line.json`) exists to close it.**

---

## 1. The prediction table

Stated confidence is **"none" on every row** (see §4), so the column is
omitted. Error factor = measured/predicted (or measured/bar) where the
prediction is quantitative.

### Campaign records

| # | source | prediction (short) | outcome | error factor |
|---|---|---|---|---|
| 1 | `campaign/MODEL_FORM_H_HILLS_PREREGISTRATION.md` | P1 kOmegaSST reproduces archived 7.6472 within 1% | HELD | 1.000005 |
| 2 | same | P2 ≥1 non-SST member fails gate (realizableKE named) | HELD (over-fulfilled: all 3 failed) | — |
| 3 | same | P3 admitted members above band; band excludes 4.455 | NOT EVALUABLE (membership n=1) | — |
| 4 | `campaign/MODEL_FORM_H_EXTENSION_PREREGISTRATION.md` | P1 SA settles 14–18k, rKE 19–24k, both <30k | FALSIFIED | SA 12,361 (0.69–0.88×); rKE >30k (>1.25×) |
| 5 | same | P2 both members carry a steady bubble | FALSIFIED (SA converged attached on all 120 faces) | — |
| 6 | same | P3 n=3 band excludes 4.455 | NOT EVALUABLE | — |
| 7 | `campaign/W1_HUMP_CHALLENGE_RESULTS.md` | Gate V reproduces F6a within ±0.005 both crossings | TRUE | 0.0000/0.0003 |
| 8 | same | separation −1..−2%; reattachment +12..+16% | TRUE (all clauses) | −1.59%, +13.92% |
| 9 | same | QCR outcome two, \|Δreatt\| < 0.010 | TRUE | 0.22 of bar |
| 10 | same | cost SST ≤6, QCR ≤8 core-min | TRUE | 0.93 / 0.59 |
| 11 | `campaign/W1_HUMP_A1_RESULTS.md` | both a1 arms converge within 5000 cap | FALSE | — |
| 12 | same | a1=0.34 moves reatt −0.010..−0.060 toward experiment | TRUE | −0.0498 (5× bar) |
| 13 | same | neither arm repairs Gate P | TRUE | +9.4% |
| 14 | same | cost ≤12 core-min | FALSE | 1.72 |
| 15 | `campaign/DMR_RESULTS.md` | Gate V passes both rungs, R1 < R2 error | TRUE | 0.15%/0.17% |
| 16 | same | Gate P1: detector finds both triple points at R1 | FALSE as written | 2nd kink 0.13 vs 0.6-cell threshold |
| 17 | same | R2 secondary structure marginal-to-absent | TRUE | — |
| 18 | same | Gate P2 \|Δchi\| ≤ 1.5° | TRUE | 0.87° |
| 19 | same | cost ≤20 core-min (estimate graded per its own cost_basis) | estimate FAILED factor-3 | 0.12 (~8× cheap) |
| 20 | `campaign/N_A10_THIRD_MEMBER_PREREGISTRATION.md` | P1 fresh solve within 1e-3/1e-4 of archived | HELD | bit-identical |
| 21 | same | P2 all clauses pass, margins ~20× | HELD | 28×/54× measured |
| 22 | same | P3 CFL3D Cl contained at n=3 | HELD | — |
| 23 | `campaign/F6b_QCR_RESULTS.md` | converges within 12,000 iters | TRUE | 6,177 |
| 24 | same | outcome N, \|Δx_R\| < 0.10 | TRUE | 0.34 of bar |
| 25 | same | cost ≤15 core-min | TRUE | 0.61 |
| 26 | `campaign/F6b_ERCOFTAC_RESULTS.md` | Gate P fails on reattachment, x_R/h in [7.0,8.3] | HELD | 7.6472 (+72%) |
| 27 | same | Gate P passes on separation, x_S/h in [0.20,0.30] | HELD | 0.2604 |
| 28 | same | Gate V passes (flagged "the risky one") | HELD | 0.043% |
| 29 | same | medium-to-fine change 3–12% | FALSIFIED | 0.032 (30× smaller) |
| 30 | same | Gate Q in [10%,16%] | HELD | 12.82% |
| 31 | `campaign/B52_RUNG7_RESULTS.md` | G4 Cd rises to 0.0535–0.0575, increment >+0.0027 | SCORED FALSE | 0.872; increment sign-flipped (−0.004055) |
| 32 | same | G1 h-ratio within 3% of 1.0904 | HOLDS | 0.94% |
| 33 | same | G2 rung settled (both limbs) | HOLDS | 0.074%/0.88% |
| 34 | `campaign/B52_RUNG8_RESULTS.md` | surface resolution flat, b < 1/3 | REFUTED | b = 0.707 |
| 35 | same | Cd(≈880k) inside valid-family span | TRUE | 0.047942 |
| 36 | same | refit stays monotone:false | FALSE as written | finest triple monotone |
| 37 | same | conclusive:false, no order fitted | TRUE in verdict (guard downgraded p=28.7) | — |
| 38 | `campaign/W3_CUBE_SETTLE_RESULTS.md` | P1 cube converges 600–3000 iters | FALSE | — |
| 39 | same | P2 settled Cd outside [1.0946,1.1102] | FALSE | 1.097820 inside |
| 40 | same | P3 \|ΔCd\| exceeds 2σ | FALSE | 0.428 |
| 41 | `campaign/W3_MESH_NOISE_FLOOR_RESULTS.md` | P1 scatter grows with cell count | FALSE (backwards on 0012: falls 14.45×) | — |
| 42 | same | P2 r1/r2 scatter <20% of increment | FALSE both bodies | 158%/87% vs 20% |
| 43 | same | P3 r3 scatter below r2→r3 increment | TRUE | 21%/15% |
| 44 | `campaign/W3_WING_VALID_FAMILY_RESULTS.md` | P1 neither family returns an observed order | scored FALSE | — |
| 45 | same | P2 NACA 4412 non-monotone | scored TRUE | — |
| 46 | same | P3 4412 moves further than 0012 | scored FALSE | — |
| 47 | `campaign/W3_RACE_NUMERICAL_RESULTS.md` | peak is NOT at the edge (proposal's remedy wrong) | CONFIRMED by G2 | curvature wrong sign, 257× off in proposal |
| 48 | `campaign/R7_STROUHAL_SPACING_RESULTS.md` | Strouhal robust (<5%) at Re 1000 | HELD | 0.024 of bar |
| 49 | `campaign/R4_ASYMPTOTIC_RESULTS.md` | G4 increments shrink, phi0 > 0.0733 | SCORED FALSE | phi0 = −0.0845 (negative drag) |
| 50 | `campaign/W1_bump_nasa_grids.md` | seeded coarse rung within 3e-7 settle tolerance | HOLDS | 0.083 of tolerance |
| 51 | same | fit above order_window like CFL3D's | held | 3.200 vs 2.913 |
| 52 | `campaign/F6a_DIFFUSION_RESULTS.md` | T1 falsifier (wrong direction / <0.005 / non-monotone) | NOT FALSIFIED — H survives | swing 6.6× the bar |
| 53 | `campaign/F8_MRF_HAND2001_GATE.md` | window mean within half-width of published torque | NOT EVALUABLE (named risk fired) | spread 19.2× cap |
| 54 | same | window turbine-signed by t=2000 (flagged "weak") | scored FALSE | +138 N·m motoring |

### Committee grids (pre-registered and scored 2026-08-01, commits `6c896fe4`→`ab132a17`)

`committee-grids/PREDICTIONS.md`, 14 predictions (P1–P14): **5 held**
(P1, P2, P5, P6, P13), **9 falsified** (P3, P4, P7–P12, P14). Rows 55–68.
Note carried from the sweep: the record's own prose says "Four of
fourteen held" while its table marks five — the table is the auditable
artifact and is counted here; the prose defect is flagged for the record's
owner.

### W2 SpaRTA regression gates (2026-08-01)

`campaign/W2_SPARTA_REGRESSION.md` (prereg committed before evaluation).
Rows 69–74: G1 HIT; G2 NEAR MISS (coeff 0.586 of published — inside
factor 2, outside ±25%); G3 MISS as worded; G4 half HIT/half MISS
(partial); G5-V1 PASS incl. tightened ±25% (1.124); G5-V2 NEAR MISS from
the good side (0.724). Counted: 2 held, 1 failed, 3 partial→(G2, G4,
G5-V2).

### DAFoam records

| # | source | prediction | outcome | error factor |
|---|---|---|---|---|
| 75 | `dafoam/DEFECT_REACH_decomposition_cases.md` | N1 A4 z-slabs in [0.05%,1.5%] | HELD | 0.52% |
| 76 | same | N2 A4 2×2×1 ≤1% | NOT HELD | 1.40 |
| 77 | same | N3 Ahmed-35 np=1 ≤1.5% | NOT HELD | 45× bar |
| 78 | same | N4 defect ≥2% both instruments | NOT HELD as registered | 0.68 |
| 79 | same | N5 Ahmed-35 simple411 ≤1% | NOT HELD | −3.13% |
| 80 | same | N6 CBFS decomposition-invariant | HELD | 1.1e-04 |
| 81 | same | N7 cross-residual ≥10×‖b‖ + localization + control | SPLIT | 0.545 on threshold |
| 82 | same | N8 sail decomposition-invariant | HELD | 0.0047% |
| 83 | same | N9 freestream BC gates defect, analytic in 2.40–2.43e-1 | HELD | 2.4062e-1 |
| 84 | `dafoam/DISCRIMINATORS_A4_decomposition_mechanism.md` | cross residual will be large | HELD | 3.3e+02 |
| 85 | same | coloring-off will not change the gradient | NOT SCORED (arm died on memory) | — |
| 86 | `dafoam/A3_TPC1_CONTROL_PREREGISTRATION.md` + `A3_SUBLU_RESULT.md` | control reproduces the −5 stall signature | HELD | bit-identical |
| 87 | same | TPC1-alone: pre-declared outcome-one mapping | outcome one FIRED (reason 2, 368/383 it.) | — |
| 88 | `dafoam/ladder-b/S1_CBFS_REINVERSION_RESULT.md` | P1 beta=1 varU < 7.6e-3 after repair | PASS | 0.081 |
| 89 | same | P2 y>2 loss share <50% at baseline | PASS | 0.512 |
| 90 | same | G1 J_qoi ≤ 0.70 within budget | GATE PASS | 0.369 |
| 91 | same | G2 >50% top-decile \|beta−1\| in window | GATE FAIL (recorded without softening) | 0.538 |
| 92 | same | FD re-anchor 3 comps <1%, no sign flips | PASS | ≤0.115% |
| 93 | same | limiter top-decile cells move below 1 | held | 75.6% |

### Addendum — weighted arm, landed 2026-08-08 22:32Z (`91fe03b3`, adjudicated `d66f82a5`), after the sweep cutoff

| # | source | prediction | outcome | error factor |
|---|---|---|---|---|
| 94 | offline weighted-loss variant (pre-reg `2c475ab5`, results `71dbf5a8`) | capturability R_W1/R_W2 ≥ 0.70 bar | HELD | 0.9494/0.9468 (1.36× bar) |
| 95 | `dafoam/ladder-b/S1_CBFS_WEIGHTED_ARM_RESULT.md` | Gate A masked-β nonlocality ≥ 0.80 (stop bar 0.70) | PASS | 0.9458/0.9283 |
| 96 | same | Gate B FD 3 comps <1%, no sign flips | PASS | ≤0.033% |
| 97 | same | G1w normalized Jw ≤ 0.05320 | GATE FAIL | 0.05713 (1.074× bar) |
| 98 | same | G2w window share >50% | **WRONG, graded as such** (42.7%; correction 79.7% inside loss support — reclassified "accounting, not placement" by `d66f82a5`) | 0.854 of bar |

---

## 2. First reliability statement

| grade | count |
|---|---|
| held / true / pass / confirmed | **55** |
| failed / false / falsified / refuted / miss | **35** |
| partial / near-miss / split | **4** |
| not evaluable / not scored | **4** |
| **total** | **98** |

**Of 90 decisively-graded predictions, 55 held → 61%** (with partials as
half-credit: 57/94 ≈ 61%). Read correctly, this number is healthy, not
alarming: the lab's pre-registrations are written to be falsifiable
(P2/L-3 discipline), and several records celebrate their own misses
("Zero of three... That is what pre-registration is for"). A hit rate
near 100% would mean the predictions were too safe to be informative. What
the scorecard cannot yet say is whether the lab *knows in advance* which
predictions are the risky ones — see §4.

Sub-populations worth tracking next cohort:
- **Gate-reproduction/verification predictions** (Gate V class, controls,
  bit-identity claims: rows 1, 7, 20, 28, 32–33, 50, 86, 95–96) ran ~100%
  held — the lab is well-calibrated about its own machinery.
- **Physics-outcome predictions** (where the flow decides: rows 4–5, 31,
  34, 38–42, 49, 54, committee grids) ran well below 50% — the lab's
  priors about unmeasured physics are appropriately adventurous and
  frequently wrong, which is where the information is.

## 3. Cost forecasts — distribution of measured/estimated

**Structural note first:** `agenda/docket.json` carries
estimate/measured/basis fields but **no factor-3 verdicts** — the grading
instrument is `scripts/cost_calibration.py`, and pass/fail-vs-estimate
verdicts live in the individual record files. The scorecard therefore
grades from both layers separately.

**Record-level (32 sweep pairs + the weighted arm's 229.07/250 = 33):**
median ≈ **0.78**; range 0.018 → 4.25. Factor-3 breaches: **2** — DMR at
**0.12** (~8× on the cheap side; the record grades its own estimate FAILED
per its cost_basis) and the A3 sub-LU sweep re-file at **4.25×** (OOM
exploration under the pre-registered runs-to-reason-codes commitment,
ended by the host floor). The dominant bias is **overestimation of cost**
(most ratios < 1) — conservative pricing, cheap reality.

**Docket-level, graded by `scripts/cost_calibration.py` off
`agenda/docket.json` (26 pairs; script re-run for this scorecard,
2026-08-08):** aggregate ratio **1.792**, median **0.766**; **three**
factor-3 breaches, all on the over-run side
(`w5-regrade-every-published-gradient-claim` 3.85×,
`w4-the-grid-not-the-box-was-the-limit` 9.79×, `agp-e5136061890b`
13.55×); **8 of 26 items spent exactly zero** solver time — the work
turned out to need no solves, which the script's own banner names as the
proof that "a 3× planning multiplier is the wrong instrument" (it
brackets only 12 of 26 pairs).

**The lab's own explanatory split** (cost_calibration.py): pairs whose
`cost_basis` begins "measured" — 10 pairs, worst 1.84×, median 0.841;
pairs priced from a forecast — 16 pairs, worst 13.55×, median 0.075.
**The predictor is the basis, not a factor**: estimates anchored on a
measured sibling are already inside factor-3 essentially always; unanchored
forecasts are the entire tail in both directions. That finding is the
strategy's "cost model v2" item stated as a measurement.

## 4. What is missing for real reliability curves — and the proposal filed

**Zero of the 98 predictions carries a numeric confidence.** The sweep
grepped the corpus for every confidence-percentage phrasing and found none
attached to any prediction (the only "95% confidence" string in the estate
is a certificate-template labelling defect the Verification Charter
records for removal). A reliability curve ("of the predictions asserted at
70%, did 70% hold?") is therefore uncomputable this quarter — the outcomes
exist, the stated probabilities do not.

The raw material is visibly there. The records hedge **ordinally** and the
hedges are informative: "the risky one" (F6b Gate V — held), "the file's
own weakest claim" (F6b prediction 4 — the one that failed), "weak and
stated as such" (F8 step 2 — failed), "the number most likely to miss"
(R7's cost — missed by 38%). In at least three cases the verbally-flagged
weakest prediction is exactly the one that failed. The lab already has
self-knowledge; it has never written it as a number, so it cannot be
scored.

**Proposal filed with this scorecard:**
`demo-output/website/agenda/proposals/pre-registrations-carry-a-confidence-line.json`
(criterion: instrument-check, 0 core-min) — the pre-registration template
gains one line per prediction, `confidence: X%`, so the machinery starts
capturing what the scorecard needs. Next quarter's scorecard can then bin
by stated confidence and draw the first reliability curve, including the
agentic-confidence question the strategy names (does 70% mean 70%?).

## 5. Method note — fork loss and inline re-verification

The cohort sweep was executed by a read-only records-sweep agent that
produced no files and whose turn ended before its report was delivered
directly (the standing watchers-die-with-the-agent pattern). Its
completed report reached this scorecard by two channels that agree
verbatim: recovery from its transcript on disk, and the chief's relay
("Explore sweep relayed by chief, 2026-08-08"). Per the dead-lever
auditor's standard for recovered output, its rows were then re-confirmed
inline against the primary records before use: every quantitative grading row in §1 was
either re-read byte-for-byte from the cited record by the compiling agent
(≈30 records opened: hills/N_A10/hump-challenge/a1/DMR/B52 r7+r8/cube/
noise-floor/wing-valid/race/R4/R7/bump/diffusion/F8/F6b×2/SPARTA/
committee-grids/DEFECT_REACH/DISCRIMINATORS/A3 control/S1 reinversion/
weighted arm) or cross-corroborated against the negative-verdict review's
outcome blocks; the docket cost table was re-derived by re-running
`scripts/cost_calibration.py` directly (§3 quotes that re-run, which is
why its breach count includes the out-of-window 13.55× pair the fork's
windowed view listed separately). The §1 addendum rows (94–98) postdate
the fork's sweep and were compiled inline from `91fe03b3`/`d66f82a5`.

## 6. Scope decisions (stated so the cohort is reproducible)

- **D5 RSM excluded** (prediction and result both 2026-07-29, out of
  window; its 2026-08-08 commit is an audit-trap addendum only). If
  included it adds 4 predictions: 2 held, 1 failed, 1 partial.
- **F12 excluded from the cohort and counted instead as an ORPHANED
  pre-registration** (chief ruling): a prediction set with no results
  record is a dashboard-metric item (see
  `IMPROVEMENT_DASHBOARD_2026-08.md` metric 5), not a graded row. It is
  the standing IOU this scorecard will look for next month.
- **R5_PREREGISTRATION.md and closure_challenge_R5_ALPHA05 excluded from
  the prediction cohort**, with the nuance stated precisely and neither
  half softened: the BINDING acceptance criterion (`0bade54a`) predated
  every solve — the anti-hindsight chain Ladder V rung V2 proved — but
  these pre-registration DOCUMENTS postdate the solves/training they
  gate, so they may not count as graded predictions under the
  written-before-outcome test. (Their own disclosure of this is the
  discipline working.)
- **Committee-grids held-count discrepancy** (chief ruling): the table
  marks FIVE predictions held, the prose says "Four of fourteen held."
  This cohort counts from the table (the auditable artifact), reports
  the discrepancy itself as a record defect, and files the correction
  request rather than silently choosing:
  `agenda/proposals/committee-grids-held-count-correction.json`.
- Predictions graded but "NOT EVALUABLE" via a pre-declared branch
  (rows 3, 6, 53, 85) are excluded from the reliability denominator: the
  registered branch fired, so neither held nor failed.
