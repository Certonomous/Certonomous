# F12 — ENERGY-BOUND DISCRIMINATOR (THREE ARMS): PRE-REGISTRATION

**cfd lane, 2026-08-25. Registered and COMMITTED BEFORE the compute it covers.**
Commissioned by `verification/campaign/F12_CRASH_TRIAGE_ROUND2_2026-08-25.md` §6, which
names the two arms and fixes the discriminator, and which itself rests on
`verification/runs/F12_runs/RUNG2_DISPOSITION_AND_CRASH_TRIAGE_2026-08-25.md` (round 1) and
its AMENDMENT 1.

**THIS DOCUMENT AND EVERY ARM UNDER IT GRADE NOTHING.** No F12 gate, threshold, band, cap or
label is touched, read against, or quoted from. **F12 rung 1 stands `NOT A RESULT`; rungs 2–5
stand `BLOCKED`.** Rung 2's `rate_calibration_gate()` interlock in `launch_f12_rung.py` is
**not invoked, not read around and not edited**. No verdict from the fixed vocabulary is due
to this probe and none will be issued from it. Its output is three iteration numbers, three
span ratios, and a completion report.

**NO MECHANISM IS CLAIMED HERE AND NONE MAY BE CLAIMED FROM THE RESULT.** Three of the last
four mechanism claims on this line have been corrected, one of them the supervisor's own. This
probe discriminates between two named candidates; **elimination of both is a finding about
those two levers and is not a coronation of a third.**

---

## 0. WHY THIS IS A SEPARATE REGISTRATION AND NOT AN AMENDMENT

`N-C4`, landed by this team from the Ekaterinaris intake, rules that **a change of scheme
order is a CHANGE OF EXPERIMENT, not a tuning knob.** Standing rule 2 forbids a change of
experiment inside a fired pre-registration, and `verification/campaign/F12_PREREGISTRATION.md`
has fired. Arm 1 changes a scheme order and arm 2 changes a relaxation factor; **neither may
ride in on any existing F12 freeze**, and neither is offered as a repair to one.

This document is therefore a **new instrument with its own questions, its own predictions, its
own decision rule and its own cap**, whose entire output is diagnostic. It cannot unblock a
rung, cannot regrade one, and cannot be cited by any F12 grading record as evidence for or
against a gate.

## 1. THE PHYSICAL BOUND THIS PROBE IS BUILT ON, DERIVED FROM THE CASE'S OWN INPUTS

Read from the registered rung-1 case
`verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/`:

| input | value | file |
| --- | --- | --- |
| `internalField` of `T` | `uniform 300` | `0/T:12` |
| `internalField` of `U` | `uniform (254.55661283 12.40536100 0)` | `0/U:12` |
| `internalField` of `p` | `uniform 101325` | `0/p:12` |
| `Cp` | `1004.5` | `constant/thermophysicalProperties`, `mixture/thermodynamics` |
| `molWeight` | `28.96` | same, `mixture/specie` |
| `Pr` | `0.71` | same, `mixture/transport` |
| energy variable | `sensibleInternalEnergy`, `hConst`, `perfectGas`, `hePsiThermo` | same, `thermoType` |
| wall `T` condition | `zeroGradient` on patch `aerofoil` — **adiabatic** | `0/T` |

**Derived, arithmetic on those numbers and nothing else:**

```
|U|^2  = 254.55661283^2 + 12.40536100^2 = 64952.9621170228 m^2/s^2
|U|    = 254.8587101063 m/s
dyn    = |U|^2 / (2 Cp) = 64952.9621170228 / 2009.0 = 32.3309915963 K
T0     = 300 + 32.3309915963 = 332.3309915963 K
```

