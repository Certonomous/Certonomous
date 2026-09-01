#!/usr/bin/env python3
"""A2-GC grader: the MACH Tutorial Wing grid-convergence study.

FROZEN WITH cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md. The md5 of
this file is pinned in that pre-registration and the driver asserts it before
any solver starts. Every threshold applied here is quoted from that document;
nothing in this file may be treated as a threshold in its own right.

Order of operations is NOT negotiable and follows CLAUDE.md rule 5:

  1. every reader is BORN against a live planted perturbation and REFUSES
     (exit 2) if it cannot see one -- rule 3, planted-zero control;
  2. completion and iterative convergence per level (GATE C, GATE I);
  3. Roache triple CLASSIFICATION -- a triple that is not CONVERGING is
     NOT A RESULT whatever its value, and no GCI is quoted when the three
     values are not monotone;
  4. only then p against its registered band, and the GCI band on CD.

A gate can only turn a PASS or GATE FAIL INTO a NOT A RESULT, never the reverse.

Usage:  a2gc_grade.py <run_root>            grade
        a2gc_grade.py --selftest            born-readers self-test only
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Thresholds -- ALL quoted from the pre-registration, none invented here.
# ---------------------------------------------------------------------------
CL_TARGET = 0.5
TRIM_TOL = 5.0e-4          # |CL - CL_TARGET| per level; miss => that level BLOCKED
RESIDUAL_TARGET = 1.0e-8   # Sanaa SS0 clause 2
ITER_RATIO_MIN = 10.0      # Delta_mesh / delta_iter must be >= 10 -- SS0 clause 2
P_BAND = (1.5, 2.5)        # SS0 clause 3, as she set it
GCI_FS = 1.25              # CLAUDE.md rule 5
R_NOMINAL = 2.0
CELL_RATIO_NOMINAL = 8.0
CELL_RATIO_TOL = 1.0e-3
TRIPLE = ("L1", "L2", "L3")

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


class Refuse(Exception):
    """A reader that could not be shown able to see a non-zero. Exit 2."""


# ---------------------------------------------------------------------------
# THE READERS. Each is a pure function of text/records so that a planted
# perturbation can be pushed through the REAL reader, not a stand-in.
# ---------------------------------------------------------------------------

def read_cd(text: str):
    """CD from the level's own GC_RESULT line."""
    m = re.findall(r"^GC_RESULT\s+\S+\s+CD\s+([-\d.eE+]+)", text, re.M)
    return float(m[-1]) if m else 0.0


def read_cl(text: str):
    m = re.findall(r"^GC_RESULT\s+\S+\s+CD\s+[-\d.eE+]+\s+CL\s+([-\d.eE+]+)", text, re.M)
    return float(m[-1]) if m else 0.0


def read_cells(text: str):
    """Cell count from the mesh build's own renumberMesh line."""
    m = re.findall(r"Mesh region0 size:\s*(\d+)", text)
    return int(m[-1]) if m else 0


def read_residual(text: str):
    """Worst final primal residual reported on the level's own summary line."""
    m = re.findall(r"^GC_RESID\s+\S+\s+worst\s+([-\d.eE+]+)", text, re.M)
    return float(m[-1]) if m else 0.0


def read_yplus(text: str):
    """y+ min/mean/max from the level's own yPlus summary line."""
    m = re.findall(
        r"^GC_YPLUS\s+\S+\s+min\s+([-\d.eE+]+)\s+mean\s+([-\d.eE+]+)\s+max\s+([-\d.eE+]+)",
        text, re.M)
    return tuple(float(x) for x in m[-1]) if m else (0.0, 0.0, 0.0)


def read_vol_growth(text: str):
    """Max cell-to-cell volume growth ratio -- the F28 similarity metric."""
    m = re.findall(r"^GC_VOLGROWTH\s+\S+\s+max\s+([-\d.eE+]+)", text, re.M)
    return float(m[-1]) if m else 0.0


def read_peak_rss(text: str):
    """Aggregate peak RSS in MiB, from the level's own cgroup reading."""
    m = re.findall(r"^GC_PEAKRSS\s+\S+\s+mib\s+([-\d.eE+]+)", text, re.M)
    return float(m[-1]) if m else 0.0


