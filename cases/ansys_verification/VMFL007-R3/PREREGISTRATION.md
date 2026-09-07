# VMFL007-R3 — Non-Newtonian (power-law) Flow in a Pipe — PRE-REGISTRATION **FROZEN**

**STATUS: FROZEN. This is the freeze commit. The gate, tolerance, ceiling, mesh
family, solver arm, convergence clause and caps below are fixed BEFORE any graded
compute (CLAUDE.md rule 2).** The graded run has NOT been launched — it is held on
the auto-mode permission classifier (Sanaa's desk); this document is the prediction
frozen ahead of it, and its entire evidentiary content is that the gate could not
have been chosen to fit an answer.

Frozen by `ansys-verification-supervisor` (ruling 2026-09-07, recorded in §15), the
files authored by `ansys-lane-opus` at its direction. The freeze commit is the
commit that introduces this file; the driver (`run_vmfl007_r3.sh`) resolves
`FREEZE_COMMIT = git rev-parse HEAD` at launch and REFUSES unless this file and the
comparator on disk equal their blobs at that commit (`--verify-frozen` corroborates).

**Cites** register row #8 (VMFL007 run 1, **DIVERGED**) and row #37 (VMFL007-R2
six-arm single-grid slate, **NOT A RESULT**). Re-grades neither; both stand. This is
a NEW registration under `ANSYS_VERIFICATION_CHARTER` §6 — the three-level Roache
triple the R2 slate was built to enable.

**Supersedes the earlier BLOCKED-DRAFT of this file.** Both prior blockers are
cleared (§10, §5); the DRAFT's `⛔ FREEZE BLOCKED` header and its two-blocker text
are removed because the conditions they named are now met and recorded with
evidence. Nothing in the gate moved.

---

## 1. Base check (L-502) — the run-1 physics premise is verified true

Before adopting the "byte-identical to run 1" premise, the five run-1 physics-input
files on disk were hashed (`git hash-object`) against the blobs this registration
asserts; **all five MATCH**, and all five blob objects exist in the repo:

| input | blob | on-disk hash |
|---|---|---|
| `0/U` (coded developed inlet, u_max 3.142857, exponent 3.5) | `b626d65a…` | MATCH |
| `0/p` (kinematic p, outlet fixedValue 0) | `54562f8c…` | MATCH |
| `constant/transportProperties` (powerLaw k 0.01 n 0.4, nuMin 1e-8, nuMax 1.0) | `db848a12…` | MATCH |
| `system/fvSchemes` (steadyState; div bounded Gauss linear; laplacian Gauss linear corrected) | `ad718abf…` | MATCH |
| `system/blockMeshDict.template` (1° wedge, wall at exact R) | `9ea967eb…` | MATCH |

The frozen case directory `case/` here carries these five files byte-identical
(the driver re-checks each against the run-1 blob at launch) plus
`constant/turbulenceProperties` (laminar Stokes), `system/controlDict.template`
(the run-1 template, `__ENDTIME__`/`__WRITEINTERVAL__` substituted), and **the ONE
changed file, `system/fvSolution` (SIMPLE → SIMPLEC, §10)**.

## 2. Case identity and ground truth

- **Case:** VMFL007, Non-Newtonian Flow in a Pipe. **Manual p. 29**, Release 2026 R1
  (title page verified against the PDF, CLAUDE.md rule 15).
- **Physics (manual):** steady laminar flow, power law for viscosity. Reference:
  W.F. Hughes & J.A. Brighton, *Schaum's Outline of Fluid Dynamics*, McGraw-Hill, 1991.
- **Material/geometry/BC (manual p. 29 verbatim):** ρ = 1000 kg/m³; power law k = 10,
  n = 0.4; L = 0.1 m; D = 0.0025 m (R = 0.00125 m); **fully developed velocity profile
  at inlet, mean 2 m/s.** Generalised (Metzner–Reed) Re = 84.597.
- **Solver here:** OpenFOAM v2606 `simpleFoam` + `viscosityModels::powerLaw`
  (k_OF = k/ρ = 0.01 kinematic, n = 0.4, nuMin 1e-8, nuMax 1.0), laminar `Stokes`,
  on a 2-D axisymmetric **1° wedge** (single cell thick).
- **Only the mesh RESOLUTION (§7), the controlDict endTime/writeInterval (§9), and
  the single `fvSolution` arm (§10) differ from run 1.** Everything setting the
  physics is byte-identical, so "the mesh is the only variable across the triple" is
  a machine-checked fact.

## 3. Reference result

```
Δp = (2kL/R) · [ ((3n+1)/n) · (Ū/R) ]^n
   = (2·10·0.1/0.00125) · [ 5.5 · 1600 ]^0.4
   = 60 521.969 Pa   =  60.522 kPa
```
- **Closed-form reference Δp_exact = 60 521.969 Pa** (Rabinowitsch–Mooney /
  Hughes–Brighton). Matches the manual's printed target **60.52 kPa** and the
  register's stated closed form.
