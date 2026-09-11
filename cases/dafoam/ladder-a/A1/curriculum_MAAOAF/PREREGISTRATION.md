# MAAOAF — MA288 compressible-primal initialisation ladder — **PERMISSION: NOT_FROZEN — DRAFT**

Not frozen, not enqueued, no compute spent. `dafoam-supervisor` freezes and launches. Nothing leaves the box (rule 7).

**Inherited by reference, restated nowhere:** `../compressible_wallresolved_triage/PREREGISTRATION_DRAFT.md`
(A1WCT) — its §1 premise, `VERDICT_CLASS = G-NOBAND`, `VERDICT_CEILING = GATE REACHED`, its 500-iteration arm
budget, its `R0` control, and its arms `A` aspect-ratio / `B` alphat / `C1` relaxation-λ / `C2` non-orth.
**This item registers only what A1WCT does not hold.**

## 1. Diagnosis — measured at MA288, `/home/ubuntu/certonomous-runs/MAAOA/MA288/`

| finding | artifact |
|---|---|
| **Clipping starts at iteration 1 ⇒ INITIALISATION, not drift.** `Bounding p<500000` **and** `p>20000` inside the `Time = 1` block. | `out/trim.log:536-537` |
| **`p` clips FIRST and alone.** `U`, `e`, `rho` do not clip until `Time = 100`. | `:550,553,562` |
| The bounds are DAFoam **shipped defaults** — `primalVarBounds` is never set. `pMax 5e5 pMin 2e4 / eMax 5.5e4 eMin -2.2e5 / rhoMax 5 rhoMin 0.2 / UMax 1e3`. | `:290-317`; no such key in `runScript.py:77-113` |
| **Those bounds are LOOSE, not tight.** `e` maps to `T ∈ [111.0, 494.0] K` at `Cv = Cp-R = 717.94`; a correct M 0.288 field cannot leave `[300,305] K`, `p` ±10 % of 101325, `rho` ±5 % of 1.1766. Excursions are blow-up, not physics. | `constant/thermophysicalProperties` |
| **The clip creates mass, monotonically**: cumulative continuity error `-9.99e-4 → -0.594 → 30.504` at `Time` 1/100/4000. | `:544,569`, tail |
| ICs uniform freestream (`U (100 0 0)`, `p 101325`, `T 300`); **`potentialFoam` absent** though `potentialFlow{nNonOrthogonalCorrectors 20;}` sits unused in `fvSolution`. | `case/0.orig/*`, `case/preProcessing.sh` |
| **Steady SIMPLE, not LTS**: `ddtSchemes default steadyState`, no `rDeltaT` in `case/4000/`, no `localEuler` under `cases/dafoam/`. | `case/system/fvSchemes` |
| The 388-line Bounding census is a **41-of-4000 sample**: `printInterval 100`, 41 `Time` blocks. | `:354` |
| 1 primal, 0 trim steps; `Primal min residual 0.8876809362068909` **== the `p` `initRes` at `Time = 4000`**, so DAFoam's own figure is an initial residual (`N-D44`-clean). | tail |

**INCOMP-vs-MA288, the entire diff.** `runScript.py`, 6 substantive hunks: `DASimpleFoam → DARhoSimpleFoam`;
`U0 10 → 100` (Re 6.7e5 → 6.5e6, **same mesh**); `p0 0 kinematic → 101325 absolute`; `+T0 = 300` state and BC;
`rho0 1.0 → 1.1766`; normalizeStates `p: U0²/2 → p0`, `+T`. Dicts: `div(phi,U)` is **`bounded Gauss
linearUpwindV grad(U)` in BOTH**; MA288's added `div(phi,e|h|K|Ekp)` are **already `upwind`**; `fvSolution`
identical but for `rho` joining the 0.30 field group; mesh, generator and `checkMesh` (`maxAR 212103.67`)
identical. **No knob differs — only the equation set and the freestream scale.** The bounding machinery is
live on the compressible path and dead on the incompressible one (INCOMP: 138 `Bounding`, `nuTilda` only).

**Mechanism.** A uniform start puts the whole pressure defect into the first SIMPLE pressure solve, taken at
`relTol 0.1` / relaxation 0.30 on a matrix whose wall-normal coefficients exceed its tangential ones by the
aspect ratio, 2.1e5. The correction is ~34× the dynamic head `ρU² = 1.18e4 Pa`, overshoots both default `p`
bounds, is hard-clipped, and the clip injects mass. `rho = ψp` clips, `e` clips, `U` clips. Everything after
`Time = 1` is downstream of that one solve.

