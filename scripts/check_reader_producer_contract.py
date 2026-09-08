#!/usr/bin/env python3
"""check_reader_producer_contract.py -- STATIC pre-freeze reader<->producer
marker/basename contract check.

WHY THIS EXISTS (the SO3DR-F6 / stage2_ vs stage2R_ class)
----------------------------------------------------------
A grader (the READER) parses line-start MARKERS and named INPUT FILES out of a
run it did not itself produce. If the rig / launcher / driver (the PRODUCER)
writes a DIFFERENT basename or a typo'd marker -- `stage2_` where the reader
looks for `stage2R_`, `D6RF9_LEG_BEGN` where the reader looks for
`D6RF9_LEG_BEGIN` -- then on a CLEAN run the reader silently finds nothing, and
the grade is `NOT A RESULT`/`BAR_NOT_PRODUCED` for a reason that has nothing to
do with the physics. This is a whole CLASS of defect (SO3DR-F4 write-after-run,
SO3DR-F6 sample-path typo, and every future one): a reader and a producer that
disagree on a name. This guard turns "the reader parses names no producer
writes" into a STATIC pre-freeze REFUSAL, so the mismatch cannot be frozen.

It is a SIBLING of `check_sidecar_before_run.py`, NOT an extension of it: that
instrument enforces a different invariant (an input echo must be WRITTEN BEFORE
the run trigger, L-504 clause-c) and is cited by a possibly-frozen prereg
(`curriculum_SO3DR_stage2_R/PREREGISTRATION.md`). Bolting an orthogonal check
onto a shared/possibly-frozen instrument, and conflating its selftest, is the
wrong move; this class gets its own file and its own planted control.

WHAT IT CHECKS
--------------
Given a READER file (a grader, parsed with `ast`), an ITEM PREFIX (e.g.
`D6RF9`), zero or more PRODUCER files (.py or .sh), and zero or more explicit
`--expect-file` input paths:

  (A) CONTRACT.  Extract the READER's contract tokens: string literals it parses
      at a line start via `<s>.startswith(<x>)` or membership `<x> in <s>`,
      where <x> is a string literal or a module-level name bound to one, AND the
      literal CONTAINS the item prefix (so DAFoam's own banners -- "Primal
      solution failed!" -- are NOT contract tokens; only THIS item's markers
      are). For EACH such token, at least ONE producer must EMIT it (a string
      literal carrying the token as a substring, inside a `print(...)`/`.write`
      for .py, or on a non-comment `echo`/`printf` line for .sh). A token no
      producer emits -> REFUSE. Reader has prefixed tokens but NO producer file
      was supplied -> REFUSE (the reader parses markers nothing on disk writes).

  (B) EXISTENCE.  Every `--expect-file PATH` must exist on disk with that EXACT
      basename. Additionally, any argparse default that looks like an input
      sample (`--*sample*`, `--*log*`, `--*path*` with a string-literal
      `default=`) must exist with its exact basename. A default naming a file
      that is not on disk with that basename -> REFUSE (the F6 on-disk case).

WHAT A STATIC CHECK CANNOT CATCH (stated honestly, as the sibling does)
-----------------------------------------------------------------------
  * A producer that composes the marker from a VARIABLE prefix in an f-string
    (`print(f"{PREFIX}_LEG_BEGIN")`): the guard sees the literal part
    `_LEG_BEGIN` but not the `PREFIX`-composed whole, so a reader token that is
    the WHOLE `D6RF9_LEG_BEGIN` may not substring-match. Emit the full literal
    token in the producer, or pass the producer and accept this limitation.
  * A reader that builds the marker it looks for at runtime, or reads names from
    argv/JSON. Extraction is literal-and-one-level-name, like the sibling.
  * It does not check the ORDER of markers, nor that the producer emits them on
    the legs it should -- only that the NAMES agree. Necessary, not sufficient.
  * .sh comment stripping is heuristic (a `#` preceded by whitespace ends the
    line); a token hidden only in a comment is deliberately NOT counted as
    emitted (that would be a false PASS), so a commented reference does not
    satisfy the contract.

PLANTED-CONTROL DISCIPLINE (CLAUDE.md rule 3 family)
----------------------------------------------------
`--selftest` runs the guard against synthetic fixtures: a MATCHING reader+
producer (must PASS), a TYPO'd producer (must FIRE), a reader with prefixed
tokens and NO producer (must FIRE), and an `--expect-file` existence pair (a
present file must PASS, an absent basename must FIRE). A guard that cannot be
shown to FIRE is not evidence.

EXITS: 0 PASS | 3 REFUSE (contract or existence violation) | 2 usage |
       4 parse error | 1 selftest failed. SUBMISSIONS PARKED; nothing leaves.
"""
import argparse
import ast
import os
import sys

