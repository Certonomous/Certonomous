# VMFL033-R2 — Viscous Heating in an Annulus — PRE-REGISTRATION (FROZEN)

**A NEW registration succeeding VMFL033-R1 (register row #21, `NOT A RESULT`,
2026-08-25). This is NOT an edit of R1.** R1's frozen files are closed and are
never touched (CLAUDE.md rule 6); R1's row #21 `NOT A RESULT` **STANDS** and is
not superseded, re-graded or softened. This file is itself a frozen file under
rule 6: a departure lands as a dated amendment at the foot, never as an edit
above.

## §0 — THE RULE-2 STATEMENT (true as of the freeze)

**This case is NOT YET RUN.** `verification/runs/ansys_verification/VMFL033-R2/`
is **absent** as of this freeze — verified by the committing lane's own
`test -e` immediately before the freeze commit, with the timestamp recorded in
the commit message and in `RESULTS.md` when R2 is graded. The gate, band, tier
ceiling, caps and label below are fixed **before** any solver starts; the
freeze's entire evidentiary content is that they could not have been chosen to
fit an answer.

## §1 — WHY R2 EXISTS, and the ONE substantive change

R1 landed `NOT A RESULT` because, under rule 5's order: **(1)** two of three
levels were not plateaued, and **(2)** the Roache triple on the volume-average
was `OSCILLATORY` (R = **−398.5** [TRANSCRIBED from R1 RESULTS.md:19]). The
diagnosis R1 recorded is specific: **L1 and L2 settled to near machine precision
(worst final residual 9.97e-13 and 7.62e-10 [TRANSCRIBED from R1
RESULTS.md:44-45]) while L3 ALONE was unconverged at 2.14e-08 with a plateau
peak-to-peak of 7.85e-03 of the rise [TRANSCRIBED from R1 RESULTS.md:46].** R1's
own §4 called it: *"the finest mesh simply ran out of iterations"* at the frozen
`endTime = 20000`.

**R2's single substantive setup change is a longer `endTime`: 20000 → 100000, a
5× fixed-iteration ceiling** [REGISTERED], so L3 has the iterations to converge.
This is **one change per run** (Sanaa 2026-08-27 §3). **Every other setup input
is BYTE-IDENTICAL to R1** — the mesh (`make_blockmeshdict.py`, `cmp`-identical),
the schemes (`fvSchemes`), the thermophysics (`thermophysicalProperties`), the
viscous-heating `fvOptions`, the relaxation factors and the `residualControl`-
empty **fixed-iteration** mode (`fvSolution`), and the boundary conditions.
`diff -rq` confirms `case/` is identical to R1's `case/` [MEASURED, this lane].

**That R1's L3 will converge on a longer run is a HINT the band is meetable, NOT
evidence that it is.** R1's §4 said so verbatim: *"This is a strong hint that
the case would meet its band on a longer run. It is NOT evidence that it does."*
If L3 still fails to plateau at `endTime = 100000`, the comparator **REFUSES**
(`NOT A RESULT`), honestly — the fix is tested, not assumed.

## §2 — THE TEN-LINE FORM

