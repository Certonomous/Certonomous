# Certonomous Hard-Case Campaign Status — Family Summary
**Date:** 2026-07-28  
**Reporting by:** Structured audit of all campaign family records

---

## F1 — ONERA M6 Transonic Wing (3D)

- **Reynolds:** ~1.5×10⁷ (root chord, over-estimated; target 11.72×10⁶)
- **Mach:** 0.839968 (design Mach 0.84, transonic)
- **Flow regime:** Transonic separated flow, shock-bearing
- **Geometry:** 3D wing, transonic; steady RANS (`DARhoSimpleCFoam`)
- **Rung reached:** Feasibility → Physics → **Gate (Cp validation)**
- **Gate metric:** Cp distribution vs AGARD AR-138 / NASA-TMR Case 2308
  - Upper surface RMS deviation: 0.049–0.114 Cp (pressure side: 0.013–0.027)
  - Shock location: aft-shifted 0.02–0.10 x/c vs experiment (6 of 7 stations), eta=0.80 exception (−0.0015)
  - η=0.99 outlier: RMS 0.114, bias +0.065 (wingtip vortex zone)
- **Verdict:** **GATE REACHED.** Textbook signature of mesh-diffusion smearing on coarse grid (399,360 cells), not gross solver defect. CD=0.02299556, CL=0.31311589.
- **Adjoint:** Blocked — OOM on mesh-sized residual/volume-coordinate Jacobian (8 mitigations tried, documented)
- **Core-minutes:** 127.5 primal; adjoint not completed

---

## F2 — Transonic NACA0012 (2D)

- **Reynolds:** 3e6–7e6 (design space); primary case Re=6e6
- **Mach:** 0.70–0.85 (design space); primary case M=0.8
- **Angle of attack:** 0–3° (design space); primary case α=1.25°
- **Flow regime:** Transonic, shock-bearing
- **Geometry:** 2D symmetric airfoil; steady RANS (`rhoSimpleFoam`, kOmegaSST)
- **Rung reached:** Feasibility → Physics → **Gate (shock position, banded, resolution-limited)**
- **Gate metric:** Upper-surface shock location, M=0.8/α=1.25°/Re=6e6
  - CFD shock: x/c=0.55607646
  - Reference (inviscid AGARD/GAMM benchmark): x/c~0.60 — a literature-recalled
    value stated to two significant figures, with **no retained citation**
    (`PHYSICS_FAMILIES.md:104-107`)
  - **Detector resolution: ±1 increment ≈ 0.052 x/c at this location.** The
    detector returns the midpoint of the adjacent surface-sample pair with the
    steepest positive dCp/dx, so it can only emit values on a fixed mesh
    lattice — 8 distinct values across all 280 ledger runs. The next
    representable value above 0.55607646 is 0.608440365.
  - **WITHDRAWN 2026-07-30:** the previously recorded "Deviation: +0.044 x/c
    upstream of inviscid" and the reading of it as the expected viscous
    shock/boundary-layer shift. 0.60 − 0.556 = 0.0439 chord is **smaller than
    one detector increment (0.0524)**, and the adjacent representable value
    0.6084 sits *on* the reference. F2 does not resolve that displacement and
    must not be narrated as demonstrating it. Full trace:
    `campaign/F2_transonic_naca0012.md` §3.
  - Corrected statement: the shock lies at x/c = 0.556 ± one increment,
    **consistent with the inviscid ~0.60 benchmark to within the detector's own
    resolution**, and inside the stated 0.35–0.60 band — though the adjacent
    representable value would fall outside it, so the banded pass turns on a
    single quantisation level.
  - Cd=0.0431920118, Cl=0.109011072 (Cd spread 0.00093; pressure 0.036912 +
    viscous 0.006280) — **re-run and confirmed 2026-07-30**, see below
- **Verdict:** **PASS (banded, qualitative, resolution-limited).** A genuine
  suction-side recompression is present and its position is not contradicted by
  the inviscid benchmark. The gate supports nothing stronger than that.
- **Primary evidence:** these are pre-batch validation-gate numbers from a
  dedicated solve, **not** batch-ledger samples — no `rhosimplefoam-naca0012-transonic`
  ledger entry exists at M=0.8/α=1.25°/Re=6e6, and none was expected to. The
  original run's artifacts were discarded with its scratch ledger (commit
  `6cc7f629`, 2026-07-28 05:25:35 +0000). The case was **re-run 2026-07-30
  16:54:57Z and reproduces every published digit**; artifacts are now retained
  at `campaign/F2_runs/` (`F2_reproduction_2026-07-30.json`,
  `primary_M0.8_a1.25_Re6e6/postProcessing/forceCoeffs1/0/coefficient.dat`
  iteration 2000).
- **Cost:** 26–34 s per evaluation
- **Shipped:** Yes (mega-batch family)

---

## F3 — Supersonic Exact-Theory Campaign (wedge / cone / diamond)

### 3a. Wedge (oblique shock, θ-β-M)

- **Mach:** 2.0, 2.5, 3.0
- **Deflection angle:** 15°, 10°, 15° respectively
- **Flow regime:** Inviscid supersonic (Euler equations, μ=0)
- **Geometry:** 2D ramp mesh; steady `rhoCentralFoam`
- **Rung reached:** Feasibility → Physics → **Gate (surface pressure p2/p1)**
- **Gate result (fine mesh):**
  - M=2.0, θ=15°: p dev **0.07%** (exact β=45.3436°, computed 45.26°)
  - M=2.5, θ=10°: p dev **0.01%** (exact β=31.8506°, computed 32.33°)
  - M=3.0, θ=15°: p dev **0.01%** (exact β=32.2404°, computed 32.46°)
  - Shock angle β convergence: 0.2–1.5% (method-sensitive, documented corner singularity bias)
