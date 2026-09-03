#!/usr/bin/env python3
"""EVIDENCE — is `analyse_t3_rff.py`'s UNFROZEN flag a scope artifact?  MEASURED: NO.

Written 2026-09-03 by a heat-transfer `lab-lane`.  An L-362-style flip
experiment: L-362 records a row moving UNFROZEN -> FROZEN once a SELFTEST-ONLY
occurrence of a case name was excised from a comparator's source, the name never
having been one the comparator read.  This probe asks whether T3's row is that
same shape.  IT IS NOT.

THIS SCRIPT GRADES NOTHING AND EDITS NOTHING.  It imports
`scripts/check_comparator_freeze.py` read-only and calls that instrument's own
`read_markers`, `scope_markers`, `earliest` and `sha_witness`.  Each variant is
written to a TEMP copy and scoped there; `analyse_t3_rff.py` is frozen and is
never modified, not even transiently (rule 6).

WHAT IT ESTABLISHES, and the numbers it returned on 2026-09-03:

  `"R_m"` / `"R_f"` occur in the comparator source in exactly two places --
    line  32   LADDER = {"c": "R_m", "m": "R_f", "f": "R_ff"}
    line 193   for c in ("R_m", "R_f"):        <- inside selftest(), forged
                                                  markers in a temp dir

    variant                          scope              earliest marker          margin      status
    A  baseline                      R_f, R_ff, R_m     DONE.R_m  08-24T15:58Z   -174586 s   UNFROZEN
    B  selftest occurrence excised   R_f, R_ff, R_m     DONE.R_m  08-24T15:58Z   -174586 s   UNFROZEN
    C  LADDER literal also broken    R_ff               DONE.R_ff 08-30T22:42Z   +368092 s   FROZEN

  B IS THE L-362 SHAPE AND IT DOES NOT MOVE THE MARGIN BY ONE SECOND.  The row
  flips only under C, which requires breaking line 32 -- and line 32 is not a
  spurious mention, it is the grader's ladder.  `analyse_t3_rff.py` genuinely
  grades the triple (R_m, R_f, R_ff).  Excising it would not remove a false
  scope term; it would remove two of the three cases the comparator grades.

  THE FLAG IS A TRUE POSITIVE.  The comparator was committed 2026-08-26T16:27:50Z
  with two of its three graded levels already complete and already published in
  `gate_t3.json` (2026-08-24).  Only `R_ff` was unknown at freeze.

  THE SHA-WITNESS ROUTE IS CHRONOLOGICALLY DEAD IN EVERY FORMAT.
  `check_comparator_freeze.py` greps the FULL sha256 of the disk bytes and can
  see neither a git blob sha1 nor a 16-hex truncation.  Measured:
    * disk sha256   e1aaf61b236fa72adb93a25e66f433584a95108947cb49c1e8969c4b28885997
    * `T3_R_FF_PREREGISTRATION.md` records only the 16-hex TRUNCATIONS
      (`44e3e2b8038b9274`, `e1aaf61b236fa72a`) -- the prefix matches disk, so
      byte-identity holds, but the instrument cannot see that form
    * the FULL blob sha1 appears in NO file at HEAD anywhere in the repository
      (it is recorded only in T3c_PREREGISTRATION.md, which is UNTRACKED)
    * sha_witness(...) returns (None, None)
  AND FORMAT IS NOT THE BINDING CONSTRAINT ANYWAY.  check_comparator_freeze.py
  line 422 requires the witness commit to PRECEDE the earliest in-scope marker
  (DONE.R_m, 2026-08-24T15:58Z).  `T3_R_FF_PREREGISTRATION.md` was first
  committed 2026-08-26T16:22:33Z.  A perfect full-sha256 witness recorded today
  would still be two days late.

  THE MTIME CAVEAT, CHECKED AND SURVIVED.  All eight ext1 markers were written
  within 356 MICROSECONDS of each other (DONE.R_c ....364540 -> DONE.O_m
  ....364896) and every one carries basis=mtime, not finished_utc -- the
  bulk-copy signature the instrument's own docstring warns about.  So the
  -174586 s MAGNITUDE is a filesystem artifact.  The SIGN is not: `R_f`'s field
  data is dated 2026-08-24T14:53Z, ahead even of the marking pass and two days
  ahead of the comparator commit.

Run from anywhere:  python3 probe_freeze_flip_t3_rff.py
"""
import hashlib, os, re, shutil, subprocess, sys, tempfile

