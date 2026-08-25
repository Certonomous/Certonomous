# VMFL022 — PRE-REGISTRATION (frozen before compute; CLAUDE.md rule 2)

Cavitation over a sharp-edged orifice, **Case B: Low Inlet Pressure**. Ansys
Fluid Dynamics Verification Manual, Release 2026 R1, **p. 87**. This is a frozen
file (rule 6): after the first graded compute, changes land only as dated
addenda that cannot alter the gate, threshold, cap or label.

Built on the shared Nurick-orifice geometry with VMFL021 (Case A); the two cases
differ ONLY in inlet pressure P1 (this case 250,000 Pa; VMFL021 250,000,000 Pa).

## The ten-line freeze (PREREG_TEMPLATE standard form + its three amendments)

```
1. CASE            : VMFL022 — Cavitation over a sharp-edged orifice, Case B
                     (low P1) — manual p.87. Solver = interPhaseChangeFoam
                     (OpenFOAM v2606), SchnerrSauer cavitation, kEpsilon RAS,
                     axisymmetric 5deg wedge. NOT YET RUN;
                     verification/runs/ansys_verification/VMFL022/ absent at
                     2026-08-25 (checked: dir does not exist at freeze time).
2. REFERENCE       : Cd = 0.780 (coefficient of discharge), source = W.H. Nurick,
                     "Orifice Cavitation and Its Effects on Spray Mixing",
                     J. Fluids Engineering 98, 681-687, 1976. Ansys Fluent
                     reported Cd = 0.777 (ratio 0.996) — CONTEXT ONLY, never the gate.
3. REFERENCE KIND  : measured/experimental → CAN buy P (Nurick 1976 is an
                     experimental paper; Sanaa's ruling: the manual is a public
                     primary source, so an experimental reference can buy P).
                     DISCLOSED NUANCE: the manual's target 0.780 coincides to 3
                     s.f. with Nurick's cavitating-orifice CORRELATION
                     Cd = Cc*sqrt(K), Cc=0.62 — see line "PHYSICS CHECK" below.
                     Read strictly as a correlation it would buy V, not P. The
                     tier ceiling (line 4) is set so this ambiguity cannot cause
                     an over-claim.
4. TIER CEILING    : GATE REACHED. Reason: this team's ceiling is GATE REACHED
                     (Sanaa: "gate reached for that team means we reached ansys,
                     good enough"); and the experimental-vs-correlation ambiguity
                     on line 3 means GATE REACHED over-claims under neither reading.
5. QUANTITIES      : Cd = |Q_inlet| / (A2 * V_theo), where Q_inlet = time-averaged
                     sum(phi) [m3/s] over the inlet patch (pure liquid there,
                     alpha.water=1, so mixture mdot = rho_l*Q exactly and rho_l
                     cancels); A2 = orifice throat area (outlet flat-wedge sector,
                     read from the FO header, cross-checked vs 0.5*r2^2*sin(5deg)
                     = 6.9725e-7 m2); V_theo = sqrt(2*(P1-P2)/rho_l) = 17.607 m/s.
6. BANDS (THE GATE): |Cd_lab - 0.780| / 0.780 <= 0.05 at the finest converged
                     level. JUSTIFICATION (not from any run): the manual's own
                     stated accuracy goal is "within 3% of the target" (manual
                     p.609/line 609) — but that 3% was achieved by Ansys with the
                     Zwart-Gerber-Belamri (ZGB) cavitation model, which OpenFOAM
                     v2606 DOES NOT PROVIDE. We substitute SchnerrSauer; the
                     cavitation-model substitution adds ~2% (cavitating-orifice
                     Cd moves by a few % between phase-change models). 3% + ~2%
                     = 5%. Reference rounding (0.780 to 3 s.f.) is ~0.06%, and
                     residual grid error is GCI-quantified, both inside the 5%.
7. LADDER          : interPhaseChangeFoam / SchnerrSauer / kEpsilon+standard wall
                     functions (matches the manual's "standard k-epsilon with
                     standard wall functions", p.87). MODEL CHOICE FROZEN:
                     SchnerrSauer — Nurick's sharp-edged orifice is inertia-driven
                     cavitation, for which SchnerrSauer is the usual OpenFOAM
                     default; it is chosen BEFORE compute and is NOT tuned to the
                     answer. (ZGB, the manual's model, is unavailable on this box;
                     Kunz/Merkle coeffs are carried in transportProperties but
                     NOT selected.) Mesh: axisymmetric 5deg wedge, 3 blocks
                     (upstream inner/outer + orifice), birth-certified by the
                     launcher (blockMesh+checkMesh, MESH_STANDARD §6).
8. DECOMPOSITION   : grid triple, spatial ratio r=2, orifice-radial N2R =
   SEED              12 / 24 / 48 (L1/L2/L3); all mesh directions x2 per level;
                     L1 ~ 832 cells. dt is Courant-limited (adjustTimeStep,
                     maxCo=5), so the triple measures the COMBINED space-time
                     discretisation error (same philosophy as VMFL050). SERIAL
                     (RANKS=1, no domain decomposition, no RNG).
9. PRINCIPAL RISK  : the ONE predicted failure mode — the cavitation pocket at
                     the vena contracta may NOT form (weak cavitation, K=1.590),
                     in which case the solve degenerates to single-phase orifice
                     flow and Cd lands at the NON-cavitating value (~0.6-0.65),
                     i.e. LOW and outside the gate → GATE FAIL. The comparator
                     records alpha.water minimum so this mode is diagnosable.
10. EXPECTED ORDER : formal p_f = 1 (div schemes are linearUpwind/vanLeer,
                     effectively first-order at the sharp-edge singularity);
                     expect p_obs in [0.5, 1.5]. p_obs > 2.0 is SUSPICIOUSLY HIGH
                     (a lucky mesh or a reference coincidence), flagged not
                     celebrated. The sharp edge is a pressure singularity — a
                     clean high order would itself be suspect.
11. WEDGE/GEOM BIAS: axisymmetric wedge — N-AV9 sin(t)/t area deficit is
                     0.127% at 5deg. It CANCELS in Cd: the gate normalises Q by
                     the SAME flat-wedge patch area the solver uses for the flux,
                     so the deficit appears in numerator and denominator alike.
                     Residual bias << 0.05 gate. Carried, not ignored.
12. COST + CAP     : estimate ~22 core-min total (L1 ~0.3, L2 ~2.3, L3 ~19,
                     serial RANKS=1; basis: L1 scratch smoke did 0.003 s in 0.89 s
                     exec, scaled by 8x/level for the space-time refinement,
                     reported-by-owner). CAP = 120 core-min as a RUNAWAY GUARD
                     (per-level timeout = remaining_core_min*60/RANKS, running
                     accounting, refuse at zero — launcher ARTIFACT 2). An overrun
                     STOPS the run (rule 12); a crossing is reported to the
                     supervisor, who decides.
13. CONTROLS       : planted-zero (rule 3) fires in grade_vmfl022.py (PLANT =
                     1.234e-6 m3/s on Q, read back, refuses if unseen); strict
                     completion (rule 4, adaptive-dt form: rc=0, End, last time ==
                     endTime, U/p_rgh/alpha.water at endTime, age guard U newer
                     than 0/U; the fixed-dt ExecutionTime-count clause is replaced
                     by "endTime reached" since dt is adaptive — documented in the
                     comparator); Roache triple (rule 5) with a PLATEAU gate (a
                     level whose Cd CoV over the steady window > 3% is NOT
                     plateaued → NOT A RESULT); LAUNCHER FREEZE CHECK (rule 2,
                     Amendment 2) verifies prereg AND comparator vs HEAD.
                     grade_vmfl022.py --selftest green (all checks).
```

