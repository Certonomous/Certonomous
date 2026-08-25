# F3 supersonic exact-theory suite — CONVERSION PRE-REGISTRATION

**Written 2026-08-24, frozen before any solver in this conversion has started.**
**Condition checked, not asserted (VERIFICATION_CHARTER §2b.1):** the run root
`verification/runs/F3_runs/conversion_2026-08-24/runs/` **does not exist** at the
time of writing; no case directory, no `0/`, no time directory and no
`log.rhoCentralFoam` beneath it exists. The launcher `rerun_f3.py` refuses (rc=3)
any case directory that already exists, so this condition is enforced and not
merely stated.

**Frame:** repo `/home/ubuntu/Certonomous`, tracked tree at `69d2f1ba`.
**Team:** cfd. **Lane:** lab-lane under cfd-supervisor.

**Why this document exists — Sanaa's directive, verbatim:**

> *"CFD team — Re-run under frozen pre-registrations, <40 core-min each: F3
> (supersonic exact suite), F11 (per capability map), F4 (hypersonic) — the
> early PASSes that lack prereqs convert to HOLDS."*

---

## 1. The defect being repaired

`verification/campaign/F3_supersonic_exact_theory.md` (2026-07-28, repo @
`ce534b3`) records **PASS on five gates** — wedge surface pressure, wedge shock
angle, cone surface pressure, cone shock angle, diamond wave drag — across 17
`rhoCentralFoam` runs costing 38.45 core-minutes.

**There is no pre-registration for any of it.** Every band in that record was
written after its number was known. Under standing rule 2 the freeze *is* the
evidentiary content of a pre-registration: it proves the gate could not have been
chosen to fit the answer. A band written afterwards proves nothing about the
band, whatever it proves about the solver.

So the 2026-07-28 record is a **result, not a credential**. This document
converts it: the gate, the reference, the band, the cap, the label vocabulary
and the grading path are fixed here, committed, and only then re-run.

**What the old record actually claims, including what is weaker than the word
PASS suggests** — stated here so this document cannot later be accused of having
discovered it afterwards:

| Old gate | Old fine-mesh result | Weaker than "PASS" reads |
|---|---|---|
| Wedge p2/p1 | 0.01–0.07% dev, 3 pairs | — |
| Wedge shock angle β | −1.10 / −0.96 / +1.26% (excl-first fit) | the record prints **two** fits per row and says the better one changes with resolution; the old record chose neither in advance |
| Cone pc/p1 | +0.29% (M2.35), +0.19% (M3.0 medium only) | the M3.0 pair has **no fine mesh at all** — it was graded PASS on a medium mesh |
| Cone shock angle β | +2.14% (excl-first), +2.81% (all stations) | the record's own verdict line reads **"PASS, not fully grid-converged"** — an open, undischarged sensitivity carried inside a PASS |
| Diamond cd | −0.26%, −0.18% | — |

The cone β row is the one this conversion exists for. "PASS, not fully
grid-converged" is not in the verdict vocabulary (standing rule 1) and it is not
a verdict; it is a PASS with a caveat attached to soften it.

---

## 2. What is already known at the time of writing

Declared, so this document cannot be accused of following the answer.

**Every number in §1's table was known before this pre-registration was
written.** This is a conversion of an existing record, so the freeze here cannot
and does not claim ignorance of the 2026-07-28 values. What it protects is
narrower and is stated exactly:

> The freeze protects against tuning a band to **the values this re-run
> produces**. It does not, and cannot, protect against knowledge of the
> 2026-07-28 values.

The defence against that residual is in §4: **every band below is derived from a
stated principle — the reference's own class, or the detector's own quantization
floor computed from mesh geometry — and not from any measured deviation.** Where
a derived band happens to be near an old number, the derivation is shown so a
grader can attack it. Where a derived band would fail an old PASS, it is left
where the derivation puts it.

**Not known at the time of writing:** any value this re-run produces; whether any
grid triple in this matrix converges; whether the cone β row survives a band it
did not choose.

---

## 3. The gates, fixed now

Five gates, matching the five the old record claims. Verdicts come from the fixed
vocabulary and from nowhere else: **PASS / GATE REACHED / GATE FAIL / NOT A
RESULT / BLOCKED / PENDING** (standing rule 1). `PENDING` is used only for "not
yet run" and never to soften a `GATE FAIL`.

