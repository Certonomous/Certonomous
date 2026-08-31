# VMFL007-R3 — Non-Newtonian (power-law) Flow in a Pipe — PRE-REGISTRATION **DRAFT**

**STATUS: DRAFT — NOT FROZEN — ⛔ NOT READY TO FREEZE — FREEZE BLOCKED. THIS IS NOT THE FREEZE COMMIT.**

> **⛔ DO NOT FREEZE THIS REGISTRATION. The freeze is BLOCKED on the pinning
> probe, which was RUN and did NOT clear its pre-fixed decision rule.** A pinning
> probe (L1+L2, arm A5) executed 2026-08-31 (see `PINNING_PROBE_RESULT.md` beside
> this file): **L1 converged cleanly; L2 DIVERGED (SIGFPE) with arm A5, so no valid
> L2 Δp exists and d21/ptp COULD NOT be evaluated.** The pre-fixed rule
> (`d21/ptp ≥ 100`, fail-closed, the supervisor's, unchanged) is therefore
> **UNSATISFIED**, and the gate quantity's non-pinning is **ARGUED, NOT MEASURED.**
> A future lane must NOT read the `SAME` / `PASS`-capable ruling below as
> readiness: two independent blockers stand — (a) the pinning question is
> unmeasured, and (b) **arm A5 is not mesh-robust (converges at 25×25, diverges at
> 50×50)**, so no graded triple can run on it as configured. **Freezing requires
> BOTH: a solver arm proven stable across the whole family, AND a re-run probe that
> clears `d21/ptp ≥ 100`.** Neither exists yet.

Drafted by `ansys-lane-opus48` on 2026-08-31T22:26:34Z (UTC, `date -u`), HEAD at
draft time `f5d117c4`, at the direction of `ansys-verification-supervisor`. Updated
2026-08-31 with the supervisor's §12.2 ruling (§4), the executed pinning-probe
result (§5), and the `§2h.8.1` citation correction. **The file is a DRAFT, so these
are direct edits, not frozen-file amendments.** The freeze commit and any further
compute are the supervisor's — and both are stood down tonight by Sanaa's demo
priority. Nothing in the graded run has run; the diagnostic probe consumed **2.8
core-min** under an authorisation later withdrawn (the probe had already completed
when the withdrawal arrived); no gate is frozen.

**Cites:** register row #37 (VMFL007-R2, the single-grid solver/preconditioner
slate, `NOT A RESULT`) and row #8 (VMFL007 run 1). Re-grades neither; both stand.
This is a NEW registration under `ANSYS_VERIFICATION_CHARTER` §6, a fresh
three-level Roache triple that the R2 slate was explicitly built to enable.

---

## 1. What the supervisor must rule BEFORE this can be frozen

Per `ANSYS_VERIFICATION_CHARTER` §11.2 (v1.5, 2026-08-30) a registration may not
reach its freeze commit with an open gate question. Three items are the
supervisor's and are flagged in place below:

1. **§12.2 SAME/DIFFERENT (the crux — §4 below).** **RULED `SAME`, `PASS`-capable,
   by `ansys-verification-supervisor` 2026-08-31** (verbatim ruling folded into §4).
   The ruling stands. `DIFFERENT` is not the fallback — the condition is met.
2. **The conservation-identity / pinning proof-by-measurement (§5 below).** **STILL
   OPEN — this is the freeze blocker.** The pinning probe was RUN 2026-08-31 and did
   NOT clear the pre-fixed rule (`d21/ptp ≥ 100`): L2 DIVERGED with arm A5, so d21 is
   unmeasured. Δp non-pinning is ARGUED, not MEASURED. **A re-run probe on a
   mesh-robust solver arm is required before any freeze** (§5, `PINNING_PROBE_RESULT.md`).
3. **The solver arm (§10 below).** **A5 (PBiCGStab/DIC) is DISPROVEN as the graded
   arm** — it converges at 25×25 but diverges at 50×50 (probe, §5/§10). A mesh-robust
   configuration must be found and proven across the family before freeze.
---

## 2. Case identity and ground truth

- **Case:** VMFL007, Non-Newtonian Flow in a Pipe. **Manual page 29**, Release
  2026 R1 (title page verified against the PDF, CLAUDE.md rule 15).
- **Physics/Models (manual):** steady laminar flow, power law for viscosity.
- **Reference (manual):** W.F. Hughes & J.A. Brighton, *Schaum's Outline of Fluid
  Dynamics*, McGraw-Hill, 1991.
