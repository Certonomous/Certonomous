# VMFL002 — PRE-REGISTRATION (template-speed form, `docs/ansys_verification/PREREG_TEMPLATE.md`)

**Frozen file (CLAUDE.md rule 6).** Committed BEFORE any solver starts. After the
first compute the gate, band, cap and label are closed; changes land only as dated
addenda that cannot alter them.

```
1. CASE            : VMFL002 -- Laminar Flow Through a Pipe with Uniform Heat Flux --
                     manual p.17.  Solver = simpleFoam (OpenFOAM v2606) with the
                     `scalarTransport` function object carrying T.  Axisymmetric
                     5-degree wedge.  NOT YET RUN;
                     verification/runs/ansys_verification/VMFL002/ ABSENT at
                     2026-08-25T19:24:49Z (checked by name; the parent directory was
                     listed and no VMFL002 entry exists).
2. REFERENCE       : Pressure drop = 1.000 Pa ; Centerline Temperature at the Outlet
                     = 341.00 K.  Source = manual p.17 Table .02.1, "Target" column,
                     attributed there to F.M. White, Fluid Mechanics 3e (1994) and
                     F.P. Incropera & D.P. DeWitt, Fundamentals of Heat Transfer (1981).
                     Ansys Fluent reported 0.999 Pa / 340.50 K and Ansys CFX 1.019 Pa /
                     340.8 K (CONTEXT ONLY -- neither is the reference).
3. REFERENCE KIND  : Category V (code verification, not physical validation).  The
                     Target is textbook-analytic (White / Incropera) as printed by the
                     manual.  V is a CATEGORY, orthogonal to the PASS/GATE-REACHED
                     verdict: VMFL019 is category V and earned PASS.
4. TIER CEILING    : GATE REACHED, per supervisor Ruling 1 (2026-08-26).  THE OPERATIVE
                     REASON is not the V category: it is that the frozen gate compares to
                     the manual's PRINTED Target (1.000 Pa / 341.00 K) -- Ansys's
                     published reference number, which the lab does NOT itself evaluate --
                     so reaching it is GATE REACHED, not an independent PASS.  The lab's
                     OWN closed-form value (0.99724 Pa / 341.0638 K, the Corroboration
                     section) is used ONLY to corroborate the archive-sourced inlet, never
                     as the gate; were the gate set against that lab-evaluated closed form,
                     PASS would be reachable (that is the VMFL004 case, Ruling 2).
5. QUANTITIES      : (a) dP = rho * [areaAverage(p)_inlet - areaAverage(p)_outlet], with
                     rho = 13529 kg/m3 converting simpleFoam's KINEMATIC p to Pa;
                     (b) T on the outlet patch, least-squares fitted in r^2 over the five
                     innermost outlet faces and evaluated at r = 0 -- the wedge has no
                     cell ON the axis.  The raw innermost-face T is reported beside it.
6. BANDS (THE GATE): at L3 (finest), BOTH of
                       |dP_lab - 1.000| / 1.000            <= 0.020
                       |rise_lab - 41.00| / 41.00          <= 0.020,  rise = T_c - 300 K
                     The TEMPERATURE channel is gated on the RISE, not the absolute K.
                     A 2 % band on 341 K is 6.8 K and would be unfalsifiable; the
                     physics being tested is the 41 K rise the wall flux produces.
                     JUSTIFICATION, arithmetic and pre-compute -- summed error budget:
                       manual target rounding, 1.000 Pa to 3 dp     +/- 0.05 %
                       manual target rounding, 341.00 K on a 41 K rise +/- 0.012 %
                       inlet-velocity sourcing (see line 7)         +/- 0.25 %
                       wedge modelling bias (line 11)               +0.095 % to +0.191 %
                       discretisation at L3 (line 10, expected)     < 0.1 %
                     Summed worst case ~0.5 %.  The band is 2.0 % -- 4x the summed
                     budget, and 1.5x TIGHTER than the manual's own 3 % goal.  It is
                     NOT derived from any run: see the disclosure at the foot.
7. LADDER          : simpleFoam, laminar, steady; `scalarTransport` FO with a CONSTANT
                     D = alpha = k/(rho*cp) = 4.5315176e-06 m2/s.  nu = mu/rho =
                     1.1257299e-07 m2/s.  Wall T is fixedGradient q"/k = 5000/8.54 =
                     585.4800936768150 K/m; inlet T = 300 K.  3 birth-certified meshes
                     (MESH_STANDARD sec.6), minted by the launcher from checkMesh.
                     THE INLET VELOCITY IS NOT PRINTED IN THE MANUAL.  It is SOURCED
                     from the manual's own case archive -- VMFL002_WB.wbpz ->
                     VMFL002_WB_1_files/dp0/FLU/Fluent/VMFL002_laminar-pipe-hotflow.set.prof,
                     20 radial points -- least-squares fitted to u = umax*(1-(r/R)^2):
                       umax = 1.0231091246e-02 m/s, U_mean = 5.1155456228e-03 m/s,
                       max |residual| = 2.535e-05 m/s = 0.248 % of umax (the fit residual
                       is the cell-averaging of a 20-cell Fluent inlet, not a bad fit).
                     This is a SOURCED INPUT, not a value backed out of the answer, and
                     the sourcing is disclosed because an unsourced driving input is the
                     failure mode this line exists to prevent.
8. DECOMPOSITION   : grid triple, r = 2 in BOTH directions, axial x radial:
   SEED                L1 =  60 x 15 =    900 cells
                       L2 = 120 x 30 =  3 600 cells
                       L3 = 240 x 60 = 14 400 cells
                     SERIAL, ranks = 1.  No parallel decomposition, no RNG: there is no
                     seed to record and the verdict is a serial-run verdict.
9. PRINCIPAL RISK  : THE SOURCED INLET VELOCITY IS THE SINGLE POINT OF FAILURE.  dP is
                     LINEAR in U_mean and the temperature rise is INVERSE in it, so a
                     1 % error in umax moves dP by +1 % and the rise by -1 % -- IN
                     OPPOSITE DIRECTIONS.  That opposition is the diagnostic: if both
                     channels miss the band in opposite senses by a similar magnitude,
                     the inlet velocity is wrong, NOT the solver.  If they miss in the
                     SAME direction, the fault is elsewhere.  Predicted before compute.
                     Second risk: the wedge axis carries zero-area faces by construction,
                     so checkMesh will report "Failed 2 mesh checks" at every level.  That
                     is the standard OpenFOAM wedge artifact, NOT a mesh fault, and it is
                     recorded in each birth certificate rather than waved away.
10. EXPECTED ORDER : p_f = 2 (Gauss linear, corrected snGrad).  Expect p_obs ~ 2 on both
                     channels.  p_obs > 2.5 is declared SUSPICIOUSLY HIGH IN ADVANCE --
                     a warning of cancellation or a lucky mesh, never a win.
11. WEDGE/GEOM BIAS: AXISYMMETRIC -- N-AV9 applies.  Total included angle t = 5 deg =
                     0.087266462599716474 rad.  THE PAIR, AND THEY ARE DIFFERENT NUMBERS:
                       AREA deficit          sin(t)/t   = 0.9987312439537492
                                                        -> -0.1268756 % on cross-section
                                                           and hence on mass flow;
                       WALL-ARC deficit      2sin(t/2)/t = 0.9996827203920081
                                                        -> -0.0317280 % on wetted area;
                       PRESSURE-DROP bias    sec(t/2)-1 = +0.095268516331992181 %.
                     THE NET, derived not asserted.  Both dP and the temperature rise
                     scale as (wall area)/(cross-section), and that ratio is exactly
                       [2sin(t/2)/t] / [sin(t)/t] = 1/cos(t/2) = sec(t/2),
                     so the NET bias is +0.09526851633199218 % on dP AND +0.09526851633199218 %
                     on the temperature rise -- both toward OVER-prediction.  On the
                     absolute outlet temperature that is +0.0116 % (0.039 K on 341 K).
                     DISCLOSED UNCERTAINTY ON THE BIAS TERM ITSELF: if dP instead scales
                     with the wedge hydraulic diameter D_h = D*cos(t/2), the dP bias is
                     sec^2(t/2)-1 = +0.19062779356602277 %.  The budget on line 6 carries
                     the RANGE +0.095 % to +0.191 %, not one end of it.  No grid
                     refinement removes any of this: the error lives in the AZIMUTHAL
                     direction the wedge holds fixed at one cell.
12. COST + CAP     : MEASURED basis, not guessed: a pre-flight smoke on this box gave
                     0.006500 s/iteration at L1 (900 cells, single core, under a load
                     average of ~9).  Scaling with cell count at endTime = 5000:
                       L1 ~ 33 s, L2 ~ 130 s, L3 ~ 520 s  ->  ~683 s = 11.4 core-min.
                     CAP = 40 core-min, running total across the three levels, enforced
                     in the launcher by timeout_s = remaining_core_min * 60 / RANKS with
                     drawdown and refusal at zero.  ADMISSIBILITY CHECK (done BEFORE the
                     freeze): L1's timeout is 2400 s against a measured need of 33 s
                     (73x); L3's is ~2237 s against ~520 s (4.3x).  The cap ADMITS the
                     registered endTime at the measured rate at every level.
                     AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET (rule 12).
                     cost_basis: $0.0513/core-h, c7a.4xlarge, owner-stated 2026-08-21/22
                     -- REPORTED-BY-OWNER, NOT MEASURED. The box cannot read its own
                     billing (COMPUTE_BUDGET_CHARTER sec.5); dollars are DERIVED.
13. CONTROLS       : planted-zero (rule 3) -- BOTH gate channels are planted into on
                     disk and read back, and grade_vmfl002.py EXITS 2 if the reader
                     cannot see the plant; PLANT = 1.234e-03.  Strict completion
                     (rule 4) -- rc from RUN_RC.txt, the End line read from
                     log.simpleFoam BY EXACT NAME (never a log* glob, which matches
                     log.blockMesh first), last time == endTime, fields present,
                     ExecutionTime count == endTime, and the age guard.  Roache gating
                     (rule 5).  LAUNCHER FREEZE CHECK (rule 2 / template Amendment 2):
                     run_vmfl002.sh re-proves at launch that this file AND the
                     comparator on disk are the blobs at HEAD, each gating with
                     `|| { echo ABORT; exit 1; }`.  Comparator --selftest: 16/16 green.
                     scripts/check_grader_self_blindness.py: clean on both probes.
```

