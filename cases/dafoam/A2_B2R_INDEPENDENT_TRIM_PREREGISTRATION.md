# A2-B2R — independent lift-trim of the twist+shape wing — PRE-REGISTRATION (frozen, NOT launched)

Filed 2026-09-01, dafoam lane, on the supervisor's ruling that A2's row
`B2_twist_shape_CL05` is not repaired by amendment. **A2's gates are closed.**
This is a separate, newly pre-registered successor item in this family's
established successor pattern (SO-1cR, D19R, SO-3aR2, D4S-F3SR), and
`cases/dafoam/A2_DRAG_DECOMPOSITION_PREREGISTRATION.md` is **not edited by it**.

**No compute has been spent on this and none will be until the supervisor gives
the launch go.** The run root asserted absent in §9 does not exist at freeze
time, and the absence was read against a positive control.

---

## 1. The one question

> Does an **independent lift-trim** of the twist+shape MACH Tutorial Wing,
> started from a **third incidence offset from both endpoints**, land on row
> **A4**'s drag inside the same **0.5 %** band gate `G5` registered?

That is the falsifier that did not fire. Nothing else is asked here.

## 2. What A2 established, what it did not, and where the citation points

A2 was frozen at blob **`899352ae5c9f81a90b47d75d6642d80c8364b3bf`**. That is a
**BLOB, not a commit** — the object class is stated because
`VERIFICATION_CHARTER.md` §2b v1.15 requires it and because the distinction is
load-bearing here. Verified at source before anything was written:

| what | verified |
|---|---|
| the blob exists and is a version of the A2 pre-registration | yes — `git cat-file -t` returns `blob`; its first line is the A2 title |
| it is the **pre-compute** state | yes — **267 lines**, ending at amendment 1; the current blob `134dbe3a456fd7cef27c34df9744eaeffb5e3f2a` is **420 lines** and carries the results addendum |
| the commit that introduced it | **`c8c470b8`** (pre-compute amendment 1) |
| the A2 record on disk is the committed one | yes — `git diff HEAD` on that path is empty; §R1–R8 as read here are HEAD's |

**A2 landed six of seven rows.** Row `B2_twist_shape_CL05` raised
`openmdao.core.analysis_error.AnalysisError: 'scenario1.coupling.solver' <class
DAFoamSolver>: Error calling solve_nonlinear(), Primal solution failed!`
(`/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/decomp.log:3996`) after
three primals, and is **NOT A RESULT**. `G5` is **UNGRADED**.

**The consequence, restated so this document does not overclaim what it is
repairing.** A2 §R8: the angle-of-attack-share-is-zero claim rests on `G6` (both
endpoints measured at CL = 0.500 within 1e-3) and on the problem's own equality
constraint (`runScript_AeroOnly.py:179`), **and on nothing more**. This rung
buys back the independent test. It does **not** buy back anything else, and A2's
own author already recorded, against their own design, that `B2` was a weaker
falsifier than intended: started at the final incidence it begins at CL 0.49995
— inside `G3`'s own 5e-4 band — and confirms A4 almost tautologically.

## 3. The repair is the STARTING POINT. It is not the threshold

**`G5`'s threshold is carried across byte for byte.** The frozen A2 text at blob
`899352ae` reads `**0.5%**`; this rung's comparator constant is `BAND = 0.5`
(`cases/dafoam/grade_a2b2r.py:52`), and the frozen token was hexdumped
(`2a2a 302e 3525 2a2a` = `**0.5%**`) rather than eyeballed.

**Why a changed start is not a changed threshold, in one line.** A threshold is
the scoring rule and belongs to the hypothesis; a starting point is an input to
the instrument and belongs to the experiment. Moving the bar changes what counts
as agreement; moving the start changes only whether the test is capable of
disagreeing. A2's `B2` was *incapable of disagreeing informatively* from one
start and *incapable of converging* from the other; both are instrument defects,
and neither is repaired by widening a band. **Nothing a verdict depends on may be
repaired on the authority of the verdict it produces**
(`VERIFICATION_CHARTER.md` §2d.1), and no verdict here depends on the start.

## 4. The start incidences, derived from measurement

### 4.1 The bracket, and the confound in it that A2 did not name

Two measured trim searches exist on this case, both in A2's own run:

| row | geometry | start CL | offset \|CL − 0.5\| | direction | outcome |
|---|---|---|---|---|---|
| `B1_twist_only_CL05` | twist only | 0.45966586124 | **0.040334139** | **BELOW** | CONVERGED to \|CL−0.5\| = 5.29e-07, AoA 4.90933 |
| `B2_twist_shape_CL05` | twist + shape | 0.72193449611 | **0.221934496** | **ABOVE** | DIVERGED after 3 primals |

**The bracket is CONFOUNDED, and this is a correction to A2's own triage.** A2
§R3 attributes B2's failure to the *magnitude* of the excursion. But the single
converging observation approached from **below** and the single diverging
observation approached from **above**. Magnitude and direction move together
across the only two points there are, so the record cannot presently tell them
apart. This rung is designed to separate them, and says so before it runs.

### 4.2 The lift-to-incidence slope, on this geometry, from this run

Both endpoints of the twist+shape geometry were measured in A2:

* `A2_twist_shape`: AoA 4.32612781 deg → CL 0.72193449611
* `A4_final`: AoA 1.10765738 deg → CL 0.49994884178

Secant **dCL/dα = 0.068972407 per deg**. It is a two-point secant over 3.218
deg, so every start-CL figure below is an **inference, registered as a
prediction with a band**, not a measurement.

### 4.3 The choice, and it is not taste

**Arm `R4`, from ABOVE.** Take the **geometric mean** of the bracket —
the scale-free midpoint between a magnitude known to converge and a magnitude
known to diverge: √(0.040334139 × 0.221934496) = **0.094612561**. At the secant
slope that is **1.371745 deg** above the final incidence, i.e. **2.4794025 deg**.
Registered rounded to **α = 2.48000 deg**; the rounding moves the predicted start
CL by **4.12e-05**, which is 0.04 % of the offset.

**Arm `R2`, from BELOW.** Symmetry would put it at 1.10766 − 1.37175 =
**−0.264 deg**, which violates the registered design-variable bound
`patchV lower=[U0, 0.0]` (`runScript_AeroOnly.py:175`). Symmetry is therefore
**unattainable inside the bound**, and `R2` takes the largest below-start the
bound allows while staying **0.20 deg clear of it**, so the start is not
bound-active: **α = 0.20000 deg**.

| arm | α start (deg) | predicted start CL | offset | ratio to the converging point | ratio to the diverging point | offset from 4.32613 | offset from 1.10766 |
|---|---|---|---|---|---|---|---|
| `R2` from below | **0.20000** | 0.4373455 | **−0.0626545** | **1.553×** | 0.282× | 4.12613 deg | 0.90766 deg |
| `R4` from above | **2.48000** | 0.5946026 | **+0.0946026** | **2.345×** | 0.426× | 1.84613 deg | 1.37234 deg |

Both are offset from **both** endpoints. `R4` sits at 2.345× the converging
magnitude and 0.426× the diverging one — by construction, symmetric in ratio.

### 4.4 The residual risk, stated plainly

**The bracket has two points and cannot exclude a failure between them.** The
trim search's convergence boundary is known only to lie somewhere in
(0.040334, 0.221934) in lift offset, if it is a function of offset at all — and
§4.1 says it may be a function of direction instead. `R4` at 0.0946 sits inside
that unknown interval. **A second divergence is therefore a live outcome, not a
surprise, and it is registered as a graded branch in §6.4 with its own label.**

## 5. The rows — frozen in `cases/dafoam/a2b2r_rows.json`

sha256 `40a3fe7b559d4c1f66b78f1db64caa56d5efd4b93ee3ca5c480721bd76abe487`.
Evaluated in this order, in one container session, by the **unchanged** A2
driver. Twist (7) and shape (96) are copied element-for-element from A2's
`A4_final` row and asserted equal to its `A2_twist_shape` row at generation.

| # | row | twist | shape | α start | trim | purpose |
|---|---|---|---|---|---|---|
| 1 | `R1_A4_anchor_cold` | final | final | 1.10765738 | — | in-session A4 reproduction, **cold**. Gate `G1R`; the denominator of every `G5`/`G6R`/`G7R` gate |
| 2 | `R2_trim_from_below` | final | final | 0.20000 | 0.5 | independent trim, lower-risk arm |
| 3 | `R3_A4_anchor_warm` | final | final | 1.10765738 | — | **warm-start control**, `G7R`: A4 repeated after a completed trim has moved the state |
| 4 | `R4_trim_from_above` | final | final | 2.48000 | 0.5 | independent trim, higher-risk arm; **runs last by design** |

