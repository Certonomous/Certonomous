# E4a. fanPressure boundary-condition verification — exact operating-point class

**FROZEN-BY-COMMIT PENDING.** Written 2026-08-24T15:58:52Z (the stamp is `date -u` output
read in the same shell invocation as this file's finalisation; every stamp in
the freeze record is a command's own dated output, per the supervisor's
2026-08-23 timestamp discipline). **The supervisor commits this freeze BEFORE
any case is built or any solver runs.** The sha256 table in §5 is the on-disk
provisional reading (`E4_runs/FREEZE_CHECK.txt`, machine-captured); it becomes
a freeze only at that commit, per standing rule 2 and the T10a-R lesson
(its ADDENDUM 2: hashed-before-compute is weaker than committed-before-compute,
and this rung does not repeat that sequence). **At the freeze reading the run
tree `verification/runs/T-family/E4_runs/` contained ZERO case directories,
ZERO numeric time directories and ZERO DONE/STATUS markers** — the `find`
output with its own timestamps is in `FREEZE_CHECK.txt`, and `build_e4a.py`,
`launch_e4a.sh` and `run_one_e4a.sh` each **refuse** to act on a tree where a
case dir, marker or time dir already exists (rule 4's age guard carried over).

Authority: `EXPERTISE_CURRICULUM.md` **E4 stage (a)**, Amendment 1 (RATIFIED
2026-08-23): *fanPressure BC verification, EXACT operating-point class,
registered polynomial fan curve × exact laminar duct resistance, NO external
document.* **Stage (b) — the manufacturer datasheet — is on Sanaa's desk and
is not started, not referenced, not graded here.** Verdict vocabulary fixed by
the Verification Charter §2: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT
/ BLOCKED / PENDING.**

---

## 0. What this rung grades, and what it does not

It grades **one boundary condition** — `fanPressure` in ESI v2606 — against
two referents that cannot be wrong at this rung's scale: **the BC's own
registered curve** (an identity: the converged solution must satisfy the
equation the BC claims to impose) and **the exact laminar resistance of a
plane channel** (Poiseuille, with the entrance contribution bounded in §1.5
before any solve). Every verdict is PASS or GATE FAIL against a prediction
registered in this file with a numeric interval and a named falsifier. A row
whose grid triple is not `CONVERGING` is **NOT A RESULT** (rule 5), and no
GCI is quoted on non-monotone values.

It grades **no fan**. There is no manufacturer curve, no datasheet, no real
air mover anywhere in this rung; the polynomial is registered *because* its
intersection with Poiseuille is exact arithmetic. What a PASS buys is the
right to point a real fan curve at this BC in stage (b) knowing the BC itself
does what its source says.

---

## 1. The system

### 1.1 The BC, from source — recorded before any run, the T10a-R way

T10a-R twice caught a directive naming dictionary knobs that do not exist,
and recording the source reading in advance was the win. Same discipline here
(all paths under `/usr/lib/openfoam/openfoam2606/src/`):

| fact | file:line |
| --- | --- |
| `fanPressure` derives from `totalPressure` | `finiteVolume/.../derived/fanPressure/fanPressureFvPatchScalarField.H:126-131` |
| entries read: `direction` (required, in/out) | `fanPressureFvPatchScalarField.cxx:91` |
| `nonDimensional` (optional, default **false** — not used here) | `.cxx:92` |
| `fanCurve` as a **Function1** (required unless legacy `file`) | `.cxx:97-107` |
| `rpm`, `dm` read **only if** `nonDimensional` | `.cxx:109-113` |
| inherited from `totalPressure`: `p0` (required), `U`/`phi`/`rho` (default `U`/`phi`/`rho`), `psi` (default `none`), `gamma`, `value` | `totalPressureFvPatchScalarField.cxx:62-67` |
| `dir = 2*direction − 1` (`in` → −1) | `fanPressureFvPatchScalarField.cxx:144` |
| `volFlowRate = dir·gSum(phip)` on the volumetric branch — **one scalar for the whole patch**, never per-face | `.cxx:149-151` |
| `pdFan = fanCurve_->value(max(volFlowRate, 0))` — **clamped at zero** | `.cxx:189` |
| parent gets `p0() − dir·pdFan` as the total pressure | `.cxx:201-205` |
| incompressible branch (p in m²/s²): `p_f = p0p − 0.5·neg(phi_f)·|U_f|²` per face | `totalPressureFvPatchScalarField.cxx:191` |
| `neg(s) = (s<0) ? 1 : 0` | `OpenFOAM/primitives/Scalar/scalarImpl.H:262` |
| `polynomial` Function1: `y = Σ coeffᵢ·x^expᵢ`, inline `polynomial ( (c e) … )` | `OpenFOAM/primitives/functions/Function1/Polynomial/PolynomialEntry.H:33-53`, `.C:147-160` |

**What does NOT exist on this path, recorded now:** no static-vs-total
switch (the BC is a *total*-pressure condition by inheritance — the
"classic silent factor" the curriculum entry warns about is a convention
error a user makes, not a knob); no per-face curve evaluation; no
`operatingPoint`, `Q`, or `pressureDrop` entry; `file`/`outOfBounds` exist
only as the legacy tableFile spelling (`.cxx:96-103`, `.H:96-99`) and are
not used here. `nonDimensional` exists and is deliberately left at its
default false — the dimensional curve is the registered object.

So the BC's whole contract, in kinematic units, per fan-patch face at any
converged state:

```
Q  = −Σ phi_f            (direction "in": dir = −1)
p_f = p0_env + dp(max(Q,0)) − 0.5·neg(phi_f)·|U_f|²
```

That equation IS row I1.

### 1.2 Geometry: 2D planar channel, not the wedge — and why

The T1c wedge trap (its §2.2, docket D435) put the wall at `R·cos(2.5°)`;
here that constant would enter the resistance as `cos⁴(2.5°)` ≈ **−0.381 %**
— larger than every interval in this file, sitting in a geometric constant
rather than in physics. The planar channel has no such constant: blockMesh
represents the rectangle **exactly** (extents read back to 1e-12 by the
comparator), the exact resistance `R = 12νL/(h³t)` is elementary, and — the
deciding reason — **the discrete FV resistance of the channel is derivable in
closed form** (§1.5), which turns the mesh ladder's prediction from a hope
into arithmetic. Registered geometry: `L = 2.0 m` (x), `h = 0.01 m` (y),
`t = 0.001 m` (z, `empty`), `ν = 1.5e-5 m²/s`,
**`R = 12νL/(h³t) = 3.6e5 (m²/s²)/(m³/s)` exactly.**

### 1.3 Solver: simpleFoam, laminar — chosen for branch coverage

`simpleFoam`'s `p` carries dimensions m²/s² and its `phi` m³/s, which lands
exactly on the two source branches §1.1 cites: the incompressible branch of
`totalPressure` (`.cxx:191`) and the volumetric branch of `fanPressure`
(`.cxx:149-151`). `buoyantSimpleFoam` (even with g=0) would move both to the
dimensioned-pressure/mass-flux branches and drag `rho`/`psi` lookups into the
identity — a different verification target. No concrete reason for it was
found; simpleFoam stands.

### 1.4 Registered curves and their exact operating points

Fan curve class: `dp(Q) = p0f − k2·Q²` (m²/s²; Q in m³/s), inlet patch
`direction in`, outlet `fixedValue p = 0`. Operating point:
`k2·Q² + R·Q − (p0_env + p0f) = 0`. The constants are chosen so the
discriminant is a **perfect square** and the exact point is a round float:

| curve | p0_env | dp(Q) | discriminant | exact Q* | U_m | Re_h |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| **A** (F_c/F_m/F_f) | 0 | `0.081 − 1.2e12·Q²` | `(3.6e5)² + 4·1.2e12·0.081 = (7.2e5)²` | **1.5e-7 m³/s** | 0.015 m/s | 10 |
| **B** (S_f) | 0 | `0.048 − 1.2e12·Q²` | `(3.6e5)² + 4·1.2e12·0.048 = (6.0e5)²` | **1.0e-7 m³/s** | 0.010 m/s | 6.67 |
| **NULL** (N_f) | 0.054 | `0` (polynomial `((0 0))`) | — | `0.054/3.6e5` = **1.5e-7 m³/s** | 0.015 m/s | 10 |

Worked for A: `Q* = (−3.6e5 + 7.2e5)/(2·1.2e12) = 3.6e5/2.4e12 = 1.5e-7`;
check `dp(1.5e-7) = 0.081 − 0.027 = 0.054 = R·Q*`. The NULL case reaches the
**same** exact operating point with the fan contribution removed — the flow
is then driven by the environmental total pressure alone, which is what makes
it the fan-term null: at identical Q*, curve A supplies 0.054 of drive
through `dp(Q)` where NULL supplies it through `p0`, and their registered
error terms differ **by derivation** (§1.5), which N1 tests.

At the operating point the fan-curve slope is `−2k2Q* = −3.6e5` for A —
equal in magnitude to R — so neither the curve nor the duct dominates the
intersection: the BC's feedback loop (flux → curve → pressure → flux) is
genuinely exercised.

### 1.5 The two error terms, derived and bounded BEFORE any solve

**(i) Wall-discretisation term, exact at leading order.** The FV plane
channel with linear schemes: interior second differences are exact on a
quadratic profile; the wall face's one-sided `snGrad` over Δ/2 is not.
Solving the discrete system exactly (interior `u_{j−1}−2u_j+u_{j+1} = −s`,
wall cells `u_2−3u_1 = −s`), the discrete mean velocity at fixed gradient is

```
mean_disc = mean_exact · (1 + 2/Ny²)
```

— the discrete channel carries MORE flow. This is not asserted: the
comparator's `--selftest` solves that system for Ny = 8, 12, 18 and verifies
`mean = (Ny²+2)/12` to 1e-9. At the operating point, `δR/R = −2/Ny²` maps to

```
dev(Q*) = + (2/Ny²) · R/(R + 2k2Q*)     = +1/Ny²   (curve A: factor 0.5)
                                         = +1.2/Ny² (curve B: factor 0.6)
                                         = +2/Ny²   (NULL:   factor 1.0)
```

Fine level Ny = 18: **+0.3086 % (A), +0.3704 % (B), +0.6173 % (NULL).**
Ladder levels A: +1.5625 % (8), +0.6944 % (12), +0.3086 % (18); the
entrance term below is level-independent to leading order, so it cancels in
the triple's differences: `e32/e21 = (1/64−1/144)/(1/144−1/324) = 2.2500`
exactly, **observed p = ln 2.25/ln 1.5 = 2.000** — row R1's prediction is
arithmetic, not optimism.

**(ii) Entrance + kinetic-energy term, bounded.** The BC makes
`p + ½|u|²` **exactly uniform** on inflow faces, so the mechanical-energy
influx is exactly `p_tot·Q` whatever the inlet profile. The balance to the
fixed-static outlet is then

```
p0_env + dp(Q) = R·Q + κ·(U_m²/2),   κ = α_out + κ_e
```

with `α_out = 54/35 = 1.5429` (plane-Poiseuille KE-flux factor, exact) and
`κ_e ≥ 0` the excess entrance dissipation. Registered: **κ_e ∈ [0, 1],
central 0.35** (hydrodynamic entrance length `0.05·Re_Dh·D_h = 0.02 m` = 1 %
of L, so the developed-outlet assumption is safe and κ_e of order a few
tenths generously covers plane-channel entrance data). Sensitivity:
`δQ = −κ·(U_m²/2)/(R + 2k2Q*)`, giving central (bounds):

| case | wall term | entrance term, κ ∈ [1.543, 2.543] | net central |
| --- | ---: | --- | ---: |
| F_f | +0.3086 % | −0.197 % [−0.265, −0.161] | **+0.111 %** |
| S_f | +0.3704 % | −0.158 % [−0.212, −0.129] | **+0.213 %** |
| N_f | +0.6173 % | −0.394 % [−0.530, −0.321] | **+0.223 %** |

The G-row intervals in §2 are these bounds widened by a registered margin
(±0.15 % fan cases, ±0.20 % null — double sensitivity) for unmodelled
x-discretisation and profile effects. **All of this is written while zero
cases exist; the arithmetic cannot have been trimmed to fit a number.**

---

## 2. Registered rows — prediction, interval, identity test, falsifier

Machine-readable in `E4_runs/E4a_registered.json`; applied by
`analyse_e4a.py` with no human step. `dev` = `100·(Q − Q_exact)/Q_exact`.

| row | case(s) | quantity | registered prediction | interval (PASS) | identity test (Charter §2a) | falsifier |
| --- | --- | --- | ---: | --- | --- | --- |
| **I1** | all 5 | max over fan-patch faces of \|p_f − (p0_env + dp(−Σφ) − ½·neg(φ_f)·\|U_f\|²)\| | **0** | `≤ 8.1e-8 m²/s²` | **THIS IS AN IDENTITY**: the registered polynomial evaluated at the measured patch flow rate vs the measured patch pressure, the BC's own §1.1 equation | any face over tolerance; a residual ~**1.125e-4** (= ½U_m²) names the static-vs-total convention error — 3 decades above the tolerance, unmissable |
| **I2** | all 5 | \|Q_in − Q_out\| / \|Q_in\| across fan patch vs outlet | **0** | `≤ 1e-4` | **IDENTITY**: mass conservation | over tolerance (leak or reader defect shows at O(1)) |
| **P1** | all 5 | fan-patch faces with φ ≥ 0 at endTime | **0** | `= 0` | precondition | any outflow face voids the analytic referent: G1/G2/N1/D1 → NOT A RESULT (I1/I2 still graded — `neg()` handles the branch) |
| **R1** | F_c/F_m/F_f | observed order p of the triple on Q*, r = 1.5 | **2.00** | `[1.6, 2.4]` | not an identity | outside → GATE FAIL; triple not CONVERGING → **NOT A RESULT**, values+orders printed, **no GCI quoted**; any level unconverged → NOT A RESULT (rule 5 order (1)) |
| **G1** | F_f | Q* vs exact 1.5e-7 | **1.500167e-7** (+0.111 %) | `[1.498350e-7, 1.504650e-7]` (dev [−0.11, +0.31] %) | not an identity — §1.5's two derived terms | outside the interval; graded independently of R1's state (its interval is analytic, not GCI-derived), requires F_f converged + P1 |
| **G2** | S_f | Q* vs exact 1.0e-7 (second registered curve, control) | **1.002130e-7** (+0.213 %) | `[0.999800e-7, 1.004000e-7]` (dev [−0.02, +0.40] %) | not an identity | outside; a G1-PASS with G2-FAIL says the machinery fits one curve rather than verifying the BC |
| **N1** | N_f | Q vs exact 1.5e-7 (zero-fan null: pressure-difference-driven alone) | **1.503345e-7** (+0.223 %) | `[1.498200e-7, 1.507500e-7]` (dev [−0.12, +0.50] %) | not an identity | outside; **structural registered prediction**: the null's wall term is 2× the fan case's because with no curve slope the §1.5 factor is 1 |
| **D1** | F triple | sign-corrected Richardson vs exact 1.5e-7 | **1.497045e-7** (−0.197 %) | dev `[−0.35, −0.08] %` | not an identity; a **registered prediction about a reported diagnostic** (T10aR RX5 class) — grades no case, not independent of the hypothesis | outside; in particular Richardson at ~0 dev falsifies the §1.5 entrance model low; NOT A RESULT if the triple is not CONVERGING |
| **Z1** | all 5 | planted-zero control on the comparator's p, U and phi patch readers | recovered change == `fl(old+plant) − old` **exactly** | exact-float rule, no tolerance | control (rule 3) | any mismatch is a comparator **REFUSAL (exit 2)**, never a graded row |

**Why I1's tolerance is 8.1e-8 and not 0.** The identity is exact in exact
arithmetic — it is the assignment the BC performs
(`fanPressureFvPatchScalarField.cxx:189-205` +
`totalPressureFvPatchScalarField.cxx:191`). Two floors keep the measured
residual off zero: (a) the BC's last `updateCoeffs` used the pre-correction
flux of the final iteration, while the comparator reads the corrected written
flux — bounded by the convergence gate below at ≲1e-11 relative once the last
two checkpoints are value-for-value identical at `writePrecision 12`; (b)
ascii rounding at 12 significant digits, ~1e-13 absolute. The registered
`1e-6 × 0.081 = 8.1e-8` sits ≥3 decades above both floors and 3 decades below
the convention-error signature ½U_m² = 1.125e-4 that this row exists to
catch. It is a floor, not a fudge: a residual between 1e-7 and 1e-4 is a
GATE FAIL that no reading of this paragraph can excuse. **I2's 1e-4** is
registered generous because OpenFOAM's residual normalisation is opaque from
outside and the defect the row exists to catch (patch leak, reader bug) is
O(1)-relative; the honest cost of the generosity is stated: a sub-1e-4
conservation defect is invisible to this row.

**Planted-zero (rule 3, T10aR §2.2 exact-float rule).** Plants
`+1.234e-3` (p), `+1.234e-3` (U_x), `+1.234e-9` (φ) into face 0 of a
**scratch copy** of the earlier checkpoint, reads back through the same
readers, and requires the recovered change to equal `fl(old+plant) − old`
exactly — not the plant, and never within a tolerance. No case tree is
written to. Runs for every case at every comparator invocation.

**Iterative convergence gate (T10aR §2.3 style).** **No `residualControl`
in any case (L-141).** A case is CONVERGED only if p, U and phi are
**value-for-value identical** between the last two written checkpoints
(`writeInterval 5000` strictly < `endTime 20000`, L-140 — four checkpoints,
`writePrecision 12` so the equality bites at ~1e-12 relative). An
unconverged level makes every row that needs it NOT A RESULT (rule 5 order
(1)); the triple is never formed over one.

**Completion (rule 4, strict).** `mark_done_e4a.py`: rc=0; `End` line; last
time == endTime; `p U phi` present at endTime; `ExecutionTime` count ==
endTime; every endTime field **newer than the case's own `0/U`** (the age
guard — `run_one_e4a.sh` re-copies `0/` from `0.orig` at the start of the
run allowed to answer). All five cases required; no optional case. The
comparator **refuses (exit 2)** any case without its DONE marker.

