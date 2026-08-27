# T17 — axisymmetric transient conduction in a finite cylinder (T11d), EXACT tier: pre-registration (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** Campaign T, rung **T17** — the rung that puts a graded number into the
capability grid's **`conduction × laminar (no flow) × axisym`** cell, which at
HEAD `cbcb1127` reads **`CAN NOT DO — not attempted`**
(`docs/capability/heat-transfer_GRID.md:48`). The grid's own convention places a
wedge in that row: *"a 1-D slab on an `empty`-patch mesh counts as 2D; a wedge
counts as axisym"* (`:7`). Verdict vocabulary fixed by `CLAUDE.md` rule 1.
Written by a heat-transfer lane; decisions `[lab-attributed]`. **Nothing here
has been sent, filed, submitted, uploaded, registered or posted outside this
box, and nothing in it may be (rule 7).**

## 0. What this rung is, what it is not, and what it can reach

**A quarter section of a solid cylinder of radius `R` and half-length `H`
(`R = H`)**: the axis at `r = 0`, a symmetry plane at `z = 0`, convective
(Robin) surfaces at `r = R` and `z = H`, uniform initial temperature, constant
properties, no generation. Solved with `laplacianFoam` on a **1-degree
OpenFOAM wedge**. It is the classic product solution — an infinite-cylinder
Bessel series times the T11 plane-wall series — and it is the family's first
axisymmetric case with no fluid in it.

> **T17 earns a verdict for CONDUCTION, no flow, AXISYMMETRIC, EXACT tier**, and
> nothing else.

**THE CEILING, STATED BEFORE THE RUN.** The reference is an exact series
solution, so under the upheld V/P ruling this rung scores **V and never P**: it
reaches **GATE REACHED at best and can NEVER reach HOLDS**.

**Condition at freeze** (rule 2), checked immediately before this commit:
`verification/runs/T-family/T17_runs/{T17_CY_c,T17_CY_m,T17_CY_f,T17_CY_f_CT}`
each hold `0.orig/`, `constant/`, `system/`, `BUILD.txt`, `CASE.txt`,
`log.blockMesh`, `log.checkMesh.build` — **no `0/`, no numeric time directory,
no `log.solve`, no `STATUS.*`, no `DONE.*`.** Zero core-minutes in the
registered tree, and **no scratch rate probe** (§7).

**`endTime` = 2.0 is 2.0 SECONDS of physical time, not an iteration count and
not a placeholder**: with `alpha` = 1e-5 m²/s and `R = H` = 0.01 m it is
`Fo = 0.20`, the Fourier number every reference and every band below is
evaluated at.

## 1. The analytic referent — derived, not transcribed (`exact_t17.py`)

    theta(r*, z*, Fo) = C(r*, Fo) P(z*, Fo)

    C(r*,Fo) = SUM_n D_n exp(-zeta_n^2 Fo) J0(zeta_n r*)      [infinite cylinder]
      zeta_n J1(zeta_n) = Bi J0(zeta_n)
      D_n = (2/zeta_n) J1(zeta_n) / (J0(zeta_n)^2 + J1(zeta_n)^2)
      C_mean = SUM_n D_n exp(-zeta_n^2 Fo) 2 J1(zeta_n)/zeta_n

    P(z*,Fo) = SUM_n A_n exp(-eta_n^2 Fo) cos(eta_n z*)       [plane wall, the T11 series]
      eta_n tan(eta_n) = Bi,  A_n = 4 sin(eta)/(2 eta + sin 2 eta)

**Bessel functions are computed inside the module, not imported.** `J0` and
`J1` come from their integral representations evaluated by the trapezoidal rule
on a periodic analytic integrand (512 points), which converges spectrally and
suffers none of the cancellation the power series suffers at large argument.
**No third-party dependency.**

**Verification, and it is heavier than T14's because the radial factor has no
registered lab number to check against:**

