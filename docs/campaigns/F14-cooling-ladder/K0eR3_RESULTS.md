# K0eR3. Forced-convection flat plate, heated and cooled arms: results

Campaign F14, gate K0e. Solved 2026-09-04: the `D0` determinism twins at
01:43:16Z–01:44:43Z, then the two main arms `FP_T10` and `FP_T290` concurrently
at 01:54:27Z–02:30:57Z. Graded by **one** invocation of the pinned grader.

Pre-registration `K0eR3_PREREGISTRATION.md`, **frozen `3f33d815` before any
K0eR3 case directory existed**; its pins were cut by a dated pre-compute
addendum at **`52928b1d`**, which altered no gate, no threshold, no cap and no
label. The three pinned scripts landed at `106b7f06`. The grader
`scripts/analyse_k0er3.py` carries git blob SHA-1
`6d7b4d2c0825771a87edfda0cc9ba0279569ed1d`, and that value is printed by the
grader's own banner in the verdict artifact — `--expect-sha` and `--prereg` are
both required arguments, so the pin cannot be silently disarmed.

Run tree `verification/runs/F14-cooling-ladder/K0eR3_runs/`. Verdict artifact
`K0eR3_runs/K0eR3_GRADE_STDOUT.txt`, landed at commit `da03ec13` together with
`STATUS.FP_T10` and `STATUS.FP_T290`; `STATUS.D0_A` and `STATUS.D0_B` landed at
`bae21aa7`. The rule-12 calibration row is
`C-20260904T023833.148263Z-dfbdde5f` in `docs/COST_CALIBRATION.md`, landed at
`f3a838ec` and **not duplicated here**; §9 below restates its figures.

Four runs, all `rc=0`, `note=clean`, all `DONE` on every one of the six clauses
of standing rule 4, with clause 6 printing the number of fields it compared —
**7 fields per arm, never a comparison over an empty set.**

---

## 0. Verdict

# `PASS`

| row | status | measured |
| --- | --- | --- |
| **`M4b`** — same-solver momentum ULP distance, `FP_T10` (plate 310 K) vs `FP_T290` (plate 290 K) | **GATED, `PASS`** | 52,224 cells × 3 components; **0 components at non-zero ULP**; worst ULP distance **0** |
| **`Z1`** — wall heat flux from the production reader on a constructed exact uniform 300.0 K field | **GATED, `PASS`** | **0** of **208** plate faces at non-zero flux, at 0 ULP against `0.0`. **There is no tolerance constant in the comparator** |
| **`D0`** — determinism twin, refusal gate armed before the main arms | **`PASS`** | **0 ULP** over 156,672 components |
| **`P7`** — the one-line premise, blocking refusal | **`PASS`** | 23 files compared; **exactly 1** differing file (`0/T`); **exactly 1** differing line, at 1-based **39** — the line the registration records |
| `P1` / `P2` / `P3`, `Z2` / `Z3` | refusals, all cleared | §7 |
| `M1`, `M1b`, `M2`, `M3`, `M4`, `M5`, `D2` | **REPORTED, not gated** | §5, §6 |
| Standing rule 5 | **does not engage** | no grid triple exists; no GCI is computed, quoted or derivable (§1, B6) |

**What the `PASS` asserts, exactly:** `beta` and `g` were demonstrated neutral
against a 20 K odd-mode thermal perturbation in the installed binary, so a
Stanton error on this rung is attributable to the thermal closure alone.
**Attribution, not validation.** §1 states what it does not assert, and is
placed there deliberately.

---

## 1. WHAT THIS `PASS` DOES NOT MEAN

**This section sits immediately after the verdict because it is exactly as
load-bearing as the verdict.** Every item was registered before compute, in
`K0eR3_PREREGISTRATION.md` §2.1.3, §3, §5.4 and §10, and none is discharged by
anything measured here.

**It is not a validation of the thermal closure.** Equation (1) of Bahrami
(2005) is Colburn-type and sits in the family of the Reynolds and Von Karman
analogies. **The Reynolds analogy is close to what a constant-`Prt`
gradient-diffusion closure asserts**, so agreement between a `Prt = 0.85` RANS
solve and eq. (1) is **partly structural rather than evidential**. `Pr^-0.4`
against `Pr^-2/3` is the only genuinely testing part of that comparison, and at
`Pr = 0.71` that gap is small. This is §2.1.3's circularity caution and it is
undischarged.