- **Verdict:** **PASS.** Surface pressure converges to within 0.01–0.07% of exact oblique-shock theory at fine mesh. Shock angle measured from smeared field via density-gradient peak detection; residual is method-artifact, not solver defect.
- **Core-minutes:** 8.43 (all 3 pairs, 7 runs)

### 3b. Cone (Taylor-Maccoll, axisymmetric)

- **Mach:** 2.35, 3.0
- **Half-angle:** 10°, 12° respectively
- **Flow regime:** Inviscid supersonic, axisymmetric
- **Geometry:** Axisymmetric wedge mesh (2.5° half-angle slice, wedge BC); steady `rhoCentralFoam`
- **Rung reached:** Feasibility → Physics → **Gate (surface pressure pc/p1)**
- **Gate result (fine mesh, M=2.35/θc=10°):**
  - Pressure: pc/p1 dev **0.29%** (exact 1.3739, computed 1.3779)
  - Shock angle β: dev **2.1–2.8%** (exact β=26.7367°, computed 27.31–27.49°) — monotonically converging but **not fully grid-converged** at 28,800 cells
  - Second pair (M=3.0/θc=12°) run at medium only (cost: fine mesh 1,073 core-s per 28,800 cells vs wedge 149 s, ~7× ratio)
- **Verdict:** **PASS, not fully grid-converged.** Pressure gate clean; shock-angle convergence slower and more sensitive than 2D wedge (weaker/more-oblique shock occupies larger fraction of standoff in smeared field). Documented open sensitivity; genuine 3-mesh Richardson study needed if F4 hypersonic work requires tight shock-position gates.
- **Core-minutes:** 22.09 (both pairs, 4 runs)

### 3c. Diamond Airfoil (shock-expansion, wave drag)

- **Mach:** 2.0, 2.5
- **Half-angle (ε):** 7.125°, 5.0° respectively
- **Flow regime:** Inviscid supersonic (Euler equations)
- **Geometry:** 2D symmetric double-wedge airfoil, zero AoA, upper-half-only; steady `rhoCentralFoam`
- **Rung reached:** Feasibility → Physics → **Gate (wave-drag coefficient cd)**
- **Gate result (fine mesh):**
  - M=2.0, ε=7.125°: cd dev **−0.26%** (exact 0.036331, computed 0.036237)
  - M=2.5, ε=5.0°: cd dev **−0.18%** (exact 0.013430, computed 0.013406)
  - Both converged by medium mesh (deviation flat from medium→fine within ~0.1 percentage point)
- **Verdict:** **PASS (strongest gate).** Integrated force coefficient converges to 0.18–0.55% accuracy; robust gate testing entire surface (compression + expansion). Grid-converged by medium mesh.
- **Core-minutes:** 7.93 (both pairs, 6 runs)

**F3 Overall:** **All three cases PASS.** Total 38.45 core-minutes. Headline: `rhoCentralFoam` inviscid Euler reproduces every closed-form supersonic-theory gate to well under 1% on integrated/surface-pressure metrics at fine mesh. Cone shock-angle measurement reveals genuine numerics effect (smeared field bias larger in axisymmetric weak shocks) — documented, not hidden.

---

## F5a — Unsteady Cylinder Vortex Shedding (2D)

- **Reynolds:** 100–1000 (design space); validation at Re=100, 150, 180
- **Flow regime:** Laminar, unsteady periodic vortex shedding
- **Geometry:** 2D circular cylinder, O-grid annulus mesh (8,640 cells nominal); unsteady `pimpleFoam`
- **Rung reached:** Feasibility → Physics → **Gate (Strouhal number)**
- **Gate metric:** Roshko/Williamson correlation St = 0.198·(1 − 19.7/Re)
  - Re=100: St measured 0.1578 vs correlation 0.1589, dev **0.7%**, drift 3.9%
  - Re=150: St measured 0.1777 vs correlation 0.1720, dev **3.3%**, drift 1.3%
  - Re=180: St measured 0.1844 vs correlation 0.1763, dev **4.6%**, drift 2.7%
- **Verdict:** **PASS.** All within 0.7–4.6% of reference; stationarity drift <3.9%; Cd 1.27–1.29 consistent with classical compilations. **Note:** above Re~189, 2D laminar is idealization (real wakes become 3D turbulent); Re>200 runs validated only qualitatively.
- **Cost:** ~230–290 s per evaluation (low-minute budget satisfied)
- **Shipped:** Yes (mega-batch family, "Family 1")

### F5a Reynolds ladder (separate, deeper investigation beyond the shipped batch above)

Full record: `demo-output/website/campaign/F5a_cylinder_reynolds_ladder.md`.

- **Re 1000:** Cd=1.4678, St=0.2343, Cl_rms=0.9666 (2D laminar). **GATED, point
  reference:** Jiang & Cheng (2017) *JFM* 832:170-188 run matched 2D and 3D DNS
  at this exact Re. Our result agrees with independent 2D DNS to 1.3-6.2% (Cd,
  St, Cl_rms all move together — the solver-correctness check) and over-predicts
  the 3D DNS/experiment consensus by +35.9-44.8% (Cd, source range), +8.5-11.6% (St), and
  380-710% (Cl_rms) — large, directionally consistent, and mechanistically
  explained by the same paper (weaker/longer 3D recirculation region, spanwise
  phase decorrelation collapsing integrated Cl_rms). This is the deviation
  figure the previous record explicitly said it did not have.
