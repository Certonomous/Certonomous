# VMFL036 — Laminar Flow Past Sphere — PRE-REGISTRATION

**Frozen 2026-08-25T21:37:15Z, BEFORE any graded solver run.** Built from
`docs/ansys_verification/PREREG_TEMPLATE.md` (all three amendments applied).

**This registration is bound by the supervisor's committed pre-freeze physics
check**, `cases/ansys_verification/VMFL036/SUPERVISOR_PREFREEZE_CHECK.md`,
committed at **`3fa6058d`**, blob `e451ca401c1c2502d1b062f4901487dcb7e2725e`. That check is the supervisor's own
§3 check and its two-arm instruction is binding on this document. Nothing below
upgrades it.

---

## THE TEN-LINE FORM

```
1. CASE            : VMFL036 — Laminar Flow Past Sphere — manual p.125-126.
                     simpleFoam (OpenFOAM v2606), steady laminar, axisymmetric wedge.
                     NOT YET RUN; verification/runs/ansys_verification/VMFL036/
                     is ABSENT at 2026-08-25T21:37:15Z.
2. REFERENCE       : Drag Coefficient Cd = 1.0895 (dimensionless), source = Mittal
                     R. (1999) IJNMF 30(7) and Tabata M. & Itakura K. (1998) IJCFD
                     9(3-4), as printed in manual Table .36.1.
                     Ansys Fluent reported 1.0875 — CONTEXT ONLY, never a gate.
3. REFERENCE KIND  : CODE-TO-CODE / high-accuracy NUMERICAL benchmark.  Mittal 1999
                     is a Fourier-Chebyshev SPECTRAL COLLOCATION computation and
                     Tabata & Itakura 1998 is "a precise COMPUTATION of drag
                     coefficients" — both titles say so.  Neither is an experiment.
                     -> buys NEITHER V NOR P.  Reproducing another solver's number
                     is not a verification and cannot be a validation credential.
4. TIER CEILING    : GATE REACHED.  Fixed by line 3 and by the supervisor's
                     committed check.  HOLDS is NOT AVAILABLE to this case whatever
                     the number lands at, because no measured/experimental reference
                     exists to buy P.  This lane does not upgrade it, and the
                     comparator hard-codes GATE REACHED as the best obtainable
                     label for Arm A.
5. QUANTITIES      : Cd = Fx / (q_inf * Aref) at the FINEST level, where Fx is
                     total_x from the OpenFOAM `forces` function object integrated
                     over the `sphere` wall patch (pressure + viscous), read from
                     postProcessing/forces/0/force.dat BY COLUMN NAME;
                     q_inf = 0.5*rho*U^2 = 0.5 (rho = 1 kg/m3, U = 1 m/s, manual
                     p.125); Aref = D^2 sin(a) cos(a)/4 = 1.08944678435e-02 m2,
                     the frontal PROJECTED area of the 5-degree wedge sector
                     (a = 2.5 deg half-angle) — see line 11.
6. BANDS (THE GATE): ARM A ONLY.  |Cd_lab - 1.0895| / 1.0895 <= 0.03  at the finest
                     level.  JUSTIFICATION, none of it from any run of this case:
                     (a) the manual's own acceptance practice is a 3% goal, the
                     same band this team froze for its other manual cases;
                     (b) the manual's printed target carries 4 decimal places, so
                     target rounding alone is ~5e-5 — negligible against 3%;
                     (c) the accepted literature spread for sphere Cd at Re = 100
                     is itself ~1.4% (1.085-1.10 across Mittal, Tabata & Itakura
                     and Schiller-Naumann's 1.0917), so a band tighter than that
                     spread would be gating on which reference was chosen rather
                     than on this solver;
                     (d) Ansys Fluent's own entry misses the target by 0.18%.
                     A 3% band is therefore ~2x the reference spread and ~16x
                     Fluent's own miss.  IT IS NOT DERIVED FROM A FIRST RUN.
7. LADDER          : simpleFoam; laminar (constant/turbulenceProperties,
                     simulationType laminar); SIMPLEC, nNonOrthogonalCorrectors 1,
                     U relaxation 0.9, p 1.0; div(phi,U) bounded Gauss linearUpwind
                     grad(U); laplacian Gauss linear corrected.  Mesh: a two-block
                     polar wedge (theta 0-180 deg, r from D/2 to 50 D), 5 deg full
                     wedge angle, collapsed axis in an `empty` patch per the
                     OpenFOAM axisymmetric convention (SandiaD_LTS tutorial
                     pattern).  Birth-certified at EVERY level by polymesh_area.py
                     reading constant/polyMesh directly — never the solver, never a
                     function object (MESH_STANDARD §6).
8. DECOMPOSITION   : r = 2 BY CONSTRUCTION, not by approximation.  The radial
   SEED              stretching is the FIXED continuous map
                     r(xi) = r_in + L*(K^xi - 1)/(K - 1), xi = i/N, K = 400 frozen;
                     the blockMesh total expansion ratio is computed PER LEVEL as
                     R(N) = K^((N-1)/N), so every L2 node at even index coincides
                     EXACTLY with an L1 node and h halves EXACTLY.  Theta is
                     uniform, so it halves exactly too.
                       L1_32x48    NT= 32  NR= 48   3 072 cells
                       L2_64x96    NT= 64  NR= 96  12 288 cells
                       L3_128x192  NT=128  NR=192  49 152 cells
                     SERIAL (ranks = 1); no domain decomposition, no RNG.
9. PRINCIPAL RISK  : THE ONE named failure mode, predicted before compute —
                     FAR-FIELD BLOCKAGE AT A FIXED 50 D IS NOT REFINED AWAY.  The
                     Roache triple refines the MESH only; the domain radius is held
                     at the manual's 50 D at every level.  If the outer boundary
                     still biases Cd at 50 D, that bias is IDENTICAL at all three
                     levels, so it CANNOT appear in d21 or d32 and the GCI will
                     UNDERSTATE the true error.  The triple can therefore read
                     CONVERGING with a tight GCI while the value sits outside the
                     band for a reason the triple is blind to.  If Arm A lands
                     outside 3% with a clean CONVERGING triple and a GCI far
                     smaller than the miss, THAT is the reading, and it will be
                     stated — not a solver defect.
10. EXPECTED ORDER : formal p_f = 2 (linearUpwind convection, Gauss linear
                     laplacian, both second order).  Expected observed
                     p_obs ~ 1.5-2.0 (linearUpwind degrades toward first order
                     where the limiter engages near the separation line).
                     p_obs > 2.3 is declared SUSPICIOUSLY HIGH IN ADVANCE — a
                     WARNING of error cancellation or a lucky mesh, never a win.
11. WEDGE/GEOM BIAS: AXISYMMETRIC — the term is carried, and it is CASE-SHAPED, as
                     the charter warns.  The wedge maps (x,y) -> (x, y cos a,
                     +/- y sin a), a = 2.5 deg, and TWO DIFFERENT factors follow:
                       WETTED area       -> sin(a)/a
                       FRONTAL PROJECTED -> sin(a) cos(a)/a
                     because the projection picks up an extra cos(a).  Aref is the
                     PROJECTED form, which makes the PRESSURE part of the drag
                     azimuthally exact and leaves the VISCOUS part biased by
                     1/cos(a).  The two limiting normalisations BRACKET the truth
                     and differ by exactly cos(a):
                       AZIMUTHAL BIAS BRACKET = 1 - cos(2.5 deg) = 9.518e-04
                                              = 0.0952% of Cd, half-width 0.0476%.
                     NO GRID REFINEMENT REMOVES IT.  The comparator PRINTS Cd on
                     BOTH normalisations beside the verdict.  It is ~1/30 of the
                     3% band, so it cannot decide the gate — but it is disclosed,
                     never dropped.
12. COST + CAP     : ESTIMATE, per arm, from a MEASURED throughput of 3.07e5
                     cell-iterations/s (machinery check, see DISCLOSURE 1):
                       L1  3.07e7 cell-iter ->  100 s ->  1.7 core-min
                       L2  1.23e8 cell-iter ->  400 s ->  6.7 core-min
                       L3  4.92e8 cell-iter -> 1601 s -> 26.7 core-min
                       ARM TOTAL ~ 2101 s = 35.0 core-min ; BOTH ARMS ~ 70 core-min
                     CAP = 120 core-min PER ARM (240 total), a runaway guard at
                     ~3.4x the estimate.  ENFORCED IN THE EXECUTABLE PATH by
                     timeout_s = remaining_core_min * 60 / RANKS with running
                     accounting core_minutes = wall_s * RANKS / 60 drawing ONE
                     budget down across the three levels and REFUSING at zero.
                     AN OVERRUN STOPS THE RUN; it does not get a new budget.
                     cost_basis: core-minutes MEASURED from each level's own
                     RUN_RC.txt.  Any dollar figure is DERIVED at the recorded
                     c7a.4xlarge rate $0.0513/core-h (owner-stated) and is
                     REPORTED-BY-OWNER, NOT MEASURED — this box cannot read its
                     own billing (COMPUTE_BUDGET_CHARTER §5).
13. CONTROLS       : grade_vmfl036.py --selftest GREEN, and the launcher runs it at
                     every launch.  It fires, with ZERO compute:
                       - PLANTED FORCE (rule 3): total_x = 7.7e-03 planted into a
                         COPY of the finest level's real force.dat; the reader must
                         see it or the comparator REFUSES (exit 2).
                       - PLANTED GEOMETRY (rule 3): every point of a COPY of the
                         finest mesh scaled by 2; every area must go by 4 or the
                         comparator REFUSES.  A zero from a reader not shown able
                         to see a non-zero is not evidence.
                       - PLANTED SYNTHETIC READER: total_x placed in a DELIBERATELY
                         PERMUTED column; a positional reader fails.  A header with
                         no total_x must be REFUSED, not guessed.
                       - ROACHE CLASSIFIER CONTROL: triples constructed to be
                         CONVERGING / DIVERGENT / OSCILLATORY / STAGNANT / EXACT
                         must each be classified correctly, and the exactly-
                         second-order triple must return p_obs = 2 to 1e-9.
                       - GEOMETRY IDENTITY: the closed-form Aref must equal an
                         independent 200 000-point quadrature of the same integral.
                       - STRICT COMPLETION (rule 4): rc = 0; an `End` line; last
                         time == endTime; U and p present at endTime;
                         ExecutionTime count == endTime; and every field at endTime
                         NEWER than the case's own 0/ (age guard).  NO DEPARTURE IS
                         DECLARED — residualControl is deliberately absent from
                         fvSolution so the fixed 10 000 iterations always run, and
                         every clause is checked LITERALLY.  The launcher refuses a
                         level directory that already exists.
                       - ROACHE GATING (rule 5): not iteratively converged (final
                         initial residual > 1e-6 on Ux, Uy, p) or not plateaued
                         (peak-to-peak of Cd over the last 20% of iterations
                         > 1e-5 relative) -> NOT A RESULT; triple not CONVERGING
                         -> NOT A RESULT with the value and both differences
                         printed; GCI at Fs = 1.25, and NEVER quoted when the three
                         values are not monotone.
                       - LAUNCHER FREEZE CHECK (rule 2; template Amendments 2+3):
                         PREREGISTRATION.md, grade_vmfl036.py AND polymesh_area.py
                         on disk are each hashed against this commit's blobs at
                         launch, each gating with || { echo ABORT; exit 1; }, and
                         the resolved shas are written into
                         verification/runs/.../VMFL036/<arm>/LAUNCH_RECORD.txt.
```