**No `GATE FAIL` was reachable on the Stanton comparison.** No band is armed on
eq. (1), because none can be honestly derived from the source in hand: Bahrami
states uncertainties for Moretti & Kays's *experiment*, not for the
correlation, and `LITERATURE_CHARTER.md` §2 forbids a tier for "widely
reported". Setting the band at Bahrami's own "approximately 10 percent" for
two-equation models would have been setting the gate to what we expect to
achieve. **`M1` and `M1b` therefore cannot produce a `PASS` and cannot produce
a `GATE FAIL`, in either direction, on any number in §4 or §5.**

**The seven named blind spots B1–B7 stand undischarged.** They were registered
before the run, not discovered after it.

- **B1 — `M4b` on the pair `(−10, +10)` is BLIND to a leak that is EVEN in
  `(T − TRef)`.** Any coupling whose effect on `U` is an even function of
  `(T − TRef)` — a term in `(T − TRef)²`, in `|T − TRef|`, a transport property
  symmetric about `TRef` — produces identical `U` perturbations in both arms and
  **cancels exactly** in this difference. It is not detected, and a 0-ULP `M4b`
  says nothing about it. **K0eR2's asymmetric `(0, +10)` pair was NOT blind to
  that class.** The blindness was bought deliberately, in exchange for removing
  the degeneracy and doubling the odd-mode drive; the mitigation — that the only
  `T → U` route in the installed v2606 source is `rhok = 1 − beta·(T − TRef)`,
  which is linear and therefore odd — **is an argument about the source, not a
  measurement**, and the whole point of a gate is to catch a route nobody
  anticipated.
- **B2 — `M4b` is a difference test and is blind to a leak common to both
  arms.** A constant spurious body force or any `T`-independent defect cancels.
  This rung carries **no gated check on absolute momentum correctness** and
  claims none.
- **B3 — `Z1` cannot detect a spurious flux that requires a non-uniform
  near-wall `T` field to appear.** A wrong `alphat` wall value, a wrong
  face-to-cell distance, a wrong sign on one patch: none fires on an exactly
  uniform field. `Z1` tests the reader's null case, and that is all it tests.
- **B4 — `Z1`'s zero is a statement about the reader, the mesh and the flux
  formula, not about the solver.** The `dT = 0` solve is not performed at all,
  so nothing here shows that the solver, run at `dT = 0`, would hold `T` at 300.
- **B5 — `0` ULP is on the WRITTEN artifact at `writePrecision 10`.** It means
  the two fields agreed to at least the written precision and rounded
  identically; it does not prove agreement in the unwritten low-order bits.
  **The gate is a necessary condition, not a sufficient one.**
- **B6 — NO GRID TRIPLE EXISTS, so EVERY NUMBER IN THIS RECORD CARRIES NO
  DISCRETISATION BOUND AT ALL.** Two arms ran on one mesh of 52,224 cells.
  Standing rule 5 does not engage; **no GCI is computed, none is printed, and
  none is derivable from anything on this rung.** Every Stanton number, every
  `Cf`, every `Prt_eff` and every boundary-layer thickness below is a
  single-mesh number with an unbounded discretisation error. The grader prints
  this statement itself, in the artifact, rather than leaving it to a reader.
- **B7 — `D0` establishes determinism WITHIN this epoch and at 200 iterations
  only.** It cannot detect a nondeterminism that manifests only after long runs
  or only under a load pattern absent while it ran. It is a cheap decisive test
  for the *presence* of nondeterminism, not a proof of its absence at scale.

**And the rung is not the mixed-convection rung, says nothing about buoyant
flows, and grades nothing against the Moretti & Kays primary — which is NOT
OBTAINED.** Nothing here was sent, filed, uploaded, registered or posted;
submissions are PARKED (standing rule 7).

---

## 2. What K0eR3 measures — the geometry, the conditions, and the confound it breaks

Every graded thermal result this lab owns is a buoyant cavity in which the
momentum and thermal fields are **both wrong and coupled through buoyancy**, so
no error is attributable to either. `K0cR` is the proof: fixing the stress
closure moved velocity **19 points toward** experiment and wall heat flux
**30 points away**, in the same solves.

K0eR3 removes the coupling at source and then **measures that the removal
holds in the binary**. With `beta = 0` and `g = (0 0 0)` there is no
source-level route from `T` to `U`; `M4b` is the row that demonstrates it,
because without `M4b` the attribution is an assertion about a dictionary rather
than a measurement.

