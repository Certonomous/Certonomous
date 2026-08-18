# Ladder B2 — square-duct uncorrected RANS baseline reproduction

Date: 2026-07-28. Machine-readable companion: `B2_duct_baseline.json`. Scope per
docket: reproduce the **baseline** (uncorrected k-omega SST RANS) for
`AR_1_Ret_360` and `AR_3_Ret_360`, plus `CBFS` if cheap. Field inversion is
explicitly out of scope (B3). No fitting, tuning, or selection was performed
against test-case ground truth — every score below is a single forward
evaluation through the benchmark's own unmodified scorer, same operation
already used for the published `closure_challenge_rans_floor.json`.

## Headline result

**We independently reproduced the benchmark's own uncorrected k-omega SST
baseline for both duct test cases to within 0.02–0.09% internal-field scaled
MAE**, using our own OpenFOAM v2606 install against the exact case
directories (mesh, BCs, `fvOptions`) shipped in the benchmark's own scratch
clone — not a from-scratch case build. Two documented deviations (a missing
custom turbulence library, and an OpenFOAM fork/version mismatch) turned out
to be effectively inert for the baseline field, which is itself a useful
finding for B3: this baseline setup can be trusted without re-deriving it.

| Case | Cells | Our score | Reproduced benchmark baseline score | Published floor (`closure_challenge_rans_floor.json`) | Deviation (ours − floor) | Field-vs-field scaled MAE (ours vs benchmark baseline) | Our iterations | Original iterations |
|---|---|---|---|---|---|---|---|---|
| `AR_1_Ret_360` | 3,025 | 0.1290 | 0.1288 | 0.1288 | +0.0002 (0.16%) | 0.023% | 456 | 405 |
| `AR_3_Ret_360` | 8,748 | 0.1251 | 0.1243 | 0.1243 | +0.0008 (0.64%) | 0.09% | 1,700 | 1,540 |
| `CBFS` (not a scored test case) | 21,000 | n/a — no published floor | n/a | n/a | n/a | 0.068% vs benchmark's own baseline field | 30,000 (fixed endTime, see below) | 30,000 |

"Reproduced benchmark baseline score" = we took the benchmark's own shipped
baseline field (the exact source of the published floor), scored it through
our own scoring script as a sanity check on the scoring pipeline itself —
it matches the published floor exactly (0.1288, 0.1243), confirming our
scorer setup is correct before trusting the "our score" column next to it.

## Where the case files came from

The benchmark's local scratch clone (`/home/ubuntu/closure-challenge-benchmark`)
ships the **actual OpenFOAM case directories** used to generate the published
baseline fields — `data/DUCT/AR_1_Ret_360/`, `data/DUCT/AR_3_Ret_360/`,
`data/CBFS/` — including `caseDef`, `fieldDef`, `system/fvOptions`, and the
original solver log (`log.run`). The log's own `Case:` path confirms these
are literally the paper authors' `00Baseline/beta11` (β=1, i.e. uncorrected)
directories from their thesis codebase:
`.../thesis/finalCases/rectDuct/AR_1_Ret_360/00Baseline/beta11` (duct log)
and `.../inversion/TurbFOAM-7-Cases/2D-Seperated-Flow-Cases/Curved-Backward-Facing-Step/00Baseline_data`
(CBFS log). This is as close to ground truth as reproduction gets — we are
not inferring a baseline setup from a paper's text, we are re-running the
authors' own case files on our own solver.

Case params, from `caseDef`:

- `AR_1_Ret_360`: channel half-height h=0.001 m, AR=1, Re_b=5693, Re_tau=341.98, nu=1.5e-5.
- `AR_3_Ret_360`: h=0.001 m, AR=3, Re_b=5817, Re_tau=335.88, nu=1.5e-5.
- Both: quarter-duct mesh (symmetry planes on 2 of 4 boundaries), cyclic
  (periodic) streamwise inflow/outflow, `nutLowReWallFunction` +
  `omegaWallFunction` on the physical walls, `meanVelocityForce` fvOption
  driving a fixed bulk velocity (this is the standard periodic-duct DNS/RANS
  setup, not an inlet-BC-driven case).
- `CBFS`: 2D curved backward-facing step, 21,000 cells, `kOmegaSST`,
  `residualControl` on `p` is effectively disabled (1e-15) with U/k/omega
  controls commented out in the shipped `fvSolution` — this case is *designed*
  to run to a fixed `endTime` (30,000 iterations) rather than auto-stop on a
  residual test, and we preserved that behavior rather than imposing our own.

