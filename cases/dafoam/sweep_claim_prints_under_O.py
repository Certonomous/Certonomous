#!/usr/bin/env python3
"""L-332 sweep: UNCONDITIONAL SUCCESS CLAIM-PRINTS in dafoam instruments.

THE SECOND HAZARD, and it is not the assert hazard restated
(SUPERVISOR_ASSERT_UNDER_O_RULING.md Amendment 1, commit 40ff9578):

  - the ASSERT hazard fails SILENTLY  -- a vacuous battery still printing its
    count.  It leaves NO evidence.
  - the CLAIM-PRINT hazard fails LOUDLY AND FALSELY -- an intact battery
    printing a success it never earned.  It leaves COUNTERFEIT evidence,
    which is worse.

L-332, adopted verbatim: never put an unconditional success `print` after a
check -- print INSIDE the passing branch, so removing the check removes the
claim.

=========================================================================
THIS SCANNER IS BUILT AGAINST THE SUPERVISOR'S OWN SCANNER'S THREE FALSE
POSITIVES on d7_g8_token.py (Amendment 1 A1.2).  Those were:
  1. a TALLY  `units=%d passed=%d failed=%d` + `return 0 if ... else 3`
     -> a count, not a claim
  2. a TERNARY `"ok    " if ok else "FAILED"`
     -> the claim IS conditional; their scanner tracked If/Try but NOT IfExp
  3. a VALUE REPORT `D7_G8_EVALUATED pass=%s`
     -> prints the VALUE, so it says pass=False on failure
So this scanner:
  * walks IfExp (and the ternary's orelse) explicitly,
  * flags value-formatting adjacent to a success token,
  * flags tally shape,
and REPORTS THE FLAGS RATHER THAN A VERDICT.  A crude detector's
"unconditional" is not evidence: EVERY HIT IS READ BY A HUMAN-EQUIVALENT
READER BEFORE IT IS REPORTED, and the read is the authority.
=========================================================================
"""
import ast
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"

SUCCESS = ("PASS", "PASSED", " OK", "OK ", "OK:", "SUCCESS", "REACHED",
           "VERIFIED", "CLEARED", "CLEAN", "FIRED", "SEEN", "MATCH",
           "CONFIRMED", "REACHABLE", "GRANTED", "SATISFIED")
FAILURE = ("FAIL", "FAILED", "REFUS", "ERROR", "MISMATCH", "ABORT", "NOT ",
           "BLOCKED", "WRONG", "MISSING", "false", "False")


def blob(path):
    r = subprocess.run(["git", "show", "HEAD:%s" % path], cwd=REPO,
                       capture_output=True, text=True)
    return None if r.returncode != 0 else r.stdout


def strings_in(node):
    """Every string constant anywhere under `node`, INCLUDING inside an IfExp
    (the ternary the supervisor's scanner could not see) and an f-string."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out


def has_ifexp(node):
    return any(isinstance(n, ast.IfExp) for n in ast.walk(node))


def has_value_format(node):
    """A %s / {} / f-string interpolation -- the shape of a VALUE REPORT
    (`pass=%s`), which says pass=False on failure and is NOT a claim."""
    for n in ast.walk(node):
        if isinstance(n, ast.JoinedStr):
            return True
    for s in strings_in(node):
        if "%s" in s or "%r" in s or "{}" in s:
            return True
    return False


def tally_shape(node):
    """A COUNT, not a claim: reports a failure count or an n/m ratio."""
    for s in strings_in(node):
        low = s.lower()
        if "failed=" in low or "fail=" in low or "n_fail" in low:
            return True
        if s.count("%d") >= 2 or s.count("%s") >= 2:
            return True
    return False


class Scan(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path
        self.guard_depth = 0     # If / Try / ExceptHandler nesting
        self.hits = []

    def _guarded(self, node):
        self.guard_depth += 1
        self.generic_visit(node)
        self.guard_depth -= 1

    visit_If = _guarded
    visit_Try = _guarded
    visit_ExceptHandler = _guarded

    def visit_Call(self, node):
        f = node.func
        name = getattr(f, "id", None) or getattr(f, "attr", None)
        if name in ("print", "write", "_p"):
            ss = strings_in(node)
            joined = " ".join(ss)
            up = joined.upper()
            if any(t in up for t in SUCCESS):
                self.hits.append({
                    "line": node.lineno,
                    "guarded": self.guard_depth > 0,
                    "ternary": has_ifexp(node),
                    "value_fmt": has_value_format(node),
                    "tally": tally_shape(node),
                    "has_fail_word": any(t.upper() in up for t in FAILURE),
                    "text": (joined[:110]).replace("\n", " "),
                })
        self.generic_visit(node)


def main():
    # ---- L-325 BOTH DIRECTIONS, on THIS scanner -----------------------
    # positive: d7_g8_token.py MUST yield the three sites the supervisor's
    # scanner flagged -- if this scanner cannot even see them, its zeros are
    # worthless.  negative: an absent path must REFUSE, never read as zero.
    P = "cases/dafoam/ladder-a/A3/curriculum_D7/d7_g8_token.py"
    t = blob(P)
    if t is None:
        print("REFUSED: positive plant %s is ABSENT" % P)
        sys.exit(2)
    s = Scan(P)
    s.visit(ast.parse(t))
    if len(s.hits) < 3:
        print("REFUSED: positive plant returned %d claim-print sites, "
              "expected >=3 (the supervisor's scanner found 3). This scanner "
              "cannot see what a cruder one could; its zeros are not evidence."
              % len(s.hits))
        sys.exit(2)
    print("CONTROL+ %s -> %d claim-print sites (>=3 required)" % (P, len(s.hits)))
    for n in ("cases/dafoam/NO_SUCH_FILE_xyz.py",):
        if blob(n) is not None:
            print("REFUSED: negative plant %s is not absent" % n)
            sys.exit(2)
        print("CONTROL- %s -> ABSENT (not a zero)" % n)
    print()

    paths = subprocess.run(["git", "ls-tree", "-r", "HEAD", "--name-only"],
                           cwd=REPO, capture_output=True,
                           text=True).stdout.split("\n")
    py = sorted(p for p in paths
                if p.endswith(".py")
                and (p.startswith("cases/dafoam/")
                     or p.startswith("docs/dafoam/")))
    print("population: %d tracked .py in dafoam folder scope" % len(py))

    n_sites = 0
    cands = []
    for p in py:
        t = blob(p)
        try:
            tree = ast.parse(t)
        except SyntaxError:
            continue
        s = Scan(p)
        s.visit(tree)
        for h in s.hits:
            n_sites += 1
            # A CANDIDATE is a success-token print that is NOT inside any
            # If/Try AND is not obviously a ternary / value report / tally.
            if (not h["guarded"] and not h["ternary"]
                    and not h["value_fmt"] and not h["tally"]):
                h["path"] = p
                cands.append(h)

    print("success-token print sites total : %d" % n_sites)
    print("after excluding guarded / ternary / value-report / tally shapes")
    print("CANDIDATES REQUIRING A READ     : %d" % len(cands))
    print()
    for h in sorted(cands, key=lambda x: (x["path"], x["line"])):
        print("  %s:%d" % (h["path"], h["line"]))
        print("      %s" % h["text"])
    print()
    print("NOTE: a candidate is NOT a defect. Each is read in the record; the "
          "read is the authority, not this count.")


if __name__ == "__main__":
    main()