- **Material/geometry/BC (manual, p. 29 verbatim table):** density ρ = 1000 kg/m³;
  viscosity power law k = 10, n = 0.4; pipe length L = 0.1 m; pipe diameter
  D = 0.0025 m (R = 0.00125 m); **"Fully developed velocity profile at inlet with
  an average velocity of 2 m/s."**
- **Solver here:** OpenFOAM v2606 `simpleFoam` + `viscosityModels::powerLaw`
  (`k_OF = k/ρ = 0.01` kinematic, n = 0.4, nuMin 1e-8, nuMax 1.0), laminar
  `Stokes`, on a 2-D axisymmetric **1° wedge** (single cell thick).

**Physics inputs CARRIED BYTE-IDENTICAL from the VMFL007 run-1 freeze** (verified
on disk this invocation; these are the run-1 blobs the R2 launcher asserts):

| input | blob |
|---|---|
| `case/0/U` (coded fully-developed inlet, u_max = 3.142857, exponent 3.5) | `b626d65ada23d57c62337f1a26e411c1bdc3cd16` |
| `case/0/p` (kinematic p, outlet fixedValue 0) | `54562f8cbc730c083492ac97d21c9d7c214414a3` |
| `case/constant/transportProperties` (powerLaw k 0.01 n 0.4) | `db848a12eb939d1ac0ad81bedea135f536926f38` |
| `case/system/fvSchemes` (steadyState; div bounded Gauss linear; laplacian Gauss linear corrected — formal order 2) | `ad718abf3cdc834b17478c2c391affeba1dbf2b2` |
| `case/system/blockMeshDict.template` (1° wedge, wall at exact R) | `9ea967ebeedf20eb9428c7785abf966eadbf01a3` |

**Only three things differ from the R2 slate:** the mesh RESOLUTION per level (§7),
the `controlDict` (endTime / residualControl / functionObjects, §9), and the single
frozen `fvSolution` arm (§10). Everything that sets the physics is unchanged, so
"the mesh is the only variable across the triple" is a machine-checkable fact.

## 3. Reference result

The fully-developed power-law pipe pressure drop (Rabinowitsch–Mooney / Hughes-
Brighton), evaluated by the lab itself:

```
Δp = (2kL/R) · [ ((3n+1)/n) · (Ū/R) ]^n
   = (2·10·0.1/0.00125) · [ 5.5 · 1600 ]^0.4
   = 60 521.969383834... Pa   =  60.522 kPa
```

- **Reference value: Δp_exact = 60 521.969 Pa.** Matches the manual's printed
  target **60.52 kPa** and the register's stated closed form (row #8/#37).
- **The manual prints four figures (60.52 kPa)**, so the printed target is known
  only to ± 5 Pa = **± 0.00826 %** (rounding half-width). Context, never the gate:
  Fluent 60.41 kPa (ratio 0.998), CFX 61.52 kPa (ratio 1.0165). This box has no
  Fluent and no CFX; nothing here is a statement about Ansys.
- **Reference kind: closed-form / exact.** Whether it is exact for the SAME model
  the solver discretises is §4 — and PASS-capability turns entirely on it.

## 4. §12.2 — SAME or DIFFERENT — argued adversarially against this lane

Declared per `ANSYS_VERIFICATION_CHARTER` §12.2 (v1.6, 2026-08-31), four points on
the face of the registration before the freeze:

**(1) The continuum model the solver discretises for this case.** The full steady
incompressible Navier–Stokes system with a generalized-Newtonian (power-law)
viscosity, in the meshed axisymmetric wedge:
```
∇·u = 0
ρ (u·∇)u = −∇p + ∇·( 2 μ(γ̇) S ),   μ(γ̇) = k γ̇^(n−1),  S = ½(∇u+∇uᵀ)
```
elliptic, non-linear (shear-thinning, n = 0.4), 2-D axisymmetric.

**(2) The model the manual's reference is the exact solution of.** The
**fully-developed, axisymmetric, unidirectional, steady** reduction
```
(1/r) d/dr( r · k (du/dr)^n ) = dp/dx = const,   u = u_z(r) ê_z,  ∂/∂z = 0
```
a one-dimensional ODE in r. The Hughes-Brighton closed form is its exact integral.

