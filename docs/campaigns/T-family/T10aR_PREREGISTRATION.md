# T10a-R. The refinement arm on T10a's B1 ceiling GATE FAIL

**FROZEN 2026-08-22 18:08 Z, before any case directory existed.** Directive
Sanaa **H-3(a)**: *"T10a follow-through: the ceiling miss gets a refinement
arm (discretization finding, cheap)."* Run tree
`verification/runs/T-family/T10aR_runs/`. Verdict vocabulary fixed by the
Verification Charter §2: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.**

**Scope: the BOX only.** No spheres. T10a's S0/S1 `NOT A RESULT` rows come
from the `viewFactor` row-sum defect that does not shrink with the mesh; that
is directive **H-3(b)** and is not this arm's topic. Nothing in this file
touches, re-runs, re-grades or amends T10a. **T10a is closed.**

---

## 0. What this arm grades, and — first — what it does not

**This arm grades NOTHING against T10a's band.** T10a's rung verdict (GATE
FAIL; B0/B2/B3 PASS, B1 GATE FAIL, S0/S1 NOT A RESULT) was published
2026-08-21 and stands unchanged whatever this arm returns. Every verdict below
is **PASS or GATE FAIL against a prediction registered in this file**, with a
numeric interval and a named falsifier, before any solve. A row whose grid
triple is not `CONVERGING` is **NOT A RESULT** and receives no verdict at all
(D440, carried forward from T10a §5.2).

**What T10a left open, in its own words** (`T10a_RESULTS.md` §7): *"Whether
B1's 0.125 % closes on a fourth level — as with T9a R1, the triple is not yet
asymptotic (error ratios 1.66, 1.50 vs p = 1.48) and only another level would
show it."* That sentence is this arm's whole subject.

**The pattern being probed, stated exactly.** On T10a's B1 and on T9a's R1 the
same thing happened: the grid triple's own successive differences implied a
convergence order (`p` = 1.480 and 1.738) faster than the rate at which the
finest level's actual distance from exact was closing (level-error ratios
1.66/1.50 and 1.63/1.38, i.e. roughly first order). The Roache GCI reads the
differences, believes the implied order, and arms a band **smaller than the
error it is supposed to cover** — 0.077 % against a 0.125 % miss on T10a B1
(1.62 bands outside), 0.92 mK against a 2.41 mK miss on T9a R1 (2.63 bands
outside). This arm asks whether a fourth level continues that, and whether the
miss is a discretisation of the enclosure or an artefact of the view-factor
quadrature or of solver tolerance.

---

## 1. The three arms, one registered change each

Every arm's case is produced by `build_t10aR.py`, which **imports the frozen
`build_t10a.py` and calls its own dictionary writers**; it copies no
dictionary text. The builder then **refuses** (`verify()`) unless every file
it did not register as changed is byte-identical (sha256) to the frozen
`T10a_runs/B_f`, and every file it did register as changed is not.

| arm | case | the ONE change from `B_f` | everything else |
| --- | --- | --- | --- |
| **R-x** | `R_x` | `blockMeshDict` N 42 → **68** per m (18 496 radiating faces, 157 216 cells) | byte-identical to `B_f` |
| **R-q** | `R_q` | `viewFactorsDict` **`distTol` 8 → 80** | byte-identical to `B_f` |
| **R-s** | `R_s` | solver tolerance / iteration **bundle** (§1.3) | `fvSchemes` byte-identical to `B_f` |

Geometry, temperatures, emissivities (all six patches black, ε = 1),
`radiationProperties` (`smoothing false; constantEmissivity true;
useDirectSolver true; nBands 1; solverFreq 1`), `boundaryRadiationProperties`,
`thermophysicalProperties`, `g = (0 0 0)`, and every `0.orig` field are the
frozen T10a box, unchanged, in all three.

### 1.1 R-x — the fourth level

Levels and ratios, in radiating-face edge count per metre:

| level | N/m | radiating faces | cells | ratio to previous |
| --- | ---: | ---: | ---: | ---: |
| c (`B_c`, frozen) | 16 | 1 024 | 2 048 | — |
| m (`B_m`, frozen) | 26 | 2 704 | 8 788 | 1.6250 |
| f (`B_f`, frozen) | 42 | 7 056 | 37 044 | 1.6154 |
| **x (`R_x`, this arm)** | **68** | **18 496** | **157 216** | **1.6190** |

