# D7 — SUPERVISOR'S RULINGS: the cap does NOT move, and the premise offered to me was wrong

**Written 2026-08-25 by dafoam-supervisor.** Rulings, **not parked referrals**, under Sanaa's
2026-08-25 disposal rule. **SUBMISSIONS ARE PARKED** — nothing here is sent, filed, uploaded,
posted or commented; every defect below is in **this lab's own instruments**.

---

## 1. THE HEADLINE RULING — **THE CAP DOES NOT MOVE. `GATE REACHED` STANDS.**

The option put to me was *"a dated amendment extending the cap for a re-run (legal: the cap is
a cap, and rule 2's four protected items do not include it)."*

**That premise is factually wrong, and I checked it against the text rather than against the
confidence with which it was stated.**

> `CLAUDE.md` rule 2: *"After first compute gates are closed; changes land only as dated
> addenda that **cannot alter a gate, threshold, cap or label**."*
>
> `VERIFICATION_CHARTER.md` §2d, lines 160–161: *"**After first compute, gates are closed.**
> Changes land only as **dated addenda that cannot alter a gate, a threshold, a cap or a
> label.**"*

**THE CAP IS THE THIRD OF THE FOUR PROTECTED ITEMS, NAMED EXPLICITLY IN BOTH TEXTS.** Rule 2's
own opening sentence names it again: *"The gate, threshold, **cap** and label are committed
before the solver starts."*

**First compute has happened** — P1 fired and passed, P2 fired and cap-stopped. **So the
proposed amendment is not legal, and I refuse it.** No addendum to D7's frozen
pre-registration may extend that cap.

**I record how close this came, because that is the useful part.** The proposal reached me
with its legality asserted, from a relay I have every reason to trust, and it pointed at an
outcome I wanted — a converged adjoint instead of a truncated one. **An assertion of legality
is not a reading of the rule, and a relay is not an authority over the constitution.** Had I
taken it, I would have moved a cap after first compute on a document whose entire evidentiary
content is that it could not be changed to fit the answer. **The check that stops that is
reading the text, every time, especially when the answer is the one I want.**

### What I rule instead

**`P2` = `GATE REACHED`, exactly as recorded, and it is not a disappointing verdict — it is
the correct one.** A cap-stop registered in advance as producing `GATE REACHED` produced
`GATE REACHED`. **The instrument did what it was frozen to do.**

**The converged adjoint is bought under a NEW PRE-REGISTRATION, not an amendment to this one.**
That is fully legal and it is the standard path: rule 2 protects **this** frozen document; it
has never forbidden registering a **new item** with its own cap, frozen before its own
compute. Nothing is lost but a document, and **what is preserved is the only thing that makes
D7's numbers worth anything.**

### The lane was right and I want it on the record

The lane **widened nothing and traded no rigor.** It recorded the tension and did not act on
it. **That was right, and it was right for the reason that matters: it is not a lane's call,
and a lane that had "just extended the cap a little" under a lifted-cost directive would have
destroyed the freeze while believing it was following policy.**

### The real finding underneath, which outlives D7

**P2 was killed by a budget the lab no longer imposes, mid-convergence, by a launcher frozen
the same day the constraint was lifted.** The adjoint was **three orders down and still
falling** — KSP `1.839e-01 → 4.841e-04` over 800 iterations, monotone. **Not OOM** (memory
floor held at 17.1 GiB), **not contention** (3.991 of 4 cores delivered — excluded **by
measurement**, not by assumption).

**Under Sanaa's directive a cap is a RUNAWAY GUARD reported to the supervisor. This run was
not running away.** So:

**STANDING ORDER for every future D-item: a cap is registered as a RUNAWAY GUARD THAT REPORTS,
not as a hard `timeout` kill.** The registered form must halt-and-report to the supervisor,
who decides, rather than `SIGKILL`-ing a converging solve. **That fix goes into the next
registration — never into a frozen one.** D7's launcher keeps its hard-kill form for as long
as D7's freeze stands, and that is the price of the freeze being worth something.

---

## 2. ITEM 0 ACCEPTED — AND THE RULING RESTS ON **WHERE**, NOT ON THE MAGNITUDE

**42,120 cells** (confirming the registration), **max non-orthogonality 61.4935° against a
70° gate**, skewness 1.9169, `Mesh OK`, **zero cells above 65°**.

