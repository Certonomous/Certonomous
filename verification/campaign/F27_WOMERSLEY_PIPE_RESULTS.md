# F27-WOMERSLEY-PIPE-3D — pulsatile (Womersley) laminar flow in a circular pipe, α = 4 (`pimpleFoam`, butterfly mesh, 4 ranks, r = 2 in h AND dt) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F27_WOMERSLEY_PIPE_PREREGISTRATION.md`
frozen at **`05ec72c41ee762b49c3dc1d25a6780689b9b9044`**. Amendment 1
(2026-08-27, **pre-compute**, run root verified ABSENT at 17:10:35Z by `ls -d` and
again by `run_f27.sh --preflight`) corrected a **mislabelled scratch cost** —
0.88 core-min on an ExecutionTime basis became 1.20 on the lab's ClockTime × ranks
basis — and moved **no gate, threshold, band, cap or label**: `BAND_FACTOR` stays
5.0, both bands stay, `CAP_CORE_MIN` stays 680, `cost_core_min_estimate` stays
456.74. The superseded sha `4bb0226d` is **struck, not rewritten**, and no run ever
cited it. **Capability cell claimed: 3D · unsteady · incompressible.**

Levels launched by the queue runner and completed 2026-08-28T07:54:50Z →
09:01:29Z with no agent attached. Graded at **zero new compute**, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F27_WOMERSLEY_PIPE/grade_f27.py --prereg-commit=05ec72c41ee762b49c3dc1d25a6780689b9b9044`
Record: `verification/runs/F27_WOMERSLEY_PIPE_runs/F27_GRADED.json` (**this grader
writes no `.out` file and none exists** — stated rather than implied). Gated by
`scripts/roache_triple.py::grade_ladder`, **one call node** (AST census: node at
line 985; 0 `assert` nodes across 5 files, planted assert seen).

---

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p | GCI | verdict |
|---|---|---|---|---|---|---|
| G-F27-1 `E2_velocity_locked_phase` | **90.7576155544706** | [6.052738753361828e−05, 1.513184688340457e−03] | **OSCILLATORY** (dim 3, r21 = r32 = 2.000, **monotone FALSE**) | **null** | **NONE — not quoted** | **NOT A RESULT** |
| G-F27-2 `Einf_axial_velocity_locked_phase` | **367.725138883767** | [1.1397841172247245e−04, 2.849460293061811e−03] | **OSCILLATORY** (dim 3, r21 = r32 = 2.000, **monotone FALSE**) | **null** | **NONE — not quoted** | **NOT A RESULT** |

**No GCI is quoted on either row, and that is the rule working, not an omission.**
Standing rule 5: *never quote a GCI when the three values are not monotone.* The
grader's `orders` field reads `[None]` on both rows and its `GCI_pct` is absent —
the classifier declined to extrapolate rather than producing a number a reader
could mistake for a bound.

**Rule 5 turned a GATE FAIL *into* NOT A RESULT — the only permitted direction.**
Both rows carry `band_verdict: "GATE FAIL"` in the JSON: read against the band
alone, 90.76 and 367.73 are outside [6.05e−05, 1.51e−03] and [1.14e−04, 2.85e−03]
by four to five orders of magnitude. That band reading is **not** the published
verdict. Rule 5's limb (1) is consulted first, the fine level is not plateaued, and
the row becomes **NOT A RESULT**. The gate can only turn a PASS or a GATE FAIL
*into* NOT A RESULT; **it can never move a verdict the other way**, and nothing in
this record should be read as a band claim.

Level values (from `<level>/processor*/5.25/U`, read by the frozen reader —
decomposed, never reconstructed):

| level | cells | nc × nr × nz | steps | dt | E2 | Einf |
|---|---|---|---|---|---|---|
| coarse | 3,840 | 8 × 8 × 12 | 672 | 0.0078125 | 7.663017112187748e−03 | 1.1740768658920181e−02 |
| medium | 30,720 | 16 × 16 × 24 | 1,344 | 0.00390625 | 2.0822348080188893e−03 | 6.395096173313534e−03 |
| fine | 245,760 | 32 × 32 × 48 | 2,688 | 0.001953125 | **90.7576155544706** | **367.725138883767** |

Coarse and medium behave exactly as registered: E2 falls 7.66e−03 → 2.08e−03, a
ratio of 3.68 on a doubling — second order, and both sit at or near the registered
model. **Then the fine level departs by four orders of magnitude.**

Registered prediction (prereg §6): both triples CONVERGING with fine values inside
their bands → PASS. **NOT MET.** `BAND_FACTOR = 5.0` (`:210-211`), bands at `:220`
and `:228`, built from the composite model's fine-level predictions 3.026369e−04
(E2) and 5.698921e−04 (Einf).

---

## 2. THE MECHANISM — and this is the centre of gravity of the record

### 2.1 Every level is iteratively CONVERGED. The run converged beautifully at every step and is wrong anyway.

The residual census is over **per-time-step final** p, Ux, Uy and Uz residuals,
across **all steps and all correctors**, at every level. Not one reading anywhere
in the ladder exceeded its tolerance:

| level | readings (p / Ux / Uy / Uz) | above tolerance | worst p (tol 1e−10) | worst Ux (tol 1e−12) | worst Uy | worst Uz | state |
|---|---|---|---|---|---|---|---|
| coarse | 2,688 / 672 / 672 / 672 | **0 / 0 / 0 / 0** | 9.99858484955e−11 | 9.99640133648e−13 | 9.97986081416e−13 | 9.99131967985e−13 | **CONVERGED** |
| medium | 5,376 / 1,344 / 1,344 / 1,344 | **0 / 0 / 0 / 0** | 9.99965839753e−11 | 9.99129449456e−13 | 9.99396933127e−13 | 9.67821162314e−13 | **CONVERGED** |
| fine | 10,752 / 2,688 / 2,688 / 2,688 | **0 / 0 / 0 / 0** | **9.99974121122e−11** | **9.99968831464e−13** | 9.99947765492e−13 | 9.98883187043e−13 | **CONVERGED** |

At the fine level that is **18,816 residual readings — 10,752 pressure and 2,688
each for Ux, Uy and Uz — every one of them under tolerance**, with the worst
pressure residual at 99.9974 % of its 1e−10 ceiling and the worst Ux at 99.9969 %
of its 1e−12 ceiling. The solver did exactly what it was asked to do at every one
of 2,688 time steps.

**And the answer is wrong by four orders of magnitude.** That is the finding worth
carrying out of this rung: *iterative convergence at every step is not evidence
that a time-marched solution is right.* A record that reported only "CONVERGED at
all levels" would have been true and useless.

### 2.2 What actually fails: the plateau limb, which here has TWO parts

This registration split the plateau class into two limbs and measured both at every
level (`plateau_note` in the JSON).

**PERIODICITY** — `||U(T_END) − U(T_END − PERIOD)||_2,V / U_REF ≤ 1e−06`, over
every cell, volume weighted:

| level | change | tolerance | state |
|---|---|---|---|
| coarse | 1.5866080939696518e−07 | 1e−06 | **PLATEAUED** |
| medium | 6.906199043296255e−08 | 1e−06 | **PLATEAUED** |
| fine | **87.34864765713063** | 1e−06 | **NOT_PERIODIC — eight orders of magnitude over** |

**UNIFORMITY** — `A_z` (each cell against its own z-column mean) and `A_theta`
(each cell against its image under the mesh's exact 90° rotation), both volume
weighted, each against `0.1 ×` **that level's own predicted E2**:

| level | A_z | A_theta | tolerance | state |
|---|---|---|---|---|
| coarse | 3.075453130820838e−14 | 2.4755621951622306e−12 | 4.732635985609876e−04 | **PLATEAUED** |
| medium | 1.6637854820592042e−13 | 3.7046208843968074e−12 | 1.2051669252831151e−04 | **PLATEAUED** |
| fine | **19.183691064991546** | **29.600928253380467** | 3.0263693766809143e−05 | **NOT_UNIFORM — six orders over** |

Both limbs fail at fine and only at fine. The grader's `why` on both rows reads
*"levels fine, fine/uniformity are not iteratively converged or not plateaued; no
grid claim can be made from this triple"*.

### 2.3 The REPORTED-NOT-GATED channels corroborate it, and carry verdict `null`

Four channels are registered **REPORTED-NOT-GATED** (prereg §6.2, `:230-248`): no
verdict is attached to any of them. They are reported here because they are the
diagnosis.

| channel | coarse | medium | fine | triple state | observed order | verdict |
|---|---|---|---|---|---|---|
| `R-F27-E_perp` spurious cross-flow | 4.375064497105305e−15 | 2.6516553604849212e−14 | **88.50989662476276** | **DIVERGENT** | −51.828 | **null** |
| `R-F27-A_z` axial non-uniformity | 3.075453130820838e−14 | 1.6637854820592042e−13 | **19.183691064991546** | **DIVERGENT** | −47.007 | **null** |
| `R-F27-A_theta` azimuthal non-uniformity | 2.4755621951622306e−12 | 3.7046208843968074e−12 | **29.600928253380467** | **DIVERGENT** | −44.453 | **null** |
| `R-F27-W` bulk mean axial velocity | 0.6425538204858712 | 0.642830934670182 | **0.5060060783172045** | **OSCILLATORY** | null | **null** |

`W` was moved to REPORTED-NOT-GATED **before compute and for a measured reason**:
a zero-compute coarse pilot found the registered model mis-predicting `W`'s error
by **sign and by 7.6×**, and L-345's rule is that a quantity the registered model
cannot predict is reported, not banded around a prediction already known to be
wrong. Its same-stencil references were pinned as numbers at registration
(0.64982005876099 / 0.644677639755022 / 0.643390292465464, CONVERGING at order
1.998) and the built meshes reproduce them to 3.3e−16.

**`A_z` and `A_theta` nonetheless DO bite** — the grader says so in its own
`why` field. They carry no verdict as *quantities*, and they re-enter rule 5
limb (1) as the **UNIFORMITY states** of §2.2. A channel can be ungated as a number
and load-bearing as a state, and this rung is the demonstration.

### 2.4 What is ESTABLISHED, and what is NOT

**ESTABLISHED, from the artefacts:** at the fine level the solution at `t = 5.25`
is **not on a periodic orbit** (it differs from itself one period earlier by 87.3
in units where the tolerance is 1e−06), and it is **neither axisymmetric nor
z-invariant** (A_z 19.18, A_theta 29.60, against a tolerance of 3.03e−05), while
**every solver residual at every one of 2,688 time steps is converged**. The
spurious cross-flow channel — identically zero for the exact solution — reads
88.51 where the two coarser levels read 4e−15 and 3e−14.

**NOT ESTABLISHED: why.** This record names no cause. It does not attribute the
fine-level behaviour to an instability, to the decomposition, to the scheme, to the
mesh, to the time step, or to anything else. **A mechanism would need work nobody
has done**, and the registered diffusion-number control says so in its own words
for the one correlate the registration did record: `Fo` rises 0.442 / 0.884 / 1.767
across the ladder against a registered ceiling of 5.0, with F21's diverging fine
level at 42.89 and F22's passing one at 0.59 recorded beside it —
`mechanism_claim: "NONE: Fo is the measured distinguishing group, not a
demonstrated cause"`. Naming a cause here would be exactly the kind of fluent
after-the-fact story the verdict vocabulary exists to prevent.

