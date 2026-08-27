#!/usr/bin/env python3
"""T9a-R1c's WORDING SWEEP -- the discharge of VERIFICATION_CHARTER 2h.4(4)/(5).

WHY THIS FILE EXISTS AND WHY IT IS NOT THE AST GUARD.  Charter 2h.5 is express:
the AST guard C_NOTRIPLE in analyse_t9aR1c.py "proves the ABSENCE OF A TRIPLE,
not the wording of the claim, and condition 4 is about the wording."  Those are
different propositions and no machine check inside the comparator discharges the
second.  This sweep is the machine half of the second one; the human half is the
supervisor reading the registered sentence.

WHAT IT LOOKS FOR.  Constructions that would turn a floor demonstration into a
continuum claim -- "the solution is correct to X" -- or into a claim about meshes
that were never run -- "so the answer does not depend on the mesh at the
resolution that matters", which is 2g.3's OWN phrase, NARROWED by 2h.4(5)
against verification's own drafting and struck from this rung throughout.

THE HARD PART IS NOT FINDING THE PHRASE, IT IS CLASSIFYING IT.  Three kinds of
occurrence are legitimate and one is not:

  ASSERTION  the document says it in its own voice          -> VIOLATION
  DISCLAIMER the document quotes it in order to DENY or
             STRIKE it                                      -> required, not a
                                                               violation: a strike
                                                               that cannot name
                                                               what it struck is
                                                               not a record
  REMOVAL    a unified-diff '-' line in INSTRUMENT_DIFFS     -> required: a diff
                                                               that cannot quote
                                                               the removed text
                                                               is useless
  VOCABULARY THIS file's own PHRASES tuple                   -> required: a
                                                               forbidden-phrase
                                                               list must contain
                                                               the forbidden
                                                               phrases

A sweep that flagged all four would be unusable and would be silenced; a sweep
that flagged none would be decorative.  The classification is the instrument.

THE VOCABULARY EXEMPTION IS LOCATED STRUCTURALLY, NEVER BY LINE NUMBER OR BY A
FILENAME TEST -- this file parses ITS OWN source and exempts exactly the source
range of the PHRASES assignment node.  That is the same move C_NOTRIPLE makes in
analyse_t9aR1c.py, and for the same reason: a self-referential checker that
exempts itself by name exempts everything it later grows, while one that exempts
a single AST node exempts only that node.  An asserting sentence written anywhere
else in this file is still a VIOLATION, and --selftest drives exactly that.

NO `assert` (L-332).  --selftest drives a PLANTED ASSERTING SENTENCE through the
same reader and requires it to come back ASSERTION, and drives a disclaimed one
and a diff-removal one and requires both to come back non-violating.

Exit: 0 no assertions, 1 at least one, 2 refusal.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXIT_OK, EXIT_VIOLATION, EXIT_REFUSE = 0, 1, 2

FILES = ["docs/campaigns/T-family/T9aR1c_PREREGISTRATION.md"] + [
    "verification/runs/T-family/T9aR1c_runs/" + f for f in (
        "T9aR1c_registered.json", "analyse_t9aR1c.py", "exact_t9aR1c.py",
        "build_t9aR1c.py", "mark_done_t9aR1c.py", "run_one_t9aR1c.sh",
        "sweep_wording_t9aR1c.py",
        "T9aR1c_INSTRUMENT_DIFFS.txt", "T9aR1c_SELFTEST_EVIDENCE.txt")]

PHRASES = ("does not depend on the mesh", "at the resolution that matters",
           "answer does not depend", "mesh-independent", "mesh independent",
           "independent of the mesh", "the solution is correct", "correct to X")

# CASE-INSENSITIVE, and that is not cosmetic.  THIS RUNG HAS NOW BEEN BITTEN BY
# CASE SENSITIVITY THREE TIMES: a filing check whose filter matched "T9aR1c" and
# missed the planted "t9aR1c"; and this very classifier, whose first version
# matched "STRUCK|struck" and missed "Struck", reporting a correctly-disclaimed
# line as a violation.  A reader that is case-sensitive about English prose is
# blind in a way that looks like vigilance.
NEGATION = re.compile(
    r"not a claim|does not say|does not claim|never|NOT '|NOT \"|struck|narrow"
    r"|overreach|withdrawn|forbid|would smuggle|deliberately does not|is not a claim"
    r"|2h\.4|2g\.3|had been|appeared in|verbatim from|removed from", re.I)
WINDOW = 5


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def vocabulary_range(text):
    """The source line range of THIS module's own PHRASES assignment, located by
    AST.  Returns (first, last) 1-based inclusive, or None if not found."""
    import ast as _ast
    try:
        tree = _ast.parse(text)
    except SyntaxError:
        return None
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, _ast.Name) and tgt.id == "PHRASES":
                    return (node.lineno, getattr(node, "end_lineno", node.lineno))
    return None


def classify(lines, i, in_diff_body, vocab=None):
    """i is 0-based.  Returns ASSERTION / DISCLAIMER / REMOVAL / VOCABULARY."""
    line = lines[i]
    if vocab and vocab[0] <= i + 1 <= vocab[1]:
        return "VOCABULARY"
    if in_diff_body and line.startswith("-") and not line.startswith("---"):
        return "REMOVAL"
    window = "\n".join(lines[max(0, i - WINDOW):min(len(lines), i + WINDOW + 1)])
    return "DISCLAIMER" if NEGATION.search(window) else "ASSERTION"


def scan_text(text, label, diffish=False, selfish=False):
    lines = text.split("\n")
    vocab = vocabulary_range(text) if selfish else None
    out = []
    for i, line in enumerate(lines):
        low = line.lower()
        for p in PHRASES:
            if p.lower() in low:
                out.append((label, i + 1, p, classify(lines, i, diffish, vocab)))
    return out


def sweep(root=None, quiet=False):
    root = root or REPO
    rows = []
    for rel in FILES:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            refuse("%s is missing -- a sweep that silently skips a file is a false zero" % rel)
        rows += scan_text(open(path, errors="replace").read(), rel,
                          diffish=rel.endswith("INSTRUMENT_DIFFS.txt"),
                          selfish=rel.endswith("sweep_wording_t9aR1c.py"))
    by = {k: [r for r in rows if r[3] == k]
          for k in ("ASSERTION", "DISCLAIMER", "REMOVAL", "VOCABULARY")}
    if not quiet:
        print("WORDING SWEEP (charter 2h.4(4)/(5)): %d files, %d phrases, %d occurrences"
              % (len(FILES), len(PHRASES), len(rows)))
        print("  ASSERTIONS  : %d   <- the only class that is a violation" % len(by["ASSERTION"]))
        for r in by["ASSERTION"]:
            print("      VIOLATION %s:%d  %r" % r[:3])
        print("  DISCLAIMERS : %d   (quoted in order to deny or strike -- required)" % len(by["DISCLAIMER"]))
        print("  REMOVALS    : %d   (unified-diff '-' lines -- required)" % len(by["REMOVAL"]))
        print("  VOCABULARY  : %d   (this file's own PHRASES tuple, located by AST -- required)"
              % len(by["VOCABULARY"]))
    return by


def selftest():
    import ast
    fails = []
    print("sweep_wording_t9aR1c selftest:")

    def check(label, ok):
        print("  [%s] %s" % ("ok " if ok else "FAIL", label))
        if not ok:
            fails.append(label)

    # EVERY planted control below is ASSEMBLED FROM `PHRASES` AT RUNTIME rather
    # than written out literally.  Two reasons, and the second is the real one:
    # the controls then track the vocabulary automatically if it grows, and THIS
    # FILE NEVER WRITES A FORBIDDEN SENTENCE IN ITS OWN VOICE -- so the sweep
    # needs no exemption for its own selftest, and the only exemption in the file
    # remains the single PHRASES node.  An instrument that had to be excused from
    # its own rule to pass it would be evidence of nothing.
    P0, P1, P6 = PHRASES[0], PHRASES[1], PHRASES[6]
    plant = ("This rung establishes that the answer %s at the coarse level,\n"
             "and that %s to X.\n" % (P0, P6))
    r = scan_text(plant, "<PLANTED ASSERTION>")
    check("PLANTED CONTROL: a sentence ASSERTING the forbidden claims -> %d hits, all ASSERTION"
          % len(r), len(r) >= 3 and all(x[3] == "ASSERTION" for x in r))

    disc = ("The phrase was STRUCK under 2h.4(5): it is NOT a claim that\n"
            "the answer %s %s.\n" % (P0, P1))
    r = scan_text(disc, "<PLANTED DISCLAIMER>")
    check("a DISCLAIMED occurrence -> classified DISCLAIMER, not a violation",
          r and all(x[3] == "DISCLAIMER" for x in r))

    mixed = ("Struck everywhere:\n"
             "    \"so the answer %s %s\".\n" % (P0, P1))
    r = scan_text(mixed, "<CASE CONTROL>")
    check("CASE CONTROL: negation spelled 'Struck' (not 'struck'/'STRUCK') -> still DISCLAIMER. "
          "This exact miss produced a false violation in the first version of this file",
          r and all(x[3] == "DISCLAIMER" for x in r))

    d = ("--- a\n+++ b\n"
         "-    claim=\"...so the answer %s %s\",\n"
         "+    claim=\"the discretisation error in T_i1 is below X at 35 cells\",\n" % (P0, P1))
    r = scan_text(d, "<PLANTED DIFF>", diffish=True)
    check("a unified-diff '-' line quoting the struck text -> classified REMOVAL, not a violation",
          r and all(x[3] == "REMOVAL" for x in r))

    r = scan_text(d, "<PLANTED DIFF, diffish OFF>", diffish=False)
    check("the SAME bytes with diff handling OFF -> NOT classified REMOVAL, so the exemption is "
          "scoped to the diffs file and is not a blanket", r and not any(x[3] == "REMOVAL" for x in r))

    own = open(__file__).read()
    vr = vocabulary_range(own)
    check("the VOCABULARY exemption is located STRUCTURALLY: this file's PHRASES tuple parses to "
          "source lines %s, not a hardcoded number and not a filename test" % (vr,), vr is not None)
    r = scan_text(own, "<SELF>", selfish=True)
    check("this file scanned as itself -> %d occurrences, %d VOCABULARY, %d ASSERTION"
          % (len(r), sum(1 for x in r if x[3] == "VOCABULARY"), sum(1 for x in r if x[3] == "ASSERTION")),
          sum(1 for x in r if x[3] == "VOCABULARY") > 0 and not any(x[3] == "ASSERTION" for x in r))
    injected = own + ('\n\nBOGUS = ("this rung shows the answer %s "\n'
                      '         "%s")\n' % (P0, P1))
    r = scan_text(injected, "<SELF + INJECTED ASSERTION>", selfish=True)
    check("an ASSERTING sentence injected into this file OUTSIDE the PHRASES tuple -> still a "
          "VIOLATION (%d ASSERTION). The exemption covers ONE AST node, not this file"
          % sum(1 for x in r if x[3] == "ASSERTION"), any(x[3] == "ASSERTION" for x in r))

    fired = False
    try:
        sweep(root="/nonexistent-root-for-this-arm", quiet=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    check("a file the sweep cannot read -> REFUSE, never a silent skip (a sweep that skips a file "
          "is a false zero)", fired)

    by = sweep(quiet=True)
    check("THE LIVE SWEEP over all %d artifacts: %d ASSERTIONS"
          % (len(FILES), len(by["ASSERTION"])), len(by["ASSERTION"]) == 0)

    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    check("AST assert count in this file = %d (planted control: the counter sees %d)" % (n0, n1),
          n0 == 0 and n1 == 1)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    by = sweep()
    return EXIT_OK if not by["ASSERTION"] else EXIT_VIOLATION


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
