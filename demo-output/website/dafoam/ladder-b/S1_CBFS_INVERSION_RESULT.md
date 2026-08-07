# S1 — the CBFS field inversion ran, the machinery worked, and the loss it minimized was measuring the wrong thing

Date: 2026-08-04 to 2026-08-07 (UTC), three session kills spanned and survived
(section 8). Item `s1-cbfs-field-inversion-run` (proposal filed with the
pre-registration, commit e6321e95; amendment 9040fc4d). Pre-registration:
`S1_CBFS_INVERSION_PREREGISTRATION.md` — loss, bounds, optimizer, caps, both gates and
the production-term label all committed before any iteration ran. Evidence:
`/home/ubuntu/certonomous-runs/S1-cbfs-inversion/` (driver, per-eval logs, `ledger.csv`,
`J_history_main.csv`, beta checkpoints, reconstructed final fields at `cbfs_inv/1563/`).
**Total cost: 335.98 core-min against the 600 hard cap.**

## Headline, in the order the evidence forces

1. **The inversion machinery works end to end — first actual field inversion on a
   closure-relevant case in this lab.** 17 evaluations, every adjoint converged
   (reason 2, 667 iters, every eval log), 10 accepted L-BFGS-B iterations, monotone
   descent of the accepted objective, gradient norm down **106x** (9.528e-4 → 9.011e-6),
   zero cells pinned at either bound. The eval-1 control reproduced the W4 baseline
   objective to all 17 digits and the W4 archived gradient **bit-identically**
   (max abs diff exactly 0).
2. **Both pre-registered gates FAIL.** G1: the normalized QoI term fell to **0.99851**
   against the ≤0.70 bar — a **0.149%** reduction. G2: 29.0% of the top-decile
   |beta−1| cells sit in the declared separated-flow window against the >50% bar.
   Recorded as failed gates, no softening.
3. **The primary cause is an objective defect, found by the post-run coverage audit:
   the case's inlet boundary condition is not the benchmark's inlet.** Our `0/U`
   carries **Ux = 0.72 uniform on all 150 inlet faces**; the benchmark's own CBFS case
   ships a developed profile (0.202 → 1.005, bulk mean **0.9149**). The Uz noise
   columns of the two files are **identical**, which pins the mechanism: the file is
   the benchmark's, with Ux/Uy overwritten — the leftover write-back of B3's
   patchVelocity pilot (magnitude 0.72, angle 0). The varianceU loss therefore compares
   a 0.72-bulk RANS flow against a 0.915-bulk LES reference: a **27% mass-flux
   mismatch no interior turbulence correction can remove**. 85.1% of the total loss
   sits at y > 2, far above the step, in what should be trivially matched channel flow;
   the physics window the inversion exists for holds only **3.7%** of the loss.
   The optimizer honestly minimized the loss it was given; the loss was measuring the
   inlet, not the closure.
4. **W4's record is corrected on one sentence** (§5c: "the case's real nonuniform inlet
   is thereby restored rather than overridden"). The beta DV indeed stopped overwriting
   the inlet each iteration, but the on-disk `0/U` it inherited had already been
   overwritten by the patchV pilot. Nonuniform-in-Uz-noise passed for nonuniform.
   Correction addendum filed in `W4_ADJOINT_PC_UNBLOCK.md`. W4's gate is unaffected:
   FD-vs-adjoint agreement is a property of the objective as built, and it stands.
5. **A second real defect, measured on the way in (Amendment 1):** DAFoam's primal
   restarted in-process from its own converged state **walks away from it** (p residual
   1e-6 → 0.21, omega/k pinned at their 1e-16 floors, varianceU +10.9%), prints
   "Primal solution failed!" — and proceeds into the adjoint anyway, which then
   stagnates flat (reason −3). In-process multi-evaluation optimization is structurally
   unavailable on this case; the loop ran out-of-process (fresh container per
   evaluation, the FD-protocol shape) at the same 16.4 core-min the cost model already
   stated.

## 1. What ran

Pre-registered configuration, as amended: host-side SciPy L-BFGS-B (maxcor 10, maxls 8,
ftol 1e-10, gtol 1e-6, bounds [0.2, 4.0]), each evaluation one fresh
`dafoam-subpclu:v1` container (`DAFOAM_SUBPC_TYPE=lu`, 4 ranks, `--cpus=2` per the
concurrency instruction, `sudo rm -rf processor*` cold reset, cold start from `0/`),
J = 65.448 · varianceU + 1e-4 · Σ(beta−1)², beta on the SST omega **production** term
(`betaFIOmega`, 21,000 DVs). **Production-term-labeled: nothing here is comparable to
Wu/Zhang's destruction-term numbers, per the pre-registration and the C2/R6 rulings.**

