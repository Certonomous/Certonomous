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
**NOT part of this freeze — a NON-registered future lever, recorded only for transparency:**
were 1–3 insufficient, a divergence change `div(phi,U)` `Gauss linear` →
`Gauss linearUpwindV grad(U)` (bounded, second order) would be a SEPARATE successor
carrying its own pre-registration and its own freeze. It is **NOT applied here**: the
frozen method changes **exactly levers 1–3** and **`div(phi,U)` remains the parent's
`Gauss linear`**. A frozen method must be deterministic; a contingent "if insufficient"
lever cannot sit inside it, so it is demoted out of the registered set (cfd `lab-lane`,
2026-09-07, pre-freeze; changes no gate, threshold, cap or label).

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

The grader is the **parallel successor instrument**
`cases/F27_WOMERSLEY_PIPE/successor_numerics/grade_f27_successor.py` (see the
2026-09-07 authoring note below for path + sha256 + commit). It is the frozen
parent grader with a **single** substantive change — its method-consistency control
checks the SUCCESSOR numerics and REFUSES a case carrying the parent method — while
**every band, `BAND_FACTOR = 5.0`, the four reported-not-gated channels and all
rule-4 / rule-5 gating are IDENTICAL to the frozen parent** (verified by `--selftest`;
bands are the exact IEEE doubles the parent `grade_f27.py::bands()` emits, not widened
by a single digit). A parallel grader is REQUIRED, not optional: the frozen parent
`control_solver_dicts_match` method-locks to the parent numerics and hard-refuses the
changed method (see the check-4-blocker note below, now resolved). Its planted-zero
controls (rule 3) are carried in full: `PZ-F27-READERS` (four channel-separated
plants, each seen only by its own channel), the on-disk per-gate plants driven both
ways, and `PZ-F27-PERIODICITY_AND_UNIFORMITY`; the selftest runs first and
unconditionally and REFUSES (exit 2) rather than degrades. A **fresh pre-registration
commit** is required for the successor (its own `--prereg-commit`), the driver hashes
the grader on disk against its committed git blob before any launch (rule 2), and the
supervisor hashes the changed `fvSchemes`/`fvSolution` and the grader against their
committed blobs at check 4. Grading is **zero-new-compute** after the solves.

---

**AUTHORING NOTE — cfd `lab-lane`, 2026-09-07 (pre-freeze; changes no gate, threshold, cap or label).**
A prior lane correctly refused this freeze because two rule-2 essentials were on disk only as prose.
They are now authored:

- **(d) changed-method artifacts authored** (no longer prose), byte-identical to the frozen parent
  `cases/F27_WOMERSLEY_PIPE/case/system/` files EXCEPT the registered levers 1–3:
  - `cases/F27_WOMERSLEY_PIPE/successor_numerics/system/fvSchemes` — sha256
    `59b77114798bad38ccfd5c9ebedcf8d69b0765b236e96472f13872c91a4fe81f`
    (gradSchemes → `cellLimited Gauss linear 1`; laplacianSchemes → `Gauss linear limited 0.5`;
    snGradSchemes → `limited 0.5`; **`div(phi,U)` stays parent `Gauss linear`; nothing else changes**).
  - `cases/F27_WOMERSLEY_PIPE/successor_numerics/system/fvSolution` — sha256
    `fea071de85b6dfc8257c88d5910cd30c8ec53078a7dd558beba6343ca72fa32f`
    (nNonOrthogonalCorrectors 1 → 3; nothing else changes).
  A byte diff against the parent shows exactly those four lines and no other. The parent's explanatory
  comment block naming `corrected`/`nNonOrthogonalCorrectors 1` is retained VERBATIM under the §2ay
  byte-identical discipline, so it now documents the parent's rationale rather than the successor's
  settings — flagged here, deliberately not edited.

- **(a) distinct successor run root declared:** `verification/runs/F27_NUMERICS_SUCCESSOR_runs`
  (the parent's `verification/runs/F27_WOMERSLEY_PIPE_runs` already exists from the parent run, so the
  successor takes its OWN root). Confirmed ABSENT on disk at authoring.

- **band constants confirmed against the grader source of truth:** the four §3 band literals each parse to
  the EXACT IEEE double emitted by `grade_f27.py::bands()` (grader blob
  `e334615966bfd9ba1d7d6988fbca775208edca9e`, unchanged since freeze commit `4bb0226d`) —
  G-F27R-1 `[6.0527387533618279e-05, 0.001513184688340457]`,
  G-F27R-2 `[0.00011397841172247245, 0.0028494602930618112]`. No §3 correction was needed.

**A FURTHER CHECK-4 BLOCKER, surfaced here and NOT resolvable by a lane authoring config files.**
The claim above that the grader is "re-used unchanged so the successor is graded by the identical
instrument" does **not hold for a method change**, because the frozen harness is method-locked to the
PARENT template:
  - `grade_f27.py::control_solver_dicts_match()` reads the FIXED path `HERE/case`
    (`cases/F27_WOMERSLEY_PIPE/case/system/`) and HARD-REFUSES unless it finds `nNonOrthogonalCorrectors 1`,
    `laplacianSchemes default Gauss linear corrected` and `snGradSchemes default corrected` — the PARENT
    method. Run unchanged it reads the untouched parent template and CERTIFIES the parent numerics (which
    the successor did not use); pointed at the successor template it REFUSES (exit 2).
  - `run_f27.sh` (frozen) hard-codes `CASE_SRC=$ROOT/case`, a single
    `RUN_ROOT=.../F27_WOMERSLEY_PIPE_runs`, and an embedded pre-flight asserting the same parent scheme
    lines (`:183`–`:186`).
  - `build_f27.py` (frozen) hard-codes `CASE_SRC = HERE/case` and copies the parent fvSchemes/fvSolution.
