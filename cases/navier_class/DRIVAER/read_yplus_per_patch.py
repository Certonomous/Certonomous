#!/usr/bin/env python3
"""read_yplus_per_patch.py -- per-patch y+ reader for the DRIVAER arms.

WHAT THIS IS AND IS NOT.  This is a READER over y+ logs already on disk.  It
grades nothing.  It is NOT wired into cases/navier_class/DRIVAER/grade_drivaer.py
(hash-pinned to DRIVAER_R2C_MEDIUM_CONTINUATION_PREREGISTRATION.md sec.4) and NOT
wired into SUBOFF's pinned comparator.  It imports scripts/yplus_reader_guard.py
and REFUSES rather than degrading.

THE CONTROLS IT DRIVES BEFORE IT PRINTS A SINGLE y+ (CLAUDE.md rule 3):

  CONTROL P (reader-level PLANT).  A known perturbation is planted into a COPY of
  the log, at a named patch, and read back with the SAME parser.  The reader must
  see exactly the planted value on exactly that patch and nothing else must move.
  A reader that cannot see a plant cannot be trusted to see a zero.

  CONTROL Z (all-zero limb, driven on a SYNTHETIC log).  On the real logs the
  guard's SPELLING limb always pre-empts the ALL-ZERO limb, so the all-zero limb
  would never be observed to fire.  It is therefore driven here against a
  synthetic log that carries a SOLVER binary name and all-zero numbers -- the one
  shape where limb 2 is the only thing standing between a fabricated zero and a
  gate.  An undriven refusal limb is not a control.

  CONTROL N (negative, real).  The generic `postProcess` arm on the same case,
  same time, same fields -- the reading the lab has measured blind four times.
  It is reported BESIDE the solver-spelling reading, never in place of it.

  CONTROL C (positive, real, independent truth).  CRM wing-alone, whose own
  solve-time yPlus functionObject wrote a known answer, re-driven through this
  same path with that field removed so the probe must reproduce it.

FORCE ARITHMETIC CONTROL.  Every force reading is taken by COLUMN NAME from the
header line and carries the identity <base>(f) + <base>(r) == <base>.  Reading
coefficient.dat positionally puts Cd(f) where Cd belongs; that mistake was made
in this lab on 2026-09-13 and a mechanism was written to explain the wrong number.
"""
import os
import sys
import json
import argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
from yplus_reader_guard import (parse_yplus_log, assert_yplus_reader_not_blind,
                                YPlusReaderBlind)

PLANT_MIN, PLANT_MAX, PLANT_AVG = 1.234e-03, 7.654321e+02, 4.242424e+01


def _fmt_patch_line(name, ymin, ymax, yavg):
    return "    patch %s y+ : min = %.8g, max = %.8g, average = %.8g\n" % (
        name, ymin, ymax, yavg)


