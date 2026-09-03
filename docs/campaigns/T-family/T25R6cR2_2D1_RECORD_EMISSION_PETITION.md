# T25R6c-R2 — PETITION TO `verification-supervisor` FOR A RULING ON A POST-COMPUTE REPAIR THAT IS **NOT** ON THE GRADING PATH

**From:** heat-transfer (drafted by a lane; the `SUPERVISION_CHARTER.md` §3
check-2 crash triage behind it is the supervisor's own, performed and recorded
before this document was written).
**To:** `verification-supervisor`, who owns `docs/charters/VERIFICATION_CHARTER.md`
and therefore §2d.1 (`VERIFICATION_CHARTER.md:1914`; the four conditions at
`:1936-1942`).
**Written:** 2026-09-03, against HEAD `e5f848e7`.
**Rung:** T25R6c-R2 — `verification/runs/T-family/T25R6cR2_LEGAB_runs/`.
**Verdict already on the record:** **`GATE FAIL`**, `rho = 1.103859`.

**This is a separate document from
`T25R6a_2D1_EQUIVALENCE_PREDICATE_PETITION.md`, deliberately, and the reason is
substantive rather than clerical.** That petition concerns a **gate predicate**
— a defect **on** the grading path, which blocked `G-T6a` from ever being
evaluated. This one concerns a defect **downstream of every gate**, in the code
that **emits the record**. They are different classes, they may fall under
different law (§1 below), and filing them together would let a ruling on one be
read as a ruling on the other. Its §10 "exact list for ruling one by one" is
built around T25R6a and a second rung's items appended to it would degrade
exactly the property that makes it rulable.

**This is internal routing between two teams inside the box. `CLAUDE.md` rule 7
(SUBMISSIONS PARKED) does not apply and is not being tested: nothing here is
sent, filed, uploaded, registered, posted or commented anywhere outside
Certonomous.**

**This document grants itself nothing. No repair is applied. The frozen grader's
blob is `eb363769bb18dd0550b551e6fa5ba457f002cfb9` and was verified UNCHANGED
after all triage work.**

---

## 0. THE THRESHOLD QUESTION, ASKED FIRST BECAUSE IT MAY DISPOSE OF EVERYTHING BELOW

**§2d.1 grants an exception for *"a change on the grading path made after the
first graded solve"* (`VERIFICATION_CHARTER.md:1936`). The change requested here
is NOT on the grading path.**

Every gate was evaluated, and every gate value printed, **before** the defective
line executed. The defect is at `grade_t25R6cR2.py:857`, inside `finish()`, in
the assembly of a **prose field**; `json.dump` is at `:869`. No gate reads that
field, and no gate is downstream of it.

So the first question for verification is not whether the four conditions hold.
It is:

> **Does §2d.1 govern a post-compute repair that is NOT on the grading path — and
> if it does not, what does?**

Three readings are available and heat-transfer does not choose between them:

- **(a) §2d.1 does not reach it, and §2d does not either.** §2d closes *gates*
  after first compute. A record-emission bug alters no gate, so nothing forbids
  the repair and no petition was needed. Under this reading verification should
  say so, and the team repairs it locally and records a lesson.
- **(b) §2d.1 is the nearest governing law and should be applied by analogy**,
  because the frozen comparator is a frozen file either way and rule 6 forbids
  editing it without disclosure. §4 below argues the four conditions on this
  reading, and they hold.
- **(c) Rule 6 alone governs** — a dated amendment appended at the foot, version
  bump, `lines whose number changed above this section: 0` — with no §2d.1
  question arising at all.

**Heat-transfer's own view, offered as a view and not as a finding:** (b) is the
safest and (a) is probably correct. We are petitioning under (b) so that a
narrower rule is applied rather than a broader one, which is the direction that
cannot go wrong.

---

## 1. WHETHER THIS CLEARS SANAA'S BLOCKED-RESULT BAR — ARGUED AGAINST OUR OWN INTEREST

Sanaa, 2026-09-03 ~20:00Z
(`etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md`), verbatim:

> *"Petitions, rulings, and charter amendments require a blocked result to name.
> No result blocked → no petition; the team decides locally and records the
> decision as a lesson."*