## 2. Arms — one change each. MA288, α = 4°, np = 1, **500 iterations**, `printInterval: 1`

`R0` is A1WCT's control re-run here: "arm X still fails" is uninterpretable without it, and the
`printInterval` change alone forbids carrying tonight's log as the ground.

| arm | the single change | **prediction, registered now** | refuter |
|---|---|---|---|
| `R0` | none | `p` clip present in `Time = 1`; max `initRes` ≥ 0.3762 | no `Time = 1` `p` clip ⇒ **whole item `NOT A RESULT`** |
| `N1` | `primalVarBounds` widened to `pMax 1e9 pMin 1e2 UMax 1e5 UMin -1e5 eMax 1e9 eMin -1e9 rhoMax 1e3 rhoMin 1e-3` — is the clip **disease or thermometer**? | **FAILS, worse than `R0`** — `nan`/FPE or a residual above `R0`'s. The bounds are loose against the physics (§1 row 4); removing the only finiteness guard cannot cure a solve that hit them | finite at 500 with max `initRes` **below** `R0`'s ⇒ the clip WAS the disease, and the sweep's six points are a DAFoam-defaults defect |
| `N2` | `potentialFoam -writePhi` between `cp -r 0.orig 0` and the primal | **most likely to move it** — direct test of the initialisation hypothesis, and it solves the same high-AR pressure-like matrix once, properly (`Phi` `relTol 0`, `tol 1e-6`, 20 correctors, already in `fvSolution`). Zero `p` clip at `Time = 1`, max `initRes` < 0.3762 | `Time = 1` `p` clip unchanged ⇒ a divergence-free start does not help; cause is the AR–pressure matrix (A1WCT arm `A`) |
| `N3` | `div(phi,U): bounded Gauss linearUpwindV grad(U) → bounded Gauss upwind` — the only div term with second-order content left; `U` is 112 of the 347 p/U/rho/e clips | **partial at best, and it does NOT clear `Time = 1`**: `U` first clips at `Time = 100`, *after* `p`. Expect fewer `U` clips, `Time = 1` `p` clip unchanged | `Time = 1` `p` clip gone ⇒ the `U` scheme feeds the first pressure solve, which §1's ordering does not predict |

**LTS: NOT REGISTERED.** `cfd`'s CRM route does not transfer — `DARhoSimpleFoam` is steady SIMPLE, there is
no `rDeltaT` field, and `localEuler` appears nowhere in the family (same finding as A3). **No arm adds
iterations**: a diverging solve is not cured by more of it.

## 3. Gates — binding

- **`G-BOUND` (`N-D45`, the limb whose absence let six diverged points through).** `Bounding (p|U|rho|e)`
  count over the **whole** log must be **0**, and **the residual is printed beside the clip count on every
  row**. **Clips > 0 ⇒ `NOT A RESULT`, whatever the residual did.**
- **`G-SAMPLE`.** A log whose dict dump is not `printInterval 1` is **REFUSED, not graded** — a 41-of-4000
  census cannot support a zero claim (§1 row 8). Enforced in the grader.
- **`G-RES` (`N-D44`).** Max over `{U0,U1,U2,he,p,nuTilda}` of **`initRes`** in the last `Time` block;
  `finalRes` never read (assert). Threshold **< 0.3762**, R0's established floor.
- **Verdict.** `GATE REACHED` iff `G-BOUND == 0` **and** `G-RES < 0.3762`; `GATE FAIL` if `G-BOUND == 0` and
  `G-RES ≥ 0.3762`; `NOT A RESULT` if `G-BOUND > 0`. **`PASS` is unreachable here** and any path emitting it
  is defective.
- **Promotion gate (the full success definition)** — a follow-on 4000-iteration trim run, on a `GATE REACHED`
  arm only: trimmed **and** zero `Bounding` on p/U/rho/e **and** `primalMaxRes ≤ 1.0e-6`. The floor is **the
  product read from this case's own log** — `primalMinResTol 1e-08` (`:185`) × `primalMinResTolDiff 100`
  (`:356`) — not carried. CL band `|CL − 0.5| ≤ 1.0e-4` (`findFeasibleDesign` shipped tol).
- **`FALSIFIER`.** All four arms leave the `Time = 1` `p` clip in place ⇒ the initialisation/bounds/scheme
  family is refuted at MA288 and the cause is the AR–solver combination A1WCT arm `A` tests. That is a
  result and is reported as one.

## 4. Planted-zero control — **direction-aware, and EXECUTED**

