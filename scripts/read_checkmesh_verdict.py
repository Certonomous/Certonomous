#!/usr/bin/env python3
"""
read_checkmesh_verdict.py -- the lab's ONE reader of a `checkMesh` verdict.

THE DEFECT IT EXISTS FOR.  `checkMesh`'s exit status is unreliable in BOTH
directions, measured on at least three independent case families on this box:

  * rc = 0 while the mesh FAILS checks.  Measured 2026-09-11 by a cfd lab-lane on
    the SUBOFF R1b triple: plain `checkMesh` printed "Mesh OK." with rc = 0 at all
    three levels, while `checkMesh -allGeometry -allTopology` on the SAME meshes
    printed "Failed 1 mesh checks." / "Failed 2 mesh checks." / "Failed 2 mesh
    checks." -- also with rc = 0.
  * rc = 0 on a mesh printing "Failed 7 mesh checks"
    (verification/runs/CRM_M085_runs/L1T/log.checkMesh_POSTSCALE).

So: THE PRINTED LINE IS THE VERDICT AND THE rc IS NEVER CONSULTED.

AND THE THIRD FAILURE MODE, which is why this refuses rather than defaults: a
reader that finds NEITHER line must not report "no failures".  An absent verdict
is not a passing verdict.  `read_verdict` raises; the CLI exits 2.

PLANTED CONTROL (CLAUDE.md rule 3).  --selftest feeds the reader a known-FAILING
log, a known-PASSING log, a log with NEITHER line, and a plain-flag log, and
REQUIRES it to tell them apart.  The control is executable, not a comment claiming
it was tested.  Run it on any edit to this file.

ZERO `assert` (L-332).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)
import os, re, json, argparse

FAILED_RE = re.compile(r"^Failed\s+(\d+)\s+mesh\s+checks\.\s*$", re.M)
OK_RE     = re.compile(r"^Mesh OK\.\s*$", re.M)
STAR_RE   = re.compile(r"^\s*\*\*\*(.+?)\s*$", re.M)
FLAG_GEO  = "-allGeometry"
FLAG_TOP  = "-allTopology"
DIM_RE    = re.compile(r"^\s*Mesh has (\d+) geometric \(non-empty/wedge\) directions", re.M)


class VerdictAbsent(Exception):
    """Neither 'Failed N mesh checks.' nor 'Mesh OK.' is present."""


def read_verdict(text, require_full_flags=True):
    """Return the verdict dict.  RAISES VerdictAbsent if the log carries no
    verdict line at all -- never returns a pass by default."""
    m_fail, m_ok = FAILED_RE.search(text), OK_RE.search(text)
    if m_fail is None and m_ok is None:
        raise VerdictAbsent("no 'Failed N mesh checks.' and no 'Mesh OK.' line")
    if m_fail is not None:
        n_failed, verdict = int(m_fail.group(1)), "FAILED"
    else:
        n_failed, verdict = 0, "OK"
    exec_line = ""
    for ln in text.splitlines():
        if ln.startswith("Exec   :"):
            exec_line = ln
            break
    full = (FLAG_GEO in exec_line) and (FLAG_TOP in exec_line)
    dim = DIM_RE.search(text)
    out = {
        "verdict": verdict,
        "n_failed_checks": n_failed,
        "failing_checks": [s.strip() for s in STAR_RE.findall(text)],
        "full_flags_present": full,
        "exec_line": exec_line,
        "geometric_directions": int(dim.group(1)) if dim else None,
        "rc_CONSULTED": False,
        "NOTE": "The exit status of checkMesh was NOT consulted. It is unreliable "
                "in both directions; the printed verdict line is the verdict.",
    }
    if require_full_flags and not full:
        out["verdict"] = "BLOCKED"
        out["BLOCKED_because"] = (
            "the log's Exec line does not carry both -allGeometry and -allTopology. "
            "Plain checkMesh printed 'Mesh OK.' with rc=0 on SUBOFF R1b meshes that "
            "the full flag set failed. A plain-flag log cannot admit a mesh.")
    return out


# ----------------------------- planted control --------------------------------
_L_FAIL = """Exec   : checkMesh -allGeometry -allTopology
    cells:            89784
    Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)
    Mesh has 3 solution (non-empty) directions (1 1 1)
 ***Cells with small determinant (< 0.001) found, number of cells: 3240
 ***Faces with small volume ratio (< 0.01) found, number of faces: 1
