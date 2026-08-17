# Round-5 QCR route — application rule, FROZEN before any solve

**Written 2026-08-05T17:41Z, before the validation arms were launched and
before any test-duct case directory was created.** Item:
`w3-qcr-forward-on-the-ducts-is-the-rank-1-route` (approved and claimed
2026-08-05, Katie's blanket approval + rank-1 directive). Plan of record:
`demo-output/website/CLOSURE_RANK1_CAMPAIGN.md` §5 (Route A1), whose proposed
rule form this document instantiates with numbers.

The purpose of this freeze is stated by the proposal's own in-sample verdict:
we already know the round-4 test-duct scores (0.0811 / 0.0775 / 0.0325), and
any protocol that lets those numbers choose between the QCR field and the
existing ML field is test-truth-informed model selection. Every degree of
freedom in that choice is therefore closed here, in writing, before any new
number exists.

## 1. The model, frozen

- `kOmegaSSTQCR`, library commit **303247bb**
  (`sdk/openfoam/qcr/kOmegaSSTQCR/`), binary
  `libkOmegaSSTQCRTurbulenceModels.so` SHA-256
  `b741839596bc8624789652fdc69b476594dc24419edd21faedac004e2c1cc808`.
- **`Ccr1 = 0.3`** (Spalart 2000, untrained). It is not tuned, not now, not
  after the validation number, not ever under this item. The moment it is
  fitted the route loses the no-training-range property that is its entire
  case.
- k and omega transport unchanged; the term is constitutive-only.
- All solves fresh from the shipped `0/` fields (`startFrom startTime`),
  shipped mesh, shipped BCs, shipped `fvOptions`, shipped `fvSchemes` and
  `fvSolution` (`residualControl`: k 5e-6, omega 1e-10), one core per arm,
  exactly the falsifier arm pattern (`w3-qcr-duct/run_arm.sh`). The only
  edits per case are the falsifier's own: `libs(...)` line, `startFrom
  startTime`, an iteration cap in `endTime`, and the two OF7-only
  `#includeFunc` lines commented out.

## 2. Validation first: `AR_7_Ret_180`

SST and QCR both run on `AR_7_Ret_180` — the benchmark's own suggested duct
validation case, not a test case — and both are scored against its shipped
LES field (`0/U_LES`) with the falsifier battery's metric, before any test
duct is touched:

- scaled MAE = `mean(||U - U_LES||_2) / mean(||U_LES||_2)` over all cells;
- in-plane Pearson r on the pooled (Uy, Uz) components;
- in-plane RMS as percent of bulk, against the LES reference.

The result is recorded whatever it says.

## 3. The all-or-none rule

**QCR ships on ALL THREE test ducts (`AR_1_Ret_360`, `AR_3_Ret_360`,
`AR_14_Ret_180`) if and only if every clause below holds on `AR_7_Ret_180`;
otherwise it ships on NONE and the route is recorded as declined on
validation evidence.**

- **V1 — accuracy.** QCR scaled MAE ≤ **0.70 ×** SST scaled MAE (≥ 30%
  reduction). Basis: the weakest of the four training-duct reductions was
  33.5% (`W3_QCR_DUCT_FALSIFIER.md` §3); a validation duct that cannot
  reach even 30% says the training-duct evidence does not transfer to an
  unseen geometry, and the route stops.
- **V2 — structure.** In-plane Pearson r(QCR, LES) ≥ **0.85**. Basis: the
  weakest training-duct r was 0.877. Magnitude without the right structure
  is not the mechanism this route claims.
- **V3 — convergence.** Both AR_7 arms stop on their own `residualControl`
  within the iteration cap of §5. A cap-stop on either arm fails the gate
  (the hump lesson: cap-stopped is not converged).

No per-case selection. No score-informed second look. If the gate passes and
a later number looks bad, it ships anyway; if the gate fails and a later
argument looks good, nothing ships.

## 4. `AR_14_Ret_180`, decided now

Our ML entry scores 0.0325 there — a tie with rank 1 — and the training
evidence (AR_10, the largest-AR training duct, had the weakest QCR ratio
0.664 and weakest r 0.877) suggests QCR may be worse than the ML correction
on the highest-aspect-ratio duct. **Under the all-or-none rule AR_14 follows
the rule, and the possible loss of the 0.0325 tie is accepted here, in
advance, in writing.** The alternative — keeping ML on AR_14 while switching
the other two — is exactly the per-case selection §3 exists to forbid,
because the only thing recommending it is a known test score.

## 5. Convergence caps (endTime), fixed per case from the shipped logs

| case | shipped baseline iters | cap (endTime) |
|---|---|---|
| `AR_7_Ret_180` | 3,636 | 12,000 |
| `AR_1_Ret_360` | 405 | 3,000 |
| `AR_3_Ret_360` | 1,540 | 6,000 |
| `AR_14_Ret_180` | 7,009 | 14,000 |

Caps are ~3× the shipped baseline count (AR_14 at 2×, bounded by budget).
**Converged-only discipline extends the all-or-none rule: if any test-duct
QCR arm cap-stops instead of converging on `residualControl`, the route is
void for all three ducts** — no cap-stopped field is submitted, and no
mixed submission (converged ducts QCR, unconverged ducts ML) is allowed,
because that mixture would again be selection.

## 6. Topology diagnostic — reported, not a gate

Per the supervisor's addition from the metric census
(`CLOSURE_EVALUATION_PROTOCOL.md`): the round-4 ML correction restores duct
secondary-flow intensity but draws the wrong topology (one vortex where LES
has the counter-rotating corner pair). On AR_7 the census's own instrument
(`sdk/scripts/closure_eval_battery/run_duct_battery.py::figure_secondary_flow`,
Ling et al. JFM 2016 layout) is run on [SST, QCR, LES] and the question
answered explicitly: **does QCR draw the counter-rotating corner-vortex pair
with two distinct centres?** The figure and the answer go in the record
whatever they show. This diagnostic is deliberately NOT a numeric clause of
§3 — it is declared here so it cannot be recruited afterwards as a post-hoc
selector in either direction.

## 7. Budget, scoring, and stop

- 95 core-min hard, ledgered in `ledger.txt` beside this file.
- If the gate passes: the three test-duct QCR solves read RANS inputs and
  mesh only — no test ground truth is opened, no scoring call is made.
  Fields are interpolated to the official evaluation points (coordinates
  only) and written as round-5 CSVs with the five non-duct CSVs copied
  byte-identical and hash-asserted.
- **HARD STOP before scoring.** The round-5 pre-registration goes to the
  supervisor; the scoring-call ledger stays at 5 in this session.

*Nothing below §7 existed when the AR_7 arms were launched.*

**Dated ledger note, 2026-08-17 (Ladder V rung V7; additive only, no frozen
clause touched, and the first addendum this file has carried):** §7's
sentence *"the scoring-call ledger stays at 5 in this session"* was true **of
the session that wrote this file (committed 2026-08-05 at `0bade54a`, before
the first validation iteration existed)** and is scoped to it, because the
standing count has since moved: the supervisor's designated scoring agent
made the round-5 call on 2026-08-07, and **the cumulative ledger is now SIX**
distinct prediction sets scored (floor, rounds 1–5), so the next call would
be the **7th**. This session made none, the frozen rule above is untouched,
and only the sentence describing the ledger needed a date on it.
