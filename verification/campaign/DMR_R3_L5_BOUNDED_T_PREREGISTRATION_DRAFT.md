# DMR R3 L5 — BOUNDED-T / POSITIVITY-PRESERVING ENERGY CLIP SUCCESSOR — PRE-REGISTRATION

> ## STATUS: **DRAFT — NOT FROZEN, NOT AUTHORISED — SOLVER-BUILD BOUNDARY — AWAITING SANAA'S GO.**
>
> Prepared by the cfd `lab-lane`, 2026-09-08. **This rung crosses the OpenFOAM
> solver-build boundary** (a `wmake` of a modified `rhoCentralFoam`), which is
> **Sanaa's authorisation alone**. Accordingly this document commits **no**
> `wmake`, **no** solver build, **no** compute, **no** freeze, **no** queue row
> and **no** launch. It is a DRAFT for the cfd supervisor's §3 **check-4**
> (patch spec / gates / lever / cost / roots / commit, taken personally) and
> Sanaa's go. Nothing is sent, filed, uploaded, registered or posted (rule 7).
>
> **Gates are transcribed BYTE-IDENTICAL from the frozen DMR parent and NOT
> widened** (§4). The single registered lever vs the L4 first-order-T successor
> is the **solver binary**: vanilla `rhoCentralFoam` → the new lab solver
> `rhoCentralFoamBoundedDMR`, which floors internal energy `e` (hence
> temperature `T`) to a positive value **before** `thermo.correct()`. Heeds
> **L-501**: a crash of this family would be a MEASURED negative result, never a
> capability inference from one/two SIGFPEs.

---

## 0. §2ay classification and why L5 is the correct next rung

Parent of THIS successor for GATES and OUTPUT identity: the **DMR L4 first-order-T
successor** (`DMR_R3_L4_FIRSTORDER_T_PREREGISTRATION.md`, frozen `3c202ab1`), which
is byte-identical to the DMR Tadmor successor except `reconstruct(T) Minmod→upwind`,
which is byte-identical to the frozen DMR parent (`DMR_PREREGISTRATION.md`) except its
registered levers. **Gate V' tol `0.0231` traces unbroken to that frozen parent
(`DMR_PREREGISTRATION.md:88,:91`).**

**Mechanism, MEASURED (background, not re-decided here):** L4 graded **NOT A RESULT**
(`DMR_R3_L4_FIRSTORDER_T_RESULTS.md`). R1 (N=60) and R2 (N=120) both `rc=0` and both
PASSED Gate V' well inside the byte-identical tolerance — position errors **0.009204**
and **0.005318** vs tol `0.0231`, **decreasing with refinement**. The finest level R3
(N=240) **SIGFPE'd (rc=136) at `Time = 0.15463531`** of `endTime 0.2`, deepest named
frame `Foam::sqrt(Field<double>&, UList<double> const&)`. The cfd supervisor's
first-hand crash triage attributed this to the **cell-centre T-positivity failure at
the reflecting-wall foot** — vanilla `rhoCentralFoam.C:136`
`volScalarField c("c", sqrt(thermo.Cp()/thermo.Cv()*rPsi));`, where `rPsi = 1/psi ∝
R·T`, so a negative argument ⟺ a negative cell-centre T produced by the conservative
update **after** `thermo.correct()`. First-order-T reconstruction delayed the collapse
by ~0.004 in sim-time (0.15464 vs the L2 Courant probe's 0.15006) but **did not cure
it** — the measured exhaustion of the *reconstruction-diffusion* lever for this
mechanism.

§2ay state **(b) NUMERICS-ROBUSTNESS** has one remaining route the lever analysis
(`DMR_R3_NUMERICS_ROBUSTNESS_LEVER_ANALYSIS.md` §2 lever **L5**, lines ~205–220)
identified as **out of the standard dict levers**: vanilla `rhoCentralFoam` v2606 has
**no in-loop bound on `T` or `e`** — the only clip is `v_zero` on wave speeds; there is
no `bound(e,eMin)` / `T.max(TMin)` after `thermo.correct()`. **L5 is that route: a
bounded internal-energy / positivity-preserving update, built as a named lab solver.**
It targets the diagnosed line-136 mechanism **directly** — it does not add diffusion,
it removes the nonphysical negative-T state that produces the `sqrt` fault.

**Why L4 is the numerics parent (single-lever purity AND best motivation).** L5 adds
**exactly one** lever to the configuration that (i) got FURTHEST in sim-time of any
measured N=240 run and (ii) whose two completed levels already PASSED Gate V' with
margin. L5 therefore keeps L4's numerics **byte-identical** (Tadmor flux, `maxCo 0.1`,
Euler ddt, `reconstruct(rho) Minmod`, `reconstruct(U) MinmodV`, `reconstruct(T)
upwind`, all BCs, write times, 4-rank layout) and changes **only** the solver binary.
Because the clip is designed to fire **only on a nonphysical negative-T excursion**
(§2), it is expected to be **inert at R1/R2** (which completed cleanly with no
crash), so R1'/R2' should reproduce L4's Gate V' PASS values; any deviation would be
reported (the solver prints a `BOUND:` line naming the cell whenever it fires).

