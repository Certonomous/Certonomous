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