| item | value | source |
| --- | --- | --- |
| Case | the lab's TMR flat plate, `/home/ubuntu/certonomous-runs/tmr-flatplate-finer` | `K0eR3_PREREGISTRATION.md` §8.4 |
| Solver | `buoyantBoussinesqSimpleFoam`, OpenFOAM **v2606** | `STATUS.*` `solver_path` |
| Cells | **52 224**, one mesh | `log.checkMesh`, `constant/birth_certificate.json` |
| Max non-orthogonality | **0** — asserted by the grader before any wall gradient is read | same |
| Plate | `x = 0` to `2.0 m`, **208 wall faces**; `y+` 0.0592 to 0.2088, wall-resolved | `constant/polyMesh/boundary` |
| `U_inf`, `nu` | 1.0 m/s, 2e-07 m²/s → `Re_x` 0 to 1.0e7 | `0/U`, `constant/transportProperties` |
| `beta`, `g` | **0**, **(0 0 0)** — buoyancy removed twice, independently | `K0eR3_PREREGISTRATION.md` §8.5 |
| `TRef` = `T_inf`, `Pr`, `Prt` | 300 K, 0.71, 0.85 | same |
| `div(phi,T)` | `bounded Gauss limitedLinear 1` — the ladder's own scheme | same |
| `alphat` on the plate | `calculated`, value 0 — wall-resolved; an `alphatJayatillekeWallFunction` would impose a high-Re thermal law on a resolved wall and is deliberately not used | same |
| `endTime`, decomposition | **9000**, `startFrom 0`; **2 ranks copied from the momentum reference**, not re-derived | same |

**The two arms differ in one line and in nothing else.**

| arm | `T_wall` | `dT` | `Tw/T_inf` | role |
| --- | --- | --- | --- | --- |
| `FP_T10` | 310 K | **+10 K** | 1.03333333 | the heated arm |
| `FP_T290` | 290 K | **−10 K** | 0.96666667 | the cooled arm: `M4b`'s second operand, non-degenerate, **and a Stanton measurement in its own right** |

`|dT| = 10 K` is small on purpose: large enough that Stanton is well
conditioned, small enough that constant properties hold and a Boussinesq solver
at `beta = 0` is not asked to represent variable-density physics.

---

## 3. Why the redesign exists — one artifact carrying two incompatible jobs

K0eR2 was graded **`NOT A RESULT`**. Its transferable finding is a **design
conflict**, and this rung is the resolution.

**Job A — the second operand of `M4b`, the only gated row.** `M4b` is a
bit-exactness comparison whose entire evidentiary content is the premise *one
binary, one operator set, two wall temperatures*. **Job A requires the two arms
be identical in every operator and every setting except the wall temperature.**

**Job B — the physical zero-heat-flux null.** With `T_wall = T_inf` the wall
heat flux must be identically zero, which catches a spurious flux manufactured
by the discretisation, the boundary conditions or the reader. That reader is
the wall-heat-flux reader — **the instrument that produces `q`, and therefore
`St`, for every reported row on the rung**. **Job B requires `dT` be
identically zero.**

K0eR2 put both jobs on one artifact, `FP_T00` at plate 300 K. **`T ≡ 300` is
then simultaneously the initial condition and the exact steady solution.** A
uniform field has zero gradient everywhere, so convective and diffusive fluxes
vanish identically; the temperature equation is satisfied to machine precision
before the first sweep; OpenFOAM's residual normalisation factor degenerates to
round-off; and the normalised residual tested against `tolerance 1e-10` is a
ratio of two round-off quantities — an O(1) number that cannot fall.

**Measured on K0eR2's artifacts:** `FP_T00` reported `No Iterations 1000` on
**349 of 349** T solves, its first solve's final residual (0.6092429219)
**exceeded its initial** (0.5053587649), and it ran at **8.99 s/outer
iteration** against `FP_T10`'s 0.3126 — a factor of **28.8**, flat. It needed
~2,696 core-min to reach `endTime`, **25.7× its own registered cap**, and was
killed by that cap at iteration 350 of 9000 with `writeInterval 9000`, so the
loss was total: no field, no restart point. *(The normaliser itself was never
instrumented; that mechanism is the reading those observations support and is
not a measurement of `normFactor`. The limit is repeated here rather than
laundered into a fact.)*

**The conflict cannot be fixed on one artifact.** A dictionary fix applied to
the control arm alone makes the arms differ in more than the wall temperature,
so the premise `M4b` rests on is false as written. A fix that preserves the
premise leaves the degeneracy exactly where it was, because the degeneracy is a
property of the *physical specification* (`T_wall = T_inf`), not of the solver
settings. **The fault is the conflation, not either job.**

**The resolution is structural: split Job A from Job B, and relax neither.**
Job A's second operand becomes `FP_T290` at `dT = −10 K` — one line of `0/T`
differs, the T solve is the same well-posed problem the heated arm solved, and
because the only `T → U` coupling is linear and therefore **odd**, the pair
`(−10, +10)` drives any leak at **twice** the amplitude of `(0, +10)` and with
opposite sign between the arms. Job B is re-homed onto `Z1`/`Z2`/`Z3`, a
constructed on-disk control at **zero solver compute**, which reads the same
production wall-flux reader on a field whose exact value is known a priori.
**No arm or artifact in this rung is simultaneously the operand of a
bit-exactness comparison and the carrier of a physical null.**

