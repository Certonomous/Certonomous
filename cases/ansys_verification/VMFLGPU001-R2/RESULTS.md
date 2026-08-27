# VMFLGPU001-R2 — RESULTS

**Case:** VMFLGPU001-R2 — the lab's GPU solver path exercised on Flow Between
Rotating and Stationary Concentric Cylinders (Taylor–Couette), Ansys Fluid
Dynamics Verification Manual, Release 2026 R1, **p. 225**. CPU parent VMFL001 /
VMFL001-R2. **Successor to VMFLGPU001 (R1), register row #33 (`NOT A RESULT`).**
**Verdict: `GATE REACHED`.** Graded by `ansys-lane-opus48` (lane B), 2026-08-27.

## 1. What is under verification

Not the physics — the physics is the known control, already graded on the CPU as
VMFL001-R2 (`PASS`). The object is **the lab's GPU solver path**: OpenFOAM v2606 +
petsc4Foam + PETSc-CUDA on an NVIDIA **L4** (sm_89, g6.xlarge, us-east-2). The
gate therefore has **three limbs**, and a miss on limb A is `NOT A RESULT`
whatever the physics says.

## 2. Freeze (CLAUDE.md rule 2)

- Frozen at commit **`0bc37653f8105c561dbc1938db2927734cf379cd`** (Amendment 1,
  pre-compute — the freeze check bound to the launch tree).
- `PREREGISTRATION.md` blob **`c43d368736e08f903dff0e02bd15429b486030b5`** — disk
  == HEAD at launch (`LAUNCH_RECORD.txt`).
- `grade_vmflgpu001_r2.py` (comparator) blob
  **`6a5d0fe7b68e5f184edb97114a2dae31dcf7512c`** — UNCHANGED by Amendment 1;
  verified this grading: the frozen disk copy at `/home/ubuntu/laneR2_freeze/…`
  hashes to `6a5d0fe7…` exactly before its output was believed. Freeze sha taken
  from `LAUNCH_RECORD.txt`, never derived from a commit subject
  (VERIFICATION_CHARTER v1.12).
- `--selftest`: **43 checks GREEN, each shown able to fail** (exit 0), run under
  the frozen comparator before grading.

## 3. R2's two repaired controls (why R1, row #33, was NOT A RESULT)

R1 was `NOT A RESULT`: its frozen plateau clause **I5** refused on the L1 probe
because a perfectly converged channel and a dead one look identical to a
peak-to-peak tolerance. The supervisor ruled (2026-08-27) that R1's clause
**stands and is not amended** — amending a frozen gate toward a good-looking
answer is the bright line the lab will not cross. R2 is a **fresh registration**
that changes ONLY the controls, every gate constant byte-identical to R1:

1. **Liveness plateau floor** — a demonstrably-live channel is no longer refused
   merely because its last window is bit-identical; a dead channel that never
   moved still refuses (liveness floor 4.548e-4 m/s).
2. **Limb-A GPU tell re-based on PETSc's GPU %F table value** — R1's tell1 (legend)
   and tell3 (ksp_view type) were loose/miscalibrated for this build. tell1 is
   NOT USED (loose on a CUDA build) and tell3 DROPPED (options-block echo on this
   build); the R2 reader reads the GPU %F table VALUE.

**Both repaired controls graded cleanly here** — the plateau passed on all levels
and the re-based limb-A tell fired.

## 4. The three limbs (all HELD)

**Limb A — GPU actually executed (physics-critical, binary).** HELD at every
level (L1_16x64, L2_32x128, L3_64x256): GPU %F > 0 on the `-log_view` event rows,
tell2 shows a PID holding device memory, and the **forced-CPU control arm showed
GPU-ABSENT** (the discriminator). A CPU number that happened to match the
reference would verify nothing about the GPU path; here the GPU path is proven to
have run.

**Limb B — GPU ≡ CPU** (`|q_GPU − q_CPU|/|q_CPU| ≤ 1e-4`, both channels, every
level). **HELD:** worst = **3.74e-11** at L3_64x256 @ r = 0.035 m. On L1 and L2 the
GPU and forced-CPU arms are bit-identical (rel = 0.0). The GPU linear-algebra path
reproduces the lab's own CPU answer to eleven digits.

**Limb C — physics vs the exact closed form** (`|q_GPU − q_exact|/|q_exact| ≤
0.02`). **HELD:** worst = **5.29e-4 (0.053 %)** at r = 0.020 m. The reference is the
closed-form annular-Couette solution `v_theta(r) = omega·R_i²(R_o²−r²)/(r(R_o²−R_i²))`,
**evaluated by the comparator itself** (White, *Viscous Fluid Flow* §3-2.3):
v_exact = 0.0151201 / 0.0105336 / 0.00718656 / 0.00454781 m/s at r = 20/25/30/35 mm.

Lab value, v_theta(GPU, L3_64x256) at r = 20/25/30/35 mm =
**0.0151121 / 0.0105288 / 0.00718355 / 0.00454578 m/s**.

**Context only, never the gate:** manual "Target" 0.0151/0.0105/0.0072/0.0046;
Ansys Fluent GPU 0.0152/0.0105/0.0072/0.0045. The lab-evaluated closed form
differs from the manual's printed 2-s.f. column by 1.15 % at 35 mm, so the two are
not interchangeable — the exact form is the gate, the printed column is context.