Failed 2 mesh checks.
End
"""
_L_OK = """Exec   : checkMesh -allGeometry -allTopology
    cells:            12345
    Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)
Mesh OK.
End
"""
_L_PLAIN_OK = """Exec   : checkMesh
    cells:            89784
Mesh OK.
End
"""
_L_NOVERDICT = """Exec   : checkMesh -allGeometry -allTopology
    cells:            89784
Segmentation fault
"""


def selftest():
    fails = []

    def chk(name, cond, got):
        if not cond:
            fails.append(f"{name}: got {got!r}")

    v = read_verdict(_L_FAIL)
    chk("known-FAILING log reads FAILED", v["verdict"] == "FAILED", v["verdict"])
    chk("known-FAILING log counts 2", v["n_failed_checks"] == 2, v["n_failed_checks"])
    chk("known-FAILING log lists both starred checks",
        len(v["failing_checks"]) == 2, v["failing_checks"])
    chk("dimensionality read from the GEOMETRIC line, not the solution line",
        v["geometric_directions"] == 2, v["geometric_directions"])

    v = read_verdict(_L_OK)
    chk("known-PASSING log reads OK", v["verdict"] == "OK", v["verdict"])
    chk("known-PASSING log counts 0", v["n_failed_checks"] == 0, v["n_failed_checks"])

    chk("the two are DISTINGUISHED",
        read_verdict(_L_FAIL)["verdict"] != read_verdict(_L_OK)["verdict"], "same")

    v = read_verdict(_L_PLAIN_OK)
    chk("a PLAIN-flag 'Mesh OK.' is BLOCKED, never OK", v["verdict"] == "BLOCKED",
        v["verdict"])
    v = read_verdict(_L_PLAIN_OK, require_full_flags=False)
    chk("...and reads OK only when full flags are explicitly not required",
        v["verdict"] == "OK", v["verdict"])

    try:
        read_verdict(_L_NOVERDICT)
        fails.append("a log with NO verdict line did not raise")
    except VerdictAbsent:
        pass

    chk("rc is never consulted", read_verdict(_L_FAIL)["rc_CONSULTED"] is False, True)

    if fails:
        for f in fails:
            sys.stderr.write(f"SELFTEST FAIL: {f}\n")
        sys.stderr.write(f"SELFTEST: {len(fails)} failure(s).\n")
        return 2
    print("SELFTEST PASS: 9/9 controls fired. The reader distinguishes a known-"
          "failing log from a known-passing one, BLOCKS a plain-flag pass, and "
          "REFUSES a log with no verdict line.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?", help="path to a checkMesh log")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--allow-plain", action="store_true",
                    help="do not BLOCK a log lacking -allGeometry/-allTopology")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.log:
        sys.stderr.write("REFUSED: give a log path or --selftest.\n"); sys.exit(2)
    if not os.path.isfile(a.log):
        sys.stderr.write(f"REFUSED: {a.log} is not a file.\n"); sys.exit(2)
    try:
        v = read_verdict(open(a.log, errors="replace").read(),
                         require_full_flags=not a.allow_plain)
    except VerdictAbsent as e:
        sys.stderr.write(f"REFUSED: {a.log} carries no checkMesh verdict ({e}). "
                         "An absent verdict is NOT a passing verdict.\n")
        sys.exit(2)
    if a.json:
        print(json.dumps(v, indent=2))
    else:
        print(f"{a.log}")
        print(f"  VERDICT           {v['verdict']}   ({v['n_failed_checks']} failed checks)")
        print(f"  full flags        {v['full_flags_present']}")
        print(f"  geometric dirs    {v['geometric_directions']}")
        for c in v["failing_checks"]:
            print(f"  FAILED            {c}")
        if "BLOCKED_because" in v:
            print(f"  BLOCKED because   {v['BLOCKED_because']}")
        print(f"  rc consulted      {v['rc_CONSULTED']}")
    sys.exit(0 if v["verdict"] == "OK" else 1)


if __name__ == "__main__":
    main()