---

## 4. THE HEADLINE — `M1b`: `St` is bit-identical between the heated and cooled arms

**This is the row the redesign bought. It was impossible under K0eR2's design,
whose control arm had no Stanton number at all.**

The constant-property Boussinesq energy equation is **exactly linear in
`(T − TRef)`**, and at `beta = 0` the momentum field is independent of `T`.
So `q` scales linearly with `dT`, and `St = q/(Cp·rho·U·dT)` is **independent
of `dT` and of its sign**. Equation (1), carrying the factor
`(Pr·Tw/T_inf)^-0.4`, instead predicts the cooled arm's `St` at
**`1.027036 ×`** the heated arm's — that constant is the ratio of the two
frozen eq.-(1) columns and was registered before compute.

Measured at the six registered stations, `|St(FP_T290) − St(FP_T10)| /
St(FP_T10)`:

| `Re_x` | `St`, FP_T290 (cooled) | `St`, FP_T10 (heated) | `\|rel\|` |
| ---: | ---: | ---: | ---: |
| 1.0e6 | 2.063363e-03 | 2.063363e-03 | **0.000e+00** |
| 2.0e6 | 1.847912e-03 | 1.847912e-03 | **0.000e+00** |
| 3.0e6 | 1.739464e-03 | 1.739464e-03 | **0.000e+00** |
| 5.0e6 | 1.607926e-03 | 1.607926e-03 | **0.000e+00** |
| 7.0e6 | 1.531325e-03 | 1.531325e-03 | **0.000e+00** |
| 1.0e7 | 1.457057e-03 | 1.457057e-03 | **0.000e+00** |

**Stations returning `NOT A RESULT` on an undefined `St`: 0.** The registered
prediction (Pred-10) was `< 1e-5` relative, derived from `writePrecision 10`
and the final linear-solve residual rather than chosen; **the measurement is
exactly zero at every station — the two arms' Stanton numbers are
bit-identical.**

### 4.1 The 2.70 % discrepancy — stated for exactly what it is

**The model says the ratio is 1.000000. The correlation says it is 1.027036.
This rung therefore MEASURES a ~2.70 % structural discrepancy between the
constant-property model and eq. (1)'s temperature-ratio factor — a
variable-property effect the model has no mechanism to represent.**

**What this is evidence of:** that the two objects being compared differ
*structurally* over the sign of `dT`, by an amount that is a fixed constant of
the correlation and identically zero in the model, and that the difference is
attributable to the temperature-ratio factor alone, because everything else in
the comparison is held identical by construction and by `P7`.

**What this is NOT evidence of, and must not be read as:**

- **It is not a validation of eq. (1).** No band is armed on the correlation
  (§1), the primary data are NOT OBTAINED, and the correlation states no
  uncertainty of its own.
- **It is not an error in eq. (1).** The correlation carries a
  variable-property factor because real gas properties vary with temperature;
  a constant-property Boussinesq solve at `beta = 0` is a model that has
  removed that physics on purpose. **A model with no mechanism for an effect
  disagreeing with a correlation that carries one is a statement about the
  model's scope**, and this rung has no third instrument that could say which
  of the two is nearer the truth.
- **It is not a discretisation finding.** Per B6 there is no grid triple and
  therefore no bound on either arm's own numerical error — though note the two
  arms share the mesh, the operators and the binary exactly, so whatever that
  error is, it is common to both and cancels in `M1b` even though it is
  unbounded in `M1`.

`M1b` also doubles as an independent cross-check on `M4b`'s premise: an `M1b`
far above round-off would mean either that the momentum field moved or that the
energy equation is not linear, **both of which `M4b` should also have seen.**
Both rows read zero, and they read it through different instruments.

---

## 5. The gated rows, with their numbers

### 5.1 `M4b` — `PASS`, 0 ULP

`FP_T10` vs `FP_T290`, momentum field `U` at `endTime 9000`, processor-local,
every component of every cell, threshold **0 ULP** frozen at `3f33d815`.
**There is no tolerance constant in the comparator.**

| | measured |
| --- | ---: |
| cells compared | **52 224 × 3 components** |
| components at non-zero ULP | **0** |
| worst ULP distance | **0** |

**The momentum field is bit-identical between a plate 20 K apart in wall
temperature.** `beta` and `g` are neutralised against an odd-mode perturbation
of twice the predecessor's amplitude — subject to B1, B2 and B5.

