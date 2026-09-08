# DMR R3 L5 — BOUNDED-T (bounded-energy clip) SUCCESSOR — RUN RESULTS

> **This is a NEW results record. It does NOT edit the frozen pre-registration
> body** (`DMR_R3_L5_BOUNDED_T_PREREGISTRATION.md`, freeze `26823d9f`
> "cfd DMR-R3 L5 BOUNDED-T: FREEZE pre-registration (banner + grading-path
> freeze stamp only)" — commit sha as relayed by the cfd supervisor and
> re-verified on disk by this lane). Frozen files are never edited (CLAUDE.md
> rule 6); the verdict below was DIAGNOSED by the cfd supervisor first-hand
> (personal §3 crash-triage / big-claim call) and is **transcribed here, not
> re-decided.**
>
> Authored by cfd `lab-lane`, 2026-09-08, from the cfd supervisor's first-hand
> triage of the run artifacts under
> `verification/runs/DMR_R3_L5_BOUNDED_T_runs/`. Every figure cites the run
> artifact it was read from; this lane re-verified each cited value at source
> before recording.
>
> **PRESERVATION NOTE (path resolution).** After this record was written the run
> directory was renamed to preserve the failed attempt and leave the L5b root
> absent (M6/RUNG1 precedent): every citation below of the form
> `verification/runs/DMR_R3_L5_BOUNDED_T_runs/…` now resolves at
> **`verification/runs/DMR_R3_L5_BOUNDED_T_runs.MISCALIBRATED_CLIP_eref_PRESERVED/…`**.
> The artifacts (R3 log 32,620,116 bytes, `PROGRESS.txt`, `CAP_BREACH.txt`,
> `R{1,2,3}/…`, `R3/0/T`) are byte-intact at the preserved path; only the parent
> directory name changed.

---

## VERDICT — **NOT A RESULT**

Roache rule 5. Two independent, mutually reinforcing grounds:

1. **The grid-convergence triple is INCOMPLETE.** The finest level **R3 (N=240)
   did not complete to `endTime = 0.2`** — the run was **cap-stopped at
   `Time = 0.19032384`** (`R3/log.rhoCentralFoamBoundedDMR`, last `Time` line),
   short of `endTime 0.2`, when the ONE registered 100-core-min family cap was
   breached. `successor.rc.txt = 9` (the wrapper's CAP_BREACH code); the R3
   solver step itself was killed at its cap slice with step
   `rc = 124` (`R3/RC_rhoCentralFoamBoundedDMR.txt`,
   `PROGRESS.txt` line 23). `CAP_BREACH.txt`: *"6001s core-seconds > 6000
   (100.0 core-min total) — L5 BOUNDED-T SUCCESSOR STOPPED at level 'R3' step
   'rhoCentralFoamBoundedDMR (timeout at its cap slice)', no new budget."* A
   triple that is not `CONVERGING` is `NOT A RESULT` whatever its levels' values.

2. **The whole triple is corrupted by a miscalibrated clip** (root cause below).
   The bounded-energy clip fired on **100 % of cells from the very first
   timestep at every resolution**, so R1 and R2 — which did reach `endTime 0.2`
   — did so on a solution corrupted from `t ≈ 1.2e-06`. Their Gate V' is
   therefore meaningless, and both in fact report **`PASS = false`** on garbage
   shock positions (`R1/locator_result.json`, `R2/locator_result.json`).

**The gate turns nothing here.** A `NOT A RESULT` stands on the incomplete,
corrupted triple; the gate can only turn a PASS/GATE FAIL *into* NOT A RESULT,
never the reverse (rule 5). There is no gradeable Gate T' and no quotable GCI.

**This is a MISCALIBRATED-CLIP BUG — NOT a physics divergence and NOT a
capability finding.** The bounded-clip lever **never got a fair test**: the
instrument (the `eMin_bound` floor) was mis-set relative to OpenFOAM's actual
internal-energy representation and clipped the physical field on the first
timestep, so the run measures the instrument defect, not the lever. No
capability inference is drawn from a miscalibrated instrument (**L-501**).
DMR-R3 continues via **L5b**, a correctly-calibrated re-run.

---

## LEVELS AS MEASURED

Family: `verification/runs/DMR_R3_L5_BOUNDED_T_runs/`. Lever vs the L4 successor:
the `rhoCentralFoamBoundedDMR` solver adds a per-step element-wise
`e = min(max(e, eMin_bound), eMax_bound)` bounded-energy clip after the
`e = rhoE/rho - 0.5*magSqr(U)` reconstruction (prereg §2.2), with
`eMin_bound = -532.4097 J/kg` derived from the DMR constants (prereg §2.3).

| level | N | grid | last Time | reached endTime 0.2? | step rc | Gate V' PASS | x_measured | error (cells) | clip fired, first step |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 60 | 240×60 | 0.2 | yes (on corrupted field) | 0 | **false** | 2.6740847469914453 | −0.3264 (−19.58) | **14 400 / 14 400 (100 %)** |
| R2 | 120 | 480×120 | 0.2 | yes (on corrupted field) | 0 | **false** | 2.7094696016011737 | −0.2838 (−34.06) | **57 600 / 57 600 (100 %)** |
| R3 | 240 | 960×240 | **0.19032384** | **NO — cap-stopped** | 124 (→ wrapper rc 9) | — (never graded) | — | — | **230 400 / 230 400 (100 %)** |

- **R1 / R2** both `rc = 0` and reach `endTime 0.2`, but both fail Gate V' —
  the shock position is garbage (R1 error −0.3264 ≈ −19.6 cells; R2 error
  −0.2838 ≈ −34.1 cells), the corruption signature. Cited:
  `R1/locator_result.json` (`"PASS": false`, `"error": -0.3264094909476345`,
  `"x_measured": 2.6740847469914453`, `"planted_control": "PASSED (shift seen,
  absence refused)"`), `R2/locator_result.json` (`"PASS": false`,
  `"error": -0.2838...`, `"x_measured": 2.7094696016011737`).
- **R3** cap-stopped at `Time = 0.19032384` (`R3/log.rhoCentralFoamBoundedDMR`),
  never graded (`R3/locator_result.json` absent). `PROGRESS.txt` line 23:
  `[R3/rhoCentralFoamBoundedDMR] rc=124 wall=1322s ranks=4 used=6001core-s`.

---

## ROOT CAUSE — MISCALIBRATED CLIP (`eMin_bound` above the physical `e` field)

### The byte-identical-worst-`e` smoking gun

At the **first timestep**, `Time = 1.199976e-06`, the clip's per-fire diagnostic
records the SAME `global worst e = -743.58928 J/kg` at ALL THREE resolutions,
against `eMin_bound = -532.4097`:

- R1: `BOUND: e below eMin in 14400 cell(s) at Time = 1.199976e-06, global worst
  e = -743.58928 J/kg (eMin_bound = -532.4097)` — `R1/log.rhoCentralFoamBoundedDMR`.
- R2: `... in 57600 cell(s) ... worst e = -743.58928 J/kg ...` —
  `R2/log.rhoCentralFoamBoundedDMR`.
- R3: `... in 230400 cell(s) ... worst e = -743.58928 J/kg ...` —
  `R3/log.rhoCentralFoamBoundedDMR`.

A worst-`e` value that is **byte-identical across three independent grids** (and
whose fired-cell count is exactly the full cell count of each grid: 14 400,
57 600, 230 400) **cannot be a flow feature** — a shock or wall-foot event would
differ resolution-to-resolution. It is a **thermo-reference constant**: the clip
is comparing the ambient field against a floor that sits above the ambient field
itself.

### The `e`-reference mismatch

- **OpenFOAM's actual `hConst sensibleInternalEnergy`** assigns `e ≈ -743.6 J/kg`
  to the physical ambient field. The physical field IS ambient nearly
  everywhere: `R3/0/T` has `min = 1.0` (ambient) across **204 173 of 230 400
  cells** and `max = 20.3875` (post-shock) — read directly from `R3/0/T`
  internalField by this lane.
- **The prereg's hand-formula** `e = Cv·(T − 298.15)` (prereg §2.3, with
  `Cv = 1.785717`, `Tref = 298.15`) predicts ambient `e(T=1.0) = 1.785717·(1.0 −
  298.15) = -530.626 J/kg` — **ABOVE** the floor `eMin_bound = -532.410`
  (prereg §2.3 line 195–196 asserts exactly this: *"`eMin_bound` sits just below
  the ambient `e`"*).
- So the prereg set `eMin_bound` just below its **predicted** ambient `e`
  (−530.6), but OpenFOAM's **actual** ambient `e` is ≈ −743.6, which is **far
  below** `eMin_bound = -532.4`. The floor therefore sat **above the entire
  physical `e` field**, and the clip **floored every physical cell** on the first
  timestep — at all three resolutions.

The corrupted field then energy-pumps: by `t ≈ 0.19`, R3's worst clipped `e` has
grown to `-49485.38 J/kg` in 176 498 cells
(`R3/log.rhoCentralFoamBoundedDMR`, last `BOUND` line at `Time = 0.19031718`),
consistent with the supervisor's ≈ −49,475 figure — the clip does not stabilise
the field, it corrupts and then drives it.

### Honest note (supervisor-disclosed, not hidden)

The supervisor's own §3 check-1 verified the frozen driver's clip arithmetic
matched the prereg's stated formula — but did **not** verify that the prereg's
`e`-formula (`e = Cv·(T − 298.15)`) matched OpenFOAM's actual `hConst`
internal-energy representation. That gap is exactly the bug: the arithmetic was
faithfully implemented; the reference the arithmetic was calibrated against was
wrong. Disclosed here, not concealed.

---

## COST (rule 12) — MEASURED

- **L5 family total: 100.02 core-min** (6001 core-s from `CAP_BREACH.txt` /
  `PROGRESS.txt` line 23, `used=6001core-s`) against the **ONE registered hard
  cap of 100 core-min** (frozen prereg `26823d9f` §6b) — a **CAP BREACH**: the
  run was **stopped on the cap**, not on completion, and got no new budget
  (rule 12). Per-level advisory watermarks (§6b, not caps): **R1 1.500 core-min**
  (`R1.coresec.txt` = 90 cumulative; `PROGRESS.txt` line 9), **R2 9.866 core-min**
  (`R2.coresec.txt` = 592 cumulative; line 18), **R3 the balance to 6001 core-s**,
  a PARTIAL solve killed at its cap slice (`wall=1322s ranks=4`; line 23).
- **§6b family point estimate 40 core-min**; measured 100.02 core-min gives
  ratio **2.50** — but this is a **MISCALIBRATED-INSTRUMENT CAP-BREACH**, NOT a
  completion misprediction and NOT waste in the ordinary sense
  (`COMPUTE_BUDGET_CHARTER.md` §6). The run never executed the intended physics:
  the clip corrupted the field on the first timestep, so the compute measured the
  instrument defect, not the model, the lever, or the estimate. The estimate is
  therefore neither credited nor faulted by the ratio. The rule-12 calibration
  row is filed in `docs/COST_CALIBRATION.md`.

Dollars are **DERIVED, NOT MEASURED** — 100.02 core-min = 1.667 core-h at
$0.0513/core-h (c7a.4xlarge, reported-by-owner; the box cannot read its own
billing — `COMPUTE_BUDGET_CHARTER.md` §5) = **$0.0855 DERIVED**.

---

## WHAT THIS SETTLES, AND WHAT IT DOES NOT

- **Settled (measured):** the bounded-energy clip **as calibrated in the frozen
  L5 prereg** (`eMin_bound = -532.4097`, derived from `e = Cv·(T − 298.15)`)
  **corrupts the DMR field** — because that floor sits ABOVE OpenFOAM's actual
  `hConst` ambient `e ≈ -743.6`, the clip fires on 100 % of cells from the first
  timestep at all three resolutions and energy-pumps the field. The byte-identical
  worst-`e` across grids proves this is a thermo-reference artefact, not physics.
- **NOT settled:** the **capability** of a bounded-energy clip to carry the DMR to
  t = 0.2 at N = 240. The lever never got a fair test — the instrument was
  miscalibrated. No capability finding is drawn from a miscalibrated instrument
  (**L-501**). The fair test is **L5b**, a re-run with `eMin_bound` calibrated
  against OpenFOAM's actual `hConst` `e`-representation (not the hand-formula).

**Ladder continues** via the correctly-calibrated **L5b** successor. The
miscalibrated L5 run is preserved (renamed) so the L5b root is absent, matching
the M6/RUNG1 preserved-attempt precedent.

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). This record
does not alter any gate, threshold, band, cap or label of the frozen
pre-registration. No tolerance was widened.**
