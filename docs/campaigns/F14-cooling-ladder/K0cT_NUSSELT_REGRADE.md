# K0cT. Nusselt re-grade against Betts and Bokhari Table 1

Campaign F14, gate K0c, turbulent tall-cavity rung. **Written 2026-08-18, after
`K0cT_RESULTS.md`, and it changes that rung's verdict on one quantity.**

> **THIS IS A VERDICT CHANGE TO AN ALREADY EXECUTED RUNG.** `K0cT_RESULTS.md`
> reported the Nusselt number as an explicitly **UNGRADED** measurement because
> its reference was NOT OBTAINED. The reference arrived later the same day. The
> Nusselt rows are graded here and the verdict is **GATE FAIL**.
>
> **`K0cT_RESULTS.md` was not edited** (W-4). It stands as executed, and its
> Section 6 remains a correct account of what was knowable when it was written.
> This document supersedes it on one quantity, by date, and names which.

Comparator: `verification/runs/F14-cooling-ladder/K0cT_runs/regrade_nusselt.py`.
Machine-readable output: `regrade_nusselt.json` beside it. The comparator holds
no reference number of its own; it parses every one from addendum A1 of
`K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` and refuses (exit 2) if it cannot.

---

## 1. What changed, and what did not

| | before 2026-08-18 | after |
| --- | --- | --- |
| Betts and Bokhari (2000) full text | paywalled, `is_oa: false`, NOT read | **READ IN FULL**, SHA-256 `905cce61...` |
| Turbulent-rung Nusselt reference | **NOT OBTAINED** | **5.85** (Ra 0.86e6), **7.57** (Ra 1.43e6), Table 1, p. 682 |
| K0cT Nusselt rows | UNGRADED measurement, no band | **GRADED. GATE FAIL, both rungs** |
| K0cT's other 18 graded rows | GATE FAIL, 8 of 18 | **unchanged; not revisited here** |

The reference, its stated uncertainty, the check that its definition is
commensurate with the solve's, and the 2.08 percent internal inconsistency found
in the paper's own lower-Ra row are all in **addendum A1**, Sections A1.2 to
A1.5, and are not repeated here.

## 2. The honest status of this grading

**These solve values pre-date the reference and this is not a pre-registered
prediction.** The Nusselt numbers were computed and published at
2026-08-18T04:42Z, before Betts and Bokhari was in hand. Nothing here was
predicted in advance and nothing here claims to have been.

What protects the grading from being tuned to its answer is that **every element
of the band is external to the solve values**:

| component | value | where it comes from |
| --- | ---: | --- |
| stated accuracy of the wall temperature gradient | 5.00 % | Betts p. 681, the authors' own figure |
| Table 1 internal inconsistency at lo Ra / abstract-vs-table dT at hi Ra | 2.09 % / 2.00 % | derived from the paper, before any solve value was looked at |
| grid uncertainty | 0.28 % (lo), 0.49 % (hi) | the executed rung's own coarse/fine pair, published 2026-08-18 |
| **u_val** (quadrature) | **5.43 % / 5.41 %** | |

No band was chosen after seeing which side of it an answer fell on, and a reader
can check that: the addendum and `gate_k0ct.json` are both dated and both
independent of this file.

## 3. The graded rows

Deviation `E = 100 (Nu_solve - Nu_ref) / Nu_ref`, taken on the **fine mesh** of
the two-mesh pair, with the coarse carried alongside, per specification Section
2.5.

| rung | model | Nu coarse | **Nu fine** | reference | **E** | u_val | \|E\|/u_val | **verdict** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| lo, Ra 0.86e6 | kOmegaSST | 4.8544 | **4.8680** | 5.85 | **-16.79 %** | 5.43 % | **3.09** | **GATE FAIL** |
| hi, Ra 1.43e6 | kOmegaSST | 5.6689 | **5.6965** | 7.57 | **-24.75 %** | 5.41 % | **4.57** | **GATE FAIL** |

**kOmegaSST under-predicts the measured heat transfer of this cavity by 17 to 25
percent, at three to four and a half times the validation uncertainty.** The
comparison error is far larger than every uncertainty in it combined, so the
modelling error is resolved rather than buried in noise. The error **grows with
Rayleigh number**, from -16.8 percent to -24.8 percent for a 66 percent rise in
Ra, which is the shape of a model that is not producing enough turbulent mixing
and falls further behind as more is required.

