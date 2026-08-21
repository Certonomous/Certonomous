# T1b fourth grid level (x): Charter 2b amendment and addendum, registered before any solve

Campaign T, tier 1, rung T1b, fourth grid level. **Written 2026-08-21,
18:05-18:15 Z, before any `R_*_x` case had solved; the four case directories
were built and meshed during this window and no solver has been launched.**
Answers D440 (`T1b_RESULTS.md` section 8: "a fourth level at y+ ~ 0.38 is the
instrument the next rung needs, and it is proposed, not run"). Approved by
Sanaa on 2026-08-21: *"the T1b fourth grid level (wall-refined, ~$5) is
approved - run it under the T1b design with the comparator amended to gate
on the triple state (disclosed as a Charter 2b amendment, the frozen original
left untouched)."* Docket entry: to be assigned at commit (the next free
number after D442); it answers D440.

---

## 0. What is frozen and what this document is

**The frozen instruments are left untouched.** sha256 at the start and at the
end of this work, byte-identical:

| file | sha256 (first 16) | status |
| --- | --- | --- |
| `analyse_t1b.py` | `647d74121677e529` | frozen at 08732fd6 (2026-08-19 19:10:04 Z); NOT edited, NOT re-run |
| `build_t1b.py` | `c65d865e7d2be5df` | NOT edited; imported and called |
| `check_t1b_mesh.py` | `9da34820fb36a9ad` | NOT edited; its `check()` imported and called |
| `mark_done_t1b.py` | `00bef3c5cde56af1` | NOT edited; its field list and parsers imported |
| `mark_done_t1b_ext1.py` | `161c58e568d0719e` | NOT edited |
| `T1b_RESULTS.md` | mtime 2026-08-21 16:48:47 Z | NOT edited; its verdicts stand as returned |
| `T1b_band.json` | committed before any case existed | NOT edited; the band read here |

**None of the nineteen attempt-2 case directories was opened for writing.**

**This is a Charter 2b amendment under clause 1 (before first compute), and
the condition was checked, not asserted.** At 2026-08-21 18:05:21 Z, before
`build_t1b_L4.py` was written, `find verification/runs/T-family/T1_runs
-maxdepth 1 -name "R_*_x"` returned nothing and `-name "*L4*"` returned
nothing: no fourth-level case, comparator, builder, marker, launcher or gate
file existed. **With respect to the frozen rung it is a 2b clause 2 addendum**:
the frozen comparator's four PASS verdicts on DIVERGENT or STAGNANT triples
are not edited, struck or re-graded; they are printed beside the amended
verdicts for the record (section 2). The amended rule itself was registered
as a candidate on 2026-08-20 (`T1b_RESULTS.md` section 8, D440) and made
binding for T3 on 2026-08-21 (`T3_PREREGISTRATION.md` 7.1) before this
document existed; nothing in it was chosen with an x-level number in view,
because no x-level number exists.

---

## 1. The fourth level, registered

The frozen ladder `RESOLVED = {c: (50, 250, 1.6), m: (80, 400, 1.0),
f: (128, 640, 0.625)}` is (radial cells, axial cells, first-cell-centre y+),
every count and the y+ target scaling by 1.6 per level. The fourth level
continues it:

| level | radial | axial | cells | target y+ (cell centre) | ratio to the level below |
| --- | ---: | ---: | ---: | ---: | --- |
| c | 50 | 250 | 12 500 | 1.6 | |
| m | 80 | 400 | 32 000 | 1.0 | 1.6 / 1.6 |
| f | 128 | 640 | 81 920 | 0.625 | 1.6 / 1.6 |
| **x** | **205** | **1024** | **209 920** | **0.390625 = 0.625 / 1.6** | **205/128 = 1.6016 radial, 1024/640 = 1.6000 axial; sqrt(209920/81920) = 1.6008 on cell count** |

