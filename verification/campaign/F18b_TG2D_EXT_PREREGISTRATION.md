# F18b — PRE-REGISTRATION: 2-D Taylor–Green vortex, LADDER EXTENSION 256² / 512² / 1024²

**Team:** cfd. **Case id:** `F18b_TG2D_EXT`. **Written before any compute. ZERO
CORE-MINUTES SPENT in the case tree or any run root.** **Status at freeze: ARMED —
never run.** Frozen by the commit that carries this file. After first compute the
gates, thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them. Decided and recorded **`[lab-attributed]`** on the
cfd supervisor's dispatch of 2026-08-26.

---

## 1. LINEAGE — WHAT IS INHERITED BYTE-FOR-BYTE, AND WHAT IS NOT

**Parent:** `verification/campaign/F18_TG2D_PREREGISTRATION.md` frozen at
`c4f72b277d74ecce19c6f81d651038ab16c338af`; case `cases/F18_taylor_green/`.
The parent was **queued when this extension was dispatched and completed while it
was being written**: `cases/F18_taylor_green/launcher.queue.out` shows all three
levels complete at 4.42 core-min (ClockTime 1 / 18 / 246 s) and
`verification/runs/F18_runs/F18_GRADED.out` reads PASS / PASS. Its files and run
root were read, never touched.

**This case:** `cases/F18b_taylor_green_ext/`, a copy of the F18 scripts with the
minimum diff (§10 lists every changed line). Measured in the writing invocation:

| item | F18 → F18b |
|---|---|
| `case/` (blockMeshDict.template, controlDict.template, fvSchemes, fvSolution, transportProperties, 0/U.template, 0/p.template) | **`diff -r` empty — byte-identical** |
| `build_f18.py`, `foam_io_f18.py` | **`cmp` identical — byte-identical** |
| gate blocks of `grade_f18.py` (`BAND_FACTOR`, `P_SOLVER_TOL`, `END_TIME`, `GATES`, `DIM`, `VERDICTS`, `PHYSICS_CRITICAL`, `INFRASTRUCTURE`, `bands()`, `iterative_state()`, `completion()`, `grade_one()`, `plant_control_e2()`, `plant_control_ke()`, `e2_from_files()`, `ke_from_files()`, `cost_claim()`, `read_U()`, `read_centres()`) | **AST-extracted and compared: the diff is EMPTY** |
| exact solution, symbolic-substitution controls, BDF2 stencil model `discrete_error()` | unchanged |
| ladder | 64² / 128² / 256² → **256² / 512² / 1024²**, Δt 0.02 / 0.01 / 0.005 → **0.005 / 0.0025 / 0.00125** (Co = 0.2 at every level, T = 2 s; F18's fine is F18b's coarse) |
| cap | 30 → **1500 core-min** (§8) |
| run root | `F18_runs` → **`verification/runs/F18b_runs`** |
| how the model reaches the ladder | integrated at F18's coarse and medium, fine extrapolated → **integrated on the same two grids (64²×100, 128²×200), all three F18b levels extrapolated** (§5) |
| gate DEMONSTRATION (§7) | stand-in built at F18's medium size → stand-in built at the finest integrated size, 128² |

Script file names are kept (`run_f18.sh`, `grade_f18.py`, …) so the diff is the
smallest it can be; the directory name carries the case identity.

## 2. THE CASE — unchanged from F18 §2

u = sin x cos y e^{−2νt}, v = −cos x sin y e^{−2νt}, p = (cos 2x + cos 2y)/4 e^{−4νt}
on [0, 2π]² doubly cyclic; ν = 0.1, U0 = 1, T = 2 s; exact u, v, p at t = 0 at the
built mesh's own cell centres; `icoFoam`, `backward`, Gauss linear, orthogonal, PISO
2 correctors, p PCG/DIC tol 1e−9 relTol 0; fields at `endTime` only. Every
dictionary is the byte-identical F18 file (§1).

