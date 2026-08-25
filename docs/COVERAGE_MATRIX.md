# The lab coverage matrix — one row per case, three columns, one tier

**Owner:** verification team. **Status: DRAFT, IN CONSTRUCTION — not yet a lab
record.** Rows are landing as they are audited; a row is not in this matrix until
this team has spot-checked its load-bearing evidence itself. Until this line is
struck, no other document may cite a tier from this file.

**Created** 2026-08-24 by the verification supervisor, at the chief's dispatch, as
the consolidation-week deliverable.

---

## 0. Provenance of the brief — read this before the rubric

**The three-column rubric and the five tier words below are the CHIEF'S
RECONSTRUCTION of Sanaa's directive. They are NOT her verbatim words, and this
document does not represent them as such.** The chief stated the reconstruction in
those terms when dispatching the work. Sanaa has not ruled on the rubric, and if
she reads it differently the rubric changes and every tier in this file is
re-derived from the same evidence — which is why each row carries its evidence and
not only its tier.

This matters more than a footnote. The whole point of the matrix is that a reader
can check it. A rubric whose provenance is fuzzy produces tiers nobody can audit,
and the tier is the only thing most readers will carry away.

---

## 1. The rubric, stated once and applied uniformly

| column | what it asks | scores green ONLY when |
| --- | --- | --- |
| **V** — code verification | Is the CODE verified against something with a known answer? | there is an **exact solution**, a **manufactured solution**, or a **correlation**, and the case was compared against it |
| **G** — grid convergence | Is the DISCRETISATION error quantified? | there is a **CONVERGING Roache triple**, with **GCI at Fs = 1.25** and an **observed order p**. Per CLAUDE.md rule 5, a triple that is DIVERGENT, STAGNANT, OSCILLATORY or EXACT is not G, and a GCI is never quoted when the three values are not monotone |
| **P** — validation | Is the RESULT compared against the world? | against a **public primary source**, with the **pre-registration ON DISK** |

**Tiers — exactly these five words, no synonyms:**

| tier | assigned when |
| --- | --- |
| **HOLDS** | V and G and P all green, under frozen pre-registrations |
| **GATE REACHED** | missing exactly one of V / G / P — **and the row names which** |
| **SURVEYED** | breadth evidence, ungated |
| **NOT HELD** | an honest FAIL, or a blocker |
| **NEVER RUN** | no solver has run in this class |

### 1.1 A vocabulary collision this matrix must not create

**`GATE REACHED` appears in two different vocabularies in this lab and they mean
different things.** In CLAUDE.md rule 1 and `VERIFICATION_CHARTER.md` §2 it is a
**gate VERDICT**: the gate was reached and the claim it serves is not thereby
established. Here it is a **matrix TIER**: the row is missing one of V / G / P.

A row can carry the verdict `PASS` and the tier **GATE REACHED** at the same time,
and that is not a contradiction — it means the gate that was armed passed, and the
matrix is recording that a different column was never armed at all. The dafoam
contribution flagged this collision independently (§0.1 of its file) and it is
recorded here because a reader who conflates the two columns will read this matrix
as saying the opposite of what it says.

**Every row below therefore prints the gate VERDICT and the matrix TIER as two
separate cells.** Where a row's tier is GATE REACHED, the missing letter is named
in the cell. A tier cell that says only "GATE REACHED" without naming the missing
letter is a defect in this file, not a row.

---

## 2. Why the family contributions could not be transcribed — the rubric divergence

Four families were asked for `MATRIX_CONTRIBUTION.md` rows. Three exist.
**Each of the three defined V, G and P differently, and differently from the
chief's rubric above.** Their tiers are therefore **claims scored on another
scale**, and transcribing them would have produced a matrix whose tier column
meant a different thing in every block of rows.

