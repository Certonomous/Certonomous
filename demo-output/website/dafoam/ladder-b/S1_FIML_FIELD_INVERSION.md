# Roadmap 4A Stage 1 — FIML field inversion: capability established and FD-verified, target case blocked

Date: 2026-07-31 (UTC). Host idle at launch (`uptime` load 0.14 at 10:18:46Z, 16 vCPU / 30 GiB).
All runs `dafoam/opt-packages:latest` (DAFoam v5.0.0, OpenFOAM v2506), 4 MPI ranks, at the
campaign cap. Working copies under `/home/ubuntu/certonomous-runs/S1-fiml/`; logs and scripts
retained under `S1_work/`.

Stage 1 as originally written: "FIML field inversion (beta on SST omega-destruction) via DAFoam
adjoint, FD-verified; first target NASA hump."

**Stage 1 as it now reads, restated 2026-08-01 under supervisor ruling R6:** *FIML field inversion
of a per-cell beta field on the SST omega-equation PRODUCTION term, via DAFoam's discrete adjoint,
FD-verified; first target NASA hump.*

**Why the goal statement moved, and what it does not do.** DAFoam exposes
`betaFIOmega_` on the omega equation's production term (`DAkOmegaSST.C:743`). The destruction
term's `beta` is the F1-blended model constant and carries no field hook, so the original wording
named something this stack cannot build. The restatement says what can actually be built. **It is
NOT a claim that the two are equivalent** — section 2 below shows they are not, because the other
omega terms do not scale with beta — and the production version therefore does not inherit the
destruction version's goal, its literature match, or its expected result. The destruction-term
variant is a separate item requiring a model patch and a rebuild, filed to the docket as
`w3-beta-on-omega-destruction-model-patch`.

**What this costs the Ladder B reproduction.** Wu, Zhang and Zhang invert on the destruction term.
A production-term inversion is therefore no longer a like-for-like reproduction of that paper, and
any score it produces must not be compared to theirs as though it were. That is a real reduction
in what Stage 1 can claim, and it is the honest one: building the production version and calling
it the roadmap item would have been the quieter and worse choice.

---

## Headline, in the order the evidence forces

1. **The mesh warp is genuinely absent from the field-inversion chain — measured, not reasoned.**
   The defect that FAILS A1 and A5 (`mesh.warpDeriv` mis-linearization) cannot reach a beta
   gradient, because the warping component is never constructed at all.
2. **No custom turbulence library is needed. B3's central disclosure is retracted.** DAFoam v5
   ships the beta hooks natively inside its own SST model. B3 substituted inlet velocity for
   beta on the stated grounds that the real design variable required a library that "is not
   distributed anywhere in the public benchmark clone". That substitution was never necessary.
3. **Disclosed deviation from the roadmap text: DAFoam's beta multiplies the omega equation's
   PRODUCTION term, not the destruction term.** The roadmap says "beta on SST omega-destruction".
   The destruction term carries no beta hook in this code.
4. **The field-inversion adjoint works, converges, and is FD-verified** on a 5,000-cell case with
   5,000 design variables: 2.67% against the real objective direction, step-independent and
   convergence-independent, no sign flip on any component the finite difference can resolve.
5. **The NASA hump target is BLOCKED, and memory is not why.** The adjoint returns PETSc
   `KSPConvergedReason = -9` (`DIVERGED_NANORINF`) at GMRES iteration 0, the identical signature
   B3 hit on CBFS, while peak memory left 18.99 GB free. Four mechanisms tested: three refuted,
   one changed the failure signature without producing convergence.

---

## 1. The warp question, settled by direct measurement

The brief asked this to be verified rather than accepted. It was, three ways, and the answer is
stronger than "the warp is not used": **the warping component is never instantiated.**

DAFoam's own official field-inversion tutorial builds its model with `mesh_options=None`, adds no
mesh subsystem, and makes no `x_aero` connection. Shape optimization scripts in this lab all do
the opposite (`get_mesh_coordinate_subsystem()` plus `connect("mesh.x_aero0", ...)`).

A counter was monkeypatched onto both `DAFoamWarper.__init__` and
`DAFoamWarper.compute_jacvec_product` — the latter being the exact function `PROOF.md` sections 15
to 22 traced the A1 and A5 defects into. On every field-inversion adjoint solve that ran to
completion this session (E1, E2 and E2-tight in section 3), the probe printed:

```
WARP PROBE: {"warper_init": 0, "warper_jacvec": 0}
```

Zero constructions, zero calls. `warper_init: 0` is the decisive number: a class that is never
instantiated cannot have a method called on it, so this is not "the warp was called with a zero
seed", it is "the warp is not in the model". Stated precisely: the hump runs in section 4 build
their model identically (`mesh_options=None`, no mesh subsystem) but failed before the probe
printed, so the direct measurement above is from the tutorial case.

**Consequence, stated plainly: FIML is reachable on a code path where shape optimization in this
lab is not.** The upstream `mesh.warpDeriv` bug that produces sign-flipped shape gradients on A1
and A5, and which `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` documents, has no route into a beta
gradient. That is a real, independent result and it holds regardless of everything below.

