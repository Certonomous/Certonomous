> **FINAL — graded 2026-08-23.** `R_x` completed 2026-08-22 23:45:53 Z
> (STATUS rc=0, wall 17 032 s); `mark_done_t10aR.py` returned **3/3 cases
> meeting the strict completion rule** and the authoritative frozen comparator
> `analyse_t10aR.py` (verified byte-identical to the `7150182b` blob at run
> time) was executed 2026-08-23 ~19:12–19:35 Z, rc = 0, planted-zero control
> recovered on every case, lean-vs-frozen F validation bit-identical on every
> case where both fit. `gate_t10aR.json` written by the comparator.
> **The comparator confirmed every interim R-q and R-s figure in this file to
> every printed digit.** Two corrections against the 2026-08-22 19:37 Z draft,
> disclosed per this banner's own promise rather than silently replaced:
> (1) §1a stated the committed pre-registration blob's length as "first
> 33 445 bytes"; the committed blob `c81223d8…` is **30 520 bytes**, and the
> prefix property holds at that length (re-measured 2026-08-23: byte-for-byte
> `cmp` of the blob against the on-disk file's first 30 520 bytes is
> identical, and the remainder is `\n---\n\n` + exactly the 5 958 preserved
> ADDENDUM 2 bytes, sha256 `ab90298a…`). The stated figure is corrected in §1a
> with this note as its record. (2) The R-x rows, PENDING in the draft, are
> now graded and carry their numbers in §3 and §6.

# T10a-R results: the refinement arm on T10a's B1 ceiling GATE FAIL

