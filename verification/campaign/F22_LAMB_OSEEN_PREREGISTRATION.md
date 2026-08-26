# F22 — PRE-REGISTRATION: 2-D decaying Lamb–Oseen vortex (icoFoam, transient, far field = the exact solution, serial), ladder 192² / 384² / 768²

**Team:** cfd. **Case id:** `F22_LAMB_OSEEN`. **Written before any compute. ZERO
CORE-MINUTES SPENT in the case tree or any run root** (a 24-step scratch smoke arm of
≈ 0.15 core-min and a one-step ARM-2 probe were run in the scratchpad and are reported
in §7; neither is a level, neither is retained, neither is a result). **Status at
freeze: ARMED — never run.** Frozen by the commit that carries this file. After first
compute the gates, thresholds, cap and labels below are **closed**; changes land only
as dated addenda that cannot alter them. Decided and recorded **`[lab-attributed]`**
on the cfd supervisor's dispatch of 2026-08-26 (batch 2 of the queue-depth
registrations; chief addenda `73eccb1b`, `7def3c6b`, `3c3ef86c`). Template: F23.

**Capability-grid cell (068c2bf0): 2D · unsteady · incompressible.**

**Lineage, stated because rule 10 requires it:** the case directory
`cases/F22_lamb_oseen/` was written by a lane killed in the fourth fleet kill
(~21:30Z) with its work uncommitted. It was **inspected, never reverted**. Kept
unchanged: `exact_f22.py`, `build_f22.py`, `foam_io_f22.py`, every template and
dictionary except `fvSolution`. Repaired: `grade_f22.py` referenced `EX.U0` (the
module defines `U_REF`) and its selftest **exited 1** on disk — a real defect, fixed
(`U_REF`, three sites) together with an `-O` refusal message that still named
`grade_f18.py`; its `--root` default now names the run root registered in §9.
`run_f22.sh`: run root renamed to `F22_LAMB_OSEEN_runs`, a run-root guard added
(F23's `refuse_if_answered`, `0/` / numeric / `processor*`), the cost projection
re-based on this invocation's own smoke arm (§8). `fvSolution`: `maxIter 5000` made
explicit on the p solver (§8, convergence risk). No gate, band, cap or label existed
before this file; nothing was struck.

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled so at registration; not a result; counts toward no challenge column; not
filmed. Its purpose: the lab's first **time-accurate, non-linear, decaying** exact
solution with a **Dirichlet far field** (F18's Taylor–Green is periodic; F21's
Womersley is linear and driven), graded through the F17b same-stencil lesson.

---

## 1. THE CASE

    ω(r, t)  = Γ / (4π ν t′) · exp(−r² / (4 ν t′)),          t′ = t + T0
    u_θ(r,t) = Γ / (2π r) · (1 − exp(−r² / (4 ν t′))),       u_r = 0
    p(r, t)  = −(Γ/2π)² / (8 ν t′) · [ (1 − e^{−η})² / η + 2 (E1(η) − E1(2η)) ],   η = r² / (4 ν t′)

| item | value |
|---|---|
| constants | Γ = 1, ν = 0.01, **T0 = 2** (virtual origin: the field is smooth at t = 0, core radius √(4νT0) = 0.2828), **T_END = 4** (t′ = 6, core radius 0.4899; peak vorticity 2.653 → **1.326291192432461**) |
| domain | square [−L, L]², **L = 2.5**, unit depth, `frontAndBack` empty; N × N × 1 cells |
| far field | **the exact solution as the boundary datum**: `U` `fixedValue` = the potential vortex Γ/(2πr) θ̂ at the mesh's own patch face centres (read from `0/C`), which equals the exact velocity there to exp(−L²/(4ν t′_end)) = **4.9e−12 relative at every time** (control in `exact_f22.py` and in the builder refuse above 1e−10); `p` `fixedFluxPressure` |
| initial field | exact u, v and p at t = 0 at the built mesh's own cell centres (`0/C`); `0/U` written **LAST** by `build_f22.py` (the age-guard datum) |
| solver | `icoFoam`, `backward` (BDF2) in time, `Gauss linear` convection and gradients, `Gauss linear orthogonal` Laplacian (non-orthogonality 0 by construction), PISO nCorrectors 2, **p DIC-PCG tolerance 1e−9 relTol 0 maxIter 5000**, U symGaussSeidel 1e−12 |
| velocity scale | U_ref = Γ/(2π r_c(0)) = **0.5626976975981913**; G-F22-1 is normalised by it |
| writes | fields at t = T_END only (`writeInterval 4`); `writePrecision 12` |

**Mesh admissibility (MESH_STANDARD §3, §8.1).** The coarse level (192²) was **BUILT
AND `checkMesh`'d** on a scratch copy by `build_f22.py` in the writing invocation:
**36,864 cells, `Mesh OK`, max non-orthogonality 0° (gate 70°), max skewness 6.8e−14
(gate 4), max aspect ratio 1.000 (advisory 1000, §3.3)** (`MESH_LINE.txt` reading:
`level=coarse n=192 cells=36864 dt=0.01 max_non_orthogonality_deg=0
max_skewness=6.8212362859e-14`). The builder enforces both hard gates at every level,
refuses a cell count other than N², and refuses a destination holding `0/` or a
numeric time directory.

## 2. THE REFERENCE IS NOT A PAPER. IT IS A SUBSTITUTION.

Rule 15 requires title-page verification of every retrieved paper; this case
retrieves none. `exact_f22.py --selftest` (rc 0, 33 s in the writing invocation;
`python3 -O` → **rc 2**) substitutes the closed forms symbolically (sympy): the
vorticity into the 2-D vorticity transport equation ω_t + u·∇ω = ν∇²ω (residual
identically **0**), the velocity's curl against ω (**0**), continuity (**0**), and the
closed-form pressure into the radial momentum balance dp/dr = u_θ²/r (**0**).
**Planted control:** t′ → 1.1 t′ inside the exponential gives a **non-zero** residual
(refuses otherwise). The far-field datum is checked numerically against the exact
velocity at T_END at four boundary points (max 4.9e−12 relative).

## 3. THE LADDER — THREE LEVELS (§9.1), `dim = 2`, r = 2 in h AND Δt

| level | N × N | cells | h = 2L/N | steps | Δt | cells per core radius r_c(T_END) = 0.49 | Co (exact max‖u‖ Δt/h) |
|---|---|---|---|---|---|---|---|
| coarse | 192 × 192 | 36,864 | 0.026042 | 400 | 0.01 | 18.8 | 0.080 |
| medium | 384 × 384 | 147,456 | 0.013021 | 800 | 0.005 | 37.6 | 0.080 |
| fine | 768 × 768 | 589,824 | 0.006510 | 1,600 | 0.0025 | 75.2 | 0.080 |

r = 2.000 in h and in Δt (control refuses otherwise); **N even so the vortex centre
sits on a vertex and the four peak cells sit at (±h/2, ±h/2) at every level — the
peak-vorticity stencil is self-similar across the ladder** (this is what makes G-F22-2
a clean triple; §4). The solver's own face-flux Courant number at the coarse level
measured **0.184 max** (§7).

**DECOMPOSITION SEED (required field): `none`.** Every level serial on **1 rank**;
`decomposePar` not invoked; no partition, no RNG. (The dispatch allowed one rank; the
fine level is ≈ 8 h serial at the estimate, §8.)

## 4. THE GATES AND THEIR BANDS — DERIVED FROM THE DISCRETISATION

**One declared parameter, `BAND_FACTOR = 3`**, applied to predictions computed by a
discretisation model of the scheme. Declared now; not fitted; not revisable.

**The model (`exact_f22.discrete_error`).** The solver's own uniform-Cartesian
stencils (Gauss linear convection, orthogonal Laplacian, Gauss linear pressure
gradient, Rhie–Chow interpolated flux, BDF2 with the Euler-implicit first step, the
far-field Dirichlet datum) are evaluated on the exact field at every step, giving the
truncation residuals; the leading-order error obeys the **linearised** discrete
equations forced by those residuals, integrated with the same BDF2 step (diffusion and
projection implicit by one sparse LU, linearised convection explicit AB2), on the two
grids **48² × 100 and 96² × 200** of the ladder's own family; each ladder level is
**extrapolated** from 96² with the model's own observed orders (control requires them
in [1.7, 2.3]; control requires a non-zero forcing residual on both grids; control
requires the predicted peak error sign-stable across the ladder). Measured model
orders: **2.0200 (E2), 1.7982 (peak vorticity)**.

