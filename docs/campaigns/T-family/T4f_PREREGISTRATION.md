# T4f — impinging round jet, H/D = 2, Re = 23 000: the TRANSIENT / URANS treatment of the fine-mesh unsteadiness — pre-registration (**DRAFT v0.1, NOT FROZEN**)

> **STATUS AT THIS WRITING: DRAFT. NOT FROZEN. NOT BUILT. NOT ENQUEUED. NOT LAUNCHED.**
> **ZERO solver core-minutes have been spent, and no compute is authorised by this file.** The run
> directory `verification/runs/T-family/T4f_runs/` holds only the DRAFT instruments below (no `0/`
> dir, no numeric time dir, no `STATUS`/`log`/`DONE`/`blockMesh` marker). This draft is produced for
> the heat-transfer supervisor's non-delegable §3 checks (measurement-script diffs read as diffs;
> pre-registration **committed before** compute) and, per **CLAUDE.md rule 12**, for the supervisor to
> carry the COSTED figure to the chief **before any compute**. The run is **HELD for a later box
> window** — the box is under M6 top-priority pressure. Nothing here authorises a launch or a send
> (**CLAUDE.md rule 7: SUBMISSIONS REMAIN PARKED**).
>
> **This draft does not freeze a gate.** Under CLAUDE.md rule 2, before first compute the gate,
> threshold, cap and label are still open to amendment; they close only at the freeze commit, which is
> the supervisor's action, not this lane's. The freeze set + sha table (§12) is left as a TEMPLATE to
> be filled at freeze time.

**Predecessor: T4e** (`docs/campaigns/T-family/T4e_PREREGISTRATION.md`, frozen v1.0 at `17fb5109`;
`T4e_registered.json` `d1_transient_route`). T4e is the FROZEN **steady** fine-convergence
discriminator of **T4d** (`docs/campaigns/T-family/T4d_RESULTS.md`, committed `73e008dc`, whole rung
**`NOT A RESULT`** 2026-09-08). T4d measured the fine level (138 240 cells) reaching endTime 64 000
**CLEAN yet NOT field-converged**: C6.3 = **0.01518 ≈ 76× the 2e-4 tol**, and all three Roache radial
triples non-CONVERGING (G1 OSCILLATORY, G2/G3 DIVERGENT, all fine values BELOW band, no GCI). T4e's §3c
and `T4e_registered.json` `d1_transient_route` sketch the **D1 → transient/URANS route** as a
separately-registered downstream rung, and record that **the chief ENDORSED that route on 2026-09-08**.
**T4f is that route**, now authorised by Sanaa to run directly ("yes run the unsteady") — it does not
wait on T4e's long steady confirmation. Chain **T4 → T4b → T4c → T4d → T4e → T4f**.

**Rung id `T4f` is FREE** (verified 2026-09-08 by the T4e id-freeness method): no file named `*t4f*`
and no `T4f`/`"T4f"` content match exists anywhere under `docs/campaigns/T-family/` or
`verification/runs/T-family/`.

Verdict vocabulary fixed by **CLAUDE.md rule 1**: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.** No synonym, no hedge.

---

## 0. What T4f changes against T4d/T4e, and what it does NOT — the fix is the PHYSICS TOOL, never a gate

**T4f is a validation-against-reference of the TIME-AVERAGED impinging-jet field, run with the correct
transient solver on the one mesh that sustains the unsteadiness.** It carries over BYTE-INVARIANT from
T4d/T4e:

- the **three graded ERCOFTAC case025 `ij2lr` bands** — G1 r/D = 1.0 [1.069, 1.109] (ref 1.089), G2
  r/D = 2.0 [0.7688, 0.8088] (ref 0.7888), G3 r/D = 3.0 [0.4432, 0.4832] (ref 0.4632); half-width 0.02;
  reference **re-read from the held files at every run**, never from a JSON;
- the **frozen reader** `analyse_t4.sample_profile` / `peak_of` / `latest_time` / `classify` / `gci` /
  `planted_zero_control` (`verification/runs/T-family/T4_runs/analyse_t4.py`, blob `6f362447`), imported
  and never re-implemented;
- the **frozen fine mesh** (N = 192, nrj = 3N/2, first_cell 3e-6, **138 240 cells**), reproduced
  byte-identically from the frozen `build_t4e.block_mesh_dict` (build-time import, not on the grading
  path) — this is the identical mesh on which T4d measured the unsteadiness;
- the **frozen fields / BCs / transportProperties / turbulenceProperties / g** from
  `build_t4.fields()` / `constant_files()` (blob `ff032f3e`), called unchanged;
- the **Roache floors** `STAGNANT_FLOOR = 0.5`, `P_MIN = 0.05` imported by name from
  `scripts/roache_triple.py`.