Campaign T, rung **T10a-R**, a follow-through arm on T10a (Sanaa directive
**H-3(a)**: *"T10a follow-through: the ceiling miss gets a refinement arm
(discretization finding, cheap)"*). Run tree
`verification/runs/T-family/T10aR_runs/`, three cases (`R_x R_q R_s`).
Pre-registration `docs/campaigns/T-family/T10aR_PREREGISTRATION.md`, frozen by
on-disk sha256 **2026-08-22 18:10:36.656 Z** — `find …/T10aR_runs -name 'R_*'`
returning zero matches at that instant — and committed as **`7150182b`**
2026-08-22 18:55:43 Z, **45 min after the hash freeze and 38 min 46 s after the
first solver started** (ADDENDUM 2 there; the commit makes the freeze
independently checkable, it does not retro-date it).

Comparator `analyse_t10aR.py`, sha256
`a3014a64f1a2e5ce507f029c45b7c1f54eaf108348cf37a63be1ca604649c5ef`, **written
and hashed before any case directory existed, verified byte-identical to the
committed blob at analysis time, and never edited.**

**This arm grades NOTHING against T10a's band.** T10a is closed at GATE FAIL
and stands unchanged. Every verdict below is PASS or GATE FAIL **against this
arm's own registered prediction interval**, with the falsifier named in
advance.

**Scope: the BOX only.** No spheres — T10a's S0/S1 NOT A RESULT rows come from
the non-converging view-factor row-sum defect and are directive H-3(b).

## 1a. The pre-registration's ADDENDUM 2 is unfrozen and uncommitted at grading — disclosed

**Recorded on the chief's binding ruling, 2026-08-22, and dated here.**

`docs/campaigns/T-family/T10aR_PREREGISTRATION.md` carries an **ADDENDUM 2**
(dated 2026-08-22 19:12 Z, amended 19:44 Z) which exists **on disk only**. It
is **not frozen and not committed.** This lane attempted the commit itself at
**18:25 Z and was refused by its own session's permission classifier**; the
refusal has not been retried, and — per the chief's ruling — **no other lane
and no supervisor may re-route it**, because a peer satisfying one session's
refusal by writing elsewhere routes around the refusal. The item goes to
Sanaa; if she directs the commit, she or a fresh session makes it.

**What ADDENDUM 2 contains, and how a reader pins it without a commit
witness.** Its content is preserved verbatim in the run tree as
`T10aR_runs/ADDENDUM2_content_at_grading.txt` (92 lines, 5 958 bytes),
**sha256 `ab90298a5f783e472c331d75d601b94ebc5ca37912e8641d72a97fb745a3d282`**
— the exact bytes the comparator run below is judged against. That hash is a
content hash written by this lane; **it carries no commit witness and is
weaker evidence than a committed blob**, which is precisely the fact being
disclosed rather than papered over.

**What ADDENDUM 2 does and does not touch — checkable in one command.** The
committed pre-registration blob in `7150182b` hashes
`c81223d88936212bc829e39fd5dc37956f8e9950f25f36230979e2065b70e903`. Taking the
**first 30 520 bytes** (the committed blob's length; the draft of this file
said 33 445, corrected 2026-08-23 — see the banner) of the on-disk file and
hashing them returns **the same `c81223d8…`**. The on-disk pre-registration is
therefore the committed one with ADDENDUM 2 **appended and nothing else
changed**: **every gate, threshold, prediction interval and falsifier used
below is byte-identical to the committed, independently checkable record.**
ADDENDUM 2 alters no gate — it records provenance and corrects one stated
time — and by construction it cannot, since the graded thresholds live in
`T10aR_registered.json` (`23c31bbee337a3ee…`, committed and unmodified) and are
applied by `analyse_t10aR.py` (`a3014a64f1a2e5ce…`, committed and unmodified).

**The arm is graded anyway**, as ruled, and the verdict line carries the
disclosure.

## 2. Method, instruments, and what refuses

**Cases, one registered change each from the frozen `B_f`.** `build_t10aR.py`
imports the frozen `build_t10a.py` and calls its own dictionary writers — it
copies no dictionary text — then **refuses** unless every file not registered
as changed is byte-identical (sha256) to `T10a_runs/B_f`, and every file
registered as changed is not. All three passed. Verified by `diff`:

- `R_x` — `blockMeshDict` `(42 42 21)` → `(68 68 34)`. **One line.**
- `R_q` — `viewFactorsDict` `distTol 8;` → `distTol 80;`. **One line.**
- `R_s` — `fvSolution` five lines + `controlDict` two lines, exactly §1.3's
  table. `fvSchemes` byte-identical.

**Frozen instruments, imported and never edited.** `analyse_t10aR.py` imports
`analyse_t10a.py` (sha256 `ad6a32861dda…434de65`, the post-repair file T10a
published) and uses its `measure`, `row_value`, `mesh_patches`, `time_dirs`,
`read_qr_all`, `patch_values`, `read_emissivities`, `sigma_used`,
`iterative_convergence`, `planted_zero_control`, `read_F`, `dense_F`,
`radiosity_on_F`, and through it `analyse_t1c.gci` (Fs 1.25, nominal r 1.6;
the comparator refuses if Fs/r differ). The frozen module's `HERE` and
`REG["cases"]` are redirected **in this process only** by a context manager
that restores both on exit — proved by the selftest — so `measure()` reads the
T10a-R tree for `R_*` and the frozen T10a tree for `B_m`/`B_f`. **No frozen
file on disk was written to.** Independent check that the shim is faithful:
it reproduces T10a's published `B_f` values to every printed digit
(6483.263010 / −3269.602153 / −1260.793300 / −1971.177941) and T10a's
published c/m/f band (p 1.4799, GCI 0.07683 %, corrected Richardson
−3267.593) from the frozen trees.

**NEW INSTRUMENT 1 — the sign-corrected Richardson extrapolate**, declared new:
`f_f + (f_f − f_m)/(r^p − 1)` (Roache). The shared `analyse_t1c.gci` returns
`f_f + (f_m − f_f)/(r^p − 1)`, the sign defect T9a §8.1 recorded and
deliberately left unedited because it sits on no grading path. **Both are
reported side by side and NOTHING is graded on either** — RX5 is a prediction
about a *reported diagnostic*, and that diagnostic uses the exact reference,
so exactly as T10a §1.1 said of the same reading, **it is not an instrument
independent of the hypothesis and grounds no repair.**

**NEW INSTRUMENT 2 — `read_F_dense_stream` + `radiosity_lean`**, declared new,
with a measured reason: `R_x`'s `constant/F` is **6 086 031 316 bytes** of
ascii and the frozen `read_F` materialises the whole file as a Python `str`
then makes three more full-length copies (`re.sub`, two `.replace`) — **> 24 GB
of transient strings on a box with ~25 GB available.** The lean path streams
line by line; peak memory is one dense n × n float64 array.
**REGISTERED VALIDATION, enforced at every run, refusal on failure:** on every
case where both paths fit, the lean matrix must be **bit-identical**
(`np.array_equal`) to the frozen one and its radiosity/reciprocity numbers
equal to ≤ 1e-12 relative. `radiosity_lean` is registered for ε = 1 only —
where `viewFactor.C`'s C matrix is the identity — and **refuses** any other
emissivity; the selftest exercises that refusal rather than asserting it.

**`--selftest` 28/28 at freeze**, before any case existed, covering both
Richardson forms against a synthetic power law, reproduction of T10a's
published p/band/Richardson, that every verdict path (PASS, GATE FAIL high
*and* low, NOT A RESULT) is reachable, that RX3 at exactly 1.0 is a GATE FAIL,
the streaming reader against a hand-written matrix, blocked vs dense
reciprocity, `radiosity_lean` against the frozen `radiosity_on_F`, the
exact-float plant rule, and that the tree shim restores the frozen module.

**Completion.** `mark_done_t10aR.py` applies the frozen strict rule unchanged
(rc = 0; `End` line; last time == `endTime`; `T` and `qr` present;
`ExecutionTime` count == `endTime`; every field newer than the case's own
`0/T`). All three cases required, no optional case.

**Guards carried over verbatim:** G1 atomic launch lock, G2 `/proc` cwd scan,
G3 no stray numeric time directory, plus refusal to run a case with no
`constant/F`. Every case launched through them; every launch logged.

## 3. Arm R-x — the fourth refinement level: the triple CONVERGES, the band OPENS, and it now COVERS the error

**The one change:** `blockMeshDict` N 42 → 68 per metre (18 496 radiating
faces, 157 216 cells), ratio 68/42 = **1.6190**, inside the family the frozen
ladder already spans (1.6250, 1.6154). Graded triple **m / f / x** =
`B_m` / `B_f` / `R_x`.

**Preprocessing complete, registered feasibility predictions held:**

| quantity | registered prediction | measured |
| --- | ---: | ---: |
| `constant/F` size | 6.08 GB | **6 086 031 316 B** |
| `globalFaceFaces` | 1.35 GB | 1 512 861 804 B |
| `viewFactorsGen` cost | ~400 core-s | 2 545 s wall at ~15 % of a core ≈ **380 core-s** |
| radiating faces | 18 496 | 18 496 |
| **generator peak memory** | **5.5 GB (this was the solver estimate; no separate generator estimate was registered)** | **21.0 GB — a MISSED prediction, reported as such** |

`viewFactorsGen` rc = 0; `blockMesh` rc = 0; `checkMesh` rc = 0. **R-x is
therefore NOT BLOCKED** — the pre-registration's §4 BLOCKED clause does not
fire.

**Completion:** STATUS `rc=0 wall=17032`, `End` line, last time 20 == endTime,
`ExecutionTime` count 20, fields newer than `0/T` — strict rule met, DONE
marker written 2026-08-23. Iteratively CONVERGED (max change between the last
two checkpoints 0.000e+00); planted-zero recovered exactly; closure_raw
8.938e-04 against the 1e-2 guard.

### 3.1 The graded triple and the four-level picture

**B1 ceiling, m / f / x** = −3271.619602 → −3269.602153 → **−3268.140038**
W/m² against exact −3265.532221 (σ_OF). Level errors **−6.0874 / −4.0699 /
−2.6078** W/m².

| row | quantity | measured | registered prediction | interval | **verdict** |
| --- | --- | ---: | ---: | --- | --- |
| **RX1** | B1 dev at x, % | **0.07986** | 0.083 | [0.070, 0.100] | **PASS** |
| **RX2** | observed p of m/f/x | **0.6850** | 1.15 | [0.80, 1.55] | **GATE FAIL** (low; the p > 2.00 falsifier did not fire; triple CONVERGING) |
| **RX3** | dev ÷ band at x | **0.542** | 2.0 | > 1.0 | **GATE FAIL — falsifier FIRED** (dev/band ≤ 1.0: the band covers the error) |
| **RX4** | \|e_f\| / \|e_x\| | **1.5607** | 1.50 | [1.30, 1.70] | **PASS** |
| **RX5** | corrected Richardson (m/f/x), % from exact | **0.03803** | 0.02 | [0, 0.100] | **PASS** (reported diagnostic; grades nothing) |

The GCI band at x is **0.14724 %** against a deviation of **0.07986 %**.
Richardson side by side, as registered: shared (sign-defect) form
−3271.98959; corrected form **−3264.290487** (0.03803 % from exact). Neither
grades anything.

**All four graded box rows, m/f/x, from the comparator:**

| row | c (published) | m | f | x | exact | dev_x % | p | band % | dev/band |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B0 | 6480.760 | 6482.28742 | 6483.26301 | 6483.88629 | 6484.92094 | 0.01595 | 0.9533 | 0.02126 | 0.751 |
| **B1** | −3275.664 | −3271.61960 | −3269.60215 | **−3268.14004** | −3265.53222 | **0.07986** | **0.6850** | **0.14724** | **0.542** |
| B2 | −1269.197 | −1264.16377 | −1260.79330 | −1258.55637 | −1254.69165 | 0.30802 | 0.8722 | 0.43843 | 0.703 |
| B3 | −1980.140 | −1974.80056 | −1971.17794 | −1968.79035 | −1964.69708 | 0.20834 | 0.8870 | 0.29306 | 0.711 |

**Every triple is CONVERGING and every triple is monotone** (GCI quoted on
monotone values only, per the standing Roache rule). **Every dev/band < 1**:
at the fourth level the band covers the error on all four rows.

### 3.2 The §2.1 registered tension, resolved by measurement

The pre-registration's §2.1 laid out two branches before the run. **Branch 1
appeared, slightly overshot in this arm's favour:** the level-error ratio
stayed ≈ 1.5 (measured 1.5607, RX4 PASS mid-interval), the observed p
collapsed (measured 0.6850, below even branch 1's computed 0.840), the band
opened (0.14724 % vs branch 1's computed 0.107 %) and **covers** the 0.07986 %
error — dev/band 0.542, **RX3 falsified exactly as branch 1 said it would
be.** The measured `f_x` = −3268.140 sits within 0.1 W/m² of branch 1's
computed −3268.245. Branch 2 (p holding at 1.48, band 0.038 %, dev/band 2.45)
did not appear.

**What that means, in one sentence:** the T10a/T9a pattern — a GCI band armed
from a pre-asymptotic triple, smaller than the very error it is supposed to
cover — **does not persist at the fourth level on this enclosure**: the
implied order was the artefact (1.48 → 0.685), and once the differences slow
to match the actual error decay, Fs = 1.25 over p ≈ 0.7–0.95 opens the band
past the miss on every row.

**One more h-independence datum, reported not graded:** `R_x`'s raw row-sum
max defect is **0.0303** vs `B_f`'s 0.0304 — the view-factor row-sum defect
did not shrink under a 2.6× mesh refinement, consistent with T10a-VF's closed
form having no `h` in it.

## 4. Arm R-q — the view-factor integration method: GATE FAIL, falsifier fired

**The one change:** `constant/viewFactorsDict` `distTol` 8 → 80. Everything
else byte-identical to the frozen `B_f` (checked by sha256 at build).

**What the knob is, and the directive correction recorded before the solve.**
The directive proposed `nRayPerFace` or turning agglomeration off. **Neither
exists on this path**, established from source at build time and written into
the pre-registration §1.2 before any case ran: `viewFactorsGen.C` v2606 reads
exactly seven dictionary entries (`writeViewFactorMatrix`, `dumpRays`,
`debug`, `GaussQuadTol`, `distTol`, `alpha`, `intTol`) — `nRayPerFace` belongs
to `createViewFactors`, which T10a used only for the reported-only 2D `H_2d`
row — and agglomeration is already off by T10a INTERPRETATION 4 (`finalAgglom`
absent, one radiating face per mesh face). `distTol` is the knob not yet
varied. From `viewFactorsGen.C:967-1002`, per face pair:

```
dist = |C_i - C_j| / ((sqrt(A_i/pi) + sqrt(A_j/pi))/2)
dist >  distTol -> 2AI: double AREA integral, ONE midpoint sample per pair
dist <= distTol -> 2LI: double LINE integral over four edge pairs, Gauss
                        quadrature refined until GaussQuadTol
```

At N = 42 the face equivalent radius is 0.01343 m, so `distTol` 8 puts the
switch at 0.107 m and nearly every visible pair in a 1 × 1 × 0.5 m box gets
the **midpoint** formula; `distTol` 80 moves it to 1.074 m, past all but the
longest of the ≤ 1.5 m diagonals, so nearly every pair is integrated by
**2LI**.

### 4.1 The rows

| row | patch | `B_f` (distTol 8) | `R_q` (distTol 80) | move | dev from exact: `B_f` → `R_q` |
| --- | --- | ---: | ---: | ---: | --- |
| **RQ1** | ceiling (B1) | −3269.6021532 | −3268.0977949 | **0.04601 %** | 0.12463 → **0.07857 %** |
| RQ2 | floor (B0) | 6483.2630102 | 6483.8975758 | 0.00979 % | 0.02557 → **0.01578 %** |
| RQ2 | x-walls (B2) | −1260.7933001 | −1258.5810235 | **0.17547 %** | 0.48631 → **0.30999 %** |
| RQ2 | y-walls (B3) | −1971.1779407 | −1968.8205983 | **0.11959 %** | 0.32987 → **0.20988 %** |

**Verdicts against the registered intervals:**

- **RQ1 — GATE FAIL.** B1 moved **0.04601 %** against a PASS interval of
  [0, 0.010 %]: **4.6× outside it.** The registered falsifier (> 0.050 %) did
  **not** fire — by 0.004 percentage points.
- **RQ2 — GATE FAIL, falsifier FIRED.** Worst of B0/B2/B3 is B2 at
  **0.17547 %**, and both B2 (0.17547 %) and B3 (0.11959 %) exceed the
  registered 0.050 % falsifier.

**What moved, and in which direction.** Every row moved **toward exact**, and
the box's remaining error fell by roughly a third: B1 0.12463 → 0.07857 %,
B2 0.48631 → 0.30999 %, B3 0.32987 → 0.20988 %, B0 0.02557 → 0.01578 %.
**A material part of T10a's B1 ceiling miss IS a view-factor integration
artefact**, which is the opposite of the registered prediction.

**Where the improvement lives — the matrix, not the assembly.** Measured by
the lean F instrument:

| case | row-sum max defect | mean row sum | `closure_raw` | `closure_F` | excess | reciprocity | Python-on-F vs solver |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `B_f` | 0.030375 | 1.002492 | 1.410e-03 | 1.410e-03 | 1.52e-17 | 2.23e-14 | 1.05e-14 |
| `R_q` | **0.029235** | **1.001758** | **8.939e-04** | 8.939e-04 | 1.01e-15 | 2.23e-14 | 1.20e-14 |
| `R_s` | 0.030375 | 1.002492 | 1.410e-03 | 1.410e-03 | 1.52e-17 | 2.23e-14 | 1.05e-14 |

2LI produces a matrix whose rows sum closer to 1 (mean excess 0.002492 →
0.001758, a **29 % reduction**) and whose heat balance closes better
(1.410e-03 → 8.939e-04). The comparator's own radiosity solve on the written
`F` reproduces the solver to ~1e-14 in every case, so **the assembly and
addressing are consistent with their own matrix and the flux change is
inherited directly from the better view factors.** No case is VOID: closure
excess ≤ 1.0e-15 against the T10a guard's 1e-2.

**The reservation registered in advance, and confirmed.** Pre-registration
§1.2 recorded, before any solve, that the directive's prediction was being
registered as given *while the analyst's own reading of `viewFactorsGen.C`
disagreed with its reasoning* — `distTol` switches integration **method**
(2AI midpoint → 2LI Gauss contour) for the majority of the matrix rather than
refining a tolerance, so a move above 0.05 % was plausible and would be a real
finding. That is what happened. **The prediction is scored as missed and the
reservation as confirmed; neither is retro-fitted**, and the falsifier was
named before the number existed.

**Cost, not free.** `distTol` 80 cost **221 s** of view-factor generation
against `B_f`'s 49.7 s on the identical mesh (≈ 4.4×, contended), for a
matrix that is better but not correct — the row-sum defect shrinks by 29 %,
it does not vanish.

## 5. Arm R-s — solver tolerance and iteration count: PASS, and it is an identity

**The one change:** the registered bundle (pre-registration §1.3) —
`p_rgh` and `(U|h)` tolerance 1e-08 → **1e-12**, both `relTol` → **0**,
`nNonOrthogonalCorrectors` 1 → **3**, `endTime` 20 → **60** with
`writeInterval` 15 (four checkpoints, L-140). **`fvSchemes` byte-identical to
`B_f`** — the `laplacian`/`div` schemes for the convective-conductive part are
untouched, as the directive required.

**The knob the directive named does not exist, recorded before the solve.**
With `constantEmissivity true; useDirectSolver true;` the radiosity system is
not solved iteratively at all: `viewFactor.C:1008` calls `LUsolve` on a dense
LU cached at the first radiation iteration. There is no radiosity tolerance
and no radiosity iteration count to tighten; the directive's *"solver
tolerance for the radiosity G to 1e-10"* has no dictionary entry to land in,
and reaching one would need `useDirectSolver false` — a second change, and a
model path T10a explicitly did not grade (its §9). R-s therefore tightens
every tolerance and iteration count that **does** exist, as one bundle,
registered as a bundle in advance.

**Precondition for the identity, checked not assumed.** `R_s` regenerates its
own view-factor matrix. `sha256(R_s/constant/F)` =
`23347e5d52d9135a8bdcd44271cd4c03ac1b350fa632f65b24e4aa582111c5cd` =
`sha256(B_f/constant/F)` — **byte-identical**, so `viewFactorsGen` is
deterministic and the Charter §2a identity has a real referent. Had it
differed, RS2 would have been NOT A RESULT and the non-determinism reported.

### 5.1 The rows

| row | patch | `B_f` [W/m²] | `R_s` [W/m²] | move | verdict vs registered |
| --- | --- | ---: | ---: | ---: | --- |
| RS1 | ceiling (B1) | −3269.6021531535562 | −3269.6021531535562 | **0.000e+00 %** | **PASS** (interval [0, 0.005 %]) |
| — | floor (B0) | 6483.2630101998857 | 6483.2630101998857 | 0.000e+00 % | reported |
| — | x-walls (B2) | −1260.7933001034194 | −1260.7933001034194 | 0.000e+00 % | reported |
| — | y-walls (B3) | −1971.1779406534574 | −1971.1779406534574 | 0.000e+00 % | reported |

**RS2, the identity (Charter §2a): max |qr(R_s) − qr(B_f)| over all 7 056
radiating faces = 0.000000e+00 W/m². Bit-identical, every face.** `B_f` read
at t = 20, `R_s` at t = 60. **PASS** against the registered interval [0, 0].

**What it establishes.** Every wall temperature is `fixedValue` and the
radiosity solve is a direct LU with no tolerance, so `qr` is determined by
T, ε and F at the first radiation solve and cannot move afterwards. Tightening
the solvers 10 000-fold, driving both relative tolerances to zero, tripling
the non-orthogonal correctors and running three times as long changes **not
one bit** of any flux. **B1's 0.12463 % miss is not a solver-tolerance
artefact, and the whole category — tolerance, iteration count, non-orthogonal
correction, run length — is ruled out at once.** That is what the bundle was
registered to buy, and it bought it.

**What it does not establish:** because it is a bundle, a *non-null* result
would have identified no single entry. It returned null, so nothing needs
bisecting — but the bundle's limitation is stated as registered, not
discovered.

## 6. Arm verdict

**T10a-R: GATE FAIL — 5 PASS / 4 GATE FAIL / 0 NOT A RESULT** against this
arm's own registered predictions (nothing graded against T10a's band; T10a is
closed and unchanged). Graded 2026-08-23 by the frozen `analyse_t10aR.py`
(`a3014a64f1a2…4649c5ef`, byte-identical to the `7150182b` blob), which wrote
`gate_t10aR.json`. **Disclosure carried on this verdict line, per the chief's
ruling recorded in §1a: the pre-registration's ADDENDUM 2 is on disk,
unfrozen and uncommitted at grading; every gate, threshold, interval and
falsifier applied is byte-identical to the committed `7150182b` record.**

| row | verdict | falsifier |
| --- | --- | --- |
| RX1 | PASS | — |
| RX2 | GATE FAIL (p low) | p > 2.00 did **not** fire |
| RX3 | GATE FAIL | **FIRED** — the band covers the error |
| RX4 | PASS | — |
| RX5 | PASS | — |
| RQ1 | GATE FAIL (4.6× outside) | > 0.050 % did **not** fire (0.04601 %) |
| RQ2 | GATE FAIL | **FIRED** — B2 0.17547 %, B3 0.11959 % |
| RS1 | PASS | — |
| RS2 | PASS (identity, bit-exact) | — |

**The two findings, stated as the registered falsifiers frame them:**

1. **The band-smaller-than-error pattern does not persist at the fourth
   level** (RX3 falsified): the m/f/x triple is CONVERGING at p 0.685, the
   Fs = 1.25 GCI opens to 0.147 % and covers the 0.0799 % error — on B1 and
   on every other box row (dev/band 0.54–0.75). The c/m/f implied order 1.48
   was the artefact.
2. **A material part of the box error is the view-factor integration
   method** (RQ2 falsified, RQ1 4.6× outside its interval): switching 2AI
   midpoint → 2LI contour moves every row toward exact by up to 0.175 %,
   against a registered prediction of ≤ 0.010 %. The directive's reasoning
   was falsified while the analyst's registered reservation (prereg §1.2) was
   confirmed — recorded in advance, on the record.

## 7. Cost — measured against the registered prediction, overrun disclosed

From `cost_t10aR.py` (accounting only, grades nothing), wall-second basis
under contention (gross, not cleaned):

| case | prep s | solve s | total s | predicted s | × pred | peak GB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R_q | 223 | 2 639 | 2 862 | 469 | 6.10 | 2.6 |
| R_s | 62 | 1 421 | 1 483 | 755 | 1.96 | 2.6 |
| R_x | 2 592 | 17 032 | 19 624 | 7 418 | 2.65 | 20.1 (gen) / 12.0 (solve) |

**Total 23 969 core-s = 6.66 core-h = $0.342** against $0.123 predicted —
**2.77×, within the registered 10× stop threshold** (24.0 core-h / $1.23), so
no case was stopped. The overrun is contention (12 T-family solvers live at
launch) plus the generator's under-predicted memory/wall at n = 18 496; the
figure is **gross** and the rate $0.0513/core-h is **owner-stated
(reported-by-owner, not measured)** — the box cannot read its own billing.
The generator's 21.0 GB peak RSS against a 5.5 GB solver-basis estimate is a
**missed prediction, reported as such** (§3 draft table, unchanged).

## 8. What this arm does NOT show

Written in the pre-registration (§6) before any number existed, restated here
against what actually came back, so it cannot be trimmed to fit.

- **Nothing about the spheres.** T10a's S0/S1 stay NOT A RESULT. This arm ran
  no sphere case and says nothing about the non-converging 4.3–4.8 %
  outer-sphere row-sum defect. That is directive H-3(b).
- **Nothing about T10a's verdict.** T10a is closed at GATE FAIL and no row of
  it moved. A PASS here is a prediction met, not a rung repaired; a GATE FAIL
  here does not make T10a worse. `gate_t10a.json` was not touched.
- **R-q does not say which view factors are right.** It says the flux depends
  on the integration *method* and that 2LI moves every box row toward the
  exact answer. The exact *continuous* view factors are known (Howell
  C-11/C-14); the exact **discrete-enclosure** view factors for a given mesh
  are not, so "2LI is closer" is measured against the continuous reference and
  is not a proof that 2LI is the correct discretisation. A row-sum defect that
  shrinks is evidence, not a derivation.
- **R-q is not a free improvement.** `distTol` 80 cost 221 s of generation
  against `B_f`'s 49.7 s at the same mesh — and the row-sum defect **does not
  vanish** (max defect 0.030375 → 0.029235; mean row sum 1.002492 → 1.001758).
  The utility's visibility/assembly error survives the method change.
- **R-s cannot separate its own bundle.** Seven entries were tightened at once
  by registration. The null result rules out the category; a non-null result
  would have identified nothing. Stated in advance, not after.
- **No asymptotic claim.** A fourth level that behaves is still not a
  demonstrated asymptotic range. The observed p is quoted beside every band
  and no band is a proof of order.
- **No participating media, no spectral or non-grey behaviour, no convection
  or conjugate coupling, no grey non-symmetric enclosure, no
  `faceAgglomerate`, no iterative radiosity solver, no parallel operation** —
  every T10a §9 bypass is inherited unchanged. In particular the grey
  radiosity path is still verified only in the ε = 1 limit; **this arm is all
  black surfaces and adds nothing to the grey claim.**
- **Nothing about production meshes.** N = 68 per metre on a 1 m box is 1.5 cm
  cells and a 6.1 GB dense view-factor matrix. No room-scale case will carry
  this, and nothing here says what `distTol` should be when it cannot.
- **The freeze is weaker than a pre-compute commit.** The gates were fixed by
  on-disk sha256 at 18:10:36 Z, +4 min 58 s before the first preprocessing and
  +6 min 20 s before the first solver; the commit `7150182b` came 45 min later,
  **38 min 46 s after the first solver started.** Every committed blob was
  verified byte-identical to what ran, which is what rule 2 actually asks — but
  a reader should read this as "hashed before compute, committed after", not as
  "committed before compute".

---

## 9. DATED ADDENDUM, 2026-08-25 — `build_t10aR.py:207` ASSERTS AN IDENTITY IT DOES NOT CONSTRUCT. Disclosed, NOT repaired.

**Lines whose number changed above this section: 0.** Appended at the foot.
**No verdict, gate, threshold, band, cap or label moves.** T10a-R's grading is
untouched and stands exactly as `gate_t10aR.json` recorded it.

### 9.1 The defect

`verification/runs/T-family/T10aR_runs/build_t10aR.py:207-208` prints, after the
build loop and **unconditionally**:

> `every other dictionary and every 0.orig field verified byte-identical to the
> frozen T10a B_f.`

**Both sides of that identity are literals.** The sentence names *"every other
dictionary"* and *"the frozen T10a `B_f`"* without deriving either from what was
actually compared — no count, no path, no sha.

**The mechanism behind it is SOUND, and that is the point.** `verify()` genuinely
refuses on mismatch in both directions — `:186` `REFUSE: {name} {rel} differs
from B_f but was registered identical` and `:196` `REFUSE: {name} {rel} is
identical to B_f but was registered CHANGED` — so the sentence prints **only**
when every check passed. **It is true by CONTROL FLOW, not by construction from
the values it asserts about.** Change `verify()` to warn instead of raise, or
hand `main()` an empty case set, and **the sentence still prints, unchanged and
false.**

**This is the class the ansys-verification team found in their own instrument** —
a freeze line reading *"X is byte-identical to HEAD:Y"* while naming two
different files as the same thing — and it is **cited as their finding.** Their
rule is the right one and this record adopts it: **print from the variable, never
from a literal.** The reason it matters is not aesthetics: **this is the sentence
a reader quotes when asserting that a freeze held.**

### 9.2 WHY IT IS NOT REPAIRED — the boundary rule, and it bites here

**`build_t10aR.py` is a FROZEN artifact whose blob IS cited evidence.** Its
sha256 `2bc6f3c22bad4143bcdec40a0a47b193b6caf93aa76ec2a77b7985fbf74c1e73` appears
in **three** places as freeze proof:

| citation | what it proves there |
|---|---|
| `T10aR_PREREGISTRATION.md:417` | §5.1's repaired-builder hash |
| `T10aR_PREREGISTRATION.md:576` | the frozen manifest row |
| `gate_t10aR.json:11` | the grading artifact's own record of the build path |

**Editing that file — even at constant line count, even to make a false sentence
true — changes the blob that IS the evidence**, and would silently falsify three
citations including one inside a graded gate artifact.

**The rule, adopted from ansys-verification via the chief:** *the in-place
correction technique's value is inversely related to how load-bearing the file's
IDENTITY is.* **Use it on census tables a reader consults; never on freeze
artifacts.** And the strong assertion *"lines whose number changed: 0"* is
**only provable for a pure append** — at constant line count one can assert the
line count held, but **not that the artifact a citation points at is the same
artifact.**

**This team used the in-place technique correctly earlier the same day** on
`MATRIX_CONTRIBUTION.md`'s §8.1/§8.2 census tables — a living record, no sha
cited, and the foot was where nobody looks. **Here the same technique would have
been a defect.** The boundary is real and it was reached within the hour.

**Disposition: DISCLOSED, NOT REPAIRED.** T10a-R is already graded, so **rule 2
closes the gates**: changes land only as dated addenda that cannot alter a gate,
threshold, cap or label — which is what this is. **A repair, if ever wanted, is a
NEW build script under a NEW pre-registration**, with both shas quoted so the
original freeze stays quotable. **It is not wanted today**: nothing in T10a-R's
verdict depends on that sentence, and the checks it describes did run and did
refuse.

### 9.3 The check that mattered more, and it came back clean

**The T1b L4 grading chain was swept for this same defect class before the pool
grades** — `analyse_t1b_L4.py`, `analyse_t1b.py`, `analyse_t1c.py`,
`mark_done_t1b_L4.py` and `planted_zero_control_t1b.py`. **They assert no
identity in prose at all.** The only matches are tolerance statements
(`analyse_t1b.py:273`, `analyse_t1b_L4.py:278`, both *"NOT verified to that
tolerance"*), which claim nothing about file identity. **The instrument that will
grade the pool is clean of this class.**

**`analyse_t10aR.py:674-675` was checked and is SOUND**, and is recorded so the
sweep's negative is not read as untested: it prints **both actual sha prefixes**
beside their labels and derives `IDENTICAL` from `sha_f == sha_s` on the **same
two variables** it printed. A reader sees the evidence, not a claim about it.
**That is the shape §9.1 asks for, already present in a sibling instrument** —
which is why the defect at `:207` reads as an oversight rather than a
misunderstanding.
