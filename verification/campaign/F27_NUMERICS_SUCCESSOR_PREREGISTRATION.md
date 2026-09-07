# F27-WOMERSLEY NUMERICS SUCCESSOR — pre-registration (DRAFT)

> **DRAFT — NOT AUTHORISED — CHECK-4 NOT TAKEN.**
> A cfd `lab-lane` draft. Not frozen; no sha commits it as a freeze; **no solver
> launched** in producing it. The rule-2 freeze (gate/threshold/cap/label by sha,
> and the hash of the grading path against the committed blob) is the cfd
> supervisor's non-delegable check 4. Editable until then, closed after. Drafted
> 2026-09-07.

**§2ay classification of the parent.** Parent verdict: **F27 NOT A RESULT** on both
gates — `verification/campaign/F27_WOMERSLEY_PIPE_RESULTS.md:27-28,36`. Rule 5 turned
a GATE FAIL into NOT A RESULT because the grid triple read **OSCILLATORY, monotone
FALSE** — the fine level (245,760 cells) departs from the exact Womersley solution by
four orders of magnitude while the two coarser levels behave exactly as registered.
The census flagged it as a standing violation: a landed NOT A RESULT with **no active
dated fix-successor** (`:384-387` explicitly leaves the successor to the cfd
supervisor and takes none). This draft is that successor: it CHANGES the numerics and
re-runs. It is **not** a capability gap (state a) — the two coarser levels converge
to the exact solution cleanly, so `pimpleFoam` on a butterfly pipe mesh is *capable*;
what failed is a fine-level numerical instability with a recoverable our-side cause.

---

## 1. WHAT FAILED, MEASURED

From `F27_WOMERSLEY_PIPE_RESULTS.md` §2:

| level | cells | E2 | Einf | periodicity | uniformity (A_z / A_theta) | E_perp (spurious cross-flow) |
|---|---|---|---|---|---|---|
| coarse | 3,840 | 7.66e−03 | 1.17e−02 | PLATEAUED | PLATEAUED | 4.4e−15 |
| medium | 30,720 | 2.08e−03 | 6.40e−03 | PLATEAUED | PLATEAUED | 2.7e−14 |
| **fine** | 245,760 | **90.76** | **367.73** | **NOT_PERIODIC (87.3, tol 1e−06)** | **NOT_UNIFORM (A_z 19.2, A_theta 29.6)** | **88.51 (DIVERGENT)** |

**Every solver residual at every one of 2,688 fine-level time steps is converged**
(18,816 readings, all under tolerance) — and the answer is wrong anyway. The
symmetry-preserving structure collapses: the spurious cross-flow channel `E_perp`,
identically zero for the exact solution and ~1e−14 at the two coarser levels, reads
**88.51** at fine; the field is neither periodic, nor axisymmetric, nor z-invariant.

The parent record **refuses to name a cause** (§2.4) and holds that a mechanism
"would need work nobody has done." It records one correlate: the diffusion number
`Fo` rises 0.442 / 0.884 / **1.767** across the ladder (ceiling 5.0) — measured, not
a demonstrated cause.

---

## 2. THE SPECIFIC NUMERICS CHANGE, AND WHY IT SHOULD RECOVER

**Working hypothesis (stated as a hypothesis, tested by this run, not asserted):**
the fine-level symmetry break is a **non-orthogonal-correction / bounded-differencing
failure** on the butterfly mesh, whose max non-orthogonality **rises across the
ladder — 28.586° / 36.159° / 40.423°** (`§5` of the parent). The parent ran:
- `Gauss linear corrected` Laplacian/`snGrad` with **1 non-orthogonal corrector**;
- default (unlimited) gradient;
- `backward` time scheme; `dt` halving 7.8e−3 / 3.9e−3 / 2.0e−3.

At 40° non-orthogonality a single non-orthogonal corrector under-resolves the
explicit correction term; the corrected Laplacian and the reconstructed cross-plane
velocity acquire an anisotropic error that grows with the sharpened fine-grid
gradients — exactly the signature of a spurious cross-flow that is ~1e−14 at 28.6°
and 88.5 at 40.4°.

**Changed levers (the fix), all numerics, reference and geometry untouched:**
1. `nNonOrthogonalCorrectors` **1 → 3** (PIMPLE), so the explicit non-orthogonal
   correction is iterated to convergence within each time step;
2. Laplacian and `snGrad` `corrected` → **`limited 0.5`** (bounded non-orthogonal
   correction, the standard robustness choice above ~35° non-orthogonality,
   `MESH_STANDARD.md` guidance);
3. gradient `Gauss linear` → **`cellLimited Gauss linear 1`** (bounds reconstructed
   gradients, suppressing the cross-plane over/undershoot);
4. divergence, if `Gauss linear` at present, → **`Gauss linearUpwindV grad(U)`**
   (bounded, second order) as a fallback lever if 1–3 are insufficient.

