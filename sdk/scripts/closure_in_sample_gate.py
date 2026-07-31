#!/usr/bin/env python3
"""In-sample gate: nothing this lab fits, inverts or calibrates on may be a
scored case of the closure challenge.

    python3 sdk/scripts/closure_in_sample_gate.py [--quiet]

WHY THIS EXISTS
---------------
`NASA_2DWMH` is one of the benchmark's eight scored test cases. Inverting a
correction field against its experimental Cf is legitimate field inversion and
the lab is capable of it; it is also in-sample by construction, and a benchmark
score obtained that way is not a generalization result. The benchmark's README
is blunter than that: training or validating on a test case gets the submission
withdrawn and a note put on the leaderboard.

That route was not caught by a rule. It was caught by a leakage aside in
`demo-output/website/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md` section 7,
written by whoever happened to be holding the file. This script is that aside
turned into an assertion, and it follows the pattern
`sdk/scripts/closure_baseline_error_gate.py` already set: the scored-case list
is never retyped, it is derived, cross-checked against the benchmark's own
README, and asserted before anything else runs.

WHAT IT CHECKS
--------------
1. The scored-case inventory agrees between two independent sources: the
   benchmark clone's README split table (the primary artifact) and this repo's
   round-1 case lists. A disagreement is fatal on its own -- a gate whose
   definition of "scored" has drifted guards nothing.
2. Every structured declaration of a training / fitting / inversion /
   calibration set in the repo is disjoint from that inventory.
3. Every prose record that says it trained or inverted on something is read for
   scored case names.

TWO SEVERITIES, AND WHY THEY ARE TUNED THAT WAY
-----------------------------------------------
A false positive costs a reviewer one minute. A false negative ships a
withdrawn submission. So:

* FAIL   -- a scored case name is a whole string value under a declaration key
            or in a declared case-list variable. That is a case list, and a
            scored case is in it.
* REVIEW -- a scored case name appears inside longer text under such a key, or
            in a prose line that says trained/inverted/fitted on. Expected
            false positives: a leakage statement saying a case was NOT used
            reads the same way to a regex. Reported, never silently dropped.

Exit code is 1 if anything FAILs, if the inventory disagrees, or if the
inventory could not be cross-checked against the benchmark.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

_SDK_SCRIPTS = Path(__file__).resolve().parent
_REPO = _SDK_SCRIPTS.parents[1]

_DEFAULT_BENCHMARK_DIR = Path.home() / "closure-challenge-benchmark"
BENCHMARK_DIR = Path(os.environ.get("CLOSURE_BENCHMARK_DIR",
                                    str(_DEFAULT_BENCHMARK_DIR)))

# A flow whose Test column is a bare check mark names its whole directory.
# Verified against the clone's data/ listing at import time, not assumed.
_FLOW_DIR = {
    "PHLL29": "Parm_PH_29",
    "DUCT": "DUCT",
    "CBFS13700": "CBFS",
    "NASAHUMP": "NASA_2DWMH",
    "PHLL10595": "PH_Breuer",
}

# Keys and variable names that declare what a model was fitted on.
_FIT_VERB = re.compile(r"train|fit|invert|inversion|calibrat|tune", re.I)
# ... minus the ones that carry a fit verb but hold a SCORE, not a case list.
# "trained_entry_per_case" is the benchmark's own per-case result table: it
# names all eight scored cases and is supposed to. A gate that cannot tell a
# score table from a training set fires on every honest submission record and
# is then switched off, which is the failure mode this is guarding against.
_NOT_A_CASE_LIST = re.compile(
    r"per_case|score|result|entry|mae|error|pooled|overall|_r2|slope|"
    r"threshold|flag|disjoint|leakage|conclusion|impact|median|_cv\b|"
    r"divergence|n_train|range", re.I)


def _DECLARES(name: str):
    """True when a key or variable name declares a set of cases fitted on."""
    return bool(_FIT_VERB.search(name)) and not _NOT_A_CASE_LIST.search(name)

# Prose that says a thing was fitted on something.
_PROSE_VERB = re.compile(
    r"\b(train(?:ed|ing)?|fit(?:ted|ting)?|invert(?:ed|ing)?|inversion|"
    r"calibrat(?:ed|ing|ion))\b", re.I)

_SCAN_JSON_ROOTS = ("demo-output/website", "models")
_SCAN_PY_ROOTS = ("sdk/scripts", "sdk/workflows", "scripts")
_SCAN_MD_ROOTS = ("demo-output/website", "docs")

_SKIP_DIR_PARTS = {"__pycache__", ".git", "node_modules", "solve_registry",
                   "mega-batch", "work"}


# --------------------------------------------------------------------------
# 1. The scored-case inventory, derived twice and cross-checked.
# --------------------------------------------------------------------------
def scored_from_benchmark_readme(benchmark_dir: Path) -> set[str]:
    """Parse the README's own train/validation/test table.

    This is the primary artifact: the rule the steward enforces is written
    there, and the test column of that table is what "scored" means.
    """
    readme = benchmark_dir / "README.md"
    text = readme.read_text(encoding="utf-8")
    scored: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        flow = cells[0].replace("*", "").strip()
        test_cell = cells[3]
        if flow in ("Flow", "-", ""):
            continue
        named = re.findall(r"`([A-Za-z0-9_]+)`", test_cell)
        if named:
            scored.update(named)
        elif test_cell.strip() in ("✓", "✔"):
            directory = _FLOW_DIR.get(flow)
            if directory is None:
                raise SystemExit(
                    f"README names a check-marked test flow this script does "
                    f"not know how to resolve to a case: {flow!r}")
            if not (benchmark_dir / "data" / directory).is_dir():
                raise SystemExit(
                    f"README maps {flow!r} to data/{directory}, which is not "
                    f"in the clone")
            scored.add(directory)
    if not scored:
        raise SystemExit(f"no test cases parsed out of {readme}")
    return scored


def scored_from_repo() -> set[str]:
    """The lab's own list, imported rather than copied.

    Round 1's script already carries executable assertions that its train,
    validation and test splits are disjoint and correctly sized; importing it
    inherits those instead of restating them.
    """
    if str(_SDK_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SDK_SCRIPTS))
    import train_closure_periodic_hill_correction as ph
    return set(ph._PH_TEST) | set(ph._OTHER_TEST_RANS)


# --------------------------------------------------------------------------
# 2. Structured declarations.
# --------------------------------------------------------------------------
def _walk_files(roots, suffix):
    for root in roots:
        base = _REPO / root
        if not base.exists():
            continue
        for path in sorted(base.rglob(f"*{suffix}")):
            if _SKIP_DIR_PARTS & set(path.relative_to(_REPO).parts[:-1]):
                continue
            yield path


def scan_json(scored: set[str]) -> tuple[list, list]:
    fails, reviews = [], []
    for path in _walk_files(_SCAN_JSON_ROOTS, ".json"):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rel = path.relative_to(_REPO)

        def visit(node, declaring: str | None, where: str) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    # A case can be named by a key as easily as by a value:
                    # {"train_cases": {"NASA_2DWMH": ...}} is a training set
                    # with a scored case in it.
                    if declaring and key.strip() in scored:
                        fails.append((str(rel), f"{where}/{key}", declaring,
                                      f"key {key.strip()}"))
                    nxt = key if _DECLARES(key) else declaring
                    visit(value, nxt, f"{where}/{key}")
            elif isinstance(node, list):
                for i, value in enumerate(node):
                    visit(value, declaring, f"{where}[{i}]")
            elif isinstance(node, str) and declaring:
                if node.strip() in scored:
                    fails.append((str(rel), where, declaring, node.strip()))
                else:
                    for case in sorted(scored):
                        if case in node:
                            reviews.append((str(rel), where, declaring,
                                            node.strip()[:160]))
                            break

        visit(doc, None, "")
    return fails, reviews


def scan_python(scored: set[str]) -> tuple[list, list]:
    fails, reviews = [], []
    for path in _walk_files(_SCAN_PY_ROOTS, ".py"):
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        rel = path.relative_to(_REPO)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            names += [t.attr for t in targets if isinstance(t, ast.Attribute)]
            declaring = next((n for n in names if _DECLARES(n)), None)
            if not declaring or node.value is None:
                continue
            for leaf in ast.walk(node.value):
                if isinstance(leaf, ast.Constant) and isinstance(leaf.value, str):
                    text = leaf.value.strip()
                    if text in scored:
                        fails.append((str(rel), f"line {leaf.lineno}",
                                      declaring, text))
                    else:
                        for case in sorted(scored):
                            if case in text:
                                reviews.append((str(rel), f"line {leaf.lineno}",
                                                declaring, text[:160]))
                                break
    return fails, reviews


def scan_prose(scored: set[str]) -> list:
    reviews = []
    for path in _walk_files(_SCAN_MD_ROOTS, ".md"):
        rel = path.relative_to(_REPO)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, start=1):
            if not _PROSE_VERB.search(line):
                continue
            for case in sorted(scored):
                if case in line:
                    reviews.append((str(rel), f"line {n}", case, line.strip()[:180]))
                    break
    return reviews


# --------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quiet", action="store_true",
                        help="print FAILs and counts only")
    args = parser.parse_args()

    repo_scored = scored_from_repo()
    verified = False
    if BENCHMARK_DIR.exists():
        readme_scored = scored_from_benchmark_readme(BENCHMARK_DIR)
        if readme_scored != repo_scored:
            print("FAIL  the scored-case inventory disagrees with the "
                  "benchmark's own README")
            print(f"      README only: {sorted(readme_scored - repo_scored)}")
            print(f"      repo only:   {sorted(repo_scored - readme_scored)}")
            return 1
        verified = True
    else:
        print(f"UNVERIFIED  benchmark clone not at {BENCHMARK_DIR}; the "
              f"scored-case list could not be checked against its README")

    scored = repo_scored
    print(f"scored cases ({len(scored)}, cross-checked against the benchmark "
          f"README: {verified}):")
    for case in sorted(scored):
        print(f"  {case}")

    json_fail, json_review = scan_json(scored)
    py_fail, py_review = scan_python(scored)
    prose_review = scan_prose(scored)
    fails = json_fail + py_fail

    print(f"\nFAIL   {len(fails)} declared training/inversion set(s) contain a "
          f"scored case")
    for rel, where, key, value in fails:
        print(f"  {rel}  {where}  (declared by {key!r})  -> {value}")

    reviews = json_review + py_review
    print(f"\nREVIEW {len(reviews)} structured declaration(s) mention a scored "
          f"case in longer text")
    if not args.quiet:
        for rel, where, key, value in reviews:
            print(f"  {rel}  {where}  (declared by {key!r})")
            print(f"      {value}")

    print(f"\nREVIEW {len(prose_review)} prose line(s) name a scored case "
          f"alongside a training or inversion verb")
    if not args.quiet:
        for rel, where, case, line in prose_review:
            print(f"  {rel}  {where}  [{case}]")
            print(f"      {line}")

    if fails:
        return 1
    if not verified:
        return 1
    print("\nPASS  no declared training, fitting, inversion or calibration set "
          "contains a scored case")
    return 0


if __name__ == "__main__":
    sys.exit(main())