**Why this order.** An `AnalysisError` terminates the whole process — measured:
A2's `B2` killed the run and cost nothing downstream because nothing was
downstream. Here the anchor, the lower-risk arm and the warm control all bank
their values **before** the arm most likely to diverge. The blast radius of an
`R4` divergence is `R4` alone. The blast radius of an `R2` divergence is `R2`,
`R3` and `R4`, and that is registered, not hoped away.

**The denominator is the in-session anchor `R1`, not A2's stored number.** A2's
own `G5` compared `B2` against `A4` measured in the same run; this is the
faithful analogue, and it removes cross-session drift from the falsifier. A2's
stored `CD = 0.02124478277` is used only by `G1R`, as a reproduction check.

## 6. Gates, and the verdict each outcome maps to

### 6.1 The gate table

| id | gate | threshold | on failure |
|---|---|---|---|
| **G1R** | anchor reproduction | \|CD(R1) − 0.02124478277\| / 0.02124478277 ≤ **0.5 %** AND \|CL(R1) − 0.49994884178\| ≤ **5e-4** | whole rung **NOT A RESULT** |
| **G2R** | geometry control | `thickcon` at R1: min ∈ [0.4995, 0.5006], max ∈ [1.726, 1.730] | **NOT A RESULT** — the shape vector never reached the mesh |
| **G3R** | trim tolerance | each trim row reaches \|CL − 0.5\| ≤ **5e-4** | that row **BLOCKED**, reported as such, never estimated |
| **G4R** | completion, per row | exactly one `DECOMP_RESULT` line; worst per-equation `finalRes` ≤ **1e-6**; DV set/readback ≤ 1e-12 | that row **NOT A RESULT**; reported, never dropped |
| **G5-R2** | **the falsifier, arm 1** | \|CD(R2) − CD(R1)\| / CD(R1) ≤ **0.5 %** | that arm **GATE FAIL**; A2 §3's structural argument is falsified and that is reported |
| **G5-R4** | **the falsifier, arm 2** | \|CD(R4) − CD(R1)\| / CD(R1) ≤ **0.5 %** | as above |
| **G6R** | cross-arm consistency | \|CD(R4) − CD(R2)\| / CD(R1) ≤ **0.5 %** | falsifier **F1** fires — see §6.5 |
| **G7R** | warm-start control | \|CD(R3) − CD(R1)\| / CD(R1) ≤ **0.5 %** | falsifier **F3** fires — the one-process protocol biases rows, which puts A2's own warm A4 row in question too |

### 6.2 `G4R` corrects a conflation in A2's own `G4`, and says so

A2's `G4` reads *"primal meets the case's own `primalMinResTol = 1e-8`"*, and
A2's results table then reports **worst final residuals of 4.15e-07 to
6.02e-07** — which do not meet 1e-8 — and calls the gate PASS on the ground that
they are *"the same order as the published converged baseline"*.

**These are two different quantities.** `primalMinResTol` acts on DAFoam's
**normalised total** residual; the log prints **per-equation `finalRes`** per
SIMPLE iteration, and the two are not comparable. `G4R` is registered on the
quantity the comparator can actually read — per-equation `finalRes` ≤ **1e-6**,
a threshold set from A2's measured 4.15e-07…6.02e-07 with **1.66× headroom** —
and this document states the substitution rather than inheriting the conflation.

### 6.3 The process return code is recorded, and it grades nothing by itself

A2's `RUN_RC.txt` reads `INNER_RC=1` because `B2` crashed, while six rows were
individually clean. The comparator prints `INNER_RC` and
`DECOMP_ALL_ROWS_DONE` **beside** the per-row verdicts and never lets either
condemn or rescue a row on its own. *Bookkeeping never voids physics; physics
never launders bookkeeping.*

### 6.4 The registered branches, including the second divergence

| branch label | condition | row verdict | gate verdict | rung verdict |
|---|---|---|---|---|
| `TRIMMED` | row completes and meets `G3R` | graded | `PASS` or `GATE FAIL` on `G5` | see below |
| `BLOCKED-TRIM` | row completes but misses `G3R` | **BLOCKED** | `G5` **NOT A RESULT** | — |
| `DIVERGED-TRIM` | `AnalysisError`, no `DECOMP_RESULT` line | **NOT A RESULT** | `G5` **NOT A RESULT** (arm UNGRADED) | — |
| `CAP-STOPPED` | the 600 s cap fired | rows not reached are **PENDING** | — | — |

