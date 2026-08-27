# T19 — fully developed laminar forced convection between parallel plates, EXACT tier: pre-registration (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** Campaign T, rung **T19** — the **planar partner of T1c**, and the rung
that puts a graded number into the capability grid's **`forced convection ×
laminar × 2D`** cell, which at HEAD `cbcb1127` reads **`CAN NOT DO — not
attempted as a graded heat-transfer class`**
(`docs/capability/heat-transfer_GRID.md:53`). That cell's own note names what
does *not* count toward it: K0e is a specification at zero compute, E4a2 backs a
flow boundary condition rather than a heat-transfer quantity, and KV1 validated
an instrument and grades no case. **T19 is the first graded heat-transfer case
proposed for that cell.** Verdict vocabulary fixed by `CLAUDE.md` rule 1.
Written by a heat-transfer lane; decisions `[lab-attributed]`. **Nothing here
has been sent, filed, submitted, uploaded, registered or posted outside this
box, and nothing in it may be (rule 7).**

## 0. What this rung is, what it is not, and what it can reach

**Laminar flow and heat transfer between two parallel plates**, `Re_Dh` = 100,
`Pr` = 0.71, solved with `buoyantBoussinesqSimpleFoam` at `simulationType
laminar`, `beta = 0` and `g = (0 0 0)` — T1c's registered configuration
(`build_t1c.py:219`, *"ZERO GRAVITY IS THE POINT"*), which with `beta = 0`
decouples momentum from `T` and makes the solver a pure incompressible
forced-convection solver. The **full gap** is meshed — no symmetry plane is
imposed — so the symmetry of the answer is a **witness** rather than an
assumption. Two wall arms (uniform temperature, uniform heat flux), six cases,
one registered sampling station.

> **T19 earns a verdict for FORCED CONVECTION, LAMINAR, 2-D, EXACT tier**, and
> nothing else. It earns **nothing turbulent**, **nothing 3-D**, nothing
> conjugate, and nothing for the entrance region, which is solved but not graded.

**THE CEILING, STATED BEFORE THE RUN.** Every reference here is a closed form or
a quantity this rung's own module derives from the governing equations. Under
the upheld V/P ruling that scores **V and never P**: this rung reaches **GATE
REACHED at best and can NEVER reach HOLDS.**

**NO PAPER IS CITED AND NONE IS NEEDED.** This is an EXACT-tier rung in the
sense of `T_FAMILY_INDEX.md` §1: nothing has to be acquired and the reference
cannot be wrong. Rule 15 is therefore not engaged — no retrieved document is
relied on anywhere in this registration.

**Condition at freeze** (rule 2), checked immediately before this commit:
`verification/runs/T-family/T19_runs/{P_q_c,P_q_m,P_q_f,P_Ts_c,P_Ts_m,P_Ts_f}`
each hold `0.orig/`, `constant/`, `system/`, `BUILD.txt`, `CASE.txt`,
`log.blockMesh`, `log.checkMesh.build` — **no `0/`, no numeric time directory,
no `log.solve`, no `STATUS.*`, no `DONE.*`.** Zero core-minutes in the registered
tree.

**`endTime` = 30 000 is an ITERATION COUNT** (`deltaT` = 1, steady `ddtSchemes`),
T1c's registered count, not a placeholder and not a physical time.

## 1. The analytic referent — derived, not transcribed (`exact_t19.py`)

**The generic duct.** The parallel-plate channel and the round pipe are the same
one-dimensional problem with a geometry index `s`: the transverse Laplacian is
`(1/xi^s) d/dxi (xi^s d/dxi)` on the half-domain `xi` in [0,1], symmetry at
`xi = 0`, wall at `xi = 1`.

    s = 0   parallel plates, xi = distance from the mid-plane / half-gap a,
            full gap b = 2a, Dh = 2b = 4a
    s = 1   round pipe,      xi = r/R, a = R, Dh = 2R
    Dh = 4a/(1+s) in both.

**EVERYTHING IS COMPUTED FOR GENERAL `s` AND THEN CHECKED AT `s` = 1 AGAINST
T1c's REGISTERED PIPE NUMBERS, WHICH THIS MODULE DID NOT COMPUTE.** A route
that cannot reproduce the pipe is not used for the plates. Measured:

| quantity | T1c registers | this module at `s` = 1 |
|---|---|---|
| `f·Re` | 64 | **64.00000000** |
| `Nu` (uniform `q"`) | 48/11 = 4.3636364 | **4.36363639** |
| `Nu` (uniform `T_s`) | 3.6567934 | **3.65679346** |