def read_iter_delta(history):
    """delta_iter: the swing in CD over the stationarity window.

    THE HIGHEST-VALUE PLANT IN THIS ITEM. A delta_iter stuck at zero would
    pass GATE I trivially and hand back an observed order that is pure
    iterative noise dressed as discretisation -- exactly the failure Sanaa's
    SS0 clause 2 was written against.
    """
    if not history:
        return 0.0
    n = max(2, int(round(0.2 * len(history))))
    w = list(history)[-n:]
    return max(w) - min(w)


def read_mesh_delta(cd_a, cd_b):
    """Delta_mesh between consecutive levels. A zero here makes GATE I's
    ratio infinite and would pass the gate for the wrong reason."""
    return abs(float(cd_b) - float(cd_a))


# ---------------------------------------------------------------------------
# Rule 3 -- BIRTH REGISTER. Every reader whose zero could pass a gate is shown,
# live and at grade time, able to see a known planted non-zero, THROUGH THE
# REAL READER FUNCTION. A reader that cannot see its plant refuses, exit 2.
# ---------------------------------------------------------------------------
PLANT = 1.234e-03

def birth_register():
    born, register = [], []

    def witness(name, zero_passes_a_gate, clean_input, planted_input, reader, expect):
        clean = reader(clean_input)
        seen = reader(planted_input)
        ok = (_close(seen, expect) and not _close(seen, clean))
        register.append({
            "reader": name,
            "a_zero_here_could_pass_a_gate": zero_passes_a_gate,
            "clean_reading": _j(clean),
            "planted_value": _j(expect),
            "reading_after_plant": _j(seen),
            "reader_is_evidence": ok,
        })
        if not ok:
            raise Refuse(
                f"REFUSED: reader {name!r} was not shown able to see a planted "
                f"non-zero (clean={clean!r}, planted={seen!r}, expected={expect!r}). "
                f"A zero from this reader is not evidence -- CLAUDE.md rule 3.")
        born.append(name)

    base_cd = 0.0296205
    clean_line = f"GC_RESULT L1 CD {base_cd:.10f} CL 0.5000000000\n"
    plant_line = f"GC_RESULT L1 CD {base_cd + PLANT:.10f} CL {0.5 + PLANT:.10f}\n"

    witness("read_cd", True, clean_line, plant_line, read_cd, base_cd + PLANT)
    witness("read_cl", True, clean_line, plant_line, read_cl, 0.5 + PLANT)
    witness("read_cells", True, "Mesh region0 size: 38304\n",
            "Mesh region0 size: 306432\n", read_cells, 306432)
    witness("read_residual", True, "GC_RESID L1 worst 1.0e-08\n",
            f"GC_RESID L1 worst {PLANT:.6e}\n", read_residual, PLANT)
    witness("read_yplus", False, "GC_YPLUS L1 min 68.79 mean 321.95 max 1266.55\n",
            "GC_YPLUS L1 min 34.40 mean 161.00 max 633.30\n", read_yplus,
            (34.40, 161.00, 633.30))
    witness("read_vol_growth", True, "GC_VOLGROWTH L1 max 1.0000\n",
            f"GC_VOLGROWTH L1 max {1.0 + PLANT:.6f}\n", read_vol_growth, 1.0 + PLANT)
    witness("read_peak_rss", False, "GC_PEAKRSS L1 mib 0.0\n",
            "GC_PEAKRSS L1 mib 9387.0\n", read_peak_rss, 9387.0)
    witness("read_iter_delta", True, [base_cd] * 40,
            [base_cd] * 39 + [base_cd + PLANT], read_iter_delta, PLANT)
    witness("read_mesh_delta", True, (base_cd, base_cd),
            (base_cd, base_cd + PLANT), lambda t: read_mesh_delta(*t), PLANT)

    return {
        "plant": PLANT,
        "readers_declared": 9,
        "readers_born": len(born),
        "zero_passing_readers": sum(1 for r in register if r["a_zero_here_could_pass_a_gate"]),
        "witnesses": register,
        "all_born": len(born) == 9,
    }