**Rung verdict mapping, fixed here:**

| condition | rung verdict |
|---|---|
| `G1R` or `G2R` not PASS, or the DV control not clean | **NOT A RESULT** |
| both `G5-R2` and `G5-R4` PASS | **PASS** |
| either `G5` reads GATE FAIL | **GATE FAIL** |
| exactly one arm PASS, the other produced no value | **GATE REACHED** |
| no arm produced a value | **NOT A RESULT** — and A2's registered falsifier is again UNGRADED, which is the honest sentence, not a softer one |

Only the six tokens `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING` appear in any verdict cell. `PENDING` is used only for
"not yet run", never to soften a `GATE FAIL`.

### 6.5 Registered falsifiers — the ones that would embarrass the expected answer

* **F1 — the equality constraint does not pin the drag.** If both arms meet
  `G3R` (both genuinely at CL = 0.500 ± 5e-4) but `G6R` fails, then two
  independent trims of the *same geometry* to the *same lift* disagree on drag
  by more than the band. **A2 §3's structural argument is then FALSIFIED** — the
  angle-of-attack share is not zero by construction, because the trim path
  matters — and the 28.3 % headline must be requoted with a trim-path
  uncertainty. This is the outcome this rung most exists to be able to find.
* **F2 — B2's failure is directional, not magnitudinal.** If `R4` diverges while
  `R2` converges, §4.1's confound resolves against §4.3's derivation: the
  bracket argument in this very document is then wrong in its own terms, and the
  finding is that the trim search fails *from above* at a magnitude it survives
  *from below*. Recorded as a correction to this document's reasoning, not as a
  nuisance.
* **F3 — the sequential one-process protocol biases rows.** If `G7R` fails, the
  warm A4 does not reproduce the cold A4, and **A2's own `A4_final` — which ran
  fifth, warm — is retroactively in question**, along with its `G1` PASS.

## 7. Controls (rule 3), and the plant is RELATIVE

**Control 1 — design-variable readback.** The frozen driver reads every vector
back out of the problem and refuses (`DECOMP_REFUSE`, `RuntimeError`) above
1e-12 (`a2_decomposition_driver.py:294-303`). A2 measured **0.000e+00 on all
seven rows**.

**Control 2 — `thickcon` as a geometry-side witness.** Exactly 1.0 on the
baseline geometry, [0.500101, 1.727944] on the final one. A shape vector that
never reached the mesh reads 1.0, and `G2R` refuses.

**Control 3 — the planted zero, registered RELATIVE.** This family's live hazard
is the **absolute** plant that does not port across functionals: SO-2M's plant
was **2.479781 % against a 5.0 % band**, short of crossing by **2.016307×**, so
it could not have detected a blind reader at all. Here:

> **P = K · (BAND/100) · |d_ref|**, with **d_ref = CD(R1_A4_anchor_cold)** and the
> **sign set AWAY from d_ref**, so the planted deviation is
> `|original| + K·BAND` and cancellation is unreachable by construction.

| leg | K | planted deviation | crossing factor | required outcome |
|---|---|---|---|---|
| **GREEN**, on `R1` (self), `R2`, `R4` | **3.0** | ≥ 1.5 % against a 0.5 % band | **≥ 3.0×** | the reader **MUST** see it. If not: `PLANT_NOT_SEEN`, **exit 2**, rung **NOT A RESULT** |
| **RED / sufficiency**, on `R1` (self) | **0.5** | 0.25 % | **0.5×**, i.e. **2.0× below** the crossing threshold | the reader **MUST NOT** see it, and the control **MUST refuse BY NAME** with the literal token `PLANT_NOT_SEEN`. A bare non-zero exit is **not accepted** — an unrelated crash also exits non-zero, and the token is what separates them. If a sub-band plant flips the gate: `PLANT_SUFFICIENCY_FAIL`, exit 2 |

The RED leg runs on the anchor's **self-comparison**, where the unplanted
deviation is identically 0, so the planted deviation is exactly K·BAND and the
leg's applicability does not depend on what the run measured. **The plant is
written to a copy of the log ON DISK and read back through the same parser and
the same gate function** — never patched in memory. Two further refusals guard
the plant itself: if the planted file is byte-identical to the source, or if the
read-back CD differs from the value written, the leg reports `PLANT_NOT_SEEN`
rather than a spurious clean pass.