| family | file | its V | its G | its P |
| --- | --- | --- | --- | --- |
| closure | `cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md` (tracked, `a42fd634`) | a verification instrument **demonstrated able to fail** — planted-zero, identity test, independent re-derivation | a **pre-registered NUMERIC gate that could have failed**, frozen by sha before the run | a **pre-registered PREDICTION**, made before the run and graded |
| dafoam | `cases/dafoam/MATRIX_CONTRIBUTION.md` (**untracked on disk**) | the **finite-difference-versus-adjoint check** (`DAFOAM_CHARTER.md` §9) | *(not a column; the family prints a lab-verdict column and a matrix-tier column instead)* | *(as above)* |
| heat-transfer | `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` (**untracked on disk**) | **a converged Roache triple with an observed order** | a **pre-registered gate with a threshold**, and what it returned | the reference **ON DISK and title-page verified** |

Read down that table: **closure's V is an instrument-integrity test, dafoam's V is
a gradient consistency check, and heat-transfer's V is grid convergence — which is
the chief's G, not the chief's V.** None of the three is the chief's V (exact
solution, manufactured solution, or correlation). Under the chief's rubric,
heat-transfer's V-green rows are G-green rows, and their V column is unfilled.

**Consequence, stated plainly because it is the single most important sentence in
this file:** a family's `HOLDS` is not this matrix's `HOLDS`. Every tier in section
3 was **re-derived by the verification team from the underlying artifacts**, not
lifted. Where a re-derived tier is weaker than the family's claimed tier, the row
says so and names the evidence, so the family can contest it against the same
artifacts.

Two of the three families anticipated exactly this and said so in their own files —
dafoam's §0.2 states its mapping is "this lane's proposal and the verification
supervisor may replace it", and heat-transfer's §0.2 defines its tiers "so they are
liftable". That is the right instinct and it is why the re-scoring is cheap.

### 2.1 Contribution files that are ON DISK BUT UNCOMMITTED

`cases/dafoam/MATRIX_CONTRIBUTION.md` (414 lines) and
`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` (730 lines) were written by lanes
that were killed by the session usage limit at ~20:50Z on 2026-08-24. **Both files
survived on disk and are untracked.** They were reported upward as lost; they are
not lost. They are their families' to commit, not this team's — this file cites
them by path and quotes them, and does not commit another team's work.

---

## 2.2 Three gaps in the rubric, and this team's rulings on them

The chief's rubric is three sentences long, which is a virtue. Applying it to real
rows exposed three places where it does not say what to do. **Each is ruled here,
by the verification supervisor, and each ruling is disclosed as a ruling so the
chief or Sanaa can overturn it.** A rubric gap filled silently is how a matrix
starts meaning something other than what it says.

### ~~Ruling 1 — a row missing MORE THAN ONE of V / G / P is still `GATE REACHED`, and names them all~~ — **STRUCK 2026-08-25, see the amendment below**

The chief's wording is *"GATE REACHED (missing one of V/G/P — name which)"*. Rows
exist that are missing two. The four other tiers do not fit them: `SURVEYED` means
*ungated*, and a row that armed a pre-registered gate and passed it is not ungated;
`NOT HELD` means the answer was no, and it was not; `NEVER RUN` is false.

**Ruling: `GATE REACHED` is assigned when AT LEAST ONE of V / G / P is missing, and
the row names EVERY missing letter.** `SURVEYED` is reserved for rows with no
pre-registered gate at all. This is a minimal widening of the chief's wording in the
only direction that does not force a row into a tier that says something false about
it, and naming every missing letter means the widening costs the reader nothing —
a row missing two is visibly weaker than a row missing one, on the face of the cell.

### Ruling 1 — AMENDED 2026-08-25, before any row was entered under it

**The original Ruling 1 above is STRUCK.** It is left standing, unrewritten, because
this file's own §1.1 discipline is worth more than a tidy page and because a reader
must be able to see what was ruled and why it changed.

**What broke it.** The first audit came back with **24 dafoam rows missing ALL THREE
of V, G and P**, not one. Under the struck ruling those 24 would have been tiered
`GATE REACHED` — the same word as a row missing exactly one letter. That flatters
them, and it flatters them in the direction of the lab's own interests, which is the
direction a rubric must never drift.

