"""Use-versus-mention: does a sentence ASSERT a claim, or MENTION one?

WHY THIS EXISTS. Three independent measurements on 2026-08-16 hit the same
instrument gap from three directions:

  1. The unattributed-QCR class (D257) is 39 sites on a filename-dated-record
     predicate, of which only 12 are bare assertions -- the rest are grading
     records QUOTING a claim in order to fault it. The whole distance between
     the floor of 12 and the ceiling of 39 is this distinction, and nothing in
     the lab drew it.
  2. V16 round 12 (D264) measured the rank-claim guard's live cost at 48 lab
     records, of which 18 of the 19 newly added were the previous round's own
     paperwork -- the guard eating the lab's own correct corrections, on a rung
     whose criterion makes false-positive rate a PASS requirement.
  3. The strike-marker false positive corrected at `faa02f80` is the same shape
     one level down: an instrument that could not tell a USED delimiter from a
     MENTIONED one, over-reporting on exactly the documents that discuss
     delimiters, which are the governance files.

WHAT IT IS NOT. It is not a replacement for `self_audit.py`'s
`_VALUE_NOT_A_SURFACE`, which excludes `sdk/tests/` BY PATH on the stated ground
that a labelled test corpus is not a claim surface. That rule is about WHERE a
sentence lives; this one is about WHAT THE SENTENCE DOES, and the two compose.
Stating both admission predicates is deliberate -- D49 records two precision
figures scored under different admission predicates, neither wrong and neither
comparable.

THE ADMISSION PREDICATE, stated so a second instrument can be compared to this
one. The caller supplies a sentence AND THE CHARACTER SPAN OF THE CLAIM inside
it. The span is not optional and the API has no overload that guesses it: the
first version of this module took the sentence alone and scored MENTION
precision at 58% on held-out sentences, because "there is a quotation mark
somewhere in this sentence" is not evidence about the claim -- a lab record
citing its own evidence carries quote marks, commit hashes and file paths just
as often as a record quoting someone else's words. What decides the question is
whether THE CLAIM ITSELF is set off, and that cannot be asked without its
offsets.

THREE-VALUED ON PURPOSE. A discriminator that silently classifies converts an
honest range into a false point estimate, which is worse than no discriminator.
Each side needs positive evidence; everything else is CANNOT_TELL, which is a
reported output and is never folded into either side.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

ASSERT = "ASSERT"
MENTION = "MENTION"
CANNOT_TELL = "CANNOT_TELL"


# --- enclosure: is the CLAIM SPAN itself set off? ---------------------------

def _code_spans(text: str) -> list[tuple[int, int]]:
    """CommonMark code spans: a run of N backticks closes only on a run of N."""
    runs = [(m.start(), m.end(), m.end() - m.start())
            for m in re.finditer(r"`+", text)]
    out, i = [], 0
    while i < len(runs):
        s, e, n = runs[i]
        j = next((k for k in range(i + 1, len(runs)) if runs[k][2] == n), None)
        if j is None:
            i += 1
        else:
            out.append((s, runs[j][1]))
            i = j + 1
    return out


def _paired(text: str, opener: str, closer: str) -> list[tuple[int, int]]:
    """Spans between alternating opener/closer marks."""
    if opener == closer:
        pos = [m.start() for m in re.finditer(re.escape(opener), text)]
        return [(pos[i], pos[i + 1] + len(opener))
                for i in range(0, len(pos) - 1, 2)]
    out, depth, start = [], 0, None
    for m in re.finditer(f"{re.escape(opener)}|{re.escape(closer)}", text):
        if m.group(0) == opener:
            if depth == 0:
                start = m.start()
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0:
                out.append((start, m.end()))
    return out


def _quote_spans(text: str) -> list[tuple[int, int]]:
    spans = _paired(text, '"', '"')
    for a, b in ("“", "”"), ("‘", "’"):
        spans += _paired(text, a, b)
    return spans


def enclosures(text: str, start: int, end: int) -> list[str]:
    """Every mechanism that sets the span [start, end) off from the sentence."""
    found = []
    checks = (("quotation", _quote_spans(text)),
              ("code-span", _code_spans(text)),
              ("strike-span", _paired(text, "~~", "~~")))
    for name, spans in checks:
        if any(s < start and end <= e for s, e in spans):
            found.append(name)
    # A blockquote marker anywhere before the claim on its own segment.
    if re.search(r"(?:^|\s)>\s[^>]{0,400}$", text[:start]):
        found.append("blockquote")
    return found


# --- lexical evidence, used only ALONGSIDE the positional test --------------

#: An attribution verb whose object is the claim: it must sit close in front.
_CITATION_VERB = re.compile(
    r"\b(?:reads?|read|quot(?:e|es|ed|ing)|verbatim|says?|said|stat(?:es|ed)|"
    r"carr(?:y|ies|ied|ying)|record(?:s|ed)|wrote|written|headed|titled|"
    r"used to (?:read|say)|as it (?:read|stood)|formerly|claimed?|asserts?)\b",
    re.I)
#: The sentence is adjudicating the claim as an object of study.
_ADJUDICATION = re.compile(
    r"\b(?:fault(?:s|ed|ing)?|false positive|claim pattern|candidate pool|"
    r"site under|in[- ]frame|unattributed|zero Spalart|gap|exception|"
    r"predicate|criterion|graded?|grading|verdict|withdrawn|struck|"
    r"superseded|falsified|refuted|stale|defect)\b", re.I)
#: The lab speaking in its own voice about its own artifact.
_FIRST_PERSON = re.compile(
    r"\b(?:our|ours|we|us|this lab(?:'s)?|the entry(?:'s)?|the submission)\b",
    re.I)

_LOOKBACK = 120


@dataclass
class Verdict:
    label: str
    mention_evidence: list[str] = field(default_factory=list)
    assert_evidence: list[str] = field(default_factory=list)
    reason: str = ""

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.label} ({self.reason})"


def classify(sentence: str, start: int, end: int) -> Verdict:
    """Grade the stance of `sentence` toward the claim at [start, end).

    MENTION requires the claim to be POSITIONALLY set off, or an attribution
    verb governing it from close in front. Lexical mood alone never decides,
    because a record citing its own evidence reads like one quoting another's.
    """
    if not 0 <= start < end <= len(sentence):
        raise ValueError("claim span outside the sentence")

    m, a = [], []
    m += enclosures(sentence, start, end)
    before = sentence[max(0, start - _LOOKBACK):start]
    if _CITATION_VERB.search(before):
        m.append("attribution-verb-governing-the-claim")
    if _ADJUDICATION.search(sentence):
        m.append("adjudication-vocabulary")
    if _FIRST_PERSON.search(sentence):
        a.append("first-person-or-our-artifact")

    positional = [x for x in m
                  if x in ("quotation", "code-span", "strike-span", "blockquote")]
    if positional:
        return Verdict(MENTION, m, a, "the claim itself is set off: " + ", ".join(positional))
    if m and not a:
        return Verdict(MENTION, m, a, "attributed or adjudicated, no own-voice signal")
    if a and not m:
        return Verdict(ASSERT, m, a, "own voice, claim not set off or attributed")
    if not m and not a:
        # NO FREE WINS. The module's own contract is that each side needs
        # positive evidence, and an earlier version broke it here by reading
        # "nothing set the claim off" as an assertion. Measured on the
        # development set, that default cost three MENTIONs -- checklists and
        # scope lists that assert nothing and quote nothing. Silence is
        # undecided, and undecided is a reportable answer.
        return Verdict(CANNOT_TELL, m, a,
                       "no evidence either way -- silence is not an assertion")
    return Verdict(CANNOT_TELL, m, a,
                   "both stances present -- a record speaking about its own claim")


def find_and_classify(sentence: str, pattern: "re.Pattern[str]") -> Verdict | None:
    """Convenience: locate the claim with `pattern`, then grade its stance."""
    hit = pattern.search(sentence)
    if hit is None:
        return None
    return classify(sentence, hit.start(), hit.end())