205 is `round(128 x 1.6 = 204.8)`. The effective ratio from the counts is
1.6008 on cell count (1.6016 radially, 1.6000 axially); `analyse_t1c.gci()`
uses `R_REFINE = 1.6` unchanged, and the 0.05 % difference moves an observed
order by a factor `ln 1.6 / ln 1.6008 = 0.9995`, which changes no state
classification at any order this rung could return. Four cases, one per
Reynolds number, `D = 0.2 m`, `L = 100 D`, `nu = 1.5e-5`, `Pr = 0.71`,
`Prt = 0.85`, `kOmegaSST` low-Re, the lab's validated wall set, stations
60/70/80 D, all exactly as the frozen builder writes them:

| case | Re | U (m/s) | first cell (m) | cell ratio | expansion (axis/wall) | endTime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `R_10k_x` | 1e4 | 0.75 | 2.490858e-04 | 1.006000 | 3.39 | 20 000 |
| `R_30k_x` | 3e4 | 2.25 | 9.581404e-05 | 1.013236 | 14.62 | 80 000 |
| `R_100k_x` | 1e5 | 7.5 | 3.294769e-05 | 1.020412 | 61.69 | 80 000 |
| `R_300k_x` | 3e5 | 22.5 | 1.226111e-05 | 1.026615 | 212.42 | 80 000 |

**The builder is `build_t1b_L4.py`, which imports `build_t1b.py` and calls its
`build()` with the new level**; it copies no grading, mesh, dictionary or
`CASE.txt` code, so the reciprocal radial `simpleGrading (1 1/expansion 1)`
that attempt 1 got wrong (L-142, D437) and every dictionary are identical in
form to the twelve solved `R_*` cases. The only other lever is `endTime`,
applied by setting the frozen builder's `END_TIME` module global for the
duration of the `build()` call, as `build_d_ts.py` sets `B.RE`. Verified
after the build: `fvSolution`, `0.orig/T`, `0.orig/U` and
`transportProperties` of `R_300k_x` are byte-identical to `R_300k_f`'s;
`fvSchemes` differs in no non-numeric token; `controlDict` differs only in
`endTime`. `CASE.txt` is written by the frozen `build()` and then carries four
appended self-describing lines (`level`, `ladder_for`, `refinement_ratio`,
`built_by`).

---

## 2. The amended gating rule, registered

**A `Nu` row whose grid triple is not CONVERGING reports NOT A RESULT, as
`analyse_t1c.py` does; the value and the triple are printed beside it.**
Comparator: `analyse_t1b_L4.py`, new; the frozen `analyse_t1b.py` is imported
for its `measure()` (Nu, f, u_tau, y+ at a station; wall radius read from
`points`; `alphaEff` factor read from the written `alphat`; friction from the
50-80 D pressure drop), `petukhov_f`, `RE_TAGS`, `STATIONS` and
`PLATEAU_FRACTION`; `analyse_t1c.py` for `gci()` and
`iterative_convergence()`; the band from `T1b_band.json`. Nothing in the
measurement can differ from the frozen comparator's because it is the frozen
comparator's code that measures.

Order of evaluation for every `Nu` row, per Reynolds number:

1. any level of **(m, f, x)** NOT iteratively CONVERGED (written `T` field
   between the last two checkpoints, relative change above 1e-6 of the range),
   or not plateaued across 60/70/80 D (spread above 0.2 x band)
   -> **NOT A RESULT**;
2. the **(m, f, x)** triple not CONVERGING as `gci()` classes it (DIVERGENT
   at `p <= 0`, STAGNANT at `0 < p < 0.5`, OSCILLATORY, EXACT)
   -> **NOT A RESULT**, with the x value, its deviation, both triples and the
   orders printed beside it;