A non-zero here was registered as **`GATE FAIL`**, not `NOT A RESULT` — a
deliberate departure from K0eR2's label, argued in §5.2 of the registration and
made before compute. That departure is what made `GATE FAIL` genuinely
reachable on this rung for the first time; **the threshold was unchanged at
0 ULP and was not widened to fit the answer.**

### 5.2 `Z1` — `PASS`, 0 flux on all 208 plate faces

An exact uniform **300.0 K** field was constructed over all 52,224 cells (a
*nonuniform* internal field every value of which is exactly `300.0`, with every
`plate` face value exactly `300.0`), and the **production** wall-heat-flux
reader — the same function the graded path calls — was run on it.

| | measured |
| --- | ---: |
| plate faces read | **208** |
| faces at non-zero flux | **0** — at 0 ULP against `0.0` |

**Expressed absolutely rather than relatively on purpose:** a relative form
`|q|/q_ref` has a denominator identically zero on the null case, which is the
D-J1 divide-by-zero-guard trap in its purest form. **There is no epsilon in
this comparison and there must never be one.** A non-zero here was registered
as `NOT A RESULT`, because a reader that manufactures flux means no measurement
exists on the rung at all.

**This is Job B, delivered at zero solver compute**, against the ~2,696
core-min K0eR2 projected to produce a field whose exact value is known a
priori.

### 5.3 `D0` — `PASS`, 0 ULP, and it was armed BEFORE the main arms

Two invocations of the same case at `endTime 200`, both `DONE` on all six
clauses of rule 4.

| | measured |
| --- | ---: |
| components compared | **156 672** (52,224 × 3) |
| components at non-zero ULP | **0** |
| worst ULP distance | **0** |
| twin wall rates | **0.1100** and **0.1050** wall s/it — **4.8 % apart** |

**The twins ran at measurably different speeds and agreed on every one of
156,672 components.** A non-zero `M4b` arising from solver nondeterminism would
have been a false `GATE FAIL`; this found its absence for ~1.43 core-min
instead of ~142. Its reach is B7: this epoch, 200 iterations.

### 5.4 `P7` — `PASS`, the premise is a blocking refusal and not an expectation

| | measured |
| --- | ---: |
| files compared over `0/`, `constant/`, `system/` | **23** |
| differing files | **1** — `0/T` |
| differing lines | **1**, at 1-based **39** — the line the registration records |
| plate `T_wall` | `FP_T10` **310.0**, `FP_T290` **290.0** |

`M4b`'s entire claim to isolate a `beta`/`g` leak rests on this premise and on
nothing else, so it is **checked at grade time and refuses (exit 2) on any
other count, on a difference at any other line, and on a wrong wall
temperature** — rather than being asserted in prose.

---

## 6. The reported rows — REPORTED, gating nothing

### 6.1 `M1` — Stanton against eq. (1), both arms, **no band**

Eq. (1) is evaluated at each station's **actual** `Re_x` (printed beside the
target), which is why these values differ in the fourth digit from the twelve
nominal-`Re_x` values frozen in the registration's §5.5 table.

| `Re_x` target | actual `Re_x` | `St` (both arms) | eq. (1) at `Tw` 310 | dev | eq. (1) at `Tw` 290 | dev |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1.0e6 | 1.00517e6 | 2.063363e-03 | 2.111760e-03 | **−2.292 %** | 2.168853e-03 | **−4.864 %** |
| 2.0e6 | 2.00567e6 | 1.847912e-03 | 1.839248e-03 | **+0.471 %** | 1.888973e-03 | **−2.174 %** |
| 3.0e6 | 2.97299e6 | 1.739464e-03 | 1.700018e-03 | **+2.320 %** | 1.745979e-03 | **−0.373 %** |
| 5.0e6 | 5.02523e6 | 1.607926e-03 | 1.530597e-03 | **+5.052 %** | 1.571978e-03 | **+2.287 %** |
| 7.0e6 | 7.05503e6 | 1.531325e-03 | 1.430186e-03 | **+7.072 %** | 1.468851e-03 | **+4.253 %** |
| 1.0e7 | 9.88891e6 | 1.457057e-03 | 1.336788e-03 | **+8.997 %** | 1.372929e-03 | **+6.128 %** |

**Stations returning `NOT A RESULT` on an undefined `St`: 0.** The deviation
grows monotonically with `Re_x` on both arms, from under-prediction at the
first station to about +9 % (heated) and +6 % (cooled) at the last. **No band
is armed, so none of these twelve numbers can produce a `PASS` and none can
produce a `GATE FAIL`** (§1). They are reported because the registration
committed to reporting them, and the two columns differ by exactly the
`1.027036` factor of §4 because the model's `St` is the same in both rows.

