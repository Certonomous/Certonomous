# LADDER RECIPE RULING — an observed order across a RECIPE-FORKED gap is NOT A RESULT

**Standing ruling of the cfd supervisor, 2026-08-25.** Recorded here because seven of
this lab's stored ladders carry a published observed order that this ruling voids, and
because a future reader who finds `observed_order: 10.467` in a study file must not be
able to read it as a result.

**ZERO SOLVER COMPUTE.** Nothing was meshed, solved or refitted to produce this
record. Every reading below comes off a dictionary or a log already on disk.

---

## 1. The ruling

> **An observed order computed across a RECIPE-FORKED gap is `NOT A RESULT`.**
>
> It is a slope fitted across a **change of experiment**
> (`docs/charters/VERIFICATION_CHARTER.md` §3.2), and under `CLAUDE.md` **rule 5** a
> row whose triple is not a valid CONVERGING triple is `NOT A RESULT` **whatever its
> value**.

### 1.1 TWO THINGS THAT MUST TRAVEL WITH THIS RULING EVERYWHERE IT IS QUOTED

**1. It says NOTHING against the underlying solves.** Every rung ran. Every
coefficient was measured on a real mesh by a real solver, and every cell count,
force history and convergence log stands exactly as recorded. **The ruling is against
the GRID-CONVERGENCE CLAIMS BUILT ON THEM and against nothing else.** A reader who
takes this as a finding about the solves has taken the opposite of what it says.

**2. The affected rows move TOWARD `NOT A RESULT`, which `CLAUDE.md` rule 5's one-way
door permits — never back.** In rule 5's own words, the gate *"can only turn a PASS or
GATE FAIL **into** NOT A RESULT, never the reverse."* Nothing in this record turns any
`NOT A RESULT` back into a `PASS`, and nothing in it ever can.

### 1.2 The vocabulary

`NOT A RESULT` here is the `CLAUDE.md` rule-1 **gate verdict**, not a matrix tier.
The matrix tier these rows carry is `NOT HELD`, in
`verification/campaign/MATRIX_CONTRIBUTION.md` §5, rows C-69 … C-76. **The two
vocabularies are distinct and this record never conflates them.**

---

## 2. The instrument

`scripts/recipe_audit.py`, first committed **`72bc966d`**, message *"cfd: mechanise
VERIFICATION_CHARTER 3.2 rule 3 -- scripts/recipe_audit.py, a per-gap recipe audit
that refuses rather than degrades."*

| property | value, verified at HEAD `af2b23b0` |
|---|---|
| HEAD blob length | **1,558 lines** |
| HEAD blob sha256 | `4e45603038f7ae03c9236e7e800f3e1f87d47086eb4bf9e467520c125da8dd9a` |
| `--selftest` | **PASS** — 53 value controls, 12 mutation controls (10 must-flip + 2 false-positive), 6 refusal controls, live `ahmed_25` regression fixture PRESENT |
| sweep coverage | **461 candidate directories, 422 parsed, 14 ladders assembled: 7 RECIPE-FORKED, 4 recipe-clean, 3 unauditable** |

**What it classifies, per adjacent pair of rungs:**

| recipe | background | class |
|---|---|---|
| fixed | changed | `SCALED` — legitimate |
| fixed | fixed | `IDENTICAL` — the rungs are the same mesh |
| **changed** | **fixed** | **`RECIPE-FORKED`** — not admissible as a refinement step |
| changed | changed | `MIXED` — two knobs at once |

**It never reads a coefficient, never fits an order, and never re-grades a stored
verdict.** It decides **admissibility**, which is upstream of grading and cannot
substitute for it. A refusal (exit 2) is **not a pass**.

---

## 3. The seven RECIPE-FORKED ladders, re-measured

**Every verdict in this table was re-run by the recording lane against the rung
directories named**, not transcribed from the sweep's summary. All seven return
`LADDER VERDICT: NOT A RESULT`.

