# F27-WOMERSLEY EINF-TOPOLOGY SUCCESSOR — RE-REGISTRATION R3 (MESH-TOPOLOGY ROOT-CAUSE FIX)

> **FROZEN — AUTHORISED (2026-09-08).** The cfd supervisor has PERSONALLY completed
> both non-delegable §3 checks and **both PASS**: **check-1** (both R3
> measurement-script diffs — grader `grade_f27_r3.py` and exact model
> `exact_f27_r3.py` — read at source as diffs; measurement logic invariant; the E2
> and Einf gate bands unchanged) and **check-4** (gate/lever/root/commit;
> pre-registration committed before compute; gates, thresholds and bands
> byte-identical to the frozen parent; lever = the mesh-topology rounded-square
> core/ring interface with rm = 0.3989422804014327, **RULED ACCEPTED** — principled
> area-equivalent circle, band-invariant, well-conditioned mesh clearing all gates
> with wide margin; run root ABSENT; grading path pinned below). **No solver was run
> in preparing this registration.** The three-level butterfly mesh WAS built
> (blockMesh/checkMesh/postProcess only — mesh generation, not the physics solve —
> "BUILD BEFORE YOU FREEZE", MESH_STANDARD 8.1) to register the checkMesh readings
> and the same-stencil reference W_REF_MESH and to prove A_MESH (hence the band) is
> unchanged. **Nothing is sent, filed, uploaded, registered or posted (rule 7).**
>
> **GRADING-PATH FREEZE (rule 2 — pinned at this freeze commit; no gate, threshold,
> band, BAND_FACTOR, reference, cap (625) or label is altered by this freeze):**
> - grader `cases/F27_WOMERSLEY_PIPE/einf_topology_successor/grade_f27_r3.py` — git blob `01acbec95f5d161c7fbb7694ebeedab1f0c4bd13`
> - exact model `cases/F27_WOMERSLEY_PIPE/exact_f27_r3.py` — git blob `d5a834cc7edc8ccff4be3315ec5624aa65350707`
> - driver `cases/F27_WOMERSLEY_PIPE/einf_topology_successor/run_f27_r3.sh` — git blob `24cfee11b880324df6aac8519123cc7f8d7cc48d`, sha256 `91c3d8239aca14edc243b9084454d81d681c0ca4d020b60ff5c24c37a3955d96`
> - builder `cases/F27_WOMERSLEY_PIPE/einf_topology_successor/build_f27_r3.py` — git blob `72298744f42aa98976ee4026de90b078b36b865e`, sha256 `7351d70496e08790abbf281f5eea168a6c18a27ae1a43a6169641b2aeb03a348`
> - `system/blockMeshDict.template` — git blob `d45e11fe46398bf6d17bf3490ef4d95d2661bcf6`, sha256 `5dd1cf77c01942b76c508137a7552a3ec69f469e218f16e3d111a0b999ff9c1c`
> - `system/fvSchemes` sha256 `59b77114798bad38ccfd5c9ebedcf8d69b0765b236e96472f13872c91a4fe81f`; `system/fvSolution` sha256 `fea071de85b6dfc8257c88d5910cd30c8ec53078a7dd558beba6343ca72fa32f` (both byte-identical to R2 numerics — numerics unchanged)

---

## 0. WHAT THIS IS, AND WHAT IT IS NOT

This is the **Einf-targeted successor to the R2 GATE FAIL**. The R2 run
(`F27_NUMERICS_SUCCESSOR_R2_RESULTS.md`, freeze `6aabb3c1`) graded a **REAL,
honest result** — both triples CONVERGING, so **not** `NOT A RESULT`:

- **G-F27R-1 E2 = PASS** (observed order `2.0671`, fine `7.285879634110018e-04`
  inside band).
- **G-F27R-2 Einf = GATE FAIL** (observed order `1.2718`, fine
  `4.136254537709814e-03` **above** the band upper bound `2.849460293061811e-03`).