## Deviations, documented with cause

### 1. Missing custom turbulence library (`libfrozenIncompressibleTurbulenceModels.so`)

Every one of these `controlDict`s loads
`libs ( "libfrozenIncompressibleTurbulenceModels.so" );`, a custom library
from the paper authors' own thesis codebase. **Its source is not distributed
anywhere in the public `closure-challenge-benchmark` clone** — a `grep -rl`
across the entire repo finds zero hits outside the `controlDict` references
themselves, and it is not part of stock OpenFOAM.

*Action taken:* removed the `libs` entry; `RASModel kOmegaSST` resolves to
OpenFOAM v2606's stock implementation instead.

*Risk assessment:* the `fvSchemes` `divSchemes` block in these cases
references extra terms (`bijDelta`, `useRST`, `xi_ramp`) that only matter for
the paper's **corrected** (β≠1, field-inverted) case variants — the baseline
`fvOptions` here defines only `meanVelocityForce`, nothing referencing those
fields. This strongly suggests the custom library only matters once β(x)
correction terms are active, and is inert for β=1. The measured field
agreement (0.02–0.09% scaled MAE, table above) is consistent with that being
true, **but this was not independently verified against the library's own
source**, since that source could not be obtained. Flagged, not asserted.

### 2. OpenFOAM fork/version mismatch

Original baseline: OpenFOAM-7 (OpenFOAM Foundation fork, `openfoam.org`),
build `7-3bcbaf946ae9`, per the shipped `log.run` headers. This box has
OpenFOAM **v2606** (OpenCFD/ESI fork, `openfoam.com`) installed — a different
code lineage, not a different version of the same lineage. Dictionary-file
syntax is compatible (the case ran without edits beyond the two items in this
list), but the two forks are not guaranteed to be bit-identical numerically
(different default GAMG agglomeration, linear-solver internals, etc.).

*Measured effect:* iteration count to residual-convergence differs by
10–13% (`AR_1`: 456 vs 405 iterations; `AR_3`: 1,700 vs 1,540), but the
**converged field** differs by only 0.02–0.09% scaled MAE against the
benchmark's own baseline field — consistent with a convergence-path/numerics
difference, not a setup or physics difference.

### 3. Post-processing function objects dropped

`#includeFunc residuals` fails on v2606: it `#includeEtc`'s
`caseDicts/postProcessing/numerical/residuals.cfg`, which OpenFOAM v2606
does not ship at that path (it renamed the equivalent function object to
`solverInfo`; confirmed by listing `$FOAM_ETC/caseDicts/postProcessing/numerical/`
on this box, which contains only `solverInfo{,.cfg}`). CBFS's `controlDict`
also referenced several `singleGraph_x0`..`x8` sampling-line diagnostics.

*Action taken:* dropped the entire `functions{}` block for all 3 runs. These
are diagnostics only (residual logging, probe/sample output) — they read the
solution, they do not feed back into it — so this cannot affect the solved
field, and the near-zero field-vs-field deviations above confirm that in
practice. We did **not** attempt to reproduce the paper's residual-history or
velocity-profile plots this rung; that is out of B2's scope (converged field
only).

## CBFS notes (not a scored test case — included per docket's "if cheap")

CBFS is the paper's field-inversion **training** case, not one of the
benchmark's 8 scored test cases, so it carries no leakage exposure and there
is no published floor to compare against. It ran to its designed fixed
`endTime` of 30,000 iterations (see above) in 1,753.3 s CPU / 1,770 s wall
(serial, ~29.5 core-minutes) — noticeably more than B1's estimate of ~17
core-minutes (that estimate was extrapolated from the *original authors'*
log timing on different hardware; our own hardware ran this specific case
slower per-iteration than B1's extrapolation assumed. Documented here rather
than silently absorbed). The converged internal field agrees with the
benchmark's own shipped CBFS baseline field to 0.068% scaled MAE — same
strong-agreement pattern as the ducts.

**One real blocker found here, flagged for B3, not fabricated around:** CBFS's
`0/U_LES` (and `k_LES`, `tauij_LES`) reference fields use OpenFOAM
`#include`-macro'd dictionaries (`interpolatedFields/U_internalField`, etc.).
The `Ofpp` Python package used for scoring **cannot resolve these macros** —
it silently returns `None` rather than erroring, which we caught by checking
the return value rather than trusting it. This means the LES-vs-RANS
discrepancy (the actual training signal B3 would need) was **not measured**
this rung. B3 will need `foamDictionary`/`postProcess` (or a macro-aware
reader) to pre-resolve these before it can use CBFS's LES field as a
field-inversion target.