**`T0` is stated as a TOTAL-ENTHALPY bound, not an isentropic-Mach one, and that is
deliberate.** `T0 = T_inf + |U_inf|^2 / (2 Cp)` contains no `gamma` and no gas constant, so it
does not depend on which value of `R` or `gamma` a reader adopts; it is the direct statement
that for a calorically perfect gas with `Cp = 1004.5`, adiabatic walls and no energy source,
the specific total enthalpy anywhere in the steady field is bounded by its freestream value,
and `T <= T0` follows wherever the local velocity is non-negative. **`EEqn.H` of
`rhoSimpleFoam` (openfoam2606) contains no source term other than `fvOptions`, and this case
registers no `fvOptions`** — verified at
`/usr/lib/openfoam/openfoam2606/applications/solvers/compressible/rhoSimpleFoam/EEqn.H`.

**Independent corroboration that this is the case it says it is:** `system/controlDict`'s
`forceCoeffs1` carries `magUInf 254.8587101`, which reproduces the `|U|` derived above to all
eight printed digits, and `atan(12.40536100 / 254.55661283) = 2.790000 deg`, which reproduces
the registered `a2.79`.

**AN HONEST MARGIN, STATED AND NOT ASSUMED.** `T0` is the inviscid adiabatic bound. At
`Pr = 0.71` the adiabatic recovery temperature is `T + r (T0 - T)` with `r ~ sqrt(Pr) ~ 0.843`,
i.e. **below** `T0`, so viscous recovery does not licence an overshoot; a small local
total-enthalpy overshoot is nonetheless admissible in a boundary layer at `Pr < 1`, and
discretisation error admits more. **A generous ceiling is therefore fixed at
`T0 + 10 K = 342.3309915963 K` — an overshoot of 30.9 % of the entire dynamic temperature of
this flow.**

### 1.1 A CORRECTION AGAINST THE COMMISSIONING DOCUMENT, MADE BEFORE ANY COMPUTE

`F12_CRASH_TRIAGE_ROUND2_2026-08-25.md` §3 states that the control run's
`T_min = 203.324 K` at iteration 100 *"implies a local Mach number of 1.542"*. **That figure
uses `T_inf = 300 K` as the stagnation reference. The stagnation reference is `T0 = 332.331 K`,
not `T_inf`.** Recomputed from the case's own constants:

```
|U|^2_local = 2 Cp (T0 - T)    = 2 * 1004.5 * (332.3309916 - 203.323501) = 259,177.6 m^2/s^2
|U|_local   = 509.09 m/s
a_local     = sqrt(gamma R T)  = sqrt(1.4001988 * 287.101865 * 203.323501) = 285.90 m/s
M_local     = 1.7807
```

**The correct implied local Mach is 1.781, not 1.542.** The direction of the triage's
conclusion is **unchanged and strengthened** — the value is further from anything RAE 2822
case 9 carries, not closer. `gamma = Cp/(Cp - R) = 1.4001988` and `R = 8314.47/28.96 =
287.101865`, both from the case's own `constant/thermophysicalProperties`. **Recorded here,
before compute, so that the corrected number is on the record whatever the arms return.**

## 2. THE QUANTITIES — AND FOR EACH ONE, PROOF THAT IT CAN PASS AND CAN FAIL

**This section exists because of the `P4` defect of
`F12_TERMINAL_DEPARTURE_PREREGISTRATION.md`, self-disclosed by that lane, and the identical
defect class in ansys-verification's VMFL059 (`6a9afa0a`): a registered quantity that could
not have taken a failing value whatever the run did.** Every quantity below is shown, on this
solver's actual on-disk output, to be able to take both a passing and a failing value, and its
write path is named.

### 2.1 `T_max` and `T_min` — the primary readings

**Write path.** `system/controlDict` sets `writeControl timeStep; writeInterval 1;
writeFormat ascii; writePrecision 10; purgeWrite 0; writeCompression off`. `Foam::Time`
writes `<case>/<iteration>/T` from `volScalarField T` through `regIOobject::writeObject`. The
reader parses `internalField nonuniform List<scalar>` and takes `max()` and `min()` over the
internal field.

**T IS NOT CENSORED ON THE WAY TO DISK. Proven at source, three ways:**

