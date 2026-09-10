# K0g. Blay–Mergui–Niculae ventilated cavity, TRANSIENT re-formulation to a statistically stationary state: PRE-REGISTRATION

> **FROZEN PRE-REGISTRATION — 2026-09-09.** The gate, thresholds, bands, cost cap
> and verdict label below are FROZEN; the grading path is pinned by git-blob sha1
> in §7.7 and verified by `scripts/check_comparator_freeze.py`. Per standing rule 2
> no departure may alter a gate, threshold, cap or label — only dated addenda that
> cannot, with the original struck never rewritten (rule 6). The heat-transfer
> supervisor's non-delegable §3 checks — the measurement-script code-diffs and the
> freeze decision — were performed before this freeze, and the verification
> supervisor gave the clause-5 sign-off for `mark_done_k0g.py`. As of this freeze
> no K0g compute has occurred and no K0g run tree exists (freeze precedes compute).

**Predecessor: `K0f` (explicit, for §2ay linkage).** K0f graded **all ten arms
`NOT A RESULT`** — no level met the §7.1 steady-convergence criterion — and the
ONE registered §7.1 extension (+20 000 iterations, 40 000 → 60 000) **failed to
close the gap** (`K0f_RESULTS.md` §E4: arms sit 1 193× to 727 875× their
criterion; §E5 invokes §8.2 item 4, no second extension exists). **K0g is a
registered METHOD change, not more iterations.** Under §2ay this maps K0f's
`NOT A RESULT` to **state (b): a dated successor**, never state (a) a capability
gap — the barrier is the *method* (a steady solver on a flow with no steady
fixed point), and the method is what K0g changes.

---

## 0. THE PIVOTAL FINDING THIS RUNG IS BUILT ON

**At `Ra = 2.135970e9` (height-based, `ΔT = 20.0 K`; the value DERIVED and
carried unchanged from `K0f_PREREGISTRATION.md` §1) the cavity flow is deep in
the TURBULENT regime and a STEADY fixed point is not physically expected. A
steady SIMPLE solver cannot converge to a steady state that does not exist. That
is a MODEL/METHOD barrier, not an iteration count.**

Evidence, from inbound research (papers title-page-verified per standing
rule 15, and OpenFOAM practice):

| source (verified) | Ra | finding relevant to K0g |
| --- | ---: | --- |
| Ampofo & Karayiannis 2003, *IJHMT* **46**:3551–3572 (title p. verified) | 1.58e9 | air-filled square cavity is **turbulent**; benchmark data are **time-mean + fluctuations** — a statistically stationary average, not a steady field |
| Tian & Karayiannis 2000, *IJHMT* **43**:849–866 (title p. verified) | 1.58e9 | same cavity, "**low turbulence natural convection**"; mean and turbulence quantities measured — again a time-average |
| Betts & Bokhari 2000, *IJHFF* **21**:675–683 (title p. verified) | 0.86e6, 1.43e6 (width) | tall cavity core is "**fully turbulent**"; benchmark is mean + turbulent statistics |
| OpenFOAM practice (web, Sept 2026) | 1e7–0.8e8 | `buoyantBoussinesqSimpleFoam` is normally applied at **Ra ≈ 1e7–0.8e8**; K0f's Ra 2.14e9 is **~30× above** that steady ceiling; convergence "becomes increasingly difficult" and steady solutions "may not exist" at elevated Ra |
| differentially-heated-cavity literature (web, Sept 2026) | ~1e9 | at Ra ~1e9 the flow **transitions to unsteadiness** (Rayleigh–Bénard-type instability of the stratified core → oscillating transverse rolls); **steady RANS is "generally inadequate"** and **statistical / time averaging is required** |

**K0f's own measured signature confirms it is a LIMIT CYCLE, not slow
convergence.** `K0f_RESULTS.md` §5/§E4: the field wanders by **0.024–14.5 K**
between checkpoints and did **not decay** over +20 000 iterations (the best arm
`M2_f` improved only 5.85× and still sits 1 193× its criterion; several arms
static or worse). Contrast the T3 repair chain the supervisor cited
(`T3f_RESULTS.md` §1): there `|U|` **decayed geometrically** at a factor 0.842
per interval — a real steady state existed and more iterations reached it. **K0f
shows no such decay.** The laminar arm `C_lam` is the *worst* performer
(727 875×): a laminar model has **no steady solution at all** at Ra 2e9, which is
the cleanest single proof that the barrier is physical, not numerical.

**Therefore the registered method change is (b): switch to the TRANSIENT solver
`buoyantBoussinesqPimpleFoam` and grade a STATISTICALLY STATIONARY TIME-AVERAGE**,
not a steady fixed point. Path (a) — under-relaxation / scheme tuning of the
steady solver — is **rejected on the evidence**: two SIMPLE runs (base + ext1,
2 124 core-min total) already measured a persistent limit cycle; relaxation
tuning reduces limit-cycle amplitude but the standard high-Ra buoyant-cavity
outcome is residual stagnation; and no relaxation setting gives `C_lam` a steady
state that does not exist. Path (b) is **robust to both hypotheses**: if the RANS
mean is in fact steady, the transient solution settles and its time-average
equals that steady field (fluctuations → 0); if the mean is genuinely unsteady
(URANS), the time-average is still well-defined and stationary. Either way K0g
can reach a **defensible, gradeable state**, which the steady solver measurably
cannot.