**The diagnosis (cfd supervisor's check-3, DEFENDED — not relitigated here).** The
Einf GATE FAIL is a **LOCALISED mesh-topology artifact, not the method's genuine
Einf-order limit.** It is a **D4 corner mode** sitting at the **butterfly O-grid
core/ring block-interface corner** at r/R = `CORE_FRAC` = 0.5, θ = 45° (+90°k),
with no physical counterpart in axisymmetric pipe flow. Evidence on record: the
max/RMS ratio of the Einf error grows 1.560 → 3.114 → 5.677 across the triple with
support shrinking to 0.23 % of cells at the corner; the grader's own documented D4
blind-spot note (`grade_f27_successor_r2.py:318–329`, the `a_theta_of` docstring)
identifies exactly this class of mode; and `CORE_FRAC = 0.5` is fixed at
`exact_f27.py:89`.

**This R3 re-registration builds the fix to that diagnosis.** It changes **ONE
physical thing — the mesh topology at the core/ring interface** — so the D4 corner
mode is resolved rather than aliased. It changes **NO gate, NO threshold and NO
band**: the E2 and Einf bands are **byte-identical** to the frozen parent, proven
below by the shared discretisation model. The successor **NUMERICS are UNCHANGED
from R2** (byte-identical `fvSchemes` / `fvSolution`, same sha256).

**Frozen parents (rule 6, bodies never edited).** The frozen R2 pre-registration
`verification/campaign/F27_NUMERICS_SUCCESSOR_R2_PREREGISTRATION.md` (freeze
`6aabb3c1`) and, before it, the successor
`F27_NUMERICS_SUCCESSOR_PREREGISTRATION.md` (`b86fe0cc`). This R3 re-registration is
a **separate document with its own commit**; the parents are cited, not rewritten.

---

## 1. THE LEVER — mesh-topology root-cause fix (PRIMARY), scheme-junction (FALLBACK)

### 1.1 PRIMARY (built and validated): rounded-square core/ring interface

The frozen butterfly `blockMeshDict.template` builds the outer wall as `arc` edges
(a true circle) but leaves the **core/ring interface a straight SQUARE** whose four
corners sit at r = CORE_FRAC·R = 0.5, θ = 45/135/225/315°. **Those four sharp
block-interface corners are the geometric feature the D4 corner mode aliases onto.**

The fix re-shapes the interface to the **AREA-EQUIVALENT CIRCLE of the frozen square
core** — a *rounded square*. The frozen square core (corners at r = 0.5, side
2·(0.5/√2) = 0.70710678) has cross-sectional area exactly **0.5**; the circle of the
same area has radius

  rm = √(0.5/π) = 0.5·√(2/π) = **0.3989422804014327**.

Eight `arc` edges (four at each z-face) bulge the interface from the square out to
this circle:

```
arc 0 1 (0 -0.3989422804014327 0)   arc 1 2 (0.3989422804014327 0 0)
arc 2 3 (0 0.3989422804014327 0)    arc 3 0 (-0.3989422804014327 0 0)
arc 8 9 (0 -0.3989422804014327 1)   arc 9 10 (0.3989422804014327 0 1)
arc 10 11 (0 0.3989422804014327 1)  arc 11 8 (-0.3989422804014327 0 1)
```

**Why area-equivalent, and why it is NOT answer-fitting.** The bulge radius is a
**geometric principle** — the minimal, area-preserving reshape of the core — chosen
**independently of any solved value** AND independently of the mesh-quality metric.
It is defensible for two reasons that both hold before any solve:

1. **The band is INVARIANT to rm** (proven in §2 and §4): A_MESH depends only on the
   OUTER WALL (unchanged), so both bands are byte-identical for **every** rm. The
   choice of rm therefore **cannot** move the acceptance region — it is physically
   impossible for it to be an answer-fit of the gate.
2. **rm = 0.3989 nearly minimises max non-orthogonality** as a by-product (§1.3),
   which is the *legitimate mesh-quality objective* — you are allowed to build a
   good mesh — and it is frozen here **before** any solve.

**A FULL circle (rm = 0.5) was BUILT and REJECTED.** It over-distorts the core
corner: it fails MESH_STANDARD 3.1 (medium 71.6°, fine 80.6° > 70° gate) and the
volume-ratio bound (fine 17.1 > 8.0). This is the classic reason butterfly cores are
rounded squares, not full circles. The rejection is recorded in the template header.

Everything else is unchanged: NC/NR/NZ at every level, CORE_FRAC, the outer wall
arcs, the five blocks, and `simpleGrading (1 1 1)` in all five (MESH_STANDARD 9.2
read-back holds — the interface arc is an `edges` entry, **not** a grading
multiplier).

### 1.2 FALLBACK (documented, NOT chosen): scheme change at the interface

A numerics-junction alternative — a local limited/blended discretisation applied at
the core/ring interface faces to suppress the aliased corner mode — was considered
as a documented fallback. It is **not primary**, for three reasons stated so the
fork is on record:

- **A mesh-topology artifact takes a mesh-topology fix.** The diagnosis (check-3,
  defended) is that the mode has **no physical counterpart** and is created by the
  interface geometry. Removing the geometric feature (the corner) removes the mode's
  cause; a scheme change only *masks its symptom* by numerically damping it, leaving
  the corner in place and the mode order-degrading.
- **The successor already limits.** R2 is `Gauss linear limited 0.5` / `limited 0.5`
  / `cellLimited Gauss linear 1` with `nNonOrthogonalCorrectors 3` — the numerics are
  **already the maximally-limited robustness choice** for high non-orthogonality, and
  it still GATE FAILed Einf at 40° corner non-orthogonality. Further scheme limiting
  would trade the Einf artifact for **additional numerical diffusion that degrades
  E2** (which currently PASSes at order 2.07); the mesh fix improves the corner
  **without** touching the schemes, so E2's clean second order is preserved.
- **Verifiability.** A local scheme junction is an interior-face selection that is
  hard to census and easy to mis-target; a mesh reshape is inspected directly in the
  built `checkMesh` readings and the (1 1 1) grading read-back.

**Fork status:** this lane judges the primary lever **settled** — the diagnosis is a
mesh-topology artifact and the physically-correct fix is mesh-topology; the fallback
is documented, not chosen. The one genuinely-open sub-question this lane flags for
the supervisor is a **judgment on the exact bulge value** (§6): the area-equivalent
circle rm = 0.3989 is principled and band-invariant, but the supervisor may prefer a
different principled rm (e.g. an explicit non-orthogonality-minimising sweep value).
Because the band is byte-identical for every rm, this is a mesh-quality preference,
not a gate decision — but it is load-bearing for whether the run resolves the mode,
so it is left for check-4.

### 1.3 BUILT-MESH EVIDENCE (all three levels; mesh generation only, no solver)

`build_f27_r3.py` built all three levels; `checkMesh` reported **`Mesh OK`** at each:

| level | cells | max non-ortho (deg) | max skew | max aspect | vol ratio | grading read-back |
|---|---|---|---|---|---|---|
| coarse | 3,840 | **19.32** | 0.726 | 2.11 | 2.48 | (1 1 1) × 5 |
| medium | 30,720 | **24.38** | 0.721 | 2.33 | 2.75 | (1 1 1) × 5 |
| fine | 245,760 | **27.25** | 0.721 | 2.46 | 2.90 | (1 1 1) × 5 |
| gate (3.1 / 3.2 / bound) | — | ≤ 70 | ≤ 4 | (advisory 1000) | ≤ 8 | must be (1 1 1) |

Against the **frozen square** interface (documented in the frozen template header:
28.59 / 36.16 / 40.42° max non-orthogonality), the rounded square **reduces the
corner non-orthogonality at every level** and **arrests its growth** across the
ladder (frozen span 28.6→40.4 = 11.8°; R3 span 19.3→27.3 = 8.0°) — restoring
geometric similarity, which is the tell that the corner singularity is now resolved
rather than sharpening under refinement. All gates pass with wide margin.

---

## 2. THE GATES, THRESHOLDS AND BANDS — BYTE-IDENTICAL TO THE FROZEN PARENT

The bands are produced by the **shared discretisation model** (`exact_f27_r3.py`,
imported by the R3 grader) via `predictions()` and `BAND_FACTOR = 5.0`. The band
inputs are **MODEL_NR** (a function of NC, NR — unchanged), **STEPS** (unchanged),
and **r_eff = √(A_MESH/(π·LZ))** (A_MESH unchanged — the wall is untouched).
W_REF_MESH — the only value that moved (§3) — is a **REPORTED-NOT-GATED reference**
and enters **NO** band.

| gate | quantity | band (IEEE double literals) | reference |
|---|---|---|---|
| G-F27R-1 | `E2_velocity_locked_phase` | `[6.052738753361828e-05, 0.001513184688340457]` | 0.0 |
| G-F27R-2 | `Einf_axial_velocity_locked_phase` | `[0.00011397841172247245, 0.002849460293061811]` | 0.0 |

**BYTE-IDENTICAL ASSERTION (executed 2026-09-08, no solver).** The band literals
`exact_f27_r3.predictions()` emits were compared field-for-field against the frozen
`exact_f27.predictions()`:

- `E2_pred` frozen `0.0003026369376680914` == R3 `0.0003026369376680914` → **True**
- `Einf_pred` frozen `0.0005698920586123623` == R3 `0.0005698920586123623` → **True**
- `r_eff` frozen `0.999799206415688` == R3 `0.999799206415688` → **True**
- G-F27R-1 band: R3 `[6.052738753361828e-05, 0.001513184688340457]` == parent → **True**
- G-F27R-2 band: R3 `[0.00011397841172247245, 0.002849460293061811]` == parent → **True**
- **BYTE-IDENTICAL BANDS ASSERTION: PASS.** These band literals match
  `F27_NUMERICS_SUCCESSOR_R2_PREREGISTRATION.md §2` digit-for-digit. **No band is
  widened by a single digit.**

Gate NAMES (G-F27R-1 / G-F27R-2) are **retained byte-identical** to R2; the R3 run
is distinguished by its run root and pre-registration commit (as R2 was distinguished
from the parent). Rule 5 applies in full: a non-CONVERGING triple is `NOT A RESULT`;
a CONVERGING triple inside the band is `PASS`, else `GATE FAIL`; no GCI on a
non-monotone triple. The four reported-not-gated channels
(`R-F27-W`, `R-F27-E`, `R-F27-A_z`, `R-F27-A_theta`) are unchanged.

**Fine resolution is NOT reduced:** cell counts 3,840 / 30,720 / 245,760 and dt
halving are byte-identical to the parent, preserving r = 2 and the Roache triple.

---

## 3. THE ONE RE-REGISTERED NUMBER — W_REF_MESH (a reported reference, not a band)

The rounded-square interface redistributes the interior cells, so the
volume-weighted **same-stencil reference** W_REF_MESH (the mean of the exact axial
velocity over the mesh's own cells) moves. It is **re-registered in `exact_f27_r3.py`**
(a NEW file; the frozen `exact_f27.py` is never edited), **recomputed from the built
R3 mesh's own 0/C, 0/V**, and **pinned by `build_f27_r3.py` to W_REF_TOL = 1e-9**:

| level | W_REF_MESH (R3, registered) | frozen exact_f27 | Δ | builder pin |
|---|---|---|---|---|
| coarse | `0.6497988002770876` | 0.649820058760990 | −2.1e-05 | diff 0.0 (exact rebuild) |
| medium | `0.6446723400039349` | 0.644677639755022 | −5.3e-06 | diff 0.0 |
| fine | `0.6433889691657636` | 0.643390292465464 | −1.3e-06 | diff ~1e-9 |

The R3 triple is monotone-decreasing (CONVERGING toward the continuum bulk mean
`0.6429610302390971`, |fine − continuum| = 4.3e-4 < 5e-3) — `exact_f27_r3.py
--selftest` passes 9 controls green, including the same-stencil reference control.
W_REF_MESH enters **only** the reported `W_minus_ref` channel; it enters **no** band,
gate, or rule-4/5 verdict.

**A_MESH BAND-PIN (new, defensive).** `build_f27_r3.py` additionally pins the built
mesh's cross-sectional area against the registered A_MESH (the band input, via
`r_eff_of`) to A_MESH_TOL = 1e-9. Built vs registered deltas: coarse 6.1e-13,
medium −1.1e-13, fine 5.4e-13 — all ≪ 1e-9. This proves at build time that **the
mesh the band was registered against is the mesh that runs**; a mesh whose area
(hence band) drifted is refused.

---

## 4. THE INSTRUMENT PAIR — parallel NEW files (rule 6; frozen instruments never edited)

All R3 instruments are **new files**; the frozen `exact_f27.py`, `build_f27.py`,
`build_f27_successor.py`, `grade_f27_successor_r2.py`, `run_f27_successor_r2.sh`,
`foam_io_f27.py`, `proj_f27.py` and `roache_triple.py` are **never edited**. The
shared readers/gate/projector (`foam_io_f27`, `roache_triple`, `proj_f27`) are reused
UNCHANGED.

### 4.1 The VERDICT instrument — `grade_f27_r3.py` (check-1 reads this AS A DIFF)

`cases/F27_WOMERSLEY_PIPE/einf_topology_successor/grade_f27_r3.py`
— git blob `01acbec95f5d161c7fbb7694ebeedab1f0c4bd13`, sha256
`dd44abb510937756b5a3376ea604db0a4a4617ae106dddacf43accb54c8b6bde` (disk blob at
draft; the supervisor pins the committed blob at freeze).

**Diff vs the frozen R2 grader `grade_f27_successor_r2.py` — FOUR NON-MEASUREMENT
lines, and NOTHING else:**

1. **module docstring note** (the R3 note; prose only).
2. `import exact_f27 as EX` → `import exact_f27_r3 as EX` — the R3 model (new
   W_REF_MESH; bands byte-identical, §2). Redirects only the reported `W_minus_ref`
   reference; the reference the ERROR is measured against, `u_exact(r,t)`, is
   byte-identical.
3. `--root` argparse default `…F27_NUMERICS_SUCCESSOR_R2_runs` →
   `…F27_NUMERICS_SUCCESSOR_R3_runs` (the run root the frozen path grades by default;
   the §2d.1-class repair already landed in R2, so R3 defaults correctly).
4. the **L-332 zero-assert census** file list names the R3 instrument files
   (`exact_f27_r3.py`, `build_f27_r3.py`) instead of the R2 ones — a census over the
   files THIS grader depends on, not a verdict change.

**NOT changed (byte-identical to the R2 grader):** every reader (decomposed, never
reconstructed), both gated quantities `e2_of` / `einf_of`, the two-sided planted-zero
control (rule 3 — plant by index into copies of the real processor files, read back
through the REAL reader, refuse if the reader is blind), the rule-4 strict-completion
+ age guard, the rule-5 Roache gating via the single AST-censused `RT.grade_ladder`
call, every exit-2 refusal, the fixed verdict vocabulary, the named external planted
control, `BAND_FACTOR`, both bands, and `CAP_CORE_MIN = 625.0` (retained). **The
mesh-topology change does NOT change how Einf is measured** — `einf_of` already takes
the max over EVERY cell of |u_z − u_exact(r)|, the correct instrument on any
D4-symmetric butterfly topology (the rounded square is 4-fold symmetric, so
`rot90_permutation` still holds).

**Checks (no solver):** `grade_f27_r3.py --selftest` → **rc 0, 16 controls green**
(both gated quantities shown able to take a passing AND a failing value through the
real reader on the pinned decomposed write format; each of four planted defects seen
by its own channel and no other; periodicity and both uniformity limbs driven both
ways; 0 assert nodes across 5 files; exactly one `grade_ladder` call node);
`python3 -O grade_f27_r3.py --selftest` → **rc 2** (refusal armed).

### 4.2 The re-registered model — `exact_f27_r3.py` (check-1 reads this AS A DIFF)

`cases/F27_WOMERSLEY_PIPE/exact_f27_r3.py`
— git blob `d5a834cc7edc8ccff4be3315ec5624aa65350707`, sha256
`28adf548590cb04fe59aba96314d070927b0ba5d6eb3f05ecaed60cfcb46c9f6`.

**Diff vs the frozen `exact_f27.py` — the three W_REF_MESH literals + a banner note,
and NOTHING else.** `u_exact`, `discrete_solution`, `predictions()`, `A_MESH`,
`BAND_FACTOR`, `MODEL_NR`, `STEPS`, `CORE_FRAC` and every control are byte-identical
→ both bands byte-identical (§2). `--selftest` rc 0 (9 controls green); `-O` rc 2.

### 4.3 The build + launch instruments (config-only diffs)

- **`build_f27_r3.py`** — git blob `72298744f42aa98976ee4026de90b078b36b865e`, sha256
  `7351d70496e08790abbf281f5eea168a6c18a27ae1a43a6169641b2aeb03a348`. Diff vs
  `build_f27_successor.py`: (a) imports `exact_f27_r3`; (b) reads
  `blockMeshDict.template` from the R3 `system/` (the fix) instead of the frozen
  parent case; (c) ADDS the A_MESH band-pin (§3); (d) header. Every mesh gate, the
  (1 1 1) read-back, the W_REF pin, the age-guard-preserving `0/U`-written-last order
  and every refusal are byte-identical. Built all three levels end-to-end (§1.3).
- **`run_f27_r3.sh`** — git blob `24cfee11b880324df6aac8519123cc7f8d7cc48d`, sha256
  `91c3d8239aca14edc243b9084454d81d681c0ca4d020b60ff5c24c37a3955d96`. Diff vs
  `run_f27_successor_r2.sh`: config pointers only — `EXACT`→exact_f27_r3, `BUILD`→
  build_f27_r3, `GRADER`/`GRADER_REL`→grade_f27_r3, `RUN_ROOT`→R3, `HERE`→the R3 dir,
  `blockMeshDict.template` preflight path→R3 `system/`, `ME` `--detach` self-path→
  run_f27_r3.sh, STATUS-note script names, and header. **No logic line changed**
  (cost accounting, `proj_f27.py` projection, the cap-consistency check, the run-root
  guard, `refuse_if_answered`, the rc-inside-wrapper, the halt logic and the rule-2
  blob-hash block are byte-identical). `CAP_CORE_MIN = 625` (unchanged). `bash -n`
  clean; `--preflight` resolves all 16 paths, greens all R3 instruments, CAP agrees
  625, and then **correctly refuses at the rule-2 blob-hash** because the grader is
  not yet committed — the launch is gated on the supervisor's freeze.
- **`system/blockMeshDict.template`** (the mesh fix) — git blob
  `d45e11fe46398bf6d17bf3490ef4d95d2661bcf6`, sha256
  `5dd1cf77c01942b76c508137a7552a3ec69f469e218f16e3d111a0b999ff9c1c`.
- **`system/fvSchemes`**, **`system/fvSolution`** — sha256
  `59b77114798bad38ccfd5c9ebedcf8d69b0765b236e96472f13872c91a4fe81f` /
  `fea071de85b6dfc8257c88d5910cd30c8ec53078a7dd558beba6343ca72fa32f`, **byte-identical
  to the R2 successor numerics** (same sha256 — the numerics are unchanged; only the
  mesh changed).

These blobs/shas are what the supervisor pins at the R3 freeze commit. The supervisor
takes check-1 on the grader and model diffs and check-4 on gate/lever/root/commit;
this lane neither authorises nor launches.

---

## 5. THE COST — costed per rule 12

**Anchor: the R2 MEASURED actual, for the IDENTICAL discretisation.** R3 has
byte-identical cell counts (3,840 / 30,720 / 245,760), byte-identical dt/steps and
byte-identical numerics to R2. R2's measured actual (from
`F27_NUMERICS_SUCCESSOR_R2_RESULTS.md §3`, ClockTime × 4 ranks ÷ 60) is the best
available point estimate.

