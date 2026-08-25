# STANDARDS_READ — this team's reading of the lab's standards book, and what it changes

**NOT FILED ANYWHERE.** Nothing in this document leaves this box (CLAUDE.md rules 7, 8).
**SUBMISSIONS PARKED.**

**Written 2026-08-25T16:01:14Z** (`date -u` in the writing invocation) by `ansys-lane-opus`
(Opus 5) on the `ansys-verification-supervisor`'s brief. **ZERO COMPUTE**: no solver, no
mesher, nothing written under `verification/runs/`. Every number below is read from a file
already on disk or computed from one by arithmetic in this session.

**Why this document exists.** Sanaa's directive of 2026-08-25, byte-exact at the top of this
team's `docs/LAB_STATE.md` section, ends: *"I have also added a book of standards about this
here https://github.com/Certonomous/Certonomous/tree/main/docs/standards"*.

**THE GITHUB URL WAS NOT FETCHED.** The repository is permanently private by her own ruling
of 2026-08-18 and CLAUDE.md rules 7 and 8 say nothing leaves this box; a fetch of that URL is
an outbound request naming a private repository path. **The local tree `docs/standards/` is
the authority and is what was read.** Read via `git show HEAD:<path>`; all six files were
first verified **byte-identical between the worktree and HEAD** (sha256 of each), so no stale
worktree copy is behind any statement here.

---

## 0. WHAT THE BOOK IS — six files, and the name collision resolved

| path | title | version on its own face | lines |
|---|---|---|---|
| `docs/standards/MESH_STANDARD.md` | *Certonomous Mesh Standard* | v1.2, 2026-08-11 | 377 |
| `docs/standards/MONITOR_STANDARD.md` | *Certonomous Monitor Standard* | v1.12, 2026-08-18 | 1537 |
| `docs/standards/INNOVATION_STANDARD.md` | *Certonomous Innovation Standard* | v1.0, 2026-07-25 | 206 |
| `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md` | *Problem Research Protocol* | v0.2, 2026-08-04 | 153 |
| `docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md` | *Infrastructure and Standards Family Supervision Guidelines* | v1.17, 2026-08-11 | 1533 |
| **`docs/MESH_STANDARD.md`** (NOT in `docs/standards/`) | *Grid-Convergence Practice — Inherited from DPW-8/AePW-4 (D8)* | 2026-07-29 | 260 |

**THE TWO `MESH_STANDARD.md` FILES ARE DIFFERENT DOCUMENTS AND BOTH SAY SO ON THEIR OWN
FACE.** The split, in their own words:

- **`docs/standards/MESH_STANDARD.md` governs whether ONE mesh is admissible** —
  non-orthogonality, skewness, aspect ratio, the mesh birth certificate. Its §7.0: *"that
  file governs how a grid **family** is sized and how family scatter is reported; this file
  governs whether **one** mesh is admissible, and owns the birth certificate."*
- **`docs/MESH_STANDARD.md` governs how a grid FAMILY is sized and how family scatter is
  reported** — the DPW-8/AePW-4 level-indexed growth formula, the y⁺-anchored Δy1 tables,
  IQR/std scatter conventions. Its own header: *"Naming collision flagged, not hidden."*

Sanaa's link points at `docs/standards/`, so **`docs/MESH_STANDARD.md` is strictly outside
the tree she named.** It is read and reported here anyway, because the file she DID name
cross-references it as its companion and because §1 below cannot be answered without it.
**That is disclosed rather than quietly folded in.**

---

## 1. MESH QUALITY — what the book sets, and whether this team's five cases meet it

### 1.1 The gates, quoted with their basis

`docs/standards/MESH_STANDARD.md` §3, with the source-code basis it states for each:

| gate | value | basis it cites | on breach |
|---|---|---|---|
| **§3.1 max non-orthogonality** | **hard gate 70°**, warning band 65–70 | `nonOrthThreshold_ = 70`, OpenFOAM `primitiveMeshCheck.C`; snappy generates to 65 | above 70: *"no validated force from this mesh"*, trust capped |
| **§3.2 max skewness** | **hard gate 4**, boundary faces INCLUDED | `skewThreshold_ = 4`, same file; the lab deliberately enforces 4 on boundary faces where snappy's default is 20 | trust capped, run proceeds *"for ranking purposes only"* |
| **§3.3 aspect ratio** | **advisory 1000, never a lone rejection** | `aspectThreshold_ = 1000`; calibrated against NASA TMR flat-plate grids at AR 66 643–74 041 | AR>1000 needs an alignment justification on the record; AR>1000 **together with** nonOrtho>60 or skew>2 is a flag |
| **§3.4 volume ratio** | **proposed only**, warn below 0.01 | snappy `minVolRatio 0.01` | not adopted; not in `physics_rules.yaml` |
| **§6 mesh birth certificate** | `birth_certificate.json` beside the `polyMesh`, carrying `points_sha256`, verdict, cells, the three metrics, hard errors, generator, `created_at` | Verification Charter v1.5 §9 | *"a mesh whose birth certificate is missing is quarantined from new work"* |

