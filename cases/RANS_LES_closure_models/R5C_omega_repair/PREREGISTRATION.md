# PREREGISTRATION — R5C, the `omega`-source repair and the 15 incomplete hills

**Frozen before any run.** Date: 2026-08-22. Lane: closure, option **C** of
`docs/closure/R5_DECISION_MEMO.md`, authorised by the chief as a **known-bias
repair inside pre-authorisation** ($0.009 estimated, 27-case re-extraction).
Departures go in a dated section of this lane's `RESULTS.md`, **never** by
editing this file (CLAUDE.md rule 6).

**This is a NEW pre-registration and a NEW extraction operator.** It is **not**
an amendment to, and not a repair inside,
`../R4_sparta_build/PREREGISTRATION.md` (sha256
`058444309f87a9e1f6faccca2086bf16364df7a06bb7702d155c35b1fcacbbe8`), which is
frozen and is never edited. R4's own record states why: writing a bounded,
positivity-preserving discretisation of the frozen `omega` source *"would change
the extraction operator that `PREREGISTRATION` sec. 5 registers as the
W2-validated path, and that is a new preregistration, not a repair inside this
one"* (`../R4_sparta_build/RESULTS.md` §2.3).

**Consequence, registered first because everything else depends on it.** The R4
targets and the R5C targets are **different quantities**. No number crosses
between them without saying so, and **no R5C target is merged with any R4 target
in any fit, ever.** R4's artefacts are not rewritten, moved or regraded by this
lane; R5C's artefacts have their own paths.

---

## 0. SCOPE — what this lane does, and what it must not touch

**Does:** repair the `omega` source term in a **copy** of the frozen-RANS
extraction path, rebuild it under a new name, and re-extract **all 27** R4
training cases under **one** operator.

**Does not, at any point, for any reason:**

* fit, select, regularise or discover anything — no FS3, no elastic net, no
  coefficients;
* propagate anything — no `kOmegaSSTSparta`, no a-posteriori solve;
* open a **TEST** or **VALIDATION** case. The 27 are R4's training set exactly.
  `r4_lib.assert_no_test_case` is called on the case list at build time and the
  assertion is in the code, not in this paragraph (charter §22.3, doctrine R1);
* start option **A**, **A′**, **B1**, **B2**, **C2** or **D**. Those wait for
  Sanaa. So do the R5 direction and any re-opening of R2/R3 (Charter §22.7);
* modify `sdk/openfoam/sparta/spartaTurbulenceModels/` or
  `sdk/openfoam/sparta/kCorrectiveFrozenFoam/`, or rebuild
  `libspartaTurbulenceModels.so` or `kCorrectiveFrozenFoam`. **R4's numbers came
  from those binaries and they are left exactly as they are.**
* edit any case file of the 27: `system/fvSchemes`, `system/fvSolution`,
  `0/*` and `constant/polyMesh/` are the benchmark's own, byte-for-byte as R4
  built them. **The `div(phi,omega)` scheme the 21 hills omit (N-B28) is NOT
  inserted** — R4 measured that inserting it does not fix the extraction
  (`ktest2`), and inserting it here would change the operator on the hills only,
  which is per-family operator switching.

**Nothing is sent, filed, uploaded, posted or registered outside this box
(CLAUDE.md rule 7).**

---

## 1. THE CLAIM

> **The repaired `omega` source yields COMPLETE frozen extractions — complete
> under the strict completion rule AND converged rather than cap-stopped or
> clipped flat — on the 15 hills R4 left INCOMPLETE, without changing the 12
> targets R4 already holds.**

Both halves are gated. The second half (§3 G1) is the one that can void the
first: a repaired operator that completes the hills but no longer reproduces R4's
targets has produced a different quantity, not fifteen extra hills.

---

## 2. THE NEW EXTRACTION OPERATOR, IN FULL

### 2.1 The defect, diagnosed from the source and from R4's four failed repairs

`sdk/openfoam/sparta/spartaTurbulenceModels/kOmegaSSTFrozen.C` solves, for
`omega` alone (`U`, `k`, `tauij` frozen at the high-fidelity values), lines
197–211:

```
  fvm::ddt(alpha, rho, omega)
+ fvm::div(alphaRhoPhi, omega)
- fvm::laplacian(alpha*rho*DomegaEff(F1), omega)
==
  alpha()*rho()*gamma*(PkLim + Rterm)/nutBounded            <-- (S), FULLY EXPLICIT
- fvm::SuSp((2.0/3.0)*alpha()*rho()*gamma*divU, omega)
- fvm::Sp(alpha()*rho()*beta*omega(), omega)
- fvm::SuSp(alpha()*rho()*(F1() - 1)*CDkOmega()/omega(), omega)
```

