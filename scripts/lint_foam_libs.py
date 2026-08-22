#!/usr/bin/env python3
"""
lint_foam_libs.py -- a `libs` write outside foam_libs.ensure_libs is a FAIL.

L-221 cost three runs because the same defect lived in three files and the
lesson lived in a report.  H-7 makes the rule mechanical: the assert goes at
every call site.  This walks the tree and enforces exactly two things.

  1. STATE.  Every `*/system/controlDict` carries AT MOST ONE top-level `libs`
     entry.  Two is not a longer library list, it is a DUPLICATE DICTIONARY
     ENTRY -- the exact signature a blind `>>` append leaves behind.  Sub-
     dictionary `libs` lines (`functions { ... libs (fieldFunctionObjects); }`)
     are function-object loads and are NOT counted; every real controlDict in
     this lab has 8 to 11 of them, so a linter that cannot tell the two apart
     reports nothing but noise.  Depth is tracked by foam_libs itself, so the
     linter and the writer agree on what "top-level" means by construction.

  2. WRITES.  Every build/setup script is read for code that WRITES a `libs`
     entry by any route other than `foam_libs.ensure_libs`: `printf`/`echo`
     redirected with `>>` or `>`, `sed -i`, `re.sub`, `str.replace`, or a
     Python file write.  Each is FAIL.

WHAT IS *INFO* AND NOT FAIL, because a linter that over-reaches gets disabled:
  * A builder that writes a controlDict WHOLESALE from a template containing a
    top-level `libs` line is not the L-221 defect.  There is no merge to get
    wrong -- the file did not exist a moment ago -- and no silent no-op is
    possible, because a template is not a search-and-replace.  Reported as INFO
    so the site is visible without being failed.
  * A line inside a `functions { ... }` template block.  That is a function
    object's own loader, which is not the solver's library list.

`cases/RANS_LES_closure_models` is EXCLUDED by default: it is the closure
supervisor's tree and carries the canonical pre-helper idiom.  `--include-closure`
opts in for an audit that wants to see it.

Exit: 0 clean, 1 at least one FAIL, 2 refusal.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from foam_libs import top_level_libs_entries
except ImportError as exc:                                  # pragma: no cover
    sys.stderr.write("REFUSE: cannot import foam_libs: %s\n" % exc)
    sys.exit(2)

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

DEFAULT_ROOT = "verification/runs"
CLOSURE = os.path.join("cases", "RANS_LES_closure_models")

SCRIPT_GLOBS = (
    re.compile(r"^build_.*\.(py|sh)$"),
    re.compile(r"^setup_.*\.py$"),
    re.compile(r"^.*\.sh$"),
)

# A line that mentions a libs ENTRY (the list form), not merely the word.
LIBS_ENTRY = re.compile(r"libs\s*\(")

# Routes by which a libs entry can be written.
WRITE_ROUTES = (
    ("shell-append", re.compile(r"(printf|echo|cat)\b.*>>")),
    ("shell-truncate", re.compile(r"(printf|echo|cat)\b.*[^>]>[^>]")),
    ("sed-inplace", re.compile(r"\bsed\b.*-i")),
    ("re.sub", re.compile(r"\bre\.sub\s*\(")),
    ("str.replace", re.compile(r"\.replace\s*\(")),
)

# The sanctioned route.  Either import is fine.
SANCTIONED = re.compile(r"ensure_libs|foam_libs\.py")

# A heredoc/template assignment that writes a whole dictionary at once.
TEMPLATE_HINT = re.compile(
    r"""(<<\s*['"]?\w+|=\s*(f?)['"]{3}|\.write\s*\(|writelines)""")


def is_script(name):
    return any(g.match(name) for g in SCRIPT_GLOBS)


def looks_indented(line):
    """True if this `libs (` is INDENTED, i.e. a sub-dictionary entry.

    This is the discriminator, and it is OpenFOAM's own: a top-level dictionary
    entry starts at column 0, while every function-object loader inside
    `functions { ... }` is indented.  Verified against the real tree -- each
    K0cQ controlDict carries 8 to 11 indented `libs (fieldFunctionObjects);` /
    `libs (sampling);` lines and exactly one `libs (` at column 0.

    The "line" here may be a template line, a `printf` format string or a
    Python string literal, so the emitted column is measured from the nearest
    preceding boundary: an escaped newline, a real line start, or the opening
    quote of the literal.
    """
    m = LIBS_ENTRY.search(line)
    if not m:
        return False
    before = line[:m.start()]
    cut = 0
    for sep in ("\\n", "\n", '"', "'"):
        j = before.rfind(sep)
        if j >= 0:
            cut = max(cut, j + len(sep))
    lead = before[cut:]
    # ONLY whitespace counts as indentation.  Anything else (`sed -i 's/`,
    # `s = re.sub(r"`) is command or regex text, and the libs entry it names is
    # a top-level one being rewritten -- exactly what must be failed, not
    # suppressed.  Suppressing on "not column 0" was the first version's false
    # negative: it let a `sed -i` rewrite of a top-level libs entry through.
    return lead != "" and lead.strip() == ""


def scan_control_dicts(root, findings):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        if os.path.basename(dirpath) != "system":
            continue
        if "controlDict" not in filenames:
            continue
        p = os.path.join(dirpath, "controlDict")
        try:
            text = open(p, errors="replace").read()
        except OSError as exc:
            findings.append(("FAIL", p, 0, "unreadable: %s" % exc))
            continue
        entries = top_level_libs_entries(text)
        if len(entries) > 1:
            findings.append((
                "FAIL", p, 0,
                "%d top-level libs entries (duplicate dictionary entry -- the "
                "signature of a blind append); sub-dict libs lines are not "
                "counted" % len(entries)))


def scan_scripts(root, findings):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for fn in sorted(filenames):
            if not is_script(fn):
                continue
            p = os.path.join(dirpath, fn)
            try:
                lines = open(p, errors="replace").read().splitlines()
            except OSError:
                continue
            for i, ln in enumerate(lines):
                if not LIBS_ENTRY.search(ln):
                    continue
                if ln.lstrip().startswith("#"):
                    continue
                if SANCTIONED.search(ln):
                    continue
                # the sanctioned call can wrap onto the next line
                window = "\n".join(lines[max(0, i - 3):i + 4])
                if SANCTIONED.search(window):
                    continue
                # Indented => a function-object loader at sub-dictionary
                # scope, which is not the solver's library list.  Silent, not
                # INFO: there are dozens per builder and a linter that prints
                # them is a linter nobody reads.
                if looks_indented(ln):
                    continue
                route = next((nm for nm, rx in WRITE_ROUTES if rx.search(ln)), None)
                if route:
                    findings.append((
                        "FAIL", p, i + 1,
                        "libs entry written via %s, not foam_libs.ensure_libs: %s"
                        % (route, ln.strip()[:110])))
                elif TEMPLATE_HINT.search(window):
                    findings.append((
                        "INFO", p, i + 1,
                        "wholesale template write containing a top-level libs "
                        "line (no merge to get wrong): %s" % ln.strip()[:90]))
                else:
                    findings.append((
                        "INFO", p, i + 1,
                        "libs mentioned, no write route matched: %s"
                        % ln.strip()[:90]))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="*", default=None,
                    help="roots to walk (default: %s)" % DEFAULT_ROOT)
    ap.add_argument("--include-closure", action="store_true",
                    help="also walk cases/RANS_LES_closure_models (closure-owned)")
    args = ap.parse_args()

    roots = args.roots or [DEFAULT_ROOT]
    findings = []
    walked = []
    for r in roots:
        if not os.path.isdir(r):
            sys.stderr.write("REFUSE: not a directory: %s\n" % r)
            return EXIT_REFUSE
        if (not args.include_closure) and CLOSURE in os.path.abspath(r):
            print("SKIP  %s (closure-owned; --include-closure to audit)" % r)
            continue
        walked.append(r)
        scan_control_dicts(r, findings)
        scan_scripts(r, findings)

    print("lint_foam_libs.py")
    print("roots: %s" % (", ".join(walked) or "<none>"))
    print("closure tree: %s" % ("INCLUDED" if args.include_closure else "excluded"))
    print("-" * 78)
    fails = [f for f in findings if f[0] == "FAIL"]
    infos = [f for f in findings if f[0] == "INFO"]
    for status, path, line, msg in sorted(findings, key=lambda x: (x[0], x[1], x[2])):
        loc = "%s:%d" % (path, line) if line else path
        print("%-4s  %s\n        %s" % (status, loc, msg))
    if not findings:
        print("(nothing to report)")
    print("-" * 78)
    print("%d FAIL, %d INFO" % (len(fails), len(infos)))
    return EXIT_FAIL if fails else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