### 1.2 MEASURED, from the `log.checkMesh` on disk beside every level

Every level of every case has a `log.checkMesh` on disk and **every one of them ends with
`End` and carries no `Failed ... mesh checks` line** — which is `docs/standards/
INFRA_FAMILY_SUPERVISION_GUIDELINES.md` §12's own completion test (*"105 of 105 real
checkMesh logs in the archive end with `End`"*), so none of them is the crashed-checkMesh
shape that §12 shows can mint a false `clean`.

| case / level | cells | **max non-ortho (gate 70)** | **max skew (gate 4)** | **max AR (advisory 1000)** | verdict vs §3 |
|---|---|---|---|---|---|
| VMFL001 L1 16×64 | 1 024 | 1.479e−06 | 0.11627 | 2.2746 | **meets all three** |
| VMFL001 L2 32×128 | 4 096 | 1.479e−06 | 0.05817 | 2.4038 | **meets all three** |
| VMFL001 L3 64×256 | 16 384 | 1.708e−06 | 0.02910 | 2.4755 | **meets all three** |
| VMFL001-R2 L1/L2/L3 | 1 024 / 4 096 / 16 384 | identical to run 1 | identical | identical | **meets all three** |
| VMFL003 L1 250×5 | 1 250 | 0 | 0.33080 | **40.038** | **meets all three** |
| VMFL003 L2 500×5 | 2 500 | 0 | 0.33080 | 20.019 | **meets all three** |
| VMFL003 L3 1000×5 | 5 000 | 0 | 0.33080 | 10.010 | **meets all three** |
| VMFL003 D-ladder 500×3 / ×4 / ×6 | 1 500 / 2 000 / 3 000 | 0 | 0.33080 | 12.011 / 16.015 / 24.023 | **meets all three** |
| VMFL005 L1 100×10 | 1 000 | 0 | 0.33080 | 16.015 | **meets all three** |
| VMFL005 L2 200×20 | 4 000 | 0 | 0.33080 | 16.015 | **meets all three** |
| VMFL005 L3 400×40 | 16 000 | 0 | 0.33080 | 16.015 | **meets all three** |
| VMFL045-R2 L1 90×76 | 6 840 | **14.906** | 0.39792 | 1.4858 | **meets all three** |
| VMFL045-R2 L2 180×152 | 27 360 | **14.953** | 0.39906 | 1.4897 | **meets all three** |
| VMFL045-R2 L3 360×304 | 109 440 | **14.976** | 0.39963 | 1.4916 | **meets all three** |
| VMFL051 L1 120×52 | 6 240 | **14.862** | 0.37245 | 1.7575 | **meets all three** |
| VMFL051 L2 240×104 | 24 960 | **14.931** | 0.37306 | 1.7600 | **meets all three** |
| VMFL051 L3 480×208 | 99 840 | **14.966** | 0.37336 | 1.7613 | **meets all three** |

**ANSWER TO §1: YES — all 23 meshes of all five cases meet every enforced gate in
`docs/standards/MESH_STANDARD.md` §3, with margin.**
- **Worst non-orthogonality anywhere in this team's corpus: 14.976°** (VMFL045-R2 L3),
  **4.7× inside the 70° gate** and below even the 65° warning band. The two wedge families
  (VMFL003, VMFL005) read exactly 0; VMFL001's reads 1.7e−06, which is machine noise.
- **Worst skewness anywhere: 0.39963** (VMFL045-R2 L3), **10× inside the gate of 4.**
- **Worst aspect ratio anywhere: 40.038** (VMFL003 L1), **25× inside the 1000 advisory**, so
  §3.3's alignment-justification requirement is never triggered and the compound flag
  (AR>1000 with nonOrtho>60 or skew>2) is never approached on any axis.
- §3.4's volume-ratio value is a **proposal**, not adopted, and nothing is owed against it.

### 1.3 THE ONE THING THE BOOK REQUIRES THAT THIS TEAM DOES NOT HAVE — stated plainly

**No mesh in this team's corpus carries a `birth_certificate.json`.** Measured: `find` over
`verification/runs/ansys_verification/` and `cases/ansys_verification/` returns **zero**
files of that name, against **23 `log.checkMesh` files present**.

That is exactly the gap `INFRA_FAMILY_SUPERVISION_GUIDELINES.md` §11 measured lab-wide and
named: *"The 2026-08-08 audit marked 105 meshes `CERTIFIED (pre-existing record)` on the
strength of a `log.checkMesh`, and **105 of 105 carried the log while 0 carried a
certificate***". Its resolution — *"a word that named a missing artifact is corrected to
**CHECKED BUT UNCERTIFIED**"* — is the honest label for this team's 23 meshes too.

**Three qualifications, so this is not overstated:**
1. **The evidence exists; only the artifact is missing.** Every metric §6 asks a certificate
   to carry is measured and on disk in the `log.checkMesh` beside the mesh, and §1.2 above
   is that reading.
