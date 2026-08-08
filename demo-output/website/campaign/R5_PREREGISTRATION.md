# R5 — the QCR forward entry: pre-registration

**Written 2026-08-07, after the forward solves and before any scoring call.
No scoring call has been made in producing anything below: the guard of
`sdk/scripts/closure_round5_qcr_forward.py` stubbed every scoring and
truth entry point of the evaluation package and verified itself armed before
the first case was touched. The scoring-call ledger stands at 5, where round
4 left it. The one call that turns this file into a per-case table belongs
to the supervisor, not to the session that wrote this.**

Item: `w3-qcr-forward-on-the-ducts-is-the-rank-1-route` (approved and
claimed 2026-08-05, Katie's blanket approval + rank-1 directive). Plan:
`CLOSURE_RANK1_CAMPAIGN.md` Route A1. Rule: `R5_RULE_FREEZE.md`, committed
`0bade54a` **before the first validation iteration existed**.

---

## 1. The frozen rule was honoured, and this section is just the receipts

The rule (frozen 2026-08-05T17:41Z, before any solve): *QCR ships on ALL
THREE test ducts iff, on the benchmark's own suggested validation duct
`AR_7_Ret_180`: V1 — QCR scaled MAE ≤ 0.70 × SST's; V2 — in-plane Pearson
r ≥ 0.85; V3 — both arms converge on their own `residualControl` within the
cap. Otherwise NONE.*

Measured (`R5_validation_AR7.json`; solves 2026-08-05, evaluated against the
validation case's legal LES truth):

| clause | bar | measured | verdict |
|---|---|---|---|
| V1 | ratio ≤ 0.70 | scaled MAE 0.0400 (QCR) vs 0.0839 (SST) → **0.4770** | pass |
| V2 | r ≥ 0.85 | **0.9284** | pass |
| V3 | converged | SST 4,652 / QCR 4,660 iters, cap 12,000, both stopped by `residualControl` | pass |

**Gate verdict: ALL.** QCR replaces the round-4 ML duct correction on all
three test ducts, including `AR_14_Ret_180` (§4). No clause was added,
dropped, or re-thresholded after the freeze.

Supporting validation measures, reported not gated: QCR in-plane RMS 0.644%
of bulk against the LES 0.701% (92% recovery, ratio 0.918 — under 1, the
same systematic slight weakness as all four training ducts); SST in-plane
RMS 1.2e-15 of bulk (the machine zero, on the fifth duct in a row).

## 2. The topology check: QCR draws the vortex pair

The metric census found the round-4 ML correction restores duct
secondary-flow *intensity* while drawing the wrong *topology* — one vortex
where the truth has the counter-rotating corner pair. The census's own
instrument (`run_duct_battery.py::figure_secondary_flow`, Ling et al. JFM
2016 layout) was run on [SST, QCR, LES] for the validation duct:
`duct_secondary_flow_AR_7_validation_qcr.png`.

**Answer, stated plainly: yes. QCR draws the counter-rotating corner-vortex
pair with two distinct centres** — one near (z/h ≈ 6.1, y/h ≈ 0.5), the
second tight against the side wall near (z/h ≈ 6.85, y/h ≈ 0.55) — in the
same positions, with the same sense, and with the same flanking high-speed
wall lobes as the LES panel. Mean in-plane magnitude 4.65e-3 of bulk vs
truth 4.90e-3. The visible deficit: the LES's weak tertiary recirculations
near the centreplane (z/h < 1.5) are smoothed into elongated lobes. The
structure the ducts are scored on losing is the corner pair, and the
untrained in-PDE term produces it where the trained post-hoc field could
not. (Per the freeze §6 this figure is a reported diagnostic, not a gate
clause, and it changed nothing about §1's verdict.)

## 3. Exactly what changes in round 5, per case

| # | case | round-5 prediction | provenance |
|---|---|---|---|
| 1 | `alpha_15_13929_4048` | **unchanged** — byte-identical to round 4 | sha256 `e7b28d5357decf691f21b1b685c641ae054f421575e97bbb94f9cf0dafbbf3e9` |
| 2 | `alpha_15_13929_2024` | **unchanged** | `1d49b9e3135a76096046479b56883a680dc0b036b1f2876b0d9ae2c54f7b54b7` |
| 3 | `alpha_05_4071_4048` | **unchanged** (declined case, = RANS) | `0c3865984218474ad83c97eb0be37389385dd446fcff499b510bd72839b2db4c` |
| 4 | `alpha_05_4071_2024` | **unchanged** (declined case, = RANS) | `af9cccda9c322b87e2d89f79829b74152f23c8829f7f32d1d92afcca68033b4e` |
| 5 | `AR_1_Ret_360` | **QCR forward solve**, converged 395/3,000 iters | `bb8d61fbbfd99f5099628cedf7b76a203558daa87e3235006b0c8527ea703e7e` |
| 6 | `AR_3_Ret_360` | **QCR forward solve**, converged 1,956/6,000 iters | `c567ff25577a20a2ac8afa8b434ea2c5ceb647c9307389021641ac89e33b4789` |
| 7 | `AR_14_Ret_180` | **QCR forward solve**, converged 8,947/14,000 iters | `286610c0488d202c84c389b18befc2d1352fbbbbef7ae125066f9e289fa699ce` |
| 8 | `NASA_2DWMH` | **unchanged** | `cf8e023c7b8fcb0572a1189977cbfebbb8f4f76b0d59f305aebca2e3e0fba686` |

Only the three ducts change. The five unchanged CSVs were copied from the
round-4 submission and hash-asserted against its manifest inside the
producing script, so any score movement is attributable to the duct family
alone. Every QCR solve stopped on its own `residualControl` — **no
cap-stops anywhere in this route** (the freeze voided the whole route on
any test-duct cap-stop; the clause was never exercised). AR_5/AR_10-style
cap-stop reruns were budgeted and not needed.

The model behind rows 5–7: `kOmegaSSTQCR` (commit `303247bb`, library
sha256 `b7418395…1cc808`), `Ccr1 = 0.3` untrained, k/omega transport
unchanged, run fresh from the shipped `0/` fields on the shipped meshes,
schemes and `fvSolution` untouched. Nothing anywhere in rows 5–7 was
fitted to anything. Test cases were opened for RANS inputs and mesh only;
the `*_LES` files were never copied into the run tree
(`/home/ubuntu/certonomous-runs/w3-qcr-rank1/`), so test truth was not
merely unread — it was absent. Interpolation to the 1,000 official
evaluation points uses the benchmark's shipped convenience coordinate
files, proven row-identical to the package's own ordering at write
precision (max row-wise deviation 4.9e-8,
`closure_round5_points_order_check.py` — a check that retrains the
deterministic round-4 model rather than open any truth file).

## 4. Known risks, stated before the score exists

- **`AR_14_Ret_180` is the sharp one: round 4 scores 0.0325 there, a
  0.00003-level tie with rank 1, and this submission puts that tie at
  risk.** Decided in the freeze, before validation ran: all-or-none, AR_14
  follows the rule, the possible loss accepted in writing. What the
  evidence says: the risk-side signal is training-side — AR_10, the
  largest-aspect-ratio training duct, had QCR's weakest ratio (0.664) and
  weakest r (0.877), and AR_14 extends that trend axis. The comfort-side
  signal is validation-side — AR_7 (AR = 7, between them) came in at
  0.477/0.928, far above the freeze bars. Neither signal is a test score,
  and the per-case selection that would "protect" AR_14 is exactly the
  test-truth-informed choice the rule exists to forbid.
- **The Ret_360 transfer is untested against truth, anywhere.** AR_7 is a
  Ret_180 case; no legal duct truth exists at Ret_360. The route's claim is
  structural, not empirical: QCR has no trained range, so the Re_y
  extrapolation that demonstrably cost round 4 its duct scores cannot
  recur by the same mechanism. But "cannot fail the old way" is not
  "cannot fail", and the campaign's own transfer band spans **0.059
  (rank 1) to 0.0666 (worse than round 4)**.
- **The two Ret_360 floors are higher** (published RANS floors 0.1288,
  0.1243 vs the training family's 0.06–0.11), so the transferred ratios
  are being applied to larger bases; the central estimate remains 0.0617
  (rank 2), and rank 1 requires roughly the best observed training ratio
  to transfer.

## 5. Accept criterion, and what ships regardless

- **The submission improves on the entry of record iff overall < 0.065438**
  (round 4). Per the campaign arithmetic, matching rank 2's duct scores
  gives ≈ 0.0563 (**rank 1**, Reissmann at 0.059525); the pre-stated
  expectation band is 0.059–0.0666.
- **One scoring call** produces the round-5 per-case table, made by the
  supervisor, not this session. **Whatever it says is what the record
  carries** — including an AR_14 regression, which is reported exactly as
  the round-2 NASA regression was, not quietly reverted. A post-hoc revert
  of any single duct after seeing its score would be the per-case
  selection this document forbids; the only honest post-score fallback is
  the whole all-or-none bundle judged as a bundle.
- If the call lands worse than 0.065438 overall, round 4 remains the entry
  of record and the route is closed as *measured worse on test*, with this
  pre-registration as the proof the attempt was clean.

## 6. Method upgrade: the fields are physical at the level the audit measures

The physicality audit (`closure_challenge_stability_physicality_audit.md`,
G2) found the round-4 ML duct fields carry volume-weighted RMS `∇·U` of
3.6e3–9.7e3 s⁻¹ — **~10¹⁵ × the RANS baseline's own 5e-12–2e-11** — because
a post-hoc cell-wise `δU` respects no conservation law; the audit recorded
this as a material physicality cost of the method class. The QCR fields
are the output of a converged SIMPLE solve: continuity is enforced by the
pressure equation on the face fluxes **by construction**, not asserted
afterwards. Measured through the audit's identical Green-Gauss operator
(`closure_challenge_round5_qcr_forward.json`):

| case | round-4 ML field rms ∇·U | QCR field rms ∇·U | improvement | QCR ∇·U / ‖∇U‖ |
|---|---|---|---|---|
| `AR_1_Ret_360` | 9,160 | **345** | 27× | 8.5e-4 |
| `AR_3_Ret_360` | 9,749 | **169** | 58× | 5.3e-4 |
| `AR_14_Ret_180` | 3,584 | **57** | 63× | 5.4e-4 |

Stated honestly rather than rounded to a slogan: the *cell-centred*
Green-Gauss divergence of the QCR fields is not the baseline's machine
zero, because SIMPLE enforces continuity on face fluxes and the explicit
QCR stress divergence enters the cell-to-face (Rhie–Chow) consistency at
the 5e-4-of-gradient level. That is a 27–63× reduction against the fields
this submission replaces, on the identical operator, and it closes audit
finding G2 for the duct family: the submitted duct fields now come from a
solve, and their residual non-solenoidality is solver-consistency small,
not model-structure large.

## 7. Cost and provenance ledger

| arm | iters | wall s | core-min (1 core) |
|---|---|---|---|
| `AR_7_Ret_180` SST (validation control) | 4,652 | 325 | 5.4 |
| `AR_7_Ret_180` QCR (validation) | 4,660 | 308 | 5.1 |
| `AR_1_Ret_360` QCR | 395 | 9 | 0.2 |
| `AR_3_Ret_360` QCR | 1,956 | 85 | 1.4 |
| `AR_14_Ret_180` QCR | 8,947 | 1,490 | 24.8 |
| **solver total** | | **2,217** | **37.0** |

Against the item's 95 core-min budget (host-side evaluation, figure and CSV
scripts ran minutes at ≤ 2 cores and made no solver calls). The
weekly-limit kill of 2026-08-05T17:45Z landed *after* both validation arms
had converged and written; the run directory survived intact and the test
arms were run on resume 2026-08-07 under the unchanged frozen rule —
pre-registration-first made the recovery exactly as cheap as the doctrine
says it should be.

Artifacts: `closure_challenge_submission_round5/test/` (8 CSVs, hashes in
§3), `closure_challenge_round5_qcr_forward.json` (machine record),
`R5_validation_AR7.json`, `R5_RULE_FREEZE.md` (@ `0bade54a`),
`duct_secondary_flow_AR_7_validation_qcr.png`, run tree
`/home/ubuntu/certonomous-runs/w3-qcr-rank1/` (per-arm `log.simpleFoam`,
converged fields, `ledger.txt`).

*Nothing below this line existed when this file was committed; the round-5
per-case table does not exist yet, and producing it is the supervisor's
call.*

**Dated citation note, 2026-08-08 (Ladder V rung V5; additive only, no
frozen clause touched):** the QCR2000 term this record names throughout is
Spalart, P. R., "Strategies for turbulence modelling and simulations,"
*Int. J. Heat Fluid Flow* **21**(3), 252–263 (2000); `Ccr1 = 0.3` is that
paper's published constant, adopted untouched.
