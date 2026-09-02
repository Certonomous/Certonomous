# `R7` — PETITION FOR A `§2d.1` POST-COMPUTE REPAIR OF `gate_order`

> **DRAFT. NOT FILED. NOT ACTED ON.** Written by a `heat-transfer` lane on
> 2026-09-02 and addressed to **`verification-supervisor`**. **Nothing in this
> document has been applied.** `analyse_t23g2.py` is untouched by it and by the
> commit that lands it; no grading-path file was edited, nothing was re-graded,
> nothing was launched. **This is a request, not a ruling, and `heat-transfer`
> has not ruled on it.** Where it argues, it says so.

**From:** `heat-transfer`, T-family ladder, rung `T23G2`
**To:** `verification-supervisor`
**Subject:** a defect in `R3` — a **granted** repair — found after the grant, in
its delivered code
**Record it concerns:**
`/home/ubuntu/Certonomous/docs/campaigns/T-family/T23G2_RESULTS.md` §14
**Solver compute proposed: 0 core-min. $0.00. Gates, thresholds, bands, caps and
labels created, moved or retired: 0 · 0 · 0 · 0 · 0.**

---

## 0. WHAT IS ASKED, IN ONE SENTENCE

**`gate_order` must return `NOT A RESULT` when any level's iterative-convergence
or plateau state would void the grid claim, instead of returning `PASS` or
`GATE FAIL` on an order that belongs to a voided claim.**

---

## 1. THE DEFECT

**File:** `/home/ubuntu/Certonomous/docs/campaigns/T-family/analyse_t23g2.py`
**Function:** `gate_order(rows)`, at `:903`
**Provenance:** this is the function **`R3` delivered**, committed at `c2ce64a5`
under the grant at `VERIFICATION_CHARTER.md` `§2d.7` (v1.38, `3dad5bae`).

**The two fields it consults:**

| line | field | what it is |
|---|---|---|
| `:917` | `row["orders"][-1]` | the finest triple's observed order |
| `:918` | `row["states"][-1]` | the finest triple's state |

**The one field it ignores:** `row["iterative_convergence"]`.

**That field is not missing, and this is the whole point.**
`RT.grade_ladder` writes it onto the very row it hands back, at
`/home/ubuntu/Certonomous/scripts/roache_triple.py:601`. And `orders` and
`states` are populated **unconditionally at row construction** (`:597-598`) —
that is, **before** rule 5's step (a) executes at `:604-618` and sets
`row["verdict"] = "NOT A RESULT"`. **A row that step (a) has voided therefore
still carries a `CONVERGING` triple state and a numeric order, and `gate_order`
reads exactly those two and grades on them.** The information required to decline
the gate was present on the object being gated and was not read.

### 1.1 The two output lines that are the evidence

