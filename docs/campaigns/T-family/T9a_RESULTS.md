# T9a results: composite wall and fin efficiency against exact theory

Campaign T, tier 4, rung T9a, attempt 1. Written 2026-08-21, from a solve
completed 2026-08-20 19:08:30 Z. Run tree
`verification/runs/T-family/T9a_runs/`, 7 cases (`W_c W_m W_f W_C3 F_c F_m F_f`).
Comparator `analyse_t9a.py`, frozen at commit `239ed2b8` (2026-08-20
19:02:01 Z) before any case existed (Charter §2d), verified byte-identical at
analysis time: sha256 `dd2d6bf0…cac9da`; `exact_t9a.py` sha256
`d3f2558c…d3d0b8`; `T9a_registered.json` sha256 `66b03c7d…b40ed`, all three
identical to the committed blobs. First solver start 19:08:20 Z (**+6 min 19 s**
after the freeze), earliest completion marker 19:08:52.6 Z (**+6 min 51.6 s**).

**Rung verdict: GATE FAIL — 1 of 3 graded rows failed. R0 (wall flux) and R2
(interface 2) PASS; R1 (interface temperature after layer 1) GATE FAIL at
−2.41 mK against a 0.92 mK GCI band; the two fin rows R3 and R4 are GATE
REACHED — reported, not graded — because their armed bands (0.00077 %,
0.00011 %) fall below the registered 0.025 % one-dimensionality floor of the
fin equation; all four controls MET (fail, as they must); 0 NOT A RESULT.**
Analysed 2026-08-20 19:09:06 Z (`gate_t9a.json`); re-run 2026-08-21 17:51:15 Z
by this report, reproducing the JSON byte for byte (sha256 `7c4c6826…f4f8`).
Docket D442.

---

## 1. The rows

Reference is closed form, re-derived two independent ways by `exact_t9a.py`
(series resistance versus a harmonic-face FV solve; `tanh(mL)/mL` versus a
second-order FD solve) at every comparator run, which refuses unless the two
agree — they agreed to 8.4e-11 (wall) and 9.5e-09 / 1.5e-08 (fin), and the
registered decimals to 2e-08 or better. The value graded is the **finest** level
of the three-level ladder; the band is that row's own Roache GCI (`Fs` 1.25,
nominal `r` 1.6) on the finest level; deviation is a percentage of the exact
value. Every geometric constant is read from `constant/polyMesh/points`.

| row | quantity | value (finest) | exact | deviation | band (GCI) | grid triple c → m → f | observed `p` | verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| R0 | wall `q″` [W/m²] | 19.854991 | 19.502682 | 1.806 % | 2.043 % | 20.425588 → 20.069440 → 19.854991, CONVERGING | 1.079 | **PASS** |
| R1 | wall `T` interface 1 [K] | 348.778673 | 348.781082 | 0.00069 % (−2.41 mK) | 0.00026 % (0.92 mK) | 348.775652 → 348.777747 → 348.778673, CONVERGING | 1.738 | **GATE FAIL** |
| R2 | wall `T` interface 2 [K] | 300.023872 | 300.024378 | 0.00017 % (−0.51 mK) | 0.00025 % (0.75 mK) | 300.022999 → 300.023532 → 300.023872, CONVERGING | 0.952 | **PASS** |
| R3 | fin efficiency `η` | 0.8331737 | 0.8332367 | 0.00756 % | 0.00077 % < 0.025 % floor | 0.8331455 → 0.8331658 → 0.8331737, CONVERGING | 1.990 | **GATE REACHED** (reported, not graded) |
| R4 | fin tip ratio `1/cosh(mL)` | 0.7523951 | 0.7523781 | 0.00226 % | 0.00011 % < 0.025 % floor | 0.7523988 → 0.7523962 → 0.7523951, CONVERGING | 1.997 | **GATE REACHED** (reported, not graded) |