```
1. CASE            : VMFL033-R2 — Viscous Heating in an Annulus — manual p.119.
                     Solver = OpenFOAM v2606 buoyantSimpleFoam (rhoConst) + the
                     SHIPPED viscousDissipation fvOption.  NOT YET RUN;
                     verification/runs/ansys_verification/VMFL033-R2/ absent at freeze.
2. REFERENCE       : the CLOSED FORM of §4, DERIVED IN THE COMPARATOR to full
                     double precision (never transcribed from R1), evaluated at the
                     mesh's own cell-centre radii read back from OpenFOAM's C field.
                     Source = R.B. Bird, W.E. Stewart, E.N. Lightfoot, "Transport
                     Phenomena", Wiley, 1960 — the reference the manual's p.119 cites.
                     Ansys reported = TWO FIGURES ONLY (.33.2, .33.3); the manual
                     prints NO numeric table.  CONTEXT ONLY, NOT DIGITISED.
3. REFERENCE KIND  : CLOSED-FORM / EXACT.  Zero reference uncertainty, zero
                     digitisation error: the curve is EVALUATED, not read off a figure.
4. TIER CEILING    : PASS-CAPABLE, per ANSYS_VERIFICATION_CHARTER §11.1 (2026-08-30).
                     See §5 for the reasoning and the date-ordering; this REVERSES,
                     for R2's own freeze, R1's line-33 "GATE REACHED" ceiling, which
                     predates §11.1 by five days and is NOT edited (rule 6).
5. QUANTITIES      : at every cell centre, radius r READ BACK from OpenFOAM's own C
                     field (never from nr, dr or (j+1/2)):
                       Q1  T                        [K]  — THE GATE quantity
                       Q2  volume-average T [K] — OpenFOAM volAverage; the Roache functional
                       Q3  v_theta = U . e_theta [m/s] — REPORTED, NOT A DISCRIMINATOR (§6)
                     Diagnostics beside them, never gates: max|v_r| (~0), interior
                     peak T, inner-wall conductive flux.
6. BANDS (THE GATE): at the FINEST level:
                       G_T  max_cells |T − T_exact| / (T_peak − T1)  <= 0.01   (THE GATE)
                     Justification, fixed here and NEVER from a first run: the manual's
                     own acceptance practice is 3%; tightened to 1% because the reference
                     carries NO uncertainty of its own and a 2nd-order scheme on 128
                     radial cells has a formal truncation error ~ (1/128)^2 ~ 6e-5 — 1%
                     is a band with room in it.  Normaliser = the viscous-heating rise
                     T_peak − T1 (NOT the 1 K wall difference, which would flatter it).
                     Velocity is REPORTED against 0.01 but is NOT the gate (§6).
                     REGISTERED EXPECTATIONS, reported either way, NEVER the gate:
                       E_T  G_T quantity also within 0.001
                       E_v  velocity within 0.001
7. LADDER          : buoyantSimpleFoam; laminar; heRhoThermo / pureMixture / const
                     transport / hConst / rhoConst (rho = exactly 1 kg/m3, never a
                     perfect-gas function of T); g = (0 0 0).  Mesh: annular sector
                     -10..+10 deg, blockMesh arc edges, rotational CYCLIC sides, empty
                     frontAndBack (2-D planar).  ALL BYTE-IDENTICAL to R1.
8. TRIPLE          : r = 2 RADIAL triple, L1_nr32 / L2_nr64 / L3_nr128 = 256 / 512 /
                     1024 cells.  Azimuthal count held FIXED at 8 (the exact solution is
                     theta-invariant, so theta carries no discretisation error).  The
                     Roache functional is the volume-average T (§6); the triple is graded
                     by rule 5.  SERIAL, ranks = 1, no decomposition, no RNG, no seed.
                     P_MIN = 0.05 (floor on |p_obs|); GCI_MAX = 10% (ceiling on the
                     functional GCI) — see §7.
9. PRINCIPAL RISK  : L3 STILL does not plateau at 100000 iterations.  PREDICTED OUTCOME
                     IF IT BITES: NOT A RESULT on rule 5 step (1) — the plateau clause
                     REFUSES, never a lenient pass.  This is R1's failure mechanism given
                     5x the iterations; if 5x is still short, the honest answer is a
                     refusal and a possible R3, not a softened row.
10. EXPECTED ORDER : p_f = 2 (Gauss linear, corrected).  On a CONVERGED family the
                     volume-average triple should give p_obs ~ 2 (a partial-2nd-order
                     estimate from R1's converged L1 and the exact volume-average predicts
                     p_obs ~ 2.0).  p_obs > 2.5 declared SUSPICIOUSLY HIGH IN ADVANCE — a
                     WARNING (cancellation, a lucky mesh), never a win.  p_obs < P_MIN or
                     GCI > GCI_MAX -> NOT A RESULT (§7).
11. CHORD/GEOM BIAS: NOT an axisymmetric wedge (N-AV9's sin(t)/t area deficit does not
                     apply).  The sector carries a chord-vs-arc bias of order (dtheta/2)^2/6
                     ~ 7.9e-5, NEUTRALISED BY CONSTRUCTION: the reference is evaluated AT
                     THE RADII OpenFOAM's own C field reports, so the compared pair share
                     the mesh's actual radius.  Unchanged from R1.
12. COST + CAP     : EXTRAPOLATED from R1's MEASURED per-level actuals at 20000 iterations
                     (0.4167 / 0.6333 / 1.0167 core-min [TRANSCRIBED from R1
                     RESULTS.md:135-137]); a longer endTime scales ~linearly in iterations,
                     so 5x -> 2.08 / 3.17 / 5.08 core-min, TOTAL ~10.3 core-min EXTRAPOLATED.
                     This is an IN-FAMILY extrapolation (C-199); no cross-family transfer.
                     PER-LEVEL CAPS, NOT a shared drawdown: L1 8, L2 12, L3 20 core-min —
                     ~3.8x headroom each.  Sized deliberately: R1 died of too FEW iterations,
                     and Sanaa's runner-side cap enforcement is now ENFORCE (2026-08-31) —
                     a cap set too tight would kill R2 the same way for a different reason,
                     so the headroom absorbs contention (box load up to ~15/16) and the
                     heavier per-iteration I/O of 100000 vs 20000 iterations.  A crossing
                     STOPS that level and is REPORTED, never absorbed.
13. CONTROLS       : planted-zero (rule 3) AT EVERY LEVEL — a known perturbation into a
                     COPY of each level's real T on disk, read back through the PRODUCTION
                     reader, plus each level's C scaled by 2 — refusing if a reader cannot
                     be shown able to see it.  Strict completion (rule 4) incl. the age
                     guard.  NUMERIC time-directory selection with a CARDINALITY REFUSAL
                     (L-339).  Roache gating in rule 5's ORDER.  PLATEAU CLAUSE (§7).
                     ZERO `assert` statements, enforced by an AST GUARD over the
                     comparator's own bytes (§7).  Comparator --selftest green under both
                     python3 and python3 -O, with an end-to-end arm proving each verdict
                     (PASS / GATE FAIL / every NOT-A-RESULT cause) is REACHABLE.
```