---

## THE TWO ARMS

The supervisor's committed check found the manual's VMFL036 page **internally
inconsistent**: its stated `mu = 0.02` gives **Re = 50**, where sphere drag is
~1.54, while its target **Cd = 1.0895 is the literature value at Re = 100**
(inverting Schiller-Naumann on 1.0895 gives Re = 100.4). Freezing 1.0895 as the
gate while running `mu = 0.02` would have produced ~1.5 and a **guaranteed GATE
FAIL measuring the manual's transcription error, not this lab's solver** — the
VMFL059 class, caught before the freeze this time.

### ARM A — THE GATE
`nu = 0.01` (rho = 1, so nu is numerically equal to mu), **Re = rho U D / mu =
100**. Gate exactly as line 6. Full three-level Roache family. Tier ceiling
**GATE REACHED**, per line 4.

### ARM B — A DISCLOSED DIAGNOSTIC ABOUT THE MANUAL, NOT A GATE ON THIS SOLVER
`nu = 0.02`, **exactly as the manual's page states**, **Re = 50**.

**REGISTERED PREDICTION, FROZEN HERE BEFORE THE RUN:**
Schiller-Naumann `Cd(Re) = (24/Re)(1 + 0.15 Re^0.687)` at Re = 50 gives
**Cd = 1.5381**. Arm B is registered to land **within 10%** of 1.5381 (the honest
band for agreement with a scattered-data correlation) **and at least 25% away
from 1.0895**.

