# VMFL033 — Viscous Heating in an Annulus — PRE-REGISTRATION (FROZEN)

**Frozen 2026-08-25T22:42:37Z.** Built from
`docs/ansys_verification/PREREG_TEMPLATE.md` — the ten-line template-speed form —
under **all six amendments**. This is a frozen file under CLAUDE.md rule 6: a departure
is a dated amendment appended at the foot, never an edit above.

**This case is NOT contested and the ten-line form applies.** The reference value's
provenance, its kind and the reference itself are all pinned from the manual's own page
plus a closed form derivable from it; no driving input is missing; no judgement call
decides which column it scores. §A below records the mandatory consistency check that
established this.

---

## THE TEN-LINE FORM

```
1. CASE            : VMFL033 — Viscous Heating in an Annulus — manual p.119.
                     Solver = OpenFOAM v2606 buoyantSimpleFoam (rhoConst) + the SHIPPED
                     viscousDissipation fvOption.  NOT YET RUN;
                     verification/runs/ansys_verification/VMFL033/ absent at 2026-08-25T22:42:37Z.
2. REFERENCE       : the CLOSED FORM of §B below, evaluated at the mesh's own cell-centre
                     radii.  Source = R.B. Bird, W.E. Stewart, E.N. Lightfoot, "Transport
                     Phenomena", John Wiley and Sons, New York, 1960 — the reference the
                     manual's own page cites, and whose solution that page calls
                     "the analytical solution provided by Bird et al (1960)".
                     Ansys reported = TWO FIGURES ONLY (.33.2, .33.3); the manual prints
                     NO numeric table for this case.  CONTEXT ONLY, and NOT DIGITISED.
3. REFERENCE KIND  : CLOSED-FORM / EXACT  ->  buys V, NEVER P.
                     There is ZERO reference uncertainty and ZERO digitisation error: the
                     curve is EVALUATED, not read off a figure, at any resolution asked.
4. TIER CEILING    : GATE REACHED.  A closed-form reference buys code VERIFICATION and
                     never validation; meeting the band is NOT a credential.
5. QUANTITIES      : at every cell centre, with the radius r READ BACK from OpenFOAM's own
                     C field (never constructed from nr, dr or (j+1/2)):
                       Q1  v_theta = U . e_theta   [m/s]
                       Q2  T                        [K]
                       Q3  volume-average T over the annulus [K] — OpenFOAM's own
                           volFieldValue volAverage; the Roache functional.
                     Diagnostics reported beside them, never gates: max|v_r| (must be ~0),
                     the interior peak temperature, and the inner-wall conductive flux.
6. BANDS (THE GATE): at the FINEST level, BOTH of
                       G1  max_cells |v_theta − v_exact| / (Omega2*r2)      <= 0.01
                       G2  max_cells |T − T_exact|       / (T_peak − T1)    <= 0.01
                     Justification, fixed here and NEVER from a first run: the manual's own
                     acceptance practice is 3%; this case is tightened to 1% because the
                     reference carries NO uncertainty of its own (unlike a literature
                     spread), and because a 2nd-order scheme on 128 radial cells has a
                     formal truncation error of order (1/128)^2 ~ 6e-5 — so 1% is a BAND
                     with room in it, not a hurdle.  Normalisers: the moving-wall speed
                     Omega2*r2 = 1 m/s, and the viscous-heating rise T_peak − T1 = 17.33 K
                     (NOT the 1 K wall difference, which would flatter the result).
                     REGISTERED EXPECTATIONS, reported either way and NEVER the gate:
                       E1  G1 quantity also within 0.001
                       E2  G2 quantity also within 0.001
7. LADDER          : buoyantSimpleFoam; laminar (constant/momentumTransport simulationType
                     laminar); heRhoThermo / pureMixture / const transport / hConst /
                     rhoConst, so density is EXACTLY the manual's 1 kg/m3 and never a
                     perfect-gas function of T.  g = (0 0 0).  Mesh: annular sector,
                     -10..+10 deg, blockMesh arc edges, rotational CYCLIC sides, empty
                     frontAndBack (2-D planar).  Birth-certified from the C field at every
                     level (MESH_STANDARD §6).
8. DECOMPOSITION   : r = 2 RADIAL triple, L1_nr32 / L2_nr64 / L3_nr128 = 256 / 512 / 1024
   SEED              cells.  The AZIMUTHAL count is held FIXED at 8 at every level, because
                     the exact solution is theta-INVARIANT and the azimuthal direction
                     therefore carries no discretisation error to converge; this is a
                     RADIAL refinement family and the verdict says so.
                     SERIAL, ranks = 1, no domain decomposition, no RNG, no seed.
9. PRINCIPAL RISK  : THE SETTLING CLAUSE REFUSES.  Pr = 300 and the energy equation is
                     relaxed at 0.3, so 20 000 SIMPLE iterations may not drive the
                     volume-average temperature to a peak-to-peak of 1e-6 of the rise.
                     PREDICTED OUTCOME IF IT BITES: NOT A RESULT on step (1) of rule 5 —
                     a refusal, never a lenient pass.  (Secondary, declared but not the
                     principal: if the rotational cyclic mishandled the tangential vector,
                     max|v_r| would be large instead of ~0; it is printed at every level.)
10. EXPECTED ORDER : p_f = 2 (Gauss linear, corrected).  Expect p_obs ~ 2.
                     p_obs > 2.5 is declared SUSPICIOUSLY HIGH IN ADVANCE — a WARNING
                     (cancellation, a lucky mesh), never a win.
11. WEDGE/GEOM BIAS: NOT an axisymmetric wedge, so the sin(t)/t area deficit of N-AV9 does
                     not apply in its usual form.  The sector DOES carry a chord-vs-arc
                     bias: blockMesh's arc edges give boundary faces that are chords, a
                     deficit of order (dtheta/2)^2/6 = 7.9e-5 (0.008%) at dtheta = 2.5 deg.
                     IT IS NEUTRALISED BY CONSTRUCTION, not assumed away: the reference is
                     evaluated AT THE RADII OpenFOAM'S OWN C FIELD REPORTS, so the compared
                     pair share whatever radius the mesh actually has.  The residual is
                     the cell-centroid-versus-C difference, which C gives exactly.
12. COST + CAP     : ESTIMATE from a throughput of 1.07e5 cell-iterations/s, MEASURED IN A
                     PRE-FLIGHT SMOKE ON A 128-CELL MESH — the cell count is stated beside
                     the basis, which is the lesson VMFL036's calibration row (C-92) paid
                     for.  20 000 iterations:
                       L1  5.12e6 cell-iter ->  48 s -> 0.80 core-min
                       L2  1.02e7 cell-iter ->  96 s -> 1.60 core-min
                       L3  2.05e7 cell-iter -> 191 s -> 3.19 core-min
                       TOTAL ~ 5.6 core-min; x1.5 CONTENTION ALLOWANCE -> ~8.4 core-min.
                     VMFL036's cache-residency effect is NOT expected to repeat here and
                     the reason is stated in advance: even L3 is 1024 cells, so no level
                     leaves cache.  The named risk is CONTENTION (box load ~12.7 of 16).
                     CAPS ARE PER LEVEL, NOT A SHARED DRAWDOWN — one slow level must never
                     starve a later one: L1 5, L2 8, L3 15 core-min.  A crossing STOPS that
                     level and is REPORTED, never absorbed.
13. CONTROLS       : planted-zero (rule 3) on BOTH readers — a known perturbation into a
                     COPY of the real T field, and every cell centre of a COPY of the real
                     C field scaled by 2 — each REFUSING if the reader cannot be shown able
                     to see it.  Strict completion (rule 4) incl. the age guard.  Roache
                     gating in rule 5's ORDER.  endTime % writeInterval == 0 AND a field
                     directory AT endTime, asserted in BOTH launcher and comparator.
                     LAUNCHER FREEZE CHECK (Amendment 2) and cap enforcement in the
                     executable path (Amendment 3), each gating with || { echo ABORT; exit 1; }.
                     AMENDMENT 5 field enumeration (see §D).  AMENDMENT 6: ZERO `assert`
                     statements carry any guard — every one is an explicit raise/exit 2.
                     PLATEAU CLAUSE (Amendment 4): see §C.  Comparator --selftest green.
```

