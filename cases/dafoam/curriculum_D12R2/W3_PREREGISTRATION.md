# W3 — THE THIRD AVERAGING WINDOW FOR THE 2D · UNSTEADY · INCOMPRESSIBLE FD LINE (`W = 2,000`), PHASES 1 → 4 AS ONE DETACHED DRIVER, WITH THE SUCCESSOR COMPARATOR — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-26**. Lane: dafoam `lab-lane` (G, re-spawned). Supervisor: `dafoam-supervisor` (lane G's brief, TASK 3: *"the 2D·unsteady·incompressible cell flips … only with an admissible FD step … the W3 draft must PREDICT the scaling of `δ_window` with W on a stated argument … the `W` key written into the manifest … if the comparator must change, that is a new frozen comparator with the change disclosed and the old one cited … phases 1→4 as ONE detached driver whose later phases refuse for themselves"*). Supersedes `W3_PREREGISTRATION_DRAFT.md` (retained, struck at its head).
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). Permission for the detached launch: Sanaa's own words at **`bc0e687e`**; queue-first `7def3c6b` / `73eccb1b` / `0b041d1a` / `3c3ef86c`; L-342 `d4d0c29d`; the grid as the goal `068c2bf0`. Every decision here is `[lab-attributed]`.

---

## 0. WHAT THIS ITEM IS FOR, AND WHAT IT INHERITS UNCHANGED

**The cell.** `docs/capability/dafoam_GRID.md` (`bd8ffcd8`), 2D · unsteady · incompressible: gradients `CAN DO, CAVEATS — no admissible FD step`; optimisation `CAN NOT DO`. Both flip on one event — an FD-verified unsteady gradient (`G12R-6` band D) that authorises S8 (`G12R-11`, `curriculum_D12R2/PREREGISTRATION.md:277` @ `e6580910`). The event is gated by `G12R-4`: `h_min = δ_eff / (0.01·|g|) ≤ h_max = 0.05`. Measured twice: D12R2 at `W = 300`, `h_min = 0.1743` (`RESULTS.md:12-13` @ `65882eb3`); W2R at `W = 900`, `h_min = 0.15755` on its plan step (run-root `step_plan.json`, `W2R_phase1_grade_replan_20260826T205826Z.json`).