- **Reference kind: closed-form / exact** for the SAME model the solver discretises
  (§4). Manual context, never the gate: Fluent 60.41 kPa (ratio 0.998), CFX 61.52 kPa
  (ratio 1.0165). This box has no Fluent and no CFX.

## 4. §12.2 — SAME / PASS-capable — RULED by the supervisor

`ANSYS_VERIFICATION_CHARTER §12.2` = **`SAME`, `PASS`-capable**, cited
`VERIFICATION_CHARTER §2h.8.1 (the exact-PDE rule)`; precedent VMFL004-R2 (row #28).
Under the frozen fully-developed inlet BC the flow is unidirectional and x-invariant,
so the convective term (u·∇)u **vanishes IDENTICALLY — not as a small parameter** —
and the full incompressible power-law Navier–Stokes momentum equation the solver
discretises reduces **EXACTLY** to the 1-D ODE `0 = −dp/dx + (1/r)d/dr(r·τ)` the
closed form solves. Full model = reduced model exactly. **The determination rests
entirely on the frozen `0/U` (blob `b626d65a`): a flat inlet would be `DIFFERENT`.**
The precondition is machine-checked at grade time (UmaxInlet peak ≈ 3.1429, QInlet
mean ≈ 2.0 — a flat slug reads 2.0 and the comparator REFUSES). `PASS`-capability
additionally requires a gradeable (non-pinned, converging) triple — established in §5.

## 5. Gate quantity and pinning — MEASURED, NOT pinned

**Gate quantity:** `Δp_Pa = ρ · ( ⟨p⟩_inlet − ⟨p⟩_outlet )`, ρ = 1000, p kinematic,
area-averaged on each end patch (frozen `pInlet`/`pOutlet` `surfaceFieldValue`
monitors), read at the run's **maximum iteration — a single scalar**, so the
planted-zero plant lands on the exact value the gate consumes (no averaging dilution,
L-340).

**Pinning probe (answer-blind, gate-value-blind), MEASURED on the mesh-robust B2 arm
from the converged L1/L2 monitors** (`verification/runs/ansys_verification/VMFL007-R3-DIAG/{L1_25x25_B2,L2_50x50_B2}`;
RUN_RC rc 0 / End 1 / 30000 iters):

- L1 (25×25) Δp = 60 432.628 Pa, tail ptp 7.7e-6 Pa; L2 (50×50) Δp = 60 498.982 Pa,
  tail ptp 1.49e-5 Pa.
- **d21 = 66.354 Pa; ptp = 1.494e-5 Pa → d21/ptp = 4.44e6** (W=1000), 3.80e6 (W=5000).
  The supervisor's pre-fixed rule `d21/ptp ≥ 100` → **NOT pinned, gradeable.**
- **Planted-zero control fired:** injecting +0.001 kinematic into L2's pInlet tail
  moved d21 by exactly 1.0 Pa = ρ·δ — the reader is live, not blind (the run-1/R2
  scale-invariant blindness is repaired). Finest-level pinning d32/ptp = 1.24e4 (also ≫ 100).

Δp is not pinned by a conservation identity: the imposed quantity is the **flow rate**
(the fixed developed inlet), and dp/dx = 2τ_w/R is the solver's OUTPUT, carrying the
radially-resolved wall-gradient discretisation error, which moves at the scheme order
as the radial mesh refines. **The comparator's fail-closed pinning-refusal stays as
belt-and-suspenders (§11): even this cleared probe does not exempt the graded triple
from refusing if d21 or d32 collapses on the real bytes.**

## 6. Gate and tolerance — CARRIED BYTE-IDENTICAL from run 1

- **Gate:** `|Δp_lab − 60520| / 60520 ≤ 0.005` (0.5 % relative) at the finest level
  L3, **AND** a `CONVERGING` Roache triple on Δp (rule 5).
- **Band: [60217.40, 60822.60] Pa** — the manual's printed 60.52 kPa = 60520 Pa ± 0.5 %.
  **CARRIED BYTE-IDENTICAL from VMFL007 run-1's freeze** (the same band the R2 slate
  carried), never re-derived from any number. The exact closed form 60521.969 Pa lies
  inside it. A gate frozen before run 1 and carried unchanged cannot have been shaped
  by any answer — the freeze's evidentiary content.
- **Ceiling: `PASS`** (§4 ruled `SAME`; the comparator's single verdict path can print
  `PASS` inside the band, `GATE FAIL` outside — no gate-fitting — and `NOT A RESULT`
  if the triple is not `CONVERGING` or any level is not converged).

## 7. Mesh family — isotropic Roache triple