with `nutBounded = max(nut, 1e-12)` and

```
Rterm = fvc::div(phi,k) - fvc::laplacian(DkEff(F1),k) - PkLim + (2/3)*divU*k
        + betaStar*omega*k                                  (kOmegaSSTFrozen.C:171-178)
PkLim = min(-2 k (bijData && gradU), c1*betaStar*k*omega)    (:163-166)
```

**`PkLim` cancels inside `S`.** Substituting,

```
S = gamma*( fvc::div(phi,k) - fvc::laplacian(DkEff(F1),k)
            + (2/3)*divU*k + betaStar*omega*k ) / max(nut, 1e-12)
```

so `S` is `gamma/nu_t` times the **convection-minus-diffusion residual of the
frozen `k` field**, plus a positive `betaStar*omega*k` piece. The first group is
data-driven and **has no sign**: wherever the frozen `k` field's convection is
weaker than its diffusion, `S` is negative. The divisor makes that decisive —
the shipped hills carry `nu_t` down to **5.55e-12**, at the `1e-12` floor's own
scale, so `S` is amplified by up to **1e11** where the numerator is not
simultaneously small (`../R4_sparta_build/RESULTS.md` §2.3; N-B27).

**Where the negativity enters, stated as a linearisation defect and not as a
physics defect.** Every other term in the equation is either implicit
(`fvm::div`, `fvm::laplacian`) or a sink placed on the **diagonal**
(`fvm::Sp`, `fvm::SuSp` with a positive coefficient). `S` alone is added to the
**right-hand side** at its full value. A large negative right-hand side in a
matrix whose diagonal carries no matching sink produces a **negative solution**
directly — `omega < 0` on the first solve, not after an accumulation. R4's
record shows exactly that first-solve signature: on `alpha_05_7071_2024` and
`alpha_05_7071_4048`, an `omega` initial residual of **0.933** followed
immediately by `bounding omega, min: -193215225.4 max: 762695.6 average:
-50081.6` — **a negative average**, i.e. most cells negative, on iteration one
(`RESULTS.md` §2.3, L-235).

`bound(omega, omegaMin)` then replaces every negative cell with a local average.
That is where the two measured failure faces come from: 13 hills in a limit
cycle re-clipped on all 5000 iterations, 2 hills clipped flat on iteration 1 and
frozen thereafter (`initRes = 9.26e-18`, `max rel domega = 0`).

**Why the four repairs R4 tested could not have worked, on this diagnosis.**
Flooring `k_LES <= 0` cells at `1e-4` and at `1e-2` of mean `k_LES` changes the
numerator on 7–51 cells of 15,600 and leaves the linearisation untouched.
Inserting `div(phi,omega) Gauss linearUpwind grad(U)` bounds the **convection**
operator and leaves the source untouched. Raising the backstop 5000 → 20000
gives a limit cycle more iterations of the same cycle, and returned
`max rel domega = 0.105158858322751` **identical to fifteen significant
figures** (`RESULTS.md` §2.3; N-B27). **None of the four touches the term that
carries the sign.** They are recorded here so that this lane is not read as
retrying them.

**What this diagnosis does not claim.** It does not claim the frozen `k`
residual *ought* to be positive, and it does not change it. It claims only that
a source of either sign added fully explicitly is an unbounded discretisation,
and that a positivity-preserving one is available at the same fixed point.

### 2.2 The repair — a Patankar-split, positivity-preserving source

In `kOmegaSSTFrozenV2` with `omegaSourceRepair true`, and **nothing else in the
equation, the case files, the schemes or the settle criterion changed**:

```
S     = alpha()*rho()*gamma*(PkLim + Rterm)/nutBounded        (unchanged)
Spos  = max(S, 0)      ->  added explicitly, at its exact value
Sneg  = min(S, 0)      ->  added as   - fvm::SuSp( -Sneg/max(omega(), omegaMin_), omega )
```

i.e. the equation's right-hand side becomes

```
==
  Spos
- fvm::SuSp( -Sneg/max(omega(), omegaMin_), omega )
- fvm::SuSp((2.0/3.0)*alpha()*rho()*gamma*divU, omega)
- fvm::Sp(alpha()*rho()*beta*omega(), omega)
- fvm::SuSp(alpha()*rho()*(F1() - 1)*CDkOmega()/omega(), omega)
```

`-Sneg` is non-negative by construction, so `- fvm::SuSp(-Sneg/omega, omega)`
places the whole negative part of the source on the **diagonal**, as a sink
proportional to `omega`. The positive part stays explicit at its exact value —
it is not linearised at all, so it carries no lagging error.

**THE REGISTERED IDENTITY OF THE TWO OPERATORS, and it is the reason G1 is a
gate and not a hope.** At a fixed point of the outer iteration
`omega_prev == omega`, so

