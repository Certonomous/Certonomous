#!/usr/bin/env python3
"""assert_t5f_setup.py -- read the BUILT dictionaries on disk and assert that
every registered value of T5f_PREREGISTRATION.md sections 3.1/3.2/3.3 is
actually there, per level and per region.

WHY THIS FILE EXISTS SEPARATELY FROM THE BUILDER.  A builder that applies a
change and reads its own write back proves the write landed.  It does not prove
the BUILT CASE as a whole is the registered case -- the builder could be right
about the five items it touched and wrong about the twelve it inherited.  This
file never patches anything.  It opens the dictionaries the solver will open and
compares them against the frozen document.

NOTHING HERE HOLDS A COPY.  Every expected value comes from
`build_t5f.parse_registration()`, i.e. from the frozen registration at run time.
The board's standing finding (T26 S19/S20) is that an instrument holding its own
COPY of a registered quantity IS the defect; the fix is to stop copying.  The
quantities that could NOT be parsed out of the frozen document are named in
`build_t5f.py`'s header (C1 the six wall patch NAMES -- read from the built mesh;
C2 the frozen recipe's own case names) and two more are named here:

  C3  THE REFINEMENT RATIO CONVENTION.  Section 3.1 registers `air r32 = 1.5929,
      r21 = 1.6060` but does not state which index is the fine grid.  The
      measured counts settle it and this file does not guess: it computes BOTH
      candidate assignments from the built meshes and requires the registered
      pair to match one of them, naming which.  Roache's convention (1 = fine)
      is what the numbers turn out to carry.

  C4  THE COMPARISON TOLERANCE on those ratios.  The registration prints four
      decimals and does not register a tolerance.  This file uses 1.5e-4 and
      PRINTS the residual for every ratio, so a reader sees the margin rather
      than taking the word PASS.

Usage:  assert_t5f_setup.py --level c|m|f          one level
        assert_t5f_setup.py --ladder               all three + the triple ratios
        assert_t5f_setup.py --selftest             plant one deviation per check
Exit 0 all asserted, 2 any failure or refusal.  Zero `assert` statements.
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t5f as B  # noqa: E402

RATIO_TOL = 1.5e-4          # C4, stated rather than hidden


class Fail(Exception):
    pass


def read(case, *parts):
    p = os.path.join(case, *parts)
    if not os.path.isfile(p):
        raise Fail("%s is not on disk" % p)
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def one(pattern, text, what, flags=0):
    m = re.findall(pattern, text, flags)
    if len(m) != 1:
        raise Fail("%s: pattern %r matched %d times, expected 1" % (what, pattern, len(m)))
    return m[0]


def n_cells(case, region):
    txt = read(case, "constant", region, "polyMesh", "owner")
    return int(one(r"nCells:\s*(\d+)", txt[:4000], "%s nCells" % region))


def checks_for_level(case, level, reg):
    """Yield (name, expected, found, ok) -- every one read off the built disk."""
    out = []

    def chk(name, expected, found, ok=None):
        out.append((name, expected, found, (expected == found) if ok is None else ok))

    # ---- the age-guard precondition (rule 4) ------------------------------
    chk("0.orig present (arming source)", True, os.path.isdir(os.path.join(case, "0.orig")))
    stale = [d for d in os.listdir(case) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d)]
    chk("no 0/ and no time directory (unarmed, unrun)", [], sorted(stale))
    chk("no log.solve (unrun)", False, os.path.exists(os.path.join(case, "log.solve")))

    # ---- S1 : the two registered divergence schemes -----------------------
    sch = read(case, "system", "air", "fvSchemes")
    for key in reg["s1_keys"]:
        v = one(r"^[ \t]*%s[ \t]+(.*?);[ \t]*$" % re.escape(key), sch,
                "air fvSchemes %s" % key, re.M)
        chk("S1 air fvSchemes %s" % key, reg["s1_new"], v)
    chk("S1 the old scheme family is gone from the k/omega lines",
        0, len(re.findall(r"^[ \t]*div\(phi,(?:k|omega)\).*%s" % re.escape(reg["s1_old_family"]),
                          sch, re.M)))

    # ---- S2 : k on every wall of the BUILT mesh (C1) -----------------------
    walls = B.wall_patches(case, "air", reg["n_walls"])
    kf = read(case, "0.orig", "air", "k")
    for w in walls:
        blk = one(r"^ {4}%s\n {4}\{\n(.*?)^ {4}\}" % re.escape(w), kf,
                  "0.orig/air/k patch %s" % w, re.M | re.S)
        t = one(r"^\s*type\s+(\S+);", blk, "type of k on %s" % w, re.M)
        chk("S2 0.orig/air/k wall %-12s type" % w, reg["s2_new"], t)
    chk("S2 wall patches found in the built mesh", reg["n_walls"], len(walls))
    chk("S2 no wall keeps the registered OLD BC (%s)" % reg["s2_old"],
        0, sum(1 for w in walls
               if re.search(r"^ {4}%s\n {4}\{\n {8}type %s;"
                            % (re.escape(w), re.escape(reg["s2_old"].split()[0])),
                            kf, re.M)))

    # ---- S3 / 3.3 : the internal fields -----------------------------------
    om = one(r"^internalField[ \t]+uniform[ \t]+(\S+);", read(case, "0.orig", "air", "omega"),
             "0.orig/air/omega internalField", re.M)
    chk("S3 omega internalField (numeric)", float(reg["omega_internal"]), float(om))
    kk = one(r"^internalField[ \t]+uniform[ \t]+(\S+);", kf,
             "0.orig/air/k internalField", re.M)
    chk("3.3 k internalField (numeric)", float(reg["k_internal"]), float(kk))

    # ---- S4 : the relaxation factors --------------------------------------
    sol = read(case, "system", "air", "fvSolution")
    eqs = one(r"equations\s*\{([^{}]*)\}", sol, "air relaxationFactors/equations")
    for name, want in sorted(reg["s4_new"].items()):
        v = one(r"\b%s\s+([0-9.]+)\s*;" % re.escape(name), eqs,
                "%s relaxation factor" % name)
        chk("S4 %s relaxation factor" % name, want, float(v))

    # ---- S5 : UNCHANGED, and checked BECAUSE it is unchanged --------------
    for region in ("air", "epoxy"):
        v = int(one(r"%s\s+(\d+);" % re.escape(reg["s5_key"]),
                    read(case, "system", region, "fvSolution"),
                    "%s %s" % (region, reg["s5_key"])))
        chk("S5 %s %s" % (region, reg["s5_key"]), reg["s5_value"], v)

    # ---- 3.3 : solver, endTime, model, Prt, interface scheme, ranks -------
    cd = read(case, "system", "controlDict")
    chk("3.3 controlDict application", reg["solver"],
        one(r"^application\s+(\S+);", cd, "application", re.M))
    chk("3.3 controlDict endTime", reg["end_time"],
        int(one(r"^endTime\s+(\d+);", cd, "endTime", re.M)))
    tp = read(case, "constant", "air", "turbulenceProperties")
    chk("3.3 RASModel", reg["ras_model"], one(r"RASModel\s+(\S+);", tp, "RASModel"))
    chk("3.3 Prt", reg["prt"], float(one(r"Prt\s+([0-9.]+)\s*;", tp, "Prt")))
    ep = read(case, "system", "epoxy", "fvSchemes")
    for k in ("laplacian(alpha,e)", "laplacian(alpha,h)"):
        v = one(r"%s\s+Gauss\s+(\S+)\s+corrected;" % re.escape(k), ep, k)
        chk("3.3 epoxy %s interface scheme" % k, reg["interface_scheme"], v)
    chk("3.3 ranks (decomposeParDict)", reg["ranks"],
        int(one(r"numberOfSubdomains\s+(\d+);", read(case, "system", "decomposeParDict"),
                "numberOfSubdomains")))

    # ---- 3.1 : the mesh this rung inherits unchanged -----------------------
    for region in ("air", "epoxy"):
        chk("3.1 %s cell count" % region, reg["cells"][region][level], n_cells(case, region))

    # ---- the T5b inheritance the y+ clause depends on ---------------------
    chk("T5b repair: no `writeTime` control survives", 0, cd.count("writeTime"))
    chk("T5b repair: exactly two repaired function objects", 2,
        cd.count("executeControl  timeStep;"))
    return out


def ladder_ratios(reg, cases):
    """C3: compute BOTH index conventions and require the registered pair to
    match one of them.  Returns rows (region, key, registered, measured, resid, ok)."""
    rows, convention = [], None
    counts = {r: {L: n_cells(cases[L], r) for L in "cmf"} for r in ("air", "epoxy")}
    cand = {}
    for r in ("air", "epoxy"):
        n = counts[r]
        cand[r] = {
            "1=fine (Roache)": {"r21": (n["f"] / n["m"]) ** (1 / 3.0),
                                "r32": (n["m"] / n["c"]) ** (1 / 3.0)},
            "1=coarse": {"r21": (n["m"] / n["c"]) ** (1 / 3.0),
                         "r32": (n["f"] / n["m"]) ** (1 / 3.0)},
        }
    for name in ("1=fine (Roache)", "1=coarse"):
        if all(abs(cand[r][name][k] - reg["ratios"][r][k]) <= RATIO_TOL
               for r in ("air", "epoxy") for k in ("r21", "r32")):
            convention = name
            break
    for r in ("air", "epoxy"):
        for k in ("r32", "r21"):
            reg_v = reg["ratios"][r][k]
            meas = cand[r][convention or "1=fine (Roache)"][k]
            rows.append((r, k, reg_v, meas, meas - reg_v, abs(meas - reg_v) <= RATIO_TOL))
    return convention, counts, rows


def run(levels, reg, quiet=False):
    fails = []
    cases = {}
    for L in levels:
        case = os.path.join(HERE, reg["cases"][L])
        if not os.path.isdir(case):
            fails.append("level %s: %s is not built" % (L, case))
            continue
        cases[L] = case
        if not quiet:
            print("\n=== LEVEL %s : %s ===" % (L, os.path.basename(case)))
        try:
            rows = checks_for_level(case, L, reg)
        except Fail as exc:
            fails.append("level %s: %s" % (L, exc))
            if not quiet:
                print("  REFUSED  %s" % exc)
            continue
        for name, exp, got, ok in rows:
            if not quiet:
                print("  %-8s %-46s registered=%-26s on disk=%s"
                      % ("ok" if ok else "FAIL", name, exp, got))
            if not ok:
                fails.append("level %s: %s: registered %r, on disk %r" % (L, name, exp, got))
    if len(cases) == 3:
        conv, counts, rows = ladder_ratios(reg, cases)
        if not quiet:
            print("\n=== THE TRIPLE (section 3.1) ===")
            print("  index convention that reproduces the registered pair: %s"
                  % (conv or "NONE -- neither convention matches"))
        if conv is None:
            fails.append("neither index convention reproduces the registered ratios")
        for r, k, reg_v, meas, resid, ok in rows:
            if not quiet:
                print("  %-8s %-5s %-4s registered=%.4f  measured=%.7f  resid=%+.2e  (tol %.1e)"
                      % ("ok" if ok else "FAIL", r, k, reg_v, meas, resid, RATIO_TOL))
            if not ok:
                fails.append("%s %s: registered %.4f, measured %.7f" % (r, k, reg_v, meas))
    if not quiet:
        print("\nSETUP ASSERTION %s (%d failed)"
              % ("PASS" if not fails else "FAIL", len(fails)))
        for f in fails:
            print("  FAILED: %s" % f)
    return fails


# =========================================================================
# --selftest : plant ONE deviation per check family into a COPY of a built
# case and require the assertion to fire.  A check that cannot be made to
# fail is not a check.
# =========================================================================
PLANTS = [
    ("S1 scheme", "system/air/fvSchemes",
     "div(phi,k)      bounded Gauss limitedLinear 1;",
     "div(phi,k)      bounded Gauss linearUpwind grad(k);"),
    ("S2 wall type", "0.orig/air/k", "type kLowReWallFunction;", "type fixedValue;"),
    ("S3 omega internalField", "0.orig/air/omega",
     "internalField uniform 1.0e+04;", "internalField uniform 55.9957;"),
    ("k internalField", "0.orig/air/k",
     "internalField uniform 0.0119885;", "internalField uniform 0.02;"),
    ("S4 relaxation", "system/air/fvSolution", "k 0.3; omega 0.3;", "k 0.5; omega 0.5;"),
    ("S5 correctors", "system/epoxy/fvSolution",
     "nNonOrthogonalCorrectors 0;", "nNonOrthogonalCorrectors 2;"),
    ("endTime", "system/controlDict", "endTime         5000;", "endTime         4000;"),
    ("RASModel", "constant/air/turbulenceProperties", "RASModel kOmegaSST;", "RASModel kEpsilon;"),
    ("Prt", "constant/air/turbulenceProperties", "Prt 0.85;", "Prt 0.5;"),
    ("interface scheme", "system/epoxy/fvSchemes", "Gauss harmonic corrected", "Gauss linear corrected"),
    ("ranks", "system/decomposeParDict", "numberOfSubdomains 1;", "numberOfSubdomains 4;"),
    ("T5b repair", "system/controlDict", "writeControl    timeStep;", "writeControl    writeTime;"),
]


def selftest(reg):
    import tempfile
    built = [L for L in "cmf" if os.path.isdir(os.path.join(HERE, reg["cases"][L]))]
    if not built:
        B.refuse("--selftest needs at least one BUILT level to plant into; none exists")
    L = built[0]
    src = os.path.join(HERE, reg["cases"][L])
    print("assert_t5f_setup.py --selftest  (planting into a COPY of level %s)" % L)
    fails = []
    tmp = tempfile.mkdtemp(prefix="t5f_assert_st_")
    try:
        # the UNPLANTED control must PASS -- a planted arm proves nothing if the
        # clean copy also fails.
        ctl = os.path.join(tmp, "ctl", reg["cases"][L])
        os.makedirs(os.path.dirname(ctl))
        shutil.copytree(src, ctl)
        r = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                            "--drive-one", ctl, "--level", L],
                           capture_output=True, text=True)
        print("  %-6s the UNPLANTED control copy passes (rc %d)"
              % ("ok" if r.returncode == 0 else "FAIL", r.returncode))
        if r.returncode != 0:
            fails.append("control copy failed: %s" % r.stdout[-400:])
        for i, (name, rel, old, new) in enumerate(PLANTS):
            d = os.path.join(tmp, "p%d" % i, reg["cases"][L])
            os.makedirs(os.path.dirname(d))
            shutil.copytree(src, d)
            p = os.path.join(d, rel)
            with open(p) as fh:
                txt = fh.read()
            if old not in txt:
                print("  FAIL   plant %-24s -- the text to plant into is ABSENT "
                      "from %s (an arm that could never fire)" % (name, rel))
                fails.append("plant %s: anchor absent in %s" % (name, rel))
                continue
            with open(p, "w") as fh:
                fh.write(txt.replace(old, new, 1))
            r = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                                "--drive-one", d, "--level", L],
                               capture_output=True, text=True)
            ok = r.returncode == 2
            print("  %-6s plant %-24s -> assertion %s"
                  % ("ok" if ok else "FAIL", name,
                     "FIRES (exit 2)" if ok else "DID NOT FIRE (rc %d)" % r.returncode))
            if not ok:
                fails.append("plant %s did not fire" % name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ASSERTION SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", choices=["c", "m", "f"])
    ap.add_argument("--ladder", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--drive-one", help="internal: assert one case directory by path")
    a = ap.parse_args()
    reg = B.parse_registration()
    if a.selftest:
        return selftest(reg)
    if a.drive_one:
        try:
            rows = checks_for_level(a.drive_one, a.level, reg)
        except Fail as exc:
            sys.stdout.write("REFUSED: %s\n" % exc)
            return 2
        bad = [r for r in rows if not r[3]]
        for name, exp, got, _ in bad:
            sys.stdout.write("FAILED %s: registered %r, on disk %r\n" % (name, exp, got))
        return 2 if bad else 0
    levels = ["c", "m", "f"] if a.ladder else ([a.level] if a.level else None)
    if not levels:
        B.refuse("--level, --ladder or --selftest is required")
    return 2 if run(levels, reg) else 0


if __name__ == "__main__":
    sys.exit(main())