**Mesh admissibility (MESH_STANDARD §3, §8.1).** The coarse level (256²) was **BUILT
AND `checkMesh`'d** on a scratch copy by `build_f18.py` in the writing invocation:
65,536 cells, max non-orthogonality **0°** (gate 70°), max skewness 2.17e−13 (gate
4), `Mesh OK`; identical to F18's fine `MESH_LINE.txt`.

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled at registration; not a result; counts toward no challenge column; not
filmed. Its purpose is the asymptotic range: F18 measured PASS/PASS but with Roache
observed orders **1.289 (E2) and 0.964 (KE)** against the model's 1.996, because the
64² level is pre-asymptotic (successive error ratios 2.76 → 3.56 for E2, 2.40 → 3.55
for KE, both rising toward 4). This extension asks whether the ratio reaches 4.

## 3. THE REFERENCE IS NOT A PAPER — unchanged from F18 §3

`exact_f18.py --selftest` (this copy, writing invocation, rc 0): the closed form
substituted symbolically into the unsteady incompressible Navier–Stokes equations
gives identically zero continuity and momentum residuals; the decay rate planted at
2.3ν gives a non-zero residual (planted control).

## 4. THE LADDER — THREE LEVELS (§9.1)

Uniform square cells; **h and Δt both refine by exactly 2** at constant Courant
number U0Δt/h = 0.2037 (control refuses otherwise). `dim = 2`, r = 2.000.

| level | N × N | cells | h | steps | Δt | E2(T) predicted | KE error predicted | model row |
|---|---|---|---|---|---|---|---|---|
| coarse | 256 × 256 | 65,536 | 0.024544 | 400 | 0.005 | 9.459008e−06 | +4.483101e−06 | extrapolated (= F18's fine row, byte-identical numbers) |
| medium | 512 × 512 | 262,144 | 0.012272 | 800 | 0.0025 | 2.372083e−06 | +1.124117e−06 | extrapolated |
| fine | 1024 × 1024 | 1,048,576 | 0.006136 | 1,600 | 0.00125 | **5.948593e−07** | **+2.818669e−07** | extrapolated |

Model orders between the integrated grids 64²×100 → 128²×200: **p = 1.9955 (E2),
1.9957 (KE)** — the numbers F18 registered; every F18b row is the 128² integrated
value scaled by (h/h₁₂₈)^p. The predicted KE error is positive and sign-stable, so
the KE triple is predicted monotone.

**Why the model is not integrated at the new levels — measured, not assumed.**
`discrete_error()` factorises the 3N+1 sparse system once (SuperLU) and back-solves
it every step. Measured on this box in the writing invocation: 128²×200 → **37.5 s,
1.14 GB RSS**; 256²×400 → **not complete after 21 min at 9.0 GB RSS, stopped**;
512²×800 was not attempted (it would exceed the 30 GB box). The grader integrates
the model at every entry (exact selftest, grader selftest, launcher preflight,
grade), so the instrument keeps F18's two integrated grids. The brief's wording
("integrate at the new coarse and medium") is therefore not met, and this is the
reason. The extrapolation spans three doublings from 128² at p = 1.9955; F18's own
measured fine level sits 1.16× above the model's extrapolated value (E2 1.1014e−05
vs 9.459e−06; KE error 5.219e−06 vs 4.483e−06), inside the factor-3 window.

**DECOMPOSITION SEED (required field): `none`.** Every level serial on 1 rank;
`decomposePar` never invoked; no partition, no RNG.

## 5. THE GATES AND THEIR BANDS — THE DERIVATION IS F18's, BYTE-FOR-BYTE

`BAND_FACTOR = 3`, `bands()` and both gate definitions are the byte-identical F18
code (§1). Only the fine-level prediction the code reads changes, because the fine
level is now 1024². **The numeric bands therefore differ from F18's numbers:** F18's
E2 band [3.15e−06, 2.84e−05] was derived at h = 0.0245; at h = 0.00614 the model
predicts an error 15.9× smaller.

