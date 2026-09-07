#!/usr/bin/env python3
"""VMFL010-R2 comparator -- Laminar Flow in a 90-degree Tee-Junction (manual p.39).

Successor to VMFL010 (NOT A RESULT, OSCILLATORY). R2 repositions the self-similar
structured-hex r=2 triple into the leading-term-dominant regime (finest N=40, not N=80:
L1/L2/L3 = 10/20/40) and tightens iteration to residualControl 1e-9, so the split's
grid-to-grid difference stays above any iterative/round-off perturbation and the Roache
sign is meaningful. The GATE IS UNCHANGED from the base (0.887 +/- 3% relative) -- a
mesh-triple fix cannot move the band (L-487).

NO GRADED COMPUTE is run by, or triggered by, this file. It grades a run the
ansys-verification SUPERVISOR unlocks after the four personal checks; the launch
permission is HELD on Sanaa's desk (rule 9). Until unlock, `--selftest` exercises the
reader, the plant (present + known-bad), the classifier and the physical-range guard
with NO run data. The comparator REFUSES (exit 2) rather than degrades.

REFERENCE KIND -- DECLARED BEFORE ANY RUN: the manual's "Target" flow split 0.887 is a
PUBLISHED NUMERICAL BENCHMARK (Hayes, Nandkumar & Nasr-El-Din, Computers & Fluids
17:537-553, 1989). Either way this is a CODE-TO-CODE comparison and it buys NEITHER V
NOR P. The best attainable verdict is GATE REACHED, NEVER PASS.

Reader: postProcessing/flowRatePatch(name=<patch>)/<t>/surfaceFieldValue.dat, last row.
Split = |phi(mainOutlet)| / |phi(inlet)|  (fractional flow in the straight-through leg).
"""
import sys, os, re, glob, json, shutil, tempfile, argparse

REF_SPLIT   = 0.887            # manual "Target" -- code-to-code, buys NEITHER V nor P
ANSYS_FLU   = 0.884            # Fluent, CONTEXT ONLY
ANSYS_CFX   = 0.8837           # CFX, CONTEXT ONLY
TOL         = 0.03             # relative band; BYTE-IDENTICAL to the base freeze (L-487)
PLANT       = 0.05123
PLANT_TOL   = 1e-9
LEVELS      = ("L1", "L2", "L3")

def refuse(msg):
    sys.stderr.write("REFUSE (VMFL010-R2): %s\n" % msg); sys.exit(2)

def _fr_path(level_dir, patch):
    pats = glob.glob(os.path.join(level_dir, "postProcessing",
                                  "flowRatePatch(name=%s)" % patch, "*", "surfaceFieldValue.dat"))
    if len(pats) != 1:
        refuse("expected one flowRatePatch dat for %r in %s, found %d" % (patch, level_dir, len(pats)))
    return pats[0]

def _data_rows(path):
    """Return list of (line_index, tokens) for non-comment, non-blank rows."""
    rows = []
    with open(path) as f:
        for i, s in enumerate(f.read().splitlines()):
            t = s.strip()
            if not t or t.startswith("#"):
                continue
            p = s.split()
            if len(p) < 2:
                refuse("row < 2 cols in %s: %r" % (path, s))
            rows.append((i, p))
    if not rows:
        refuse("no data rows in " + path)
    return rows

def _read(path):
    """Reader the gate depends on: the LAST data row's (time, last-column) value."""
    rows = _data_rows(path)
    _, p = rows[-1]
    try:
        return (float(p[0]), float(p[-1]))
    except ValueError:
        refuse("unparseable last row in %s: %r" % (path, " ".join(p)))

def flow(level_dir, patch):
    return _read(_fr_path(level_dir, patch))[1]

def split(level_dir):
    qin   = abs(flow(level_dir, "inlet"))
    qmain = abs(flow(level_dir, "mainOutlet"))
    qbr   = abs(flow(level_dir, "branchOutlet"))
    if qin <= 0:
        refuse("zero inlet flow in " + level_dir)
    # mass conservation guard: |in| == |main|+|branch| to 0.5%
    if abs(qin - (qmain + qbr)) / qin > 5e-3:
        refuse("mass not conserved in %s: in=%.6g main+br=%.6g" % (level_dir, qin, qmain + qbr))
    s = qmain / qin
    # GATE-BLIND physical-range guard: a fractional flow split MUST be strictly in (0,1).
    # References NEITHER the +/-3% band NOR the 0.887 target -- only physical plausibility.
    if not (0.0 < s < 1.0):
        refuse("split %.6g not a physical fractional flow split in (0,1) for %s" % (s, level_dir))
    return s