**(3) SAME or DIFFERENT — RECOMMENDED: `SAME`, and here is the adversarial case for
and against.**

The reduction in (2) drops the convective term (u·∇)u and the axial derivatives.
**The decisive question (the VMFL029 trap): is the closed form the exact solution
of the system in (1), or of a genuinely REDUCED system that our elliptic solver
only APPROACHES?**

- **The convective term vanishes IDENTICALLY, not approximately, for the symmetric
  solution.** With u = u_z(r) ê_z and ∂u_z/∂z = 0, (u·∇)u = u_z ∂u_z/∂z ê_z ≡ 0,
  the r- and θ-momentum give ∂p/∂r = ∂p/∂θ = 0. So the exact steady solution of the
  FULL system (1), under a fully-developed axisymmetric inlet and a developed
  outlet, **IS** the profile in (2). The dropped terms are exactly zero on that
  solution, not small. This is the opposite of the VMFL029 trap, where the closed
  form solved a rank-one non-elliptic reduction whose solution genuinely differs
  from the full system; here full = reduced **exactly**.
- **The load-bearing precondition, stated so it can be attacked: this holds ONLY
  because the manual specifies — and the frozen `0/U` imposes — a FULLY-DEVELOPED
  inlet profile.** If the inlet were a flat 2 m/s slug, there would be a developing
  entrance region where (u·∇)u ≠ 0, the total inlet-to-outlet Δp would carry an
  entrance loss the closed form does not model, and the honest answer would be
  `DIFFERENT`. This is not hypothetical: the generalized (Metzner-Reed) Reynolds
  number is **Re = 84.6**, giving a laminar entrance length ≈ 0.05·Re·D ≈
  **0.0106 m ≈ 10.6 % of the 0.1 m pipe** — a flat inlet would contaminate the
  gate by ~10 % of the domain. **The frozen `0/U` (blob `b626d65a`) is a
  `codedFixedValue` imposing u(r) = u_max·(1−(r/R)^3.5), u_max = 3.142857 m/s, mean
  2 m/s** — the exact developed profile. `SAME` stands or falls on this one input,
  and it is frozen and asserted.
- **The wedge is a faithful axisymmetric representation, not a model reduction.**
  A 1° `wedge` with proper `wedge` patches enforces axisymmetry; its continuum
  solution is the axisymmetric pipe solution, save an azimuthal GEOMETRIC bias
  (§8), which is a disclosed error-budget term, not a different PDE. The continuum
  model is unchanged.

**Adversarial residue that I cannot dismiss and hand to the supervisor:** `SAME`
depends on the *outlet* not inducing a development/recirculation that reintroduces
a convective term, and on the imposed *continuous* inlet profile being sustained by
the discrete interior rather than relaxing over the first cells into a mildly
developing region. Physically both are negligible here (short pipe, developed
inlet, no adverse gradient), but they are the seam where `SAME` could fail, and
they are the reason the pinning/convergence controls (§5, §9) are not optional.

**(4) The five §2h.4 conditions, declared and discharged** — required by
`ANSYS_VERIFICATION_CHARTER` §12.2 point 4 whenever `SAME`/`PASS` is sought.
Conditions cited as `VERIFICATION_CHARTER §2h.4 (v1.17, 2026-08-27, the five
floor-demonstration conditions)` and the ceiling rule as `VERIFICATION_CHARTER
§2h.8.1 (v1.28, 2026-08-31, the exact-PDE rule)` — the §12.3 (v1.6, 2026-08-31)
citation form; a bare `§2h.6` is banned in this territory.

> **CITATION CORRECTED PRE-FREEZE, SUBSTANCE UNMOVED.** An earlier draft cited the
> exact-PDE rule as `§2h.6.1 (v1.27)`. That address is superseded: `VERIFICATION_CHARTER`
> v1.28 (2026-08-31, `§2h.8`) renumbered the exact-PDE rule `§2h.6.1`→`§2h.8.1` with
> **its words unchanged**, because `§2h.6` denotes non-retroactivity alone and a bare
> `§2h.6` would name two rules, one of which defeats the claim. Verified at source
> (`VERIFICATION_CHARTER` lines 3750, 3756–3759, 3791). `§2h.4`'s address was **not**
> renumbered (still `§2h.4`, v1.17). The file is a DRAFT, so this is a direct edit.

