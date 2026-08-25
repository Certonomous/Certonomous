# VMFL021 — PRE-REGISTRATION (frozen before compute; CLAUDE.md rule 2)

Cavitation over a sharp-edged orifice, **Case A: High Inlet Pressure**. Ansys
Fluid Dynamics Verification Manual, Release 2026 R1, **p. 85**. Frozen file
(rule 6): after first graded compute, only dated addenda that cannot alter gate,
threshold, cap or label.

Shares the Nurick-orifice geometry with VMFL022 (Case B); differs ONLY in inlet
pressure **P1 = 250,000,000 Pa** (Case B is 250,000 Pa). This case sits in the
DEEP-cavitation limit (K → 1), where Nurick's law gives Cd → Cc = 0.62.

## The ten-line freeze (PREREG_TEMPLATE standard form + its three amendments)

```
1. CASE            : VMFL021 — Cavitation over a sharp-edged orifice, Case A
                     (high P1) — manual p.85. Solver = interPhaseChangeFoam
                     (OpenFOAM v2606), SchnerrSauer cavitation, kEpsilon RAS,
                     axisymmetric 5deg wedge. NOT YET RUN;
                     verification/runs/ansys_verification/VMFL021/ absent at
                     2026-08-25 (checked: dir does not exist at freeze time).
2. REFERENCE       : Cd = 0.620 (coefficient of discharge), source = W.H. Nurick,
                     "Orifice Cavitation and Its Effects on Spray Mixing",
                     J. Fluids Engineering 98, 681-687, 1976. Ansys Fluent
                     reported Cd = 0.631 (ratio 1.018), Ansys CFX 0.637 (1.03) —
                     CONTEXT ONLY, never the gate.
3. REFERENCE KIND  : measured/experimental → CAN buy P (Nurick 1976 experimental;
                     Sanaa's ruling: manual is a public primary source).
                     DISCLOSED NUANCE: the target 0.620 coincides with Nurick's
                     correlation Cd = Cc*sqrt(K) = 0.62 in the K→1 (fully
                     cavitated) limit, i.e. it is essentially the contraction
                     coefficient Cc itself. Read strictly as a correlation it
                     would buy V. Tier ceiling (line 4) set so neither reading
                     over-claims.
4. TIER CEILING    : GATE REACHED. Team ceiling (Sanaa); and safe under the
                     experimental-vs-correlation ambiguity on line 3.
5. QUANTITIES      : Cd = |Q_inlet| / (A2 * V_theo); Q_inlet = time-averaged
                     sum(phi) [m3/s] over the inlet patch (pure liquid there);
                     A2 = orifice flat-wedge sector = 6.9725e-7 m2 (FO header,
                     cross-checked); V_theo = sqrt(2*(P1-P2)/rho_l) = 706.97 m/s.
6. BANDS (THE GATE): |Cd_lab - 0.620| / 0.620 <= 0.05 at the finest converged
                     level. JUSTIFICATION (not from any run): manual's stated 3%
                     accuracy goal (p.609) + ~2% for the SchnerrSauer-vs-ZGB
                     cavitation-model substitution (OpenFOAM has no ZGB) = 5%.
                     Reference rounding ~0.08%, grid error GCI-quantified, both
                     inside the 5%.
7. LADDER          : interPhaseChangeFoam / SchnerrSauer / kEpsilon + standard
                     wall functions (matches manual p.85: "standard k-epsilon
                     with standard wall functions"). SchnerrSauer FROZEN before
                     compute (inertia-driven cavitation default; NOT tuned). ZGB
                     unavailable on this box. Mesh: axisymmetric 5deg wedge,
                     3 blocks, birth-certified by the launcher (MESH_STANDARD §6).
8. DECOMPOSITION   : grid triple, spatial ratio r=2, orifice-radial N2R =
   SEED              12 / 24 / 48 (L1/L2/L3), all directions x2 per level; L1 ~
                     832 cells. dt Courant-limited (adjustTimeStep, maxCo=2 —
                     TIGHTER than Case B for stability at the extreme pressure),
                     so the triple measures COMBINED space-time error. SERIAL
                     (RANKS=1).
9. PRINCIPAL RISK  : the ONE predicted failure mode — NUMERICAL STIFFNESS. The
                     inlet pressure is 2.5e8 Pa and the ideal jet velocity is
                     ~707 m/s (water Mach ~0.48 vs the incompressible assumption
                     the manual itself makes). The p_rgh solve spans 2.5e8 Pa;
                     the cavitation source is stiff at the vena contracta. The
                     PREDICTED failure is that the solve does not reach a plateau
                     within the cap (or diverges), giving NOT A RESULT — an
                     honest statement of this incompressible solver's limit at
                     this pressure, not a fabricated number. If it DOES stabilise,
                     the deep-cavitation Cd should saturate near Cc = 0.62.
10. EXPECTED ORDER : formal p_f = 1 (linearUpwind/vanLeer at a sharp-edge
                     singularity); expect p_obs in [0.5, 1.5]; p_obs > 2.0
                     SUSPICIOUSLY HIGH (flagged, not celebrated).
11. WEDGE/GEOM BIAS: N-AV9 sin(t)/t = 0.127% at 5deg; CANCELS in Cd (same
                     flat-wedge patch area in numerator flux and denominator
                     normalisation). Residual << 0.05 gate. Carried.
12. COST + CAP     : estimate ~40 core-min total (L1 ~0.6, L2 ~5, L3 ~34; serial
                     RANKS=1; basis: Case A has a shorter endTime (0.003 s) but a
                     much smaller Courant-limited dt (~1e-6 s) than Case B, giving
                     a comparable step count with more inner iterations per step;
                     reported-by-owner). CAP = 180 core-min RUNAWAY GUARD
                     (per-level timeout = remaining_core_min*60/RANKS, running
                     accounting, refuse at zero — launcher ARTIFACT 2). Overrun
                     STOPS the run (rule 12); crossing reported to the supervisor.
13. CONTROLS       : planted-zero (rule 3) in grade_vmfl021.py (PLANT = 1.234e-6
                     m3/s, read back, refuses if unseen); strict completion
                     (rule 4, adaptive-dt form — see comparator); Roache triple
                     (rule 5) with the 3% PLATEAU gate (a non-plateaued level →
                     NOT A RESULT); LAUNCHER FREEZE CHECK (rule 2, Amendment 2)
                     verifies prereg AND comparator vs HEAD.
                     grade_vmfl021.py --selftest green.
```