**The ONE substantive change vs the T4-lineage is the SOLVER: steady `buoyantBoussinesqSimpleFoam` →
transient `buoyantBoussinesqPimpleFoam`** (same Boussinesq physics, β = 0 passive T, same `kOmegaSST`
closure run as **URANS = unsteady RAS**). Everything downstream of that — the transient time controls,
the `fieldAverage` and sampling functionObjects, and the transient-statistics gates (S1–S4) — exists
only to *support* the transient measurement. **No band, threshold, floor, reference or reader is
widened, moved or loosened.** The T4-lineage failure was a steady solver chasing an unsteady flow; the
fix is the correct tool, not a kinder gate (T25 discipline).

---

## 1. The solver — STOCK, system-path, USER-independent

- **`buoyantBoussinesqPimpleFoam`** — the transient PIMPLE counterpart of T4d/T4e's steady
  `buoyantBoussinesqSimpleFoam`. Same incompressible-Boussinesq momentum + `p_rgh` + passive-T + k/omega
  equation set; the only difference is a time-accurate `ddt` term and the PIMPLE pressure–velocity loop.
- **Confirmed present as a stock system binary** (2026-09-08):
  `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/buoyantBoussinesqPimpleFoam`
  exists in the same platforms `bin` as `buoyantBoussinesqSimpleFoam`. It is a stock ESI v2606 solver
  on the system path — **not a user build, not a compiled variant** — so the toolchain is identical to
  the frozen T4 lineage and USER-independent.
- **Turbulence: identical `kOmegaSST` RAS model, run transiently (URANS).** `constant/turbulenceProperties`
  (`simulationType RAS; RASModel kOmegaSST`) is the frozen `build_t4.constant_files()` output, unchanged.
  URANS resolves only the large-scale unsteadiness; this is **not** an LES and the schemes stay the
  URANS-appropriate ones the steady lineage used (see §2).

---

## 2. The case and the transient set-up — mesh and BCs inherited, time-controls new

**Mesh (inherited, byte-identical to the frozen T4e fine level `T4e_IJ_f`):** wedge 2.5°, three blocks
(jet core, wall jet, pipe), collapsed axis edge, N = 192, jet-core/pipe radial nrj = 3N/2 = 288
(inverted grading, fine at r0), wall-jet radial 288, axial 192, pipe axial 96, first cell 3e-6 m at the
plate and pipe wall, **138 240 cells**. Geometry D = 0.02 m, H = 2D, R = 6D, L_pipe = 10D, U_bulk =
17.25 m/s, ν = 1.5e-5, Re_D = 23 000, Pr/Pr_t 0.71/0.85. `build_t4f.py` imports the frozen
`build_t4e.block_mesh_dict` so the `blockMeshDict` is **byte-identical** to the T4e fine mesh; the
supervisor's §3 check must confirm that byte-identity (diff the generated `blockMeshDict` against
`T4e_IJ_f/system/blockMeshDict`).

**Fields / BCs (inherited, byte-identical):** `build_t4.fields("f")` — mapped recycling inlet (U, k,
omega), noSlip plate/pipeWall, pressureInletOutletVelocity entrainment/farfield, low-Re wall functions
(`kLowReWallFunction`, `omegaWallFunction`, `nutLowReWallFunction`, `calculated` alphat), plate constant
heat flux 1000 W/m². Valid for a transient run: the initial condition is a fresh start from the uniform
`0.orig` fields (`startFrom startTime; startTime 0`), so the rule-4 age guard holds (no pre-existing
time dir is reused).

**What is NEW (transient time-controls, in `system/`):**

- **controlDict:** `application buoyantBoussinesqPimpleFoam`; **FIXED time step** `deltaT` (see §5/§4,
  `adjustTimeStep off`) — chosen so that `endTime / deltaT` is an exact integer (this keeps the rule-4
  completion clause 5 an exact integer generalisation, §6); `endTime` = **T_end = 0.08 s**;
  `writeControl adjustableRunTime`/`timeStep` at a coarse full-field `writeInterval`; `purgeWrite 0`
  (retain the averaged fields and the checkpoints); functionObjects below.
- **fvSchemes:** the ONLY change from the frozen steady `build_t4.system_files()` schemes is
  `ddtSchemes { default backward; }` (steadyState → 2nd-order implicit `backward`, robust for URANS).
  `divSchemes` are kept the URANS-appropriate frozen set (`div(phi,U) bounded Gauss linearUpwind
  grad(U)`, limitedLinear for T/k/omega) — a URANS, not an LES, so no LUST/filteredLinear swap.
- **fvSolution:** the steady `SIMPLE` block is replaced by a `PIMPLE` block (`nOuterCorrectors 2`,
  `nCorrectors 2`, `nNonOrthogonalCorrectors 1`, `pRefCell 0`, `pRefValue 0`, `momentumPredictor yes`);
  the p_rgh GAMG solver is kept with a **final** tolerance loop (`p_rgh`/`p_rghFinal`, relTol 0.01/0);
  transient relaxation is `1.0` (or a light implicit-under-relaxation only on the non-final loops).
