#!/usr/bin/env python3
"""Build the SO-3 demo series: the IPOPT major trace for both rows, the
baseline-to-final coefficient table, and the endpoint finite-difference table.

Every value written here is READ from an artefact on disk in the SO-3 run root.
Nothing is recomputed, rounded up, or carried from memory.

READER CONTROL (CLAUDE.md rule 3).  The IPOPT table is read with the FROZEN
parser `so3_stall.parse_majors`, not a whitespace split.  Before it is trusted
this script PLANTS a known change into a copy of the log text and REFUSES
(exit 2) unless the reader reads the plant back.  A reader not shown able to
see a non-zero is not evidence.

Writes: cases/dafoam/ladder-a/A1_so3_demo_series.json
"""
import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASE = os.path.join(REPO, "cases", "dafoam", "ladder-a", "A1", "curriculum_SO3")
RUN = ("/home/ubuntu/certonomous-runs/"
       "CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation")
GRADE = os.path.join(RUN, "SO3_grade_20260901T040709Z.json")
OUT = os.path.join(REPO, "cases", "dafoam", "ladder-a", "A1_so3_demo_series.json")

OPT_LOG = {"PATCHED": "O-P_20260901T035101Z_1094485.log",
           "SHIPPED": "O-S_20260901T033306Z_1080385.log"}

sys.path.insert(0, CASE)
import so3_stall  # noqa: E402  the frozen parser, used as-is


def refuse(token, detail):
    print("%s %s" % (token, detail))
    sys.exit(2)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def planted_reader_control(text, row):
    """Plant a known objective into a COPY of the log text; refuse unless the
    frozen reader reads it back.  Also drives the NEGATIVE leg: a table whose
    column count is wrong must yield no rows at all."""
    real = so3_stall.parse_majors(text)
    if not real:
        refuse("REFUSE_NO_MAJORS", "the frozen reader found no iteration row in %s" % row)

    plant_value = 7.654321e-03
    target = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = so3_stall.ITER_RE.match(line)
        if m and int(m.group("iter")) == real[-1]["iter"]:
            target = i
            break
    if target is None:
        refuse("REFUSE_NO_PLANT_SITE", "no line matched the last major of %s" % row)

    m = so3_stall.ITER_RE.match(lines[target])
    planted_line = (lines[target][:m.start("obj")]
                    + "%14.7e" % plant_value
                    + lines[target][m.end("obj"):])
    planted = list(lines)
    planted[target] = planted_line
    read_back = so3_stall.parse_majors("\n".join(planted))
    if len(read_back) != len(real):
        refuse("REFUSE_PLANT_CHANGED_ROW_COUNT",
               "%d rows before, %d after the plant on %s" % (len(real), len(read_back), row))
    seen = read_back[-1]["objective"]
    if abs(seen - plant_value) > 1e-12:
        refuse("REFUSE_PLANT_UNSEEN",
               "planted %.7e into %s, reader returned %.7e" % (plant_value, row, seen))
    if abs(real[-1]["objective"] - plant_value) < 1e-12:
        refuse("REFUSE_PLANT_DEGENERATE",
               "the unplanted value already equals the plant on %s" % row)

    # NEGATIVE leg: drop one column and the reader must return nothing for it.
    broken = list(lines)
    broken[target] = " ".join(lines[target].split()[:-1])
    if len(so3_stall.parse_majors("\n".join(broken))) != len(real) - 1:
        refuse("REFUSE_READER_TOO_LOOSE",
               "a short-column row on %s was still parsed" % row)

    return {"plant": plant_value, "read_back": seen,
            "unplanted_last_objective": real[-1]["objective"],
            "n_majors_real": len(real),
            "negative_leg": "a short-column row is not parsed",
            "seen": True}


