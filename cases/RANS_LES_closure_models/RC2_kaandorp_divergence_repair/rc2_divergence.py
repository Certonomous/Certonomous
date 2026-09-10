#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RC2 HALF A -- the Kaandorp divergence-flag SUCCESSOR reader.

STATUS: DRAFT / UNFROZEN.  This file is NOT the freeze.  Standing rule 2 fixes the
grading path at the pre-registration commit; the freeze is the closure supervisor's
SUPERVISION_CHARTER.md section 3 check-4 act after a personal diff-read, and it is a
commit whose message carries the sha256 of PREREGISTRATION.md AND of both instruments
together.  Nothing may run against this file for a graded result before that commit.

WHAT THIS IS.  A SUCCESSOR to the DEFECTIVE frozen reader at
  cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/run_lane.py:175
which tests, in a line loop:
      if "Floating point exception" in line or "FOAM FATAL" in line:
          diverged = True
Both substrings are UNANCHORED.  OpenFOAM writes, at line 18 of every log this box
produces:
      trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
so the first predicate matches that safety notice on EVERY run, healthy or not.
`diverged` is a constant True, not a measurement (D548 shape; L-396 lesson).  Measured
on the 16 preserved Kaandorp logs at drafting: banner present on 16/16, genuine fatal
signature on 0/16, clean `End` on 16/16 -- the frozen reader reads `diverged=True` on
all 16 and every one is false in fact.

run_lane.py IS NOT EDITED BY THIS ITEM (PREREGISTRATION.md section 1.5; rules 2 and 6).
This is a successor module, exactly as G1->G1b and R4b-I->R4b-Ib.

THE REPAIR.  The successor's pattern is the lab's OWN verified precedent, invented
nowhere here and selected against no answer:
  * the FOAM-ERROR channel of sdk/chief_engineer/mesh_certificate.py:123 (`_FATAL`), and
  * the LINE-ANCHORED FPE channel of sdk/chief_engineer/head_engineer.py:188,
the same pair grade_g2.py:129 (`FATAL_RE`) and grade_g1b.py's `RE_FATAL` were built
from.  ANCHORING is what defeats the banner: the banner's phrase is preceded by
`trapFpe: ` and so never begins its line.  Neither `trapFpe:` nor `trapping enabled`
appears in any channel.