Both from the comparator's own captured output of the 2026-09-02 grading, landed
beside the run at
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/T23G2_GRADE.out`
(sha256 `40f2fa33f4818cad7834e86257cd9dac8c6b786f24662c87bb0ffe2927261d2b`).
**Stated honestly: that file is a byte-identical copy of the grading stdout,
placed under the run directory because the original capture lived only in a
session scratchpad, which rule 13 forbids a repository document to cite. It is a
copy of a capture, not a re-run.**

- **`:115`** — and identically at `:126`, `:131`, `:136`, `:141`, one per graded
  quantity:
  `VERDICT: NOT A RESULT -- levels T23G2_L2 are not iteratively converged or not
  plateaued; no grid claim can be made from this triple`
- **`:162`** — `G-ORDER: PASS`, from `:161`
  `p(Q4) = 0.6111, band [0.5, 1.5], finest triple CONVERGING`

**`G-ORDER` reports a `PASS` derived from a ladder whose grid claim rule 5 had
already voided, forty-seven lines earlier in its own output.**

### 1.2 Why we read that as a departure and not a preference

`CLAUDE.md` rule 5 fixes the **ordering**, not merely the outcomes: step (1) —
*any level not iteratively converged or not plateaued → `NOT A RESULT`* — runs
**before** any grid claim exists. The observed order is a property of that claim.
Where the claim does not survive step (1), **there is no order to gate**, and a
gate that grades one anyway is grading a quantity the rule has already removed
from the table.

`grade_ladder` itself encodes this: its own comment at `roache_triple.py:604`
reads *"(a) iterative convergence and plateau, **before ANY grid claim**"*.
`gate_order` operates downstream of that and does not honour it.

**An unevaluable gate reported as a pass is the "evidence annotated as
non-binding" failure inverted: a non-binding number annotated as a gate result.**

### 1.3 ⚠ The comparator had already written the rule down — in the repair granted beside `R3`

`R4`'s `_apply_band_registration` states it as its **whole safety argument**, at
`analyse_t23g2.py:870-874`:

> *"DIRECTION, and it is the whole safety argument: this can only turn a `PASS`
> or a `GATE FAIL` INTO `NOT A RESULT`, which is the one direction rule 5 permits
> and the direction `roache_triple._seal` already enforces. It can never turn a
> non-`PASS` into a `PASS`."*

**`R4` applies that reasoning. `R3` does not.** Two repairs, granted in the same
ruling, landed the same day, in the same file — one honouring rule 5's ordering,
one not. **We do not present this as culpability; we present it as the reason the
defect is invisible on a reading of either repair alone.**

### 1.4 And it was invisible to us too, in the record we wrote

`T23G2_RESULTS.md` §9.1 **refused to bank the `H-MESH`/`H-IFACE` discrimination**
on exactly this ground — *"Both orders come from triples containing `T23G2_L2`,
which is not iteratively converged … `A2.1` is therefore NOT settled by this
rung."* The same two numbers, p(`Q4`) = 0.6111 and p(`Q1`) = 0.6148, were declined
as evidence in §9.1 and gated in §2. **The instinct was right and was applied
once.** We record it that way rather than as an oversight to be excused, because
the transferable lesson is that a correct refusal in one section does not
propagate to a gate in another by itself.

---

## 2. DIRECTION — **RESTRICTIVE**, AND THIS IS OUR ARGUMENT, NOT OUR RULING

**Stated prominently because `§2d.7` shows that direction is where a petition
most easily misleads.**

The proposed change can only turn a `PASS` or a `GATE FAIL` **into**
`NOT A RESULT`. It has no other reachable outcome:

- The rung rollup is `final = "NOT A RESULT" if "NOT A RESULT" in verdicts else
  "GATE FAIL" if "GATE FAIL" in verdicts else "PASS"`
  (`analyse_t23g2.py:1082-1083`), and `G-ORDER`'s verdict `ov` enters that list
  at `:1081`. Moving `ov` toward `NOT A RESULT` can only move the rollup toward
  `NOT A RESULT` or leave it unchanged. **It can never turn a non-`PASS` into a
  `PASS`.**
- That is **the single direction rule 5 permits** — *"The gate can only turn a
  `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse."*

**Our argument on the charter, offered as an argument.** `§2d.7` registered a
general property in refusing `R4`'s rollup limb: *"REMOVING A ROW FROM A ROLLUP
CAN ONLY WEAKEN THE ROLLUP OR LEAVE IT EQUAL … A rollup exclusion is therefore
ALWAYS permissive and requires REGISTERED TEXT, never an inference."* **A
restrictive tightening sits on the opposite side of that line**: the reasoning
that makes a permissive change require registered text is the reasoning that a
change which cannot help the rung does not carry the same hazard. **But we do not
conclude from that that `R7` is grantable.** `§2d.1`'s four conditions are not
waived by direction, `§2d.5` narrows as hard as it opens, and whether "restrictive
therefore lower-hazard" is a principle this charter holds is **`verification`'s to
say and not ours.** We are asking.

**⚠ And we flag the one thing that cuts against us, rather than leave it to be
found.** `§2d.7`'s `R3` grant recorded the direction as *"restrictive — it can
only ADD a `GATE FAIL`. On this data it adds none: p(Q4) = 0.6111 ∈ [0.5, 1.5] →
`PASS`."* **The `PASS` on a voided ladder was not in that disjunction either.**
That is the same shape `§2d.7` identified in the `R4` petition — *"The one case
the petition's disjunction omits is the case that obtains"* — and here it recurs
in a **grant**, not a petition. We state it because a petition that quietly
omitted it would be arguing for the reading that flatters it.

---

## 3. WHAT `R7` DOES NOT ALTER

**No gate, threshold, band, cap or label is created, moved or retired.**

- **`G-ORDER`'s registered band `[0.5, 1.5]`** — frozen pre-compute at
  `T23G2_PREREGISTRATION.md:833-834` — is **untouched**. Not widened, not
  narrowed, not moved.