### 0.1 THIS DOCUMENT STATES ITS OWN CEILING, ON ITS FACE

**K0g CANNOT REACH `HOLDS`, AND AS REGISTERED CANNOT REACH THE `G` (GCI) GROUND.**

| ground | reachable on K0g as registered | why |
| --- | --- | --- |
| **`V`** (reference-free verification) | **YES** — this is K0g's job | strict completion (transient-adapted), extraction equivalence, the five guards, achieved `y⁺`, and the **new stationarity criterion** are all measurable without a reference |
| **`G`** (Roache triple / GCI) | **NO** | a triple needs THREE levels; §5 authorises **L1 and L2 only**. No L3 ⇒ no triple ⇒ no observed order ⇒ no GCI. Carried from K0f's own §0 restriction |
| **`P`** (primary reference) | **NO** | Blay, Mergui & Niculae (1992) is **`NOT OBTAINED`** — a separate acquisition matter **on Sanaa's desk** (standing rules 7, 8). No agent obtains it |

**THE BEST VERDICT K0g CAN REACH AS REGISTERED IS `GATE REACHED`, naming both
`P` and `G` unreached.** K0g's *deliverable* is the answer to the barrier
question — **can this case reach a defensible statistically-stationary state at
all** — plus the reference-free `V`-ground evidence and the time-averaged
`G1…G8` station values reported (never graded against `P`). **No band is
widened, and no reference is worked around, to manufacture a pass** — the reachable
grounds are stated, and the unreachable ones are named, exactly as K0f did.

---

## 1. CASE — CARRIED OVER UNCHANGED FROM K0f, EXCEPT THE SOLVER AND THE TIME INTEGRATION

**Geometry, fluid properties, boundary conditions and the derived Rayleigh
number are adopted BYTE-UNCHANGED by citation from `K0f_PREREGISTRATION.md` §1
(and through it `K0d_REREGISTRATION.md` §§1–1.3).** Blay–Mergui–Niculae
ventilated cavity; 2D, `x ∈ [0, 1.04]`, `y ∈ [0, 1.04]`; inlet `x = 0,
y ∈ [1.022, 1.040]`; outlet `x = 1.04, y ∈ [0, 0.024]`; `g = (0, −9.81, 0)`;
`T_ref 298.00 K`, `β 3.3557047e-03 K⁻¹`, `ν 1.569e-5 m²/s`, `Pr 0.71`,
`Pr_t 0.85` (never tuned), `ΔT 20.0 K`, **`Ra 2.135970e9` DERIVED, REPORTED,
NEVER A TARGET**.