**Driven, not asserted.** `python3 cases/dafoam/grade_a2b2r.py --selftest`
exercises 27 legs before any solver runs — including K = 0 (must NOT be seen, so
the control is not stuck on `SEEN`), K = 3 (crossing measured at **exactly
3.000000×**) and K = 0.5 (measured at **0.500000×**). `run_a2b2r.sh` refuses to
launch if that selftest does not pass.

## 8. The age guard — rule 4's premise is FALSE here, and this is not boilerplate

`D19` was refused by `REFUSE G1 age_datum_moved` because CLAUDE.md rule 4's
premise — that `0/T` is touched last at launch and therefore dates the run — does
not hold for DAFoam. **Measured on this exact case, at zero new compute:**

1. **`0/` does not exist to be pinned.** The pristine tree
   `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing` carries `0.orig/` and no
   `0/`. `preProcessing.sh` creates `0/` **inside the container** with
   `cp -r 0.orig 0` — i.e. **after** the launch datum. A pre-launch manifest
   cannot pin a file that does not yet exist.
2. **The rewrite happens under `processor*/0/`, not only at case level.** In
   `/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/case`,
   `processor0/0/U.gz` carries mtime **01:09:35** — the run's end — while its
   five siblings carry **01:06:35**, the `decomposePar` time. Case-level `0/*`
   all stayed at 01:06:29.
3. **The names carry `.gz` there and not at case level**, because
   `system/controlDict:27` sets `writeCompression on`. This is the same shape as
   `D19`'s `T` → `T.gz`.
4. **A COUNT IS NOT AN IDENTITY.** `D19`'s file-count clause passed by
   coincidence — 9 before, 9 after, six of the nine names changed. **Nothing in
   this rung's guard compares a count.** Every decision is per **NAME** with a
   **CONTENT HASH** beside it.

### 8.1 What is registered instead

**Datum:** `t0`, written by the launcher after the last stage copy and before
`docker run`. A2's own datum had **5 ms** of margin (instrument copy at
1788224781.093, `t0` at 1788224781.098); the launcher now sleeps 1 s between
them so the age relation cannot turn on filesystem timestamp granularity.

**Manifest:** the staged files the run must not rewrite, by **name + sha256 +
mtime**, taken post-stage and pre-launch.

**The exclusion is ENFORCING, not descriptive.** A prior selftest in this lab
recorded `excluded_write_targets: ['0']` while `0/U` sat pinned in the same
manifest — a record asserting what the code did not guarantee. Here a single
function `partition()` (`cases/dafoam/a2b2r_age_guard.py`) applies one predicate
`is_write_target()` to one enumeration and returns **both halves from one pass**.
The pinning loop consumes the first; the `excluded_write_targets` a record may
quote is the second and nothing else. At verify time every pinned name is
re-classified with that same predicate, and a disagreement refuses with
`REFUSE_PIN_EXCLUSION_DISAGREE`.

**The predicate is derived from measurement, not taste.** Of the **23** staged
pristine files in A2's run, **exactly one** changed:
`system/decomposeParDict`, which DAFoam rewrites with its own
`numberOfSubdomains`. The other 22 were byte-identical afterwards and all kept
mtime < `t0`. 147 new files were created, every one of them under an excluded
head.

### 8.2 The legs, all driven

| leg | required refusal | driven |
|---|---|---|
| predicate classifies `0/T`, `0/T.gz`, `processor0/0/T.gz`, `processor3/0/U.gz`, `1000/U`, `constant/polyMesh/points.gz`, `system/decomposeParDict` as **write targets** | — | PASS (14 paths) |
| predicate classifies `system/fvSchemes`, `0.orig/U`, `constant/thermophysicalProperties`, the driver, the row spec, the geometry tarball as **pinned** | — | PASS (14 paths) — an over-matching predicate that excluded everything would make the guard vacuous, and `REFUSE_PREDICATE_OVERMATCH` fires at pin time if it does |
| pinned name that is really a write target | `REFUSE_PIN_EXCLUSION_DISAGREE` | PASS |
| **rename at CONSTANT file count** (13 → 13, `fvSchemes` → `fvSchemes.gz`) | `REFUSE_MANIFEST_NAME_MISSING` | PASS |
| same name, mutated content | `REFUSE_MANIFEST_HASH_MOVED` | PASS |
| pinned file newer than `t0` | `REFUSE_AGE_DATUM_MOVED` | PASS |
| graded artifact older than `t0` | `REFUSE_ARTIFACT_NOT_NEWER` | PASS |
| census blind to `processor*/0/` | `REFUSE_CENSUS_BLIND` | PASS |

