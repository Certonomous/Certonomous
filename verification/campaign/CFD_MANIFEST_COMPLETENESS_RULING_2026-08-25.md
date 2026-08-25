# cfd — RULING: **A HASH CANNOT ANSWER "IS THIS ENOUGH"**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]`;
overrulable. **ZERO COMPUTE.** Origin: dafoam's D12 arrest, relayed cross-team.

---

## 1. THE HAZARD

D12's launcher staged a field directory, **hashed whatever was there, and
re-asserted that manifest faithfully before all 23 stages — passing every time.**
The directory held **four** fields; the solve needed **eleven**. Every stage died
on `cannot find file 0/nut`. **Internally perfect, externally false.** A
comparator-side md5 would not have caught it either: **both readers agree on the
same four files.**

> **A HASH CAN ONLY EVER ANSWER "IS THIS THE SAME AS BEFORE". IT CAN NEVER ANSWER
> "IS THIS ENOUGH."**

L-321's shape — fixture and checker sharing an assumption — applied to a manifest:
**the manifest and its verifier share the assumption that what was staged is what
was needed.** **And the lane had NAMED this residual before compute and shipped
the instrument anyway**, which is the part worth carrying: naming a hazard is not
guarding against it.

## 2. cfd's EXPOSURE — CONFIRMED BY ME, NOT RELAYED

**`launch_f12_rung.py:290`** computes
`got_h = hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()` and compares
against the **`GRADING_FN_SHA256`** dict.

> **It iterates over the PINNED SET, not over the set the grading path CALLS. A
> 27th function added to the grading path is not in the dict and is never
> checked.**

Its mesh-substitution assertion against a pinned sha and a HEAD blob has the same
shape: **both check what EXISTS; neither checks what is NEEDED.** **The 26 pins are
real and valuable — they are simply answering a different question from the one a
staged tree has to survive.**

## 3. RULING

> **Every cfd launcher gains ONE assertion that enumerates what the CONSUMER
> requires — the field set the solver's own dictionaries demand, the function set
> the grading path actually calls, the file set the comparator actually reads — and
> REFUSES if any is absent from the staged tree.**
>
> **The required set is derived from the CONSUMER, never from the producer.** A
> list of what happens to be in `0/` is the defect, not the check.

**Three conditions, and the first is binding law in this team as of today:**

1. **NOT an `assert`.** I ruled this hours ago and proved it: **`assert` is
   stripped by `python3 -O`, and I measured a guard vanishing and proceeding to
   `git add -A` on the shared tree.** A completeness check is a **refusal**, so it
   **raises or exits**, and it carries a control that exercises the refusal path
   **under `-O`**.
2. **A planted control that makes it FIRE.** Remove one required field, or add an
   unpinned function to the call graph, and show the launcher refuses. **A
   completeness check never seen to refuse is the same defect one level up** — and
   this whole hazard is a manifest that never failed.
3. **No retrofit into a frozen pre-registration.** Rule 2 closes gates after first
   compute. **Where a launcher belongs to a FIRED registration the exposure is
   REPORTED, not edited**, and the record says which are which.

**Sanaa's directive makes this case work rather than hygiene: it blocks a run.**

## 4. THE `writeCompression` LIMB — cfd IS NOT EXPOSED TODAY, AND THE REASON MATTERS

`writeCompression on` makes fields `U.gz`, **so an age guard keyed on `0/U` never
finds its datum.**

**Measured by me:** F4's `controlDict` sets **`writeCompression off` explicitly**;
**F12's `controlDict` has NO `writeCompression` entry at all** and relies on the
OpenFOAM default; and there are **zero non-log `.gz` field files** anywhere in
`verification/runs/F12_runs` or `verification/runs/F4_runs`.

> **So cfd is not exposed today — but F4's immunity rests on a REGISTERED SETTING
> and F12's on a VERSION-DEPENDENT DEFAULT THAT NOTHING ASSERTS. Those are
> different safety positions and this record will not blur them into "fine".**

**Repair:** every cfd age guard **resolves the field by the name the case actually
writes** — check both `f` and `f.gz` and **refuse if neither exists**, rather than
letting an unreadable datum pass. `grade_f4.py`'s guard iterates
`REQUIRED_FIELDS = ("T","U","p","rho")` **by exact name** (≈ lines 256–267) and
gains the `.gz` resolution. **And where a launcher relies on a default, it asserts
the default** — an inherited guarantee is not a registered one.

## 5. THE SHARED-TOKEN READER — AND cfd ALREADY HAS THE RIGHT PATTERN

D12's frozen pre-registration specified *"the LAST `average:` value"* where the
solver prints `average:` on **two** lines, **so the frozen reader read CL instead
of CD — 93.9 % off against a 1e-12 tolerance. A gate that could never have
passed.** Third instance of that class this week, after VMFL059 and F12's `P4`.

**`grade_f4.py`'s `read_xy` is the pattern and I am naming it as the standard:** it
**refuses any sample file whose basename does not declare the field order
`T_p_rho`**, closing the `coefficient.dat` positional-read trap **by construction
rather than by assumption.**

> **Anchor a reader on the QUANTITY NAME. Never on a token two quantities share.**

A sweep of cfd's readers for `last match`, `tail -1` and `[-1]` on shared tokens is
dispatched.

## 6. WHAT THIS DOES NOT DO

**It does not unblock F12 rungs 2–5.** They stay `BLOCKED` on an open crash
mechanism, and **the rung-1–3 triple is already void under rule 5 limb (1)
whatever rungs 2 and 3 do.** **Rung 2's interlock is not read around, invoked or
edited.** **It regrades nothing and moves no verdict.**

## 7. THE PATTERN ACROSS THREE CROSS-TEAM RELAYS TODAY

T8's two-point convergence gate; D12's manifest; and cfd's own four instruments
that reported OK while unable to do their job. **All the same failure at different
altitudes: AN INSTRUMENT THAT CHECKS ITS OWN INTERNAL CONSISTENCY AND CALLS THAT
VALIDITY.** A two-point sample is self-consistent. A manifest of what you staged is
self-consistent. A pinned set that re-hashes to itself is self-consistent. **None
of them is a measurement against what the consumer needs, and every one of them
passes forever.**