```
Spos + (Sneg/omega)*omega  =  Spos + Sneg  =  S      exactly
```

**The repaired operator has the legacy operator's fixed point, in exact
arithmetic.** The repair changes only *which part of the source sits on the
diagonal*, i.e. the path, not the answer. Registered prediction, made before any
run: **if the repair is implemented as described, G1 passes**; if G1 fails, then
either the implementation departs from this description or the legacy fixed
point is not the one the repaired iteration reaches, and in both cases the
targets are a different quantity.

The clamp `max(omega(), omegaMin_)` is inactive wherever `omega > omegaMin_`
(`omegaMin_ = SMALL` in dimensioned form; `omega` on these cases is O(1)–O(1e6)).
**Registered check, reported in `RESULTS.md`:** the minimum `omega` over the
written field of every graded case, so a reader can see the clamp never bound.

### 2.3 How it is built — R4's binaries are not touched

| artefact | path | status |
|---|---|---|
| `libspartaTurbulenceModels.so`, `kCorrectiveFrozenFoam` | `sdk/openfoam/sparta/{spartaTurbulenceModels,kCorrectiveFrozenFoam}/` | **NOT MODIFIED, NOT REBUILT.** R4's numbers came from these. |
| `kOmegaSSTFrozenV2` (new RAS model) | `sdk/openfoam/sparta/spartaFrozenV2/` → `libspartaFrozenV2.so` | new, this lane |
| `kCorrectiveFrozenFoamV2` (new driver) | `sdk/openfoam/sparta/kCorrectiveFrozenFoamV2/` | new, this lane |

`kOmegaSSTFrozenV2` is a copy of `kOmegaSSTFrozen` under a new type name,
carrying **one** behavioural switch read from the `RAS` sub-dictionary:

```
omegaSourceRepair   [ false | true ];      default: false  ==  R4's exact legacy path
```

**Default false.** The legacy branch is byte-for-byte the arithmetic of
`kOmegaSSTFrozen.C:197-211`. It exists so that §3 G2 can prove the new build is
not a different solver.

`kCorrectiveFrozenFoamV2` is a copy of `kCorrectiveFrozenFoam` driving
`kOmegaSSTFrozenV2`, with the same pre-registered settle criterion
(`residTol 1e-8`, `changeTol 1e-9`, `nSettle 50`, 20 % verification iterations,
`writeNow()` at the settle iteration, the L-26 sign experiment) and **two purely
diagnostic additions that touch no field**:

1. a per-iteration history file `<case>/omegaHistory.csv` with columns
   `iter,initRes,maxRelDomega,minOmegaPreBound,nNegOmegaCells,nNegSourceCells`,
   written every iteration — this is the artefact §3 G3 is graded on, and it
   exists because the legacy driver prints only every 50th iteration, which
   cannot resolve the clipping signature at the iteration where it happens;
2. a cumulative count of `bound(omega, omegaMin)` events, printed before the
   field write — **L-235's own prescribed repair**: *"count the solver's own
   bounding messages before the field write and refuse the run if there are
   any."*

Neither reads or writes a solved field. The `Info` stream and the extra CSV are
not compared byte-for-byte against anything; §3 G2 compares **fields**.

**`libs` (L-221 / L-222 / rule 14).** Where any dictionary's `libs` entry is
written or edited by this lane it is written through `scripts/foam_libs.py`
`ensure_libs` (merge, never blind-append, never blind-replace, depth-aware) and
the call site immediately asserts the library name back **from disk**. The same
law applies to the one-line `RASModel` rewrite in `constant/turbulenceProperties`:
it is inserted-or-replaced and then asserted from disk, because a silent no-op
there returns R4's own model and R4's own answer, which is exactly the L-221
shape — a failure that returns a plausible-looking field.

### 2.4 The case set, and how the 27 + 2 cases are built

| set | n | built from | mode |
|---|---|---|---|
| R5C re-extraction | **27** | `/home/ubuntu/closure-data/r4/frozen/<case>/{0,constant,system}` copied to `/home/ubuntu/closure-data/r5c/frozen/<case>/` | `omegaSourceRepair true` |
| G2 W2 reproduction | **2** | `verification/runs/W2_sparta_runs/{ph,cbfs}_frozen/{0,constant,system}` copied to `/home/ubuntu/closure-data/r5c/w2_legacy/{ph,cbfs}/` | `omegaSourceRepair false` |

Copying R4's own `0/`, `constant/` and `system/` — rather than rebuilding from
the benchmark — is deliberate and is registered as a **strengthening** of G1:
the inputs are then bit-identical to R4's by construction, so any difference
G1 measures is the operator's and nothing else. `sha256` of every copied `0/`
field is recorded in `artefacts/inputs_sha256.json` and asserted equal to the
source before any run.

