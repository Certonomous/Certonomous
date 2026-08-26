> **SUPERSEDED 2026-08-26 by `W3_PREREGISTRATION.md` (v1.0, FROZEN by its own commit sha) — this draft is RETAINED AND STRUCK, never deleted. Its numbers were re-derived by the freezing lane with the frozen comparator's own `read_series`/`block_averages` (envelope constant 0.89065 at 1-step sampling, registered as `C_ENV = 0.8907`); its §1 item 2 mechanism is CORRECTED in the frozen file: the `--plan` path is `plan()` at `d12y_grade.py:2011` passing the literal `W_PRIMARY`, not `:2511` `man.get("W")`, so the frozen item carries a SUCCESSOR comparator (`d12y_grade_w3.py`), not a manifest key alone. Nothing below binds anything.**

# DRAFT — NOT FROZEN — NO COMPUTE — W3: the third averaging window for the 2D·unsteady·incompressible FD line

**Status: DRAFT. This file is not a pre-registration. Nothing in it is frozen, nothing may be launched from it, no queue entry exists or may be filed from it, and no gate, threshold, cap or label below binds anything until the dafoam-supervisor freezes a `W3_PREREGISTRATION.md` by sha (`CLAUDE.md` rule 2; `VERIFICATION_CHARTER.md` §2b, §2d).** Written 2026-08-26 by dafoam lane G for dafoam-supervisor, prediction-first, entirely from the W2R and D12R2 records on disk and at HEAD. Zero compute: every number below is read from an existing log, ledger or JSON, or is arithmetic on such numbers; the arithmetic is reproducible from the S2b series named in §1 with the comparator's own `read_series` / `block_averages` (`d12y_grade.py:143-190` at HEAD).

**The flip this rung is for.** `docs/capability/dafoam_GRID.md`, cell 2D·unsteady·incompressible: gradients `CAN DO, CAVEATS — no admissible FD step`, optimisation `CAN NOT DO`. Both flip together on one event — an FD-verified unsteady gradient (`G12R-6` band D) that then authorises S8 (`G12R-11`, `PREREGISTRATION.md:277` @ `e6580910`). The event is gated by `G12R-4`: `h_min = δ_eff / (0.01·|g|) ≤ h_max = 0.05`. Twice the lab has measured `h_min > h_max`: D12R2 at `W = 300`, `h_min = 0.1743` (`RESULTS.md:12-13, :54` @ `65882eb3`); W2R at `W = 900`, `h_min = 0.15755` on its plan step (run-root `step_plan.json`, `W2R_phase1_grade_replan_20260826T205826Z.json`).

---

## 1. What the W2R record actually contains, read before any prediction is made

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady/` (ledger, 33 stages, `PHASE1_COMPLETE spent=105.2334 core-min`); D12R2 run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady/` (`PHASE1_COMPLETE spent=55.5167 core-min`, C-115).

1. **The noise-floor series is the same series in both items.** W2R's S2b log (`S2b_20260826T160035Z_23510.log`) and D12R2's (`S2b_20260826T033053Z_3069758.log`) each carry 2,400 `CD:` samples at `Δt = 1e-2`, and the two series are **identical sample for sample** (mean `0.6563231414` both; P1 of W2R predicted exactly this: *"W2R's S2b is bit-identical"*, `W2R_PREREGISTRATION.md:93` @ `5d1f89cd`). Period from sign changes: **18.9644 steps**; peak-to-peak **0.13162**.
2. **The plan-step `δ_window` was evaluated at `W = 300` in both items.** W2R's replan JSON records `G12R-3` with `"W": 300, "n_windows": 2101, "delta_window": 1.7958478e-03` — the same value, to every digit, as D12R2's `G12R-3` (`RESULTS.md:47` @ `65882eb3`). Mechanism, read from the frozen comparator: `d12y_grade.py:2511` calls `g3_delta_window(retained, man.get("W", W_PRIMARY))` and the W2R launcher's `manifest.jsonl` carries no `W` key, so `W_PRIMARY = 300` was used. **The recorded W2R `h_min = 0.15755` is therefore `δ_window(300) / (0.01·|g(900)|)` with `|g(900)| = 1.13984` — not a `W = 900` noise floor.** This is disclosed here because a W3 built on "h_min fell only from 0.174 to 0.158 across a 3× window" would be built on a misreading; it is a scoring matter for the W2R record (another lane's file) and is not acted on in this draft.
3. **What did change with `W = 900`:** the objective stages ran 900 steps (S3_r1 log: 900 `CD:` samples against D12R2's 300), the gradient component moved `|g| = 1.03042 → 1.13984` (+10.6 %, inside P2's ±30 % band), and the per-stage cost moved 1.0667 → 2.8167 core-min (S3_r1, both ledgers).
4. **`δ_pert = 1.2228e-06` and `δ_repeat = 0`** (replan JSON, `G12R-3b`, `G12R-2`) — three orders below `δ_window`; `δ_window` is the only term that matters for the step.