1. **`f·Re`, closed form.** `u = u_max(1 - xi²)` with `u_max/ubar = (s+3)/2`;
   the force balance and `f = (-dp/dx)Dh/(rho ubar²/2)` give
   **`f·Re = 32(s+3)/(1+s)`** — 96 for plates, 64 for the pipe.
2. **`Nu` for uniform wall heat flux, by double quadrature** of the fully
   developed energy equation. The plate value is additionally checked against
   its own closed form **140/17 = 8.2352941176**, and agrees to **1.0e-08
   relative**. *(A first-order defect was found and fixed by driving this: the
   cumulative trapezoid began from zero rather than from the integrand's value
   at `xi` = 0, which is `3/2` for plates and `0` for the pipe — so the pipe was
   already at 5.7e-09 while the plates converged at O(h) and missed 140/17 by
   5.4e-05. It is fixed and the fix carries the measurement in a comment.)*
3. **`Nu` for uniform wall temperature, by eigenvalue.**
   `(1/xi^s)(xi^s psi')' + Lambda (u/ubar) psi = 0`, `psi'(0) = 0`, `psi(1) = 0`,
   discretised conservatively on cell centres and solved by inverse iteration
   with a tridiagonal Thomas solve — **no third-party dependency** — then
   **Richardson extrapolated over two ODE meshes**. The route is verified second
   order in its own ODE mesh (measured ratio **4.000** over M = 2000/4000/8000).

**The NORMALISATION control.** A uniform scaling of the velocity satisfies the
ODE and the no-slip wall exactly and is invisible to both; it is caught by
requiring the bulk mean of `u/ubar` to be 1. `--selftest` REFUSES a 1 % and a
**1e-06** mutation. **SELFTEST PASS (0 failed).**

| PLATE reference | value |
|---|---|
| `f·Re` | **96.0000000000** (exact) |
| `Nu` uniform `q"` | **8.2352942009** (140/17 = 8.2352941176) |
| `Nu` uniform `T_s` | **7.5407008741** |

## 2. The registered case (`build_t19.py`)

| quantity | value |
|---|---|
| full gap `b` / `Dh` | 0.02 m / 0.04 m |
| length `L` / station `x_s` | 1.2 m (30 `Dh`) / **0.8 m (20 `Dh`)** |
| `x+ = x_s/(Dh Re Pr)` | **0.28169** |
| `nu` / `Pr` / `Re_Dh` / `U0` | 1.5e-05 m²/s / 0.71 / 100 / 0.0375 m/s |
| inlet | uniform `U0`, uniform `T_in` = 300 K |
| walls, Ts arm | `fixedValue` **400 K** on BOTH walls |
| walls, q arm | `fixedGradient` **500 K/m** on BOTH walls |
| solver / closure | `buoyantBoussinesqSimpleFoam` / **`simulationType laminar`, `beta = 0`, `g = 0`** |
| `endTime` / `deltaT` / `writeInterval` | 30 000 iterations / 1 / 2 000 |
| **ranks / decomposition seed** | **1 / `serial, 1 rank, no decomposition`** |

| level | `nx` × `ny` (full gap) | cells | `dx` (m) | `dy` (m) |
|---|---|---:|---:|---:|
| `c` | 120 × 20 | 2 400 | 0.01 | 1.0e-03 |
| `m` | 240 × 40 | 9 600 | 0.005 | 5.0e-04 |
| `f` | 480 × 80 | 38 400 | 0.0025 | 2.5e-04 |

`r = 2` exactly **in both directions**, and `build_t19.py --check-levels`
refuses a ladder that is not (driven). **The station lies on a cell FACE on
every level** (0.8/dx = 80, 160, 320), so the reader's axial interpolation is the
mean of the two straddling columns and is the same operation at every level; the
builder refuses a station that is not (driven).