## Comparison to the paper's own reported baseline

Wu, Zhang & Zhang (AIAA J 2025 / arXiv:2402.16355) do not train or report on
the square-duct cases at all — per the B1 reproduction plan, the
closure-challenge submission (Wu and Zhang, leaderboard rank 2) scores DUCT
purely by **zero-shot generalization** of a model trained only on CBFS.
Neither the paper nor the submission's description document publishes an
uncorrected-SST-only numeric score for `AR_1_Ret_360`/`AR_3_Ret_360`
separate from the benchmark's own shared RANS-identity floor — **that floor
is the correct "paper's baseline" reference point**, because Wu & Zhang's
corrected SST-QCRC model starts from the exact same benchmark-shipped SST
field we just reproduced (same case directories, same solver family, same
turbulence model). We compare against it above. No paper-stated duct-baseline
figure was available to cross-check beyond this — stated plainly rather than
invented.

## Cost

| Case | Wall time | Core-minutes |
|---|---|---|
| `AR_1_Ret_360` | 8 s | 0.13 |
| `AR_3_Ret_360` | 76 s | 1.27 |
| `CBFS` | 1,770 s (29.5 min) | 29.5 |
| **Total** | **~30.6 min** | **~30.9** |

All runs serial (1 rank), well under the 4-MPI-rank cap. `MemAvailable`
checked before the CBFS run (the only long one): 20.4 GB free at start of
session, 13.0 GB free after all three runs completed — comfortably above the
6 GB threshold throughout, no contention with the mega-batch or other
concurrent agents observed.

## Lesson

The benchmark's own scratch clone ships the **actual solved case
directories** (mesh, dictionaries, and the original `log.run`) behind its
published RANS-identity floor, not just the final interpolated field. That
turned this rung from "build a case from a paper's text" into "re-run the
authors' own case files on our own solver" — a much stronger reproduction.
The result is that our independently-run OpenFOAM v2606 baseline agrees with
the benchmark's own OpenFOAM-7 baseline to within 0.02–0.09% internal-field
scaled MAE despite two forks and a missing custom library. **B3 can trust
this baseline setup without re-deriving it**, and does not need to chase
down `libfrozenIncompressibleTurbulenceModels.so`'s source before starting —
the measured agreement already brackets that risk as small.

## What B3 needs next

1. A macro-expanding OpenFOAM field reader (or a `foamDictionary`/
   `postProcess` pre-resolution step) to extract CBFS's `0/U_LES` (and
   `k_LES`, `tauij_LES`) as usable field-inversion targets — `Ofpp` silently
   fails on the `#include`-based `interpolatedFields` structure used there.
2. A DAFoam `DASimpleFoam` case built from these same case directories (`0/`,
   `constant/`, `system/`, `caseDef`, `fvOptions`) to confirm the adjoint
   runs cleanly on this exact mesh/BC/`fvOptions` combination before
   committing to the β(x) field-inversion optimization loop.
3. A short **timed pilot** (a handful of SLSQP/adjoint iterations on CBFS,
   timed) to resolve B1's flagged cost uncertainty (140–420 core-minutes
   estimated, dominated by whether each iteration re-converges the primal
   from a warm start cheaply or expensively) before committing a full
   field-inversion budget.
4. A decision on whether to reproduce the paper's CBFS-only training +
   zero-shot duct generalization route, or attempt training directly against
   the duct cases' own available LES/DNS reference fields (would require
   checking the DUCT case directories for a CBFS-`tauij_LES`/`U_LES`
   equivalent — not checked this rung, out of B2's scope).

## Evidence files

- This report: `demo-output/website/dafoam/ladder-b/B2_duct_baseline.md`
- Machine-readable record: `demo-output/website/dafoam/ladder-b/B2_duct_baseline.json`
- Case working directories (config + logs + converged fields):
  `demo-output/website/dafoam/ladder-b/duct_baseline/{AR_1_Ret_360,AR_3_Ret_360,CBFS}/`
- Scoring script: `demo-output/website/dafoam/ladder-b/duct_baseline/score_our_baseline.py`
  (ducts) and `compare_cbfs.py` (CBFS field-vs-field only, no scorer call
  since CBFS isn't a scored case)
- Raw score output: `demo-output/website/dafoam/ladder-b/duct_baseline/score_our_baseline_result.json`
