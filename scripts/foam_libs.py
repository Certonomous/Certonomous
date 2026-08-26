#!/usr/bin/env python3
"""
foam_libs.py -- the one place an OpenFOAM `libs` entry is written.

WHY THIS FILE EXISTS (L-221, and Sanaa's H-7).

L-221 cost three runs in three files: a `str.replace` of a `libs` line that
is ABSENT succeeds silently by doing nothing, the solver then dies with
`Unknown RAS model type`, or -- worse -- returns the UNPERTURBED field, which
looks like a plausible physical answer.  The lesson was written down and the
other call sites kept the defect, so the rule is now H-7: a defect class that
bit three call sites gets an ASSERT at every call site, never a paragraph in
a report.  This module is that assert, factored once so there is nothing left
to copy wrongly.

THE TWO THINGS THAT MAKE THIS DIFFERENT FROM `>> controlDict`:

  1. MERGE, NEVER REPLACE AND NEVER BLIND-APPEND.  The result is the union of
     the libs already named and the libs required, in that order.  A blind
     `>>` append is silently wrong the moment the source dictionary already
     carries a top-level `libs` entry -- it produces TWO, which is a duplicate
     dictionary entry, not a longer list.  A blind `re.sub` replace is
     silently wrong in the other direction: it DROPS whatever was there.

  2. TOP-LEVEL ONLY.  A `controlDict` `functions { ... }` block is full of
     `libs (fieldFunctionObjects);` and `libs (sampling);` lines.  Those are
     function-object loads at sub-dictionary scope and they are NOT the
     solver's library list.  Every real controlDict in this lab has between
     8 and 11 of them.  A regex that does not track brace depth will read one
     of those as "the libs entry" and either merge into the wrong scope or
     clobber a function object.  Depth is tracked here, through comments and
     quoted strings, because that is the only way to get it right.

And the assertion that gives the module its point: after writing, the file is
RE-READ FROM DISK and checked.  Not the in-memory string -- the bytes that
the solver will actually open.

API
    ensure_libs(control_dict_path, *required)  -> merge, write, verify on disk
    assert_libs(control_dict_path, *required)  -> read-only check, no write

CLI
    python3 foam_libs.py ensure  <controlDict> lib.so [lib.so ...]
    python3 foam_libs.py assert  <controlDict> lib.so [lib.so ...]
    python3 foam_libs.py --selftest
"""
import os
import re
import sys

__all__ = ["ensure_libs", "assert_libs", "top_level_libs_entries",
           "FoamLibsError"]


class FoamLibsError(AssertionError):
    """A libs entry could not be installed or verified.  Never silent."""


# --------------------------------------------------------------------------
# Depth-aware scanning.  This is the whole trick; everything else is bookkeeping.
# --------------------------------------------------------------------------

_LIBS_TOKEN = re.compile(r"\blibs\b")


def _code_spans(text):
    """[(start, end, depth)] for every CODE region, with `{}` nesting depth.

    A span is closed at EVERY depth change -- on `{` as well as on `}` -- so a
    region is always tagged with the depth that actually held while it was
    being read.  (Closing only on `}` was the first version's bug: everything
    between a nested block's close and the next brace inherited the wrong
    depth, and a top-level `libs` sitting after the FoamFile block read as
    depth 1.)

    Comments (`//`, `/* */`) and double-quoted strings are skipped, so a brace
    inside a comment or a string cannot move the depth.
    """
    spans = []
    i, n, depth, run_start = 0, len(text), 0, 0
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            spans.append((run_start, i, depth))
            j = text.find("\n", i)
            i = n if j < 0 else j
            run_start = i
        elif c == "/" and nxt == "*":
            spans.append((run_start, i, depth))
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            run_start = i
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            i = j + 1
        elif c == "{":
            spans.append((run_start, i, depth))
            depth += 1
            i += 1
            run_start = i
        elif c == "}":
            spans.append((run_start, i, depth))
            depth -= 1
            i += 1
            run_start = i
        else:
            i += 1
    spans.append((run_start, n, depth))
    return spans


def _depth_at(spans, idx):
    """Brace depth at index `idx`, or None if `idx` sits inside a comment."""
    for start, end, depth in spans:
        if start <= idx < end:
            return depth
    return None


