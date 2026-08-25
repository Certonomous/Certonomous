# The lab coverage matrix — one row per case, three columns, one tier

**Owner:** verification team. **Status: FIRST COMPLETE PASS, 2026-08-25.** All five
families are scored and every load-bearing row was spot-checked against its artifacts
by this team, not lifted from a family's claim. **The tier column may be cited.**

**What is still open, stated so nobody over-reads the file:** the cfd rows are
selected rather than exhaustive and several are families rather than single rows;
four rulings (§2.2) are this team's and are **overrulable by the chief or Sanaa**;
and one escalation is unresolved — whether FD-vs-adjoint is admitted as a fourth `V`
instrument, which moves 23 dafoam rows. **Re-derive any census before quoting it.**

> **THE HEADLINE. There are no `HOLDS` rows. Zero, in the whole lab.**
> Not because the work is weak — the lab holds four converging grid ladders, exact
> solutions, manufactured comparisons, correlations, and the best pre-registration
> hygiene this team has audited anywhere. **It is because the lab has never closed a
> validation loop against measured physical reality under a frozen pre-registration,
> in any dimension.** §4 carries the evidence. The tier is empty for a specific,
> nameable and fixable reason, and §4 names the shortest path out of it.

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
| dafoam | `cases/dafoam/MATRIX_CONTRIBUTION.md` (**tracked**) | the **finite-difference-versus-adjoint check** (`DAFOAM_CHARTER.md` §9) | *(not a column; the family prints a lab-verdict column and a matrix-tier column instead)* | *(as above)* |
| heat-transfer | `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` (**tracked**, landed at `71ecb659`) | **a converged Roache triple with an observed order** | a **pre-registered gate with a threshold**, and what it returned | the reference **ON DISK and title-page verified** |

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

### 2.1 ~~Contribution files that are ON DISK BUT UNCOMMITTED~~ — CORRECTED 2026-08-25, both are now tracked

**This section's original text is superseded and the correction is dated because the
section was stale within about a minute of being written.**

`cases/dafoam/MATRIX_CONTRIBUTION.md` (414 lines) and
`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` were written by lanes killed by the
session usage limit at ~20:50Z on 2026-08-24, and were reported upward as **lost**.
They were not lost — both survived on disk, untracked — and **both are now tracked**;
the thermal file landed at **`71ecb659`**. The original text, that they were "on disk
but uncommitted", was true when written and stopped being true almost at once.
Corrected here at this team's own hand: the owning supervisors and their lanes both
declined to edit this file, which was right.

**The recovery finding stands and is worth keeping** — work reported as lost to a
session kill was sitting on disk the whole time. That is a cheap thing to check
before anyone rewrites a dead lane's output.

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

### ~~Ruling 1 — AMENDED 2026-08-25, before any row was entered under it~~ — **ALSO STRUCK, see the second amendment below**

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

### Ruling 1 — SECOND AMENDMENT, 2026-08-25. The tier counts GREEN columns, not missing ones

**Both earlier forms of Ruling 1 are STRUCK.** They are left standing above. This is
the third statement of the same rule and the convergence is worth reading, because
each version broke on a real row rather than on an argument.

- The **original** tiered a row by how many letters were *missing*, and broke on
  dafoam's 24 rows missing all three: it would have called them `GATE REACHED`.
- The **first amendment** sent "missing two or three" to `SURVEYED`, and broke on
  **VMFL005**, which has the lab's cleanest `G` — a CONVERGING triple under a
  pre-registration frozen 194 seconds before first compute — and is missing V and P.
  Calling that `SURVEYED` ("ungated") is as wrong as calling dafoam's rows
  `GATE REACHED`, only in the other direction.

**The defect in both was the same: counting absences.** A tier should be monotone in
the evidence a row actually holds.

**Ruling 1, final form — count the GREEN columns:**

| green columns | tier |
| --- | --- |
| **3** | **HOLDS** |
| **1 or 2**, under a frozen pre-registration | **GATE REACHED** — and the row names every missing letter |
| **0** | **SURVEYED** — *nothing on the V / G / P axes*, whatever lab gates the row passed |
| a green column's own gate returned FAIL, or a blocker | **NOT HELD** |
| no solve | **NEVER RUN** |

This is simple, monotone, and it resolves both breaking cases the way the evidence
reads: dafoam's 24 rows hold **zero** green columns → `SURVEYED`; VMFL005 holds
**one** → `GATE REACHED`, missing V and P; K0c holds **one** → `GATE REACHED`,
missing G and P.

### Ruling 4 — `P` requires validation against MEASURED PHYSICAL REALITY. An exact solution scores `V`, never `P`

Two audits collided on this and the collision is why the ruling exists. Scoring
VMFL005, one lane read `P` green — the Ansys manual is a primary source, held on
disk with a verified sha256, and the pre-registration is frozen. Another lane,
scoring the thermal rows, read the same clause the opposite way: *"under the chief's
rubric an exact analytic solution scores V, not P — so every row marked
`P ANALYTIC-HELD` has a green V and an empty P."*

**The second reading is right, and the word that settles it is the first word of the
chief's own clause: `P` — validation.** In V&V, *verification* asks whether the
equations are solved right and *validation* asks whether the right equations were
solved — which only reality can answer. The rubric already spends V on exact
solutions, manufactured solutions and correlations. Reading P to cover them too
would let one comparison score two columns and would make `HOLDS` reachable without
the lab ever comparing anything to the world.

**Ruling: `P` is green only for a comparison against MEASURED PHYSICAL REALITY — an
experiment or measured data — from a public primary source, with the
pre-registration on disk. An exact solution, an analytic benchmark, a manufactured
solution, a correlation, another code's result, or a numerical benchmark scores `V`
if it qualifies there, and scores `P` never.**

**This ruling is severe and I want its cost stated, not buried.** It empties the P
column across most of the lab, and it means **`HOLDS` requires the lab to have
compared something to an experiment under a frozen pre-registration and been
right** — which, as §4 now records, has not yet happened anywhere. That is the
finding. A rubric that could not produce that finding would not be worth running.

It also resolves a question §4 raised about the Ansys VM manual — whether a
proprietary vendor manual is a "public primary source" — by making it moot for
these rows. VMFL005's reference value **is the Hagen-Poiseuille exact solution**,
so the comparison is a `V` comparison whatever the manual's licence, and the
licence question does not need deciding to score the row.

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

~~**PARTIAL — dafoam and closure audited 2026-08-25; heat-transfer, cfd and
ansys-verification still under audit.**~~ — **STRUCK 2026-08-25. ALL FIVE FAMILIES
ARE NOW AUDITED; the exhaustive pass is §3.8 and the measured census is §3.8g.**
Nothing is entered until this team has checked the row's load-bearing evidence
against the artifacts itself.

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

### 3.4 heat-transfer — 37 sub-rows, 0 HOLDS. The five claimed HOLDS are GATE REACHED, and one of them has no triple at all

Source: `/home/ubuntu/Certonomous/docs/campaigns/T-family/MATRIX_CONTRIBUTION.md`
(tracked, `71ecb659`). The family's own audit lane re-derived its census by parsing
its §3 table rather than copying its prose and applied 28 corrections; it reports
**37 ids — HOLDS 5 (S1, S6, S13, S19, S22), GATE REACHED 1, SURVEYED 13, NOT HELD
12, NEVER RUN 6**, and found that a row (**S20b**) had been **missing**, so the
file's own totals had been wrong **in the optimistic direction** until that pass.
**VERIFY:** this team's independent audit scored **36** sub-rows against the
pre-correction file; the one-row delta is S20b, a `NOT HELD` row, and it moves no
tier and no headline.

**The rubric is not merely different here, it is rotated.** The contribution's **V**
asks *"is there a converged Roache triple with an observed order?"* — **that is the
chief's G.** Its **P** asks a custody question (is the reference on disk and
title-page verified?) where the chief's P asks a validation question. So under
Ruling 4 every row the family marks `P ANALYTIC-HELD` has a **green V and an empty
P** — and that single re-reading moves **four of its five HOLDS rows to GATE
REACHED** in one step.

| id | claim | V | G | P | tier here | family said |
| --- | --- | --- | --- | --- | --- | --- |
| **S1 — K0c** | laminar square cavity, 0 of 20 graded rows failed, largest deviation **1.139 %** on a **3 %** band | **YES** — benchmark values parsed from the frozen spec at run time; planted control fires at 3.19 % | **NO — there is no triple, and there cannot be** | **NO** | **GATE REACHED — missing G and P** | HOLDS |
| S6 — T9a | wall q″ + interface 2, conjugate | YES — closed-form composite wall | **YES** — p 1.079 / 0.952, CONVERGING | NO — analytic | **GATE REACHED — missing P** | HOLDS |
| S13 — E4a2 | fan BC, Q deviation 0.144 % | YES — exact to 1.5e-07 | **YES** — p 1.959, GCI 0.393 % | NO — analytic | **GATE REACHED — missing P** | HOLDS |
| S19 — T1c | f·Re = 64 and 48/11, Graetz λ₀² = 7.313587 to **1.6e-08** | YES | **YES** — p 2.031, CONVERGING | NO — analytic | **GATE REACHED — missing P** | HOLDS |
| S22 — T10a | 3D radiation box, closed-form view factors verified to 0.005 % | YES | **YES** — p 0.954 / 0.853 / 0.825 | NO — analytic | **GATE REACHED — missing P** | HOLDS |

**Sub-row census under this rubric: HOLDS 0 · GATE REACHED 6 · SURVEYED 13 ·
NOT HELD 11–12 · NEVER RUN 6.** The 11 `NOT HELD` rows are the family's most
valuable holding and they are not absences — they are measured negatives with model-
error attribution.

#### S1 / K0c — the load-bearing row of the whole matrix, and the one material error found in any contribution

**K0c has no grid triple and cannot have one: it was designed as mesh PAIRS.** The
eight case directories under
`/home/ubuntu/Certonomous/verification/runs/F14-cooling-ladder/K0c_runs/` are
`Ra1e3_{m32,m64}`, `Ra1e4_{m40,m80}`, `Ra1e5_{m64,m128}`, `Ra1e6_{m128,m192}` — **two
levels per Rayleigh number** — and every one of the 20 rows in `gate_k0c.json`
carries exactly `coarse_mesh` and `fine_mesh`. **A Roache triple needs three levels.**
No GCI, no observed order and no Richardson extrapolation exists anywhere in the K0c
comparator or run tree.

**Where the contribution's "`p` 1.94–2.33 on the Richardson ladder" actually comes
from: a different rung.** That triple is at `K0c_RESULTS.md:338-344` under the
heading *"The K0b mesh-sensitivity pair"* — a 32/64/128 ladder on the **K0b
capability rung**, at Pr = 0.706814 with different schemes. **K0b's own record
disclaims the reference**, at line 335:

> *"K0b's Pr = 0.706814 and its `limitedLinear`/`linearUpwind` schemes are kept
> deliberately, so **the de Vahl Davis values do not apply to these cases and are not
> used**: K0b is a capability rung graded against no published datum."*

The quoted range is not even that table's range — its six orders are **1.94, 1.75,
2.12, 2.98, 2.33, 1.84**, spanning **1.75 to 2.98**.

**So a different rung's grid ladder, one whose own record says the reference does not
apply to it, was attributed to K0c's gate. That is the single error that would have
carried K0c to HOLDS,** and it is exactly the failure the chief's instruction to
spot-check load-bearing rows exists to catch. **G is empty. K0c is GATE REACHED on
this alone**, before Ruling 4 is even reached.

**Two false friends that would trip any future sweep**, recorded so nobody re-finds
them: the `"Richardson_note"` key in all eleven `K0c_runs/audit/*.json` files is about
the **Richardson NUMBER** Ri = Gr/Re², not Richardson extrapolation; and the gate-row
field `fine_value_3pt_estimator` is a **three-point wall-gradient stencil**, not a
three-mesh ladder.

**Everything else about K0c holds up, and the record is good.** Pre-registration
frozen at **`7c606b74`, 2026-08-17 15:43:21 UTC**, message *"filed from literature
**before any mesh burns**"*; earliest run artifact **16:04:01 UTC** — the run
postdates the freeze by **19 minutes**. Reference values and bands are **parsed out of
the frozen spec at run time** rather than copied into the comparator, which exits 2
and grades nothing if the spec will not parse. The **0-of-20 denominator is confirmed
from `gate_k0c.json` directly**: 20 `gate_rows`, all `passed: true`; 4
`reported_never_graded`, all `energy_balance`; largest deviation
**1.1388340512100987 %** on `Nu_min` at Ra 1e6 against a 3 % band.

**One rule-2 defect, reported rather than waved through.** Rule 2 fixes the grading
path at the pre-registration commit. `analyse_k0c.py` was **first committed at
`32d4ae0d`, 17:03:13 UTC — after every solve finished.** The substantive exposure is
small, because the comparator holds no private copy of any reference or band. But the
claim must be stated as *"the specification was frozen before compute; the comparator
was not"*, and not as a clean rule-2 freeze.

**And a caution about the K0c comparator that generalises.** Its second dated
correction records that `analyse_k0c.py:122` resolved its spec by a fixed relative
path, the 2026-08-18 reorg moved the file, and **the K0c comparator was unrunnable at
HEAD and nothing noticed — because a comparator that is never invoked reports
nothing.** The repair swept 428 scripts and all 13 analysers and reported the zero as
a measurement. That is the right handling, and the failure mode is worth carrying
lab-wide.

**On K0c's P column, for completeness:** the family's disclosure verifies exactly —
`K0c_RESULTS.md:47-51` records tier **SECONDARY**, de Vahl Davis (1983) paywalled
(`10.1002/fld.1650030305`, Unpaywall `is_oa: false`) and **not read**, values carried
from Han & Xie (2019) Table 3. The tier string is reproduced into `gate_k0c.json`'s
`reference_tier` field so a reader of the JSON cannot lose the caveat — good practice.
**But P fails here for a reason that does not need Ruling 3 at all:** the record
itself says *"This rung is a verification result against a numerical benchmark. It is
not an experimental comparison"*, and the frozen specification **capped the rung at
TREND ONLY before compute**. Under Ruling 4 a numerical benchmark scores V, not P;
under rule 2 a cap frozen before the answer cannot be lifted after it.

### 3.5 cfd — 0 HOLDS, and the family's best-shaped row has never been run

Source: `verification/campaign/*.md`. cfd wrote no `MATRIX_CONTRIBUTION.md`; these
rows were built by this team from the campaign records. Selected rows; the family is
larger and several entries are families rather than rows.

