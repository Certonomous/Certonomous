#!/usr/bin/env python3
"""SO-2a C5 trapFpe CONFIRMATION, driven on a REAL log.

Reads so2a_grade.py's FROZEN bytes (no edit, no copy-with-changes), imports it,
and drives fatal_token_sites() against
/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/ACC_mp_20260829T015422Z_2086625.log
-- a clean multipoint run with no FPE.

Four limbs, all DRIVEN, none asserted:
  (1) THE UNREPAIRED FORM (SO-1a's shape: `[t for t in FATAL_TOKENS if t in text]`
      over the WHOLE FILE) is reconstructed here and shown FIRING on that log --
      the planted positive that makes limb (2)'s zero a claim about the code.
  (1b) the LINE NUMBERS of the bare-token hits, so the supervisor's measurement
      (lines 62, 749, 1432) is checked rather than repeated.
  (2) the REPAIRED form returns ZERO non-benign sites on the SAME bytes, and the
      benign lines it excluded are named with their reason.
  (3) a REAL SIGFPE is still CAUGHT: the OpenFOAM handler symbol, and OpenMPI's
      NON-LINE-INITIAL `process rank 2 exited on signal 8 (Floating point
      exception).` -- the report an `^`-anchored fix would MISS.
  (4) the token is STILL IN FATAL_TOKENS: what was removed is the whole-file
      substring scan, never the token.
"""
import importlib.util
import os
import sys

CASE = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO2a"
GRADER = os.path.join(CASE, "so2a_grade.py")
REAL_LOG = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/"
            "ACC_mp_20260829T015422Z_2086625.log")

spec = importlib.util.spec_from_file_location("so2a_grade_probe", GRADER)
G = importlib.util.module_from_spec(spec)
sys.modules["so2a_grade_probe"] = G
spec.loader.exec_module(G)

PASS = 0
FAIL = 0


def ok(msg):
    global PASS
    PASS += 1
    print("  [OK ] %s" % msg)


def bad(msg):
    global FAIL
    FAIL += 1
    print("  [BAD] %s" % msg)


import subprocess
md5 = subprocess.run(["md5sum", GRADER], capture_output=True, text=True).stdout.split()[0]
stamp = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True,
                       text=True).stdout.strip()
print("SO2a C5 trapFpe CONFIRMATION %s grader_md5=%s" % (stamp, md5))
print("  real log: %s (%d bytes, %d lines)"
      % (REAL_LOG, os.path.getsize(REAL_LOG),
         len(open(REAL_LOG, errors="replace").read().splitlines())))

text = open(REAL_LOG, errors="replace").read()

# ---- (1) THE UNREPAIRED FORM, reconstructed, shown FIRING -------------------
# This is SO-1a's shape at so1a_grade.py:122-125 -- a whole-file substring test.
unrepaired = [t for t in G.FATAL_TOKENS if t in text]
if unrepaired:
    ok("(1) the UNREPAIRED whole-file substring form FIRES on this clean log: %s "
       "-- the planted positive that makes limb (2)'s zero evidence" % (sorted(unrepaired),))
else:
    bad("(1) the unrepaired form did NOT fire -- limb (2)'s zero would be a claim "
        "about the LOG, not about the code")

# ---- (1b) the bare token's LINE NUMBERS, checked not repeated ---------------
bare_lines = [i for i, ln in enumerate(text.splitlines(), 1)
              if "Floating point exception" in ln]
EXPECT = [62, 749, 1432]
if bare_lines == EXPECT:
    ok("(1b) the bare token 'Floating point exception' hits %d times, at lines %s "
       "-- the supervisor's measurement reproduced exactly"
       % (len(bare_lines), bare_lines))
else:
    bad("(1b) bare-token lines %s, supervisor's reading was %s" % (bare_lines, EXPECT))
for i in bare_lines:
    print("        line %d: %s" % (i, text.splitlines()[i - 1].strip()[:110]))

# ---- (2) THE REPAIRED FORM: ZERO non-benign sites on the SAME bytes ---------
sites, benign = G.fatal_token_sites(text, REAL_LOG)
if not sites:
    ok("(2) the REPAIRED fatal_token_sites() returns ZERO non-benign sites on the "
       "real log -- a clean run is read as clean")
else:
    bad("(2) repaired form returned %d site(s): %s" % (len(sites), sites[:3]))
if len(benign) == len(bare_lines) and all(b["line"] in bare_lines for b in benign):
    ok("(2b) all %d hits were classified BENIGN and each is NAMED with its reason, "
       "not silently dropped: %s" % (len(benign), benign[0]["why_benign"]))
