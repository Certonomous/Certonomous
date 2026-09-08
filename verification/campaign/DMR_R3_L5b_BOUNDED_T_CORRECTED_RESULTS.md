# DMR R3 L5b — BOUNDED-T CORRECTED (field-anchored positivity clip) SUCCESSOR — RUN RESULTS

> **This is a NEW results record. It does NOT edit the frozen pre-registration
> body** (`DMR_R3_L5b_BOUNDED_T_CORRECTED_PREREGISTRATION.md`, freeze
> `4745198733a40543d9f203f5ff4758a4065883cb` — `L5B_PREREG_SHA`, commit sha as
> relayed by the cfd supervisor and re-verified on disk by this lane). Frozen
> files are never edited (CLAUDE.md rule 6); the per-level verdicts below were
> produced by the frozen instrument and the triple verdict by the frozen Roache
> arithmetic, and are **transcribed here, not re-decided.**
>
> Authored by cfd `lab-lane`, 2026-09-08, after the cfd supervisor's first-hand
> §3 verification of the per-level facts (all three PASS Gate V', errors monotone
> decreasing, clip localised to ~4 wall-foot cells — a genuine localized cure,
> not L5's mass-clipping). Every figure cites the run artifact it was read from;
> this lane re-verified each cited value at source and re-verified the grader
> identity and the live planted control before recording.

---

## VERDICT — **PASS**

Roache rule 5, worked in order:

1. **All three levels COMPLETE (rule 4 strict completion).** R1 (N=60), R2
   (N=120) and R3 (N=240) each: `rc=0`, exactly one `End` line, last written
   `Time = 0.2 == endTime 0.2`, required fields present at `0.2/`
   (`T U p rho C Cx Cy Cz`), and the age guard satisfied (`0.2/T` newer than the
   case's own `0/T`). No `CAP_BREACH.txt`: the family stopped on **completion**,
   not on the cap (99.35 core-min against the 100 core-min registered cap). **R3
   (N=240) reaching `t = 0.2` at `rc=0` is the FIRST N=240 DMR completion of this
   ladder** — every prior finest level (L2 Courant probe, L4 first-order-T, L5
   miscalibrated clip) crashed or cap-stopped short of `endTime`.
2. **Triple state: CONVERGING.** Roache no-exact self-convergence form (frozen
   DMR triple method §2/§4.3, exact 2:1 nesting) on the located Gate V' incident
   positions: `e32 = |x120 − x60| = 0.011103279`, `e21 = |x240 − x120| =
   0.001450257`, ratio `R = e21/e32 = 0.130615 < 0.95` → **CONVERGING**. The
   located positions are monotone toward exact (3.0097 → 2.9986 → 2.9971) and the
   Gate V' position errors are monotone-decreasing (0.009204 → 0.005318 →
   0.002665), so the triple is monotone and a GCI is quotable (rule 5).
3. **CONVERGING → graded against the band → PASS.** All three Gate V' position
   errors lie inside the byte-identical parent tolerance `0.0231`
   (0.009204 < 0.005318 < 0.002665, all < 0.0231). **Observed order (position-
   difference Roache form) `p = log2(1/R) = 2.937`; `GCI_fine = 1.25·e21/(2^p −
   1) = 2.724e-04`** in shock-position (x) units = **0.0118 % of the 2.30940
   travelled distance**, far inside the 0.0231 band. The physical error-based
   convergence rate (per-interval `log2(e_coarse/e_fine)`) is **0.791 (R1→R2)**
   and **0.997 (R2→R3)** — first-order-ish, degraded from the scheme's formal
   order by the shock discontinuities, exactly the expected DMR behaviour. Both
   diagnostics agree: the triple converges and every level is in band.

**The gate turns nothing adverse here.** The gate can only turn a PASS/GATE FAIL
*into* NOT A RESULT (rule 5); the triple is CONVERGING and complete, so the PASS
stands. There is a gradeable Gate T' and a quotable GCI.

**This is fix-until-runs SUCCESS, NOT a capability finding.** A correctly-
calibrated bounded-energy positivity-preserving solver
(`rhoCentralFoamBoundedDMRb`) carries the Mach-10 DMR to `t = 0.2` at `N = 240`
with a converging, in-band triple. This settles that **OpenFOAM v2606 CAN carry
this DMR with a positivity-preserving energy update** — it is not a statement
that the vanilla numerics cannot; it is a positive capability result for the
augmented solver.

---

## LEVELS AS MEASURED

Family: `verification/runs/DMR_R3_L5b_BOUNDED_T_runs/`. The ONE lever vs the L5
solver, applied uniformly across all three levels: the field-anchored floor
`eMin_bound = e_min_initial − Cv·(T_min_initial − TMin)` (no assumed
`Tref`/`eref`) plus the mandatory `t=0` zero-clip startup assertion (prereg §1).
All L4/L5 numerics (Tadmor flux, `maxCo 0.1`, Euler ddt, `reconstruct(rho)
Minmod`, `reconstruct(U) MinmodV`, `reconstruct(T) upwind`, BCs, states, thermo,
mesh, writes, 4-rank layout) are byte-identical.

Grader `dmr_locator_v2.py` (**blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`**,
`GATEV_TOL = 0.0231` at `:69`), re-hashed on disk == `HEAD:` by this lane before
recording; reused unchanged (rule 6). Two-sided planted-zero control (rule 3) run
before every per-level number.

| level | N | grid | rc | last Time | endTime 0.2? | Gate V' | x_measured | error | tol | PASS | planted control |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 60 | 240×60 | 0 | 0.2 | yes | — | 3.009698606595904 | **0.009204368656824169** | 0.0231 | **PASS** | **PASSED** (shift seen, absence refused) |
| R2 | 120 | 480×120 | 0 | 0.2 | yes | — | 2.998595327522941 | **0.005317967948731628** | 0.0231 | **PASS** | **PASSED** (shift seen, absence refused) |
| R3 | 240 | 960×240 | 0 | **0.2** | **yes — FIRST N=240 completion** | — | 2.9971450707826204 | **0.0026648981475987377** | 0.0231 | **PASS** | **PASSED** (shift seen, absence refused) |

- Per-level cited: `R1/locator_result.json`, `R2/locator_result.json`,
  `R3/locator_result.json` (each `"PASS": true`, `"planted_control": "PASSED
  (shift seen, absence refused)"`, `"control": "two-sided, run before grading"`).
- Completion cited per level: `R{1,2,3}/log.rhoCentralFoamBoundedDMRb` (one `End`
  line; last `Time = 0.2`), `R{1,2,3}/RC_rhoCentralFoamBoundedDMRb.txt` = 0,
  `R{1,2,3}/system/controlDict` (`endTime 0.2`), `R{1,2,3}/0.2/` field listing,
  `successor.rc.txt` = 0. No `CAP_BREACH.txt` on disk.
- **Planted-zero control (rule 3)** additionally re-confirmed live by this lane
  with the pinned grader's `--selfcheck`: on both reference rungs the planted
  integer-cell shift is SEEN exactly (`0.116666667` / `0.058333333`), the planted
  absence is REFUSED, and the regression reproduces the recorded Gate V positions
  to `|delta| = 0.000e+00` — `SELFCHECK: PASS — controls live and instrument
  unchanged`.

### The grid-convergence triple (Gate T') — CONVERGING

| quantity | value | source |
|---|---|---|
| `e32 = |x120 − x60|` | 0.011103279 | R1/R2 `locator_result.json` |
| `e21 = |x240 − x120|` | 0.001450257 | R2/R3 `locator_result.json` |
| `R = e21/e32` | **0.130615** (`< 0.95` → **CONVERGING**) | derived |
| observed order `p = log2(1/R)` | **2.937** | derived |
| `GCI_fine = 1.25·e21/(2^p − 1)` | **2.724e-04** (x-units) = **0.0118 % of travel 2.30940** | derived, Fs=1.25 |
| error-based per-interval order | **0.791** (R1→R2), **0.997** (R2→R3) | derived from the tabled errors |

The triple is monotone (positions and errors both), CONVERGING, and every level
in band — so the GCI is quotable and the family PASSES.

---

## THE CLIP — HONEST CHARACTERIZATION: a LOCALIZED positivity cure, not L5's mass-clip

This is the distinction between L5 (NOT A RESULT, miscalibrated) and L5b (PASS,
correctly calibrated), and it is the record's real content.

- **`t=0` calibration held (the guard that would have caught L5).** The mandatory
  startup zero-clip assertion PASSED: **0 cells clip at `t=0`** on the physical
  initial field, at all three resolutions — the floor `eMin_bound = -745.35714`
  (R3, `R3/log.rhoCentralFoamBoundedDMRb`) is anchored on the measured field min
  and sits *below* the physical `e`, so it is inert on the ambient field by
  construction. (L5's floor `-532.4097` sat *above* OpenFOAM's actual ambient
  `e ≈ -743.6` and clipped 100 % of cells from the first step — the L5 defect.)
- **R1 and R2: the clip NEVER fires.** `grep -c "BOUND:"` = **0** on both
  `R1/log.rhoCentralFoamBoundedDMRb` and `R2/log.rhoCentralFoamBoundedDMRb`. At
  N=60 and N=120 the solver is bit-for-bit the vanilla positivity-preserving path
  with an inert safeguard — which is exactly why R1/R2's Gate V' errors are
  identical to the L4 first-order-T successor's R1/R2 (0.009204368656824169 and
  0.005317967948731628): same numerics, clip never engaged.
- **R3 (N=240): the clip fires, but ONLY on ~4 cells at the reflecting-wall
  foot.** `R3/log.rhoCentralFoamBoundedDMRb`: **2270 `BOUND:` fire lines over
  9629 time steps**; the **maximum cells clipped in any single fire is 4**; the
  worst (most negative) reported `e` is **-947.21409 J/kg** against the floor
  **-745.35714 J/kg**. This is a **localized positivity safeguard** at the exact
  location where every prior finest level crashed (the reflecting-wall-foot
  T-positivity collapse, `Foam::sqrt` of a negative argument). It is
  **NON-conservative on those ~4 wall-foot cells only** — orders of magnitude
  from L5's mass-clipping of every cell.
- **The ~4-cell non-conservation did NOT corrupt shock-position accuracy.** The
  proof is the triple itself: the Gate V' incident-shock position errors are
  monotone-decreasing and all inside `0.0231` (0.009204 → 0.005318 → 0.002665),
  and the triple is CONVERGING. A clip that corrupted the field would displace
  the shock and blow the band (L5's R1/R2 read errors of −0.33 / −0.28, ≈ −20 to
  −34 cells, `PASS=false`). The localized clip is inert on the ambient field,
  bounds a 4-cell wall-foot positivity event, and leaves the shock system
  converging to exact.

---

## COST (rule 12) — MEASURED

- **L5b family total: 99.35 core-min** (5961 core-s, `successor.coresec.txt`;
  `PROGRESS.txt` final line) against the **ONE registered hard cap of 100
  core-min** (frozen prereg `4745198733…` §5) — **NO cap breach; the run stopped
  on completion, not on the cap** (`CAP_BREACH.txt` absent). Dollars **DERIVED,
  NOT MEASURED**: 99.35 core-min = 1.6558 core-h × $0.0513/core-h (c7a.4xlarge,
  reported-by-owner; the box cannot read its own billing —
  `COMPUTE_BUDGET_CHARTER.md` §5) = **$0.0849 DERIVED**.
- Per-level (advisory §5 watermarks, not caps): **R1 1.050 core-min**
  (`R1.coresec.txt` = 63), **R2 4.166 core-min** (`R2.coresec.txt` = 250), **R3
  94.133 core-min** (`R3.coresec.txt` = 5648) — the finest level completing to
  `t = 0.2` for the first time.
- **§5 family point estimate 40 core-min**; measured 99.35 core-min gives ratio
  **2.48** actual/predicted. **This is a genuine per-level under-estimate of the
  finest completing level, honestly attributed:** the advisory R3 watermark of 33
  core-min was L4-anchored on a **crash-truncated** R3 (L4 R3 spent 24.6 core-min
  to `t≈0.155` before SIGFPE, extrapolated ≈33 to completion). **No correctly-
  clipped N=240 DMR had ever run to `t = 0.2`** — L5b R3 is the first, and the
  final ~23 % of sim-time (t≈0.155→0.2), never previously measured, is where the
  step count and the clip's per-step `min/max` overhead accumulated to 94.13
  core-min. The gap is misprediction of an unmeasured completion tail, **not
  waste** (`COMPUTE_BUDGET_CHARTER.md` §6 — no stall: R3 `rhoCentralFoamBoundedDMRb`
  ran `wall=1403s ranks=4`, under the 3600-s stall threshold). The rule-12
  calibration row is filed in `docs/COST_CALIBRATION.md`.

---

## WHAT THIS SETTLES, AND WHAT IT DOES NOT

- **Settled (measured):** a correctly-calibrated, field-anchored bounded-energy
  positivity clip (`rhoCentralFoamBoundedDMRb`) **carries the Mach-10 DMR to
  `t = 0.2` at `N = 240` (1/240) with a CONVERGING, in-band grid triple.** All
  three levels PASS Gate V' inside the byte-identical parent tolerance `0.0231`;
  the position triple is CONVERGING with `GCI_fine = 0.0118 %` of travel; the clip
  is a **localized** wall-foot positivity safeguard (≤4 cells, non-conservative on
  those cells only) that does **not** corrupt shock-position accuracy. This is the
  **culmination of the five-lever numerics-robustness ladder** (Minmod → Tadmor →
  Courant-halving → first-order-T → bounded-`e` clip): the answer to
  "**can OpenFOAM v2606 carry this DMR to completion at 1/240?**" is **YES, with a
  positivity-preserving energy update.**
- **This is fix-until-runs SUCCESS, NOT a capability-exhaustion finding.** The
  ladder ran until the DMR ran; the result is a *positive* capability statement
  about the augmented solver, not a negative statement about the vanilla numerics
  (L-501: capability inferences are drawn only from measured, correctly-calibrated
  instruments — here the instrument is calibrated, the `t=0` assertion PASSED, and
  the outcome is a completion, not a crash).

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). This record
does not alter any gate, threshold, band, cap or label of the frozen
pre-registration. No tolerance was widened — Gate V' tol `0.0231` and
`x_exact 2.99568` are the frozen parent's byte-identical values.**
