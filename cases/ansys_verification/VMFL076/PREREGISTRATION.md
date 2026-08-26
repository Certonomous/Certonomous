# VMFL076 — Forced Convection Over a Flat Plate — PRE-REGISTRATION

**Frozen by sha at the commit that carries this file. No solver had run when it was
written: `verification/runs/ansys_verification/VMFL076/` did not exist at
2026-08-26T03:2xZ, checked by `test -d` on that exact path.** Written by
`ansys-lane-opus` from the standard-case form in
`docs/ansys_verification/PREREG_TEMPLATE.md` and all six of its amendments.

Built on the committed pre-freeze groundwork
`cases/ansys_verification/VMFL076/PREFREEZE_GROUNDWORK.md` (commit `671936c0`),
whose analytic reference was derived **before any case, mesh, launcher or
comparator existed** — which is why the gate below cannot have been chosen to fit
an answer.

---

## THE TEN-LINE FORM

```
 1. CASE            : VMFL076 — Forced Convection Over a Flat Plate — VM2026R1 p.219.
                      Solver = OpenFOAM v2606 simpleFoam (laminar) + the scalarTransport
                      function object for the energy equation. NOT YET RUN;
                      verification/runs/ansys_verification/VMFL076/ absent at 2026-08-26T03:2xZ.
 2. REFERENCE       : the Sparrow & Gregg low-Prandtl similarity solution, EVALUATED by
                      this lab (never digitised, never tabulated from a book):
                        theta'(0) = Nu_x/sqrt(Re_x) = 0.029370785745  at Pr = 0.003
                      and, on the frozen 201-point sample line at x = 0.75 m,
                        I_ref = INT_0^0.5 Theta dy = 6.131186321895e-02 m.
                      Manual reference line, p.219 verbatim: "NASA Memorandum 02-27-1959,
                      DETAILS OF EXACT LOW PRANDTL NUMBER BOUNDARY-LAYER SOLUTIONS FOR
                      FORCED AND FOR FREE CONVECTION, By E. M. Sparrow and J. L. Gregg,
                      Lewis Research Center, Cleveland, Ohio".
                      Ansys's own result, p.220: "Figure .76.2: Comparison of Normalized
                      Temperature with analytical results" — A FIGURE, NO NUMERIC TABLE.
                      CONTEXT ONLY; it is not digitised and it is not gated on.
                      LIMITATION, STATED ON THE REFERENCE LINE AS THE GROUNDWORK REQUIRED:
                      the NASA memorandum itself is NOT in this lab's archive. What is
                      evaluated here is the physics the manual's page describes, not that
                      document's tables. The Blasius constants are a control on THIS
                      lab's ODE solver, not proof that the memorandum agrees.
 3. REFERENCE KIND  : closed-form / exact — an independent similarity solution the lab
                      evaluates itself, with ZERO digitisation error. It is NOT the
                      manual's code output and NOT a code-to-code comparison.
 4. TIER CEILING    : **GATE REACHED**, and the reason is mathematical, not procedural.
                      The reference KIND would permit PASS. It is lowered here because the
                      reference solves the BOUNDARY-LAYER equations while the lab solver
                      solves the full incompressible Navier-Stokes + energy system, and at
                      Pr = 0.003 the thermal layer is NOT thin: delta_th/x = 0.23 at x = L,
                      so the streamwise-conduction term the reference drops is
                      O(eta^2/(4 Re_x)) — 0.17 % Theta-weighted on the gate scalar, 1.7 %
                      pointwise at eta_99. A reference that solves a DIFFERENT (approximated)
                      PDE cannot certify this code to PASS; it can be REACHED.
                      **Flagged for the supervisor: this is a deliberate lowering of a
                      ceiling the reference kind would otherwise allow.**
 5. QUANTITIES      : on ONE frozen sample line — x = 0.75 m, y = 0 .. 0.5 m, z = 0.025 m,
                      201 uniform points (spacing 2.5e-03 m), written by OpenFOAM's own
                      `sets` function object with `interpolationScheme cellPoint`:
                        Theta(y) = (T - T_inf)/(T_wall - T_inf)   [-]   (1 at wall, 0 far)
                        GATE A scalar  I_lab = trapz(Theta, y) over those points  [m]
                        GATE B scalar  max_i |Theta_lab,i - Theta_ref,i|          [-]
 6. BANDS (THE GATE): GATE A  |I_lab - I_ref| / I_ref  <=  3.00e-02  (3.00 %)
                      GATE B  max |dTheta|             <=  1.00e-02  (absolute)
                      BOTH must be met at the FINEST level (L3) for GATE REACHED.
                      Justification, budgeted BEFORE any run and never from a first result:
                        boundary-layer approximation in the reference   0.17 %  (computed)
                        far-field / displacement blockage at H = 0.5 m  <=0.50 %
                        leading-edge singularity + inlet-at-leading-edge <=0.50 %
                        outlet influence at 0.25 m upstream (alpha/U = 3.7 mm) <=0.10 %
                        discretisation at L3 (to be reported as GCI)     <=0.50 %
                        ------------------------------------------------------------
                        budget total                                     ~1.8 %
                      3.00 % is the manual's own stated goal and sits above that budget.
                      GATE B: the modelling budget above peaks at ~9e-04 in Theta; 1.00e-02
                      is one point of normalised temperature and is the honest band for a
                      pointwise profile comparison of this kind.
 7. LADDER          : OpenFOAM v2606 simpleFoam, `simulationType laminar` (manual p.219:
                      "Laminar steady flow", Re_L = 9.0e+04). Energy carried as a PASSIVE
                      scalar by the `scalarTransport` FO with D = alpha = k/(rho cp)
                      = 3.703703703703704e-03 m2/s, so Pr = nu/alpha = 0.003 EXACTLY.
                      nu = mu/rho = 1.111111111111111e-05 m2/s.
                      VISCOUS DISSIPATION IS OFF: Ec = 4.70e-04 and Sparrow-Gregg carry none
                      — the OPPOSITE of VMFL033, where dissipation is the whole physics.
                      Three birth-certified meshes (MESH_STANDARD §6): blockMesh writes the
                      certificate FROM the C field at time 0, nothing constructed from nx/ny.
 8. DECOMPOSITION   : grid triple, r = 2 in BOTH directions, geometric y-grading with the
    SEED              TOTAL expansion ratio held FIXED at 200 so the three meshes are one
                      family (first cell height falls as r^2, measured 2.157e-04 m at L1):
                        L1  160 x 60  =   9 600 cells
                        L2  320 x 120 =  38 400 cells
                        L3  640 x 240 = 153 600 cells
                      x is UNIFORM at every level, so x = 0.75 m is a mesh FACE at all three
                      (0.75/dx = 120 / 240 / 480) and the gate station is identical.
                      SERIAL — RANKS = 1, no decomposition, no RNG.
 9. PRINCIPAL RISK  : **the domain height clips the THERMAL layer.** delta_mom(L) = 0.0167 m
                      but delta_th(L) ~ 0.30 m — 18.3x thicker, because
                      delta_th/delta_mom ~ 1/sqrt(Pr). A domain sized off the momentum layer
                      would bias EVERY gated point. H = 0.5 m is eta = 173 at the gate
                      station against eta_99 = 67.76, a factor 2.56. If this is still not
                      enough the failure will show as a LOW I_lab at every level with a
                      CONVERGING triple — i.e. GATE FAIL, not NOT A RESULT.
                      SECOND named risk: the freestream/freestreamPressure far-field pair at
                      the top. If it misbehaves the symptom is a non-uniform edge velocity
                      and an I_lab error that does NOT shrink with refinement.
10. EXPECTED ORDER  : p_f = 2 (Gauss linear convection, corrected laplacian, trapezoidal
                      functional). Expect p_obs ~ 2. **p_obs > 2.4 is declared SUSPICIOUSLY
                      HIGH here and now — a warning (cancellation, a lucky mesh, a reference
                      coincidence), never a win.**
11. WEDGE/GEOM BIAS : N/A — Cartesian planar 2-D, not axisymmetric. No sin(t)/t term.
12. COST + CAP     : ESTIMATE, from a MEASURED basis: the pre-freeze residual probe ran
                      2500 SIMPLE iterations on the L1 mesh (9 600 cells, 1 rank) in
                      31.63 s wall = 1.318e-06 s per cell per iteration, measured on this
                      box. Scaled at that rate:
                        L1  2000 it x   9 600 cells ->   25 s ->  0.42 core-min
                        L2  3000 it x  38 400 cells ->  152 s ->  2.53 core-min
                        L3  5000 it x 153 600 cells -> 1012 s -> 16.87 core-min
                        total estimate 19.8 core-min; 30 core-min with a 1.5x contention margin.
                      CAPS (runaway guards, per level, enforced in the executable path by
                      timeout_s = cap*60/RANKS):  L1 10, L2 30, L3 150 — total 190 core-min.
                      Sanaa lifted the cost constraint on 2026-08-25: **a cap crossing is
                      REPORTED to the supervisor and extended by dated amendment if the work
                      is sound; it is a runaway guard, not a stop condition.** The launcher
                      prints `CAP CROSSED` and records rc = 124 in RUN_RC.txt either way.
                      cost_basis: core-minutes MEASURED from logs. The dollar figure —
                      190 core-min = 3.167 core-h x $0.0513/core-h = $0.163 at the
                      c7a.4xlarge rate — is **DERIVED at an owner-stated rate and
                      REPORTED-BY-OWNER, NOT MEASURED**: the box cannot read its own billing
                      (COMPUTE_BUDGET_CHARTER §5).
13. CONTROLS       : planted-zero (rule 3); strict completion with the age guard (rule 4);
                      Roache triple gating (rule 5); launcher freeze check (Amendment 2);
                      cap in the executable path, no `set -u`, mesh birth certificate,
                      launcher smoke test (Amendment 3); plateau clause (Amendment 4);
                      consumer-side field completeness (Amendments 5 / 5a); NO `assert`
                      carrying any guard (Amendment 6); no unconditional success print and
                      a mutation test recorded below (Amendment 6a).
                      Grading path, FIXED AT THIS COMMIT:
                      `cases/ansys_verification/VMFL076/grade_vmfl076.py`.
                      Launcher: `cases/ansys_verification/VMFL076/run_vmfl076.sh`.
```

