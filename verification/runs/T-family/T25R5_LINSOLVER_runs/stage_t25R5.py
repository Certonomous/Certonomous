#!/usr/bin/env python3
"""T25R5 STAGER -- build one arm's case directory from the T25R4 L2 probe case.

Copies `0.orig/`, `constant/` and `system/` from the DONDR case, installs the
arm's coolant fvSolution, and edits EXACTLY THREE top-level controlDict keys.

⛔ IT DOES NOT CREATE `0/` AND IT DOES NOT RUN decomposePar.  `run_one_t25R5.sh`
does both, and its guard REFUSES a case where `0/` or any time directory already
exists -- because `0/module/T` is touched last at launch and so DATES the run
allowed to produce the answer (rule 4's age guard).  A stager that pre-created
`0/` would make the age guard unevaluable for every arm.

    python3 stage_t25R5.py --arm C4 [--donor <case>] [--force]
    python3 stage_t25R5.py --all
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DONOR = os.path.join(os.path.dirname(HERE), "T25R4_MODULE_runs", "P2")   # L2
ARMS = ["D0", "B0", "C1", "C2", "C3", "C4", "C5"]

# --- FROZEN AT THE PRE-REGISTRATION section 2 ("CHANGED, and this is the complete
# --- list") and section 3.1: 40 steps at dt 0.02, one field write, at the end.
CONTROLDICT_EDITS = {
    "endTime":      ("2",       "0.8"),        # 40 steps x dt 0.02
    "writeControl": ("runTime", "timeStep"),   # immune to the A2.2 name drift
    "writeInterval": ("5",      "40"),         # exactly one write, at endTime
}


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def edit_controldict(path):
    """Rewrite exactly the three registered TOP-LEVEL keys. Refuse on anything else.

    Top-level only: the `functions` block carries its own writeControl/
    writeInterval and is DELIBERATELY left alone, because the baseline's
    functionObject behaviour is part of what section 3.5's reproducibility control
    compares against.
    """
    lines = open(path).read().split("\n")
    depth, done = 0, {}
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("//"):
            continue
        # track brace depth so `functions { ... }` is never touched
        if depth == 0 and s.endswith(";"):
            p = s[:-1].split()
            if len(p) == 2 and p[0] in CONTROLDICT_EDITS:
                old, new = CONTROLDICT_EDITS[p[0]]
                if p[1] != old:
                    refuse("%s: top-level %s is %r, expected the donor's %r. The "
                           "donor is not the case this stager was written for."
                           % (path, p[0], p[1], old))
                if p[0] in done:
                    refuse("%s: top-level key %s appears twice. Ambiguous." % (path, p[0]))
                lines[i] = ln.replace(p[1], new, 1)
                done[p[0]] = (old, new)
        depth += ln.count("{") - ln.count("}")
    missing = set(CONTROLDICT_EDITS) - set(done)
    if missing:
        refuse("%s: registered top-level key(s) %s not found. A stager that "
               "silently skips an edit produces a case that is not the registered "
               "one." % (path, sorted(missing)))
    open(path, "w").write("\n".join(lines))
    return done


def stage(arm, donor=None, force=False):
    donor = donor or DONOR
    case = os.path.join(HERE, arm + "_L2")
    src = os.path.join(HERE, "arms", "fvSolution.coolant." + arm)
    if not os.path.isfile(src):
        refuse("no arm dictionary at %s" % src)
    if os.path.isdir(case):
        if not force:
            refuse("%s already exists. Refusing to overwrite a staged case; pass "
                   "--force only when you know nothing has run in it." % case)
        for t in os.listdir(case):
            if t == "0" or re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) or t.startswith("processor"):
                refuse("%s holds %r -- a run has happened here. A staged case is "
                       "never rebuilt over compute output." % (case, t))
        shutil.rmtree(case)
    os.makedirs(case)
    for d in ("0.orig", "constant", "system"):
        s = os.path.join(donor, d)
        if not os.path.isdir(s):
            refuse("donor %s lacks %s" % (donor, d))
        shutil.copytree(s, os.path.join(case, d), symlinks=True)

    shutil.copyfile(src, os.path.join(case, "system", "coolant", "fvSolution"))
    done = edit_controldict(os.path.join(case, "system", "controlDict"))

    # ---- POST-CONDITIONS.  A stager that cannot prove its own output is not one.
    for bad in ("0", "processor0", "processor1"):
        if os.path.exists(os.path.join(case, bad)):
            refuse("%s: %s exists after staging. The age guard would be "
                   "unevaluable." % (case, bad))
    for t in os.listdir(case):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t):
            refuse("%s: time directory %r exists after staging." % (case, t))
    inst = open(os.path.join(case, "system", "coolant", "fvSolution")).read()
    if inst != open(src).read():
        refuse("%s: the installed coolant fvSolution is not the arm dictionary." % case)
    print("staged %-3s -> %s" % (arm, case))
    print("         controlDict: " + ", ".join(
        "%s %s->%s" % (k, o, n) for k, (o, n) in sorted(done.items())))
    return 0


if __name__ == "__main__":
    d = sys.argv[sys.argv.index("--donor") + 1] if "--donor" in sys.argv else None
    f = "--force" in sys.argv
    if "--all" in sys.argv:
        for a in ARMS:
            stage(a, d, f)
        sys.exit(0)
    sys.exit(stage(sys.argv[sys.argv.index("--arm") + 1], d, f))
