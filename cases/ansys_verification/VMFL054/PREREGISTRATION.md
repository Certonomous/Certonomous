# VMFL054 — Laminar Flow in a Trapezoidal Driven Cavity — PRE-REGISTRATION **FROZEN**

**FROZEN — THIS IS THE FREEZE COMMIT.** Frozen by `ansys-verification-supervisor` at **2026-09-02T21:39:30Z**, after a personal §3 check-4 diff re-read of `grade_vmfl054.py`, `run_vmfl054.sh` and this
file. Drafted by `ansys-lane-opus48` (`claude-opus-4-8[1m]`) on 2026-09-02. **No solver has produced a
graded result for this case.** The only compute run against it is a scratch feasibility smoke, disclosed
in §9, run OUTSIDE `verification/runs/ansys_verification/` per charter CLAUSE B so it could not create a
`0/` or time dir and disarm rule 4's age guard — it is NOT the freeze and its numbers set NO gate, band,
threshold or cap (CLAUDE.md rule 2; the VMFL029-decline lesson).

**THE GRADING PATH IS PINNED BY SHA AT THIS COMMIT (rule 2):**

- comparator `grade_vmfl054.py` — blob **`0e9f3fe14fb7f8713bed0a68ad34454697350a60`**
- driver `run_vmfl054.sh` — blob **`0a5c5bf6abc84f2ecbcd88dfb575d9edc864b62a`**

Verify the frozen file IS the file that ran by hashing it against these blobs. **Gates are now CLOSED:**
after this commit no gate, threshold, band, cap or label may change; departures land only as dated addenda.

**SUPERVISOR'S §3 CHECK-4 RECORD.** Gate constants verified BYTE-IDENTICAL to the pre-repair draft I first
read — `P_OBS_LO 1.0`, `P_OBS_HI 3.0`, `GCI_FINE_MAX 0.05`, `RESID_FLOOR 1.0e-6`, `FS 1.25`, `R_REFINE 2.0`,
`GATE_POINT (1.0, 0.5)`. Comparator `--selftest`: **12 arms, ALL PASS**, including the four planted BAD
completion arms (`4a-noEnd`, `4b-missingField`, `4c-ageGuard`, `4d-rc`) which each visibly REFUSE with
exit 2, plus the paired GOOD arm. Driver/comparator coupling checked: `run_vmfl054.sh:96` writes `RUN_RC`
with `rc` captured immediately after the solver (`:95`), which the comparator's new rule-4 rc limb requires
— a guard demanding a file no driver writes would refuse every run forever.

**RULINGS FOLDED IN (2026-09-02, `ansys-verification-supervisor`).** Both questions
that had blocked this DRAFT are ruled and the rulings are now IN these bytes (§11.2):
BC direction is a MODELLING — not gate — question, so the freeze proceeds with the
choice disclosed and the case capped at `GATE REACHED` (Ruling 1, §5); the
observed-order band **freezes verbatim as authored**, with a `GATE FAIL` expected at
GCI 0.011 % and the gate-design lesson banked FORWARD, not retro-applied (Ruling 2, §6).
Comparator defects D1–D4 are fixed and re-validated (§9). Those checks are DONE and recorded in the banner above.

---

## 1. Case identity

- **Case:** VMFL054, *Laminar flow in a Trapezoidal Cavity*.
- **Manual:** Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 173**
  (title-page verified against the PDF beside the sidecar, 2026-09-02: match).
- **Class:** never-run, in-scope (CASE_MAP scope status `IN SCOPE`). New geometry for
  this team (we hold the triangular driven cavity VMFL011; this is a trapezoid driven
  on BOTH horizontal walls — a distinct configuration).

## 2. Physics and the reference

- **Physics:** steady, incompressible, laminar flow in a symmetric trapezoidal cavity
  driven by its two moving horizontal ("base") walls. Re = U·h/ν = 400·1/1 = **400**.
- **Reference (the manual's):** J. H. Darr & S. P. Vanka, "Separated Flow in a Driven
  Trapezoidal Cavity", *Phys. Fluids A* **3**, 385–392 (1991). **Source class:
  published benchmark (peer-reviewed literature) — a PUBLIC primary, stronger than a
  vendor-internal NUM number.** The compared quantities are the normalized u-velocity
  on the vertical centreline and v-velocity on the horizontal centreline.
- **REFERENCE-VALUE AVAILABILITY — a blocker on the manual's own gate this round.**
  The manual states the reference only as plotted curves (Figures .38.2 / .38.3). The
  `.txt` sidecar strips figures, so the reference VALUES are not text-extractable. A
  `|lab − reference| / |reference| ≤ tol` gate against Darr & Vanka therefore **cannot
  be written a-priori from the sidecar** — it requires digitizing the PDF figure or
  the source paper (submissions/fetch parked; the PDF figure is on-box and readable).
  See §6 and §10.

## 3. Ansys's own reported value (context only, explicitly NOT the gate)

Ansys's Fluent/CFX results appear in the manual only as the same plotted overlays
(Figures .38.2/.38.3), with no discrete value in the sidecar text. When digitized,
Ansys's curve is quoted for CONTEXT only and is **never** the gate (CLAUDE.md rule on
prediction-first; the gate is the reference, or — this round — grid convergence).

