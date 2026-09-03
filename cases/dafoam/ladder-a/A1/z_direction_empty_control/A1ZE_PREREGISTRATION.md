# A1ZE — `empty` VERSUS `symmetry` ON THE TWO BOUNDING PLANES — **PRE-REGISTRATION, FROZEN**

> ## ✅ FROZEN 2026-09-03. ZERO COMPUTE HAS BEEN SPENT. NO RUN ROOT EXISTS. NO QUEUE ROW IS FILED.
>
> Gates, thresholds, caps, labels, the verdict class and the verdict ceiling are **fixed at this
> commit** (rule 2). The grading path is fixed here too: `a1ze_grade.py`, md5
> **`9b755c3b1a043879a664853a3d747c53`**, is the only path allowed to emit an A1ZE verdict.
>
> **Condition checked by execution at freeze:** the run root
> `/home/ubuntu/certonomous-runs/A1ZE` **does not exist**, and no `Sc/Ec/S3/E3` unit directory
> exists anywhere. Amendments therefore remain legal under rule 2 until first compute, and each
> must state its condition and how it was checked. After first compute, gates close and changes
> land only as dated addenda that cannot alter a gate, threshold, cap or label.
>
> **The queue row is PARKED, not filed** — `A1ZE_QUEUE_ROW.parked.json` beside this document,
> outside `verification/queue/`. It enters the queue only after `dafoam-supervisor`'s personal
> `SUPERVISION_CHARTER.md` §3 check 4, which is not delegable. **SUBMISSIONS PARKED** (rule 7).

**Item id:** `A1ZE` · **Family:** dafoam, ladder A, A1 (NACA0012) · **Frozen:** 2026-09-03

---

## 0. WHAT CHANGED FROM THE DRAFT, AND WHY — READ THIS FIRST

This supersedes `PREREGISTRATION_DRAFT.md` (landed unfrozen at `2ecc50be`, revised at
`d880cf7e`). Full register in §11. **Three corrections are load-bearing. Two were found by this
lane re-executing the draft's own anchors against the artifacts on disk rather than accepting
them. The third is the supervisor's, it arrived mid-pass, it falsifies the premise this item was
drafted on, and it is the most important of the three** — so it is stated first.

**CORRECTION 0 — THE CONVERGENCE MECHANISM IS FALSIFIED, AND A GATE THAT WOULD HAVE FALSELY
CONDEMNED A CORRECT COMMIT IS REMOVED.** `dafoam-supervisor` measured on D19T's own logs that
`U2` is **not in the quantity the solver declares convergence on**: `T10` declared 22 times at
~9.04e-11 while `U2`'s best value over the whole run was 1.716383e-10 — 1.72× above its own
tolerance. This lane re-derived it independently in the quantity the solver actually tests
(`min over iterations of max over channels`), confirmed it, and **extended it to A1WR, where it had
not been tested: all 14 α points miss 1e-8 even with `U2` excluded.** So *"removing `U2` restores
convergence"* is a prediction already measured false, and the draft carried it. It is removed as a
gate, split into two REPORTED channels, and §3b.0 now states narrowly what a `GATE FAIL` condemns
`d3f47bfa` **for** — the assembly facts — and what it explicitly does **not**. Full derivation in
§1a. **The supervisor's read here was right and this lane's draft was wrong; the record says so in
that direction because that is the direction the evidence ran.**

**CORRECTION 1 — THE DRIFT ANCHOR WAS TAKEN FROM THE WRONG ANGLE OF ATTACK, AND IT WAS THE
WORST ONE IN THE SWEEP.** The draft registered `CL` 3.310e-03 / `CD` 5.735e-04 as "A1WR
`sweep_I`, L3, fixed geometry, last 10 printed iterations". Re-derived by execution, those two
figures reproduce **exactly** — `3.3096549607706817e-03` and `5.734690681545189e-04` — but they
are the last 10 prints **of the whole log**, which fall inside **α = 13**: the sweep's *final*
segment, **26 prints where every other segment has 41**, cut short by the `SIGTERM` at
02:25:05.618Z, and never settled after its continuation from α = 12. **The L3 arms of this item
run at α = 12, whose own measured last-10 drift is `CL` 4.830552e-04 / `CD` 1.116421e-04.** The
draft's band was therefore **6.85× too wide on `CL` and 5.14× too wide on `CD`** at the operating
point it grades — it would have called "no contamination" on a movement nearly seven times larger
than the instrument's actual resolution there.

*This is the same error class the draft had just rejected one paragraph earlier.* §5.3 of the
draft correctly threw out D19T `T08`/`T12` as anchors because their spread measures an FD
perturbation rather than numerical drift — and then adopted an anchor whose spread measures an
unsettled continuation transient in a truncated segment. **The rejected anchors were named; the
adopted one was not checked the same way.**

**CORRECTION 2 — THE 8-WAY COST ANCHOR IS 6-WAY, ITS CITED ARTIFACT DOES NOT CONTAIN IT, AND THE
3-WAY ANCHOR HAS NO ARTIFACT AT ALL.**

- `0.5614 it/s` was cited to `A1WR/STAGE12/CHAIN_LEDGER.tsv`. **That file does not contain it.**
  Its `cold_I_4` row holds `wall_s 3317`, `rc 97`, `core_min 55.2833`. The figure lives in
  `cold_I_4/out/sweep.log` — `Time = 1800`, `ExecutionTime = 3206.51 s` — and the arm it comes
  from was **deadline-killed**, which is legitimate for a *rate* and must be said.
- **"8-way" is false against the ledger's own timestamps.** `probe_I` ended `18:34:58Z` and
  `probe_C` ended `18:35:58Z`; the six `COLD` units launched `18:35:59–18:36:01Z`. **Six ran
  concurrently, not eight.** The count came from counting the ledger's eight rows.
- `2.36 it/s at 3-way`, the anchor the whole `3.0×` envelope leg multiplies, is cited to
  `S-26`/`S-27`. **`S-27` §4 states it only as prose, with no artifact, and it could not be
  reproduced from any A1WR run artifact on disk.** The only L3 / np=1 / incompressible rates that
  *do* cite an artifact are `1.6496 it/s` (`probe_I`, 2 concurrent units) and `0.5614 it/s`
  (`cold_I_4`, 6 concurrent units). **A board sentence is not an artifact.**

The rate model is refitted on the two anchors that cite artifacts. **The refit lands almost
exactly where the draft was** — `rate(14)` central `0.2445` against the draft's `0.2474` — because
the two label errors partly cancelled. **That is luck, and it is recorded as luck.** What did move
is the fitted exponent, from **−1.4641 to −0.9812**, and that is the physically expected shape:
an exponent near −1 is throughput saturation on a fixed core count, whereas −1.46 asserts
*super-linear* degradation nobody measured. **The caps move too: `S3`/`E3` from 254.0 to 257.0,
because the draft's cap did not in fact cover its own corrected requirement.**

**Where the supervisor's brief for this correction pass was wrong, said plainly:** it located the
two corrections in board block `S-29`. They are not there. `S-29` §3 records only the reciprocal
condemnation link; the phrase "its two corrections" appears in `S-30` §3 item 2 and is a
back-reference to commit `d880cf7e`'s two — the extrapolated binding clause and the `pred_quiet`
label — **both of which were already applied before this lane opened the file.** The two above are
different defects, found by re-execution, and neither was known to the record.

---

## 1. THE QUESTION, AND WHY IT IS WORTH ASKING NOW

Measured across three incompressible items (D19T, A1WR, MAAOA), all sharing a byte-identical
`system/createPatchDict` (md5 `5e89709961881491e3f05dc97bbcf75c`, lines 29 and 43
`type symmetry;`):

- the two bounding planes of these one-cell-thick 2-D meshes are **`symmetry`, not `empty`**;
- every solver log prints **`Mesh has 3 solution (non-empty) directions (1 1 1)`**, so the
  **z-momentum equation is assembled and solved on a single cell layer**;
- **`U2` is the largest printed residual in every incompressible trace measured** — A1WR `sweep_I`
  floor **3.238410485530894e-08** (re-derived by this item's own frozen reader over all 559 print
  steps of `/home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_I/out/sweep.log`, matching
  `A1WR_STAGE12_RESULTS.md` §16, and the largest last-iteration residual at 12 of 14 points),
  MAAOA `INCOMP` last **2.48e-08**, D19T `T10` floor **1.716383e-10**;
- **the floor scales with the mesh** — ~1.7e-10 on the coarse 4,032-cell grid, ~1.2–3.2e-08 on the
  130,304-cell L3 grid.

**That is the whole of what is established. The convergence half of the story is NOT, and §1a is
the reason this registration exists in the shape it does.**

### ⚠⚠ 1a. THE CONVERGENCE MECHANISM IS **FALSIFIED**, MEASURED, BEFORE THIS ITEM FREEZES — AND THAT REMOVES A GATE THAT WOULD HAVE FALSELY CONDEMNED A CORRECT COMMIT

The account this item was drafted against held that `U2`'s floor caps the achievable tolerance and
so explains five non-convergences. **`dafoam-supervisor` measured that it does not, on D19T's own
logs; this lane re-derived it independently and then extended it to A1WR, where it had not been
tested.** Both derivations are on artifacts, not on a source read.

**The quantity a solver actually tests is `min over iterations of (max over channels)`, not the
per-channel minimum over a whole run** — channel minima are attained at different iterations and
may never be attained jointly. Re-derived in that quantity from
`/home/ubuntu/certonomous-runs/CURRICULUM-D19T-…/T{08,10,12}_*.log`:

| arm | tol | declarations | best declared | **min-over-it max, ALL channels** | **same, U2 EXCLUDED** | binding channel |
|---|---|---|---|---|---|---|
| `T08` | 1e-8 | **22** | 9.087147e-09 | **1.466042e-08** — *above tol* | **9.089292e-09** | `he` |
| `T10` | 1e-10 | **22** | 9.038369e-11 | **1.967098e-10** — *above tol* | **9.034983e-11** | `he` |
| `T12` | 1e-12 | **0** | — | 5.729091e-09 | **1.743972e-12** — *still above tol* | **`p`** |

**`U2` IS NOT IN THE DECLARED QUANTITY, and the proof needs no source.** `T10` declared convergence
22 times at ~9.04e-11 while `U2`'s *best value over the entire run* was 1.716383e-10 — **1.72×
above its own tolerance.** A maximum over a set can never fall below the minimum ever attained by a
member of that set, so `U2` is not a member. Excluding it reproduces the declared number to four
significant figures in both converging arms and identifies the binding channel as `he`. **And
`T12`'s zero declarations are `p`'s doing, not `U2`'s — it fails even with `U2` excluded.**

**THIS LANE'S EXTENSION, ON A1WR, WHICH NOBODY HAD MEASURED.** Same quantity, per α segment of
`sweep_I/out/sweep.log`: **all 14 points fail 1e-8 even with `U2` excluded.** The best U2-excluded
per-iteration max over the whole sweep is **1.340732e-08** (α = 10); at this item's own operating
point α = 12 it is **2.997861e-08** against 2.058682e-07 with `U2` in. Binding channels are `U1`
and `nuTilda`, **never `U2`**. Declarations in the whole sweep: **0**.

> **REGISTERED CONSEQUENCE: removing `U2` would not have converged a single A1WR point.** The
> mechanism does not explain A1WR's 0 of 13 any more than it explains D19T's rows. **Any gate
> predicting "removing `U2` restores convergence" is registering a prediction already measured
> false, and this registration contains none.**

**What this does NOT touch, and it is the half that survives intact:** the *assembly* facts. The
planes are `symmetry`; the solver reports **3 solution directions `(1 1 1)`**; a z-momentum
equation **is** assembled and solved on a one-cell-thick mesh; `U2` **is** printed and **is** the
largest printed residual. Those are read directly off the log and off
`constant/polyMesh/boundary`, and they are what `G-DIRN` and `G-U2` gate. **A one-cell-thick 2-D
mesh should carry `empty` bounding planes on its own merits, independent of any convergence
effect.**

### 1b. WHAT IS ACTUALLY UNMEASURED, AND IT IS NOW THE CENTRE OF THIS ITEM

**Whether the redundant z-momentum equation moves the published `CL` and `CD` is UNMEASURED**, in
either direction, and no evidence above bears on it. **It is the only question here whose answer is
unknown**, and `G-COEF` is the gate that settles it.

**`A1WR sweep_C` remains a separate and disconfirming arm** and is named in the opening rather than
buried: `U2` min 5.32e-02 while **`p` min is 3.16e-01 and `p` is the largest at the last iteration
at 9.29e-01** — `N-C9`'s separate, more violent mechanism. This item's own reader measures that
arm's last-10 `CL` spread at **7.56e+00**, four orders above the incompressible arm's: the
compressible sweep is not merely differently floored, **it is not stationary at all.**