CONTROLS (PREREGISTRATION.md section 6), every one a `raise`/`sys.exit(2)`, no assert:
  6.1  two-direction planted control ON REAL NAMED LOGS -- 6 real fatals it MUST flag,
       16 real banner-only Kaandorp logs it MUST NOT (the gate; refuses both ways)
  6.2  the BLIND control -- the FROZEN line-loop predicate reinstated, must read fatal
       on all 16 banner-only logs (else the corpus is not the defect's corpus)
  6.5  L-332 -- every refusal is a raise/exit; the module parses its OWN AST and
       refuses if a single ast.Assert node exists, after the counter is shown able to
       count a planted assert.
Green under python3 AND python3 -O, __pycache__ cleared before each.

IMPORTABLE.  `read_fatal(text)` is the successor predicate, exposed so a fifth call
site has something to import (PREREGISTRATION.md section 10.7; rule 14 disclosure: this
is the fourth independent copy of a correct predicate, and RC2 says so rather than
pretending it closes D548).
"""

import argparse
import ast
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------
# Refusal.  L-332: NO assert may carry a refusal, guard, control or gate --
# python3 -O deletes every assert.  Every refusal below is a raise or sys.exit(2).
# --------------------------------------------------------------------------
class Refusal(Exception):
    """A condition that must stop this instrument under ANY interpreter flag."""


def refuse(msg):
    raise Refusal(msg)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# THE SUCCESSOR PREDICATE.  Byte-for-byte the lab's established FATAL_RE
# (grade_g2.py:129); five channels, all line-anchored where the shell/banner
# would otherwise slip a false match in:
#   (1) a genuine FOAM error header, with or without ` IO`, at any MPI rank prefix
#   (2) the library's own exit line
#   (3) a signal handler that actually FIRED (sigFpe, sigSegv, sigInt, ...)
#   (4) a stack trace being printed
#   (5) a message the SHELL wrote, which always begins the line it is on
# `trapping enabled` appears in none of them.
# --------------------------------------------------------------------------
FATAL_RE = re.compile(
    r"-->\s*FOAM FATAL(?:\s+IO)?\s+ERROR"
    r"|FOAM exiting"
    r"|Foam::sig\w+::sigHandler"
    r"|Foam::error::printStack"
    r"|^(?:Floating point exception|Segmentation fault)",
    re.MULTILINE)

# OpenFOAM's startup banner, VERBATIM from a real log on this box.  The negative
# direction of the control is defined by the fact that this line -- and nothing
# else fatal-looking -- is what the 16 Kaandorp logs carry.
FPE_BANNER = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n"


def read_fatal(text):
    """The successor: True iff `text` carries a genuine fatal signature.

    Importable.  This is the predicate the re-grade calls per log, and the one a
    fifth call site should import rather than re-copy (rule 14)."""
    return bool(FATAL_RE.search(text))


def read_fatal_frozen_lineloop(text):
    """THE FROZEN DEFECT, reinstated verbatim for the BLIND control (section 6.2)
    and for NOTHING else.  This is run_lane.py:175 exactly -- a line loop over an
    UNANCHORED substring test.  It MUST read fatal on the 16 banner-only logs, or
    the corpus handed to the control is not the corpus the defect lives on.

    Reproduced here, never imported from the frozen file, so the frozen file is
    not touched (rules 2, 6)."""
    for line in text.splitlines(keepends=True):
        if "Floating point exception" in line or "FOAM FATAL" in line:
            return True
    return False


# --------------------------------------------------------------------------
# THE CORPUS -- named file by file (PREREGISTRATION.md sections 3.2, 5.2), each
# verified present and each verified to carry the stated signature at drafting.
# Absolute paths: the reader's control corpus is fixed and does not depend on cwd.
# --------------------------------------------------------------------------
_KRUN = "/home/ubuntu/closure-data/aposteriori/kaandorp"

# NEGATIVE corpus: the 16 preserved Kaandorp logs the frozen reader gets wrong.
# The successor MUST read NOT-fatal on every one; the frozen predicate MUST read
# fatal on every one.
NEG_CORPUS = [
    "AR_1_Ret_360__NULL", "AR_1_Ret_360__TRUTH", "AR_1_Ret_360__MEANB",
    "AR_1_Ret_360__ML0", "AR_1_Ret_360__ML1", "AR_1_Ret_360__ML2",
    "AR_1_Ret_360__MEANB64", "AR_3_Ret_360__NULL", "AR_3_Ret_360__TRUTH",
    "AR_3_Ret_360__MEANB", "CBFS13700__NULL", "CBFS13700__TRUTH",
    "CBFS13700__MEANB", "CBFS13700__ML0", "CBFS13700__ML1", "CBFS13700__ML2",
]

def neg_log_path(case):
    return os.path.join(_KRUN, case, "log.run")

# POSITIVE corpus: six named real fatal logs from ELSEWHERE on this box.  Forced,
# not chosen -- not one of the 16 Kaandorp logs holds a genuine fatal, so the
# positive direction cannot be demonstrated on this case's own artifacts.  The
# three distinct signature classes must all be represented.
POS_CORPUS = [
    ("/home/ubuntu/closure-data/hump_gate/G0a_shipped/log.run", "FOAM FATAL IO ERROR"),
    ("/home/ubuntu/certonomous-runs/adjwall/HUMP51k/log.run", "FOAM FATAL ERROR"),
    ("/home/ubuntu/certonomous-runs/adjwall/N100k/log.run", "FOAM FATAL ERROR"),
    ("/home/ubuntu/certonomous-runs/adjwall/A1_4032/log.run", "FOAM FATAL ERROR"),
    ("/home/ubuntu/Certonomous/verification/runs/DPW8_V2_runs/"
     "run_L4_diagA_relax/log.simpleFoam", "Foam::sigFpe::sigHandler"),
    ("/home/ubuntu/certonomous-runs/S1-cbfs-inversion/log.calib", "FOAM FATAL ERROR"),
]


def _read_text(path):
    if not os.path.isfile(path):
        refuse("CORPUS: named real log absent on disk: %s -- the control cannot be "
               "demonstrated on an artifact that is not there (section 5.2)" % path)
    with open(path, "r", errors="replace") as f:
        return f.read()


# --------------------------------------------------------------------------
# L-332 CONTROL -- section 6.5.
# --------------------------------------------------------------------------
def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def no_assert_control():
    planted = count_asserts("def f(x):\n    assert x, 'planted'\n    return x\n")
    if planted != 1:
        refuse("AST-CONTROL: the counter returned %d on a snippet holding exactly one "
               "assert; its zero here would be a blind spot, not a reading." % planted)
    own = count_asserts(Path(__file__).read_text())
    if own != 0:
        refuse("AST-CONTROL: this module holds %d ast.Assert node(s); python3 -O "
               "deletes every one (L-332)." % own)
    return planted, own


# --------------------------------------------------------------------------
# 6.1 + 6.2 -- the two-direction control ON REAL LOGS, plus the blind mirror.
# This is the GATE (section 5.1 clause 1): if it does not fire in BOTH directions
# on real logs, the reader grades NOTHING and this module exits 2.
# --------------------------------------------------------------------------
def planted_control_fatal_real():
    """Standing rule 3 for the FATAL reader, in BOTH directions, on REAL producer
    logs named in section 5.2 -- not synthetic strings (Sanaa 2026-08-28: a control
    that writes a schema the producer never emits certifies blindness).

    Returns a dict of the readings; refuses (Refusal) on any disagreement.
    """
    report = {"positive": [], "negative": [], "blind": []}

    # POSITIVE: the successor MUST read fatal on all six, and all three signature
    # classes must be represented.
    classes_seen = set()
    for path, sig in POS_CORPUS:
        text = _read_text(path)
        got = read_fatal(text)
        if not got:
            refuse("PLANT fatal(+): the successor read NOT-fatal on %s, which carries "
                   "%r -- the reader cannot see the failure it exists to see" % (path, sig))
        classes_seen.add(sig if "IO" not in sig and "sigFpe" not in sig else sig)
        report["positive"].append((path, sig, got))
    class_keys = set()
    for _, sig in POS_CORPUS:
        if "IO" in sig:
            class_keys.add("FOAM_FATAL_IO")
        elif "sigFpe" in sig or "sigHandler" in sig:
            class_keys.add("SIGFPE")
        else:
            class_keys.add("FOAM_FATAL")
    if class_keys != {"FOAM_FATAL", "FOAM_FATAL_IO", "SIGFPE"}:
        refuse("PLANT fatal(+): the positive corpus does not represent all three "
               "signature classes; represented=%s" % sorted(class_keys))

    # NEGATIVE: the successor MUST read NOT-fatal on all 16 banner-only logs; each
    # must carry the banner verbatim and a clean End (else the negative direction
    # proves nothing).  MIRROR: the frozen predicate MUST read fatal on the same 16.
    for case in NEG_CORPUS:
        path = neg_log_path(case)
        text = _read_text(path)
        if FPE_BANNER not in text:
            refuse("PLANT fatal(-): %s does not carry OpenFOAM's trapFpe banner "
                   "verbatim; it is not an artifact the defect lives on" % path)
        if "\nEnd\n" not in text and not text.rstrip().endswith("End"):
            refuse("PLANT fatal(-): %s carries no clean `End`; the negative corpus is "
                   "meant to be clean runs the frozen reader wrongly flagged" % path)
        succ = read_fatal(text)
        if succ:
            refuse("PLANT fatal(-): the successor read FATAL on %s, whose only "
                   "fatal-looking text is the trapFpe banner -- a detector that cannot "
                   "return NOT-fatal is a constant (L-396)" % path)
        # 6.2 THE BLIND CONTROL -- the frozen predicate, reinstated for exactly this
        # comparison, MUST fire on the same log.  If it does not, this is not the
        # defect's corpus and the control refuses.
        frozen = read_fatal_frozen_lineloop(text)
        if not frozen:
            refuse("BLIND CONTROL: the FROZEN run_lane.py:175 predicate read NOT-fatal "
                   "on %s -- but the defect IS that it fires on the banner. If it is "
                   "silent here the corpus is not the corpus the defect lives on" % path)
        report["negative"].append((case, path, succ))
        report["blind"].append((case, path, frozen))

    return report


# --------------------------------------------------------------------------
# A SUPPLEMENTARY planted-token control (rule 3 in its plant-and-read-back shape).
# It plants a GENUINE producer-written FOAM FATAL block into a COPY of a real
# clean Kaandorp log in a TemporaryDirectory (the real file is never touched),
# reads it back, and refuses if (a) the reader cannot see the planted token, or
# (b) the reader reports it on the UNPLANTED copy.  This is the boolean-detector
# analog of the L-508 PLANT read-back; there is NO numeric field in RC2's read
# path, so the numeric PLANT=1.234e-3 magnitude control is not applicable -- the
# thing planted here is the fatal token, and the read-back is exact (present/absent).
# --------------------------------------------------------------------------
PLANT_FATAL_BLOCK = (
    "--> FOAM FATAL ERROR: (planted-control-1.234e-03)\n"
    "    Maximum number of iterations exceeded\n"
    "    From function void Foam::PBiCGStab::solve(...)\n"
    "    in file lduMatrix/solvers/PBiCGStab/PBiCGStab.C at line 193.\n\n"
    "FOAM exiting\n")


def planted_token_control():
    donor = neg_log_path("CBFS13700__NULL")  # smallest of the 16 (897,986 B)
    clean = _read_text(donor)
    if read_fatal(clean):
        refuse("PLANT token(pre): the donor clean log %s already reads fatal; the "
               "plant/no-plant contrast would prove nothing" % donor)
    with tempfile.TemporaryDirectory(prefix="rc2plant_") as td:
        planted_path = Path(td) / "planted.run"
        unplanted_path = Path(td) / "unplanted.run"
        planted_path.write_text(clean + PLANT_FATAL_BLOCK)
        unplanted_path.write_text(clean)
        # the token must be on disk in the file the reader is handed
        if PLANT_FATAL_BLOCK not in planted_path.read_text():
            refuse("PLANT token: the block is not in the file ON DISK the reader was "
                   "handed; the read-back would prove nothing")
        if not read_fatal(planted_path.read_text()):
            refuse("PLANT token: a genuine planted `--> FOAM FATAL ERROR ... FOAM "
                   "exiting` block was read as NOT-fatal; the reader cannot see a "
                   "failure it is asked to report")
        # INVERSE: the same reader on the unplanted copy must be silent
        if read_fatal(unplanted_path.read_text()):
            refuse("PLANT token(inv): the reader reports fatal on the UNPLANTED copy "
                   "of a clean log; it is a constant, not a reader")
    return True


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def selftest():
    planted, own = no_assert_control()
    print("[L-332] planted-assert counter = %d (must be 1); own ast.Assert nodes = %d "
          "(must be 0)  OK" % (planted, own))

    rep = planted_control_fatal_real()
    print("[6.1 +] successor read FATAL on all %d named real fatals; 3/3 signature "
          "classes represented  OK" % len(rep["positive"]))
    print("[6.1 -] successor read NOT-fatal on all %d banner-only Kaandorp logs  OK"
          % len(rep["negative"]))
    print("[6.2 blind] FROZEN run_lane.py:175 predicate read FATAL on all %d banner-only "
          "logs (the defect reproduces on the very corpus)  OK" % len(rep["blind"]))

    planted_token_control()
    print("[plant] genuine FOAM FATAL block planted into a temp copy of a real clean "
          "log: successor SEES it, and is SILENT on the unplanted copy  OK")

    print("SELFTEST PASS: successor birth demonstrated in both directions on 22 real "
          "named logs; blind mirror fires; no ast.Assert; green target python3 and -O.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="RC2 successor divergence-flag reader (DRAFT/UNFROZEN)")
    ap.add_argument("--selftest", action="store_true",
                    help="run every control on the named real logs and exit 0 iff all pass")
    ap.add_argument("--read", metavar="LOG",
                    help="print JSON {fatal: bool} for one log through the successor")
    args = ap.parse_args(argv)
    try:
        if args.read:
            import json
            print(json.dumps({"fatal": read_fatal(_read_text(args.read)), "log": args.read}))
            return 0
        if args.selftest:
            return selftest()
        ap.print_help()
        return 0
    except Refusal as e:
        sys.stderr.write("REFUSE (exit 2): %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
