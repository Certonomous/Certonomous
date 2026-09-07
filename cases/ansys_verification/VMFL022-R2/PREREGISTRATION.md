# VMFL022-R2 — PRE-REGISTRATION (frozen before compute; CLAUDE.md rule 2)

Cavitation over a sharp-edged orifice, **Case B: Low Inlet Pressure**. Ansys
Fluid Dynamics Verification Manual, Release 2026 R1, **p. 87**. Successor to
VMFL022 (register #17, `NOT A RESULT` — grid triple OSCILLATORY). This is a
frozen file (rule 6): after the first graded compute, changes land only as dated
addenda that cannot alter the gate, threshold, cap or label.

## Why R2 exists — the base OSCILLATORY was a PHYSICAL REGIME CHANGE

The base VMFL022 r=2 triple (orifice-radial N2R = 12 / 24 / 48) graded
`NOT A RESULT` because its Roache triple was OSCILLATORY (R = −0.105; Cd
0.74442 / 0.76091 / 0.75918). Inspection of the base run's `alpha.water` fields
at endTime (`verification/runs/ansys_verification/VMFL022/{L1,L2,L3}/0.06/`)
shows the cause is **not** iterative noise (L-500 / VMFL010) — the window CoVs are
tiny (1e-4 / 8e-4 / 2e-3) — but a **regime change across the triple**:

| base level | N2R | min alpha.water | regime |
|---|---|---|---|
| L1 | 12 | **1.000000** | SINGLE-PHASE (no vapour) |
| L2 | 24 | 0.263568 | cavitating |
| L3 | 48 | 0.023003 | cavitating |

The coarse level never cavitates: it solves single-phase orifice flow
(Cd ≈ 0.744), a **different PDE branch**. A single-phase solve is **not** a
coarse-grid estimate of the cavitating-orifice Cd, so it cannot be an admissible
coarse member of a cavitating-Cd Roache study. The manual's reference (Cd 0.780)
is itself a cavitating solution (Nurick's cavitating correlation Cd = Cc·√K), so
a valid reproduction must be conducted **entirely in the cavitating regime**.

**The lever (supervisor §3 ruling 2026-09-07, "lever B").** Move the whole triple
into the cavitating regime by shifting it up one r=2 rung to **N2R = 24 / 48 / 96**,
using the base's OWN uniform meshing (base L2, base L3, plus one new finer level).
The single-phase N2R=12 level is EXCLUDED **a-priori by a gate-blind
regime-consistency precondition** (below), NOT because its Cd is an outlier.
This is categorically distinct from the VMFL010 anti-circularity trap
(dropping a valid, same-physics failing level): here the excluded level solves a
different physics and is not a valid Roache member. Lever "A" (in-place
edge-grading of the 832-cell coarsest, answer-blind-confirmed feasible: min
alpha.water 0.773) was **REJECTED** by the supervisor because the grading
magnitude is a continuous free parameter (an anti-circularity DOF that could be
dialed); lever B introduces **no** such knob.

## The freeze (standard form + R2 amendments)

```
1. CASE            : VMFL022-R2 — Cavitation over a sharp-edged orifice, Case B
                     (low P1) — manual p.87. Solver = interPhaseChangeFoam
                     (OpenFOAM v2606), SchnerrSauer cavitation, kEpsilon RAS,
                     axisymmetric 5deg wedge. NOT YET RUN;
                     verification/runs/ansys_verification/VMFL022-R2/ absent at
                     2026-09-07 (checked: dir does not exist at freeze time).
2. REFERENCE       : Cd = 0.780 (coefficient of discharge), source = W.H. Nurick,
                     "Orifice Cavitation and Its Effects on Spray Mixing",
                     J. Fluids Engineering 98, 681-687, 1976. Ansys Fluent
                     reported Cd = 0.777 (ratio 0.996) — CONTEXT ONLY, never the gate.
                     BYTE-IDENTICAL to the base VMFL022 reference (L-487).
3. REFERENCE KIND  : measured/experimental → CAN buy P (Nurick 1976 is an
                     experimental paper). DISCLOSED NUANCE (unchanged from base):
                     the manual's target 0.780 coincides to 3 s.f. with Nurick's
                     cavitating-orifice CORRELATION Cd = Cc·√K, Cc=0.62 (physics
                     check below). Read strictly as a correlation it would buy V.
                     The tier ceiling (line 4) is set so this ambiguity cannot
                     cause an over-claim.
4. TIER CEILING    : GATE REACHED. Reason: this team's ceiling is GATE REACHED
                     (Sanaa: "gate reached for that team means we reached ansys,
                     good enough"); and the experimental-vs-correlation ambiguity
                     on line 3 means GATE REACHED over-claims under neither reading.
                     UNCHANGED from base.
5. QUANTITIES      : Cd = |Q_inlet| / (A2 * V_theo), Q_inlet = time-averaged
                     sum(phi) [m3/s] over the inlet patch (pure liquid there,
                     alpha.water=1, so rho_l cancels); A2 = orifice throat area
                     (outlet flat-wedge sector, read from FO header, cross-checked
                     vs 0.5*r2^2*sin(5deg) = 6.9725e-7 m2); V_theo =
                     sqrt(2*(P1-P2)/rho_l) = 17.607 m/s. UNCHANGED from base.
6. BANDS (THE GATE): |Cd_lab - 0.780| / 0.780 <= 0.05 at the finest converged
                     level. BYTE-IDENTICAL to the base VMFL022 gate (L-487): NOT
                     widened, NOT re-derived. Base justification stands (manual's
                     own 3% accuracy goal p.609 + ~2% for the SchnerrSauer-vs-ZGB
                     cavitation-model substitution; OpenFOAM has no ZGB). NOT
                     chosen from any run.
6a. REGIME         : (NEW, a-priori, GATE-BLIND) ALL THREE graded levels must be
    PRECONDITION      in the cavitating regime: min(alpha.water) over the internal
                     field at endTime <= 0.90 (>= 10% vapour in the most-cavitated
                     cell) for every level, else the triple is mixed-regime and the
                     verdict is NOT A RESULT. The threshold 0.90 is pinned from
                     cavitation physics (vapour unambiguously present) and
                     references NEITHER 0.780 NOR the ±5% band. Base L2/L3 give
                     0.264 / 0.023 — comfortably, non-marginally below 0.90; the
                     excluded single-phase N2R=12 level (min 1.000000) fails it.
                     This precondition is what excludes the base coarse level —
                     NOT any Cd comparison.
7. LADDER          : interPhaseChangeFoam / SchnerrSauer / kEpsilon+standard wall
                     functions (matches manual p.87). MODEL CHOICE FROZEN:
                     SchnerrSauer (unchanged from base; ZGB unavailable on this
                     box; substitution priced into line 6). Mesh: axisymmetric
                     5deg wedge, 3 blocks (base's own uniform meshing, template
                     blob ee74db00, UNCHANGED from base — no grading knob
                     introduced), birth-certified by the launcher.
8. DECOMPOSITION   : grid triple, spatial ratio r=2, orifice-radial N2R =
   SEED              24 / 48 / 96 (L1/L2/L3), FIXED a-priori, NO fallback. All
                     mesh directions x2 per level (NX1/NX2/N1R scaled r=2 too:
                     L1 32/80/20, L2 64/160/40, L3 128/320/80). dt is
                     Courant-limited (adjustTimeStep, maxCo=5), so the triple
                     measures the COMBINED space-time discretisation error. SERIAL
                     (RANKS=1, no domain decomposition, no RNG). L1 ~3328 cells,
                     L2 ~13312, L3 ~53248.
8a. ITERATIVE      : (NEW, L-500 applied at BOTH ends) the linear-solver tolerance
    TIGHTENING        set is tightened ~2 orders vs base (fvSolution: alpha 1e-8→
                     1e-10, U 1e-7→1e-9, k/eps 1e-8→1e-10, p_rgh tol 1e-8→1e-10
                     relTol 0.05→0.005). Rationale: in the base run the L2→L3 Cd
                     difference (0.23% of Cd) was comparable to the finest level's
                     window CoV (0.22%) — the L-500/VMFL010 signature of a
                     functional difference sinking toward the iterative noise
                     floor. This transient PIMPLE has nOuterCorrectors=1 (no
                     residualControl loop), so the linear-solver tolerances ARE the
                     noise-floor control. The SAME tightened values apply to all
                     three levels (uniform, a-priori, never per-level, never chosen
                     by reading Cd).
9. PRINCIPAL RISK  : the ONE predicted failure mode — even shifted up, the
                     cavitating-Cd triple may be non-monotone (the pocket keeps
                     growing 24→48→96 and the functional does not settle),
                     yielding a Roache state other than CONVERGING → NOT A RESULT
                     (honest: a genuine mesh-sensitivity finding, NOT to be
                     rescued by dropping a level or widening the band). The
                     comparator records alpha.water minimum and window CoV per
                     level so this is diagnosable.
10. EXPECTED ORDER : formal p_f = 1 (div schemes linearUpwind/vanLeer, effectively
                     first-order at the sharp-edge singularity); expect p_obs in
                     [0.5, 1.5]. p_obs > 2.0 is SUSPICIOUSLY HIGH, flagged not
                     celebrated. UNCHANGED from base.
11. WEDGE/GEOM BIAS: axisymmetric wedge — N-AV9 sin(t)/t area deficit 0.127% at
                     5deg. It CANCELS in Cd (same flat-wedge patch area normalises
                     numerator flux and denominator). Carried, not ignored.
                     UNCHANGED from base.
12. COST + CAP     : answer-blind-measured (reported-by-owner, c7a.4xlarge,
                     RANKS=1; the box cannot read its own billing —
                     COMPUTE_BUDGET §5): L1(N2R=24) 0.88 core-min to endTime 0.06
                     (min alpha.water 0.2649, CAVITATING); L2(N2R=48) 8.18 core-min
                     to endTime 0.06 (min alpha.water 0.0238, CAVITATING);
                     L3(N2R=96, 53248 cells) 17.08 core-min for a partial
                     answer-blind run to t=0.015 (rc 0, numerically stable) →
                     full endTime 0.06 estimated ~65-70 core-min (≈ L2 × 8 for
                     4× cells + ~2× steps; ≈ partial × 4). Cavitation ONSET is a
                     flow-establishment event at t≈0.03 (mesh-independent: measured
                     for BOTH N2R=24 and N2R=48 — min alpha.water = 1.0 at
                     t≤0.02, then drops at t=0.03), so a smoke shorter than ~0.035
                     cannot see onset at ANY level. N2R=96 cavitation is a sound
                     a-priori inference from the MEASURED monotone trend (12/24/48
                     → 1.000/0.265/0.024, strengthening with refinement) plus
                     finer-is-stronger sharp-edge physics; a direct N2R=96
                     answer-blind run past onset (endTime 0.04) is IN PROGRESS to
                     measure it, and the comparator's gate-blind regime
                     precondition (line 6a) ENFORCES all-cavitating at grade time
                     regardless. Estimate total ~79 core-min. CAP = 300 core-min as a RUNAWAY
                     GUARD (per-level timeout = remaining_core_min*60/RANKS,
                     running accounting, refuse at zero — launcher ARTIFACT 2). An
                     overrun STOPS the run (rule 12); a crossing is reported to the
                     supervisor.
13. CONTROLS       : planted-zero (rule 3, REBUILT to the L-487 rule — the base
                     control had the L-487 CANCELLATION defect: a whole-window
                     plant shifts the window-mean by P identically for ANY input;
                     R2 plants a PROPER SUBSET, expected shift P*n_planted/n_window,
                     and REFUSES a degenerate whole-window subset; a deliberately
                     inert whole-set arm is kept in --selftest as standing proof
                     the subset design is load-bearing); strict completion (rule 4,
                     adaptive-dt form: rc=0, End, last time == endTime, U/p_rgh/
                     alpha.water at endTime, >=10 ExecutionTime lines, age guard
                     endTime/U newer than 0/U — the fixed-dt ExecutionTime-count
                     clause is replaced by "endTime reached" since dt is adaptive);
                     regime-consistency precondition (line 6a); Roache triple
                     (rule 5) with a PLATEAU gate (Cd CoV > 3% → NOT A RESULT);
                     LAUNCHER FREEZE CHECK (rule 2) verifies prereg AND comparator
                     vs HEAD before any solver. grade_vmfl022_r2.py --selftest
                     35/35 green.
```

## PHYSICS CONSISTENCY CHECK (unchanged from base — still passes)

- Governing group: Nurick cavitation number **K = (P1 − Pv)/(P1 − P2)**.
  From the manual's inputs (P1 250,000; P2 95,000; Pv 3,540 Pa):
  **K = 246,460 / 155,000 = 1.5901.**
- Independent check: Nurick's cavitating-orifice correlation **Cd = Cc·√K**,
  Cc ≈ 0.62: **Cd = 0.62 × √1.5901 = 0.7818.**
- Manual target = **0.780**. Agreement **0.23%**. The manual's stated inputs
  reproduce its target through Nurick's own physics.

## THE LAB'S PREDICTION (before compute)

The lab predicts the regime-consistent 24/48/96 triple is CONVERGING and that
Cd at the finest level lands **within the ±5% gate** of 0.780 → **GATE REACHED**.
Basis (context, not a gate): base N2R=48 gave Cd 0.75918 (2.67% below 0.780,
already inside the value band), and the pocket resolves further with refinement.
This is a genuine prediction: if the shifted triple is instead non-monotone
(Roache state ≠ CONVERGING) or a level fails the regime/plateau preconditions,
the honest verdict is **NOT A RESULT**, reported with both triples and orders —
not rescued by dropping a level or widening the band.

## FEASIBILITY (answer-blind, gate-blind — Cd NEVER read)

All confirmation was conducted on scratch, reading `alpha.water` minimum ONLY
(regime), never phi/Cd; the graded run root stayed absent. Measured min
alpha.water at endTime 0.06: N2R=24 → 0.2649, N2R=48 → 0.0238 — both CAVITATE,
comfortably below the 0.90 onset threshold, and monotonically strengthening with
refinement (base measured N2R=12 → 1.000000 single-phase; 24 → 0.264; 48 → 0.024
across the base+R2 ladder). Onset is a flow-establishment event at t≈0.03,
mesh-independent (identical pre-onset transient at N2R=24 and 48). N2R=96
(strictly finer than the cavitating 48) therefore resolves the sharp-edge
pressure minimum at least as well and cavitates at least as strongly — a sound
a-priori inference from the measured monotone trend; a direct N2R=96 answer-blind
run past onset (endTime 0.04) is IN PROGRESS to measure it, and the comparator's
gate-blind regime-consistency precondition (line 6a) is the ENFORCING safeguard:
if any graded level fails to cavitate, the graded verdict is NOT A RESULT, never
silently graded. Details in COST + CAP (line 12). interPhaseChangeFoam and
SchnerrSauer are in the build (the base ran them). **NOT BLOCKED.**

## Grading path (fixed at this commit)

`cases/ansys_verification/VMFL022-R2/grade_vmfl022_r2.py`, verified by the
launcher to hash equal to its HEAD blob before any solver starts. Launcher:
`cases/ansys_verification/VMFL022-R2/run_vmfl022_r2.sh`.