| id | claim | V | G | P | tier |
| --- | --- | --- | --- | --- | --- |
| **flat-plate-tmr** | TMR 2D ZPG flat plate, SST, five rungs 816 → 208,896 cells: **Cd p 1.6344 / GCI 0.1482 %**, **Cf p 1.5281 / GCI 0.1880 %**, both CONVERGING, band earned | NO — reference is CFL3D/FUN3D, code-to-code | **YES** — CONVERGING at Fs = 1.25, order quoted; **order still rising**, not asymptotic | NO — code-to-code, **and no pre-registration on disk** | **GATE REACHED — missing V and P** |
| **DMR** | double Mach reflection, prereg `74797a57` frozen **before any mesh existed**: incident-shock kinematics vs exact theory **PASS** both rungs (0.15 %, 0.17 %); structure detector **FAIL as registered, left standing** | **YES** — exact theory | NO — two rungs | NO | **GATE REACHED — missing G and P.** The best-disciplined row in the family |
| **F3** | wedge / cone / diamond, `rhoCentralFoam`: surface pressure **0.01–0.07 %** of exact oblique-shock theory, cone 0.19–0.29 %, wave drag 0.18–0.55 % | **YES** — oblique-shock, Taylor–Maccoll, shock-expansion | NO — three levels exist, no order, no GCI | NO | **GATE REACHED — missing G and P**; a conversion prereg is frozen, so the re-gated row is **PENDING** |
| **F4** | 2D cylinder M 6–8: standoff vs **Billig (1967) correlation** +0.70…+2.33 %; Cp RMS vs modified Newtonian 3.87–3.91 % | **YES** — a correlation scores V | NO | NO | **GATE REACHED — missing G and P** |
| **DPW8_V2** | Joukowski airfoil vs analytic inviscid: L1 −8.262e-08 ± 1.029e-06, L3 −2.039e-06 ± 7.162e-07, both PASS | **YES** — analytic | NO | NO | **GATE REACHED — missing G and P**; L4 **PENDING** |
| **W1** | bump on **NASA's own grids**, prereg `3e252b5c` before any solve: the pressure order returns where the blockMesh family had none | NO | **CONTESTED** — all three quantities CONVERGING by state (p 4.037 / 3.200 / 1.246) but the campaign's **own certifier records `conclusive: no`**, failing `order_window` and `extrapolation_sanity` | NO | **GATE REACHED — missing V and P**, with G disclosed as contested |
| **F11** | lid-driven cavity Re 100 / 1000 vs Ghia, Ghia & Shin (1982) | NO | NO — two resolutions, not three | NO — public but numerical, no prereg | **GATE REACHED — missing V and G** |
| **F7a** | Martin & Moyce (1952) dam break, spec frozen at **zero compute**: pinning the measurement definition **refutes** the ambiguity hypothesis; every reading lands **+7.8 % to +11.9 %**, all FAIL a 5 % band | NO | NO | **YES — experiment, public primary, spec frozen on disk** | **NOT HELD** — and one of the lab's most defensible rows |
| **F8** | UAE Phase VI vs Hand et al. (2001), NREL experiment | NO | NO | experimental and public; **no frozen prereg** | **NOT HELD**. Vocabulary flag: *"NO VERDICT"* and *"NO MILESTONE"* are outside rule 1 |
| **F12** | RAE 2822 / AGARD AR-138 Case 9, prereg written 2026-07-30 **before any solver**, admission gates A/B plus Gates 1–3, overall PASS rule frozen | — | — | **YES in principle** | **NEVER RUN** — *"F12 remains PENDING"*. **The family's best-shaped unfired row** |
| 4G, B52_RUNG6, D5_rsm, F2, F5b, F5c, GEN_ALT, MESH_AUDIT, W2_sparta, W3 | diagnoses, replicates, scored predictions, instrument audits | mixed | none | none | **SURVEYED** (10 rows) |

**Two caveats the flat-plate row must carry and the charter does not.** From the
ladder's own proposal record: **(1)** the grids are *"this module's blockMesh at
matching cell counts, **NOT NASA's point files**"* — W1 is the case that ran NASA's
grids. **(2) The same ladder at the default iteration cap is a DIVERGENCE**: at the
module's 15,000-iteration cap this rung read Cd 1.05 % high and still falling, and
the same certifier reads **p = −0.745 with growing increments**. **36,000 iterations
were needed.** Measured spend **483.6 core-min against a 327 estimate (1.48×)**, of
which **202.7 went on a stage the module then refused.** Any row claiming this ladder
must claim the iteration count with it.

**Two filing defects found and referred, not scored:** `FPE_DIAG` **could not be
located** under that id — no campaign record exists, and this team will not guess at
a row; and `F4_SIGFPE_STEP01_RESULTS.md` **contains a "CERTONOMOUS MORNING REPORT"
dated 2026-08-24, not an F4 SIGFPE result** — filename and content do not match.
Both are cfd's, and the second is a docket item independent of this matrix.

**Vocabulary drift found in cfd records, referred to cfd:** `GEN_ALT` grades
*"GENERATOR-OWNED"*; `W1_hump` grades *"OUTCOME ONE"* / *"outcome two"* / *"outcome
N"*; `F8` grades *"NO VERDICT"* / *"NO MILESTONE"*. These are pre-registered branch
labels, which is legitimate design — but they are **not rule 1 verdict words**, and
they are the same defect shape the thermal family catalogued in its own §7. A sweep
for the lab's verdicts does not see them.

### 3.6 ansys-verification — the lab's cleanest G, audited row by row

**VMFL005's `PASS` is SOUND.** This team audited it as a gate audit rather than
reading the claim:

- **Pre-registration frozen 194 seconds before the first solver artifact existed.**
  Freeze commit `2d54a629`, 18:42:07Z; earliest run artifact 18:45:21.32Z. The
  prereg blob at that commit is `43aaf6bf…` and **the same file hashed on disk now is
  `43aaf6bf…`** — byte-identical, never amended. The comparator blob frozen in the
  prereg's §10 table is `8e7410cc…` and **the file on disk hashes to `8e7410cc…`**:
  the frozen file **is** the file that ran. Checked by hashing against the committed
  blob, which is what rule 2 demands, not by reading a claim.
