# F21 — PRE-REGISTRATION: pulsatile Womersley channel flow, α = 5, ladder 128² / 256² / 512²

**Team:** cfd. **Case id:** `F21_WOMERSLEY`. **Written before any compute. ZERO
CORE-MINUTES SPENT in the case tree or any run root** (a 24-step scratch smoke probe
of ≈ 0.07 core-min was run in the scratchpad and is reported in §8; it is not a
result and nothing of it is retained). **Status at freeze: ARMED — never run.**
Frozen by the commit that carries this file. After first compute the gates,
thresholds, cap and labels below are **closed**; changes land only as dated addenda
that cannot alter them. Decided and recorded **`[lab-attributed]`** on the cfd
supervisor's dispatch of 2026-08-26 (batch 2 of the queue-depth registrations).

**Capability-grid cell (068c2bf0): 2D · unsteady · incompressible.**

---

## 1. THE CASE

Laminar pulsatile flow in a 2-D channel, `pimpleFoam` in PISO mode (nOuterCorrectors
1, nCorrectors 2, momentumPredictor yes), `simulationType laminar`, `backward` (BDF2)
in time, Gauss linear everywhere, orthogonal Laplacian on a uniform Cartesian mesh.

| item | value |
|---|---|
| domain | x ∈ [0, LX = 2] **cyclic** (left/right); y ∈ [−H, H] = [−1, 1] **no-slip walls** (top/bottom); z empty |
| drive | uniform kinematic body force **f(t) = A cos(ωt) x̂**, A = 1, ω = 2π (PERIOD = 1), by `fvOptions` `vectorSemiImplicitSource` (`selectionMode all`, `volumeMode specific`, `explicit { type cosine; frequency 1; amplitude 1; scale (1 0 0); }`) — the oscillating pressure gradient −∂p/∂x |
| viscosity | ν = ωH²/α² = 2π/25 = **0.25132741228718347**, so the Womersley number **α = H√(ω/ν) = 5 exactly** |
| velocity scale | U_ref = A/ω = 1/(2π) = 0.15915494309189535 (the Womersley amplitude scale); every gate is normalised by it |
| initial condition | the EXACT field at t = 0 at the built mesh's own cell centres (from `0/C`), `0/U` written LAST by `build_f21.py`; `0/p` uniform 0 (the exact pressure is uniform) |
| end time | **t_end = 12.25 = 12 periods + T/4**, the locked phase at which the centreline velocity peaks (§4 says why the phase was chosen and which phase was rejected) |
| writes | every 0.25 (quarter period); the gates read t = 12.25, the periodicity check t = 11.25 |
| linear solvers | p DIC-PCG 1e−9 relTol 0 (the F18 lineage, so its measured iteration growth transfers); U DILU-PBiCGStab 1e−12 relTol 0 |

**The solution is x-invariant, so the x direction is a test, not padding:** any
x-variation the solver produces is error and is counted by G-F21-1. The mesh is N×N
square cells over LX × 2H = 2 × 2.

**Mesh admissibility (MESH_STANDARD §3, §8.1).** The coarse level (128²) was **BUILT
AND `checkMesh`'d** on a scratch copy by `build_f21.py` in the writing invocation:
16,384 cells, max non-orthogonality **0°** (gate 70°), max skewness **0** (gate 4),
`Mesh OK` (`MESH_LINE.txt` reading quoted in §8). The builder enforces both gates at
every level and refuses a destination holding `0/` or a numeric time directory.

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled at registration; not a result; counts toward no challenge column; not
filmed. Its purpose: a **time-accurate** exact solution (the F18 Taylor–Green family
tests decay; this tests a **driven periodic state** with a Stokes layer of thickness
√(2ν/ω) = 0.283 H resolved by 18 / 36 / 72 cells), the `fvOptions` time-dependent
source path, and the cyclic/no-slip pairing.

## 2. THE REFERENCE IS NOT A PAPER — it is a substitution

    u(y, t) = Re[ (A / (iω)) (1 − cosh(ky) / cosh(kH)) e^{iωt} ],   k = √(iω/ν),   v = 0,   p = const

