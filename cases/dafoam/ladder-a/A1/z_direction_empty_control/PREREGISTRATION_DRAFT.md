# A1ZE — `empty` VERSUS `symmetry` ON THE TWO BOUNDING PLANES — **PRE-REGISTRATION, DRAFT**

> ## ⚠ DRAFT. NOT FROZEN, NOT COMMITTED AS A FREEZE, NOT ENQUEUED. ZERO COMPUTE HAS BEEN SPENT.
>
> No run root exists, no queue row exists, no solve has been run against this document.
> Gates, thresholds, caps, labels, the verdict class and the verdict ceiling are **proposed**.
> The cap arithmetic below is **evaluated but not ratified**: `dafoam-supervisor` reads the cap
> table and the registered prediction personally before this freezes
> (`SUPERVISION_CHARTER.md` §3 check 4, not delegable). **SUBMISSIONS PARKED** (rule 7).

**Item id:** `A1ZE` · **Family:** dafoam, ladder A, A1 (NACA0012) · **Drafted:** 2026-09-03

---

## 1. THE QUESTION, AND WHY IT IS WORTH ASKING NOW

Measured across three items (D19T, A1WR, MAAOA), all sharing a byte-identical
`system/createPatchDict` (md5 `5e89709961881491e3f05dc97bbcf75c`, lines 29 and 43
`type symmetry;`):

- the two bounding planes of these one-cell-thick 2-D meshes are **`symmetry`, not `empty`**;
- every solver log prints **`Mesh has 3 solution (non-empty) directions (1 1 1)`**, so the
  **z-momentum equation is assembled and solved on a single cell layer**;
- **`U2` is the worst residual floor and the largest last-iteration residual in every
  incompressible trace measured** — A1WR `sweep_I` floor **3.24e-08**, MAAOA `INCOMP` last
  **2.48e-08**, D19T `T10` floor **1.72e-10**, D19T `T12` where `U2` alone holds the solve up;
- **the floor scales with the mesh** — ~1.7e-10 on the coarse 4,032-cell grid, ~1.2–3.2e-08 on
  the 130,304-cell L3 grid — and that one number predicts five observed outcomes with no
  exceptions (D19T converges at 1e-8 and 1e-10 and fails at 1e-12; A1WR `sweep_I` fails at
  1e-8; MAAOA `INCOMP` fails to declare at 1e-8).

**Two things follow, and only one of them has been measured.** That `U2` caps the achievable
convergence tolerance is established. **Whether the redundant z-momentum equation also
contaminates the published `CL` and `CD` is UNMEASURED**, and this item exists to settle it by
experiment rather than by argument, because if it does, the finding reaches **every
incompressible coefficient this ladder has produced** — A1WR, MAAOA and the D19 family.

**Explicitly NOT claimed here:** that `symmetry` is *wrong* physics. It is geometrically valid
and pins the normal velocity at both planes. It is **numerically redundant** — it adds an
equation whose residual floors instead of driving to zero. Whether that redundancy is *inert*
for the coefficients is the question.

**Provenance of the patch type is INFERRED, not verified.** The repo-side ancestor
`cases/dafoam/work/NACA0012_Airfoil_Incompressible/system/createPatchDict` carries the same
md5 and an **OpenFOAM v1812** header against the image's v2506, which points to an inherited
DAFoam tutorial file rather than lab authoring. The image ships no tutorials directory and
**nothing was fetched**. Recorded as a **candidate upstream defect class**, evidence attached,
**NOT FILED and not to be filed — that decision is Sanaa's alone** (rule 7).

---

## 2. ⚠ A DESIGN TRAP IN THE OBVIOUS COMPARISON, AND HOW THIS ITEM AVOIDS IT

The natural comparator is A1WR `sweep_I` at α = 12 (`CL` 1.19079592024, `CD` 0.030665481166).
**It cannot be used as the comparator, and using it would have made this a two-variable item.**

`sweep_I` α = 12 was reached by **continuation**: its log records
`AOA_POINT_BEGIN idx=12 alpha=12.0 mode=CONTINUED continued_from=11.0`. Every point inherits
its predecessor's converged state in memory (the design behind `L-456`). **A COLD `empty` run
compared against a CONTINUED `symmetry` run differs in TWO variables — the patch type AND the
initial state.**