STARTSWITH_ATTRS = {"startswith"}
WRITE_ATTRS = {"write"}
PRINT_NAMES = {"print"}


class ContractRefusal(Exception):
    """Raised when a reader contract token is not emitted by any producer, or an
    expected input file is absent with its exact basename."""


# ----------------------------- READER side --------------------------------
def _module_str_consts(tree):
    """name -> str value for `Name = "literal"` assignments anywhere in the
    tree (one level of name resolution, matching the sibling's discipline)."""
    consts = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) \
                and isinstance(n.value.value, str):
            for tgt in n.targets:
                if isinstance(tgt, ast.Name):
                    consts[tgt.id] = n.value.value
    return consts


def _resolve_str(node, consts):
    """A str literal, or a Name bound to one; else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in consts:
        return consts[node.id]
    return None


def reader_contract_tokens(source, item_prefix, filename="<reader>"):
    """The line-start markers the reader parses that carry the item prefix."""
    tree = ast.parse(source, filename=filename)
    consts = _module_str_consts(tree)
    tokens = set()
    for n in ast.walk(tree):
        # <s>.startswith(<x>)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in STARTSWITH_ATTRS and n.args:
            v = _resolve_str(n.args[0], consts)
            if v and item_prefix in v:
                tokens.add(v)
        # <x> in <s>   (Compare, In op, left is the needle)
        if isinstance(n, ast.Compare) and len(n.ops) == 1 \
                and isinstance(n.ops[0], ast.In):
            v = _resolve_str(n.left, consts)
            if v and item_prefix in v:
                tokens.add(v)
    return tokens


def reader_sample_defaults(source, filename="<reader>"):
    """[(option, default_basename, default_path)] for argparse add_argument
    calls whose option looks like an input sample and has a str default."""
    tree = ast.parse(source, filename=filename)
    out = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_argument"):
            continue
        opts = [a.value for a in n.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        looks_input = any(k in o.lower()
                          for o in opts for k in ("sample", "log", "path"))
        if not looks_input:
            continue
        for kw in n.keywords:
            if kw.arg == "default" and isinstance(kw.value, ast.Constant) \
                    and isinstance(kw.value.value, str):
                p = kw.value.value
                out.append((opts[0] if opts else "?", os.path.basename(p), p))
    return out


# ---------------------------- PRODUCER side -------------------------------
def _py_emitted_literals(source, filename="<producer>"):
    """String literals emitted by a .py producer: args of print(...) and of
    any `.write(...)` call, plus the constant parts of f-strings in those."""
    tree = ast.parse(source, filename=filename)
    lits = []

    def _lits_under(node):
        for c in ast.walk(node):
            if isinstance(c, ast.Constant) and isinstance(c.value, str):
                lits.append(c.value)

    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            is_print = isinstance(n.func, ast.Name) and n.func.id in PRINT_NAMES
            is_write = isinstance(n.func, ast.Attribute) \
                and n.func.attr in WRITE_ATTRS
            if is_print or is_write:
                for a in n.args:
                    _lits_under(a)
    return lits


def _sh_emitted_text(source):
    """Emitted text of a .sh producer: non-comment lines carrying echo/printf,
    with any whitespace-preceded inline comment stripped (heuristic)."""
    out = []
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "echo" not in line and "printf" not in line:
            continue
        # strip a whitespace-preceded inline comment (conservative heuristic)
        cut = line
        for i in range(1, len(line)):
            if line[i] == "#" and line[i - 1] in " \t":
                cut = line[:i]
                break
        out.append(cut)
    return out


def producer_emits(path):
    """The list of emitted strings (as substrings to match against) for one
    producer file. .py -> emitted literals; .sh -> emitted text lines."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    if path.endswith(".py"):
        return _py_emitted_literals(src, filename=path)
    return _sh_emitted_text(src)