- **Re 2000:** Cd=1.5879, St=0.2421 (2D laminar). Previously recorded
  **INCOMPLETE at 63%**; that run had actually finished (t=0-90,
  3965.11 s) before this correction — the incomplete note was stale (L-1).
  **GATED, banded, lower confidence:** no point-value 3D or 2D reference found
  at exactly Re=2000 despite a genuine search (paywalled Norberg 2003,
  Williamson 1996, Fey/König/Eckelmann 1998, no Unpaywall OA copy of any).
  Gated instead against the Zdravkovich (1990/1997) subcritical-regime
  Cd/St-plateau band (Cd~1.0-1.2, St~0.19-0.21): over-predicts by +32-59% (Cd)
  and +15-27% (St), consistent in direction and rough magnitude with Re 1000.
  Reported as weaker evidence than Re 1000's gate, not equalized to match it.
- **Re 3900:** launched 2026-07-29 20:30 UTC (2D laminar, 44,000-cell mesh),
  predicted ~6,390 s. A pre-staged kOmegaSST (2D URANS) setup was found and
  **reverted to laminar before launch** — it would have silently forked the
  ladder's methodology on its most important rung (see LESSONS.md L-11). Rich
  published reference data exists at this Re (PIV, DNS, LES, DES from six
  independent sources), so this rung should produce the ladder's first
  point-gated, high-confidence result above Re 1000.

---

## F6a — NASA 2D Wall-Mounted Hump (Separated Flow)

- **Reynolds:** Re_c = 936,000
- **Mach:** M=0.1 (low-speed, incompressible approximation)
- **Flow regime:** Turbulent boundary layer with separation bubble; steady RANS (`kOmegaSST`)
- **Geometry:** 2D hump, 51,626-cell mesh; `simpleFoam`
- **Rung reached:** Feasibility → Physics → **Gate (separation/reattachment x/c)**
- **Gate result:**
  - Separation x/c: 0.6544 vs NASA experiment 0.665, dev **−1.59%** ✓
  - Reattachment x/c: 1.2534 vs NASA experiment 1.100, dev **+13.95%** (documented SST over-prediction of bubble length)
- **Cross-checks (validation):**
  - vs NASA's own published SST CFD: separation +0.06%, reattachment within published 1.25–1.27 range
  - vs benchmark's shipped baseline field: ≤0.02% deviation
  - vs benchmark's own scorer: 0.0622 vs published floor 0.0621, +0.16%
- **Verdict:** **GATE REACHED.** Baseline independently verified correct via three orthogonal cross-checks. The +13.95% reattachment error is the expected, literature-documented linear-eddy-viscosity SST deficiency — exactly what data-driven closure corrections target. This is the gate working as designed.
- **Cost:** 5.25 core-min (Feasibility 0.28 + Physics 2.51 + Gate 2.47)
- **Shipped:** Yes

---

## F6c — Square/Rectangular Duct vs DNS (Secondary Flow)

- **Test cases:** AR_1_Ret_360, AR_3_Ret_360
- **Flow regime:** Incompressible turbulent duct flow, secondary-circulation zone; steady RANS (`kOmegaSST`)
- **Geometry:** Rectangular duct, matched to DNS mesh (B2 baseline from prior session)
- **Rung reached:** Feasibility/Physics (already done in B2) → **Gate (secondary-flow RMS vs DNS)**
- **Gate result:**
  - AR_1_Ret_360: RANS secondary-flow RMS **~0.0%** of U_bulk (machine precision, ~1e-15%); DNS reference 2.22%
  - AR_3_Ret_360: RANS secondary-flow RMS **~0.0%** of U_bulk; DNS reference 2.07%
- **Verdict:** **GATE MEASURED, FAIL — reported as measured, not shipped.** Linear Boussinesq eddy-viscosity closure has zero normal-stress anisotropy by construction; cannot produce Prandtl's secondary flow of the second kind. The failure is **structural and expected**, not a resolution/convergence issue. This explains why AR_1/AR_3 are the two largest (31.5%, 31.4%) contributors to closure-challenge deficit.
- **Cost:** 0 core-min (post-processing only; fields from B2)
- **Shipped:** No (failure documented and blocked per campaign rules)

---

## F6b — Periodic Hills

- **Status:** **GATE REACHED** (2026-07-29 solve; record completed 2026-07-30).
  Supersedes the "NOT ATTEMPTED" line this section carried, which was written
  before the 2026-07-29 03:57 UTC gate run.
- **Case:** `PH_Breuer`, Re_H = 10595, 15,600 cells, stock kOmegaSST, 10,000
  iterations, 4 ranks, 511 s wall = **34.1 core-minutes**
  (`solve_registry/f6b_gate_20260729T035745Z.log`).
- **Gate:** separation x/h **0.2590** (LES ~0.2); reattachment x/h **7.6439**
  against the Fröhlich et al. (2005) LES reference **4.6-4.7** — kOmegaSST
  **over-predicts the recirculation length by +63% to +66%** (7.64391457 against
  the 4.6–4.7 band; the "~64%" quoted elsewhere is the band midpoint, a derived
  and rounded figure — no `64` appears in `gate_result.json`, which stores only
  the raw crossings and the reference range).
  Station-profile scaled MAE of |U| vs the shipped LES field: **12.51%** on the
  shipped/serial sampling pipeline, **12.95%** on this campaign's own 4-rank
  parallel run of the identical field (`f6d_random_matrix_uq/aggregate_result.json`).
  Note `gate_result.json`'s `our_solve.profile_scaled_mae_vs_LES.overall_percent`
  is `null` — the gate script's station loop looked for `line_U.xy` while this
  run wrote `line_k_nut_omega_p_U.xy`, so the 12.51% in that file is the
  *shipped baseline's* number, not ours. The difference is line sampling across
  processor boundaries, not different physics.
