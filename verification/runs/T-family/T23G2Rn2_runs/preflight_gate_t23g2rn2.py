#!/usr/bin/env python3
"""T23G2Rn2 A2.5 PRE-FLIGHT GATE.  DEFAULT DENY.  THE FIRST ACTION OF THE JOB.

Structural sibling of
``verification/runs/T-family/T23G2Rn_runs/preflight_gate_t23g2rn.py`` (T23G2Rn),
adapted for the §2ba numerics CORRECTED-successor T23G2Rn2 per
``docs/campaigns/T-family/T23G2Rn2_PREREGISTRATION.md`` (FROZEN, two-commit freeze
1/2 9ff29322 / 2/2 6c29b259).  Differences from the T23G2Rn gate, all registered:
  * the LEVEL NAMES are T23G2Rn2_L1/L2/L3 (corrected successor rung);
  * the REGISTERED endTimes are 8000 / 16000 / 28000 (UNCHANGED from T23G2R --
    the §2ba fix touches only the p_rgh linear-solver stopping/iteration dials,
    not the iteration budget; T23G2Rn2_PREREGISTRATION.md §2.2);
  * the §5.3 NUMERICS GATE (T23G2Rn2_PREREGISTRATION.md §5.3): the WRITTEN
    system/fluid/fvSolution p_rgh block must read tolerance 1e-09 / maxIter 100 /
    relTol 0.01 (and solver GAMG / smoother GaussSeidel unchanged), REFUSING
    otherwise.  T23G2Rn's relTol-0 config ran GAMG to its default maxIter (1000
    V-cycles) EVERY outer step (MEASURED 13-15x cost); the corrected config keeps
    the relTol-0.01 relative early-exit, drops the ABSOLUTE tolerance one decade
    below the gate (1e-9) so the sub-gate floor binds only near convergence, and
    INSERTS an explicit maxIter 100 ceiling.  This gate reads the WRITTEN file,
    not the in-memory string, so a silent non-propagation is caught before any
    solver iterates.
Every other gate, threshold and band is reused BYTE-FOR-INTENT from T23G2R.

This is a RUN ARTIFACT (a launcher-side safety gate), NOT a frozen grading-path
file: it grades nothing.  It reads and refuses; it starts no solver.

WHAT IT REFUSES ON -- all default-deny, none of them warnings:
  1. the case directory is absent
  2. system/controlDict is absent or unreadable
  3. any of the SEVEN registered function objects is missing from controlDict
  4. `housing_wall_heat` does not read the field `housing_whf` writes, or is
     ordered BEFORE it (OpenFOAM executes function objects in dictionary order)
  5. endTime in controlDict is not the level's REGISTERED endTime
  6. RULE 4 AGE GUARD: `0/` or any numeric time directory already exists
  7. 0.orig/ is absent or does not carry the twelve registered fields
  8. §5.3 NUMERICS GATE: the WRITTEN p_rgh block is not tolerance 1e-09 /
     maxIter 100 / relTol 0.01 / solver GAMG / smoother GaussSeidel
"""
import os
import re
import sys

RUNS = os.path.dirname(os.path.abspath(__file__))

# T23G2Rn2_PREREGISTRATION.md §2.2: endTimes UNCHANGED from T23G2R (8000 / 16000 /
# 28000).  These are the values build_t23g2r.py writes (LEVELS[*]["n_iter"]),
# reached through build_t23g2rn2.py's parametric edit which touches ONLY the p_rgh
# solver block.
ENDTIME = {"T23G2Rn2_L1": 8000, "T23G2Rn2_L2": 16000, "T23G2Rn2_L3": 28000}

REQUIRED_FO = ("housing_T", "core_T", "core_volavg_T", "housing_volavg_T",
               "housing_patch_T", "housing_whf", "housing_wall_heat")

NEEDED_ORIG = {
    "fluid": ("T", "U", "p", "p_rgh", "alphat", "nut", "k", "omega"),
    "housing": ("T", "p"),
    "core": ("T", "p"),
}

# §5.3 NUMERICS GATE (T23G2Rn2_PREREGISTRATION.md §5.3 / §2.1): the p_rgh block the
# build must have WRITTEN.  tolerance changed (1e-08->1e-09), maxIter INSERTED
# (100), relTol KEPT (0.01), solver/smoother held invariant.
P_RGH_REQUIRED = (("solver", "GAMG"), ("tolerance", "1e-09"),
                  ("maxIter", "100"), ("relTol", "0.01"),
                  ("smoother", "GaussSeidel"))

EXIT_REFUSE = 3


def refuse(msg):
    print("PREFLIGHT REFUSE (exit %d): %s" % (EXIT_REFUSE, msg))
    sys.exit(EXIT_REFUSE)


