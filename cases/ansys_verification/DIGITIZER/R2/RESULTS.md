# RESULTS — DIGITIZER re-file R2

**BOTH QUANTITIES PASS. The digitizer's grading is certified as an instrument;
the §29.3 fix works — POSITION now carries a `u_read` the locator can back, and
its planted null passes by construction.** Verdicts taken by
`ansys-verification-supervisor` personally, 2026-09-03, by reproducing the frozen
R2 instrument against the freeze. This certifies the READER; **it gates no VMFL
case** (§25.7/§28.8 unmet — `u_read` is re-derived per case on each target's
answer-blind format).

| quantity | verdict | u_read | binds | null | prediction |
|---|---|---|---|---|---|
| **R2-VALUE** (y-data) | **PASS** | 0.00505051 | pixel floor (max err 0.00111 < floor) | 0.000746 ≤ u_read | u_read ≈ floor — **held** |
| **R2-POSITION** (x-data) | **PASS** | 0.00470157 | **term A = MAX** (§29.3) | **0.0032424 ≤ 0.0047016, passes BY CONSTRUCTION** | u_read ≈ 1.693 px = 0.004703 — **held to 3 s.f.** |

The POSITION null offset **0.0032424** is the *exact* clean-control offset that
**refused in R1**; it now passes because `u_read = max per-plate error ≥ it`. The
§29.3 statistic change did precisely what it was ruled to do. Both PLANT-DETECT
bands and biases passed; both AXIS negatives (log-as-linear, planted-flip) caught.

## Freeze & reproduction

Freeze `5714f2c7`; R2 instrument blob `c1d275a2…` (imports frozen R1 `2092c55d…`
read-only, verified intact). Verdicts reproduced by **two independent paths**:
the CLI stdout (`GRADE_R2.out`, `REPRO_R2.supervisor.out`) and a direct
`calibrate_r2(verbose=False)` call that returns the graded dict cleanly — both
give identical numbers. **The verdict rests on the clean computation.**

## ⚠ CRASH TRIAGE (§3 check 2) — a real toolchain defect, triaged to post-grading, verdict unaffected

The authorised CLI run **exited rc 1** — not on a verdict and not on an overrun,
but on an **uncaught `ValueError: Circular reference detected` in the final
`json.dumps`**. I did not accept this as cosmetic on report; I triaged it:

1. **Grading completed before the crash** — both PASS verdicts and the full
   per-quantity breakdown printed to stdout, then `json.dumps` died. Confirmed in
   `GRADE_R2.out` / `REPRO_R2.supervisor.out` (verdicts present) vs
   `GRADE_R2.err` / `.supervisor.err` (traceback last).
2. **Mechanism proven:** the frozen default handler
   `lambda o: float(o) if isinstance(o, np.floating) else o` returns **`np.bool_`**
   objects (from comparisons like `recovery_err <= band`) **unchanged** —
   `np.bool_` is not `np.floating` — so the encoder re-encounters the same
   non-serializable object and raises circular-reference. Reproduced the exact
   `np.bool_`-through-the-handler behaviour in isolation.
3. **Verdict independent of the crash:** `calibrate_r2(verbose=False)` returns the
   graded dict without ever calling `json.dumps`, with identical verdicts and
   numbers. The grading path is sound; only the reporting print is broken.

**Disposition (rule 6 — frozen files are never edited):** the defect is
**DISCLOSED, NOT REPAIRED**. It is **latent in R1 too** (R1 refused at exit 2
before reaching `json.dumps`, so it never surfaced there). It moves **no verdict
number**. The one-line fix (cast `np.bool_`/`np.integer` in the handler) folds
into the **first per-case registration's instrument** — which re-matches each
target's answer-blind format per §28.6 anyway — rather than a standalone R3 freeze
for a reporting-layer one-liner. **Per-case use that reads stdout works today;
use that reads the JSON file or the exit code needs that fix.** Recorded as a
lesson (the selftest never ran the full `--calibrate` path, so serialization was
never exercised until now).

`GRADE_R2.json` is a **reconstruction** by the lane (via `calibrate_r2` +
numpy-aware encoder), byte-matching the stdout numbers — labelled as such, not the
CLI's own emission.

## Cost (rule 12)

Filed 0.1 core-min, cap 0.3. Authorised run **4.032 s = 0.0672 core-min** single
core; my reproduction corroborates. **Under cap, no overrun** (the rc 1 is the
reporting crash, not a budget kill). Full-calibration run, no early refuse.
Calibration row in `docs/COST_CALIBRATION.md`.

## What this does and does not unlock

The instrument's VALUE and POSITION grading are certified. **No VMFL case gates
on a digitized reference on the strength of this** — §25.7 requires a per-case
registration that freezes prediction, the per-case `u_read` (re-derived on that
plate's answer-blind format), band arithmetic and plate hash. VMFL046-R2 (Fig
.46.2, a POSITION/shock-location read) is the first such per-case candidate, and
§29.5 stands: its digitized `u_read` (~1.7 px) will likely cap it at
`GATE REACHED`. **Row #54's `GATE FAIL` is permanent.**