2. **The enforcement machinery §6 describes does not reach this team.** §2 of the mesh
   standard names the geometry workflow (`sdk/workflows/geometry_study.py`) and §6 names the
   three mesh caches as the chokepoints. This team meshes with `blockMesh` from its own
   `run_vmfl<nnn>.sh`, through none of them, so nothing was bypassed — the coverage simply
   does not extend here. That is a **gap with a stated price, never a constraint** (the
   guidelines' own L-48 formulation).
3. **Minting a retrospective certificate is possible and is NOT done in this task.** §11's
   own precedent requires the **cell-count cross-check** (the log's cell count equals the
   mesh's own `nCells` from the polyMesh `owner` header) and the provenance string
   `retrospective-from-archived-log`. That is a change to run directories and is the
   supervisor's call, not this lane's, inside a zero-compute records task.

### 1.4 What the FAMILY document adds, and where VMFL003 sits against it

`docs/MESH_STANDARD.md` governs the *sequence*, not the single mesh, and two of its rules
bear directly:

- **"Refine the same way each step; change only the resolution parameter."** All five
  families satisfy this: VMFL001 (16×64 → 32×128 → 64×256, r = 2 both directions, 4× cells),
  VMFL005 (100×10 → 200×20 → 400×40, r = 2 both, 4× cells), VMFL045-R2 (90×76 → 180×152 →
  360×304, r = 2 both, 4× cells), VMFL051 (120×52 → 240×104 → 480×208, r = 2 both, 4× cells).
- **VMFL003 is the exception and it is a DELIBERATE, PRE-REGISTERED one.** Its triple is
  250×5 → 500×5 → 1000×5: **r = 2 in the AXIAL direction only, with the radial count held at
  N_r = 5 across the whole triple.** The frozen `blockMeshDict.template` states the reason in
  its own header — *"`__NR__` radial cells (r), UNIFORM — deliberately not graded, because
  the first-cell y⁺ is what the wall function reads and it is fixed at NR = 5 across the
  whole Roache triple (PREREGISTRATION.md section 4)"* — and the separate D-ladder
  (500×3 / ×4 / ×5 / ×6, y⁺ 60.02 → 31.66) is the wall-normal axis, run as a diagnostic.
  **This is the right design for a wall-function case and it is not a departure from the
  standard; it is the standard's own logic applied.** What it means is stated in this team's
  own `RESULTS.md`: the axial channel the GCI can see moves Δp by **7.8 ppm**, the
  wall-treatment channel it structurally cannot see moves it by **1.7356 %** — *"These differ
  by a factor of ~2200."*
- **The y⁺-anchored Δy1 tables of `docs/MESH_STANDARD.md` §b DO NOT TRANSFER to VMFL003**,
  and saying so is the point. They target y⁺ ≈ 1.00 down to ≈ 0.29 — a **wall-RESOLVED** RANS
  grid. VMFL003 runs `nutkWallFunction`, which requires the first cell in the log layer
  (y⁺ ≈ 30–300), and its D-ladder spans 60.02 → 31.66. Applying §b's numbers here would be
  precisely what `docs/standards/MESH_STANDARD.md` §7.6 forbids: *"Applying the **form** of
  these rules to a hull case is intended; transplanting the **numbers** is not."*

---

## 2. CONVERGENCE AND MONITORING — and whether it bears on the plateau clause and rule 5

### 2.1 What the book sets

`docs/standards/MONITOR_STANDARD.md` is 16 signatures (S1–S16, S7 withdrawn), each with a
detection rule, a severity from {FATAL, FLAG, WATCH, CONFIGURATION RISK}, an action, and —
by its own **standing rule 6** — a **replay line**: corpus, fire count, fatal count, and
behaviour on the case that motivated it. *"A rule nobody has replayed against real logs is a
hypothesis, not a check."*

The four that bear on this team:

- **S6 residual stall** — rolling median improving by < 2× over 200 iterations while above
  the `residualControl` target. Honest measured fire rate **47 % on real declared targets**
  (87 logs), after the corpus behind six adopted rules turned out to have been *"selected by
  a filename accident"* (449 files globbed as `*.log` against **1 375** real run logs).
- **S12 unsettled stop** — over a trailing window (a quarter of iterations, floored 20,
  capped 2000): **relative drift ≥ 1e−3 AND monotone fraction ≥ 0.90**. Severity FLAG.
  Replayed on 760 histories, fires on 36 (4.74 %), 0 fatal.
- **S13 converged residuals over a graded quantity still moving** — **peak-to-peak of the
  monitored quantity over a FIXED WINDOW of outer iterations**, as a percentage **of the
  range the quantity spanned over the whole run**, against **0.02 %**. Severity **FATAL for
  any number graded off that quantity**.
- **S8 Courant excursion** — the reported max exceeding the case limit by more than **2 %**
  (FLAG), or growing monotonically across 20 consecutive steps **with the time step held
  fixed** (FATAL). The 2 % is measured, not assumed: in four healthy archived `interFoam`
  runs the largest overshoot anywhere is **0.403 %** while 27–43 % of all steps sit strictly
  above the limit by construction, so a strict comparison *"would have called every healthy
  transient run in the lab an excursion."*

`docs/standards/MESH_STANDARD.md` §7.4 adds the reporting rule: **the recorded Courant number
is the MAXIMUM over the run, for both `Co` and `alphaCo`, never the final line**; a run under
`adjustTimeStep` **records whether its cap was exceeded and by how much** — *"Exceedance is
normal; an unrecorded exceedance is not."*

### 2.2 DOES IT BEAR ON THE PLATEAU CLAUSE AND ON ROACHE TRIPLE GATING? YES — see §3

The plateau clause is what turns a value into a measurement in this team's frozen
comparators, and it is CLAUDE.md rule 5 step 1. The standards book's S12 and S13 grade the
same question by two different constructions. The comparison is the substance of §3 and is
not repeated here.

**On rule 5 itself the book adds nothing and contradicts nothing.** Roache triple gating,
Fs = 1.25, and the never-quote-a-GCI-on-non-monotone-values rule are CLAUDE.md rule 5 and
`T1b_L4_AMENDMENT.md`, not the standards book. What the book adds is the **family-size**
question of §4 below.

### 2.3 PRECONDITIONERS, CFL AND UNSTEADY RUNS — Sanaa's rule 2, mapped

Her rule 2: *"When a grid doesnt converge, try different pre conditioners, see if that's a
raised issue online/in the litterature, check for bugs, if unsteady check cfl, pick different
meshing"*. Where each clause lands in the book:

| her clause | what the book prescribes | status |
|---|---|---|
| *"try different pre conditioners"* | **NOTHING. The standards book says nothing about linear-solver preconditioners** — not in the mesh standard, not in the monitor standard, not in the innovation standard. The nearest thing in the lab is `PROBLEM_RESEARCH_PROTOCOL.md` §1 tier 2's worked example, which is a **warning**: *"the 'obvious' PETSc ILU shift fix has been hard-coded in DAFoam since 2022; a docket item to 'try the shift' would have burned a run on a no-op."* | **GAP, reported not filled.** The lesson transfers as a method: **check the deployed source at the exact version before proposing a preconditioner change** (§1 tier 2's *"deployed-source check first, not last"* — *"the single highest-leverage read of the whole pass was three lines of the shipped C file"*). |
| *"see if that's a raised issue online/in the litterature"* | `PROBLEM_RESEARCH_PROTOCOL.md` in full: source tiers in payoff order (upstream issues **AND discussions** — *"a zero-hit issue search proves nothing until discussions were swept too"*; upstream source pinned to a sha; docs **and** the tutorials repo; mailing lists; forums as **leads only**; papers). Three search rings: literal machine string → maintainer's mechanism words → the mechanism we measured. **Every zero-hit query is logged with where it ran** — that recorded negative is what later justifies "unreported upstream." | **DIRECTLY APPLICABLE.** See §3.5 for the one thing it obliges that a memo does not discharge. |
| *"check for bugs"* | `INFRA_FAMILY_SUPERVISION_GUIDELINES.md` §1.8: **evidence is derived from what EXECUTED, never from what was DECLARED**; and *"Fix false-positive channels before false-negative ones"* — *"A gate that fails open costs evidence you can still go and collect. A gate that fails false costs the ability to tell verified from unverified anywhere it may have fired."* | **APPLICABLE**, and it is the discipline VMFL045's own energy-key bug was found under. |
| *"if unsteady check cfl"* | **S8** (2 % tolerance; FATAL only on monotone growth at FIXED dt) **and MESH_STANDARD §7.4** (max over the run, never the final line; record the exceedance). | **DIRECTLY APPLICABLE AND MEASURED — see §3.4.** |
| *"pick different meshing"* | `docs/MESH_STANDARD.md`: a stated Level index with the same refinement rule at every step; y⁺-anchored Δy1 with a **<1.2× growth-rate ceiling**; **provision the full 6-level family up front**; report scatter as an **IQR/std band**, never a point estimate. Plus the NACA-4412 anti-pattern: a ladder whose rungs differ by *"which single `addLayersControls` knob was toggled"* is **NOT VALIDATED**. | **APPLICABLE**, and it constrains how a "different meshing" attempt may be run — see §3.2. |

---

## 3. CONFLICTS WITH WHAT THIS TEAM HAS ALREADY FROZEN

**Disclosed precisely. NOT reconciled. No frozen file was edited, and none of the four
findings below changes any verdict already recorded.** Retiring or widening a gate,
threshold or band is Sanaa's alone (CLAUDE.md, reserved matters).

### 3.1 CONFLICT — the plateau clause's SHAPE is the shape S13 argues against, on both axes

**What is frozen.** `grade_vmfl051.py` and `grade_vmfl045_r2.py` (identical construction):

```
PLATEAU_FRAC = 0.20      # last 20 % of the gate time series
PLATEAU_TOL_MA = 1.0e-3  # peak-to-peak in Mach units
```

— an **ABSOLUTE** peak-to-peak tolerance over a **FRACTION-OF-RUN** window.

**What S13 v1.12 says about each half, in its own words.**
- On the normaliser (D389): *"A criterion normalised by the mean measures the OFFSET on any
  quantity that carries one."* S13 refers peak-to-peak to **the range the quantity spanned
  over the whole run**. This team's clause refers it to **nothing** — it is absolute.
- On the window: *"a fraction-of-run window silently loosens as a run is extended, so the
  same case passes by being run longer."* S13 uses a **fixed window of outer iterations**.

**MEASURED, from the `volFieldValue.dat` files on disk, re-deriving this team's own numbers
first as a control.** The frozen clause's own figures reproduce exactly (6.240e−03,
3.535e−03, 8.549e−04 for VMFL051 L1/L2/L3), so the re-reading below is the same series.

