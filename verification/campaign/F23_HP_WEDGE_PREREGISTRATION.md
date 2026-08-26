# F23 — PRE-REGISTRATION: Hagen–Poiseuille pipe flow on an OpenFOAM axisymmetric WEDGE (simpleFoam, streamwise cyclic, fixed body force, 4 ranks)

**Team:** cfd. **Case id:** `F23_HP_WEDGE`. **Written before any compute. ZERO
CORE-MINUTES SPENT in the case tree or any run root.** **Status at freeze: ARMED —
never run.** Frozen by the commit that carries this file. After first compute the
gates, thresholds, cap and labels below are **closed**; changes land only as dated
addenda that cannot alter them. Decided and recorded **`[lab-attributed]`** under
Sanaa's standing order that the cfd queue is kept deep with pre-registered, costed
cases sized in HOURS (chief addenda `73eccb1b`, `7def3c6b`, `3c3ef86c`). Templates
in structure and rigour: F17b (`cases/F17b_kovasznay_ext/`, simpleFoam ladder),
F19/F20 (rhoCentralFoam ladders).

**Capability-grid cell (068c2bf0): axisym · steady · incompressible.**

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled so at registration; not a result; counts toward no challenge column; not
filmed. Its purpose: the lab's first axisymmetric-wedge ladder against an exact
target with the N-AV9 wedge bias carried explicitly, and the first 4-rank
(decomposePar) ladder graded from the processor directories.

---

## 1. THE CASE, AND WHY THIS FORM OF IT

Fully developed laminar pipe flow, **Re_D = 100**: R = 0.5 (D = 1), ν = 0.01,
Ubar = 1. Exact solution u(r) = 2 Ubar (1 − r²/R²), −dp/dx = G = 8 ν Ubar / R² =
**0.32**, u_max = 2, **f·Re = 64** (f = 2 D |dp/dx| / (ρ Ubar²), Re = Ubar D/ν).

**Fully developed by construction — streamwise `cyclic` with a FIXED body force.**
Two forms were open (the dispatch asked for the one whose exact solution is
cleanest, and why):

