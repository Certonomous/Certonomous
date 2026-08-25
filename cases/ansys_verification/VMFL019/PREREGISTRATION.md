# PRE-REGISTRATION — VMFL019: Transient Flow Near a Wall Set in Motion (Stokes' First Problem)

Standard case, filed from `cases/ansys_verification/_template/PREREGISTRATION_TEMPLATE.md`
(committed blob `8d65d36516bd4273f94ae85e4e391850a5827d3e`). Frozen by sha before any
solver starts (rule 2). Drafted by `ansys-lane-opus48` (Opus 4.8), 2026-08-25.

1. **Case id + manual page:** VMFL019, VM2026R1 p. 77 (title-page verified).
2. **Reference value + unit + source:** the closed-form Rayleigh/Stokes profile
   `u(y,t) = U·erfc(y/(2√(νt)))`, U=0.01 m/s, ν=1e-3 m²/s. At t=5 s the two gate
   points are u_x(0.05)=**6.1708e-3 m/s** and u_x(0.10)=**3.1731e-3 m/s**. Source:
   H. Schlichting & K. Gersten, *Boundary Layer Theory*, 8th ed., pp. 126-127, 2000.
   The manual gives only a FIGURE (.19.2/.19.3), no discrete target row, so the gate
   is against the analytic value directly.
3. **Reference CATEGORY:** **V (code verification).** EXACT closed-form analytic
   (Schlichting) ⇒ scores V, never P (Sanaa 2026-08-25).
4. **Ansys's own reported value (context only):** the manual publishes the Fluent/CFX
   profiles as figures overlaid on the analytic curve; no numeric table is printed, so
   there is no scalar Ansys value to quote here (figure-only agreement).
5. **GATE expression + tolerance:** at the finest level (L3), BOTH probes:
   `|u_lab − u_analytic| / |u_analytic| ≤ 0.01` (1 %). 1 % is above the discretisation
   error a pre-freeze scratch build showed (0.10 % / 0.19 % at L2) and well within the
   manual's figure-agreement class; not chosen from a graded run. BOTH probes must pass.
6. **Level family (grid triple — 3 levels):** space (Ny) AND time (Δt) refined together
   by ratio 2. L1 Ny=30 Δt=0.05 s; L2 Ny=60 Δt=0.025 s; L3 Ny=120 Δt=0.0125 s; endTime
   5 s. Solver `icoFoam` (transient incompressible laminar), ν=1e-3 m²/s. Domain
   0.75 m (x, cyclic — the flow is homogeneous in x for the infinite plate) × 0.3 m (y),
   1 cell z (empty). Bottom wall (y=0) fixedValue (0.01,0,0); top wall (y=0.3) held at 0
   (undisturbed: analytic u(0.3,5)=2.7e-5). Gate is on the wall-normal boundary layer,
   the refined y-direction.
7. **CAP + cost_basis:** cap **9 core-minutes total** (est ~0.15 core-min clean × ~60
   slack; the box has 8-10 CPU-bound neighbours — a NEW regime, so slack is taken and
   the per-run rate will be MEASURED from this case's own iterations/s, not assumed from
   any whole-box loadavg). Per-level wall `timeout = 180 s` (=3 core-min at ranks=1;
   ~60× the ~3 s clean solve). Ranks=1, wall timeout IS the core-minute cap. Overrun
   STOPS the level (rule 12). Rate $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.
8. **Comparator path + sha:** `cases/ansys_verification/VMFL019/grade_vmfl019.py`, blob
   **`c20d72fc4e03a431f0d874b943420ca2de1c6a8c`**. Planted-zero (1.234e-3 m/s on u_x of
   probe 0, read back from disk), strict completion (rc, End, last time==5, U+p present,
   ExecutionTime count == 5/Δt per level, age guard U newer than 0/U), Roache triple per
   probe. `check_grader_self_blindness.py` **exit 0**; `--selftest` green; `--dryrun-reader`
   parses the real vector-probe file.
9. **TIER CEILING declared in advance:** **HOLDS** is reachable (V and G both directly
   available, reference exact). Fallback: if either probe's triple is CONVERGING with a
   noise-floor (untrustworthy) observed order, the ceiling drops to **GATE REACHED**.
10. **FALSIFICATION clause:** WRONG here if a finest-level probe deviates from the analytic
    erfc value by >1 % (→ `GATE FAIL`), or the space+time triple is not `CONVERGING`
    (→ `NOT A RESULT`). Real possible outcomes: a wrong ν, a contaminating top BC (if the
    boundary layer reached y=0.3), or a too-coarse Euler step would each drive a probe out
    of band or break monotone convergence.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING. A GATE FAIL or NOT A RESULT is recorded honestly, never softened.*