- **functionObjects:**
  - `fieldAverage` over `(U p_rgh T k omega)` with `timeStart = T_init = 0.03 s`, writing
    `UMean` (and the rest) — the TIME-AVERAGED field the comparator grades;
  - `sets`/`sampledSets` writing the **instantaneous** |U| radial line at G1/G2/G3 every `M` steps
    (M small, files tiny) — the time series `stationarity_t4f.py` uses to measure stationarity onset,
    the shedding/limit-cycle period, and window adequacy;
  - a `courantNo`/`Co` write (or the solver's own Co print) for the S3 Courant control.

---

## 3. The measurement — TIME-AVERAGE, then peak, then compare to the SAME band

**The graded quantity per station is the peak of the TIME-AVERAGED mean-velocity profile**,
`peak(UMean profile)/U_bulk` at r/D = 1, 2, 3, compared to the SAME ERCOFTAC case025 band the T4/T4b/
T4d/T4e rungs use (byte-identical, re-read from the held file). This is deliberately **peak-of-the-mean,
not mean-of-the-peak**: the ERCOFTAC reference is the mean velocity profile, and the two differ when the
instantaneous peak location moves in time — so the comparator reads `UMean`, not a time-average of
instantaneous peaks.

**How the frozen reader reads `UMean` without being edited (the NEW reader path).** The frozen
`analyse_t4.sample_profile` hard-codes `fields (U)`. Rather than edit a frozen file, `analyse_t4f.py`
makes a **scratch copy** of the case at `endTime`, **promotes `UMean` into a field object named `U`** in
that copy (byte-copy of the `UMean` file with its `object` renamed to `U`), and then calls the frozen
`sample_profile` / `peak_of` **unchanged** on the scratch copy. The frozen reader therefore reads the
time-averaged field exactly as it read the steady field, with no edit to any frozen instrument. This
promotion is a NEW code path and is controlled by a NEW planted-zero control (§4).

**One mesh, and why — the honest triple / GCI call (CLAUDE.md rule 5).** T4f runs on **one mesh: the
fine 138 240-cell mesh.** This is not an economy — it is forced by the physics. In T4d the **coarse and
medium meshes cleared C6.3** (1.4e-6 and 3.39e-6, i.e. they went effectively **steady**); only the fine
mesh sustained the unsteadiness (C6.3 76× tol, non-CONVERGING triples). A transient run on the
coarse/medium meshes would therefore average an essentially-steady field, and a c/m/f "time-averaged
triple" would compare a time-averaged unsteady fine field against near-steady coarse/medium fields —
violating the smooth-refinement assumption a Roache triple and GCI rest on. **So there is NO Roache
triple, and NO GCI is quoted.** Per rule 5, gate (2) (triple state) is **UNREACHABLE by registration**,
and gate (1) (the iterative/statistical-plausibility controls) binds in full. **The rung is a
validation-against-reference of the time-averaged field, gated but explicitly NOT GCI'd**, and this
draft quotes no observed order, no GCI and no discretisation bound on any number. (A 3-mesh transient
triple is costed as a rejected option in §5.)

---

## 4. Gates — REUSED-UNCHANGED, and the NEW transient-statistics gates

### 4a. Reused UNCHANGED from T4d/T4e (the fix is the tool, never the gate)

Applied to the **time-averaged** field (via the `UMean → U` scratch promotion) except where noted:

- **C1 / C1b** plate & pipeWall y+_max < 1.0 (wall-resolved; read through the solver's own `yPlus`
  post-processing, with the y+-scaling and blind-generic-reader arms). Fires NOT A RESULT on gate (1).
- **C2** nozzle-exit U_c/U_bulk within ±3 % of 1.2245 (on the time-mean). Fires NOT A RESULT on gate (1).
- **C3** global mass conservation |Σφ|/|φ_in| < 1e-3 (on the written φ). Fires NOT A RESULT on gate (1).
- **C4** the frozen `analyse_t4.planted_zero_control`, both arms, on the G-row reader — run on the
  `UMean → U` scratch copy (it plants into the promoted `U` and reads it back through the frozen reader).
  Fires REFUSAL (exit 2). Reused byte-for-byte.
- **C5** strict completion + age guard (`mark_done_t4f.py`; see §6 for the clause-5 adaptation and its
  FLAG). Fires NOT DONE → comparator refuses.
- **Roache floors** imported by name; **no triple applies** (§3), so gate (2) is UNREACHABLE, not waived.

### 4b. NEW — transient-statistics gates, prediction-first (NOT edits to any existing gate)

- **S1 STATIONARITY.** The running time-average of each G-row instantaneous peak has converged by
  `timeStart`, i.e. the measured stationarity onset **t_stat ≤ T_init = 0.03 s** (the discard covered
  the initial transient). Measured by `stationarity_t4f.py` from the instantaneous G-row peak series via
  a running-mean + running-variance criterion. If t_stat > T_init the `UMean` is biased →
  **NOT A RESULT** (inadequate discard; continuation with a later start). Registered threshold:
  running-mean change over the pre-`timeStart` tail ≤ **ε_stat = 1e-3** in U/U_bulk (5 % of the 0.02
  band half-width).
- **S2 AVERAGING-WINDOW ADEQUACY.** The window [T_init, T_end] = [0.03, 0.08] s contains **≥ N_min = 20**
  shedding/limit-cycle periods (period measured from the dominant frequency / detrended zero-crossing
  count of the instantaneous G-row peak series), **AND** the running average of the windowed `UMean`-peak
  has converged (change over the last 25 % of the window ≤ **ε_avg = 1e-3** U/U_bulk). If the signal is
  **steady** (no resolved unsteadiness — a measured finding falsifying the premise, see L1 §7) the
  N_min-periods clause is satisfied trivially and adequacy rests on running-mean convergence alone.
  Fires **NOT A RESULT** if not met.
- **S3 COURANT CONTROL.** max Co over the whole run ≤ **maxCo = 0.9**. Read from the solver Co output /
  `courantNo` FO. A breach means the fixed dt was inadequate → **NOT A RESULT**.
- **S4 TIME-STEP ADEQUACY.** (i) the committed fixed dt ≤ the **probe-measured** CFL-limited dt at
  Co = 0.9 (§5, the calibration probe), AND (ii) a **dt-halving spot check** on a short sub-window of the
  stationary régime moves the time-averaged G-row peak by ≤ **ε_dt = 1e-3** U/U_bulk. **FLAG:** a full
  dt-halving over the whole run would double the cost; the spot-check form (a short stationary sub-window
  at dt/2, ~2 000 steps) is registered instead. Fires **NOT A RESULT** if (i) or the spot check fails.

### 4c. Planted-zero controls (CLAUDE.md rule 3) — one reused, two new

1. **REUSED** — frozen `analyse_t4.planted_zero_control` on the `UMean → U` scratch copy (C4 above).
2. **NEW** — the **`UMean → U` promotion** control: plant a known offset into `UMean` on a scratch copy,
   run the promotion, confirm the frozen reader recovers it from the promoted `U`; blind arm (no plant →
   reader returns 0). A reader path that promotes a field is not evidence until it is shown able to see a
   non-zero planted into the source field. Refuses (exit 2) on failure.
3. **NEW** — the **`stationarity_t4f.py` windowed classifier** control (it BOTH measures stationarity/period
   AND decides S1/S2, so a reader not shown able to both see stationarity AND reject drift is not
   evidence): synthetic **stationary-converged** series MUST pass S1/S2; synthetic **drifting**
   (non-stationary) series MUST fail S1; synthetic **too-short-window** series MUST fail S2; a
   **determinism** arm (identical bytes → identical classification). Modelled on the trajectory_t4e.py
   two-arm + slow-decay control. Self-test must be green under both `python3` and `python3 -O`.

---

## 5. COST — CLAUDE.md rule 12, COSTED BEFORE COMPUTE (the key deliverable)

**Basis, honestly labelled.** The per-timestep cost is an **ESTIMATE, not a measurement**: the T-family
holds no measured `buoyantBoussinesqPimpleFoam` (or any URANS PIMPLE) rate — every T4-lineage run is
steady SIMPLE, and the transient-conduction rungs (T11/T14/T17/T18) solve only T with no pressure loop,
so none is a valid per-step basis. The estimate is built from **T4d's OWN clean measured fine SIMPLE
rate** — **1200.233 core-min / 64 000 iters = 0.0187536 core-min/iter = 1.1252 core-s/iter** on the
identical 138 240-cell mesh (T4d_RESULTS.md, `capped=no`) — scaled by a **PIMPLE-step factor
f_pimple** (a PIMPLE step with nOuterCorrectors 2 + nCorrectors 2 solves the U–p system more than once
per step). **This factor and the time-step dt are the two dominant uncertainties and are flagged for
calibration at completion (rule 12).**

**A cheap CALIBRATION PROBE pins the dt uncertainty before the expensive run** (itself HELD, no compute
now): ~500 steps with `adjustTimeStep on`, maxCo 0.9, to MEASURE the CFL-limited dt on this mesh; the
measured dt (rounded down to divide `endTime` evenly) becomes the committed fixed dt. Probe cost ≈ 500 ×
(1.1252 × f_pimple) ≈ **24 core-min** (~23 min wall, ranks 1, ~$0.02 derived) — registered separately.

**Time-step estimate.** Wall-resolved cells 3–6e-6 m near r0 / the plate, tangential wall-jet velocity
up to ~1.1 U_bulk ≈ 19 m/s; Co is set by the flow-direction cell size at the worst cell. Estimated
CFL-limited dt at Co = 0.9: **central 8e-7 s, range [5e-7, 1.5e-6] s.** (This is the calibration-probe
target.)

**Physical-time budget:** discard T_init = **0.03 s** (≈ 26 convective D/U_bulk times, ≈ 13 shedding
periods at St ≈ 0.5); averaging window **0.05 s** (≈ 21 shedding periods ≥ N_min = 20); **T_end = 0.08 s.**

**Time steps:** POINT dt 8e-7 → **100 000 steps**; CAP dt 5e-7 → 160 000 steps; best dt 1.5e-6 → 53 333.

**SERIAL basis** (ranks 1 — the per-timestep compute basis; the operative run is PARALLEL, re-cost in §5b):

| scenario | dt (s) | steps | f_pimple | core-s/step | **core-min** | **core-h** | wall (ranks 1) | **$ derived** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **BEST** | 1.5e-6 | 53 333 | 2.0 | 2.25 | **2 000** | 33.3 | ~1.4 d | **$1.71** |
| **POINT** | 8e-7 | 100 000 | 2.5 | 2.81 | **4 688** | 78.1 | ~3.3 d | **$4.01** |
| **CAP (backstop)** | 5e-7 | 160 000 | 3.5 | 3.94 | **10 507** | 175.1 | ~7.3 d | **$8.98** |

- **$ derived, NOT measured** (rule 12; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER`
  §5), at owner-stated $0.0513/core-h, reported-by-owner.
- Per rule 12 an overrun **stops the run** (`capped=yes` → NOT A RESULT), it does not get a new budget.

---

## 5b. PARALLEL DECOMPOSITION — verification ruling `19b7330a` (application of `PARALLEL_GATE_DOCTRINE`, NOT a relaxation), and the re-cost

**Verification GRANTED T4f parallel decomposition** on 2026-09-08 —
`verification/campaign/T4f_PARALLEL_DECOMPOSITION_RULING_2026-09-08.md`, committed `19b7330a` — as an
**application of the ratified `docs/standards/PARALLEL_GATE_DOCTRINE.md` (Sanaa 2026-08-25), not a
relaxation**, so **no Sanaa escalation**. The lineage's `ranks = 1 (F15)` shorthand protects a
**grid-convergence ORDER FIT** (`F15_OSR29_PREREGISTRATION.md` Amendment 1 reason (a): different rank
counts inject non-mesh floating-point-summation differences into the level-to-level differences the
observed-order fit consumes). **T4f has no Roache triple**, so F15's protected quantity is **absent by
construction** and the serial rule does not apply.

**Registered conditions — verbatim from the ruling; I register EXACTLY these, invent none, exceed none:**
1. **Deterministic decomposition, pinned pre-compute** (doctrine C1): **`method simple`** (deterministic
   geometric, reproducible from the committed `decomposeParDict` *alone* — the only method fully
   specifiable pre-compute; `scotch` is admissible only with its partition pinned, a launch-phase
   artifact, so it is **not** registered here). Rank count frozen in the committed `decomposeParDict`.
   C1 check: decompose twice from a byte-identical case, per-rank cell counts identical.
2. **S1–S4 unchanged and binding** — they *are* the invariance guarantee; S2 (≥ 20 periods + running-avg
   convergence ≤ 1e-3) is the load-bearing backstop (a failed S2 is NOT A RESULT regardless of ranks).
3. **Proper parallel I/O** — the graded `UMean` is read from a **reconstructed** field (`reconstructPar`).
4. **Numerics identical to serial** — same schemes, same **fixed dt** (`adjustTimeStep off` → timestep
   decomposition-independent), same PIMPLE correctors, same solver; **only `decomposeParDict` changes**.
5. **Gate, band, threshold, cap, label UNMOVED.**
6. **Optional (not a condition)** — a 2-rank-vs-serial spot check on the ~24 core-min probe window would
   convert the ergodic argument to a lab measurement; S1/S2 suffice without it.

**Decomposition-invariance basis (CITED from the ruling, not re-derived here):** the verdict is the peak
of a statistically-converged **time-average**; parallel and serial instantaneous trajectories diverge
(FP reduction reordering, decomposition-dependent GAMG — N-D12, N-D30), but the time-average over a
stationary window is a property of the stationary statistics both layouts sample identically
(ergodicity), so the divergence washes out; T4f's **S1/S2 are the measured backstop** — a converged
time-average is decomposition-invariant to within the sampling tolerance ≤ 1e-3, far inside the 0.02
band (recorded spread ~2e-5 to ~1e-4). **Honest limit (from the ruling):** the lab has no direct
measurement of decomposition-invariance for a time-averaged *URANS* statistic; the grant rests on the
ergodic argument + S1/S2, not on a serial-vs-parallel comparison.

**Decomposition registered:** `method simple`, `numberOfSubdomains 8`, `simpleCoeffs (4 2 1)` — n_z = 1
(the 2.5° wedge is one cell thick in z); 138 240 / 8 ≈ 17 280 cells/rank. The doctrine codifies **no
numeric cells/rank floor**, so 8 is a lane efficiency judgment (leaving headroom on the 16-vCPU box),
stated as such. The coeffs are a DRAFT choice and may be balance-tuned at the staged build to target a
per-rank max/min cell ratio ≤ ~1.5, **changing only `decomposeParDict`** (condition 4).

**RE-COST (rule 12).** Core-minutes are *not* invariant: parallel adds comms + imbalance idle, so
`core-min_parallel = core-min_serial / η` and `wall_h = core-h_serial / (nRanks × η)`. η (parallel
efficiency) is an **ESTIMATE to be calibrated** — central **0.80**, range [0.65, 0.90] (8-rank PIMPLE on
~17 k cells/rank, 2D-like wedge, `simple` geometric on a graded multi-block mesh → some imbalance; the
supervisor's ~0.90 is the optimistic end).

| scenario | serial core-min | η | **parallel core-min** | **core-h** | **wall @ 8 ranks** | **$ derived** |
|---|---:|---:|---:|---:|---:|---:|
| **BEST** | 2 000 | 0.80 | **2 500** | 41.7 | **~5.2 h** | **$2.14** |
| **POINT** | 4 688 | 0.80 | **5 860** | 97.7 | **~12.2 h** | **$5.01** |
| **CAP (backstop)** | 10 507 | 0.65 | **16 165** | 269.4 | **~33.7 h** | **$13.82** |

- **`timeout_s` (parallel) = 16 165 × 60 / 8 = 121 238 s** (~33.7 h). Stall backstop; an overrun stops
  the run (rule 12).
- **Does it exceed $25/run? NO** — the dearest single run (parallel CAP at pessimistic η = 0.65) is
  **$13.82 ≪ $25**. Parallel raises core-min ~1/η vs serial, but the box-time bill stays under the
  per-run unit.
- **The win is WALL TIME:** POINT ~12 h and CAP ~34 h (~1.4 d) at 8 ranks, versus ~3.3 d / ~7.3 d serial.
  Whether to *spend* the parallel compute in the M6 window remains a heat-transfer + chief scheduling
  call; the run stays **HELD**.

**Does it exceed $25/run? NO.** The dearest single run is the fine transient at its CAP = 10 507 core-min
= 175.1 core-h × $0.0513 = **$8.98 ≪ $25.** Well inside Sanaa's 2026-08-21 blanket, still costed here per
rule 12. **BUT the binding constraint is WALL TIME, not dollars:** a **3.3-day POINT / up-to-7.3-day CAP
single-rank** solve on the shared 16-core box while it is under M6 pressure is a capacity/scheduling call
for the chief — this is why the run is **HELD**. (See §8: parallelising, i.e. ranks > 1, leaves
core-minutes ~unchanged but is the lever that cuts wall time, and touches the F15 ruling.)

**Rejected option — a 3-mesh transient triple for a GCI.** Coarse + medium + fine transient runs, to
attempt a time-averaged Roache triple, would cost roughly fine + (fine/4) + (fine/16) ≈ **1.33 × the
fine POINT ≈ 6 200 core-min, ~$5.3, still under $25/run** — but it is **rejected on physics grounds, not
cost**: the coarse/medium meshes do not sustain the unsteadiness (§3), so the triple would be
incoherent. Recorded so the choice is visible, not hidden.

---

## 6. Scripts — NAMED, and the completion adaptation that TOUCHES Sanaa's rule-4 clause 5

All under `verification/runs/T-family/T4f_runs/` (DRAFT; the supervisor reads each as a diff at the §3
review):

- **`build_t4f.py`** — imports the FROZEN `build_t4e.block_mesh_dict` (byte-identical fine mesh) and the
  FROZEN `build_t4.fields()` / `constant_files()`; provides a NEW **transient** `system_files()`
  (application → `buoyantBoussinesqPimpleFoam`, fixed `deltaT`, `endTime` 0.08, PIMPLE block, `backward`
  ddt, `fieldAverage` + `sampledSets` functionObjects) **and writes `system/decomposeParDict`** (`method
  simple`, `numberOfSubdomains 8`, `simpleCoeffs (4 2 1)`; refuse-guard: coeff product == ranks, z-split
  == 1). Refuse-guards on every derived change from the frozen writer (as `build_t4e` does). **Drafted.**
- **`analyse_t4f.py`** — the time-averaged comparator: imports the FROZEN `analyse_t4`
  (`sample_profile`, `peak_of`, `planted_zero_control`, `classify`, `gci`), performs the `UMean → U`
  scratch promotion + its NEW planted control, applies C1/C1b/C2/C3/C4/C5 and the reused band, and
  records **no triple / no GCI** (§3). **Drafted.**
- **`stationarity_t4f.py`** — the NEW instrument (S1/S2 stationarity + window adequacy + period), with
  the NEW two-/three-arm planted control (§4c). Reads the instantaneous G-row peak series through the
  FROZEN `analyse_t4.sample_profile`/`peak_of`. **Drafted.**
- **`mark_done_t4f.py`** — strict completion (rule 4) + age guard, adapted for a transient. **See the
  FLAG below.** **Drafted.**
- **`launch_t4f.sh`** — the **PARALLEL** launcher (DRAFTED, `bash -n`-clean): `checkMesh`, arm `0.orig →
  0` with `0/T` touched **last**, **`decomposePar`**, then **`mpirun -np 8 <solver> -parallel`** in the
  wrapper foreground under `timeout` (no `setsid` between `timeout` and `mpirun`, so `$?` is the solve
  rc — the setsid-parent discipline), then **`reconstructPar`**, then write `STATUS.T4f_IJ_f`
  (`rc` = solve rc; `decompose_rc`/`reconstruct_rc` as infrastructure witnesses). Reads the registered
  `timeout_s` and `nRanks` and refuses a mismatch (a cap/rank is not changed at launch). Adapted from the
  frozen `launch_t4e.sh`; the supervisor diffs it against that at the §3 review.
- **`t4f_registered.json`** — the machine-readable registration (bands, controls, S1–S4, cost, solver).

### THE CLAUSE-5 FLAG — this touches Sanaa's rule-4 clause 5 and needs her ruling

The frozen `mark_done_t4e.py` clause 5 is hard-wired `n_exec == int(endTime)` (line 136), which is the
**deltaT = 1 STEADY form**: for a steady SIMPLE run `endTime` *is* the iteration count, so the
ExecutionTime-line count equals it. For a transient run with `deltaT = 8e-7` and `endTime = 0.08`,
`int(endTime) = 0`, so the frozen clause 5 would spuriously fail. `mark_done_t4f.py` therefore
**generalises clause 5 to `n_exec == round(endTime / deltaT)` = the number of time steps** (reading
`deltaT` from the case's own controlDict).

- This is the **minimal, faithful** generalisation: clause 5 exists to catch a truncated log
  (steps-recorded == steps-that-should-have-run); `round(endTime/deltaT)` is exactly that count.
- **Choosing a FIXED dt (adjustTimeStep OFF) keeps the generalisation EXACT and INTEGER** —
  `endTime/deltaT` is a whole number by construction (deltaT chosen to divide endTime). This is the
  reason the design commits to a fixed dt rather than an adaptive one.
- **If an ADAPTIVE dt were used instead, this clause degrades badly**: the step count is not knowable a
  priori, `int(endTime)` is meaningless, and even `last time == endTime` becomes a floating-point
  comparison. That would be a **worse** touch of clause 5. The design therefore recommends fixed dt.
- **This is a genuine touch of CLAUDE.md rule 4's clause-5 WORDING** ("ExecutionTime count == endTime").
  It must not be made on a lane's or supervisor's say-so. **Precedent:** the `phi`-field addition to
  rule 4 was made only on **Sanaa's approval (2026-09-06)**, aligning the rule with its enforcing
  instrument. The supervisor must carry this clause-5 generalisation to Sanaa the same way **before
  freeze**. Until then it is a flagged open item, not a settled clause.

---

## 7. Predictions — prediction-first loss modes

- **P1 / L1 — the premise (the run sustains stationary unsteadiness).** PREDICTED: the transient URANS
  on the fine mesh reaches a **statistically-stationary unsteady state** (limit cycle / shedding) that
  a time-average is meaningful over. **LOSS:** if kOmegaSST URANS **damps to steady**, the time-average
  = the steady value — a MEASURED finding that URANS *also* renders the flow steady, which would point
  the D1/D2/D3 discriminator back toward D2/D3 (a numerical / longer-transient explanation of T4d's
  fine non-convergence) rather than physical unsteadiness. **Not a fail — a measured discriminator**,
  reported via S2's steady branch.
- **P2 / L2 — band containment.** PREDICTED: the time-averaged peak U/U_bulk lands **in** the ERCOFTAC
  bands, and closer to the reference than the T4d fine steady values, which were all **below** band (G1
  1.0591 dev −0.0299; G2 0.6615 dev −0.1273; G3 0.4403 dev −0.0229). **LOSS:** if a row is still outside
  band, **GATE FAIL** — a real joint statement about the kOmegaSST closure and the resolved
  unsteadiness, not a tooling artefact.
- **P3 / L3 — stationarity within budget.** PREDICTED: stationarity by T_init = 0.03 s and ≥ N_min = 20
  periods in the window. **LOSS:** if t_stat > 0.03 or the window holds < 20 periods, **NOT A RESULT**
  → continuation (larger discard / longer window). A disclosed contingency, not a fail.
- **P4 / L4 — the transient runs where the steady solver could not.** PREDICTED: PIMPLE integrates the
  unsteadiness the steady SIMPLE solver rendered as a non-converging limit cycle. **LOSS:** if the
  transient itself is numerically unstable (Co blow-up, divergence), that is an **infrastructure
  finding → triage** (a crash is a finding until triaged), never a physics verdict.

---

## 8. Open questions for the supervisor / chief

1. **Clause-5 ruling (§6).** The transient completion generalises rule 4's clause 5 from
   `n_exec == int(endTime)` to `n_exec == round(endTime/deltaT)`. This touches Sanaa's rule-4 wording
   and needs her approval before freeze (phi-addition precedent). **This lane cannot self-authorise it.**
2. **Fixed vs adaptive dt.** The draft commits to **fixed dt** to keep clause 5 exact/integer and Co
   bounded by a probe-pinned value. Confirm this is preferred over adaptive dt (which would need the
   worse clause-5 form and a floating-point last-time check).
3. **ranks — RESOLVED (admissibility).** Verification GRANTED parallel decomposition (ruling `19b7330a`;
   §5b): **ranks = 8, `method simple`**. F15's serial rule protects a grid-convergence order fit, which
   T4f does not have. Whether to **spend** the parallel compute in the M6 window is a heat-transfer +
   chief scheduling call; the run stays HELD. Confirm the DRAFT `simpleCoeffs (4 2 1)` and η = 0.80 at
   the §3 review.
4. **Scheduling / HELD window.** A multi-day single-tenant fine leg while the box is under M6 pressure is
   a cross-family/daemon capacity call for the chief (same class as T4e's held fine leg, larger).
5. **N_min, T_init, T_end, ε values.** The registered N_min = 20, T_init = 0.03 s, T_end = 0.08 s,
   ε_stat/ε_avg/ε_dt = 1e-3 are prediction-first choices grounded in St ≈ 0.5 and D/U_bulk; the
   supervisor should confirm them (and the St ≈ 0.5 basis) before freeze. The calibration probe also
   sharpens T_init (it exposes the early transient length).
6. **Solver detail:** confirm `buoyantBoussinesqPimpleFoam` PIMPLE settings (nOuterCorrectors 2,
   nCorrectors 2, `backward` ddt) at the §3 review; these are URANS-standard but are a registration
   choice.

---

## 9. What this rung cannot see (stated up front)

- **No GCI, no observed order, no discretisation bound** — one mesh, no triple (§3). This is a
  **validation**, not a mesh-verification.
- **No Nu row** is graded (BLOCKED, T4 §2.1); a band PASS on G1–G3 is a joint code-plus-closure
  statement about the time-averaged velocity field.
- **URANS resolves only large-scale unsteadiness** — nothing here is an LES or a claim about the
  turbulence spectrum; the wedge is one 2.5° sector, so nothing about azimuthal structure.
- A confirmed stationary-unsteady state **discharges the T4e D1 route as a MEASURED finding** (steady
  RANS renders an intrinsically unsteady jet as a limit cycle; URANS integrates it); it does not,
  by itself, prove the reference — that is L2's band gate.
- Nothing here authorises a launch or a send (**rule 7**). No frozen T4/T4b/T4c/T4d/T4e file is modified.

---

## 12. The freeze set — grading path to be FIXED BY SHA at freeze (TEMPLATE, not yet frozen)

To be filled at the freeze commit (`git hash-object` blobs of the exact committed files):

| file (grading path) | git blob | note |
|---|---|---|
| `verification/runs/T-family/T4f_runs/build_t4f.py` | _(at freeze)_ | frozen `build_t4e` mesh import + transient `system_files()` behind refuse-guards |
| `verification/runs/T-family/T4f_runs/analyse_t4f.py` | _(at freeze)_ | frozen `analyse_t4` import + `UMean→U` promotion + its planted control; no triple/GCI |
| `verification/runs/T-family/T4f_runs/stationarity_t4f.py` | _(at freeze)_ | NEW instrument; S1/S2/period; three-arm planted control; selftest both interpreters |
| `verification/runs/T-family/T4f_runs/mark_done_t4f.py` | _(at freeze)_ | rule 4 + age guard; **clause-5 generalisation pending Sanaa's ruling (§6)** |
| `verification/runs/T-family/T4f_runs/launch_t4f.sh` | _(at freeze)_ | PARALLEL: decomposePar → mpirun -np 8 -parallel → reconstructPar; in-wrapper rc; 0.orig→0 last; `bash -n` clean |
| `verification/runs/T-family/T4f_runs/t4f_registered.json` | _(at freeze)_ | bands/controls/S1–S4/cost/solver |

**Frozen imported members (build-time and grading-path), pinned by blob at freeze:**

| frozen import | git blob | imported by | provides |
|---|---|---|---|
| `verification/runs/T-family/T4_runs/analyse_t4.py` | `6f362447` | `analyse_t4f.py`, `stationarity_t4f.py` | `sample_profile`, `peak_of`, `classify`, `gci`, `planted_zero_control`, `latest_time` |
| `verification/runs/T-family/T4e_runs/build_t4e.py` | _(pin at freeze)_ | `build_t4f.py` (build-time) | `block_mesh_dict` (byte-identical fine mesh) |
| `verification/runs/T-family/T4_runs/build_t4.py` | `ff032f3e` | `build_t4f.py` (build-time) | `header`, `grading_ratio`, `system_files`, `constant_files`, `fields` |
| `scripts/roache_triple.py` | `78e56a3b` | `analyse_t4f.py` | `STAGNANT_FLOOR` (0.5), `P_MIN` (0.05) |

**WITHHELD until a supervisor-run STAGED launch phase in a later box window:** the build
(`blockMesh`/`checkMesh` birth certificate), the calibration probe, and the queue entries. Launch is
HELD for box capacity. Nothing here authorises a launch or a send (rule 7).

*Drafted by a heat-transfer `lab-lane`, 2026-09-08, for the supervisor's §3 check and the chief's
rule-12 costing. Zero solver core-minutes. Not committed by this lane. Not frozen.*
