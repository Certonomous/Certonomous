#!/usr/bin/env python3
"""
D7 G8 TOKEN WRITER -- repair of `D7-LAUNCHER-DEF-1`, authorised by the
dafoam-supervisor under VERIFICATION_CHARTER.md sec.2d.1 at `f340e4d2`.

THE DEFECT.  `d7_run_arm.sh:214-216` gates colouring inheritance on
`test -f "$BASE/.d7_g8_pass"`, and its own comment at :213 says arm P1 writes
that token.  NOTHING WRITES IT -- all three occurrences of the name in the
launcher are the comment and the read.  Arm O therefore aborts at exit 5
unconditionally: the item cannot start at all.

WHAT THIS FILE DELIBERATELY DOES NOT DO.  It edits ZERO BYTES of any frozen
file.  It does not patch, monkey-patch, wrap or re-implement `d7_grade.py` or
`d7_run_arm.sh`.  It writes ONE artifact -- `.d7_g8_pass` -- and only when the
COMMITTED GRADER'S OWN `g8_decomp` says G8 passes.

NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.  G8 is unchanged; its result was
simply never recorded.  Every number below comes out of the committed blob.

THE THING THIS FILE EXISTS TO AVOID.  The token could be written by hand in one
command, and G8's evidence genuinely passes, so the hand-written token would
have recorded something TRUE -- and it would still have been forged, and the
next reader could not have told the difference.  The gate is therefore evaluated
HERE BY THE INSTRUMENT THAT OWNS IT, never by a lane's reading of a log.

CONTROLS.  Refuses (exit 2) rather than degrading, as the instruments it drives do.

  C1  `d7_grade.py` on disk must hash to its HEAD blob.  If the instrument is
      not the committed instrument, refuse.
  C2  `d7_run_arm.sh` on disk must hash to its HEAD blob AND to the md5
      registered in PREREGISTRATION.md Addendum 1 sec.A1.2.  The token means
      nothing if the launcher that reads it is not the frozen launcher.
  C3  The G8 evidence artifacts must exist and be read from DISK by the
      grader's own reader.
  C4  The bound `g8_decomp` must come from the committed module, not from this
      file -- asserted by module path.
  C5  The token is NEVER written unconditionally.  `--selftest` DEMONSTRATES the
      refusal path firing on a mutated decomposition map, because a control is
      not tested until something makes it FIRE.

USAGE
  python3 d7_g8_token.py --selftest      # exit 0 pass, 3 fail
  python3 d7_g8_token.py                 # evaluate G8 and write the token, or refuse
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "d7_grade.py")
LAUNCHER = os.path.join(HERE, "d7_run_arm.sh")

BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin"
G8_WORK = os.path.join(BASE, "P1")
TOKEN = os.path.join(BASE, ".d7_g8_pass")

# PREREGISTRATION.md Addendum 1 sec.A1.2 / Addendum 2 sec.A2.7
REGISTERED_LAUNCHER_MD5 = "c55b2cdeaf8a0975641b491b24912d63"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def head_blob_md5(relpath):
    """md5 of the file as COMMITTED, read from git, not from disk."""
    repo = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
    out = subprocess.run(["git", "-C", repo, "show", "HEAD:" + relpath],
                         capture_output=True)
    if out.returncode != 0:
        return None
    return hashlib.md5(out.stdout).hexdigest()


def refuse(msg, detail=None):
    sys.stderr.write("D7_G8_TOKEN REFUSED %s\n" % msg)
    if detail is not None:
        sys.stderr.write("  %s\n" % json.dumps(detail, sort_keys=True, default=str)[:800])
    sys.exit(2)


def load_grader():
    """Import the COMMITTED grader under a name that is not __main__, so its
    own entrypoint does not fire.  C4: the bound g8_decomp must come from it."""
    spec = importlib.util.spec_from_file_location("d7_grade_committed", GRADER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if os.path.abspath(mod.__file__) != os.path.abspath(GRADER):
        refuse("C4 -- g8_decomp did not come from the committed grader",
               {"bound_to": mod.__file__, "expected": GRADER})
    return mod


def check_hashes():
    rel_g = "cases/dafoam/ladder-a/A3/curriculum_D7/d7_grade.py"
    rel_l = "cases/dafoam/ladder-a/A3/curriculum_D7/d7_run_arm.sh"
    dg, dl = md5_of(GRADER), md5_of(LAUNCHER)
    hg, hl = head_blob_md5(rel_g), head_blob_md5(rel_l)
    if hg is None or hl is None:
        refuse("C1/C2 -- could not read the HEAD blobs; refusing rather than trusting disk")
    if dg != hg:
        refuse("C1 -- d7_grade.py on disk is NOT the committed instrument",
               {"disk": dg, "HEAD": hg})
    if dl != hl:
        refuse("C2 -- d7_run_arm.sh on disk is NOT the committed instrument",
               {"disk": dl, "HEAD": hl})
    if dl != REGISTERED_LAUNCHER_MD5:
        refuse("C2 -- launcher md5 does not match the md5 REGISTERED in Addendum 1",
               {"disk": dl, "registered": REGISTERED_LAUNCHER_MD5})
    return {"grade_md5": dg, "launcher_md5": dl}


def evaluate(mod, work):
    """C3: the grader's OWN g8_decomp, reading the artifacts from DISK."""
    for name in ("d7_decomp_A.json", "d7_decomp_B.json"):
        p = os.path.join(work, name)
        if not os.path.isfile(p):
            refuse("C3 -- G8 evidence artifact absent", {"missing": p})
    return mod.g8_decomp(work)