def main():
    if not os.path.isfile(GRADE):
        refuse("REFUSE_NO_GRADE", GRADE)
    grade = json.load(open(GRADE))
    if grade.get("verdict") != "PASS":
        refuse("REFUSE_ITEM_NOT_PASS", str(grade.get("verdict")))

    out = {
        "item": grade["item"],
        "item_verdict": grade["verdict"],
        "rows": grade["rows"],
        "mesh_cells": grade["mesh_cells"],
        "grade_file": GRADE,
        "grade_sha256": sha256(GRADE),
        "run_root": RUN,
        "note": ("every number in this file is read from the artefact named "
                 "beside it; nothing here is recomputed or estimated"),
        "controls": {},
        "majors": {},
        "coefficients": {},
        "endpoint_fd": {},
        "alpha": {},
        "cost": {},
    }

    g_alpha = grade["gates"]["G-ALPHA_operating_points"]
    out["alpha"] = {
        "registered": g_alpha["registered"],
        "weights_registered": g_alpha["weights_registered"],
        "tolerance_abs": g_alpha["tolerance_abs"],
        "verdict": g_alpha["verdict"],
        "worst_abs_deviation": max(
            max(v["abs_deviation"]) for v in g_alpha["per_artefact"].values()),
        "source": "gates.G-ALPHA_operating_points",
    }

    for row in ("SHIPPED", "PATCHED"):
        log = os.path.join(RUN, OPT_LOG[row])
        if not os.path.isfile(log):
            refuse("REFUSE_NO_OPT_LOG", log)
        text = open(log, "r", errors="replace").read()
        out["controls"]["ipopt_reader_%s" % row] = planted_reader_control(text, row)
        majors = so3_stall.parse_majors(text)
        out["majors"][row] = {
            "log": log,
            "log_sha256": sha256(log),
            "exit_statement": so3_stall.read_exit_statement(text),
            # SAME definition the frozen grader uses (stall.n_majors_parsed):
            # the count of parsed iteration ROWS, whose index runs 0..n-1.
            # One canonical convention per quantity; asserted against the grade
            # below so two numbers can never be published for one thing.
            "n_majors": len(majors),
            "iter": [m["iter"] for m in majors],
            "objective": [m["objective"] for m in majors],
            "inf_du": [m["inf_du"] for m in majors],
            "n_restoration": sum(1 for m in majors if m["restoration"]),
        }

        s9 = grade["gates"]["G-OPT9_optimisation_per_row"][row]
        if out["majors"][row]["n_majors"] != s9["n_majors"]:
            refuse("REFUSE_MAJOR_COUNT_DISAGREES",
                   "%s: this reader %d, the frozen grader %d"
                   % (row, out["majors"][row]["n_majors"], s9["n_majors"]))
        if out["majors"][row]["exit_statement"] != s9["optimiser_exit_statement"]:
            refuse("REFUSE_EXIT_STATEMENT_DISAGREES", row)
        out["coefficients"][row] = {
            "alpha_deg": g_alpha["registered"],
            "CD_baseline": s9["CD_baseline"],
            "CD_final": s9["CD_final"],
            "CL_baseline": s9["CL_baseline"],
            "CL_final": s9["CL_final"],
            "J_baseline": s9["J_baseline"],
            "J_final": s9["J_final"],
            "weighted_drag_reduction_pct": s9["weighted_drag_reduction_pct"],
            "n_majors": s9["n_majors"],
            "max_iter_registered": s9["max_iter_registered"],
            "optimiser": s9["optimiser"],
            "optimiser_exit_statement": s9["optimiser_exit_statement"],
            "tol_registered": s9["tol_registered"],
            "verdict": s9["verdict"],
            "forbidden_readings": s9["forbidden_readings"],
            "source": "gates.G-OPT9_optimisation_per_row.%s" % row,
        }

        g5j = grade["gates"]["G5J"][row]
        obj = g5j["G5J_objective"]
        out["endpoint_fd"][row] = {
            "band_D_pct": obj["band_D_pct"],
            "plateau_tol_pct": obj["plateau_tol_pct"],
            "n_graded_pairs": obj["n_graded_pairs"],
            "n_pass": obj["n_pass"],
            "worst_rel_err_pct": obj["worst_rel_err_pct"],
            "aggregate_rel_err_pct": obj["aggregate_rel_err_pct"],
            "verdict": obj["verdict"],
            "harness_floor_status": g5j["G5J_harness_floor"]["status"],
            "pairs": [{"idx": p["idx"], "adjoint": p["J_adj"], "fd": p["d_ref"],
                       "fd_ladder": p["d_fd"],
                       # SIGNED, and on the GRADER'S OWN denominator |d_ref|
                       # (so3_grade.py: rel = |ref - j| / |ref| * 100).  The
                       # middle entry therefore equals the grader's own
                       # rel_err_pct up to sign; asserted below, so the figure
                       # and the table can never carry two numbers for one thing.
                       "fd_ladder_rel_err_pct": [
                           (v - p["J_adj"]) / abs(p["d_ref"]) * 100.0 for v in p["d_fd"]],
                       "rel_err_pct": p["rel_err_pct"], "steps": p["steps"],
                       "plateau_neighbour_pct": p["plateau_neighbour_pct"],
                       "plateau_proved_against": p["plateau_proved_against"],
                       "verdict": p["verdict"]}
                      for p in obj["pairs"]],
            "trivial_baseline_n_passing": g5j["G_TB_trivial_baseline"]["n_passing_at_the_wrong_step"],
            "trivial_baseline_max_allowed": g5j["G_TB_trivial_baseline"]["max_allowed"],
            "trivial_baseline_worst_rel_err_pct": max(
                v["rel_err_pct"] for v in g5j["G_TB_trivial_baseline"]["per_component"].values()),
            "trivial_baseline_best_rel_err_pct": min(
                v["rel_err_pct"] for v in g5j["G_TB_trivial_baseline"]["per_component"].values()),
            "assembly_identity_worst_rel_residual": max(
                v["rel_residual"] for v in g5j["G_MP_STRUCT_assembly_identity"]["per_component"].values()),
            "assembly_identity_tolerance": list(
                g5j["G_MP_STRUCT_assembly_identity"]["per_component"].values())[0]["tolerance"],
            "source": "gates.G5J.%s" % row,
        }

        for p in out["endpoint_fd"][row]["pairs"]:
            if abs(abs(p["fd_ladder_rel_err_pct"][1]) - p["rel_err_pct"]) > 1e-9:
                refuse("REFUSE_LADDER_DISAGREES_WITH_GRADER",
                       "%s idx %d: ladder %.9f, grader %.9f"
                       % (row, p["idx"], abs(p["fd_ladder_rel_err_pct"][1]),
                          p["rel_err_pct"]))

    g10 = grade["gates"]["G10_caps"]
    out["cost"] = {
        "total_core_min": g10["total_core_min"],
        "ceiling_core_min": g10["ceiling"],
        "usd_derived_not_measured": g10["usd_derived_not_measured"],
        "cost_basis": g10["cost_basis"],
        "per_arm": g10["per_arm"],
        "verdict": g10["verdict"],
        "source": "gates.G10_caps",
    }
    out["predictions"] = grade["predictions"]
    out["planted_controls_from_grade"] = {
        k: {kk: vv for kk, vv in v.items() if kk != "benign_banners_excluded_and_counted"}
        for k, v in grade["controls"].items()}
    out["completion"] = {
        "declared": grade["completion"]["declared"],
        "executed": grade["completion"]["executed"],
        "verdict": grade["completion"]["verdict"],
    }

    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("WROTE %s" % OUT)
    for row in ("SHIPPED", "PATCHED"):
        c = out["controls"]["ipopt_reader_%s" % row]
        print("  reader control %-7s SEEN plant=%.7e read_back=%.7e majors=%d"
              % (row, c["plant"], c["read_back"], c["n_majors_real"]))
        print("  %-7s exit=%r majors=%d J %.7f -> %.7f"
              % (row, out["majors"][row]["exit_statement"],
                 out["majors"][row]["n_majors"],
                 out["coefficients"][row]["J_baseline"],
                 out["coefficients"][row]["J_final"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
