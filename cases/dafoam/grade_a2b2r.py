#!/usr/bin/env python3
"""A2-B2R comparator -- grades the independent lift-trim rung against the gates
frozen in cases/dafoam/A2_B2R_INDEPENDENT_TRIM_PREREGISTRATION.md.

FROZEN AT THE PRE-REGISTRATION COMMIT.  Committed BEFORE any compute, unlike
A2's own grader, which the A2 record (§R7) discloses was written after first
compute and therefore carried no independent authority.  Every threshold below
is quoted from the frozen document; nothing here computes a bar.

THE PLANTED-ZERO CONTROL IS RELATIVE, NOT ABSOLUTE (rule 3).
SO-2M died on an ABSOLUTE plant that did not port across functionals: its plant
was 2.479781 % against a 5.0 % band -- short of crossing by 2.016307x, so the
control could not have detected a blind reader.  Here the plant is

        P = K * (BAND/100) * |d_ref|,     d_ref = CD(R1_A4_anchor_cold)

with the sign set AWAY from d_ref, so the planted deviation is
|orig| + K*BAND and cancellation is unreachable by construction.  The plant is
written to a COPY OF THE LOG ON DISK and read back through the SAME parser and
the SAME gate function -- never patched in memory.

    GREEN legs  K = 3.0 -> planted deviation crosses the 0.5 % band by >= 3.0x.
                The reader MUST see it.  If it does not: PLANT_NOT_SEEN, exit 2.
    RED leg     K = 0.5 -> planted deviation is 0.25 %, i.e. 2.0x BELOW the
                crossing threshold.  The reader MUST NOT see it, and the control
                MUST refuse BY NAME with the literal token PLANT_NOT_SEEN.  A
                bare non-zero exit is not accepted: an unrelated crash also
                exits non-zero, and the token is what separates them.

The RED leg is run on the anchor's SELF-comparison, where the unplanted
deviation is identically 0, so the planted deviation is exactly K*BAND and the
leg's applicability does not depend on what the run measured.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a2b2r_age_guard as guard  # noqa: E402

RUNROOT_DEFAULT = "/home/ubuntu/certonomous-runs/A2B2R-independent-trim"

# --- frozen constants: A2's own measured anchor, blob 899352ae ---------------
A4_CD_A2 = 0.02124478277      # A2 RESULTS R1, row A4_final
A4_CL_A2 = 0.49994884178
A4_AOA = 1.1076573755757662
BAND = 0.5                    # PERCENT.  G5's threshold, byte for byte from A2 §6.
CL_TARGET = 0.5
TRIM_TOL = 5e-4               # G3
RESID_MAX = 1e-6              # G4: worst per-equation finalRes per row
DV_TOL = 1e-12                # planted control 1: DV set/readback
THICK_MIN = (0.4995, 0.5006)  # G2
THICK_MAX = (1.726, 1.730)
ANCHOR = "R1_A4_anchor_cold"
WARM = "R3_A4_anchor_warm"
ARMS = ("R2_trim_from_below", "R4_trim_from_above")
DRIVER_SHA = "c4f421497ae221ae1f8fb2f655530ea552e6372a935a6d3e0355ce81a4389cf0"
ROWS_SHA = "40a3fe7b559d4c1f66b78f1db64caa56d5efd4b93ee3ca5c480721bd76abe487"

RESULT_RE = re.compile(
    r"DECOMP_RESULT (\S+) CD ([-\d.eE+]+) CL ([-\d.eE+]+) AoA ([-\d.eE+]+) "
    r"thickcon_min ([-\d.eE+]+) thickcon_max ([-\d.eE+]+) volcon ([-\d.eE+]+)")
SETCHECK_RE = re.compile(
    r"DECOMP_SETCHECK (\S+) twist ([-\d.eE+]+) shape ([-\d.eE+]+) patchV ([-\d.eE+]+)")
FINALRES_RE = re.compile(r"(?:U0|U1|U2|he|p|nuTilda) initRes: [-\d.eE+]+ finalRes: ([-\d.eE+]+)")


def parse(log_path):
    """The ONLY reader.  Both the clean pass and every planted pass go through
    this function and through gate_row() below -- a plant that the parser cannot
    see is a plant the gate cannot see."""
    txt = open(log_path, encoding="utf-8", errors="replace").read()
    rows, order = {}, []
    for m in RESULT_RE.finditer(txt):
        rows[m.group(1)] = dict(CD=float(m.group(2)), CL=float(m.group(3)),
                                AoA=float(m.group(4)), tmin=float(m.group(5)),
                                tmax=float(m.group(6)), vol=float(m.group(7)))
        order.append(m.group(1))
    setchk = {m.group(1): max(float(x) for x in m.groups()[1:])
              for m in SETCHECK_RE.finditer(txt)}
    resid, trims = {}, {}
    parts = re.split(r"DECOMP_ROW_BEGIN (\S+)", txt)
    for i in range(1, len(parts), 2):
        rid, body = parts[i], parts[i + 1]
        fr = FINALRES_RE.findall(body)
        resid[rid] = max(float(x) for x in fr[-6:]) if len(fr) >= 6 else None
        t = re.search(r"DECOMP_TRIM_END \S+ AoA ([-\d.eE+]+)", body)
        trims[rid] = float(t.group(1)) if t else None
    return dict(rows=rows, order=order, setchk=setchk, resid=resid, trims=trims,
                all_done="DECOMP_ALL_ROWS_DONE" in txt,
                n_result_lines={r: len(re.findall(r"DECOMP_RESULT %s " % re.escape(r), txt))
                                for r in rows})


def gate_row(rows, rid, ref_id=ANCHOR):
    """|CD(rid) - CD(ref)| / CD(ref), in PERCENT.  The one quantity every G5/G6/G7
    gate is read off, and the one quantity the plant perturbs."""
    return abs(rows[rid]["CD"] - rows[ref_id]["CD"]) / abs(rows[ref_id]["CD"]) * 100.0


# --- the planted-zero control ------------------------------------------------

def plant_into_log(src_log, dst_log, target_row, ref_cd, K, self_compare=False):
    """Rewrite target_row's DECOMP_RESULT CD on disk, moving it AWAY from ref_cd.
    Returns the planted CD and the deviation the gate should now read (percent)."""
    txt = open(src_log, encoding="utf-8", errors="replace").read()
    m = None
    for mm in RESULT_RE.finditer(txt):
        if mm.group(1) == target_row:
            m = mm
    if m is None:
        raise RuntimeError("plant target row %s not in %s" % (target_row, src_log))
    cd = float(m.group(2))
    P = K * (BAND / 100.0) * abs(ref_cd)
    base = 0.0 if self_compare else (cd - ref_cd)
    sign = 1.0 if base >= 0 else -1.0          # AWAY from ref: cancellation unreachable
    planted = cd + sign * P
    line = m.group(0)
    newline = line.replace("CD %s" % m.group(2), "CD %.11f" % planted, 1)
    txt = txt[:m.start()] + newline + txt[m.end():]
    with open(dst_log, "w") as fh:
        fh.write(txt)
    expected = (abs(base) + P) / abs(ref_cd) * 100.0
    return planted, expected, P


def run_plant_leg(log_path, target_row, ref_cd, K, self_compare, tmpdir):
    """Plant, READ BACK FROM DISK through the same parser, re-evaluate the same
    gate.  Returns (token, detail).  token is PLANT_SEEN or PLANT_NOT_SEEN."""
    dst = os.path.join(tmpdir, "planted_%s_K%s.log" % (target_row, K))
    planted, expected, P = plant_into_log(log_path, dst, target_row, ref_cd, K, self_compare)
    if K != 0.0 and open(dst, "rb").read() == open(log_path, "rb").read():
        # the plant did not change the bytes on disk: nothing was planted, so a
        # "not seen" below would be uninformative.  Refuse rather than report.
        return "PLANT_NOT_SEEN", "the plant did not change the file on disk"
    back = parse(dst)
    if target_row not in back["rows"]:
        return "PLANT_NOT_SEEN", "reader lost row %s after the plant" % target_row
    read_cd = back["rows"][target_row]["CD"]
    if abs(read_cd - planted) > 1e-10:
        # what came back is not what was written: the value being graded did not
        # come from the file the plant went into.
        return "PLANT_NOT_SEEN", ("read-back %.11f != planted %.11f -- the graded value "
                                  "is not the one on disk" % (read_cd, planted))
    if self_compare:
        dev = abs(read_cd - ref_cd) / abs(ref_cd) * 100.0
    else:
        dev = abs(read_cd - back["rows"][ANCHOR]["CD"]) / abs(back["rows"][ANCHOR]["CD"]) * 100.0
    crossing = dev / BAND
    seen = dev > BAND
    detail = ("K=%.2f plant=%.6e planted_CD=%.11f read_back_CD=%.11f dev=%.6f%% "
              "band=%.3f%% crossing=%.3fx expected_dev=%.6f%%"
              % (K, P, planted, read_cd, dev, BAND, crossing, expected))
    return ("PLANT_SEEN" if seen else "PLANT_NOT_SEEN"), detail


def controls(log_path, rows, out=print):
    """GREEN legs must be SEEN; the RED sufficiency leg must NOT be, and must say
    so with the literal token.  Any GREEN failure refuses the whole rung."""
    ref_cd = rows[ANCHOR]["CD"]
    tmp = tempfile.mkdtemp(prefix="a2b2r_plant_")
    ok = True
    try:
        out("\n--- PLANTED-ZERO CONTROL 3 (relative plant, rule 3) ---")
        for row in (ANCHOR,) + tuple(r for r in ARMS if r in rows):
            self_cmp = (row == ANCHOR)
            tok, det = run_plant_leg(log_path, row, ref_cd, 3.0, self_cmp, tmp)
            good = tok == "PLANT_SEEN"
            out("  GREEN %-20s %-14s %s   %s" % (row, tok, "PASS" if good else "FAIL", det))
            if not good:
                out("PLANT_NOT_SEEN GREEN leg on %s: the reader cannot see a plant that "
                    "crosses its own band by 3.0x. The rung is NOT A RESULT." % row)
                sys.exit(2)
        tok, det = run_plant_leg(log_path, ANCHOR, ref_cd, 0.5, True, tmp)
        good = tok == "PLANT_NOT_SEEN"          # the refusal is DEMANDED, BY NAME
        out("  RED   %-20s %-14s %s   %s" % ("sufficiency", tok, "PASS" if good else "FAIL", det))
        if not good:
            out("PLANT_SUFFICIENCY_FAIL a sub-band plant (0.25%% against a 0.500%% band) "
                "flipped the gate. The control is not measuring the registered quantity.")
            sys.exit(2)
        ok = True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ok


# --- grading -----------------------------------------------------------------

def grade(runroot, out=print, skip_guard=False):
    log = os.path.join(runroot, "decomp.log")
    case = os.path.join(runroot, "case")
    man = os.path.join(runroot, "pin_manifest.json")
    t0 = os.path.join(runroot, "t0")
    rc_file = os.path.join(runroot, "RUN_RC.txt")

    out("=" * 104)
    out("A2-B2R -- INDEPENDENT LIFT-TRIM OF THE TWIST+SHAPE WING, GRADED ON THE FROZEN GATES")
    out("=" * 104)

    if not skip_guard:
        out("\n--- AGE GUARD (rule 4, adapted; premise 0/T-is-touched-last is FALSE here) ---")
        guard.cmd_verify(case, man, t0, [log, rc_file])

    # instrument identity: the frozen driver, unchanged, plus this rung's row spec
    inst = os.path.join(runroot, "instrument_sha256.txt")
    if os.path.isfile(inst):
        txt = open(inst).read()
        for name, sha in (("a2_decomposition_driver.py", DRIVER_SHA),
                          ("a2b2r_rows.json", ROWS_SHA)):
            good = sha in txt
            out("  instrument %-28s %s" % (name, "sha256 MATCHES frozen" if good
                                           else "sha256 MISMATCH -- NOT A RESULT"))
            if not good:
                out("REFUSE_INSTRUMENT_MISMATCH %s" % name)
                sys.exit(2)

    d = parse(log)
    rows, resid, setchk = d["rows"], d["resid"], d["setchk"]
    inner_rc = None
    if os.path.isfile(rc_file):
        m = re.search(r"INNER_RC=(\d+)", open(rc_file).read())
        inner_rc = int(m.group(1)) if m else None

    out("\n--- ROWS (every drag figure carries its lift) ---")
    out("%-22s %15s %14s %10s %21s %14s" %
        ("row", "CD", "CL", "AoA deg", "thick min/max", "worst finalRes"))
    for rid in d["order"]:
        r = rows[rid]
        c = resid.get(rid)
        out("%-22s %15.11f %14.11f %10.5f %10.6f/%10.6f %14s" %
            (rid, r["CD"], r["CL"], r["AoA"], r["tmin"], r["tmax"],
             "n/a" if c is None else "%.3e" % c))
    spec_rows = [ANCHOR, ARMS[0], WARM, ARMS[1]]
    missing = [r for r in spec_rows if r not in rows]
    for r in missing:
        out("%-22s %s" % (r, "NO VALUE -- NOT A RESULT (row did not complete)"))

    verdicts = {}

    # --- G1R anchor reproduction ------------------------------------------
    out("\n--- GATES (thresholds frozen before the run; G5's 0.5%% is A2's, byte for byte) ---")
    if ANCHOR not in rows:
        out("G1R anchor         ANCHOR ROW ABSENT -> whole rung NOT A RESULT")
        verdicts["G1R"] = "NOT A RESULT"
        return verdicts, rows
    a = rows[ANCHOR]
    g1_cd = abs(a["CD"] - A4_CD_A2) / A4_CD_A2 * 100.0
    g1_cl = abs(a["CL"] - A4_CL_A2)
    g1 = g1_cd <= BAND and g1_cl <= TRIM_TOL
    verdicts["G1R"] = "PASS" if g1 else "GATE FAIL"
    out("G1R anchor         CD dev %.5f%% (band %.3f%%)  |dCL| %.3e (band %.1e)  -> %s"
        % (g1_cd, BAND, g1_cl, TRIM_TOL, verdicts["G1R"]))

    # --- G2R geometry control (planted witness 2) --------------------------
    g2 = (THICK_MIN[0] <= a["tmin"] <= THICK_MIN[1] and THICK_MAX[0] <= a["tmax"] <= THICK_MAX[1])
    verdicts["G2R"] = "PASS" if g2 else "GATE FAIL"
    out("G2R geometry ctrl  thickcon %.9f / %.9f  (bands %s / %s) -> %s"
        % (a["tmin"], a["tmax"], THICK_MIN, THICK_MAX, verdicts["G2R"]))

    # --- planted control 1: DV set/readback --------------------------------
    worst_dv = max(setchk.values()) if setchk else float("nan")
    dv_ok = setchk and worst_dv <= DV_TOL
    out("control 1 (DV)     max set/readback deviation over %d rows: %.3e (tol %.0e) -> %s"
        % (len(setchk), worst_dv, DV_TOL, "PASS" if dv_ok else "FAIL"))

    # --- G4R completion, PER ROW, and the process rc stated separately -----
    out("\nG4R completion     process INNER_RC=%s  DECOMP_ALL_ROWS_DONE=%s"
        % (inner_rc, d["all_done"]))
    out("                   (NOTE: primalMinResTol=1e-8 is DAFoam's NORMALIZED TOTAL residual,")
    out("                    a DIFFERENT quantity from the per-equation finalRes the log prints.")
    out("                    G4R is graded on finalRes <= %.0e, registered from A2's measured"
        % RESID_MAX)
    out("                    4.15e-07..6.02e-07. A2's own G4 conflated the two; this one does not.)")
    for rid in spec_rows:
        if rid not in rows:
            verdicts["G4R:" + rid] = "NOT A RESULT"
            out("  %-22s NO DECOMP_RESULT LINE                       -> NOT A RESULT" % rid)
            continue
        c = resid.get(rid)
        n = d["n_result_lines"].get(rid, 0)
        good = (c is not None and c <= RESID_MAX and n == 1
                and setchk.get(rid, 1.0) <= DV_TOL)
        verdicts["G4R:" + rid] = "PASS" if good else "NOT A RESULT"
        out("  %-22s finalRes %s  result_lines=%d  dv=%.1e  -> %s"
            % (rid, "n/a" if c is None else "%.3e" % c, n, setchk.get(rid, float("nan")),
               verdicts["G4R:" + rid]))

    # --- G3R trim tolerance -------------------------------------------------
    for rid in ARMS:
        if rid not in rows:
            verdicts["G3R:" + rid] = "NOT A RESULT"
            out("G3R %-18s row absent -> NOT A RESULT" % rid)
            continue
        dcl = abs(rows[rid]["CL"] - CL_TARGET)
        good = dcl <= TRIM_TOL
        verdicts["G3R:" + rid] = "PASS" if good else "BLOCKED"
        out("G3R %-18s |CL-0.5| = %.3e  (band %.1e)  final AoA %.5f deg -> %s"
            % (rid, dcl, TRIM_TOL, rows[rid]["AoA"], verdicts["G3R:" + rid]))

    # --- G5 THE FALSIFIER, one gate per arm, threshold unchanged -----------
    for rid in ARMS:
        key = "G5-" + rid.split("_")[0]
        if rid not in rows:
            verdicts[key] = "NOT A RESULT"
            out("%-11s %-18s row produced no value -> NOT A RESULT (arm UNGRADED)" % (key, rid))
            continue
        if verdicts.get("G3R:" + rid) != "PASS":
            verdicts[key] = "NOT A RESULT"
            out("%-11s %-18s trim gate not met -> NOT A RESULT" % (key, rid))
            continue
        dev = gate_row(rows, rid)
        verdicts[key] = "PASS" if dev <= BAND else "GATE FAIL"
        out("%-11s %-18s |CD-CD(anchor)|/CD(anchor) = %.5f%%  (band %.3f%%) -> %s"
            % (key, rid, dev, BAND, verdicts[key]))

    # --- G6R cross-arm ------------------------------------------------------
    if all(r in rows for r in ARMS):
        dev = abs(rows[ARMS[1]]["CD"] - rows[ARMS[0]]["CD"]) / abs(a["CD"]) * 100.0
        verdicts["G6R"] = "PASS" if dev <= BAND else "GATE FAIL"
        out("G6R cross-arm      |CD(R4)-CD(R2)|/CD(anchor) = %.5f%%  (band %.3f%%) -> %s"
            % (dev, BAND, verdicts["G6R"]))
        if verdicts["G6R"] == "GATE FAIL":
            out("     FALSIFIER F1 FIRED: two independent trims both at CL=0.5 disagree on drag.")
            out("     A2 section 3's structural argument is FALSIFIED and is reported as such.")
    else:
        verdicts["G6R"] = "NOT A RESULT"
        out("G6R cross-arm      one or both arms produced no value -> NOT A RESULT")

    # --- G7R warm-start control --------------------------------------------
    if WARM in rows:
        dev = gate_row(rows, WARM)
        verdicts["G7R"] = "PASS" if dev <= BAND else "GATE FAIL"
        out("G7R warm control   |CD(R3)-CD(anchor)|/CD(anchor) = %.5f%%  (band %.3f%%) -> %s"
            % (dev, BAND, verdicts["G7R"]))
        if verdicts["G7R"] == "GATE FAIL":
            out("     FALSIFIER F3 FIRED: the one-process sequential protocol biases rows,")
            out("     which puts A2's own warm A4 row in question too.")
    else:
        verdicts["G7R"] = "NOT A RESULT"
        out("G7R warm control   row absent -> NOT A RESULT")

    controls(log, rows, out=out)

    # --- rung verdict -------------------------------------------------------
    out("\n--- RUNG VERDICT (mapping registered in the frozen document) ---")
    if verdicts["G1R"] != "PASS" or verdicts["G2R"] != "PASS" or not dv_ok:
        rung = "NOT A RESULT"
        why = "anchor or geometry control did not hold; nothing downstream is readable"
    else:
        armv = [verdicts.get("G5-" + r.split("_")[0]) for r in ARMS]
        if all(v == "PASS" for v in armv):
            rung = "PASS"
            why = "both independent trims landed on the anchor inside the 0.5% band"
        elif any(v == "GATE FAIL" for v in armv):
            rung = "GATE FAIL"
            why = "an independent trim did NOT land on the anchor; A2 section 3 is falsified"
        elif any(v == "PASS" for v in armv):
            rung = "GATE REACHED"
            why = "one arm graded PASS, the other produced no value; the falsifier fired once"
        else:
            rung = "NOT A RESULT"
            why = "no arm produced a value; the falsifier registered for A2 section 3 is again UNGRADED"
    out("  %s -- %s" % (rung, why))
    verdicts["RUNG"] = rung
    return verdicts, rows


# --- selftest: every gate and every control DRIVEN on synthetic logs ---------

def _synth(rows, all_done=True, resid=4.5e-07, dv=0.0):
    L = []
    for rid, (cd, cl, aoa, tmin, tmax, trim) in rows.items():
        L.append("DECOMP_ROW_BEGIN %s" % rid)
        L.append("DECOMP_SETCHECK %s twist %.3e shape %.3e patchV %.3e" % (rid, dv, dv, dv))
        if trim is not None:
            L.append("DECOMP_TRIM_BEGIN %s target_CL 0.500000" % rid)
            L.append("DECOMP_TRIM_END %s AoA %.11f" % (rid, aoa))
        for eq in ("U0", "U1", "U2", "he", "p", "nuTilda"):
            L.append("%s initRes: 1.0e-03 finalRes: %.9e nIters: 1" % (eq, resid))
        L.append("DECOMP_RESULT %s CD %.11f CL %.11f AoA %.11f thickcon_min %.9f "
                 "thickcon_max %.9f volcon 1.00007830385"
                 % (rid, cd, cl, aoa, tmin, tmax))
        L.append("DECOMP_ROW_END %s" % rid)
    if all_done:
        L.append("DECOMP_ALL_ROWS_DONE")
    return "\n".join(L) + "\n"


def _clean_rows(**over):
    base = {
        ANCHOR: (0.02124478277, 0.49994884178, A4_AOA, 0.500101380, 1.727944397, None),
        ARMS[0]: (0.02124501000, 0.50000012000, 1.10770, 0.500101380, 1.727944397, 0.5),
        WARM: (0.02124480000, 0.49994900000, A4_AOA, 0.500101380, 1.727944397, None),
        ARMS[1]: (0.02124460000, 0.49999980000, 1.10763, 0.500101380, 1.727944397, 0.5),
    }
    base.update(over)
    return base


def selftest():
    ok = True
    lines = []

    def cap(s=""):
        lines.append(str(s))

    def run(rowspec, **kw):
        del lines[:]
        tmp = tempfile.mkdtemp(prefix="a2b2r_grade_selftest_")
        try:
            rr = os.path.join(tmp, "run")
            os.makedirs(rr)
            open(os.path.join(rr, "decomp.log"), "w").write(_synth(rowspec, **kw))
            open(os.path.join(rr, "RUN_RC.txt"), "w").write("INNER_RC=0\n")
            try:
                v, _ = grade(rr, out=cap, skip_guard=True)
                return v, "\n".join(lines), 0
            except SystemExit as e:
                return None, "\n".join(lines), e.code
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def check(name, cond, extra=""):
        nonlocal ok
        print("  %-52s %s %s" % (name, "PASS" if cond else "FAIL", extra if not cond else ""))
        ok &= bool(cond)

    print("A2-B2R COMPARATOR SELFTEST")
    print("\n[clean run: every gate must PASS and the rung must be PASS]")
    v, txt, code = run(_clean_rows())
    check("no refusal", code == 0, "code=%r" % code)
    for g in ("G1R", "G2R", "G6R", "G7R", "G5-R2", "G5-R4"):
        check("%s PASS" % g, v and v.get(g) == "PASS", v and v.get(g))
    check("RUNG PASS", v and v["RUNG"] == "PASS", v and v.get("RUNG"))
    check("GREEN plant legs all SEEN", txt.count("PLANT_SEEN") == 3, txt.count("PLANT_SEEN"))
    check("RED sufficiency leg refused BY NAME",
          "RED   sufficiency          PLANT_NOT_SEEN PASS" in txt.replace("  PASS", " PASS")
          or ("RED" in txt and "PLANT_NOT_SEEN" in txt))

    print("\n[G5 is a real gate: move an arm just outside the 0.5%% band]")
    off = _clean_rows()
    off[ARMS[1]] = (0.02124478277 * 1.006, 0.50000000000, 1.11, 0.500101380, 1.727944397, 0.5)
    v, txt, code = run(off)
    check("G5-R4 GATE FAIL at +0.6%", v and v.get("G5-R4") == "GATE FAIL", v and v.get("G5-R4"))
    check("rung GATE FAIL", v and v["RUNG"] == "GATE FAIL", v and v.get("RUNG"))
    check("F1 cross-arm falsifier fired", "FALSIFIER F1 FIRED" in txt)

    print("\n[G5 is not trivially passable: just INSIDE the band must PASS]")
    inb = _clean_rows()
    inb[ARMS[1]] = (0.02124478277 * 1.004, 0.50000000000, 1.11, 0.500101380, 1.727944397, 0.5)
    v, txt, code = run(inb)
    check("G5-R4 PASS at +0.4%", v and v.get("G5-R4") == "PASS", v and v.get("G5-R4"))

    print("\n[a diverged arm: the registered branch, not a surprise]")
    div = _clean_rows()
    del div[ARMS[1]]
    v, txt, code = run(div, all_done=False)
    check("G5-R4 NOT A RESULT", v and v.get("G5-R4") == "NOT A RESULT", v and v.get("G5-R4"))
    check("rung GATE REACHED (one arm graded)", v and v["RUNG"] == "GATE REACHED",
          v and v.get("RUNG"))

    print("\n[both arms absent: the A2 outcome repeated]")
    non = _clean_rows()
    del non[ARMS[0]], non[ARMS[1]]
    v, txt, code = run(non, all_done=False)
    check("rung NOT A RESULT", v and v["RUNG"] == "NOT A RESULT", v and v.get("RUNG"))

    print("\n[anchor fails G1R: the whole rung dies before anything downstream]")
    bad = _clean_rows()
    bad[ANCHOR] = (0.02124478277 * 1.02, 0.49994884178, A4_AOA, 0.500101380, 1.727944397, None)
    v, txt, code = run(bad)
    check("G1R GATE FAIL", v and v.get("G1R") == "GATE FAIL", v and v.get("G1R"))
    check("rung NOT A RESULT", v and v["RUNG"] == "NOT A RESULT", v and v.get("RUNG"))

    print("\n[G2R: a shape vector that never reached the mesh reads thickcon 1.0]")
    flat = _clean_rows()
    flat[ANCHOR] = (0.02124478277, 0.49994884178, A4_AOA, 1.0, 1.0, None)
    v, txt, code = run(flat)
    check("G2R GATE FAIL on flat thickcon", v and v.get("G2R") == "GATE FAIL", v and v.get("G2R"))

    print("\n[G4R: an unconverged row is NOT A RESULT even with a value]")
    v, txt, code = run(_clean_rows(), resid=3.0e-05)
    check("G4R:anchor NOT A RESULT", v and v.get("G4R:" + ANCHOR) == "NOT A RESULT",
          v and v.get("G4R:" + ANCHOR))

    print("\n[planted control 1: a DV that did not take]")
    v, txt, code = run(_clean_rows(), dv=1.0e-06)
    check("DV control FAILs -> rung NOT A RESULT", v and v["RUNG"] == "NOT A RESULT",
          v and v.get("RUNG"))

    print("\n[G3R: a trim that missed its target is BLOCKED, not graded]")
    miss = _clean_rows()
    miss[ARMS[0]] = (0.02124501000, 0.50300000000, 1.15, 0.500101380, 1.727944397, 0.5)
    v, txt, code = run(miss)
    check("G3R:R2 BLOCKED", v and v.get("G3R:" + ARMS[0]) == "BLOCKED", v and v.get("G3R:" + ARMS[0]))
    check("G5-R2 NOT A RESULT (gate not reachable)",
          v and v.get("G5-R2") == "NOT A RESULT", v and v.get("G5-R2"))

    print("\n[THE PLANT ITSELF: the GREEN leg must refuse a BLIND reader]")
    tmp = tempfile.mkdtemp(prefix="a2b2r_blind_")
    try:
        rr = os.path.join(tmp, "run")
        os.makedirs(rr)
        lg = os.path.join(rr, "decomp.log")
        open(lg, "w").write(_synth(_clean_rows()))
        rows = parse(lg)["rows"]
        # a reader that cannot see the plant, simulated by planting with K=0:
        tok, det = run_plant_leg(lg, ANCHOR, rows[ANCHOR]["CD"], 0.0, True, tmp)
        check("K=0 plant is NOT SEEN (control is not stuck on SEEN)",
              tok == "PLANT_NOT_SEEN", tok)
        tok3, det3 = run_plant_leg(lg, ANCHOR, rows[ANCHOR]["CD"], 3.0, True, tmp)
        check("K=3 plant IS seen", tok3 == "PLANT_SEEN", tok3)
        crossing = float(re.search(r"crossing=([\d.]+)x", det3).group(1))
        check("K=3 crossing factor >= 2.0 (registered floor)", crossing >= 2.0,
              "crossing=%.3f" % crossing)
        check("K=3 crossing factor == 3.0 on the self-comparison", abs(crossing - 3.0) < 1e-6,
              "crossing=%.6f" % crossing)
        tokh, deth = run_plant_leg(lg, ANCHOR, rows[ANCHOR]["CD"], 0.5, True, tmp)
        crossing_h = float(re.search(r"crossing=([\d.]+)x", deth).group(1))
        check("K=0.5 sufficiency leg sits 2.0x BELOW the crossing threshold",
              tokh == "PLANT_NOT_SEEN" and abs(crossing_h - 0.5) < 1e-6,
              "%s crossing=%.6f" % (tokh, crossing_h))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runroot", default=RUNROOT_DEFAULT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--plantleg", metavar="K", type=float,
                    help="standalone plant leg on the anchor; exits 2 with the named token")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.plantleg is not None:
        log = os.path.join(a.runroot, "decomp.log")
        rows = parse(log)["rows"]
        tmp = tempfile.mkdtemp(prefix="a2b2r_plantleg_")
        try:
            tok, det = run_plant_leg(log, ANCHOR, rows[ANCHOR]["CD"], a.plantleg, True, tmp)
            print("%s %s" % (tok, det))
            return 0 if tok == "PLANT_SEEN" else 2
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    grade(a.runroot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