**G-F18-1 — normalised L2 velocity error at t = T**
Prediction at the fine level: **5.948593e−07**.
**Band = [prediction/3, prediction×3] = [1.982864e−07, 1.784578e−06].**

**G-F18-2 — box-mean kinetic energy at t = T**, exact **0.112332241029305**.
**Band = exact ± 3 × 2.818669e−07 = [0.112331395429, 0.112333086630].**

**Registered prediction: both triples `CONVERGING` with Roache observed order
rising above F18's (1.29 / 0.96) toward 2 as the pre-asymptotic 64² level leaves
the triple; fine values inside both bands → PASS.** Cross-check from F18's measured
trend, not from the model: continuing F18's last measured error ratio (3.56 per
doubling) from its fine level gives E2(1024²) ≈ 8.7e−07 and KE error ≈ 4.1e−07;
at ratio 4 they give 6.9e−07 and 3.3e−07 — all four inside the bands above.

**No plateau gate**, as in F18: the graded quantities are values at the fixed
instant t = T of a decaying transient; `plateau_states` is `None` and recorded
ABSENT in every row.

## 6. CRITERIA — unchanged from F18 §6, confirmed by running this copy

All F18 criteria hold verbatim (verdict vocabulary; rule 5 through `grade_ladder`
only; no plateau gate, said so; rule 5 limb 1 census over EVERY time step's final p
residual against the solver's own 1e−9; completion rule 4 with the fixed-Δt
identity **`Time` lines == 400 / 800 / 1600** and the age guard; L-342 field
classes driven both ways; planted-zero controls through the real parser; guards
refuse and never delete; `--preflight` fires nothing). **Measured in the writing
invocation on the F18b copy:**

| check | result |
|---|---|
| `exact_f18.py --selftest` | rc 0, 4 controls green, 51.6 s, 1.18 GB RSS |
| `python3 -O exact_f18.py --selftest` | **rc 2** |
| `grade_f18.py --selftest` | rc 0, 8 controls green, 40.8 s, 1.18 GB RSS |
| `python3 -O grade_f18.py --selftest` | **rc 2** |
| `assert` census (AST) over grade / exact / foam_io / build | **0 nodes; planted assert seen** |
| `grade_ladder` call nodes (AST) | **exactly 1** (line 484); grep matcher driven both ways |
| L-342 classes | PHYSICS_CRITICAL / INFRASTRUCTURE declared; control drives both directions |
| `set +u` around the bashrc source | inherited from F18, lines 136–139 of `run_f18.sh` |
| `scripts/check_launcher_can_launch.py --worktree run_f18.sh` (ARM 1 + ARM 3 at `3f29a32e`) | **rc 0**: 0 time-dir globs, 0 bashrc sources under `set -u` |
| `bash -n run_f18.sh` | parses |
| `run_f18.sh --preflight` | **rc 0**; instrument green; cap agrees 1500/1500; ν and endTime agree; run root reported ABSENT; blockMesh NOT run |
| ladder control | h ratios [2, 2], Δt ratios [2, 2], Co 0.2037 constant |

## 7. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING AND A PASSING VALUE

Through the real readers on files in the pinned write format (pinned against real
icoFoam output on this box, `verification/runs/ansys_verification/VMFL019/L1_30/5/U`,
parsed at selftest). The 128² integrated error field, scaled by the model's
128² → 1024² E2 ratio (0.015771), stands in for the fine field; both gate quantities
are cell means, so the size of the stand-in does not enter (the box-mean of the exact
field over a uniform periodic grid is exact to round-off at any N ≥ 3).

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F18-1 | exact(T) + **1×** scaled model error field | 5.948593e−07 | [1.983e−07, 1.785e−06] | **inside** |
| G-F18-1 | exact(T) + **40×** the same | 2.379437e−05 | same | **outside** |
| G-F18-2 | exact(T) + **1×** the same | 0.112332523 | [0.112331395, 0.112333087] | **inside** |
| G-F18-2 | exact(T) + **40×** the same | 0.112343520 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned against
real output, the *values* are constructed.