**Ruling 1, as it now stands:**

- **`GATE REACHED` — missing EXACTLY ONE of V / G / P**, and the row names which.
  This is the chief's wording, restored unchanged.
- **Missing TWO OR THREE → `SURVEYED`**, and the row names every missing letter.
- **`SURVEYED`'s gloss is sharpened to make this honest:** *breadth evidence,
  ungated **on the V / G / P axes***. A `SURVEYED` row may well have armed a frozen
  pre-registered lab gate and passed it — many do. What `SURVEYED` asserts is that
  the gate it passed tested **neither code verification, nor grid convergence, nor
  validation against a primary source**. That is a real distinction and it is the
  one the matrix exists to draw.

**A tier is not a grade on the team that produced the row.** A `SURVEYED` row can be
better instrumented, better frozen and better reproduced than a `GATE REACHED` one —
closure's frozen-field ceiling (§3.2 below) is exactly that. The tier says what
**kind** of evidence the row is, not how well it was done.

### Ruling 2 — an UNSETTLED observed order still scores `G`; it does not license the word "asymptotic"

The rubric asks G for *"a CONVERGING Roache triple, with GCI at Fs = 1.25 and an
observed order p"*. It does not ask that p have **settled**. `VERIFICATION_CHARTER.md`
§3.4 is directly on point and holds the two apart:

> *"A conclusive ladder has earned a quotable band. It has not thereby shown that it
> is in the asymptotic range, and the two are separate claims with separate
> evidence."*

**Ruling: `G` is green on a CONVERGING triple with a GCI at Fs = 1.25 and a quoted
observed order, whether or not the order has settled** — the band is what the guards
certify, and the band is what G is asking about. **But §3.4 also requires the record
to state which of the two claims it is making, so every G-green row in this matrix
additionally carries an `order settled?` disclosure, and a row whose order is still
moving quotes the sequence.** No row in this file may be called asymptotic on the
strength of a green G.

This is the ruling that keeps the flat plate scorable: under the opposite ruling the
lab's best verification result would score no G at all, which would be a statement
about the rubric rather than about the plate.

### Ruling 3 — a benchmark reached THROUGH a secondary source does NOT make `P` green

This is the hard one, it is the one the lab's single cleanest gate PASS turns on, and
**the charter has already settled it twice.** `VERIFICATION_CHARTER.md` §6b's mapping
table adjudicates two rows of exactly this shape and both come out the same way:

- F5a, where no primary reporting the value could be found and the lab fell back to a
  secondary reproduced as a figure in a 2014 thesis, is recorded as **`NOT OBTAINED`
  as a primary. What is held is SECONDARY**, and the row is graded *BANDED and LOWER
  CONFIDENCE*.
- F7, where no tabulated Martin & Moyce (1952) data could be located and the lab
  digitised a 2021 figure at 600 dpi, is likewise **`NOT OBTAINED` as a primary**.

**Ruling: `P` is green only against a source the lab HOLDS and can read. A value that
reaches the lab through a third party is `SECONDARY`, and `SECONDARY` does not score
P.** The reference is recorded as `NOT OBTAINED` as a primary, in those two words,
with §6b's four fields — what is missing, which row it blocks, why it was not
obtained with the availability check named and dated, and the acquisition path with
its price.

**What this ruling does NOT do, and §6b says so in its own words:** *"`NOT OBTAINED`
is a statement about a document, never about a verdict, and it changes no tier by
itself."* No gate verdict anywhere in this lab moves because of this ruling. A row
whose gate returned `PASS` still returned `PASS`; the matrix is recording that a
different column was never filled. **The verdict column and the tier column say
different things and §1.1 is why they are printed separately.**

### A consequence worth stating in advance of the rows