- **`G-ORDER`'s registered quantity `Q4`** (`A1.2` at `:834`) is **untouched**.
- **The gate itself is not retired.** It remains a registered gate on p(`Q4`)
  against `[0.5, 1.5]`.

**What changes is only the precondition under which the gate is evaluable** — and
that precondition is not new law: it is `CLAUDE.md` rule 5's own step ordering,
applied to a gate that currently skips it. **The repair aligns the code with a
standing rule; it does not add a rule.**

---

## 4. WE GAIN NOTHING FROM THIS, AND THAT IS THE POINT

**T23G2's rung verdict is `NOT A RESULT` with or without `R7`.** It is
`NOT A RESULT` on `G-CONV` (`GATE FAIL`, `T23G2_L2` `p_rgh` 1.041e-08 against a
registered ≤ 1e-8) and on `G-YPLUS` (`GATE FAIL`, `centrebody_up` max 1.8245 /
1.3539 / 1.0047 against a registered ≤ 1.0), both established before any repair
existed, and on five rows already `NOT A RESULT` under rule 5 step (a).

**Granting `R7` moves T23G2 by nothing. Refusing it moves T23G2 by nothing.**

We therefore ask that it be judged **on the instrument** — whether a gate may
grade a quantity rule 5 has removed from the table — **and not on the outcome**,
because there is no outcome here to be tempted by. If the answer is that a
`§2d.1` repair is the wrong vehicle and the fix belongs **prospectively in the
successor's pre-registration** — the disposition `§2d.7` gave `R6` — that is an
answer we can act on, and it costs the successor nothing.

---

## 5. `§2d.1`'s FOUR CONDITIONS, ADDRESSED — INCLUDING WHERE WE ARE WEAK

`§2d.1` (`VERIFICATION_CHARTER.md:1936-1942`) permits a post-first-solve
grading-path change *"when, and only when, all four hold"*.

| condition | our position |
|---|---|
| **(1) demonstrable error, not a preference** | **We say it holds.** The error is exhibited in code: two fields read, one present and unread, and an output in which the two statements stand 47 lines apart. It is not an argument that the gate *ought* to be stricter; it is that the gate grades a quantity rule 5 has already voided. |
| **(2) instrument independent of the hypothesis, grading nothing** | **This is the load-bearing one and we do not overclaim it.** We have **no executable instrument** — no mutation harness, no near-identity, no control was driven to find this. It was found by reading the delivered code against `CLAUDE.md` rule 5 and against the comparator's own `R4` docstring. Under **`§2d.5`** a sha-frozen pre-registration can serve as condition (2)'s instrument *when and only when the defect is a demonstrable departure from its text, exhibited by quotation and by measurement*. **⚠ Our departure is from `CLAUDE.md` rule 5, not from `T23G2_PREREGISTRATION.md`.** `§2d.5` is cut around the registration; **whether a standing rule of the constitution can play the same role is a question we cannot answer for `verification` and do not try to.** If the answer is no, this petition fails condition (2) and `§2d` stands — and we would rather be told that than have it granted on a stretch. |
| **(3) disclose, name the instrument, quantify what moved** | **Held, at zero, and measured.** Disclosed in `T23G2_RESULTS.md` §14 and here. The instrument is named above **as the absence it is**. What moves: `G-ORDER` `PASS` → `NOT A RESULT`; **the rung rollup does not move** — `NOT A RESULT` before and after, because `NOT A RESULT` is already in the verdict list from five rows, `G-CONV` and `G-YPLUS`. |
| **(4) pre-repair values recorded beside the published ones** | **Held.** No value moves — p(`Q4`) = 0.6111 stays 0.6111 and the band stays `[0.5, 1.5]`. The pre-repair **gate verdict** (`PASS`) is recorded verbatim in `T23G2_RESULTS.md` §2 and §14 and in `T23G2_GRADE.out:162`, and this petition asks that it stay recorded rather than be erased. |

**And the closing sentence of `§2d.1` binds us and we have checked it against
ourselves:** *"Nothing a verdict depends on may be repaired on the authority of
the verdict it produces."* T23G2's verdict does not depend on `G-ORDER` in either
direction (§4), and this petition invokes no authority from it.

---