---

## §A — THE MANDATORY CONSISTENCY CHECK (run BEFORE the freeze, from the manual's OWN inputs)

Manual p.119, verbatim: density 1 kg/m3, specific heat 1 J/kg-K, thermal conductivity
1 W/m-K, viscosity 300 kg/m-s; r1 = 1 m, r2 = 2 m; Omega1 = 0.0 rad/s, Omega2 = 0.5 rad/s;
T1 = 273 K, T2 = 274 K.

| group | from the manual's own numbers | reading |
|---|---|---|
| moving-wall speed | `U2 = Omega2*r2` = **1 m/s** | — |
| Reynolds | `rho U2 (r2−r1)/mu` = **3.33e-3** | CREEPING. The page's "the flow is laminar and steady" is **CONSISTENT**. |
| Taylor-like | `Re sqrt(gap/r1)` = **3.33e-3** | far below the ~41 Taylor-vortex onset — no instability to miss. |
| Prandtl | `mu cp/k` = **300** | — |
| **Brinkman** | `mu U2^2/(k dT)` = **300** | **Viscous heating DOMINATES the imposed 1 K wall difference — CONSISTENT with the case title.** |

**NO DRIVING INPUT IS MISSING**, so the case is not contested on that ground. Stronger:
**rho and cp do not even enter the steady solution** — `v_r == 0`, so there is no radial
convection of heat and the energy balance is conduction against dissipation alone.