# ------------------------------- the check --------------------------------
def check(reader, item_prefix, producers, expect_files):
    """Run the contract + existence checks. Returns a report dict; raises
    ContractRefusal on any violation."""
    with open(reader, encoding="utf-8") as fh:
        rsrc = fh.read()
    tokens = reader_contract_tokens(rsrc, item_prefix, filename=reader)
    defaults = reader_sample_defaults(rsrc, filename=reader)

    report = {"reader": reader, "item_prefix": item_prefix,
              "reader_contract_tokens": sorted(tokens),
              "producers": list(producers),
              "sample_defaults": defaults}

    # ---- (A) CONTRACT ----
    if tokens and not producers:
        raise ContractRefusal(
            "reader %s parses %d prefixed marker(s) %s but NO producer file was "
            "supplied to write them. The reader parses markers nothing on disk "
            "writes -- name the rig/launcher/driver, or it cannot be shown that "
            "any leg the reader looks for is ever produced."
            % (reader, len(tokens), sorted(tokens)))
    emitted = {}
    for p in producers:
        emitted[p] = producer_emits(p)
    unmatched = {}
    for tok in sorted(tokens):
        producers_with = [p for p in producers
                          if any(tok in e for e in emitted[p])]
        if not producers_with:
            unmatched[tok] = None
    report["emitted_counts"] = {p: len(emitted[p]) for p in producers}
    report["matched_tokens"] = {
        tok: [p for p in producers if any(tok in e for e in emitted[p])]
        for tok in sorted(tokens)}
    if unmatched:
        raise ContractRefusal(
            "reader %s parses marker(s) %s that NO supplied producer emits "
            "(producers: %s). A reader and a producer that disagree on a name "
            "grade a clean run NOT A RESULT for a name, not a number "
            "(SO3DR-F6 class)." % (reader, sorted(unmatched), list(producers)))

    # ---- (B) EXISTENCE ----
    missing = []
    checked = []
    for p in expect_files:
        base = os.path.basename(p)
        ok = os.path.isfile(p) and os.path.basename(p) == base
        checked.append({"path": p, "basename": base, "exists": ok})
        if not ok:
            missing.append(p)
    for opt, base, path in defaults:
        exists = os.path.isfile(path)
        checked.append({"option": opt, "basename": base, "default": path,
                        "exists": exists})
        if not exists:
            missing.append(path)
    report["existence_checked"] = checked
    if missing:
        raise ContractRefusal(
            "expected input file(s) absent with their exact basename: %s. A "
            "grader whose default/registered sample is not on disk with the "
            "basename it looks for reads nothing on a clean run (F6 class)."
            % missing)

    report["verdict"] = "PASS"
    return report


def check_cli(reader, item_prefix, producers, expect_files):
    if not os.path.isfile(reader):
        sys.stderr.write("check_reader_producer_contract: no reader %s\n" % reader)
        return 4
    try:
        rep = check(reader, item_prefix, producers, expect_files)
    except SyntaxError as e:
        sys.stderr.write("parse error: %s\n" % e)
        return 4
    except ContractRefusal as e:
        sys.stderr.write("REFUSE (exit 3): %s\n" % e)
        return 3
    sys.stdout.write(
        "PASS: reader %s -- %d contract token(s) all emitted by a producer, "
        "%d existence check(s) ok\n"
        % (reader, len(rep["reader_contract_tokens"]),
           len(rep["existence_checked"])))
    return 0