## §3 — RESOLVED. NO SECTION REACHES THIS FREEZE WITH AN OPEN QUESTION (§11.2)

Every interpretive call below is **made here, before the freeze commit**, not
flagged for later. No clause defers a gate, band, threshold, cap, level,
ceiling or label.

## §4 — THE CLOSED FORM, derived here and cross-checked by TWO independent instruments

Steady, constant-property, purely tangential flow. θ-momentum reduces to
`d/dr[(1/r) d(rv)/dr] = 0` → `v(r) = A r + B/r`; with `v(r1)=Ω1 r1=0`,
`v(r2)=Ω2 r2=1`: **`v(r) = (2/3)(r − 1/r)`** (A = 2/3, B = −2/3) [DERIVED, this
lane, reproduced by the comparator to double precision]. With `v_r ≡ 0` the
energy equation is `(1/r) d/dr(r dT/dr) = −Φ/k`, dissipation
`Φ = 4 μ (2/3)²/r⁴ = 533.333…/r⁴`. Integrating twice with both Dirichlet walls:

    T(r) = −133.333333…/r² − (99/ln 2) ln r + 406.333333…

the log coefficient being **A_T = −99/ln 2 = −142.8268…** [DERIVED — the
comparator computes `-99/math.log(2)` to full double precision and does **not**
transcribe R1's rounded `−142.826809048007` nor any hand value]. From it:

| quantity | value | tag |
|---|---|---|
| interior peak radius | r = 1.366405… | DERIVED |
| **interior peak T** | **290.331779… K** (16.33 K above the hotter wall) | DERIVED |
| viscous-heating rise T_peak − T1 (the T normaliser) | 17.331779… K | DERIVED |
| volume-average T (the Roache functional) | 284.133655… K | DERIVED |
| inner-wall conductive flux −k dT/dr\|_r1 | −123.839858… W/m² | DERIVED |

**A single derivation of a gate value is an unchecked derivation.** The
comparator's `--selftest` confirms these by **TWO** routes independent of the
BVP integration that produces them:

1. **An independent numerical BVP** solves the same two boundary-value problems
   by finite differences, never using the closed form; its error against the
   closed form falls **4.00× per doubling** (n = 100/200/400) — exactly second
   order, and the selftest **REFUSES** if that ratio leaves (3, 5) [MEASURED:
   ratio 4.00 this lane].
2. **A global energy balance** — total viscous dissipation `∫ μΦ dV` against net
   conductive wall outflow `[q_r·2πr]_{r2} − [q_r·2πr]_{r1}` — must close in
   steady state with no convection. Measured: dissipation **1256.63706 W** =
   net wall outflow **1256.63706 W**, relative difference **0.00e+00**
   [MEASURED this lane]. This validates `C1_T` (hence T_peak, T_avg, q_wall) by
   a route that never touches the BVP integration. The selftest **REFUSES** if
   the relative difference exceeds 1e-12.

## §5 — THE CEILING: PASS-CAPABLE, and why the reversal of R1's line 33 is legitimate

R1's frozen pre-registration line 33 reads *"TIER CEILING: GATE REACHED. A
closed-form reference buys code VERIFICATION and never…"*. **That line predates
`ANSYS_VERIFICATION_CHARTER` §11.1 (Amendment 1.5, 2026-08-30) by five days.**
§11.1 settles that `VERIFICATION_CHARTER` §2f.3's `GATE REACHED` cap is the
ceiling **WITHOUT a triple** — its own column heading reads *"ceiling WITHOUT a
triple"* — and that a limb declaring a `CONVERGING` triple is graded by CLAUDE.md
rule 5 step 3, **where `PASS` is available, because a converging triple separates
and bounds the discretisation error.**

R2 declares a Roache triple (§2 line 8) and grades its temperature limb by rule 5
step 3. **R2 is therefore PASS-capable at its own freeze.** The date-ordering is
stated so no auditor has to reconstruct it: R1 was frozen 2026-08-25; §11.1 was
adopted 2026-08-30; **R2 is frozen today** and declares the ceiling in force
today. **R1's frozen line is NOT edited** (rule 6) — a new registration declares
the ceiling at its own freeze. The precedent is this team's own **row #46
(VMFL069-R2), landed 2026-08-31, a `PASS` on exactly this ground.**

**The limit, stated so it is not over-read:** the cap still binds wherever its
ground holds — any limb with no triple, any non-`CONVERGING` triple, any
EXPERIMENTAL reference. R2's reference is a **closed form** and the temperature
limb's triple is expected `CONVERGING`; §11.1 applies squarely. §2h (the
no-triple floor-demonstration clause, referred to Sanaa) is **not** invoked and
R2 claims nothing about it.