Refinement r = 2, isotropic (both NX and NR double each level; Δx and Δr both halve;
Δx/Δr constant). Laminar, no wall function, so refinement is radial as well as axial.

| level | NX × NR | cells |
|---|---|---|
| L1 | 25 × 25 | 625 |
| L2 | 50 × 50 | 2 500 |
| L3 | 100 × 100 | 10 000 |

GCI at **Fs = 1.25**, quoted beside a `PASS`/`GATE FAIL` only when the three Δp values
are monotone. **Observed-order floor `P_MIN = 0.05`** below which no GCI is quoted
(the value and triple class are still printed).

## 8. Error budget (with signs)

- **Wedge azimuthal geometric bias (N-AV9):** at 1°, `sec(t/2) − 1 = +0.003808 %` —
  Δp biased HIGH; **no grid refinement removes it** (azimuthal), invisible to the
  triple/GCI, below the reference's own ±0.00826 % rounding — the reason for 1° not 5°.
- **Discretisation:** the coarse mesh under-resolves the wall gradient and reads Δp
  LOW; the triple establishes the sign and magnitude. (Measured directionally in the
  DIAG triple: L1 < L2 < L3, all approaching the exact value from below.)
- **Reference rounding:** manual target ±0.00826 %. **Round-off:** ≈ 6e-11 Pa, negligible.

## 9. Convergence clause (rule 5 limb 1, one-way; ANSYS §16.4; N-AV15) — FROZEN CONSTANTS

This run does **NOT** stop on residualControl (that would cut L3 short of its
functional Δp floor — see §14). Each level runs the fixed budget (endTime 60000,
§13) and a level is **convergent iff BOTH hold, each VALUE-BLIND**:

- **(a) FUNCTIONAL PLATEAU:** peak-to-peak of Δp over the last **W = 5000** iterations
  is below **PLATEAU_THRESH = 1e-2 Pa** (1.65e-7 relative — it references the
  convergence NOISE FLOOR, never the reference or band, and cannot backdoor-widen the
  0.5 % gate). Written as a threshold on a window on a named channel, **never as
  `ptp → 0`** (unsatisfiable against the L3 limit cycle, N-AV15 §5).
- **(b) RESIDUALS SETTLED, NOT STILL FALLING:** over the same window the Ux and p
  initial residuals have not dropped by more than **RESID_FALL_FACTOR = 3×**
  (median first-half / median last-half). This is NOT a hard 1e-8 (the limit cycle
  floors p at ~1.5e-8); a **still-falling residual → `NOT A RESULT`**.

A level failing either → verdict `NOT A RESULT`, all Δp printed, via the single
verdict path (which can never turn `NOT A RESULT` into `PASS`). These constants are
frozen in the comparator and were driven by planted controls in `--selftest`.

## 10. Solver arm — B2 (SIMPLEC), the single answer-blind §2ay lever

**Root cause of the run-1/R2 finer-mesh divergence: the SIMPLE velocity-correction
inconsistency** — not the bounded nuMin floor (`calcNu()` floors strain at SMALL
and hard-clips, so the viscosity evaluation cannot itself raise the exception).
Measured (`ARM_SELECTION.md` §3, at 50×50): under-relaxation alone only POSTPONES the
SIGFPE (A5 iter 13274 → p0.2/U0.5 15667 → p0.1/U0.3 20626); a stronger Krylov U solve
makes it WORSE (8086); **only SIMPLEC (`consistent yes`) reaches endTime rc 0.**

**Frozen arm (`system/fvSolution`), the ONLY change from run 1:**
```
solvers { p { solver PBiCGStab; preconditioner DIC; tolerance 1e-12; relTol 0.01; }
          U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-12; relTol 0.1; nSweeps 2; } }
SIMPLE  { nNonOrthogonalCorrectors 0; consistent yes; }
relaxationFactors { fields { p 1.0; } equations { U 0.9; } }
```
Mesh-robust across the whole family (DIAG, endTime 30000, rc 0): residuals settle at
L1 Ux 2.4e-14/p 4.1e-12, L2 6.5e-14/9.1e-12, L3 3.1e-9/1.5e-8. The lever is
convergence-robustness-justified; **no Δp deviation was read to choose it** (ARM_SELECTION §1).

## 11. Comparator and driver — AUTHORED AND FROZEN WITH THIS FILE

- **Comparator `grade_vmfl007_r3.py`** (drafted from `grade_vmfl064_r2.py`):
  planted-zero (single scalar into the exact endTime value, blind-reader refusal);
  functional-plateau + residual-settled convergence clause (§9); Roache triple + P_MIN
  floor with its planted control; SAME-precondition asserts (UmaxInlet 3.1429, QInlet
  mean 2 — flat slug refuses); viscosity-class asserts (nuMin/nuMax do not bind at
  endTime); zero-Courant steady check; strict completion (rule 4, FIXED-endTime
  variant: `last time == endTime`; L-342 field classes; age guard); numeric time-dir
  selection with a cardinality refusal (`one_or_refuse`); ρ named by derivation, not a
  bare literal; the SINGLE verdict path with ceiling `PASS`; `--verify-frozen`.
  **`--selftest` is 32/32 PASS and BYTE-IDENTICAL under `python3` and `python3 -O`;
  zero `ast.Assert` nodes.**