**THE ONE PHYSICS-METHOD CHANGE:** solver
`buoyantBoussinesqSimpleFoam` (steady) → **`buoyantBoussinesqPimpleFoam`
(transient)**, present in the installed OpenFOAM v2606 at
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/buoyantBoussinesqPimpleFoam`
(verified on disk at this draft). It consumes the **identical Boussinesq physics,
fields and boundary conditions** — the change is time integration, not the model
of the fluid. `constant/`, `0/` and the mesh are reused unchanged; only
`system/fvSchemes` (ddt scheme), `system/fvSolution` (PIMPLE block) and
`system/controlDict` (transient control + averaging function objects) change.

**Neither `K0f_PREREGISTRATION.md` nor any K0d document is edited by this
document** (standing rule 6).

## 2. REFERENCE — GROUND `P`, UNCHANGED AND NOT TO BE WORKED AROUND

**PRIMARY: Blay, Mergui & Niculae (1992), ASME HTD-213 — `NOT OBTAINED`.**
Obtaining it is from outside the box, **Sanaa's alone** (standing rules 7, 8),
and is **not attempted by any agent**. Every graded reference value is `PENDING`
on it; K0g grades **no row against `P`**. The reachable ground is **`V`**
(reference-free). This is unchanged from K0f §2 and is **not to be worked
around**; a stationary time-average that misses no band is still not a `P` pass.

## 3. QUANTITIES AND BANDS — CARRIED OVER UNCHANGED

**Adopted by citation from `K0f_PREREGISTRATION.md` §3 and §4:** the graded rows
`G1 G2 G3 G4 G5a G5b G6 G7 G8 S1`; the thirteen graded stations; the reported
rows `M0` (Boussinesq model-form floor) and `R1`; the five guards
`HB B I DC MB`; the bands `±1.00 K`, `±0.0570 m/s`, `±0.0208 m`, `±0.104 m`,
`±10 % of |q_ref|`, `EXACT MATCH REQUIRED`; the `y⁺` windows **`≤ 5.0` on L1**
and **`≤ 3.3` on L2**.

**NO BAND IS SET, WIDENED, NARROWED OR REINTERPRETED BY THIS DOCUMENT.** The
graded quantities are evaluated on the **final-window TIME-AVERAGE** (§7.1',
`avg2`), not the instantaneous field — that is the only change, and it is a
change of *what field the same band is read on*, made because the transient
solution has no instantaneous field to read. A band read on a time-average is
grading the same physical mean the reference reports; it is **not** a widening.

---

## 5. LADDER — L1 AND L2 AUTHORISED, L3 DEFINED AND NOT AUTHORISED

**Serial. `nProcs = 1`. No decomposition** (carried from K0f §5/§6; the launcher
refuses any `--ranks` other than 1). Two levels authorised: **L1 (25 600 cells)
and L2 (50 176 cells)**, the meshes and grading of `K0f_PREREGISTRATION.md` §G.4
reused unchanged. **L3 (98 596) is DEFINED and NOT AUTHORISED** — a Roache triple
is out of scope for a barrier-breaking method rung; adding L3 is a
re-registration (K0g §0.1).

**THE FIVE AUTHORISED ARMS** (a focused feasibility set: does the transient
method reach a stationary state on the representative closures at both levels,
and does it discriminate a model that cannot):

| arm | closure | level | cells | purpose |
| --- | --- | --- | ---: | --- |
| `M1_c` | `kOmegaSST` | L1 | 25 600 | ladder, primary closure |
| `M1_m` | `kOmegaSST` | L2 | 50 176 | ladder, primary closure |
| `M2_c` | `RNGkEpsilon` | L1 | 25 600 | ladder, second closure |
| `M2_m` | `RNGkEpsilon` | L2 | 50 176 | ladder, second closure |
| `C_lam` | laminar | L2 | 50 176 | **DISCRIMINATION CONTROL — predicted NON-STATIONARY (§7.9)** |

**DEFINED AND NOT AUTHORISED in this rung** (deferred to a K0g extension or `K0h`
once stationarity is demonstrated on the five arms above, so the method is proven
before the guard/sweep matrix is re-spent): `B_hi` (ΔT-arbitration guard), `I_hi`
(inlet-turbulence sweep), `M1_m_seed` (seed control), and the L3 pair
`M1_f`/`M2_f`. **Fresh case directories** are used (names may reuse the K0f
labels under a distinct `K0g_runs/` root); the age guard (§7.2) refuses any case
whose `0/` or a time directory already exists, so no K0f field is inherited.

---

## 7. CRITERIA

### 7.1' STATIONARITY — THE NEW INSTRUMENT, REPLACING K0f's STEADY §7.1

**K0f §7.1 demanded `max|Δcell| ≤ 1e-6 × range` of `T` and `U` between
`endTime−4000` and `endTime` — a STEADY-FIXED-POINT demand
(`analyse_k0f.py:1146`), which a limit-cycling flow cannot meet by construction.
K0g replaces it with a STATISTICAL-STATIONARITY criterion on the running
time-average.** The residual is not the instrument; the instantaneous field is
not the instrument; the **windowed time-average** is.

**Buoyancy time scale (registered, from the case, not tuned):**
`U_b = sqrt(g β ΔT H) = sqrt(9.81 · 3.3557047e-3 · 20.0 · 1.04) = 0.8275 m/s`;
turnover `τ = H / U_b = 1.04 / 0.8275 = 1.257 s`.

**Time integration (registered):** `buoyantBoussinesqPimpleFoam`, `ddtScheme
Euler` (bounded, first order — appropriate for driving to a stationary mean),
adjustable time step with **`maxCo = 2.0`**, **`maxDeltaT = 0.05 s`**,
`deltaT (initial) = 1e-3 s`. PIMPLE **`nOuterCorrectors = 2`**,
`nCorrectors = 2`, `nNonOrthogonalCorrectors = 1`, with an **outer-corrector
`residualControl` of `1e-4`** on `p_rgh` and `U` (a per-time-step convergence
floor, not the stationarity test). **`endTime = 60.0 s`** (≈ 47.7 τ).

**Two consecutive windowed averages, produced by a SINGLE OpenFOAM `fieldAverage`
function object `windowAvg` with `restartOnOutput true`, registered before the
run** (one FO whose accumulator RESETS at every write, NOT two overlapping FOs —
the reset makes the window→directory mapping independent of function-object write
ordering; see the construction note below):
- `timeStart 20`, `writeControl writeTime`; with `writeInterval 20 s` the solver
  writes at 20, 40 and 60 s, so the FO emits and RESETS after each write:
- the write at **20.0 s** is the one-sample **`spin-up` of [0, 20.0 s] (≈ 15.9 τ)**,
  **DISCARDED** — averaged over by no graded window and never read;
- **`avg1` = the [20.0 s, 40.0 s] window**, written to the **`40` time directory**;
- **`avg2` = the [40.0 s, 60.0 s] window**, written to the **`60` time directory**
  (the GRADED window);
- each graded window is **≈ 15.9 τ** long — long enough for a statistically
  meaningful mean of a turbulent cavity;
- the FO produces `TMean`, `UMean` (and `TPrime2Mean`, `UPrime2Mean` reported, not
  graded — the resolved fluctuation level) in each written directory.

**Construction note (ITEM-A robustification — NO gate, threshold, window or tol
moved).** This single-FO `restartOnOutput` form REPLACES an earlier draft that used
two overlapping `fieldAverage` FOs (`avg2` listed first, `avg1` second) which relied
on undocumented function-object write ordering to win the shared `t = 40 s` write —
a fragility that could have produced a silent false-stationary result. The numeric
windows (**`avg1` = [20, 40] s at the `40` dir, `avg2` = [40, 60] s at the `60`
dir**) and the tolerances (**`tol_T = 0.020 K`, `tol_U = 0.005 m/s`**) are
**BYTE-UNCHANGED**; only the *mechanism* that produces those windows changed. The
directory→window mapping was smoke-verified in OpenFOAM v2606 before this prose was
written: the `40` dir holds the [20, 40] time-weighted mean and the `60` dir holds
the [40, 60] mean (and NOT the cumulative [20, 60] mean — the reset was confirmed).

**A case is STATIONARY iff, evaluated cell-wise over the whole field:**

```
  max_cell | TMean(avg2) − TMean(avg1) |  ≤  tol_T   = 0.020 K
  max_cell | UMean(avg2) − UMean(avg1) |  ≤  tol_U   = 0.005 m/s   (per component)
