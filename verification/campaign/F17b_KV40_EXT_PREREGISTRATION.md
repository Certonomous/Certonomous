# F17b — PRE-REGISTRATION: Kovasznay flow, LADDER EXTENSION 192×128 / 384×256 / 768×512

**Team:** cfd. **Case id:** `F17b_KV40_EXT`. **Written before any compute. ZERO
CORE-MINUTES SPENT in the case tree or any run root.** **Status at freeze: ARMED —
never run.** Frozen by the commit that carries this file. After first compute the
gates, thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them. Decided and recorded **`[lab-attributed]`** on the
cfd supervisor's dispatch of 2026-08-26 (F17 completed the same day at 1.2 core-min;
the ladder is extended by three levels on the byte-identical case definition).

---

## 1. LINEAGE — WHAT IS INHERITED BYTE-FOR-BYTE, AND WHAT IS NOT

**Parent:** `verification/campaign/F17_KV40_PREREGISTRATION.md` frozen at
`4ad083fbd76d9e75bdf33963e5bfba787291e51d` (AMENDMENT 1 included); case
`cases/F17_kovasznay/`; graded PASS/PASS on 2026-08-26 at 1.2 core-min
(`verification/runs/F17_runs/GRADE_F17.out`: E2 triple CONVERGING, observed order
2.099; u(probe) triple CONVERGING, observed order 2.070).

**This case:** `cases/F17b_kovasznay_ext/`, a copy of the F17 scripts with the
minimum diff (§10 lists every changed line). Measured in the writing invocation:

| item | F17 → F17b |
|---|---|
| `case/` (blockMeshDict.template, controlDict, fvSchemes, fvSolution, transportProperties, turbulenceProperties, 0/U.template, 0/p) | **`diff -r` empty — byte-identical** |
| `build_f17.py`, `foam_io_f17.py` | **`cmp` identical — byte-identical** |
| gate blocks of `grade_f17.py` (`BAND_FACTOR`, `P_RES_TOL`, `U_RES_TOL`, `CLASS_C`, `GATES`, `DIM`, `VERDICTS`, `PHYSICS_CRITICAL`, `INFRASTRUCTURE`, `bands()`, `class_c()`, `iterative_state()`, `completion()`, `grade_one()`, `plant_control_e2()`, `plant_control_u_probe()`, `e2_from_files()`, `u_probe_from_files()`, `cost_claim()`) | **AST-extracted and compared: the diff is EMPTY** |
| exact solution, symbolic-substitution controls, boundary-datum rule, stencil model `discrete_error()` | unchanged |
| ladder | 48×32 / 96×64 / 192×128 → **192×128 / 384×256 / 768×512** (F17's fine is F17b's coarse) |
| cap | 40 → **150 core-min** |
| run root | `F17_runs` → **`verification/runs/F17b_runs`** |
| how the model reaches the fine level | solved at all three grids → **solved at 96×64 and 192×128, extrapolated to 384×256 and 768×512** (§5) |
| gate DEMONSTRATION (§7) | synthetic fine file from the solved fine grid → synthetic file **at 768×512** carrying the solved 192×128 error field prolongated and scaled (§7) |

The script file names are kept (`run_f17.sh`, `grade_f17.py`, …) so the diff is
the smallest it can be; the directory name carries the case identity.

## 2. THE CASE — unchanged from F17 §2

Kovasznay flow, Re = 40, ν = 0.025, λ = −0.963740544195769; domain x ∈ [−0.5, 1],
y ∈ [−0.5, 0.5] cyclic; inlet/outlet `fixedValue` = face-averaged exact velocity,
`fixedFluxPressure`; `simpleFoam`, laminar, `steadyState`, Gauss linear, orthogonal;
U 0.7 / p 0.3; **no `residualControl`**, fixed 4000 iterations, checkpoints every
100. Every dictionary is the byte-identical F17 file (§1).

**Mesh admissibility (MESH_STANDARD §3, §8.1).** The coarse level (192×128) was
**BUILT AND `checkMesh`'d** on a scratch copy by `build_f17.py` in the writing
invocation: 24,576 cells, max non-orthogonality **0°** (gate 70°), max skewness
1.42e−14 (gate 4), `Mesh OK`; identical to F17's fine `MESH_LINE.txt`. The builder
enforces both gates at every level.

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled at registration; not a result; counts toward no challenge column; not
filmed. Its purpose is the asymptotic range: F17 established p ≈ 2 over h = 1/32 →
1/128; this extension asks whether it holds to h = 1/512 at 16× the cells.

## 3. THE REFERENCE IS NOT A PAPER — unchanged from F17 §3

`exact_f17.py --selftest` (this copy, run in the writing invocation, rc 0): the
closed form substituted symbolically into the steady incompressible Navier–Stokes
equations gives identically zero continuity and momentum residuals; λ planted at
1.1× gives a non-zero residual (planted control); numeric λ agrees with the
symbolic one to 1e−12.