---

## THE FINDING THIS FREEZE IS BUILT ON, AND THE CONTROL THAT PROTECTS IT

The pre-freeze groundwork established, and **this lane re-derived independently by a
different method** (scipy `solve_ivp` at rtol 1e-12 with an **analytic `erfc` tail**
replacing the groundwork's brute integration to eta = 200), that the obvious low-Prandtl
shortcut must not be the reference:

| quantity | value |
|---|---|
| exact similarity `theta'(0)` at Pr = 0.003 | **0.029370785745** |
| slug-flow / erfc shortcut `sqrt(Pr/pi)` | **0.030901936162** |
| gap, normalised **by the slug value** | **4.954869 %** — the groundwork's 4.955 % figure, reproduced |
| gap, normalised **by the exact value** (`\|lab-ref\|/\|ref\|`, the gate's own normalisation) | **5.213175 %** |

**Both normalisations are recorded because they are not the same number and only the
second is the one a gate would read.** The finding is unchanged and is stronger under the
gate's normalisation: the shortcut is **outside any tolerance worth registering**.

**The finding is locked into the instrument.** `control_slug_shortcut_is_not_the_reference`
recomputes the gap at grade time and **refuses (exit 2)** unless it equals
4.954869 % ± 0.01. Substituting the slug/erfc shortcut for the exact solution makes the
comparator refuse rather than grade — demonstrated by mutation below (`mut_slug`).

Two classical constants control the ODE solver itself, and the comparator refuses if
either misses: `f''(0) = 0.332057336215` against the classical `0.33205733621519630`, and
the Blasius displacement constant `beta = 1.7207876576` against `1.7207876575`.

## THE MANDATORY CONSISTENCY CHECK — IT FELL CONSISTENT

From the manual's own p.219 inputs (rho = 900, mu = 0.01, cp = 42.6, k = 142, U = 1,
T_inf = 300, T_wall = 350, L = 1): **Pr = 3.00e-03** (the page says "very low Prandtl
numbers, typically encountered in liquid metal flows"); **Re_L = 9.00e+04** (below the
~5e5 transition, so "Laminar steady flow" is consistent); **Pe_L = 270**;
**Ec = 4.70e-04** (dissipation negligible). **No driving input is missing.** Unlike
VMFL036, this page's numbers and its stated physics agree, so the case is standard and
takes the template-speed form.

## THE PLATEAU CLAUSE (Amendment 4), AND THE ONE PLACE IT IS READ NARROWLY

Window: the **FIXED** interval `[endTime - 1000, endTime]` in SIMPLE iterations, sampled
every 50 iterations, so **21 samples** at every level against a registered floor of **12**;
below the floor the comparator refuses `CANNOT_TELL`, never a lenient pass. Settled requires
BOTH `peak-to-peak/mean <= 2.0e-04` AND `|trend*window|/mean <= 1.0e-04` — a
trend fit that **rejects a growing series**, not a coefficient of variation. `n_window` and
`n_distinct` are printed in the grading artifact.

**The null-range refusal is placed on the WHOLE SAMPLED SERIES, not on the settling
window, and this is a deliberate reading stated before any run.** Measured on the pre-freeze
residual probe: this case drives every residual to ~1e-12 by iteration 1000, so a correct,
fully converged run can write an **exactly identical** value through the whole settling
window. Refusing that would refuse a correct run — the unsafe-for-progress direction
Amendment 5a names. So: **if the estimator saw no variation ANYWHERE across the run it
refuses (a dead series); having been shown able to see this run's own motion, a frozen
settling window is convergence.** Both directions are controlled (`K7` refuses a globally
null series, `K7b` accepts a moved-then-frozen one).

## PRE-FREEZE VERIFICATION, ALL RUN AND ALL RECORDED

| check | result |
|---|---|
| Amendment 6 statement-type sweep, `grep -nE '^[[:space:]]*assert[[:space:]]'` on the comparator | **0 asserts** |
| `--selftest`, `python3` | rc **0**, `SELFTEST GREEN: 10/10 controls passed.` |
| `--selftest`, `python3 -O` | rc **0**, `SELFTEST GREEN: 10/10 controls passed.` |
| launcher smoke test (`run_vmfl076.sh smoke L1`, scratch root, 60 iterations) | rc **0** |
| rule-4 guard, relaunch into a directory already holding `0/` | rc **2**, refused |
| residual probe, 2500 iterations on the L1 mesh | rc 0, 31.63 s wall, residuals ~1e-12 by it. 1000, no NaN, no bounding |

### THE MUTATION TEST (Amendment 6a item 3) — seven controls broken, fourteen runs

Each mutant breaks one control on a sacrificial copy so that control **must** fail.
`--selftest` was then run under **both** interpreters. Required outcome: non-zero exit
**and no green line**.

| mutant (what was broken) | rc `python3` | rc `python3 -O` | green lines |
|---|---|---|---|
| `mut_estimator` — `theta_integral` returns 0.0 | **2** | **2** | **0** |
| `mut_slug` — `theta'(0)` replaced by the slug shortcut `sqrt(Pr/pi)` | **2** | **2** | **0** |
| `mut_plateau` — settling statistic always `True` | **2** | **2** | **0** |
| `mut_completion` — `completion_check` can never raise | **2** | **2** | **0** |
| `mut_vocab` — the verdict-vocabulary guard disabled | **2** | **2** | **0** |
| `mut_reader` — the 195-point gate-line floor disabled | **2** | **2** | **0** |
| `mut_ode` — the Blasius RHS changed from `-0.5 f f''` to `-0.4 f f''` | **2** | **2** | **0** |

**Fourteen of fourteen refused; zero green lines.**

**And one negative result recorded because it decides how this test must be written.**
An eighth mutant was tried first and is NOT in the table: it *disabled* the Blasius check
(`if abs(sim.fpp0 - BLASIUS_FPP0) > 1e-8:` → `if False:`). It exited **0** and printed a
green line under **both** interpreters — correctly, and it proves nothing. **Removing a
check is not breaking a control: the measured quantity was still right, so nothing had to
fail.** A valid mutation must break what the control MEASURES — here the ODE itself
(`mut_ode`), which then makes the control fire. Written down because the invalid form is
the easy one to reach for and it manufactures a green that looks like evidence. The success print sits after ten controls
each of which exits 2 on its own failing path, so the claim is unreachable when its checks are.

## WHAT WAS AND WAS NOT OBSERVED BEFORE THIS FREEZE

**The gate value is analytic and was fixed at commit `671936c0`, before any case, mesh,
launcher or comparator existed.** The pre-freeze smoke and residual probes measured
**only** wall-clock per iteration, solver return codes, residual decay, mesh statistics
and the absence of NaN. **No gate scalar, no `I_Theta`, and no `Theta` profile was
computed from any pre-freeze run**, and no pre-freeze run wrote into
`verification/runs/ansys_verification/VMFL076/`.

## THE VERDICT RULE (rule 5 order, and it can only make a row worse)

1. Any level failing strict completion, or not plateaued → **`NOT A RESULT`**.
2. Grid triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → **`NOT A RESULT`**, with
   the value, the triple and the orders printed beside it.
3. Triple `CONVERGING` → **`GATE REACHED`** if BOTH bands are met at L3, else
   **`GATE FAIL`**. GCI at Fs = 1.25, never quoted on a non-monotone triple.

**`PASS` is unavailable to this case by line 4 above, whatever the number.**