## 1. WHY A NEW FAMILY, NOT A RE-RUN

The parent DMR triple prereg names as a **disqualifier** "any difference in scheme,
constants, boundary conditions, maxCo, write times or rank count between rungs — the
triple requires one numerics family and a difference invalidates it." The solver-binary
change is therefore applied **uniformly to all three levels** of a **fresh,
self-contained three-level family** — R1' (1/60, 240×60), R2' (1/120, 480×120),
R3' (1/240, 960×240), nested exactly 2:1 — graded as its OWN Gate V' and its OWN
grid-convergence triple. The vanilla-`rhoCentralFoam` L4, Tadmor, Minmod-positivity and
original `vanLeer` families are all **untouched**.

## 2. THE EXACT SOLVER PATCH SPEC — the build boundary

**This is a solver-code modification requiring `wmake`. It is Sanaa's authorisation.**

### 2.1 Base solver and the new named target
- **Base:** stock OpenFOAM **v2606** `rhoCentralFoam` (the density-based
  Kurganov/Tadmor central-upwind solver;
  `/usr/lib/openfoam/openfoam2606/applications/solvers/compressible/rhoCentralFoam/`).
- **New named lab solver:** **`rhoCentralFoamBoundedDMR`**. `Make/files` sets
  `EXE = $(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMR`. **A DISTINCT binary name** —
  it does **not** overwrite the stock `rhoCentralFoam` binary, and it does **not**
  overwrite the existing `rhoCentralFoamBounded` (which is behind PUBLISHED F4 SWBLI
  results — `verification/runs/F4_runs/swbli_cylflare/warmup20_bounded/` and siblings
  name `application rhoCentralFoamBounded;`, and its `boundE.H` hard-codes the SWBLI
  thermo constants `Cv = 1005 − 8314.47/28.9 = 717.30`, which are **wrong for the DMR
  nondimensional thermo** — see §2.3). L5 is a NEW solver so nothing published moves.
- **Source home (tracked):** a new dir
  `verification/runs/DMR_runs/rhoCentralFoamBoundedDMR_src/`, carrying the stock
  `rhoCentralFoam` sources plus the two-file addition below, so the solver is
  rebuildable from tracked source per `docs/OPENFOAM_SOLVER_BUILD.md`.

### 2.2 The exact source site and the bound
The patch mirrors the existing, proven `rhoCentralFoamBounded` pattern
(`verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src/`), which floors
`e` at exactly the crash-critical site. **The single change to the time loop** is a
`#include "boundE.H"` inserted **after** the energy update line
`e = rhoE/rho - 0.5*magSqr(U);` (stock `rhoCentralFoam.C:265`) and its
`e.correctBoundaryConditions();`, and **BEFORE** `thermo.correct();` (stock `:268`):

