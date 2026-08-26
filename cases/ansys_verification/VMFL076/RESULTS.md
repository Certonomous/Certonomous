# VMFL076 — Forced Convection Over a Flat Plate — RESULTS

## VERDICT: **`NOT A RESULT`**

**Both frozen gates were met at the finest level, and the row is still `NOT A RESULT`,
because the grid triple is `OSCILLATORY`.** CLAUDE.md rule 5 fixes that order and fixes
its direction: the triple can only turn a result **into** `NOT A RESULT`, never the
reverse. The value, both error terms and the classification are printed beside it below,
as rule 5 requires.

Graded by the frozen comparator `cases/ansys_verification/VMFL076/grade_vmfl076.py`,
blob `42c8945544721e60a41fbe1a01513405b64d5f3c`, re-proved equal to its HEAD blob at
grade time. Pre-registration `PREREGISTRATION.md`, blob
`a0d5cb5b04d8e41096b8915e957f67d73577a93f`, frozen at commit
**`ab168c0e802e89cd32cce0467f0ce67b63c5685c`** — **before any solver started**, and the
launcher printed `FREEZE VERIFIED` against both blobs before every level.
Raw grading output: `cases/ansys_verification/VMFL076/GRADING_OUTPUT.txt`.

---

## 1. THE MEASUREMENT

Gate scalar `I = INT Theta dy` over the frozen 201-point sample line at x = 0.75 m,
`Theta = (T - T_inf)/(T_wall - T_inf)`. Reference evaluated by the same discrete
functional on the same points, so the quadrature error is identical on both sides.

| level | cells | first cell height [m] | `I_lab` [m] | deviation from reference | max &#124;dTheta&#124; |
|---|---|---|---|---|---|
| L1 | 9 600 | 2.15705466e-04 | 6.080627762560e-02 | **−0.824613 %** | 6.3258e-03 |
| L2 | 38 400 | 1.09390746e-04 | 6.075620301094e-02 | **−0.906285 %** | 5.6925e-03 |
| L3 | 153 600 | 5.5081298e-05 | 6.075971480062e-02 | **−0.900557 %** | 5.3969e-03 |

Reference, evaluated not digitised: `I_ref = 6.131186321895e-02 m`, from the Sparrow &
Gregg similarity solution at Pr = 0.003 with `theta'(0) = Nu_x/sqrt(Re_x) = 0.029370785745`.

**The two frozen gates, at the finest level:**

| gate | measured | band | |
|---|---|---|---|
| A — &#124;I_lab − I_ref&#124;/I_ref | **0.900557 %** | ≤ 3.00 % | **met** |
| B — max &#124;dTheta&#124; | **5.396919e-03** | ≤ 1.00e-02 | **met** |

**And the row is still `NOT A RESULT`. That is the rule working, not the rule
misfiring.**

## 2. THE TRIPLE, AND WHY IT CARRIES NO ORDER

```
e21 = I(L2) − I(L1) = −5.007461e-05
e32 = I(L3) − I(L2) = +3.511790e-06
R   = e32/e21       = −0.070131      ->  OSCILLATORY
```

The sign flipped and the magnitude collapsed 14×. **`p_obs` is not quoted and `GCI` is
not quoted** — rule 5 forbids a GCI on a non-monotone triple, and an order fitted to a
sign change is not an order. For the record and explicitly NOT as a result: on the
magnitudes alone the fit would read **3.834**, which is above the **2.4** threshold this
pre-registration declared **SUSPICIOUSLY HIGH before any compute** (line 10). **Both
readings of this triple say the same thing: it is not in an asymptotic range.**

**The diagnosis, and it is not a solver fault.** Between L2 and L3 the gate scalar moves
by **5.78e-05 relative** — the discretisation error was already exhausted at L2, and what
remains is not the leading truncation term but non-smooth residue (the singular
leading-edge cell, the `cellPoint` interpolation onto the fixed line, the graded-mesh
first-cell placement). **The grid family was refined past its own asymptotic range**, so
no order can be extracted from it. A useful triple for this case would be COARSER, not
finer.

**A second reading, which is the physically interesting one.** The deviation from the
reference is **−0.9063 %** at L2 and **−0.9006 %** at L3 — it does not move under a 4×
cell-count increase. **The ~0.90 % shortfall is therefore MODELLING, not
discretisation**, and it sits inside the ~1.8 % error budget totalled in the
pre-registration before any run — dominated there by the boundary-layer approximation in
the reference (0.17 % Theta-weighted), the far-field treatment and the leading-edge
singularity. **The pre-registration predicted the size of this gap and was right.**