**Cross-check of the extrapolation, disclosed:** the model was integrated ONCE at the
coarse level's own grid (192² × 400; 344 s and ≈ 5.7 GB RSS on a loaded box; NOT part
of the instrument): E2 **5.848e−05** against the extrapolated **5.788e−05** (1.0 %
apart); peak error **1.235e−03** against the extrapolated **1.376e−03** (the 96² → 192²
order is 1.954, so the 1.798 extrapolation OVER-predicts the fine-level peak error and
the band below is conservative in that direction).

**Omissions, covered by the factor 3:** the nonlinear feedback of the error on itself;
PISO's non-iterated splitting; the pressure-error boundary datum (zero-gradient in the
model against `fixedFluxPressure` in the solver, confined to the boundary ring where
the velocity is 5 % of the core value); solver tolerances; round-off.

| level | E2 predicted | peak-vorticity error predicted (solver) | stencil under-read of the exact peak | raw peak predicted |
|---|---|---|---|---|
| coarse | 5.787579e−05 | +1.375942e−03 | −3.739334e−03 | 1.323927800 |
| medium | 1.426939e−05 | +3.956161e−04 | −9.364021e−04 | 1.325750406 |
| fine | **3.518148e−06** | **+1.137491e−04** | **−2.341987e−04** | **1.326170743** |