REPO = "/home/ubuntu/Certonomous"
sys.path.insert(0, os.path.join(REPO, "scripts"))
import check_comparator_freeze as F  # instrument -- imported read-only

TREE = os.path.join(REPO, "verification/runs/T-family/T3_runs")
COMP = os.path.join(TREE, "analyse_t3_rff.py")
RELC = "verification/runs/T-family/T3_runs/analyse_t3_rff.py"


def main():
    src = open(COMP).read()
    disk_sha = hashlib.sha256(open(COMP, "rb").read()).hexdigest()
    print("disk sha256 of analyse_t3_rff.py = %s\n" % disk_sha)

    markers = F.read_markers(TREE)
    print("markers in tree: %s\n" % ", ".join(sorted(m["case"] for m in markers)))

    print('occurrences of "R_m" / "R_f" in the comparator source:')
    for i, line in enumerate(src.split("\n"), 1):
        if re.search(r'"R_[mf]"', line):
            print("  %4d  %s" % (i, line.strip()))
    print()

    variants = {
        "A_BASELINE": src,
        "B_SELFTEST_EXCISED": src.replace('for c in ("R_m", "R_f"):', 'for c in ():'),
        "C_LADDER_EXCISED": src.replace('for c in ("R_m", "R_f"):', 'for c in ():')
                               .replace('LADDER = {"c": "R_m", "m": "R_f", "f": "R_ff"}',
                                        'LADDER = {"c": "X1", "m": "X2", "f": "R_ff"}'),
    }

    _, iso, _ = F.git(REPO, "log", "-1", "--format=%cI", "--", RELC)
    ct = F.parse_utc(iso.strip())
    print("comparator last commit (git) = %s\n" % ct.isoformat())

    tmp = tempfile.mkdtemp(prefix="probe_flip_")
    try:
        for name, text in variants.items():
            p = os.path.join(tmp, "analyse_variant.py")
            open(p, "w").write(text)
            mine, _rule = F.scope_markers(p, markers)
            if not mine:
                print("%-20s scope EMPTY -> AMBIGUOUS-SCOPE\n" % name)
                continue
            mk = F.earliest(mine)
            margin = (mk["time"] - ct).total_seconds()
            status = "FROZEN" if ct < mk["time"] else "UNFROZEN"
            print("%-20s scope=%s" % (name, sorted(m["case"] for m in mine)))
            print("%-20s earliest in-scope marker %s @ %s (basis %s)"
                  % ("", mk["name"], mk["time"].isoformat(), mk["basis"]))
            print("%-20s margin = %+.0f s   -> %s\n" % ("", margin, status))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=== sha-witness probe (the instrument greps the FULL sha256 only) ===")
    w_iso, w_path = F.sha_witness(REPO, RELC, disk_sha)
    print("full-sha256 witness: %s  (%s)" % (w_iso, w_path))
    blob = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD:%s" % RELC],
                          capture_output=True, text=True).stdout.strip()
    for label, needle in (("git blob sha1", blob), ("sha256[:16]", disk_sha[:16])):
        _rc, out, _ = F.git(REPO, "grep", "-l", needle, "HEAD")
        print("%-14s %s -> at HEAD in: %s"
              % (label, needle, out.replace("HEAD:", "").split() or "NONE"))


if __name__ == "__main__":
    main()
