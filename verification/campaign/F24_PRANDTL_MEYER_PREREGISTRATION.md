# F24 — PRE-REGISTRATION: Prandtl–Meyer expansion around a convex corner (rhoCentralFoam Kurganov/vanLeer, M₁ = 2, θ = 15°, inviscid, 4 ranks), ladder h = 1/150 / 1/300 / 1/600

**Team:** cfd. **Case id:** `F24_PRANDTL_MEYER`. **Written before any compute. ZERO
CORE-MINUTES SPENT in the case tree or any run root** (a three-grid sub-ladder of
≈ 1.08 core-min, a 10-step 4-rank smoke arm and a one-step ARM-2 probe were run in
the scratchpad and are reported in §4 and §7; none is a level, none is retained,
none is a result). **Status at freeze: ARMED — never run.** Frozen by the commit
that carries this file. After first compute the gates, thresholds, cap and labels
below are **closed**; changes land only as dated addenda that cannot alter them.
Decided and recorded **`[lab-attributed]`** on the cfd supervisor's dispatch of
2026-08-26 (batch 2; chief addenda `73eccb1b`, `7def3c6b`, `3c3ef86c`). Template: F23.

**Capability-grid cell (068c2bf0): 2D · steady · supersonic.**

**Lineage, stated because rule 10 requires it:** `cases/F24_PRANDTL_MEYER/` was
written by a lane killed in the fourth fleet kill (~21:30Z) with its work
uncommitted and NO launcher and NO pre-registration. It was **inspected, never
reverted**. Kept unchanged: `build_f24.py`, `foam_io_f24.py`, every template and
dictionary (M₁ = 2, θ = 15°, the two-block sheared mesh, the boundary types, 4
ranks, endTime 4, Δt/h = 0.04 — all sound, §1). Kept from `exact_f24.py`: the
closed forms and their controls; **rewritten**: its band derivation rested on two
PLACEHOLDER probe constants (1e−3 / 5e−4, never measured) — replaced by a measured
three-grid sub-ladder whose triples are run through `roache_triple.py` and whose
states ADMIT each gate's mode (§4). Kept from `grade_f24.py`: readers, plateau
limbs, completion, cost claim, L-342 and AST controls; **repaired**: its Class-C
ramp control was too small to trip the trend limb and the selftest **exited 2 on
disk**; **restructured**: three quantities in registered modes, the plateau made a
property of the level, the fan-line gate on the window-mean field, and the grader
no longer creates the run root to write its JSON. `run_f24.sh` is new (F23 pattern).

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3),
labelled so at registration; not a result; counts toward no challenge column; not
filmed. Its purpose: the lab's first supersonic **expansion** (F15 is a shock
reflection, F19 a shock tube, F20 a smooth vortex), the first ladder on a sheared
two-block mesh, and the first registration whose gate MODES are admitted by a
sub-ladder triple rather than chosen.

---

## 1. THE CASE

    ν(M) = √((γ+1)/(γ−1)) atan √((γ−1)/(γ+1)(M²−1)) − atan √(M²−1)
    ν(M₂) = ν(M₁) + θ  →  M₂ = 2.598446326990895;  p₂/p₁ = 0.393067794609090;  T₂/T₁ = 0.765832090572358
    fan (centred simple wave): on the ray at polar angle φ from the corner, μ(M) − (ν(M) − ν(M₁)) = φ,
    head ray φ = μ₁ = 30°, tail ray φ = μ₂ − θ = 7.634°; p, T isentropic in M; flow direction −(ν(M) − ν(M₁))