**Diagnostic to confirm or refute the hypothesis (mandated, reported-not-gated):**
`E_perp` and `A_theta` are read at the fine level. If the changed numerics drop
`E_perp` back to O(1e−14) and the triple becomes CONVERGING, the non-orthogonal-
correction mechanism is **demonstrated**; if `E_perp` stays O(1) the hypothesis is
**refused** and the record says the change did not recover it and names the next
lever (dt refinement / decomposition / flux). **The registration does not promise
recovery** — it commits a specific, mechanism-motivated change and a diagnostic that
can prove it wrong.

---

## 3. THE GATE, AND THE BANDS ARE NOT WIDENED (IDENTICAL TO THE PARENT)

The gate quantities, bands and rule-5 gating are **carried over unchanged** from the
frozen parent (`F27_WOMERSLEY_PIPE_PREREGISTRATION.md`), because the reference is the
**exact Womersley solution** — which no numerics change can move — and the ladder
(cell counts, `dt`, refinement ratio r = 2 in h and dt) is unchanged:

| gate | quantity | band (unchanged) |
|---|---|---|
| G-F27R-1 | `E2_velocity_locked_phase` | [6.052738753361828e−05, 1.513184688340457e−03] |
| G-F27R-2 | `Einf_axial_velocity_locked_phase` | [1.1397841172247245e−04, 2.849460293061811e−03] |

`BAND_FACTOR = 5.0` (unchanged). Rule 5 applies in full: a non-CONVERGING triple is
**NOT A RESULT**; a CONVERGING triple inside the band is PASS, else GATE FAIL; no GCI
is quoted on a non-monotone triple. The periodicity and uniformity plateau limbs and
the four reported-not-gated channels (`E_perp`, `A_z`, `A_theta`, `W`) are carried
over identically. **The bands are held EXACTLY at the parent's values — not widened
by a single digit** — because the whole point is to test whether the numerics change
brings the *same* solution inside the *same* bar. Widening the band to admit the
fine level's current 90.76 / 367.73 would be precisely the answer-fitting Sanaa's
T25 ruling forbids, and is not done.

---

## 4. GRADING PATH — FIXED AT THE FREEZE, PLANTED-ZERO CONTROL

The grader is the frozen `cases/F27_WOMERSLEY_PIPE/grade_f27.py` (blob at the parent
freeze), re-used **unchanged** so the successor is graded by the identical instrument
that graded the parent. Its planted-zero controls (rule 3) already exist and passed
on the parent: `PZ-F27-READERS` (four channel-separated plants, each seen only by its
own channel), the on-disk per-gate plants, and `PZ-F27-PERIODICITY_AND_UNIFORMITY`.
A **fresh pre-registration commit** is required for the successor (its own
`--prereg-commit`), and the supervisor hashes the changed `fvSchemes`/`fvSolution`
against the committed blobs at check 4. Grading is **zero-new-compute** after the
solves.

---

## 5. COST — rule 12 (measured anchor from the parent run)

Parent measured actuals (`ClockTime × 4 ranks ÷ 60`): coarse **0.40**, medium
**8.00**, fine **257.07** = **265.47 core-min** (`F27...RESULTS.md` §6, corroborated
three ways). The numerics change adds cost on the fine level chiefly through
`nNonOrthogonalCorrectors` 1 → 3 (two extra pressure solves per time step; the
pressure solve dominates `pimpleFoam` cost):

| level | parent actual | change factor | successor estimate |
|---|---|---|---|
| coarse | 0.40 | ~1.4× | 0.6 |
| medium | 8.00 | ~1.4× | 11.2 |
| fine | 257.07 | ~1.4× | 360.0 |
| **total estimate** | | | **≈ 372 core-min** |
| **HARD CAP** | | | **500 core-min** |

The ~1.4× factor is an estimate: two extra non-orthogonal correctors do not double
the step cost because only the pressure Poisson solve is repeated and it warm-starts
from the previous corrector; the limited schemes add a bounded correction pass. An
overrun of the 500 cap **stops the run** (rule 12). Dollars: 500 core-min = 8.333
core-h × $0.0513 = **$0.4275 — DERIVED, NOT MEASURED** (reported-by-owner,
`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 ceiling. Calibration row owed at
completion (this factor is exactly the kind of misprediction the lab tracks).

---

## 6. WHAT THIS SUCCESSOR CAN AND CANNOT SETTLE

- **Can:** whether the named non-orthogonal-correction change recovers a CONVERGING
  fine-level triple inside the (unchanged) bands, and — via the `E_perp` diagnostic —
  whether the non-orthogonal-correction mechanism is the cause.
- **Cannot, if it still fails:** it would then localise the next lever (dt,
  decomposition, flux), but a persistent failure remains **state (b)** — a live
  numerics investigation with named next steps — unless and until every reasonable
  numerics family is shown unable to recover it on a mesh whose two coarser levels
  already converge, which no evidence supports.

**Nothing is sent, filed, uploaded, registered or posted (rule 7). Draft handed to
the cfd supervisor for the check-4 freeze.**
