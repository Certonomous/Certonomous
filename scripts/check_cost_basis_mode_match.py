#!/usr/bin/env python3
"""check_cost_basis_mode_match.py — the executable check shipping with L-520.

THE PROPOSITION UNDER TEST
--------------------------
A pre-registration's cost basis must price the POST-FREEZE GRADED INVOCATION,
and only that. When the cost section charges for a MODE that the registered
`launch_cmd` does not invoke, the estimate prices work the run will never
perform, and the run under-runs its budget by the size of the unpriced mode.

Two closure items on 2026-09-10 came in at actual/predicted ratios 0.259 and
0.062 for exactly this reason (docs/COST_CALIBRATION.md rows
C-20260910T040337.011383Z-01cfe9a4 and C-20260910T040337.011480Z-8db039c0).

Two mode classes are detected:

  SELFTEST_NOT_INVOKED
      A priced line charges for `--selftest` (or another named flag) while the
      registered `launch_cmd` never passes that flag. A selftest pass belongs
      to the AUTHORING/FREEZE item and is costed there.

  DEVELOPMENT_MULTIPLIER_PRICED
      A priced line carries a development multiplier (a "x3", "3x" or
      "development multiplier" factor). A multiplier prices REPEATED authoring
      runs. A single graded invocation cannot perform repeated authoring runs,
      so a multiplier in a graded-run budget is a finding regardless of what
      the `launch_cmd` says.

REFUSAL DISCIPLINE
------------------
The guard and the refusal are carried by `sys.exit(2)`, NEVER by `assert`
(L-332 / D476 section 31.3: asserts vanish under `python3 -O`). This file is
green under BOTH `python3` and `python3 -O`, and its `--selftest` drives a
PLANTED FAILURE: it proves the refusal FIRES on known-bad input, rather than
proving only that the check passes on good input.

USAGE
-----
    check_cost_basis_mode_match.py --prereg PREREG.md --queue ENTRY.json
    check_cost_basis_mode_match.py --selftest

EXIT CODES
----------
    0   no finding (or selftest green)
    2   REFUSAL: a priced mode is not invoked by the launch_cmd
    3   usage / unreadable input (a refusal too: the check could not be made)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

VERSION = "1.0"

# A cost unit token, for discriminating a PRICED line from PROSE that merely
# mentions a mode. Prose mentioning `--selftest` is not a budget line-item and
# firing on it would make the check useless.
COST_UNIT = re.compile(
    r"core[-\s]?min(?:ute)?s?\b|\bcore[-\s]?h(?:our)?s?\b", re.I)

# A number that could be a budget quantity, inside a markdown table cell.
TABLE_NUMBER = re.compile(r"\|[^|]*?(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])[^|]*\|")

# A named invocable mode: a long flag. `--selftest` is the one this lab prices
# most often, but the detector is general over long flags.
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]{2,})")

MULTIPLIER = re.compile(
    r"development\s+multiplier"
    r"|(?<![\w.])[x×]\s?(\d+(?:\.\d+)?)\s*(?:development|dev)\b"
    r"|(?<![\w.])(\d+(?:\.\d+)?)\s?[x×]\s*(?:development|dev)\b",
    re.I)


def refuse(msg):
    """The single refusal path. Never an assert (L-332)."""
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def _is_priced_line(line):
    """A line is PRICED if it is a budget line-item, not prose.

    Two independent forms qualify, and prose qualifies under neither:
      (a) a markdown table row carrying a bare number in a cell, or
      (b) any line carrying an explicit cost unit (core-min / core-hours).
    """
    stripped = line.strip()
    if stripped.startswith("|") and TABLE_NUMBER.search(stripped):
        return True
    if COST_UNIT.search(stripped):
        return True
    return False


def parse_priced_modes(text):
    """Return the modes a cost section PRICES, with the line that prices them.

    Returns a list of dicts: {kind, token, lineno, line}.
    """
    found = []
    for i, line in enumerate(text.splitlines(), start=1):
        if not _is_priced_line(line):
            continue
        for m in MULTIPLIER.finditer(line):
            found.append(dict(kind="multiplier", token=m.group(0).strip(),
                              lineno=i, line=line.strip()))
            break
        for m in FLAG.finditer(line):
            found.append(dict(kind="flag", token=m.group(1),
                              lineno=i, line=line.strip()))
    return found


def parse_launch_cmd(path):
    """Read the registered launch_cmd from a queue entry.

    Accepts a JSON queue entry carrying `launch_cmd` (at top level or nested
    one level down), or a plain-text file holding the command itself.
    """
    try:
        raw = open(path, errors="replace").read()
    except OSError as exc:
        sys.stderr.write("REFUSED: cannot read queue entry %s: %s\n"
                         % (path, exc))
        sys.exit(3)
    try:
        obj = json.loads(raw)
    except ValueError:
        return raw
    if isinstance(obj, dict):
        if isinstance(obj.get("launch_cmd"), str):
            return obj["launch_cmd"]
        if isinstance(obj.get("launch_cmd"), list):
            return " ".join(str(x) for x in obj["launch_cmd"])
        for v in obj.values():
            if isinstance(v, dict) and isinstance(v.get("launch_cmd"), str):
                return v["launch_cmd"]
    sys.stderr.write(
        "REFUSED: queue entry %s carries no `launch_cmd` — the check cannot "
        "be made, and a check that cannot be made is not a pass.\n" % path)
    sys.exit(3)


def evaluate(prereg_text, launch_cmd):
    """Return the findings. Empty list means the cost basis matches the run."""
    findings = []
    invoked = set(FLAG.findall(launch_cmd or ""))
    for mode in parse_priced_modes(prereg_text):
        if mode["kind"] == "multiplier":
            findings.append(dict(
                code="DEVELOPMENT_MULTIPLIER_PRICED",
                token=mode["token"], lineno=mode["lineno"], line=mode["line"],
                why="a multiplier prices REPEATED authoring runs; a single "
                    "graded invocation cannot perform them, so this cost "
                    "belongs to the authoring/freeze item"))
        elif mode["token"] not in invoked:
            findings.append(dict(
                code="SELFTEST_NOT_INVOKED" if mode["token"] == "--selftest"
                     else "MODE_NOT_INVOKED",
                token=mode["token"], lineno=mode["lineno"], line=mode["line"],
                why="priced in the cost basis but absent from the registered "
                    "launch_cmd — the graded run will never perform it"))
    return findings


def report(findings, prereg, queue, launch_cmd):
    print("check_cost_basis_mode_match v%s" % VERSION)
    print("  pre-registration : %s" % prereg)
    print("  queue entry      : %s" % queue)
    print("  launch_cmd       : %s" % (launch_cmd or "").strip()[:200])
    if not findings:
        print("\nVERDICT: no finding — every priced mode is invoked by the "
              "registered launch_cmd.")
        return
    print("\n%d FINDING(S):" % len(findings))
    for f in findings:
        print("  [%s] %s  (line %d)" % (f["code"], f["token"], f["lineno"]))
        print("      %s" % f["line"][:200])
        print("      %s" % f["why"])
    print("\nCANNOT SEE: which of the document's tables is the BUDGET table. "
          "This is a WARN-level screen over every priced-looking line, so a "
          "MEASURED-outcome row that names a mode alongside a number is "
          "reported too. Findings are READ, not counted: check each cited "
          "line is a cost line-item before acting on it. Nor can it see "
          "whether a launch_cmd's script invokes the mode internally.")


# ---------------------------------------------------------------------------
# PLANTED-FAILURE SELFTEST
#
# The weak test is one that shows the check passes on good input. What matters
# is whether the REFUSAL FIRES on input known to be bad. Every BAD fixture
# below is driven through the real entry point as a subprocess and is required
# to exit 2; every GOOD fixture is required to exit 0. The PLANT case takes a
# firing fixture and mutates the one byte the detector claims to read, and is
# required to STOP firing — proving the detector reads what it says it reads.
# ---------------------------------------------------------------------------

FIXTURES = [
    # name, expect_rc, prereg text, launch_cmd
    ("GOOD-selftest-priced-and-invoked", 0,
     "| `--selftest` x2, startup | | | **60** |\n",
     "python3 grade_x.py --selftest --case /runs/x"),

    ("GOOD-no-mode-priced", 0,
     "| solver, 3 ranks | | | **420** |\n\n**REGISTERED ESTIMATE: 21.0 core-minutes.**\n",
     "python3 grade_x.py --case /runs/x"),

    ("GOOD-prose-mention-is-not-a-priced-line", 0,
     "`--selftest` runs both directions and exits 0 only if every one of the\n"
     "22 named limbs reddens. It refuses (`sys.exit(2)`), never warns.\n",
     "python3 grade_x.py --case /runs/x"),

    # RC2's shape: 60 s charged for two --selftest passes the launch_cmd
    # does not invoke. MUST FIRE.
    ("BAD-rc2-selftest-priced-not-invoked", 2,
     "| `--selftest` x2 (`python3`, `python3 -O`), report and JSON "
     "assembly, startup | | | **60** |\n"
     "**REGISTERED ESTIMATE: 4.0 core-minutes.**\n",
     "python3 regrade_rc2.py --regrade --out REGRADE_RC2.json"),

    # A'/R4b-Ib's shape: a x3 development multiplier inside the budget.
    # MUST FIRE, whatever the launch_cmd says.
    ("BAD-r4b-development-multiplier-priced", 2,
     "| clean pass 3.16 + x3 development multiplier (9.48) + slack 2.52 "
     "core-min |\n**REGISTERED ESTIMATE: 12.0 core-minutes.**\n",
     "python3 grade_r4b_ib.py --birth-only"),

    ("BAD-other-mode-priced-not-invoked", 2,
     "| `--d4-control` sweep | | | **45** |\n",
     "python3 grade_r4b_ib.py --birth-only"),

    # THE PLANT: BAD-rc2 with the launch_cmd mutated to actually invoke the
    # priced mode. The detector must STOP firing. If this still fires, the
    # check is not reading the launch_cmd at all and every red above is
    # worthless.
    ("PLANT-same-prereg-but-mode-now-invoked", 0,
     "| `--selftest` x2 (`python3`, `python3 -O`), report and JSON "
     "assembly, startup | | | **60** |\n"
     "**REGISTERED ESTIMATE: 4.0 core-minutes.**\n",
     "python3 regrade_rc2.py --selftest --regrade --out REGRADE_RC2.json"),
]


def selftest():
    opt = "ON" if sys.flags.optimize else "off"
    print("check_cost_basis_mode_match v%s — PLANTED-FAILURE SELFTEST" % VERSION)
    print("python3 -O optimization: %s (sys.flags.optimize=%d)\n"
          % (opt, sys.flags.optimize))

    me = os.path.abspath(__file__)
    cmd0 = [sys.executable]
    if sys.flags.optimize:
        cmd0 += ["-O"] * sys.flags.optimize

    fired = 0
    clean = 0
    failures = []
    with tempfile.TemporaryDirectory() as td:
        for name, expect_rc, prereg_text, launch in FIXTURES:
            p = os.path.join(td, name + ".md")
            q = os.path.join(td, name + ".json")
            open(p, "w").write(prereg_text)
            json.dump(dict(case_id=name, launch_cmd=launch), open(q, "w"))
            proc = subprocess.run(
                cmd0 + [me, "--prereg", p, "--queue", q],
                capture_output=True, text=True)
            got = proc.returncode
            ok = (got == expect_rc)
            verb = "FIRED" if got == 2 else ("clean" if got == 0 else
                                             "rc=%d" % got)
            print("  %-46s expect rc=%d  got rc=%d  %-5s  %s"
                  % (name, expect_rc, got, verb, "OK" if ok else "**MISMATCH**"))
            if not ok:
                failures.append((name, expect_rc, got, proc.stdout, proc.stderr))
            elif expect_rc == 2:
                fired += 1
            else:
                clean += 1

    # A refusal-bearing selftest that never drove a refusal is not evidence.
    n_bad = sum(1 for f in FIXTURES if f[1] == 2)
    print("\n  refusals driven and observed : %d of %d bad fixtures" % (fired, n_bad))
    print("  clean passes observed        : %d of %d good fixtures"
          % (clean, len(FIXTURES) - n_bad))

    if failures:
        print("\nSELFTEST FAILED — %d fixture(s) did not behave as registered:"
              % len(failures))
        for name, exp, got, out, err in failures:
            print("  %s: expected rc=%d, got rc=%d" % (name, exp, got))
            if err.strip():
                print("    stderr: %s" % err.strip()[:300])
        sys.exit(2)

    if fired == 0:
        sys.stderr.write(
            "REFUSED: the selftest completed without driving a single "
            "refusal. A check not shown able to fire is not evidence.\n")
        sys.exit(2)

    print("\nSELFTEST GREEN: %d/%d fixtures behaved as registered, and the "
          "refusal was DRIVEN AND OBSERVED %d times (not merely absent)."
          % (len(FIXTURES), len(FIXTURES), fired))
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Refuse when a pre-registration's cost basis prices a "
                    "mode the registered launch_cmd does not invoke (L-520).")
    ap.add_argument("--prereg", help="pre-registration markdown file")
    ap.add_argument("--queue", help="queue entry (JSON with launch_cmd)")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted failures and prove the refusal fires")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not args.prereg or not args.queue:
        sys.stderr.write("REFUSED: --prereg and --queue are both required "
                         "(or use --selftest).\n")
        sys.exit(3)

    try:
        prereg_text = open(args.prereg, errors="replace").read()
    except OSError as exc:
        sys.stderr.write("REFUSED: cannot read pre-registration %s: %s\n"
                         % (args.prereg, exc))
        sys.exit(3)

    launch_cmd = parse_launch_cmd(args.queue)
    findings = evaluate(prereg_text, launch_cmd)
    report(findings, args.prereg, args.queue, launch_cmd)

    if findings:
        refuse("%d priced mode(s) are not invoked by the registered "
               "launch_cmd. Budget the post-freeze GRADED invocation, and "
               "only that." % len(findings))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