1. `hConstThermo<EquationOfState>::limit(const scalar T) const { return T; }` —
   `/usr/lib/openfoam/openfoam2606/src/thermophysicalModels/specie/thermo/hConst/hConstThermoI.H:84-90`.
   This is the `limit` function pointer passed into `species::thermo::T(...)`
   (`specie/lnInclude/thermoI.H:44-56`), i.e. the only clamp on the Newton inversion, and for
   this case's `hConst` thermo **it is the identity.** (Contrast `janafThermo::limit`, which
   does clamp — this case does not use it.)
2. `grep -rl 'TMin_\|TMax_'` over
   `/usr/lib/openfoam/openfoam2606/src/thermophysicalModels` returns **zero files**. There is
   no temperature-range limiter in this thermo library.
3. `EEqn.H` applies no `bound()` and no `max()`/`min()` to `he` or `T`.

**The contrast that makes this a real check and not a formality:** `p` **is** censored, by
`bool pLimited = pressureControl.limit(p);` at `rhoSimpleFoam/pEqn.H:93`, which is exactly why
the terminal-departure probe's `P4` was degenerate. **`T` does not go through that path. This
probe reads `T` and does not read `p`.**

**Both branches are attainable, measured, on-disk, in the committed control artifact**
`verification/runs/F12_runs/terminal_departure_2026-08-25/evidence/terminal_departure.json`
(`Q2_T_min_track`):

| branch | attained? | evidence |
| --- | --- | --- |
| `T_max <= 332.331` (passing) | **YES** | iteration 1: `302.835189`; iteration 8: `329.624836`; time 0: exactly `300` |
| `T_max > 332.331` (failing) | **YES** | iteration 4: `332.985381`; iteration 147: `608.505297` |
| `T_max <= 342.331` (passing) | **YES** | every iteration 1 through 18 |
| `T_max > 342.331` (failing) | **YES** | iteration 19: `342.519742` |

### 2.2 DISCLOSURE — THE `T0` THRESHOLD IS NEAR-DEGENERATE IN THE FAILING DIRECTION, AND IS THEREFORE NOT THE PRIMARY DISCRIMINATOR

**This is a departure from the commissioning brief's framing and it is made before compute,
with its reason.** §6 of the round-2 triage names *"`T_max` against `T0` in the first 20
iterations"* as the discriminator. **`T_max > T0` is a bound that a perfectly healthy
converged solution touches from below**: the stagnation cell of an adiabatic transonic
aerofoil solve sits at `T0` by construction, so a fraction-of-a-Kelvin crossing is expected
from discretisation error alone in any run, healthy or not. The control's own first crossing
is `332.985` — **0.65 K, i.e. 2.0 % of the dynamic temperature, above the bound.** A quantity
whose failing branch is nearly guaranteed is a weak discriminator, and registering it as the
primary one would repeat the `P4` class in the opposite direction.

**Accordingly:**

- **The primary timing discriminator is `D1`, the generous ceiling `T0 + 10 K = 342.331 K`**,
  which a healthy solve sits ~10 K clear of and which the control breaches by 31 % of the
  dynamic temperature. Both branches are freely attainable (§2.1 table).
- **The primary magnitude discriminator is `D2`, a span ratio** (§2.3), which is two-sided by
  construction and has no bound to touch.
- **`D3`, the `T0` crossing, IS STILL REGISTERED AND REPORTED**, because it is the most
  sensitive early indicator and because the brief asks for it — but it is reported **with this
  degeneracy disclosed beside it** and **no arm is classified on `D3` alone.**

### 2.3 `D2` — THE SPAN RATIO, AND WHY IT IS THE SOUNDEST QUANTITY HERE

```
S20 = ( T_max(iteration 20) - T_min(iteration 20) ) / 32.3309915963
```

The denominator is **the entire dynamic temperature of this flow**. A converged adiabatic
solution of this case has a field span of order one dynamic temperature (`S ~ 1`); it cannot
have a much larger one without a local Mach far above anything RAE 2822 case 9 carries.