```
        e = rhoE/rho - 0.5*magSqr(U);
        e.correctBoundaryConditions();
        #include "boundE.H"        // <-- L5 addition (before thermo.correct)
        thermo.correct();
```

and, only if the case were viscous, the identical `#include "boundE.H"` before the
second `thermo.correct()` in the `if (!inviscid)` energy-diffusion branch (stock
`:282–283`). **The DMR case is inviscid** (`transport const`, `mu 0`; confirmed in the
L4 case `constant/thermophysicalProperties`), so **only the first clip site fires**;
the viscous site is present for solver generality but is not exercised.

`boundE.H` clips `e` element-wise and reports the localisation:
```
    e = min(max(e, eMin_bound), eMax_bound);
```
with a per-fire `Info<< "BOUND: e below eMin in <n> cell(s) at Time = ... worst e = ...
at cell ... C = ..."` diagnostic (built-in localisation — the crash's own artifacts
could not provide this because the failing step was never written).

**Why this cures the diagnosed mechanism.** Flooring `e ≥ eMin_bound` (i.e. `T ≥ TMin >
0`) **before** `thermo.correct()` guarantees `psi ∝ 1/(R·T) > 0`, hence `rPsi = 1/psi >
0`, hence the line-136 argument `Cp/Cv · rPsi > 0` and `c = sqrt(...)` is real — **the
specific SIGFPE at `rhoCentralFoam.C:136` cannot recur**. Once the cell-centre `c` and
`rPsi` fields are positive, the reconstructed FACE sound speeds (`cSf_pos/neg`, stock
`:137–147`) are TVD/`upwind` interpolations of positive cell fields and stay positive
by monotonicity — so the face `sqrt` path is protected too.

### 2.3 How `eMin`/`TMin` are chosen — physically justified, NOT tuned to the answer
The clip must floor **temperature** positive; under `hConst` the T-inversion is exact
and linear, `T = Tref + (e − eref)/Cv`, so an `e`-floor bounds `T` exactly:
`eMin_bound = Cv·(TMin − Tref)`.

- **Cv and Tref are DERIVED FROM THE DMR CASE'S OWN thermophysicalProperties**, not
  from recall and not from the SWBLI solver. The L4/DMR case (verified on disk,
  `verification/runs/DMR_R3_L4_FIRSTORDER_T_runs/R1/constant/thermophysicalProperties`)
  is `hePsiThermo / pureMixture / const transport / hConst thermo / perfectGas /
  sensibleInternalEnergy`, with `Cp 2.5`, `molWeight 11640.3`, `Hf 0`. Hence
  `R = 8314.47/11640.3 = 0.714283`, **`Cv = Cp − R = 1.785717`**, `γ = Cp/Cv =
  1.40000`; `Tref = Tstd = 298.15 K` (OpenFOAM's `hConst` default, NOT overridden in
  this case; `eref` default 0). These are the constants baked into (or read by) this
  solver's `boundE.H`; the SWBLI solver's `Cv = 717.30` would be wrong by a factor of
  ~400 and is the reason a new solver is required.
- **`TMin` is a pure positivity floor, provably below every physical state.** The DMR
  undisturbed (pre-shock) state is `p = 1.0`, `ρ = 1.4`, so ambient `T = p/(ρR) =
  1.0/(1.4·0.714283) = 1.000` (nondim); the flow is shock **compression** and
  reflection, all heating — **no expansion cools any cell below ambient `T = 1.0`.**
  Setting **`TMin = 1e-3`** (0.1% of ambient, three orders of magnitude below the
  coldest physical state) means the clip can activate **only** on a nonphysical
  near-zero/negative `T` excursion — the crash itself — and can never touch a physical
  value. This is the plant-the-zero discipline in the solver: the clip is inert unless
  the run is already producing an impossible state. `TMin` is read from
  `controlDict` (`getOrDefault<scalar>("TMin", 1e-3)`) so it is transparent and
  adjustable without recompiling; the registered value is `1e-3`.