| item | value |
|---|---|
| gas | nondimensional perfect gas exactly as F19/F20: R = 1 (`molWeight` = 1e3 N_A k = 8314.47006650545), γ = 1.4 (`Cp` 3.5), `Tref` = `Hsref` = `Hf` = 0, **μ = 0** (inviscid) |
| state 1 | p₁ = T₁ = ρ₁ = 1, c₁ = √1.4, U₁ = (2c₁, 0, 0) = (2.3664, 0, 0), everywhere at t = 0 (the corner is the only disturbance) |
| geometry | block A: x ∈ [−0.5, 0] × y ∈ [0, 1], square cells h × h; block B: x ∈ [0, 1.5], bottom = the deflected wall y = −x tan θ, top = the parallel line y = 1 − x tan θ — **every cell of B is the same parallelogram** (h wide, h tall, 15° shear), so the ladder is geometrically similar at every level; z one cell, `empty` |
| patches | `inlet` (x = −0.5) and `topA` (y = 1, x < 0): supersonic inflow / undisturbed tangential freestream, `fixedValue` state 1; `outlet` (x = 1.5) and `topB` (the sloped top): supersonic outflow (U·n = \|U\| sin(θ + θ_local) ≥ 0), `zeroGradient`; `wallUp`, `wallDown`: `slip` (inviscid), p, T `zeroGradient`; `frontAndBack`: **the ONLY `empty` pair** |
| F15 / F16 lessons applied | F16's `empty` on ±x removed the solved x-component (F16b prereg §1, RESULTS): here `empty` is declared on ±z only — the grader's dictionary control counts the `empty` declarations in `blockMeshDict.template` and the three `0/*.template` files and refuses unless each is exactly `[frontAndBack]`; F15's boundary types (fixedValue supersonic inflow, zeroGradient outflow, all four front/back faces of BOTH blocks listed under `frontAndBack`) are followed |
| solver | `rhoCentralFoam`, `fluxScheme Kurganov`, `reconstruct(rho|U|T) vanLeer/vanLeerV/vanLeer`, `Euler` explicit, `adjustTimeStep no`, **fixed Δt with Δt/h = 0.04** (solver-reported Courant 0.132–0.137 at every grid, §4/§7; ceiling 0.35), time-marched to **endTime 4** (4.7 flow-through times of the 2-unit domain at u₁), checkpoints every 0.1 → **40** |
| initial field | state 1 at the mesh's own cell centres from `0/C`; `0/U` written **LAST** by `build_f24.py` (the age-guard datum) |
| ranks | **4 at every level**, `decomposePar` `simple n (4 1 1)` (bands along x), **never reconstructed**: the grader reads `processor*/` |

**Mesh admissibility (MESH_STANDARD §3, §8.1).** The coarse level (h = 1/150) was
**BUILT AND `checkMesh`'d** on a scratch copy by `build_f24.py` in the writing
invocation: **45,000 cells (75 + 225) × 150, `Mesh OK`, max non-orthogonality
15.0000° (gate 70°; the sheared block, uniform), max skewness 0.268 (gate 4), max
aspect ratio 1.268 (advisory 1000, §3.3)**; `decomposePar` → 4 × 11,250 cells. The
builder enforces both hard gates at every level, refuses a cell count other than
2N², and refuses a destination holding `0/`, a numeric time or `processor*`.

## 2. THE REFERENCE IS NOT A PAPER. IT IS A SUBSTITUTION.

Rule 15 requires title-page verification of every retrieved paper; this case
retrieves none. `exact_f24.py --selftest` (rc 0; `python3 -O` → **rc 2**): the
closed-form ν(M) is checked against its defining integral ∫√(M²−1)/(1+(γ−1)/2 M²)
dM/M by adaptive quadrature at four Mach numbers (1e−11) and ν(M₂) − ν(M₁) = θ to
1e−12; the isentropic ratios re-derive from T₀ = const (1e−14); the fan field is
continuous with state 1 at the head ray and state 2 at the tail ray, satisfies the
ray relation to **6.7e−16** on 50 rays, M increases monotonically through the fan,
and the flow direction is −(ν(M) − ν(M₁)). **Planted control:** γ → 1.1 γ in the
closed form only breaks the quadrature identity (refuses otherwise).

## 3. THE LADDER — THREE LEVELS (§9.1), `dim = 2`, r = 2 in h AND Δt

| level | h = 1/N | cells (2N²) | steps to t = 4 | Δt | cells per rank | box cells (region 2, 0.4 × 0.25) | line cells (column at x = 1 + h/2) |
|---|---|---|---|---|---|---|---|
| coarse | 1/150 | 45,000 | 15,000 | 2.667e−4 | 11,250 | ≈ 2,300 | 150 |
| medium | 1/300 | 180,000 | 30,000 | 1.333e−4 | 45,000 | ≈ 9,300 | 300 |
| fine | 1/600 | 720,000 | 60,000 | 6.667e−5 | 180,000 | ≈ 37,000 | 600 |