### 2.5 THE INSTRUMENT POINT, and it is the transferable one

**The uniformity limb was added to this registration BECAUSE of a different past
failure.** The grader's own `plateau_note` says it: uniformity *"is the instrument
that would have caught F21_WOMERSLEY's wall-localized mode directly"*. F21 failed
with a mode localised at the wall; the lab registered a limb designed to see that
class of defect; and here that limb caught **a different, unanticipated failure it
was not designed for**.

The counterfactual is worth stating precisely. Without the uniformity limb, the
periodicity limb alone still refuses this rung — so the verdict would be unchanged.
What would change is what the lab *knows*: the rung would read as a number outside
a band, with no statement about **what** is wrong with the field. With it, the
record can say the solution is neither periodic nor axisymmetric nor z-invariant,
and can point at the three ungated channels that agree. **An instrument built from
one past failure earned its keep on a failure nobody predicted.** That is an
argument for registering diagnostic limbs beyond the minimum the gate needs, and it
is the finding this rung contributes to the lab's method.

---

## 3. CONTROLS — 16 in the graded path, plus one on-disk plant per gate; ALL PASSED

**Planted-zero (rule 3), into the real fine-level artefacts through the real
readers** (`fine/processor*/5.25/U`):

- **G-F27-1** — planted **−1.1405586050727834e−05** into `e2_of`; read back
  identically to 17 digits.