| level | R2 actual (core-min) | R3 point estimate (core-min) |
|---|---|---|
| coarse | 0.667 | 0.667 |
| medium | 13.867 | 13.867 |
| fine | 403.133 | 403.133 |
| **total** | **417.667** | **417.667 (point estimate)** |

The R3 mesh is **better conditioned** (max non-orthogonality 27.3° vs 40.4° at fine),
so the `nNonOrthogonalCorrectors 3` loop and the pressure Poisson solve are expected
to cost **≤ R2**, not more. No discount is banked into the point estimate; the
improved conditioning is one-sided insurance.

**Registered HARD CAP = 625 core-min** (RETAINED byte-identical from the frozen R2
cap). Basis: R2 **completed this exact discretisation under 625** at 417.667 core-min
— a **proven-sufficient** ceiling — and the R3 mesh is better conditioned. Headroom
above the point estimate = (625 − 417.667)/417.667 = **49.6 %**, ample to absorb any
corrector-count change from the topology reshape. An overrun of **625 STOPS the run**
(rule 12); the cap is **not** raised in flight. Mesh generation (blockMesh/checkMesh/
postProcess, a few serial seconds per level) is negligible and, as in R2, outside the
solver-ClockTime cost accounting.

**Dollars — DERIVED, NOT MEASURED** (the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md §5; c7a.4xlarge at $0.0513/core-h, reported-by-owner):**
- point estimate 417.667 core-min = 6.9611 core-h × $0.0513 = **$0.3571 (derived)**
- hard cap 625 core-min = 10.4167 core-h × $0.0513 = **$0.5344 (derived)**

