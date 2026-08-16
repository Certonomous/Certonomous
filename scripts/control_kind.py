r"""Which kind of positive control a sweep ran, and whether its zero is earned.

THE DISTINCTION THIS MODULE EXISTS TO MAKE MECHANICAL
=====================================================
A positive control proves **REACHABILITY** or **RECOGNITION**, and these are not
the same thing. Both get written up the same way -- *"the control fired, so the
zero is a measurement"* -- and only one of them earns that sentence.

    REACHABILITY   The sweep could OPEN the files. You planted a token, the
                   reader found it, so the reader works. This says nothing
                   whatever about whether the pattern would recognise the claim
                   you are looking for.

    RECOGNITION    The pattern matches the CLAIM CLASS in forms other than the
                   literals you already thought of. Planted in the claim's own
                   vocabulary, in VARIANTS, and every variant found.

THE MEASURED FAILURE, which is why one inflected verb is the whole lesson: a
sweep returned a false zero because *"the tie **is** lost"* and *"the tie **was**
lost"* share no 5-gram. The reader had opened every file. The reachability
control fired. The zero was still false.

WHY THE CALLER DOES NOT GET TO DECLARE THE KIND
===============================================
The kind is DERIVED from the evidence supplied, never from a label the caller
types -- the same reason `check_rung_attribution.py`'s `--tag` never decides a
verdict. An agent that can write `kind="recognition"` will write it, and a
convention that is satisfied by typing a word is not a control.

A ledger entry is promoted to RECOGNITION only when all three hold:

  1. **Two or more distinct forms were planted.** One form is a reachability
     probe however it is described.
  2. **No form is a substring of another**, compared case-folded and
     whitespace-normalized. This is the computable proxy for "a variant a
     literal search for its sibling would MISS", and it is exactly the is/was
     case: `the tie is lost` is not a substring of `the tie was lost`, so the
     pair qualifies, while `tie lost` and `the tie lost` do not.
  3. **Every planted form was found.** A control that did not fire is a broken
     instrument, and a broken instrument yields UNKNOWN, never PASS.

Anything else is recorded as REACHABILITY with the reason stated, so the report
says which one the sweep actually has rather than which one it hoped for.

WHAT A ZERO IS WORTH, BY KIND
=============================
    hits > 0              the zero question does not arise; findings stand.
    hits == 0, RECOGNITION fired    the zero is a measurement of absence.
    hits == 0, REACHABILITY only    UNKNOWN. The sweep is not known to be able
                                    to see the thing it reports absent.
    hits == 0, no control at all    UNKNOWN, and said so loudly.
    any control did not fire        UNKNOWN. The instrument is broken.

A NEGATIVE FORM MAY ALSO BE PLANTED and is scored separately: a string that the
pattern MUST NOT match. It never promotes a control to RECOGNITION -- it guards
against a pattern so loose that it would match anything, which is the opposite
failure and produces false hits rather than a false zero.

WHAT THIS MODULE CANNOT DO
==========================
It cannot tell whether your variants are the RIGHT variants. Nothing can: that
is a claim about the claim class, and it is the judgement the author is paid
for. What it can do is refuse to let one planted literal be reported as
evidence that a pattern recognises a class, and print the difference on every
run so a reader is never left inferring it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

REACHABILITY = "REACHABILITY"
RECOGNITION = "RECOGNITION"
BROKEN = "BROKEN"
NONE = "NONE"

#: Verdicts a caller maps onto its own exit contract.
ZERO_IS_A_MEASUREMENT = "ZERO_IS_A_MEASUREMENT"
ZERO_IS_UNSUPPORTED = "ZERO_IS_UNSUPPORTED"
NOT_A_ZERO = "NOT_A_ZERO"


def _norm(text: str) -> str:
    """Case-folded, whitespace-collapsed, for the substring comparison."""
    return re.sub(r"\s+", " ", text).strip().casefold()


@dataclass
class Control:
    """One planted control, with its own classification and its reason."""

    name: str
    vocabulary: str
    planted: dict[str, bool]
    negative: dict[str, bool] = field(default_factory=dict)

    @property
    def all_fired(self) -> bool:
        return bool(self.planted) and all(self.planted.values())

    @property
    def negatives_held(self) -> bool:
        """A negative form must NOT have been matched."""
        return not any(self.negative.values())

    @property
    def distinct_forms(self) -> list[str]:
        """Forms none of which is a substring of another, case/space-folded."""
        forms = list(self.planted)
        keep = []
        for form in forms:
            a = _norm(form)
            if any(a != _norm(other) and a in _norm(other) for other in forms):
                continue
            keep.append(form)
        return keep

    def classify(self) -> tuple[str, str]:
        """(kind, why). Derived from evidence; never from a caller's label."""
        if not self.planted:
            return NONE, "no form was planted at all"
        if not self.all_fired:
            missed = sorted(f for f, hit in self.planted.items() if not hit)
            return BROKEN, (f"{len(missed)} planted form(s) were NOT found, so "
                            f"the instrument is not known to work: "
                            f"{', '.join(repr(m) for m in missed)}")
        if not self.negatives_held:
            matched = sorted(f for f, hit in self.negative.items() if hit)
            return BROKEN, (f"a negative form WAS matched, so the pattern is "
                            f"too loose to be believed: "
                            f"{', '.join(repr(m) for m in matched)}")
        if len(self.planted) < 2:
            return REACHABILITY, ("only one form was planted -- that proves the "
                                  "sweep could OPEN the corpus, not that its "
                                  "pattern recognises the claim class")
        distinct = self.distinct_forms
        if len(distinct) < 2:
            return REACHABILITY, (
                "the planted forms are not mutually independent: every one is a "
                "substring of another, so a literal search for one would find "
                "the others and nothing about recognition has been shown")
        return RECOGNITION, (
            f"{len(distinct)} mutually independent forms in the vocabulary of "
            f"{self.vocabulary!r}, all found"
            + (f"; {len(self.negative)} negative form(s) correctly rejected"
               if self.negative else ""))