## PHYSICS CONSISTENCY CHECK (mandatory before freeze — supervisor's directive)

- Governing group: Nurick cavitation number **K = (P1 - Pv)/(P1 - P2)**.
  From the manual's inputs (P1 = 250,000,000 Pa, P2 = 95,000 Pa, Pv = 3,540 Pa):
  **K = 249,996,460 / 249,905,000 = 1.00037.**
- Independent check: Nurick's correlation **Cd = Cc·√K**, Cc ≈ 0.62:
  **Cd = 0.62 × √1.00037 = 0.6201.**
- Manual target = **0.620**. Agreement **0.02%**. **THE PHYSICS CHECK PASSES.**
  Physical reading: at very high inlet pressure the flow is FULLY cavitated at the
  vena contracta (K→1), so Cd saturates at the contraction coefficient Cc = 0.62,
  INDEPENDENT of the pressure magnitude — which is exactly why "high inlet
  pressure" gives the LOWER Cd (0.620) and "low inlet pressure" (Case B, weak
  cavitation, K=1.59) gives the HIGHER Cd (0.780). Both are Nurick's own physics;
  neither is a mis-specified regime (contrast VMFL036 / VMFL059).

## FEASIBILITY GATE (supervisor's directive — decided honestly, first)

interPhaseChangeFoam EXISTS (OpenFOAM v2606) with Kunz/Merkle/SchnerrSauer. The
case is configurable to the manual's setup. **NOT BLOCKED on solver capability.**
The only gap is ZGB (Ansys's model), substituted by SchnerrSauer and priced into
the gate. VMFL017 (the capability-block fallback) is NOT triggered. The real
question for Case A is not capability but whether an INCOMPRESSIBLE solver can be
driven to a steady discharge at 2.5e8 Pa — recorded as the principal risk
(line 9), to be answered by the run, not assumed.

## Grading path (fixed at this commit)

`cases/ansys_verification/VMFL021/grade_vmfl021.py`, verified by the launcher to
hash equal to its HEAD blob before any solver starts. Launcher:
`cases/ansys_verification/VMFL021/run_vmfl021.sh` (six Amendment-3 artifacts).
