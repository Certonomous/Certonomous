# T10a results: view-factor enclosures against analytic surface-to-surface exchange

Campaign T, tier EXACT, rung T10a, attempt 1. Written 2026-08-21, from a solve
chain completed 2026-08-21 22:58:15 Z. Run tree
`verification/runs/T-family/T10a_runs/`, 13 cases
(`S_c S_m S_f S_C1 S_f_q S_f_s B_c B_m B_f B_C3 B_f_q B_f_s H_2d`).
Comparator `analyse_t10a.py`, frozen at commit `181a5668` (2026-08-21
19:18:08 Z) before any solve (Charter §2d), **verified byte-identical at
analysis time**: the file that produced the graded rows hashes sha256
`674bac302193…4fe57ca`, equal to `git show 181a5668:…/analyse_t10a.py |
sha256sum` and to the freeze prefix recorded in the pre-registration §12.1;
`exact_t10a.py` (`8efb4d61d445…`) and `T10a_registered.json` (`bdfbd8120ff2…`)
likewise identical to the committed blobs. First solver launch 21:27:08 Z
(**+2 h 09 m** after the freeze), earliest `STATUS` 21:27:10 Z, completion
markers 22:58:46 Z (`mark_done_t10a.py`, strict rule, 13/13).

**One Charter §2d.1 repair, after first compute, disclosed in full in §6:**
the frozen comparator printed every graded row and then crashed with
`ZeroDivisionError` at line 887 (`plant_against`) while reporting the
`C2b_opposite_only` control, whose registered referent for a box side wall is
exactly 0.0 W/m² (the opposite face sits at the same temperature). The
pre-repair stdout is preserved unmodified as `analyse_t10a.out`; the repaired
file (sha256 `ad6a32861dda…434de65`, pre-repair copy kept beside it as
`analyse_t10a.py.pre_repair_2026-08-21`) re-ran to completion as
`analyse_t10a.out.post_repair`, with **every graded row byte-identical between
the two stdouts** (§6). The repair touches only the control-report path, which
executes after all six graded rows are computed and printed; it can change no
graded number, and did not. `gate_t10a.json` (sha256 `02060f39c34f…94b7c29`)
was first written by the post-repair run — the pre-repair crash occurred
before the JSON write. Docket D447.

**Rung verdict: GATE FAIL — the box enclosure grades 3 of 4 rows PASS and one
GATE FAIL; the spheres return no result. B0 floor 6483.263010 vs 6484.920941,
0.02557 % inside a 0.03326 % GCI band (p 0.954), PASS; B1 ceiling
−3269.602153 vs −3265.532221, 0.12463 % against a 0.07676 % band (p 1.480),
GATE FAIL; B2 x-walls −1260.793300 vs −1254.691645, 0.48631 % inside
0.67756 % (p 0.853), PASS; B3 y-walls −1971.177941 vs −1964.697075, 0.32987 %
inside 0.48472 % (p 0.825), PASS. S0 and S1 are NOT A RESULT: both sphere
grid triples are DIVERGENT (orders −3.25 and −1.84), the outcome the
pre-registration's own build-time measurement pointed at — the outer-sphere
raw row-sum defect sits at 4.3–4.8 % at every ladder level and does not
converge (§5.3 there), so refining the mesh does not refine the matrix. All
12 evaluable controls MET (fail, as they must); the 6 sphere-row controls are
UNMEASURED — no band armed on a NOT A RESULT row (Charter §2c boundary
clause 1) — not NOT MET.**

---

## 1. The rows

Reference is closed form (two-surface grey network; Howell C-11/C-14 box view
factors confirmed by a Stokes contour integral), re-derived two independent
ways by `exact_t10a.py` at every comparator run, which refuses on
disagreement. Graded against σ_OF = 5.670408558e-08 W/m²K⁴, READ from
`etc/controlDict` at run time. The value graded is the **finest** level; the
band is the row's own Roache GCI (Fs 1.25, nominal r 1.6, the same `gci()` as
T1c/T9a); qr is read from the written checkpoints, view factors from the
`constant/F` the utility wrote, geometry from `constant/polyMesh`.