## 2. What field inversion on this stack actually requires

Read directly from the installed source, not from documentation.

| Requirement | What the install provides |
|---|---|
| beta field on SST | `betaFIOmega_` and `betaFIK_` are members of `DAkOmegaSST`, constructed `READ_IF_PRESENT` with default 1.0 |
| beta as a design variable | `DAInputField` (`TypeName("field")`), keyed by `fieldName`/`fieldType` |
| restricting beta to a region | `DAInputField` accepts an optional `cellSetName`, so the DV count need not equal the cell count |
| loss against reference data | `DAFunctionVariance`, modes `field` / `surface` / `probePoint`; supports `wallShearStress` as a target |
| worked example | an official steady field-inversion tutorial shipping `betaFIOmega` reference data |

**The design-variable count is one per cell** (or one per selected cell with `cellSetName`):
5,000 on the tutorial case, 51,626 on the hump.

**This is the point B3 got wrong, and it matters** because it is the stated reason Ladder B never
attempted the real inversion. `DAkOmegaSST` is DAFoam's own SST implementation and the beta hooks
are compiled into it.

### The deviation that must be disclosed

The roadmap specifies beta on the **omega destruction** term. In `DAkOmegaSST.C` the omega
equation reads (abridged):

```
== phase_() * rho() * gamma * GbyNu(GbyNu0, F23(), S2()) * betaFIOmega_()   <- PRODUCTION, beta here
    - fvm::Sp(phase_() * rho() * beta * omega_(), omega_)                    <- DESTRUCTION, no beta hook
```

`betaFIOmega_` multiplies production. The destruction term's `beta` is the SST model constant
blended by F1, not a field. The two are not equivalent: scaling production by beta and scaling
destruction by 1/beta give different equations because the other omega terms do not scale with
them. Anything built on this hook is a production-term inversion and should be recorded as such,
or the model must be patched and rebuilt.

## 3. Capability and FD verification, on a case that works

Official steady field-inversion tutorial, 5,000 cells, one beta per cell, `DASimpleFoam`, 4 ranks.
Reference data generated by the tutorial's own preprocessing (an SST primal, converged to
9.939e-09 at iteration 1355). Objective reduced to a single field-variance term so the adjoint
seed is one unambiguous quantity; the tutorial's neural-network parameterization was deactivated
so the design variable is the raw beta field.

| Run | model | GMRES | reason | primal | adjoint | objective |
|---|---|---|---|---|---|---|
| E1 | kOmega | 80 iters | **2 (converged)** | 7.815 s | 10.933 s | 9.2484596382675626e-03 |
| E2 | **kOmegaSST** | 91 iters | **2 (converged)** | 8.323 s | 11.947 s | 1.3816040076915038e-02 |
| E2-tight | kOmegaSST | 91 iters | **2 (converged)** | 12.818 s | 5.753 s | 1.3816066996509691e-02 |

E2 is the case that matters: **the SST field-inversion adjoint converges.** B3's `-9` blocker is
therefore not a property of the SST adjoint as such, which is the discriminator
`B3_supervisor_debug.md` names as open and records four failed attempts to land.

### Finite-difference verification

