#!/usr/bin/env python
"""Curriculum D7F -- D4's LANDED D4-DEF-4 REPAIR, APPLIED TO D7, as a WRAPPER that edits zero bytes.

AUTHORISED BY `SUPERVISOR_D4DEF4_REPAIR_RULING.md` (commit dbb88eb4) under
`VERIFICATION_CHARTER.md` 2d.1, AND BY THE STANDING RULING THAT D7 INHERITS
D4'S REPAIR RATHER THAN AUTHORING ITS OWN (`../curriculum_D7R/PREREGISTRATION.md`
sec.6).  D7-DEF-4 IS CONFIRMED BY MEASUREMENT TWICE: the pinned witness read
`29.160000000000004` against `29.16` registered at `5551db3d` BEFORE any
`OptView.hst` existed on this box, and `patchV[1]` read `0.30600000000000005`
= 3.06 x 0.1 (`../curriculum_D7R/D7R_DEF4_CONFIRMED.md`).

ZERO BYTES OF D7's FROZEN EXTRACTOR ARE EDITED, AND THERE IS NO EXTRACTOR DIFF:
that is this repair's central property, not an omission from it.  THREE LIMITS BIND IT and each is enforced here
mechanically rather than promised in prose:

  LIMIT 1  The repair is NOT FROZEN until one primal at the corrected design
           point reproduces arm O's IPOPT objective inside a band registered
           BEFORE the run.  That is `d7fr_accept_primal.py` and
           `d7fr_accept_compare.py`, and this file is useless without them.
  LIMIT 2  ZERO BYTES of any frozen file are edited.  This wrapper INVOKES the
           committed `d7_extract_endpoint.py` blob (md5 asserted first, imported
           under a module name that is not `__main__`) and corrects DOWNSTREAM
           of it -- the `d8_grade_entry.py` shape this family has already
           validated.  The scalers are READ from `d7_opt_runScript.py`, the file
           that registered them, and are never typed into this file.
  LIMIT 3  NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.  Nothing here reads or
           writes one.  A band is not an instrument; it is the hypothesis's own
           scoring rule.

WHAT IT DOES, in order, refusing (exit 2) at the first failure:

  C1  `d7_extract_endpoint.py` on disk must hash to the frozen md5.
  C2  `d7_opt_runScript.py` on disk must hash to the frozen md5.
  C3  the extractor is imported and run; its two outputs must exist AND be
      strictly newer than the age datum handed in -- the same age-guard
      discipline the frozen launcher applies to a cold case (CLAUDE.md rule 4).
      A stale `d7_endpoint_dvs.json` lying in the work directory from an earlier
      arm is exactly the shape of a false result, so it is refused by DATE and
      not merely by presence.
  C4  the extractor's output is PRESERVED BYTE-FOR-BYTE as
      `d7_endpoint_dvs_DRIVERSCALED.json` and the copy is md5-verified against
      the original -- 2d.1 condition (4), the pre-repair values recorded beside
      the published ones.
  C5  the scalers, bounds and `U0` are PARSED from `d7_opt_runScript.py`; every
      extracted family is divided by ITS OWN registered scaler.
  C6  CONTROL P -- the pinned witness.  Refuses if it finds nothing to check.
  C7  CONTROL B -- bounds containment on every component.
  C8  `d7_endpoint_dvs_PHYSICAL.json` is written -- the corrected artifact, a
      NEW FILE BESIDE the preserved original, carrying its own provenance.
  C9  `d7_endpoint_dvs.json` is then written with the PHYSICAL content, because
      the FROZEN `d7_fd_endpoint.py` reads that filename and this wrapper may
      not edit it.  NOTHING IS LOST: the driver-scaled pre-image is on disk at
      C4 with its md5 recorded in both files, and D7R arm `O`'s artifacts under `O/` is never touched by this file at all.

WHAT THIS FILE DOES NOT ESTABLISH, named plainly: it does not prove the
corrected point IS the optimum.  Two controls that grade nothing say the point
is SELF-CONSISTENT with the registration.  Only a solve says it is the optimum.
That solve is LIMIT 1 and it is a PRECONDITION of the freeze, not a follow-up.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d7fr_endpoint_locus as locus                                  # noqa: E402

EXTRACTOR = "d7_extract_endpoint.py"
RUNSCRIPT = "d7_opt_runScript.py"
# curriculum_D7R/PREREGISTRATION.md sec.10 froze these two md5s, verbatim.  These are the FREEZE, not a preference.
MD5_EXTRACT = "651d40c78cc52288a856934c108d1334"
MD5_RUNSCRIPT = "e43902ed2cfc99022c6e21e075f88695"

SCALED_OUT = "d7_endpoint_dvs.json"                 # the frozen extractor writes this
PRESERVED = "d7_endpoint_dvs_DRIVERSCALED.json"     # 2d.1 condition (4)
PHYSICAL = "d7_endpoint_dvs_PHYSICAL.json"          # the corrected artifact
HISTORY = "d7_major_history.json"


def refuse(msg):
    sys.stderr.write("D7FR_ENDPOINT_PHYSICAL REFUSE %s\n" % msg)
    sys.exit(2)


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    argv = sys.argv[1:]
    age_datum = None
    for i, a in enumerate(argv):
        if a == "--age-datum" and i + 1 < len(argv):
            age_datum = float(argv[i + 1])
    if age_datum is None:
        refuse("--age-datum <epoch> is REQUIRED; without it C3 cannot "
               "distinguish this arm's artifact from a stale one")

    # ---- C1 / C2 : the instruments on disk ARE the committed instruments ----
    for path, want, label in ((EXTRACTOR, MD5_EXTRACT, "C1"),
                              (RUNSCRIPT, MD5_RUNSCRIPT, "C2")):
        if not os.path.isfile(path):
            refuse("%s %s absent" % (label, path))
        got = md5_of(path)
        print("  %s %-26s md5 %s (frozen %s) %s"
              % (label, path, got, want, "OK" if got == want else "FAIL"))
        if got != want:
            refuse("%s %s is not the frozen instrument" % (label, path))

    # ---- C3 : invoke the COMMITTED extractor blob, edit zero bytes ---------
    for stale in (SCALED_OUT, PRESERVED, PHYSICAL, HISTORY):
        if os.path.exists(stale):
            os.remove(stale)
    spec = importlib.util.spec_from_file_location("d7_extract_frozen",
                                                  os.path.abspath(EXTRACTOR))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["d7_extract_frozen"] = mod
    spec.loader.exec_module(mod)      # __name__ != "__main__": no entrypoint fires
    mod.main()                        # the frozen bytes do the extraction

    for need in (SCALED_OUT, HISTORY):
        if not os.path.isfile(need):
            refuse("C3 the frozen extractor did not write %s" % need)
        mt = os.stat(need).st_mtime
        print("  C3 %-26s mtime %.0f > age datum %.0f  %s"
              % (need, mt, age_datum, "OK" if mt > age_datum else "FAIL"))
        if mt <= age_datum:
            refuse("C3 %s is NOT newer than the age datum %.0f -- it did not "
                   "come from this arm" % (need, age_datum))

    # ---- C4 : preserve the pre-repair values BYTE-FOR-BYTE -----------------
    shutil.copy2(SCALED_OUT, PRESERVED)
    m_src, m_dst = md5_of(SCALED_OUT), md5_of(PRESERVED)
    print("  C4 pre-repair preserved as %s md5 %s == %s %s"
          % (PRESERVED, m_src, m_dst, "OK" if m_src == m_dst else "FAIL"))
    if m_src != m_dst:
        refuse("C4 the byte-for-byte preservation copy does not match")

    with open(PRESERVED) as fh:
        scaled_doc = json.load(fh)

    # ---- C5 : the scalers are READ FROM THE REGISTERING SOURCE -------------
    try:
        reg = locus.parse_registration(RUNSCRIPT)
        keys = sorted(reg["dvs"])
        scaled = {}
        for k in keys:
            if k not in scaled_doc:
                refuse("C5 registered design variable %r absent from the "
                       "extractor's output" % k)
            scaled[k] = [float(v) for v in scaled_doc[k]]
        phys, scalers_used = locus.descale(scaled, reg)
    except locus.LocusRefusal as e:
        refuse("C5 %s" % e)
    print("  C5 scalers READ from %s: %s"
          % (RUNSCRIPT, json.dumps(scalers_used, sort_keys=True)))

    # ---- C6 / C7 : the two controls that establish WHERE -------------------
    try:
        cp = locus.control_pinned(phys, reg)
    except locus.LocusRefusal as e:
        refuse("C6 CONTROL P (pinned witness) %s" % e)
    print("  C6 CONTROL P pinned witnesses=%d  %s"
          % (cp["n_pinned_found"],
             "; ".join("%s[%d] == %r (rel residual %.3e)"
                       % (w["dv"], w["idx"], w["pinned_value"], w["rel_residual"])
                       for w in cp["witnesses"])))
    try:
        cb = locus.control_bounds(phys, reg)
    except locus.LocusRefusal as e:
        refuse("C7 CONTROL B (bounds containment) %s" % e)
    print("  C7 CONTROL B checked=%d violations=%d closest_to_a_bound=%s"
          % (cb["n_checked"], cb["n_violations"],
             json.dumps(cb["closest_to_a_bound"], sort_keys=True)))

    # ---- C8 : the corrected artifact, a NEW FILE beside the preserved one --
    moved = {}
    for k in keys:
        a = scaled[k]
        b = phys[k]
        moved[k] = {"scaler_applied": scalers_used[k],
                    "scaled_min": min(a), "scaled_max": max(a),
                    "physical_min": min(b), "physical_max": max(b),
                    "n": len(a)}
    out = dict(scaled_doc)
    for k in keys:
        out[k] = phys[k]
    out["_units"] = "PHYSICAL"
    out["_repair"] = "D7-DEF-4"
    out["_repair_authority"] = "SUPERVISOR_D4DEF4_REPAIR_RULING.md (dbb88eb4); " \
                               "VERIFICATION_CHARTER.md 2d.1"
    out["_scalers_applied"] = scalers_used
    out["_scaler_source"] = reg["source"]
    out["_scaler_source_md5"] = MD5_RUNSCRIPT
    out["_extractor_md5"] = MD5_EXTRACT
    out["_preimage_file"] = PRESERVED
    out["_preimage_md5"] = m_src
    out["_quantified_move"] = moved
    out["_control_P"] = cp
    out["_control_B"] = cb
    out["_not_established"] = ("Two controls that grade nothing show this point "
                               "is self-consistent with the registration. They "
                               "do NOT show it is the optimum. Only the "
                               "acceptance primal does that.")
    for path in (PHYSICAL, SCALED_OUT):
        with open(path, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
    print("  C8 %s written (corrected artifact, beside the preserved pre-image)"
          % PHYSICAL)
    print("  C9 %s rewritten with PHYSICAL content for the FROZEN "
          "d7_fd_endpoint.py; pre-image preserved at %s md5 %s"
          % (SCALED_OUT, PRESERVED, m_src))

    sys.stdout.write("D7FR_ENDPOINT_PHYSICAL_WRITTEN %s scalers=%s "
                     "pinned_witnesses=%d bounds_checked=%d bounds_violations=%d\n"
                     % (PHYSICAL, json.dumps(scalers_used, sort_keys=True),
                        cp["n_pinned_found"], cb["n_checked"], cb["n_violations"]))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