Ruling 3 bears directly on **K0c**, the laminar square cavity, which the
heat-transfer contribution calls *"this family's ONE CLEAN GATE PASS"* — 0 of 20
graded rows failed, largest deviation **1.139 %** on a **3 %** band, **41.73
core-min**. That family's own file discloses that K0c's reference is **de Vahl Davis
(1983) reached through Han and Xie (2019) Table 3**, the original **paywalled and
never read**. Under Ruling 3 that is `SECONDARY` and P is not green. The `PASS`
stands; the tier is under audit and this team has not yet entered it.

**The disclosure is the family's own, made in its own contribution, unprompted.**
That is the behaviour this lab is trying to produce, and it should be read as the
record working rather than as a row failing.

---

## 3. The matrix

**PARTIAL — dafoam and closure audited 2026-08-25; heat-transfer, cfd and
ansys-verification still under audit.** Nothing is entered until this team has
checked the row's load-bearing evidence against the artifacts itself.

### 3.1 The headline, before the rows

**Across the two families audited so far — 58 dafoam rows and 6 closure rows, 64
rows in all — there is not one HOLDS row, and the `G` column is empty on every
single one.**

Neither family has ever computed a grid convergence index. The token `GCI` appears
in **zero** files under `cases/dafoam/`, `docs/dafoam/` and
`cases/RANS_LES_closure_models/`; so does `Roache`; no observed order `p` is
reported anywhere in either tree. Neither contribution contains the word
`CONVERGING`.

Two traps a later reader will otherwise fall into, recorded now:

- **Every `Richardson` hit in the dafoam tree is something else.** It is either
  Richardson extrapolation over **finite-difference step size**
  (`/home/ubuntu/Certonomous/cases/dafoam/rotation_branch/independent_check/verify_rotderiv.py:60`)
  or a Richardson **preconditioner sweep** (`globalPCIters` / `localPCIters`,
  `/home/ubuntu/Certonomous/cases/dafoam/R5_ADJOINT_CONDITIONING.md:335`). Neither is
  grid Richardson extrapolation, and reading either as grid convergence is a
  category error this file names in advance so nobody makes it.
- **DAFoam's only three-level grid family is A3** at 21,840 / 42,120 / 79,560 cells,
  and **its finest level `GATE FAIL`ed** — `reason −3` at 4,000 iterations, 1.31×
  residual reduction, memory comfortable at 11.65 of 22 GiB
  (`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md` §2d).
  Under CLAUDE.md rule 5 that triple could not be graded even if someone tried.
- **Closure has no grid family at all** — fixed benchmark meshes throughout — and
  its own frozen pre-registration says so, verbatim at
  `/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md:313-314`:
  *"no `Re` sweep, no mesh-refinement study. A converged answer on one mesh is not a
  grid-converged answer."*

**The G column is a heat-transfer and cfd capability that neither of these two
families has ever exercised.** That is a structural fact about the lab, it is
cheap to state and expensive to have discovered late, and it is the first
confirmation of the inventory's standing fact (§4).

### 3.2 dafoam — 58 rows, 0 HOLDS

Source: `/home/ubuntu/Certonomous/cases/dafoam/MATRIX_CONTRIBUTION.md` (untracked on disk).

**The family's V standard is the finite-difference-versus-adjoint check**, landed as
a family standard at `/home/ubuntu/Certonomous/docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md`
(at HEAD, last changed `4a6ea0b8`). **It is not one of the chief's three V
instruments.** A finite difference is a second numerical approximation of the same
discrete object; it is not an exact solution, not a manufactured solution, and not a
correlation. The family says so itself in §3.1 of its file — *"This family has NO
exact solution and NO manufactured solution for the quantity it verifies… The entire
V column of every row above therefore rests on finite differences"* — and §3.2 adds
that no complex-step build exists and forward-AD does not reproduce the plain primal
(D460).

**So `V` is absent on all 58 dafoam rows, `G` on all 58, and `P` on all 58.** All 24
rows the family tiers `HOLDS` are **`SURVEYED`** under Ruling 1 as amended, each
missing all three letters. **dafoam contributes zero HOLDS and zero GATE REACHED
rows to this matrix.**