---

## Disclosure: the pre-flight smoke, and why it did not set the band

A pre-flight smoke test was run **before this freeze**, in scratch
(`/tmp/.../scratchpad/smoke/VMFL002`), at L1 with `endTime = 60` — it produced no
graded number and nothing under `verification/runs/`. It is disclosed here because
the team's rule is that a comparator `--selftest` proves the GRADER, never the CASE
(VMFL045 selftested 45/45 and died on the first timestep), so the case itself must
be exercised. What it established: the solver advances, `rc = 0`, `T` spans
300.08–341.53 K, and inlet kinematic `p` reads 7.40137222534e-05.

**The band on line 6 is not derived from it.** The band is the arithmetic sum of the
five budget terms printed on line 6, each of which is independently checkable from
the manual page, the archive profile file and the wedge geometry. A reader who
disagrees can re-add them. The smoke value is stated here so that the reader can see
the band does **not** hug it: a band chosen to fit that number would have been far
tighter than 2 %.

## Corroboration: the closed form, computed independently of the manual's Target

Using the sourced inlet velocity and the textbook constant-flux laminar pipe
solution (Nu = 48/11; `T_s - T(r) = (4 q" R / k)[3/16 + (r/R)^4/16 - (r/R)^2/4]`):

| quantity | closed form, this lab | manual Target | deviation |
|---|---|---|---|
| pressure drop | 0.99724 Pa | 1.000 Pa | 0.28 % |
| centreline outlet T | 341.0638 K | 341.00 K | 0.019 % |

Supporting: Re = 227.2 (laminar), Pr = 0.02484 (mercury), thermal entry length
0.00141 m of a 0.1 m pipe, so the flow is thermally fully developed over 98.6 % of
the pipe. **The gate is against the manual's printed Target, not against this
column** — this is corroboration that the sourced inlet velocity is the right one,
and it is what makes line 9's diagnostic meaningful.
