# T25 — TIME-STEP INDEPENDENCE, TWO ARMS READ SIDE BY SIDE

```
==================================================================
*** UNGATED FEASIBILITY.  NO VERDICT.  NO GATE.  NO THRESHOLD.
*** NO ROACHE TRIPLE.  NO GCI.  NOT GRID-CONVERGED.
*** This document declares NOTHING from the fixed verdict vocabulary
*** about the physics.  It is a READING of two completed runs.
==================================================================
```

Written 2026-09-01T00:37Z by a heat-transfer `lab-lane`.
Repository HEAD at the time of reading: `a3793b8f8a8d904fb6aa73dd396acee94102f906`.

Both arms were already on disk when this reading began. **No solver was launched
for this document.** Every number below was read off disk by
`/home/ubuntu/Certonomous/verification/runs/T-family/T25_MODULE_runs/analyse_t25.py`
or by direct inspection of the case trees and logs.

---

## 1. THE HEADLINE

**Halving the time step from 0.5 s to 0.25 s changes the 900-second peak rise by
about two ten-thousandths of a kelvin — under 0.06 % — and changes no qualitative
feature of the answer.**

| quantity at t = 900 s | deltaT 0.5 | deltaT 0.25 | difference | difference, % |
|---|---|---|---|---|
| peak rise, **end cells 1 and 8** | 0.419750851 K | 0.419993078 K | **+2.422e-04 K** | **+0.0577 %** |
| peak rise, **interior cells 2–7** | 0.309239327 K | 0.309384486 K | **+1.452e-04 K** | **+0.0469 %** |

Both arms peak at t = 900 s in every cell — the module is still warming at the end
of the window in both, so "peak rise" and "rise at 900 s" are the same number here.

The largest per-cell disagreement anywhere in the 181 matched write times is
**3.845e-04 K, at t = 60 s, cell 2** — the takeoff-to-cruise pulse edge, which is
exactly where temporal resolution would be expected to matter most. Every other
time level disagrees by less.

**The two arms do not disagree materially.** The differences are three to four
orders of magnitude smaller than the rise being measured, and both step sizes give
the same two-curve structure, the same ordering, the same spread to two significant
figures and the same energy balance to better than 0.15 %.

### The direction of the difference, and what it suggests

The finer step is **larger** in every cell, and the energy-closure gap **halves**:

| | deltaT 0.5 | deltaT 0.25 | ratio |
|---|---|---|---|
| unaccounted energy | 0.145859 % | 0.073031 % | **1.997** |

A gap that halves when the step halves is what a **first-order-in-time**
discretisation error looks like, and Euler-implicit time integration is
first order. Two independent quantities point the same way: the closure gap scales
as `dt^1` to within 0.15 % of a clean factor of two, and the per-cell temperatures
move monotonically upward toward a limit.

**This is an observation, not a measured order of convergence.** An observed order
`p` cannot be computed from two levels — it needs a third, and none exists.
**No GCI is quoted anywhere in this document** and none may be derived from it: rule
5 requires a converging triple, and there is no triple. If one *assumes* p = 1
(assumption, not measurement), a two-level Richardson extrapolation puts the
zero-step limit near 0.420235 K for the end cells and 0.309530 K for the interior,
leaving the deltaT 0.25 arm about 2.4e-04 K and 1.5e-04 K short of it respectively.
Those two numbers are **estimates resting on an unverified assumption** and are
recorded here so that nobody has to re-derive them from a footnote — they are not
results and carry no verdict.

---

## 2. THE TWO ARMS

| | `T25_MOD_L1` | `T25_MOD_L1_DT025` |
|---|---|---|
| case dir | `/home/ubuntu/Certonomous/verification/runs/T-family/T25_MODULE_runs/T25_MOD_L1` | `/home/ubuntu/Certonomous/verification/runs/T-family/T25_MODULE_runs/T25_MOD_L1_DT025` |
| deltaT | 0.5 s | 0.25 s |
| registered steps to endTime | 1800 | 3600 |
| endTime | 900.0 s | 900.0 s |
| writeInterval | 5.0 s | 5.0 s |
| time directories written | 181 | 181 |
| solver | `chtMultiRegionFoam` | `chtMultiRegionFoam` |
| region | `module`, solid only | `module`, solid only |
| mesh | 960 cells | 960 cells, **the same mesh** |
| ran (UTC) | 2026-08-31T23:31:23 → 23:31:24 | 2026-09-01T00:32:33 → 00:32:34 |

