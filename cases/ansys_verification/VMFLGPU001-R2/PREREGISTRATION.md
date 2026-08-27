# VMFLGPU001-R2 — PRE-REGISTRATION (frozen before compute)

**Case:** the lab's GPU solver path on flow between rotating and stationary
concentric cylinders (Taylor–Couette Couette flow), Ansys Fluid Dynamics
Verification Manual, Release 2026 R1, **p. 225**. CPU parent VMFL001 / VMFL001-R2.
**Drafted by `ansys-lane-opus48` (lane H), 2026-08-27, for the supervisor to freeze.**
Prediction-first, frozen by sha before any solver runs (CLAUDE.md rule 2).

**Comparator (frozen grading path):** `grade_vmflgpu001_r2.py`, blob **`6a5d0fe7`**
(committed in the freeze commit; the launcher verifies on-disk == HEAD before any solve).
**Launcher:** `run_vmflgpu001_r2.sh`. **Case inputs:** `case/` (byte-identical to R1).

---

## 1. Why R2 exists — a successor to a REFUSAL, not a second attempt at a number

VMFLGPU001 (R1), **register row #33**, is `NOT A RESULT`: R1's FROZEN plateau clause I5
refused, verbatim:

> REFUSE (VMFLGPU001 I5): L1_16x64: the plateau window has NULL RANGE (peak-to-peak
> exactly 0 over 600 samples). A dead field and a perfectly converged one look identical
> to a tolerance (Amendment 4 item 4).

The refusal was correct behaviour of the frozen clause on a **perfectly converged** channel:
the L1 probe (v_theta at r = 35 mm) rose from 1.86e-16 to 4.639246e-03 m/s and then went
bit-identical for its final 1662 iterations. A peak-to-peak test over the last window cannot
tell that live-and-converged channel from a dead one, so R1's clause refused rather than guess.

**Sanaa's 2026-08-27 §3 anti-gaming clause is the highest authority on why R1 stands and why
R2 is a FRESH REGISTRATION:** *"Frozen gates never edited post-compute"* and *"Converged-but-wrong
= NOT HELD with diagnosis, never a parameter hunt."* R1's I5 liveness could be established only
by reading R1's own run values, so amending R1 would be a change justified by the answer — the
bright line. R2 therefore re-registers the case from scratch, before any R2 compute, changing
**only the controls**.

## 2. GATE-IDENTICAL to R1 — the diff is EMPTY everywhere except the controls

Every gate-determining constant is **byte-identical to R1** (the launcher hashes the case
inputs; the comparator carries the same constants):

| gate element | value (identical to R1) |
|---|---|
| reference | EXACT analytical Taylor–Couette `v_theta(r) = omega·R_i²(R_o²−r²)/(r(R_o²−R_i²))` (White §3-2.3) |
| gate quantity | v_theta sampled at r = 20/25/30/35 mm |
| limb C band | 0.02 (2 %) at the finest level |
| limb B band | 1e-4 (GPU == forced-CPU) |
| tier ceiling | `GATE REACHED` (exact ref buys V never P; comparator cannot print `PASS`) |
| mesh family | 16x64 / 32x128 / 64x256 (r = 2) |
| endTime | 3000 / 3000 / 6000 |
| cap | 2.0 GPU-h; CPU-arm 40 core-min |
| P_MIN floor | 0.05 |

**What moved, and ONLY this:** (a) the plateau control gets a liveness floor (§3), and (b)
limb A's GPU tell is re-based (§4). Both are CONTROLS/READERS, not the gate — no limb, band,
threshold, cap or label moves. R1's answer is on disk (row #33), so any change to a
gate-determining constant would be gate-fitting; none is made.

## 3. THE ONE SUBSTANTIVE CHANGE — the liveness plateau control

**Registered NUMBER, before compute:** `LIVENESS_FLOOR = 0.1 × |v_exact(0.035)| =
4.547810e-04 m/s`. **Derived from the PHYSICS, not from R1's measured range.** The probe
channel is v_theta at r = 35 mm; the initial field is at rest (v_theta = 0) and a correct
solve MUST traverse to the exact analytic value 4.547810e-03 m/s. The floor is 10 % of that
exact value. It is deliberately NOT R1's measured 4.639e-3 m/s (that would be fitting the
control to the answer). A dead channel (full-history range 0) fails; the real solve
(range ~4.5e-3) clears it ~10×; a barely-moved channel fails.

**The clause:** plateau holds when the last-window peak-to-peak `< PLATEAU_TOL` (1e-6, unchanged)
**AND** the full-history range `≥ LIVENESS_FLOOR`. A NULL last-window range (ptp = 0) is no longer
refused when the channel is demonstrably live — that is a perfectly converged double-precision
fixed point, exactly what R1's I5 over-refused.

**Strictly stronger where it must be, driven both ways in `--selftest`:**
- `--drive-refusal dead-channel`: a channel bit-identical from the start (full-history range 0)
  **REFUSES** on the liveness floor. R2 still catches a dead channel.
- `--drive-verdict live-converged`: a channel that rose to `v_exact` then went bit-identical
  (null last-window range, full-history range above the floor) **GRADES to `GATE REACHED`**.
  R2 resolves R1's I5 over-refusal.

## 4. THE OTHER CONTROL CHANGE — limb-A GPU tell re-based (VMFLGPU002 Amendment 5, applied fresh)