- **`eMax`/`TMax`** is a symmetric **runaway ceiling only**, not a physical bound. The
  positivity-critical bound is `eMin`. `TMax = 1e4` (nondim), well above any true DMR
  peak, so `eMax` should never bind; **if it ever binds that is itself a reported
  finding** (a diverging solve), not a silent correction.

Derived (checkable): `eMin_bound = 1.785717·(1e-3 − 298.15) = −532.410 J/kg`; ambient
`e = 1.785717·(1.0 − 298.15) = −530.626 J/kg`. So `eMin_bound` sits **just below** the
ambient `e` and far below every post-shock `e` (T higher ⇒ e higher) — it clips only
sub-ambient-by-orders-of-magnitude (i.e. nonphysical) excursions.

### 2.4 Honest statement of what the clip is and is not
The clip is **NON-CONSERVATIVE** in any cell where it fires: it injects the energy
needed to lift `e` to `eMin_bound`. In cells where it does not fire (all of R1/R2 if
they behave as in L4, and all bulk-flow cells away from the reflecting-wall foot) the
solver is bit-for-bit the stock conservative update. The non-conservation is therefore
**localised to the wall foot at R3'**. This is the source of the GATE-FAIL-on-accuracy
risk in §4/§7 and is stated **before** the run (rule 2), not discovered after.

## 3. GATES — NO THRESHOLD WIDENED (BYTE-IDENTICAL transcription proof)

- **Gate V' (kinematics vs exact theory):** PASS iff
  **`|x_measured − 2.99568| ≤ 0.0231`**, applied at each of R1'/R2'/R3'.
  **BYTE-IDENTICAL to the frozen parent**, proven by quotation:
  - frozen parent `DMR_PREREGISTRATION.md:91` reads verbatim
    `PASS iff |x_measured − 2.99568| ≤ 0.0231 at both rungs`, and `:88`
    `(±0.0231 in x)`;
  - the grader literal on disk, `verification/runs/DMR_runs/dmr_locator_v2.py:69`,
    reads verbatim **`GATEV_TOL = 0.0231`** (confirmed at authoring 2026-09-08);
  - the L4 successor carried the same `0.0231` byte-identical
    (`DMR_R3_L4_FIRSTORDER_T_PREREGISTRATION.md:118`).
  **No band moved. The tolerance is NOT relaxed to accommodate a non-conservative
  clip** — a clip that displaces the shock past `0.0231` GATE FAILs, honestly (§7).
- **Gate T' (grid-convergence triple, rule 5 in full):** self-convergence triple of
  the Gate V' position error across R1'/R2'/R3' (Roache no-exact form, exact 2:1
  nesting). A non-`CONVERGING` triple is **NOT A RESULT**; a `CONVERGING` triple is
  graded against its band; GCI at `Fs = 1.25`, never quoted on a non-monotone triple.
  A run failing the strict completion rule (rule 4: `rc=0`, `End`, last time ==
  `endTime`, fields present, age guard) is not a completed level. No band loosened.
- **Controls carried over from the grader (unchanged):** planted whole-cell density
  displacement (rule 3), planted-absence refusal, and the regression reproducing the
  2026-08-07 R1/R2 Gate V positions to 1e-12.

## 4. GRADING PATH — REUSED UNCHANGED, HASHED AT GRADE TIME