r = 2.000 in h and in Δt (control refuses otherwise); Δt/h = 0.04 at every level
(control). **DECOMPOSITION SEED (required field): `none`** — `simple` geometric
decomposition from `system/decomposeParDict`, deterministic, no RNG; 4 subdomains at
every level (one method for the whole ladder, so the levels differ only in mesh —
the F15 AMENDMENT 1 rule).

## 4. THE GATES, THEIR MODES AND THEIR BANDS — FROM THE REAL SCHEME ON A SUB-LADDER, DISCLOSED

**The model.** F17/F20/F22 derived bands from a re-implementation of the solver's
stencils. A 2-D Kurganov/vanLeer re-implementation on a two-block sheared mesh was
not affordable in this registration, so the "model" is **the real scheme on three
SUB-LADDER grids that are not levels of the ladder — h = 1/16, 1/32, 1/64 (512 /
2,048 / 8,192 cells)** — built by `build_f24.py --scratch N` (which refuses a
registered N), run **serially** to the registered endTime with the registered
dictionaries in the scratchpad (ClockTime **2 / 8 / 55 s = 1.08 core-min**, box load
26 → 25 on 16 cores; not retained; not a level), and read by the grader's own
readers with the grader's own plateau-window mean (last 12 of 40 checkpoints).
**Every quantity's sub-ladder triple was run through `scripts/roache_triple.py` at
registration (the F19 rule), and the triple's state ADMITS the gate mode** — a
control in `exact_f24.py` re-derives the admitted modes through `roache_triple` and
refuses a registered mode the triple does not admit (CONVERGING admits only
GATED-EXTRAPOLATED; anything else admits only GATED-ABSOLUTE or REPORTED-NOT-GATED);
the derivation is shown able to say no (a planted equal-increment series) and yes (a
planted power law).

| quantity (window mean) | 1/16 | 1/32 | 1/64 | sub-ladder triple (`roache_triple`, dim 2) | registered mode |
|---|---|---|---|---|---|
| p₂/p₁ box mean (exact 0.393067795) | 0.387170 (err −5.90e−3; 28 box cells) | 0.393349 (+2.81e−4) | 0.393197 (+1.29e−4) | **OSCILLATORY** (sign change at the 28-cell 1/16 box, then decreasing) | **GATED-ABSOLUTE** |
| M box mean (exact 2.598446) | 2.589250 (−9.20e−3) | 2.583220 (−1.52e−2) | 2.590399 (−8.05e−3) | **OSCILLATORY** (no trend; the entropy error through the captured fan and the slip wall dominates M — 60× the p error) | **REPORTED-NOT-GATED** |
| fan-line L2 of p on the window-mean field (→ 0) | 3.395e−2 | 1.854e−2 | 9.981e−3 | **CONVERGING, order 0.848** (1/32 → 1/64: 0.894) | **GATED-EXTRAPOLATED** |

**One declared parameter, `BAND_FACTOR = 3`.** Declared now; not fitted; not revisable.

**G-F24-1 — p₂/p₁ in region 2.** Volume-weighted box mean of p/p₁ over the cells
with x ∈ [0.9, 1.3] and wall-normal distance n ∈ [0, 0.25] (the tail ray is ≥ 0.139
further out over the whole box — control), the **plateau-window mean** over the
last 12 checkpoints. **Reference = exact p₂/p₁ = 0.393067794609090. ABSOLUTE band =
reference ± 3 × the finest sub-ladder error (1.2927e−4) = [0.392679994, 0.393455596].
NO ORDER CLAIM and no extrapolation:** the sub-ladder triple is OSCILLATORY, so the
registration predicts the band verdict only; **rule 5 may return NOT A RESULT on
the ladder triple and that outcome is registered as possible, not as a failure of
the case.** (The dispatch named "Mach number (or p₂/p₁)"; p is the quantity whose
region-2 error is set by the wave structure and converged 60× better than M on the
sub-ladder, so p₂/p₁ is gated and M is reported.)