## 2. Trajectory (J_history_main.csv, complete)

| eval | varianceU | J_qoi (norm.) | penalty | J | beta min/max | ‖g‖₂ |
|---|---|---|---|---|---|---|
| 1 (control) | 1.5279278906359758e-02 | 1.00000000 | 0 | 1.00000000 | 1.000/1.000 | 9.528e-04 |
| 3 | 1.5263334215e-02 | 0.99895645 | 3.083e-04 | 0.99926474 | 0.780/1.077 | 6.457e-04 |
| 6 | 1.5256283994e-02 | 0.99849503 | 5.887e-04 | 0.99908377 | 0.719/1.139 | 6.193e-05 |
| 11 | 1.5256460644e-02 | 0.99850659 | 5.724e-04 | 0.99907903 | 0.735/1.145 | 9.581e-06 |
| 16 | 1.5256460061e-02 | 0.99850655 | 5.725e-04 | 0.99907903 | 0.735/1.145 | 9.011e-06 |

Evals 11–17 agree in J to seven digits. **The run was stopped by decision at the
plateau after 17 evaluations, not by the optimizer's own test and not by the budget
cap** — recorded as such (charter §4: a stop is named for what it is). The final-state
control (fresh cold process at `beta_final`, §6 of the prereg) reproduced
varianceU = 1.5256460061195715e-02, matching eval 16 to all digits, and wrote the
fields the audit below reads (`cbfs_inv/1563/`, cell centres from
`postProcess -parallel writeCellCentres`, the field-vs-DV check confirming the written
field is a permutation of the DV vector — sorted max diff 5.1e-15).

## 3. Gate verdicts

| act | gate | measured | verdict |
|---|---|---|---|
| S1 CBFS inversion | G1: J_qoi ≤ 0.70 within budget | 0.99851 (−0.149%) | **GATE FAIL** |
| S1 CBFS inversion | G2: >50% of top-decile \|beta−1\| in window 0≤x/h≤6, 0≤y/h≤2 | 29.0% (3.45x the 8.4% all-cells base rate, but under the bar) | **GATE FAIL** |
| eval-1 control | reproduce W4 baseline + gradient | bit-identical, grad diff 0.0 | PASS |
| final-state control | cold reproduction of final J | all-digits match | PASS |

Reported with no gate attached, per the prereg: 0 cells at either bound; penalty =
0.057% of the post-optimization QoI error (their tuning convention wanted 10–20%; the
deviations stayed too small for the pre-declared lambda_L2 to reach that band);
qualitative sign expectation held — 68.6% of the top-decile cells moved **below** 1,
the nu_t-raising direction, the production-term mirror of Wu/Zhang's beta>1 on
destruction.

## 4. The diagnosis, ranked by the evidence in hand

**(1) PRIMARY — the objective is defective: the loss floor is an inlet mismatch, not a
closure error.** Measured on the reconstructed final fields against `0/UData`:

- Inlet-adjacent column (x<−7): RANS bulk Ux **0.7194**, LES reference bulk **0.9153**
  (ratio 1.272). The case's inlet file: Ux = 0.72 uniform × 150 faces; the benchmark's
  own: bulk 0.9149, profile 0.202→1.005. Identical Uz noise columns prove ours is the
  benchmark file with Ux/Uy overwritten (the patchV pilot's write-back).
- Error distribution: y>2 carries **85.1%** of the total Σ|U−UData|²; the pre-declared
  physics window carries **3.7%**; near-wall y<0.5 carries 1.4%. The free-channel bands
  (y 2–7) show a near-uniform RANS-vs-reference offset of 0.27 — mass conservation at
  work, not turbulence modeling.
- Consequence arithmetic: the FD-verified gradient is the true derivative of this loss,
  and along it a first-order 30% reduction would need a step of norm ~315 in beta-space
  (rms 2.2 per cell) — outside any physical bound. The 0.149% plateau is the honest
  optimum of the wrong loss.

**(2) SECONDARY — the stationary point is a penalty balance.** At the plateau
|g_penalty|/|g_QoI| = **0.998** with cos(g_QoI, −g_penalty) = **0.9995**: the optimizer
stopped exactly where the pre-declared per-cell L2 pull to 1 cancels the (tiny) QoI
gradient, pinning rms|beta−1| at 0.0165. A plain L2-to-1 prior with no
smoothness/TV term also lets the deviation scatter cell-by-cell instead of forming
coherent regions — visible in the top-decile map (28.9% of it hugs y<0.5 wall cells
against an 8.0% base rate). With the loss floor removed, the same balance would land
elsewhere; lambda_L2 re-tuning belongs to the re-run, disclosed in advance there.

**(3) CONTRIBUTING — the SST shear-stress limiter bypasses beta where beta most wants
to act.** Zero-compute mask on the written fields (nut < k/omega ⇔ the F23·S > a1·omega
branch is active): the limiter binds on 7.7% of all cells — but on **49.5%** of the
top-decile |beta−1| cells (6.4x enrichment) and 18.7% of the physics window. Where it
binds, nu_t = a1·k/(F23·S) and the omega-production lever reaches nu_t only weakly.
This is the Dow-style parameterization argument made measurable: a beta on omega
production is a structurally weak handle in exactly the separated-shear-layer cells
that matter. Real, but subordinate to (1) — it bounds what a repaired objective can
recover through this hook, it does not explain the 0.9985 floor.

**(4) UNRESOLVED BY THIS RUN — production vs destruction term.** The pre-registered
label stands, but this run cannot rank the term choice as a cause: the objective defect
masks it. What this run does establish is that the `w3-beta-on-omega-destruction-model-patch`
**alone would not have changed this outcome** — the destruction hook would have chased
the same inlet mismatch. The patch remains the term-parity item, after the objective is
repaired.

## 5. What survives this run

- The verified adjoint capability is untouched and got 17 more converged solves on the
  record, plus a bit-identical independent gradient reproduction.
- The out-of-process inversion driver (fresh-container evaluations, per-eval
  checkpoints, ledger, budget guard) is built, exercised, and survived three session
  kills with zero lost work — it is the template for the re-run.
- Two named defects with primary evidence: the inlet overwrite (this document,
  benchmark file vs ours) and the primal-restart walk-off with the failed-primal
  adjoint proceeding anyway (Amendment 1, `log.calib` lines 29935–29991).
- A measured limiter-overlap number (49.5%/7.7%) that any future beta-on-production
  plan has to price in.

**For Stage 2:** nothing from this beta field may train a beta(features) model — the
field is an artifact of a defective loss. Stage 2 stays blocked pending the objective
repair and re-inversion.

## 6. Follow-up filed

`s1-cbfs-objective-repair-and-reinversion` (proposed, not self-approved): restore the
benchmark's own inlet profile to the case (the file is on disk in the clone), re-verify
the FD gate at one cell under the corrected objective, re-baseline varianceU (the floor
should collapse — the prediction is on the record before the run), then re-run this
driver unchanged. Wu/Zhang-style sparse points in the separation region as the loss
variant, lambda_L2 re-tuned and disclosed. The destruction-term patch (w3, spec ready in
`W2_WU_ZHANG_DESTRUCTION_FIML_READING.md` §5) is the term-parity follow-on after that;
a Dow-style nu_t-discrepancy parameterization is the named alternative if the limiter
overlap proves to cap the production hook's reach.

## 7. Ledger

| stage | core-min |
|---|---|
| in-process calibration (bought Amendment 1's defect, 2026-08-04) | 31.07 |
| evaluations 1–17 (fresh-container compute_totals, --cpus=2) | 298.71 |
| eval 18, stopped by decision 36 s in | 1.20 |
| final-state cold control + field/centres write-out | 5.00 |
| **total vs 600 hard cap** | **335.98** |

Post-processing (coverage audit, masks, G2) was host-side arithmetic on written fields,
zero solver compute. Every entry opens to START/END epochs in `ledger.csv`.

## 8. Continuity note

Three kills spanned this item: 2026-08-04 ~18:46Z (session limit, mid-calibration — the
detached run completed and checkpointed unattended), 2026-08-05 ~15:08Z (harness death —
the setsid driver kept stepping through it), 2026-08-05 ~17:45Z (weekly limit plus a
box power-cycle; resumed 2026-08-07 with only the in-flight coverage-audit command
lost). Pre-registration-first plus out-of-process execution plus per-eval checkpoints
made every recovery a file read. That doctrine is now load-tested.

## Related

- `S1_CBFS_INVERSION_PREREGISTRATION.md` (e6321e95; Amendment 1, 9040fc4d)
- `W4_ADJOINT_PC_UNBLOCK.md` (capability; §5c correction addendum dated 2026-08-07)
- `VERIFICATION_cbfs_unblock_supervisor_sweep.md` (independent gradient, cell 6490)
- `W2_WU_ZHANG_DESTRUCTION_FIML_READING.md` (the reproduction target and the w3 spec)
- `S1_FIML_FIELD_INVERSION.md` (Stage 1 lineage and the R6 restatement)