### 6.2 `M2` — skin friction, control

`Cf` at the six stations: 3.430407e-03, 3.077291e-03, 2.898975e-03,
2.683021e-03, 2.555255e-03, 2.432247e-03. Read by the same reader on the same
field; REPORTED.

### 6.3 `M3` — `Prt_eff = nut/alphat`, a convergence diagnostic and not physics

Both arms, over 52,224 cells, with **0 cells excluded** for `alphat == 0`
(the count is printed, because an unstated exclusion is an unstated blind
spot): min **0.849950**, max **0.850001**, **max |dev from 0.85| =
4.957e-05**, exactly 0.85 in 816 cells — identical in both arms.

### 6.4 `M5` — thermal boundary layer

At `x = 0.594598` m, 192 column cells, `delta_T_99` = **0.008869112008 m** —
**identical to all printed digits between the heated and the cooled arm**,
which is the same linearity §4 measures, read through a different quantity.

### 6.5 `M4` — cross-solver, REPORTED and correctly **not** gated

**216 639 507 ULP** against the recorded `simpleFoam` field.

`simpleFoam/UEqn.H` solves `UEqn == -fvc::grad(p)`, while
`buoyantBoussinesqSimpleFoam` solves `UEqn == fvc::reconstruct(...)`. **Those
are different discrete operators and they differ independently of `beta` and
`g`**, so a non-zero `M4` conflates *"`beta`/`g` leaked"* with *"the operators
are not identical"*. **A row that cannot answer its own question is not
gated** — that disposition was registered before compute (Pred-8 predicted the
non-zero), and this large number is **not a defect of this rung**.

### 6.6 `D2` — cross-epoch, REPORTED and not gated

**0 ULP.** K0eR2's `FP_T10` arm reproduces bit-for-bit across the epoch.

Both arms were nonetheless **re-run fresh inside one run root, under one
registration, in one box epoch**, at a deliberate cost of ~95 core-min, because
a non-zero here cannot separate solver nondeterminism from a change in the box
between 2026-09-03 and now — and a `GATE FAIL` manufactured by an epoch
difference would have been a false failure, which is worse than the spend. The
0 ULP is what a reuse would have needed and is recorded **after** the decision,
not as a justification for skipping it.

---

## 7. The controls — a reader can be wrong in two directions, and both were tested

**Standing rule 3: a zero from a reader not shown able to see a non-zero is not
evidence.** Six plants were registered and **all six were exercised**.

| plant | into | required | measured |
| --- | --- | --- | --- |
| **P1** | scalar `1.234e-03` K into a copy of the graded `T`, by line index | be SEEN | read back `0.001234` at line 23 — **SEEN** |
| **P2** | vector `1.234e-03` m/s in `x` into a copy of the graded `U` | be SEEN by the **vector** reader | read back `0.001234` at line 23 — **SEEN** |
| **P3** | exactly `0.0` | **NOT** fire | **DID NOT FIRE** |
| **Z1** | the constructed uniform-300.0 field | 0 flux on 208 faces | **0** — §5.2 |
| **Z2** | `1.234e-03` K into **cell 12288**, the owner of **plate face 0** at `x = 0.0002221885509` (line 12311) | make the **wall-flux** reader move | moved to **−1.0242e−03 K m/s** — **SEEN** |
| **Z3** | `1.234e-03` K into **interior cell 0**, which owns no plate face (line 23) | leave the plate reader unmoved | **DID NOT FIRE** over all 208 faces |

The live background against which P1/P2/P3 fired is printed beside them:
`T` 300.0, `U` (0.9999993635, 5.913965652e-11, 0.0) — so the plants were read
against a real field, not against an empty one.

**Why `Z1`'s zero is credible, stated as the argument and not as an
assurance.** `Z1` reports a zero. On its own that zero is compatible with a
reader that cannot see anything at all, and with a reader that sums over cells
it has no business reading and happens to find them at 300 too. **`Z2` closes
the first: the same wall-flux reader, on the same field, moved to
−1.0242e−03 K m/s when 1.234e-03 K was planted in the owner cell of a named
plate face — so it is demonstrably able to see a non-zero. `Z3` closes the
second: the same plant into a named interior cell adjacent to no plate face
left the plate reader unmoved — so it is reading the plate's cells and not
everything.** A reader can be wrong in two directions — blind, or
over-inclusive — **and both directions were tested, by separate plants, from a
pristine field kept outside the case so neither plant contaminates the other.**

**`Z2` is separate from `P1` on purpose**, because the scalar-field reader and
the wall-flux reader are different instruments, and it is the wall-flux
reader's zero that `Z1` asserts. **`P2` is separate from `P1` on purpose**,
because a scalar plant does not exercise a vector reader and `M4b` reads
vectors. Every plant goes into the field file the graded path reads — never a
dict, a spec or a constants table — and is read back through the same function
the graded path calls, matched at **0 ULP** rather than at a tolerance.

