# F6a / C-15 — NASA wall-mounted hump vs Greenblatt et al. Table 2 — PRE-REGISTRATION

## ⚠ THIS DOCUMENT IS FROZEN. IT IS THE `CLAUDE.md` RULE-2 FREEZE FOR C-15.

**Status: `PENDING` — frozen 2026-08-25 by a cfd `lab-lane` at the cfd supervisor's
direction. `PENDING` here is rule 1's DISPLAY/QUEUE state — "not yet run" — and is NOT a
softened verdict. No solver has run under this document.**

* **The freeze commit spent ZERO CORE-MINUTES, and the freeze and the launch are SEPARATE
  DISPATCHES BY CONSTRUCTION.** The dispatch that produced this freeze opens *"ZERO
  COMPUTE IN THIS DISPATCH"* and closes *"a lane that freezes and launches in the same
  dispatch has destroyed the evidentiary value of the freeze."* Between the two sits the
  cfd supervisor's own §3 check — **pre-registration committed before compute** — which
  `SUPERVISION_CHARTER.md` §3 forbids him to delegate to the lane that wrote it.
* **What this freeze closes on first compute:** every gate, threshold, cap and label
  below — **Gate M** (§5.5), **Gates P1 and P2** (§2.3), the plateau clauses
  **(P-a)–(P-d)** (§3.1), the ordering rule (§3.2), the **30 core-min cap** (§8.3) and
  the forecast (§10). After first compute, changes land only as dated addenda that
  **cannot alter a gate, threshold, cap or label**; originals are struck, never rewritten.
* **Amendments BEFORE first compute remain legal**, and each must state its condition and
  how it was checked. **One is already registered and owed: §9.3's grading wrapper.**
* **THE FREEZE CONDITION IS NOT SATISFIED BY READING THIS FILE.** §9.1's `test -e` is
  evaluated **in the launching shell invocation**, and it has not been evaluated in one.
* **This file supersedes and renames `F6a_GREENBLATT_PREREGISTRATION_DRAFT.md`**, whose
  own text pre-committed to that rename as the freeze event's signal. The rename also
  removes a double-count the draft itself identified: cfd's coverage survey enumerates
  `*PREREGISTRATION*` across the tree, and `..._DRAFT.md` matches that glob, so leaving
  both would count one item twice. **`c10abf68` (Ruling 6) cites the draft under its
  pre-freeze path; that citation resolves to THIS file, and to the draft blob preserved
  in git history at that commit.**
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


### 1.5 VERIFICATION'S RULING 6 — the ground this document did not have, and the two corrections it makes to the record

**Folded in AT FREEZE from `c10abf68` (2026-08-25), the coverage-matrix owner's Ruling 6.**
It was written after this document's draft. **It alters no gate, threshold, cap or label
here** — it supplies the *ground* §1.4 was reasoning towards, and it corrects two things
§1.4 had wrong.

#### 1.5.1 The ruling

**A sourcing addendum to W1's existing pre-registration is LEGAL but INERT on `P`.**
Legal, because a citation is none of rule 2's four protected items. **Inert, because
Ruling 3's operative test is the route the VALUE travelled** — a historical fact about a
run that has already fired — and because **L-44** holds that a frozen artifact's
evidentiary value is *"its TIMESTAMP RELATIVE TO WHAT IT JUDGES"*. A citation written on
2026-08-25 has no standing against a run graded on 2026-08-07.

> **`W1` STAYS `GATE FAIL`. C-45's cells do not move. The row converts ONLY under a fresh
> freeze — this one.**

#### 1.5.2 THE DECIDING FACT — and it sharpens §1.4's "corroboration" into something harder

§1.4 records the agreement between TMR's 1.100 and Table 2's PIV limb as *"corroboration
that arrives for free."* **Ruling 6 measured the same fact and found the sharper thing in
it.** Greenblatt Table 2's baseline carries reattachment **TWICE**:

| quantity | Greenblatt Table 2, baseline | frozen at `74797a57` |
|---|---|---|
| separation — 2-D PIV centerline | **0.665 ± 0.005** | 0.665 |
| reattachment — **oil-film (OFF centerline)** | **1.11 ± 0.003** | *(absent)* |
| reattachment — **2-D PIV (ON centerline)** | **1.10 ± 0.005** | 1.100 |

**The primary does not carry one reattachment value. It carries two, and they disagree by
0.9 %.** The frozen W1 gate uses **1.10** — and **this lab never made that limb choice.
NASA TMR made it, and the pre-registration inherited it.** So an honest re-sourcing
addendum to W1 could never have been a re-labelling: to be true it would have had to
declare **which limb it adopts**, **why**, **the ±0.005 it sits inside**, and **the Re
condition mismatch** — four selections made today with **1.2531 already in hand**.
Verification's sentence is the whole ruling:

> **"A citation is not one of rule 2's four protected items; but a citation that must
> carry a limb choice to be true is a threshold choice wearing a citation's clothes."**

**§2.1 of this document is precisely that choice made PROSPECTIVELY** — the limb, the
reason, the interval, and (in §7.1) the condition mismatch, all declared under a freeze
that predates its own run. That is the difference between this document and an addendum,
and it is the only difference that matters.

#### 1.5.3 CORRECTION 1 — the lab HELD this primary at W1's freeze. It failed to READ it.

**Greenblatt entered this box at `03814b0a`, 2026-08-05** — verified at freeze by this
lane against the commit itself, which adds
`greenblatt_et_al_cfdval2004_hump.pdf` together with its **2,480-line** sidecar.
**W1's freeze is `74797a57`, 2026-08-07 — two days later.** And
`W1_HUMP_CHALLENGE_PREREGISTRATION.md:60` **already NAMES the paper**: *"Reference: the
CFDVAL2004 experiment (Greenblatt et al., AIAA-2004-2220 / AIAA J 44(12), 2006), as
carried by NASA TMR's hump validation page"*.

> **The lab did not fail to hold the primary. It failed to read its table.**

**This correction is recorded because it makes the defect worse, not better**, and a
frozen document that states the flattering version of its own origin is not worth
freezing. §1.4's framing — that the missing piece "was never the gate, it was the
sourcing" — survives; what does not survive is any implication that the paper was
unavailable. It was on this box, named in the very document that then gated against a
carrier.

#### 1.5.4 CORRECTION 2 — §10.4 refused this manoeuvre FIRST, and verification affirmed rather than corrected it

Ruling 6 records that **this document's own §10.4 had already refused the re-labelling
manoeuvre, unprompted and against its own interest**, in its own words — *"re-sourcing a
gate's reference IS altering the gate"* — and states that the ruling *"supplies a ground
that draft did not have — the two-limb table — not a correction to it."*