| id | gate quantity | reference (class) | band | grid triple |
|---|---|---|---|---|
| **G-F3-1** | wedge surface pressure `p2/p1`, patch face values, no interpolation | oblique-shock relations, **exact analytic** | ±0.5% | M2.0/θ15 only |
| **G-F3-2** | wedge shock angle β, excl-first fit | θ-β-M, **exact analytic** | ±2.0% | M2.0/θ15 only |
| **G-F3-3** | cone surface pressure `pc/p1` | Taylor-Maccoll, **exact analytic (own verified solver)** | ±0.5% | yes |
| **G-F3-4** | cone shock angle β, excl-first fit | Taylor-Maccoll, **exact analytic (own verified solver)** | ±2.0% | yes |
| **G-F3-5** | diamond wave drag `cd`, integrated pressure force | shock-expansion theory, **exact analytic** | ±1.0% | M2.0/ε7.125 only |

### 3.1 The reference values, frozen to full double precision

Computed by `verification/runs/F3_runs/exact_theory.py`, which takes **no CFD
input of any kind**. Frozen numerically in `grade_f3.py` so the reference cannot
drift if that module is later edited:

| case | β exact (deg) | pressure ratio exact | cd exact |
|---|---|---|---|
| wedge M2.0 θ15 | 45.343616761855984 | p2/p1 = 2.1946531336077966 | — |
| wedge M3.0 θ15 | 32.240400182744665 | p2/p1 = 2.821562321277495 | — |
| wedge M2.5 θ10 | 31.85059223127216 | p2/p1 = 1.8638705181801498 | — |
| cone M2.35 θc10 | 26.73671771893154 | pc/p1 = 1.3739363670377716 | — |
| diamond M2.0 ε7.125 | — | — | 0.036331061285517954 |
| diamond M2.5 ε5.0 | — | — | 0.01343027834624868 |

**Provenance of the reference class.** The θ-β-M and oblique-shock building
blocks were checked against NASA GRC's own analytic 15°-wedge / M=2.5 page
(`oblshk.f`, tol 1e-6) to **six significant figures on all five quantities**; the
Taylor-Maccoll shooting solver was checked against the NASA GRC 10°-cone / M=2.35
page's grid-converged multi-code CFD table (M3 dev −0.003%, p3/p1 dev −0.012%)
after that page's own labelled "Theory" row was found internally inconsistent
with stagnation-temperature conservation. Both trails are in `exact_theory.py`
and in §0 of the 2026-07-28 record. **Nothing in this conversion re-opens them.**

### 3.2 The identity test — what would make each gate FAIL, and how a wrong treatment could still pass (VERIFICATION §2a)

- **G-F3-1 / G-F3-3 (surface pressure).** Fails if the post-shock wall pressure
  is more than 0.5% from the analytic value. *Could a wrong treatment pass?* The
  reference is computed from M and γ alone by a module that reads no CFD output,
  and the measured value is read off the solver's own patch faces, so there is no
  route by which the measurement is derived from the reference. **We know of no
  way a wrong treatment passes it.**
- **G-F3-2 / G-F3-4 (shock angle).** Fails if the fitted shock locus is more than
  2.0% from the analytic angle. *Could a wrong treatment pass?* **Yes, in one
  way:** a detector pinned to a fixed y regardless of the flow would produce a
  stable, plausible β. That is why (a) the planted-zero control PZ-2 requires the
  frozen detector to relocate a synthetic step to an arbitrary known position,
  and (b) the M2.0 wedge and the cone carry grid triples, since a pinned detector
  yields a zero-increment (`EXACT`/`STAGNANT`) triple and is caught by rule 5.
- **G-F3-5 (wave drag).** Fails if the integrated pressure drag is more than 1.0%
  from shock-expansion theory. *Could a wrong treatment pass?* A solver that got
  the compression panel too high and the expansion panel too low by compensating
  amounts would pass on the integral while being wrong on both panels. That
  cancellation is **not** gated here and is declared as a known blind spot; the
  per-panel pressures are reported as a diagnostic, never gated.

---

## 4. Where each band comes from — derivations, fixed before compute

**No band below was read off a measured deviation.**

### 4.1 ±0.5% on surface pressure (G-F3-1, G-F3-3)

The reference is **exact analytic**, so it contributes zero uncertainty and the
whole error budget is numerical. `p2/p1` is read from patch face centres with
`interpolate false` — no interpolation, no detector, no fit — so the only error
term is discretization. `rhoCentralFoam`'s reconstruction is nominally
second-order, and every level of this ladder halves `h` exactly (§4.4), so a
medium-level error of order 1% must fall by ≈4× at fine if the solver is
second-order-consistent on this quantity. **±0.5% is that requirement, stated as
a band.** It is a real bar: a first-order-behaving solve would land near 0.5–1%
and fail it.

### 4.2 ±2.0% on shock angle (G-F3-2, G-F3-4)

β is not read; it is **detected and then fitted**, and its floor is the
detector's own quantization. Computed here from **mesh geometry only, with no CFD
value entering**, for the fine wedge meshes this matrix will run:

| case | domain height H | fine Δy = H/80 | 1σ(β) | **2σ(β)** |
|---|---|---|---|---|
| wedge M2.0 θ15 | 1.6193 | 0.02024 | 0.759% | **1.518%** |
| wedge M3.0 θ15 | 1.0092 | 0.01261 | 0.963% | **1.926%** |
| wedge M2.5 θ10 | 0.9940 | 0.01242 | 0.969% | **1.937%** |

(1σ from uniform quantization σ = Δy/√12 on each of the 5 fitted stations,
propagated through the frozen least-squares slope over the station span, then
through β = atan(m). The arithmetic is reproduced by
`grade_f3.py::beta_quantization_pct`.)

**The band is set at 2.0%, the rounded-up 2σ quantization floor of the family's
fine meshes.** A band tighter than that would be gating the detector's discrete
arithmetic rather than the solver.

**The band is 2.0% for every case in the family, including the cone.** β is the
same measured quantity produced by the same detector; a family gate does not get
a per-case bar sized to what each case can achieve. If the cone geometry gives
that detector a larger quantization floor, **that is a property of the cone, not
a licence for a wider bar** — and `grade_f3.py` prints each case's own floor
beside its row as a diagnostic that never moves a verdict.

### 4.3 ±1.0% on wave drag (G-F3-5)

`cd` is an integrated pressure force over the whole airfoil surface, taken from
OpenFOAM's own `forces` function object — no detector, no fit. It carries two
panels' worth of the §4.1 surface-pressure budget (a compression panel and an
expansion panel), plus leading- and trailing-edge corner smearing that the wedge
gate does not see. **±1.0% = 2 × the §4.1 band**, one band per panel.

### 4.4 The grid triples and standing rule 5

Every generator doubles **both** mesh directions between levels
(`make_wedge_case.py` / `make_cone_case.py` / `make_diamond_case.py` `RES`
tables), so **h halves exactly and r = 2 by construction** — the refinement ratio
is not inferred from a cell count, so VERIFICATION §3.1's dimensionality
assumption cannot corrupt it. The observed order is reported at **dim = 2**
(justified: the wedge and diamond meshes are single-cell-thick 2-D `blockMesh`
slabs; the cone is a single-cell-thick axisymmetric wedge slice, refined only in
x and r) **and at dim = 3**, which is exactly 1.5× the first.

**Standing rule 5 is applied in its stated order, without exception:**

1. any level failing the completion rule (§5) → the row is **NOT A RESULT**;
2. triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → **NOT A RESULT**,
   whatever the value, with the value, the triple, the increments and the orders
   printed beside it, and **no GCI quoted**;
3. triple `CONVERGING` → PASS inside the band else GATE FAIL, GCI at Fs = 1.25
   printed.

The triple can only turn a PASS or a GATE FAIL **into** NOT A RESULT, never the
reverse. Rows carrying no triple (wedge M3.0, wedge M2.5, diamond M2.5) are
graded on the band alone and **carry the annotation "no grid triple — no
discretization-error estimate" on their face**; they are not presented as
grid-converged.

### 4.5 Planted-zero controls (standing rule 3) — the comparator refuses if it cannot see a plant

`grade_f3.py` runs four controls and **exits 2** if any fails. None is optional
and none can be skipped by a flag.

| id | reader under test | plant | refusal condition |
|---|---|---|---|
| **PZ-1** | surface-pressure reader | additive `1.234e-03` into the p column of a **copy of the case's own artifact** | read-back offset differs from the plant by > 1e-9 |
| **PZ-2** | the frozen shock detectors `find_shock_y` (wedge) and `find_shock_r` (cone), tested separately | a **synthetic** sample line carrying a density step at a known, arbitrary fraction 0.3717 of its span | detector returns `None`, or misses the planted step by more than 2 sample spacings |
| **PZ-3** | the β least-squares fit | a known slope increment `1.000e-02` added to the stored shock locus | fitted β differs from `atan(m + 0.01)` by > 1e-6 deg |
| **PZ-4** | the `force.dat` reader | additive `1.234e-05` into the `total_x` column | cd differs from the definition's predicted shift by > 1e-12 relative |

PZ-3 and PZ-4 additionally **re-derive** β and cd independently from the primary
artifact and refuse if the re-derivation does not reproduce the runner's stored
value — so the grader is not taking `result.json` on trust for either.

**PZ-2 is the control this suite most needs**, because it is the only one that
demonstrates the shock detector can see a non-zero at all. A detector that
returned a constant would sail through every deviation test in the record.

---

## 5. The completion rule (standing rule 4), and its one declared adaptation

A run counts only if **all** of it holds. `grade_f3.py::completion_check` reads
each clause off disk and a run failing any clause is **not graded** — its row
carries the label, never a number.

