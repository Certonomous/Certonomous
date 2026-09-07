# T4c — impinging round jet, H/D = 2, Re = 23 000: the RE-RUN successor of T4b that changes what failed — pre-registration (FROZEN)

> **STATUS AT THIS COMMIT: FROZEN, BEFORE ANY SOLVER HAS ITERATED ON ANY `T4c_IJ_*` CASE.**
> NOT BUILT. NOT ENQUEUED. NOT LAUNCHED. **Zero solver core-minutes have been spent on this rung.**
>
> **The grading path is fixed by sha in §12 below** (the five-file freeze set, computed with
> `git hash-object` and sha256 on the exact committed files; the frozen comparator verifies at
> runtime by hashing each file against its committed blob). The heat-transfer supervisor's
> non-delegable §3 checks are complete (2026-09-07): the `analyse_t4c.py` and `mark_done_t4c.py`
> diffs read as rename-only, `build_t4c.py` confirmed to implement exactly the three ruled changes
> each behind a refuse guard, and the relaxation fork RULED (Change B IN the design, §2). **The
> build (`blockMesh`/`checkMesh` birth certificate) and the queue entries remain WITHHELD** — the
> fire order is the supervisor's, a separate phase after verifying this freeze commit exists.
> Nothing here authorises a launch or a send (rule 7: SUBMISSIONS REMAIN PARKED).

**Predecessor: T4b** (`docs/campaigns/T-family/T4b_PREREGISTRATION.md`; grade record
`docs/campaigns/T-family/T4b_RESULTS.md`, **`NOT A RESULT` ×3, all at gate (1)**;
`gate_t4b.json` in `verification/runs/T-family/T4b_runs/`). T4c is that record's successor the way
T3f is T3e's and T3g is T3d/T3e/T3f's — the predecessor is named here explicitly so the §2ay
enforcement check sees the successor linkage. **T4c carries over every band, reference, threshold,
floor and control of T4b UNCHANGED** (T25 ruling: a band, threshold or reference is never widened
to manufacture a pass). What changes is the mesh resolution, the solver's under-relaxation, and the
`endTime` schedule — the three things the T4b run measured to be wrong — and nothing else.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.**

---

## 0. Why a successor, and why it is a RE-RUN and not a diagnosis

T4b returned `NOT A RESULT` ×3. **The mesh family behaved** — all three Roache triples came out
`CONVERGING` (prediction P8 hit), so the rung did not fail on grid convergence. **The run schedule
did not** — every row was stopped by gate (1) on five control failures across the three levels
(`T4b_RESULTS.md` §3):

| # | level | control | measured | requirement | miss |
|---|---|---|---:|---:|---:|
| 1 | c | C2 `U_c/U_bulk` | 1.1746 | ≥ 1.1878 (−3 % of 1.2245) | pipe/centreline under-resolved |
| 2 | c | C6.1 `p_rgh` floor | 2.121e-06 | ≤ 1e-06 | 2.12× |
| 3 | m | C6.2 growth ratio | 1.1366 | ≤ 1.05 | field still moving |
| 4 | m | C6.3 field change | 2.848e-04 | ≤ 2e-04 | 1.42× |
| 5 | f | C6.3 field change | 8.170e-04 | ≤ 2e-04 | 4.09× |

Sanaa's law is that **the only acceptable terminal fail is a measured OpenFOAM capability gap;
everything else is fixed until it runs.** None of the five is a capability gap. T4c fixes each with
a registered change and re-runs. **This draft's design rests on a read of the T4b run logs
(`verification/runs/T-family/T4b_runs/T4b_IJ_{c,m,f}/log.solve`), reported in §5**, and that read
CORRECTS the first-pass diagnosis in one respect that matters (limb 3/4, the medium level).

## 1. The case — inherited from T4b §1 unchanged