## 4. Reported, and NOT graded

| case | model | Nu | reference | E | \|E\|/u_val | why it is not graded |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `M_hi_f_LS` | LaunderSharmaKE | 7.9866 | 7.57 | **+5.50 %** | **1.02** | **Fine mesh only. No coarse twin was run.** Specification Section 2.5: a solve presented without its grid-sensitivity pair is not graded at all |
| `C1_hi_c_laminar` | laminar | 4.7197 | 7.57 | -37.65 % | 6.96 | control, not a graded case |
| `C2_hi_c_Ra130` | kOmegaSST | 6.1464 | 7.57 | -18.81 % | 3.48 | Ra raised 30 percent; not the reference case |
| `B_hi_c_adiabatic` | kOmegaSST | 5.6934 | 7.57 | -24.79 % | 4.58 | boundary-condition twin, not the reference case |

**The LaunderSharma row is the closest number on this page to the experiment and
it is still not graded.** The rule that excludes it was written on 2026-08-17,
before any of these numbers existed, and applying it only when it is convenient
would make it worthless. It is reported at full precision so nothing is hidden by
the exclusion.

## 5. Does the 40 percent spread resolve? Plainly

`K0cT_RESULTS.md` Section 5 recorded a **40.2 percent model-to-model spread** on
Nusselt with no reference to adjudicate it: kOmegaSST 5.6965, LaunderSharmaKE
7.9866, identical mesh, identical boundary conditions, identical schemes.

**The reference does not sit between them symmetrically. It sits at 81.8 percent
of the way from kOmegaSST to LaunderSharmaKE.**

```
   SST 5.6965                        ref 7.57      LS 7.9866
   |---------------------------------------|---------|
   0 %                                  81.8 %     100 %
```

**The verdict, in the required vocabulary:**

- **kOmegaSST: GATE FAIL.** Excluded at 3.1 and 4.6 times the validation
  uncertainty, at both Rayleigh numbers. This is not close.
- **LaunderSharmaKE: not graded, and not vindicated either.** Its comparison
  error is +5.50 percent against a validation uncertainty of 5.41 percent, so
  `|E|/u_val = 1.02`: **the error and the noise floor are the same size.** The
  data cannot distinguish LaunderSharma's Nusselt number from the experiment's,
  and equally cannot confirm it. A reference with a stated +/-5 percent
  uncertainty is not an instrument that can certify a 5.5 percent agreement.
- **So the spread resolves in favour of NEITHER MODEL as a passed gate, but it
  is decisively asymmetric.** One model is refuted; the other is merely not
  refuted. Those are different statuses and neither is a pass.

### 5.1 And LaunderSharma's near-hit on Nusselt is a compensating error, not a success

This is the part that would be lost by reading the Nusselt row alone. Against the
same experiment, on the same cases, on every quantity the rung measured:

| quantity | reference | kOmegaSST | LaunderSharmaKE |
| --- | ---: | ---: | ---: |
| Average Nusselt (this document) | 7.57 | **-24.7 %** | **+5.5 %** |
| Core stratification S | 0.095 | **+147.7 %** | **-80.4 %** |
| Mid-height peak vertical velocity | 0.190 m/s | **+16.4 %** | **-33.3 %** |
| nu_t/nu (solve domain max vs measured centre-line 55, A1.6b) | 55 | **-60.4 %** | **-27.5 %** |

**LaunderSharmaKE reproduces the wall heat flux to within the experiment's own
uncertainty while getting the velocity field wrong by a third and the core
stratification wrong by a factor of five.** A model that transports the right
amount of heat through a boundary layer whose velocity is 33 percent too low is
not right about this flow; it is wrong in two directions that partly cancel in
one integral. Any downstream use of a LaunderSharma Nusselt number on this case
class must carry that, and **the 40 percent spread must not be replaced in
anyone's notes by "LaunderSharma was right".**

The last row is a further, independent statement about both models: **neither
reaches the measured eddy viscosity anywhere in the domain.** The comparison is
deliberately unfavourable to the conclusion - it puts each solve's *domain
maximum* against the experiment's *centre-line* value, so the true shortfall at
the centre-line is at least this large. kOmegaSST's largest eddy viscosity
anywhere is 60 percent below what was measured at one specific point.