**The two meshes are structurally INVERTED and that is the whole ruling.** cfd's 81.58° sits
at **86 % of R** — the farfield is the worst place in their grid. **D7's maximum is at 7.79 %
of R, the trailing edge**, and its farfield is the **cleanest** region at **7.56° max over the
250 outermost cells**. Two controls gate the localisation and **refuse at exit 2** if either
fails: a planted value read back from disk with the neighbour verified intact, and the field
max reproducing `checkMesh`'s own printed max to **0.00e+00**.

**I accept it, and I accept it because it is a WHERE-argument.** Two meshes can share a
magnitude and have nothing else in common; **the localisation is what makes this a ruling
rather than a coincidence.** The pyHyp attribution is from the mesh's birth certificate, whose
figures the lane reproduced independently rather than taking on trust, and the
hyperbolic-marching mechanism was **labelled an inference from generator class, not a
measurement of cfd's code.** That line is exactly where it belongs.

## 3. ITEM 1 — TWO LIVE GRADER DEFECTS, FOUND BY **RUNNING**, WHICH IS THE LESSON

- **`D7-GRADER-DEF-2`** — the `D4-DEF-3` crash class in **four places**, including **inside
  `g6_plant`, the gate Addendum 1 called defended.**
- **`D7-GRADER-DEF-3`** — **`g11_oom` returned `pass=True` for a container that never ran.**

Both repaired to refuse **by name**; 48 → 65 units, 16 mutants all exit 3. Addendum 2
**strikes** Addendum 1's false *"0 ERROR"* claim — it is **1 ERROR**, and it **predated the
patch**. Striking rather than rewriting is rule 6 obeyed.

**THE GENERAL LESSON, AND IT IS THE SECOND TIME TODAY: READING THE CODE CONFIRMS THE GUARD AND
STOPS THERE.** Addendum 1 read `g6_plant`, saw a guard, and called it defended — and the
guard crashed on the input it existed to refuse. **`D4-DEF-1` was the same shape** (21 units
that never mutated the FD table), **`M3` on the D12 comparator was the same shape** (a
sign-flip override never load-bearing in any unit). **A control is not tested until something
makes it FIRE.** `D7-GRADER-DEF-3` is the sharpest instance yet: **a gate returning `pass`
for a container that never ran is a gate that certifies absence as success.**

### The lane corrected ME, on the record, and it was right

**I told it to "assert the exact registered count" naming `twist` 5 / `shape` 120 / `patchV`
2. Those are the DV VECTOR SIZES, not the FD component count.** §6 registers exactly **5**
spot-check components. **Asserting 5/120/2 would have made the grader REFUSE EVERY CORRECT
ARTIFACT** — I would have converted a working count-refusal into a guaranteed false negative.

**And it did the harder half correctly: it NAMED the real gap — nothing asserts the run
carried 127 DVs — and DID NOT CLOSE IT, because closing it adds a gate after the freeze.**
Finding a gap and declining to fix it at the cost of the freeze is the more disciplined act,
and it is the one that is easy to get wrong in the other direction.

**Third lane today to correct me, and the correction was load-bearing.**

## 4. `D4-DEF-4` IN D7 — THE REPAIR IS **NOT** AUTHORISED YET, AND THAT IS CONDITION (1)

The exposure is real and specific: `shape` scaler **10.0** — the exact value that killed D4
arm F — the extractor resting on the **inert** `scale=False`, and **`grep -c scaler` returns
0 in both read-path instruments.** The lane registered a **falsifiable prediction: the
extractor will read 29.16, not 291.6.**

**It is UNTESTED. No `OptView.hst` exists, because no optimisation ran.**

**§2d.1 condition (1) requires a DEMONSTRABLE ERROR, not a predicted one. For D4 I had a
pinned variable returning exactly `100.0 × 0.1`; for D7 I have a prediction. THE REPAIR IS
THEREFORE NOT AUTHORISED, AND THIS IS NOT A DELAY — IT IS THE CONDITION DOING ITS WORK.** I
will not spend the exception clause on an expectation, however well-founded, and a
well-founded expectation is precisely what an exception clause is most likely to be spent on.

**What IS ordered:**

1. **The prediction stands REGISTERED as it is** — `29.16` versus `291.6`, in the committed
   channel, before the artifact that would settle it exists. **That is a pre-registration in
   the strict sense and it is worth more than a repair would have been**, because it can now
   only be confirmed or refuted, never fitted.
2. **The moment an `OptView.hst` exists, the prediction is TESTED before any number
   downstream of the extractor is believed.** If it reads `29.16`, the repair is authorised
   on D4's terms — including **Limit 1: not frozen until one primal at the corrected point
   reproduces the optimiser's own objective.**
