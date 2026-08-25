#!/usr/bin/env python3
"""F12 TERMINAL-DEPARTURE PROBE -- reader.

Answers Q1-Q4 of verification/campaign/F12_TERMINAL_DEPARTURE_PREREGISTRATION.md
and grades the four registered predictions P1-P4.  GRADES NO F12 GATE.

Every count and every "did not" below rests on the planted-zero control in
section 0, which plants a known perturbation into a field WRITTEN BY THIS RUN,
reads it back THROUGH THIS READER, and REFUSES if the reader cannot see it.
"""
from __future__ import annotations
import json, math, os, re, shutil, sys, tempfile, pathlib

CASE = pathlib.Path("/home/ubuntu/certonomous-runs/f12_terminal_departure_2026-08-25/case")
EV = pathlib.Path("/home/ubuntu/Certonomous/verification/runs/F12_runs/"
                  "terminal_departure_2026-08-25/evidence")
RUNG1_LOG = pathlib.Path("/home/ubuntu/Certonomous/verification/runs/F12_runs/"
                         "attempt2_coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam")
P_REF, T_REF = 101325.0, 300.0
P_LO, P_HI = 0.1 * P_REF, 2.0 * P_REF        # pMinFactor 0.1, pMaxFactor 2
QC = (0.25, 0.0, 0.0)
PLANT = -7.654321e+09


def refuse(msg):
    print("CONTROL REFUSED: " + msg)
    sys.exit(1)


# --------------------------------------------------------------------------
# field reading -- ascii internalField nonuniform List<scalar>
# --------------------------------------------------------------------------
def read_scalar(path):
    txt = pathlib.Path(path).read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(",
                  txt)
    if m:
        n = int(m.group(1))
        start = m.end()
        end = txt.index(")", start)
        vals = [float(x) for x in txt[start:end].split()]
        if len(vals) != n:
            refuse(f"{path}: declared {n} values, parsed {len(vals)}")
        return vals
    m = re.search(r"internalField\s+uniform\s+([-\deE.+]+)\s*;", txt)
    if m:
        return None                        # uniform: caller handles
    refuse(f"{path}: no readable internalField")


def read_vector(path):
    txt = pathlib.Path(path).read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n(\d+)\s*\n\(",
                  txt)
    if not m:
        return None
    n = int(m.group(1)); start = m.end(); end = txt.index("\n)", start)
    body = txt[start:end]
    out = [tuple(float(v) for v in t.split())
           for t in re.findall(r"\(([^)]*)\)", body)]
    if len(out) != n:
        refuse(f"{path}: declared {n} vectors, parsed {len(out)}")
    return out


def cell_centres():
    """From writeCellCentres output C, written by postProcess."""
    p = CASE / "0" / "C"
    if not p.exists():
        return None
    return read_vector(p)


# --------------------------------------------------------------------------
# 0. THE PLANTED-ZERO CONTROL (standing rule 3)
# --------------------------------------------------------------------------
def planted_control(time_dir="147", field="T"):
    src = CASE / time_dir / field
    if not src.exists():
        refuse(f"no field to plant into at {src}")
    base = read_scalar(src)
    if base is None:
        refuse(f"{src} is uniform; a plant into it proves nothing about a "
               "nonuniform read path")
    arms = {}
    tmp = tempfile.mkdtemp(prefix="f12_td_plant_")
    try:
        work = pathlib.Path(tmp) / field
        shutil.copy(src, work)
        arms["baseline_read"] = (len(base), min(base), max(base))
        # NEGATIVE: the unplanted original must not contain the plant value
        arms["negative_clean_has_no_plant"] = PLANT not in base
        # POSITIVE + LOCALISATION: plant at a KNOWN cell index
        target = 12345 if len(base) > 12345 else len(base) // 2
        txt = work.read_text()
        m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(",
                      txt)
        start = m.end(); end = txt.index(")", start)
        vals = txt[start:end].split()
        vals[target] = repr(PLANT)
        work.write_text(txt[:start] + "\n" + "\n".join(vals) + "\n" + txt[end:])
        back = read_scalar(work)
        arms["cell_count_preserved"] = (len(back) == len(base))
        arms["positive_plant_returned"] = (PLANT in back)
        arms["localisation_exact_cell"] = (back.index(PLANT) == target
                                           if PLANT in back else False)
        arms["plant_cell_index"] = target
        arms["minimum_moved_to_plant"] = (min(back) == PLANT)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = all([arms["negative_clean_has_no_plant"], arms["cell_count_preserved"],
              arms["positive_plant_returned"], arms["localisation_exact_cell"],
              arms["minimum_moved_to_plant"]])
    arms["PASSED"] = ok
    if not ok:
        refuse(f"planted-zero control FAILED: {arms}")
    return arms


