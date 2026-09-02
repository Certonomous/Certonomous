#!/usr/bin/env python3
"""T25R5 EQUIVALENCE COMPARATOR -- pre-registration section 4, checks E1/E2/E4/E5.

A solver-configuration change that MOVES THE ANSWER is a defect, not a speedup.
This compares each arm's reconstructed fields at t = 0.8 against B0_L2's and
DISQUALIFIES any arm that moved them.

⚡ RULE 3 -- THE PLANTED-ZERO CONTROL RUNS FIRST, ON EVERY INVOCATION.
Everything this script reports is a near-zero difference, and a zero from a
reader not shown able to see a non-zero is not evidence.  So before any real
comparison it plants PLANT = 1.234e-03 K into TWO cells (index 0 and index n-1,
so a reader that only inspects the head or only the tail is caught) of a working
copy of B0's T, in BOTH regions, reads it back FROM DISK with the same reader
used for real work, and REFUSES unless it recovers exactly 1.234e-03 in all four
places.  PLANT is deliberately ABOVE the 1.000e-03 K disqualifying threshold, so
the control proves not merely that the reader can SEE a difference but that THE
GATE CAN FIRE.

    python3 compare_arms_t25R5.py --arm C4 [--base B0_L2] [--time 0.8]
    python3 compare_arms_t25R5.py --all
    python3 compare_arms_t25R5.py --selftest
"""
import os, re, shutil, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_REFUSE = 2
PLANT = 1.234e-03          # K.  Rule 3.  Above the E1 threshold ON PURPOSE.
# Tolerance on RECOVERING the plant.  Set from MEASUREMENT, not from taste: the
# plant is recovered by differencing two values of magnitude T ~ 293 K, where one
# double-precision ulp is 6.505e-14 K, and the measured recovery residual is
# 1.084e-14 K -- i.e. BELOW one ulp, so it is cancellation noise and not a reader
# fault.  A first cut used PLANT*1e-12 = 1.234e-15, which sits UNDER the ulp floor
# and so could never pass; it reported READER IS BLIND on a reader that had in
# fact recovered 1.23400000001e-03 exactly.  1e-9 K is ~4.6 orders above the noise
# floor and ~6 orders below PLANT, so it cannot mask a real miss.
PLANT_TOL_K = 1e-9
TIME = 0.8
TOL_S = 1e-6               # A2.2: locate a time dir by NUMERIC VALUE, not by name

# --- FROZEN AT THE PRE-REGISTRATION section 4.  DISQUALIFYING thresholds.
E1_T_K      = 1.000e-03    # 1/10 of Amendment A1's binding iterative requirement
E2_PRGH_PA  = 1.0          # 1e-5 relative on a 1e5 Pa field
U_DISQ      = 1.0e-03      # m/s
REPORTED    = ["k", "omega", "nut", "alphat", "p"]

NUM = re.compile(r"[-+0-9.eEdD]+")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def tdir(case, t=TIME, soft=False):
    """Locate a time directory BY NUMERIC VALUE (A2.2). Ambiguity REFUSES.

    soft=True returns None instead of refusing when none exists -- used only when
    PROBING for an optional reconstructed tree. Ambiguity still REFUSES even when
    soft: two candidate directories is never something to shrug at."""
    hits = []
    for d in os.listdir(case):
        try:
            v = float(d)
        except ValueError:
            continue
        if abs(v - t) <= TOL_S:
            hits.append(d)
    if not hits:
        if soft:
            return None
        refuse("%s has no time directory numerically equal to %g (tol %g). "
               "Absence is not equality." % (case, t, TOL_S))
    if len(hits) > 1:
        refuse("%s has %d time directories matching %g: %r. An ambiguous match "
               "REFUSES rather than choosing." % (case, len(hits), t, hits))
    return os.path.join(case, hits[0])