@dataclass
class ControlLedger:
    """Every control a sweep ran, and what its zero is therefore worth."""

    claim_class: str
    controls: list[Control] = field(default_factory=list)

    def plant(self, name: str, *, vocabulary: str,
              planted: dict[str, bool],
              negative: dict[str, bool] | None = None) -> Control:
        control = Control(name=name, vocabulary=vocabulary,
                          planted=dict(planted), negative=dict(negative or {}))
        self.controls.append(control)
        return control

    @property
    def kind(self) -> str:
        """The STRONGEST kind established, or BROKEN if any control failed."""
        kinds = [c.classify()[0] for c in self.controls]
        if not kinds:
            return NONE
        if BROKEN in kinds:
            return BROKEN
        if RECOGNITION in kinds:
            return RECOGNITION
        return REACHABILITY

    def verdict_for(self, hits: int) -> tuple[str, str]:
        """(verdict, why) for a sweep that returned *hits* hits."""
        kind = self.kind
        if kind == BROKEN:
            why = "; ".join(c.classify()[1] for c in self.controls
                            if c.classify()[0] == BROKEN)
            return ZERO_IS_UNSUPPORTED, f"a control did not hold: {why}"
        if hits > 0:
            return NOT_A_ZERO, (f"{hits} hit(s) -- the sweep found something, so "
                                f"the question of what a zero would be worth "
                                f"does not arise here")
        if kind == RECOGNITION:
            return ZERO_IS_A_MEASUREMENT, (
                f"zero hits, under a RECOGNITION control for {self.claim_class!r}: "
                f"the pattern was shown to match this claim class in forms other "
                f"than the ones searched for, so the absence is measured")
        if kind == REACHABILITY:
            return ZERO_IS_UNSUPPORTED, (
                f"zero hits, but only a REACHABILITY control was run. The sweep "
                f"is known to have OPENED the corpus and is NOT known to be able "
                f"to recognise {self.claim_class!r} in any form it was not "
                f"already searching for. This zero is not a measurement of "
                f"absence")
        return ZERO_IS_UNSUPPORTED, (
            f"zero hits and NO control was run at all, so nothing distinguishes "
            f"this from a sweep that read nothing")

    def render(self, hits: int, width: int = 78) -> str:
        """The block a check prints. The kind is printed whatever it is."""
        verdict, why = self.verdict_for(hits)
        out = ["-" * width,
               f"CONTROL KIND: {self.kind}   (claim class: {self.claim_class})"]
        for control in self.controls:
            kind, reason = control.classify()
            out.append(f"  {control.name}: {kind}")
            out.append(f"      {reason}")
            for form, hit in sorted(control.planted.items()):
                out.append(f"      planted  {'FOUND    ' if hit else 'NOT FOUND'}"
                           f"  {form!r}")
            for form, hit in sorted(control.negative.items()):
                out.append(f"      negative {'MATCHED  ' if hit else 'rejected '}"
                           f"  {form!r}")
        if not self.controls:
            out.append("  (none planted)")
        out.append(f"ZERO VERDICT: {verdict}")
        out.append(f"BECAUSE: {why}")
        return "\n".join(out)