| clause | as checked here |
|---|---|
| C1 `rc = 0` | `run_rc.txt`, written by the launcher, reads `0` |
| C2 `End` line | `^End$` present in `log.rhoCentralFoam` |
| C3 last time == `endTime` | \|last time dir − `endTime`\| ≤ `maxDeltaT`, **and** the log's final `Time =` equals that time dir |
| C4 fields present | `T U p rho` all present at the last written time |
| C5 log step integrity | count(`^ExecutionTime = `) == count(`^Time = `), and > 0 |
| C6 **age guard** | every field at the last written time is **strictly newer** than the latest mtime anywhere in the case's own `0/` |

**Two departures, declared here and not discovered later:**

1. **C3 tolerance.** These cases run `adjustTimeStep yes`, so the final written
   time lands *within one timestep* of `endTime` rather than exactly on it
   (`maxDeltaT = 1e-3` against `endTime` of order 4). The rule's literal equality
   is unmeetable for an adjustable-timestep solver; the tolerance is one
   `maxDeltaT`, read from the case's own `controlDict`, and the log's own final
   time must agree with the directory.
2. **C5.** The rule's literal clause is `ExecutionTime` count == `endTime`, which
   is a **steady-iteration** clause: it holds when one iteration is one time
   unit. `rhoCentralFoam` here is transient with an adaptive timestep, so its
   step count (~8,000) is not `endTime` (~4) and never can be. The invariant that
   clause exists to protect — *the log is not truncated mid-step* — is checked
   directly instead: one `ExecutionTime` line per `Time` line.
3. **C6 is STRICTER than the rule**, not looser: the rule dates the run from
   `0/T`; this check dates it from the **latest** mtime anywhere in `0/`.

The launcher additionally enforces the rule's own guard: **`rerun_f3.py` refuses
(rc=3) any case directory that already exists**, so no run in this conversion can
inherit a `0/` or a time directory from an earlier campaign.

---

## 6. The run matrix, fixed now

12 runs. Fresh directories under
`verification/runs/F3_runs/conversion_2026-08-24/runs/<family>/<pair>/<level>`.
The 2026-07-28 case generators and runners (`make_*_case.py`, `run_*_case.py`)
are used **byte-unchanged**; the launcher adds only `meta.json`, `run_rc.txt` and
a timing record, which those scripts do not write and the completion rule needs.

| # | family | pair | levels | purpose |
|---|---|---|---|---|
| 1 | cone | M2.35, θc = 10° | coarse, medium, fine | **the grid triple this conversion exists for** (G-F3-3, G-F3-4) |
| 2 | wedge | M2.0, θ = 15° | coarse, medium, fine | grid triple (G-F3-1, G-F3-2) |
| 3 | wedge | M3.0, θ = 15° | fine | band only |
| 4 | wedge | M2.5, θ = 10° | fine | band only |
| 5 | diamond | M2.0, ε = 7.125° | coarse, medium, fine | grid triple (G-F3-5) |
| 6 | diamond | M2.5, ε = 5.0° | fine | band only |

**Deliberately NOT re-run:** the cone M3.0/θc12 pair. The old record graded it
PASS on a **medium mesh with no fine level**, and a fine cone mesh costs ~17.9
core-min on its own — more than half this cap. Its old PASS is therefore **not
converted by this exercise and does not become a credential**; the results record
will say so in those words rather than carrying it forward silently.

---

## 7. Cost, costed before launch (standing rule 12)

Predictions are the 2026-07-28 record's **own measured per-run core-seconds**,
which is the only measured basis available for these cases.

| run | predicted core-s |
|---|---|
| cone M2.35 coarse / medium / fine | 16.3 / 118.9 / 1072.7 |
| wedge M2.0 coarse / medium / fine | 6.1 / 18.7 / 146.4 |
| wedge M3.0 fine | 149.0 |
| wedge M2.5 fine | 148.1 |
| diamond M2.0 coarse / medium / fine | 11.1 / 35.5 / 201.2 |
| diamond M2.5 fine | 189.8 |
| **total** | **2,113.8 core-s** |

**Arithmetic, shown:**

- core-minutes = 2,113.8 core-s ÷ 60 = **35.23 core-min** (every run serial,
  1 rank, so core-min = Σ wall-seconds ÷ 60).
- core-hours = 35.23 ÷ 60 = 0.5872 core-h.
- **dollars = 0.5872 core-h × $0.0513/core-h = $0.0301.**
- `cost_basis`: **reported-by-owner, NOT measured.** The rate $0.0513/core-h for
  c7a.4xlarge is owner-stated (Sanaa, 2026-08-21/22) and corroborated at
  `Xiao2016_EnKF/PREREGISTRATION.md:197`; this box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5). The **core-minutes** are the measured unit;
  the dollar figure is **derived**.
- Under the $25 pre-authorisation by four orders of magnitude. That
  pre-authorisation is not a new ceiling (standing rule 9): the cap below binds.