Grading is by the frozen method-agnostic
`verification/runs/DMR_runs/dmr_locator_v2.py` — it grades shock **POSITION** and reads
**no** scheme or solver file, so it grades the bounded-solver family unchanged. Its
identity is pinned:
- **git blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`**, confirmed at authoring
  (2026-09-08) to equal `HEAD:verification/runs/DMR_runs/dmr_locator_v2.py`
  (`git hash-object` == `git rev-parse HEAD:…`, both
  `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`), `GATEV_TOL = 0.0231` at `:69`.
- The L5 driver **re-hashes the grader against this blob before grading each level and
  refuses on mismatch** (rule 2). The grader is **REUSED UNCHANGED and NOT edited**
  (rule 6). The planted-zero controls of §3 are mandated before any verdict (rule 3).

## 5. SOLVER-BUILD PROVENANCE — what the build MUST record (per `docs/OPENFOAM_SOLVER_BUILD.md`)

Because L5 crosses the build boundary, the following are **mandatory build artifacts**,
to be produced **only after Sanaa's go**, before any solve, and pinned into the frozen
successor at freeze:

1. **Tracked source + full diff vs stock.** The complete
   `rhoCentralFoamBoundedDMR_src/` tree tracked in git, with a
   `diff -rq` vs stock v2606 `rhoCentralFoam` showing the change set is **exactly**:
   the added `boundE.H`, the `createFields.H` addition that derives
   `eMin_bound/eMax_bound` from the DMR constants (§2.3), the two `#include "boundE.H"`
   lines, and `Make/files` `EXE` renamed to `rhoCentralFoamBoundedDMR` — **and nothing
   else**. (The five stock headers `centralCourantNo.H`, `createFieldRefs.H`,
   `directionInterpolate.H`, `readFluxScheme.H`, `setRDeltaT.H` must be byte-identical
   to stock, per §7 of the build doc.)
2. **Build environment recorded:** OpenFOAM v2606 (`openfoam2606-common`), g++ 13.3.0,
   target `linux64GccDPInt32Opt`, built via `openfoam2606 -c '… wmake'` per §4 of the
   build doc; the **full `wmake` build log** captured.
3. **wmake target name** read from the committed `Make/files` (`EXE =
   $(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMR`), not asserted.
4. **Binary hash recorded** (md5 **and** sha256 of the produced
   `rhoCentralFoamBoundedDMR`), pinned in the frozen successor, exactly as
   `docs/OPENFOAM_SOLVER_BUILD.md` §6 records the four existing artifacts.
5. **Rebuild-verify** per §5 of the build doc: rebuild under a redirected `$HOME` and
   `cmp` (or hash-match) to confirm rebuildable-from-tracked-source, and confirm the
   build **did not** touch `$(FOAM_USER_APPBIN)/rhoCentralFoam` or
   `rhoCentralFoamBounded`.