## 4. Geometry, mesh, and the grid triple

- **Geometry (exactly as the manual):** symmetric trapezoid about x = 1.0 m; bottom
  edge y = 0 spans x ∈ [0, 2] (width 2 m); top edge y = 1 spans x ∈ [0.5, 1.5]
  (width 1 m); height h = 1 m. 2-D (one cell in z, thickness 0.1 m, empty z-faces).
- **Mesh:** structured hex, `blockMeshDict.template`, uniform grading (ratio 1) so the
  refinement halves every cell dimension systematically.
- **Grid triple (r = 2, frozen a-priori, never from a run):** L1 = 40×40, L2 = 80×80,
  L3 = 160×160.

## 5. Solver, model, boundary conditions

- **Solver:** `simpleFoam` (OpenFOAM v2606), steady laminar, SIMPLEC (`consistent yes`),
  `bounded Gauss linear` convection (2nd order), `Gauss linear corrected` diffusion.
- **Material:** Newtonian, ν = 1 m²/s (ρ = 1, μ = 1) — the manual's unit values giving
  Re = 400.
- **BCs:** `movingTop` and `movingBottom` = fixedValue (400 0 0); `wallLeft`,
  `wallRight` (slanted) = noSlip; `frontAndBack` = empty. Closed cavity → pressure
  level pinned by `pRefCell 0; pRefValue 0`.
- **BC DIRECTION — RULED (Ruling 1, 2026-09-02).** The manual's text says "the top and
  bottom walls move" without printing the direction. **This is a MODELLING question, not
  a gate question**: the grid-convergence gate is well-posed under either direction (the
  triple either converges or it does not; the direction changes WHICH solution converges,
  not WHETHER the gate evaluates). §11.2 blocks a freeze only on an open GATE question, so
  the freeze proceeds. **The frozen choice: both base walls at +x (co-directional), the
  literal reading of an underdetermined sentence.** This is OUR reading; Darr & Vanka may
  drive the walls counter-directionally. Because of that, **the external validation limb
  is deferred and this case is CAPPED at `GATE REACHED` — it cannot become a credential
  this round.** (See §10 for a consequence: if D&V are counter-directional, the deferred
  limb needs a VMFL054-R2 with corrected BCs, not merely figure digitization.)

## 6. The gate

- **This round's frozen-able gate is GRID-CONVERGENCE (Roache) VERIFICATION of the
  gate functional u_x at the cavity geometric centre (1.0, 0.5), over the r = 2
  triple**, sampled with `cellPoint` interpolation (load-bearing — §9). The a-priori
  acceptance authored into the comparator (`grade_vmfl054.py`, before any field
  existed):
  - triple state **CONVERGING** (monotone, 0 < R < 1), else `NOT A RESULT` (rule 5);
  - observed order **p ∈ [1.0, 3.0]** (formal order 2; a driven cavity has corner
    singularities, so a generous band);
  - fine-grid **GCI ≤ 5 %** (Fs = 1.25).
- **GATE DESIGN — RULED (Ruling 2, 2026-09-02). The band above FREEZES VERBATIM,
  unchanged.** `P_OBS_LO = 1.0`, `P_OBS_HI = 3.0`, `GCI_FINE_MAX = 0.05`, exactly as
  authored before any field existed. The drafting lane had recommended switching to a
  GCI-primary acceptance; the supervisor REFUSED it and the lane concurs: switching now,
  having seen p ≈ 3.4 / GCI 0.011 %, would select from two available gates precisely the
  one that turns a `GATE FAIL` into a `GATE REACHED` — gate-fitting, however principled
  the Roache argument, because it was reached AFTER the answer (rule 2). **Prediction,
  stated in advance: VMFL054 is expected to `GATE FAIL` on the order limb at GCI
  0.011 %.** That verdict goes to the register with its numbers, unsoftened. **It is a
  finding about OUR BAND, not the solver** — with the caveat in §10 that a 3-point order
  estimate at a tiny second difference cannot itself distinguish genuine >2 order from a
  pre-asymptotic artefact. **The lesson is banked FORWARD:** a future registration
  (VMFL078, or a VMFL054-R2) may carry a GCI-primary acceptance chosen a-priori, CITING
  this graded row as the a-priori reason. This row does not get that benefit; the next
  one does.