### The cap

**HARD CAP: 39.5 core-minutes** — under the directive's 40, with 4.27 core-min
(12%) of headroom over the prediction for contention. **An overrun stops the run;
it does not get a new budget.** Three enforcement points, all in `rerun_f3.py`:

1. **Per-run wall cap** — `max(120 s, 2.5 × predicted)`, and **1,500 s** for the
   cone fine run specifically. A run past its cap is SIGTERMed and graded
   `KILLED`.
2. **Pre-wave budget check** — a wave whose predicted cost does not fit the
   remaining budget with 20% headroom is **not launched**; its rows grade
   `PENDING`.
3. **Global watchdog** — polls every 5 s and terminates every live run the moment
   cumulative core-seconds reach 2,370 (= 39.5 core-min).

**Launch order is frozen** so that what the budget takes first is the least
load-bearing thing. Waves, at most 2 live at once:

| wave | runs | predicted core-s | cumulative core-min |
|---|---|---|---|
| 1 | cone coarse, cone medium | 135.2 | 2.25 |
| 2 | cone **fine**, wedge M2.0 coarse | 1,078.8 | 20.23 |
| 3 | wedge M2.0 medium, wedge M2.0 **fine** | 165.1 | 22.99 |
| 4 | diamond M2.0 coarse, diamond M2.0 medium | 46.6 | 23.76 |
| 5 | diamond M2.0 **fine**, wedge M3.0 fine | 350.2 | 29.60 |
| 6 | wedge M2.5 fine, diamond M2.5 fine | 337.9 | **35.23** |

If the budget stops the line, wave 6 is lost first — the two single-grid,
band-only rows — and **never a grid triple**.

**Concurrency: at most 2 live runs**, deliberately below the 4-rank ceiling, so
memory-bandwidth contention does not inflate the core-minute total. Load is
checked before each wave; the three `buoyantBoussinesqSimpleFoam` processes on
this box belong to heat-transfer and are not touched.

---

## 8. The grading path, fixed at this commit

| file | sha256 at freeze |
|---|---|
| `verification/runs/F3_runs/conversion_2026-08-24/grade_f3.py` | `fe9fe6dfa94f529634355da152486983a847d9003e6ab05c129585cfdff04f87` |
| `verification/runs/F3_runs/conversion_2026-08-24/rerun_f3.py` | `d53d32e8e779c3725bfe49b825535e9f58acb92023121f6f6f89e3467072abb2` |

**Verified at grade time, not merely recorded.** `grade_f3.py` is run as
`--prereg-commit <sha of this commit>`; it hashes its own source against
`git cat-file blob <sha>:verification/runs/F3_runs/conversion_2026-08-24/grade_f3.py`
and **REFUSES (exit 2)** if the file on disk is not byte-identical to the blob
committed here. A grading run with no such verification line in its output is
not a grade.

**No threshold in `grade_f3.py` is settable from the command line.** Every band,
every plant constant and every reference value is a module-level constant fixed
by this commit.

---

## 9. What each outcome will mean

Stated now, so no outcome can be re-read afterwards.

- **PASS** on a gate whose triple CONVERGES: the 2026-07-28 claim is converted
  and becomes a credential.
- **GATE FAIL**: the old PASS was unearned at the band this document derives. It
  ships as a documented failure (VERIFICATION §8) and the old record is annotated,
  not repaired.
- **NOT A RESULT**: the grid triple did not converge, or a level failed the
  completion rule. The value is printed beside it with both triples and both
  orders and **no GCI**. This is the honest label for the cone β row if its
  refinement behaviour is what the old record's own prose describes.
- **PENDING**: not launched, budget or otherwise. Never used to soften a fail.

**A GATE FAIL or a NOT A RESULT here is a success of this exercise**, not a
failure of it: it means the original PASS was unearned, which is precisely what
pre-registration exists to detect. **Nothing will be tuned to preserve the old
word.** Should any measured value land outside a band, the band stands and the
verdict follows the numbers.

---

## 10. Standing rules this document is bound by

Rule 1 (vocabulary, §3 and §9) · rule 2 (this freeze; grading path §8) · rule 3
(planted-zero controls §4.5) · rule 4 (completion rule §5) · rule 5 (Roache
triple gating §4.4) · rule 7 (nothing here is sent anywhere) · rule 9 (the $25
pre-authorisation is not a ceiling; the §7 cap binds) · rule 10 (committed under
the private-index protocol, this file and the two scripts only) · rule 12 (cost
§7, and a `docs/COST_CALIBRATION.md` row is mandatory at completion) · rule 13
(no scratch path is cited by this document) · rule 16 (silent background
operation).

---

## AMENDMENT 1 — 2026-08-25: THE ATTRIBUTION IN §"Why this document exists" IS WITHDRAWN

