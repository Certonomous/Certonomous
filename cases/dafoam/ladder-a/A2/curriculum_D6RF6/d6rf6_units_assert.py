#!/usr/bin/env python
"""Curriculum D6RF -- THE UNITS GATE.  It stands between the endpoint repair and
the mesh deformer, and it refuses with a DISTINCT rc.

    exit 0   the design vector on disk is PHYSICAL, provably, and in bounds
    exit 77  ANY refusal -- registered, distinct, and never confused with
             docker's 125/126/127 or timeout's 124/137

WHY IT EXISTS, IN ONE MEASUREMENT.  D4's arm F crashed at 15 s with
`AnalysisError: Mesh quality error!`.  Its endpoint artefact is still on disk at
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/F/d4_endpoint_dvs.json`
and it carries **no `_units` key of any kind**; its `shape` vector is
bit-identical to the DRIVER-SCALED frame; **62 of its 96 shape components lie
outside the registered [-1, 1] bound, with a maximum |value| of 6.024592.**
The mesh deformer refused.

**THE CRASH WAS THE LUCKY OUTCOME, AND THAT IS THE WHOLE ARGUMENT FOR THIS
FILE.**  Nearly two thirds of the design vector at up to 6x its bound is so far
out that idwarp could not proceed.  Had the excursion been milder -- a smaller
optimum, a scaler nearer 1 -- every primal would have converged and the arm
would have returned a complete, well-formed, plausible FD table at a wing that
was never the design point.  **Not one of this family's count, plant or order
controls would have caught it, because every one of them interrogates the TABLE
and none interrogates the FRAME.**  In this family an FD table is the artefact
that converts a DAFoam gradient into a result, so a defect that silently
relocates the geometry underneath the table attacks the bright line itself.

**THE DEFORMER REFUSING WAS LUCK.  THIS FILE MAKES IT LAW.**

A MISSING MARKER IS A REFUSAL, NEVER A DEFAULT.  The crashed arm's file proves
that an unmarked file is exactly what a naive extractor produces, so "no marker"
cannot be read as "probably physical".  There is no default and no override.

THE SEVEN CHECKS, in order, refusing at the first failure:

  U1  the file exists and parses as a JSON object.
  U2  `_units` is present AND equals `PHYSICAL`.  Absent -> REFUSE.
  U3  `_scaler_source` is present; if that path resolves on this filesystem its
      md5 must match `_scaler_source_md5` (inside the container it does resolve;
      on the host a recorded container path legitimately does not, and the
      binding check is U4, which does not depend on the path at all).
  U4  `_scaler_source_md5` is present and EQUALS the md5 of the runscript this
      invocation was handed.  A marker that names a producer other than the one
      in use is a lie about the frame, and it refuses.
  U5  `_scalers_applied` is present and EQUALS, factor for factor, the scalers
      parsed out of that runscript by `d6rf_endpoint_locus.parse_registration`.
      **A marker cannot vouch for itself:** the claimed scalers are checked
      against the registering source, not believed.
  U6  CONTROL P -- every registered component whose `lower == upper` is
      DEFINITIONAL and must hold to 1e-12 relative.  REFUSES if the registration
      has no pinned component at all (L-302: a control with nothing to check is
      not a control).
  U7  CONTROL B -- BOUNDS CONTAINMENT ON EVERY COMPONENT, **before the mesh is
      touched**.  Any component outside its registered bound REFUSES here rather
      than being handed to the deformer to adjudicate.

Every registered design variable must be present; a file carrying fewer
families than the producer registers refuses at U5/U6.

TWO CALL SITES, AND BOTH ASSERT (CLAUDE.md rule 14 -- a lesson is not applied
until EVERY call site asserts it):
  * `d6rf_run_arm.sh`, host side, at staging, against any endpoint artefact that
    survived the product sweep;
  * the arm command itself, in the container, BETWEEN the physical wrapper that
    writes the vector and the mpirun that consumes it.
Neither call site can be satisfied by the other.

Self-test: `python3 d6rf6_units_assert.py --selftest` drives mutants AND the two
LIVE artefacts on disk -- D4's crashed unmarked vector, which MUST refuse, and
D4's arm-F3 repaired vector, which MUST pass.  A gate that refuses everything is
not a gate either.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import d6rf6_endpoint_locus as locus                                # noqa: E402

RC_UNITS_REFUSAL = 77
UNITS_MARKER = "PHYSICAL"


def refuse(check, detail):
    sys.stderr.write("D6RF_UNITS REFUSE %s %s\n"
                     % (check, json.dumps(detail, sort_keys=True,
                                          default=str)[:1200]))
    sys.stderr.write("D6RF_UNITS rc=%d -- the design vector was NOT handed to "
                     "the mesh deformer.\n" % RC_UNITS_REFUSAL)
    sys.exit(RC_UNITS_REFUSAL)


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def check(dvfile, runscript, verbose=True):
    """Raises SystemExit(77) on any refusal; returns a report dict on pass."""
    # ---- U1 -------------------------------------------------------------
    if not os.path.isfile(dvfile):
        refuse("U1", {"design_variable_file_absent": dvfile})
    try:
        with open(dvfile) as fh:
            doc = json.load(fh)
    except Exception as e:                                       # noqa: BLE001
        refuse("U1", {"file": dvfile, "json_parse_failed": repr(e)[:300]})
    if not isinstance(doc, dict):
        refuse("U1", {"file": dvfile, "top_level_is_not_an_object": True})
    if not os.path.isfile(runscript):
        refuse("U1", {"runscript_absent": runscript})

    # ---- U2 : THE MARKER.  Absent is a REFUSAL, never a default. --------
    if "_units" not in doc:
        refuse("U2", {"file": dvfile, "_units": "ABSENT",
                      "note": "a missing marker is a refusal, never a default. "
                              "An unmarked file is exactly what a naive "
                              "extractor produces -- see D4 arm F, rc=1 at "
                              "15 s, 62 of 96 shape components outside "
                              "[-1,1], max |value| 6.024592",
                      "keys_present": sorted(k for k in doc if k.startswith("_"))})
    if doc["_units"] != UNITS_MARKER:
        refuse("U2", {"file": dvfile, "_units": doc["_units"],
                      "required": UNITS_MARKER})

    # ---- U3 / U4 : the marker names a producer, and it is THIS one ------
    if "_scaler_source" not in doc:
        refuse("U3", {"file": dvfile, "_scaler_source": "ABSENT"})
    if "_scaler_source_md5" not in doc:
        refuse("U4", {"file": dvfile, "_scaler_source_md5": "ABSENT"})
    src = doc["_scaler_source"]
    src_resolved = None
    if isinstance(src, str) and os.path.isfile(src):
        src_resolved = md5_of(src)
        if src_resolved != doc["_scaler_source_md5"]:
            refuse("U3", {"_scaler_source": src, "md5_on_disk": src_resolved,
                          "md5_recorded": doc["_scaler_source_md5"]})
    rs_md5 = md5_of(runscript)
    if doc["_scaler_source_md5"] != rs_md5:
        refuse("U4", {"file": dvfile, "runscript_in_use": runscript,
                      "runscript_md5": rs_md5,
                      "_scaler_source_md5": doc["_scaler_source_md5"],
                      "note": "the marker vouches for a producer that is not "
                              "the one in use; that is a lie about the frame"})

    # ---- U5 : the CLAIMED scalers are checked against the REGISTERING
    # ---- source.  A marker cannot vouch for itself.
    try:
        reg = locus.parse_registration(runscript)
    except locus.LocusRefusal as e:
        refuse("U5", {"runscript": runscript, "parse_refusal": str(e)[:700]})
    registered = dict((k, reg["dvs"][k]["scaler"]) for k in reg["dvs"])
    if "_scalers_applied" not in doc:
        refuse("U5", {"file": dvfile, "_scalers_applied": "ABSENT",
                      "registered": registered})
    claimed = dict((k, float(v)) for k, v in doc["_scalers_applied"].items())
    if claimed != registered:
        refuse("U5", {"file": dvfile, "_scalers_applied": claimed,
                      "registered_by_the_producer": registered,
                      "note": "the marker's claimed scalers disagree with the "
                              "source that registered them"})

    # ---- the vectors themselves ----------------------------------------
    phys = {}
    for k in reg["dvs"]:
        if k not in doc:
            refuse("U5", {"file": dvfile, "registered_dv_absent": k,
                          "registered": sorted(reg["dvs"])})
        try:
            phys[k] = [float(x) for x in doc[k]]
        except Exception as e:                                   # noqa: BLE001
            refuse("U5", {"file": dvfile, "dv": k,
                          "not_a_numeric_vector": repr(e)[:200]})

    # ---- U6 : CONTROL P ------------------------------------------------
    try:
        cp = locus.control_pinned(phys, reg)
    except locus.LocusRefusal as e:
        refuse("U6", {"file": dvfile, "control_P": str(e)[:700]})

    # ---- U7 : CONTROL B, BEFORE the mesh is touched --------------------
    try:
        cb = locus.control_bounds(phys, reg)
    except locus.LocusRefusal as e:
        refuse("U7", {"file": dvfile, "control_B": str(e)[:700],
                      "note": "a component outside its registered bound is "
                              "refused HERE and is never handed to the mesh "
                              "deformer to adjudicate"})

    rep = {"file": os.path.abspath(dvfile), "units": doc["_units"],
           "runscript": os.path.abspath(runscript), "runscript_md5": rs_md5,
           "scaler_source_resolved_md5": src_resolved,
           "scalers": registered,
           "n_pinned_witnesses": cp["n_pinned_found"],
           "n_components_bounds_checked": cb["n_checked"],
           "closest_to_a_bound": cb["closest_to_a_bound"]}
    if verbose:
        sys.stdout.write(
            "D6RF_UNITS_PASS file=%s units=%s runscript_md5=%s scalers=%s "
            "pinned_witnesses=%d bounds_checked=%d closest_to_a_bound=%s\n"
            % (rep["file"], rep["units"], rs_md5,
               json.dumps(registered, sort_keys=True), cp["n_pinned_found"],
               cb["n_checked"], json.dumps(cb["closest_to_a_bound"],
                                           sort_keys=True)))
        sys.stdout.flush()
    return rep


# ------------------------------------------------------------- the self-test
D4_CRASHED = ("/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/"
              "F/d4_endpoint_dvs.json")
D4_REPAIRED = ("/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/"
               "F3/d4_endpoint_dvs_PHYSICAL.json")
RS_D4 = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D4",
                                     "d4_opt_runScript.py"))
RS_D6R = os.path.abspath(os.path.join(HERE, "d6rf6_opt_runScript.py"))


def _clean_d6r_doc():
    return {"_units": "PHYSICAL",
            "_scaler_source": RS_D6R,
            "_scaler_source_md5": md5_of(RS_D6R),
            "_scalers_applied": {"twist": 0.1, "shape": 10.0,
                                 "patchV_cl04": 0.1, "patchV_cl05": 0.1,
                                 "patchV_cl06": 0.1},
            "twist": [0.1 * i - 0.3 for i in range(7)],
            "shape": [0.01 * ((i % 11) - 5) for i in range(96)],
            "patchV_cl04": [100.0, 1.10],
            "patchV_cl05": [100.0, 1.60],
            "patchV_cl06": [100.0, 2.10]}


def selftest():
    import copy
    import shutil
    import subprocess
    import tempfile
    ok, fail = [], []
    tmp = tempfile.mkdtemp(prefix="d6rf_units_st_")

    def drive(label, doc_or_path, runscript, want_rc):
        if isinstance(doc_or_path, dict):
            p = os.path.join(tmp, "dv_%02d.json" % (len(ok) + len(fail)))
            with open(p, "w") as fh:
                json.dump(doc_or_path, fh, indent=1, sort_keys=True)
        else:
            p = doc_or_path
        # RESOLVED FROM __file__, NEVER HARD-CODED.  The predecessor spawned
        # the literal name "d6rf_units_assert.py"; on the rename to this item
        # that path stopped existing and EVERY leg errored -- 0/25, a self-test
        # that reported total failure for a reason that had nothing to do with
        # the gate it tests.  A self-test that cannot find itself is the
        # rename-drift class this family keeps meeting.
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            p, "--runscript", runscript],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        got = r.returncode
        good = (got == want_rc)
        note = (r.stderr.decode(errors="replace").strip().splitlines() or [""])[0]
        print("  %-58s want rc=%-3d got rc=%-3d %s" % (label, want_rc, got,
                                                       "PASS" if good else "FAIL"))
        if note:
            print("        %s" % note[:150])
        (ok if good else fail).append(label)

    print("D6RF UNITS GATE SELFTEST -- rc 0 = physical and in bounds, "
          "rc %d = refusal\n" % RC_UNITS_REFUSAL)

    print("A. THE TWO LIVE ARTEFACTS ON DISK -- the controls that are not fixtures")
    drive("D4 arm F, THE CRASHED UNMARKED VECTOR (must refuse)",
          D4_CRASHED, RS_D4, RC_UNITS_REFUSAL)
    drive("D4 arm F3, THE REPAIRED PHYSICAL VECTOR (must PASS)",
          D4_REPAIRED, RS_D4, 0)

    print("\nB. THE MARKER -- absent is a refusal, never a default")
    clean = _clean_d6r_doc()
    drive("clean D6 multipoint physical vector (must PASS)",
          clean, RS_D6R, 0)
    d = copy.deepcopy(clean); del d["_units"]
    drive("no _units key at all", d, RS_D6R, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["_units"] = "DRIVER_SCALED"
    drive("_units says DRIVER_SCALED", d, RS_D6R, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["_units"] = "physical"
    drive("_units lower-case (not the registered literal)", d, RS_D6R,
          RC_UNITS_REFUSAL)

    print("\nC. THE MARKER CANNOT VOUCH FOR ITSELF")
    d = copy.deepcopy(clean); del d["_scaler_source_md5"]
    drive("_scaler_source_md5 absent", d, RS_D6R, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); del d["_scaler_source"]
    drive("_scaler_source absent", d, RS_D6R, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["_scaler_source_md5"] = "0" * 32
    drive("_scaler_source_md5 does not match the runscript in use", d, RS_D6R,
          RC_UNITS_REFUSAL)
    drive("a PHYSICAL D6 vector graded against D4's runscript (wrong producer)",
          clean, RS_D4, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["_scalers_applied"]["shape"] = 1.0
    drive("_scalers_applied LIES about shape (claims 1.0, registered 10.0)",
          d, RS_D6R, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); del d["_scalers_applied"]
    drive("_scalers_applied absent", d, RS_D6R, RC_UNITS_REFUSAL)
    src = os.path.join(tmp, "moved_runscript.py")
    shutil.copy2(RS_D6R, src)
    with open(src, "a") as fh:
        fh.write("\n# moved\n")
    d = copy.deepcopy(clean); d["_scaler_source"] = src
    drive("_scaler_source resolves on disk but its md5 has MOVED", d, RS_D6R,
          RC_UNITS_REFUSAL)

    print("\nD. THE FRAME ITSELF -- a marked file whose vectors are still scaled")
    d = copy.deepcopy(clean)
    d["shape"] = [v * 10.0 for v in d["shape"]]
    d["twist"] = [v * 0.1 for v in d["twist"]]
    for pt in ("cl04", "cl05", "cl06"):
        d["patchV_" + pt] = [v * 0.1 for v in d["patchV_" + pt]]
    drive("marked PHYSICAL but the vectors are DRIVER-SCALED (the live defect)",
          d, RS_D6R, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["patchV_cl05"][0] = 99.9
    drive("one pinned witness off U0 by 0.1 %", d, RS_D6R, RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["patchV_cl06"][0] = 10.0
    drive("one pinned witness left driver-scaled at 10.0", d, RS_D6R,
          RC_UNITS_REFUSAL)

    print("\nE. BOUNDS CONTAINMENT -- refused HERE, never by the deformer")
    d = copy.deepcopy(clean); d["shape"][0] = 1.000001
    drive("ONE shape component 1e-6 above its [-1,1] bound", d, RS_D6R,
          RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["shape"][0] = 6.024592
    drive("ONE shape component at the crashed arm's own max |value|", d, RS_D6R,
          RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["twist"][0] = -10.5
    drive("one twist component below its lower bound", d, RS_D6R,
          RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["patchV_cl04"][1] = 10.5
    drive("one angle of attack above its 10 deg upper bound", d, RS_D6R,
          RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["shape"][0] = 1.0
    drive("a component exactly ON its bound (must NOT refuse)", d, RS_D6R, 0)

    print("\nF. STRUCTURE")
    d = copy.deepcopy(clean); del d["shape"]
    drive("a registered design variable missing from the file", d, RS_D6R,
          RC_UNITS_REFUSAL)
    d = copy.deepcopy(clean); d["shape"] = ["not", "numbers"]
    drive("a design variable that is not a numeric vector", d, RS_D6R,
          RC_UNITS_REFUSAL)
    p = os.path.join(tmp, "notjson.json")
    with open(p, "w") as fh:
        fh.write("{ this is not json")
    drive("the file does not parse as JSON", p, RS_D6R, RC_UNITS_REFUSAL)
    drive("the file does not exist", os.path.join(tmp, "nope.json"), RS_D6R,
          RC_UNITS_REFUSAL)

    print("\nD6RF_UNITS_SELFTEST %d/%d PASS" % (len(ok), len(ok) + len(fail)))
    if fail:
        print("FAILED: %s" % ", ".join(fail))
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dvfile", nargs="?")
    ap.add_argument("--runscript")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.dvfile or not a.runscript:
        sys.stderr.write("usage: d6rf6_units_assert.py <dvfile> --runscript "
                         "<producer.py>  |  --selftest\n")
        return 64
    check(a.dvfile, a.runscript)
    return 0


if __name__ == "__main__":
    sys.exit(main())
