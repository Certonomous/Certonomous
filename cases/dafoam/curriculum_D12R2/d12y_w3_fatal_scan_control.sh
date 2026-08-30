#!/usr/bin/env bash
# W3 ADDENDUM 1 (2026-08-30) -- PLANTED-FAILURE PROOF for R-RC-4's log scan, REPAIRED and
# now TWO-DIRECTIONAL AGAINST THE REAL CORPUS (Sanaa's standing directives sec.1: "Every
# guard ships its planted-failure proof", L-314 standard).  ZERO COMPUTE.
#
# WHY THIS CONTROL WAS REPAIRED, AND IT IS THE WHOLE LESSON OF W3-LAUNCHER-DEF-2.
# The superseded version passed 12/12 while the instrument it certified was BLIND on every
# real log this lab produces.  It failed in TWO independent ways, and only the first is the
# one people remember:
#
#   (1) EVERY FIXTURE WAS SYNTHETIC.  It invented nine planted crash strings, confirmed each
#       was caught, added innocuous prose and confirmed that was not -- and NEVER ONCE ran a
#       pattern against a REAL DAFoam log.  A control validated only against fixtures it
#       invented can pass while the instrument is blind to the real corpus.  The bare token
#       `Floating point exception` matched OpenFOAM's STANDARD STARTUP BANNER
#           trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
#       on 5 of 5 real clean corpora, and no synthetic fixture ever contained that line.
#
#   (2) IT TESTED A COPY OF THE ALGORITHM, NOT THE ALGORITHM.  It extracted the launcher's
#       PATTERN LIST (correctly, and its own header says why) but then re-implemented the
#       SCAN as its own whole-file `re.search(p, txt, re.M)`.  So the pattern list was
#       driven live while the SEMANTICS -- the part that was actually broken -- were a
#       private copy the launcher could never invalidate.  Its own header names this exact
#       trap for the pattern list and then walks into it for the scan.
#
# THE REPAIR CLOSES BOTH.  The launcher's REAL scan block is EXTRACTED FROM ITS SOURCE AND
# EXECUTED here, so this control drives the shipping implementation rather than a
# description of it; and the must-not-flag fixtures are REAL LOG BYTES from three preserved
# corpora, registered by md5 so a fixture that drifts REFUSES instead of quietly passing.
#
# THE TOKEN MUST STAY.  Deleting `Floating point exception` would blind the scan to a real
# SIGFPE, which is the WORSE error direction.  This control therefore asserts the token is
# STILL PRESENT, and drives three real SIGFPE spellings plus a REAL CRASH LOG EXCERPT as
# MUST-FLAG.  A repaired scan that cannot still catch a real SIGFPE is not repaired, it is
# disabled, and these units are what tell the two apart.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 - "$HERE" <<'PYEOF'
import hashlib
import os
import re
import sys
import textwrap

HERE = sys.argv[1]
LAUNCHER = os.path.join(HERE, "d12y_w3_stage_and_run.sh")

# ---- REAL-CORPUS FIXTURES, registered by md5. -----------------------------------------
# A fixture whose bytes have drifted is not the corpus this control claims to test, so a
# mismatch REFUSES rather than reporting a clean zero over bytes nobody has looked at.
FIXTURES = {
    # W3's OWN first stage: the 2,450-cell mesh log the supervisor stopped the run on.
    # 4 trapFpe banner lines, 0 FOAM FATAL, 5 End lines -- a CLEAN, COMPLETED stage.
    # These same bytes are independently frozen by curriculum_SO1aR as
    # so1ar_fixture_REAL_SO1a_MESH_checkMesh.log's sibling fixture, md5 ccc4f40f... --
    # two items reached the same bytes separately, which is a cross-check, not a copy.
    "d12y_w3_fixture_REAL_D12R2W3_S0.log": "ccc4f40fa0e1c1849bb7bc15a4042d47",
    # A SECOND, INDEPENDENT ITEM (D6R multipoint accuracy run) so the must-not-flag
    # direction does not rest on one corpus.
    "d12y_w3_fixture_REAL_D6R_ACC_excerpt.log": "61add2fd3f29a476c68f59aec5abaf02",
    # A REAL SIGFPE CRASH, from the lab's dpw5 committee probe.  MUST-FLAG.
    "d12y_w3_fixture_REAL_SIGFPE_crash_excerpt.log": "8131701608d412c10460339a73e43795",
}
CLEAN_FIXTURES = ("d12y_w3_fixture_REAL_D12R2W3_S0.log",
                  "d12y_w3_fixture_REAL_D6R_ACC_excerpt.log")
