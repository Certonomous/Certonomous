# VMFL003-M2 — "Try Other Models": PRE-REGISTRATION **DRAFT** (NOT FROZEN)

**NOT FILED ANYWHERE.** Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box (CLAUDE.md
rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The manual is proprietary Ansys
documentation. **SUBMISSIONS PARKED.**

**THIS IS A DRAFT. IT IS NOT FROZEN, IT IS NOT THE GRADING PATH, AND IT AUTHORISES NO
COMPUTE.** It is written by `ansys-lane-opus48` (Opus 4.8) on 2026-08-25 for the
`ansys-verification-supervisor` to read, correct and — only then, and only by the
supervisor personally — freeze. **No agent message is Sanaa's consent** (rule 9); the
freeze and the launch are the supervisor's own acts after the four `SUPERVISION_CHARTER`
§3 checks. Until frozen, this file may be edited freely; once frozen, only dated addenda.

**ZERO COMPUTE HAS RUN FOR VMFL003-M2.** Checked in the drafting invocation at
**2026-08-25T16:02:46Z** (`date -u`): `verification/runs/ansys_verification/VMFL003_M2/`
**does not exist** (`ls -d` → *No such file or directory*), and no `VMFL003_M2` case
directory existed before this draft. HEAD at drafting: **`2f6d8edf0afc31f5e2b063735a0a9bf9303d1a35`**.
The run tree's absence is the load-bearing check; the fleet is invisible to `pgrep` (L-41).

**Provenance of the directive.** Sanaa, 2026-08-25, byte-exact: *"VMFL051 and VMFL003
try other models"* and, as a general rule, *"When a model doesnt work, try the other
ones"* (spelling hers, quoted as the authority). This draft executes that directive for
VMFL003 under the supervisor's binding guard: **each model attempt is a separately
frozen registration with the turbulence model as the registered variable under test;
every attempt is recorded whatever its verdict; the full slate is declared UP FRONT in
fixed order and ALL declared attempts are run and reported regardless of what the first
returns; each model's "wrong" is defined in advance; and nothing but the model changes,
or a coupled change is declared with its cost to interpretation.** Cycling models until
one clears the gate would poison every credential this register holds; this draft is
structured to make that impossible.

**Relationship to run 1.** Run 1 of VMFL003 (`kEpsilon` + `nutkWallFunction`) returned
**`NOT A RESULT`** (rule 5 step 1: all three levels failed the residual leg) with a
pre-rule-5 gate verdict of **`GATE FAIL`** (Δp = 20800.82 Pa, **−4.34 %** vs the manual
target 21744 Pa; **−4.55 %** vs Colebrook 21792.88 Pa; f_dev −4.63 %). **Run 1's frozen
`PREREGISTRATION.md`, its comparator `grade_vmfl003.py` and its `RESULTS.md` are NOT
edited, cleared or re-labelled by this draft, and none of run 1's run-tree artifacts is
touched.** This is a NEW case id (`VMFL003_M2`) with its own case tree, its own
comparator blobs and its own register rows.

---

## 0. WHAT RUN 1 ESTABLISHED, AND WHAT IT DID NOT — read before the slate

Run 1's two findings are **separate defects** and must not be conflated:

**Defect A — the MODEL-LEVEL miss (substantive).** Δp is **−4.34 %** low against the
manual and **−4.55 %** against closed-form Colebrook — nearly identical deviations, so
it is *not* a 3-s.f. chart-read artefact of the target. The developed-region friction
factor f_dev = 0.027147 is **−4.63 %** below Colebrook, free of entrance and BC effects:
**this lab's `kEpsilon` + `nutkWallFunction` genuinely under-predicts developed turbulent
pipe friction by ~4.6 % at Re = 1.37×10⁴.** Δp is converged to **7.8 ppm** (L2→L3 moved
0.161 Pa) while the wall-treatment ladder (N_r = 3/4/5/6) moves it **1.7356 %** — the
model/wall channel is ~2200× the axial-discretisation channel. **This is the defect
"try other models" is aimed at.**

**Defect B — the ITERATIVE-CONVERGENCE miss (procedural, SEPARATE, must not be buried).**
All three levels failed the registered residual leg (final initial residuals of p, Ux,
k, ε each < 1.0e−8): L1/L2 failed 4 of 4; L3 failed on **ε alone** (2.523e−8 vs 1e−8, by
2.5×). This is *why* the verdict was `NOT A RESULT` rather than `GATE FAIL`. **It is a
consequence of run 1's iteration counts (6000/8000/12000) being too short — run 1's §4.5
declared them ESTIMATES and its §7c/§11-item-5 registered the exact repair: re-run at a
longer endTime as a NEW RUNG.** Defect B is *not* the model's fault and a longer run
fixes it — but run 1's own RESULTS states that a converged kEpsilon would then return
**`GATE FAIL`, not `PASS`**, because Δp is already converged to 5 significant figures at
−4.34 %. **Fixing Defect B does not fix Defect A.** See §5 for why fixing B is *not* a
confound with the model change.

**What I believe is imperfect in run 1's frozen registration (reported, NOT edited):**

1. **The y⁺ clause binds only the AVERAGE, leaving the MINIMUM unbound.** §5/§6 of run 1
   gate mean wall y⁺ ∈ [25, 65]. At L3 the mean was 37.60 (held comfortably) but the
   **minimum** was **23.812**, below the band floor — a few near-inlet faces sat below
   y⁺ = 25. Run 1 disclosed this honestly and volunteered it rather than burying it, and
   the comparator was correct against its frozen clause. But a clause on the average
   alone can accept a mesh with faces in a regime the wall function is not valid for.
   **I judge this worth correcting for M2** — see §6, where I bind the minimum at the
   physically correct floor (the `nutkWallFunction` yPlusLam log-law crossover, 11.06),
   which would have **held** in run 1 and is therefore not answer-directed.
2. **The Roache triple's design cannot reliably yield an observed order for this
   quantity.** Run 1's §4.3/§6 predicted level-to-level Δp differences of **6–45 Pa**;
   the actual differences were **0.16 and 2.01 Pa** — the triple differenced values
   agreeing to five significant figures and returned **p = 3.64**, which run 1's RESULTS
   correctly refused to read as a real convergence order. This is inherent: Δp is
   dominated by the developed region where axial pressure is linear and mesh-exact, so
   axial refinement at fixed N_r barely moves the gate quantity. **This weakness carries
   into M2** (§7); it is a limitation of the quantity+family, not an error, but it means
   the substantive M2 output is the **gate verdict at L3**, with the triple reported
   honestly and its order interrogated, never presented as evidence the numerics are
   healthy.
3. **The k-ε cost multiplier of 1.6 was wrong** (measured aggregate implied ~2.66, itself
   confounded by a small-mesh overhead floor). Run 1's RESULTS reports this. M2's cost
   (§8) uses run 1's **measured** aggregate rate 5.806e−6 s/(cell·iter) instead, which is
   the honest calibration.

None of these is a reason to touch run 1's frozen files; all three are carried forward
as corrections or acknowledged limitations here.

## 1. THE INSTALLED MODEL SLATE — read from the library, not recalled

The selectable incompressible RAS model names were read from the installed OpenFOAM
**v2606** source at `/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/` — the
`makeRASModel(...)` instantiations compiled into the incompressible momentum-transport
library that `simpleFoam` links (`incompressible/turbulentTransportModels/`), **not from
memory**:

**Templated (instantiated for incompressible):** `SpalartAllmaras`, `kEpsilon`,
`RNGkEpsilon`, `realizableKE`, `LaunderSharmaKE`, `kEpsilonPhitF`, `kOmega`, `kOmegaSST`,
`kOmegaSSTSAS`, `kOmegaSSTLM`, `LRR`, `SSG`, `EBRSM`, `GEKO` (+ DES/DDES/IDDES hybrids,
not RANS).
**Incompressible-only nonlinear (self-registering `addToRunTimeSelectionTable`):**
`LienCubicKE`, `kkLOmega`, `ShihQuadraticKE`, `LienLeschziner`, `LamBremhorstKE`,
`qZeta`.
**Available nut wall functions:** `nutkWallFunction` (run 1), `nutUSpaldingWallFunction`,
`nutUWallFunction`, `nutUBlendedWallFunction`, `nutLowReWallFunction`,
`nutkRoughWallFunction`, `nutURoughWallFunction`, `nutUTabulatedWallFunction`.

The `epsilon`/`omega` wall functions (`epsilonWallFunction`, `omegaWallFunction`) and
`kqRWallFunction` for k are present in the same tree.

## 2. THE DECLARED SLATE, IN FIXED ORDER — ALL RUN, WHATEVER EACH RETURNS

The slate is fixed **now**, before any M2 number exists. **Every model below is run and
recorded; none is dropped after seeing a number** (a model dropped after a number is
answer-directed selection and is forbidden). The order is fixed and does not encode a
preference for any outcome.

| # | rung id | RASModel | 2nd transport var | wall fn | comparator | change vs run 1 |
|---|---|---|---|---|---|---|
| **M2-A** | `VMFL003_M2_A_kEpsilon` | `kEpsilon` | ε | `nutkWallFunction` | frozen run-1 comparator, byte-identical | **only endTime** (→ converge; NEW RUNG per run-1 §7c) |
| **M2-B** | `VMFL003_M2_B_realizableKE` | `realizableKE` | ε | `nutkWallFunction` | frozen run-1 comparator, byte-identical | **only RASModel keyword** |
| **M2-C** | `VMFL003_M2_C_RNGkEpsilon` | `RNGkEpsilon` | ε | `nutkWallFunction` | frozen run-1 comparator, byte-identical | **only RASModel keyword** |
| **M2-D** | `VMFL003_M2_D_kOmegaSST` | `kOmegaSST` | **ω** | `nutkWallFunction` + `omegaWallFunction` | **omega-family variant** (see §3) | RASModel **+ coupled ε→ω** (declared confound) |

**Justification per model — why THIS model, and what it tests:**

- **M2-A `kEpsilon` (baseline, converged).** The same model as run 1, re-run only long
  enough to clear Defect B. It is the **control**: it discharges the residual-convergence
  defect and gives a clean *converged* kEpsilon Δp so the other three are compared
  model-to-model at the same converged state, not against a `NOT A RESULT`. Run 1's own
  RESULTS predicts this returns **`GATE FAIL` at ~−4.3 %**; M2-A tests that prediction.
  Without M2-A, any movement in B/C/D could be confounded with the convergence fix.

- **M2-B `realizableKE`.** The most common next step when standard k-ε mispredicts:
  Shih's realizable model makes C_μ variable and reformulates the ε source to satisfy
  realizability and improve strained/separated flows. It shares fields (k, ε) and the
  **identical wall function**, so the frozen comparator grades it byte-identical.

- **M2-C `RNGkEpsilon`.** RNG adds the strain-dependent R term to the ε equation
  (effective C₂), altering the near-wall dissipation balance. Fields (k, ε), identical
  wall function, frozen comparator byte-identical.

- **M2-D `kOmegaSST`.** The other industry workhorse and the model most likely to move
  wall friction, because its ω-based near-wall treatment and eddy-viscosity limiter
  compute the wall shear on a different basis than the ε log-law wall function. It is the
  **strongest physical test of whether the ~4.6 % deficit is a wall-treatment artefact**.
  It is included **despite** requiring a coupled change (§3), precisely because dropping
  the most informative model to avoid a comparator variant would be answer-directed in
  the opposite direction.

**Considered and DEACTIVATED FROM THE COMMITTED SLATE, with reasons stated so the slate
is bounded and nothing is silently dropped:**

- `LaunderSharmaKE`, `LamBremhorstKE`, `kkLOmega`, `kEpsilonPhitF`, `nutLowReWallFunction`
  paths — **low-Reynolds / integrate-to-the-wall** models. They require y⁺ ≈ 1 near-wall
  resolution and **no** wall function, i.e. a **completely different mesh** (N_r ~ 40–80,
  first cell in the viscous sublayer). That is a mesh + wall-treatment confound of the
  largest kind. It is a legitimate *separate* case (a future `VMFL003_M3`, low-Re family)
  but it is **not** a "change the model and nothing else" attempt and is excluded here to
  keep M2's variable clean.
- `SpalartAllmaras` — one-equation, transports `nuTilda`, needs a different wall approach
  (`nutUSpalding`/low-Re). Field-set and wall-treatment confound; deferred to M3.
- `LRR`, `SSG`, `EBRSM` (Reynolds-stress), `GEKO`, `kOmegaSSTSAS/LM`, nonlinear
  `LienCubic/Shih/Lien` — either transport six stress components / extra scalars (large
  confound and convergence burden on a wall-function pipe) or are tuned/transition models
  outside the "standard turbulence model" reading of the directive. Deferred; naming them
  here keeps the exclusion explicit rather than silent.

**The bound.** The committed M2 slate is exactly **{A, B, C, D}**. Extending it is a
supervisor decision made *before* freeze, not a lane decision made *after* a number.

## 3. THE ONE COUPLED CHANGE (M2-D), DECLARED WITH ITS COST TO INTERPRETATION

`kOmegaSST` fundamentally transports **ω**, not **ε**. The frozen run-1 comparator
hard-codes `epsilon` in `FIELDS_REQUIRED` (line 160) and in the residual leg
`gated = ["p","Ux","k","epsilon"]` (line 399), so it **cannot** grade an ω run — it would
refuse (field `epsilon` absent) or mis-check the residual leg. M2-D therefore requires,
**and only requires**, the following coupled changes, each named:

1. `constant/turbulenceProperties`: `RASModel kOmegaSST`.
2. `0/epsilon` → `0/omega` (with `omegaWallFunction` on `walls`); `epsilonWallFunction`
   removed, `omegaWallFunction` added. **`nut` stays `nutkWallFunction`** (it is built
   from k and works for both families), so the wall *treatment for nut* is held constant;
   what changes is the near-wall length-scale variable.
3. `system/fvSolution`: solver regex `"(U|k|epsilon)"` → `"(U|k|omega)"`.
4. `system/fvSchemes`: `div(phi,epsilon)` term → `div(phi,omega)`.
5. **A model-family comparator variant `grade_vmfl003_omega.py`**, identical to the frozen
   run-1 comparator **except** `FIELDS_REQUIRED = ["U","p","k","omega","nut"]` and
   `gated = ["p","Ux","k","omega"]`. **Every gate, band, reference value, threshold, and
   all three planted-zero plants are byte-identical** (they read p-monitors, yPlus and
   slab-p — none is model-specific). This variant is frozen and hashed like any grading
   path; its `--selftest` must pass before M2-D runs.

**Cost to interpretation, stated plainly.** For M2-D the ε→ω change is **not a nuisance
confound to be regretted — it is partly the very thing under test** (the near-wall
length-scale treatment is a leading suspect for Defect A). But it means M2-D's movement
relative to M2-A cannot be attributed to "the interior closure" alone; it is the
*combined* interior+near-wall-variable effect. M2-B and M2-C isolate the interior effect
at fixed wall treatment; M2-D adds the near-wall-variable effect on top. That decomposition
is registered now, before the numbers, so it cannot be reverse-fitted later.

## 4. THE GATE, BAND AND DIAGNOSTICS — PROPOSED **UNCHANGED** FROM RUN 1

> **G-VMFL003-M2 (per model, at the finest level `L3_1000x5`):**
> **|Δp_lab − 21744| / 21744 ≤ 0.025 (2.5 %)**. Inside ⇒ gate met; outside ⇒ `GATE FAIL`.
> Δp_lab = ρ·(areaAverage(p)_inlet − areaAverage(p)_outlet), ρ = 1.225, from the two
> `surfaceFieldValue` monitors, exactly as run 1.

**Diagnostics, unchanged, printed never gated:** Colebrook DP_COLEBROOK = 21792.88 Pa at
2.0 %; developed-region f_dev vs F_COLEBROOK = 0.028464 at 2.0 %.

**Why UNCHANGED — and why a changed band here would be the poison the guard names.** The
reference (manual target 21744 Pa) is fixed by `ANSYS_VERIFICATION_CHARTER.md` §5.1 as
"the reference result as the manual states it"; it does not depend on which turbulence
model the lab runs. Run 1's §3.4 derived the 2.5 % band from a **model-independent** error
budget — the target's 3-s.f. chart-read (±0.176 %), the entrance excess (+0.28…0.70 %),
the wedge azimuthal bias (+0.095 %) — and from the manual's **own** Fluent–CFX spread of
**1.210428 %** on this exact case, deliberately sized to **PASS both Ansys solvers**. None
of that changes when the lab swaps closures. **Run 1 failed this band at −4.34 %, i.e. by
3.6× the band; widening the band for M2 so that a −4.3 % answer could "pass" would be
gating the answer, not the physics — exactly re-running until the answer is liked.** The
band therefore stays 2.5 %, and the Colebrook/f_dev diagnostics stay 2.0 %. A model that
truly reproduces the manual will clear 2.5 % on its own; one that does not is a `GATE FAIL`
row that stays in the register honestly. (Run 1's §3.4 offered the supervisor the option to
*tighten* to 2.0 % at freeze; that option remains, and tightening — never loosening — is
the only defensible direction if the supervisor wants a stiffer bar.)

## 5. THE ADVANCE DISCRIMINATOR — what counts as each model being WRONG, frozen before the number

The point of "try other models" is to learn whether *any* installed closure recovers the
~4.6 % friction deficit. Two registered discriminators, per model, frozen now:

**Discriminator 1 — the gate (reproduction).** A model **reproduces the manual** iff its
L3 Δp is inside ±2.5 % → `PASS`. A model **fails to reproduce** iff outside → `GATE FAIL`.
This is the credential-bearing line and is identical for all four.

**Discriminator 2 — f_dev, the clean model statement (mechanism).** Run 1's kEpsilon gave
**f_dev = 0.027147** (−4.63 % vs Colebrook). A model has **materially moved the wall
friction** iff its L3 f_dev differs from **0.027147** by more than **1.0 %** (a threshold
set at ~60 % of run 1's measured wall-channel ladder spread of 1.7356 %, so it is above the
wall-cell-placement noise but well inside the gate band). Frozen predictions, each of which
a number can falsify:

- **M2-A (kEpsilon converged): PREDICTED `GATE FAIL` at −4.0…−4.6 %, f_dev within 0.3 % of
  run 1's 0.027147.** *Wrong if* the converged answer lands inside ±2.5 % — that would mean
  Defect B (not the model) drove run 1's miss, contradicting run 1's 7.8-ppm convergence
  evidence. Registered as the strongest single check on run 1's own story.
- **M2-B (realizableKE) and M2-C (RNGkEpsilon): PREDICTED to stay `GATE FAIL`, within ~1 %
  of M2-A on both Δp and f_dev.** The mechanistic reason, frozen now: with a **standard
  log-law wall function**, the wall shear τ_w is imposed by the log law from the first-cell
  k, **not** computed from the interior closure; high-Re k-ε variants that share the wall
  function therefore share most of their wall friction. *Wrong (and the surprising,
  reportable result) if* either lands inside ±2.5 %, or moves f_dev by >1 % from M2-A —
  that would falsify the "wall function dominates the friction" hypothesis and would be the
  finding of the exercise.
- **M2-D (kOmegaSST): the OPEN test — no directional prediction is registered, deliberately.**
  Its ω-based near-wall treatment can compute τ_w on a different basis, so it is the model
  most able to move friction. Two pre-registered readings: **(a)** if D lands inside ±2.5 %
  (or moves f_dev >1 % toward Colebrook), **the near-wall length-scale treatment was a
  material cause of the deficit** — a real, mechanism-locating result; **(b)** if D stays at
  ~−4.5 % like A/B/C, **the deficit is deeper than any wall-function/closure choice
  available on this mesh** and is a property of high-Re wall-modelled RANS of this pipe at
  Re = 1.37×10⁴ — an honest, non-credential finding. Both are registered; neither is "the
  liked answer".

**The whole-exercise discriminator, frozen now.** If **all four** cluster at −4.0…−5.0 %
(all `GATE FAIL`), the registered conclusion is: *this lab's wall-modelled RANS, with a
standard log-law wall function on an R⁺ = 408 pipe, under-predicts turbulent pipe friction
by ~4.5 % at this Re independent of the two-equation closure* — recorded as a `GATE FAIL`
slate, **not** softened, **not** a credential, and drafted for `N-AV`/`LESSONS`. That this
outcome is written down **before** the runs is what keeps the slate honest.

**Why fixing Defect B is NOT a confound with the model change.** The invariant held
constant across all four attempts is the **convergence criterion** (final initial
residuals of p, Ux, k, {ε|ω} each < 1.0e−8; plateau peak-to-peak ≤ 1.0e−2 Pa), which is
**identical to run 1's**. Only `endTime` varies — per level and per model — to *reach*
that fixed criterion. Every graded Δp is therefore read at the **same converged state**.
A confound would arise only if answers were compared at *different* convergence states;
they are not. endTime is not the registered variable and is not a discriminator; the
residual clause is the arbiter, exactly as in run 1. A level that misses either leg is
`NOT A RESULT` and re-runs longer as a NEW RUNG (run 1 §7c), moving no gate, band, cap or
label.

## 6. THE y⁺ CLAUSE — corrected so the MINIMUM is bound, not only the average

Fixed N_r = 5 at every Roache level (run 1 §4.2's R⁺ = 408 constraint is unchanged: a
ratio-2 *radial* triple cannot fit the log layer below Re ≈ 21252, so the triple refines
**axially** and holds N_r fixed; the wall treatment is then identical at every level).
Predicted first-cell y⁺ from Colebrook u_τ is **40.835**, mid-window.

**Primary clause — UNCHANGED from run 1:** mean wall y⁺ at endTime ∈ **[25, 65]** →
one-way `NOT A RESULT`. Unchanged because the band came from the same R⁺ = 408 log-layer
window and the same fixed N_r = 5, neither of which M2 alters; changing it would need a
non-answer-directed reason I do not have.

**NEW clause — the minimum is bound:** minimum wall y⁺ at endTime ≥ **11.06** → one-way
`NOT A RESULT`. **11.06 is the `nutkWallFunction` `yPlusLam` log-law crossover**: below it
OpenFOAM's own wall function abandons the log law and returns the laminar value, so a face
below 11.06 is a face the standard wall function is *not* validly modelling. Run 1's L3
minimum was **23.812**, which clears 11.06 comfortably — **this clause would have HELD in
run 1**, which is exactly why it is not answer-directed: it makes explicit what run 1 only
volunteered as a caveat, without retroactively failing run 1's mesh.

**Both clauses are validity guards, not discriminators.** Different models produce slightly
different u_τ and hence different y⁺ on the same mesh; the clauses are set wide enough
(mean band 2.6× wide; min floor at the physical crossover) that a model with legitimately
lower friction is **graded**, not knocked to `NOT A RESULT` by the y⁺ guard — otherwise the
guard would hide the very Δp the exercise exists to measure. For M2-D (`omegaWallFunction`,
which blends continuously rather than switching at a hard yPlusLam), the same numeric floor
of 11.06 is used as a conservative validity floor, with the note that ω blends rather than
cuts.

## 7. THE ROACHE QUANTITY, GRID FAMILY AND TRIPLE GATING (rule 5)

**Quantity:** Δp_lab (inlet−outlet, ρ-scaled), identical to run 1. **Grid family:** the
run-1 axial triple at fixed N_r = 5 — `L1_250x5` / `L2_500x5` / `L3_1000x5`, ratio 2 by
construction (each level doubles N_x, so h halves exactly; r = 2 is never inferred from a
cell count). Per model, a fresh triple. GCI at **Fs = 1.25**; a GCI is never quoted unless
the three values are monotone. Triple gating in the frozen order (rule 5): any level not
iteratively converged / not plateaued / outside the y⁺ guards / failing a completion clause
→ `NOT A RESULT`; a triple `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` → `NOT A RESULT`
with the three values, R and increments printed and **no GCI**; `CONVERGING` → `PASS`
inside 2.5 % else `GATE FAIL` with GCI printed. **The gate can only turn a PASS/GATE FAIL
INTO `NOT A RESULT`, never the reverse.**

**Carried-forward limitation (run 1 §0-item-2), registered before the number.** Because Δp
is dominated by the developed region where axial pressure is linear and mesh-exact, the
axial triple again risks tiny level-to-level differences (run 1: 0.16 and 2.01 Pa) and an
**unextractable / implausible order** (run 1 got p = 3.64 from 7.8-ppm differences, which
it correctly refused to treat as a real order). Registered warning, verbatim in spirit from
run 1 §6: **an observed order outside [0.5, 2.5], or a triple whose largest difference is
below ~10× EPS_ABS, is a coincidence to be interrogated and reported as such in RESULTS,
never presented as evidence the numerics are healthy.** The substantive M2 output is the
**gate verdict and f_dev at L3**; the triple certifies convergence where it can and is
reported honestly where it cannot. **A supervisor option, offered not baked in:** coarsen
L1 (e.g. `L1_125x5`) so the entrance is genuinely under-resolved at the coarse level and
the triple carries real axial signal; this changes the M2 grid family (consistently across
all four models, so no intra-M2 confound) and is a freeze-time supervisor call, not a lane
call. My recommendation is to **keep the run-1 family** so M2's wall-channel characterisation
transfers from run 1 unchanged, and to accept the honest triple limitation.

## 8. THE WALL-TREATMENT LADDER (§4.4 of run 1) — run for M2-D only, declared up front

Run 1 measured the wall-cell-placement channel with the ladder D_500x3/4/6 (N_r = 3/4/5/6
at fixed N_x = 500) and found a **1.7356 %** spread with the standard `nutkWallFunction` on
this mesh. **For M2-B and M2-C the ladder is NOT repeated:** they use the *identical* wall
function and mesh, so run 1's wall-channel characterisation transfers; re-measuring would
spend compute to reproduce a known number. **For M2-D the ladder IS run** (D_500x3/4/6 with
`omegaWallFunction`), because its wall treatment differs and run 1's characterisation does
not transfer. **This split is declared here, before any number, and is justified by
physics (same wall fn + same mesh ⇒ same wall-channel), not chosen after seeing a result.**
The one-way clause is unchanged: ladder spread > **5.0 %** → `NOT A RESULT`.

## 9. STRICT COMPLETION (rule 4) AND THE PLANTED-ZERO CONTROLS (rule 3)

**Completion clauses, per level, identical to run 1** except the field list adapts to the
model family: C1 rc=0 (`RUN_RC.txt`); C2 an `End` line; C3 last time == endTime (no
`residualControl`, so exact); **C4 fields present** — `U p k epsilon nut` for A/B/C,
**`U p k omega nut`** for D; C5 ExecutionTime count == endTime; C6 age guard in the
stricter form (every field at endTime strictly newer than the latest mtime in the level's
own `0/`, touched last at launch). The comparator **refuses (exit 2)** on any failed
clause and never grades a partial run. Beyond-rule-4 clauses (all tighter, none looser):
the residual leg, the plateau leg, the two y⁺ guards (§6), the ladder-spread clause (M2-D),
the non-empty patch/cellZone controls, and the three planted-zero controls.

**Planted-zero controls (rule 3), the same three as run 1, byte-identical in every
comparator (they are model-independent):** (1) PLANT_DP = 1.234 into the kinematic
`areaAverage(p)` inlet column, must move the graded Δp by 1.234·ρ = 1.51165 Pa — this is
simultaneously the live test that ρ = 1.225 is applied (a ρ-blind reader sees 1.234 and is
**refused**); (2) PLANT_YPLUS = 7.77 into the yPlus `average` column; (3) PLANT_SLAB = 2.345
into `pSlabA` `volAverage(p)`, moving f_dev by PLANT·ρ·D/(0.80·q). Agreement demanded to
1e−9 absolute; both arms (planted moves, unplanted moves by exactly zero) exercised in
`--selftest`. The omega-family comparator variant (§3) keeps all three plants unchanged.

## 10. COST (rule 12) — estimate, cap, and the honest basis

**Basis: run 1's MEASURED aggregate rate 5.806e−6 s/(cell·iter)** on this box for this
solver family (the run-1 §9.1 k-ε multiplier of 1.6 is **abandoned** — run 1 measured it
wrong; the aggregate rate is the calibrated figure). Serial, RANKS = 1, core-minutes =
wall_s × RANKS / 60. **endTimes are bumped from run 1 to reach the residual floor with
margin** (run 1's counts were too short — Defect B): proposed Roache endTimes
**15000/18000/22000** (L1/L2/L3), ladder **18000** — these are **ESTIMATES carrying MORE
uncertainty than run 1's** (they must clear ε/ω to < 1e−8, which run 1 missed), and the
residual clause, not the count, is the arbiter; a level that misses re-runs longer as a NEW
RUNG.

| rung | meshes | cell-iterations | est. wall s | **est. core-min** |
|---|---|---|---|---|
| M2-A kEpsilon | Roache ×3 | 1.875e7+4.5e7+1.1e8 = 1.7375e8 | ~1009 | **~16.8** |
| M2-B realizableKE | Roache ×3 | 1.7375e8 | ~1009 | **~16.8** |
| M2-C RNGkEpsilon | Roache ×3 | 1.7375e8 | ~1009 | **~16.8** |
| M2-D kOmegaSST | Roache ×3 + ladder ×3 | 1.7375e8 + 1.17e8 = 2.9075e8 | ~1688 | **~28.1** |
| **POINT ESTIMATE (all four)** | 12 meshes + smoke tests | | | **≈ 78.5 core-min** |

**Round the point estimate to ≈ 80 core-min.** **CAP (enforced): 120 core-minutes**
(1.5× the point estimate), as a **running total across all four models and all meshes**,
via `timeout` with `TIMEOUT_S = REMAINING_CORE_MIN·60/RANKS`; **an overrun STOPS the run
and does not get a new budget** (rule 12). Suggested per-model sub-caps that stop that
model: **28 core-min** for A/B/C, **42 core-min** for D. Dollars: 120 core-min = 2.0
core-h × $0.0513/core-h = **$0.1026 DERIVED, not measured** (the box cannot read its own
billing; `COMPUTE_BUDGET_CHARTER.md` §5). Well under the 2026-08-21 $25 CPU blanket — **and
still costed per item; a blanket is not a per-item read** (rule 9). At completion, actual
core-minutes from the logs are compared to this estimate per model and one row per rung is
appended to `docs/COST_CALIBRATION.md` (rule 12); the specific figure to calibrate is
whether the bumped endTimes reached convergence at the estimated cost.

**Run 1's own calibration, for context:** run 1 measured **13.5 core-min against a 9.6
estimate** (ratio 1.406), the gap attributed to misprediction (the k-ε multiplier), not
contention or waste. M2's estimate uses the corrected basis, so its ratio should be closer
to 1.0; the residual risk is the endTime bump.

## 11. WHAT THIS DRAFT DOES NOT DO, AND WHAT NEEDS THE SUPERVISOR

- **It authorises no compute.** No mesh, no smoke test, nothing under `verification/runs/`.
- **It is not frozen and is not a grading path.** The case tree (`case/` with the four
  model configs), the comparator's omega variant (`grade_vmfl003_omega.py`), and the
  launcher for M2 **do not yet exist** and must be built, `--selftest`-ed and committed
  **before** this file is frozen — same order as run 1 (`9fea6a65` before the freeze).
- **Open supervisor calls, before freeze:** (a) whether to tighten the gate to 2.0 %
  (never loosen); (b) whether to coarsen L1 for a signal-bearing triple (§7); (c) whether
  to extend the slate beyond {A,B,C,D} (§2); (d) the exact bumped endTimes (§10). Each is
  a freeze-time decision; none is a lane decision made after a number.
- **The four §3 SUPERVISION checks are the supervisor's, personally:** the comparator
  omega-variant diff read as a diff; crash/refusal triage on the first smoke test; the
  big-claim check on §5's frozen predictions; and the freeze **committed** before compute.

---

**DRAFTED by `ansys-lane-opus48` (Opus 4.8), 2026-08-25, for the
`ansys-verification-supervisor`. NOT FROZEN. NO COMPUTE. `NOT FILED`.**