**Guards.** G1 atomic launch lock, G2 `/proc` cwd scan, G3 no stray numeric
time directory — carried verbatim from `run_one_t10aR.sh`/`launch_t10aR.sh`;
plus builder/launcher refusal on any pre-existing case dir, marker or time
dir (§5), and comparator mesh read-back (patch face counts vs registered
`ny`/`nx`; domain extents to 1e-12), refusal on mismatch.

---

## 3. Instruments — what is frozen, what is new

**Frozen, imported, never copied or edited:** `T1_runs/analyse_t1c.py` —
its `gci` (Fs = 1.25) is the triple grader, its sha256
(`60893b28e2…6ee7e6c5135`, matching the hash T10a-R recorded for the same
file) is printed at every comparator run, and the comparator **refuses** if
its `FS` or `R_REFINE` differ from the registered contract.

**Declared departure, registered here rather than discovered later:** the
frozen module's `R_REFINE` is **1.6**; this rung's ratio is **1.5**, because
integer cell counts across h = 0.01 m admit r = 1.5 exactly (8/12/18) while
r = 1.6 needs 25/40/64 — and at Ny = 64 the derived wall term (+0.049 %)
sits at the plateau floor, risking a floor-dominated OSCILLATORY triple on a
rung that is supposed to measure a clean p = 2. The comparator therefore
redirects `R_REFINE` to 1.5 **in-process only**, through a restoring context
manager (`with_ratio`, the T10a-R `in_tree` precedent); the frozen file on
disk is never touched and the selftest proves the restoration.

