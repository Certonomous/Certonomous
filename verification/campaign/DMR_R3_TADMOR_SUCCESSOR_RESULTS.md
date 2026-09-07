# DMR TADMOR-FLUX SUCCESSOR — RUN RESULTS

> **This is a NEW results record. It does NOT edit the frozen pre-registration
> body** (`DMR_R3_TADMOR_SUCCESSOR_PREREGISTRATION.md`, freeze `ee544f1d`;
> pre-compute STEP-0 repair amendment `e29812e7`, parallel v2 driver committed
> `5d6856ab` — commit shas as relayed by the cfd supervisor). Frozen files are
> never edited (CLAUDE.md rule 6); the verdict below was graded by the frozen
> instruments and is transcribed here, not re-decided.
>
> Authored by cfd `lab-lane`, 2026-09-07, from the cfd supervisor's first-hand
> grading and STEP-0 mechanism read. All figures cite the run artifact they were
> read from; the lane re-verified each cited value at source before recording.

---

## VERDICT — **NOT A RESULT**

Roache rule 5, **clause 1**: the grid-convergence triple is **INCOMPLETE** — the
finest level R3t (N=240) did not complete to `endTime = 0.2` (SIGFPE crash at
t = 0.15006). A triple that is not `CONVERGING` is `NOT A RESULT` whatever the two
completed levels' values are. The gate is not turned; there is no gradeable GCI.

This is a **MEASURED L1 (Tadmor flux) failure**, not a capability finding: the
L2 lever (Courant reduction) is unmeasured, so no capability inference is drawn
from this or the Minmod crash (L-501). Under fix-until-runs the ladder **continues
as a dated successor**; the next rung is on the chief's desk.

---

## LEVELS AS MEASURED

Family: `verification/runs/DMR_R3_TADMOR_SUCCESSOR_runs/`. Single lever vs the
Minmod positivity successor, applied uniformly across all three levels:
`fluxScheme Kurganov;` → `fluxScheme Tadmor;` (§3 of the prereg; proven exactly one
line). Grader `dmr_locator_v2.py` (blob `52aacf96…`, `GATEV_TOL = 0.0231`), reused
unchanged; two-sided planted-zero control run before grading each level.

| level | N | rc | Gate V' | x_measured | error | tol | planted control |
|---|---|---|---|---|---|---|---|
| R1t | 60 | 0 | **PASS** | 3.0112081635118253 | 0.01071392557274553 | 0.0231 | **PASSED** (shift seen, absence refused) |
| R2t | 120 | 0 | **PASS** | 2.9994729945108287 | 0.006195634936619232 | 0.0231 | **PASSED** (shift seen, absence refused) |
| R3t | 240 | 136 | — (crashed) | — | — | 0.0231 | — |

- **R1t / R2t** both `rc=0`, both Gate V' **PASS** inside the byte-identical parent
  tolerance 0.0231. The position error **DECREASES with refinement**
  (0.01071 → 0.00620) — the two completed levels are converging. Cited:
  `R1t/locator_result.json`, `R2t/locator_result.json` (`PASS: true`,
  `planted_control: "PASSED (shift seen, absence refused)"`).
- **R3t** (`rhoCentralFoam`): **rc=136 SIGFPE (signal 8)**, deepest frame
  `Foam::sqrt(Field<double>&, UList<double> const&)` in `libOpenFOAM.so`. Last
  written `Time = 0.15005683` — the solve did **not** reach t = 0.2. Cited:
  `R3t/log.rhoCentralFoam` (last `Time` line + the signal-8 frame),
  `successor.rc.txt` = 136.

### The Tadmor-vs-Minmod finding (MEASURED partial mitigation)

R3t fails by the **SAME energy-positivity mechanism** as the Minmod positivity
successor (`rhoCentralFoam.C:136`, cell-centre sound-speed/energy positivity), but
**Tadmor DELAYED the collapse**: Minmod crashed at t = 0.11648, Tadmor at
t = 0.15006 — **~29% further in simulation time** (437 s wall for R3t vs 275 s for
the Minmod R3p). Tadmor's more diffusive interface flux is therefore a **measured
PARTIAL mitigation — it delays but does not cure the collapse.** This is a measured
L1 failure of the flux-diffusion lever, reported not softened.