| form | exact solution of the case as posed? | what is imposed / read |
|---|---|---|
| long pipe, inlet profile, outlet pressure (VMFL005's form) | **no** — a developing pipe has no closed form; imposing the parabola at the inlet leaves a discretisation-dependent adjustment length, and the pressure drop must be sampled between two stations inside the developed region | Ubar imposed, Δp read at two stations |
| **cyclic in x, adaptive `meanVelocityForce`** | yes, but the source is a nonlinear controller (relaxed Ubar correction), the pressure gradient is a log/`uniform/` artefact, and the discrete problem is not linear | Ubar imposed, G read from the controller |
| **cyclic in x, FIXED `vectorSemiImplicitSource` G = 0.32 (CHOSEN)** | **yes**: the parabola is an exact solution of the case as posed; every x-column is the same column | **G imposed, Ubar_h READ from the field**; f·Re_h = 2 D² G / (ν Ubar_h) |

The chosen form makes the discrete problem **linear** and makes **both gate quantities
readings of the velocity field** (planted-zero controls through the real reader on
the real artifact), with no controller and no pressure sampling.

| item | value |
|---|---|
| geometry | x ∈ [0, L], **L = 16 D = 16.0** (cyclic; the length buys cells for the hours order, not accuracy — the physics is 1-D in r); r ∈ [0, R] along +y; wedge symmetric about z = 0, **half angle a = 0.04°** (0.08° total), wall vertices at EXACT radius R (VMFL005's construction) |
| patches | `inlet`/`outlet` **cyclic** pair; `wall` (noSlip; p zeroGradient); `wedge1`/`wedge2` **`type wedge`** |
| solver | `simpleFoam`, laminar, `steadyState`; `Gauss linear` everywhere; Laplacian `Gauss linear corrected` (the mesh is orthogonal in r–x: checkMesh **non-orthogonality max 0**, §2); U 0.7 / p 0.3; **U solved by GAMG to relTol 1e-3 / 1e-12** (pure radial diffusion: the low-frequency error must be removed by multigrid, not by 4000 Gauss–Seidel sweeps); **no `residualControl`**, fixed **4000 iterations**, checkpoints every 100 |
| source | `constant/fvOptions`: `vectorSemiImplicitSource`, `selectionMode all`, `volumeMode specific`, `U ((0.32 0 0) 0)` |
| initial field | U = (0 0 0) everywhere (the flow is driven from rest; nothing of the answer is seeded); 0/U written **last** by the builder |
| ranks | **4 at every level**, `decomposePar` `simple n (1 4 1)` (radial bands; the cyclic pair and the wedge pair stay whole on every rank), **never reconstructed**: the grader reads `processor*/` |

**Mesh admissibility (MESH_STANDARD §3, §8.1).** The coarse level (64 × 2048) was
**BUILT AND `checkMesh`'d** on a scratch copy by `build_f23.py` in the writing
invocation: 131,072 cells, `Mesh OK`, **max non-orthogonality 0° (gate 70°)**, max
skewness 0.33 (gate 4), **max aspect ratio 2.0** (advisory 1000, §3.3), both wedge
patches reported at **0.0400002766821°** (checkMesh's own reading; the builder
refuses a wedge angle that is not the registered half angle to 1e-6). The builder
enforces both hard gates at every level and records aspect ratio and wedge angles in
`MESH_LINE.txt`.

**The N-AV9 wedge bias, carried explicitly.** A wedge cell is flat-sided, so the
discrete solution converges under r–x refinement to (1 + O(a²)) times the polar
discrete solution — an error refinement does not remove (`NUMERICS_KNOWLEDGE.md`
N-AV9). The model in §4 contains the bias exactly (the mesh's own cos a / sin a
factors) and prints it per level as model(a) − model(a → 0). **The half angle
0.04° was chosen so the bias at the FINE level is below a tenth of the fine level's
discretisation error** — a control in `exact_f23.py` refuses otherwise:

| level | E2n bias (model(a) − polar) | fine-level discretisation E2n (polar) | f·Re bias | f·Re discretisation error (polar) |
|---|---|---|---|---|
| fine | −6.44e−08 | 7.193e−06 (bias = 0.9 %) | +3.12e−05 | −4.883e−04 (bias = 6.4 %) |

At 1° half angle the same bias would be 6e−4 on E2n — larger than every level's
discretisation error — and the ladder would be DEGENERATE by construction; that is
why the angle is 25× smaller than VMFL005's 2.5°.

## 2. THE REFERENCE IS NOT A PAPER. IT IS A SUBSTITUTION.

Rule 15 requires title-page verification of every retrieved paper; this case
retrieves none. `exact_f23.py --selftest` (rc 0 in the writing invocation) substitutes
the profile symbolically into the axisymmetric x-momentum equation
ν (1/r) d/dr(r du/dr) + G = 0 (residual identically **0**), checks Ubar =
(2/R²)∫u r dr = **1** and f·Re = **64** symbolically, and the planted control (R
scaled 1.1× inside the profile against the registered G) gives a **non-zero**
residual. `python3 -O exact_f23.py --selftest` → **rc 2**.

## 3. THE LADDER — THREE LEVELS (§9.1), `dim = 2`

Square cells dx = dr = R/NR at every level; both directions refine by exactly 2
(control refuses otherwise). r = 2.000 from cell counts.

| level | NR × NX | cells | h = dr | ranks | E2n predicted (§4) | f·Re predicted (§4) |
|---|---|---|---|---|---|---|
| coarse | 64 × 2048 | 131,072 | 1/128 | 4 | 1.149980e−04 | 63.992221588 (err −7.778e−03) |
| medium | 128 × 4096 | 524,288 | 1/256 | 4 | 2.869164e−05 | 63.998078262 (err −1.922e−03) |
| fine | 256 × 8192 | 2,097,152 | 1/512 | 4 | 7.128682e−06 | 63.999542924 (err −4.571e−04) |

Model orders across the ladder: E2n **2.003 / 2.009**, f·Re **2.017 / 2.072** (the
polar limit gives 2.000 / 2.000; the small excess is the wedge bias bending the fine
end). **Registered prediction: both triples CONVERGING with observed order p ≈ 2,
fine values inside both bands → PASS × 2.**

**DECOMPOSITION SEED (required field): `none`** — `simple` geometric decomposition
from `system/decomposeParDict`, deterministic, no RNG; 4 subdomains at every level.

## 4. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION

**One declared parameter, `BAND_FACTOR = 3`**, applied to predictions computed from
the scheme on the mesh's own geometry. Declared now; not fitted; not revisable.

**The derivation.** On the fully developed cyclic wedge the x-faces cancel
identically and convection is null, so simpleFoam's steady discrete x-momentum
equation per cell reduces **exactly** to the radial stencil
Σ_f ν |S_f| (u_N − u_P)/|d_f| + G V_P = 0, with |S_f| the planar chord areas
2 r_f sin a, V_P the trapezoid volumes, |d_f| the centroid-to-centroid distances
(trapezoid centroids, cos a scaled) and the wall a fixedValue face at |C_f − C_P|.
`exact_f23.discrete()` builds and solves that tridiagonal system on the blockMesh
geometry. `build_f23.py` then checks the built mesh's own `0/C` and `0/V` against the
model geometry to 1e−9 and refuses otherwise, so the band rests on the geometry the
solver actually sees.

**Instrument check, scratch, disclosed (0.3 core-min; NOT a level of the ladder; not
retained; not a result):** a 16 × 64 wedge (1,024 cells, 4 ranks, the real chain
`build_f23.py` → `decomposePar` → `mpirun -np 4 simpleFoam -parallel`, 4000
iterations, ClockTime 17 s) returned E2n = **1.8361784389e−03** and f·Re =
**63.8756587360** against the model's **1.8361784398e−03** and **63.8756587360**
— the solver's discrete station profile matches the model's cell by cell to
**5.7e−12**, `Ux` initial residual reached 2.3e−16, max|Uy| = 4.5e−16, max|Uz| =
9.2e−16, all-cell and station bulk velocities equal to 1e−15. **The model IS the
discretisation to round-off on that grid;** the factor-3 window therefore guards
what the model omits (the iterative tolerance at 2.1 M cells over 4 ranks, the
floating-point ordering across ranks, the 4000-iteration plateau), not the stencil.

**G-F23-1 — E2 of the NORMALISED axial profile at the station**
E2n = √( Σ_j V_j (u_j/Ubar_h − u_exact(r_j)/Ubar)² / Σ_j V_j ), over the one x-column
of cells nearest x = L/2 + dx/2 (its count must equal NR; refused otherwise), r_j the
mesh's own cell-centre y, V_j its own cell volume, Ubar_h the station's
volume-weighted bulk velocity. Normalised by the READ bulk velocity so the gate is the
profile SHAPE (the amplitude is G-F23-2's).
Prediction at fine: **7.128682e−06**.
**Band = [prediction/3, prediction×3] = [2.376227e−06, 2.138605e−05].**

**G-F23-2 — f·Re from the imposed G and the READ bulk velocity**
f·Re_h = 2 D² G / (ν Ubar_h). Exact **64**. Predicted fine error **−4.571e−04**.
**Band = 64 ± 3 × 4.571e−04 = [63.998628773, 64.001371227].**

## 5. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
  PENDING, and nothing else.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node (`grade_f23.py:769`
  at freeze), AST-censused; the text matcher driven both ways.
- **Class C plateau** (all four elements) on the graded quantity itself at every
  checkpoint (100 iterations apart, 40 samples; min 20; window 12 = 1200 iterations;
  trend 2e−4, stationarity 1e−4, variance ratio [0.2, 5]); element 4 exits.
- **Rule 5 limb (1) — census, with the excluded channels declared (N-AV8).** The
  solver's **`Ux` initial residual ≤ 1e−8 at every iteration of the census window**
  (the driven component), plus a **field-level** check that the transverse
  components are zero: max|Uy|, max|Uz| ≤ 1e−10 × U_MAX at endTime. The normalised
  initial residuals of **Uy, Uz and p are PRINTED beside the verdict and EXCLUDED
  from the gate**: each is a vanishing channel (u_r ≡ 0; u_z is the direction the
  wedge constrains rather than solves; p is uniform on the cyclic domain) whose
  relative residual is normalised by a vanishing scale — measured on the scratch
  instrument run: Uy residual 5.5e−2 with max|Uy| = 4.5e−16 in the field. Excluded
  at the freeze, printed anyway.
- **Completion (rule 4):** `RC.txt` = 0; `End`; latest + 1 > endTime; **`Time` lines
  == 4000**; `U` and `p` at `4000/` in **every one of the 4 processor directories**,
  each **newer than the serial `0/U`** (written last at build, before decomposePar).
- **L-342 field classes.** `PHYSICS_CRITICAL`: log `End`/`Time` count, `RC.txt`,
  processor endTime fields + age guard, `processor*/0/C` and `0/V`, checkpoint U
  files, `Ux` residuals and the transverse field maxima. `INFRASTRUCTURE`:
  `ClockTime`, box probes, `MESH_LINE.txt`, utility logs (`log.decomposePar`,
  `log.blockMesh`, `log.checkMesh`, `log.build`), runner `STATUS`/`launcher.queue.out`
  /`LAUNCH_LOG` rows, calibration figures. Verdicts key on the first only; a missing
  INFRASTRUCTURE field prints `BOOKKEEPING DEFECT` and refuses the **cost claim
  only**. Driven both ways at selftest (infra deleted → completion unchanged + cost
  claim refused; rc corrupted / `End` deleted / one `Ux` reading above tolerance
  inside the window / transverse field above floor / a missing rank → the level
  flips).
- **Planted-zero controls (rule 3)** into copies of the real processor `U` files, read
  back with the real parser: δ = 1.234e−3 on Ux must move E2n to the value predicted
  in memory (the plant shifts u and the read Ubar_h together; 1e−13) and f·Re to
  2 D² G/(ν (Ubar_h + δ)) (1e−10); a plant that does not move a reading refuses.
- **`assert` census: ZERO** across `grade_f23.py`, `exact_f23.py`, `foam_io_f23.py`,
  `build_f23.py`; planted assert seen. **Hard `-O` refusal at entry** — measured:
  `exact_f23.py --selftest` rc 0 / `-O` rc 2; `grade_f23.py --selftest` rc 0 (7.1 s,
  72 MB RSS) / `-O` rc 2.
- **Success messages print INSIDE the passing branch.**
- **Guards.** Launcher and builder **REFUSE** a pre-existing `0/`, numeric time or
  `processor*` directory in the run root and in each level directory; neither deletes;
  the builder refuses a destination inside the tracked case tree and refuses to build
  a registered level under `--scratch`.
- **`set -u` dropped around the OpenFOAM bashrc source only** (L-339;
  `run_f23.sh:167–170`); `scripts/check_launcher_can_launch.py --worktree
  cases/F23_HP_WEDGE/run_f23.sh` → **rc 0** (0 time-directory globs, 0 bashrc sources
  under `set -u`).
- **`--preflight` fires nothing** (no blockMesh, no build, no decomposePar); measured:
  rc 0, instrument green, cap agrees 1100/1100, ν/G/ranks/endTime agree, run root
  reported ABSENT; no-argument invocation rc 1.
- **Dictionaries cross-checked** at every grader entry and by the launcher (ν, G,
  `volumeMode specific`/`selectionMode all`, `numberOfSubdomains 4`, `endTime 4000`,
  `writeInterval 100`, no `residualControl`, cyclic/wedge/wall declarations, `noSlip`).

## 6. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Through the real readers on files in the pinned write format (`U`, `C`, `V`; pinned
against real solver output on this box,
`verification/runs/ansys_verification/VMFL019/L1_30/5/U`, parsed at selftest), on a
4-column synthetic level at the fine radial size carrying the model's SOLVED fine
station profile:

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F23-1 | exact + 1× model error field | 7.128682e−06 | [2.376e−06, 2.139e−05] | **inside** |
| G-F23-1 | exact + 40× the same | 1.916700e−04 | same | **outside** |
| G-F23-2 | exact + 1× the same | 63.999542924 | [63.998628773, 64.001371227] | **inside** |
| G-F23-2 | the same with u × 1.001 | 63.935607317 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned, the
*values* are the model's.

## 7. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** Ranks = 4 at every level.

**Rate basis — DERIVED, NOT MEASURED on this case:** F17's MEASURED simpleFoam rate
on a DIFFERENT case (`verification/runs/F17_runs/fine/log.simpleFoam`: 24,576 cells
× 4000 iterations in ClockTime 58 s = **0.59 µs per cell-iteration**), grown
**+30 % per doubling** of the cell count (the GAMG cycle-growth reading in
`F17b_KV40_EXT_PREREGISTRATION.md` §8). Disclosed against it: VMFL005, the lab's
other simpleFoam wedge, measured **2.1 µs/cell-iteration** at 16k cells with an extra
non-orthogonal corrector (`verification/runs/ansys_verification/VMFL005/L3_400x40/log.simpleFoam`,
6000 iterations, ClockTime 200 s); the +30 %/doubling growth places every F23 level
at or above that reading. The projection assumes ideal 4-rank scaling; the cap
check is on the measured ClockTime × 4 regardless.

| level | cells | doublings over 24,576 | rate (µs) | core-s | core-min | wall on 4 ranks |
|---|---|---|---|---|---|---|
| coarse | 131,072 | 2.415 | 1.112 | 583 | 9.7 | 2.4 min |
| medium | 524,288 | 4.415 | 1.879 | 3,940 | 65.7 | 16 min |
| fine | 2,097,152 | 6.415 | 3.175 | 26,637 | **444.0** | **1.85 h** |
| **total** | | | | **31,160** | **519.4** | **≈ 2.2 h** |

**Serial versus 4 ranks — stated:** the fine level serial would be 26,637 s ≈ 7.4 h
on this basis, over the ~4 h line the dispatch drew, so the ladder runs on **4 ranks
with `decomposePar` at every level** (one decomposition method for the whole ladder;
the runner reserves 4 cores for the launch).

**REGISTERED CAP: 1,100 core-minutes** (2.12× the estimate; the admission is the
parallel efficiency at 2.1 M cells on a shared box and GAMG growth beyond +30 %/
doubling). **Derived dollars at $0.0513/core-h: $0.44 estimate, $0.94 at the cap —
DERIVED, NOT MEASURED, reported-by-owner rate** (`COMPUTE_BUDGET_CHARTER.md` §5).
Under the $25 pre-authorisation. **`cost_basis: derived, reported-by-owner, not
measured.`**

Cap checked **incrementally after each level** and **projected before each level**
from the launcher's own box probe (`PROJ_CORE_S` = 583 / 3940 / 26640 core-s, scaled
up when fewer than 4 cores are free); a crossing **HALTS at exit 3**; unlaunched
levels stay `PENDING`; launcher and grader refuse to start if their caps disagree.

**Memory floor: 4.0 GB** (simpleFoam + GAMG at 2.1 M cells over 4 ranks; the grader's
model is a 256-row tridiagonal, negligible). **Disk:** 40 checkpoints × (U + p + phi)
≈ 8.8 GB for the fine level, ≈ 11.5 GB for the ladder (274 GB free on `/` in the
writing invocation).

**Scratch smoke arm, reported (cfd pre-freeze requirement since F16):** ONE real
`simpleFoam` iteration on a scratch copy of the **coarse level** (64 × 2048 =
131,072 cells) built by `build_f23.py` into the scratchpad, decomposed and run on
**4 ranks** through the launcher's own chain: rc 0, `Time = 1`, `End`, **`Solving
for Ux` initial residual 1 → final 7.2e−05 in 2 GAMG iterations; max|Ux| after one
iteration = 1.139e−03 (NON-ZERO: the driven component moves)**, max|Uy| = 4.5e−08,
max|Uz| = 0 exactly (the wedge's constrained direction), ExecutionTime 0.49 s; not
retained, not a measured rate, not a result.

**Convergence risk, registered:** the census window is iterations 2801–4000. On the
scratch 16 × 64 instrument run `Ux` reached 1e−8 by iteration ≈ 60 and 2e−16 by
4000; if the 2.1 M-cell level has not reached 1e−8 inside the window the level is
**NOT A RESULT** by rule 5 limb 1 and stays so.

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 8. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`test -e /home/ubuntu/Certonomous/verification/runs/F23_HP_WEDGE_runs` → **ABSENT**
(and `--preflight` printed the same reading at 2026-08-26T21:09Z). No `RC.txt`,
`log.*`, numeric time or `processor*` directory exists under `cases/F23_HP_WEDGE/`;
the only numeric directory is the tracked template `case/0` (holding `p` and
`U.template`).

## 9. NEVER RUN — THE EVIDENCE (L-337 controls first)

- `git ls-tree -r HEAD --name-only`: **14,944** tracked paths at the writing
  invocation; **planted control: the known `cases/F20_ISENTROPIC_VORTEX/` paths are
  returned (15)**; matches for `F23|HP_WEDGE`: **0**.
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (536 entries) **0**;
  `/home/ubuntu/closure-data` (22) **0**; `/home/ubuntu/closure-challenge-benchmark`
  (7) **0**. `verification/runs/` holds no `F23*` directory.

## 10. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F23_HP_WEDGE/run_f23.sh --prereg-commit=<this file's freeze sha>

4 ranks at every level (`mpirun -np 4 simpleFoam -parallel`); grading is a separate
invocation `python3 cases/F23_HP_WEDGE/grade_f23.py --prereg-commit=<sha>` reading
the processor directories. The queue entry
`cases/F23_HP_WEDGE/queue_entry_F23_HP_WEDGE.json` is **HELD in the case directory**
until the supervisor's check 1/4; the supervisor, not this lane, moves it into
`verification/queue/cfd/`; enqueueing is not authorisation.

## 11. FROZEN FILES (sha256 at this freeze, first 8 / last 4)

    cases/F23_HP_WEDGE/exact_f23.py    6c60bdfc…1015     cases/F23_HP_WEDGE/grade_f23.py   0cf82b8c…dfb9
    cases/F23_HP_WEDGE/build_f23.py    59c8ff14…05a5     cases/F23_HP_WEDGE/foam_io_f23.py 160384ee…9235
    cases/F23_HP_WEDGE/run_f23.sh      e1cbdfd6…89a9
    cases/F23_HP_WEDGE/case/0/{p,U.template}
    cases/F23_HP_WEDGE/case/constant/{transportProperties,turbulenceProperties,fvOptions}
    cases/F23_HP_WEDGE/case/system/{blockMeshDict.template,controlDict,fvSchemes,fvSolution,decomposeParDict}
    verification/campaign/F23_HP_WEDGE_PREREGISTRATION.md   (this file)

## 12. WHAT IS **NOT** REGISTERED HERE

- No claim about developing flow, entry length or any x-dependence: the case is
  fully developed by construction and every x-column is the same column (the grader
  prints the all-cell vs station bulk-velocity difference as a diagnostic, ungated).
- No re-grade of VMFL005; no amendment to any standard, charter or to N-AV9.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