| level | series rows | full-run range | frozen ptp (abs, 20 % window) | **vs frozen tol 1.0e−3** | **as % of run range** | **vs S13's 0.02 %** |
|---|---|---|---|---|---|---|
| VMFL051 L1 | 1 693 | 0.73280 | 6.2402e−03 | **6.24× — FAILS** | **0.85156 %** | **43× — would FAIL** |
| VMFL051 L2 | 3 365 | 0.72671 | 3.5354e−03 | **3.54× — FAILS** | **0.48650 %** | **24× — would FAIL** |
| VMFL051 L3 | 6 714 | 0.73006 | 8.5488e−04 | 0.85× — passes | **0.11710 %** | **5.9× — would FAIL** |
| VMFL045-R2 L1 | 3 127 | 0.62987 | 3.8422e−04 | 0.38× — passes | **0.06100 %** | **3.05× — would FAIL** |
| VMFL045-R2 L2 | 6 305 | 0.62717 | 6.1403e−05 | 0.06× — passes | 0.00979 % | passes |
| VMFL045-R2 L3 | 12 661 | 0.62704 | 7.7687e−05 | 0.08× — passes | 0.01239 % | passes |

**THE TWO CONSEQUENCES, AND THEY POINT IN OPPOSITE DIRECTIONS.**