- **The gate could have failed, and it discriminates.** The 2 % band is in the frozen
  prereg and hardcoded in the comparator frozen five minutes earlier still. The
  prereg's own §2 states — **before any number existed** — that Ansys's own CFX value
  of 10.49 Pa would fail it. Driving values through the frozen gate expression:
  10.2909853852 → **PASS** (0.4979 %); 10.22 (Fluent's own value) → PASS; **10.49
  (CFX's own value) → GATE FAIL (2.4414 %)**; 10.45 → GATE FAIL; 5.0, 20.0, 0.0 → GATE
  FAIL. **A plausible wrong answer — a commercial code's own published number for this
  exact case — fails.** The band is 4.0× the measured deviation, so it is not tight;
  it was argued from the manual's own 3 % goal, not chosen to clear the answer.
- **The instrument is demonstrably capable of not-PASS**: the same family's VMFL001
  returned **`NOT A RESULT`** on real data — the comparator refused (exit 2) on a
  v2606 filename mismatch and L3 missed the registered 1e-6 residual clause.
- **The planted-zero control fired on the real file** — planted 1.234 Pa, read back
  1.234, with a negative arm confirming an unplanted copy shows no change to 1e-15.
- **The reference traces to the manual on disk**, sha256 `577659469a30…`, line 1208
  (Fluent, p. 25) and line 1223 (CFX, p. 26). **Transcription trap worth carrying: a
  literal search for `10.24` in the sidecar returns NOTHING** — the PDF text layer
  renders it as `10. 24`, with a space inside the number. Any checker matching the
  reference literally would find zero. The value is unambiguous by the manual's own
  printed ratios: 10.22/10.24 = 0.998 ✓ and 10.49/10.24 = 1.024 ✓.

| id | V | G | P | tier |
| --- | --- | --- | --- | --- |
| **VMFL005** | **NO — and this is a measured negative, not an absence.** The reference **is** an exact solution (Hagen-Poiseuille), and the code is measured **not to converge to it**: the CONVERGING triple extrapolates to **10.29511921 Pa, 0.5383 % from exact — FURTHER than the fine grid's 0.4979 %**. Deviation/GCI = **9.92**, so ~90 % of the residual is not discretisation error. Grid refinement does not close it | **YES — the strongest G in the lab.** 10.23475565622 / 10.27932261636 / 10.2909853852 Pa at 1,000 / 4,000 / 16,000 cells, r = 2.0 exact, **CONVERGING**, **p = 1.9340642**, **GCI_fine = 0.0502 % at Fs = 1.25**, monotone so the GCI is quotable | **NO** — under Ruling 4 the Hagen-Poiseuille comparison is a V comparison, not validation | **GATE REACHED — missing V and P** |
| **VMFL001-R2** | NO | **YES** — CONVERGING, **p = 2.0102**, GCI_fine 5.633e-04, prereg frozen `4507fc66` 18:05:49Z against a first artifact 18:10:44Z, **295 s later** | NO | **GATE REACHED — missing V and P** |
| **VMFL001** | NO | NO | NO | **NOT HELD** — `NOT A RESULT`, kept rather than deleted, correctly excluded from the credential count |

**The register is correct and I recomputed it rather than reading it.** At HEAD
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` holds **3 rows, 2 PASS
of 3 run**, and **every PASS row's cited artifact exists on disk** — verified
individually, including that **dP = 10.2909853852 Pa reproduces from the raw monitor
files by subtraction** (`pInletMonitor` last row `1.029098538520e+01`,
`pOutletMonitor` last row `0.000000000000e+00`). **No non-PASS row is carried as a
credential, and I found no softening anywhere.** The re-run is a new row citing the
old one, exactly as `VERIFICATION_CHARTER.md` §6 requires.

**⚠ The register's WORKTREE copy is STALE** — it holds 1 row and reads *"Credential
count: 0 PASS of 1 run"* where HEAD holds 3 rows and *"2 PASS of 3 run"*. It
**understates**, so it is not a false credential; but **the file a reader opens is not
the record**. Same staleness class as `docs/LAB_STATE.md`, `docs/COST_CALIBRATION.md`
and `docs/NUMERICS_KNOWLEDGE.md`. This is now a **four-file pattern** and is recorded
in §6.

**The ansys team reached the same tier independently** (`docs/ansys_verification/COVERAGE_ROWS.md`,
N-AV7: *"A team scoring the V column from GCI alone would score VMFL005 HOLDS and be
wrong"*). This team checked that reasoning rather than relaying it, and it holds.
**That is a family grading itself down on its own evidence, unprompted, and it is the
behaviour the audit exists to produce.**

### 3.7 The census so far

| tier | dafoam | closure | heat-transfer | cfd | ansys | **total** |
| --- | --- | --- | --- | --- | --- | --- |
| **HOLDS** | 0 | 0 | 0 | 0 | 0 | **0** |
| **GATE REACHED** | 0 | 0 | 6 | 7 | 2 | **15** |
| **SURVEYED** | 49 | 4 | 13 | 10 | 0 | **76** |
| **NOT HELD** | 0 | 2 | 11–12 | 2 | 1 | **16–17** |
| **NEVER RUN** | 9 | 0 | 6 | 1 | 0 | **16** |

~~**Read as a claim, not as an authority.**~~ — **SUPERSEDED 2026-08-25 by §3.8g,
which is exhaustive across all five families (153 rows) under stated enumeration
rules.** The caveat was correct for this table and is kept visible because the
table was circulated under it. Its ground: dafoam's row is its corrected 58-row
census re-tiered wholesale; **cfd's rows here are selected, not exhaustive**, and
several are families rather than rows. **Quote §3.8g, not this table.**

---
---


---

## 3.8 THE EXHAUSTIVE PASS — heat-transfer, cfd and ansys-verification completed 2026-08-25. **The zero is now a MEASURED zero**

**§3.4, §3.5 and §3.6 were a first pass. §3.5 said so in its own words — *"Selected
rows; the family is larger"* — and the §3.7 census was correctly labelled *"a claim,
not an authority"*. This section removes that partiality.** The earlier sections are
**kept, not rewritten**; where a row moves, this section names it and says why.

**All three audits were read-only against HEAD `af2b23b0`, zero compute, no worktree
reads.** No solver, no mesher, no container, no GPU.

### 3.8a Enumeration rules, so the next auditor re-derives rather than trusts

**cfd — 48 rows.** Territory: `cases/` minus closure/dafoam/ansys; `verification/runs/`
minus T-family, F14-cooling-ladder, THERMAL_K0, ansys; all of `verification/campaign/`;
`models/`. A **row** is one distinct case or campaign evidenced at HEAD by a run tree
(27 exist), a case directory with a record (7), or a `verification/campaign/` grading
artefact. Rows are keyed by **case identity**, so prereg + results + json + run tree for
one case is **one** row. Excluded as non-rows: administrative records with no case
identity, `cases/demo-surfaces/` (geometry assets), `models/` (inputs).

**heat-transfer — 37 sub-rows.** The open **VERIFY is RESOLVED at 37** (S1…S27 with
S2b, S3b, S5b–S5g, S18b, S20b). This team's earlier 36 was scored against the
pre-correction file; the delta is **S20b**. **The 11–12 ambiguity is RESOLVED: NOT HELD
= 12.**

**ansys-verification — 4 rows.** Four pre-registered cases, three run, one armed and
unfired.

### 3.8b ⚠ THE EARLIER PASS WAS WRONG THAT cfd HAD NO CONTRIBUTION FILE

`verification/campaign/MATRIX_CONTRIBUTION.md` **exists at HEAD** — 521 lines, 19 rows,
landed `9060e751`, 2026-08-25 00:14:07Z. §2.1's *"cfd has no `MATRIX_CONTRIBUTION.md`"*
is **struck by this section**. It applies the owner's rubric verbatim and defines no
private V/G/P — **but it was written against Ruling 1's ORIGINAL form and predates
Ruling 4 entirely**, so its tiers are not liftable. Its evidence clauses are, and were
used.

### 3.8c RULING 5 — `GATE REACHED` REQUIRES A FROZEN PRE-REGISTRATION. The clause in Ruling 1 is a CONDITION, not a description

**The cfd audit asked this team to rule it, and gave both counts rather than pick.
Ruling, and it goes against this lab's own favour:**

Ruling 1's second amendment reads *"1–2 green columns **under a frozen
pre-registration** → GATE REACHED"*. **That clause is a condition and is now read as
one.** Sanaa's own directive text — recovered at §6b.8 — settles it independently:
**`GATE REACHED = passed a gate but missing one of V/G/P`**. A row with **no
pre-registration for the graded work has not passed a gate** in this lab's sense,
because CLAUDE.md rule 2 makes a gate a thing frozen before the run. **A green column
earned without a frozen gate is breadth evidence, and breadth evidence is `SURVEYED`.**

**This resolves an internal contradiction §3.5 was already carrying:** it tiered
`flat-plate-tmr` **GATE REACHED** while that row's own P cell says *"no
pre-registration on disk"*. **Under Ruling 5 `flat-plate-tmr` is `SURVEYED`**, and so
are `F3`, `F4`, `DPW8_V2` and `F9`. **`DMR` is the only cfd row whose green column sits
under a frozen pre-registration** (`74797a57`, frozen before any mesh existed).

**The movement is toward the more conservative tier in every case**, which is the only
direction a rubric may be tightened on rows already scored.

**VERIFY — and it is named rather than glossed.** The frozen-prereg condition was
**verified individually** for ansys (VMFL005 at +194 s, VMFL001-R2 at +295 s, both blob-
hashed at HEAD) and for cfd (each row read to source). **It was NOT individually
verified for heat-transfer's seven `GATE REACHED` rows.** One is confirmed —
**S5d/K0cG, prereg `3b454b37` before any case reported**. The other six carry the tier
**pending that check**, and the check is the first item of the handover list in §3.8g.

### 3.8d heat-transfer — 37 sub-rows. **HOLDS 0 · GATE REACHED 7 · SURVEYED 12 · NOT HELD 12 · NEVER RUN 6**

Full table in the audit record; the movements against §3.4 are:

- **S5d / K0cG re-tiered SURVEYED → GATE REACHED (missing V and P).** Five kOmegaSST
  quantities CONVERGING, **p 1.516–4.078**, and **`Fs: 1.25` read directly out of
  `verification/runs/F14-cooling-ladder/K0cG_runs/gate_k0cg.json`** rather than from
  prose. Prereg `3b454b37` before any case reported. **Exactly the VMFL005 shape.**
- **NOT HELD settled at 12; SURVEYED 13 → 12.**

**The 12 `NOT HELD` rows remain the family's most valuable holding**, and §3.4's reading
of them stands: they are measured negatives with model-error attribution, not absences.

**⚠ THE OPTIMISTIC-OMISSION FAILURE HAS REPEATED, and twice.** The contribution omits
three rows the territory holds, **two of them negatives**:

1. **K0b D403 re-run** — `K0b_D403_RERUN_RESULTS.md` plus a 71-file run tree. **V3 GATE
   FAIL**: run unaided, the committed `build_and_run.sh` produced a 128×128 leg **4.490 %
   below** the published `Nu_avg_hot` at observed order **−1.25** against the published
   **+1.94**. **The contribution carries S2b — the D406 *repair*, 4 × PASS — and omits
   the re-run that FOUND the defect.** Tier **NOT HELD**.
2. **T1b attempt 1** — `NOT A RESULT`, all 19 cases, **56.6 core-hours discarded**. The
   contribution carries attempt 2 and omits attempt 1. Tier **NOT HELD**.
3. **K1a / K1c standing thermal checks** — executed against planted defects. Tier
   **SURVEYED**, neutral direction.

**This is the S20b failure mode repeated: the row carrying the negative was dropped and
the row carrying the PASS was kept.** Adding the three resolvable rows gives **40 rows
at 0 / 7 / 13 / 14 / 6**. **37 is carried here as the settled figure and the correction
is the family's to make**, but the pattern is named because it has now happened twice in
the same file and it moves the census in the flattering direction both times.

**Two rows that cannot be tiered at all: K2bU and K2bU3** carry a pre-registration,
tracked case inputs and tracked comparators, and **no results record and no sub-row**.
Their run output would be gitignored, so **NEVER RUN cannot be separated from
completed-but-unfiled from HEAD.** Not guessed at.

**`NEVER RUN 6` is a SUB-ROW figure, not a count of never-run classes** — eleven
never-run cells (C3, C5, C7–C9, C11–C13, C16–C18) carry no sub-row at all.

### 3.8e cfd — 48 rows. **HOLDS 0 · GATE REACHED 1 · SURVEYED 37 · NOT HELD 8 · NEVER RUN 2** (Ruling 5)

**Column census: V green 5 of 48 · G green 1 of 48 · P green 0 of 48.**

**THE P ZERO IS NOW MEASURED, NOT PARTIAL.** Every P-candidate was read to its source
and each fails for a **named** reason: **F6b** on Rulings 3 **and** 4 (Breuer et al. is
LES/DNS *and* reached via KBwiki); **F7a** and **F5a** on `VERIFICATION_CHARTER.md`
§6b's `NOT OBTAINED` (Martin & Moyce not held as a primary; a 2021 figure digitised at
600 dpi); **F8** on a secondary reference and no gateable number; **F11** on Ruling 4
(Ghia et al. is a numerical benchmark); **F1** on a missing pre-registration; **F12** on
not having run.

**⚠ TWO ROWS CORRECTED AGAINST §3.5, BOTH IN THE UNFAVOURABLE DIRECTION:**

- **F7a's P cell was GREEN in §3.5 and is now RED.** `VERIFICATION_CHARTER.md:1713`
  records Martin & Moyce as **`NOT OBTAINED` as a primary**. **§3.5's green P
  contradicted this file's own Ruling 3 and the charter simultaneously.** The tier
  **NOT HELD** does not move — the row still GATE FAILED at +8.2 % mean / +11.0 % max
  on a 5 % band, 389.8 core-min — but **the lab's one green P is withdrawn, and the
  correct count of green P cells in cfd is zero.**
- **W1 moves GATE REACHED → SURVEYED.** `verification/runs/W1_runs/ladder_fit.json`
  records `conclusive: false` and **`reportable_band: null`** on cd and cd_pressure
  (`guards_failed: ["order_window"]`) and on cd_viscous (`extrapolation_sanity`).
  **No band was issued, so there is no GCI. A contested G is not a green column.**

**Three rows newly enumerated that no pass had ever carried:** **F9** (pulsatile valve
vs Womersley — V green on an exact solution, though **Womersley (1955) is NOT held on
disk**), **F1** (ONERA M6 — the experiment is right and **no prereg exists**, so
SURVEYED), and **bump-tmr-blockmesh**.

**`bump-tmr-blockmesh` is the sharpest find in the family and it is a refusal.**
`cases/tmr/bump_sst.json` publishes a monotone triple, `observed_order` **0.5446** and
`gci_fine_pct` **3.8393 %** — and the safety factor **back-solves to Fs = 1.2500**, so
it is formally a GCI. **But there is no `certifier` block, no `conclusive` field and no
plateau evidence at any level**, p sits **on the very edge** of the [0.5, 2.5] window,
and 4G §10 records the pressure component's increments changing sign at every matched
iteration count. **Rule 5 clause (1) is unmet on the artefact. Scored SURVEYED, handed
to cfd as a G *candidate*, not a G *result*.**

**The two filing defects re-checked at HEAD: both NARROW, neither clears.** `FPE_DIAG`
**does** have a pre-registration — inside the run tree, not under `verification/campaign/`
— so the earlier *"could not be located"* is wrong on the id; **what does not exist
anywhere at HEAD is a grading record.** Five `record.json` and no landed grade. **The
defect is a missing verdict, not a missing id.** And `F4_SIGFPE_STEP01_RESULTS.md`
**still opens with `CERTONOMOUS MORNING REPORT`** — the F4 grade *is* inside the file,
so no content is lost, but a sweep for F4's record of grade meets a filename that does
not describe its contents.

### 3.8f ansys-verification — 4 rows. **HOLDS 0 · GATE REACHED 2 · SURVEYED 0 · NOT HELD 1 · NEVER RUN 1**

**⚠ THIS TEAM'S OWN §3.6 IS WRONG ON VMFL001-R2's V COLUMN, and the correction makes it
the lab's nearest-to-HOLDS row anywhere.** §3.6 scores V `NO` with no reason given.
**The exact White §3-2.3 formula IS a registered comparison in the frozen
pre-registration** — blob `c6b4a7c4…` lines 95–96, *"against the exact formula,
|v_lab − v_exact|/|v_exact| ≤ 0.005 at all four radii"* — and it was **met at all four**:
0.0529 / 0.0456 / 0.0420 / 0.0447 %. Decisively, **the CONVERGING triple's Richardson
extrapolate 0.004547826544889741 m/s lands on the exact 0.00454781 to 3.7 ppm, with the
closed form never given to the solver.** That is code verification in the strict sense,
under a frozen pre-registration.

**The tier word does not move — GATE REACHED either way — but the cell must read
"missing P", not "missing V and P". VMFL001-R2 is then ONE COLUMN SHORT OF HOLDS, and
it is the closest any row in this lab comes.**

**The contrast with VMFL005 is the whole point and the ansys team wrote it down
themselves (N-AV7):** same machinery, p ≈ 2 on both, GCI ≈ 0.05 % on both — and **one
code converges to exact while the other is measured NOT to** (VMFL005's extrapolate is
**0.5383 % from exact, FURTHER than the fine grid's 0.4979 %**; deviation/GCI **9.92**).
**Their V columns must differ, and §3.6 collapsed them to the same `NO`.**

**VMFL051 — NEVER RUN, and it is the best-armed unfired pre-registration in the lab.**
Frozen `22249c82`, Amendment 1 at `54d34542` **before first compute** (legal under rule
2), its condition-check genuine: at 2026-08-25T00:15:28Z the run directory did not
exist, `find` returned 0 files, `pgrep -a rhoCentralFoam` returned nothing. **Its gate
can genuinely fail, priced in advance:** the manual's own literal *"incompressible"*
instruction leaves M at 2.5 and **fails by 45×** (−22.77 %); sampling inside the fan
fails by up to 22 %; **Fluent's own −0.1668 % and CFX's −0.0494 % pass with 3× and 10×
margin, so a lab result three times worse than Fluent's fails.** The band was **derived,
not rounded to** — it must exceed a 0.0605 % systematic floor and sit ≈2× under the
O(1 %) failure mode. **One blind spot declared BEFORE the freeze:** γ = 1.4 against the
manual's derived γ = 1.3990094 differ by 0.005 % and this gate cannot separate them.

**Register recomputed, not read: 3 rows, 2 PASS of 3 run**, every cited artifact
verified present at HEAD by `git cat-file -e` — including **both PASS rows' gate-source
files**. No non-PASS row is carried as a credential. Both PASS preregs re-verified by
**blob hash at HEAD**, neither amended.

**⚠ THE STRUCTURAL FINDING §3.6 WAS MISSING, and it names the lab's shortest path to a
first HOLDS.** The family's own `CASE_MAP.md` classifies all 95 VM cases by reference
type: **`AN` analytical 26 · `EXP` experimental 50 · `NUM` numerical benchmark 19.**
**Every case this family has run or armed — VMFL001, VMFL005, VMFL051 — is `AN`, so all
three are P-capped at GATE REACHED BY CONSTRUCTION, however well they are run.** But the
family is **not** structurally capped: **it holds 50 experimental-reference cases, the
largest reservoir of P-capable rows anywhere in this lab, and has run none of them.**
**This SHARPENS §4's Fact-2 remedy rather than reversing it:** §4 correctly withdrew
"the Ansys cases are a route to P" **on the cases the family had run**; the `EXP` half
of the manual is a different population, and **VMFL071 / VMFLGPU006 (Goldman stator
blade, pressure ratio vs experiment) is already named in the family's own map.**

### 3.8g THE MEASURED CENSUS — 153 rows, and the zero survives

| tier | dafoam | closure | heat-transfer | cfd | ansys | **total** |
| --- | --- | --- | --- | --- | --- | --- |
| **HOLDS** | 0 | 0 | 0 | 0 | 0 | **0** |
| **GATE REACHED** | 0 | 0 | 7 | 1 | 2 | **10** |
| **SURVEYED** | 49 | 4 | 12 | 37 | 0 | **102** |
| **NOT HELD** | 0 | 2 | 12 | 8 | 1 | **23** |
| **NEVER RUN** | 9 | 0 | 6 | 2 | 1 | **18** |
| **total** | 58 | 6 | 37 | 48 | 4 | **153** |

**Under the permissive reading Ruling 5 rejects** (counting green columns without the
frozen-gate condition), cfd's row would read GATE REACHED **6** / SURVEYED **32** and
the totals GATE REACHED **15** / SURVEYED **97**. **Both are printed so the ruling can
be overturned without re-auditing.**

**THE ZERO IS NOW MEASURED.** **HOLDS 0 across 153 rows in five families, every row
enumerated by a stated rule, every green column read to an artifact.** It is no longer a
partial count with a caveat attached.

**And the reason is unchanged and now better evidenced: `P` green appears on ZERO rows
in the entire lab.** V is green on a handful, G on a few, **P on none.**

### 3.8h ⚠ A CORRECTION AGAINST THIS FILE'S OWN HEADLINE, and it matters more than the census

**§3.1 and §4 say the lab *"has NEVER CLOSED A VALIDATION LOOP AGAINST MEASURED PHYSICAL
REALITY UNDER A FROZEN PRE-REGISTRATION — in any dimension."* That sentence is FALSE as
written, and the family it is wrong about is heat-transfer.**

**K0cS closed exactly that loop** — Ampofo & Karayiannis (2003), **read in full**, Fig.
11 digitised to ±0.15, under a frozen pre-registration — and returned **GATE FAIL, 14 of
20 rows, 0 models passing.** **K0cT and K0cX closed it too** — ERCOFTAC Case 079, the
primary files **on disk**, Betts & Bokhari Table 1 read in full — returning **GATE FAIL
8 of 18** and **24 of 42, 0 of 3 models.**

**The loop WAS closed. The answer was NO.** Those rows are tiered `NOT HELD` **because
their gates failed, not because no comparison was made** — and the difference is the
whole distinction between a lab that has not tried and a lab that tried and reported an
honest negative. **The corrected sentence is Ruling 4's own wording: HOLDS requires that
the lab compared something to measured physical reality under a frozen pre-registration
AND WAS RIGHT.**

**This is the second time in two sessions this team has published a sentence stronger
than its evidence** (§6a.0 was the first). **The pattern is the finding: a headline
sharpened for force outruns the rows beneath it, and this team is not exempt from the
scepticism it applies to others.**

### 3.8i FOUR ITEMS THIS PASS REFUSES TO DECIDE, named so nobody assumes they were

1. **THE `V` COLUMN IS SCORED TWO DIFFERENT WAYS ON THE SAME EVIDENCE CLASS, and Ruling
   4's text arguably makes both green.** `flat-plate-tmr` scores V `NO` because the
   reference is *"CFL3D/FUN3D, code-to-code"*; `K0c` scores V `YES` on a **numerical
   benchmark** that is additionally **SECONDARY** (de Vahl Davis 1983, paywalled, never
   read, reached through Han & Xie Table 3). **Ruling 4 as written admits *"another
   code's result or a numerical benchmark"* — which would make BOTH green.** Moving
   either row is a **rubric widening in the flattering direction**, and this pass will
   not take it. **If K0c's V goes the way of flat-plate-tmr, K0c holds ZERO green
   columns.** To the chief and to Sanaa; no row moved.
2. **The class-vs-case row structure** (§6b.8). Her directive says rows are **problem
   classes**; this file is one row per case. **Escalated, not decided.**
3. **`GATE REACHED` = missing one, or missing one-or-two** (§6b.8). Her text says
   **one**; Ruling 1's second amendment says **one or two**. Disclosed; **every GATE
   REACHED row already names its missing letters, so the strict reading is recoverable
   from the tables without re-auditing.**
4. **Six of heat-transfer's seven `GATE REACHED` rows have not had their frozen-prereg
   condition individually verified** (§3.8c). **The tier is carried pending that check,
   and the check is one lane's work.**

### 3.8j ⚠⚠ A HAZARD TO A FROZEN PRE-REGISTRATION, REPORTED TO THE CHIEF AND NOT ACTED ON

**All thirteen `cases/ansys_verification/VMFL051/*` paths appear in the session's opening
`git status` snapshot as STAGED DELETIONS (`D `), while every one of them exists at
HEAD.** Under §6a's ruling `git status` is not a valid instrument here and this is
**not treated as a fact** — it has the exact shape of the phantom `D` rows §6a
measured. **But if that staged deletion is ever committed, a FROZEN, ARMED, UNFIRED
pre-registration leaves HEAD and its rule-2 freeze is destroyed.** VMFL051's is the
cleanest unfired freeze in the lab. **The shared index is the chief's to clear and
nothing was touched here (rule 10).**


### 3.8k ⚠ DATED CORRECTION, 2026-08-25T01:20Z — **TWO ROWS OF THIS CENSUS WERE STALE WITHIN THE HOUR, and the staleness is itself the finding**

**This pass was audited against HEAD `af2b23b0`. Two rows moved before the ink was
dry, both from `NEVER RUN`, and this team found out by reading the cost ledger while
writing its own calibration row — not by any instrument that watches for it.**

| row | tiered here | what actually happened | correct tier |
| --- | --- | --- | --- |
| **VMFL051** (ansys) | **NEVER RUN** | **GRADED `NOT A RESULT`** — C-51, commit `0c3f3054`. Three-level refinement-2 Roache family (6,240 / 24,960 / 99,840 cells), `rhoCentralFoam`, the family's first compressible case. Register row **#4**. `NOT A RESULT` on **two independent clauses of rule 5** | **NOT HELD** |
| **F12** (cfd) | **NEVER RUN** | **RUNG 1 FIRED AND FAILED** — commit `cd1ac21a`, C-50. **Gate A `GATE FAIL`: non-orthogonality 70.646 against a frozen limit of 70**, solver then diverged to negative T at iteration 180 | **NOT HELD** |

**Corrected census: `NEVER RUN` 18 → 16; `NOT HELD` 23 → 25.** `HOLDS 0` is
unchanged, `GATE REACHED 10` is unchanged, and the total stays **153**.

**Three things worth carrying, none of them comfortable.**

1. **A coverage matrix is a MEASUREMENT WITH A TIMESTAMP, not a standing fact.** Every
   row in this file is true of a sha, and this file names its sha. **Two rows decayed
   in under an hour because the lab was working while it was being written.** Any
   future pass must **print the sha it was taken at** — §3.8 does — and any reader
   must treat a tier older than the rows beneath it as **provisional**. This is the
   same non-stationarity `L-307` measured on the index, arriving in a second place.
2. **`NEVER RUN` is the least stable tier in the vocabulary and should be read as
   such.** It is the only tier a peer team can invalidate by doing exactly what it is
   supposed to do. **The other four require a re-grade; this one requires only a
   launch.**
3. **BOTH MOVEMENTS ARE THE LAB WORKING CORRECTLY, and neither is a defect.** VMFL051
   returned `NOT A RESULT` on two independent rule-5 clauses; **F12's gate A failed on
   a mesh-quality limit frozen in advance — 70.646 against 70 — which is a gate
   discriminating, i.e. the thing a gate is for.** **The two rows this team lost are
   two rows the lab earned.**

**AND IT BEARS ON §91 OF `docs/CROSS_TEAM_GATE_AUDIT.md`, so it is stated rather than
left to be noticed.** That ruling's **primary** ground was that **§2d had not been
triggered because F12 had never run** — verified on disk at the time and **true when
the ruling was made**. **F12 has now run, and that is precisely what the ruling
authorised.** The ruling is **unaffected**: §2d asks whether the grading path changed
**after** the first graded solve, and the repair **predates** it. **What has changed is
that the ground is now historical rather than current, and any future citation of §91
must say so.** Rung 1's `GATE FAIL` on a pre-frozen non-orthogonality limit is also
the first direct evidence that F12's gates discriminate.
---
---

## 4. The two standing facts — BOTH RESOLVED

`docs/inventory/2026-08-24/LAB_INVENTORY.md` §7 asserts two structural facts. The
chief asked that they be **tested rather than assumed**. Both now have answers, and
**one of them is false**.

### Fact 1 — *"Not one aerodynamic case, 2D or 3D, carries a CONVERGING Roache triple."* — **FALSE**

Refuted on four independent counts, each re-derived by running the lab's own
canonical instrument `scripts/roache_triple.py` (Fs = 1.25, `STAGNANT_FLOOR` 0.5) on
values already on disk:

| ladder | family | result |
| --- | --- | --- |
| **TMR 2D flat plate**, five rungs 816 → 208,896 cells | cfd | **six CONVERGING triples.** Finest: **Cd p 1.634406, GCI 0.148208 %**; **Cf p 1.528107, GCI 0.187998 %**. The certifier records `conclusive: true` with `reportable_band_abs` 4.244064059104043e-06 (Cd) and 5.084493331132672e-06 (Cf) |
| **VMFL005** | ansys | **CONVERGING**, **p 1.9340642**, GCI_fine 5.0211727801e-04, `verdict PASS` |
| **VMFL001-R2** | ansys | **CONVERGING**, **p 2.0102122635**, GCI_fine 5.6328392451e-04, `verdict PASS` |
| **W1 bump on NASA's own grids** | cfd | **CONVERGING by state** on all three quantities (p 4.037 / 3.200 / 1.246) — **but the campaign's own certifier records `conclusive: no`**, failing `order_window` on two and `extrapolation_sanity` on the third. Orders of 3.2 and 4.0 on a formally second-order scheme are the lab's own signature for *"the coarsest level is outside the asymptotic range"*. **Both readings reported; this team does not pick** |

**The charter is not quoting a vanished artifact.** `VERIFICATION_CHARTER.md` §3.4's
flat-plate numbers are all on disk, in `cases/tmr/flatplate_sst.json` under
`convergence_extended`. The `VERIFY` this team placed on them is **lifted**.

**The honest restatement, offered to the inventory:**

> *"Outside the thermal family, four aerodynamic ladders carry CONVERGING Roache
> triples — the TMR flat plate (both functionals, conclusive band earned), the W1
> bump on NASA's grids (converging state, certifier-refused on the order window), and
> two Ansys VM cases. **What none of them has is a pre-registered gate against
> experiment.**"*

That preserves the strategic point §7 was reaching for while ceasing to be false —
and the strategic point survives intact, because the missing column was never G.

**Three false friends cleared**, so nobody re-finds them: `PATH_CONVERGING.gs_id_conv`
in a dafoam A3 record is a guard-selftest marker *filename*; an agenda proposal uses
*"the CONVERGING one"* of a **linear-solver** rung; and a closure arm-2 prereg
**registers a branch** for a non-CONVERGING triple and has not run.

### Fact 2 — *"3D validation against experiment is empty."* — **TRUE, and it is true far more broadly than stated**

No 3D case reached a PASS against an experimental reference with a pre-registration
on disk. Every candidate and why it fails:

| candidate | why not |
| --- | --- |
| **Ahmed body 25°** — 3D, experimental, prereg properly frozen | **No PASS.** Non-monotone ladder; Cd 0.3041 against 0.285, **+6.73 %**. The turn was **withdrawn** |
| **F8 / UAE Phase VI vs Hand et al. (2001)** | **No PASS** — *"NO VERDICT — and that is the result"*; no frozen prereg |
| **ONERA M6** | *"documented failure. The ninth act does not certify"* |
| **W3 cube / W3 wing family** | prereg'd, but arm no gate against experiment |
| **D5 square duct RSM** | reference is **DNS, not experiment**; *"two of four right"* |
| **B52 rung 6** | mesh replicates, no external reference |
| **T10a (thermal, 3D)** | `PASS` ×3, but against **closed-form view factors**, not experiment |

**The stronger fact this matrix actually found.** Under Ruling 4, look at the P column
across all five families: **the lab has never recorded a PASS against measured
physical reality under a frozen pre-registration — in any dimension.** Every place
the lab did compare against an experiment under a frozen spec, the honest answer was
**no**: F7a's dam break lands +7.8 % to +11.9 % against a 5 % band; the thermal
turbulent-cavity rows (Ampofo & Karayiannis; Betts & Bokhari) are `GATE FAIL`; the
Ahmed turn was withdrawn; F8 reached no verdict. **The one favourable experimental
comparison in the lab — dafoam's G-16 against AGARD AR-138 Case 2308 — has no
pre-registration**, so its "PASS" was written after the numbers were in hand.

**That is the week's most useful finding, and it is why the matrix was worth
building.** It is not a criticism of any team. It says the lab has built real
verification capability — exact solutions, manufactured comparisons, correlations,
and now four converging grid ladders — and has **not yet closed a single validation
loop against the world under a frozen gate**. The `HOLDS` tier is empty for a
specific, nameable, fixable reason.

**⚠ §7's proposed remedy is UNSOUND and should not be acted on as written.** It says
*"A 3D case with a clean triple and an experimental reference — **the Ansys VM cases
are exactly this shape**."* They are not, on two counts:

1. **They are not 3D.** VMFL001 is a concentric-cylinder annulus and VMFL005 a pipe.
2. **Their reference is not experimental and not public.** It is the Ansys VM2026R1
   manual, which those very records mark **proprietary Ansys documentation**. A
   proprietary vendor manual is the opposite of a public primary source, and the
   VMFL005 value is in any case **the Hagen-Poiseuille exact solution** — a `V`
   reference under Ruling 4, not a `P` one.

**The Ansys cases are the lab's cleanest G. They are not a route to P.**

**The genuine nearest candidate is 2D and already written: F12.** RAE 2822 / AGARD
AR-138 Case 9 — public, experimental, **pre-registration frozen 2026-07-30 before any
solver**, admission gates A and B plus Gates 1–3, and an overall PASS rule already
fixed. It has **never been run**. If the lab wants its first `HOLDS`, F12 is the
shortest path to it that does not require writing a new pre-registration — and its
gate could genuinely fail, which is the point.

**ADOPTED 2026-08-25.** The chief has adopted F12 as the lab's shortest path to a
first `HOLDS` and routed it to cfd. **The chief also withdrew the earlier briefing
position that the Ansys campaign was a route to `P`**, on this section's evidence.
That correction is recorded here rather than in a private exchange because the
withdrawn claim had already been briefed, and a claim that circulated should be seen
to be withdrawn.

---

## 5. The Richardson-sign cross-team audit — one instrument, one convention

**18 distinct implementations exist across 22 files. All 18 agree on the observed
order and on the GCI to the last bit; they split exactly two ways on the extrapolate,
and the split is the sign.** Fed one shared triple with a known analytic answer
(`f = 1 + 0.01h²`, r = 2, so p = 2 and the limit is 1.0 exactly), every implementation
returned **p = 1.9999999999999973** and **GCI = 1.2376237623762418 %**; the
extrapolate came back **1.0** from thirteen and **1.02** from five. The error is not
small — **1.02 against a true limit of 1.0 is 2 % of the value and 100 % of the
correction, which has the wrong sign** — and it is invisible on a printout because
1.02 sits plausibly between the levels.

**RULING — the lab standardises on `/home/ubuntu/Certonomous/scripts/roache_triple.py`,
with N-T8's convention verbatim: `f_ext = f_f + (f_f − f_m)/(r^p − 1)`.**

**This supervisor read that instrument's arithmetic personally, as a diff**
(`SUPERVISION_CHARTER.md` §3 check 1 — it may not be delegated, and a lane's test is
evidence, not the read). What I verified with my own eyes:

- `richardson = f_fine − e21/den` with `e21 = f_med − f_fine` **is** N-T8's registered
  form, algebraically identical.
- The defective form is returned **beside** it as `richardson_parent_convention`,
  under a name that says it is wrong — so a reader holding a published thermal number
  can reconcile it without re-deriving the algebra. That matters because the frozen
  T-family records can never be edited.
- **Both the equal- and unequal-ratio paths return `EXACT`, `OSCILLATORY`,
  `DIVERGENT` and `STAGNANT` before any GCI key is created**, so a non-monotone triple
  physically cannot carry a GCI — and a belt-and-braces assertion re-checks it.
- A second assertion requires the final verdict to be the band verdict or
  `NOT A RESULT` — rule 5's one-way door, enforced in code.
- It **refuses** on `r <= 1.0` rather than degrading (rule 4), and `dim` is required
  and asserted with no default.

**Its `--selftest` returns 53/53, and it imports both parents and cross-checks against
them live — so its provenance claim is executable rather than a comment.** Under rule
6 that is the only kind of citation that cannot rot.

**Adopting one instrument going forward is NOT retiring five, and I have not retired
anything.** `analyse_t1c.py` and `analyse_t3.py` are byte-frozen with hash identities
that other code refuses on; editing them would break running checks. The sidecar
addenda are the right disposition and they stand. **Retiring a standard is reserved to
Sanaa.**

### 5.1 "Display-only" is correct at every defective site, and FALSE as a lab-wide sentence

heat-transfer's conclusion was re-derived here rather than relayed, and it holds
**within its scope**: across the whole repository there is **not one comparison
outside a `--selftest` whose operand is an extrapolate** at a defective site. Every
defective site writes the extrapolate into a record and nothing reads it back. The
trace's own two un-adjudicated residues (`f9_criteria.py`, `4G/ladder.py`) were driven
and **both carry the correct form**. **No verdict moved and none could have.**

**But N-T8's registered sentence — *"No verdict in this lab was ever a function of a
Richardson value"* — is too broad, and there are two counterexamples:**

1. **`sdk/chief_engineer/uq.py`.** `_asymptotic_guard` tests whether the extrapolate
   lands inside the fit triple's range ± 0.15; that boolean sets `conclusive`, which
   is consumed by eight call sites and **selects the band formula itself**. Driven on
   an engineered triple, the correct form gives `conclusive: False` with a
   factor-3 fallback band; the defective form gives **`conclusive: True`** with a GCI
   band. The defective sign makes the extrapolate land **inside the range by
   construction, always** — so that guard would pass unconditionally and certify
   exactly the ladders its own docstring exists to reject.
2. **The ansys coverage tiers.** VMFL005's and VMFL001-R2's V columns are functions of
   a Richardson value, and **under the defect the two tiers exchange places** —
   VMFL005 would read V green and VMFL001-R2 V red, the exact inverse of the truth.

**Both surfaces carry the CORRECT form, so nothing actually moved.** But
*"display-only"* is a property of **where the defective code happens to live**, not a
property of the defect. **Referred to heat-transfer as a narrowing of N-T8** — that
fact is theirs, not this team's, and the accurate sentence is *"no verdict that a
DEFECTIVE implementation feeds is a function of its extrapolate."* Two further facts
for that amendment: N-T8's header says *"four independent implementations"* while its
own body lists **five**, and the census confirms five; and its adopted rule binds only
*"every T-family and F14 comparator"*, so **by its own terms it does not reach**
`scripts/roache_triple.py`, the ansys graders, `sdk/`, F3, F9 or 4G — several of which
conform anyway, unasked.

### 5.2 A worse defect found on the way: THREE implementations quote a GCI on a DIVERGENT triple

This was not the question asked, and in this team's judgement it matters more than
the sign — **a wrong extrapolate is display-only everywhere it currently lives; a
negative GCI printed beside a `PASS` is a quoted uncertainty on a row rule 5 says is
`NOT A RESULT`.**

Planted the divergent triple 1.00 / 1.02 / 1.05 (error **growing** under refinement,
increments same-sign so a sign-only guard misses it) and read back:

| implementation | returns |
| --- | --- |
| `verification/runs/F14-cooling-ladder/K0b_D403_rerun/analyse_k0b_mesh.py:318-321` (and its D406 and `mesh_sensitivity` copies) | p = −0.5850, extrapolated 0.96, **GCI_fine_pct = −10.714 %** — a **negative GCI**, `reason = None` |
| `verification/runs/4G_runs/bump_iteration_matched/ladder.py:63-66` | same |
| `sdk/workflows/tmr_verification.py:199` | `observed_order` returns **−0.5850** rather than `None`, and the GCI then divides by `2^(−0.585) − 1 < 0` |

All three guard **only** on increment sign change, never on `p <= 0` or
`p < STAGNANT_FLOOR`. **The K0b instruments are the ones N-T8 holds up as correct** —
and on the extrapolate sign they **are**. They are not correct on rule 5's class
taxonomy. `scripts/roache_triple.py` and eleven others refuse a divergent triple
before any GCI is formed.

**`sdk/workflows/tmr_verification.py` is the flat-plate ladder's own instrument**, so
this is not hypothetical for the matrix's own strongest G row.

**OWNED, NOT REFERRED — routing corrected 2026-08-25 on the chief's override, and the
override was right.** This team's first instinct was to refer the trace to cfd and
heat-transfer. The chief overrode that, on the reasoning that **a defect spanning
three implementations across two territories has no owner when it is split between
two families — each will reasonably assume the other holds the load-bearing half.**
Cross-team gate audit is this team's entire charter purpose, so the trace is this
team's. Two lanes are running it.

**The question being traced, stated so the answer cannot be softened into a
reassurance:** *is there any number — in any record, certificate, RESULTS file, JSON
artifact or published figure — whose uncertainty was quoted from one of these three
implementations while the triple behind it was NOT CONVERGING?* **Not "could there
be". Traced.**

**Why it is worth the compute even though the expected answer is nothing.** Under
rule 5's one-way door a gate may only turn a PASS or GATE FAIL **into**
`NOT A RESULT`, never the reverse — so a row scored with a negative GCI beside it has
a tier wrong **in the favourable direction**, which is the direction that costs the
lab. And a negative GCI is wrong **twice**: it is quoted on a row that is not a
result, and it points the wrong way, saying the answer is **better**-determined than
it is.

**Both lanes plant a positive control BEFORE reporting any null** (rule 3 — a zero
from a reader not shown able to see a non-zero is not evidence), in each shape the
real artifacts use: a JSON key, a markdown table cell, a prose sentence, a figure
caption. **Any shape the sweep cannot see is a hole in the null and is reported as
one.** The sdk lane additionally re-derives the flat plate's own six triples through
the guarded `scripts/roache_triple.py` — because the row that refuted a lab-wide
standing fact tonight should not rest on an instrument that cannot refuse.

**A traced null, with its method named, is a real result and closes the item.**

### 5.2a RESULT — K0b (×3) and 4G: **TRACED NULL.** Nothing published rests on a non-CONVERGING triple

**Answer: NO.** No number in any record, certificate, RESULTS file, JSON artifact or
published figure has its uncertainty quoted from these four implementations while the
triple behind it was not CONVERGING. **Rule 5's one-way door is not breached by any of
the four.** This closes the K0b and 4G half of the item.

**THE CONTROL FAILED FIRST, AND THAT IS THE MOST IMPORTANT LINE IN THIS SECTION.**
The lane planted `GCI = −10.714` and `p = −0.5850` in eight shapes and swept for them
**before** concluding anything. **The first detector missed the markdown-table-cell
shape** — its numeric-row test required a line to begin with a digit, and a real table
row begins with a **label**. The detector was rebuilt to carry a "table whose header
named a GCI/order column" context to the end of the block, and re-controlled: **all
eight shapes then fired** — JSON key structurally and as text, table cell in row 1 and
in row 6, prose sentence, plain-text log line, HTML figure caption, whitespace-column
`.dat` row, CSV row.

**Had the null been reported from the first detector it would have been a FALSE NULL,
blind to exactly the shape the lab's records use most.** That is rule 3 working as
intended: *a zero from a reader not shown able to see a non-zero is not evidence* —
and here the reader **was** shown unable, and was fixed before it was believed. **A
null is worth precisely what its control is worth.**

**A code-side control was run too**, and it locates the defect precisely: on the
divergent triple all four functions return `p = −0.5849625007211563`, GCI
`−10.71428571428572`, `reason = None`; on the sign-change triple 1.00 / 1.05 / 1.02
**all four correctly REFUSE**. **The guard exists and works — it is simply the wrong
guard.** It tests increment sign change and never `p <= 0`.

**The trace itself:** all six K0b triples classified from their own stored values are
**monotone and CONVERGING** (|d32/d21| 0.127–0.297, p 1.7529–2.9824, GCI 0.063 %–0.784 %,
all positive), and all three `k0b_mesh_sensitivity.json` files are byte-identical to
their HEAD blobs. The five negative GCIs in `k0b_d403_regrade.json` belong to the
un-continued 128×128 leg and **reach no record**: `K0b_D403_RERUN_RESULTS.md` §6 prints
the `p` column and **omits the GCI column entirely**. The direction is the safe one —
that block is cited to support **`V3 = GATE FAIL`** and to expose the leg as
*"iteration error wearing a mesh study's clothes"*. For 4G the negatives **are** in a
HEAD-committed record, and are published **as the demonstration of the defect**: the
record's own footnote says the n = 2,000 row *"is here to show the pole, not to quote a
number through it"*. Every row carrying a real conclusion is CONVERGING (matched
n = 9,000: p 0.516, GCI 4.26 %; published caps p 0.5446, GCI 3.839 %). **Nothing was
moved from `NOT A RESULT` into a `PASS`.**

**Three residual defects are real and must not be read as harmless:**

1. **The guard is the wrong guard in all four files.** The null holds on today's data,
   not by construction.
2. **A negative GCI is sitting in two HEAD-committed artifacts** —
   `verification/runs/F14-cooling-ladder/K0b_D403_rerun/grade_d403.txt` (in a `GCI %`
   column) and `verification/campaign/4G_tmr_mesh_aspect_ratio.json` — **where a future
   reader can lift it** without the surrounding prose.
3. **Only the surrounding prose, not the instrument, is doing the honest work.** That
   is the whole finding: the records are honest because their authors were careful,
   and the instrument would not have stopped a careless one.

**Two defects owed to cfd as dated corrections, found while tracing:**

- **A factual error stated TWICE in HEAD.** `verification/campaign/4G_tmr_mesh_aspect_ratio.md`
  §10.3 and its JSON's `iterative_error_verdict` both say *"at n = 2,000 the increments
  cross."* **They do not cross** — both are positive (+7.534e-05 and +7.547e-05); they
  nearly **equalise**. The footnote gets it right (*"p passes through zero"*); the body
  sentence does not. **Under rule 5's vocabulary that row is `DIVERGENT`, not
  `OSCILLATORY`.**
- **`4G_runs/bump_iteration_matched/ladder.py` carries the D403 blindness the K0b script
  was repaired for.** Its `PUB` path under `demo-output/website/tmr/runs/` no longer
  exists after the R20/R21 move, and **it does not refuse** — `os.path.exists` returns
  False and it silently continues on local re-run histories. `analyse_k0b_mesh.py`
  **refuses** in the same situation. **Measured consequence today:** a re-run gives
  n = 3,000 as p = 0.4410 / GCI 5.416 % against the recorded 0.4416 / 5.406 %. A
  comparator that silently continues on a moved path is the D403 defect exactly.

**One live alarm defused before anyone re-discovers it.** `gate_t1b.json` rows 0/2/4
read `verdict: PASS` beside `grid.state: DIVERGENT` with a `band_pct`, which looks like
a rule-5 breach and is not: **that band is NOT a GCI**, it is the pre-registered
Dittus-Boelter/Gnielinski half-spread from `T1b_band.json` (0.8789 = (31.78566 −
30.02785)/2). `docs/campaigns/T-family/T1b_L4_AMENDMENT.md:126-129` already records
those four rows, **is the origin of CLAUDE.md rule 5**, and deliberately leaves the
JSON un-rewritten. **Known, adjudicated, superseded.** By contrast `gate_t3.json` and
`gate_t10a.json` return `NOT A RESULT` on their DIVERGENT rows and quote no band —
the reference behaviour.

**Coverage limits stated rather than glossed:** 35 files over an 8 MB cap (solver logs,
adjoint dumps, mesh JSON; the two large JSONs spot-checked, zero GCI tokens); ~45.4k
compressed files under the out-of-repo roots unread (the 533 in-repo `.gz` were
`zgrep`ped); **binary formats entirely** — a GCI rendered into a PNG would be invisible,
mitigated by `demo-output/` carrying **no GCI token in any source form**; and
extensionless OpenFOAM dictionaries. `git status` was **not used as an instrument**;
HEAD was asked directly.

**Cost: reads only, no solver, no container. No core-minute figure is quoted, because
none was measured** — rule 12 forbids calling a cost measured without a record behind
it, and an unmeasured single-core read is not worth inventing one for.

**The sdk / `tmr_verification.py` half of this trace — the flat plate's own instrument
— is still running and is NOT covered by this null.**

---

## 6. A four-file pattern: the worktree copies of the lab's ledgers are STALE

Measured on four files during this audit, three of them independently:

| file | worktree | HEAD |
| --- | --- | --- |
| `docs/LAB_STATE.md` | 870 lines | 1,173 — **303 short** |
| `docs/COST_CALIBRATION.md` | max **C-43**, later **C-48**, 168,635 B | max **C-47**, later **C-49**, 181,803 B. **Both readings correct at their stamps — see §6a.2** |
| `docs/NUMERICS_KNOWLEDGE.md` | **254,652 B, and DOES NOT CONTAIN N-T8 AT ALL** (0 occurrences) | **312,617 B**, N-T8 present (2 occurrences) |
| `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | 1 row, *"0 PASS of 1 run"* | 3 rows, *"2 PASS of 3 run"* |

**The consequence is not untidiness, and the sharpest instance is this team's own
standardisation.** §5 rules that the lab standardises on `scripts/roache_triple.py`
with **N-T8's convention**. **N-T8 does not exist in the worktree copy of
`docs/NUMERICS_KNOWLEDGE.md`** — 0 occurrences against 2 at HEAD, a **57,965-byte**
shortfall. **So a lane that opens that file to check the very convention this matrix
just standardised on will not find it**, and will reasonably conclude no convention is
registered. A lane that reads the ansys
register sees a credential count that is wrong. And a lane that *edits* any of these
from the worktree **reverts everything a peer landed since the copy went stale** —
303 lines, in the LAB_STATE case.

**The rule this team now applies and recommends lab-wide: these files are HEAD-only.
Read them with `git show HEAD:<path>`, and rebuild from HEAD content before writing.**
Every commit this team made to `docs/LAB_STATE.md` today was built that way, which is
why they are insertion-only.

---

## 6a. INSTRUMENT VALIDITY — how every row in this file was checked, and the audit of that audit

**`git status`, `git diff HEAD`, and anything else consulting the SHARED git index
are NOT VALID INSTRUMENTS in this repository.** This is not an incident to be cleared;
it is structural. Rule 10's private-index protocol **by design never writes the shared
index**, so **every file any team commits widens the gap by one entry**. The chief
cleared it tonight — **443 staged deletions and 63 staged modifications, every sampled
staged blob a HISTORICAL version of its file** — and a re-reading a short while later
found it **decayed again inside the same session (11,067 against 11,089)**. Clearing
it is a treadmill, not a fix.

**CORRECTED 2026-08-25. This section originally cited FOUR measured misreadings. TWO
DO NOT HOLD and are withdrawn here rather than quietly dropped**, because this file
had already been committed and cited when the correction arrived. The chief, who
supplied the original four, withdrew two of them on its own re-check.

| claim | status |
| --- | --- |
| a file reported **entirely deleted** while present and correct | **HOLDS** |
| **phantom `D` / `MM` rows with no writer** | **HOLDS, and now MEASURED rather than asserted: 8 of 8 sampled `D ` rows were present at HEAD and correct on disk** |
| ~~a docket misdiagnosed as "47 lines behind HEAD" when the worktree was **ahead** in a preserved-tail pattern~~ | **WITHDRAWN as stated.** A documented docket misreading does exist, but it is a **different shape and figure**: disk **849** against HEAD **876**, **27 ids missing from disk** — i.e. genuinely **behind**, not ahead. The "ahead" version is unsupported |
| ~~clean status over genuinely dirty files under concurrency~~ | **WITHDRAWN.** It comes from a working note, **not from any repository artifact**, and the lane that checked it did not reproduce it and correctly refused to cite it as measured |

**Two misreadings still establish the rule**, and the withdrawal costs the argument
nothing — but a rule argued from four instances when two are real is a rule that
invites exactly the scepticism it cannot afford.

### 6a.0 This finding is NOT NEW, and saying so is the point

**The structural index argument was already codified three times before this file
restated it.** This section originally presented it as a discovery. It is not one:

- **`L-92`** holds the entire **read** side, including the *"grows on its own"*
  measurement — an instrument reading the index measures a per-machine, per-moment
  scratch state no reader of the repository will ever see.
- **`L-253`** holds the **write** side almost verbatim: *"always take the base for the
  next edit from `git show HEAD:<path>`, never from the tree."*
- **`L-294`** fixes the **instrument** rule: `git ls-files` reads the INDEX, so any
  corpus is framed on `git ls-tree -r --name-only <rev>` **and prints the rev**.
- **`L-307`** landed 2026-08-25 as an explicit **extension** citing all three rather
  than a restatement — deliberately, to avoid repeating the **`L-185`/`L-205`
  duplication defect the lessons file has already committed once.**

**And `docs/COST_CALIBRATION.md` lines 40–52 already carry the per-file warning**,
headed *"Divergence-by-design"*, which is why a proposed addition to it was correctly
declined as redundant.

**The lesson for this matrix is uncomfortable and worth keeping.** This team wrote a
section warning that unchecked claims propagate, and in the same section propagated an
unchecked claim of its own — that the finding was new. **Re-deriving a fact is cheap;
checking whether the lab already knows it is the step that gets skipped.** L-307's
own framing is the model: cite the prior art and state what you ADD.

**What `L-307` genuinely adds, and it is sharper than the version this file first
carried:** the gap is **NON-STATIONARY, not merely stale — its size AND ITS DIRECTION
change within minutes, so every figure about it is void without a sha and a UTC
stamp.** The decay was originally described as *"mechanical drift plus fresh
staleness"*. **There is no separate fresh-staleness category.** Across 9 peer commits
the tree gained **672 insertions against 3 deletions**, and staged deletions grew by
exactly **669 = 672 − 3**. **The decay rate does not merely correlate with the commit
rate; it EQUALS it, line for line.**

**Why this section sits inside the coverage matrix and not only in a lesson.** This
file's entire value is that its rows were *checked*. Spot-checking a row means asking
whether an artifact exists and whether a pre-registration is frozen — and **a
status-based reading can report a present file absent, or an unchanged file
modified**. **A row scored from a status reading is a row scored from a broken
instrument**, and it would be indistinguishable, on the page, from a row scored
properly.

**The instruments that work, and that this file's rows were re-checked with:**

| question | valid instrument |
| --- | --- |
| does this file exist in the repository? | `git cat-file -e HEAD:<path>` |
| what does it actually contain? | `git show HEAD:<path>` |
| what is in this directory? | `git ls-tree -r HEAD <dir>` |
| has the worktree copy diverged? | a direct `diff` of the HEAD blob against the worktree file |
| **never** | `git status`, `git diff HEAD`, `git diff --cached` |

### 6a.1 The audit of this audit — two claims re-checked HEAD-direct, and both survive

Two load-bearing claims in this file were originally read from `git status`. Both were
**re-derived with HEAD-direct instruments** before this section was written, because a
finding about broken instruments that does not re-check its own author's work is a
lecture rather than an audit.

1. **"Both contribution files were untracked."** Re-checked: **NOT a phantom.**
   `git cat-file -e 2bf4915a:<path>` confirms **both were genuinely absent at HEAD**
   at this session's start, and each was introduced later by a named commit — dafoam's
   at **`7d09e4c9`**, heat-transfer's at **`71ecb659`**. §2.1's dated correction is
   therefore accurate as written: the description was true when written and stopped
   being true shortly after. **The recovery finding stands.**
2. **G-16's AGARD artifact "tracked in git".** Re-checked HEAD-direct, not by status:
   `git ls-tree -r HEAD` lists
   `cases/dafoam/ladder-a/logs_A3/case_2308.dat`; `git cat-file -e` confirms it;
   **the HEAD blob and the worktree file are both 22,695 B**; and the title line was
   read **out of the HEAD blob itself** — `TITLE = "M6 WING - SURFACE PRESSURE
   DISTRIBUTIONS"`. The artifact is real, tracked, and title-verified from the
   repository's own object store rather than from a working file.

**No row in this matrix rests on a status reading.** Every other existence and
freeze check in §3 was made by hashing a file against its committed blob
(`git cat-file`), by reading a HEAD blob, or by reading the artifact on disk directly.

### 6a.2 The append trap, which is the same mechanism and will bite every team

The same decay makes **the worktree copy of any append-only shared record presumed
STALE**, and **editing one in place silently reverts peers' rows**. Measured:
`docs/COST_CALIBRATION.md`'s worktree copy was **four rows stale, carrying C-43
against HEAD's C-47** — an in-place edit would have reverted **C-44 through C-47**.
**Every team appends there under rule 12 at every process completion**, so this is
the whole lab's trap, not one team's.

**Build every append from `git show HEAD:<path>`.** Every commit this team made to
`docs/LAB_STATE.md` today was built that way, which is why each is insertion-only and
reverted nothing.

**CORRECTED, and the correction IS `L-307`'s point.** The C-43/C-47 figure above was
this team's own direct reading, taken early in the session and correct at that moment.
**Re-measured later the same session it reads worktree `C-48` against HEAD `C-49`,
worktree 168,635 B against HEAD 181,803 B** — and the chief reports the **shared-index
blob further behind still, at `C-47`**, so the three surfaces hold three different
values at once. **A figure about this gap is void without a sha and a UTC stamp**, and
the figure above is retained with its stamp rather than silently refreshed, because
that is the evidence for the rule. The **direction** of the finding is unchanged and
the append trap is real; only the integers move, and they move constantly.

**Not amended into `CLAUDE.md` by anyone.** Rule 9 reserves that to Sanaa, and no
agent's judgement — chief's included — is her consent. **Two proposals are already on
her desk, and this team is adding no third:** a rule-10 amendment at
`docs/BOARD_BASE_RULE_PROPOSAL.md` §2, which was there **before** a second was
commissioned, and `docs/SHARED_INDEX_INSTRUMENT_PROPOSAL.md`, written not to compete
and saying **which to adopt if only one is**. Both verified present at HEAD.

---

## 6b. ATTRIBUTION INTEGRITY — a new standing audit class, opened 2026-08-25

**Opened by this team as a cross-team audit pass.** The trigger: heat-transfer found a
block in its own records marked as **Sanaa's verbatim words** that a non-ignoring
`find | xargs grep` located **nowhere on disk**. Their supervisor did not hear it said,
would not vouch for it, and **withdrew the attribution while keeping the text**,
re-marked as a brief's paraphrase. Nothing depended on it. **That is exactly the right
handling** — and it establishes that the class exists.

**Why this is a verification matter and ranks above a wrong number.** A wrong number
meets a gate: some comparator, band or triple can catch it. **A wrong quotation from
the lab's principal meets nothing.** It becomes standing law and propagates into
charters, briefs and agent definitions, where every later agent reads it as authority
and has no instrument that could contradict it. **Nothing downstream can catch it.**

**Grading classes:** **A SOURCED** (traceable to a durable artifact recording her
saying it) · **B CORROBORATED-BY-REPETITION ONLY** (appears in several places, every
one a lab document citing another lab document, no originating record — the dangerous
middle) · **C UNSOURCED** (attributed verbatim, found nowhere else — high severity) ·
**D HONESTLY LABELLED NON-VERBATIM** (already marked a paraphrase or reconstruction;
not a defect, counted to establish the honest baseline).

**DRIFT is audited alongside fabrication and is likelier.** Where one quotation appears
in several places the wordings are diffed against each other. A quote that has gained
or lost words as it propagated is a defect **even when an originating record exists**.
One known-good quotation contains a typo — *"I apporve all actually"* — so **a variant
that silently CORRECTS that typo is itself evidence of drift**, because it proves the
text was retyped rather than copied.

**Priority is set by blast radius, not by count:** `.claude/agents/*.md` and
`harness/teams.yaml` first, because they are regenerated into **every agent's standing
instructions every session**; then `docs/charters/*_CHARTER.md`, which are law; then
`CLAUDE.md`; then `docs/LAB_STATE.md`.

### 6b.1 RESULT — **CLASS C IS EMPTY. There is no fabricated quotation anywhere in this lab.**

**41 distinct person-attributed quotations / 78 instances**, graded against **481
genuine Sanaa messages** (2026-07-26 → 2026-08-24) reconstructed from the session
transcripts:

| class | distinct | instances |
| --- | --- | --- |
| **A — SOURCED**, byte-exact against her own messages | **18** | 31 |
| **B — corroborated by repetition only** | **1** | 2 |
| **C — UNSOURCED** | **0** | **0** |
| **D — honestly labelled non-verbatim** | 68 marker lines | 42 files |
| **DRIFT** — sourced, but the wording changed | **17** | **~68 locations** |

**The audit's own premise was wrong, and that inversion is the finding.** It was opened
because heat-transfer appeared to have found a fabricated quotation. **It had not.**

### 6b.2 THE REAL DEFECT — three teams withdrew TRUE directives, because the lab has no instrument that can see what Sanaa said

**All three withdrawals standing in the record are OVER-CORRECTIONS. In every case the
words are genuinely hers.** Each team behaved correctly in procedure — searched, found
nothing, and withdrew rather than asserted — and each was **factually wrong for the
same reason: they searched THE REPOSITORY, and her words live in THE SESSION RECORD,
which is not in git.**

| team | what was withdrawn | the fact |
| --- | --- | --- |
| **heat-transfer** | the 18-combination zero-pass block, re-marked *"a brief's paraphrase, not Sanaa's words"* | **byte-identical to a message she sent three times on 2026-08-24** (18:56:35Z, 18:59:19Z, 19:00:48Z) |
| **cfd** | the conversion-batch directive, `docs/LAB_STATE.md:1212` | **ratio 1.0000** against §2 of the same message |
| **closure** | D514 draft: clauses (b) TBNN-fallback and (c) parallel-capacity, ruled `ATTRIBUTED-BUT-UNCORROBORATED`, consequence *"NOTHING IN CLOSURE MAY LEAN ON THEM AS AUTHORITY TO RUN"* | **ratio 1.0000.** **This one is BLOCKING WORK on a false premise** |

**This supervisor verified the closure case personally rather than relaying it**, since
it would unblock another team's work. The message is a **genuine `user`-role,
non-sidechain record** — not a task-notification, not a system-reminder — carrying
*"R3 is ratified (SpaRTA-class, TBNN fallback) — R4's CPU-minutes run in parallel; they
never displace consolidation work."* and *"R4 (SpaRTA build) runs in parallel on its
CPU-minutes; FS gates apply."* **The premise of the block — that the words cannot be
found — is false.**

**THE HONEST CAVEAT, WHICH THIS TEAM WILL NOT RESOLVE AND CANNOT.** The message is a
block Sanaa **pasted**. This supervisor confirmed at the source that it is written **in
the third person about her** (`"Sanaa's directive"`) and carries **agent-role tags**
(`[FABLE...`, `[OPUS...`). **She issued it — it is an instruction sent under her name.
It is not her original prose.**

**So both the attribution and the withdrawal are wrong, in opposite directions.**
Marking it *"Sanaa, verbatim"* overclaims; marking it *"a brief's paraphrase"*
underclaims to the point of blocking work she authorised. **The accurate label is a
third thing the lab has no vocabulary for — a directive ISSUED by her, from
lab-drafted text she adopted and sent.** Whether that counts as "her words" is
**Sanaa's to rule, not this team's and not the chief's.**

**But authority and verbatimness are different questions, and only one of them is
open.** She sent it under her name; that is not in doubt. **The `ATTRIBUTED-BUT-
UNCORROBORATED` finding rested on "we cannot find it", and that premise is now
falsified.** Closure's supervisor should re-decide on the corrected facts.

### 6b.3 THE INSTRUMENT FAILED THREE TIMES IN ONE AUDIT — including twice for us

**This is the most transferable thing in this section.**

1. **The three teams' instrument** searched the repository. Her words are not there.
2. **The audit lane's own first-pass corpus missed 240 of her 481 messages** — every
   message she **queued** while an agent was working is stored as a `queue-operation`
   record, not a `user` record. Rebuilding against that channel **moved nine
   quotations from "unsourced" to "sourced", including the one about to be reported as
   the audit's worst finding.** *(This supervisor confirmed the channel exists
   independently: 10,330 `queue-operation` records against 106,870 `user` records.)*
3. **This supervisor's own verification grep was blind to 13 of 24 locations.** A
   line-based `grep` found **11** files carrying the rule-16 directive; a
   newline-tolerant scan found **24** — because **twelve charters wrap the quotation
   across lines** and a line-anchored pattern cannot see it. The lane's first detector
   failed the same way on markdown table cells (§5.2a).

**Three independent instrument failures of one class — a reader that cannot see the
shape the thing is actually stored in — in a single audit.** Each would have produced
a confident, wrong, *reassuring* answer. **A null is worth precisely what its control
is worth**, and here the controls were what caught all three.

### 6b.4 DRIFT — the lab retypes Sanaa rather than copying her, and silently fixes her spelling

**17 drifted quotations across ~68 locations.** The dominant mechanism is **silent
typo-correction**, verified by this supervisor at the source for the highest-blast-radius
case:

**Rule 16, the silent-background directive — 24 locations, and NOT ONE preserves her
spelling.**

- **She typed** (2026-08-23T19:54:49Z, as **item 4 of a numbered list**): *"...act in a
  silent way on the **backrgound** without showing bash or ssh on the screen, the
  screen must always remain clean **wit** only discussion and results."*
- **Every one of the 24 says** *"back**g**round"* and *"wit**h**"*. **Zero files carry
  `backrgound`.** Every copy also presents it as a standalone directive with **no
  elision mark** for the list it came from.
- Distribution, counted newline-tolerant at HEAD: **12 charters + 10 agent definitions
  + `CLAUDE.md` + `harness/teams.yaml` = 24.**

**And it is ONE error copied 24 times, not 24 errors.** The session record shows the
corrected form already in circulation **about 90 seconds after she typed it** — the
drift entered **at first transcription**, and all 24 locations inherited it from that
single retype. **The ten agent definitions and `teams.yaml` are regenerated into every
agent's standing instructions every session, so two corrupted words are read as law by
every agent the lab spawns.**

**Other drift worth naming:**

- **A FALSE PROVENANCE CLAIM in a charter.** `docs/charters/SUPERVISION_CHARTER.md:603`
  says a second quotation came *"earlier in the same message"*. It was a **separate
  message 89 seconds later** (18:59:19Z vs 19:00:48Z). **Both halves of the clause are
  wrong**, inside a dated addendum that presents itself as the careful record.
- **A SEMANTIC substitution, not a typo fix** — `docs/DOCKET.md:836` and
  `docs/campaigns/T-family/EXPERTISE_CURRICULUM.md:10`: she wrote *"the designated heat
  transfer **case** can run them"*; the repo says *"**team**"*. **The lab corrected her
  meaning.**
- **An ellipsis that elides the load-bearing detail** —
  `.claude/agents/ansys-verification-supervisor.md:119` and `harness/teams.yaml:434`
  quote the lane-cap authority with `...` where **`(5 and 4.8)`** stood: the model
  identities, **which is exactly what the cap clause turns on.**
- **`R3:Sparta` → `R3: Sparta`** — a space inserted into closure's two-word founding
  authority, at 14 locations.
- **Five silent corrections in one "verbatim" quotation** at
  `docs/inventory/2026-08-24/LAB_INVENTORY.md:5`, plus a dropped opening sentence with
  no ellipsis.
- **A LIVE INTERNAL CONTRADICTION inside one file**: `docs/LAB_STATE.md:1212` records
  cfd's withdrawal while **`:1297` of the same file still cites the withdrawn text as
  "Sanaa's §2 directive (verbatim)"** — and that surviving copy is itself abridged.

### 6b.5 The exemplar, and the one Class B item

**`docs/charters/ANSYS_VERIFICATION_CHARTER.md:12-25` is the only long quotation in the
lab with ZERO drift** — ratio **1.0000**, byte-identical, preserving `ansy-verification`,
`anf`, `th everification`, `lessosns`, `verfication`, `bc` — **and it is the only record
that states the copying rule**: *"Recorded character for character, spelling included;
the spelling is hers and is not corrected because the quotation is the authority."*
**That is the standard, it already exists in this lab, and it should simply be copied.**

**Class B, the single item: the compute rate**, `CLAUDE.md:140-143`. `c7a` appears **0
times** in her 481 messages; `0.0513` appears 3 times, **all three inside lab-authored
reports she pasted back**. The cited corroboration is a lab pre-registration reusing the
same figure, so the chain runs **constitution → lab document → same number** and
**terminates without an originating record**. **Mitigating and material: the
constitution already labels it *"reported-by-owner, not measured"*, so nothing treats
it as measured.** A provenance defect, not a numerical one.

### 6b.6 What this team will NOT do, and what goes to Sanaa

**Nothing here is fixed by this team.** No attribution is restored, no withdrawal
reversed, no quotation normalised. Each belongs to its owning team, and **the two
governing questions belong to Sanaa alone:**

1. **Does a work order she pastes and sends count as "her words, verbatim"?** No
   current record draws the distinction, and three teams' withdrawals turn on it.
2. **May the lab silently correct her spelling when quoting her?** The ANSYS charter
   says no and is the only record that asks. **24 locations currently say yes by
   default.**

**Coverage limits, stated plainly:** nothing before 2026-07-26 (earliest transcript);
deleted or rotated transcripts are undetectable; **other machines are invisible** — she
confirmed on 2026-08-24 she runs multiple windows; verbal or out-of-band instruction is
unreachable, **which is why the compute rate is class B and not class C**; PDFs and
binaries unsearched. **And the corpus was wrong once already** — the
`queue-operation` discovery — **so every absence in this section is provisional on
there being no further message channel nobody has found.**

**Cost: 0.0 core-minutes**, predicted 0.0, actual 0.0, ratio 1.000 — reads, greps and
diffs; no solver, no run directory, no GPU. **No verdict-vocabulary word applies to an
audit report and none is claimed.**

---


### 6b.7 THE SUPERVISOR'S OWN VERIFICATION OF §6b.1–§6b.6, and the NEAR-MISS CONTROL it establishes

**§6b.1–§6b.6 above were written by a lane that was killed by the weekly usage limit at
~00:50Z. Its work survived on disk, uncommitted, and is recovered here.** The
supervisor who commissioned it was killed with it. **A relayed check is a summary, not
a check** (`SUPERVISION_CHARTER.md` §3), and the verification recorded inside §6b.2 was
performed by that predecessor. **It does not transfer.** This successor re-verified the
load-bearing claims personally, at source, before committing any of it.

**Two defects in the recovered draft, repaired here, disclosed rather than tidied.**
(1) The dying lane appended a **byte-identical duplicate of §6a and §6b** (182 lines)
after its own results — the `L-185`/`L-205` duplication shape the file had explicitly
set out to avoid. Verified byte-identical against the HEAD blob and **dropped**; no
content is lost. (2) Its results were numbered §6b.1–§6b.6 inside §6b, which is kept.

#### What this supervisor re-measured, and it holds

| claim in §6b.4 | this supervisor's independent measurement | result |
| --- | --- | --- |
| She typed `backrgound` and `wit` | Her message located at source, **2026-08-24, `user` role, `isSidechain: false`**, as **item 4 of a numbered list**: *"…must always act in a silent way on the `backrgound` without showing bash or ssh on the screen, the screen must always remain clean `wit` only discussion and results."* | **CONFIRMED to the character** |
| **Zero** repository files preserve her spelling | Newline-tolerant sweep over every tracked `.md`/`.yaml` at HEAD | **CONFIRMED — 0 files** |
| **24** locations carry the corrected form | Same sweep | **CONFIRMED — exactly 24** |
| closure's two withdrawn clauses are genuinely hers | Located at source: *"R3 is ratified (SpaRTA-class, TBNN fallback) — R4's CPU-minutes run in parallel; they never displace consolidation work."* | **CONFIRMED present** |

#### THE NEAR-MISS CONTROL — rule 3 applied to a search, and it fired on this supervisor's own grep

> **An audit that reports a phrase UNSOURCED must first demonstrate, on the same
> corpus and with the same command, that its search can find a NEAR-MISS: an
> instance it would plausibly have missed and did not. A control that fires on an
> easy hit proves only that the tool runs. Until the near-miss fires, a zero is an
> under-count of unknown size, not a finding.**

**This is CLAUDE.md rule 3 applied to a search**, and a documentary sweep needs it more
than a comparator does, because **an UNSOURCED verdict is the loudest negative the lab
can publish about its own principal and is produced by the instrument least able to
refuse.**

**It fired against this supervisor, on this very check.** Searching the 24 rule-16
locations: a **line-anchored** grep found **11 files**; the **newline-tolerant** scan
found **24**. **Thirteen of twenty-four invisible to the obvious command** — because
twelve charters wrap the quotation across a line break. Had this supervisor reported
from the line-anchored count, the drift finding would have been understated by more
than half.

**Measured in both directions, by three teams, this session:**

- **FALSE UNSOURCED at a 50 % rate.** `L-308` (ansys-verification): a naive
  `git grep -Fl` found **2** files for *"exclusively work on these verification
  cases"*; whitespace-normalised found **4**. The two missed were
  **`harness/teams.yaml`, the roster source of truth, and `ANSYS_VERIFICATION_CHARTER.md` §1**.
  A prior lane had already reported *"UNSOURCED, 2 hits, high severity"* on the naive
  count. **`git log -S` is line-bounded too** (`L-61` addendum, `dee8f024`).
- **A MISS CAUSED BY THE PRINCIPAL'S OWN TYPING.** dafoam's exact-string search missed a
  genuine user turn because her raw text reads *"for theheat transfer"*; it surfaced
  only on a typo-variant search, and the team **corrected itself** (`ae21ae6c`).
- **THE HONEST SCOPE LIMIT, stated against its own interest.** `L-308` re-tested on a
  different withdrawn attribution: normalisation changed **nothing**, 1 hit either way.
  **The blindness does not invalidate phrase audits in general.**

**PRIOR ART, credited — and this team was already caught once this session presenting
settled prior art as new (§6a.0).** The discipline was **already practised,
independently and unprompted, by closure** at `39340d3d`: *"EVERY NEGATIVE CARRIES A
FIRED CONTROL, rule 3's discipline applied to a documentary search."* Closure ran three
paired controls **before** withdrawing four attributions. **This section names an
existing practice; it does not introduce one.**

**Scope, and where the wider version goes.** This binds **THIS TEAM'S OWN AUDITS**. It
constrains what a verification audit may **conclude**; it gates no commit and obliges no
other family. **A lab-wide binding form is a gate on lab process, and adding a gate is
reserved to Sanaa exactly as retiring one is** — the same ruling this team applied to
itself over `check_threshold_resolution.py`. It goes to her desk as a proposal, **not
into a charter on this team's say-so** (rule 9).

### 6b.8 ⚠ THE CONSOLIDATION-WEEK DIRECTIVE IS **NOT LOST**. It is recoverable, and this file's §0 rests on a reconstruction that is now checkable

**The single most consequential recovery of this session, and it is against this file's
own foundation.** `docs/LAB_STATE.md`'s chief section records the week's directive as
irrecoverable: *"the directive was issued in a session transcript that has since been
compacted"* and *"the chief does not hold her wording."* **That is false.** Located by
this supervisor at source: **three `user`-role, `isSidechain: false` records** on
2026-08-24 at **18:56:35Z, 18:59:19Z and 19:00:48Z**, ~5,700–5,800 characters each.

**The three sends are NOT identical to each other** — send 3 closes *"for now this
means we are using ops 5 for anything needig fable temporarily"* where send 2 reads
*"this set of instructions mean that for now anything requiering Fable 5 uses OPus 5
temporaril"*. **Any future citation must name which send.**

**THE RECONSTRUCTION IS SUBSTANTIALLY FAITHFUL, AND IT LOST ONE STRUCTURAL THING.** The
three columns V / G / P, the five tier words and their glosses, the derived-not-asserted
rule and the HOLDS spot-check all match her text. **But the ROWS do not.**

> **Her text:** *"Rows = problem classes: dimension (2D / axisym / 3D) × regime
> (laminar steady / laminar unsteady / turbulent RANS steady external / internal /
> URANS / transonic / supersonic / hypersonic / multiphase-free-surface /
> buoyant-thermal / conjugate / radiation / adjoint-gradient / adjoint-optimization)"*

**This file's own title is *"one row per case"*. Her directive says one row per PROBLEM
CLASS**, and her opening sentence says why: *"this week is about being able to POINT at
problem classes — by dimension, regime, difficulty, physics type — and say: 'the lab ran
this class; it is verified, validated, and converged; this is a category the lab knows
how to handle.'"* **The matrix as built answers a different question from the one she
asked.** The case rows are not wasted — *"the matrix is derived from records, never
asserted"* is her rule, and the case rows **are** that derivation — but they are the
**evidence layer**, and the deliverable she named is the **class layer above them**.
**Escalated to the chief, not decided here.**

**Three further items her text settles that were open:**

1. **§7's hold is HER design, not merely the chief's caution.** Her §7: *"every HOLDS
   row of the matrix as a manual entry… Grows automatically as matrix rows convert."*
   **With zero HOLDS rows the Verification Manual has nothing to draw on by her own
   construction.** The hold is correct and is now sourced.
2. **`GATE REACHED` in her words is *"passed a gate but missing ONE of V/G/P (name
   which)"*.** Ruling 1's second amendment tiers **1–2 green** columns as GATE REACHED,
   i.e. missing one **or two**. **That is a widening of her text and is disclosed here
   as such**, now against her words rather than against a reconstruction. It is not
   corrected unilaterally — but every GATE REACHED row already names its missing
   letters, so the strict reading is recoverable from the table without re-auditing.
3. **Two withdrawn attributions are confirmed OVER-CORRECTIONS from her own text.**
   cfd withdrew *"the early PASSes that lack prereqs convert to HOLDS"* — **it is her
   §2, verbatim.** heat-transfer withdrew the 18-combination zero-pass block — **it is
   her §5**: *"the 18-combination zero-pass finding enters the matrix as NOT HELD with
   its model-error attribution (43-722x GCI proof) — that's a defensible scientific
   position, stated as one."* **Both teams should re-decide on the corrected facts.
   Neither is restored by this team** (§6b.6).

**THE CAVEAT THAT DOES NOT GO AWAY, and it is §6b.6's open question in its sharpest
form.** The block is written **in the third person about her** (*"Sanaa's directive:"*)
and carries **agent-role tags** (`[FABLE+HAIKU]`, `[OPUS]`, `[SONNET]`, `[ORCH]`). It is
a work order she **sent**, not her original prose throughout. **But she interleaved her
own sentences in her own voice, with her own typos** — *"In that sense, the most
important teams this week are the cfd team, the verification team, the ansys
verification team and the heat transfer team."*, *"Sanaa confirms these are PUBLIC Ansys
resources."*, *"Priority should be given to cases we never ran before"*, *"I added
additional papers in…"*, *"for now this means we are using ops 5 for anything needig
fable temporarily"*. **Its authority as an instruction she issued is not in doubt.
Whether the agent-drafted paragraphs count as "her words, verbatim" is Sanaa's to rule
and nobody else's.**
~~**Sweep IN PROGRESS. No result is claimed here and none may be quoted from this
section yet.**~~ — **STRUCK 2026-08-25: the sweep COMPLETED and its result is
§6b.1–§6b.6 above, verified by the supervisor in §6b.7.** The line is struck in
place rather than rewritten, per CLAUDE.md rule 6. **This file's own §0 is a worked example of the honest form** — it
records the three-column rubric as *the chief's reconstruction of Sanaa's directive,
explicitly NOT her verbatim words*, which is class **D** by construction.

**Nothing found by this audit will be "fixed" by this team.** A withdrawal or a
re-marking belongs to the **owning team, or to Sanaa** — never to the auditor, and
never to the chief by proxy. This team reports the class and the evidence.

---

## 5. What this file is not

- It is **not** the Certonomous Verification Manual. That document is
  **SEQUENCED BEHIND this matrix and deliberately held** by the chief; it draws
  only on rows this matrix has confirmed **HOLDS**, by this team's own spot-check.
  Drafting it from claimed rows is the failure mode it is sequenced to avoid.
- It is **not** a compute record. Costs live in `docs/COST_CALIBRATION.md`.
- It does **not** commit or edit another team's files.

---

## RULINGS 6 AND 7 — 2026-08-25, verification team. Two questions referred by cfd, both answered at **ZERO COMPUTE**

**Scope of this addition, stated first.** Appended at the foot. **No existing row, cell,
tier or ruling above this line is edited, and nothing is re-tiered.** This team stands
paused by Sanaa's 2026-08-25 directive; these two questions are answered because the
rubric is this team's, because both answers are free, and because one of them may save a
solve. Nothing else was resumed.

### Ruling 6 — a dated addendum MAY re-source a citation, and it does **NOT** turn a fired `GATE FAIL`'s `P` column green. **Ruling 3 tests the state AT FREEZE, not the state now.**

**The question.** `verification/campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md` §3, frozen
at **`74797a57`** (2026-08-07 22:40:28 +0000, blob `6c757db6`) before any solve, gates
hump separation and reattachment against **0.665 / 1.100 at ±5 %** and sources them
*"as carried by NASA TMR's hump validation page"* … *"(NASA TMR, fetched live
2026-07-28, on disk)"*. It has **fired**: separation **0.6544 (−1.59 %) `PASS`**,
reattachment **1.2531 (+13.92 %) `GATE FAIL`**. The primary — Greenblatt et al.,
AIAA-2004-2220, Table 2 — is held at
`docs/papers/benchmark_test_cases/greenblatt_et_al_cfdval2004_hump.pdf` with its sidecar.
**May a dated addendum re-source the reference to the primary — moving no gate, no
threshold, no cap and no label — and thereby make `P` green?**

> **RULING: NO. The addendum is LEGAL and it is INERT on the `P` column.** The question
> looked hard because its two halves have different answers.

**(a) LEGAL.** `CLAUDE.md` rule 2 permits post-compute dated addenda that alter none of
the four protected items, and a citation is none of them. **D336** settled by execution
that a *"dated addendum below the freeze line"* is the **maximum permitted action** on a
frozen surface — and this very file already carries one, at
`W1_HUMP_CHALLENGE_PREREGISTRATION.md:130`, the *"Dated citation note, 2026-08-08 (Ladder
V rung V5; additive only)"*. Nothing forbids writing it.

**(b) INERT.** Ruling 3's operative test is the **route the VALUE travelled**, not the
presence of the document: *"A value that reaches the lab through a third party is
`SECONDARY`."* A route is a historical fact about a run that has already fired. An
addendum can record that the route was checked afterwards; **it cannot re-route a number
that already reached the grading path.** The ground is the lab's own, **L-44**: a frozen
artifact's evidentiary value is *"its TIMESTAMP RELATIVE TO WHAT IT JUDGES"*. A citation
written on 2026-08-25 carries a 2026-08-25 timestamp and therefore has no evidentiary
standing relative to a run graded on 2026-08-07. **Ruling 3 is a statement about the
state AT FREEZE. It is now settled as such, and that is the whole answer to the question
as the chief framed it.**

#### THE FACT THAT DECIDES IT — measured here, not argued

**The premise that the two sources are *numerically identical* is NOT TRUE AS STATED**,
and the way it fails is exactly the way that matters. **Greenblatt Table 2, page 7,
baseline row, read from the held sidecar, carries THREE numbers where the frozen document
carries two:**

| quantity | Greenblatt Table 2, baseline | frozen at `74797a57` |
| --- | --- | --- |
| separation — 2-D PIV centerline | **0.665 ± 0.005** | 0.665 |
| reattachment — **oil-film (off centerline)** | **1.11 ± 0.003** | *(absent)* |
| reattachment — **2-D PIV (centerline)** | **1.10 ± 0.005** | 1.100 |

**The primary does not carry ONE reattachment value. It carries two, and they disagree by
0.9 %.** The frozen gate uses the 2-D PIV centerline limb. **This lab never made that
choice — NASA TMR made it, and the pre-registration inherited it.** Table 2 also carries
an instrument uncertainty the frozen band never engaged, and the condition it was measured
at — **Re = 929,000, M = 0.100**, stated in §V of the paper and nowhere in Table 2 itself
— is **not** the condition this lab runs, which is **Re = 936,000 (+0.75 %)**.

**Therefore an honest re-sourcing addendum cannot be a re-labelling.** To be true it must
additionally declare **which limb of Table 2 it adopts**, **why**, **the ±0.005 it sits
inside**, and **the condition mismatch** — four selections the frozen document never made,
made today with **1.2531 already in hand**. **A citation is not one of rule 2's four
protected items; but a citation that must carry a limb choice to be true is a threshold
choice wearing a citation's clothes.** That is what rule 2's ordering exists to prevent.

#### The cost of this ruling, stated rather than buried

**It does NOT cost the lab the finding, and the `GATE FAIL` is robust to the limb.**
Against the oil-film limb **1.11** the ±5 % band is **[1.0545, 1.1655]** and 1.2531 misses
it by **+12.89 %**; against **1.10** it misses by **+13.92 %**. Same verdict either way —
and Ruling 3's own sentence holds unchanged: *"No gate verdict anywhere in this lab moves
because of this ruling."*

**What it DOES cost is a solve.** The row cannot be converted on paper. It converts only
by a fresh pre-registration against the held primary, frozen before its own compute —
`verification/campaign/F6a_GREENBLATT_PREREGISTRATION_DRAFT.md`, priced at **13.74
core-min** in its §8. **That is the price of the rubric being honest, and it is small.**

#### The cfd lane had already reached this answer. This team AFFIRMS it rather than claiming it.

The draft's **§10.4** refuses the manoeuvre in its own words, unprompted and against its
own interest: *"the one manoeuvre that is explicitly REFUSED here: re-labelling
`74797a57` as a primary-sourced gate by amendment … **re-sourcing a gate's reference IS
altering the gate.** The W1 record is not touched by this document, and C-45's cells are
not moved by it."* **This ruling supplies a ground that draft did not have — the two-limb
table — not a correction to it.**

#### The draft's self-discipline is UPHELD, explicitly, so nothing here is read as licence to undo it

Its §2.3 adopts the **±5 % band verbatim from `74797a57`** rather than deriving one today,
on the stated ground that *"any number derived now, in either direction, is a number
derived with the answers in hand"*; where its own construction principle wanted a
**tighter** band it registered that as **REPORTED — NOT A GATE**. **This team endorses
that move.** Inheriting a band from a freeze that predates the answers preserves a
prediction-first property a fresh derivation cannot manufacture. **And note the asymmetry
that makes it legitimate rather than convenient: the inherited band is the one under which
the row ALREADY FAILED.** A lane inheriting a band that had already passed would be a
different question and is not decided here.

#### SCOPE — cfd said this *"plausibly reaches beyond"* the one case. It does. Here is how far, traced and untraced.

**The shape this ruling governs is narrow: the primary is HELD and readable, AND the
frozen value nevertheless routed through a carrier.** Rows checked:

- **C-45 / W1 hump** — the referred row. Greenblatt entered this box at **`03814b0a`,
  2026-08-05**, *two days before* the 2026-08-07 freeze. **The lab HELD the primary at
  freeze time and its §3 even NAMES it as the Reference — it simply did not read its
  table.** Not converted, for the reason above. *(This corrects the framing the question
  arrived with: the lab did not fail to hold the primary; it failed to read it.)*
- **C-9 / F5a cylinder** — **the one other row of this exact shape**, and it is flagged
  rather than scored; see Ruling 7's closing paragraph.

**Rows NOT of this shape and therefore untouched either way** — in each the primary is
genuinely absent or unread, so Ruling 3's *first* clause disposes of them without
reaching this one: **K0c** (de Vahl Davis 1983, paywalled, never read, via Han & Xie
Table 3); **F7 / C-22** (Martin & Moyce 1952 `NOT OBTAINED`, 2021 figure digitised);
**C-18 / F6b** (Rapp & Manhart 2011 not held); **C-26 / F9** (Womersley 1955 not located).

**NOT TRACED, and named so nobody assumes it was:** heat-transfer's 37 sub-rows, dafoam's
58, closure's 6 and ansys-verification's 4 were **not** swept for this shape. **A row
elsewhere in the lab whose primary is held but whose frozen value routed through a carrier
is governed by this ruling and has not been looked for.** One lane's work, not done here.

### Ruling 7 — what Ruling 4's **"correlation"** clause admits, and what a manufactured solution buys

**The question.** Ruling 4 makes `V` green for *"an exact solution, a manufactured
solution, or a correlation"*. cfd asks what the correlation clause admits, because the
answer decides whether **F5a-MMS** is worth spending.

> **RULING — a correlation scores `V` only when it is used as a KNOWN-ANSWER INSTRUMENT,
> which requires ALL FOUR of:**
>
> 1. **It is a PUBLISHED CLOSED-FORM RELATION** — an equation with stated coefficients.
>    **A table of scattered measured points is not a correlation, and a curve the lab
>    fitted itself is not an instrument — it is the data.**
> 2. **The source stating it is HELD, readable and title-page verified** (rule 15).
>    Ruling 3's holding clause reaches `V` here, and the lab's own precedent shows why it
>    must: **C-7 / F4** took Billig (1967) from *the primary textbook page image* — web
>    search returned **4.76**, the printed coefficient is **4.67**, and the record says
>    so. **A 1.9 % error in a coefficient is the size of the deviations these gates
>    measure.** Recall and OCR are not readings.
> 3. **Its STATED VALIDITY RANGE covers the case's condition**, and the record states
>    both the range and the condition.
> 4. **Its own scatter or stated uncertainty is quoted, and the gate band is WIDER than
>    it** — otherwise the gate is measuring the correlation's noise, not the code.

**And the operative half, which is the exclusion.** **A correlation establishes no
observed order of accuracy and never demonstrates that the code solves the equations
right** — it shows the answer lands in the neighbourhood a fit predicts. **It is by a wide
margin the weakest of `V`'s three instruments**, and every `V`-green cell in this file
already names which of the three it is (§1). **Nothing in this ruling widens `V`.**

**EXPLICITLY NOT DECIDED HERE: §3.8i item 1** — whether code-to-code results and
numerical benchmarks score `V`. That is a **rubric widening in the flattering direction**,
it is on the refused list, and this ruling does not touch it.

#### The premise of the MMS question is MIS-COSTED, and that has to be said before it is answered

cfd asks whether F5a-MMS is worth **465 core-minutes**. **It is not a manufactured-solution
price.** `verification/campaign/F5a_MMS_SCOPING_MEMO.md` §5 states it in its own words:
*"the **G+P limb** is COSTED at **465–612 core-min**; the **V limb is UNCOSTED**; so
F5a-MMS as a whole is not yet fully costed."* **The 465 buys the SHEDDING LADDER — `G`,
and contingently `P`. It buys no `V`, and the manufactured solution's own price is not
known.** Under **rule 12** nothing may be authorised on an uncosted limb, so **the question
as posed cannot be answered yes on any reading.**

#### Does a manufactured-solution study buy a column the lab does not already hold? **NO — not a column.**

**`V` is green on 7 of cfd's 82 rows** — C-3/C-4/C-5 (F3 wedge, cone, diamond: exact),
**C-7 (F4: correlation)**, C-26 (F9: exact, carrying its own VERIFY), C-53 (DMR: exact),
C-54 (DPW8_V2: exact) — and on heat-transfer's analytic rows besides. **The rubric's `V`
is BINARY and does not grade the instrument**, so a manufactured solution scores the same
green as a Hagen–Poiseuille comparison. On F5a it would buy `V` **on that row**. **It buys
the lab no column it lacks.**

**What it WOULD buy is a CAPABILITY, and the honest thing is to name it and then decline
to price it as a column.** **No row in this lab joins a known answer to a converging
ladder.** The exact-solution rows carry no Roache triple at all — cfd's own audit records
`observed_order`, `gci*` and `richardson` appearing **zero times** in
`F3_supersonic_exact_theory.json` and in `F4_hypersonic_blunt_body.json` — while the one
row with a clean triple, the **TMR flat plate**, has **no known answer to converge to**.
**An MMS is the only instrument that joins those two halves, and that gap is the strongest
thing that can be said for the proposal.**

**But the rubric cannot hear that argument, and that is a defect in the rubric rather than
a reason to spend.** Grading `V` by the strength of its instrument would be a **rubric
change**, and widening or retiring a rubric clause is **Sanaa's alone**
(`CLAUDE.md` FIRST-ACTION). **Referred to her desk. Not decided, and not worked around.**

#### THE OPERATIVE ANSWER TO cfd, so nothing has to be mined out of the prose

**The memo's own §9 already sequences this correctly and this team affirms it: settle the
`P` band question at ZERO COMPUTE FIRST.** If Roshko's scattered points cannot support a
gateable band, F5a-MMS buys `V` and `G` and no `P` — *"and it is then just a more expensive
F3"*. **Do not spend 465 core-min to buy a `V` the lab already holds seven of.**

#### ⚠ A CHECKABLE ITEM THAT MAY MAKE THE `V` LIMB REDUNDANT OUTRIGHT — and two lab records that disagree

**`docs/papers/turbulence_models/roshko_1954_naca_tr_1191.pdf` and its `.txt` sidecar ARE
on this box**, and the sidecar carries what reads as a **closed-form Strouhal–Reynolds
relation with stated coefficients and a stated validity range** — the form `0.212(1 −
c/R)` at sidecar lines **703** and **741**, and a range clause **`50 < R < 150`** at line
**1073**, beside *"FIGURE 5 — Strouhal number against Reynolds number for circular
cylinder"* at line **843**. **`VERIFICATION_CHARTER.md` §6b records F5a's reference as
`NOT OBTAINED` as a primary, with what is held being a figure in a 2014 thesis. Those two
records disagree and this team has NOT reconciled them.**

**Three consequences, and none of them is a score:**

1. **If Roshko is held and readable, F5a's `V` may be earnable FROM THE SHELF at zero
   compute** under Ruling 7's four conditions — **which would make the MMS's `V` limb
   redundant outright.**
2. **The coefficients MUST be read from a rendered page image, not from this sidecar.**
   Its OCR is visibly degraded at exactly the load-bearing characters (line 741 renders as
   `.0.212 (1_ 2~2)`). **Condition 2 excludes OCR for the same reason it excludes recall,
   and the F4 precedent is the model: render the page, read the printed value.**
3. **Condition 3 may bite.** F5a's ladder spans **Re 100–180**; the range clause visible in
   the sidecar reads **`50 < R < 150`**. **Re 160–180 may fall outside the relation's
   stated validity**, in the band Roshko himself treats separately. **If so, condition 3
   fails on the upper rungs and `V` is earnable only on part of the ladder.**

**Nothing above is scored, and rule 15 is why: this team has not rendered Roshko's page.
It is named as a checkable item for cfd, at zero compute, and it is worth doing BEFORE the
`P` band question rather than after.**

*Standing rules observed: rule 1 (verdict vocabulary — no gate verdict is moved by either
ruling); rule 2 (the ordering, which is Ruling 6's whole ground); rule 6 (nothing above
this line edited, appended at the foot with the anchor asserted last before writing);
rule 9 (a rubric widening and a clause retirement both referred to Sanaa, not taken);
rule 12 (an uncosted limb authorises nothing); rule 15 (no paper scored unread).*