**K0eR2 EXERCISED NO CONTROLS AT ALL.** Its plants sat after the both-arms
early return, so on a `NOT DONE` arm they were structurally unreachable. **No
planted-control evidence was inherited by this rung and none is claimed;** all
six were exercised here, on this rung's own data.

---

## 8. The registered predictions, measured — including one that is FALSIFIED

Ten predictions were registered at `3f33d815` before any compute, with their
falsifiers.

| # | registered | measured | outcome |
| --- | --- | --- | --- |
| **Pred-1** | `FP_T290` completes rule 4 and **zero** of its 9000 T solves report `No Iterations 1000` | **0 of 9000** (re-counted from `FP_T290/log.solve`; `FP_T10` also 0 of 9000) | **held** |
| **Pred-2** | `FP_T290` cost in **[71.1, 118.5]** core-min | **70.8000** | **FALSIFIED** — §8.1 |
| **Pred-3** | `M4b` = 0 ULP | 0 ULP | held |
| **Pred-4** | `Z1` = 0 flux at 0 ULP on 208 faces | 0 on 208 | held |
| **Pred-5** | `D0` = 0 ULP | 0 ULP | held |
| **Pred-6** | max `\|nut/alphat − 0.85\|` **below 1e-3**, against 0.697 on K0eR2's 5-iteration preflight | **4.957e-05** | held, by a factor of ~20 |
| **Pred-7** | `\|St − St_eq1\|/St_eq1` of order 10 % or less at all six stations on both arms | worst **+8.997 %** (heated, 1.0e7); worst cooled **+6.128 %** | held. **This was a prediction and not a band: it could not produce `PASS` and could not produce `GATE FAIL`** |
| **Pred-8** | `M4` non-zero | 216 639 507 ULP | held |
| **Pred-9** | `D2` = 0 ULP | 0 ULP | held |
| **Pred-10** | `M1b` below `1e-5` at all six stations; eq. (1) predicts `1.027036 ×` | **0.000e+00** at all six | held — §4 |

**Pred-1 is the measurement that the degeneracy is gone**, and it is worth the
comparison in full: K0eR2's zero-`dT` arm hit the 1000-sweep cap on **349 of
349** T solves; this rung's cooled arm hit it on **0 of 9000**. The sign of
`dT` is irrelevant to well-posedness, and the artifact now says so.

### 8.1 Pred-2 is FALSIFIED, and it is reported as a miss

**Registered interval [71.1, 118.5] core-min. Measured 70.8000 core-min.
OUTSIDE THE FLOOR by 0.3000 core-min — 0.42 %.**

It is a miss in the conservative direction — the arm cost less than the
interval allowed — and it touches no gate, no threshold and no cap. **It is
nonetheless a miss. A registered interval missed by 0.42 % is missed, and
recording it as "essentially inside" would be widening an interval after the
fact**, which is the thing standing rule 2 exists to prevent. It is recorded
here, and in the calibration ledger row, as a registered falsifier that fired.

The cause is the same one §9 attributes: the interval was built as ±25 % around
K0eR2's `FP_T10` at **0.3126 wall s/it**, and these arms ran at **0.2366 wall
s/it** — 24.3 % faster on a byte-identical case, against a different mix of
co-tenants. **A ±25 % interval around a load-measured rate was 0.42 % too
narrow at its floor**, and that is the calibration lesson, not the direction of
the miss.

---

## 9. Cost — rule 12, estimate against actual

**The calibration row `C-20260904T023833.148263Z-dfbdde5f` is already landed in
`docs/COST_CALIBRATION.md` at commit `f3a838ec`. It is restated here and NOT
duplicated there.**

| | core-min |
| --- | ---: |
| Registered **POINT** (`K0eR3_PREREGISTRATION.md` §7.2, frozen `3f33d815`) | **197.30** |
| **Measured actual** | **143.2000** |
| `FP_T10` (2129 wall s × 2 ranks ÷ 60) | 70.9667 |
| `FP_T290` (2124 × 2 ÷ 60) | 70.8000 |
| `D0_A` + `D0_B` (22 and 21 wall s) | 1.4333 |
| **Ratio actual / predicted** | **0.7258** — the rung came in **27.4 % under** its registered POINT |
| Registered **CEILING** | 971.90 — **usage 14.73 %** |
| Per-arm registered **CAP** | 475.00, enforced in metal as `timeout 14250` s at 2 ranks — **usage 14.94 % and 14.91 %** |
| **WASTE** | **0.0000** |

