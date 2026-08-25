#!/usr/bin/env python3
"""VMFL010 comparator -- Laminar Flow in a 90-degree Tee-Junction (manual p.39).

NO GRADED COMPUTE has been run by, or is triggered by, this file. It grades a
run the ansys-verification SUPERVISOR unlocks after four personal checks; until
then `--selftest` exercises the reader, the plant and the classifier with NO
run data. REFUSES (exit 2) rather than degrades.

REFERENCE KIND -- DECLARED BEFORE ANY RUN: the manual's "Target" flow split
0.887 is a PUBLISHED NUMERICAL BENCHMARK (Hayes, Nandkumar & Nasr-El-Din,
Computers & Fluids 17:537-553, 1989); the manual's own text also speaks of
comparison "with experimental results" but the provenance of 0.887 cannot be
established independently from the manual. Either way this is a CODE-TO-CODE
comparison and it buys NEITHER V NOR P (charter reference-kind rule). The best
attainable verdict is therefore GATE REACHED (band met = we reproduced the
reference number), NEVER PASS. Matching it is not a validation credential.

Driving input: fully-developed parabolic inlet, centerline velocity Uc=1.0 m/s
(archive profile plarb_r4.set.prof), NOT derived from the 0.887 target.

Reader: postProcessing/flowRatePatch(name=<patch>)/<t>/surfaceFieldValue.dat.
Split = |phi(mainOutlet)| / |phi(inlet)|.
"""
import sys, os, re, glob, shutil, tempfile, argparse

REF_SPLIT   = 0.887            # manual "Target"  -- code-to-code, buys NEITHER V nor P
ANSYS_FLU   = 0.884           # Fluent, CONTEXT ONLY
ANSYS_CFX   = 0.8837         # CFX, CONTEXT ONLY
TOL         = 0.03            # relative band (manual's own 3% accuracy goal); frozen in prereg
PLANT       = 0.05123
PLANT_TOL   = 1e-9
LEVELS      = ("L1", "L2", "L3")

def refuse(msg):
    sys.stderr.write("REFUSE (VMFL010): %s\n" % msg); sys.exit(2)

def _fr_path(level_dir, patch):
    pats = glob.glob(os.path.join(level_dir, "postProcessing",
                                  "flowRatePatch(name=%s)" % patch, "*", "surfaceFieldValue.dat"))
    if len(pats) != 1:
        refuse("expected one flowRatePatch dat for %r in %s, found %d" % (patch, level_dir, len(pats)))
    return pats[0]

def _read(path):
    last = None
    with open(path) as f:
        for s in f:
            s = s.strip()
            if not s or s.startswith("#"): continue
            p = s.split()
            if len(p) < 2: refuse("row < 2 cols in %s: %r" % (path, s))
            try: last = (float(p[0]), float(p[-1]))
            except ValueError: refuse("unparseable row in %s: %r" % (path, s))
    if last is None: refuse("no data rows in " + path)
    return last

def flow(level_dir, patch): return _read(_fr_path(level_dir, patch))[1]

def split(level_dir):
    qin   = abs(flow(level_dir, "inlet"))
    qmain = abs(flow(level_dir, "mainOutlet"))
    qbr   = abs(flow(level_dir, "branchOutlet"))
    if qin <= 0: refuse("zero inlet flow in " + level_dir)
    # mass conservation guard: |in| == |main|+|branch| to 0.5%
    if abs(qin - (qmain + qbr)) / qin > 5e-3:
        refuse("mass not conserved in %s: in=%.5g main+br=%.5g" % (level_dir, qin, qmain+qbr))
    return qmain / qin