**This is escalated, not decided: whether FD-vs-adjoint is admitted as a fourth `V`
instrument is a rubric widening and is the chief's or Sanaa's call, never this
team's.** It is not a small question — **23 of the 24 rows change tier if it is
admitted.** This team's position, offered as input and not as a ruling: if it were
admitted, it should be admitted only for the **SHIPPED** rows, because **code
verification whose instrument cannot be re-run by anyone outside this box is a
self-consistency check rather than verification**. The chief's V asks whether the
code gets the right answer to a problem whose answer is known independently of this
box, and a number no reader can regenerate cannot discharge that. On the family's
own §3.3 standing fact — *"a reader who installs DAFoam 5.0.0 with OpenFOAM v2506
and PETSc 3.15.5 gets the SHIPPED rows and none of the PATCHED ones"* — **only 6 of
the 24 would survive**: G-03, G-16, G-19, G-27, O-04, O-06.

**The two rows that reach for the outside world, and why both still fail `P`:**

| row | what it reaches for | source held? | pre-registration? | `P` |
| --- | --- | --- | --- | --- |
| **G-16** | A3 399k Cp vs **AGARD AR-138 Case 2308** | **YES, and it is the strongest external artifact in either family.** `/home/ubuntu/Certonomous/cases/dafoam/ladder-a/logs_A3/case_2308.dat`, 22,695 B, **tracked in git**, title-verified from its own content: `TITLE = "M6 WING - SURFACE PRESSURE DISTRIBUTIONS"`, `Run= 308, Mach= 0.8395, Alpha= 3.06, Re= 11.72x10**6"` — genuine Schmitt & Charpin (1979) experimental surface pressure via the NASA-TMR mirror | **NO.** No `PREREGISTRATION.md` exists in `A3/grading_confirmation/`, and no pre-registration anywhere in `cases/dafoam/` registers a Cp band against AGARD 2308. The record states RMS 0.0128–0.0265 (pressure) and 0.0491–0.1139 (suction) and then writes *"Verdict: PASS"* — **numbers reported, then a verdict written, with no threshold that could have failed** | **NO** |
| **G-33** | B2 duct, 0.1290 vs a "published floor" 0.1288 (+0.16 %) | **Qualified NO.** The origin is the public benchmark `github.com/rmcconke/closure-challenge-benchmark` at `deb91557…`, cloned at `/home/ubuntu/closure-challenge-benchmark/`. But the cited file `closure_challenge_rans_floor.json` is **not in the clone**; its only live copy is `/home/ubuntu/Certonomous/research/closure/data/closure_challenge_rans_floor.json`, whose own header says every number is **regenerated by the lab**. **The record itself disclaims the framing**: *"Neither the paper nor the submission's description document publishes an uncorrected-SST-only numeric score… No paper-stated duct-baseline figure was available"* — what was done is a **code-to-code reproduction of the benchmark's own shipped baseline, re-run from the authors' own case files** | **NO.** No B2 pre-registration exists anywhere in `cases/dafoam/`; the 0.16 % was measured and then narrated | **NO** |

**On G-16 the record is better than the tier and deserves saying so:** the artifact is
real, held, tracked and title-verified. What it lacks is a band frozen before the
comparison, and that cannot now be supplied for a run already made. **If the chief
wants one dafoam row promoted, G-16 is the candidate — on a re-run under a frozen
pre-registration, not on the run that exists.**

**One citation defect, verdict-neutral:** `A3/grading_confirmation/RESULTS.md:44`
cites the AGARD file as `../../logs_A3/case_2308.dat`, which resolves to
`cases/dafoam/logs_A3/` — **a directory that does not exist**. The file is one level
up, at `cases/dafoam/ladder-a/logs_A3/`. The number is sound; the pointer is off by
one directory. Owed to dafoam as a dated correction.

### 3.2a The dafoam census is wrong in every cell, and its own derivation command is broken

This is a defect in an instrument, not in a row, so it is recorded separately.