- **G-F27-2** — planted **−7.75345066904265e−03** into `einf_of`; read back
  identically to 17 digits.

**The strongest control in this rung, and it should be read in full:
`PZ-F27-READERS`.** On the **exact** field every error channel returns **exactly
0.0** — E2, Einf, E_perp, A_z and A_theta all read `0.0` (the fifth reading, `W`
= 0.6512835589736095, is a bulk mean rather than an error norm and is not expected
to vanish). Four separate defects are then planted, and **each must be seen by its
OWN channel and by no other**:

| plant | E2 | Einf | E_perp | A_z | A_theta |
|---|---|---|---|---|---|
| radial | 5.794485946727744e−04 | 9.930555555555842e−04 | **0.0** | **0.0** | **0.0** |
| axial | 7.071067811865611e−04 | 7.071067811865962e−04 | **0.0** | 7.071067811865612e−04 | **0.0** |
| azimuthal | 7.07106781186556e−04 | 9.876883405961923e−04 | **0.0** | **0.0** | 1.000000000000012e−03 |
| cross-flow | 1.0e−03 | **0.0** | 1.0e−03 | **0.0** | **0.0** |

Every off-diagonal entry is an exact zero: **channel separation demonstrated, not
assumed.** The azimuthal plant is at **wavenumber 3 deliberately**, and the reason
is declared in the control itself: `A_theta` reads exactly zero on any
D4-invariant azimuthal mode (wavenumber 4k), because the mesh's own 90° symmetry
is blind to it. **A declared blind spot with a stated remedy** — that class of
error is carried in full by G-F27-1 and G-F27-2, which have no null space — is
worth more than an undeclared clean sweep.