**The model's own triples, run through `scripts/roache_triple.py` at registration
(the F19 rule: a DEGENERATE prediction is a registration defect):**

| series | state | observed order (dim 2) | GCI at Fs 1.25 | fine value vs band |
|---|---|---|---|---|
| E2 prediction (coarse/medium/fine) | **CONVERGING** | **2.0200** | 4.398e−06 absolute (the % figure, 125 %, is relative to a value converging to 0 and is not the reading) | inside → PASS |
| raw peak vorticity prediction (stencil + solver) | **CONVERGING** | **2.1164** | 0.0119 % = 1.575e−04 absolute | inside → PASS |

**G-F22-1 — E2 of the velocity field at T_END**
E2 = √(mean over every cell |U_h − U_exact(x_c, T_END)|²) / U_ref, both components,
at the mesh's own cell centres from `0/C`. Prediction at fine: **3.518148e−06**.
**Band = [prediction/3, prediction×3] = [1.172716e−06, 1.055445e−05].**

**G-F22-2 — peak vorticity at T_END.** Max over interior cells of the grader's own
central-difference curl of the cell-centred U. **Reference = the SAME stencil applied
to the exact velocity sampled at the fine level's own cell centres =
1.3260569937248692** (pointwise exact Γ/(4πνt′) = 1.326291192432461; the stencil
under-reads the Gaussian peak by 2.342e−04 and that is removed from the reference —
the F17b AMENDMENT 1 lesson applied at registration; control: the exact field written
in the real format and read through the real reader returns error **0.0**, and a
planted Ux ramp of curl −PLANT/(2L) is read back as **−2.468e−04** exactly).
**Band = reference ± 3 × 1.137491e−04 = [1.325715747, 1.326398241].**

**Why G-F22-2 is peak vorticity and not the dispatch's peak u_θ, decided
`[lab-attributed]`.** The dispatch named "peak u_θ (or circulation within r₁)". The
max of |U| over cells samples the peak ring r = 0.549 at cell centres whose offset from
the ring is **not self-similar across levels** (the sampling error, ≤ |u″| h²/8 ≈ 5.8e−5
/ 1.5e−5 / 3.7e−6 at the three levels, is erratic and of the SAME SIZE as the model's
solver error there, 6.6e−5 / 1.8e−5 / 5.1e−6 — measured on the model: the 48² → 96²
sampling errors are −8.9e−5 and −1.4e−6); a raw-value triple of that quantity would
carry a non-physical order. Circulation within r₁ integrates the error curl over a
disc whose staircase boundary dominates the (tiny) solver contribution. Peak vorticity
at a vertex-centred stencil is self-similar, its raw triple is CONVERGING at p ≈ 2.1 on
the model, and it is the classical Lamb–Oseen diagnostic. The dead lane's choice was
sound and is kept.