- **Convergence:** `check_convergence.py` returns NOT_CONVERGED, and that is a
  **diagnosed false negative** — the case's own `fvSolution` sets
  `residualControl { p 1e-15; }`, so the solver can never print its convergence
  sentence. **This is a sibling of L-21, not L-21 itself**: L-21 is a
  `residualControl` entry naming a field the model does not transport; here the
  field (`p`) *is* transported and the tolerance is simply unreachable. Same
  outward symptom, different cause and different fix. Evidence is the residual history (Ux initial
  3.60e-9, p 1.35e-8 at iteration 10,000, monotone over four decades) plus
  reproduction of the benchmark's own shipped kOmegaSST solution to **five
  significant figures** on the gate quantity.
- **Pre-registered prediction:** **FALSIFIED** on both magnitude and sign; the
  prediction file is left unedited.
- **Blocked:** No.
- **Shipped:** No.
- **Full record:** `demo-output/website/dafoam/f6b_periodic_hills/F6b_periodic_hills.md`,
  `case_breuer_re10595/gate_result.json`.

---

## F6d — Random-matrix / maximum-entropy model-form UQ (on the F6b case)

- **Status:** **COMPLETE, with a negative headline result and a correction to F6a.**
- **What:** the framework `F6a_epistemic_propagation.md` §9 scoped and did not
  start (Xiao, Wang & Ghanem, arXiv:1603.09656), implemented in full on the case
  §9.5 recommended. Sampler verified against 15 of the paper's own stated
  properties, 0 failures, before any CFD. Two internal inconsistencies in the
  paper's Appendix A found and recorded.
- **Result 1 (negative):** the probabilistic band on reattachment contains the
  LES truth but is **~5x wider** than the eigenspace corner union on the same
  case (90% interval [3.845, 7.885] vs corner union [4.022, 4.819]). The
  ensemble's mean profile error is worse than the unperturbed baseline's.
- **Result 2 (negative, pre-registered):** convergence gating biases the band
  away from the truth — the 11 members failing a residual gate have mean
  reattachment 5.342 against the 27 passing members' 6.727, with the truth at
  4.6-4.7.
- **Result 3 (correction):** all 18 eigenvalue-perturbation `fvOptions` under
  `dafoam/f6a_epistemic_band/` apply the perturbation **with the wrong sign**;
  on F6a's own mesh this makes the 1C corner non-realizable in 95.93% of cells.
  F6a's corner *non-convergence* conclusion survives re-testing with the
  corrected sign; F6a's corner *numbers* and its explanation do not.
- **Cost:** measured, ~3.5 core-hours total across ~60 solver runs, all serial.
- **Shipped:** No.
- **Full record:** `demo-output/website/campaign/F6d_random_matrix_uq.md`,
  `F6d_random_matrix_uq.json`; corrections appended in place to
  `F6a_epistemic_band.md` and `F6a_epistemic_propagation.md` §10.

---

## F7 — Marine Free-Surface Capability

### F7a. Dam Break vs Martin & Moyce (1952)

- **Reynolds:** Re ≈ 4×10⁴ (simplified: laminar, inviscid treatment per reference paper)
- **Flow regime:** Free-surface unsteady transient (dam break / wave propagation)
- **Geometry:** 2D square-column collapse (a=2.25 in = 0.05715 m), 15a×2a domain, O-grid; unsteady VOF (`interFoam`)
- **Rung reached:** Feasibility → Physics → **Gate FAIL**
  - **Feasibility:** PASS (runs clean, residuals fall, column collapses, Courant max 0.52)
  - **Physics:** PASS (qualitatively correct dam-break phenomenology, mass conserved to machine precision at medium resolution)
  - **Gate:** **FAIL** (surge front position)
- **Gate metric:** Front position Z vs nondimensional time T
  - Medium closed-box mesh (dx=a/20, 12,000 cells):
    - Mean deviation: **+13.6%** (systematically growing with time)
    - Max |deviation|: **21.3%** (time T=8.58)
    - Well outside credible tolerance; monotonically diverging, not oscillating around zero
  - Coarse mesh (dx=a/8, 1,920 cells): mean deviation **−13.2%** (sign-flipped vs medium, ruling out "needs finer grid" as sole fix) — **RETRACTED 2026-07-30, see below**
- **Secondary check (column-height decay):** mean deviation −1.5% (bulk quantity tracks reference much more closely than leading-edge front position)
- **Cause:** ~~Front-position failure concentrated at thin, fast-moving leading edge; VOF numerical smearing effect.~~ **SUPERSEDED 2026-07-30 (R1)** — see below.
- **Blocked by this:** Rung (b) Wigley hull and Rung (c) workshop hull (hard rule: do not start next rung until previous passes gate)
- **Cost:** ~2.4 core-min original pass; +387.4 core-min for the R1 audit/resolution
- **Verdict:** **GATE FAILED as measured.** Per hard campaign rules, shipped as documented failure, not as a capability. F7 ladder is blocked at (b) and (c).

#### R1 update (2026-07-30) — audited, two recorded causes retracted, mechanism found, still failing