**§10.4 stands unchanged in this frozen text.** It is not rewritten to cite the ruling
that later agreed with it, because the value of §10.4 is that it was written **before**
anyone asked.

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

**AND THE FINDING IS ROBUST TO THE LIMB — stated numerically, in the frozen text, before
the solver starts.** Against the oil-film limb **1.11** the ±5 % band is
**[1.0545, 1.1655]**; against the gated PIV limb **1.10** it is **[1.045, 1.155]**. The
value already on this box for this case, mesh and closure — **1.2531** — misses the first
by **+12.89 %** and the second by **+13.92 %**.

> **THE INSTRUMENT CHOICE CANNOT FLIP THE VERDICT. Both limbs return `GATE FAIL` on the
> SST baseline.**
>
> *Arithmetic re-derived at freeze by this lane rather than carried from the ruling:*
> `(1.2531 − 1.11)/1.11 = +12.8919 %`; `(1.2531 − 1.10)/1.10 = +13.9182 %`.
> Verification reached the same two figures independently at `c10abf68` and concluded
> *"no gate verdict anywhere in this lab moves because of this ruling."*

**AND WHAT THIS ROBUSTNESS DOES NOT LICENSE, stated so it cannot be misread later: it
does NOT make the limb choice optional.** A gate that would return the same verdict
either way is still a gate that must name its comparator in advance — because **1.2531 is
not this run's answer**, this run has not happened, and a document that declined to
choose would be a document choosing after the fact. The robustness protects the *record*
against a reader who suspects the limb was picked to fail. It does not excuse the
picking.

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

**AND VERIFICATION'S REASON, WHICH IS SHARPER THAN THE ONE ABOVE AND IS RECORDED
ALONGSIDE IT RATHER THAN IN PLACE OF IT.** Ruling 6 (`c10abf68`) endorses this
inheritance explicitly — *"Inheriting a band from a freeze that predates the answers
preserves a prediction-first property a fresh derivation cannot manufacture"* — and then
names the asymmetry this document's own argument had not isolated:

> **"And note the asymmetry that makes it legitimate rather than convenient: the
> inherited band is the one under which the row ALREADY FAILED. A lane inheriting a band
> that had already passed would be a different question and is not decided here."**

**That is the load-bearing half, and it is the half this document did not have.**
Inheritance is not virtuous in itself. It is legitimate *here* because the transplanted
band is the one that has **already refused this lab's own answer** — so adopting it
cannot be self-serving, whatever the lane's intentions were.

**This document therefore does NOT read Ruling 6 as blanket licence to inherit bands.**
Were the precedent a band this case had already **passed**, §2.3 would owe a fresh
derivation and nothing above would license skipping it. The endorsement is of *this*
inheritance, on *this* asymmetry, and it is recorded with its limit attached.

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
>
> **RE-READ AT FREEZE TIME by this lane, in the freezing invocation: BOTH ABSENT.** That
> is now two readings, both at zero compute, and **neither of them is the check that
> authorises a launch.** The launching invocation evaluates `test -e` itself, or it does
> not launch.

### 9.2 The rule-4 existing-directory guard — MIRRORED, not reinvented

> The launcher **refuses (exit 3)** if any registered run directory already exists.
> **The implementation is mirrored from
> `verification/runs/F12_runs/run_f12_rung.py:66–70`, which already does exactly this
> for this family.** A new guard is not invented; rule 14's principle applies —
> a guard is inserted, and asserted, not re-authored.

### 9.3 Comparator and grading-path freeze — PINNED HERE, with the one gap NAMED

**The EXTRACTION path — the code that turns a `Cf` trace into `x_s/c` and `x_r/c`, and
therefore the code that produces both gated numbers — is PINNED BY HASH NOW, at freeze:**

| item | value |
|---|---|
| canonical path | `cases/dafoam/f6a_nasa_hump/case/hump_gate_analysis.py` |
| **sha256** | **`9a6ec8553b863b3b43a1a3ca03970923778f7da5c2bf3e1cfacdfa8f6fd2414f`** |
| **git blob id** (`HEAD:<path>` at HEAD `dd4ba663`) | **`ec263bed8623a81b67106c3880febdca1b3d5eff`** |

**Twenty-three copies of this file exist in the tree and ALL TWENTY-THREE ARE
BYTE-IDENTICAL** — verified at freeze by hashing every copy and finding exactly **one**
distinct digest. §2.2's phrase *"the unmodified `hump_gate_analysis.py` used by F6a and
W1"* is therefore unambiguous — **and it is pinned to one path and one digest here
anyway, because a name is not a hash.** Before grading, the file that ran is hashed
against the digest above. **A mismatch is `NOT A RESULT`, not a repair.**

> **THE GAP, NAMED RATHER THAN GLOSSED. It is the one thing this freeze could not fully
> satisfy, and it is stated in the frozen text rather than discovered at launch.**
>
> **The extraction path exists and is pinned. THE GRADING WRAPPER DOES NOT EXIST YET.**
> Nothing on disk today implements §3.1's (P-a)–(P-d) plateau clauses, §3.2's ordering
> rule, §3.3's planted-zero control, §5.5's **pre-launch** Gate M enforcement, §9.2's
> existing-directory guard or §8.5's `timeout` derivation. **No blob sha can be recorded
> at freeze for a file that has not been written, and inventing one would be worse than
> admitting it.**
>
> **REGISTERED CONDITION, binding on the launching dispatch:** the grading wrapper and
> the launcher are written and **COMMITTED BEFORE THE FIRST SOLVER PROCESS STARTS**, and
> their paths, sha256 digests and blob ids land in this document as a **dated pre-compute
> amendment under rule 2**. That amendment is legal *precisely because* it is before
> first compute, and it must state its condition and how it was checked: **the §9.1 run
> directories do not exist, checked by `test -e` in the amending invocation.**
>
> **It may not alter any gate, threshold, cap or label — and it cannot**, because §2.2,
> §2.3, §3.1, §3.2, §5.5 and §8.5 specify the arithmetic, the thresholds, the ordering
> and the cap **completely, here, in the frozen text**. The wrapper is an
> **implementation of gates already frozen. It is not a gate.**
>
> **AND THE CLAUSE THAT MAKES THAT MORE THAN A PROMISE: if the wrapper as written cannot
> implement a clause of §3 as frozen, THE CLAUSE IS NOT RELAXED TO MATCH THE CODE.** The
> campaign stops, the conflict goes to the supervisor, and the row stays `PENDING`.
> Bending a frozen clause to fit an implementation is how a freeze becomes decorative.

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