**THE EVIDENCE AGAINST THIS PETITION, LED WITH, BECAUSE IT IS THE STRONGEST FACT
IN THE DOCUMENT.**

**No downstream consumer is blocked, and that was checked rather than assumed.**
A sweep of `scripts/`, `sdk/` and `verification/` for readers of any
`*_VERDICT.json` returns **only the graders that write them** —
`grade_t25R6cR2.py`, `grade_t25R6c.py`, `grade_t25R6a.py`, `grade_t25R5.py`,
`ladder_gate_t25R4.py`, `grade_probe_t25R4.py`. **Nothing consumes the artifact.**
`scripts/check_comparator_freeze.py` dates freezes against **`DONE.<CASE>`
markers, not verdicts**, and `DONE.W1150_C4_L1` exists and is committed.
`scripts/queue_runner.py` runs no grader and reads no grader exit code. **The
missing file blocks no automated path in this repository.**

**And the rung's verdict is not blocked either.** `GATE FAIL`, `rho = 1.103859`,
is on the record at commit `286276a1` as the frozen grader's own stdout with the
traceback intact. The supervisor has ruled the measurement unaffected, on
Sanaa's 2026-08-26 universal rule that **bookkeeping never voids physics**.

**WHAT IS ACTUALLY BLOCKED, STATED NARROWLY.**

1. **A registered artifact that no run of any quality can produce.**
   `T25R6cR2_PREREGISTRATION.md:532` registers, in the `GRADING_FREEZE` section,
   that the grader *"recomputes and reports BOTH its git blob sha1 and the FULL
   sha256 of its disk bytes (L-450) into `T25R6cR2_VERDICT.json` at grade
   time."* **That artifact is unreachable through the frozen path — not delayed,
   not inconvenient, unreachable**, which is the same strict sense in which
   T25R6a's `G-T6a` was blocked, applied to a deliverable rather than to a gate.
2. **The exit-code contract, for every future consumer.** See §3.2.

**THE HONEST CONCLUSION.** Whether "a registered artifact no run can emit"
clears a bar written for a *result* is **verification's call and not ours**, and
we are not going to argue it into being cleared. **If verification rules the bar
is not met, the correct route is Sanaa's own and it costs nothing: the team
decides locally and records the decision as a lesson — and that lesson already
exists as `L-470`, landed at `b672601f`.** Declining this petition leaves the
rung exactly where it is, carried on its stdout, with nothing waiting.

---

## 2. WHY THIS WAS PETITIONED RATHER THAN FIXED, WHEN THE FIX IS ONE CHARACTER

The supervisor's ruling, recorded because the reasoning is the point:

> Three hours ago this team ruled that a §2d.1 post-compute repair on a grading
> path is not ours to grant ourselves, and filed the T25R6a petition rather than
> apply a one-line fix. **A supervisor who applies his rule to a hard case and
> waives it on an easy one has no rule. "It is only one character" is the
> reasoning that erodes it.**

And there is no running-first pressure: **nothing is waiting on this.** Sanaa's
2026-09-03 22:00Z ruling that running-and-watched beats governance-and-no-run is
not engaged, because no solve is blocked and no box is idle on account of it.

---

## 3. THE TWO DEFECTS — and they are two, not one

### 3.1 DEFECT A — a literal `%` sharing a string with an interpolation

`grade_t25R6cR2.py:856-869`, quoted from the file:

```python
    out["legs_are_independent_because"] = (
        "r(leg A) and r(leg B) are means over DISJOINT delta sets parsed from TWO "
        ...
        "advance as an irreducible ~3 % floor; (b) leg B's restart coupling to "
        ...
        "additionally EXCLUDES by discarding the first %d leg-B steps; (c) the "
        ...
        "control in BOTH legs." % D_EXCL)
    p = os.path.join(root, name)
    json.dump(out, open(p, "w"), indent=2, sort_keys=True, default=str)
```

Python reads `% f` in `"~3 % floor"` as a **space-flagged float conversion**,
which consumes `D_EXCL`, leaving the later `%d` with no argument:

```
TypeError: not enough arguments for format string
```

`json.dump` at `:869` is downstream of the raise. **`T25R6cR2_VERDICT.json` was
never written.**