**Positive control on the real tree, not a fixture.** Run against
`/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/case` the census reads
**170 files, 25 pinned, 145 excluded, 24 `processor*/0/` files seen** — the
enumeration provably reaches the site of the D19 rewrite. A full
stage → pin → simulate-run → verify cycle was driven end to end on real DAFoam
files and returned `AGE_GUARD_OK pinned_names_verified=25
processor_zero_seen=24`, and mutating one pinned file in that same tree returned
`REFUSE_MANIFEST_HASH_MOVED system/fvSchemes`.

## 9. Instrument and grading path — fixed at this pre-registration commit

**The driver is A2's, byte-identical and unchanged.** Nothing is derived from an
A2 ancestor by mechanical rename, so this rung is not exposed to the defect class
that cost `SO-2MR` its first arm (md5 pins stale the instant a rename rewrote the
bytes they pinned) or to `SO-3aR`'s (a rename turned a real directory name into
one that does not exist). Verified: the driver on disk hashes to git blob
`7fe3e45aa329e4815c55feb95053cd9892b71f35`, identical to
`HEAD:cases/dafoam/a2_decomposition_driver.py`. The only new inputs are a row
spec, a launcher, a guard, a comparator and a census, all written fresh.

**A2 disclosed that its grader was written AFTER first compute and carried no
independent authority (A2 §R7). That is not repeated here:** every script below
exists and is committed **in this freeze commit**, before any compute.

| role | path | md5 | sha256 |
|---|---|---|---|
| `instrument` | `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing/runScript_AeroOnly.py` | `2906d52a5dbed2bacbaeaf85a37d3fe8` | `0ce111ae9aa2f940dc73dcb029e2cf33b3239284fee97438f2a657aab8aca3b1` |
| `instrument` | `cases/dafoam/a2_decomposition_driver.py` | `a3b55171b38f25395d086e8c7f6f448c` | `c4f421497ae221ae1f8fb2f655530ea552e6372a935a6d3e0355ce81a4389cf0` |
| `instrument` | `cases/dafoam/a2b2r_rows.json` | `217fc111eaf8267427f6d36cd1e450a2` | `40a3fe7b559d4c1f66b78f1db64caa56d5efd4b93ee3ca5c480721bd76abe487` |
| `instrument` | `/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/case/mdolab_wing_surface_mesh.cgns.tar.gz` | `92956aa0e4cb9b17fa063bd95e8f78ba` | `bc70f99cc4eadbfc3ab5f211b6e3d5b857e571ff419dcebdedc0a328e498c53e` |
| `grading-path` | `cases/dafoam/a2b2r_age_guard.py` | `e15eb1d3053e46a1560808ab63cc528b` | `ca5ffa023affba713795c1343de0cea83bad79e06155073c661d422990f1531f` |
| `grading-path` | `cases/dafoam/grade_a2b2r.py` | `0e1133d9806db852276fbf1b8eb3f31f` | `78ae0ec1a3f534e5a37928c38bcbdb5f3cd9519b5b0592f1bba35497801bcd77` |
| `grading-path` | `cases/dafoam/run_a2b2r.sh` | `c4beaa1c388c0425440203b98a1460f8` | `ac4f248f5849cedbb00b566cf5f5ef330f207d39e1d1a27295d936f1afd36b98` |
| `grading-path` | `cases/dafoam/a2b2r_pin_census.py` | `9680328cbf7de9b0dd5e21320c51830a` | `ac400159e43dedc72e65fd9f60296d30fc5b92bb45c3bff84e1b369713b11f96` |

**`pins_exist == pins_driven`, by role, and it is checked by code**
(`cases/dafoam/a2b2r_pin_census.py`), not by this table asserting it:

* **`instrument`** — secured **at run time**. Every one of the three has its
  hash asserted by a literal inside `run_a2b2r.sh`, which refuses to stage
  anything if one differs; and every hash literal in the launcher must belong to
  a pin, or `REFUSE_LITERAL_UNPINNED` fires. That second half is what catches the
  `SO-3aR` shape: a citation with no referent.
