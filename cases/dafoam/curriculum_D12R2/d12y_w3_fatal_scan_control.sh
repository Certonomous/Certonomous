#!/usr/bin/env bash
# W3 AMENDMENT 2 -- PLANTED-FAILURE PROOF for R-RC-4's log scan (Sanaa's standing
# directives sec.1: "Every guard ships its planted-failure proof", L-314 standard).
# ZERO COMPUTE.
#
# THE PATTERNS ARE EXTRACTED FROM d12y_w3_stage_and_run.sh ITSELF, never retyped here:
# a control that carries its own copy of the thing it is testing tests the copy, and
# would keep passing after the launcher drifted.  If the extraction finds nothing, this
# control REFUSES rather than reporting a clean zero on an empty population.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 - "$HERE/d12y_w3_stage_and_run.sh" <<'PYEOF'
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r"^\s*_FATAL = \[(.*?)\]\s*$", src, re.S | re.M)
if not m:
    print("REFUSE: could not extract _FATAL from the launcher. A pattern list this control "
          "cannot find is a population it cannot test, and a clean zero over an empty "
          "population is exactly the false green this lab has been misled by three times.")
    raise SystemExit(2)
pats = re.findall(r'r"((?:[^"\\]|\\.)*)"', m.group(1))
if len(pats) < 5:
    print("REFUSE: extracted only %d pattern(s) from the launcher: %r" % (len(pats), pats))
    raise SystemExit(2)
print("EXTRACTED %d fatal/signal patterns FROM THE LAUNCHER: %s" % (len(pats), pats))

def scan(txt):
    return [p for p in pats if re.search(p, txt, re.M)]

CLEAN = "Time = 1\nCD: 0.65 average: 0.65\nExecutionTime = 1.2 s\nEnd\n"
npass = nfail = 0
def unit(name, cond, detail=""):
    global npass, nfail
    if cond:
        npass += 1; print("  [OK ] %s %s" % (name, detail))
    else:
        nfail += 1; print("  [BAD] %s %s" % (name, detail))

# (a) THE NEGATIVE CONTROL FIRST.  A scanner that flags everything is not a scanner.
unit("(a) CLEAN log -> no tokens", scan(CLEAN) == [], "(the reader is not trigger-happy)")

# (b) EVERY PATTERN PLANTED INDIVIDUALLY.  Not one representative -- each one, because a
#     pattern never driven is a pattern nobody has shown can match anything.
PLANTS = {
    "FOAM FATAL ERROR":    "--> FOAM FATAL ERROR:\nrequest for volScalarField\n",
    "FOAM FATAL IO ERROR": "--> FOAM FATAL IO ERROR:\ncannot open file\n",
    "Segmentation fault":  "[node01:12345] *** Process received signal ***\nSegmentation fault\n",
    r"signal \(11\)":      "Foam::sigSegv::sigHandler(int) signal (11)\n",
    r"signal \(8\)":       "Foam::sigFpe::sigHandler(int) signal (8)\n",
    r"signal \(6\)":       "Foam::sigAbrt::sigHandler(int) signal (6)\n",
    "Floating point exception": "Floating point exception (core dumped)\n",
    r"^\s*\[\d+\]\s+#\d+\s": "[1] #3  Foam::sigFpe::sigHandler(int)\n",
    "MPI_ABORT":           "MPI_ABORT was invoked on rank 0\n",
}
undriven = [p for p in pats if p not in PLANTS]
unit("(b0) every launcher pattern has a planted fixture here",
     not undriven, "" if not undriven else "UNDRIVEN: %r" % undriven)
for p in pats:
    if p in PLANTS:
        hits = scan(CLEAN + PLANTS[p])
        unit("(b) PLANTED %-26r -> CAUGHT" % p, p in hits, "hits=%r" % hits)

# (c) THE CONTROL ON THE CONTROL.  Innocuous prose carrying the bare words must NOT trip
#     it, or the guard would refuse good runs -- the VMFLGPU001 failure, running backwards.
PROSE = CLEAN + ("the solver handles the signal correctly, the error norm fell, and no "
                 "fatal condition was reached during this segment\n")
unit("(c) PLANTED innocuous prose ('signal', 'error', 'fatal', 'segment') -> no tokens",
     scan(PROSE) == [], "the patterns are ANCHORED, not substrings")

print("W3 FATAL-SCAN CONTROL pass=%d fail=%d" % (npass, nfail))
raise SystemExit(0 if nfail == 0 else 1)
PYEOF