**Registered prediction: both triples CONVERGING with observed order p ≈ 2 (model
2.02 / 2.12), fine values inside both bands → PASS × 2.**

## 5. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
  PENDING, and nothing else.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node (`grade_f22.py:585`
  at freeze), AST-censused; the text matcher driven both ways.
- **No plateau, said rather than hidden:** the graded quantities are values at the
  fixed instant T_END of a decaying transient; `plateau_states=None`, recorded ABSENT
  (VERIFICATION_CHARTER §9), never as a pass.
- **Rule 5 limb (1) — census over EVERY time step's final p residual** (both
  correctors) against the solver's own tolerance 1e−9 (read from `fvSolution` by a
  control); one reading above → NOT_CONVERGED → row NOT A RESULT.
- **Completion (rule 4):** `RC.txt` = 0 (written by the launcher in the solver's own
  shell); `End`; latest + Δt > T_END; **`Time =` count == T_END/Δt** (fixed-Δt
  identity); `U` and `p` at `4/` present and **newer than the case's own `0/U`** (age
  guard). Crash → NOT A RESULT; absent → PENDING.
- **L-342 field classes** declared in the grader; driven both ways at selftest (infra
  deleted → completion unchanged + cost claim refused; rc corrupted / `End` deleted →
  the level flips).
- **Planted-zero controls (rule 3)** into copies of the real `U` file, read back with
  the real parser: δ = 1.234e−3 on Ux must move E2 to the value predicted in memory
  (1e−14); a Ux ramp of curl −δ/(2L) must move the peak vorticity by exactly that
  (1e−10); a plant that does not move a reading refuses.
- **`assert` census: ZERO** across `grade_f22.py`, `exact_f22.py`, `foam_io_f22.py`,
  `build_f22.py`; planted assert seen. **Hard `-O` refusal at entry** — measured:
  `exact_f22.py --selftest` rc 0 / `-O` rc 2; `grade_f22.py --selftest` **rc 0 (9
  controls, 48 s, 1.06 GB RSS)** / `-O` **rc 2**.
- **Success messages print INSIDE the passing branch.**
- **Guards.** Launcher and builder **REFUSE** a pre-existing `0/`, numeric time or
  `processor*` directory in the run root and in each level directory; neither deletes;
  the builder refuses a destination inside the tracked case tree.
- **`set -u` dropped around the OpenFOAM bashrc source only** (L-339;
  `run_f22.sh:154–157`); `scripts/check_launcher_can_launch.py --worktree
  cases/F22_lamb_oseen/run_f22.sh` → **rc 0** (0 time-directory globs, 0 bashrc
  sources under `set -u`); ARM 2 `--one-iteration` on the scratch coarse build →
  **PASS (rc 0, reached Time = 0.01)**.
- **`--preflight` fires nothing** (no blockMesh, no build); measured: **rc 0**,
  instrument green, cap agrees 1100/1100, ν and endTime agree, run root reported
  **ABSENT**; no-argument invocation rc 1. The launcher prints the grade command and
  never grades.
- **Dictionaries cross-checked** at every grader entry and by the launcher (ν, p
  tolerance, endTime 4, `backward`, `icoFoam`, far-field `fixedValue`/
  `fixedFluxPressure`, box half-width L against `blockMeshDict.template`).

## 6. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Through the real readers on files in the pinned write format (pinned against real
solver output on this box, `verification/runs/ansys_verification/VMFL019/L1_30/5/U`,
parsed at selftest), **built at the fine size 768²**: the 96² model error field
prolongated piecewise-constant and scaled by the model's 96² → 768² E2 ratio; for the
peak, a Gaussian vorticity bump of the model's predicted peak error:

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F22-1 | exact(T) + 1× scaled model error | 3.51815e−06 | [1.173e−06, 1.055e−05] | **inside** |
| G-F22-1 | exact(T) + 40× | 1.40726e−04 | same | **outside** |
| G-F22-2 | exact(T) + 1× bump | 1.326171 | [1.325716, 1.326398] | **inside** |
| G-F22-2 | exact(T) + 40× bump | 1.330606 | same | **outside** |

**Honest limit:** format-faithful synthetic files; the *format* is pinned, the
*values* are the model's.

