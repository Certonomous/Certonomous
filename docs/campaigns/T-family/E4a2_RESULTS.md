# E4a2. fanPressure BC verification, successor rung — results

**Written 2026-08-24T17:40:40Z** (the stamp is `date -u` output read in the same shell
invocation that stamped this file). Pre-registration
`docs/campaigns/T-family/E4a2_PREREGISTRATION.md`, **FROZEN BY COMMIT
`cd1f46e1`** (2026-08-24T17:23:22Z) before any case directory existed.
Predecessor: `docs/campaigns/T-family/E4a_RESULTS.md`, rung verdict
**NOT A RESULT**, prereg frozen at `628e29c4`.

Comparator output: `verification/runs/T-family/E4a2_runs/log.analyse_e4a2.20260824T173504Z.txt`
(exit **0**). Completion marker log:
`verification/runs/T-family/E4a2_runs/log.mark_done.20260824T173456Z.txt` (exit 0).

---

## 1. Rung verdict

**PASS.**

**All eight registered rows PASS** — I1, I2, P1, R1, G1, G2, N1, D1 — and both
controls held (**Z1** planted-zero, **X1** reproduction; either would have been
a refusal, exit 2). The comparator exited **0**: it neither failed a row
(exit 1) nor refused (exit 2).

**The one thing this rung re-registered — the iterative-convergence gate —
CLOSED on all five cases.** C1 (sustained floor), C2 (not growing) and C3
(graded-quantity stationarity) all hold for F_c, F_m, F_f, S_f and N_f. That is
the §3.2 registered prediction, made before any case existed, and it is
**confirmed**; its falsifier did not fire.

What this establishes that E4a could not: `fanPressure`'s operating point agrees
with the exact plane-Poiseuille intersection inside every registered analytic
interval (G1, G2, N1); the ladder's observed order is **1.959**, inside the
registered `[1.6, 2.4]` around a predicted 2.00, on a triple the frozen grader
classified **CONVERGING**; and the §1.5 error model's corrected-Richardson
extrapolation lands at **−0.171 %** inside the registered `[−0.35, −0.08] %`
(D1). E4a established none of these — all five were void under rule 5 order (1).

**No gate, threshold, cap or label was touched.** The gate that closed is the
gate committed at `cd1f46e1`, verified by hash against that blob before the
build, and re-verified by the comparator against the same blob at run time.

---

## 2. The convergence gate — the one row this rung re-registers

Registered constants (`E4a2_PREREGISTRATION.md` §2.2): `FLOOR = 1e-8`,
`sustained_intervals = 3`, `fit_r2_min = 0.90`, `fit_slope = 0.01 dec/1000`,
`CUM_TOL = 1e-7`. A case is CONVERGED iff C1 **and** C2 **and** C3.

| case | converged | `r_last` | **C1** max `r` over last 3 intervals (floor 1e-8) | first crossing | class | slope (dec/1000) | R² | p95/p05 | **C3** \|dQ\| over half the run (tol 1e-7) |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| F_c | **True** | 6.836e-10 | **1.113e-09** | 4 000 | LIMIT CYCLE | −0.01449 | 0.151 | 4.48 | **2.526e-10** |
| F_m | **True** | 6.583e-10 | 9.522e-10 | 4 000 | FLOOR | −0.00386 | 0.089 | 1.66 | 1.308e-10 |
| F_f | **True** | 6.181e-11 | 6.181e-11 | 4 000 | LIMIT CYCLE | −0.02366 | 0.078 | 10.24 | 3.249e-11 |
| S_f | **True** | 1.951e-10 | 2.385e-10 | 4 000 | FLOOR | −0.02157 | 0.686 | 2.23 | 1.738e-10 |
| N_f | **True** | 4.644e-11 | 7.960e-11 | 4 000 | LIMIT CYCLE | −0.02891 | 0.768 | 4.16 | **0.000e+00** |