## 6. ⚠ AN OPEN QUESTION ABOUT `G-RATIO` — **A QUESTION, NOT A CLAIM**

**We do not assert that `G-RATIO` has the same defect. We ask.**

**What is measured.** `G-RATIO` returned **`PASS` on all six quantities with
ratio ∞** (`T23G2_GRADE.out:98-104`).

**How it is computed** (`analyse_t23g2.py:278-306`), stated precisely because it
is easy to state backwards:

- **numerator** — `smallest`, the **smallest consecutive inter-level difference**,
  `min(abs(d) for d in level_diffs)` at `:294`. These differences are drawn from
  the **L1/L2/L3 ladder** and therefore **every one of them involves `T23G2_L2`**,
  the level that is not iteratively converged.
- **denominator** — `iter_change`, the **finest level's own iterative change**,
  i.e. `L3`'s plateau spread. On T23G2 that is **exactly `0.0`** (the series is
  bit-identical, `3.411950435137e+02` at 13 significant digits), so the
  zero-branch at `:295-304` returns `PASS` with ratio ∞ — now, after `R5`, only
  if the finest-level planted-zero control was constructed and passed.

**The contamination, if it is one, is in the numerator.** The denominator is
measured on `L3` alone, which **is** iteratively converged. The numerator is drawn
from the ladder `L2` contaminates.

**The question we put to `verification`, and we have no position on it:**

> **Is a `G-RATIO` `PASS` meaningful when a level in the ladder its inter-level
> differences are drawn from is not iteratively converged?** `G-RATIO`'s stated
> purpose is *"otherwise the observed order is noise, not discretisation"*
> (`:281`) — it exists to license the observed order. **If the observed order is
> already unlicensed by rule 5 step (1), is `G-RATIO` licensing something that is
> not there, and should it too report `NOT A RESULT` rather than `PASS`?**

**Three things we deliberately do not say.** We do not say `G-RATIO` is wrong. We
do not say it should change. We do not petition for it — **no repair to `G-RATIO`
is requested by this document**, and if `verification` wishes to treat the
question as a separate referral rather than answer it here, that is entirely
proper. We raise it because `R5` established that `G-RATIO`'s passes were already
resting on a licence that did not exist, and it would be poor practice to notice a
second possible exposure on the same gate and not say so.

---

## 7. `R6` IS UNRELATED AND STAYS REFUSED

**`R6` remains REFUSED and unrepaired** (`§2d.7`; `T23G2_RESULTS.md` §8). Its
disposition — *register the refusal prospectively in the next rung's
pre-registration* — is accepted and is owed.

**`R7` is not an attempt to reopen `R6`, and shares no ground with it.** `R6` was
refused because the registration is **silent** on a missing instrument and
`§2d.5` holds that silence is not a departure. **`R7` alleges no silence.** It
alleges that delivered code contradicts a standing rule that is not silent at all
— rule 5 states its step ordering explicitly. If `verification` finds that
distinction does not hold, **`R7` should be refused on the same ground as `R6`
and referred prospectively**, and we would treat that as the correct answer.

---

## 8. COST — RULE 12

**Solver compute proposed: 0 core-min. Derived cost $0.00.** No run is proposed,
no mesh is built, no field is written. The change is to a comparator and its
effect is re-derivable from artifacts already on disk. **No re-grade is requested
in this document** — whether T23G2 is re-graded under a repaired comparator, and
what its record then says, is a separate question and `verification`'s to
sequence.

`cost_basis = NOT APPLICABLE — no compute proposed`.

---

## 9. WHAT WE DID NOT DO, STATED SO IT IS NOT ASSUMED

- **We did not edit `analyse_t23g2.py`, `mark_done_t23.py`,
  `scripts/roache_triple.py` or `T23G2_PREREGISTRATION.md`.** Verified: the
  commit landing this petition touches this file only.
- **We did not re-grade and we did not launch anything.**
- **We did not write the repair.** No patch is attached, deliberately: a patch
  would invite the repair to be judged as already made.
- **We did not test the proposed behaviour.** We have not driven a mutated
  `gate_order` to confirm it returns `NOT A RESULT` on this row, so the claim in
  §2 that the change is restrictive rests on **reading** `:1081-1083`, not on
  running it. **That is an argument from code, not a measurement, and is labelled
  as such.**
- **We have not ruled on any of this.** A lane found it; the record caveats it;
  `verification` decides it.