| row | quantity | value (finest) | exact (σ_OF) | deviation | band (GCI) | grid triple c → m → f | observed p | verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| S0 | inner sphere q [W/m²] | 3320.340752 | 3374.471705 | — | none armed | 3316.250 → 3316.979 → 3320.341, **DIVERGENT** | −3.253 | **NOT A RESULT** |
| S1 | outer sphere q [W/m²] | −902.808211 | −843.617926 | — | none armed | −906.022 → −905.069 → −902.808, **DIVERGENT** | −1.838 | **NOT A RESULT** |
| B0 | box floor q [W/m²] | 6483.263010 | 6484.920941 | 0.02557 % | 0.03326 % | 6480.760 → 6482.287 → 6483.263, CONVERGING | 0.954 | **PASS** |
| B1 | box ceiling q [W/m²] | −3269.602153 | −3265.532221 | 0.12463 % | 0.07676 % | −3275.664 → −3271.620 → −3269.602, CONVERGING | 1.480 | **GATE FAIL** |
| B2 | box x-walls q, mean [W/m²] | −1260.793300 | −1254.691645 | 0.48631 % | 0.67756 % | −1269.197 → −1264.164 → −1260.793, CONVERGING | 0.853 | **PASS** |
| B3 | box y-walls q, mean [W/m²] | −1971.177941 | −1964.697075 | 0.32987 % | 0.48472 % | −1980.140 → −1974.801 → −1971.178, CONVERGING | 0.825 | **PASS** |

Ladder (read back from the meshes at analysis, refusal on mismatch): spheres
2 400 / 9 216 / 40 560 cells (1 200 / 3 072 / 8 112 radiating faces), box
2 048 / 8 788 / 37 044 cells (1 024 / 2 704 / 7 056 faces). Pair-symmetry
guard on the finest box: x-walls differ by 5.08e-05 relative, y-walls by
3.18e-12. Discrimination (Charter §2c): every graded band is below one tenth
of its row's C2 departure (B0: 0.0333 % < 0.23 %); no GATE REACHED.

### 1.1 What the B1 failure is, and what the sphere DIVERGENT triples are

**B1.** The ceiling triple moves 4.045 then 2.017 W/m² per refinement (ratio
2.005, p = 1.480) and arms a 0.077 % band; the finest value sits 4.070 W/m²
(0.125 %) from exact — 1.62 bands outside. As in T9a's R1, the triple's own
differences imply a faster approach than the actual distance to exact closes:
the level errors are −10.13 / −6.09 / −4.07 W/m² (ratios 1.66, 1.50), roughly
first order, while the GCI reads p = 1.48 from the differences and arms a band
smaller than the remaining error. That reading uses the exact reference, so it
is not an instrument independent of the hypothesis and grounds no repair; the
row is reported as the frozen comparator returned it. The sign-corrected
Richardson extrapolates (stored as `richardson_corrected`; the triple dict's
`richardson` field carries the sign defect T9a §8.1 already recorded in the
shared `gci()`, unedited, on no grading path) land at 6484.988 / −3267.594 /
−1253.959 / −1963.534 — within 0.001–0.063 % of exact on all four box rows.

**S0/S1.** Both sphere triples have successive differences that grow
(S0: +0.729 then +3.362 W/m²; S1: +0.953 then +2.261), the definition of
DIVERGENT, and no band is armed (D440: NOT A RESULT, never PASS). The finest
levels sit −1.60 % (inner) and +7.02 % (outer) from exact, and the comparator's
own radiosity solve on the written F reproduces the solver to ≤ 8.2e-15 on
every sphere case — the registered attribution lever: **Python-on-F == solver
!= exact means the view factors are wrong, not the assembly.** The
pre-registration measured this at build (§5.3): the outer-sphere raw row-sum
defect is 4.77 / 4.27 / 4.47 % at c/m/f — held-fixed quadrature settings, a
defect that does not shrink with the mesh — while the inner rows converge
(0.48 → 0.30 → 0.11 %) and the faceting deficit converges O(h²)
(−0.538 → −0.211 → −0.080 %). A ladder in which the geometric error terms
shrink while the dominant matrix defect stays fixed produces exactly this:
differences that grow as the shrinking terms stop masking the fixed one. The
registered §7 pattern anticipated a STAGNANT ladder for "quadrature floor
dominating"; the observed state is DIVERGENT, same cause, same handling — NOT
A RESULT, no band improvised.

## 2. Controls

Each MUST fail if the rung is sound; a control on a row that armed no band
cannot be evaluated and is labelled UNMEASURED (Charter §2c boundary clause 1,
via the §6 repair — the pre-repair code printed NOT MET for these, asserting
an evaluation that never ran).