The contribution's §4.1 census table reports **51** rows. The command the document
itself prints to derive that table returns **`TOTAL 58`**. §4.2's own honesty clause
settles which wins — *"where the two disagree the command wins and the table is
corrected, not the command"* — so the answer is **58**, and **the prose sentence
"43 + 15 = 58" and "the census counts every id exactly once" were both RIGHT all
along. The table was the error.** All 43 G ids and all 15 O ids are present, none
missing, none duplicated, and every row matches the pattern.

**Note the direction.** D414 and D420 were **inflated** denominators. This one is
**deflated** — 7 rows short — and it understates the family. The corrected census:

| tier *(as dafoam tiers them, not as this matrix does)* | SHIPPED | PATCHED | OTHER | true total | §4.1 claimed |
| --- | --- | --- | --- | --- | --- |
| HOLDS | 7 | 16 | 1 | **24** | 18 |
| GATE REACHED | 2 | 0 | 0 | **2** | 2 |
| SURVEYED | 2 | 7 | 0 | **9** | 8 |
| NOT HELD | 6 | 8 | 0 | **14** | 14 |
| NEVER RUN | 4 | 4 | 1 | **9** | 9 |
| **column total** | **21** | **35** | **2** | **58** | 23 / 27 / 1 = 51 |

**Three defects in the command itself, and anyone lifting this census must not
re-run it as printed:**

1. **Field shift.** The command reads the tier from `$9` under `-F'|'`, and **five
   rows carry literal `|` inside their measured-statistic cell** — G-23's
   `max |FD_stock − FD_patched|`, O-05/O-07/O-08's `|CL − 0.5|`, and O-10's
   `‖Δshape‖_∞` plus `|ΔAoA|`. Every field after the pipe shifts, and the command's
   printed tier keys come out as sentence fragments rather than tier words. **Reading
   `$(NF-3)` instead of `$9` is field-shift-immune** — all five extra pipes fall
   before the tier column — and recovers clean tier words on all 58 rows.
2. **The command contradicts the document's own bucketing rule.** §4 rules that the
   `‡` rows count as PATCHED. The ternary tests `/SHIPPED/` **before** `/PATCHED/`,
   and **G-07's toolchain cell contains the string "SHIPPED-equivalent"**, so the
   command buckets G-07 as SHIPPED. The rule is applied to 2 of its 3 target rows by
   the document's own instrument.
3. **`OTHER` is 2, not 1.** §4 says *"One row (G-33, B2) is neither."* **G-32** also
   falls to OTHER — its toolchain cell reads *"— no toolchain: no image was
   started"* and matches neither regex. Undisclosed.

**§4.3's headline conclusion survives; its arithmetic does not.** It reads *"the
PATCHED column is larger than the SHIPPED column (27 to 23)"*. The direction is
right and the warning it carries is right — **the true integers are 35 to 21**, so
the imbalance it warns about is considerably worse than it claimed.

**Recommendation to the matrix, adopted here:** carry the **SHIPPED / PATCHED split
as a visible column**, not a footnote, exactly as the family's own §0.3 demands.
Without it this matrix would report dafoam as roughly three times better covered on
reproducible ground than it is.

**One staleness marker to clear, owed to dafoam:** §0.6 states that
`docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md` *"is NOT at HEAD"* and marks its sha
**VERIFY** in every row. **It is at HEAD**, last changed **`4a6ea0b8`**. Every
`sha VERIFY` marker in that contribution resolves to `4a6ea0b8`.

### 3.3 closure — 6 rows, 0 HOLDS

Source: `/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md`
(tracked, `a42fd634`).

Closure asked for exactly this recomputation in its own file — *"If the owner's
expansion differs, the letters are wrong and the evidence clauses are still right —
recompute from the clauses"* — and that is what happened. **The evidence clauses are
all sound; only the letters move.**