def check_completion(level_dir):
    log = glob.glob(os.path.join(level_dir, "log.simpleFoam"))
    if not log: refuse("no log.simpleFoam in " + level_dir)
    if not re.search(r"^End\b", open(log[0]).read(), re.M):
        refuse("no End line in solver log: " + level_dir)
    u0 = os.path.join(level_dir, "0", "U")
    if not os.path.exists(u0): refuse("no 0/U launch marker (age guard): " + level_dir)
    times = [d for d in os.listdir(level_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0]
    if not times: refuse("no written time > 0: " + level_dir)
    latest = max(times, key=float)
    uf = os.path.join(level_dir, latest, "U")
    if not os.path.exists(uf): refuse("no U at latestTime %s: %s" % (latest, level_dir))
    if os.path.getmtime(uf) <= os.path.getmtime(u0):
        refuse("age guard: U at %s not newer than 0/U in %s" % (latest, level_dir))
    return latest

def planted_zero_control(level_dir, patch):
    src = _fr_path(level_dir, patch); before = _read(src)[1]
    tmp = tempfile.mkdtemp(prefix="vmfl010plant_")
    try:
        work = os.path.join(tmp, os.path.basename(src)); lines = open(src).read().splitlines()
        for i in range(len(lines)-1, -1, -1):
            s = lines[i].strip()
            if s and not s.startswith("#"):
                p = lines[i].split(); p[-1] = repr(float(p[-1]) + PLANT); lines[i] = "\t".join(p); break
        open(work, "w").write("\n".join(lines) + "\n")
        moved = _read(work)[1] - before
        return dict(passed=abs(moved - PLANT) <= PLANT_TOL, planted=PLANT, seen=moved)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def roache(vals):
    import math
    f1, f2, f3 = vals; e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0: return dict(triple="EXACT", p=None, gci=None)
    R = e32 / e21
    if R <= 0: return dict(triple="OSCILLATORY", p=None, gci=None)
    if R >= 1: return dict(triple="DIVERGENT", p=None, gci=None)
    p = math.log(e21 / e32) / math.log(2.0)
    return dict(triple="CONVERGING", p=p, gci=1.25*abs((f3-f2)/f3)/(2.0**p - 1.0))

def selftest():
    ok = True
    def chk(n, c):
        nonlocal ok; print(("  PASS " if c else "  FAIL ") + n); ok = ok and c
    print("VMFL010 comparator --selftest (NO run data touched)")
    chk("reference kind is code-to-code -> success ceiling is GATE REACHED, not PASS", True)
    tmp = tempfile.mkdtemp(prefix="vmfl010self_")
    try:
        for patch, val in (("inlet", -0.6675), ("mainOutlet", 0.61488), ("branchOutlet", 0.05262)):
            d = os.path.join(tmp, "postProcessing", "flowRatePatch(name=%s)" % patch, "400")
            os.makedirs(d); open(os.path.join(d, "surfaceFieldValue.dat"), "w").write("# t v\n400\t%r\n" % val)
        s = split(tmp); chk("split reader ~0.9211", abs(s - 0.61488/0.6675) < 1e-6)
        chk("plant seen", planted_zero_control(tmp, "mainOutlet")["passed"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    chk("CONVERGING triple", roache([0.90, 0.892, 0.889])["triple"] == "CONVERGING")
    print("SELFTEST", "OK" if ok else "FAILED"); sys.exit(0 if ok else 1)

def grade(run_root):
    vals = []
    for lvl in LEVELS:
        d = os.path.join(run_root, lvl)
        if not os.path.isdir(d): refuse("missing %s (run LOCKED until supervisor unlock)" % d)
        check_completion(d)
        for patch in ("inlet", "mainOutlet", "branchOutlet"):
            if not planted_zero_control(d, patch)["passed"]:
                refuse("planted-zero control did not fire for %s in %s" % (patch, d))
        vals.append(split(d))
    rc = roache(vals); vf = vals[-1]; rel = abs(vf - REF_SPLIT) / abs(REF_SPLIT)
    print("VMFL010  split(L1,L2,L3)=%s" % vals)
    if rc["triple"] != "CONVERGING":
        print("  NOT A RESULT  triple=%s  value=%.4f" % (rc["triple"], vf)); return
    verdict = "GATE REACHED" if rel <= TOL else "GATE FAIL"   # never PASS: code-to-code
    print("  %s  split=%.4f ref=%.4f rel=%.4f%% tol=%.1f%% GCI=%.3g%% p=%.2f  (buys NEITHER V nor P)"
          % (verdict, vf, REF_SPLIT, 100*rel, 100*TOL, 100*rc["gci"], rc["p"]))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run-root")
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.run_root: grade(a.run_root)
    else: ap.error("give --selftest or --run-root")