If both hold, that is positive evidence the error is **the manual's viscosity**
and not this lab's solver. **Arm B carries the verdict `NOT A RESULT` BY
REGISTRATION**: it is evidence about the manual, it is not a gate on the solver,
and it never scores. Its full three-level family is run anyway so the diagnostic
is not a single-grid assertion.

---

## DISCLOSURES — stated because hiding them would be worse

### DISCLOSURE 1 — a partial coarse Cd was seen BEFORE this freeze
Validating the machinery (the mesh topology had to be rewritten from the dead
predecessor lane's version, and the polyMesh face format had to be confirmed
readable), this lane ran **300 iterations of simpleFoam on a scratch L1-geometry
mesh at nu = 0.01**, in a scratchpad directory **outside `verification/runs/`**,
on a mesh path that is not the graded one, at 3% of the graded iteration count.
Its `force.dat` was inspected, and **a coarse partial Cd of approximately 1.09
was therefore visible to this lane before this document was frozen.**

**Why it does not compromise the freeze, stated so a reader can check rather than
take it on trust:**
- **The target 1.0895 is PRINTED IN THE MANUAL.** It was not choosable.
- **The band 0.03 is argued on line 6 from four sources** — the manual's own 3%
  practice, target rounding, the published reference spread, and Fluent's own
  miss — **none of which is this case's output**, and all of which were fixed by
  the supervisor's committed check at `3fa6058d` before this lane ran anything.
