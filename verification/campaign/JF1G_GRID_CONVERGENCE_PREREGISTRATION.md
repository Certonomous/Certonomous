# JF1G — JET-FLAP GRID CONVERGENCE STUDY AT `C_mu = 0.1` — PRE-REGISTRATION

**Status at freeze: ARMED — never run.** No solver and no mesh generator has run
against this document.

**Authority.** Sanaa's SANAA-DIRECT of 2026-09-01 ~15:45Z,
`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`
(committed `f4c8e466`): **§0**, the automatic convergence study that is now a
pipeline stage on every gated case, and **§3**'s jet-flap instance of it —
*"three grids at `C_mu = 0.1` (the 39,984-cell grid as L2; build L1 and L3 at
`r = 1.5` from the same script). p, GCI, band on CL. One grid family on screen for
all figures."*

**This is a NEW registration and it does NOT run against `JF1_PREREGISTRATION.md`
(`12b1bd84`).** No gate of that document scores here; **gate 6 of `12b1bd84` is not
inherited** (`verification/campaign/JF1_GATE6_FINDING.md` — unsatisfiable by a
cosine, repair reserved to Sanaa). Nothing here presumes that ruling.

**Relationship to `12b1bd84` §4's mesh ladder.** That frozen document registers a
**C-mesh** ladder at `r ≈ 1.3693` whose L2 is **86,638 cells**
(`verification/runs/JF1_jet_flap/mesh/`, generator `make_jf1_mesh.py`). **This study
does not use it.** Sanaa named the **39,984-cell O-mesh** — the grid all five 2026-08-31
rows actually ran on, from `cases/JF1_JET_FLAP/build_jf1.py` — and `r = 1.5`. Her
directive is later and specific. **The two families are different topologies and must
never be mixed on one figure or in one triple**; that hazard, and her "one grid family
on screen" instruction, is the reason this is said here rather than left to a reader.

---

## 0. REGISTER SEARCH BEFORE FREEZING (L-427)

**Registers searched for `jet flap` / `JF1` / `blown` / `Cmu` / `observed order` /
`GCI` / `mesh similarity` / `growth ratio` / `refinement ratio` / `clipping`, in
`docs/NUMERICS_KNOWLEDGE.md`, `docs/LESSONS.md` and `verification/campaign/`. What the
search returned:**

| register | returned |
|---|---|
| `docs/NUMERICS_KNOWLEDGE.md` | **`N-T8` — and it is the most important thing this search returned.** *A Richardson extrapolate is the one grid-convergence output whose SIGN a key-presence selftest cannot catch, and four independent implementations in this lab got it wrong the same way.* It carries a **standing rule adopted 2026-08-24**: every such comparator's `--selftest` must carry a **value-checking** Richardson control — a synthetic power-law triple with a known limit, asserted to 1e-12 relative — not merely a key-existence check. **Adopted verbatim in §6.3.** Nothing else in the 45 `N-*` families concerns jet-flap, blown-slot or `C_mu`. |
| `docs/LESSONS.md` (max existing number **L-428**) | **L-235** (clipping reads as convergence) — adopted as an instrument, §6.4. **L-341** (a mesh-dependent BC coefficient turns a grid study into a BC measurement) — checked against this case and **negative**, §0.1. |
| `verification/campaign/` | `JF1_PREREGISTRATION.md`, `JF1_L1_FEASIBILITY_FIRST_FIELDS.md`, `JF1_GATE6_FINDING.md`, `F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`. **No prior JF1 grid-convergence study exists** — no observed order and no GCI has ever been computed on this case. |

**Nothing already on this box refutes any claim registered below.**

### 0.1 L-341 checked, negative

Read off the running case's own `0/`: `airfoil` = `noSlip` / `zeroGradient` /
`fixedValue 1e-10` (k) / `omegaWallFunction` / `nutLowReWallFunction`; `farfield` =
`freestreamVelocity` / `freestreamPressure` / `inletOutlet`; `jetSlot` = `fixedValue`
on U, k, omega. **No `mixed` condition and no hardcoded `deltaCoeff`-bearing
coefficient anywhere**, so no level silently carries a different boundary condition.
`omegaWallFunction`'s mesh dependence is by construction and correct. Recorded as a
negative result rather than left unstated.

