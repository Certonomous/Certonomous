#!/usr/bin/env python3
"""
F28 -- ASSEMBLED-CASE GUARDS.  Two guards, each with a NEGATIVE LIMB in
`--selftest`.  Neither guard is allowed to be a check that cannot fail.

Called by `run_f28.sh` at `phase=assemble`, BEFORE the solver.  Both guards are
PRE-COMPUTE INSTRUMENT CHECKS: they refuse (exit 2), they never degrade.

-----------------------------------------------------------------------------
GUARD 1 -- PLACEHOLDERS.  `placeholders <run_dir> --tokens T1 T2 ...`
-----------------------------------------------------------------------------
The launcher previously swept for a BARE `__`.  That guard was RIGHT to exist
-- it fired on a real unsubstituted placeholder in the feasibility path -- but
its rule was the wrong one: `system/controlDict.template:2` reads
"__PLACEHOLDERS__ are substituted by run_f28.sh", so the sweep aborted every
gated run at `phase=assemble` on the case's OWN header comment.

The fix is PRECISION, NOT PERMISSIVENESS.  Two limbs:

  LIMB A -- NAMED.  Every token the launcher SAYS it substitutes must be ABSENT
  from the assembled tree.  Catches a `sed` that did not fire (a renamed token,
  a mistyped `-e`, a template edited without the launcher).  The token list is
  passed in BY THE LAUNCHER, so the launcher stays the single authority on what
  it substitutes and this file cannot drift away from it.

  LIMB B -- GENERIC, COMMENT-STRIPPED.  No `__UPPER__` token may survive
  OUTSIDE a comment.  Catches a token NOBODY declared -- a template that gains
  `__NEW_THING__` the launcher does not know about.

WHY THIS CANNOT BE FOOLED, stated as the rule it actually is:  a placeholder
that MATTERS is by construction in a VALUE POSITION -- it is text OpenFOAM
parses as a dictionary entry.  A placeholder inside a comment is not read by
OpenFOAM, cannot reach a solver, and cannot change a number.  So the line
between "a genuinely unsubstituted token" and "text that merely looks like
one" is NOT its spelling -- it is whether the parser sees it.  That is the
line this guard draws, by removing exactly what the parser removes: OpenFOAM
dictionaries take C and C++ comments (`/* */`, `//`), and nothing else is
stripped.  Limb A is spelling-based and is deliberately NOT comment-stripped:
a declared token appearing anywhere at all means a substitution went wrong.

Residual, stated rather than hidden: limb B refuses a VALUE that happens to
contain `__WORD__` (e.g. a literal `FOO__BAR__BAZ`).  That direction is
REFUSAL, never silent acceptance, and no F28 dictionary carries such a value.
A single `__` inside a name -- `M1_kOmegaSST_null__AR_10`, a real filename
form in this repository -- is NOT matched and NOT refused; the old bare-`__`
sweep refused it.

-----------------------------------------------------------------------------
GUARD 2 -- MANDATORY fieldValue ENTRIES.  `fieldvalues <controlDict>`
-----------------------------------------------------------------------------
In OpenFOAM v2606, `Foam::functionObjects::fieldValue::read` reads
`writeFields` with a FATAL accessor:

    src/functionObjects/field/fieldValues/fieldValue/fieldValue.C:98
        dict.readEntry("writeFields", writeFields_);

`dictionary::readEntry` defaults to `IOobjectOption::MUST_READ`
(src/OpenFOAM/db/dictionary/dictionary.H:686-692, "FatalIOError if ... it is
mandatory and not found").  Both `surfaceFieldValue` and `volFieldValue`
derive from `fieldValue`, so an object of either type that omits `writeFields`
kills the run AT STARTUP, before iteration 1 -- under `mpirun`, as MPI_ABORT.

NOTE THE DOC/CODE CONTRADICTION, because it is why this was missed:
`fieldValue.H:57` documents `writeFields | ... | bool | no | false` -- OPTIONAL
with default false.  The CODE is mandatory.  The header is wrong.  Reading the
table and not the accessor is exactly how this defect gets written.

When `writeFields` is TRUE, `surfaceFieldValue.C:1297-1299` then reads
`surfaceFormat` with `dict.get<word>` -- also fatal.  So this guard also
refuses `writeFields true` without `surfaceFormat`: the repair for one fatal
entry must not introduce the next one.
"""