| level | wall cells (layers 1/2/3) | fin cells `nx × ny` | refinement read from the mesh |
| --- | ---: | ---: | --- |
| c | 35 (10/20/5) | 500 (50 × 10) | — |
| m | 56 (16/32/8) | 1280 (80 × 16) | wall 1.600/1.600/1.600; fin 1.600/1.600 |
| f | 90 (26/51/13) | 3328 (128 × 26) | wall 1.625/1.594/1.625; fin 1.600/1.625 |

### 1.1 How each band is produced, and why R1 fails at 0.0007 % while R0 passes at 1.8 %

**There is no common tolerance.** Each row's band is the Roache GCI of its own
triple: `GCI = 1.25 · |f_m − f_f| / |f_f| / (1.6^p − 1)` with
`p = ln|(f_c − f_m)/(f_m − f_f)| / ln 1.6`; a row whose triple is OSCILLATORY,
STAGNANT (`p < 0.5`) or DIVERGENT (`p ≤ 0`) arms no band and is NOT A RESULT
(none occurred). The band therefore measures **how far that quantity was still
moving between the medium and fine meshes**, scaled by the observed order.

- **R0.** `q″` moved 0.3561 then 0.2144 W/m² per refinement (ratio 1.661,
  `p` = 1.079, first order). Band 2.043 % = 0.406 W/m². The finest value sits
  0.352 W/m² (1.806 %) above exact: inside the band, PASS, by 0.88 of the band.
- **R1.** Interface-1 temperature moved 2.10 then 0.93 mK (ratio 2.264,
  `p` = 1.738). Band 0.000263 % of 348.78 K = **0.92 mK**. The finest value
  is **2.41 mK** below exact: 2.63 bands outside, GATE FAIL.
- **R2.** Interface-2 temperature moved 0.53 then 0.34 mK (ratio 1.564,
  `p` = 0.952). Band 0.000251 % = **0.75 mK**. Finest value **0.51 mK** below
  exact: inside by 0.67 of the band, PASS.

The percentages on the temperature rows are of the absolute Kelvin value, which
is why a 2.4 mK miss reads as 0.0007 %. Expressed on the drop the row actually
measures (1.218918 K across layer 1 for R1; 0.024378 K across layer 3 for R2),
R1's deviation is 0.198 % of its drop against a band of 0.075 %, and R2's is
2.08 % of its drop against 3.09 %. **The verdicts do not depend on the
denominator** — deviation and band share it — and are stated here both ways so
the scale of a 2.4 mK gate failure is visible.

**What the R1 failure is.** Against the exact value the three levels are off by
−5.43 / −3.33 / −2.41 mK (ratios 1.63 then 1.38): the error is shrinking at
roughly first order and then slower, not at the `p` = 1.74 the triple's own
differences imply. The GCI takes the differences at face value, reads a
near-second-order triple, and arms a band (0.92 mK) smaller than the finest
level's actual distance from exact (2.41 mK). R2's errors shrink by 1.63 then
1.67 — a clean first-order triple — and its band covers its error. This reading
uses the exact reference itself, so it is **not an instrument independent of the
hypothesis** (Charter §2d.1 condition 2) and grounds no repair; the row is
reported as the frozen comparator returned it, GATE FAIL, with the numbers
beside it.

**The 1.8 % flux excess is the registered exposure, not a surprise.**
`laplacian(DT,T)` was left at `Gauss linear` by registration (`T9a_registered.json`,
`interface_scheme_note`): the face conductivity at the 0.8 | 0.04 interface is
the arithmetic mean 0.42 W/mK where the series-resistance (harmonic) value is
0.0762, and at the 0.04 | 16 interface 8.02 against 0.0798 — one face per
interface is too conductive by a margin that shrinks with `dx`, which is exactly
a first-order error in `q″`, and is what R0's `p` = 1.079 shows. The 400×
contrast was chosen so that this treatment could not hide; it did not.