- **The observation is NOT A RESULT and is not in the graded family**: different
  directory, un-birth-certified mesh, 300 of 10 000 iterations, no completion
  check, no controls fired.
- **The launcher's smoke test was rebuilt to print NO value** — it opens the gate
  channel with `--dryrun-reader`, which reports structure only. No further
  pre-freeze number is obtainable through the sanctioned path.

This is disclosed rather than buried. A reader who judges it fatal should read
Arm A as `GATE REACHED` with this caveat attached, and Arm B — whose prediction
1.5381 was registered here with **no** corresponding observation of any kind — as
the clean arm.

### DISCLOSURE 2 — inherited, uncommitted predecessor work
A predecessor lane died before committing anything. Its `polymesh_area.py`,
`grade_vmfl036.py` (truncated at line 472, mid-file, with **no** `main`, no
`--selftest` and no verdict logic) and case inputs were found on disk, judged,
and **reused deliberately where correct and corrected where not**:

- **KEPT**: `polymesh_area.py` (verified against a real v2606 `faceList`
  polyMesh), the force.dat name-based reader, the Roache classifier, the strict-
  completion checker, the two planted controls, the K = 400 exact-nesting scheme.
- **CORRECTED — mesh topology**: the predecessor emitted **two coincident
  vertices** on the axis, which blockMesh does **not** merge under the default
  `mergeType topology`. Rewritten to the **single shared axis vertex** pattern
  OpenFOAM's own `SandiaD_LTS` tutorial uses (`axis { type empty; faces
  ( (0 7 7 0) ... ); }`). The mesh now builds with `checkMesh` reporting
  `Mesh OK`.
- **CORRECTED — the reference area, a real 0.095% bias**: the predecessor froze
  `Aref = D^2 sin(a)/4` and argued the sin(a) cancels. It does not fully: the
  frontal projection carries an **extra cos(a)** (line 11). The analytic
  projected area `D^2 sin(a) cos(a)/4 = 1.08944678435e-02` matches the value
  `polymesh_area.py` reads off the real L1 mesh to **1 part in 1e8**, while the
  predecessor's form is 0.095% larger. Corrected, and the residual bracket
  carried rather than assumed zero.
- **DISCARDED**: a `spherePatchArea` function object using
  `areaNormalIntegrate` on `U`, which does not return a patch area; and a stray
  `constant/momentumTransport` (the .org fork's name) that v2606 would not read
  and that the launcher now refuses outright.

---

## WHY THIS CASE IS STANDARD-FORM AND NOT BESPOKE

The reference value, its provenance and its reference-KIND are all pinned from
the manual page plus its two cited titles, with no judgement call. The one
contested question — **which viscosity** — was settled by the supervisor's own
committed pre-freeze check, and is carried here as two frozen arms rather than as
an argument. The disclosure of a code-to-code ceiling on line 3 IS the honest
ceiling, not a dispute.