Normally-impinging round air jet from a fully developed pipe (recycling `mapped` inlet), H/D = 2,
Re_D = 23 000, D = 0.02 m, ν = 1.5e-05 m²/s, U_bulk = 17.25 m/s, Pr/Pr_t = 0.71/0.85, plate at
1000 W/m², jet 293.15 K; `buoyantBoussinesqSimpleFoam` (β = 0, passive T), `kOmegaSST`, steady,
axisymmetric 2.5° wedge, wall-resolved on every level. **All boundary conditions per field per
patch, `transportProperties`, `turbulenceProperties`, `g` and `fvSchemes` are the frozen
`build_t4.fields()` / `constant_files()` / `system_files()` output, unchanged** — the same writers
T4b called. Reference: ERCOFTAC Classic Collection case025 `ij2lr`, HELD at
`docs/campaigns/T-family/reference-data/ercoftac_case025/`, re-read at every run.

## 2. The three registered changes against T4b, and NOTHING else

**Change A — jet-core/pipe radial resolution DOUBLED, family-wide.** `build_t4c.py`'s
`block_mesh_dict` sets the jet-core/pipe radial division `nrj = 3N/2` (T4b: `3N/4`); the wall-jet
radial (`3N/2`), axial (`N`) and pipe-axial (`N/2`) divisions are unchanged, so **`r = 2` is
preserved exactly in every direction** and cells become **3.75 N²** (T4b: 2.625 N²).

| level | `N` | cells (T4b → T4c) | jet-core/pipe radial (T4b → T4c) |
|---|---:|---:|---:|
| `T4c_IJ_c` | 48 | 6 048 → **8 640** | 36 → **72** |
| `T4c_IJ_m` | 96 | 24 192 → **34 560** | 72 → **144** |
| `T4c_IJ_f` | 192 | 96 768 → **138 240** | 144 → **288** |

*Ground (§5.3):* coarse C2 (`U_c/U_bulk` = 1.1746) is **resolution-limited, not pipe-length
limited** — it converges monotonically with global refinement (c 1.1746, m 1.1909, f 1.2021, toward
the 1/7-law 1.2245), and the T4b medium level, which carries 72 jet-core-radial cells, PASSES C2 at
1.1909. The T4b inverted radial grading (fine at the pipe wall for the C1b y+ gate) starves the
axis, under-resolving the centreline exit peak. Doubling the radial count with the first cell fixed
gives a gentler grading and finer axis cells — resolving the peak — **without touching the wall cell
height**, so C1 (plate y+) and C1b (pipe-wall y+, T4b margin 0.398 ≪ 1) are unaffected. The
refinement also lowers every level's residual plateau, which is why it is the coarse-C6.1 fix too
(§5.2). **A longer inlet pipe is the WRONG fix and is rejected on the data**: a length deficit would
depress `U_c/U_bulk` on all three levels together, not converge it away under refinement.

**Change B — under-relaxation of U, T, k, ω reduced 0.7 → 0.6, family-wide** (p_rgh 0.3 unchanged).
**INCLUDED in the frozen design by the heat-transfer supervisor's §3 ruling (2026-09-07), not
sequenced as a contingency.** `build_t4c.py`'s `system_files()` applies this to the inherited
(frozen) `fvSolution` alongside the T4b `residualControl` removal. *Ground (§5.1):* the medium C6.3
failure is NOT a decaying transient — the medium velocity residual **plateaus in a limit cycle** at
~7.3e-7 (COV 0.28) from ~15 000 iterations on, so more iterations alone cannot clear it, and
mesh+endTime **alone** leave the medium at ~2.14e-04 (still failing; §7 P5). A modest under-relaxation
reduction damps the limit cycle so the residual decays instead of oscillating. **The limit cycle is
NUMERICAL, not physical unsteadiness** — an independent blind diagnostic (which did not read this
draft) confirmed the character (COV 0.298, period ~900–1000 iterations, onset ~9–10.5k), and the
finer, more-resolved fine level decays *cleanly* rather than oscillating *more*, the opposite of what
a physical instability would do; this is therefore NOT the K0f/T8 transient class, and relaxation is
the correct remedy. **This changes only the iteration PATH, never the converged fixed point**: the
graded G1/G2/G3 values are a property of the mesh and discretisation, unchanged by relaxation, so
this moves no band and games no gate. It is a convergence fix, exercised through the same C6 controls.

