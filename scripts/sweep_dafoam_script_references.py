"""Sweep every dafoam driver/launcher for references to sibling scripts that are
ABSENT FROM DISK -- the SO2a-DRIVER-DEF-1 shape (2026-08-30).

WHY.  SO-2a's copy-forward from SO-1a took the chain driver and NOT the
`*_aggregate_memory.py` it calls at line 143.  The reference resolved to nothing,
`AGG` was the empty string, the `ok` test could never be true, and the driver was
guaranteed to poll for four hours and write BLOCKED_AGGREGATE at the first arm --
an 8 GB reservation held for four hours to produce no verdict.  The freeze did not
catch it because the pre-registration's instrument table enumerates INSTRUMENTS and
not their DEPENDENCIES: eight of eight md5s agreed while the ninth file was absent.
Rule 14: a lesson is not applied until EVERY call site asserts it.  This is the
call-site assertion.

METHOD.  `os.walk`, never a recursive grep -- ugrep honours ignore files and races
on multi-file output, so a recursive grep's zero here would mean nothing.  Every
`.sh` under the tree is read as bytes.  For each, `$HERE` is bound to the script's
own directory (the `cd "$(dirname "$0")"` idiom this family uses everywhere) and
every other `VAR=` assignment whose value resolves to a literal path is bound too.
Every `$VAR/name`, `${VAR}/name` and bare `python3 name.py` / `bash name.sh`
reference is then resolved and tested with os.path.exists.

CLASSIFICATION.
  PRESENT  the target exists on disk.
  ABSENT   it does not -- the SO2a shape, and the thing this sweep hunts.
  RUNTIME  the target sits under a run root (a `BASE=` path outside the repo).
           A run root is created by the fire, so absence there is normal and is
           reported without alarm.  Never silently dropped: a RUNTIME row that
           looks like an instrument is still a row a reader can see.

KNOWN POSITIVE.  `--root` lets the sweep be pointed at an exported tree.  Pointed
at the tree as it stood BEFORE the SO-2a repair, it MUST report
so2a_aggregate_memory.py ABSENT.  A sweep that cannot see the defect it was
written for has zeros that mean nothing (standing rule 3).
"""
import argparse
import os
import re
import sys

VARREF = re.compile(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?/([A-Za-z0-9_.@+-]+(?:\.[A-Za-z0-9]+)?)')
ASSIGN = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)=(.+?)\s*$')
BARE = re.compile(r'(?:^|[;&|(]\s*|\s)(?:python3?|bash|sh)\s+"?\./?([A-Za-z0-9_.@+-]+\.(?:py|sh))"?')
# `( cd "$D18" && python3 ./d18_grade.py ... )` -- the bare name resolves against
# the cd's directory, NOT the script's own.  The first version of this sweep
# missed that and reported curriculum_D18R_P7's `./d18_grade.py` ABSENT when
# $D18/d18_grade.py is present: a FALSE ABSENT, which is the failure that lets a
# real ABSENT hide in noise.  Caught by resolving the one hit by hand before
# reporting it, and fixed here rather than annotated away.
CDVAR = re.compile(r'\bcd\s+"?\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?"?')
# a reference is only interesting if it names a FILE -- these are the extensions
# this family's instruments actually carry
INTERESTING = (".py", ".sh", ".json", ".txt", ".diff", ".md")


def strip_comment(line):
    """Drop a whole-line shell comment.  A trailing comment after code is left
    alone: quoting makes it unsafe to guess, and a false PRESENT is worse than a
    duplicate row."""
    return "" if line.lstrip().startswith("#") else line


