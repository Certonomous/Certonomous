# Curriculum item D6R-ACC2 — D6R's `ACC_mp` arm re-run at a repaired cap: RESULTS

**ITEM STATUS: `NOT A VERDICT ITEM`.** This is not a verdict, not a refusal, and not a deferral.
This item **poses no question that a DAFoam verdict answers**, and the reason is what the item
**is**, not anything that failed in it. Every number below carries its provenance tag per
`DAFOAM_CHARTER.md` §18.6, and every `MEASURED` tag names its artefact.

**Zero solver compute was spent producing this record, and no grading instrument was written.**
§5 says why not, and the reason is about the author.

---

# 1. WHY THERE IS NO VERDICT HERE, AND WHY THAT IS THE CHARTER WORKING RATHER THAN FAILING

`DAFOAM_CHARTER.md` §1:

> *"a DAFoam verdict is two rows — shipped and patched — or it is not a verdict about DAFoam."*

**This item has exactly ONE arm row: `ARM=ACC_mp ROW=PATCHED`** [MEASURED,
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint/ledger.txt`, the sole `ARM=`
line]. **No SHIPPED arm exists, and none was ever registered** — the item's whole purpose was to
re-run *one* arm of D6R at a corrected cap, and its `PREREGISTRATION.md` mentions neither
`SHIPPED` nor a two-row requirement anywhere in the document [MEASURED, grep over that file: zero
hits].

**THEREFORE D6R-ACC2 PRODUCES NO DAFOAM VERDICT — BY CONSTRUCTION, NOT BY FAILURE.** The two-row
requirement is not unmet here in the way a threshold is missed; it is **unsatisfiable by an item
shaped like this one**, and it would remain unsatisfiable on any re-fire, because a re-fire of one
arm is still one arm.

**THIS IS §1 BEING APPLIED, NOT NARROWED.** Ruled by the dafoam-supervisor, 2026-08-31. Saying
*"this item yields no verdict"* is the clause doing its work. Writing a one-row grader so that a
verdict could be emitted anyway would be **waiving** the clause, and retiring or narrowing a
charter clause is reserved to Sanaa (`CLAUDE.md` FIRST-ACTION rule, reserved list).

## 1.1 A NOTE TO THE NEXT READER, WHO WILL BE TEMPTED TO "COMPLETE" THIS RECORD

**No `CLAUDE.md` rule-1 verdict word belongs in this item's status cell — not `PASS`, not `GATE
FAIL`, and NOT `NOT A RESULT`.** All six of those words answer the question *"what did the gate
say?"*, and **this item does not pose that question.** `NOT A RESULT` is the one most likely to be
reached for, because it sounds like the humble choice; it is not, because it asserts that a gate
was reachable and returned nothing. **Nothing here is missing. The record is complete as it
stands.**

---

# 2. WHAT THIS ITEM ACTUALLY BOUGHT — three real results, none of which needs a verdict word

## 2.1 THE RE-REGISTERED 240.0 CAP IS DEMONSTRATED ADEQUATE

| | |
|---|---|
| spend | **119.933 core-min** [MEASURED, `ledger.txt`: `core_min=119.933`] |
| registered cap | **240.0 core-min** [REGISTERED, `PREREGISTRATION.md` §7, frozen `4e4adf66`] |
| fraction of cap used | **0.4997** [DERIVED] |
| exit | `rc=0`, `inspect(exit,oomkilled)=[0 false]` [MEASURED, `ledger.txt`] |
| wall | **1,799 s** against a **3,510 s** in-container deadline — 51.3 % [MEASURED, `ledger.txt`] |

**The arm finished on its own, comfortably inside the cap, and was not stopped by anything.** The
cap was not merely un-breached — it was breached by *nothing like* a near miss, which is what
makes it a demonstration of adequacy rather than a lucky pass.

## 2.2 THE PREDECESSOR'S CAP IS NOW FALSIFIED BY MEASUREMENT, NOT BY ARGUMENT

`D6R-PREREG-DEF-1` held that D6R's `ACC_mp` cap of **30.0 core-min** priced a program the arm does
not run. That was argued from an extrapolation (`PREREGISTRATION.md` §2a, `1,685.98 s` from a
seven-segment model, six segments measured and one interpolated). **The run has now measured it,
and the defect is WORSE than the extrapolation claimed:**

| against D6R's registered figures | extrapolated at freeze | **MEASURED by this run** |
|---|---|---|
| vs the **30.0 core-min** cap | 3.75× | **4.00×** [DERIVED, `119.933 / 30.0`] |
| vs the **360 s** deadline | 4.68× | **5.00×** [DERIVED, `1799 / 360`] |

**D6R's cap would have killed this work at about a quarter of the way through** — `30.0 / 119.933`
= **25.0 %** [DERIVED]. **The defect finding no longer rests on an interpolated segment. It rests
on an arm that ran to completion.**

## 2.3 A CALIBRATION DATUM, ALREADY LANDED

**`C-220`** in `docs/COST_CALIBRATION.md`: 119.933 measured against **112.40 REGISTERED**, ratio
**1.0670**, with the gap closed segment-by-segment to the second. That row is landed and is not
restated here.

---

# 3. THE `G1_completion` READING — an **UNREGISTERED DIAGNOSTIC**, and never a verdict

`PREREGISTRATION.md` §6 outcome 1 says the arm *"is graded against D6R's frozen `G1` completion
clauses for a SCRIPT arm."* **That names a CLAUSE SET. It names no instrument, no argv and no
md5.** There is no grading script in this item's directory [MEASURED, directory listing].

The nearest available instrument, `cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_grade.py`, was run
against this run root as a **diagnostic**. Its output is preserved beside this record at
`cases/dafoam/ladder-a/A2/curriculum_D6RACC2/D6RACC2_unregistered_diagnostic.json`:

| gate | reading |
|---|---|
| `G1_completion` | **`PASS`** |
| `G12_placement` | `PASS` |
| `G9_toolchain` | `PASS` |
| `G10_caps` | `GATE FAIL` — **DISCARDED, see §4** |
| all `G-D6R-*` | `NOT A RESULT` (they need arms this item never had) |

**EVERY ONE OF THOSE READINGS IS AN UNREGISTERED DIAGNOSTIC AND NONE IS A VERDICT.** `d6r_grade.py`
is **D6R's** registered instrument, not this item's; it was frozen for a four-arm item and it
composes a whole-item verdict against **D6R's** registration. **A reading from an instrument an
item did not register is a diagnostic, whatever the reading says** — and that holds for the
`PASS` exactly as much as for the `GATE FAIL`. It may be cited as an observation. It may not be
cited as this item's grade.

**The run root was not modified by that probe**, established with a control rather than assumed:
the newest file anywhere in the run root is its own `CHAIN_DONE` at **2026-08-31 00:23:31**, and
the same reader, pointed at this case directory, does see files written minutes ago [both
MEASURED, `find -printf '%T@'`]. **A "nothing newer" from a reader not shown able to see a newer
file would not be evidence** (`CLAUDE.md` rule 3).

---

# 4. THE DISCARDED `G10_caps` — **A FABRICATED ADVERSE VERDICT ON A CLEAN ARM**, and this is the section to remember

**`G10_caps` returned `GATE FAIL`. It is DISCARDED, and the mechanism is exact.**

The instrument's own report cell names the caps it applied [MEASURED,
`D6RACC2_unregistered_diagnostic.json`, `G10.deadline_plus_allowance_inverts_to_cap`]:

```
{"ACC_mp": 30.0, "F_mp": 300.0, "O_mp": 2900.0, "REF_off": 40.0}
```

**It applied `ACC_mp: 30.0` — D6R's cap. THE EXACT CAP THIS ITEM EXISTS TO REPLACE.** This item is
registered at **240.0**, it spent **119.933**, and it used **49.97 %** of its own cap. The
instrument compared that spend against a figure from a **different registration, pricing a
different program**, and returned an adverse verdict on an arm that finished comfortably inside
every limit that governs it.

**THIS IS `DAFOAM_CHARTER.md` §18.1's CATEGORY ERROR ARRIVING AT THE GRADING END.** §18.1 forbids
pricing an arm from a row that measured a different program. §18.6 supplies the reporting-end
companion: *a ratio whose denominator prices a different program is not reportable AT ANY TAG,
because there is no tag that makes a category error true.* **A gate whose threshold prices a
different program is the same defect wearing a verdict word instead of a ratio.**

**AND THE DEMONSTRATION IS WORTH MORE THAN THE DIAGNOSTIC IT CAME WITH.** Had this reading been
filed as a grading, the record would now carry a `GATE FAIL` against `D6R-ACC2` — **an item whose
entire purpose was to repair the very cap that produced the failure.** The repair would have been
recorded as a failure, by the instrument the repair made obsolete. **That is the concrete cost of
grading an item with a predecessor's frozen comparator, and it is why §3's "unregistered
diagnostic" label is doing real work rather than being punctilious.**

---

# 5. WHY NO GRADING INSTRUMENT WAS WRITTEN — including a disqualification of the author

**A record that says why an instrument does not exist is stronger than one that quietly lacks
one.** Three reasons, in ascending order of how much they bind.

## 5.1 The two-row requirement (§1) — an instrument could never pass

A grader built to emit a two-row verdict on a one-arm item refuses on every input, forever: a
**dead lever by construction**. A grader built to emit a one-row verdict waives §1, which is
reserved. **There is no third instrument.**

## 5.2 "Frozen before it grades" was never available — and §2d.1 is NOT reached for

`CLAUDE.md` rule 2: *"The grading path is fixed at the pre-registration commit."* The timeline
[all MEASURED, `git log` on the pre-registration path and the run root's own stamps]:

| event | when |
|---|---|
| `PREREGISTRATION.md` frozen at **`4e4adf66`** | **2026-08-30 23:24:10Z** |
| first compute — the arm's container starts | **2026-08-30 23:53:32Z** (29 min later) |
| `chain=COMPLETE` | **2026-08-31 00:23:31Z** |
| dated addenda on the pre-registration | **0** |

**The path fixed at `4e4adf66` is a clause reference and nothing more.** Registering an invocable
grading path now would fix the grading path **sixteen hours after the answer was on disk**. That is
not freezing before grading; it is freezing after the run.

**`VERIFICATION_CHARTER.md` §2d.1 IS NOT REACHED FOR, AND THE REFUSAL IS DELIBERATE.** That
exception exists for repairing a demonstrable error in an instrument, not for **supplying a
missing instrument after the answer is known.** This family has refused §2d.1 five times, and
using an exception where the ordinary path is open is an exception being widened. **The ordinary
path here is that the item yields no verdict — §1 — and that path is open.**

## 5.3 THE AUTHOR IS DISQUALIFIED, AND THE AUTHOR IS THE ONE WRITING THIS

**I ran the `d6r_grade.py` probe in §3 before any instrument was proposed, and I saw its output.
I know that `G1_completion` returns `PASS` on this run root.** Any grader I then wrote, I would
write **knowing what it must emit in order to pass.**

`CLAUDE.md` rule 2: *"The freeze is the document's entire evidentiary content: it proves the gate
could not have been chosen to fit the answer."* **I cannot supply that proof for an instrument I
author after seeing its output.** The probe was the right call — it produced §4, which is the most
valuable thing in this record — and it also **contaminated me as an author of the instrument it
was probing.** Both are true, the contamination is my own doing, and it is disclosed here rather
than worked around.

**If an instrument is ever written for an item of this shape, it must be written by someone who
has not seen §3's table.**

---

# 6. WHAT IS OWED, AND WHAT IS NOT

1. **Nothing is owed on the verdict. There is no verdict to owe** (§1). The record is complete.
2. **`C-220` is LANDED** (§2.3). **No further calibration row is filed**, and one is not owed for
   this record, which spent no compute. `docs/COST_CALIBRATION.md` is in any case **append-blocked**
   at `scripts/append_record.py` exit 7 on its D549 shape audit, over strike-form lines belonging
   to another item.
3. **`D6R-CAP-FRAME-2` is inherited unrepaired**, by design and as `PREREGISTRATION.md` §5 states.
   Nothing here repairs or re-opens it.
4. **D6R's own verdict is untouched.** D6R is `NOT A RESULT`, `curriculum_D6RG` graded it, and
   `PREREGISTRATION.md` §5 forbids this item from re-opening, revising or repairing that. **This
   record does none of those things.**

---

**Record written 2026-08-31 by a dafoam lane. Item status `NOT A VERDICT ITEM`, ruled by the
dafoam-supervisor on `DAFOAM_CHARTER.md` §1 applied to a one-arm item. No gate, threshold, band,
cap or label is moved by this document, and no instrument is registered by it.**
