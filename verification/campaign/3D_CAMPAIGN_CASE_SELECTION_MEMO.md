# Consolidation-week 3D campaign — case selection memo: Ahmed body vs Meinders cube

**Date:** 2026-08-25
**Team:** cfd. **Status:** MEMO FOR SUPERVISOR RULING. Not a pre-registration.
**ZERO COMPUTE.** No solver was launched, no mesh was built, no case directory
was created for this memo. Every number below is either read off an artifact
already on disk (cited by absolute path) or derived by arithmetic shown in
place.

**What this memo does NOT do.** It does not rule on the Meinders configuration.
That decision is the heat-transfer team's, this session, on their own spine
(Sanaa's H-2: `T3 → T5 → T8 → T12 → K2 rack row`). This memo takes their
artifact as an INPUT and says exactly which artifact, below in §0.

---

## 0. The heat-transfer Meinders finding — what I found, and what I did not

I was told the heat-transfer team "has already established that the geometry is
TIGHT ON REFINEMENT RATIO" and to find that finding on disk before writing
anything about Meinders. Stated plainly, because the distinction matters:

**FOUND — the refinement-ratio arithmetic, on disk, dated 2026-08-22:**
`docs/campaigns/T-family/T5_PREREGISTRATION_DRAFT.md`, §5.4 (the ladder) and
§11.1–§11.3 (the cost and the stop threshold). This is where the tightness
lives and it is quantified there. It is quoted and used in §2 and §3 below.

**FOUND — this session's state of that rung**, in the T-family's coverage-matrix
contribution written at 19:21 on 2026-08-24,
`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` rows S11, C14 and the
3D-conjugate row: T5's primary is `P PAPER-HELD`, the pre-registration is
**unfrozen**, **12 INTERPRETATIONs sit on Sanaa's desk**, and the rung is
**NEVER RUN**. (That file is untracked at the time of writing — it is this
session's work in progress, not a committed record.)

**FOUND — the acquisition commit** that put the primary on disk:
`4cc8c22c` ("T5 unblocked and T4 half-opened…"), 2026-08-21.

**NOT FOUND, and I am saying so rather than assuming it.** I could not find a
**configuration ruling** from this session — no document, commit or board entry
dated 2026-08-24/25 that RULES the Meinders configuration (single cube vs row
vs 4×4 matrix) or that states a refinement-ratio conclusion in the supervisor's
own words. I searched `docs/LAB_STATE.md`, all of
`docs/campaigns/T-family/`, all of `verification/campaign/`, the full
2026-08-24 git log, and a repo-wide grep for "meinders" across `docs/`,
`cases/` and `verification/`. The seven files that mention Meinders are listed
in the appendix; none of them is a ruling.

**Consequence, applied honestly throughout this memo:** where I state Meinders'
refinement-ratio headroom I am reading the T5 DRAFT's own arithmetic, which is
a design lane's proposal and is **explicitly unfrozen**. Its headroom is
therefore **UNVERIFIED BY ME as a supervisor ruling**, and if heat-transfer
rules a different configuration this session — the row of cubes (thesis Ch. 6)
or the 4×4 matrix (Ch. 8) rather than the single cube — **every Meinders number
in this memo is superseded**, because those configurations have different
domains, different cell counts and a different cost. §6 states that as an
explicit flip condition.

---

## 1. THE PUBLIC PRIMARY

Rule 15 is title-page verification, never by filename, file type or hash. Both
verdicts below are mine, taken this session.

### 1.1 Meinders — **ON DISK AND TITLE-VERIFIED**

`docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf`
`sha256 36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb`
(15,477,157 bytes, 281 pages).

**How I verified it, and why the ordinary route did not work.** The `.txt`
sidecar beside it is a **stub**: 281 bytes, and every one of those bytes is a
form-feed character (`\f`) — it carries no text at all. `pdftotext` on pages
1–3 returns nothing. **The PDF has no text layer; it is a scanned image.** So a
sidecar-based check here would have verified nothing while looking like it had.

I rendered the pages and read them:

- **Page 1** (the *Stellingen*, the propositions sheet bound with a Dutch
  thesis) reads: *"behorende bij het proefschrift getiteld: **Experimental study
  of heat transfer in turbulent flows over wall-mounted cubes**, van **Erwin R.
  Meinders**"*, followed by 11 numbered propositions, of which #1 concerns the
  cube-averaged convective heat transfer coefficient.
- **Page 3** is the title page proper, carrying the same title over two lines
  and the archive stamp `TR 3213`.

Author and title are confirmed **from the document's own front matter**. That
is title-page verification and it is independent of the filename, which is
exactly what L-144 asks for.

**Stated experimental uncertainty** (recorded in `4cc8c22c` and in the T5 draft
§2): **5 % in local `h` mid-face, ≈10 % at the edges**; single cube
`Re_H` 2500–5000, matrix `Re_H` 2380–5280. A stated uncertainty is what a `P`
chip needs and Ahmed does not have.

**The honest defect in this primary, and it is not small.** The data are
**digitisable figures with no tabulated appendix**
(`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md`, the heated-cubes row). T5's
own §12 names as *"the single largest"* uncertainty the question of **whether
the digitised curve is the `Re_H = 4440` series at all** — Fig. 5.39 carries
five overlapping series and has no abscissa to check the digitisation against.
A `P` built on a mis-identified series is a wrong number with a real citation.

### 1.2 Ahmed — **NOT ON DISK**

The primary is **Ahmed, Ramm & Faltin (1984), SAE 840300**. It is not in the
repository. `find docs/papers -iname "*ahmed*"` returns nothing; the only
"Ahmed" in `docs/papers/closure/MANIFEST.md` is *S. E. Ahmed*, a co-author of
the Sanderse 2024 ML-closure review — a different person and an irrelevant
paper. There is no `.pdf`, no `.txt` sidecar, and no manifest row.

**A case whose primary is not on disk cannot earn `P`. Ahmed cannot earn `P`
this week, and no amount of solver time changes that.**

**It is worse than absent — the number the lab has been using is unsourced.**
Three independent records already say so, all predating this memo:

- `docs/EXTERNAL_REFERENT_AUDIT.md` §4.2, RANK 2: *"the Ahmed body reference
  value has a paper but no extraction record"* —
  `models/curriculum/ahmed_25/reference.yaml:4` holds `cd: 0.285` and **no
  record states which table, figure or page it came from**. A sibling file from
  the same import commit `5336dd57` was caught being a hand-set estimate
  wearing a citation.
- `docs/EXTERNAL_REFERENT_AUDIT.md` §4.5, RANK 5, and `docs/DOCKET.md` D15: the
  **±15 % band is the lab's own `tolerance: 0.15`**, not the paper's scatter,
  and it has been written up as though it were the reference's.
- `docs/VALIDATION_INVENTORY.md` row 6: the cell was **corrected down from
  `SOLVER-BACKED`** because the cited transcript states no tier.

**Purchase, and it is a Sanaa item, not ours.** SAE 840300 is paywalled at
**roughly 30 USD** — the figure is the lab's own, recorded in
`docs/VALIDATION_INVENTORY.md` line 614 and in that file's remediation row 6
(*"Roughly 30 USD and one provenance note"*). Buying it is a purchase decision
outside this box and is reserved to Sanaa under the standing rules. **Nothing
in this memo requests it; it is named so the supervisor can put it on her desk
if he wants the Ahmed `P` reachable at all.**

| | primary | verdict | stated uncertainty | can earn `P`? |
|---|---|---|---|---|
| **Meinders** | Meinders 1998, TU Delft thesis | **ON DISK AND TITLE-VERIFIED** | 5 % mid-face / 10 % edges | **yes** (subject to the digitisation hazard) |
| **Ahmed** | Ahmed, Ramm & Faltin 1984, SAE 840300 | **NOT ON DISK** (~30 USD, Sanaa's call) | none available | **no** |

---

## 2. REFINEMENT-RATIO HEADROOM — the decisive criterion

The instrument that will grade this is `scripts/roache_triple.py`, committed at
HEAD, blob `8dee0d31e94d3f59d28658f88a4cd6df80ae8e39` (verified:
`git rev-parse HEAD:scripts/roache_triple.py` returns that blob). Four facts
from its own source that constrain the ladder design before a cell is meshed:

- **`dim` is REQUIRED and asserted** — `require_dim()` at line 186, `assert dim
  in (1, 2, 3)` at line 195, refusal not default. `representative_h` is
  `(N_ref/N)**(1/dim)` at line 199. Per VERIFICATION_CHARTER §3.1, reading a 3D
  ladder at `dim=2` **divides every observed order by exactly 1.5**. Both
  candidates are `dim=3` and both must say so with the mesh fact that
  justifies it (§3.1 rule 1: *"A closed body meshed by snappyHexMesh is
  `dim=3`"*).
- **`EQUAL_RATIO_TOL = 1.0e-9`** (line 157). This is a much sharper knife than
  it looks: *any* ladder not constructed to exactly equal ratios dispatches to
  `gci_unequal` (Celik et al. 2008 fixed point). Neither candidate's ladder is
  equal-ratio in this instrument's sense unless it is built to be.
- `FS = 1.25` (line 154), `STAGNANT_FLOOR = 0.5` (line 156).
- The states are `EXACT / OSCILLATORY / DIVERGENT / STAGNANT / CONVERGING`
  (lines 226–249); the first four are `NOT A RESULT` (line 165).

### 2.1 Meinders — the ladder, and where the tightness actually is

From `T5_PREREGISTRATION_DRAFT.md` §5.4, the **registered default ladder**
(this is the draft's INTERPRETATION 1, and the draft flags it as the one most
likely to be argued with):

| level | fluid | epoxy | **total** | first layer on cube | predicted `y+_max` |
|---|---:|---:|---:|---:|---:|
| `C` coarse | 5.1e4 | 3.0e3 | **5.4e4** | 0.128 mm | ≈ 2.6 |
| `M` medium | 2.09e5 | 1.1e4 | **2.20e5** | 0.080 mm | ≈ 1.6 |
| `F` fine | 8.57e5 | 4.6e4 | **9.03e5** | 0.050 mm | ≈ **1.0** |

**The arithmetic, computed here rather than quoted:**

```
r21 = (9.03e5 / 2.20e5)^(1/3) = 4.104545^(1/3) = 1.601124
r32 = (2.20e5 / 5.4e4)^(1/3)  = 4.074074^(1/3) = 1.597151
|r21 - r32| = 0.003973
```

**Ladder class: UNEQUAL-ratio as this instrument classifies it.** 0.003973 is
six orders of magnitude above `EQUAL_RATIO_TOL = 1e-9`, so
`triple_from_cells(..., form="auto")` dispatches `gci_unequal`, not
`gci_equal`. The draft's own prose calls the ladder equal-ratio ("1.60 and 1.61
per direction"); **that is true of the mesh recipe and false of the
instrument's classification**, and a pre-registration that names `form="equal"`
would be REFUSED at line 336. This is a small, concrete, zero-compute defect
in the draft worth passing to heat-transfer.

**Both ratios are comfortably above the r ≥ 1.3 floor** that the unequal form
inherits from Celik et al. 2008. That is good headroom — better than Ahmed's
as-built ladder by a wide margin (§2.2).

**So where is the tightness?** Not in `r`. It is that **the ladder is pinned at
both ends and cannot be moved**:

- **The floor is geometric.** The epoxy shell is 1.5 mm thick and is resolved
  with **2 / 3 / 5 cells** across the three levels (§5.4). Two cells is the
  floor — one cell through a conduction shell has no internal gradient and the
  conjugate problem stops existing. So `C` cannot be coarsened. Note also that
  2 → 3 → 5 gives shell ratios of **1.500 and 1.667**, neither of which is the
  fluid's 1.60: the solid region's refinement is **integer-quantised** over a
  1.5 mm layer and cannot be made geometrically similar to the fluid's. That is
  a real, named tightness and it is intrinsic to the geometry.
- **The ceiling is budget.** The draft's stretch ladder (§5.4, §11.2) is
  1.39e5 / 5.77e5 / **2.37e6** — the same recipe one step up, r ≈ 1.60/1.61
  again — and §11.2 states the consequence in its own heading: **"and it
  breaches"**. Under the draft's Model A the stretch **fine level alone costs
  28.86 USD, more than Sanaa's whole 25 USD ceiling**, with a wall of *"141 h
  on 4 ranks, 70 h on 8"*.

**The verdict on Meinders' headroom: there is exactly ONE viable ladder.** The
default. It works, it clears the r ≥ 1.3 floor at both gaps, and its fine level
fits — but there is no second choice, no margin to widen `r`, and no room to
add a fourth level. That is what "tight on refinement ratio" means here, and
having read the arithmetic I agree with the characterisation. **The fine level
does fit this box**: 9.03e5 cells is ~1–2 GB, against 30 GB total / 26 GB
available (measured this session), and 2308 core-min under Model B (§3).

### 2.2 Ahmed — the as-built ladder is worse than tight; it is invalid

The lab has already run an Ahmed 3D triple, **twice**, and both are on disk.
`models/curriculum/uq-studies/ahmed_25.json`:

| rung | cells | Cd (planform) |
|---|---:|---:|
| coarse | 20,621 | 0.10099 |
| medium | 45,753 | 0.08979 |
| production | 79,439 | 0.08481 |

```
r21 = (79439 / 45753)^(1/3) = 1.736251^(1/3) = 1.201908
r32 = (45753 / 20621)^(1/3) = 2.218758^(1/3) = 1.304307
|r21 - r32| = 0.102399
```

**`r21 = 1.2019` is BELOW the r ≥ 1.3 floor**, and the ladder is strongly
unequal. Its stored result is `"conclusive": false`, `"observed_order": 1.95`,
`"guards_failed": ["extrapolation_sanity"]` — the Richardson value falls
outside the measured range. The 35° sibling
(`models/curriculum/uq-studies/ahmed_35.json`, cells 20,425 / 45,813 / 79,778,
r21 = 1.2030, r32 = 1.3093) fails **two** guards, `order_window` and
`extrapolation_sanity`, at `observed_order` 3.169.

**And there is a defect underneath that nobody has named. I read the
dictionaries.**

| rung | `blockMeshDict` | snappy level | cells |
|---|---|---|---:|
| coarse | `hex (…) (42 9 25)` | 1 | 20,621 |
| medium | `hex (…) (60 13 36)` | 1 | 45,753 |
| production | `hex (…) (60 13 36)` | **2** | 79,439 |

Sources, all read directly this session:
`/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb/system/{blockMeshDict,snappyHexMeshDict}`
(cell count from `constant/polyMesh/owner` note: `nCells:20621`),
`/home/ubuntu/certonomous-runs/study-ahmed_25-medium-b37e86/…` (`nCells:45753`),
`/home/ubuntu/certonomous-runs/act7-ahmed_25-04261b/…` (`nCells:79439`).

**Coarse and medium share the refinement level and differ only in background
block density. Production alone changes the level.** Now read
VERIFICATION_CHARTER.md §3.2, "The two ways an observed order lies", second
way, describing the NACA 4412 failure verbatim:

> *"Read from the dictionaries, coarse and medium are both `level (2 3)` and
> differ only in background block density; production alone is `level (3 4)`.
> Rungs that do not share a refinement recipe are not extrapolation-comparable,
> so that number is fitted across a change of experiment and **is not a
> discretization order at all**."*

**The Ahmed 25 ladder has the identical pathology, one level lower.** The
charter names NACA 4412 as its worked case; nobody has connected the Ahmed
ladder to the same rule, and the lab's own
`verification/campaign/AHMED_BODY_RECONCILIATION.md` (2026-07-30) calls rungs 1
and 2 *"two rungs of a single grid-refinement ladder"* approvingly — while its
own field-by-field diff independently confirms the fork: it lists
`system/blockMeshDict` under **Identical** between medium and production, and
the snappy refinement level under **Different**.

This is the most dangerous shape §3.2 describes, because §3.2's rule 4 is
exactly on point: *"An order inside the credible window earns no presumption."*
Ahmed 25's stored `observed_order` is **1.95** — monotone, textbook-plausible,
and fitted across a change of experiment.

**A note on the single-`h` fiction.** Going medium → production, the cell count
rises only ×1.736 (representative `r` = 1.2019) while the **surface refinement
level doubles**, i.e. cells in the refined band went ×8 and the near-wall
spacing halved. A single `h = (1/N)^(1/3)` cannot represent a mesh that refined
by 2 where it matters and by 1 everywhere else. The instrument will compute
`r21 = 1.2019` obediently and that number is a fiction.

### 2.3 What a DEFENSIBLE Ahmed ladder would have to be, and whether it fits

Constructed rather than inherited: one parametric recipe, snappy levels
**fixed**, background block scaled by 1.6 in all three directions per level
(this is legitimate — it is what coarse → medium already did — and it is the
same discipline T5 §5.4 applies), so that cell count scales by 1.6³ = 4.096.

| level | cells | `r` to next |
|---|---:|---:|
| coarse | **3.576e5** | 1.600 |
| medium | **1.465e6** | 1.600 |
| fine | **6.00e6** | — |

`r21 = r32 = 1.600` **exactly, by construction** — the only way to satisfy
`EQUAL_RATIO_TOL = 1e-9` and use `gci_equal`.

**Does the fine level fit this box?** Marginally, and this is measured, not
assumed. The box is **16 cores, 30 GB total / 26 GB available, 297 GB free
disk** (read this session). Steady `simpleFoam` runs roughly 1–2 GB per million
cells, so 6.0e6 cells is ~6–12 GB and **fits**. It is also the practical
ceiling: a wall-resolved Ahmed at Re 2.78e6 would need ~20 M cells, ~20–40 GB,
and **does not fit in 30 GB**. So the fine level is boxed in by RAM long before
it is boxed in by dollars — a constraint the dollar ceiling alone would have
hidden.

**But the ladder above cannot be built from the meshes the lab has**, and §5
explains why: it requires prism layers, and `addLayers` is `false` on every
Ahmed mesh on this box.

### 2.4 Headroom, side by side

| | Meinders (T5 default) | Ahmed as-built | Ahmed as it would have to be |
|---|---|---|---|
| cells C/M/F | 5.4e4 / 2.20e5 / 9.03e5 | 20,621 / 45,753 / 79,439 | 3.576e5 / 1.465e6 / 6.00e6 |
| `r21` | 1.6011 | **1.2019** (below 1.3 floor) | 1.600 |
| `r32` | 1.5972 | 1.3043 | 1.600 |
| class | unequal (gap 3.97e-3) | unequal (gap 0.102) | **equal** (gap 0) |
| recipe shared across rungs? | **yes**, one parametric recipe | **NO — production forks the level** | yes, by construction |
| fine fits box? | yes, ~1–2 GB | trivially | yes, ~6–12 GB (RAM is the ceiling) |
| ladder alternatives available? | **none** — pinned floor and ceiling | — | one, and it must be built |

---

## 3. COST, in core-minutes

A proposal with no cost is DISQUALIFIED. Both are costed. Dollars at
**$0.0513/core-h** and every dollar figure below is **DERIVED, NOT MEASURED** —
this box cannot read its own billing (COMPUTE_BUDGET_CHARTER §5).

### 3.1 The measured basis, and the charter clause that judges it

COMPUTE_BUDGET_CHARTER has a section written for exactly this situation, *"A
per-cell rate borrowed across solver families is a factor wearing a basis's
clothes"* (line 375): *"a repricing crosses solver families only from that
case's own record. Where no such record exists, the item is reported UNPRICED
rather than given a number."* Applied honestly, **it splits the two candidates
the opposite way from every other criterion in this memo.**

**Ahmed has a legitimate measured basis — same body, same solver family.**
`/home/ubuntu/certonomous-runs/r4-ahmed-c3b`:

- 251,113 cells (`constant/polyMesh/owner`: `nCells:251113`), `kOmegaSST` with
  `nutkWallFunction`, 4 ranks (`system/decomposeParDict`:
  `numberOfSubdomains 4`)
- `SIMPLE solution converged`, **203 iterations**, `ExecutionTime = 47.13 s`
  (`log.simpleFoam`)

```
core-min = 47.13 s × 4 ranks / 60 = 3.1420 core-min   [MEASURED]
unit rate = 3.1420 / (251113 cells × 203 iters)
          = 6.1637e-8 core-min per cell-iteration      [MEASURED]
```

**Meinders' cost is a cross-family borrow and the charter says it should be
UNPRICED.** T5 §11's Models A and B are extrapolated from **T3**, a 2D,
single-region `buoyantBoussinesqSimpleFoam` case, and applied to a 3D,
multi-region `chtMultiRegionSimpleFoam` case, via a **2.0× penalty the draft
itself labels** *"an assumption, not a measurement"*. That is precisely the
gap the clause names. The T5 numbers are used below because they are the
registered ones and the supervisor should see them, but **they carry the
charter's own UNPRICED caveat and I am not laundering it away.**

### 3.2 Meinders — from `T5_PREREGISTRATION_DRAFT.md` §11.1, converted

| case | cells | Model B core-min | Model A core-min | Model B $ | Model A $ |
|---|---:|---:|---:|---:|---:|
| `C` coarse | 5.4e4 | 45.6 | 45.6 | 0.039 | 0.039 |
| `M` medium | 2.20e5 | 530.4 | 530.4 | 0.453 | 0.453 |
| `F` fine | 9.03e5 | **2,308.2** | **6,338.4** | 1.974 | 5.419 |
| **triple only** | | **2,884.2** | **6,914.4** | **2.466** | **5.912** |
| full ladder (+ 2D precursor, 4 arms) | | **4,350.0** | **8,382.0** | **3.719** | **7.167** |

Dollars check against the rate: 38.47 core-h × $0.0513 = $1.974 ✓.

**Uncertainty:** the A/B pair *is* the draft's uncertainty statement, and it is
a **factor 2.75 on the fine level**. Basis: T3, cross-family (§3.1). Stop
threshold registered at **20 USD / 390 core-h cumulative**, with the fine level
named as *"what is cut first"* (§11.3).

### 3.3 Ahmed — priced from the measured basis

Ladder from §2.3, at 3,000 SIMPLE iterations. (The basis run converged in 203
and the act's production rung in 154, both on layerless meshes ≤ 251k cells; a
6 M-cell layered mesh will not hold that, and L-300 / commit `ba3178e6` records
**sub-linear SIMPLE continuation**. 3,000 is a working figure, not a
measurement.)

```
floor cost = cells × 3000 × 6.1637e-8 core-min
```

| level | cells | floor core-min | ×3 conditioning | $ derived |
|---|---:|---:|---:|---:|
| coarse | 3.576e5 | 66.1 | 198.4 | 0.170 |
| medium | 1.465e6 | 270.9 | 812.6 | 0.695 |
| fine | 6.00e6 | 1,109.5 | 3,328.4 | 2.846 |
| **triple** | | **1,446.5** | **4,339.4** | **3.710** |
| + meshing (3 levels, snappy + layers) | | | **~300** | 0.257 |
| **total** | | | **≈ 4,640** | **≈ 3.97** |

**The 3× conditioning factor is an ASSUMPTION, not a measurement**, named the
same way T5 names its 2.0×. It covers prism layers, higher aspect ratios and
worse pressure-system conditioning at 6 M cells. **The floor row (1,446.5
core-min) is the only defensible lower bound; the 4,640 figure is an estimate
and should be read as one.**

### 3.4 The np=1 vs np=N decomposition row

Core-minutes are rank-seconds. Ideal scaling leaves them invariant and changes
only wall; real scaling **inflates** them by 1/η. Stated for the fine level of
each candidate:

| candidate | np | η | core-min | wall |
|---|---:|---:|---:|---:|
| **Meinders `F`** (Model B) | 1 | 1.00 (def.) | 1,962 | 32.7 h |
| | 4 | 0.85 | 2,308 | 9.62 h |
| | 8 | 0.85 | 2,308 | **4.81 h** |
| **Meinders `F`** (Model A) | 8 | 0.85 | 6,338 | 13.21 h |
| **Ahmed fine** (est.) | 1 | 1.00 (def.) | 3,328 | 55.5 h |
| | 4 | 0.85 | 3,916 | 16.3 h |
| | 8 | 0.75 | 4,438 | **9.25 h** |

Meinders' np=1 row removes the 0.85 loading already baked into the T5 table
(38.47 × 0.85 = 32.70 core-h). Ahmed's np=8 η is dropped to 0.75 because 6 M /
8 = 750 k cells per rank pushes the communication fraction up.

**A scheduling fact that binds both, and it is not a detail.** T5 §11 records
that **14+ of 16 cores are committed**; I measured 16 cores and 30 GB this
session. **np=8 is not reliably available for either candidate**, which pushes
both fine levels onto the np=4 row — 9.62 h (Meinders, Model B) or 16.3 h
(Ahmed, est.) of wall on the critical path.

**Both fit under the 25 USD pre-authorisation.** Cost does not separate these
two candidates. Everything else does.

---

## 4. WHAT EACH CASE CAN AND CANNOT EARN

Scoring: **V** code verification (exact, manufactured or correlation), **G**
CONVERGING Roache triple + GCI + observed order, **P** validation against a
public primary with a pre-registration on disk. Tiers, the five words exactly:
**HOLDS / GATE REACHED / SURVEYED / NOT HELD / NEVER RUN.**

### 4.1 The finding that reframes the whole question

The chief's gap has **two halves**:

> *(i)* "no 3D PASS against experiment with a pre-registration on disk", and
> *(ii)* "no converging Roache triple anywhere outside the thermal family".

**Meinders is IN the thermal family.** T5 is a T-family rung on the DC-cooling
spine. A CONVERGING triple on T5 closes half (i) and **does not touch half
(ii)** — it would be the thermal family's fourth triple, not the lab's first
one outside it.

**Ahmed is outside the thermal family and cannot earn `P` at all**, because its
primary is not on disk (§1.2). It can close half (ii) and **cannot touch half
(i)**.

**Neither candidate closes both halves.** This is the single most important
sentence in the memo and the supervisor's real decision is which half to buy.

### 4.2 The columns

| | Meinders (T5) | Ahmed |
|---|---|---|
| **V** | **NOT HELD this week.** No exact solution, no MMS, no correlation for local `h` on a cube. The T5 draft registers a laminar baseline `L_m` and a `Gauss linear` interface twin `H_c` — those are discrimination arms, not `V`. | **NOT HELD this week.** No exact or manufactured solution for a 3D bluff body. A correlation route does not exist for a 25° slant. |
| **G** | **GATE REACHED is realistic**, not certain. The ladder is sound (r 1.60/1.60, shared recipe, wall treatment fixed — §5). It fires only if the triple returns CONVERGING; §11.3 registers the consequence that cutting `F` on budget makes **every graded row NOT A RESULT by construction**, tally 0 of 9. | **NOT HELD this week.** The as-built ladder is invalid (§2.2) and a valid one needs a layered mesh family that does not exist (§5.2). Buildable, not in one week. |
| **P** | **GATE REACHED is realistic** *if* Sanaa rules the 12 INTERPRETATIONs and the digitisation identifies the right series. Front/top/rear faces only — **side faces are not graded** (shedding, `St` 0.093–0.10, forbidden by steady RANS + symmetry plane, T5 §12). | **NEVER RUN, and unreachable.** No primary on disk. Not a matter of effort. |
| **closes gap half** | **(i) only** | **(ii) only, and only after a mesh project** |

**Said plainly:** in one week, Meinders can realistically earn **G + a
partial P** and cannot earn V. Ahmed can realistically earn **nothing** — its
`P` is blocked on a purchase and its `G` is blocked on a mesh family. What
Ahmed can earn is the *start* of the only route the lab has to half (ii).

---

## 5. THE TURBULENCE-MODEL AND SIMILARITY HAZARD

VERIFICATION_CHARTER §3.2's second way an observed order lies is a slope fitted
across a **change of experiment**. A ladder whose `y+` crosses the
wall-function / resolved boundary as it refines is exactly that. This section
is where the two candidates separate most sharply, and the Ahmed side is
**measured**, not estimated.

### 5.1 Meinders — the wall treatment stays fixed, and that is the case's best property

Predicted `y+_max` on the cube (T5 draft §5.4): **2.6 / 1.6 / 1.0** for
`C` / `M` / `F`.

The draft's own honest statement is worth quoting because it makes the right
argument: `y+ ≤ 1` is met **only on the fine level, the level whose value is
graded**, and the coarse and medium levels sit at 2.6 and 1.6. It discloses
this as INTERPRETATION 1 rather than papering over it, and bounds the damage
three ways: *(i)* `y+ = 2.6` is still deep inside the viscous sublayer, so **no
wall function is active anywhere on the ladder** and the SST low-Re treatment
is **continuous across all three levels**; *(ii)* achieved `y+` is **measured
per case, per face, and printed beside every row**; *(iii)* the alternative
that would give `y+ ≤ 1` everywhere — fixing the first layer at 0.050 mm and
refining tangentially only — produces a triple that **does not contain the
wall-normal discretisation error at all**, and a GCI that therefore understates
it.

That third point is the T1b lesson applied correctly, and it is the reason the
draft refines **the first wall layer along with everything else**. This is the
right design and it is the opposite of the trap.

**One caveat I must state: these `y+` values are PREDICTED, not measured.** The
T5 case has never been built (`find verification/runs/T-family -maxdepth 1
-iname "*T5*"` returns nothing — the draft records that check itself). The
wall-treatment argument is sound in design and **unverified in fact**.

**Verdict: wall treatment stays fixed across the Meinders ladder. No boundary
is crossed. §3.2's second failure mode does not fire.**

### 5.2 Ahmed — it cannot stay fixed, and the arithmetic is measured

`cases/mega-batch/F10_YPLUS_FIX.md` carries **measured** `y+` on this exact
body, this exact solver and these exact meshes. The lab's own gate is
`AHMED_YPLUS_LOW = 30.0`, `AHMED_YPLUS_HIGH = 500.0`, applied to the **average**.

| rung | cells | Re | `y+` min | `y+` max | `y+` avg |
|---|---:|---:|---:|---:|---:|
| medium (ref 2) | 45,760 | 2.727e6 | 111.39 | 1,409.14 | 438.99 |
| production (ref 3) | 79,439 | 2.810e6 | **46.68** | **1,766.31** | 334.43 |
| production (ref 3) | 79,439 | 3.990e6 | 67.11 | 2,508.32 | 463.89 |

The graded ladder runs at `magUInf 40`, `lRef 1.044`, `nu 1.5e-05`
(`/home/ubuntu/certonomous-runs/r4-ahmed-c3b/system/controlDict`,
`constant/transportProperties`), i.e. **Re = 2.784e6** — between rows 1 and 2.

**Finding A — `addLayers` is `false` on every Ahmed mesh the lab has.**
Confirmed in `system/snappyHexMeshDict` of both
`/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb` and
`/home/ubuntu/certonomous-runs/r4-ahmed-c3b`. Every Ahmed mesh is a **layerless
isotropic** snappyHexMesh. The turbulent boundary layer at this Re is
δ ≈ 0.37·L·Re^(−1/5) ≈ **20 mm**; the production rung's first cell centre is
~22 mm. **The entire boundary layer sits inside one cell.**

**Finding B — the `y+` spread on a single mesh is wider than the wall
function's entire validity window.** On the production rung:

```
measured y+ spread   = 1766.31 / 46.68 = 37.84
validity window      =  500.00 / 30.00 = 16.67
ratio                = 37.84 / 16.67   =  2.27
```

**The body's own `y+` distribution is 2.27× too wide to fit inside the log
layer.** At every level, some fraction of the wetted area is outside the wall
function's validity — and refining changes **which** fraction. That is a change
of experiment between rungs, and it is §3.2's second failure mode firing on
measured data.

*Honest limit on Finding B:* the 37.84 spread mixes wall-shear variation over
the body with surface-cell-size variation on an isotropic mesh. The record does
not decompose it and **I have not decomposed it**. The conclusion survives
either way, because 37.84 > 16.67 regardless of the split — but the *remedy*
depends on the split, and adding prism layers fixes only the cell-size half.

**Finding C — the treatment demonstrably moves along the existing ladder.**
`y+` avg goes **≈627 (coarse, scaled from the measured medium by the background
ratio 0.2486/0.174) → 438.99 (medium, measured) → 334.43 (production,
measured)**, while `y+` min goes **111.39 → 46.68**. One more refinement level
drives `y+` min below 30 — **below the lab's own gate floor and into the buffer
layer**, where `nutkWallFunction` switches behaviour. Any credible Ahmed fine
level crosses that boundary explicitly.

**Verdict: the wall treatment CANNOT stay fixed across an Ahmed ladder built
the way this lab builds Ahmed meshes. That is a finding, not a detail**, and it
is the single most likely way this campaign would produce a beautiful,
meaningless order — which is precisely what the existing `observed_order = 1.95`
already is.

**What would be required** (scoping, not a plan): `addLayers true` with
`relativeSizes true` so layers scale with the background and the ladder stays
geometrically similar; layer thickness targeted so `y+` min > 30 at the finest
level; and `y+` measured per face per level and printed beside every row, as T5
already requires. Note that `relativeSizes false` — an absolute first-layer
thickness held fixed across the ladder — reproduces the T1b DIVERGENT failure
exactly. Snappy layer addition on a 25° slant with a sharp trailing edge is the
most failure-prone step in the OpenFOAM meshing stack. **This is a mesh
development project, not a consolidation-week campaign.**

---

## 6. RECOMMENDATION

### 6.1 The recommendation

**For the cfd team's consolidation-week 3D campaign: take AHMED, scoped
explicitly and only as a `G`-and-mesh-capability campaign — NOT a `P`
campaign — and let Meinders/T5 remain heat-transfer's rung, run by them, on
their spine, when Sanaa rules the 12 INTERPRETATIONs.**

The reasoning, and it turns on §4.1 rather than on any single criterion:

1. **Meinders wins nearly every criterion in this memo and still cannot close
   the half of the gap that is cfd's to close.** T5 is a T-family rung. A
   CONVERGING triple on it is the thermal family's next triple. Half (ii) —
   *"no converging Roache triple anywhere outside the thermal family"* — would
   stand exactly where it stands now.
2. **Ahmed's `P` is unreachable this week no matter what we do** (primary not
   on disk, ~30 USD, Sanaa's call). Scoping the campaign to `G` therefore
   **costs nothing that was reachable** and removes the temptation to grade
   against `cd: 0.285`, a number three separate lab records already say has no
   extraction route.
3. **The Ahmed defect found in §2.2 is worth the week on its own.** The lab has
   an `observed_order` of 1.95 on record, monotone and plausible, fitted across
   a refinement-recipe fork that reproduces VERIFICATION_CHARTER §3.2's own
   worked NACA 4412 failure. That is a live, unnamed defect in a published
   family. Naming it and replacing the ladder with a shared-recipe one is
   verification work of exactly the kind this lab exists to do.
4. **Ahmed has the only legitimate measured cost basis of the two** (§3.1):
   same body, same solver family, on disk, 6.1637e-8 core-min per
   cell-iteration. Meinders' cost is a cross-family borrow that
   COMPUTE_BUDGET_CHARTER's own clause says should be reported UNPRICED.
5. **It is cfd's territory.** Recommending Meinders would mean the cfd team's
   3D campaign is another team's rung, blocked on another team's ruling and on
   Sanaa's desk.

**What must be pre-registered as the expected outcome, so it is not discovered
later:** the honest prediction is **`G` = GATE REACHED at best, and a
documented `NOT A RESULT` at worst**, with the mesh-family capability and the
§2.2 defect as the deliverables that survive either way. VERIFICATION_CHARTER
§8 — failed gates ship as documented failures — is the frame, and the
pre-registration must say so **before** compute, not after.

### 6.2 The losing case's strongest argument, stated fairly

**Meinders is the better case on the merits and I want that on the record
rather than softened.**

Its primary is on disk and I title-verified it myself from the rendered scan,
with a **stated experimental uncertainty** (5 % / 10 %) — which is more than
most references in this lab carry, and strictly more than Ahmed will have even
after a 30 USD purchase, since nobody has yet found the extraction route in
that paper. Its ladder clears the r ≥ 1.3 floor at both gaps with a shared
parametric recipe. Its wall treatment is continuous across all three levels
with no wall function active anywhere — the single hazard that §5 shows kills
Ahmed simply does not exist for it. It has a **73 kB pre-registration draft
already written**, with 12 decisions explicitly labelled and collected for
review, a registered stop threshold, a planted-positive mesh check, and §12's
honest list of what the rung cannot see. It is, by a distance, the more mature
and more defensible artifact.

**The strongest form of the argument for choosing it anyway:** half (i) of the
gap — *a 3D PASS against experiment with a pre-registration on disk* — is the
half that produces a **wall credential**, and it is the half the lab has been
unable to close for its entire existence. Half (ii) is an internal
verification property with no external referent. If the consolidation week is
judged on what the lab can *show*, Meinders is the answer and Ahmed is a week
of mesh development with a documented failure at the end of it.

**Why I still do not recommend it:** that argument is right about the value and
wrong about the owner. Half (i) via T5 is **already the heat-transfer team's
next spine item** (H-2 position 2). It does not need the cfd team to take it,
and the cfd team taking it would duplicate a rung, annex a live configuration
decision, and leave half (ii) untouched by anyone. **The two halves are best
bought in parallel by the two teams that own them, and this memo's
recommendation is the cfd half.**

### 6.3 Conditions under which the recommendation flips

Any one of these flips it, and each is checkable:

1. **Sanaa buys SAE 840300** (~30 USD) **and the extraction route for a
   reference `Cd` is recorded from it.** Ahmed then has a real primary, `P`
   becomes reachable, and the case is worth a full `V/G/P` campaign rather than
   the scoped one — the scoping in §6.1 exists *because* the primary is absent.
2. **Heat-transfer rules a Meinders configuration other than the single cube**
   — the row (thesis Ch. 6), the tandem (Ch. 7) or the 4×4 matrix (Ch. 8). Every
   Meinders number in this memo is for the **single cube** and would be
   superseded; the matrix in particular is where the rack recirculation and the
   adiabatic-reference-temperature machinery actually live, and its cost is not
   costed anywhere I could find.
3. **Heat-transfer declines or defers T5** (e.g. Sanaa's 12 INTERPRETATIONs
   stay unruled past the consolidation week). Half (i) is then unowned, and the
   cfd team taking Meinders stops being duplication and starts being cover.
   **This is the most likely flip and the supervisor should check it with
   heat-transfer before ruling.**
4. **A scoping probe shows snappy cannot build a layered Ahmed family** with
   `y+` min > 30 at the fine level and geometric similarity across three
   levels. Ahmed's `G` is then not merely hard but unreachable, and the
   campaign has no deliverable. **This is cheap to test and should be tested
   first** — it is a meshing probe, no solver, and it is the deciding fact for
   the whole recommendation.
5. **A third case beats both.** Flagged, not pursued, because selecting it is
   not this memo's remit:
   `docs/papers/benchmark_test_cases/pinelli_uhlmann_sekimoto_kawahara_jfm2010_square_duct.pdf`
   — Pinelli, Uhlmann, Sekimoto & Kawahara (2010), *"Reynolds number dependence
   of mean flow structure in square duct turbulence"*, JFM **644**, 107–122,
   doi:10.1017/s0022112009992242, with a **populated `.txt` sidecar** (title
   verified from the sidecar's own citation block). It is 3D, **outside the
   thermal family**, its primary is **on disk**, and it is DNS data. It is the
   only artifact I found that could touch **both** halves of the gap. Two
   honest caveats: a linear eddy-viscosity closure produces **zero** secondary
   flow of Prandtl's second kind, so a `P` gate on the secondary-flow structure
   is a near-certain GATE FAIL by construction — which VERIFICATION_CHARTER §2c
   may well read as a row that cannot discriminate; and its HARD criterion under
   CASE_SELECTION §2 needs arguing, since there is no separation. **Recommend the
   supervisor task a half-day scoping read before the week is committed.**

### 6.4 One thing the supervisor should check that I could not

**Does the Meinders cube clear the CASE_SELECTION floor?** §3 lists **cube**
among the eight canonical cylinder-class calibration bodies, and §2's clause
*"hardness is a property of the regime, not of the shape"* plus the §8 ruling
say the shape list is guidance, not the test. My read is that a heated
wall-mounted cube at `Re_H` ≈ 4440 with a horseshoe vortex, three separating and
reattaching shear layers, an arc wake vortex and a conjugate solid shell is
**HARD criterion 1, 3D separated flow**, and clears the floor comfortably. But
§9 is explicit that this judgement *"stays a person's"* and is not mechanizable.
It is not mine to make, and a supervisor will be asked it. **Ahmed is HARD
criterion 1 without argument** and `docs/DOCKET.md` records three 2026-08-04
entries already stating exactly that for the 25° body.

---

## Appendix — files consulted, by absolute path

**Meinders / T5**
`/home/ubuntu/Certonomous/docs/campaigns/T-family/T5_PREREGISTRATION_DRAFT.md` (§2, §5.4, §11.1–11.3, §12)
`/home/ubuntu/Certonomous/docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` (rows S11, C14 — untracked, this session)
`/home/ubuntu/Certonomous/docs/campaigns/T-family/T_FAMILY_INDEX.md`
`/home/ubuntu/Certonomous/docs/THERMAL_CAPABILITY_STATE.md`
`/home/ubuntu/Certonomous/docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf` (sha256 `36c89a54…`, title-verified pp. 1 and 3)
`/home/ubuntu/Certonomous/docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.txt` (**stub — 281 bytes, all form-feeds**)
commit `4cc8c22c`

**Ahmed**
`/home/ubuntu/Certonomous/models/curriculum/uq-studies/ahmed_25.json`
`/home/ubuntu/Certonomous/models/curriculum/uq-studies/ahmed_35.json`
`/home/ubuntu/Certonomous/verification/campaign/AHMED_BODY_RECONCILIATION.md`
`/home/ubuntu/Certonomous/cases/mega-batch/F10_YPLUS_FIX.md` (measured `y+` table)
`/home/ubuntu/Certonomous/docs/EXTERNAL_REFERENT_AUDIT.md` §4.2, §4.5
`/home/ubuntu/Certonomous/docs/VALIDATION_INVENTORY.md` rows 6, 340, 341, 614, 733
`/home/ubuntu/Certonomous/docs/DOCKET.md` D15
`/home/ubuntu/certonomous-runs/r4-ahmed-c3b/` (cost basis: `log.simpleFoam`, `log.checkMesh`, `system/{controlDict,decomposeParDict,snappyHexMeshDict,blockMeshDict}`, `constant/polyMesh/owner`)
`/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb/`, `/home/ubuntu/certonomous-runs/study-ahmed_25-medium-b37e86/`, `/home/ubuntu/certonomous-runs/act7-ahmed_25-04261b/` (ladder recipes)

**Instrument and charters**
`/home/ubuntu/Certonomous/scripts/roache_triple.py` (blob `8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`)
`/home/ubuntu/Certonomous/docs/charters/VERIFICATION_CHARTER.md` §1, §2, §2a–§2e, §3.1, §3.2, §9
`/home/ubuntu/Certonomous/docs/charters/CASE_SELECTION_CHARTER.md` §2, §3, §4, §8, §9, §10
`/home/ubuntu/Certonomous/docs/charters/COMPUTE_BUDGET_CHARTER.md` §2, §5, the borrowed-rate clause (line 375)
`/home/ubuntu/Certonomous/docs/standards/MESH_STANDARD.md` (§3 gates; it carries **no** `y+` or refinement-ratio clause — checked, so the `y+` reasoning in §5 rests on the verification charter and on measured data, not on the mesh standard)

**Third candidate flagged in §6.3(5)**
`/home/ubuntu/Certonomous/docs/papers/benchmark_test_cases/pinelli_uhlmann_sekimoto_kawahara_jfm2010_square_duct.pdf` + populated `.txt` sidecar