CRASH_FIXTURE = "d12y_w3_fixture_REAL_SIGFPE_crash_excerpt.log"

# THE REAL BANNER LINE, verbatim.  This ONE LINE is what would have returned NOT A RESULT
# on W3's clean solve and burned ~558 core-min to say nothing.
REAL_BANNER_LINE = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)."

# FROZEN AT THE DRIVEN POPULATION, not guessed: this lane's first draft wrote 31 and the
# guard below REFUSED with rc=2 rather than accept a control whose population had silently
# changed.  The number is recorded here as the count the control actually drove.
EXPECTED_UNITS = 36

npass = nfail = 0


def unit(name, cond, detail=""):
    global npass, nfail
    if cond:
        npass += 1
        print("  [OK ] %s %s" % (name, detail))
    else:
        nfail += 1
        print("  [BAD] %s %s" % (name, detail))


def refuse(msg):
    print("REFUSE: %s" % msg)
    raise SystemExit(2)


# ======================================================================================
# 0.  EXTRACT THE LAUNCHER'S REAL SCAN AND EXECUTE IT.
#     Never a retyped copy: a control that carries its own copy of the thing it tests
#     tests the copy, and keeps passing after the launcher drifts.
# ======================================================================================
src = open(LAUNCHER, errors="replace").read()
m = re.search(r"^(?P<ind>[ \t]*)_FATAL = \[.*?^[ \t]*row\[\"fatal_benign_excluded\"\] = _benign\s*$",
              src, re.S | re.M)
if not m:
    refuse("could not extract the scan block from the launcher. A scan this control cannot "
           "find is a population it cannot test, and a clean zero over an empty population "
           "is exactly the false green this lab has been misled by three times.")
BLOCK = textwrap.dedent(m.group(0))

# ---- STRUCTURAL ASSERTIONS ON THE SHIPPING SOURCE -------------------------------------
# These are what stop a future edit from silently undoing the repair while this control
# keeps printing green.
unit("(s1) the scan block was EXTRACTED from the launcher, not retyped",
     len(BLOCK) > 400, "bytes=%d" % len(BLOCK))
unit("(s2) the scan is LINE-BY-LINE, not a whole-file substring search",
     "txt.splitlines()" in BLOCK and not re.search(r"re\.search\([^)]*,\s*txt\s*,", BLOCK),
     "(a revert to whole-file re-opens W3-LAUNCHER-DEF-2)")
unit("(s3) the FPE TOKEN IS STILL PRESENT -- not deleted",
     r'r"Floating point exception"' in BLOCK,
     "(deleting it would blind the scan to a real SIGFPE)")
unit("(s4) the `^` line anchor was NOT adopted on the FPE token",
     r'r"^Floating point exception"' not in BLOCK,
     "(OpenMPI's real report is not line-initial)")
unit("(s5) a benign-exclusion list exists and every exclusion is RECORDED",
     "_BENIGN" in BLOCK and "fatal_benign_excluded" in BLOCK,
     "(a suppression a reader cannot see is the same defect wearing the other hat)")

_ns = {"re": re, "txt": "", "row": {}}
exec(compile(BLOCK, "<launcher scan block>", "exec"), _ns)  # noqa: S102 -- the point
PATS = _ns["_FATAL"]
BENIGN = _ns["_BENIGN"]
unit("(s6) the exclusion list is NARROW BY CONSTRUCTION (exactly one entry)",
     len(BENIGN) == 1, "n_benign_patterns=%d" % len(BENIGN))
