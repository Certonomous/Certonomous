#!/usr/bin/env python3
"""F26D -- build ONE arm x ONE level of the discriminating arm.

Registered by PREREGISTRATION_F26D_2026-08-27.md. THIS IS A DIAGNOSTIC, NOT A
LADDER: nothing built here is an F26 ladder level and nothing here rescopes or
unblocks F26_RINGLEB, which stays BLOCKED.

It is a THIN WRAPPER over build_f26.py and deliberately reimplements none of it:
the mesher, the exact-field writer, the geometry cross-check, the checkMesh
gates and the 0/U-written-last age-guard datum are build_f26's and stay
build_f26's. A wrapper that copied them would drift from the thing it copied.

THE ONE CHANGE PER ARM (Sanaa section 3), and nothing else moves:
  A0  reference: band k = [0.5, 0.8],           mu = 0
  AV  A0 with THE ONE CHANGE  mu 0 -> 1e-3      (band identical to A0)
  AM  A0 with THE ONE CHANGE  band -> [0.277154, 0.35]   (mu identical to A0)

The band is applied by rebinding exact_f26's module-level PSI_MIN/PSI_MAX, which
exact_f26.lattice() reads AT CALL TIME -- verified by the selftest, which builds a
lattice under a patched band and requires the corner coordinates to move. mu is
applied by rewriting `mu 0` in the DESTINATION's constant/thermophysicalProperties
AFTER build_f26 has run, so build_f26's own molWeight/Cp validation is untouched.

Zero `assert` (L-332); refuses under `python3 -O` at entry.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: build_f26d.py must not run under `python3 -O`.\n")
    sys.exit(2)

import os
import re
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f26 as EX          # noqa: E402
import build_f26 as B           # noqa: E402

# Registered in the pre-registration section 3. Not tunable at the command line:
# a band a caller can move is not a registered band.
ARMS = {
    "A0": dict(k_min=0.500000, k_max=0.800000, mu=0.0),
    "AV": dict(k_min=0.500000, k_max=0.800000, mu=1e-3),
    "AM": dict(k_min=0.277154, k_max=0.350000, mu=0.0),
}
LEVELS = {"L1": (24, 4), "L2": (48, 8), "L3": (96, 16), "L4": (192, 32)}
ITERATIONS = 4000
WRITE_EVERY = 200


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f26d): %s\n" % msg)
    sys.exit(rc)


def apply_band(k_min, k_max):
    """Rebind the band exact_f26.lattice() reads. PSI_MIN/PSI_MAX are precomputed
    at import, so rebinding K_MIN/K_MAX alone would silently do nothing -- the
    selftest plants exactly that mistake and requires it to be caught."""
    EX.K_MIN, EX.K_MAX = k_min, k_max
    EX.PSI_MIN, EX.PSI_MAX = 1.0 / k_max, 1.0 / k_min


def set_mu(dest, mu):
    path = os.path.join(dest, "constant", "thermophysicalProperties")
    txt = open(path).read()
    new, n = re.subn(r"mu\s+[0-9eE.+-]+;", "mu %g;" % mu, txt)
    if n != 1:
        die("thermophysicalProperties: expected exactly one `mu <value>;`, found %d" % n)
    open(path, "w").write(new)
    back = re.search(r"mu\s+([0-9eE.+-]+);", open(path).read())
    if back is None or float(back.group(1)) != mu:
        die("mu did not read back as %g from %s" % (mu, path))
    return float(back.group(1))


def build(arm, level, dest):
    if arm not in ARMS:
        die("unknown arm %r; registered arms are %s" % (arm, sorted(ARMS)))
    if level not in LEVELS:
        die("unknown level %r; registered levels are %s" % (level, sorted(LEVELS)))
    spec = ARMS[arm]
    na, nc = LEVELS[level]
    apply_band(spec["k_min"], spec["k_max"])
    rc = B.main([dest, "--scratch", str(na), str(nc),
                 "--steps", str(ITERATIONS), "--write-every", str(WRITE_EVERY)])
    if rc != 0:
        die("build_f26 returned %d for %s/%s" % (rc, arm, level), rc=rc)
    mu = set_mu(dest, spec["mu"])
    print("F26D built arm %s level %s (%dx%d) at %s: band k=[%.6f, %.6f], mu=%g"
          % (arm, level, na, nc, dest, spec["k_min"], spec["k_max"], mu))
    return 0


def selftest():
    problems, lines = [], []
    import ast
    src = open(os.path.abspath(__file__)).read()
    n = sum(1 for x in ast.walk(ast.parse(src)) if isinstance(x, ast.Assert))
    if n:
        problems.append("B1 FAILED: %d assert node(s); -O deletes them (L-332)." % n)
    else:
        lines.append("B1: zero `assert` nodes in this builder (L-332).")

    # B2 -- the band rebinding actually moves the mesh. Planted: rebind ONLY
    # K_MIN/K_MAX (the mistake apply_band exists to prevent) and require the
    # lattice NOT to move; then rebind properly and require it to move.
    k0 = EX.lattice(4, 2)
    EX.K_MIN, EX.K_MAX = 0.277154, 0.350000          # the incomplete rebinding
    k_bad = EX.lattice(4, 2)
    moved_bad = float(abs(k_bad["X"] - k0["X"]).max())
    apply_band(0.277154, 0.350000)                    # the correct rebinding
    k_good = EX.lattice(4, 2)
    moved_good = float(abs(k_good["X"] - k0["X"]).max())
    apply_band(0.500000, 0.800000)                    # restore the reference band
    k_back = EX.lattice(4, 2)
    if moved_bad != 0.0:
        problems.append("B2 FAILED: rebinding K_MIN/K_MAX alone moved the lattice by %g; "
                        "the control's premise is wrong." % moved_bad)
    elif moved_good <= 0.0:
        problems.append("B2 FAILED: apply_band() did NOT move the lattice, so every arm "
                        "would silently build the SAME geometry and AM would be A0.")
    elif float(abs(k_back["X"] - k0["X"]).max()) != 0.0:
        problems.append("B2 FAILED: the reference band was not restored.")
    else:
        lines.append("B2 CONTROL FIRED: rebinding K_MIN/K_MAX alone moves the lattice by "
                     "0 (the planted mistake), apply_band() moves it by %.4f, and the "
                     "reference band restores exactly. AM is a different geometry from A0 "
                     "and is shown to be." % moved_good)

    # B3 -- the registered design numbers are what this file will actually build.
    for arm, want_m in (("A0", 0.8567), ("AM", 0.3544)):
        s = ARMS[arm]
        apply_band(s["k_min"], s["k_max"])
        lat = EX.lattice(400, 8)
        got = float(EX.mach_of(lat["V"]).max())
        if abs(got - want_m) > 5e-3:
            problems.append("B3 FAILED: arm %s max Mach is %.4f, pre-registration section 3 "
                            "registered %.4f." % (arm, got, want_m))
        else:
            lines.append("B3: arm %s max Mach %.4f matches the registered %.4f." % (arm, got, want_m))
    apply_band(0.500000, 0.800000)

    for l in lines:
        print("  " + l)
    if problems:
        print("")
        for p in problems:
            print("  " + p)
        print("\nBUILDER SELFTEST FAILED: %d control(s) did not behave." % len(problems))
        return 2
    print("\nBUILDER SELFTEST PASS: %d controls fired, each shown able to fail." % len(lines))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="Build one F26D arm x level. Diagnostic, not a ladder.")
    ap.add_argument("dest", nargs="?")
    ap.add_argument("--arm")
    ap.add_argument("--level")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.dest and a.arm and a.level):
        ap.error("give <dest> --arm <A0|AV|AM> --level <L1..L4>, or --selftest")
    return build(a.arm, a.level, os.path.abspath(a.dest))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
