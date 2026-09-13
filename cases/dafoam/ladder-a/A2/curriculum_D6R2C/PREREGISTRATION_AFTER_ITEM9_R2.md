# Curriculum D6R2C — PRE-REGISTRATION for the SUCCESSOR to Sanaa's AFTER-ITEM 9

**Item id:** `D6R2C-AFTER9-R2`, arm **`FM6`**. Successor to after-item 9, whose arms `FM`, `FM2`, `FM3`,
`FM4` and `FM5` are each closed at **`NOT A RESULT`** and are never re-graded.
**Version 1.0 — DRAFT, NOT YET FROZEN.** Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`.
**This item has burned 0 core-min, started 0 containers and generated 0 meshes at the time of writing.**
**The rule-2 pre-compute condition, checked rather than asserted:** amendments are legal only while this
file has produced no compute, and the test is that its registered run root does not exist. Checked
2026-09-13 by `ls -d`: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER9R2-a2-wing-freshmesh-warmstart`
— `No such file or directory`. **After the freeze commit this file takes dated addenda only.**
It is frozen by the commit that introduces it **together with its three instruments** (§11).
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
**No frozen file is edited** (rule 6): `PREREGISTRATION_AFTER_ITEMS.md` governs `FM5` and is untouched.

**ONE REGISTERED CHANGE.** The fresh-mesh primal is **initialised from `O_mp`'s converged fields at the
same design point, transferred cell-for-cell by index**, instead of from freestream. Nothing else moves:
the mesh, the geometry, the design variables, the solver, the weights, `primalMinResTol` and every
inherited gate stand exactly as they were.

---

## 1. THE RUNG, AND THE EVIDENCE THAT PUT THIS CHANGE ON IT

Sanaa's ladder is **mesh, then numerics, then model, in that order.** This change is on **rung 2**, and
rung 1 was **tested and refuted by measurement**, not skipped.

### 1a. RUNG 1 WAS TESTED — AND THE HYPOTHESIS WAS REFUTED

The hypothesis: the family script's extrusion gave the **fresh** mesh a wall-normal layer growth-ratio
defect. `checkMesh` does not report growth ratio, so it was measured.

**The comparison is exact, not approximate.** `faces.gz`, `owner.gz`, `neighbour.gz` and `boundary` are
**byte-identical** between the fresh mesh, the base, and the warped mesh `O_mp` ran. Only `points.gz`
differs. So the wall-normal marching was built **once** — 1008 chains off the `wing` patch, **every chain
exactly 39 layers**, matching the family script's registered `N = 39` — and evaluated against both point
sets. Same cells, same chains, same code path.

| | **fresh (`FM5`)** | **base (warped by `O_mp`)** |
|---|---|---|
| growth ratio, median | **1.330314** | **1.330151** |
| growth ratio, mean | 1.322246 | 1.322055 |
| growth ratio, max | 1.618285 | 1.618969 — **the fresh mesh's max is LOWER** |
| first-cell height, median | 2.313647e-03 m | 2.336999e-03 m — **the fresh first cell is 1.0 % SMALLER** |

**The medians differ by 0.012 %, the means by 0.014 %.** Per-layer medians track to three decimals
through layers 1–12. **There is no growth-ratio defect in the fresh mesh.**

*(The full distributions, and a second finding about the family's aggressive ~1.33 growth ratio which is
present in BOTH meshes and is therefore a candidate for something else entirely, are in
`FINDING_NOTE_D6R2C_LAYER_GROWTH.md`. **Nothing in that note is registered here and it changes nothing
in this document.**)*

### 1b. AND THE STALL PREDATES THE FRESH MESH ENTIRELY — VERIFIED INDEPENDENTLY

The second, independent reason rung 1 is answered: **the same stall happens on the warped mesh**, which
the extrusion never touched.

- `DEC3` state `S` stalled at `1.0912e-05` on a warped mesh.
- `O_mp`, on the warped mesh: **52 of 87 `F` records carry `fail = 1`**, and its log carries **48**
  `Primal solution failed` signatures.

**THE 48-versus-52 IS REGISTERED AS AN UNRECONCILED INTERVAL, NOT TIDIED.** The four could not be
accounted for cheaply and no clean number is asserted. **The floor — at least 48 primal stalls on the
warped mesh out of 87 evaluations — is what the rung decision rests on and it is not in doubt.**

**A CORRECTION TO THE CLAIM THIS ITEM WAS BRIEFED WITH, MEASURED AND ACCEPTED BY ITS AUTHOR.** The
failures were described as clustering *"preferentially at large `|shape|`"*, from a comparison of group
means (`2.6298` at failures against `2.3313` at successes). **The medians say otherwise —`2.7369` at
successes, HIGHER than the `2.6477` at failures** — and the mean gap is an artefact of four
zero-deformation baseline records sitting in the success group. The failure rate is **not monotone**:

| `max\|shape\|` band | `[0, 1.0)` | `[1.0, 2.0)` | `[2.0, 2.5)` | `[2.5, 3.0)` | `[3.0, ∞)` |
|---|---|---|---|---|---|
| failure rate | **0 %** | 25 % | 75 % | 54 % | 75 % |

**The supportable claim, and the one registered: the stall is ENDEMIC ACROSS THE DEFORMED DESIGN SPACE
and is absent only near zero deformation.** That is weaker than the briefed claim and it is what the
data carries.

### 1c. WHAT RUNG 2 THEREFORE MEANS HERE, AND WHY IT IS NOT THE WITHDRAWN WARM-START HYPOTHESIS

`O_mp`'s 52 failures occurred warm-started **from a different design point**. **This initialises from a
converged solution AT THE SAME DESIGN POINT, on a different mesh.** Those are materially different
starts and the distinction is registered here rather than left to be assumed: the first asks the solver
to travel across design space, the second asks it only to absorb a ~1 % change in cell geometry.

---

## 2. THE ONE CHANGE

### 2a. IT IS AN INDEX TRANSFER, NOT A MAP — AND THE PREMISE IS ASSERTED, NEVER ASSUMED

**MEASURED:** `faces.gz`, `owner.gz`, `neighbour.gz` and `boundary` are byte-identical across **all
three** meshes — the base, the fresh extrusion, and the warped mesh `O_mp` ran:

| file | md5, all three |
|---|---|
| `faces.gz` | `0a94bba01e37c8587676b056c7a2bb05` |
| `owner.gz` | `16febaf5dfa4137ef7fb1ec4a3659ec5` |
| `neighbour.gz` | `803a7546fd09fcbd673ef1ed52b4fcd6` |
| `boundary` | `c8d1891562dc7a1d5822cd6b94c2c2d4` |

Only `points.gz` differs. **Same topology, different geometry.** Cell index `i` is therefore the **same
structured cell** in all three, and the transfer carries **no interpolation error at all** — it removes
an error term instead of disclosing one, and it makes the planted control exact.

**THE PREMISE IS CHECKED ON EVERY RUN, IN TWO PLACES, AND BOTH REFUSE.** `d6r2c_fm6_init.py` hashes the
**destination** (fresh) and **source** (warped) connectivity before it transfers anything and refuses
(`exit 2`, `REFUSE_CONNECTIVITY_MISMATCH`) on any difference — **never degrading to an interpolation**.
`d6r2c_fm6_grade.py` re-checks both at grading under `I1`. A cell-for-cell copy between meshes that do
not share ordering would be meaningless, and that is the one way this change could be silently wrong.

### 2b. THE SOURCE — WHICH FIELDS, AND THE ONE GAP THAT CANNOT BE CLOSED

| fact | value | how established |
|---|---|---|
| the converged primal at this arm's design point | `F` record **`n = 88`, `fail = 0`**, `2026-09-13T04:15:59Z` | `O_mp/d6r2c_evals.jsonl`, md5 `2c0b8143caad198cd2e21d8047986aa3` |
| the last record of **any** kind | `G` record `n = 88`, `fail = 0`, `04:19:07Z` — **an adjoint at the SAME design point** | same file |
| the fields on disk | time `1000`, mtimes `04:19`–`04:20` | `O_mp/mp0{4,5,6}/processor{0..3}/1000/` |

**So the fields are the `n = 88` converged primal, as left after an adjoint ran on top of them at the
same design point.** The adjoint does not advance the primal state; it linearises about it.

**THE GAP, NAMED RATHER THAN ASSERTED AWAY: it cannot be established that the adjoint left `U`, `p`,
`T`, `nut`, `nuTilda` and `alphat` bit-identical, because no reference copy exists.** It is **bounded**
instead of asserted, and the bound is a measurement:

> The transferred field is an **INPUT to the gated quantity, not the gated quantity.** `J_fresh` is
> obtained by converging the fresh-mesh primal to `primalMinResTol = 1.0e-8` **from** that field. The
> influence of a different starting field on a converged objective is bounded by the measured
> path-dependence of this solver class — **`8.764756e-07` absolute in `J`** (`N-D48`) — which is
> **350× INSIDE** the registered band `FM_BAND_ABS = 3.064163144e-04`.

**That number is written into the verdict record, not only into this registration**, so a reader of the
result sees the bound without going hunting.