**Headroom.** The worst C1 reading anywhere is F_c's **1.113e-09**, **8.99×
inside** the registered floor — within 7 % of the 1.189e-9 that §2.5 measured
read-only on E4a's trees and cited as feasibility. The worst C3 reading is
F_c's **2.526e-10**, **396× inside** `CUM_TOL`, measured across a window
(30 000 → 60 000) twice the widest E4a span, against §2.6's cited E4a worst of
3.886e-10. **The floor was reachable, and the achieved values sit an order of
magnitude inside it rather than at it** — which is what §2.5 registered as the
intent, not a post-hoc reading.

**C2 fired on nothing.** Every fitted slope is negative (−0.0039 to −0.0289
decades per 1 000 iterations) and every R² is far below the 0.90 the GROWING
flag requires; no series is growing on the fitted trend.

**Three cases classify LIMIT CYCLE, and that does not gate — by registration,
not by concession.** §2.8 registered that of the four classifications only the
GROWING flag gates (it is C2); §2.2 registered *why*, in advance: E4a's own F_c
series grew 1.54× across its last three intervals while sitting three decades
inside the floor, and "a strict non-growth-between-intervals requirement would
void the rung for **bounce at a floor** — E4a's defect in a new costume."
F_c (p95/p05 4.48), F_f (10.24) and N_f (4.16) are that bounce. **This is a
disclosed, pre-registered property of the gate and is flagged for the
supervisor rather than smoothed over**: the rung certifies a stationary iterate
that bounces within a band three decades below any registered interval, not a
monotonically settling one. §7 of the pre-registration already states the
weaker, honest claim this supports.

**First crossing is 4 000 on all five cases — the first measurable interval.**
The `r_k` series begins at 4 000 (the 2 000 → 4 000 pair), so the floor was met
at the earliest reading the retained-checkpoint schedule can produce. **The
registered `endTime` of 60 000 is therefore ~15× longer than first crossing
required.** That is an observation about run length, not a verdict, and rule 2
closes the gate to change now; it is recorded for a successor's cost model.

---

## 3. Registered rows — every row, as the comparator graded it

Comparator `verification/runs/T-family/E4a2_runs/analyse_e4a2.py`, sha256
`26a10ef4d55319b8de01988a2d24631f15a680ae91dc066d6aab9e1096cf7261`, verified
identical in three places — the `FREEZE_CHECK.txt` §6 table, the working tree at
run time, and the blob committed at `cd1f46e1`.

| row | verdict | measured | registered interval | falsifier fired? |
| --- | --- | --- | --- | --- |
| **I1** | **PASS** | max fan-patch face residual **6.033e-11 m²/s²** (worst case F_m) | `≤ 8.1e-8 m²/s²` | **no** — 1 343× inside tolerance; the ½U_m² ≈ 1.125e-4 static-vs-total convention signature the row exists to catch is ~6.3 decades above it |
| **I2** | **PASS** | max \|Q_in − Q_out\|/\|Q_in\| **9.712e-10** (worst case F_m) | `≤ 1e-4` | **no** |
| **P1** | **PASS** | **0** fan-patch faces with φ ≥ 0 in any case | `= 0` | **no** — the analytic referent for G1/G2/N1/D1 stands |
| **R1** | **PASS** | observed order **1.959**; GCI(Fs = 1.25) **0.393 %**; Richardson frozen **1.506878761e-07**, corrected **1.497435362e-07** | `p ∈ [1.6, 2.4]`, predicted 2.00 | **no** |
| **G1** | **PASS** | F_f `Q` **1.502157061e-07 m³/s**, dev **+0.144 %** (predicted +0.111 %) | dev `[−0.11, +0.31] %` | **no** |
| **G2** | **PASS** | S_f `Q` **1.002387044e-07 m³/s**, dev **+0.239 %** (predicted +0.213 %) | dev `[−0.02, +0.40] %` | **no** — the G1-PASS/G2-FAIL signature that would say the machinery fits one curve did not appear |
| **N1** | **PASS** | N_f `Q` **1.504314707e-07 m³/s**, dev **+0.288 %** (predicted +0.223 %) | dev `[−0.12, +0.50] %` | **no** |
| **D1** | **PASS** | corrected Richardson **1.497435362e-07**, dev **−0.171 %** (predicted −0.197 %) | dev `[−0.35, −0.08] %` | **no** — the §1.5 entrance model is not falsified low |
| **Z1** | **PASS (control)** | planted-zero exact-float rule held for the `p`, `U` and `φ` readers in **every** case | exact-float, no tolerance | **no** — a failure would have been a refusal (exit 2); the comparator exited 0 |
| **X1** | **PASS (control)** | \|dev(E4a2) − dev(E4a)\| = **0.0000 pp** in **all five** cases | `≤ 0.01 pp` | **no** — a failure would have been a refusal (exit 2) |

