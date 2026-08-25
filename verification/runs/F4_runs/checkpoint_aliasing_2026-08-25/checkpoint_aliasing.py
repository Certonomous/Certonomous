#!/usr/bin/env python3
"""F4 CHECKPOINT-ALIASING DIAGNOSTIC -- 2026-08-25.

THIS GRADES NOTHING AND MOVES NO VERDICT.  F4's nine gate rows are closed
(``verification/runs/F4_runs/conversion_2026-08-25/F4_CONVERSION_GRADE.json``:
eight NOT A RESULT, one CONVERGING).  Nothing here re-grades them, and nothing
here is a pre-registration.  It is a diagnostic answering ONE question:

    does the mesh-triple state on the F4 standoff gate MOVE when the temporal
    checkpoint used to evaluate it is changed?

If it does not move, the 2026-07-28 detector diagnosis stands.  If it does, the
temporal sampling is contaminating a mesh triple.

INSTRUMENT.  The readers are the FROZEN ones: this file IMPORTS
``conversion_2026-08-25/grade_f4.py`` (HEAD blob f51961435729558dc768d89e429c1818e8ae1da6)
by path and calls its ``find_shock``, ``read_xy`` and ``control_p1`` unchanged.
The frozen file is NOT edited and NOT copied.  What is varied is which
checkpoint the reader is pointed at -- the sampling, not the instrument.

TWO DELIBERATE DEPARTURES FROM ``grade_f4.standoff()``, both declared:

  1. ``grade_f4.standoff()`` averages ``snapshot_times(case_dir)``, which
     returns only the LAST THREE sampled times.  This diagnostic enumerates
     EVERY sampled time on disk, because the count of sampled times is the
     variable under test.
  2. ``grade_f4.standoff()`` REFUSES the whole case on a censored read.  A
     refusal would end the diagnostic at the first censored snapshot and hide
     the answer.  Here a censored snapshot is EXCLUDED AND COUNTED, never
     averaged in, and every exclusion is reported.  The censoring rule itself
     -- index 0 or N_SAMPLE_POINTS-1 is the instrument's range limit and not a
     measurement -- is unchanged.

WRITES.  Only under this directory.  Neither ``verification/runs/F4_runs/cyl/``
nor ``conversion_2026-08-25/runs/`` is written to, and the frozen grader's own
production-tree guard is not touched, disabled or worked around -- ``grade_all``
is never called.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
F4 = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(F4, "..", "..", ".."))
GRADER = os.path.join(F4, "conversion_2026-08-25", "grade_f4.py")
GRADER_BLOB = "f51961435729558dc768d89e429c1818e8ae1da6"

sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, F4)
_spec = importlib.util.spec_from_file_location("grade_f4_frozen", GRADER)
GF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(GF)                      # FROZEN, imported not copied
import roache_triple as RT                        # noqa: E402

TREES = {
    "production_2026-07-28": os.path.join(F4, "cyl"),
    "conversion_2026-08-25": os.path.join(F4, "conversion_2026-08-25",
                                          "runs", "cyl"),
}


def sampled_times(case_dir):
    """EVERY sampled time on disk, ascending.  Not grade_f4.snapshot_times(),
    which truncates to the last three -- that truncation is the variable."""
    root = os.path.join(case_dir, "postProcessing", "sampleDict")
    if not os.path.isdir(root):
        return []
    out = []
    for name in os.listdir(root):
        try:
            out.append((float(name), name))
        except ValueError:
            continue
    return [n for _, n in sorted(out)]


def field_times(case_dir):
    """The written FIELD time directories -- the checkpoints that exist as
    fields, whether or not a line sample was written at them."""
    out = []
    for name in os.listdir(case_dir):
        p = os.path.join(case_dir, name)
        if not os.path.isdir(p):
            continue
        try:
            out.append((float(name), name))
        except ValueError:
            continue
    return [n for _, n in sorted(out)]


def standoff_at(case_dir, st):
    """The frozen detector at ONE checkpoint, with the endpoint-censoring guard
    applied as EXCLUDE-AND-COUNT (departure 2 above)."""
    p = os.path.join(case_dir, "postProcessing", "sampleDict", st,
                     "r0_T_p_rho.xy")
    if not os.path.isfile(p):
        return dict(time=st, censored=False, absent=True, standoff=None,
                    index=None)
    i, dist, rho = GF.find_shock(p)               # FROZEN reader
    censored = (i == 0 or i == GF.N_SAMPLE_POINTS - 1)
    return dict(time=st, censored=censored, absent=False, index=int(i),
                standoff=None if censored else float(dist),
                rho_at_peak=float(rho))


def triple(values):
    """The mesh triple on three level values, with grade_f4's OWN registered
    CELLS / DIM / FS / FORM.  Nothing here is re-chosen."""
    if any(v is None for v in (values.get(lv) for lv in GF.LEVELS)):
        return dict(state="UNEVALUABLE", order=None, monotone=None)
    c, m, f = values["coarse"], values["medium"], values["fine"]
    # THE DETECTOR IS QUANTISED.  find_shock is an argmax over a FIXED 400-point
    # line spanning [0, 0.7] identically at every mesh level, so the detected
    # standoff can only take 400 values and two levels can return the SAME one.
    # An exact tie makes the Richardson exponent undefined (log of zero) --
    # roache_triple.gci_equal raises rather than inventing a number.  That is
    # the EXACT state of rule 5 clause 2 and it is reported, never swallowed.
    if (m - c) == 0.0 or (f - m) == 0.0:
        return dict(state="EXACT", order=None, monotone=False,
                    tie=("coarse==medium" if (m - c) == 0.0
                         else "medium==fine"))
    tr = RT.triple_from_cells(c, m, f, GF.CELLS["coarse"], GF.CELLS["medium"],
                              GF.CELLS["fine"], dim=GF.DIM, fs=GF.FS,
                              form=GF.FORM)
    return dict(state=tr["state"], order=tr.get("order"),
                monotone=RT.monotone(tr), r21=tr.get("r21"),
                r32=tr.get("r32"))


def main():
    report = dict(
        what="F4 checkpoint-aliasing diagnostic; grades nothing, moves no gate",
        grader=dict(path=os.path.relpath(GRADER, REPO), blob=GRADER_BLOB),
        controls={}, trees={})

    # ---- CONTROL, FIRST.  CLAUDE.md rule 3.  The frozen planted-zero control,
    # run on a donor from the tree this diagnostic reads.  A detector not shown
    # able to see a plant produces no evidence here either.
    donor_case = os.path.join(TREES["production_2026-07-28"], "M6.0", "fine")
    donor = os.path.join(donor_case, "postProcessing", "sampleDict",
                         sampled_times(donor_case)[-1], "r0_T_p_rho.xy")
    tmp = os.path.join(HERE, "_control_tmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        report["controls"]["P1_frozen"] = GF.control_p1(donor, tmp)
        report["controls"]["P1_donor"] = os.path.relpath(donor, REPO)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- CONTROL 2.  The censoring guard must be shown able to FIRE, or its
    # never-firing below is not evidence of anything.
    tmp2 = os.path.join(HERE, "_censor_tmp")
    os.makedirs(tmp2, exist_ok=True)
    try:
        dst = os.path.join(tmp2, "r0_T_p_rho.xy")
        GF._plant_spike(donor, dst, GF.N_SAMPLE_POINTS - 1)
        i, _, _ = GF.find_shock(dst)
        fired = (i == 0 or i == GF.N_SAMPLE_POINTS - 1)
        report["controls"]["censor_guard_fires"] = dict(
            planted_index=GF.N_SAMPLE_POINTS - 1, located_index=int(i),
            guard_would_fire=bool(fired))
        if not fired:
            raise SystemExit("CONTROL FAILED: a plant at the last sample index "
                             "did not put the detector at an endpoint; the "
                             "censoring guard cannot be shown to fire.")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    for tree_name, root in TREES.items():
        tinfo = dict(root=os.path.relpath(root, REPO), cases={}, machs={})
        for M in GF.MACHS:
            per_level, ordinals = {}, {}
            for lv in GF.LEVELS:
                cd = os.path.join(root, f"M{M}", lv)
                sts = sampled_times(cd)
                fts = [t for t in field_times(cd) if float(t) > 0.0]
                snaps = [standoff_at(cd, st) for st in sts]
                per_level[lv] = snaps
                tinfo["cases"][f"M{M}/{lv}"] = dict(
                    n_field_checkpoints=len(fts), field_checkpoints=fts,
                    n_sampled_times=len(sts), sampled_times=sts,
                    n_censored=sum(1 for s in snaps if s["censored"]),
                    censored_times=[s["time"] for s in snaps if s["censored"]],
                    standoffs=[s["standoff"] for s in snaps])
                ordinals[lv] = [s["standoff"] for s in snaps]

            n = min(len(ordinals[lv]) for lv in GF.LEVELS)
            rows = []
            # (a) the triple at EACH checkpoint ordinal, independently
            for k in range(n):
                vals = {lv: ordinals[lv][k] for lv in GF.LEVELS}
                rows.append(dict(
                    basis=f"single checkpoint, ordinal {k+1} of {n}",
                    times={lv: per_level[lv][k]["time"] for lv in GF.LEVELS},
                    values=vals, **triple(vals)))
            # (b) the triple on the mean of the last j checkpoints, j = 1..n --
            #     j = n reproduces the frozen gate value on a 3-sample tree.
            for j in range(1, n + 1):
                vals = {}
                for lv in GF.LEVELS:
                    w = [v for v in ordinals[lv][n - j:] if v is not None]
                    vals[lv] = (sum(w) / len(w)) if w else None
                rows.append(dict(
                    basis=f"mean of the last {j} checkpoint(s)",
                    n_averaged=j, values=vals, **triple(vals)))
            tinfo["machs"][f"M{M}"] = rows
        report["trees"][tree_name] = tinfo

    # ---- THE DETECTOR'S RESOLUTION.  find_shock is an argmax over a FIXED
    # 400-point line spanning [0, L_RADIAL] at EVERY mesh level, so its output
    # is QUANTISED to that spacing.  A mesh-triple difference smaller than a few
    # quanta is not a resolved difference, and a Richardson exponent fitted
    # across such differences is fitted across detector noise.  The quantum is
    # reported beside every triple so no reader can see the state without it.
    q = GF.L_RADIAL / (GF.N_SAMPLE_POINTS - 1)
    report["detector"] = dict(
        line_length=GF.L_RADIAL, n_points=GF.N_SAMPLE_POINTS,
        sample_quantum=q,
        note="detected standoff can take only %d values; every difference "
             "below is stated in quanta of %.6e"
             % (GF.N_SAMPLE_POINTS, q))
    for tree_name, tinfo in report["trees"].items():
        for M, rows in tinfo["machs"].items():
            for r in rows:
                v = r["values"]
                if any(v[lv] is None for lv in GF.LEVELS):
                    continue
                e21 = v["medium"] - v["coarse"]
                e32 = v["fine"] - v["medium"]
                r["e21_quanta"] = e21 / q
                r["e32_quanta"] = e32 / q

    # ---- IS THE TRIPLE DIFFERENCE EVEN RESOLVED?  The pre-registration
    # derives gate G-F4-2's band as ONE LOCAL RADIAL CELL, on the stated
    # ground (prereg 5.1, transcribed in standoff_band_pct) that "two shock
    # positions closer together than dr produce the SAME detected locus" and a
    # deviation below dr "is not a resolved disagreement".  THAT REASONING WAS
    # APPLIED TO THE BAND AND NOT TO THE TRIPLE.  Applied to the triple it asks
    # whether e21 and e32 -- the level-to-level differences whose SIGNS decide
    # CONVERGING vs OSCILLATORY -- are larger than one local cell.  Where they
    # are not, the sign pattern is not a resolved measurement.  This block only
    # reports the comparison; it changes no verdict.
    res = {}
    for M in GF.MACHS:
        dref = float(GF.billig_delta_over_R(M))
        cells = {lv: GF.cell_at_distance(GF.RES[lv][1], dref) for lv in GF.LEVELS}
        res[f"M{M}"] = dict(
            billig_delta_over_R=dref,
            local_cell=cells,
            local_cell_in_quanta={lv: cells[lv] / q for lv in GF.LEVELS},
            finest_local_cell_quanta=cells["fine"] / q)
    report["resolution"] = res
    for tree_name, tinfo in report["trees"].items():
        for M, rows in tinfo["machs"].items():
            lim = res[M]["finest_local_cell_quanta"]
            for r in rows:
                if "e21_quanta" not in r:
                    continue
                r["e21_resolved"] = abs(r["e21_quanta"]) > lim
                r["e32_resolved"] = abs(r["e32_quanta"]) > lim
                r["resolution_limit_quanta"] = lim

    # ---- STATION CENSUS.  The gate reads r0 ONLY.  The 2026-07-28 record
    # reports this detector pinning at index 399 at theta ~ 60 deg; that is a
    # statement about the OTHER stations, and it is checked here rather than
    # repeated.  A censored station is counted, never averaged into anything.
    census = {}
    for tree_name, root in TREES.items():
        c = {}
        for M in GF.MACHS:
            for lv in GF.LEVELS:
                cd = os.path.join(root, f"M{M}", lv)
                for st in sampled_times(cd):
                    base = os.path.join(cd, "postProcessing", "sampleDict", st)
                    for fn in sorted(os.listdir(base)):
                        if not fn.endswith("_T_p_rho.xy"):
                            continue
                        stn = fn.split("_")[0]
                        i, _, _ = GF.find_shock(os.path.join(base, fn))
                        d = c.setdefault(stn, dict(n=0, censored=0,
                                                   at_last_index=0))
                        d["n"] += 1
                        if i == 0 or i == GF.N_SAMPLE_POINTS - 1:
                            d["censored"] += 1
                        if i == GF.N_SAMPLE_POINTS - 1:
                            d["at_last_index"] += 1
        census[tree_name] = c
    report["station_census"] = census

    out = os.path.join(HERE, "checkpoint_aliasing.json")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=False)
    print("WROTE " + os.path.relpath(out, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