---

## STEP-0 MECHANISM READ (diagnostic probe, answer-blind, L-501)

`verification/runs/DMR_R3_STEP0_DIAG_v2_runs/` — the STEP-0 probe restarts the
Minmod R3p from t = 0.10 with dense per-timestep `fieldMinMax` writes and NO
numerics change, and reads which physical field first goes negative and where.
Reader `step0_negativity_reader.py`; two-sided planted-zero control PASSED (`rc=0`).
The probe ran to the expected SIGFPE at t ≈ 0.116.

**FIRST NEGATIVE: internal energy `e = -743.589283` at t = 0.10002811** (first
post-restart step), location **(1.86458333, 0.235416667, 0.005)** — the post-shock
near-wall zone. At the crash step (t ≈ 0.11646) `p` is also negative
(min `-0.146691842`) while `rho` stays strictly positive (min 1.40000504). Cited:
`STEP0/step0_negativity_result.json` (`first_negative.field = "e"`,
`mechanism_note: "rhoCentralFoam.C:136 cell-centre sound speed (post-update
energy/positivity failure)"`).

**Mechanism = cell-centre energy-positivity failure** (`rhoCentralFoam.C:136`), a
CELL-CENTRE fault, NOT a face-only reconstruction undershoot. This is why a more
diffusive flux scheme delays but cannot cure it: the negative energy is produced at
the cell centre after the update, downstream of the interface flux. The relevant
next levers are therefore Courant reduction (L2/L3) or a bounded-energy solver
build (L5) — not further flux-scheme diffusion.

---

## COST (rule 12) — MEASURED

- **STEP-0 diagnostic:** 3.33 core-min (200 core-s = 50 s wall × 4 ranks, from
  `PROGRESS.txt`) of the 5 core-min probe cap — no breach. **Infrastructure
  bookkeeping artifact flagged:** `step0.coresec.txt` reads **0** because the
  `step()` `USED_CORESEC` increment ran in a command-substitution subshell and did
  not propagate to the parent; the AUTHORITATIVE cost is the 3.33 core-min from
  `PROGRESS.txt` (wall × ranks). "Bookkeeping never voids physics" — the run and its
  measurement stand; the coresec-file=0 must not be mistaken for a zero-cost run.
- **L1 Tadmor family:** total **35.33 core-min** (2120 core-s cumulative from
  `PROGRESS.txt`) of the 60 core-min family cap — **NO cap breach; the run stopped
  on the R3t SIGFPE, not on the cap.** R3t's own `rhoCentralFoam` solve = 29.1
  core-min (437 s × 4 ranks), **crash-truncated** (SIGFPE at t = 0.15 before
  completing to t = 0.2) — the finest level never spent its full budget, so the
  underspend against the 38 core-min estimate is NOT a favourable misprediction.

Dollars are **DERIVED, NOT MEASURED** (c7a.4xlarge $0.0513/core-h, reported-by-owner;
the box cannot read its own billing — `COMPUTE_BUDGET_CHARTER.md` §5). Rule-12
calibration rows filed in `docs/COST_CALIBRATION.md`.

---

## WHAT THIS SETTLES, AND WHAT IT DOES NOT

- **Settled (measured):** the Tadmor flux lever, uniform at maxCo 0.1, does NOT
  carry the DMR to t = 0.2 at N = 240 — it delays the energy-positivity collapse
  by ~29% in sim-time but does not prevent it; the first-negative field is internal
  energy at a cell centre (`rhoCentralFoam.C:136`).
- **NOT settled:** capability exhaustion — that requires the full measured lever
  chain (L2 Courant reduction, L3 combined, L5 bounded-energy) which is unmeasured.
  No capability finding is drawn from L1 (L-501).

**Ladder continues** as a dated successor; the next rung (L2/L3 Courant reduction or
L5 bounded-energy solver build) is on the chief's desk.

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). This record does
not alter any gate, threshold, band, cap or label of the frozen pre-registration.**