## 7. THE SMOKE ARM — real solver steps on the real build (NOT a level; not retained; not a result)

Scratch copy of the **coarse level** built by `build_f22.py` into the scratchpad (never
the case tree), `endTime` cut to 0.24 in the scratch copy only: **24 real `icoFoam`
steps, rc 0, `Time = 0.24` written with 36,864 entries, ExecutionTime 8.85 s /
ClockTime 9 s, RSS 66 MB**; `Solving for Ux` initial residual 1.2e−04 (non-zero: the
fields move), p DIC-PCG **345 / 330 iterations on the first step, 256 at step 24**,
every final p residual ≤ 9.8e−10 (below the 1e−9 tolerance the census gates on);
face-flux Courant max 0.184. Box load at the probe: **26.6 on 16 cores** (contended).
≈ 0.15 core-min including blockMesh/checkMesh/postProcess. ARM 2 of the launcher
checker (one step on a second fresh scratch build): PASS.

## 8. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** Ranks = 1 at every level.

**Rate basis — the dispatch named two; this registration uses F18's icoFoam basis,
re-based on this case, and says why.** F18 (`F18b_TG2D_EXT_PREREGISTRATION.md` §8) is
the SAME solver, the SAME p solver (DIC-PCG, 1e−9, relTol 0) and the same 2-D
Cartesian family, with a MEASURED per-doubling growth (+61 % / +72 % at 64² → 128² →
256², DIC-PCG iterations growing with N per side; F18b registered +75 % / +80 % for
the next doublings). F21's 10.71 µs at 128² is `pimpleFoam` with its own per-step
overhead and is disclosed as a comparison, not used. **The base rate is MEASURED on
THIS case's coarse grid: 10.00 µs per cell-step** (§7: 8.85 s / (36,864 × 24), on a
box at load 26.6 — contention can only inflate it, so the estimate is conservative
in that direction; F18 measured 9.39 µs at 256²), grown **+75 % then +80 %** per
doubling of N per side:

| level | cells | steps | cell-steps | rate (µs) | projected serial s | core-min | wall |
|---|---|---|---|---|---|---|---|
| coarse | 36,864 | 400 | 14.75 M | 10.00 (measured, 24 steps) | 147 | 2.5 | 2.5 min |
| medium | 147,456 | 800 | 117.96 M | 17.5 | 2,064 | 34.4 | 34 min |
| fine | 589,824 | 1,600 | 943.72 M | 31.5 | 29,727 | **495.5** | **8.3 h** |
| **total** | | | **1,076.4 M** | | **31,938** | **532.3** | **≈ 8.9 h** |

At the asymptotic +100 %/doubling (PCG iterations ∝ N per side) the fine level is
40 µs → 37,749 s = **629 core-min**, total ≈ 666. **REGISTERED CAP: 1,100
core-minutes** (2.07× the estimate, 1.65× the asymptotic bound; the width is the
admission — DIC-PCG on 590k cells at 1e−9, relTol 0, serial, on a shared box, is the
unknown). **Derived dollars at $0.0513/core-h: $0.46 estimate, $0.57 asymptotic, $0.94
at the cap — DERIVED, NOT MEASURED, reported-by-owner rate** (`COMPUTE_BUDGET_CHARTER.md`
§5). Under the $25 pre-authorisation. **`cost_basis: derived — base rate measured on
this case's coarse grid in a 24-step scratch smoke arm, growth per doubling from
F18's measured ClockTimes as registered by F18b; not measured on the medium and fine
levels; reported-by-owner rate.`**

**Sized for hours, said plainly:** the fine level is ≈ 8.3 h serial at the estimate
(≈ 10.5 h asymptotic). Serial was chosen because no parallel-efficiency measurement
exists on this box for icoFoam/DIC-PCG at this size and the F18 growth basis is a
serial reading.

**Convergence risk, registered:** DIC-PCG took 345 iterations per p solve at 192²
and the count grows ∝ N per side, so ≈ 1,400 is expected at 768². OpenFOAM's default
`maxIter 1000` would have truncated those solves silently above the 1e−9 tolerance
and the residual census would then read every fine-level step NOT_CONVERGED → NOT A
RESULT by construction; **`maxIter 5000` is therefore explicit in `fvSolution`** (a
pre-freeze case-definition choice, not a gate). If a step still ends above 1e−9 the
level is NOT A RESULT by rule 5 limb 1 and stays so.