**Document version 1.0 → 1.1.** Appended at the foot under standing rule 6; the
original text above is **struck, never rewritten**. **lines whose number changed
above this section: 0.**

**Rule-2 condition, checked by `test -e` in this commit's own shell invocation and
not recalled:** `verification/runs/F3_runs/conversion_2026-08-24/runs` — the run
root §6 registers — **does not exist**. Its parent
`verification/runs/F3_runs/conversion_2026-08-24/` does exist and holds exactly the
two grading scripts frozen in §8 plus a `__pycache__/`; **no case directory, no
`0/`, no time directory and no `log.rhoCentralFoam` exists anywhere beneath it.**
The case is **UNFIRED**. No graded solve has started, §2b's **pre-compute** limb
governs, and this amendment is legal under it. **This amendment is ZERO COMPUTE:**
no solver was launched, no mesh was built and no case directory was created.

---

### A1.1 What is withdrawn

**Line 14** of this document introduces its motivating text as **"Sanaa's
directive, verbatim"** and sets it as a block quotation at lines 16–18:

> *"CFD team — Re-run under frozen pre-registrations, <40 core-min each: F3
> (supersonic exact suite), F11 (per capability map), F4 (hypersonic) — the
> early PASSes that lack prereqs convert to HOLDS."*

**That attribution is WITHDRAWN. It is struck, and the block quotation must not be
read as Sanaa's words by any future reader of this file.**

**The text is KEPT and re-marked as A cfd BRIEF'S PARAPHRASE**, following the
precedent this team and heat-transfer both set: withdraw the attribution, keep the
words, label them honestly. The paraphrase may still be cited as **what motivated
this document**. **It may never again be cited as her words, and never as a compute
authorisation.**

#### The source search, redone by this lane rather than inherited — and it does not reproduce the withdrawal note's own citation

The withdrawal recorded on `docs/LAB_STATE.md` sources the text to *"exactly two
places: `docs/LAB_STATE.md`, and cfd's OWN commit messages `2bf4915a` and
`157793db`."* This lane re-ran that search rather than taking it on trust — a
**non-ignoring** `find … -print0 | xargs -0 grep`, because a plain `grep -r` in
this repository honours ignore files and would have missed occurrences outside the
tracked walk. Two corrections result, and both are recorded against cfd:

1. **`157793db` does NOT contain the text.** Its full commit message — the F11
   conversion pre-registration freeze — was read in full at this commit. It
   *refers* to *"the directive's 40"* and *"the directive's 'early PASSes'"*, i.e.
   it **consumes** the figure; it never **reproduces** the quotation and is
   therefore **not a source of it**. Citing it as one was itself an unverified
   citation inside a withdrawal notice about unverified citation.
2. **Exactly ONE commit message in this repository's history reproduces the
   text, and it is `2bf4915a` — THIS DOCUMENT'S OWN FREEZE COMMIT.** The full
   `--all` commit-message sweep returns that commit and no other.

The text's tracked-file occurrences at this commit are four: `docs/LAB_STATE.md`,
`verification/campaign/F_FAMILY_TRIPLE_CROWN_SURVEY.md`, this file, and
`verification/campaign/F11_CONVERSION_PREREGISTRATION.md`. **None of the four is a
source.** Three are cfd's own documents quoting the paraphrase, and the fourth is
cfd's own board. **The text is not independently sourceable to anything Sanaa
said**, and no cfd supervisor heard it said or will vouch for it.

---

### A1.2 Why this correction is made HERE, and not only on the board

**The withdrawal was announced last session on `docs/LAB_STATE.md` and in a commit
message — and this document, which actually carries the attribution, was never
corrected.** `F_FAMILY_TRIPLE_CROWN_SURVEY.md` §8.4 named that gap explicitly and
left it open: *"`F3_CONVERSION_PREREGISTRATION.md` does not"* carry the correction.

**A withdrawal that does not reach the artifact bearing the claim has not been
made.** That is the defect this amendment repairs, and it is recorded here as **a
finding against cfd's own process, not as housekeeping.**

**L-309 applies directly: an attribution authorising SPEND must carry its source
when recorded.** The block quotation at lines 16–18 carries a **core-minute
figure**, and §7's cap is set by explicit reference to it (*"under the directive's
40"*). That is precisely the shape the lesson names: a spend authorisation frozen
into a pre-registration under an owner's name, with no source recorded beside it.

**Two further artifacts still carry the uncorrected reading. REPORTED, NOT FIXED
by this lane** — a board is the supervisor's to correct, and this lane's scope is
this file:

- `docs/LAB_STATE.md` **line 1748** carries the withdrawal, while **line 1833** of
  the same file still reads *"per Sanaa's §2 directive (verbatim in `2bf4915a`)"*
  and **line 1837** still lists *"F11 freeze then its <40 core-min re-run"* as a
  next action. The board contradicts itself on its own face.