## §6 — THE TEMPERATURE CHANNEL IS THE GATE; VELOCITY IS NOT A DISCRIMINATOR

**`v_theta(r)/(Ω2 r2)` is independent of EVERY material property.** The velocity
field `v(r) = (2/3)(r − 1/r)` contains no μ, k, ρ or cp — it is the solution of
the momentum equation alone. A pass on the normalised velocity therefore tests
the **momentum solve** (which is legitimate code verification) but tests **none
of the viscous-heating physics** this case exists to verify. It is **not void**
— it is a real solve — but it is **not a discriminator**, and an unremarked pass
on it would overstate what the row proves.

**Normalised temperature depends on the Brinkman number** `Br = μ U²/(k ΔT) =
300` [DERIVED], i.e. on μ and k, the very properties the manual prints. That is
why the **temperature channel carries the gate** and the velocity channel is
**reported and explicitly labelled NON-DISCRIMINATOR** on the comparator's face
and in the register row. **This is the trap that disqualified VMFL070 and
VMFL061: a gate quantity insensitive to the unprinted properties is insensitive
to the physics being tested, and an unfalsifiable gate is not a weak gate — it
is not a gate.** The credential, if R2 earns one, rides on temperature.

## §6a — THE EXACT-TRIPLE CHECK: no gate quantity is reproduced to round-off

`1/r²` and `ln r` are **not** polynomials; a 2nd-order Gauss-linear finite-volume
scheme reproduces polynomials only up to its formal order and carries a nonzero,
mesh-refinable truncation error on transcendental/rational integrands. The gate
quantity (pointwise T, involving `1/r²` and `ln r`) and the Roache functional
(volume-average T) therefore have **genuine truncation error to refine**; neither
is reproduced to round-off. **No limb here is `EXACT`** [DERIVED / reasoned this
lane] — the trap that retired VMFL059 and VMFL070 does not fire, and R1's own
result (finite, level-dependent T errors 6.06e-03 → 2.79e-03 across L1→L2
[TRANSCRIBED from R1 RESULTS.md:44-45]) is direct evidence the error is nonzero
and refinable. The velocity field `(2/3)(r − 1/r)` (containing `1/r`) is likewise
not reproduced exactly, but velocity is non-discriminating and does not gate.

## §7 — THE FOUR DESIGN REQUIREMENTS, and the completion clause, each declared