import os
import re
import sys

REFUSE = 2

FIELDVALUE_TYPES = ("surfaceFieldValue", "volFieldValue")

# Limb B.  A double-underscore-delimited ALL-CAPS token: the launcher's own
# placeholder convention.  Requires BOTH delimiters, so a single `__` inside a
# name is not matched.
PLACEHOLDER_RE = re.compile(r"__[A-Z0-9][A-Z0-9_]*__")

# polyMesh is machine-written mesh data, is large, and carries no placeholder.
SKIP_DIRS = ("polyMesh",)


def refuse(msg):
    sys.stderr.write("REFUSE: %s\n" % msg)
    sys.exit(REFUSE)


def strip_foam_comments(text):
    """Remove exactly what the OpenFOAM dictionary parser removes: C block
    comments and C++ line comments.  Nothing else."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


# --------------------------------------------------------------------------
# GUARD 1
# --------------------------------------------------------------------------

def dict_files(run_dir):
    out = []
    for sub in ("system", "constant", "0"):
        root = os.path.join(run_dir, sub)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in sorted(filenames):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def check_placeholders(run_dir, tokens):
    files = dict_files(run_dir)
    if not files:
        refuse("no assembled dictionaries under %s -- the guard would have "
               "swept nothing and reported clean.  A zero from a reader with "
               "nothing to read is not evidence (CLAUDE.md rule 3)." % run_dir)

    named = []
    generic = []
    for path in files:
        try:
            with open(path, "r", errors="replace") as fh:
                raw = fh.read()
        except OSError as exc:
            refuse("cannot read assembled file %s: %s" % (path, exc))
        for tok in tokens:
            if tok in raw:
                named.append((path, tok))
        for hit in sorted(set(PLACEHOLDER_RE.findall(strip_foam_comments(raw)))):
            generic.append((path, hit))

    if named:
        refuse("LIMB A: a token this launcher substitutes SURVIVED into the "
               "assembled case -- a `sed` did not fire: %s"
               % ", ".join("%s in %s" % (t, p) for p, t in named))
    if generic:
        refuse("LIMB B: an UNDECLARED __UPPER__ placeholder survived OUTSIDE a "
               "comment, i.e. in a position the OpenFOAM parser reads: %s"
               % ", ".join("%s in %s" % (t, p) for p, t in generic))

    print("placeholders OK: %d assembled dictionaries; %d declared tokens all "
          "substituted; no undeclared __UPPER__ token in any value position"
          % (len(files), len(tokens)))
    return 0


# --------------------------------------------------------------------------
# GUARD 2
# --------------------------------------------------------------------------

def top_level_subdicts(body):
    """Yield (name, body) for each sub-dictionary at depth 0 of `body`."""
    i, n = 0, len(body)
    while i < n:
        m = re.compile(r"([A-Za-z_][A-Za-z0-9_.]*)\s*\{").search(body, i)
        if not m:
            return
        name = m.group(1)
        depth, j = 1, m.end()
        while j < n and depth:
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
            j += 1
        if depth:
            refuse("unbalanced braces in the `functions` dictionary near %r" % name)
        yield name, body[m.end():j - 1]
        i = j


def check_fieldvalues(control_dict):
    try:
        with open(control_dict, "r", errors="replace") as fh:
            text = strip_foam_comments(fh.read())
    except OSError as exc:
        refuse("cannot read %s: %s" % (control_dict, exc))

    m = re.search(r"\bfunctions\s*\{", text)
    if not m:
        refuse("no `functions` dictionary in %s -- this guard would have "
               "inspected nothing and reported clean (CLAUDE.md rule 3)."
               % control_dict)
    depth, j = 1, m.end()
    while j < len(text) and depth:
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
        j += 1
    body = text[m.end():j - 1]

    seen, bad = [], []
    for name, blk in top_level_subdicts(body):
        tm = re.search(r"\btype\s+([A-Za-z][A-Za-z0-9_]*)\s*;", blk)
        if not tm or tm.group(1) not in FIELDVALUE_TYPES:
            continue
        seen.append(name)
        wm = re.search(r"\bwriteFields\s+(\w+)\s*;", blk)
        if not wm:
            bad.append("%s (%s) omits the MANDATORY `writeFields` entry -- "
                       "fieldValue.C:98 reads it with dict.readEntry, which "
                       "defaults to MUST_READ and is FATAL at startup"
                       % (name, tm.group(1)))
        elif (wm.group(1) in ("true", "yes", "on", "1")
              and tm.group(1) == "surfaceFieldValue"
              and not re.search(r"\bsurfaceFormat\s+\w+\s*;", blk)):
            bad.append("%s sets `writeFields %s` but omits `surfaceFormat`, "
                       "which surfaceFieldValue.C:1297-1299 then reads with "
                       "dict.get<word> -- also fatal at startup"
                       % (name, wm.group(1)))

    if not seen:
        refuse("no surfaceFieldValue/volFieldValue object found in %s.  The "
               "guard inspected NOTHING; a clean result from it would be a "
               "planted-zero failure (CLAUDE.md rule 3)." % control_dict)
    if bad:
        refuse("mandatory fieldValue entries missing:\n  - " + "\n  - ".join(bad))

    print("fieldValue entries OK: %d objects checked (%s); every one carries "
          "`writeFields`" % (len(seen), ", ".join(seen)))
    return 0


# --------------------------------------------------------------------------
# SELFTEST -- every limb, positive AND negative
# --------------------------------------------------------------------------

_CD = """/*--------------------------------*- C++ -*------------------------------*\\
  F28 -- __PLACEHOLDERS__ are substituted by run_f28.sh.   %(banner)s
\\*---------------------------------------------------------------------*/
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
endTime         15000;   // the end time, substituted above
note            "%(value)s";
functions
{
    diskPlaneUp
    {
        type            surfaceFieldValue;
        regionType      sampledSurface;
        name            planeUp;
        sampledSurfaceDict { type plane; pointAndNormalDict { point (0 0 0); } }
        operation       areaAverage;
        fields          (p);
        %(wf)s
    }
    forcesDuct { type forces; patches (ductInner); }
}
"""


def _case(tmp, banner="", value="M1_kOmegaSST_null__AR_10", wf="writeFields     false;",
          extra=""):
    for sub in ("system", "constant", "0"):
        os.makedirs(os.path.join(tmp, sub), exist_ok=True)
    cd = os.path.join(tmp, "system", "controlDict")
    with open(cd, "w") as fh:
        fh.write(_CD % {"banner": banner, "value": value, "wf": wf})
    with open(os.path.join(tmp, "0", "U"), "w") as fh:
        fh.write("FoamFile { object U; }\ninternalField uniform (10 0 0);\n%s\n" % extra)
    return cd


def _run(fn, *a):
    """Return 0 if the guard passed, 2 if it refused."""
    try:
        fn(*a)
        return 0
    except SystemExit as exc:
        return exc.code


def selftest():
    import tempfile
    tokens = ["__END_TIME__", "__WRITE_INTERVAL__", "__SU_X__", "__DELTA_P__",
              "__U_INF__", "__K_INIT__", "__OMEGA_INIT__"]
    results = []

    def expect(label, got, want):
        results.append((label, got, want, got == want))

    with tempfile.TemporaryDirectory() as tmp:
        # ---- GUARD 1 ----
        # NEGATIVE LIMB (the one that matters): the real defect.  The header
        # comment says `__PLACEHOLDERS__`, a `//` comment says `__END_TIME__`,
        # and a VALUE carries a single `__`.  None is a defect.  The old bare
        # `__` sweep refused all three.  This guard MUST NOT.
        d = os.path.join(tmp, "clean"); _case(d)
        expect("G1 negative: __PLACEHOLDERS__ in a block comment not refused",
               _run(check_placeholders, d, tokens), 0)

        d = os.path.join(tmp, "underscore")
        _case(d, value="verification/queue/closure/M1_kOmegaSST_null__AR_10_Ret_180")
        expect("G1 negative: single `__` inside a value not refused",
               _run(check_placeholders, d, tokens), 0)

        # NEGATIVE, third form: a `//` line comment that mentions the
        # placeholder CONVENTION without being an unsubstituted token.
        d = os.path.join(tmp, "linecomment")
        _case(d, banner="// tokens of the form __NAME__ are set by run_f28.sh")
        expect("G1 negative: __NAME__ inside a // comment not refused",
               _run(check_placeholders, d, tokens), 0)

        # POSITIVE LIMB A: a declared token left unsubstituted in a value.
        d = os.path.join(tmp, "limbA"); _case(d, extra="internalField uniform (__U_INF__ 0 0);")
        expect("G1 positive A: unsubstituted __U_INF__ in a value REFUSED",
               _run(check_placeholders, d, tokens), REFUSE)

        # POSITIVE LIMB B: an UNDECLARED token in a value position.
        d = os.path.join(tmp, "limbB"); _case(d, extra="relaxation __NEW_KNOB__;")
        expect("G1 positive B: undeclared __NEW_KNOB__ in a value REFUSED",
               _run(check_placeholders, d, tokens), REFUSE)

        # POSITIVE, the sharpest: a declared token inside a COMMENT is still
        # refused by limb A -- limb A is spelling-based on purpose.
        d = os.path.join(tmp, "limbAcomment"); _case(d, banner="// __SU_X__")
        expect("G1 positive A: declared __SU_X__ even in a comment REFUSED",
               _run(check_placeholders, d, tokens), REFUSE)

        # PLANTED-ZERO CONTROL: a reader with nothing to read must refuse.
        d = os.path.join(tmp, "empty"); os.makedirs(d, exist_ok=True)
        expect("G1 planted zero: empty tree REFUSED, not reported clean",
               _run(check_placeholders, d, tokens), REFUSE)

        # ---- GUARD 2 ----
        cd = _case(os.path.join(tmp, "fv_ok"))
        expect("G2 positive: writeFields present -> OK",
               _run(check_fieldvalues, cd), 0)

        # NEGATIVE-DEFECT LIMB: the planted omission the check must catch.
        cd = _case(os.path.join(tmp, "fv_missing"), wf="")
        expect("G2 planted omission: writeFields absent REFUSED",
               _run(check_fieldvalues, cd), REFUSE)

        # The repair must not introduce the NEXT fatal entry.
        cd = _case(os.path.join(tmp, "fv_true"), wf="writeFields     true;")
        expect("G2: writeFields true without surfaceFormat REFUSED",
               _run(check_fieldvalues, cd), REFUSE)

        cd = _case(os.path.join(tmp, "fv_true_ok"),
                   wf="writeFields     true;\n        surfaceFormat   vtk;")
        expect("G2: writeFields true WITH surfaceFormat -> OK",
               _run(check_fieldvalues, cd), 0)

        # PLANTED-ZERO CONTROL for guard 2.
        cd = os.path.join(tmp, "nofuncs", "system", "controlDict")
        os.makedirs(os.path.dirname(cd), exist_ok=True)
        open(cd, "w").write("FoamFile { object controlDict; }\nendTime 1;\n")
        expect("G2 planted zero: no functions dict REFUSED, not clean",
               _run(check_fieldvalues, cd), REFUSE)

    width = max(len(r[0]) for r in results)
    for label, got, want, ok in results:
        print("%-4s %-*s  got=%s want=%s" % ("PASS" if ok else "FAIL",
                                             width, label, got, want))
    nfail = sum(0 if r[3] else 1 for r in results)
    print("\nselftest: %d checks, %d failed" % (len(results), nfail))
    return 1 if nfail else 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        return selftest()
    if len(argv) > 2 and argv[1] == "placeholders":
        run_dir = argv[2]
        if "--tokens" not in argv[3:]:
            refuse("`placeholders` requires --tokens <T1> [T2 ...]; the "
                   "launcher owns the substitution list, not this script.")
        tokens = argv[argv.index("--tokens") + 1:]
        if not tokens:
            refuse("--tokens was given with no token.  Limb A would have "
                   "checked nothing (CLAUDE.md rule 3).")
        return check_placeholders(run_dir, tokens)
    if len(argv) > 2 and argv[1] == "fieldvalues":
        return check_fieldvalues(argv[2])
    sys.stderr.write(__doc__ + "\nusage: check_assembled_case.py "
                     "{placeholders <run_dir> --tokens T...|"
                     "fieldvalues <controlDict>|--selftest}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
