# F6 — Closure-aligned flows (Certonomous hard-case campaign)

Date: 2026-07-28. Machine-readable companion: `F6_closure_aligned_flows.json`.
Docket priority order: **F6a (NASA hump) → F6c (duct vs DNS) → F6b (periodic
hills, only if time remains)**, by measured deficit contribution per
`demo-output/website/closure_challenge_C2_error_decomposition.md`
(`AR_1_Ret_360` 31.5%, `AR_3_Ret_360` 31.4%, `NASA_2DWMH` 18.2%, `alpha_05`
combined 18.9%). F6a and F6c were completed and gated this session; F6b was
**not attempted** — time-boxed per the docket's own "only if time remains"
instruction, after F6a and F6c were fully climbed and gated.

Every number below is either a fresh forward CFD solve run in this session
or a re-derivation from already-existing, already-converged fields (B2,
commit `e2c45ab`). No fitting, tuning, or selection against any test-case
ground truth occurred anywhere in this work. All external reference numbers
(NASA experimental data, NASA's own SST CFD result) were fetched live from
their source this session, not recalled from memory — URLs are cited in
each sub-report.

## Summary table

| Sub-family | Rung reached | Gate quantity | Ours | Reference | Deviation | Verdict | Core-min |
|---|---|---|---|---|---|---|---|
| **F6a** NASA_2DWMH | Feasibility → Physics → **Gate** | Separation `x/c` | 0.6544 | NASA exp. 0.665 | -1.6% | close | **5.25** |
| F6a | (same run) | Reattachment `x/c` | 1.2534 | NASA exp. 1.100 | +13.9% | documented SST bias (expected) | (included above) |
| F6a | (same run) | Separation `x/c` (cross-check) | 0.6544 | NASA's own SST CFD 0.654 | +0.06% | near-exact | — |
| F6a | (same run) | Reattachment `x/c` (cross-check) | 1.2534 | NASA's own SST CFD 1.25–1.27 | in range | near-exact | — |
| F6a | (same run) | Benchmark scorer self-check | 0.0622 | published floor 0.0621 | +0.16% | reproduction verified | — |
| **F6c** DUCT vs DNS | Feasibility/Physics already passed (B2) → **Gate** | Secondary-flow RMS, `AR_1_Ret_360` | 6.1e-16% `U_bulk` | DNS 2.22% `U_bulk` | RANS captures ~0% | **fail, expected & documented** | **0** (post-processing only) |
| F6c | (same rung) | Secondary-flow RMS, `AR_3_Ret_360` | 2.4e-15% `U_bulk` | DNS 2.07% `U_bulk` | RANS captures ~0% | **fail, expected & documented** | — |
| **F6b** Periodic hills | **Not attempted** | — | — | ERCOFTAC reference | — | time-boxed, not run | 0 |

**Total new compute this session: ~5.25 core-minutes** (all in F6a; F6c was
free re-analysis of already-converged fields).

## F6a — NASA 2D wall-mounted hump

Fresh work, all three rungs climbed on the benchmark's own shipped case
(51,626-cell mesh, `Re_c=936,000`, `M=0.1`, `c=0.42 m`, confirmed against
NASA TMR's own stated parameters). Stock `kOmegaSST` substituted for the
unavailable custom `AugmentedkOmegaSST`/`libfrozenIncompressibleTurbulenceModels.so`
(same substitution B2 made for the duct cases), measured inert (0.00–0.02%
deviation vs the benchmark's own shipped baseline field).

- **Feasibility** (0→100 iter, 4.25 s, 0.28 core-min): runs clean, no crash,
  residuals falling.
- **Physics** (0→800 iter, 37.58 s, 2.51 core-min): separation bubble
  clearly present pre-convergence (`Cf` sign changes at `x/c≈0.65` and
  `x/c≈1.26`).
- **Gate** (800→1772 iter, `SIMPLE` auto-converged on `residualControl`
  `U/p/k<5e-7`, `omega<1e-10`, 36.99 s, 2.47 core-min): final Cf/Cp
  extracted and compared against NASA's own published experimental data
  (separation 0.665, reattachment 1.1 — fetched live from
  [tmbwg.github.io/turbmodels/nasahump_val_sst.html](https://tmbwg.github.io/turbmodels/nasahump_val_sst.html),
  the relocated NASA Turbulence Modeling Resource site).

**Gate result:** separation `x/c=0.6544` vs experiment `0.665` (**-1.6%**,
close agreement); reattachment `x/c=1.2534` vs experiment `1.100`
(**+13.9%**, over-predicted bubble length). This +13.9% reattachment error
is not a setup bug: our result matches NASA's own published SST CFD
solution (different code, different mesh) to within 0.06% on separation and
inside their quoted 1.25–1.27 reattachment range — i.e. we are reproducing
the textbook linear-eddy-viscosity SST deficiency exactly, independently
confirmed against NASA's own SST numbers, the benchmark's own shipped
baseline field (0.00–0.02% deviation), and the benchmark's own scorer
(our score 0.0622 vs published floor 0.0621, **+0.16%**, field-vs-field
scaled MAE **0.02%**). Cp shape vs experiment: 2.89% scaled MAE over 110
overlapping `x/c` points (secondary metric, subject to a documented
Cp-reference-pressure caveat).

**Verdict: GATE REACHED.** Baseline independently verified correct via
three cross-checks; the deviation from experiment is the expected,
literature-documented model-form error that a data-driven closure
correction targets — exactly what F6a was ordered to establish.

Full report: `demo-output/website/dafoam/f6a_nasa_hump/F6a_nasa_hump.md`

## F6c — Square/rectangular duct vs DNS

Baseline reproduction was already complete (B2, commit `e2c45ab`,
`AR_1_Ret_360`/`AR_3_Ret_360` within 0.16%/0.64% of the published floor).
This rung went straight to the gate ordered by the docket: compare the
converged secondary-flow field against DNS. **Zero new CFD** — pure
post-processing of B2's fields against the DNS reference field
(`0/U_LES`) the benchmark ships on the identical mesh, sourced (per the
benchmark's own README) from
[vinuesalab.com/duct](https://www.vinuesalab.com/duct/).

**Gate result:** the uncorrected `kOmegaSST` baseline predicts secondary-flow
RMS at floating-point machine precision (**~1e-15% of bulk velocity —
genuinely, exactly zero**) in both cases, while DNS shows a real
**2.07–2.22% of bulk velocity**. RANS captures **0%** of the DNS
secondary-flow magnitude in either case.

**Verdict: GATE MEASURED, FAIL — reported as measured, not shipped as a
pass.** This is the expected, literature-consistent structural limitation
of the linear Boussinesq eddy-viscosity closure (no mechanism for Prandtl's
secondary flow of the second kind), and it is the physical mechanism
directly responsible for `AR_1_Ret_360`/`AR_3_Ret_360` being the two
largest single contributors (31.5%, 31.4%) to our measured closure-challenge
deficit: the correction these cases need is not a refinement of an
already-reasonable RANS field, it is the entire secondary-flow structure,
supplied from zero.

Full report: `demo-output/website/dafoam/f6c_duct_dns/F6c_duct_vs_dns.md`

## F6b — Periodic hills

**Not attempted this session.** Per docket priority order, F6b was
explicitly conditional on time remaining after F6a and F6c were fully
climbed and gated. Both were completed to the gate rung with solid,
independently cross-checked results; the remaining session budget was spent
writing up and cross-validating those results rather than opening a third
family. No feasibility rung was started for F6b.

## What's blocked / next

- **F6a**: velocity-profile and Reynolds-stress comparison at the case's
  own sampling stations (`x/c=0.65…1.3`) not attempted — out of the ordered
  gate's scope (separation/reattachment/Cp). Cp-reference-pressure
  convention not independently verified against NASA's own method.
- **F6c**: `AR_14_Ret_180` (third duct test case on the leaderboard) has no
  reproduced baseline yet — case files exist in the benchmark clone,
  flagged for a future rung; not prioritized this session since it is not
  named in the docket's measured-deficit breakdown. Spatial vortex-pattern
  comparison (vs bulk RMS magnitude used here) not attempted.
- **F6b**: entirely unstarted. Next session should open with a feasibility
  rung on a single periodic-hill case before deciding whether it is worth
  climbing further, per staging doctrine.

## Evidence files

- This report: `demo-output/website/campaign/F6_closure_aligned_flows.md`
- Machine-readable: `demo-output/website/campaign/F6_closure_aligned_flows.json`
- F6a: `demo-output/website/dafoam/f6a_nasa_hump/{F6a_nasa_hump.md,F6a_nasa_hump.json,case/,nasa_experimental_reference/}`
- F6c: `demo-output/website/dafoam/f6c_duct_dns/{F6c_duct_vs_dns.md,F6c_duct_vs_dns.json,*.json,secondary_flow_gate.py}`
- F6c source RANS fields (from B2): `demo-output/website/dafoam/ladder-b/duct_baseline/`