| check | measured |
|---|---|
| `J0`, `J1` satisfy Bessel's equation | worst residual < 1e-05 at six arguments |
| an **INDEPENDENT power-series** implementation of `J0`/`J1` | agrees to **6.66e-14** |
| `scipy.special` (REPORTED, never required) | agrees to **1.11e-16** |
| axisymmetric PDE residual, two stencil widths | **9.03e-06**, ratio **4.00** |
| axis regularity and the `z = 0` symmetry plane | 0.0 |
| both Robin surfaces | 1.2e-07 / 8.6e-08 |
| initial condition (Gibbs at the surfaces) | 3.9e-04 |
| 2r-weighted Simpson mean vs the closed form | **6.2e-13** |
| **the LUMPED LIMIT** `exp(-2 Bi Fo)` (cylinder) and `exp(-Bi Fo)` (wall) at `Bi` = 1e-4 | holds |
| **CROSS-CHECK** of the plane-wall factor against T11's registered `P_mean` 0.8515954577, `P(0)` 0.9506417785, `P(1)` 0.6433907845 | to 1e-09 |

**The lumped limit is the NORMALISATION control and it was earned the hard
way.** A uniform scaling of `D_n` or `A_n` satisfies the PDE and both Robin
conditions exactly and is invisible to Route B; the first version of this module
therefore let a 1 % mutation of `D_n` through. It was caught by driving it, and
the fix is that the limit check is now built with **the same mutation factors
as the series under test**. With that, `--selftest` REFUSES a 1 % `D_n`
mutation, a 1e-6 `D_n` mutation, a 1 % and a 1e-7 `A_n` mutation, and
eigenvalues taken from the wrong `Bi`. **SELFTEST PASS (0 failed).**

| quantity at `Fo` = 0.20, `Bi` = 1 | value |
|---|---|
| `C_mean` (cylinder factor) | 0.7185162587 |
| `P_mean` (wall factor) | 0.8515954577 — T11's registered number |
| `theta_mean` | **0.6118851822** |
| `theta(r*=0, z*=0)` | **0.8272239909** |
| `theta(r*=1, z*=0)` | **0.5420823169** |

Cylinder eigenvalues (`Bi` = 1): 1.25578371, 4.07947771, 7.15579917, 10.27098536.

## 2. The registered case (`build_t17.py`)

| quantity | value |
|---|---|
| `R` = `H` | 0.01 m each |
| `alpha` (`DT`) / `Bi` | 1.0e-05 m²/s / **1.0** in both directions |
| axis / `z = 0` | wedge patches / `zeroGradient` |
| `r = R`, `z = H` | `mixed`, **two different `valueFraction`s** (§2a) |
| initial / `T_inf` | 1 / 0, so `theta = T` |
| `endTime` / `deltaT` | **2.0 s physical (`Fo` = 0.20)** / **1.0e-04 s fixed on c/m/f** |
| schemes / solver | `Euler`, `Gauss linear corrected`; `laplacianFoam`, `PCG/DIC` 1e-12 |
| **wedge angle** | **1.0 degree TOTAL** (T1c used 5.0; §2b says why) |
| **ranks / decomposition seed** | **1 / `serial, 1 rank, no decomposition`** |

| level | `N` (both directions) | cells | `dr` = `dz` | `deltaT` | `f_axial` | `f_radial` |
|---|---:|---:|---:|---:|---:|---:|
| `T17_CY_c` | 50 | 2 500 | 2.0e-04 | 1e-04 | 9.90099010e-03 | 9.86761036e-03 |
| `T17_CY_m` | 100 | 10 000 | 1.0e-04 | 1e-04 | 4.97512438e-03 | 4.96664405e-03 |
| `T17_CY_f` | 200 | 40 000 | 5.0e-05 | 1e-04 | 2.49376559e-03 | 2.49159279e-03 |
| `T17_CY_f_CT` | 200 | 40 000 | 5.0e-05 | **5e-05** | 2.49376559e-03 | 2.49159279e-03 |

`r21 = r32 = 2` exactly. `checkMesh` on all four: **max aspect ratio 2.0000762,
non-orthogonality 0, max skewness 0.3332, Mesh OK** (`BUILD.txt`).

### 2a. Two `valueFraction`s, not one — and the radial cell centre is not `(j+½)dr`

OpenFOAM's `mixed` boundary reproduces `-k dT/dn = h(T_f - T_inf)` with
`f = Bi_d/(1 + Bi_d)`, `Bi_d = h·delta/k` and `delta` the **face-normal
cell-centre-to-face distance**. The two Robin surfaces have different `delta`:

- **axial** (`z = H`): the mesh is uniform in `z`, `delta = dz/2`, so
  `f_z = Bi/(Bi + 2N)` — the T11/T14 form.