## 3. THE LOAD-BEARING FINDING, TESTED AGAINST A REAL RUN

The pre-freeze groundwork ruled that the obvious low-Prandtl slug/erfc shortcut must not
be the reference. With a graded run in hand that ruling can now be scored rather than
argued. On this case's own gate scalar:

| reference used | `I_ref` [m] | what the L3 gate would have read |
|---|---|---|
| **exact similarity ODE (what was frozen)** | 6.131186321895e-02 | **−0.900557 %** |
| slug / erfc shortcut `sqrt(Pr/pi)` | 5.947637936396e-02 (**−2.9937 %**) | **+2.157723 %** |

**Stated honestly, including the part that does not flatter the finding: on THIS gate the
shortcut would not, by itself, have flipped the verdict — +2.16 % is still inside the
3.00 % band.** What it would have done is consume **72 % of the tolerance instead of
30 %**, and **reverse the reported sign**, turning a 0.90 % agreement into a 2.16 %
disagreement in the opposite direction. On the primary similarity scalar the shortcut is
**5.2132 % high** (normalised by the exact value, the gate's own normalisation), which no
tolerance here would have survived. **The ruling stands; its margin on this particular
scalar was narrower than the headline number suggests, and that is worth knowing.**

## 4. THE CONTROLS, ALL LIVE AT GRADE TIME

Ten controls ran before any level was read, each refusing (`exit 2`) on its own failing
path: the Blasius constants `f''(0) = 0.332057336215` and `beta = 1.7207876576`; the
**slug-shortcut control**, which refuses unless the exact/shortcut gap is 4.954869 %
± 0.01, so substituting the shortcut makes the instrument refuse rather than grade; the
rule-3 planted controls (a known +1.234 K plant must move the estimator by exactly
1.234/50 × (y_max − y_min), and a line held at `T_inf` must integrate to exactly zero and
then SEE a single planted spike); the Roache classifier; the plateau clause; the strict
completion refusal; the rule-1 vocabulary guard; the gate-line floor and grid checks.

**Comparability was proved, not assumed** (Amendment 5a): the comparator refuses unless
all three levels return the identical 201-point y-vector to 1e-12, and it re-reads the
frozen station `(0.75 0 0.025) -> (0.75 0.5 0.025)`, `nPoints 201`, out of each run's own
`system/controlDict`.

**Strict completion (rule 4)** held at every level: `rc = 0`, an `End` line, last time ==
`endTime`, `ExecutionTime` count == `endTime`, `T U p` present at `endTime`, and every one
of them newer than that case's own `0/T` (the age guard).

**Settling (Amendment 4)**, fixed window of the last 1000 iterations, 21 samples against a
floor of 12 at every level:

| level | n_window | n_distinct | peak-to-peak/mean | trend | settled |
|---|---|---|---|---|---|
| L1 | 21 | 6 | 2.039e-10 | 7.979e-11 | yes |
| L2 | 21 | 17 | 1.758e-09 | 9.386e-10 | yes |
| L3 | 21 | 21 | 4.573e-05 | 4.027e-05 | yes |

**The deliberate narrow reading registered before the run earned its keep.** L1's window
holds only 6 distinct values in 21 samples at a peak-to-peak of 2e-10; had the null-range
refusal been placed on the settling window rather than on the whole series, a correct,
fully converged level would have been refused. It was placed on the whole series instead,
and both directions are controlled.

## 5. COST — ESTIMATE VERSUS ACTUAL (rule 12)

| level | predicted [core-min] | actual [core-min] | ratio | cap |
|---|---|---|---|---|
| L1 | 0.42 | **0.4500** | 1.071 | 10 |
| L2 | 2.53 | **3.3833** | 1.337 | 30 |
| L3 | 16.87 | **45.0667** | 2.672 | 150 |
| **total** | **19.82** | **48.9000** | **2.467** | **190** |

Actuals measured from each level's own `RUN_RC.txt` (`wall_s × ranks ÷ 60`, ranks = 1).
**No cap was crossed** (4.5 % / 11.3 % / 30.0 % of each). **Waste: 0.000 core-min** —
nothing stalled, nothing was killed, nothing re-run; no level's `wall_s` reaches the
3600-s stall trigger except L3 at 2704 s, which is below it, so cleaned == gross.

**Gap attribution, and the transferable datum.** The prediction's basis was a rate
**measured on this box** — 2500 iterations on the L1 mesh in 31.63 s = **1.318e-06 s per
cell per iteration**. On its own mesh it was excellent (**1.071×**). It degrades with mesh
size: the realised rate is **1.41e-06** at L1, **1.76e-06** at L2 and **3.52e-06 s/cell/it**
at L3 — **2.67× the calibration rate at 16× the cells**. **A per-cell-per-iteration rate
calibrated on a small mesh does not extrapolate up; it under-predicts.** Cause is not
isolated here and is not claimed to be: GAMG work per cell grows with mesh size, and the
box carried three of this team's levels plus three heat-transfer solvers concurrently.
**Contention is named and NOT separated from mesh-size scaling** — no uncontended control
was bought, so none is inferred. The direction of the evidence favours mesh-size scaling,
since L1 ran under the same contention and was only 7 % over.

**$0.0418 DERIVED, NOT MEASURED**, at $0.0513/core-h (c7a.4xlarge, owner-stated) — the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

## 6. DRAFT REGISTER ROW (for the supervisor to rule on and land)

```
VMFL076 | Forced Convection Over a Flat Plate | p.219 | OpenFOAM v2606 simpleFoam
  + scalarTransport | reference: Sparrow-Gregg similarity ODE, closed form,
  EVALUATED by the lab (zero digitisation error) | ceiling GATE REACHED (lowered from
  the PASS the reference kind allows: the reference solves the boundary-layer
  equations, the solver full Navier-Stokes+energy, delta_th/x = 0.23 at Pr = 0.003)
  | VERDICT: NOT A RESULT | reason: grid triple OSCILLATORY (R = -0.0701), rule 5
  | gates A and B BOTH MET at L3 (0.9006 % vs 3.00 %; 5.397e-03 vs 1.00e-02) and
  the row is still NOT A RESULT | GCI NOT QUOTED (non-monotone) | 48.90 core-min
  of 190 cap | freeze ab168c0e | grading GRADING_OUTPUT.txt
```

**This case buys NO credential.** It is not a V and not a P. Recorded so the register
carries the honest count.

## 7. WHAT WOULD MAKE THIS A RESULT, AND WHAT WOULD NOT

**Would not:** refining further. L2→L3 already moved the scalar by 5.78e-05 relative;
an L4 would sit deeper in the same noise.

**Would:** a COARSER triple that sits inside the asymptotic range — e.g. 40×15, 80×30,
160×60, with L1 of this run as its finest level. That is a NEW pre-registration with its
own freeze, not an amendment to this one: after first compute, gates are closed. It is
proposed here and is **not** decided by this lane.

**Recorded as NOT VERIFIED**, carried forward from the groundwork: whether NASA
Memorandum 02-27-1959 tabulates values differing from this similarity solution at
Pr = 0.003. **The memorandum is not in the lab's archive.** The Blasius constants control
this lab's ODE solver; they are not proof that the memorandum agrees.

---

## ADDENDUM 1 — 2026-08-26 — the contention measurement §5 asserted but did not show

**Appended at the foot, not an edit above. Lines whose number changed above this section:
0. No verdict, value, band, triple state, cap or label moves by anything below.**

§5 attributed the 2.467× cost gap to mesh-size scaling and named contention as
unseparated. **It did not print the measurement that excludes the coarse form of
contention, and an attribution whose evidence is not on the page is an assertion.** The
measurement, read from each level's own `log.simpleFoam` and `RUN_RC.txt`:

| level | `ExecutionTime` [s] | `ClockTime` [s] | launcher `wall_s` | ClockTime/ExecutionTime | wall_s/ClockTime |
|---|---|---|---|---|---|
| L1 | 27.44 | 27 | 27 | 0.9840 | 1.0000 |
| L2 | 203.26 | 203 | 203 | 0.9987 | 1.0000 |
| L3 | 2697.44 | 2704 | 2704 | 1.0024 | 1.0000 |

Box load average during L3 was 13–21 on 16 cores (this team's three levels plus three
heat-transfer solvers). **Both ratios sit at 1.00 at every level: the solver process was
never descheduled, and the launcher's wall equals the solver's own clock exactly.** So
**the wall time is clean in the CPU-starvation sense, stated as a measurement rather than
assumed by default** — and that is the honest limit of the claim. It **excludes CPU
starvation only.** Memory-bandwidth contention slows a process without moving either
ratio, so it and GAMG-per-cell growth remain the two live candidates for the L3 gap and
**they are NOT separated here.** No uncontended control was bought, so none is inferred.
The direction of the evidence still favours mesh-size scaling, because L1 ran under the
same load and came in at 1.071×.