The **only** edits made to a copied case:

1. `constant/turbulenceProperties`: `RASModel kOmegaSSTFrozen;` →
   `RASModel kOmegaSSTFrozenV2;`, plus, in the R5C 27 only,
   `omegaSourceRepair true;` inside the `RAS` block. Written insert-or-replace,
   asserted from disk.
2. `system/controlDict`: `libs` merged through `foam_libs.ensure_libs`, asserted
   from disk. **`endTime`, `deltaT`, `writeInterval`, `writePrecision`,
   `writeFormat`, `purgeWrite`, `startFrom`, `startTime` are NOT changed.**

No time directory is copied. The build **refuses** a destination that already
holds a `0/` or a numeric time directory (rule 4's guard). `0/` is touched last
at build time, so the age guard dates the run allowed to produce the answer.

**Backstop, registered.** `endTime = 5000`, `deltaT = 1`, `writeInterval = 5000`
— R4's own values, unchanged. **Raising the backstop is forbidden in this lane**:
N-B27 measures `initRes = 4.21656145422043e-04` and
`max rel domega = 0.105158858322751` identical to fifteen significant figures at
iteration 5000 and at iteration 20000, so a longer cap buys nothing and would
only inflate the cost. A case that reaches 5000 without settling is
**INCOMPLETE (cap-stopped)** and is reported as such.

---

## 3. GATES AND THRESHOLDS — registered now, before any run

Every gate below answers `VERIFICATION_CHARTER.md` §2a's two questions
explicitly: **(1) what result would make this gate FAIL?** and **(2) could a
wrong treatment still PASS it?**

### G0. PLANTED-ZERO CONTROL — runs FIRST, before any gate is graded

`PLANT = 1.234e-03` (this lab's own constant,
`verification/runs/T-family/T3_runs/analyse_t3.py`). Every comparator in this
lane must be shown able to see a non-zero **before** it is allowed to report a
zero (CLAUDE.md rule 3).

| control | what is planted | what the comparator MUST report |
|---|---|---|
| **G0a** numeric | `PLANT` added to a single named cell of a scratch copy of one R5C `kDeficit` field | a relative-L2 difference within **1 %** of the analytic `PLANT / \|\|f\|\|_2`, and non-zero |
| **G0b** byte | the same scratch copy | **DIFFERS** from the unperturbed file under the `sha256` comparator |
| **G0c** history | a synthetic `omegaHistory.csv` carrying one `maxRelDomega = 0.0` row inside the pre-settle window, and a synthetic log carrying one `bounding omega` line | **NOT CONVERGED** under the G3 grader, on both signatures independently |

The plants are written to scratch copies. **No R5C artefact is modified.** If any
control fails — the comparator reports zero, or identical, or CONVERGED — the
comparator **REFUSES (exit 2)** and the lane's verdict is **NOT A RESULT**. A
zero from a reader not shown able to see a non-zero is not evidence.

*(1) FAILS if any planted perturbation is invisible. (2) A wrong treatment
cannot pass G0 — G0 grades the reader, not the run.*

### G1. IDENTITY GATE — the repaired operator reproduces R4's 12 targets

**Population:** the **12** cases R4 graded COMPLETE
(`../R4_sparta_build/artefacts/frozen_inventory.json`): `alpha_10_12000_4048`,
`alpha_125`, `alpha_15_10929_3036`, `alpha_15_10929_4048`, `alpha_15_13929_3036`,
`alpha_15_7929_3036`, `AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`,
`AR_10_Ret_180`, `PHLL10595`, `CBFS13700`. Run with `omegaSourceRepair true`.

**Quantity:** for each case and for `f` in `{kDeficit, bijDelta}`,

```
e(f) = || f_R5C - f_R4 ||_2 / || f_R4 ||_2        over all cells
```

`f_R4` is read from `/home/ubuntu/closure-data/r4/frozen/<case>/<settleIter>/`;
`f_R5C` from `/home/ubuntu/closure-data/r5c/frozen/<case>/<settleIter>/`.

**THRESHOLD, registered: `max` over the 12 cases and both fields `<= 1e-6`.**

**Derivation of `1e-6`, from RESULTS.md §2's own identity numbers.** The
extraction operator's defining identity closes to **8.771e-14** relative L2 on
PH10595 and **1.7e-13** on CBFS13700 (`../R4_sparta_build/PREREGISTRATION.md` §5,
from `../Schmelzer2020_SpaRTA/RESULTS.md` §3; N-B13, N-B14). That is the
**arithmetic floor** of the operator — what it can resolve at all — and it is
~`1e-13`. §2.2 registers that the repaired operator shares the legacy fixed point
**exactly**, so the only admissible source of difference between the two targets
is the distance at which each run's outer iteration stops, bounded by the
solver's own settle criterion (`omega initRes < 1e-8` **and**
`max rel domega < 1e-9`, sustained 50 iterations). `1e-6` therefore sits

