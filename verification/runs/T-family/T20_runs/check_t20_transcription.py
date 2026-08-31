#!/usr/bin/env python3
"""REFUSE unless T20_registered.json's transcribed cases are byte-equal to the
prose-frozen values in T20_prose_cases_7b93b2c8.json, and unless every condition
of DEAD_LEVER_AUDIT.md section 24.4 holds.

THIS COMPARATOR REFUSES; IT DOES NOT REPORT.  Any mismatch exits 2.  A printed
warning that lets a bad transcription stand would certify nothing -- section
24.4(c) is explicit that the check must refuse.

WHAT IS CHECKED, one condition per limb, all of them from section 24.4:

  (a) EVERY field of every transcribed case is either TRANSCRIBED (carries a
      `*_source_section` citation) or DERIVED (carries a `*_derivation` naming
      its rule), following the schema pattern that `T20_LC_c` already sets.  A
      field that is neither is new registration content post-compute and is
      FORBIDDEN.  The field->evidence map below is derived from `T20_LC_c`'s own
      entry, which section 24.3 names as the worked example.
  (b) `timeout_s` is DERIVED by ONE rule for every case:
      `cap_core_min * 60 / ranks`.  THE RULE MAY NOT VARY BY CASE.
  (c) this file's own refusal behaviour, exercised by --selftest.
  (e) SEVEN IS THE CEILING: `cases` may never exceed seven entries, and no case
      may appear that is absent from S11.2's table.

NON-BLIND DISCLOSURE.  T20's gated grading is NO LONGER ANALYST-BLIND: its
pre-registered predictions have been read, including by the lane that wrote this
file.  The bands were frozen at `7b93b2c8` BEFORE any of that, so rule 2's
evidentiary content -- that the gate could not have been chosen to fit the answer
-- survives intact.  The declaration is here, at the top, because a disclosure in
a closing paragraph is one a reader can miss.

usage: check_t20_transcription.py            # exits 0 or 2
       check_t20_transcription.py --selftest # both planted control limbs
"""
import argparse
import ast
import json
import os
import shutil
import sys
import tempfile

SELF = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(SELF, "T20_registered.json")
PROSE = os.path.join(SELF, "T20_prose_cases_7b93b2c8.json")
EXIT_REFUSE = 2

# S11.2's seven rows.  Section 24.4(e): nothing outside this set, ever.
S11_2_ROWS = {"T20_LC_c", "T20_LC_m", "T20_LC_f", "T20_LC_Sc",
              "T20_LC_Sf", "T20_LC_D", "T20_LC_P10"}
CEILING = 7

# Condition (a).  Every case field must appear here, mapped to the field that
# carries its evidence.  Taken from T20_LC_c's own entry (section 24.3's worked
# example), NOT invented: the five *_source_section keys and the one
# *_derivation key are exactly the ones that entry already uses.
EVIDENCE = {
    "role":                     None,                  # prose label, carried with graded_source_section
    "nx":                       "mesh_source_section",
    "ny":                       "mesh_source_section",
    "nz":                       "mesh_source_section",
    "cells":                    "mesh_source_section",
    "deltaT":                   "ladder_source_section",
    "endTime":                  "ladder_source_section",
    "steps":                    "executiontime_source_section",
    "executiontime_expected":   "executiontime_source_section",
    "point_core_min":           "cost_source_section",
    "cap_core_min":             "cost_source_section",
    "timeout_s":                "timeout_derivation",
    "graded":                   "graded_source_section",
}
EVIDENCE_KEYS = {"mesh_source_section", "ladder_source_section",
                 "executiontime_source_section", "cost_source_section",
                 "graded_source_section", "timeout_derivation"}


def fail(msgs):
    for m in msgs:
        sys.stderr.write("REFUSE: %s\n" % m)
    sys.stderr.write("REFUSE (exit %d): the transcription is NOT certified.\n"
                     % EXIT_REFUSE)
    return EXIT_REFUSE


def check(reg_path=REG, prose_path=PROSE, ranks=None):
    """Returns (rc, messages).  rc 0 = certified, 2 = refused."""
    bad = []
    reg = json.load(open(reg_path))
    prose = json.load(open(prose_path))
    if ranks is None:
        ranks = reg["ranks"]
    rcases, pcases = reg["cases"], prose["cases"]

    # (e) ceiling and membership
    if len(rcases) > CEILING:
        bad.append("cases has %d entries; section 24.4(e) ceiling is %d"
                   % (len(rcases), CEILING))
    for k in rcases:
        if k not in S11_2_ROWS:
            bad.append("%s is NOT a row of S11.2's table; 24.4(e) bars it by this "
                       "route, ever" % k)

    for case, pv in sorted(pcases.items()):
        if case not in rcases:
            bad.append("%s is in the prose file but NOT transcribed into %s"
                       % (case, os.path.basename(reg_path)))
            continue
        rv = rcases[case]

        # byte-equality of every prose-carried field
        for k, want in sorted(pv.items()):
            if k not in rv:
                bad.append("%s.%s missing from the registration" % (case, k))
            elif rv[k] != want:
                bad.append("%s.%s MISTRANSCRIBED: registration has %r, prose has %r"
                           % (case, k, rv[k], want))

        # (a) every field is transcribed-with-citation or derived-with-rule
        for k in sorted(rv):
            if k in EVIDENCE_KEYS:
                continue
            if k not in EVIDENCE:
                bad.append("%s.%s is NEITHER transcribed nor derived -- it is new "
                           "registration content post-compute (24.4(a))" % (case, k))
                continue
            ev = EVIDENCE[k]
            if ev is not None and not str(rv.get(ev, "")).strip():
                bad.append("%s.%s carries no evidence: %s is absent or empty "
                           "(24.4(a))" % (case, k, ev))

        # (b) the ONE timeout rule, identical for every case
        if "cap_core_min" in rv and "timeout_s" in rv:
            want_t = rv["cap_core_min"] * 60.0 / ranks
            if float(rv["timeout_s"]) != want_t:
                bad.append("%s.timeout_s = %s but the single registered rule "
                           "cap_core_min x 60 / ranks gives %g -- 24.4(b) forbids a "
                           "per-case rule" % (case, rv["timeout_s"], want_t))
    return (EXIT_REFUSE if bad else 0), bad