**Therefore this item runs its own `symmetry` COLD arm as the comparator.** The landed
continued number is retained as **context only** and is **never** the quantity a gate reads.
*This family has refused a two-variable change three times; the trap here is that the second
variable is invisible in the results table and lives only in the log.*

**A second, matching trap, avoided the same way.** The `symmetry` arm **cannot** converge to
1e-8 — its `U2` floor is 3.24e-08, measured. A tolerance-based stop would therefore let the two
arms run **different numbers of iterations**, which is a third variable. **Both arms run a
FIXED 2,000 iterations** and are compared at equal iteration count.

---

## 3. THE ARMS — ONE VARIABLE, AND IT IS TWO PATCH TYPES

**The only delta between the paired arms is the `type` entry for `symmetry1`/`symmetry2` in
`constant/polyMesh/boundary` and `system/createPatchDict`: `symmetry` → `empty`.** Same mesh
geometry, same image, same solver, same `fvSolution`, same operating point, same `endTime`,
same tolerance setting, same `np`, cold start on every arm.

| arm | mesh | cells | bounding planes | α | iterations | np |
|---|---|---|---|---|---|---|
| **`Sc`** | coarse A1 | 4,032 | **`symmetry`** (control) | 4 | 2,000 | 1 |
| **`Ec`** | coarse A1 | 4,032 | **`empty`** (treatment) | 4 | 2,000 | 1 |
| **`S3`** | A1WR L3 | 130,304 | **`symmetry`** (control) | 12 | 2,000 | 1 |
| **`E3`** | A1WR L3 | 130,304 | **`empty`** (treatment) | 12 | 2,000 | 1 |

