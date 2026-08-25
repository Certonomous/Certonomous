# ANSYS VALIDATION REGISTER — every VM2026R1 case the lab has run

**Owner:** `ansys-verification-supervisor`. **Charter:**
`docs/charters/ANSYS_VERIFICATION_CHARTER.md` §6. **Created:** 2026-08-24 by
the harness-build lane, empty. **Append-only** under the private-index
protocol (CLAUDE.md rule 10): a row is never edited after it lands; a
correction or a re-run is a new row citing the old one.

**Reading rule.** Every case run is a row, whatever its verdict. **Only `PASS`
rows are credentials** — the lab's credential count from this suite is the
number of `PASS` rows and nothing else. `GATE FAIL` and `NOT A RESULT` rows
stay here honestly, with their numbers; they are findings, not deletions.
Verdict vocabulary only: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT`
/ `BLOCKED` / `PENDING`. Dates are UTC from a `date -u` read in the writing
invocation. Dollars are **derived** at the owner-stated $0.0513/core-h, never
measured (the box cannot read its own billing).

Reference result and tolerance are the **frozen** values from the case's
pre-registration, whose sha is the row's `prereg sha`; the comparator sha is the
committed grading script that produced the number.

| # | Case | Date (UTC) | Verdict | Lab value | Reference (source, manual p.) | Tolerance (frozen) | Artifact path | Prereg sha | Comparator sha | Cost, core-min (measured) | $ (derived) | RESULTS path |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **VMFL001** — Flow Between Rotating and Stationary Concentric Cylinders (VM2026R1, pp. 15–16) | 2026-08-24 | **`NOT A RESULT`** | **none — comparator refused (exit 2) + L3 not converged.** The frozen comparator could not find its sampled file (v2606 writes `gateAxis_p_U.xy`, header-less; it was frozen to expect `U_gateAxis.*` with a header) and refused rather than guess a column; independently, L3 fails the registered iterative-convergence clause (final-iteration initial residuals Ux/Uy 1.19876e-06, p 2.89185e-06 vs frozen < 1e-6; plateau ptp 2.77178e-05 m/s vs frozen < 1e-6 m/s) while L1/L2 pass (4.69e-14 / 1.49e-12; ptp 1.00e-14 / 1.27e-11), which under CLAUDE.md rule 5 step 1 makes the rung `NOT A RESULT` before the triple is classified. No planted-zero firing, no triple, no GCI | v_θ at r = 20/25/30/35 mm = **0.0151 / 0.0105 / 0.0072 / 0.0046 m/s** — analytical, F. M. White, *Viscous Fluid Flow* §3-2.3, as printed in the manual's "Target, m/s" column, **manual pp. 15–16**. Context only, never the gate: Fluent 0.0151/0.0105/0.0072/0.0045, CFX 0.0150/0.0105/0.0071/0.0045 | **2 % relative at all four radii, at the finest level (L3, 64 × 256)** — frozen in `PREREGISTRATION.md` §3, justified from the manual's own printed-target rounding (worth 1.148 % at 35 mm) and tighter than the manual's own 3 % goal. Never reached | `verification/runs/ansys_verification/VMFL001/` (committed `ae30f914`) | **`d6ea5de9286ad5c8699b6e709e105c2cd484e8c1`** (as amended and as it ran; original freeze **`e0afc25936277798d3054137734fd9775311fbbb`**, commit `ffeed580`) | **`8cb29610e5d6f6fa4291df503a98bc99d0ff660f`** | **1.9833** (119 wall s, serial; cap 10, never approached) | **$0.0017** (derived at $0.0513/core-h, not measured) | `cases/ansys_verification/VMFL001/RESULTS.md` |
| **2** | **VMFL001-R2** — Flow Between Rotating and Stationary Concentric Cylinders (VM2026R1, pp. 15–16). **Re-run of row #1 after that row's `NOT A RESULT`**, per `VERIFICATION_CHARTER.md` §6: a new row citing the old one, which is not removed, re-labelled or softened. Two things changed and both repair a named run-1 mechanism — the comparator's reader matched to what OpenFOAM v2606 actually writes (header-less `gateAxis_p_U.xy`), and L3's `endTime` raised 3000 → 6000. **The gate, tolerance, diagnostic, mesh levels, solver settings and Roache quantity are UNCHANGED from row #1** | 2026-08-24 | **`PASS`** | **v_θ at r = 20/25/30/35 mm = `0.0151121317` / `0.0105287949` / `0.0071835454` / `0.0045457781` m/s** at L3 (64 × 256, 16384 cells), from `L3_64x256/postProcessing/radialProbes/6000/gateAxis_p_U.xy`. **Deviations vs the manual's printed targets: 0.0803 % / 0.2742 % / 0.2285 % / 1.1787 % — all four inside the frozen 2 %, so the gate is MET.** Deviations vs the exact White §3-2.3 formula: **0.0529 % / 0.0456 % / 0.0420 % / 0.0447 %** — the frozen 0.5 % diagnostic is met at all four radii too (the diagnostic is not the gate). The 35 mm row's 1.179 % is dominated by the manual's own rounding of its printed target (0.0046 vs exact 0.00454781 = 1.148 %), exactly as `PREREGISTRATION.md` §2 justified before any number was seen. **Roache triple on v_θ(35 mm), ratio 2.0, Fs 1.25: coarse `0.0045145840`, medium `0.0045395745`, fine `0.0045457781` m/s; R = `0.2482366`; state `CONVERGING`; observed order p = `2.0102`; GCI_fine = `5.6328e-04` = 0.0563 %; Richardson extrapolated `0.0045478265` m/s, which lands on the analytic value to 0.000374 %.** Monotone, so the GCI is quotable. **Planted-zero control PASSED: planted 1.234e-03, read_back_delta 1.234e-03, reader_delta 1.234e-03, agreeing to 1e-15 m/s, no other radius moved.** **Iterative convergence, all three levels ✅:** final Ux/Uy/p initial residuals L1 4.69e-14 / 4.57e-14 / 6.51e-11, L2 1.49e-12 / 1.49e-12 / 4.85e-11, **L3 1.61027e-09 / 1.61026e-09 / 8.43e-11** — L3 is 620× inside the 1e-6 clause it failed in row #1 (1.19876e-06 there); plateau ptp 1.00e-14 / 1.27e-11 / **1.772e-07 m/s**, all inside 1e-6. Strict completion holds at all three levels (rc 0; one `End`; last time == that level's endTime 3000/3000/**6000**; `U`,`p` present; `ExecutionTime` count == endTime; age guard ✅). Levers verified from the run tree: ν = 2.0e-4, ω = 1.0, `laminar`, cells 1024/4096/16384, `Mesh OK` ×3. Azimuthal spread over 8 rays ≤ **3.10e-13 m/s** anywhere — axisymmetric to round-off | v_θ at r = 20/25/30/35 mm = **0.0151 / 0.0105 / 0.0072 / 0.0046 m/s** — analytical, F. M. White, *Viscous Fluid Flow* §3-2.3, as printed in the manual's "Target, m/s" column, **manual pp. 15–16**. Exact formula values 0.0151201 / 0.0105336 / 0.00718656 / 0.00454781. Context only, never the gate: Fluent 0.0151/0.0105/0.0072/0.0045, CFX 0.0150/0.0105/0.0071/0.0045. **This box has no Fluent and no CFX; nothing here is a statement about Ansys** | **2 % relative at all four radii, at the finest level (L3, 64 × 256)** — frozen in `R2/PREREGISTRATION.md` §2 (unchanged from row #1's freeze), justified from the manual's own printed-target rounding (worth 1.148 % at 35 mm) and deliberately tighter than the manual's own 3 % goal. **Met at all four.** Secondary diagnostic, printed beside the gate and never the gate: 0.5 % vs the exact formula — also met at all four | `verification/runs/ansys_verification/VMFL001/R2/` (committed `fd2321ef`; grading JSON `GRADING_VMFL001_R2.json`, stdout `GRADING_VMFL001_R2.stdout.txt`, cost `COST.txt`) | **`c6b4a7c4fd09d2286a30440f5090116a7dae0eea`** (commit `4507fc66`; frozen before compute, no amendment, and re-read by the run script at launch — every `RUN_RC.txt` carries this blob) | **`64b02be807a8adb6c2638fe739c55f735c8259ca`** (run script `116c7c2d5fc5ebe1ac742f69478d66ed37dbfc17`; HEAD at run `1fb3bf74`) | **3.2833** (197 wall s, serial; cap 10 core-min, 32.8 % used, never approached; predicted 3.7167, ratio **0.8834×**) | **$0.002807** (derived at $0.0513/core-h, not measured) | `cases/ansys_verification/VMFL001/R2/RESULTS.md` |
| **3** | **VMFL005** — Poiseuille Flow in a Pipe (VM2026R1, p. 25). Fully developed laminar flow in a circular tube at Re = 500; only the axisymmetric half-domain is modelled. Reproduced in OpenFOAM v2606 `simpleFoam` on a one-cell-thick 5° **wedge** (half-angle 2.5°, wall vertices at **exact** radius R = 0.00125 m), steady, `laminar`, ν = 1e-5 m²/s, ρ = 1 kg/m³ — so the solved kinematic pressure is numerically equal to Pa. Inlet is `codedFixedValue` `poiseuilleInlet`, u_x(r) = 2·V_avg·(1 − (r/R)²) from each patch face's own centre radius; outlet `fixedValue` p = 0. **Independent of rows #1 and #2 and re-grades neither** | 2026-08-24 | **`PASS`** | **dP = `10.2909853852` Pa** at L3 (400 × 40, 16 000 cells), from the last rows (iteration 6000) of `L3_400x40/postProcessing/{pInletMonitor,pOutletMonitor}/0/surfaceFieldValue.dat`; `p_outlet = 0` **exactly** at all three levels (`fixedValue` outlet — measured, not assumed, and believed only because the planted-zero control below fired on this exact file). **Deviation vs the manual's printed target 10.24 Pa: 0.4979 % — inside the frozen 2 % gate by a factor of 4.0.** Deviation vs the exact Hagen–Poiseuille closed form: **the same 0.4979 %** to eight significant figures — unlike VMFL001 (`N-AV3`), none of this rung's deviation is the manual's printed rounding. **Per level: `10.23475566` / `10.27932262` / `10.29098539` Pa** (1 000 / 4 000 / 16 000 cells; endTime 2000 / 3000 / 6000). **Roache triple on dP, ratio 2.0, Fs 1.25: R = `0.261691`; state `CONVERGING`; observed order p = `1.9341`; GCI_fine = `5.0212e-04` = 0.0502 %; Richardson extrapolated `10.295119` Pa.** Monotone, so the GCI is quotable and is quoted. **THE FINDING, recorded because the `PASS` does not convey it (`N-AV7`, `RESULTS.md` §5): the deviation from the analytic reference (0.4979 %) is 9.92× the fine-grid discretisation uncertainty (GCI_fine 0.0502 %), and Richardson extrapolation moves the answer FURTHER from the analytic value — the extrapolated 10.295119 Pa is 0.5383 % above the exact 10.24 Pa against the fine level's 0.4979 %. The triple is genuinely `CONVERGING` and the gate is genuinely met, and grid refinement does NOT close the gap: roughly 90 % of the residual deviation is a modelling/setup signature, not discretisation error. The mechanism is UNRESOLVED and is not claimed — candidates and what is and is not measurable are in `RESULTS.md` §5.3, and the open question is docket `D510`.** **Planted-zero control PASSED:** planted 1.234 Pa into a **temp copy** of L3's `surfaceFieldValue.dat` (the run tree was never modified), read_back_delta 1.234, reader_dp_delta 1.234; the control fires before the verdict and the comparator refuses on its failure. **Iterative convergence, all three levels ✅:** final Ux/Uy/p initial residuals L1 4.14e-12 / 5.40e-08 / 7.10e-10, L2 1.36e-12 / 9.49e-08 / 7.37e-10, L3 1.73e-13 / 2.00e-08 / 8.39e-10 — worst gated channel 9.49e-08, 10.5× inside the frozen 1e-6; inlet-pressure plateau ptp 4.10e-10 / 3.20e-10 / 6.00e-11 over the last 400/600/1200 iterations, all inside the frozen 1e-4. `Uz` (1.85e-02 / 8.82e-03 / 2.54e-03) is the wedge's out-of-plane null channel, excluded from the gate by the freeze before any number was seen and printed rather than dropped (`N-AV8`). Strict completion holds at all three levels (rc 0; one `End`; last time == that level's endTime; `U`,`p` present; `ExecutionTime` count == endTime; age guard vs that level's own `0/U`). Levers read from the run tree: ν = 1e-5, `laminar` active-in-log, cells 1 000 / 4 000 / 16 000, `Mesh OK` ×3, **Re = 500.0000** (manual: 500). Wedge verified by the lane from `constant/polyMesh/boundary` (`wedge1`/`wedge2` both `type wedge`) and from the monitor header's patch area 6.809042402188e-08 m² = ½R² sin 5° to twelve significant figures — the comparator's `wedge_in_log` lever reads `false` because v2606 does not print patch types in the solver log, which is a null and not a failure | **dP = 10.24 Pa** — analytical, Hagen–Poiseuille, F. M. White, *Fluid Mechanics*, 3rd ed., McGraw-Hill, New York, 1994, as printed in the manual's "Target" column of Table .05.1, **manual p. 25**. Exact closed form 8·μ·L·V_avg/R² = 10.240000 Pa (μ=1e-5, L=0.1, V_avg=2.0, R=0.00125), cross-checked via 8·μ·L·Q/(πR⁴) — the two forms agree, so the reference is not a transcription. Context only, never the gate: Fluent 10.22 Pa (ratio 0.998), CFX 10.49 Pa (ratio 1.024); this lab's 10.2910 Pa is ratio 1.0050. **This box has no Fluent and no CFX; nothing here is a statement about Ansys** (`ANSYS_VERIFICATION_CHARTER.md` §2) | **2 % relative to the manual's printed target, at the finest level (L3, 400 × 40)** — frozen in `PREREGISTRATION.md` before any solver started, at blob `43aaf6bf` / commit `2d54a629` / 2026-08-24T18:42:07Z, with the first run artifact at 18:45:32Z. No amendment, no addendum. **Met with a factor of 4.0 of margin.** Secondary diagnostic, printed beside the gate and never the gate: **1 %** vs the exact Hagen–Poiseuille closed form — also met (0.4979 %) | `verification/runs/ansys_verification/VMFL005/` (committed `90ee8d80`, 54 files; grading JSON `GRADING_VMFL005.json`, stdout `GRADING_VMFL005.stdout.txt`, cost `COST.txt`). **The six gate-source `surfaceFieldValue.dat` files match `.gitignore:67` and are invisible to `git add`; they were filed by explicit path via `update-index --add`, which does not consult the ignore rules (L-300)** | **`43aaf6bf5c5f1189495e1460e5de415e56860447`** (commit `2d54a629`; frozen before compute, no amendment, and re-read by the run script at launch — all three `RUN_RC.txt` carry this blob) | **`8e7410cc356c3e175fe0d993efa366d51085ba81`** (run script `06056e18a9fee92e2e8765b279ae31f5373c62c5`; HEAD at run **derived** as `22abb11d` from the artifact timestamps against `git log`, and HEAD moved during the run — the exact binding is the per-level `prereg_blob` stamp, not a single HEAD) | **4.0000** (240 wall s, serial; L1 11 s / L2 29 s / L3 200 s; cap 13 core-min, 30.8 % used, never approached, no `CAP_EXCEEDED.txt`; predicted 4.9, ratio **0.8163×**; waste **0.000**, named separately; calibration row **C-47**) | **$0.003420** (derived at $0.0513/core-h, c7a.4xlarge, reported-by-owner — **not measured**, the box cannot read its own billing) | `cases/ansys_verification/VMFL005/RESULTS.md` |
| **4** | **VMFL051** — Isentropic Expansion of Supersonic Flow Over a Convex Corner (VM2026R1, pp. 165–166). Inviscid, compressible, ideal-gas supersonic flow turning 15° around a convex corner through a **centred Prandtl-Meyer expansion fan**; the manual's target is the post-expansion Mach number. **The lab's FIRST compressible/supersonic case from this manual** — rows #1–#3 are all incompressible `simpleFoam`. Reproduced in OpenFOAM v2606 **`rhoCentralFoam`**, a density-based shock-capturing solver, transient with `adjustTimeStep yes`, on a three-level refinement-2 family (6 240 / 24 960 / 99 840 cells) at the **same physical `endTime` = 7e−3 s at every level**. Inlet M 2.5, static T 300 K, p 202 636.9 Pa; adiabatic slip walls. **Independent of rows #1, #2 and #3 and re-grades none of them** | 2026-08-25 | **`NOT A RESULT`** | **Gate value (finest level L3, 480 × 208, 99 840 cells, 1 816 zone cells): `Ma = 3.2294355513`**, `volAverage(Ma)` over the frozen `gateZone` cellZone at `endTime`, from `L3_480x208/postProcessing/gateMach/0/volFieldValue.dat`. Deviation vs the manual's printed target 3.2370: **−0.233687 %**, which is INSIDE the frozen ± 0.5000 % band by a factor of 2.14 — **and the row is `NOT A RESULT` regardless, because rule 5 gates the gate.** **TWO INDEPENDENT CLAUSES OF `CLAUDE.md` RULE 5 EACH PRODUCE THIS VERDICT ON ITS OWN. (1) Rule 5 step 1, the frozen plateau clause: L1 AND L2 BOTH FAIL.** Peak-to-peak of the `volAverage(Ma)` gate series over each level's last 20 % of rows is **L1 6.240e−03** (over its last 339 of 1 693 rows) and **L2 3.535e−03** (last 673 of 3 365) against a frozen tolerance of **1.000e−03** — 6.24× and 3.54×. Only **L3** plateaus, at **8.549e−04** (last 1 343 of 6 714), 0.85× the tolerance. **(2) Rule 5 step 2, the Roache triple: `OSCILLATORY`.** Coarse **3.2278606097**, medium **3.2233427020**, fine **3.2294355513**; **d32 = +4.517908e−03**, **d21 = −6.092849e−03**, **R = −1.348600** — the increments change sign. **No observed order exists and NO GCI IS QUOTED**, correctly: the three values are not monotone. `triple.f_extrapolated` and `triple.gci_fine` are both `null`, so the ρ and dev_extrap readings that Amendment 1 registered in advance are **not computable**; this is that amendment's reading **(d)**, and none of readings (a) the VMFL001-R2 pattern, (b) the VMFL005 pattern or (c) indeterminate is available or claimed. **Per-level deviations vs the manual target: −0.282341 % / −0.421912 % / −0.233687 %**; vs the closed-form exact value: **−0.237380 % / −0.377014 % / −0.188704 %**. **DIAGNOSTIC ONLY AND NEVER THE GATE: the closed-form exact `M₂ = 3.2355411372251854`**, Prandtl-Meyer at **γ = 1.3990093734749485** derived from the manual's OWN Cp = 1006.43 J/kg-K and MW = 28.966 — **not** the textbook 1.4, at which the exact value is 3.2368431056638847. L3's deviation from it is **−0.188704 %** against a frozen ± 0.25 % diagnostic band: inside. **ALL THREE PLANTED-ZERO CONTROLS FIRED** (`CLAUDE.md` rule 3), every plant into a temporary copy and the run tree never modified: **PZ-1** gated `.dat` reader, planted 1.234e−03 Mach, read back 1.2339999999997353e−03; **PZ-2** the `Ma` FIELD reader on the real 99 840-cell L3 field, planted 7.77e−02, read back 7.770000000000010e−02, with the field measured **non-uniform** (min 2.49999805, max 3.396358576, mean 2.7006549026427984) — a uniform Mach field after an expansion fan is not a solution; **PZ-3** the reference computation itself, +5° of turn moving M₂ by 0.30002701584152813, with the identity ν(M₂) − ν(M₁) returning **14.999999999999972°** against the required 15°, so the root finder solves rather than returning a constant. **Declared inner-zone clause PASSED** and is recorded because its failure would have been a third independent route to the same verdict: at L3, the gate-zone and inner-zone averages differ by **2.284871e−04 = 0.0228 %** against the frozen 1e−2, inside by 43.8×. **Strict completion HELD at all three levels** (rc = 0 ×3; exactly one `End` line each; fields `T U p rho Ma` present; `ExecutionTime` count == `Time` count, 1 693 / 3 365 / 6 714 steps; age guard dated from the latest mtime anywhere in each level's own `0/`, STRICTER than the rule) — **with the two departures from rule 4's literal text declared on the face of the freeze (§8) before the answer was known, both tighter-or-equal rather than looser**: DEPARTURE 1 replaces `last time == endTime` with agreement to within `maxDeltaT` = 1e−5 s (`adjustTimeStep yes`; last times 0.0070015301 / 0.0069997882 / 0.0069999107 against 7e−3), and DEPARTURE 2 replaces the steady-iteration `ExecutionTime` count clause — which a transient adaptive-step solver can never satisfy — with a direct check of the invariant it protects, that the log is not truncated mid-step. **MECHANISM: A LEADING CANDIDATE WITH ARITHMETIC BEHIND IT, EXPLICITLY NOT ESTABLISHED** (`RESULTS.md` §3). The two coarse levels have not reached a steady plateau in the sampling zone at `endTime`, and an unplateaued coarse and medium value is the most likely origin of the non-monotone triple: the level-to-level differences are **the same order as the coarse levels' own residual unsteadiness** — |d32| = 4.518e−03 is **0.72×** L1's peak-to-peak and **1.28×** L2's, and |d21| = 6.093e−03 is **1.72×** L2's — so the triple is plausibly measuring transient noise rather than discretisation error. **Four reasons it is NOT claimed as established are given rather than glossed:** the arithmetic is a consistency argument and not a demonstration; **L2, not L1, is the outlier** (3.2279 / 3.2233 / 3.2294 — the medium level dips below both neighbours) and nothing here explains why the middle level specifically; **no time-refinement study was run and none was pre-registered**, so whether a longer `endTime` would restore monotonicity is untested and is not asserted; and L3 being both the plateaued level and the one closest to exact is suggestive, not evidence. **No re-run is proposed by this row and no `endTime` is recommended.** **THE DISCIPLINE WORKING AS DESIGNED, and worth stating plainly** (`RESULTS.md` §4): the gate value sits inside the frozen ± 0.5 % gate band, inside the tighter ± 0.25 % diagnostic band, and inside the manual's own 3 % accuracy goal (§1.3, p. 5) by **12.8×** — and rule 5 makes it `NOT A RESULT` anyway, because two of three levels never settled and the lab therefore cannot show the number is a converged property of the discretisation rather than a snapshot of a still-moving solution. Had the order been read gate-first, this row would today be a `PASS` and it would be unsupported. **The rule's one-way property held**: the gate turned a would-be `PASS` INTO `NOT A RESULT`, never the reverse. **MANUAL DEFECT, recorded on the frozen pre-registration §1a BEFORE any compute so it cannot be presented as a discovery that followed a number:** VMFL051's *"Analysis Assumptions and Modeling Notes"* (p. 165) calls the flow *"steady, inviscid, and **incompressible**"* while its own *"Physics/Models"* line **on the same page** says *"**Compressible**, inviscid flow"*, its Material Properties line says *"Density: Ideal Gas law"*, and the case is an M 2.5 → 3.24 isentropic expansion. **Quantified: an incompressible treatment produces no Mach change at all** — M stays 2.5 against a target of 3.2370, **−22.77 %**, failing the frozen gate by a factor of **45**; the comparator's `--selftest` fires exactly this arm. Two further manual defects are on the freeze §1a and are not re-derived here: the printed target 3.2370 is not the exact Prandtl-Meyer value at any γ consistent with the case (≈ 0.005 % of two-decimal ν table-rounding), and Table .51.2's value column is headed *"Ansys Fluent"* under a *"Results Comparison for Ansys CFX"* section. **All three are `NOT FILED`** — contacting Ansys is Sanaa's decision alone (`CLAUDE.md` rule 7). **No `N-AV` or docket id is cited by this row, because none has been appended for this case**: an id written into prose before its append is a prediction and not an identifier (`L-292`), which is the defect this register already carries once in row #3 and corrected in the dated note below | **Mach number after expansion = 3.2370** — the manual's printed "Target" column, **Table .51.1, p. 166**, an analytic Prandtl-Meyer value attributed to John Anderson, *Modern Compressible Flow: With Historical Perspective*, McGraw-Hill, 2002. Table .51.2 prints **3.237** for the same quantity. **Closed-form exact for the gas the manual actually specifies: 3.2355411372251854** at γ = 1.3990093734749485 — computed in the freeze §2 to full double precision rather than taken from the printed four decimals, and used ONLY as a declared diagnostic. Context only, never the gate: **Fluent 3.2316** (ratio 0.9980), **CFX 3.2354** (ratio 0.9995); this lab's 3.2294355513 is ratio 0.99766 against the printed target. **This box has no Fluent and no CFX; nothing in this row is a statement about Ansys** (`ANSYS_VERIFICATION_CHARTER.md` §2) — `VMFL051_FLUENT.cas` and `VMFL051_CFX.def` were never opened or run, and no VM2026R1 archive was touched | **± 0.5000 % relative to the manual's printed target, at the finest level (L3, 480 × 208)** — frozen in `PREREGISTRATION.md` §3.1 with its derivation in §3.3, and deliberately tighter than the manual's own 3 % goal by 6×. **The band was met (−0.233687 %) and the band is not what decides this row**: rule 5 steps 1 and 2 both fire first. Secondary diagnostic, printed beside the gate and never the gate: **± 0.25 %** vs the closed-form exact value — also met (−0.188704 %). **Plateau clause, frozen in §6: peak-to-peak of the gate series over each level's last 20 % ≤ 1.000e−03 in Mach** (= 3.1e−4 relative, 16× tighter than the gate) — **FAILED at L1 and L2**. Inner-zone clause, frozen in §6: gate-vs-inner disagreement ≤ 1e−2 at L3 — met at 2.285e−04 | `verification/runs/ansys_verification/VMFL051/` (committed **`fc46ad2d`**, 25 files: `GRADING_VMFL051.json`, `GRADING_VMFL051.stdout.txt`, `COST.txt`, `CONTENTION.txt`, and per level `RUN_RC.txt`, `log.rhoCentralFoam`, `log.blockMesh`, `log.checkMesh`, `log.topoSet` and both `postProcessing` `volFieldValue.dat` series). **The six gate-source `volFieldValue.dat` files match `.gitignore` and are invisible to `git add`; they were filed by explicit path via `git update-index --add`, which does not consult the ignore rules — `L-300`, met again on this case.** **DISCLOSED, not glossed: the OpenFOAM field data (~51 MB of per-time-directory volFields) is on disk and deliberately NOT committed.** Every graded number above is read from the committed `.dat` series and logs, with one exception — **PZ-2 read the L3 `Ma` field directly**, so if that run root is cleared PZ-2 becomes unreproducible from the repository alone, though its firing is recorded in the committed grading JSON | **`7dad56168d7ad7d599f92e05aa249a3014d0dc63`** (commit **`22249c82`**, 2026-08-25T00:20:33Z; **before-first-compute Amendment 1** at **`54d34542`**, 00:25:34Z, legal under `CLAUDE.md` rule 2 and altering **no** gate, threshold, cap or label; **first mesh written 00:25:59Z**, so zero compute preceded the freeze). **Verified in this lane by hashing rather than taken on report**: the worktree file, the HEAD blob and **all three** per-level `RUN_RC.txt` stamps carry this identical sha, so the binding is per level and not a single HEAD read. The freeze's own §2b.1 condition was checked and not asserted — at 00:15:28Z the run directory did not exist and `find` beneath it returned 0 files | **`acad1aff71da4a960045484f9e6f8470f8beccb7`** (`grade_vmfl051.py`; run script `run_vmfl051.sh`). Identical across the worktree file, the HEAD blob and all three `RUN_RC.txt` stamps. The launcher's own guards — refuse to start into any pre-existing level directory (rule 4's guard), refuse unless the pre-registration is committed at HEAD, refuse if `topoSet` left either sampling zone empty, and enforce the cap with `timeout` — none fired as a refusal | **23.3167** (1 399 wall s × 1 rank ÷ 60, serial, from `COST.txt` and corroborated level by level against the three `RUN_RC.txt`: L1 9 s / 0.1500, L2 207 s / 3.4500, L3 1 183 s / 19.7167). **Cap 28 core-min, 83.27 % used, never reached, no `CAP_EXCEEDED.txt`.** Predicted point estimate 11.3, **ratio 2.0634×**. **Waste 0.000, named separately and netted off nothing** — no level failed or restarted, no re-run, comparator exit 0 first invocation. **CONTENTION 14.408 core-min, MEASURED and named separately from the ratio** (`COMPUTE_BUDGET_CHARTER.md` §6): solver CPU is **534.52 s** (final `ExecutionTime` 7.71 + 59.31 + 467.50) against 1 399 s of wall, on a 16-core box carrying loadavg **68.38 → 75.84** of other teams' jobs. **The frozen solver estimate was GOOD — 534.52 s measured against a 637 s solver-plus-function-object allowance, 0.839× and conservative — and essentially the whole 2.06× overrun is contention.** Calibration row **`C-50`** | **$0.019936** (derived at $0.0513/core-h, c7a.4xlarge, **reported-by-owner — NOT measured**, the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) | `cases/ansys_verification/VMFL051/RESULTS.md` |

*Credential count: 2 PASS of 4 run.*

---

## Dated correction — 2026-08-25 — the `D510` docket citation in row #3 is wrong; the open question is `D512`

**Append-only correction under CLAUDE.md rule 6 and this register's own reading rule
(a row is never edited after it lands). Row #3 above is NOT edited; this note corrects
a citation it carries.**

Row #3 (VMFL005), in its "Lab value" cell, states: *"…the open question is docket
`D510`."* **`D510` is wrong.** `docs/DOCKET.md` `D510` is the **closure team's R3
SpaRTA ratification**, an unrelated item (a docket-id collision — the id was written
into prose before it was appended, the failure `L-292` names). The VMFL005
open-mechanism question — the ≈ 90 % non-discretisation deviation from Hagen–Poiseuille,
the `CONVERGING` triple that extrapolates *away* from the exact value (`N-AV7`), with
`RESULTS.md` §5.3's candidates and the `N-AV9` wedge-geometry arithmetic attached — was
opened under a genuinely free id, **`D512`**, at commit `20afae1b` (2026-08-25),
`docs/DOCKET.md` `D512`.

- Struck, verbatim: ~~"the open question is docket `D510`"~~
- Corrected: the open question is docket **`D512`**.

Read `D512`, not `D510`, wherever row #3 says `D510`. The same correction is recorded at
the foot of `cases/ansys_verification/VMFL005/RESULTS.md`.

**Lines whose number changed above this section: 0.**

---

## Dated note — 2026-08-25 — row #4 landed; what this append moved, and what it did not

**Recorded because the section immediately above asserts `Lines whose number changed
above this section: 0`, and this append shifted that section down.** That assertion was
true **of its own landing** and is not retracted; this note states what the *next*
append did, so a reader diffing the file is never left to infer it.

**Row #4 (VMFL051) was appended to the table**, between row #3 and the credential-count
line. **No existing row was edited** — the register's append-only reading rule holds,
and rows #1, #2 and #3 are byte-identical to their committed form.

**One derived line was updated**, and it is a tally rather than a row: the
credential-count line moved from *"2 PASS of 3 run"* to *"2 PASS of 4 run"*. **The
credential count itself did NOT change** — row #4's verdict is `NOT A RESULT`, and only
`PASS` rows are credentials. Leaving the denominator at 3 would have been false.

**Lines whose number changed above the table: 0.** The header, the reading rule and the
table's own header and separator are untouched. The `D510`→`D512` correction section
above shifted down by **two lines** and its text is unaltered.

**Row #4 cites no `N-AV` and no docket id**, deliberately. None has been appended for
VMFL051, and an id written into prose before its append is a prediction and not an
identifier (`L-292`) — the defect this register already carries once and corrects above.
The manual defect and the instrument defect that VMFL051 found are recorded in
`cases/ansys_verification/VMFL051/RESULTS.md` §5 and §7.1 and are **referred to the
supervisor** for an `N-AV` / `LESSONS` append under a genuinely free id; this lane
appended neither and cited neither.

**Lines whose number changed above this section: 1** — the credential-count tally
described above, and nothing else.

---

## Dated correction — 2026-08-25 — row #4's `C-50` calibration citation is wrong; VMFL051's calibration row is `C-51`

**Append-only correction under `CLAUDE.md` rule 6 and this register's own reading rule
(a row is never edited after it lands). Row #4 above is NOT edited; this note corrects
a citation it carries.** This is the same treatment row #3's `D510` mis-citation got.

Row #4 (VMFL051), in its "Cost, core-min (measured)" cell, states: *"Calibration row
`C-50`"*. **`C-50` is wrong.** `docs/COST_CALIBRATION.md` `C-50` is the **cfd team's
F12 rung 1** — RAE 2822, AGARD AR-138 Case 9, the coarse workshop rung — an unrelated
item belonging to another team.

- Struck, verbatim: ~~"Calibration row `C-50`"~~
- Corrected: VMFL051's calibration row is **`C-51`**, landed at commit `0c3f3054`.

**THE CAUSE, STATED PLAINLY AND NOT SOFTENED — and the two timestamps are the proof.**
cfd's `C-50` landed at commit `cd1ac21a`, **2026-08-25T01:09:21Z**. Register row #4
landed at **2026-08-25T01:14:13Z** — **four minutes and fifty-two seconds later**. The
id was therefore **already taken and already visible at HEAD** when row #4 was written.
Nothing raced: **the id was derived BEFORE the commit and was not re-derived inside the
committing shell invocation**, which `CLAUDE.md` rule 11 requires in terms — *"Peers
commit constantly: re-derive at commit time, in the same shell invocation."*

**A contributing factor, recorded as a factor and NOT as an excuse:** the worktree copy
of `docs/COST_CALIBRATION.md` is **~19.8 kB shorter than the HEAD blob** (168 635 B
against 188 448 B). An id derived from that copy is derived from a truncated file and
is **wrong before any race begins** — it races nothing and is still incorrect.

**THIS IS THE TEAM'S SECOND INSTANCE OF `L-292`** — *an id in prose before its append is
a prediction, not an identifier* — **and row #4 itself cites `L-292` while committing
it.** The first instance is row #3's `D510`, corrected in the note above only hours
earlier. That the defect recurred inside the very row that named it is the part worth
keeping: **naming a failure mode in prose does not implement it; only the committing
invocation does.**

**`C-51` was landed with its id re-derived from the HEAD blob's own tail inside the
shell invocation that wrote its tree**, with a re-derivation on any CAS retry, and its
building script now refuses to commit at all unless the tree actually changed.

**Every other identifier cited by row #4 was re-checked against HEAD at the time of
this correction and every one exists:** `L-292`, `L-300`, `N-AV7`, `N-AV8`, `N-AV9` and
`D512`. Row #4 deliberately cites **no** `N-AV` and **no** docket id of its own, because
none has been appended for VMFL051. **`C-50` was the single failing citation and it is
corrected here.**

**Lines whose number changed above this section: 0** — verified by hashing, not
asserted: the file's entire content up to and including the previous correction section
is byte-identical to its committed form, and this note is appended below it.

---

## Dated addendum — 2026-08-25 — TIER back-filled onto rows #1–#4, on Sanaa's directive

**Append-only addendum. Rows #1–#4 above are NOT edited** — the same treatment the
`D510` and `C-50` corrections got. This addendum adds a fact the rows were written
before the directive existed; it corrects nothing in them and moves no number.

**Sanaa's directive, 2026-08-25, quoted byte-exact with typos preserved and NOT
normalised:**

> *"i just meant for now cfd, ansys verification and heat transfer teams work on
> completeing all the tasks/ running all the cases and recording per our conventions,
> and record whether the case is hold, gate reached or surveyed or not held. Once that
> is done we will go back to the Matrix config. But for now these three teams work on
> that"*

**EVERY FUTURE ROW CARRIES ITS TIER IN THE ROW ITSELF, WRITTEN AT GRADING TIME.** This
addendum exists only because rows #1–#4 predate the directive. It is a back-fill and
must not become a pattern: a tier appended afterwards is weaker evidence than one
written when the number was first graded, for exactly the reason a pre-registration is
frozen before a run.

**The tier and the rule-1 verdict are DIFFERENT VOCABULARIES and are recorded side by
side. The tier NEVER flatters the verdict.** They overlap at one word only,
`GATE REACHED`. The verdict vocabulary — `PASS` / `GATE REACHED` / `GATE FAIL` /
`NOT A RESULT` / `BLOCKED` / `PENDING` — is unchanged and is not replaced by this
column. Tier values are `HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` /
`NEVER RUN`.

**All four tiers below are the `ansys-verification-supervisor`'s rulings, recorded as
such and overrulable. They are not this lane's calls.**

| row | case | verdict (rule 1, unchanged) | **tier** | the reason, as ruled |
|---|---|---|---|---|
| **#1** | VMFL001 run 1 | `NOT A RESULT` | **`NOT HELD`** | The comparator refused (exit 2) on the v2606 sampled-file naming and never produced a number, and independently L3 failed the registered iterative-convergence clause. **Nothing was measured**, so there is nothing to hold |
| **#2** | VMFL001-R2 | `PASS` | **`HOLDS`** — **a CANDIDATE, stated plainly as one and NOT as settled** | V and G are both present and strong: triple `CONVERGING`, observed order **2.0102**, GCI_fine **0.0563 %**, Richardson extrapolate landing on the analytic value to **3.7 ppm**. **It is a candidate rather than a hold because the P limb is UNRESOLVED**, and neither this register nor this addendum resolves it. Calling it a settled hold on the strength of V and G alone is exactly the flattery this column is built to prevent |
| **#3** | VMFL005 | `PASS` | **`GATE REACHED`** | The gate is genuinely met (0.4979 % inside a frozen 2 %) and the triple is genuinely `CONVERGING` (observed order 1.9341, GCI_fine 0.0502 %). **P is the missing limb, and it is named rather than left implicit:** the deviation from the analytic reference is **9.92× the fine-grid GCI**, and Richardson extrapolation moves the answer **FURTHER from** the exact value — so roughly **90 % of the residual deviation is a modelling/setup signature, not discretisation error** (`N-AV7`). The mechanism is **unresolved and not claimed**, open at docket **`D512`** |
| **#4** | VMFL051 | `NOT A RESULT` | **`NOT HELD`** | **V present, G ABSENT, and G decides it.** The reference is the exact Prandtl-Meyer solution derived here to full double precision — **public classical gas dynamics** (Anderson; NACA 1135), **not vendor documentation** — so V is not the problem. But the triple is `OSCILLATORY` at **R = −1.348600** with **no observed order** and **no quotable GCI**, and **two of three levels fail the frozen plateau clause**. P is open. **The softer `GATE REACHED` was refused deliberately:** that word fits a case that produced a **believable measurement** and lacks one column, as row #3 does. **VMFL051 produced no usable measurement at all — its G column is not missing, it is actively negative.** Precedent is this team's own row #1 |

**The credential count is unchanged: `2 PASS of 4 run`.** A tier is not a credential and
does not create one. Only `PASS` rows are credentials, and no row's verdict moved.

**The suite-wide picture, derivable rather than recalled**, lives in
`docs/ansys_verification/CASE_MAP.md`, where all **95** case rows now carry this same
tier column and the counts are printed with the grep rule that derives each:
**3 of 95 run, 92 never run**; **12** cases have no lab solver on this box and **10**
are the `VMFLGPU` family, with **zero overlap**, giving **73 runnable distinct-physics
cases — 3 run, 70 never run**. **Whether the GPU family and the 12 count toward
"completed" is scope, and scope is Sanaa's**; that document prints both readings and
chooses neither.

**Lines whose number changed above this section: 0** — verified by hashing the prior
file as an exact prefix of this one, not merely asserted.