**The frozen `richardson` carries the sign defect** T9a §8.1 recorded
(`f_f + (f_m−f_f)/(r^p−1)`, toward coarse). As in T10a-R: a corrected form
is declared as a **new instrument**, both are printed side by side, no case
row grades on either, and D1 is a registered prediction about the corrected
diagnostic only.

**New instruments, declared:** the field readers (`patch_values`,
`internal_values`, `boundary_nfaces`), the identity evaluator
(`identity_I1`, a pure function so the selftest can mutate its inputs), the
exact-operating-point solver, the planted-zero planters, and the discrete
channel solver used only by the selftest to verify §1.5's law.

**`--selftest`: 38/38 at the freeze reading** (stamped inside
`FREEZE_CHECK.txt`; synthetic in-memory data, zero case trees), covering:
every verdict path reachable (PASS, GATE FAIL high and low, NOT A RESULT on
an OSCILLATORY triple **with no GCI key present**); rule 5's order (an
unconverged level forces NOT A RESULT over a CONVERGING triple — the gate
turns PASS into NOT A RESULT, never the reverse); the planted-zero
exact-float rule on all three readers plus the exactly-zero unplanted
control; **mutation controls through the file readers** — a corrupted patch
p value flips I1, a corrupted outlet φ flips I2; the identity's `neg()`
outflow branch; the three exact operating points to 1e-14; the discrete
`(N²+2)/12` law at all three ladder levels; corrected-vs-frozen Richardson
on a clean power law; `with_ratio` restoration; checkpoint equality breaking
on a 1e-12 perturbation; and that every registered interval contains its own
prediction.