1. **On VMFL051 the conflict is harmless and the verdict is MORE robust, not less.** S13's
   form refuses **all three** levels where the frozen clause refused two. `NOT A RESULT`
   stands under either reading, and step 2's `OSCILLATORY` triple (R = −1.348600) is an
   independent second reason. **Nothing about VMFL051 needs revisiting.**
2. **On VMFL045-R2 the conflict is material and is disclosed as such.** Its **coarse level
   L1 reads 0.06100 % of its own run range — 3.05× S13's threshold** — while the frozen
   absolute clause passed it at 0.38× of tolerance. VMFL045-R2 is this team's **third
   credential** (`PASS`, tier `GATE REACHED`). **The `PASS` is not withdrawn and is not in
   question**: the gate was frozen before compute, the frozen clause was applied unmodified,
   and CLAUDE.md rule 2 closes gates after first compute. What is disclosed is that a
   different, lab-standard settle criterion reads the **coarse** level as the least settled
   of the three — which is **new, independent support for the concern this team already put
   on the record itself**, namely that its G column is unclean (observed order **p = 3.3862**
   above the scheme's formal order; **d21 = 2.447e−04 against an L3 noise floor of 7.769e−05,
   a ratio of 3.150**, re-derived here from the RESULTS table).

**AND THE WINDOW SHAPE BITES EXACTLY WHERE THE OBVIOUS REMEDY LIES.** The natural fix for
VMFL051 is a longer `endTime`. Under a **fraction-of-run** window, lengthening the run moves
the window later into the settled region and therefore makes the clause **easier to pass —
which is precisely the failure mode S13 names.** Under a **fixed-iteration** window it would
not. **A VMFL051 re-run that clears the plateau clause only by being longer has not
demonstrated settling, and any new pre-registration for it should say so and gate on a fixed
window.** That is a design note for a NEW registration, not an amendment to a frozen one.

**S12 is a clean independent corroboration and fires on nothing.** Applied as a diagnostic to
all six levels: relative drift ranges **−1.1189e−06 to −1.4985e−05** (against S12's 1e−3
floor) and monotone fraction **0.489 to 0.592** (against 0.90). **S12 clears every level of
both cases.** The two criteria disagree because they measure different things — S12 measures
*direction*, S13 measures *spread* — and the honest reading is that these series **wobble
without travelling**. That is a real, favourable finding for both cases.

### 3.2 CONFLICT (house practice vs a standing rule) — three rungs against a six-level family

`docs/MESH_STANDARD.md` is unambiguous: *"**Provision the full 6-level family up front**, not
a 3-rung ladder extended reactively when Richardson extrapolation fails to settle. The DPW
family's whole point is that 6 levels exist precisely because 3 is not reliably enough to
detect a moving observed order before publishing a GCI number as if it were settled."* Its
measured precedent is this lab's own TMR flat-plate ladder: **adding a 4th rung moved the
observed order from 1.0833 to 1.2587**, and the GCI fell 2.09 % → 0.70 % *"only once the
extra rung was appended reactively."*

