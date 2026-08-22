# T3 ext1: extension of the ladder from `latestTime`

**Dated addendum under Charter §2b clause 2. Written 2026-08-22, after first
compute on T3.** It alters no gate, no threshold, no cap and no label. The
original verdict — `PASS 0, GATE FAIL 0, NOT A RESULT 4, BLOCKED 0` from the
frozen comparator at `gate_t3.json` — stands beside it, unamended, and is
restated in §7 below. This document adds iterations and a marking tool; it
adds nothing else.

The route taken is the one T3_PREREGISTRATION.md §5 registered before any case
existed: *"a case that has not converged at 20 000 may be **extended** from
`latestTime` under the T1b section 6 disclosure rule (new log, new STATUS,
first extension `Time` exactly `endTime + 1`, marker re-judged across both
segments); the decision to extend is taken on the convergence state alone and
never with a `St` in view."* T3_RESULTS.md §10.1 repeats it and adds: *"This
report takes no such decision and runs nothing."* This document takes it.

---

## 1. The Charter §2b clause 2 condition, checked with a timestamped command

Clause 2 permits a dated addendum after first compute provided the addendum
alters no gate, threshold, cap or label, and provided the thing it adds does
not already exist in a form that could have been chosen with an outcome in
view. For an extension, the operative check is that **no extension has ever
run**: if an `ext1` log already existed, its `endTime` could have been picked
after seeing what the extension produced.

```
$ date -u +%FT%TZ
2026-08-22T17:41:39Z
$ cd /home/ubuntu/Certonomous/verification/runs/T-family/T3_runs
$ ls T3_runs/*/log.solve.ext1
ls: cannot access '*/log.solve.ext1': No such file or directory
$ echo rc=$?
rc=2
```

**Returns nothing, rc = 2.** No `log.solve.ext1` exists for any of the eight
cases. Every `endTime` in §3 was therefore fixed from the *pre-extension*
convergence state only. The eight case directories at that moment each held
exactly `0 0.orig 18000 20000` (`purgeWrite 2`), and every `system/controlDict`
read `startFrom latestTime; stopAt endTime; endTime 20000; deltaT 1;
writeInterval 2000; purgeWrite 2`.

**The `St` firewall.** T3_PREREGISTRATION §5 and T3_RESULTS §10.1 both require
the decision to be taken "on the convergence state alone and never with a `St`
in view". The only inputs to §2 and §3 below are: (a) the per-iteration
`Initial residual` history parsed out of each `log.solve`, and (b) the
`T`/`U` relative max-change column of T3_RESULTS §3, which is a convergence
measurement and carries no `St`. No `St`, `x_peak`, `x_R` or `Cf` number
entered the extrapolation, the decision rule, or the choice of any `endTime`.
The four graded rows have no value today — they read NOT A RESULT — so there
is no number an `endTime` could have been tuned toward.

---

## 2. The instrument: residual decay per case, over the last 5 000 iterations

The gate (T3_PREREGISTRATION §5) is on the **written field**: the largest change
of any cell value of `T`, and separately of `U`, between the checkpoints at
`18000` and `20000`, at most `1e-6` of that field's range. With `purgeWrite 2`
only two checkpoints survive, so that quantity has exactly **one** measurement
per case and cannot itself be trended. The per-iteration `Initial residual`
in `log.solve` is the only history on disk, and for a fixed-point iteration the
field increment over a fixed window and the equation residual decay at the same
rate; the residual is therefore used as the **extrapolator**, and the §3 field
measurement as the **starting offset**. This is stated plainly because it is an
assumption: if a case's residual decays but its field increment does not, the
extension will show that, and §6 registers the prediction that would fail.

**Method.** For each case and each of `Ux`, `Uy`, `T`: take the first
`Initial residual` of each field at each iteration; over iterations
`15000 < t <= 20000`, form ten blocks of 500 and take the **median** within
each block (the median, not the mean, so a limit cycle's spikes do not steer
the fit); least-squares fit `log10(residual)` against `t`. The slope `s` is
reported in **decades per 1 000 iterations** with its `R²`.

| case | `s(T)` | `R²` | `s(Ux)` | `R²` | `s(Uy)` | `R²` | `p_rgh` med @20000 | class |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `R_c` | −0.00000 | 0.000 | −0.00003 | 0.004 | +0.00012 | 0.048 | 1.37e−02 | **STALLED** |
| `R_m` | −0.17752 | 1.000 | −0.19552 | 0.997 | −0.15260 | 0.984 | 2.21e−07 | **DECAYING** |
| `R_f` | −0.05266 | 1.000 | −0.09560 | 1.000 | −0.01154 | 0.465 | 1.31e−07 | **DECAYING** |
| `P_m` | −0.17874 | 0.999 | −0.19552 | 0.997 | −0.15260 | 0.984 | 2.21e−07 | **DECAYING** |
| `C_lam_m` | +0.00991 | 0.068 | −0.01289 | 0.249 | −0.00646 | 0.444 | 4.50e−01 | **STALLED** |
| `W_m` | +0.00002 | 0.013 | −0.00000 | 0.044 | −0.00007 | 0.354 | 4.48e−04 | **STALLED** |
| `D_m` | −0.16596 | 0.995 | −0.01506 | 0.564 | −0.00650 | 0.555 | 3.05e−07 | **DECAYING** |
| `O_m` | −0.14680 | 0.999 | −0.15645 | 0.999 | −0.09137 | 0.970 | 3.19e−07 | **DECAYING** |

**The eight cases fall into two populations and the split is not marginal.**
Five fit a straight line in `log10(residual)` with `R² ≥ 0.97` and slopes
between `−0.05` and `−0.20` decades per 1 000 iterations. Three fit nothing at
all: their `R²` is between 0.004 and 0.44 and their slopes are within noise of
zero. There is no case in between.

**What the stalled cases look like, at 2 000-iteration resolution.** The
median `Initial residual` per 2 000-iteration block, from iteration 0 to 20 000:

```
R_c      p_rgh  1.91e-02 1.35e-02 1.37e-02 1.37e-02 1.37e-02 1.37e-02 1.37e-02 1.37e-02 1.37e-02 1.37e-02
R_c      T      7.73e-04 2.68e-05 1.47e-05 1.12e-05 1.07e-05 1.06e-05 1.06e-05 1.06e-05 1.06e-05 1.06e-05
C_lam_m  p_rgh  4.31e-01 4.49e-01 4.38e-01 4.32e-01 4.43e-01 4.55e-01 4.44e-01 4.65e-01 4.60e-01 4.50e-01
W_m      T      5.43e-05 7.17e-07 7.09e-07 7.09e-07 7.10e-07 7.09e-07 7.09e-07 7.09e-07 7.10e-07 7.10e-07
```

`R_c` reached `p_rgh = 1.37e-02` at iteration 4 000 and has not moved from it in
the 16 000 iterations since — three significant figures, unchanged, for
**80 % of the run**. `C_lam_m` never decayed at all: its `p_rgh` is *higher* at
20 000 than at 2 000. `W_m` reached `T = 7.09e-07` at iteration 4 000 and has
held it to three figures ever since, but at a level a thousand times below
`R_c`'s. `R_c` and `C_lam_m` are **limit cycles** (spread `p95/p05` in the last
5 000: `R_c` 1.1–1.4, `C_lam_m` 1.6–2.5, i.e. a stationary oscillation about a
fixed mean); `W_m` is a **floor** (spread 1.1, and its residuals are constant
to three figures — the linear-solver tolerance, not a flow oscillation).

For comparison, the five DECAYING cases are still marching: `R_f`'s `T`
residual fell `3.05e-04 → 1.12e-04 → 6.23e-05 → 2.47e-05 → 1.60e-05 → 1.22e-05
→ 9.16e-06 → 7.09e-06 → 5.56e-06 → 4.36e-06`, a clean geometric sequence to the
last block.

---

## 3. The decision rule, and the eight `endTime`s

**The rule, stated before it is applied.** For each case, for each **gated**
field (`T`; and `U`, whose rate is taken from the slower of `Ux`/`Uy`):

1. **Miss factor** `m_f` = (that field's relative max change at 20 000, from
   T3_RESULTS §3) ÷ `1e-6`. This is how many factors of ten the field increment
   must still fall.
2. If `m_f <= 1` the field is already inside tolerance and **imposes no
   requirement**, whatever its residual is doing.
3. Else if the field's fit has `R² >= 0.90` **and** `s <= −0.01` decades per
   1 000 iterations, it is **DECAYING**, and the iterations it needs are
   `N_f = 1000 · log10(m_f) / |s|`.
4. Else the field is **STALLED**: no finite `N_f` exists, because a flat
   residual extrapolates to `1e-6` at infinity.
5. The case's `N = max(N_f)` over the gated fields. A case with any STALLED
   gated field outside tolerance is a **STALLED case**.
6. `endTime` = `20000 + N`, **rounded up to the next multiple of the
   `writeInterval`, 2 000**, so the gate's two checkpoints land on the last two
   writes. **Capped at 80 000 total.**
7. **A STALLED case is run to the cap, 80 000.** Not because 80 000 is expected
   to converge it — the extrapolation says explicitly that it will not — but
   because that converts an extrapolation into a measurement, and
   T3_PREREGISTRATION §11 registered exactly this alternative outcome in
   advance: *"a steady RANS of a flapping shear layer may be in a limit cycle
   that no extension resolves, in which case the rung says so rather than
   averaging."* 60 000 further iterations at the cap is the strongest evidence
   this rung can produce for that sentence, and it costs USD 0.64 across the
   three of them (§5).

**The rule is applied. The result:**

| case | `T` rel @20000 | `m_T` | `s(T)` | `N_T` | `U` rel @20000 | `m_U` | `s(U)` slower | `N_U` | class | **`N`** | **`endTime`** | extra its |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `R_c` | 4.944e−02 | 49 440 | ~0 | **∞** | 1.524e−01 | 152 400 | ~0 | **∞** | STALLED | cap | **80 000** | 60 000 |
| `R_m` | 2.855e−05 | 28.6 | −0.17752 | 8 200 | 1.378e−04 | 137.8 | −0.15260 | 14 019 | DECAYING | 14 019 | **36 000** | 16 000 |
| `R_f` | 1.095e−03 | 1 095 | −0.05266 | **57 713** | 3.703e−03 | 3 703 | −0.09560 | 37 328 | DECAYING | 57 713 | **78 000** | 58 000 |
| `P_m` | 1.526e−05 | 15.3 | −0.17874 | 6 622 | 1.378e−04 | 137.8 | −0.15260 | 14 019 | DECAYING | 14 019 | **36 000** | 16 000 |
| `C_lam_m` | 6.000e−01 | 600 000 | ~0 (+) | **∞** | 1.189e+00 | 1 189 000 | ~0 | **∞** | STALLED | cap | **80 000** | 60 000 |
| `W_m` | 1.417e−06 | 1.42 | ~0 (+) | **∞** | 1.252e−06 | 1.25 | ~0 | **∞** | STALLED | cap | **80 000** | 60 000 |
| `D_m` | 1.893e−05 | 18.9 | −0.16596 | **7 696** | 1.246e−09 | 0.001 | (floor) | **0** | DECAYING | 7 696 | **28 000** | 8 000 |
| `O_m` | 9.622e−05 | 96.2 | −0.14680 | 13 510 | 1.915e−04 | 191.5 | −0.09137 | **24 976** | DECAYING | 24 976 | **46 000** | 26 000 |

Worked examples, so the arithmetic can be checked without rerunning anything:

* **`R_f`, the critical path.** `T` must fall from `1.095e−03` to `1e−06`, a
  factor of 1 095, i.e. `log10(1095) = 3.0394` decades. At `0.05266` decades
  per 1 000 iterations that is `3.0394 / 0.05266 × 1000 = 57 713` iterations.
  `20000 + 57713 = 77 713`, rounded up to the next multiple of 2 000 = **78 000**,
  which is inside the 80 000 cap with 2 000 to spare. `U` needs only 37 328, so
  `T` binds. `R_f` has the **slowest** `T` decay of the five decaying cases, by
  a factor of 2.8 against `O_m` and 3.4 against `R_m` — which is why the fine
  level is 38 × further from steady than the medium (T3_RESULTS §3) and why it
  needs 3.6 × their extension.
