#!/usr/bin/env python3
"""Comparator for the two JF1 ladders frozen on 2026-09-01.

  gateE   -- JF1E turbulence-stall escalation, Gate E
             verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md
             frozen 6e83157c112cdf606094f88ff0592bf1b02bc4b3
  gridG   -- JF1G grid convergence, Gates G1..G7
             verification/campaign/JF1G_GRID_CONVERGENCE_PREREGISTRATION.md
             frozen 038f4bca160af8bc201f93805cb841a30236a28c

ONE FILE, because the clipping counter, the CL reader and the completion check are
shared by both ladders and a second copy of any of them is a second place for them to
drift apart.

THIS COMPARATOR REFUSES (exit 2) RATHER THAN DEGRADE.  Every refusal is registered in
JF1E section 7 or JF1G section 6.1.  `--selftest` proves each reader can see a
non-zero before any zero it returns is believed (CLAUDE.md rule 3).

## THE RICHARDSON SIGN, AND WHY IT HAS ITS OWN CONTROL

`docs/NUMERICS_KNOWLEDGE.md` N-T8: four independent implementations in this lab wrote

    f_ext = f_fine + e21/(r^p - 1)      # WRONG -- reflects the limit through f_fine

where the correct form is

    f_ext = f_fine - e21/(r^p - 1),     e21 = f_mid - f_fine

The wrong form has the right magnitude, the right units and a plausible position
between the levels; `p` and `GCI` are both sign-independent, so every neighbouring
number stays correct and a key-presence selftest cannot catch it.  The standing rule
adopted 2026-08-24 requires a VALUE-checking control: a synthetic power-law triple
whose limit is known by construction, asserted to 1e-12 relative.  N-T8's free
identity `frozen + corrected == 2 f_fine` is asserted on the real data as well.
"""

import argparse
import glob
import math
import os
import re
import shutil
import sys
import tempfile

R_LADDER = 1.5          # JF1G section 2, frozen
FS_GCI = 1.25           # CLAUDE.md rule 5, frozen
PLANT_CL = 1.234e-03    # the planted perturbation for the CL reader
# The clipping counter's live control.  This row is on disk and its final-500
# `bounding k` count is 494.  A counter that cannot return 494 here is not
# trusted to return 0 anywhere.
CLIP_CONTROL_RUN = "JF1_L1_BLOWN_CMU010_A0"
CLIP_CONTROL_EXPECT = 494
CLIP_WINDOW = 500