## 6. Three defects found while doing this, reported because they were real

### 6.1 `analyse_k0ct.py` was BROKEN AT HEAD, and the breakage was invisible

The K0cT comparator resolved its specification and its primary data as `../`
relative to itself. **That path was correct when the rung was written and false
by the time this re-grade ran**: a repository reorganisation moved the run tree
from `docs/campaigns/F14-cooling-ladder/K0cT_runs/` to
`verification/runs/F14-cooling-ladder/K0cT_runs/`, and the literal did not move
with it.

Verified by execution, not by reading:

```
$ cd verification/runs/F14-cooling-ladder/K0cT_runs && python3 analyse_k0ct.py
REFUSE: gate specification not found at
  /home/ubuntu/Certonomous/verification/runs/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md
exit 2
```

**The rung's own comparator could not be re-run at HEAD.** This is the L-137
failure class, and the K2c lane hit an independent live instance of the same
class, from the same reorganisation, on the same day. Both scripts now resolve
by **searching upward for the repository root** and naming the file, rather than
assembling a relative literal. Fixed in `analyse_k0ct.py` and written that way
from the start in `regrade_nusselt.py`.

Worth stating plainly: the analyser **refused loudly** rather than grading
against something wrong. The guard discipline held. But a comparator that cannot
run is a verdict that cannot be reproduced, and the rung shipped that way.

### 6.2 The provenance guard was moved, not defeated, and it was wrong twice first

The mandate was to supersede the NOT OBTAINED statement by dated addendum and to
update the guard **in the same change-set**, with the guard's new referent being
the addendum. Done. The guard now requires **both** sentences and exits 2 if
either is missing.

It was written wrong twice, and a two-way control caught both:

1. **First version refused on an unmutated specification.** The addendum's marker
   sentence wraps across a line break in the markdown; the guard looked for a
   single space. **A provenance guard that breaks when a paragraph is rewrapped
   is a guard that the next person deletes.** Fixed by normalising whitespace
   before matching.
2. **Second version could not tell the record from a quotation of it.** The
   sentence "Nusselt number, turbulent rung: reference NOT OBTAINED" now occurs
   **three times** in the specification: once in Section 2.3 where it is the
   record, and twice inside addendum A1 where it is quoted while being
   superseded. Deleting Section 2.3's statement outright left the guard
   satisfied by A1's quotation. Fixed by anchoring on Section 2.3's own
   continuation, which occurs exactly once.

Final control, all three directions executed:

| mutation | required | observed |
| --- | --- | --- |
| none (specification as filed) | guard passes | **exit 1**, the rung's own published GATE FAIL |
| addendum A1 marker removed | exit 2 | **exit 2**, refused on the addendum |
| Section 2.3 statement removed | exit 2 | **exit 2**, refused on the original |

**The statement in Section 2.3 was never deleted.** It is still there, unedited.

### 6.3 A false negative in the control itself, recorded so the next reader is not misled

The third mutation above first reported **exit 1** - a pass where a refusal was
required - and the guard looked broken. It was not: **the mutation had silently
failed to apply**, because the test rewrote a string that wraps across a line in
the raw file, the same wrapping that caused defect 6.2. A control that does not
perturb what it thinks it perturbs reports the system as sound. The mutation was
reapplied whitespace-insensitively and the guard refused correctly.

## 7. What this does NOT change

- **The other 18 graded rows of `K0cT_RESULTS.md` were not revisited.** That
  rung's headline verdict was already GATE FAIL, 8 of 18 rows, and this document
  adds two more failing rows on a quantity that was previously ungraded. It does
  not soften or reopen anything else.
- **Section 2.3's core stratification rows stand unchanged.** Betts Table 1's
  `Centre-line dT/dx` is a *horizontal* gradient, not the vertical
  stratification, and the paper supplies no vertical stratification figure
  (addendum A1.7).
- **Heat balance remains a near-identity on this sealed geometry and is still not
  a passed gate.** `K0cT_RESULTS.md` Section 7 said so and it is still true.
- **Nothing here is submitted, sent, filed, uploaded or registered.**
  Submissions are PARKED.