---

## 4. Cost — measured basis, prediction, and the empty actuals column

Rate **$0.0513/core-h**, owner-stated 2026-08-21/22 (rule 12; the box cannot
read its own billing — every dollar below is **derived, not measured**).

**Measured basis, cited not re-run:** the T1c-class ladder replicates
`L_Ts_P_c/m/f` (`T1_runs/STATUS.L_Ts_P_*`, meshes from `build_t1c.LEVELS`
via `build_d_ts_p.py`, endTime 30000): 4 000 cells / 809 s, 10 240 / 2 221 s,
26 112 / 5 844 s → **6.7–7.5e-6 s per cell-iteration** (serial
buoyantBoussinesqSimpleFoam on the contended box). **7.5e-6 is the basis**,
conservative for a momentum-only solver.

| case | cells | iterations | predicted core-s | **actual core-s** |
| --- | ---: | ---: | ---: | :---: |
| F_c | 800 | 20 000 | 130 | *(empty — filled at completion)* |
| F_m | 1 800 | 20 000 | 280 | *(empty)* |
| F_f | 4 050 | 20 000 | 620 | *(empty)* |
| S_f | 4 050 | 20 000 | 620 | *(empty)* |
| N_f | 4 050 | 20 000 | 620 | *(empty)* |
| blockMesh + checkMesh ×5 | — | — | 15 | *(empty)* |
| **total** | | | **2 285 core-s = 38.1 core-min = 0.635 core-h ≈ $0.033** | *(empty)* |