## 4. THE LADDER — THREE LEVELS (§9.1)

Square cells, uniform, h refines by exactly 2 in both directions (control refuses
otherwise). `dim = 2`, r = 2.000 from cell counts.

| level | Nx × Ny | cells | h | E2 predicted (§5) | u(probe) error predicted (§5) | model row |
|---|---|---|---|---|---|---|
| coarse | 192 × 128 | 24,576 | 1/128 | 1.106949e−04 | −5.708149e−05 | **solved** (= F17's fine row, byte-identical numbers) |
| medium | 384 × 256 | 98,304 | 1/256 | 2.763616e−05 | −1.425047e−05 | extrapolated, orders 2.0020 / 2.0020 |
| fine | 768 × 512 | 393,216 | 1/512 | 6.899661e−06 | −3.557649e−06 | extrapolated, orders 2.0020 / 2.0020 |

**Why the model is extrapolated rather than solved at the two new levels — measured,
not assumed.** `discrete_error()` assembles and factorises the 3N+1 sparse system
with `scipy.sparse.linalg.spsolve` (SuperLU). Measured on this box in the writing
invocation: 192×128 → **29.5 s, 2.85 GB RSS**; 384×256 → **254.7 s, 14.9 GB RSS**;
768×512 would exceed the box's 30 GB and was not attempted. The grader solves the
model at every entry (selftest, launcher preflight, grade), so the 384×256 solve
would cost 15 GB three times per launch on a shared box. The model is therefore
solved on F17's own 96×64 and 192×128 grids (`MODEL_GRIDS`) and extrapolated with
its own observed order between them (E2: 2.0020; probe: 2.0020; a control refuses
outside [1.7, 2.3]). **Cross-check, solved once, not part of the instrument:** the
384×256 solve above returned E2_pred = **2.766730e−05**, probe_err = −1.426764e−05;
the extrapolated row gives 2.763616e−05 / −1.425047e−05 — **0.11 % / 0.12 %
apart**, so the extrapolation reproduces the solved model to a tenth of a percent.

**DECOMPOSITION SEED (required field): `none`.** Every level serial on 1 rank;
`decomposePar` not invoked; no partition, no RNG.

## 5. THE GATES AND THEIR BANDS — THE DERIVATION IS F17's, BYTE-FOR-BYTE

`BAND_FACTOR = 3`, `bands()` and both gate definitions are the byte-identical F17
code (§1). Only the fine-level prediction the code reads changes, because the fine
level is now 768×512. **The numeric bands therefore differ from F17's numbers, and
this is stated rather than glossed:** F17's band for E2_fine, [3.69e−05, 3.32e−04],
was derived at h = 1/128; at h = 1/512 the model predicts an error 16.04× smaller,
and keeping F17's *numbers* would register a gate the extension could only fail by
being more accurate. The gate is the derivation, and the derivation is unchanged.

**G-F17-1 — normalised L2 velocity error at the last checkpoint (4000)**
Prediction at h_fine = 1/512: **6.899661e−06**.
**Band = [prediction/3, prediction×3] = [2.299887e−06, 2.069898e−05].**

**G-F17-2 — u/U0 at the probe (0.5, 0)**, bilinear between the four surrounding cell
centres. Exact **0.382372819953864**.
**Band = exact ± 3 × 3.557649e−06 = [0.382362147006, 0.382383492902].**

**Registered prediction: both triples `CONVERGING` with observed order p ≈ 2
(model 2.002); fine values inside both bands → PASS.**

### 5.1 A LIMIT OF THE PROBE GATE THAT F17 ABSORBED AND THIS LEVEL DOES NOT — quantified before compute

F17 §5 said of G-F17-2: *"the interpolation error is O(h²) and is absorbed in the
window."* The window is 3 × the model's pointwise error; the bilinear interpolation
of the **exact** field at the probe carries its own O(h²) error which the model does
not predict. Measured in the writing invocation (exact field sampled at cell centres,
interpolated by the grader's own `bilinear()`):

| grid | interpolation error of the exact field at the probe | band half-width (3 × model) | ratio |
|---|---|---|---|
| 192×128 | +1.816425e−04 | 1.712e−04 (F17) | 1.06 |
| 384×256 | +4.541212e−05 | — | — |
| 768×512 | **+1.135312e−05** | **1.067295e−05** | **1.06** |

So at every level the interpolation error alone is 1.06× the half-width; the gate
passes only because the solver's discretisation error at the probe is **negative**
and partly cancels it. F17 measured exactly that: fine value − exact = +6.834e−05 =
interpolation +1.816e−04 plus solver −1.133e−04 (the solver's pointwise error was
2.0× the model's −5.7e−05, inside the factor 3). Registered, before compute:

- **model path:** value − exact = +1.135e−05 − 3.558e−06 = **+7.80e−06 → inside, at
  73 % of the half-width** (the §7 demonstration built at 768×512 returns exactly
  0.382380615 = exact + 7.795e−06);
- **F17-measured-trend path:** +6.834e−05 / 2^(2×2.070) = **+3.9e−06 → inside**;
- **a solver with zero pointwise error** would land at +1.135e−05 → **outside by 6 %**.

**Both live predictions land inside; the gate is registered as F17 wrote it, and
this section exists so a GATE FAIL on G-F17-2 could be read for what it would be**
(a probe-interpolation artefact the parent registration declared absorbed), rather
than discovered after the fact. Changing the gate to include the interpolation term
would change `bands()`, which this extension was dispatched not to do; that choice
is on the supervisor's desk before compute, not this lane's.

## 6. CRITERIA — unchanged from F17 §6, confirmed by running this copy

All F17 criteria hold verbatim (verdict vocabulary; rule 5 through `grade_ladder`
only; Class C all four elements on the graded quantity with window 12 checkpoints;
rule 5 limb 1 census Ux, Uy ≤ 1e−6, p ≤ 1e−5 over iterations 2801–4000; completion
rule 4 with the fixed-count identity and the age guard; L-342 field classes driven
both ways; planted-zero controls through the real parser; guards refuse and never
delete; `--preflight` fires nothing). **Measured in the writing invocation on the
F17b copy:**

| check | result |
|---|---|
| `exact_f17.py --selftest` | rc 0, 5 controls green, 39.6 s, 2.89 GB RSS |
| `python3 -O exact_f17.py --selftest` | **rc 2** (refused at entry) |
| `grade_f17.py --selftest` | rc 0, 10 controls green, 45.5 s, 2.89 GB RSS |
| `python3 -O grade_f17.py --selftest` | **rc 2** |
| `assert` census (AST) over grade / exact / foam_io / build | **0 nodes; planted assert seen** |
| `grade_ladder` call nodes (AST) | **exactly 1** (line 627); grep matcher driven both ways |
| L-342 classes | PHYSICS_CRITICAL / INFRASTRUCTURE declared; control drives both directions (infra deleted → completion unchanged + cost claim refused; rc corrupted / `End` deleted → NOT A RESULT) |
| `set +u` around the bashrc source | inherited from F17 AMENDMENT 1, lines 146–149 of `run_f17.sh` |
| `scripts/check_launcher_can_launch.py --worktree run_f17.sh` (ARM 1 + ARM 3 at `3f29a32e`) | **rc 0**: 0 time-dir globs, 0 bashrc sources under `set -u` |
| `bash -n run_f17.sh` | parses |
| `run_f17.sh --preflight` | **rc 0**; instrument green; cap agrees 150/150; ν and endTime agree; run root reported ABSENT; blockMesh NOT run |

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING AND A PASSING VALUE

Through the real readers, on files in the pinned write format (pinned against real
solver output on this box, `verification/runs/ansys_verification/VMFL019/L1_30/5/U`,
parsed at selftest). **Built at the fine size 768×512** (393,216 cells): the solved
192×128 error field is prolongated piecewise-constant onto the fine grid (E2 is
preserved exactly by the prolongation) and scaled by the model's 192×128 → 768×512
E2 ratio, 0.062330. The probe therefore sees the fine level's own interpolation error
(§5.1), not the solved grid's.

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F17-1 | exact + **1×** scaled model error field | 6.899661e−06 | [2.300e−06, 2.070e−05] | **inside** |
| G-F17-1 | exact + **40×** the same | 2.759864e−04 | same | **outside** |
| G-F17-2 | exact + **1×** the same | 0.382380615 | [0.382362147, 0.382383493] | **inside** |
| G-F17-2 | exact + **40×** the same | 0.382241856 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned against
real output, the *values* are constructed.

## 8. COST — COSTED BEFORE THE RUN, FROM F17's MEASURED CLOCKTIMES

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.**

**Rate basis — MEASURED on the byte-identical case definition, F17,
`verification/runs/F17_runs/{coarse,medium,fine}/log.simpleFoam`, 2026-08-26:**

| F17 level | cells | iterations | ClockTime | ExecutionTime | µs per cell-iteration (ClockTime) |
|---|---|---|---|---|---|
| coarse | 1,536 | 4,000 | 3 s | 3.13 s | 0.488 |
| medium | 6,144 | 4,000 | 11 s | 11.53 s | 0.448 |
| fine | 24,576 | 4,000 | 58 s | 57.41 s | **0.590** |

**Iteration growth.** The SIMPLE count is fixed at 4000 by the case definition, so
no outer-iteration growth enters. The inner GAMG cycle count per pressure solve grew
4 → 5 → 7 (iteration 1) across F17's levels and falls to 0 once converged (F17
reached Ux < 1e−6 at iterations 65 / 130 / 37, non-monotone in h); the measured
medium → fine growth of the per-cell-iteration rate is **+32 %**, taken here as
**+30 % per doubling** on top of the 4× cell count. F17's coarse→medium rate fell
(−8 %), so the +30 % is the pessimistic half of the record.

| F17b level | cells | cell-iterations | rate (µs) | projected serial s | core-min |
|---|---|---|---|---|---|
| coarse (= F17 fine, same grid) | 24,576 | 98.3 M | 0.590 (measured) | 58 | 0.97 |
| medium | 98,304 | 393.2 M | 0.767 | 302 | 5.03 |
| fine | 393,216 | 1,572.9 M | 0.997 | 1,568 | 26.1 |
| **total** | | **2,064 M** | | **1,928** | **32.1** |

**REGISTERED CAP: 150 core-minutes** (4.7× headroom; the width is the admission —
GAMG cycle growth beyond +30 %/doubling is the unknown). **Derived dollars at
$0.0513/core-h: $0.027 estimate, $0.128 at the cap — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation.
**`cost_basis: derived from F17's measured ClockTimes, not measured on these levels.`**

**Memory floor: 3.0 GB** — the grader's own model solve at 192×128 is **2.89 GB RSS
measured**; `simpleFoam` serial at 393k cells is estimated below 1 GB. **Disk:**
40 checkpoints × (U + p + phi) at 393k cells ≈ 1.8 GB for the fine level, ≈ 2.4 GB
for the ladder (277 GB free on `/` in the writing invocation).

**Wall time, stated because it is serial:** ≈ 32 min for the ladder if the estimate
holds; ≈ 2.5 h at the cap.

The cap is checked **incrementally after each level** and **projected before each
level** from the launcher's own box probe (`PROJ_SERIAL_S` = 58 / 302 / 1568 s, the
table above); a crossing **HALTS at exit 3**, unlaunched levels stay `PENDING`, the
cap is never raised. Launcher and grader carry the same cap and refuse to start if
they disagree (measured: "CAP AGREES … 150").

**Scratch smoke arm, reported:** one real `simpleFoam` iteration on a scratch copy
of the coarse level (192×128) built by `build_f17.py` into the scratchpad, never the
case tree: rc 0, `Time = 1`, `End` written, **`Solving for Ux` initial residual
1.05795770282e−03 (non-zero: the fields move)**, p GAMG 7 cycles, ExecutionTime
0.16 s, ClockTime 0 s; `1/U` written with 24,576 entries — **≈ 0.01 core-min including
blockMesh/checkMesh/postProcess**; not retained, not a measured history, not a result.

**Convergence risk, registered:** the census window is iterations 2801–4000. F17
converged (Ux < 1e−6) by iteration 130 at worst; if 768×512 has not converged inside
the window the level is **NOT A RESULT** by rule 5 limb 1 and stays so.

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F17b_runs` → **ABSENT** (and
`--preflight` printed the same reading). `find cases/F17b_kovasznay_ext -name RC.txt
-o -name 'log.*'` → **0** files; the only numeric directory under the case tree is the
tracked template `case/0`. `ls -d verification/runs/F17b*` → 0.

## 10. EVERY CHANGED LINE — the diff the supervisor reads (check 1)

`diff -u cases/F17_kovasznay/<f> cases/F17b_kovasznay_ext/<f>`: `exact_f17.py` 23
removed / 48 added; `grade_f17.py` 9 removed / 18 added; `run_f17.sh` 11 removed /
14 added; `build_f17.py`, `foam_io_f17.py`, `case/**` **0**. sha256 of the F17b
files at this freeze: `exact_f17.py` aec9f7f0…c6730, `grade_f17.py` ab30b337…6524,
`run_f17.sh` cda71739…982c, `build_f17.py` cd129a55…d565, `foam_io_f17.py`
b0609f8e…01be. The full unified diffs follow, verbatim.


```diff
# run_f17.sh
@@ -1,5 +1,6 @@
-# F17 -- LAUNCHER for Kovasznay flow (simpleFoam, steady, Re = 40, three-level ladder).
+# F17b -- LAUNCHER for Kovasznay flow, LADDER EXTENSION 192x128 / 384x256 / 768x512
+# (simpleFoam, steady, Re = 40; byte-identical case definition to F17).
@@ -20,25 +21,27 @@
-ROOT="/home/ubuntu/Certonomous/cases/F17_kovasznay"
+ROOT="/home/ubuntu/Certonomous/cases/F17b_kovasznay_ext"
-RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F17_runs"
+RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F17b_runs"
-CAP_CORE_MIN=40             # must equal grade_f17.py::CAP_CORE_MIN
+CAP_CORE_MIN=150            # must equal grade_f17.py::CAP_CORE_MIN
-LEVELS=("coarse 48 32 1" "medium 96 64 1" "fine 192 128 1")
-# projected SERIAL seconds per level at 3.55 us/cell/iteration -- a rate read
-# from one lab record of a DIFFERENT case (FPE_DIAG BL1: 3520 cells, 2000
-# iterations, ClockTime 25 s, serial), applied here; DERIVED, NOT MEASURED on
-# this case.  Used ONLY by the pre-level projected-cap check.
-declare -A PROJ_SERIAL_S=( [coarse]=22 [medium]=88 [fine]=350 )
+LEVELS=("coarse 192 128 1" "medium 384 256 1" "fine 768 512 1")
+# projected SERIAL seconds per level from F17's MEASURED ClockTimes on the SAME
+# case definition (verification/runs/F17_runs/{coarse,medium,fine}/log.simpleFoam:
+# 3 / 11 / 58 s for 1536 / 6144 / 24576 cells x 4000 iterations = 0.49 / 0.45 /
+# 0.59 us per cell-iteration), scaled by cells and by the measured +30 % per
+# doubling (GAMG cycle growth); DERIVED from a measurement of the parent case,
+# NOT MEASURED on these levels.  Used ONLY by the pre-level projected-cap check.
+declare -A PROJ_SERIAL_S=( [coarse]=58 [medium]=302 [fine]=1568 )
@@ -98,7 +101,7 @@
-sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F17_kovasznay")
+sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F17b_kovasznay_ext")
```

```diff
# grade_f17.py
@@ -68,7 +68,7 @@
-CAP_CORE_MIN = 40.0                     # ClockTime s * ranks / 60, summed over levels
+CAP_CORE_MIN = 150.0                    # ClockTime s * ranks / 60, summed over levels (F17b)
@@ -533,14 +533,23 @@
-    """ZERO COMPUTE."""
-    m = EX.model("fine")
+    """ZERO COMPUTE.  F17b: the finest SOLVED grid's error field, prolongated
+    (piecewise constant) onto the FINE grid and scaled by the model's solved->fine
+    E2 ratio, stands in for the extrapolated fine field -- built AT the fine size
+    so the probe's own bilinear interpolation error is the fine level's, not the
+    solved grid's (which is 16x larger and would fail the band by itself)."""
+    m = EX.solved(*EX.MODEL_GRIDS[-1])
+    k = nx // m["nx"]
+    if k * m["nx"] != nx or k * m["ny"] != ny:
+        refuse("fine grid %dx%d is not an integer refinement of the solved %dx%d" % (nx, ny, m["nx"], m["ny"]))
+    ratio = dict((r["name"], r) for r in EX.predictions())["fine"]["E2_pred"] / m["E2_pred"]
+    eu, ev = np.kron(m["eu"], np.ones((k, k))), np.kron(m["ev"], np.ones((k, k)))
-            up, xc, yc = synth_case(tmp, nx, ny, scale * m["eu"], scale * m["ev"])
+            up, xc, yc = synth_case(tmp, nx, ny, scale * ratio * eu, scale * ratio * ev)
@@ -724,7 +733,7 @@
-    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F17_runs"))
+    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F17b_runs"))
@@ -757,16 +766,16 @@
-    out = a.out or os.path.join(a.root, "F17_GRADED.json")
+    out = a.out or os.path.join(a.root, "F17b_GRADED.json")
-        json.dump(dict(rung="F17-KV40", prereg_commit=a.prereg_commit,
-                       prereg="verification/campaign/F17_KV40_PREREGISTRATION.md",
+        json.dump(dict(rung="F17b-KV40-EXT", prereg_commit=a.prereg_commit,
+                       prereg="verification/campaign/F17b_KV40_EXT_PREREGISTRATION.md",
-    print("F17 -- KOVASZNAY FLOW -- TALLY")
+    print("F17b -- KOVASZNAY FLOW, LADDER EXTENSION -- TALLY")
```

```diff
# exact_f17.py
@@ -80,7 +80,12 @@
-LEVELS = (("coarse", 48, 32), ("medium", 96, 64), ("fine", 192, 128))
+LEVELS = (("coarse", 192, 128), ("medium", 384, 256), ("fine", 768, 512))   # F17b: F17's fine is this coarse
+# F17b EXTENSION: the linear model is SOLVED on these grids (F17's own medium and
+# fine; 192x128 = 29.5 s, 2.85 GB RSS measured) and EXTRAPOLATED to the two finer
+# F17b levels with the model's own observed order between them.  384x256 measured
+# 255 s / 14.9 GB RSS and 768x512 would exceed this 30 GB box, so it is not solved.
+MODEL_GRIDS = ((96, 64), (192, 128))
@@ -347,28 +352,52 @@
+def solved(nx, ny):
+    """The full model (error fields included) SOLVED on one grid, cached per process."""
+    if (nx, ny) not in MODEL_GRIDS:
+        refuse("grid %dx%d is not solved by the model; it is extrapolated" % (nx, ny))
+    if (nx, ny) not in _CACHE:
+        _CACHE[(nx, ny)] = discrete_error(nx, ny)
+    return _CACHE[(nx, ny)]
+
+
-    """The full model (error fields included) at one level, cached per process."""
-    if name not in _CACHE:
-        lv = dict((n, (nx, ny)) for n, nx, ny in LEVELS)
-        if name not in lv:
-            refuse("unknown level %r" % name)
-        _CACHE[name] = discrete_error(*lv[name])
-    return _CACHE[name]
+    """The full model at one LADDER level -- only where that level's grid is solved."""
+    lv = dict((n, (nx, ny)) for n, nx, ny in LEVELS)
+    if name not in lv:
+        refuse("unknown level %r" % name)
+    return solved(*lv[name])
+
+
+def model_orders():
+    a, b = solved(*MODEL_GRIDS[0]), solved(*MODEL_GRIDS[1])
+    r = math.log(a["h"] / b["h"])
+    return (math.log(a["E2_pred"] / b["E2_pred"]) / r,
+            math.log(abs(a["probe_err_pred"]) / abs(b["probe_err_pred"])) / r)
-    """The model at every level, cached per process."""
+    """Solved where the ladder grid is a MODEL_GRID; otherwise extrapolated from
+    the finest solved grid with the model's own orders (E2 and probe separately)."""
+        ref = solved(*MODEL_GRIDS[-1])
+        p_e2, p_pr = model_orders()
-            m = model(name)
-            tab.append(dict(name=name, nx=nx, ny=ny, cells=nx * ny, h=m["h"],
-                            E2_pred=m["E2_pred"], probe_err_pred=m["probe_err_pred"],
+            if (nx, ny) in MODEL_GRIDS:
+                m, src = solved(nx, ny), "solved"
+                e2, pe = m["E2_pred"], m["probe_err_pred"]
+            else:
+                m, src = ref, ("extrapolated from %dx%d with model orders %.4f (E2), %.4f (probe)"
+                               % (ref["nx"], ref["ny"], p_e2, p_pr))
+                e2 = ref["E2_pred"] * (h_of(nx) / ref["h"]) ** p_e2
+                pe = ref["probe_err_pred"] * (h_of(nx) / ref["h"]) ** p_pr
+            tab.append(dict(name=name, nx=nx, ny=ny, cells=nx * ny, h=h_of(nx),
+                            E2_pred=e2, probe_err_pred=pe,
-                            solve_residual_max=m["solve_residual_max"]))
+                            solve_residual_max=m["solve_residual_max"], source=src))
@@ -465,18 +494,18 @@
-    for row in tab:
+    for nx, ny in MODEL_GRIDS:
+        row = solved(nx, ny)
-            refuse("linear model at level %s not solved: max residual %.3e"
-                   % (row["name"], row["solve_residual_max"]))
+            refuse("linear model on grid %dx%d not solved: max residual %.3e"
+                   % (nx, ny, row["solve_residual_max"]))
-                   "truncation residual on the exact field at level %s" % row["name"])
-    p12 = math.log(tab[0]["E2_pred"] / tab[1]["E2_pred"]) / math.log(2.0)
-    p23 = math.log(tab[1]["E2_pred"] / tab[2]["E2_pred"]) / math.log(2.0)
+                   "truncation residual on the exact field on grid %dx%d" % (nx, ny))
+    p12, p23 = model_orders()          # E2 order and probe order between the SOLVED grids
-        refuse("the model's predicted E2 does not scale as h^2 across the ladder: "
-               "model orders %.3f, %.3f" % (p12, p23))
+        refuse("the model's predicted errors do not scale as h^2 between the solved grids: "
+               "model orders %.3f (E2), %.3f (probe)" % (p12, p23))
@@ -534,9 +563,9 @@
-        print("%-7s %dx%d h=%.6g  E2_pred=%.6e  probe_err_pred=%.6e  |r|=%.3e  solve_res=%.1e"
+        print("%-7s %dx%d h=%.6g  E2_pred=%.6e  probe_err_pred=%.6e  |r|=%.3e  solve_res=%.1e  [%s]"
-                 r["r_momentum_L2"], r["solve_residual_max"]))
+                 r["r_momentum_L2"], r["solve_residual_max"], r["source"]))
```

## 11. NEVER RUN — THE EVIDENCE

- Tracked paths enumerated with `git ls-tree -r HEAD --name-only`: **14,427** at the
  writing invocation; matches for `F17b|kovasznay_ext`: **0** (planted control:
  `cases/F17_kovasznay/run_f17.sh` is in the enumeration, 1 hit).
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (534 entries) **0**;
  `/home/ubuntu/closure-data` (22) **0**; `/home/ubuntu/closure-challenge-benchmark`
  (7) **0**. `verification/runs/` holds no `F17b*` directory.

## 12. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F17b_kovasznay_ext/run_f17.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F17b_kovasznay_ext/grade_f17.py --prereg-commit=<sha>`. The queue
entry `cases/F17b_kovasznay_ext/queue_entry_F17b_KV40_EXT.json` is **HELD in the
case directory** until the supervisor's check 1/4; the supervisor, not this lane,
drops it into `verification/queue/cfd/`.

## 13. WHAT IS NOT REGISTERED HERE

- No re-grade of F17; no claim about p (not graded); no turbulence claim.
- No amendment to any standard, charter or to F17's frozen record.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).

---

## AMENDMENT 1 — 2026-08-26T20:48:05Z (pre-compute)

**Version 1.1. Lines whose number changed above this section: 0** (this block is
appended at the foot; the frozen text at `9b354fad` is untouched — disk blob
`c25c90e21db0da5340cef82888b4316ae4669201` == `HEAD:` blob at the writing
invocation, 443 lines before this block). Decided and recorded `[lab-attributed]`
on the cfd supervisor's ruling of 2026-08-26 on the §5.1 disclosure.

**Condition (rule 2 §2b): before first compute.** Checked in the writing
invocation, `date -u` = 2026-08-26T20:48:05Z:

- `ls -d verification/runs/F17b_runs` → **`ls: cannot access
  'verification/runs/F17b_runs': No such file or directory`** (the run root is
  ABSENT; the launcher has never created it).
- `find cases/F17b_kovasznay_ext -name RC.txt -o -name 'log.*' | wc -l` → **0**.
- `verification/queue/cfd/` holds no `F17b*` entry and `launched/` holds none;
  the entry was HELD in the case directory (§12) and never dropped.
- Core-minutes spent on this case: **0**.

**What changes — G-F17-2's REFERENCE only.** §5.1 disclosed, before compute, that
the grader's bilinear interpolation of the **exact** field at the probe (0.5, 0)
carries its own O(h²) error of **+1.135312e−05** at 768×512 — **1.06×** the band
half-width 1.067295e−05 — so a solver with zero pointwise error would land
**outside** the band by 6 %, and the registered PASS prediction rested on the
solver's negative discretisation error partly cancelling it. Ruling: the
reference moves

| | old (`9b354fad`) | new (this amendment) |
|---|---|---|
| reference | pointwise exact u(0.5, 0)/U0 = **0.382372819953864** | exact field sampled at the fine level's own cell centres, interpolated by the grader's own `bilinear()` — the same stencil the solved field goes through = **0.382384173078692** (= pointwise + 1.1353124828e−05, the §5.1 figure) |
| band half-width | 3 × 3.557649e−06 = 1.067295e−05 | **1.067295e−05 — UNCHANGED** |
| band | [0.382362147006, 0.382383492902] | **[0.382373500131, 0.382394846027]** (shifted by the stencil error; same width) |
| threshold logic | `band_verdict` in `grade_ladder`, one-way | **UNCHANGED** |
| `BAND_FACTOR`, `bands()` E2 branch, G-F17-1 | | **UNCHANGED** |

The correction is one-directional: it removes a known instrument artefact from
the reference; it does not widen the band, and a solver reading the old band's
"PASS by cancellation" path now has to be within ±3× the model's pointwise error
of the interpolated exact value.

**How `grade_f17.py` changes — 55 changed lines, the diff read-able below.**
`bands()` calls the new `u_probe_reference(nx, ny)` for G-F17-2 instead of
`EX.u_probe_exact()`; the `principle` string prints both the interpolated and
the pointwise values; one new driven control
`control_probe_reference_same_stencil()` is appended to the control list.
**Driven in the writing invocation** (`grade_f17.py --selftest`, rc 0, 11
controls green; `python3 -O` → rc 2): the exact field written in the pinned
format and read through the real `u_probe_from_files()` returns
`zero_error_readback` = **0.0** against the reference; a planted Ux offset of
`RT.PLANT` = 1.234e−03 in that file is read back as **1.234000000000013e−03**
(`planted_readback`); `stencil_error` = **1.1353124828472616e−05**. The §7
demonstration rows are unchanged in value (G-F17-2: 0.3823806152 inside,
0.3822418565 outside) and both sides still hold against the new band. Registered
prediction under the new reference: model path value − reference = −3.558e−06
(33 % of the half-width, inside); F17-trend path −7.5e−06 (inside); a zero-error
solver **0** (inside — the case §5.1 said would fail). sha256 of `grade_f17.py`
after this amendment:
`5b9a77ee4c718054babb6898b0a64c410803b4bd51dca72b9815da3e516682e3`.

```diff
--- a/cases/F17b_kovasznay_ext/grade_f17.py (9b354fad)
+++ b/cases/F17b_kovasznay_ext/grade_f17.py (AMENDMENT 1)
@@ -484,14 +484,59 @@
 
 
 # ---------------------------------------------------------------------------
+# AMENDMENT 1, 2026-08-26, PRE-FIRST-COMPUTE (run root F17b_runs ABSENT when
+# written).  G-F17-2's REFERENCE is the exact field sampled at the fine level's
+# own cell centres and interpolated by the SAME bilinear() stencil the solved
+# field goes through -- so the stencil's own O(h^2) error (prereg section 5.1:
+# 1.06x the band half-width, enough to fail a zero-error solver) cancels in
+# value - reference.  Band WIDTH, threshold logic and one-way gate UNCHANGED.
+# ---------------------------------------------------------------------------
+def u_probe_reference(nx, ny):
+    h = EX.h_of(nx)
+    xg = EX.X0 + (np.arange(nx) + 0.5) * h
+    yg = EX.Y0 + (np.arange(ny) + 0.5) * h
+    X, Y = np.meshgrid(xg, yg)
+    return float(EX.bilinear(xg, yg, EX.u_exact(X, Y), EX.PROBE[0], EX.PROBE[1]) / EX.U0)
+
+
+def control_probe_reference_same_stencil():
+    """Driven: the exact field written in the real format and read through the
+    real probe reader returns ZERO error against the reference (to round-off);
+    a planted Ux perturbation in that file is read back exactly."""
+    nx, ny = SHAPE["fine"]
+    ref = u_probe_reference(nx, ny)
+    d = RT.PLANT
+    tmp = tempfile.mkdtemp(prefix="f17_ref_")
+    try:
+        z = np.zeros((ny, nx))
+        up, xc, yc = synth_case(tmp, nx, ny, z, z)
+        v0 = u_probe_from_files(up, xc, yc, nx, ny)
+        work = os.path.join(tmp, "U_planted")
+        if FIO.plant_into_vector_file(up, work, 0, d) == 0:
+            refuse("nothing to plant into %s" % up)
+        v1 = u_probe_from_files(work, xc, yc, nx, ny)
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    if abs(v0 - ref) > 1e-12:
+        refuse("AMENDMENT 1 CONTROL FAILED: the exact field through the probe reader returned "
+               "%.17g against reference %.17g; a zero-error solver would not read zero" % (v0, ref))
+    if abs((v1 - ref) - d / EX.U0) > 1e-12:
+        refuse("AMENDMENT 1 CONTROL FAILED: a planted Ux offset of %.6e was read back as %.6e"
+               % (d / EX.U0, v1 - ref))
+    return dict(control="PZ-F17-AMEND1_probe_reference_same_stencil_zero_error_and_plant_read_back",
+                reference=ref, pointwise_exact=EX.u_probe_exact(), stencil_error=ref - EX.u_probe_exact(),
+                zero_error_readback=v0 - ref, planted_readback=v1 - ref, plant=d / EX.U0, passed=True)
+
+
+# ---------------------------------------------------------------------------
 # BANDS -- both from ONE declared parameter applied to the model prediction
 # ---------------------------------------------------------------------------
 def bands():
     tab = dict((r["name"], r) for r in EX.predictions())
     fine = tab["fine"]
     e2p = fine["E2_pred"]
-    up = EX.u_probe_exact()
-    tol = BAND_FACTOR * abs(fine["probe_err_pred"])
+    up = u_probe_reference(*SHAPE["fine"])          # AMENDMENT 1: same-stencil reference
+    tol = BAND_FACTOR * abs(fine["probe_err_pred"])  # width UNCHANGED
     return {
         "G-F17-1_E2_velocity_L2": dict(
             band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
@@ -500,9 +545,11 @@
                        "times [1/%g, %g]" % (e2p, fine["h"], BAND_FACTOR, BAND_FACTOR))),
         "G-F17-2_u_at_probe": dict(
             band=(up - tol, up + tol), reference=up, dim=DIM,
-            principle=("exact u(%g, %g)/U0 = %.15f +/- %g x the model's predicted pointwise "
-                       "error there (%.9e) = +/- %.9e" % (EX.PROBE[0], EX.PROBE[1], up, BAND_FACTOR,
-                                                           fine["probe_err_pred"], tol))),
+            principle=("exact field sampled at the fine level's cell centres and interpolated by "
+                       "the grader's own bilinear() at (%g, %g): u/U0 = %.15f (pointwise exact "
+                       "%.15f; AMENDMENT 1) +/- %g x the model's predicted pointwise error there "
+                       "(%.9e) = +/- %.9e" % (EX.PROBE[0], EX.PROBE[1], up, EX.u_probe_exact(),
+                                              BAND_FACTOR, fine["probe_err_pred"], tol))),
     }
 
 
@@ -746,7 +793,7 @@
                 EX.control_model_is_second_order_and_solved(),
                 control_class_c_can_say_no(), control_grade_ladder_is_called(),
                 control_solver_dicts_match(), control_reader_parses_real_solver_output(),
-                control_field_classes_separate()]
+                control_field_classes_separate(), control_probe_reference_same_stencil()]
     bnd = bands()
     demo = demonstrate(bnd)
 
```

**Queue entry:** `cases/F17b_kovasznay_ext/queue_entry_F17b_KV40_EXT.json` is
refreshed in the FOLLOWING commit so that `prereg_commit` and the launch argv's
`--prereg-commit=` cite the sha of the commit carrying this amendment, and gains
`cap_core_min_registered: 150` for the runner's cap watch. Cost, cap (150
core-min), estimate (32.1 core-min), ladder, launcher and every other gate block
are unchanged. Nothing is sent, filed or submitted (rule 7).