| row | closure's tier | V | G | P | **tier here** |
| --- | --- | --- | --- | --- | --- |
| 1 — a-priori model fit | GATE REACHED | **NO** — the planted-zero `b_rms` control (plant `1.234e-03` recovered at `1.6e-14`) is instrument integrity, not code verification | **NO** — no grid family; fixed benchmark meshes | **YES** — DNS/LES truth from the public closure-challenge benchmark at `/home/ubuntu/closure-challenge-benchmark/data/`; papers on disk with title-verified sidecars; pre-registrations committed | **SURVEYED** (missing V, G) |
| 2 — a-posteriori propagation | NOT HELD | NO | **NO**, and the pre-registration disclaims it in its own words | YES | **NOT HELD** — confirmed. H0 `GATE FAIL` (TRUTH raises `U_rms` +56.99 % to +63.05 % on all three cases), H5 continuity `GATE FAIL ×6`, lane `NOT A RESULT` |
| **3 — frozen-field ceiling** | **HOLDS** | **NO** — and this is the closest near-miss in the lab: byte-identical reproduction of the W2 record, an independent Python re-derivation agreeing to worst `3.969e-12`, and planted controls registered to refuse `exit 2`. **None of the three is an exact solution, a manufactured solution or a correlation** | **NO** | YES | **SURVEYED** (missing V, G) — **not HOLDS** |
| 4 — FS2 degeneracy audit | SURVEYED | NO — the invariance check caught **58 of 110** features non-invariant, a real instrument, but not V in this sense | NO | **NO** — closure scores its own P as NO: *"no pre-registered prediction. The report is generated from the data, not predicted in advance of it"* | **SURVEYED** — confirmed |
| 5 — FS5 extrapolation coverage | SURVEYED | NO — the A1 refusal-path proof (mutated readers exiting `rc 2`, naming the planted `83.4855` at cell 31818) is the lab's best planted-zero work, and still is not one of the three | NO | **NO** — FS5's standing gate carries no declared factor, *"stated three times, met zero times"*, and `COVERAGE.md` §5 refuses to invent one post-hoc | **SURVEYED** — confirmed |
| 6 — GPU training | NOT HELD | NO — G0 planted zero recovered at `1.6e-14` identically on the GPU node and the lab box | NO | YES | **NOT HELD** — confirmed. G1 `NOT A RESULT`, G2 `GATE FAIL` (TBNN pooled `b_rms` `3.90e7` vs MLP `0.3604`), G3 `NOT A RESULT` on both. **Arm 2 is separately `NEVER RUN`** — frozen and unlaunched |

**Row 3 is the row to study, and it is why §1.1 and Ruling 1's amendment exist.**
The frozen-field ceiling is a well-instrumented, well-frozen, independently
re-derived measurement whose headline numbers reproduce exactly from the artifact
`/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/R4_sparta_build/artefacts/aposteriori.json`
— `PHLL10595` **0.0035226**, `CBFS13700` **0.398057**, `AR_5_Ret_180` **0.00013995**,
and `CBFS13700` ceiling/BASE **0.3975260** against the W2 campaign's independent
0.39753. **All four check out.** It is `SURVEYED` here because it has no code
verification and no grid convergence, **not** because anything about it is weak.

**Closure's pre-registration hygiene is the best in the lab and was verified, not
taken on trust.** Every pre-registration cited by a `HOLDS` or `GATE REACHED` row
exists at its cited path, its disk sha256 equals its HEAD blob, and its commit
history is exactly as claimed:

| pre-registration | commits | claim | result |
| --- | --- | --- | --- |
| `R4_sparta_build/PREREGISTRATION.md` | **one only, `b36daf06`** | *"sha256 058444…cbbe8, never edited"* | **confirmed exactly** |
| `Ling2016_TBNN/gpu/PREREGISTRATION.md` | one only, `e8309b6c` | *"frozen alone at `e8309b6c`"* | confirmed |
| `R5C_omega_repair/PREREGISTRATION.md` | one only, `f364cf2d` | as claimed | confirmed |
| `Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md` | one only, `0ebc9d53` | *"one commit ever; blob == HEAD == disk"* | confirmed |
| `_common/features/FS5_D476_CLIP_REPAIR_PREREGISTRATION.md` | two, `bf4956bc` → `7e973ba8` | freeze blob `8fac067c…` | **confirmed, and the second commit is a LEGAL dated Addendum 1** — +29 lines appended at the foot carrying *"lines whose number changed above this section: 0"* and *"No gate, threshold, cap or label is altered"*. Rule 2 and rule 6 compliant |
| `Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md` | four, `f36fbdd9` (freeze) → `77f064a8` | closure discloses all four and explains why last-changed ≠ freeze | confirmed as disclosed |

