# VMFL003-M3 — Pressure Drop in Turbulent Flow Through a Pipe, WALL-RESOLVED kOmegaSST — PRE-REGISTRATION

**Case:** VMFL003 (Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 19–20).
**Successor to:** VMFL003-M2 (base freeze `c5fdcad4`; register rows #9–#12).
**Lane:** `ansys-lane-opus48`. **Supervisor ruling authorising this design:** 2026-09-07
(`ansys-verification-supervisor`, §3 check-2 lever ruling — single-lever wall resolution,
overturning the earlier compound "kOmegaSST-wall-function + relaxed ε residualControl" dated plan).

**NOT FILED ANYWHERE.** Nothing here is sent, emailed, uploaded, registered, posted or
commented outside this box (CLAUDE.md rules 7, 8). **The graded run is LOCKED:** it launches
only after the supervisor's four §3 checks AND clearance of the auto-mode graded-launch block,
which is Sanaa's desk (rule 9 — no agent message is her consent).

**Manual title-page verified** (Release 2026 R1, March 2026, ANSYS/Synopsys; L-144).

---

## 0. THE ONE-PARAGRAPH STATEMENT

VMFL003-M2 established, across a four-arm turbulence-model ladder (kEpsilon, realizableKE,
RNGkEpsilon, kOmegaSST) all sharing the **log-law wall FUNCTION** (`nutkWallFunction`) held
fixed as a control, that this lab's **wall-modelled** RANS under-predicts turbulent pipe
friction by ~4.5–6.4 % at Re = 1.37×10⁴ — a converged **model-form** discrepancy, not a
discretisation or budget defect. Under the fix-until-runs law (VERIFICATION_CHARTER §2ay:
a model-form diagnosis routes into an *active successor*, never a capability-gap filing, until
model-form is ruled out at source), M3 exercises the one near-wall lever M2 never tried:
**integrating kOmegaSST TO THE WALL** (y⁺ ≈ 1, `nutLowReWallFunction`, no wall function), on a
**radial** Roache triple that directly refines the friction-controlling direction. The gate,
band, Colebrook diagnostic, verdict path, planted-zero controls, `roache()` and the 1×10⁻⁸
residual leg are carried **byte-identical** from the M2 comparator (L-487); the **ceiling is
GATE REACHED, never PASS** (the reference is an empirical Moody-chart correlation). If, once
converged and wall-resolved, Δp is still outside the band, **GATE FAIL STANDS** — no gate-fitting.

---

## 1. L-502 LINEAGE CENSUS (done before authoring; base verified against HEAD)

| item | finding |
|---|---|
| **The actual latest frozen base** | **VMFL003-M2** (dir `cases/ansys_verification/VMFL003_M2/`, freeze `c5fdcad4`). Landed **NOT A RESULT** on all four arms (register rows #9–#12). |
| **Base blob shas (disk == HEAD, no drift)** | `PREREGISTRATION.md` `cdbf2659b6eec2599fc3eda7a149aaca391461b0`; `grade_vmfl003_m2_omega.py` `b595c86a4b8580d5928b4d4dd1458698f6de8ac2`; `grade_vmfl003_m2.py` `6dcc99940154ea204a598ba2118042bf972a786d`; `run_vmfl003_m2.sh` `29a53e035a1bb595d7dde69b0e2e6b77bcd561b4`; the answers-seen doc `BUDGET_KILL_REPAIR_REFUSED.md` `318eef041fe52b5f63b48e2a9cbaf6e7b1103fa9`. |
| **FALSE PREMISE in the dated plan (HALTED on, then overturned)** | The FIX_SUCCESSOR_REGISTRY line-78 entry stated *"the M2 arms varied only endTime/grid."* **FALSE:** M2 varied the turbulence MODEL across four arms and held `nutkWallFunction` FIXED. The plan's "change to kOmegaSST" was therefore not novel — kOmegaSST-with-wall-function was M2 arm D, the **worst** at −6.414 %. The registry correction was made by the supervisor (2026-09-07); this lane does not touch it. |
| **CONTAMINATION (one-way door)** | M2 `BUDGET_KILL_REPAIR_REFUSED.md` §7 read the four wall-function Δp answers off disk: A_kEpsilon −4.338 %, C_RNGkEpsilon −5.943 %, D_kOmegaSST −6.414 % (all vs 21744 Pa). Any successor re-using a wall-function model is written by someone who has seen its answer (rule 2 forfeit). **M3's configuration — kOmegaSST integrated to the wall, y⁺ ≈ 1 — has NEVER been run or seen**, which is the clean standing this successor rests on (§2 firewall). |
| **CEILING** | GATE REACHED, never PASS — 21744 Pa is the empirical Moody-chart smooth-pipe correlation (§2h.6.1). Carried unchanged from M2. |

---

## 2. THE SINGLE LEVER, AND THE CONTAMINATION FIREWALL (mandatory, ruling item ii)

**THE LEVER IS EXACTLY ONE: the near-wall TREATMENT.** Log-law wall FUNCTION →
model integrated **TO THE WALL**:

| | VMFL003-M2 (all four arms, control) | VMFL003-M3 |
|---|---|---|
| `nut` wall BC | `nutkWallFunction` (log-law, imposes wall shear) | **`nutLowReWallFunction`** (nut → 0 in sublayer; shear computed) |
| `k` wall BC | `kqRWallFunction` | **`kLowReWallFunction`** |
| `omega` wall BC | `omegaWallFunction` | `omegaWallFunction` (unchanged — Menter automatic wall treatment, correct at y⁺ ≈ 1) |
| radial mesh | uniform NR = 5, y⁺ ≈ 40.8 (log layer) | **graded, y⁺ ≈ 1 (resolved sublayer)** |
| turbulence model | four arms | **kOmegaSST only, pinned a priori** |

**MODEL PINNED A PRIORI, FOR METHODOLOGICAL REASONS ONLY.** kOmegaSST natively integrates
through the viscous sublayer without the wall-damping functions the low-Re k-ε variants require;
it is the single well-posed wall-resolved model that adds no damping-function degrees of freedom,
and integrating it to the wall is standard OpenFOAM low-Re practice. *"kOmegaSST OR low-Re
kEpsilon" is deliberately NOT left open* — choosing among candidate models after seeing results
is model-shopping. The choice is **not** the arm ranking and **not** proximity to the target.

**CONTAMINATION FIREWALL.** This lane has seen the four M2 wall-function Δp values. They are
cited **only** as the state-(b) prior-art diagnosis that *motivates* trying wall resolution.
They are **never** used to set any gate constant, band, threshold, cap, ceiling, or the model
choice. The gate, band, Colebrook diagnostic, verdict path, `roache()`, readers, the three
planted-zero controls and the GATE REACHED ceiling are carried **byte-identical** from
`grade_vmfl003_m2_omega.py` (verified: all 41 gate constants and all 19 gate functions
byte-identical; only `grade`, `selftest` and `verify_frozen` differ, in config/paths/y⁺-clause).
The M3 prediction is **DIRECTIONAL ONLY**: resolving the sublayer raises the computed wall
friction, so Δp is expected to rise **toward** 21744 Pa relative to the wall-function
under-prediction — the *value is unseen*, and because the M3 configuration is unrun its answer
cannot have been fitted.

---

## 3. THE GATE (byte-identical from M2 — NOT re-derived)

- **Gate quantity:** Δp[Pa] = ρ·(⟨p⟩_inlet − ⟨p⟩_outlet), ρ = 1.225, at the finest **CONVERGING**
  level (manual p.19 defines the compared quantity as the inlet-to-outlet pressure difference).
- **Reference / target:** **21744 Pa** (manual Tables .03.1/.03.2; Fluent 21480/ratio 0.988,
  CFX 21740/ratio 1.000; White, *Fluid Mechanics*, 3rd ed., 1994).
- **Band:** ±2.5 % (`GATE_BAND = 0.025`). In-band → **GATE REACHED**; out-of-band → **GATE FAIL**.
- **Ceiling: GATE REACHED, never PASS.** 21744 Pa is the empirical Moody-chart (Colebrook/P-vK)
  correlation — a different-model reference; VERIFICATION_CHARTER §2h.6.1 caps such a case at
  GATE REACHED however exact its own algebra. A converged, in-band, wall-resolved result reaches
  the ceiling; it does not become a PASS.
- **Colebrook / friction-factor DIAGNOSTIC** (printed with equal prominence, never the gate):
  `F_COLEBROOK = 0.028464169573919965`, `DP_COLEBROOK = 21792.879830032474 Pa`, diagnostic bands
  ±2 % on Δp and on the developed-region f_dev. Byte-identical.
- **Case facts** (verified): ρ = 1.225, μ = 1.7894×10⁻⁵, U = 50, R = 0.002 (D = 0.004),
  L = 2 (L/D = 500), ν = 1.4607346938775508×10⁻⁵, Re = 13691.740248127866, q = 1531.25 Pa.

---

## 4. THE MESH FAMILY, THE RADIAL ROACHE TRIPLE, AND THE y⁺ CLAUSE (ruling item v)

**PRIMARY Roache triple = RADIAL (wall-normal).** Fixed NX = 1000; NR doubled per level, the
**wall-cell height halved**, so y⁺ ≈ 1 → 0.5 → 0.25. This refines the **friction-controlling**
direction directly (far stronger than M2's axial triple: developed pipe Δp is linear in x, so
axial refinement barely tests it). RATIO = 2 (byte-identical `roache()`).

| level | NX | NR | wall cell (m) | g_r (last/first) | y⁺ (designed) | cells | endTime | mesh cert (scratch, answer-blind) |
|---|---|---|---|---|---|---|---|---|
| **L1_1000x25** | 1000 | 25 | 9.8×10⁻⁶ | 0.0369274 | ~1.0 | 25 000 | 5000 | **clean**, aspect 204.8 (y⁺ measured min 0.95 / max 1.77 / avg 0.98) |
| **L2_1000x50** | 1000 | 50 | 4.9×10⁻⁶ | 0.0361289 | ~0.5 | 50 000 | 5000 | **clean**, aspect 408 (designed) |
| **L3_1000x100** | 1000 | 100 | 2.45×10⁻⁶ | 0.0357391 | ~0.25 | 100 000 | 5000 | **clean**, aspect 817 (designed) |

**g_r is FROZEN, not solved at run time** — computed once from (NR, wall-cell target, R) as the
blockMesh `simpleGrading` ratio along the radial edge (axis→wall); g_r < 1 places the small cell
at the wall. First-cell-centre y⁺ = (h_wall/2)·u_τ/ν with u_τ = 2.9824575423381954 (Colebrook,
methodological — not the answer).

**N-AV10 IS REMOVED BY WALL RESOLUTION.** N-AV10 forbade a radial ratio-2 triple **only** because
R⁺ = 408.35 put the log-law window at a factor 2.72 < 4 — an obstruction of the wall **FUNCTION**.
With the model integrated to the wall, y⁺ = 1, 0.5, 0.25 are all valid inside the resolved
sublayer, so a proper radial ratio-2 triple exists. (This is exactly the friction-controlling
channel M2 could not refine, hence M2's GATE REACHED-only ceiling on the *no-usable-triple*
ground; that ground is now removed, but the ceiling still holds on the empirical-reference ground.)

**THE y⁺ CLAUSE IS INVERTED FOR WALL RESOLUTION** (config, one-way NOT A RESULT — NOT the Δp gate):
`YPLUS_RESOLVED_MAX = 5.0`. If max wall y⁺ > 5 (viscous-sublayer edge) at any graded level, the
mesh did not integrate to the wall, the M3 lever was not exercised, and the level is ungradeable.
Set from sublayer physics, answer-blind. This **replaces** M2's log-law-validity band [25, 65] +
min floor 11.06, which apply only to a wall function and are moot here.

**ORTHOGONAL (axial) diagnostic ladder** (fixed NR = 25, y⁺ ≈ 1; NX = 500 / 1000 / 2000; L1
reused as the middle rung): probes the channel the radial GCI cannot see (N-AV7 principle applied
to the orthogonal direction). One-way spread clause `LADDER_SPREAD_MAX = 0.05` unchanged.
M2 established the axial channel is negligible (slab difference bit-identical between axial
levels), so the spread is expected tiny; the ladder is the check that it is.

**RADIAL-MESH-ADEQUACY DIAGNOSTIC** (ruling v): the comparator records, per level, designed vs
measured y⁺ (min/max/avg) and whether the max y⁺ roughly halves L1→L2→L3 (the ratio-2 radial
refinement). Printed, never able to change the verdict.

**N-AV9 azimuthal deficit** (unchanged, carried in the error budget): the flat-sided 5° wedge
biases Δp high by sec(2.5°) − 1 = +0.09526851633199218 %; azimuthal, untouched by NX/NR refinement.

---

## 5. ITERATIVE-CONVERGENCE (RESIDUAL) LEG + THE BRANCH (ruling item iii)

**`RESID_TOL = 1.0×10⁻⁸` on each of {p, Ux, k, omega}, checked per level BEFORE the triple is
formed (rule 5 step 1) — CARRIED BYTE-IDENTICAL FROM M2, NOT RELAXED.** Relaxing this
verdict-determining leg is a threshold change reserved to Sanaa (D539 / ESCALATION §4.1); it is
the exact leg that set the prior verdict, and it is above this lane's and the supervisor's
authority to relax.

**THE PRE-REGISTERED BRANCH.** An answer-blind scratch smoke (y⁺ and linear-solver residuals read;
Δp NEVER read) showed that with the near-wall region resolved, the residuals descend far below
M2's log-law-matching epsilon floor of 1.4×10⁻⁸ – 8×10⁻⁸: **omega → 1.2×10⁻⁹, k → 1.2×10⁻¹²** by
~iter 600, while **p and Ux reach ~1×10⁻⁸ and plateau there (measured 8.9×10⁻⁹ to 1.15×10⁻⁸)** —
marginal against the 1×10⁻⁸ bar. Therefore:

- **If all of {p, Ux, k, omega} reach 1×10⁻⁸ at endTime** → the residual leg passes and the
  verdict proceeds to the triple/gate (§3, §6).
- **If any does NOT reach 1×10⁻⁸ at endTime** → the comparator returns **NOT A RESULT** on the
  residual leg (rule 5 step 1), UNCHANGED — the *same instrument refusal as M2*. A
  **Δp-1-ppm-plateau** completion criterion (Δp within 1 ppm of its final value and flat; M2
  §4 measured this satisfiable and far stronger here than any residual threshold) is then
  **escalated to Sanaa** with the measured floor as evidence. That criterion is a threshold
  change and is on Sanaa's desk as a PENDING item; it is **not** applied in this freeze.

**NO TUNING is done to force the leg below 1×10⁻⁸** (that would fit the reserved completion
threshold). The p-solver change below is a numerics fix for *solvability*, not for the floor.

**NUMERICS FIX (instrument, not a physics lever; §2ay "change the numerics").** On the
high-aspect wall-resolved mesh (aspect 204–817), GAMG+GaussSeidel hit its 1000-iteration ceiling
every outer step (measured in the smoke) — it does not converge the pressure equation on
high-aspect cells and would make the run ~1000× too slow (rule 12). **p solver → PCG with DIC
preconditioner** (`system/fvSolution`): the standard robust choice for the ill-conditioned
pressure matrix of a boundary-layer mesh; it solved p in 0–1 inner iterations/step and drove all
four outer residuals down monotonically. This touches neither the Δp gate nor the 1×10⁻⁸ floor.

---

## 6. THE VERDICT PATH (byte-identical rule-5 order) AND THE HONEST CAVEAT (ruling item vii)

`grade()` applies rule 5 in its frozen order:
1. any level not iteratively converged (residual leg) / not plateaued / **max y⁺ > 5** → **NOT A RESULT**;
2. radial triple not `CONVERGING` → **NOT A RESULT**, no GCI quoted;
3. `CONVERGING` → **GATE REACHED** (Δp in ±2.5 % band) else **GATE FAIL**; GCI printed (radial
   wall-normal channel; a real discretisation estimate, but the ceiling stays GATE REACHED on the
   empirical-reference ground, never PASS).

**HONEST OUTCOMES (mandatory, verbatim intent):**
- **converged + wall-resolved + in-band → GATE REACHED** (the ceiling; §2h.6.1 forbids PASS).
- **converged + wall-resolved + still outside band → GATE FAIL STANDS.** No gate-fitting, no
  band-widening, no further endTime/grid persistence, **no further model-shopping** (one model is
  pinned). A genuine converged model-form discrepancy against the manual, honestly recorded, is a
  legitimate GATE FAIL.
- **cannot form a gradeable CONVERGING triple, or the residual leg is unmet → NOT A RESULT.** The
  terminal model-form capability-gap (state a, §2ay) becomes reachable ONLY after this resolved
  attempt fails, escalated with data — never before.

---

## 7. PLANTED-ZERO CONTROLS (byte-identical, both arms; rule 3)

Three controls on the finest level's REAL artifacts (planted into temp copies; the run tree is
never modified), each with a PRESENT arm and a KNOWN-BAD/negative arm; the comparator REFUSES
(exit 2) if the reader is blind:
- **control 1 (Δp + ρ):** plant `PLANT_DP = 1.234` m²/s² into the kinematic inlet column; the
  graded Pa value must move by exactly PLANT·ρ = 1.5116500000000002 Pa (a ρ-blind reader is caught).
- **control 2 (y⁺):** plant `PLANT_YPLUS = 7.77` into the yPlus `average` column.
- **control 3 (f_dev):** plant `PLANT_SLAB = 2.345` into the slabA volAverage(p) column.
`PLANT_TOL = 1×10⁻⁹`. Gate-blind physical-range guards (`# Faces`/`# Cells` non-empty, column-by-
header, no positional guessing) are byte-identical. Selftest: **64 checks, 0 failures**, under
python3 and python3.12.

---

## 8. FROZEN PREDICTION (directional only — value unseen)

- **Direction:** resolving the viscous sublayer raises the computed wall friction relative to the
  log-law wall function, so Δp_fine is expected to be **higher** than M2's wall-function values
  (which sat at −4.3 % to −6.4 %) and to move **toward** 21744 Pa. Whether it reaches within
  ±2.5 % is **not predicted** and **not fitted** — that is the question the graded run answers.
- **Residual leg:** expected to be met by omega/k comfortably; **p/Ux are marginal at ~1×10⁻⁸**
  (§5) — the branch is live.
- **Triple:** a monotone `CONVERGING` radial triple with observed order p ≈ 2 is *expected*
  (smooth wall-normal gradients on a y⁺ ≈ 1 mesh); the comparator flags any order outside
  [0.5, 2.5] as untrusted and does not gate on it.
- **y⁺ adequacy:** expected to hold (L1 measured max 1.77 < 5; finer levels lower).

---

## 9. COST (CLAUDE.md rule 12)

Serial, RANKS = 1, so core-min = wall_s / 60. **EXTRAPOLATED** from the answer-blind smoke rate
(12 500 cells did ~1200 iters in 72 s ⇒ 4.8×10⁻⁶ s per iteration·cell), padded for the
super-linear PCG scaling on the finest mesh; endTime = 5000 each. **Estimate, not a measurement**
(the box cannot read its own billing; COMPUTE_BUDGET_CHARTER §5).

| level | cells | est. core-min | per-level cap → rc124 |
|---|---|---|---|
| A_500x25 | 12 500 | ~3 | 12 |
| L1_1000x25 | 25 000 | ~6 | 20 |
| L2_1000x50 | 50 000 | ~12 | 35 |
| A_2000x25 | 50 000 | ~12 | 35 |
| L3_1000x100 | 100 000 | ~24 (pad to ~40) | 80 |
| **total** | | **~57–70 est.** | **running-total cap 180** |

**Derived cost:** ~70 core-min = 1.17 core-h × $0.0513/core-h = **$0.060 DERIVED, NOT MEASURED**
(rate owner-stated, Sanaa 2026-08-21/22). Well under the $25 pre-authorised ceiling. An overrun
**stops the run** (rule 12). **At completion, the actual (from `RUN_RC.txt`/`COST.txt`, core-min)
is compared against this estimate and a row is landed in `docs/COST_CALIBRATION.md`** (rule 12,
estimate-vs-actual calibration).

**Scratch/authoring compute already spent (ephemeral, outside `verification/runs`, ungraded):**
~15 core-min (y⁺ smoke, p-solver calibration smoke, mesh-adequacy probes). Reported, not absorbed.

---

## 10. FREEZE DISCIPLINE (CLAUDE.md rule 2)

- This document, `grade_vmfl003_m3.py`, `run_vmfl003_m3.sh` and the `case/` inputs are committed
  **before** any graded solver runs. The freeze is the entire evidentiary content.
- The grading path is fixed at the freeze commit: `run_vmfl003_m3.sh` resolves `FREEZE_COMMIT` via
  `git rev-parse HEAD` (never hand-typed; L-382) and calls
  `grade_vmfl003_m3.py --verify-frozen $FREEZE_COMMIT`, which re-hashes the comparator's own bytes
  against the committed blob and REFUSES (exit 2) unless byte-identical.
- Before first compute, this file may be amended only with a stated, checkable condition. After
  first compute, gates are closed; changes land only as dated addenda that cannot alter a gate,
  threshold, cap or label. Originals are struck, never rewritten (rule 6).
- Driver guards: freeze-pin (disk == HEAD), comparator freeze-pin, refuse pre-existing level dirs
  (rule 4 age guard), per-level core-min caps → rc124 (rule 12), rc captured from a foreground
  `( cd && timeout ); RC=$?` subshell (setsid deliberately NOT used — the setsid-parent-returns-
  zero trap), mesh birth-certificate must admit each mesh.

---

## 11. WHAT THIS FREEZE DOES NOT CLAIM

- It does not claim Δp will land in-band — the prediction is directional only (§8).
- It does not relax the 1×10⁻⁸ residual leg; the plateau-criterion alternative is Sanaa's,
  pending (§5).
- It does not promote the ceiling above GATE REACHED (§3, §2h.6.1).
- It does not re-open or re-grade the M2 rows (they stand NOT A RESULT).
- No graded compute has run; no verdict is issued here. Verdict vocabulary on the eventual run:
  PASS is unavailable; the reachable outcomes are **GATE REACHED**, **GATE FAIL**, **NOT A RESULT**
  (or **BLOCKED**/**PENDING** as queue states).
