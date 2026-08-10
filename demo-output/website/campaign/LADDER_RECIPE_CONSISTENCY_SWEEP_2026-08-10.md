# Lab-wide ladder recipe-consistency sweep

**Chief-ordered 2026-08-10 (`de27b492`), zero compute.** The question:
**for each ladder, does one and only one knob move between rungs, and does it move
monotonically?** Three classes: **CLEAN**, **CONFOUNDED**, **UNDETERMINABLE**.

> **Headline: the confound is wider than the recipe audits recorded. Both NACA
> wings — 2 of the 3 ladders in this lab that carry draw-scatter evidence — are
> CONFOUNDED, and nobody had written it down.**

---

## 0. CORRECTION — Route A landed and Route B (this document's primary) was WRONG on its headline

**Everything below §1 is Route B's and is retained unedited. This section
supersedes its headline and two of its conclusions.** The reconciliation the
pre-registered method requires is here, not resolved silently.

### What Route B got right

The **structural fact**, verified from the generating dictionaries and unchanged:
on both NACA wings, `coarse → medium` moves the background divisions only, and
`medium → production` holds the divisions **exactly** at (33 60 20) while surface,
region and feature levels all move. That is a real confound and Route B measured
it from the artifacts rather than taking anyone's word.

### What Route B got WRONG

**1. "…and nobody had written it down." FALSE, and it is the headline.**
`naca0012_wing.json` and `naca4412_wing.json` **both carry a `recipe_audit`
saying exactly this**: *"The three stored rungs are TWO mesh recipes, and no knob
moves twice."* It was written down, in the very files I was classifying.

**Why I said it:** my pre-flight checked `recipe_audit` on the **five retrofit
ladders only** — `ahmed_25`, `ahmed_35`, `motorBike`, `cube`, `naca0015_sail` —
found it absent on three, and I generalised "absent" to bodies I had never
queried. **The wings were never in that query.** A conclusion about what the lab
had not recorded, drawn from a search that did not look.

**2. "Exactly one ladder in this lab is known to be a ladder." BADLY WRONG.**
Route B enumerated case directories by the glob `study-<body>*`. **The
single-recipe replacement families live under other names**, so the glob could
not see them. They exist for four bodies:

| body | valid single-recipe family | knob |
| --- | --- | --- |
| B-52 | 5–6 rungs (135 779 … 441 057) | background divisions only |
| Ahmed 25° | R4's 5 rungs (79 439 … 454 691) | background divisions only |
| **NACA 0012** | **W3's 4 rungs (140 545 … 525 692)** | background divisions only |
| **NACA 4412** | **W3's 4 rungs** | background divisions only |

**And Route A found many more clean ladders Route B never reached**, because they
are campaign ladders with no stored study: TMR flat plate and TMR bump (structured
dimensions doubled, gradings fixed), W1's NASA bump grids (exact point-drop,
r = 2), F3 wedge/cone/diamond, F4 hypersonic, F7 dam-break (two ladders, an
explicit *"one knob per flag"* generator), F6b ERCOFTAC, DPW8, F11 cavity.

**3. The direction of the error is the same one L-49 names, one level up.**
Route B was *structural* and therefore different in kind from a text search — that
part was right. But its **enumeration** was still a pattern I chose
(`study-<body>*`), and it found the ladders that pattern could reach. **Being
different in kind protects the reading; it does not protect the sampling frame.**

### The corrected picture