def bind_vars(path, text):
    """HERE is the script's own directory (the family's `cd "$(dirname "$0")"`
    idiom).  Every other simple literal assignment is bound as written."""
    env = {"HERE": os.path.dirname(os.path.abspath(path))}
    for raw in text.splitlines():
        line = strip_comment(raw)
        m = ASSIGN.match(line)
        if not m:
            continue
        name, val = m.group(1), m.group(2)
        val = val.split("#")[0].strip().strip('"').strip("'")
        if not val or "$(" in val or "`" in val:
            continue
        # one level of substitution against what is already bound
        def sub(mm):
            return env.get(mm.group(1), "\x00")
        val = re.sub(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?', sub, val)
        if "\x00" in val or "$" in val:
            continue
        if val.startswith("/"):
            env[name] = val.rstrip("/")
    return env


def classify(target, repo_root):
    if os.path.exists(target):
        return "PRESENT"
    inside = os.path.abspath(target).startswith(os.path.abspath(repo_root) + os.sep)
    return "ABSENT" if inside else "RUNTIME"


def sweep(root, repo_root):
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in sorted(filenames):
            if not fn.endswith(".sh"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                text = open(path, "rb").read().decode("utf-8", "replace")
            except OSError:
                continue
            env = bind_vars(path, text)
            here = env["HERE"]
            seen = set()
            for raw in text.splitlines():
                line = strip_comment(raw)
                for m in VARREF.finditer(line):
                    var, name = m.group(1), m.group(2)
                    if not name.endswith(INTERESTING):
                        continue
                    if var not in env:
                        continue
                    target = os.path.join(env[var], name)
                    key = ("$" + var, name)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append((path, "$%s/%s" % (var, name), target,
                                 classify(target, repo_root)))
                for m in BARE.finditer(line):
                    name = m.group(1)
                    base = here
                    label = "bare"
                    cdm = [c for c in CDVAR.finditer(line) if c.start() < m.start()]
                    if cdm and cdm[-1].group(1) in env:
                        base = env[cdm[-1].group(1)]
                        label = "cd $%s" % cdm[-1].group(1)
                    target = os.path.join(base, name)
                    key = (label, name)
                    if key in seen:
                        continue
                    seen.add(key)
                    ref = name if label == "bare" else "%s/%s" % (label, name)
                    rows.append((path, ref, target, classify(target, repo_root)))
    return rows


def item_of(path, root):
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)
    return os.sep.join(parts[:-1]) or "."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/ubuntu/Certonomous/cases/dafoam")
    ap.add_argument("--repo-root", default=None,
                    help="paths under this prefix are repo files; outside it a "
                         "missing target is RUNTIME.  Defaults to --root.")
    ap.add_argument("--absent-only", action="store_true")
    ap.add_argument("--expect-absent", default=None,
                    help="known-positive check: this basename MUST appear ABSENT, "
                         "else exit 3")
    a = ap.parse_args()
    repo_root = a.repo_root or a.root
    rows = sweep(a.root, repo_root)

    n_abs = sum(1 for r in rows if r[3] == "ABSENT")
    n_run = sum(1 for r in rows if r[3] == "RUNTIME")
    print("SWEEP root=%s" % a.root)
    print("shell files walked (os.walk, not grep): %d"
          % len({r[0] for r in rows}))
    print("references resolved: %d   PRESENT %d   ABSENT %d   RUNTIME %d"
          % (len(rows), len(rows) - n_abs - n_run, n_abs, n_run))
    print("")
    print("%-46s %-34s %s" % ("item", "referenced", "verdict"))
    print("-" * 100)
    for path, ref, target, verdict in sorted(rows, key=lambda r: (r[3] != "ABSENT", r[0], r[1])):
        if a.absent_only and verdict == "PRESENT":
            continue
        print("%-46s %-34s %s" % (item_of(path, a.root)[:46], ref[:34], verdict))

    if a.expect_absent:
        hits = [r for r in rows if os.path.basename(r[2]) == a.expect_absent
                and r[3] == "ABSENT"]
        if not hits:
            print("\nKNOWN-POSITIVE FAILED: %s was not reported ABSENT.  This "
                  "sweep cannot see the defect it hunts and its zeros mean "
                  "nothing." % a.expect_absent)
            return 3
        print("\nKNOWN-POSITIVE OK: %s reported ABSENT in %d place(s)."
              % (a.expect_absent, len(hits)))
        for h in hits:
            print("  %s -> %s" % (h[0], h[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