## PHYSICS CONSISTENCY CHECK (mandatory before freeze — supervisor's directive)

Derive the governing dimensionless group from the manual's OWN stated properties
and confirm the target is consistent with an independent source.

- Governing group: Nurick cavitation number **K = (P1 - Pv)/(P1 - P2)**.
  From the manual's inputs (P1 = 250,000 Pa, P2 = 95,000 Pa, Pv = 3,540 Pa):
  **K = 246,460 / 155,000 = 1.5901.**
- Independent check: Nurick's cavitating-orifice correlation
  **Cd = Cc·√K** with the sharp-edged contraction coefficient **Cc ≈ 0.62**:
  **Cd = 0.62 × √1.5901 = 0.7818.**
- Manual target = **0.780**. Agreement **0.23%**. **THE PHYSICS CHECK PASSES:**
  the manual's stated inputs reproduce its target through Nurick's own physics.
  This is the OPPOSITE of the VMFL036 / VMFL059 defect (a target that belonged to
  a different regime than the manual's inputs). Case A (VMFL021) passes the same
  check at K≈1.0004 → Cd → Cc = 0.620.

## FEASIBILITY GATE (supervisor's directive — decided honestly, first)

VMFL021/022 need a cavitating two-phase solver. **interPhaseChangeFoam EXISTS on
this box (OpenFOAM v2606) with Kunz / Merkle / SchnerrSauer phase-change models**
(confirmed on disk and by the supervisor). The case is configurable to the
manual's setup (pressure-driven orifice, k-epsilon, water/vapour properties as
stated). **THEREFORE NOT BLOCKED on solver capability.** The only model gap is
that Ansys's Zwart-Gerber-Belamri model is not in OpenFOAM; SchnerrSauer is
substituted and the substitution is priced into the gate (line 6). VMFL017 (the
fallback for a capability block) is NOT triggered.

## Grading path (fixed at this commit)

`cases/ansys_verification/VMFL022/grade_vmfl022.py`, verified by the launcher to
hash equal to its HEAD blob before any solver starts. Launcher:
`cases/ansys_verification/VMFL022/run_vmfl022.sh` (six Amendment-3 artifacts).