**G-F24-2 — L2 error of p along a line crossing the fan.** The one column of cells
at x = 1 + h/2 (block B has vertical grid lines, so every level has exactly N cells
there, from the wall y = −0.268 through the tail ray y = 0.134 and the head ray
y = 0.577 to the sloped top y = 0.732 — the whole fan, inside the domain; count ≠ N
refuses), E = √(Σ_j V_j (p_j − p_exact(x_j, y_j))² / Σ_j V_j) / p₁ with p_exact the
centred simple-wave field of §1 at the mesh's own cell centres, **evaluated on the
WINDOW-MEAN p field** (the captured fan edges oscillate checkpoint to checkpoint at
±1.7e−4 of p₁ on the 1/64 grid — the per-checkpoint series is printed with its
std, ungated). Prediction at fine, extrapolated from 1/64 with the observed order
0.894 (clamped to [0.5, 2]): **1.350935e−03**. **Band = [prediction/3, prediction×3]
= [4.503115e−04, 4.052804e−03]. Registered order claim: p ≈ 0.9** (the fan's head
and tail are kinks in p that a limited second-order scheme captures at first order;
the corner is a singularity of the exact field). The extrapolation spans 9.4× in h
from three coarse grids; that is what the factor 3 admits.

**R-F24-M — box-mean Mach number in region 2, REPORTED-NOT-GATED.** Values at every
level, the ladder triple and its order are printed beside the exact M₂ =
2.598446326990895; its reader carries a planted-zero control (rule 3); **no verdict
is issued and nothing of it reaches rule 5.**

**Same-field control on the line reader (the F17b lesson):** the exact fan field
written in the pinned format and read through the real reader returns error
**exactly 0.0**; exact + a uniform offset of the predicted fine error returns exactly
that error (1.3509345e−03).

**Registered prediction:** G-F24-1 fine value inside its absolute band (band verdict
PASS), triple state not predicted; G-F24-2 CONVERGING with observed order ≈ 0.9 and
fine value inside its band → PASS; R-F24-M reported. **The two gates rest on
different physics** (region-2 pressure level; the fan structure), and the reported
Mach number carries the entropy channel.

## 5. CRITERIA

- **Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
  PENDING, and nothing else; the reported quantity carries **no** verdict.
- **Rule 5 through `grade_ladder` ONLY** — exactly one call node (`grade_f24.py:905`
  at freeze), AST-censused; the text matcher driven both ways.
- **The plateau is the LEVEL's** (rule 5 limb 1, "any level not plateaued → NOT A
  RESULT"), carried by the box-mean p/p₁ series: **(i) Class C** (40 checkpoints; min
  20; window 12 = t 2.9 … 4.0; relative trend 3e−4; half-window split 1.5e−4;
  variance ratio [0.1, 10]; element 4 exits) — the 1/64 sub-ladder grid read drift
  2.5e−5 and split 9.3e−6 (10× inside), the 1/32 grid failed the split (2.35e−4) and
  is **registered as the risk**: the coarse level is 2.3× finer than 1/64; **(ii) a
  residual**: max over box cells |p_k − p_{k−1}|/p₁ between the last two checkpoints
  ≤ 5e−3 (sub-ladder: PLATEAUED at every grid); **(iii) a stability census**: every
  step's solver-reported max Courant ≤ 0.35, line count == steps, nan/`FOAM FATAL`
  refusing (explicit inviscid `rhoCentralFoam` has no iterative residual: F15/F19/F20
  form). (i)+(ii) enter `grade_ladder` as `plateau_states`, (iii) as
  `iterative_states`, for every quantity of that level. Each limb is driven both ways
  at selftest (flat / ramp / step / 5-sample series; small / large residual; Courant
  0.41; nan).
- **Completion (rule 4):** `RC.txt` = 0 (written by the launcher in the shell that
  ran `mpirun`); `End`; latest + Δt > 4; **`Time =` count == registered steps**;
  `rho`, `U`, `p`, `T` at `4/` in **every one of the 4 processor directories**, each
  **newer than the serial `0/U`**; 40 checkpoints with p, T, U in every rank
  (refused otherwise). Crash → NOT A RESULT; absent → PENDING.