| control | row | value | graded against | deviation | band | verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| C1 black-body | S0 | 3320.3408 | 6889.5464 | 51.81 % | none | **UNMEASURED** |
| C2 parallel-plate | S0 | 3320.3408 | 2175.6462 | 52.61 % | none | **UNMEASURED** |
| C2 parallel-plate | S1 | −902.8082 | −2175.6462 | 58.50 % | none | **UNMEASURED** |
| C1-live (S_C1, ε = 1 solved) | S0 | 6889.1835 | grey 3374.4717 | 104.16 % | none | **UNMEASURED** (see below) |
| C2 cube matrix | B0 | 6483.2630 | 6335.8516 | 2.33 % | 0.0333 % | **MET** |
| C2 cube matrix | B1 | −3269.6022 | −1930.3977 | 69.37 % | 0.0768 % | **MET** |
| C2 cube matrix | B2 | −1260.7933 | −740.8592 | 70.18 % | 0.6776 % | **MET** |
| C2 cube matrix | B3 | −1971.1779 | −1461.8677 | 34.84 % | 0.4847 % | **MET** |
| C2b opposite-only (reported) | B0 | 6483.2630 | 6889.5464 | 5.90 % | — | reported |
| C2b opposite-only (reported) | B1 | −3269.6022 | −6889.5464 | 52.54 % | — | reported |
| C2b opposite-only (reported) | B2, B3 | −1260.79, −1971.18 | **0.0** | **UNDEFINED (zero referent)** | — | reported |
| C3a radiation-off zero | S0, S1 | 0.0 | refs | 100.00 % | none | **UNMEASURED** ×2 |
| C3a radiation-off zero | B0–B3 | 0.0 | refs | 100.00 % | armed | **MET** ×4 |
| C3b uniform-300 K box solved (B_C3) | B0–B3 | −0.6961 / −2.2441 / −0.9870 / −0.9769 | refs | 99.92–100.01 % | armed | **MET** ×4 |

**22 control rows: 0 NOT MET, 12 MET, 6 UNMEASURED, 4 reported.** The
deviation convention is the comparator's |value − referent| / |referent|; the
pre-registration's §6 quoted the same departures in the referent-relative
convention (−2.30 / −40.89 / −40.95 / −25.59 % for the cube matrix), which is
why the printed figures differ while carrying the same information. The C2b
zero referent is registered physics, not a defect: an opposite-only network
for a box side wall exchanges with a wall at its own temperature, net flux
exactly zero, and the prereg's "−100 %" for those two entries was that zero
stated in the other convention.

**C1-live, the arm that matters.** `S_C1` (the finest sphere mesh solved with
ε₁ = ε₂ = 1) gives 6889.1835 W/m² on the inner patch — **0.005 % from the
black-body σ(T₁⁴ − T₂⁴) = 6889.546 W/m²** — and sits 107.48 % away from
`S_f`'s grey 3320.3408. The emissivity dictionary is demonstrably read (the
registered VOID/BLOCKED condition, S_C1 reproducing S_f, is nowhere near
firing), and the ε = 1 limit of the whole chain — matrix, assembly, BC — is
correct to 5e-05. What is UNMEASURED is only the registered band-arithmetic
test ("must FAIL against grey within S0's band"), because S0 armed no band.

**C3b is not zero to round-off, and the record keeps the number.** The solved
uniform-300 K box was registered as "every flux 0 by symmetry"; the solver
returns max |qr| = 13.95 W/m² against σT⁴ = 459.3 W/m² — 3.0 %, the raw
row-sum defect of the written F (1.9–3.0 % on those patches) passed straight
through, since a uniform enclosure's qr is (Σ_j F_ij − 1)·σT⁴ per face. The
control is MET regardless (each patch sits ~100 % from its registered
referent), and the figure independently confirms that the graded rows' errors
live in the view-factor matrix.

## 3. The twins: what smoothing and tighter quadrature move

Both twins share the finest meshes (points verified identical).

| row | finest (graded) | GaussQuadTol 0.001 twin | moves | smoothing-true twin | moves | twin vs exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S0 | 3320.340752 | 3320.339326 | 4.3e-05 % | 3397.663515 | +2.329 % | +0.687 % |
| S1 | −902.808211 | −902.809795 | 1.8e-04 % | −817.848317 | −9.411 % | 3.055 % |
| B0 | 6483.263010 | 6483.242984 | 3.1e-04 % | 6484.650960 | +0.021 % | 0.0042 % |
| B1 | −3269.602153 | −3269.622179 | 6.1e-04 % | −3252.299399 | −0.529 % | 0.405 % |
| B2 | −1260.793300 | −1260.868430 | 6.0e-03 % | −1255.102435 | −0.451 % | 0.033 % |
| B3 | −1971.177941 | −1971.258166 | 4.1e-03 % | −1965.265410 | −0.300 % | 0.029 % |