* **seven orders above** the `1e-13` arithmetic floor, and
* **two orders above** the `1e-8` residual tolerance the settle criterion allows,

and is deliberately loose, because the gate exists to detect a **moved fixed
point** — a different operator — which appears at `O(1e-2)` or worse, not to
re-measure roundoff. A tighter bar would grade path noise; a looser one would
not see an operator change.

**Reported, NOT gated (§2a: an identity may be reported and may never be gated
on).** The same `e(f)` is also reported against `1e-9` and `1e-12`, and the
per-case `max` cellwise difference is tabulated, so the record shows how close
the two operators actually came rather than only that they cleared a bar.

**Also required for G1 PASS:** all 12 remain COMPLETE under the strict completion
rule (§4) **and** CONVERGED under G3.

**G1c — the switch-active control, and it is part of G1.** A repair that is a
silent no-op would pass G1 trivially. So G1 PASS additionally requires, on every
one of the 27 R5C runs:

* the run log records `omegaSourceRepair` selected **true**; and
* `nNegSourceCells > 0` on **at least one** iteration of the run, from
  `omegaHistory.csv` — i.e. the repaired branch was actually exercised, because
  a source with no negative cells anywhere is a source the repair cannot have
  changed.

If `nNegSourceCells == 0` for **every** iteration of **every** case, the repair
was never exercised and the lane's verdict is **NOT A RESULT** — the L-221
shape, a silent no-op returning a plausible-looking field.

*(1) FAILS if any of the 24 `e(f)` values exceeds `1e-6`, or any of the 12 stops
being COMPLETE or CONVERGED, or G1c's switch-active control does not fire.
(2) Could a wrong treatment PASS? A no-op repair would — which is what G1c
catches. A repair that changed the fixed point could not.*

**If G1 FAILS the lane's verdict is `GATE FAIL`. R4's 12 targets stand, the 15
hills remain INCOMPLETE, and the R5C targets are reported and used for nothing.**

### G2. W2 BYTE-IDENTICAL REPRODUCTION — the new build is not a new solver

**Population:** the 2 W2 validation cases, run with `omegaSourceRepair false`
(the legacy branch), from copies of the W2 record's own inputs.

| run dir | inputs copied from | compared against |
|---|---|---|
| `/home/ubuntu/closure-data/r5c/w2_legacy/ph/` | `verification/runs/W2_sparta_runs/ph_frozen/{0,constant,system}` | `verification/runs/W2_sparta_runs/ph_frozen/1492/` |
| `/home/ubuntu/closure-data/r5c/w2_legacy/cbfs/` | `verification/runs/W2_sparta_runs/cbfs_frozen/{0,constant,system}` | `verification/runs/W2_sparta_runs/cbfs_frozen/354/` |

**THRESHOLD, registered — all of it, no partial credit:**

1. the settle iteration is **1492** on `ph` and **354** on `cbfs`, the W2
   record's own (`../R4_sparta_build/RESULTS.md` §2.1; N-B26); and
2. `sha256` of each of the **7** fields
   `U`, `k`, `omega`, `nut`, `bijData`, `bijDelta`, `kDeficit`
   in the run's written time directory equals the `sha256` of the same file in
   the W2 record's time directory — **14 of 14 matches, byte for byte.**

The `sha256` pairs are tabulated in `RESULTS.md` and written to
`artefacts/g2_w2_sha256.json`.

**Reason this is the registered gate.** R4 §2.1 and N-B26 establish
byte-identity as the check that a rebuild is sound: *"A broken rebuild could not
have produced bit-identical fields."* A V2 build whose legacy branch differs from
`kOmegaSSTFrozen` in any way — a reordered expression, a changed `tmp` lifetime,
a different compiler path — cannot reproduce 14 of 14.

*(1) FAILS on any `sha256` mismatch or either settle iteration ≠ the record's.
(2) Could a wrong treatment PASS? Only by being byte-identical to the record,
which is the assertion. G2 says nothing whatever about the repaired branch —
that is what G1, G3 and G4 are for, and G2 is not read as evidence about them.*

**If G2 FAILS the lane's verdict is `GATE FAIL`**: the comparison base is gone,
every R5C-vs-R4 number is void, and R4's targets stand.

### G3. CONVERGED, NOT CLIPPED — the criterion that tells them apart

Applied to **all 27** R5C runs, and to the 12 as well as the 15. A run is
**CONVERGED** for grading only if **all five** hold.

