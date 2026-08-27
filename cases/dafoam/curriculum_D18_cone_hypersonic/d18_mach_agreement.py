#!/usr/bin/env python3
"""G-MACH -- D18's ONE REGISTERED DELTA IS CARRIED BY TWO FILES, AND THEY MUST AGREE.

WHY THIS GATE EXISTS, stated as a defect that has not happened yet rather than one that has.
The Cone_Supersonic tutorial holds the freestream in TWO independent places:

  * `0.orig/include/freestreamConditions` -- `U (1736.0 0 0); p 101325.0; T 300.0;`
    THE SOLVER READS ITS ACTUAL BOUNDARY CONDITION FROM HERE.  The `primalBC` block in
    runScript.py that would override it IS COMMENTED OUT IN THE TUTORIAL.
  * `runScript.py` -- `U0`, `p0`, `T0`, used ONLY for `scale = 1/(0.5*U0^2*A0*rho0)` on CD
    and CL, and for `normalizeStates`.  IT DOES NOT MOVE THE FLOW.

So a change to the producer alone RESCALES THE OBJECTIVE WITHOUT MOVING THE FLOW, and a
change to the BC file alone MOVES THE FLOW AND NORMALISES IT BY THE WRONG DYNAMIC PRESSURE.
Either produces a plausible CD that is silently wrong by the square of a ratio, with every
other check in this family passing: rc 0, an End line, the age guard, the cell count, the
FD plateau -- ALL OF THEM WOULD PASS.  Nothing else in this instrument set can see it.
That is exactly the shape D5-LAUNCHER-DEF-1 and W3-LAUNCHER-DEF-1 took: one quantity,
two spellings, no gate across them.

REFUSES (exit 2) rather than degrading.  A value it cannot read is a refusal, never a pass.
"""
import argparse, json, math, os, re, sys

U0_REGISTERED = 1736.0      # D18 sec.2, the ONE registered delta (D17: 680.0)
P0_REGISTERED = 101325.0    # unchanged from the tutorial and from D17
T0_REGISTERED = 300.0       # unchanged from the tutorial and from D17
GAMMA, RGAS = 1.4, 287.0
TOL = 0.0                   # EXACT equality: these are typed constants, not measurements


class MachRefusal(Exception):
    pass


def read_bc(path):
    """freestreamConditions -> (Ux, p, T).  Refuses on anything it cannot parse."""
    if not os.path.isfile(path):
        raise MachRefusal("G-MACH: freestreamConditions absent at %s" % path)
    txt = open(path, errors="replace").read()
    mU = re.search(r"^\s*U\s+\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)\s*;", txt, re.M)
    mp = re.search(r"^\s*p\s+([0-9.eE+-]+)\s*;", txt, re.M)
    mT = re.search(r"^\s*T\s+([0-9.eE+-]+)\s*;", txt, re.M)
    if not (mU and mp and mT):
        raise MachRefusal("G-MACH: could not parse U, p and T from %s -- a value this gate "
                          "cannot read is a REFUSAL, never a pass" % path)
    uy, uz = float(mU.group(2)), float(mU.group(3))
    if uy != 0.0 or uz != 0.0:
        raise MachRefusal("G-MACH: freestream U has non-zero y/z components (%r, %r). This item "
                          "registers aoa 0 and a y-symmetric wedge; a cross-flow component would "
                          "break the CL symmetry reading silently." % (uy, uz))
    return float(mU.group(1)), float(mp.group(1)), float(mT.group(1))


def read_producer(path):
    """runScript.py -> (U0, p0, T0).  Each must appear EXACTLY ONCE as a top-level assignment."""
    if not os.path.isfile(path):
        raise MachRefusal("G-MACH: producer absent at %s" % path)
    txt = open(path, errors="replace").read()
    out = []
    for name in ("U0", "p0", "T0"):
        hits = re.findall(r"^%s\s*=\s*([0-9.eE+-]+)\s*$" % name, txt, re.M)
        if len(hits) != 1:
            raise MachRefusal("G-MACH: producer %s carries %d top-level `%s =` assignment(s), "
                              "expected exactly 1: %r. Two spellings of one quantity is the "
                              "defect this gate exists to catch." % (path, len(hits), name, hits))
        out.append(float(hits[0]))
    return tuple(out)