```

**Basis of the tolerances, PHYSICAL and registered before the run — NOT derived
from the grading bands** (the bands are `±1 K`, `±0.057 m/s`; a case can be fully
stationary and still miss a band — stationarity is a prerequisite for grading,
not a pass): `tol_T = 0.020 K = 1e-3 × ΔT` — the drift of a well-averaged mean
over ~16 turnover times should be far below the driving temperature scale;
`tol_U = 0.005 m/s ≈ 6e-3 × U_b`. **These are the method's own stationarity floor,
frozen before the run; they are never widened to admit a case.** A case failing
either bound after the one registered extension (§7.1'') is **`NOT A RESULT`** on
stationarity grounds, its measured drift printed beside it — the honest K0f label,
carried.

### 7.1'' THE ONE REGISTERED EXTENSION

**One** extension is registered: `endTime 60 → 120 s`, restarted from the 60 s
field, with `avg1' = [80, 100] s` and `avg2' = [100, 120] s`. **A second is not
authorised** (the K0f discipline, carried). The decision to extend is taken **on
the stationarity-drift numbers alone, never with a graded G-row value in view**.
If an arm still fails stationarity at 120 s, the finding is that the **RANS mean
itself is non-stationary at this Ra** (genuine large-scale unsteadiness a
2-equation URANS closure cannot damp) — and the successor to *that* is a
**re-registration** (longer averaging window, an explicitly-URANS or
scale-resolving formulation, or L3), **not** a relaxation of `tol_T`/`tol_U`.
**A failure disposition written before the failure is a disposition; one written
after is an accommodation** (K0f §G.6, carried).

### 7.2 STRICT COMPLETION RULE (transient-adapted) with the age guard

`rc = 0`; an `End` line; **last time == `endTime`** (60.0 or, after §7.1'',
120.0); the per-closure completion field sets of `K0f_PREREGISTRATION.md` §7.2
present at `endTime` (`kOmegaSST` `T U p_rgh alphat nut k omega phi`;
`RNGkEpsilon` `… k epsilon phi`; laminar `T U p_rgh alphat phi`) **plus** the
averaging outputs `TMean UMean` from `avg2`; a full `ExecutionTime`/time count;
and **every field at `endTime` NEWER than the case's own `0/T`** (the age guard).
`mark_done_k0g.py` **refuses (exit 2)** rather than infer any exemption. `0/T` is
touched **last** at launch; a missing `0/T` **refuses**; a pre-existing `0/` or
time directory **refuses** (no inherited K0f field).

### 7.3 ROACHE TRIPLE GATING — standing rule 5, `Fs = 1.25`, UNREACHABLE here

Carried unchanged and, as at K0f, **unreachable** under L1+L2 only (§0.1, §5).

### 7.4 PLANTED-ZERO CONTROL — standing rule 3, on the TIME-AVERAGE reader

Three plants, carried in kind from K0f §7.4 but planted into the **averaged**
fields the grader actually reads: `P1` `1.234e-03 K` into cell 0 of a COPY of
`TMean(avg2)`, read back through the production scalar reader — **must be SEEN**;
`P2` `1.234e-03 m/s` into the x-component of cell 0 of a COPY of `UMean(avg2)` —
**must be SEEN** by the production vector reader; `P3` a `0.0` plant on a `0.0`
background — **not distinguishable**, as registered. **`analyse_k0g.py` REFUSES
(exit 2) if the reader cannot see the plant** — a zero from a reader not shown
able to see a non-zero is not evidence.

### 7.5 ORDER OF OPERATIONS, and 7.6 NO SELF-GRADING

`check_k0g_mesh.py` → `build_k0g.py --preflight` → `launch_k0g.sh` (transient) →
`mark_done_k0g.py` → `check_k0g_extraction_equivalence.py` (the standing
pre-grading equivalence gate, carried from K0f §V.4, run **on `TMean(avg2)`**) →
`analyse_k0g.py`. **Every comparator is hashed against its committed blob before
analysis; the grading path is fixed at the freeze commit.** No verdict is
assigned by the lane that runs this (K0f §7.6, carried).

### 7.7 THE GRADING PATH — FROZEN BY THE SUPERVISOR (standing rule 2)

The eight instruments below are committed and pinned by git-blob sha1; the
grading path is fixed at GRADING_PATH_FREEZE_COMMIT a257ddf670a037fb2862cde2f072b26d20865770 (the commit
whose tree holds all eight at these blobs). `scripts/check_comparator_freeze.py`
enforces IDENTITY (worktree bytes == HEAD blob), CURRENCY (HEAD blob is a pinned
sha) and COVERAGE (every pinned path judged) on this set.

| instrument | committed git-blob sha1 |
| --- | --- |
| `scripts/analyse_k0g.py` | `409e403d0c648b88d05ca5e06a466c11588ddd8a` |
| `scripts/build_k0g.py` | `4dace6456803c15c5e2a6286f579c254573f2dbc` |
| `scripts/check_k0g_mesh.py` | `39e55f2d4da55943c529257403cfd26190cb41e0` |
| `scripts/mark_done_k0g.py` | `387b8b82b179291d4d7d177d6cc593255fd03914` |
| `scripts/check_k0g_extraction_equivalence.py` | `2506603bc2600028cb2d037d08ff4eba2de795b6` |
| `scripts/check_k0g_instrument_standard.py` | `0196356a0cbcafd7ef992642bac62840ffb73dc4` |
| `scripts/launch_k0g.sh` | `e14de416050c12d6cafe60a6a2bc4ff4d4127a86` |
| `scripts/launch_k0g_selftest.sh` | `f7594e00d9caff1f22c2ecfa4598f0b80de1807f` |

**Self-hash.** This document's integrity after freeze is its own committed
git-blob sha1, recorded in the freeze commit message and re-derivable via
`git rev-parse HEAD:docs/campaigns/F14-cooling-ladder/K0g_PREREGISTRATION.md`;
any change is a standing-rule-6 dated amendment that cannot alter a gate,
threshold, cap or label.

**Ancestry (provenance, NOT pins — 8-hex short shas, and not table rows):**
analyse from analyse_k0f.py 764dedc6; build from build_k0f.py 0881fa08;
check_mesh from check_k0f_mesh.py 587e6693; mark_done from mark_done_k0f.py
f01e3fce; extraction_equivalence from check_k0f_extraction_equivalence.py
31c902de; instrument_standard from check_k0f_instrument_standard.py 8fa5bd22;
launch from launch_k0f.sh 519e8361; launch_selftest from launch_k0f_selftest.sh
c6e60dbd. The K0f instruments are NOT edited (standing rule 6). §3C's no-assert
standard, §3A's consumer-side completeness assertion and §R6's setsid rc-capture
are carried; the launcher's detached and --selftest re-execs invoke `bash "$0"`
so the frozen grading path carries no executable-bit dependency.

### 7.9 REGISTERED PREDICTIONS (prediction-first, before any K0g compute)

- **`P-K0g-1`** — the four turbulent RANS arms (`M1_c M1_m M2_c M2_m`) **REACH
  stationarity** under §7.1' by `endTime` (or by the one §7.1'' extension).
  *Failure mode named:* if the drift stays above `tol_T`/`tol_U` after the
  extension, the RANS mean is non-stationary → re-registration, not a `tol`
  relaxation.
- **`P-K0g-2`** — the discrimination control `C_lam` **DOES NOT reach
  stationarity** (a laminar model at Ra 2.14e9 is grossly under-resolved and has
  no stationary state) → `NOT A RESULT` on stationarity grounds. This is the
  intended discrimination finding: turbulence closure is *required*.
- **`P-K0g-3`** — cost ratio actual/POINT within `[0.8, 1.6]` per arm (transient
  rate is a calibration item, §8).
- **`P-K0g-4`** — the resolved fluctuation `sqrt(max TPrime2Mean)` is **non-zero
  and O(0.1–1 K)** on the turbulent arms (a stationary mean with zero fluctuation
  would signal the averaging window is mis-set or the flow collapsed to steady).

---

## 8. COST, REGISTERED BEFORE THE RUN (standing rule 12)

**Basis:** K0f's OWN MEASURED per-cell-iteration rates (`K0f_RESULTS.md` §6:
L1 3.07–3.26e-6 s, L2 3.18–3.76e-6 s — the honest predecessor-on-identical-mesh
basis, rule 12), scaled by a **transient overhead factor ×1.5** (PIMPLE pressure
solves per outer corrector are dearer than a SIMPLE iteration) → **POINT rate
`4.8e-6 s` per cell-iteration-equivalent**. **Effective iterations per arm** =
`N_steps × nOuterCorrectors`, with `N_steps = endTime / Δt_mean`,
**`Δt_mean = 5e-3 s`** (a conservative registered estimate: the `maxCo = 2`,
bulk-cell estimate gives 1.1–1.5e-2 s; 5e-3 s allows for near-wall Courant
limiting) → `N_steps = 60 / 5e-3 = 12 000`, `× 2 = 24 000` effective iterations.

| arm | cells | eff. iters | **core-min (cells × iters × 4.8e-6 / 60)** |
| --- | ---: | ---: | ---: |
| `M1_c` L1 | 25 600 | 24 000 | 49.15 |
| `M2_c` L1 | 25 600 | 24 000 | 49.15 |
| `M1_m` L2 | 50 176 | 24 000 | 96.34 |
| `M2_m` L2 | 50 176 | 24 000 | 96.34 |
| `C_lam` L2 | 50 176 | 24 000 | **72.25** — 0.75 × the L2 line (no turbulence solve; the calibrated laminar factor, K0f §6) |
| **SOLVER SUBTOTAL `S`** | | | **363.23** |

| instruments, bounded | core-min |
| --- | ---: |
| meshing (L1 + L2, reused/rebuilt) | 2.00 |
| `check_k0g_mesh.py` | 0.50 |
| `mark_done` + `analyse` + `fieldAverage` extraction + selftests | 3.00 |
| extraction-equivalence gate + instrument-standard + launcher selftest | ≤ 2.00 |
| **`I` = instruments, bounded** | **≤ 7.50** |

```
  REGISTERED POINT   = S + I               = 363.23 +  7.50 =   370.73 core-min
  REGISTERED CEILING = 2S + 0.5S + I       = 726.46 + 181.62 + 7.50 = 915.58 core-min