### The arms differ in the time step and in nothing that the solver reads

Claimed by `T25_MOD_L1_DT025/CASE.txt` and **checked here rather than believed**.
A recursive comparison of `system/`, `constant/` and `0.orig/` between the two trees
returns exactly two differing files:

- `system/controlDict` — one line: `deltaT 0.5;` against `deltaT 0.25;`. This is the
  intended difference and the only executable difference in the whole pair.
- `constant/module/fvOptions` — **comment text only.** Both files carry the same
  Function1 heat-source table with the same breakpoints; the DT025 copy restates the
  pulse-ramp sampling argument for its own step size. With `/* */` and `//` comments
  stripped and whitespace normalised, the two `fvOptions` files are **byte-identical**
  (SHA-256 of the stripped text `848e7eb6313c4730…` on both, 339 characters each).

`constant/module/polyMesh/points` has the same MD5 (`ee5ad3578fc7fb862ad5a49b044c3cb7`)
in both arms: **one mesh, two step sizes.**

**Minor defect, recorded not repaired:** the appended block in
`T25_MOD_L1_DT025/CASE.txt` says the two cases "differ in `system/controlDict`
`deltaT` and in nothing else." Taken literally that is false — `fvOptions` differs
too. Taken as a claim about what the solver reads it is true, and this section is the
check that makes it true. `CASE.txt` is not edited here (rule 6); the correction lives
in this record.

---

## 3. COMPLETION VERIFICATION — CLAUSE BY CLAUSE, PER ARM

CLAUDE.md rule 4, every clause, measured for each arm separately.

The clause rule 4 states as "`ExecutionTime` count == `endTime`" is a shorthand that
is only literally true at deltaT 1. **The operative test is the registered step
count** — precedent `T20_LC_c`, 750 steps against `endTime` 4500. Both arms are
tested against the step count `CASE.txt` registers for them.

The field list is **the one this case registers, measured not inherited**:
`CASE.txt` under "RULE 4 COMPLETION" fixes it at exactly **`{T, p}`** and says in
terms that the thermal-family default `T U p_rgh alphat nut k omega` does **not**
apply, because there is no fluid region and those fields must not exist.

| clause | `T25_MOD_L1` | `T25_MOD_L1_DT025` |
|---|---|---|
| `rc = 0` | **PASS** — `rc=0` in `STATUS.T25_MOD_L1` | **PASS** — `rc=0` in `STATUS.T25_MOD_L1_DT025` |
| exactly one `End` line | **PASS** — 1 exact-match line in `log.solve`, 1 line beginning `End` | **PASS** — 1 and 1 |
| last time == registered `endTime` 900 | **PASS** — last `Time =` is 900; `controlDict endTime 900.0` | **PASS** — last `Time =` is 900; `controlDict endTime 900.0` |
| registered fields at `900/module/` | **PASS** — `{T, p}` present, nothing missing, nothing extra | **PASS** — `{T, p}` present, nothing missing, nothing extra |
| `ExecutionTime` count == registered step count | **PASS** — 1800 `ExecutionTime` lines against registered 1800; 1800 `Time =` lines corroborate | **PASS** — 3600 against registered 3600; 3600 `Time =` lines corroborate |
| **AGE GUARD** — every field at 900 newer than this case's own `0/module/T` | **PASS** — see below | **PASS** — see below |

### The age guard, in full, per arm

The datum is each case's **own** `0/<region>/T`, which `run_one_t25.sh` copies from
`0.orig`, then `sleep 1`, then `touch`es **last** before the solver starts, precisely
so that it dates the run allowed to produce the answer.