def check(bc_path, producer_path):
    bU, bp, bT = read_bc(bc_path)
    pU, pp, pT = read_producer(producer_path)
    bad = []
    for nm, b, p, reg in (("U0", bU, pU, U0_REGISTERED),
                          ("p0", bp, pp, P0_REGISTERED),
                          ("T0", bT, pT, T0_REGISTERED)):
        if abs(b - p) > TOL:
            bad.append("%s DISAGREES between the two files: freestreamConditions=%r producer=%r"
                       % (nm, b, p))
        elif abs(b - reg) > TOL:
            bad.append("%s AGREES between the files (%r) but is NOT the registered %r -- both "
                       "files were changed together to a value this item did not register"
                       % (nm, b, reg))
    if bad:
        raise MachRefusal("G-MACH REFUSES: " + "; ".join(bad))
    a = math.sqrt(GAMMA * RGAS * bT)
    return {"gate": "G-MACH", "ok": True, "U0": bU, "p0": bp, "T0": bT,
            "a_m_s": round(a, 4), "mach": round(bU / a, 4),
            "registered_U0": U0_REGISTERED,
            "note": "the BC file and the producer agree AND carry the registered value; "
                    "the solver's flow and the objective's normalisation are the same freestream"}


def selftest(tmpdir):
    """PLANTED-FAILURE PROOFS (Sanaa's standing directives sec.1, L-314). Zero compute.
    Every leg PLANTS a condition and DRIVES the gate. No `assert` is used: `-O` strips those."""
    import tempfile, shutil
    n = 0; bad = []

    def unit(name, cond):
        nonlocal n
        n += 1
        print("  [%s] %s" % ("OK " if cond else "BAD", name))
        if not cond:
            bad.append(name)

    d = tempfile.mkdtemp(dir=tmpdir)
    BC = ("U             (%s 0 0);\np             %s;\nT             %s;\n#inputMode    merge\n")
    PR = ("import x\nU0 = %s\np0 = %s\nT0 = %s\nrho0 = p0 / 287.0 / T0\nA0 = 0.1\n")

    def write(u_bc, p_bc, t_bc, u_pr, p_pr, t_pr, bc_text=None, pr_text=None):
        b = os.path.join(d, "fs_%d" % n); r = os.path.join(d, "rs_%d.py" % n)
        open(b, "w").write(bc_text if bc_text is not None else BC % (u_bc, p_bc, t_bc))
        open(r, "w").write(pr_text if pr_text is not None else PR % (u_pr, p_pr, t_pr))
        return b, r

    def drive(*a, **kw):
        b, r = write(*a, **kw)
        try:
            return True, check(b, r)
        except MachRefusal as e:
            return False, str(e)

    # (1) POSITIVE CONTROL FIRST -- a gate that refuses everything is not a gate.
    ok, res = drive(1736.0, 101325.0, 300.0, 1736.0, 101325.0, 300.0)
    unit("(1) both files carry the REGISTERED 1736.0/101325.0/300.0 -> PASS, M=%s"
         % (res.get("mach") if ok else "?"),
         ok and res["mach"] == 5.0002 and res["U0"] == 1736.0)

    # (2) THE DEFECT THIS GATE EXISTS FOR: the producer alone left at D17's value.
    ok, m = drive(1736.0, 101325.0, 300.0, 680.0, 101325.0, 300.0)
    unit("(2) PLANTED producer still at D17's 680.0, BC at 1736.0 -> REFUSED "
         "(the objective would be normalised by the wrong q and every other check would pass)",
         (not ok) and "U0 DISAGREES" in m)

    # (3) The mirror image: the BC alone left behind.
    ok, m = drive(680.0, 101325.0, 300.0, 1736.0, 101325.0, 300.0)
    unit("(3) PLANTED BC still at D17's 680.0, producer at 1736.0 -> REFUSED "
         "(the flow would never leave D17's Mach)", (not ok) and "U0 DISAGREES" in m)

    # (4) BOTH moved together, to a value this item did not register. Agreement is NOT enough.
    ok, m = drive(2000.0, 101325.0, 300.0, 2000.0, 101325.0, 300.0)
    unit("(4) PLANTED both files agreeing on an UNREGISTERED 2000.0 -> REFUSED. Agreement "
         "between two files is not agreement with the registration",
         (not ok) and "NOT the registered" in m)

    # (5)/(6) p0 and T0 carry the same coupling (rho0 and the speed of sound).
    ok, m = drive(1736.0, 90000.0, 300.0, 1736.0, 101325.0, 300.0)
    unit("(5) PLANTED p0 disagreeing -> REFUSED (rho0 and hence the CD scale)",
         (not ok) and "p0 DISAGREES" in m)
    ok, m = drive(1736.0, 101325.0, 250.0, 1736.0, 101325.0, 300.0)
    unit("(6) PLANTED T0 disagreeing -> REFUSED (the speed of sound, hence the Mach)",
         (not ok) and "T0 DISAGREES" in m)

    # (7) A cross-flow component would break the CL symmetry reading silently.
    ok, m = drive(0, 0, 0, 1736.0, 101325.0, 300.0,
                  bc_text="U             (1736.0 5.0 0);\np             101325.0;\nT             300.0;\n")
    unit("(7) PLANTED non-zero freestream v -> REFUSED (aoa 0 and the CL symmetry reading)",
         (not ok) and "non-zero y/z" in m)

    # (8) TWO spellings of U0 in the producer -- the exact shape the gate is named for.
    ok, m = drive(0, 0, 0, 0, 0, 0,
                  bc_text=BC % (1736.0, 101325.0, 300.0),
                  pr_text="U0 = 1736.0\np0 = 101325.0\nT0 = 300.0\nU0 = 680.0\n")
    unit("(8) PLANTED the producer carrying TWO top-level `U0 =` lines -> REFUSED rather than "
         "taking one of them", (not ok) and "assignment(s), expected exactly 1" in m)

    # (9)/(10) A value the gate cannot read is a refusal, never a pass.
    ok, m = drive(0, 0, 0, 1736.0, 101325.0, 300.0, bc_text="nothing parseable here\n")
    unit("(9) PLANTED unparseable BC file -> REFUSED, not passed", (not ok) and "could not parse" in m)
    b, r = write(1736.0, 101325.0, 300.0, 1736.0, 101325.0, 300.0)
    os.unlink(b)
    try:
        check(b, r); ok = True; m = ""
    except MachRefusal as e:
        ok = False; m = str(e)
    unit("(10) PLANTED absent BC file -> REFUSED, not passed", (not ok) and "absent" in m)

    shutil.rmtree(d, ignore_errors=True)
    print("G-MACH SELFTEST units=%d failures=%d python_O=%s" % (n, len(bad), not __debug__))
    if n != 10 or bad:
        print("G-MACH SELFTEST FAIL: %s" % (bad or "unit count %d != 10" % n))
        return 2
    print("G-MACH SELFTEST PASS 10/10")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bc", default=None)
    ap.add_argument("--producer", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.tmpdir)
    if not (a.bc and a.producer):
        print("usage: d18_mach_agreement.py --bc <freestreamConditions> --producer <runScript.py>")
        return 3
    try:
        print(json.dumps(check(a.bc, a.producer)))
        return 0
    except MachRefusal as e:
        print(json.dumps({"gate": "G-MACH", "ok": False, "refusal": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