3. CONVERGING -> **PASS** if the x-level `Nu` lies within the band of
   `T1b_band.json` (the correlations' half-spread, 2.84 / 3.89 / 5.33 /
   5.75 %), else **GATE FAIL**; the GCI of the x level is printed beside the
   verdict and does not replace the band (that is T1c's rule, not this one).

**Both triples are reported at every Re**: (c, m, f) with its state and
order, as the frozen comparator graded it, and (m, f, x). **The frozen
comparator's verdict on (c, m, f) is printed beside, read from
`gate_t1b.json`, for the record**: B0/B2/B4/B6 PASS on DIVERGENT / DIVERGENT
/ DIVERGENT / STAGNANT. The friction triples (c, m, f) and (m, f, x) are
REPORTED the same way, against Petukhov, as the attribution lever. Rows are
tagged `X0..X7`. Output `gate_t1b_L4.json`; `gate_t1b.json` is not rewritten.

**What the rule can and cannot do.** It can only turn a PASS or a GATE FAIL
into NOT A RESULT; it cannot move a value, a reference or a band, and it
cannot make a value pass that the frozen rule, applied to that same value, would fail. A CONVERGING (m, f, x)
triple means the x-to-f step has fallen to at most `1.6^-0.5 = 0.79` of the
f-to-m step; it does not mean a limit has been reached.

**The comparator refuses unless `DONE.<case>` exists for all sixteen
cases**: the twelve `R_*_{c,m,f}` (markers written by `mark_done_t1b_ext1.py`
on 2026-08-21, not re-judged here) and the four `R_*_x` (markers from
`mark_done_t1b_L4.py`, section 7). It does not re-grade the Prt
discrimination, the wall-function comparison or `C_lam`; those are the
frozen rung's rows.

**`--selftest`**, run 2026-08-21 before any solve, proves on synthetic
triples at the Re = 1e4 band that DIVERGENT, STAGNANT, OSCILLATORY and EXACT
triples whose x value lies INSIDE the band return NOT A RESULT, that
CONVERGING reaches both PASS and GATE FAIL by moving the x value (the
mutation control), that the frozen rule returns PASS on the same DIVERGENT
triple (the defect being closed), and that the recorded T1b (c, m, f) triples
at 1e4 and 3e5 read PASS under the frozen rule and NOT A RESULT under the
amended one. Output in section 9.

---

## 3. Registered predictions, before any solve

**3.1 The measured steps.** `T1b_RESULTS.md` section 8: `Nu` rises by a
near-constant step per 1.6x refinement, c->m / m->f:

| Re | c | m | f | step c->m | step m->f | ratio (m->f)/(c->m) | y+ achieved c / m / f |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1e4 | 30.119 | 30.831 | 31.619 | +0.711 | +0.789 | 1.108 | 1.55 / 0.98 / 0.62 |
| 3e4 | 69.103 | 70.732 | 72.480 | +1.629 | +1.748 | 1.073 | 1.53 / 0.97 / 0.61 |
| 1e5 | 177.506 | 181.582 | 185.771 | +4.076 | +4.189 | 1.028 | 1.53 / 0.97 / 0.61 |
| 3e5 | 430.220 | 439.761 | 449.255 | +9.541 | +9.494 | 0.995 | 1.53 / 0.97 / 0.61 |

**3.2 The x-level `Nu`, by extrapolating the last step once more** (the
prediction is the step repeated; a growing step as at 1e4-1e5 gives a larger
value, a shrinking one as at 3e5 a smaller one):

| Re | predicted `Nu_x` | reference | deviation | band | where it would land if graded |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1e4 | **32.41** | 30.907 | 4.86 % | 2.84 % | **OUTSIDE** the band, moving away from it |
| 3e4 | **74.23** | 73.684 | 0.74 % | 3.89 % | inside, having crossed the reference from below |
| 1e5 | **189.96** | 190.398 | 0.23 % | 5.33 % | inside, just below the reference |
| 3e5 | **458.75** | 456.723 | 0.44 % | 5.75 % | inside, having crossed the reference from below |

**3.3 Will the (m, f, x) triples come back CONVERGING? Prediction: NO, at all
four Reynolds numbers.** With the step repeated exactly, `e32/e21 = 1`,
`p = 0.000`, and `gci()` classes that DIVERGENT (`p <= 0`). **A CONVERGING
triple requires `p >= 0.5`, i.e. the f->x step at most `1.6^-0.5 = 0.79` of
the m->f step**: `Nu_x <= 32.24` at 1e4 (step <= 0.62), `<= 73.86` at 3e4
(step <= 1.38), `<= 189.08` at 1e5 (step <= 3.31), `<= 456.76` at 3e5 (step
<= 7.51). No Re has yet shown a step ratio below 0.995, and the reason
registered in section 8 of the results is that the step tracks the first-cell
y+ of the low-Re `kOmegaSST` wall treatment (1.53 -> 0.97 -> 0.61 -> 0.39
across the four levels) rather than an asymptotic range. The ratio does fall
with Re (1.108, 1.073, 1.028, 0.995), so **if any triple converges it is
predicted to be 3e5 first, and that would be STAGNANT-to-CONVERGING by a
small margin, not a clean second-order triple.** Consequence under the
amended rule if the prediction holds: **four NOT A RESULT rows, the x values
and both triples printed beside them, and the x level reported as the fourth
point on a direction rather than a limit.** If the prediction fails at a
given Re, that row is graded (section 2, step 3) and the prediction's failure
is the finding: the wall treatment reached its asymptotic range between y+
0.61 and 0.39.

**3.4 Friction, the attribution lever, same extrapolation** (`f` c/m/f and
the last step repeated):

| Re | f c / m / f | predicted `f_x` | Petukhov | predicted shortfall | CONVERGING needs `f_x <=` |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1e4 | 0.02960 / 0.03028 / 0.03106 | 0.03184 | 0.03148 | +1.14 % (crosses above) | 0.03168 |
| 3e4 | 0.02181 / 0.02233 / 0.02290 | 0.02348 | 0.02364 | -0.67 % | 0.02336 |
| 1e5 | 0.01652 / 0.01691 / 0.01733 | 0.01774 | 0.01799 | -1.39 % | 0.01766 |
| 3e5 | 0.01327 / 0.01358 / 0.01389 | 0.01420 | 0.01444 | -1.60 % | 0.01414 |

Prediction: the friction triples (m, f, x) are also NOT CONVERGING, and the
shortfall against Petukhov shrinks from 1.3-3.8 % to about 0.7-1.6 % at
3e4-3e5 while at 1e4 `f` crosses above Petukhov. Friction is REPORTED, not
gated.

**3.5 Achieved y+.** The fine levels landed at 0.61-0.62 against a target of
0.625 (the wedge `cos(theta/2)` factor and the friction shortfall); the x
level is predicted to land at **0.38-0.39** against 0.390625, read from the
written fields as always, never assumed.

**3.6 Iterative convergence at the registered endTime.** Fine levels needed
20000 (1e4, 1.8e-07 K between 18000 and 20000), 40000, 58000 and 68000
iterations to reach 0.0 K between their last two checkpoints. On a mesh 1.6x
finer in each direction the iteration count to the same state is expected to
rise, roughly with the count per direction. Prediction: **`R_10k_x` is NOT
CONVERGED at 20000 and needs the section 4 extension (to about 32000);
`R_30k_x`, `R_100k_x`, `R_300k_x` are CONVERGED by 80000** (fine-level
counts times 1.6 are 64000 / 92800 / 108800, so 1e5 and 3e5 are at risk of
needing an extension as well; that is why the protocol is registered here
rather than decided later).

---

## 4. endTime, checkpoints, and the extension protocol

| case | endTime | writeInterval | purgeWrite | checkpoints compared by the gate |
| --- | ---: | ---: | ---: | --- |
| `R_10k_x` | 20 000 | 2 000 | 2 | 18000 vs 20000 |
| `R_30k_x` | 80 000 | 2 000 | 2 | 78000 vs 80000 |
| `R_100k_x` | 80 000 | 2 000 | 2 | 78000 vs 80000 |
| `R_300k_x` | 80 000 | 2 000 | 2 | 78000 vs 80000 |

`writeInterval` strictly below `endTime` (L-140: durability, and the gate
needs two checkpoints); `purgeWrite 2` keeps the last two sets (about 30 MB
each at 209 920 cells in ascii, writePrecision 16). `residualControl` is the
frozen builder's and is inoperative in a wedge (L-141); every case runs to
`endTime`, and the state is decided by the written fields.

**Extension protocol, registered now so that no `endTime` is ever chosen with
a `Nu` in view (T1b section 6.2, T3 7.1 form).** If `iterative_convergence()`
reports a level NOT_CONVERGED at its `endTime`: the case is resumed from
`latestTime` to a raised `endTime` by an extension runner of the
`run_one_ext1.sh` form (checkMesh to `log.checkMesh.ext1`, solver appending
to `log.solve.ext1`, `log.solve` untouched, `STATUS_ext1.<case>` beside
`STATUS.<case>`); the raised `endTime` is the smallest multiple of 2000 at or
above 1.6 times the fine level's converged count (32000 / 64000 / 92800 ->
94000 / 108800 -> 110000), and a second extension, if needed, repeats the
step; **the decision is taken on the convergence state alone and is
disclosed in the results record with the time it was taken, the first
extension `Time` (exactly `endTime + 1`), and which rows rest on it.**
`mark_done_t1b_L4.py` already judges an extended case across both segments
(section 7).