| # | criterion | threshold, registered | why this number |
|---|---|---|---|
| **a** | `bound(omega, omegaMin)` events before the field write | **exactly 0** | R4's six genuinely-converged hills bound `omega` **zero** times; the thirteen cap-stopped bound it on **all 5000** iterations; the two clipped-flat on **1**. The counter separates all three populations perfectly (L-235). |
| **b** | `min(omega)` over the **written** field, read from disk | **> 0**, and **> `omegaMin_`** | a disk-side check independent of the log. A field whose minimum sits at the bound is a field the bound produced. |
| **c** | settle iteration `convergedAt` | **>= 100** | the settle criterion needs **50** consecutive qualifying iterations, so `convergedAt >= 100` guarantees **at least 50 iterations of genuine evolution before the settle window opened**. R4's two clipped-flat hills settled at **51** — the counter opened on iteration 1, immediately after the clip. All twelve R4-COMPLETE cases clear it with margin: `convergedAt` = 133, 295, 392, 694, 1174, 1243, 1346, 1362, 1378, 1382, 1391, 1625 (minimum **133**). |
| **d** | fall of the `omega` initial residual, `initRes(1) / initRes(convergedAt)` | **>= 1e6** | the settle criterion's absolute bar is `initRes < 1e-8`; the hills start at `O(1e-1)`–`O(1)` (the clipped pair at **0.933**), so a genuine fall is **>= 7 orders**. **6** is registered to leave one order of margin for a case that starts low. R4's cap-stopped hills plateau at `initRes = 4.2166e-04` and never fall at all. |
| **e** | count of iterations in `[1, convergedAt - 50]` with `maxRelDomega == 0.0` | **exactly 0** | R4's clipped-flat hills return `max rel domega = 0` at **every** iteration from 2 onward. **A field that has stopped changing before the settle window opens has stopped for a reason other than convergence.** This is L-235 stated as a threshold. |

(d) and (e) are graded from `<case>/omegaHistory.csv`, written **every**
iteration by `kCorrectiveFrozenFoamV2` (§2.3). The legacy driver prints every
50th iteration only, which cannot resolve a clip that happens on iteration 1;
that resolution gap is why the CSV exists.

*(1) FAILS if any of (a)–(e) fails. (2) Could a wrong treatment PASS? A run that
converged by clipping flat fails (a), (b) and (e); a limit cycle fails (d) — and
fails the completion rule anyway on the `NOT CONVERGED` line; R4's exact false
convergence at iteration 51 fails (c) and (e). The five are deliberately
redundant: each of R4's measured failure shapes is caught by more than one.*

### G4. COMPLETION COUNT — the 15

Let **M** = the number of the **15** hills R4 graded INCOMPLETE that are, under
R5C, **COMPLETE** under the strict completion rule (§4, unchanged from R4's six
conditions) **AND CONVERGED** under G3.

The 15: `alpha_05_10071_3036`, `alpha_05_4071_3036`, `alpha_05_7071_2024`,
`alpha_05_7071_3036`, `alpha_05_7071_4048`, `alpha_075`, `alpha_10_12000_2024`,
`alpha_10_12000_3036`, `alpha_10_6000_2024`, `alpha_10_6000_3036`,
`alpha_10_6000_4048`, `alpha_10_9000_2024`, `alpha_10_9000_3036`,
`alpha_10_9000_4048`, `alpha_15_10929_2024`.

| M | verdict |
|---|---|
| **M >= 13** | **PASS** |
| **1 <= M <= 12** | **GATE REACHED** |
| **M = 0** | **GATE FAIL** |

**Why N = 13, registered with its reason.** R4's 15 split into **two measured
failure faces**: **13** in a limit cycle at the backstop — `initRes =
4.21656145422043e-04` and `max rel domega = 0.105158858322751`, identical to
fifteen significant figures at iteration 5000 and at iteration 20000 — and **2**
clipped flat at iteration 51 (`RESULTS.md` §2.2, §2.3; N-B27). §2.1 attributes
**both** faces to **one** mechanism, the fully explicit signed source. **A repair
of that mechanism that leaves more than 2 of the 15 incomplete has not repaired
the mechanism; it has helped some cases.** The slack of 2 is exactly the size of
the smaller face and is registered because an additional, second cause is
admissible there on R4's own evidence: the clipped pair's first `omega` solve
starts at `initRes = 0.933`, three orders above the other hills. `M >= 13` is
13/15 = **86.7 %**.

*(1) FAILS at M = 0. (2) Could a wrong treatment PASS? A run that "completes" by
clipping is excluded by G3 before it is counted, and a run whose targets are a
different quantity is excluded by G1, which overrides.*

**Registered rule for a partial outcome** — the memo's fourth pre-registration
requirement, fixed now rather than judged afterwards:

* The 27 R5C targets are **one set under one operator**. They are used
  **together or not at all**. A subset of hills is never spliced into R4's 12.
* Under **GATE REACHED** the hills family is **still incomplete**, no
  enlarged-dataset claim is licensed, and the coefficients R4 holds remain
  fitted on a biased six-member sample (`RESULTS.md` §11.3(c)) — that exposure is
  reduced, not removed, and the record says so in those words.
* Whether any R5C target is ever **used** — in A′, in C2, in anything — is a
  **separate, later, separately pre-registered decision** and **is not taken by
  this lane.** This lane produces targets and a verdict; it fits nothing.

### 3.1 How the four combine into the lane's verdict

Graded in this order, and the order is registered:

1. **G0 fails** → **NOT A RESULT** (the comparator is not evidence). Stop.
2. **G1 fails, or G2 fails** → **GATE FAIL**. R4's 12 targets stand; the 15
   remain INCOMPLETE; the R5C targets feed nothing. Stop.
3. **G1 and G2 pass** → the lane's verdict is **G4's** verdict, with **G3**
   applied case by case inside it.
4. Any of the §5 failure modes observed → **NOT A RESULT**, which overrides a
   PASS but never converts a GATE FAIL into a PASS.
5. Cap reached before grading → **BLOCKED** (§6).

---

## 4. THE COMPLETION RULE — all six conditions, registered UP FRONT

R4 added its sixth condition **after** first compute (its departure D-4). It is
registered here **before** any run, in full, and it is not extended afterwards.
A run is **COMPLETE** only if all six hold:

1. recorded `rc = 0`;
2. an `End` line in `log.frozen`, and **no `NOT CONVERGED` line**;
3. the last time directory equals the iteration the solver says it wrote at
   (`Writing fields at iteration N`), the settle iteration — **not**
   `controlDict`'s `endTime`, which is only the backstop cap;
4. every required field present in that directory —
   `U`, `k`, `omega`, `nut`, `bijDelta`, `kDeficit`, `bijData`, `grad(U)`;
5. every one of those fields **newer than the case's own `0/`** (the age guard:
   `0/` is touched last at build, so it dates the run allowed to produce the
   answer), and the solver's own settle verification marked **`[SETTLED]`**;
6. **`omega` never bounded before the field write** — `bounding omega` count
   `== 0`.

Conditions 1–6 are exactly `r4_lib.frozen_complete`, which is **re-used
unmodified** so that R5C and R4 are graded by the same code. G3 (a)–(e) is an
**additional** requirement on top of them, not a relaxation of any of them.

**A guard refuses a case whose destination already holds `0/` or a numeric time
directory.** No run is resumed, restarted in place, or re-graded after the fact.

---

## 5. THE FAILURE MODES THAT MAKE THIS **NOT A RESULT**

Quoted **verbatim** from `docs/closure/R5_DECISION_MEMO.md`, option C, *"The
failure mode that makes it NOT A RESULT"*:

> *The repaired operator converges the hills but no longer reproduces the
> record.*
> If the identity or the byte-identical W2 reproduction breaks, the targets are a
> different quantity, every comparison to R4 is void, and the enlarged dataset
> carries an unmeasured operator error rather than fifteen extra hills.
> *And the sharper one:* **a repair that converges by clipping flat**. R4 measured
> exactly this shape — an `omega` solve with an initial residual of 0.933 followed
> by `bounding omega, min: -193215225.4`, after which `omega initRes = 9.26e-18`
> and `max rel domega = 0` at every subsequent iteration, reported as CONVERGED.
> **A settle criterion that measures change cannot tell a converged field from a
> clipped one**, and a plausible-looking field from a broken repair is the L-221
> failure shape.

**Registered mapping of those two modes onto this lane's machinery**, so that
neither can be argued away after the fact:

* the first is **G1** (identity, `1e-6`) and **G2** (byte-identity, 14 of 14).
  If either breaks the verdict is **GATE FAIL** and no R5C target is used;
* the second is **G3** (a)–(e), five redundant criteria, and the **G1c**
  switch-active control against the no-op form of the same shape.

**Three further NOT A RESULT modes registered by this lane:**

* **NR-1.** Any R4 artefact under `/home/ubuntu/closure-data/r4/`, or any file
  under `cases/RANS_LES_closure_models/R4_sparta_build/`, is modified, moved or
  regraded by this lane. R4's record is not this lane's to touch.
* **NR-2.** `libspartaTurbulenceModels.so` or `kCorrectiveFrozenFoam` is
  rebuilt, relinked or replaced — R4's numbers came from those exact binaries,
  and a silent rebuild would void them retroactively.