**R1's triple state is CONVERGING, and rule 5 is satisfied by construction, not
by assertion.** R1 is graded by the **frozen** `E4_runs/analyse_e4a.py`
`grade_triple`, which returns a verdict other than NOT A RESULT only after
`gci()` reports `state == "CONVERGING"`; every other path returns NOT A RESULT
with `(no GCI quoted)`. The comparator took the verdict branch and printed a
GCI, so the triple is CONVERGING and the GCI quote is rule-5-legal. The literal
state string is not printed on the PASS path — that is a property of the frozen
instrument, stated here rather than inferred silently.

**§2.7's disclosed risk on I1 did NOT materialise.** The pre-registration
registered, before any solve, that under this floor I1's headroom argument
weakens: the flux-lag bound becomes **9.72e-9 m²/s²**, only 8.3× below I1's
carried-over tolerance, and a reading between 1e-8 and 8.1e-8 would be
"a **PASS with the headroom argument spent**, not a clean one." Measured I1 is
**6.033e-11 m²/s² — 161× BELOW that flux-lag bound** and 1 343× below the
tolerance. **I1 is a clean PASS; the headroom argument is not spent.**

---

## 4. Predictions scored

### 4.1 §3.2 — the new registered prediction

> *Registered before any solve: the convergence gate CLOSES at `endTime` 60 000
> for ALL FIVE cases — C1, C2 and C3 all hold for F_c, F_m, F_f, S_f and N_f.*

**CONFIRMED, 5/5.** Its falsifier ("**any** case failing C1, C2 or C3 makes
R1/G1/G2/N1/D1 NOT A RESULT again and the rung NOT A RESULT") **did not fire**.

### 4.2 §3.3 — the four registered readings

**None fires.** All four readings in §3.3 are conditioned on a **failing** case
("the failing case classifies …", "C1 and C2 hold while C3 fails"), and no case
failed the gate. There is no discriminating measurement to report under (i),
(ii), (iii) or (iv), and no NOT A RESULT to diagnose. Registering the branches
in advance (L-244) did its work: the outcome discriminated rather than
confirmed, and it discriminated toward the arm that needs no reading.

### 4.3 §3.1 — the carried-over rows against their predictions

Every registered interval contains its own prediction (asserted in the
selftest), and every measurement lands inside its interval. Signed distances
from the registered central prediction:

| row | predicted | measured | measured − predicted |
| --- | ---: | ---: | ---: |
| R1 (order) | 2.00 | 1.959 | −0.041 |
| G1 (F_f dev) | +0.111 % | +0.1438 % | **+0.033 pp** |
| G2 (S_f dev) | +0.213 % | +0.2387 % | **+0.026 pp** |
| N1 (N_f dev) | +0.223 % | +0.2876 % | **+0.065 pp** |
| D1 (corrected Richardson dev) | −0.197 % | −0.171 % | **+0.026 pp** |

These are now **graded rows**, not the diagnostic table E4a §4 was forced to
carry: the gate closed, so rule 5 permits the interval verdict to stand.

### 4.4 X1 — the reproduction control

X1 recovered **0.0000 pp** gaps on all five cases against E4a's measured
deviations (+1.3699, +0.5255, +0.1438, +0.2387, +0.2876 %), with `Q` agreeing
to ten significant figures despite **3× the iterations** (60 000 vs 20 000).
That is direct evidence for the flat-floor reading §2.5 registered: the extra
40 000 iterations moved the graded target by less than the tenth significant
figure. **X1 grades nothing and is not a prediction** (§0.2), and §7 records
what it cannot see: it is blind to any defect common to both rungs, and every
carried-over instrument is common to both by design.

---

## 5. Execution record and completion audit

Build: `build_e4a2.py` rc=0 — five case dictionaries, the frozen
`verify()` one-change-per-case check passed, manifest
`verification/runs/T-family/E4a2_runs/BUILD_MANIFEST.txt` (42 lines).
Immediately after the build the tree held **zero numeric time directories** and
zero markers, and each case carried `0.orig` but no `0`. **Disclosed gap:** the
build's stdout was **not** captured to a stamped log file (E4a's practice, its
`log.build.*.txt`); the pre-registration does not require one, the summary is
quoted in this record, and `BUILD_MANIFEST.txt` is the on-disk artifact. Naming
it is cheaper than leaving a reader to notice the absence.