N must be even (`build_t10a.box_block_mesh` asserts `nz*2 == N` for the 0.5 m
height), so 42 × 1.6 = 67.2 rounds to **68**, giving 1.6190 — inside the
family the frozen ladder already spans (1.6250, 1.6154). The graded triple is
**m / f / x**; c is reported for the four-level picture but is not in the
triple. As in T10a the GCI uses the **nominal** r = 1.6 imported from
`analyse_t1c` (the comparator refuses if `Fs`/`r` differ from that module's);
the built ratios are stated here and printed by the comparator rather than
silently reconciled.

### 1.2 R-q — the quadrature knob that was NOT yet varied, and a correction

**The directive proposed `nRayPerFace` or turning agglomeration off. Neither
exists on the registered path**, and that is recorded here before any solve:

* `viewFactorsGen.C` (v2606, lines 469–486) reads **exactly seven** dictionary
  entries: `writeViewFactorMatrix`, `dumpRays`, `debug`, `GaussQuadTol`,
  `distTol`, `alpha`, `intTol`. **`nRayPerFace` is `createViewFactors`'**
  entry — the utility T10a used only for the 2D, reported-only `H_2d` row.
* **Agglomeration is already off.** T10a INTERPRETATION 4 runs no
  `faceAgglomerate`; `finalAgglom` is absent, the identity agglomeration is
  used, one radiating face per mesh face. There is nothing to turn off.

**`distTol` is the knob not yet varied, and it is the sharpest one this
utility has.** From `viewFactorsGen.C` lines 967–1002, for each pair of faces:

```
dist = |C_i - C_j| / ((sqrt(A_i/pi) + sqrt(A_j/pi))/2)
dist >  distTol  ->  2AI: double AREA integral, ONE midpoint sample per pair
dist <= distTol  ->  2LI: double LINE integral over the four edge pairs,
                     Gauss quadrature refined until the relative change is
                     below GaussQuadTol
```

At N = 42 a face's equivalent-circle radius is 0.01343 m, so `distTol` 8 puts
the switch at **0.107 m**: in a 1 × 1 × 0.5 m box nearly every visible pair is
"far" and gets the **midpoint** formula. `distTol` **80** moves the switch to
**1.074 m**, past all but the longest of the box's ≤ 1.5 m diagonals, so
nearly every pair is integrated by **2LI** instead. The factor of ten matches
the `GaussQuadTol` twin T10a already ran, for comparability.

**A registered reservation, stated before the run so that it cannot be
retro-fitted.** The directive's registered prediction for this arm is that B1
moves by **< 0.01 %** (falsifier > 0.05 %), on the reasoning that the ceiling
miss is not a quadrature artefact and that T10a's `GaussQuadTol` twin moved
every row by ≤ 0.006 %. **The analyst's own reading of the source disagrees
with the reasoning while accepting the prediction:** `distTol` does not refine
a tolerance, it switches integration *method* for the majority of the matrix —
so a move larger than 0.05 % is entirely plausible, and would be a real
finding (the ceiling miss WOULD then be a view-factor quadrature artefact).
The prediction is registered **as the directive gives it**, with this
reservation recorded beside it, so that a > 0.05 % move is scored as a
**falsification of the registered prediction**, not as something anyone
"expected all along".

### 1.3 R-s — solver tolerance, and the knob the directive named that does not exist

**The radiosity system is not solved iteratively at all on the registered
path.** With `constantEmissivity true; useDirectSolver true;`,
`viewFactor.C:1008` calls `LUsolve` on a dense LU cached at the first
radiation iteration. **There is no radiosity tolerance and no radiosity
iteration count to tighten**: the directive's *"solver tolerance for the
radiosity G to 1e-10 and more radiation iterations"* has no dictionary entry
to land in. Reaching one would require `useDirectSolver false`, which is a
**second** change and a model path T10a explicitly did not grade (its §9,
*"Nothing about the iterative (non-direct) radiosity solver"*).

R-s therefore tightens **every tolerance and iteration count that does exist**
on the registered path, as one registered **bundle**, exhaustively:

| file | entry | `B_f` | `R_s` |
| --- | --- | ---: | ---: |
| `system/fvSolution` | `p_rgh` tolerance | 1e-08 | **1e-12** |
| | `p_rgh` relTol | 0.01 | **0** |
| | `(U\|h)` tolerance | 1e-08 | **1e-12** |
| | `(U\|h)` relTol | 0.1 | **0** |
| | `nNonOrthogonalCorrectors` | 1 | **3** |
| `system/controlDict` | `endTime` | 20 | **60** |
| | `writeInterval` | 5 | **15** (strictly < endTime, 4 checkpoints, L-140) |

`system/fvSchemes` is **byte-identical** to `B_f` — the `laplacian`/`div`
schemes for the convective-conductive part are untouched, as the directive
requires. **That this is a bundle is registered, not discovered:** if it moves
nothing, the whole category (solver tolerance, iteration count, non-orthogonal
correction, run length) is ruled out at once, which is the point; if it moves
something, a follow-up would have to bisect it, and no such bisection is
claimed here.

---

## 2. Registered rows — prediction, identity test, falsifier, threshold

Thresholds are machine-readable in `T10aR_runs/T10aR_registered.json` and are
applied by `analyse_t10aR.py` with no human step. `dev` means
`100·|value − exact|/|exact|`, exact = the σ_OF reference T10a registered
(B1 ceiling **−3265.532221 W/m²**); `move` means `100·|R − B_f|/|B_f|`.

| row | arm | quantity | registered prediction | interval (PASS) | identity test (Charter §2a) | falsifier |
| --- | --- | --- | ---: | --- | --- | --- |
| **RX1** | R-x | B1 `dev` at level x, % | **0.083** | `[0.070, 0.100]` | **not an identity** — a discretisation ladder; this toolchain has no exact-at-every-resolution property here (T10a §3.1 withdrew the one identity claim it had made) | dev ≥ 0.1100 % (error not shrinking as registered) or ≤ 0.060 % (falling faster than the registered first-order-like family) |
| **RX2** | R-x | observed `p` of the m/f/x triple | **1.15** | `[0.80, 1.55]` | not an identity | `p` > 2.00; or the triple is not CONVERGING → **NOT A RESULT**, no verdict |
| **RX3** | R-x | **dev ÷ band** at level x | **2.0** | `> 1.0` | not an identity | **dev/band ≤ 1.0** — the band covers the error and the T10a/T9a band-smaller-than-error pattern does **not** persist |
| **RX4** | R-x | level-error ratio \|e_f\| / \|e_x\| | **1.50** | `[1.30, 1.70]` | not an identity | outside `[1.30, 1.70]` |
| **RX5** | R-x | sign-corrected Richardson (m/f/x), % from exact | **0.02** | `[0, 0.100]` | not an identity | > 0.100 % (worse than the 0.063 % T10a's c/m/f corrected Richardson already reached) |
| **RQ1** | R-q | B1 `move` from `B_f`, % | **0.000** | `[0, 0.010]` | not an identity — a method switch changes the matrix | **> 0.050 %** (the ceiling miss IS a view-factor quadrature/method artefact) |
| **RQ2** | R-q | worst of B0/B2/B3 `move`, % | **0.000** | `[0, 0.010]` | not an identity | any of the three > 0.050 % |
| **RS1** | R-s | B1 `move` from `B_f`, % | **0.000** | `[0, 0.005]` | see RS2 | > 0.005 % |
| **RS2** | R-s | **max \|qr(R_s) − qr(B_f)\| over all 7 056 radiating faces, W/m²** | **0.0 exactly** | `[0, 0]` | **THIS IS AN IDENTITY (§2a).** With every wall `fixedValue T`, `constantEmissivity true` and `useDirectSolver true`, `qr` is fixed by T, ε and F at the first radiation solve and a direct LU has no tolerance: `R_s` must be **bit-identical** to `B_f` face by face, at this resolution and at every other. **Precondition:** `sha256(R_s/constant/F) == sha256(B_f/constant/F)` — R_s regenerates its own matrix, and if `viewFactorsGen` is not deterministic the identity has no referent and the row is **NOT A RESULT**, with the non-determinism itself reported | any nonzero difference, given the precondition holds |

### 2.1 The arithmetic tension inside RX1+RX2+RX3, registered before it is resolved

The directive's prediction has two halves — *"p stays ≈ 1.5 first-order-like"*
and *"B1 deviation falls to ~0.08 %"* — and **the arithmetic says they cannot
both hold exactly.** From the frozen numbers (`f_m` = −3271.620,
`f_f` = −3269.602153, exact −3265.532221, `e_f` = −4.070 W/m²):

* **If the level-error ratio stays 1.5** (errors −6.09 → −4.07 → −2.71), then
  `f_x` = −3268.245, dev = **0.0830 %**, the differences become
  −2.017 then −1.357 (ratio 1.486), so **p = 0.840** — and the band opens to
  **0.107 %**, which **covers** the 0.083 % error: **dev/band = 0.77, RX3
  FALSIFIED.**
* **If the difference ratio stays 2.005 (p = 1.480)**, then `f_x` = −3268.596,
  dev = **0.0938 %**, band **0.0383 %**, **dev/band = 2.45, RX3 confirmed** —
  and the level-error ratio drops to 1.33, **RX4 falsified low**.

Both branches sit inside RX1's `[0.070, 0.100]` interval, which is why RX1 is
registered wide and RX2/RX3/RX4 are registered separately: **RX3 is this arm's
headline claim and RX2/RX4 are the two ways it can be reached.** The measured
outcome discriminates them, and either outcome is reportable. Registering the
tension in advance is the point; whichever branch appears, the report will not
be able to claim it was the only one foreseen.

### 2.2 Planted-zero control

The registered plant is **+1.234e-03 W/m²** (T10a's value, unchanged). For
**every** case in this arm the frozen `planted_zero_control` plants it by line
index into a **scratch copy** of the earlier checkpoint, reads it back through
the same reader, and requires the recovered maximum change to equal
**exactly** `fl(old + plant) − old` — not the plant, and not within a
tolerance (T10a §5.5; the selftest shows why: at a ~6.5e3 W/m² base the
recovered float is 0.001234000000295054633, and a 1e-12 relative tolerance is
unsatisfiable against the ulp). **No case tree is written to.** A failed plant
is a comparator **refusal**, not a graded row.

### 2.3 Convergence, guards, and what refuses

* **Convergence (§5.5 rule, carried forward):** a case is CONVERGED only if
  `qr` is identical value for value between the last two written checkpoints.
  No `residualControl` in any case (L-141). The comparator **refuses** on an
  unconverged level — no triple is formed from one (D440).
* **Completion:** `mark_done_t10aR.py` applies the frozen strict rule
  unchanged (rc=0, `End` line, last time == endTime, `T` and `qr` present,
  `ExecutionTime` count == endTime, every field newer than the case's own
  `0/T`). All three cases are required; there is no optional case.
* **Stale-write guards G1/G2/G3** (atomic launch lock, `/proc` cwd scan, no
  stray numeric time directory) are carried over verbatim from
  `launch_t10a.sh` / `run_one_t10a.sh`, plus the refusal to run a case with no
  `constant/F`.
* **Closure guard:** the T10a referent `|c_raw − c_F| > 1e-2` is applied to
  every case with the frozen threshold read from `T10a_registered.json`. A
  VOID case withdraws its rows (they become NOT A RESULT), it does not have
  them graded anyway.
* **Mesh read-back:** box extents to 1e-12 and every patch area to 1e-10,
  through the frozen `measure()`, refusal on mismatch.
* **Provenance:** the comparator prints the sha256 of every frozen instrument
  it imported at every run.

---

## 3. Instruments — what is frozen, what is new

**Frozen, imported, never edited.** `analyse_t10aR.py` imports
`T10a_runs/analyse_t10a.py` and uses its `measure`, `row_value`,
`mesh_patches`, `time_dirs`, `read_qr_all`, `patch_values`,
`read_emissivities`, `sigma_used`, `iterative_convergence`,
`planted_zero_control`, `read_F`, `dense_F`, `radiosity_on_F`, and through it
`T1_runs/analyse_t1c.gci` (Fs 1.25, nominal r 1.6). The frozen module's `HERE`
and `REG["cases"]` are redirected **in this process only**, by a context
manager (`in_tree`) that restores both on exit — proved by the selftest — so
that `measure()` reads the T10a-R tree for `R_*` and the frozen T10a tree for
`B_m`/`B_f`. **The frozen files on disk are never written to**; their sha256s
are printed at every comparator run.

**NEW INSTRUMENT 1 — the sign-corrected Richardson extrapolate.** Declared new
because it is new:

```
richardson_corrected(f_c, f_m, f_f) = f_f + (f_f - f_m) / (r**p - 1)      [Roache]
```

The shared `analyse_t1c.gci` returns `f_f + (f_m − f_f)/(r**p − 1)` — the sign
defect **T9a §8.1 recorded and deliberately left unedited** because it sits on
no grading path. This arm reports **both, side by side**, and **grades on
neither**: no verdict in this file is a function of a Richardson value. RX5 is
registered as a *prediction about a reported diagnostic*, and the diagnostic
uses the exact reference, so — exactly as T10a §1.1 said of the same reading —
**it is not an instrument independent of the hypothesis and grounds no
repair.** The selftest proves the corrected form recovers the exact value of a
clean synthetic power law to 1e-8 while the shared form does not, and that it
reproduces T10a's own published −3267.594 from T10a's published triple.

**NEW INSTRUMENT 2 — `read_F_dense_stream` + `radiosity_lean`.** A
line-streaming replacement for `read_F`/`dense_F`/`radiosity_on_F` whose peak
memory is one dense n × n float64 array. **It exists for a measured reason:**
`R_x`'s `constant/F` is projected at ~6.1 GB of ascii (from `B_f`'s measured
885 342 436 B at 7 056² = 17.78 B/entry, times 18 496²/7 056²), and the frozen
`read_F` materialises the whole file as a Python `str` and then makes three
more full-length copies (`re.sub`, and two `.replace`) — **> 24 GB of
transient strings on a box with 25 GB available.**

**Registered validation, enforced at every run, refusal on failure:** on
`B_m`, `B_f`, `R_q` and `R_s` — every case where both paths fit — the lean
path must reproduce the frozen path's dense matrix **bit-identically**
(`np.array_equal`) and its radiosity and reciprocity numbers to **≤ 1e-12
relative**, or the comparator exits 2. `radiosity_lean` is registered for
ε = 1 **only** (the whole box), where `viewFactor.C`'s C matrix is the
identity and the frozen assembly reduces algebraically to
`F₀ @ σT⁴ − σT⁴`; it **refuses** any other emissivity, and the selftest
exercises that refusal rather than asserting it.

**`--selftest`: 28/28 at freeze** (2026-08-22, run before any case existed),
covering the corrected and defective Richardson forms, reproduction of T10a's
published p/band/Richardson, that every verdict path (PASS, GATE FAIL both
high and low, NOT A RESULT) is reachable, that RX3 at exactly 1.0 is a GATE
FAIL, the streaming reader against a hand-written matrix, the blocked
reciprocity against the dense one, `radiosity_lean` against the frozen
`radiosity_on_F`, the exact-float plant rule, and that `in_tree` restores the
frozen module.

---

## 4. Cost — measured basis, honest extrapolation, stop threshold

**$0.0513 per core-hour** (T1b's measured figure). Serial, `nice 15`, one case
at a time: the 16-core box is carrying 4 T1b L4 solvers, 8 T3 ext1 solvers and
a T9a-D lane at ~3 cores at the time of writing (load average 30), so **this
lane takes one core and queues everything else.**

**Measured basis** (`T10a_RESULTS.md` §8 and the frozen `BUILD.txt` files):

| case | faces n | `viewFactorsGen` wall | solve wall |
| --- | ---: | ---: | ---: |
| `B_c` | 1 024 | 1.5 s | 1 s |
| `B_m` | 2 704 | 7.8 s | 13 s |
| `B_f` | 7 056 | 49.7 s | 389 s |

Generation scales as ~n^1.93 measured (log-ratio B_m→B_f); the solve is
dominated by the one-off dense LU of the n × n C matrix, **n³**.

**Pre-freeze timing probe, disclosed.** To size R-q, three throwaway box cases
were built in the session scratch directory (**not** in any run tree, no
`R_*` path, never solved) and `viewFactorsGen` was timed on them:
N = 16 `distTol` 8 → 4.63 s; N = 16 `distTol` 80 → 6.89 s; N = 26 `distTol` 80
→ 35.59 s. Against the frozen `B_c`/`B_m` figures the box is running ~3.1×
contended today, so **`distTol` 80 costs ~1.49× the generation time, roughly
mesh-independent.** **What was read: wall time, peak RSS, and the byte size of
`constant/F`. No flux, no `qr`, no view-factor value, and no solver was run.**
The two coarse `F` files differ in size (18 379 599 vs 18 383 786 B), which
establishes the knob is live; **no numeric comparison of any `F` entry was
made.**

**Predicted cost:**

| case | blockMesh + checkMesh | `viewFactorsGen` | solve | total core-s | USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `R_x` | ~5 s | 49.7 × (18496/7056)^1.93 ≈ 320 s, **400 s** with margin | 389 × (18496/7056)³ = 389 × 18.03 = **7 013 s** | **7 420** | **0.106** |
| `R_q` | ~5 s | 49.7 × 1.49 ≈ **75 s** | ≈ `B_f`'s **389 s** (same n, same LU) | **470** | **0.0067** |
| `R_s` | ~5 s | **50 s** (dict identical to `B_f`) | LU ≈ 334 s + 3× the fluid part (≈ 165 s) + tighter tolerances ≈ **700 s** | **750** | **0.011** |
| | | | **grand total** | **8 640 core-s = 2.40 core-h** | **$0.123** |

**The 10× stop-and-investigate threshold is 24.0 core-hours (≈ $1.23).** A
case that passes it is stopped and investigated, not waited out.

**The cap rule, and why it did not fire.** The directive caps R-x at ~3 USD
and names ratio 1.26 (N = 54) as the fallback. At **$0.106** predicted, the
cap is 28× away and the **full ratio 1.6190 stands**. Recorded so that the cap
is on the record as evaluated, not ignored.

**Feasibility of R-x, measured rather than assumed** (the directive's BLOCKED
clause):

* **Disk:** `F` ≈ 6.08 GB + `globalFaceFaces` ≈ 1.35 GB + mesh ≈ 7.5 GB for
  the case. **319 GB free.** Fine.
* **Solver memory:** `viewFactor.C` holds `Fmatrix_` and `CLU_`, two dense
  n × n doubles = 2 × 2.74 GB ≈ **5.5 GB** plus the ascii read buffers.
  **25 GB available.** Fine. (T10a measured ≈ 1.1 GB at n = 8 112 — two
  copies — which is the basis for this scaling.)
* **Comparator memory:** the lean instrument holds one 2.74 GB matrix plus
  148 MB blocks ≈ **3.2 GB**. The frozen `read_F` would need > 24 GB, which is
  why the lean instrument exists.
* **If any of these turns out infeasible in fact, R-x is recorded BLOCKED with
  the measured numbers and R-q/R-s are run alone** — as the directive
  requires.

---

## 5. Freeze set and hashes

Frozen 2026-08-22 18:08 Z. `find verification/runs/T-family/T10aR_runs -name
'R_*'` returned **nothing** at freeze (timestamped in
`T10aR_runs/FREEZE_CHECK.txt`), i.e. **no case directory of any kind existed,
let alone a time directory.**

| file | sha256 |
| --- | --- |
| `T10aR_runs/T10aR_registered.json` | `23c31bbee337a3eeb42dae0b2d27743022a0735cb0c466f9eeeea607b4eabcbd` |
| `T10aR_runs/build_t10aR.py` | `6f254b9504c01e92fa1529279411fd5f47fa38f0e64a9c98fdc4e87535acc706` |
| **`T10aR_runs/analyse_t10aR.py`** (the comparator) | **`a3014a64f1a2e5ce507f029c45b7c1f54eaf108348cf37a63be1ca604649c5ef`** |
| `T10aR_runs/mark_done_t10aR.py` | `07525c22ac086761a7a53c8f485f66dbcf5dc758107a19a88507f5657a81aab9` |
| `T10aR_runs/preprocess_t10aR.sh` | `44bbf14ae4d8ae78c16af1e293592e77e652d7fa6a887aa4a4b6ca45889aaf51` |
| `T10aR_runs/run_one_t10aR.sh` | `1dd4fc36c4c7dec8ccf0362aeb165c8dcfe70eaf891470c86c7b1e220283fc4e` |
| `T10aR_runs/launch_t10aR.sh` | `dd3f0e32f742f0368da17697bc8d60604b92f5d3a51aad388e10fc13e2a9997e` |

### 5.1 One builder repair, before any solver ran — disclosed

`build_t10aR.py` **refused at its first run and wrote no `R_s`**: its guard
required each `fvSolution` substitution to match exactly once, and the frozen
`fv_solution()` emits `tolerance 1e-08;` **twice** — once in the `p_rgh` block
and once in the `"(U|h)"` block. **Both are registered as tightened in §1.3.**
Charter §2d.1 boundary case (D419): repairing an instrument so that it can run
at all is not tuning; the test is whether the repair can change a number.

**The edit, all of it:** the substitution table now carries an expected count
per entry (**2** for the tolerance line, 1 for the other three) instead of a
hard 1, and a new post-condition refuses if any untightened tolerance survives
the bundle. Nothing else changed.

**It can change no number, and did not.** `R_x` and `R_q` had been written
identically before the refusal fired; **both were deleted before the repair
and rebuilt after it**, so nothing pre-repair survives on disk. **No solver had
run and no case held a time directory at any point** (re-verified and
timestamped in `FREEZE_CHECK.txt`: 0 time directories after the build).
`build_t10aR.verify()` independently re-checks by sha256, against the frozen
`B_f`, that every file not registered as changed is byte-identical and every
file registered as changed is not — and it passed for all three cases. **The
builder produces no graded number**; every number in this arm comes from
`analyse_t10aR.py`, whose sha256 is unchanged
(`a3014a64f1a2…4649c5ef`).

| file | sha256 |
| --- | --- |
| `build_t10aR.py` (repaired, the one that built the cases) | `2bc6f3c22bad4143bcdec40a0a47b193b6caf93aa76ec2a77b7985fbf74c1e73` |
| `build_t10aR.py.pre_repair_2026-08-22` (kept beside it) | `6f254b9504c01e92fa1529279411fd5f47fa38f0e64a9c98fdc4e87535acc706` |

The §5 table's `build_t10aR.py` row is the **pre-repair** hash, left as frozen;
this is the repaired one.

**Verified one-change-per-case after the build** (`diff` against the frozen
`B_f`, full output in the results file): `R_x` — `blockMeshDict` `(42 42 21)`
→ `(68 68 34)`, one line. `R_q` — `viewFactorsDict` `distTol 8;` → `80;`, one
line. `R_s` — `fvSolution` five lines, `controlDict` two lines, exactly §1.3's
table. Every other file byte-identical.

**Imported frozen instruments, hashed at freeze and re-hashed by the
comparator at every run:**

| file | sha256 |
| --- | --- |
| `T10a_runs/analyse_t10a.py` | `ad6a32861dda217259b16231e7f044e12d9dc4be96de130046cceba0b434de65` |
| `T10a_runs/build_t10a.py` | `534947076a533dc53c2ce29db5f202956ea241bff02ddb0291c1c002e188652a` |
| `T10a_runs/exact_t10a.py` | `8efb4d61d445b765c98076378f3decbea5553815b4594e36fe9e09603fe689c6` |
| `T10a_runs/T10a_registered.json` | `bdfbd8120ff2e7badbb8cfc8e51f4e2121c203fa8221665bd8d992e8befb2dd1` |
| `T1_runs/analyse_t1c.py` | `60893b28e284127f61b41842c520897a2202cb024d5a4d260272c6ee7e6c5135` |

The `analyse_t10a.py` hash is the **post-repair** file T10a published (its §6),
which is the file that produced every T10a graded row byte-identically to the
pre-repair one.

---

## 6. What this arm will not be able to see, whatever it returns

Written before the numbers exist, so it cannot be trimmed to fit them.

* **Nothing about the spheres.** S0/S1 stay NOT A RESULT. This arm runs no
  sphere case and says nothing about the non-converging outer-sphere row-sum
  defect. That is H-3(b).
* **Nothing about T10a's verdict.** T10a is closed at GATE FAIL. A PASS here
  is a prediction met, not a rung repaired; a GATE FAIL here does not make
  T10a worse.
* **No participating media, no spectral behaviour, no convection or conjugate
  coupling, no grey non-symmetric enclosure, no `faceAgglomerate`, no
  iterative radiosity solver, no parallel operation** — every T10a §9 bypass
  is inherited unchanged.
* **No asymptotic claim.** A four-level ladder that behaves is still not a
  demonstrated asymptotic range; the observed `p` is quoted beside every band
  and no band is a proof of order.
* **R-s cannot separate its own bundle.** It tightens seven entries at once by
  registration (§1.3). A null result rules out the category; a non-null result
  identifies no single entry.
* **R-q changes the matrix, so it is not a "same answer, better arithmetic"
  test.** If it moves a row, that tells us the row depends on the integration
  method; it does not by itself say which method is right, because the exact
  view factors are known but the *discrete* enclosure's are not.
* **Nothing about production meshes.** N = 68 per metre on a 1 m box is
  1.5 cm cells; no room-scale case will carry this.

---

## ADDENDUM, dated 2026-08-22 18:26 Z — the freeze is by hash, not by commit

**This addendum alters no gate, threshold, cap or label.** It records how the
freeze was established, because the honest answer is weaker than the standing
rule asks for.

**What happened, in order.**

| event | time (Z) | evidence |
| --- | --- | --- |
| pre-registration, registered JSON, builder, comparator, scripts written; `--selftest` 28/28 | 18:07–18:10 | this file; `FREEZE_CHECK.txt` |
| **freeze by on-disk sha256**; `find …/T10aR_runs -name 'R_*'` returns **zero** matches | **18:10:36** | `FREEZE_CHECK.txt`, timestamped, hashes in §5 |
| builder repair (§5.1), cases deleted and rebuilt; **0 time directories** | 18:11–18:12 | `FREEZE_CHECK.txt` |
| **first compute of any kind**: `viewFactorsGen` for `R_q` completes (mesh-side preprocessing, Charter §2d — the same class of step T10a ran *before* its own freeze commit) | **18:15:35** | `R_q/BUILD.txt` |
| **first solver launch**: `R_q` | **≈18:20** | `R_q/LAUNCH_LOCK/launch.log` |
| T-family supervisor course-correction: standing rule 2 requires the pre-registration to be **committed**, not merely hashed, before compute; a private-index commit recipe supplied (scratchpad `GIT_INDEX_FILE`, **not** the shared index) | ≈18:21 | supervisor message |
| **commit attempted, DENIED by this session's permission classifier**; not retried, no workaround attempted | **18:25** | `FREEZE_CHECK.txt` |

**The interval: the freeze precedes first preprocessing by ~5 minutes and the
first solver launch by ~10 minutes — by hash, not by commit.** This lane's own
brief said "no git commit, no shared-index use"; the supervisor's correction
superseded that and the correction could not be carried out.

**What this costs, stated rather than glossed.** A sha256 written by the same
process that wrote the file is weaker evidence than a commit object: it proves
the file is unchanged since 18:10:36 Z only to a reader who trusts this
record's own timestamps. A commit would have made the freeze independently
checkable by anyone with the repository. **It is not available, and no claim in
`T10aR_RESULTS.md` rests on anything stronger than the hashes in §5 and
`FREEZE_CHECK.txt`.** Disclosure shape follows `T3_EXT1_AMENDMENT.md` §14. The
supervisor's instruction not to stop already-launched runs was followed: they
were not stopped.

**What is unaffected.** The comparator (`a3014a64f1a2…4649c5ef`) was written
and hashed before any case directory existed and has not been touched since;
it re-hashes every frozen instrument it imports at every run and prints them.
Every prediction interval and falsifier in §2 is unchanged from 18:10:36 Z.