# --------------------------------------------------------------------------
# first-solve residual reader (gate-B ruling section 3: read where the solver reads)
# --------------------------------------------------------------------------
FIRST = re.compile(r"Solving for (\w+), Initial residual = ([-\d.eE+]+)")


def first_solve_series(log_path):
    out, cur, seen = [], None, set()
    for line in pathlib.Path(log_path).read_text(errors="replace").splitlines():
        m = re.match(r"^Time = (\d+)$", line.strip())
        if m:
            if cur is not None:
                out.append(cur)
            cur, seen = {"iteration": int(m.group(1))}, set()
            continue
        if cur is None:
            continue
        f = FIRST.search(line)
        if f and f.group(1) not in seen:      # FIRST solve only
            seen.add(f.group(1))
            cur[f.group(1)] = float(f.group(2))
    if cur is not None:
        out.append(cur)
    return out


PC = re.compile(r"pressureControl: p (max|min) ([-\d.eE+]+)")


def pressure_control_series(log_path):
    out, cur = [], None
    for line in pathlib.Path(log_path).read_text(errors="replace").splitlines():
        m = re.match(r"^Time = (\d+)$", line.strip())
        if m:
            if cur is not None:
                out.append(cur)
            cur = {"iteration": int(m.group(1))}
            continue
        if cur is None:
            continue
        g = PC.search(line)
        if g:
            cur["p_" + g.group(1)] = float(g.group(2))
    if cur is not None:
        out.append(cur)
    return out