**GaussQuadTol.** Tightening the quadrature tolerance tenfold moves every row
by at most 0.006 % — orders below every armed band, so the registered
quadrature-floor gate fired nowhere. The row-sum defect is therefore not a
Gauss-tolerance artefact: it is the utility's ray/visibility discretisation,
which `GaussQuadTol` does not control.

**Smoothing.** Row renormalisation moves the sphere fluxes by 2.3 % and 9.4 %
and the box fluxes by 0.02–0.53 % — mostly toward the exact values (S0 lands
+0.69 % from exact instead of −1.60 %; B0 at 0.004 %), overshooting on B1
(0.405 % versus the graded 0.125 %). Graded with smoothing false by
registration (INTERPRETATION 3): these twins are reported, and they quantify
how much of the graded error the renormalisation hides. `S_f_s` is VOID under
the closure guard (§4) — expected, and confined to the twin.

## 4. Iterative convergence, the planted control, and the closure guard

All 13 cases CONVERGED: qr identical value for value between checkpoints 15
and 20 (max change 0.000e+00 on every case; L-141, no residualControl). The
live planted control recovered +1.234e-03 W/m² through the same reader on a
scratch copy of every case's earlier checkpoint, exactly (fl(old + plant) −
old: 0.0012339999998403073 / …2950546 / …0001794 depending on the base
value); the case trees were not touched.

| case group | closure raw | closure from-F | excess (tol 0.01) | reciprocity max defect | Python-vs-solver max rel |
| --- | ---: | ---: | ---: | ---: | ---: |
| S_c / S_m / S_f | 4.44e-02 / 4.37e-02 / 4.20e-02 | same to 1.3e-16 | ≤ 1.3e-16 | ≤ 3.1e-19 | ≤ 8.2e-15 |
| S_C1 | 5.66e-03 | same | 6.5e-17 | 6.5e-20 | 4.1e-15 |
| B_c / B_m / B_f | 3.40e-03 / 2.18e-03 / 1.41e-03 | same | ≤ 7.5e-16 | ≤ 2.2e-14 | ≤ 1.1e-14 |
| B_C3 | 1.00 (all fluxes ~0) | same | 0.0 | 2.2e-14 | 3.2e-13 |
| S_f_q / B_f_q | 4.20e-02 / 1.43e-03 | same | ≤ 7.6e-17 | ≤ 2.2e-14 | ≤ 1.1e-14 |
| S_f_s / B_f_s | 1.89e-02 / 9.25e-04 | 4.20e-02 / 1.41e-03 | **2.30e-02 → VOID** / 4.85e-04 | ≤ 2.2e-14 | 2.7e-02 / 2.0e-02 |
| H_2d | 8.56e-03 | same | 5.6e-17 | 2.8e-18 | 5.5e-16 |