## 8. COST — COSTED BEFORE THE RUN, FROM F18's MEASURED CLOCKTIMES

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.**

**Rate basis — MEASURED on the byte-identical case definition, F18,
`verification/runs/F18_runs/{coarse,medium,fine}/log.icoFoam`, 2026-08-26:**

| F18 level | cells | steps | cell-steps | ClockTime | ExecutionTime | µs per cell-step | DIC-PCG iterations per p solve (mean) |
|---|---|---|---|---|---|---|---|
| coarse | 4,096 | 100 | 0.41 M | 1 s | 1.39 s | 3.4 | 75 |
| medium | 16,384 | 200 | 3.28 M | 18 s | 17.92 s | 5.47 | 143 |
| fine | 65,536 | 400 | 26.2 M | 246 s | 246.17 s | **9.39** | 257 (max 321) |

**The dispatch's basis of 5 µs/cell-step (≈ 140 core-min for the fine level) is
superseded by measurement.** F18's own estimate (5 µs, 2.5 core-min) was overrun
1.77× (actual 4.42 core-min; the queue runner wrote `CAP_OVERRUN.txt` at 190 s,
reported not enforced). The cause is visible in the log: the p solver is DIC-PCG
at tolerance 1e−9 with relTol 0 and its iteration count grows **∝ N** (75 → 143 →
257, ratios 1.91 and 1.80), so the per-cell-step rate grows **+61 % and +72 %** per
doubling and will approach +100 % (PCG iterations ∝ condition number^½ ∝ N). Taken
here as **+75 % then +80 %**, on top of ×8 cell-steps per level (×4 cells × ×2 steps):

| F18b level | cells | steps | cell-steps | rate (µs) | projected serial s | core-min | wall |
|---|---|---|---|---|---|---|---|
| coarse (= F18 fine, same grid and Δt) | 65,536 | 400 | 26.2 M | 9.39 (measured) | 246 | 4.1 | 4 min |
| medium | 262,144 | 800 | 209.7 M | 16.4 | 3,444 | 57.4 | 57 min |
| fine | 1,048,576 | 1,600 | 1,677.7 M | 29.6 | 49,670 | 827.8 | 13.8 h |
| **total** | | | **1,913.6 M** | | **53,360** | **889** | **14.8 h** |

At the asymptotic +100 %/doubling the total is **1,121 core-min** (fine 63,050 s =
17.5 h). **REGISTERED CAP: 1500 core-minutes** (1.69× the estimate, 1.34× the
asymptotic bound; the width is the admission — PCG on 1M cells at 1e−9 with relTol
0, serial, is the unknown). **Derived dollars at $0.0513/core-h: $0.76 estimate,
$0.96 at the asymptotic bound, $1.28 at the cap — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation.
**`cost_basis: derived from F18's measured ClockTimes, not measured on these levels.`**

**Stated for the supervisor's desk, not decided here:** the fine level is a
~14–18 h serial solve, and the case definition (serial, DIC-PCG, relTol 0) is what
makes it so. Running the fine level on 4 ranks or with GAMG for p would cut the
wall time several-fold, but either is a change to the launcher or to `fvSolution`,
i.e. to the byte-identical case definition this extension was dispatched on. The
ladder is registered serial as dispatched.

**Memory floor: 2.0 GB** — `icoFoam` at 1,048,576 cells serial is estimated at
**1–2 GB** (≈ 1 kB per cell for U, p, phi, the momentum matrix and the PCG work
vectors; an estimate, not measured — F18's fine level ran 65k cells); the grader's
model integration is **1.18 GB RSS measured**. **Disk:** fields at `endTime` only:
≈ 0.1 GB for the fine level (277 GB free on `/`).

The cap is checked **incrementally after each level** and **projected before each
level** from the launcher's own box probe (`PROJ_SERIAL_S` = 246 / 3444 / 49670 s,
the table above); a crossing **HALTS at exit 3**, unlaunched levels stay `PENDING`,
the cap is never raised. Launcher and grader carry the same cap and refuse to start
if they disagree (measured: "CAP AGREES … 1500").

