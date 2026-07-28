# F6c — Square/rectangular duct: uncorrected RANS baseline vs DNS secondary flow

Date: 2026-07-28. Family F6 (Certonomous hard-case campaign), sub-family c.
Machine-readable companion: `F6c_duct_vs_dns.json`. Per docket instruction,
this rung goes **straight to the gate**: ladder B2 (commit `e2c45ab`) already
climbed feasibility and physics for `AR_1_Ret_360` and `AR_3_Ret_360` and
reproduced the benchmark's own uncorrected `kOmegaSST` baseline to
0.02–0.09% field-vs-field deviation. What was missing was the comparison
against DNS — that is what this rung measures. **Zero new CFD was run**;
this is pure post-processing of B2's already-converged fields against the
DNS reference field the benchmark ships alongside them. No fitting, tuning,
or selection against test-case ground truth occurred.

## Headline result

**The uncorrected linear-eddy-viscosity `kOmegaSST` baseline predicts
exactly zero secondary flow (RMS ~1e-15% of bulk velocity — machine
precision, i.e. genuinely zero, not "small") in both duct cross-sections,
while the DNS reference field shows a real, finite secondary-flow magnitude
of 2.07–2.22% of the bulk velocity.** This is not a numerics bug: it is the
textbook consequence of the linear Boussinesq eddy-viscosity hypothesis,
which cannot represent the Reynolds-stress anisotropy that drives Prandtl's
secondary flow of the second kind in a non-circular duct. This is the exact
physical mechanism behind `AR_1_Ret_360`/`AR_3_Ret_360` being the two
largest single contributors to our measured deficit versus the rank-2
leaderboard entry (31.5% and 31.4%, per
`demo-output/website/closure_challenge_C2_error_decomposition.md`).

## Reference data provenance

The benchmark's own `data/DUCT/{case}/0/U_LES` (and `k_LES`, `tauij_LES`)
ship alongside the RANS baseline case files on the **same mesh** (same
cell-center ordering as the RANS `U` field — confirmed identical cell count,
3025 for `AR_1_Ret_360`, 8748 for `AR_3_Ret_360`). Per the benchmark's own
README, the duct dataset's "Original data link" is
[vinuesalab.com/duct](https://www.vinuesalab.com/duct/) (the Vinuesa-lab DNS
square/rectangular-duct database), and the README states explicitly that
each dataset ships "DNS or LES 'ground truth' data, including velocity
gradients" alongside the `kOmegaSST` RANS prediction. We did not
independently re-derive or re-fetch the DNS from vinuesalab.com this rung —
we used the copy already shipped and referenced by the benchmark's own
release, exactly as B2 used the benchmark's own shipped RANS case files.

## Method

For each case, on the shared mesh:

- `U_secondary = sqrt(Uy^2 + Uz^2)` per cell, for both the converged RANS
  field (B2's `456/U`, `1700/U`) and the shipped `0/U_LES` field.
- `U_bulk` estimated as the arithmetic mean of `Ux` over all cells (a direct
  measurement from the field itself, not assumed from `Re_b`/`nu`/`D_h`).
- Reported as RMS over all cells, both in absolute units (m/s) and as a
  percentage of `U_bulk`.

## Gate: RANS secondary-flow magnitude vs DNS

| Case | Cells | `U_bulk` (m/s, RANS) | RANS secondary RMS | DNS secondary RMS | RANS as % of DNS |
|---|---|---|---|---|---|
| `AR_1_Ret_360` | 3,025 | 33.08 | 2.01e-16 m/s (**6.1e-16% of U_bulk**) | 0.734 m/s (**2.22% of U_bulk**) | **~0%** |
| `AR_3_Ret_360` | 8,748 | 38.45 | 9.12e-16 m/s (**2.4e-15% of U_bulk**) | 0.796 m/s (**2.07% of U_bulk**) | **~0%** |

The RANS secondary-flow RMS is at floating-point machine precision (1e-15–
1e-16), confirming it is exactly zero rather than merely small — consistent
with the closed-form fact that a linear eddy-viscosity model with an
isotropic normal-stress difference produces no streamwise vorticity source
term in a straight duct. The DNS magnitude (2.07–2.22% `U_bulk`) matches the
well-known literature range for this flow (secondary flows in non-circular
duct DNS are typically reported at 1–3% of bulk velocity).

## Verdict

**GATE MEASURED, FAIL AS EXPECTED AND DOCUMENTED — not shipped as a pass.**
The uncorrected RANS baseline captures 0% of the DNS secondary-flow
magnitude in both cases. This is the correct, honest outcome for a linear
eddy-viscosity closure on this flow, and it directly explains why
`AR_1_Ret_360`/`AR_3_Ret_360` carry the largest share of our measured
closure-challenge deficit: the "learned quantity" a data-driven correction
must supply here is not a small refinement to an already-reasonable RANS
field, it is the *entire* secondary-flow structure, from zero.

## Cost

Zero new CFD — post-processing only on B2's already-converged fields.
Analysis wall time: under 5 seconds total (Python field parsing + arithmetic
on both cases), no MPI, no memory pressure.

## Evidence files

- This report: `demo-output/website/dafoam/f6c_duct_dns/F6c_duct_vs_dns.md`
- Machine-readable: `demo-output/website/dafoam/f6c_duct_dns/F6c_duct_vs_dns.json`
- Per-case gate numbers: `demo-output/website/dafoam/f6c_duct_dns/{AR_1_Ret_360,AR_3_Ret_360}_secondary_flow_gate.json`
- Analysis script: `demo-output/website/dafoam/f6c_duct_dns/secondary_flow_gate.py`
  (also copied into `ladder-b/duct_baseline/` alongside the source fields it reads)
- Source RANS fields: `demo-output/website/dafoam/ladder-b/duct_baseline/{AR_1_Ret_360,AR_3_Ret_360}/` (from B2)
- Source DNS fields: `/home/ubuntu/closure-challenge-benchmark/data/DUCT/{AR_1_Ret_360,AR_3_Ret_360}/0/U_LES` (benchmark's own scratch clone, not duplicated into this repo)

## What's next / blocked

- `AR_14_Ret_180` is the third duct test case on the leaderboard but its
  RANS baseline has **not** been reproduced by this campaign (B2 only
  covered `AR_1_Ret_360`/`AR_3_Ret_360`). Case files exist at
  `data/DUCT/AR_14_Ret_180/` in the benchmark clone — flagged for a future
  rung, not run here (lower priority: not named in the docket's measured
  deficit breakdown).
- This rung measures bulk secondary-flow magnitude only, not the spatial
  vortex-pattern structure (the classic 8-vortex pattern in a square duct).
  A per-cell or streamwise-vorticity spatial comparison was not attempted —
  out of scope for this gate.