## 5. Roache triple (rule 5) and controls

- Gate quantity v_theta(35 mm) across L1/L2/L3 = **0.00451458 / 0.00453957 /
  0.00454578 m/s** — state **`CONVERGING`**, ratio R = **0.24827**, observed order
  p = **2.0100**, **GCI_fine = 0.05635 % at Fs = 1.25**, f_extrapolated =
  0.00454783 m/s. Monotone, second order, well inside the band.
- **Planted-zero control (rule 3): SEEN on all 4 gate channels** — 0.001234 m/s
  planted at each radius moved that radius by exactly 0.001234 m/s and no other;
  plant / smallest gated value = 0.271 (> 0.1), so a working point reader cannot
  be refused by dilution.
- **Reference kind: closed-form/exact — buys V (`GATE REACHED`), NEVER P.** The
  tier ceiling is `GATE REACHED`, hard-coded in the comparator, which cannot print
  `PASS`. All three limbs held and the triple converged, so the case reaches its
  ceiling: **`GATE REACHED`.**

## 6. Strict completion (rule 4) and infrastructure

All six solves: rc = 0, an `End` line, last time == endTime, declared fields
present at endTime, `Time =` count == endTime, age guard met, cap_fired = 0.
**INFRASTRUCTURE note (L-342, does not touch the verdict):** the `ExecutionTime`
line count is **endTime + 2** at every level (petsc4Foam prints two init timing
lines inside `Time = 1`); reported as a labelled warning, not a refusal.

## 7. Cost (rule 12)

- **Measured (`COST.txt`):** total wall 1588 s → **0.441111 GPU-h**; CPU control
  arm **9.0500 core-min** on the same billed instance. Per-arm wall: L1 gpu 26 /
  cpu 4; L2 gpu 132 / cpu 26; L3 gpu 880 / cpu 513 s. Caps: 2.0 GPU-h (used
  22.1 %, cap_fired 0) and 40 core-min CPU arm (used 22.6 %). No overrun.
- **Estimate:** 0.44 GPU-h (from R1's measured 0.441667, row #33); CPU arm ~9.2
  core-min (R1 measured 9.15).
- **Ratio actual/predicted:** **1.003×** on GPU-h, **0.984×** on CPU-arm core-min —
  essentially bang-on; the estimate was drawn from R1's measured figures and R2
  reproduced them. Gap attribution: **misprediction ≈ 0**, no contention
  (dedicated GPU instance), **WASTE 0.000** (no truncation, no re-run).
- **$ derived:** 0.441111 GPU-h × **$0.8048/GPU-h** (g6.xlarge us-east-2,
  published list) = **$0.3550, DERIVED not measured** — the box cannot read its own
  billing (`COMPUTE_BUDGET_CHARTER.md` §5); **the console figure is still owed and
  supersedes.** The CPU arm runs on the same billed instance, so its core-minutes
  are work, not a separate charge. Calibration row **C-181**.

## 8. Honest performance note — a correctness vehicle, not a speedup

At these problem sizes the **GPU arm is SLOWER than the CPU arm** (L2: 132 s GPU
vs 26 s CPU; L3: 880 s GPU vs 513 s CPU). This is **expected and registered as
expected**: at ~1k–16k cells the host↔device transfer overhead dominates the
linear-algebra work, so the GPU path cannot win on wall time. **It is NOT a
finding and NOT a defect.** But it is recorded plainly so the lab implies no
speedup it did not measure: **at these sizes the GPU path is a CORRECTNESS
vehicle — the object verified is that the CUDA linear-algebra path produces the
right answer (limbs A+B+C) — not a performance result.**

## 9. Artifacts

- Run root (on GPU instance 3.15.199.152):
  `verification/runs/ansys_verification/VMFLGPU001-R2/` — `GRADING_VMFLGPU001-R2.json`,
  `gpu/` + `cpu/` each L1/L2/L3, `RUN_RC.{L1_16x64,L2_32x128,L3_64x256}.{cpu,gpu}`
  (rc = 0 each), `COST.txt`, `LAUNCH_RECORD.txt`, `TOOLCHAIN_MANIFEST.txt`,
  `launcher.queue.out`.
- Frozen comparator that ran: `/home/ubuntu/laneR2_freeze/cases/ansys_verification/VMFLGPU001-R2/grade_vmflgpu001_r2.py`
  (blob `6a5d0fe7…`).
- Register row **#39**; calibration **C-181**.

**Note on STATUS.VMFLGPU001-R2:** it is STALE (`launcher_rc=1 end=2026-08-27T18:09:24Z`,
from the aborted 18:09Z attempt). The live launch is `LAUNCH_RECORD.txt`
(`launched_utc = 2026-08-27T18:55:29Z`). STATUS was not deleted, moved or
rewritten — nothing under `verification/runs/` is tidied.

**Note on the launcher FIELD-COMPLETENESS guard:** it printed `required={}` in
this run. It is VACUOUS, recorded in Amendment 1 as NOT EVIDENCE for this case,
and is not cited anywhere in this record as evidence of anything.
