# T1c results: the first thermal rung this lab has graded against a reference that cannot be wrong

Campaign T, tier 1, rung T1c. Written 2026-08-19, after the cases reported.
Run tree `verification/runs/T-family/T1_runs/`.

**Rung verdict: GATE FAIL — 1 of 4 graded rows failed.**

---

## 1. The rows

| row | quantity | value | exact | deviation | GCI band | observed `p` | verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| L0 | `Nu`, constant `Ts` | 3.659958 | 3.6567934 | 0.0865 % | 0.0301 % | 1.854 | **GATE FAIL** |
| L1 | `f·Re` | 63.98771 | 64 | 0.0192 % | 0.0236 % | — | **PASS** |
| L2 | `Nu`, constant `q″` | 4.365298 | 4.3636364 | 0.0381 % | 0.0459 % | 2.031 | **PASS** |
| L3 | `f·Re` | 63.98771 | 64 | 0.0192 % | 0.0236 % | — | **PASS** |
| L4 | `Nu` at the station as originally registered | 3.658427 | 3.6567934 | — | — | — | **NOT A RESULT** |

**Both controls behaved as registered.** C1, sampled at `x/D = 1` inside the
thermal entry length, returned `Nu = 6.2812` against the fully developed 4.3636
— **+43.9 %**, which it had to exceed. C2, grading the constant-flux arm against
the constant-temperature constant, deviated **19.38 % against a band of
0.046 %** and failed, which it had to.

**The references are derivations, and the comparator refuses to run unless they
reproduce.** `f·Re = 64` from the integrated Hagen–Poiseuille profile, `48/11`
by quadrature, and `3.656793` from solving the Graetz eigenproblem by inverse
iteration — first eigenvalue **λ₀² = 7.313587**, agreeing with the tabulated
value to **1.6e-08**.

---

## 2. Three defects in the comparator, and none of them in the cases

**The rung first read GATE FAIL and DIVERGENT, and all of that was measurement.**
The solutions were correct throughout: the velocity field is **Poiseuille to
0.17 %**, and the temperature field matches the **exact Graetz eigenfunction to
0.03 %** — θ(0)/θ_m of **1.80203** measured against **1.80262** analytic, and
constant with `x`, which is what fully developed means.

**2.1 A dead precondition made a whole arm unreachable.** `measure()` read the
wall patch, refused when it came back empty, **and never used the value.** ESI
writes a `fixedGradient` patch with no `value` entry, so the check was
structurally unsatisfiable for the entire constant-flux arm. **A gate on a
quantity the code discards is not a safeguard, it is an outage.**

**2.2 The wall radius was assumed rather than read, and it cost 9 % of the
Nusselt number.** An OpenFOAM wedge replaces the arc by a chord, so the wall
face lies at `y = R·cos(2.5°) = 0.00999048`, not at `R = 0.01`. Taking it at
`D/2` overstated the wall-normal distance by a **fixed 9.5e-06 m**.

**That fixed absolute error is the whole trap: `h` shrinks under refinement, so
the RELATIVE error grew — 3.8 %, 6.1 %, 9.7 % across the three levels — and
Nusselt moved AWAY from exact as the mesh improved.** The triple reported
**DIVERGENT at an observed order of −0.80**, which looks exactly like a
discretisation failure and was not one. **A 0.095 % error in a geometric
constant produced a 9 % error in the graded quantity and a false verdict about
the numerics.** Reading the radius from `polyMesh/points` turns the same
solutions **CONVERGING at order 1.854**.

**2.3 A guard fired on physics it was not written for.** The saturation guard
killed the constant-flux arm at a driving fraction of 0.089, when that arm's
wall-to-bulk difference is **constant by construction and cannot saturate.**
Restricted to the constant-`Ts` arm.

---

## 3. The convergence gate, and what paid for it

**No case tripped `residualControl` — not one of the six, at either `endTime`.**
At the registered `endTime` of 6000 the fine constant-flux case was still moving
its temperature field by **4.081 K between iterations 5000 and 6000**, while the
coarse and medium cases were **bit-identical** over the same interval. Graded as
converged it put `Nu` at **4.622 against an exact 4.364** and turned the grid
triple **OSCILLATORY** — an iteration-count problem wearing the clothes of a
discretisation one.

**Residuals would not have caught this cleanly:** that case's reported `T`
residual was an unremarkable **4e-05**. Comparing the written fields is the
direct test, and it is now a gate that refuses any grid claim from a triple
containing an unconverged level.

**That gate is only possible because `writeInterval < endTime`.** The durability
fix in `LESSONS.md` L-140 — made this morning after a crash destroyed an
85 %-complete run — is what leaves two checkpoints on disk to compare. **A
change made to survive a crash turned out to buy a verification instrument.**

`endTime` was amended 6000 → 30000 **on that measurement**. At 30000 every one
of the six is byte-identical between its last two checkpoints, **and the zero was
confirmed with a live planted perturbation** rather than trusted: the same
parser on the same files measures the real change from the initial field
(9.999989 K to 30.405249 K across the cases) and recovers a planted 1.234e-03 K
offset exactly.

---

## 4. Two amendments to the pre-registration, both mine, both disclosed

**4.1 The registered sampling station was wrong for the constant-`Ts` arm.** The
pre-registration checked the thermal **entry** length and never the thermal
**saturation** length. For a constant-`Ts` pipe the driving difference decays as
`exp(−4Nu(x/D)/(Re·Pr))`, which at the registered `x/D = 40` has fallen by a
factor of **3792** — to 0.0026 K out of 10 K. The replacement station is derived
from that closed-form law, which **contains no solved quantity and could have
been evaluated before a case existed**. **The original station is kept and
graded as row L4 rather than deleted**, because it is the row the amendment
exists for.

**4.2 The registered `endTime` was too short**, per §3.

---

## 5. What this rung does and does not establish

**It establishes that the solver, the mesh and the boundary conditions reproduce
exact laminar theory to better than 0.1 %, at second order, on both thermal
boundary conditions and on friction.** That is the precondition every turbulent
thermal claim above it rests on, and until now this lab had never checked it.

**It grades no turbulence model.** A laminar solution has no closure.

**The GATE FAIL is real and is not excused.** Row L0 deviates 0.0865 % against a
band of 0.0301 %. **Both arms overshoot the exact constant even after Richardson
extrapolation to zero mesh spacing** — +0.1106 % and +0.0748 % — so the excess is
**not discretisation error**. Its cause is under test in
`DIAGNOSTIC_PREDICTION.md`, whose predictions were registered before either
diagnostic case was built. **Explaining a failure is not the same as excusing
it, and no verdict here moves on the outcome of that test.**