else:
    bad("(2b) benign count %d against %d bare-token lines" % (len(benign), len(bare_lines)))

# ---- (3) A REAL SIGFPE IS STILL CAUGHT --------------------------------------
handler = text + "\n#1  Foam::sigFpe::sigHandler(int) at ??:?\n"
s3a, _ = G.fatal_token_sites(handler, "PLANT_handler")
if len(s3a) == 1 and "Foam::sigFpe::sigHandler" in s3a[0]["tokens"]:
    ok("(3a) OpenFOAM's FPE HANDLER SYMBOL planted into the same clean log -> "
       "CAUGHT, 1 site at line %d" % s3a[0]["line"])
else:
    bad("(3a) handler symbol not caught: %s" % (s3a,))

mpi = text + ("\nprimary job  terminated: process rank 2 exited on signal 8 "
              "(Floating point exception).\n")
s3b, _ = G.fatal_token_sites(mpi, "PLANT_openmpi")
if len(s3b) == 1 and "Floating point exception" in s3b[0]["tokens"]:
    ok("(3b) OpenMPI's NON-LINE-INITIAL report -- 'process rank 2 exited on signal 8 "
       "(Floating point exception).' -- CAUGHT, 1 site at line %d.  An '^'-anchored "
       "fix would MISS this, which is why the benign pattern anchors the BANNER and "
       "not the token" % s3b[0]["line"])
else:
    bad("(3b) OpenMPI signal-8 report not caught: %s" % (s3b,))

# every other token, driven one at a time, on the same real bytes
missed = [t for t in G.FATAL_TOKENS
          if len(G.fatal_token_sites(text + "\nxx %s yy\n" % t, "P")[0]) != 1]
if not missed:
    ok("(3c) EVERY one of the %d registered tokens, planted in turn into the real "
       "log, produces exactly one site -- the repair narrowed nothing but the banner"
       % len(G.FATAL_TOKENS))
else:
    bad("(3c) tokens planted and NOT caught: %s" % (missed,))

# and the banner itself, planted, is still benign and still the ONLY exclusion
banner = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n"
s4, b4 = G.fatal_token_sites(text + banner, "PLANT_banner")
if not s4 and len(b4) == len(bare_lines) + 1:
    ok("(3d) the banner planted a fourth time is still read as an ENABLEMENT NOTICE "
       "(%d benign, 0 sites)" % len(b4))
else:
    bad("(3d) banner leg: %d sites, %d benign" % (len(s4), len(b4)))

# ---- (4) THE TOKEN STAYS -----------------------------------------------------
if "Floating point exception" in G.FATAL_TOKENS and \
        "Foam::sigFpe::sigHandler" in G.FATAL_TOKENS:
    ok("(4) the token STAYS: 'Floating point exception' and 'Foam::sigFpe::sigHandler' "
       "are both still in FATAL_TOKENS -- what was removed is the WHOLE-FILE SCAN")
else:
    bad("(4) a registered token is missing from FATAL_TOKENS")
if len(G.BENIGN_LINE_PATTERNS) == 1 and G.BENIGN_LINE_PATTERNS[0][0] == r"^\s*trapFpe:\s":
    ok("(4b) EXACTLY ONE benign exclusion is registered and it anchors the trapFpe "
       "BANNER PREFIX, not the token")
else:
    bad("(4b) benign exclusions: %s" % (G.BENIGN_LINE_PATTERNS,))

# ---- the AST detector, both directions, on the REAL files --------------------
own = G.whole_file_token_scan_sites(GRADER)
anc = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO1a/so1a_grade.py"
if own == []:
    ok("(5) the AST detector finds ZERO whole-file token scans in so2a_grade.py")
else:
    bad("(5) whole-file token scan sites in so2a_grade.py: %s" % (own,))
if os.path.isfile(anc):
    got = G.whole_file_token_scan_sites(anc)
    if got == ["fatal_tokens_in"]:
        ok("(5b) THE SAME DETECTOR, run on SO-1a's frozen grader, FLAGS "
           "'fatal_tokens_in' -- so limb (5)'s zero is a claim about the CODE, "
           "not about the pattern (L-400)")
    else:
        bad("(5b) detector on SO-1a returned %s, expected ['fatal_tokens_in']" % (got,))
else:
    bad("(5b) SO-1a's grader is absent; the detector's known positive cannot be driven")

print("SO2a C5 trapFpe CONFIRMATION pass=%d fail=%d %s"
      % (PASS, FAIL,
         subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                        capture_output=True, text=True).stdout.strip()))
sys.exit(0 if FAIL == 0 else 1)
