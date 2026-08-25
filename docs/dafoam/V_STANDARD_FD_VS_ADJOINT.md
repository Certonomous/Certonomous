# The adjoint family's V-column standard — FD-vs-adjoint as code verification

**Team:** dafoam. **Dated 2026-08-24.** **Scope:** every discrete-adjoint gradient this
lab produces with DAFoam, IDWarp, pyGeo and pyOptSparse — `cases/dafoam/` in full, and
the run trees under `/home/ubuntu/certonomous-runs/` that feed them.

**What this document is.** The V column of a code-coverage matrix means *code
verification*: an exact solution, a manufactured solution, or a correlation gate. **For a
discrete adjoint gradient none of the three exists.** There is no closed-form derivative
of a converged finite-volume SIMPLE/rhoSimple solve on an unstructured mesh, and no
manufactured solution for the transpose of a Jacobian this lab did not assemble. What
this family has instead is the **finite-difference-versus-adjoint check**: an
independently computed reference derivative, taken from the *same discrete function* the
adjoint differentiates, at a step proved to lie in a plateau. That check **is** this
family's code-verification standard. This document exists to make that claim inspectable
rather than asserted — every rule below is already registered somewhere in this lab, and
every number below was re-read from the artifact it cites while this file was written.

**What this document is NOT.** It **creates no gate, no threshold and no cap.** Every band
and bar here is quoted from a charter that already owns it; retiring or moving one is
Sanaa's alone (`CLAUDE.md` FIRST-ACTION RULE, reserved matters; rule 9). It is not a
charter and does not amend one. It does not edit any frozen record. Nothing in it is
filed, sent or posted anywhere (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Deliverable of curriculum item D15.** `cases/dafoam/EXPERTISE_CURRICULUM.md:126`, Tier 5
— *"Verification-at-scale institutionalization: the A6 mechanical step rule + measured-η
protocol applied as the standard endpoint check of every curriculum case"*, prerequisites
*"none — folds into each prereg"*, estimated cost **"~0 standalone"** core-min, falsifier
column **"n/a (it IS a gate template)"**. §13 below is that template. D15's registered
limitation — *"the rule's own registered limitation: on a rung whose adjoint is wrong, the
|J_adj| proxy sizes steps from a wrong number (RESULTS.md §7 limitation 8) — carried
verbatim into the template"* — is carried verbatim inside §13, as that row requires.

**Governing documents, in precedence order.** `docs/charters/VERIFICATION_CHARTER.md` §7
owns the band, the five-step reporting protocol and the harness floor.
`docs/charters/DAFOAM_CHARTER.md` §2–§5 and §9 own this family's instantiation.
`cases/dafoam/FAMILY_SUPERVISION_GUIDELINES.md` §4.2–4.3 owns the operational half
(`check_totals`, central differences, `step_calc="abs"`, one error convention throughout).
**This document cross-references; it does not duplicate, and where it and a charter
disagree the charter wins.**

**Disclosure about the coverage matrix itself, made because it is the reason this file was
commissioned.** `docs/COVERAGE_MATRIX.md` **does not exist on disk**, and a repo-wide grep
of `docs/` for "coverage matrix", "V column", "V-column" and "manufactured solution"
returns **zero hits**. The V-column definition in the opening paragraph is therefore
carried from the verification team's brief, **not from a committed artifact**. That
document is the verification supervisor's to write; this one states only what the adjoint
family can defend, and if the matrix's eventual V-column definition differs from the one
above, **this file's §13 checklist is the part that survives and the framing paragraph is
the part that must be re-read against it.**

---

## 1. The statistic, named as a statistic

> **This family's aggregate is the vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` as
> printed.** It is named as a statistic in every record that quotes it, and the
> per-component flags are reported beside it, never instead of it.

`DAFOAM_CHARTER.md` §2 is the governing clause and states it in those words. A worked
instance of the naming discipline is
`cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md` §4.2:

> *"Vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` over the EIGHT GRADED components =
> 1.0432%. Sign flips: 0. Flagged and excluded BY NAME: `twist` idx6. Not reached: none."*

### 1.1 It is NOT the statistic the toolchain's own authors use, and the two must never be compared

This is `DAFOAM_CHARTER.md` §2's first sub-point and it is load-bearing. All three
DAFoam/ADflow method papers were read in full; the protocol table is
`cases/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` §1, re-read for this document.
**No paper in the corpus uses a vector-norm relative error.**

| paper | operator verified | reference used | result as the on-disk table records it |
|---|---|---|---|
| He, Mader, Martins & Maki, **C&F 168 (2018)** §3.1 Tables 4–5 | v1 explicit FD-coloring Jacobian | FD, step studies | **per-component**: −0.00049 % best; **avg < 0.1 %**, worst **0.252 %** |
| He, Mader, Martins & Maki, **AIAA J**, DOI **10.2514/1.J058853** §2.4.2 Table 3 | v1 explicit FD-coloring Jacobian (Jacobian-free explicitly deferred to future work) | brute-force FD, step studies | **per-row**: avg **< 0.1 %**, worst flow row **0.195 %** |
| Kenway, Mader, He & Martins, **PAS (2019)** §5.1 — DAFoam row | Jacobian-free reverse-AD (operator overloading, dco/c++), **serial, np=1, stated twice, by design** | full-code AD (Towara & Naumann) — **not FD** | **10-digit agreement** |
| Kenway, Mader, He & Martins, **PAS (2019)** §5.1 — ADflow row | Jacobian-free source-transformation AD | **complex step** | **11 / 6 digits** |

PAS 2019 declines finite differences as a reference in its own words, quoted at
`docs/dafoam/PRIOR_WORK_INVENTORY.md:473`: *"the finite-difference method is subject to
subtractive and cancellation errors, which degrades the accuracy of reference
derivatives."*

> **FORBIDDEN.** Comparing this lab's vector norm against a published per-component or
> per-row average. They are different statistics. A vector norm is dominated by whichever
> component carries the squared-error mass — on A1 that is one component carrying **82.7 %**
> of it (`cases/dafoam/ladder-a/A_stepsize_study.md:53`) — and an average is not.

**One correction to the record, made here rather than silently inherited.**
`DAFOAM_CHARTER.md` §2 states PAS 2019 measured *"12 digits (ADflow)"* and that *"the
FD-Jacobian option in the same table reaches only 3–4 digits, ~0.1 % average."* The
on-disk protocol record does **not** carry either figure: its ADflow row reads **11 / 6
digits**, and the string "3-4"/"3–4" and the phrase "FD-Jacobian" as a digit count appear
**nowhere** in `DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` (191 lines, grepped). The ~0.1 %
average is real but attaches to the **C&F 2018 and AIAA J 2020** rows, not to a PAS 2019
table row. **This document uses the on-disk figures.** The discrepancy is reported to the
supervisor as a charter-text defect candidate and is **not** repaired here — a lane does
not edit a charter (`docs/charters/README.md` §4.4: contradictions get surfaced, not
resolved locally).

---

## 2. The registered band, exactly as the charter fixes it

`VERIFICATION_CHARTER.md` §7, at `:841-846`, verbatim:

- **PASS** at 5 percent or better on the aggregate **and** zero flagged components.
- **CONDITIONAL** between 5 and 15 percent, and it requires a per-component breakdown
  before it can be graded at all.
- **FAIL** above 15 percent **or** on any sign-flipped or unstable component, regardless
  of the aggregate.

`DAFOAM_CHARTER.md` §2 adopts this band for this family in the same terms. **A sign flip
is decisive: it fails the gate whatever the aggregate says.** The earlier "1 to 12 percent
is normal" band was inferred from a single rung and is **retired**
(`VERIFICATION_CHARTER.md:848-851`).

**The five-step reporting protocol, none optional** (`VERIFICATION_CHARTER.md:853-864`):

1. Confirm the step sits in the well-converged plateau with a two- or three-point
   mini-sweep. Not assumed.
2. Report per-component or cosine-similarity agreement alongside the aggregate percentage.
3. Flag any component whose FD value changes sign, or moves by more than **50 percent of
   its own magnitude across one decade of step** (`:858-860`). That is a real defect
   signature, not noise.
4. The harness-sound floor on this stack, for a case with no flagged components, is **2.5
   to 5 percent** vector-norm relative error; *"a number below that is a claim about the
   harness"* (`:861-863`). **See §3 — reading this clause wrongly is the trap.**
5. Central differences, `step_calc=abs`, step between **1e-3 and 1e-2** (`:864`).

**Table shapes** (`VERIFICATION_CHARTER.md:866-889`), pick by what is being graded:
per-derivative summary `| derivative | analytic (Jan) | FD (Jfd) | abs error | rel error |`;
per-component with an explicit sign-match column
`| idx | analytic | FD (step) | rel. err % | sign match |`; and the step sweep
`| step | rel err | rel err (excl. flagged) | cosine | status |` — **with the failed steps
as rows**, because *"a sweep that hides its failed steps is reporting a plateau it did not
measure"* (`:888-889`).

**A vocabulary conflict, disclosed and not resolved.** The FD band's own labels are
`PASS` / `CONDITIONAL` / `FAIL`. The lab's fixed verdict vocabulary is `PASS` /
`GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` (`CLAUDE.md` rule 1;
`DAFOAM_CHARTER.md` §8). `CONDITIONAL` is not in it and bare `FAIL` is not either —
`CLAUDE.md` rule 1 already records the bare-`FAIL` conflict as *"referred, unruled"*. **In
practice: the band's three labels grade the FD table; the item's verdict is written in the
six-token vocabulary, and the two are stated separately rather than one being substituted
for the other.** Ruling on whether §7's band labels should be restated in the six-token set
is the verification supervisor's and ultimately Sanaa's, not this document's.

---

## 3. The harness floor, and the trap in reading it

§7 step 4's **2.5–5 % floor is calibrated on shape derivatives through IDWarp.** A per-cell
field design variable has **no mesh warp in its chain at all**.

The evidence that it has none is a planted probe, not an argument:
`cases/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md:70` records
`WARP PROBE: {"warper_init": 0, "warper_jacvec": 0}` — *"Zero constructions, zero calls.
`warper_init: 0` is the decisive number: a class that is never [constructed]"* (`:73`).

Every S1/W4 field-inversion FD number sits **one to two orders below the floor**:

| record | cells probed | rel. err | path |
|---|---|---|---|
| W4 CBFS unblock §5d | 5491 / 6740 / 12486 | **0.085 % / 0.059 % / 0.199 %** | `cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md:319-322` |
| S1 CBFS re-inversion, Amendment 1 §C | 5363 / 5428 / 5491 | **0.032 % / 0.115 % / 0.009 %** | `cases/dafoam/ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md:201-213` |
| supervisor sweep, a cell the lab never published | one cell | **0.0211 %** | `cases/dafoam/VERIFICATION_cbfs_unblock_supervisor_sweep.md:107` |

> **The charter §2 conclusion, and it is the operative sentence:** *"The two are not the
> same instrument, and this charter records that so §7 step 4 is not read as an accusation
> against the S1 numbers."* **A DAFoam record states which instrument it is on.**

**How to state it.** One line in the FD section naming the DV class and whether the mesh
warp is in the derivative chain — and, where it is claimed absent, the warp probe's own
counters, not the claim alone. A shape-DV number at 0.03 % **is** a claim about the
harness and §7 step 4 applies to it in full; a field-DV number at 0.03 % is not, and the
probe is what separates them.

---

## 4. The step-size selection rule — mechanical, and the mechanical half is the operative half

`N-D21`, `docs/NUMERICS_KNOWLEDGE.md:3439`. Registered before any value existed; first used
on A6 N=16, 2026-08-22. **Stated here operationally so a future lane executes it without
re-deriving it.**

### 4.1 The rule

Registered at
`cases/dafoam/ladder-a/A6/rung_n16_remaining_components/PREREGISTRATION.md:154-186`:

1. **Register `η` — the noise floor — BEFORE the run, and never move it afterwards.** `η`
   is the objective's within-run peak-to-peak over a stated window: *"`η` = 1.0910e-05 —
   the within-run CD peak-to-peak over the last 200 iterations of the baseline"* (`:154`).
   The registered consequence is registered with it, so it cannot be chosen later: *"`η`
   **stays 1.0910e-05** for every clearance and every verdict in this item whatever this
   arm's own baseline measures"* (`:157`, `:339`).
2. **Derivative noise floor at step `s`** := `η / (2s)` for a central difference (`:158`).
3. **Clearance** `C(s) := |J_adj| · 2s / η`, using the **stored adjoint magnitude**
   `|J_adj|` as the proxy for the true derivative (`:159`).
4. **Fix a ladder of candidate steps per DV class, in that DV's own units, before
   computing anything.** A6 used `{3e-2, 5e-2, 1e-1, 2e-1, 3e-1}` for `twist` (degrees) and
   `{3e-2, 1e-1, 3e-1, 1e0}` for `patchV` idx0 (m s⁻¹) (`:178-179`).
5. **`s_lo` := the smallest ladder rung with predicted `C ≥ 5`.**
   **`s_hi` := the smallest ladder rung with `s_hi ≥ 2 · s_lo`.** The registered pair is
   `{s_lo, s_hi}` (`:179-181`).
6. **The graded step is the one with the higher clearance among those with `C ≥ 5`, i.e.
   `s_hi`, and it is NOT selected on agreement** (`:181-182`). This is the clause that
   makes the rule a rule rather than a preference.
7. **Plateau test, registered with the pair:** *"two steps agree if
   `|d(s_hi) − d(s_lo)| / |d(s_hi)| ≤ 10%`"* (`:236`).
8. **A component is GRADED only where `C ≥ 5` at the graded step AND the two-step plateau
   holds; otherwise it is FLAGGED and excluded by name** (`:162`, `:369`).

### 4.2 What it measured, and it is the reason to use it

`cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md` §3.1:

- **All ten registered steps cleared `C ≥ 5` on the measurement**, not merely on the proxy:
  smallest measured clearance **5.83×** (`twist` 4 at `5e-2`) against a predicted **5.75×**.
  **The proxy predicted the measurement to within 8 % on every one of the ten.**
- **Zero of the five components were flagged.** The registered falsifier — more than one
  flagged — did not fire.
- **The rule chose four different pairs across five components spanning 4.6× in `|J|`** —
  `{3e-2,1e-1}` twice, `{5e-2,1e-1}`, `{1e-1,2e-1}`, `{1e-1,3e-1}` — *"which is the point:
  a single hand-picked pair could not have cleared the floor on components spanning 4.6× in
  `|J|`."*

### 4.3 The registered LIMITATION, verbatim

From `cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md` §7 limitation 8:

> **8. The step-selection rule of §3.1 is validated on one case only, and on the easy side
> of its own assumption.** It sizes the step from `|J_adj|` — the quantity under test. Here
> the adjoint turned out to be right, so the proxy was good. **On a rung where the adjoint
> is wrong by an order of magnitude, the rule would size the step from a wrong number and
> could register steps that cannot grade.** That failure mode is unmeasured and this record
> does not claim otherwise.

**One further caution from the same record, §7.3, because it changes how a marginal
component is read:** *"clearing `C ≥ 5` makes a component gradeable; it does not make it
converged … A clearance bar is a floor, not a target, and a component sitting just above it
should be read as marginal even when its plateau passes."* Measured: `twist` idx5 read
**0.389 %** at `C = 13.87×` against **3.316 %** at `C = 6.74×` — **8.5× better at the larger
step**, the opposite of the truncation-dominated reasoning that had been registered for it.

---

## 5. The plateau rule — per component, at the graded run's own primal tolerance

`DAFOAM_CHARTER.md` §3:

> **The sweep is run at the primal tolerance the graded run uses, and the plateau is read
> per component, not off the vector. A component whose FD estimate does not stabilise
> anywhere in the sweep is flagged and excluded by name from any aggregate quoted as
> agreement — never dropped silently, and never rescued by a step at which it happens to
> cross.**

### 5.1 The A1 measurement: a vector dip is not a plateau

`cases/dafoam/ladder-a/A_stepsize_study.md` — twelve invocations on A1, 4,032 cells, np=2,
one step varying and nothing else. Full 8-vector relative error against step:

**94.95 / 52.88 / 17.64 / 12.27 / 11.52 / 11.43 / 10.47 / 8.94 / 4.28 / 9.83 %** at
1e-8 / 1e-7 / 1e-6 / 1e-5 / 1e-4 / 1e-3 / 5e-3 / 1e-2 / 2e-2 / 3e-2, and the **primal fails
to converge at 5e-2 and 1e-1** (`:14-24`, and the failed steps are rows: *"FAILED: primal
did not converge for idx6 (+step); residual stalled at 4.8e-5 vs 1e-8 tolerance"*, `:24`).

- **The 4.28 % dip at 2e-2 is not a minimum.** `:37-40`: *"It is caused entirely by one
  component (idx6) whose FD estimate is sign-flipped and unstable at every other step,
  happening to cross near [the adjoint's magnitude] … There is no step at which idx6 is a
  trustworthy estimate."* idx6 runs **−88 % to −119 %** relative across nearly the whole
  range (`:47`) and pushes the primal into outright non-convergence above ~3e-2 (`:76`).
- **Excluding idx0, idx1 and idx6 the curve is dead flat at 2.5–3.0 % from 1e-4 to 3e-2,
  cosine 0.99998** (`:41`). **That is the real plateau, and it belongs to five of eight
  components, not to the vector.**
- idx6 alone carries **82.7 %** of the squared-error norm at the original step (`:53`), and
  the same record's independent re-derivation reproduces **82.70 % vs 82.7 %**, cosine
  excluding idx0/1/6 **0.999983 vs 0.999983**, cosine including all 8 **0.993451 vs
  0.993452** (`:62-63`).

Recorded as **N-D3**, `docs/NUMERICS_KNOWLEDGE.md:2306`: *"On this stack the
finite-difference plateau is a per-component property, and the vector norm can dip where no
component supports it."*

### 5.2 The S1 incident: the step was never the problem, the primal's stopping rule was

`cases/dafoam/ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md` Amendment 1 §B (`:173-198`):

- At `primalMinResTol 1e-6` the cold primal **stops at its first tolerance crossing**
  (iterations 383–458) and central FD misses the adjoint by a systematic `fd/adj ≈ 0.7` on
  all three cells — **25.9 % / 32.0 % / 32.2 %**, zero sign flips (`:178`).
- **One pair re-run at `primalMinResTol 1e-8` moves the same cell from 25.9 % to 0.032 %**
  (`:190`). The record's own conclusion: *"The adjoint was right; the 1e-6 stop was
  polluting the FD"* (`:191`).
- The protocol change was then registered for **every** run of that item — *"the FD probes,
  the inversion's every evaluation, the final write-out"* (`:194`) — not only for the
  probes that had failed.

> **A step sweep at a loose primal tolerance defends nothing.** No step sweep would have
> diagnosed the 0.7 ratio, because the step was not the free variable. Run the sweep at the
> tolerance the graded run uses.

### 5.3 And do not prescribe "converge harder" before checking whether convergence is available

`VERIFICATION_CHARTER.md:892-898`, L-7. The DAFoam instance is A5: tightening solver
tolerances 1–2 orders and running **10× more iterations** moved the aggregate **46.64 % →
46.21 %** and made the sign flips **worse, 2 → 3** (`cases/dafoam/ladder-a/A5_ubend_internal.md`,
via `DAFOAM_CHARTER.md` §3). Iterations 1000 through 10000 produced bit-identical residuals
on the case where this was tested.

---

## 6. The FD-noise caveats — three, and each has cost this lab something

### 6.1 N-D3 — the plateau is per component; the vector norm can dip where no component supports it

`docs/NUMERICS_KNOWLEDGE.md:2306`. Figures as §5.1 above, plus two the block adds:
**registered wrong-step control on the same case: 132.75 % at 1e-8 where the graded step
reads 0.038 %**; and the loose-primal-tolerance finding — three per-cell probes at
**25.9 / 32.0 / 32.2 %** at `primalMinResTol 1e-6` against **0.032 %** at 1e-8, *"a
systematic `fd/adj ~ 0.7` that no step sweep would have diagnosed."*

### 6.2 N-D13 — a peak-to-peak from three samples is a biased noise estimator, and `printInterval` hides the bias

`docs/NUMERICS_KNOWLEDGE.md:3231`. A6 N=16's FD noise floor rested on **η = 9.00e-06** taken
from **three** central-difference samples, because `printInterval` defaults to **100**. At
`printInterval 10` — numerically inert, since `DASolver.C:124` calls
`calcAllFunctions(printToScreen_)` every iteration and the flag gates only the `Info`
output — **the same 200-iteration window reads 1.0910e-05, 21 % larger**, and the floor at
step 1e-3 moves **`4.5043e-03` → `5.4550e-03`**.

> *"The estimator cannot see excursions between samples and its bias grows as the sampling
> interval approaches the oscillation period. **Every FD noise floor computed from a DAFoam
> log at default `printInterval` carries it; the fix costs nothing.**"*
> (Measured 2026-08-22, `cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/RESULTS.md`.)

**Operational consequence for this standard: an `η` taken at default `printInterval` is a
biased `η`, and every clearance `C` computed from it is biased in the optimistic
direction.** Set `printInterval` to give the window enough samples, and say in the
pre-registration what it was set to.

### 6.3 N-D15 — solve-to-solve noise and within-run wobble are different quantities, and they differed 2.47×

`docs/NUMERICS_KNOWLEDGE.md:3250`. Two back-to-back `run_model` calls at an identical A6
N=16 design point give CD `0.03506349413916734` and `0.035065704525484256`, so
**δ_repeat = 2.2104e-06**, against a within-run 200-iteration peak-to-peak of
**1.0910e-05** — a factor of **2.47×**.

> *"**Central FD differences two SOLVES, not two points of one solve**, and a warm restart
> lands near the same limit-cycle phase. Which one is the right denominator decides whether
> a marginal component is gradeable, so it is fixed in the pre-registration before the run,
> never after (L-233)."*

**Operational consequence: the pre-registration names which quantity `η` is** — δ_repeat or
the within-run peak-to-peak — **and it is named before the run, because the choice moves
every `C` by up to 2.47× and therefore moves which components are gradeable.**

---

## 7. The trivial baseline — the discrimination test, registered before its own run

`DAFOAM_CHARTER.md` §4:

> **A finite-difference gate whose verdict is counted as evidence names its trivial
> baseline in the preregistration, before its own run. For a DAFoam FD gate that baseline
> is the same probe at a step chosen to be wrong — an order of magnitude off the registered
> one. If the wrong step also passes, the gate is not measuring what it claims and the
> verdict it produced is withdrawn.**

This instantiates `VERIFICATION_CHARTER.md` §2c for this lane, whose reach-limit 3 says
*"what counts as the trivial baseline is a judgement, not a datum"* — §4 fixes the
judgement so no DAFoam pre-registration has to re-derive it.

### 7.1 The charter's worked instance — B3, cell 5491 at h = 0.5

`cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/PREREGISTRATION.md:98-104` registered,
**before any arm ran**: cell 5491 at **h = 0.5**, ten times the registered step, with the
prediction stated as a bar — *"Central-difference truncation is O(h²), so a 10× step
predicts ~100× the 0.0854 % error before nonlinearity, i.e. **> 2 %**"* — against the real
probes' **< 1 %** bar (`:67`, `:87`). Its measured outcome is in that item's `RESULTS.md`
§5. **The baseline was registered in writing before its own run, which is the whole of the
rule.**

### 7.2 The family's live instance — curriculum D1-C′, and it clears its bar by far more

Read for this document directly from the grading artifact, not relayed:
`/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint/GRADE_20260824T171942Z_1479979.json`,
graded record `cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md`, commit `5bec45b7`.

| key in the grading JSON | value | reading |
|---|---|---|
| `vector_rel_err_graded_only` | `0.0011469250679977656` | **0.1147 %** — the graded statistic |
| `worst_rel_hi` | `0.002550876167566669` | **0.2551 %** — worst of the four graded components |
| `any_sign_flip` | `False` | zero flags |
| `trivial/component`, `trivial/step` | `shape[6]`, `1e-08` | the deliberately-wrong-step probe |
| `trivial/rel_err` | `1.1260042821409841` | **112.60 %**, shipped row |
| `trivial/sign_flip` | `True` | **and the sign is flipped** |
| `trivial/armO_patched_rel_err` | `1.126004049294347` | **112.60 %** on the patched reference too |

**These are the CONTROL's numbers and they are labelled as controls.** No number produced by
a plant carries a verdict about the item it guards; it establishes only that the instrument
could have failed.

**The ratio, stated honestly rather than flattened.** 112.60 % against 0.1147 % is a factor
of **≈ 981**. The B3 instance's registered bar was **"> 2 % against < 1 %"** — a factor of
2. **D1-C′ therefore clears its bar by far more than the charter's own worked example
does**, and the two are not one sentence: B3 registered a modest, defensible prediction and
met it; D1-C′'s baseline was crushed by three orders of magnitude, on **both** toolchain
rows. A baseline that fails on only one row would leave the other row's gate undefended.

**And the provenance stamp that makes it a SHIPPED row.** That run's ledger records
`IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663`
(`/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint/ledger.txt:13`,
printed in-process by the arm itself and reproduced in
`armCprime_20260824T171942Z_1479979.log:5`). That md5 is the **stock** IDWarp; the patched
library is `85f59e87253e0a71a813f64ca6e4c425` (`docs/dafoam/README.md:154`, which also
records that **both are 491,344 bytes** — so size is not an identity either). This is
`DAFOAM_CHARTER.md` §6 being executed rather than stated: **the hash is the identity and
the version string is not**, and the stamp is what lets a reader tell which of the two rows
they are looking at.

---

## 8. The decomposition rule — an FD reference is part of a CONFIGURATION, not a property of a case

`DAFOAM_CHARTER.md` §5:

> **A DAFoam gradient measured at np > 1 states the decomposition method and, for `simple`,
> the subdivision, in the same table as the number. A new case's first FD verification is
> run at np = 1 before any parallel figure is graded, and where both exist both are
> reported. A gradient verified at one np is a statement about that np and is never carried
> to another.**

**The A4 measurement.** Ahmed-25, 2,777 cells, one scalar FFD shape DV, patched IDWarp,
everything else held: **np=4 `scotch` 8.95 %** against **np=4 `simple` 4×1×1 0.00054 %** — a
factor of **16,600 between two decompositions of the same mesh**
(`docs/dafoam/PRIOR_WORK_INVENTORY.md:380`: np=4 scotch `2.2086e-01` / FD `2.4258e-01`;
np=4 simple `2.4220e-01` / FD `2.4220e-01`; stock equivalents 10.04 % and 0.76 %). The
effect is **np-dependent** too — np=1 0.34 %, np=2 0.26 %, **np=3 6.05 %**, np=4-scotch
8.95 % (`:136`, `:380`). The hanging-node explanation is **refuted backwards**: scotch cuts
**4 of 456** refinement-interface faces and `simple` 4×1×1 cuts **68**, and the 68-cut arm
is the clean one (`cases/dafoam/DISCRIMINATORS_A4_decomposition_mechanism.md:135-136`).
A4's published 10.04 % stood for two days as a gradient defect before the decomposition was
varied; the graded configuration is now **np=1 against the shipped toolchain, 1.10 %**
(`docs/dafoam/PRIOR_WORK_INVENTORY.md:136`).

**The carrying failure, subtler than the first.**
`cases/dafoam/W4_IDX16_IS_THE_REFERENCE.md` records that A5's stored FD reference
for component idx16 is **np=4-specific**, and A5's claimed decomposition-invariance is cited
from a run whose `PYTHONPATH` pointed at the **patched** IDWarp — so it covers the patched
gradient, not the stock one it is cited for (`docs/dafoam/PRIOR_WORK_INVENTORY.md` §1f).

**Why the papers cannot help.** *"No paper ever varies the decomposition of anything — not
at fixed np, not across np"*; "decompose", "processor" and "scotch" are **absent from the
AIAA J paper entirely** (`cases/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md:53, 57-60`).
The lab ran the papers' own C&F 2018 Table-4 acceptance check on the defect's own case at
np=1 and np=4-scotch and got **3.55 % and 3.68 %** — **it passes on both sides**. **A
single-decomposition protocol cannot see this defect even in principle**, and the
pre-registered prediction that it would was REFUTED (`DAFOAM_CHARTER.md` §5).

> **This is the sharpest thing a V column entry of "FD-vs-adjoint" has to carry: the
> family's most consequential gradient defect passes the published verification protocol.**

---

## 9. The endpoint rule — every optimisation FD-checks at its FINAL design point

`DAFOAM_CHARTER.md` §9: *"Every optimisation reports a finite-difference check of the
gradient **at its final design point**, not only at the baseline."*

**Why it is not a nicety, in the charter's own terms.** Every FD verification this lab held
before this week was measured at or near a **baseline** design. The IDWarp defect that flips
A1's idx6 and A5's idx8/idx17 is **guaranteed to fire at the undeformed baseline** —
`axisMag = 1e-15 < tol = sqrt(eps)` makes branch 0 certain at every non-corner surface node
— and its second regime behaves differently just **above** the threshold: measured error
against angle reads 1e-5 rad → 4.1e-08, 1e-6 → 6.7e-05, 5e-8 → 1.2e-02
(`cases/dafoam/ROOTCAUSE_getRotationMatrix3d.md` §1.6, §6.4, via `DAFOAM_CHARTER.md` §9).

**And now it is measured, not argued.** Curriculum **D1-C′**,
`cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md`, graded `5bec45b7`, A1 NACA0012,
np=1:

> *"On the A1 NACA0012 case at np=1, the stock IDWarp analytic `dCD/dshape` is
> **catastrophically wrong at the undeformed baseline design point** (640 % and sign-flipped
> at index 6) and **indistinguishable from the patched result at arm O's converged, deformed
> design point** (≤ 2.8e-06 relative, all four probed components, right signs). **The defect
> is design-point dependent.**"* (`:277-280`)

The baseline half is a separate prior measurement, at the undeformed point on the same case
at np=1: shipped `shape[6]` analytic `+5.69074e-03` against FD `-1.05312e-03` —
**640.3696 % with a sign flip** — while the patched row gave `-1.06564e-03`, **1.1888 %**,
right sign; and **8 of 8 raw `Jfd` components were bit-identical across the two images**, so
the FD side did not move (`cases/dafoam/ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md`
§3, §4.1–4.2, cited at `curriculum_D1_Cprime/RESULTS.md:267-272`).

**Both registered hypotheses were falsified, and the record says so.** H1 (the absolute
defect carries to the endpoint ⇒ 24.35 %) and H2 (the relative error carries ⇒ ≈ 640 % with
a sign flip) were registered as a discriminator on `shape[6]`, whose `|J|` grew **26×**
between baseline and endpoint. **Measured: `5.16e-08` absolute, `0.0527 %` relative, right
sign.** H1 is out by **1.3 × 10⁵**, H2 by **1.2 × 10⁴** — *"Neither hypothesis survives, and
the measurement is not between them — it is five orders below both"* (`:262-264`).

### 9.1 The mechanism is an UNTESTED HYPOTHESIS and is reported as one

`curriculum_D1_Cprime/RESULTS.md:279-292`, and this document repeats its framing rather than
its conclusion:

> One candidate — *"and it is a **hypothesis this run did not test**, offered only so the
> next item can be pre-registered against it"* — is that the defect lives in a degenerate
> branch of `getRotationMatrix3d`'s reverse mode reached when the local warp rotation is at
> or near zero, which is exactly the undeformed baseline and is not the deformed endpoint.
> **"That is speculation until a registered arm measures the defect against rotation
> magnitude."**

The record also names what must **not** be read as support for it: the sign-and-magnitude
pattern of the individual ~1e-8 differences sits at the **cross-run noise floor**, and
`patchV[1]` — a component that cannot carry a warp-derivative defect at all — shows a
difference of the same relative size. **The finding is a conjunction of two measurements,
not a mechanism**, and it is neither a recommendation to adopt nor to drop either stack
(R11 untouched; adoption is Sanaa's).

### 9.2 An endpoint FD reference is a property of the PATH, not only of the point

**L-229** (`docs/LESSONS.md:9334`): *"An endpoint FD-vs-adjoint error may be compared across
toolchains only when both `check_totals` were taken at the **same** design by the **same**
path (same warm state, same perturbation history). Otherwise the comparison is reported as
two separate rows and the analytic columns are compared directly."* Measured on the A4
shipped-image optimisation twin (D455): both stop at `shape = −0.05` (6 vs 9 majors, 16 vs
47 objective evaluations); their **analytic** gradients agree to **3.9e-06** relative; their
**FD references differ by 1.83e-03**, and the reported endpoint errors — **0.3112 % and
0.4936 %** — differ **entirely because of the FD column**.

**Operational consequence: an endpoint FD number is stamped with the path that reached it,
and two endpoint numbers from different optimisation histories are two rows, never a
comparison.**

---

## 10. THE HONEST LIMIT — every reference in this family is a finite difference, and that is a deficiency of this standard

**This section is not a footnote and is not to be summarised away.**

### 10.1 The reason the reference is FD, and it is measured rather than chosen

`DAFOAM_CHARTER.md` §2's second sub-point requires that *"a record that reports only an FD
table where a forward-AD or complex-step reference was reachable states that it did not
reach for it, and why."* **Here the reason is measured.**

**Forward-AD.** The images ship `libDASolverADF.so` — the `CODI_ADF` forward-AD build. It is
present, it loads, and it runs: `find / -name "libDASolverAD*.so"` inside
`dafoam-idwarp-rot:v1` returns `libDASolverADF.so` (9,534,464 B) and `…ADR.so`
(11,415,712 B), and `nm -D --defined-only libDASolverADF.so | c++filt | grep -c
DARhoSimpleCFoam` returns **28** symbols including `::solvePrimal()` and `::initSolver()`
(`cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/RESULTS.md:359-360`; the same three
libraries are listed in `cases/dafoam/patched_build/subpclu/BUILD.md:42` and gate G1 at
`:124`).

**And it does not reproduce the plain primal.** **N-D16**, `docs/NUMERICS_KNOWLEDGE.md`:
cold, same mesh and `daOptions` — momentum `finalRes` bit-identical; `he` `finalRes` diverges
at the **8th significant figure** (`0.06128002514528321` plain vs `0.06128001402295498`
ADF); the GAMG pressure solve stops at **5 sweeps instead of 7**; cumulative continuity is
**10× worse**; CD at iteration 1 is **13.5 % low**; and **every state is NaN within 10
iterations.** `libDASolverADF.so` is md5-identical
(`44538ed4ac157ecb5dbb6850cf4bde64`) across `dafoam/opt-packages:latest` and
`dafoam-idwarp-rot:v1` — **a shipped-toolchain property, measured on a patched row.**

The lane reached for it anyway, and the reach is on the record as a measurement:
`cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/RESULTS.md` §8.2 — *"Every forward-AD arm
returned `FWDAD_DERIV: nan` … **As a graded reference, forward-mode AD is NOT AVAILABLE on
A6 N=16.** That is a **measured** answer to `DAFOAM_CHARTER.md` §2, not a decline — the lane
reached for it, ran it, and found the instrument broken on this case."* Warm-started, its
per-iteration trace is finite for thirteen iterations and **converges monotonically onto the
adjoint — 11.38 → 8.04 → 4.53 → 1.55 → 0.600 %** — before the primal jumps CD from 0.0353 to
0.1039 and reaches `nan`. **That 0.600 % is reported as corroboration and is NOT used as a
graded reference**, because the registered settling test failed.

**The defect record and its class.**
`cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md`, docket **D460**
(`docs/DOCKET.md:825`), stamped **"Status: NOT FILED ANYWHERE, AND NOT FILING-READY"** in its
opening lines. Sweep 1 has since run: its 2026-08-24 addendum (`:333-395`, appended, *"lines
whose number changed above this section: 0"*) records

> **VERDICT: `PASS` — CLASS: CONDITIONING / DIAGNOSABILITY** (docket **D498**, commit
> `e8c89050`; pre-registration frozen at `538c9f51`, comparator `analyse_sweep1.py`
> sha256 `239c1764…1be7e94` hash-checked inside the grading invocation, all three planted
> controls read back live on that same invocation).

— i.e. *"the upstream ask is a documentation + warning change, not an AD fix, and the more
serious AD-correctness reading is not reached"*, **for this case, one solver, one mesh,
np = 1, ten iterations.** The addendum's own caveat travels with the class and is carried
here: the gated ratio `r = |cum_F|/|cum_P|` fell from `10.029307` to `0.968227` **mainly
because the CONTROL's own continuity error grew ×17.437**, while the forward-AD arm's grew
×1.683 — *"It is **not** 'the amplification collapsed'"*. And unchanged by sweep 1: the
8th-significant-figure `he finalRes` difference is **still present**, unchanged in every
digit. **D460 sweep 2 is UNRUN and UNAUTHORISED.**

**Complex step.** **No complex-step build is recorded anywhere on this box.** The strongest
statement the evidence supports is an absence-of-record: the in-image library probe above
returned exactly two AD libraries, forward and reverse, and no complex-arithmetic build
appears in `docs/dafoam/TOOLCHAIN_INVENTORY.md`'s image inventory (§1, §3, §6b) or in any
`cases/dafoam/` record. **This is weaker than a measurement and is labelled so: nobody has
run a probe designed to find a complex-step build and shown that probe able to see one**
(`CLAUDE.md` rule 3 — a zero from a reader not shown able to see a non-zero is not
evidence). **A lane that needs this claim to be load-bearing must plant the control first.**

### 10.2 How much resolution this family is giving up, in the papers' own units

From `cases/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` §1 (§1.1 above for the full
table): the **non-FD** references reach **10-digit agreement** (DAFoam, full-code AD) and
**11 / 6 digits** (ADflow, complex step). The **FD** references in the same corpus reach
**avg < 0.1 %, worst 0.252 %** (C&F 2018) and **avg < 0.1 %, worst 0.195 %** (AIAA J 2020)
— roughly **3 significant figures**. `:98-99` of that record states where the 0.1 % scale
comes from: *"The 0.1% scale is the FD-partials error floor (Kenway §5.1/§6 says so
directly), not a parallel-consistency scale."*

> **A non-FD reference resolves a gradient to ten or eleven digits. This family's reference
> resolves it to about three. That is roughly seven orders of resolution this V column does
> not have**, and no amount of step-sweeping recovers it, because the limit is the
> reference, not the step.

### 10.3 The shared-primal limitation — the deepest one, and it is structural

**Docket D16** (`docs/DOCKET.md:141`): *"An FD gradient and an adjoint gradient from the same
solver on the same primal **agree wherever the primal is wrong together**."* The lab knows
this and uses it decisively — `cases/dafoam/PROOF.md:917-940` (*"FD and the adjoint are, provably,
differentiating the exact same frozen-`yWall` discrete function"*, the move that refutes a
hypothesis), `cases/dafoam/W5_GRADIENT_REGRADE.md:622-631` (*"the FD cannot change between the runs"*,
retracting a control that could not have failed) — **and D16's open finding is that it is
absent from the gate lines themselves**, where the FD is called "the true derivative". D16 is
open, zero compute, and this document is one of the places its wording should reach.

### 10.4 What a V-column entry of "FD-vs-adjoint" therefore DOES and DOES NOT certify

**It DOES certify**, for the exact configuration named beside it (case, mesh, np,
decomposition, image md5, primal tolerance, design point):

- that the discrete adjoint reproduces a **numerically independent** derivative of **the
  same discrete objective the primal actually solves**, to the stated aggregate and per
  component, at a step proved to lie in a plateau;
- that no graded component's sign is wrong;
- that the instrument could have failed — the registered wrong-step baseline did fail
  (§7);
- that the number is reproducible from artifacts still on disk.

**It DOES NOT certify:**

1. **That the discretisation is right.** FD and adjoint differentiate the *same* discrete
   function. Both are wrong together wherever the discretisation is wrong (§10.3, D16).
   **This is a code-verification statement about the derivative, not about the solver.**
2. **Anything to better than ~3 significant figures.** The reference itself carries a
   ~0.1 % floor (§10.2). A 0.03 % agreement on a shape DV is a claim about the harness
   (§3), not a tighter certificate.
3. **Anything at a decomposition, np, image, primal tolerance or design point other than
   the one measured.** §5.2, §8 and §9 each contain a measured instance of the same
   number moving by orders of magnitude when one of these changed.
4. **Anything about a flagged component.** A flagged component has **no reference at all** —
   *"not a bad one, a missing one"*
   (`ladder-a/A6/rung_n16_remaining_components/RESULTS.md` §7 limitation 1). An aggregate
   over graded components is silent about it.
5. **Anything about components not in the table.** `shape` (~10² components) is still not
   graded by any pre-registration in this family; *"a nine-component table is not the whole
   gradient"* (same record, §7 limitation 2).
6. **That the toolchain the number belongs to is the one that ships.** That requires the
   two-row discipline and the md5 stamp (§7.2, `DAFOAM_CHARTER.md` §6).

> **The honest one-line summary for a coverage matrix cell:** *V = FD-vs-adjoint gradient
> check, configuration-scoped, ~3-significant-figure reference, shared-primal — no exact or
> manufactured solution exists for this quantity, and the family's preferred non-FD
> references are measured unavailable on this box (D460/D498) or unrecorded (complex step).*

---

## 11. What is forbidden

Carried verbatim from `DAFOAM_CHARTER.md` §2 and §3, and from `VERIFICATION_CHARTER.md` §7.

**From §2 — "What is forbidden."** *Quoting an adjoint gradient with no FD table. Reporting
an aggregate with the flagged components dropped and not saying so. Comparing this lab's
vector norm against a published per-component average. Calling a `PetscConvergedReason: 2` a
verified gradient.*

**From §3 — "What is forbidden."** *Quoting an FD number from a single step. Reporting an
aggregate computed with unstable components silently removed. Selecting the step after
seeing which one agrees.*

**From §5 — "What is forbidden."** *A parallel gradient table with no decomposition column.
Carrying an FD reference across np. Describing a case as decomposition-invariant from one
arm.*

**From §9 — "What is forbidden."** *Grading an optimisation from the size of its
improvement. Reporting a design change as validated without an FD check at the design point
that produced it. Using the word converged of a run whose optimiser printed no convergence
statement.*

**From `VERIFICATION_CHARTER.md` §7 (`:888-889`).** A sweep that hides its failed steps is
reporting a plateau it did not measure — **the failed steps are rows.**

**One reason `PetscConvergedReason: 2` is on that list, stated so it is not read as
pedantry.** A4's scotch arm converged at true-residual **1.7e-07** on an operator that is
**328.8× ‖b‖** away from the transpose Jacobian (`DAFOAM_CHARTER.md` §1;
`docs/dafoam/PRIOR_WORK_INVENTORY.md` §1e). **The KSP converged. The derivative was
wrong.**

---

## 12. Enforcement, honestly

**Written from what exists, not from intent.** `DAFOAM_CHARTER.md` §13's own table is the
source, and it is repeated here rather than improved on, because a standard that claims
enforcement it does not have is worse than one that admits the gap.

| clause of this standard | what checks it today |
|---|---|
| §1 the statistic is named | **NOTHING.** §13's row for `DAFOAM_CHARTER.md` §2 reads *"Nothing. The vector-norm-versus-per-component confusion is caught only by reading. **Proposed, not built.**"* |
| §2 an FD table is present at all | **NOTHING AUTOMATIC.** §13: *"`VERIFICATION_CHARTER.md` §7 states the band; a reviewer checks the table is present. A grep for an `FD` heading in `cases/dafoam/**/RESULTS.md` would catch an omission and does not exist."* |
| §3 which instrument (warp / no warp) | **NOTHING.** Not in §13's table at all; the warp probe exists in one record and is not required anywhere. |
| §4 mechanical step rule | **NOTHING.** N-D21 records the rule; no check requires it. §13's §3 row: *"Partly — `ladder-a/A_stepsize_study.{md,json}` is the worked instance and `analyse_fd.py`-class helpers recompute it, but no check requires a sweep before a graded FD number."* |
| §5 plateau read per component | **PARTLY**, as above — the helpers recompute, nothing gates. |
| §6 noise caveats | **NOTHING.** `printInterval` and the η-denominator choice are honoured by hand. |
| §7 trivial baseline | `scripts/check_row_discrimination.py` (rules `D1-HOLLOW-PASS`, `D2-INERT-ROW`, `D3-GUARD-GRADED`) is the closure lane's instrument. §13: *"**It has never been run against `cases/dafoam/`**, and whether its row schema fits this tree is unmeasured."* |
| §8 decomposition disclosed | **NOTHING.** §13: *"A column-presence check on parallel gradient tables is buildable and does not exist."* |
| §9 endpoint FD check | **NOTHING.** §13's §9 row: *"A check that an optimisation record carries a convergence statement or the token `GATE REACHED` is buildable; the A2 case was caught by reading a JSON field that a human had filled in honestly."* |
| §10 the honest limit is stated | **NOTHING.** It is a duty on the writer. |
| the two-row shipped/patched requirement | **PARTLY** — `patched_build/*/BUILD.md` gates G2a–G2d are real, reproducible and were run. §13: *"Nothing enforces that a *record* carries both rows."* |

**PROPOSED, NOT BUILT — and deliberately not built by this document.** A `scripts/`-level
checker could, at zero compute, grep `cases/dafoam/**/RESULTS.md` for (a) an FD-table
heading, (b) the literal statistic string `‖J_an − J_fd‖ / ‖J_fd‖` or an equivalent naming
line, (c) a decomposition column wherever `np` > 1 appears, and (d) an
`IDWARP_SO_MD5`/image-id stamp. **It does not exist, nothing in this document creates it,
and no claim anywhere here should be read as implying that it does.** Building it is a
separate, costed item for the supervisor to register; note also that §13's own row for §11
records that `scripts/check_filing.py` *"says nothing about lesson or numerics numbering"*,
so the existing checker is not the place to bolt this on without a decision.

**And the layer below, which `DAFOAM_CHARTER.md` §13's 2026-08-22 note raised and left
unratified:** *"Nothing audits a pre-registration's own registered thresholds"* — a
pre-registration can invent a guard no existing check covers, as A3 rung 2 did (a registered
8 GiB host-memory floor, a record-only watcher, nothing connecting them, breached for
**52.6 %** of the graded arm by the arm's own container, **no stop fired**; L-239, D462).
**That proposal is not ratified and this document does not ratify it.**

---

## 13. THE V-COLUMN CHECKLIST — the gate template D15 promises

**Copy this block into a pre-registration and answer every numbered item in writing, before
first compute.** An item answered "n/a" states why. **This template registers nothing new:
every threshold in it is quoted from a charter that already owns it.**

```
V-COLUMN CHECK (FD-vs-adjoint) — <case>, <rung/item>
Standard: docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md
Governing: VERIFICATION_CHARTER.md §7 (:841-846, :853-864); DAFOAM_CHARTER.md §2-§5, §9

 1. STATISTIC. The aggregate is the vector-relative error ||J_an - J_fd|| / ||J_fd|| as
    printed, named as a statistic in the record. It is NEVER compared against a published
    per-component or per-row average (DAFOAM_CHARTER.md §2; no method paper uses a vector
    norm). Per-component flags are reported BESIDE it, never instead of it.

 2. BAND (registered, not chosen): PASS <= 5 % aggregate AND zero flagged components;
    CONDITIONAL 5-15 % and only with a per-component breakdown; FAIL > 15 % OR on any
    sign-flipped or unstable component regardless of the aggregate. A component is flagged
    if its FD value changes sign, or moves by > 50 % of its own magnitude across one decade
    of step. The item's own verdict is written in the six-token vocabulary separately.

 3. INSTRUMENT. State whether the DV chain contains a mesh warp. Shape DV through IDWarp:
    the 2.5-5 % vector-norm harness floor of §7 step 4 applies, and a number below it is a
    claim about the harness. Per-cell field DV: it does not, and the claim is evidenced by
    the warp probe's own counters (warper_init / warper_jacvec), not asserted.

 4. NOISE FLOOR eta. Registered BEFORE the run, with:
      - which quantity it is: within-run peak-to-peak over a stated window, or solve-to-
        solve delta_repeat. They differed 2.47x on A6 N=16 (N-D15). Central FD differences
        two SOLVES, not two points of one solve.
      - the printInterval it was measured at. Default 100 gives a biased three-sample
        peak-to-peak; printInterval 10 read 21 % larger on the same window (N-D13).
      - the registered consequence, so it cannot move later: eta stays at the registered
        value for every clearance and every verdict in this item, whatever a later arm
        measures.

 5. STEP SELECTION — mechanical, from |J_adj| and eta and from NOTHING ELSE (N-D21):
      - fix a ladder of candidate steps per DV class, in that DV's own units, in writing;
      - derivative noise floor at step s := eta / (2s)  (central difference);
      - clearance  C(s) := |J_adj| * 2s / eta ;
      - s_lo := smallest ladder rung with predicted C >= 5 ;
      - s_hi := smallest ladder rung with s_hi >= 2 * s_lo ;
      - registered pair {s_lo, s_hi}; GRADED STEP = the higher-clearance one, i.e. s_hi,
        and it is NOT selected on agreement;
      - plateau test: two steps agree if |d(s_hi) - d(s_lo)| / |d(s_hi)| <= 10 % ;
      - a component is GRADED only where C >= 5 at the graded step AND the plateau holds;
        otherwise FLAGGED and excluded BY NAME from any aggregate quoted as agreement.
      - A clearance bar is a floor, not a target: a component just above C = 5 is read as
        marginal even when its plateau passes.

    D15's REGISTERED LIMITATION, carried verbatim as the curriculum row requires
    (cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md §7 limitation 8):

      "8. The step-selection rule of §3.1 is validated on one case only, and on the easy
       side of its own assumption. It sizes the step from |J_adj| - the quantity under
       test. Here the adjoint turned out to be right, so the proxy was good. On a rung
       where the adjoint is wrong by an order of magnitude, the rule would size the step
       from a wrong number and could register steps that cannot grade. That failure mode
       is unmeasured and this record does not claim otherwise."

 6. PLATEAU / SWEEP. The sweep runs at THE PRIMAL TOLERANCE THE GRADED RUN USES, and the
    plateau is read PER COMPONENT, not off the vector. Failed steps are ROWS, not omissions:
      | step | rel err | rel err (excl. flagged) | cosine | status |
    A vector-norm dip is not a plateau (A1: 4.28 % at 2e-2 was one unstable component
    crossing; the real plateau was 2.5-3.0 %, cosine 0.99998, on five of eight components).
    A loose primal tolerance, not the step, can own the disagreement (S1: 25.9 % at
    primalMinResTol 1e-6 -> 0.032 % at 1e-8 on the same cell).

 7. TRIVIAL BASELINE (DAFOAM_CHARTER.md §4; VERIFICATION_CHARTER.md §2c). Named in THIS
    pre-registration, BEFORE its own run: the same probe at a deliberately wrong step, an
    order of magnitude or more off the registered one, with its predicted failure stated as
    a bar. If the wrong step also passes, the gate is not measuring what it claims and the
    verdict it produced is WITHDRAWN. Its numbers are labelled CONTROLS and carry no
    verdict about the item. Where two toolchain rows exist, the baseline is checked on both.

 8. DECOMPOSITION DISCLOSURE (DAFOAM_CHARTER.md §5). Every gradient table states np, the
    decomposition METHOD, and for `simple` the SUBDIVISION, in the same table as the number.
    First FD verification of a new case is at np = 1. An FD reference is part of a
    CONFIGURATION and is NEVER carried across np, across decomposition, or across image.
    (A4: 16,600x between two decompositions of the same mesh.)

 9. ENDPOINT CHECK (DAFOAM_CHARTER.md §9). Every optimisation reports an FD check at its
    FINAL design point, not only at the baseline. The endpoint FD reference is stamped with
    the PATH that reached it; two endpoint numbers from different optimisation histories are
    two rows, never a comparison (L-229). Measured reason this is not a nicety: the stock
    IDWarp warpDeriv defect is DESIGN-POINT DEPENDENT - 640 % and sign-flipped at the
    undeformed baseline, <= 2.80e-06 relative at the converged point (D1-C', 5bec45b7); the
    proposed mechanism is an UNTESTED HYPOTHESIS and is reported as one.

10. TWO ROWS - SHIPPED AND PATCHED (DAFOAM_CHARTER.md §6). Every verdict is two rows, one
    against the shipped toolchain and one against whatever was patched; a patched row never
    replaces a shipped row. Identity is an image tag AND image ID, plus the md5 of the
    patched source or built .so - a version string is NOT an identity (IDWarp reads 2.6.2
    either way while the reverse-mode derivative moves seven orders). Print the provenance
    stamp in-process from the arm itself (IDWARP_IMPORTED_FROM: / IDWARP_SO_MD5:) and quote
    it in the record: stock libidwarp.so f0fcb488e0e98156575cd19548e91663, patched
    85f59e87253e0a71a813f64ca6e4c425 - same byte size, so size is not an identity either.

11. NON-FD REFERENCE - REACH FOR IT, AND SAY WHAT HAPPENED (DAFOAM_CHARTER.md §2). Where a
    forward-AD or complex-step reference was reachable and only an FD table is reported, the
    record states that it did not reach for it, AND WHY. On this box the answer is measured,
    not assumed: forward AD (libDASolverADF.so) ships and loads but does not reproduce the
    plain primal and returns nan (N-D16; D460, class CONDITIONING / DIAGNOSABILITY per
    D498); no complex-step build is recorded anywhere, and that is an absence-of-record, not
    a measurement. Re-state, do not inherit: if a later item reaches successfully, the
    non-FD reference becomes the reference.

12. WHAT THIS ENTRY DOES NOT CERTIFY - stated in the record, not left to the reader:
    the discretisation (FD and adjoint share the primal and are wrong together where it is
    wrong, D16); anything beyond ~3 significant figures (the FD reference's own floor);
    anything at another np / decomposition / image / primal tolerance / design point;
    anything about a flagged component (it has NO reference, not a bad one); anything about
    components absent from the table.

13. ENFORCEMENT, STATED HONESTLY. Nothing automatic checks items 1, 3, 4, 5, 8, 9, 10, 11
    or 12 (DAFOAM_CHARTER.md §13). This checklist is honoured by the writer and audited by
    the supervisor's personal read. Do not describe it as enforced.
```

---

## 14. Numbers in the commissioning brief that this document could NOT verify as stated

Recorded here because a brief is evidence, not authority.

1. **PAS 2019 "12 digits (ADflow)" and "3–4 digits, ~0.1 % average" for the FD-Jacobian
   option.** `cases/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` (191 lines) records
   **11 / 6 digits** for the ADflow complex-step row and carries no "3–4 digits" figure and
   no FD-Jacobian digit count anywhere; its <0.1 % averages attach to the C&F 2018 and
   AIAA J 2020 rows. **§1.1 and §10.2 above use the on-disk figures.** The charter text at
   `DAFOAM_CHARTER.md` §2 carries the unverified wording and is **not** edited by this
   document.
2. **`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6a as the citation for `libDASolverADF.so`
   shipping in all three tags.** The string `libDASolverADF` does **not** appear anywhere in
   that file, and §6a is *"(a) Core package versions — all three images"*. The shipping
   claim **is** supported, by `cases/dafoam/patched_build/subpclu/BUILD.md:42` and gate
   **G1** at `:124` (three libraries relink, sizes given) and by the in-image `find` at
   `cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/RESULTS.md:359`. **§10.1 cites those
   instead.**
3. **"No complex-step build exists on this box."** Downgraded in §10.1 to an
   absence-of-record with the reason stated: no planted control has been shown able to see a
   complex-step build, so `CLAUDE.md` rule 3 forbids treating the zero as evidence.
4. **`docs/COVERAGE_MATRIX.md` and the V-column definition.** The file does not exist and a
   repo-wide grep of `docs/` for "coverage matrix" / "V column" / "V-column" /
   "manufactured solution" returns zero hits. Disclosed in the front matter.
5. **The trivial baseline "an order of magnitude off the registered one."** That is the
   charter's wording and B3 honoured it exactly (h = 0.5 against a registered 0.05). D1-C′'s
   baseline probe is at `1e-08` against a registered `1e-3` — **five** orders off, not one.
   §7.2 states the actual step rather than the charter's typical case.

**Everything else cited in this document was re-read from the artifact named beside it while
it was written.**

---

## 15. Artifact index

| what | path |
|---|---|
| the band, five-step protocol, table shapes, harness floor | `docs/charters/VERIFICATION_CHARTER.md` §7, `:833-898` |
| this family's instantiation; the statistic; the forbidden lists; enforcement table | `docs/charters/DAFOAM_CHARTER.md` §2, §3, §4, §5, §6, §9, §13 |
| operational half of the FD protocol | `cases/dafoam/FAMILY_SUPERVISION_GUIDELINES.md` §4.2–4.3, §8 |
| the method-paper protocol survey | `cases/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` §1–§3 |
| the mechanical step rule, as registered | `cases/dafoam/ladder-a/A6/rung_n16_remaining_components/PREREGISTRATION.md` §4.1–4.3 |
| the mechanical step rule, as scored, and its limitation 8 | `cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md` §3.1, §4.2, §7 |
| forward-AD reachability, reached and NOT AVAILABLE | `cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/RESULTS.md` §4, §8.2 |
| the step sweep and the per-component plateau | `cases/dafoam/ladder-a/A_stepsize_study.md` (+ `.json`) |
| the primal-tolerance incident and the re-verified cells | `cases/dafoam/ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md` Amendment 1 §B, §C |
| field-DV FD numbers below the harness floor | `cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §5d; `cases/dafoam/VERIFICATION_cbfs_unblock_supervisor_sweep.md` |
| the warp probe (no warp in a field-DV chain) | `cases/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md` §1 |
| the registered trivial baseline, charter's worked instance | `cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/PREREGISTRATION.md` §"The Charter-2c trivial baseline" |
| the endpoint check and the design-point-dependent defect | `cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md` (graded `5bec45b7`) |
| the undeformed-baseline 640 % measurement | `cases/dafoam/ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` §3, §4.1–4.2 |
| the D1-C′ grading artifact (controls, stamps) | `/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint/GRADE_20260824T171942Z_1479979.json`; `…/ledger.txt` |
| the decomposition mechanism | `cases/dafoam/DISCRIMINATORS_A4_decomposition_mechanism.md`; `docs/dafoam/PRIOR_WORK_INVENTORY.md` §1e, §1f, §5.4 |
| the ADF non-reproduction defect and its class | `cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md` (D460; addendum 2026-08-24 = D498); `cases/dafoam/d460_sweep1_solver_family/` |
| numerics facts | `docs/NUMERICS_KNOWLEDGE.md` N-D3 (`:2306`), N-D13 (`:3231`), N-D15 (`:3250`), N-D16, N-D21 (`:3439`) |
| lessons | `docs/LESSONS.md` L-229 (`:9334`) |
| docket | `docs/DOCKET.md` D16 (`:141`), D460 (`:825`), D455 (`:820`); D498 landed at `e8c89050` |
| the curriculum row this document discharges | `cases/dafoam/EXPERTISE_CURRICULUM.md:126` (D15), §7 ratification and execution ledger |
| image identities and patch hashes | `docs/dafoam/TOOLCHAIN_INVENTORY.md` §1, §3, §4; `docs/dafoam/README.md:154`; `cases/dafoam/patched_build/subpclu/BUILD.md` §4.2–4.3 |

---

## 16. Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-24 | First issue, by the dafoam lane under the dafoam-supervisor, as the deliverable of curriculum item **D15**. Records the family's V-column standard: the statistic (§1), the registered band (§2), the harness floor and the instrument trap (§3), the mechanical step rule and its verbatim limitation (§4), the plateau rule (§5), the three FD-noise caveats (§6), the trivial baseline with B3's registered instance and D1-C′'s measured one (§7), the decomposition rule (§8), the endpoint rule and the design-point-dependent `warpDeriv` finding reported as the untested hypothesis it is (§9), **the honest limit in its own section (§10)**, the forbidden lists (§11), enforcement stated as the gap it is (§12), and the copy-pasteable V-COLUMN CHECKLIST (§13). Creates no gate, threshold or cap; edits no frozen record; nothing filed or sent. Five figures in the commissioning brief could not be verified as stated and are listed with their on-disk replacements in §14. Zero compute. |

**Dated addenda only.** This file is cited by line from the checklist onward; a departure is
disclosed as a dated addendum appended at the foot with the assertion `lines whose number
changed above this section: 0` (`CLAUDE.md` rule 6).

---

## 17. AMENDMENT 2 — 2026-08-25 — five checklist items the D4 endpoint FD bought, and one of them is the hole §13 had

**Lines whose number changed above this section: 0.** Version **1.1**. This is a dated addendum
appended at the foot, as §16 requires (`CLAUDE.md` rule 6). §13's items 1–13 are **unchanged in
wording, numbering and line position**; items 14–18 below **continue** that block and are copied
into a pre-registration beside it.

**This amendment creates NO gate, NO threshold, NO band and NO cap.** Every item below is a
**disclosure or a control**, never a scoring rule. Retiring or moving a threshold is Sanaa's
alone. Nothing here is filed, sent, uploaded or posted.

### 17.0 What bought these — and item 14 is the one that matters

**Curriculum D4's endpoint FD, arm F, 2026-08-25.** The frozen extractor read the optimum's
design point out of `OptView.hst`, which holds **driver-scaled** values because OpenMDAO's
`pyOptSparseDriver` applies each DV's `scaler` **before pyOptSparse sees the problem** — so
pyOptSparse's own scale factor is 1.0, its `scale` flag is a **no-op**, and the extractor's
`getValues(..., scale=False)` argument is **inert**. The FD producer then applied those values as
**physical** through `prob.set_val`. `shape`'s registered scaler is **10.0**, so arm F set the
wing to ten times its optimised deformation and destroyed the mesh: 2,989 non-orthogonality
errors, `AnalysisError: Mesh quality error!`, 15 wall s. That is **`D4-DEF-4`**.

**The sentence this amendment exists for:**

> **Had `shape`'s scaler been 1.0, every primal would have converged and arm F would have
> produced a complete, well-formed, plausible FD table AT A DESIGN POINT THAT IS NOT THE
> OPTIMUM.** Five components requested, five returned, in the registered order; every count
> refusal passing; the planted-zero control seeing its plant; the blind reader refused; all four
> mutation controls raising their named refusals. **THE FULLY ARMED INSTRUMENT SET WOULD HAVE
> CERTIFIED IT.**

**A units error is invisible to every count-based, plant-based and order-based control in this
family. They check THAT n components were measured. THEY NEVER CHECK WHERE.** §13 as issued has
no item that establishes the design point's location, and item 9 — the endpoint rule — stamps the
endpoint with its **path** without ever asking whether the point is in the right **units**.
**Item 14 closes that.**

### 17.1 The five items — copy them into the pre-registration beside §13's block

```
V-COLUMN CHECK — ADDENDUM (2026-08-25).  Items 14-18 continue the block in §13.

14. THE ENDPOINT LOCUS - a control that establishes WHERE the design point is, not only
    THAT n components were measured.  MANDATORY on any item that re-applies a design
    vector it did not itself set.  Count-, plant- and order-based controls are NECESSARY
    AND DEMONSTRABLY NOT SUFFICIENT (D4-DEF-4, §17.0).  Two controls, and each must be
    shown able to REFUSE:

      (a) THE PINNED WITNESS.  A DV component whose registered `lower` EQUALS its
          registered `upper` cannot be moved by any optimiser: its physical value is
          DEFINITIONAL.  Assert every such component equals its pinned value.
          - the control DISCOVERS pinned components by scanning the registration; it is
            never TOLD where to look, or it only checks the case its author imagined;
          - it REFUSES IF IT FINDS NONE.  A control with nothing to check is not a
            control (L-302).  An item with no pinned DV states that, and says what stands
            in for the witness.
          - D4 measured: patchV[0] pinned at U0 = 100.0 read back as 10.0 - exactly
            100.0 x 0.1, the registered scaler, to all digits.  No second explanation
            exists for a variable that cannot move.

      (b) BOUNDS CONTAINMENT.  Assert EVERY reconstructed component lies inside its
          registered bounds.  IPOPT does not violate bound constraints, so a component
          outside its bounds is a units or indexing error and NOT an optimum.
          - D4 measured: 63 of 105 components outside their registered bounds before the
            repair (62 shape + 1 patchV), 0 of 105 after.

    Both controls run in the PRODUCER, before any core-minute is spent, AND are re-asserted
    at grading time against the artifact ON DISK.  Neither may be satisfied by a value the
    producer merely asserts.

15. UNITS AND SCALING DECLARATION - on every path that reads design variables out of an
    optimiser history and re-applies them.  State the framework's scaling convention and
    PROVE IT; do not trust an argument to mean what it reads like.
      - THE DISCRIMINATOR IS THE SOURCE OF THE VECTOR, NOT THE set_val call.
        prob.get_val(...) returns the MODEL value and is PHYSICAL.  History.getValues(...)
        on OptView.hst returns DRIVER-SCALED values.  A round trip through get_val is safe;
        a round trip through the history is the defect.
      - The proof is a MEASUREMENT in the registered container, not a reading of the
        docstring: print getValues(scale=True) beside getValues(scale=False), and print
        getDVInfo()'s bounds.  D4 measured them IDENTICAL, with getDVInfo() bounds already
        multiplied by the scalers and pyOptSparse's own `scale` = 1.0 for every DV.
      - Any divisor applied to correct the units is PARSED FROM THE REGISTERING SOURCE, never
        typed into the reader.  A typed constant can drift from the registration and
        reintroduces the defect somewhere new.  MEASURED INSTANCE, not hypothetical:
        sdk/scripts/build_a2_shape_frames.py already de-scales OptView.hst correctly - by a
        typed SCALER_SHAPE that nothing checks against the registration.  It is right today
        and right BY LUCK.
      - The published artifact carries an explicit units field, and every consumer REFUSES
        an artifact that does not declare the units it expects.

16. EVERY GATE'S REFUSAL IS MADE TO FIRE IN THE SELFTEST.  For each gate the
    pre-registration emits, the selftest carries at least one unit in which THAT GATE'S
    REFUSAL ACTUALLY FIRES, driven by a deliberate mutant, and the battery is shown able to
    FAIL.  A unit that REFERENCES a control without making it LOAD-BEARING does not test it,
    however many units there are.
      - THE MECHANISM IS ALWAYS THE SAME: READING THE CODE CONFIRMS THE GUARD AND STOPS
        THERE.  Three independent instances in one day:
          D4-DEF-1        21 selftest units that NEVER mutated the FD table, so the bright
                          line itself had no end-to-end unit behind it;
          M3 (D12)        deleting the sign-flip override ENTIRELY left the whole selftest
                          passing, because the only unit referencing it was not load-bearing
                          there;
          D7-GRADER-DEF-2/3  the crash class inside g6_plant - the gate its own addendum
                          called "defended" - and g11_oom returning pass=True FOR A
                          CONTAINER THAT NEVER RAN.  A gate that certifies absence as
                          success.
      - "21/21" and "48/48" have both been true of unit sets that omitted the gate that
        mattered.  A selftest count is not evidence about coverage; the mutant is.
      - This subsumes the planted-zero control (CLAUDE.md rule 3): the plant must be shown
        to MOVE the graded quantity ACROSS the band, and a blind reader that ignores its
        path must be REFUSED.

17. COST BASIS - EVERY TERM CARRIES A NUMBER, OR THE BASIS IS LABELLED PARTIAL.  A basis
    reading "X + Y" where only X has a figure has NOT priced Y, and must say so.
      - MEASURED: D7's arm P2 came in at ratio 1.915 - predicted 31.5, actual 60.334
        core-min.  Its basis read "+ coloring build" with NO NUMBER BESIDE IT, and setup +
        primals + colouring consumed 682 of 901 s.  THE ONLY TERM ACTUALLY PRICED - the
        adjoint - was about right.  THE UNPRICED TERM WAS ESSENTIALLY THE ENTIRE OVERRUN.
        That is a PRICING DEFECT, not a mis-estimate.
      - The prediction carries a numeric STOP THRESHOLD, and an overrun STOPS THE RUN; it
        does not get a new budget (CLAUDE.md rule 12).
      - At completion the actual/predicted ratio is stated in core-minutes from logs, the
        gap is ATTRIBUTED (contention / waste / misprediction / instrument defect), waste is
        named SEPARATELY and never absorbed into the ratio, dollars are labelled DERIVED,
        and a row lands in docs/COST_CALIBRATION.md.
      - An arm that DELIVERED NO WORK gets NO RATIO.  A ratio compares work done against
        work predicted for it, and there is nothing to compare (precedent c21ada18).

18. STAGED-TREE COLD START - a tree copied from another arm inherits that arm's OUTPUTS.
    State, per staged arm, that it satisfies the same cold-start standard the launcher
    enforces on a fresh arm - no pre-existing answer file, no inherited output time
    directory, no inherited reports/ - or state the exemption AND why it is safe.
      - MEASURED (D4-DEF-6): `cp -a O F2` carried arm O's 84 pseudo-time directories
        0.0001..0.0082 into the staged tree.  DASolver.renameSolution counts from 1, so the
        FIRST rename collided: "processor1/0.0001 already exists, moving failed!", and the
        arm died in compute_totals AFTER both primals had converged correctly.
      - THE DEFECT WAS INHERITED FROM THE ORIGINAL STAGER, SO THE ARM COULD NEVER HAVE
        COMPLETED EVEN WITH CORRECT UNITS.  The earlier units crash masked it.  TWO
        INDEPENDENT BLOCKERS ON ONE ARM: fixing only the first buys a second crash at a
        higher price.  This is the case FOR making a SOLVE, not an argument, the
        precondition of any freeze.
      - The staging repair removes OUTPUTS from the COPY only, asserts the count removed is
        NON-ZERO (a repair that removes nothing is a no-op wearing the costume of one),
        asserts the INPUTS survive, and asserts the SOURCE tree is unharmed AFTER the
        removal rather than assuming it.

19. ENFORCEMENT, RESTATED.  Nothing automatic checks items 14-18 either, with one
    exception: item 14's two controls ARE executable and DO refuse - the reference
    implementation is cases/dafoam/ladder-a/A2/curriculum_D4/d4_endpoint_locus.py, whose
    selftest builds deliberate mutants and requires each control to fire (22/22 at
    e63df1845771c3e67457443918f5b82e).  It parses the registering runScript with `ast` and
    hard-codes no design-variable name, so another item adopts it by pointing it at its own
    runScript.  TESTED, NOT CLAIMED: pointed at curriculum D7's d7_opt_runScript.py with
    zero code changes it read U0 = 291.6, DISCOVERED patchV[0] as the pinned witness, and
    REFUSED a driver-scaled vector at 29.16.  Items 15-18 are honoured by the writer and
    audited by the supervisor's personal read.  Do not describe them as enforced.
```

### 17.2 What this amendment does NOT establish

1. **It does not make item 14 general beyond a bounded DV registration.** The reference
   implementation reads `add_design_var(name, lower=, upper=, scaler=)`. An item whose DVs are
   registered another way, or whose scaler is a variable rather than a literal, gets a
   **refusal** from the parser rather than a silent half-application — which is the safe
   direction, but it is **not coverage**, and it is stated rather than implied.
2. **It does not claim a pinned DV always exists.** D4 and D7 both have one because `patchV`
   pins the freestream. **An item with no pinned component has no unforgeable witness**, and
   item 14 requires it to say so instead of quietly checking nothing.
3. **Item 15's proof is a measurement of ONE framework version.** OpenMDAO/pyOptSparse could
   change where the scaler is applied. The requirement is therefore to **re-measure per item**,
   not to inherit D4's reading.
4. **Nothing here was bought with new compute.** The measurements cited are D4's arms ACC, F2
   and F3, D7's P2, and the D12/D7 grader findings, all already spent.

### 17.3 Amendment record, continued

| Version | Date | Change |
|---|---|---|
| **1.1** | **2026-08-25** | **AMENDMENT 2**, by the D4-DEF-4 repair lane. Adds §17: checklist items **14–18** continuing §13's block, plus item 19 restating enforcement. **14** — the endpoint locus (pinned witness + bounds containment), which closes the hole D4-DEF-4 fell through: §13 as issued had no item establishing WHERE a design point is. **15** — the units/scaling declaration, with the source-of-the-vector discriminator and the measured `build_a2_shape_frames.py` typed-constant instance. **16** — every gate's refusal made to fire by a deliberate mutant, from three independent instances in one day. **17** — every cost-basis term carries a number or the basis is PARTIAL (D7 P2, ratio 1.915). **18** — staged-tree cold start (D4-DEF-6). **Creates no gate, threshold, band or cap; edits no frozen record; zero compute; nothing filed or sent.** Lines whose number changed above §17: **0**. |
