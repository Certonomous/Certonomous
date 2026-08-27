# VMFLGPU001 — GPU solver path, concentric-cylinder (Taylor–Couette) Couette flow: `NOT A RESULT` (comparator refused)

## VERDICT: `NOT A RESULT` — the frozen comparator REFUSED (exit 2) at the plateau clause I5

The frozen comparator `grade_vmflgpu001.py` (blob `21fa2387`, the Amendment-4 repair
of the launch-time `f4b07b7f`) refused on its **frozen plateau clause I5** — a null
range on the L1 gate-probe series — and produced no graded verdict. Per the
supervisor's ruling of 2026-08-27 the frozen clause **STANDS and is not amended**
(the reason is recorded below), so that refusal **is** the result. Drafted by
`ansys-lane-opus48` (lane H) for the supervisor's audit. Manual **p. 225**; reference
the **exact analytical** Taylor–Couette solution `v_theta(r) = omega·R_i²(R_o²−r²) /
(r(R_o²−R_i²))` (White, *Viscous Fluid Flow* §3-2.3); **tier ceiling `GATE REACHED`**
(a closed-form/exact reference buys V, never P; the comparator cannot print `PASS`).

### The refusal, exactly

`grade_vmflgpu001.py --run-root …/VMFLGPU001` (blob `21fa2387`) → **exit 2**, verbatim
from `verification/runs/ansys_verification/VMFLGPU001/GRADING_regrade.txt`:

> REFUSE (VMFLGPU001 I5): L1_16x64: the plateau window has NULL RANGE (peak-to-peak
> exactly 0 over 600 samples). A dead field and a perfectly converged one look
> identical to a tolerance (Amendment 4 item 4).

with, on the same run, the C7 (ExecutionTime) clause emitting only an INFRASTRUCTURE
warning and NOT refusing (L-342, Amendment 4):

> WARNING(INFRASTRUCTURE): L1_16x64: INFRA: ExecutionTime lines 3002 != endTime 3000
> (L-342: a count of TIMING-REPORT lines is a property of what the libraries print,
> not of the physics. It does not touch the verdict.)

### Diagnosis — the null range is a PHYSICS FACT, not a reader/infrastructure defect

Measured by this lane on the preserved artifacts (both arms), replicating the frozen
`probe_series` exactly — the L1 gate probe (v_theta at the triple radius r = 0.035 m):

| level | full-history range | last-600 peak-to-peak | distinct in last 600 | bit-identical tail |
|---|---|---|---|---|
| L1 (GPU) | **4.639e-3** (rose 1.86e-16 → 4.639246e-03) | **0.000** | **1** | **1662 iters** |
| L1 (CPU) | 4.639e-3 (rose 1.86e-16 → 4.639246e-03) | 0.000 | 1 | 1776 iters |
| L2 (GPU) | 4.463e-3 | 1.093e-11 | 585 | 1 |
| L3 (GPU) | 4.577e-3 | 3.527e-08 | 600 | 1 |

The L1 channel is **demonstrably live**: it rose by the full magnitude of its final
value (4.639e-3, from ~0 at iteration 1) and then went **bit-identical for its final
1662 (GPU) / 1776 (CPU) iterations** — a perfectly converged double-precision fixed
point, not a dead reader. The reader read the correct window and column; 600 samples
are present; no poller file is missing and there is no off-by-one. L2 and L3 pass the
plateau (ptp below the 1e-6 tol); **only L1 hits I5**. This is neither a reader defect
nor "does not plateau" — it plateaus *perfectly*, which the null-range guard refuses to
certify because peak-to-peak alone cannot separate a perfectly converged channel from a
dead one, and the frozen clause was written to **refuse rather than guess**.

### The ruling — the frozen clause STANDS (supervisor, 2026-08-27, [lab-attributed])