- **radial** (`r = R`): the outermost cell's centre sits at the **annular-sector
  centroid** `r_c = (2/3)(r2³-r1³)/(r2²-r1²)`, **not** at `(N-½)dr`, and the
  face-normal distance carries the wedge factor: `delta_r = (R - r_c(N-1))cos(h)`.

**The sector centroid is exact for this mesh, not an approximation.** The wedge
cell's cross-section is a trapezoid (the outer face is a planar chord), and its
centroid is at exactly the annular-sector centroid — checked by hand at `i = 0`
and `i = 1` and encoded in both `build_t17.py` and, independently,
`analyse_t17.py`.

**C_GEOM verifies the geometry model against OpenFOAM's own numbers**, and it
discriminates: the exact identity *(volume-weighted mean of the radial cell
centre) = (2/3)R for every N* holds to 1e-17 for the sector centroid and is
**failed by the naive `(j+½)dr` by 6.67e-05 at N = 50** (driven). Against
`checkMesh`'s own three numbers on the built meshes:

| | checkMesh | this registration's analytic model |
|---|---|---|
| Total volume | 8.7262032205803e-09 | 8.7262032186418e-09 |
| Min volume (coarse) | 6.9809625764643e-14 | 6.9809625749134e-14 |
| Max volume (fine) | 4.3521938562647e-13 | 4.3521938552976e-13 |

— agreement 2.2e-10 relative, and the comparator refuses above 1e-08.

**THE RESIDUAL ASSUMPTION, NAMED.** The **per-cell centroid** is analytic and
has **not** been checked against OpenFOAM's own cell-centre field, because
writing cell centres would create a time directory and break the launch age
guard. The volume model that produces the centroid *is* checked, on three
independent numbers. This is the weakest assumption in this registration.

### 2b. The wedge-geometry bias — computed, registered, and made a prediction

**A planar-faced OpenFOAM wedge does not discretise the true axisymmetric
operator.** For a wedge of **half** angle `h`, every interior radial face has
area `2 r sin(h) dz` against the true `(2h) r dz`; every cell has volume
`sin(h)cos(h)(r2²-r1²)dz` against the true `h(r2²-r1²)dz`; and the face-normal
centre-to-centre distance carries a further `cos(h)`. The radial flux per unit
volume is therefore larger than the true one by **exactly `sec²(h)`**, for every
interior radial face and every `N`. The axial direction is unaffected.

**Consequence:** the wedge mesh converges, as `N → ∞`, to the solution with the
**radial Fourier number multiplied by `sec²(h)`**. This is a **fixed bias that
does not vanish under mesh refinement**. It does **not** enter the Roache triple
— a constant offset cancels from `e21` and `e32` and leaves `p` unchanged — but
it does enter every band.

At **1 degree total**, `sec²(h) - 1 = 7.6158e-05`, and its computed effect is
**−2.418e-05 (G1), −2.128e-05 (G2), −2.566e-05 (G3)**. At T1c's 5 degrees it
would be `1.905e-03` — larger than any band this rung could arm. That is why
this rung uses 1 degree.

**A FLAG, NOT A CLAIM.** The same derivation implies a 1.905e-03 radial-operator
bias in every 5-degree wedge case this family owns, **T1c included**. This
document does **not** claim that as a finding: the derivation is analytic and has
never been measured here, and T1c's own `f·Re` landed 0.019 % *low* against 64,
not 0.19 % high. **Prediction P5 below is the first measurement of it**, and if
P5 loses this paragraph is wrong and must be recorded as wrong.

## 3. Graded rows, bands, gate

Floors imported from `scripts/roache_triple.py`; the comparator defines none and
refuses if the registered copy differs (driven). `dim = 2`, `Fs` = 1.25.

| row | quantity | reference | band (rel.) | predicted fine deviation |
|---|---|---|---|---|
| **G1** | `theta_mean`, **VOLUME-weighted** over the wedge (weight `r2²-r1²` per radial cell) | 0.6118851822 | **±5.0e-05** | **−2.20e-05** |
| **G2** | `theta` at (`r*`,`z*`) = (0,0), separable linear extrapolation over the **non-uniform** radial stations | 0.8272239909 | **±3.0e-05** | **−5.9e-06** |
| **G3** | `theta` at (1,0), mid-plane of the curved Robin surface | 0.5420823169 | **±4.0e-05** | **−1.28e-05** |