- The `157793db` mis-citation above propagates from `docs/LAB_STATE.md` line 1748
  into `F_FAMILY_TRIPLE_CROWN_SURVEY.md` line 670 and into
  `F11_CONVERSION_PREREGISTRATION.md`'s AMENDMENT 2. Those documents' **conclusion
  is unaffected** — the text is still not sourceable to Sanaa, and is if anything
  sourceable to **fewer** places than claimed — but the citation is wrong in each.

---

### A1.3 The loop this document closed, and it is tighter here than it was for F11

On **2026-08-25** a **40 core-minute** figure reached the cfd supervisor through
the chief as a **per-item spend authorisation attributed to Sanaa**. F11's
AMENDMENT 2 named its own lines 22–27 as *"the most likely proximate source"*.

**On the evidence at this commit, the proximate source is THIS file.** F11's
quotation was itself copied from here: this document was frozen first, at
`2bf4915a`, and **`2bf4915a` is the only commit message in the repository that
reproduces the text.** The path is:

> **cfd wrote it → cfd froze it, in this file, as her words → cfd's own freeze
> commit message reproduced it → it propagated to F11, to the survey and to the
> board → it returned to cfd as her authorisation.**

**The laundering required no dishonest act by anyone.** It required only that one
label — *"verbatim"* — was applied to text whose source had never been checked, in
the one class of document the lab treats as unalterable. **A frozen document is the
worst possible place to put an unsourced attribution, because freezing is exactly
what stops anyone from correcting it in place.**

---

### A1.4 What this amendment does NOT change

**No gate, no threshold, no cap, no band and no label is altered by this
amendment.** All five gate bands (G-F3-1 ±0.5 %, G-F3-2 ±2.0 %, G-F3-3 ±0.5 %,
G-F3-4 ±2.0 %, G-F3-5 ±1.0 %), the §3.1 frozen reference values, the §4.5 plant
constants, the §5 completion clauses, the §6 run matrix, the §7 cap and wave order,
the §8 grading-path sha256 pair and every §9 verdict meaning stand **exactly as
frozen**.

Two conclusions in this document lean on the withdrawn figure. Standing practice
is that **a conclusion which survives the removal of a bad premise must be SHOWN to
survive it, not merely asserted to.** Both are worked below, and the second does
not come out clean.

#### A1.4.1 §7's cap of 39.5 core-minutes — SURVIVES, on this document's own arithmetic

§7 reads *"**HARD CAP: 39.5 core-minutes** — under the directive's 40"*. **That
justification is withdrawn: there is no Sanaa-authorised 40 core-minute cap and
there never was.** The number 39.5 was chosen by reference to a figure that had no
source.

**The cap nevertheless stands, and the demonstration is arithmetic, not assertion:**

| | this document (F3) | F11, whose cap was set **without** reference to the directive |
|---|---|---|
| prediction | 35.23 core-min | 8.02 core-min |
| cap | **39.5 core-min** | 13.0 core-min |
| cap ÷ prediction | **1.121** | 1.621 |
| headroom over prediction | **12.1 %** | 62.1 % |

F11's freeze commit `157793db` states its own standard in terms: its cap was set
*"at 62 % headroom, **not at the directive's 40**, because a cap 5× the prediction
is a rubber stamp and a blanket is not a per-item read (rule 9)."* **F3's cap is
TIGHTER against its own prediction than the cap that team set deliberately without
the directive** — 12.1 % headroom against 62.1 %. It therefore satisfies, on this
document's own numbers, the standard cfd applied when it was *not* looking at the
withdrawn figure.

Three further points, each checkable:

- **A cap constrains; it never authorises.** Removing the reason a self-imposed
  ceiling was set *low* can make it look unnecessarily tight. It cannot make it
  unsafe, and it cannot license raising it.
- **Rule 9 already governs the authority question and is unchanged.** §7 and §10
  both record that the **$25 pre-authorisation is not a ceiling and the §7 cap
  binds**. With the directive withdrawn, that sentence is not weakened — it becomes
  the *only* authority statement in the document, and it is the correct one. The
  predicted spend is **$0.0301 derived, not measured** (rate owner-stated, box
  cannot read its own billing), four orders under the pre-authorisation.
- **Rule 2 forbids altering a cap on a frozen document**, and this amendment does
  not attempt it even though the pre-compute limb would permit a change. **The cap
  stays at 39.5 core-minutes.**

#### A1.4.2 §6's exclusion of the cone M3.0/θc12 pair — the STATED reason does NOT survive, and its arithmetic is FALSE. The exclusion stands on a different ground, named here