1. **It is FROZEN, and it still authorises no compute in the dispatch that froze it.**
   §9.1's condition has never been evaluated in a launching invocation, and §9.3's
   grading wrapper does not yet exist. **A freeze is a permission to be GRADED AGAINST.
   It is not a permission to LAUNCH.**
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

**Drafted and FROZEN 2026-08-25 by a cfd `lab-lane` at the cfd supervisor's direction, in
TWO SEPARATE DISPATCHES, neither of which spent a core-minute.
ZERO SOLVER COMPUTE: no solver, no mesher, no `checkMesh`, no case directory, no MPI rank.
FROZEN. `PENDING` — rule 1's display state, "not yet run", never a softened verdict.
SUBMISSIONS PARKED: nothing here is sent, filed, uploaded, registered, posted or
commented outside this box.**
<!-- FROZEN-BODY-ENDS-HERE -->

---

## AMENDMENT 1 — 2026-08-25 — PRE-COMPUTE. The §9.3 grading wrapper, its hashes, and the hazard it was written under.

**Document version 1.0 → 1.1.**
**Lines whose number changed above this section: 0.**
*(Verified mechanically, not asserted: everything above the `FROZEN-BODY-ENDS-HERE`
marker is byte-for-byte the document frozen at commit `5b6b1ece`, sha256
`9989f1f909b358ae30c663b041598358cf247f6aee2a8b3dcb6bda99543a30cc`. The comparator
hashes the body ABOVE the marker, not the whole file — so a legal amendment can never
make the frozen text un-verifiable, and no future lane is quietly pressured to skip an
amendment to keep a hash green.)*

### A1.0 THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**This is a BEFORE-FIRST-COMPUTE amendment and is legal only because of that.**
Rule 2: before first compute, amendments are legal **and must state the condition and
how it was checked, naming the run directory that does not exist.**

> **CONDITION: no solver has run under this document.**
> **CHECKED BY `test -e` IN THE AMENDING SHELL INVOCATION, on both registered roots:**
> * `/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs` — **ABSENT**
> * `/home/ubuntu/certonomous-runs/f6a-greenblatt-baseline` — **ABSENT**
>
> The amendment aborts before writing a byte if either exists. **That check is still
> not the launch check**: §9.1's `test -e` is evaluated in the LAUNCHING invocation.

**THIS AMENDMENT ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL**, and it cannot:
§2.2, §2.3, §3.1, §3.2, §5.5 and §8.5 specify the arithmetic, the thresholds, the
ordering and the cap completely in the frozen body. Everything below is an
**IMPLEMENTATION of gates already frozen.** `--show-frozen` on both scripts prints
every transcribed constant for a line-by-line diff against the body above.

### A1.1 THE ARTIFACTS, PINNED

| role | path | sha256 | git blob |
|---|---|---|---|
| **grading wrapper** | `scripts/f6a_greenblatt_gate.py` | `b251333b0a6bac6fb9191f41eb67594de12e6baabc4c81dd1213c1d71dd9038b` | `d58486695b8b2d1b7e17cae98f460fb38e2c3fe3` |
| **launcher** | `scripts/run_f6a_greenblatt.py` | `461bc34dc82f0af6b9bcc7996aa4466872d6fcb72539b277376aecee325f3781` | `3c40023ce298f8119f2b80698711d9f8e72d7c75` |
| **mutation controls** | `scripts/f6a_greenblatt_selftest.py` | `3b131218f4baf38a9724b8ce928ce4391032aa6df7d3cdc7545df48e3d13dcd9` | `289f429bf5504e7673ec4be6947f818a5521f3a5` |
| **extraction path** *(unchanged, re-affirmed)* | `cases/dafoam/f6a_nasa_hump/case/hump_gate_analysis.py` | `9a6ec8553b863b3b43a1a3ca03970923778f7da5c2bf3e1cfacdfa8f6fd2414f` | `ec263bed8623a81b67106c3880febdca1b3d5eff` |

**WHY THESE LIVE IN `scripts/` AND NOT UNDER THE RUN ROOT.** The family convention
puts a comparator beside its run (`verification/runs/F12_runs/run_f12_rung.py`).
**Following it here would have destroyed §9.1.** The run root
`verification/runs/F6a_GREENBLATT_runs` is a directory this document requires **not to
exist** at launch; creating it to hold a script would trip §9.2's guard permanently and
kill the campaign. `scripts/` is the filing charter's home for `lower_snake.py` and
costs the guard nothing. **The convention was departed from to keep a frozen condition
evaluable, and the departure is recorded rather than quietly taken.**

### A1.2 THE HAZARD, NAMED — because the structure does not obviously guard it

> **THE WRAPPER WAS WRITTEN WITH `1.2531` ALREADY KNOWN.**

**The risk is NOT that a gate moves.** The gates are frozen with explicit numbers and
the wrapper only transcribes them. **The risk is that an AMBIGUOUS CLAUSE GETS
IMPLEMENTED IN THE DIRECTION OF THE EXPECTED ANSWER** — nudged, not falsified, by a
lane that knows what the run will say.

**Three things blunt it, and they are stated as doing so rather than left implicit:**

1. **THE EXTRACTION PATH IS PINNED BY HASH.** The code that actually produces `x_r/c`
   and `x_s/c` is frozen, invoked as a subprocess, never edited and never
   re-implemented. A one-byte drift refuses (control `rule 2 / §9.3 FAIL`).
2. **§3's CLAUSES CARRY EXPLICIT NUMERIC THRESHOLDS** — peak-to-peak ≤ **0.0055** /
   **0.0033**, at most **one** sign alternation across **10** samples, initial
   residuals **U/p/k 5e-7, omega 1e-10**. There is little room to implement a number
   "in a direction".
3. **EVERY CLAUSE CARRIES A CONTROL THAT MUST FAIL** (§A1.4). A clause that cannot be
   made to refuse is a clause that cannot bind.

**AND THE ONE PLACE THE FROZEN TEXT LEFT A GENUINE CHOICE, declared rather than
buried.** §2.2 defines separation as *"the FIRST crossing downstream of the hump
crest"* and **gives the crest no number.** The extractor reports four sign crossings on
this case, two of them spurious near `x/c ≈ 0`; where the crest is put decides which
pair is graded.