- **L-342 field classes** declared; driven both ways at selftest (infra deleted →
  completion unchanged + cost claim refused; rc corrupted / `End` deleted / a missing
  rank → the level flips).
- **Planted-zero controls (rule 3)** into copies of the real processor files, read
  back with the real parsers: δ = 1.234e−3 on p in every rank moves the box mean by
  exactly δ/p₁ (1e−13); the same δ on every averaged checkpoint moves the fan-line
  error to the value computed in memory (1e−13); a Ux offset moves the reported Mach
  number to the value computed in memory; a plant that does not move a reading refuses.
- **`assert` census: ZERO** across `grade_f24.py`, `exact_f24.py`, `foam_io_f24.py`,
  `build_f24.py`; planted assert seen. **Hard `-O` refusal at entry** — measured:
  `exact_f24.py --selftest` rc 0 / `-O` rc 2; `grade_f24.py --selftest` **rc 0 (11
  controls, 1.3 s)** / `-O` **rc 2**.
- **Success messages print INSIDE the passing branch.** The grader **creates no run
  root**: a grade against an absent root prints PENDING × 2 + REPORTED and writes
  nothing (measured: rc 0, root still absent).
- **Guards.** Launcher and builder **REFUSE** a pre-existing `0/`, numeric time or
  `processor*` directory in the run root and in each level directory; neither
  deletes; the builder refuses a destination inside the tracked case tree and
  refuses to build a registered level under `--scratch`.
- **`set -u` dropped around the OpenFOAM bashrc source only** (L-339;
  `run_f24.sh:176–179`); `scripts/check_launcher_can_launch.py --worktree
  cases/F24_PRANDTL_MEYER/run_f24.sh` → **rc 0** (0 time-directory globs, 0 bashrc
  sources under `set -u`); ARM 2 `--one-iteration` on a fresh scratch coarse build →
  **PASS (rc 0, reached Time = 0.000266667)**.
- **`--preflight` fires nothing** (no blockMesh, no build, no decomposePar);
  measured: **rc 0**, instrument green, cap agrees 1450/1450, molWeight/Cp/ranks/
  Kurganov/vanLeer/endTime/writeInterval agree, run root reported **ABSENT**;
  no-argument invocation rc 1. The launcher prints the grade command and never grades.
- **Dictionaries cross-checked** at every grader entry and by the launcher (R = 1,
  γ = 1.4, μ = 0, Kurganov, the three vanLeer reconstructions, Euler, endTime 4,
  writeInterval 0.1, `adjustTimeStep no`, `rhoCentralFoam`, `numberOfSubdomains 4`,
  slip walls, fixedValue inflow, zeroGradient outflow, `empty` on `frontAndBack` only).

## 6. EACH GATE QUANTITY SHOWN ABLE TO TAKE A FAILING **AND** A PASSING VALUE

Through the real readers on files in the pinned write format (pinned against real
`rhoCentralFoam` output on this box, `verification/runs/F15_runs/coarse/4/{rho,U}`,
10,000 cells, parsed at selftest), on a synthetic level carrying a region-2 box grid
**and the fine level's own 600-cell fan-line column** with the exact fan field:

| gate | construction | value | band | side |
|---|---|---|---|---|
| G-F24-1 | exact state 2 + 1× finest sub-ladder error | 0.393197062 | [0.392679994, 0.393455596] | **inside** |
| G-F24-1 | exact state 2 + 40× | 0.398238474 | same | **outside** |
| G-F24-2 | exact fan field + 1× predicted fine error (uniform) | 1.3509345e−03 | [4.503e−04, 4.053e−03] | **inside** |
| G-F24-2 | exact fan field + 40× | 5.4037382e−02 | same | **outside** |
| G-F24-2 | exact fan field, no error | **0.0** | — | zero-error control |
| R-F24-M | exact state 2 → reader returns 2.598446326990894 (M₂ to 1e−15); planted Ux offset seen | — | none | reported |

**Honest limit:** format-faithful synthetic files; the *format* is pinned, the
*values* are constructed.

## 7. THE SMOKE ARM — the real 4-rank chain on the real coarse build (NOT a level; not retained; not a result)