* **`grading-path`** — secured **by the freeze commit**. Nothing asserts these at
  run time and nothing could without circularity, so the census compares each
  against its committed git blob and refuses with `REFUSE_PIN_NOT_COMMITTED` on
  a difference.

The census also re-hashes every pinned path on disk and refuses `REFUSE_PIN_STALE`
on any mismatch, which is exactly the check `SO-2MR` did not have.

**Toolchain identity, by hash and not by version string** (`DAFOAM_CHARTER.md`
§6): container image `dafoam/opt-packages:latest`, **image ID `9d45679d55fd`**,
the **SHIPPED** toolchain — no `PYTHONPATH` override, no IDWarp bind-mount, no
patched library. This is the same image and the same protocol A2 ran on, which
is what makes `R1` a reproduction of `A4` rather than a comparison across
toolchains. **This rung produces a SHIPPED row only.** It makes no claim about a
patched toolchain and none may be read from it.

**Run root, asserted ABSENT at freeze time, against a positive control:**

```
ABSENT  /home/ubuntu/certonomous-runs/A2B2R-independent-trim
EXISTS  /home/ubuntu/certonomous-runs/ACTD-a2-decomposition
```

The second line is the positive control: **the same check reports `EXISTS` for a
directory that does exist**, so `ABSENT` on the first is a reading and not a
blindness. `ls` on the first returns "No such file or directory". The launcher
refuses (exit 2) if it exists.

## 10. Cost — pre-registered per rule 12

**Basis, measured on the rows this rung repeats, not recalled.** A2's own
`ExecutionTime` ledger, read from
`/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/decomp.log`:

| item | measured |
|---|---|
| plain primal, rows A1/A2/A3/A4 | **13.61 / 13.73 / 13.56 / 13.71 s** — mean **13.65 s** at 4 ranks |
| first row A0, including solver warm-up | **15.38 s** |
| `B1` trim search, offset 0.0403, converged | **68.14 s** = **4.99 primal-equivalents** |
| `B1` confirm primal after the trim | **13.45 s** |
| container start + `preProcessing` + OpenMDAO setup | ≈ **15 s** (208 s total wall − 193.01 s accumulated `ExecutionTime`) |

**The rate this document does NOT use, and why.** A2 §8 priced 24.7 s per
evaluation from the optimisation log's 3606 s / 146 evaluations. That average
absorbs 47 gradient computations, over-priced primal-only work by **1.8×**, and
is the named cause of A2's **0.43×** actual/predicted ratio. It is not reused.

| item | count | basis | wall s | core-min |
|---|---|---|---|---|
| container start + mesh + setup | 1 | measured ≈ 15 s, registered at 20 | 20.0 | 1.33 |
| `R1` anchor primal (first row) | 1 | 15.38 s | 15.4 | 1.03 |
| `R2` trim search | 1 | 1.25 × B1's 68.14 s | 85.0 | 5.67 |
| `R2` confirm primal | 1 | 13.71 s | 13.7 | 0.91 |
| `R3` warm anchor primal | 1 | 13.71 s | 13.7 | 0.91 |
| `R4` trim search | 1 | 1.47 × B1's 68.14 s | 100.0 | 6.67 |
| `R4` confirm primal | 1 | 13.71 s | 13.7 | 0.91 |
| chown + cost + guard + grade | 1 | — | 5.0 | 0.33 |
| **registered point** | | | **266.5** | **17.8** |

**Band, from the trim search being the only uncertain term:** low **14.2**
core-min (both trims at B1's measured 68 s), high **27.1** core-min (both trims
at 2× and 2.5× B1, plus a 30 s setup).

**Hard cap: 40.0 core-min = 600 s wall at 4 ranks**, enforced by `timeout 600s`
inside the container. That is **1.48×** the top of the band. **An overrun stops
the run; it does not get a new budget.** Rows completed before the cap are graded
on their own gates; rows not reached are **PENDING**, never estimated.

**Divergence and stall aborts, registered:**

* **Divergence** — an `AnalysisError` propagates and terminates the process. This
  is measured, not assumed: A2's `B2` died **41.4 s** into its trim, so a
  diverging arm is *cheap*, not expensive.
* **Stall** — a trim search that neither converges nor diverges is stopped by the
  600 s container timeout. This is the failure mode the cap is actually for, and
  A2's `B2` printed its own tell: lift values sitting at 0.7219356 / 0.7219896
  without advancing.