**`T_wall` is 400 K and not T1c's 310 K, and the reason is registered.** The
graded constant-`T_s` Nusselt number is `q"Dh/(k(T_w - T_m))`, and at `x+` =
0.2817 the wall-to-bulk difference has decayed to about 2.0e-04 of the inlet
difference. With T1c's 10 K that is 2.0e-03 K; with 100 K it is 2.0e-02 K, ten
times better conditioned, and `beta = 0` makes the larger difference dynamically
inert. **T1c's constant-`T_s` row is the one that GATE FAILED**
(`T1c_RESULTS.md:14`, 0.0865 % against a 0.0301 % band; *"The GATE FAIL is real
and is not excused"*, `:123`), and conditioning is one of the two things this
rung changes about it. The other is the band — §3.

**C_PROV was driven, and it fired.** `scripts/check_case_provenance.py` REFUSED
the first draft of this case template for the compressible scheme spelling
`div(((rho*nuEff)*dev2(T(grad(U)))))` — the T4 provenance defect. It was removed
before the build; the checker now returns **rc = 0** on the built case, inside
`build_t19.py --selftest`.

## 3. Graded rows, bands, gate

Floors imported from `scripts/roache_triple.py`; the comparator defines none and
refuses if the registered copy differs (driven). `dim = 2`, `Fs` = 1.25.

| row | quantity | arm | reference | band (rel.) | predicted fine deviation |
|---|---|---|---|---|---|
| **G1** | `f·Re` at the station, from the **axial pressure gradient** between the two straddling columns | `P_q_*` | **96.0** | **±8.0e-04** | **−3.12e-04** |
| **G2** | `Nu` for uniform wall heat flux | `P_q_*` | **8.2352942009** | **±1.6e-03** | **+6.19e-04** |
| **G3** | `Nu` for uniform wall temperature | `P_Ts_*` | **7.5407008741** | **±3.5e-03** | **+1.41e-03** |

The pressure route for `f·Re` is second order in `dy`; the **one-sided
wall-shear route is first order** and is computed too, **REPORTED and never
graded**.

**BAND GROUND — A MEASURED PRECEDENT, NOT OPTIMISM.** T1c graded the same three
quantities, on the same solver, at the same `Re` and `Pr`, and its fine level
carried **51 cells across the pipe radius** against this ladder's **40 across the
half-gap**. Scaling T1c's *measured* fine-level deviations by the second-order
factor `(51/40)² = 1.626`:

| row | T1c measured at its fine level | scaled to this ladder |
|---|---|---|
| `f·Re` | −1.92e-04 (63.98771 vs 64, `T1c_RESULTS.md:15-17`) | **−3.12e-04** |
| `Nu` uniform `q"` | +3.81e-04 (4.365298 vs 48/11, `:15`) | **+6.19e-04** |
| `Nu` uniform `T_s` | **+8.65e-04 — the row that GATE FAILED** (`:14`) | **+1.41e-03** |

**G3's band is armed from a failure, not from a hope.** Its ±3.5e-03 is 2.5×
the deviation T1c actually measured on the row it could not pass. If T19's fine
level lands nearer +8.65e-04 than +1.41e-03, it still PASSES, and that would say
the extra transverse resolution T1c had was not what mattered.

*The READER component is computed separately and exactly*, by applying this
comparator's own station reader to the exact fully developed profiles at cell
centres — **it is contained in the measured totals above rather than added to
them**:

| level | `Nu` uniform `q"` reader | `Nu` uniform `T_s` reader |
|---|---|---|
| `c` (ny=20) | +1.1204e-03 | +1.1898e-03 |
| `m` (ny=40) | +2.9636e-04 | +3.0506e-04 |
| `f` (ny=80) | **+7.6101e-05** | **+7.7200e-05** |

**Every band discriminates the ladder.** Each is cleared by the fine level by
about 2.5× and **failed by the medium level** (predicted −1.25e-03 / +2.5e-03 /
+5.6e-03) and by the coarse level.

**Gate order** (`apply_gate`, the only verdict-writing function): (1) any level
failing C_PLATEAU, C_SYM, C_MASS or C_ID → NOT A RESULT on every row; (2) triple
not CONVERGING → NOT A RESULT with `p` printed and GCI REFUSED; (3) CONVERGING →
PASS / GATE FAIL with GCI at `Fs` = 1.25. One way only.

**THE FINE VALUE IS GRADED, NEVER THE RICHARDSON EXTRAPOLATE.**

| control | what | floor | on failure |
|---|---|---|---|
| **C_PLATEAU** | each graded quantity recomputed at the PREVIOUS write (28 000) must have moved no more than the floor by the last write (30 000) | 1e-06 | gate (1) |
| **C_SYM** | no symmetry plane is imposed, so mid-plane symmetry is a witness: max \|T_j − T_(ny−1−j)\| and the same for `u` | 1e-06 K / 1e-09 m/s | gate (1) |
| **C_MASS** | the bulk velocity read at the station equals the registered `U0` | 1e-06 rel. | gate (1) |
| **C_ID** | `beta = 0` makes the arms hydrodynamically identical: `f·Re` from `P_Ts_*` and `P_q_*` must agree | 1e-06 rel. | gate (1) |
| C_REF | §1 in full, including the `s` = 1 cross-check to 1e-07 | — | exit 2 |
| C_PZ | planted-zero control on two readers (§4) | — | exit 2 |
| C_PROV | `check_case_provenance.py` rc = 0 on every built case | — | build refuses |
| completion | `mark_done_t19.py`, rule 4 in full including the age guard | — | NOT DONE → the grader refuses |

**AN ABSOLUTE RESIDUAL FLOOR IS DELIBERATELY NOT THE GATE, and the reason is on
the record.** T1c ran this solver for these 30 000 iterations and *"the solver's
own residualControl never tripped on any of the six cases and the offending
case's T residual was an unremarkable 4e-05, so this was caught by comparing
written fields, not by reading residuals"* (`build_t1c.py:57-63`). Gating on a
residual T1c never reached would manufacture a NOT A RESULT out of a healthy run
— the T3 failure shape. The residuals **are** read and are **REPORTED** beside
the verdict; the gate is C_PLATEAU, which is the check that actually caught
T1c's iteration-count defect.

**THE PER-RUNG FIELD TUPLE, CHECKED AGAINST THE CLOSURE THIS RUNG REGISTERS.**
The registered closure is **`simulationType laminar`**, which instantiates no
turbulence model and writes **no `nut`, no `k`, no `omega`, no `epsilon`**. The
tuple is therefore **`('T', 'U', 'p_rgh', 'alphat')`** — the four fields in
`0.orig` and the four the solver writes at `endTime`, verified against T1c's own
completed run, whose `30000/` directory holds `T`, `U`, `alphat`, `p_rgh` (plus
`p` and `phi`, which are derived and are **not** registered as conjuncts).
**T1b's thermal-family tuple `T U p_rgh alphat nut k omega` would make
completion IMPOSSIBLE here** — the exact defect that cost K0d its whole 829
core-minute rung. **This check was performed for this rung explicitly and is
recorded as performed.**

## 4. The planted-zero control — rule 3, sized per reader (L-340)

Two readers on the fine `q` case, both arms, on a scratch copy that must not
resolve inside the case tree; negative arm exactly 0.0 on identical bytes;
`PLANT` = 1.234e-03 imported from `scripts/roache_triple.py`.

**THE NUSSELT PLANT IS ONE CELL AND NOT THE WHOLE COLUMN, FOR A MEASURED
REASON.** `Nu` is built from `(T_wall - T_bulk)`, so a **uniform** plant across
the station column shifts the wall value and the bulk mean by the same amount
and is **invisible by construction** — driven, and it moved the read by
**1.9e-13**, i.e. round-off. The plant therefore goes into the **single
near-wall cell** of the downstream station column, located structurally by
index, where it moves the read by **2.09e-03** on a `Nu` of 8.24. The `f·Re`
reader takes a plant into `p_rgh` across that column and moves by 2.81e+03.

**THE SIZING RULE IS RESTATED RATHER THAN INHERITED.** T14's rule *"the read
must move by at least 0.1 × the plant"* transfers only when the read carries the
plant's units. These readers return a Nusselt number and `f·Re` while the plant
is a temperature or a kinematic pressure, so the transferable requirement — and
the one registered — is that the **registered plant must be VISIBLE** (a
non-zero move) and the **demonstrated detection floor must be at or below it**.
Both refusals are coded and both fire.

## 5. Instruments — L-332, and their measured selftest state

| instrument | result |
|---|---|
| `exact_t19.py` | **PASS (0 failed)** — profile ODE, normalisation control, ODE-mesh ratio 4.000, the three `s` = 1 cross-checks against T1c, plate `f·Re` exactly 96, plate `Nu_H` vs 140/17 to 1.0e-08, two planted-mutation refusals (1 % and 1e-06), AST 0 |
| `build_t19.py` | **PASS (0 failed)** — `r` = 2 in both directions and the station on a cell face at every level; a level pair sharing `ny` REFUSED; both arms write their wall condition on BOTH walls; `0.orig` holds exactly {U, p_rgh, T, alphat}; `check_case_provenance.py` rc = 0; AST 0 |
| `analyse_t19.py` | **PASS (0 failed)** — floors import; the full rule-5 ladder at the floors; **VALUE CONTROL** (the exact fully developed profiles on the registered ladder grade PASS ×3 with `p` = 2.000 / 1.903 / 1.957 and fine deviations +1.562e-04 / +7.610e-05 / +7.721e-05, matching the computed reader components); C_PLATEAU broken → NOT A RESULT ×3; C_SYM broken → NOT A RESULT ×3; C_MASS broken → NOT A RESULT ×3; `f·Re` perturbation 30/ny² → GATE FAIL; live tree without DONE refused; both planted controls PASS; AST 0 |
| `mark_done_t19.py` | **PASS (0 failed)** — 10 forged clauses of rule 4 against the **four-field** tuple |

**0 `ast.Assert` in every instrument**; every refusal is `sys.exit(2)`.

**TWO DEFECTS WERE FOUND BY DRIVING THESE SELFTESTS AND ARE RECORDED RATHER THAN
QUIETLY FIXED**: (i) the invisible whole-column Nusselt plant above; (ii) an
earlier C_MASS floor that was measuring the *forge's* midpoint-quadrature error
rather than the solver's mass conservation — a real solve conserves the discrete
flux exactly, so the forge, not the floor, was wrong.

**COMPARATOR STATUS — PROPOSED, NOT YET DIFF-READ.** The supervisor's §3 check 1
has not happened. The instruments are frozen by sha256 and git blob in §9;
`verification/runs/T-family/T19_runs/T19_INSTRUMENT_DIFFS.txt` carries the
unified diff of `mark_done_t19.py` and `run_one_t19.sh` against their T14
parents and names `exact_t19.py`, `build_t19.py` and `analyse_t19.py` as new
files with no parent to diff against. **No launch before that read.**

## 6. Predictions — registered before compute, and every one can lose

- **P1.** G1, G2, G3 all **PASS** at −3.12e-04 / +6.19e-04 / +1.41e-03. *Can
  lose*, and **G3 is the likeliest to**: its prediction is a scaled version of
  the only row in T1c that GATE FAILED.
- **P2.** All three triples CONVERGING with `p` in **[1.6, 2.4]**.
- **P3.** C_ID holds at better than **1e-12**, not merely better than its 1e-06
  floor: with `beta = 0` the two arms should produce bit-identical velocity and
  pressure fields. If they differ above round-off, something in the registered
  configuration couples them and this registration is wrong about the solver.
- **P4.** The wall-to-wall Nusselt asymmetry (REPORTED, never gated) is below
  1e-08 relative on every level.
- **P5.** The REPORTED first-order wall-shear route for `f·Re` misses 96 by
  roughly `1/(2 ny)` — about 2.5 % at ny = 20 and 0.6 % at ny = 80 — while the
  GRADED pressure route is second order. Nothing is gated on it.

**If a prediction loses it is reported as wrong.**

## 7. Cost — rule 12

**Rate: MEASURED, ON THE SAME SOLVER — and this is the strongest of the three
rates in today's registration set.** Taken from T1c's own completed runs at HEAD:

| case | cells | iterations | `ExecutionTime` | rate (core-s per cell-iteration) |
|---|---:|---:|---:|---:|
| `T1_runs/L_q_c` | 4 000 | 30 000 | 294.89 s | 2.457e-06 |
| `T1_runs/L_q_m` | 10 240 | 30 000 | 809.07 s | 2.633e-06 |
| `T1_runs/L_q_f` | 26 112 | 30 000 | 3 162.26 s | 4.037e-06 |
| `T1_runs/L_Ts_f` | 26 112 | 30 000 | 3 176.51 s | 4.055e-06 |

Same solver (`buoyantBoussinesqSimpleFoam`), same closure (laminar), same
schemes family, same iteration count, same box, serial. **The rate RISES with
mesh size**, so this registration uses the size-matched value at each level
rather than a single number: 2.46e-06 at 2 400 cells, 2.63e-06 at 9 600,
4.06e-06 at 38 400.

**MISPREDICTION RISK, NAMED.** The fine level is 38 400 cells against the 26 112
the top rate was measured on, so the borrow crosses a **1.47× mesh jump in the
direction where the rate has been observed to rise**. A rate borrowed across a
mesh jump made T1b L4 miss by 31.4 %; the same shape is possible here and the
expected direction is **under-prediction**. It is **not** borrowed across a
solver family — the failure shape of carrying a transient PIMPLE rate into a
steady SIMPLE run does not apply, because the case the rate was measured on **is**
a steady SIMPLE-family laminar forced-convection run.

| case | cells | **POINT core-min** | **cap core-min** | `timeout` (s) | ranks |
|---|---:|---:|---:|---:|---:|
| `P_q_c` / `P_Ts_c` | 2 400 | 2.952 each | **12** each | 720 | 1 |
| `P_q_m` / `P_Ts_m` | 9 600 | 12.624 each | **50** each | 3 000 | 1 |
| `P_q_f` / `P_Ts_f` | 38 400 | 77.952 each | **250** each | 15 000 | 1 |
| **total (6 cases)** | | **187.06** | **624** | | |

POINT 187.06 core-min = 3.118 core-h = **$0.1599 derived**; CAP 624 core-min =
10.4 core-h = **$0.5335 derived**, at $0.0513/core-h — **derived, not measured;
reported-by-owner**. **An overrun stops the run.** A `docs/COST_CALIBRATION.md`
row is owed at completion, per level.

**A LONG RUN, DECLARED IN ADVANCE.** The two fine cases are predicted at about
**4 680 wall seconds each**, above the 3 600 wall-second marker rule 12 uses to
flag a stalled row. **They are not stalls**: the length is predicted here, before
compute, and follows from 38 400 cells × 30 000 SIMPLE iterations at a measured
rate. A spend report on this rung must not classify those two rows as stalls on
the wall-clock marker alone.

## 8. The launcher

`run_one_t19.sh` is `run_one_t14.sh` with the rung name, case set, solver and
field set changed: rc captured in the wrapper, `capped` as an independent expiry
witness, cap read from `T19_registered.json`, existing STATUS refused,
regex-fullmatch time-dir guard, lineage-aware foreign-process guard
(`9fa66065`), **all four `0.orig` fields required and `0/T` touched LAST** (the
age-guard datum), `exit "$RC"`, `--no-detach` as the queue mode.

**THE LAUNCHER HAS NOT BEEN DRIVEN — ARM A is UNDRIVEN**; the lane was
instructed to launch no solver. `bash -n` passes.

**THIS DOCUMENT DOES NOT AUTHORISE A LAUNCH.** Nothing has been placed in
`verification/queue/heat-transfer/`, which is a launch button on a one-minute
cron tick with `host` defaulting to this box and a validator that ignores
unrecognised keys, so no annotation makes an entry inert. **Dropping is the
supervisor's, after his own check 4.**

## 9. The freeze set

Committed **in the same commit as this document**.

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T19_runs/exact_t19.py` | `aeaae65c9e849c8a` | `053e2b50ee1d7526eb5b32a61ec53fdf1b49b014` | 317 |
| `verification/runs/T-family/T19_runs/build_t19.py` | `e27c1f02b52da46c` | `d28e32a379afdda9f8c23be173953106f1609785` | 349 |
| `verification/runs/T-family/T19_runs/analyse_t19.py` | `c2d8120ff510b1c4` | `0bafecd0a4bece177d2735fd41cb044b47aa2fba` | 721 |
| `verification/runs/T-family/T19_runs/mark_done_t19.py` | `a4dee8b3eb2e1af2` | `13117be1af47e0153877f98e1b93feb339f217b2` | 224 |
| `verification/runs/T-family/T19_runs/run_one_t19.sh` | `e0c0bc1558916611` | `21c774c0b10776a0f0c7236c8215b9c4a68ac76b` | 193 |
| `verification/runs/T-family/T19_runs/T19_registered.json` | `84b3652a5187f04e` | `d63e8a4bf5ef8b3a5982940b044b08c75d9b4da0` | 152 |

Case inputs for the six cases (`0.orig/`, `constant/` **less `polyMesh`**,
`system/`, `BUILD.txt`, `CASE.txt`, build logs) are committed alongside; the
`polyMesh` directories are regenerated by `build_t19.py` and stay out of git.

## 10. What this document does not do

It does not modify any frozen file of another rung — in particular it does not
touch T1c's frozen comparator or its registered numbers, which it only cites and
cross-checks against; it does not authorise a launch and **enqueueing is not
authorisation**; it does not claim a turbulent, 3-D or conjugate capability; and
it authorises no send — **SUBMISSIONS REMAIN PARKED** (rule 7).