| ladder | published p | forked gap(s) | background cells, coarse → medium → fine | rung directories |
|---|---|---|---|---|
| `ahmed_25` | **1.95** | gap 2 | **9,450 → 28,080 → 28,080** (gap 1 `SCALED` ×2.9714; gap 2 background **HELD FIXED**, recipe moved in **3 fields**) | `/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb` (20,621 cells) · `…/study-ahmed_25-medium-b37e86` (45,753) · `…/w3-published-rung-ahmed_25/a` (79,439) |
| `ahmed_35` | **3.169** | gap 2 | **9,450 → 28,080 → 28,080** | `…/study-ahmed_35-coarse-186b41` (20,425) · `…/study-ahmed_35-medium-d198f3` (45,813) · `…/act7-ahmed_35-02688b` (79,778) |
| `naca0012_wing` | **3.173** | gap 2 | **13,524 → 39,600 → 39,600** (gap 1 `SCALED` ×2.9281) | `…/study-naca0012_wing-coarse-09bec1` (27,265) · `…-medium-520ccb` (67,356) · `…/study-naca0012_wing-1021cb` (140,580) |
| `naca4412_wing` | **10.467** | gap 2 | **13,524 → 39,600 → 39,600** | `…/study-naca4412_wing-coarse-a6c5e0` (27,237) · `…-medium-337080` (67,826) · `…/study-naca4412_wing-1af072` (137,569) |
| `motorBike` | **7.298** | **BOTH gaps** | **(20 8 8) = 1,280 on all three rungs** — the background never moves at all | `…/mb-iterfix/coarse` (14,714) · `…/mb-iterfix/medium` (66,302) · `…/study-motorBike-f8b4a2` (353,688) |
| `airliner_wing_span52` | none | gap 2 | **6,300 → 17,280 → 17,280** (gap 1 `SCALED` ×2.7429) | `…/study-airliner_wing_span52-coarse-1f61fe` (9,639) · `…-medium-e565e1` (22,754) · `…/study-airliner_wing_span52-2cdf8e` (32,385) |
| `credential-repair-naca4412` | none | **BOTH gaps** | **39,600 throughout**; levels move (3 4)/(4 5)/(5 6) | `…/credential-repair-naca4412-medium` (263,359) · `…-fine` (645,251) · `…-finer` (1,849,113) |

**In every one of the seven, the stored `levels[]` cell counts match the rung
directories to the cell**, which is what makes the directories identifiable as those
rungs.

**`naca4412_wing` is `VERIFICATION_CHARTER.md` §3.2's OWN worked example**, and it is
now measured mechanically rather than argued. **`ahmed_25` is the case that shows why
the defect survived inspection**: gap 1 looks exactly like a legitimate refinement,
and four of its five stored guards PASS. **No guard in the set was looking at the
recipe.** The protection was accidental.

### 3.1 What is annotated where

The ruling is written into the artefacts the orders actually live in — struck, never
rewritten, with the original number left visible beside its verdict:

| file | annotations |
|---|---|
| `models/curriculum/uq-studies/ahmed_25.json` | `numerical.observed_order`, `refit_in_place.reproduced_exactly.observed_order` |
| `models/curriculum/uq-studies/ahmed_35.json` | both, as above |
| `models/curriculum/uq-studies/naca0012_wing.json` | both, as above |
| `models/curriculum/uq-studies/naca4412_wing.json` | `numerical`, `superseded.numerical` (the 4.625 predecessor), `refit_in_place`; **and the `credential-repair-naca4412` ladder, whose rungs were built to repair this study** |
| `models/curriculum/uq-studies/motorBike.json` | both, as above |
| `models/curriculum/uq-studies/airliner-wing.json` | no `numerical` block exists; annotated so no order is ever fitted from these three rungs |

Each carries a top-level `recipe_fork_ruling_2026_08_25` block with the ruling, both
clauses of §1.1, the sweep commit sha, and the instrument's stated limit; and each
voided number carries a **sibling key beside the number itself**, so a reader who
greps `observed_order` cannot reach the value without reaching the verdict.

---

## 4. Cases where NOTHING is withdrawn, stated so the ruling is not over-read

* **`airliner_wing_span52` and `credential-repair-naca4412` never had an order
  fitted.** Nothing is withdrawn. Their rows are a **forward bar**: no order may be
  fitted from those rungs in future.
* **`cube`'s stored `observed_order` is `null`.** There is nothing to void.
* **`naca0015_sail`'s 1.696 is NOT withdrawn by this ruling — and is not certified by
  it either.** It is one of the **3 unauditable** ladders, so its admissibility is
  **unknown**. **An unauditable ladder is not a clean one**, and the sail's order
  should not be quoted as if this sweep had cleared it.
* **The `b52` stored orders are not voided on recipe grounds** — its `recipe_audit`
  carved a single-recipe sub-family out of a mixed set. They fail for separate,
  already-recorded reasons: **28.675** is clamped and refused by `order_window`, and
  **2.253** is superseded by rung 7's *"no order fitted; the ladder is no longer
  monotone"*.