def top_level_libs_entries(text):
    """Return [(start, end, inner)] for every DEPTH-0 `libs ( ... );` entry.

    `inner` is the raw text between the parentheses.  Entries inside
    `functions { }` or any other sub-dictionary are deliberately not returned:
    those are function-object loads, not the solver's library list.
    """
    spans = _code_spans(text)
    out = []
    for m in _LIBS_TOKEN.finditer(text):
        j = m.end()
        while j < len(text) and text[j] in " \t\r\n":
            j += 1
        if j >= len(text) or text[j] != "(":
            continue          # not the list form
        if _depth_at(spans, m.start()) != 0:
            continue          # inside functions{} or another sub-dict
        close = text.find(")", j)
        if close < 0:
            continue
        k = close + 1
        while k < len(text) and text[k] in " \t\r\n":
            k += 1
        end = k + 1 if k < len(text) and text[k] == ";" else close + 1
        out.append((m.start(), end, text[j + 1:close]))
    return out

_TOKEN = re.compile(r'"[^"]*"|[^\s()]+')


def _names(inner):
    """Library tokens inside a libs(...) list, in order, quotes stripped."""
    return [t.strip('"') for t in _TOKEN.findall(inner) if t.strip('"')]


def _render(names):
    return "libs ( " + " ".join('"%s"' % x for x in names) + " );"


# The banner terminator: the `// * * * ... //` line that closes the FoamFile
# header.  Anchored to the FoamFile block so the FOOTER of the same shape at
# the end of the file cannot be mistaken for it.
_BANNER = re.compile(r"^// \*[ \*]*\*.*$", re.M)


def _banner_end(text):
    m = re.search(r"\bFoamFile\b", text)
    if not m:
        return None
    depth_open = text.find("{", m.end())
    if depth_open < 0:
        return None
    j, depth = depth_open, 0
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    else:
        return None
    b = _BANNER.search(text, j)
    return b.end() if b else None


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def assert_libs(control_dict_path, *required):
    """Read-only check.  Raises FoamLibsError; returns the merged name list."""
    if not os.path.isfile(control_dict_path):
        raise FoamLibsError("no such controlDict: %s" % control_dict_path)
    text = open(control_dict_path).read()
    entries = top_level_libs_entries(text)
    if len(entries) == 0:
        raise FoamLibsError(
            "%s: NO top-level libs entry (the %d `libs` lines present are all "
            "inside sub-dictionaries and are function-object loads)"
            % (control_dict_path, len(_LIBS_TOKEN.findall(text))))
    if len(entries) > 1:
        raise FoamLibsError(
            "%s: %d top-level libs entries, expected exactly 1 -- a duplicate "
            "dictionary entry, the signature of a blind append"
            % (control_dict_path, len(entries)))
    have = _names(entries[0][2])
    missing = [r for r in required if r not in have]
    if missing:
        raise FoamLibsError(
            "%s: libs entry does not name %s (it names: %s)"
            % (control_dict_path, ", ".join(missing), " ".join(have) or "<empty>"))
    return have