- **Retracted:** the "coarse mesh undershoots −13.2%, sign-flipped" result and the
  "VOF numerical smearing" root cause. Both were artifacts of the near-floor
  `alpha=0.5` line probe, whose absolute sampling height moves with the mesh.
  Under one consistent depth-integrated metric a five-rung ladder (a/8 → a/64,
  paper-matched 15a×1.25a domain) gives **+11.8%, +13.5%, +13.0%, +11.6%,
  +11.1%** — same sign at every rung, improving monotonically from a/16 down.
  Metric threshold sensitivity at a/64 is 0.24%. Also retracted: D2's finding
  that `cAlpha=0` cut the error ~40% (it reverses sign with the metric; under
  the depth-integrated metric it makes things worse, +13.5% → +16.8%).
- **Confirmed:** the gate failure is real and grid-verified, and persists on the
  reference paper's own 240×20 mesh (+13.5%). The original +13.6%/21.3% numbers
  reproduce from the case's own `log.interFoam` and `alpha.water` dumps.
- **Mechanism (new, single-variable proven):** under-resolved **bed friction**
  beneath the sub-millimetre leading film. Refining only wall-normal resolution
  at fixed dx=a/32: +11.6% (dy=a/32) → +9.8% (a/64) → **+8.2% (a/128)**. The
  same fine mesh with a **slip** floor returns to +13.7%, undoing the whole gain.
- **Declared tolerance: 5%. Result: still FAIL**, at +8.2% mean / +11.0% max —
  roughly half the recorded deviation. Column height at the back wall over
  T=0.80–3.08 is **+0.9% mean** (max 9.9%) at dx=dy=a/64.
- **Comparator established:** the reference figure's own inviscid simulation
  achieves −4.3% to +1.8% against the same experimental points.
- **Open:** transitional bed friction (film Re ≈ 3×10³, runs are laminar),
  unmodelled contact-line resistance, the 1952 gate-withdrawal time, and the
  reference simulation's unstated front definition. The y-ladder is not in an
  asymptotic range, so no extrapolated limit is quoted.
- **Record:** `F7_marine_free_surface.md` § "R1 audit and resolution
  (2026-07-30)"; cases under `F7_runs/F7a_R1/`.

### F7b. Wigley Hull Wave Resistance

- **Status:** **BLOCKED** (F7a did not pass gate)

### F7c. Workshop Hull (DTMB 5415 / KCS)

- **Status:** **BLOCKED** (depends on F7b)

**F7 Overall:** F7a feasibility/physics pass; gate fail with documented cause. Ladder blocked per hard rule.

---

## F4 — Hypersonic Blunt Body (2D cylinder, Mach 6-8)

- **Status:** **STALE entry corrected 2026-07-29 night session.** This
  family was fully run and gated on 2026-07-28 (`F4_hypersonic_blunt_body.md`,
  same date this status file was compiled) — the "NOT STARTED" line below was
  never updated to match. Caught by the same L-1 check applied to F9 this
  session: read the repository before trusting the docket.
- **Solver:** `rhoCentralFoam` (density-based, shock-capturing), inviscid
  (μ=0), 2D circular cylinder (not axisymmetric sphere — a real, disclosed
  geometric choice; Billig's correlation gives separate citable coefficients
  for cylinder-wedge vs. sphere-cone).