**Every pre-registration this team has frozen is a 3-level triple**, because CLAUDE.md rule 5
and `ANSYS_VERIFICATION_CHARTER.md` §5.5 specify a triple. **The tension is between a
standing rule (a 3-level Roache triple) and house practice (a 6-level DPW family), and it is
not this lane's to resolve.**

Where it bites, measured:

| case | observed order p | formal order | GCI_fine | reading |
|---|---|---|---|---|
| VMFL001-R2 | **2.0102** | 2 | 0.0563 % | matches formal order; clean |
| VMFL005 | **1.9341** | 2 | 0.0502 % | matches formal order to 3.3 %; clean |
| **VMFL045-R2** | **3.3862** | 2 | 0.0017 % | **above formal order; the team's own record already calls it *"measured but NOT trusted"* and the GCI *"NOT a discretisation-uncertainty statement"*** |
| VMFL051 | none | — | none | triple `OSCILLATORY`, R = −1.348600; correctly no GCI quoted |

**The standards book independently prescribes the remedy this team had already identified.**
The board records that a fourth, coarser level is needed on VMFL045 to test whether the
triple is asymptotic; `docs/MESH_STANDARD.md` says the same thing as general practice, and
supplies the lab's own precedent for why. **The two agree, which is the useful part.**

**Not a conflict, but binding on Sanaa's item 1, and easy to miss:** `docs/MESH_STANDARD.md`
§c's scatter conventions include *"**Fully-qualified model naming as a scatter-reduction
lever** … Any Certonomous report comparing runs across models must name the exact variant
and closure constants, not a family name"* — DPW's own example being *"French Vanilla
SA-(neg) (All-terms)"*, not generic "SA". **Every "try other models" pre-registration this
team writes must name the variant AND its closure constants**, not `kEpsilon`. VMFL003's
current record names `kEpsilon + nutkWallFunction`, which is the OpenFOAM class pair and not
the constants (C_mu, C1, C2, sigma_eps, kappa, E).

### 3.3 NOT A CONFLICT — a coverage gap, named as one

`docs/standards/MESH_STANDARD.md` §6's birth certificate: 23 `log.checkMesh`, **0
certificates**. Fully stated at §1.3 above. **CHECKED BUT UNCERTIFIED** is the honest label;
the metrics all pass; the enforcement chokepoints do not reach this team's `blockMesh` path.

### 3.4 NEW MEASUREMENT — a Courant exceedance nobody had recorded, and it is above S8's tolerance

This is not a conflict with a frozen file. It is a number the frozen comparators **do not
read at all** — `grep -ci 'courant\|maxCo'` returns **0 mentions in both**
`grade_vmfl051.py` and `grade_vmfl045_r2.py` — and which `docs/standards/MESH_STANDARD.md`
§7.4 rules 1 and 3 say must be recorded. **It is recorded here for the first time.**

Both compressible cases run `rhoCentralFoam` under `adjustTimeStep yes; maxCo 0.4;` — so
they are **transient solvers marched to steady state**, and Sanaa's *"if unsteady check cfl"*
lands squarely on them.

| level | Courant lines | **MAX over run** | **FINAL line** | max ÷ maxCo(0.4) | **overshoot** | steps strictly > 0.4 | **S8 (2 % tol)** |
|---|---|---|---|---|---|---|---|
| VMFL051 L1 | 1 693 | 0.401297 | 0.400013 | 1.0032 | **+0.32 %** | 873 (51.57 %) | silent |
| VMFL051 L2 | 3 365 | 0.401323 | 0.399657 | 1.0033 | **+0.33 %** | 1 718 (51.05 %) | silent |
| VMFL051 L3 | 6 714 | 0.401228 | 0.399800 | 1.0031 | **+0.31 %** | 3 485 (51.91 %) | silent |
| VMFL045-R2 L1 | 3 127 | 0.405922 | 0.402199 | 1.0148 | **+1.48 %** | 1 553 (49.66 %) | silent |
| VMFL045-R2 L2 | 6 305 | 0.407309 | 0.397445 | 1.0183 | **+1.83 %** | 3 548 (56.27 %) | silent |
| **VMFL045-R2 L3** | 12 661 | **0.412936** | 0.400207 | **1.0323** | **+3.23 %** | 6 789 (53.62 %) | **would FLAG** |

**Five things, each bounded.**
1. **§7.4 rule 1 is demonstrated on this team's own data.** On VMFL045-R2 L3 the final line
   reads **0.400207** and the maximum over the run is **0.412936** — the final line
   understates the maximum by a factor of 1.032, and the final line is the number a casual
   reading would have quoted. *"An `adjustTimeStep` run overshoots its own cap between
   adjustments, and the final line of the log is not the maximum."*
2. **The 49.66–56.27 % of steps above the limit is EXPECTED and is not a finding.** F7a
   measured 27–43 % in four healthy runs; this is the adaptive stepper working, and is
   exactly why S8 carries a tolerance rather than a strict comparison.
