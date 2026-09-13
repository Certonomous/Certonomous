#!/usr/bin/env python3
"""D6R3 DECOMP GRADER -- the grading path fixed at the D6R3_DECOMP_PREREGISTRATION.md commit.

It grades ONE cell of the decomposition sweep (a run of the FROZEN producer, published
configuration, at a given rank count) and it rolls the cells up into the sweep gates.

It REFUSES (exit 2) rather than degrade.  Rule 3: --selftest plants TWO known perturbations
into a real log in memory and requires this reader to REPORT BOTH before any silence of this
reader is believed.

usage: d6r3_decomp_grade.py <ARM> <RANKS> <LOG> <ARMDIR> <RC>   -> <ARM>_GRADE.json on stdout
       d6r3_decomp_grade.py --selftest <LOG>
       d6r3_decomp_grade.py --rollup <cellJSON> [<cellJSON> ...]
"""
import json
import os
import re
import sys

TOL = 1.0e-8           # primalMinResTol -- UNTOUCHED
DIFF = 100.0           # primalMinResTolDiff -- UNTOUCHED
GATE = TOL * DIFF      # 1.0e-06, the gate the case must meet

# --- the P0 reference, position 1, 28 ranks, published configuration (P0_20260913T190426Z.log) ---
P0_R1_MAXFIELD = "nuTilda"
P0_R1_MAXRES = "1.194718885139746e-07"
P0_R1_CD = 0.02090109066417552
P0_STEP1_U0_FINALRES = "0.0944846591692384"

CD_BAND_REL = 5.0e-4   # G-CD band, registered before compute
MOVE_FACTOR = 10.0     # G-MOVE threshold, registered before compute
DET_CELL_RANKS = 28    # the replication cell that carries G-DET

FIELDS = ("U0", "U1", "U2", "he", "p", "nuTilda")
RES = re.compile(r"^(\w+) initRes: (\S+) finalRes: (\S+) nIters: (\d+)\s*$")
CDRE = re.compile(r"^CD: (\S+) final: (\S+)\s*$")
DECOMP = re.compile(r"^Decomposition method (\w+) \[(\d+)\]")


class Refusal(Exception):
    pass


def parse_instances(text):
    """Split a run_model log into primal instances by the step counter restarting."""
    t, rows = None, []
    for ln in text.splitlines():
        if ln.startswith("Time = "):
            v = ln.split("=")[1].strip()
            if v == "0":
                continue
            t = int(v)
            continue
        m = RES.match(ln)
        if m and t is not None:
            rows.append((t, m.group(1), m.group(2), m.group(3), int(m.group(4))))
            continue
        m = CDRE.match(ln)
        if m and t is not None:
            rows.append((t, "CD", m.group(1), m.group(1), 0))
    inst, cur, last = [], [], 0
    for r in rows:
        if r[0] < last and cur:
            inst.append(cur)
            cur = []
        cur.append(r)
        last = r[0]
    if cur:
        inst.append(cur)
    return inst


def parse_decomp(text):
    """Every 'Decomposition method <m> [N]' the run printed, in order."""
    return [(m.group(1), int(m.group(2))) for m in
            (DECOMP.match(ln) for ln in text.splitlines()) if m]