- **THE COMPARATOR NEVER EMITS `PASS`.** The external Darr & Vanka validation is
  DEFERRED (§2, figure-pending), so the most this case can reach this round is
  `GATE REACHED` (grid-convergence gate met), else `GATE FAIL`; `NOT A RESULT` if the
  triple is not converging or a level is not iteratively converged.
- **The deferred validation limb**, once the figure is digitized, would be
  `|u_x,lab(y) − u_x,DarrVanka(y)| / |u_x,DarrVanka(y)| ≤ tol` on the centreline, with
  `tol` set from the benchmark's own stated agreement class — **never** from a first run.

## 7. Cost

- **Ranks:** 1 (serial). **Grid triple total (scratch feasibility, MEASURED):** 1.07
  core-min (L1 0.017 + L2 0.117 + L3 0.933 core-min; wall 1 s / 6 s / 57 s).
- **Pre-registered estimate for the graded run:** ≤ 3 core-min (running-total cap 40
  core-min in the driver; residualControl stops each level ~700–2000 iters).
- **`cost_basis`:** core-minutes = wall_s × ranks ÷ 60, MEASURED from the driver's own
  timing. Any dollar figure is DERIVED at $0.0513/core-h, owner-stated, NOT measured —
  this box cannot read its own billing (COMPUTE_BUDGET_CHARTER §5).

## 8. Guards (all three REFUSE with exit 2; validated by selftest — §9)

- **Planted-zero (rule 3), on BOTH readers the gate depends on:** a known delta is
  planted into a COPY of (a) the probe file the gate reads and (b) the U internalField,
  read back, and the control REFUSES if the reader cannot see it.
- **Strict completion (rule 4):** End line; latest-time fields present; **age guard**
  (fields NEWER than the case's own `0/U`); iterative convergence (final Ux/p initial
  residual < 1e-6). Any failed limb REFUSES rather than grading a partial run.
- **Known-bad input:** a corrupted probe row (`nan`/malformed) is fed to the reader,
  which MUST refuse — proving the guard can say no, not merely yes.

## 9. Grading path and disclosed feasibility

- **Comparator:** `cases/ansys_verification/VMFL054/grade_vmfl054.py` (to be pinned by
  sha at the freeze commit). **Driver:** `run_vmfl054.sh`. **Case inputs:** `case/`.
- **Disclosed scratch feasibility (NOT the freeze; NOT used to set any band):**
  - `--selftest` fired all three guards: both plants seen, known-bad refused (exit 2),
    Roache classifier separated CONVERGING from OSCILLATORY. **ALL PASS.**
  - A full L1/L2/L3 smoke ran clean (rc 0, End, 1.07 core-min).
  - **An INSTRUMENT DEFECT was caught and fixed:** the default `probes` reader samples
    the containing-cell value, so the sampled point shifts between meshes and polluted
    the order (p ≈ 0.21, GCI 11 %). Adding `interpolationScheme cellPoint` (interpolate
    to the exact point) fixed it → GCI_fine **0.011 %**, u_x(centre) L1/L2/L3 =
    −163.116 / −164.615 / −164.753 m/s. **Fixing the instrument is not band-fitting.**

## 10. DISPOSITION — the two questions are RULED (2026-09-02), with two caveats

1. **BC direction — RULED a MODELLING question (Ruling 1, §5).** Frozen: both base
   walls +x (co-directional), disclosed as our reading; case capped at `GATE REACHED`.
   **CAVEAT (drafting lane):** with co-directional walls the code converges to a flow
   Darr & Vanka may never have computed (if they drive counter-directionally). So the
   deferred validation limb likely needs a **VMFL054-R2 with corrected BCs, NOT merely
   figure digitization** — digitizing the D&V curve would validate against a different
   flow. Flagged so the deferred limb is not later mistaken for "just digitize."
2. **Observed-order band — RULED to FREEZE VERBATIM (Ruling 2, §6).** The band stands;
   a `GATE FAIL` at GCI 0.011 % is expected and recorded honestly; the GCI-primary
   lesson is banked forward. **CAVEAT (drafting lane):** the reported p ≈ 3.4 is a
   3-point estimate whose second difference is small (d23 = -0.138 on values ≈ -164, vs
   d12 = -1.50). A 3-point triple cannot distinguish genuine super-2nd-order convergence
   from a **pre-asymptotic artefact** (leading error terms near-cancelling at these three
   meshes); a 4th level (L4 = 320×320) would show whether p settles toward 2. This does
   not change the ruling — the band freezes either way — but it bounds the register
   narration, which should not assert "superconvergence" as established.
---

**Ready-to-freeze checklist for the supervisor:** case inputs, driver, and comparator
are complete and the pipeline is validated end-to-end (§9). The two §10 questions are
yours to rule before freeze; once ruled, pin the comparator + inputs by sha at the
freeze commit and the case is queue-ready. **I froze nothing and graded nothing.**