- **Driver `run_vmfl007_r3.sh`** (modelled on `run_vmfl064_r2.sh`): freeze-pin
  disk == HEAD for prereg + comparator + the 8 `case/` files, plus the 5 physics
  inputs re-hashed against the run-1 blobs; `--selftest` green + identical under both
  interpreters before a core-minute; age guard (rule 4); per-level caps → `rc 124`;
  rc captured INSIDE the detached subshell (setsid-returns-zero trap avoided);
  `FREEZE_COMMIT = git rev-parse HEAD`; mesh birth certificate per level.
- **A machine-readable `GRADING_VMFL007_R3.json`** is written by the comparator into
  the run root at grade time.

## 12. Cost

**Per-level caps (frozen): L1 2 / L2 7 / L3 40 core-min** (timeout_s = cap·60/RANKS,
RANKS 1 serial). An overrun STOPS that level (`rc 124`); endTime is NEVER shrunk to
fit (rule 12). Estimate from the DIAG runs (serial): L1 ~0.9, L2 ~3, L3 ~16–30
core-min → total **~20–34 core-min expected, cap 49**. **$ DERIVED:** ~30 core-min =
0.5 core-h × $0.0513/core-h = **$0.026 DERIVED**; at the 49-core-min cap, **$0.042
DERIVED**. Rate owner-stated (the box cannot read its own billing); dollars derived,
never measured. A COST_CALIBRATION row is owed at graded completion, not now.

## 13. Run root and paths

- **Run root (fresh):** `verification/runs/ansys_verification/VMFL007-R3/` — the
  age guard (rule 4) refuses any level path holding `0/` or a numeric time dir.
  The DIAG tree (`…/VMFL007-R3-DIAG/`) is a separate diagnostic tree, not a graded
  artifact, and is not written by the graded run.
- endTime 60000, writeInterval 20000 (a field time dir lands at 60000 for the age guard).
- Neither VM2026R1 archive copy is written, moved or deleted by any run.

## 14. Honest caveats (mandatory, prominent)

- **The L3 (100×100) FIELD carries a persistent single-cell entry-region `max(nu)`
  limit cycle (N-AV15, measured to 90 000 iterations — no decay).** It does NOT
  perturb the gate functional beyond ~1.45e-3 Pa (2.4e-8 relative, ~200,000× below
  the 302.6 Pa band half-width; the L3 Δp mean is stable 60517.068 @30k vs 60517.072
  @90k). **Mechanism undiagnosed** (physical entry adjustment vs wedge-axis artifact);
  **untested at 200×200**; **unknown if SIMPLEC-specific** (the SIMPLE arm cannot
  reach L3). This is a **limit-cycle CAVEAT, NOT the §2ay capability-gap terminal** —
  the case converges functionally at all three levels and yields a CONVERGING,
  non-pinned triple, so it IS gradeable.
- **If the graded finest Δp is out of band → `GATE FAIL` stands (no gate-fitting).**
  If any level diverges or fails strict completion at grade time → `NOT A RESULT`,
  and **no level is dropped** (L-500). If d21 or d32 collapses on the real triple →
  the comparator's pinning-refusal fires → `NOT A RESULT`.
- The pinning result (§5) and the DIAG triple were measured on the prior lane's B2
  DIAG monitors (logs cleaned; RUN_RC is the completion record). **The graded run must
  RE-DEMONSTRATE mesh-robust convergence under the frozen driver's strict-completion +
  age-guard; if it diverges at grade time, rule 4 catches it.** The DIAG values are
  NOT the verdict — the graded run produces it.

## 15. Supervisor ruling (2026-09-07) — recorded as given

> Both hard blockers cleared; freeze APPROVED. §2ay FIX accepted (single answer-blind
> lever SIMPLE→SIMPLEC; root cause verified sound). Pinning probe accepted
> (d21/ptp = 4.44e6 ≫ 100, planted control fired at ρ·δ). §12.2 SAME/PASS-capable
> confirmed at source (VERIFICATION_CHARTER §2h.8.1; precedent VMFL004-R2). Functional-
> plateau completion criterion approved (value-blind, threshold 1e-2 Pa referencing the
> noise floor; residuals settled not still-falling; planted control carried into the
> selftest). Honest caveats mandatory and prominent. Do NOT launch (blocked on the
> auto-mode permission classifier, Sanaa's desk).

**END OF FROZEN PRE-REGISTRATION.**