Both under the $25 standing pre-authorisation (rule 12). A calibration row
(`docs/COST_CALIBRATION.md`, rule-12 estimate-vs-actual) is **owed at completion**;
its input is already known — R2 came in at actual/projected = 0.771 (over-projection).

---

## 6. WHAT THE SUPERVISOR MUST RULE ON (check-4 / check-1)

- **check-1 (measurement scripts, non-delegable):** the `grade_f27_r3.py` four-line
  diff (§4.1) and the `exact_f27_r3.py` W_REF_MESH diff (§4.2), read at source as
  diffs. Both are asserted measurement-logic-invariant; the supervisor confirms.
- **check-4 (gate/lever/root/commit, non-delegable):** (i) the bands are byte-
  identical (§2) — no widening; (ii) the lever is the mesh-topology fix (§1), with the
  scheme-junction fallback documented and not chosen; (iii) the **one flagged open
  judgment** is the exact bulge radius rm — area-equivalent circle 0.3989 is
  principled and band-invariant, but the supervisor may prefer a different principled
  rm (the band does not move either way, §2/§4); (iv) the R3 run root
  `verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs` is **confirmed ABSENT** on disk
  (rule-2 absence condition; the driver's run-root guard passes); (v) the grading path
  is pinned at the freeze commit (rule 2) and the driver hashes the grader on disk
  against the committed blob before running.

**Run root:** `verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs` — **ABSENT** at
draft (rule-2 absence condition holds).

---

## 7. WHAT THIS RE-REGISTRATION DOES AND DOES NOT DO

- **Does:** change ONE physical thing — the core/ring interface topology to a
  rounded square — to resolve the D4 corner mode; register the moved W_REF_MESH and
  pin it and A_MESH from the built mesh; declare a fresh absent R3 run root; reuse the
  verdict logic, both gates, thresholds and bands byte-identically; retain the 625 cap.
- **Does not:** change any gate, threshold, band, `BAND_FACTOR`, reference (the exact
  Womersley solution), ladder, refinement ratio, the successor numerics
  (`fvSchemes`/`fvSolution`), decomposition, or any reported-not-gated channel; reduce
  fine resolution; edit any frozen file; authorise, freeze or launch anything.

**Nothing is sent, filed, uploaded, registered or posted (rule 7). Draft handed to the
cfd supervisor for check-1 (grader + model diffs) and check-4 (gate/lever/root/commit).
Banner stays NOT FROZEN until then.**