def read_cell(arm, ranks, text, armdir, rc):
    out = {"arm": arm, "ranks": int(ranks), "gate_abs": GATE, "rc": rc,
           "instances": [], "checks": [], "verdict": None}

    def chk(name, ok, detail):
        out["checks"].append({"check": name, "ok": bool(ok), "detail": detail})
        return bool(ok)

    ok = True

    # --- IC-A: LEVER ACTIVITY (L-40).  The decomposition the ranks actually built, read back
    # --- from the runtime log, must be the one this cell asked for.  pyDAFoam.py:2228 rewrites
    # --- system/decomposeParDict from self.nProcs, so the dict on disk proves nothing.
    dec = parse_decomp(text)
    out["decomposition_readback"] = ["%s[%d]" % (m, n) for m, n in dec]
    got = sorted({n for _, n in dec})
    ok &= chk("IC-A decomposition readback == %d ranks" % int(ranks),
              len(dec) >= 1 and got == [int(ranks)],
              "log printed %s; this cell requested %d" % (out["decomposition_readback"], int(ranks)))
    ok &= chk("IC-A three condition dirs decomposed", len(dec) == 3,
              "%d 'Decomposition method' lines, expected 3 (mp04 mp05 mp06)" % len(dec))

    # --- IC-F: the rule-17 mesh-read gate the producer wrote on rank 0
    r17p = os.path.join(armdir, "d6r3_rule17.json")
    if os.path.isfile(r17p):
        r17 = json.load(open(r17p))
        bad = [p for p, v in r17.items() if v.get("verdict") != "OK"]
        ok &= chk("IC-F rule-17 mesh read OK for all three", not bad,
                  "verdicts %s" % json.dumps({p: r17[p].get("verdict") for p in r17}))
    else:
        ok &= chk("IC-F rule-17 mesh read OK for all three", False,
                  "no d6r3_rule17.json at %s" % r17p)

    # --- IC-D': the run ended the way an arm of this design may end.  rc==0, or rc==1 WITH the
    # --- AnalysisError that names the position that failed.  NOT rc==0 as a control: the
    # --- PREDICTED outcome of this arm is a non-zero rc, so rc==0 cannot be an instrument
    # --- control here (the predecessor's IC-4 defect, disclosed and not repeated).
    ae = re.findall(r"<class DAFoamSolver>: Error calling solve_nonlinear\(\), Primal solution failed!", text)
    named = re.findall(r"'(cl0\d)\.coupling\.solver' <class DAFoamSolver>", text)
    out["analysis_error_positions"] = named
    ok &= chk("IC-D' termination is rc==0 or rc==1 with a named AnalysisError",
              rc == 0 or (rc == 1 and len(ae) >= 1 and len(named) >= 1),
              "rc=%s, AnalysisError count=%d, named=%s" % (rc, len(ae), named))

    # --- IC-G: mesh identity.  Recorded here, compared across cells in --rollup.
    # REPAIR 1 (ADDENDUM 1, 2026-09-13, VERIFICATION_CHARTER s2d.1): this reader looked ONLY for
    # constant/polyMesh/points and this mesh is stored GZIPPED.  It returned md5=None on every
    # cell -- a control that reads nothing.  It is repaired to accept either spelling and to NAME
    # the file it hashed, so a future silence is attributable.  The pre-repair reading, recorded
    # beside the repaired one per condition (4): mp04_points = "" (empty), md5 = None, IC-G FAIL
    # on every cell.  The blindness failed CLOSED -- it could not have moved a verdict toward a
    # pass -- which is why it is a repair and not a widening.
    pts = None
    for cand in ("points", "points.gz"):
        c = os.path.join(armdir, "mp04", "constant", "polyMesh", cand)
        if os.path.isfile(c):
            pts = c
            break
    if pts:
        import hashlib
        h = hashlib.md5(open(pts, "rb").read()).hexdigest()
    else:
        h = None
    out["mp04_points_md5"] = h
    out["mp04_points_file"] = pts
    ok &= chk("IC-G mp04 polyMesh points readable for the cross-cell identity check",
              h is not None, "md5=%s from %s" % (h, pts))

    inst = parse_instances(text)
    if not inst:
        chk("PARSE at least one primal instance", False, "no instance found in log")
        out["verdict"] = "NOT A RESULT"
        return out
    chk("PARSE at least one primal instance", True, "%d instance(s)" % len(inst))

    for i, rows in enumerate(inst, 1):
        s1 = {r[1]: r for r in rows if r[0] == 1}
        last_t = max(r[0] for r in rows)
        at_end = {r[1]: r for r in rows if r[0] == last_t}
        res = {f: float(at_end[f][2]) for f in FIELDS if f in at_end}
        maxf = max(res, key=res.get) if res else None
        cd = at_end.get("CD")
        u0 = s1.get("U0")
        rp = s1.get("p")
        out["instances"].append({
            "position": i,
            "last_time": last_t,
            "residuals_at_last_time": {f: "%.16g" % v for f, v in res.items()},
            "max_field": maxf,
            "max_residual": None if maxf is None else "%.16g" % res[maxf],
            "multiple_of_primalMinResTol": None if maxf is None else round(res[maxf] / TOL, 4),
            "passes_gate": None if maxf is None else bool(res[maxf] < GATE),
            "step1_U0_finalRes": None if u0 is None else u0[3],
            "step1_p": None if rp is None else {"initRes": rp[2], "finalRes": rp[3], "nIters": rp[4]},
            "CD": None if cd is None else cd[2],
        })

    p1 = out["instances"][0]

    # --- The MECHANISM PREDICTION, registered before compute and readable either way.
    # --- The smoothSolver GaussSeidel smoother is processor-block in parallel, so step 1 of
    # --- position 1 must DIFFER from the 28-rank value at any other rank count, and must be
    # --- EXACTLY it at 28.  Both branches are reachable; neither is an instrument control.
    if int(ranks) == DET_CELL_RANKS:
        out["prediction_step1_U0"] = {
            "predicted": "EXACTLY %s" % P0_STEP1_U0_FINALRES,
            "observed": p1["step1_U0_finalRes"],
            "held": p1["step1_U0_finalRes"] == P0_STEP1_U0_FINALRES}
    else:
        out["prediction_step1_U0"] = {
            "predicted": "DIFFERENT from %s (processor-block GaussSeidel)" % P0_STEP1_U0_FINALRES,
            "observed": p1["step1_U0_finalRes"],
            "held": p1["step1_U0_finalRes"] != P0_STEP1_U0_FINALRES}

    # --- G-DET, carried by the 28-rank cell alone.
    if int(ranks) == DET_CELL_RANKS:
        det = (p1["max_field"] == P0_R1_MAXFIELD and p1["max_residual"] == P0_R1_MAXRES)
        out["G-DET"] = {"gate": "position-1 max residual reproduces P0 to all printed digits",
                        "reference": "%s %s" % (P0_R1_MAXFIELD, P0_R1_MAXRES),
                        "measured": "%s %s" % (p1["max_field"], p1["max_residual"]),
                        "verdict": "PASS" if det else "GATE FAIL"}
        ok &= chk("G-DET replication", det, out["G-DET"]["measured"])

    # --- G-CD, per cell: position-1 CD within the registered band of the P0 value.
    if p1["CD"] is not None:
        rel = abs(float(p1["CD"]) - P0_R1_CD) / P0_R1_CD
        out["G-CD"] = {"gate": "|CD - P0_CD|/P0_CD < %.1e" % CD_BAND_REL,
                       "measured_CD": p1["CD"], "relative_deviation": "%.6e" % rel,
                       "verdict": "PASS" if rel < CD_BAND_REL else "GATE FAIL"}

    # --- the cell's own gate reading: does the PUBLISHED case pass at this rank count?
    out["cell_gate"] = {
        "gate": "position-1 max residual at endTime < %.1e" % GATE,
        "measured": p1["max_residual"], "field": p1["max_field"],
        "multiple_of_primalMinResTol": p1["multiple_of_primalMinResTol"],
        "verdict": "PASS" if p1["passes_gate"] else "GATE FAIL"}

    out["instrument_controls_all_ok"] = bool(ok)
    out["verdict"] = out["cell_gate"]["verdict"] if ok else "NOT A RESULT"
    return out


