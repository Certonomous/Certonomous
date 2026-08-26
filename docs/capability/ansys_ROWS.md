# ansys-verification — EVERY REGISTER ROW MAPPED ONTO Sanaa's cfd / heat-transfer CLASSES — VERIFICATION SUPERVISOR'S DRAFT FROM THE RECORDS

**Written 2026-08-26 by verification lane `cfd` for the verification-supervisor, FROM THE RECORDS AT HEAD, as the draft the ansys-verification-supervisor (and the cfd- / heat-transfer-supervisors, whose grids these rows feed) are asked to CORRECT by appending a dated section. Zero compute.** Source of every verdict: `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` **at HEAD, commit `eadbe157`** — 29 rows. **The worktree copy of the register is STALE (51 lines short of HEAD, `git diff HEAD --stat`); it was not used and, per rule 10, not touched.** Each row also cites its own record path (`RESULTS.md` / supervisor ruling / lane report) with the sha of the commit that last touched it, and the grading artifact under `verification/runs/ansys_verification/` — five of thirteen named artifacts are at HEAD; the other eight are on disk only and are marked so (they are not cited as records).

**Taxonomy (Sanaa, `068c2bf0`):** cfd cells = dimension (2D / axisym / 3D) × time (steady / unsteady) × regime (incompressible / subsonic-compressible / transonic / supersonic / hypersonic / multiphase-free-surface); heat-transfer cells = mode (conduction / forced conv / natural conv / mixed / conjugate / radiation) × laminar-vs-turbulent × dimension. **Conventions this lane chose, stated so they can be overruled:** (i) 1-D exact-solution rungs (Stokes' first problem, semi-infinite slab) are filed in the **2D** row — the taxonomy has no 1-D class; (ii) a cavitating orifice run with `interPhaseChangeFoam` to a steady discharge coefficient is filed **axisym · steady · multiphase-free-surface** with the note that it is cavitation (VoF phase change), not a free surface; (iii) VMFL002 and VMFL076 carry BOTH a cfd cell (their dP / momentum solve) and a heat-transfer cell (their temperature gate); (iv) "axisym" is asserted only where the prereg or the mesh at HEAD says `wedge` (`grep -l wedge` on `constant/polyMesh/boundary` under `verification/runs/ansys_verification/<case>/`: VMFL002, 003, 003_M2, 005, 007, 021, 022, 036 — all others are Cartesian planar).

**Verdict vocabulary.** The register's tokens (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `PENDING`) are copied verbatim. **Only `PASS` rows are credentials** (register reading rule). Rows that are `NOT A RESULT` because a **frozen comparator refused** rather than because the physics failed are said so per row: the refusal classes on record are the v2606 filename mismatch (row #1), the iterative-convergence residual leg (rows #6, #9, #10), the transverse-residual normalisation-noise clause (**L-338**, row #25), the planted-zero threshold on an averaging reader (**L-340**, row #26), and the wall-shear sign-change reader (row #29). A refusal is not a physics result and not a physics failure; it is also not a credential.

## 1. Class per case, derived from the frozen pre-registration by path:line

| case | solver / conditions (path:line) | cfd cell | heat-transfer cell |
|---|---|---|---|
| VMFL001 / -R2 concentric rotating cylinders | `simpleFoam`, steady laminar, **Re_gap = 2.53**, planar r–θ annulus 64 × 256 — `cases/ansys_verification/VMFL001/PREREGISTRATION.md:25-26,60-63` | 2D · steady · incompressible (laminar) | — |
| VMFL002 laminar pipe, uniform heat flux | `simpleFoam` + `scalarTransport` T, **axisymmetric 5° wedge**, laminar mercury — `cases/ansys_verification/VMFL002/PREREGISTRATION.md:8-11,35` | axisym · steady · incompressible (laminar) | **forced conv · laminar · axisym** |
| VMFL003 / VMFL003-M2 (arms A–D) turbulent pipe | `simpleFoam`, k-ε / realizableKE / RNG / kOmegaSST + `nutkWallFunction`, axisym wedge (mesh `L3_1000x5`), Δp vs Moody/Colebrook — register rows #6, #9–#12 | axisym · steady · incompressible (turbulent) | — |
| VMFL004 / -R2 Couette–Poiseuille | `simpleFoam`, steady incompressible laminar, ν = 1, Cartesian 2-D — `cases/ansys_verification/VMFL004/PREREGISTRATION.md:45,106-109` | 2D · steady · incompressible (laminar) | — |
| VMFL005 Poiseuille pipe | `simpleFoam`, axisym wedge `L3_400x40`, Hagen–Poiseuille dP — register row #3 | axisym · steady · incompressible (laminar) | — |
| VMFL007 non-Newtonian pipe | `simpleFoam`, axisym wedge, power-law (Rabinowitsch–Mooney) — register row #8 | axisym · steady · incompressible (laminar, non-Newtonian) | — |
| VMFL010 90° tee | `simpleFoam`, steady laminar incompressible, planar branch — `cases/ansys_verification/VMFL010/PREREGISTRATION.md:24-30,46` | 2D · steady · incompressible (laminar) | — |
| VMFL011 triangular cavity | `simpleFoam`, steady laminar, **Re = 400** — `cases/ansys_verification/VMFL011/PREREGISTRATION.md:43-44` | 2D · steady · incompressible (laminar) | — |
| VMFL017 RAE 2822 | `rhoSimpleFoam` + kOmegaSST, steady, 2-D C-mesh, **transonic** (magUInf 253.5 m/s) — `cases/ansys_verification/VMFL017/PREREGISTRATION.md:8-9,22,32` | 2D · steady · transonic (turbulent) | — |
| VMFL019 Stokes' first problem | `icoFoam`, transient laminar, ν = 1e−3, 1-D bar — `cases/ansys_verification/VMFL019/PREREGISTRATION.md:25` | 2D · unsteady · incompressible (laminar; 1-D) | — |
| VMFL021 / -R2, VMFL022 cavitating orifice | `interPhaseChangeFoam` / SchnerrSauer / k-ε, **axisymmetric 5° wedge** — `cases/ansys_verification/VMFL021/PREREGISTRATION.md:16-18,46-50`; `VMFL022/PREREGISTRATION.md:15-17,53-61` | axisym · steady · multiphase-free-surface (cavitation, turbulent) | — |
| VMFL023 oscillating cylinder | `pimpleFoam`, **Re = 100**, St from lift zero-crossings — `cases/ansys_verification/VMFL023/PREREGISTRATION.md:17,24-27` | 2D · unsteady · incompressible (laminar) | — |
| VMFL033 viscous heating annulus | `buoyantSimpleFoam` (rhoConst), laminar, **2-D planar, NOT an axisymmetric wedge**, Re 3.3e−3 — `cases/ansys_verification/VMFL033/PREREGISTRATION.md:20,57-62,80,126` | 2D · steady · incompressible (laminar) | **forced conv (viscous dissipation) · laminar · 2D** |
| VMFL036 sphere | `simpleFoam`, steady laminar, **axisymmetric wedge**, Re = 100 — `cases/ansys_verification/VMFL036/PREREGISTRATION.md:18,43,51` | axisym · steady · incompressible (laminar) | — |
| VMFL045 / -R2 oblique shock ramp | `rhoCentralFoam`, **inlet Mach ≈ 2.5**, 15° ramp, laminar (μ = 1e−8) — `cases/ansys_verification/VMFL045/PREREGISTRATION.md:47-48`; register row #7 | 2D · steady · supersonic | — |
| VMFL050 semi-infinite slab | `laplacianFoam`, transient conduction, 1-D bar — `cases/ansys_verification/VMFL050/PREREGISTRATION.md:29-30` | — | **conduction · (no flow) · 2D (1-D bar)** · unsteady |
| VMFL051 Prandtl–Meyer corner | `rhoCentralFoam`, inviscid, post-expansion **M = 3.237** target, 2-D — `cases/ansys_verification/VMFL051/PREREGISTRATION.md:41,45`; register row #4 | 2D · steady · supersonic | — |
| VMFL059 composite block | `laplacianFoam` steady limit, Cartesian planar 2-D — `cases/ansys_verification/VMFL059/PREREGISTRATION.md:25,61-62` | — | **conduction · (no flow) · 2D** · steady |
| VMFL064 / -R2 asymmetric expansion | `simpleFoam`, laminar, **Re_D = 200**, Cartesian planar 2-D — `cases/ansys_verification/VMFL064/PREREGISTRATION.md:4,41-44,66` | 2D · steady · incompressible (laminar) | — |
| VMFL076 flat plate, low Pr | `simpleFoam` laminar + `scalarTransport`, **Re_L = 9.0e4, Pe_L = 270**, planar 2-D — `cases/ansys_verification/VMFL076/PREREGISTRATION.md:21,76-77,108,174` | 2D · steady · incompressible (laminar) | **forced conv · laminar · 2D** |

## 2. Every register row (HEAD `eadbe157`), mapped

| # | case | class (cfd cell / heat cell) | register verdict | what the record says (lab value → reference; triple) | record path @ sha; grading artifact |
|---|---|---|---|---|---|
| 1 | VMFL001 | 2D·steady·incompressible | **`NOT A RESULT`** | **Comparator refusal (exit 2)** — frozen reader expected `U_gateAxis.*` with a header, v2606 wrote header-less `gateAxis_p_U.xy`; independently L3 missed the 1e−6 residual clause. No number produced. | `cases/ansys_verification/VMFL001/RESULTS.md` @ `ebb7da5a`; `verification/runs/ansys_verification/VMFL001/GRADING_VMFL001.stdout.txt` |
| 2 | VMFL001-R2 | 2D·steady·incompressible | **`PASS`** (credential) | v_θ at r = 20/25/30/35 mm 0.0151121 / 0.0105288 / 0.0071835 / 0.0045458 m/s vs White §3-2.3 analytic 0.0151/0.0105/0.0072/0.0046, all inside 2 %; **CONVERGING, p = 2.0102, GCI_fine 0.0563 %**, Richardson extrapolate on exact to 3.7 ppm (register §tier table). | `cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196` |
| 3 | VMFL005 | axisym·steady·incompressible | **`PASS`** (credential) | dP = 10.2909853852 Pa vs Hagen–Poiseuille 10.24 Pa (0.498 %, band 2 %); **CONVERGING, p 1.9341, GCI_fine 0.0502 %**; extrapolate 0.538 % from exact — deviation/GCI 9.92, so the code is measured NOT to converge to exact (register tier note; coverage §3.6). | `cases/ansys_verification/VMFL005/RESULTS.md` @ `4bb0f6a1`; `verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json` |
| 4 | VMFL051 | 2D·steady·supersonic | **`NOT A RESULT`** | Ma = 3.2294 (L3 zone average) vs 3.2370 target — in band, but **G absent: triple not CONVERGING** (register tier table: "V present, G ABSENT, and G decides it"). Physics ran; rule 5 took it. | `cases/ansys_verification/VMFL051/RESULTS.md` @ `63c8d044`; `verification/runs/ansys_verification/VMFL051/GRADING_VMFL051.json` |
| 5 | VMFL045 run 1 | 2D·steady·supersonic | **`NOT A RESULT`** | `rhoCentralFoam` **crashed on its first timestep** (`Entry 'e' not found in fvSolution/solvers`) — a case-file defect inherited from the inviscid VMFL051; nothing gradeable. | `cases/ansys_verification/VMFL045/RESULTS.md` @ `64b02355` |
| 6 | VMFL003 | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | Δp = 20 800.82 Pa vs 21 744 Pa (−4.34 %, band 2.5 %: `gate_verdict_before_rule5 = GATE FAIL`); **comparator refused at rule 5 step 1 — all three levels failed the frozen residual leg** (ε 2.52e−08 vs 1e−08 at L3). Model statement beside it: k-ε under-predicts pipe friction −4.6 % vs Colebrook. | `cases/ansys_verification/VMFL003/RESULTS.md` @ `288a5862`; `verification/runs/ansys_verification/VMFL003/GRADING_VMFL003.json` |
| 7 | VMFL045-R2 | 2D·steady·supersonic | **`PASS`** (credential; tier `GATE REACHED` inline) | M₂ = 1.874779 at L3 vs 1.874 (band 1 %), per level 1.87198 / 1.87453 / 1.87478; **observed order 3.3862 — measured but NOT trusted** as G (register row text). | `cases/ansys_verification/VMFL045/R2/RESULTS.md` @ `f4332fe3` |
| 8 | VMFL007 run 1 | axisym·steady·incompressible (non-Newtonian) | **`NOT A RESULT`** | **DIVERGED** — inlet pressure grew 3.02e4 → 9.45e+… over 10 000 iterations with rc 0 and `End`; no number. A physics/setup failure, not a refusal. | `cases/ansys_verification/VMFL007/RESULTS.md` @ `2793f23e` |
| 9 | VMFL003-M2 arm A (k-ε) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | Δp = 20 800.82 Pa, −4.34 % vs target (−4.55 % vs Colebrook); **refused at the residual leg** (L3 ε 2.49e−08 vs 1e−08); the endTime bump did not fix it. | `cases/ansys_verification/VMFL003_M2/GRADING_LANE_REPORT.md` @ `64b367ef` |
| 10 | VMFL003-M2 arm B (realizableKE) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | Δp = 20 278.13 Pa, −6.74 % (**realizableKE under-predicts friction more than k-ε**); **refused at the residual leg** (L3 k 1.38e−07, ε 7.49e−08). | same lane report @ `64b367ef` |
| 11 | VMFL003-M2 arm C (RNG k-ε) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | **Ladder incomplete — the frozen 40 core-min per-arm cap fired** at `Time = 4085` of 18 000 (22.7 %); no Δp graded; no fresh cap (rule 12). Ruled `aba61e53`. | `cases/ansys_verification/VMFL003_M2/TRIAGE_ARM_D_BUDGET_STOP.md` @ `2dcea996` |
| 12 | VMFL003-M2 arm D (kOmegaSST) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | **Ladder incomplete — cap fired to the second** at `Time = 5949` of 22 000 (27 %); L3 ran 7× over its mesh scaling; no Δp graded. Ruled `2dcea996`. | same triage @ `2dcea996` |
| 13 | VMFL019 | 2D·unsteady·incompressible (1-D) | **`PASS`** (credential) | u_x(0.05 m, 5 s) = 6.16765e−3 (dev 0.050 %) and u_x(0.10 m, 5 s) = 3.17008e−3 m/s (dev 0.095 %) vs U·erfc(·), band 1 %; **both triples CONVERGING, p 1.0933 / 0.9881, GCI_fine 0.058 % / 0.121 %** (space and time refined together). | `cases/ansys_verification/VMFL019/RESULTS.md` @ `f3fad674`; `verification/runs/ansys_verification/VMFL019/GRADING_VMFL019.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 14 | VMFL010 | 2D·steady·incompressible | **`NOT A RESULT`** | flow split 0.88475 vs 0.887 (0.26 %, band 3 % — value-only reading would be inside); **triple OSCILLATORY** (0.88595 / 0.88445 / 0.88475) → rule 5 step 2, no GCI. Physics ran; rule 5 took it. | `cases/ansys_verification/VMFL010/RESULTS.md` @ `f3fad674`; `verification/runs/ansys_verification/VMFL010/GRADING_VMFL010.stdout.txt` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 15 | VMFL050 | **heat: conduction · 2D (1-D bar) · unsteady** | **`PASS`** (credential; tier capped `GATE REACHED` by a frozen clause) | wall T = 392.977 K (0.023 % on the rise) and T(150 mm) = 318.401 K (0.006 %) vs Incropera analytic, band 1 % on the rise; **both triples CONVERGING** — wall p 0.6883, p150 **p 5.5982** (noise-floor order → ceiling `GATE REACHED`, `HOLDS` refused). | `cases/ansys_verification/VMFL050/SUPERVISOR_RULING_VERDICT.md` @ `311feb37`; `verification/runs/ansys_verification/VMFL050/GRADING_VMFL050.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 16 | VMFL059 | **heat: conduction · 2D · steady** | **`NOT A RESULT`** | cooled wall 378.0 K vs 378 K and adiabatic wall 412.948 K vs 413 K — solve clean at all levels; **`rightWall` triple EXACT (378.0 / 378.0 / 378.0)** → rule 5; *"a MIS-SPECIFIED GATE QUANTITY, not a failed solve"*. | `cases/ansys_verification/VMFL059/SUPERVISOR_RULING_VERDICT.md` @ `6a9afa0a` |
| 17 | VMFL022 case B | axisym·steady·multiphase (cavitation) | **`NOT A RESULT`** | L3 Cd = 0.75918 vs Nurick 0.780 (band 5 %); **triple OSCILLATORY** (0.74442 / 0.76091 / 0.75918), p and GCI `None` → rule 5. Physics ran. | `verification/runs/ansys_verification/VMFL022/LANE_REPORT_opus48_collision.md` @ `2e83a89b`; `verification/runs/ansys_verification/VMFL022/GRADING_VMFL022.json` |
| 18 | VMFL021 attempt 1 | axisym·steady·multiphase (cavitation) | **`NOT A RESULT`** | Run cannot be certified (two independent instrument defects) although the physics was going right (Cd 0.663 → 0.642 toward 0.620, stable at P1 = 2.5e8 Pa). Re-run registered as row #23. | register row only (no separate RESULTS path at HEAD) |
| 19 | VMFL017 | 2D·steady·transonic | **`PENDING`** | **`rhoSimpleFoam` DIVERGES** (`Negative initial temperature T0`); no gradeable run; a queue state, NOT a softened `GATE FAIL`. | `cases/ansys_verification/VMFL017/RESULTS.md` @ `f746233a` |
| 20 | VMFL036 | axisym·steady·incompressible | **`GATE REACHED`** (not a credential) | Cd = 1.088834 at L3 (49 152 cells) vs Mittal (1999) 1.0895, band 3 %; **CONVERGING** 1.091486 / 1.089233 / 1.088834, r = 2 by construction; ceiling `GATE REACHED` frozen on prereg lines 3–4 (numerical-benchmark reference); arm B (μ = 0.02 as printed) shows the manual's μ is a transcription error. | `cases/ansys_verification/VMFL036/RESULTS.md` @ `a86357e6` |
| 21 | VMFL033 | 2D·steady·incompressible / **heat: forced conv (viscous heating) · laminar · 2D** | **`NOT A RESULT`** | T_avg(finest) = 286.8955 K; **two of three levels NOT PLATEAUED** (ptp/rise 6.5e−05 and 7.8e−03 vs a frozen 1e−06 floor) and **triple OSCILLATORY (R = −398.5)** → rule 5 step (1); the prereg named this failure before compute. Comparator repaired under §2d.1 before grading (8 mutants × 2 interpreters). | `cases/ansys_verification/VMFL033/RESULTS.md` @ `f5a81a69` |
| 22 | VMFL023 | 2D·unsteady·incompressible | **`GATE REACHED`** (not a credential) | St = 0.165993 at L3 (384 × 128) vs 0.165 (experimental St–Re correlation, White / Kim & Lee), band 3 %; **CONVERGING, p = 1.9140 vs formal 2, GCI 0.3791 %**. | `cases/ansys_verification/VMFL023/RESULTS.md` @ `c487e3c7` |
| 23 | VMFL021-R2 case A | axisym·steady·multiphase (cavitation) | **`GATE REACHED`** (not a credential) | Cd = 0.634868 at L3 vs Nurick 0.620 (2.398 %, band 5 %); **CONVERGING, p = 1.7405 vs formal 1, GCI 0.5524 %**; all three levels PLATEAU; 32.93 core-min. | `cases/ansys_verification/VMFL021/R2/RESULTS.md` @ `c487e3c7` |
| 24 | VMFL002 | axisym·steady·incompressible / **heat: forced conv · laminar · axisym** | **`GATE REACHED`** (not a credential) | dP = 1.000 Pa and centreline outlet T = 341.00 K vs manual targets 1.000 Pa / 341.00 K (White 1994 / Incropera 1981), both inside 2 % at L3, **both triples CONVERGING**; 5.2 core-min. | `cases/ansys_verification/VMFL002/RESULTS.md` @ `959a31b1`; `verification/runs/ansys_verification/VMFL002/GRADING_VMFL002.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 25 | VMFL004 | 2D·steady·incompressible | **`NOT A RESULT`** | **Frozen-instrument block, L-338 class:** volAverage(U)_x 2.50125 / 2.5003125 / 2.5000781 vs exact 2.5, **CONVERGING p = 1.99999997**, rel_dev 3.1e−5 ≪ 0.1 % band — a textbook PASS — but the inherited check gated Uy/p initial residuals (< 1e−7), which are normalisation NOISE in 1-D fully-developed flow. Not edited (rule 2); re-run is row #28. | `cases/ansys_verification/VMFL004/RESULTS.md` @ `959a31b1`; `verification/runs/ansys_verification/VMFL004/GRADING_VMFL004.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 26 | VMFL011 | 2D·steady·incompressible | **`NOT A RESULT`** | **Comparator refusal, L-340 class:** planted-zero control on `rms_vs_benchmark` (401-point RMS) moved 3.68e−7 < 0.1·plant → refused (exit 2). Physics beside it, not a verdict: rms 0.0403 / 0.0348 / 0.0341 all exceed the 3 % band (would be `GATE FAIL`); `u_min` triple CONVERGING p 1.60, extrapolate −0.3465 vs digitised −0.318 (8.9 %, OPEN). | `cases/ansys_verification/VMFL011/RESULTS.md` @ `cb5b6eb8` |
| 27 | VMFL076 | 2D·steady·incompressible / **heat: forced conv · laminar · 2D** | **`NOT A RESULT`** | **"BOTH GATES WERE MET AND RULE 5 TOOK THE ROW ANYWAY"** — Gate A |I_lab − I_ref|/I_ref = 0.9006 % vs frozen 3.00 %, Gate B 5.397e−03 vs its band; verdict `NOT A RESULT` on the triple state. Physics ran; rule 5 took it. | `cases/ansys_verification/VMFL076/RESULTS.md` @ `9c86962e`; `verification/runs/ansys_verification/VMFL076/GRADING_OUTPUT.txt` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 28 | VMFL004-R2 | 2D·steady·incompressible | **`PASS`** (credential) | volAverage(U)_x = 2.50007812 m/s vs exact 2.5, band 0.1 %; **CONVERGING on errors 5.00e−4 / 1.25e−4 / 3.13e−5, p = 1.99999760, GCI_fine 3.906e−5**; transverse mean ≤ 1e−6 clause met; four planted controls fired. Re-registration of row #25 gating on the driven Ux. | `cases/ansys_verification/VMFL004-R2/RESULTS.md` @ `6a0a1a99`; `verification/runs/ansys_verification/VMFL004-R2/GRADING_VMFL004_R2.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 29 | VMFL064 | 2D·steady·incompressible | **`NOT A RESULT`** | **Comparator refusal (exit 2) at L3: "wall shear never changes sign — no reattachment found"**; all three levels ran clean (`SIMPLE solution converged` at 424 / 907 / 2 152 iterations); no triple, no GCI, no value vs Armaly et al. (1983) LR/s = 5 (band 10 %). Not a solver failure. Calibration C-131. | `cases/ansys_verification/VMFL064/RESULTS.md` @ `b8b5e2bf`; `verification/runs/ansys_verification/VMFL064/GRADING_ATTEMPT_REFUSED.txt` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |

**Register census at HEAD `eadbe157` (recomputed from the rows, not read from the count line — the file's last printed count line reads "5 PASS of 16 run" and predates rows #17–#29):** **29 rows: `PASS` 6** (#2, #3, #7, #13, #15, #28), **`GATE REACHED` 4** (#20, #22, #23, #24), **`NOT A RESULT` 18**, **`PENDING` 1** (#19), `GATE FAIL` 0 (two rows carry `gate_verdict_before_rule5 = GATE FAIL`, #6 and #9, and closed `NOT A RESULT`). Of the 18 `NOT A RESULT`: **comparator/instrument refusals 7** (#1, #6, #9, #10, #25, #26, #29), **cap-fired ladders 2** (#11, #12), **crash / divergence 2** (#5, #8), **uncertifiable instrument 1** (#18), **rule 5 on a non-CONVERGING or EXACT triple with the physics clean 6** (#4, #14, #16, #17, #21, #27).

## 3. What the rows put into each grid cell (evidence for the cfd and heat-transfer tables — the family supervisors rule, this is the record's reading)

| cell | rows | reading in Sanaa's words |
|---|---|---|
| **2D · steady · incompressible** | #2 `PASS`, #28 `PASS`, #1/#14/#25/#26/#29 `NOT A RESULT` | **CAN DO — 2 cases**; strongest **VMFL001-R2** (`cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196`): exact-solution check at four radii, p = 2.0102, GCI 0.056 %, extrapolate on exact to 3.7 ppm — the lab's nearest row to HOLDS (coverage §3.8f). Checked: error vs exact + GCI + order. Caveat: exact-solution references only (V, never P); VMFL064's experimental reattachment is unread (refusal). |
| **2D · unsteady · incompressible** | #13 `PASS`, #22 `GATE REACHED` | **CAN DO — 1 case** (VMFL019 @ `f3fad674`, erfc exact, both triples CONVERGING) with VMFL023 St = 0.166 vs 0.165 experimental correlation `GATE REACHED` beside it (p 1.914, GCI 0.38 %). |
| **2D · steady · supersonic** | #7 `PASS`, #4 / #5 `NOT A RESULT` | **CAN DO, CAVEATS — 1 case** (VMFL045-R2 @ `f4332fe3`, M₂ = 1.87478 vs 1.874); caveat: observed order 3.39 measured but not trusted (G held back); VMFL051 Prandtl–Meyer in band but triple not CONVERGING. |
| **2D · steady · transonic** | #19 `PENDING` | **CAN NOT DO — attempted**: `rhoSimpleFoam` diverges (negative T0) on RAE 2822; nothing graded. |
| **axisym · steady · incompressible** | #3 `PASS`; #20 `GATE REACHED`; #6/#8/#9–#12 `NOT A RESULT` | **CAN DO, CAVEATS — 1 `PASS`** (VMFL005 @ `4bb0f6a1`, p 1.934, GCI 0.050 %) + sphere Cd `GATE REACHED`; caveats: VMFL005's extrapolate is measured NOT to converge to exact (deviation/GCI 9.92); **turbulent pipe: 0 of 6 arms graded** — three refusals on the residual leg, two cap-fired, all k-ε family −4.3…−6.7 % vs Moody; non-Newtonian pipe diverged. |
| **axisym · steady · multiphase-free-surface** (cavitation) | #23 `GATE REACHED`; #17 / #18 `NOT A RESULT` | **CAN DO, CAVEATS — 0 `PASS`, 1 `GATE REACHED`** (VMFL021-R2 @ `c487e3c7`, Cd 0.6349 vs Nurick 0.620, CONVERGING p 1.74, GCI 0.55 %); caveats: cavitation not free surface; case B triple OSCILLATORY; no `PASS`. |
| **heat: conduction · 2D** | #15 `PASS` (unsteady, 1-D bar), #16 `NOT A RESULT` (steady) | **CAN DO — 1 case** (VMFL050 @ `311feb37`, erfc exact, both triples CONVERGING; tier capped by a frozen noise-floor clause); steady composite wall EXACT triple → rule 5 (gate quantity mis-specified, solve clean). |
| **heat: forced conv · laminar · axisym** | #24 `GATE REACHED` | **CAN DO, CAVEATS — 0 `PASS`, 1 `GATE REACHED`** (VMFL002 @ `959a31b1`, dP and 41 K outlet rise both inside 2 %, both triples CONVERGING); caveat: reference is the manual's analytic target, tier ceiling. |
| **heat: forced conv · laminar · 2D** | #21, #27 `NOT A RESULT` | **CAN NOT DO — attempted 2**: VMFL076 met both gates and was taken by rule 5 on the triple; VMFL033 two levels not plateaued, triple OSCILLATORY. What would fix it: a plateau-clean ladder (VMFL033 L3 settled to 2e−08 already; L1/L2 need the same). |

**Structural note carried from the coverage matrix (§3.8f), still true at HEAD:** every `PASS` row is an `AN` (analytic) reference — **P (validation against measured physical reality) is green in no ansys row**; the experiment-referenced rows are VMFL064 (refused), VMFL023 (correlation, `GATE REACHED`), VMFL021/022 (Nurick, `GATE REACHED` / `NOT A RESULT`), VMFL017 (`PENDING`).

---

## Footer — the planted control: every cited sha, resolved

Run from the repository root; every line must read `ok`, and the count must equal the number of distinct shas cited above (26):

```
for s in eadbe157 ebb7da5a 5e789196 4bb0f6a1 63c8d044 64b02355 288a5862 f4332fe3 2793f23e 64b367ef aba61e53 2dcea996 f3fad674 311feb37 6a9afa0a 2e83a89b c487e3c7 f746233a a86357e6 f5a81a69 959a31b1 cb5b6eb8 9c86962e 6a0a1a99 b8b5e2bf 068c2bf0; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

(26 shas listed; 26 distinct commits. A `MISSING` line is a defect in this file, not in the record.) Reading at write time, 2026-08-26: 26 ok, 0 MISSING, 26 distinct shas; 27 verdict tokens re-read from `git show <sha>:<path>` and matched.

---

## Correction 2 — 2026-08-26, verification lane ansys-rows: register row #30 (87afd1d6) mapped; census recomputed at HEAD 8c7e1854

**Lines whose number changed above this section: 0.**

Appended by verification lane `ansys-rows` for the verification-supervisor. Zero compute. Everything below was read with `git show <sha>:<path>`; neither the worktree nor the shared index was used. **Numbering note:** no "Correction 1" section exists in this file at HEAD `8c7e1854` (the file's only prior commit is `b847b97f`); this section carries the number its supervisor assigned. **Blob identity, checked:** the register blob at HEAD `8c7e1854` is `0dabcdda…`, identical to the blob at `87afd1d6` (the last commit that touched the register), so "`@ 8c7e1854`" and "`@ 87afd1d6`" cite the same register bytes; likewise `cases/ansys_verification/VMFL064-R2/RESULTS.md` is blob `48c19ae6…` at both shas, and `VMFL064-R2/PREREGISTRATION.md` at HEAD is blob `abe17c3b…`, the blob its own RESULTS names, with `3e7c792c` the only commit that ever touched it.

### C2.1 Register row #30, read from the register at HEAD

Row #30 is one physical line — `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md:513 @ 8c7e1854`; the column header that names the 13 columns is `:22`. Every field below is from `:513` unless another line is named.

| field | reading (`ANSYS_VALIDATION_REGISTER.md:513 @ 8c7e1854`) |
|---|---|
| case | **VMFL064-R2** — Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion (VM2026R1, p. 195/196); "Re-registration of row #29 under `ANSYS_VERIFICATION_CHARTER` §6: a NEW row that CITES row #29 and does NOT overwrite it — row #29 stands as `NOT A RESULT` and is unchanged by this row" |
| date | 2026-08-26 |
| verdict token, verbatim | **`GATE REACHED`** |
| lab value | `LR/s` = **4.853056** at L3 (49 152 cells; `LR` = 0.023779973479 m); deviation **2.9389 %** of a 10 % band ("consuming 29 % of the tolerance"); triple 4.714416 / 4.800738 / 4.853056, d21 = 0.086322377043, d32 = 0.052317864523, R = 0.606075, **`CONVERGING` and monotone**; `p_obs` = 0.722431; `GCI_fine` = 2.0733 % at Fs = 1.25; Richardson `f_ex` = 4.933550 |
| reference (source, manual page) | `LR/s` = **5** — "**EXPERIMENTAL**: Armaly, Durst, Pereira & Schoenung, *J. Fluid Mech.* **127**:473, 1983 (also Freitas, *J. Fluids Eng.* **117**, p. 208, 1995). **REFERENCE KIND: measured/experimental — CAN buy P**, and this row still does **not**, because the ceiling was lowered in advance"; Ansys Fluent 4.91 "CONTEXT ONLY, never the gate"; manual **p. 195** |
| tolerance (frozen) | `abs(LR/s − 5.0) / 5.0 ≤ 0.10` (10 %) at the finest level **and** a `CONVERGING` triple (rule 5); "BYTE-IDENTICAL to attempt 1's band"; tier ceiling **`GATE REACHED`** "declared on pre-registration line 4 and hard-coded in the comparator, which cannot print `PASS` or `HOLDS`"; "NOT A CREDENTIAL"; cap **90 core-min** |
| artifact path | `verification/runs/ansys_verification/VMFL064-R2/GRADING_VMFL064_R2.json` (with `{L1,L2,L3}/`, `RUN_RC.{L1,L2,L3}`, `COST.txt`, `LAUNCH_RECORD.txt`, `CONTENTION.txt`, `CAP_OVERRUN.txt`, `STATUS.VMFL064-R2`, `STATUS.VMFL064-R2.attempt1-refused-no-run_root`, `launcher.queue.out`, `launcher.queue.out.attempt1`). **This grading artifact IS at HEAD** (`git ls-tree HEAD` lists `GRADING_VMFL064_R2.json` plus `CAP_OVERRUN.txt`, `CONTENTION.txt`, `COST.txt`, `LAUNCH_RECORD.txt`, `RUN_RC.L1/L2/L3`, both `STATUS.*` files) — unlike the eight on-disk-only artifacts flagged in §2. |
| prereg sha | **`3e7c792cbde23a7cc105d63d01487dc5d01c8040`** ("the only commit that has ever touched that pre-registration, and it landed before any R2 solver started"); prereg blob `abe17c3b990acd31bba12fde01aaf757c6ab398e` |
| comparator sha | blob **`e04fdf937d557b4919928ab72b9fe5eb42f8b49a`** ("the launcher printed `freeze OK` against this blob before every level"); launcher blob `c17ee2e2693b382fd043aadc326bdae8e51fd7b6` |
| cost, core-min | **5.3** MEASURED (L1 0.0167 + L2 0.2833 + L3 5.0; wall 318 s × RANKS 1 ÷ 60) vs **5.4** predicted → ratio **0.98**; 5.9 % of the 90 core-min cap; WASTE 0.000; $0.0045 derived, not measured |
| RESULTS path | `cases/ansys_verification/VMFL064-R2/RESULTS.md`; calibration **C-141** (`docs/COST_CALIBRATION.md:217 @ 87afd1d6`) |

**From the record itself — `cases/ansys_verification/VMFL064-R2/RESULTS.md @ 87afd1d6` (214 lines):**

- Verdict headline, `:20`: `## VERDICT — \`GATE REACHED\``.
- Value vs reference, `:22-23`: "**`LR/s = 4.853056`** at the finest level against the experimental reference **5.0** — **2.9389 %** deviation inside the frozen **10 %** band, on a **`CONVERGING`** triple." Per level, `:40-42`: L1 3 072 cells 4.714416 (corner vortex resolved: no; crossings 1/0), L2 12 288 cells 4.800738 (no; 1/0), L3 49 152 cells 4.853056 (**yes**; 1/1). Gate at L3, `:44-45`: 2.9389 % against 10.00 % — met.
- Triple / order / GCI, `:51-54`: d21 = 0.086322377043, d32 = 0.052317864523, R = 0.606075 → `CONVERGING` (monotone, 0 < R < 1); `p_obs = 0.722431`, `GCI_fine (Fs = 1.25) = 2.0733 %`, `f_extrapolated = 4.933550`. `:57`: "**`p_obs = 0.7224` is BELOW the formal `p_f = 2`, and that is reported as what it is.**" `:61-64`: above the registered floor `P_MIN = 0.05` so a GCI is quoted; "2.0733 % is of the same order as the 2.9389 % deviation itself … not that the reattachment length has been pinned to three digits."
- What changed relative to row #29 (the refusal), `:68-72`: row #29 died at "`REFUSED (exit 2): L3: wall shear never changes sign -- no reattachment found`"; "The R2 changed the reader to the **last** crossing inside a registered window, and nothing else." `:74-79`: `corner_vortex_resolved` false at L1 and L2, true at L3; crossing census `n→p = 1, p→n = 0` at the coarse levels, `n→p = 1, p→n = 1` at L3 with the profile starting positive — "the mechanism named in row #29's triage, measured here rather than argued." `:81-84`: L1 4.714416 and L2 4.800738 "identical to the values row #29 published as the only two that existed."
- Reference kind — **experiment**, not analytic and not a correlation. `:25-26`: "The reference is experimental (Armaly et al. 1983) and experimental references *can* buy P". Pre-registration `cases/ansys_verification/VMFL064-R2/PREREGISTRATION.md:31 @ 3e7c792c`: `3. REFERENCE KIND  : measured/experimental -- CAN buy P.` The manual's own source: `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt:5071-5073 @ 8c7e1854` — "Reference  B. Armaly, F. Durst, J. Pereira, B. Schönung. "Experimental and theoretical investigation of a backward-facing step". Journal of Fluid Mechanics, Vol 127, pg. 473, 1983" (Freitas 1995 at `:5075-5076`); `:5086`: "The reattachment length predicted by the solvers is validated against experimental results"; the results table `:5123`: "Non-dimensionalized Reattachment length (LR/Step-height)  5.0  4.91  0.982" (Target / Ansys Fluent / Ratio).
- Why `GATE REACHED` and not `PASS`, `:25-30`: "**`GATE REACHED` is the ceiling, and it is not a `PASS`.** … pre-registration line 4 declared the ceiling `GATE REACHED` in advance because this team's product is **reproducing the Ansys manual**, and the comparator hard-codes that string: it cannot print `PASS` or `HOLDS` whatever the number. **This row is not a credential and must not be counted as one.**" (`PREREGISTRATION.md:32-35 @ 3e7c792c` says the same: "Sanaa's ruling caps that at GATE REACHED. The comparator hard-codes GATE REACHED as the in-band verdict; it cannot print HOLDS or PASS.") `:182`: "It is not a credential. Ceiling `GATE REACHED`, declared before compute."
- Cost, `:125-131`: total 318 s, 5.3 core-min measured vs 5.4 predicted, ratio 0.98, 5.9 % of cap; `:133`: waste 0.000; `:136-138`: $0.0045 derived, C-141.

### C2.2 Its class

**cfd cell: 2D · steady · incompressible (laminar)** — confirmed from the R2 pre-registration `cases/ansys_verification/VMFL064-R2/PREREGISTRATION.md @ 3e7c792c` (= HEAD blob): `:24-25` "Solver = simpleFoam (OpenFOAM v2606), steady laminar SIMPLEC, Re_D = 200, 2-D Cartesian"; `:60` "simpleFoam, laminar (momentumTransport = laminar), SIMPLEC consistent yes"; `:63` "Inlet uniform 0.288462 m/s (Re_D = 200.0 on D = 10.4 mm)"; `:70` "z = 1 cell (2-D). SERIAL, RANKS = 1"; `:87` "WEDGE/GEOM BIAS: N/A (Cartesian planar 2-D, not an axisymmetric wedge; N-AV9 does not apply)". The attempt-1 lines §1 cites, `cases/ansys_verification/VMFL064/PREREGISTRATION.md:4,41-44,66 @ 8c7e1854`, agree: `:4` "laminar, Re_D = 200"; `:41` "z is 1 empty cell (2-D)"; `:43-44` "Solver `simpleFoam` (steady incompressible laminar, SIMPLEC `consistent yes`)"; `:66` "Cartesian planar 2-D, not an axisymmetric wedge". The §1 row "VMFL064 / -R2" therefore stands as written; this section adds the R2 prereg citation beside it. **Heat-transfer cell: —** (none; isothermal momentum solve, no temperature gate — the file's convention for "none").

**Row #30 in the §2 format (appended here, not inserted above):**

| # | case | class (cfd cell / heat cell) | register verdict | what the record says (lab value → reference; triple) | record path @ sha; grading artifact |
|---|---|---|---|---|---|
| 30 | VMFL064-R2 | 2D·steady·incompressible | **`GATE REACHED`** (not a credential; ceiling frozen on prereg line 4) | `LR/s` = 4.853056 at L3 (49 152 cells) vs **experimental** Armaly et al. (1983) 5.0 — 2.9389 %, band 10 %; **CONVERGING** 4.714416 / 4.800738 / 4.853056, `p_obs` 0.7224 (below formal 2, above floor 0.05), **GCI_fine 2.0733 %** — the same order as the deviation. Re-registration of row #29: reader changed from FIRST to LAST wall-shear crossing in a window `0 < x ≤ 0.05 m`; corner vortex present at L3 only, confirming #29's diagnosis; L1/L2 values unchanged. 5.3 core-min. | `cases/ansys_verification/VMFL064-R2/RESULTS.md` @ `87afd1d6`; `verification/runs/ansys_verification/VMFL064-R2/GRADING_VMFL064_R2.json` (at HEAD `8c7e1854`) |

### C2.3 Census recomputed at HEAD `8c7e1854` from the Verdict column

Method: `git show HEAD:verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` piped to a small python that takes every line beginning `|`, splits it on **unescaped** pipes only (`re.split(r'(?<!\\)\|', …)` — the Case cell of rows #7 and #21 contains `\|`, and a naive `split('|')` mis-columns exactly those two rows), keeps lines whose first cell is a bare integer (`**n**`), and reads the FIRST backticked fixed-vocabulary token (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`) in the 4th cell, the `Verdict` column named at `:22`. Row #7's cell reads `PASS` first with `GATE REACHED` as an inline tier, so it counts as `PASS` — the same reading §2 made.

Per row (#, register line, case → token): #1 `:24` VMFL001 → NOT A RESULT · #2 `:25` VMFL001-R2 → PASS · #3 `:26` VMFL005 → PASS · #4 `:27` VMFL051 → NOT A RESULT · #5 `:28` VMFL045 run 1 → NOT A RESULT · #6 `:29` VMFL003 → NOT A RESULT · #7 `:30` VMFL045-R2 → PASS · #8 `:32` VMFL007 run 1 → NOT A RESULT · #9 `:34` VMFL003-M2 arm A → NOT A RESULT · #10 `:36` arm B → NOT A RESULT · #11 `:37` arm C → NOT A RESULT · #12 `:38` arm D → NOT A RESULT · #13 `:39` VMFL019 → PASS · #14 `:40` VMFL010 → NOT A RESULT · #15 `:41` VMFL050 → PASS · #16 `:42` VMFL059 → NOT A RESULT · #17 `:43` VMFL022 → NOT A RESULT · #18 `:44` VMFL021 attempt 1 → NOT A RESULT · #19 `:45` VMFL017 → PENDING · #20 `:433` VMFL036 → GATE REACHED · #21 `:460` VMFL033 → NOT A RESULT · #22 `:461` VMFL023 → GATE REACHED · #23 `:462` VMFL021-R2 → GATE REACHED · #24 `:463` VMFL002 → GATE REACHED · #25 `:464` VMFL004 → NOT A RESULT · #26 `:465` VMFL011 → NOT A RESULT · #27 `:466` VMFL076 → NOT A RESULT · #28 `:467` VMFL004-R2 → PASS · #29 `:468` VMFL064 → NOT A RESULT · #30 `:513` VMFL064-R2 → GATE REACHED.

**Totals at HEAD `8c7e1854`: 30 numbered rows, 30 entries, no row number missing or duplicated. `PASS` 6** (#2, #3, #7, #13, #15, #28) · **`GATE REACHED` 5** (#20, #22, #23, #24, #30) · **`NOT A RESULT` 18** (#1, #4, #5, #6, #8–#12, #14, #16, #17, #18, #21, #25, #26, #27, #29) · **`PENDING` 1** (#19) · `GATE FAIL` 0 · `BLOCKED` 0; sum 30. **This matches the supervisor's expectation (30: 6 / 5 / 18 / 1) exactly**, and it matches the register's own re-derived count in its struck-headline paragraph at `:47 @ 8c7e1854` ("30 rows … `PASS` 6 … `GATE REACHED` 5 … `NOT A RESULT` 18 … `PENDING` 1 … Credential count: 6 PASS of 30 run"). Relative to the §2 census at `eadbe157`: one row added, `GATE REACHED` 4 → 5, every other class unchanged; the breakdown of the 18 `NOT A RESULT` (refusals 7, cap-fired 2, crash/divergence 2, uncertifiable 1, rule 5 on a clean solve 6) is unchanged because row #30 is not in that class. **Credentials remain 6; row #30 adds none.**

### C2.4 The `2D · steady · incompressible` cell in §3, re-read

Old line (§3, struck here, not edited above):

~~| **2D · steady · incompressible** | #2 `PASS`, #28 `PASS`, #1/#14/#25/#26/#29 `NOT A RESULT` | **CAN DO — 2 cases**; strongest **VMFL001-R2** (`cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196`): exact-solution check at four radii, p = 2.0102, GCI 0.056 %, extrapolate on exact to 3.7 ppm — the lab's nearest row to HOLDS (coverage §3.8f). Checked: error vs exact + GCI + order. Caveat: exact-solution references only (V, never P); VMFL064's experimental reattachment is unread (refusal). |~~

New line:

| cell | rows | reading in Sanaa's words |
|---|---|---|
| **2D · steady · incompressible** | #2 `PASS`, #28 `PASS`, **#30 `GATE REACHED`**, #1/#14/#25/#26/#29 `NOT A RESULT` | **CAN DO — 2 cases**; strongest **VMFL001-R2** (`cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196`): exact-solution check at four radii, p = 2.0102, GCI 0.056 %, extrapolate on exact to 3.7 ppm — the lab's nearest row to HOLDS (coverage §3.8f). Checked: error vs exact + GCI + order. **New beside it, row #30 VMFL064-R2 (`cases/ansys_verification/VMFL064-R2/RESULTS.md` @ `87afd1d6`): the first experiment-referenced row in this cell to reach its gate — the P channel — `LR/s` 4.853 vs Armaly et al. (1983) 5.0, 2.94 % of a 10 % band, CONVERGING, GCI 2.07 %; still `GATE REACHED`, not `PASS`, because the tier ceiling was frozen at `GATE REACHED` on prereg line 4 before compute (this team's product is reproducing the Ansys manual, and Sanaa's ruling caps that tier) and the comparator hard-codes that string and cannot print `PASS` or `HOLDS` (RESULTS `:25-30`). Not a credential; P is reached, not banked.** Caveat: the two `PASS` rows are exact-solution references only (V); the one P-channel row is capped by ruling, and its GCI (2.07 %) is the same order as its deviation (2.94 %), so the reattachment length is not pinned to three digits (RESULTS `:61-64`). VMFL064 attempt 1 (#29) stays a refusal on record. |

**Structural note (§3), updated for row #30 — the old sentence is otherwise unchanged:** "every `PASS` row is an `AN` (analytic) reference — P is green in no ansys row" is **still true at HEAD `8c7e1854`** (the six `PASS` rows are unchanged). The list of experiment-referenced rows now reads: **VMFL064 (#29 refused; #30 R2 `GATE REACHED`, experimental Armaly 1983, in band on a CONVERGING triple, ceiling-capped)**, VMFL023 (correlation, `GATE REACHED`), VMFL021/022 (Nurick, `GATE REACHED` / `NOT A RESULT`), VMFL017 (`PENDING`). Row #30 is the first experiment-referenced ansys row in the 2D·steady·incompressible cell to reach its gate; per the register `:513` it "CAN buy P, and this row still does not, because the ceiling was lowered in advance."

### C2.5 Footer extension — the planted control on the shas this section adds

New commit shas cited in this section: `87afd1d6` (row #30 + RESULTS + C-141), `3e7c792c` (R2 prereg freeze), `b847b97f` (this file's own commit), `8c7e1854` (HEAD at write time). `eadbe157` was already in the footer list. Run from the repository root, same form as the footer:

```
for s in 87afd1d6 3e7c792c b847b97f 8c7e1854; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at write time, 2026-08-26: `87afd1d6 ok` · `3e7c792c ok` · `b847b97f ok` · `8c7e1854 ok` — 4 ok, 0 MISSING. The original 26-sha loop re-run at the same time: 26 ok, 0 MISSING. **Distinct commit shas cited by this file: 26 + 4 = 30.** The three blob ids cited above (`abe17c3b`, `e04fdf93`, `c17ee2e2`) are blobs, not commits, and are deliberately outside the `^{commit}` loop; `git cat-file -t` on each reads `blob` (3 of 3). A `MISSING` line is a defect in this file, not in the record.

---

## Correction 3 — 2026-08-26, ansys-verification lane `ansys-lane-opus`: register rows #31 and #32 mapped; row #30 CONFIRMED already mapped by Correction 2; census recomputed at HEAD `c7aea761`

**Lines whose number changed above this section: 0.**

Appended by the `ansys-verification` team's Opus lane on the supervisor's dispatch. Zero compute
beyond the two gradings this section records. Everything below was read with
`git show <sha>:<path>`; neither the worktree nor the shared index was used (L-333: the worktree
copies of these ledgers have repeatedly been behind HEAD, and one of them — `docs/COST_CALIBRATION.md`
— was measured stale by exactly one row during this lane's own work).

**The dispatch asked for row #30 to be mapped here. It is already mapped, and I am not mapping it
twice.** Correction 2 above maps row #30 (VMFL064-R2, `GATE REACHED`, `87afd1d6`, backward-facing
step, `2D · steady · incompressible`) in §C2.1/§C2.2, and I re-read that entry against the register
row at HEAD `c7aea761` and against `cases/ansys_verification/VMFL064-R2/RESULTS.md`: **it is
correct and complete — verdict token, `LR/s` = 4.853056, 2.9389 % of a 10 % band, `CONVERGING`
4.714416 / 4.800738 / 4.853056, `p_obs` 0.722431, `GCI_fine` 2.0733 %, prereg `3e7c792c`, comparator
blob `e04fdf93`, 5.3 core-min, C-141 — all match.** A duplicate entry would put two rows numbered 30
in this file and would be a defect, so this section maps **#31 and #32 only** and records the check
instead.

### C3.1 Rows #31 and #32 in the §2 format (appended here, not inserted above)

| # | case | class (cfd cell / heat cell) | register verdict | what the record says (lab value → reference; triple) | record path @ sha; grading artifact |
|---|---|---|---|---|---|
| 31 | VMFL011-R2 | 2D·steady·incompressible (laminar) | **`NOT A RESULT`** | **Comparator refusal (exit 2) on the planted-zero control for `u_min_norm`**, verbatim: `planted -0.1234 into …/L1/postProcessing/bisector/20000/bisect_U.xy, reader moved by only 0.` **No value, no triple, no `p_obs`, no GCI** — the refusal preceded every channel read, so nothing is quoted against the digitised Jyotsna & Vanka (1995) `u_min/U_wall` = −0.318062 (band: `rms_vs_benchmark` ≤ 0.030 at L3). Re-registration of row #26: the **L-340 plant SIZING repair worked and is measured on the real attempt-1 bytes** (sized plant delta 1.185698e-01 > threshold 3.221137e-02, inside the derived bounds [8.052843e-02, 1.610569e-01]; the parent pair still refuses at 3.677091e-07 < 1.234000e-04). **The refusal came from the OTHER channel — a SECOND, DISTINCT L-340 failure mode: plant LOCATION, not plant MAGNITUDE.** `_perturb` plants into the FIRST data row of the bisector, which on the real profile is the collapsed-hex apex at y = −4 m where `u ≡ 0`, so −0.1234 sits above `min(u) = −0.528988913215` and a `min()` reader cannot move. It was never caught at the freeze because both comparators build channels in the same dict order (rms first) and attempt 1 exited 2 inside the first entry — **the `u_min` plant had never once run on real VMFL011 bytes.** Strict completion (rule 4) HOLDS at all three levels (rc = 0, one `End`, last `Time` 20000 == `endTime`, `U`/`p` present, `ExecutionTime` count 20000, age guard): **the instrument refused; the solver did not fail.** 9.0833 core-min vs 8.3 predicted, ratio 1.094. | `cases/ansys_verification/VMFL011-R2/RESULTS.md` @ `77096fe8`; `verification/runs/ansys_verification/VMFL011-R2/GRADING.txt` (**at HEAD** `c7aea761`; no grading JSON exists — the comparator exited before writing one); prereg `9f9d6925`, prereg blob `a8c9b6f3…`, comparator blob `45aa4613…`; calibration **C-144** |
| 32 | VMFL017-R2 | **2D·unsteady·transonic (turbulent)** — see §C3.2, this CORRECTS §1's cell for the R2 | **`NOT A RESULT`** | **Registered per-level cap fired (`rc = 124` after 18 000 wall s = 300.0 core-min), launcher stopped without launching L2 or L3, and the frozen comparator REFUSED (exit 2) on strict completion**, verbatim: `REFUSE (VMFL017-R2): no End line in solver log: …/VMFL017/R2/L1`. **No `Cd`, no `Cl`, no plateau window, no triple, no GCI** — L1 reached **1.778 %** of its registered `endTime`, so nothing is quoted against AGARD AR-138 `Cd` = 0.0168 / `Cl` = 0.803 (bands 10 % and 5 %). **A MEASURED INSTRUMENT LIMIT, NOT A FAILED SOLVE, and predicted by name before compute** (PRE-COMPUTE AMENDMENT 2 §E at `45328f8a`). **What it buys is a cost measurement, and all three of §E's pre-compute figures held:** physical time reached 8.89114e-04 s vs projected ~9.0e-04 s (**0.988**); 27.04 steps/wall-s (486 748 steps in 17 999 s) vs projected ~27.7 (**0.976**); **16 871 core-min for L1 ALONE to reach `endTime`** vs projected ~16 700 (**1.010**) — **about 56× L1's own cap**. Realised Δt at the stop 1.852520264e-09 s. **Contention falsified as the cause, measured:** `ExecutionTime` 17 761.7 s vs `ClockTime` 17 999 s = **98.68 % CPU-bound**. Cites row #19 (attempt 1, `PENDING`), which is unchanged. 300.0 core-min vs 300.0 registered, ratio 1.000 — **a cap, not a forecast, and not banked as a calibration win.** | `cases/ansys_verification/VMFL017/R2/RESULTS.md` @ `fd975fcf`; `verification/runs/ansys_verification/VMFL017/R2/GRADING.txt` (**at HEAD** `c7aea761`; no grading JSON, no `COST.txt` — the launcher stopped on the cap before writing one; `L1/log.rhoCentralFoam` is 504 MB and stays on disk only); prereg `45328f8a`, prereg blob `9a58eed3…`, comparator blob `97c556f4…`, mesh birth certificate `2a7e82c2…`; calibration **C-149** |

### C3.2 Their classes, and one correction to §1

**Row #31 — `2D · steady · incompressible (laminar)`; heat cell: —.** Unchanged from §1's VMFL011
line and confirmed from the R2 pre-registration `cases/ansys_verification/VMFL011-R2/PREREGISTRATION.md
@ 9f9d6925` (= HEAD blob `a8c9b6f3…`): line 1 "Solver = simpleFoam (OpenFOAM v2606), steady
incompressible laminar SIMPLEC, Re = U_wall*base/nu = 2*2/0.01 = 400, 2-D"; line 8 "SERIAL, RANKS = 1";
line 11 "N/A (planar 2-D Cartesian, not an axisymmetric wedge)".

**Row #32 — `2D · unsteady · transonic (turbulent)`; heat cell: —. THIS CORRECTS §1's VMFL017 cell for
the R2, and the correction is a solver change, not a re-reading.** §1 maps VMFL017 as
"`rhoSimpleFoam` + kOmegaSST, **steady**, 2-D C-mesh, transonic" — which is right for **attempt 1
(register row #19, `PENDING`)** and wrong for the R2. The supervisor's ladder ruling switched the
instrument to **`rhoCentralFoam`, which is explicit and TRANSIENT**:
`cases/ansys_verification/VMFL017/R2/PREREGISTRATION.md @ 45328f8a` line 1 "Solver = rhoCentralFoam
(OpenFOAM v2606), kOmegaSST RAS, hePsiThermo/perfectGas, **TRANSIENT explicit** (adjustTimeStep,
maxCo), shock-capturing. 2D C-mesh"; line 8 "TRANSIENT; endTime a **physical settling time** (not
iterations), adjustTimeStep, maxCo"; line 11 "N/A (2D Cartesian C-mesh, planar in z, empty
frontAndBack — not axisymmetric)". **The time axis of the cell therefore moves from `steady` to
`unsteady` for row #32 while row #19 keeps `steady`** — the same manual case occupying two different
grid cells because the lab ran it on two different instruments. **Nothing above is edited**; §1's
line stands as written and is corrected here by appending, which is what this file's own convention
requires.

**Consequence for §3's grid reading, stated and NOT applied above.** The `2D · unsteady · transonic`
cell is now **occupied and empty-handed**: one row, `NOT A RESULT`, no value. That is a genuine
capability statement — **the lab has attempted transonic RAE 2822 twice, on two different solvers,
and has produced no number either time** — and it should not be read as "CAN DO". The
`2D · steady · incompressible` cell gains row #31 as a further `NOT A RESULT` and its "CAN DO — 2
cases" reading (from §C2.4) is **unchanged**, because #31 adds no credential and removes none.

### C3.3 Census recomputed at HEAD `c7aea761` from the Verdict column

Same method as §C2.3 — `git show HEAD:verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`
split on **unescaped** pipes only (`re.split(r'(?<!\\)\|', …)`, because the Case cells of rows #7 and
#21 contain `\|` and a naive `split('|')` mis-columns exactly those two), keeping lines whose first
cell is a bare `**n**`, and reading the first backticked fixed-vocabulary token.

**Totals at HEAD `c7aea761`: 32 numbered rows, 32 entries, no row number missing or duplicated.**
**`PASS` 6** (#2, #3, #7, #13, #15, #28) · **`GATE REACHED` 5** (#20, #22, #23, #24, #30) ·
**`NOT A RESULT` 20** (#1, #4, #5, #6, #8–#12, #14, #16, #17, #18, #21, #25, #26, #27, #29, **#31**,
**#32**) · **`PENDING` 1** (#19) · `GATE FAIL` 0 · `BLOCKED` 0; sum **32**. Row #31 is register line
`:549`, row #32 is `:574`.

**The credential count does NOT move: 6 `PASS` of 32 run.** Both new rows are `NOT A RESULT`. The
register's own headline still reads "6 PASS of 30 run" and is **deliberately not struck** — the
standing instruction strikes it only when the `PASS` count changes — so its **denominator is two
behind by design**, recorded in the register's own dated notes for rows #31 and #32 and repeated
here so a reader of this file alone is not misled.

**The reading these two rows share, and it is worth the space.** Neither is a solver failure. Row
#31's instrument refused because a control had never been exercised on real bytes; row #32's
instrument ran flawlessly for five hours and simply cannot afford the physics at the registered
`endTime`. **Two different ways to spend compute and buy no number — one a grading defect, one an
honest cost measurement — and the point of this file is that neither of them reads as a capability.**

### C3.4 Footer extension — the planted control on the shas this section adds

New commit shas cited in this section: `77096fe8` (row #31 + RESULTS + C-144), `fd975fcf` (row #32 +
RESULTS + C-149), `9f9d6925` (VMFL011-R2 prereg freeze), `45328f8a` (VMFL017-R2 prereg freeze),
`db2c7f9a` (the run records landed at HEAD for the rows that cited them). `3e7c792c` and `87afd1d6`
were already in §C2.5's list. Run from the repository root, same form as the footer:

```
for s in 77096fe8 fd975fcf 9f9d6925 45328f8a db2c7f9a; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at write time, 2026-08-26: 77096fe8 ok · fd975fcf ok · 9f9d6925 ok · 45328f8a ok · db2c7f9a ok  — 5 ok, 0 MISSING. **Distinct commit shas cited by
this file: 26 + 4 + 5 = 35.**
