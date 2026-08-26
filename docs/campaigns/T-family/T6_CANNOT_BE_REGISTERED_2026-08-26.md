# T6 — **CANNOT BE PRE-REGISTERED OR FIRED. `BLOCKED` at `ACQUIRE`, and the brief's three instructions have no object.**

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26. ZERO COMPUTE —
no solver launched, no mesh built, no case written.** **No pre-registration was written
and nothing was frozen.** Nothing has been sent, filed, submitted, uploaded, registered
or posted outside this box (`CLAUDE.md` rule 7).

---

## 0. The answer, first

**T6 is `BLOCKED`.** Not `PENDING` — `PENDING` is "not yet run", and T6 cannot be *armed*,
let alone run. **Its reference data does not exist in this lab**, and `CLAUDE.md` rule 2
requires prediction-first bands **with their derivation**, committed before the solver
starts. **A band cannot be derived against published scaling data the lab does not
hold.** There is nothing to freeze.

## 1. The index says so in its own legend, and I verified the row

`T_FAMILY_INDEX.md:29` — the reference-tier legend:

| tier | meaning | state |
|---|---|---|
| **`ACQUIRE`** | published data or a digitised figure | **blocked until obtained** |

`T_FAMILY_INDEX.md:46` — the T6 row:

> **T6** | Rayleigh–Bénard `Nu`–`Ra` scaling | **ACQUIRE** | 3–4 decades of published
> scaling data; **transient, far over $25**

**`ACQUIRE` carries no `(obtained)` annotation on T6** — and the annotation is used
elsewhere on the same page precisely to mark the difference: `T1a` reads
*ACQUIRE (obtained)*, `T4` reads *ACQUIRE (partial 2026-08-21)*, `T5` reads
*ACQUIRE (obtained 2026-08-21)*. **T6 has no such mark, and the legend's own words for
that state are "blocked until obtained."**

## 2. The absence is MEASURED, on all four L-337 axes, with a live control

**SOURCE** — enumerated from `git ls-tree -r HEAD --name-only`, never `git ls-files`.

**CONTROL, run first (standing rule 3 applied to a search):** the same sweep finds
**1** file for `meinders` (T5's held primary) and **91** for `ercoftac` (T4's held
tabulated data). **The sweep is shown able to return a held reference, so a zero from it
is evidence.**

**VOCABULARY** — searched the **subject**, not the rung id, because a search built from
what you expect can only confirm it:

| term searched | tracked files at HEAD |
|---|---:|
| `rayleigh` | **0** |
| `benard` / `bnard` | **0** |
| `grossmann` (Grossmann–Lohse scaling theory) | **0** |
| `ahlers` (Ahlers–Grossmann–Lohse review) | **0** |
| `niemela` (high-`Ra` cryogenic `Nu`–`Ra`) | **0** |
| `chilla` (Chillà–Schumacher review) | **0** |

**PLACE** — all three `FILING_CHARTER` homes checked for a T6 registration
(`verification/campaign/`, `docs/campaigns/<FAMILY>/`, beside the case): **none exists.**

**KEY** — not keyed on the string `T6` alone. The 9 tracked paths matching `T6` are
`verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/t6_SHELL_NR16/`, an
**unrelated F1 mesh-trial variant**. **Excluding those, T6 has zero tracked files.**

**The 70 PDFs in `docs/papers/` include a `buoyant_natural_convection/` topic of nine —
Ampofo, Betts, Tian, Gjesdal, Vierendeels and others. Those are differentially-heated
cavity and indoor-airflow papers. None is a Rayleigh–Bénard `Nu`–`Ra` scaling
reference**, and none spans the 3–4 decades of `Ra` the row requires.

## 3. THE BRIEF'S THREE INSTRUCTIONS EACH HAVE NO OBJECT, AND THAT IS THE CLEANEST PROOF

The brief was specific, and its specificity is what makes the blocker unambiguous:

| instruction | why it cannot be carried out |
|---|---|
| *"Establish where T6's case template came from BEFORE you freeze it"* | **There is no T6 case template.** No `T6_runs/`, no builder, no `0.orig/`, no `system/`. Zero tracked T6 files. |
| *"Sweep it for compressible-namespace tokens — `compressible::`, `rho*`, `alphaEff`, `thermo:` — in `0/`, `constant/` and `system/`"* | **There are no such directories to sweep.** |
| *"Bring me the measured `y+`, do not assume it"* | **`y+` is measured from a built mesh against a solved field.** There is no T6 mesh and no T6 solve. **Reporting a `y+` here would be exactly the assumption the instruction forbids.** |