The other graded-path controls, each passed: symbolic substitution into the
unsteady axisymmetric axial momentum equation (residual `0` symbolically,
2.78e−16 numerically, wall value 0.0, α = 4.0, ν = 0.39269908169872414) with a
**1.1λ plant non-zero**; Bessel evaluation cross-checked scipy vs mpmath to
4.01e−16 and against the `J0(i^{3/2})` form exactly, with a planted order shift
seen; constant-ratio refinement in `h`, `dt` and the model's own radial recipe
(all ratios 2.0, cell ratios 8.0), with `simpleGrading (1 1 1)` in every block at
every level so `MESH_STANDARD` §9.2's branch-flip hazard **cannot arise**; the
model second order (orders 1.973 E2, 1.850 W) and shown able to see planted wall
and axis stencil defects (0.743 and 0.138 against a clean 0.00473);
**`PZ-F27-L345`** the model's triples through the grading classifier with a
**DEGENERATE** positive control; **`PZ-F27-L346`** every floor derived from **this**
ladder's predicted fine error and **nothing inherited from a coarser ladder**, with
the measured transient decaying 8,866× over five periods; the `Fo` control of §2.4;
the same-stencil references pinned as numbers; the single `grade_ladder` call site;
solver dictionaries agreeing with the registration (ν, p_tol 1e−10, U_tol 1e−12,
endTime 5.25, `backward`, `Gauss linear corrected`, 1 non-orthogonal corrector,
cosine drive f = 1 A = 1 ẑ, `simple (1 1 4)`); the reader parsing **real
solver-written `U` on this box**; **`PZ-F27-PERIODICITY_AND_UNIFORMITY`** driven
both ways (identical fields → 0.0; a planted change read back to 3e−17 of its
expected value); **`PZ-F27-ITERATIVE`** flagging one bad p and one bad Uz reading;
and **`PZ-F27-L342`** infrastructure-vs-physics both ways **including the age
guard**, which was tripped by a stale endTime field.

