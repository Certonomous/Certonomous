# Sail panel stats: study-naca0015_sail (solved record)

Internal note for transcribing onto the website panel. The NUMBERS
go on the panel; the source paths below are internal only and must
never appear in the website text itself.

| Quantity | Value | Source |
|---|---|---|
| Convergence | iteration 138 of a 300 budget ("SIMPLE solution converged in 138 iterations") | mission-output/geometry-study/study-naca0015_sail/log.simpleFoam |
| p residual, last iteration | initial 3.03e-05, final 9.84e-08 | mission-output/geometry-study/study-naca0015_sail/log.simpleFoam, Time = 138 block |
| Ux residual, last iteration | initial 1.23e-05, final 6.49e-07 | mission-output/geometry-study/study-naca0015_sail/log.simpleFoam, Time = 138 block |
| Uy residual, last iteration | initial 9.41e-05, final 7.31e-06 | mission-output/geometry-study/study-naca0015_sail/log.simpleFoam, Time = 138 block |
| Uz residual, last iteration | initial 9.60e-05, final 6.80e-06 | mission-output/geometry-study/study-naca0015_sail/log.simpleFoam, Time = 138 block |
| k residual, last iteration | initial 4.33e-05, final 3.70e-06 | mission-output/geometry-study/study-naca0015_sail/log.simpleFoam, Time = 138 block |
| omega residual, last iteration | initial 2.19e-05, final 1.31e-06 | mission-output/geometry-study/study-naca0015_sail/log.simpleFoam, Time = 138 block |
| Residual convergence criterion | initial residuals below 1e-4 for all fields (p, U, k, omega) | mission-output/geometry-study/study-naca0015_sail/case/system/fvSolution, residualControl |
| Cd (solved) | 0.01015 +/- 4e-06 (95% envelope [0.01015, 0.01016], settle window 27; final sample 0.01015084) | mission-output/geometry-study/study-naca0015_sail/report.md; mission-output/geometry-study/study-naca0015_sail/log.simpleFoam (the act's copy of the WSL case /home/foam/certonomous-runs/study-naca0015_sail-16e5ff, postProcessing/forceCoeffs1/0/coefficient.dat) |
| Cl (solved) | -0.0002874 +/- 1.6e-06 (95% envelope [-0.000289, -0.0002858], settle window 27; final sample -0.00028823) | mission-output/geometry-study/study-naca0015_sail/report.md; mission-output/geometry-study/study-naca0015_sail/log.simpleFoam (the act's copy of the WSL case /home/foam/certonomous-runs/study-naca0015_sail-16e5ff, postProcessing/forceCoeffs1/0/coefficient.dat) |
| Mesh cells | 243,929 | mission-output/geometry-study/study-naca0015_sail/log.checkMesh |
| Turbulence model | kOmegaSST | mission-output/geometry-study/study-naca0015_sail/case/constant/turbulenceProperties |
| Freestream | U_inf = 75.0 m/s, chord 1.2 m, Re 6.0e6 | mission-output/geometry-study/study-naca0015_sail/case/0/U; scripts/run_sail_study.py |

Footer line for the panel: "AUTO-MESH - K-OMEGA SST - 243,929 CELLS".

Notes: residuals are the solver's own linear-solver report at the
final iteration; "initial" is the quantity the convergence
control (1e-4) acts on, "final" is where the last sweep left the
field. For p (two correctors per iteration) the initial residual
is the first solve's and the final residual the last solve's.