Scratch copy of the **coarse level** built by `build_f24.py` (§1 checkMesh readings),
`decomposePar` (4 × 11,250 cells), **10 real `rhoCentralFoam` steps on 4 ranks
(`mpirun -np 4 rhoCentralFoam -parallel`)**: rc 0, `Time = 0.002666666667` written
in every rank with 45,000 p entries in total, **max |p − p₁| = 0.302 after 10 steps
(non-zero: the corner moves the field)**, solver-reported Courant mean 0.128 / max
0.133 (ceiling 0.35), ExecutionTime 0.49 s, ClockTime 1 s, RSS 96 MB per rank, box
load 14.2 → 14.7 on 16 cores. Startup-dominated — **not a rate measurement**. The
sub-ladder (§4) ran the same dictionaries serially to t = 4 at three sizes: Courant
max 0.1370 at every grid; plateau reached at 1/64 with the margins stated in §5.

## 8. COST — COSTED BEFORE THE RUN

**Unit: core-minutes = ClockTime(s) × ranks ÷ 60.** Ranks = 4 at every level.

**Rate basis — DERIVED, NOT MEASURED on this case:** F15's MEASURED serial
`rhoCentralFoam` rate on a DIFFERENT case (`verification/runs/F15_runs/{coarse,
medium,fine}/log.rhoCentralFoam`: **0.736 / 0.698 / 0.710 µs per cell-step** at
10k / 40k / 160k cells, inviscid, `COST_CALIBRATION.md` C-133) with F20's
carry-forward **0.9 µs per cell-step above ~200k cells** (C-136: 0.88 µs measured at
262k cells, cache-shaped). The explicit scheme has no linear solve, so the rate does
not grow with N beyond the cache effect. The projection assumes ideal 4-rank scaling
for the wall figure; the cap check is on the measured ClockTime × 4 regardless.

| level | cells | steps | cell-steps | rate (µs) | core-s | core-min | wall on 4 ranks |
|---|---|---|---|---|---|---|---|
| coarse | 45,000 | 15,000 | 0.675 G | 0.72 | 486 | 8.1 | 2.0 min |
| medium | 180,000 | 30,000 | 5.40 G | 0.90 | 4,860 | 81.0 | 20 min |
| fine | 720,000 | 60,000 | 43.2 G | 0.90 | 38,880 | **648.0** | **2.7 h** |
| **total** | | | **49.3 G** | | **44,226** | **737.1** | **≈ 3.1 h** |

At F15's flat 0.72 µs the total would be 590 core-min (the lower bound). **REGISTERED
CAP: 1,450 core-minutes** (1.97× the estimate; the admission is the 4-rank parallel
efficiency of an explicit solver at 180k cells per rank on a shared box and the
cache-shaped rate above 262k cells, which no record measures). **Derived dollars at
$0.0513/core-h: $0.63 estimate, $1.24 at the cap — DERIVED, NOT MEASURED,
reported-by-owner rate** (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25
pre-authorisation. **`cost_basis: derived, reported-by-owner, not measured.`**

**Serial versus 4 ranks — stated:** the fine level serial would be 38,880 s ≈ 10.8 h
on this basis; the ladder runs on **4 ranks with `decomposePar` at every level** (one
decomposition for the whole ladder; the runner reserves 4 cores).

Cap checked **incrementally after each level** and **projected before each level**
from the launcher's own box probe (`PROJ_CORE_S` = 486 / 4860 / 38880 core-s, scaled
up when fewer than 4 cores are free); a crossing **HALTS at exit 3**; unlaunched
levels stay `PENDING`; launcher and grader refuse to start if their caps disagree
(measured: "CAP AGREES … 1450").