**Gate demonstration — both gates driven inside AND outside**, re-executed at
grading time: `exact(T) + 0.0005231 ×` a smooth radial error field puts both inside
(3.026369376680809e−04 and 5.210904271202719e−04); `× 0.02093` puts both outside
(1.2105477506723656e−02 and 2.0843617084809828e−02).

---

## 4. FROZEN FILES — disk == blob at the pre-registration commit, checked by THIS LANE

**The F27 grader records the pre-registration sha but does not itself hash the
frozen files against it.** That check was therefore done by this lane,
`git hash-object <disk>` against `git rev-parse 05ec72c4:<path>`, over every path
the commit carries for this case plus the gating script — **18 of 18 SAME**:

| path | blob |
|---|---|
| `cases/F27_WOMERSLEY_PIPE/grade_f27.py` | `e3346159` |
| `cases/F27_WOMERSLEY_PIPE/exact_f27.py` | `2e2938a8` |
| `cases/F27_WOMERSLEY_PIPE/foam_io_f27.py` | `ec0de730` |
| `cases/F27_WOMERSLEY_PIPE/build_f27.py` | `0ce7475d` |
| `cases/F27_WOMERSLEY_PIPE/proj_f27.py` | `1ce87225` |
| `cases/F27_WOMERSLEY_PIPE/run_f27.sh` | `a0b5ae29` |
| `case/0/U.template`, `case/0/p.template` | `98486b05`, `6736dd40` |
| `case/constant/fvOptions`, `transportProperties`, `turbulenceProperties` | `fee69011`, `90da50e4`, `ba5bb3d1` |
| `case/system/blockMeshDict.template`, `controlDict.template`, `decomposeParDict`, `fvSchemes`, `fvSolution` | `c7186b97`, `831256c4`, `7f00b35f`, `03ab16ad`, `8dec7a60` |
| `scripts/roache_triple.py` | `78e56a3b` |
| `verification/campaign/F27_WOMERSLEY_PIPE_PREREGISTRATION.md` | `d5648b47` |

**One file differs and it is named rather than omitted:**
`cases/F27_WOMERSLEY_PIPE/queue_entry_F27_WOMERSLEY_PIPE.json`. Its blob at the
pre-registration commit still names the **struck** sha `4bb0226d`; the copy on disk
names `05ec72c4`, carries an explicit `superseded_prereg_commit` field recording the
strike, and is byte-identical to HEAD. Structural, not a defect — a queue entry is
re-issued **against** a freeze and so cannot sit inside the commit it names. It is
INFRASTRUCTURE by the grader's own `field_classes` and no verdict reads it.

---

## 5. RULE 4 — strict completion, re-read from the run root by this lane

| level | `RC.txt` | `End` lines | `Time =` lines | last time == endTime | fields at `5.25/` | field at `4.25/` (periodicity limb) | age guard (`0/U` → `processor0/5.25/U`) | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 672 == 5.25/0.0078125 | 5.25 == 5.25 | U p in all 4 processor dirs | present | 07:54:52.427 → 07:54:59.489 Z | 6 s / 6.40 s |
| medium | 0 | 1 | 1,344 == 5.25/0.00390625 | 5.25 == 5.25 | U p in all 4 processor dirs | present | 07:55:02.016 → 07:57:02.871 Z | 120 s / 119.87 s |
| fine | 0 | 1 | 2,688 == 5.25/0.001953125 | 5.25 == 5.25 | U p in all 4 processor dirs | present | 07:57:10.064 → 09:01:28.922 Z | 3,856 s / 3,855.13 s |