def main(argv):
    if len(argv) != 1 or argv[0] not in ENDTIME:
        refuse("usage: preflight_gate_t23g2rn2.py {T23G2Rn2_L1|T23G2Rn2_L2|"
               "T23G2Rn2_L3}; got %r.  A level this gate does not know is "
               "REFUSED, never guessed." % (argv,))
    level = argv[0]
    cd = os.path.join(RUNS, level)

    if not os.path.isdir(cd):
        refuse("case directory %s does not exist" % cd)

    # ---- 6. RULE 4 AGE GUARD, checked BEFORE anything that could write -------
    if os.path.exists(os.path.join(cd, "0")):
        refuse("%s/0 already exists; the rule 4 age guard cannot date this run "
               "and a run is never launched into a tree that already holds an "
               "answer" % cd)
    for e in sorted(os.listdir(cd)):
        if re.fullmatch(r"[1-9][0-9]*", e) and os.path.isdir(os.path.join(cd, e)):
            refuse("time directory %s/%s already exists; REFUSING rather than "
                   "solving on top of an existing answer" % (cd, e))

    # ---- 7. 0.orig and its twelve registered fields -------------------------
    orig = os.path.join(cd, "0.orig")
    if not os.path.isdir(orig):
        refuse("%s is absent; there is nothing to copy 0/ from" % orig)
    n = 0
    for region, fields in NEEDED_ORIG.items():
        for f in fields:
            p = os.path.join(orig, region, f)
            if not os.path.isfile(p):
                refuse("0.orig/%s/%s is missing" % (region, f))
            n += 1
    if n != 12:
        refuse("0.orig carries %d registered fields, expected 12" % n)

    # ---- 2/5. controlDict and the registered endTime ------------------------
    cdict = os.path.join(cd, "system", "controlDict")
    if not os.path.isfile(cdict):
        refuse("%s is absent" % cdict)
    txt = open(cdict, errors="replace").read()
    m = re.search(r"^\s*endTime\s+(\d+)\s*;", txt, re.M)
    if not m:
        refuse("no endTime in %s" % cdict)
    got = int(m.group(1))
    if got != ENDTIME[level]:
        refuse("%s controlDict endTime is %d; the registration (§2.2) says %d. "
               "The case that would run is not the case that was registered."
               % (level, got, ENDTIME[level]))

    # ---- 3. every registered function object present ------------------------
    missing = [fo for fo in REQUIRED_FO
               if not re.search(r"^\s{4}%s\s*$" % re.escape(fo), txt, re.M)]
    if missing:
        refuse("controlDict is missing registered function object(s): %s."
               % ", ".join(missing))

    # ---- 4. wallHeatFlux ordering, which is load-bearing --------------------
    i_whf = txt.find("\n    housing_whf\n")
    i_wh = txt.find("\n    housing_wall_heat\n")
    if i_whf < 0 or i_wh < 0:
        refuse("cannot locate housing_whf / housing_wall_heat blocks to check "
               "their order")
    if i_whf > i_wh:
        refuse("housing_whf is ordered AFTER housing_wall_heat; the integral "
               "would read a field that does not exist yet and Q5 would be "
               "silently absent.")
    blk = txt[i_wh:i_wh + 600]
    if "wallHeatFlux" not in blk:
        refuse("housing_wall_heat does not integrate the field `wallHeatFlux`.")

    # ---- 8. §5.3 NUMERICS GATE: the WRITTEN p_rgh block ---------------------
    # Read off the FILE, never the in-memory build string: this is the
    # independent on-disk confirmation that build_t23g2rn2.py's p_rgh override
    # (tolerance 1e-09 + inserted maxIter 100) reached disk
    # (T23G2Rn2_PREREGISTRATION.md §5.3).
    fvsol = os.path.join(cd, "system", "fluid", "fvSolution")
    if not os.path.isfile(fvsol):
        refuse("%s is absent; the §5.3 numerics gate cannot read the p_rgh "
               "block and an unevaluated gate is not a passed one" % fvsol)
    ftxt = open(fvsol, errors="replace").read()
    pm = re.search(r"\n    p_rgh\n    \{\n(.*?)\n    \}", ftxt, re.S)
    if not pm:
        refuse("could not delimit the p_rgh block in %s; the written file is "
               "not the structure the §5.3 gate expects" % fvsol)
    body = pm.group(1)
    for key, val in P_RGH_REQUIRED:
        km = re.search(r"\b%s\s+(\S+?);" % re.escape(key), body)
        if not km:
            refuse("§5.3: the WRITTEN p_rgh block in %s has no `%s` entry"
                   % (fvsol, key))
        if km.group(1) != val:
            refuse("§5.3 NUMERICS GATE: the WRITTEN p_rgh block reads `%s %s;`, "
                   "the registration (§2.1/§5.3) requires `%s %s;`.  A silent "
                   "non-propagation of the numerics change is caught here BEFORE "
                   "any solver iterates -- NO SOLVER STARTS."
                   % (key, km.group(1), key, val))

    print("PREFLIGHT PASS: %s" % level)
    print("  age guard clean (no 0/, no time directory)")
    print("  0.orig carries all 12 registered fields")
    print("  controlDict endTime = %d, as registered (§2.2)" % got)
    print("  all %d registered function objects present" % len(REQUIRED_FO))
    print("  housing_whf ordered BEFORE housing_wall_heat, which integrates "
          "wallHeatFlux")
    print("  §5.3 numerics gate: WRITTEN p_rgh block is tolerance 1e-09 / "
          "maxIter 100 / relTol 0.01 / solver GAMG / smoother GaussSeidel")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