| arm | reference `0/module/T` mtime | `900/module/T` | `900/module/p` | verdict |
|---|---|---|---|---|
| `T25_MOD_L1` | 1788219083.676100 | 1788219084.499107 (**+0.823 s**) | 1788219084.499107 (**+0.823 s**) | both NEWER — **PASS** |
| `T25_MOD_L1_DT025` | 1788222753.411438 | 1788222754.836450 (**+1.425 s**) | 1788222754.835450 (**+1.424 s**) | both NEWER — **PASS** |

No field at 900 is older than or equal to its own case's `0/module/T` in either arm.

### Supporting facts, checked at the same time

- `FOAM FATAL` occurrences in `log.solve`: **0** in both arms.
- The launcher captures `rc` from the solver **inside** the wrapper —
  `run_one_t25.sh:120-121` runs `timeout … chtMultiRegionFoam` in the foreground and
  takes `RC=$?` from it directly. It is not the exit status of a `setsid` line.
  `T25_MOD_L1_DT025/STATUS.queue.T25_MOD_L1_DT025` is explicitly labelled
  `launcher_rc=0 … note=exit-status-of-the-launch-argv-NOT-the-solver-rc`, so the two
  are not confused.
- No `RC.txt`-style file exists in either case directory. The solver `rc` lives in the
  `STATUS.<case>` file at the campaign root and nowhere else; that is stated here so
  that a future check looking for a filename that does not exist does not report an
  absence as a fact about the world.
- Per-step function-object output corroborates the step counts independently of the
  log: `postProcessing/module/moduleMinMax/0/fieldMinMax.dat` has **1802** lines in the
  0.5 arm and **3602** in the 0.25 arm — 1800 and 3600 per-step rows plus two header
  lines each.

### One count in the dispatch brief did not reproduce

The brief that commissioned this reading gave `T25_MOD_L1_DT025` **182** time
directories. **Measured: 181**, the same as the baseline, by the reader's own
`times_of()` rule (a directory whose name matches `[0-9]+(\.[0-9]+)?`). The likely
origin of 182 is counting `0.orig`, which is not a time directory. Both arms write on
the same `writeInterval` 5.0 s to the same `endTime` 900, so 181 (0 through 900
inclusive) is the count both arms should have and both do. This changes nothing in
the comparison — the reader compared 181 matched time levels out of 181 — but a count
that does not reproduce is reported rather than quietly corrected.

---

## 4. THE READER, AND ITS PLANTED CONTROL

Reader: `/home/ubuntu/Certonomous/verification/runs/T-family/T25_MODULE_runs/analyse_t25.py`.
`__pycache__` was cleared before the first run and `PYTHONDONTWRITEBYTECODE=1` set for
all runs, so no stale bytecode could invert the readings.

### The geometry guard did not refuse

`analyse()` refuses (`sys.exit`) unless the mesh matches the registered geometry
**four ways**. It refused neither arm; the four measured quantities were:

| guard | required | measured, both arms |
|---|---|---|
| cell count | 960 | 960 |
| total volume | 8 × 0.1 × 0.03 × 1.0 = 0.024 m³ | 0.024000 m³ |
| channel-face area | (2×8 − 2) × 0.1 × 1.0 = 1.4 m² | 1.4000 m², over 280 faces |
| mesh cells per module cell | 120 in each of the 8 | 120 in each of the 8 |

Everything above is computed **from `constant/module/polyMesh`**, not from the
builder's constants; the builder's constants are used only as the assertions the guard
tests against.

### Planted control — rule 3, run on each arm separately

`--selftest` copies the case, plants **+1.000000 K on all 960 internal temperatures at
t = 900 s**, and re-reads the perturbed tree **through the same parser**, refusing if
the reader cannot see it.

| arm | planted | reader saw, per-cell mean | stored energy seen | expected | result |
|---|---|---|---|---|---|
| `T25_MOD_L1` | +1.000000 K | **+1.000000 K** | **+60000.0000 J** | +60000.0000 J | **PLANT SEEN** |
| `T25_MOD_L1_DT025` | +1.000000 K | **+1.000000 K** | **+60000.0000 J** | +60000.0000 J | **PLANT SEEN** |