**All three levels are rule-4 COMPLETE.** The grader's own `completion()` agrees at
every level (`done: true`, with `0/C` cell centres and `0/V` cell volumes present as
this case's completion rule additionally requires). **The refusal in §1 is not a
completion failure** — the runs finished cleanly and wrote everything they were
asked to write.

**Decomposed, never reconstructed.** 4 ranks at every level, `simple (1 1 4)`,
axial bands, **the butterfly cross-section is never cut**; decomposition seed
`none`.

**Mesh admissibility** from each level's `MESH_LINE.txt`: max non-orthogonality
**28.586° / 36.159° / 40.423°** against the 70° gate, max skewness **0.964 / 0.980
/ 0.990** against 4, max aspect ratio 2.219 / 2.529 / 2.738 under the 1000
advisory; `simpleGrading (1 1 1)` read back from the **written** `blockMeshDict` in
all five blocks at all three levels; total mesh volume 3.1214 / 3.1365 / 3.1403
against the exact pipe volume π = 3.14159, converging as the inscribed polygon
refines. Non-orthogonality **rises** across the ladder and the registration
disclosed that in advance (§14 departure 7: increments shrinking geometrically to a
limit near 45.8°, well under the gate).

---

## 6. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted | **`cost_core_min_estimate` = 456.74 core-min** (coarse 0.563, medium 12.028, fine 444.145; 704,471,040 cell-steps), registered at prereg `:378`, table at `:371-376`. Registered cap **680** (`:619`, `:378-379`), = 1.489× the estimate |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` (4 ranks) | coarse 6 s → **0.4000**; medium 120 s → **8.0000**; fine 3,856 s → **257.0667**; **265.4667 core-min gross** |
| corroboration | the launcher's own tally (`cases/F27_WOMERSLEY_PIPE/launcher.queue.out`, *"Cumulative spend: 265.46666666666664 core-min of 680"*) and the grader's `cost_claim.core_min_claim` / `partial_sum_core_min` in `F27_GRADED.json` (`defects: []`) — **all three agree to every digit** |
| ExecutionTime basis, stated beside it | (6.40 + 119.87 + 3,855.13) × 4 ÷ 60 = **265.4267 core-min** |
| **the 3,600-second row, addressed rather than passed over** | the fine level ran **3,856 wall s**, above the charter §2 stall heuristic. It is **not a stall**: 2,688 `Time =` steps written, 660.6 million cell-steps, and **ExecutionTime / ClockTime = 3,855.13 / 3,856 = 0.99977** — the ranks delivered CPU for 99.98 % of that wall. A stall is a wall with no work behind it. **There is nothing to clean.** |
| actual cleaned | **265.4667 — cleaned == gross**, for the reason in the row above |
| waste, named separately | **0.000 core-min** (`COMPUTE_BUDGET_CHARTER.md` §6) — no stall, no kill, no re-run, no cap movement; the ladder ran once and was graded once. **The NOT A RESULT verdict is not waste**: the compute bought a registered reading, and the reading was refusal |
| scratch spend, disclosed separately and outside the cap | **6.733 core-min measured** (rate arms 0.267 / 1.333 / 3.933 and the coarse physics pilot 1.200), plus **~1.57 core-min estimated** for an overwritten 30-step probe and serial mesh work — grand total **≈ 8.3 core-min, of which 6.733 is measured** (prereg `:631-648`). None of it is charged against the cap and none of it is a result |
| quantisation | `ClockTime` is integer-second: ± 0.0333 core-min per level at 4 ranks. At the coarse level this is 8 % of the level's own figure, and it is why ExecutionTime (6.40 s) exceeds ClockTime (6 s) there |
| share of cap | **39.0 %** (265.4667 / 680); no overrun, cap never raised |
| dollars | 265.4667 / 60 = 4.4244 core-h × $0.0513/core-h = **$0.2270 — DERIVED, NOT MEASURED** (c7a.4xlarge, reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5). Registered: $0.39 at the estimate, $0.58 at the cap |
| **ratio actual/predicted** | **0.581** |

**Gap attribution — MISPREDICTION, and the registration predicted its own
direction in advance.** Prereg §8's caveat (a), at `:387-390`, written before the
run: the fine rate arm ran only 24 steps **from rest**, during the phase where the
pressure field changes fastest, so *"its iteration count is therefore likely an
**over**-estimate, making 456.74 conservative."* That is exactly what happened.

| level | registered rate (core-µs/cell-step) | **measured rate** | measured/registered |
|---|---|---|---|
| coarse | 13.09 | **9.301** | 0.711 |
| medium | 17.48 | **11.626** | 0.665 |
| fine | 40.34 | **23.348** | 0.579 |

All three measured rates come in **under** the registered ones, and the shortfall
**widens** with level — consistent with the caveat's own mechanism, since the
from-rest transient the rate arms measured is a larger fraction of a short arm than
of a full run, and the DIC-PCG pressure iteration count settles as the field does.
The measured per-level growth is **1.250×** and **2.008×**, against the registered
1.335× and 2.308×: the *shape* of the growth was read correctly and only the
*level* of the rate was high. A registration that says in advance which way its own
estimate is likely to be wrong, and is then right about it, is doing what a
cost basis is for.

**Contention: present in the box load, absent from the wall-versus-CPU reading.**
`box_before.txt` / `box_after.txt` record load1 **11.75 → 11.87 → 13.71 → 13.00 of
16 cores**, free cores 4.25 → 4.13 → 2.29 → 3.00, MemAvailable 28.1–29.7 GB, with
the probes explicitly labelled *"INFRASTRUCTURE observation only: the pre-spend
projector does NOT read it"*. ExecutionTime/ClockTime is **1.067 / 0.9989 /
0.99977**; the coarse figure above 1 is integer-second quantisation on a 6-second
run, not a measurement. §8's decision to apply **no contention multiplier** —
because the rate was itself measured under real contention at load 19.66 of 16 —
**held**.

**Carry forward.** A rate arm run **from rest** over a handful of steps
over-estimates a pulsatile `pimpleFoam` run's steady-state cost by roughly 1.7×,
and the error grows with level. Marginal differencing (first-to-last
`ExecutionTime` over the arm) removes *startup*, but it does not remove the
*transient*: those are two different things and this rung separates them.

**Estimate-versus-actual calibration lands as a row in `docs/COST_CALIBRATION.md`,
appended at the file's foot at commit time under its own append rules and the
rule-10 private-index protocol.**

---

## 7. WHAT THIS RUNG SETTLED, AND WHAT IT DID NOT

**Settled.** The capability cell **3D · unsteady · incompressible** is **not
claimed** by this rung. The registered ladder does not support a grid claim: both
rows are NOT A RESULT and no observed order or GCI exists to quote. The two coarser
levels behave as registered, and that fact carries no verdict of its own — rule 5
gates the triple, not a pair.

**Not settled, and named as such.** Why the fine level departs. Whether a different
time step, decomposition, corrector count or scheme would recover it. Whether the
`Fo` correlate (0.442 / 0.884 / 1.767, ceiling 5.0) is the relevant group — the
registration itself refuses to call it a mechanism, and this record holds to that.

**What a successor would need** is a registration matter, not a re-grade, and it
sits with the cfd supervisor: nothing in this record proposes one as done, and no
gate, band, threshold, cap or label of this frozen registration may move to
accommodate one (this case is **post-compute**).

---

## 8. BOOKKEEPING — L-342 infrastructure fields; none touches a verdict

- `cases/F27_WOMERSLEY_PIPE/STATUS.F27_WOMERSLEY_PIPE` reads `launcher_rc=0
  end=2026-08-28T09:01:29Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc`
  and was written by the queue runner. **The solver rc per level is `RC.txt` = 0 at
  all three**, cited in §5.
- The grader's `cost_claim` carries **`defects: []`**; the cost claim in §6 is not
  refused.
- **No foreign grade artefact** in the run root: `F27_GRADED.json` is the only
  non-level entry, written 2026-08-28T16:13Z.
- The frozen grader was run with plain `python3`, never `-O`.

## 9. NOT REGISTERED, NOT SENT

No re-grade of any row; no amendment to the frozen pre-registration (post-compute —
gates, thresholds, cap and labels are **closed**); no mechanism claim; no order
claim; no GCI. **Nothing is sent, filed, uploaded, registered, posted or submitted**
(rule 7). Field data stays on disk under
`verification/runs/F27_WOMERSLEY_PIPE_runs/` and is not committed.