Cap checked **incrementally after each level** and **projected before each level**
from the launcher's own box probe (`PROJ_SERIAL_S` = 147 / 2064 / 29727 s, scaled up
when fewer than 1 core is free); a crossing **HALTS at exit 3**; unlaunched levels
stay `PENDING`; launcher and grader refuse to start if their caps disagree (measured:
"CAP AGREES … 1100").

**Memory floor: 2.0 GB** — 66 MB RSS measured at 36,864 cells (≈ 1.8 kB/cell → ≈ 1.1 GB
at 590k cells, estimated, not measured); the grader's model integration is **1.06 GB
RSS measured**. **Disk:** fields at `endTime` only: ≈ 0.05 GB for the fine level
(271 GB free on `/`).

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`date -u` = **2026-08-26T22:21:28Z**. `ls -d
/home/ubuntu/Certonomous/verification/runs/F22_LAMB_OSEEN_runs` → **`No such file or
directory`** (ABSENT; `--preflight` printed the same reading). `find
cases/F22_lamb_oseen -name RC.txt -o -name 'log.*' | wc -l` → **0**; the case tree
holds no numeric directory (the templates live in `case/0/*.template`).

## 10. NEVER RUN — THE EVIDENCE (L-337 controls first)

- `git ls-tree -r HEAD --name-only`: **15,072** tracked paths at the writing
  invocation; **planted control: the known `cases/F20_ISENTROPIC_VORTEX/` paths are
  returned (15)**; matches for `F22|lamb_oseen|LAMB_OSEEN`: **0**.
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (536 entries) — **1
  substring hit, `study-b52-f223a4`, not this case**; `/home/ubuntu/closure-data`
  (22) **0**; `/home/ubuntu/closure-challenge-benchmark` (7) **0**. `verification/runs/`
  holds no `F22*` directory (`F2_runs` is a different campaign).

## 11. FROZEN FILES (sha256 at this freeze)

    cases/F22_lamb_oseen/exact_f22.py    f13ff85f9b1cfc67afdb49ecf032d9f2f8113063b610a6f6c5030cbb34b6f9ca
    cases/F22_lamb_oseen/grade_f22.py    123fbac71c8259eda7b02ffe022ff404f41a40eb6889ff776472afb9e66680e8
    cases/F22_lamb_oseen/build_f22.py    0a9858a9299d1e3ada5261a707393edcc06defb8f75f8bdbf2dcc0ab0f05b179
    cases/F22_lamb_oseen/foam_io_f22.py  d3a5601d75ace5fb1ae817ab9ced4c3840f1e86b92c8df0816eb4b6edd4849c7
    cases/F22_lamb_oseen/run_f22.sh      d26e14dd718eb643d12d7cfa1c9513dac8927e420640849e4e556c374183e4f5
    cases/F22_lamb_oseen/case/0/{U.template,p.template}
    cases/F22_lamb_oseen/case/constant/transportProperties
    cases/F22_lamb_oseen/case/system/{blockMeshDict.template,controlDict.template,fvSchemes,fvSolution}
    verification/campaign/F22_LAMB_OSEEN_PREREGISTRATION.md   (this file)

## 12. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F22_lamb_oseen/run_f22.sh --prereg-commit=<this file's freeze sha>

Serial, 1 rank, all levels; grading is a separate invocation
`python3 cases/F22_lamb_oseen/grade_f22.py --prereg-commit=<sha>`. The queue entry
`cases/F22_lamb_oseen/queue_entry_F22_LAMB_OSEEN.json` is **HELD in the case
directory** until the supervisor's check 1/4; the supervisor, not this lane, moves it
into `verification/queue/cfd/`; enqueueing is not authorisation.

## 13. WHAT IS **NOT** REGISTERED HERE

- No claim about the pressure field beyond its role as the initial condition and the
  model's boundary datum; no claim about the far-field ring beyond the 4.9e−12 datum
  error; no claim about peak u_θ or circulation (the grader prints the pointwise exact
  peak vorticity beside the reference, ungated).
- No amendment to any standard, charter or frozen record.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
