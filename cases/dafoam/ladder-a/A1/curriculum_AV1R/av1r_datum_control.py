#!/usr/bin/env python3
"""AV1R/AV2R DRIVEN CONTROL for the successor's age-guard datum resolution.

WHAT THIS IS.  A pre-compute diagnostic, not a grading path and not a comparator.  It
imports the SUCCESSOR GRADER'S OWN `resolve_datum_ref` and `read_write_compression` --
the two functions that are the whole successor delta -- and drives them against:

  (a) the REAL AV-1 and AV-2 run roots, whose frozen comparators refused at G1 with
      `age_reference_absent` on "0/U", to show the resolver sees the datum those runs
      actually left on disk; and
  (b) a PLANTED directory carrying NEITHER candidate, to show the resolver STILL REFUSES.

(b) is the point.  A guard relaxed without a control showing it can still fire is a guard
retired, not repaired (CLAUDE.md rule 3, applied to a guard rather than to a zero).

WHAT THIS IS NOT.  It reads no artefact, computes no gradient, quotes no band and reaches
no verdict.  AV-1 and AV-2 remain `NOT A RESULT` on their own frozen comparators; nothing
here grades them, and VERIFICATION_CHARTER.md sec.2d.1 was REFUSED for those items rather
than used.  This script exists so the successor's pre-registration can cite a DRIVEN
demonstration instead of an argument.

Usage:  av1r_datum_control.py --grader <path to avNr_grade.py> --root <run root>
                              --datum <.avN_age_datum> [--tmpdir DIR]
"""
import argparse
import importlib.util
import json
import os
import sys
import tempfile


def load(grader_path):
    spec = importlib.util.spec_from_file_location("succ_grader", grader_path)
    mod = importlib.util.module_from_spec(spec)
    sys.argv = [grader_path]                      # the grader parses argv only under main()
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grader", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--datum", required=True, help="the datum filename in that run root")
    ap.add_argument("--tmpdir", default="/tmp")
    a = ap.parse_args()
    g = load(a.grader)

    print("CONTROL grader=%s" % os.path.basename(a.grader))
    print("CONTROL root=%s" % a.root)
    seen_gz = 0
    seen_plain = 0
    rc = 0
    for arm in g.ARMS_REQUIRED:
        d = os.path.join(a.root, arm)
        if not os.path.isdir(d):
            print("  %-6s DIR ABSENT -- arm not present in this run root" % arm)
            continue
        dp = os.path.join(d, a.datum)
        rec = int(open(dp).read().strip()) if os.path.isfile(dp) else None
        own = int(os.path.getmtime(dp)) if os.path.isfile(dp) else None
        try:
            ref, name = g.resolve_datum_ref(d, arm)
        except g.Refusal as e:
            print("  %-6s RESOLVER REFUSED %s" % (arm, e))
            rc = 1
            continue
        m = int(os.path.getmtime(ref))
        seen_gz += name.endswith(".gz")
        seen_plain += not name.endswith(".gz")
        print("  %-6s resolved=%-12s ref_mtime=%s recorded=%s datumfile_mtime=%s "
              "self_delta=%s ref-datum=%+d writeCompression=%s"
              % (arm, name, m, rec, own, (own - rec) if rec is not None else "NA",
                 (m - rec) if rec is not None else 0, g.read_write_compression(d)))
        if rec is not None and m < rec:
            print("       ^ REFERENCE OLDER THAN DATUM -- the successor would refuse here")
            rc = 1
    print("CONTROL resolved_by_name_plain=%d resolved_by_name_gz=%d" % (seen_plain, seen_gz))

    # ---- the planted control: NEITHER candidate on disk MUST refuse -----------------
    tmp = tempfile.mkdtemp(prefix="datum_control_", dir=a.tmpdir)
    arm0 = [x for x in g.ARMS_REQUIRED if g.ARM_KIND[x] == "SOLVER"][0]
    empty = os.path.join(tmp, arm0)
    os.makedirs(os.path.join(empty, "0"))
    fired = False
    detail = None
    try:
        g.resolve_datum_ref(empty, arm0)
    except g.Refusal as e:
        fired = True
        detail = json.loads(str(e))["detail"]
    print("PLANTED CONTROL (neither candidate present, arm %s): guard_fired=%s key=%s"
          % (arm0, fired, ("age_reference_absent" in (detail or {}))))
    if not fired:
        print("CONTROL FAIL: the relaxed guard did NOT fire on an absent datum -- retired, not repaired")
        return 2
    # ---- and the positive half of the same control: plant 0/U.gz, it must be SEEN ---
    open(os.path.join(empty, "0", "U.gz"), "w").write("planted\n")
    ref, name = g.resolve_datum_ref(empty, arm0)
    print("PLANTED CONTROL (0/U.gz planted): resolver returns %s" % name)
    if name != "0/U.gz":
        print("CONTROL FAIL: the resolver cannot see a planted compressed datum")
        return 2
    print("CONTROL OK: the resolver sees a planted non-zero AND refuses an absent one")
    return rc


if __name__ == "__main__":
    sys.exit(main())