A plain arithmetic mean would over-weight the axis and is **not** what the
reader does.

**BAND GROUND — THREE COMPONENTS, ALL COMPUTED BEFORE COMPUTE.**

*(a) READER*, from applying this comparator's own reader to the **exact field at
the registered cell stations**:

| level | G1 | G2 | G3 |
|---|---|---|---|
| `c` (N=50) | +2.513e-05 | +2.309e-04 | +1.909e-04 |
| `m` (N=100) | +6.282e-06 | +5.771e-05 | +4.743e-05 |
| `f` (N=200) | **+1.571e-06** | **+1.443e-05** | **+1.182e-05** |

*(b) WEDGE BIAS*, mesh-independent, from §2b: **−2.418e-05 / −2.128e-05 /
−2.566e-05** at every level.

*(c) FINITE VOLUME*, from T11's measured +4.4e-06 at `N` = 100 less this
module's computed +3.148e-06 midpoint-reader component, leaving +1.25e-06 per
factor, scaled by `(100/N)²` and doubled for the product: +1.0e-05 / +2.5e-06 /
+6.3e-07.

**What each band does, stated honestly.**

- **G1's ±5.0e-05 does NOT discriminate the ladder**, and the reason is
  registered rather than hidden: the mesh-independent wedge bias dominates the
  fine level, so no band both contains the fine value and excludes the coarse
  one. The mesh-convergence claim on this row is carried by the **Roache
  triple**, whose `p` a constant bias cannot move. What the band **does** test is
  the wedge-bias derivation itself — a bias 4× larger than derived puts the fine
  value outside.
- **G2's ±3.0e-05 DOES discriminate**: cleared by `f` (5.1×), **failed** by `m`
  (+4.13e-05) and by `c` (+2.19e-04).
- **G3's ±4.0e-05** is cleared by `f` (3.1×) and **failed by `c`** (+1.77e-04);
  `m` (+2.47e-05) sits inside it, so this row discriminates the coarse level only.

**Gate order** (`apply_gate`, the only verdict-writing function): (1) any level
failing C_CONV or W0 → NOT A RESULT on every row; (2) triple not CONVERGING →
NOT A RESULT with `p` printed and GCI REFUSED; (3) CONVERGING → PASS / GATE FAIL
with GCI at `Fs` = 1.25. One way only.

**THE FINE VALUE IS GRADED, NEVER THE RICHARDSON EXTRAPOLATE**, which is carried
as `richardson_REPORTED_ONLY` and is a function of no verdict this comparator
emits.

| control | what | on failure |
|---|---|---|
| C_CONV | every `T` solve's final residual ≤ 1e-10; an `End` line | gate (1) |
| W0 | **monotonicity**: worst INCREASE between radially or axially adjacent cells ≤ **1e-12** | gate (1) |
| C_GEOM | §2a, independent volume model + the (2/3)R identity | exit 2 |
| C_VF | two `valueFraction`s per level, axial derived and radial strictly below it | exit 2 |
| C_REF | §1 in full | exit 2 |
| C_PZ | planted-zero control per reader (§4) | exit 2 |
| separability defect | **REPORTED, never gated** — backward Euler on the coupled operator is not exactly separable, so a non-zero value is expected | never |
| C-T | `T17_CY_f_CT`, `deltaT` halved: movement of G1 REPORTED | never gated |
| completion | `mark_done_t17.py`, rule 4 in full including the age guard | NOT DONE → the grader refuses |

**W0 is monotonicity and not symmetry, and its weakness is stated.** T18 can use
exact permutation symmetry; here the `r` and `z` operators are not
interchangeable, so the structural witness is that the field decreases strictly
in both directions — true because the first radial eigenvalue 1.2558 lies below
the first zero of `J0` (2.4048) and the first axial eigenvalue 0.8603 below
`pi/2`. **This is a weaker witness than T18's and is named as such.**

**THE PER-RUNG FIELD TUPLE, CHECKED AGAINST THE REGISTERED CLOSURE.** The
closure is **NONE** (solid conduction, `laplacianFoam`); the solver writes `T`
alone and reads no `turbulenceProperties`; the tuple is **`('T',)`**. It is
**not** copied from T1b, whose `T U p_rgh alphat nut k omega` would make
completion impossible here — the K0d defect, 829 core-minutes. **The check was
performed for this rung explicitly.**