def selftest(mod):
    """C5.  THE REFUSAL PATH MUST BE SHOWN TO FIRE.  A control is not tested
    until something makes it fail."""
    units = []

    def unit(name, ok, note=""):
        units.append((name, bool(ok), note))

    tmp = tempfile.mkdtemp(prefix="d7g8st_")
    try:
        # POSITIVE: the real artifacts must pass.
        real = evaluate(mod, G8_WORK)
        unit("REAL_evidence_passes_G8", real["pass"],
             "identical=%s n=%d sum=%d" % (real["identical"],
                                           real["n_subdomains_A"], real["sum_cells_A"]))

        # NEGATIVE 1: a single differing cell must FAIL.
        w = os.path.join(tmp, "mutated"); os.makedirs(w)
        a = json.load(open(os.path.join(G8_WORK, "d7_decomp_A.json")))
        b = json.load(open(os.path.join(G8_WORK, "d7_decomp_B.json")))
        json.dump(a, open(os.path.join(w, "d7_decomp_A.json"), "w"))
        k = sorted(b)[0]; b2 = dict(b); b2[k] = b2[k] + 1
        json.dump(b2, open(os.path.join(w, "d7_decomp_B.json"), "w"))
        m1 = evaluate(mod, w)
        unit("ONE_DIFFERING_CELL_fails_G8", not m1["pass"],
             "identical=%s" % m1["identical"])

        # NEGATIVE 2: wrong subdomain count must FAIL.
        w2 = os.path.join(tmp, "nsub"); os.makedirs(w2)
        a3 = {k: v for k, v in list(a.items())[:3]}
        json.dump(a3, open(os.path.join(w2, "d7_decomp_A.json"), "w"))
        json.dump(a3, open(os.path.join(w2, "d7_decomp_B.json"), "w"))
        m2 = evaluate(mod, w2)
        unit("WRONG_SUBDOMAIN_COUNT_fails_G8", not m2["pass"],
             "n=%d" % m2["n_subdomains_A"])

        # NEGATIVE 3: cell sum not matching the registered 42,120 must FAIL.
        w3 = os.path.join(tmp, "ncells"); os.makedirs(w3)
        a4 = dict(a); a4[sorted(a4)[0]] = a4[sorted(a4)[0]] - 7
        json.dump(a4, open(os.path.join(w3, "d7_decomp_A.json"), "w"))
        json.dump(a4, open(os.path.join(w3, "d7_decomp_B.json"), "w"))
        m3 = evaluate(mod, w3)
        unit("CELL_SUM_NOT_REGISTERED_fails_G8", not m3["pass"],
             "sum=%d registered=%d" % (m3["sum_cells_A"], m3["ncells_registered"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, ok, _ in units if ok)
    print("D7_G8_TOKEN_SELFTEST units=%d passed=%d failed=%d"
          % (len(units), n_ok, len(units) - n_ok))
    for name, ok, note in units:
        print("  %-38s %s  %s" % (name, "ok    " if ok else "FAILED", note))
    return 0 if n_ok == len(units) else 3


def main():
    if "--selftest" in sys.argv[1:]:
        mod = load_grader()
        sys.exit(selftest(mod))

    h = check_hashes()
    mod = load_grader()
    r = evaluate(mod, G8_WORK)

    print("D7_G8_EVALUATED pass=%s identical=%s n_subdomains=%d sum_cells=%d registered=%d"
          % (r["pass"], r["identical"], r["n_subdomains_A"],
             r["sum_cells_A"], r["ncells_registered"]))
    print("  map_A=%s" % json.dumps(r["map_A"], sort_keys=True))
    print("  map_B=%s" % json.dumps(r["map_B"], sort_keys=True))

    if not r["pass"]:
        # C5: NEVER written unconditionally.
        refuse("G8 did NOT pass -- the token is not written", r)

    if os.path.exists(TOKEN):
        print("D7_G8_TOKEN already present at %s -- not rewritten" % TOKEN)
        sys.exit(0)

    with open(TOKEN, "w") as fh:
        json.dump({"gate": "G8", "pass": True,
                   "evaluated_by": "d7_grade.py g8_decomp (committed blob)",
                   "grade_md5": h["grade_md5"], "launcher_md5": h["launcher_md5"],
                   "work": G8_WORK, "map_A": r["map_A"], "map_B": r["map_B"],
                   "n_subdomains": r["n_subdomains_A"], "sum_cells": r["sum_cells_A"],
                   "authorised_by": "dafoam-supervisor ruling f340e4d2, "
                                    "VERIFICATION_CHARTER.md 2d.1"}, fh,
                  indent=1, sort_keys=True)
    print("D7_G8_TOKEN WRITTEN %s" % TOKEN)
    sys.exit(0)


if __name__ == "__main__":
    main()