> **RESOLVED FROM GEOMETRY ALONE: the crest is the x of MAXIMUM WALL HEIGHT, read from
> the case's own wall sample.** On the shipped mesh this measures **x/c = 0.51466** at
> `z_max = 0.053751`.
>
> **WHY THIS CANNOT BE ANSWER-DIRECTED:** wall height is a property of the **MESH**. It
> does not depend on the solution, on `Cf`, or on any closure; it is identical for
> every run of this case; and it is computed **before any crossing is examined**. It
> cannot be tuned toward 1.2531 or away from it.
>
> **AND IT IS LOAD-BEARING, NOT DECORATIVE** — proved, not asserted: with the crest
> removed the same reader returns the **spurious** pair `(−0.01290, +0.00717)`
> (control `§2.2 FAIL`).

### A1.3 TWO DEFECTS THE CONTROLS CAUGHT IN THIS LANE'S OWN CODE, recorded because a control that never caught anything is not evidence that the code was right

1. **A STALE DEFAULT ARGUMENT IN THE §9.2 DIRECTORY GUARD.** `freeze_condition` was
   written `def freeze_condition(roots=RUN_ROOTS)`. A default binds the module global
   **once, at definition** — so the guard checked a captured tuple rather than the
   live one. **The guard passed while pointing at the wrong directories.** In
   production the two coincide and nothing would have been observed; the control
   exposed it because it redirected the roots. `roots` is now resolved **at call
   time**.
2. **A PLANTED-ZERO WINDOW THAT WAS WRONG IN THE REFUSING DIRECTION.** The §3.3
   control first required the recovered crossing to lie **within** the flipped block
   `[lo, hi]`. A sign crossing is **interpolated between the last unflipped sample and
   the first flipped one**, so it lands **one sample spacing outside** that block. The
   control refused a reader that had demonstrably seen the plant (crossings **4 → 6**).
   **A control that is wrong in the refusing direction is still wrong**, and it was
   corrected to **bracket** the block — never loosened by a fudge factor.

### A1.4 THE MUTATION CONTROLS — **42 controls, 0 failures, across 18 frozen clauses; every clause carries BOTH arms**

`python3 scripts/f6a_greenblatt_selftest.py` → **`SELFTEST PASSED`**. The standard is
**N-T8** (`docs/NUMERICS_KNOWLEDGE.md` at HEAD — *the worktree copy of that file does
not contain N-T8*): a control must check the **VALUE**, by construction, not that a key
exists. **VMFL045 is the second form of the same disease** — 45/45 with real negative
controls, and it could never have caught its own crash. **A selftest that only ever
passes proves the grader, not the case.** The file **fails** if any clause lacks a
failing arm.

