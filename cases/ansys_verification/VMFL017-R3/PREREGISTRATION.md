# VMFL017-R3 — PRE-REGISTRATION (frozen before compute; CLAUDE.md rule 2)

Transonic Flow over an RAE 2822 Airfoil. Ansys Fluid Dynamics Verification
Manual, Release 2026 R1, **p. 69**. Title-page verified against the PDF (rule 15):
"Ansys Fluid Dynamics Verification Manual", Release 2026 R1, March 2026,
© 2026 Synopsys/ANSYS — matches the sidecar footer. Frozen file (rule 6): after
first graded compute, only dated addenda that cannot alter gate, threshold, cap or
label.

## THE NAME IS R3, NOT R2 — an obvious brief-label slip, corrected against HEAD evidence

The dispatch brief said "VMFL017-R2". **That name is already taken:** VMFL017-R2 is
**register row #32**, a GRADED verdict (`NOT A RESULT`) committed at HEAD
(`cases/ansys_verification/VMFL017/R2/`, freeze `45328f8a`). Reusing it would collide
with a registered row. Every other signal in the brief points at the R3 successor:
the base is register **row #19** (VMFL017, `rhoSimpleFoam`, `PENDING`); the brief's
deliverable 4 says "Move VMFL017 **OWED-DATED-PLAN** → REGISTERED", and the ONLY
VMFL017 OWED-DATED-PLAN entry in `docs/ansys_verification/FIX_SUCCESSOR_REGISTRY.md`
is the **VMFL017-R3** row. So the successor is **VMFL017-R3**, and the brief's "-R2"
is a label slip. This is surfaced for the supervisor's §3 diff-read; if the supervisor
intends a different name, this freeze is pre-compute and struck-not-rewritten (rule 6).

## The ladder so far, and why R3 keeps rhoCentralFoam (the failure was COST, not physics)

- **Row #19 (VMFL017, `rhoSimpleFoam`, `PENDING`):** the pressure-based steady solver
  DIVERGED — `FOAM FATAL ERROR: Negative initial temperature T0` inverting energy to
  temperature across the forming shock (~150–540 iters, every attempt). Named as the
  principal risk before compute. Row #19 stays exactly as it is.
- **Row #32 (VMFL017-R2, `rhoCentralFoam`, `NOT A RESULT`):** the supervisor switched
  to the density-based shock-capturing solver. It CAPTURED THE SHOCK WITH NO
  TEMPERATURE BLOW-UP — the physics was right — but graded `NOT A RESULT` on **COST**:
  the birth-certified **y+ ~ 0.5 (low-Re) mesh** (wall-normal grading last/first ratio
  **4 401 087**, first cell ≈ 2.0e-6 m) forced the explicit acoustic-CFL step to
  **Δt ≈ 1.85e-9 s**, so L1 alone reached only 1.778 % of `endTime` inside its 300
  core-min cap — ≈ 16 871 core-min would have been needed for L1 to reach `endTime`,
  ~56× its cap. Row #32's OWN pre-registration named the remedy as a **DIFFERENT
  registration**: *"a wall function raising the near-wall cell by three decades."*
- **This registration (VMFL017-R3) IS that remedy.** The supervisor's standing ruling
  (adopted here) is to keep `rhoCentralFoam` — the density-based shock-capturing
  instrument is the right one for an embedded transonic shock, and the manual itself
  (p.69) uses *"the implicit formulation of the density-based solver … SST k-ω …
  steady state"*. The dated-plan's alternative (return to `rhoSimpleFoam`) is
  superseded by that ruling: row #19 already showed the pressure-based solver diverges
  on this shock, and the fix for row #32's failure is a mesh change, not a solver
  change. **The ONE change from row #32 is the mesh: y+ ~ 0.5 → y+ ~ 30 wall functions.**

## FIX-UNTIL-RUNS EVIDENCE (§2ay; Sanaa 2026-09-06: "the only acceptable reason for a fail is if OpenFOAM can't do the case") — MEASURED, answer-blind, before this freeze

An ephemeral answer-blind smoke (scratch only; run root never created; the graded Cd/Cl
NEVER read for grading — read only to confirm bounded, non-diverging forces) established
that `rhoCentralFoam` + `kOmegaSST` wall functions + the high-Re y+ ~ 30 mesh RUNS the
transonic RAE 2822 case within a feasible cost:

| quantity | row #32 (y+~0.5, measured) | R3 smoke (y+~30, measured) | effect |
|---|---|---|---|
| explicit adaptive Δt | 1.85e-9 s | **1.866e-7 s** | **~100× larger step** |
| L1 core-min to reach `endTime` 0.05 s | ≈ 16 871 | **≈ 132** (267 900 steps / 33.9 steps·wall-s⁻¹ / 60) | **~128× cheaper** |
| temperature blow-up (row #19 failure mode) | — | **NONE** — zero `bounding T` / `bounding e` / negative-T events over 8136 steps | shock captured, stable |
| max Courant | — | **0.20** (capped, stable) | stable |
| wall y+ (aerofoil, `yPlus` FO) | ~0.5 | **avg ≈ 43–51, max ≈ 53–66**, min ~3–10 at stagnation | in the log-law band |
| forces (NOT read for grading) | — | bounded, physical O(0.1), no NaN/divergence | developing, not settled |

The only bounding events were routine `bound(k)` (turbulent KE floored to a positive
value — normal early-transient RANS behaviour, benign). `checkMesh` on all three levels:
`Mesh OK`, max aspect ratio 337/321/298 (LOWER than the low-Re family's 805), max
non-orthogonality ~35.3 (self-similar), max skewness 0.85/0.83/0.80. **rhoCentralFoam
CAN do this case; the acceptable-fail clause is not triggered.**

## The ten-line freeze (PREREG_TEMPLATE standard form + all four amendments)

```
1. CASE            : VMFL017-R3 — Transonic Flow over an RAE 2822 Airfoil —
                     manual p.69. Solver = rhoCentralFoam (OpenFOAM v2606),
                     kOmegaSST RAS, hePsiThermo/perfectGas, TRANSIENT explicit
                     (adjustTimeStep, maxCo 0.2), shock-capturing (Kurganov +
                     vanLeer). 2D C-mesh, characteristic far-field, HIGH-Re
                     WALL-FUNCTION near-wall (y+ ~ 30, held constant across levels).
                     NEW ROW citing row #32 (VMFL017-R2, NOT A RESULT, rhoCentralFoam,
                     freeze 45328f8a) and row #19 (VMFL017, PENDING, rhoSimpleFoam,
                     d1de064b). NOT YET RUN; verification/runs/ansys_verification/
                     VMFL017-R3/ absent at 2026-09-07 (checked: dir does not exist).
2. REFERENCE       : Cd = 0.0168 and Cl = 0.803. Source = P.H. Cook, M.A.
                     McDonald, M.C.P. Firmin, "Aerofoil RAE 2822 — Pressure
                     Distribution and Boundary Layer and Wake Measurements",
                     AGARD AR-138, 1979. Ansys Fluent Cd 0.016 (0.952), Cl 0.78
                     (0.971); CFX Cd 0.0162 (0.9662), Cl 0.7981 (0.9339) —
                     CONTEXT ONLY, never the gate.
3. REFERENCE KIND  : measured/experimental → CAN buy P (AGARD AR-138 wind-tunnel
                     data; the manual is a public primary source).
4. TIER CEILING    : GATE REACHED. Team ceiling (Sanaa). A measured reference could
                     in principle buy HOLDS/validation with BOTH bands met at a
                     CONVERGING finest level, but transonic drag's mesh/settling
                     sensitivity AND the wall-function skin-friction approximation
                     make GATE REACHED the realistic and registered ceiling.
5. QUANTITIES      : Cd (drag) and Cl (lift) from OpenFOAM's forceCoeffs function
                     object on the 'aerofoil' patch, time-averaged over the final
                     settled window of PHYSICAL TIME. rhoInf=0.50823 kg/m3,
                     magUInf=253.4664 m/s, lRef=Aref=1 m, dragDir=(0.998814,
                     0.048685,0), liftDir=(-0.048685,0.998814,0), alpha=2.79 deg.
                     Forces read DIRECTLY from OpenFOAM — no constructed geometry
                     enters the gate.
6. BANDS (THE GATE): |Cd_lab − 0.0168|/0.0168 ≤ 0.10 AND |Cl_lab − 0.803|/0.803
                     ≤ 0.05, at the finest CONVERGING level. BYTE-IDENTICAL to
                     row #32's gate (L-487: do not move a gate you did not have to
                     move). Justification (NOT from a run): the manual's own Fluent
                     is 4.8% off on Cd and 2.9% on Cl; transonic DRAG carries larger
                     numerical uncertainty (shock position + skin friction, now via a
                     wall function) than lift, so Cd gets 10% and Cl gets 5%. BOTH
                     must hold.
7. LADDER          : rhoCentralFoam / kOmegaSST + characteristic far-field. Air
                     (manual p.69): molWeight 28.966, Cp 1006.43, mu 1.983e-5,
                     Pr = Cp*mu/k = 0.8247 (k=0.0242). energy sensibleInternalEnergy
                     (e); fvSolution provides an "(e|h)" energy solver (VMFL045 row #5
                     lesson: a viscous rhoCentralFoam case needs the e entry). WALL
                     FUNCTIONS: nut nutUSpaldingWallFunction (continuous, valid y+
                     1–300), k kLowReWallFunction (blended), omega omegaWallFunction,
                     alphat compressible::alphatWallFunction. Mesh: a NEW birth-
                     certified high-Re C-mesh family — the frozen row #19/#32
                     blockMeshDicts with ONLY the wall-normal grading token replaced
                     (first cell 2.0e-6 → 2.5e-4 m, y+ ~ 30), same geometry/topology/
                     cell counts. See cases/ansys_verification/VMFL017-R3/mesh_birth/
                     BIRTH_CERTIFICATE.md. Geometry is a PUBLIC reference (AGARD
                     AR-138) reused with provenance; the solver result is verified.
8. DECOMPOSITION   : r=2 triple L1/L2/L3 = 23040 / 92160 / 368640 cells (mult
   SEED              1/2/4), SAME cell counts as rows #19/#32 for direct
                     comparability. SERIAL (RANKS=1; no RNG). The wall-normal FIRST
                     CELL is held at y+ ~ 30 on ALL THREE levels (grading 23969 /
                     11414 / 5306.57 for ny 80/160/320) — a wall-function-consistent
                     family: the levels refine streamwise + wall-normal-count while
                     the near-wall y+ is held ~constant, so the triple is an
                     admissible convergence study for a wall-function result.
                     TRANSIENT; endTime a physical settling time (not iterations),
                     adjustTimeStep, maxCo 0.2. Single-grid if <3 levels are run —
                     verdict then single/partial-grid, family PENDING for GCI.
9. PRINCIPAL RISK  : (a) transonic DRAG via a WALL FUNCTION — skin friction is now
                     modelled, not resolved, so Cd may miss the 10% band → GATE FAIL;
                     (b) the shock-turbulence interaction produces a temporal ripple
                     that does not settle within the cap → NOT A RESULT (the plateau
                     clause refuses a non-settled window, never averages through it);
                     (c) the wall y+ drifts out of the log-law band on a level → NOT A
                     RESULT (the y+ regime precondition, line 13). The PREDICTED
                     honest outcome, given wall-function drag sensitivity, is
                     GATE REACHED (bands met) or GATE FAIL (Cd out of band), NOT a cost
                     failure — the smoke measured L1 at ~132 core-min to endTime,
                     inside its cap.
9a. PHYSICS CHECK  : (carried forward from row #19, PASSED) Governing groups M and
   (INDEPENDENT)     Re, from the manual's OWN inputs (p=43765 Pa, T=300 K, M=0.73,
                     air R=287.04 from MW=28.966, mu=1.983e-5, c=1 m): a=√(γRT)=347.2,
                     U=253.47 m/s, ρ=0.5082 kg/m3, Re=ρUc/μ=6.496e6 vs the manual's
                     stated 6.5e6 — 0.06%. Self-consistent.
10. EXPECTED ORDER : p_f ~ 1 EXPECTED — an embedded shock is a genuine discontinuity;
                     a conservative shock-capturing scheme has O(h) shock-position
                     error that pollutes the integrated forces at first order (same
                     reasoning as VMFL045). p_obs in [0.5,1.5]; p_obs > 2.0
                     SUSPICIOUSLY HIGH (flagged, not celebrated). Observed-order floor
                     P_MIN=0.05: a triple below it is NOT A RESULT with NO GCI.
11. WEDGE/GEOM BIAS: N/A (2D Cartesian C-mesh, planar in z, empty frontAndBack —
                     not axisymmetric).
12. COST + CAP     : COST DRIVER IS THE CFL-LIMITED TIMESTEP TO A SETTLED STATE
                     (rhoCentralFoam is explicit/transient). SMOKE-MEASURED, not
                     guessed: L1 Δt ≈ 1.866e-7 s, 33.9 steps/wall-s, ≈ 132 core-min to
                     reach endTime 0.05 s. Projected family (L2 ~4× cells × finer
                     streamwise; L3 ×4 again): ~ 1056 / ~ 8500 core-min. PER-LEVEL
                     caps (NOT a shared drawdown; anti-starvation): L1 300, L2 1500,
                     L3 12000 core-min; family ceiling ~13800 core-min ≈ $11.8 derived
                     (reported-by-owner, c7a.4xlarge $0.0513/core-h; inside the
                     2026-08-21 under-$25 blanket, still costed per item). Each level
                     records remaining budget AND prereg_blob at launch; endTime is
                     NEVER silently reduced to fit a cap (rule 12); an overrun STOPS
                     the run. RANKS=1 for reproducibility/comparability; a launch may
                     parallelise for wall-clock (core-min unchanged). L1+L2 alone
                     (~1350 core-min) yields a partial-grid graded Cd/Cl.
13. CONTROLS       : grade_vmfl017_r3.py --selftest green (26/26, python3 AND
                     python3 -O, zero bare asserts); planted-zero PLANT=7.531e-3
                     matched to the mean reduction (rule 3, L-487); strict completion
                     (End + age guard + last-time≈endTime for a TRANSIENT adaptive-
                     step solver, VMFL045 form) (rule 4); Roache triple gating on BOTH
                     Cd and Cl, else single/partial-grid (rule 5); observed-order
                     floor P_MIN=0.05 with a driven planted control; PLATEAU CLAUSE
                     (Amendment 4, all five items: fractional window + minimum-sample
                     CANNOT_TELL refusal + ptp/range growing-series rejector + null-
                     range refusal + realised sample count; CoV only beside); NEW —
                     WALL-FUNCTION REGIME PRECONDITION (gate-blind, L-501 cause-3
                     analog): window max y+ ≤ 300 AND window mean-avg y+ ≥ 10 (value-
                     blind, from log-law validity, references neither the bands nor
                     0.0168/0.803), else NOT A RESULT; min y+ recorded, never gated;
                     vocabulary guard is a REFUSAL, not an assert; LAUNCHER FREEZE
                     CHECK of prereg + comparator + the three blockMeshDicts vs HEAD;
                     endTime/writeInterval/maxCo/deltaT/maxDeltaT + forceCoeffs &
                     yPlus executeInterval assertions; NO set -u.
```

## Grading path (fixed at this commit) and run-readiness

The comparator `cases/ansys_verification/VMFL017-R3/grade_vmfl017_r3.py` is the frozen
grading path (`--selftest` green under `python3` and `python3 -O`). The case inputs
(`case/0/` characteristic far-field + high-Re wall functions; `case/constant/` air
hePsiThermo/perfectGas + kOmegaSST; `case/system/` Kurganov+vanLeer fvSchemes, "(e|h)"
fvSolution, controlDict with forceCoeffs + yPlus FOs, the three high-Re blockMeshDicts)
and the launcher `run_vmfl017_r3.sh` are committed with this freeze; the launcher
verifies each frozen file (and each blockMeshDict) hashes equal to its HEAD blob before
any solver starts, and its Amendment-3 item-6 self-smoke (scratch only) is recorded in
`LAUNCH_SMOKE.md`. Run root: `verification/runs/ansys_verification/VMFL017-R3/`.
**VMFL017-R3 is `NOT YET RUN`. The launch gate is HELD on Sanaa's decision (rule 9); no
graded solver is started by this freeze, and no queue entry is written.**