* **`D_m`, the shortest.** Its `U` relative change is `1.246e−09`, already
  **803 × inside** the `1e-6` tolerance, and its `Ux`/`Uy` residuals sit on a
  floor at `1.9e−10`/`3.4e−10` with `R² ≈ 0.56` — STALLED, but rule clause 2
  fires first and `U` imposes nothing. `T` alone binds: `log10(18.93) = 1.2771`
  decades at `0.16596` per 1 000 = `7 696` iterations → `27 696` → **28 000**.
  Without clause 2, `D_m` would have been sent to the cap for a field that is
  three orders of magnitude better converged than the gate demands.
* **`W_m`, the case that misses by 1.25 ×.** It is the closest of the eight and
  the most likely to be dismissed as "nearly there". It is not nearly there: it
  is **not moving**. Its `T` residual has read `7.09e−07` to three figures since
  iteration 4 000, and the fitted slope is `+0.00002` decades per 1 000 — the
  wrong sign, at `R² = 0.013`. To close a 1.42 × gap at that rate is not a long
  extension; it is an infinite one. `W_m` goes to the cap, and the honest
  prediction (§6) is that it will still miss.
* **`R_m` and `P_m` share `N_U`** because they are the same mesh and the same
  momentum problem — `P_m` differs only in `Pr_t` — and their `Ux`/`Uy`
  residual series are numerically identical. Only their `T` series differ
  (`N_T` 8 200 vs 6 622), and `U` binds on both. This identity is a check on the
  parser, not a coincidence.

**Total extra iterations across the eight: 304 000.** Highest `endTime` 80 000,
at the cap; lowest 28 000.

---

## 4. Report only: the `R_f` 8.23 % heat-balance miss against non-convergence

T3_RESULTS §5.2 records `R_f` closing its energy budget to **8.234 %** against
a governed **0.5 %**, while `R_c` and `R_m` on the same geometry close to
0.074 % and 0.090 %. This section **reports and does not act**: no `endTime` in
§3 was chosen from it, the heat balance is a Charter §2c GUARD counted in no
tally, and nothing below changes any gate.

The solver logs carry no `functionObject` output, so there is no outlet-flux
time series to read directly — the closure was computed by `analyse_t3.py` from
the *written fields*, not printed per iteration. Two things can be read:

**(a) Mass is not drifting; it is frozen.** `R_f`'s cumulative continuity error
reads `−7.0779e−04` at iteration 2 001, `−7.1920e−04` at 6 001, and
`−7.1919e−04` at 18 001 — constant to five figures over the last 12 000
iterations, and T3_RESULTS §5.2 records the mass imbalance as `−1.5e−14`
relative. **The 8.2 % is not a mass-flux drift.** Whatever is open in the
energy budget is not open in the mass budget.