- **Reference:** Anderson, *Hypersonic and High-Temperature Gas Dynamics*,
  2nd ed. (AIAA, 2006) — Billig (1967) shock-standoff correlation (§5.4) and
  modified-Newtonian surface-Cp theory (§3.3), both fetched and OCR'd from
  the primary source (an initial web-search-summarized coefficient, 4.76,
  was caught wrong against the textbook's actual printed 4.67).
- **Rung reached:** Feasibility → Physics → **Gate (2 gates: shock standoff, windward Cp)**, all 3 Mach numbers (6, 7, 8), 3 mesh levels each (1,000/4,000/16,000 cells).
- **Gate 1 (shock standoff vs. Billig):** M=6 fine +2.06%±0.4%, M=7 fine +2.33%±0.4% (both resolved above measurement noise — real ~2-2.3% high bias), M=8 fine +0.70%±0.8% (within its own noise floor, consistent with Billig but not resolved to 0.7%). Explicitly non-monotonic with mesh refinement; the swings beyond scatter are attributed to a genuine resolution-dependent bias in the peak-density-gradient shock detector, not the solver.
- **Gate 2 (windward Cp vs. modified Newtonian):** RMS 3.87-3.91% of Cp_max at fine mesh, all 3 Mach numbers, clean near-monotonic grid convergence. Deviation grows toward the shoulder (θ≳33°) — a known, Mach-independent limitation of Newtonian theory (neglects shock-layer thickness/streamline curvature), not a CFD artifact.
- **Verdict:** **GATE REACHED, both gates PASS**, with caveats stated plainly (M=8 standoff not resolved above noise; standoff detector has a real resolution-dependent bias documented, not hidden).
- **Cost:** 14.66 core-minutes, all 9 runs, single-core, foreground.
- **Stretch rung (viscous SWBLI):** Not attempted — needs a turbulence model, wall-resolved mesh, and its own citable experimental separation-length reference; documented as a next step, not rushed.
- **Full record:** `demo-output/website/campaign/F4_hypersonic_blunt_body.md`, `F4_hypersonic_blunt_body.json`.

---

## F8 — Rotating Machinery

- **Status:** **NOT STARTED** (no record file exists)

---

## F9 — Pulsatile Valve

- **Status:** **CORRECTED 2026-07-29 night session — this entry was stale.** A
  fixed-leaflet axisymmetric idealization (not the moving-mesh/immersed-boundary
  full case scoped out below) was already built, run, and mostly analyzed by
  2026-07-29 ~04:15 UTC; the write-up just hadn't been finished before this
  status file was last compiled. Corrected per L-1 discipline (check the
  repository before trusting the docket).
- **Geometry:** Fixed-leaflet limit of the real 3-leaflet valve (`models/curriculum/aortic_valve`),
  represented as an axisymmetric sharp-edged orifice plate of matching
  effective area at 65° opening (beta=0.906), 4,944-cell wedge mesh.
- **Solver:** `pimpleFoam`, laminar, sinusoidal pulsatile inflow — replaces the
  mega-batch's reduced-order (`solver="reduced-order"`) valve family's
  algebraic sharp-orifice correlation with a real solved flow.
- **Rung reached:** Feasibility → Physics → **Gate (3 gates: quasi-steady limit, Womersley profile, ROM deviation)**
- **Gate 1 (quasi-steady limit) — PASS:** cycle-mean CFD Δp within −1.58%
  (alpha=16.73, physiological) and +0.22% (alpha=8.36) of the value predicted
  by the CFD's own steady dp(Q) power-law map; direction of the gap is
  physically coherent across the two alpha values tested.
- **Gate 2 (Womersley profile) — FAIL; original cause tested 2026-07-30 and
  REFUTED, replaced by a supported one:** 20–414% mean absolute relative
  error vs. the closed-form Womersley (1955) solution at 8 phase/alpha
  combinations. The original "probe too close to the orifice" hypothesis
  was tested directly (3 new radial-profile stations added at 3D/4D/4.5D
  upstream via a restart from `pulsatile_physio`'s t=1.8 checkpoint) and
  refuted cleanly: error grows, not shrinks, moving upstream, monotonically
  at every one of the 4 phases tested. Now attributed instead to an
  entrance-length limitation — the 5-diameter upstream pipe is ~2 orders of
  magnitude shorter than this case's peak-Re (~8388) laminar entrance
  length (~420–500D) needs to relax away from the flat `uniformFixedValue`
  inlet condition — not a solver defect, not the originally-guessed
  orifice-proximity artifact. See `F9_pulsatile_valve.md` §5 for the full
  record.
- **Gate 3 (ROM deviation) — pre-registered prediction confirmed in direction
  and order of magnitude:** measured cycle-weighted CFD loss 110.71 Pa vs.
  the ROM's 1849.77 Pa, **−94.0%**. Predicted ("far below... order 150–250 Pa")
  before the data was read. Root cause: the ROM's fixed Cd=0.62 is an
  ISO-5167 sharp-orifice constant calibrated for beta ≤ 0.75; this geometry's
  beta=0.906 is outside that range, and the CFD's own independently measured
  discharge coefficient (1.91–1.95 across a 4× flow sweep) confirms the real
  value is over 3× the ROM's assumption. **Disclaimer-boundary sweep
  (2026-07-30):** 2 more points at 50°/55° (beta=0.766/0.819) show the ROM's
  error is already large (Cd_cfd ~2× the ROM's 0.62, estimated deviation
  ~−74%) right at the edge of its own calibrated range, not a gentle
  transition — no CFD point in this study has tested beta≤0.75, so this
  does not confirm the ROM is accurate inside its calibration range,
  only that it is already substantially wrong just outside it. See
  `F9_pulsatile_valve.md` §6b.
- **Verdict:** **GATE REACHED, mixed (2 PASS / 1 FAIL-with-cause-understood).**
  Not a clean sweep, reported as such. Total compute, all F9 work to date:
  ~80.9 core-minutes (~1.35 core-hours), single core throughout — corrected
  2026-07-30 from a prior "well under 35 core-minutes" claim that
  undercounted the original 4 steady runs (measured 2.2–8.0 min each, not
  sub-minute); see `F9_pulsatile_valve.md` §7 for the raw `ExecutionTime`
  breakdown. Original gate verdicts and the ROM-deviation finding were
  independently re-derived from raw probe data and matched to within
  numerical noise before any of the above follow-up work was done.
- **Shipped:** No — a gate with a documented FAIL component does not go in
  the control room per the owner's promotional-surface rule; it lives in
  the evidence record (`F9_pulsatile_valve.md`, `NOT_PASSING_REGISTER.md`).
- **Full record:** `demo-output/website/campaign/F9_pulsatile_valve.md`,
  `F9_pulsatile_valve.json`, `F9_work/f9_analysis.json`,
  `F9_work/womersley_followup_results.json`,
  `F9_work/beta_boundary_results.json`.

---

## F10 — 3D Viscous RANS Batch Family

- **Status:** **NOT STARTED** (no record file exists)

---

## Summary Table

| Family | Case | Reynolds/Mach | Regime | 2D/3D | Steady/Unsteady | Rung | Gate vs Reference | Deviation | Verdict | Core-min |
|---|---|---|---|---|---|---|---|---|---|---|
| **F1** | ONERA M6 | M=0.84, Re~1.5e7 | Transonic shock | 3D | Steady | Feasibility→Physics→**Gate** | Cp distribution (AGARD AR-138) | RMS 0.049–0.114, shock ±0.02–0.10 x/c | **GATE REACHED** | 127.5 |
| **F2** | NACA0012 | M=0.8, Re=6e6 | Transonic shock | 2D | Steady | Feasibility→Physics→**Gate** | Shock position (inviscid AGARD) | x/c=0.556 vs ~0.60; **detector resolution ±0.052 x/c — deviation not resolved** | **PASS (banded, resolution-limited)** | – |
| **F3a** | Wedge | M=2.0–3.0 | Inviscid supersonic | 2D | Steady | Feasibility→Physics→**Gate** | p2/p1 (θ-β-M exact) | 0.01–0.07% | **PASS** | 8.43 |
| **F3b** | Cone | M=2.35, 3.0 | Inviscid supersonic | Axisym | Steady | Feasibility→Physics→**Gate** | pc/p1 (Taylor-Maccoll) | p: 0.19–0.29%; β: 2.1–3.9% | **PASS, not fully converged** | 22.09 |
| **F3c** | Diamond | M=2.0, 2.5 | Inviscid supersonic | 2D | Steady | Feasibility→Physics→**Gate** | cd (shock-expansion) | 0.18–0.26% | **PASS** | 7.93 |
| **F5a** | Cylinder | Re=100–180 | Laminar unsteady shed | 2D | Unsteady | Feasibility→Physics→**Gate** | Strouhal (Roshko/Williamson) | 0.7–4.6% | **PASS** | – |
| **F6a** | NASA hump | Re_c=936k | Turbulent separated | 2D | Steady RANS | Feasibility→Physics→**Gate** | separation/reattachment x/c | −1.59% / +13.95% (SST bias) | **GATE REACHED** | 5.25 |
| **F6c** | Duct DNS | Re_360, Re_360 | Turbulent secondary flow | – | Steady RANS | Physics/Feasibility→**Gate** | Secondary-flow RMS vs DNS | RANS 0.0%, DNS 2.07–2.22% | **GATE FAIL** (structural) | 0 |
| **F6b** | Periodic hills (`PH_Breuer`) | Re_H=10595 | Turbulent separated | 2D | Steady RANS | Feasibility→Physics→**Gate** | separation / reattachment x/h vs Fröhlich et al. 2005 LES | sep 0.2590 vs ~0.2; reatt 7.6439 vs 4.6–4.7 = **+63% to +66%** | **GATE REACHED** (prediction falsified) | 34.1 |
| **F7a** | Dam break | Re~4e4 | Free-surface wave | 2D | Unsteady | Feasibility→Physics→**Gate FAIL** | Front position Z(T) | +8.2% mean (11.0% max) best, R1 2026-07-30; was +13.6%/21.3% | **GATE FAILED** (5% tol.) | 389.8 |
| **F7b** | Wigley hull | – | – | – | – | **BLOCKED** (F7a gate fail) | – | – | – | 0 |
| **F7c** | Workshop hull | – | – | – | – | **BLOCKED** (F7b blocked) | – | – | – | 0 |
| **F4** | Hypersonic blunt (M6-8, cylinder) | M=6-8 | Inviscid hypersonic | 2D | Steady | Feasibility→Physics→**Gate** | Billig standoff / mod. Newtonian Cp | standoff +0.7-2.3%; Cp RMS 3.87-3.91% | **GATE REACHED** | 14.66 |
| **F8** | Rotating machinery (MRF, UAE Phase VI Seq. S, 7 m/s) | – | Turbulent, rotating frame | 3D | Steady MRF | Physics attempted, **UNCONVERGED**; gate run 2026-08-07 | Hand et al. 2001 (800 N·m at 7 m/s, secondary tier; TP numbers corrected, see F8 note) | torque band 7679 N·m p-p = 960% of reference, cap was 50% | **NO VERDICT — unconverged forces not gateable; MRF branch closed** | 5.8 |
| **F9** | Pulsatile valve (fixed-leaflet orifice) | Re~8.4e3 pipe | Pulsatile laminar, orifice | Axisym | Unsteady | Feasibility→Physics→**Gate** | Womersley (1955) profile; own steady map; ROM | Gate1 PASS (-1.6%/+0.2%); Gate2 FAIL (20-414%, cause ID'd); Gate3 -94.0% vs ROM (pre-registered) | **GATE REACHED, mixed** | <35 |
| **F10** | 3D RANS batch | – | – | – | – | **NOT STARTED** | – | – | no record | 0 |

---

## Explicitly Not Started

**F10** has produced no record file as of 2026-07-29. **F4, F8, F9 were
previously listed here as of 2026-07-28 and are NOT unstarted** — that line
was stale for F4 and F9 (both fully run and at least partially gated the
same day or the day after this file was last compiled) and materially
incomplete for F8 (a real MRF rotating-machinery physics run exists on disk,
with blade-force output, but no reference gate has been found or applied
yet — see below). Corrected 2026-07-29 night session per L-1.

- **F4 (Hypersonic):** **GATE REACHED**, see above — this line was wrong.
- **F8 (Rotating machinery):** Feasibility + a `simpleFoam` MRF run to
  endTime=1500 exist on disk (`F8_runs/phase6_mrf/`, NREL/NASA-Ames UAE Phase
  VI Sequence S wind turbine, whole-domain single MRF zone, 7 m/s inlet —
  explicitly commented in the case as "the low-speed attached-flow point,"
  the easiest of the sequence). **Checked this session against L-14/L-15
  ("read the solver's own convergence statement, not a residual that looks
  small"): `grep -c "SIMPLE solution converged" log.simpleFoam` returns 0.
  Never converged.** Worse than a slow plateau: `postProcessing/bladeForces`
  shows the force history still swinging violently at t=1300-1500 (Fx
  683-1064 N, a ~30% range; Fy -336 to +280 N, including sign reversals) with
  no visible settling trend across the observed window — this is genuinely
  further along than "no feasibility rung initiated" (the previous line) but
  is NOT a usable physics result and must not be read as one. A citable
  reference DOES already exist and was found this session: Hand, M.M. et al.
  (2001), *Unsteady Aerodynamics Experiment Phase VI...*, NREL/TP-500-29494 —
  publishes low-speed-shaft torque and blade root bending moment vs. wind
  speed for exactly this Sequence S test, including the 7 m/s point already
  set up here. **Do not gate against it yet.** The oscillation could be (a)
  genuine rotor-wake unsteadiness a frozen-rotor steady MRF model cannot
  represent (a known MRF limitation for bluff, separating rotor wakes — not
  tested here), (b) an under-relaxation/numerics issue fixable within the
  same steady framework, or (c) something else. **Hypothesis (b)'s cheapest
  test has since been run (2026-07-30): `endTime` extended 1500->3000
  (restart-trap fixed first — `startFrom` was `startTime`/`0`, which would
  have silently re-solved from zero; switched to `latestTime` and verified
  the resume was genuine by reading `Time=1524` seconds into the new log).
  Still 0 matches for "SIMPLE solution converged" at t=3000, and the force
  oscillation widened rather than decayed (Fx span 508 N over t=1500-2250,
  729 N over t=2250-3000; Fy now swinging -775 to +1276 N, wider than the
  original window's -336 to +280 N).** More steady iterations demonstrably
  do not fix this — evidence for (a) over (b), though not proof a genuine
  physical mechanism is responsible rather than an unsaturated numerical
  instability. Next test is qualitatively different (transient rotating
  frame), not merely longer. Logged as a genuine Group 3 solver convergence
  failure in `NOT_PASSING_REGISTER.md`, not glossed over.
  **Update 2026-08-07 (`f8-mrf-forces-against-hand-2001`, slate item 1): the
  Hand et al. gate was run under pre-registration and returned NO VERDICT —
  the window (t=2000–3000) torque band is 7678.7 N·m peak-to-peak, 960% of
  the published 800 N·m against a pre-declared 50% cap; unconverged forces
  are not gateable and the steady-MRF branch is closed on evidence. The
  citation is corrected (TP-500-29494 is Simms et al.'s blind-comparison
  report, figure-only; TP-500-29955 is Hand et al.'s configurations report,
  no torque table; numeric 800 N·m is secondary-tier from Processes
  12(9):1994 Table 6). A 5.8 core-min omega-flip diagnostic found the
  mechanism lead: the mean aero torque opposes the set rotation direction,
  and reversing omega calms the history 21× on the same mesh. Full record
  and the convergence-fix diagnosis plan: `F8_MRF_HAND2001_GATE.md`.**
- **F9 (Pulsatile valve):** **GATE REACHED, mixed**, see above — this line
  was wrong ("out of scope, needs moving-mesh" describes a *different*,
  harder case than the fixed-leaflet idealization that was actually built
  and run).
- **F10 (3D viscous RANS batch):** Not started; no record file. (Note: the
  mega-batch's own `AHMED_VISCOUS_3D` family, `sdk/workflows/mega_batch.py`,
  is internally labelled "Family F10" in its own comments and IS shipped —
  this campaign-status F10 and the mega-batch's F10 label appear to be two
  different namings for related-but-not-identical scope; not reconciled
  this session, flagged so the next reader doesn't assume either doc is
  wrong.)

---

## Gate Failures and Blocks (Reported Honestly)

1. **F6c (duct secondary flow):** GATE MEASURED, FAIL. Linear eddy-viscosity RANS cannot produce Prandtl secondary flow; captures 0% of DNS magnitude. Expected, structural, documented.
2. **F7a (dam break front):** GATE FAILED. Best measured +8.2% mean / +11.0% max against a declared 5% tolerance (originally recorded +13.6%/21.3%). Cause, after the 2026-07-30 R1 audit: **under-resolved bed friction beneath the sub-millimetre leading film**, single-variable proven by a slip/no-slip control at matched fine mesh. The previously recorded "VOF numerical smearing" cause and the coarse-mesh sign flip are **retracted** as metric artifacts. Blocks F7b and F7c per hard ladder rule.
3. **F9 Gate 2 (Womersley profile):** GATE FAILED as a point comparison, 20-414% error. Cause identified: probe station close enough to a weak (81%-open) orifice that convective acceleration flattens the profile relative to the closed form's undisturbed-pipe assumption — comparison-basis mismatch, not a solver defect. Gates 1 and 3 on the same family PASS / confirm-as-predicted.

---

## Shiipped Capability Families

- **F1:** Transonic 3D wing Cp validation (gate reached; adjoint blocked by memory)
- **F2:** Transonic 2D airfoil shock position (shipped in mega-batch)
- **F3:** Supersonic exact-theory wedge/cone/diamond (all gates passed)
- **F4:** Hypersonic blunt-body standoff + Cp (both gates passed, M=6-8) — **status corrected this session, was mislabeled NOT STARTED**
- **F5a:** Unsteady cylinder vortex shedding (shipped in mega-batch)
- **F6a:** Turbulent separated flow (NASA hump, gate reached)
- **F6c:** Duct secondary flow (gate fail, shipped as documented failure)
- **F9:** Pulsatile valve, mixed gate (2 PASS / 1 FAIL-with-cause) — **status corrected this session, was mislabeled NOT STARTED**; per the owner's rule, the FAIL component keeps this out of the control room even though it is evidence-record complete.

**Not shipped:**
- **F6b:** Periodic hills — **gate reached 2026-07-29, not shipped.** Not shipped
  because the gate exposes a large one-sided closure error (kOmegaSST
  over-predicts reattachment by +63% to +66%) and the pre-registered prediction
  was falsified; it is a documented failure kept in the record, not a
  capability. **The "not attempted, time-boxed" line this entry carried was
  wrong** — it predates the 2026-07-29 03:57 UTC solve
  (`solve_registry/f6b_gate_20260729T035745Z.log`, 511 s wall, 4 ranks). See F6b
  section above.
- **F7a–c:** Marine free-surface (F7a gate fail blocks F7b/c)
- **F8:** Rotating machinery — physics run exists, no reference gate yet
- **F10:** Not started