`exact_f21.py --selftest` (rc 0 in the writing invocation; rc 2 under `python3 -O`):
the closed form substituted symbolically (sympy, k symbolic, k² → iω/ν) into the
unsteady x-momentum equation u_t = ν u_yy + A cos ωt gives an identically zero
residual; the convective term is identically zero for an x-invariant field and
continuity is trivially satisfied by v = 0; the residual is also evaluated
numerically at 200 random (y, t) points (max **< 1e−12**); u(±H, t) = 0 to 1e−14;
α = 5 to 1e−12. **Planted control:** k → 1.1 k gives a non-zero residual.

## 3. THE LADDER — THREE LEVELS, r = 2 in h AND Δt

| level | N × N | cells | h | steps to 12.25 | steps / period | Δt | Co (max) |
|---|---|---|---|---|---|---|---|
| coarse | 128 × 128 | 16,384 | 1/64 | 1,176 | 96 | 1/96 | 0.113 |
| medium | 256 × 256 | 65,536 | 1/128 | 2,352 | 192 | 1/192 | 0.113 |
| fine | 512 × 512 | 262,144 | 1/256 | 4,704 | 384 | 1/384 | 0.113 |

`dim = 2`, r = 2.000 in h and in Δt (control refuses otherwise); N even (the probe
straddles y = 0); steps = 12.25 × steps/period exactly (control).

**DECOMPOSITION SEED (required field): `none`.** Every level serial on 1 rank;
`decomposePar` not invoked; no partition, no RNG. (4 ranks were considered for the
fine level and rejected: the parallel efficiency of DIC-PCG at 262k cells is not
measured on this box, and a 4-rank entry is held longer by the runner; §8.)

## 4. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION, NOT MEASURED

**The model (`exact_f21.discrete_solution`).** The flow is linear and one-dimensional,
so the solver's discretisation reduces EXACTLY to a 1-D finite-volume heat equation:
cell-centred second-order Laplacian, no-slip wall face gradient (u_P − 0)/(h/2),
BDF2 with OpenFOAM's Euler-implicit first step, the cosine source at the new time
level. The PISO pressure correction is identically zero on an x-invariant field. The
model is **solved** on the coarse and medium grids and **extrapolated** to the fine
grid with its own observed order; the direct fine solve is also computed as a
cross-check (control: agree to 10 %; measured **0.07 %** apart, ratio 0.99932).
Model orders between the solved grids: **2.0035 (E2), 1.9976 (probe)**.

| level | E2_pred | probe error pred (u/U_ref) | period-to-period change pred | row |
|---|---|---|---|---|
| coarse | 1.240156e−03 | −1.738896e−03 | 4.07e−08 | solved |
| medium | 3.092833e−04 | −4.354489e−04 | 6.79e−09 | solved |
| fine | **7.713234e−05** | **−1.090437e−04** | 1.69e−09 | extrapolated (direct solve: 7.718462e−05 / −1.088888e−04) |

**Planted control on the model:** a zero-gradient wall stencil (coefficient 2 instead
of 3) moves the coarse E2_pred from 1.24e−03 to 1.24e−02 (10×), so the model reads
its own wall discretisation.

`BAND_FACTOR = 3`, the one declared parameter, covers the omissions: solver
tolerances, the x-invariance the 2-D solver must keep, PIMPLE's momentum predictor,
round-off.

**G-F21-1 — normalised L2 velocity error at the locked phase**
E2 = √(mean over cells |U_h − U_exact(x_c, y_c, 12.25)|²) / U_ref, both components.
Prediction **7.713234e−05**. **Band = [prediction/3, prediction×3] =
[2.571078e−05, 2.313970e−04].**

**G-F21-2 — centreline u/U_ref at the probe (LX/2, 0) at the locked phase**, bilinear
between the four surrounding cell centres. **Reference = the exact field sampled at the
fine level's own cell centres and interpolated by the grader's own `bilinear()`** =
**1.053804125252269** (pointwise exact 1.053803060669801; stencil error +1.06e−06,
0.3 % of the half-width — small here, but the F17b AMENDMENT 1 lesson is applied at
registration so a zero-error solver reads exactly zero; control §5).
**Band = reference ± 3 × 1.090437e−04 = [1.053476994120, 1.054131256385].**

