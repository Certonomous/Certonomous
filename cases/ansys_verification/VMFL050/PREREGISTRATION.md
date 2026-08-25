# PRE-REGISTRATION — VMFL050: Transient Heat Conduction in a Semi-Infinite Slab

Standard case, filed from `cases/ansys_verification/_template/PREREGISTRATION_TEMPLATE.md`
(committed blob `8d65d36516bd4273f94ae85e4e391850a5827d3e`). Frozen by sha before any
solver starts (CLAUDE.md rule 2). Drafted by `ansys-lane-opus48` (Opus 4.8) for the
`ansys-verification-supervisor`, 2026-08-25.

1. **Case id + manual page:** VMFL050, VM2026R1 p. 163 (title-page verified; sidecar
   `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`).
2. **Reference value + unit + source:** wall temperature at t=120 s = **393 K**; temperature
   150 mm from the heated wall at t=120 s = **318.4 K** (manual Table .50.1, "Target"
   column). Source: F.P. Incropera, D.P. DeWitt, T.L. Bergman, A.S. Lavine, *Introduction
   to Heat Transfer*, 5th ed., Wiley, p. 287, 2007 — the closed-form semi-infinite-solid
   solution with constant surface heat flux (Eq. 5.62). Exact analytic values recomputed
   by the comparator: **393.0266 K** (wall) and **318.4060 K** (150 mm), matching the
   manual targets to <0.01 %.
3. **Reference CATEGORY:** **V (code verification).** The reference is an EXACT closed-form
   analytic solution (Incropera), so by Sanaa's 2026-08-25 ruling it scores **V, never P**.
4. **Ansys's own reported value (context only, NEVER the gate):** Fluent 392.95 K (wall,
   ratio 0.9998) and 318.41 K (150 mm, ratio 1.0000).
5. **GATE expression + tolerance:** on the temperature RISE (T − 293 K), at the finest
   level (L3), for BOTH probes: `|rise_lab − rise_manual| / |rise_manual| ≤ 0.01`
   (1 %). rise_manual = 100 K (wall), 25.4 K (150 mm). 1 % is chosen from the manual's own
   printed precision (wall 3 s.f. ≈ 0.5 % of the rise; 150 mm 4 s.f. ≈ 0.2 %) widened to a
   round 1 %, and is far above the discretisation error a pre-freeze scratch build showed
   (~0.09 % at L2); it is NOT chosen from a graded run. BOTH probes must pass.
6. **Level family (grid triple — 3 levels, the gate standard):** space AND time refined
   together by ratio 2. L1 Nx=75 Δt=2 s; L2 Nx=150 Δt=1 s; L3 Nx=300 Δt=0.5 s; endTime
   120 s. Solver `laplacianFoam` (transient conduction), DT = α = k/(ρcp) =
   401/(8995.67·381) = 1.170000e-4 m²/s. 1-D bar through the 0.75 m thickness (laterals
   empty = symmetry). Heat-flux BC imposed as ∂T/∂n = +q″/k = 748.1296758 K/m on the
   heated wall; opposite wall adiabatic (zeroGradient).
7. **CAP + cost_basis:** cap **8 core-minutes total** (est ~0.2 core-min clean × ~40 slack
   for I/O contention — the box has ~11 D-state tasks; a clean-box cap would false-kill).
   Per-level wall `timeout = 160 s` (=2.67 core-min at ranks=1; ~80× the ~2 s clean solve).
   Ranks=1, so the wall timeout IS the core-minute cap. Overrun STOPS the level (rule 12).
   Rate $0.0513/core-h, **REPORTED-BY-OWNER, NOT MEASURED** (the box cannot read its
   billing; COMPUTE_BUDGET_CHARTER §5).
8. **Comparator path + sha:** `cases/ansys_verification/VMFL050/grade_vmfl050.py`, blob
   **`22e7c758d117fe23c4b549bbc18512c73d6a2023`**. Planted-zero control (1.234 K, both gate
   quantities, read back from disk), strict-completion rule (rc, End, last time==120,
   T present, ExecutionTime count == 120/Δt per level, age guard T newer than 0/T), Roache
   triple per quantity. `scripts/check_grader_self_blindness.py` returns **exit 0**;
   `--selftest` all-green; `--dryrun-reader` parses the real v2606 files.
9. **TIER CEILING declared in advance:** **HOLDS** is reachable. Both V (analytic) and G
   (grid triple) limbs are directly available here and the reference is exact, so a
   `PASS` with a `CONVERGING` triple and small GCI would be a genuine hold — there is no
   missing limb to cap it at `GATE REACHED`. If the triple is `CONVERGING` but the
   observed order is untrustworthy (noise-floor), the ceiling drops to `GATE REACHED`,
   declared here as the fallback.
10. **FALSIFICATION clause:** the model/solver is WRONG here if the finest-level wall rise
    or 150 mm rise deviates from the analytic value by more than 1 % (→ `GATE FAIL`), or if
    the space+time triple is not `CONVERGING` (→ `NOT A RESULT`). Both are real possible
    outcomes: an incorrect diffusivity, a mis-signed flux BC, or an Euler time step too
    coarse would each drive the rise outside the band or break monotone convergence.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING. A GATE FAIL or NOT A RESULT is recorded honestly, never softened.*