**(b) The imbalance is a tight power law in the `T` residual — but only for the
cases that are still marching.** Taking each case's median `T` `Initial
residual` at 20 000 against its §5.2 imbalance:

| case | `T` residual @20000 | imbalance % | class |
| --- | ---: | ---: | --- |
| `P_m` | 5.436e−08 | 0.0382 | DECAYING |
| `D_m` | 5.758e−08 | 0.0212 | DECAYING |
| `R_m` | 1.018e−07 | 0.0900 | DECAYING |
| `O_m` | 3.606e−07 | 0.3458 | DECAYING |
| **`R_f`** | **3.984e−06** | **8.2340** | DECAYING |
| `W_m` | 7.104e−07 | 0.0082 | STALLED (floor) |
| `R_c` | 1.059e−05 | 0.0739 | STALLED (limit cycle) |
| `C_lam_m` | 3.402e−03 | 99.3200 | STALLED (limit cycle) |

Over the **five DECAYING cases** the least-squares fit is

> `imbalance % = 10^7.982 × (T residual)^1.308`,  **`R² = 0.986`**

across three decades of residual and 2.6 decades of imbalance, with `R_f` the
top point and on the line. **The two low-level STALLED cases sit far below that
line**: the fit predicts 30 % for `R_c` (observed 0.074 %, **400 × below**) and
0.88 % for `W_m` (observed 0.0082 %, **107 × below**).

That separation is the finding, and it has a mechanism. A steady energy balance
assumes no storage term. A case whose residual is *marching one way* still has
one — the field is systematically accumulating enthalpy — and the budget fails
to close in proportion. A case in a *stationary limit cycle* oscillates about a
fixed mean and carries **no net storage**, so its budget closes even though its
residual is large: `R_c`'s `T` residual (`1.06e−05`) is **2.7 × larger than
`R_f`'s** and yet it closes 111 × better. Residual magnitude alone does not
predict the imbalance; residual *magnitude in a case that is still moving*
does, at `R² = 0.986`.

**Conclusion, report only: the `R_f` 8.23 % is consistent with non-convergence
and is not evidence of a mesh, discretisation or boundary-condition fault on
the fine level.** It sits on a relation defined by four other cases that differ
from it only in how far along the same transient they are. It is a prediction
in §6, not a conclusion here: if `R_f`'s balance does **not** close as its
residual falls, this paragraph is wrong and the fine level has a real fault.

---

## 5. Cost, predicted **before launch**

Measured throughput per case in cell-iterations per core-second, from
T3_RESULTS §9 — the *measured* rates, not the pre-registration's `4.0e5`
planning figure, which §9 found to be 1.5–5.2 × optimistic and steeply
cell-count dependent. `nProcs = 1`, serial, **USD 0.0513 per core-hour**.

`core-s = extra iterations × cells ÷ measured rate`.

| case | cells | measured cell-it/core-s | extra its | core-s | core-h | USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `R_c` | 36 000 | 2.20e5 | 60 000 | 9 818 | 2.727 | 0.140 |
| `R_m` | 92 160 | 1.16e5 | 16 000 | 12 712 | 3.531 | 0.181 |
| **`R_f`** | 235 520 | **7.73e4** | 58 000 | **176 716** | **49.088** | **2.518** |
| `P_m` | 92 160 | 1.16e5 | 16 000 | 12 712 | 3.531 | 0.181 |
| `C_lam_m` | 92 160 | 1.79e5 | 60 000 | 30 892 | 8.581 | 0.440 |
| `W_m` | 28 160 | 3.78e5 | 60 000 | 4 470 | 1.242 | 0.064 |
| `D_m` | 79 360 | 1.50e5 | 8 000 | 4 233 | 1.176 | 0.060 |
| `O_m` | 128 000 | 9.56e4 | 26 000 | 34 812 | 9.670 | 0.496 |
| **total** | | | **304 000** | **286 364** | **79.55** | **4.08** |

**Predicted cost of the ext1 extension: USD 4.08 (79.55 core-hours).**

* The three STALLED cases run to the cap cost **USD 0.64** of that total, 16 %.
* `R_f` alone is **USD 2.52 and 62 %** of the compute. Serial, one core, its
  wall is **49.1 h ≈ 2.05 days**, and it sets the critical path. Every other
  case finishes inside 9.7 h. Under the same contention that made T3's measured
  wall 3.71 × its prediction, `R_f` could reach 3 days.
* Rung to date: **USD 2.07** spent (T3_RESULTS §9). Rung after ext1:
  **USD 6.15**, against the pre-authorised **USD 25** ceiling — **24.6 %** of it.
  T3_PREREGISTRATION §10 said "an extension of every case to 60 000 iterations
  would still be under 2 USD"; this extension takes three cases to 80 000 and
  `R_f` to 78 000 and lands at 4.08, **2.0 × that sentence**, for the reason §9
  of T3_RESULTS already identified: the measured throughput on the large meshes
  is 5.2 × worse than the plan's.

**The 10 × stop threshold.** If measured spend reaches **10 × 4.08 = USD 40.8
(795 core-hours)** the extension is stopped and reported as stopped. **That
threshold is not the binding one.** The rung's remaining pre-authorised budget
is `25.00 − 2.07 = ` **USD 22.93 (447 core-hours)**, which binds first, at
**5.6 ×** the prediction. The operative stop is therefore: **stop at USD 22.93
of ext1 spend, or at 10 × prediction, whichever comes first — i.e. USD 22.93.**
Wall is read from `STATUS_EXT1.<case>` and totalled on completion; a case still
running when the total crosses the threshold is stopped where it is and its
partial state reported, never graded.

---

## 6. Registered predictions, written before any extension iterates

Scored on the next comparator run. Written to be wrong in a recorded direction,
in the manner of T3_PREREGISTRATION §8.

**P1 — which cases reach `1e-6`.**
**The five DECAYING cases reach the criterion at their registered `endTime`:
`R_m` (36 000), `P_m` (36 000), `D_m` (28 000), `O_m` (46 000), `R_f` (78 000).**
Each is a direct read-out of the §3 extrapolation with no margin added beyond
the round-up to the `writeInterval`, so P1 is a genuine test of the log-linear
model: if the decay flattens at any point before the target, the case misses and
the model is falsified in a recorded direction. `R_f` is the most exposed — it
needs 57 713 iterations of continued decay, 2.4 × the longest anyone else needs,
and its `Uy` residual has *already* flattened (`R² = 0.465`, plateaued at
`6.6e−07` since iteration 14 000) even though `Ux` has not.

**The three STALLED cases do NOT reach it, even at 80 000: `R_c`, `C_lam_m`,
`W_m`.** For `R_c` and `C_lam_m` this is the limit cycle T3_PREREGISTRATION §11
named. For `W_m` — 1.25 × away, the closest of all eight — the prediction that
it still misses is the one most likely to look foolish and is registered
deliberately: its residual has been flat to three significant figures for 16 000
iterations, so 60 000 more should change nothing. **If `W_m` converges, the
"flat residual means a floor" reading in §2 is wrong** and the field increment
decays where the residual does not; that would be a real finding about the
instrument and is why P1 names `W_m` explicitly.

**P2 — the `R_f` heat balance.** **It closes below 0.5 %.** From the §4 fit,
0.5 % corresponds to a `T` residual of `4.63e−07`; `R_f` reaches that from
`3.98e−06` at `0.05266` decades per 1 000 in **17 755 iterations, i.e. at Time
≈ 37 800** — well inside the registered `endTime` of 78 000, so `R_f` should
already be under 0.5 % at the 38 000 checkpoint and far under it by 78 000. **If
`R_f`'s imbalance is still above 0.5 % at 78 000 with its `T` residual at or
below `1e−06`, §4 is wrong** and the fine level has a fault that is not
iterative — a mesh, `alphat` or heated-patch problem — and it must be found
before the level is graded. `C_lam_m`'s 99.3 % is predicted to remain outside;
it is not a finding either way (T3_RESULTS §5.2).

**P3 — do any triples become CONVERGING?** Following T3_PREREGISTRATION §8
prediction 8 — which registered *"at least one of G1–G4 comes back not
CONVERGING"* and which T3_RESULTS §8 scored **HELD, emphatically**, all four
plus every level NOT CONVERGED — the registered prediction here is the
conservative continuation of the same logic:

> **At least one of G1–G4 is still not CONVERGING after ext1, and the most
> likely outcome is that none of the four is.**

The reasoning is the same one prediction 8 gave and it has not weakened: the
`G1`–`G4` triple is `R_c` / `R_m` / `R_f`, and **`R_c` is one of the three
STALLED cases**. P1 predicts `R_c` does not converge at 80 000. A triple
containing a level that is NOT CONVERGED cannot be read as a mesh statement at
all, so on P1's own prediction all four triples remain unreadable and G1–G4
remain NOT A RESULT under gate (1) before gate (2) is even reached. Even
setting `R_c` aside, the observed orders today are `−0.892`, `−3.282`, `−0.516`
and `−0.209` — DIVERGENT and OSCILLATORY, not marginal — and T3_RESULTS §3
found the ladder *not ordered by mesh*, with the fine level further from steady
than the medium. Converging the levels removes one cause of that disorder; it
does not guarantee a positive observed order.

**The rule, stated so it cannot be renegotiated afterwards.** T3_PREREGISTRATION
§7.1 orders the gates: **(1)** any ladder level NOT CONVERGED → NOT A RESULT;
**(2)** triple not CONVERGING → NOT A RESULT; **(3)** no primary file → BLOCKED.

> **A triple that is still not CONVERGING after ext1 stays NOT A RESULT.** Gate
> (2) is not relaxed, not averaged over, not reported with a "nearly" and not
> converted into a REPORTED row because iterations were spent on it. Spending
> USD 4.08 buys the ladder more iterations to be judged on; it buys no change to
> the judgement. If the levels converge and the triples remain DIVERGENT or
> OSCILLATORY, the response is the one T3_RESULTS §10.1 and
> T3_PREREGISTRATION §8 prediction 8 already registered — **a fourth mesh
> level, proposed and not run** — and the four rows stay NOT A RESULT until
> that is done. `BLOCKED` on the missing Vogel & Eaton 1985 primary remains
> downstream of both gates and is not reached by this extension either.

**P4 — the marking tool.** Run against the pool while the extensions are still
going, `mark_done_t3_ext1.py --dry-run` will report **0/8** and flag **all eight**
stale `DONE.<case>` markers for removal, so the frozen comparator correctly
refuses for as long as any extension runs.

---

## 7. The original verdict, retained unaltered

Nothing in this addendum edits, supersedes or annotates the following. It is
the frozen comparator's output of 2026-08-21 and it stands as the T3 record:

| row | quantity | triple state | iterative conv. `c`/`m`/`f` | **verdict** |
| --- | --- | --- | --- | --- |
| G1 | `St_peak` | DIVERGENT (`p` −0.892) | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** |
| G2 | `x_peak/H` | OSCILLATORY | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** |
| G3 | `St(10 H)` | DIVERGENT (`p` −0.516) | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** |
| G4 | `St(20 H)` | DIVERGENT (`p` −0.209) | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** |

`gate_t3.json` tally: **`PASS 0, GATE FAIL 0, NOT A RESULT 4, BLOCKED 0,
PENDING 0, REPORTED 0`**. `0 of 4` graded rows. `T3_reference_primary.json`
absent; Vogel & Eaton 1985 (DOI 10.1115/1.3247522) **NOT OBTAINED**. The heat
balance GUARD fired on `R_f` (8.234 %) and `C_lam_m` (99.32 %).

`analyse_t3.py`, `build_t3.py`, `mark_done_t3.py`, `run_one_t3.sh`,
`launch_t3.sh`, `T3_PREREGISTRATION.md`, `T3_CONTRACT.md` and `T3_RESULTS.md`
are **not edited by this addendum**; §9 hashes them before and after.

---

## 8. The marking-tool amendment

**`verification/runs/T-family/T3_runs/mark_done_t3_ext1.py`** — new file. The
frozen `mark_done_t3.py` is not touched.

**Why it is needed.** `mark_done_t3.py` judges the original segment only, and
two of its six tests become permanently unsatisfiable for an extended case:

* **test 3** — last written time == controlDict `endTime`. After ext1 the
  `endTime` is 28 000–80 000 and the last time dir is that; but during the
  extension it is not, and the test would fail.
* **test 5** — `^ExecutionTime` lines in `log.solve` == `endTime`. `log.solve`
  holds exactly **20 000** lines for ever, against an `endTime` of 28 000–80 000.
  **This can never be satisfied, however well the extension finishes.**

And the deeper problem: **`mark_done_t3.py` never retracts.** Its `main()` only
writes markers. All eight `DONE.<case>` files written when the cases met the
rule at 20 000 sit on disk now, certifying a state the extension supersedes,
and `analyse_t3.py` asks only whether `DONE.<case>` **exists**. Left alone, a
stale marker would let the frozen comparator grade fields out of a half-finished
extension.

**The two-segment rule.** With no `log.solve.ext1`, a case is judged by
`mark_done_t3.check()` exactly as before, untouched. With one:

1. `STATUS.<case>` `rc=0` **and** `STATUS_EXT1.<case>` `rc=0`.
2. **`End` in `log.solve` (segment 1) and `End` in `log.solve.ext1`
   (segment 2)** — both segments finished under OpenFOAM's own hand.
3. **Last time dir == the NEW `endTime`** from `system/controlDict`.
4. `NEEDED` (`T U p_rgh alphat phi`) plus `NEEDED_TURBULENT` (`nut k omega`)
   when `is_ras`, present at that time.
5. **`ExecutionTime(log.solve) + ExecutionTime(log.solve.ext1) == endTime`**,
   `log.solve` still holding exactly 20 000 (segment 1 unaltered), **and the
   first `Time =` of `log.solve.ext1` exactly `20001`** — one past segment 1's
   count. Nothing replayed, nothing skipped.
6. **Age guard**: every field at the last time **newer than `0/T`** (the
   original L-143 stray-write guard — `run_one_t3.sh` touched `0/T` last, and
   `run_one_t3_ext1.sh` never touches `0/` at all, so that datum survives)
   **and newer than `STATUS.<case>`**, the file that dated the end of segment 1.
   A field older than `STATUS.<case>` was written by segment 1, not by the
   extension.

**Retraction.** A case *with* an ext1 log that fails has any pre-existing
`DONE.<case>` **removed**, with reasons printed. A marker is never removed for a
case *without* an ext1 log — that is the original tool's territory. `--dry-run`
reports and touches nothing.

**It imports its rules rather than restating them:** `CASES`, `NEEDED`,
`NEEDED_TURBULENT`, `check`, `control_end_time` and `is_ras` all come from
`mark_done_t3`. (`mark_done_t3` exposes `is_ras`, not `is_laminar` — that name
is T1b's — so laminar is taken as `not is_ras(case_dir)`, which is the same test
the original `check` makes.) Nothing is redefined locally, so the two tools
cannot drift apart.

**This is an amendment to the MARKING tool only.** It cannot move a number. It
decides only whether the frozen comparator may read a case at all, and only ever
in the direction of **refusing more**.

### 8.1 Selftest transcript

It forges complete two-segment case directories in a temp root and checks each
rule fires. Run **before any extension was launched**:

```
$ date -u +%FT%TZ
2026-08-22T17:51:35Z
$ python3 mark_done_t3_ext1.py --selftest
SELFTEST mark_done_t3_ext1.py  (forged case dirs under /tmp/t3ext1_selftest__ppyk8_y)
  [ok ] clean two-segment case PASSES
  [ok ] first ext1 Time 20501 -> REJECT (replayed or skipped)
  [ok ] ExecutionTime count 29000 != 30000 -> REJECT
  [ok ] no End in log.solve.ext1 -> REJECT
  [ok ] STATUS_EXT1 rc=1 -> REJECT
  [ok ] no STATUS_EXT1 -> REJECT
  [ok ] last time 28000 != endTime 30000 -> REJECT
  [ok ] final T older than 0/T -> REJECT (age guard)
  [ok ] failing ext1 case: stale DONE.I flagged for removal
  [ok ] --dry-run left DONE.I on disk
  [ok ] real run REMOVED stale DONE.I
  [ok ] laminar case (no nut/k/omega) PASSES
  [ok ] no-ext1 case judged by the ORIGINAL tool, marker untouched
