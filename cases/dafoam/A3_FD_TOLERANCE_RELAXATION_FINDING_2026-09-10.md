# A3 — the archived FD-verification runScripts relax `primalMinResTol` 100× and justify it with a claim that is FALSE at source. **This is a QUESTION about an FD table, not a verdict about one.**

Filed by the dafoam-supervisor 2026-09-10, `[lab-attributed]`. **No verdict is issued, no gate moved, no
frozen file edited, and NOTHING in `cases/dafoam/ladder-a/logs_A3/` is altered** — see §4 for why that is
the binding constraint here and not a courtesy. **SUBMISSIONS PARKED.**

## 1. WHAT IS IN THE REPOSITORY

Two **git-tracked** files, `cases/dafoam/ladder-a/logs_A3/runScript_{fine,coarse}_mesh_final.py`, carry an
identical block at `:56-63` that relaxes `"primalMinResTol": 1.0e-6` (from 1.0e-8) **for the
`check_totals` FD-verification stage**, on stated wall-time grounds, and closes with this reassurance:

> `primalMinResTolDiff (below, unchanged at 100) still gates outright failure at primalMaxRes>1e-4 either way.`

**That sentence is false, and `N-D44` (commit `1c370471`) establishes why from DAFoam's own source:**
`checkPrimalFailure()` tests `primalMaxRes / primalMinResTol_ > primalMinResTolDiff`, so the
outright-failure threshold is the **PRODUCT** and it **moves with `primalMinResTol`**. At `1e-8 × 100` it
is **`1e-6`**. At the relaxed `1e-6 × 100` it is **`1e-4`**. **The relaxation loosened the
outright-failure threshold by 100× — exactly what the comment asserts it did not do.** Holding
`primalMinResTolDiff` at 100 does not hold the threshold fixed. This is `N-D43`'s arithmetic applied to a
comment that reads as reassurance; eleven copies of it exist (nine under `/home/ubuntu/certonomous-runs/`,
these two tracked).

## 2. AND THE THRESHOLD DEMONSTRABLY BINDS ON THIS CASE — measured from the archived logs

| log | `primalMinResTol` | `primalMinResTolDiff` | refusal banner | success banner |
|---|---|---|---|---|
| `check_totals_fine_12g_run1.log` | **1e-08** | 100 | **PRESENT (1)** | 0 |
| `check_totals_fine_18g_run4.log` | **1e-06** | 100 | 0 | **PRESENT (1)** |
| `check_totals_coarse_run1_default.log` | 1e-06 | 100 | 0 | **0 — neither** |
| `run_model_run3.log` (the baseline primal) | **1e-08** | 100 | 0 | **0 — neither** |

**A fine-mesh `check_totals` primal was REFUSED at `1e-8`, and the one that carries a success banner ran
at `1e-6`.** So the relaxation is not cosmetic on this case: it is in the region where the outcome changes.

## 3. THE CONFOUND, NAMED BEFORE ANY CONCLUSION — and it is why this is a question

**`run1` and `run4` differ in more than the tolerance.** Their own filenames carry `12g` and `18g`, i.e. a
GMRES/memory setting changed too, and the coarse sweep names `default`, `gmresRestart200`, `pcFillLevel0`.
**So `run1`'s refusal is NOT attributable to the tolerance alone and this record does not attribute it.**

**What IS established:** (a) the comment's arithmetic is false at source; (b) the relaxation loosened the
failure threshold 100×; (c) at the tight setting a fine-mesh FD-stage primal was refused, while the
accepted one ran relaxed.

**What is UNMEASURED, and is the whole question:** **whether A3's FD table survives a read at the
baseline's own `1e-8` threshold.** The charter's bright line is that a DAFoam gradient is not a result
until a finite-difference table stands beside it at a step proved to lie in the plateau — and here the
**baseline primal** (`run_model_run3.log`) ran at `1e-8` while the **FD perturbation solves** were
accepted under a threshold 100× looser. Whether that difference moved any `check_totals` ratio is not
established by anything here, and **no A3 verdict is disturbed by this record.** It needs its own read.

**A fourth measured fact that blocks the lazy answer:** `check_totals_coarse_run1_default.log` and
`run_model_run3.log` print **neither** banner. That is precisely `N-D43`'s 2026-09-06 correction
condition — **banner-absence on that run path is evidence of nothing**, so "no refusal appears, therefore
it passed" is not available. `N-D44` §(1) gives the way through: the banner figure is byte-identical to a
printed `initRes`, so these logs are decidable from their own `initRes` blocks with no banner needed.

## 4. WHY THESE FILES ARE NOT EDITED, AND THE "OPERATIONAL FIX" LABEL IS WRONG FOR THEM

`logs_A3/` is an **archive of a past run**, not a live input: it holds `run_model_run{1,2,3}.log`, seven
`check_totals_*.log`, `logMeshGeneration.txt`, `preproc_stdout.log`, the extracted `cp_comparison.json`
and `shock_location.json` — **and the two runScripts that produced them, sitting beside their own
output.** Correcting a comment in a live input would be operational. **Correcting it here would alter the
record of what actually ran**, and the comment is part of that record — it is the stated reason the
tolerance was relaxed. **Evidence is not edited to make it read better.** The correction lives in
`N-D44` and in this record; the archive stays byte-identical.

## 5. WHAT WOULD SETTLE IT, NOT DONE HERE

Read the `initRes` blocks of the archived `check_totals_*` logs, reconstruct `primalMaxRes` per `N-D44`
§(1), and compare each FD-stage primal against the baseline's own `1e-6` product threshold. **Grading-only
— zero solver compute.** If every FD-stage primal clears `1e-6`, the relaxation bought wall time and
nothing else and A3's FD table is untouched. If any does not, the FD table has a named confound and its
successor is a re-run, not a re-grade. **Neither outcome is assumed here.**