**Memory floor: 2.0 GB** (96 MB per rank measured at 11k cells per rank; ≈ 1 kB/cell
→ ≈ 0.3 GB per rank at 180k cells per rank, estimated, not measured; the grader
holds one level's 40 checkpoint p fields sequentially, negligible). **Disk:** 40
checkpoints × 4 ranks × (rho, U, p, T, phi) ≈ 4 GB for the fine level, ≈ 5 GB for
the ladder (269 GB free on `/`).

**Plateau risk, registered:** if a level's box-mean p/p₁ series fails Class C or the
residual limb, every quantity of the ladder is NOT A RESULT by rule 5 limb 1 and
stays so (§5 states the sub-ladder margins).

**At completion** actual/predicted lands in `docs/COST_CALIBRATION.md`.

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`date -u` = **2026-08-26T22:43:41Z**. `ls -d
/home/ubuntu/Certonomous/verification/runs/F24_PRANDTL_MEYER_runs` → **`No such file
or directory`** (ABSENT; `--preflight` printed the same reading). `find
cases/F24_PRANDTL_MEYER -name RC.txt -o -name 'log.*' | wc -l` → **0**; the case tree
holds no numeric directory beyond the tracked template `case/0` (holding
`T.template`, `U.template`, `p.template`) and no `processor*`.

## 10. NEVER RUN — THE EVIDENCE (L-337 controls first)

- `git ls-tree -r HEAD --name-only`: **15,426** tracked paths at the writing
  invocation; **planted control: the known `cases/F22_lamb_oseen/` paths are returned
  (13)**; matches for `F24|PRANDTL|prandtl`: **0**.
- Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` **0**;
  `/home/ubuntu/closure-data` **0**; `/home/ubuntu/closure-challenge-benchmark` **0**.
  `verification/runs/` holds no `F24*` directory.

## 11. FROZEN FILES (sha256 at this freeze)

    cases/F24_PRANDTL_MEYER/exact_f24.py    91e29607f33955bd1f75271397607520d2df273b1e9537192cbd59cbc7d04723
    cases/F24_PRANDTL_MEYER/grade_f24.py    e17486750d732475874751a26798744e15dcca37484f0426d2013b150baecce7
    cases/F24_PRANDTL_MEYER/build_f24.py    208e47c684152b732ee38b93ca703435b7caa0dc0f116195ab4014962c349bd5
    cases/F24_PRANDTL_MEYER/foam_io_f24.py  cde97b5aeb1876500f603d177112c46702c4cd61782c67fafe11176f917a6b10
    cases/F24_PRANDTL_MEYER/run_f24.sh      7b0190995bae769ffb027e4c44dbbc95f473f9f1e65d5bf162e2feedae087a6e
    cases/F24_PRANDTL_MEYER/case/0/{T.template,U.template,p.template}
    cases/F24_PRANDTL_MEYER/case/constant/{thermophysicalProperties,turbulenceProperties}
    cases/F24_PRANDTL_MEYER/case/system/{blockMeshDict.template,controlDict.template,decomposeParDict,fvSchemes,fvSolution}
    verification/campaign/F24_PRANDTL_MEYER_PREREGISTRATION.md   (this file)

## 12. LAUNCH SHAPE (for the supervisor's check 4; NOT an authorisation)

    bash /home/ubuntu/Certonomous/cases/F24_PRANDTL_MEYER/run_f24.sh --prereg-commit=<this file's freeze sha>

4 ranks at every level (`mpirun -np 4 rhoCentralFoam -parallel`); grading is a
separate invocation `python3 cases/F24_PRANDTL_MEYER/grade_f24.py --prereg-commit=<sha>`
reading the processor directories. The queue entry
`cases/F24_PRANDTL_MEYER/queue_entry_F24_PRANDTL_MEYER.json` is **HELD in the case
directory** until the supervisor's check 1/4; the supervisor, not this lane, moves it
into `verification/queue/cfd/`; enqueueing is not authorisation.

## 13. WHAT IS **NOT** REGISTERED HERE

- No order claim on G-F24-1; no verdict on the Mach number; no claim about the fan's
  captured width, the corner cell or the entropy layer beyond what the reported
  Mach number carries; no claim about the region above the head ray beyond its
  boundary datum.
- A finer sub-ladder grid (1/128, ≈ 6 core-min) would give the region-2 quantities a
  triple in a nearer range and could re-register G-F24-1 with an extrapolated band
  before first compute — it was not run because the registration compute limit is
  one core-minute; **stated for the supervisor's desk, not decided here.**
- No amendment to any standard, charter or frozen record.
- **Nothing is sent, filed, uploaded or submitted** (rule 7).