def ensure_libs(control_dict_path, *required):
    """Merge `required` into the top-level libs entry, write, verify ON DISK.

    Merge semantics: the result is the union of the libs already named and
    `required`, existing order preserved and new names appended.  Nothing is
    ever dropped and nothing is ever appended blindly.

    Returns the merged list of library names.
    """
    if not os.path.isfile(control_dict_path):
        raise FoamLibsError("no such controlDict: %s" % control_dict_path)
    if not required:
        raise FoamLibsError("ensure_libs called with no required libraries")

    text = open(control_dict_path).read()
    entries = top_level_libs_entries(text)

    merged = []
    for _, _, inner in entries:
        for nm in _names(inner):
            if nm not in merged:
                merged.append(nm)
    for r in required:
        if r not in merged:
            merged.append(r)

    if entries:
        if len(entries) > 1:
            # Never silent: collapsing duplicates is a REPAIR and it is announced.
            sys.stderr.write(
                "foam_libs: NOTE %s carried %d top-level libs entries; "
                "collapsing to one union entry: %s\n"
                % (control_dict_path, len(entries), " ".join(merged)))
        # Rewrite the first entry, delete the rest, back-to-front so the
        # earlier offsets stay valid.
        first = entries[0]
        for start, end, _ in reversed(entries[1:]):
            text = text[:start] + text[end:]
        text = text[:first[0]] + _render(merged) + text[first[1]:]
    else:
        pos = _banner_end(text)
        if pos is None:
            # GUARD: banner missing (a hand-written or truncated dict).  Append
            # at the end rather than guessing an offset -- still legal OpenFOAM.
            sys.stderr.write(
                "foam_libs: NOTE %s has no FoamFile banner terminator; "
                "appending libs entry at end of file\n" % control_dict_path)
            sep = "" if text.endswith("\n") else "\n"
            text = text + sep + "\n" + _render(merged) + "\n"
        else:
            text = text[:pos] + "\n\n" + _render(merged) + "\n" + text[pos:]

    with open(control_dict_path, "w") as fh:
        fh.write(text)

    # THE POINT OF THE MODULE: verify the bytes the solver will open, not the
    # string we just built.
    have = assert_libs(control_dict_path, *required)
    for r in required:
        if r not in have:
            raise FoamLibsError("%s: %s absent after write" % (control_dict_path, r))
    return have


# --------------------------------------------------------------------------
# Selftest
# --------------------------------------------------------------------------

_HEAD = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     buoyantBoussinesqSimpleFoam;
endTime         30000;
"""

_FUNCS = """
functions
{
    wallHeatFlux
    {
        type            wallHeatFlux;
        libs            (fieldFunctionObjects);
    }
    sampleLine
    {
        type            sets;
        libs            (sampling);
    }
}