6. **Case wiring:** each level's `system/controlDict` sets `application
   rhoCentralFoamBoundedDMR;` and `TMin 1e-3; TMax 1e4;`. The rule-4 age-guard and
   absent-root guard (§8) apply to the case dirs as for any run.

The one-time build is **compute** (a `wmake` compile) but crosses the **authorisation**
boundary regardless of its trivial cost; it is costed in §6 for completeness.

## 6. COST — rule 12 (core-minutes; dollars DERIVED, not measured)

4 ranks per solve. **Measured anchor: the L4 family's own figures**
(`DMR_R3_L4_FIRSTORDER_T_RESULTS.md`), because L5 keeps L4's numerics and step count and
adds only a per-step element-wise `min/max` over cells (a marginal, sub-few-% overhead;
no limiter added).

### 6a. One-time solver build (essentially free compute, crosses the boundary)
`wmake` of one solver executable, single-threaded compile: ~1–3 min wall ≈ **~2
core-min** one-time. This is a compile, not a solve; it produces the binary hashed in §5.

### 6b. The three-level triple run (anchored on measured L4)
| item | h | grid | basis | core-min |
|---|---|---|---|---|
| R1' | 1/60 | 240×60 | L4 R1 MEASURED (`R1.coresec.txt`=59) | **0.983 MEASURED-ANCHORED** |
| R2' | 1/120 | 480×120 | L4 R2 MEASURED (`R2.coresec.txt`=269) | **4.483 MEASURED-ANCHORED** |
| R3' | 1/240 | 960×240 | L4 R3 spent 24.6 core-min reaching t=0.15464 (77.3% of endTime 0.2), crash-truncated; extrapolate to COMPLETION: 24.6/0.773 ≈ **~32** | **~33 ADVISORY (extrapolated to completion, +clip overhead)** |
| build (§6a, one-time) | | | wmake compile | ~2 |
| mesh/init/reconstruct/locator overhead | | | | ~1.5 |
| **family point estimate (solves + overhead, ex-build)** | | | | **≈ 40 core-min** |
| **HARD CAP (the ONE registered family cap)** | | | | **100 core-min** |

**ONE registered hard cap: 100 core-min** — a single accumulator across all steps of
all three levels of the solve family (the build in §6a is a separate one-time compile,
not under the solve cap). An overrun **STOPS the run** and writes `CAP_BREACH.txt`; no
new budget (rule 12). Per-level figures are advisory rule-12 watermarks, NOT per-level
caps. R3' dominates.

**Why the cap is RETAINED at 100 and NOT raised above L4's 100.** The task flags a
possible ~110–120 for a completing R3. The anchored figures do **not** support raising
it: L4's **measured** R3 rate (24.6 core-min at 77.3% ⇒ ~32 to completion) puts the
whole family at ~40 core-min — a **2.5× margin** under 100. The earlier ~77 core-min R3
estimate in the L4 prereg (§6, from the L2 Courant probe) is **superseded** by L4's own
measured R3 rate, which ran ~3× cheaper per unit endTime than that probe (the probe was
a different, more expensive configuration). **The honest uncertainty is that no N=240
DMR run has EVER reached t=0.2** — the final ~23% of sim-time (t=0.155→0.2) is
unmeasured territory, and the clip could raise per-step cost if it fires on many cells
or slows the energy `smoothSolver`. Retaining 100 (rather than tightening to, say, 60)
**absorbs that extrapolation risk** while giving no room for an unbounded overrun. A cap
above 100 is therefore **not justified** by the measured anchor.

### 6c. Dollars — DERIVED, NOT MEASURED
At c7a.4xlarge **$0.0513/core-h** (owner-stated; the box cannot read its own billing —
`COMPUTE_BUDGET_CHARTER.md` §5):
- family point estimate 40 core-min = 0.667 core-h × $0.0513 = **$0.0342 DERIVED**;
- one-time build ~2 core-min = 0.033 core-h × $0.0513 = **$0.0017 DERIVED**;
- the 100-core-min cap = 1.667 core-h × $0.0513 = **$0.0855 DERIVED**.

All well under the $25 CPU pre-authorised ceiling. A calibration row (estimate vs
actual, `docs/COST_CALIBRATION.md`) is owed at completion (rule 12). The build boundary,
not the cost, is what makes this Sanaa's call (rule 9: a blanket is not a per-item read).

## 7. FALSIFIABLE PROPOSITIONS — what each outcome means for the measured-capability question

Stated before any run (rule 2). A "completing" level means the strict completion rule
(rule 4) holds: `rc=0`, an `End` line, last time == `endTime = 0.2`, required fields
present, age guard satisfied.

1. **WORKS.** The R1'/R2'/R3' triple all **complete to t = 0.2 at their grids** AND the
   triple is **`CONVERGING`** (rule 5) AND every level PASSES Gate V' inside `0.0231`.
   → The DMR crash **was** the diagnosed cell-centre T-positivity failure at
   `rhoCentralFoam.C:136`, and a bounded-energy update cures it **while preserving
   shock-position accuracy**. The lab has a defensible 1/240 Mach-10 DMR result under a
   named, hash-pinned lab solver. **Measured-capability answer: YES** — a positivity
   clip on the vanilla family carries the DMR to 1/240. (L4's R1/R2 already PASSED Gate
   V' with margin under these numerics, so a completing R3' has a genuine, not nominal,
   shot at PASS.)
2. **GATE-FAIL-on-accuracy.** R3' (and/or the triple) **completes** but the triple
   exceeds tol `0.0231`, or is non-monotone / `STAGNANT`. → The clip's non-conservative
   energy injection at the wall foot **displaced the shock** or masked the formal order.
   This is a **REAL robustness-vs-accuracy trade result** (completion bought at the cost
   of conservation), **NOT a widening** — the tolerance was held byte-identical.
   **Measured-capability answer:** the clip enables **completion but not an accurate**
   1/240 result → motivates a **conservative** positivity-preserving scheme as a further
   rung, not a capability-exhaustion claim.
3. **STILL-CRASHES.** R3' **SIGFPEs again** (rc=136) despite the clip. → The fault is
   **not (solely)** a cell-centre post-update negative-`e` at line 136: either the
   negativity lives on a **reconstructed FACE** (`rhoCentralFoam.C:137/143`) that a
   cell-`e` clip does not directly set, or the clip induces an energy-pumping
   limit-cycle that diverges elsewhere. This is the **measured insufficiency of the
   cell-`e` clip** (a negative result) → next rung a **face-level** positivity-preserving
   reconstruction / flux. **Under L-501 this is NEVER a capability-exhaustion finding
   from one or two SIGFPEs**, and is reported not softened.

**On capability exhaustion.** Only after L5 **and** any face-level successor are
MEASURED can the tooling finding — "the vanilla `rhoCentralFoam` v2606
numerics-robustness levers, even with a cell-energy positivity clip, do not carry a
Mach-10 DMR to 1/240" — become defensible. L5 is a **necessary rung** toward (or away
from) that finding; it is not itself the finding.

## 8. RUN ROOTS — DECLARED ABSENT (rule 2 / rule 4)

`verification/runs/DMR_R3_L5_BOUNDED_T_runs` — **confirmed ABSENT at
2026-09-08T18:10Z**. The (to-be-authored, post-go) driver's rule-4 guard must refuse
each level whose case dir already exists; the family writes into a fresh self-contained
root only. The solver-source dir
`verification/runs/DMR_runs/rhoCentralFoamBoundedDMR_src/` does not yet exist and is
created only after Sanaa's go.

## 9. WHAT IS AND IS NOT DONE IN THIS DRAFT

- **DONE (read-only, on disk):** the base solver (`rhoCentralFoamBounded_src`) read and
  its clip site confirmed (`e = min(max(e, eMin_bound), eMax_bound)` before
  `thermo.correct()`); the DMR thermo constants read from the L4 case
  (`Cp 2.5`, `molWeight 11640.3` ⇒ `Cv 1.785717`, `γ 1.4`); ambient `T = 1.0` derived;
  the grader identity confirmed on disk (blob `52aacf96…`, `GATEV_TOL 0.0231` at `:69`);
  the frozen parent tolerance quoted (`DMR_PREREGISTRATION.md:88,:91`); the L4 measured
  cost figures transcribed; the run root confirmed absent.
- **NOT DONE (crosses the boundary — awaits Sanaa's go):** authoring the
  `rhoCentralFoamBoundedDMR` source, `wmake`, the generator/driver, the freeze,
  the queue row, and any launch. **No compute of any kind was run for this draft.**

---

**DRAFT — NOT FROZEN, NOT AUTHORISED — solver-build boundary, awaiting Sanaa's go.
Nothing is sent, filed, uploaded, registered or posted (rule 7). No gate, threshold,
band, cap or label is set by this draft to anything other than the frozen parent's
values; Gate V' tol `0.0231` and `x_exact 2.99568` are transcribed byte-identical and
NOT widened.**