---

## 5. Cost prediction, from measured throughput

`nProcs = 1` on every case, as on every T1b case; core-hours = wall seconds /
3600; 0.0513 USD per core-hour (`T1b_RESULTS.md` section 10).

**Throughput, measured on the fine levels' original segment** (20 000
iterations on 81 920 cells, wall 22 900 / 23 533 / 22 163 / 20 734 s at
1e4 / 3e4 / 1e5 / 3e5, nineteen cases concurrent on sixteen cores with other
teams' jobs, so a lower bound on throughput and an upper bound on cost):

| Re | cell-iterations / s | x cells | endTime | predicted wall | core-hours | USD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1e4 | 71 546 | 209 920 | 20 000 | 58 700 s (16.3 h) | 16.3 | 0.84 |
| 3e4 | 69 621 | 209 920 | 80 000 | 241 200 s (67.0 h) | 67.0 | 3.44 |
| 1e5 | 73 925 | 209 920 | 80 000 | 227 200 s (63.1 h) | 63.1 | 3.24 |
| 3e5 | 79 020 | 209 920 | 80 000 | 212 500 s (59.0 h) | 59.0 | 3.03 |
| **total** | | | | **739 600 s** | **205.4** | **10.54** |

**Against Sanaa's ~5 USD: the registered endTimes cost about twice that on
the measured contended throughput.** 5 USD buys 97.5 core-hours, which at
these rates is roughly `R_10k_x` to 20 000 plus the other three to about
35 000 each, below the 40 000 / 58 000 / 68 000 the fine levels themselves
needed. Two honest alternatives, for the decision that is Sanaa's and not this
document's:

| schedule | endTimes | core-hours | USD |
| --- | --- | ---: | ---: |
| registered (section 4) | 20000 / 80000 / 80000 / 80000 | 205.4 | 10.54 |
| same, at the extension segment's less-contended throughput (91 271 / 115 866 / 143 515 cell-it/s at 3e4 / 1e5 / 3e5; 1e4 taken at the 3e4 rate) | same | 136.7 | 7.01 |
| endTime at the fine levels' converged counts, extension if needed | 20000 / 40000 / 58000 / 68000 | 145.7 | 7.48 |
| all four to 20000 only (the original-segment shape) | 20000 x 4 | 63.6 | 3.26 |

The wall column includes whatever contention the box carries at launch (the
T3 rung launches first, per Sanaa), so the 10.54 USD is an upper bound and
the 7.01 USD a less-contended estimate; the cost is governed by `endTime`,
not by convergence, because `residualControl` cannot stop a wedge case. The
registered endTimes stand unless Sanaa amends them **before the first launch**,
which is legal under 2b clause 1 and must be noted here with its time.

---

## 6. Mesh verification from the written points, before any solve

`check_t1b_L4_mesh.py` imports `check_t1b_mesh.check()` unchanged and runs
it on the four x meshes after `blockMesh` and `checkMesh` (2026-08-21
18:07 Z). Measured straight from each case's `constant/polyMesh/points`:

| case | radial cells | cells (checkMesh) | wall cell, points (m) | designed (m) | off | axis/wall | smallest cell at wall | max aspect ratio | AR / fine level | non-orthogonality | skewness | checkMesh |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| `R_10k_x` | 205 | 209 920 | 2.488488e-04 | 2.490858e-04 | 0.095 % | 3.4 | yes | 79 | 0.999 | 0 | 0.331 | Mesh OK |
| `R_30k_x` | 205 | 209 920 | 9.572285e-05 | 9.581404e-05 | 0.095 % | 14.6 | yes | 204 | 1.000 | 0 | 0.331 | Mesh OK |
| `R_100k_x` | 205 | 209 920 | 3.291633e-05 | 3.294769e-05 | 0.095 % | 61.7 | yes | 593 | 1.000 | 0 | 0.331 | Mesh OK |
| `R_300k_x` | 205 | 209 920 | 1.224943e-05 | 1.226111e-05 | 0.095 % | 212.4 | yes | 1 595 | 1.000 | 0 | 0.331 | Failed 1 mesh check (aspect ratio, 18 432 cells) |

All four PASS the frozen checks A-D (wall cell is the design value to
0.095 %, which is the wedge `cos(2.5 deg)` factor and nothing larger; the wall
cell is the SMALLEST radial cell and the axis cell the largest; the cells sum
to the wall radius; the grading is geometric at the builder's ratio) and the
new check E: **the maximum aspect ratio is the fine level's to 0.1 %** (79 vs
78.6, 204 vs 204.2, 593 vs 593.5, 1595 vs 1594.6), because radial and axial
spacings both shrank by 1.6, which is what makes the ladder uniform and the
observed order meaningful (`T1b_DESIGN.md` 4a). The `R_300k_x` aspect-ratio
failure is the same inherent one every resolved 3e5 mesh carries (1594.6 on
`R_300k_f`), recorded rather than hidden; non-orthogonality 0 and skewness
0.331 on all four. No solver has run: each case holds `0.orig`, `constant`,
`system`, `CASE.txt`, `log.blockMesh`, `log.checkMesh` and nothing else.

---

## 7. Completion rule, age guard, launch discipline

**Completion.** `mark_done_t1b_L4.py` writes `DONE.R_*_x` under the six tests
of `mark_done_t1b.py`, importing its field list and parsers and reading
`STATUS.<case>` (the pool format `rc= wall= checkMesh_rc=`) in place of
`STATUS2`: rc = 0; an `End` line; last time = `endTime`; `T U p_rgh alphat
nut k omega` present; `ExecutionTime` count = `endTime`; every field at
`endTime` NEWER than the case's own `0/T`. For an extended case
(`log.solve.ext1` present) it applies `mark_done_t1b_ext1.py`'s form: both
STATUS files rc = 0, `End` in both logs, counts summing to `endTime`, first
extension `Time` exactly one past the original count, fields newer than `0/T`
AND than `STATUS.<case>`; a failing extended case has any stale marker
REMOVED with the reasons printed. Dry-run 2026-08-21 18:08 Z: 0/4, "no STATUS
file (case never finished)" on each, as it must be before any solve.

**Age guard (D438, L-143).** `run_one_t1b_L4.sh` creates `0` from `0.orig`
and touches `0/T` LAST, so its mtime dates the run allowed to produce the
answer; G3 refuses a case in which `0` or any numeric time directory already
exists, so a stray write from any earlier process can neither be overwritten
nor certified.

**Launch.** `launch_t1b_L4.sh <case>` accepts only the four x names, takes
`LAUNCH_LOCK` atomically (G1), refuses if any process has the case directory
as its cwd (G2) or if a solution time directory exists (G3), then detaches
`run_one_t1b_L4.sh` with `setsid nohup`; the runner re-checks G1 (first to
claim `solver.pid`, noclobber), G2 and G3 before `cd`, re-runs `checkMesh`
into `log.checkMesh`, solves serially into `log.solve`, and writes
`STATUS.<case>`. Nothing in either script kills a process; neither has been
run. **Sanaa launches when cores free; the T3 rung launches first.**