The bright line the supervisor drew: a post-compute instrument repair is legal only when
**the defect is provable from the frozen document itself, with no reference to any run
output.** The I5 liveness of this channel could be established **only by reading the
run's own values** (the full-history range 4.639e-3). Amending the clause now would be a
change justified by the answer, moving VMFLGPU001 from no-verdict toward `GATE REACHED`
— the favourable direction — and the line is not crossed for a good-looking case. The
remedy is **forward, not backward**: a liveness-controlled plateau clause (ptp < tol
**AND** full-history range ≥ a pre-registered liveness floor) is registered before
compute in **VMFLGPU001-R2** (this row's successor) and in VMFLGPU003+. This row stays
`NOT A RESULT`.

### The physics beside the verdict — CONTEXT, explicitly NOT THE VERDICT

The comparator refused before computing the gate, so the numbers below were computed
**independently by this lane** from the preserved sampled `gateAxis` set files, and are
recorded as context only. **The lab is not claiming this physics as a result** — it has
no frozen-comparator verdict behind it.

- **Gate quantity** v_theta at r = 35 mm, GPU arm, three levels: **4.51458e-3 / 4.53957e-3
  / 4.54578e-3 m/s**. Triple is **CONVERGING** (d21 = −6.204e-6, d32 = −2.499e-5, **R =
  0.24827**), observed order **p = 2.010**, monotone.
- **Agreement with the exact closed form** (four radii 20/25/30/35 mm), GPU arm:
  L1 0.75 % / L2 0.18 % / L3 **0.045 %** — textbook second-order grid convergence.
- **Limb C** (finest vs exact) at r = 35 mm: **0.0446 %**, well inside the frozen 2 % band.
- **Limb B** (GPU vs forced-CPU): the arms agree to the last digits (final gate probe
  bit-identical across arms), so the GPU linear-algebra path reproduced the CPU answer.
- **The GPU path genuinely ran** (see the note on limb A below).

So the honest reading: the physics looks strong — a clean second-order convergence to
the exact Taylor–Couette solution — and **the lab is deliberately not claiming it**,
because the frozen instrument refused before grading it and a lane does not manufacture a
verdict the instrument declined to produce.

### A further finding recorded (NOT acted on here): the limb-A tells are miscalibrated for this build

Independently of I5, this comparator's limb-A tells `tell1_gpu_flops` and `tell3_cuda_type`
are defective readers for this PETSc build (the same defect diagnosed and repaired in
VMFLGPU002 under the supervisor's §2d.1 ruling): `tell1` matches the arm-independent
`-log_view` legend and `tell3` expects a `type: aijcusparse` ksp_view line this build
echoes only in the options block. 001's I5 refusal fires *before* limb A
(`iterative_convergence` runs before `limb_A`), so this comparator never reached limb A;
the finding is recorded so that VMFLGPU001-R2 carries the repaired tells.

### Strict completion (rule 4) — HELD at all six solves (from Amendment 4, re-confirmed)

`rc = 0` at all six (3 GPU + 3 CPU), an `End` line each, `Time =`-line count == the
registered endTime (3000/3000/6000), the declared fields present at endTime, the age
guard met (every endTime field newer than the case's own `0/`), and the ExecutionTime
+2 reclassified INFRASTRUCTURE (petsc4Foam init prints). The instrument refused; the
solver did not fail.

### Provenance
- **Freeze commit:** `0429091e` (2026-08-26 17:31:44Z, "VMFLGPU001 FREEZE", zero compute);
  prereg blob at launch **`b9bb3779`**, current blob **`ed697a13`** (Amendment 4 appended).
- **Comparator:** launch blob **`f4b07b7f`**; re-grade blob **`21fa2387`** (Amendment 4,
  C7 reclassification), blob-verified == HEAD.
- **Freeze proven at launch:** `LAUNCH_RECORD.txt` records prereg_sha_head == prereg_sha_disk
  == `b9bb3779` and comparator_sha_head == comparator_sha_disk == `f4b07b7f`, written
  before any solver ran (host `ip-172-31-44-162`, launched 2026-08-26T22:17:08Z).

## COST (rule 12 calibration)
- **Measured actual:** **0.441667 GPU-h** (total wall 1590 s), of a **2.0 GPU-h cap** —
  the cap **never fired**. CPU arm **9.15 core-min** of its 40 core-min cap. `COST.txt`.
- **Pre-registered estimate:** **0.40 GPU-h** (prereg §12). **Ratio actual/predicted =
  1.10** — a modest under-prediction; no contention noted, no waste (the comparator
  refusal is not a re-run and costs no solver time).
- **$ derived:** 0.441667 GPU-h × $0.8048/GPU-h = **$0.3555**, **DERIVED not measured**
  (published-list rate, g6.xlarge us-east-2; the box cannot read its own billing,
  `COMPUTE_BUDGET_CHARTER.md` §5). **The console figure is still owed and supersedes.**

**Ledger follow-up:** register **row 33** and **calibration C-165** land with this record.
`VMFLGPU001-R2` is registered as this row's successor with a liveness plateau control and
the repaired limb-A tells, and cites this row's refusal as the reason it exists.