Acceptance is tight — `abs(d_mean − 1.0) < 1e-9` and `abs(d_E − expected) < 1e-6` —
and a failure is a hard refusal, not a warning. Both arms passed. The small numbers
in this document are therefore numbers from a reader that has been **shown able to see
a non-zero on the very case it is reading**, on both arms, and not merely on one of
them.

---

## 5. THE FULL SIDE-BY-SIDE READING

### 5.1 Per-cell peak rise above 293 K, all eight cells

Peak over the whole history; in both arms every cell peaks at t = 900 s.

| cell | deltaT 0.5, K | deltaT 0.25, K | difference, K | difference, % |
|---|---|---|---|---|
| 1 | 0.419750851000 | 0.419993078167 | +2.422e-04 | +0.0577 |
| 2 | 0.309239326667 | 0.309384486000 | +1.452e-04 | +0.0469 |
| 3 | 0.309239326667 | 0.309384486000 | +1.452e-04 | +0.0469 |
| 4 | 0.309239326667 | 0.309384486000 | +1.452e-04 | +0.0469 |
| 5 | 0.309239326667 | 0.309384486000 | +1.452e-04 | +0.0469 |
| 6 | 0.309239326667 | 0.309384486000 | +1.452e-04 | +0.0469 |
| 7 | 0.309239326667 | 0.309384486000 | +1.452e-04 | +0.0469 |
| 8 | 0.419750851000 | 0.419993078167 | +2.422e-04 | +0.0577 |

Peak in absolute terms: 293.419751 K (20.2698 °C) end cells and 293.309239 K
(20.1592 °C) interior at deltaT 0.5; 293.419993 K (20.2700 °C) and 293.309384 K
(20.1594 °C) at deltaT 0.25.

### 5.2 The two curves, and whether the within-group agreement survives

There are **two distinct curves and only two**, in both arms:

- **end cells 1 and 8** — against the adiabatic casing, cooled on **one** face;
- **interior cells 2–7** — cooled on **two** faces.

That structure is the module's geometric asymmetry and nothing else; `CASE.txt` says so
on its face, and this reading does not extend it.

**The within-group agreement is not merely six-decimal at deltaT 0.25 — it is exact.**
Tested at full float precision rather than at printed precision:

| arm | cells 1 and 8 bitwise identical | max &#124;Δ&#124; within the end group | cells 2–7 all bitwise identical | max spread within the interior group |
|---|---|---|---|---|
| deltaT 0.5 | **yes** | 0.000e+00 K | **yes** | 0.000e+00 K |
| **deltaT 0.25** | **yes** | **0.000e+00 K** | **yes** | **0.000e+00 K** |

So the answer to the question asked is: **yes, and stronger than asked.** Halving the
step did not degrade the symmetry — the six-decimal agreement holds at deltaT 0.25
because the underlying agreement is exact to the last bit of the double, in both arms.
This is the expected consequence of a symmetric mesh, a symmetric source and identical
boundary conditions on every interior cell, and it is worth stating that the exactness
is a property of the *problem's symmetry*, not evidence about the *time integration*.

### 5.3 Spread (hottest minus coldest cell, volume-average)

| t, s | deltaT 0.5, K | deltaT 0.25, K |
|---|---|---|
| 0 | 0.000000 | 0.000000 |
| 30 | 0.000609 | 0.000605 |
| 60 | 0.002365 | 0.002356 |
| 120 | 0.007328 | 0.007333 |
| 300 | 0.026258 | 0.026297 |
| 600 | 0.066185 | 0.066262 |
| **900** | **0.110512** | **0.110609** |

**Spread at 900 s: 0.110511524 K against 0.110608592 K — a difference of
+9.707e-05 K, or +0.0878 %.** The maximum spread over the history is the 900 s value
in both arms.

Module point min/max rise at 900 s: 0.295253 / 0.449031 K at deltaT 0.5;
0.295391 / 0.449292 K at deltaT 0.25 — the hottest point in the module moves by
+2.610e-04 K between the arms.

### 5.4 Energy closure

All three terms are measured independently: the input from the registered duty cycle,
the stored energy as `rho·cp·V·(T−293)` summed over all 960 mesh cells, and the removal
as `h·A·(T_face−293)` integrated trapezoidally over the 181 write times.