def _close(a, b, tol=1e-9):
    if isinstance(a, tuple) or isinstance(b, tuple):
        return (isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b)
                and all(_close(x, y, tol) for x, y in zip(a, b)))
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def _j(v):
    return list(v) if isinstance(v, tuple) else v


# ---------------------------------------------------------------------------
# Roache -- CLASSIFY FIRST (rule 5). The value never gets to speak before the
# triple has been classified.
# ---------------------------------------------------------------------------
def classify_triple(f1, f2, f3):
    """f1 coarse, f2 middle, f3 fine. Returns (class, epsilon_21, epsilon_32)."""
    e21 = f2 - f1
    e32 = f3 - f2
    if e21 == 0.0 and e32 == 0.0:
        return "EXACT", e21, e32
    if e21 == 0.0 or e32 == 0.0:
        return "STAGNANT", e21, e32
    R = e32 / e21
    if R < 0.0:
        return "OSCILLATORY", e21, e32
    if R >= 1.0:
        return "DIVERGENT", e21, e32
    return "CONVERGING", e21, e32


def observed_order(e21, e32, r=R_NOMINAL):
    """Closed form, valid because r is CONSTANT across the family (r = 2.000
    exactly, by construction -- see a2gc_levels.json). No fixed-point
    iteration is needed and none is used."""
    return math.log(abs(e21 / e32)) / math.log(r)


def gci_fine(f2, f3, p, r=R_NOMINAL, fs=GCI_FS):
    """GCI on the FINE pair, Fs = 1.25 (rule 5). Only ever called on a
    CONVERGING, monotone triple -- the caller enforces that."""
    rel = abs((f3 - f2) / f3)
    return fs * rel / (r ** p - 1.0)


# ---------------------------------------------------------------------------
# Composition. compose_row hands back BOTH the pre-ceiling verdict and the
# capped one; compose_item reads verdict_before_ceiling. Reading the already-
# capped token here is the defect measured in D19M's compose_item on
# 2026-09-01 -- it makes the item-level ceiling structurally unable to fire.
# ---------------------------------------------------------------------------
def compose_row(row_id, verdict, ceiling_verdict=None, reason=None):
    assert verdict in VERDICTS, verdict
    capped = verdict
    capped_by_ceiling = False
    if ceiling_verdict is not None and ceiling_verdict in ("NOT A RESULT", "BLOCKED"):
        capped, capped_by_ceiling = ceiling_verdict, True
    return {
        "row": row_id,
        "verdict_before_ceiling": verdict,
        "verdict": capped,
        "capped_by_ceiling": capped_by_ceiling,
        "reason": reason,
    }


# Severity rank. PENDING is a queue state (CLAUDE.md rule 1) and may never
# soften a GATE FAIL, so it sits BELOW GATE FAIL here and above PASS.
SEVERITY = {"PASS": 0, "GATE REACHED": 1, "PENDING": 2,
            "GATE FAIL": 3, "BLOCKED": 4, "NOT A RESULT": 5}


def compose_item(rows, item_ceiling=None):
    """Item verdict composed from the rows' PRE-ceiling verdicts, so that an
    item-level ceiling can actually fire.

    Reading the already-capped row token as the primary input is the defect
    measured in D19M's compose_item on 2026-09-01: with the cap already applied
    at row level, the item ceiling has nothing left to change and can never
    fire. It is not inherited here.

    But the item must also never read LESS severe than a row whose own ceiling
    DID fire, so a fired row ceiling is folded in as a floor.
    """
    pre = [r["verdict_before_ceiling"] for r in rows]
    fired = [r["verdict"] for r in rows if r.get("capped_by_ceiling")]
    if not pre:
        v = "PENDING"
    elif all(x == "PASS" for x in pre):
        v = "PASS"
    else:
        v = max(pre, key=lambda x: SEVERITY[x])
    for f in fired:                      # a fired row ceiling is a floor
        if SEVERITY[f] > SEVERITY[v]:
            v = f
    out = {"verdict_before_ceiling": v, "verdict": v, "capped_by_ceiling": False}
    if item_ceiling in ("NOT A RESULT", "BLOCKED") and SEVERITY[item_ceiling] > SEVERITY[v]:
        out["verdict"] = item_ceiling
        out["capped_by_ceiling"] = True
    return out