**Memory (`DAFOAM_CHARTER.md` §7 — predicted before the launch, not after).**
Container capped at `--memory=12g`. A2's identical run completed under that cap
with **no OOM, no kill and no memory error anywhere in its log**, so 12 GiB is a
demonstrated **upper bound** for this configuration — a bound, explicitly not a
peak-RSS measurement, because none was taken. Host headroom at freeze time:
**28 GiB available of 30 GiB total**. A run stopped by memory would be recorded
as stopped by memory and would be **NOT A RESULT about convergence**.

**Dollars, DERIVED NOT MEASURED.** 17.8 core-min = 0.2967 core-h → **$0.0152**;
at the cap, 0.6667 core-h → **$0.0342**. Rate **$0.0513/core-h, c7a.4xlarge,
reported-by-owner (Sanaa 2026-08-21/22), never measured — this box cannot read
its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). Three orders of magnitude
under the $25 pre-authorisation; **a blanket is not a per-item read**, and this
is the per-item read.

Per rule 12's calibration clause, the completion report will carry actual
core-minutes from this run's own `t0`/`t1` ledger against the **17.8** predicted
here, with the ratio, its attribution, and waste named separately — and it will
land as a row in `docs/COST_CALIBRATION.md`.

## 11. Predictions — committed before the solver starts

A2 registered 7 predictions, 5 landed inside band, and **A2's own drag
prediction MISSED** (registered ≥ 0.045, measured 0.03721) and was recorded as a
miss rather than rounded in. That is the standard held here.

| # | prediction | band | reasoning |
|---|---|---|---|
| P1 | CD(R1) | 0.02124478277 ± **0.5 %** | reproduction of A4 on the same image and protocol |
| P2 | CL at R2's start, before trimming | **0.4323 – 0.4424** (point 0.4373455) | secant slope, ±8 % on the offset |
| P3 | CL at R4's start, before trimming | **0.5870 – 0.6022** (point 0.5946026) | secant slope, ±8 % on the offset |
| P4 | final AoA of R2 and R4 | both within **0.02 deg** of 1.10766 | `G3R`'s 5e-4 in CL is 0.0073 deg at the secant slope |
| P5 | \|CD(R2) − CD(R1)\|/CD(R1) | ≤ **0.1 %** — deliberately **five times tighter than the gate** | if lift is genuinely pinned, the two should agree far inside the band; a value between 0.1 % and 0.5 % passes `G5` and still fails this prediction, and will be reported as a miss |
| P6 | \|CD(R4) − CD(R1)\|/CD(R1) | ≤ **0.1 %** | as P5 |
| P7 | R2's trim converges | **stated as likely** | same direction as the only converging observation, at 1.553× its magnitude |
| P8 | R4's trim converges | **stated as UNCERTAIN, ~60 %** | same direction as the only *diverging* observation, at 0.426× its magnitude, inside a bracket with two points in it |
| P9 | gross cost | **17.8** core-min, band 14.2 – 27.1 | §10 |

**If the measurement contradicts these, the measurement is the finding and it
goes on the page.**

## 12. What this rung does not buy, stated so nobody reads more into it

1. **It does not re-verify the gradient.** No adjoint runs here; nothing in it
   touches `DAFOAM_CHARTER.md` §2's FD-table duty, and it makes no gradient
   claim.
2. **It does not re-run the optimisation.** The 28.3 % still rests on a preserved
   history file, verified gradients and a preserved optimiser log
   (`W5_GRADIENT_REGRADE.md:373-374` still lists S11 as NOT REGRADED). This rung
   re-evaluates endpoints, exactly as A2 did.
3. **It produces a SHIPPED row only** — see §9. No patched-toolchain claim.
4. **It cannot fully de-confound §4.1.** Two new points give a 2×2 with one cell
   each; direction and magnitude are separated only at the magnitudes tested. A
   full de-confounding would need arms this rung does not buy, and that is a
   limitation, not an oversight.
5. **A `PASS` here confirms the falsifier fired and found nothing.** It does not
   convert A2 §3's structural argument into an empirical measurement of an
   angle-of-attack share; that share remains zero *by construction* of the
   equality constraint, and this rung only shows the construction is not
   contradicted from two independent starts.

## 13. Status

**FROZEN, NOT LAUNCHED.** Awaiting the supervisor's check 4 and check 1 and the
launch go. No solver has been started; the run root does not exist; every
selftest above was driven before this document was written, and `run_a2b2r.sh`
refuses to launch if any of them stops passing.