**The analysis sequence, registered**: `mark_done_t1b_L4.py` (markers only
where the rule is met) -> `analyse_t1b_L4.py` (refuses on any missing marker
among the sixteen) -> `gate_t1b_L4.json` -> a dated results addendum under
`T1b_RESULTS.md`'s numbering, with the frozen verdicts beside, the
predictions of section 3 scored one by one, and the cost measured against
section 5. Before analysis the comparator is hashed against its committed
blob (Charter 2d test).

---

## 8. What this level cannot see

- Whether either correlation is right; the band is their disagreement.
- A mesh-converged `Nu` at any Re, unless a triple comes back CONVERGING;
  even then the GCI bounds the fine-to-x step, not the distance to a limit.
- Anything from the wall-function or Prt arms at the x level; they are not
  built, and the frozen rung's rows for them stand.
- Aspect-ratio damage except through the observed order and the friction
  row, both reported per Re.
- Whether the step's dependence on the first-cell y+ would continue below
  0.39; a fifth level is not proposed.

---

## 9. The selftest, as run before any solve

```
selftest: reference 30.907, band 0.879 (2.844 %)
  ok  DIVERGENT inside band              (29.746, 30.546, 31.346) -> DIVERGENT p=+0.000               dev 1.422 % -> NOT A RESULT  (expected NOT A RESULT)
  ok  STAGNANT inside band               (29.646, 30.546, 31.346) -> STAGNANT p=+0.251                dev 1.422 % -> NOT A RESULT  (expected NOT A RESULT)
  ok  OSCILLATORY inside band            (31.846, 30.846, 31.346) -> OSCILLATORY                      dev 1.422 % -> NOT A RESULT  (expected NOT A RESULT)
  ok  EXACT (f == x) inside band         (30.846, 31.346, 31.346) -> EXACT                            dev 1.422 % -> NOT A RESULT  (expected NOT A RESULT)
  ok  CONVERGING inside band             (30.346, 31.096, 31.346) -> CONVERGING p=+2.337 GCI=0.498 %  dev 1.422 % -> PASS  (expected PASS)
  ok  CONVERGING outside band            (31.665, 32.415, 32.665) -> CONVERGING p=+2.337 GCI=0.478 %  dev 5.687 % -> GATE FAIL  (expected GATE FAIL)
  ok  CONVERGING, x outside, f inside    (29.346, 31.346, 32.246) -> CONVERGING p=+1.699 GCI=2.854 %  dev 4.334 % -> GATE FAIL  (expected GATE FAIL)
  frozen rule on the DIVERGENT triple: PASS (DIVERGENT p=+0.000) -- this is the defect the amendment closes
  T1b (c,m,f) at Re 10000 as recorded: frozen PASS, amended NOT A RESULT (DIVERGENT)
  T1b (c,m,f) at Re 300000 as recorded: frozen PASS, amended NOT A RESULT (STAGNANT)
SELFTEST PASSED
```

Run without `--selftest` at the same time, the comparator returned
`REFUSE: no completion marker for R_100k_x, R_10k_x, R_300k_x, R_30k_x`
(exit 2) and wrote nothing.

---

## 10. Files this amendment registers

All under `verification/runs/T-family/T1_runs/` unless stated; none existed
before 2026-08-21 18:05 Z.

| path | role |
| --- | --- |
| `docs/campaigns/T-family/T1b_L4_AMENDMENT.md` | this document |
| `build_t1b_L4.py` | builds `R_*_x` only, by calling the frozen builder |
| `check_t1b_L4_mesh.py` | mesh verification reusing `check_t1b_mesh.check()`, plus checkMesh reading and check E |
| `mark_done_t1b_L4.py` | completion markers, extension-aware |
| `analyse_t1b_L4.py` | the amended comparator, with `--selftest` |
| `launch_t1b_L4.sh`, `run_one_t1b_L4.sh` | G1-G3 launcher and detached runner, STATUS in pool format |
| `R_10k_x/`, `R_30k_x/`, `R_100k_x/`, `R_300k_x/` | the four cases, meshed, unsolved |
| `gate_t1b_L4.json` | written by the comparator at analysis time; does not exist yet |