**Two open items owed back to closure, neither verdict-moving:**

1. **Row 3's *"all eleven cases where it converged"* needs one qualifier.** The
   artifact shows `CBFS13700/configs/ceiling` with `converged_by_residual_control =
   False`, `stagnated = True`, `iterations = 30000` — and it is one of the three
   headline ratios. **This is not a falsification**: the B2 record independently
   confirms CBFS runs a designed fixed `endTime` of 30,000 and its continuity is
   clean at `2.6e-13`. But a reader taking "eleven converged" at face value
   mis-reads the headline case, and the row should say which of the eleven ran to a
   fixed endTime rather than to residual control.
2. **Closure's own declared VERIFY stands unresolved** and is **not** credited here
   as demonstrated: whether the GPU arm-1 comparator's registered refusal branch was
   ever exercised **live**, as FS5's A1 refusal was with mutated readers exiting
   `rc 2`.

---

## 4. The two standing facts, under test

`docs/inventory/2026-08-24/LAB_INVENTORY.md` §7 asserts two structural facts about
the lab. The chief asked that they be **tested by this matrix rather than assumed**.
Both are under audit; neither is confirmed or refuted in this draft.

1. **"No converging Roache triple exists outside the thermal family."**
   **PARTIALLY CONFIRMED, 2026-08-25 — and confirmed harder than the fact claims.**
   Across dafoam (58 rows) and closure (6 rows) there is not merely no *converging*
   triple: **there is no triple at all, no GCI ever computed, and no observed order
   ever reported.** The tokens `GCI` and `Roache` appear in **zero** files under
   `cases/dafoam/`, `docs/dafoam/` and `cases/RANS_LES_closure_models/`. See §3.1.
   **Still under test for cfd**, which is where the fact is most likely to break —
   and the lead below is exactly where it would break.
   A lead that may refute it: `VERIFICATION_CHARTER.md` §3.4 calls the
   **2D flat plate** "the lab's best verification result" and states it is the first
   family the Eca-Hoekstra certifier declares **conclusive**, on the finest triple,
   on both functionals — Cd at observed order **1.634**, reportable band
   **4.244e-6** (**0.148 %** of the value). The flat plate is not thermal. The
   open question is whether an **Eca-Hoekstra certifier verdict is the same
   instrument as a Roache triple with a GCI at Fs = 1.25**; they are not obviously
   the same, and the answer decides the fact.
   The same section records a second thing that bears on the G column: the flat
   plate's **band is earned and quotable while its observed order is still
   rising** (Cd 1.0833 → 1.2587 → 1.6344; Cf 1.0315 → 1.1110 → 1.5281), so the
   ladder is **not demonstrated asymptotic**. Whether an unsettled order still
   scores G is a ruling this file must make explicitly rather than by default.

2. **"No 3D PASS against experiment with a pre-registration on disk exists at all."**
   Under test.

If the matrix confirms either, that is a finding, not an embarrassment — it is the
kind of structural fact a lab can only state once it has counted.

---

## 5. What this file is not

- It is **not** the Certonomous Verification Manual. That document is
  **SEQUENCED BEHIND this matrix and deliberately held** by the chief; it draws
  only on rows this matrix has confirmed **HOLDS**, by this team's own spot-check.
  Drafting it from claimed rows is the failure mode it is sequenced to avoid.
- It is **not** a compute record. Costs live in `docs/COST_CALIBRATION.md`.
- It does **not** commit or edit another team's files.