**The actuals column is filled at process completion only, never at
registration** (Sanaa's 2026-08-23 estimate-vs-actual law, rule 12): the
completion report states actual core-minutes from the STATUS/`time -v`
records, the ratio actual/predicted with the gap attributed, and lands a row
in `docs/COST_CALIBRATION.md`. **10× stop-and-investigate threshold: 6.35
core-h (≈ $0.33)** for the rung; per case, any run exceeding 10× its
predicted wall is stopped and investigated, not waited out (a row over
3 600 wall s is a stall by rule 12 regardless). Serial, `nice 15`, one case
at a time; spine compute keeps priority. Total sits well under $1 and inside
the curriculum's ~$1–2 estimate for all of E4.

---

## 5. Freeze set — provisional until the supervisor's commit

`E4_runs/FREEZE_CHECK.txt` (machine-captured 2026-08-23T21:25:44Z, both
stamps inside it are `date -u` output from the capturing invocation) records:
**zero directories of any kind, zero numeric time directories, zero
DONE/STATUS markers** in the run tree, the selftest line `SELFTEST 38/38 OK`,
and this table:

| file | sha256 (provisional until commit) |
| --- | --- |
| `E4_runs/E4a_registered.json` | `bb363d0232683f50a8f75ecbd15aef436bd72762686764c56027aac6f0401b05` |
| `E4_runs/build_e4a.py` | `451eae3682bff7f89f31147c1d2d74fe1badc4c2af2c0e0f40e76ca665e46956` |
| **`E4_runs/analyse_e4a.py`** (the comparator — the only file that produces a graded number) | **`a9f31c3f569181f27b17bcaca318ce1f1a0a3f0e85e788a4214c8d8d5d63ff4b`** |
| `E4_runs/mark_done_e4a.py` | `b152ed0071bfe8cea060fc8164587ffeec7ca02ab0c6ce259565935d4b10fbe6` |
| `E4_runs/run_one_e4a.sh` | `226fd26b019a7fe73b559dda36451ca328ee371bcb1c8fb6b776d024f12ffe19` |
| `E4_runs/launch_e4a.sh` | `0e2b893fd134cba67975792d3defefb453ed929ca4d122f22022e4cad9c81274` |
| `T1_runs/analyse_t1c.py` (imported frozen) | `60893b28e284127f61b41842c520897a2202cb024d5a4d260272c6ee7e6c5135` |

**Order of operations, binding:** (1) the supervisor commits this file,
`FREEZE_CHECK.txt` and the six instruments (private-index protocol, rule 10)
and verifies the committed blobs hash identical to this table; (2) only then
`build_e4a.py` writes the five case dictionaries (its `verify()` refuses
unless the one-change-per-case structure holds: F_c/F_m differ from F_f only
in `blockMeshDict`; S_f/N_f only in `0.orig/p`); (3) only then
`launch_e4a.sh` runs cases, serially. The builder, launcher and runner each
refuse a tree where any case dir, marker or time dir already exists —
**nothing in this rung can run twice, and nothing can run first.** Amendments
before the commit are legal and must name the condition checked (the case
directories that do not exist); after first compute, gates are closed and
changes land only as dated addenda.

---

## 6. What this rung cannot see, whatever it returns

Written now, while zero numbers exist, so it cannot be trimmed to fit them.

* **Nothing about any real fan.** No datasheet, no digitised curve, no
  measurement uncertainty — stage (b)'s whole subject, on Sanaa's desk.
* **Nothing about `direction out`,** the outlet-fan configuration: only the
  `in` branch of `.cxx:144` is exercised. A defect specific to `dir = +1`
  is invisible here.
* **Nothing about the `nonDimensional` path** (`.cxx:109-113, 168-199`),
  the tableFile legacy path, or `outOfBounds` handling — the registered
  curve is an inline polynomial, always evaluated inside its valid range.
* **Nothing about the mass-flux branch** (`.cxx:153-157`) or compressible
  `totalPressure` branches — simpleFoam pins the volumetric/incompressible
  pair by construction (§1.3).
* **Nothing about the `max(Q,0)` clamp under reversed flow** — P1 predicts
  no outflow face, so the clamp is never armed at the operating point; a
  defect in the reversed-flow branch is invisible.
* **Nothing about MRF or actuation-disk fans** — E4's other half; different
  code entirely.
* **Nothing about turbulence.** Laminar by registration; a fan patch feeding
  a turbulence model's inlet quantities is unexamined.
* **The entrance term is bounded, not verified:** κ_e's [0, 1] band is a
  bound from theory, and only D1 probes it, weakly. A PASS does not validate
  entrance-region physics; the rung is designed so it does not need to.
* **I2's generosity** (1e-4) means sub-1e-4 conservation defects pass
  unseen, stated in §2.
* **A triple that goes non-monotone returns NOT A RESULT, not a diagnosis**
  — this rung has no arm for separating iteration floor from discretisation
  if that happens; T1c's §3 lesson (endTime, not residuals) is the designed
  mitigation, at 20 000 iterations against T1c's 30 000 for a stiffer
  problem.