R1's `tell1` matched PETSc's arm-independent `-log_view` legend (fires on the forced-CPU arm too
on a CUDA build) and `tell3` expected a `type: aijcusparse` ksp_view line this build echoes only
in the options block — both miscalibrated for this build. R2's limb A reads the GENUINE
discriminator: PETSc's **GPU %F table VALUE** (the last field of a `-log_view` event row), 0 on a
CPU solve and > 0 on a GPU one. `tell2` (a PID holding device memory) is kept; `tell3` is dropped
from the conjunction. The forced-CPU control refuses only on genuine device work in the control
arm. Limb A's MEANING is unchanged. **Driven:** `--drive-refusal gpu-zero-pctf` forges a GPU-arm
log that is cusparse-typed with the legend present (so R1's loose tells would fire) but with
GPU %F = 0 on every event row, and it **REFUSES**.

## 5. L-342 FIELD SPLIT and R-RC (Sanaa 2026-08-27), declared

**PHYSICS-CRITICAL (a failure refuses or votes NOT A RESULT):** rc VALUE (`rc != 0` refuses);
the `End` line; `Time =`-line count == endTime; the fields at endTime; the age guard; the
residual clause; the liveness+plateau clause; limb A's three-limb discrimination; the planted-zero
control; the mass/torque-free reference arithmetic.

**INFRASTRUCTURE (reported, never refuses):** the `ExecutionTime`-line count (petsc4Foam prints
endTime + 2 — two init timing lines inside `Time = 1`); COST.txt and every GPU-hour / core-minute
figure; LAUNCH_RECORD.txt's non-sha bookkeeping; contention/status files; pids/sids/mtimes.

**R-RC as an explicit conjunction (Sanaa's desk ruling):** an absent or unreadable RUN_RC record
is INFRASTRUCTURE and gives rc = **NOT MEASURED** (the level cannot be a PASS; the caller votes
NOT A RESULT) **ONLY WHEN** the other four rule-4 conditions (End line, last Time == endTime,
fields at endTime, age guard) all hold. If any of those is ALSO missing, completion **REFUSES**;
a missing rc record never becomes a blanket pass. **Driven:** `--drive-refusal norc-noend` removes
the rc record AND the End line and the comparator **REFUSES** (C4).

## 6. PLANTED-ZERO CONTROL — plant at the row the reader actually selects (L-347)

The gate is four POINT readers — v_theta at r = 20/25/30/35 mm from the sampled set file — so the
plant-to-read mapping is 1:1 (`PLANT = 1.234e-3` m/s planted at each radius reads back exactly
PLANT, no averaging dilution). The plant is placed at the RADIUS ROW the reader selects, not at an
arbitrary first row (the VMFL011 L-347 failure). Every channel's control executes before any exit,
and the negative arm (an unplanted copy sees 0 move) and the blind-reader refusal are both driven.
The plant is supra-threshold on the smallest gated channel (`PLANT / v(35 mm) > 0.1`).

## 7. COST (CLAUDE.md rule 12) — from the measured 0.4417 GPU-h, with real headroom

- **Estimate:** **0.44 GPU-h** for the whole case (both arms), from R1's **measured 0.441667
  GPU-h** (register row #33). CPU arm ~9.2 core-min (R1 measured 9.15).
- **Cap:** **2.0 GPU-h** ENFORCED by `timeout` in the launcher — **~4.5× headroom** over the
  estimate (R1 used 22 % of it; not a tight cap — VMFLGPU002 came within 10.3 % of its cap and
  that is not repeated here). CPU-arm cap **40 core-min** (R1 used 23 %). An overrun stops the run.
- **$ derived:** 0.441667 GPU-h × $0.8048/GPU-h = **$0.3555**, DERIVED not measured (published-list
  rate, g6.xlarge us-east-2; `COMPUTE_BUDGET_CHARTER.md` §5); console figure owed.

## 8. EVERY GUARD DRIVEN, not read (Sanaa §1 / L-314) — the selftest mutation table

`grade_vmflgpu001_r2.py --selftest` is **43 checks GREEN**, byte-identical under `python3` and
`python3 -O`, **zero `ast.Assert` nodes**. Each guard ships a planted-failure proof:

| guard | driven mutation | must |
|---|---|---|
| liveness floor (dead channel) | `dead-channel` (full-history range 0) | REFUSE |
| liveness (converged live) | `live-converged` (null last window, live) | GRADE to GATE REACHED |
| plateau min samples | `short-plateau` | REFUSE |
| limb A GPU tell | `gpu-zero-pctf` (GPU %F = 0, legend present) | REFUSE |
| limb A missing tells | `limbA-miss` | NOT A RESULT, exit 2 |
| forced-CPU control leak | `control-leak` | REFUSE |
| completion End line | `endline` | REFUSE |
| completion Time count | `time-count-short` | REFUSE (C7) |
| R-RC conjunction | `norc-noend` (rc + End gone) | REFUSE (C4) |
| age guard | `age-guard` | REFUSE |
| planted zero | `plant-blind` + negative arm | REFUSE / see 0 move |
| verdict vocabulary | `vocabulary` under -O | REFUSE |
| P_MIN / STAGNANT / limb-C routing | `below-p-min` / `stagnant-triple` / `limbC-miss` | NOT A RESULT / GATE FAIL |
| petsc4Foam log shape (endTime+2) | `petsc-exec-shape` | GRADE + print INFRA note |

## 9. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and only these
(rule 1). **This rung is `PENDING` until the comparator has graded a completed R2 run.** PASS is
unreachable (exact reference; ceiling GATE REACHED). Enqueueing is not authorisation; the freeze
is committed before any solver runs and the supervisor verifies the commit personally.