Launch: **serial, one case at a time**, via `launch_e4a2.sh`, `nice 15`,
nProcs 1, detached with `setsid`/`nohup`. Guards **G1** (atomic `mkdir` lock),
**G2** (`/proc` cwd scan) and **G3** (no stray numeric time dir) passed for all
five cases; per-case evidence in `<case>/LAUNCH_LOCK/launch.log`. The three
T1b L4 `buoyantBoussinesqSimpleFoam` solvers (pids 442445, 450274, 488219) were
live in `../T1_runs` throughout, were verified alive after the last case, and
were **not touched**.

| case | curve | Ny | cells | rc | solver wall (s) | wrapper gross (s) | blockMesh rc | checkMesh rc | maxRSS (kB) | end (UTC) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| F_c | A | 8 | 800 | 0 | 38 | 38 | 0 | 0 | 60 216 | 2026-08-24T17:26:06Z |
| F_m | A | 12 | 1 800 | 0 | 70 | 70 | 0 | 0 | 61 064 | 2026-08-24T17:27:57Z |
| F_f | A | 18 | 4 050 | 0 | 135 | 135 | 0 | 0 | 62 180 | 2026-08-24T17:30:20Z |
| S_f | B | 18 | 4 050 | 0 | 134 | 134 | 0 | 0 | 62 376 | 2026-08-24T17:32:46Z |
| N_f | NULL | 18 | 4 050 | 0 | 114 | 114 | 0 | 0 | 62 696 | 2026-08-24T17:34:47Z |

Source: `verification/runs/T-family/E4a2_runs/STATUS.<case>` (five files) and
`<case>/LAUNCH_LOCK/launch.log`.

Retained checkpoints: **30 numeric time directories per case** (2 000 …
60 000), `purgeWrite 0`, exactly as §2.4 registered — 29 consecutive-pair
intervals, all reported.

Completion: `mark_done_e4a2.py` rc=0, **5/5 cases meet the strict completion
rule** through the frozen `mark_done_e4a.check` — rc=0; an `End` line; last time
== `endTime` **60 000**; `p U phi` present at `endTime`; `ExecutionTime` count
== 60 000; and every `endTime` field newer than the case's own `0/U` (the age
guard). **No `NOT DONE` reason line was printed for any case.** Markers
`DONE.F_c`, `DONE.F_f`, `DONE.F_m`, `DONE.N_f`, `DONE.S_f`.
`mark_done_e4a2.py` has **no `--dry-run`**: `main()` ignores `argv` entirely
(checked by reading it), so it was run once, for real.

**No run was stopped, killed, relaunched or discarded.** No case approached its
10× per-case stop threshold (F_c 390 s, F_m 690 s, F_f 1 350 s, S_f 1 350 s,
N_f 1 340 s — closest approach F_m at **10.1 %** of its threshold), and no wall
exceeded 3 600 s, so rule 12's stall rule matches nothing.

---

## 6. Cost — registered versus actual (rule 12, Sanaa's 2026-08-23 law)

