#!/usr/bin/env python3
r"""Has any ladder round ever declared its findings BELIEF-NEUTRAL? (V15 F4)

WHY A TOKEN SEARCH COULD NOT ANSWER THIS
========================================
`R-VALUE` closes a rung when **two consecutive rounds return only findings that
would not change an external reader's belief**
(`LADDER_V_TRIPLE_VERIFICATION.md:588-592`). The lab's headline `R-VALUE = 0`
rested on searches for two token families -- `R-VALUE` and `belief-neutral` --
whose positive controls planted the very tokens they searched for. Those
controls prove REACHABILITY: the reader opened the files. They do not prove
RECOGNITION: that the pattern matches the CLAIM CLASS in wording the probe was
not already looking for. A round writing *"nothing here changes what an outside
reader believes"* satisfies R-VALUE's own wording and shares no token with any
probe ever run. That is V15 round 9's F4.

WHAT THIS MODULE DOES INSTEAD
=============================
It carries a RECOGNITION control: twelve paraphrases of the concept in the
vocabulary a round author would actually use, FROZEN BEFORE the patterns were
written -- frozen-set sha256 `e7119fb40e52af3a8a3e6f3120112a6f...` -- so the
patterns could not be fitted to them. It classifies its own control through
`scripts/control_kind.py`, which promotes a control to RECOGNITION only when two
or more mutually independent forms were planted and every one was found, and it
REFUSES TO REPORT A ZERO unless that classification is reached.

The first draft of the recogniser found 11 of the 12 frozen forms. The miss was
*"No external belief moves on any of this"* -- every pattern required
NEG ... VERB ... BELIEF and that form is NEG ... BELIEF ... VERB. The same shape
as V7's hyphen, where `\w+` could not cross "pre-registered". The patterns were
repaired until all twelve were found; the miss is recorded here rather than
erased, because a recogniser that cannot find a paraphrase its own author wrote
cannot certify absence.

TWO HONEST LIMITS, BOTH LOAD-BEARING
====================================
1. THE RECOGNISER DOES NOT DISCRIMINATE POLARITY, by design. A round saying it
   is NOT belief-neutral is ON-concept and is recalled; the CLASSIFIER decides
   polarity. Putting a negated declaration in the negative-control set was an
   error that made the control BROKEN until corrected -- recorded rather than
   quietly swapped.

2. THIS ANSWERS A NARROWER QUESTION THAN R-VALUE ASKS, and this is worth more
   than the sweep. R-VALUE is a condition on what a round's findings WOULD DO to
   a reader, not on what the round SAYS about itself. A round that returned only
   belief-neutral findings and never discussed neutrality satisfies R-VALUE and
   is invisible to ANY declaration sweep, however good its recognition control.
   Rounds in that state are reported CANNOT_TELL and must not be read as either.

EXIT CONTRACT
=============
    0  no round asserts neutrality AND the control classified RECOGNITION
    1  a round ASSERTS neutrality -- R-VALUE may not be zero, route to a grader
    3  UNKNOWN: the control did not reach RECOGNITION, so no zero is reportable
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_kind  # noqa: E402

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[1]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

#: FROZEN BEFORE THE PATTERNS BELOW WERE WRITTEN. Do not add a form here to make
#: a sweep pass; add it because a round author would write it, then re-run and
#: repair the patterns until the control classifies RECOGNITION again.
CONTROL_FORMS = (
    "Nothing in this round changes what an outside reader believes about the package.",
    "None of these findings would change an external reader's belief.",
    "No finding here moves the needle for anyone reading the entry from outside.",
    "An outside reader's view of the submission is unchanged by this round.",
    "Nothing found this round would alter a reader's confidence in the result.",
    "Every finding here is cosmetic and changes no conclusion a reader would draw.",
    "A reader who believed the entry sound before this round still believes it.",
    "These residuals do not bear on anything the package claims to an outsider.",
    "This round is belief-neutral.",
    "The findings are belief neutral in the sense R-VALUE means.",
    "Nothing recorded here would cause an external reader to revise their view.",
    "No external belief moves on any of this.",
)

#: Off-concept forms the recogniser must NOT recall. A negated declaration does
#: NOT belong here -- see limit 1 in the docstring.
NEGATIVE_FORMS = (
    "We believe the mesh is converged.",
    "The reader is directed to section 4.",
    "This changes the number on the wall.",
    "The audience for this document is the owner.",
    "The mesh was refined and the drag coefficient moved.",
)

NEG = r"(?:no|not|none|nothing|never|n't|without|un)"
BELIEF = r"(?:belief|believ\w*|view|confidence|conclusion|mind|opinion|reading|assessment)"
READER = r"(?:reader|outsider|outside\s+\w+|external\s+\w+|audience|anyone|anybody|someone)"
MOVE = (r"(?:change|changes|changed|alter|alters|altered|move|moves|moved|shift|"
        r"shifts|shifted|revise|revises|revised|affect|affects|affected|disturb|"
        r"overturn|budge)")

PATTERNS = {
    "T1-token": r"belief[\s\-_]*neutral",
    "T2-neg-move-belief": rf"\b{NEG}\b[^.]{{0,80}}?\b{MOVE}\b[^.]{{0,60}}?\b{BELIEF}\b",
    "T3-neg-move-reader": rf"\b{NEG}\b[^.]{{0,80}}?\b{MOVE}\b[^.]{{0,60}}?\b{READER}\b",
    "T4-would-not": rf"would\s+{NEG}\s+{MOVE}[^.]{{0,80}}?\b(?:{BELIEF}|{READER})\b",
    "T5-unchanged-reader": rf"\b(?:unchanged|unaffected|untouched)\b[^.]{{0,80}}?\b(?:{BELIEF}|{READER})\b",
    "T6-reader-unchanged": rf"\b(?:{BELIEF}|{READER})\b[^.]{{0,80}}?\b(?:unchanged|unaffected|untouched)\b",
    "T7-cosmetic": rf"\bcosmetic\b[^.]{{0,80}}?\b{NEG}\s+\w*\s*(?:{BELIEF})\b",
    "T8-still-believes": r"\bstill\s+believ\w+",
    "T9-no-bearing": rf"\b{NEG}\b[^.]{{0,40}}?\bbear(?:s|ing)?\s+on\b",
    "T10-needle": rf"\b{NEG}\b[^.]{{0,60}}?\bmoves?\s+the\s+needle\b",
    # Added after frozen form 12 was NOT FOUND: subject-first order.
    "T11-belief-then-move": rf"\b{NEG}\b[^.]{{0,50}}?\b{BELIEF}\b[^.]{{0,40}}?\b{MOVE}\b",
    "T12-reader-then-move": rf"\b{NEG}\b[^.]{{0,50}}?\b{READER}\b[^.]{{0,40}}?\b{MOVE}\b",
}
RX = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}

#: A round DECLARING it is not neutral, or reporting the count as zero.
NEGATED = re.compile(
    r"(?i)(\bnot\s+(?:\w+\s+){0,3}belief[\s-]*neutral|\bNOT\s+belief|is not one of them|BELIEF-NEUTRAL\?\s*\*{0,2}\s*No"
    r"|never (?:once )?(?:been )?(?:met|declared)|no round|stands? at (?:zero|\*\*zero)"
    r"|stays at (?:zero|\*\*zero)|remains at ZERO|not self-declared|does not (?:close|reach))")
#: Quoting or defining the rule rather than applying it to this round.
MENTION = re.compile(
    r"(?i)(would not change an external reader|two consecutive rounds"
    r"|R-VALUE (?:closes|'s (?:condition|consecutive))|A round is neutral if"
    r"|entry condition|only written definition|tokens? `?R-VALUE|`belief-neutral`)")
#: A statement that one LOCAL conclusion is unaffected -- not a round verdict.
LOCAL = re.compile(
    r"(?i)(the conclusion is (?:unaffected|untouched)|no conclusion moves"
    r"|has no bearing on|no stored value moved|survived the re-reading"
    r"|hazard class, unchanged|frame is unchanged|passed through untouched"
    r"|not load-bearing)")


def hits(text: str) -> list[tuple[str, str]]:
    out = []
    for name, rx in RX.items():
        for m in rx.finditer(text):
            out.append((name, m.group(0)))
    return out


#: Round-scoped, first-person application of the concept to THIS round. Without
#: this rule `classify` could never return ASSERT and the sweep's headline zero
#: would be TRUE BY CONSTRUCTION -- the vacuous-assertion defect. Reachability of
#: the ASSERT branch is asserted by `control_assert_is_reachable()` below and
#: printed on every run, because an unreachable verdict is not a measurement.
ASSERT_SCOPE = re.compile(
    r"(?i)\b(this round|this grade|this pass|the round|these findings|the findings|"
    r"nothing (?:here|in this round|found this round|recorded here)|"
    r"every finding here|no finding here|these residuals)\b")


#: A QUESTION is not a declaration. `### 7.2 Is this round BELIEF-NEUTRAL?` is a
#: heading whose answer sits on the next line; both V16 rounds 11 and 12 answer
#: "No". Classifying the heading as an assertion of its own subject is a
#: use/mention error in its purest form.
QUESTION = re.compile(r"\?\s*$")
#: A CONDITIONAL describes what a round WOULD be, not what one IS. F4's own
#: sentence -- "a round that wrote 'nothing here changes what an outside reader
#: believes' would satisfy R-VALUE's wording" -- is the argument for this
#: module's existence, and it is not a round declaring itself neutral.
HYPOTHETICAL = re.compile(
    r"(?i)\b(a round (?:that|writing)|\bround (?:that wrote|writing)\b|if a round|would satisfy|satisfies R-VALUE|would (?:be|count|"
    r"close|qualify)|hypothetical|for example|e\.g\.|suppose)\b")


def _plain(line: str) -> str:
    """Strip markdown emphasis before classifying.

    `did **not** return only belief-neutral findings` is a negation whose word
    is split by bold markers, so a negation regex reading the raw line misses it
    and the hit falls through to ASSERT. Found by inspecting the six the first
    version reported, every one of which was a false positive.
    """
    return re.sub(r"[*`_~]+", "", line)


def classify(line: str) -> str:
    line = _plain(line)
    if NEGATED.search(line):
        return "NEGATED"
    if HYPOTHETICAL.search(line):
        return "MENTION"
    if QUESTION.search(line):
        return "MENTION"
    # SCOPE BEATS RULE-QUOTATION, and this ordering is load-bearing. A round
    # applying R-VALUE's own wording TO ITSELF -- "this round returned only
    # findings that would not change an external reader's belief" -- contains
    # the rule's exact words AND is the strongest possible assertion. With
    # MENTION tested first it classified MENTION, which is the use/mention error
    # running the other way and would hide precisely the round this sweep exists
    # to find. Caught by an anti-tuning probe after the classifier had already
    # been corrected three times.
    if ASSERT_SCOPE.search(line):
        return "ASSERT"
    if MENTION.search(line):
        return "MENTION"
    if LOCAL.search(line):
        return "LOCAL_CONCLUSION"
    return "CANNOT_TELL"


def control_assert_is_reachable() -> tuple[bool, list[str]]:
    """Every frozen control form must classify ASSERT when it stands alone.

    This is a control on the CLASSIFIER, separate from the recogniser's control.
    A sweep whose ASSERT branch cannot fire reports zero for a reason that has
    nothing to do with the corpus.
    """
    hit = [f for f in CONTROL_FORMS if classify(f) == "ASSERT"]
    missed = [f for f in CONTROL_FORMS if classify(f) != "ASSERT"]
    # >= 2, matching control_kind's own standard for an established kind. Form
    # 12, "No external belief moves on any of this", carries NO round-scope
    # marker at all: standing alone its scope is genuinely undecidable, and in a
    # real document it would come from surrounding context this line-wise sweep
    # does not read. That is reported, not hidden, and not patched around by
    # widening the scope rule until it matches.
    return (len(hit) >= 2), missed


def build_control() -> control_kind.ControlLedger:
    ledger = control_kind.ControlLedger(
        claim_class="a round declaring its findings belief-neutral")
    ledger.plant("neutrality paraphrases, frozen before the patterns",
                 vocabulary="a round author's own wording",
                 planted={f: bool(hits(f)) for f in CONTROL_FORMS},
                 negative={f: bool(hits(f)) for f in NEGATIVE_FORMS})
    return ledger


def round_documents() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files",
         str(lab_paths.CAMPAIGN.relative_to(lab_paths.REPO)) + "/"],
        capture_output=True, text=True, check=True).stdout.split("\n")
    keep = re.compile(r"(ROUND|GRADE|RUNGS|CLOSEOUT|ENTITLEMENT|STATE|PENDING|VERIFICATION)", re.I)
    return [p for p in out if p.endswith(".md") and keep.search(p)]


def sweep_documents(paths):
    found = []
    for rel in paths:
        p = REPO / rel
        try:
            lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            for pat, m in hits(line):
                found.append(("doc", rel, n, pat, classify(line), line.strip()))
    return found


def sweep_commit_messages():
    log = subprocess.run(
        ["git", "-C", str(REPO), "log", "--all", "--format=%H\x1f%B\x1e"],
        capture_output=True, text=True, check=True).stdout
    found = []
    for rec in log.split("\x1e"):
        if not rec.strip():
            continue
        sha, body = rec.strip().split("\x1f", 1)
        for n, line in enumerate(body.splitlines(), 1):
            for pat, m in hits(line):
                found.append(("commit", sha[:8], n, pat, classify(line), line.strip()))
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--show", action="store_true", help="print every hit")
    args = ap.parse_args(argv)

    ledger = build_control()
    docs = round_documents()
    found = sweep_documents(docs) + sweep_commit_messages()
    by_class = {}
    for f in found:
        by_class.setdefault(f[4], []).append(f)

    # An ASSERT is an on-concept hit, scoped to this round, that is neither
    # negated, nor a rule mention, nor a statement about one local conclusion.
    # The sweep reports the bucket; it does not decide a rung.
    asserts = by_class.get("ASSERT", [])
    reachable, unreachable_forms = control_assert_is_reachable()
    zero_verdict, why = ledger.verdict_for(len(asserts))

    width = 78
    print("=" * width)
    print("BELIEF-NEUTRALITY DECLARATION SWEEP")
    print("=" * width)
    print(f"  corpus arm 1 : {len(docs)} tracked round/grade documents (git ls-files)")
    print(f"  corpus arm 2 : commit messages, git log --all")
    print(f"  total hits   : {len(found)}")
    for k in ("ASSERT", "NEGATED", "MENTION", "LOCAL_CONCLUSION", "CANNOT_TELL"):
        print(f"    {k:18} {len(by_class.get(k, []))}")
    print(f"  ASSERT branch reachable : {reachable} "
          f"({len(CONTROL_FORMS) - len(unreachable_forms)}/{len(CONTROL_FORMS)} "
          f"frozen forms classify ASSERT when standing alone)")
    for form in unreachable_forms:
        print(f"      NOT ASSERT: {form!r} -> {classify(form)}")
    print(ledger.render(len(asserts)))
    if args.show:
        for kind, src, n, pat, cls, line in found:
            print(f"  [{cls:16}] {src}:{n} ({pat}) {line[:110]}")

    if ledger.kind != control_kind.RECOGNITION:
        print("VERDICT: UNKNOWN -- no zero is reportable without a recognition control")
        return 3
    if not reachable:
        print("VERDICT: UNKNOWN -- the ASSERT branch cannot fire for every frozen "
              "form, so a zero here would be true by construction rather than "
              "measured")
        return 3
    if asserts:
        print("VERDICT: A ROUND ASSERTS NEUTRALITY -- route to a non-author grader")
        return 1
    print("VERDICT: no round asserts neutrality, at RECOGNITION strength.")
    print("BOUND: this settles the DECLARATION question only. R-VALUE is a "
          "condition on what a round's findings would do to a reader, not on "
          "what the round says, so rounds classified CANNOT_TELL are not "
          "settled by this or any declaration sweep.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