**Dollars: `$0.12244` at $0.0513/core-h. DERIVED, NOT MEASURED**; `cost_basis`
**reported-by-owner** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Predicted `$0.16869` on the same derivation.

**Waste is 0.0000 and that is a measurement rather than an omission.** All four
runs completed `rc=0` on all six rule-4 clauses and all four are usable; no run
was restarted and no attempt discarded; no run approaches the charter's 3600
wall s stall rule (2129, 2124, 22, 21 s). **Gross equals cleaned.**

**The contrast with the predecessor is the point of the redesign.** K0eR2 spent
**105.03 core-min — 52.6 % of its rung total — on an arm that bought nothing**,
and that spend is named separately and is **not** folded into this rung's
ratio. K0eR3 spent zero on waste, and the arm that replaced the degenerate one
completed in **70.80 core-min**.

**Attribution of the 0.7258.** The POINT was the **measurement itself, not a
factor on a proxy**: K0eR2's `FP_T10` ran this exact mesh, `endTime` and rank
count at 94.7667 core-min, rounded to 95.00 — deliberately not repeating
K0eR2's 35.00, which was 28.00 × an *estimated* 1.25 and missed by ×2.7076.
The residual 24.3 % is attributed to **co-tenancy**, the only variable measured
to have changed: 12 of 16 vCPUs were busy in both epochs, but K0eR2's arm ran
against two 455,456-cell solves while these ran against a single 8-rank job.
**No split between contention and residual misprediction is asserted on a
guess** — there exists no quiet-box measurement of this mesh at this date, so
any unmeasured drift sits inside that figure and is said to.

**The two arms agreed with each other to 0.24 %** (70.9667 against 70.8000)
despite staggered starts: **a control arm that reverses the sign of a gradient
costs what the heated arm costs.** K0eR2's lesson — that a control arm must be
costed as a *different* solve — applies to an arm that nulls a gradient, not to
one that reverses it.

**The grader's own cost is not separately instrumented:** registered POINT 0.30
core-min against a 0.90 cap, one invocation at 1 rank returning in seconds, so
it is **bounded** far below its point — a bound, not a measurement, and not
entered as one.

---

## 10. Provenance, and what this record could not establish

**The verdict of record is the stdout artifact and the landed commit, never an
exit code.** K0eR2's grader exited `rc = 0` while printing `NOT A RESULT`; this
grader returns its PASS code at exactly one site and a failure code at six
others, and takes the registration path as a required argument and prints it as
given, rather than hard-coding a predecessor's path in a banner. Both
predecessor traps are closed in code.

**The grading path was pinned before compute and the pin was armed at run
time.** `--expect-sha 6d7b4d2c…` was supplied; `--expect-sha` and `--prereg`
are required arguments, so the K0eR2 fail-open in which omitting the flag
silently disarmed the pin cannot occur. The queue rows for both arms declared
`grading_freeze` naming all three pinned paths, and the runner logged them as
`PINNED`, which **required setting the rows' `prereg_commit` to the addendum
commit `52928b1d` rather than the registration commit `3f33d815`** — because
the grader did not exist at the registration freeze, §0.1 having deliberately
left the pins uncut there. That is disclosed rather than buried, and it is a
structural finding for any successor: **if a registration defers its pins to an
addendum, the queue row's `prereg_commit` must be the addendum commit, or the
freeze gate cannot see the comparator.**

**Not established here, and not claimed:**

- **Everything in §1.** The blind spots are the load-bearing limits and they
  are undischarged.
- **The `Prt = 0.85` closure is not validated, and no rung on this ladder has
  validated it.** What K0eR3 buys is **attribution**: a Stanton error on this
  case is now attributable to the thermal closure alone rather than to a
  buoyancy coupling — which is the confound `THERMAL_CAPABILITY_STATE.md` §5
  names as binding, and which `K0cR` demonstrated by moving velocity 19 points
  toward experiment and wall heat flux 30 points away in the same solves.
- **No number here has a discretisation bound** (B6), so none of them may be
  carried into a comparison that assumes one.
- **The Moretti & Kays primary is NOT OBTAINED**, and no row grades against
  their data.
- **`SUPERVISION_CHARTER.md` §3 checks 1 and 4 — the measurement-script diff
  read, and pre-registration committed before compute — were discharged
  personally by the heat-transfer supervisor before the launch.** This record
  did not perform them and does not claim them.

*Recorded by a heat-transfer lane, 2026-09-04, from the artifacts named above.
No frozen file was edited, no grader was re-run and nothing was re-graded.
Nothing was sent, filed, uploaded, registered or posted — submissions are
PARKED (standing rule 7).*