// ************************************************************************* //
"""


def _selftest():
    if sys.flags.optimize:
        print("REFUSE: foam_libs selftest does not run under python -O -- its checks would be stripped")
        return 2
    import tempfile
    import traceback

    results = []

    def check(name, fn):
        try:
            fn()
            results.append(("PASS", name, ""))
        except Exception as exc:                      # noqa: BLE001
            results.append(("FAIL", name, "%s: %s" % (type(exc).__name__, exc)))
            traceback.print_exc()

    tmp = tempfile.mkdtemp(prefix="foam_libs_selftest_")

    def write(name, body):
        p = os.path.join(tmp, name)
        open(p, "w").write(body)
        return p

    QCR = "libkOmegaSSTQCRTurbulenceModels.so"

    # 1. ABSENT KEY -- the K0cQ shape.  8 sub-dict libs lines, no top-level one.
    def t_absent():
        p = write("absent", _HEAD + _FUNCS)
        assert len(top_level_libs_entries(open(p).read())) == 0, "precondition"
        got = ensure_libs(p, QCR)
        assert got == [QCR], got
        s = open(p).read()
        assert len(top_level_libs_entries(s)) == 1, "exactly one top-level entry"
        # inserted after the banner, BEFORE the functions block
        assert s.index("libs ( \"%s\" );" % QCR) < s.index("functions"), \
            "must be inserted after the banner, not appended past the footer"
        assert "libs            (fieldFunctionObjects);" in s, "sub-dict libs untouched"
        assert "libs            (sampling);" in s, "sub-dict libs untouched"
        assert_libs(p, QCR)
    check("absent key -> inserted after banner, sub-dict libs untouched", t_absent)

    # 2. EXISTING WITH ANOTHER LIB -- merge must keep BOTH.  This is the case a
    #    blind `>>` append and a blind `re.sub` replace each get wrong, in
    #    opposite directions.
    def t_merge():
        p = write("merge", _HEAD + '\nlibs ( "libOther.so" );\n' + _FUNCS)
        got = ensure_libs(p, QCR)
        assert got == ["libOther.so", QCR], got
        s = open(p).read()
        assert len(top_level_libs_entries(s)) == 1, "still exactly one"
        assert "libOther.so" in s and QCR in s, "both libs survive"
        assert_libs(p, "libOther.so", QCR)
    check("existing other lib -> merged, both kept, order preserved", t_merge)

    # 2b. IDEMPOTENCE: running twice must not produce a second entry.
    def t_idem():
        p = write("idem", _HEAD + _FUNCS)
        ensure_libs(p, QCR)
        first = open(p).read()
        ensure_libs(p, QCR)
        assert open(p).read() == first, "ensure_libs is not idempotent"
        assert len(top_level_libs_entries(first)) == 1
    check("idempotent -- second ensure is a byte-for-byte no-op", t_idem)

    # 3. DUPLICATE DETECTION -- two top-level entries, the signature of the
    #    blind append that this module exists to retire.
    def t_dup():
        p = write("dup", _HEAD + '\nlibs ( "libA.so" );\n' + _FUNCS +
                  '\nlibs ( "libB.so" );\n')
        s = open(p).read()
        assert len(top_level_libs_entries(s)) == 2, "precondition: two entries"
        try:
            assert_libs(p, "libA.so")
        except FoamLibsError as exc:
            assert "2 top-level libs entries" in str(exc), str(exc)
        else:
            raise AssertionError("assert_libs did NOT flag the duplicate")
        # ensure_libs repairs it, announced on stderr, to the union.
        got = ensure_libs(p, QCR)
        assert got == ["libA.so", "libB.so", QCR], got
        assert len(top_level_libs_entries(open(p).read())) == 1, "collapsed to one"
    check("duplicate entries -> assert FAILS, ensure repairs to union", t_dup)

    # 4. SUB-DICT libs MUST NOT COUNT.  A functions-only dict has NO top-level
    #    libs, and assert_libs must say so rather than reading a function
    #    object's loader as the solver's library list.
    def t_subdict():
        p = write("subdict", _HEAD + _FUNCS)
        s = open(p).read()
        assert len(_LIBS_TOKEN.findall(s)) == 2, "two libs lines present"
        assert top_level_libs_entries(s) == [], "none of them is top-level"
        try:
            assert_libs(p, "fieldFunctionObjects")
        except FoamLibsError as exc:
            assert "NO top-level libs entry" in str(exc), str(exc)
        else:
            raise AssertionError("a functions{} libs line was read as top-level")
    check("libs inside functions{} does NOT count as top-level", t_subdict)

    # 5. BANNER MISSING -> guarded append at end, still verified on disk.
    def t_nobanner():
        p = write("nobanner", "application foo;\nendTime 10;\n")
        got = ensure_libs(p, QCR)
        assert got == [QCR], got
        assert len(top_level_libs_entries(open(p).read())) == 1
        assert_libs(p, QCR)
    check("banner missing -> guarded append at end of file", t_nobanner)

    # 6. A brace inside a comment or a string must not move the depth.
    def t_bracetrap():
        p = write("bracetrap",
                  _HEAD + '// a stray { in a comment\n'
                  '\nlibs ( "libA.so" );\n' + _FUNCS)
        got = ensure_libs(p, QCR)
        assert got == ["libA.so", QCR], got
        assert len(top_level_libs_entries(open(p).read())) == 1
    check("brace inside a comment does not shift depth", t_bracetrap)

    width = max(len(n) for _, n, _ in results)
    print("foam_libs.py --selftest")
    print("-" * (width + 12))
    for status, name, detail in results:
        print("%-4s  %-*s %s" % (status, width, name, detail))
    print("-" * (width + 12))
    bad = [r for r in results if r[0] == "FAIL"]
    print("%d/%d passed" % (len(results) - len(bad), len(results)))
    print("tmp tree: %s" % tmp)
    return 1 if bad else 0


def main(argv):
    if "--selftest" in argv:
        if sys.flags.optimize:
            print("REFUSE: foam_libs selftest does not run under python -O -- its checks would be stripped")
            return 2
        return _selftest()
    if len(argv) < 3:
        sys.stderr.write(__doc__.split("CLI\n")[-1])
        return 2
    mode, path, libs = argv[0], argv[1], argv[2:]
    if mode not in ("ensure", "assert"):
        sys.stderr.write("REFUSE: mode must be 'ensure' or 'assert', got %r\n" % mode)
        return 2
    try:
        have = (ensure_libs if mode == "ensure" else assert_libs)(path, *libs)
    except FoamLibsError as exc:
        sys.stderr.write("REFUSE: %s\n" % exc)
        return 2
    print("OK %s  libs ( %s )" % (path, " ".join(have)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