§6 reads: *"**Deliberately NOT re-run:** the cone M3.0/θc12 pair. … a fine cone
mesh costs ~17.9 core-min on its own — **more than half this cap**."* This is the
F11 `n = 256` situation, and unlike F11 it does **not** come out clean. F11's
exclusion carried **two** reasons and the second was sufficient alone. **This one
carries exactly one, it chains through the withdrawn figure, and it is also
arithmetically wrong.**

**The arithmetic, checked:** the fine cone solve measured **1,072.7 core-s =
17.878 core-min** in the 2026-07-28 record (its §2 cost finding, and its own
per-case table). Half of §7's 39.5 core-minute cap is **19.75 core-min**.
**17.878 < 19.75.** The fine cone is **45.3 % of the cap, not more than half** —
short of the stated threshold by **1.872 core-min**. The claim is false as written,
under either denominator: it is also below half of the withdrawn 40.

The nearest **true** statement is about a different object: a full cone **grid
triple** at this pair costs 16.3 + 118.9 + 1,072.7 = **1,207.9 core-s = 20.13
core-min**, which does exceed half the cap — by 0.38 core-min. The frozen sentence
does not say that; it says *"a fine cone mesh … on its own"*.

**The stated reason is therefore withdrawn twice over** — once because it chains
through a cap justified by a sourceless figure, and once because its own comparison
is wrong. **It is struck and may not be cited again.**

**The exclusion itself STANDS, on a ground independent of every cost figure, and
this lane states plainly that it is NAMING that ground now rather than pointing at
one the document already gave.** The ground is this document's own §1 and §4.4:

1. §1's table records the M3.0 cone pair's specific defect: *"the M3.0 pair has
   **no fine mesh at all** — it was graded PASS on a medium mesh."* The defect is
   the **absence of refinement evidence**.
2. §4.4 governs what a single added level could buy: a row carrying no grid triple
   is graded on the band alone and must carry *"no grid triple — no
   discretization-error estimate"* **on its face**, and is *"not presented as
   grid-converged."*
3. **Therefore adding one fine cone M3.0 run converts nothing.** It would produce
   exactly the class of row whose deficiency is the thing being repaired. Only a
   full **grid triple** could convert that pair — and a grid triple is a **new
   gate-bearing scope item added to a frozen matrix after the freeze**, which is
   the precise manoeuvre standing rule 2 exists to prevent.

**And the direction of bias is decisive.** §6 states the consequence of the
exclusion in terms: the pair's old PASS *"is therefore **not converted by this
exercise and does not become a credential**"*. **The exclusion WITHHOLDS a
credential from this lab.** A contaminated premise that causes the lab to claim
**less** cannot inflate any verdict, band, PASS or credential in this conversion.
**No gate outcome of this document depends on the withdrawn figure in the
flattering direction**, and that is checkable against §3 and §9 rather than taken
on this lane's word.

**Open item for the supervisor, flagged and NOT taken by this lane.** The
pre-compute limb of rule 2 would legally permit widening §6's matrix to restore the
cone M3.0/θc12 pair as a full triple — 20.13 core-min, taking the campaign to
**55.36 core-min, 40 % over the §7 cap**, which would additionally require a cap
change this amendment refuses to make. **Widening a frozen matrix is a scope
decision above a lane's level and is not taken here.** It is recorded so that no
future reader is left resting on a reason this amendment has struck.

---

### A1.5 What remains true and is not disturbed

**Every band in this document was derived from a reference class or from mesh
geometry, and never from the directive's wording.** §4.1 derives ±0.5 % from
second-order consistency under exact halving; §4.2 derives ±2.0 % from the
detector's own 2σ quantization floor computed from domain heights and Δy alone;
§4.3 derives ±1.0 % as two panels of the §4.1 budget. **No withdrawn figure enters
any band's derivation**, and the withdrawal of the attribution touches none of
them.

**The paraphrase's phrase *"convert to HOLDS"* was never achievable for this
family, and that was established before this amendment.**
`F_FAMILY_TRIPLE_CROWN_SURVEY.md` (rank 4) records F3 as **`GATE REACHED`, missing
G and P**, with **P `NO — IMPOSSIBLE`**: *"exact theory admits no experiment"*, so
P can never be bought for this case. **This conversion earns V and G, and cannot
reach `HOLDS` whatever the five gates return.** That judgement rests on the physics
of the reference class and is untouched by the withdrawal of the attribution.

*(Tier vocabulary — `HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` /
`NEVER RUN` — is separate from and never conflated with the standing rule 1 verdict
vocabulary used in §3, §4.4 and §9.)*

*Written 2026-08-25 by a cfd lab-lane under cfd-supervisor, as a **ZERO-COMPUTE**
provenance correction. The rule-2 ABSENT condition was checked by `test -e` in the
committing shell invocation. Committed under the rule-10 private-index protocol,
this file alone, as a pure append proven three ways.*