def rollup(cells):
    r = {"cells": [], "gates": {}}
    usable = []
    for c in cells:
        p1 = c["instances"][0] if c["instances"] else {}
        r["cells"].append({
            "arm": c["arm"], "ranks": c["ranks"], "verdict": c["verdict"],
            "position1_max_field": p1.get("max_field"),
            "position1_max_residual": p1.get("max_residual"),
            "position1_multiple": p1.get("multiple_of_primalMinResTol"),
            "position1_CD": p1.get("CD"),
            "position1_step1_U0_finalRes": p1.get("step1_U0_finalRes"),
            "positions_reached": len(c["instances"]),
            "position2_max_field": c["instances"][1].get("max_field") if len(c["instances"]) > 1 else None,
            "position2_max_residual": c["instances"][1].get("max_residual") if len(c["instances"]) > 1 else None,
            "mp04_points_md5": c.get("mp04_points_md5"),
            "rc": c.get("rc"),
        })
        if c["verdict"] in ("PASS", "GATE FAIL") and p1.get("max_residual"):
            usable.append((c["ranks"], float(p1["max_residual"]), c))

    # IC-G across cells: every cell read the SAME mesh.  Only the decomposition varied.
    md5s = {c.get("mp04_points_md5") for c in cells}
    r["gates"]["IC-G-cross"] = {
        "gate": "all cells read one identical mp04 polyMesh/points",
        "measured": sorted(str(m) for m in md5s),
        "verdict": "PASS" if len(md5s) == 1 and None not in md5s else "GATE FAIL"}

    if len(usable) < 3:
        r["gates"]["G-MOVE"] = {"verdict": "NOT A RESULT",
                                "why": "%d usable cells, the registration requires 3" % len(usable)}
        r["gates"]["G-PROD"] = {"verdict": "NOT A RESULT", "why": "sweep not readable"}
        return r

    vals = [v for _, v, _ in usable]
    spread = max(vals) / min(vals)
    r["gates"]["G-MOVE"] = {
        "gate": "max/min of position-1 max residual across cells >= %.1f" % MOVE_FACTOR,
        "measured_spread": "%.4f" % spread,
        "min": "%.16g at %d ranks" % (min(vals), [n for n, v, _ in usable if v == min(vals)][0]),
        "max": "%.16g at %d ranks" % (max(vals), [n for n, v, _ in usable if v == max(vals)][0]),
        "verdict": "GATE REACHED" if spread >= MOVE_FACTOR else "GATE FAIL"}

    prod = [(n, v) for n, v, _ in usable if n <= 20]
    r["gates"]["G-PROD"] = {
        "gate": "position-1 max residual < %.1e at every rank count <= 20" % GATE,
        "measured": ["%d ranks: %.16g" % (n, v) for n, v in sorted(prod)],
        "verdict": ("PASS" if prod and all(v < GATE for _, v in prod)
                    else ("GATE FAIL" if prod else "NOT A RESULT"))}

    cds = [(n, float(c["instances"][0]["CD"])) for n, _, c in usable if c["instances"][0]["CD"]]
    if cds:
        rels = [abs(v - P0_R1_CD) / P0_R1_CD for _, v in cds]
        r["gates"]["G-CD"] = {
            "gate": "every cell's position-1 CD within %.1e relative of the P0 value" % CD_BAND_REL,
            "measured": ["%d ranks: %.17g (rel %.3e)" % (n, v, abs(v - P0_R1_CD) / P0_R1_CD)
                         for n, v in sorted(cds)],
            "max_relative_deviation": "%.6e" % max(rels),
            "CD_spread_relative": "%.6e" % ((max(v for _, v in cds) - min(v for _, v in cds))
                                            / P0_R1_CD),
            "verdict": "PASS" if max(rels) < CD_BAND_REL else "GATE FAIL"}

    ordc = [(n, c) for n, _, c in usable if len(c["instances"]) > 1]
    if ordc:
        rats = []
        for n, c in ordc:
            a = float(c["instances"][0]["max_residual"])
            b = float(c["instances"][1]["max_residual"])
            rats.append((n, b / a))
        r["gates"]["G-ORD"] = {
            "gate": "where position 2 is reached, position2/position1 max residual >= 10",
            "measured": ["%d ranks: %.4g" % (n, x) for n, x in sorted(rats)],
            "verdict": "PASS" if all(x >= 10.0 for _, x in rats) else "GATE FAIL"}
    else:
        r["gates"]["G-ORD"] = {"verdict": "NOT A RESULT",
                               "why": "no cell reached position 2"}
    return r