**Change C — the `endTime` schedule.** 20 000 / 30 000 / 40 000 → **30 000 / 60 000 / 64 000**
(§3). `writeInterval` is **PINNED to 2 000 / 3 000 / 4 000** and `purgeWrite 2` is unchanged, so **C6.3
measures a change over the identical iteration window it measured in T4b** — the measurement is not
shortened to manufacture a pass. (The frozen `build_t4` writer derives `writeInterval = endTime/10`,
which for these endTimes would give 3 000 / 6 000 / 6 400; `build_t4c.py`'s `system_files()` overrides
it to the pinned values, refusing unless exactly one `writeInterval` line is changed and `endTime` is
an exact multiple of it — so the last checkpoint always lands on `endTime`.)

Everything else — every BC, scheme, transport property, the wedge, the three graded stations, the
bands, the references, all controls C1–C6 with their thresholds and floors, and every planted-zero
control — is carried over from T4b unchanged (§6).

## 3. The `endTime` schedule, sized arithmetically against the 2e-04 C6.3 floor

C6.3 (max over G1/G2/G3 of |peak `U/U_bulk` change between the last two checkpoints|) decays with
iteration at the same geometric factor ρ as the velocity residual, because for a fixed-point
iteration settling as `x∞ + A·ρⁿ` the change over a fixed window ∝ ρⁿ. Sizing model:
`C6.3(n) = C6.3(n₀)·ρ^((n−n₀)/W)`, W = writeInterval; target **≤ 1e-04 (2× margin below the 2e-04
floor)**; ρ taken CONSERVATIVELY (the slowest measured tail estimate) and inflated for the finer
mesh + lower relaxation.

| level | T4b C6.3 @ old endTime | measured tail behaviour (§5) | new endTime | predicted C6.3 | margin to floor |
|---|---:|---|---:|---:|---:|
| c | 1.19e-09 | already fully settled; the coarse failures are C2 + C6.1 (mesh, not time) | **30 000** | ~1e-09 | settled |
| m | 2.848e-04 | limit-cycle plateau — Change B breaks it; ×2 iterations let the damped decay reach the floor | **60 000** | **≤ 1e-04** (thin — see §7) | ≥ 2× |
| f | 8.170e-04 | clean decaying transient, ρ ≈ 0.44 per 4 000-it (2nd-half log-regression) | **64 000** | **≤ 8e-05** | ≥ 2.5× |

**Fine arithmetic, shown in full.** To fall from 8.170e-04 to 1e-04 at the measured ρ = 0.44/4000it
needs `k = ln(1e-4/8.17e-4)/ln(0.44) = 2.56` write-interval blocks. The finer mesh (×1.43 cells)
and the lower relaxation (0.7→0.6) both slow convergence; inflating the block count to **6 blocks
(24 000 extra iterations → endTime 64 000)** clears the 2e-04 floor even under a badly pessimistic
ρ = 0.75/4000it: `8.170e-04 × 0.75⁶ = 1.45e-04 < 2e-04`, and at the measured ρ = 0.44 the margin is
enormous (`8.170e-04 × 0.44⁶ = 5.9e-06`). **Coarse** keeps a comfortable `endTime` (30 000, up from
20 000 to cover the relaxation slowdown; it settled by ~4 000 iterations in T4b). **Medium** is
doubled to 60 000: without Change B more iterations do nothing (the plateau is a limit cycle); with
Change B the damped decay needs room, and 60 000 is 2× the T4b value.

## 4. Completion rule and controls — carried over from T4b UNCHANGED

`mark_done_t4c.py` is `mark_done_t4b.py` with only the rung id and case names changed (§8 diff): the
strict all-or-nothing rule (rule 4) stands — `rc = 0`, an `End` line, last time == `endTime`, fields
**`T U p_rgh alphat nut k omega phi`** present at `endTime`, `ExecutionTime` count == `endTime`, and
every field NEWER than the case's own `0/T` (the age guard); infrastructure fields disclosed if
absent, `capped` never a completion conjunct, absent `STATUS` → REFUSE `exit 2`.

## 5. THE T4b LOG READ — the evidence the schedule is built on, and the one diagnosis it corrects

Read-only analysis of the frozen `T4b_IJ_{c,m,f}/log.solve` files; no compute launched, nothing
written to the run tree.