def main():
    EV.mkdir(parents=True, exist_ok=True)
    R = {"grades_no_F12_gate": True,
         "prereg": "verification/campaign/F12_TERMINAL_DEPARTURE_PREREGISTRATION.md",
         "prereg_blob": "118fe0d1e409ce5fd64d284fa2172a8c6e5c7788"}

    print("0. PLANTED-ZERO CONTROL")
    R["planted_zero"] = planted_control()
    print("   PASSED:", R["planted_zero"]["PASSED"],
          "| localisation at cell", R["planted_zero"]["plant_cell_index"])

    # --- P1 faithfulness ---------------------------------------------------
    print("P1. FAITHFULNESS")
    probe = first_solve_series(CASE / "log.rhoSimpleFoam")
    ref = first_solve_series(RUNG1_LOG)
    n = min(len(probe), len(ref))
    mismatch, compared = [], 0
    for i in range(n):
        a, b = probe[i], ref[i]
        if a["iteration"] != b["iteration"]:
            mismatch.append(("iteration", i, a["iteration"], b["iteration"]))
            continue
        for k in ("Ux", "Uy", "e", "p", "k", "omega"):
            if k in a and k in b:
                compared += 1
                if a[k] != b[k]:
                    mismatch.append((k, a["iteration"], a[k], b[k]))
    R["P1"] = {"iterations_probe": len(probe), "iterations_reference": len(ref),
               "residuals_compared": compared, "mismatches": len(mismatch),
               "first_mismatches": mismatch[:5],
               "spot_checks": {str(it): next((r.get("p") for r in probe
                                              if r["iteration"] == it), None)
                               for it in (1, 5, 10, 15, 147)},
               "PASS": len(mismatch) == 0 and compared > 0}
    print(f"   compared {compared} first-solve residuals over {len(probe)} "
          f"iterations, mismatches {len(mismatch)} -> "
          f"{'PASS' if R['P1']['PASS'] else 'FAIL'}")
    if not R["P1"]["PASS"]:
        R["ARM_VOID"] = True
        (EV / "terminal_departure.json").write_text(json.dumps(R, indent=1))
        print("   ARM VOID -- no location is reported.")
        return 1

    # --- P2 the same death -------------------------------------------------
    print("P2. THE SAME DEATH")
    log = (CASE / "log.rhoSimpleFoam").read_text(errors="replace")
    m = re.search(r"Negative initial temperature T0: ([-\d.eE+]+)", log)
    last_time = max(int(x.name) for x in CASE.iterdir()
                    if x.is_dir() and x.name.isdigit())
    times = sorted(int(x.name) for x in CASE.iterdir()
                   if x.is_dir() and x.name.isdigit())
    rc = int((EV / "RC.txt").read_text().strip())
    abort_iter = max(r["iteration"] for r in probe)
    R["P2"] = {"rc": rc, "abort_message_found": bool(m),
               "T0": float(m.group(1)) if m else None,
               "abort_iteration": abort_iter,
               "reference_T0": -2.384321367, "reference_abort_iteration": 148,
               "last_written_time": last_time,
               "PASS": bool(m) and rc == 134 and abort_iter == 148
                       and abs(float(m.group(1)) - (-2.384321367)) < 1e-9}
    print(f"   rc = {rc}, abort at iteration {abort_iter}, T0 = "
          f"{R['P2']['T0']} -> {'PASS' if R['P2']['PASS'] else 'FAIL'}")

    # --- Q1/Q2/P3: when and where --------------------------------------
    print("Q1/Q2/P3. WHEN AND WHERE")
    C = cell_centres()
    if C is None:
        print("   cell centres absent -- run postProcess -func writeCellCentres first")
        R["Q2"] = {"MEASURED": False,
                   "why": "cell centres not written; location NOT MEASURED, "
                          "and an absent measurement is reported as absent"}
        R["P3"] = {"PASS": None, "why": "not measurable without cell centres"}
    else:
        thresholds = [250.0, 200.0, 100.0, 0.0]
        crossings, series = {}, []
        for t in times:
            if t == 0:
                continue
            Tv = read_scalar(CASE / str(t) / "T")
            if Tv is None:
                continue
            i = min(range(len(Tv)), key=lambda j: Tv[j])
            x, y, z = C[i]
            r = math.dist((x, y, z), QC)
            series.append({"iteration": t, "T_min": Tv[i], "cell": i,
                           "xyz": [x, y, z], "r_qc": r, "T_max": max(Tv)})
            for th in thresholds:
                if th not in crossings and Tv[i] < th:
                    crossings[th] = {"iteration": t, "T_min": Tv[i], "cell": i,
                                     "xyz": [x, y, z], "r_qc": r}
        R["Q1_crossings"] = {str(k): v for k, v in crossings.items()}
        R["Q2_T_min_track"] = series
        last = series[-1]
        R["P3"] = {"last_written_time": last["iteration"],
                   "T_min": last["T_min"], "cell": last["cell"],
                   "xyz": last["xyz"], "r_qc": last["r_qc"],
                   "threshold_c": 1.5,
                   "PASS": last["r_qc"] < 1.5}
        print(f"   crossings: " + ", ".join(
            f"{k:g}K@it{v['iteration']}" for k, v in sorted(
                crossings.items(), reverse=True)))
        print(f"   T_min at last written time {last['iteration']}: "
              f"{last['T_min']:.6f} K at cell {last['cell']} "
              f"({last['xyz'][0]:.6f}, {last['xyz'][1]:.6f}), "
              f"r_qc = {last['r_qc']:.6f} c -> "
              f"P3 {'PASS' if R['P3']['PASS'] else 'FAIL'}")

    # --- Q3/P4: the limiter ------------------------------------------------
    print("Q3/P4. THE LIMITER")
    pcs = pressure_control_series(CASE / "log.rhoSimpleFoam")
    frac = []
    for t in times:
        if t == 0:
            continue
        pv = read_scalar(CASE / str(t) / "p")
        if pv is None:
            continue
        out = sum(1 for v in pv if v < P_LO or v > P_HI)
        # p on disk is CENSORED by pressureControl::limit(); count cells AT the
        # bound, which is what a limited cell reads as.
        at = sum(1 for v in pv if abs(v - P_LO) <= 1e-6 or abs(v - P_HI) <= 1e-6)
        frac.append({"iteration": t, "n": len(pv), "outside": out,
                     "at_bound": at, "at_bound_frac": at / len(pv)})
    R["Q3_preclip"] = pcs
    R["Q3_ondisk_limited"] = frac
    lastf = frac[-1]
    tail = [f["at_bound_frac"] for f in frac[-50:]]
    nondec = all(b >= a - 1e-12 for a, b in zip(tail, tail[1:]))
    # HONESTY, AGAINST THIS LANE'S OWN PRE-REGISTRATION.  Q3 of the freeze names
    # "the on-disk count of cells OUTSIDE the bounds"; P4 names "the on-disk
    # pressure-limited cell fraction".  THOSE ARE NOT THE SAME QUANTITY, and the
    # first of them is DEGENERATE: pressureControl::limit() censors p on the way
    # to disk, so a limited cell reads exactly AT the bound and never outside it.
    # The registered Q3 quantity is 0 at every iteration of this run and could
    # never have been anything else.  That is a MIS-SPECIFIED MEASUREMENT
    # QUANTITY in this lane's own freeze, and it is disclosed here rather than
    # quietly replaced.  Both readings are carried; neither is presented as the
    # other.
    printed = {q["iteration"] for q in pcs if "p_max" in q}
    disagree = sum(1 for f in frac
                   if (f["at_bound"] > 0) != (f["iteration"] in printed))
    R["P4"] = {"last_written_time": lastf["iteration"],
               "registered_Q3_quantity_cells_OUTSIDE_bounds":
                   {"max_over_run": max(f["outside"] for f in frac),
                    "total_over_run": sum(f["outside"] for f in frac),
                    "DEGENERATE": max(f["outside"] for f in frac) == 0,
                    "why": "pressureControl::limit() censors p before it is "
                           "written; a limited cell reads AT the bound, never "
                           "outside it. The registered quantity could not have "
                           "been non-zero. MIS-SPECIFIED IN THIS LANE'S OWN "
                           "FREEZE, disclosed not replaced."},
               "proxy_used_cells_AT_bound": lastf["at_bound_frac"],
               "proxy_disagrees_with_solver_print":
                   {"iterations": disagree, "of": len(frac),
                    "why": "a cell can sit at the bound because it was clipped "
                           "in an EARLIER iteration and has not moved; the "
                           "proxy is therefore not a per-iteration clip count"},
               "threshold": 0.90, "monotone_nondecreasing_last_50": nondec,
               "PASS": lastf["at_bound_frac"] >= 0.90 and nondec,
               "STATUS": "NOT EVALUABLE AS REGISTERED -- the registered quantity "
                         "is degenerate and the proxy actually read is not the "
                         "registered quantity. The proxy reading is reported "
                         "with its disagreement count and is NOT presented as a "
                         "refutation."}
    print(f"   limited fraction at it {lastf['iteration']}: "
          f"{lastf['at_bound_frac']*100:.2f} % ({lastf['at_bound']}/{lastf['n']}), "
          f"monotone over last 50: {nondec} -> "
          f"P4 {'PASS' if R['P4']['PASS'] else 'FAIL'}")

    (EV / "terminal_departure.json").write_text(json.dumps(R, indent=1))
    print(f"\nwritten {EV / 'terminal_departure.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