# --------------------------------------------------------------------------------------------
# RULE 3 -- THE PLANTED CONTROL.  Two known perturbations, planted into a REAL log in memory,
# read back through the SAME code path.  A reader that cannot see them refuses everything.
PLANT_RES = "9.876543210987654e-03"
PLANT_DECOMP = 99


def selftest(path):
    raw = open(path, errors="replace").read()
    base = parse_instances(raw)
    if not base:
        print("SELFTEST REFUSE: the control log has no instance to plant into")
        return 2
    # locate the LAST nuTilda residual line of instance 1 and plant a value into it
    lines = raw.splitlines()
    idx = [i for i, ln in enumerate(lines) if ln.startswith("nuTilda initRes: ")]
    if not idx:
        print("SELFTEST REFUSE: no nuTilda line to plant into")
        return 2
    target = idx[0]
    for i in idx:
        if i > target:
            break
    # plant into the line that carries the LAST time of instance 1
    lt = max(r[0] for r in base[0])
    seen_t, target = None, None
    for i, ln in enumerate(lines):
        if ln.startswith("Time = "):
            v = ln.split("=")[1].strip()
            seen_t = int(v) if v.isdigit() else seen_t
        if seen_t == lt and ln.startswith("nuTilda initRes: ") and target is None:
            target = i
    if target is None:
        print("SELFTEST REFUSE: could not locate the endTime nuTilda line")
        return 2
    old = lines[target]
    lines[target] = re.sub(r"initRes: \S+", "initRes: " + PLANT_RES, old)
    dsub = [i for i, ln in enumerate(lines) if DECOMP.match(ln)]
    if not dsub:
        print("SELFTEST REFUSE: no 'Decomposition method' line to plant into")
        return 2
    lines[dsub[0]] = re.sub(r"\[\d+\]", "[%d]" % PLANT_DECOMP, lines[dsub[0]])
    mutated = "\n".join(lines)

    i2 = parse_instances(mutated)
    saw_res = i2 and any(r[1] == "nuTilda" and r[2] == PLANT_RES
                         for r in i2[0] if r[0] == max(x[0] for x in i2[0]))
    saw_dec = any(n == PLANT_DECOMP for _, n in parse_decomp(mutated))
    base_clean = not any(n == PLANT_DECOMP for _, n in parse_decomp(raw))

    print(json.dumps({
        "control_log": path,
        "planted_residual": PLANT_RES, "reader_reported_residual": bool(saw_res),
        "planted_decomposition": PLANT_DECOMP, "reader_reported_decomposition": bool(saw_dec),
        "unplanted_log_is_clean_of_the_plant": bool(base_clean),
        "verdict": "READER SEES THE PLANT" if (saw_res and saw_dec and base_clean)
                   else "REFUSE -- reader is blind to a planted perturbation"}, indent=1))
    return 0 if (saw_res and saw_dec and base_clean) else 2


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    if a[0] == "--selftest":
        sys.exit(selftest(a[1]))
    if a[0] == "--rollup":
        cells = [json.load(open(p)) for p in a[1:]]
        print(json.dumps(rollup(cells), indent=1))
        sys.exit(0)
    arm, ranks, log, armdir, rc = a[0], a[1], a[2], a[3], int(a[4])
    txt = open(log, errors="replace").read()
    print(json.dumps(read_cell(arm, ranks, txt, armdir, rc), indent=1))