**Consequence for the gates:** every gate below is written so the **disconfirming answer is
reachable and is a registered outcome**. `G-DIRN.S`/`G-U2.S` return `NOT A RESULT` if the premise
itself fails to reproduce; `G-COEF` has an explicit `NOT A RESULT` middle band; the residual
comparison is **REPORTED, never gated** (§5.1a). **No gate here can only agree with the account.**

**Explicitly NOT claimed here:** that `symmetry` is *wrong* physics. It is geometrically valid and
pins the normal velocity at both planes. It is **numerically redundant**. Whether that redundancy
is *inert* for the coefficients is the question.

**Provenance of the patch type is INFERRED, not verified.** The ancestor `createPatchDict` carries
an **OpenFOAM v1812** header against the image's v2506, which points to an inherited DAFoam
tutorial file rather than lab authoring. **Nothing was fetched.** Recorded as a candidate upstream
defect class, **NOT FILED and not to be filed — that decision is Sanaa's alone** (rule 7).

---

## 2. ⚠ THREE DESIGN TRAPS IN THE OBVIOUS COMPARISON, AND HOW THIS ITEM AVOIDS THEM

**TRAP 1 — the landed comparator is a CONTINUED run.** A1WR `sweep_I` α = 12 (`CL`
1.19079592024, `CD` 0.030665481166) records `AOA_POINT_BEGIN idx=12 alpha=12.0 mode=CONTINUED
continued_from=11.0`. **A cold `empty` run against a continued `symmetry` run differs in TWO
variables.** *Therefore this item runs its own `symmetry` COLD arm as the comparator*, and the
landed continued number is context only, never a quantity a gate reads.

**TRAP 2 — a tolerance-based stop is a third variable.** Nothing here assumes *which* arm converges
first, or that either does; the measured record says A1WR's L3 configuration reaches 1e-8 on no
channel combination at any α (§1a), so a tolerance stop could leave the two arms at wildly
different iteration counts, or leave both running to `endTime` for different reasons. **Both arms
of a pair therefore run a FIXED 2,000 iterations** and are compared at equal iteration count.
**`G-TOL` enforces it by execution** — it refuses the comparison if either log carries a
tolerance-satisfied line, whichever arm carries it. *The justification is equal-iteration
comparison and nothing else; it does not rest on the falsified convergence account.*

**TRAP 3 — the base template inverted under this item's feet.** See §3.

---

## 3. THE ARMS — ONE VARIABLE, AND IT IS TWO PATCH TYPES

**The only delta between the paired arms is the `type` entry for `symmetry1`/`symmetry2` in
`constant/polyMesh/boundary`, `system/createPatchDict`, and every `0/` and `0.orig/` field file
declaring those patches.** Same mesh geometry, same image, same solver, same `fvSolution`, same
operating point, same iteration count, same `np`, cold start on every arm.

| arm | mesh | cells | bounding planes | α | iterations | np | built by |
|---|---|---|---|---|---|---|---|
| **`Sc`** | coarse A1 | 4,032 | **`symmetry`** (control) | 4 | 2,000 | 1 | **mutation of HEAD** |
| **`Ec`** | coarse A1 | 4,032 | **`empty`** (treatment) | 4 | 2,000 | 1 | HEAD template, unmodified |
| **`S3`** | A1WR L3 | 130,304 | **`symmetry`** (control) | 12 | 2,000 | 1 | **mutation of HEAD** |
| **`E3`** | A1WR L3 | 130,304 | **`empty`** (treatment) | 12 | 2,000 | 1 | HEAD template, unmodified |

### ⚠ 3a. THE CONTROL IS NOW THE MUTATED ARM, AND THAT IS THE WHOLE POINT

**TRAP 3, and the draft carried it.** The draft stated the delta as `symmetry → empty`, which
presumes the templates are `symmetry`. **Since `d3f47bfa` they are not.** Verified by execution at
freeze:

| object | md5 | patch type |
|---|---|---|
| `cases/dafoam/work/NACA0012_Airfoil_Incompressible/system/createPatchDict` at **HEAD** | `b06b32856f75d4813a763af819b6149c` | `empty` at lines 29 and 43 |
| the same path at **`d3f47bfa^`** | `5e89709961881491e3f05dc97bbcf75c` | `symmetry` at lines 29 and 43 |

**So the TREATMENT arms are HEAD as it stands, built with no modification whatever, and the
CONTROL arms are the deliberate reversion to the ancestor.** That is the stronger design and it is
the one this item needs: `G-DIRN.E` and `G-U2.E` then test **the shipped state of the repository**,
which is exactly what condemning or clearing `d3f47bfa` requires. A design in which the treatment
was hand-patched would test a hand-patch, not the commit.

**Registered construction, and the driver asserts it before any solve:** `Ec`/`E3` copy the HEAD
template and assert `createPatchDict` md5 == `b06b3285…`; `Sc`/`S3` copy the same template, apply
the two-line reversion, and assert md5 == `5e897099…`. **Both arms of a pair are built from the
same parent commit in the same invocation.** `G-EMPTY` then re-reads the built mesh and every `0/`
field from disk and refuses the arm (`BLOCKED`) unless both planes carry the arm's registered type
in *every* file — a patch cannot be `empty` in the mesh and `symmetry` in the field, and neither
OpenFOAM nor this gate accepts the combination.