def die(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# --------------------------------------------------------------------------
# readers
# --------------------------------------------------------------------------
def coefficient_file(run_root):
    hits = sorted(glob.glob(os.path.join(
        run_root, "postProcessing", "forceCoeffs*", "*", "coefficient*.dat")))
    if not hits:
        die("no forceCoeffs coefficient file under %s" % run_root)
    return hits[-1]


def read_cl(path):
    """time -> Cl, with the Cl column located BY THE FILE'S OWN HEADER.

    Locating it by index is registered as a refusal (JF1G section 6.1 clause 6):
    the file carries Cd, Cd(f), Cd(r), Cl, Cl(f), Cl(r), ... and an index taken
    from memory silently returns Cd(r) or Cl(f) on a column-order change.
    """
    header = None
    out = {}
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("#"):
                cols = line.lstrip("#").split()
                if "Cl" in cols:
                    header = cols
                continue
            if header is None:
                die("%s has data rows before any header naming Cl" % path)
            parts = line.split()
            if len(parts) != len(header):
                continue
            try:
                out[int(float(parts[header.index("Time")]))] = \
                    float(parts[header.index("Cl")])
            except (ValueError, IndexError):
                continue
    if not out:
        die("no Cl rows read from %s" % path)
    return out


def count_bounding(log_path, field, window=CLIP_WINDOW):
    """`bounding <field>` events in the final `window` solver iterations.

    Counted by walking the log and attributing each bounding line to the `Time`
    block it sits in -- NOT by tailing the file, because the number of lines per
    iteration is not constant and a tail is a coin flip on where the window starts.
    """
    if not os.path.isfile(log_path):
        die("no solver log at %s" % log_path)
    times = []
    marker = "bounding %s" % field
    hits = []
    t = None
    with open(log_path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("Time = "):
                try:
                    t = int(float(line.split("=", 1)[1]))
                except ValueError:
                    continue
                times.append(t)
            elif t is not None and line.startswith(marker):
                hits.append(t)
    if not times:
        die("no `Time = ` lines in %s" % log_path)
    cutoff = max(times) - window
    return sum(1 for h in hits if h > cutoff), max(times)


def last_initial_residual(log_path, field):
    """Initial residual of `field` at the final iteration.

    Takes the LAST match, which is correct ONLY for a field solved once per
    iteration.  `p` is solved (nNonOrthogonalCorrectors + 1) times per iteration,
    so for `p` the last match is the final corrector pass -- which is the value
    the SIMPLE residualControl itself reads, so it is the right one here.  The
    hazard is recorded rather than left implicit.
    """
    pat = re.compile(r"Solving for %s, Initial residual = ([0-9.eE+-]+)" % re.escape(field))
    val = None
    with open(log_path, "r", errors="ignore") as fh:
        for line in fh:
            m = pat.search(line)
            if m:
                val = float(m.group(1))
    if val is None:
        die("no `Solving for %s` line in %s" % (field, log_path))
    return val


def completion(run_root):
    """CLAUDE.md rule 4, all clauses.  Returns (ok, list of failed clause names)."""
    fails = []
    log = os.path.join(run_root, "log.simpleFoam")
    rcf = os.path.join(run_root, "SOLVER_RC.txt")
    if not os.path.isfile(log):
        return False, ["no solver log"]

    rc = None
    if os.path.isfile(rcf):
        m = re.search(r"solver_rc\s+(-?\d+)", open(rcf, errors="ignore").read())
        if m:
            rc = int(m.group(1))
    if rc != 0:
        fails.append("rc=%s (not 0)" % rc)

    txt = open(log, "r", errors="ignore").read()
    if not re.search(r"^End", txt, re.M):
        fails.append("no End line")

    times = [int(float(x)) for x in re.findall(r"^Time = ([0-9.eE+-]+)", txt, re.M)]
    cd = os.path.join(run_root, "system", "controlDict")
    end_time = None
    if os.path.isfile(cd):
        m = re.search(r"^endTime\s+([0-9.eE+-]+);", open(cd, errors="ignore").read(), re.M)
        if m:
            end_time = int(float(m.group(1)))
    if end_time is None:
        fails.append("no endTime in controlDict")
    elif not times or times[-1] != end_time:
        fails.append("last time %s != endTime %s" % (times[-1] if times else None, end_time))

    n_exec = len(re.findall(r"^ExecutionTime", txt, re.M))
    if end_time is not None and n_exec != end_time:
        fails.append("ExecutionTime count %d != endTime %s" % (n_exec, end_time))

    # fields present at endTime, and the AGE GUARD: every one newer than 0/U,
    # which is touched last at launch and so dates the run allowed to answer.
    if end_time is not None:
        tdir = os.path.join(run_root, str(end_time))
        ref = os.path.join(run_root, "0", "U")
        if not os.path.isdir(tdir):
            fails.append("no %s time directory" % end_time)
        elif not os.path.isfile(ref):
            fails.append("no 0/U to date the run against")
        else:
            t0 = os.path.getmtime(ref)
            for f in ("U", "p", "k", "omega", "nut"):
                fp = os.path.join(tdir, f)
                if not os.path.isfile(fp):
                    fails.append("field %s absent at endTime" % f)
                elif os.path.getmtime(fp) <= t0:
                    fails.append("AGE GUARD: %s/%s not newer than 0/U" % (end_time, f))
    return (not fails), fails


# --------------------------------------------------------------------------
# Roache
# --------------------------------------------------------------------------
def richardson(f_fine, f_mid, r, p):
    """CORRECT form.  f_ext = f_fine - e21/(r^p - 1), e21 = f_mid - f_fine."""
    den = r ** p - 1.0
    if den == 0.0:
        die("r^p - 1 == 0; no Richardson extrapolate exists")
    return f_fine - (f_mid - f_fine) / den


def richardson_frozen_defect(f_fine, f_mid, r, p):
    """The N-T8 sign defect, kept ONLY so the identity control can assert it."""
    return f_fine + (f_mid - f_fine) / (r ** p - 1.0)


def triple(f_coarse, f_mid, f_fine, r=R_LADDER):
    """Classify and, where legal, compute p / GCI.  CLAUDE.md rule 5."""
    e21 = f_mid - f_fine        # mid  - fine
    e32 = f_coarse - f_mid      # coarse - mid
    out = {"f_coarse": f_coarse, "f_mid": f_mid, "f_fine": f_fine,
           "e21": e21, "e32": e32, "p": None, "gci_fine": None,
           "f_ext": None, "kind": None}

    tiny = 1e-14 * max(1.0, abs(f_fine))
    if abs(e21) < tiny and abs(e32) < tiny:
        out["kind"] = "EXACT"
        return out
    if abs(e21) < tiny or abs(e32) < tiny:
        out["kind"] = "STAGNANT"
        return out

    ratio = e21 / e32
    if ratio < 0.0:
        out["kind"] = "OSCILLATORY"
        return out
    if ratio >= 1.0:
        out["kind"] = "DIVERGENT"
        return out

    out["kind"] = "CONVERGING"
    out["p"] = math.log(abs(e32 / e21)) / math.log(r)
    out["f_ext"] = richardson(f_fine, f_mid, r, out["p"])
    out["gci_fine"] = FS_GCI * abs(e21 / f_fine) / (r ** out["p"] - 1.0)
    return out


# --------------------------------------------------------------------------
# selftest -- every reader shown able to see a non-zero
# --------------------------------------------------------------------------
def selftest(runs_dir):
    print("== SELFTEST ==")
    ok = True

    # 1. RICHARDSON VALUE CONTROL (N-T8's standing rule, 2026-08-24).
    #    A synthetic power law whose limit is known BY CONSTRUCTION.
    f_ex, A, p_true, r = 0.5488, 0.01, 2.0, R_LADDER
    h = [1.0, r, r * r]                       # fine, mid, coarse
    f1, f2, f3 = (f_ex + A * x ** p_true for x in h)
    t = triple(f3, f2, f1, r)
    if t["kind"] != "CONVERGING":
        print("  FAIL richardson control: synthetic triple classified %s" % t["kind"]); ok = False
    else:
        dp = abs(t["p"] - p_true)
        rel = abs(t["f_ext"] - f_ex) / abs(f_ex)
        print("  richardson VALUE control: p %.12f (true %.1f, |d| %.2e), "
              "f_ext %.15f (true %.15f, rel %.2e)" % (t["p"], p_true, dp, t["f_ext"], f_ex, rel))
        if rel > 1e-12:
            print("  FAIL: extrapolate is not the known limit to 1e-12 -- THIS IS THE "
                  "N-T8 SIGN DEFECT"); ok = False
        if dp > 1e-10:
            print("  FAIL: observed order not recovered"); ok = False
        # N-T8's free identity: frozen + corrected == 2 f_fine
        lhs = richardson_frozen_defect(f1, f2, r, t["p"]) + t["f_ext"]
        if abs(lhs - 2.0 * f1) > 1e-12 * abs(f1):
            print("  FAIL identity frozen+corrected == 2 f_fine"); ok = False
        else:
            print("  identity frozen + corrected == 2 f_fine: HOLDS")
        # and the defective form must be measurably WRONG, or the control is vacuous
        if abs(richardson_frozen_defect(f1, f2, r, t["p"]) - f_ex) / abs(f_ex) < 1e-6:
            print("  FAIL: the defective form is NOT distinguishable here -- the "
                  "control cannot detect the defect it exists for"); ok = False
        else:
            print("  defective form is distinguishable (control is not vacuous)")

    # 2. TRIPLE CLASSIFIER -- each verdict shown able to fire.
    cases = [((3.0, 2.0, 1.0), "DIVERGENT"),      # e21=1, e32=1 -> ratio 1.0
             ((1.0, 3.0, 2.0), "OSCILLATORY"),    # e21=1, e32=-2
             ((5.0, 5.0, 5.0), "EXACT")]
    for (c, m, f), want in cases:
        got = triple(c, m, f)["kind"]
        print("  classifier (%s,%s,%s) -> %s (want %s)%s"
              % (c, m, f, got, want, "" if got == want else "   FAIL"))
        if got != want:
            ok = False

    # 3. CL READER PLANTED CONTROL (CLAUDE.md rule 3).
    ctrl = os.path.join(runs_dir, CLIP_CONTROL_RUN)
    if not os.path.isdir(ctrl):
        print("  FAIL: control run %s absent -- the planted controls cannot run" % ctrl)
        return False
    src = coefficient_file(ctrl)
    base = read_cl(src)
    t_end = max(base)
    tmpd = tempfile.mkdtemp(prefix="jf1_plant_")
    try:
        dst = os.path.join(tmpd, "coefficient.dat")
        hdr_cols = None
        with open(src, errors="ignore") as fin, open(dst, "w") as fout:
            for line in fin:
                if line.startswith("#"):
                    cols = line.lstrip("#").split()
                    if "Cl" in cols:
                        hdr_cols = cols
                    fout.write(line)
                    continue
                parts = line.split()
                if hdr_cols and len(parts) == len(hdr_cols):
                    i = hdr_cols.index("Cl")
                    parts[i] = "%.12e" % (float(parts[i]) + PLANT_CL)
                    fout.write("\t".join(parts) + "\n")
                else:
                    fout.write(line)
        planted = read_cl(dst)
        delta = planted[t_end] - base[t_end]
        print("  CL reader planted control: read-back delta %.12e (plant %.12e)"
              % (delta, PLANT_CL))
        if abs(delta - PLANT_CL) > 1e-9:
            print("  FAIL: the reader cannot see the plant -- no zero or small "
                  "difference it returns is evidence"); ok = False
        if abs(base[t_end] - 0.54884644) > 1e-7:
            print("  FAIL: control CL %.8f is not the recorded 0.54884644" % base[t_end])
            ok = False
        else:
            print("  CL reader returns the control's recorded value 0.54884644")
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    # 4. CLIPPING COUNTER LIVE CONTROL -- must see a non-zero before a zero counts.
    log = os.path.join(ctrl, "log.simpleFoam")
    n, t_last = count_bounding(log, "k")
    print("  clipping counter on %s: final-%d `bounding k` = %d (expect %d), last Time %d"
          % (CLIP_CONTROL_RUN, CLIP_WINDOW, n, CLIP_CONTROL_EXPECT, t_last))
    if n != CLIP_CONTROL_EXPECT:
        print("  FAIL: the counter does not reproduce the recorded control value")
        ok = False
    # and it must return 0 on a log with the lines removed -- a counter that
    # returns 494 on everything is not a counter.
    tmpd = tempfile.mkdtemp(prefix="jf1_clip_")
    try:
        stripped = os.path.join(tmpd, "log.simpleFoam")
        with open(log, errors="ignore") as fin, open(stripped, "w") as fout:
            for line in fin:
                if not line.startswith("bounding k"):
                    fout.write(line)
        n0, _ = count_bounding(stripped, "k")
        print("  clipping counter on the same log with `bounding k` removed: %d (expect 0)" % n0)
        if n0 != 0:
            print("  FAIL: counter returns non-zero on a log with no bounding lines"); ok = False
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("== SELFTEST %s ==" % ("PASS" if ok else "FAIL"))
    return ok


# --------------------------------------------------------------------------
# gate E
# --------------------------------------------------------------------------
def gate_e(runs_dir, rung):
    print("== JF1E GATE E, rung %s ==" % rung)
    print("   LABEL numerics-diagnostic: no physics verdict, no lift claim, no")
    print("   observed order, no GCI and no band comes off this ladder.")
    print("   CAVEAT D-1: no run in this chain was seeded from a CONVERGED field.")
    rows, verdicts = [], []
    for tag in ("CMU005", "CMU010", "CMU020", "CMU040"):
        rr = os.path.join(runs_dir, "JF1E_%s_%s_A0" % (rung, tag))
        if not os.path.isdir(rr):
            rows.append((tag, "PENDING", None, None, None, None, None, None))
            continue
        done, fails = completion(rr)
        log = os.path.join(rr, "log.simpleFoam")
        bk, _ = count_bounding(log, "k")
        bo, _ = count_bounding(log, "omega")
        rk = last_initial_residual(log, "k")
        ro = last_initial_residual(log, "omega")
        rp = last_initial_residual(log, "p")
        cl = read_cl(coefficient_file(rr))
        cl_end = cl[max(cl)]
        if not done:
            v = "NOT A RESULT"
        elif bk == 0 and bo == 0 and rk < 1e-6 and ro < 1e-6 and rp < 1e-6:
            v = "GATE REACHED"
        else:
            v = "GATE FAIL"
        verdicts.append(v)
        rows.append((tag, v, bk, bo, rk, ro, rp, cl_end))
        if fails:
            print("   %s completion failures: %s" % (tag, "; ".join(fails)))

    print("\n%-8s %-13s %8s %8s %12s %12s %12s %12s"
          % ("row", "verdict", "bk/500", "bo/500", "res k", "res omega", "res p", "CL"))
    for tag, v, bk, bo, rk, ro, rp, cl in rows:
        fmt = lambda x, f: (f % x) if x is not None else "-"
        print("%-8s %-13s %8s %8s %12s %12s %12s %12s"
              % (tag, v, fmt(bk, "%d"), fmt(bo, "%d"), fmt(rk, "%.3e"),
                 fmt(ro, "%.3e"), fmt(rp, "%.3e"), fmt(cl, "%.8f")))

    if len(verdicts) < 4:
        print("\nRUNG %s: PENDING -- %d of 4 rows complete" % (rung, len(verdicts)))
    elif all(v == "GATE REACHED" for v in verdicts):
        print("\nRUNG %s: GATE REACHED on all four rows -- the ladder ENDS here." % rung)
    elif any(v == "NOT A RESULT" for v in verdicts):
        print("\nRUNG %s: NOT A RESULT -- a row failed the strict completion rule." % rung)
    else:
        print("\nRUNG %s: GATE FAIL -- escalate to the next rung in the frozen order." % rung)
        print("   The residual clauses alone would have passed rows whose k field was")
        print("   FLAT BECAUSE IT WAS CLIPPED.  That is L-235 and it is why the")
        print("   bounding counters are load-bearing clauses, not diagnostics.")
    return 0


# --------------------------------------------------------------------------
# grid G
# --------------------------------------------------------------------------
def grid_g(runs_dir, passno):
    print("== JF1G GRID CONVERGENCE, pass %s ==" % passno)
    if str(passno) == "0":
        print("   LABEL diagnostic: THIS PASS SCORES NOTHING.  No PASS, no GATE")
        print("   REACHED, no observed order and no GCI may be quoted from it.")
        print("   Its purpose is to measure the level-to-level |dCL| that the")
        print("   tightness rule needs.")
    lev = {}
    for L in ("C1", "C2", "C3"):
        rr = os.path.join(runs_dir, "JF1G_P%s_%s_CMU010_A0" % (passno, L))
        if not os.path.isdir(rr):
            print("   %s: PENDING (no run root)" % L)
            continue
        done, fails = completion(rr)
        log = os.path.join(rr, "log.simpleFoam")
        if not os.path.isfile(log):
            print("   %s: NOT A RESULT -- no solver log (%s)" % (L, "; ".join(fails)))
            continue
        cl = read_cl(coefficient_file(rr))
        t_end = max(cl)
        eps = abs(cl[t_end] - cl[t_end - 2000]) if (t_end - 2000) in cl else None
        bk, _ = count_bounding(log, "k")
        bo, _ = count_bounding(log, "omega")
        ypl = None
        m = re.findall(r"patch airfoil y\+ : min = [0-9.eE+-]+, max = ([0-9.eE+-]+)",
                       open(log, errors="ignore").read())
        if m:
            ypl = float(m[-1])
        lev[L] = {"cl": cl[t_end], "eps": eps, "bk": bk, "bo": bo, "yplus": ypl,
                  "done": done, "fails": fails, "t_end": t_end}

    print("\n%-4s %14s %13s %9s %9s %9s %8s  %s"
          % ("lvl", "CL", "eps(2000)", "y+max", "bk/500", "bo/500", "endTime", "completion"))
    for L in ("C1", "C2", "C3"):
        if L not in lev:
            print("%-4s %14s" % (L, "PENDING")); continue
        d = lev[L]
        print("%-4s %14.8f %13s %9s %9d %9d %8d  %s"
              % (L, d["cl"],
                 ("%.3e" % d["eps"]) if d["eps"] is not None else "-",
                 ("%.4f" % d["yplus"]) if d["yplus"] is not None else "-",
                 d["bk"], d["bo"], d["t_end"],
                 "OK" if d["done"] else ("FAIL: " + "; ".join(d["fails"])[:60])))

    # Gate G2 -- y+ < 1 on every level
    for L, d in lev.items():
        if d["yplus"] is not None and d["yplus"] >= 1.0:
            print("\nGATE G2 BREACH: %s max y+ = %.4f >= 1" % (L, d["yplus"]))
            print("VERDICT: NOT A RESULT"); return 0

    # L-235 -- report clipping whatever the verdict
    clipped = [L for L, d in lev.items() if d["bk"] > 0 or d["bo"] > 0]
    if clipped:
        print("\nL-235 NOTE: %s clipping k/omega through the final %d iterations."
              % (", ".join(sorted(clipped)), CLIP_WINDOW))
        print("   A level whose forces are stationary while k is being clipped is")
        print("   STATIONARY-AND-CLIPPING-HELD, never converged.")

    if len(lev) < 3:
        print("\nVERDICT: PENDING -- %d of 3 levels present." % len(lev))
        return 0
    if not all(lev[L]["done"] for L in ("C1", "C2", "C3")):
        print("\nVERDICT: NOT A RESULT -- a level failed the strict completion rule")
        print("   (rule 5 clause 1: a level not iteratively converged voids the triple)")
        return 0

    t = triple(lev["C1"]["cl"], lev["C2"]["cl"], lev["C3"]["cl"])
    d21 = abs(lev["C2"]["cl"] - lev["C1"]["cl"])
    d32 = abs(lev["C3"]["cl"] - lev["C2"]["cl"])
    eps_max = max(d["eps"] for d in lev.values() if d["eps"] is not None)
    print("\n-- level-to-level differences --")
    print("   |CL_C2 - CL_C1| = %.6e" % d21)
    print("   |CL_C3 - CL_C2| = %.6e" % d32)
    print("   max iterative change over the final 2000 iterations = %.6e" % eps_max)

    # GATE G4 -- the tightness rule.  Refuse to report p or GCI if it fails.
    need = 0.1 * min(d21, d32)
    print("   tightness rule: %.6e <= %.6e ?  %s"
          % (eps_max, need, "YES" if eps_max <= need else "NO"))
    if eps_max > need:
        print("\nGATE G4 BREACH -- the observed order would be NOISE, NOT")
        print("DISCRETISATION.  The comparator REFUSES to report p or a GCI.")
        print("VERDICT: PENDING -- tighten residuals and the stationarity window,")
        print("then re-run the levels.  This is NOT a converged study with a caveat.")
        return 0

    print("\n-- Roache triple (CLAUDE.md rule 5), r = %.3f --" % R_LADDER)
    print("   e21 (mid-fine) = %.6e   e32 (coarse-mid) = %.6e" % (t["e21"], t["e32"]))
    print("   classification = %s" % t["kind"])
    if t["kind"] != "CONVERGING":
        print("\nVERDICT: NOT A RESULT -- triple is %s." % t["kind"])
        print("   CL values: C1 %.8f  C2 %.8f  C3 %.8f"
              % (t["f_coarse"], t["f_mid"], t["f_fine"]))
        print("   NO GCI is quoted: the three values are not monotone.")
        return 0

    print("   observed order p = %.6f" % t["p"])
    print("   Richardson extrapolate f_ext = %.8f  (CORRECT sign, N-T8)" % t["f_ext"])
    print("   GCI on the fine level at Fs = %.2f: %.6e  (%.4f %%)"
          % (FS_GCI, t["gci_fine"], 100.0 * t["gci_fine"]))
    # N-T8's free identity, asserted on the REAL data.
    lhs = richardson_frozen_defect(t["f_fine"], t["f_mid"], R_LADDER, t["p"]) + t["f_ext"]
    if abs(lhs - 2.0 * t["f_fine"]) > 1e-10 * abs(t["f_fine"]):
        die("N-T8 identity frozen + corrected == 2 f_fine FAILS on the real data")
    print("   N-T8 identity on real data: HOLDS")

    if str(passno) == "0":
        print("\nPASS 0 SCORES NOTHING.  The numbers above are diagnostic and no")
        print("verdict of the fixed vocabulary attaches to them.")
        return 0

    # GATE G6 -- acceptance band on p
    if 1.5 <= t["p"] <= 2.5:
        print("\nGATE G6: p = %.6f is inside [1.5, 2.5] -- the case is GRADABLE." % t["p"])
        print("VERDICT: PASS.  Band on CL at C_mu = 0.1 is the fine-level GCI,")
        print("        CL = %.8f +/- %.6e (%.4f %%)"
              % (t["f_fine"], t["gci_fine"] * abs(t["f_fine"]), 100.0 * t["gci_fine"]))
    else:
        print("\nGATE G6: p = %.6f is OUTSIDE [1.5, 2.5]." % t["p"])
        print("VERDICT: GATE FAIL on the acceptance band.")
        print("SECTION 7 EXECUTES AUTOMATICALLY AND IT DOES NOT STOP:")
        print("  1. re-check tightness on the finest level at residualControl 1e-9")
        print("  2. re-verify mesh similarity (section 2.2) on the emitted meshes")
        print("  3. add C4 at the same r = 1.5 (455,456 cells); p on the finest three")
        print("  4. repeat for up to two more levels")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "gateE", "gridG"])
    ap.add_argument("--runs", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--rung", default="E1")
    ap.add_argument("--pass", dest="passno", default="0")
    a = ap.parse_args()

    # THE SELFTEST GATES EVERY GRADING PATH.  A comparator whose readers have not
    # been shown able to see a non-zero does not get to report a zero.
    if a.mode == "selftest":
        sys.exit(0 if selftest(a.runs) else 2)
    if not selftest(a.runs):
        die("selftest failed -- no grading is performed")
    print()
    sys.exit(gate_e(a.runs, a.rung) if a.mode == "gateE" else grid_g(a.runs, a.passno))


if __name__ == "__main__":
    main()