**Why phase 90° and not phase 0 — scanned before compute, F19 lesson.** At phase 0
(drive maximum) the centreline velocity is −0.022 U_ref and its discretisation error
is a near-cancellation of the temporal and spatial parts: the model's probe-error
order there is **3.6 / 7.8** with a sign change between 512² and 1024² — a gate
quantity whose own model predicts a degenerate triple, which the F19 ruling says
must not be registered as a gate. At 90° (centreline peak, +1.054 U_ref) the model
orders are **2.00 / 2.00**. The scan (8 phases) is recorded in the writing
invocation's transcript; the registered phase is 90°.

**Registered prediction: both triples `CONVERGING` with observed order p ≈ 2 (model
2.00); fine values inside both bands → PASS.**

## 5. CRITERIA

- Verdict vocabulary fixed; rule 5 reached through `grade_ladder` only (exactly one
  call node, AST-censused, grep matcher driven both ways).
- **Rule 5 limb (1), iterative:** a CENSUS over EVERY time step's final residual of
  `p` (≤ 1e−9) and `Ux` (≤ 1e−12), both correctors, against the solver's own
  tolerances (read from `fvSolution` by a control); one reading above → the level is
  NOT_CONVERGED → row NOT A RESULT. Control: one planted bad p reading and one planted
  bad Ux reading are each flagged.
- **Rule 5 limb (1), plateau analogue = PERIODICITY, measured:** at every level
  ‖U(12.25) − U(11.25)‖₂/U_ref ≤ **PERIOD_TOL = 1e−5**, else NOT_PERIODIC → NOT A
  RESULT. Registered tolerance is ≥ 10× the model's worst predicted change (4.07e−08;
  control refuses otherwise) and would flag a run started from rest (transient
  ≈ 1e−3 relative after 11 periods at decay rate νπ²/4 = 0.62 s⁻¹). Control: two
  synthetic files differing by a uniform Ux offset PLANT read back as exactly
  PLANT/U_ref; identical files read 0.0.
- **Completion, rule 4, at every level:** rc 0 (RC.txt written by the launcher in the
  solver's shell); `End`; latest + Δt > 12.25; `Time =` count == steps (fixed-Δt
  identity); U and p at 12.25 present and NEWER than the case's own `0/U` (age
  guard); **U at 11.25 present** (the periodicity check is PHYSICS_CRITICAL). Crash →
  NOT A RESULT; absent → PENDING.
- L-342 field classes declared; control drives both directions (infrastructure
  deleted → completion unchanged + cost claim refused; rc corrupted / `End` deleted /
  `11.25/U` deleted → not complete).
- Planted-zero controls through the real parser on the real artifact for both gates
  (rule 3), refusing with exit 2.
- Guards refuse and never delete; `--preflight` fires nothing (blockMesh not run).

**Measured in the writing invocation:**

| check | result |
|---|---|
| `exact_f21.py --selftest` / `python3 -O` | rc 0 / **rc 2** |
| `grade_f21.py --selftest` / `python3 -O` | rc 0, **11 controls green**, 10 s / **rc 2** |
| `assert` census (AST) over grade / exact / foam_io / build | **0 nodes; planted assert seen** |
| `grade_ladder` call nodes (AST) | **exactly 1**; grep matcher driven both ways |
| same-stencil probe reference control | exact field through the real reader: error **0.0**; planted 1.234e−03 read back as 7.753450669e−03 / U_ref (exact) |
| solver dictionaries vs registration | ν, laminar, p/U tolerances, PISO mode, endTime 12.25, writeInterval divides PERIOD and endTime, `backward`, cosine drive f = 1, A = 1, x̂, specific, all — all agree |
| `scripts/check_launcher_can_launch.py --worktree run_f21.sh` (ARM 1 + ARM 3) | **rc 0**: 0 time-dir globs, 0 bashrc sources under `set -u` |
| `scripts/check_launcher_can_launch.py --one-iteration <scratch coarse build> --solver pimpleFoam` (ARM 2) | **PASS**: rc 0, reached Time = 0.0104167 (one step). *First attempt FAILED at `timePrecision 10` — the log printed 0.01041666667 and ARM 2 compares to Δt at 1e−12; `timePrecision 12` (a naming change only) resolves it and is the registered value.* |
| `bash -n run_f21.sh` | parses |
| `run_f21.sh --preflight` | **rc 0**; instrument green; cap agrees 1500/1500; ν and endTime agree; run root reported ABSENT; blockMesh NOT run |
| `set +u` around the bashrc source | `run_f21.sh:139–142` (the F17 AMENDMENT 1 form, L-339) |