* **Draw-scatter measurements on any of these bodies remain valid as measurements of
  scatter.** Replicate meshes at a fixed resolution measure what they measure
  regardless of how the ladder was built. What does not survive is treating those
  rungs' **differences** as discretization increments.

---

## 5. A STATED LIMIT ON THE INSTRUMENT — carry it wherever the instrument is cited

**`similarity_failures()` treats ANY change of a block's grading as a similarity
failure** — *"regraded cells are not scaled cells"*.

**That is correct for the uniform-background snappyHexMesh ladders this sweep covers,
where the background block is ungraded (`simpleGrading (1 1 1)`) and refinement is
bought by scaling `(nx ny nz)`. It is WRONG for a correctly-built GRADED ladder.**

A geometrically similar graded family **must** change its grading string as it
refines, and precisely in order to stay similar: the invariant a wall-resolved ladder
has to hold is the **first cell scaling with the mesh**, and in blockMesh the first
cell is set by the total expansion ratio over a fixed span at a given cell count.
Halve the first cell while doubling the count and the expansion ratio **must** move.
**A graded family that held its grading string FIXED would be the defective one.**

**The live case this matters for: F12's repaired RAE 2822 ladder.** First cells
2.0e-6 / 1.0e-6 / 5.0e-7 chord; wall-normal total expansion 4.401087e6 / 4.598885e6 /
4.702009e6 — the similarity invariant held to **6.84 %** across a ×4 cell-count
refinement, with the recipe otherwise untouched. **Running `recipe_audit.py` against
it would report a SPURIOUS FORK.**

**Two separate facts, and they are not the same fact:**

1. Run against F12's ladder **as it stands on disk**, the file **REFUSES** (exit 2,
   "no `system/snappyHexMeshDict`"). F12 is a pure blockMesh O-grid and carries no
   snappy dict, so the similarity rule is never reached. **A refusal is not a pass and
   it is not a fork either.**
2. The moment a graded ladder **does** carry a snappy dict — or if the blockMesh
   similarity rule is ever lifted out and applied on its own — the rule fires and the
   verdict is **`NOT A RESULT` on a correctly-built ladder.**

**Note the shape of that wrong answer, because it is not the obvious one.** The gap is
**not** classified `RECIPE-FORKED`; the recipe half of the audit is correct and says
so. **The false verdict arrives through the SIMILARITY channel on a `SCALED` gap.** A
reader who saw only `NOT A RESULT` would misattribute it to the recipe, which is the
wrong repair on the wrong file.

**So: do not run this file against a graded ladder and believe a `NOT A RESULT`.**
Extending it to graded families needs a different similarity invariant — the per-level
first cell, or the total expansion held within a stated band — and that is a change to
the classifier, deliberately not made.

**A check that overstates its reach is worse than none, so this limit is pinned as an
executable claim, not a paragraph.** A STATED-LIMIT control in `--selftest` (section
viii-b, **8 controls**) **asserts the wrong answer on purpose**: if somebody later
teaches the file about graded families, that control **fails** and forces the
docstring to be rewritten with the classifier.

> **STATUS OF THAT TEXT, disclosed rather than assumed.** The stated-limit docstring
> section and its 8 selftest controls are **ON DISK at
> `/home/ubuntu/Certonomous/scripts/recipe_audit.py` (1,680 lines) and are NOT AT
> HEAD `af2b23b0`** (1,558 lines) at the time this record was written — somebody's
> uncommitted work, **inspected and not reverted** per `CLAUDE.md` rule 10. The limit
> is therefore **restated in full above**, so that it survives independently of
> whether and when that file lands. Verified by the recording lane:
> `python3 scripts/recipe_audit.py --selftest` on the disk copy returns **SELFTEST
> PASS** with the 8 stated-limit controls reported by name.

---

## 6. `LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md` — SUPERSEDED on its closing line, and two facts corrected

The 2026-08-10 sweep's closing sentence reads:

> *"**Exactly one ladder in this lab is known to be a ladder**, and it is the one whose
> turn was withdrawn today for a different reason."*

**That sentence is SUPERSEDED.** The mechanised sweep assembled **14** ladders and
found **4 recipe-clean**. The 2026-08-10 document had already corrected its own
headline once, in its §0, and this is the second correction, made against measurement
rather than against a better argument.

**Two factual rows in its §2 classification table are corrected:**

