# F6a / C-15 — NASA wall-mounted hump vs Greenblatt et al. Table 2 — PRE-REGISTRATION **DRAFT**

## ⚠ THIS DOCUMENT IS A DRAFT. IT IS NOT FROZEN. IT AUTHORISES NO COMPUTE.

**Status: `PENDING` — drafted 2026-08-25 by a cfd `lab-lane` at the cfd supervisor's
direction, under a dispatch whose first line reads "ZERO COMPUTE in this dispatch: no
solver, no mesher, no case directory. You DRAFT; you do not freeze and you do not
run."**

* **No gate in this document is frozen.** Nothing here has been committed as a
  `CLAUDE.md` rule-2 freeze, and nothing here may be graded against.
* **No solver may be launched on the strength of this file.** The freeze condition is
  in §9 and is unmet by construction: this file has not been frozen, so §9's `test -e`
  has never been evaluated in a launching invocation.
* **The filename carries `_DRAFT` deliberately.** cfd's own coverage survey enumerates
  `*PREREGISTRATION*` across the tree and counts what it finds as frozen
  pre-registrations (`MATRIX_CONTRIBUTION.md` §3, C-31's cell). A draft named like a
  freeze would be miscounted by that enumeration. **On freeze, this file is renamed to
  `F6a_GREENBLATT_PREREGISTRATION.md` and the rename is the freeze event's own
  signal.**
* **The supervisor rules on this draft before anything is frozen.** Zero compute has
  been spent producing it.

---

## 0. What this pre-registration is for, and the one thing it must not be read as claiming

**cfd's `P` column is 0 green across 82 rows** (`MATRIX_CONTRIBUTION.md` §7.2, §9.2).
Under the coverage matrix owner's **Ruling 4**, `P` is green only for a comparison
against **measured physical reality — an experiment or measured data — from a public
primary source, with the pre-registration on disk**. This document is the
pre-registration that, once frozen and once its solve runs, supplies all three.

**And it is written expecting to FAIL its own physics gate.** §10 states the forecast
numerically, in advance. **The `P` column goes GREEN on the source and the frozen
pre-registration; the VERDICT will most likely be `GATE FAIL` and the TIER
`NOT HELD`.** Those are three different statements about three different things and
this document keeps them apart throughout:

| vocabulary | values | what it describes |
|---|---|---|
| rule-1 **verdict** | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` | what the gate returned |
| matrix **tier** | `HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` / `NEVER RUN` | how the coverage matrix ranks the row |
| matrix **column** | `V` / `G` / `P` green or not | which axis the row has evidence on |

`GATE REACHED` appears in two of those meaning different things
(`COVERAGE_MATRIX.md` §1.1). **They are never conflated below.**

**A pre-registration that predicts its own failure and is proved right is worth more
than one that quietly hopes.** That is the whole design intent here, and it is why
§10 is written before §11's grading path rather than after the run.

---

## 1. SOURCE CLAUSE — the held primary, title-page verified, on the face of this document

Ruling 4's source test is met **by reading this section**, without following a
citation off this page.

### 1.1 The paper

**`/home/ubuntu/Certonomous/docs/papers/benchmark_test_cases/greenblatt_et_al_cfdval2004_hump.pdf`**
— on disk, with its `.txt` sidecar
(`greenblatt_et_al_cfdval2004_hump.txt`, **2,480 lines / 46,845 non-whitespace
characters**, verified real and not a stub).

**Title-page verified 2026-08-25 by RENDERING page 1 at 150 dpi and READING THE
RENDERED IMAGE** — not by filename, file type, hash, metadata or sidecar
(`CLAUDE.md` rule 15). What the rendered title page states:

* **AIAA-2004-2220**
* **"A Separation Control CFD Validation Test Case — Part 1: Baseline & Steady
  Suction"**
* **David Greenblatt, Keith B. Paschal, Chung-Sheng Yao, Jerome Harris, Norman W.
  Schaeffler and Anthony E. Washburn**
* **Flow Physics and Control Branch, NASA Langley Research Center, Hampton VA**
* **2nd AIAA Flow Control Conference, June 28 – July 1, 2004, Portland, OR**
* Abstract, first sentence, verbatim: *"Low speed flow separation over a
  wall-mounted hump, and its control using steady suction, were **studied
  experimentally** in order to generate a data set for a workshop aimed at validating
  CFD turbulence models."*
* The six author footnotes place every author in the same Flow Physics & Control
  Branch, Mail Stop 170. **The people who took the measurements wrote the paper.**

**Why the method is stated and not assumed.** This PDF's embedded metadata reads
`Title: Microsoft Word - PortlandPaperPart1.doc`, `Author: Administrator`. **A
manifest built from metadata would record this paper as authored by
"Administrator".** Rule 15 exists for exactly this: *a manifest can be internally
consistent and externally false.* The verification here is a reading of the page.

**Ruling 4 disposition: this is a PUBLIC PRIMARY EXPERIMENT, held on disk and
readable.** Not a computation, not a correlation, not another code's result, not a
numerical benchmark, and — critically for §1.4 — not a value carried to us by a third
party.

### 1.2 The gated data — Table 2, page 7, read from the rendered page

**Table 2, page 7: *"A comparison of measured separation and reattachment
location."*** Verified 2026-08-25 by rendering page 7 at 200 dpi and reading the
table image. All values are x/c. Reproduced in full, both rows, so no reader has to
take a selective quotation on trust:

| Case | Separation — 2-D PIV Centerline | Reattachment — Oil-film (off centerline) | Reattachment — 2-D PIV (centerline) | C'_Pmax |
|---|---|---|---|---|
| **Baseline** | **0.665 ± 0.005** | **1.11 ± 0.003** | **1.10 ± 0.005** | 1.08 |
| Control | 0.680 ± 0.005 | 0.94 ± 0.005 | 0.92 ± 0.005 | 0.90 |

**Only the BASELINE row is gated by this pre-registration.** The Control row is
reproduced for completeness and is out of scope: no suction is modelled.

### 1.3 THE CONDITION, which Table 2 DOES NOT CARRY AND A READER MUST NOT ASSUME

**Table 2 states no flow condition anywhere in the table itself.** The condition lives
in §V, "Test Cases", and is stated here explicitly so the frozen text carries it
rather than letting a reader assume the table is self-describing. Verbatim from the
paper (sidecar lines 349–350):

> *"One baseline test case (**Re = 929,000, M = 0.100 with no control**) and one
> control test case [Re = 929,000, M = 0.100, ṁ = 0.01518 kg/s, corresponding to
> Cµ = 0.241% …] were selected for detailed 2-D and 3-D PIV flow field
> measurements."*

**THE GATED CONDITION IS THEREFORE: Re_c = 929,000 (chord-based), M = 0.100,
BASELINE — NO CONTROL.** §7 records that the case this lab actually runs is **not** at
that Reynolds number, states the discrepancy as a numbered deviation, and does not
paper over it.

**One further sentence from the abstract that licenses a 2-D solve at all, and which
is therefore load-bearing rather than decorative:** *"Stereoscopic PIV and oil-film
flow visualization indicated that the **baseline separated flow field was mainly
two-dimensional**."* Under control the paper reports three-dimensionality appearing —
which is a second reason the Control row is out of scope here.

### 1.4 THE SOURCING DEFECT THIS DOCUMENT EXISTS TO REPAIR — and it is NOT what the dispatch believed

**This must be stated plainly because it corrects the premise this lane was
dispatched under, and a pre-registration built on a wrong premise is worth nothing.**

The dispatch that produced this draft said the missing piece for C-15 was *"only a
frozen pre-registration gating agreement with it — the 2026-07-29 agreement numbers
were ungated."* **That is not the case, and this lane found the counter-evidence in
the lab's own record rather than accepting the brief.**

**A frozen pre-registration gating agreement with 0.665 and 1.100 ALREADY EXISTS and
has ALREADY FIRED.** `verification/campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md` §3,
committed **`74797a57`** before any solve of that item, registers:

> *"Experimental values: **separation x/c = 0.665, reattachment x/c = 1.100**"* …
> *"Tolerance, declared now: **±5%** of each experimental x/c value — separation PASS
> iff |dev| ≤ 5% (x/c 0.632–0.698), reattachment PASS iff |dev| ≤ 5%
> (x/c 1.045–1.155)."*

and it graded (`W1_HUMP_CHALLENGE_RESULTS.md:36`): **SST separation 0.6544 (−1.59 %)
PASS; SST reattachment 1.2531 (+13.92 %) FAIL.**

**So why is C-45's P cell scored `NO` in the coverage survey, and why is this document
needed at all?** Because of **where that pre-registration says the numbers came
from.** Its own §3 sources them like this:

> *"Reference: the CFDVAL2004 experiment (Greenblatt et al., AIAA-2004-2220 / AIAA J
> 44(12), 2006), **as carried by NASA TMR's hump validation page** and the on-disk
> fetched data (`nasa_experimental_reference/{noflow_cf,noflow_cp}.exp.dat`)"*
> … *"Experimental values … (**NASA TMR, fetched live 2026-07-28**, on disk)."*

**Under the owner's Ruling 3 — *"a value reaching the lab through a third party is
`SECONDARY` and does not score P"* — that is a comparison against a SECONDARY
carrier**, even though the primary paper sat on this box the whole time and even
though the values are correct. **The missing piece was never the gate. It was the
sourcing.**

**THIS DOCUMENT'S DISTINGUISHING CONTENT IS THEREFORE PRECISELY THIS: it gates against
values read from the HELD PRIMARY — Table 2, page 7, of a title-page-verified
AIAA-2004-2220 — and from nothing else.** No TMR page, no fetched `.dat`, no
downstream carrier appears anywhere in §2's gate definitions. That is the whole of the
difference, and it is sufficient to satisfy Ruling 4 where `74797a57` could not.

**A corroboration that arrives for free, and which is recorded because it independently
supports §2.1's instrument choice:** the value NASA TMR carries for reattachment,
**1.100**, is Table 2's **2-D PIV centerline** figure — not the oil-film **1.11**. The
community's own CFD-comparison page picked the centerline PIV limb for comparison
against 2-D CFD. §2.1 reaches the same choice from first principles and did not need
this; that the two agree is corroboration, not the reason.

---

## 2. THE GATES

**Every gate below is defined before any solver runs under this document. The
reasoning for each threshold is stated BEFORE its number is given, in the order the
reasoning was actually done.**

### 2.1 THE INSTRUMENT CHOICE — made HERE, in writing, with the reason. **This is the L-284 clause.**

**The problem, stated so it cannot be pretended away later.** Table 2 gives **two**
reattachment values for the baseline, and they are **not** two readings of one
instrument:

* **1.11 ± 0.003** — **oil-film interferometry**, **OFF centerline**
* **1.10 ± 0.005** — **2-D PIV**, **ON centerline**

Different instruments, different spanwise stations, non-overlapping intervals
(`[1.107, 1.113]` and `[1.095, 1.105]`). **Silently picking one after the run is
exactly the L-284 failure the F4 grade already paid for.** So it is picked now.

> **DECISION: the gated reattachment comparator is x/c = 1.10 ± 0.005 — the 2-D PIV
> CENTERLINE value. The oil-film 1.11 is REPORTED beside it and is NOT gated.**

**Four reasons, in the order they were weighed:**

1. **Station match, not just quantity match.** The comparator is a **2-D solve** and
   its solution plane *is* the centerline. The 2-D PIV measurement was taken at the
   centerline; the oil-film measurement was taken off it. Gating a centerline
   computation against an off-centerline measurement imports a spanwise station
   mismatch into what is meant to be a closure-fidelity comparison.
2. **Commensurability with the separation gate.** §2.2's separation comparator,
   0.665 ± 0.005, is **also 2-D PIV centerline** — Table 2 offers no second
   instrument for separation. Gating both quantities on the same instrument at the
   same station means a separation/reattachment discrepancy is attributable to the
   *closure*, which is the question. A mixed pair would let a discrepancy be
   attributed to the change of instrument instead, and an ambiguity of that kind is
   fatal to a validation claim.
3. **The paper's own caveat sits on the oil-film limb, not on the PIV limb.** Page 7,
   read from the rendered image: the oil-films were exposed *"for a relatively long
   time (approximately 10 minutes)"* at low oil viscosity (20 cs), so *"the
   interpretation of these images must be done with some care"*; and while the
   reattachment line is *"essentially two-dimensional"*, *"there appears to be a
   cross-flow component with the shear stress apparently acting perpendicular to the
   reattachment line at some locations."* The paper flags the instrument this
   document declines to gate on.
4. **The alternative was the WIDER band, and the wider band was refused.** The
   registered alternative was to gate against the union interval spanning both
   limbs, **[1.095, 1.113]**. That band is wider than either limb's own interval, and
   **choosing the more generous of two available bands, before seeing either result,
   is still choosing generously.** cfd takes the narrower, non-flattering option, and
   names the alternative rather than hiding that it existed.

**AND THE HONEST LIMIT OF THIS CHOICE, so it is not oversold.** The two limbs differ
by **0.01 in x/c = 0.91 %**. §2.3's model-form tolerance is **±5 %**. **At the width
of the gate that actually grades this row, the two instruments are indistinguishable
and the choice cannot flip the verdict.** The choice matters for the *record* — for
being able to say afterwards which number was the target and to have said it first —
not for the arithmetic. Claiming otherwise would be overstating the ground, which is
the failure mode this lane spent Task A correcting elsewhere.

### 2.2 The two gated quantities

Both are the Table 2 **baseline** row, both **2-D PIV centerline**:

| gate | quantity | measured value | instrument uncertainty | as a fraction |
|---|---|---|---|---|
| **P1** | separation x_s/c | **0.665** | **± 0.005** | 0.75 % |
| **P2** | reattachment x_r/c | **1.10** | **± 0.005** | 0.45 % |

**Measurement definition, pinned contractually so no later re-grade can drift it**
(the `F7a_REGATE_SPEC.md` idiom, applied in advance rather than after a dispute):
separation and reattachment are the **sign crossings of the wall skin-friction
coefficient** along the hump wall, with
`Cf = −wallShearStress_x / (0.5 · U_inf²)` — **the F6a sign convention**, which is the
convention whose *inversion* produced F5c's withdrawn "4–12× reattachment error"
(`MATRIX_CONTRIBUTION.md` C-12). Separation is the **first** crossing downstream of
the hump crest; reattachment is the **first** crossing downstream of separation.
Extraction is by the unmodified `hump_gate_analysis.py` used by F6a and W1.

### 2.3 THE THRESHOLD IS A MODEL-FORM TOLERANCE, NOT THE MEASUREMENT UNCERTAINTY

**The reasoning, stated before the number.**

The intervals in §2.2 are **instrument uncertainty**: ±0.005 in x/c is what the PIV
system can resolve, i.e. 0.45 % on reattachment and 0.75 % on separation. **No RANS
closure will meet that on a smooth-body pressure-induced separation, and a gate set
there would not be a validation gate — it would be a guaranteed failure dressed as
one.** The threshold this document registers is a different quantity: **a MODEL-FORM
TOLERANCE — the width inside which the lab is prepared to say "this closure
reproduces this experiment."**

**Construction principle, declared before any number:** the model-form tolerance is
set as a **multiple of the instrument uncertainty**, and the multiple reflects whether
the quantity is **geometry-set** (weakly closure-dependent — the separation point on
this hump is largely fixed by the concave ramp and its pressure gradient) or
**closure-set** (strongly closure-dependent — the reattachment length is set by the
shear-layer turbulent transport the model *is*). A closure-set quantity earns the
larger multiple, because that is where model form legitimately lives.

**AND THEN THE PRINCIPLE IS OVERRIDDEN, DELIBERATELY, AND THE OVERRIDE IS THE STRONGER
RULE-2 ARGUMENT.** Applying the principle fresh, today, would yield a tolerance chosen
by a lane **who has already seen the answers** — 0.6544 (−1.59 %) and 1.2531
(+13.92 %) are in the lab's record and in this lane's context. **Any number derived
now, in either direction, is a number derived with the answers in hand.** A tighter
band on separation would be a band chosen knowing −1.59 % squeaks inside it; a looser
one on reattachment would be a band chosen knowing +13.92 % does not.

> **DECISION: this document ADOPTS, VERBATIM AND UNCHANGED, the ±5 % model-form
> tolerance registered at `74797a57` — a freeze made BEFORE any of those values
> existed.**
>
> * **Gate P1 — separation.** `PASS` iff `|x_s/c − 0.665| / 0.665 ≤ 0.05`,
>   i.e. **x_s/c ∈ [0.63175, 0.69825]**.
> * **Gate P2 — reattachment.** `PASS` iff `|x_r/c − 1.10| / 1.10 ≤ 0.05`,
>   i.e. **x_r/c ∈ [1.045, 1.155]**.
> * Otherwise **`GATE FAIL`**.
>
> **Both are MODEL-FORM TOLERANCES and are labelled as such. Neither is a measurement
> uncertainty, and neither may be reported as one.** ±5 % is **11.0×** the instrument
> uncertainty on reattachment and **6.7×** on separation.

**Why inheritance beats derivation here, stated once and plainly:** `74797a57`'s ±5 %
was genuinely prediction-first — it was frozen before its own solve and its own solve
then failed it. Inheriting it transplants that prediction-first property into this
document. Deriving a fresh number today cannot have that property, however good the
argument. **The construction principle above is retained because it is the reasoning
the lab should use when no prediction-first precedent exists — and because, applied to
reattachment, it independently lands on ±5 % (11× the instrument uncertainty on the
closure-set quantity), which is why adopting the precedent costs nothing there.**

**Where the principle and the precedent DISAGREE, the disagreement is registered as a
REPORTED channel and NOT as a gate.** On separation the principle would give a tighter
band (~±2 %, ≈2.7× the instrument uncertainty, on a geometry-set quantity). Turning
that into a gate today would be exactly the post-hoc tightening rule 2 forbids. So:

> **REPORTED, NOT GATED:** the ±2 % reading on separation (`x_s/c ∈ [0.6517,
> 0.6783]`) is computed and printed beside Gate P1's verdict, labelled
> **`REPORTED — NOT A GATE`**. It can never turn a `PASS` into a `GATE FAIL` or the
> reverse. It exists so the tighter physics question is *asked* on this run and can be
> *gated* prediction-first on the next one.

### 2.4 WHAT IS DELIBERATELY NOT GATED — Cp and Cf, and why gating them would undercut the row

> **NO GATE IN THIS DOCUMENT IS DEFINED ON Cp OR Cf VALUES DRAWN FROM AIAA-2004-2220.**

**Part 1 tabulates neither.** The paper contains exactly two tables — Table 1
(a comparison of cryogenic-facility and present-facility conditions) and Table 2 (§1.2
above) — verified by sweeping the held sidecar for table captions. Cp and Cf appear in
Part 1 **as figures only**.

**And the paper says outright that the Cf data is not in this document.** §VI, verbatim
(sidecar line 567): *"In addition, phase-locked 3-D PIV measurements, corresponding
approximately to the locations shown in fig. 7b, **will be available in part 2 of the
paper**."* **The lab does not hold Part 2** (AIAA Reno 2005). A gate on Cf from Part 1
would be a gate on data Part 1 does not contain.

**Digitising a figure is a strictly weaker basis than reading a table, and it would
undercut the very row this document exists to create.** The row's entire strength is
that its numbers are **printed values read off a rendered page of a title-page-verified
primary**. A digitised curve substitutes an unrecorded, unreproducible extraction step
between the primary and the gate — and it would hand any reviewer a clean objection to
cfd's first green `P`. **Table 2 is the strongest thing this paper offers. This
document gates on that and on nothing weaker.**

Cp along the wall **is** computed and **is** reported as a shape check, labelled
**`REPORTED — NOT A GATE`**, against the case's own shipped reference under F6a's
documented `p_ref` convention. It grades nothing.

---

## 3. PLATEAU AND ITERATIVE CONVERGENCE — fixed HERE, before compute

**`CLAUDE.md` rule 5 clause (1): *any level not iteratively converged or not plateaued
→ `NOT A RESULT`.*** That clause is worthless unless "plateaued" is defined **before**
the numbers are seen. It is defined here.

**Why this section is long, and whose bill paid for it.** ansys-verification's
**VMFL051** returned **`NOT A RESULT`** on a gate deviation of **−0.2337 %** against a
±0.5 % band — *a deviation that looked exactly like a `PASS`* — because the level was
not plateaued and the triple was **`OSCILLATORY` at R = −1.3486**
(`docs/campaigns/T-family/THERMAL_TIERING_DIRECTIVE.md:147,155`;
`docs/LAB_STATE.md:1312,1317`). **F12 has just shown the cost of not having this fixed
in advance.** The finding is ansys-verification's and is cited as theirs; **no lesson
is assigned from it here.**

### 3.1 The definition — ALL FOUR clauses must hold

A run is **PLATEAUED** only if all of (P-a) … (P-d) hold. Any failure ⇒ the run is
**`NOT A RESULT`** and **Gates P1 and P2 do not grade at all.**

* **(P-a) `residualControl` is TRIPPED, not the iteration cap reached.**
  `simpleFoam` must print `SIMPLE solution converged in N iterations` with
  **N < the registered `endTime` cap**. Reaching the cap is **not** convergence.
  *(This is where C-31's flat-plate triple is fragile — it ran to its 9,000-iteration
  cap — and that fragility is not inherited here.)*

* **(P-b) INITIAL residuals, never Final.** At the converging iteration the
  **Initial** residuals must satisfy the shipped controls: **U 5e-7, p 5e-7, k 5e-7,
  omega 1e-10.** **This lab has already paid for the Initial/Final confusion on this
  exact case:** `F6a_epistemic_band.md`'s kOmega reading of 1.0722 was recorded as
  gate-met and later corrected — *"supersedes the earlier 1.0722 / 'k final 1.37e-7'
  reading, which was Final-not-Initial and not actually gate-met."* The comparator
  reads the **Initial** column and asserts it is reading the Initial column.

* **(P-c) THE GATED FUNCTIONAL ITSELF MUST BE FLAT — this is the clause VMFL051
  needed.** A residual floor is a statement about the linear solve, not about the
  answer. So the *answer* is sampled: `x_r/c` and `x_s/c` are extracted **every 50
  iterations over the final 500 iterations** (10 samples each). **Peak-to-peak spread
  must be ≤ 10 % of that quantity's gate half-width:**
  * reattachment: **ptp ≤ 0.0055 in x/c** (10 % of 0.055)
  * separation: **ptp ≤ 0.0033 in x/c** (10 % of 0.033)

  **A functional still moving by a tenth of the gate band is not plateaued, whatever
  the residuals say.**

* **(P-d) NO OSCILLATION — the VMFL051 clause, stated in its own terms.** Across those
  10 samples, the **sign of the successive increment may alternate at most once**. Two
  or more sign alternations ⇒ oscillatory ⇒ **`NOT A RESULT`**. VMFL051's triple was
  `OSCILLATORY` at **R = −1.3486** and its deviation still read like a `PASS`; this
  clause is what refuses that shape *before* the deviation is looked at.

### 3.2 The ordering rule, registered so it cannot be re-ordered afterwards

> **PLATEAU IS EVALUATED FIRST AND ITS RESULT IS BINDING. A deviation inside the band
> on a run that is NOT plateaued is `NOT A RESULT` — it is NOT a `PASS`.**
>
> Per rule 5, the plateau clause can only turn a `PASS` or a `GATE FAIL` **into**
> `NOT A RESULT`, **never the reverse.** A `NOT A RESULT` is never rescued by a
> favourable deviation.

The comparator **refuses (exit 2) rather than degrades** when any of (P-a)–(P-d)
cannot be evaluated — a missing residual line, a truncated log, fewer than 10
available samples. **An unevaluable clause is a refusal, not a pass.**

### 3.3 Planted-zero control on the comparator (rule 3)

**A zero from a reader not shown able to see a non-zero is not evidence.** Before
grading, the comparator:

1. writes a known perturbation into a **copy** of the extracted `Cf` trace — a
   synthetic sign crossing planted at a **known** x/c offset from the true one;
2. re-reads that copy through **the same extraction path** that produces the graded
   value;
3. **refuses (exit 2) unless it recovers the planted crossing at the planted
   location.**

The perturbation is planted **by line index into the sampled trace**, not by value
match, so a reader that silently returns nothing cannot be mistaken for a reader that
correctly found nothing. **The plant is a control on the READER, and no gate verdict
is written by a comparator whose plant did not come back.**

---

## 4. NO GRID LADDER IS REGISTERED, AND THAT IS A DECISION, NOT AN OMISSION

> **THIS PRE-REGISTRATION REGISTERS NO ROACHE TRIPLE, NO GCI AND NO OBSERVED ORDER.
> IT CLAIMS NO `G`. THE `G` COLUMN FOR C-15 REMAINS `NO`.**

**Why, and the instruction it follows.** The cfd supervisor's standing instruction on
this draft is: *"establish that a hump mesh can actually pass this gate before you
freeze… If you cannot show hump meshes clear the gate, say so and register no ladder —
that is a far better outcome than a second inadmissible campaign."*

**What is established (§5): ONE hump mesh clears the admission gate, with a wide
margin, on measurement.** **What is NOT established: that a three-level hump *family*
does.** The benchmark ships exactly one mesh. Levels 2 and 3 would have to be
generated by this lab, and **their quality is unknown until they exist and are
`checkMesh`-ed.** F12 is the precedent for registering a ladder whose meshes had not
been shown admissible: it failed admission at **every** level and **worsened under
refinement** — the failing fraction of faces was structural, not a resolution
artefact, and refinement could not cure it.

**Registering an unproven ladder here would be repeating that, and it is not
necessary:** under Ruling 4, **`P` does not require `G`.** `P` requires a public
primary measured source, a frozen pre-registration, and the comparison. This document
supplies all three without a triple.

**The honest limitation, which travels with any result this document produces and is
NOT to be dropped from the RESULTS record:** *the graded value comes from a single
mesh level. No grid-convergence evidence supports it. It is not asymptotic and nothing
here may be read as saying so.*

**The follow-on item, named so the gap is a queue entry and not a silence:**
**`F6a-MESH-FAMILY-SURVEY` — generate coarse and fine hump meshes on the shipped
topology, `checkMesh` all three, and report max non-orthogonality and skewness per
level. ZERO SOLVER COMPUTE.** Only if all three clear §5's thresholds does a `G`
ladder become registerable, in its own separate pre-registration. **That survey is not
authorised by this document either.**

---

## 5. GATE M — MESH ADMISSION, ENFORCED **BEFORE** LAUNCH

### 5.1 The thresholds, from the standard rather than from habit

`docs/standards/MESH_STANDARD.md`:

| § | gate | threshold | kind |
|---|---|---|---|
| 3.1 | max non-orthogonality | **≤ 70°** (warning band 65–70) | **HARD** |
| 3.2 | max skewness | **≤ 4**, boundary faces included | **HARD** |
| 3.3 | max aspect ratio | 1000 | **ADVISORY — never a lone rejection** |

### 5.2 THE EVIDENCE THAT A HUMP MESH CAN ACTUALLY CLEAR IT — measured, not assumed

**This section exists because the supervisor required the question answered before a
freeze, and because F12 is what happens when it is not.**

The case's mesh is the benchmark's **shipped 51,626-cell `NASA_2DWMH` mesh**
(`W1_HUMP_CHALLENGE_PREREGISTRATION.md` §1). **Two independent `checkMesh` logs of
that mesh are on disk** and this lane read both:

* `/home/ubuntu/Certonomous/mission-output/nasa-hump/act6-nasa_hump/log.checkMesh`
* `/home/ubuntu/Certonomous/verification/runs/MESH_AUDIT_runs/2026-08-08/S1-fiml__hump__constant__polyMesh.log.checkMesh`

**They agree exactly on every figure that matters:**

| quantity | measured | gate | margin |
|---|---|---|---|
| cells | **51,626** | — | — |
| faces / internal faces | **207,209 / 102,547** | — | — |
| **max non-orthogonality** | **40.5495°** (average 9.19635) | ≤ 70° | **29.45° of margin** |
| **max skewness** | **0.743352** | ≤ 4 | **factor 5.4** |

> **A hump mesh clears both hard gates, and not narrowly.**

### 5.3 THE DISCREPANCY BETWEEN THE TWO LOGS, RESOLVED RATHER THAN WAVED THROUGH

**The two logs reach opposite verdicts** — `Mesh OK.` and `Failed 2 mesh checks.` — and
a pre-registration that quoted only the favourable one would be exactly the
"red with an innocent explanation" failure. So the explanation is established, not
asserted:

**The two runs differ in DIMENSIONALITY, not in mesh.**

* The `Mesh OK` log reports *"Mesh has **2** geometric (non-empty/wedge) directions
  (1 0 1)"* and max aspect ratio **99.6138**.
* The failing log reports *"Mesh has **3** geometric (non-empty/wedge) directions
  (1 1 1)"*, and its two failures are **max aspect ratio 12131.6 on 18,352 cells** and
  **cell determinant minimum 0 on all 51,626 cells** — i.e. on *every* cell in the
  mesh.

**A one-cell-thick 2-D mesh read as 3-D produces exactly those two artefacts by
construction**: the spanwise extent is a single cell, so aspect ratio and cell
determinant degenerate. The audit copy ran `checkMesh` against the bare `polyMesh`
without the case's `empty` front/back patches in force. **A defect that appears on
100 % of cells and vanishes when the same mesh is read in its own dimensionality is a
reading artefact, not a mesh defect.**

**And the clinching point: BOTH HARD GATES ARE IDENTICAL IN BOTH READINGS.**
Non-orthogonality and skewness are angle and face-centre measures that do not depend on
the dimensionality reading — 40.5495° and 0.743352 in both logs. **The evidence for
Gate M does not rest on choosing between the two verdicts.**

Two consequences, registered:

* **Aspect ratio is ADVISORY (§3.3) and is never a lone rejection.** The standard's own
  calibration is the NASA TMR flat plate at max aspect ratio **74,041** with max
  non-orthogonality 0. **It is REPORTED here, not gated.**
* **The cell-determinant check is NOT one of §3.1–§3.3's gates and is not made one
  here.** REPORTED, not gated. Inventing a gate at freeze time to look thorough is
  still inventing a gate.

### 5.4 The contrast with F12, which is why this section is not a formality

F12 rung 1's mesh measured **max non-orthogonality 70.64625857 against the ≤ 70
threshold, with 892 severely non-orthogonal faces** (`docs/COST_CALIBRATION.md` C-50,
read by this lane from the HEAD blob). The supervisor's brief reports the full
three-level series as **70.6463 / 70.8615 / 72.5422°** — failing at **all three**
levels and **worsening under refinement**, with face counts scaling ×4.03 and ×4.00,
i.e. a fixed *fraction* of the mesh that refinement cannot cure.

**Disclosure of read depth:** this lane independently located **rung 1's** figure in
the committed record. **It did NOT independently locate the level-2 and level-3
figures**; the three-level series is carried from the supervisor's brief and is
labelled as carried, not as verified by this lane.

**A structural reason to expect the hump family to behave differently — offered as a
REASON and explicitly NOT as evidence.** F12's is a `blockMesh` C-grid wrapped around
an aerofoil with a sharp trailing edge, which is the classic generator of high
non-orthogonality in the wake cut. The hump mesh is a shipped structured grid over a
**smooth wall-mounted body** with no wrap and no sharp edge. **That is an argument.
It is not a measurement, it licenses nothing, and it is why §4 registers no ladder.**

### 5.5 GATE M, AS REGISTERED — and the enforcement clause is the point

> **Gate M.** Before any solver process starts, `checkMesh` is run on the case mesh
> and its output parsed. **`PASS` iff max non-orthogonality ≤ 70.0° AND max skewness
> ≤ 4.0.** Aspect ratio, cell determinant and all other checks are **REPORTED and
> NOT gated**.
>
> **ENFORCEMENT — THE SINGLE CHANGE THAT WOULD HAVE SAVED F12's SPEND:**
> **the launcher REFUSES to start the solver when Gate M fails.** Non-zero exit, no
> solver process, no MPI rank spawned. **Gate M is enforced before launch, not
> recorded after it.**
>
> **A Gate M failure is `BLOCKED`**, not `GATE FAIL` and not `NOT A RESULT`: nothing
> was computed, so nothing was graded.

**Why this clause is written in these terms.** `docs/COST_CALIBRATION.md` C-50 records,
as a finding reported and not repaired, that F12's *"frozen `run_case` computes
`mesh_gate` and then launches the solver anyway"* — **20.5 s of solver wall went into a
mesh already known to fail admission gate A.** C-50 is careful that this was **not** a
departure from F12's frozen text, which gates the admission of *evidence* rather than
the act of launching. **This document closes that gap by gating the act of launching,
in the frozen text, in advance.**

**And be clear-eyed about what §6's smoke test would and would not have caught: a
one-timestep smoke test would NOT have caught F12,** which died at **iteration 180 of
6,000**. A smoke test would have passed and F12 would have crashed anyway. **Gate M
enforcement is what would have caught F12. The smoke test catches a different failure
and is registered for that different failure, not as insurance against this one.**

---

## 6. THE CASE, ITS REGIME PROVENANCE, AND THE PRE-FLIGHT SMOKE TEST

### 6.1 The case, stated completely so the frozen text does not depend on another file

The benchmark's shipped `NASA_2DWMH` OpenFOAM case: **Glauert-Goldschmied
wall-mounted hump, chord c = 0.42 m**, the **51,626-cell shipped mesh**, shipped
inlet/outlet profiles (`0/inletOutletFields`), **`simpleFoam`**, **SIMPLEC**, shipped
`residualControl` (**U/p/k 5e-7, omega 1e-10**), **`kOmegaSST` stock OpenFOAM v2606**,
**`mpirun -np 4`** with the shipped `decomposeParDict` (the family convention).
F6a's documented deviations 1–4 are inherited verbatim, including the stock-`kOmegaSST`
substitution **proven inert to 0.02 %** against the shipped baseline field
(`W1_HUMP_CHALLENGE_PREREGISTRATION.md` §1).

### 6.2 REGIME PROVENANCE — the supervisor's question, answered directly

**Question put to this draft: "cfd's dictionaries have been copied across regime
boundaries — the F family spans incompressible, low-speed, transonic, supersonic and
hypersonic. If the F6a case configuration is inherited from any case in a different
regime, say so and say which, so the smoke test is aimed rather than decorative."**

**Answer: it is not.** The F6a/W1 hump configuration is the benchmark's **shipped**
case, used as shipped. The solver is incompressible `simpleFoam`; the case is
low-speed incompressible (M = 0.1); **no dictionary here was copied from a
compressible, transonic, supersonic or hypersonic F-family case.** The single
substitution is stock `kOmegaSST` for the shipped model, and its inertness was measured
rather than assumed.

**That answer aims the smoke test rather than excusing it.** The VMFL045 mechanism —
which is **ansys-verification's finding and is cited as theirs, with no lesson assigned
from it here** — was a dictionary **complete for one regime and incomplete for
another**: its `fvSolution` solvers block was byte-identical to VMFL051's, and VMFL051
ran 1,693 timesteps successfully with the same missing entry, because VMFL051 is
inviscid and VMFL045 viscous, and `rhoCentralFoam` only enters the implicit viscous
corrector when μ > 0. **The gap was latent until the path that needed the key was
taken.** The analogue with a foothold here is not a regime boundary but a **model-library
boundary**: W1 ran this same case with a lab-built `libkOmegaSSTQCRTurbulenceModels.so`,
so the `libs` entries and the `RASModel` selection are the paths that differ between
the runs on this case. **The smoke test is aimed there.**

**Rule 14 applies to those `libs` entries and is restated because a lesson is not
applied until every call site asserts it: `libs` entries are INSERTED WITH AN ASSERT,
NEVER REPLACED.**

### 6.3 The smoke test — a PRE-FLIGHT CONDITION, explicitly NOT a gate

> **Before the graded run, ONE SIMPLE iteration is executed on the actual mesh with
> the actual dictionary set and the actual `libs` entries, in a scratch directory
> OUTSIDE `verification/runs/`. Non-zero rc, or any `FOAM FATAL` line, ABORTS the
> campaign before the graded run starts.**
>
> **It decides whether the run STARTS. It never decides what the run MEANS.** It
> produces no number that enters any gate, and its scratch directory is not evidence
> and is not cited by any record.

**Why this is registered even though the comparator will have its own selftests: a
comparator selftest proves the GRADER, not the CASE.** VMFL045's comparator passed
**45/45 with real negative controls** and could never have caught its crash, because
nothing in the pre-compute checks exercised the actual solver dictionary set. The case
died at **wall 0 s** on `FOAM FATAL IO ERROR: Entry 'e' not found in dictionary
"system/fvSolution/solvers"`. **Cost of the smoke test: seconds. Cost of not having
it: the whole campaign's setup, discovered at launch.**

---

## 7. DECLARED DEVIATIONS — including one this lane found and will not paper over

### 7.1 DEVIATION 1 — THE REYNOLDS NUMBER DOES NOT MATCH THE TABLE'S CONDITION

**This is the material one and it is stated first.**

* **Table 2's baseline was measured at Re_c = 929,000, M = 0.100** (§1.3, quoted from
  §V of the paper).
* **The case this lab runs is at Re_c = 936,000, M = 0.1**, U_inf = 34.625 m/s from
  the shipped `caseDef` — stated identically in
  `W1_HUMP_CHALLENGE_PREREGISTRATION.md` §1, `cases/dafoam/f6a_nasa_hump/F6a_nasa_hump.md:33,35`
  and `verification/campaign/F6_closure_aligned_flows.md:54`.
* **Discrepancy: +0.75 % in Reynolds number (936,000 / 929,000 = 1.00753).**

**This is the F12 pattern and it is named as such.** F12's pre-registration solves
**two** conditions because *"the published corrected conditions for this case do not
agree and picking one silently is the classic way to be confidently wrong here."*
**Picking one silently is refused here too.**

**DECISION, with the reason: the graded arm runs the SHIPPED case at Re_c = 936,000,
and the mismatch is carried as a declared deviation on the face of every result.**
The reason is that the shipped inlet/outlet profiles (`0/inletOutletFields`) are
supplied *with* the case at its stated Re_c, and **rescaling measured inflow profiles
to a different Reynolds number is an unvalidated modification whose error is not
bounded** — plausibly larger, and certainly less controlled, than a 0.75 % Re
mismatch on a pressure-gradient-driven separation.

**What is NOT claimed, and this is the honest half:** this document **does not claim
the 0.75 % is negligible.** No bound is asserted, because none has been measured here.
The paper does contain baseline data across **370,000 ≤ Re ≤ 1,114,800** (sidecar
line 349) and a figure of the separated-flow region versus Reynolds number, so the
sensitivity **is** answerable from the held primary — **and answering it is a
follow-on item, not a claim made now.**

> **REGISTERED FOLLOW-ON (not authorised by this document):
> `F6a-RE-SENSITIVITY` — read the baseline bubble's Re-dependence from
> AIAA-2004-2220's own Re sweep and bound the 936,000-vs-929,000 deviation. ZERO
> SOLVER COMPUTE.**

**A second arm at Re_c = 929,000 is deliberately NOT registered here**, because
constructing it requires the profile rescaling this section just called unvalidated.
**Naming that as the reason is better than registering an arm whose inflow is a
guess.**

### 7.2 DEVIATION 2 — single mesh level, no grid convergence

Per §4. Travels with every result this document produces.

### 7.3 DEVIATION 3 — stock `kOmegaSST` for the shipped model

Inherited from F6a, **measured inert to 0.02 %** against the shipped baseline field.
Inherited verbatim, not re-derived.

### 7.4 DEVIATION 4 — `p_ref` convention on the reported Cp

F6a's documented convention carries. **Cp is REPORTED, not gated** (§2.4), so this
deviation cannot affect any verdict.

---

## 8. COST — in core-minutes, per `CLAUDE.md` rule 12

**A proposal with no cost is disqualified. Every figure below is labelled ESTIMATED or
MEASURED-ANALOG, and none is called measured for this run, because this run has not
happened.**

### 8.1 The analog, named as rule 12 requires

**The analog is C-45 / C-46 — prior F6a hump solves on this box, on the SAME case,
the SAME shipped mesh, the SAME solver and the SAME rank count.** This is the
strongest analog class available: not a borrowed per-cell rate across geometries, but
an identical-configuration measurement.

| analog | measured | artifact |
|---|---|---|
| **C-45 SST leg** | **5.58 core-min** (83.68 s wall × 4 ranks) | `W1_HUMP_CHALLENGE_RESULTS.md:93` |
| C-45 QCR arm | 4.71 core-min (70.59 s × 4) | `:94` |
| C-45 decompose/reconstruct/extraction | < 0.3 core-min | `:95` |
| **C-46 a1 study** | **20.7 core-min gross against a registered cap of 12** | `W1_HUMP_A1_RESULTS.md:74` |

**C-46 is in this table because it is the cautionary one: a cap was already overrun on
this exact case family, by 1.7×.** §8.3's cap carries headroom for that reason and for
no other.

### 8.2 The estimate, term by term

| # | term | figure | basis |
|---|---|---|---|
| 1 | `checkMesh` (Gate M) | **0.05 core-min** | **ESTIMATED.** C-50 measured `checkMesh` at 0.407 s on a 23,040-cell mesh; 51,626 cells ≈ 2.24× ⇒ ~0.9 s at 1 rank |
| 2 | pre-flight smoke test | **0.10 core-min** | **ESTIMATED.** One SIMPLE iteration of a 1,772-iteration / 83.68 s run ≈ 0.05 s wall × 4 ranks, plus process startup |
| 3 | graded solver run | **6.42 core-min** | **ESTIMATED from a MEASURED analog**: C-45's 5.58 core-min × **1.15** for the §3.1 (P-c) functional-sampling `functionObject`. **The 1.15 is an estimate and is labelled one** |
| 4 | decompose / reconstruct / extract / grade | **0.30 core-min** | **ESTIMATED**, analog `:95` |
| | **UNCONTENDED SUBTOTAL** | **6.87 core-min** | |
| 5 | **CONTENTION ALLOWANCE — NAMED SEPARATELY AND NETTED OFF NOTHING** | **+6.87 core-min** | **ESTIMATED at ×1.0 of the subtotal.** See §8.4 |
| | **POINT ESTIMATE** | **13.74 core-min ESTIMATED** | |

### 8.3 The cap, and what an overrun does

> **CAP: 30 core-min.** **An overrun STOPS THE RUN. It does not get a new budget.**

**Why 30 and not 15.** C-46 measured **20.7 core-min against a registered cap of 12**
on this exact case family. A cap set at the point estimate would be a cap the family
has already demonstrated it can exceed. 30 sits **2.2×** above the uncontended
subtotal and **1.5×** above the with-contention point estimate.

**DOLLARS, DERIVED — NOT MEASURED**, at **$0.0513/core-h**, c7a.4xlarge,
**reported-by-owner** (the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5):

* point estimate 13.74 core-min = 0.2290 core-h ⇒ **$0.011748 DERIVED**
* cap 30 core-min = 0.5 core-h ⇒ **$0.025650 DERIVED**

**Both are far under the $25 pre-authorisation, and being under it is not a substitute
for costing it** — a blanket authorisation is not a per-item reading (rule 9).
**Zero GPU. Zero container.**

### 8.4 The contention term, and the standing gap it is drawn from

`docs/COST_CALIBRATION.md` **C-51** measured contention on this box at **864.48 s of a
1,399 s run = 62 % of the entire spend on that item**, with `loadavg` read live at
**68.38 / 64.32 / 56.15 on `nproc = 16`**. C-50 read **3.62 / 8.31 / 31.34** before
F12's launch. C-51 names the standing gap in its own words: **"the lab's estimating
method has no CONTENTION TERM AT ALL."**

**This document applies an explicit ×1.0-of-subtotal contention allowance to ITS OWN
estimate, states it as a separate line, and nets it off nothing.** It **does not**
propose a lab-wide convention: C-51 flags that change as **PROPOSED AND NOT DECIDED**
and notes that *"moving an estimating convention is not a lane's call"* (rule 9). **A
lane does not decide it here either.**

### 8.5 Cap enforcement — the derivation, stated explicitly

**RANKS = 4** (`mpirun -np 4`, shipped `decomposeParDict`).

> **A WALL-CLOCK `timeout` IS NOT A CORE-MINUTE CAP. They coincide only at 1 rank.**
>
> `timeout_seconds = cap_core_min × 60 / ranks = 30 × 60 / 4 = **450 s**`
>
> A naive `timeout 1800` (= cap × 60) at 4 ranks would permit **4× the registered
> budget** before firing — **a cap that does not cap.**
>
> Mirroring F12's launcher, a **mesh reserve** is subtracted before the remainder is
> handed to the solver: `MESH_RESERVE_S = 30`, so **solver timeout = 420 s**, with
> 30 s covering `checkMesh`, the smoke test and `decomposePar`.

**This finding is `ansys-verification`'s and is cited as theirs**
(`docs/LAB_STATE.md:1298–1303`; `docs/COST_CALIBRATION.md` C-51 item (8);
`cases/ansys_verification/VMFL045/PREREGISTRATION.md:533–535`). **No lesson is assigned
from it here, and this document claims no part of it.**

### 8.6 If the run is interrupted

> **No total ratio is written for an interrupted run.** C-50's convention, arrived at
> independently by cfd and followed here in its own words: *"the run stopped at
> iteration 180 of the registered 6,000 (3.0 %), so 0.4617 against 11.9 is not a
> calibration, it is an interruption."* **An interrupted run's ratio is UNDEFINED, not
> 0.0×.** The **rate** (core-min per 1,000 SIMPLE iterations at 4 ranks on this mesh)
> is calibrated instead, and that is what enters `docs/COST_CALIBRATION.md`.

### 8.7 The calibration row this run will owe

Rule 12's estimate-versus-actual duty attaches **at completion of the graded run** and
is not optional: a row in `docs/COST_CALIBRATION.md` comparing **13.74 core-min
predicted** against the actual read from logs, stating the ratio, and attributing the
gap across **contention / waste / misprediction** with **waste named separately and
never absorbed into the ratio**.

**It does NOT attach to the drafting of this document**, which spent zero
core-minutes. Per the cfd supervisor's standing ruling of 2026-08-25: **a process with
no core-minutes has no actual to compare against an estimate, and inventing a
denominator corrupts the ledger. Zero-compute dispatches add no calibration row.**

---

## 9. THE FREEZE CONDITION — rule 2, with the directory named and the check specified

**This is a BEFORE-FIRST-COMPUTE document.** Until the first solver process starts,
amendments are legal **and each must state its condition and how it was checked**
(rule 2). After first compute, gates are closed; changes land only as dated addenda
that **cannot alter a gate, threshold, cap or label**, and originals are struck, never
rewritten.

### 9.1 The directories that must not exist

> **FREEZE CONDITION, to be evaluated by `test -e` IN THE LAUNCHING SHELL INVOCATION —
> not read from this file:**
>
> * **`/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs`**
> * **`/home/ubuntu/certonomous-runs/f6a-greenblatt-baseline`**
>
> **Both verified ABSENT by `test -e` on 2026-08-25 by this lane.** That reading is
> **evidence of the condition at drafting time and is NOT a substitute for the check
> at launch time** — the C-30 precedent is explicit: *"Re-check the freeze condition in
> the same shell invocation as the launch, not from this file."*

### 9.2 The rule-4 existing-directory guard — MIRRORED, not reinvented

> The launcher **refuses (exit 3)** if any registered run directory already exists.
> **The implementation is mirrored from
> `verification/runs/F12_runs/run_f12_rung.py:66–70`, which already does exactly this
> for this family.** A new guard is not invented; rule 14's principle applies —
> a guard is inserted, and asserted, not re-authored.

### 9.3 Comparator and grading-path freeze

* **The grading path is fixed at the pre-registration commit.** The comparator file's
  blob sha is recorded in this document at freeze time, and before grading the frozen
  file **is hashed against the committed blob** to verify it *is* the file that ran.
* **No GCI, observed order or Richardson value is quoted anywhere in this campaign**,
  and none could be — §4 registers no triple. Standing cfd constraint: Roache/GCI
  numbers come from `scripts/roache_triple.py` only, **never** from
  `sdk/workflows/tmr_verification.py`.

### 9.4 Completion, per rule 4

A run is done only if **all** of: `rc = 0`; an `End` line; **last time == `endTime`**;
the required fields present (`U p k omega nut` for this incompressible family — the
`T`/`p_rgh`/`alphat` list is the **thermal** family's and does not apply); and the
**age guard** — every field at `endTime` **newer** than the case's own `0/U`, which is
touched last at launch and so dates the run permitted to produce the answer. **The
comparator refuses (exit 2) rather than degrades on any failed clause.**

*(Note the deliberate substitution: rule 4 names `0/T` for the thermal family. This
case has no `T`. The age guard's anchor here is **`0/U`**, and it is named explicitly
rather than left for a launcher to guess.)*

---

## 10. THE HONEST FORECAST — written BEFORE the run, in the fixed vocabulary

> **THIS GATE WILL PROBABLY FAIL, AND THIS DOCUMENT SAYS SO BEFORE THE SOLVER
> STARTS.**

### 10.1 What this box already knows, all MEASURED and all cited

| solve | separation x/c | reattachment x/c | vs 1.10 | artifact |
|---|---|---|---|---|
| **C-45 SST baseline** | 0.6544 (−1.59 %) | **1.2531** | **+13.92 %** | `W1_HUMP_CHALLENGE_RESULTS.md:36` |
| C-45 SST + QCR2000 | 0.6538 (−1.68 %) | 1.2553 | +14.12 % | `:36` |
| **C-46 a1 = 0.34** | 0.6558 | **1.2033** | +9.39 % | `W1_HUMP_A1_RESULTS.md` |

**A small discrepancy this lane found and reports rather than smoothing over.** The
same baseline reattachment appears as **1.2531** (`W1_HUMP_CHALLENGE_RESULTS.md:36`)
and as **1.2534** (`F6a_epistemic_band.md`, `W1_HUMP_CHALLENGE_PREREGISTRATION.md` §2).
The results file's own Gate-V table (`:25–26`) shows why: **1.25314 is W1's fresh
measurement; 1.2534 is F6a's earlier value used as W1's Gate-V reference**; they differ
by **−0.0003**, inside W1's own ±0.005 band. **Both are correct readings of different
runs. This document gates against neither and quotes both.**

**And the framing fact that makes this campaign a formalisation rather than a
discovery:** `verification/campaign/F6a_epistemic_band.md:134` already carries the row
*"NASA experiment 0.6650 / 1.1000"*. **Those ARE Greenblatt Table 2's baseline
values. cfd has been comparing against this paper all along — ungated on the primary.**

### 10.2 The predictions, scored clause-by-clause afterwards against this frozen text

1. **Gate M — predicted `PASS`.** Measured margin 29.45° and factor 5.4 (§5.2).
2. **Gate P1 (separation) — predicted `PASS`.** Band [0.63175, 0.69825]; every closure
   on record for this case lands **0.6541–0.6679**.
3. **Gate P2 (reattachment) — predicted `GATE FAIL`.** Band [1.045, 1.155]; SST is
   expected near **1.25**, roughly **+13 % to +14 %** — about **0.10 in x/c outside the
   band's upper edge. This is not marginal.**
4. **Plateau — predicted to HOLD.** C-45's SST leg tripped `residualControl` at
   **1,772 iterations**; §3's (P-c)/(P-d) clauses have never been evaluated on this
   case and could still refuse it.
5. **ROW VERDICT — predicted `GATE FAIL`.**
6. **ROW TIER — predicted `NOT HELD`** — *a green column's own gate returned FAIL*, in
   Ruling 1's own words.
7. **`P` COLUMN — predicted GREEN.** Measured physical reality, public primary source,
   held and title-page verified, pre-registration on disk frozen before the solve.
   **Ruling 4 asks for the source and the pre-registration. It does not ask the gate to
   pass.**

> **Stated once, in the words that must survive into the RESULTS record: the `P` column
> goes GREEN on the source and the frozen pre-registration; the VERDICT will likely be
> `GATE FAIL` and the TIER `NOT HELD`.**

### 10.3 The named outcomes

* **OUTCOME A — expected.** P1 `PASS`, P2 `GATE FAIL`, plateau holds.
  Verdict **`GATE FAIL`**, tier **`NOT HELD`**, **`P` green.** **cfd's first green `P`,
  earned on a failed gate.** *A pre-registration that predicts its own failure and is
  proved right is worth more than one that quietly hopes.*
* **OUTCOME B — surprise.** P1 `PASS` and P2 `PASS`. Verdict **`PASS`**.
  **This would be treated as a surprise and investigated, not celebrated:** the first
  action is to diff this run's extraction path against W1's, because a fresh agreement
  at ±5 % where W1 measured +13.92 % on the same case and mesh is more likely an
  instrument change than a physics change.
* **OUTCOME C — refusal.** Any of §3's (P-a)–(P-d) fails. Verdict **`NOT A RESULT`**,
  whatever the deviations say. **`P` does NOT go green**: Ruling 4 requires a
  comparison, and a `NOT A RESULT` is not a comparison.
* **OUTCOME D — blocked.** Gate M fails on the shipped mesh, contradicting §5.2's
  measurement. Verdict **`BLOCKED`**, no solver launched, ≈ 0.05 core-min spent.

### 10.4 THE CONSTRAINT THAT MAKES A FRESH SOLVE UNAVOIDABLE

> **THE EXISTING NUMBERS CANNOT BE RETRO-GATED, AND NO WORDING AVOIDS IT.**

Rule 2 freezes the gate **before the solver starts**, and the freeze is *"the
document's entire evidentiary content: it proves the gate could not have been chosen
to fit the answer."*

**1.2531 already exists.** It is in `W1_HUMP_CHALLENGE_RESULTS.md`, it is in this
document at §10.1, and it was in this lane's context while §2.3 was being written. **A
pre-registration written on 2026-08-25 and graded against it is, by rule 2's own
definition, a gate chosen to fit the answer.**

**This is not a technicality and careful drafting does not dissolve it.** §2.3's band
is *numerically identical* to `74797a57`'s — deliberately — and **that still does not
license applying it backwards**, because what rule 2 protects is not the number but
the **ordering**.

> **A FRESH SOLVE UNDER THE NEW FREEZE IS REQUIRED. This is the shortest path to a
> green `P` in cfd territory. It is not a free one.** Its price is §8's **13.74
> core-min** point estimate.

**And the one manoeuvre that is explicitly REFUSED here:** re-labelling `74797a57` as a
primary-sourced gate by amendment. Rule 2 closes gates after first compute; changes
land only as dated addenda that **cannot alter a gate, threshold, cap or label** — and
**re-sourcing a gate's reference IS altering the gate.** **The W1 record is not touched
by this document, and C-45's cells are not moved by it.**

---

## 11. GRADING PATH AND ARTIFACTS

* **Run root (must not exist at launch, §9.1):**
  `verification/runs/F6a_GREENBLATT_runs/baseline_Re936k/`
* **Preserved on failure.** If the run fails, **the tree is the proof of the finding
  and is NOT cleared to make room for a nicer one** — F12's failed tree stands and is
  cited by its own calibration row. Note that `log.*`, time directories,
  `constant/polyMesh/` and `postProcessing/` are **gitignored**, so — following F12's
  precedent — **any `FOAM FATAL` text is captured into a committed `result.json`
  `traceback` field**, where git can hold it.
* **Reported, never gated:** Cp shape check; the oil-film reattachment limb 1.11; the
  ±2 % separation reading; aspect ratio; cell determinant; `checkMesh`'s full output.
* **Every reported channel is labelled `REPORTED — NOT A GATE` at the point it is
  printed.** A printed discrepancy annotated as non-binding is worse than one never
  computed, so the labelling is on the value, not in a footnote.

---

## 12. WHAT THIS DOCUMENT DOES NOT DO

1. **It is not frozen and it authorises no compute.** §9's condition has never been
   evaluated in a launching invocation.
2. **It claims no `V` and no `G`.** No exact solution, no manufactured solution, no
   correlation; no triple, no GCI, no observed order.
3. **It does not touch `docs/COVERAGE_MATRIX.md`**, which is the verification team's.
4. **It does not touch the W1 record** (`74797a57` and its results), and moves no cell
   of C-45 or C-46.
5. **It does not edit `MATRIX_CONTRIBUTION.md`'s C-15 row.** That row moves — if it
   moves — when this document is frozen and its run graded, not before. **A verified
   source is not a green `P`.**
6. **It registers no ladder** (§4) and no Re-sensitivity arm (§7.1); both are named as
   follow-on items and neither is authorised here.
7. **It sends nothing.** **SUBMISSIONS ARE PARKED.** Nothing here is filed, sent,
   uploaded, registered, posted or commented outside this box.

---

**Drafted 2026-08-25 by a cfd `lab-lane` at the cfd supervisor's direction.
ZERO SOLVER COMPUTE: no solver, no mesher, no case directory, no MPI rank.
NOT FROZEN. `PENDING` the supervisor's ruling.**
