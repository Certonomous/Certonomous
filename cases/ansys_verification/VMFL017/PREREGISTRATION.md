# PRE-REGISTRATION — VMFL017 — Transonic Flow over an RAE 2822 Airfoil

Template-speed standard form (docs/ansys_verification/PREREG_TEMPLATE.md, incl. Amendments 1-3).
Frozen file under CLAUDE.md rule 6.

```
1. CASE            : VMFL017 — Transonic Flow over an RAE 2822 Airfoil — manual p.69.
                     Solver=rhoSimpleFoam (OpenFOAM v2606), kOmegaSST, steady,
                     hePsiThermo/perfectGas. 2D C-mesh, freestream far-field BCs.
                     NOT YET RUN; verification/runs/ansys_verification/VMFL017/ absent at 2026-08-25T22:03:00Z.
2. REFERENCE       : Cd = 0.0168 and Cl = 0.803. Source = P.H. Cook, M.A. McDonald,
                     M.C.P. Firmin, "Aerofoil RAE 2822 — Pressure Distribution and Boundary
                     Layer and Wake Measurements", AGARD AR-138, 1979. Ansys Fluent reported
                     Cd 0.016 (ratio 0.952), Cl 0.78 (0.971) — CONTEXT ONLY.
3. REFERENCE KIND  : measured/experimental → CAN buy P (AGARD AR-138 wind-tunnel data;
                     Sanaa's ruling: the manual is a public primary source).
4. TIER CEILING    : HOLDS — measured reference; BOTH bands met at a CONVERGING finest level
                     is a validation credential (verdict PASS). Realistic expectation given
                     transonic drag's mesh/convergence sensitivity is GATE REACHED.
5. QUANTITIES      : Cd (drag) and Cl (lift) coefficients from OpenFOAM's forceCoeffs function
                     object on the 'aerofoil' patch, time-averaged over the last 20% of SIMPLE
                     iterations (steady window). rhoInf=0.50823, magUInf=253.4664, lRef=Aref=1,
                     dragDir=(cos2.79,sin2.79,0), liftDir=(-sin2.79,cos2.79,0). Forces are read
                     DIRECTLY from OpenFOAM — no cell-centre radius or constructed geometry
                     enters the gate (supervisor standing instruction; not a wedge case).
6. BANDS (THE GATE): |Cd_lab − 0.0168|/0.0168 ≤ 0.10 AND |Cl_lab − 0.803|/0.803 ≤ 0.05, at the
                     finest CONVERGING level. Justification (NOT from a run): the manual's own
                     Fluent is 4.8% off on Cd and 2.9% on Cl; transonic DRAG carries larger
                     numerical uncertainty (shock position + boundary-layer resolution) than
                     lift, so Cd gets 10% (~2x the manual's own gap + grid) and Cl gets 5%
                     (~the manual's own gap + margin). BOTH must hold for PASS.
7. LADDER          : rhoSimpleFoam / kOmegaSST + freestream far-field. Air (manual p.69):
                     molWeight 28.966, Cp 1006.43, mu 1.983e-5, Pr 0.8247 (=Cp*mu/k, k=0.0242).
                     Mesh: birth-certified ratio-2 C-mesh family built from the in-repo RAE 2822
                     ordinates (verification/runs/F12_runs/reference/rae2822_coordinates.dat,
                     NPARC/AGARD AR-138 Table 6.1, cross-checked to 3.1e-6 chord) via the closure
                     team's birth-certified recipe (F12 mesh_ladder_attempt2). Geometry is a
                     PUBLIC reference, reused with provenance; the solver result is what is verified.
8. DECOMPOSITION   : r=2 triple L1/L2/L3 = 23040 / 92160 / 368640 cells (mult 1/2/4). SERIAL
   SEED              (RANKS=1; no RNG). Steady SIMPLE; endTime 6000 iters or residualControl,
                     whichever first. Single-grid if only L1 is run — verdict is then single-grid.
9. PRINCIPAL RISK  : TRANSONIC DRAG SENSITIVITY + UNDER-RESOLUTION. Cd is set by shock position
                     and skin friction; a coarse mesh over-predicts drag and a partly-converged
                     SIMPLE run has a swinging Cd/Cl. MEASURED in a scratch smoke: coarse L1 at
                     ~150 iters gave Cd~0.09 (5x target) and Cl swinging 0.2-0.9 — NOT converged.
                     The PREDICTED failure is that a coarse/under-converged level gives Cd far
                     from 0.0168 (GATE FAIL or, if not plateaued, NOT A RESULT). The gate is met
                     only at a fine, fully-converged level; the plateau check (rule 5) refuses a
                     non-steady window rather than average through a transient.
9a. PHYSICS CHECK  : (MANDATORY, supervisor directive) Governing groups = M and Re. From the
   (INDEPENDENT)     manual's OWN inputs (p=43765 Pa, T=300 K, M=0.73, air R=287.04 from
                     MW=28.966, mu=1.983e-5, c=1 m): a=sqrt(gRT)=347.2, U=M*a=253.47 m/s,
                     rho=p/RT=0.5082, Re=rho*U*c/mu=6.496e6 — matches the manual's stated
                     Re=6.5e6 to 0.06%. THE MANUAL'S STATED INPUTS ARE SELF-CONSISTENT.
10. EXPECTED ORDER : p_f ~ 2 (linearUpwind momentum) but the shock and upwind turbulence cap the
                     effective order; expect p_obs in [1,2]; p_obs > 2.3 SUSPICIOUSLY HIGH.
11. WEDGE/GEOM BIAS: N/A (2D Cartesian C-mesh planar in z, empty frontAndBack — not axisymmetric).
12. COST + CAP     : estimate ~800 core-min TOTAL for the full family (L1 coarse ~40 min, L2
                     medium ~160 min, L3 fine ~600 min; serial; smoke-calibrated), reported-by-
                     owner basis (c7a.4xlarge $0.0513/core-h; dollars DERIVED, not measured).
                     PER-LEVEL RUNAWAY CAPS (NOT a shared drawdown — supervisor's anti-starvation
                     directive 2026-08-25): L1 90, L2 300, L3 900 core-min; each level records its
                     remaining budget AT LAUNCH; a disproportionate level is reported before the
                     next launches; endTime/tolerance are NEVER silently reduced to fit a cap.
13. CONTROLS       : grade_vmfl017.py --selftest green; planted-zero PLANT=7.531e-3 fires in the
                     comparator (rule 3); strict completion (End + age guard + converged-or-endTime
                     for a STEADY solver) (rule 4); Roache triple gating on BOTH Cd and Cl (rule 5);
                     LAUNCHER FREEZE CHECK of prereg+comparator vs HEAD, each || exit 1 (rule 2 /
                     Amendment 2); per-level cap enforcement with remaining-at-launch recorded
                     (Amendment 3 item 2 + supervisor anti-starvation); NO set -u (item 3); mesh
                     birth certificate (item 5); smoke_launcher_vmfl017.sh exercises the launcher
                     itself, L1 with a short-iteration override on scratch (item 6).
```