1. **GCI_MAX ceiling beside the P_MIN floor.** `P_MIN = 0.05` (a floor on |p_obs|;
   matches VMFL063's precedent — catches an essentially-zero order) and
   `GCI_MAX = 10%` (a ceiling on the Roache functional's GCI). A `CONVERGING`
   triple with `p_obs < P_MIN` or `GCI > GCI_MAX` is **`NOT A RESULT`**. The
   ceiling catches the pathology the brief names — VMFL063's 120.62% and row #46
   limb C's 145.91%, both an uncertainty larger than the value it qualifies. A
   properly-converged R2 is expected to give `GCI ~ 5e-4%` [DERIVED estimate],
   four orders below the ceiling, so `GCI_MAX` guards pathology without
   threatening a legitimate result. Both are **registered before compute** and
   applied in `decide_verdict`.
2. **The plant fires at EVERY level.** The comparator plants `1.234e-03` into a
   copy of **each** level's real T on disk and scales **each** level's C by 2,
   reading both back through the production reader and refusing if unseen — not
   the finest level alone (R1's disclosed weakness; rows #44/#46 fired at L1
   only). Verified on a real on-disk field file in `--selftest` [MEASURED:
   reader saw 0.001234].
3. **NUMERIC time-directory selection with a cardinality refusal** (L-339), never
   `sorted(glob)[-1]`: `select_endtime_dir` parses each directory name to a float,
   selects the numeric max, **records `lexicographic_would_have_misread`**, and
   **REFUSES** if two names denote the same numeric time. Driven to refusal on
   real `{100000, 100000.0}` dirs before the freeze [MEASURED, refusal C3].
4. **No `assert` in the comparator; an AST guard proven to fire.** The comparator
   parses its own source at every invocation and **REFUSES** if any `ast.Assert`
   node exists (an assert vanishes under `python3 -O`). Driven to refusal on the
   comparator's own bytes with an `assert` injected [MEASURED, refusal A2, exit 2].
   `--selftest` carries an end-to-end arm proving the gate **CAN** return
   **`GATE FAIL`** (an outside-band CONVERGING family), and PASS and every
   NOT-A-RESULT cause, from `decide_verdict` [MEASURED, all arms reachable].

**THE CONVERGENCE / COMPLETION CLAUSE — declared expressly.** R2 keeps R1's
**fixed-iteration** mode (`fvSolution` `residualControl {}` empty; every level
runs the full `endTime` iterations). The completion signal is therefore the
same as R1's — **`last time == endTime`** and `ExecutionTime count == endTime`,
with the age guard and every other completion clause **unchanged**. The
convergence refusal is carried by the **PLATEAU CLAUSE**: a FIXED 500-sample
window on the per-iteration volume-average, minimum-sample refusal, a
peak-to-peak statistic that **rejects a growing series** (`ptp/(T_peak−T1) ≤
1e-6`), and a null-range refusal — the comparator **REFUSES an unconverged level
rather than grading it**, which is exactly R1's mechanism made a refusal.

`VERIFICATION_CHARTER` / VMFL063 §6 clause 4's **inversion** — *"for a
`residualControl`-terminated steady solve the honest completion is last `Time`
STRICTLY LESS THAN `endTime`"* — is the correct form **when `residualControl`
TERMINATES the solve**. R2 deliberately does **not** use `residualControl`
termination, for two reasons stated before compute: (a) it keeps R2 to **exactly
one** substantive change (endTime), and (b) it avoids introducing a
`residualControl` threshold as a **second tuning parameter** that could
under-provision and reproduce R1's failure for a different reason — the
`residualControl` threshold that also satisfies the plateau clause is not
predictable a priori, and R1 died of under-provisioning. The plateau clause
already provides the explicit unconverged-level refusal the fix requires. **This
is a resolved design decision, not a deferral; an adaptation is not a waiver and
no other completion clause is touched.**

## §8 — THE MANDATORY CONSISTENCY CHECK (from the manual's OWN inputs)

Manual p.119, verbatim: ρ 1 kg/m³, cp 1 J/kg-K, k 1 W/m-K, μ 300 kg/m-s;
r1 = 1 m, r2 = 2 m; Ω1 = 0, Ω2 = 0.5 rad/s; T1 = 273 K, T2 = 274 K.

| group | from the manual's own numbers | reading |
|---|---|---|
| moving-wall speed | U2 = Ω2 r2 = **1 m/s** | — |
| Reynolds | ρ U2 (r2−r1)/μ = **3.33e-3** | CREEPING; "laminar and steady" is CONSISTENT |
| Brinkman | μ U2²/(k ΔT) = **300** | viscous heating DOMINATES the 1 K wall difference — CONSISTENT with the title |

**No driving input is missing.** ρ and cp do not even enter the steady solution
(`v_r ≡ 0`, so no radial heat convection). It fell **CONSISTENT** — reported
whichever way it fell. [All figures DERIVED this lane; unchanged from R1's §A,
re-derived not transcribed.]

## §9 — DISCLOSURES

- **No pre-freeze observation of any gated value exists.** The bands on line 6
  are argued from the manual's 3% practice and the scheme's formal order, both
  fixed independently of any run.
- **The reference is a closed form this lane derived**, not a number lifted from
  the page; the manual prints only figures. §4 confirms it against two
  independent instruments.
- **Cost is EXTRAPOLATED, not MEASURED** — 5× R1's measured in-family per-level
  actuals; labelled EXTRAPOLATED on line 12 and in the register row.
- **The velocity channel's non-discriminator status is a grading-honesty change
  from R1**, which gated on velocity too. It is disclosed here, motivated by the
  VMFL070/VMFL061 trap, and touches no physics.