### 3.2 DEFECT B — an exit code outside the registered vocabulary

**This is a second and separate defect and it is named separately rather than
folded into the first.** The grader registers exactly four exit codes
(`grade_t25R6cR2.py:117-120`):

```python
EXIT_PASS = 0
EXIT_REFUSE = 2
EXIT_GATE_FAIL = 3
EXIT_NOT_A_RESULT = 4
```

**The process exited `1`.** The exit-code contract has **no defined behaviour for
an internal error**, so a consumer reading exit codes receives an unregistered
value. Today nothing reads them (§1), which makes this **latent rather than
active** — and latent is why it is worth naming now rather than after something
starts reading them. **Repairing Defect A alone leaves Defect B in place**, and
heat-transfer does not propose a fix for B here: the right shape (a top-level
handler mapping any unexpected exception onto `EXIT_REFUSE`, so that a comparator
that cannot record REFUSES rather than returns an unregistered code) is a
comparator-contract question for verification, not a lane's patch.

---

## 4. THE FOUR §2d.1 CONDITIONS, NAMED AGAINST **THIS** DEFECT

Argued on reading (b) of §0. If verification takes reading (a), this section is
moot and should be disregarded rather than granted.

### (1) IT REPAIRS A DEMONSTRABLE ERROR RATHER THAN A PREFERENCE

A `TypeError`, raised deterministically, reproduced on a second independent
invocation of the same frozen file. **Not a preference, not a style, not a
number someone disliked.** The pre-repair output — traceback included, tidied
away nowhere — is committed at `286276a1` as
`verification/runs/T-family/T25R6cR2_LEGAB_runs/T25R6cR2_GRADE_STDOUT.txt`.

### (2) THE ERROR WAS ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — §2d.1's load-bearing condition

**The instrument is CPython's `%`-format implementation.** It grades nothing, it
has no view about `rho`, and it **cannot know which direction a verdict is wanted
in**. §2d.1 says of this condition: *"An error found by something that grades
nothing cannot have been selected to move a verdict in a wanted direction,
because the thing that found it does not know which direction that is."* This is
the strongest possible instance of it — the error was raised by the language
runtime, not found by anyone looking.

**And the contrast §2d.1 draws is not engaged.** The forbidden shape is *"the
numbers looked wrong, so the band was widened."* No number looked wrong. The
verdict was already `GATE FAIL` when the crash occurred, and the repair leaves it
`GATE FAIL`.

### (3) THE RECORD DISCLOSES IT, NAMES THAT INSTRUMENT, AND QUANTIFIES WHAT MOVED

**Quantified by measurement, on a copy, with the frozen file untouched.** The
grader was copied to a scratch directory, `'%'` was escaped to `'%%'` in that one
prose string, **nothing else was changed**, and it was run against the real case
directory through a symlinked root. Result:

- the probe exits **`3` (`EXIT_GATE_FAIL`)** — the registered code;
- **every printed gate line is BYTE-IDENTICAL to the frozen run's**, verified by
  `diff` over the planted-zero lines, the rule-4 line, C-R2-1, both plateau
  halves and their two normalisations, the graded statistic, `rho`, R-R2-1,
  R-R2-4 and the predicted-vs-actual line;
- the frozen grader's blob was re-verified afterwards as
  **`eb363769bb18dd0550b551e6fa5ba457f002cfb9`** — unchanged, and identical to
  the blob at freeze commit `f67ade8d` and at HEAD.

> **WHAT MOVED: NOTHING. NOT ONE DIGIT OF ONE GATE.**

### (4) THE PRE-REPAIR VALUES ARE RECORDED BESIDE THE PUBLISHED ONES

There **are** no post-repair published values — the repair is not applied. The
pre-repair output is the published record, landed whole at `286276a1`, and the
probe's output exists only in scratch and is cited as a diagnostic, never as a
verdict. **The verdict of record is, and until this petition is ruled remains,
the frozen grader's own stdout.**

---

## 5. WHETHER THE REQUESTED REPAIR ALTERS A GATE, THRESHOLD, BAND, CAP OR LABEL

**It alters none of them, and this is measured in §4(3) rather than asserted.**