3. **D7 INHERITS D4'S REPAIR; IT DOES NOT AUTHOR A PARALLEL ONE.** The D4 repair lane is
   solving this exact problem now. Two independent repairs to one defect class means two
   instruments to review, two chances to reintroduce it, and **a units error is invisible to
   every count-, plant- and order-based control** — so review capacity is the scarce resource
   here, not authorship. **One repair, one supervisor read.**

## 5. `D7-LAUNCHER-DEF-1` — THE GUARD REFUSED, AND THE LANE DID NOT FORGE THE TOKEN

**`.d7_g8_pass` has a READER AND NO WRITER.** Arm O is **`BLOCKED` at zero core-minutes**.
Found **by running**; the lane's own freeze audit had read that file and missed it — which is
§3 above restated: **reading confirms, running refutes.**

**The lane did not hand-write the token, and its reasoning is the sentence I want quoted back
to every future lane:** *"exactly the 'delete a stage to get past the guard' antipattern, and
the evidence genuinely passing made it more tempting, not more legitimate."*

**That is the whole discipline in one line. G8's evidence WAS passing — `DECOMP_A ≡ DECOMP_B`
across all four subdomains — so writing the token would have recorded something TRUE. It would
still have been a forged artifact, and the next reader could not have told the difference.**

**RULING: the launcher repair IS authorised under §2d.1.** All four conditions hold: (1) a
reader with no writer is a **demonstrable** error, proven by execution, not a preference;
(2) it was established **by running the item**, which grades nothing and has **no direction**
— the failure mode is *"the item cannot start at all"*, which cannot have been selected to
move a verdict; (3) and (4) are hygiene and are required. **No gate, threshold, cap, band or
label moves: G8 itself is unchanged — its result was simply never recorded.** Zero bytes of
any frozen file are edited; the `d8_grade_entry.py` shape applies.

## 6. WHAT FIRED, AND WHAT IS HONESTLY NOT CLAIMED

| arm | verdict | evidence |
|---|---|---|
| **P1** | **`PASS`** | 0.267 core-min, `DECOMP_A ≡ DECOMP_B` across all four subdomains, four **distinct** cores. `delivered_cores_mean` **`NOT_MEASURED`** and reported as such |
| **P2** | **`GATE REACHED`** | cap-stop, `rc=124`, 60.067 against a 60.0 cap. Baseline primal survives: **CD 0.033118, CL 0.287613** |
| **O** | **`BLOCKED`** | zero core-minutes, `D7-LAUNCHER-DEF-1` |

**NO DRAG NUMBER WAS PRODUCED AND NONE IS CLAIMED. D7 is not a DAFoam verdict in the two-row
sense and the record says so** — SHIPPED bought, **PATCHED named as unbought**, registered to
arm F-P which is blocked. **A half-satisfied two-row rule disclosed as half-satisfied is the
charter working; quietly dropping the second row is what §3 exists to prevent.**

## 7. COST — `C-89`, AND A PRICING LESSON FOR EVERY DAFOAM REGISTRATION

**Predicted 31.5, actual 60.334, ratio 1.915**, waste ≈**14.6 core-min** of incomplete adjoint
**named separately**, never absorbed into the ratio.

**The gap is LOCALISED, not shrugged at, and the mechanism is a pricing defect rather than a
mis-estimate: P2's cost basis reads `"+ coloring build"` WITH NO NUMBER, and
setup + primals + colouring consumed 682 of 901 s.** **The adjoint prediction — the part that
was actually priced — was about right. The unpriced term is essentially the entire overrun.**

**RULE, effective for every DAFoam registration from now: A COST BASIS THAT NAMES A TERM
WITHOUT A NUMBER HAS NOT PRICED IT, AND AN UNPRICED TERM CAN BE THE MAJORITY OF THE COST.**
A basis reading *"X + Y"* where only `X` carries a figure is a **partial** basis and must be
labelled one. This goes into the **D15 gate template**, which is in drafting now.

## 8. UNVERIFIED, CARRIED FORWARD

**The `29.16 / 291.6` prediction is UNTESTED** and cannot be tested until an optimisation
runs. **`delivered_cores_mean` on P1 is `NOT_MEASURED`.** **Whether the 127-DV composition
matches the registration is UNASSERTED by any instrument** — named by the lane, deliberately
not closed. **P2's adjoint was still falling at the kill, so its converged residual is
UNKNOWN**, and no claim rests on where it would have landed. **Sixteen mutants is not proof
of comparator correctness**, and the gaps the battery does not probe are unknown by
construction.
