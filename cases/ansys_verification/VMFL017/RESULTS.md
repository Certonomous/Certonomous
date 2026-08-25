# RESULTS — VMFL017 — Transonic Flow over an RAE 2822 Airfoil

**VERDICT: PENDING** — the case is FROZEN and READY (prereg + comparator + birth-certified
mesh family committed at d1de064b, before any compute), but no GRADED run has produced a
gradeable result: rhoSimpleFoam does not reach a converged steady transonic solution on this
case. This is the principal-risk failure mode the pre-registration named (sec.9), reported
honestly rather than force-converged. Frozen file rule 6 applies; this record cannot alter the
frozen gate, band, cap or label.

## What ran
- Physics-consistency check (sec.9a): PASSES. Manual inputs p=43765, T=300, M=0.73, air
  (MW=28.966, mu=1.983e-5) -> U=253.47 m/s, rho=0.5082, Re=6.496e6, matching the stated
  Re=6.5e6 to 0.06%. Inputs self-consistent.
- Comparator grade_vmfl017.py --selftest: GREEN (reader, plant, plateau, Roache on Cd+Cl).
- Launcher freeze check + machinery: exercised; freeze verified against HEAD.
- SCRATCH smokes only (grade NOTHING; discarded): the coarse (L1, 23040-cell) mesh builds
  (blockMesh rc=0, checkMesh OK) and rhoSimpleFoam starts, but the solve DIVERGES.

## The blocker (crash triaged — a crash is a finding until triaged, and this one is)
rhoSimpleFoam aborts with **FOAM FATAL ERROR: Negative initial temperature T0** in the
thermo energy->T inversion (thermoI.H:57), at shock formation (~150-540 SIMPLE iterations).
Two principled stabilization attempts, both DIVERGED (diagnostic only, non-grading):
  1. limitTemperature fvOption [100,1000 K] + energy relaxation 0.5->0.3: crashed at iter 155.
  2. first-order Gauss upwind for div(phi,U) AND energy + relaxation p 0.2 / U 0.3 / e 0.2 +
     limitTemperature: survived to iter 542 but Ux residual plateaued at ~0.02 (NOT converging)
     with erratic Cd/Cl (Cd -0.047, Cl 0.11 — non-physical), then the same negative-T abort.
The field-limiter does not catch it because the abort is in the thermo INVERSION of an
over-shot energy field, before the field limiter applies. This is a genuine transonic-
convergence problem, NOT solver availability (rhoSimpleFoam is present and runs) and NOT a
mesh defect (checkMesh clean; the mesh is F12's birth-certified geometry).

## Recommended path (for the supervisor to schedule — a solver/ladder decision, not a lane tweak)
A converged transonic RAE 2822 needs a stabilization campaign beyond a single lane and beyond
random relaxation tweaks: candidates are (a) rhoCentralFoam (density-based, shock-robust) run
transiently to steady state — a LADDER change from the frozen rhoSimpleFoam, so a supervisor
decision; (b) rhoSimpleFoam with a low-Mach / lower-CFL continuation to a converged field
before enabling second-order; (c) local-time-stepping. The closure team's F12 campaign runs
the SAME airfoil at M=0.734 and has itself found this regime hard (attempt2, contention) —
worth coordinating. Full converged family est ~800 core-min regardless.

## Cost (estimate vs actual)
No graded compute incurred (scratch smokes only, ~a few core-min, discarded). Pre-registered
family estimate ~800 core-min stands UNCONSUMED. Actual graded = 0; the gap is the un-run
family, attributable to the convergence blocker above, not to contention or waste.

Prepared 2026-08-25T22:10:07Z. NOT FILED / not sent anywhere (submissions parked).