---

## 2. Prediction (a) — how `h_min` scales with the window `W`

**The hypothesis Sanaa's question names:** if the window noise were statistical, `δ_window ∝ 1/√N` with `N = W` samples, so `h_min(900)/h_min(300) = 1/√3 = 0.577`.

**The physics says otherwise before the data is read:** the objective is the mean of a limit-cycle signal over a window of `W` steps that is not a whole number of periods; the block mean of a periodic signal of amplitude `A` and period `P` over a window `W` carries a phase-dependent residual of amplitude `A·|sin(πW/P)| / (πW/P)`, whose spread over all phases is `2A·|sin(πW/P)|/(πW/P)` — a **deterministic `1/W` envelope with an oscillating factor**, zero at whole periods (the comparator's frozen degeneracy branch, `d12y_grade.py:676-699`), not a `1/√W` law.

**Measured from the record — the sliding-block spread `δ_window(W)` of the retained S2b series, the comparator's own statistic (`block_averages`, every start offset), evaluated at windows the record never graded:**

| `W` (steps) | windows | `δ_window(W)` | `h_min` at `|g| = 1.13984` (W2R) | `h_min` at `|g| = 1.03042` (D12R2) |
|---|---|---|---|---|
| 300 | 2,101 | **1.795848e-03** (= the graded value, both items) | 0.15755 (= W2R's recorded value) | 0.17428 (= D12R2's recorded value) |
| 600 | 1,801 | 1.334082e-03 | 0.11704 | 0.12947 |
| 900 | 1,501 | **9.879556e-04** (= W2R's own P1 prediction, `:93`) | **0.08668** | 0.09588 (= W2R's P4 point prediction, `:97`) |
| 1,200 | 1,201 | 6.516613e-04 | 0.05717 | 0.06324 |
| 1,500 | 901 | 3.327772e-04 | 0.02920 | 0.03230 |
| 1,800 | 601 | 1.087860e-04 | 0.00954 | 0.01056 |
| 2,000 | 401 | 4.385710e-04 | 0.03848 | 0.04256 |

The planted check on this reader: it reproduces the graded `1.795848e-03` at `W = 300` and W2R's pre-registered `9.879556e-04` at `W = 900` to every printed digit.

**The measured scaling.** Fitting `log δ_window` against `log W` over `W = 100…2000` in steps of 25: slope **−1.03** over all points, **−1.01** over the 24 local maxima (the envelope). The statistical hypothesis (slope −0.5) is **rejected by the record**; the deterministic `1/W` envelope holds. The envelope constant is remarkably stable: `max(W·δ_window)` over every 300-step band from 300 to 2,100 is **0.8904–0.8907**, i.e.

**`δ_window,env(W) = 0.8906 / W`** (steps), `h_min,env(W) = 89.06 / (W·|g|)`.

The sinusoid model `2A·|sin(πW/P)|/(πW/P)` with `A = 0.06581`, `P = 18.9644` reproduces the measured values to a factor 0.93–1.29 (harmonics), confirming the mechanism without being needed for the prediction — the prediction uses the measured envelope.

**Why the envelope, not the exact `δ_window(W)`, must size the step.** The exact spread has deep minima near whole periods (`W = 910`: `k = 47.985`, `δ = 2.19e-04`, `h_min = 0.019`; `W = 1800`: `δ = 1.09e-04`). Those minima belong to the BASELINE geometry's period. An FD arm perturbs the cylinder by up to `h_max = 0.05` = 10 % of the radius, and the shedding period scales with the body size (Strouhal number fixed), so the perturbed arms' `W/P` shifts by up to ~5 periods and their window residual lands anywhere on the envelope. **A window chosen on a baseline minimum is a window chosen to fit the answer it will not see** — the frozen degeneracy branch, which EXCLUDES `δ_window` by name near whole periods and lets `δ_pert = 1.2e-06` carry the floor (`h_min = 1.1e-04`), is unsafe as a step-sizing route for the same reason, and W3 must not use it (§5, amendment W3-A1).

---

## 3. Prediction (b) — the window at which `h_min < h_max`, with its uncertainty

Admissibility on the envelope: `89.06 / (W·|g|) < 0.05` ⇔ **`W > 1,781 / |g|`**.

| `|g|` assumption | basis | `W*` (first admissible, envelope) |
|---|---|---|
| 1.13984 | W2R measured at `W = 900` | **1,563** |
| 1.03042 | D12R2 measured at `W = 300` | 1,729 |
| 0.95 | −17 % below W2R, the pessimistic edge of a ±15 % band on a quantity that moved +10.6 % per 3× window | 1,875 |
| 1.25 | +10 % above W2R, the optimistic edge | 1,425 |

**Predicted `W*` = 1,563 steps, band 1,425–1,875 (the `|g|` band ±15 % about the W2R value).** The registered window must clear the pessimistic edge with margin: **W3 registers `W = 2,000`** (2.22× W2R), giving `h_min,env(2000) = 0.03906` at `|g| = 1.13984` (margin 1.28× to `h_max`), `0.04321` at `1.03042` (1.16×), `0.04687` at `0.95` (1.07×). The S2b series of 2,400 samples supports `W = 2,000` with 401 sliding windows spanning 21 periods of phase — sufficient to measure the envelope, and the comparator's `block_averages` refuses below `W` samples, so S2b need not be lengthened. **`P3` of this draft is the binary form: `h_min(2000) ≤ 0.05` (admissible).** It is falsified iff `|g(2000)| < 0.8906·100/(2000·0.05) = 0.8906`.

A `W = 2,400` variant with S2b lengthened to 4,800 steps (margin 1.28–1.53×, cost in §4) is the fallback if the supervisor wants the pessimistic edge cleared by more than 7 %.

---

## 4. Prediction (c) — the cost, derived from the two measured phase-1 anchors (C-row for phase 1)

**Anchors (measured, ledgers):** D12R2 phase 1 at `W = 300`: **55.5167 core-min** (C-115); W2R phase 1 at `W = 900`: **105.2334 core-min**; per objective stage `S3_r1`: 1.0667 (300) and 2.8167 (900) core-min = **3.1–3.6e-03 core-min per step**, linear in `W`. Both runs share the same 33-stage graph (`PREREGISTRATION.md:152`: S0 1 + S1a 1 + S1b 1 + S2a 1 + S2b 1 + S3 3 + S3b 16 + S4 6 + S5 1 + S7 2), so a two-point linear model in `W` is exactly determined: `cost₁(W) = F + V·(W/900)` with `F + V = 105.2334`, `F + V/3 = 55.5167` ⇒ **`V = 74.575`, `F = 30.658` core-min** (the W-independent part is S0–S2b plus overheads: S2b alone measured 7.02 core-min at both windows, its 2,400 steps being fixed).

| item | at `W = 2,000` | at `W = 2,400` (S2b doubled) | basis |
|---|---|---|---|
| **Phase 1 (33 stages) — the C-row** | **196.4 core-min** ($0.168) | 229.5 + 7.0 (S2b 4,800 steps) = **236.5** ($0.202) | two-anchor linear model above; `derived, not measured` |
| Phase 2 (≤ 10 FD stages: 5 steps × 2 signs) | 10 × 2.8167 × (2000/900) = 62.6 → **65** | 10 × 7.51 = 75.1 → **80** | W2R A2.4 arithmetic (`W2R_PREREGISTRATION.md:190`), scaled |
| Phase 3 (S6b × 2 + S6c 4 × 2) | **65** | **80** | same |
| Phase 4 (S8, one stage; W2R upper 120 at `W = 900`) | 120 × 2.22 = **267** upper | **320** upper | scaled linearly; `timeout` would have to be re-registered accordingly |
| **Total, upper** | **≈ 593 core-min ≈ $0.51** | **≈ 716 core-min ≈ $0.61** | dollars at $0.0513/core-h, reported-by-owner, **not measured** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Proposed caps | `CAP_CORE_MIN` 900 (1.5× total), `CAP_S8` 400 | 1,100 / 480 | overrun stops the run (rule 12) |

**Calibration commitment.** On completion the actual/predicted ratio for phase 1 is entered in `docs/COST_CALIBRATION.md` against the 196.4 (or 236.5) point; the two-anchor model's own test is whether a third window lands on its line (P4 below).

---

## 5. Prediction (d) — the alternative rung: a wider plateau band on a stated physical argument, and its admissibility

**The alternative.** Leave `W = 900` and raise `h_max` from 0.05 to ≥ 0.16 so that W2R's recorded `h_min = 0.15755` becomes admissible; the physical argument offered would be that the FFD perturbation stays within the mesh's deformation capacity to a larger fraction of the radius.

**Not admissible under `VERIFICATION_CHARTER.md` §2 / §2b as a re-banding of the same claim.** `h_max` is a threshold of the frozen D12R2 item and its W2R re-registration; changing it after `h_min` has been measured is *"an amendment made after the answer exists"*, which *"destroys exactly"* the property the freeze protects (`:150-152`) — the new band would be selected to admit a number already seen, and `§2b` item 1 (`:156-158`) makes amendments legal only *"while there is no answer to tune to"*. D7FR's pre-registration states the family's rule in one line: a band *"inherited unchanged and not re-derived by a lane that has seen an answer"* (`curriculum_D7FR/PREREGISTRATION.md:228-230` @ `faeda019`); *"never re-banded"* (`:423`).

**What WOULD be admissible, and is not this rung:** a separately pre-registered **linearity rung** that measures, before any FD grade and with its own predictions, the objective's departure from linearity over steps 0.05–0.30 (three-point secant-vs-tangent test on the baseline, with `δ_window,env` as the noise floor), and freezes `h_max` for a later item from that measurement. It is a different claim (a secant over a non-linear range is not a derivative check) — the grid cell would carry the caveat "FD at a step outside the small-perturbation range". Cost: ~6 objective stages at `W = 900` ≈ 17 core-min. It is recorded here as the alternative, not proposed over W3, because W3 flips the cell on the same claim the family grades everywhere else (band D at a plateau step) while the linearity rung flips it on a weaker one.

**W3-A1 (a pre-compute amendment W3 would carry, legal because no W3 run directory exists — to be checked by the freezing lane by name):** the `G12R-3` degeneracy branch does not size the step. `δ_window` is always measured and always carries; at a `W` within 0.05 periods of a whole number the comparator reports the envelope value `0.8906/W` in place of the exact spread and says so. Rationale in §2 (the FD arms' period shifts). And **W3-A2:** the launcher writes `"W": 2000` into the manifest so `g3_delta_window` grades the registered window (§1 item 2); the comparator refuses if the manifest `W` and the ledger `W_STEPS` disagree.

---

## 6. Predictions P1–P4, falsifiable before compute

| # | prediction | value / falsifier |
|---|---|---|
| **P1** | W3's S2b (2,400 steps, unchanged staging) is bit-identical to W2R's, so `δ_window(2000)` reproduces exactly | **`4.385710e-04`**; falsified by any other value (a non-deterministic primal, or a staging change) |
| **P2** | `|g(2000)|` | **`1.19 ± 0.18`** (W2R's 1.13984 continued at +10 % per window tripling, ±15 % band); falsified outside `[1.01, 1.37]` |
| **P3 (PRIMARY, BINARY)** | `h_min(2000) = 100·δ_eff/|g| ≤ h_max = 0.05`: **an admissible FD step EXISTS** | `admissible: true`; point `h_min = 100 × 4.3857e-04 / 1.19 = 0.0369`, envelope-worst `0.0390` at `|g| = 1.13984`; **falsified iff `|g(2000)| < 0.877`** (exact spread) — or `< 0.8906` on the envelope |
| **P4** | phase-1 cost lands on the two-anchor line | **196.4 core-min ± 15 %** (`[167, 226]`); falsified outside — and a miss re-anchors the model, it does not re-cost the run |

**Then, if P3 holds, the FD line runs as registered in D12R2/W2R with no new gate:** `G12R-5` plateau on the plan steps `[0.004, 0.04, 0.05]` (from `h_min ≈ 0.037–0.039`: `h_min/10`, `h_min`, capped `h_max`), `G12R-6` band D (PASS ≤ 5 %, any sign flip FAIL), `G12R-7` trivial baseline at `10·h*`, `G12R-8` envelope, `G12R-9` planted zeros, `G12R-10` two rows, `G12R-11` optimisation authorised only on a `G12R-6 PASS`. **A `G12R-6` prediction is deliberately not made here** — no unsteady FD number exists in this family in any direction, and a band predicted without one would be a guess wearing a number.

---

## 7. Verdict mapping (the rung's, in the fixed vocabulary)

| outcome | rung verdict | grid cell (gradients / optimisation) |
|---|---|---|
| P3 HIT, `G12R-6 PASS`, S8 reaches `Optimal Solution Found.` | **`PASS`** | `CAN DO` / `CAN DO` (single mesh, 2,450 cells — a caveat, ≤ 1 line) |
| P3 HIT, `G12R-6 PASS`, S8 stopped on its cap | **`GATE REACHED`** (`DAFOAM_CHARTER.md` §9) | `CAN DO` / `CAN DO, CAVEATS` |
| P3 HIT, `G12R-6 GATE FAIL` (outside band D or a flip) | **`GATE FAIL`** | `CAN DO, CAVEATS` (FD-checked, disagrees) / `CAN NOT DO` |
| P3 MISS (`admissible: false` at `W = 2,000`) | **`NOT A RESULT`** — the registered no-launch branch, phase 2 never fires | unchanged; the record then states `|g(2000)|` and the envelope, and the next window is computable from them |
| any refusal (completion clause, planted zero not seen, manifest/ledger `W` mismatch) | **`NOT A RESULT`** | unchanged |
| aggregate memory guard or PETSc failure | **`BLOCKED`** | unchanged |

---

## 8. What this draft could not verify, stated plainly

- `|g(W)|`'s dependence on `W` rests on two points (1.0304 at 300, 1.1398 at 900); P2's band is a stated assumption, not a measured law.
- The envelope constant 0.8906 is the BASELINE series' — the FD arms' series are not on record at any window other than the graded steps that never ran; §2's argument that the perturbed arms land on the same envelope is physical reasoning, not a measurement.
- Phase-4 (S8) cost scales the W2R upper bound linearly; the unsteady adjoint's memory footprint at `W = 2,000` (checkpointing) was not measured — the aggregate-memory guard and `MemAvailable` floor of W2R (`MEM_LIMIT 8g`, floor 14 GiB) must be re-derived by the freezing lane, not inherited.
- The W2R scoring record (`RESULTS_W2R.md`) is not at HEAD; §1 item 2 is this lane's reading of the run-root JSON and the comparator source, owed to the W2R scoring lane and the supervisor for their own read.

**No queue entry, no launch, no freeze. Draft ends.**