unit("(s7) enough patterns extracted to be a real population",
     len(PATS) >= 9, "n_patterns=%d" % len(PATS))
print("EXTRACTED %d fatal/signal patterns AND %d benign pattern(s) FROM THE LAUNCHER"
      % (len(PATS), len(BENIGN)))


def scan(txt):
    """Runs the LAUNCHER'S OWN extracted block over `txt`.  Returns (hits, benign)."""
    ns = {"re": re, "txt": txt, "row": {}}
    exec(compile(BLOCK, "<launcher scan block>", "exec"), ns)  # noqa: S102
    return ns["row"]["fatal_tokens"], ns["row"]["fatal_benign_excluded"]


# ======================================================================================
# 1.  FIXTURE INTEGRITY.  Registered md5s, checked before anything is concluded from them.
# ======================================================================================
TEXT = {}
for fn, want in FIXTURES.items():
    p = os.path.join(HERE, fn)
    if not os.path.isfile(p):
        refuse("fixture ABSENT: %s. A must-not-flag claim with no corpus is not evidence." % fn)
    raw = open(p, "rb").read()
    got = hashlib.md5(raw).hexdigest()
    if got != want:
        refuse("fixture DRIFTED: %s md5=%s registered=%s" % (fn, got, want))
    TEXT[fn] = raw.decode("utf-8", errors="replace")
unit("(f0) all %d real-corpus fixtures present and md5-identical to the registration"
     % len(FIXTURES), True, "")

CLEAN = "Time = 1\nCD: 0.65 average: 0.65\nExecutionTime = 1.2 s\nEnd\n"

# ======================================================================================
# 2.  MUST-NOT-FLAG -- against the REAL corpus.  THIS IS THE DIRECTION THE SUPERSEDED
#     CONTROL NEVER TESTED, and the direction W3 died in.
# ======================================================================================
h, b = scan(CLEAN)
unit("(a1) synthetic CLEAN log -> no tokens", h == [], "(the reader is not trigger-happy)")

h, b = scan(REAL_BANNER_LINE + "\n")
unit("(a2) THE REAL trapFpe BANNER LINE, VERBATIM -> ZERO hits",
     h == [] and len(b) == 1,
     "hits=%r benign_excluded=%d" % (h, len(b)))
unit("(a3) ... and the exclusion is RECORDED with its reason, not silent",
     len(b) == 1 and b[0]["line"] == 1 and "ENABLEMENT NOTICE" in b[0]["why"]
     and "Floating point exception" in b[0]["tokens"],
     "why=%r" % (b[0]["why"] if b else None))

for fn in CLEAN_FIXTURES:
    h, b = scan(TEXT[fn])
    n_fatal = TEXT[fn].count("FOAM FATAL")
    unit("(a4) REAL CLEAN LOG %-44s -> ZERO hits" % fn,
         h == [] and n_fatal == 0,
         "hits=%r benign_excluded=%d FOAM_FATAL=%d" % (h, len(b), n_fatal))
    unit("(a5) ... and it DID carry banner lines that the OLD scan flagged (%s)" % fn,
         len(b) >= 1,
         "benign_excluded=%d -- a zero here would mean the corpus proves nothing" % len(b))

# THE PLANTED ZERO, IN THE FORM THAT MATTERS: show the reader CAN see a non-zero on the
# very same real bytes.  A zero from a reader not shown able to see a non-zero is not
# evidence (standing rule 3).
for fn in CLEAN_FIXTURES:
    h, b = scan(TEXT[fn] + "--> FOAM FATAL ERROR:\n")
    unit("(a6) PLANT into the SAME real clean log %-22s -> CAUGHT" % fn,
         "FOAM FATAL ERROR" in h,
         "hits=%r (proves the zero above is a reading, not a blind spot)" % h)