3. **VMFL045-R2 L3's +3.23 % is above S8's adopted 2 % tolerance** and is **8.0× the largest
   overshoot anywhere in the F7a archive (0.403 %)** against which that tolerance was
   calibrated. Under S8 as written that level is a **FLAG (Courant excursion)**.
4. **S8's FATAL branch does NOT fire and cannot**: it requires monotone growth across 20
   consecutive steps **with the time step held fixed**, and every one of these runs uses
   `adjustTimeStep`.
5. **This changes no verdict and is not offered as one.** The frozen VMFL045-R2 gate contains
   no Courant clause, gates were closed at first compute, and S8 is by the monitor standard's
   own coverage table **UNREACHABLE on production paths and carries no replay line at all**
   (*"S8. No replay exists at all"*). A rule with no replay line is, in that standard's own
   words, **a hypothesis, not a check.** What is claimed here is exactly this: a number was
   measured that the record did not carry, it is above a calibrated tolerance, and it is
   **level-dependent** (+1.48 % coarse → +3.23 % fine). **A level-dependent time-integration
   error is a candidate contributor to an observed order above the formal order**, and that
   is a hypothesis for the fourth-level re-run of §3.2 to test — not a conclusion.

**A contribution back to the lab, worth naming:** the monitor standard states S8's replay
corpus as *"21 transient logs with residual series."* This team's six `rhoCentralFoam` logs
(3 VMFL051 + 3 VMFL045-R2), each with 1 693–12 661 Courant lines, are transient logs of a
family the archive did not have — a **compressible density-based solver**, where the four
F7a calibration runs were `interFoam` VOF. **That is a 29 % widening of S8's prospective
corpus and a new physics family in it**, offered to the verification and cfd teams.

### 3.5 AN OBLIGATION, NOT A CONFLICT — a research pass may not close on a memo

`PROBLEM_RESEARCH_PROTOCOL.md` §4 is binding once this team acts on Sanaa's *"see if that's
a raised issue online/in the litterature"*: if any of four triggers fires, **the pass does
not close on a memo alone and must produce a docket proposal** — (1) a concrete, settable,
untried option exists for the live blocker; (2) the fix already exists upstream; (3) an
upstream claim contradicts a lab measurement; (4) a pinned mechanism is unreported upstream.

**And §4 trigger 4's action is a DRAFT and nothing more.** Its own words: *"proposal to
file/report upstream. **Drafts only: the liaison is read-only on the web — never post,
comment, or create accounts.**"* That is the same line as CLAUDE.md rule 7 and this team's
charter §8, arrived at independently. **SUBMISSIONS REMAIN PARKED.** Reading upstream issue
trackers and the literature is inbound and permitted; posting, filing, commenting or opening
an account is not, by any agent, ever.

**One method note that will pay immediately if VMFL051 is researched:** §5's *"Deployed-source
check first, not last"* — *"the single highest-leverage read of the whole pass was three lines
of the shipped C file; it should be step zero whenever the blocker names a code path."* For
VMFL051 the code path is named: `rhoCentralFoam` at OpenFOAM v2606 on this box.

---

## 4. DOES IT CHANGE THE NEXT TRANCHE OF NEVER-RUN CASES? YES — four concrete changes

**The tranche, measured from `docs/ansys_verification/CASE_MAP.md` at HEAD.** 70 rows carry
`NEVER RUN` (denominator 73, 3 run — the fraction the board records). Composition:

| axis | counts |
|---|---|
| dimension | 40 × 2D, 18 × axisymmetric, 10 × 3D |
| ladder feasibility | 8 clean `Y`, **58 caveated `Y*`**, 0 `N` |
| **gate shape** | **55 are a `profile`** (a plotted curve with no discrete target row), 12 are `discrete(N)` |
| cost class | 12 trivial (<5 core-min), 44 small (<60), 8 medium (<600), 4 large (≥600) |
| physics | 29 turbulent, 12 carrying a stated y⁺ band, 9 transient / time-accurate / periodic |

### 4.1 The y⁺ band is now a MESH-DESIGN input, not a caveat in a comment

**12 of the 70 carry a stated y⁺ caveat** (VMFL012 wavy channel, VMFL013 backward step +
heat, VMFL027 realizable-kε backward step, VMFL028 pipe expansion, and eight more).
`docs/MESH_STANDARD.md` §b gives the machinery — a per-level Δy1 target under a **<1.2×
growth-rate ceiling** and a minimum count of constant-spacing wall cells (2 at Tiny rising to
7 at Ultra Fine) — **but its numbers target y⁺ ≈ 1.00 → 0.29, i.e. wall-RESOLVED.** For a
wall-function case the target band is the log layer.