**Both branches attainable, measured, on-disk:** `S = 0` at time 0 (uniform 300);
`S = 0.710023` at iteration 1; `S = 1.757569` at iteration 4; **`S20 = 3.282372` for the
control**; `S = 19.075` at iteration 147. **No bound is touched and no censor lies on the
path** — `T_max` and `T_min` come from the same uncensored field read as §2.1.

**Control values, fixed now from the committed artifact, to be reproduced by arm 0:**

| iteration | `T_max` | `T_min` | span | span / 32.331 |
| --- | --- | --- | --- | --- |
| 1 | 302.835189 | 279.879433 | 22.955756 | 0.710023 |
| 4 | 332.985381 | 276.161434 | 56.823946 | 1.757569 |
| 8 | 329.624836 | 270.272989 | 59.351848 | 1.835757 |
| 11 | 335.446862 | 264.218612 | 71.228250 | 2.203095 |
| 19 | 342.519742 | 233.939444 | 108.580298 | 3.358397 |
| 20 | 342.626798 | 236.504460 | 106.122338 | **3.282372** |

### 2.4 `rc` — read back, never inferred

Each arm's runner writes the solver's exit status to `<case>/RC.txt`, calls `sync`, and the
runner then **reads the file back**; a missing, empty or non-integer `RC.txt` is a **REFUSAL
(exit non-zero)** and `rc` is reported as **NOT MEASURED**. `set -e` does not gate at tool top
level and is not relied on anywhere in the runner. Both branches attainable: `rc = 134` is the
control's measured value; `rc = 0` is what an arm reaching `endTime 148` without aborting will
write.

### 2.5 The first-solve residual comparator — and its positive control is built in

Both branches attainable and **both will actually be exercised in this probe**: the comparator
returns **0 mismatches over 885 comparisons** for a faithful re-run (measured, control `P1`),
and it **must** return a non-zero mismatch count for arms 1 and 2, because they change the
discretisation. **That is registered as a hard control, `L1`, in §5.**

## 3. THE THREE ARMS — AND THE ENTIRE DELTA OF EACH

All three arms are copies of
`verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/` (`0/`, `constant/`,
`system/`), **1 rank**, executed **outside the repository** under
`/home/ubuntu/certonomous-runs/f12_energy_bound_discriminator_2026-08-25/arm{0,1,2}/case`.