**Two grids on purpose.** The coarse pair is minutes and tests the **mesh-scaling half** of the
account (`U2`'s floor is ~100× lower there); the L3 pair sits where the floor actually bites and
where the published coefficients live. **Each pair is internally one-variable; the two pairs
are not compared to each other.**

**Field files:** `0/U` names `symmetry1`/`symmetry2` explicitly, so the `empty` arms need the
corresponding `type empty;` entries there. **This is part of the same single change** (a patch
cannot be `empty` in the mesh and `symmetry` in the field) and is asserted, not assumed —
see `G-EMPTY`.

---

## 3b. ⚠ THIS ITEM IS THE VERIFICATION OF A LANDED COMMIT, AND CAN CONDEMN IT

**Commit `d3f47bfa50944c466ff0bad019b36a7b048a0fae`** (2026-09-03, dafoam) changed the three
A1 2-D case templates' bounding planes from `symmetry` to `empty` — `createPatchDict` md5
`5e89709961881491e3f05dc97bbcf75c` -> `b06b32856f75d4813a763af819b6149c`, plus every `0/` and
`0.orig/` field file declaring those two patches, 41 files in all. It is **forward-only**: no
run root touched, no frozen registration re-pointed, nothing re-run.

**It was committed UNVERIFIED and says so in its own message.** The verification it names is
this item. The reason it could not verify itself is recorded rather than glossed: the check
requires building a mesh in a container, and this family does not invoke a driver, launcher or
container outside the queue daemon to test its own arithmetic.

**WHAT IS UNVERIFIED, PRECISELY: that DAFoam's adjoint and IDWarp mesh warping accept `empty`
bounding planes on this case family.** The templates carry an **OpenFOAM v1812** header against
the image's v2506, which is evidence — **INFERRED, nothing fetched** — that `symmetry` came
from the upstream DAFoam tutorial rather than from this lab. **If upstream chose `symmetry`
deliberately because the adjoint or the mesh warping requires it, `empty` will not survive
contact with IDWarp and `d3f47bfa` is wrong.**

> ### **REGISTERED CONSEQUENCE, BEFORE ANY COMPUTE: a `GATE FAIL` on `G-DIRN.E` or `G-U2.E` CONDEMNS COMMIT `d3f47bfa50944c466ff0bad019b36a7b048a0fae`, WHICH IS THEN REVERTED FORWARD.**
>
> No case built from those templates between `d3f47bfa` and this item's verdict may be treated
> as verified on the patch-identity point. **A commit whose only verification lives in another
> item's gates must say so in both places, and it does: `d3f47bfa`'s own message names this
> registration, and this section names the sha.**

---

## 4. VERDICT CLASS AND CEILING

**`VERDICT_CLASS = G-NOBAND`.** No Roache triple exists for any quantity here; the two grids
are not a refinement pair for this question (they differ in `s0`, chordwise spacing and aspect
ratio simultaneously — see `N-C9`). **Nothing this item produces is grid-converged and no band
may be claimed for any value.**

**`VERDICT_CEILING = "GATE REACHED"`.** `PASS` requires a value inside a pre-registered band
and there is none. Any grading path emitting `PASS` here is defective and its output is
`NOT A RESULT`.

Vocabulary: `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` only.

---

## 5. GATES, THRESHOLDS AND LABELS — FIXED BEFORE ANY COMPUTE

### 5.1 The mechanism gates (the boring half, near-certain, and still gated)

| gate | reads | threshold | met | not met |
|---|---|---|---|---|
| `G-DIRN.S` | control arms' `Mesh has N solution (non-empty) directions` | **N = 3**, triple `(1 1 1)` | continue | **item `NOT A RESULT`** — the premise does not reproduce |
| `G-DIRN.E` | treatment arms' same line | **N = 2** | continue | **arm `GATE FAIL`** — the change did not take effect |
| `G-U2.S` | control arms' per-equation `initRes` | `U2` **present** | continue | **item `NOT A RESULT`** |
| `G-U2.E` | treatment arms' per-equation `initRes` | `U2` **absent from every printed block** | `GATE REACHED` for that arm | `GATE FAIL` |
| `G-EMPTY` | mesh + field files of treatment arms | both planes `empty` in `constant/polyMesh/boundary` **and** in every `0/*` field | continue | **arm `BLOCKED`**, not run |

### 5.2 `G-STAT` — the stationarity precondition, and it gates the coefficient comparison

**No coefficient comparison is admissible until both arms are shown stationary.** `L-453`: a
gate that samples an unsteady quantity at one instant reports a draw from a distribution.

**Read the last 10 printed `CL`/`CD` samples of each arm. Required: relative spread
`(max−min)/|mean|` ≤ `2 ×` the measured drift anchor in §5.3 for that quantity.** An arm
failing `G-STAT` makes **the coefficient comparison `NOT A RESULT`** — never a value.

### 5.3 THE NOISE ANCHOR — MEASURED, AND THE REJECTED ANCHORS NAMED

**Anchor: A1WR `sweep_I`, L3, fixed geometry, last 10 printed iterations —
`CL` relative spread `3.310e-03`, `CD` relative spread `5.735e-04`.**

**⚠ D19T `T08` and `T12` are REJECTED as anchors and the reason is registered now**: both are
**finite-difference programs whose `CL`/`CD` prints span perturbed geometries**, so their
spread (`T08` `CD` 4.18e-02) measures the FD perturbation, not numerical drift. **Using them
would have inflated the noise floor by ~70× and made contamination undetectable.** The anchor
must come from a fixed-geometry segment, and `sweep_I`'s is the only measured one available.

### 5.4 `G-COEF` — THE GATE THAT MATTERS

Per pair, on the **mean of the last 10 stationary samples**,
`Δrel = |mean_E − mean_S| / |mean_S|`:

| band | `CL` | `CD` | label |
|---|---|---|---|
| **within measured drift** | `Δrel ≤ 3.310e-03` | `Δrel ≤ 5.735e-04` | **`GATE REACHED` — NO CONTAMINATION DETECTED at this instrument's resolution** |
| **indeterminate** | `3.310e-03 < Δrel ≤ 3.310e-02` | `5.735e-04 < Δrel ≤ 5.735e-03` | **`NOT A RESULT`** — the movement is larger than drift and smaller than 10× drift; **this instrument cannot separate them and says so instead of choosing** |
| **contamination** | `Δrel > 3.310e-02` | `Δrel > 5.735e-03` | **`GATE FAIL` — CONTAMINATION.** The redundant z-momentum equation moves the published coefficients, and the finding reaches every incompressible number in this ladder |

**The middle band is deliberate.** A binary threshold on a noisy quantity manufactures a
confident answer where the instrument has none; **registering the indeterminate band in advance
is what stops a 4× movement being argued either way after the fact.**

### 5.5 Cost and placement gates

| gate | threshold |
|---|---|
| `G-CAP` | arm `core_min` ≤ its §6 cap, else `GATE FAIL` |
| `G-CEIL` | summed `core_min` ≤ **100.0 core-min**, checked after every arm, else chain stops (rule 12) |
| `G-BUDGET` | at launch, per arm: `TMO > 0` **and** `TMO×ranks/60 ≥ 3.0 × predicted_quiet` **and** exact back-check |
| **`G-OCC`** | **see §7** |
| `G-NP` | every arm `np = 1` |

---

## 6. COST — ESTIMATE AS A FUNCTION OF OCCUPANCY; CAP SIZED AT THE REGISTERED MAXIMUM

### 6.1 Anchors — INCOMPRESSIBLE ONLY

The compressible contention factor (3.1198x) must NOT be used here and is named so it cannot
be reached for by mistake: importing a compressible rate into an incompressible cost basis is
the scope error of `L-454`.

| figure | value | basis |
|---|---|---|
| incompressible L3, np=1, **3-way** | **2.36 it/s** | **MEASURED** (`S-26`/`S-27`) |
| incompressible L3, np=1, **8-way** | `cold_I_4`: 1,800 it / 3206.51 s = **0.5614 it/s** | **MEASURED**, `A1WR/STAGE12/CHAIN_LEDGER.tsv` |
| rate model | `rate(n) = 2.36 x (n/3)^-1.4641` | **DERIVED** from those two MEASURED points; deadline sizing only, never a result |
| coarse 2,000 it, np=1, 3-way | ~14 s | **DERIVED** from D19T `T12`'s `ExecutionTime 3.62 s` at iteration 500 |

**THE ESTIMATE IS STATED AS A FUNCTION OF OCCUPANCY, never as one number.**

| occupancy | rate (it/s) | L3 arm wall | L3 arm core-min | coarse arm core-min | basis of the rate |
|---|---|---|---|---|---|
| solo (n=1) | 11.789 | 169.6 s | **2.83** | 0.039 | EXTRAPOLATED |
| n=2 | 4.273 | 468.1 s | **7.80** | 0.108 | EXTRAPOLATED |
| **n=3** | **2.360** | 847.5 s | **14.12** | 0.233 | **MEASURED** |
| **n=8** | **0.5614** | 3,562.9 s | **59.38** | 0.980 | **MEASURED** |
| **n=14 (registered maximum)** | **0.2474** | 8,084.0 s | **134.73** | **2.226** | **EXTRAPOLATED BEYOND THE MEASURED SPAN** |

**WEAKEST NUMBER IN THIS DOCUMENT, FLAGGED: `rate(14) = 0.2474 it/s` extrapolates a power law
roughly an octave past the last measured point (n=8).** Every figure in the n=14 column
inherits that weakness. It is used only to size a deadline conservatively, never to claim a
cost, and the certificate reports predicted-versus-actual against it — which is precisely the
calibration payoff Sanaa's 2026-09-03 ~21:00Z rule exists to collect.

### 6.2 THE CAP RULE, AND THE READING THAT WAS REJECTED

The solver receives `cap - CAP_MARGIN_S x ranks / 60` = **`cap - ranks`**, never `cap` (`L-452`).
Caps are set on the **effective** budget.

**Two readings of "3x envelope at the registered maximum occupancy" were evaluated and they
differ by 2.4x on the L3 arms:**

- **(A) PRODUCT** — `effective >= 3.0 x estimate-at-n=14`. Gives L3 caps of **405.5** core-min
  and a cap sum of **827.0**, for an item whose solo cost is 2.83 core-min per arm. **REJECTED:
  it compounds two margins that answer different questions.** The occupancy factor already
  carries the contention allowance (n=14 is 9.5x slower than solo); multiplying by a further 3
  makes the effective budget ~28x the solo runtime, and a deadline that generous has stopped
  protecting anything. Sanaa's ceiling is meant to be far above the estimate; **the cap is not
  the ceiling.**
- **(B) MAX — ADOPTED** — `effective >= max(3.0 x solo estimate, 1.25 x wall-at-n=14)`. **The
  3x envelope covers ESTIMATE uncertainty; the occupancy clause covers CONTENTION. They are
  different risks, so the binding constraint is the MAX of the two, never their product.**

### 6.3 The table, EVALUATED — `CAP_MARGIN_S = 60`, `SAFETY = 1.25`, envelope `3.0x`, max occupancy `n = 14`

| arm | solo est | est @ n=14 | required effective | **cap** | `TMO` | back-check | **effective** | clauses |
|---|---|---|---|---|---|---|---|---|
| `Sc` | 0.233 | 2.226 | 2.782 | **4.0** | **180 s** | 4.000000 | **3.000** | **PASS** |
| `Ec` | 0.233 | 2.226 | 2.782 | **4.0** | **180 s** | 4.000000 | **3.000** | **PASS** |
| `S3` | 14.124 | 134.734 | 168.418 | **169.5** | **10110 s** | 169.500000 | **168.500** | **PASS** |
| `E3` | 14.124 | 134.734 | 168.418 | **169.5** | **10110 s** | 169.500000 | **168.500** | **PASS** |

**All four arms pass `TMO > 0`, `effective >= max(3x solo, 1.25x wall@14)`, and the exact
back-check. Evaluated 2026-09-03, not asserted.**

| quantity | value |
|---|---|
| cap sum | **347.0 core-min** |
| predicted @ n=14 (the registered figure) | **273.92 core-min** |
| predicted solo | 5.74 core-min |
| **ITEM CEILING** | **360.0 core-min**, checked after every arm, **below the cap sum by design** |
| fleet safety ceiling | **min(3x cap, remaining box budget)** per arm, monitor-enforced, graceful stop regardless of residual trend (Sanaa ~21:00Z) |
| dollars | predicted **$0.2342**, ceiling **$0.3078** — **DERIVED at $0.0513/core-h, never measured** |

**Calibration row OWED to `docs/COST_CALIBRATION.md` at item completion**, and it is unusually
valuable here because it tests `rate(14)` against reality for the first time.

---

## 7. `G-OCC` — THE OCCUPANCY GATE **QUEUES; IT NEVER REFUSES**

Sanaa ~21:00Z: resource gates *"queue, don't launch. But queueing is not blocking; the run
stays scheduled."* Sanaa ~22:00Z: *"box should never be idle."* **`G-OCC` therefore never
returns a refusal and never consumes an entry.**

At launch and at every arm boundary the launcher measures occupancy `n` and `MemAvailable`
(from a reader first proved able to return a non-zero), **records both in `ledger.txt`**, and
**queues** — leaving the row in place, scheduled — only while

```
TMO  <  1.25 x iterations / rate(n)
```

Evaluated for the L3 arms at `TMO = 10110 s`, 2,000 iterations:

| occupancy `n` | required wall | decision |
|---|---|---|
| 8 | 4,453 s | **LAUNCH** |
| 12 | 8,063 s | **LAUNCH** |
| **14 (registered maximum)** | **10,105 s** | **LAUNCH** |
| 16 | 12,287 s | **QUEUE** |
| 20 | 17,035 s | **QUEUE** |

**The boundary falls exactly at the registered maximum occupancy, which is what "sized at the
registered maximum" means when it is done honestly** — the deadline covers n=14 with 5 s to
spare and does not pretend to cover n=16.

---

## 8. PLANTED-ZERO CONTROLS — EVERY FIXTURE STATIC AND INDEPENDENT OF THE GRADED RUN

`L-435`: **not one control reads anything produced by this item's own solves.** Fixtures are
authored at freeze, stored at `<item>/controls/`, md5-pinned in the frozen document.

| control | reader under test | static fixture | must return | else |
|---|---|---|---|---|
| `P1` | solution-directions reader | `P1_dirn3.log` / `P1_dirn2.log` — frozen lines with `3 ... (1 1 1)` and `2 ... (1 1 0)` | **distinguish them** | `CONTROL_READER_NOT_BORN` |
| `P2` | per-equation `initRes` reader | `P2_eqs.log` — frozen block with `U2 initRes: 3.0000e-04` among five others | `U2 = 3.0000e-04` | `CONTROL_READER_NOT_BORN` |
| `P2n` | same reader, **negative leg** | `P2n_noU2.log` — frozen block with `U0`,`U1`,`p`,`nuTilda` and **no `U2`** | **`U2` absent** | `CONTROL_READER_ALWAYS_FIRES` |
| `P3` | `CL`/`CD` series reader | `P3_coef.log` — 12 frozen `CL:`/`CD:` lines, known mean and spread | mean and spread to 1e-12 | `CONTROL_READER_NOT_BORN` |
| `P4` | `G-STAT` spread test | `P4_stationary.log` (spread 1e-9) and `P4_swinging.log` (spread 0.5) | **PASS one, FAIL the other** | `CONTROL_GATE_STUCK` |
| `P5` | patch-type reader | `P5_symmetry` / `P5_empty` — frozen `boundary` excerpts | distinguish them | `CONTROL_READER_NOT_BORN` |

**`P2n` and `P4` are two-sided because a reader that always finds `U2`, or a gate that always
says "stationary", is exactly as blind as one that never does** — `L-452`'s addendum: a gate
never shown to return **both** answers is not a gate.

**Asserted by EXECUTION at grade time:** every fixture's md5 == its pin; every fixture's
`mtime` **older than the run root**; no fixture inside the run root. **Any control refusal makes
the whole item `NOT A RESULT`**; no reader may be substituted.

---

## 9. THE REGISTERED PREDICTION — THE BORING OUTCOME, BEFORE THE ANSWER EXISTS

| gate | **PREDICTION** | what would **REFUTE** it |
|---|---|---|
| `G-DIRN.E` | **2 solution directions** on the `empty` arms | 3 → the change did not take effect; arm `GATE FAIL` |
| `G-U2.E` | **`U2` absent entirely** — no equation, so no residual and no floor | `U2` still printed → the mechanism is not the patch type and the whole account is wrong |
| convergence | the `empty` arms' max-over-equations residual **falls below the `symmetry` arms' floor** at equal iteration count | it does not → `U2` was not what capped the tolerance |
| **`G-COEF`** | **⚠ THE REGISTERED PREDICTION IS THE BORING ONE: `CL` and `CD` are UNCHANGED, `Δrel` inside the measured drift (`CL` 3.310e-03, `CD` 5.735e-04). The only thing that changes is that the solve converges.** | `Δrel` above 10× drift → **CONTAMINATION**, and every incompressible coefficient in this ladder is affected |

**Why the boring outcome is the registered one.** The exciting result — *"a one-word patch-type
change invalidates the ladder's published coefficients"* — would flatter this team enormously
and would be the most-cited finding of the fortnight. **That is exactly why it is not what is
predicted.** `U2`'s magnitude is pinned near zero by the symmetry conditions themselves, so the
physical expectation is that its redundant equation is **inert** for the integrated forces even
while its residual floors. **Recorded now so it cannot be reframed as a prediction afterwards:
the drafter expects no contamination and expects this item to close the question rather than
open one.**

---

## 10. WHAT THIS ITEM CANNOT DO

1. **It cannot produce a grid-converged anything** (§4).
2. **It cannot detect contamination below the measured drift.** A real movement smaller than
   3.310e-03 (`CL`) is invisible to this instrument and the item says so rather than reporting
   zero. **A null here is bounded, not absolute.**
3. **It cannot settle the compressible failure.** `A1WR sweep_C` fails with `p` floored at
   3.16e-01 — a different and more violent mechanism (`N-C9`), and `U2` is not its largest
   residual. **The disconfirming arm is named here so this item is not later read as explaining
   it.**
4. **It cannot re-grade any landed verdict.** Whatever it finds, existing verdicts move only by
   a ruling above this team.

---

## 11. OPEN ITEMS FOR THE SUPERVISOR BEFORE FREEZE

1. **The cap table (§6.2) is evaluated but yours to ratify** — §3 check 4.
2. **`S3`/`E3` sit at `1.05×` on the 6-way clause.** Tightest number in the item; raising both
   caps to 60.0 would give ~1.23× at +16 core-min of ceiling.
3. **The 3×-envelope conflict in §6.2 is real** — 3× the quiet estimate does not cover the
   measured 8-way case, and `G-OCC` is doing that work instead. If you want the envelope to
   cover 8-way unconditionally, the L3 caps must go to ~76.0 and the ceiling to ~150.
4. **The coarse pair's operating point is α = 4** (D19T's) and the L3 pair's is **α = 12**
   (`sweep_I`'s). Deliberate — each pair is compared only within itself.
5. **`G-COEF`'s 10× contamination multiplier is a judgement**, not a measurement. The 1× band
   edge is measured; the 10× edge is chosen to leave an honest indeterminate zone.
6. **The `createPatchDict` upstream attribution stays INFERRED** and is **NOT FILED** (rule 7).

**SUBMISSIONS PARKED. Nothing here is sent, filed, uploaded, registered or posted outside this
box.**
