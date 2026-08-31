#!/usr/bin/env python3
"""SO-1cR -- RULE 14 MADE MECHANICAL: the row-label call-site sweep.

`CLAUDE.md` rule 14: *"a lesson is not applied until EVERY call site asserts it."*

SO-1c's amendment R8 registered a fence that said "the row-label comparison" --
SINGULAR -- and repaired the one site the lane had found.  THREE more were live:

  (2) `so1c_run_arm.sh` G-OPTDEP  -- refused the REAL artefact in PREFLIGHT,
      rc=5, and stopped SO-1c's chain at its second arm 176 s in;
  (3) `so1c_grade.py`  G-XSTAR    -- would have refused at GRADING even had (2)
      passed;
  (4) `so1c_grade.py`  the selftest FIXTURE -- wrote a label the real producer
      never writes, which is what kept (3) GREEN across 53 units and three
      amendments.  A fixture that disagrees with its producer does not merely
      fail to catch a break, it CONCEALS one.

THIS SWEEP IS THE REPAIR FOR THE CLASS, NOT THE INSTANCE.  It carries no
whitelist of known sites -- a whitelist cannot fail on a site nobody has thought
of yet.  It refuses on the BROKEN FORM wherever it appears, so an unrepaired
call site added tomorrow turns it red without anyone remembering to extend it.

WHY IT TOKENIZES RATHER THAN GREPS, AND THE TWO WRONG TURNS ON THE WAY -- BOTH
RECORDED, BECAUSE THE SECOND IS THE MORE DANGEROUS AND WOULD HAVE SHIPPED.

  * A first version GREPPED, and reported two call sites that are not call
    sites: the word `row[0]` inside a unit DESCRIPTION, and a unit asserting the
    GRADER'S OWN OUTPUT record.  A detector that fires on prose is a detector a
    reader learns to overrule, and a check somebody overrules has stopped being
    a check.
  * A second version tokenized and dropped **every** STRING token -- AND THAT
    MADE IT BLIND TO BOTH PYTHON CALL SITES, because the key it matches on IS a
    string (`d["row"]`, `.get("row")`).  IT REPORTED CLEAN ON THE BROKEN
    PREDECESSOR.  That is a FALSE CLEAN, and a false clean is the same defect
    class as the fixture this item exists to repair: a green that a reader
    cannot distinguish from a blind spot.  It was caught only because the sweep
    was driven against the KNOWN-BROKEN predecessor as a positive control
    instead of being trusted on the repaired tree.

So strings are KEPT when identifier-like (a dict key or a row label -- code) and
replaced by `"..."` otherwise (a unit description -- prose).  `tokenize` is used
because only the tokenizer knows where a string actually begins and ends.

THE SWEEP IS NEVER BELIEVED ON A GREEN ALONE.  Its registered drive is a PAIR:
red on the broken predecessor, clean on the repaired tree.

exit 0 = clean, exit 1 = at least one finding (each printed), exit 2 = the sweep
could not run (fail closed -- an unreadable consumer is never a clean consumer).
"""
import ast
import io
import os
import re
import sys
import tokenize

MAPPING_CANON = "ROW_LABELS={PATCHED:(PATCHED,P),SHIPPED:(SHIPPED,S)}"
CONSUMERS = ("so1cr_chain_driver.sh", "so1cr_run_arm.sh", "so1cr_grade.py")

# A row label taken from a PARSED PRODUCER ARTEFACT and compared with `==` / `!=`
# against a single scalar.  That is the form that cannot accept two registered
# labels, and it is the form that killed SO-1c.
BROKEN = re.compile(r"""(\[\s*['"]row['"]\s*\]|\.get\(\s*['"]row['"]\s*\))\s*[!=]=""")
DERIVED = re.compile(r"\brow\s*\[\s*0\s*\]")


IDENTLIKE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def code_lines(path):
    """Return [(lineno, code_only_text)] with COMMENTS removed and PROSE STRINGS
    replaced by a placeholder.

    A FIRST VERSION OF THIS FUNCTION DROPPED **EVERY** STRING TOKEN, AND THAT
    MADE THE SWEEP BLIND TO BOTH PYTHON CALL SITES: the key it matches on IS a
    string (`d["row"]`, `.get("row")`), so dropping strings deleted the thing
    being looked for and the sweep reported CLEAN ON THE BROKEN PREDECESSOR.  A
    clean that a reader cannot distinguish from a blind spot is exactly the
    defect this item exists to repair, so it is recorded here rather than
    quietly corrected.

    Strings are therefore KEPT when their content is identifier-like -- a dict
    key or a row label, which is code -- and replaced by `"..."` otherwise,
    which is what removes unit DESCRIPTIONS from consideration without removing
    any comparison.  `tokenize` is used rather than a regex because only the
    tokenizer knows where a string actually begins and ends.
    """
    src = open(path, "rb").read()
    if not path.endswith(".py"):
        out = []
        for i, ln in enumerate(src.decode("utf-8", "replace").splitlines(), 1):
            out.append((i, re.sub(r"#.*$", "", ln)))
        return out
    keep = {}
    try:
        for tok in tokenize.tokenize(io.BytesIO(src).readline):
            if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                            tokenize.INDENT, tokenize.DEDENT):
                continue
            text = tok.string
            if tok.type == tokenize.STRING:
                try:
                    body = ast.literal_eval(text)
                except Exception:                                    # noqa: BLE001
                    body = None
                if not (isinstance(body, str) and IDENTLIKE.match(body)):
                    text = '"..."'
                else:
                    text = '"%s"' % body
            keep.setdefault(tok.start[0], []).append(text)
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        sys.stderr.write("SWEEP REFUSE cannot tokenize %s: %r\n" % (path, exc))
        raise SystemExit(2)
    return [(n, "".join(v)) for n, v in sorted(keep.items())]