1. **Reference is the exact solution of the SAME continuum model.** Argued in (3):
   YES conditional on the frozen developed-inlet BC. This is the load-bearing
   condition and it is the one the supervisor rules.
2. **Iterative error separately gated by rule 5 limb (1), one-way.** Discharged by
   §9's convergence clause: each level whose functional Δp has not plateaued (or
   whose residuals have not fallen) is `NOT A RESULT` regardless of its value, via a
   single verdict-writing path that cannot turn `NOT A RESULT` into `PASS`.
3. **Round-off stated with its magnitude, negligible against the band.** Δp ≈
   6.05e4 Pa in IEEE double (≈ 1e-15 relative) carries round-off ≈ **6e-11 Pa**,
   which is **~5e9× smaller** than the band half-width (§6, ≈ 302 Pa). Stated as a
   number, not an assurance.
4. **The registration's wording makes no over-reaching continuum claim.** Because
   this registration DECLARES A CONVERGING TRIPLE, the PASS is a continuum claim
   **bounded by the GCI** — which is exactly the instrument §2h.4 condition 5 says a
   no-triple floor demonstration lacks. The registered verdict sentence reads: *"the
   finest-level Δp agrees with the reference inside the band, and the GCI at Fs=1.25
   bounds the discretisation uncertainty at Y %"* — a discretisation-error statement,
   never *"Δp is correct to X."*
5. **The claim is bounded by the levels actually run.** The triple establishes
   behaviour across the three meshes run and quotes a GCI for the finest; it claims
   nothing about meshes not run. (For a triple this is satisfied a fortiori — the
   triple is the across-mesh instrument the floor demo lacks.)

**PASS path (the supervisor RULED `SAME`):** `§2h.8.1` makes the reference
`PASS`-capable (not capped at `GATE REACHED`); the triple returns `CONVERGING`
(rule 5 step 3); `PASS` iff the finest Δp is inside §6's band. This is the exact
route register row #28 (VMFL004-R2) took to a landed `PASS`. **This lane did NOT
manufacture PASS-capability; it argued `SAME` and handed the ruling up.**

### §12.2 RULING — `SAME`, `PASS`-capable — `ansys-verification-supervisor`, 2026-08-31 (dated ruling line on a DRAFT, folded in at the supervisor's instruction; this is NOT the freeze)

> Ruling, recorded as given by the supervisor: **§12.2 = `SAME`, `PASS`-capable**,
> cited `VERIFICATION_CHARTER §2h.8.1 (v1.28, 2026-08-31, the exact-PDE rule)`. The
> supervisor read the frozen `0/U` (blob `b626d65a`) at source: the inlet is a
> `codedFixedValue` imposing u(r) = u_max(1−(r/R)^3.5), u_max = 3.142857 — the exact
> fully-developed Rabinowitsch-Mooney profile the manual's p.29 BC specifies. On that
> BC the flow is unidirectional and x-invariant, so **(u·∇)u vanishes IDENTICALLY —
> not as a small parameter** — and the full incompressible power-law NS momentum
> equation the solver discretises reduces **EXACTLY** to the 1-D ODE
> `0 = −dp/dx + (1/r)d/dr(r·τ)` that the closed form solves. **Full model = reduced
> model exactly. This is NOT the VMFL029 trap** (there the closed form solved a
> structurally different rank-one non-elliptic PDE and ellipticity was not a small
> parameter; here the two models coincide because the convective term is identically
> zero under the imposed developed inlet). **The determination rests entirely on that
> one frozen input** — a flat inlet would be `DIFFERENT`. `DIFFERENT` is not the
> fallback because the condition is met; the `GATE REACHED` fallback would stand only
> if the pinning probe (§5) fails.
>
> **STATUS OF THE ONLY REMAINING CONDITION:** `§2h.8.1`'s `PASS`-capability requires
> `§2h.4`'s five conditions **and** — per this team's practice — a gradeable
> (non-pinned, converging) triple. Condition 1 (SAME) is now RULED. **But the
> registration is NOT thereby freezable:** the gradeability of the triple is exactly
> what the §5 pinning probe was to establish, and that probe DID NOT clear its rule
> (§5). **A `SAME` ruling does not make a pinned-or-undiagnosed gate gradeable.**

## 5. Gate quantity and the conservation-identity / pinning analysis