**WHERE THE ARMS RUN — A DEPARTURE FROM THE BRIEF'S LETTER, STATED WITH ITS REASON.** The
commissioning message asks that each arm be built under
`verification/runs/F12_runs/energy_bound_discriminator_2026-08-25/`. Each arm writes 147 ascii
time directories totalling ~535 MB (measured: the terminal-departure probe's case is 535 MB),
so three arms are ~1.6 GB of transient field data. The model probe this document is built on
ran outside the repository for exactly this reason, and `CLAUDE.md`'s WHERE THINGS LIVE table
places bulk run data outside git under `/home/ubuntu/certonomous-runs/`. **The record,
readers, evidence and every artifact any number cites therefore land under
`verification/runs/F12_runs/energy_bound_discriminator_2026-08-25/` and are committed; only
the transient time directories live outside.** This departure is disclosed to the supervisor
in the lane report, not merely here.

**Common to all three arms — the output-control delta, four lines of `system/controlDict`:**
`endTime 6000 -> 148`; `writeInterval 6000 -> 1`; `purgeWrite 1 -> 0`; `writeCompression off`
added. This is the identical delta class the terminal-departure probe used, so arm 0 is
directly comparable to the committed control.

> ### ARM 0 — CONTROL. **No further change. RUN FIRST.**
> The unmodified case under this lane's own harness. **If arm 0 does not reproduce `rc = 134`,
> abort at iteration 148, `T0 = -2.384321367`, 0 residual mismatches, and the §2.3 `T_max` /
> `T_min` table exactly, THE HARNESS IS THE VARIABLE AND ARMS 1 AND 2 ARE VOID.** No
> discrimination is reported from a probe whose control did not reproduce.
>
> ### ARM 1 — SCHEME. **One line of `system/fvSchemes`.**
> `div(phi,e)      $energy;`  ->  `div(phi,e)      bounded Gauss upwind;`
>
> **Registered scope limit, named rather than glossed.** The `fvSchemes` entry `energy` is
> also referenced by `div(phi,K)` and `div(phi,Ekp)`. **This arm changes `div(phi,e)` ONLY**,
> exactly as commissioned, so the *implicit* energy convection becomes first order while the
> *explicit* `fvc::div(phi, Ekp)` term in `EEqn.H` remains `bounded Gauss linearUpwind
> limited`. **If arm 1 shows no effect, what is exonerated is the implicit energy convection
> scheme, NOT second-order energy transport in general.** That limit is registered now so it
> cannot be forgotten when the result is read.
>
> **And the candidate is registered at its correct strength, not its rhetorical one.** The
> terminal-departure probe described `div(phi,e)` as *"second-order and not TVD-bounded"*.
> **This lane read the dictionary and confirms the supervisor's correction: `limited` in
> `bounded Gauss linearUpwind limited` is NOT a flux limiter — it is the name of a
> `gradSchemes` entry, and that entry reads `limited cellLimited Gauss linear 1`.**
> `linearUpwind`'s second token is a gradient-scheme *name* looked up in `gradSchemes`, and
> `cellLimited ... 1` is the most restrictive form available, bounding the reconstructed face
> value to the neighbouring cell range. **`bounded` is also applied.** The candidate is real
> but weak, and it is registered as weak.
>
> ### ARM 2 — RELAXATION. **One line of `system/fvSolution`.**
> `relaxationFactors { fields { rho 0.05; } }`  ->  `rho 0.3;`  (matching `p 0.3`)
>
> **The lever is live, verified at source.** `rho.relax()` fires at
> `rhoSimpleFoam/pEqn.H:107-110`, inside `if (!simple.transonic())`, and this case's `SIMPLE`
> dictionary does not set `transonic`, so the non-transonic branch is taken and the factor is
> read.
>
> **The path from this lever to `T` is INDIRECT, and that is stated now rather than
> discovered later.** Under `hePsiThermo`, `T` is recovered from `he` alone; `rho = psi*p` is
> then relaxed. So `rho`'s relaxation reaches the energy equation through the mass flux `phi`
> and through the `Ekp = 0.5|U|^2 + p/rho` term in `EEqn.H`, not through the `he -> T`
> inversion. **The path exists; its magnitude is unknown; no claim is made about it.**

**CHANGING ANYTHING ELSE VOIDS THE ARM IT IS CHANGED IN.** Byte-identity of the 18 files that
must not change (`system/fvSolution`, `system/fvSchemes`, `system/blockMeshDict`,
`system/decomposeParDict`, `0/{T,U,p,k,omega,nut,alphat}`,
`constant/{thermophysicalProperties,turbulenceProperties}`,
`constant/polyMesh/{points,faces,owner,neighbour,boundary}`) is asserted against the source
case before each arm fires — **18/18 for arm 0, and 17/18 for arms 1 and 2 with the single
differing file being the arm's own named lever and no other.** The runner **aborts** otherwise.

## 4. THE DECISION RULE — FIXED NOW, BEFORE ANY ARM RUNS

For arm `A` in {1, 2}:

- `i_gen(A)` = the first iteration whose on-disk `T_max` exceeds **342.3309915963 K**, or
  `NONE` if no written iteration does. *Control: `i_gen(0) = 19`.*
- `S20(A)` = `(T_max(20) - T_min(20)) / 32.3309915963`. *Control: `S20(0) = 3.282372`.*
  **If arm `A` aborts before writing iteration 20, `S20(A)` is reported ABSENT — never
  estimated — and `A` is classified on `i_gen` alone, with its abort iteration stated.**
- `i_T0(A)` = the first iteration whose on-disk `T_max` exceeds **332.3309915963 K**, or
  `NONE`. *Control: `i_T0(0) = 4`.* **Reported, with its §2.2 degeneracy, never used alone.**

| classification | condition |
| --- | --- |
| **REMOVED** | `i_gen(A) = NONE` **and** `S20(A) <= 1.5` |
| **MITIGATED** | not REMOVED, **and** ( `i_gen(A) >= 38` **or** `S20(A) <= 1.641186` ) |
| **EXONERATED** | `i_gen(A) <= 37` **and** `S20(A) > 1.641186` |

`38` is twice the control's `i_gen`; `1.641186` is half the control's `S20`. Both are fixed
here and neither is derived from any arm's output.

**THE JOINT OUTCOME, AND ITS WORDING IS FIXED NOW SO IT CANNOT BE SOFTENED LATER.** If arm 1
and arm 2 are **both EXONERATED**, this probe reports, in these words:

> **BOTH ARMS ARE EXONERATED — AND THAT IS A RESULT, NOT A NULL.** Neither the implicit
> energy-convection scheme order nor the `rho` under-relaxation factor removes or materially
> delays the early excursion above the flow's own stagnation-enthalpy ceiling. The search
> moves to the boundary conditions.

**And its limit is fixed now too:** exonerating two candidates **names no third.** No
mechanism follows from this outcome, and none will be asserted.

## 5. PRE-REGISTERED PREDICTIONS AND HARD CONTROLS — THESE CAN FAIL

**`P0` — HARNESS FAITHFULNESS (arm 0). IT GATES EVERYTHING.** Arm 0 reproduces the registered
rung 1 exactly: first-solve initial residuals equal to
`verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam` with
**0 mismatches over at least 885 comparisons**; `rc = 134`; abort at **iteration 148** with
`Negative initial temperature T0: -2.384321367`; **and the six on-disk `T_max`/`T_min` pairs of
the §2.3 table reproduced to every printed digit.** *If `P0` fails, this lane's harness is the
variable, arms 1 and 2 are **VOID**, and no classification is reported from either.*

**`P1` — ARM 1 IS EXONERATED.** `i_gen(1) <= 37` **and** `S20(1) > 1.641186`. *Fails if arm 1
is MITIGATED or REMOVED — i.e. if making the implicit energy convection first order actually
delays or removes the excursion. That is a live possibility: first-order upwind is strongly
diffusive and the supervisor's downgrade of this candidate is a reading of a dictionary, not a
measurement.*

**`P2` — ARM 2 IS EXONERATED.** `i_gen(2) <= 37` **and** `S20(2) > 1.641186`. *Fails if
matching `rho`'s relaxation to `p`'s delays or removes the excursion.*

**`P3` — ARM 1 BARELY MOVES THE MAGNITUDE.** `|S20(1) - 3.282372| / 3.282372 < 0.20`, i.e.
`S20(1)` lies in `[2.625898, 3.938846]`. *This is deliberately riskier than `P1`. First-order
upwind on the energy equation is a large numerical change and a span ratio is sensitive; a
20 % band is easy to miss. If `P3` fails while `P1` holds, the scheme has a measurable but
non-curative effect, and that is a finding in its own right.*

**`P4` — ARM 2 MOVES THE MAGNITUDE MATERIALLY.** `|S20(2) - 3.282372| / 3.282372 >= 0.20`,
**in either direction.** *Basis: a 6x change in a primary relaxation factor that enters the
mass flux producing under 20 % change in a field-span diagnostic would be surprising. It may
move it the WRONG way — a less heavily under-relaxed `rho` may diverge faster. The prediction
is about magnitude, and the direction is **not** predicted and will be reported as measured.*

**`P5` — AT LEAST ONE OF ARMS 1, 2 DIES DIFFERENTLY FROM THE CONTROL.** At least one of them
has an abort iteration other than 148, or an `rc` other than 134, or reaches `endTime 148`
without aborting. *Fails if both arms abort at exactly iteration 148 with `rc = 134`, which
would say the levers changed the trajectory not at all.*

**`P1` through `P5` are independent and any of them may fail without voiding any arm. Only
`P0` voids.** **A failed prediction is reported as a finding in its own words and is not
reframed.**

### 5.1 `L1` — LEVER-EFFECT CONTROL (a hard control, not a prediction)

Each of arm 1 and arm 2 **must** produce a first-solve residual series that **differs** from
arm 0's. **If an arm's residuals are identical to arm 0's, the dictionary edit did not reach
the solver and THAT ARM IS VOID** — its classification is not reported and the failure is
reported instead. This control also serves as the **positive control for the residual
comparator itself**: the comparator is shown returning a non-zero mismatch count on live data
in the same run in which it returns zero for arm 0.

### 5.2 `L2` — THE PLANTED-ZERO CONTROL (standing rule 3)

Every `T_max`, every `T_min`, every "did not cross" and every `NONE` below rests on a reader
shown able to see a value that is really there. The control plants a known perturbation into a
`T` field **written by this probe's own run**, reads it back **through the same reader that
produces every number in the results**, and **REFUSES (exit non-zero)** if the reader cannot
see it. **Arms, all six required to pass:**

1. **negative** — the unplanted original contains neither plant value;
2. **positive (min side)** — a planted `-7.654321e+09` is returned by the reader;
3. **positive (max side)** — a planted `+9.876543e+09` is returned by the reader;
4. **localisation** — each plant is reported at the **exact cell index** it was placed in;
5. **cell count preserved** — the planted read returns the same cell count as the clean read;
6. **extremum relocation** — `min()` relocates to the negative plant **and `max()` relocates
   to the positive plant.**

**Arm 6's max-side limb is an addition to the model probe's control set and it is required
here, not optional: this probe's primary reading is `T_max`, and a control that only exercises
`min()` would not have shown the reading path that every registered threshold is compared
against.** **A classification reported without a passing `L2` is void.**

## 6. COMPLETION — REPORTED, NEVER CLAIMED (standing rule 4)

Each arm is registered **to run to `endTime 148` or to abort, whichever comes first.** For an
aborting arm, standing rule 4's limbs cannot all hold and **no completed run is claimed.** For
each arm this probe reports, per limb and without adjectives: `rc`; whether an `End` line is
present; the last written time against `endTime`; whether the seven fields are present at the
last written time; and the `ExecutionTime` count against `endTime`. **An arm that reaches
`endTime 148` cleanly is still not a graded run** — it is a diagnostic under a registration
that grades nothing, and it produces no verdict.

**A crash or a bounded stop is `NOT A RESULT`, never `GATE FAIL`** — no gate is read here at
all, and standing rule 5 may only turn a `PASS` or a `GATE FAIL` **into** `NOT A RESULT`, never
the reverse.

## 7. ASSERTIONS AROUND EVERY ARM

Before **and** after each arm, in the **same shell invocation as the assertion**:

- `test -e` on each of `attempt2_medium_workshop_M0.734_a2.79`,
  `attempt2_fine_workshop_M0.734_a2.79`, `attempt2_medium_tape_M0.730_a2.79`,
  `attempt2_medium_farfield2x_M0.734_a2.79` under `verification/runs/F12_runs/` —
  **each must be ABSENT; the runner aborts if any exists or appears.**
- A recursive sha256 fingerprint of
  `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/` — **unchanged before and
  after; the runner aborts otherwise.**
- The target case directory must **not already exist**; the runner **refuses** a directory in
  which `0/` or any time directory is already present (standing rule 4's guard).

**`launch_f12_rung.py` and its `rate_calibration_gate()` are not invoked, not imported, not
read around and not edited by any part of this probe.** An interlock that can be edited when
it fires is not an interlock.

**No GCI, observed order or Richardson value is computed, quoted or read from anywhere in this
probe, and `sdk/workflows/tmr_verification.py` is not used.**

## 8. COST — REGISTERED BEFORE THE RUN (standing rule 12)

**Basis: the terminal-departure probe's own MEASURED figure for this exact workload** — 148
iterations, 147 ascii field writes, 23,040 cells, 1 rank: **25.333804 s wall = 0.422230
core-min** (`verification/runs/F12_runs/terminal_departure_2026-08-25/evidence/WALL_S.txt`).
*Applying that probe's own calibration lesson: a workload is priced from a measurement of the
same workload, not from a predecessor's estimate of a different one.*

| item | figure |
| --- | --- |
| Arm 0 solver + writes, PREDICTED | **0.4222 core-min** |
| Arm 1 solver + writes, PREDICTED | **0.4222 core-min** |
| Arm 2 solver + writes, PREDICTED | **0.4222 core-min** |
| Reader, PREDICTED | **0.0300 core-min** — the model probe's reader measured **1.08 s** walking 147 `T` fields plus 147 `p` fields; this reader walks `T` only, for three arms (441 field reads vs 294), so 1.08 x 1.5 = 1.62 s, rounded up |
| `L2` planted control, PREDICTED | **0.0100 core-min** — one field copied, edited and re-read |
| **TOTAL, PREDICTED** | **1.31 core-min**, 1 rank, serial |
| **CAP** | **10 core-min — a RUNAWAY GUARD, not a budget gate.** Sanaa lifted cost constraints (2026-08-25). **A breach is REPORTED TO THE SUPERVISOR, who decides. This lane does not extend a cap itself and does not stop work to save money.** |
| dollars | **$0.00112 DERIVED, NOT MEASURED**, at $0.0513/core-h (owner-stated 2026-08-21/22; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| disk, transient, outside git | ~1.6 GB (3 x 535 MB measured), on a volume with 289 GB free |

**Ranks = 1 per arm, run SERIALLY.** Two other cfd lanes are working and the box carries three
`buoyantBoussinesqSimpleFoam` processes belonging to heat-transfer. **No process this lane did
not start is touched, reniced or killed.** Serial single-rank execution also keeps contention
out of the comparison between arms, which is the whole point of the control.

**Estimate-versus-actual calibration is owed at completion** (standing rule 12, Sanaa's
directive of 2026-08-23): actual core-minutes from `WALL_S` files, dollars derived at the rate
above and labelled derived, the ratio actual/predicted, attribution of the gap, and waste named
separately — as a row in `docs/COST_CALIBRATION.md`.

## 9. WHAT THIS DOCUMENT DOES NOT DO

It does not authorise any F12 rung. It does not regrade rung 1. It does not unblock rung 2 or
touch its interlock. It does not alter admission gate A or B, Gates 1-4, any threshold
(0.08, 0.04, 0.020 chord, 5 %, 20 %, 70 deg, skewness 4), any cap in
`verification/campaign/F12_PREREGISTRATION.md` §5, any label, any cell count, either
condition, or any of its four predictions. **No frozen file is edited.** The `N-C4` ruling
that a scheme-order change is a change of experiment is applied, not amended.

**HONEST SCOPE OF THIS FREEZE. It is NOT blind.** This lane read the terminal-departure
probe's committed results, including the full 147-row `T_max`/`T_min` track, before writing
this document, and the control values in §2.3 are quoted from it. This freeze therefore does
**not** carry standing rule 2's full evidentiary content that the criteria could not have been
chosen to fit the answer **for arm 0**, whose outcome is already known. **It carries that
content in full for arms 1 and 2, whose outcomes are not known to anyone**: the thresholds
`342.3309915963 K`, `38`, `1.641186` and `[2.625898, 3.938846]`, the classification rule, the
joint-outcome wording and the five predictions are all fixed and committed **before either arm
executes**, and `P1` through `P5` can each fail.

**The supervisor's check-4 (`SUPERVISION_CHARTER.md` §3) has NOT been performed on this
document at the time of its commit.** It is committed by the lane before compute because
standing rule 2 requires the artifact to exist first; the supervisor's personal verification
that the commit exists is his and has been requested. **No agent message authorises anything,
and this document is an agent's work product, not consent** (standing rule 9).