# --------------------------------------------------------------------------
# PLANTED CONTROL, BOTH LIMBS (rule 3; section 24.4(c); section 2j.2).
#
# 2j.2: THE BYTES THE CONTROL READS MUST BE WRITTEN BY THE REAL PRODUCER, NOT BY
# THE CONTROL.  So both limbs run against a COPY of the real, transcribed
# T20_registered.json -- the file the transcription actually produced -- and the
# corruption is applied to that copy.  The control never authors a registration.
#
# No limb touches a live run tree (T20 S8; and analyse_t18.py:509 /
# analyse_t19.py:691 both inverted on 2026-08-31 for doing exactly that).
# --------------------------------------------------------------------------
def selftest():
    fails = []

    def ok(cond, label):
        print("  [%s] %s" % ("ok " if cond else "FAIL", label))
        if not cond:
            fails.append(label)

    tmp = tempfile.mkdtemp(prefix="t20_transcheck_")
    if os.path.realpath(tmp).startswith(os.path.realpath(SELF) + os.sep):
        sys.exit("REFUSE: selftest scratch resolves inside the live rung tree")
    try:
        live = os.path.join(tmp, "reg.json")
        shutil.copyfile(REG, live)          # bytes written by the real producer

        # NEGATIVE LIMB: the untouched real transcription must go SILENT (rc 0).
        rc0, msgs0 = check(reg_path=live)
        ok(rc0 == 0, "UNCORRUPTED real transcription -> rc 0, silent (%d msgs)"
                     % len(msgs0))

        # POSITIVE LIMB 1: corrupt ONE numeric value -> must REFUSE.
        d = json.load(open(live))
        target = "T20_LC_f" if "T20_LC_f" in d["cases"] else sorted(d["cases"])[-1]
        d["cases"][target]["point_core_min"] += 1e-9   # a NINTH-figure change
        c1 = os.path.join(tmp, "c1.json")
        json.dump(d, open(c1, "w"), indent=1)
        rc1, m1 = check(reg_path=c1)
        ok(rc1 == EXIT_REFUSE and any("MISTRANSCRIBED" in x for x in m1),
           "PLANTED: %s.point_core_min +1e-09 -> REFUSES (exit %d)" % (target, rc1))

        # POSITIVE LIMB 2: strip a citation -> must REFUSE under 24.4(a).
        d = json.load(open(live))
        d["cases"][target].pop("cost_source_section", None)
        c2 = os.path.join(tmp, "c2.json")
        json.dump(d, open(c2, "w"), indent=1)
        rc2, m2 = check(reg_path=c2)
        ok(rc2 == EXIT_REFUSE, "PLANTED: %s cost_source_section REMOVED -> REFUSES"
                               % target)

        # POSITIVE LIMB 3: break the ONE timeout rule -> must REFUSE under 24.4(b).
        d = json.load(open(live))
        d["cases"][target]["timeout_s"] = int(d["cases"][target]["timeout_s"]) + 1
        c3 = os.path.join(tmp, "c3.json")
        json.dump(d, open(c3, "w"), indent=1)
        rc3, m3 = check(reg_path=c3)
        ok(rc3 == EXIT_REFUSE and any("24.4(b)" in x for x in m3),
           "PLANTED: %s.timeout_s +1 s -> REFUSES on the single-rule limb" % target)

        # POSITIVE LIMB 4: an off-table case -> must REFUSE under 24.4(e).
        d = json.load(open(live))
        d["cases"]["T20_LC_ZZ"] = dict(d["cases"][target])
        c4 = os.path.join(tmp, "c4.json")
        json.dump(d, open(c4, "w"), indent=1)
        rc4, m4 = check(reg_path=c4)
        ok(rc4 == EXIT_REFUSE and any("24.4(e)" in x for x in m4),
           "PLANTED: off-table case T20_LC_ZZ added -> REFUSES on the ceiling limb")

        # RESTORE limb: the control's own last act is to prove it goes silent
        # again on the unmodified producer bytes -- both limbs, not just one.
        rc5, _ = check(reg_path=live)
        ok(rc5 == 0, "RESTORED to the real transcription -> rc 0, silent again")

        src = open(os.path.abspath(__file__)).read()
        n = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src)))
        planted = sum(isinstance(x, ast.Assert)
                      for x in ast.walk(ast.parse(src + "\nassert True\n")))
        ok(n == 0 and planted == 1,
           "AST assert count in this file = 0 (counter sees a planted assert: %d)"
           % planted)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rc, msgs = check()
    if rc:
        return fail(msgs)
    n = len(json.load(open(PROSE))["cases"])
    print("CERTIFIED: %d transcribed case(s) byte-equal to the prose frozen at "
          "7b93b2c8; 24.4 (a) (b) (e) all hold." % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