def control_P_plant(path, scratch):
    """Plant a known y+ into a COPY of a real log; require the parser to see it."""
    base, _b, _a = parse_yplus_log(path)
    target = base[len(base) // 2][0]          # a named patch, not the first
    src = open(path, errors="replace").read().splitlines(True)
    out, hit = [], 0
    for ln in src:
        if ln.lstrip().startswith("patch %s y+ :" % target):
            out.append(_fmt_patch_line(target, PLANT_MIN, PLANT_MAX, PLANT_AVG))
            hit += 1
        else:
            out.append(ln)
    if hit != 1:
        raise YPlusReaderBlind(
            "CONTROL P could not place a unique plant: patch %r matched %d lines "
            "in %s. The control is inconclusive, so no y+ from this log is "
            "admissible." % (target, hit, path))
    planted_path = os.path.join(scratch, "PLANTED_" + os.path.basename(path))
    with open(planted_path, "w") as fh:
        fh.write("".join(out))
    seen, _b2, _a2 = parse_yplus_log(planted_path)
    got = {n: (a, b, c) for n, a, b, c in seen}
    if target not in got:
        raise YPlusReaderBlind("CONTROL P: reader lost patch %r after planting; "
                               "it cannot see what it was shown." % target)
    gmin, gmax, gavg = got[target]
    ok = (abs(gmin - PLANT_MIN) <= 1e-12 * max(1.0, abs(PLANT_MIN)) and
          abs(gmax - PLANT_MAX) <= 1e-9 * max(1.0, abs(PLANT_MAX)) and
          abs(gavg - PLANT_AVG) <= 1e-9 * max(1.0, abs(PLANT_AVG)))
    # nothing else may have moved
    moved = [n for n, a, b, c in base
             if n != target and got.get(n) != (a, b, c)]
    if not ok or moved:
        raise YPlusReaderBlind(
            "CONTROL P FAILED on %s: planted (%g,%g,%g) into %r, read back "
            "(%g,%g,%g); %d other patches also moved. REFUSING to report y+ "
            "from a reader that cannot see its own plant."
            % (path, PLANT_MIN, PLANT_MAX, PLANT_AVG, target,
               gmin, gmax, gavg, len(moved)))
    return {"passed": True, "patch": target, "n_patches": len(base),
            "planted": [PLANT_MIN, PLANT_MAX, PLANT_AVG],
            "read_back": [gmin, gmax, gavg],
            "other_patches_moved": 0,
            "planted_artifact": planted_path}


def control_Z_allzero(scratch):
    """Drive the ALL-ZERO limb, which the SPELLING limb hides on every real log."""
    p = os.path.join(scratch, "SYNTHETIC_allzero_solver_spelling.log")
    with open(p, "w") as fh:
        fh.write("Exec   : simpleFoam -postProcess -func yPlus -time 10000\n")
        for n in ("BodyHood", "BodySide", "Tiresfront"):
            fh.write(_fmt_patch_line(n, 0.0, 0.0, 0.0))
        fh.write("End\n")
    r, b, a = parse_yplus_log(p)
    if b == "postProcess":
        return {"passed": False, "why": "synthetic log named the generic binary; "
                "the SPELLING limb would pre-empt and limb 2 stays undriven"}
    try:
        assert_yplus_reader_not_blind(r, source=p, binary=b, args=a)
    except YPlusReaderBlind as e:
        return {"passed": True, "limb": "ALL-ZERO", "binary_in_log": b,
                "n_readings": len(r), "refusal": str(e).split(". ")[0],
                "artifact": p}
    return {"passed": False, "why": "ALL-ZERO limb did NOT fire on an all-zero "
            "log carrying a solver binary name. The guard is not arming."}


def read_forces(path):
    """Read coefficient.dat BY COLUMN NAME and carry the (f)+(r)==base identity."""
    hdr, rows = None, []
    with open(path, errors="replace") as fh:
        for ln in fh:
            if ln.startswith("#"):
                s = ln.lstrip("#").split()
                if s and s[0] == "Time" and "Cd" in s:
                    hdr = s
                continue
            if ln.strip():
                rows.append(ln.split())
    if hdr is None:
        raise YPlusReaderBlind("%s: no named header line. A positional read of "
                               "this file puts Cd(f) where Cd belongs." % path)
    if not rows:
        raise YPlusReaderBlind("%s: header but no data rows." % path)
    idx = {n: i for i, n in enumerate(hdr)}
    ctrl, worst = {}, {}
    for base in ("Cd", "Cl", "Cs"):
        f, r = base + "(f)", base + "(r)"
        if not all(k in idx for k in (base, f, r)):
            continue
        w = (-1.0, None)
        for row in rows:
            v, vf, vr = (float(row[idx[base]]), float(row[idx[f]]),
                         float(row[idx[r]]))
            d = abs(vf + vr - v)
            if d > w[0]:
                w = (d, row[0])
        worst[base] = {"worst_abs_residual": w[0], "at_time": w[1]}
        ctrl[base] = w[0] <= 1e-8
    last = rows[-1]
    out = {"artifact": path, "header_read_by_name": hdr,
           "positional_trap_col3_is": hdr[2],
           "n_rows": len(rows), "last_time": last[idx["Time"]],
           "identity_control": {"passed": all(ctrl.values()), "per_coeff": worst}}
    for base in ("Cd", "Cl"):
        if base in idx:
            out[base] = float(last[idx[base]])
    if not out["identity_control"]["passed"]:
        raise YPlusReaderBlind(
            "%s: the (f)+(r)==base identity does NOT close: %s. The force read "
            "is not admissible." % (path, json.dumps(worst)))
    return out


def read_case(name, solver_log, generic_log, scratch, forces=None):
    rec = {"case": name, "solver_arm": {}, "generic_arm": {}}
    # --- CONTROL P on the arm we intend to believe, BEFORE reading it ---
    rec["control_P_plant"] = control_P_plant(solver_log, scratch)
    readings, binary, args = parse_yplus_log(solver_log)
    assert_yplus_reader_not_blind(readings, source=solver_log,
                                  binary=binary, args=args)
    rec["solver_arm"] = {"artifact": solver_log, "binary": binary,
                         "n_patches": len(readings),
                         "n_zero_max": sum(1 for _, _, m, _ in readings if m == 0.0),
                         "patches": [{"patch": n, "min": a, "max": b, "avg": c}
                                     for n, a, b, c in readings]}
    # --- CONTROL N: the generic arm, reported beside, never instead ---
    if generic_log and os.path.isfile(generic_log):
        g, gb, ga = parse_yplus_log(generic_log)
        try:
            assert_yplus_reader_not_blind(g, source=generic_log, binary=gb, args=ga)
            verdict = "ADMITTED (did not refuse)"
        except YPlusReaderBlind as e:
            verdict = "REFUSED: " + str(e).split(". ")[0]
        rec["generic_arm"] = {"artifact": generic_log, "binary": gb,
                              "n_patches": len(g),
                              "n_zero_max": sum(1 for _, _, m, _ in g if m == 0.0),
                              "guard": verdict}
    if forces:
        rec["forces"] = read_forces(forces)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", required=True,
                    metavar="NAME=SOLVERLOG[,GENERICLOG[,COEFFDAT]]")
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--report")
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    out = {"instrument": os.path.relpath(os.path.abspath(__file__), _ROOT),
           "guard": "scripts/yplus_reader_guard.py",
           "not_wired_into": ["cases/navier_class/DRIVAER/grade_drivaer.py",
                              "SUBOFF pinned comparator"],
           "control_Z_allzero_limb": control_Z_allzero(a.scratch),
           "cases": []}
    if not out["control_Z_allzero_limb"]["passed"]:
        print("CONTROL Z FAILED -- the guard's all-zero limb does not arm. "
              "REFUSING to report any y+.", file=sys.stderr)
        print(json.dumps(out["control_Z_allzero_limb"], indent=1), file=sys.stderr)
        return 2
    rc = 0
    for spec in a.case:
        name, _, paths = spec.partition("=")
        parts = (paths.split(",") + ["", ""])[:3]
        try:
            out["cases"].append(read_case(name, parts[0], parts[1] or None,
                                          a.scratch, parts[2] or None))
        except YPlusReaderBlind as e:
            out["cases"].append({"case": name, "REFUSED": str(e)})
            rc = 2
    if a.report:
        with open(a.report, "w") as fh:
            json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))
    return rc


if __name__ == "__main__":
    sys.exit(main())