## 6. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING AND A PASSING VALUE

Through the real readers, on files in the pinned write format (pinned against real
solver output on this box, `verification/runs/ansys_verification/VMFL019/L1_30/5/U`,
parsed at selftest), **built at the fine size 512²**: the solved 256-cell 1-D error
profile prolongated piecewise-constant onto the fine grid (constant in x) and scaled
by the model's 256 → 512 E2 ratio, so the probe sees the fine level's own stencil.

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F21-1 | exact + **1×** scaled model error | 7.71323e−05 | [2.571e−05, 2.314e−04] | **inside** |
| G-F21-1 | exact + **40×** | 3.08529e−03 | same | **outside** |
| G-F21-2 | exact + **1×** | 1.053695 | [1.053477, 1.054131] | **inside** |
| G-F21-2 | exact + **40×** | 1.049457 | same | **outside** |

Honest limit: format-faithful synthetic files; the *format* is pinned against real
output, the *values* are constructed.

## 7. THE SMOKE ARM — a real solver step on a real build (cfd pre-freeze requirement, F16 lesson)

Scratch copy of the coarse level built by `build_f21.py` into the scratchpad, never
the case tree: `blockMesh` + `checkMesh` (`level=coarse n=128 cells=16384
dt=0.010416666666666666 max_non_orthogonality_deg=0 max_skewness=0`), `0/C` by
`postProcess -func writeCellCentres`, `0/U` exact at t = 0. One real `pimpleFoam`
step: **rc 0, `Time = 0.01041666667`, `End` written, `Solving for Ux` initial
residual 0.171425730435 (non-zero: the fields move), Ux final 5.2e−13 in 23
PBiCGStab iterations, p DIC-PCG 238 / 239 iterations to 9.95e−10 / 8.14e−10**,
ExecutionTime 0.29 s; the time directory holds U with 16,384 entries. Not retained,
not a measured history, not a result.

## 8. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.**

**Rate basis.** The dispatch named F18's MEASURED icoFoam rate
(`verification/campaign/F18b_TG2D_EXT_PREREGISTRATION.md` §8: 3.4 / 5.47 / 9.39 µs
per cell-step at 64² / 128² / 256², DIC-PCG iterations 75 / 143 / 257 growing ∝ N).
**A 24-step scratch probe on THIS case's coarse grid measured 10.71 µs per
cell-step** (ExecutionTime 4.21 s, 24 steps × 16,384 cells, RSS 89 MB, ≈ 0.07
core-min in the scratchpad, not retained) — **2.0× the F18 figure at 128²**, because
the p solve here takes ≈ 238 DIC-PCG iterations per corrector to reach 1e−9 from a
normalised initial residual of order 1 (the exact pressure is uniform, so every
solve starts far from its scaled tolerance) and `pimpleFoam` carries more per-step
overhead than `icoFoam`. The basis registered here is therefore **the measured
10.71 µs at 128², grown per doubling by F18's MEASURED +72 % / +75 %**:

| level | cells | steps | cell-steps | rate (µs) | projected serial s | core-min | wall |
|---|---|---|---|---|---|---|---|
| coarse | 16,384 | 1,176 | 19.3 M | 10.71 (measured, 24 steps) | 206 | 3.4 | 3.4 min |
| medium | 65,536 | 2,352 | 154.1 M | 18.42 | 2,839 | 47.3 | 47 min |
| fine | 262,144 | 4,704 | 1,233.1 M | 32.24 | 39,752 | 662.5 | 11.0 h |
| **total** | | | **1,406.5 M** | | **42,797** | **713** | **11.9 h** |