> **THE BRIEF'S OWN DISCIPLINE IS WHAT REFUSES IT. Every one of its three checks presumes
> an artifact that does not exist, and the correct response to "measure this" when the
> thing does not exist is to say so — not to produce a number.**

## 4. The precedent on the same page, which sets the bar T6 is far below

- **`T1a`** holds its reference — *ACQUIRE (obtained)* — **and is still `BLOCKED`**:
  *"reference held, but no band can be armed from one correlation."* **Holding a
  reference is necessary and not sufficient.**
- **`T3`**'s primary is `NOT OBTAINED` and the row records that *"its absence remains
  disqualifying."*
- **`T5`** holds its primary (Meinders 1998, **OPEN, title-page verified, sha256
  `36c89a54…`, stated uncertainty 5 % mid-face / 10 % edges**), and its
  pre-registration draft is **still unfrozen, with 12 INTERPRETATIONs on Sanaa's desk.**

**T6 has none of what T5 has, and T5 is not yet frozen.** A T6 freeze tonight would
place a rung with **no reference, no case and no cost basis** ahead of a rung with a
verified primary that is still awaiting a ruling.

## 5. Cost — the row flags it, and rule 12 is not discharged by a blanket

The index row reads **"transient, far over $25"**. `CLAUDE.md` rule 12: *"Every run is
costed in its pre-registration; a proposal with no cost is disqualified"*, and **a
blanket authorisation is not a per-item reading (rule 9).**

A Rayleigh–Bénard `Nu`–`Ra` study is **transient**, spans **3–4 decades of `Ra`**, and
under Sanaa's grid ruling needs a **converging three-level family per `Ra` decade**.
**No cost basis can be written before the reference fixes how many `Ra` points are
graded** — the reference determines the design, and the design determines the cost.
**This is a second, independent reason the registration cannot be written tonight**, and
it does not depend on the first.

## 6. WHAT WOULD UNBLOCK IT, in order

1. **Acquire a Rayleigh–Bénard `Nu`–`Ra` reference** spanning the stated 3–4 decades,
   with a **stated uncertainty** — without one there is no band, only a line to eyeball.
2. **Title-page verify it (`CLAUDE.md` rule 15)** — never by filename, file type or hash.
   File under `docs/papers/<topic>/author_year_identifier.pdf` **with its `.txt`
   sidecar**.
3. **Establish whether a band can be armed from it at all** — this is the step that
   stopped `T1a` *after* its reference was in hand, and it is the step most likely to
   stop T6 too.
4. **Then** design the ladder, cost it per `Ra` point, and take the transient formulation
   and the aggregate spend to a decision — the row's *"far over $25"* makes that a
   per-item reading, not a blanket one.

**Steps 1–3 are acquisition and analysis, not compute.** None of them is a fire.

## 7. What was done instead, because the transferable half of the brief DID have an object

The brief's most valuable content is **generic**: T4's launch failures 2 and 3 were **one
PROVENANCE defect**, not two typos — a case template derived from a compressible case,
whose compressible artifacts survived into a frozen rung *because nothing in the
registration had an opinion about them*.

**That is now an executable instrument rather than a warning:
`scripts/check_case_provenance.py`.** It reads the solver from `system/controlDict`,
classifies it, and sweeps `0/`, `0.orig/`, `constant/` and `system/` for tokens of the
**other** family. It **refuses (`exit 2`)** on a finding, carries **zero `assert`
statements**, plants a known contaminant in its own selftest and **refuses if it cannot
see it**, ignores `//`-commented occurrences (so a repair record does not read as a
defect), and **drives itself under `python3 -O` requiring the refusal to fire
identically**. Selftest: **4 arms, 0 FAILED**, rc 0 under both interpreters.

**It runs BEFORE the freeze.** `scripts/check_launcher_can_launch.py` catches this class
at launch by driving the real solver for one iteration, and remains the right last line
of defence. **This one answers the earlier question — *where did this template come from,
and is it internally consistent with the solver it names?* — and a case can be
contaminated in a file the one-iteration arm never reaches.**