`grade_maaoaf.py` runs **both** directions on **every** log, never the one the arm's outcome invites (A5P's
control could grade failure and not success; that cost a refusal on the arm that worked). `plant_fail()`
injects one `Bounding p<500000` line — verdict must become `NOT A RESULT`; `plant_pass()` strips the
p/U/rho/e clips and rewrites the last block's `initRes` to `1e-9` — verdict must become `GATE REACHED`.
Either direction failing to flip ⇒ **exit 2, no verdict**. **Executed before any arm exists, against both
sweep logs:** MA288's (347 real clips, `initRes` 8.877e-01) and INCOMP's (**a genuinely clean log** — 0
p/U/rho/e clips, `initRes` 2.485e-08); both flipped both ways, and the single clip injected into the clean
log graded `NOT A RESULT`. **Correction to the wording of the INCOMP control claim, not to its verdict:**
INCOMP's primal 005 — the one whose CL/CD were read — hit the 4000-iteration ceiling without satisfying
`1e-8` (only 3 of its 5 primals printed `Minimal residual … satisfied`), so INCOMP is accepted **on the
1.0e-6 floor, not on the tolerance**. Grader: `cases/dafoam/ladder-a/A1/curriculum_MAAOAF/grade_maaoaf.py`.

## 5. Cost — `cost_basis`: core-minutes from the sweep's own log; **dollars DERIVED, never measured**

Measured anchor: `ExecutionTime = 5518.61 s` / 4000 iterations at np = 1 → **1.3797 s/iter = 0.022994
core-min/iter**. (Sweep anchor: 664.0 ÷ 7 = 94.86 core-min/point.) A 500-iteration arm = 689.8 s = **11.50
core-min**; `R0+N1+N2+N3` = 45.99; `potentialFoam` pre-step ≤ 1.0 core-min **estimated, not measured**;
`printInterval 1` multiplies the per-print force/yPlus work 100× in count → **+20 % headroom** = 56.4.
**CAP = 60.0 core-min = 1.000 core-h → $0.0513 DERIVED** at $0.0513/core-h (owner-stated). **0.63 of one
sweep point** buys the ladder. Per-arm wall cap **1800 s**; **an overrun stops that arm** (rule 12).
Estimate-vs-actual lands in `docs/COST_CALIBRATION.md` at completion.

## 6. Unknown at freeze time

- ~~Whether `potentialFoam` reads `Phi` `READ_IF_PRESENT` or `MUST_READ`~~ — **RESOLVED BY MEASUREMENT,
  2026-09-11, before freeze.** Run in the registered image against a scratch copy of the MA288 case with no
  `0/Phi`: it printed `Constructing velocity potential field Phi`, converged (`Continuity error 1.38e-05`),
  `End`, rc 0, **45.66 s**. It wrote `0/Phi.gz` and rewrote `0/U.gz`; it left `0/p` and `0/T` untouched and
  wrote **no `0/phi`** — so no volumetric flux is handed to a solver that reads `phi` as a mass flux.
  **`N2` is NOT `BLOCKED`.** Its 45.66 s is inside the arm's graded wall.
- Whether `printInterval 1` touches any solver state beyond printing. Assumed not; unverified.
- Whether `N1`'s widened bounds trip an FPE before 500 iterations. A non-zero rc with `nan` **is `N1`'s
  result** (its own prediction), not `BLOCKED`.

## 7. Freeze values — handed to the supervisor, who freezes; this lane froze nothing