---

## 1. THE DEFECT IN THE GENERATOR'S DEFAULT PATH — FOUND BEFORE FREEZING, AND IT WOULD HAVE POISONED THE ORDER

`cases/JF1_JET_FLAP/build_jf1.py` refines with `--scale s`: tangential counts scale by
`s`, near-wall spacing `y1` scales by `1/s`. **The wall-normal count does not.** With
its default `--n-rad 0` the radial count is *solved from the growth cap*
(`min_count_for_cap(y1, R, g_cap)`), and shrinking `y1` at a fixed cap barely moves it.

**Computed from the generator's own functions, before any mesh was built:**

| `s` | `y1` | wall-normal count under **default `--n-rad 0`** | under **explicit `--n-rad 98`** |
|---|---|---|---|
| 1.00 | 5.000e-06 | 98 | 98 |
| 1.50 | 3.333e-06 | **100** | **147** |
| 2.25 | 2.222e-06 | **103** | **220** |

**The default path refines the wall-normal direction by a factor of 1.02 while
refining the tangential direction by 1.5.** A triple built that way is not
geometrically similar, and its observed order would measure the mixture rather than
the discretisation — **precisely the F28 failure Sanaa names in §0 step 4(b)**. It is
found here at zero cost because §0 step 1 says *uniform refinement ratio in every
direction* and that sentence was checked against the generator instead of assumed.

**The repair is to pass `--n-rad 98` explicitly**, which the script already supports
(`n_rad = round(n_rad * s)`), and it is registered as binding in §2. The generator is
**not edited**; the defect is in its *default*, and a successor calling it without
`--n-rad` will reproduce the defect, so this is also recorded as a finding for the
`cfd` board.

### 1.1 Why the growth ratio is SUPPOSED to change between levels, and the identity that proves similarity

A reader checking "same growth ratio on every level" will find `g` = 1.148350 /
1.096414 / 1.063364 and wrongly call the family dissimilar. **Uniform refinement of a
geometrically stretched stack requires `g` to change.** Halving-by-`r` every cell in a
stack that starts at `y1`, grows at `g` and reaches the same outer radius `R` gives
`y1 → y1/r`, `n → n·r`, and **`g → g^(1/r)`**. So the similarity test is not `g` equal
but **`g_fine^r == g_coarse`**:

| pair | `g_fine^r` | `g_coarse` | difference |
|---|---|---|---|
| C2/C1 | 1.14805201 | 1.14835037 | **2.98e-04** |
| C3/C2 | 1.09653608 | 1.09641350 | **1.23e-04** |
| C4/C3 | 1.06309672 | 1.06336399 | **2.67e-04** |

Agreement to `3e-04` on all three pairs, the residue being integer rounding of `n_rad`.
**This identity is registered as a similarity clause in §2.2 so that the check is
executed rather than admired.**

---

## 2. THE MESH FAMILY — FROZEN

**One family, one script, one topology (O-mesh), one farfield radius (26 c about
`c/4`), one-cell span (0.01 m), `--slot-type patch`.** Generator
`cases/JF1_JET_FLAP/build_jf1.py`, **called with `--n-rad 98` on every level**.

| level | `--scale` | `--n-rad` | `n_base` | `n_side` | `Ni` | `Nj` | `y1` (m) | `g` | **cells** | complete layers inside `delta` |
|---|---|---|---|---|---|---|---|---|---|---|
| **C1** | 1.000 | 98 | 12 | 198 | 408 | 98 | 5.0000e-06 | 1.148350 | **39,984** | 47 |
| **C2** | 1.500 | 98 | 18 | 297 | 612 | 147 | 3.3333e-06 | 1.096414 | **89,964** | 70 |
| **C3** | 2.250 | 98 | 27 | 446 | 919 | 220 | 2.2222e-06 | 1.063364 | **202,180** | 105 |
| **C4** *(contingency, §7)* | 3.375 | 98 | 40 | 668 | 1,376 | 331 | 1.4815e-06 | 1.041634 | **455,456** | 159 |