> **A crash is cheap. A frozen rung carrying a silent inconsistency is not.**

Driven live against T4's three repaired cases (`T4_IJ_c`, `T4_IJ_m`, `T4_IJ_f`): **all
three clean, rc 0** — the amendments at `build_t4.py:312` and `:367` did close it.

## 8. Cost of this work

**Zero core-minutes.** Index and specification reads, a filename sweep, and a
sub-second Python selftest. `docs/COST_CALIBRATION.md` gains no row.

---

> **NO PRE-REGISTRATION WAS WRITTEN. NOTHING WAS FROZEN. NO SOLVER WAS LAUNCHED AND
> NOTHING IS QUEUED. T6 IS `BLOCKED` UNTIL ITS REFERENCE IS ACQUIRED, AND THE
> DECISION ABOUT WHAT FIRES INSTEAD IS THE SUPERVISOR'S.**

---

## 9. ADDENDUM — the territory provenance sweep, COMPLETED and reported as a number

**`UNMEASURED` is now measured.** `scripts/check_case_provenance.py` driven over every
case directory holding a `system/controlDict` under `verification/runs/T-family/`,
`verification/runs/F14-cooling-ladder/` and `verification/runs/THERMAL_K0_runs/`:

| | |
|---|---|
| **cases swept** | **357** |
| **cases with findings** | **0** |
| solver not in the classification tables | **63** — `application none` ×38, `laplacianFoam` ×25 |
| files scanned head+tail only (>1 MB) | **35** |
| elapsed | **4 s** |

> **ZERO SOLVER-NAMESPACE CONTAMINATIONS ACROSS 357 CASES. The T4 defect class is not
> present anywhere else in this territory.**

**The 63 unclassified are reported as unclassified, never as clean.** The tool prints
*"UNCLASSIFIED solver, no sweep performed — add it to the tables rather than assuming it
is clean"* and returns no verdict on them. `application none` is a mesh-only or utility
case; `laplacianFoam` solves a bare scalar Laplacian and belongs to neither family in a
way this check can discriminate. **Guessing a family for them would manufacture exactly
the false confidence this instrument exists to prevent.**

**The 35 partially scanned files are declared in the tool's own output**, with the first
three named per case — see §10.

## 10. THE INSTRUMENT'S OWN DEFECT LOG — four defects in four live uses, none findable by its selftest

| # | defect | found by | status |
|---|---|---|---|
| 1 | descended into `constant/polyMesh/` — hundreds of MB of `points`/`faces` | sweep timed out at 170 s | **fixed**, correctness-preserving |
| 2 | scanned binary/compressed field files line by line | same timeout | **fixed**, correctness-preserving |
| 3 | **`constant/` holds BULK NUMERICAL DATA too** — `T10aR_runs/R_x` carries a **6,086 MB `constant/F`** view-factor matrix and a **1,513 MB `globalFaceFaces`**, neither under `polyMesh` | sweep stalled indefinitely at case 186 of 357 | **fixed** by head+tail scanning above 1 MB — **a declared NARROWING OF SCOPE, printed in the tool's output, not a correctness-preserving speedup** |
| 4 | **`p_rgh` was in the Boussinesq-only token list and produced 109 FALSE POSITIVES across 31 cases** — every K2e `buoyantSimpleFoam` case flagged | the first clean full sweep | **fixed** — `p_rgh` is solved by **both** `buoyantSimpleFoam` and `buoyantBoussinesqSimpleFoam`; it is **shared**, and had no business in a discriminating list |

**Defect 4 is the one that mattered most, and it is the opposite failure from the first
three.** They made the tool slow; **it made the tool WRONG, in the direction of a
finding.**

> **A TOKEN BOTH FAMILIES USE DISCRIMINATES NOTHING. A CHECKER THAT CRIES WOLF ON
> LEGITIMATE CASES TRAINS READERS TO IGNORE IT — WHICH IS WORSE THAN NOT HAVING THE
> CHECKER AT ALL.**

**None of the four could have been found by the selftest**, whose fixtures are two-file
synthetic cases with no mesh, no bulk data and no second solver family. **A passing
selftest exercises the clean path.** Every one was found by pointing the instrument at
the real corpus — **which is the only thing that ever finds them, and is why the
`0-findings` result above is worth more than the `109-findings` result that preceded it.**