| slot | value |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/MAAOAF-ma288-init` — **confirmed absent** at drafting |
| image | `dafoam-idwarp-rot:v1` — **the PATCHED build the sweep actually ran** (`maaoa_chain_driver.sh:27-28`), **not** A5's `dafoam/opt-packages:latest` |
| image id | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |
| staged instrument | `…/fixed_lift_mach_sweep/maaoa_runScript_comp.py`, md5 **`bd22df020be42fbd2eef14cbc25182f7`** — byte-identical to `MAAOA/MA288/runScript.py`, so R0 reproduces the graded failure |
| grader md5 | `0b81bdef8ab595e7901612f7908f44a2` |
| runner md5 | `408e73e799a89d2849c8bbf5ac4e35c0` (`maaoaf_run_arm.sh`; a file cannot hash itself — the supervisor verifies this against the committed blob) |
| cpuset map | `R0→8 N1→9 N2→10 N3→11`; cores 2–7 were MAAOA's, 12–15 are A5's |
| per-arm | np 1, mem 3g, `endTime`/`writeInterval` 500, `TMO` 1800 s, `CAP_COREMIN` 15.0 (4 × 15.0 = the 60.0 item cap) |

**Runner:** `cases/dafoam/ladder-a/A1/curriculum_MAAOAF/maaoaf_run_arm.sh`, derived from A5P2's frozen
launcher and carrying its discipline. Four item-specific hazards are handled and each is measured, not
assumed: (i) **`potentialFoam` prints `ExecutionTime = ` before the solver exists**, so on N2 it would
satisfy the registered launch witness with no solver started — its output is redirected to a file and
`LA.0c` asserts that redirect; (ii) the shipped `maaoa_cmd.sh` resets `0/` at container start, destroying
the host-side age datum, so the reset is removed and `0/` is staged on the host; (iii) the age datum is
**`0/T`, not `0/U`**, because `potentialFoam` rewrites `0/U` and N2's datum would otherwise not mean what
the others' means; (iv) `daOptions` sits **inside** the instrument's own md5-hashed physics block, so every
`daOptions` change is appended **after** the closing marker — verified in dry test to leave the block md5 at
`cc2e3aba1861bcf17a09965e03cc956b`, i.e. the instrument's self-assert still passes.
`writeInterval` moves to 500 with `endTime`: at the shipped 4000 an `endTime` of 500 writes **no fields at
all** and rule 4's age guard would have nothing to read.

**Exercised before freeze, on real bytes:** `G-FREEZE.0` trips on the draft (8 placeholders, exit 3) and
**passes** on a fully-filled copy without matching its own prose — the A5P2 trap, tested in both directions.
The `daOptions` append and the N3 `fvSchemes` edit were dry-run against the real staged files and their
`G-DEADLEVER` read-backs pass, with R0's `assert_out` correctly clean.

## FREEZE STAMP — 2026-09-11, dafoam-supervisor

**FROZEN AT THIS COMMIT.** Values verified **by me from the machine**, not from the lane's report:
image `dafoam-idwarp-rot:v1` @ `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` (my own `docker images --digests --no-trunc`) — **the PATCHED build the sweep actually ran, NOT `dafoam/opt-packages:latest`**; staged instrument `MA288/runScript.py` md5 `bd22df020be42fbd2eef14cbc25182f7` (my own `md5sum`, byte-identical to the sweep's, so **R0 reproduces the graded failure rather than a rebuild of it**); run root `/home/ubuntu/certonomous-runs/MAAOAF-ma288-init` **CONFIRMED ABSENT** by my own `ls`; runner md5 `07483d2a942f65e021342e089e318496` post-substitution, `bash -n` clean, 0 unfilled slots; grader md5 `0b81bdef8ab595e7901612f7908f44a2`; cpusets R0→8 N1→9 N2→10 N3→11 (2–7 were the sweep's, 12–15 A5's).

**§3 CHECK-1, DISCHARGED BY EXECUTION.** I ran `grade_maaoaf.py` against **both real sweep logs**: it **REFUSED each (exit 3)** on `printInterval is 100, not 1 — a sampled Bounding census cannot support a zero claim`, and its **direction-aware control flipped BOTH ways on real bytes** — MA288 plant-fail → `NOT A RESULT` at 348 clips {p 81, U 112, rho 75, e 80} with max initRes 8.876809e-01, plant-pass → `GATE REACHED`; INCOMP likewise, naturally clean with max initRes 2.484578e-08. **That closes the control gap that cost A5P a refusal on its one successful arm.** `G-FREEZE.0` exercised both directions: the draft trips it (my own run, exit 3), a filled copy passes.

**THE HAZARD THAT WOULD HAVE SHIPPED, and it is the reason launch discipline is not ceremony:** `potentialFoam` — N2's initialiser — prints `ExecutionTime = 45.66 s` and `End` **before the primal exists**. Left on stdout it becomes the registered `^ExecutionTime = ` witness and N2 reports LAUNCHED with no solver started. Its output is redirected and `LA.0c` asserts both the redirect and the absence of any unredirected `potentialFoam` line. **A witness is only as good as the set of things that can emit it.**

**N2's UNKNOWN IS RESOLVED AND IT IS NOT BLOCKED:** `Phi` is `READ_IF_PRESENT` in this image — `potentialFoam` ran to `End`, rc 0, continuity error 1.38e-05 on 130,304 cells in 45.66 s, wrote `0/Phi.gz`, rewrote `0/U.gz`, left `0/p` and `0/T` untouched and wrote **no `0/phi`**. Hence the age datum is **`0/T`, not `0/U`** — `0/U` would not mean the same thing on N2 as on the other arms.