# --------------------------------------------------------------------------
# PLANTED CONTROL (rule 3 family): the guard must be shown able to FIRE
# --------------------------------------------------------------------------
_READER_FIX = '''
import argparse
LEG_BEGIN = "ZZZ_LEG_BEGIN"
LEG_END = "ZZZ_LEG_END"
MARKER = "ZZZ_CONFIG_INSTALLED"
BANNER = "Primal solution failed!"
def read_legs(path):
    for line in open(path):
        if line.startswith(LEG_BEGIN): pass
        if line.startswith(LEG_END): pass
        if line.startswith(MARKER): pass
        if BANNER in line: pass
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log")
    ap.add_argument("--rung", default="R1")
'''

_PRODUCER_OK = '''
def run():
    print("ZZZ_CONFIG_INSTALLED leg=R1 endTime=2500")
    print("ZZZ_LEG_BEGIN R1 mode=P_conv")
    print("ZZZ_LEG_END R1 mode=P_conv")
'''

_PRODUCER_TYPO = '''
def run():
    print("ZZZ_CONFIG_INSTALLED leg=R1 endTime=2500")
    print("ZZZ_LEG_BEGN R1 mode=P_conv")   # typo: BEGN
    print("ZZZ_LEG_END R1 mode=P_conv")
'''


def _write(tmp, name, text):
    p = os.path.join(tmp, name)
    with open(p, "w") as fh:
        fh.write(text)
    return p


def _fires(reader, prefix, producers, expect):
    try:
        check(reader, prefix, producers, expect)
        return False
    except ContractRefusal:
        return True


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="rpc_selftest_")
    reader = _write(tmp, "reader.py", _READER_FIX)
    prod_ok = _write(tmp, "producer_ok.py", _PRODUCER_OK)
    prod_typo = _write(tmp, "producer_typo.py", _PRODUCER_TYPO)
    present = _write(tmp, "present_sample.txt", "x\n")
    absent = os.path.join(tmp, "absent_sample.txt")

    checks = [
        ("matching reader+producer -> PASS",
         _fires(reader, "ZZZ", [prod_ok], []), False),
        ("typo'd producer marker -> REFUSE",
         _fires(reader, "ZZZ", [prod_typo], []), True),
        ("prefixed tokens but NO producer -> REFUSE",
         _fires(reader, "ZZZ", [], []), True),
        ("expect-file present -> PASS",
         _fires(reader, "ZZZ", [prod_ok], [present]), False),
        ("expect-file absent basename -> REFUSE",
         _fires(reader, "ZZZ", [prod_ok], [absent]), True),
    ]
    # negative control: a prefix that matches NO reader token (nothing to
    # contract) and no producer must PASS -- there is nothing to disagree on.
    checks.append(("prefix matches no token, no producer -> PASS",
                   _fires(reader, "QQQ", [], []), False))
    all_ok = True
    for label, fired, must_fire in checks:
        ok = (fired == must_fire)
        all_ok = all_ok and ok
        print("  [%s] %s  (fired=%s, expected_fire=%s)"
              % ("OK" if ok else "FAIL", label, fired, must_fire))
    if all_ok:
        print("SELFTEST OK -- the guard FIRES on a name mismatch / missing "
              "producer and PASSES when the names agree.")
        return 0
    print("SELFTEST FAILED -- the guard did not behave as a planted control "
          "requires.")
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Static reader<->producer marker/basename contract check.")
    p.add_argument("--reader", help="the grader/reader .py file")
    p.add_argument("--item-prefix",
                   help="only markers carrying this substring are contract "
                        "tokens (e.g. D6RF9)")
    p.add_argument("--producer", action="append", default=[],
                   help="a rig/launcher/driver that writes the markers (repeatable)")
    p.add_argument("--expect-file", action="append", default=[],
                   help="an input path that must exist with its exact basename "
                        "(repeatable)")
    p.add_argument("--selftest", action="store_true",
                   help="run the planted-control selftest and exit")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.reader or not args.item_prefix:
        sys.stderr.write("usage: --reader <grader.py> --item-prefix <PFX> "
                         "[--producer <f> ...] [--expect-file <p> ...] "
                         "| --selftest\n")
        return 2
    return check_cli(args.reader, args.item_prefix, args.producer,
                     args.expect_file)


if __name__ == "__main__":
    sys.exit(main())