* **NR-3.** Any threshold, population, verdict ladder or cap in this file is
  changed after first compute. Departures are dated addenda in `RESULTS.md` that
  cannot alter a gate, a threshold, a cap or a label (CLAUDE.md rule 2).

---

## 6. COMPUTE — costed before launch, with the arithmetic shown

**Rate: `$0.0513` per core-hour**, c7a.4xlarge, **owner-stated 2026-08-21/22,
reported-by-owner and NOT measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5, CLAUDE.md rule 12). Core-hours are
`wall_seconds x 1 rank / 3600`, taken from each case's own `ExecutionTime`. All
runs are **serial** (1 rank); the solver writes once, at its own settle
iteration, so no decomposition is used.

**Registered estimate, derived from R4's own measured rates
(`../R4_sparta_build/RESULTS.md` §10; `docs/closure/R5_DECISION_MEMO.md` §2):**

```
(1) 27-case repaired re-extraction
    R4's measured analogue: the sum of `ExecutionTime` over the 27
    /home/ubuntu/closure-data/r4/frozen/<case>/log.frozen files
                                       =  660.46 s
    660.46 / 3600                      =  0.18346 core-h   -> 0.184 core-h
    0.184 x 0.0513                     =  $0.009439        -> $0.0094
      (this is the memo's own "0.184 core-h = $0.009" for option C)

(2) 2 legacy W2 reproduction runs (gate G2)
    R4's measured ExecutionTime, same two cases:
      PHLL10595  14.35 s   +   CBFS13700   7.34 s   =  21.69 s
    21.69 / 3600                       =  0.00603 core-h
    0.00603 x 0.0513                   =  $0.00031

(3) postProcess -func 'grad(U)' on 29 written time directories
    not separately measured by R4 (its 0.184 counts log.frozen only)
    REGISTERED ESTIMATE                =  0.020 core-h  =  $0.00103

    -------------------------------------------------------------------
    REGISTERED TOTAL ESTIMATE          =  0.184 + 0.006 + 0.020
                                       =  0.210 core-h
    0.210 x 0.0513                     =  $0.01077       -> $0.0108
```

The memo's headline for option C is **0.184 core-h / $0.009** and priced the G2
identity re-validation at *"~ 0"*. This lane registers **0.210 core-h /
$0.0108** instead, because the G2 reproduction is two real solves and
`postProcess` is real work. The difference, **$0.0014**, is disclosed here
rather than absorbed.

**CAP, registered: `1.0 core-h` = `$0.0513`.** That is **4.8x** the registered
estimate. **If the projected spend would reach the cap, the lane STOPS and
reports `BLOCKED`.** An overrun stops the run; it does not get a new budget
(CLAUDE.md rule 12). The projection is re-computed from accumulated
`wall_seconds` each time the run set is polled.

**Concurrency, registered.** At most **6** concurrent serial solves. The box
carries ~13 load from the T-family thermal lane, whose priority is restored;
**nothing is reniced** and no other lane's job is touched. Runs are launched
under `nohup` with logs in the case directories under
`/home/ubuntu/closure-data/r5c/`; pids are recorded in
`artefacts/pids.json`.

**Reduction clause.** If, after the first 6 hills complete, the projected
27-case total exceeds **0.6 core-h**, the remaining runs are launched at
concurrency 3 and the projection is re-registered in `RESULTS.md` as a departure.
The cap does not move.

**Under this cap nothing else runs.** This lane launches no propagation, no fit
and no test-case solve, so there is no second budget line.

---

## 7. WHAT IS COMMITTED, AND WHEN

| commit | contents | when |
|---|---|---|
| 1 | **this file, alone**, with its `sha256` in the commit message | **before** the repair code runs on any case |
| 2 | the V2 solver and library sources, the build log path, the case-build and run scripts, the comparator | after the build, **before** grading |
| 3 | `RESULTS.md` with the verdict, the 27-row table, departures, cost actual vs registered; the `artefacts/*.json`; the docket / lesson / numerics rows; the `docs/LAB_STATE.md` closure-section update | after grading |

**The grading path is fixed at commit 1** (CLAUDE.md rule 2). The comparator's
`sha256` is recorded in `RESULTS.md` and the frozen file is verified to **be**
the file that ran, by hashing it against the committed blob. Bulk field data is
**not** committed; it lives at `/home/ubuntu/closure-data/r5c/` and the paths are
listed in `RESULTS.md`.

---

## 8. VERDICT VOCABULARY

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`,
and nothing else. `PENDING` is a queue state for "not yet run" and is never used
to soften a `GATE FAIL`. No synonyms and no hedging prose: honesty is carried by
the value, its threshold and the label (CLAUDE.md rule 1,
`VERIFICATION_CHARTER.md` §2).

**Lane verdict at freeze time: `PENDING` — nothing has been run.**
