#!/usr/bin/env python3
"""Curriculum D7F -- THE ACCEPTANCE COMPARATOR for the D7-DEF-4 repair.

Reads `d7fr_accept_primal.json` FROM DISK and grades it against the bands
registered in `PREREGISTRATION.md` sec.5 ACC-1 BEFORE the primal ran.

  ACC-1  THE GATE.  rel_CD = |CD_acc - CD_OPT| / CD_OPT <= 1.0e-3
         PASS -> the diagnosis is proved, the repair is frozen, arms F-S and F-P run.
         GATE FAIL -> THE DIAGNOSIS IS WRONG.  The repair is withdrawn, the FD arms stay
         BLOCKED, a second finding is recorded.  THE BAND IS NOT WIDENED AND THE
         CORRECTION IS NOT ADJUSTED UNTIL IT FITS.
  ACC-2  REPORTED, GATES NOTHING.  rel_CD <= 1.0e-6.  A corroboration channel.
         It can never turn a PASS into a GATE FAIL or the reverse.
  ACC-CL REPORTED, GATES NOTHING.  rel_CL = |CL_acc - CL_OPT| / |CL_OPT| <= 1.0e-3.

CD_OPT and CL_OPT are ARM O's, not this run's, and they are typed here because
they are the PRE-REGISTERED COMPARISON TARGETS -- the number the hypothesis must
hit, fixed before the answer existed.  Their provenance is
`O/opt_IPOPT.txt` (objective) and the frozen extractor's `_final_CL`.  The
comparator additionally CROSS-CHECKS CD_OPT against `_final_CD` carried in the
run's own artifact and REFUSES on a mismatch, so a typo here cannot pass
silently.

PLANTED-ZERO CONTROL (CLAUDE.md rule 3), run BEFORE the number is believed:
  * a known perturbation is planted into `CD` ON DISK, in a copy of the
    artifact, and re-read THROUGH THE SAME READER.  The graded quantity must
    move by the exact predicted amount AND must cross OUT of band ACC-1.  If the
    reader cannot see the plant the comparator REFUSES and grades nothing.
  * a BLIND READER -- one that ignores the path it is handed and returns a fixed
    document -- must be REFUSED, or a reader that never opened the file would
    score identically on clean and planted input.
  * the count channel: the artifact must carry the registered design-variable
    counts (5 twist, 120 shape, 2 patchV) or the comparator REFUSES BY COUNT,
    WITH THE COUNT PRINTED.

REFUSES (exit 2) rather than degrading.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

# ---- registered comparison targets, fixed before the primal ran -----------
CD_OPT = 2.3048932443550496e-02      # D7R arm O IPOPT objective, printed at
                                     # FULL PRECISION in its own log:
                                     # 'Objective...: 2.3048932443550496e-02'
                                     # (scaled == unscaled) at
                                     # O_20260825T223806Z_2844774.log:15946,
                                     # and 2.3048932e-02 at iterate 30 of
                                     # O/opt_IPOPT.txt.
# CL_OPT IS THE REGISTERED TARGET, NOT AN ACHIEVED VALUE, AND THAT IS A
# DELIBERATE DEPARTURE FROM D4 THAT IS DECLARED RATHER THAN LEFT QUIET.
# D7R's arm O log prints THREE different CL values after the IPOPT summary
# (0.2876108208534867, 0.2876108138077296, 0.28761081), from
# post-optimisation evaluations, and NO SINGLE ONE IS IDENTIFIABLE AS THE
# FINAL MAJOR'S CL.  Rather than pick one, this comparator compares against
# the CL the constraint was REGISTERED on -- read from O/d7_cl_target.json,
# which the launcher wrote from the MEASURED baseline BEFORE the driver
# started -- and reports the deviation.  THE CHANNEL GATES NOTHING EITHER
# WAY, so this choice cannot move a verdict; it is declared because an
# undeclared one could not be checked.
CL_OPT = 0.2876130251655752          # O/d7_cl_target.json CL_target
CL_VIOL_OPT = 2.2315752228885266e-06 # IPOPT 'Constraint violation' at the end
BAND_ACC1 = 1.0e-3                   # THE GATE
BAND_ACC2 = 1.0e-6                   # reported, gates nothing
BAND_ACCCL = 1.0e-3                  # reported, gates nothing
PLANT = 1.234e-03                    # rule 3
N_REGISTERED = {"n_twist": 5, "n_shape": 120, "n_patchV": 2}   # sec.2: 127 DVs
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}


class Refuse(Exception):
    pass


def refuse(where, detail):
    raise Refuse("%s: %s" % (where, json.dumps(detail, sort_keys=True,
                                               default=str)[:1200]))


def read_artifact(path):
    """THE reader.  Everything -- the grade, the plant and the blind-reader
    control -- goes through this one function, or the control proves nothing."""
    if not os.path.isfile(path):
        refuse("read_artifact", {"absent": path})
    with open(path) as fh:
        doc = json.load(fh)
    if doc.get("kind") != "d7fr_acceptance_primal":
        refuse("read_artifact", {"kind": doc.get("kind"),
                                 "required": "d7fr_acceptance_primal"})
    for k in ("CD", "CL"):
        if k not in doc:
            refuse("read_artifact", {"missing_key": k})
        if not isinstance(doc[k], (int, float)):
            refuse("read_artifact", {"key": k, "not_a_number": repr(doc[k])})
    return doc


def blind_reader(path):
    """Ignores the path it is handed.  MUST be refused."""
    return {"kind": "d7fr_acceptance_primal", "CD": CD_OPT, "CL": CL_OPT,
            "n_twist": 5, "n_shape": 120, "n_patchV": 2,
            "CD_repr": repr(CD_OPT), "CL_repr": repr(CL_OPT)}


def grade(doc, reader_name="read_artifact"):
    """The graded quantities.  No side effects, so the plant and the clean run
    are scored by identical code."""
    for k, want in sorted(N_REGISTERED.items()):
        got = doc.get(k)
        if got != want:
            refuse("count", {"channel": k, "count_found": got,
                             "count_registered": want})
    cd = float(doc["CD"])
    cl = float(doc["CL"])
    rel_cd = abs(cd - CD_OPT) / abs(CD_OPT)
    rel_cl = abs(cl - CL_OPT) / abs(CL_OPT)
    return {"reader": reader_name, "CD": cd, "CL": cl,
            "rel_CD": rel_cd, "rel_CL": rel_cl,
            "ACC1_in_band": rel_cd <= BAND_ACC1,
            "ACC2_in_band": rel_cd <= BAND_ACC2,
            "ACCCL_in_band": rel_cl <= BAND_ACCCL}


def planted_zero_control(path, tmp):
    """Plant, re-read through the SAME reader, require the graded number to move
    by the predicted amount and to cross OUT of band ACC-1."""
    clean = grade(read_artifact(path))
    planted_path = os.path.join(tmp, "d4_accept_primal_PLANTED.json")
    shutil.copy2(path, planted_path)
    with open(planted_path) as fh:
        doc = json.load(fh)
    cd_planted = float(doc["CD"]) + PLANT
    doc["CD"] = cd_planted
    doc["CD_repr"] = repr(cd_planted)
    with open(planted_path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())

    planted = grade(read_artifact(planted_path))
    expect_rel = abs((clean["CD"] + PLANT) - CD_OPT) / abs(CD_OPT)
    residual = abs(planted["rel_CD"] - expect_rel)
    rec = {"control": "G-ACC-PLANT", "plant": PLANT,
           "planted_artifact": planted_path,
           "rel_CD_clean": clean["rel_CD"], "rel_CD_planted": planted["rel_CD"],
           "rel_CD_expected_under_plant": expect_rel,
           "expectation_residual": residual,
           "clean_in_band_ACC1": clean["ACC1_in_band"],
           "planted_in_band_ACC1": planted["ACC1_in_band"]}
    if residual > 1.0e-12:
        refuse("G-ACC-PLANT", dict(rec, why="the reader did not move by the "
                                            "predicted amount"))
    if planted["ACC1_in_band"]:
        refuse("G-ACC-PLANT", dict(rec, why="a plant of %g did not carry the "
                                            "graded quantity out of band ACC-1; "
                                            "the band cannot see the plant" % PLANT))
    # the blind reader must be refused
    blind_clean = grade(blind_reader(path), "blind_reader")
    blind_planted = grade(blind_reader(planted_path), "blind_reader")
    identical = (blind_clean["rel_CD"] == blind_planted["rel_CD"])
    rec["blind_reader_returns_identical_on_clean_and_planted"] = identical
    rec["blind_reader"] = "REFUSED" if identical else "NOT REFUSED"
    if not identical:
        refuse("G-ACC-PLANT", dict(rec, why="the blind-reader control did not "
                                            "behave as a blind reader; the "
                                            "control proves nothing"))
    rec["verdict"] = "PASS"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="d4_accept_cmp_")
    try:
        doc = read_artifact(a.artifact)

        # CD_OPT cross-check: the target typed here must equal the target the
        # run's own artifact carries, or a typo in this file passes silently.
        hist_cd = doc.get("endpoint_final_CD_from_history")
        if hist_cd is None:
            refuse("target_crosscheck", {"endpoint_final_CD_from_history": None})
        if abs(float(hist_cd) - CD_OPT) > 1.0e-15 * abs(CD_OPT):
            refuse("target_crosscheck",
                   {"CD_OPT_registered_here": CD_OPT,
                    "final_CD_carried_by_the_artifact": hist_cd,
                    "why": "the comparison target does not match the endpoint "
                           "row the extractor selected"})

        control = planted_zero_control(a.artifact, tmp)
        g = grade(doc)

        verdict = "PASS" if g["ACC1_in_band"] else "GATE FAIL"
        # D7F-ACC-DEF-1, REPAIRED IN THIS PORT AND REPORTED FOR D4's COPY.
        # D4's landed comparator guards its verdict vocabulary with a bare
        # `assert`, and `python3 -O` DELETES IT -- so under -O the one check
        # standing between this instrument and a token outside CLAUDE.md rule
        # 1's fixed vocabulary is not there at all.  A guard that vanishes
        # under an interpreter flag is not a guard.  Replaced by a real
        # refusal; D4's FROZEN file is NOT edited and the finding is reported.
        if verdict not in VOCAB:
            refuse("verdict", {"verdict_not_in_fixed_vocabulary": verdict,
                               "vocabulary": sorted(VOCAB),
                               "note": "CLAUDE.md rule 1"})
        res = {
            "gate": "ACC-1 -- does the corrected design point reproduce arm O's "
                    "IPOPT objective",
            "verdict": verdict,
            "artifact": os.path.abspath(a.artifact),
            "CD_measured": g["CD"], "CD_measured_repr": repr(g["CD"]),
            "CD_target": CD_OPT,
            "rel_CD": g["rel_CD"], "band_ACC1": BAND_ACC1,
            "ACC2_reported_gates_nothing": {"band": BAND_ACC2,
                                            "in_band": g["ACC2_in_band"],
                                            "rel_CD": g["rel_CD"]},
            "ACC_CL_reported_gates_nothing": {"band": BAND_ACCCL,
                                              "in_band": g["ACCCL_in_band"],
                                              "CL_measured": g["CL"],
                                              "CL_target": CL_OPT,
                                              "rel_CL": g["rel_CL"]},
            "counts_verified": N_REGISTERED,
            "planted_zero_control": control,
            "dv_units": doc.get("dv_units"),
            "dv_scalers_applied": doc.get("dv_scalers_applied"),
            "dv_preimage_md5": doc.get("dv_preimage_md5"),
            "wall_s": doc.get("wall_s"), "ranks": doc.get("ranks"),
            "consequence": ("PASS: the D7-DEF-4 diagnosis is proved by an "
                            "instrument that grades nothing; the repair is "
                            "frozen and arms F-S and F-P run."
                            if verdict == "PASS" else
                            "GATE FAIL: THE DIAGNOSIS IS WRONG. The repair is "
                            "WITHDRAWN, D4 stays BLOCKED, a second finding is "
                            "recorded. The band is NOT widened."),
        }
    except Refuse as e:
        sys.stderr.write("D7FR_ACCEPT_COMPARE REFUSE %s\n" % e)
        return 2
    txt = json.dumps(res, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(txt)
            fh.flush()
            os.fsync(fh.fileno())
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