```

**CEILING structure:** `2S` = base run + one §7.1'' extension (physical time
doubled 60→120 s); `+0.5S` contingency for `Δt_mean` proving smaller than
estimated or a slower transient rate; `+I`. **Reaching the CEILING STOPS THE
RUN** with unrun arms named; an overrun does not get a new budget (rule 12).

**PER-ARM HARD STOP: 10× that arm's POINT line, enforced as a wall-clock
`timeout` = `cap_core_min × 60 ÷ ranks`, `ranks = 1`:**

| arm | 10× POINT (core-min) | enforced `timeout` (s) |
| --- | ---: | ---: |
| `M1_c`, `M2_c` | 491.5 | 29 490 |
| `M1_m`, `M2_m` | 963.4 | 57 804 |
| `C_lam` | 722.5 | 43 350 |

A `timeout`-expiry is a **CAP-STOP (rc 124)**, not a crash (K0f §R6.3, carried);
`STATUS.<case>` records `timeout_s` and `wall` so a reader can see whether the
wall clock reached the cap.

**Dollars, DERIVED, NOT MEASURED**, at the owner-reported **$0.0513/core-h**
(`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing):

```
  POINT    370.73 / 60 =  6.179 core-h × $0.0513 = $0.3170
  CEILING  915.58 / 60 = 15.260 core-h × $0.0513 = $0.7828
```