# ======================================================================================
# 3.  MUST-FLAG -- every superseded fixture KEPT, plus the three real SIGFPE spellings.
#     Coverage is not reduced: (b0) refuses if any launcher pattern lacks a fixture.
# ======================================================================================
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
    "Foam::sigFpe::sigHandler": "Foam::sigFpe::sigHandler(int)\n",
}
undriven = [p for p in PATS if p not in PLANTS]
unit("(b0) EVERY launcher pattern has a planted fixture here (coverage not reduced)",
     not undriven, "" if not undriven else "UNDRIVEN: %r" % undriven)
for p in PATS:
    if p in PLANTS:
        h, b = scan(CLEAN + PLANTS[p])
        unit("(b) PLANTED %-28r -> CAUGHT" % p, p in h, "hits=%r" % h)

# ---- THE THREE REAL SIGFPE SPELLINGS, REQUIRED BY NAME --------------------------------
REAL_SIGFPE_FORMS = [
    ("stack-trace handler symbol", "Foam::sigFpe::sigHandler(int)\n"),
    ("shell report", "Floating point exception (core dumped)\n"),
    # NOT line-initial, and carrying no handler symbol.  `^Floating point exception`
    # would MISS this, which is why the `^` anchor was rejected.
    ("OpenMPI rank report",
     "mpirun noticed that process rank 2 exited on signal 8 (Floating point exception).\n"),
]
for what, txt in REAL_SIGFPE_FORMS:
    h, b = scan(CLEAN + txt)
    unit("(c) REAL SIGFPE FORM (%s) -> CAUGHT" % what, h != [], "hits=%r" % h)

# ---- A REAL CRASH LOG, REAL BYTES -----------------------------------------------------
h, b = scan(TEXT[CRASH_FIXTURE])
unit("(c4) A REAL SIGFPE CRASH LOG EXCERPT -> CAUGHT",
     h != [], "hits=%r" % h)

# ---- THE BANNER MUST NEVER SUPPRESS A CRASH IN THE SAME FILE --------------------------
# The exclusion is PER LINE, so a benign line 1 cannot cover a crash on line 400.
mixed = REAL_BANNER_LINE + "\n" + CLEAN + "Floating point exception (core dumped)\n"
h, b = scan(mixed)
unit("(c5) banner AND a real crash in ONE file -> STILL CAUGHT, banner still excluded",
     h != [] and len(b) == 1,
     "hits=%r benign_excluded=%d" % (h, len(b)))

h, b = scan(TEXT[CLEAN_FIXTURES[0]] + "Floating point exception (core dumped)\n")
unit("(c6) REAL clean log + a real crash appended -> CAUGHT (per-line, not whole-file)",
     "Floating point exception" in h, "hits=%r benign_excluded=%d" % (h, len(b)))

# ======================================================================================
# 4.  THE CONTROL ON THE CONTROL.
# ======================================================================================
PROSE = CLEAN + ("the solver handles the signal correctly, the error norm fell, and no "
                 "fatal condition was reached during this segment\n")
h, b = scan(PROSE)
unit("(d1) innocuous prose ('signal', 'error', 'fatal', 'segment') -> no tokens",
     h == [], "the patterns are anchored, not loose substrings")

# A DELIBERATELY WRONG BANNER must NOT be excluded: the exclusion is narrow, and a line
# that merely MENTIONS trapFpe mid-sentence is not the setup banner.
h, b = scan("the solver reported Floating point exception after trapFpe: was enabled\n")
unit("(d2) a NON-line-initial 'trapFpe:' does NOT buy an exclusion",
     h != [] and len(b) == 0,
     "hits=%r benign_excluded=%d (over-wide exclusion would hide crashes)" % (h, len(b)))

print("W3 FATAL-SCAN CONTROL pass=%d fail=%d units=%d expected=%d"
      % (npass, nfail, npass + nfail, EXPECTED_UNITS))
if npass + nfail != EXPECTED_UNITS:
    print("REFUSE: unit count %d != frozen EXPECTED_UNITS %d -- a control whose population "
          "silently changed is not the control that was registered."
          % (npass + nfail, EXPECTED_UNITS))
    raise SystemExit(2)
raise SystemExit(0 if nfail == 0 else 1)
PYEOF