**Two grids on purpose.** The coarse pair is minutes and tests the mesh-scaling half of the account
(`U2`'s floor is ~100× lower there); the L3 pair sits where the floor bites and where the published
coefficients live. **Each pair is internally one-variable; the two pairs are never compared to each
other.**

---

## 3b. ⚠ THIS ITEM IS THE VERIFICATION OF A LANDED COMMIT, AND CAN CONDEMN IT

**Commit `d3f47bfa50944c466ff0bad019b36a7b048a0fae`** (2026-09-03, dafoam) changed the three A1 2-D
case templates' bounding planes from `symmetry` to `empty` — `createPatchDict` md5
`5e89709961881491e3f05dc97bbcf75c` → `b06b32856f75d4813a763af819b6149c`, plus every `0/` and
`0.orig/` field file declaring those two patches, 41 files in all. It is **forward-only**: no run
root touched, no frozen registration re-pointed, nothing re-run.

**It was committed UNVERIFIED and says so in its own message.** The verification it names is this
item. The reason it could not verify itself is recorded rather than glossed: the check requires
building a mesh in a container, and this family does not invoke a driver, launcher or container
outside the queue daemon to test its own arithmetic.

**WHAT IS UNVERIFIED, PRECISELY: that DAFoam's adjoint and IDWarp mesh warping accept `empty`
bounding planes on this case family.** The templates carry an **OpenFOAM v1812** header against the
image's v2506, which is evidence — **INFERRED, nothing fetched** — that `symmetry` came from the
upstream DAFoam tutorial rather than from this lab. **If upstream chose `symmetry` deliberately
because the adjoint or the mesh warping requires it, `empty` will not survive contact with IDWarp
and `d3f47bfa` is wrong.**

> ### **REGISTERED CONSEQUENCE, BEFORE ANY COMPUTE: a `GATE FAIL` on `G-DIRN.E` or `G-U2.E` CONDEMNS COMMIT `d3f47bfa50944c466ff0bad019b36a7b048a0fae`, WHICH IS THEN REVERTED FORWARD.**
>
> No case built from those templates between `d3f47bfa` and this item's verdict may be treated as
> verified on the patch-identity point. The frozen grader prints the sha verbatim on either
> `GATE FAIL` branch, so the condemnation is emitted by the instrument and not composed afterwards
> by a reader.

### ⚠ 3b.0 WHAT A `GATE FAIL` CONDEMNS `d3f47bfa` **FOR**, STATED NARROWLY SO IT CANNOT BE A FALSE CONDEMNATION

Both condemning gates are **assembly facts read off the solver's own output**, and neither is a
convergence claim:

- **`G-DIRN.E` `GATE FAIL`** = the solver still reports **3 solution directions** on a mesh whose
  bounding planes the commit made `empty`. **Condemns:** *the byte change did not reach the
  solver's mesh.*
- **`G-U2.E` `GATE FAIL`** = a `U2` equation is **still assembled and printed**. **Condemns:** *the
  z-momentum equation is still being solved on a one-cell layer, so the commit did not do the one
  thing it was made to do.*
- **`G-EMPTY` `BLOCKED`** on a treatment arm = the mesh could not be built, or IDWarp/the adjoint
  refused `empty`. **That is the upstream-deliberate hypothesis confirmed, and it condemns
  `d3f47bfa` as well** — recorded here in advance so the `BLOCKED` label cannot later be argued as
  merely infrastructural.

> **AND WHAT A `GATE FAIL` DOES *NOT* CONDEMN IT FOR, REGISTERED BEFORE ANY COMPUTE:**
> **failing to change convergence, failing to lower a declared residual, or failing to move `CL`
> or `CD`.** §1a measures that `U2` is not in the declared quantity, so removing it *cannot* move
> that quantity; **a gate keyed to that effect would condemn a correct commit for failing to do
> something it was never able to do.** No such gate exists in this registration. `G-COEF` grades
> the coefficient question on its own terms and **its verdict, whatever it is, does not reach
> `d3f47bfa`** — a coefficient movement would be a finding about the ladder's numbers, not a
> defect in the commit.

**Independent of every gate above:** a one-cell-thick 2-D mesh should carry `empty` bounding
planes. If every gate here comes back clean, the commit is verified on the point it was made for,
and no wider claim is licensed.

### 3b.1 THE CLAUSE NOW STANDS AT BOTH ENDS, AND ONE END WAS MISSING

**Checked by execution at freeze.** A repository-wide search for the sha across `cases/dafoam/`,
`docs/dafoam/`, `docs/LESSONS.md`, `docs/LAB_STATE.md` and `docs/NUMERICS_KNOWLEDGE.md` returned
**this document and the board block `S-29` §3 only**. The `d3f47bfa` end carried the clause **in
its commit message alone** — real, but reachable only by someone who already knows to run
`git show`, and invisible to anyone opening a template.

**Written at freeze, and it is the other end:**
`cases/dafoam/PATCH_IDENTITY_D3F47BFA_UNVERIFIED.md`, with a pointer file
`README_PATCH_IDENTITY.md` inside each of the three template directories, so a reader who opens a
template finds the note without knowing the sha exists.

**⚠ A defect the brief did not anticipate, found while checking the other end:** `d3f47bfa`'s own
message names *"`A1ZE`'s **MESHA**/`Ec` arms"* as its verification. **`A1ZE` has no arm called
`MESHA`** — it has `Sc`, `Ec`, `S3`, `E3`. `MESHA` is an arm of a different item (`A1WCT`). The
commit is frozen history and is not edited; the correction is recorded here and in the note at the
other end, and the arms that actually verify it are **`Ec` and `E3`**.

---

## 4. VERDICT CLASS AND CEILING

**`VERDICT_CLASS = G-NOBAND`.** No Roache triple exists for any quantity here; the two grids are
not a refinement pair for this question (they differ in `s0`, chordwise spacing and aspect ratio
simultaneously — see `N-C9`). **Nothing this item produces is grid-converged and no band may be
claimed for any value.**

**`VERDICT_CEILING = "GATE REACHED"`.** `PASS` requires a value inside a pre-registered band and
there is none. The frozen grader **refuses (exit 2) and prints `NOT A RESULT`** if its own logic
ever reaches `PASS`.

Vocabulary: `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` only.

---

## 5. GATES, THRESHOLDS AND LABELS — FIXED BEFORE ANY COMPUTE

**Every gate below is a PHYSICS or ill-posedness gate, or a cost gate that is graded after the
fact and never blocks a launch** (Sanaa 2026-09-03 ~21:00Z and ~22:00Z). `G-OCC` §7 queues and
never refuses. Nothing here can block a run for a non-physics reason.

### 5.1 The mechanism gates

| gate | reads | threshold | met | not met |
|---|---|---|---|---|
| `G-DIRN.S` | control arms' `Mesh has N solution (non-empty) directions` | **N = 3**, triple `(1 1 1)` | continue | **item `NOT A RESULT`** — the premise does not reproduce |
| `G-DIRN.E` | treatment arms' same line | **N = 2** | `GATE REACHED` | **`GATE FAIL` — CONDEMNS `d3f47bfa`** |
| `G-U2.S` | control arms' per-equation `initRes` | `U2` **present** | continue | **item `NOT A RESULT`** |
| `G-U2.E` | treatment arms' per-equation `initRes` | `U2` **absent from every printed block** | `GATE REACHED` | **`GATE FAIL` — CONDEMNS `d3f47bfa`** |
| `G-EMPTY` | built mesh **and** every `0/` field of every arm | both planes carry that arm's registered type in **every** file | continue | **arm `BLOCKED`**, not graded |
| `G-TOL` | every arm's log | **no** tolerance-satisfied line — the stop was the fixed iteration count | continue | **`GATE FAIL`** — the arms ran unequal iteration counts and the comparison is three-variable |

**Not a gate, by measurement:** there is **no** gate on "the `empty` arm converges" or "the declared
residual falls". §1a measures `U2` out of the declared quantity, so such a gate would be
unreachable by construction — the same defect as A1WR's 1e-8 against its own floor, one level up.
The residual comparison is kept and is **REPORTED** (§5.1a).

### 5.1a `R-MAXRES` and `R-DECL` — **REPORTED, NEVER GATED** (Sanaa 2026-09-03 ~20:00Z default)

| report | reads | why it is reporting and not gating |
|---|---|---|
| `R-MAXRES` | per-iteration **max over all printed channels**, both arms, at equal iteration count | The `empty` arm's printed max is *expected* to fall — `U2` is the largest printed residual at 12 of 14 A1WR points — but **that is a fact about what is printed, not about what is declared.** It cannot support a verdict and it is not allowed to. |
| `R-DECL` | `Minimal residual … satisfied the prescribed tolerance` lines, both arms, both counts | **Registered expectation: NEITHER arm declares**, because at α = 12 the U2-excluded per-iteration max floors at 2.997861e-08 against 1e-8 (§1a). If the `empty` arm *does* declare and the `symmetry` arm does not, that is a **new and unexplained fact** and is reported as one — it would mean `U2` reaches the criterion after all, contradicting D19T `T10`, and it is not folded into any gate here. |

Both attach to the certificate. Neither blocks a solve, a mesh, or a hand-off.

### 5.2 `G-STAT` — the stationarity precondition, and it gates the coefficient comparison

**No coefficient comparison is admissible until both arms are shown stationary** (`L-453`: a gate
that samples an unsteady quantity at one instant reports a draw from a distribution).

**Read the last 10 printed `CL`/`CD` samples of each arm. Required: relative spread
`(max−min)/|mean|` ≤ `2 ×` that pair's measured drift anchor in §5.3.** An arm failing `G-STAT`
makes **that pair's coefficient comparison `NOT A RESULT`** — never a value.

### 5.3 THE NOISE ANCHOR — MEASURED **AT EACH PAIR'S OWN OPERATING POINT**, WITH ITS RECIPE

**The recipe is registered, not just the number, because the number is window-sensitive by 4.6
orders of magnitude and a threshold the grader cannot re-execute is not a threshold.**

> **Recipe:** file `/home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_I/out/sweep.log`; split on
> `AOA_POINT_BEGIN idx=<i> alpha=<a>`; within one segment take the **last 10** `^CL:` and the last
> 10 `^CD:` prints as independent streams; spread = `(max − min) / |mean|`.

Re-derived by execution at freeze (all 14 segments; the file holds 559 `CL:` and 559 `CD:` prints):

| α | prints | `CL` last-10 spread | `CD` last-10 spread | |
|---|---|---|---|---|
| 0 | 41 | 9.464404e-01 | 9.190482e-03 | |
| 4 | 41 | **2.300624e-04** | **2.276654e-05** | **coarse pair's proxy anchor** |
| 8 | 41 | 1.666133e-05 | 1.468468e-05 | quietest segment in the sweep |
| 12 | 41 | **4.830552e-04** | **1.116421e-04** | **L3 pair's anchor — its own operating point** |
| 13 | **26** | 3.309655e-03 | 5.734691e-04 | **the draft's anchor. Truncated, SIGTERM-killed, unsettled** |

**Registered anchors.** L3 pair (α = 12): **`CL` 4.830552e-04, `CD` 1.116421e-04 — GATED.**
Coarse pair (α = 4): **`CL` 2.300624e-04, `CD` 2.276654e-05 — REPORTED, NOT GATED**, because those
figures are measured on **L3** and the coarse pair runs a different grid whose drift is unmeasured.
A cross-grid proxy is honest as a report and dishonest as a gate; Sanaa's ~20:00Z default settles
it as reporting.

**⚠ Anchors REJECTED, and the reason registered now.** D19T `T08`/`T12` are **finite-difference
programs whose `CL`/`CD` prints span perturbed geometries**, so their spread (`T08` `CD` 4.18e-02)
measures the FD perturbation, not drift; using them would have inflated the floor ~70×. **And the
draft's α = 13 anchor is rejected on the same principle** — it measures an unsettled continuation
transient in a segment cut short by a kill signal.

### 5.4 `G-COEF` — THE GATE THAT MATTERS

Per pair, on the **mean of the last 10 stationary samples**,
`Δrel = |mean_E − mean_S| / |mean_S|`, against that pair's own anchor `D`:

| band | threshold | label |
|---|---|---|
| **within measured drift** | `Δrel ≤ D` | **`GATE REACHED` — NO CONTAMINATION DETECTED at this instrument's resolution** |
| **indeterminate** | `D < Δrel ≤ 10 D` | **`NOT A RESULT`** — larger than drift, smaller than 10× drift; **this instrument cannot separate them and says so instead of choosing** |
| **contamination** | `Δrel > 10 D` | **`GATE FAIL` — CONTAMINATION.** The redundant z-momentum equation moves the published coefficients |

Evaluated thresholds, **L3 pair, GATED**: `CL` `GATE REACHED` ≤ 4.830552e-04, `NOT A RESULT` to
4.830552e-03, `GATE FAIL` above; `CD` `GATE REACHED` ≤ 1.116421e-04, `NOT A RESULT` to
1.116421e-03, `GATE FAIL` above. **Coarse pair, same arithmetic on 2.300624e-04 / 2.276654e-05,
REPORTED only.**

**The middle band is deliberate.** A binary threshold on a noisy quantity manufactures a confident
answer where the instrument has none. **The 10× multiplier is a stated JUDGEMENT, not a
measurement**; the 1× edge is measured.

### 5.5 Cost and placement gates — **graded after the fact, never a launch blocker**

| gate | threshold |
|---|---|
| `G-CAP` | arm `core_min` ≤ its §6 cap, else `GATE FAIL` **on the certificate** (rule 12; the launch is not refused for it) |
| `G-CEIL` | summed `core_min` ≤ **370.0 core-min**, checked after every arm, else the chain stops |
| `G-BUDGET` | at launch, per arm: `TMO > 0`, `TMO ≥ 1.5 ×` the arm's measured-anchor wall, and the exact back-check `(TMO + 60) × ranks / 60 == cap` |
| `G-OCC` | **§7 — queues, never refuses** |
| `G-NP` | every arm `np = 1` |
| fleet ceiling | `min(3 × registered cap, remaining box budget)` per arm, monitor-enforced, graceful stop regardless of residual trend (Sanaa ~21:00Z) |

---

## 6. COST — ANCHORS THAT CITE AN ARTIFACT, CAP SIZED AT THE REGISTERED MAXIMUM OCCUPANCY

### 6.1 The two MEASURED rate points, and what each one's artifact actually says

**The compressible contention factor (3.1198×) must NOT be used here** and is named so it cannot
be reached for by mistake: importing a compressible rate into an incompressible cost basis is the
scope error of `L-454`.

| n (concurrent A1WR solver units) | rate | artifact, and the exact lines |
|---|---|---|
| **2** | **1.649566 it/s** | `/home/ubuntu/certonomous-runs/A1WR/STAGE12/probe_I/out/sweep.log` — `Time = 1500`, `ExecutionTime = 909.33 s`. `probe_I` and `probe_C` are the only units alive in that window (`CHAIN_LEDGER.tsv`, launched `18:19:35/36Z`, ended `18:34:58Z` / `18:35:58Z`) |
| **6** | **0.561358 it/s** | `/home/ubuntu/certonomous-runs/A1WR/STAGE12/cold_I_4/out/sweep.log` — `Time = 1800`, `ExecutionTime = 3206.51 s`. Six `COLD` units alive `18:35:59–19:31:16Z` per `CHAIN_LEDGER.tsv`; **that arm exited `rc=97` at its deadline, which is fine for a rate and is stated** |

**Comparability caveat, disclosed rather than smoothed:** `probe_I` ran `tol 1e-30` / `mem 4g` /
α 18, `cold_I_4` ran `tol 1.0e-8` / `mem 3g` / α 4. Tolerance sets when a solve *stops*, not what an
iteration *costs*; `oom=false` on every row, so the memory limit did not bind. **Both are L3, np=1,
incompressible, same image.** The two are comparable as rate points and the differences are named.

**`2.36 it/s at 3-way` is NOT used.** It has no artifact (§0, correction 2). Nothing in this
registration multiplies it.

| model | form | basis |
|---|---|---|
| `rate(n) = 1.649566 × (n/2)^(−0.981155)` | exponent fixed exactly by the two MEASURED points | **DERIVED** from MEASURED points; deadline sizing only, never a result |
| coarse rate | `rate(n) × 130304/4032 = rate(n) × 32.3175` | **DERIVED** by cell ratio — deliberately the *conservative* choice; D19T's direct coarse measurement is ~7.6× faster, and this registration does not import a cross-item anchor when a conservative in-family one exists |

**The exponent −0.9812 is close to −1, i.e. throughput saturation on a fixed core count — the
physically expected shape.** The draft's −1.4641 asserted super-linear degradation, which followed
from the 8-way mislabel and which nobody measured.

### 6.1a `rate(14)` IS A BAND AND THE CAP IS SIZED ON ITS PESSIMISTIC END

`n = 14` is the **registered maximum occupancy** and extrapolates past the last MEASURED point
(n = 6), so it is quoted as a band and the allowance is applied **at the input**, never by
inflating the cap:

| end | model | rate @ n=14 |
|---|---|---|
| power law | exponent fixed by the two MEASURED points | **0.244454 it/s** |
| saturating throughput | `C/n`, `C = 6 × 0.561358 = 3.368148`, anchored on the MEASURED n=6 point | **0.240582 it/s** |
| **pessimistic — THE SIZING INPUT** | power law ÷ **1.5 extrapolation allowance**, applied to the extrapolated segment only | **0.162970 it/s** |

**The two models now agree to 1.6%**, because an exponent near −1 *is* `C/n`. **The `1.5` is a
stated JUDGEMENT and is labelled one:** two measured points fix a power law exactly and leave no
fitted residual, so no uncertainty band is computable *from the data*, and inventing a statistical
one would be worse than naming a judgement.

### 6.2 THE CAP TABLE — EVALUATED AND ASSERTED, NOT ASSERTED AND HOPED

Adopted form (`S-29` §7 item 4): **`effective ≥ max(3.0 × estimate-at-a-MEASURED-anchor,
1.25 × wall-at-registered-max-occupancy)` — the MAX of two different risks, never their product.**
The MEASURED anchor used for the `3.0×` leg is the **more conservative** of the two, n = 6.
`CAP_MARGIN_S = 60`, `effective = cap − CAP_MARGIN_S × ranks / 60`,
**`TMO = int(CAP × 60 / RANKS) − 60`**, guard `TMO > 0`.

| arm | est @ n=6 (MEASURED) | est @ n=14 central | est @ n=14 pessimistic | `3.0 ×` meas | `1.25 ×` pess | required | **cap** | effective | **`TMO`** | back-check |
|---|---|---|---|---|---|---|---|---|---|---|
| `Sc` | 1.8374 | 4.2193 | 6.3290 | 5.5122 | **7.9112** | 7.9112 | **9.0** | 8.0000 | **480 s** | 9.000000 |
| `Ec` | 1.8374 | 4.2193 | 6.3290 | 5.5122 | **7.9112** | 7.9112 | **9.0** | 8.0000 | **480 s** | 9.000000 |
| `S3` | 59.3798 | 136.3581 | 204.5372 | 178.1394 | **255.6715** | 255.6715 | **257.0** | 256.0000 | **15360 s** | 257.000000 |
| `E3` | 59.3798 | 136.3581 | 204.5372 | 178.1394 | **255.6715** | 255.6715 | **257.0** | 256.0000 | **15360 s** | 257.000000 |

All figures in core-minutes at `ranks = 1`. **The contention leg binds on all four arms; the
`3.0 ×` envelope binds on none.** Every row is asserted by execution — `TMO > 0`,
`effective ≥ required`, and the exact back-check — and the assertions are in the sizing script, not
in this prose.

**The `TMO ≥ 1.5 × anchor wall` guard, which is what `D19T` died on.** `D19T`'s `MESH` arm had
`TMO = int(1.0 × 60 / 1) − 60 = 0 s`, refused at run time, and **no A1ZE arm can repeat it**:

| arm | `TMO` | measured-anchor wall (n = 6) | `1.5 ×` it | ratio | |
|---|---|---|---|---|---|
| `Sc` / `Ec` | 480 s | 110.2 s | 165.4 s | **4.35×** | ✅ |
| `S3` / `E3` | 15360 s | 3562.8 s | 5344.2 s | **4.31×** | ✅ |

| quantity | value |
|---|---|
| cap sum | **532.0 core-min** |
| predicted @ n=14, central | **281.15 core-min** — the registered figure |
| predicted @ n=6 (MEASURED rate) | 122.43 core-min |
| **ITEM CEILING** | **370.0 core-min**, checked after every arm, **1.316× the central prediction and below the cap sum by design** |
| dollars | predicted **$0.2404**, ceiling **$0.3164** — **DERIVED at the owner-stated $0.0513/core-h, NEVER measured**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

**Rule-12 calibration is OWED at completion** to `docs/COST_CALIBRATION.md`: actual/predicted ratio
against the 281.15 registered figure, with contention, waste and misprediction attributed
separately and waste never folded into the ratio.

---

## 7. `G-OCC` — THE OCCUPANCY GATE **QUEUES; IT NEVER REFUSES**

Sanaa ~21:00Z: resource gates *"queue, don't launch. But queueing is not blocking; the run stays
scheduled."* Sanaa ~22:00Z: *"box should never be idle."* **`G-OCC` never returns a refusal and
never consumes an entry.**

At launch and at every arm boundary the launcher measures occupancy `n` and `MemAvailable` (from a
reader first proved able to return a non-zero), **records both in `ledger.txt`**, and **queues** —
leaving the row scheduled — only while `TMO < 1.25 × iterations / rate(n)`.

Evaluated for the L3 arms at `TMO = 15360 s`, 2,000 iterations, **on the PESSIMISTIC rate**:

| occupancy `n` | required wall | decision |
|---|---|---|
| 2 | 1,515.5 s | **LAUNCH** |
| 6 (MEASURED) | 4,453.5 s | **LAUNCH** |
| 8 | 8,858.8 s | **LAUNCH** |
| 12 | 13,187.1 s | **LAUNCH** |
| **14 (registered maximum)** | **15,340.3 s** | **LAUNCH** |
| 15 | 16,414.7 s | **QUEUE** |
| 18 | 19,630.0 s | **QUEUE** |

**The boundary falls exactly at the registered maximum occupancy on the PESSIMISTIC end of the rate
band** — the deadline covers n = 14 even if the extrapolation is wrong by the full 1.5× allowance,
and does not pretend to cover n = 15.

**Occupancy read at freeze, for the record:** one dafoam container live
(`d12y_w3_S3b_c0_am_…`, `W3_chain_r2` phase 1, np = 1), 16 vCPU, 1-minute load average 53.72,
`MemAvailable` 26.9 GiB. **That chain is not disturbed by this item and is counted in the
occupancy leg.**

---

## 8. PLANTED-ZERO CONTROLS — EVERY FIXTURE STATIC, PINNED, AND INDEPENDENT OF THE GRADED RUN

`L-435`: **not one control reads anything produced by this item's own solves.** Fixtures live at
`controls/`, are authored at freeze, and are md5-pinned inside the frozen grader.

| control | reader under test | fixture (md5) | must return | else |
|---|---|---|---|---|
| `P1` | solution-directions reader | `P1_dirn3.log` `28ac80cdc8823775cd9f1271ab600ef3` / `P1_dirn2.log` `66d4555036ebaf661673ca03541b02a1` | **distinguish** `3 (1 1 1)` from `2 (1 1 0)` | `CONTROL_READER_NOT_BORN` |
| `P2` | per-equation `initRes` reader | `P2_eqs.log` `412754b0a7673c6e65db010d66be51d9` | `U2 = 3.0000e-04` among five channels | `CONTROL_READER_NOT_BORN` |
| `P2n` | same reader, **negative leg** | `P2n_noU2.log` `8674c4a076872924a6248e636016c7c0` | **`U2` absent**, other four still seen | `CONTROL_READER_ALWAYS_FIRES` |
| `P3` | `CL`/`CD` series reader | `P3_coef.log` `8693c7445260b7775d5ba6678cec72cd` | mean and spread to **1e-12 relative** | `CONTROL_READER_NOT_BORN` |
| `P4` | `G-STAT` spread test | `P4_stationary.log` `8d0d8023e95d4c305c81075433e5af1a` / `P4_swinging.log` `83246d34f4b2828b2f6fef645d36596f` | **PASS one, FAIL the other** | `CONTROL_GATE_STUCK` |
| `P5` | patch-type reader | `P5_symmetry` `8343e69e4695ee363dc02c5d697dc79b` / `P5_empty` `a681ef56baac150de46c2c846599fbe9` | distinguish `symmetry` from `empty` on **both** planes | `CONTROL_READER_NOT_BORN` |

**`P2n` and `P4` are two-sided because a reader that always finds `U2`, or a gate that always says
"stationary", is exactly as blind as one that never does** (`L-452` addendum: a gate never shown to
return **both** answers is not a gate). **`G-U2.E`'s entire content is an ABSENCE**, so the absence
must be demonstrable, and `P2n` is what demonstrates it.

**Asserted by EXECUTION at grade time:** every fixture's md5 == its pin; every fixture's `mtime`
**older than the run root**; no fixture inside the run root. **Any control refusal makes the whole
item `NOT A RESULT`** (grader exits 2); no reader may be substituted.

### 8.1 THE CONTROLS WERE DRIVEN BOTH WAYS AT FREEZE, ON ZERO COMPUTE

- `a1ze_grade.py --selftest` → `A1ZE_BIRTH 7 readers born, both legs proved on P2n and P4`, rc 0.
- **Planted violation:** a copy of the item tree with one byte-level mutation of `P2n_noU2.log`
  (`U1 initRes` → `U2 initRes`) → `A1ZE_CONTROLS REFUSED -- CONTROL_FIXTURE_MOVED`,
  `A1ZE_VERDICT NOT A RESULT`, **rc 2**. The enforcer fires through the real path.
- **The readers were then pointed at REAL foreign artifacts and returned non-zeros**, which is what
  makes a later zero evidence rather than silence:
  `read_dirn(sweep_I/out/sweep.log)` → `(3, (1, 1, 1))`; `read_equations` →
  `['U0','U1','U2','nuTilda','p']`; `read_eq_min(…,'U2')` → **`3.238410485530894e-08`**, matching
  `A1WR_STAGE12_RESULTS.md` §16's `3.238410e-08`; `read_coefs` → 559/559; last-10 spreads
  `3.3096549607706817e-03` / `5.734690681545189e-04`, reproducing the draft's figures exactly and
  locating them at α = 13; and `read_patch_types` on the **real** L3 mesh
  `/home/ubuntu/certonomous-runs/A1WR/L3/constant/polyMesh/boundary` → `{'symmetry1': 'symmetry',
  'symmetry2': 'symmetry'}`.

**Cost of every check in this section: 0 solver core-min.** Reader execution on foreign artifacts,
well under 0.02 core-min, disclosed rather than omitted.

---

## 9. THE REGISTERED PREDICTION — BEFORE THE ANSWER EXISTS

| gate | **PREDICTION** | what would **REFUTE** it |
|---|---|---|
| `G-DIRN.E` | **2 solution directions** on the `empty` arms | 3 → the change did not take effect; **`GATE FAIL`, `d3f47bfa` condemned** |
| `G-U2.E` | **`U2` absent entirely** — no equation, so no residual and no floor | `U2` still printed → the mechanism is not the patch type and the whole account is wrong; **`d3f47bfa` condemned** |
| `G-EMPTY` / IDWarp | the `empty` arms **build and run** | the mesh warping or the adjoint refuses `empty` → arm `BLOCKED`, **and that condemns `d3f47bfa` too** (§3b.0) |
| `R-MAXRES` *(reported)* | the `empty` arms' per-iteration **printed** max **falls** — `U2` is the largest printed channel at 12 of 14 A1WR points, so removing it must lower the printed max | it does not → `U2` was not the largest printed residual on this configuration after all |
| `R-DECL` *(reported)* | **NEITHER arm declares convergence**, because the U2-excluded per-iteration max at α = 12 floors at **2.997861e-08** against 1e-8 (§1a) | the `empty` arm declares and the `symmetry` arm does not → `U2` reaches the criterion after all, contradicting D19T `T10`; **reported as a new fact, folded into no gate** |
| `G-STAT` | **both arms stationary at 2,000 cold iterations** | see §9a — this is the item's weakest registered prediction and it is named as such |
| **`G-COEF`** | **⚠ THE REGISTERED PREDICTION IS THE BORING ONE: `CL` and `CD` UNCHANGED, `Δrel` inside the α = 12 measured drift (`CL` 4.830552e-04, `CD` 1.116421e-04). The only thing that changes is that the solve converges.** | `Δrel` above 10× drift → **CONTAMINATION**, and every incompressible coefficient in this ladder is affected |

**Why the boring outcome is the registered one.** The exciting result — *"a one-word patch-type
change invalidates the ladder's published coefficients"* — would flatter this team enormously.
**That is exactly why it is not what is predicted.** `U2`'s magnitude is pinned near zero by the
symmetry conditions themselves, so the physical expectation is that its redundant equation is
**inert** for the integrated forces even while its residual floors. **Recorded now so it cannot be
reframed as a prediction afterwards: the drafter expects no contamination.**

### 9a. ⚠ THE HONEST RISK: COLD STATIONARITY AT 2,000 ITERATIONS ON L3 IS UNMEASURED

A1WR's `sweep_I` points ran **4,000** iterations each and every one was **CONTINUED** from its
predecessor. **The only cold L3 evidence the lab holds is `cold_I_4`, which was deadline-killed at
`Time = 1800` and wrote no time directory and no coefficients at all.** So whether a *cold* L3 solve
is stationary by iteration 2,000 is genuinely unknown, and `G-STAT` is exactly the gate that will
catch it if it is not.

**Registered consequence, before the answer exists: if `G-STAT` fails on the L3 pair, this item
spends up to 512 core-min of its arms' caps and returns `NOT A RESULT` on the question it exists to
answer.** That is stated here rather than discovered afterwards, and the mechanism gates
(`G-DIRN.E`, `G-U2.E`) — which are what verify `d3f47bfa` — **do not depend on stationarity and
still resolve.** The coarse pair, which is minutes, resolves independently.

---

## 10. WHAT THIS ITEM CANNOT DO

1. **It cannot produce a grid-converged anything** (§4).
2. **It cannot detect contamination below the measured drift.** A real movement smaller than
   4.830552e-04 (`CL`, L3) is invisible to this instrument and the item says so rather than
   reporting zero. **A null here is bounded, not absolute.**
3. **It cannot settle the compressible failure.** `A1WR sweep_C` fails with `p` floored at 3.16e-01
   and a last-10 `CL` spread of 7.56e+00 — a different and more violent mechanism (`N-C9`).
   **The disconfirming arm is named in §1b so this item is never later read as explaining it.**
4. **It cannot explain ANY non-convergence, incompressible ones included.** §1a measures that
   `U2` is not in the declared quantity and that A1WR's 14 points miss 1e-8 with `U2` excluded.
   **A `GATE REACHED` here does not restore a single A1WR point and does not license re-running
   one at the same tolerance.** Whatever floors those solves is unidentified and stays open.
5. **It cannot discriminate the FORM of the declared quantity.** §1a proves `U2`'s *exclusion*,
   which is all any conclusion here needs. Whether the solver takes a median of the vector
   components or drops the z-component is **INFERRED, not measured**: the claim rests on a lane's
   read of `DAUtility.C`, and **that file is not on this box** (searched; zero hits). No arithmetic
   in this registration depends on the form, and none may be added by addendum without a source
   whose location and hash are verified.
6. **It cannot gate the coarse pair's coefficients**, whose drift anchor is a cross-grid proxy
   (§5.3). That pair is reported, not gated.
7. **It cannot re-grade any landed verdict.** Whatever it finds, existing verdicts move only by a
   ruling above this team. What it *can* do is condemn `d3f47bfa`, which is a commit, not a verdict.

---

## 11. THE CORRECTIONS REGISTER — WHAT MOVED FROM THE DRAFT, AND ON WHOSE READING

| # | what the draft said | what the artifact says | where |
|---|---|---|---|
| **1** | drift anchor `CL` 3.310e-03 / `CD` 5.735e-04, "fixed geometry, last 10 printed iterations" | reproduces exactly, **but from α = 13** — 26 prints against 41, SIGTERM-truncated, unsettled. **α = 12's own drift is 4.830552e-04 / 1.116421e-04**, so the band was 6.85× / 5.14× too wide at the operating point | §0, §5.3 |
| **2** | `0.5614 it/s` MEASURED **8-way**, cited to `CHAIN_LEDGER.tsv`; `2.36 it/s` MEASURED **3-way** cited to `S-26`/`S-27` | the ledger holds `wall_s 3317`, `rc 97` and **not** that figure; **six** units overlapped, not eight; and `2.36` **has no artifact anywhere** — the two rates that do are `1.6496` (n=2) and `0.5614` (n=6) | §0, §6.1 |
| 3 | the delta is `symmetry → empty` | since `d3f47bfa` the templates are **`empty` at HEAD** — the **control** is now the mutated arm, and treating HEAD as the treatment is what makes this a verification of the commit | §3a |
| 4 | `d3f47bfa` names *"`A1ZE`'s `MESHA`/`Ec` arms"* as its verification | **`A1ZE` has no `MESHA` arm.** `MESHA` belongs to `A1WCT`. The verifying arms are `Ec` and `E3` | §3b.1 |
| 5 | condemnation clause "says so in both places" | it stood in **one** repository place plus a commit message. The other end is written at freeze | §3b.1 |
| 6 | §11 open items 2 and 3 cited "1.05× on the 6-way clause" and caps of 60.0/76.0 | **stale against the draft's own revised §6.3** (caps 5.5/254.0). Dropped, not carried forward | this table |
| 7 | no gate checked that the arms ran equal iteration counts | **`G-TOL`** added, justified on equal-iteration comparison alone | §5.1 |
| **8** | the draft registered *"the `empty` arms' max-over-equations residual falls below the `symmetry` arms' floor"* as a **gate-relevant prediction** | **`U2` is not in the declared quantity** — D19T `T10` declared 22× at 9.04e-11 while `U2`'s best over the whole run was 1.716383e-10. **Removing a channel that was never in the criterion cannot change the criterion.** The prediction is split: `R-MAXRES` (printed max, REPORTED) and `R-DECL` (declared, REPORTED). **No convergence gate remains** | §1a, §5.1a, §9 |
| **9** | the condemnation clause did not say what it condemned *for* | narrowed to the **assembly facts** in §3b.0, with an explicit list of what a `GATE FAIL` does **not** condemn — **a gate keyed to a convergence effect that cannot occur would have falsely condemned a correct commit** | §3b.0 |
| **10** | *(nobody's claim — this lane's own extension)* | **A1WR's 14 α points miss 1e-8 EVEN WITH `U2` EXCLUDED**; best U2-excluded per-iteration max over the whole sweep is 1.340732e-08, binding `U1`/`nuTilda`, never `U2`. **Removing `U2` would not have converged a single A1WR point.** Nobody had measured this | §1a |

**Where the opening brief for this pass was wrong, and where it was right — both recorded, because
the family's record says a lane reading the artefacts over its supervisor has been right every
time, and this pass is the counter-example that keeps that rule honest.**

*Wrong:* (a) it placed the two corrections in `S-29`; they are in `S-30` §3 as a back-reference to
`d880cf7e`, and *those* two were already applied. (b) Its reading — "do not assert the `U2`
mechanism as a three-item finding, the compressible arm disconfirms it" — was **already satisfied**
by the draft's §10 and its two-sided refutation column, and it **understated the problem by an
order of magnitude**: the mechanism does not survive on the *incompressible* items either. (c) Its
reading — "check any registered tolerance against the measured `U2` floor" — was **already
satisfied by design** (the fixed-2,000-iteration stop), though only as prose; `G-TOL` makes it
executable.

*Right, and decisively:* the mid-pass correction. **The supervisor's own §2 claim was the thing
that needed falsifying, they falsified it themselves against their own block, and they sent it
before this document froze.** Had it arrived an hour later, A1ZE would have frozen a gate that
could have condemned a correct commit for failing to do something measurement says it cannot do.
**That is the single most valuable thing that happened in this pass and none of it was this lane's
doing.**

---

## 12. FILING, FREEZE AND PROHIBITIONS

| object | path | md5 |
|---|---|---|
| this registration | `cases/dafoam/ladder-a/A1/z_direction_empty_control/A1ZE_PREREGISTRATION.md` | frozen at this commit |
| **the frozen grading path** | `cases/dafoam/ladder-a/A1/z_direction_empty_control/a1ze_grade.py` | **`9b755c3b1a043879a664853a3d747c53`** |
| controls | `cases/dafoam/ladder-a/A1/z_direction_empty_control/controls/` | pinned in §8 and inside the grader |
| **parked queue row** | `cases/dafoam/ladder-a/A1/z_direction_empty_control/A1ZE_QUEUE_ROW.parked.json` | **outside `verification/queue/` — not filed** |
| the other end of the condemnation | `cases/dafoam/PATCH_IDENTITY_D3F47BFA_UNVERIFIED.md` | — |
| run root (must be ABSENT at launch) | `/home/ubuntu/certonomous-runs/A1ZE` | **checked absent at freeze** |

**Launches are daemon-only.** No agent invokes a driver, launcher or container for this item. The
queue row is filed by `dafoam-supervisor` after check 4, or not at all.

**The `createPatchDict` upstream attribution stays INFERRED** and is **NOT FILED** (rule 7).

**SUBMISSIONS PARKED. Nothing here is sent, filed, uploaded, registered, posted or commented
outside this box.**

---
---

# ADDENDUM A — 2026-09-03 — THE LAUNCH PATH, ITS PINS, AND A MEMORY FIGURE CORRECTED

**`lines whose number changed above this section: 0`**

Nothing above this line has been edited. This addendum **alters no gate, no threshold, no cap and
no label**, and it cannot: it registers the *launch* path, which the freeze did not contain, and it
corrects one figure that lives in the parked queue row rather than in any registered gate.
**Zero compute has been spent. The run root `/home/ubuntu/certonomous-runs/A1ZE` is still absent,
re-asserted by execution at this stamp.**

## A.1 WHY THIS ADDENDUM EXISTS

The freeze fixed the **grading** path (rule 2: "the grading path is fixed at the pre-registration
commit"). It did not contain a driver, and the supervisor's check-4 read found that: the parked
row's `launch_cmd` named `a1ze_chain_driver.sh`, **which did not exist**. The registration was not
the blocker; the absent driver was. The launch path lands here.

## A.2 THE LAUNCH PATH, PINNED

| instrument | role | md5 |
|---|---|---|
| `a1ze_chain_driver.sh` | ONE detached process, four arms in order, stops at the first non-zero rc | see `A1ZE_INSTRUMENT_MD5.txt` |
| `a1ze_stage.py` | stages both arms of a pair from the same sources **and carries the one-variable assert** | ditto |
| `a1ze_cmd.sh` | the in-container unit program; **captures its own rc to `out/rc.txt`** | ditto |
| `a1ze_runScript.py` | the primal. **A byte-identical copy of `a1wr_runScript_incomp.py`, md5 `d48f48c5e2e41e86981acbf6feccb3c4`** | ditto |
| `A1ZE_INSTRUMENT_MD5.txt` | the pins the driver verifies with `md5sum -c` before anything runs | — |

**The runScript is not new code.** A1ZE needs one cold point at a fixed α for a fixed iteration
count at `np = 1` — exactly A1WR's `COLD` mode with a one-element α list. **Authoring fresh solver
code that this lane cannot execute would be the larger risk**, and reusing an already-exercised
frozen instrument means the *only* thing A1ZE varies from A1WR's proven path is the patch type,
which is the item's whole point. The grader `a1ze_grade.py` is **unchanged at `9b755c3b1a043879a664853a3d747c53`**,
verified disk == the blob at the freeze commit `03120e2244d52aee5dd79f7e0ea66b4b2940f7fd`.

## A.3 THE ONE-VARIABLE ASSERT — AND ONE DELIBERATE WIDENING, DECLARED

`a1ze_stage.py` stages **both arms of a pair in one invocation from the same sources**, then
md5-walks both trees and **refuses** unless: the file *sets* are identical; the *only* files that
differ are the ones the patch legitimately touches; every differing line is a `type` or `inGroups`
line; each differing line carries **its own arm's registered type**; and no allow-listed file is
identical between the arms (which would mean the mutation silently did not take).

**⚠ THE WIDENING, DECLARED RATHER THAN DONE QUIETLY.** The supervisor's requirement said the diff
must be confined to the **`type`** lines. It is confined to `type` **and `inGroups`**. A patch
cannot be `type empty` while its `inGroups` still reads `1(symmetry)` — that is the same
"a patch cannot be `empty` in the mesh and `symmetry` in the field" constraint that forced
`d3f47bfa` to touch 41 files rather than 3, one level down. **`inGroups` is not a second variable;
it is the same variable's second line.** It appears in no registered gate, so **no gate moves.**

**Both legs proved by execution, on a scratch copy, with the real run root untouched:**

| plant | result |
|---|---|
| an untouched file (`case/system/fvSolution`) edited in one arm | **REFUSED** — `A SECOND VARIABLE: 1 file(s) differ that the patch does not touch` |
| a non-`type` line changed inside a touched file (`0.orig/U` `internalField`) | **REFUSED** — `A SECOND VARIABLE inside case/0.orig/U` |
| a file removed from one arm (`case/system/fvSchemes`) | **REFUSED** — `arm file SETS differ` |
| the mutation silently not taking on one file (`0.orig/p`) | **REFUSED** — `the patch was staged but 1 file(s) are IDENTICAL between the arms` |
| the clean staging | **ADMITTED** — a gate that only ever refuses is as useless as one that never does |

Clean coarse staging, measured: **38 files compared, exactly 10 differ** (`constant/polyMesh/boundary`
plus the nine `0.orig` fields that declare both planes), **44 differing lines, all `type`/`inGroups`.**

**The treatment type is not a literal in any instrument.** `a1ze_stage.py` parses it out of
`system/createPatchDict` **at HEAD** (md5 asserted `b06b3285…`) and the control type out of the
**ancestor blob at `d3f47bfa^`** (md5 asserted `5e897099…`), and refuses if the two agree — because
then the commit under test changed nothing and there is no experiment. **If `d3f47bfa` is wrong,
the wrong type is staged and `G-DIRN.E`/`G-U2.E` see it.** That is what makes this a test of the
commit rather than of a hand-patch.

## A.4 WHAT STOPS THE RUN, AND WHAT DELIBERATELY DOES NOT

**Stops it:** (1) the per-arm `TMO` **inside** the container, surviving the death of the driver,
the daemon and every agent; (2) the **370.0 core-min item ceiling, checked before every arm** —
below the 532.0 cap sum by design, so the ceiling binds first. `G-BUDGET` re-derives
`TMO = int(CAP×60/RANKS) − 60` from the registered cap at run time and refuses on a mismatch, on
`TMO ≤ 0`, or on a failed exact back-check, rather than trusting the table.

**Does NOT stop it: occupancy and memory.** `occ_wait()` records containers, `MemAvailable` and
load average to `ledger.txt` and **waits**; it has no refusal branch and cannot consume the entry
(Sanaa ~21:00Z, ~22:00Z). `d19t_run_arm.sh`'s `G-QUIET` refuse-to-launch form is **not reproduced**.

`docker inspect` is read for `ExitCode` and `OOMKilled` **before** `docker rm`. The in-container
`out/rc.txt` is **physics-critical**; the docker exit code and the ledger rows are infrastructure —
except that a *missing* `rc.txt` is not bookkeeping, because it means the unit program never
reached its own end.

## A.5 ⚠ THE MEMORY FIGURE WAS A GUESS, AND IT IS CORRECTED — `3.0` → `4.0` GiB

**The parked row's `memory_floor_gb = 3.0` had no measurement behind it, and the supervisor was
right to refuse it.** **Peak RSS for this case family is UNMEASURED and cannot be measured without
running something, which this lane will not do.**

What *is* measured, from `/home/ubuntu/certonomous-runs/A1WR/STAGE12/CHAIN_LEDGER.tsv` on the
**identical 130,304-cell L3 mesh**: six `COLD` units at `--memory=3g`, **`OOMKilled=false` on every
row**, reaching iteration 1800; and two probes at `--memory=4g`, **also `OOMKilled=false`**.
**A non-OOM observation is an upper bound not reached, not a peak** — and those arms stopped at
1800 of a 4,000 endTime, so nothing on disk covers a full run.

**Sized conservatively at 4 GiB** — the value already demonstrated non-OOM on this mesh, and 1.33×
the value demonstrated non-OOM through iteration 1800. **It is labelled a size, not a
measurement.** It gates nothing: memory is a resource condition and `G-OCC` **queues** on it.

## A.6 STATE AT THIS STAMP

Run root **absent**, re-asserted by execution. **Nothing launched, nothing queued, zero solver
core-min.** The queue row remains parked at `A1ZE_QUEUE_ROW.parked.json`, outside
`verification/queue/`, and enters the queue only on `dafoam-supervisor`'s personal check-4 of the
driver as a diff. The live `W3_chain_r2` container was not touched.

**SUBMISSIONS PARKED.**

---
---

# ADDENDUM B — 2026-09-03 — **v1.2** — THE MEDIAN FORM IS MEASURED, IN BOTH TOOLCHAIN ROWS, AND UPSTREAM'S OWN COMMENT SAYS WHY IT EXISTS

**`lines whose number changed above this section: 0`** — asserted mechanically, not by eye: the
disk file's first **731** lines are byte-identical to the blob at
`03120e2244d52aee5dd79f7e0ea66b4b2940f7fd` under `cmp`, and `a1ze_chain_driver.sh`'s `G-FREEZE`
re-executes exactly that comparison before any arm runs. **Addendum A's 114 lines are likewise
untouched.**

**LAWFUL BECAUSE ZERO COMPUTE HAS BEEN SPENT, AND THE CONDITION IS CHECKED BY EXECUTION IN THE
AMENDING INVOCATION:** `/home/ubuntu/certonomous-runs/A1ZE` **does not exist** (`ls` returned
*"No such file or directory"* at this stamp), no `Sc/Ec/S3/E3` unit directory exists anywhere, and
no queue row has been filed. **NO GATE, THRESHOLD, CAP OR LABEL CHANGES HERE, AND NONE MAY.**

## B.1 §10 ITEM 5 IS UPGRADED FROM **INFERRED** TO **MEASURED**

Line 667 of the frozen text reads that the median form rests on a lane's read of `DAUtility.C` and
that *"that file is not on this box (searched; zero hits)"*. **That sentence is false, and it is
false in a specific way: it was true of the HOST filesystem and is stated as though it were true of
the toolchain.** The file is in the image, and under `DAFOAM_CHARTER.md` **§6** the image *is* the
toolchain identity. The frozen bytes are not edited; this is their correction of record.

> **⚠ THE CHARTER CITATION IS ALSO CORRECTED.** The clause was cited to §11. **§11 is the lesson and
> numerics NUMBERING clause.** Toolchain identity is **§6** — *"Shipped and patched are always two
> rows, and toolchain identity is an image ID and a library hash, never a version string."* The
> right clause matters here, because §6 is precisely what the next section had to satisfy.

## B.2 ⚠⚠ THE MEASUREMENT WAS SCOPED TO THE WRONG IMAGE, AND §6 IS THE CLAUSE THAT CATCHES IT

The finding was measured in **`dafoam/opt-packages:latest`**, `sha256:9d45679d55fd…`, on the grounds
that it matches the live `W3_chain_r2` row. **It does — and `W3_chain_r2` is not this item.**

**A1ZE's registered image is `dafoam-idwarp-rot:v1`, `sha256:2927768a16ac…`** — the PATCHED build,
named in `a1ze_chain_driver.sh` and asserted by its `G-IMG` before any arm runs. **They are two
different images, both present on this box.** Under §6 they are **two rows**, and a library hash
measured in one is not a fact about the other. *This is the same "true in one scope, stated as
another" pattern the correction itself was written to name, one level down.*

**BOTH ROWS MEASURED, read-only, at this stamp** — `docker run --rm --network=none` with no volume
and no mount, `md5sum` and `sed` only. **No run root, no solver, no arithmetic tested, nothing
graded.** That is toolchain identification under §6, not the prohibited invocation of a driver or
container to test its own arithmetic.

| toolchain row | image | id | `DAUtility.C` md5 |
|---|---|---|---|
| **shipped** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd…` | `d5fb5b0a781b11a780133901a8c2241c` |
| **patched — A1ZE's registered image** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16ac…` | **`d5fb5b0a781b11a780133901a8c2241c`** |

**The two are byte-identical, so the finding does transfer — and it is now MEASURED to transfer
rather than assumed to.** Path in both:
`/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DAUtility/DAUtility.C`.

**`SolverPerformance<vector>` overload, read from the image:** `vector initRes = solverP.initialResidual();`
**:782**; `scalarList initResList = {initRes[0], initRes[1], initRes[2]};` **:783**; `sort(initResList);`
**:784**; `if (initResList[1] > primalMaxRes)` **:786**; `primalMaxRes = initResList[1];` **:788**.
**`sort`, then index 1 of three — the median, with a hash.** The `<scalar>` overload for contrast:
`scalar initRes = solverP.initialResidual();` **:747**; `if (initRes > primalMaxRes)` **:749** — a
true max.

## B.3 ⚠ UPSTREAM'S OWN COMMENT NAMES THIS EXACT CONFIGURATION — AND IT CUTS AGAINST `d3f47bfa`, NOT FOR IT

`DAUtility.C:775-780`, verbatim from the image:

> *"for vectors, we need to use the median value for the residual / this is because we often need to
> run 2D simulations with symmetry BC, so one component of the residual vector, which is related to
> the symmetry BC, may be high while the other two components' residuals are low. In this case, we
> can use the median value for the residual vector, which better represents the convergence."*

**Upstream anticipated a one-cell-thick 2-D mesh with `symmetry` bounding planes, expected exactly
the high z-component this lab measured, and built the median to tolerate it.** §1's *"the provenance
is INFERRED"* is therefore strengthened into something sharper: **`symmetry` on these planes is
documented upstream design intent, not an oversight inherited by accident.**

> **REGISTERED BEFORE COMPUTE, BECAUSE IT MOVES THE ODDS AGAINST THE COMMIT UNDER TEST AND MUST BE
> SAID BEFORE THE ANSWER EXISTS: this raises, not lowers, the prior that `empty` is not what this
> toolchain expects on this case family.** It is direct evidence that upstream *chose* `symmetry`
> deliberately for 2-D. **`G-EMPTY` `BLOCKED` on a treatment arm — IDWarp or the adjoint refusing
> `empty` — is the outcome this comment makes more likely, and §3b.0 already registers that as
> condemning `d3f47bfa`.** It remains INFERRED that the adjoint or the warping *requires* `symmetry`;
> what is now measured is that the residual criterion was written around it.

## B.4 THE MEDIAN FORM REPRODUCES D19T'S DECLARED NUMBERS — SO IT IS CONFIRMED FROM BEHAVIOUR TOO, NOT ONLY FROM SOURCE

Computed at this stamp from D19T's own logs, evaluating `max(median(U0,U1,U2), p, nuTilda)` per
iteration and minimising over iterations:

| arm | tol | declarations | best declared | **median form** | agrees? |
|---|---|---|---|---|---|
| `T08` | 1e-8 | 22 | 9.087147e-09 | **9.089292e-09** | ✅ 4 s.f., and it declares |
| `T10` | 1e-10 | 22 | 9.038369e-11 | **9.034983e-11** | ✅ 4 s.f., and it declares |
| `T12` | 1e-12 | **0** | — | **1.743972e-12** | ✅ above tol, so it does **not** declare |

**Three arms, three reproductions, including the one that produced no declaration at all.** A source
read says what the code contains; this says the code's behaviour is what we observe.

**AND IT SHARPENS §1a's WORDING WITHOUT MOVING ITS CONCLUSION.** §1a says *"`U2` is not in the
declared quantity."* Mechanically, `U2` **is** one of the three values fed to the median — it is
**discarded whenever it is an extreme**, which on these meshes it is (largest at 12 of 14 A1WR
points). **The conclusion is unchanged and the proof in §1a is unaffected**: a maximum over a set
can never fall below the minimum ever attained by a member, and `T10` declared 22× at ~9.04e-11
while `U2`'s best was 1.716383e-10. **`U2` does not set the declared value. That is what §1a
establishes and all it needs.**

## B.5 `R-DECL`'s REGISTERED EXPECTATION SURVIVES — AND IT IS NOW COMPUTED, NOT ASSERTED

With the median measured, an `empty` plane makes the z-component vanish, so the vector's list is
`[0, U0, U1]` and the median is `min(U0, U1)`. **The U-channel therefore moves from `max(U0,U1)` to
`min(U0,U1)` — a real change, and one that makes convergence EASIER, so it had to be checked rather
than waved through.** Evaluated on every α segment of A1WR `sweep_I`, both forms, against 1e-8:

| α | symmetry — `max(median(U0,U1,U2), p, nuTilda)` | empty — `max(min(U0,U1), p, nuTilda)` | empty declares? |
|---|---|---|---|
| 1 | 3.586409e-08 | **1.018184e-08** — lowest in the sweep | **no** |
| 4 | 1.984672e-08 | 1.247299e-08 | **no** |
| 10 | 1.340732e-08 | 1.340732e-08 | **no** |
| **12 — this item's operating point** | **2.997861e-08** | **2.795397e-08** | **no** |
| 13 | 4.145549e-07 | 4.145549e-07 | **no** |

**No segment reaches 1e-8 under either form. The closest the `empty` form ever gets is
1.018184e-08 at α = 1 — within 2 % of the tolerance and still above it.** At α = 12 the improvement
is **2.997861e-08 → 2.795397e-08, a factor of 1.07**. **`R-DECL`'s registered expectation — that
NEITHER arm declares — stands, unmoved, and is now backed by a computed margin instead of an
assertion.** `R-MAXRES` is likewise unaffected: it reads the max over *printed* channels, which is
a different quantity from the declared one and always was.

**Note the segments where the two columns are IDENTICAL (α = 6–10): at the minimising iteration the
U-channel was not binding at all — `p` or `nuTilda` was.** So the patch swap cannot move the
declared value there by construction. **That is a sharper account than either the board block or
the correction that prompted this addendum, and it is the reason `R-DECL` is REPORTED and gates
nothing.**

## B.6 WHAT DID NOT CHANGE

No gate, no threshold, no cap, no label, no arm, no anchor, no cost figure, no verdict class and no
verdict ceiling. `a1ze_grade.py` is **unchanged at `9b755c3b1a043879a664853a3d747c53`**. No
arithmetic anywhere in this registration depends on the median form; B.5 shows what the form implies
and changes nothing on the strength of it.

**Zero solver core-min. Read-only image identification only, well under 0.02 core-min, disclosed
rather than omitted. SUBMISSIONS PARKED.**

---
---

# ADDENDUM C — 2026-09-03 — **v1.3** — THE ITEM CEILING DID NOT BIND, AND FOUR GUARDS COULD NOT TELL "CHECKED AND CLEAN" FROM "NEVER RAN"

**`lines whose number changed above this section: 0`** — asserted mechanically: the disk file's
first **731** lines are byte-identical under `cmp` to the blob at `03120e22`, its first **845** to
`2a31f940`, and its first **988** to `cd7d383a`, so Addenda A and B are untouched.

**LAWFUL PRE-COMPUTE, CONDITION CHECKED BY EXECUTION IN THIS INVOCATION:**
`/home/ubuntu/certonomous-runs/A1ZE` **does not exist**, no `Sc/Ec/S3/E3` unit directory exists,
no queue row is filed. **This addendum changes ONE registered figure — the item ceiling — and says
so in its title rather than burying it. No gate, threshold, cap or label otherwise moves.**

## C.1 ⚠⚠ THE ITEM CEILING OF 370.0 WAS NOT A CEILING

`§6.2` registered *"ITEM CEILING 370.0 core-min, checked after every arm, 1.316× the central
prediction and below the cap sum by design"*, and `§5.5` said the same. **As implemented it could
never bind.** `G-CEIL` tests cumulative spend **before** an arm and never `spend + cap`. The walk,
computed:

| before | cumulative cap bound | `SPEND >= 370.0` ? |
|---|---|---|
| `Sc` | 0.0 | LAUNCH |
| `Ec` | 9.0 | LAUNCH |
| `S3` | 18.0 | LAUNCH |
| **`E3`** | **275.0** | **LAUNCH** |

**Worst case 532.0 core-min — 1.44× the figure the registration called a ceiling.** The real bound
was always the cap sum. **"Below the cap sum by design" was exactly backwards: a ceiling below the
cap sum is not a ceiling, it is a number that reads like one.**

**NOT repaired by making `G-CEIL` predictive at 370.0.** That would stop the chain before `E3` —
**the item's principal treatment arm, and one of the two arms that verify `d3f47bfa`** — making it
unreachable by construction. *That is the same defect one level up: a threshold a run cannot reach,
which is what A1WR's 1e-8 against its own 3.238410e-08 floor already cost this ladder.*

> **REGISTERED CHANGE: `ITEM_CEILING = 532.0 core-min`**, equal to the cap sum, in the driver and in
> the frozen grader (`a1ze_grade.py`). **The honest worst case is 532.0 core-min = $0.4549 DERIVED**
> at the owner-stated $0.0513/core-h, never measured. The central prediction is unchanged at
> **281.15 core-min ($0.2404 DERIVED)**, and every per-arm cap is unchanged at 9.0/9.0/257.0/257.0.
> **The previous $0.3164 ceiling figure was wrong and is superseded here.**

The structural stop is now genuinely two-layer and both layers bind: the per-arm `TMO` **inside**
the container, and a ceiling that is actually reachable by the arithmetic that produces it.

## C.2 THE UNIFYING TEST, APPLIED TO EVERY GUARD — **can the code path distinguish "the check ran and found nothing" from "the check did not run"? If it cannot, its zero must refuse.**

| # | guard | the vacuous pass | measured | repair |
|---|---|---|---|---|
| 2 | `occ_wait`'s container census | a failed `docker ps` prints nothing, `wc -l` says **0**, written to the ledger as `containers=0` — **indistinguishable from an idle box** | live read → `1`; empty query → `0`; **failed call → `0`** | rc captured; a failed read records **`containers=UNMEASURED`**, never `0` |
| 3 | `G-EMPTY`'s field limb | if `0.orig` held no field declaring the planes the loop body never ran, `NBAD` stayed 0, **success having examined nothing** | reproduced on a `0.orig` with one non-matching file | counts `fields_checked`; **zero REFUSES**; the count is printed |
| 4 | `md5sum -c` on the pin file | a short pin file passes having checked a subset | **⚠ the stated premise does not hold for an EMPTY file on this box** — coreutils 9.4 returns **rc 1**. The real hazard is **TRUNCATION: a 1-of-6-line pin file returns rc 0** | pin-file entry count asserted `== 6` **before** `md5sum -c` runs |
| — | grader selftest | `rc 0` with **no** control lines would have satisfied the check | — | control count asserted `>= 7` |
| **NEW** | **the arm-selection loop** | **a pair name matching no arm completes SILENTLY as success — the item ends having run nothing.** Found by applying the test to the guards the check-1 read did not name | `pair='TYPO'` → 0 arms matched, loop returns success | `NPAIR == 2` per pair and `NRUN == 4` overall, both refuse |

**And `G-GUARDS` in the frozen grader — plant the RUN, not only the value.** A control proving a
reader can *see* a non-zero does not prove the reader *executed*. `a1ze_cmd.sh` now emits an
execution marker only after each guard has run and counted what it examined —
`A1ZE_G_EMPTY_OK … fields_checked=N`, `A1ZE_TIMEDIR_SCAN`, `A1ZE_TOL_VAR_OK`, `A1ZE_COLD_START` —
and the grader makes an arm **`NOT A RESULT`** if any marker is missing or if `fields_checked` is
zero. Driven four ways: clean → all 4 markers; one marker removed → `NOT A RESULT`;
`fields_checked=0` → `NOT A RESULT`; empty log → `NOT A RESULT`.

## C.3 ⚠ THE `A1WR_PRIMAL_TOL` NAME IS LOAD-BEARING AND WAS MIS-DOCUMENTED — FAIL-OPEN AND SILENT

`a1ze_cmd.sh`'s header said `A1ZE_PRIMAL_TOL`; the code correctly sets **`A1WR_PRIMAL_TOL`**, which
is the name `a1ze_runScript.py:60` reads (`os.environ.get("A1WR_PRIMAL_TOL", "1.0e-8")`) — the A1WR
prefix survives because the runScript is a byte-identical copy. **A successor trusting the header
would export the wrong name, it would be silently ignored, the `1.0e-8` DEFAULT would apply, and the
two arms could then stop at DIFFERENT iteration counts — reintroducing the exact third variable
TRAP 2 exists to exclude, with no error printed anywhere.** The header is corrected *and* the name is
now **asserted on the staged bytes at the point of use** (`A1ZE_TOL_VAR_OK`), because a comment is
not a check.

## C.4 WHAT DID NOT CHANGE

Every gate and its threshold; every per-arm cap and `TMO`; the drift anchors; the arms; the verdict
class and ceiling; the central cost prediction. Changed: the **item ceiling only** (370.0 → 532.0,
with its dollars), plus non-registered guard hardening and one corrected comment.
**`a1ze_grade.py`'s md5 changes with the ceiling and the new `G-GUARDS`:
`9b755c3b1a043879a664853a3d747c53` -> `505b883efb1fedadad88e47dd6d07249`.**
`§12`'s pin sits in the frozen portion and **is not edited** (rule 6); **this addendum supersedes
it**, and `A1ZE_INSTRUMENT_MD5.txt` — which `a1ze_chain_driver.sh` verifies with `md5sum -c` after
asserting the file holds exactly 6 entries — carries the operative value. The grader's `--selftest`
still returns **7 readers born, both legs proved on `P2n` and `P4`, rc 0**.

**OPERATIVE PINS AT v1.3, superseding `§12`'s table for the two files that moved:**

| instrument | md5 |
|---|---|
| `a1ze_grade.py` — the frozen grading path | **`505b883efb1fedadad88e47dd6d07249`** |
| `a1ze_chain_driver.sh` | `610d951088e9039b261c3b9b13f1aae6` |
| `a1ze_cmd.sh` | `b0e2c8eaf8c16aefb373bb3211a483cd` |
| `a1ze_stage.py` | `8e62ad7b3557e55bd7316b0d66ba92b9` (unchanged) |
| `a1ze_runScript.py` | `d48f48c5e2e41e86981acbf6feccb3c4` (unchanged) |

**Zero solver core-min. SUBMISSIONS PARKED.**

---
---

# ADDENDUM D — 2026-09-03 — **v1.4** — TWO OPERATIONAL FAULTS OF MINE, ONE OF THEM A COMMIT WHOSE MESSAGE WAS FALSE AGAINST ITS OWN DIFF

**`lines whose number changed above this section: 0`** — the disk file's first **731** lines are
byte-identical under `cmp` to the blob at `03120e22`, its first **845** to `2a31f940`, its first
**988** to `cd7d383a`. Addenda A, B and C are untouched. **No gate, threshold, cap or label
changes here.** Run root `/home/ubuntu/certonomous-runs/A1ZE` re-asserted **absent** by execution.

## D.1 ⚠⚠ COMMIT `4fdfaae2b23e98c1c390a903672ecb2cddadab40` IS A PURE DELETION WHOSE MESSAGE CLAIMS FIVE FIXES LANDED. THAT IS A FALSE RECORD AND IT IS MINE.

Its diff is **one file, 136 deletions** — the parked queue row — and nothing else.
`a1ze_grade.py`, `a1ze_cmd.sh`, `a1ze_chain_driver.sh`, `A1ZE_PREREGISTRATION.md` and
`A1ZE_INSTRUMENT_MD5.txt` were **on disk only**. The message describes work that did not enter the
tree.

**MECHANISM, so it is not repeated:** `git update-index --add -- <many paths>` is **all-or-nothing**.
One path in the list — `verification/queue/dafoam/A1ZE_chain.json` — had **vanished between the
`cp` that created it and the `update-index` that tried to add it**, because the queue daemon picked
it up and moved it to `refused/` in that window. `update-index` aborted on that path and **added
none of the other six**. The separate `--force-remove` then succeeded, so the tree carried only the
deletion.

**THE ASSERT FIRED CORRECTLY AND I MISREAD IT.** `git diff-tree --stat` printed exactly one line, a
136-line deletion. I read it as "the parked row was removed, as intended" and did not notice that
**six additions I expected were absent**. *The rule-10 assert says "only your paths"; it does not
say "all of your paths", and a diff that is a strict subset of what you meant passes it.* Recorded
here as the operational lesson: **check the assert for what is MISSING, not only for what is
foreign** — and never stage a path a live daemon owns in the same `update-index` as your own files.

Nothing was lost: the working tree was intact throughout and every instrument is committed by the
commit that carries this addendum. **`4fdfaae2` is not rewritten** — history is not edited; this is
its correction of record.

## D.2 THE DAEMON REFUSED THE ROW, THE REFUSAL WAS CORRECT, AND IT IS RECORDED RATHER THAN ERASED

`2026-09-03T18:54:54Z`, `verification/queue/dafoam/refused/A1ZE_chain.REFUSED.txt`:

> `SCHEMA: 'cost_basis' must contain the phrase 'not measured' -- this box cannot read its own
> billing (COMPUTE_BUDGET_CHARTER.md section 5)`

The row said **"NEVER measured"** — the same claim in different words, and
`scripts/queue_entry_check.py:274` tests for the literal phrase. **The validator was right to
refuse: a rule that accepts synonyms cannot be checked mechanically, and this one exists precisely
because the box cannot read its own billing.** Corrected to *"reported-by-owner and not measured"*.

**And the refusal caught a second, real defect in the same string:** `cost_basis` still carried the
**stale `$0.3164` ceiling figure**, which was tied to the 370.0 ceiling that Addendum C had just
shown does not bind. **Corrected to `$0.4549` at the 532.0 core-min ceiling.** Addendum C had
updated the ceiling in the driver, the grader and the registration and **missed this one copy of
the derived dollars** — a figure that travelled into a second document and was not carried with its
scope, which is this family's most-repeated error and is named as such.

## D.3 THE ROW NOW HAS A CANONICAL TRACKED HOME

The queue directory is owned by a live daemon that may move a file within seconds of its creation,
so a row that exists **only** there cannot be committed reliably. The canonical copy is
**`A1ZE_QUEUE_ROW.json` in this item's directory**, tracked and committed; filing is a **copy** into
`verification/queue/dafoam/`, done as the last action, and the daemon may move it to `launched/` or
`refused/` immediately — which is normal and is reported wherever it lands.

**Zero solver core-min. SUBMISSIONS PARKED.**

---
---

# ADDENDUM E — 2026-09-03 — **v1.5** — THE FIRST FIRE DIED IN 42 SECONDS ON A SETUP DEFECT OF MINE, AND IT COST 0.7 CORE-MIN BECAUSE THE COARSE PAIR RUNS FIRST

**`lines whose number changed above this section: 0`** — the disk file's first **731** lines are
byte-identical under `cmp` to `03120e22`, **845** to `2a31f940`, **988** to `cd7d383a`. Addenda A–D
untouched. **No gate, threshold, cap or label changes.** Run root re-asserted **absent** by
execution after the archive below.

## E.1 WHAT HAPPENED, AND WHAT IT COST

The daemon accepted the row at **18:58:59Z** and launched. Every guard fired and left its marker:
`G-FREEZE` (731 lines vs the blob), `G-CONTROLS` (7 born), `G-IMG`, `A1ZE_ONE_VARIABLE_PASS`
(38 files compared, 10 differing, 44 lines), `G-BUDGET`, `G-OCC` (`containers=1`),
`A1ZE_G_EMPTY_OK … fields_checked=9 of 9`, `A1ZE_TIMEDIR_SCAN`, `A1ZE_TOL_VAR_OK`. **Then the
solver died 42 s in:**

> `--> FOAM FATAL ERROR: cannot find file "/mnt/case/constant/transportProperties"`

**Chain stopped at arm `Sc`, `rc=73`, `spend 0.7 core-min` of a 532.0 ceiling.** The frozen grader
ran on the partial root and returned **`A1ZE_VERDICT NOT A RESULT`** — it manufactured nothing.

**THE COARSE-PAIR-FIRST ORDERING IS WHY THIS COST 0.7 CORE-MIN AND NOT 512.** That ordering was
registered in Addendum A for exactly this reason, and it is the first thing in this item that has
now been paid for rather than argued for.

## E.2 THE DEFECT IS MINE AND IT IS A SETUP MISMATCH, NOT A PHYSICS FINDING

`a1ze_runScript.py` is **`DASimpleFoam` — INCOMPRESSIBLE** — and reads
`constant/transportProperties`. I staged the coarse pair from **D19T's `MESH/`, which is the
COMPRESSIBLE/THERMAL case**: `constant/thermophysicalProperties`, `0.orig/T`, `0.orig/alphat`, no
`transportProperties`. **A1WR's driver already distinguishes `SKEL_I` from `SKEL_C` and picks
`simpleFoam` or `rhoSimpleFoam` accordingly; I collapsed that distinction when I reused D19T's
directory as both mesh source and skeleton.** Cause class **SETUP**, never `PHYSICS-FAIL`.

**Repair, and it is a one-entry change because `PAIRS` already separates mesh from skeleton:** the
coarse **mesh** stays D19T's built 4,032-cell `polyMesh`; the coarse **skeleton** becomes the
**incompressible AOAI case**, the same skeleton the L3 pair already uses. **The two meshes carry
identical patch names — `symmetry1 symmetry2 wing inout` — verified by execution**, so the
incompressible fields stage onto the coarse mesh unchanged. Measured after the repair: coarse
**37 files compared, 8 differing** (7 incompressible fields + `boundary`), 36 differing lines;
L3 **38 compared, 8 differing**. The touched count drops from 10 to 8 because `T` and `alphat` are
gone — **the pair is now the incompressible configuration throughout, which is better one-variable
hygiene, not worse.** §3's registered α = 4 and 4,032 cells are unchanged, and the two pairs are
still never compared to each other.

## E.3 THREE GUARDS ADDED, EACH BECAUSE THE RUN SHOWED THEY WERE MISSING

**`G-SOLVERMATCH`, at staging, where it is free.** The skeleton must carry
`constant/transportProperties` **and must not** carry `constant/thermophysicalProperties`. Driven
both ways: the compressible skeleton **REFUSES at staging** instead of dying 40 s into a container;
the incompressible one stages clean. *A defect that costs 0.7 core-min to discover in a container
costs nothing to discover in a file listing.*

**The staging clean, then the assert.** The AOAI skeleton is a real run root and ships its own
leftover **`1000/`** time directory; the age-guard precondition correctly refused it. Skeleton time
directories are **run output, not case definition**, so they are now removed and the assert is
re-run on the survivors — **clean, then prove** — with an explicit check that **`0.orig` survived**,
because it starts with a digit and deleting it is the bug A1WR's Addendum D records.

**⚠ AND THE RUN FOUND THE SAME VACUOUS-PASS DISEASE INSIDE THE FROZEN GRADER, WHICH ADDENDUM C's
SWEEP HAD MISSED.** The partial grade printed:

> `G-EMPTY Ec: both planes 'empty' in the mesh and in 0 field file(s)`

**`Ec` never ran, so `case/0` did not exist, the loop examined nothing, and the guard reported the
planes fine.** It changed no verdict — `COMPLETION` caught the arm — but it is exactly the class
Addendum C swept `a1ze_cmd.sh` for and **I did not turn the same test on the grader.** Now
`nfield <= 0` makes the arm **`BLOCKED`**. **Proved by replaying the SAME partial root through the
hardened grader**: `G-EMPTY Ec: BLOCKED -- the mesh reads 'empty' but ZERO field files were
examined; the check did not run`. *A sweep that stops at the file you were asked about is not a
sweep, and this one had to be paid for by a run.*

## E.4 SPEND, AND THE ARCHIVE

**0.7 core-min spent, $0.0006 DERIVED** at the owner-stated $0.0513/core-h, never measured. **It
bought no physics and is named as waste, not folded into any ratio** (rule 12 §6). The rule-12
calibration row is **not yet owed** — it keys to process completion and this item has not completed.
**The 0.7 is carried forward as spend-to-date on A1ZE and will be disclosed in that row.**

The run root was **archived by `mv`, never `rm`** —
`/home/ubuntu/certonomous-runs/A1ZE_partial_20260903T190245Z`, **114 entries preserved, count
verified both sides** — and `/home/ubuntu/certonomous-runs/A1ZE` re-asserted **absent by
execution**, which is what `G-ROOT` requires before the next fire.

**SUBMISSIONS PARKED.**

---
---

# ADDENDUM F — 2026-09-03 — **v1.6** — **THE ANSWER: DAFoam HARD-ABORTS ON A 2-DIRECTION MESH BY EXPLICIT DESIGN. `empty` BOUNDING PLANES CANNOT BE USED ON THIS CASE FAMILY, AND `d3f47bfa` IS WRONG.**

**`lines whose number changed above this section: 0`** — first **731** lines byte-identical to
`03120e22`, **845** to `2a31f940`, **988** to `cd7d383a`. Addenda A–E untouched. **No gate,
threshold, cap or label changes; this addendum records a measurement and a registration gap.**

## F.1 WHAT THE RUN MEASURED

| arm | planes | result |
|---|---|---|
| **`Sc`** control | `symmetry` | **`rc=0`, every completion clause holds.** `Mesh has 3 solution (non-empty) directions (1 1 1)`. `U2` **present**, floor **6.656746e-08**. 206 s, **3.4333 core-min** of a 9.0 cap |
| **`Ec`** treatment | `empty` | **`Mesh has 2 solution (non-empty) directions (1 1 0)`** — *the change took effect perfectly* — then **`FOAM FATAL ERROR`, core dumped**, `rc=97`, 88 s, 1.4667 core-min |

`G-DIRN.S` and `G-U2.S` both reproduce the premise on the control. **`G-DIRN.E`'s registered
threshold of `N = 2` is MET.** Chain stopped at `Ec`, `rc=73`; `S3`/`E3` never ran.
**Frozen grader: `A1ZE_VERDICT NOT A RESULT`.** It manufactured nothing.

## F.2 THE CAUSE, MEASURED FROM A1ZE's OWN REGISTERED IMAGE, WITH A HASH

`Ec`'s log names its own killer:

> `--> FOAM FATAL ERROR: Mesh geometric directions is less than 3 and not supported!`
> `From Foam::checkGeometry(...) in file DACheckMesh/DACheckGeometry.C at line 278.`

Read read-only from `dafoam-idwarp-rot:v1` (`sha256:2927768a16ac…`), the image this item registers
and `G-IMG` asserts —
`/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DACheckMesh/DACheckGeometry.C`,
md5 **`e6b9497656105a2cf6958e5a6d329823`**, lines 276–281:

```
if (mesh.nGeometricD() < 3)
{
    FatalErrorInFunction
        << "Mesh geometric directions is less than 3 and not supported!"
        << abort(FatalError);
}
```

**This is DAFoam's own code, in `libDASolver.so`, not OpenFOAM's. DAFoam REFUSES any mesh with
fewer than three geometric directions, by explicit design.** `empty` bounding planes give
`nGeometricD() == 2`. **Therefore DAFoam cannot run this case family with `empty` planes, and
`d3f47bfa` is wrong on the merits.**

**And note where the abort sits.** The `Mesh has N solution (non-empty) directions` line that
`G-DIRN.E` reads is printed by **the same function, four lines above the abort**. *`G-DIRN.E`'s
threshold was met on the last line DAFoam printed before refusing to continue.*

## F.3 ⚠ THIS CLOSES ADDENDUM B's LOOP — UPSTREAM'S COMMENT WAS NOT A PREFERENCE, IT WAS A CONSEQUENCE

Addendum B recorded `DAUtility.C:775-780`: the median exists *"because we often need to run 2D
simulations with symmetry BC"*, and registered — **before this run** — that this **raises the prior
that `empty` is not what this toolchain expects**. It does more than that. **DAFoam requires ≥ 3
geometric directions, so `symmetry` is not upstream's stylistic choice for 2-D — it is the ONLY
option DAFoam permits**, and the median exists to cope with the residual component that choice
forces. **The prediction registered in B.3 is confirmed by F.2, and it was registered before the
answer existed.**

## F.4 ⚠ THE REGISTRATION'S CONDEMNATION TRIGGER WAS POINTED AT THE WRONG FAILURE, AND I SAY SO RATHER THAN CLAIMING THE GATE FIRED

`§3b` registers: *a `GATE FAIL` on `G-DIRN.E` or `G-U2.E` condemns `d3f47bfa`.* **Neither fired, and
neither could have.** `G-DIRN.E` anticipated **"the change did not take effect"** (`N` still 3).
What actually happened is the opposite and worse: **the change took effect perfectly — `N = 2` — and
the toolchain then refused the result.** `G-U2.E` was never evaluated, because the arm did not
complete.

`§3b.0` did register `G-EMPTY` `BLOCKED` — *"the mesh could not be built, or IDWarp / the adjoint
refused `empty`"* — as condemning. **That is substantively what happened**, but `G-EMPTY` reads the
staged *files*, which were perfectly correct, so it passed; the refusal arrived through the strict
completion rule as `NOT A RESULT`. **The right gate existed and was pointed at the wrong artifact.**

**So the frozen grader's `NOT A RESULT` stands and is correct, and no registered gate condemns
`d3f47bfa` by its own letter.** The commit is condemned by **measurement** — `DACheckGeometry.C:276`
— not by a gate. **That distinction is preserved rather than smoothed over: a gate that did not fire
is not a gate that fired, and the evidence is strong enough not to need the pretence.**

**Recommended, and NOT taken by this lane:** `d3f47bfa` is reverted forward on the physics, under
Sanaa's 2026-09-03 ~20:00Z blocking-physics-fix rule ("wrong patch identity on a mesh"), which now
runs in the opposite direction from the one that motivated it. **That is `dafoam-supervisor`'s
ruling to take, not a lane's.** Until it is taken, `cases/dafoam/PATCH_IDENTITY_D3F47BFA_UNVERIFIED.md`
and the three template `README_PATCH_IDENTITY.md` notes remain accurate and are what a reader finds.

## F.5 COST, AND THE ORDERING THAT PAID FOR ITSELF TWICE

**Fire 2: 4.9 core-min of a 532.0 ceiling** (`Sc` 3.4333 + `Ec` 1.4667). Fire 1: 0.7, named as
waste. **Total 5.6 core-min, $0.0048 DERIVED** at the owner-stated $0.0513/core-h, **not measured**.

**The coarse-pair-first ordering has now saved the L3 budget twice** — once on a setup defect
(Addendum E) and once on the item's actual answer. **The question `A1ZE` exists to ask about `CL`
and `CD` cannot be answered at all**, because the treatment arm cannot run in this toolchain: there
is no `empty` solve to compare against. `§1b`'s coefficient question is **`BLOCKED` by the
toolchain, not unmeasured by choice**, and `S3`/`E3` are not worth 514 core-min to re-confirm what
`Ec` established for 1.4667.

**Calibration, rule 12:** `Sc` actual **3.4333** against its registered `est @ n=6 (MEASURED)` of
**1.8374** — ratio **1.87×**, inside its 9.0 cap; contention at launch was `loadavg 33.64` on 16
cores with one other container, i.e. well above the n=6 anchor's conditions. A full
`COST_CALIBRATION.md` row is owed **when the supervisor rules on whether this item is complete** —
it has answered its verification question and cannot answer its coefficient question.

**SUBMISSIONS PARKED.**

---
---

# ADDENDUM G — 2026-09-03 — **v1.7** — `G-GUARDS` REFUSED A CLEAN ARM ON A PATH BUG, AND THE FROZEN GRADER **CANNOT LAWFULLY BE REPAIRED FOR THIS ITEM**

**`lines whose number changed above this section: 0`** — first **731** lines byte-identical to
`03120e22`, **845** to `2a31f940`, **988** to `cd7d383a`. Addenda A–F untouched. **No gate,
threshold, cap or label changes — and after first compute none may.**

## G.1 THE DEFECT, AND IT IS THE INVERSE OF WHAT IT LOOKS LIKE

The grade printed:

> `G-GUARDS Sc: NOT A RESULT -- 4 guard(s) left no execution marker, so they cannot be shown to have
> run: ['A1ZE_COLD_START', 'A1ZE_G_EMPTY_OK', 'A1ZE_TIMEDIR_SCAN', 'A1ZE_TOL_VAR_OK']`

**All four markers were present. Measured, in `logs/Sc_20260903T190524Z.log`: 1 occurrence each.**

| marker | in the **docker log** | in `out/sweep.log` |
|---|---|---|
| `A1ZE_G_EMPTY_OK` | **1** | 0 |
| `A1ZE_TIMEDIR_SCAN` | **1** | 0 |
| `A1ZE_TOL_VAR_OK` | **1** | 0 |
| `A1ZE_COLD_START` | **1** | 0 |

`G-GUARDS` searches `<arm>/out/guards.log` — **never written** — and `<arm>/out/sweep.log`, which is
the *runScript's* redirected stdout and by construction cannot contain the *wrapper's* prints.
**The markers live in the docker log at `<root>/logs/<arm>_<stamp>.log`, and `G-GUARDS` never looks
there.** A one-line path bug.

**⚠ IT IS NOT THE VACUOUS-PASS DISEASE; IT IS ITS MIRROR.** A vacuous pass admits an arm that was
never checked. **This REFUSES an arm that was fully checked.** It fails **closed**, which is the
safe direction and is why it cost nothing here — but a guard that cannot see its own evidence would
make **every clean arm `NOT A RESULT`**, and that is a defect in exactly the way A1WR's unreachable
1e-8 was: **a gate whose passing condition cannot be met by a correct run.**

## G.2 IT CHANGED NOTHING, AND THAT IS CHECKED, NOT ASSUMED

`A1ZE_VERDICT NOT A RESULT` is reached **independently and over-determinedly**: `COMPLETION Ec`
failed on `rc=97`, no `End`, and `last Time = None != 2000`; `G-COEF` on both pairs returned
`NOT A RESULT` because an arm of each pair did not complete; `S3`/`E3` never staged. **Strike
`G-GUARDS` entirely and the verdict is unchanged.** The false refusal is a defect in the
instrument, not a change to the item's answer.

## G.3 ⚠ IT CANNOT BE REPAIRED FOR THIS ITEM, AND THE REASON IS RULE 2

**A1ZE has spent compute — 5.6 core-min across two fires — so its gates are CLOSED.** Rule 2: after
first compute, *"changes land only as dated addenda that cannot alter a gate, threshold, cap or
label."* **`G-GUARDS` is a gate.** Repairing its reader changes which arms it admits, and that is a
gate change by any honest reading.

**So: the frozen grader is NOT edited, and no other reader may be substituted for it** — the
D19/D19R2 precedent this family already carries (*a refusal is not a verdict, and the grading path
is fixed at the pre-registration commit*). **The repair belongs to a SUCCESSOR ITEM, not to
A1ZE.** Registered here as the successor's first requirement, so the next registration inherits it:

> **`G-GUARDS` must read the arm's DOCKER LOG (`<root>/logs/<arm>_<stamp>.log`), which is where the
> in-container wrapper's stdout is captured, and must be driven on a REAL completed arm before it is
> frozen** — the fixture-only proof this item used passed happily while pointed at a file that never
> exists. **A control that proves a reader can parse a marker does not prove the reader can FIND
> one**, and that is the same distinction as *"plant the run, not only the value"*, one level up.

**No frozen instrument was edited to establish any of this.** The diagnosis is entirely from the
run's own artifacts and from `grep -c` over them.

## G.4 STATE

`d3f47bfa` is **reverted forward** on the measured engineering fact that the templates could not
run — **not** on a gate reading, and **not** on this item's verdict, which remains `NOT A RESULT`.
The record files `cases/dafoam/PATCH_IDENTITY_D3F47BFA_REVERTED.md` and the three template
`README_PATCH_IDENTITY.md` notes carry that distinction on their first screen, as does the revert
commit's own message.

**Zero further solver core-min. SUBMISSIONS PARKED.**