**`cost_basis`:** the per-cell-iteration rate is **MEASURED** (K0f on this box);
the **×1.5 transient overhead, `Δt_mean = 5e-3 s`, `N_steps`, the `nOuterCorrectors`
factor, the 0.75 laminar factor and the ≤ 7.50 instrument bound are NAMED
CALIBRATION ITEMS and none is called measured.** `Δt` is adjustable, so the run's
physical duration (not its step count) is what is fixed; the step count is the
estimate. **Estimate-vs-actual is compared at completion into
`docs/COST_CALIBRATION.md`** (rule 12). Sanaa's blanket lifts the ceiling but
every run is still costed and calibrated (rule 9: a blanket is not a per-item
read).

---

## 9. WHAT K0g DOES NOT ESTABLISH

- **It grades no row against `P`** — Blay is `NOT OBTAINED` (§2); the time-averaged
  `G1…G8` values are **reported, never graded** against a reference.
- **It computes no Roache triple, observed order or GCI** — L1+L2 only (§0.1, §5);
  no number in a K0g record carries a discretisation bound.
- **It is not a validation of the Blay physics** — it answers the *convergence /
  stationarity barrier*: can the case reach a defensible statistically-stationary
  state at all.
- **The model-form-vs-experiment question for the K0c* cavity is OUT OF SCOPE** —
  it is already routed to the closure ladder as a cross-team call and is **not
  re-taken here** (K0g's scope is the method barrier only).
- **If the turbulent arms fail stationarity even after the §7.1'' extension**, the
  finding is genuine RANS-mean unsteadiness and the next step is a
  **re-registration**, not a `tol` relaxation (§7.1'').

---

## 10. §2ay LINKAGE — PREDECESSOR STATE MAPPING

**Predecessor `K0f`: `NOT A RESULT` (all ten arms, no steady state reached) →
state (b) A DATED SUCCESSOR (this document, K0g), a registered METHOD change
(steady SIMPLE → transient PIMPLE + statistical stationarity).** This is **NOT
state (a) a capability gap**: the lab *can* compute this flow; the steady
formulation was the wrong instrument for a flow with no steady fixed point, and
K0g changes the instrument. The chain is
`K0f (steady, NOT A RESULT) → K0g (transient, stationarity gate)`, and K0g's own
ceiling (`GATE REACHED`, `P` and `G` unreached) is stated on its face (§0.1).

---
# DEAD-LEVER DISCLOSURE APPENDIX — 2026-09-10. **DISCLOSURE ONLY. POST-COMPUTE. NO VERDICT CHANGES.**

**THIS APPENDIX EXISTS BECAUSE §7.2 OF THIS FROZEN DOCUMENT REGISTERS CLAUSE 7 AS
A BINDING REFUSAL, AND IT WAS NEVER REACHED.** §7.2 (`:263-265`) reads verbatim:

> *"`0/T` is touched **last** at launch; a missing `0/T` **refuses**; a
> pre-existing `0/` or time directory **refuses** (no inherited K0f field)."*

**That registered refusal had no call site on any K0g launch path.** The sentence
is **not struck and not rewritten** (rule 6) — it registered the right standard,
and registering it was correct. What a future reader needs beside it is that
nothing executed it, and that is what this appendix supplies. **This is the
sharpest instance in the F14 territory of the reader-misleading shape the whole
disclosure is aimed at**, which is why K0g's registration carries it explicitly.

## D.0 RULE 6 COMPLIANCE, VERIFIED RATHER THAN CLAIMED

**lines whose number changed above this section: 0.**

**Verified BYTE-FOR-BYTE IN PYTHON against the `HEAD` blob `df811dab594ed95966c7a0ee407bfadff9f02a69`**, by
asserting `new_bytes[:len(head_bytes)] == head_bytes` over all **26,826** bytes of
the pre-append file, with the differing-byte count asserted `== 0`. **It was NOT
verified with `git diff`**, which in this repository reads the permanently stale
shared index and is not a valid instrument (`ESCALATION_CHARTER.md` §9.6).
The pre-append disk file was first confirmed byte-identical to its `HEAD` blob,
so the prefix property is a statement about the committed record and not merely
about a local file. **This append is pure insertion at the foot: 0 deletions, 0
modifications, 0 renumbered lines.**

**THIS APPENDIX ALTERS NO GATE, NO THRESHOLD, NO BAND, NO CAP AND NO LABEL, AND
COULD NOT ALTER ONE**: it registers no test, computes no number, reads no
artifact and touches no instrument. Standing rule 2 permits it for exactly that
reason.

## D.1 THE FACT BEING DISCLOSED

**Standing rule 4's CLAUSE 7 — the PRE-launch refusal of a case in which `0` or
any numeric time directory already exists — was defined in this rung's
completion instrument and CALLED BY NO LAUNCHER.**

Measured 2026-09-10 by a repository-wide census. Every occurrence of
`launch_guard` / `--launch-guard` in `scripts/mark_done_k0g.py` is **internal to that file**
— definition `:169`, argparse `--launch-guard` `:343`, dispatch `:358-365`, selftest `:528-538` — and there is no occurrence anywhere on a launch path.

**`scripts/launch_k0g.sh` carries 0 occurrences of `launch_guard` or
`--launch-guard`, and 3 occurrences of `mark_done`** (measured 2026-09-10);
`scripts/launch_k0g_selftest.sh`, `scripts/build_k0g.py`, `scripts/analyse_k0g.py`,
`scripts/check_k0g_mesh.py`, `scripts/check_k0g_extraction_equivalence.py` and
`scripts/check_k0g_instrument_standard.py` each carry 0, the last of these while
carrying 5 occurrences of `mark_done`. **Every instrument that knew the grader
existed declined to pull this one lever, and could not have pulled it (§D.2).**

**The census that measured this carried a positive control before it was
believed** (`VERIFICATION_CHARTER.md` §2bm): the identical filter, over the
identical corpus, was first run against a pattern known to be present and was
required to return non-zero. A zero from a filter not shown able to return
non-zero on the same corpus is not a measurement. `/usr/bin/grep` was used
explicitly, because the shell's `grep` on this box is **ugrep**, which rejects
flags GNU `grep` accepts and whose swallowed usage error prints as an empty
result (`LESSONS.md` L-386 class).

## D.2 IT WAS **UNCALLABLE**, NOT MERELY UNCALLED — the structural cause, and it EXONERATES the authors

**THIS IS STATED FIRST AND PLAINLY, BECAUSE A DEAD-LEVER FINDING READS LIKE AN
ACCUSATION OTHERWISE.** `scripts/build_k0g.py` **creates `0/` itself** — `:1016` creates the `0` directory and `:1054` calls `os.utime` on `0/T` — and
stages **no `0.orig`** (`0.orig` occurrences in that file: **0**; the
repaired `scripts/build_k0h.py` carries **34**). So there is no point in the
sequence at which clause 7 could have been pulled: **invoked AFTER the build it
would have refused EVERY case of this rung; invoked BEFORE it, there was nothing
to judge.**

**NOBODY FORGOT TO CALL IT. IT COULD NOT BE CALLED.** No author of this rung's
instruments is at fault, and no reader should infer carelessness from this
appendix. The defect is one of *sequencing*, inherited by derivation across the
whole K0 family, and it was invisible for a specific and instructive reason:
**the selftest passed throughout, because it drives `launch_guard()` DIRECTLY, as
a function.** A green control over zero call sites is a pass about the code and
not about the world — `L-221`/`L-222` in its purest form, *a lesson is not
applied until every call site asserts it, and here there were none.*

This was ruled by the verification team as **D616** and stands at
`VERIFICATION_CHARTER.md` v1.82 §2bl; the family-wide census is at
`docs/DEAD_LEVER_AUDIT.md`, and the repaired exemplar at
`docs/campaigns/F14-cooling-ladder/K0h_PREREGISTRATION.md` §A1 (`:1355-1420`).

## D.3 WHAT THIS APPENDIX IS **NOT** — no withdrawal, and no allegation against any case

- **NO VERDICT IS WITHDRAWN, MOVED, SOFTENED OR RE-OPENED.** K0g's rung verdict remains **`NOT A RESULT`** — the comparator
  exited 2 and **zero gate readings were taken**. There is no graded row to
  withdraw, no band was read, and nothing in `K0g_VERDICT.txt` or the §8 cost
  accounting (888.12 core-min actual against the registered CEILING 915.58,
  WITHIN) moves by one digit.
- **NO CASE IS ALLEGED DIRTY, AND NONE WAS LOOKED FOR.** This appendix reports
  the state of an instrument, not the state of a run tree. No case directory was
  inspected for a stray `0/` or a pre-existing time directory, no such stray was
  found, and none is claimed to exist. A reader who takes this as evidence that
  anything on disk is contaminated has read it backwards.
- **NOTHING ABOVE THIS SECTION IS EDITED, STRUCK OR REWRITTEN.** Every line above
  stands byte-identical (§D.0).
- **AND THE FORMULATION THAT CARRIES THE WHOLE OF IT, RECORDED VERBATIM:**
  **An absent check is not a failed check, and it is not a passed one either.**
  Clause 7 did not fire and did not fail to fire. It was never reached. The
  honest record of that is a disclosure, which is what this is.

## D.4 WHAT THIS RUNG'S STRAY-WRITE ASSURANCE ACTUALLY RESTS ON

**IT RESTS ON CLAUSE 6 ALONE — THE AGE GUARD, EVALUATED AT GRADING — AND NOT ON
CLAUSE 7 HAVING BEEN CHECKED.** Clause 6 is a live, executed, separately
implemented check: it compares each field's mtime at `endTime` against the case's
own `0/T` and fails the case if the fields are not newer. Across roughly ten
implementations in this lab clauses 6 and 7 **never share code**; clause 6's
passing is therefore untouched by clause 7's absence, and nothing in this
appendix weakens a clause-6 result anywhere.

**AND THE POSITIVE EVIDENCE ON THIS RUNG IS NOT WITHDRAWN, RESTATED HERE SO IT
IS NOT LOST BESIDE A NEGATIVE FINDING.** The verification team verified **clause 6
holding on BOTH K0g arms**, with the fields at `endTime` post-dating the case's
own `0/T` by approximately **2.6 hours**. That is a measurement, it stands, and
this appendix neither weakens nor re-opens it. `DONE.M1_c` and `DONE.M2_c` stand.

**ONE BOUNDED OBSERVATION, ASSERTING NO DEFECT AND CHANGING NO VERDICT.** In this
rung's builder, `0/T` is created and stamped by **the build** rather than by the
launcher (`:1016` creates the `0` directory and `:1054` calls `os.utime` on `0/T`). A reader entitled to know what clause 6 dates its
comparison against should not have to derive that from source, so it is recorded
here. **It is already on the lab's record** at
`K0h_PREREGISTRATION.md:1372`, it is **not a new finding**, it **alleges nothing
about any case on disk**, and it **does not withdraw or qualify any clause-6
result that has been reported.** It is stated as a fact about the referent, and
nothing follows from it in this document.

## D.5 WHAT IS **NOT** ORDERED HERE, AND WHY — so the omission is not read as an oversight

**THE BUILDER REPAIR IS EXPLICITLY NOT ORDERED.** Re-sequencing this rung's
builder to stage `0.orig` and let the launcher arm `0/` would touch an
instrument that sits on a graded path; on this rung the launcher and builder are pinned by blob in the
**frozen** §7.7 grading-path table (`check_comparator_freeze` PASS 8/8 at the
`4d0046c1` freeze), so re-sequencing them would move a pinned grading-path blob
on a frozen registration after compute — the one move rule 2 forbids outright. And the cost of that
repair exceeds the risk it retires, because §D.4's assurance does not depend on
it. **What is owed here is DISCLOSURE, and this appendix is the whole of the
discharge.** The repair pattern exists and is on the record — `K0h` carries it
(`build_k0h.py`, 34 `0.orig` occurrences; `launch_k0h.sh`, two clause-7 call
sites with negative controls) — so a future team that decides the repair IS
worth taking has a worked exemplar and does not have to invent one.

## D.6 WHAT THIS APPENDIX DID NOT DO — each stated explicitly

- **It altered no gate, no threshold, no band, no cap, no cost basis and no
  label**, and it could not: it adds no test and computes no number.
- **It withdrew, re-graded and re-ran nothing.** No comparator was executed, no
  marker was written or removed, no `DONE.*` or `STATUS.*` file was touched.
- **It launched nothing. ZERO core-minutes**, solver or otherwise.
- **It repaired no builder, no launcher and no instrument.** Not one byte of
  executable code was changed anywhere by this write.
- **It edited nothing above its own heading**, in this file or any other.
- **It touched nothing in the navier-class territory.** `cases/navier_class/PRD/mark_done_prd.py`
  carries the same uncalled definition and is **REFERRED, NOT TOUCHED** — it is
  not this team's file.
- **Nothing was sent, filed, uploaded, registered, posted or commented**
  (standing rule 7). Submissions remain **PARKED**.
- **No permission setting, `CLAUDE.md` or `.claude/` configuration was touched**
  (standing rule 9), and no agent message was treated as Sanaa's consent.

*Written by a heat-transfer lane on the heat-transfer supervisor's disclosure
brief, 2026-09-10. Zero core-minutes. Disclosure only.*