| term | deltaT 0.5 | deltaT 0.25 |
|---|---|---|
| heat in, from the duty cycle | 34080.0000 J | 34080.0000 J |
| stored in the cells at 900 s | 20212.0325 J | 20222.1980 J |
| removed through the channel faces | 13818.2587 J | 13832.9130 J |
| accounted for | 34030.2912 J | 34055.1110 J |
| **CLOSURE** | **99.854141 %** | **99.926969 %** |
| unaccounted | 0.145859 % | 0.073031 % |

Both close to better than 0.15 %; the finer step closes to better than 0.08 %. The
ratio of the two gaps is 1.997 — see §1.

### 5.5 Final removal rate at 900 s

| | deltaT 0.5 | deltaT 0.25 | difference |
|---|---|---|---|
| removal rate at 900 s | **22.123034 W** | **22.133798 W** | +0.010764 W (+0.0487 %) |
| as a fraction of the 32.0 W cruise input | **69.1345 %** | **69.1681 %** | +0.0336 pp |

The module is removing roughly 69 % of the cruise heat input at the end of the window
in both arms — that is, it is still storing the balance and still warming at t = 900 s.
The window ends before steady state; that is a property of the registered 900 s
duration, and it is identical between the arms.

---

## 6. WHAT THIS COMPARISON ESTABLISHES, AND WHAT IT DOES NOT

### It establishes

Within this one case, on this one mesh, with this one solver configuration and this one
900-second window, **the reported quantities are insensitive to the time step at the
0.5 s / 0.25 s level to better than 0.09 % on every quantity read.** The baseline
deltaT 0.5 arm is not being carried by its step size, and its numbers would not have
been meaningfully different had it been run at half the step.

### It does NOT establish grid independence

**One mesh. Both arms.** `constant/module/polyMesh/points` is byte-identical between
the two cases (same MD5, §2). Nothing here says anything whatever about spatial
discretisation error. The 960-cell mesh is a **chosen** mesh — `CASE.txt` marks it
`CHOSEN`, not derived and not converged — and no coarser or finer mesh exists for this
case. **Any statement of the form "T25 is grid-converged" or "T25's mesh is adequate"
would be unsupported by this document and by anything else currently on disk.**

### It does NOT make this a gated result

**T25 is UNGATED FEASIBILITY and carries no verdict.** There is no pre-registration,
no gate, no threshold, no band and no label for any quantity here, and none may be
invented after the fact from these numbers. `CASE.txt` says so on its face; the queue
entries say so (`tag: FEASIBILITY`, `gated: false`,
`prereg_status: NONE -- UNGATED FEASIBILITY RUNG`), resting on Sanaa's feasibility-first
ruling at `etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md` §1; and
`analyse_t25.py` says so in its own header. **No word from the fixed verdict vocabulary
is applied to the physics anywhere in this document.** The `PASS` entries in §3 attach
strictly to the rule-4 completion clauses — a statement about whether the runs finished,
not about whether their answers are right.

### Other things it does not establish

- **Not a Roache triple and not a GCI.** Two levels in time, one in space; there is no
  triple, so rule 5's machinery does not apply and is not invoked. No GCI appears in
  this document.
- **Nothing about the coolant channel.** The channels are not meshed in either arm —
  `CASE.txt` SIMPLIFICATION 1. The convective coefficient `h = 53.9 W/m²K` is derived
  from Dittus-Boelter, declared representative, **not measured and not validated**.
  Neither arm says anything about channel flow, outlet coolant temperature, or the
  laminar-vs-SST model-form sensitivity.
- **Nothing about anisotropic conduction.** Both arms use the directive's own stated
  isotropic fallback `kappa = 3.0 W/mK`, not the registered in-plane 25 /
  through-plane 1 (SIMPLIFICATION 2).
- **Nothing about the plenums or cell-to-cell contact** (SIMPLIFICATIONS 3 and 4).
- **Nothing about the pulse edge below 1 ms.** Both arms step over the linear ramp in
  `(59.999, 60.000)` without landing inside it — the builder checks that count in exact
  decimal arithmetic and refuses to emit a case where it is non-zero. A step finer than
  1 ms would sample the ramp and the breakpoint placement would have to be revisited;
  **this comparison does not probe that regime.**