## 4. The planted-zero control — rule 3, sized per reader (L-340)

Copies the fine case to scratch (refuses if the copy resolves inside the case
tree); the negative arm must read exactly 0.0 on identical bytes; the positive
arm plants `PLANT` = 1.234e-03 **into all 40 000 cells for the volume-weighted
mean G1**, and into **one cell** for each point reader — index 0 (the axis cell
on the symmetry plane) for G2 and index `N_f-1` (the surface cell on the
symmetry plane) for G3, located structurally by index. A descending ladder
records the demonstrated detection floor; a read below 0.1 × plant refuses. A
**blind reader mutant** is driven and must be refused — it is.

## 5. Instruments — L-332, and their measured selftest state

| instrument | result |
|---|---|
| `exact_t17.py` | **PASS (0 failed)** — Route B, Bessel ODE, independent power series 6.66e-14, scipy 1.11e-16 (reported), lumped limit, T11 cross-check, four planted-mutation refusals, AST 0 |
| `build_t17.py` | **PASS (0 failed)** — L-341 guard; the (2/3)R identity at N = 7/50/200 and the naive centroid failing it by 6.67e-05; both `valueFraction`s written separately; two wedge patches; AST 0 |
| `analyse_t17.py` | **PASS (0 failed)** — floors import; the full rule-5 ladder at the floors; **VALUE CONTROL** on the registered ladder (the *predicted* field, analytic + `sec²(h)` radial bias, grades PASS ×3 with G1 `p` = 1.9998 and deviations −2.261e-05 / −6.855e-06 / −1.383e-05 against the predicted −2.200e-05 / −5.900e-06 / −1.280e-05); a **P5-LOSES CONTROL** driving the no-bias field through the whole grade and requiring PASS ×3; residual 1e-08 → NOT A RESULT ×3; monotonicity broken → NOT A RESULT ×3; deviation 6.0/N² → GATE FAIL; blind reader refused; live tree without DONE refused; AST 0 |
| `mark_done_t17.py` | **PASS (0 failed)** — 10 forged clauses of rule 4 |

**0 `ast.Assert` in every instrument**; every refusal is `sys.exit(2)`.

**COMPARATOR STATUS — PROPOSED, NOT YET DIFF-READ.** The supervisor's §3 check 1
has not happened. The instruments are frozen by sha256 and git blob in §9;
`verification/runs/T-family/T17_runs/T17_INSTRUMENT_DIFFS.txt` carries the
unified diff of each file against its T14 parent. **No launch before that read.**

## 6. Predictions — registered before compute, and every one can lose

- **P1.** G1, G2, G3 all **PASS** at −2.2e-05 / −5.9e-06 / −1.28e-05.
- **P2.** All three triples CONVERGING with `p` in **[1.8, 2.2]**. The wedge bias
  is mesh-independent and cancels from `e21`/`e32`, so it should not move `p`.
- **P3.** C-T moves G1 by **< 10 %** of its band (|move| < 5e-06 relative).
- **P4.** W0 = **0 exactly** on every level.
- **P5 — the interesting one.** Every fine-level deviation will be **NEGATIVE**:
  G1 near −2.2e-05 rather than the reader-only +1.6e-06, G2 near −5.9e-06 rather
  than +1.4e-05, G3 near −1.3e-05 rather than +1.2e-05. **If instead all three
  land near their reader-only values, the `sec²(h)` derivation in §2b is WRONG
  and this document says so in advance.** P5 losing does **not** by itself fail
  any row: the bands were sized to contain both outcomes, and the comparator's
  selftest carries a **P5-LOSES CONTROL** that drives the no-bias field through
  the whole grade and requires PASS ×3, so the gate cannot become a test of P5
  by the back door.

**If a prediction loses it is reported as wrong.**

## 7. Cost — rule 12

**Rate: 1.64e-07 core-s per cell-step. BORROWED, NOT MEASURED ON THIS RUNG** —
T14's rate, MEASURED 2026-08-26T21:03Z on a scratch copy of `T14_SQ_c`
(`laplacianFoam`, `Euler`, `Gauss linear corrected`, `PCG/DIC` 1e-12, serial,
2 500 cells, 2 000 steps, `ExecutionTime` 0.82 s).