**The fin rows, reported.** Both fin triples are clean second order
(`p` = 1.990, 1.997) and their bands (6.4e-06 in `η`, 8.4e-07 in the tip ratio)
are 32× and 220× below the registered 0.025 % floor, so by registered §3.1 the
rows are GATE REACHED and not graded. Had there been no floor, both would have
been GATE FAIL: the finest `η` is 0.00756 % below `tanh(mL)/mL` (9.8 bands) and
the tip ratio 0.00226 % above `1/cosh(mL)` (20 bands), and the level errors
(−9.1e-05 / −7.1e-05 / −6.3e-05 in `η`) are converging toward a value a few
1e-05 below the one-dimensional constant, not toward it. That is the fin
equation's own O(Bi) = 0.025 % neglected transverse conduction showing at about
0.3 Bi, the outcome the pre-registration's §3.1 anticipated from T1c: **a
two-dimensional solve disagreeing with one-dimensional theory by less than the
theory's own validity, resolved finely enough to see that it does.**

## 2. Controls, each of which MUST fail

Registered before any case existed (`T9a_registered.json`, `controls`).

| control | realisation | value | graded against | deviation | band | must | verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| C1 wrong resistance rule | finest wall `q″` against `k̄·ΔT/L`, `k̄` the arithmetic mean of the three `k` | 19.8550 | 1650.9804 | 98.80 % | 2.043 % | FAIL | **MET (fails, as it must)** |
| C2 perfect fin | finest `η` against `η = 1` | 0.833174 | 1.0 | 16.68 % | 0.00077 % | FAIL | **MET (fails, as it must)** |
| C3 wall, solved uniform solid (`W_C3`, both faces 350 K) | `q″` | −1.1e-09 | 19.502682 | 100.000 % | 2.043 % | FAIL | fails |
| | `T_i1` | 350.000000 | 348.781082 | 0.349 % | 0.00026 % | FAIL | fails |
| | `T_i2` | 350.000000 | 300.024378 | 16.657 % | 0.00025 % | FAIL | fails → **MET** |
| C3 fin, synthetic uniform field at `T_base` through the identical pipeline on `F_f` | `η` | 0.000000 | 0.833237 | 100.000 % | 0.00077 % | FAIL | fails |
| | tip ratio | 1.000000 | 0.752378 | 32.912 % | 0.00011 % | FAIL | fails → **MET** |

The C2 docstring quotes "20.0 % above the registered 0.8332"; the comparator
forms `|η − 1| / 1` = 16.68 % ((1 − η)/η is 20.02 %). Either figure is four
orders of magnitude above the band. The fin C3 is synthetic by registration: a
solved uniform fin needs `T_inf = T_base`, which makes `η` 0/0.

## 3. Iterative convergence and heat balance

The gate carried from T1c and T1b: no grid claim from a triple containing a
level still moving between its last two written checkpoints. `residualControl`
is absent from every `fvSolution` (L-141); `endTime` 1000, `writeInterval` 100,
`purgeWrite` 2 (L-140), so checkpoints 900 and 1000 exist on every case.

| case | cells | `T` change 900 → 1000, max | field range | relative | state | heat-balance closure |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| W_c | 35 | 0.0 K (internal field byte-identical) | 49.93 K | 0.0 | CONVERGED | 2.14e-11 |
| W_m | 56 | 0.0 K (byte-identical) | 49.96 K | 0.0 | CONVERGED | 4.36e-11 |
| W_f | 90 | 0.0 K (byte-identical) | 49.98 K | 0.0 | CONVERGED | 1.14e-10 |
| W_C3 | 90 | 4.5e-12 K | 5.0e-12 K | 0.91 | NOT_CONVERGED (see below) | 2.17 (see below) |
| F_c | 500 | 1.6e-11 K | 12.12 K | 1.3e-12 | CONVERGED | 4.26e-11 |
| F_m | 1280 | 2.2e-10 K | 12.22 K | 1.8e-11 | CONVERGED | 8.39e-11 |
| F_f | 3328 | 3.4e-11 K | 12.28 K | 2.7e-12 | CONVERGED | 3.66e-11 |