**Scratch smoke arm, reported:** one real `icoFoam` step (Δt = 0.005) on a scratch
copy of the coarse level (256²) built by `build_f18.py` into the scratchpad, never
the case tree: rc 0, `Time = 0.005`, `End` written, **`Solving for Ux` initial
residual 4.99725050793e−04 (non-zero: the fields move)**, p DIC-PCG 321 and 254
iterations (the two correctors), final residuals 9.94e−10 / 9.50e−10, ExecutionTime
1.2 s; `0.005/U` written with 65,536 entries — **≈ 0.05 core-min including
blockMesh/checkMesh/postProcess**; not retained, not a measured history, not a
result.

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F18b_runs` → **ABSENT** (and
`--preflight` printed the same reading). `find cases/F18b_taylor_green_ext -name
RC.txt -o -name 'log.*'` → **0** files; the only numeric directory under the case
tree is the tracked template `case/0`. `ls -d verification/runs/F18b*` → 0.

## 10. EVERY CHANGED LINE — the diff the supervisor reads (check 1)

`diff -u cases/F18_taylor_green/<f> cases/F18b_taylor_green_ext/<f>`: `exact_f18.py`
21 removed / 34 added; `grade_f18.py` 10 removed / 11 added; `run_f18.sh` 11
removed / 14 added; `build_f18.py`, `foam_io_f18.py`, `case/**` **0**. sha256 of
the F18b files at this freeze: `exact_f18.py` 0524980c9…, `grade_f18.py`
9187e2ef1…, `run_f18.sh` 9703d6b09…, `build_f18.py` df0487791…, `foam_io_f18.py`
30501eac0…. The full unified diffs follow, verbatim.


```diff
# run_f18.sh
@@ -1,5 +1,6 @@
-# F18 -- LAUNCHER for the 2-D Taylor-Green vortex (icoFoam, transient, three-level ladder).
+# F18b -- LAUNCHER for the 2-D Taylor-Green vortex, LADDER EXTENSION 256^2 / 512^2 / 1024^2
+# (icoFoam, transient; byte-identical case definition to F18).
@@ -22,26 +23,28 @@
-ROOT="/home/ubuntu/Certonomous/cases/F18_taylor_green"
+ROOT="/home/ubuntu/Certonomous/cases/F18b_taylor_green_ext"
-RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F18_runs"
+RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F18b_runs"
-CAP_CORE_MIN=30             # must equal grade_f18.py::CAP_CORE_MIN
+CAP_CORE_MIN=1500           # must equal grade_f18.py::CAP_CORE_MIN
-LEVELS=("coarse 64 100 1" "medium 128 200 1" "fine 256 400 1")
-# projected SERIAL seconds per level at 5 us/cell-step -- DERIVED from one lab
-# record of a DIFFERENT case (VMFL019 icoFoam: 480 cells x 400 steps in 0.38 s
-# ExecutionTime = 2 us/cell-step, overhead-dominated at that size; 5 us allows
-# PCG growth with cell count).  NOT MEASURED on this case.  Used ONLY by the
+LEVELS=("coarse 256 400 1" "medium 512 800 1" "fine 1024 1600 1")
+# projected SERIAL seconds per level from F18's MEASURED ClockTimes on the SAME
+# case definition (verification/runs/F18_runs/{coarse,medium,fine}/log.icoFoam:
+# 1 / 18 / 246 s = 3.4 / 5.5 / 9.4 us per cell-step; DIC-PCG iterations 75 / 143 /
+# 257 grow with n), scaled by cell-steps (x8 per level) and by the measured +75 %
+# per doubling of the per-cell-step rate (+80 % at the last level); DERIVED from a
+# measurement of the parent case, NOT MEASURED on these levels.  Used ONLY by the
-declare -A PROJ_SERIAL_S=( [coarse]=2 [medium]=17 [fine]=131 )
+declare -A PROJ_SERIAL_S=( [coarse]=246 [medium]=3444 [fine]=49670 )
@@ -101,7 +104,7 @@
-sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F18_taylor_green")
+sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F18b_taylor_green_ext")
```

```diff
# grade_f18.py
@@ -57,7 +57,7 @@
-CAP_CORE_MIN = 30.0
+CAP_CORE_MIN = 1500.0                  # F18b: see the pre-registration section 8
@@ -414,10 +414,11 @@
-    """ZERO COMPUTE.  The model's MEDIUM error field is integrated; scaled by the
-    model's own medium->fine ratio it stands in for the fine field, so the rows
-    are format-faithful synthetic files at the medium size."""
-    m = EX.model("medium")
+    """ZERO COMPUTE.  F18b: the finest INTEGRATED grid's error field (128^2),
+    scaled by the model's 128^2 -> fine ratio, stands in for the fine field, so
+    the rows are format-faithful synthetic files at the 128^2 size (both gate
+    quantities are cell means, so the size of the stand-in does not enter)."""
+    m = EX.integrated(*EX.MODEL_GRIDS[-1])
@@ -511,7 +512,7 @@
-    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F18_runs"))
+    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F18b_runs"))
@@ -542,16 +543,16 @@
-    out = a.out or os.path.join(a.root, "F18_GRADED.json")
+    out = a.out or os.path.join(a.root, "F18b_GRADED.json")
-        json.dump(dict(rung="F18-TG2D", prereg_commit=a.prereg_commit,
-                       prereg="verification/campaign/F18_TG2D_PREREGISTRATION.md",
+        json.dump(dict(rung="F18b-TG2D-EXT", prereg_commit=a.prereg_commit,
+                       prereg="verification/campaign/F18b_TG2D_EXT_PREREGISTRATION.md",
-    print("F18 -- 2-D TAYLOR-GREEN VORTEX -- TALLY")
+    print("F18b -- 2-D TAYLOR-GREEN VORTEX, LADDER EXTENSION -- TALLY")
```

```diff
# exact_f18.py
@@ -56,8 +56,13 @@
-LEVELS = (("coarse", 64, 100), ("medium", 128, 200), ("fine", 256, 400))
-MODEL_LEVELS = ("coarse", "medium")          # integrated; fine is extrapolated
+LEVELS = (("coarse", 256, 400), ("medium", 512, 800), ("fine", 1024, 1600))   # F18b: F18's fine is this coarse
+# F18b EXTENSION: the linearised error equations are INTEGRATED on these (n, steps)
+# grids -- F18's own coarse and medium, 37.5 s / 1.14 GB RSS measured for 128^2 --
+# and EXTRAPOLATED to every F18b level with the model's own observed order between
+# them.  256^2 x 400 measured 6.9 GB RSS and > 12 min per integration; 512^2 would
+# exceed this 30 GB box; the grader integrates at every entry, so neither is solved.
+MODEL_GRIDS = ((64, 100), (128, 200))
@@ -242,34 +247,43 @@
+def integrated(n, steps):
+    if (n, steps) not in MODEL_GRIDS:
+        refuse("grid %d^2 x %d is not integrated by the model; it is extrapolated" % (n, steps))
+    if (n, steps) not in _CACHE:
+        _CACHE[(n, steps)] = discrete_error(n, steps)
+    return _CACHE[(n, steps)]
+
+
-    if name not in _CACHE:
-        lv = dict((nm, (n, s)) for nm, n, s in LEVELS)
-        if name not in MODEL_LEVELS:
-            refuse("level %r is not integrated by the model; it is extrapolated" % name)
-        _CACHE[name] = discrete_error(*lv[name])
-    return _CACHE[name]
+    lv = dict((nm, (n, s)) for nm, n, s in LEVELS)
+    if name not in lv:
+        refuse("unknown level %r" % name)
+    return integrated(*lv[name])
-    """Integrated at coarse and medium; fine extrapolated with the model's own order."""
+    """Integrated on MODEL_GRIDS; every ladder level not among them is extrapolated
+    from the finest integrated grid with the model's own orders (E2, KE separately)."""
-        mc, mm = model("coarse"), model("medium")
-        p_e2 = math.log(mc["E2_pred"] / mm["E2_pred"]) / math.log(2.0)
-        p_ke = math.log(abs(mc["ke_err_pred"]) / abs(mm["ke_err_pred"])) / math.log(2.0)
-        fine_e2 = mm["E2_pred"] / 2.0 ** p_e2
-        fine_ke = mm["ke_err_pred"] / 2.0 ** p_ke
+        mc, mm = integrated(*MODEL_GRIDS[0]), integrated(*MODEL_GRIDS[1])
+        r = math.log(mc["h"] / mm["h"])
+        p_e2 = math.log(mc["E2_pred"] / mm["E2_pred"]) / r
+        p_ke = math.log(abs(mc["ke_err_pred"]) / abs(mm["ke_err_pred"])) / r
-            if nm in MODEL_LEVELS:
-                m = model(nm)
+            if (n, s) in MODEL_GRIDS:
+                m = integrated(n, s)
+                f = h_of(n) / mm["h"]
-                                E2_pred=fine_e2, ke_err_pred=fine_ke,
-                                source="extrapolated from medium with model orders %.4f (E2), %.4f (KE)" % (p_e2, p_ke)))
+                                E2_pred=mm["E2_pred"] * f ** p_e2, ke_err_pred=mm["ke_err_pred"] * f ** p_ke,
+                                r_conv_L2=mm["r_conv_L2"], r_diff_L2=mm["r_diff_L2"],
+                                source="extrapolated from %d^2 x %d with model orders %.4f (E2), %.4f (KE)"
+                                       % (mm["n"], mm["steps"], p_e2, p_ke)))
@@ -338,10 +352,11 @@
-    for row in tab:
-        if row.get("source") == "integrated" and (row["r_conv_L2"] <= 0.0 or row["r_diff_L2"] <= 0.0):
+    for n, st in MODEL_GRIDS:
+        row = integrated(n, st)
+        if row["r_conv_L2"] <= 0.0 or row["r_diff_L2"] <= 0.0:
-                   "on the exact field at level %s" % row["name"])
+                   "on the exact field on grid %d^2 x %d" % (n, st))
```

## 11. NEVER RUN — THE EVIDENCE

- Tracked paths enumerated with `git ls-tree -r HEAD --name-only`: **14,484** at the
  writing invocation; matches for `F18b|taylor_green_ext`: **0** (planted control:
  `cases/F18_taylor_green/run_f18.sh` is in the enumeration, 1 hit).
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (534 entries) **0**;
  `/home/ubuntu/closure-data` (22) **0**; `/home/ubuntu/closure-challenge-benchmark`
  (7) **0**. `verification/runs/` holds no `F18b*` directory.

## 12. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F18b_taylor_green_ext/run_f18.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F18b_taylor_green_ext/grade_f18.py --prereg-commit=<sha>`. The queue
entry `cases/F18b_taylor_green_ext/queue_entry_F18b_TG2D_EXT.json` is **HELD in the
case directory** until the supervisor's check 1/4; the supervisor, not this lane,
drops it into `verification/queue/cfd/`.

## 13. WHAT IS NOT REGISTERED HERE

- No re-grade of F18; no claim about p beyond its role as an initial field.
- No amendment to any standard, charter or to F18's frozen record; F18's own
  estimate-versus-actual calibration row is F18's completion duty, not this file's.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