**Inherited unchanged from D12R2 (`e6580910`) and W2R (`5d1f89cd`):** the 33-stage phase-1 graph (S0 · S1a · S1b · S2a · S2b · S3 ×3 · S3b ×16 · S4 ×6 · S5 · S7 ×2), `TRANSIENT_DISCARD = 300`, `S2_STEPS = 2400`, `ENV_STEPS = 20 40 80`, `DPERT_HA/HB = 1e-6 / 1e-5`, `NSHAPES = 4`; every gate `G12R-0` … `G12R-11`, `G12R-W`; `h_max = 0.05`; `EPS_NOISE_TARGET = 0.01`; band D (PASS ≤ 5 %, CONDITIONAL 5–15 %, FAIL > 15 % or any sign flip) at `G12R-6`; the trivial baseline at `10·h*` (`G12R-7`); the envelope `3σ` (`G12R-8`); planted zeros (`G12R-9`); two rows (`G12R-10`; this item, like W2R, buys the SHIPPED row first — `--image shipped` is the launcher's default — and the PATCHED row is a re-fire with `--image patched` into `<root>_p`, registered here and not queued until the shipped row has a plan-step reading); `MEM_LIMIT = 8g`; `MEMAVAIL_FLOOR_GIB = 14.0` (not lowered); the producer `d12y_run_script.py` (md5 `2790c39a…`, unchanged through five items); the aggregate-cap wait-and-retry (`AGG_WAIT_MAX_S = 1200`). **Changed, and only these (§5):** `W_STEPS = 2000`; `CAP_CORE_MIN = 900.0`, `CAP_S8 = 400.0`; the S8 stage wall bound 7,200 → 16,000 s; `CPUSET_CPUS = 1`; the run root; the container-name prefix `d12y_w3_`; G-ROOT.5 on the re-fire phases; **every manifest row carries `"W"`**; and **the SUCCESSOR comparator `d12y_grade_w3.py`** (W3-A1, W3-A2).

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady` DOES NOT EXIST.**

`test -e` → false at **2026-08-26T22:54:09Z** (after the driver selftest, `d12y_w3_groot5_selftest_evidence.txt`: "run root ABSENT after the test"). The launcher's phase 1 creates it and refuses (exit 6) if it exists. **0 core-min spent; no solver container fired** (the selftest's only container was a sacrificial `sleep`, removed). W3-A1 and W3-A2 are pre-compute amendments of the D12R2/W2R item form, legal under `VERIFICATION_CHARTER.md` §2b item 1 because no W3 run directory exists — checked as stated, not asserted.

## 2. THE MEASURED SCALING OF `δ_window` WITH `W` — PREDICTION (a), AND THE MECHANISM CORRECTION

**What the W2R record contains, read before any prediction (re-derived by this lane with the frozen comparator's own `read_series` / `block_averages`, `d12y_grade.py:143-190`).** W2R's S2b series (`S2b_20260826T160035Z_23510.log`, 2,400 `CD:` samples at `Δt = 1e-2`) is **identical sample for sample** to D12R2's (`S2b_20260826T033053Z_3069758.log`; mean `0.6563231414421499`, period 18.9644 steps, p2p 0.13162) — W2R's P1 HIT. **The plan step evaluated `δ_window` at `W = 300` in both items**: `plan()` at `d12y_grade.py:2011` passes the literal `W_PRIMARY` (`g3_delta_window(retained, W_PRIMARY, period_steps=…)`); the `man.get("W", W_PRIMARY)` at `:2511` belongs to the legacy `grade_from_manifest` path and did not run (the draft's citation of `:2511` is corrected here; `dafoam_GRID.md` Correction 1a). So W2R's recorded `h_min = 0.15755 = δ_window(300) / (0.01 · |g(900)|)` with `|g(900)| = 1.13984`, not a `W = 900` noise floor — and **no manifest `W` key could have changed that**; only a comparator that reads the window from the record can (§5, W3-A2).

**The two hypotheses.** Statistical noise: `δ_window ∝ 1/√W` → `h_min(900)/h_min(300) = 0.577`. Deterministic phase residual of a limit-cycle mean over a window of `W` steps that is not a whole number of periods `P`: amplitude `A·|sin(πW/P)|/(πW/P)`, spread `2A·|sin(πW/P)|/(πW/P)` — a **`1/W` envelope with an oscillating factor**, zero at whole periods (the comparator's degeneracy branch).

**The measurement, from the retained series at windows the record never graded:**

| `W` | windows | `δ_window(W)` | `h_min` at `\|g\| = 1.13984` | `h_min` at `\|g\| = 1.03042` |
|---|---|---|---|---|
| 300 | 2,101 | **1.795848e-03** (the graded value, both items) | 0.15755 (= W2R's recorded value) | 0.17428 (= D12R2's) |
| 600 | 1,801 | 1.334082e-03 | 0.11704 | 0.12947 |
| 900 | 1,501 | **9.879556e-04** (= W2R's own P1 prediction, `W2R_PREREGISTRATION.md:93`) | 0.08667 | 0.09588 (= W2R's P4 point) |
| 1,200 | 1,201 | 6.516613e-04 | 0.05717 | 0.06324 |
| 1,500 | 901 | 3.327772e-04 | 0.02920 | 0.03230 |
| 1,800 | 601 | 1.087860e-04 | 0.00954 | 0.01056 |
| **2,000** | **401** | **4.385710e-04** | **0.03848** | **0.04256** |
| 2,100 | 301 | 2.442726e-04 | 0.02143 | 0.02371 |
| 2,200 | 201 | 1.762172e-04 | 0.01546 | 0.01710 |

The planted check on this reader: it reproduces the graded `1.795848e-03` at 300 and W2R's registered `9.879556e-04` at 900 to every printed digit. **The scaling:** `log δ_window` vs `log W` over `W = 100…2375` in 25-step increments has slope **−1.034** over all points and **−1.003** over the 29 local maxima (the envelope). **The statistical hypothesis (slope −0.5) is rejected by the record; the deterministic `1/W` envelope holds.** The envelope constant at 1-step sampling: **`max(W·δ_window) = 0.89065` over `W = 300…2100`** (at `W = 1639`), and within every 300-step band 0.8904–0.8907 — i.e. **`δ_window,env(W) = 0.8907 / W`** (rounded up; frozen as `C_ENV = 0.8907` in the successor comparator), `h_min,env(W) = 89.07 / (W·|g|)`. The sinusoid model with `A = 0.06581`, `P = 18.9644` reproduces the measured values to a factor 0.93–1.29 (harmonics) — the mechanism, not the prediction; the prediction uses the measured envelope. **Uncertainty:** the two graded points (D12R2, W2R) cannot by themselves distinguish the laws because both were graded at the same `W = 300`; the law is measured from the series itself across 92 windows, and its residual against `C_ENV/W` at the local maxima is ≤ 0.3 %.

**Why the envelope, not the exact `δ_window(W)`, sizes the step (W3-A1).** The exact spread has deep minima near whole periods (`W = 1800`: 1.09e-04; `W = 910`: 2.19e-04). Those minima belong to the BASELINE geometry's period; an FD arm perturbs the cylinder by up to `h_max = 0.05` = 10 % of the radius, the shedding period scales with the body (Strouhal fixed), so the perturbed arms' `W/P` shifts by up to ~5 periods and their window residual lands anywhere on the envelope. **A window chosen on a baseline minimum is chosen to fit an answer it will not see.** The frozen degeneracy branch (excluding `δ_window` by name near whole periods and letting `δ_pert = 1.2e-06` carry the floor, `h_min = 1.1e-04`) is unsafe as a step-sizing route for the same reason. W3-A1: `δ_window,used = max(δ_window(W) exact, C_ENV/W)`; the degeneracy flag is reported, never applied.

## 3. PREDICTION (b) — THE WINDOW AT WHICH `h_min < h_max`, WITH ITS UNCERTAINTY, AND THE REGISTERED `W`

Admissibility on the envelope: `89.07 / (W·|g|) < 0.05` ⇔ **`W > 1,781 / |g|`**.

| `\|g\|` assumption | basis | `W*` (first admissible, envelope) |
|---|---|---|
| 1.13984 | W2R measured at `W = 900` | **1,563** |
| 1.03042 | D12R2 measured at `W = 300` | 1,729 |
| 0.95 | −17 % below W2R, the pessimistic edge of a ±15 % band on a quantity that moved +10.6 % per 3× window | 1,875 |
| 1.25 | +10 % above W2R, the optimistic edge | 1,425 |

**Predicted `W* = 1,563`, band 1,425–1,875.** The registered window must clear the pessimistic edge with margin: **`W = 2,000`** (2.22× W2R; 6.67× D12R2), giving `h_min,env(2000) = 0.03907` at `|g| = 1.13984` (margin 1.28× to `h_max`), `0.04322` at 1.03042 (1.16×), `0.04688` at 0.95 (1.07×). The S2b series of 2,400 samples supports `W = 2,000` with 401 sliding windows spanning 21 periods of phase, so S2b is not lengthened (`block_averages` refuses below `W` samples; 2,400 > 2,000). **The `W = 2,400` variant** (S2b lengthened to 4,800 steps, margin 1.28–1.53×, phase-1 cost 236.5 core-min) is the registered fallback if this item returns `admissible: false` — it is NOT this item and is not queued.

## 4. COST — DERIVED FROM THE TWO MEASURED PHASE-1 ANCHORS, NOT MEASURED

**Anchors (ledgers on disk):** D12R2 phase 1 at `W = 300`: **55.5167 core-min** (C-115); W2R phase 1 at `W = 900`: **105.2334 core-min** (`PHASE1_COMPLETE spent=105.2334`); per objective stage `S3_r1` 1.0667 (300) / 2.8167 (900) core-min = 3.1–3.6e-03 core-min per step; S2b 7.08 / 7.02 (fixed 2,400 steps); S5 (adjoint) 10.9 / 26.17. Both runs share the 33-stage graph, so the two-point linear model in `W` is exactly determined: `cost₁(W) = F + V·(W/900)` with `F + V = 105.2334`, `F + V/3 = 55.5167` ⇒ **`V = 74.575`, `F = 30.658`** core-min.

| item | at `W = 2,000` | basis |
|---|---|---|
| **Phase 1 (33 stages) — the C-row** | **196.4 core-min** ($0.168), band ±15 % `[167, 226]` | the two-anchor line; `derived, not measured` |
| Phase 2 (the sweep) | point **37.6** (3 steps `[0.004, 0.04, 0.05]` from `h_min ≈ 0.039` × 2 signs = 6 stages × 6.26); upper 65 (≤ 10 stages) | W2R A2.4 arithmetic scaled by 2000/900 |
| Phase 3 (S6b × 2 + S6c 4 × 2) | **62.6** (10 stages × 6.26); upper 65 | same |
| Phase 4 (S8, one stage) | **≤ 266.7** — the registered per-stage wall bound 16,000 s at np = 1 (W2R's 7,200 s × 2000/900); **no S8 has ever run in this family, so this is a BOUND, not a prediction from a record** (`COMPUTE_BUDGET_CHARTER.md:375-395`: no record, no price — the bound is the honest number) | `timeout 16000` in `run_stage` for S8 |
| **Total point / upper** | **563.3 core-min ≈ $0.48** point (S8 at its bound) / **≈ 593** upper | dollars at $0.0513/core-h, reported-by-owner, **not measured** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| **Caps, registered and asserted by the launcher** | **`CAP_CORE_MIN = 900.0`** (cumulative, evaluated before every stage), **`CAP_S8 = 400.0`** | overrun stops the run (rule 12); the queue entry carries `cap_core_min_registered = 900.0` |

**Calibration commitment:** on completion the actual/predicted ratio for phase 1 is entered in `docs/COST_CALIBRATION.md` against 196.4; the two-anchor model's own test is whether a third window lands on its line (P4).

## 5. THE TWO PRE-COMPUTE AMENDMENTS, THE SUCCESSOR COMPARATOR, AND THE ONE-DRIVER FORM

**W3-A2 — the window is read from the run's own record.** The launcher writes `"W": 2000` into **every** manifest row (both python row-writers, `d12y_w3_stage_and_run.sh`: `row["W"] = int(os.environ["W_STEPS"])`) and `W_STEPS=2000` into the ledger (as W2R did). The successor comparator's `plan()` calls `_w_from_record(rows, ledger)`: it **refuses** if any row lacks `W`, if the rows disagree, if the ledger carries other than exactly one `W_STEPS=` line, if the two disagree, or if the value is not the registered `W_PRIMARY = 2000` — and only then grades `δ_window` at that `W`. **The frozen comparator is NOT edited** (`d12y_grade.py` md5 `02a9ab62…`, blob `aecceb4e…`, cited); `d12y_grade_w3.py` is a **new frozen comparator**, derived from it by the diff `d12y_grade_w3_DELTAS_from_d12y_grade.diff` (223 diff lines: constants `W_PRIMARY 300 → 2000`, `W_CONTINGENCY 900 → 2400`, `CAP_CORE_MIN 600 → 900`, `CAP_S8 350 → 400`, `C_ENV`; `_w_from_record`; the W3-A1 block in `plan()`; `selftest_w3`; nothing else — every gate function is byte-identical).

**W3-A1 — the envelope sizes the step.** In `plan()`: `δ_window,exact = block_max − block_min` (recovered even where the frozen `g3` excludes the term as degenerate and returns `None`), `δ_window,env = C_ENV / W`, `δ_window,used = max(exact, env)`; `g4_delta_eff` is called with `window_degenerate=False` so the term is never excluded; `step_plan.json` records `delta_window_exact`, `delta_window_envelope`, `W`, `C_ENV` beside `h_min`. Adding a term to a maximum can only RAISE `h_min` (the D12R2 ruling's own argument): it can cause a `NOT A RESULT`, it cannot manufacture a `PASS`.

**Selftests, run under `python3` and `python3 -O` (`d12y_grade_w3_selftest_evidence.txt`):** the successor's `--selftest-w3` **12/12** both flags (rows without `W` / disagreeing / ledger 900 vs rows 2000 (the W2R shape) / no ledger line / two lines / 300 ≠ registered → all REFUSED; the envelope at 2000 = 4.4535e-04 carries over an exact 3.96e-04 on a synthetic series; at a near-degenerate `W = 891` the frozen `g3` returns `None` and W3-A1 recovers 4.85e-05 exact with the envelope 1.00e-03 carrying the floor; `g4_delta_eff` accepts it; step sizing at `|g| = 1.13984` gives `h_min = 0.03907` admissible, at `|g| = 0.85` not admissible); the inherited `--selftest` (the frozen comparator's own planted controls) **still passes** both flags on the successor; `ast.Assert` count outside the selftest function: 0 (the 59 inside `selftest` are the frozen file's, disclosed at its `:972`).

**The one-driver form (`d12y_w3_chain_driver.sh`, md5 `5ed357e1…`).** One detached process runs `--phase 1` → `--plan` → `--phase 2` → `--plan2` → `--phase 3` → `--plan3` → `--phase 4`, **stopping at the first non-zero rc and recording every rc in `STATUS.W3_chain`** in the case directory (never the `$?` of a `setsid` line; each step's output in `W3_<step>.out`). **The driver evaluates no precondition**: each later phase refuses for itself — the launcher's `[ -f step_plan*.json ] || ABORT exit 1`, its registered no-launch branches (`admissible: false` → phase 2 launches nothing, exit 0; `h_star = None` → phase 3 nothing; `optimisation_authorised ≠ True` → S8 nothing), and the comparator's plan modes exit 2 on a Refusal (e.g. `--plan2` with no S6 stages). **A stop at a registered no-launch branch is the registered terminus** (§7), never a driver failure; the four W2R wait-wrappers still waiting at their bounds are the lesson this form removes — there are no separate runner entries for phases 2–4 and no wrapper waits on an artefact a no-launch branch will never write. The driver's own G-ROOT.5: a running `d12y_w3_` container or a live sibling driver refuses (`rc=3`) before anything; an existing root refuses (`rc=6`) because phase 1 requires an absent one — **driven 7/7 (`d12y_w3_groot5_selftest_evidence.txt`, 22:54:09Z)** with a sacrificial `sleep` container, a live sacrificial pid in a temporary root, and a stale pidfile; no step output written; the temporary root absent afterwards. The launcher's re-fire phases (2–4) carry the same G-ROOT.5 reading before any stage's `rm -rf`.

**`rc` from inspect, placement, memory (as W2R, brief):** container `rc` read from `docker inspect .State.ExitCode|OOMKilled` before `docker rm` (`run_stage`); `CPUSET_CPUS = 1` (**the supervisor's placement for W3; W2R's was 12**), `--cpus=1`, np = 1; `MEM_LIMIT = 8g` (D12R2 phase-1 peak RSS 1.3461 GiB, S4 envelope flat in `n`), `MEMAVAIL_FLOOR_GIB = 14.0` (refuse-per-stage, not lowered), aggregate cap wait-and-retry bounded 1,200 s. The unsteady adjoint's memory at `W = 2,000` (checkpointing) is NOT measured: S4's `n = 20/40/80` envelope measured RAM flat (1.3145 → 1.3129 GiB), so 8g is ~5.9× the measured peak and the item relies on the per-stage OOM kill (`--oom-score-adj=500`) as its guard — an S5 OOM is `BLOCKED` (§7), stated in advance.

## 6. PREDICTIONS P1–P5 — HIT/MISS, scored by the successor comparator and the record, never adjusted

| # | prediction | HIT form | MISS form |
|---|---|---|---|
| **P1** | W3's S2b (2,400 steps, unchanged staging) is bit-identical to W2R's, so `δ_window,exact(2000)` reproduces the pre-computed value | `delta_window_exact = 4.385710e-04` to the printed digits in `step_plan.json` | any other value — a non-deterministic primal or a staging change; P1 MISS does not move P3's reading, which uses the envelope |
| **P2** | `\|g(2000)\|` (the `S5` adjoint's `dobj_dshape[0]`) | in **`[1.01, 1.37]`** (1.19 ± 0.18: W2R's 1.13984 continued at +10 % per window tripling, ±15 %) | outside the band |
| **P3 (PRIMARY, BINARY)** | **an admissible FD step EXISTS at `W = 2,000`**: `h_min = 100 · max(δ_window,exact, 0.8907/2000, δ_repeat, δ_pert) / \|g\| ≤ 0.05` | `step_plan.json` `admissible: true`; point `h_min = 0.0391` (envelope at `\|g\| = 1.13984`); steps `[0.004, 0.04, 0.05]` | `admissible: false` — **falsified iff `\|g(2000)\| < 0.8907`** (envelope) — the registered no-launch branch fires, phase 2 launches nothing, the driver stops at `--plan2`'s refusal: the registered terminus |
| **P4** | phase-1 cost lands on the two-anchor line | **`196.4 ± 15 %` core-min `[167, 226]`** from the ledger's `PHASE1_COMPLETE spent=` | outside — re-anchors the model, does not re-cost the run |
| **P5** | conditional on P3 HIT and `G12R-6 PASS` (band D at `h*`): S8 is authorised (`optimisation_authorised: true` in `step_plan3.json`) and reaches its registered terminus | S8 log carries `EXIT: Optimal Solution Found.` → item **`PASS`**; or stops on `CAP_S8` / the 16,000-s bound → **`GATE REACHED`** (`DAFOAM_CHARTER.md` §9), the registered terminus | `G12R-6 GATE FAIL` (outside band D or a flip) → S8 not authorised, `S8 NOT LAUNCHED` in the ledger — a MISS that is itself the finding; a `G12R-6` **number is deliberately not predicted** (no unsteady FD number exists in this family in any direction) |

## 7. VERDICT MAPPING (the item's, in the fixed vocabulary) AND THE GRID CONSEQUENCE

| outcome | item verdict | grid cell (gradients / optimisation) |
|---|---|---|
| P3 HIT, `G12R-6 PASS`, S8 `Optimal Solution Found.` | **`PASS`** | `CAN DO` / `CAN DO` (caveat ≤ 1 line: single mesh, 2,450 cells) |
| P3 HIT, `G12R-6 PASS`, S8 stopped on `CAP_S8` or its wall bound | **`GATE REACHED`** | `CAN DO` / `CAN DO, CAVEATS` |
| P3 HIT, `G12R-6 GATE FAIL` | **`GATE FAIL`** | `CAN DO, CAVEATS` (FD-checked, disagrees) / `CAN NOT DO` |
| P3 MISS (`admissible: false` at 2,000) | **`NOT A RESULT`** — the registered no-launch branch; phases 2–4 never fire | unchanged; the record states `\|g(2000)\|` and the envelope, and the `W = 2,400` fallback is computable from them |
| any refusal (completion, planted zero not seen, manifest/ledger `W` mismatch, `G12R-0b` row count) | **`NOT A RESULT`** | unchanged |
| aggregate-cap bound, `MemAvailable` floor, an S5 OOM, a PETSc failure | **`BLOCKED`** | unchanged |

## 8. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | status |
|---|---|---|
| `d12y_grade_w3.py` | `f3c1252c11fb94a3d4c580fdcbe7a62d` | **the grading path — the SUCCESSOR comparator**; from `d12y_grade.py` (`02a9ab62…`, blob `aecceb4e…`, UNEDITED) by `d12y_grade_w3_DELTAS_from_d12y_grade.diff` (223 lines); `--selftest-w3` 12/12 and the inherited `--selftest` PASS, both under `python3` and `-O` |
| `d12y_w3_stage_and_run.sh` | `fc7585cf27736593bf3df198e5d73836` | from `d12y_w2r_stage_and_run.sh` (`736aa849…`, UNEDITED) by `d12y_w3_stage_and_run_DELTAS_from_w2r.diff` (157 lines): root, `GRADEPY`, caps, `W_STEPS = 2000`, `CPUSET_CPUS = 1`, instrument list, ledger `ITEM`, container prefix `d12y_w3_`, S8 wall bound 16,000 s, the `W` key in both row-writers, G-ROOT.5 on phases 2–4; it asserts every instrument's md5 against the committed HEAD blob before staging |
| `d12y_w3_chain_driver.sh` | `5ed357e1f25b4f413d05f8b6a6680e75` | new; carries the launcher and comparator md5s; G-ROOT.5 driven 7/7 (`d12y_w3_groot5_selftest.sh` `c277331b…`, evidence file beside it) |
| `d12y_run_script.py` | `2790c39a09cd458d5a3263d7f1811da5` | the producer, unchanged through D12R / D12R2 / W2 / W2R / W3 |
| `W3_PREREGISTRATION_DRAFT.md` | struck at its head, retained | the draft this file supersedes |

**No `assert` carries a guard** outside the frozen selftest function (L-332). **Classifier denials in this lane while building W3: none.**

## 9. WHAT THIS ITEM WILL NOT ESTABLISH

Nothing about the PATCHED row until it is re-fired (`--image patched`, `<root>_p`) — the two-row rule is carried, not discharged, by the shipped row alone; nothing on a second mesh (2,450 cells, no grid family, **no GCI**); `St ≈ 0.53` remains a resolution artefact, never a Strouhal number; the envelope constant is the BASELINE series' — the perturbed arms' series are not on record at any window; the unsteady adjoint's memory at `W = 2,000` is not measured; the S8 cost is a bound, not a prediction.

## 10. FREEZE AND QUEUE

**Committed BEFORE any container starts** (rule 2). The grading path is fixed at this commit: `d12y_grade_w3.py` md5 `f3c1252c11fb94a3d4c580fdcbe7a62d`, asserted by the launcher against the HEAD blob before staging and by the driver before each step. **Queue entry `verification/queue/dafoam/W3_chain.json`:** team `dafoam`, `prereg_commit` = the sha of the commit introducing this file, `launch_cmd` = `["bash", "<abs>/d12y_w3_chain_driver.sh"]`, `cwd` = this directory, `ranks 1`, `cost_core_min_estimate 563.3`, `cap_core_min_registered 900.0`, `memory_floor_gb 14.0`, `cost_basis` derived / not measured, `permission bc0e687e`. Enqueueing is not authorisation: `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own, discharged on the sha. **Predicted outcome:** P1–P4 HIT, phase 2 fires at `[0.004, 0.04, 0.05]`, `G12R-6` graded for the first time on an unsteady objective in this family; P5 undetermined by design.

---

## 11. AMENDMENT 1 — 2026-08-27, PRE-COMPUTE. Two launcher defects; the registered caps do not move.

**Version 1.1.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (B). Supervisor: `dafoam-supervisor` (ruling `[lab-attributed]`; check 1 discharged — the supervisor read `d12y_w3_stage_and_run.sh` and `d12y_w3_chain_driver.sh` as diffs against HEAD personally and recomputed the driver's launcher pin before approving). **Lines whose number changed above this section: 0. Bytes changed above this section: 0** — this amendment is appended at the foot and nothing above it, including the Version 1.0 line at `:3`, is edited. Sections 1–10 stand as frozen.

**Nothing this amendment touches is a gate, a threshold, a cap, a band, a label, a prediction, a cost or a cpuset.** `CAP_CORE_MIN = 900.0` and `CAP_S8 = 400.0` are what §4 registered on 2026-08-26 and are what they remain; `W_STEPS 2000`, `MEM_LIMIT 8g`, `MEMAVAIL_FLOOR_GIB 14.0`, `CPUSET_CPUS 1`, band D, `h_max 0.05`, every gate `G12R-0`…`G12R-11`/`G12R-W`, P1–P5, the 563.3 core-min estimate and the S8 wall bound are all unchanged. **The comparator `d12y_grade_w3.py` is UNTOUCHED**, md5 `f3c1252c11fb94a3d4c580fdcbe7a62d` on disk and at HEAD — W3's evidentiary value is that the successor comparator was frozen before the answer was known, and this amendment does not reach it.

### 11.1 The §2b condition, stated AND CHECKED

`VERIFICATION_CHARTER.md` §2b makes a pre-registration amendment legal **only while there is no answer to tune to**, and requires the condition to be *stated and how it was checked*, not asserted. **Checked, not assumed, at 2026-08-27T16:35–16:37Z, three ways:**

| the condition | how it was checked | reading |
| --- | --- | --- |
| the run root does not exist | `test -e /home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady` | **false** — driven twice inside `d12y_w3_groot5_selftest.sh` (its opening leg, and again as the closing freeze condition after the temporary root is removed); both `[OK ]` in `d12y_w3_groot5_selftest_evidence.txt` |
| no W3 container has ever run | `docker ps -a --format '{{.Names}}' \| grep '^d12y_w3_'` | **no `d12y_w3_` container survives** — `[OK ]`, same evidence file |
| no W3 stage has been recorded | no `ledger.txt` and no `manifest.jsonl` exist, because the root that would hold them does not exist | follows from row 1 |
| the one launch that happened spent nothing | `W3_phase1.out`, 63 bytes, mtime 03:43 — the launcher's `A1` `ABORT` line, emitted **before** `A2`'s image read and therefore before any container | **0 core-min**; `verification/queue/runner.log:1249` and `verification/queue/LAUNCH_LOG.tsv:53` carry the launch (03:43:17Z, pid 662453, ranks 1) |

**There is no answer to tune to, because W3 has produced no answer of any kind.**

### 11.2 `W3-LAUNCHER-DEF-1` — the operative cap defaults were the draft's

`d12y_w3_stage_and_run.sh` carried the frozen values in its `*_REGISTERED` constants (`:117-118`, `"900.0"` / `"400.0"`) and the **W3 draft's** values in the two OPERATIVE defaults immediately below them (`600.0` / `350.0`, carried over from `W3_PREREGISTRATION_DRAFT.md`). The launcher's own `A1` agreement control — the control written for exactly this class after `D12-E'` §6.1 — compared them and **refused**, at `A1`, before `A2` read an image digest:

> `ABORT: CAP_CORE_MIN is 600.0, the pre-registration names 900.0`

That single line is the whole of `W3_phase1.out` and the whole of the 03:43:17Z launch. **The control did its job and cost nothing.** The repair moves the two OPERATIVE defaults to the values the document already named. **The registered cap does not move, because 900.0 is already what is registered** — the frozen document governs its instrument, and here the instrument was wrong.

**A second stale default was masked by the first.** `A1` tests the cumulative cap before the S8 sub-cap, so the first `ABORT` hid that the S8 operative default was also the draft's (`350.0` against a registered `400.0`). Repairing only the reported line would have produced a second identical refusal on the next launch. Both are repaired together; the S8 sub-cap value registered in §4 is unchanged.

### 11.3 `W3-SELFTEST-DEF-1` — the selftest destroyed the evidence of `W3-LAUNCHER-DEF-1`

`d12y_w3_groot5_selftest.sh` was written and driven 7/7 on 2026-08-26T22:54:09Z, **before any W3 launch existed**. It therefore treated *any* `STATUS.W3_chain` and *any* `W3_*.out` as its own leakage: it `rm -f`-ed the first at its foot and scored the second by absolute count. Run at **2026-08-27T16:35:49Z** it consequently **deleted `STATUS.W3_chain`**, the 93-byte file the queue runner wrote at the 03:43:17Z launch, and mis-scored the surviving `W3_phase1.out` as leakage.

**Disclosed, not tidied.** The deleted file was untracked and never at HEAD, so it is not recoverable byte-for-byte. Everything it carried is independently attested and nothing rests on it: the launch by `verification/queue/runner.log:1249` and `verification/queue/LAUNCH_LOG.tsv:53`, and `rc=1` by `W3_phase1.out`, which survives intact at its 03:43 mtime. **0 core-min were spent, so no verdict, cost or prediction depends on it.** `STATUS.W3_chain` now on disk is a **labelled reconstruction** of the runner's fixed format and says so in its own second line; it is not presented as the original.

The repair: the selftest **snapshots** `STATUS.W3_chain` and the set of `W3_*.out` before its first leg, restores the former byte-for-byte at the end, and scores only files it **added**. Both new legs are driven and both pass.

### 11.4 The cap-agreement legs, driven with a planted disagreement shown to FAIL

A control not shown able to fire is not a control (`CLAUDE.md` rule 3). Six legs added to `d12y_w3_groot5_selftest.sh`, all **zero compute** — `(d)`/`(e)`/`(f)` refuse inside the launcher's `A1`/`A3`, both of which run before `A6` starts any container, and `(g)`/`(h)`/`(i)` are text reads. They run **ahead of** the G-ROOT.5 legs, so a cap failure stops the selftest before a single container is started.

| leg | what is planted | what must happen | reading 16:37:15Z |
| --- | --- | --- | --- |
| (d) | `CAP_CORE_MIN=600.0` — the draft's value | launcher exits 1 at `A1` with the exact registered-vs-operative message | **`[OK ]`** |
| (e) | `CAP_S8=350.0` — the draft's value | launcher exits 1 at `A1` on the S8 limb; **this also proves the cumulative limb PASSES at its registered default**, since otherwise this leg would abort on that message instead | **`[OK ]`** |
| (f) | nothing planted; `SRC` pointed at an absent directory | `A1` passes BOTH limbs and the refusal is `A3` (exit 4, instrument-freeze), with no `ABORT: CAP_` line anywhere in the output | **`[OK ]`** |
| (g) | nothing | the launcher's OPERATIVE defaults equal its own `*_REGISTERED` constants — **the drift reading that would have caught this defect at freeze time** | **`[OK ]` 900.0 / 400.0** |
| (h) | nothing | those constants equal the caps **this document** names, at every place it names them, refusing on any internal disagreement — *the document governs its instrument* | **`[OK ]` 900.0 / 400.0** |
| (i) | a sacrificial copy of the launcher with `600.0` restored | leg (g)'s reader must come out **UNEQUAL** on it | **`[OK ]`** — operative 600.0 vs registered 900.0 |

**Leg (i) is the planted control on the new reader** and is the reason (g)'s pass is evidence rather than an assertion. **Full selftest: `pass=14 fail=0`**, `d12y_w3_groot5_selftest_evidence.txt`, 2026-08-27T16:37:15–16:37:16Z. A6's throwaway container is never reached by any cap leg; the only container the selftest starts is leg (a)'s registered sacrificial `sleep`.

**A second honest correction, and the control caught its own author.** Leg (h)'s reader was first written to scan the WHOLE document, and on its next run it **REFUSED** — because this amendment's own leg table quotes the planted draft values as legs (d)/(e) plant them, and a document-wide scan cannot tell a value a document QUOTES from one it REGISTERS. The reader was scoped to the frozen §4 registration line by that row's literal label (the row beginning `Caps, registered and asserted …`), refusing if the anchor is missing, DUPLICATED, or does not carry both caps exactly once. It then refused a second time — because this very paragraph had reproduced the anchor verbatim, making it appear twice. That refusal is the reader working: two rows both claiming to register the cap is an ambiguity, not a detail, and the reader is right to decline to pick one. The prose was truncated; §4 still stands untouched. **§4 was not edited to make the reader pass** — that would be repairing a document on the authority of an instrument, which is backwards. The instrument was wrong about where registration lives, and the instrument is what changed.

**An honest correction recorded rather than dropped.** Leg (f) was first written to expect `A4`'s planted-instrument control (exit 5) and **measured** `A3` (exit 4) instead: with an absent instrument the on-disk md5 is the empty string while the HEAD-blob md5 is `d41d8cd9…` (the md5 of empty input), so `A3` does **not** compare empty against empty and does **not** silently pass on a missing file. The leg was corrected to its measured refusal. `A3` is sound; the concern that prompted the check was unfounded and is recorded so nobody re-derives it.

### 11.5 The instruments, re-pinned

`d12y_grade_w3.py` is deliberately absent from this table: it did not change.

| file | md5 at Version 1.0 | md5 at Version 1.1 | what changed |
| --- | --- | --- | --- |
| `d12y_w3_stage_and_run.sh` | `fc7585cf27736593bf3df198e5d73836` | `5563d8a8e22d28247233ca0e3aebfc2b` | the two OPERATIVE cap defaults, and a six-line comment naming the defect. Nothing else — a `diff` against the Version 1.0 file is 2 changed lines plus that comment |
| `d12y_w3_chain_driver.sh` | `5ed357e1f25b4f413d05f8b6a6680e75` | `aaa5339db4abd9e0cf6c20701acefef4` | `MD5_LAUNCHER` re-pinned to the line above, plus a three-line comment. The driver's own `md5sum -c` at `:34` would otherwise refuse, which is the check `D8R-DRIVER-DEF-1` failed |
| `d12y_w3_groot5_selftest.sh` | `c277331b…` (Version 1.0 table) | `c8ae8b5bce24e37b970ba8c90637ae91` | §11.3's snapshot/restore and §11.4's six legs |
| `d12y_grade_w3.py` | `f3c1252c11fb94a3d4c580fdcbe7a62d` | **unchanged** | — |

`A3` in the launcher asserts every instrument's md5 against the **committed HEAD blob** before staging, and the driver asserts the launcher's and the comparator's before each step, so **none of the above can run until it is committed** — the freeze is executed, not asserted.

### 11.6 Re-file

`verification/queue/dafoam/W3_chain.json` was launched at 03:43:17Z and the runner never re-fires a launched entry. The re-file is **`W3_chain_r2.json`**, identical in every registered field — same `launch_cmd`, `cwd`, `ranks 1`, `cost_core_min_estimate 563.3`, `cap_core_min_registered 900.0`, `memory_floor_gb 14.0`, `cost_basis`, `permission bc0e687e` — with `prereg_commit` set to the sha of the commit carrying **this amendment**, since that is the commit at which the instruments that will run exist. **Enqueueing is not authorisation**: `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own.

| what this amendment did | figure |
| --- | --- |
| gates, thresholds, caps, bands, labels or predictions altered | **0** |
| core-minutes spent by W3 before this amendment | **0** |
| lines whose number changed above this section | **0** |
| defects named and repaired | **2** (`W3-LAUNCHER-DEF-1`, `W3-SELFTEST-DEF-1`) |
| selftest legs added, all driven | **6 + 2** (cap agreement; snapshot/restore) |
| selftest result | **pass=14 fail=0** |

---

## 12. AMENDMENT 2 — 2026-08-27, PRE-COMPUTE. Ruling R-RC applied in full, and the L-342 field-class split. No gate, threshold, cap, band or label moves.

**Version 1.1 → 1.2.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (B). Supervisor: `dafoam-supervisor` (`[lab-attributed]`). **Lines whose number changed above this section: 0 — proved on BYTES**, not on a line count: the HEAD blob of this file is asserted a byte-exact PREFIX of the amended file in the commit invocation. Sections 1–11 stand.

### 12.1 Authority — a standing rule enforced, not an exception granted

**This amendment's authority is `L-342` and ruling `R-RC`, and it is deliberately NOT `VERIFICATION_CHARTER.md` §2d.1.**

`L-342` is Sanaa's own universal rule: *a bookkeeping failure invalidates the bookkeeping, never the physics artifacts — and graders must separate physics-critical fields from infrastructure fields so a dead poller can never void a run again.* `R-RC` was **APPROVED BY SANAA HERSELF** on 2026-08-27, in her standing directives §0 (`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`), verbatim:

> **R-RC: APPROVED — rc value is physics, rc record is infrastructure; absent record -> NOT MEASURED only when the other four rule-4 conditions hold.**

§2d.1 is the four-condition **repair exception to the post-compute freeze**, and it is not reached here for two independent reasons. First, **W3 has spent 0 core-min and its comparator has never fired**, so the ordinary pre-compute amendment clause (§2b, rule 2) is wide open and an exception used where the ordinary path is open is an exception being widened. Second, and the one that matters: **a comparator that refuses on a launcher-written record is in breach of a standing rule, and bringing it into compliance is the freeze's own terms being enforced, not a discretionary departure from them.**

**§2b's condition, stated AND CHECKED** — re-driven at 17:08:59Z, not carried over from Amendment 1: `test -e /home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady` is **false**, driven twice inside `d12y_w3_groot5_selftest.sh` (`pass=14 fail=0`); no `d12y_w3_` container has ever existed; no ledger or manifest exists; `W3_phase1.out` records the one launch, which spent nothing. **There is no answer to tune to.**

**Sanaa can overrule any of this.**

### 12.2 What moves, and what deliberately does not

| clause | before | after | class |
| --- | --- | --- | --- |
| `g0_completion` `ExecutionTime` count below registered steps (`:375-377`) | **REFUSAL** | **REPORTED** as a bookkeeping defect beside the verdict | INFRASTRUCTURE |
| `g0_completion` `Time =` count != registered steps | REFUSAL | **REFUSAL, unchanged** | PHYSICS |
| `rc` **record** absent from the manifest row | refused via `REQUIRED_ROW_KEYS` | **`NOT MEASURED`, `rc=0` INFERRED**, fenced (§12.3) | INFRASTRUCTURE |
| `rc` **value** present and non-zero | REFUSAL | **REFUSAL, unchanged** (R-RC-1, R-RC-3) | PHYSICS |
| `rc` key present but `None` | — | **REFUSAL, new** | PHYSICS |
| `FOAM FATAL` / signal token in the stage log | **not checked at all** | **REFUSAL, new — regardless of rc and of every other limb** (R-RC-4) | PHYSICS |
| `W3-A2` ledger **absent** (`:1976`) | REFUSAL | **cross-read `NOT MEASURED`**; the window itself still gated | INFRASTRUCTURE |
| `W3-A2` ledger **present** with ≠ 1 `W_STEPS` line, or disagreeing | REFUSAL | **REFUSAL, unchanged** — present-and-wrong is R-RC-3's shape | PHYSICS |
| `g0b` ledger absent + manifest count ≠ registered (`:453`) | REFUSAL | **REFUSAL, unchanged — see §12.5** | PHYSICS |

**Unmoved:** `CAP_CORE_MIN = 900.0`, `CAP_S8 = 400.0`, `W_STEPS 2000`, `MEM_LIMIT 8g`, `MEMAVAIL_FLOOR_GIB 14.0`, `CPUSET_CPUS 1`, band D, `h_max 0.05`, `C_ENV`, `W_PRIMARY`, every gate `G12R-0`…`G12R-11`/`G12R-W`, P1–P5, the 563.3 core-min estimate, the S8 wall bound, and every band, threshold and label in §§3–8.

### 12.3 R-RC-2's fence, and why the permissive half is safe

An absent rc record yields `NOT MEASURED` **only when all four remaining rule-4 conditions hold**, and each is **named individually in the artefact** — `end_line_present`, `last_time_equals_endTime`, `registered_fields_present`, `age_guard`. "All four held" without naming them is the self-assessment shape this lab amended against. If any one fails, **its own limb refuses first** and the ordinary refusal stands; the absent record buys nothing.

**`rc = 0` is INFERRED and printed as an inference, never graded as a measurement.** `CLAUDE.md` rule 3 is untouched by R-RC. The artefact carries the words `INFERRED, NOT MEASURED` and `NOT graded as a measurement`, and a top-level `rc_note` flags the whole result so a reader cannot take the grade without the caveat.

**R-RC-4 is the fence, and it is load-bearing.** The one shape that can pass all four conditions and still deserve refusal is a solver returning non-zero **after** writing every field and the `End` line. So the launcher — which already holds the whole log text — now records `fatal_tokens`, and the grader refuses on any hit **regardless of rc**. Where the record is absent **and** the scan never ran, the grader **REFUSES**: in the ruling's own words, *without that limb the inference is not safe and R-RC-2 does not apply.* `None` (no log read) and `[]` (scanned, clean) are different values and the grader treats them so.

### 12.4 Planted-failure proofs — Sanaa's §1, L-314 standard, all zero compute

> *"Every guard ships its planted-failure proof."*

**`--selftest-rrc`: 22/22 under `python3` AND `python3 -O`** (`d12y_grade_w3_rrc_evidence.txt`). Every permissive leg is paired with the strict leg that shows the same guard still refusing — *a guard shown only to pass is not shown to be a guard*:

| leg | planted | required | got |
| --- | --- | --- | --- |
| R1 | nothing (positive control) | PASS, 0 infrastructure defects | `[OK ]` |
| R2–R5 | rc record absent, four conditions hold | PASS; artefact says `INFERRED, NOT MEASURED`; all four named individually; `rc_note` flags it | `[OK ]` ×4 |
| R6 ×4 | rc absent **+ each condition broken in turn** | REFUSE **on that condition**, not on the missing record | `[OK ]` ×4 |
| R7 | rc present = 1 | REFUSE (R-RC-3) | `[OK ]` |
| R8 | rc key present but `None` | REFUSE — a record that exists and says nothing is not a licensed inference | `[OK ]` |
| R9, R10 | `FOAM FATAL ERROR`; `Segmentation fault`, with rc=0 and every limb perfect | REFUSE (R-RC-4 strict half) | `[OK ]` ×2 |
| R11 | rc absent **and** the scan never ran | REFUSE — the inference is fenced, not granted | `[OK ]` |
| R12 | scan absent but rc measured 0 | PASS with the gap reported | `[OK ]` |
| R13 | ExecutionTime 3 vs 300, `Time =` correct | PASS with a bookkeeping defect | `[OK ]` |
| **R14** | **`Time =` 299 vs 300** | **STILL REFUSE — the control that proves the physics limb was SPLIT OFF, not deleted** | `[OK ]` |
| R15 | W3-A2 ledger absent, rows agree at `W_PRIMARY` | return the window, cross-read `NOT MEASURED` | `[OK ]` |
| R16, R17 | ledger absent + W ≠ `W_PRIMARY`; ledger absent + a row with no `W` | REFUSE — the window is physics and is not waived with the ledger | `[OK ]` ×2 |
| R18, R19 | ledger present with two `W_STEPS` lines; ledger present and disagreeing | STILL REFUSE (the `W2R-GRADER-DEF-1` shape) | `[OK ]` ×2 |

**`d12y_w3_fatal_scan_control.sh`: 12/12.** The patterns are **extracted from `d12y_w3_stage_and_run.sh` itself, never retyped** — a control carrying its own copy tests the copy and keeps passing after the launcher drifts — and the control **REFUSES** rather than reporting a clean zero if the extraction finds fewer than five patterns. Legs: a clean log yields nothing (the reader is not trigger-happy); **all nine patterns planted individually** with a leg asserting no launcher pattern is left undriven; and innocuous prose containing *signal*, *error*, *fatal* and *segment* yields nothing — the patterns are anchored, not substrings, because a scanner that refuses good runs is the `VMFLGPU001` failure running backwards.

**The inherited battery: 82/82, 0 failures, under both flags** — and it **failed 2/82 first**, at `U-01b` and `U-0d`, both on the ExecutionTime clause. Recorded rather than tidied: those two units encoded the pre-amendment behaviour and were **updated to the new registered behaviour, not deleted**. `U-0d` now drives **both halves of the split**, and its second half — a short `Time =` count still refusing — is the control that proves the physics limb was separated rather than removed. `U-01b` loses `execution_time_count` from the rule-4 refusal matrix and **gains the two guards this amendment creates** (`rc=None`, `fatal_tokens=[...]`), so the inherited battery exercises them too. The registered unit count stays **82**.

**`ast.Assert` count 0, with the counter shown COUNTING one**: the clean file audits to `0`; a sacrificial copy carrying one planted module-level `assert` audits to `1`. An assert audit that has never seen an assert is not evidence.

### 12.5 What was audited and deliberately NOT changed — the honest half

The `L-342` audit (`8fed44ed`) listed four ledger sites in this file: `:453`, `:1976`, `:1984`, `:1986`. **Only `:1976` is a conflation. The other three are correct as they stand and repairing them would have been a permissive widening `R-RC` does not license.**

- **`:453` is already compliant.** Its `ADDENDUM 1` block already returns `NOT_MEASURED` on an absent ledger; the refusal beside it fires on `len(names_manifest) != expected_rows` — **the count against a frozen constant this file types, which needs no ledger** and which caught `D12R2-DEF-2` and `W2-DEF-1`. The audit matched the line; reading it, the refusal is on the count, not on the ledger's absence.
- **`:1984` and `:1986` fire on a ledger that is PRESENT and ambiguous or PRESENT and disagreeing.** That is `R-RC-3`'s shape — present-and-wrong refuses — and two `W_STEPS` lines is a real ambiguity about which window ran.

**A second honest correction.** The `A3` instrument-freeze check was suspected of comparing empty against empty on an absent instrument. **Measured: it does not** — the on-disk md5 is the empty string while the HEAD-blob md5 is `d41d8cd9…` (the md5 of empty input), so they differ and it refuses. Recorded so nobody re-derives it.

### 12.6 Instruments re-frozen at this commit

| file | md5 at v1.1 | md5 at v1.2 | change |
| --- | --- | --- | --- |
| `d12y_grade_w3.py` | `f3c1252c11fb94a3d4c580fdcbe7a62d` | `3b0a75079c932b41ec19477388498842` | the R-RC branch, the R-RC-4 limb, the infrastructure channel, the `W3-A2` ledger split, `selftest_rrc` (22 legs), and the two inherited units. `d12y_grade_w3_DELTAS_amendment2.diff`, 489 lines |
| `d12y_w3_stage_and_run.sh` | `5563d8a8e22d28247233ca0e3aebfc2b` | `20f8c0c51593576bddaa8a410659d997` | `row["fatal_tokens"]` and the nine-pattern scan. `d12y_w3_stage_and_run_DELTAS_amendment2.diff`, 35 lines. **No cap, cpuset, memory, stage graph or `W_STEPS` value is touched** |
| `d12y_w3_chain_driver.sh` | `aaa5339db4abd9e0cf6c20701acefef4` | `60b1edc17a1d041a78fe8e17cbbbaebf` | `MD5_LAUNCHER` and `MD5_GRADER` re-pinned. The driver asserts both at `:34`/`:38` before every step; **pin == actual is asserted in the commit invocation**, because a stale pin here is the `D8R-DRIVER-DEF-1` death |
| `d12y_w3_fatal_scan_control.sh` | — | new | §12.4's twelve legs |

The launcher's `A3` asserts every instrument against the **committed HEAD blob** before staging, so none of this runs until it is committed — the freeze is executed, not asserted.

### 12.7 Re-file

`W3_chain_r2.json` was withdrawn to `held/` at 16:46:37Z **before the runner fired it**, precisely to keep this window open. The successor is **`W3_chain_r3.json`**, identical in every registered field, with `prereg_commit` set to the commit carrying this amendment. **Enqueueing is not authorisation.**

| what this amendment did | figure |
| --- | --- |
| gates, thresholds, caps, bands, labels or predictions altered | **0** |
| core-minutes spent by W3 before this amendment | **0** |
| refusal clauses reclassified INFRASTRUCTURE | **3** |
| refusal clauses ADDED (both physics) | **2** (`rc` present-but-`None`; `FOAM FATAL`/signal) |
| audited clauses examined and deliberately left strict | **3** (`:453`, `:1984`, `:1986`) |
| planted-failure legs driven | **22 + 12 + 82**, all passing under `python3` and `python3 -O` |
| lines whose number changed above this section | **0**, proved on bytes |

---

## 13. AMENDMENT 3 — 2026-08-28, PRE-COMPUTE. `W3-GRADER-DEF-2`: the S2b log selection REFUSES instead of resolving. No gate, threshold, cap, band, label, cost or prediction moves.

**Version 1.2 → 1.3.** Dated **2026-08-28**. Lane: dafoam `lab-lane` (U). Supervisor: `dafoam-supervisor` (`[lab-attributed]`; **check 1 discharged before this lane wrote a byte** — the supervisor read the comparator change as a `diff` against the HEAD blob personally and approved it). **Lines whose number changed above this section: 0 — proved on BYTES**, not on a line count: the HEAD blob of this file is asserted a byte-exact PREFIX of the amended file in the commit invocation, the assertion Amendment 2 introduced and this one inherits. Sections 1–12 stand as frozen.

### 13.1 The §2b condition, stated AND CHECKED

`VERIFICATION_CHARTER.md` §2b permits amendment **before first compute**, and requires the condition to be stated *and* checked by naming the run directory that does not exist. Re-driven at **2026-08-28T16:14:36Z**, not carried over from Amendments 1 or 2:

- `test -e /home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady` → **FALSE**. The W3 run root has never existed. (`CURRICULUM-D12R2-`, `-D12R2W2-` and `-D12R2W2R-` roots exist and are other items; no root of any name carries W3 artifacts.)
- **W3 has spent 0 core-minutes.** Two launches have been fired and both refused at zero: `2026-08-27T03:43:17Z` at the launcher's A1 cap-agreement control (§11.2, `W3-LAUNCHER-DEF-1`), and **`2026-08-28T02:15:29Z`, which aborted `rc=4 reason=grader_md5_drifted` BEFORE its `START` line** — recorded by the driver's own `rec()` in `STATUS.W3_chain`, the last line in that file.
- No `d12y_w3_` container has ever existed; no W3 ledger, manifest or `step_plan*.json` exists.

**There is no answer to tune to.** The gates are open, and this is the ordinary §2b path — **not** the §2d.1 post-compute repair exception, which is not reached and is deliberately not invoked.

**Sanaa can overrule any of this.**

### 13.2 `W3-GRADER-DEF-2` — a multi-file state RESOLVED BY SORT ORDER, on the path that feeds G12R-4

The predecessor comparator selected the S2b series with `sorted(cands)[-1]` — **last wins by lexicographic sort**. S2b runs **exactly once per run root**: the launcher fires it at one call site and the cold-start guard refuses a re-fire into an existing root. A second `S2b_*.log` is therefore *a re-fired stage — itself a FINDING*, never something for a comparator to pick between. Silently taking the lexicographically-last file converts an anomaly into a number.

The repaired path raises a `Refusal` on `len(cands) != 1`, naming the count, the root and every candidate.

**The path is load-bearing, not incidental.** It feeds `delta_eff` and `h_min`, and **`h_min` is the quantity `G12R-4` grades against `h_max`**. A wrong selection here does not crash; it moves a graded number.

### 13.3 A SECOND, SEPARATE FINDING — the dead `logp`, and why the manifest name is a cross-check and not the primary

The predecessor also computed `logp = os.path.join(root, os.path.basename(s2.get("log", "")))` and **never used it**. This is recorded as a distinct finding rather than folded into `W3-GRADER-DEF-2`, because the tempting repair — "adopt the manifest's declared name as the primary" — **is wrong, and measurably so**:

- The launcher **writes no `"log"` key into any manifest row**. Checked over every `row[...]` assignment in `d12y_w3_stage_and_run.sh`, and confirmed against the real 33-row D12R2 phase-1 manifest, whose S2b row carries **39 keys and no `"log"`**.
- So `s2.get("log", "")` returned `""`, `os.path.basename("")` is `""`, and **`logp` resolved to the run ROOT, not to a log.**

The dead variable is therefore **REMOVED, not adopted**. The manifest name is used **only as a cross-check, and only where a row actually carries one** — a row with no name is not an error and does not refuse. The selection is put **on the record** rather than left implicit in a sort order: the artefact now carries `s2b_log_selected`, `s2b_log_candidates`, and `s2b_log_declared_by_manifest` (`NOT_MEASURED` where the manifest declares nothing).

(`grade_from_manifest`'s `read_series(os.path.join(root, s2["log"]))` is the LEGACY single-JSON path, not this one; §2 already records that it does not run.)

### 13.4 Planted-control proofs, DRIVEN — zero compute, both directions

> Sanaa's standing directives §1 (L-314): *every guard ships its planted-failure proof.* `CLAUDE.md` rule 3: **a reader not shown able to see a non-zero is not evidence.**

**`d12y_w3_s2b_selection_control.sh`: 11/11, `pass=11 fail=0`.** Driven through the REAL `plan()` code path on a fixture assembled from the REAL 33-row D12R2 phase-1 manifest and its REAL S2b log; it creates no container, touches no run root, and writes only under its `TMPD`. It **refuses rather than reporting a clean zero** if its seed run root is absent.

| leg | planted | required | got |
| --- | --- | --- | --- |
| L1 | exactly one `S2b_*.log` | `plan()` rc=0; `s2b_log_selected` NAMES the file on disk | `PASS` |
| L2 | the same one-file fixture, graded by the PRE-`W3-A3` comparator | `step_plan` **byte-identical** pre vs post — **the repair moves no number** | `PASS` |
| L3 | a SECOND `S2b_*.log` | REFUSE rc=2, and the refusal NAMES the ambiguity | `PASS` |
| **L3c** | **the same plant, on the PRE-`W3-A3` comparator** | **it ACCEPTS (rc=0) and its `h_min` MOVES — the defect is real, not hypothetical** | `PASS` |
| L4 | the plant REMOVED again | passes again rc=0 — **the refusal was caused by the plant, not by the fixture** | `PASS` |
| L5 | manifest row `"log"` == the true name | passes rc=0 — the cross-check is not a blanket refusal | `PASS` |
| L6 | manifest row `"log"` == a WRONG name | REFUSE rc=2 on the cross-check | `PASS` |
| L7 | no `S2b_*.log` at all | REFUSE rc=2 — pre-existing limb, carried unchanged | `PASS` |
| L8 | `ast.Assert` audit | `0`, with the SAME counter shown reading `1` on a planted assert (0 → 1) | `PASS` |

**THE MEASURED MOVEMENT, on the PRE-`W3-A3` comparator, one file → the planted two-file state:**

| quantity | one `S2b_*.log` | with the planted second log (same series × 1.05) | moved |
| --- | --- | --- | --- |
| `delta_eff` | `4.453500e-04` | `4.604996e-04` | **yes** |
| `h_min` | `0.043220413943883054` | `0.044690652644557820` | **yes — and `h_min` is what `G12R-4` grades** |

rc was **0** and **no refusal fired**: the predecessor would have graded the planted state as a clean result.

**`d12y_w3_pin_guard_control.sh`: 6/6, `pass=6 fail=0` (NEW at this amendment).** It drives the chain driver's OWN md5 assertion in **both directions**. The assertion is **not retyped**: the harness is the driver's own first *N* bytes, cut at the grader-assertion line and **byte-asserted identical to the driver's prefix** (`21e47be43d75b3711de9c8cf6eb5e038`), so the control cannot keep passing after the driver drifts. The launcher and grader are reached by **symlink**, so `md5sum` reads the REAL files' bytes; only the sandbox `STATUS` file is written. Nothing is launched — the harness stops at the line after the guard, and `STATUS.W3_chain` in the case directory was verified unchanged.

| leg | condition | required | got |
| --- | --- | --- | --- |
| P1 | extraction control | driver holds **exactly one** `MD5_GRADER=` and **exactly one** grader assertion, else **ABORT** rather than report a zero | `PASS` (1/1) |
| P2 | harness prefix | byte-identical to driver lines 1–46 | `PASS` |
| **P3** | **correct pin + REAL grader** | **rc=0, `GUARD_PASSED`, zero drift lines** | `PASS` |
| **P4** | **pin deliberately WRONG** | **rc=4 `reason=grader_md5_drifted`, and `GUARD_PASSED` never printed** | `PASS` |
| P5 | correct pin + PLANTED grader bytes | rc=4 — **the guard reads the FILE, not merely its own constant** | `PASS` |
| P6 | the limb that fired | GRADER limb, not the launcher limb (launcher drift lines 0/0) | `PASS` |

**An honest defect in this lane's own instrument, recorded rather than tidied.** Leg P6 FAILED on its first run — because of a bug in the *control*, not in the driver: `grep -c` prints `0` **and exits 1** on no-match, so the `|| echo 0` fallback emitted **two** values (`"0\n0"`) and the equality test failed. Repaired with a `cnt()` helper, and the helper was itself shown returning exactly one value in all three states (no-match on an existing file, match, absent file) before the re-run. A control whose own reader is broken measures its reader, not the code.

**The inherited batteries, re-driven at this amendment under `python3` AND `python3 -O`:** `--selftest` **82/82, failures 0** (`units REGISTERED (frozen constant) 82, units in the list 82, units that RETURNED A RESULT 82`); `--selftest-rrc` **22/22**; `--selftest-w3` **12/12**. The registered unit count stays **82** — this amendment adds no unit to that battery and removes none.

### 13.5 The stale pin, and why the `02:15:29Z` launch aborted — the guard did its job

The comparator was repaired on disk at `2026-08-27T23:11Z` and **never committed**; the fleet died four minutes later on the account's weekly usage limit. The daemon runner fired `W3_chain_r3` at `2026-08-28T02:15:29Z` regardless. The driver's `MD5_GRADER` pin still named `3b0a7507…` while the file on disk was `3950d30f…`, so the assertion fired and the driver exited **`rc=4 reason=grader_md5_drifted` before its `START` line, at zero core-minutes.**

**This is the instrument working, not failing.** A comparator whose bytes have drifted from its registered pin **did not run**. That is `VERIFICATION_CHARTER.md` §2's freeze executed rather than asserted, and it is the `D8R-DRIVER-DEF-1` death prevented. The abort is recorded here as corroboration of §13.1's zero-compute condition, not as a defect.

The pin is bumped **in the same commit as the comparator it pins**, which is the only ordering that cannot leave a window in which the two disagree.

### 13.6 Instruments re-frozen at this commit

Every md5 below was **re-derived in the same shell invocation** as the freeze assertion, never carried over from a previous section.

| file | md5 at v1.2 | md5 at v1.3 | change |
| --- | --- | --- | --- |
| `d12y_grade_w3.py` | `3b0a75079c932b41ec19477388498842` | `3950d30fd09c9b56213a02f5e9864e20` | `W3-GRADER-DEF-2`: `sorted(cands)[-1]` → a `len(cands) != 1` uniqueness Refusal; the dead `logp` removed; a manifest cross-check where a row carries a name; `s2b_log_selected` / `s2b_log_candidates` / `s2b_log_declared_by_manifest` recorded. **Two hunks, adjacent, in one function; `diff` against the v1.2 file is exactly 3 lines removed and 40 added, of which 22 are the comment naming the defect (measured from the diff, not estimated -- this lane's first draft of this row said 'one hunk, 2 removed, 21 comment lines' and all three figures were wrong). No gate, band, threshold, cap, label or constant is touched.** |
| `d12y_w3_chain_driver.sh` | `60b1edc17a1d041a78fe8e17cbbbaebf` | `4ae856128101115c3ba566eae9f41fd2` | `MD5_GRADER` re-pinned to the repaired comparator, plus the four-line comment naming this amendment. `MD5_LAUNCHER` **unchanged**. `diff` against the v1.2 file is exactly that one block. The pins are asserted at `:45`/`:46` before every step |
| `d12y_w3_stage_and_run.sh` | `20f8c0c51593576bddaa8a410659d997` | `20f8c0c51593576bddaa8a410659d997` | **UNCHANGED — deliberately.** No cap, cpuset, memory, stage graph or `W_STEPS` value is touched by this amendment |
| `d12y_w3_s2b_selection_control.sh` | — | `cdc2fcd489898e725abebc01f9f1e7aa` | new — §13.4's eleven legs |
| `d12y_w3_pin_guard_control.sh` | — | `50e2898af3a221cb7942dc766acc0bb0` | new — §13.4's six pin-guard legs, both directions |

The launcher's `A3` check asserts every instrument against the **committed HEAD blob** before staging, so none of this runs until it is committed — the freeze is executed, not asserted.

### 13.7 Re-file

`W3_chain_r3.json` was fired by the runner at `02:15:29Z` and has moved to `verification/queue/dafoam/launched/`. The successor is **`W3_chain_r4.json`**, identical in every registered field, with `prereg_commit` set to the commit carrying this amendment and `instrument_md5s_at_this_commit` carrying the **post-amendment** comparator and driver md5s. The registered cost is unchanged: **563.3 core-min estimate, `ranks 1`, cap `900.0` core-min**, dollars **DERIVED** at `$0.0513/core-h` with `cost_basis` **REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Enqueueing is not authorisation.**

**The `CAP_CORE_MIN` question, checked rather than assumed.** `STATUS.W3_chain` records the `2026-08-27T03:43:17Z` abort at the cap-agreement control, where the launcher's *operative default* was the W3 DRAFT's `600.0` against the registered `900.0`. **That mismatch is gone and was verified gone, not inferred:** `d12y_w3_stage_and_run.sh:118` reads `CAP_CORE_MIN_REGISTERED="900.0"` and `:126` reads `CAP_CORE_MIN="${CAP_CORE_MIN:-900.0}"`; the agreement control at `:187-188` aborts unless they are equal; and the queue entry carries `cap_core_min_registered = 900.0`. No `600.0` remains in any operative position.

| what this amendment did | figure |
| --- | --- |
| gates, thresholds, caps, bands, labels, costs or predictions altered | **0** |
| core-minutes spent by W3 before this amendment | **0** |
| refusal clauses ADDED | **2** (S2b selection ambiguous; the manifest/disk name disagreement) |
| refusal clauses REMOVED or weakened | **0** |
| dead variables removed | **1** (`logp`, §13.3) |
| output keys added (record-only, graded by nothing) | **3** |
| planted-failure legs driven | **11 + 6 + 82 + 22 + 12**, all passing, the last three under `python3` and `python3 -O` |
| this lane's own instrument defects found and recorded | **1** (§13.4, leg P6) |
| lines whose number changed above this section | **0**, proved on bytes |