SELFTEST PASSED  (14/14 checks)
```

Pre-launch state of the real pool, both tools, with no `ext1` log on disk:

```
$ date -u +%FT%TZ ; python3 mark_done_t3.py
2026-08-22T17:47:49Z
8/8 cases meet the strict completion rule
rc=0

$ date -u +%FT%TZ ; python3 mark_done_t3_ext1.py --dry-run
2026-08-22T17:47:51Z
DRY RUN -- nothing written or removed: 8/8 cases meet the strict completion rule (0 with an ext1 extension)
  PASS      R_c ... PASS  O_m
rc=0
```

Both agree at 8/8 before the extension, which is the correct pre-extension
answer and confirms the fall-through path. Once `log.solve.ext1` appears the
ext1 tool switches each case to the two-segment rule (P4).

---

## 9. The runner and the launcher

**`verification/runs/T-family/T3_runs/run_one_t3_ext1.sh`** — resumes one case
from `latestTime` to a raised `endTime`. Pattern of `T1_runs/run_one_ext1.sh`
(T1b §6), with the controlDict edit made explicit and defended:

* `system/controlDict` is **copy-edited** (`sed > tmp`, `mv`), never edited in
  place, after a `.pre_ext1` snapshot is taken.
* **Every `sed` is followed by a `grep` post-check, and the script REFUSES with
  `exit 2` if the post-check does not see the intended line** — before the
  solver is started. Three post-checks: `startFrom latestTime`, `endTime
  <new>`, `stopAt endTime`. A silently unapplied `sed` would either restart the
  case from `0` (destroying 20 000 iterations of work) or stop it at 20 000
  (wasting the whole extension), and either would be discovered only after
  hours of wall. It refuses instead.
* Solver output to **`log.solve.ext1`**; `log.solve` is never opened.
* **`0/` is never touched** — no `cp`, no `touch`, no `rm` anywhere in the
  script — so `0/T`'s mtime still dates the start of segment 1 and the §8 age
  guard keeps working.
* Writes **`STATUS_EXT1.<case>`** as `rc=<rc> wall=<seconds> endTime=<n>`.

**`verification/runs/T-family/T3_runs/launch_t3_ext1.sh`** — same **G1/G2/G3**
guards as the frozen `launch_t3.sh`:

* **G1** — `mkdir <case>/LAUNCH_LOCK_EXT1` atomically; if it exists, SKIP. The
  original `<case>/LAUNCH_LOCK` is left strictly alone: it is segment 1's record
  and holds `run_one_t3.sh`'s noclobber `solver.pid` claim.
* **G2** — refuse if any running process has `/proc/<pid>/cwd` == the case dir,
  naming the pid and its `exe`. Unchanged.
* **G3, adapted for a continuation** — the mirror image of the original. The
  frozen `launch_t3.sh` refused when a solution time dir existed (a fresh run
  must start clean). An extension requires the opposite: **time dir `20000/`
  MUST exist** (there must be something to resume from) and **`log.solve.ext1`
  must NOT exist** (no extension may already have run). Both are also
  re-checked inside the runner, defence in depth.
* Detaches via `setsid nohup`, logs to `<case>/LAUNCH_LOCK_EXT1/launch.log` and
  to `T3_runs/LAUNCH_EXT1.log`. **Nothing here ever kills a process** — in
  particular the four T1b L4 solvers (pids 442445, 450274, 488219, 503891) are
  never touched, and G2 would refuse rather than collide with any of them.

---

## 10. Launch

Box state confirmed immediately before launch:

```
$ nproc
16
$ uptime
 17:41:02 up 1 day,  2:19,  2 users,  load average: 7.76, 9.85, 8.15