A `check_totals` over 5,000 design variables would need 10,000 primal re-solves. Verification was
done instead by central differences in **fresh processes** (eliminating warm-start path dependence,
the artifact A5's record found worth 1.05e-5), at two step sizes, with a reproducibility control
and both a real-objective and a random direction.

**Reproducibility control:** two identical fresh runs gave
`1.3816040076915038e-02` and `1.3816040076915038e-02` — **bit-identical, difference exactly 0**.

**Directional test along the REAL objective gradient** (this lab has twice been burned by
gradients that looked right under a random seed; that failure mode is directly targeted here):

| direction | step | FD | adjoint `g·d` | rel err |
|---|---|---|---|---|
| **gradient (real seed)** | 1e-3 | 7.426746889338e-03 | 7.233332581166e-03 | **2.674%** |
| **gradient (real seed)** | 1e-4 | 7.427403293393e-03 | 7.233332581166e-03 | **2.683%** |
| random | 1e-3 | -6.739224728183e-05 | -6.624566174661e-05 | 1.731% |
| random | 1e-4 | -6.862686771289e-05 | -6.624566174661e-05 | 3.594% |

**Component test**, on cells spanning the gradient magnitude distribution:

| cell | adjoint `g[i]` | rel err @1e-2 | rel err @1e-3 |
|---|---|---|---|
| 1290 | 1.8529e-03 (largest) | 3.13% | 2.16% |
| 1254 | -1.8296e-03 | 2.26% | 2.26% |
| 1660 | 8.2758e-07 | 20.7% | 21.7% |
| 4116 | 1.0604e-08 | 25226% | 301%, sign flip |
| 4504 | 2.8187e-12 | unresolvable | unresolvable |
| 3752 | 0.0 exactly | unresolvable | unresolvable |

### The velocity-bound clips, audited 2026-08-01 — and the audit inverted the question

A monitor replay found four of these 34 logs printing `Bounding U<1000`
(`comp1254_p_0.001`, `comp1254_m_0.01`, `comp1660_p_0.001`, `comp4504_p_0.001`; 13 events, all at
the single printed iteration `Time = 100`). Monitor Standard S10a calls a ceiling clip FATAL. The
escalation asked which four points to exclude and whether 2.674% survives without them. **Both
questions turned out to be the wrong ones, and the reason is worth more than the answer.**

**DAFoam gates its bound message on `printInterval`.** The campaign ran at the default
`printInterval 100` (`logs/fd_points/base_a.log:474`), so each log reports clipping from **1% of
its iterations**. The four were never the four runs that clipped. They were the four whose clip
happened to land on a printed iteration.

**Measured, not reasoned.** Twelve points were re-run 2026-08-01 in a private case copy
(`/home/ubuntu/certonomous-runs/S1-fiml/ramp_kw_clipcheck/`) under the campaign protocol
byte-for-byte — same `runScript_S1.py`, same `rm -rf c1/processor*` cold reset, same 4 ranks — with
`printInterval: 1` as the only change:

| point | objective, archived | objective, re-run | iters | clips logged then | clips actually | clip window |
|---|---|---|---|---|---|---|
| base_a | 1.3816040076915038e-02 | **bit-identical** | 1833 | 0 | **20** | 40–56 |
| base_b | 1.3816040076915038e-02 | **bit-identical** | 1833 | 0 | **20** | 40–56 |
| dirg_p_0.001 | 1.3823467297330421e-02 | **bit-identical** | 3291 | 0 | **144** | 36–142 |
| dirg_m_0.001 | 1.3808613803551745e-02 | **bit-identical** | 1815 | 0 | **203** | 31–90 |
| dirg_p_0.0001 | 1.3816783010325821e-02 | **bit-identical** | 1910 | 0 | **27** | 37–55 |
| dirg_m_0.0001 | 1.3815297529667142e-02 | **bit-identical** | 1879 | 0 | **13** | 34–43 |
| dirr_p_0.001 | 1.3815972955104720e-02 | **bit-identical** | 2164 | 0 | **43** | 35–54 |
| dirr_m_0.001 | 1.3816107739599284e-02 | **bit-identical** | 2066 | 0 | **26** | 27–54 |
| comp1290_p_0.001 | 1.3817932976973112e-02 | **bit-identical** | 1977 | 0 | **3** | 38–43 |
| comp1290_m_0.001 | 1.3814146956982194e-02 | **bit-identical** | 2040 | 0 | **97** | 41–93 |
| comp1254_p_0.001 | 1.3814171027823122e-02 | **bit-identical** | 2625 | 3 | **93** | 69–102 |
| comp1254_m_0.001 | 1.3817913025369282e-02 | **bit-identical** | 2001 | 0 | **0** | — |

Three findings, in the order that matters.

1. **Eleven of the twelve clip — including the unperturbed baseline, and including both runs the
   2.674% headline is computed from.** 689 clip events against the 3 the archive recorded for the
   same twelve runs: a 230x undercount. The exclusion the escalation contemplated is therefore not
   available. There is no clip-free subset to retreat to; only `comp1254_m_0.001` is clean, and one
   leg of one component is not a verification.
2. **The clip provably does not touch the answer.** All twelve objectives return bit-identical to
   sixteen significant figures, and every iteration count matches the archive exactly (1833, 3291,
   2625, 2040, 2001 …). `printInterval` changed what was printed and nothing else. **`2.674%` and
   `2.683%` stand unchanged — and for a stronger reason than before: the very solves that produced
   them are now known to have clipped, and they reproduce the same numbers.**
3. **The clip is a startup transient, not a corrupted solution.** All 689 events fall in iterations
   **27 to 142** of runs 1815 to 3291 iterations long; every run is clip-free over its final **95%
   or more**. The bound is `UMax 1000`, DAFoam's own default — `runScript_S1.py` overrides only
   `omegaMin` — against a 10 m/s inlet. It is inactive at the fixed point the objective is read
   from, so the converged state satisfies the unbounded discrete equations and the finite difference
   is a difference of the same function. That is exactly what separates these from the withdrawn A4
   run, whose ceiling clip (`omega<1e+16`) is present at **every** printed iteration including its
   last (`logs_A4/A4_fine_primal_par4.log`, iterations 100/200/300/400/500 of 500).

**Both hypotheses in the escalation are refuted by the data.** The clip is *not* a symptom of the
perturbation being too large: three of the four originally-flagged points clip at the **smaller**
step `h=1e-3` while the same cell and direction at `h=1e-2` does not, and the baseline — zero
perturbation — clips 20 times. And the step-study plateau is *not* measuring the limiter: the
limiter is active in both plateau steps and in the baseline alike, so it cannot be what
distinguishes them. The residual ~2.7% remains unexplained, and this audit does not explain it.

**What the audit did cost, and this is the real defect it found.** `scripts/analyze_fd.py` reads
only the `OBJ` line and never inspects the log it came from. Had a clip mattered, nothing in this
protocol would have caught it — and the campaign's own `printInterval` meant the evidence was 99%
discarded before the analyzer ever ran. Any future FD campaign on this stack should run at
`printInterval 1` and have its analyzer refuse a point whose log clips outside the startup window.
That is a protocol defect, not a result defect, and it is recorded here rather than closed.

**Reading, stated at the precision the evidence supports.** The disagreement is ~2.7% and it is
**step-independent**: a factor of 10 in step moves it by 0.009 percentage points, where genuine
central-difference truncation error would fall by ~100x. By this lab's own doctrine that makes it
a real gap, not a resolution artifact.

**The obvious cause was tested and refuted.** Primal convergence was tightened 1000x
(`primalMinResTol` 1e-8 to 1e-11, achieved residual 9.947e-12). The objective moved by 1.9e-06
relative; the disagreement moved from **2.6739% to 2.6728%** — unchanged. Primal
under-convergence does not explain it, by the same decisive test A5's record used.

The large errors at cells 1660, 4116, 4504 and 3752 are **not** evidence of a defect: their
adjoint sensitivities are 3 to 9 orders of magnitude below the largest component, so the objective
change under perturbation is at or under double-precision resolution. Cell 4116's sign flip across
a decade of step is what an unresolvable component looks like, not what a corrupted one looks
like. They are reported as **unverified**, not as passed and not as failed.

**Verdict: PASS on the resolvable set** — 2.2 to 3.1% per component and 2.67% on the real
objective direction, all under the 5% bar, zero sign flips among components the finite difference
can actually resolve. With the caveat, recorded rather than buried, that the residual ~2.7% is
real, step-independent, convergence-independent, and unexplained.

**Verdict re-affirmed 2026-08-01 after the clip audit, and the basis restated.** The numbers above
did not move; what moved is what is known about the solves behind them. They are not clip-free
solves — eleven of twelve re-audited points trip DAFoam's default velocity bound during the SIMPLE
startup, the baseline included. They are solves in which the bound is confined to the first ~5% of
iterations and inactive at the converged state, re-run under the identical protocol to bit-identical
objectives. **The finite-difference verification stands.** It stands on a narrower and better-stated
claim than before: not "no clip occurred", which was never true and was never measured, but "the
clip is a transient the iteration discards, and the objective is provably unchanged by it".

## 4. The NASA hump: scoped, stood up, blocked

### The case

The F6a case is plain OpenFOAM and its `sides` patch is `empty`. DAFoam rejects meshes with fewer
than three geometric directions (established at zero compute in `B3_supervisor_debug.md` rung 2),
so `sides` was converted to `symmetry`. Warm-started from F6a's own converged field.

Three setup faults were found and fixed, each worth recording:

1. `Pr`/`Prt` must be **plain scalars**, not dimensioned entries. A dimensioned entry produces
   `Wrong token type - expected scalar value` from a stream named `Pr`.
2. A constraint patch requires a matching patch-field type. Declaring `calculated` on the
   `symmetry`-type `top` patch of the reference-data field is rejected by `decomposePar`.
3. **A silent-failure trap worth carrying forward: DAFoam does not check `decomposePar`'s exit
   status.** Fault 2 made `decomposePar` exit with a clean, precise `FOAM FATAL IO ERROR`, and
   DAFoam then continued into a broken state and died with a bare `SEGV` 4 seconds later. The
   SEGV is 12 lines of PETSc backtrace with no cause; the real error was only visible by running
   `decomposePar` by hand. This is the same class as L-15 and it is likely the true explanation of
   A3's undiagnosed "SEGV / corrupted field read during `decomposePar`" on its vcoarse mesh.

### Mesh quality, measured

| metric | measured | DAFoam default gate | result |
|---|---|---|---|
| max aspect ratio | **12,131.6** (18,352 cells above 1000) | 1000 | exceeds |
| max non-orthogonality | 40.55 deg (avg 9.20) | 70 | passes |
| max skewness | 0.743 | 4 | passes |
| cell volume | min 1.15057e-08, max 6.63754e-05 | — | "Cell volumes OK" |

The aspect-ratio gate was raised to 20,000, **disclosed**: this relaxes a quality gate, not a
solver tolerance, and the same mesh already produced F6a's validated primal (separation within
0.06% of NASA's own published SST result). The measured value is reported rather than hidden.

### Primal: works, and the objective cross-checks exactly

`primalMinResTol` 1e-6 satisfied at 9.72157e-07, 10.155 s. Objective, the variance of wall shear
stress on the hump wall against NASA's own experimental Cf:

```
Find 622 reference points for variance of wallShearStress
OBJ cfVar: 1.6263651522923017e-01
```

Independently pre-computed from the reference builder before the solver ran: mean squared residual
over the 289 faces inside the experimental window was 3.500412e-01, and 3.500412e-01 x 289/622 =
**1.62637e-01**. The two agree to 6 significant figures. This confirms the loss is reading the real
experimental data and is not B3's silent all-zero-objective trap.

Reference construction, disclosed: experimental Cf where the experiment has data (x/c in
[-0.07, 1.57], 289 of 622 wall faces); our own uncorrected SST baseline on the remaining 333 faces,
which lie far upstream where the experiment does not measure and where SST is already validated.
The second choice is an anchor, not a measurement: it makes those faces contribute ~0 at beta=1 so
the inversion is not driven by unmeasured stations.

### Adjoint: BLOCKED, `DIVERGED_NANORINF` at iteration 0

```
Calculating dRdW Coloring... Completed! 68.62 s
Partial derivative matrix created. 74.89 s
Solving Linear Equation... 112.12 s
Main iteration 0 KSP Residual norm 1.094138002900e+00 121.95 s.
**Completed**! Total iterations: 0. PetscConvergedReason: -9. 123.72 s
Residual tolerance not satisfied, solution failed!
```

**This is bit-for-bit the same failure class B3 hit on CBFS**: `-9` (`KSP_DIVERGED_NANORINF`),
zero iterations completed, finite nonzero initial residual. Two independent cases, two different
meshes, two different objectives, same signature.

**Memory is not the constraint, and this is the measurement that says so.** Host `MemAvailable`
went 30.06 GB at launch to a minimum of **18.99 GB** — a peak of roughly 11 GB, with no OOM, no
kill, and the Jacobian coloring completing normally in 68.62 s. The coloring stage is exactly
where A3's fine mesh and `naca0015_sail_medium` died; it does not die here. **`DAFOAM_CASE_STATUS.md`'s
cross-rung finding 1 ("working envelope is order 10^3 to 10^4 cells") does not apply to this case:
a 51,626-cell incompressible adjoint fits comfortably.** The wall here is conditioning, exactly as
R5 concluded for the compressible family.

### Mechanism ladder run on the hump

Each is one change against the same case, prediction written before launch.

| # | change | result |
|---|---|---|
| 1 | `useWallFunction: True` (high-Re wall treatment; verified applied, `nutkWallFunction` / `kqRWallFunction` / `omegaWallFunction` on `bottom`) | **REFUTED** — still `-9` at iteration 0 |
| 2 | `limitVelocity` fvOption removed (a non-differentiable clip active on all 51,626 cells; inert at the solution, max abs U 44.54 against a limit of 70) | **REFUTED** — still `-9`, identical initial residual |
| 3 | `normalizeResiduals: ["None"]` (verified applied: `normalizeResiduals 1 ( None )` against the baseline's 11 normalized residuals) | **SIGNATURE CHANGED** — no NaN. Runs the full budget and terminates `PetscConvergedReason: -3` (`DIVERGED_ITS`), 2000 of 2000 iterations, 965.94 s, residual **exactly flat** at 1.094138002900e+00 to 13 digits throughout |
| 4 | `jacMatReOrdering: natural` instead of `rcm`, matching the working tutorial's own adjoint settings | **SIGNATURE CHANGED** — no NaN. Runs the full budget and terminates `PetscConvergedReason: -3` (`DIVERGED_ITS`), 1000 of 1000 iterations, 565.71 s, residual flat at 1.094138002841e+00 to 13 digits throughout |

Rung 4's terminal state is worth quoting exactly, because it reproduces R5's most useful
mechanical observation. R5 established that DAFoam's success gate is fooled by a collapsing
residual: a `-5`/`-9` run prints "Residual tolerance satisfied, solution finished!" and lets
OpenMDAO continue, while a `-3` run prints "not satisfied" and correctly aborts. The hump
follows that exactly — `-9` while the NaN is present, `-3` once it is not.

**Rung 4 matters for reading B3.** The reverse Cuthill-McKee reordering is what B3's CBFS script
used and what this hump attempt used first; the working tutorial uses `natural`. Switching to
`natural` is on its own enough to stop the NaN. So `rcm` is implicated in *producing* the
`DIVERGED_NANORINF` specifically, and any future attempt should treat the reordering as a variable
rather than a constant. It is not, however, the whole story: with the NaN gone the solver still
makes no progress at all.

**The two levers that change the signature do not stack into a fix.** Both rung 3 and rung 4
convert catastrophic failure into honest stagnation, and in both the residual is flat to 13
significant figures — not slow convergence, zero progress. That is the same place R5 ended up on
the M6 family after four levers.

**Result 3 reproduces R5's headline finding on a completely different physics family.** R5
established on the compressible transonic M6 that `normalizeResiduals=None` converts a
catastrophic failure into honest stagnation without producing convergence. That is exactly what it
does here on an incompressible, separated, wall-resolved SST case: the NaN goes away, the solver
stops lying about being finished, and nothing converges. R5's conclusion — that residual scaling
was never the whole story and a second, un-fixed layer of ill-conditioning remains — now has
support from two unrelated case families.

Note also that **prediction 1 was mine and it was wrong**, and it is recorded as such: wall
treatment looked like the clean discriminator across the three cases (tutorial works with wall
functions; CBFS and hump both fail wall-resolved), and it is not the cause on the hump.

### What is NOT available as a route around this

`B3_supervisor_debug.md`'s ladder lists "frozen-turbulence adjoint" as rung 4. **That route is
structurally unavailable to field inversion.** beta lives inside the turbulence model, so
`dR/dbeta` exists only through the turbulence residuals; freezing them out of the Jacobian removes
the very sensitivity being solved for. It remains a valid diagnostic for locating the NaN, but it
can never be the configuration a real inversion runs in.

### Addendum 2026-08-02 (well W4): the reordering axis run to completion, and rung 4's reading corrected

Rung 4 above tested one alternative ordering (`natural`) on one case (the hump) and concluded
*"`rcm` is implicated in producing the `DIVERGED_NANORINF` specifically, and any future attempt
should treat the reordering as a variable rather than a constant."* Both halves were worth testing
properly. Docket item `w4-rcm-reordering-across-blocked`. Full record: `PROOF.md` §25.2-25.3.

**1. Rung 4 generalises to CBFS.** B3's own `runScript.py` used `rcm` and had never had it varied.
One-token change, `compute_totals`, np=4, 21,000 cells / 4 ranks = **5,250 cells per rank**: `rcm`
reproduces B3's published `Total iterations: 0. PetscConvergedReason: -9` exactly (87.96 s against
its own 111.17 s on a busier box), `natural` gives `Total iterations: 1000. PetscConvergedReason:
-3` (237.9 s). Same signature change, second case.

**2. But it is not "`rcm` is the bad one". The whole ordering axis was run, and it splits two ways.**
`DALinearEqn.C` exposes five orderings; this lab had ever used two.

| `jacMatReOrdering` | reason | iterations | wall |
|---|---|---|---|
| `rcm` (DAFoam's default, `pyDAFoam.py:530`) | **-9** `DIVERGED_NANORINF` | 0 | 87.96 s |
| `1wd` one-way dissection | **-9** `DIVERGED_NANORINF` | 0 | 90.53 s |
| `natural` | -3 `DIVERGED_ITS` | 1000 | 237.9 s |
| `nd` nested dissection (the source's own suggestion at `pyDAFoam.py:525`) | -3 `DIVERGED_ITS` | 1000 | 353.5 s |
| `qmd` quotient minimum degree | -3 `DIVERGED_ITS` | 1000 | 245.43 s |

**Two of five produce the NaN, three produce honest stagnation, and none converges.** The initial
residual is identical (7.091590452305e-04) in all five, as it must be. A single buggy ordering
would not do this; a factorization that is singular, hitting a destructive zero pivot under some
elimination orders and not others, does exactly this.

**3. The objective controls nothing.** Changing the objective changes `dF/dW` and leaves `dR/dW`
untouched; B3 had varied it only under `rcm`. Run as a clean single-factor 2x2 (same mesh, DVs,
`pcFillLevel: 1`, only the `function` block swapped for the standard `force`/CD objective):

| | `rcm` | `natural` |
|---|---|---|
| `varianceU` (field) | `-9`, iteration 0, 92 s | `-3`, 1000 iterations, 238 s |
| `CD` (force) | `-9`, iteration 0, 92 s | `-3`, 1000 iterations, 263 s |

Under `force`+`natural` the residual is **bit-identical** at 5.324334345172e-02 from iteration 100
to iteration 1000 -- this document's own hump signature, on a different case and a different
objective.

**4. The cause, reproduced with no DAFoam in the loop.** The preconditioner matrix and RHS were
dumped with stock PETSc runtime flags (`-ksp_view_pmat binary:`, `-ksp_view_rhs binary:`; no source
change) and analysed offline. `||b|| = 7.091590452305e-04`, matching the printed iteration-0
residual to all 13 digits. The matrix (210,592 square, 13,710,468 nonzeros) has **no zero rows, no
zero columns and no zero diagonal entries**, and a diagonal spread of **8.67 decades against the M6
family's 14.17** -- so R5's conditioning mechanism does not transfer to this case. Then:

* `scipy.sparse.linalg.spilu(drop_tol=1e-5, fill_factor=10)` -> **`RuntimeError: Factor is exactly
  singular`**. The `-9`, in a second independent implementation.
* `scipy.sparse.linalg.splu` -- full LU **with partial pivoting** -- solves it exactly,
  `||Ax-b||/||b|| = 2.535461e-12`. The system is nonsingular and consistent; a solution exists.
* Unpreconditioned `scipy` GMRES reproduces the stagnation (relative residual 1.0 -> 9.999687e-01
  over 1000 matvecs) with no DAFoam, no PETSc solver and no MPI, which exonerates DAFoam's KSP/PC
  configuration.

One mechanism covers both signatures and explains why B3's own `pcFillLevel: 4` also returned `-9`:
**fill adds fill, not pivoting.** `DALinearEqn.C` hard-codes `PCType localPCType = PCILU;` (and
already switches on `PCFactorSetPivotInBlocks(PETSC_TRUE)` and `MAT_SHIFT_NONZERO` with
`PETSC_DECIDE`, which are not sufficient here), so a pivoting-capable factorization is not reachable
from `daOptions` without recompiling `libDASolver.so`. Stated as a located limitation; nothing filed.
*Caveat, stated rather than buried:* the dumped matrix is the assembled preconditioner `dRdWTPC`,
not the matrix-free transpose Jacobian GMRES applies. The singular-ILU result is direct -- that is
the matrix DAFoam factors -- and the GMRES-stagnation results are corroborative.

**5. This section's own claim about the success gate is CORRECTED, on measurement.** Rung 4's
write-up above says: *"a `-5`/`-9` run prints 'Residual tolerance satisfied, solution finished!' and
lets OpenMDAO continue, while a `-3` run prints 'not satisfied' and correctly aborts. The hump
follows that exactly."* **The hump's own log does not support that.** Counting the two strings
directly:

| log | `...satisfied, solution finished` | `...not satisfied, solution failed` | reason |
|---|---|---|---|
| `S1_work/logs/hump_adjoint_run1.log` | **0** | 1 | `-9` |
| `S1_work/logs/hump_nat_run1.log` | **0** | 1 | `-3` |
| `W4-cbfs-reordering/cbfs_rcm_computetotals.log` | **0** | 1 | `-9` |
| `A3-onera-m6-sweep-n15_21840/run_opt5_onera_n15_21840.log` | **2** | 0 | `-5` |

R5's finding is correct and is specific to **`-5`**, where the residual collapses to denormal range
and therefore reads as converged to the tolerance test. **`-9` never fools the gate** -- a NaN fails
the comparison and DAFoam raises `AnalysisError("Adjoint solution failed!")`, which every `-9` run
here does. Extending R5's `-5` result to `-9` was an over-generalisation. It matters in the safe
direction: the hump and CBFS `-9` blockers were never at risk of silently returning a wrong
gradient, whereas the M6 `-5` runs were.

**6. And the premise that motivated the docket item is half wrong, at zero compute.** The item's
rationale states *"A3, CBFS and the transonic case are all blocked with related signatures and none
has had the reordering varied."* Read from DAFoam's own runtime echo rather than the scripts, the
**entire A3/ONERA-M6 family -- transonic included -- was already running `natural` when it failed**,
in its original 2026-07-28 logs, before R5 touched anything (`A3-onera-m6-transonic/check_totals_run1-6.log`,
`A3-onera-m6-adjoint-coarse/check_totals_run1-3.log`, all echoing `jacMatReOrdering natural`). The
reordering cannot be their shared setting. Across 354 `runScript*.py` on this box the split is 181
`rcm` / 118 `natural` / 55 unset, and the cases that **work** span both -- A1, the naca0015 sail, A2
and A4 all use `rcm`; the working `ramp_kw` SST field-inversion tutorial uses `natural`. **The
ordering is neither necessary nor sufficient for success. What it controls, reproducibly, is
whether a case that was going to fail anyway fails as a NaN or as honest stagnation.**

All four cells of that table have primary evidence, read from each case's own runtime echo and
converged reason:

| | converges | fails |
|---|---|---|
| `rcm` | **A1** (`Mat ReOrdering: rcm`, `PetscConvergedReason: 2`); **A4** (`rcm`, reason `2`, 719 iterations, 21.48 s) | **hump**, **CBFS** (`rcm`, reason `-9`, 0 iterations) |
| `natural` | **`ramp_kw`** SST field inversion (91 iterations, reason `2`) | **A3/M6 family** (`natural`, reason `-5`); reconfirmed this session on R5's own 21,840-cell reproducer, 5,460 cells per rank: CD adjoint `-5` at 400 iterations / 100.87 s, CL adjoint `-5` at 600 iterations / 169.57 s |

Evidence: `/home/ubuntu/certonomous-runs/W4-cbfs-reordering/` -- `cbfs_{rcm,natural,nd,1wd,qmd,force_rcm,force_natural}_computetotals.log`,
`cbfs_dump/{pmat,rhs}.dat`, `analyze_dump.py`, `analyze_dump2.py`, `run_cbfs.sh`, `stage.sh`.

### Addendum 2026-08-04 (well W4): the blocker is broken

The `-9` mechanism this section measures is now located and fixed:
`W4_ADJOINT_PC_UNBLOCK.md`. The ASM sub-block incomplete factorization is the
failing layer; switching it to complete LU (env-var switch `DAFOAM_SUBPC_TYPE=lu`
in a locally rebuilt `libDASolver`, image `dafoam-subpclu:v1`) converges the CBFS
adjoint (`PetscConvergedReason: 2`, 667 iterations) on B3's exact `-9`
configuration, and the first closure-relevant field-inversion gradient now exists:
21,000 beta components on CBFS, FD-verified to 0.085/0.059/0.199 percent on three
components. On the hump the same switch replaces the `-9` NaN with a completing
factorization and a monotonically descending (but slow) residual, stopped at the
memory envelope — details and the remaining hump question in that document.

## 5. Cost scoping, measured rather than estimated

| quantity | tutorial case (works) | NASA hump (blocked) |
|---|---|---|
| cells | 5,000 | 51,626 |
| design variables (one beta per cell) | 5,000 | 51,626 |
| primal, 4 ranks | 7.8 to 12.8 s | 10.2 s (warm-started) |
| Jacobian coloring (one-time, cached) | included below | 68.6 s |
| partial-derivative matrix | included below | ~6 s |
| adjoint solve | 5.8 to 11.9 s | never completes |
| peak host memory | not a factor | ~11 GB, 18.99 GB still free |
| one gradient (primal + adjoint) | **~25 s wall / ~1.7 core-min** | not obtainable |

**On the hump the adjoint cost is not the obstacle and neither is memory.** Had the linear solve
converged at a per-call cost comparable to the tutorial's scaling, a 50-iteration inversion would
sit in the low hours on this host. The blocker is that the linear solve produces NaN or does not
descend at all.

**The number that actually constrains FD verification, and it is worth stating separately:** a
full `check_totals` over a per-cell beta field is 2N primal solves — 10,000 on the tutorial case,
**103,252 on the hump**. Field-inversion gradients cannot be verified the way this lab's shape
gradients have been. The directional-plus-sampled-component protocol used in section 3 is the
affordable substitute and it is what "FD-verified" has to mean at this design-variable count.

## 6. Where Stage 1 stands, and what the cheapest affordable target is

- **Stage 1's capability half is DONE and verified**: a per-cell beta field on the PRODUCTION term
  of DAFoam's own SST model, driven through a converging discrete adjoint, FD-verified to 2.67% on
  the real objective direction, with the warp defect proven absent from the chain. The term is
  named here because it is the whole of what was verified: nothing in this record establishes
  anything about a beta on the destruction term, which this install does not expose. The 2.67%
  survived a clip audit on 2026-08-01 (section 3): the FD solves do trip DAFoam's default velocity
  bound in their startup transient, the baseline included, and re-running them with full logging
  returns bit-identical objectives.
- **Stage 1's stated target, the NASA hump, is NOT reachable today**, for a reason that is now
  measured rather than guessed: an adjoint linear-solve conditioning failure that is independent
  of memory, of mesh size in the range the lab feared, of wall treatment, and of the
  non-differentiable clip in the case's fvOptions.
- **The cheapest case where field inversion IS affordable today is the 5,000-cell tutorial case at
  ~1.7 core-min per gradient** — but it is a synthetic self-inversion (kOmega corrected toward SST)
  and carries no closure-benchmark value. **There is currently no closure-relevant case on which
  this lab can run a field inversion**: CBFS (21,000 cells) and the hump (51,626 cells) both fail
  with the same `-9`.
- **C2, the error decomposition against the top-4 gap, stays blocked on this.** That is the
  planning consequence and it should not be softened.

## 7. Leakage statement

No inversion was run against any scored test case, because no inversion ran at all. The hump's
experimental Cf was read only to build the loss function and to compute the baseline objective
value reported above.

Recorded for whoever runs the inversion once the blocker clears: **`NASA_2DWMH` is one of the
closure challenge's scored test cases.** Inverting beta against its experimental data is
legitimate field inversion but it is in-sample by construction, and the resulting benchmark score
must never be reported as a generalization result. The FIML workflow that stays clean is to invert
on a training case, learn beta as a function of local features, and apply it forward.

## 8. Evidence

Logs and scripts: `S1_work/logs/` and `S1_work/scripts/`.

| file | what it holds |
|---|---|
| `logs/fd_sweep_run1.log`, `logs/fd_points/` | 34 fresh-process FD evaluations, at `printInterval 100` |
| `logs/fd_clip_audit_run1.log` | **the 2026-08-01 clip audit**: 12 points re-run at `printInterval 1`, every one of the 689 clip events with its iteration, and the bit-identical objective and iteration count against the archived run |
| `logs/fd_plan.json` | FD design, adjoint component values, directions |
| `logs/s1_e1_kw.json`, `s1_e2_sst.json`, `s1_e2_tight.json` | gradients, timings, warp probe |
| `logs/hump_adjoint_run1.log` | hump `-9` blocker, primary evidence |
| `logs/hump_mem_run1.log` | host MemAvailable sampled every 2 s during that run |
| `logs/hump_wf_run1.log`, `hump_nofvopt_run1.log`, `hump_nrn_run1.log`, `hump_nat_run1.log` | mechanism ladder rungs 1 to 4 |
| `scripts/` | run scripts, FD generator and analyzer, reference-field builder |

Case working directories are not committed (OpenFOAM binary and processor state, regenerable):
`/home/ubuntu/certonomous-runs/S1-fiml/{ramp_kw,hump,hump_wf,hump_nrn,hump_nofvopt,hump_nat}`, and
`ramp_kw_clipcheck` holding the 21 MB of full `printInterval 1` logs the clip audit distilled.