**Reported whichever way it fell:** it fell CONSISTENT. Unlike VMFL036, whose stated
viscosity gave Re = 50 against an Re = 100 target, **this page's inputs and its physics
agree**, and no arm is needed to test the manual.

## §B — THE CLOSED FORM, derived here and CONFIRMED against an independent numerical BVP

Steady, constant-property, purely tangential flow. The theta-momentum equation reduces to
`d/dr[ (1/r) d(r v)/dr ] = 0`, so `v(r) = A r + B/r`. With `v_r == 0` the energy
equation is `(k/r) d/dr( r dT/dr ) + mu*Phi = 0` with the only surviving dissipation term
`Phi = [ r d(v/r)/dr ]^2 = 4 B^2 / r^4`, giving
`T(r) = −(mu B^2/k)/r^2 + C1 ln r + C2`. Constants from `v(r1)=Omega1 r1`,
`v(r2)=Omega2 r2`, `T(r1)=T1`, `T(r2)=T2`:

    v(r) = 0.666666666666667 r − 0.666666666666667 / r
    T(r) = −133.333333333333 / r^2 − 142.826809048007 ln r + 406.333333333333

    interior peak      r = 1.36640517878826 ,  T = 290.331779355891 K
    the rise T_peak − T1 (the T normaliser)  = 17.331779355891 K
    volume-average T (the Roache functional) — evaluated in the comparator
    inner-wall conductive flux −k dT/dr|_r1  — evaluated in the comparator

**The interior peak sits 16.33 K ABOVE the hotter wall.** That overshoot IS the viscous
heating, and it makes the gate genuinely discriminating: a solver with the dissipation
source absent or mis-scaled cannot land anywhere near it.

**CONFIRMED, not asserted.** The comparator's `--selftest` solves the SAME two boundary-
value problems by finite differences **without ever using the closed form**, and the
maximum error against it falls **4.00x per doubling** (n = 100/200/400) — exactly second
order. The selftest **REFUSES** if that ratio leaves (3, 5).

## §C — THE PLATEAU CLAUSE (PREREG_TEMPLATE Amendment 4, all five items)

1. **FIXED window**, not a fraction: the last **500** samples of the volume-average
   temperature series, which the `Tmean` `volFieldValue` function object writes **every
   iteration**. A fixed window is knowable at freeze time and cannot move when
   `writeInterval` does.
2. **REFUSAL below the floor:** fewer than **500** samples is `CANNOT_TELL` — a
   `NOT A RESULT`, never a lenient pass.
3. **A statistic that REJECTS A GROWING SERIES:** peak-to-peak over the window,
   `ptp/(T_peak − T1) <= 1e-6`. The selftest **demonstrates** it by feeding it a
   monotonically rising series and requiring rejection. No coefficient of variation is
   used anywhere.
4. **NULL-RANGE REFUSAL:** a series with zero variation over its whole length is REFUSED.
   A dead field and a perfectly converged one look identical to a tolerance.
5. **The realised sample count is RECORDED** in the grading artifact as `n_window`,
   beside the floor, so a reader can check it without re-running anything.

## §D — AMENDMENT 5: the field enumeration, MEASURED rather than read off the regex

`system/fvSolution` carries the solver regex `"(U|h|e|k|epsilon|omega)"`, while
`constant/momentumTransport` says `simulationType laminar`. **A naive enumeration from
the regex surface would demand `k`, `epsilon` and `omega` of a laminar case and REFUSE
A CORRECT RUN.**

**Measured in the pre-flight smoke:** a laminar `buoyantSimpleFoam` writes
**`T U p p_rgh phi`** at a write time — and **no `alphat`**, which an earlier draft of
this case's comparator demanded. **That draft would have refused every level.** Caught
before the freeze.

The required set is therefore built as: **what the CONSUMER needs**, INTERSECTED with the
field set of the closure `constant/momentumTransport` **actually names**, EXCLUDING
solver-generated `phi` — and the refusal **names the missing field**. Both the launcher
and the comparator do this, and an unknown closure is **REFUSED, never guessed**.

## §E — DISCLOSURES

**DISCLOSURE 1 — NO pre-freeze observation of any gated value exists.** The pre-flight
smoke ran 50 iterations on a 16x8 mesh in scratch and **printed no field value**. The one
substantive thing it established is a **BOOLEAN**: with the `viscousDissipation` fvOption
removed, the T fields **DIFFER** (so the source is wired) and the U fields are
**IDENTICAL** (so it touches energy only). Neither of those is a value, and neither could
have been used to choose a band. The bands on line 6 are argued from the manual's own 3%
practice and the scheme's formal order, both fixed independently of any run.

**DISCLOSURE 2 — the reference is a closed form this lane derived**, not a number lifted
from the page; the manual prints only figures for this case. That is why §B is confirmed
against an independent numerical BVP inside the comparator's own selftest, and why the
selftest refuses if the confirmation fails.