Consequently the successor cannot be run OR graded by the frozen scripts without either editing the frozen
parent template (forbidden by rule 6 and the §2ay discipline) or standing up a PARALLEL successor instrument
set — a successor driver and builder, and (because `control_solver_dicts_match` is method-locked) a
successor grader with its own controls and its own freeze. That is a research-direction / supervisor
decision, not lane config authoring. **The scheme artifacts and run root above are necessary but NOT
sufficient: F27 is NOT freeze-ready until the supervisor rules on the successor instrument set.**

**AUTHORING NOTE — cfd `lab-lane`, 2026-09-07 (pre-freeze; changes no gate, threshold, cap or label).
THE PARALLEL INSTRUMENT SET IS NOW BUILT (chief-directed, fix-until-runs).** The check-4 blocker above is
resolved by three NEW artifacts under `cases/F27_WOMERSLEY_PIPE/successor_numerics/` (the frozen parent
`grade_f27.py` / `run_f27.sh` / `build_f27.py` were NEVER edited; the shared `exact_f27.py` /
`foam_io_f27.py` / `proj_f27.py` / `roache_triple.py` are imported unchanged):

- **NEW GRADER** `cases/F27_WOMERSLEY_PIPE/successor_numerics/grade_f27_successor.py` —
  sha256 `53f748006c6acfa7c28123077a338d12434831641fad609e0ce3e9d997aeb0b4`, commit
  `cccce4d2cf3e5b45bca67cfc735e98fcfaad7d8f`. Its `control_solver_dicts_match` reads the CHANGED dicts from
  `successor_numerics/system/` and the UNCHANGED physics from the frozen parent `case/`; it REQUIRES the
  successor levers (nNonOrthogonalCorrectors 3, `Gauss linear limited 0.5`, `limited 0.5`,
  `cellLimited Gauss linear 1`, div(phi,U) unchanged `Gauss linear`) and EXPLICITLY refuses a case still
  carrying any parent lever. `--selftest`: **16 controls green, exit 0**; **exit 2 under `python3 -O`**;
  the method-lock **refuses the parent numerics (exit 2)** when driven that direction. The two gate bands it
  emits are the exact IEEE doubles of the parent — G-F27R-1 `[6.052738753361828e-05, 0.001513184688340457]`,
  G-F27R-2 `[0.00011397841172247245, 0.002849460293061811]` — with `BAND_FACTOR = 5.0` and the four
  reported-not-gated channels (E_perp, A_z, A_theta, W) unchanged; `CAP_CORE_MIN = 500.0`.

- **NEW DRIVER** `cases/F27_WOMERSLEY_PIPE/successor_numerics/run_f27_successor.sh` —
  sha256 `43555a430af64571e71581c2b78e4d315f0d469e571d0d1245c4d50e3e606d19`, commit
  `42f3141b65d3b3c21dc5549a823e887109f2770d`. Mirrors the parent's proven idioms (rc captured inside the
  wrapper; `proj_f27.py` pre-spend projector; rule-4 ABSENT guards; refuse-never-delete), builds with the
  successor builder from the successor schemes, pre-flight-asserts the successor numerics (rejecting the
  parent method), writes to the fresh run root **`verification/runs/F27_NUMERICS_SUCCESSOR_runs`
  (declared and confirmed ABSENT)**, carries **HARD CAP 500 core-min**, hashes the grader on disk against
  its committed git blob before any launch (rule 2), and writes a `CAP_BREACH` file at any projected or
  actual cap crossing. `bash -n` parses; its `CAP_CORE_MIN` (500) agrees with the grader's.

- **NEW BUILDER** `cases/F27_WOMERSLEY_PIPE/successor_numerics/build_f27_successor.py` —
  sha256 `fa3b4d5d80a065a2ad71af1a649bcf48728550a71f0f9aaefdbe895994b488d3`, commit
  `48e8af0b8546050d433e5da8da5711a052b55f26`. Copies `fvSchemes`/`fvSolution` from the successor
  `system/` and every other dictionary/template from the frozen parent `case/`, refuses a destination
  inside either instrument tree, and read-back-refuses if the built case does not carry the successor
  levers. Diff-confirmed: the produced successor case differs from the produced parent case **ONLY** in
  `fvSchemes`/`fvSolution`, and within those **only in the four registered levers** (3 in fvSchemes,
  1 in fvSolution).

This resolves the "grader re-used unchanged" tension flagged above: for a method change it does NOT hold,
and §4 is rewritten accordingly to cite the parallel grader. It also resolves the prior internal cap
inconsistency (the frozen parent `grade_f27.py` carries `CAP_CORE_MIN = 680`, the parent run's cap; the
successor grader and driver both carry the §5 HARD CAP of **500**). **The draft REMAINS NOT AUTHORISED:**
the rule-2 freeze (gate/threshold/cap/label by sha, and the hash of the grading path against the committed
blob) is the cfd supervisor's non-delegable check 4, and the read of `grade_f27_successor.py` as a diff is
check 1. No solver was launched in building or self-testing these instruments.

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