Rate **$0.0513/core-h**, c7a.4xlarge, **owner-stated / reported-by-owner** — the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so **every
dollar figure below is derived, not measured**. Serial, `nice 15`, nProcs 1, so
core-s equals wall s.

| line | registered core-s (§5) | **actual core-s** | ExecutionTime (s) | s per cell-iteration | ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| F_c (800 cells) | 39 | **38** | 37.98 | 7.9125e-07 | **0.974×** |
| F_m (1 800) | 69 | **70** | 69.52 | 6.4370e-07 | **1.014×** |
| F_f (4 050) | 135 | **135** | 134.62 | 5.5399e-07 | **1.000×** |
| S_f (4 050) | 135 | **134** | 133.57 | 5.4967e-07 | **0.993×** |
| N_f (4 050) | 134 | **114** | 113.37 | 4.6654e-07 | **0.851×** |
| *solver subtotal* | *512* | ***491*** | *489.06* | | ***0.959×*** |
| blockMesh + checkMesh ×5 | 3 | **≤ 5, below resolution** | — | — | — |
| extra checkpoint I/O (26 further ascii writes/case) | 30 | *(inside the solver walls above)* | — | — | — |
| comparator (5 × 30 checkpoints) | 120 | **≤ 4** | — | — | **≤ 0.033×** |
| `mark_done_e4a2.py` | *(not separately registered)* | **≤ 2** | — | — | — |
| **total** | **665** | **≈ 497** | | | **0.747×** |

**Totals.** Predicted **665 core-s = 11.083 core-min = 0.18472 core-h =
$0.0095 derived**. Actual **≈ 497 core-s = 8.283 core-min = 0.13806 core-h =
$0.00708 derived**. **Ratio 0.747×.** No overrun. The rung consumed **7.47 %**
of its registered 10× stop-and-investigate threshold (1.8472 core-h).

**Actual cleaned = actual gross.** The longest wall on the box is 135 s, more
than a decade below the 3 600-s stall rule, so the stall rule matches nothing
and there is nothing to clean out.

**Measurement honesty on two lines.** The five solver figures are `wall=` from
`STATUS.<case>` with `ExecutionTime` from each `log.solve` beside them —
directly measured. **Meshing is NOT separately resolvable**: wrapper
start-to-end from `LAUNCH_LOCK/launch.log` equals the solver wall to the second
on **all five** cases, so blockMesh + checkMesh + the `0.orig → 0` copy cost
**under 1 s per case** and is bounded, not measured, at ≤ 5 core-s. The
comparator and marker figures are likewise **upper bounds**, from the UTC stamp
in each log's filename to that log's mtime (≤ 4 s and ≤ 2 s respectively) — the
processes were not separately timed, and a bound is reported rather than a
figure the record cannot back.

**Gap attribution.**

* **The solver line is not a miss — it is the E4a calibration lesson paying
  off, and that is this row's main content.** §5 registered its basis as
  **5.50e-7 s per cell-iteration**, measured on E4a's own F_f completion
  (44.56 s / (4 050 × 20 000)) and explicitly rejecting E4a's borrowed
  `buoyantBoussinesqSimpleFoam` basis of 7.5e-6 that over-predicted by 13.6×
  (ledger **C-21**, lesson **L-271**). E4a2's F_f measures **5.5399e-7 s per
  cell-iteration** — the basis reproduced to **0.7 %** at 3× the iterations —
  and the whole solver subtotal lands at **0.959×** against E4a's 0.075×.
  **A per-cell-iteration basis measured on the solver that will actually run is
  portable within its own solver class**; that is the calibration claim this
  rung tests and supports.
* **Misprediction, one material line: the comparator, over-predicted by ≥ 30×**
  (120 core-s registered, ≤ 4 measured). §5 costed it as 5 × 30 checkpoints ×
  ~24 700 parsed floats without a measured parsing rate; the reader is
  substantially faster than that guess. **This is the successor's calibration
  item**, and it is the only line where the estimate is materially wrong.
