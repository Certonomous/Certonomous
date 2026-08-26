#!/usr/bin/env python3
"""D14-M G14-0 -- THE NAMED CONTAMINANT CHECK.  A REFUSING GATE THAT RUNS FIRST.

cases/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md measured that this lab's pyHyp
extrusion lets the MAXIMUM cell aspect ratio worsen under a refinement in which the
RESOLUTION parameters change while pyHyp's SMOOTHING parameters (epsE, epsI, theta,
volCoef, volBlend, volSmoothIter) are left unscaled (97.87 -> 167.50 on the airfoil
generator).  D14-M regenerates the MACH wing mesh with the same tool, so that finding
is a contaminant of this item BY NAME, and its check runs BEFORE any container starts.

WHAT IT REFUSES (exit 2, nothing launched):
  * the staged generator's md5 is not the registered md5 of the generator that made
    D4's baseline mesh (dab5e959187ab2e2bfb4e2c0ded0feb6);
  * any RESOLUTION parameter (N, s0, marchDist, cMax) differs from the registered value;
  * any SMOOTHING key is ACTIVE (uncommented) -- the registered generator leaves all six
    at pyHyp's defaults, and activating one while resolution is fixed, or refining the
    resolution while they stay fixed, is exactly the finding's recipe.
The check reads the generator FILE that will run, not a copy of the registered values;
`--plant` drives it against a copy whose s0 is halved and whose N is doubled (the
finding's own recipe) and REFUSES if the reader does not see the change.  A gate never
shown able to refuse is ceremony (CLAUDE.md rule 3).  No `assert` (L-332): every
refusal is a sys.exit(2), and this file counts its own ast.Assert nodes.
"""
import ast
import hashlib
import json
import os
import re
import sys
import tempfile

REGISTERED_MD5 = "dab5e959187ab2e2bfb4e2c0ded0feb6"
REGISTERED_RESOLUTION = {"N": 39, "s0": 1.0e-3, "marchDist": 300.0, "cMax": 0.1}
SMOOTHING_KEYS = ("epsE", "epsI", "theta", "volCoef", "volBlend", "volSmoothIter")


def count_asserts(path):
    tree = ast.parse(open(path).read())
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


def read_generator(path):
    """Values as the file that will run declares them.  Active keys are lines whose first
    non-space character is a quote; commented keys are lines starting with '#'."""
    txt = open(path).read()
    found, active_smoothing = {}, {}
    for line in txt.splitlines():
        s = line.strip()
        m = re.match(r'^"(\w+)"\s*:\s*([-+0-9.eE]+)\s*,', s)
        if m:
            k, v = m.group(1), m.group(2)
            if k in REGISTERED_RESOLUTION:
                found[k] = float(v)
            if k in SMOOTHING_KEYS:
                active_smoothing[k] = float(v)
    md5 = hashlib.md5(txt.encode()).hexdigest()
    return md5, found, active_smoothing


def check(path):
    md5, found, active = read_generator(path)
    reasons = []
    if md5 != REGISTERED_MD5:
        reasons.append("generator md5 %s != registered %s" % (md5, REGISTERED_MD5))
    for k, v in REGISTERED_RESOLUTION.items():
        if k not in found:
            reasons.append("resolution parameter %s not found in the generator" % k)
        elif abs(found[k] - v) > 1e-12 * max(1.0, abs(v)):
            reasons.append("resolution parameter %s = %r differs from registered %r" % (k, found[k], v))
    for k, v in active.items():
        reasons.append("smoothing key %s is ACTIVE at %r; registered generator leaves it at pyHyp's default" % (k, v))
    report = {"gate": "G14-0", "generator": path, "md5": md5, "resolution_read": found,
              "smoothing_active": active, "reasons": reasons,
              "verdict": "PASS" if not reasons else "REFUSED"}
    return report


def plant(path):
    """The finding's recipe: refine s0 and N, leave smoothing alone."""
    txt = open(path).read()
    t2 = txt.replace('"N": 39,', '"N": 78,').replace('"s0": 1.0e-3,', '"s0": 5.0e-4,')
    if t2 == txt:
        return None
    fd, p = tempfile.mkstemp(prefix="d14m_plant_", suffix=".py")
    os.write(fd, t2.encode()); os.close(fd)
    return p


def main():
    if len(sys.argv) < 2:
        print("usage: d14m_contaminant_check.py <genWingMesh.py> [--plant] [--json OUT]", file=sys.stderr)
        return 64
    path = sys.argv[1]
    n_assert = count_asserts(os.path.abspath(__file__))
    if n_assert != 0:
        print("REFUSAL: this file carries %d assert statement(s); a refusal written as an assert is deleted by -O (L-332)" % n_assert)
        return 2
    if "--plant" in sys.argv:
        # the reader must see a planted departure, and must still pass the untouched file
        clean = check(path)
        p = plant(path)
        if p is None:
            print("REFUSAL: planted control could not be built -- the registered N/s0 lines were not found in %s" % path)
            return 2
        planted = check(p)
        os.unlink(p)
        seen = [r for r in planted["reasons"] if r.startswith("resolution parameter")]
        ok = clean["verdict"] == "PASS" and planted["verdict"] == "REFUSED" and len(seen) >= 2
        print(json.dumps({"planted_control": {"clean": clean["verdict"], "planted": planted["verdict"],
                                              "planted_reasons": planted["reasons"], "ok": ok}}, indent=1))
        if not ok:
            print("REFUSAL: the planted control did not fire as registered (clean=%s planted=%s)" % (clean["verdict"], planted["verdict"]))
            return 2
        print("G14-0 PLANTED CONTROL FIRED: clean generator PASS, planted refinement REFUSED with %d resolution reasons" % len(seen))
        return 0
    rep = check(path)
    rep["ast_assert_count"] = n_assert
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        with open(out, "w") as f:
            json.dump(rep, f, indent=1)
    print(json.dumps(rep, indent=1))
    if rep["verdict"] != "PASS":
        print("G14-0 REFUSED: the generator is not the registered one, or its resolution/smoothing departs from registration. NOTHING LAUNCHED.")
        return 2
    print("G14-0 PASS: generator md5 %s, N=%g s0=%g marchDist=%g cMax=%g, smoothing at defaults" % (
        rep["md5"], rep["resolution_read"]["N"], rep["resolution_read"]["s0"], rep["resolution_read"]["marchDist"], rep["resolution_read"]["cMax"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