Wall closure is `|q_hot − q_cold| / q̄` from the two discrete boundary fluxes;
fin closure is `|Q_base − Q_conv| / Q_base` with the convective total rebuilt
from the written `valueFraction` over both Robin faces (`F_f`: `Q_base`
0.2082934264, `Q_conv` 0.2082934264 W). The three wall checkpoints differ only in
their `location` header line. The solver (`DICPCG`, tolerance 1e-14) reached an
initial residual of 4e-15 with zero iterations from the second step on the wall
cases; the fin cases ended at 2e-11 initial residual.

**A zero needs a live planted control** (L-141). On a scratch copy of `W_f` and
`F_f`, +1.234e-03 K planted in one cell of `900/T` was recovered by the frozen
`iterative_convergence` reader as `max_change` 1.2340000e-03 K on both, state
NOT_CONVERGED; the case tree was not touched.

**`W_C3` reads NOT_CONVERGED because its relative test divides round-off by
round-off**: the solved field is uniform to 5.0e-12 K, the change between
checkpoints is 4.5e-12 K, and 4.5/5.0 = 0.91 exceeds 1e-06. Its "closure" of
2.17 is likewise `|9.5e-11 − (−2.4e-09)| / 1.1e-09`, three numbers that are all
zero flux to round-off. Neither figure is a defect in the case; both are the
comparator's relative tests applied to a field with no range. The control is
not gated on either (only registered rows are) and is MET; the comparator prints
`unconverged cases: ['W_C3']` in its summary and that line is reproduced here
rather than explained away.

## 4. Mesh

`checkMesh` rc 0 and `Mesh OK` on all seven: non-orthogonality 0, max skewness
2.2e-14 to 2.3e-13, aspect ratio 1 (wall) and 5.00 / 5.00 / 5.08 (fin). Read
from the mesh by `check_t9a_mesh.py` (run 2026-08-21 17:54 Z, `ALL MESHES
VERIFIED`, zero solver compute; no log from an earlier run survives, so whether
it ran on 2026-08-20 is not established): wall thickness 0.17 exactly, a mesh
plane at `x` = 0.05 and 0.15 to 0.0e+00, per-layer counts as registered with
spacing uniform to 7e-13, `0/DT` carrying the registered `k` of its layer in
35/35, 56/56, 90/90, 90/90 cells against cell centres; fin `L` = 0.05,
`t` = 0.002 exactly, `nx × ny` as registered, and the written Robin
`valueFraction` equal to `1/(1 + k/(h·d))` for the mesh's own wall distance `d`
to 1.8e-13 / 2.3e-14 / 1.2e-11. The same checks sit on the comparator's grading
path as refusals and did not fire. The refinement ratio is nominal 1.6; the
ratios the meshes actually carry are 1.600 at the first step and 1.594–1.625 at
the second (integer rounding, as T1c), and the GCI uses the nominal value.

## 5. Provenance and the freeze

| event | time (Z) | evidence |
| --- | --- | --- |
| pre-registration written | 2026-08-19 | `T9a_PREREGISTRATION.md` |
| `exact_t9a.py`, `T9a_registered.json`, `analyse_t9a.py` written | 2026-08-20 18:57:39, 18:59:16, 19:01:15 | file mtimes |
| **comparator frozen**, commit `239ed2b8`, 3 files, 932 insertions, no case directory in the tree | **19:02:01** | `git log`; commit message |
| builder `build_t9a.py` written; seven cases built, `blockMesh` run | 19:03:09; 19:03:30–19:03:31 | mtimes, `log.blockMesh` |
| `check_t9a_mesh.py` written | 19:05:10 | mtime |
| `run_one_t9a.sh`, `run_chain_t9a.sh` written; serial chain starts (`0/` re-copied, `checkMesh`, `laplacianFoam`) | 19:08:20.0 | mtimes, `log.solve` headers, `STATUS.W_c` |
| chain finishes (`F_f` last) | 19:08:30 | `CHAIN_DONE`, `STATUS.F_f` |
| `mark_done_t9a.py` written; 7/7 `DONE.*` markers | 19:08:33; **19:08:52.6** | mtimes recorded before the re-run |
| comparator first run, `gate_t9a.json` | 19:09:02–19:09:06 | `log.writeCellCentres` mtimes, JSON mtime |
| this report: marker tool 7/7, comparator re-run, JSON byte-identical; mesh check | 2026-08-21 17:51:15; 17:54:03 | §6 |