# ---------------------------------------------------------------------------
def grade(run_root: Path):
    reg = birth_register()          # refuses (exit 2) before anything is read
    levels, rows = {}, []

    for lv in TRIPLE:
        d = run_root / lv
        rec = {"level": lv, "present": d.is_dir()}
        if not d.is_dir():
            levels[lv] = rec
            rows.append(compose_row(f"{lv}/completion", "PENDING",
                                    reason="level directory absent"))
            continue
        log = (d / "level.log").read_text(errors="replace") if (d / "level.log").exists() else ""
        mesh = (d / "mesh.log").read_text(errors="replace") if (d / "mesh.log").exists() else ""
        hist = []
        hp = d / "cd_history.json"
        if hp.exists():
            try:
                hist = list(json.loads(hp.read_text()))
            except Exception:
                hist = []
        # G-HIST: the history must be the SAME quantity the gate is graded on.
        # Its last sample must be the level's reported CD. A history on a
        # different scaling would corrupt the GATE I ratio silently, so a
        # mismatched history is DISCARDED (making GATE I NOT A RESULT) rather
        # than used.
        hist_ok = bool(hist) and abs(hist[-1] - read_cd(log)) <= 1e-6 * max(
            1e-12, abs(read_cd(log)))
        if hist and not hist_ok:
            hist = []
        rec.update({
            "cells": read_cells(mesh),
            "CD": read_cd(log),
            "CL": read_cl(log),
            "worst_residual": read_residual(log),
            "yplus_min_mean_max": list(read_yplus(log)),
            "max_vol_growth": read_vol_growth(mesh),
            "peak_rss_mib": read_peak_rss(log),
            "delta_iter": read_iter_delta(hist),
            "cd_history_n": len(hist),
            "rc": int((d / "RC").read_text().strip()) if (d / "RC").exists() else None,
        })
        # Resource failure vs numerical failure -- classified from the stage's
        # own cost.txt and container log, not inferred from rc alone.
        cost_txt = (d / "cost.txt").read_text(errors="replace") if (d / "cost.txt").exists() else ""
        cont = (d / "container.log").read_text(errors="replace") if (d / "container.log").exists() else ""
        if "overrun=YES-RUN-STOPPED" in cost_txt:
            fclass, freason = "BLOCKED", ("registered core-minute cap exceeded; "
                                          "an overrun STOPS the run, it does not "
                                          "get a new budget (rule 12)")
        elif rec.get("rc") in (137, 143) or "Killed" in cont or "out of memory" in cont.lower():
            fclass, freason = "BLOCKED", ("killed on memory or signal: the box could "
                                          "not hold this level")
        else:
            fclass, freason = "NOT A RESULT", "ran and did not produce a standing value"
        rec.update({
            "failure_class": fclass,
            "failure_reason": freason,
        })
        levels[lv] = rec

        # GATE C -- completion and trim
        cells_ok = rec["cells"] == SPEC["levels"][lv]["cells_predicted"]
        trim_ok = abs(rec["CL"] - CL_TARGET) <= TRIM_TOL
        if rec["rc"] != 0 or rec["CD"] == 0.0:
            # A RESOURCE failure is BLOCKED, not NOT A RESULT. The two are
            # different findings: BLOCKED says the box could not run it,
            # NOT A RESULT says it ran and the answer does not stand.
            kind, why = rec["failure_class"], rec["failure_reason"]
            rows.append(compose_row(f"{lv}/completion", kind,
                                    reason=f"rc={rec['rc']}, CD={rec['CD']}; {why}"))
        elif not cells_ok:
            rows.append(compose_row(f"{lv}/completion", "NOT A RESULT",
                                    reason=f"cell count {rec['cells']} != predicted "
                                           f"{SPEC['levels'][lv]['cells_predicted']}: "
                                           f"the family is not similar"))
        elif not trim_ok:
            rows.append(compose_row(f"{lv}/completion", "BLOCKED",
                                    reason=f"|CL-0.5| = {abs(rec['CL']-CL_TARGET):.3e} "
                                           f"> {TRIM_TOL:.1e}; reported, never estimated"))
        else:
            rows.append(compose_row(f"{lv}/completion", "PASS",
                                    reason=f"rc=0, cells {rec['cells']}, "
                                           f"|CL-0.5| = {abs(rec['CL']-CL_TARGET):.3e}"))
        rows.append(compose_row(
            f"{lv}/residual",
            "PASS" if 0.0 < rec["worst_residual"] <= RESIDUAL_TARGET else "GATE FAIL",
            reason=f"worst final residual {rec['worst_residual']:.3e} "
                   f"against {RESIDUAL_TARGET:.0e}"))

    # ---- GATE I: iterative change must be >= 10x smaller than the mesh step
    have = [lv for lv in TRIPLE if levels.get(lv, {}).get("CD")]
    iter_gate, ratios = {}, {}
    if len(have) == 3:
        f1, f2, f3 = (levels[lv]["CD"] for lv in TRIPLE)
        d21 = read_mesh_delta(f1, f2)
        d32 = read_mesh_delta(f2, f3)
        neighbour = {"L1": [d21], "L2": [d21, d32], "L3": [d32]}
        for lv in TRIPLE:
            dm = min(neighbour[lv])
            # A MISSING history is NOT a satisfied gate. delta_iter == 0 with no
            # samples behind it would make the ratio infinite and pass GATE I for
            # the wrong reason -- the planted-zero control proves the reader CAN
            # see a non-zero, not that a non-zero was ever there to see.
            if not levels[lv].get("cd_history_n"):
                iter_gate[lv] = False
                ratios[lv] = None
                rows.append(compose_row(
                    f"{lv}/iterative_vs_mesh", "PENDING",
                    reason="cd_history.json absent or empty: delta_iter could not "
                           "be measured, so GATE I is NOT satisfied and is NOT "
                           "assumed satisfied. Sanaa's SS0 clause 2 is the clause "
                           "most often skipped; it is not skipped here."))
                continue
            di = levels[lv]["delta_iter"]
            ratio = (dm / di) if di > 0 else float("inf")
            ratios[lv] = ratio
            ok = ratio >= ITER_RATIO_MIN
            iter_gate[lv] = ok
            rows.append(compose_row(
                f"{lv}/iterative_vs_mesh", "PASS" if ok else "NOT A RESULT",
                reason=f"Delta_mesh/delta_iter = {ratio:.2f} against >= "
                       f"{ITER_RATIO_MIN:.0f} (delta_iter {di:.3e} over "
                       f"{levels[lv]['cd_history_n']} samples, Delta_mesh "
                       f"{dm:.3e}); below it the observed order is iterative "
                       f"noise, not discretisation"))

    # ---- Roache: CLASSIFY FIRST
    roache = {"classified": False}
    if len(have) == 3:
        f1, f2, f3 = (levels[lv]["CD"] for lv in TRIPLE)
        cls, e21, e32 = classify_triple(f1, f2, f3)
        monotone = (cls == "CONVERGING")
        roache = {"classified": True, "class": cls, "CD": [f1, f2, f3],
                  "epsilon_21": e21, "epsilon_32": e32, "r": R_NOMINAL,
                  "monotone": monotone, "p": None, "GCI_fine_pct": None,
                  "band_on_CD": None}
        if not monotone:
            rows.append(compose_row("order/roache", "NOT A RESULT",
                                    reason=f"triple is {cls}; CD = {f1!r}, {f2!r}, "
                                           f"{f3!r}. No GCI is quoted: rule 5 forbids "
                                           f"a GCI when the three values are not "
                                           f"monotone."))
        else:
            p = observed_order(e21, e32)
            g = gci_fine(f2, f3, p)
            roache["p"] = p
            roache["GCI_fine_pct"] = g * 100.0
            roache["band_on_CD"] = [f3 * (1 - g), f3 * (1 + g)]
            in_band = P_BAND[0] <= p <= P_BAND[1]
            noise = any(not v for v in iter_gate.values())
            rows.append(compose_row(
                "order/roache", "PASS" if in_band else "GATE FAIL",
                ceiling_verdict="NOT A RESULT" if noise else None,
                reason=f"CONVERGING; p = {p:.4f} against band "
                       f"{P_BAND[0]}-{P_BAND[1]}; GCI(fine, Fs=1.25) = "
                       f"{g*100:.4f}% on CD = {f3:.10f}"
                       + ("; CAPPED: a level failed GATE I, so this order is "
                          "iterative noise and the row is NOT A RESULT" if noise else "")))

    else:
        # THREE LEVELS ARE THE MINIMUM FOR AN OBSERVED ORDER. If any member of
        # the triple did not stand, the item reports the triple's status and
        # reports NO p AND NO GCI. There is deliberately no two-level fallback
        # anywhere in this file: a p from two levels is not an observed order,
        # it is an assumption about the order written as a measurement.
        missing = [lv for lv in TRIPLE if lv not in have]
        blocked = [lv for lv in TRIPLE
                   if levels.get(lv, {}).get("failure_class") == "BLOCKED"]
        verdict = "BLOCKED" if blocked else (
            "PENDING" if all(not levels.get(lv, {}).get("present") for lv in missing)
            else "NOT A RESULT")
        roache = {"classified": False, "levels_standing": have,
                  "levels_missing": missing, "levels_blocked": blocked,
                  "p": None, "GCI_fine_pct": None, "band_on_CD": None}
        rows.append(compose_row(
            "order/triple", verdict,
            reason=f"only {len(have)} of 3 levels stand ({', '.join(have) or 'none'}); "
                   f"missing {', '.join(missing)}"
                   + (f"; BLOCKED: {', '.join(blocked)}" if blocked else "")
                   + ". Three levels are the minimum for an observed order, so NO p "
                     "is reported and NO GCI is quoted. The item does NOT fall back "
                     "to two levels."))

    item_ceiling = "NOT A RESULT" if (roache.get("classified") and
                                      not roache.get("monotone")) else None
    item = compose_item(rows, item_ceiling=item_ceiling)

    return {
        "_what": "A2-GC: MACH Tutorial Wing grid-convergence study, graded by the "
                 "frozen comparator against the thresholds in "
                 "cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md.",
        "_grader_md5": _self_md5(),
        "run_root": str(run_root),
        "birth_register": reg,
        "levels": levels,
        "iterative_gate_ratios": ratios,
        "roache": roache,
        "rows": rows,
        "item": item,
    }