**5.1 The medium level is a limit cycle, not a slow transient — the correction.** The first-pass
diagnosis (T4b §5) reads limb 3/4 as "field still moving, needs longer `endTime`." The velocity
residual (C6.3 is a U quantity) shows otherwise: the medium |U| initial residual reaches ~7.3e-7 by
~15 000 iterations and then **oscillates** (tail mean 7.3e-7, std 2.0e-7, COV 0.28; log-regression
slope over the 2nd half is +3e-6/it, i.e. zero within noise, with inconsistent sign across
sub-windows). A checkpoint pair 3 000 iterations apart therefore differs by the oscillation
amplitude — which is why C6.2 read 1.14 (growing) and C6.3 read 2.85e-4 — and **more iterations at
the same mesh and relaxation leave it there.** This is why T4c does not fix the medium with `endTime`
alone: Change A lowers the plateau and Change B damps the cycle. **An independent blind diagnostic
(2026-09-07, which did not read this draft) confirmed the reading**: coarse = plateaued floor ~2e-6,
medium = limit cycle (COV 0.298, period ~900–1000 iterations, onset ~9–10.5k), fine = still
monotonically decaying (factor ~3 per 4 000-it) — the non-monotonic character across levels confirmed.
**The cycle is numerical, not physical**: the higher-resolution fine level decays cleanly instead of
oscillating more, the opposite of a physical instability, so this is not the K0f/T8 transient class and
under-relaxation is the correct remedy (heat-transfer supervisor's §3 ruling, 2026-09-07).

**5.2 The coarse C6.1 floor is mesh-limited, not time-limited.** The coarse `p_rgh` initial residual
is **dead flat at 2.11e-6 from iteration ~4 000 to 20 000**, against a GAMG solver tolerance of
1e-09 (so it is not solver-tolerance limited). The c→m `p_rgh`-floor ratio is 2.12e-6/1.33e-7 ≈ 16×,
anomalous beside the m→f ratio of ~1.5×, which places the excess on a coarse-mesh resolution
deficit. More iterations cannot lower a flat plateau; the radial refinement (Change A) is the lever.
**Predicted, and disclosed as a prediction (§7): the refined coarse floor drops below 1e-06.**

**5.3 The coarse C2 deficit is resolution-limited (the §2 Change-A ground).** `U_c/U_bulk` =
1.1746 / 1.1909 / 1.2021 across c/m/f — a monotone approach to 1.2245 under refinement, and the
medium (72 jet-core-radial) already clears the −3 % edge (1.1878). Length is ruled out; radial
resolution is the lever.

**5.4 The fine level is a clean decaying transient (the §3 fine sizing basis).** The fine |U|
residual falls from 6.4e-6 at 16 000 to 9.4e-8 at 40 000 and is still decaying at the tail;
2nd-half log-regression gives ρ ≈ 0.44 per 4 000 iterations (last-quarter is faster, 0.35). C6.3
will track this down — the fine is exactly the level the "longer `endTime`" diagnosis fits.

## 6. Controls — every one carried over from T4b, byte-identical readers

`analyse_t4c.py` is `analyse_t4b.py` with only the rung id, the registered-JSON filename and the
case-name prefix changed (§8 diff); **no reader, threshold, band, floor, gate order or planted
control is touched.** It imports the frozen `analyse_t4.py` unchanged, as T4b did. Carried over:

- **C1 / C1b** plate / pipe-wall `y+_max < 1.0` via the solver's own `-postProcess -func yPlus`
  reader, **with the y+ scaling control** (U ×4 → y+ ×2.000000000 exactly, on plate AND pipeWall,
  and the blind generic `postProcess -func yPlus` returning 0 on every patch beside it — the blind
  reader shown blind is what makes the seeing reader's zero evidence).
- **C2** nozzle-exit `U_c/U_bulk` within ±3 % of 1.2245; planted control aimed at the profile's own
  maximum.
- **C3** global mass conservation `|Σφ|/|φ_inlet| < 1e-3`; planted control `φ_in ×1.01` → analytic
  imbalance to 1e-9.
- **C4** planted-zero controls (rule 3), both arms, on EVERY reader on the grading path — G-row
  profile (`PLANT = 1.234e-03`, measured detection floor), y+ (above), exit-line (aimed at the max),
  flux (analytic).
- **C5** strict completion + age guard (`mark_done_t4c.py`, §4).
- **C6.1** every `p_rgh` initial residual over the last 2 000 iterations ≤ 1e-06; **C6.2** directional
  growth ratio ≤ 1.05; **C6.3** max G1/G2/G3 peak `U/U_bulk` change between the last two checkpoints
  ≤ 2e-04.
- **Roache floors** `STAGNANT_FLOOR = 0.5`, `P_MIN = 0.05` imported from `scripts/roache_triple.py`;
  gate order per rule 5 (a non-CONVERGING triple is `NOT A RESULT`; the gate can only turn a verdict
  INTO `NOT A RESULT`).

**Graded rows (carried over, references re-read from the held file):** G1 r/D = 1.0, ref 1.0890,
band [1.0690, 1.1090]; G2 r/D = 2.0, ref 0.7888, band [0.7688, 0.8088]; G3 r/D = 3.0, ref 0.4632,
band [0.4432, 0.4832]. Nu rows remain REPORT-ONLY / **BLOCKED** (T4 §2.1: no first-hand Nu
uncertainty). A PASS on G1–G3 is a joint code-plus-closure statement, not a code-verification claim;
no eigenspace band is armed.

## 7. Predictions — registered as numbers before compute (to land in `T4c_registered.json`)

| id | quantity | point | interval / verdict | ground |
|---|---|---:|---|---|
| P1 | plate `y+_max` c/m/f | ~0.69 / 0.35 / 0.18 | as T4b (first cell unchanged) | Change A does not move the wall cell |
| P1b | pipeWall `y+_max` c/m/f | ~0.40 / 0.20 / 0.10 | < 1 on every level | wall cell unchanged; refinement only helps |
| P2 | coarse `U_c/U_bulk` | 1.191 | **≥ 1.1878 (C2 passes) — THIN, disclosed** | 72 jet-core-radial ≈ T4b medium (1.1909) |
| P2m/P2f | m / f `U_c/U_bulk` | 1.20 / 1.21 | ≥ 1.1878 | already passed in T4b, refinement improves |
| P3 | mass imbalance, all levels | 1e-05 | [0, 1e-04] (C3 passes) | steady SIMPLE at plateau |
| P4 | coarse C6.1 `p_rgh` floor | 5e-07 | **< 1e-06 — a PREDICTION, disclosed** | c→m ratio 16× is a resolution deficit (§5.2) |
| P5 | medium C6.3 | 8e-05 | **≤ 1e-04 — THINNEST, disclosed** | mechanism = Change B (0.7→0.6 breaks the limit cycle, §5.1) + Change A (lower plateau) + Change C (room); pre-change extrapolation WITHOUT relaxation ≈ **2.14e-04 (still failing)**, recorded so the post-run comparison measures what the relaxation bought; damped-decay rate not measured |
| P6 | fine C6.3 | 3e-05 | ≤ 8e-05 | clean decay, 6 blocks, safe to ρ = 0.75 (§3) |
| P7 | G1/G2/G3 fine values | ≈ T4b 1.085 / 0.812 / 0.537 | CONVERGING triples; band position unchanged | different mesh family from T4b — no cross-rung triple; values are context |
| P8 | all three triples | — | CONVERGING | T4b P8 hit; the mesh family behaves |
| P9 | fine limit-cycle contingency | — | **a disclosed contingency, NOT a terminal fail** | the fine level had NOT plateaued at 40 000 (still decaying), so at 64 000 it is predicted to settle; IF it instead limit-cycles at its extended floor (as the medium did), C6.3 will not clear and that is a **measured finding**, remedied by the same deeper under-relaxation as the medium (0.6→0.5), not a re-diagnosis |

**The two disclosed thin margins are P2 (coarse C2) and P5 (medium C6.3).** They are named here in
the T4b discipline: a disclosed thin margin that then fails is the disclosure working, not a
surprise. **The relaxation fork is RULED (Change B is IN the frozen design, §2); the remaining
pre-identified contingencies are costed so they are not new ceilings**: if P2 fails,
`nrj = 2N` (cells 4.5 N², ×1.71 vs T4b); if P5 or P9 fails, under-relaxation 0.6 → 0.5 (the
limit-cycle damping deepened, ~1.4× iterations). **These are sequenced next steps on a measured
finding, not band moves** — the lane records them so a re-cycle is cheap, and none can alter a gate,
band, threshold or floor.

## 8. Instruments and the measurement-script changes, as diffs

The freeze set will live in `verification/runs/T-family/T4c_runs/`: `build_t4c.py`, `analyse_t4c.py`,
`mark_done_t4c.py`, `launch_t4c.sh`, `T4c_registered.json`, and the three case dictionaries after the
build. **Every change from the T4b instrument is a diff read by the supervisor before belief
(`SUPERVISION_CHARTER` §3).** In summary:

- **`build_t4c.py`** (the real logic change): `nrj = (3*N)//2` (Change A); `system_files()` also
  substitutes the four `0.7` relaxation factors to `0.6` (Change B) beside the T4b `residualControl`
  removal, and **pins `writeInterval` to 2 000 / 3 000 / 4 000** (Change C — the frozen writer would
  derive `endTime/10`), each guarded by an exact-count refuse and an `endTime % writeInterval == 0`
  refuse; `LEVELS` `endTime` 30000/60000/64000 and `writeInterval`; `CASE_PREFIX = "T4c_IJ_"`;
  docstring.
- **`analyse_t4c.py`**, **`mark_done_t4c.py`**, **`launch_t4c.sh`**: rung-id / path / case-name
  renames ONLY — **no reader, threshold, band, floor, gate, completion clause or launch guard
  changed.** The frozen `analyse_t4.py` is imported unchanged.

The verbatim unified diffs are carried in the lane's hand-off to the supervisor, not pasted into this
repository document. **Selftest evidence (for the supervisor, not a substitute for the §3 check):**
`analyse_t4c.py --selftest` 20/20 under `python3` and `python3 -O` (the three driven refusals fire);
`mark_done_t4c.py --selftest` PASS, 0 failed, both interpreters (every completion clause driven, the
absent-STATUS refusal fires, AST assert count 0); `build_t4c.py` AST assert count 0 and a scratch
build gives cells 8 640 / 34 560 / 138 240, `writeInterval` 2 000 / 3 000 / 4 000, relaxation 0.6,
no `residualControl`; `launch_t4c.sh` `bash -n` clean and its refusal arms fire (serial-only, wrong
timeout, unregistered case) writing no STATUS.

## 9. Cost — rule 12, from T4b's OWN measured per-cell-iteration rates (the C-155 correction applied)

**Rate basis.** T4b measured `core-s per cell-iteration` **c 6.9940e-06, m 7.1346e-06,
f 9.7543e-06** (`T4b_RESULTS.md` §7). Using T4b's own measured per-level rates for its successor is
exactly the C-155 correction (T13) — the same discipline T4b used against T4, which cut its POINT
miss from 3.17× to 1.41×. The ~4 % rate rise from the ×1.43 cell increase (the coupled-solver
mesh-scaling penalty, `T4b_RESULTS.md` §7: rate ∝ cells^0.12) is absorbed by the CEILING, per the
same section.

| level | cells | iterations | rate (core-s/cell-it) | **POINT core-min** | CEILING (1.5×) | **cap (2×) core-min** | `timeout` s |
|---|---:|---:|---:|---:|---:|---:|---:|
| `T4c_IJ_c` | 8 640 | 30 000 | 6.9940e-06 | **30.2** | 45.3 | **65** | 3 900 |
| `T4c_IJ_m` | 34 560 | 60 000 | 7.1346e-06 | **246.6** | 369.9 | **500** | 30 000 |
| `T4c_IJ_f` | 138 240 | 64 000 | 9.7543e-06 | **1 438.3** | 2 157.5 | **2 880** | 172 800 |
| **total** | | | | **1 715.1** (28.6 core-h) | 2 572.7 (42.9 core-h) | **3 445** (57.4 core-h) | |

Arithmetic, level `c`: 8 640 × 30 000 × 6.9940e-06 = 1 812.9 core-s = 30.2 core-min; likewise `m`
14 795 core-s, `f` 86 297 core-s. **USD, DERIVED not measured, reported-by-owner rate $0.0513/core-h
(`COMPUTE_BUDGET_CHARTER` §5): POINT $1.47, CEILING $2.20, cap $2.94** — inside the $25 pre-authorised
band, and still costed here per rule 12. **OPERATIONAL FLAG for the supervisor: the fine level's wall
time at POINT is ~24 h at ranks 1 (cap 48 h), the single longest run this ladder has scheduled.**
Ranks stay 1 on every level (F15 decomposition-confound ruling: a ladder differs only in mesh). An
overrun stops the run at its cap (`capped=yes` → `NOT A RESULT`, not re-launched larger).
Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at completion (rule 12).

## 10. What this rung cannot see

- No Nu row is graded (BLOCKED, T4 §2.1); a PASS on G1–G3 is a joint code-plus-closure statement.
- **A different mesh family from T4b** (3.75 N² vs 2.625 N²): no cross-rung triple; T4b's numbers are
  context, never a level.
- The refined-mesh + relaxation-0.6 decay RATE is not measured; §3 sizes conservatively and the
  CEILING/cap absorb the misprediction. If a level's C6.3 still exceeds 2e-04, that is a measured
  finding for the §7 contingency, not a terminal fail.
- The wedge is one 2.5° sector: nothing about azimuthal structure.
- Nothing here authorises a launch or a send (rule 7: SUBMISSIONS REMAIN PARKED). No frozen T4/T4b
  file is modified.

## 11. Status

**FROZEN, BUILT? NO — NOT FIRED. Solver core-minutes on this rung: 0.** The heat-transfer
supervisor's §3 checks are complete (2026-09-07): the `analyse_t4c.py` and `mark_done_t4c.py` diffs
read as rename-only; `build_t4c.py` implements exactly the three ruled changes (A nrj 3N/2, B
relaxation 0.7→0.6, C endTimes + the writeInterval pin), each behind a refuse guard; the relaxation
fork is RULED — Change B is IN the frozen design (§2). The grading path is fixed by the §12 freeze
set. **Still WITHHELD until the supervisor's separate launch phase:** the build (`blockMesh`/
`checkMesh` birth certificate) and the queue entries. The supervisor verifies this freeze commit
exists (non-delegable check 4) before authorising any launch.

## 12. The freeze set — committed in the same commit as this document

Git blobs computed with `git hash-object` on the exact files committed; sha256 first 16. The frozen
comparator prints its own `sha256_of()` provenance at runtime (`analyse_t4c.py` `grade()`); verify the
frozen file **is** the file that ran by hashing it against the committed blob below.

| file | git blob | sha256₁₆ | lines / note |
|---|---|---|---:|
| `verification/runs/T-family/T4c_runs/analyse_t4c.py` | **`ec63f0a6`** | `742744660fa13b51` | 753; AST 0; selftest 20/20 (`python3` and `-O`); rename-only from `analyse_t4b.py` (frozen `analyse_t4.py` imported unchanged) |
| `verification/runs/T-family/T4c_runs/mark_done_t4c.py` | **`5b6ed30f`** | `cc121151345a214a` | 256; AST 0; selftest PASS both interpreters; rename-only from `mark_done_t4b.py` |
| `verification/runs/T-family/T4c_runs/build_t4c.py` | **`470a5936`** | `2f72a4a60429483e` | 282; AST 0; the three ruled changes (A/B/C), each behind a refuse guard |
| `verification/runs/T-family/T4c_runs/launch_t4c.sh` | **`0dc9d142`** | `612aded4c468f3f0` | 185; `bash -n` clean; rc-capture architecture carried verbatim; refusal arms fire |
| `verification/runs/T-family/T4c_runs/T4c_registered.json` | **`8889c0af`** | `e29d9575b04e9cf1` | 283; bands, thresholds, caps, floors, predictions P1–P9 (no self-reference: this freeze table lives in the `.md`) |

Frozen inherited instruments, unchanged in the worktree at this freeze (imported, never copied):
`analyse_t4.py` (its readers, `classify`, `gci`, `planted_zero_control`, `sample_profile`, `peak_of`),
`build_t4.py` (`header`, `grading_ratio`, `system_files`, `constant_files`, `fields`),
`scripts/roache_triple.py` (`STAGNANT_FLOOR`, `P_MIN`), `scripts/check_case_provenance.py`,
`scripts/check_launcher_can_launch.py`.