### 2c. WHAT IS TRANSFERRED, AND WHAT IS NOT

**The transfer set is exactly the volFields the destination case's own `0.orig` carries, MEASURED from
`0.orig` and not assumed:** `T`, `U`, `alphat`, `nuTilda`, `nut`, `p`. A difference between that
directory and this list is a change to the **case**, not to the instrument, and the producer refuses
(`REFUSE_FIELD_SET`) rather than transferring a set nobody registered.

**`phi` IS NOT TRANSFERRED.** It is a `surfaceScalarField`, and reconstructing a face field requires
`faceProcAddressing` with its sign convention. **Registering a transfer this lane has not implemented
would be registering an intention**, so it is excluded and said so.

**THE BOUNDARY CONDITIONS ARE NOT TOUCHED.** The producer takes the destination's **own** `0.orig/<f>`
as the template and replaces **only** its `internalField`; the `boundaryField` and the header survive
byte for byte, and the selftest asserts both. The case definition remains the case definition.

**THE RECORD.** The producer writes **`d6r2c_fm6_init.json`** into the arm directory as it goes, and
`I1` grades that file. Its absence is a refusal (`REFUSE_MISSING_INIT_RECORD`), not a pass: *the one
registered change of this arm leaving no record means there is nothing to grade.*

**HOW THE UNDECOMPOSED FIELD IS ASSEMBLED.** `O_mp`'s fields are decomposed over 4 processors. The
producer reconstructs the undecomposed `internalField` **in-process**, using each processor's own
`cellProcAddressing`, and refuses on a duplicate global index (`REFUSE_ADDR_DUPLICATE`), a hole
(`REFUSE_ADDR_HOLE`) or an out-of-range index (`REFUSE_ADDR_RANGE`). **A partially filled initial field
is not an initial field.** `decomposePar` is then DAFoam's own, from `0/`, exactly as for `FM5` — which
is why the transfer must happen **before** `prob.setup()`: DAFoam reads `0/` at construction, and a field
written after that would never reach the solver. *(That is the shape of producer defect 4, ADDENDUM 4
§A4.1, and the launcher's selftest asserts the phase order to stop it recurring.)*

### 2d. `O_mp` IS OPENED READ-ONLY AND IS NEVER WRITTEN

`O_mp` is a **graded** run directory whose artefacts a closed verdict cites by path. The container mounts
it `:ro`, the producer only reads, and the planted control runs on **synthetic trees in a temporary
directory** — never on `O_mp`.

---

## 3. THE GATES, FROZEN — AND FOR EACH, RE-DERIVED OR INHERITED

Graded by **`d6r2c_fm6_grade.py --item 9R2`**, after the container exits.

| gate | threshold | **re-derived or inherited** |
|---|---|---|
| `I1` the initialisation is what it says it is | exact equalities; no tolerance | **NEW** — §3a |
| `H1` the fresh mesh is the final shape | `SHAPE_MATCH_TOL = 1.0e-8` **and the A4.3 equality** | **INHERITED**, with a **NEW** equality clause — §3b |
| `H2` the mesh is fresh, and from the family script | `GENWINGMESH_MD5 = dab5e959187ab2e2bfb4e2c0ded0feb6`, `BASE_POINTS_MD5 = 0fb1935a9b8781b73ac4ccb136e3ec68`; `checkMesh` recorded, never gated | **INHERITED unchanged** — §3b1 |
| `H3` the band | `FM_BAND_ABS = 3.064163144e-04` | **INHERITED, RE-CHECKED** — §3c |
| `H4` completion and hygiene | cap `47.211` core-min; `primalMinResTol = 1.0e-8` | **INHERITED**, with **NEW** input pins — §3d |
| plant | `PLANT = 1.234e-03` | **INHERITED, re-checked against every band** — §7 |

### 3a. `I1` — NEW. THE ONE REGISTERED CHANGE IS WHAT IT SAYS IT IS

**Every clause is an exact equality. There is no tolerance in `I1`, because there is no error term to
tolerate** — an index copy is exact or it is wrong.

1. The **destination** connectivity equals the four registered md5s of §2a.
2. The **source** connectivity equals them too, for each of `mp04`, `mp05`, `mp06`.
3. The transfer set equals the six registered fields of §2c.
4. Every field covers **all 38,304 cells**.
5. **Every field's read-back difference is exactly `0.0`.** The producer writes each field, **reads it
   back from disk**, and compares. *A value the producer believes it wrote is not evidence that the file
   on disk carries it* — and the grader re-checks the recorded difference rather than trusting it.
6. The source is the **registered converged primal**: `evals_md5` matches, `record_n = 88`, `time = 1000`.

**Any of these failing is `NOT A RESULT`**, with the offending value printed. The grader's selftest
drives **a failing control for each** — including a read-back difference of **one part in 10^18**, which
must flip the label.

### 3b. `H1` — INHERITED, PLUS THE REGISTERED EQUALITY. **AN ANCHOR OUTSIDE THIS RUN**

`SHAPE_MATCH_TOL = 1.0e-8` is **inherited unchanged** from `PREREGISTRATION_AFTER_ITEMS.md` §2c, with its
basis unchanged: coordinates are `O(10)`, round-off through two deformation paths is `O(1e-11)`, and the
physical scale it must catch is `max|s*| = 0.2786` — seven decades above. **No ambiguous middle.**

**NEW, and it is the strongest external anchor in this family.** ADDENDUM 4 §A4.3 registered, before
`FM5` ran, that `H1` must produce **exactly**:

| field | value |
|---|---|
| `n_foam_wall_points` | 1031 |
| `bijective` | true |
| `n_unmatched` | 0 |
| `worst_dist` | **`5.010837892761856e-09`** |

**`H1` depends only on the `DVGeo` deformation and on `O_mp`'s wall points already on disk — it is
INDEPENDENT OF THE FLOW SOLVE — and this solver class is measured bitwise reproducible across
independent cold runs.** So `FM6`'s `H1` block must equal that table **bit for bit**. **This is not a
tolerance; it is an equality**, and any difference at all is a finding, escalated and never absorbed.
A control drives **one ulp** off it — a value still comfortably inside `SHAPE_MATCH_TOL` — and requires
`NOT A RESULT`.

### 3b1. `H2` — INHERITED UNCHANGED, AND ITS TWO PINS STATED

`rc = 0` for the mesh step; **`genWingMesh.py` executed at md5
`dab5e959187ab2e2bfb4e2c0ded0feb6`** and the md5 asserted before it ran; the staged surface md5 printed;
the generated `constant/polyMesh` strictly newer than the arm's age datum; and
**`constant/polyMesh/points.gz` must DIFFER from the base mesh's `0fb1935a9b8781b73ac4ccb136e3ec68`** —
*a "fresh" mesh identical to the base means the deformation never reached the mesher.*

**`checkMesh` OUTPUT IS RECORDED, NOT GATED.** This registration fixes no mesh-quality threshold and
will not invent one after the fact. `checkMesh`'s own trip levels are `checkMesh`'s, not this item's.

### 3c. `H3` — THE BAND, INHERITED AND RE-CHECKED

**`|J_fresh(s*, t*, a*) − Jf| ≤ FM_BAND_ABS = 3.064163144e-04`**, with `Jf = 0.0230632595286777639`,
comparison **(i)**: same DVs including `a*`, **no re-trim**, so the only thing that differs is the mesh.

**Re-checked, not merely copied:** the derivation is `0.01 × J0 = 0.01 × 0.0306416314389976151`, exact
arithmetic on a measured number, and it reproduces. **It remains a DECLARED decision-relevance band —
one percentage point of the headline reduction — and it is NOT a measured discretisation uncertainty and
NOT a GCI.** The grader writes that sentence into every record.

**REPORTED, NEVER GATED, beside `H3`:** per-condition `CD`, `CL` and `CL` miss on the fresh mesh against
the deformed mesh, with one registered finding trigger inherited unchanged —
**`CL_FINDING_TRIGGER = 5.0e-3`**, five times the `G3` tolerance the optimiser was working against
(declared, not measured). Exceeding it is **named in the record as a finding and changes no label**, and
a control asserts that it does not.

**A miss is a `GATE FAIL` on this item and does not invalidate the 24.732 %**, on the reasoning
registered in `PREREGISTRATION_AFTER_ITEMS.md` §2f, carried unchanged: it binds how the headline may be
quoted, and the `J_fresh ≥ 0.90 × J0` case still escalates as a defect against the `O_mp` record.

### 3d. `H4` — COMPLETION AND HYGIENE, INHERITED, PLUS NEW INPUT PINS

`rc = 0`; all three primals converged to `primalMinResTol = 1.0e-8` or their residuals recorded and the
arm graded `NOT A RESULT`; the record newer than the arm's own age datum; **zero** files under the arm
newer than the datum owned by uid 0 or gid 0; uid 1000; the §8 cap not crossed.

**NEW:** the producer's recorded `runscript_md5` must equal **`2f2ae43a627146cf8e0f065b035ada4b`** — the
bytes `O_mp` ran — and its `evals_md5` must equal **`2c0b8143caad198cd2e21d8047986aa3`**. **The staged
inputs must be the registered inputs**, and nothing checked the first of those until this document.

### 3e. THE FLOOR DISCRIMINATOR — REPORTED, NEVER GATED, AND FIXED BEFORE THE RUN

**THE MEASUREMENT THAT MAKES THIS NECESSARY, AND IT CUTS AGAINST THE CHANGE BEING REGISTERED.** `FM5`'s
pressure residual fell 4.5 decades in 300 iterations and then **stopped**:

| iteration | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 |
|---|---|---|---|---|---|---|---|---|
| `p initRes` | 2.242e-05 | 1.3034e-05 | 1.2795e-05 | 1.27849e-05 | 1.27841e-05 | 1.27839e-05 | 1.27838e-05 | **1.278378e-05** |

Over the last 400 iterations it moved by a **relative `8.456e-05`** — the sixth significant figure. At
that rate, reaching `1.0e-8` would take of order **`3.4 × 10^7` iterations**. **This is not a primal that
needs more iterations. It is a primal that has stopped.**

**A converged initial field changes where the solve STARTS, not where the floor IS.** So the registered
change may well be refuted, and the discriminator is fixed **now**:

> If a primal does not converge, its final residual is compared against **`FM5_FLOOR = 1.278377566e-05`**
> — a number from a run this one did not produce. **Within `FLOOR_SAME_REL = 1 %`: the initial field was
> not the obstacle and THE REGISTERED CHANGE IS REFUTED.** Outside it: the stall depends on the starting
> state, so it is not a fixed floor, and that is itself a finding.

**REPORTED, NEVER GATED.** It changes no label — a control asserts that — because it is a diagnosis, not
a threshold. **`primalMinResTol` IS NEVER LOOSENED.** A surviving stall is a finding about this
`DARhoSimpleFoam` configuration at deformation and goes to Sanaa as one.

### 3f. LABELS

`PASS` = `H1 ∧ H2 ∧ H3 ∧ H4 ∧ I1`.
`GATE FAIL` = `H1 ∧ H2 ∧ H4 ∧ I1` hold and `H3` misses, with `J_fresh`, `Jf`, the difference, the band
and the per-condition table printed beside it.
`NOT A RESULT` = `H1`, `H2`, `H4` or `I1` fails, or the §8 cap is crossed.
**No other label and no synonyms** (rule 1). **`H3` is a two-mesh comparison and is NOT a grid
convergence study** — no Roache triple, no GCI, no observed order, at any point (rule 5).

---

## 4. WHICH CLAUSES SEE WHICH FAULTS (L-588, as amended)

L-588 requires that at least one clause compare against a quantity this run did not produce, and — as
amended — that **each clause name the fault class it can see.** `FM5`'s family failed that test: `H1`,
`H2` and `H4` were all self-referential and only `H3` pointed outside.

| clause | anchored to | fault class it CAN see | what CANCELS in it |
|---|---|---|---|
| **`I1`** | **EXTERNAL** — four connectivity md5s and `O_mp`'s md5-pinned record, all fixed before this run | the premise of the transfer failing; a wrong source; a short or corrupted transfer; a read-back difference of one part in 10^18 | anything after the solver starts |
| **`H1`** | **EXTERNAL** — the ADDENDUM 4 §A4.3 equality, registered before `FM5` ran | **PATH faults**: a deformed wall against an undeformed CGNS surface, either way round | **INPUT faults** — a common-mode error in the shared `DVGeo` input moves both sides identically (L-588 as amended) |
| **`H3`** | **EXTERNAL** — `Jf`, md5-pinned | a fresh-mesh drag outside one percentage point of the headline | anything below the band; it is a decision-relevance band, not an accuracy claim |
| **`H4`** | internal **+ two external md5 pins** | completion, ownership, age, cap, an edited runscript, a wrong inherited record | every numerical fault |
| `H2` | internal + the `genWingMesh.py` md5 (**EXTERNAL**) | a mesh that is not fresh, not from the family script, or identical to the base | mesh *quality* — recorded, never gated |

**Four clauses are externally anchored, and `I1` is anchored at exact equality on quantities the flow
solver never touches.** That is the structural property `FM5`'s family lacked.

**AND THE LIMIT OF ALL OF IT, NAMED.** No clause here can see a **common-mode error in `O_mp`'s
converged fields themselves.** If those fields are wrong, `I1` will confirm they were transferred
faithfully and `H3` will compare a wrong answer against the value `O_mp` recorded for it. **The bound on
that is §2b's, not a gate.**

---

## 5. THE ARM

| arm | what it is | ranks | run under this registration? |
|---|---|---|---|
| `FM6` | deform → mesh → **init** → solve, one container, three conditions | 4 | **YES** |

**Run root, NEW and separate:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER9R2-a2-wing-freshmesh-warmstart`

**Why a new root.** The `D6R2C` root holds `O_mp`'s graded artefacts; the `D6R2C-AFTER` root holds five
closed `NOT A RESULT` rows; the `D6R2C-AFTER8R2` root holds the **live** arm `DEC4`. All three are in
`FORBIDDEN_ROOTS` and the launcher's selftest drives `G-ROOT` against them.

**Ranks, placement, hygiene** are inherited unchanged from `PREREGISTRATION_AFTER_ITEMS.md` §5 and §9:
`RANKS = 4`, `CPUSET = 2,3,4,5`, `--memory=20g --memory-swap=20g`, `memory_footprint_gb = 17`,
`--user 1000:1000 --group-add 1002`, `-e HOME=/tmp`, **never root**, image pinned by digest
`sha256:2927768a…f6d35`, `O_mp` mounted `:ro`. **Nothing is stopped by a time or budget cap**
(directive #17): the container prints `D6R2C_FM6_DEADLINE_IN_CONTAINER_S: NONE` and no wrapper carries a
`timeout`.

**BOX PRECONDITION.** `DEC4` is live on the other lane. The launcher's `G-BOX` refuses to **start** if
`load1 > nproc` or swap is in use — **a launch precondition that refuses to start and never stops
anything running.**

---

## 6. THE MONITOR

**None is registered**, for the reason `PREREGISTRATION_AFTER_ITEMS.md` §6 gives and which still holds:
this arm is **primal-only** — no adjoint, no IPOPT, no design iteration — so the item-7 stop rules have
no iterate to act on and no step to halve. A primal that fails to converge is covered by `H4` as a
**completion** gate and by §3e as a **diagnosis**, not as a stop rule.

---

## 7. THE PLANTED CONTROL (rule 3)

`d6r2c_fm6_grade.py` plants **`PLANT = 1.234e-03`** into values it read back from disk and **REFUSES
(`exit 2`)** if any plant leaves the verdict at `PASS`. Five live plants on every real grading: into
`CD_fresh`; into `Jf` as read from the inherited record; into `H1`'s `worst_dist`; and into the recorded
read-back difference of **two different conditions**.

**`PLANT` is inherited and re-checked against every band this document uses:**

| band | value | `PLANT` is |
|---|---|---|
| `FM_BAND_ABS` (the loosest) | `3.064163144e-04` | **4.0×** it |
| `SHAPE_MATCH_TOL` | `1.0e-8` | 5 decades above it |
| `I1`'s read-back clauses | **exact equality** | unbounded — any plant at all is visible |

`d6r2c_fm6_init.py` carries the transfer's own control: it plants into a value, reads it back off disk,
and the selftest asserts the reader **sees** it and sees it **in the right cell**.

**`--selftest` drives 56 grader controls and 24 producer controls, in both directions**, on synthetic
trees in a temporary directory, touching no run directory and never `O_mp`. **A failing control is
driven for every gate**, and the anchors are the literals of this document typed as **assertions, not as
sources** — the defect `PREREGISTRATION_AFTER_ITEM8_R2.md` §8a records, where a control read the constant
it was checking and would have passed for any value.
**Driven at this draft: `D6R2C_FM6_GRADE SELFTEST PASS n=56`, `D6R2C_FM6_INIT SELFTEST PASS n=24`,
`D6R2C_FM6_LAUNCH SELFTEST PASS n=9`, all exit 0.**

---

## 8. COST, IN CORE-MINUTES, BEFORE THE RUN (rule 12)

**Measured anchors, both at 4 ranks:**

| anchor | value | where measured |
|---|---|---|
| `FM5` end to end — container, staging, deform (3 primals on the base mesh), mesh generation, and one fresh-mesh primal run to its 1000-iteration cap | **114 s wall = 7.600 core-min** | the arm's ledger row, `rc = 1` |
| one primal evaluation of all three conditions | 48.081 s → **16.027 s per condition** | `O_mp/d6r2c_evals.jsonl`, `F` record `n = 2` |

| phase | wall s | basis |
|---|---|---|
| everything `FM5` did | **114.000** | **measured**, the ledger row |
| **the init phase — the one registered change** | **90.000** | **ESTIMATE, LABELLED AN ESTIMATE.** Pure-Python reconstruction of 6 volFields × 3 conditions × 38,304 cells. Not measured, because this instrument has never run |
| `cl05` and `cl06`, which `FM5` never reached, at the 1000-iteration cap | **32.054** | 2 × 16.027, the measured per-condition anchor |
| **TOTAL** | **236.054** | |

```
PREDICTION      236.054 s wall × 4 ranks / 60 = 15.737 core-min
REGISTERED CAP (3.00×)                        = 47.211 core-min
```

**Derived dollars:** `15.737 core-min = 0.2623 core-h × $0.0513 = $0.0135`; at the cap, `$0.0404`.
**DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5);
`cost_basis` class **reported-by-owner** at the owner-stated c7a.4xlarge rate.

**THE NUMBER THIS ESTIMATE IS WEAKEST ON, NAMED: the init phase's 90 s.** If the initialisation works,
the three primals converge in far fewer than 1000 iterations and the run comes in **under** the
prediction; if it fails, all three run to the cap and the total is close to it. **Either way the 3.00×
cap is not reachable by this misprediction** — the whole arm is 15.7 core-min against a 47.2 cap, and the
init phase would have to be **eight times** its estimate to cross it. That is stated now rather than
discovered at the ledger.

**THE CAP IS DERIVED IN CODE AND EXISTS IN ONE PLACE.** `d6r2c_fm6_grade.py` carries
`PREDICTION_CORE_MIN = 15.737` and `CAP_FACTOR = 3.00` and computes the cap; the launcher **asks the
grader** for it, after `G-FREEZE` has pinned the grader's bytes. **A cap that exists as a literal in two
files is two things that can drift, and in this item they did** (§8a of the item-8 successor).

**THE CAP REPORTS; NOTHING KILLS ON IT.** A crossing writes `D6R2C_FM6_CAP_CROSSED`, the row is graded
**`NOT A RESULT`**, and **the cap is never raised** (directive #17).

**Calibration row OWED** to `docs/COST_CALIBRATION.md` at this arm's completion — actual against the
15.737 above, the ratio, and contention / waste / misprediction attributed **separately** (rule 12).

---

## 9. THE MESH, THE OBJECTIVE AND THE FLOW REGIME

**38,304 cells**, 40,209 points, all hexahedra, 3 patches — `wing` (wall, 1008 faces), `inout` (patch,
1008 faces), `sym` (symmetry, 1672 faces).

**THE GRADED QUANTITY, STATED IN FULL.** `J` is the **weighted mean drag coefficient**:

```
J = 0.25 × CD04  +  0.50 × CD05  +  0.25 × CD06
targets: cl04 -> CL = 0.400 , cl05 -> CL = 0.500 , cl06 -> CL = 0.600
```

**`WEIGHTS = {0.25, 0.50, 0.25}` is carried unchanged from `PREREGISTRATION.md` §1** — the objective
`O_mp` was optimised against, not this document's to alter. The grader **recomputes `J`** from the
per-condition `CD` and these weights and refuses if the producer's `J` disagrees by more than `1.0e-12`.
*(A registration that does not state the weights of its own objective has not registered its objective —
the third find of the item-8 successor's constant sweep.)*

**THE INHERITED STATE.** `J0 = 0.0306416314389976151` (`n = 2`), `Jf = 0.0230632595286777639` (`n = 88`),
both from `O_mp/d6r2c_evals.jsonl` at md5 `2c0b8143caad198cd2e21d8047986aa3`;
`Jf/J0 = 0.7526772709407745`; the design vector from `O_mp/d6r2c_x0.json` at md5
`b225fe7fdbd12eaa8a9b8a70835849c8`.

**`M∞ = 0.288`, compressible subsonic.** **No shock figure can be produced from any artefact of this
item.** The run root does not carry the word "transonic".

---

## 10. WHAT THIS ITEM DOES NOT CLAIM

- **It does not re-grade `O_mp`.** Closed at **`GATE FAIL`**: 24.732273 %, the `G3` miss of 2.79×,
  `Jf/J0 = 0.7526772709407745`, on the runscript this item pins unchanged.
- **It does not re-grade `FM`, `FM2`, `FM3`, `FM4`, `FM5`, `DEC`, `DEC2` or `DEC3`.** Eight closed
  `NOT A RESULT` rows, never re-seeded.
- **It does not claim the change will work.** §3e registers, with its arithmetic, that `FM5`'s primal was
  on a **floor**, and that a converged initial field changes where a solve starts and not where a floor
  is. **The discriminator for that outcome is fixed before the run.**
- **It does not touch `primalMinResTol`.** Not to make a stall pass, not at all.
- **It does not claim the transferred fields are bit-identical to the `n = 88` primal.** §2b names that
  gap and bounds it at 350× inside the band.
- **It does not transfer `phi`.** §2c.
- **It is not a grid study.** Single nominal resolution; no Roache triple, no GCI, no observed order.
- **It does not verify any gradient.** Not one adjoint is solved.
- **It does not claim the layer growth ratio causes anything.** That is a candidate in a separate
  finding note and is **not registered here**.
- **It does not satisfy Sanaa's item 10.** The report is a separate record.

---

## 11. THE FROZEN INSTRUMENTS

**Every instrument this document names EXISTS, is in THIS COMMIT, and carries its md5 below.** The list
is closed: **these are every instrument named anywhere in this document.**

| file | role | md5 at freeze | selftest driven at freeze |
|---|---|---|---|
| `d6r2c_fm6_grade.py` | **THE GRADING PATH** — `I1`, `H1`–`H4`, the floor discriminator, the planted controls, and `--print-cap`, the cap's single source | `1a5ca51f8dab59e3c72b9a71ce8f77e6` | **`D6R2C_FM6_GRADE SELFTEST PASS n=56`** |
| `d6r2c_fm6_init.py` | **THE ONE REGISTERED CHANGE** — the index transfer, in-container | `0d335d95aa294a96fb8df106e71b8970` | **`D6R2C_FM6_INIT SELFTEST PASS n=24`** |
| `d6r2c_fm6_run_arm.sh` | the launcher: `G-ROOT`, `G-BOX`, `G-FREEZE`, `G-COLD`, digest pin, age datum, ledger, rotator. **Carries no cap of its own** | `3a88ba1112ebe0996ed96ff43ed0f03c` | **`D6R2C_FM6_LAUNCH SELFTEST PASS n=9`** |

**AND ONE INSTRUMENT REUSED UNCHANGED, WHICH IS ITSELF THE EVIDENCE THAT NOTHING ELSE MOVED:**

| file | role | md5 — **UNCHANGED, the bytes that ran `FM5`** |
|---|---|---|
| `d6r2c_freshmesh.py` | phases `deform`, `mesh`, `solve` | **`1d15ce361673ca600d565280441b67e0`** |
| `d6r2c_opt_runScript.py` | the frozen model | **`2f2ae43a627146cf8e0f065b035ada4b`** |

**The new files are forks and their parents stay on disk unedited:** `d6r2c_fm6_grade.py` from
`d6r2c_after_grade.py` (`6c22013af54569ae651f8f23d1088861`), `d6r2c_fm6_run_arm.sh` from
`d6r2c_after_run_arm.sh` at its **committed blob** `c4433db6b60f9c695d785a871a6d3c7d` (commit
`ab9fdec231567eb3acfeffdac6903ae290d147cb`). `d6r2c_fm6_init.py` is new.

**Every threshold in the grader is copied verbatim from this document, each carrying the sentence it was
copied from as its comment. Nothing in the grader was chosen by its author — AND THAT SENTENCE IS
CHECKED RATHER THAN ASSERTED:** §12's constant sweep compares all of them, match and mismatch alike.

### 11a. THE HONEST GAP IN THIS FREEZE

**`d6r2c_fm6_init.py` HAS NEVER BEEN EXECUTED AGAINST A REAL DECOMPOSED CASE.** What is driven at the
freeze is `--selftest`: the reconstruction against a synthetic two-processor decomposition with
**deliberately non-contiguous, non-sorted** addressing, every refusal path, the header and
`boundaryField` preservation, and — the one control anchored **outside** the instrument — the premise
assertion run against the **real fresh mesh on this box**, which must pass.

**Specifically untested:** that the six reconstructed fields are accepted by DAFoam's own `decomposePar`
at `prob.setup()` and reach the solver. **L-589 applies:** the synthetic control cannot bear on that and
does not claim to.

> **Registered in advance: if `FM6` reaches the solve phase and its first-iteration residuals are
> indistinguishable from a freestream start, the transfer did not reach the solver. That is a PRODUCER
> DEFECT — stopped, graded `NOT A RESULT`, repaired under `VERIFICATION_CHARTER` §2d.1. The grading path
> `d6r2c_fm6_grade.py` is NOT touched by such a repair, and if it ever must be, that is a new
> registration.**

**A producer defect is a defect in how a number was made and is repairable with disclosure; a grader
changed after seeing data is not.**

---

## 12. THE CONSTANT SWEEP — THE STANDING PRE-FREEZE CHECK

`PREREGISTRATION_AFTER_ITEM8_R2.md` §8c makes this a standing check for this item: **before any freeze,
every constant in every named instrument is compared against the value the registration states for it,
and the comparison is reported in full, matches included.** A sweep that lists only its failures cannot
be told apart from a sweep that was never run.

**The sweep for this document was driven at this draft and its result is in §12a, every row.**

### 12a. THE SWEEP, EVERY ROW

**34 rows. 34 OK. 0 mismatches.** Where a constant lives in **both** instruments (`PLANT`, `N_CELLS`,
`EVALS_MD5`, `TRANSFER_SET`, `RUN_DIRS`) the two agree with each other as well as with this text.

| # | constant | value | in both instruments? |
|---|---|---|---|
| 1 | `SHAPE_MATCH_TOL` | `1.0e-8` | grader |
| 2 | `FM_BAND_ABS` | `3.064163144e-04` | grader |
| 3 | `G2_BAR_ON_J0` | `0.90` | grader |
| 4 | `CL_FINDING_TRIGGER` | `5.0e-3` | grader |
| 5 | `PLANT` | `1.234e-03` | **both** |
| 6 | `PREDICTION_CORE_MIN` | `15.737` | grader |
| 7 | `CAP_FACTOR` | `3.00` | grader |
| 8 | `CAPS["FM6"]` | `47.211` — **derived, not typed** | grader |
| 9 | `PRIMAL_MIN_RES_TOL` | `1.0e-8` | grader |
| 10 | `FM5_FLOOR` | `1.278377566e-05` | grader |
| 11 | `FLOOR_SAME_REL` | `0.01` | grader |
| 12 | `N_CELLS` | `38304` | **both** |
| 13 | `RUNSCRIPT_MD5` | `2f2ae43a627146cf8e0f065b035ada4b` | grader |
| 14 | `EVALS_MD5` | `2c0b8143caad198cd2e21d8047986aa3` | **both** |
| 15 | `X0_MD5` | `b225fe7fdbd12eaa8a9b8a70835849c8` | grader |
| 16 | `BASE_POINTS_MD5` | `0fb1935a9b8781b73ac4ccb136e3ec68` | grader |
| 17 | `GENWINGMESH_MD5` | `dab5e959187ab2e2bfb4e2c0ded0feb6` | grader |
| 18 | `J0_INHERITED` | `0.0306416314389976151` | grader |
| 19 | `JF_INHERITED` | `0.0230632595286777639` | grader |
| 20 | `SOURCE_TIME` | `"1000"` | producer |
| 21 | `SOURCE_RECORD_N` | `88` | producer |
| 22 | `WEIGHTS` | `0.25 / 0.50 / 0.25` | grader |
| 23 | `CL_TARGETS` | `0.4 / 0.5 / 0.6` | grader |
| 24 | `H1_REGISTERED["worst_dist"]` | `5.010837892761856e-09` | grader |
| 25 | `H1_REGISTERED["n_foam_wall_points"]` | `1031` | grader |
| 26–29 | `CONNECTIVITY_MD5` × 4 | §2a's four hashes | grader (producer carries its own copy under the same name) |
| 30 | `TRANSFER_SET` | `T U alphat nuTilda nut p` | **both** |
| 31 | `RUN_DIRS` | `mp04 mp05 mp06` | **both** |
| 32 | `RECORD` | `d6r2c_fm6_init.json` | producer |
| 33 | the reused producer's pin | `1d15ce361673ca600d565280441b67e0` | launcher |
| 34 | **a cap literal in the launcher** | **must NOT exist** — confirmed absent | launcher |

**FOUR ROWS FAILED ON THE FIRST PASS AND ALL FOUR WERE GAPS IN THIS DOCUMENT, NOT IN THE INSTRUMENTS.**
`CL_FINDING_TRIGGER`, `BASE_POINTS_MD5`, `GENWINGMESH_MD5` and the init record's filename were carried by
the instruments and stated **nowhere** in the text, so a reader could not have checked those literals
against anything. They are now in §3b1, §3c and §2c. **That is the fourth time this check has paid for
itself in this item**, and it is the reason it is standing rather than optional.

---

## ADDENDUM 1 — 2026-09-13 — `FM6` DIED ON A DEPENDENCY ITS LAUNCHER DID NOT STAGE, AND THE PIN DID NOT COVER IT

**This addendum carries the document to version 1.1.** The version line above still reads `Version 1.0`
and is **deliberately not edited**: editing it would falsify this section's own append-only assertion.
The version of record is the one stated here.

**Lines whose number changed above this section: 0.** Proof in §A1.7, derived from the committed blob.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** `I1`, `H1`–`H4`,
`SHAPE_MATCH_TOL`, `FM_BAND_ABS`, `GENWINGMESH_MD5`, `BASE_POINTS_MD5`, `CL_FINDING_TRIGGER`,
`PLANT`, `FM5_FLOOR`, `FLOOR_SAME_REL`, `PRIMAL_MIN_RES_TOL`, the weights, and the cap of §8 stand
exactly as frozen at `e52e09316844f92ee683ec200a047a59e2a44b75`.
**THE GRADING PATH `d6r2c_fm6_grade.py` IS NOT TOUCHED BY THIS ADDENDUM AND ITS md5 IS UNCHANGED.**

### A1.0 WHAT HAPPENED

Arm `FM6` was launched 2026-09-13T08:00:57Z under the frozen launcher, container
`d6r2c_fm6_FM6_20260913T080057Z_1427681`, 4 ranks, uid 1000:1000+1002, cpuset 2,3,4,5. **All five launch
guards passed** — `G_ROOT`, `G_BOX` (`load1=38.19 nproc=96 solver_swap_offenders=0 avail_gb=556`),
`G_FREEZE`, the cap read from the grader at `47.211`, and `G_COLD` (age datum `1789286457`).

**It died after 23 s wall, rc = 1, 1.533 core-min, before one primal and before any phase completed.**
All four ranks raised the identical error:

```
File "/mnt/FM6/d6r2c_freshmesh.py", line 67, in <module>
    from d6r2c_decomp import (Refusal, load_frozen_model, read_final_dv, ...)
ModuleNotFoundError: No module named 'd6r2c_decomp'
```

**The arm is graded `NOT A RESULT`** — `d6r2c_fm6_grade.py` refused with
`REFUSE_MISSING_FRESHMESH_RECORD`, which is §11a's registered contingency operating exactly as
registered. That row is closed, is never re-graded and is never overwritten. Its evidence —
`FM6/`, `FM6_20260913T080057Z_1427681.log` and the ledger row — stays on disk.

### A1.1 THE DEFECT — A PIN PROVES WHAT A FILE **IS**, NOT WHAT IT **NEEDS**

`d6r2c_freshmesh.py` — the producer this document **reuses unchanged**, and whose pin §11 calls *"itself
the evidence that nothing else moved"* — **imports `d6r2c_decomp` as a library** at its line 67. The
parent launcher both **pins** it (`d6r2c_after_run_arm.sh:128`) and **stages** it (`:219`), which is why
`FM5` reached a stalled primal and `FM6` reached no phase at all.

This launcher's `seed_arm` staged **three** files where **four** are needed:

```
cp "$SRC/d6r2c_opt_runScript.py" "$SRC/d6r2c_freshmesh.py" "$SRC/d6r2c_fm6_init.py" "$WORK/"
```

`d6r2c_decomp.py` was dropped **deliberately**, on the reasoning that item 8 is not registered by this
document. **That reasoning was about the DOCUMENT, and the dependency is about the CODE.** Those are
different questions and only one of them is answerable by reading a registration.

> **THE PIN WAS HONEST ABOUT THE BYTES AND SILENT ABOUT THE ENVIRONMENT THOSE BYTES REQUIRE.**
> `d6r2c_freshmesh.py` was staged at exactly its frozen md5 `1d15ce361673ca600d565280441b67e0`,
> `G-FREEZE` passed on it, and the arm was unrunnable. **A hash proves identity, not sufficiency.**

**It is a LAUNCHER defect: a defect in how a number would have been made.** It is repairable with
disclosure under `VERIFICATION_CHARTER` §2d.1. **A grader changed after seeing data is not**, and the
grader is not changed.

### A1.2 THE REPAIR

1. **`d6r2c_decomp.py` is STAGED and PINNED** at `42ec0dd582584812a69129a474b2783e` — the md5 the
   parent launcher pins and the **exact bytes `FM5` ran with**, verified on disk. **Staging an unpinned
   file into a frozen arm would be worse than the defect it repairs.** It is a **library dependency of a
   reused producer, not a new instrument**: it introduces no gate, no threshold, no cap and no label.
2. **The staged list has ONE source**, the shell variable `STAGED_PY`, read by **both** `seed_arm` and
   the new `G-DEPS`. The canonical list is referenced, never re-spelled (L-221/L-222).
3. **`G-DEPS` — NEW, and it is the part that outlasts this item.** Every local module imported by a
   staged `.py` must itself be staged. It parses the real files with `ast`, treats a module as *local*
   only if a file of that name sits in `SRC` (an image module is not this launcher's to vouch for), and
   **refuses (exit 4) naming the file and the module it needs.**

### A1.3 THE FAILING CONTROL, WHICH IS WHAT MAKES `G-DEPS` A CHECK

`guard_deps` takes the staged list **as arguments**, so the selftest drives it with
`d6r2c_decomp.py` removed — **the exact set that killed `FM6`** — and **requires it to FAIL**, and
requires it to **name** the missing module rather than merely return non-zero. **A check that cannot be
seen to fail is not a check** — the lesson this item's cap controls taught at
`PREREGISTRATION_AFTER_ITEM8_R2.md` §8a, applied to a new clause.

**A defect was found in that control by driving it, and is recorded rather than quietly fixed.** The
first draft piped `guard_deps` into `grep -q`. `set -o pipefail` is active, so a pipeline ending in a
successful `grep` still returns the **deliberately failing** command's non-zero status, and the control
reported a failure that had not happened. The output is now **captured first and matched after**.

### A1.4 `FM7` — THE RE-RUN ID, CARRYING THE IDENTICAL REGISTERED CAP

**`FM7` carries the IDENTICAL registered figure of `47.211` core-min** — the same number looked up
under another key. **No threshold is invented, raised or reduced.**

**And the cap still has ONE source.** The grader is **not** edited to learn a new arm id — its pin must
not move — so `cap_core_min()` asks it for the **item's** cap under the canonical key `FM6` and applies
it to whichever registered arm runs. **The cap is a property of the item, not of the arm id.** The
launcher's selftest asserts `cap_core_min FM7 == cap_core_min FM6 == 47.211`, because a lesson is not
applied until every call site asserts it.

**`FM6` keeps its directory and its `NOT A RESULT` row, is never re-seeded (`G-COLD` refuses a case
where `0` or a time directory already exists) and is never re-graded.**

### A1.5 A CONSEQUENCE OF THE FROZEN GRADER, DISCLOSED RATHER THAN REPAIRED

`d6r2c_fm6_grade.py` writes `"arm": "FM6"` as a **literal**. Grading the `FM7` arm will therefore
produce a record whose `arm` field reads `FM6`. **The grader is NOT edited to fix this**, because its
pin must not move and a cosmetic field is not worth reopening a grading path for.
**The authoritative arm identity is the ledger row and the arm directory path**, both of which carry
`FM7`. Disclosed here so no later reader mistakes the literal for the arm that ran.

### A1.6 SPEND — DEFECT-ATTRIBUTABLE WASTE, NAMED SEPARATELY AND NEVER ABSORBED

| category | core-min | note |
|---|---|---|
| `FM6` | **1.533** | `NOT A RESULT`. **DEFECT-ATTRIBUTABLE WASTE** — a launcher defect, not a falsified assumption |

**It is NOT in the same class as `DEC3`'s 63.000 or `FM5`'s 7.600**, both of which bought measurements:
`DEC3` falsified §1a's shape-only trimmability assumption, and `FM5` produced the residual floor that
§3e's discriminator is built on. **`FM6` bought nothing but the knowledge that I mis-staged a file.**
`1.533 core-min = /bin/bash.0013`, **derived, not measured**; `cost_basis` class **reported-by-owner**.

**The §8 prediction of 15.737 core-min and the cap of 47.211 are UNCHANGED** and are not adjusted to
absorb this. **No calibration row is owed: no arm has completed.**

### A1.7 THE APPEND-ONLY PROOF

- Pre-append state, read from the **committed blob** at `e52e09316844f92ee683ec200a047a59e2a44b75`, in
  the same shell invocation as the append: md5 **`cf8ded9648795176ec5729fc899f5ecf`**, **587 lines**.
- The working-tree file was **byte-identical to that blob** before this section was appended — asserted
  in that same invocation, so the append is provably the first change since the freeze.
- `git diff --numstat` on this path must show **insertions only and `0` deletions**.
- **Lines whose number changed above this section: 0.**
- This is `ADDENDUM 1`, the number derived from the maximum existing heading, never a count.

### A1.8 WHAT THIS ADDENDUM DOES NOT DO

- **It does not re-grade `FM6`.** `NOT A RESULT`, closed, never re-seeded.
- **It does not touch the grading path.** `d6r2c_fm6_grade.py` is unchanged and its pin is unmoved.
- **It does not alter a gate, a threshold, a cap or a label**, and it does not move the §8 prediction.
- **It does not claim `FM7` will pass.** §3e's discriminator stands exactly as frozen, and the
  expectation on the record — that a converged initial field may not move a residual floor — is unchanged.
- **It does not touch `primalMinResTol`.**
- **It does not register the layer-growth candidate.** That stays a finding note.

### A1.9 SECTION 11 — THE INSTRUMENT TABLE, REPINNED

**Only the launcher changed.** §11's table above is not edited — that would falsify §A1.7 — so the
current state of record is here:

| file | md5 now | selftest |
|---|---|---|
| `d6r2c_fm6_grade.py` | `1a5ca51f8dab59e3c72b9a71ce8f77e6` — **UNCHANGED SINCE THE FREEZE** | `PASS n=56` |
| `d6r2c_fm6_init.py` | `0d335d95aa294a96fb8df106e71b8970` — **UNCHANGED SINCE THE FREEZE** | `PASS n=24` |
| `d6r2c_fm6_run_arm.sh` | `bac46645b4b23da5eb7d8a55c70fdf1c` — repaired by this addendum | `PASS n=14` (was `n=9`) |
| `d6r2c_freshmesh.py` | `1d15ce361673ca600d565280441b67e0` — **REUSED UNCHANGED**, the bytes `FM5` ran | — |
| `d6r2c_decomp.py` | `42ec0dd582584812a69129a474b2783e` — **NEWLY STAGED AND PINNED** (§A1.2) | `PASS n=32` |

**The launcher's five checks gained five more**, all of them driven: `G-DEPS` on the registered set;
`G-DEPS` **failing** on the exact set that killed `FM6`; `G-DEPS` **naming** the missing module;
`FM7` carrying the identical cap; and the staged list having one source read by both the copy and the
check.

**`d6r2c_decomp.py` IS A LIBRARY DEPENDENCY, NOT A NEW INSTRUMENT.** It is listed here because it is now
staged and pinned and a reader is entitled to its hash, **not** because this document registers item 8.
Its `--selftest` is driven and reported for the same reason. **It introduces no gate, no threshold, no
cap and no label**, and `d6r2c_fm6_grade.py` neither imports it nor reads anything it writes.

---

## ADDENDUM 2 — 2026-09-13 — THE `arm` FIELD IS **WRONG** FOR `FM7`, AND TWO IDENTIFIERS THAT ARE NOT

**This addendum carries the document to version 1.2.** Earlier version lines are **deliberately not
edited**, for the reason `ADDENDUM 1` gives.

**Lines whose number changed above this section: 0.** Proof in §A2.3.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL**, and **does not touch the grading
path**, whose md5 `1a5ca51f8dab59e3c72b9a71ce8f77e6` is unchanged **across both freezes**
(`e52e09316844f92ee683ec200a047a59e2a44b75` and `12d27323fc6580b0c7e3f2d6c98c1b853d0fef05`).

### A2.0 THE CORRECTION TO `ADDENDUM 1` §A1.5 — STRONGER WORDING, RULED BY THE SUPERVISOR

§A1.5 said the `arm` field is "not authoritative". **That is too soft and it is corrected here, in the
words the supervisor ruled:**

> **WHEN `FM7` IS GRADED, THE `arm` FIELD IN `d6r2c_fm6_grade.py`'s OUTPUT WILL READ `"FM6"` AND THAT
> VALUE IS WRONG.** It is a frozen literal in a grading path that must not move. It is not a synonym,
> not an alias and not a label whose meaning depends on context. **It is wrong.**

*"Not authoritative"* is phrasing a reader skims past; *"this field is wrong"* is phrasing that stops
them. **Three separate numbers were misread tonight because they meant something other than what they
appeared to mean**, and this is that shape exactly.

**The grader is NOT edited, and that ruling stands:** rule 2's protection of the grading path is worth
more than a correct string; **no gate reads that field**; and editing an instrument carrying 56 driven
controls to repair a cosmetic literal trades a real risk for a presentational one.

### A2.1 THE MITIGATION IS STRUCTURAL, NOT NARRATIVE — TWO IDENTIFIERS CARRY `FM7`

A disclosure a reader must find is not a mitigation. **Two independent identifiers, produced by two
different instruments, will carry `FM7`, against the one frozen literal that carries `FM6`:**

| identifier | value for this arm | produced by |
|---|---|---|
| the ledger row | `D6R2C_FM6_ROW arm=FM7 …` | `d6r2c_fm6_run_arm.sh:517`, from `$ARM` |
| **the grade record's filename** | `AFTER_ITEM9R2_FM7_GRADE.json` | the `--out` path, **registered below** |
| the `arm` field inside that record | `"FM6"` — **WRONG** | a frozen literal |

**THE GRADING INVOCATION IS REGISTERED HERE, BEFORE THE ARM RUNS**, so the filename is not a choice made
after seeing a verdict. `d6r2c_fm6_grade.py`'s `--out` default is `AFTER_ITEM9R2_GRADE.json`, which
carries no arm id at all; **the `FM7` grading MUST pass `--out` explicitly:**

```
--out <run root>/AFTER_ITEM9R2_FM7_GRADE.json
```

**Two out of three identifiers say `FM7`, and the third is documented as wrong.** A reader who checks
any two of them cannot be misled by the one that is.

### A2.2 WHY THE DESIGN RULE BEHIND `G-DEPS` IS RECORDED, NOT JUST THE GUARD

`guard_deps` takes the staged list **as arguments** rather than reading `$STAGED_PY` from the
environment. That is **the only reason its failing control is possible at all**: a guard that reads its
inputs from globals can be driven only against the one set the globals hold, so **it can be shown to
pass and can never be shown to fail.**

**Registered as a design rule for this item's instruments:** *a guard that cannot be handed a bad input
cannot be driven against one.* It sits beside the three instruments that measured themselves and
reported success tonight — cap controls that read their own constant, a phase check that matched its own
grep lines, and a dependency control masked by `pipefail`.

### A2.3 THE APPEND-ONLY PROOF

- Pre-append state, read from the **committed blob** at `12d27323fc6580b0c7e3f2d6c98c1b853d0fef05`, in
  the same shell invocation as the append: md5 **`063bef11051f6fd00bfc688f7dd39e7f`**, **754 lines**.
- The working-tree file was **byte-identical to that blob** before this section was appended, asserted in
  that same invocation.
- `git diff --numstat` on this path must show **insertions only and `0` deletions**.
- **Lines whose number changed above this section: 0.**
- This is `ADDENDUM 2`, the number derived from the maximum existing heading, never a count.

### A2.4 WHAT THIS ADDENDUM DOES NOT DO

- **It does not touch the grading path**, its md5, or any threshold, cap, gate or label.
- **It does not re-grade `FM6`.** `NOT A RESULT`, closed.
- **It does not change what `FM7` runs** — only the `--out` path the grading is invoked with.
- **It does not claim `FM7` will pass.** §3e's discriminator stands exactly as frozen.

---

## ADDENDUM 3 — 2026-09-13 — `FM7` TRANSFERRED THE FIELD CORRECTLY AND THE SOLVER NEVER SAW IT

**This addendum carries the document to version 1.3.** Earlier version lines are **deliberately not
edited**, for the reason `ADDENDUM 1` gives.
**Lines whose number changed above this section: 0.** Proof in §A3.6.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL**, and **does not touch the grading
path**, whose md5 `1a5ca51f8dab59e3c72b9a71ce8f77e6` is unchanged since the first freeze.

### A3.0 THE RESULT THAT LOOKS LIKE A REFUTATION AND IS NOT ONE

**`FM7` reached the solve phase and stalled at `Primal min residual 1.278377566e-05` — identical to
`FM5` to all ten significant digits.** §3e's discriminator, read alone, says *"SAME FLOOR AS FM5 — the
initial field was not the obstacle and the registered change is REFUTED"*.

> **THAT READING IS WRONG, AND IT IS THE MOST IMPORTANT SENTENCE IN THIS DOCUMENT:
> YOU CANNOT REFUTE A CHANGE THAT DID NOT TAKE EFFECT.**

**The transfer never reached the solver, so the rung-2 hypothesis is UNTESTED, not refuted.** Had §3e
stood alone, a clean refutation would have been recorded and the ladder would have climbed to the model
rung **on false evidence**. **A discriminator that can return "refuted" must be accompanied by a check
that the change occurred at all** — §11a was that check, and it is why this was caught.

### A3.1 THE EVIDENCE, IN THREE INDEPENDENT LINES

1. **The transfer itself was correct.** `d6r2c_fm6_init.json`: all six fields, **38,304 cells each**,
   `readback_worst_abs_diff = 0.0` in every field of every condition, connectivity premise held.
   `mp04/0/p` carries 38,304 nonuniform values beginning `105669.7255, 104525.1293, 103394.0378` —
   `O_mp`'s converged pressure. **`I1` would have passed.**
2. **The fields the solver read were freestream.** `mp04/processor0/0/`: `U` is
   `internalField uniform (100 0 0)`, `p` is `uniform 101325`, `T` is `uniform 300`, `nuTilda` is
   `uniform 4.5e-05` — at **455–628 bytes**, where a decomposed 9,504-cell nonuniform field is 50–190 kB.
3. **The whole residual trajectory is bit-identical to `FM5`'s from the first iterate** —
   `t=100: 0.001103361217`, `t=200: 1.836762e-04`, `t=300: 2.242450e-05`, floor `1.278377566e-05`.
   **An identical trajectory from iteration 1 means an identical initial state.**

### A3.2 THE MECHANISM, FROM THE MTIMES

`processor0/constant/polyMesh` written **08:11:48** — the **deform** phase decomposed. `init` wrote the
undecomposed `0/` at **08:12:50**. The solve phase's processor fields date from **08:12:58–08:13:01** and
are still uniform. **DAFoam decomposes ONCE; at the solve phase `processorN/` already exists and is what
the solver reads.**

**§2c said *"the transfer must happen before `prob.setup()`, because DAFoam reads `0/` at
construction"*. That was right about the constraint and wrong about WHICH `setup()`** — the deform
phase's, which runs one phase earlier. **A true sentence pointing at the wrong instance of the thing it
describes.**

### A3.3 THE REPAIR — WRITE WHERE THE SOLVER READS

`distribute_internal()` writes each `mp0X/processorN/0/<field>` by **the exact inverse of the map the
producer already uses**: cell `g` of the global array becomes local cell `k` of processor `n`, where
`addr[k] == g`, through the **same** `cellProcAddressing`. **No interpolation.**

**The template is each processor's OWN `0/<field>`**, because it carries the inter-processor boundary
patches the undecomposed file does not have; splicing into an undecomposed template would produce a file
OpenFOAM cannot read. Only the `internalField` is replaced, and a control asserts the `boundaryField`
survives byte for byte.

**The rejected alternative, recorded with its reason:** deleting `processorN/` to force a
re-decomposition rests on behaviour evidenced only by a clean-tree case, and throws away a mesh
decomposition to move a field. **Not done.**

### A3.4 TWO REFUSALS — AND NEITHER IS A GATE

**§11a already registers this condition in words** — *"if its first-iteration residuals are
indistinguishable from a freestream start, the transfer did not reach the solver … a PRODUCER DEFECT,
stopped, graded `NOT A RESULT`"*. **These make a registered condition executable. No condition is
added, no threshold is moved, no verdict is written and no label is assigned** (`VERIFICATION_CHARTER`
§2d.1; the sibling registration's `D5` is likewise *"a refusal, not a gate"*).

- **REFUSAL 1 — THE PRECONDITION, in `--phase init`, BEFORE the solve.** Every
  `processorN/0/<field>` is **read back from disk** and compared against the slice it was built from;
  anything but exactly `0.0` refuses. **Seconds, against `FM7`'s 7.533 core-min.** A post-mortem
  becomes a precondition.
- **REFUSAL 2 — THE SECOND LINE, `--phase verify`**, run by the launcher as `G-VERIFY` after the arm
  exits. If the solve-phase `t=100` residual equals **`1.103361217e-03`** or the floor equals
  **`1.278377566e-05`**, **bit for bit**, it refuses. **Both anchors come from runs the next arm did not
  produce.** The test is **equality, not proximity** — a control drives one ulp off each and requires it
  **not** to fire, so a genuinely different run is never blocked by it.

### A3.5 THE ROUND-TRIP IDENTITY, AND `FM8`

**`reconstruct → distribute → reconstruct` must return the IDENTICAL array**, for scalars and vectors,
against a deliberately non-contiguous, non-sorted two-processor addressing. If that holds the two maps
are exact inverses and the transfer carries no error at all. Driven at this freeze.

**`FM8` is the re-run id and carries the IDENTICAL registered cap of `47.211`** — the same number under
another key, asserted by the launcher's selftest. **`FM6` and `FM7` keep their directories and their
`NOT A RESULT` rows, are never re-seeded and are never re-graded.**

### A3.5a A CORROBORATION NOBODY WENT LOOKING FOR

**`FM5` and `FM7` are two independent cold runs on SEPARATELY EXTRUDED MESHES, and their residual
trajectories agree to every printed digit.** That is `N-D48`'s bitwise run-to-run floor appearing
unlooked-for on a third pair. **It was not the point of either run**, which is what makes it good
evidence rather than a number someone went hunting for.

### A3.6 THE APPEND-ONLY PROOF, AND A DISCLOSURE ABOUT ITS BASELINE

- Pre-append state of the **working-tree file**, read in the same shell invocation as the append:
  md5 **`c1264f1c66675a0ec191357389a09a4f`**, **835 lines**.
- `git diff --numstat` on this path must show **insertions only and `0` deletions**. *(No count is
  asserted: a concurrent commit landing during a `git diff` makes the number read against a stale
  baseline — measured on `ADDENDUM 2`, which read `248` against a moving `HEAD` and `81` against the
  explicit commit. **A proof written to be true rather than to be precise survives that.**)*
- **THE BASELINE IS THE WORKING TREE, NOT `HEAD`, AND HERE IS WHY — DISCLOSED RATHER THAN GLOSSED.**
  **`ADDENDUM 2` IS ON DISK AND WAS NEVER COMMITTED.** The last freeze of this document is
  `12d27323fc6580b0c7e3f2d6c98c1b853d0fef05` (blob `063bef11051f6fd00bfc688f7dd39e7f`); `HEAD` has since advanced on other
  teams' work and still does not carry `ADDENDUM 2`. **`FM7` therefore ran with `ADDENDUM 2`
  uncommitted.** That addendum altered **no gate, threshold, cap or label** — it corrected wording and
  registered the `--out` filename for grading — so **nothing that governed `FM7` was unfrozen**, and the
  registration `FM7` ran under was committed. **But the discipline is freeze-by-commit before compute,
  and this fell short of it. It is recorded here rather than left for someone to find in a diff.**
- **Lines whose number changed above this section: 0.**
- This is `ADDENDUM 3`, the number derived from the maximum existing heading, never a count.

### A3.7 THE INSTRUMENT TABLE

| file | md5 now | selftest |
|---|---|---|
| `d6r2c_fm6_grade.py` | `1a5ca51f8dab59e3c72b9a71ce8f77e6` — **UNCHANGED SINCE THE FIRST FREEZE** | `PASS n=56` |
| `d6r2c_fm6_init.py` | `75bf53d8e798980332ef8dfdcc25b0c6` — the distributor and both refusals | `PASS n=39` (was `n=24`) |
| `d6r2c_fm6_run_arm.sh` | `cead1008eeb4d151c0ccddae2653d64b` — `G-VERIFY` and `FM8` | `PASS n=17` (was `n=14`) |
| `d6r2c_freshmesh.py` | `1d15ce361673ca600d565280441b67e0` — **REUSED UNCHANGED** | — |
| `d6r2c_decomp.py` | `42ec0dd582584812a69129a474b2783e` — staged library dependency | `PASS n=32` |

### A3.8 SPEND

`FM7`: **7.533 core-min**, `NOT A RESULT`, **DEFECT-ATTRIBUTABLE WASTE**. Running total on this item:
**9.066 core-min** across `FM6` and `FM7`. **Neither is in the class of `DEC3`'s 63.000 or `FM5`'s
7.600**, which bought measurements. The §8 prediction of `15.737` and the cap of `47.211` are
**UNCHANGED and are not adjusted to absorb it.**

### A3.9 WHAT THIS ADDENDUM DOES NOT DO

- **It does not re-grade `FM6` or `FM7`.** Both `NOT A RESULT`, closed.
- **It does not touch the grading path, any gate, threshold, cap or label.**
- **It does not claim the rung-2 hypothesis is refuted.** It claims the opposite: **it has not yet been
  tested.** §3e's discriminator stands exactly as frozen and is still the test.
- **It does not touch `primalMinResTol`.**

---

## ADDENDUM 4 — 2026-09-13 — THE GRADE-RECORD FILENAME IS A RULE, NOT A PATTERN; AND `FM8` IS A `PASS`

**This addendum carries the document to version 1.4.** Earlier version lines are **deliberately not
edited**, for the reason `ADDENDUM 1` gives.
**Lines whose number changed above this section: 0.** Proof in §A4.3.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL**, and **does not touch the grading
path**, whose md5 `1a5ca51f8dab59e3c72b9a71ce8f77e6` is unchanged across **all four** freezes of this
document.

### A4.0 THE RULE, STATED INSTEAD OF INFERRED

`ADDENDUM 2` §A2.1 registered the grading `--out` path for **`FM7` by name**. `FM8` then ran, and its
filename was chosen by **applying the same shape to a new arm id** — which is an unstated rule a later
reader has to infer from two examples. **That is the shape of thing this item has been paying for all
night**, so it is stated:

> **THE GRADE RECORD FOR EVERY ARM OF THIS REGISTRATION IS
> `<run root>/AFTER_ITEM9R2_<ARM>_GRADE.json`, WITH `<ARM>` THE ARM ID THAT RAN.**
> `d6r2c_fm6_grade.py`'s `--out` default is `AFTER_ITEM9R2_GRADE.json`, which carries **no arm id at
> all**, so `--out` is passed **explicitly on every grading** and is never left to the default.

Applied so far: `AFTER_ITEM9R2_FM8_GRADE.json`. **The rule covers arms not yet run**, which a pattern
inferred from examples does not.

**And the reason it matters is still §A2.0's:** the `arm` field **inside** every record reads `"FM6"`
and **is wrong** for any other arm. Two identifiers carry the truth — the filename and the ledger row —
and one does not. **A rule that names the filename is what keeps that count at two.**

### A4.1 `FM8` — THE RESULT, AND THE ONE THING A READER MUST NOT CONCLUDE FROM IT

**`FM8`: `PASS`.** rc=0, 144 s wall, **9.600 core-min** against a cap of 47.211 (20.3 % of it) and a
prediction of 15.737. `I1`, `H1`, `H2`, `H3`, `H4` all hold; all five planted controls visible;
**zero primal failures**, where `FM5` and `FM7` each stalled at `1.278377566e-05`.

| | value |
|---|---|
| `J_fresh` | `0.023063278222500323` |
| `Jf` (deformed mesh, inherited) | `0.023063259528677764` |
| absolute difference | **`1.869382e-08`** against the band `3.064163e-04` — **16,391× inside** |
| `H1` `worst_dist` | `5.010837892761856e-09` — the ADDENDUM 4 §A4.3 **equality**, met bit for bit on a third run |

**THE REGISTERED CHANGE TOOK EFFECT, AND THAT WAS CHECKED BEFORE THE NUMBER WAS BELIEVED.** `FM5` and
`FM7` both begin at `p initRes = 1.0` — a freestream start normalises to exactly 1. **`FM8`'s three
conditions begin at `4.476e-02`, `1.937e-02`, `1.172e-02`: two decades below a freestream start.**
`G-VERIFY` recorded `t100 = 3.734093363e-06` against `FM5`'s `1.103361217e-03` and no floor line at all.

**THE CAVEAT, WHICH IS PART OF THE RESULT AND NOT A FOOTNOTE.** `1.869e-08` is **46.9× tighter than
`N-D48`'s measured path-dependence of `8.765e-07`** — two solutions on **different meshes** agreeing
more closely than this solver agrees with itself on the **same** mesh reached by a different path. **A
reader handed that number without this paragraph will conclude the solve inherited its answer.** It did
not: the transferred field does **not** satisfy the fresh-mesh equations — the solves start at residual
`~1e-2`, not `1e-8`, and do roughly four decades of work — and the solution moved, `cl05`'s `CL`
shifting by `1.45e-7`. **The honest reading: the two meshes are geometrically very close** (identical
topology, same extrusion parameters, first-cell heights 1.0 % apart) **and a converged start removes the
cold-start path-dependence channel.** §2e registered `H3` as *"the only thing that differs is the
mesh"*; **with the initialisation that is MORE true than it was for a freestream start, not less** — but
the comparison no longer carries the cold-start channel, and **that sentence belongs in the item-10
report rather than left to be inferred.**

### A4.2 A VACUOUS CLAUSE IN AN INHERITED INSTRUMENT — DISCLOSED, NOT REPAIRED

**`H4`'s `primal_converged` is carried by `d6r2c_freshmesh.py`'s `_converged()`, which DEFAULTS TO
`True` when `mp0X/primal_residual.json` is absent — and it is absent.** That clause is therefore
**vacuous**: `H4`'s convergence evidence is carried entirely by `rc = 0` and the absence of any
`Primal solution failed` line. **That is real evidence** — `FM5` and `FM7` both showed `rc = 1` with a
failure line — **but it is not the evidence the clause claims to be.**

**It is in the REUSED producer, which is frozen and unchanged at `1d15ce361673ca600d565280441b67e0`, and
it is NOT repaired here.** It did not bite on `FM8` because `rc` carries the same information. **It is
disclosed now rather than discovered on an arm where `rc` and the field disagree.**

### A4.3 THE APPEND-ONLY PROOF

- Pre-append state of the working-tree file, read in the same shell invocation as the append: md5
  **`55fd03d2306b6e2f8f9de4c17f9023bd`**, **979 lines**, and **byte-identical to `HEAD`'s committed blob** — asserted in
  that same invocation, so the append is provably the first change since the freeze.
- `git diff --numstat` on this path must show **insertions only and `0` deletions**. *(No count is
  asserted: a concurrent commit landing during a `git diff` makes the number read against a stale
  baseline — measured on `ADDENDUM 2`.)*
- **Lines whose number changed above this section: 0.**
- This is `ADDENDUM 4`, the number derived from the maximum existing heading, never a count.

### A4.4 WHAT THIS ADDENDUM DOES NOT DO

- **It does not re-grade anything.** `FM8` is `PASS`; `FM6` and `FM7` are `NOT A RESULT`, closed.
- **It does not touch the grading path, any gate, threshold, cap or label**, and it does not repair the
  vacuous clause of §A4.2.
- **It does not claim the fresh mesh validates the 24.732 %.** `H3` is a **two-mesh comparison at one
  nominal resolution** — no Roache triple, no GCI, no observed order — and `O_mp` stands at `GATE FAIL`.
- **It does not touch `primalMinResTol`.**