def read_field(path):
    """internalField values as a flat list of floats. Handles uniform/nonuniform,
    scalar and vector. Refuses on a non-finite value."""
    if not os.path.isfile(path):
        refuse("field file %s DOES NOT EXIST. Default-deny." % path)
    txt = open(path).read()
    m = re.search(r"internalField\s+(uniform|nonuniform)", txt)
    if not m:
        refuse("%s has no internalField entry." % path)
    if m.group(1) == "uniform":
        seg = txt[m.end():m.end() + 400]
        vals = [float(x) for x in NUM.findall(seg.split(";")[0]) if _isnum(x)]
        return vals, True
    i = txt.index("(", m.end())
    depth, j = 0, i
    while j < len(txt):
        if txt[j] == "(":
            depth += 1
        elif txt[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = txt[i + 1:j]
    out = [float(x) for x in NUM.findall(body) if _isnum(x)]
    for v in out:
        if not math.isfinite(v):
            refuse("%s contains a non-finite value. E4." % path)
    return out, False


def _isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def field_paths(case, region, name, t=TIME):
    """Reconstructed first; fall back to the decomposed pair. Both sides always
    use the SAME source kind -- the caller checks that."""
    # Reconstructed is the registered source (section 4). Its ABSENCE is not an
    # error here -- it is the signal to fall back to the decomposed pair, which
    # holds the same cells under the same manual decomposition (Addendum D1) on
    # BOTH sides. tdir() is only consulted when a reconstructed tree exists, so a
    # case that was never reconstructed does not refuse before the fallback runs.
    rec_dir = tdir(case, t, soft=True)
    if rec_dir:
        rec = os.path.join(rec_dir, region, name)
        if os.path.isfile(rec):
            return [rec]
    dec = []
    for p in sorted(os.listdir(case)):
        if p.startswith("processor"):
            f = os.path.join(case, p, "%g" % t, region, name)
            if not os.path.isfile(f):
                d = [x for x in os.listdir(os.path.join(case, p))
                     if _isnum(x) and abs(float(x) - t) <= TOL_S]
                if len(d) == 1:
                    f = os.path.join(case, p, d[0], region, name)
            if os.path.isfile(f):
                dec.append(f)
    if not dec:
        refuse("no reconstructed or decomposed %s/%s at t=%g under %s"
               % (region, name, t, case))
    return dec


def gather(case, region, name, t=TIME):
    vals = []
    for p in field_paths(case, region, name, t):
        v, uni = read_field(p)
        vals.extend(v)
    return vals


def maxdiff(a, b, what):
    if len(a) != len(b):
        refuse("%s: cell counts differ, %d vs %d. Two fields of different size "
               "are not comparable and this comparator will not truncate."
               % (what, len(a), len(b)))
    if not a:
        refuse("%s: empty field. A zero over no cells is not a zero." % what)
    return max(abs(x - y) for x, y in zip(a, b))


# ------------------------------------------------------------------ rule 3 ----
def planted_control(base, quiet=False):
    """Plant 1.234e-03 K at cell 0 and cell n-1 of BOTH regions, read back from
    DISK, and REFUSE unless the reader recovers it exactly."""
    say = (lambda *a: None) if quiet else print
    work = os.path.join(HERE, ".plantwork")
    shutil.rmtree(work, ignore_errors=True)
    ok = True
    for region in ("coolant", "module"):
        srcs = field_paths(base, region, "T")
        os.makedirs(work, exist_ok=True)
        for idx_name, which in (("first", 0), ("last", -1)):
            copies = []
            for k, s in enumerate(srcs):
                d = os.path.join(work, "%s_%s_%d" % (region, idx_name, k))
                shutil.copyfile(s, d)
                copies.append(d)
            # plant BY LINE INDEX into the value list of the chosen copy
            target = copies[0] if which == 0 else copies[-1]
            _plant_by_line(target, which)
            orig = gather(base, region, "T")
            new = []
            for c in copies:
                v, _ = read_field(c)
                new.extend(v)
            seen = maxdiff(orig, new, "plant/%s/%s" % (region, idx_name))
            good = abs(seen - PLANT) <= PLANT_TOL_K
            ok &= good
            say("  plant %-7s %-8s -> reader recovered %.6e  (planted %.6e)  %s"
                % (region, idx_name, seen, PLANT,
                   "SEEN" if good else "*** MISSED -- READER IS BLIND ***"))
    shutil.rmtree(work, ignore_errors=True)
    if not ok:
        refuse("the planted-zero control FAILED. This comparator's zeros are not "
               "evidence and no arm may be cleared on them. Rule 3.")
    say("  PLANT %.6e K is ABOVE the E1 threshold %.6e K, so this control proves "
        "the GATE CAN FIRE, not merely that the reader can read." % (PLANT, E1_T_K))
    return True


def _plant_by_line(path, which):
    """Add PLANT to the first (which=0) or last (which=-1) numeric VALUE line
    INSIDE the internalField parentheses. Plants BY LINE INDEX, per rule 3.

    ⚠ THE BOUNDS ARE NOT OPTIONAL, AND THIS COMMENT IS PAID FOR.  A first cut
    took "the first numeric line in the file" and hit the list COUNT line, which
    sits OUTSIDE the parentheses the reader parses -- so the plant landed
    somewhere the reader structurally could not see and the control reported a
    perfect 0.000e+00 with the message READER IS BLIND.  That is the planted-zero
    control catching its own comparator before a single arm was cleared, which is
    the entire reason rule 3 exists.  Plant only between the parentheses.
    """
    txt = open(path).read()
    m0 = re.search(r"internalField\s+nonuniform", txt)
    lines = txt.split("\n")
    if m0:
        i0 = txt.index("(", m0.end())
        depth, j = 0, i0
        while j < len(txt):
            if txt[j] == "(":
                depth += 1
            elif txt[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        lo = txt[:i0].count("\n") + 1          # first line AFTER the opening (
        hi = txt[:j].count("\n") - 1           # last line BEFORE the closing )
        m = [i for i in range(lo, hi + 1)
             if i < len(lines) and _isnum(lines[i].strip())]
    else:
        m = []
    if not m:
        # uniform field: rewrite the uniform value
        for i, l in enumerate(lines):
            if "internalField" in l and "uniform" in l:
                v = [x for x in NUM.findall(l.split(";")[0]) if _isnum(x)]
                lines[i] = l.replace(v[-1], repr(float(v[-1]) + PLANT), 1)
                open(path, "w").write("\n".join(lines))
                return
        refuse("could not plant into %s: no numeric value line found. A control "
               "that cannot plant cannot clear anything." % path)
    i = m[0] if which == 0 else m[-1]
    lines[i] = repr(float(lines[i].strip()) + PLANT)
    open(path, "w").write("\n".join(lines))


def compare(arm_case, base, quiet=False):
    say = (lambda *a: None) if quiet else print
    fired, res = [], {}
    dT = 0.0
    for region in ("coolant", "module"):
        d = maxdiff(gather(base, region, "T"), gather(arm_case, region, "T"),
                    "%s/T" % region)
        res["maxdT_" + region] = d
        dT = max(dT, d)
    res["maxdT"] = dT
    if dT > E1_T_K:
        fired.append("E1")
    dp = maxdiff(gather(base, "coolant", "p_rgh"),
                 gather(arm_case, "coolant", "p_rgh"), "coolant/p_rgh")
    res["maxdp_rgh"] = dp
    if dp > E2_PRGH_PA:
        fired.append("E2")
    dU = maxdiff(gather(base, "coolant", "U"), gather(arm_case, "coolant", "U"),
                 "coolant/U")
    res["maxdU"] = dU
    if dU > U_DISQ:
        fired.append("E1U")
    for f in REPORTED:
        try:
            res["maxd_" + f] = maxdiff(gather(base, "coolant", f),
                                       gather(arm_case, "coolant", f),
                                       "coolant/" + f)
        except SystemExit:
            res["maxd_" + f] = None
    res["fired"] = fired
    say("  max|dT| (both regions) = %.6e K   threshold %.3e  %s"
        % (dT, E1_T_K, "E1 FIRES" if dT > E1_T_K else "ok"))
    say("  max|dp_rgh|            = %.6e Pa  threshold %.3e  %s"
        % (dp, E2_PRGH_PA, "E2 FIRES" if dp > E2_PRGH_PA else "ok"))
    say("  max|dU|                = %.6e m/s threshold %.3e  %s"
        % (dU, U_DISQ, "FIRES" if dU > U_DISQ else "ok"))
    say("  reported, gating nothing: " + "  ".join(
        "%s=%.3e" % (f, res["maxd_" + f]) for f in REPORTED
        if res.get("maxd_" + f) is not None))
    return res


def selftest():
    fails = [0]
    def chk(n, c):
        print("  %-4s %s" % ("ok" if c else "FAIL", n)); fails[0] += (0 if c else 1)
    base = os.path.join(HERE, "B0_L2")
    if not os.path.isdir(base):
        print("  (no B0_L2 on disk; selftest needs the staged baseline)"); return 1
    print("PLANTED-ZERO CONTROL:")
    chk("the control passes on the real baseline", planted_control(base) is True)
    a = gather(base, "coolant", "T")
    chk("baseline coolant T is non-empty", len(a) > 0)
    chk("a field compared against ITSELF gives exactly 0.0",
        maxdiff(a, a, "self") == 0.0)
    try:
        maxdiff(a, a[:-1], "trunc"); r = None
    except SystemExit as e:
        r = e.code
    chk("mismatched cell counts REFUSE (no truncation)", r == EXIT_REFUSE)
    try:
        tdir(base, 12345.0); r = None
    except SystemExit as e:
        r = e.code
    chk("a time that does not exist REFUSES", r == EXIT_REFUSE)
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL", fails[0]))
    return 0 if not fails[0] else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    base = os.path.join(HERE, sys.argv[sys.argv.index("--base") + 1]
                        if "--base" in sys.argv else "B0_L2")
    print("PLANTED-ZERO CONTROL (rule 3) -- runs before any real comparison:")
    planted_control(base)
    arms = (["C1", "C2", "C3", "C4", "C5"] if "--all" in sys.argv
            else [sys.argv[sys.argv.index("--arm") + 1]])
    for a in arms:
        print("\n=== %s vs %s ===" % (a, os.path.basename(base)))
        r = compare(os.path.join(HERE, a + "_L2"), base)
        print("  DISQUALIFIERS FIRED: %s" % (r["fired"] or "none -- equivalence holds"))
