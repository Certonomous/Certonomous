# How far does the decomposition-adjoint defect reach? A breadth matrix across cases, meshes, and cuts

**2026-08-04, well W4. Docket items `w4-does-the-decomposition-defect-reach-other-cases`
(120 core-min) and `w4-decomposition-invariance-is-a-gate` (60), both approved under
Katie's blanket approval 2026-08-04 and claimed by this session.** Builds on the
verified phenomenon (`VERIFICATION_A4_decomposition_supervisor_sweep.md`), the named
mechanism (`DISCRIMINATORS_A4_decomposition_mechanism.md` + its 2026-08-04
amendments), and the mechanism sweep
(`VERIFICATION_A4_mechanism_supervisor_sweep.md`). Purpose: run cases that SHOULD and
SHOULD NOT show the defect, so the trigger condition is bracketed by measurement
rather than asserted from one case. Run artifacts:
`/home/ubuntu/certonomous-runs/W4-defect-reach/` (per-arm dirs, logs, `ledger.txt`,
drivers).

**Status: PRE-REGISTRATION. Predictions below are committed before any arm runs.**
Results will be appended after; predictions are not edited after the fact.

## What is already on record (folded in, not rerun)

From the verified np-sweep table (`VERIFICATION_A4_decomposition_supervisor_sweep.md`
Axis 1, all patched-IDWarp, A4 coarse 2,777-cell snappy mesh WITH refinement
interfaces, single shape DV, analytic-vs-own-run-FD):

| arm | log | analytic | FD | rel. err |
|---|---|---|---|---|
| np=1 | `a4_np1_patched.log` | 2.4150e-01 | 2.4232e-01 | 0.34% |
| np=2 scotch | `a4_np2_patched.log` | 2.4118e-01 | 2.4182e-01 | **0.26%** |
| np=3 scotch | `a4_np3_patched.log` | 2.5641e-01 | 2.4178e-01 | **6.05%** |
| np=4 scotch | `a4_np4_patched.log` | 2.2086e-01 | 2.4258e-01 | **8.95%** |
| np=4 simple 4x1x1 | `a4_np4_simple4x1x1.log` | 2.4220e-01 | 2.4220e-01 | 0.00054% |
| np=4 simple 1x4x1 | `a4_np4_simple1x4x1.log` | 2.4379e-01 | 2.4265e-01 | 0.47% |

Three record facts this matrix leans on:

1. **The np=2-clean / np=3-dirty contrast is itself evidence.** scotch at np=2 (0.26%)
   sits at the np=1 floor; scotch at np=3 (6.05%, analytic HIGH where np=4's is LOW)
   is catastrophic. Rank count per se is not the trigger (np=4 simple is clean);
   what changes from np=2 to np=3 is the shape/orientation of scotch's cut.
2. **The deliberate "cut through the refinement region" discriminator is already on
   record, backwards:** `simple` 4x1x1 cuts **68** refinement-interface faces (17x
   more than scotch's 4) and is the CLEANEST configuration (0.00054%), and the
   mechanism record's localization puts all 15 large cross-residual entries on
   `cellLevel` 0 cells away from refinement interfaces. "Partition cut touching a
   refinement interface" is refuted as the trigger; it does not need a new run.
3. Decomposition-invariant so far: A1 (4,032-cell structured/conformal airfoil,
   np=1 vs np=4), A2 (38,304-cell conformal wing, scotch vs simple at np=4), A5
   (4,800-cell conformal U-bend, scotch vs simple at np=4) — all at the 1e-04-ish
   level. Every clean case is conformal; the only dirty case (A4) is the only
   snappy-refined mesh tested. That confound is what this matrix breaks.

## The new arms and their PRE-REGISTERED predictions

Hypothesis under test, from the mechanism record's localization (worst cells on
y-normal scotch processor faces; x-normal slabs clean; jagged mixed-orientation
scotch cut catastrophic): **the defect is a property of the parallel reverse-AD
operator's treatment of processor-boundary coupling whose magnitude depends on the
cut's shape/orientation relative to the flow, and it is excited by the cut
geometries scotch produces on snappy-refined meshes — not by refinement interfaces
per se, not by rank count, not by one specific mesh.**

| arm | case / mesh | decomposition | protocol | prediction (registered before running) |
|---|---|---|---|---|
| N1 | A4 (snappy+refinement, 2,777 cells) | np=4 `simple` 1x1x4 (z-normal slabs) | `check_totals`, patched IDWarp | rel. err in **[0.05%, 1.5%]** — same order as y-normal's 0.47%, far below scotch's 8.95%: planar slabs of any orientation are benign-to-moderate |
| N2 | A4 | np=4 `simple` 2x2x1 (x+y planar cuts, 4-rank corner line) | `check_totals` | rel. err **<= 1%** (roughly the x- and y-slab scales combined). Registered decision rule: if > 2%, "scotch-style jaggedness required" is REFUTED — mixed-orientation planar cuts with corners suffice |
| N3 | **Ahmed-35** — NEW second snappy-refined case: ahmed_35.stl (same frame, bbox identical), meshed by A4's own recipe (blockMesh+snappy, cellLevel interfaces present) | np=1 | `check_totals` | control: rel. err **<= 1.5%** (the np=1 floor of this case class) |
| N4 | Ahmed-35 | np=4 `scotch` | `check_totals` | **DEFECT APPEARS: rel. err >= 2%**, and the analytic differs from N3's analytic by >= 2% while the FD column stays within ~0.5% of N3's. This is the headline prediction: the defect travels with (snappy-refined mesh x scotch cut), not with A4's particular mesh. If instead N4 is clean (<1%), the trigger is narrower than hypothesized (specific to A4's cut geometry) and the record says so |
| N5 | Ahmed-35 | np=4 `simple` 4x1x1 (x-normal slabs) | `check_totals` | clean: rel. err **<= 1%** regardless of N4's outcome |
| N6 | **CBFS** (21,000-cell conformal blockMesh — `constant/polyMesh` carries NO cellLevel — beta-field DVs, 21,000 components, `varianceU` objective, `dafoam-subpclu:v1` + `DAFOAM_SUBPC_TYPE=lu` exactly as the record arm) | np=4 `simple` 4x1x1 vs the np=4 `scotch` RECORD arm (`W4-adjoint-pc-unblock/cbfs_beta`, FD at 3 cells on record: 0.085% / 0.059% / 0.199%) | `compute_totals`; both arms' gradient vectors mapped to serial cell ordering via each arm's own `cellProcAddressing` (rank-concatenation convention verified before use) | **decomposition-invariant**: mapped analytic agrees at the three recorded FD cells to **<= 1%** per component, vector norms to <= 2%. Conformal mesh + different DV type (volume field, not shape) both stay clean |
| N7 (contingent — runs only if N4 fires) | Ahmed-35 | scotch psi vs np=1 operator | the cross-residual instrument of the discriminators session (`W4-a4-discriminators/runScript_w4.py` tasks `w4_dump`/`w4_crossres`, `build_maps.py`), sign convention **A^T psi = -b**: the instrument computes `Atpsi - b`, so own-operator logs print the degenerate `ratio=2.0` and the reported numbers are exact offline corrections `res + 2b` from the dumped vectors — stated per the amended M1 caption | cross-residual **>= 10x ||b||** under the np=1 operator, concentrated on momentum rows of partition-interface cells; np=1 control at its ~1e-04-ish floor |

Scoring discipline: each prediction is scored HELD / NOT HELD / NOT SCORED exactly
as written above; no post-hoc bands.

## Budget

180 core-min combined across the two items. Planned: N1+N2 ~12, Ahmed-35 mesh ~1,
N3 ~4, N4+N5 ~12, N6 ~16, N7 (contingent) ~12; total ~45-60 planned, the rest is
reserve for the contingent instrument and any arm that needs a rerun. All runs
ledgered wall x cpus-cap in `W4-defect-reach/ledger.txt`; overruns stated.

*(Results and verdict sections follow after the runs; nothing below this line
existed at pre-registration commit time.)*