def production_cut(path):
    """Line beyond which `so1cr_grade.py` is its own SELFTEST rather than the
    grading path.  THE FIXTURE IS BEFORE THIS CUT AND IS THEREFORE SWEPT -- it
    is call site (4) and is the one that hid the break.  What lies after the cut
    is the unit BODIES, which assert on the grader's own OUTPUT record rather
    than on a producer artefact; they are covered by the POSITIVE fixture leg
    below, not by this negative sweep."""
    if not path.endswith("so1cr_grade.py"):
        return 10 ** 9
    for i, ln in enumerate(open(path).read().splitlines(), 1):
        if ln.startswith("def selftest("):
            return i
    sys.stderr.write("SWEEP REFUSE %s carries no `def selftest(` -- the production/"
                     "selftest boundary could not be located\n" % path)
    raise SystemExit(2)


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    findings = []

    # ---- (1) EVERY REGISTERED CONSUMER PRESENT.  FAIL CLOSED: a consumer that
    # ---- has been renamed or deleted is not a consumer that has been fixed.
    missing = [b for b in CONSUMERS if not os.path.isfile(os.path.join(d, b))]
    if missing:
        for b in missing:
            print("MISSING CONSUMER %s -- the sweep cannot see a file that is not there" % b)
        return 1

    for base in CONSUMERS:
        path = os.path.join(d, base)
        cut = production_cut(path)
        for n, code in code_lines(path):
            if n >= cut:
                continue
            # ---- (2) THE BROKEN FORM.
            if BROKEN.search(code):
                findings.append("UNREPAIRED ROW-LABEL CALL SITE  %s:%d  %s"
                                % (base, n, code.strip()[:110]))
            # ---- (3) NO LABEL DERIVED FROM THE FIRST LETTER.  `row[0]` agrees
            # ---- with the producer only by the coincidence that PATCHED and
            # ---- SHIPPED share first letters with P and S.
            if DERIVED.search(code):
                findings.append("DERIVED LABEL (row[0])  %s:%d  %s"
                                % (base, n, code.strip()[:110]))

        # ---- (4) THE SAME REGISTERED MAPPING IN EVERY CONSUMER.  Quote style
        # ---- differs between the shell-embedded python and the modules, so the
        # ---- literal is canonicalised before comparison: three files each
        # ---- carrying a DIFFERENT mapping would satisfy a per-file check, and
        # ---- that is exactly what this sweep exists to catch.
        got = None
        for ln in open(path).read().splitlines():
            st = ln.strip()
            if st.startswith("#") or st.startswith("# "):
                continue
            if re.match(r"^\s*ROW_LABELS\s*=", ln):
                got = re.sub(r"[\s\"']", "", ln.split("=", 1)[0] + "=" + ln.split("=", 1)[1])
                break
        if got != MAPPING_CANON:
            findings.append("MAPPING ABSENT OR NOT THE REGISTERED FORM in %s: got %r"
                            % (base, got))

    # ---- (5) CALL SITE (4), ASSERTED POSITIVELY.  The grader's own fixture must
    # ---- derive the staged artefact's row label FROM `ROW_LABELS`, never from
    # ---- the bare directory name.  SO-1c's fixture wrote `"row": rowname` and
    # ---- that single line is why three amendments of green units saw nothing.
    g = os.path.join(d, "so1cr_grade.py")
    src = open(g).read()
    if re.search(r'"row"\s*:\s*rowname\b', src):
        findings.append("FIXTURE WRITES THE BARE DIRECTORY NAME as the artefact's row label "
                        "in so1cr_grade.py -- that is SO-1c's concealing fixture, restored")
    if "row_label = ROW_LABELS[rowname]" not in src:
        findings.append("FIXTURE DOES NOT DERIVE THE ROW LABEL FROM THE REGISTERED MAPPING "
                        "in so1cr_grade.py -- call site (4) is unasserted")

    for f in findings:
        print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