**REGISTERED CAP: 1500 core-minutes** (2.1× the estimate; the width is the admission —
PCG iteration growth beyond +75 %/doubling at 262k cells, serial, is the unknown).
**Derived dollars at $0.0513/core-h: $0.61 estimate, $1.28 at the cap — DERIVED, NOT
MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation.
**`cost_basis: derived — base rate measured on this case's coarse grid in a 24-step
scratch probe, growth per doubling from F18's measured ClockTimes; not measured on
the medium and fine levels.`**

**Sized for hours, said plainly:** the fine level is ≈ 11 h serial at the estimate;
serial was chosen over 4 ranks because no parallel-efficiency measurement exists on
this box for this solver at this size, and a 1-rank entry is what the runner can
place beside F18b and the 8-rank T3_R_ff now on the box.

**Memory floor: 1.0 GB** — 89 MB RSS measured at 16k cells; ≈ 1 kB/cell at 262k
cells is ≈ 0.3 GB (estimated, not measured); the grader's model is 1-D and
negligible. **Disk:** 49 writes × (U + p + phi) ≈ 2.1 GB at the fine level, ≈ 2.8 GB
for the ladder (274 GB free on `/`).

The cap is checked **incrementally after each level** and **projected before each
level** from the launcher's own box probe (`PROJ_SERIAL_S` = 206 / 2836 / 39710 s);
a crossing **HALTS at exit 3**, unlaunched levels stay `PENDING`, the cap is never
raised. Launcher and grader carry the same cap and refuse to start if they disagree
(measured: "CAP AGREES … 1500").

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`date -u` = 2026-08-26T21:03:51Z. `ls -d verification/runs/F21_runs` → **`No such
file or directory`** (ABSENT; `--preflight` printed the same reading). `find
cases/F21_womersley -name RC.txt -o -name 'log.*' | wc -l` → **0**; the case tree holds
no numeric directory (the templates live in `case/0/*.template`).

## 10. NEVER RUN — THE EVIDENCE

- Tracked paths enumerated with `git ls-tree -r HEAD --name-only`: **14881** at the
  writing invocation; matches for `F21|womersley`: **8, none of them this case** —
  `cases/valve/02-womersley.png` and seven files under
  `verification/runs/F9_work/womersley_probe_check/` + `womersley_followup_results.json`
  (the F9 probe check of an earlier campaign; a different case, mesh, drive and
  solver setup, not a run of this registration); matches for `F21`: **0**
  (planted control: `cases/F18b_taylor_green_ext/run_f18.sh` is in the enumeration, 1 hit).
- `verification/runs/` holds no `F21*` directory; no queue directory holds an F21 entry.

## 11. FROZEN FILES (sha256 at this freeze)

`cases/F21_womersley/exact_f21.py` d928189e58c725984afe0d3bb4a17a2491f6bc689f81f11eba383477c41be093; `cases/F21_womersley/grade_f21.py` 8a6e9102ce337d79defbe12449abea3ca4c9054083c5adfd9b74c40f037af095; `cases/F21_womersley/run_f21.sh` ad3016a0b9ce3d51bdbbcf0d6bccb999e26dfbce791dc9e51dbb657ae3f7db63; `cases/F21_womersley/build_f21.py` 1830231a823104c0b6883d014b23a5cbeb961217d55139b6d5eadb81e0114f46; `cases/F21_womersley/foam_io_f21.py` 4b4a52e8c3f996466af8e4a6a09f42aaac4b764dc6de486e4539c7338882f1af; `case/**`: 9 dictionaries and templates under `cases/F21_womersley/case/`.

## 12. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F21_womersley/run_f21.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F21_womersley/grade_f21.py --prereg-commit=<sha>`. The queue entry
`cases/F21_womersley/queue_entry_F21_WOMERSLEY.json` is **HELD in the case directory**
until the supervisor's check 1/4; the supervisor, not this lane, drops it into
`verification/queue/cfd/`.

## 13. WHAT IS NOT REGISTERED HERE

- No claim about p beyond the registered prediction; no turbulence claim; no
  Richardson-annular-effect claim beyond what the exact profile carries.
- No amendment to any standard, charter or frozen record.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