**The rule this team should carry into every wall-bounded pre-registration**, and VMFL003 is
the measured argument for it: **declare the wall-treatment class and its y⁺ band BEFORE
meshing, state which direction the triple refines, and state in advance what the ladder in
the OTHER direction is worth.** VMFL003 did exactly this and it is why its `GATE FAIL` is
diagnosable at all — 7.8 ppm axial against 1.7356 % wall-treatment, a factor of ~2200.

### 4.2 A "profile" gate needs its scalar functional named in the pre-registration

**55 of 70 gates are profiles**, and `docs/MESH_STANDARD.md`'s NACA-4412 anti-pattern is
precisely about a band that is not fixed in advance: an acceptance band *"anchored on the
solve's own Cl"* widened until *"the **worst-resolved rung (4.36 % coverage) passed** and the
**two best-resolved rungs (94 %+) failed**."* Verdict on record: **NOT VALIDATED.**

**So: for a profile case the pre-registration names the scalar functional it gates on — a
peak, a reattachment length, an integral, a value at a stated station — and its band, before
compute, and the band is never a function of the lab's own solve.** The CASE_MAP already
anticipates this (*"a lab PASS needs a digitized profile or a scalar functional"*); the
standards book supplies the failure that makes it non-negotiable.

### 4.3 Scatter is reported as a BAND, and this team has never done that

`docs/MESH_STANDARD.md` §c: the DPW convention presents disagreement as **IQR *and* standard
deviation reported simultaneously**, never a point estimate; and *"a predicted **increment**
scatters roughly **3× less** than an absolute drag value."* This team reports single values
with a GCI. **Where a case's manual page prints an inter-code spread (VMFL003's did: Fluent
−1.214 %, CFX −0.018 %), that spread is the band's natural anchor** — and VMFL003's own
finding is the argument: its 2.5 % band was set to pass both commercial codes, and a band
tighter than **1.210428 %** *"would be gating the manual's own inter-code disagreement rather
than this lab's accuracy."*

### 4.4 Transient cases carry two extra registered fields from the start

**9 of the 70 are transient / time-accurate / periodic** (VMFL019 Stokes' first problem,
VMFL020 piston with dynamic mesh, VMFL023 vortex shedding, and six more). From §3.4's
measurement on this team's own corpus, every transient pre-registration should register, in
advance: **(a) `max_Co_over_run` — the maximum, never the final line — with the log line
quoted; and (b) whether the `maxCo` cap was exceeded and by how much.** Both are
`docs/standards/MESH_STANDARD.md` §7.4 rules 1 and 3, and neither is currently in any frozen
comparator this team owns.

And §7.4 rule 4, recorded so the experiment is not repeated: **do not spend a ladder on the
Courant knobs.** F7a measured tightening `maxCo` 0.5→0.2, `maxAlphaCo` 0.5→0.1 and
`nAlphaSubCycles` 1→3 as giving **+15.1 % against a +13.5 % baseline — worse**, and a 2.4×
larger fixed timestep at fixed mesh as moving the answer by **< 1 point**. *"On this case
these are stability and admissibility controls, **not accuracy knobs**."* Honest scope: that
was `interFoam` VOF; whether it transfers to `rhoCentralFoam` is unknown and untested.

### 4.5 The cheapest honest first tranche, unchanged in membership by this reading

The 12 `trivial` never-run cases (<5 core-min per level) remain the right next tranche on
cost grounds, and the standards book changes **how each is registered**, not **which**:
VMFL002 (p. 17), VMFL004 (21), VMFL007 (29), VMFL010 (39), VMFL019 (77), VMFL029 (109),
VMFL033 (119), VMFL050 (163), VMFL059 (185), VMFL061 (189), VMFL070 (207), VMFL076 (219).
Of these, **VMFL010 and VMFL007 are `discrete(N)` gates on clean `Y` ladders** — the cleanest
shape available — while **VMFL019 and VMFL050 are transient** and take §4.4's two extra
registered fields.

---

## 5. WHAT THIS LANE COULD NOT VERIFY

Stated plainly, per the reporting contract.

1. **Whether S8's 2 % tolerance transfers to a compressible density-based solver.** It was
   calibrated on four `interFoam` VOF runs. VMFL045-R2 L3's +3.23 % is above it; whether
   that is an excursion or the ordinary behaviour of `rhoCentralFoam` under `adjustTimeStep`
   is **not established**, and this lane did not run anything to find out.
2. **Whether the S13-form reading of VMFL045-R2 L1 (0.06100 % of range) actually contaminates
   the observed order.** It is a candidate mechanism alongside the Courant one; **neither is
   demonstrated**, and separating them needs the fourth level.
3. **Anything about `physics_rules.yaml`.** The mesh standard §5 says a gate value is
   enforced only once written there with its citation. This lane did not read that file and
   makes no claim about what is or is not currently enforced in code.
4. **The GitHub tree Sanaa linked.** Not fetched, by ruling (§0). If the remote `docs/standards`
   differs from the local one, **this reading would not know.** The local tree was verified
   byte-identical to HEAD, which is the strongest statement available from inside the box.
5. **Whether any peer team is mid-run on these cases.** Not checked in this task; it is a
   zero-compute records task and launched nothing.