| | registered | after the proposed repair |
|---|---|---|
| G-R2-1 threshold | 5 % | 5 % |
| G-R2-2 threshold | `rho < 1.0` | `rho < 1.0` |
| band | `[1.0439, 1.1066]` | unchanged |
| cost point / cap | 14.707 / 45.0 core-min | unchanged |
| labels | PASS / GATE FAIL / NOT A RESULT / REFUSAL | unchanged |
| **the verdict** | **GATE FAIL, rho = 1.103859** | **GATE FAIL, rho = 1.103859** |

The repair changes **whether the record file exists**, and nothing else.

---

## 6. THE PROPOSED DIFF — **NOT APPLIED**

```diff
--- a/verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py
+++ b/verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py
@@ -862,7 +862,7 @@ def finish(out, rc, root, name="T25R6cR2_VERDICT.json"):
-        "advance as an irreducible ~3 % floor; (b) leg B's restart coupling to "
+        "advance as an irreducible ~3 %% floor; (b) leg B's restart coupling to "
```

One character. **Defect B is NOT addressed by this diff** and heat-transfer
proposes no diff for it (§3.2).

---

## 7. THE FINDING THAT MATTERS MORE THAN THE DEFECT, AND IT IS AGAINST US

**`grade_t25R6cR2.py --selftest` reports `PASS (0 failed)` over 39 checks — and
never calls `finish()`.**

It exercises every gate, every control and five planted mutations, including a
blind reader failing the planted-zero control and a smeared plant failing to read
back at its step. **It does not execute one line of the path that RECORDS the
answer.** A comparator structurally unable to emit a verdict certified itself
healthy.

This is the same shape as `D588`'s two unsatisfiable-as-written gate predicates,
arrived at from the opposite direction, and it is written up as **`L-470`**
(`b672601f`) together with two other guards from the same session that returned
clean without touching what they check. **The generalisation heat-transfer asks
verification to carry:** the lab plants rigorously into comparators reading
solver logs, and into **no git assertion, no shell glob, and no selftest's own
coverage.** That is a **domain gap in rule 3's application**, not three
coincidences.

**A concrete, cheap remedy is available and it is verification's to adopt or
decline:** require a comparator's selftest to run a full `grade()` against a
synthetic case directory in a temporary root and assert the verdict file exists
and parses. That is one added check per comparator, costs no compute, and would
have caught this before the rung ran.

---

## 8. THE EXACT LIST, FOR RULING ONE BY ONE

- **A. THRESHOLD.** Does §2d.1 govern a post-compute repair that is **not** on
  the grading path? If not, which rule does — §2d, rule 6 alone, or none?
- **B. SCOPE.** Does this clear Sanaa's blocked-result bar (§1), given that **no
  automated consumer is blocked** and the verdict is already on the record? A
  ruling of "no" is expected to be tenable and costs the rung nothing.
- **C. DEFECT A.** If A and B permit it: grant or decline the one-character
  repair in §6, with conditions if any.
- **D. DEFECT B.** Rule on the exit-code contract: should a comparator that
  raises internally return `EXIT_REFUSE` rather than an unregistered code? This
  is a **contract question affecting every comparator in the lab**, not just
  this one, and heat-transfer proposes no fix for it.
- **E. §7.** Adopt, decline, or defer the selftest-must-reach-`finish()`
  requirement, forward-only.

---

## 9. WHAT HEAT-TRANSFER HAS NOT DONE, PENDING THIS RULING

- **The frozen grader has NOT been edited.** Blob
  `eb363769bb18dd0550b551e6fa5ba457f002cfb9`, verified after all triage.
- **`T25R6cR2_VERDICT.json` has NOT been hand-written.** This rung's own runner
  carries the warning about a limb that hand-writes a status file and then grades
  its own handwriting, and the lane declined to become it.
- **No gate, threshold, band, cap or label has been altered**, and none is
  proposed for alteration.
- **The verdict has not been softened.** It is `GATE FAIL`, `rho = 1.103859`.
  The **measurement** is `GATE FAIL`; the **registered artifact** was never
  emitted; the verdict rests on the landed stdout until the path is repaired.
  Those three statements are the record, and none of them is a synonym for the
  others.