| frozen clause | the FAIL arm, and it must actually flip |
|---|---|
| **§3.1 (P-a)** | a run that **reached the iteration cap** instead of tripping `residualControl` → refused; `converged_at == cap` also refused |
| **§3.1 (P-b)** | a reader pointed at **Final** rather than **Initial** → refused, **and the mutated Final-reading comparator PASSES the same log** — the confusion this exact case has already paid for once (`F6a_epistemic_band.md`'s 1.0722) |
| **§3.1 (P-c)** | a **still-drifting** functional → NOT PLATEAUED; fewer than 10 samples → **REFUSAL** |
| **§3.1 (P-d)** | an **oscillating** series (8 alternations) → refused — VMFL051's shape, whose deviation still read like a `PASS` |
| **§3.2** | **an identical dead-centre deviation grades `PASS` when plateaued and `NOT A RESULT` when not.** The gate turned a `PASS` **into** `NOT A RESULT`, never the reverse |
| **§3.3** | a **blind reader** — one returning the same answer whatever is on disk — → **REFUSAL**; the plant is by **line index** |
| **§5.5** | **Gate M fails → the launcher returns exit 4 and NO `simpleFoam` or `mpirun` command is invoked at all**, asserted by recording every command the launcher issues |
| **§9.2** | an **existing** run directory → exit 3, **0 commands run, no case built** |
| **§8.5** | the naive `timeout 1800` is **4× the correct 450 s**; `ranks = 0` and an over-large reserve both raise |
| **§9.4** | a field **older than `0/U`** → the **age guard** refuses; `rc ≠ 0`, no `End`, `last ≠ endTime`, a missing field — each refused |
| **§2.2** | without the crest the reader returns the **spurious** pair |
| **§4** | the no-triple scan is shown able to **SEE** a planted GCI/Richardson block |
| **§2.3 / §2.1** | **grading on the REPORTED oil-film limb would FLIP `GATE FAIL` to `PASS` at `x_r/c = 1.16`** — so the code demonstrably used the **gated** band and the reported channel is genuinely non-binding |
| **rule 1** | a mutated comparator emitting *"roughly converged"* → **REFUSAL**. *(This control found a real gap: only the headline verdict was vocabulary-checked, so a hedge reached the per-gate cells. `grade()` now checks **every** cell.)* |
| **rule 2 / §9.3** | a **one-comment drift** in the extraction script → **HASH MISMATCH** → the campaign stops |
| **rule 14** | an **active** top-level `libs` entry → **REFUSAL**, never silently replaced |
| **§3.1 (P-c) install** | a `controlDict` the sampling install cannot fully patch → **REFUSAL**, rather than launching a run that cannot produce 10 samples |
| **zero-compute** | the selftest asserts **both registered run roots are still ABSENT** when it finishes |

### A1.5 THE CROSS-FAMILY DEPENDENCY, NAMED SO A FUTURE READER KNOWS WHY AN F6a CAMPAIGN COULD HALT

> **The pinned extraction path lives in DAFOAM'S TERRITORY, not cfd's:**
> `cases/dafoam/f6a_nasa_hump/case/hump_gate_analysis.py`, blob
> **`ec263bed8623a81b67106c3880febdca1b3d5eff`**.

**cfd does not reach into another team's tree and has not.** The hash pin means a
dafoam-side edit is **CAUGHT rather than absorbed** — and under §9.3's standing clause
the campaign then **STOPS**, which is the right failure mode and not a defect. **But it
is a genuine cross-family coupling and it is escalated, not resolved here.** Twenty-three
byte-identical copies of this file exist across the tree; the pin names one.

### A1.6 WHAT THIS AMENDMENT STILL DOES NOT DO

1. **It authorises no compute.** §9.1's condition has not been evaluated in a launching
   invocation. **No mesh has been built, no `checkMesh` run, no case directory created,
   no solver started.**
2. **It moves no gate, threshold, cap or label**, and by §A1.0's construction it could
   not.
3. **It does not verify the wrapper against real solver output**, because none exists.
   The clauses are exercised against synthetic fixtures and against the **real** wall
   data of the C-45 run for §3.3. **If the case's actual output does not match the
   contract the wrapper asserts, the comparator REFUSES (exit 2) and the campaign
   stops — the clause is not relaxed to match the code.**
4. **It sends nothing. SUBMISSIONS ARE PARKED.**

**Amended 2026-08-25 by a cfd `lab-lane` at the cfd supervisor's direction.
PRE-COMPUTE. ZERO SOLVER COMPUTE. The frozen body above is untouched.**

---

## ADDENDUM 2 — 2026-08-25 — **RULING 1 (cfd supervisor).** A SECOND run root is registered for attempt 2. The §9.1 registration stands verbatim. NOTHING IS DELETED.

**Document version 1.1 → 1.2.**
**Lines whose number changed above this section: 0.** *(Append-only; the frozen body
above the `FROZEN-BODY-ENDS-HERE` marker is untouched and still hashes to
`9989f1f9…`. Amendment 1 is likewise untouched.)*

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Gates P1 and P2,
their bands `[0.63175, 0.69825]` and `[1.045, 1.155]`, Gate M's ≤ 70° / ≤ 4, the
plateau clauses (P-a)–(P-d), the 30 core-min cap, the ±5 % model-form tolerance and
every `REPORTED — NOT A GATE` label stand **verbatim and unchanged**.

### A2.0 What happened, in one line

**ATTEMPT 1 returned `BLOCKED`.** Gate M `PASS` (40.5495° / 0.743352, reproducing §5.2
exactly), then §6.3's smoke test aborted the campaign on a `FOAM FATAL`. **The graded
solver never started.** Full record: `verification/runs/F6a_GREENBLATT_runs/baseline_Re936k/result.json`,
committed `fbe99573`.

> **AND THE SENTENCE THE SUPERVISOR REQUIRED IN THE RECORD VERBATIM:**
>
> **THE SMOKE TEST DID NOT TEST THE CASE.** It crashed on an empty dictionary of its
> own making — the launcher's `open(p,"w")` truncated the file before reading it.
> **No conclusion about the case's dictionary completeness may be drawn from attempt 1
> in either direction, and the VMFL045 failure class remains UNTESTED here.**
>
> **If anyone later reads attempt 1 as evidence that the case is sound, that reading is
> wrong, and this record forbids it.**

### A2.1 THE RULING

> **PRESERVE THE ATTEMPT-1 TREE. REGISTER A SECOND, DIFFERENTLY-NAMED RUN ROOT FOR
> ATTEMPT 2. DELETE NOTHING. RENAME NOTHING.**
>
> **REGISTERED FOR ATTEMPT 2:**
> `/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs/attempt2_Re936k`
> — **verified ABSENT by `test -e` in the amending invocation**, and to be re-verified
> by `test -e` **in the launching invocation**.
>
> **STILL REGISTERED AND STILL MUST NOT EXIST:**
> `/home/ubuntu/certonomous-runs/f6a-greenblatt-baseline`.
>
> **§9.1's ORIGINAL REGISTRATION AND ITS "BOTH VERIFIED ABSENT" ASSERTION STAND
> VERBATIM** as the historical record that the case was unfired at freeze. The new root
> is added **beside** them, never in place of them.

**Both options the lane was offered were refused, and the reasons are recorded because
they generalise:**

* **Deleting the tree: REFUSED OUTRIGHT.** It carries the Gate M measurement and the
  launcher-defect evidence. **You do not delete a measurement to make room for a nicer
  one.** ansys-verification refused exactly this on VMFL051 and cfd upheld them; cfd
  does not now do the thing it praised them for refusing.
* **Renaming or repurposing the §9.1 path: REFUSED.** That assertion is the historical
  record that the case was unfired at freeze, and **it stays true by staying untouched.**

### A2.2 WHY THIS IS LEGAL — and the reasoning does not rest on §2d being unengaged

1. **A run directory is NONE of rule 2's four protected items.** It is not a gate, a
   threshold, a cap or a label. **Even read as post-compute**, rule 2 permits a dated
   addendum that alters none of the four, and this one alters none.
2. **THE HAZARD §9.2 EXISTS TO PREVENT IS NOT PRESENT HERE, AND THIS IS THE DECISIVE
   POINT.** §9.2 guards against **re-running until you like the answer**.
   **NO GRADED QUANTITY EXISTS.** The graded solver never started: there is no `x_r/c`,
   no `x_s/c`, no `Cf`, no crossing and no coefficient — **nothing that could make a
   re-launch answer-directed, because there is no answer.**
3. **AND THAT WAS SHOWN, NOT ASSERTED.** The preserved tree was enumerated exhaustively
   before this addendum was written:

   | probe | result |
   |---|---|
   | time directories beyond `0/` | **NONE** |
   | `processor*` directories | **0** — decomposition never ran |
   | solver logs | **NONE** (`log.checkMesh` only) |
   | `postProcessing/`, `*.raw`, `gate_result*`, `cf_xc*`, `cp_xc*`, `*.dat`, coefficients | **NONE** |
   | `0/` vs the shipped case | **byte-identical** (`diff -rq` clean) |
   | files written by the attempt | **3** — `log.checkMesh`, `result.json`, `system/controlDict` (the §3.1 (P-c) sampling install) |

   *(The one `wallValues` path in the tree is `system/wallValues` — the shipped
   function-object DICTIONARY, an INPUT, not output.)*

   **Total: 46 files, all of them inputs, one mesh-quality log, and this lane's own
   record. No graded quantity of any kind.**
4. **EXACTLY ONE BEHAVIOURAL CHANGE BETWEEN ATTEMPT 1 AND ATTEMPT 2** — the VMFL051-R2
   discipline. Auditable by `git diff 3017eb4c HEAD -- scripts/run_f6a_greenblatt.py`:
   * **the `open(p,"w")` truncation bug**, replaced by `rewrite_file()`, which reads
     fully and refuses to write empty content. **This is the only logic change.**
   * *(mandated by this addendum)* the launcher's registered run root, per §A2.1.
   * *(documentation only, zero behavioural diff)* one stale sentence in
     `rewrite_file`'s docstring said the selftest *"greps the source"* — true of the
     control's first form, false of the AST walk that replaced it. **Corrected rather
     than left standing, because a knowingly false sentence in code is worse than an
     extra line in a diff.**
   * **`scripts/f6a_greenblatt_gate.py` is BYTE-IDENTICAL to attempt 1** — verified by
     blob comparison, not by inspection.

**WHAT IS EXPLICITLY NOT RELIED UPON, recorded as raised and unused.** §6.3's smoke-test
solver ran in a scratch directory **outside every registered path**, which is an
argument that rule 2's post-compute clause was never engaged at all. **This ruling
deliberately does NOT rest on that**, because the attempt-1 run root **does** now exist
and that is the fact §9.2 keys on. **The ruling stands on grounds 1 and 2, which hold
either way. If verification later rules the post-compute clause engaged, this
disposition is unaffected.**

### A2.3 The preserved tree is now an EXECUTABLE assertion, not a promise

> The launcher **asserts that
> `verification/runs/F6a_GREENBLATT_runs/baseline_Re936k` STILL EXISTS** and refuses to
> launch attempt 2 if it does not.
>
> **"Do not delete the evidence" is thereby a check the code performs rather than a
> discipline the lane remembers.** Attempt 2 cannot run on a tree where attempt 1's
> proof has been cleared away.

---

## ADDENDUM 3 — 2026-08-25 — **RULING 2 (cfd supervisor).** §3.1 (P-a) GOVERNS; §9.4's endTime equality is read as the legitimate termination time.

**Document version 1.2 → 1.3. Lines whose number changed above this section: 0.**

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Every band, the
30 core-min cap and every label stand verbatim.

### A3.1 The contradiction, stated in the frozen text's own terms

| clause | requires |
|---|---|
| **§3.1 (P-a)** | `SIMPLE solution converged in N iterations` with **N < the endTime cap**. Reaching the cap is **not** convergence. |
| **§9.4** (importing `CLAUDE.md` rule 4) | **last time == `endTime`** |

**Against the controlDict literal `endTime 2000`, a run converging at 1772 CANNOT
SATISFY BOTH.** C-45 converged at 1772. **The frozen text cannot be satisfied on both
readings at once**, and the conflict surfaced twice unresolved before it was ruled.

### A3.2 THE RULING

> **§3.1 (P-a) GOVERNS. §9.4's endTime limb is read as *"last time == the time at which
> the run LEGITIMATELY TERMINATED"*, which for a `residualControl` run is its
> CONVERGENCE ITERATION.**
>
> **This is the SUPERVISOR'S INTERPRETATION and is marked as such so it can be
> overturned.** Both readings are disclosed here and the comparator prints both into
> every record it writes.

**The reasoning, with the second point deciding it:**

1. **Rule 4's endTime equality exists to catch a run that DIED EARLY**, and its real
   discriminators are `rc = 0`, the `End` line, field presence and the age guard — **all
   of which a converged run satisfies.** The clause was written for fixed-`endTime`
   thermal runs and imported here without noticing that this case terminates on a
   **criterion** instead.
2. **THE LITERAL READING MAKES §3.1 (P-a) UNSATISFIABLE — AND WORSE, IT INVERTS BOTH
   CLAUSES: a CONVERGED run would FAIL, while a run that burned to the cap without
   converging would PASS.** That is precisely what (P-a) refuses. **A reading that makes
   a sibling frozen clause unsatisfiable, and that admits exactly what that sibling
   rejects, is the wrong reading.**
3. **IT IS VERDICT-NEUTRAL, AND THAT WAS CHECKED BEFORE RULING RATHER THAN AFTER.** The
   forecast is `GATE FAIL` at **+13.918 %**. This resolution decides whether the run can
   be **graded at all**; it does not move the verdict toward `PASS`. **Had it favoured a
   `PASS`, the supervisor's stated position is that he would have REFERRED it rather
   than ruled it.**

### A3.3 The mechanism, which is a solver fact and not a grading choice

On convergence `simpleControl::loop()` calls `runTime.writeAndEnd()`, which **sets the
run's endTime to the current time**. The run's **effective** endTime therefore IS the
converged iteration, and *last time == endTime* holds against it. **(P-a) independently
gates that the termination was a genuine `residualControl` trip and not a cap hit**, so
nothing is loosened by reading it this way — and a control asserts the reconciliation
**cannot launder a cap-hit into a convergence**: on a run that reached 2000 the effective
endTime is 2000 and **(P-a) still refuses it.**

### A3.4 THE UNDERLYING DEFECT, named plainly — it is about the CLAUSE, not only this document

> **`CLAUDE.md` rule 4's completion clause ASSUMES A FIXED-`endTime` RUN AND DOES NOT
> FIT A CRITERION-TERMINATED ONE.** Any campaign whose solver stops on `residualControl`
> inherits this contradiction the moment it also gates on convergence.
>
> **The next pre-registration in this family should register its completion rule in
> terms of LEGITIMATE TERMINATION rather than importing the endTime equality
> unexamined.** That is a finding about the clause and is recorded as one. **Retiring or
> rewording a `CLAUDE.md` rule is not cfd's to do** — it is noted here and referred.

**Amended 2026-08-25 by a cfd `lab-lane` on the cfd supervisor's two rulings.
PRE-LAUNCH for attempt 2. The frozen body and Amendment 1 are untouched.
SUBMISSIONS PARKED.**

---

## ADDENDUM 4 — 2026-08-25 — **RULING 1 (cfd supervisor).** Attempt 2's `rc` limb was INFERRED, not measured. **The row is `NOT A RESULT`. The `P` column is `PENDING`, NOT green.** A third run root is registered.

**Document version 1.3 → 1.4. Lines whose number changed above this section: 0.**
**ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.**

### A4.1 THE RULING, and it costs this team the headline

**Attempt 2 returned every gate the forecast predicted** — Gate M `PASS`, P1 `PASS` at
−1.5923 %, P2 `GATE FAIL` at **+13.9485 %**, plateau HOLDS, all seven §10.2 predictions
correct. **And it is `NOT A RESULT` anyway.**

> **`rc = 0` WAS INFERRED, NOT MEASURED, AND RULE 4 IS ALL-OR-NOTHING BY DESIGN.**
> Four limbs were measured — the `End` line, `last time == endTime 1813` under
> Addendum 3, all five fields present, and the age guard (`0/U` 03:00:39Z against
> `1813/U` 03:02:05Z). **The fifth was not.** The launcher captured the solver exit
> code in memory and then crashed on a typo in its own reporting line
> (`effective_endtime` vs `effective_endtime_used`) before writing it out.
>
> **AN INFERRED LIMB IN AN ALL-OR-NOTHING RULE IS A DEGRADATION, AND THIS LAB'S
> COMPARATORS REFUSE RATHER THAN DEGRADE.**

**Four grounds, the fourth decisive:**

1. **Rule 4 is not a checklist satisfied on balance.** It is **conjunctive** precisely so
   no limb can be carried by the others. An inference resting on the `End` line and the
   absence of `FOAM FATAL` is an argument **from the other limbs** — which is exactly
   what conjunctivity forbids.
2. **Standing rule 3 applies by analogy and bites hard.** *A zero from a reader not
   shown able to see a non-zero is not evidence.* **The reader crashed before it could
   report at all**, so nothing demonstrates it could have distinguished `rc = 1` from
   `rc = 0`. **That is an unplanted zero in a different currency.**
3. **The precedent is permanent and asymmetric.** This would be the lab's **first green
   `P` cell in 153 rows** and it **will be quoted**. A first-ever credential carrying an
   inferred limb teaches every future completion check that the awkward limb may be
   **reasoned rather than read**.
4. **THE DEFECT IS IN OUR LAUNCHER, NOT THE CASE — AND WE DO NOT LOWER AN EVIDENTIARY
   STANDARD TO COMPENSATE FOR OUR OWN TOOLING BUG.** That is the identical principle to
   *the clause is not relaxed to match the code*, upheld twice already in this campaign.
   **It would be incoherent to apply it to the case and exempt ourselves.**

**The cost of refusing is ~6.1 core-minutes and about half a cent, on a case that has
now demonstrated end to end that it works. The trade is not close.**

### A4.2 WHAT THIS DOES AND DOES NOT SAY

> **IT DOES NOT SAY THE NUMBER IS WRONG.** **+13.9485 % is almost certainly right and
> will very likely reproduce.** All seven §10.2 predictions came back correct; the fresh
> solve landed at **1.25343**, the 1.2534 reading §10.1 quoted while gating against
> neither; and the finding is robust to the limb at **+13.9485 % PIV / +12.9219 %
> oil-film**, both `GATE FAIL`.
>
> **IT SAYS THE ROW IS NOT YET A CREDENTIAL.**

> **AND THE CONSEQUENCE THAT IS NOT SOFTENED: THE `P` COLUMN IS *NOT* GREEN.**
> A `NOT A RESULT` row has **no admissible measurement**, and a `P` cell certifies a
> comparison that **actually happened**. **`P` is `PENDING` — rule 1's display state,
> "not yet run" — until attempt 3 lands.** **This team does not keep a green cell earned
> under a limb it just refused**; that would be exactly the flattering reading this lab
> exists to refuse.

### A4.3 ATTEMPT 3 — registered, with ONE change

> **REGISTERED FOR ATTEMPT 3:**
> `/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs/attempt3_Re936k`
> — **ABSENT by `test -e` in the amending invocation**, to be re-verified in the
> launching one. `/home/ubuntu/certonomous-runs/f6a-greenblatt-baseline` remains
> registered as must-not-exist.
>
> **ATTEMPT 1'S AND ATTEMPT 2'S TREES ARE BOTH PRESERVED — undeleted, unrenamed, and
> now BOTH asserted by the launcher**, which refuses to start if either tree or its
> evidence is gone.

**Ruling 1's legality grounds hold again, and the reason is worth stating exactly:
attempt 2's graded quantity does NOT license a re-run aimed at a different answer.
Attempt 3 re-runs to MEASURE A LIMB.** The gate, the bands, the cap and every label are
untouched, and the predicted answer is the one already in hand — **an unchanged
`GATE FAIL` at ≈ +13.9 % is the expected and desired outcome.** A materially different
number would itself be a finding to investigate, not a result to prefer.

**EXACTLY ONE CHANGE, and it is not a gate:** the solver exit code is **PERSISTED TO
DISK IMMEDIATELY ON CAPTURE**, fsync'd, **before any reporting, formatting or
f-string**, and the comparator reads it **from disk** via `--rc-file`. **A value held
only in memory until a reporting line runs is a value one typo from unrecoverable** —
which is precisely what happened. **A missing or non-integer `rc` file is REFUSED, never
inferred**, and two controls prove both refusals fire.

**Gate M is re-evaluated from scratch on attempt 3. Attempt 2's PASS is NOT carried
forward.** **The 30 core-min cap is CUMULATIVE and stands: 6.15 spent, 23.85 remaining.**

### A4.4 WHY NO CONTROL CAUGHT THE TYPO — **L-316's shape, cited as its author's**

> **The 51 mutation controls covered the FROZEN CLAUSES, not the launcher's post-solve
> REPORTING GLUE — which cannot be exercised without a real solve.**

That is **`L-316`**'s finding, and it is **ansys-verification's**, cited as theirs and
**no lesson is assigned from it here**: *a comparator `--selftest` proves the GRADER,
never the CASE or the LAUNCHER*. **It caught this lane on precisely the path L-316
names.** The repair is not a bigger selftest: it is **persisting the value at the moment
of capture**, so no reporting path can lose it.

**Amended 2026-08-25 by a cfd `lab-lane` on the cfd supervisor's Ruling 1.
PRE-LAUNCH for attempt 3. The frozen body and Amendments 1–3 are untouched.**

---

## ADDENDUM 5 — 2026-08-25 — **CAMPAIGN CLOSURE (cfd supervisor, option 3).** Row `NOT A RESULT`. Nothing further launches under this pre-registration.

**Document version 1.4 → 1.5. Lines whose number changed above this section: 0.**
**ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.**

### A5.1 THE ROW

> **VERDICT `NOT A RESULT`. TIER `NOT HELD`. `P` COLUMN `PENDING`, NOT GREEN.**
>
> A `NOT A RESULT` row has **no admissible measurement**, and a `P` cell certifies a
> comparison that **actually happened**. `PENDING` is rule 1's display state — *"not yet
> run"* — never a softened `GATE FAIL`.

**No fourth attempt is authorised and none was taken.** Three run trees stand preserved,
undeleted and unrenamed: `baseline_Re936k` (attempt 1, `BLOCKED`), `attempt2_Re936k`
(complete solve, voided on an unmeasured limb), `attempt3_Re936k` (complete solve,
`NOT A RESULT` on (P-a)).

### A5.2 EVERY ROUTE OUT WAS REFUSED, AND THE REASONS DIFFER

**Option 1 — fix the decomposition: REFUSED. The `REFERENCE_DIR` analogy breaks on the
one fact that ruling turned on.** F12's `REFERENCE_DIR` repair was ruled in scope because
it was made when **NO ANSWER EXISTED** — F12 was unfired, nothing had been measured, and
the repair **could not have been aimed**: *"found with zero compute, which is the only
reason it cost nothing."*

> **HERE, THREE RUNS HAVE BEEN OBSERVED AND THE DISTRIBUTION IS KNOWN: TWO OF THREE
> PARTITIONS CONVERGE.** Any change to the decomposition is now made **with the outcome
> distribution in hand**, and that is precisely the knowledge that makes an intervention
> **answer-directed — even when the mechanism is innocent and the intent is honest.**

**Option 2 — raise `endTime`: REFUSED. It changes a threshold.** **And loosening omega's
control is refused on identical grounds**, named explicitly here because it is the
obvious next suggestion.

**Option 3 — accept `NOT A RESULT` and record the finding: TAKEN.**

**The lane's refusal to re-run is upheld without qualification.** Its reasoning stands as
the campaign's best argument: *a re-run is not neutral merely because the gate VALUE
would be unchanged, because it would move the row verdict from `NOT A RESULT` to
`GATE FAIL`, and the row verdict IS the verdict.* **Rule 5's one-way door is not a
technicality about values — it is about what the row ASSERTS. A row that says "we could
not measure this" and a row that says "we measured it and it failed" are different claims
about the world.**

### A5.3 THE FINDING — and it locates a defect in this lab's instruments, not in this case

**`scotch` decomposition is NOT DETERMINISTIC between invocations.** On a **byte-identical**
mesh, `0/` directory and `system/controlDict` (`diff -rq` clean):

| run | partition (first three ranks) | converged | omega initial residual |
|---|---|---|---|
| C-45 | *(not recorded)* | at **1772** | — |
| attempt 2 | **12777 / 12906 / 12965** | at **1813** | **9.94318e-11** — met, by **0.568 %** |
| attempt 3 | **12974 / 12870 / 12865** | **NO — hit the 2000 cap** | **4.63816e-10** — **4.638× the control** |

Different partition → different parallel summation order → different round-off →
different residual trajectory.

**AND THE SHARPER FORM, WHICH LOCATES THE DEFECT:**

> **THE BINDING CHANNEL IS `omega` ALONE, AND ITS CONTROL IS `1e-10` WHILE EVERY OTHER
> CHANNEL IS `5e-7` — FIVE THOUSAND TIMES TIGHTER.** At attempt 3's cap, Ux 2.89e-8,
> Uz 5.92e-8, p 5.78e-8 and k 8.32e-8 were all comfortably inside `5e-7`. Only omega was
> not.
>
> **A CRITERION MET BY 0.568 % ON ONE RUN AND MISSED BY 4.638× ON THE NEXT, ON A
> BYTE-IDENTICAL CASE, IS NOT MEASURING CONVERGENCE — IT IS MEASURING THE PARTITION.**
>
> **The defect is in the frozen case's RESIDUAL CONTROLS — not in the solver, not in the
> mesh, not in the physics.** That is a finding about **this lab's instruments across
> every parallel case it runs**, and **no passing row would ever have surfaced it.**

### A5.4 THE ASSET THIS CAMPAIGN ACTUALLY PRODUCED — a reproducibility measurement, independent of any gate

**The graded quantity is stable. The convergence criterion is not.** Two independent runs
with **different partitions**:

| quantity | attempt 2 | attempt 3 | spread |
|---|---|---|---|
| separation x_s/c | 0.6544112 | 0.6544109 | **3e-7 in x/c** |
| reattachment x_r/c | 1.2534333 | 1.2534550 | **2.17e-5 in x/c** |

**2.17e-5 in x/c is 0.0017 % of the value and 3.95e-4 of Gate P2's half-width.** This is
a **genuine reproducibility measurement of the case, independent of any gate**, and it is
the most useful number the campaign produced. **It is recorded here as a measurement in
its own right, not as a footnote to a failed row.**

### A5.5 THE PHYSICS FINDING IS UNAFFECTED — the row is not a credential; the number is not in doubt

**Had the row been gradeable it would have been `GATE FAIL`**, and by the same margin on
either limb of Table 2:

* against the gated 2-D PIV centerline limb **1.10**: **+13.9485 %**
* against the REPORTED oil-film limb **1.11**: **+12.9239 %**

**Both `GATE FAIL`, reproduced across two independent partitions.** §2.1's frozen
robustness statement — *the instrument choice cannot flip the verdict* — is now
**measured**, not argued.

> **THE ROW IS NOT A CREDENTIAL. THE NUMBER IS NOT IN DOUBT.** Those are two different
> statements and this document has kept them apart from §0 onward.

### A5.6 REAL GAINS, recorded as gains

1. **ALL FIVE RULE-4 LIMBS MEASURED AND PASSING on attempt 3** — `rc = 0` read **from
   disk**, the `End` line, `last time == endTime 2000`, all five fields present, and the
   age guard. **Addendum 4's repair worked exactly as designed.**
2. **THE SMOKE TEST FINALLY TESTED THE CASE** — rc = 0, no `FOAM FATAL`. **The VMFL045
   dictionary-completeness class is GENUINELY EXERCISED for the first time in this
   campaign**, having been explicitly **untested** at attempt 1, where the smoke test
   crashed on an empty dictionary of its own making.
3. **Gate M `PASS` on all three attempts**, re-evaluated from scratch each time, never
   carried forward — 40.5495° and 0.743352, reproducing §5.2 exactly.

### A5.7 THE ROUTE TO A CREDENTIAL — named, NOT walked, NOT authorised, NOT costed

> A **NEW** pre-registration whose convergence criterion is **calibrated on a stated
> principle** — omega's control set on the **same basis as the other four channels** —
> and whose **decomposition is deterministic**.
>
> **It must disclose everything now known**: three observed runs, the partition
> non-determinism, the 0.568 % margin, and the reattachment value already in hand. And it
> must **derive its criterion FROM PRINCIPLE rather than to fit** — exactly as this
> document inherited `74797a57`'s ±5 % rather than deriving a band with the answer
> available.
>
> **NOT AUTHORISED BY THIS DOCUMENT. NOT COSTED. NOT WRITTEN.**

### A5.8 Cost at closure

**Campaign cumulative 13.3965 core-min against the 30 core-min CUMULATIVE cap; 16.6035
remain unspent.** Ledger rows **C-59** (attempt 2) and **C-60** (attempt 3).

**WASTE IS NAMED SEPARATELY AND LEFT VISIBLE, NEVER ABSORBED INTO A RATIO:** attempt 1
**≤ 0.017 core-min** (bounded) **and attempt 2's FULL 6.1333 core-min** — a complete
solve voided on an unmeasured limb, **attributable to a launcher defect, not to the
case**. **That is the honest cost of Ruling 1 and it belongs on the record.**

**The contention finding is now a TWO-ROW result and is stated as one:** loadavg 2.02 at
attempt 3's launch, contention **absent again**, **1.05× against the uncontended
subtotal**. **Two rows agree the ×1.0 allowance is the ENTIRE headline miss** — it must be
**conditioned on measured load at launch, not applied blind.**

**Closed 2026-08-25 by a cfd `lab-lane` on the cfd supervisor's option-3 ruling.
NOTHING FURTHER LAUNCHES UNDER THIS PRE-REGISTRATION.
The frozen body and Amendments 1–4 are untouched. SUBMISSIONS PARKED.**