**C1 is the exact grid the five 2026-08-31 rows ran on** (verified: `--scale 1.0`,
`--n-rad 98` reproduces `Ni = 408`, `Nj = 98`, `39,984` cells — the same numbers that
level's `log.build_jf1` printed). **So the sweep figures and the discretisation band
come from one family, satisfying "one grid family on screen for all figures."**

### 2.1 ⚠ DISCLOSED DEPARTURE FROM THE DIRECTIVE'S WORDING, D-2 — 39,984 IS THE COARSEST LEVEL, NOT THE MIDDLE ONE

Sanaa's §3 places the 39,984-cell grid as **L2**, with L1 coarser. **The generator
refuses to build that L1.** `build_jf1.py` carries a registered floor of **12 cells
across the slot height `h`** and exits `REFUSED: fewer than 12 cells across h` below
it. At `r = 1.5` the coarser level would need `12 / 1.5 = 8`. **The floor is a
resolution constraint on the physically decisive region — the slot — and lowering it
to build a coarse level would make that level measure slot under-resolution rather
than discretisation.**

**The ladder is therefore taken upward: 39,984 is C1, the coarsest, and the family
refines from it at `r = 1.5`.** This keeps every substantive clause of §0 — three
geometrically similar levels, one parametric script, `r = 1.5` (inside her 1.5–2.0
band), the existing grid inside the family — and it is the same direction of travel
§0 step 4(c) itself prescribes when a ladder needs another level. **It is still a
departure from her literal placement, and it is disclosed rather than absorbed.**

### 2.2 SIMILARITY CLAUSES — CHECKED BEFORE ANY SOLVER STARTS, REFUSING ON FAILURE

Computed and asserted for each consecutive pair. Values below are the pre-computed
expectations; the checker recomputes them from the emitted meshes' own `build.log`
and `checkMesh` output and **REFUSES (exit 2)** on any breach.

| clause | tolerance | C2/C1 | C3/C2 |
|---|---|---|---|
| `n_base` ratio | 1.5 ± 0.02 | **1.5000** | **1.5000** |
| `n_side` ratio | 1.5 ± 0.02 | **1.5000** | **1.5017** |
| `Ni` ratio | 1.5 ± 0.02 | **1.5000** | **1.5016** |
| `Nj` (wall-normal) ratio | 1.5 ± 0.02 | **1.5000** | **1.4966** |
| `y1` ratio | 1.5 ± 1e-9 | **1.5000** | **1.5000** |
| **total cell ratio** | `r^2` = 2.25 ± 0.02 (2-D) | **2.2500** | **2.2473** |
| **`g_fine^r` vs `g_coarse`** | ± 1e-3 | **2.98e-04** | **1.23e-04** |
| complete layers inside `delta` | ≥ 30 every level, and increasing | 47 → 70 | 70 → 105 |
| topology / farfield `R` / span / `--slot-type` | identical strings | — | — |
| `checkMesh` | `Mesh OK` on every level | — | — |

**The total-cell ratio clause is the cheap arithmetic check that catches the §1
defect**: under the defaulted `--n-rad` the C2/C1 cell ratio would read **1.531**, not
2.25, and the checker would refuse. It is registered because an assertion that
would have caught a defect already found is the one most likely to catch the next one.

---

## 3. THE GRADED QUANTITY, AND THE CONDITIONS

- **Graded quantity: `CL_total`** on the airfoil, at **`C_mu = 0.1`, `alpha = 0`,
  `tau = 30°`** — the point Sanaa names. Read from
  `postProcessing/forceCoeffs*/0/coefficient.dat`, **column located by the file's own
  header**, never by index.
- `CL` is an **integrated force**, i.e. already the smooth companion quantity §0 step
  4(d) asks for. No single-cell maximum is graded.
- **`y+` is reported on every level** and is gated (§5). The case is wall-resolved.
- **`bounding k` / `bounding omega` counts are reported on every level** (§6.4).

---

## 4. THE TWO PASSES, AND WHY THERE ARE TWO

The numerics this study runs under are the subject of the companion ladder
`verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md`. Sanaa
ordered both, and ordered convergence studies to *"launch in parallel now"*. The
resolution, frozen here:

- **PASS 0 — `LABEL: diagnostic`. Launches immediately, in parallel with JF1E.**
  Runs C1/C2/C3 on the **E0 baseline numerics** at `endTime 8000`. **Pass 0 scores
  nothing: no `PASS`, no `GATE REACHED`, no observed order and no GCI may be quoted,
  published or implied from it.** Its entire purpose is to measure the **magnitude of
  the level-to-level `|ΔCL|`**, which is the number §0 step 2's tightness rule needs
  and which nobody in this lab currently knows. It cannot fit a gate because it
  cannot produce a verdict.
- **PASS 1 — the graded pass.** Runs C1/C2/C3 on **the numerics of the first JF1E
  rung to reach Gate E at `C_mu = 0.1`**, at `endTime 30,000` with `residualControl`
  tightened to **1e-8** on `p`, `U`, `k` and `omega` per §0 step 2.
  **If no JF1E rung reaches Gate E**, Pass 1 runs on the E0 baseline numerics and
  **every number it produces carries the clipping disclosure**, the case remains
  **ungraded on physics**, and the observed order is reported with that limitation
  stated on the row.

**The selection rule above is frozen; its outcome is not chosen by this lane.** Mesh
builds and every §2.2 similarity check are numerics-independent and run immediately.

---

## 5. THE GATES — FROZEN THRESHOLDS, FROZEN LABELS

### Gate G1 — mesh similarity
Every clause of §2.2 satisfied on all three levels. Breach → **`NOT A RESULT`** for
the whole study, with the offending ratio printed.

### Gate G2 — `y+`, per level
`max(y+)` on the `airfoil` patch **< 1.0** on **every** level. Breach on any level →
**`NOT A RESULT`**. *(Measured context, not a prediction: the C1 grid's five completed
rows gave `max(y+)` 0.1914 (unblown) rising monotonically with blowing to **0.3982**
at `C_mu = 0.40`; the `C_mu = 0.10` row read **0.2556**. Finer levels scale `y1` down
by `r`, so `y+` is expected to fall. It is measured on every level regardless.)*

### Gate G3 — iterative convergence, per level
On every level: `p`, `U`, `k`, `omega` initial residuals below the pass's
`residualControl` at `endTime` (**1e-6** Pass 0, **1e-8** Pass 1), **and** the strict
completion rule (CLAUDE.md rule 4) satisfied in full. Any level failing → the study is
**`NOT A RESULT`** (rule 5 clause 1: a level not iteratively converged voids the
triple whatever its value).

### Gate G4 — THE TIGHTNESS RULE (Sanaa §0 step 2), AND IT IS THE ONE MOST LIKELY TO BITE
Define, per level, the iterative change `eps_L = |CL(endTime) − CL(endTime − 2000)|`,
and the level-to-level differences `D21 = |CL_C2 − CL_C1|`, `D32 = |CL_C3 − CL_C2|`.

> **`max(eps_C1, eps_C2, eps_C3) <= 0.1 × min(D21, D32)`**

If this is not satisfied, **the observed order is noise, not discretisation**, and the
comparator **REFUSES to report `p` or a GCI** — the study is **`PENDING`**, residuals
and the stationarity window are tightened, and the levels are re-run. **It is not
reported as a converged study with a caveat.**

*(Measured context for the reader, from the C1 grid's completed `C_mu = 0.10` row:
`|CL(8000) − CL(6000)| = 4.181e-08`, and peak-to-peak over the final 2000 iterations
is `1.233e-06`. If `min(D21, D32)` exceeds `~1.2e-05` the rule is satisfied with
margin. That is a context figure, not a threshold; the threshold is the inequality
above.)*

### Gate G5 — Roache triple (CLAUDE.md rule 5)
Order of evaluation is the rule's, and it is not negotiable:
1. Any level not iteratively converged or not plateaued → **`NOT A RESULT`** (G3, G4).
2. Triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → **`NOT A RESULT`**, with
   the value, both triples and the orders printed beside it.
3. `CONVERGING` → observed order and GCI reported. **GCI at `Fs = 1.25`.**
   **No GCI is ever quoted when the three values are not monotone.**

`p = ln( (CL_C1 − CL_C2) / (CL_C2 − CL_C3) ) / ln(r)`, `r = 1.5`, C1 coarsest.

### Gate G6 — the acceptance band on `p` (Sanaa §0 step 3)
Formal order of the scheme is **2** (`bounded Gauss linearUpwind grad(U)` on momentum;
`bounded Gauss limitedLinear` on `k`/`omega`; `Gauss linear` on the viscous term).

> **`p` in [1.5, 2.5]` → the case is gradable and the band goes on every number.**
> **`p` outside [1.5, 2.5]` → §7 executes automatically. IT DOES NOT STOP.**

### Gate G7 — the reported band
On acceptance, the band on `CL` at `C_mu = 0.1` is the **GCI on the fine level at
`Fs = 1.25`**, and **that band is applied to every reported `CL` in the sweep**, with
the disclosure that it was measured at `C_mu = 0.1` and applied across the sweep.

---

## 6. THE COMPARATOR — REFUSALS AND CONTROLS

### 6.1 Registered refusals (exit 2, never a degraded number)
1. Any §2.2 similarity clause breached.
2. `checkMesh` not printing `Mesh OK` on any level.
3. Any strict-completion clause unmet on any level.
4. Gate G4 (tightness) unsatisfied → refuse to emit `p` or GCI.
5. The three `CL` values not monotone → refuse to emit a GCI.
6. The `coefficient.dat` `Cl` column located by index rather than by the file's own
   header.
7. Either planted control (§6.2, §6.3) failing.
8. Any attempt to form a triple from levels of two different mesh families.

### 6.2 Planted-zero control on the `CL` reader (CLAUDE.md rule 3)
The reader is proven able to see a non-zero before any zero or any small difference it
returns is believed. `PLANT = 1.234e-03` is added to the `Cl` column of a **copy** of
`JF1_L1_BLOWN_CMU010_A0/postProcessing/forceCoeffs*/0/coefficient.dat`; the reader
must return the planted file's `CL` minus the original's as `1.234e-03 ± 1e-09`, and
must return the original's `CL` as `0.54884644 ± 1e-08`. **REFUSE (exit 2) if the
plant is invisible.**

### 6.3 Richardson VALUE control — the standing rule from `N-T8`, adopted verbatim
`N-T8` records that **four independent implementations in this lab reflected the
Richardson extrapolate through the fine value onto the coarse side**, a defect
invisible to `p` and to `GCI` (both sign-independent) and to every key-presence
selftest. The correct form is

> `f_ext = f_fine + (f_fine − f_mid) / (r^p − 1)`

The comparator's `--selftest` carries a **value-checking** control: a synthetic
power-law triple `f_k = f_ex + A (r^p)^k` with `f_ex` known by construction, asserted
to **1e-12 relative**, plus `N-T8`'s free identity `frozen + corrected == 2 f_fine`
asserted on the real data. **REFUSE (exit 2) on either.**

### 6.4 Clipping counter on every level — `L-235`
`bounding k` and `bounding omega` counts over the final 500 iterations are read and
**printed on every level's row**, whatever the verdict. The counter carries the same
planted control as JF1E §4 (it must return **494** on
`JF1_L1_BLOWN_CMU010_A0/log.simpleFoam`). **A level whose forces are stationary while
`k` is being clipped is reported as stationary-and-clipping-held, never as
converged** — the whole content of L-235.

---

## 7. IF `p` LANDS OUTSIDE [1.5, 2.5] — THE AUTOMATIC RESPONSE, FROZEN IN ORDER

Executed in this order, without asking, per Sanaa §0 step 4:

1. **Re-check tightness on the finest level** (G4): tighten `residualControl` to
   **1e-9**, extend `endTime`, widen the stationarity window, re-read `p`.
2. **Re-verify mesh similarity** (§2.2) on the emitted meshes — cell-count ratios,
   wall-normal counts, layer counts, growth-ratio identity.
3. **Add C4** at the same `r = 1.5` (`--scale 3.375`, **455,456 cells**) and recompute
   `p` on the **finest three** (C2, C3, C4).
4. **Repeat for up to two more levels** (C5 at `--scale 5.0625`, ≈1.02 M cells).

`CL` is already an integrated quantity, so §0 step 4(d)'s smoother-companion clause
does not apply; **if it ever does, the substitution is stated on the row.**

---

## 8. COST — CLAUDE.md RULE 12

**Basis: MEASURED.** Unit rate **`4.0798e-06` core-s per cell per iteration**, derived
from `JF1_L1_BLOWN_CMU010_A0` (39,984 cells, 8,000 iterations, 1,305 wall s,
`ranks = 1`, from that run's own `RUN_STATUS` file). Serial throughout; the three
levels run **concurrently as three serial processes**, which is the cheapest option in
core-minutes and the fastest in wall time on this 16-core box.

**Every prior JF1 per-solve estimate assumed convergence before the iteration cap,
which has never once happened. Every figure below assumes the cap is reached.**

| item | cells | `endTime` | estimate | **registered cap** |
|---|---|---|---|---|
| Mesh builds C1–C3 + `checkMesh` | — | — | ~5 core-min | **20** |
| **Pass 0** C1 | 39,984 | 8,000 | 21.8 | |
| **Pass 0** C2 | 89,964 | 8,000 | 48.9 | |
| **Pass 0** C3 | 202,180 | 8,000 | 110.0 | |
| **Pass 0 subtotal** | | | **180.7** | **250** |
| **Pass 1** C1 | 39,984 | 30,000 | 81.6 | |
| **Pass 1** C2 | 89,964 | 30,000 | 183.5 | |
| **Pass 1** C3 | 202,180 | 30,000 | 412.4 | |
| **Pass 1 subtotal** | | | **677.5** | **850** |
| **C4 contingency** (§7) | 455,456 | 30,000 | 929.1 | **1,200** |
| | | | | **STUDY CAP 2,320 core-min** |

**Derived cost at the recorded `c7a.4xlarge` rate of `$0.0513/core-h`: 2,320 core-min
= 38.67 core-h = `$1.98`. DERIVED, NOT MEASURED — this box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5).**

**An overrun stops the run; it does not get a new budget.** Each level's wrapper
carries `timeout` at its own cap and exits non-zero on the kill. The C4 contingency
cap is drawn **only if §7 step 3 is reached**, and is registered here rather than
requested later precisely so that reaching it is not a new budget.

**At completion, estimate-versus-actual lands as a row in `docs/COST_CALIBRATION.md`**
per rule 12, stating the ratio actual/predicted and attributing the gap.

---

## 9. PRE-REGISTERED EXPECTATION — WHERE THIS WILL FAIL IF IT FAILS

Registered so that being wrong is visible rather than reinterpretable.

1. **Most likely failure: Gate G4, the tightness rule, on Pass 0.** The C1 grid's
   iterative drift in `CL` is `4.2e-08` over the last 2,000 iterations — extremely
   small — so tightness fails only if `min(D21, D32)` is itself below `~1.2e-05`,
   i.e. if `CL` is already grid-insensitive at 40k cells. That is the honest risk and
   it is the reason Pass 0 exists.
2. **Second: `p` below 1.5.** The `k`/`omega` equations run `limitedLinear`, a limited
   scheme whose effective order degrades toward first order where the limiter is
   active — and the limiter will be active in the jet shear layer, which is exactly
   where this case's lift comes from. **A `p` near 1 would be a real result about this
   discretisation, not an error**, and §7 executes rather than explaining it away.
3. **Third: the clipping (§6.4) does not clear on the finer levels**, in which case
   Pass 1 grades on E0 numerics and the case stays ungraded on physics with the
   limitation on the row.

---

## 10. WHAT THIS REGISTRATION DOES NOT COVER

- It grades **one point** — `C_mu = 0.1`, `alpha = 0`. The band it produces is applied
  across the sweep **with that disclosure attached**, per §7 of the directive's intent
  and G7 above.
- It does not repair, inherit or rule on gate 6 of `12b1bd84`. Reserved to Sanaa.
- It does not compare against jet-flap theory. Any theory comparison is a separate
  registration.
- It makes **no claim about the C-mesh ladder** of `12b1bd84` §4, which is untouched.

---

## 11. FREEZE

Frozen at the commit that adds this file. The gates, thresholds, caps and labels above
are fixed from that commit. After first compute, changes land only as dated addenda
that cannot alter a gate, threshold, cap or label; originals are struck, never
rewritten. The grading path is fixed at this commit and the comparator is hashed
against its committed blob at grading time.

**SUBMISSIONS PARKED.** Nothing in or derived from this document is sent, filed,
uploaded, posted or registered outside this box.