$ ps -o pid,pcpu,etime,cmd -C buoyantBoussinesqSimpleFoam
    PID %CPU     ELAPSED CMD
 442445 99.9    20:13:48 buoyantBoussinesqSimpleFoam
 450274 99.9    20:12:17 buoyantBoussinesqSimpleFoam
 488219 99.9    19:16:36 buoyantBoussinesqSimpleFoam
 503891 99.9    19:03:03 buoyantBoussinesqSimpleFoam
```

Four cores are held by the T1b L4 serial solvers and are **not touched**.
16 − 4 = **8 free**, and the eight T3 extensions are serial (`nProcs 1`), one
core each: exactly 8. No oversubscription.

### 10.1 Launch record

All eight launched detached (`setsid nohup`), serial, one core each, by
`launch_t3_ext1.sh <case> <endTime>`. Every one passed **G1, G2 and G3** and
exited 0. Timestamps from `T3_runs/LAUNCH_EXT1.log`:

| case | `endTime` | wrapper pid | solver pid | launched (UTC) |
| --- | ---: | ---: | ---: | --- |
| `R_c` | 80 000 | 752891 | 754946 | 2026-08-22T17:51:43Z |
| `R_m` | 36 000 | 754100 | 756428 | 2026-08-22T17:51:43Z |
| `R_f` | 78 000 | 755591 | 757934 | 2026-08-22T17:51:44Z |
| `P_m` | 36 000 | 757098 | 759476 | 2026-08-22T17:51:44Z |
| `C_lam_m` | 80 000 | 758609 | 761058 | 2026-08-22T17:51:45Z |
| `W_m` | 80 000 | 760188 | 762535 | 2026-08-22T17:51:45Z |
| `D_m` | 28 000 | 761716 | 763872 | 2026-08-22T17:51:46Z |
| `O_m` | 46 000 | 763273 | 764454 | 2026-08-22T17:51:46Z |

Solver pids were mapped to cases by `readlink /proc/<pid>/cwd`, not assumed.
The four T1b L4 pids (442445, 450274, 488219, 503891) were still running,
untouched, at 99.9 % CPU each after the launch; the eight new solvers settled
at 91–97 % CPU each, i.e. 12 near-saturated cores of 16.

### 10.2 Verification at launch + 2 minutes

Four things were checked on every case, and all eight passed all four:

| check | result |
| --- | --- |
| `log.solve.ext1` exists and holds `Starting time loop` | **8/8**, exactly one occurrence each |
| first `Time =` line is exactly **20001** (`startFrom latestTime` honoured, `endTime + 1`, nothing replayed or skipped) | **8/8** |
| `controlDict` post-check line printed by the runner | **8/8** `controlDict OK <case>: startFrom latestTime; stopAt endTime; endTime <n>;` |
| `log.solve` still holds exactly **20 000** `ExecutionTime` lines (segment 1 untouched) | **8/8** |

`0/T` mtimes are all pre-launch (`2026-08-21T18:03Z`–`2026-08-22T10:59Z`) on
every case: **`0/` was not touched**, so the §8 age guard's datum survives.
`system/controlDict.pre_ext1` snapshots were taken on all eight, each still
reading `endTime 20000`.

### 10.3 The stale markers were removed, and the comparator now refuses

P4 scored while the extensions were in flight, at **2026-08-22T17:53:21Z**:

```
$ python3 mark_done_t3_ext1.py
0/8 cases meet the strict completion rule (8 with an ext1 extension)
  NOT DONE  <every case>  [ext1 present]
            - no STATUS_EXT1 file (ext1 extension not finished)
            - log.solve.ext1 has no End line (segment 2 did not finish)
            - last written time 20000 != endTime <new>
            - time 20000 holds fields OLDER than STATUS (...) -- not written by the ext1 extension
            - 20000+<n>=<...> ExecutionTime lines (log.solve+ext1), expected <new>
            REMOVED stale DONE.<case> -- it certified the superseded pre-extension state