- **The agreement is between two arms of the same code, not against a reference.** No
  analytic solution, no experiment and no other code enters this document. Two step
  sizes agreeing is evidence about temporal discretisation and about nothing else — it
  would look exactly like this even if the physics setup were wrong in some way both
  arms share.

---

## 7. COST

The unit is core-minutes (wall s × ranks ÷ 60), CLAUDE.md rule 12.

| | registered POINT | registered CAP | actual | actual/predicted |
|---|---|---|---|---|
| `T25_MOD_L1` | **1.0 core-min** | **10.0 core-min** | **0.017 core-min** | ≈ 0.017, i.e. ~59× over-predicted |
| `T25_MOD_L1_DT025` | 2.0 core-min | 10.0 core-min | **0.017 core-min** | ≈ 0.0083, i.e. ~118× over-predicted |
| **both arms together** | — | — | **0.034 core-min** | — |

The baseline's POINT 1.0 / CAP 10.0 is registered in
`verification/queue/heat-transfer/refused/T25_MOD_L1.json`; the DT025 arm's POINT 2.0 /
CAP 10.0 in `verification/queue/heat-transfer/launched/T25_MOD_L1_DT025.json`
(`cost_core_min_estimate`, `cap_core_min_registered`, `cost_basis`), both fixed before
their respective launches. Neither arm approached its cap: 1 wall s against a 600 s
timeout and against a 1200 s timeout respectively. `capped=no`, `note=clean` on both.

At $0.0513/core-h the two arms together are **$2.9e-05 DERIVED, NOT MEASURED** — the
rate is reported-by-owner (Sanaa 2026-08-21/22) and the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**THESE FIGURES ARE PRECISE TO NO BETTER THAN THEIR OWN MAGNITUDE.** `ClockTime` prints
as an integer second and the `STATUS` timestamps are also 1-second resolution, so a
1-second run carries **±1 s quantisation, which is ±100 % on this number**. The
per-arm 0.017 core-min and the 0.034 core-min total should be read as order-of-magnitude
figures, not measurements. This is the same caveat the baseline's own calibration row
carries at `docs/COST_CALIBRATION.md:347`, and it applies unchanged to the second arm.

A better-resolved but **different** time base exists and is deliberately not fused with
the above: final `ExecutionTime` is **0.77 s** for the 0.5 arm and **1.38 s** for the
0.25 arm (0.01 s resolution). That is CPU time, not wall, so it is not rule 12's basis;
it is admissible only as a lower bound on wall for these single-rank serial runs. Read
as a pair it is nonetheless informative, and it corroborates the calibration lesson the
baseline row already drew: **2× the steps cost 1.79× the `ExecutionTime`, not 2×**,
which is what an additive fixed startup term plus a per-step term looks like. Solving
the two-point system gives ≈0.16 s of fixed startup and ≈0.34 ms per step at 960 cells.
Offered as **consistent-with, not proven** — two points, on a CPU-time base, at the
instrument's resolution floor.

**Calibration owed.** Rule 12's estimate-versus-actual clause and the DT025 entry's own
`calibration_owed` field require a row in `docs/COST_CALIBRATION.md` for
`T25_MOD_L1_DT025`. The baseline has one (`docs/COST_CALIBRATION.md:347`); **the DT025
arm does not yet, and this document does not create it.** It is flagged here so it can
be dispatched rather than forgotten.

---

## 8. HOW TO REPRODUCE THIS READING

```
cd /home/ubuntu/Certonomous/verification/runs/T-family/T25_MODULE_runs
find . -name __pycache__ -type d -exec rm -rf {} +
export PYTHONDONTWRITEBYTECODE=1
python3 analyse_t25.py --case-dir <case> --selftest
```

for `<case>` in `T25_MOD_L1` and `T25_MOD_L1_DT025`. `--selftest` runs the planted
control first and then the full reading. The differences in §1 and §5 are the two
readings subtracted; the full-precision values are printed by `analyse()` at six
decimals and were taken here from the returned `percell` list at double precision.