The lab's instrument `scripts/check_comparator_freeze.py` classes
`T9a_runs/analyse_t9a.py` **FROZEN**; it reads marker mtimes, and because the
marker tool re-run of 2026-08-21 rewrote the seven `DONE.*` files (content
unchanged, 16 bytes, "strict rule met") it now reports a margin of +82 155 s.
The margin that applies is the one between the commit and the markers as they
stood before this report touched them, recorded above: **+411.6 s to the
earliest marker, +379 s to the first solver start**. `STATUS.*`, `CHAIN_DONE`
and every `log.solve` header carry the 2026-08-20 19:08 Z times untouched.

## 6. The re-run, and what it changed on disk

`gate_t9a.json` was copied to `gate_t9a.json.pre_rerun_2026-08-21` before
anything ran. `mark_done_t9a.py` reported 7/7 under its six tests (rc 0; `End`
line; last time = `endTime`; `T` and `DT` present; 1000 `ExecutionTime` lines;
final fields newer than the case's own `0/T`). `analyse_t9a.py` then printed
every figure in §1–§3 and exited 1, its own rule for a rung with a GATE FAIL
row; `diff` against the preserved copy is empty and both files hash
`7c4c6826…f4f8`. The comparator did not invoke OpenFOAM (the cell-centre and
volume fields already existed). On disk the re-run changed the seven marker
mtimes (§5) and added the preserved JSON copy; the mesh check added one
`log.writeCellCentres.t0` per case and left `0/T` untouched (19:08:21 Z).

## 7. Disclosure: the solve preceded the ordering approval

`T_FAMILY_INDEX.md` §3 recommends pulling T9a forward and records that "nothing
is reordered without approval; the ordering above is recorded, not applied";
the pre-registration's §6 says the same. **The seven cases were built and
solved on 2026-08-20 between 19:03 and 19:08:30 Z, and first graded at
19:09:06 Z; Sanaa's approval to build and run came on 2026-08-21.** The solve
therefore ran ahead of the ordering approval it was waiting on. It ran inside
the standing compute pre-authorisation — every run under 25 USD (487
core-hours) is pre-authorised (`T3_PREREGISTRATION.md` §10) — at a cost of
0.00012 USD (§8), and it was preceded by the comparator freeze it depended on.
Nothing in the result depends on the order of those two dates; the sequencing
is disclosed because the index said it would not happen unilaterally and it
did. No case was re-run for this report.

## 8. Findings in the frozen instrument, none on the grading path

Reported under Charter §2b(2) and §2d as dated observations; the comparator is
not edited and no verdict moves.

1. **The printed Richardson extrapolate has the wrong sign on every row.**
   `gci()` forms `e21 = f_m − f_f` and returns `richardson = f_f + e21/(r^p − 1)`;
   Roache's extrapolate is `f_f + (f_f − f_m)/(r^p − 1)`. The instrument that
   shows it grades nothing: R0's triple falls monotonically 20.4256 → 20.0694 →
   19.8550, so its limit must lie below 19.8550, and the comparator prints
   20.1795 — above the fine value, back toward the coarse. With the sign
   corrected the extrapolates are 19.5304 W/m² (+0.142 % from exact), 348.77941 K
   (−1.68 mK), 300.02447 K (+0.10 mK), 0.833179 (−0.0069 %), 0.752394
   (+0.0022 %). The `richardson` field is stored in the printed grid-triple
   dict and read by no verdict; the GCI uses `|e21|` and is unaffected. A repair
   cannot change a number a verdict depends on, so it belongs in the next
   comparator and not in this one.
2. **The relative convergence test and the relative closure are undefined on a
   rangeless field** (§3, `W_C3`). Both are reported as printed.
3. **The percent-of-absolute-Kelvin scale on R1 and R2** makes a 2.4 mK gate
   failure read as 0.0007 % (§1.1). Verdicts are invariant to the choice; the
   next exact-theory wall rung should register which scale its deviation is on.

## 9. What this rung cannot see

From the comparator's own docstring and the pre-registration's §5, extended:

- **Conjugate coupling.** Both fluids are boundary conditions (fixed
  temperatures on the wall, a Robin condition on the fin). The coupled
  interface is T9b.
- **Any turbulence or thermal closure.** There is no fluid.
- **Contact resistance, anisotropic or temperature-dependent conductivity**,
  excluded by construction.
- **A harmonic interface treatment.** The scheme was left at `Gauss linear`
  by registration; whether a harmonic `DT` interpolation would pass R1 is not
  something this rung measured.
- **Whether R1's band is representative.** The GCI assumes an asymptotic
  triple; R1's error ratios (1.63, 1.38) say it is not yet there, and only a
  fourth wall level would show whether the 2.4 mK closes. Proposed, not run.
- **The fin's transverse-conduction defect at any resolution coarser than the
  O(Bi) floor**: the rows report a disagreement of about 0.3 Bi and grade
  nothing about it.
- **The geometric ratio at the second refinement step**, which is 1.594–1.625
  by integer rounding while the GCI uses 1.6.

## 10. Cost

`nProcs` 1 on every case, serial chain; the host carried other solver processes
(`run_chain_t9a.sh` comment: 15 on 16 cores), so wall includes contention.
0.0513 USD per core-hour. No numeric cost prediction was registered; the index
said "almost nothing".

| case | cells | `STATUS` wall, s | solver `ExecutionTime`, s |
| --- | ---: | ---: | ---: |
| W_c | 35 | 0.09 | 0.05 |
| W_m | 56 | 0.10 | 0.05 |
| W_f | 90 | 0.09 | 0.06 |
| W_C3 | 90 | 0.10 | 0.06 |
| F_c | 500 | 0.46 | 0.42 |
| F_m | 1280 | 1.49 | 1.45 |
| F_f | 3328 | 5.85 | 5.82 |
| **total** | | **8.18** | **7.91** |

**8.18 core-seconds = 2.27e-03 core-hours = 0.000117 USD** (solver time alone
7.91 s, 0.000113 USD). Comparator and mesh checks: zero solver compute.

## 11. Rung verdict

**GATE FAIL — 1 of 3 graded rows failed. R0 wall `q″` 19.854991 against
19.502682, 1.806 % inside a 2.043 % band (`p` 1.079), PASS; R1 interface 1
348.778673 against 348.781082, −2.41 mK against a 0.92 mK band (`p` 1.738),
GATE FAIL; R2 interface 2 300.023872 against 300.024378, −0.51 mK inside a
0.75 mK band (`p` 0.952), PASS; R3 `η` 0.8331737 and R4 tip ratio 0.7523951
GATE REACHED — reported, not graded — with bands 0.00077 % and 0.00011 % below
the registered 0.025 % floor, deviations 0.0076 % and 0.0023 % inside that
floor; controls C1 (98.80 %), C2 (16.68 %), C3 wall (100 / 0.349 / 16.657 %)
and C3 fin (100 / 32.912 %) all MET; every graded triple CONVERGING; every
graded case CONVERGED with 0.0 K change on the wall levels; comparator
byte-identical to 239ed2b8 and its output reproduced byte for byte on
2026-08-21; 8.18 core-seconds, 0.000117 USD.**