$ ls DONE.*
ls: cannot access 'DONE.*': No such file or directory
$ python3 analyse_t3.py ; echo $?
REFUSE: no completion marker for R_c, R_m, R_f, P_m, C_lam_m, W_m, D_m, O_m
2
```

**All eight stale `DONE.<case>` markers are removed and the frozen comparator
refuses with exit 2.** This is the safety-critical step: left in place, those
markers would have let `analyse_t3.py` grade fields out of a half-finished
extension, because it asks only whether the marker exists. `gate_t3.json` was
**not** rewritten (mtime `2026-08-22T17:33:22Z`, pre-launch), so the §7
verdict on disk is still the original one. P4 is **HELD**.

### 10.4 Measured rate and ETA, over a clean 5-minute window

Rates from the launch timestamp would include solver startup (mesh and field
read), so they are measured instead over a **steady-state window,
17:54:57Z → 17:59:57Z**, from the count of `^Time = ` lines in each
`log.solve.ext1` at each end.

| case | `endTime` | at 17:59:57Z | remaining | **it/min** | measured cell-it/core-s | **ETA, h** | **ETA (UTC)** | predicted h | measured/pred |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `D_m` | 28 000 | 20 840 | 7 160 | 98.2 | 1.299e5 | **1.22** | 2026-08-22T19:12:55Z | 1.18 | 1.15 × |
| `W_m` | 80 000 | 25 773 | 54 227 | 673.8 | 3.162e5 | **1.34** | 2026-08-22T19:20:29Z | 1.24 | 1.19 × |
| `R_c` | 80 000 | 22 543 | 57 457 | 295.4 | 1.772e5 | **3.24** | 2026-08-22T21:14:31Z | 2.73 | 1.24 × |
| `R_m` | 36 000 | 20 500 | 15 500 | 58.2 | 8.940e4 | **4.44** | 2026-08-22T22:26:20Z | 3.53 | 1.30 × |
| `P_m` | 36 000 | 20 491 | 15 509 | 57.6 | 8.847e4 | **4.49** | 2026-08-22T22:29:15Z | 3.53 | 1.31 × |
| `C_lam_m` | 80 000 | 20 795 | 59 205 | 93.0 | 1.428e5 | **10.61** | 2026-08-23T04:36:37Z | 8.58 | 1.25 × |
| `O_m` | 46 000 | 20 284 | 25 716 | 33.2 | 7.083e4 | **12.91** | 2026-08-23T06:54:35Z | 9.67 | 1.35 × |
| **`R_f`** | 78 000 | 20 117 | 57 883 | **14.0** | 5.495e4 | **68.91** | **2026-08-25T14:54:30Z** | 49.09 | **1.41 ×** |

**Critical path `R_f`: 68.9 h ≈ 2.9 days, finishing 2026-08-25T14:54Z.** Six
of the eight finish inside 13 h, five of them today. `D_m` and `W_m` finish
this evening.

**Revised cost from measured rate: 108.3 core-hours = USD 5.56**, against the
§5 prediction of 79.55 core-h / USD 4.08 — **1.36 ×**, well inside both the
10 × stop threshold (USD 40.8) and the binding remaining-ceiling stop
(USD 22.93). Rung total would be USD 2.07 + 5.56 = **USD 7.63**, 30.5 % of the
25 USD ceiling.

**Why every case is 15–41 % slower than predicted, and it is not a surprise.**
The §5 rates came from T3_RESULTS §9, measured while the box was shared. It is
shared again: alongside the eight extensions and the four T1b L4 solvers
(which are untouched and still at 99.9 %), the closure team is running
`fs3_select.py` in `cases/RANS_LES_closure_models/R4_sparta_build` at **~291 %
CPU, about 3 cores**. That is 12 + 3 ≈ 15 of 16 cores committed. The eight
extension solvers are nonetheless each holding **95–97.5 % of a core**, so
they are not being starved — the slowdown is memory-bandwidth and
cache contention, which is the same mechanism T3_RESULTS §9 identified when it
found throughput falling 4.9 × from the smallest case to the largest. The
degradation is worst on the largest mesh (`R_f`, 235 520 cells, 1.41 ×) and
mildest on the smallest (`D_m`, 79 360 cells, 1.15 ×), which is that mechanism's
signature and not a scheduling problem.



---

## 11. sha256 of every frozen file

Hashed **before** the amendment was written, at `2026-08-22T17:45:15Z`:

| file | sha256 (before) |
| --- | --- |
| `verification/runs/T-family/T3_runs/build_t3.py` | `7527a54630b271ce7fca3a916d43e2f4c6c9c923b8e1b014785e1ecc4436f739` |
| `verification/runs/T-family/T3_runs/analyse_t3.py` | `f41c544d7552e7abfe6adeb8ff1d7ff4c14288017d36821ea3040f1158498741` |
| `verification/runs/T-family/T3_runs/mark_done_t3.py` | `ba466e23a5b633993c726c6657802cf146e200c4d96c311d962666361fc2d60d` |
| `verification/runs/T-family/T3_runs/run_one_t3.sh` | `7cd0df46b23f4eaeb02891fc43cde1405c6bff24c152296cccd82fd6ce4879ff` |
| `verification/runs/T-family/T3_runs/launch_t3.sh` | `a6561b6577a9b8097745c1c9d028cd1de0d35aaa80edc6a427acd904fd9db82d` |
| `docs/campaigns/T-family/T3_PREREGISTRATION.md` | `c18077d9daa9a2bcdb2ee856c3bb7311c57ee383fe275c8d5f682a8909e59d81` |
| `verification/runs/T-family/T3_runs/T3_CONTRACT.md` | `9156d607056d6f634a3d2221ab38a2a62c4122caaf04683a6a9005e62eb80649` |
| `docs/campaigns/T-family/T3_RESULTS.md` | `4459b5dc2f42240edd29535fb9f3403984216f153d288d311efe91e7a751d25a` |

Re-hashed **after** the launch, at `2026-08-22T17:53:53Z`:

| file | sha256 (after) | |
| --- | --- | --- |
| `build_t3.py` | `7527a546...36f739` | **unchanged** |
| `analyse_t3.py` | `f41c544d...498741` | **unchanged** |
| `mark_done_t3.py` | `ba466e23...fc2d60d` | **unchanged** |
| `run_one_t3.sh` | `7cd0df46...4879ff` | **unchanged** |
| `launch_t3.sh` | `a6561b65...9db82d` | **unchanged** |
| `T3_PREREGISTRATION.md` | `c18077d9...e59c81` | **unchanged** |
| `T3_CONTRACT.md` | `9156d607...b80649` | **unchanged** |
| `T3_RESULTS.md` | `e557c798df87181e196086f39cdf0d00f3b65b53d9969f0d8cfc1dfce87ba279` | **CHANGED — not by this lane; see §13** |

**Seven of the eight are byte-identical before and after.** This lane edited
none of them: it created four new files and wrote nothing to any frozen path.
The eighth is accounted for in §13.

---

## 12. Files created by this addendum

All new. No existing file is edited.

* `/home/ubuntu/Certonomous/docs/campaigns/T-family/T3_EXT1_AMENDMENT.md` — this document
* `/home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/run_one_t3_ext1.sh`
* `/home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/launch_t3_ext1.sh`
* `/home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/mark_done_t3_ext1.py`
* `/home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/LAUNCH_EXT1.log`

Written during the extension by the runner, per case: `<case>/log.solve.ext1`,
`<case>/system/controlDict.pre_ext1`, `<case>/LAUNCH_LOCK_EXT1/launch.log`,
`STATUS_EXT1.<case>`, `wrapper_ext1.<case>.out`. `log.solve`, `0/`, `0.orig/`
and every frozen file are untouched.

---

## 13. Concurrent modification of a frozen file, observed and reported

`docs/campaigns/T-family/T3_RESULTS.md` was hashed at **17:45:15Z** as
`4459b5dc2f42240edd29535fb9f3403984216f153d288d311efe91e7a751d25a` and
re-hashed at **17:53:53Z** as
`e557c798df87181e196086f39cdf0d00f3b65b53d9969f0d8cfc1dfce87ba279`. **This
lane did not edit it**, and it is a frozen file, so the change was traced
before anything else was done.

**What happened.** The current on-disk content is **byte-identical to git
`HEAD`** (`git diff` on the path returns empty; `git show HEAD:<path> |
sha256sum` returns the same `e557c798`). `HEAD` is **`fd831c11` "T-family:
Thermal Buildup Directive recorded; T3 NOT A RESULT 4/4; charter 2e; ..."**,
committed by another lane at about **17:52:37Z**, which is the file's mtime.
The `4459b5dc` version hashed at 17:45 was therefore an *uncommitted
working-tree* variant, and the commit brought the working tree to the
committed text. The staged state shows other T-family paths marked `D` in the
shared index by that lane; **this lane touched no index and ran no git
command that writes** — only `git diff`, `git log`, `git show` and
`git status`, all read-only.

**Whether it matters to this addendum: it does not.** Every number this
addendum took from `T3_RESULTS.md` was re-read from the current text and is
byte-identical to what was used:

* §3's convergence table, all eight rows — `R_c` `4.944e-02`/`1.524e-01`,
  `R_m` `2.855e-05`/`1.378e-04`, `R_f` `1.095e-03`/`3.703e-03`, `P_m`
  `1.526e-05`/`1.378e-04`, `C_lam_m` `6.000e-01`/`1.189e+00`, `W_m`
  `1.417e-06`/`1.252e-06`, `D_m` `1.893e-05`/`1.246e-09`, `O_m`
  `9.622e-05`/`1.915e-04` — the sole field input to §3's `endTime`s.
* §5.2's heat-balance column, all eight rows, including `R_f` `8.234 %` and
  `C_lam_m` `99.32 %` — the input to §4.
* §9's measured cell-iterations per core-second, all eight rows — the input
  to §5's cost.
* §13's rung verdict, `NOT A RESULT` 4 of 4 — restated in §7 above.

**No `endTime`, cost figure or prediction in this addendum changes.** The
difference between the two hashes lies elsewhere in the file. It is recorded
here because a frozen file's hash moved inside the window this addendum
covers, and a hash that moves without explanation is worse than one that moves
with one.