**Candidate gate quantity: Δp_Pa = ρ · ( ⟨p⟩_inlet − ⟨p⟩_outlet )**, ρ = 1000, p
kinematic, area-averaged on each end patch (the frozen `pInlet`/`pOutlet`
`surfaceFieldValue` objects, `writeFields false`).

**Is Δp pinned by a conservation identity — structurally EXACT on every mesh?**
This is the trap that killed VMFL038 (τ_w = (dp/L)·δ pinned to gravity, exact to
3.62e-13 on every mesh) and VMFL029 (net wall heat flux at the solver floor), and
that made VMFL003-M2's f_dev bit-identical between levels. **Argued NOT pinned:**

- The DRIVING quantity here is **not imposed**. VMFL038 imposed the body force
  (gravity) and global balance pinned τ_w to it. Here the imposed quantity is the
  **flow rate** (via the fixed developed inlet profile); the pressure gradient
  dp/dx is the solver's OUTPUT, free to carry discretisation error.
- dp/dx is set by the near-wall shear: from the fully-developed balance
  dp/dx·(πR²) = τ_w·(2πR), so dp/dx = 2τ_w/R, and τ_w = k(du/dr|_w)^n depends on
  the **radially-resolved** wall gradient. As the radial mesh refines the wall
  gradient sharpens toward the exact steep (exponent-3.5) profile, so τ_w — and Δp
  — **move at the scheme order**. This is a radial-resolution quantity, unlike
  f_dev (built from axial slabs, which carry no information in fully-developed
  flow).
- The isotropic triple (§7) refines radially as well as axially, so the radial
  wall-gradient error is reduced level to level and Δp changes. **The axial
  refinement carries little/no information for a fully-developed flow (a known
  feature, not a bug), so p_obs will reflect the radial convergence** — this is
  disclosed, and it is precisely NOT the f_dev pinning because the GATE carries the
  radial information the diagnostic lacked.

**⛔ THE PINNING PROBE WAS RUN 2026-08-31 AND DID NOT CLEAR ITS RULE — THE FREEZE IS
BLOCKED.** Full record beside this file: `PINNING_PROBE_RESULT.md`. The supervisor
authorised a two-level diagnostic probe (L1 25×25, L2 50×50, arm A5, scratch OUTSIDE
the runs tree, cap 3 core-min) with the decision rule **fixed in advance and
fail-closed: `d21/ptp ≥ 100` → not pinned → proceed; `< 100` → pinned → do not
freeze.** Measured:

- **L1 (25×25, A5): CONVERGED.** Δp = **60 437.9488 Pa**, plateau peak-to-peak
  **0.0000 Pa** (bit-flat over the last 6000 of 30000 iterations); dev −0.1388 % from
  the reference — inside §6's band already at the coarsest level.
- **L2 (50×50, A5): DIVERGED.** SIGFPE / core dump at iteration ≈ 13 275; the U
  residual was rising (≈ 0.07 and climbing) and Δp blew up to ≈ 1e308 (garbage).
  **No valid L2 Δp exists.**

**Consequence: `d21 = |Δp(L2)−Δp(L1)|` is UNMEASURED** — L2 produced no converged
value — **so `d21/ptp` cannot be evaluated and the rule is UNSATISFIED. Fail-closed:
DO NOT FREEZE.** Two distinct blockers now stand, and both must be cleared before any
freeze:

1. **The pinning question is STILL OPEN.** Δp non-pinning is ARGUED (above; L1's
   clean converged value is consistent with it and refutes nothing) but **NOT
   MEASURED** — no d21 exists. The pre-fixed `d21/ptp ≥ 100` rule stands, unexecuted
   to a valid result, and must be re-run to a PASS on a solver that survives L2.
2. **Arm A5 is NOT mesh-robust.** It converged at 25×25 and diverged at 50×50, so
   **no graded triple can run on A5 as configured.** A mesh-robust configuration must
   be found and proven across all three levels FIRST — likely tighter relaxation
   (U 0.7 → lower; p already 0.3), a Krylov U solver (PBiCGStab for U rather than
   `smoothSolver`), and/or SIMPLEC (`consistent yes`). **This is a solver-robustness
   investigation the single-grid R2 slate could not have surfaced** — it is the same
   "cause class is not repair class" pattern as VMFL007 itself.

**The fail-closed pinning-refusal in the comparator (§11) stays regardless** — belt
and suspenders: even a future probe that clears the rule does not exempt the graded
comparator from refusing if d21 collapses on the real triple.

