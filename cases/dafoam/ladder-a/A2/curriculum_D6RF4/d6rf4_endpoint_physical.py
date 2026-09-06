#!/usr/bin/env python
"""Curriculum D6RF4 -- the MULTIPOINT endpoint repair, as a WRAPPER that edits
zero bytes of any frozen file.

DERIVED FROM `curriculum_D6RF2/d6rf2_endpoint_physical.py`
(md5 `6e5fa9f9c2048b0665593282f62ba3dc`, verified on disk before this file was
written); the deltas are in `d6rf4_endpoint_physical_DELTAS_from_d6rf2.diff`
beside this file.  THREE OF THEM ARE COUPLED CONSEQUENCES OF ANOTHER RULING and
are recorded here so a reader does not have to reconstruct why they moved:

  D1  `EXTRACTOR` / `MD5_EXTRACT` are RE-PINNED to `d6rf4_extract_endpoint.py`.
      This file INVOKES the extractor (C3), so the supervisor's POSITION 1
      ruling on `PREREGISTRATION.md` section 9 -- a successor extractor reading
      DVs and `J` only -- does not land in the extractor alone.  Had this pin
      not moved, C1 would have refused on the first fire.
  D2  Every product name is this item's own (`d6rf4_*`).
  D3  ⚠ `PHYSICAL` IS `d6rf4_endpoint_dvs_PHYSICAL.json`, WHICH REPAIRS
      `D6RF3-DEF-6`.  MEASURED IN THE FROZEN `D6RF2` SET: `d6rf2_grade.py:94`,
      `:104` and `:458` and `d6rf2_run_arm.sh:546` all register
      `d6rf2_endpoint_dvs_PHYSICAL.json`, while `d6rf2_endpoint_physical.py:75`
      -- THE ONLY FILE THAT WRITES IT -- still wrote `D6RF`'s
      `d6rf_endpoint_dvs_PHYSICAL.json`.  `d6rf2_grade.py:324-329` walks
      `REGISTERED_PRODUCTS` and REFUSES `registered_product_absent` when the
      producing arm ran, so `D6RF2` would have refused at grading even had every
      arm run clean.  This is `DAFOAM_CHARTER.md` section 18.3's failure mode
      exactly: a name in the instrument/product table that no instrument writes.
      `d6rf4_grade.py` additionally carries an executable `PRODUCT_WRITER` check
      so the class cannot recur silently.

DERIVED FROM `cases/dafoam/ladder-a/A2/curriculum_D4/d4_endpoint_physical.py`
(md5 `74c35c80bb4d395cf8939d851bc6b3f9`), which D4's arm F3 ran to `rc = 0`.
The three limits below are D4's and bind here unchanged; the deltas are the two
file names and the locus module, and they are enumerated in `PREREGISTRATION.md`
section 7a.

  LIMIT 1  Both controls are near-identities and neither grades anything.  They
           say the FD table is at the design point the registration names.  They
           do NOT say it is an optimum, and this item does not claim one -- the
           producing optimisation exited
           `EXIT: Invalid number in NLP function or derivative detected.`
           (`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/`
           `O_mp/opt_IPOPT.txt:822`).
  LIMIT 2  ZERO BYTES of any frozen file are edited.  This wrapper INVOKES the
           committed `d6r_extract_endpoint.py` blob (md5 asserted first,
           imported under a module name that is not `__main__`) and corrects
           DOWNSTREAM of it.  The scalers are READ from `d6r_opt_runScript.py`,
           the file that registered them, and are never typed into this file.
  LIMIT 3  NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.  Nothing here reads or
           writes one.

WHAT IT DOES, in order, refusing (exit 2) at the first failure:

  C1  `d6r_extract_endpoint.py` on disk must hash to the frozen md5.
  C2  `d6r_opt_runScript.py` on disk must hash to the frozen md5.
  C3  the frozen extractor is imported and run; its two outputs must exist AND
      be strictly newer than the age datum handed in (CLAUDE.md rule 4's age
      guard).  A stale `d6r_endpoint_dvs.json` lying in the work directory from
      an earlier fire is exactly the shape of a false result, so it is refused
      by DATE and not merely by presence.
  C4  the extractor's output is PRESERVED BYTE-FOR-BYTE as
      `d6r_endpoint_dvs_DRIVERSCALED.json`, md5-verified against the original.
  C5  the scalers, bounds, `U0` and `POINTS` are PARSED from
      `d6r_opt_runScript.py`; every extracted family is divided by ITS OWN
      registered scaler.
  C6  CONTROL P -- the pinned witnesses (`patchV_cl04/05/06[0]`, each pinned at
      `U0`).  Refuses if it finds nothing to check (L-302).
  C7  CONTROL B -- bounds containment on every component.
  C8  `d6rf_endpoint_dvs_PHYSICAL.json` is written -- the corrected artefact, a
      NEW FILE BESIDE the preserved original, carrying its own provenance.  It
      is the artefact the grader re-reads at `G-DVL`.
  C9  `d6r_endpoint_dvs.json` is then rewritten with the PHYSICAL content,
      because the FROZEN `d6r_fd_endpoint.py:96` reads that filename and this
      wrapper may not edit it.  NOTHING IS LOST: the driver-scaled pre-image is
      on disk at C4 with its md5 recorded in both files.

WHAT THIS FILE DOES NOT ESTABLISH, named plainly: it does not prove the
corrected point is an optimum.  Two controls that grade nothing say the point is
SELF-CONSISTENT with the registration.  Only a solve says anything more, and
`D6R`'s solve failed.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d6rf4_endpoint_locus as locus                                # noqa: E402

EXTRACTOR = "d6rf4_extract_endpoint.py"
RUNSCRIPT = "d6rf4_opt_runScript.py"
# PREREGISTRATION.md section 7.  These are the FREEZE, not a preference.
MD5_EXTRACT = "7adc049421cce82f021603bbbe93dd1e"
MD5_RUNSCRIPT = "137539e0a99be27f27fdb69e063b2a87"

SCALED_OUT = "d6rf4_endpoint_dvs.json"                 # the frozen extractor writes this
PRESERVED = "d6rf4_endpoint_dvs_DRIVERSCALED.json"     # the pre-repair pre-image
PHYSICAL = "d6rf4_endpoint_dvs_PHYSICAL.json"         # the corrected artefact
HISTORY = "d6rf4_major_history.json"


def refuse(msg):
    sys.stderr.write("D6RF4_ENDPOINT_PHYSICAL REFUSE %s\n" % msg)
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
               "distinguish this arm's artefact from a stale one")

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
    spec = importlib.util.spec_from_file_location("d6rf4_extract_frozen",
                                                  os.path.abspath(EXTRACTOR))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["d6rf4_extract_frozen"] = mod
    spec.loader.exec_module(mod)      # __name__ != "__main__": no entrypoint fires
    mod.main()                        # the frozen bytes do the extraction

    for need in (SCALED_OUT, HISTORY):
        if not os.path.isfile(need):
            refuse("C3 the frozen extractor did not write %s" % need)
        mt = os.stat(need).st_mtime
        print("  C3 %-30s mtime %.0f > age datum %.0f  %s"
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
    print("  C5 POINTS READ from %s: %r  U0 = %r"
          % (RUNSCRIPT, reg["point_lists"].get("POINTS"),
             reg["module_constants"].get("U0")))

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

    # ---- C8 : the corrected artefact, a NEW FILE beside the preserved one --
    moved = {}
    for k in keys:
        a, b = scaled[k], phys[k]
        moved[k] = {"scaler_applied": scalers_used[k],
                    "scaled_min": min(a), "scaled_max": max(a),
                    "physical_min": min(b), "physical_max": max(b),
                    "n": len(a)}
    out = dict(scaled_doc)
    for k in keys:
        out[k] = phys[k]
    out["_units"] = "PHYSICAL"
    out["_repair"] = "D6RF-DEF-1 (the D4-DEF-4 class, unrepaired in the D6 lineage)"
    out["_repair_authority"] = ("cases/dafoam/ladder-a/A2/curriculum_D6RF/"
                                "PREREGISTRATION.md sections 1 and 3b; the "
                                "precedent is D4's arm F3, rc=0")
    out["_scalers_applied"] = scalers_used
    out["_scaler_source"] = reg["source"]
    out["_scaler_source_md5"] = MD5_RUNSCRIPT
    out["_extractor_md5"] = MD5_EXTRACT
    out["_preimage_file"] = PRESERVED
    out["_preimage_md5"] = m_src
    out["_points"] = reg["point_lists"].get("POINTS")
    out["_U0"] = reg["module_constants"].get("U0")
    out["_quantified_move"] = moved
    out["_control_P"] = cp
    out["_control_B"] = cb
    out["_not_established"] = ("Two controls that grade nothing show this point "
                               "is self-consistent with the registration. They "
                               "do NOT show it is an optimum, and D6R's "
                               "optimisation exited on a non-finite objective, "
                               "so this item claims none.")
    for path in (PHYSICAL, SCALED_OUT):
        with open(path, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
    print("  C8 %s written (corrected artefact, beside the preserved pre-image)"
          % PHYSICAL)
    print("  C9 %s rewritten with PHYSICAL content for the FROZEN "
          "d6r_fd_endpoint.py; pre-image preserved at %s md5 %s"
          % (SCALED_OUT, PRESERVED, m_src))

    sys.stdout.write("D6RF4_ENDPOINT_PHYSICAL_WRITTEN %s scalers=%s "
                     "pinned_witnesses=%d bounds_checked=%d bounds_violations=%d\n"
                     % (PHYSICAL, json.dumps(scalers_used, sort_keys=True),
                        cp["n_pinned_found"], cb["n_checked"], cb["n_violations"]))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