def check_completion(level_dir):
    """Rule 4, adapted for a residualControl-terminated steady solve. last==endTime and the
    ExecutionTime count are DELIBERATELY INAPPLICABLE (solve stops before endTime) -- same
    declared basis as VMFL038/VMFL054/VMFL063. Every other limb is enforced; refuse on any."""
    logs = glob.glob(os.path.join(level_dir, "log.simpleFoam"))
    if not logs:
        refuse("no log.simpleFoam (exact name, never a log* glob) in " + level_dir)
    txt = open(logs[0]).read()
    if not re.search(r"^End\b", txt, re.M):
        refuse("no End line in solver log: " + level_dir)
    if re.search(r"FOAM FATAL", txt):
        refuse("FOAM FATAL in solver log: " + level_dir)
    if "SIMPLE solution converged" not in txt:
        refuse("not iteratively converged (no 'SIMPLE solution converged', residualControl 1e-9 unmet): " + level_dir)
    u0 = os.path.join(level_dir, "0", "U")
    if not os.path.exists(u0):
        refuse("no 0/U launch marker (age guard): " + level_dir)
    times = [d for d in os.listdir(level_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0]
    if not times:
        refuse("no written time > 0: " + level_dir)
    latest = max(times, key=float)
    uf = os.path.join(level_dir, latest, "U")
    if not os.path.exists(uf):
        refuse("no U at latestTime %s: %s" % (latest, level_dir))
    if os.path.getmtime(uf) <= os.path.getmtime(u0):
        refuse("age guard: U at %s not newer than 0/U in %s" % (latest, level_dir))
    return latest

def planted_zero_control(level_dir, patch, row_from_end=0):
    """Rule 3 / L-487. Plant a known delta into ONE row of a COPY of the flowRatePatch dat,
    then read it back through the SAME reader the gate uses (_read -> last row, last col).

    L-487 match-the-reduction: the reduction is a DIRECT read of a single scalar (the last
    row's last column), NOT a sum/mean (would cancel a full-set plant) nor a ptp/max (would
    absorb an interior plant). So the plant is seen by IDENTITY iff it lands on the row the
    reader reads. row_from_end=0 plants THAT row -> must be seen. row_from_end>0 plants a row
    the reader does NOT read -> a load-bearing control MUST report blindness (passed=False),
    which is the known-bad arm proving the control is not a rubber stamp."""
    src = _fr_path(level_dir, patch)
    before = _read(src)[1]
    tmp = tempfile.mkdtemp(prefix="vmfl010r2plant_")
    try:
        lines = open(src).read().splitlines()
        rows = _data_rows(src)                      # [(line_index, tokens), ...]
        idx = rows[-1 - row_from_end][0]            # line index of the targeted data row
        p = lines[idx].split()
        p[-1] = repr(float(p[-1]) + PLANT)
        lines[idx] = "\t".join(p)
        work = os.path.join(tmp, os.path.basename(src))
        open(work, "w").write("\n".join(lines) + "\n")
        moved = _read(work)[1] - before
        return dict(passed=abs(moved - PLANT) <= PLANT_TOL, planted=PLANT, seen=moved,
                    row_from_end=row_from_end)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def roache(vals):
    import math
    f1, f2, f3 = vals
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0:
        return dict(triple="EXACT", p=None, gci=None)
    R = e32 / e21
    if R <= 0:
        return dict(triple="OSCILLATORY", p=None, gci=None)
    if R >= 1:
        return dict(triple="DIVERGENT", p=None, gci=None)
    p = math.log(e21 / e32) / math.log(2.0)
    return dict(triple="CONVERGING", p=p, gci=1.25 * abs((f3 - f2) / f3) / (2.0 ** p - 1.0))

def grade(run_root):
    vals = []
    for lvl in LEVELS:
        d = os.path.join(run_root, lvl)
        if not os.path.isdir(d):
            refuse("missing %s (run LOCKED until supervisor unlock; launch HELD, rule 9)" % d)
        check_completion(d)
        for patch in ("inlet", "mainOutlet", "branchOutlet"):
            if not planted_zero_control(d, patch, row_from_end=0)["passed"]:
                refuse("planted-zero control did not fire for %s in %s" % (patch, d))
        vals.append(split(d))
    rc = roache(vals)
    vf = vals[-1]
    rel = abs(vf - REF_SPLIT) / abs(REF_SPLIT)
    out = dict(case="VMFL010-R2", quantity="flow_split", split=vals, finest=vf,
               ref=REF_SPLIT, ref_kind="code-to-code (buys NEITHER V nor P)",
               tol=TOL, rel=rel, triple=rc["triple"], p=rc["p"], gci=rc["gci"],
               ansys_fluent=ANSYS_FLU, ansys_cfx=ANSYS_CFX)
    print("VMFL010-R2  split(L1,L2,L3)=%s" % vals)
    if rc["triple"] != "CONVERGING":
        out["verdict"] = "NOT A RESULT"
        print("  NOT A RESULT  triple=%s  value=%.6f  (rule 5: non-CONVERGING triple)" % (rc["triple"], vf))
    else:
        out["verdict"] = "GATE REACHED" if rel <= TOL else "GATE FAIL"   # never PASS: code-to-code
        print("  %s  split=%.6f ref=%.4f rel=%.4f%% tol=%.1f%% GCI=%.3g%% p=%.2f  (buys NEITHER V nor P)"
              % (out["verdict"], vf, REF_SPLIT, 100 * rel, 100 * TOL, 100 * rc["gci"], rc["p"]))
    art = os.path.join(run_root, "GRADING_VMFL010_R2.json")
    try:
        json.dump(out, open(art, "w"), indent=2, default=str)
        print("  verdict artifact -> %s" % art)
    except OSError as e:
        refuse("could not write verdict artifact %s: %s" % (art, e))

def selftest():
    ok = True
    n_pass = 0
    n_total = 0
    def chk(name, cond):
        nonlocal ok, n_pass, n_total
        n_total += 1
        if cond:
            n_pass += 1
        print(("  PASS " if cond else "  FAIL ") + name)
        ok = ok and cond
    print("VMFL010-R2 comparator --selftest (NO run data touched)")
    chk("reference kind is code-to-code -> success ceiling is GATE REACHED, not PASS", True)
    chk("gate band byte-identical to base (TOL == 0.03)", TOL == 0.03)
    tmp = tempfile.mkdtemp(prefix="vmfl010r2self_")
    try:
        # a physically-sane split ~0.9211 (inlet -0.6675, main 0.61488, branch 0.05262)
        for patch, val in (("inlet", -0.6675), ("mainOutlet", 0.61488), ("branchOutlet", 0.05262)):
            dd = os.path.join(tmp, "postProcessing", "flowRatePatch(name=%s)" % patch, "400")
            os.makedirs(dd)
            open(os.path.join(dd, "surfaceFieldValue.dat"), "w").write("# t v\n300\t0.0\n400\t%r\n" % val)
        s = split(tmp)
        chk("split reader ~0.9211", abs(s - 0.61488 / 0.6675) < 1e-6)
        chk("planted-zero PRESENT arm: plant on the row the reader reads is SEEN",
            planted_zero_control(tmp, "mainOutlet", row_from_end=0)["passed"])
        chk("planted-zero KNOWN-BAD arm: plant on a row the reader does NOT read is NOT seen (blindness detected)",
            planted_zero_control(tmp, "mainOutlet", row_from_end=1)["passed"] is False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # gate-blind physical-range guard: mass CONSERVED but split=0 (all flow to the branch) is
    # not a physical dividing split in (0,1) -- isolates the (0,1) guard from the mass guard.
    tmp2 = tempfile.mkdtemp(prefix="vmfl010r2rng_")
    try:
        for patch, val in (("inlet", -0.6675), ("mainOutlet", 0.0), ("branchOutlet", 0.6675)):
            dd = os.path.join(tmp2, "postProcessing", "flowRatePatch(name=%s)" % patch, "400")
            os.makedirs(dd)
            open(os.path.join(dd, "surfaceFieldValue.dat"), "w").write("# t v\n400\t%r\n" % val)
        rc_seen = {"v": 0}
        try:
            split(tmp2)
        except SystemExit:
            rc_seen["v"] = 2
        chk("gate-blind guard REFUSES a non-physical split (=0, mass conserved) out of (0,1)", rc_seen["v"] == 2)
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)
    # known-bad input row -> reader refuses
    tmp3 = tempfile.mkdtemp(prefix="vmfl010r2bad_")
    try:
        dd = os.path.join(tmp3, "postProcessing", "flowRatePatch(name=inlet)", "400")
        os.makedirs(dd)
        open(os.path.join(dd, "surfaceFieldValue.dat"), "w").write("# t v\n400\tNOTANUMBER\n")
        rc_seen = {"v": 0}
        try:
            _read(_fr_path(tmp3, "inlet"))
        except SystemExit:
            rc_seen["v"] = 2
        chk("known-bad input: unparseable row is REFUSED, never coerced", rc_seen["v"] == 2)
    finally:
        shutil.rmtree(tmp3, ignore_errors=True)
    chk("CONVERGING triple classified", roache([0.900, 0.892, 0.889])["triple"] == "CONVERGING")
    chk("OSCILLATORY triple classified (base signature 0.88595/0.88445/0.88475)",
        roache([0.885949, 0.884453, 0.884749])["triple"] == "OSCILLATORY")
    chk("DIVERGENT triple classified", roache([0.90, 0.88, 0.85])["triple"] == "DIVERGENT")
    print("SELFTEST %d/%d %s" % (n_pass, n_total, "OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run-root")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.run_root:
        grade(a.run_root)
    else:
        ap.error("give --selftest or --run-root")