**MISPREDICTION RISK, NAMED — and it is the smallest of the three registrations
landed today.** Same solver, same schemes, same linear solver, **same cell
counts (2 500 / 10 000 / 40 000, identical to T14's ladder)**, same transient
class. The only difference is mesh **topology**: a wedge whose cells carry two
zero-flux wedge faces and whose innermost cells are degenerate. **The borrow does
not cross a mesh jump or a dimension change** — the two failure shapes on record
(T1b L4's 31.4 % miss came from a rate borrowed across a mesh jump). Expected
miss: within a factor of 1.5 either way. No scratch probe was run because the
lane was instructed to launch no solver.

| case | cell-steps | **POINT core-min** | **cap core-min** | `timeout` (s) | ranks |
|---|---:|---:|---:|---:|---:|
| `T17_CY_c` | 5.0e07 | 0.137 | **2** | 120 | 1 |
| `T17_CY_m` | 2.0e08 | 0.547 | **8** | 480 | 1 |
| `T17_CY_f` | 8.0e08 | 2.187 | **30** | 1 800 | 1 |
| `T17_CY_f_CT` | 1.6e09 | 4.373 | **60** | 3 600 | 1 |
| **total** | | **7.244** | **100** | | |

POINT 7.244 core-min = **$0.0062 derived**; CAP 100 core-min = 1.667 core-h =
**$0.0855 derived**, at $0.0513/core-h — **derived, not measured;
reported-by-owner**. `timeout = cap × 60 / ranks`. **An overrun stops the run.**
A `docs/COST_CALIBRATION.md` row is owed at completion.

## 8. The launcher

`run_one_t17.sh` is `run_one_t14.sh` with the rung name, case set and
registered-JSON path changed; rc captured in the wrapper, `capped` as an
independent expiry witness, cap read from `T17_registered.json`, existing STATUS
refused, regex-fullmatch time-dir guard, lineage-aware foreign-process guard
(`9fa66065`), `0/T` touched last, `exit "$RC"`, `--no-detach` as the queue mode.

**THE LAUNCHER HAS NOT BEEN DRIVEN — ARM A is UNDRIVEN** and is named as such;
the lane was instructed to launch no solver. `bash -n` passes.

**THIS DOCUMENT DOES NOT AUTHORISE A LAUNCH.** Nothing has been placed in
`verification/queue/heat-transfer/`, which is a launch button on a one-minute
cron tick. **Dropping is the supervisor's, after his own check 4.**

## 9. The freeze set

Committed **in the same commit as this document**.

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T17_runs/exact_t17.py` | `29c5e0975885b26f` | `c07487e70909344accfc9ae6cb45bdb9143db99c` | 380 |
| `verification/runs/T-family/T17_runs/build_t17.py` | `d321df6e682b0016` | `5b76ef3bfea248f0b68a8554f4978aebe24d1f5d` | 319 |
| `verification/runs/T-family/T17_runs/analyse_t17.py` | `baa053900e58c2a5` | `9a5a409adbd307bb35dde4da0926029586dbfb66` | 646 |
| `verification/runs/T-family/T17_runs/mark_done_t17.py` | `adf2cbafd140804d` | `a9260b42ee997219017206bbeda638e5965dd3b1` | 219 |
| `verification/runs/T-family/T17_runs/run_one_t17.sh` | `adf7436a740a6e54` | `9afde791a795b2bffa09e87ba3b56ce53eaadf11` | 193 |
| `verification/runs/T-family/T17_runs/T17_registered.json` | `b77fd3acbd72d7a2` | `542e55b5f903c49e866a5d523d2f168f65628ef2` | 161 |

Case inputs for the four cases (`0.orig/`, `constant/` **less `polyMesh`**,
`system/`, `BUILD.txt`, `CASE.txt`, build logs) are committed alongside; the
`polyMesh` directories are regenerated by `build_t17.py` and stay out of git.

## 10. What this document does not do

It does not modify any frozen file of another rung; it does not authorise a
launch and **enqueueing is not authorisation**; it does not claim a capability,
a conjugate result, or a finding about T1c's wedge (§2b is a flag and a
prediction, not a finding); and it authorises no send — **SUBMISSIONS REMAIN
PARKED** (rule 7).