**Standing anchors for the re-run rule** (the supervisor's, unchanged): VMFL021-R2
measured ≈ 300× and was sound; VMFL003-M2 measured d21 = 0 exactly and was pinned;
the 100× threshold is fixed and is not adjusted to fit any probe return.

## 6. Gate and tolerance

- **Gate:** `|Δp_lab − 60520| / 60520 ≤ 0.005` (0.5 % relative) at the finest level
  L3, **AND** a `CONVERGING` Roache triple on Δp (rule 5).
- **Band: [60217.40, 60822.60] Pa**, i.e. the manual's printed 60.52 kPa = 60520 Pa
  ± 0.5 %. **CARRIED BYTE-IDENTICAL from VMFL007 run-1's freeze** (the same band the
  R2 slate carried, never re-justified from any number). The exact closed form
  60521.969 Pa lies inside it. **A gate frozen before run 1 and carried unchanged
  cannot have been shaped by any answer** — the freeze's evidentiary content.
- **Tolerance justification (from the manual's agreement class, not a run):** the
  reference is exact; the band is limited by our discretisation, not the reference
  (whose own rounding is ±0.00826 %). 0.5 % is comfortably above the disclosed
  wedge bias (+0.0038 %) and the reference rounding, and is the run-1 class.
- **Ceiling:** `PASS` if the supervisor rules `SAME` (§4); `GATE REACHED`
  hard-coded if `DIFFERENT`. The comparator must be able to print only the ruled
  ceiling.

## 7. Mesh family — isotropic Roache triple

- **Refinement r = 2, isotropic, cells ×4 per level, constant aspect ratio.** Both
  NX and NR double each level, so Δx and Δr both halve and Δx/Δr is constant (= 80).
  Laminar, no wall function, so N-AV10's axial-only constraint does not apply and
  refinement is radial as well as axial (the frozen `blockMeshDict.template` says so).

| level | NX × NR | cells | Δr at wall (m) |
|---|---|---|---|
| L1 | 25 × 25 | 625 | 5.00e-5 |
| L2 | 50 × 50 | 2 500 | 2.50e-5 |
| L3 | 100 × 100 | 10 000 | 1.25e-5 |

- GCI at **Fs = 1.25**, quoted beside a `PASS`/`GATE FAIL` only when the three Δp
  values are monotone; never otherwise.
- **Observed-order floor `P_MIN` beside the GCI** (team standing requirement): a
  `P_MIN` (e.g. 0.05, to be fixed in the frozen comparator) below which no GCI is
  quoted; the value is still printed with the triple class.
- **Note for the supervisor's probe (§5.1):** confirm L1 (25 radial cells) is in the
  asymptotic range (monotone, difference ratio ≈ 4); if not, shift the family finer
  (e.g. 40/80/160) before freezing. This lane cannot measure it.

## 8. Error budget (with signs)

- **Wedge azimuthal geometric bias (Clause A, `ANSYS_VERIFICATION_CHARTER` v1.4;
  N-AV9):** at t = 1°, the pressure-drop bias is `sec(t/2) − 1 = +0.003808 %` — Δp
  biased **HIGH**. **NO grid refinement removes it** (azimuthal); it is invisible to
  the triple and the GCI, so it is stated here with its sign as required. It is
  11.5× smaller than the 5° wedge and sits below the reference's own ±0.00826 %
  rounding — the deliberate criterion behind the 1° choice.
- **Sign consequence:** the wedge makes our Δp read HIGH. If the discretisation also
  reads high on the coarse mesh, the two add; if the discretisation reads low
  (under-resolved wall gradient, the usual laminar case) they partly cancel. The
  coarse-mesh sign is genuinely unknown from the unconverged single-grid slate and
  the triple will establish it — do not assume it.
- **Reference rounding:** manual target ±0.00826 %.
- **Round-off:** ≈ 6e-11 Pa (§4 condition 3), negligible.

## 9. Convergence clause (L-413) — and the A3/A5 warning that makes it load-bearing

**The warning, measured, from the R2 slate (row #37):** on the SAME single 25×25
grid, arm A3 (PCG/DIC) reported last pInlet 71.9 and A5 (PBiCGStab/DIC) 63.3
(kinematic; ×ρ → ~71 900 vs ~63 300 Pa). **Two consistent linear solvers on the
same discretisation must converge to the SAME discrete Δp; a ~12 % spread proves at
least one had NOT reached functional convergence at endTime 10000.** The strongly
shear-thinning (n = 0.4) momentum equation converges its FUNCTIONAL far more slowly
than a naive residual read suggests. **Therefore the convergence gate must be on the
FUNCTIONAL Δp, not on the linear residual alone.**

**Clause (satisfiable from converged-flat-at-machine-floor to still-descending,
L-413):**

- Add `residualControl` on `p` and `U` (recommend 1e-7) to `controlDict`/`fvSolution`
  so a level stops when converged, with a generous `endTime` ceiling as a safety cap
  (recommend endTime 60000; the fully-developed geometry should converge well
  inside it).
- **Functional plateau on Δp over a FIXED (absolute-iteration) window**, not a
  fraction-of-run window (per `MONITOR_STANDARD` S13's finding that a fraction-of-run
  window loosens as a run is extended): the level is `plateaued` iff the
  peak-to-peak of Δp over the last W iterations (W fixed, e.g. 2000) is below a
  fraction (e.g. 1e-4) of Δp's own converged magnitude. **Still-descending →
  NOT plateaued → `NOT A RESULT`.** This is what would have caught the A3/A5 spread.
- The clause fires per level, BEFORE the triple is classified (rule 5 limb 1,
  one-way).

**W, the plateau fraction and `residualControl` values are frozen in the
comparator; the numbers above are recommendations for the supervisor to fix at the
freeze.**

## 10. Solver arm — A5 DISPROVEN by the probe; a mesh-robust arm must be found first

**⛔ A5 (PBiCGStab/DIC) is DISPROVEN as the graded arm.** The §5 probe measured it:
A5 converged at 25×25 (L1) but **DIVERGED (SIGFPE) at 50×50 (L2)**. A single-grid
survivor is not a mesh-robust solver, and the R2 slate — being single-grid — could
not have shown this. **No graded triple can be frozen on A5 as configured.**

*(Superseded recommendation, kept for the record:* A5 was recommended pre-probe as
the more robust of the R2 slate's two single-grid survivors (A3 71.9, A5 63.3;
A1/A2/A4/A6 diverged to 1e+135–1e+161). The probe overturned it.*)*

**What a mesh-robust arm probably needs** (a solver-robustness investigation, the
supervisor's to scope; NOT decided here): tighter under-relaxation (U 0.7 → e.g.
0.5; p already 0.3), a Krylov U solver (`PBiCGStab`/`DIC` for U rather than
`smoothSolver`/`symGaussSeidel`), and/or SIMPLEC (`consistent yes`). Any candidate
must be proven to converge on **all three** levels (25/50/100) before it can be the
frozen arm — that proof is itself the first thing a resumed VMFL007-R3 effort does.

**The 12 % A3/A5 disagreement is itself the argument for the §9 clause:** if two
DIC arms still disagree beyond the plateau tolerance on any graded level, one is not
converged and the convergence clause MUST return `NOT A RESULT` for that level. A
truly converged triple gives the same Δp under A3 or A5.

## 11. Comparator and launcher requirements (to be written and frozen WITH this file)

The grader (`grade_vmfl007_r3.py`) and launcher (`run_vmfl007_r3.sh`) are drafted
from the team's triple-grader idiom (e.g. `grade_vmfl064_r2.py`) and must carry, all
frozen with this registration and verified against their blobs at launch:

- **Planted-zero control at EVERY level, running BEFORE any refusing clause**
  (rule 3): plant a known scalar δ into the `pInlet` (or `pOutlet`)
  `surfaceFieldValue.dat` value read from disk, re-read, and confirm Δp moved by
  ρ·δ; REFUSE (exit 2) if the reader cannot see it. Single scalar plant into a
  single scalar reader — **no averaging dilution** (contrast VMFL011's RMS, L-340),
  and the plant lands on the exact value the reader consumes (contrast VMFL011-R2's
  apex-row miss, L-340). Bounds checked as VMFL064-R2 did.
- **Pinning-refusal clause** (§5.2): `NOT A RESULT` if d21 or d32 ≤ the per-level
  plateau noise floor (structurally EXACT → rule 5 limb 2), triple and orders
  printed beside it.
- **Numeric time-directory selection with a cardinality refusal:** select the
  endTime directory by numeric maximum; refuse if the candidate set is ambiguous.
- **Zero `assert` under an AST guard**, with a planted control proving the guard can
  see a forbidden name.
- **`--selftest` green under `python3` AND `python3 -O`**, with every verdict path
  reachable; `--verify-frozen <sha>` rc 0.
- **A machine-readable JSON grading record** (`GRADING_VMFL007_R3.json`) frozen with
  the comparator.
- **Coefficient / viscosity-class asserts** carried from the R2 launcher (k 0.01,
  n 0.4, nuMin/nuMax never bind, `Stokes` laminar, `generalizedNewtonian` NOT
  selected — the wrong `powerLaw` class silently reads nu0 and gives ~3819 Pa).
- **Inlet-profile asserts** carried: `QInlet` (mean 2 m/s) and `UmaxInlet` (peak
  3.1429, proves the shape is the developed profile, not a flat slug — the §4 `SAME`
  precondition, machine-checked at run time).
- **Strict completion (rule 4)** at every level: rc 0; one `End`; last time ==
  that level's endTime (or the residualControl stop); fields present;
  `ExecutionTime` count consistent; age guard (every field newer than `0/U`).
- **EXACT-collapse guard:** the pinning-refusal above is the rule-5-limb-2 instrument.
- **Freeze naming (rule 2):** `--prereg-sha` mandatory; launcher verifies the on-disk
  comparator and registration equal their blobs at that commit before any solver.

## 12. Cost

**Estimate (bracketed — convergence rate is the uncertainty, per §9):** the R2
slate ran 25×25 to endTime 10000 at ~92 wall-s/arm. With `residualControl` the
graded levels should converge in a few thousand iterations; scaling by cells:

| level | cells | est. wall-s | est. core-min (serial) |
|---|---|---|---|
| L1 | 625 | ~150 | ~2.5 |
| L2 | 2 500 | ~600 | ~10 |
| L3 | 10 000 | ~2 400 | ~40 |
| **triple** | | | **~50 core-min (bracket 30–90)** |

- **Cap: 120 core-min total** (per-level caps e.g. 20/40/90); an overrun STOPS the
  run and does not get a new budget (rule 12).
- **$ DERIVED:** ~50 core-min = 0.833 core-h × $0.0513/core-h = **$0.043 DERIVED**;
  at the 120-core-min cap, **$0.103 DERIVED**. Both far under the $25 blanket. The
  rate is owner-stated, not measured (the box cannot read its own billing); dollars
  are derived, never measured.
- **cost_basis:** c7a.4xlarge $0.0513/core-h, RANKS = 1 (serial).

## 13. Run root and paths

- **Run root (fresh, confirmed ABSENT this invocation):**
  `verification/runs/ansys_verification/VMFL007-R3/` — the age guard (rule 4)
  refuses any path holding a `0/` or numeric time dir, and VMFL007_R2's tree exists,
  so a fresh path is mandatory. `cases/ansys_verification/VMFL007-R3/`,
  `.../VMFL007_R3`, and `verification/runs/.../VMFL007_R3` are all absent too.
- Neither VM2026R1 archive copy is written, moved or deleted by any run.

## 14. Status of each open item (updated 2026-08-31 after the probe and the stand-down)

1. **§12.2 SAME/DIFFERENT** — **RULED `SAME`, `PASS`-capable** by the supervisor (§4).
   Closed.
2. **The pinning proof-by-measurement** — **⛔ OPEN, THE FREEZE BLOCKER.** The probe
   ran and did NOT clear `d21/ptp ≥ 100` (L2 diverged, d21 unmeasured; §5). Must be
   re-run on a mesh-robust arm.
3. **The solver arm** — **⛔ OPEN. A5 DISPROVEN** (diverges at L2; §10). A mesh-robust
   arm must be found and proven across all three levels first.
4. **The frozen numeric constants** — `residualControl`, the plateau window W and
   fraction, `P_MIN`, GCI ceiling, per-level caps — still to be fixed at freeze.
5. **The freeze commit and any further compute** — the supervisor's, and **stood down
   tonight** by Sanaa's demo priority.

**⛔ NET: NOT READY TO FREEZE. Two hard blockers (items 2 and 3) stand. A resumed
effort starts by finding a solver arm that converges on 25/50/100, then re-runs the
pinning probe to a `d21/ptp ≥ 100` PASS. Only then do items 4–5 arise.**

**END OF DRAFT — NOT FROZEN — NOT READY TO FREEZE.**
