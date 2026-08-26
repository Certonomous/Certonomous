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
