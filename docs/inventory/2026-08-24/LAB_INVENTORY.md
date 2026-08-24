# Lab inventory — what was run, what the lab can do, what is missing

**Written 2026-08-24T17:15Z by the chief (certonomous-d6), synthesised from six read-only
sweeps of the committed record (verification/campaign, cases/, F14 cooling ladder,
closure ladders, DAFoam ladders, UQ machinery).** Sanaa's request, verbatim: *"For each of
the following, I need a bullet point list of the cases that were ran, the lab's capability,
and what is missing: 2D CFD, all regimes, 3D CFD, all regimes, DAFOAM adjoint optimization,
Closure modeling challenge, Epistemic uncertainty/ Parametric uncertainty, Heat transfer
(all regimes). I want an inventory of what was ran for each 2D/3D-regime type so I know
where to have the lab focus on next."*

**Reading rules.** Verdicts are quoted as written in the record. "Validated" below means
exactly one thing: **PASS against a pre-registered gate, with the pre-registration on
disk.** Many early PASS/GATE REACHED words predate the pre-registration regime and are
marked *(no prereg)* — they are results, not credentials. Costs are core-minutes at
$0.0513/core-h, reported-by-owner, not measured. Nothing here is a new result.

---

## 1. 2D CFD — all regimes

### Cases run
- **Laminar, steady, internal:** F11 lid-driven cavity (Ghia 1982), Re 100 and 1000, two meshes each — GATE REACHED on both rungs *(no prereg; explicitly code verification, not validation)*. `verification/campaign/F11_lid_driven_cavity_ladder.md`
- **Laminar, steady, external:** mega-batch cylinder Re 10–45, 69,081 evaluations — ledger only, ungated. `cases/mega-batch/BATCH_INVENTORY.md`
- **Laminar, unsteady, external:** F5a cylinder Re 100/150/180 PASS *(no prereg)*; Re 1000 GATE REACHED; Re 2000 "gated, banded, lower confidence"; Re 3900 GATE REACHED (provisional — a model-deviation measurement, not a validation). R7 Strouhal mesh-spacing twin at Re 1000: G1/G2/G3 PASS, 47.3 core-min. `F5a_cylinder_reynolds_ladder.md`, `R7_STROUHAL_SPACING_RESULTS.md`
- **Laminar, unsteady, internal (axisymmetric):** F9 pulsatile valve — feasibility/physics/periodicity PASS, Gate 1 PASS, Gate 2 (Womersley) FAIL with cause identified (entrance length); Roache triple refuses — not in the asymptotic range, grid uncertainty ~20 %. 51.6 core-min. `F9_pulsatile_valve.md`
- **Turbulent RANS, steady, external, incompressible:** F6a NASA hump GATE REACHED (separation −1.6 %, reattachment +13.9 % = documented SST bias), 5.25 core-min; W1 hump at challenge conditions (Gate V PASS, separation PASS, reattachment FAIL +13.9 %); W1 a1-limiter arm ("the limiter is a mechanism", 20.7 core-min, cost gate FALSE); QCR2000 arm null; W1 bump on NASA's own grids (pressure order does not return — CFL3D's own ladder inconclusive too; viscous drag agrees with CFL3D to 0.04 %); 4G TMR aspect-ratio (GCI numerically meaningless on those ladders; helper used the 3D r-formula on 2D grids); DPW8_V2 Joukowski L1/L3 PASS, L4 BLOCKED (SIGFPE); MODEL_FORM band, 36 cells (4 of 9 groups 0 converged, excluded), 101.5 core-min; W3 NACA0012 published verdict NOT REPRODUCIBLE at 140k cells. `F6_closure_aligned_flows.md`, `W1_*`, `4G_tmr_mesh_aspect_ratio.md`, `DPW8_V2_*`, `MODEL_FORM_BAND.md`
- **Turbulent RANS, steady, internal:** F6b ERCOFTAC periodic hills (Gate V PASS 0.043 %, Gate P FAIL +63 % vs LES, Gate Q PASS, ~40 core-min); F5c backward-facing step GATE NOT REACHED (x_r off 4–12×; later found both records read the linear solver's final residuals — the convergence claim was wrong); F5c lever isolation (relaxation attributable, SIMPLEC misattributed); W2 SpaRTA frozen CBFS/PH PASS (27.7 core-min) and regression PASS (137 core-min); B2 CBFS baseline PASS reproduced. `F6b_ERCOFTAC_RESULTS.md`, `F5bc_unsteady_statistics.md`, `W2_SPARTA_*`
- **Turbulent, unsteady (URANS):** F5b pitching NACA0012 dynamic stall — feasibility PASS, physics PENDING, **no gate exists** (reference NOT OBTAINED), 0 core-min; TMR C4 NACA0012 time-accurate — budget short by 1–3 orders of magnitude. `F5b_PHYSICS_PREREGISTRATION.md`, `cases/tmr/C4_naca0012_closure.md`
- **Compressible, transonic:** F2 NACA0012 M 0.8 PASS (banded, qualitative, resolution-limited) *(no prereg)*; mega-batch rhoSimpleFoam transonic 142 evaluations (ledger); F12 RAE 2822 AGARD Case 9 PENDING — prereg only, no solver launched (est. 12–219 core-min). `F2_transonic_naca0012.md`, `F12_PREREGISTRATION.md`
- **Supersonic, inviscid:** F3 wedge M 2–3 and diamond airfoil PASS ×5 gates (38.5 core-min, 17 runs); F3 cone (axisymmetric) PASS, not fully grid-converged *(all no prereg)*; DMR double Mach reflection M 10 — Gate V PASS both rungs, P1 FAIL as registered (2.4 core-min). `F3_supersonic_exact_theory.md`, `DMR_RESULTS.md`
- **Hypersonic:** F4 blunt cylinder M 6/7/8 — standoff PASS 0.7–2.3 % vs Billig, Cp PASS, standoff non-monotonic under refinement (14.7 core-min) *(no prereg)*; F4 SWBLI cylinder-flare M 7.05 (viscous, axisymmetric) — SIGFPE then persistent energy defect; step-0/1 arms launched and COMPLETE 2026-08-24, NOT GRADED. `F4_hypersonic_blunt_body.md`, `F4_SIGFPE_STEP01_PREREGISTRATION.md`
- **Multiphase VOF free surface:** F7a dam break (Martin & Moyce) — feasibility PASS, GATE FAIL (+8.2 % mean / +11.0 % max vs 5 % tolerance; re-gate stands); family total 387 core-min. `F7_marine_free_surface.md`
- **Buoyancy-coupled 2D:** see §6 (heat transfer).

### Capability (each proven by an artifact)
- Solvers exercised and gated: simpleFoam, pimpleFoam, rhoSimpleFoam, rhoCentralFoam (Kurganov), interFoam, buoyantBoussinesqSimpleFoam; moving mesh (solidBody oscillation, F5b); NASA PLOT3D grid import (W1).
- Turbulence models run: kOmegaSST (+a1 sweep, +QCR2000), SA, kEpsilon, realizableKE, kOmega, LienCubicKE, LRR/SSG/EBRSM Reynolds-stress models, custom frozen/corrected SST and the SpaRTA-discovered model (kOmegaSSTSparta).
- Comparators with planted controls and refuse-rather-than-degrade; frozen pre-registration for every case since ~2026-08-08; draw-scatter law (VERIFICATION §17) for ladder features; mesh birth-certificate audit (400+ meshes).
- Reference-quality comparisons: exact theory (F3, F11 Ghia, DMR), CFL3D/FUN3D (W1, 4G, MODEL_FORM), LES/DNS (F6b, hump), experiment (F5c, F7a).

### Missing
- **Grid convergence:** no 2D aerodynamic case has a CONVERGING Roache triple with a quoted GCI — ladders exist (F3, F4, F6b, W1, 4G) but the GCI machinery is armed only on the thermal family; F9's triple refuses; the TMR bump's pressure drag has no observed order even on NASA's grids.
- **Validation credentials:** the early PASSes (F2, F3, F4, F5a Re100–180, F11) have no pre-registration on disk — results, not credentials; re-registration with the frozen comparator would convert them cheaply (all under 40 core-min each).
- **Regimes never gated:** URANS/unsteady turbulent (F5b has no reference; TMR C4 unaffordable); transitional flow (none); LES/DNS (none); viscous supersonic (SWBLI at the SIGFPE wall); transonic viscous with experiment (F12 RAE 2822 unrun); reacting/combustion (none); non-Newtonian/compressible multiphase (none).
- **Known wrongs on the record:** F5c backstep convergence claim (residual misread); 4G's helper formula; three bare `FAIL` ledger cells (D-5, now ruled — correction owed by owners).

---

## 2. 3D CFD — all regimes

### Cases run
- **Turbulent RANS, steady, external (bluff/aircraft):** B-52 rungs 6/7/8 + replicates — rung 7 prediction scored FALSE, rung 8 hypothesis REFUTED, turn closure INDETERMINATE then WITHDRAWN (8 draws), ~65 core-min across legs; 113 hash-suffixed B-52 study dirs outside git without per-run verdicts. R4 Ahmed 25° asymptotic ladder, 5 rungs 79k→834k cells — **no asymptotic range** (non-monotone, Richardson extrapolate is negative drag); G1/G2 met, G4 scored FALSE; 267 core-min spent on a refused fifth rung; draw-scatter legs DISSOLVE (no SIGNAL verdict). W3 cube settle (predictions scored FALSE, 68.5 core-min); W3 NACA0012/4412 wing families ("the turn does not survive" — increments swamped by mesh scatter above ~358k cells, ~70 core-min); NACA0015 sail coarse PASS (DAFoam, 64.5 core-min); NACA4412 wing primal PASS, adjoint BLOCKED. `B52_*`, `R4_ASYMPTOTIC_RESULTS.md`, `W3_*`
- **Turbulent RANS, steady, internal:** F6c/D5 square duct secondary flow — GATE MEASURED, FAIL (Boussinesq closures have no secondary flow); RSMs 52–207 % vs DNS **with the caveat that the three RSM logs on disk are copies of the SST donor's log**; B2 ducts AR1/AR3 PASS reproduced (0.16/0.64 % from published floor); W3 QCR duct falsifier — structural claim confirmed. `F6c_duct_vs_dns.md`, `D5_RSM_RESULT.md`
- **Rotating machinery (MRF):** F8 UAE Phase VI rotor vs Hand 2001 — "NO VERDICT, and that is the result": forces still oscillating, settled by rule with the wrong sign, NO MILESTONE (19.4 core-min). `F8_MRF_HAND2001_GATE.md`
- **Compressible transonic 3D:** A3 ONERA M6 primal GATE REACHED (adjoint BLOCKED); A6 CRM wing primal matches the tutorial to 0.0067 %; A2 MACH wing PASS — all DAFoam, see §3.
- **High-lift / committee grids:** HLPW6 case 1 feasibility — memory PASS, second-order diverges at iteration 16, only first order completes: not a defensible submission (est. 6,390 core-min at 14 ranks); DPW5/HLPW6 numerics probe (12 hardened batches, diagnosis record only). `cases/hlpw6/`, `cases/committee-grids/`
- **Laminar unsteady 3D:** F5b cylinder Re 100 3D pilot — feasibility PASS, physics/gate PENDING.
- **Multiphase 3D:** F7b Wigley hull and F7c DTMB 5415/KCS — BLOCKED behind F7a's GATE FAIL.
- **Panel/vortex-lattice:** mega-batch VSPAERO wing, 69,010 evaluations (ledger; inviscid).
- **3D thermal:** T10a sphere/box radiation enclosures, T9a fin, T1b pipe — see §6.

### Capability
- Meshing: blockMesh, snappyHexMesh, pyHyp, UGRID/CGNS import; mesh birth-certificate audit; generator-pathology matrix (GEN_ALT).
- Parallel: scotch/simple decomposition with the decomposition effect measured and disclosed (DAFoam §5; A4 10 % artifact found); memory guards and launch gates; replicate-scatter methodology (four-for-four table in VERIFICATION §17).
- MRF machinery exists (F8) — unsettled, not validated.
- Repeatable large runs: the 30-GiB box handles ~580k-cell RANS primals; the lab knows exactly where the adjoint memory wall is (§3).

### Missing
- **No 3D case has a CONVERGING Roache triple.** Every 3D ladder is non-monotone or scatter-dominated (Ahmed, B-52, wings, cube). This is the single largest gap against the lab's own verification law.
- **No 3D PASS against experiment with a pre-registration on disk** outside DAFoam gradient rows and B2's reproduction — the bluff-body work produced falsified predictions and withdrawn features, honestly, but no credential.
- Regimes never run in 3D: LES/DES (none), unsteady turbulent (none graded), free-surface hulls (blocked), rotating machinery (unsettled), supersonic/hypersonic 3D (none), transitional (none), internal turbulent with heat transfer beyond T1b/T3 (2D).
- HLPW6/DPW committee-grid runs are not defensible (second order diverges) — the lab cannot yet reproduce a workshop case at its own stated order.

---

## 3. DAFoam adjoint optimisation

### Rungs run (SHIPPED / PATCHED rows never blended — DAFoam charter R11)
- **A1 NACA0012 (2D):** shipped GATE FAIL (CD/shape 11.43 %, one sign flip); patched PASS 0.038 % (301× improvement). 3.5 core-min.
- **A2 MACH wing (3D, M 0.3):** gradient PASS both rows (1.71 % → 0.051 %); 105-DV table with 7 of 96 CD components beyond 15 % (idx46 sign-flips patched); optimisation NOT A RESULT (wall-clock stopped, 28.3 % drag cut at 47 majors). 692.5 core-min incl. 207 wasted.
- **A3 ONERA M6 (3D transonic):** original adjoint BLOCKED (OOM; predicted serial peak 66–94 GiB vs 24 GiB gate); primal GATE REACHED; sweep rung 1 PASS / rung 2 PASS (tightest stock numbers, 0.0077 %) / rung 3 GATE FAIL (stagnation); patched rung 2 is the **first row where the rotation patch degrades a gradient** (D462); patched rung 1 dual reading PASS-per-component vs FAIL-aggregate → **D485, Sanaa's call**; patched rung 3 NOT A RESULT (stopped by memory at 85 s).
- **A4 Ahmed body (3D):** gradient PASS 1.10 % shipped, 0.0005 % patched; the published 10 % was a scotch-decomposition artifact; **first optimisation converged** (IPOPT optimal, −7.48 % CD, endpoint gradient 0.49 %/0.31 %); trivial-baseline control behaved.
- **A5 U-bend (3D internal):** shipped GATE FAIL 46.8 % with two sign flips; patched PASS 2.77 %; idx16 shown to be an FD-reference defect, not a second solver defect (0.10 % patched vs corrected FD).
- **A6 CRM wing (3D transonic, 579k cells):** full-size adjoint BLOCKED on memory (94.7–116 GiB predicted vs 30 GiB) and independently on conditioning; N=16 rung: the first A6 adjoint that has ever existed (517 GMRES iterations, converged); gradient 8 of 9 graded PASS at 1.043 %, twist idx6 NOT A RESULT; **N=29 NOT RUN — Sanaa's gate (D464)**.
- **B1** reproduction plans (zero compute); **B2** duct + CBFS baselines PASS reproduced (30.9 core-min); **B3** CBFS field-inversion pilot: Stage 3 BLOCKED on the shipped image (`KSP -9` at iteration 0), unblocked on the patched sub-LU image; **Stage 4 (the inversion) never ran**.
- **S1 CBFS inversion:** first run G1/G2 GATE FAIL (loss measured the wrong thing, 336 core-min); re-inversion G1 PASS (−74.2 %) / G2 GATE FAIL (425 core-min, budget-capped); weighted arm G1w/G2 GATE FAIL (229 core-min); FIML hump inversion PASS on the resolvable set.
- **W4 conditioning well:** hump `-9` reproduced deliberately (O0/M2/M1-D PASS, M1 PENDING, O3 BLOCKED on a denied memory guard); O2 re-buy: incomplete LU singular at all four drop tolerances, complete LU exceeds 20 GiB (NOT A RESULT at the cap, 15 core-min); D460 sweep 1: forward-AD NaN class = CONDITIONING/DIAGNOSABILITY, PASS (4.7 core-min).
- **W5 gradient regrade:** every published shape-gradient claim re-run stock vs patched (≈620 core-min vs 300 est.; 333 core-min bought no table); A5's 46.6 % → 2.24 %; sail 4.52 % was 99.5 % rotation defect; A4 not rescued.
- **Curriculum D1 (first ratified item):** A1 lift-constrained drag minimisation — patched row PASS (11 majors, −16.31 % CD, |CL−0.5| = 1.9e-7, endpoint gradient ≤ 0.26 %), shipped row BLOCKED (comparator KeyError) → D1-C′ mini-item frozen 2026-08-24 (Phase 1). 7.0 core-min.

### Capability
- FD-vs-adjoint verification protocol with a registered band (5/15 %, sign-flip decisive), per-component tables, step-size calibration, FD-noise-aware graded subsets (A6: mechanically sized steps predicted clearance within 8 % on 10/10).
- Two root-caused upstream defects with local patches: the IDWarp rotation branch (`dafoam-idwarp-rot:v1`) and the decomposition-dependent adjoint operator; plus sub-LU (`subpclu:v2`) and `kspopts` images; the union image `dafoam-team:v1`. **Nothing a reader can install produces the patched numbers** — stated in the inventory.
- Two converged constrained optimisations (A4, D1) with endpoint gradient checks; operator dump-and-verify to 13 digits; four planted-control comparators.
- **Five upstream defect drafts, all NOT FILED** (two `DEFECT_*` records lack the marker in their opening lines — a §10 gap to close).

### Missing
- No complex-step build (PETSc real-opt only); the forward-AD build does not reproduce the plain primal (D460) — every gradient reference is FD.
- Full-size adjoints on A3 and A6 are BLOCKED on memory (needs a ≥128 GiB instance — Sanaa-gated D16a); B3 Stage 4 (an actual field inversion at scale) never ran; O2 needs >20 GiB or a factorisation that fits; O3 needs an authorised memory guard.
- Untouched classes: unsteady adjoint (D12), MRF/rotating adjoint (D11), thermal objectives (D10), aerostructural (D16b), GPU-resident adjoint (D16c); curriculum D2–D15 pending (Tiers 1–5 ≈ 7,700–12,300 core-min ≈ $6.6–10.6).
- Decisions on Sanaa's desk: N=29 reading (D464), A3 rung-1 rule conflict (D485), O3 guard authorisation, 12 GiB floor, §13 PROPOSAL, five NOT FILED drafts.
- Seven charter clauses have no automatic enforcement; `check_row_discrimination.py` has never been run on `cases/dafoam/`.

---

## 4. Closure modelling challenge

### Cases and rungs run
- **Paper reproductions (a-priori):** Wu 2018 PIML-RF PASS (beats SST on 7/8 test cases, 0.3 core-h); Kaandorp 2020 TBRF GATE FAIL on all three claims (16-feature worse than 5-feature; 10.9× worse than SST; realisability 4.7× the truth's own violation rate; 17.8 core-h); Ling 2016 TBNN CPU arm GATE REACHED (7/8 vs baselines, pooled metric dominated by NASA_2DWMH); Schmelzer 2020 SpaRTA PASS at ceiling and discovered-model gates (from the existing W2 reproduction); Xiao 2016 EnKF BLOCKED at the forward model (no ensemble ran, 0.87 core-h).
- **A-posteriori (re-solved) arms:** Wu 2018 NOT A RESULT twice (truth injection makes U worse by 57–63 %; frozen-k arm 6/6 fail); Kaandorp NOT A RESULT for the whole lane on three cases (H0 GATE FAIL +57 to +63 %; 3.66 core-h, 0.565× estimate, zero waste).
- **R-ladder:** R1 doctrine, R2 shortlist memo delivered, **R3 = Sanaa picks the class (not taken)**, R4 SpaRTA-class build CLOSED GATE FAIL (G1 2 of 4 families; G2 diverged on all 12 cases; the frozen-field ceiling beats NULL by 60–99.99 % — "the harness carries the truth; the model does not"; 9.2 core-h, $0.47), R5 constraints discharged as a record, R5C ω-source repair CLOSED GATE FAIL by its identity gate (repair works as engineering: 22/27 zero bound events, 10/15 hills complete), R6 NOT DONE — blocked on Sanaa's phrasing.
- **FS-ladder:** FS1 110-feature library (40 cases, 641,652 cells); FS2 degeneracy gate ARMED (no family reaches full rank; ducts 96/110, 48 dead features, condition 1e33); FS3 three selection methods × three seeds with planted zero; FS4 term-set frozen; FS5 coverage gate ARMED, D476 clip-repair A1/A2/A4 PASS, A3 GATE FAIL referred, adoption lift EFFECTIVE (D494); FS6 comparative feature document DONE (34 papers mined).
- **GPU:** Ling 2016 arm 1 on gpu1 — NOT A RESULT (0/8 vs every baseline under full-batch SGD: ~3.4e5× fewer updates than Ling's per-point regime; tuned arm beats baselines 7/8 but violates realisability on 25–46 % of duct cells); 10.71 GPU-h = $8.62, 0.97× the timing-gate projection, 7.88 GPU-h idle waste named. **Arm 2 (matched update count) frozen at `f36fbdd9`, 3–32 GPU-h, cap 40 — awaiting instance start.**

### Capability
- End-to-end frozen-field harness (kOmegaSSTFrozen/Corrected) with a ceiling that works; a-priori + a-posteriori grading; planted-zero control in 12 scripts; five-seed spread reporting; realisability gate (Charter §4) in every prereg; extrapolation-coverage instrument with the clip blind spot repaired.
- Training pipelines live on CPU (RF, TBRF, TBNN, SpaRTA symbolic regression) and now GPU (TBNN with Optuna search, self-shutdown approved).
- 35 papers title-verified with sidecars; the benchmark pinned at one commit with data hashes stamped in every record.

### Missing
- **No learned model has beaten the harness's own ceiling or passed realisability at scale** — the line's central finding so far is negative and well-documented.
- **R3 (choose the model class) is Sanaa's decision and has not been taken**; R6 phrasing likewise; the round-5 entry is NOT SENT and **no lab-prepared submission exists** (submissions PARKED by charter).
- 16 papers PENDING (institutional access); two GPU case directories empty (drafts live under docs/closure/gpu_prereg_drafts/); Bae 2022 is a CPU item, Lozano-Durán BLOCKED on data/charLES.
- Xiao's EnKF has never run an ensemble; no Bayesian calibration exists in the line.
- Record hygiene: closure README scoreboard stale (Ling shown PENDING), no consolidated R/FS ladder-status table, only 4 of 12 graded records state their prereg commit sha in the RESULTS file.

---

## 5. Epistemic / parametric uncertainty

### What has been run
- **Numerical (discretisation) uncertainty:** Roache GCI (Fs 1.25, r 1.6, observed p per row) armed on the thermal family — T1c, T9a, T10a, T10a-R (fourth level: p 1.48 → 0.685, band opens to cover the error), T3 (unequal-ratio GCI validated against T1c's); T1b's triples all DIVERGENT/STAGNANT; E4a's order returned None. The SDK `uq.py` ladder bands on 12 curriculum studies — **every one `conclusive: False`** (Ahmed p 1.95 with extrapolate outside the measured range; B-52 fitted p 28.7; wing band wider than its value).
- **Model-form (epistemic):** eigenspace/barycentric envelopes measured on eight training cases — shape contained 0.995–1.0, production contained only 0.928–0.943 on hills/curved step, δ_B required 0.31–0.54 on separated flows vs 0.95–0.98 on ducts → VERIFICATION §2e (bands inherit the flow class they were calibrated on; a band is not a correction); P-A4 velocity envelope 1,344× the signal — NOT A RESULT as a UQ statement. F6d random-matrix (max-entropy) UQ — found the sign error in F6a's perturbation; 40-sample band contains the LES truth but the gated subset does not. MODEL_FORM band, 36 cells (contains CFL3D, not FUN3D; lever-activity unproven for 32/36). GP epistemic layer (`uncertainty.py`, LOO-calibrated) with sure/moderately-sure/not-sure verdicts.
- **Parametric:** SST closure-coefficient propagation on the TMR flat plate — 42-sample LHS over five coefficients with the log-layer constraint, Cd envelope width 30 % of working value, PCE holdout Q² 0.92, Sobol first-order σ_w1 = 0.96; motorbike two-corner + LHS coefficient envelopes (deliberately not merged); five-seed spreads on every ML reproduction (seed spread as an extrapolation detector, N-B17); Optuna 100-trial search on GPU; Xiao EnKF designed (N=60, 16 KL modes, 48-dim state) but BLOCKED — nothing stochastic ran.
- **Validation uncertainty:** V&V-20 `u_val` used in K0cT's Nusselt regrade (5.4 %; kOmegaSST excluded at 3.1–4.6 u_val); T1b arms four bands from correlation disagreement (2.8–5.8 %).
- **Doctrine and law:** three-channel doctrine (input/numerical/model, RSS in one function, "unquantified is not zero", shared evaluations withheld); §3.1 dimensionality rule (p divides by exactly 1.5); §6 labels-are-claims (five acts caught quoting ± bands off non-conclusive ladders as CIs); §17 draw-scatter before any ladder feature; N-T2 (a CONVERGING triple can arm a band narrower than the actual error, and the next triple 11× too wide).

### Capability
- The lab can bound **numerical** error honestly on 2D thermal rungs, **measure** model-form envelope containment (and show where the published frameworks fail), **propagate** coefficient uncertainty with LHS/PCE/Sobol on cheap cases, and **refuse** to label non-statistical bands as confidence intervals.

### Missing
- **No certificate line carries a combined u_val** — on the flat plate every channel reads unquantified and the total is null; `uncertainty_band.py` is written but not wired into `certificate.py`.
- Two independent GCI implementations (SDK vs thermal comparators) with independent Fs constants, and a sign defect in one repaired by a new instrument rather than reconciled.
- No 3D rung with a conclusive numerical band; no input/boundary-condition uncertainty propagated on a graded rung; no Bayesian calibration or ensemble inference has ever run (EnKF blocked); the GP epistemic layer has never been used on a pre-registered gate.
- Cost calibration gaps: Xiao, the eigenspace lane, and the hump gate have measured costs but no ledger row.

---

## 6. Heat transfer — all regimes

### Cases run (by regime)
- **Conduction / conjugate (composite wall + fin), 2D/3D:** T9a — R0 wall flux PASS (1.8 % vs GCI 2.0 %), R2 interface temperature PASS (−0.51 mK vs 0.75 mK band), R1 GATE FAIL (−2.41 mK vs 0.92 mK band), R3/R4 fin quantities GATE REACHED (bands below the O(Bi) floor); T9a-D found the cause (interface scheme; `Gauss harmonic corrected` exact to 9 digits); T9a-H re-grade under harmonic interpolation.
- **Forced convection, laminar internal:** T1c pipe — f·Re PASS (0.019 % on a 0.024 % band), Nu constant-q″ PASS, Nu constant-Ts GATE FAIL (0.087 % vs 0.030 % band, ~2.9 bands out).
- **Forced convection, turbulent internal:** T1b pipe — four rows PASS by the frozen comparator, but every Roache triple DIVERGENT/STAGNANT; under the binding triple gate these read NOT A RESULT; L4 arms 10k/30k/100k/300k running (300k lands 2026-08-24, rest by 08-26). T3 heated backward-facing step — NOT A RESULT 4/4 (primary Vogel & Eaton 1985 NOT OBTAINED; the reference is the blocker); ext1 all eight extensions now complete, re-grade in progress in the peer session.
- **Forced convection, external:** K0e flat plate — BLOCKED/PENDING by construction (no honest band from one correlation; Bahrami 2005 obtained; rung not built). E4a fanPressure BC verification — NOT A RESULT (comparator order None; D493).
- **Natural convection, laminar:** THERMAL_K0 K0a/K0b capability rungs (all PASS, "not results about the world", 0.86 core-min); K0b reproduction: numbers reproduce bit-for-bit, the script failed (V3 GATE FAIL), then repaired (W1–W4 PASS); K0c square cavity Ra 1e3–1e6 vs de Vahl Davis — **GATE PASS, 0 of 20 rows failed** (largest deviation 1.14 % on a 3 % band; 41.7 core-min + 44 discarded); K2e Boussinesq validity limit — velocity separates first at ε ≈ 0.033–0.05, Nusselt last at ε > 0.3 (28.9 core-min, solver-backed, no experimental reference).
- **Natural convection, turbulent:** K0cS square cavity Ra 1.58e9 (Ampofo) — kOmegaSST GATE FAIL 8/10, kEpsilon GATE FAIL 6/10, LaunderSharma REFUSED (206.5 core-min); K0cT tall cavity (Betts & Bokhari) GATE FAIL 8/18 + Nusselt regrade GATE FAIL (excluded at 3.1–4.6 u_val; 95 core-min); K0cX cross-geometry GATE FAIL for all three models (24/60 rows; 321.8 core-min); K0cG third mesh level — grades nothing, deviation/GCI ratios 43–722× (model error, not grid; 300.6 core-min, 1.35× overrun); K0cP Prt sweep (WORSE — constant would need 1.1–1.2), K0cQ QCR anisotropy (SMALL, ruled out by 50–250×), K0cR SSG (velocity 19 points better, heat flux 30 points worse); K0cX grid convergence: only 1 of 6 model/quantity pairs in the asymptotic range. **Headline: three models, two geometries, three Rayleigh decades, zero passes; gradient-diffusion refuted three ways.**
- **Mixed convection / DC spine:** K2b rack-row 2D pilot — physically unsteady (6.0 s limit cycle, 1.1 K amplitude; the steady cost plan VOID; 65.4 core-min); K2b 3D unsteadiness prereg PENDING (run dirs exist, no results); K0d Blay cavity NOT RUN (primary NOT OBTAINED); K2a rack-row spec (zero compute); K2c validation search — hard-floor rung armable (Wibron 2018), raised-floor rung BLOCKED (no primary); KV1 heat-balance instrument confirmed (0.93 core-min).
- **Radiation, surface-to-surface:** T10a sphere/box enclosures — box 3 of 4 PASS, sphere triples DIVERGENT (NOT A RESULT); T10a-R fourth level — GATE FAIL 5/4/0 with the band-smaller-than-error pattern dying at level four and the quadrature method confirmed material (RQ2 fired); T10a-VF row-sum defect characterised (upstream candidate #4, NOT FILED); iteration exonerated.
- **Transient / thermal mass, participating-media radiation, phase change, humidity:** none run.

### Capability
- The only family with a real Roache GCI per row (Fs 1.25, observed p, refusal on non-monotone triples); planted-zero comparators with refusal; the strict completion rule with the age guard; mark-done instruments; heat-balance instrument validated with mutation tests.
- Solvers/models exercised: buoyantBoussinesqSimpleFoam (laminar, SST, kEpsilon, LaunderSharma, SSG, QCR variants), viewFactor radiation, conduction/CHT, fanPressure BC.
- The DC certificate template holds ten backed lines (8 PASS, 2 GATE REACHED) — all conduction/laminar/radiation; all four DC quantity classes (inlet temperature, recirculation, stratification, transient) PENDING.
- Ratified expertise curriculum (12 candidates, $86–227) queued behind the spine.

### Missing
- **No turbulence model has ever passed a turbulent thermal gate against experiment** — the deepest open problem the lab owns, and it is reference-limited as much as model-limited (a buoyancy-driven flux term needing transported temperature variance is named, not built).
- No forced-convection heat-transfer PASS with a converged triple (T1b's triples diverge; T3 blocked on its primary; K0e cannot be gated by construction).
- Mixed convection ungated (K0d unrun, K2b unsteady, K2c-B blocked); conjugate heat transfer beyond pure conduction none; radiation participating media none; transient thermal response none; humidity/phase change none; 3D thermal limited to T10a/T9a/T1b.
- Primaries NOT OBTAINED: Vogel & Eaton 1985 (T3/T5), Blay 1992 (K0d), Tian & Karayiannis Part II, raised-floor rack data; T4–T13 unstarted (T5 prereg draft awaiting freeze).
- Vocabulary drift in the F14 records (FORM, SMALL, WORSE, REFUSED, GRADES NOTHING, O1) — branch labels sitting where verdicts should be; and the K0c denominator (24 vs 20) differs between the results file and the capability state.

---

## 7. Where to focus next — the chief's reading of the gaps

1. **Grid convergence outside the thermal family is the lab's largest structural gap.** Not one aerodynamic case, 2D or 3D, carries a CONVERGING Roache triple. Arming the thermal comparators' GCI on the cheapest aerodynamic ladders (F3, F6b, F11 — all under 40 core-min to re-run under a frozen prereg) would convert results into credentials at near-zero cost.
2. **3D validation against experiment is empty.** The bluff-body and wing programmes produced honest negatives (withdrawn features, non-monotone ladders). A 3D case with a clean triple and an experimental reference — the Ansys VM cases are exactly this shape — is the natural next credential.
3. **Turbulent heat transfer has zero passes and is reference-limited.** Obtaining Vogel & Eaton, Blay and Tian Part II unblocks T3/T5, K0d and the K0cS statistics at no compute cost.
4. **DAFoam is memory-limited, not method-limited.** The full-size A3/A6 adjoints, O2's complete factorisation and B3 Stage 4 all wait on a ≥128 GiB instance (Sanaa-gated) or on the memory-guard authorisation.
5. **Closure needs R3 — Sanaa's model-class choice** — before any new build; everything runnable below that decision has been run.
6. **UQ needs one wired certificate**: `uncertainty_band.py` into `certificate.py`, and one graded rung carrying all three channels — the flat plate is the cheapest candidate.