| §2 row | what it says | what is measured |
|---|---|---|
| `motorBike` | **UNDETERMINABLE**, *"1 of 3"* rungs on disk, *"deciding rung's case absent"* | **All three rungs are on disk**: `mb-iterfix/coarse` **14,714**, `mb-iterfix/medium` **66,302**, `study-motorBike-f8b4a2` **353,688**. The ladder is **RECIPE-FORKED at BOTH gaps**, **directly measured** |
| `ahmed_25` / `ahmed_35` | **CONFOUNDED**, *"2 of 3"*, *"production missing, `recipe_audit` records the level change"* | **The production rungs exist** — `w3-published-rung-ahmed_25/a` (79,439) and `act7-ahmed_35-02688b` (79,778). Both forks are **directly measured, not inherited from prose** |

**Why the 2026-08-10 sweep could not see them, and it is not a failure of care:** its
Route B enumerated case directories by the glob `study-<body>*`, and it says so in its
own §6. The production rungs live under `w3-published-rung-*`, `act7-*` and
`mb-iterfix/*`. **The mechanised sweep walks the filesystem with `os.walk` and
consults neither git nor grep**, which is the only reason it reached them —
`/home/ubuntu/certonomous-runs/` is outside the repository and `grep` in this shell
honours ignore files.

**What the 2026-08-10 sweep got RIGHT and this record does not disturb:** the
structural finding that on both NACA wings `coarse → medium` moves the background
divisions only while `medium → production` holds them exactly and moves three levels
at once; and its §0 identification of the **single generator defect**,
`sdk/workflows/geometry_study.py::refinement_rungs()`, whose runtime guard checks
**distinctness, not comparability**. **One generator defect with downstream victims
and a filed fix is a materially more tractable finding than N independent failures**,
and it is still the right frame.

---

## 7. DRAFT NOTE FOR THE VERIFICATION TEAM — NOT AN EDIT, and NOT FILED

**`docs/charters/VERIFICATION_CHARTER.md` is the verification team's file and cfd does
not edit it.** This section is a note for the chief to route, and it is not sent,
filed or registered anywhere (rule 7).

**The note:**

> §3.2's NACA 4412 worked example — *"coarse and medium are both `level (2 3)` and
> differ only in background block density; production alone is `level (3 4)`"* — is
> **now measured mechanically** rather than described. `scripts/recipe_audit.py`
> (`72bc966d`) classifies that ladder's gap 2 as **RECIPE-FORKED**: background held at
> **39,600 cells** while the recipe moves. The published **observed order 10.467** is
> `NOT A RESULT` under `CLAUDE.md` rule 5, and the same defect is measured on **six
> further ladders**, including `ahmed_25`, whose order of **1.95** looked entirely
> plausible and was caught by nothing.
>
> **The charter clause §3.2 rule 3 — *"A recipe audit precedes an order"* — was written
> as checkable and left UNMECHANISED, and `docs/LESSONS.md` L-303 is what that cost.**
> It is mechanised now. **The verification team may wish to consider whether §3.2
> should cite an executable check rather than a worked example**, and whether the
> recipe audit should be an **explicit** prerequisite of an order rather than an
> implicit one — a recommendation the 2026-08-10 sweep already made in its §5 and
> which nobody has ruled on.
>
> **Carry the instrument's stated limit with any such citation** (§5 above): the
> similarity rule is correct for uniform-background snappy ladders and **wrong for a
> correctly-built graded ladder**, and F12's repaired RAE 2822 family is exactly such
> a ladder.

**Reserved to the verification team, and to no cfd agent:** any change to
`VERIFICATION_CHARTER.md`, and the ruling on whether a charter clause cites a check.

---

## 8. Provenance and cost

**Recorded** 2026-08-25 by a cfd `lab-lane` under the cfd supervisor, against HEAD
`af2b23b0`. **ZERO SOLVER COMPUTE** — no solver, no mesh, no MPI rank. The lane ran
`scripts/recipe_audit.py --selftest` (PASS), seven ladder audits, and one `--discover`
walk over **417** case directories under `/home/ubuntu/certonomous-runs/`. Those are
single-rank Python reads of dictionaries on disk; they were not instrumented, and the
time is **reported as an estimate under 2 core-minutes — an estimate, not a
measurement**. **Estimate-versus-actual (rule 12):** predicted 0 core-minutes of
solver time, actual **0**, ratio n/a, zero waste. **No `docs/COST_CALIBRATION.md` row
is due**, because no compute process completed.

**Submissions are parked.** Nothing here is filed, sent, uploaded or registered
outside this box.