| class | count | which |
| --- | --- | --- |
| **CONFOUNDED** | **5** | the stored 3-rung ladders: `ahmed_25`, `ahmed_35`, `naca0012_wing`, `naca4412_wing`, plus the B-52's stored 8-rung set |
| **CLEAN** | **≥13** | 4 purpose-built replacement families (B-52, Ahmed R4, both wings' W3 families) + TMR flat plate, TMR bump, NASA bump grids, F3, F4, F7 ×2, F6b, DPW8, F11 |
| **UNDETERMINABLE** | **3** | `motorBike` (deciding rung's case gone), `cube`, `naca0015_sail` |
| not a grid ladder | 3 | `aortic-valve` (quadrature), `airliner-wing` (geometry family), F5a (Reynolds + mesh both move) |

### The finding that actually matters, and Route A alone could reach it

**All five confounded ladders come from ONE code path:**
`sdk/workflows/geometry_study.py::refinement_rungs()`. Its own docstring says
what it does:

> *"when the floor would make two rungs identical, the coarser one **also scales
> the background-mesh divisions** so the cell budgets stay distinct; the runtime
> cell-count guard still refuses to report a study if they do not."*

**The guard checks DISTINCTNESS, not COMPARABILITY** — two rungs can differ in
every cell and still not be two rungs of one ladder. **This is already an open
docket item: #75, `w3-refinement-rungs-varies-two-knobs`.** So the confound is
one generator defect with five downstream victims and a filed fix, not five
independent failures — a materially different and more tractable finding than
Route B's.

### What is unchanged

The wings' **draw-scatter measurements remain valid as measurements of scatter**;
the confound is about treating their stored rungs' *differences* as
discretization increments. And every claim listed in §4 below still inherits the
confound — that list stands.

## 1. Two routes, and which is which (L-49)

**L-49 says a search built from the vocabulary of what you just read returns what
you just read.** I had just read the B-52 and Ahmed `recipe_audit` findings, so a
text search would have been built from *their* words — "two mesh recipes", "no
knob moves twice".

| | route | reads | can it find a confound nobody wrote down? |
| --- | --- | --- | --- |
| **A** | text sweep of records and stored studies | what the lab **SAYS** about each recipe | **No** — only what someone already noticed |
| **B** | **structural**: diff each rung case's `blockMeshDict` divisions and `snappyHexMeshDict` levels | what the generating dictionaries **SHOW** moved | **Yes** |

**Route B is the primary and it is different in kind** — it reads the artifacts
that built the meshes, not anyone's description of them. **Route A is dispatched
and its reconciliation is outstanding**; the classification below is Route B's,
and any disagreement will be reported as a correction rather than resolved.

**Route B is also the only route that can establish UNDETERMINABLE**, because
"no case survives" is a fact about the filesystem, not about the prose.

## 2. The classification

| ladder | rungs on disk | what moves, rung to rung | **class** |
| --- | --- | --- | --- |
| **`naca0012_wing`** | 3 of 3 | coarse→medium: **divisions only**; medium→production: **levels only** | **CONFOUNDED** |
| **`naca4412_wing`** | 3 of 3 | *identical pattern* | **CONFOUNDED** |
| **`ahmed_25`** | 2 of 3 | coarse→medium: divisions only; production missing, `recipe_audit` records the level change | **CONFOUNDED** |
| **`ahmed_35`** | 2 of 3 | *identical pattern* | **CONFOUNDED** |
| **`b52`** | many | `recipe_audit` carved a 5-rung single-recipe family (background divisions only) out of a mixed set | **CLEAN (the carved family only)** |
| **`motorBike`** | **1 of 3** | deciding rung's case absent | **UNDETERMINABLE** |
| **`cube`** | **1 of 3** | " | **UNDETERMINABLE** |
| **`naca0015_sail`** | **1 of 3** | " | **UNDETERMINABLE** |
| `airliner-wing`, `aortic-valve`, `tmr_flatplate_*` | — | no ladder stored (0 rungs) | not a ladder |

## 3. The measurement, for the two wings — three knobs move at once

**`naca0012_wing`** (cell counts match the stored rungs exactly):

| rung | cells | blockMesh divisions | surface level | region level |
| --- | --- | --- | --- | --- |
| coarse | 27 265 | **(23 42 14)** | (2 3) | 1 |
| medium | 67 356 | **(33 60 20)** | (2 3) | 1 |
| production | 140 580 | **(33 60 20)** — *identical to medium* | **(3 4)** | **2** |

**`naca4412_wing`** — the same, to the same division triples:

| rung | cells | blockMesh divisions | surface level | region level |
| --- | --- | --- | --- | --- |
| coarse | 27 237 | (23 42 14) | (2 3) | 1 |
| medium | 67 826 | (33 60 20) | (2 3) | 1 |
| production | 137 569 | (33 60 20) | **(3 4)** | **2** |

> **coarse → medium refines the background and holds the levels.
> medium → production holds the background EXACTLY and moves surface level,
> region level and feature level together.**
>
> **No knob moves twice, and the second step moves three at once.**

**These ladders were never measuring discretization.** Their increments are a
recipe change plus a resolution change, confounded, with no way to separate them
after the fact — which is a larger class of defect than the shape features the
draw-scatter retrofit went looking for.

## 4. What has been published off the confounded ladders

These claims **inherit the confound whether or not anyone measured scatter.**
Listed, not withdrawn — the chief rules.

**`naca0012_wing`**
- `W3_GUARD_SWEEP.md:69` — *"Its increments grow under refinement"*
- `W3_WING_VALID_FAMILY_RESULTS.md:179` — corpus row *"flattens, inside the mesh scatter"*
- `NOT_PASSING_REGISTER.md:674` — *"monotone decreasing"* across the three rungs
- `W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md` — the r3→r4 increment reading
- `naca0012_wing.json` — `band_rel` 1.25448

**`naca4412_wing`**
- `W3_WING_VALID_FAMILY_RESULTS.md:73` — *"**P2 is scored TRUE.** The NACA 4412 comes back non-monotone."*
- same, :178 — corpus row *"turns, inside the mesh scatter"*
- `NOT_PASSING_REGISTER.md:547-554` — *"non-monotonic"*, *"diverged from monotonicity criterion"*
- `W3_NACA4412_LAYERED_REPLICATES.md:131, 209` — the non-monotonicity's *"leading suspect"*
- `W3_MESH_QUALITY_GATE_TWO_VALUES.md:152` — where the non-monotonicity *"should be looked for"*
- `naca4412_wing.json` — `band_rel` 0.52115

**`ahmed_25` / `ahmed_35`** — already dispositioned RESTATE on recipe grounds
(`79ab1765`).

**An important non-consequence.** The wings' **draw-scatter measurements stay
valid as measurements of scatter** — replicate meshes at a fixed resolution
measure what they measure regardless of how the ladder was built. What does not
survive is treating those rungs' **differences** as discretization increments.

## 5. What this changes about the retrofit, and about the rule

**The recipe audit is not a prerequisite of the draw-scatter rule; it is the
larger question.** Of the eight real ladders:

- **4 CONFOUNDED** — their increments were never discretization increments
- **3 UNDETERMINABLE** — the rung cases no longer exist
- **1 CLEAN**, and only because a `recipe_audit` explicitly carved a
  single-recipe sub-family out of a mixed set

**Exactly one ladder in this lab is known to be a ladder**, and it is the one
whose turn was withdrawn today for a different reason.

**Recommended, not taken:** Verification Charter §17 currently makes the recipe
audit an implicit prerequisite (via *"a recipe audit precedes an order"*).
**It should be explicit** — a draw-scatter measurement on a confounded ladder is
a precise measurement of the wrong quantity, and this sweep shows that is the
common case rather than the exception.

## 6. Method note

Route B compares, per body, every surviving `study-<body>*` case directory:
`system/blockMeshDict`'s `hex ... (nx ny nz)` triple, `system/snappyHexMeshDict`'s
`refinementSurfaces` level pair, `refinementRegions` level, and feature-edge
level; cell counts from `log.checkMesh` or the `polyMesh/owner` header, and they
**match the stored `levels[]` to the cell** on both wings, which is what makes
the dirs identifiable as those rungs. No file was modified and no solver ran.