def _self_md5():
    import hashlib
    return hashlib.md5(Path(__file__).read_bytes()).hexdigest()


SPEC = json.loads((Path(__file__).with_name("a2gc_levels.json")).read_text())


def main(argv):
    if "--selftest" in argv:
        try:
            reg = birth_register()
        except Refuse as e:
            print(str(e), file=sys.stderr)
            return 2
        print(json.dumps(reg, indent=1))
        # THE CONTROL ON THE CONTROL. A birth register that has never been
        # shown able to REFUSE is not evidence either. Each reader in turn is
        # replaced by a blind stub that always returns zero, and the register
        # must refuse on that reader -- every time, through the real code path.
        g = globals()
        names = [w["reader"] for w in reg["witnesses"]]
        caught = []
        for name in names:
            real = g[name]
            g[name] = (lambda *_a, **_k: (0.0, 0.0, 0.0)) if name == "read_yplus" \
                else (lambda *_a, **_k: 0.0)
            try:
                birth_register()
            except Refuse as exc:
                if name in str(exc):
                    caught.append(name)
            finally:
                g[name] = real
        if len(caught) != len(names):
            print(f"selftest failed: blinding {sorted(set(names)-set(caught))} "
                  f"did NOT make the register refuse", file=sys.stderr)
            return 2
        print(f"REFUSAL PATH DEMONSTRATED: blinding each of the {len(names)} "
              f"readers in turn made the register refuse, {len(caught)}/"
              f"{len(names)}.")
        return 0
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(argv[1])
    try:
        out = grade(root)
    except Refuse as e:
        print(str(e), file=sys.stderr)
        return 2
    dest = root / "a2gc_grade.json"
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps(out["item"], indent=1))
    print(f"written: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