* **N_f at 0.851× is misprediction in the conservative direction, by
  construction.** §5 registered the **larger** of two estimates per case
  (basis 133.7 vs 3× E4a's measured wall 129 → 134), disclosed rather than
  averaged. N_f's per-cell-iteration cost fell from E4a's 5.362e-7 at 20 000
  iterations to **4.6654e-7** at 60 000 — fixed per-run overhead amortising
  over 3× the iterations. The same effect is visible on F_m (6.603e-7 →
  6.4370e-7) and F_c (7.925e-7 → 7.9125e-7) and inverted slightly on F_f
  (5.501e-7 → 5.5399e-7, +0.7 %).
* **Contention is not the explanation and could only push the other way.**
  Three peer `buoyantBoussinesqSimpleFoam` solvers ran at `nice 0` and 99.9 %
  CPU each throughout, load1 **3.90** on the 16-core box, with this lane at
  `nice 15` on one core and ~12 cores idle. Contention can only inflate an
  actual, so it cannot produce a sub-1 ratio; the per-case ratios of 0.851–1.014
  show its effect on this rung was negligible. **The figures are stated gross
  and are not netted off for it.**
* **WASTE: none.** No run was stopped, relaunched or discarded; no case tree was
  rebuilt; the builder, the marker and the comparator each ran exactly once.
  There is no waste figure to name separately, and none is folded into the
  ratio.

Disk: **199 MB** of retained checkpoints and logs across the five cases, against
a registered ~360 MB and 298 GB free.

---

## 7. Instrument provenance

All seven frozen E4a2 files hash **identical** in three places — the
`FREEZE_CHECK.txt` §6 tables, the working tree at run time, and the blobs
committed at **`cd1f46e1`** — asserted before the build (step 0 of the binding
order of operations) and re-verified by the comparator and the marker at every
invocation:

| file | sha256 |
| --- | --- |
| `docs/campaigns/T-family/E4a2_PREREGISTRATION.md` | `140c47577c3fa9e583a1d6e1334834dd380b26967f12b51a80d5f42f207e684c` |
| `E4a2_runs/FREEZE_CHECK.txt` | `11fc8fe782f5fb9e22c28483b3e8afad19e690f5ee22c9e0ca8c12e87adfd0ba` |
| `E4a2_runs/E4a2_registered.json` | `c8877e6ca376a04300eebd3c69d906ba06a5b8dec30c5747d701a23718471d6b` |
| `E4a2_runs/build_e4a2.py` | `f788ba740938777f60621e9bf6bcacbb7e0682ef5192657f49fdb866ab9a2c9b` |
| `E4a2_runs/analyse_e4a2.py` | `26a10ef4d55319b8de01988a2d24631f15a680ae91dc066d6aab9e1096cf7261` |
| `E4a2_runs/mark_done_e4a2.py` | `48c01195f10bd6d97ddde69f5ace586cf4a9e4953f93e4fa9b6299ac937d4aae` |
| `E4a2_runs/run_one_e4a2.sh` | `9c01d3d70453c5698f74c709ae150a96134b4c024ba84e9824f4a30f6245c09d` |
| `E4a2_runs/launch_e4a2.sh` | `2444d9644e9065d0afcbb5f3929674ed85f89ddc174fab6c206bc9567dbd9659` |

Frozen imports, re-verified against the blobs committed at `628e29c4` at every
invocation and printed at the head of the comparator log — `E4_runs/`
`E4a_registered.json` `bb363d02…0401b05`, `build_e4a.py` `451eae36…c665e46956`,
`analyse_e4a.py` `a9f31c3f…d5d63ff4b`, `mark_done_e4a.py` `b152ed00…35b4d10fbe6`,
`run_one_e4a.sh` `226fd26b…d024f12ffe19`, `launch_e4a.sh` `0e2b893f…4ead9c81274`;
and `T1_runs/analyse_t1c.py` `60893b28…6ee7e6c5135`.

**`--selftest`: SELFTEST 95/95 OK, exit 0**, run from `E4a2_runs` before the
build against zero case trees, matching the count stamped in `FREEZE_CHECK.txt`
at the freeze.

**No frozen file was edited.** The `in_dir` redirect declared in §4 restored the
frozen modules' `HERE` on every use — both the comparator and the marker refuse
if it does not, and neither refused.

---

## 8. What changed on disk

Written by this lane, all under `verification/runs/T-family/E4a2_runs/` except
the last two lines:

* five case directories `F_c/ F_m/ F_f/ S_f/ N_f/` — dictionaries from
  `build_e4a2.py`, `0.orig/`, `0/`, **30 numeric checkpoints each**,
  `log.blockMesh`, `log.checkMesh`, `log.solve`, `log.solve.time`,
  `LAUNCH_LOCK/{launch.log,solver.pid}`;
* `BUILD_MANIFEST.txt` (42 lines);
* `STATUS.F_c STATUS.F_m STATUS.F_f STATUS.S_f STATUS.N_f` (five, all rc=0);
* `DONE.F_c DONE.F_m DONE.F_f DONE.S_f DONE.N_f` (five);
* `log.mark_done.20260824T173456Z.txt`, `log.analyse_e4a2.20260824T173504Z.txt`;
* `E4a2_runs/RECORDS_DRAFT.txt` — draft ledger and docket row text, filed under
  the case directory it belongs to and **not** in a scratchpad (rule 13);
* this file, `docs/campaigns/T-family/E4a2_RESULTS.md`.

**No `__pycache__` was created anywhere.** The 19 pre-existing `.pyc` files
under `verification/runs/T-family/` were enumerated with mtimes before the
selftest and again after the comparator: **identical, path for path and
nanosecond for nanosecond**. `E4a2_runs/` and `E4_runs/` hold none.

**No tracked file was modified and nothing was committed.** `git status` reports
**phantom staged deletions** of all seven frozen E4a2 files — the **D486**
shared-index decay, not a rogue writer. Each was checked against `HEAD` and is
**byte-identical on disk** (`c8877e6c…`, `11fc8fe7…`, `26a10ef4…`, `f788ba74…`,
`48c01195…`, `9c01d3d7…`, `2444d964…`). Per rule 10 the condition was
**inspected, never reverted**; the index is the chief's call.

---

## 9. Supervisor's read (2026-08-24)

The four `SUPERVISION_CHARTER.md` §3 checks are the supervisor's personally and
are not delegable. They were done, and the supervisor's own words are quoted:

1. **Measurement scripts read as diffs, before the freeze commit.** *"The
   comparator, builder and marker were read as diffs against the frozen E4a
   instruments after inverse rename BEFORE the freeze commit `cd1f46e1` — no
   rule re-implemented, every grading path the frozen E4a function via a
   restoring `in_dir` redirect with refusal."*
2. **The gate block and every row read from the comparator's own output, after
   the run.** *"The gate block and every row were read from the 17:35:04Z log
   after the run; worst C1 1.113e-09, worst C3 2.526e-10, C2 nowhere."*
3. **The LIMIT CYCLE classification, carried rather than smoothed.** *"The
   LIMIT CYCLE classification on F_c/F_f/N_f while passing is a pre-registered
   property (§2.2: no interval-to-interval growth ratio is gated) and is carried
   as reported, with the plain statement that the rung certifies a stationary
   bouncing iterate, not a monotone settle."*
4. **First crossing at 4 000, read as a cost fact and not a verdict.** *"First
   crossing at 4 000 on all five: the registered `endTime` bought margin, not
   convergence — a successor's cost-model observation, gates closed."*

**Record ids were re-derived at commit time, not copied**, and this rung watched
rule 11 earn itself inside twenty minutes: at the start of drafting HEAD was
`8871acf3` with tails **C-29 / D498 / L-276**; HEAD moved to `dfe5292d` while
the lane was still writing (a dafoam peer landing L-277, L-278 and its own
rows), and the same tails re-derived at the new HEAD read **C-32 / D502 /
L-278**. Neither reading was copied into a record. The eight frozen E4a2 files
were re-hashed against `cd1f46e1` after HEAD moved: **no drift**.