The guard referent is |c_raw − c_F| (INTERPRETATION 6 as refined at build):
on every graded case the solver's heat balance equals the comparator's own
radiosity solve on the written F to machine precision — the assembly and
addressing are consistent with their own matrix, and the raw non-closure
(flagged where above 1e-2: the sphere cases, 4.2–4.4e-02) is the matrix's
row-sum defect itself, already measured by the ladder and twins. `S_f_s` is
VOID because the solver smooths F at run time while the guard's referent is
the raw written matrix — the twin measures exactly that renormalisation, and
the void withdraws nothing graded. B_C3's closure ratio of 1.00 divides
near-zero by near-zero (T9a §3's W_C3 pattern) and is printed, not explained
away. Hottel 2D row (reported only, never gated): 6517.19 / −4573.39 /
−1833.22 W/m², i.e. 0.10 / 1.37 / 2.15 % from the crossed-strings closed form
— the §3.1 amendment's build-time observation reproduced by the solve.

## 5. Provenance and the freeze

| event | time (Z) | evidence |
| --- | --- | --- |
| draft pre-registration | 2026-08-20 | `T10a_PREREGISTRATION_DRAFT.md` |
| first execution instance killed at session limit mid-write, leaving `exact_t10a.py`, `T10a_registered.json`, `analyse_t10a.py` | 2026-08-21 ~18:20 (prior day's session) | prereg §12.0 |
| second instance validates and completes; 13 cases built, meshed, view factors generated (9.4 core-min); `check_t10a_mesh.py` exit 0, three planted positives fired; selftest 24/24; frozen prereg written | 2026-08-21 | prereg §12.0–12.3 |
| **freeze commit `181a5668`** — prereg + 8 scripts, no time directory in any case | **19:18:08** | `git log`; commit message |
| serial chain start (S_c) | 21:27:08 | `log.chain_serial` |
| chain ends (H_2d), all 13 STATUS rc=0 | 22:58:15 | `log.chain_serial`, `STATUS.*` |
| `mark_done_t10a.py` strict rule 13/13, `DONE.*` written | 22:58:46 | marker mtimes |
| comparator first run: graded rows printed, **crash at line 887**; stdout preserved | 23:01:37 | `analyse_t10a.out` mtime |
| §6 repair; re-run completes, `gate_t10a.json` first written, graded rows byte-identical | 23:08:07 | `analyse_t10a.out.post_repair`, JSON mtime |

The 2d enforcement test: the freeze commit 19:18:08 Z precedes the first
solver start by **+2 h 09 m** and the earliest completion marker by
**+3 h 41 m**;
the comparator that produced every graded row hashes identical to the
committed blob. The two-instance authorship and the pre-freeze
answer-adjacent reads (S_c coarse fluxes, H_2d fluxes, row-sum defects — no
medium or fine flux) are disclosed exhaustively in the pre-registration
§12.0/§12.3 and referenced here rather than restated.

## 6. The Charter §2d.1 repair, quantified

**What broke.** The frozen comparator's `plant_against()` (line 887) divides
by the control referent. The `C2b_opposite_only` referent for the box side
walls is exactly 0.0 W/m² (registered physics, §2), so the first B2 control
row raised `ZeroDivisionError`: every graded row and 9 of 22 control rows had
printed; `gate_t10a.json` had not been written.

**The four §2d.1 conditions.** (1) *Demonstrable error*: the instrument
cannot run to completion at all — D419's boundary case ("repairing an
instrument so it can run is not tuning; the test is whether the repair can
change a number"). (2) *Established independently of the hypothesis*: by the
Python interpreter's uncaught exception and by reading the control-evaluation
code — both grade nothing and know no preferred direction. The same reading
established the second defect: for a must-fail control on a row with no armed
band, the code returned `met = False` and printed **NOT MET**, asserting an
evaluation that never ran; had the run not crashed first, the summary would
have declared "the rung is unsound" on the strength of four unevaluable
controls. An unevaluable control is **UNMEASURED**, not NOT MET (Charter §2c
boundary clause 1). (3) *Disclosed, what moved quantified*: below.
(4) *Pre-repair values beside published ones*: `analyse_t10a.out` is the
pre-repair record, preserved unmodified; the pre-repair file is kept as
`analyse_t10a.py.pre_repair_2026-08-21` (sha256 `674bac302193…4fe57ca`, equal
to the committed blob); the repaired file hashes `ad6a32861dda…434de65`.

**The edit, all of it.** Three hunks, all in `main()`'s control-report code,
which runs after every graded row is computed and printed: (i) `plant_against`
guards the zero referent — deviation stored as null, printed "UNDEFINED (zero
referent)" — and labels a must-fail control with no armed band UNMEASURED
instead of NOT MET; (ii) the `C1_live_S_C1` verdict gets the same UNMEASURED
label when no band is armed; (iii) the summary line counts UNMEASURED
separately. Controls with an armed band evaluate exactly as before (the 12
MET rows print byte-identically).

**What moved between the two stdouts, exhaustively (diff of
`analyse_t10a.out` against `analyse_t10a.out.post_repair`):** lines 1–194 —
every measurement, every graded row, every verdict, every printed digit —
**byte-identical**; lines 195–198, four control labels changed from "NOT MET"
to "UNMEASURED (cannot fire: no band armed; Charter 2c boundary 1)" with
every number on those lines unchanged; lines 204 onward, the ten-line
traceback replaced by the 27 lines the crash had swallowed (B2's C2b with
UNDEFINED deviation, B3's cube control MET, C3a ×6, C3b ×4, the Hottel
report, and the summary: 3 PASS / 1 GATE FAIL / 2 NOT A RESULT, 22 control
rows, 0 NOT MET, 6 UNMEASURED). Exit code 1 in both intent and fact (B1 GATE
FAIL); the relabel changed no graded verdict, no number, and no exit code —
it changed which sentence the summary prints about the controls, which is
precisely the sentence that was wrong. `--selftest` still passes 24/24.

## 7. What this rung cannot see

From the comparator's docstring and prereg §9, plus what this run adds:

- **No participating media, no spectral or non-grey behaviour, no coupling to
  convection or conduction** — every wall T imposed, the fluid inert; T10b
  and T9b/c own those.
- **No grey non-symmetric enclosure** — no exact answer exists; the grey path
  is graded on nothing (spheres NOT A RESULT), so after this rung the grey
  radiosity assembly is verified only in the ε = 1 limit (C1-live, 0.005 %)
  and against its own F (≤ 8.2e-15); **the grey graded claim is still open**.
- **No faceAgglomerate, no iterative radiosity solver, no parallel operation**
  (registered bypasses).
- **Whether the sphere ladder would converge under a quadrature that refines
  with the mesh** — the settings were registered fixed; a T10a-followup
  varying the generator's ray density with resolution is proposed, not run.
- **Whether B1's 0.125 % closes on a fourth level** — as with T9a R1, the
  triple is not yet asymptotic (error ratios 1.66, 1.50 vs p = 1.48) and only
  another level would show it.

## 8. Cost

Serial chain, nProcs 1, nice 10; walls from `STATUS.*` include contention
from concurrent rungs. 0.0513 USD per core-hour.

| case | cells | wall, s | | case | cells | wall, s |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| S_c | 2 400 | 1 | | B_c | 2 048 | 1 |
| S_m | 9 216 | 48 | | B_m | 8 788 | 13 |
| S_f | 40 560 | 863 | | B_f | 37 044 | 389 |
| S_C1 | 40 560 | 865 | | B_C3 | 37 044 | 368 |
| S_f_q | 40 560 | 858 | | B_f_q | 37 044 | 474 |
| S_f_s | 40 560 | 863 | | B_f_s | 37 044 | 495 |
| H_2d | 512 | 0 | | **total** | | **5 238** |

**Solve: 5 238 core-seconds = 87.3 core-minutes = 1.455 core-hours =
0.0746 USD**, against the registered prediction of ≤ 35 core-minutes solve /
≤ 45 grand total: **2.5× the solve prediction, 1.9× the grand total** — the
n³ LU extrapolation from S_c underestimated the fine dense factorisations —
inside the registered 10× stop-and-investigate threshold. Adding the
9.4 core-minutes of viewFactorsGen preprocessing already spent at build
(0.157 core-hours, 0.0080 USD): **grand total 96.7 core-minutes =
1.61 core-hours ≈ 0.083 USD.** Comparator runs: zero solver compute.

## 9. Rung verdict

**GATE FAIL — box enclosure 3 of 4 graded rows PASS: B0 6483.263010 vs
6484.920941 (0.02557 % inside 0.03326 %, p 0.954) PASS; B1 −3269.602153 vs
−3265.532221 (0.12463 % against 0.07676 %, p 1.480) GATE FAIL; B2
−1260.793300 vs −1254.691645 (0.48631 % inside 0.67756 %, p 0.853) PASS; B3
−1971.177941 vs −1964.697075 (0.32987 % inside 0.48472 %, p 0.825) PASS.
Spheres NOT A RESULT ×2 on DIVERGENT triples (orders −3.25 / −1.84), the
build-time-measured non-converging 4.3–4.8 % outer-sphere row-sum defect
dominating a ladder whose geometric errors shrink; no band improvised.
Controls: 12 MET, 0 NOT MET, 6 UNMEASURED (no band armed; Charter §2c
boundary 1); C1-live lands 0.005 % from black-body with ε = 1 and 107 % from
the grey run, so the emissivity path is read. Every case CONVERGED with 0.0
change between checkpoints; planted 1.234e-03 recovered exactly ×13; closure
excess ≤ 7.5e-16 on every graded case; Python-on-F matches the solver to
≤ 1.1e-14, placing the graded error in the view-factor matrix. GaussQuadTol
10× tighter moves no row by more than 0.006 %; smoothing moves rows 0.02–9.4 %
and is reported, not graded. Comparator byte-identical to 181a5668 for every
graded number; one §2d.1 repair after first compute (zero-referent guard +
UNMEASURED label, line 887), graded rows verified byte-identical across the
repair, both stdouts preserved. 87.3 core-minutes solve + 9.4 build =
0.083 USD, 1.9× the ≤ 45 core-minute prediction.**
