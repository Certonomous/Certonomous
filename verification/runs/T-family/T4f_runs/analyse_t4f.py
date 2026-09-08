#!/usr/bin/env python3
"""DRAFT time-averaged comparator for T4f -- the TRANSIENT / URANS impinging-jet rung.

Grades peak(UMean profile)/U_bulk at r/D = 1, 2, 3 against the SAME ERCOFTAC case025 bands the
T4/T4b/T4d/T4e rungs use (byte-identical, re-read from the held files).  The reader is the FROZEN
analyse_t4.sample_profile / peak_of, imported and NEVER re-implemented.  Because the frozen reader
hard-codes `fields (U)`, this comparator makes a SCRATCH COPY and PROMOTES `UMean` into a field object
named `U`, then reads the frozen way -- no frozen file is edited.

ONE MESH -> NO Roache triple -> NO GCI, NO observed order, NO discretisation bound (CLAUDE.md rule 5).
This is a validation-against-reference of the time-averaged field, gated but explicitly NOT GCI'd.  The
reason is physics: the coarse/medium meshes went STEADY in T4d, so a c/m/f transient triple would be
incoherent (T4f_PREREGISTRATION.md section 3).

Gates: C1/C1b/C2/C3 (reused, on the time-mean); C4 the frozen planted-zero control on the promoted mean
field; C5 strict completion (mark_done_t4f.py); PLUS the NEW transient-statistics gates S1-S4 read from
stationarity_t4f.py + the Co max from log.solve.  Two NEW planted controls (rule 3): the UMean->U
promotion control below, and stationarity_t4f.py's own classifier control.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is an explicit sys.exit(2).

STATUS: DRAFT.  Not frozen, not run against any real case.  Some gate wiring (C1/C1b/C2/C3, the S4
dt-halving spot check) is specified but left as clearly-marked stubs for completion + diff at the
section-3 review; the load-bearing NEW logic (UMean->U promotion, its planted control, the band grade,
the no-triple/no-GCI structure) is implemented.

PARALLEL (verification ruling 19b7330a): the run is decomposed (method simple).  This comparator grades
the RECONSTRUCTED fields in the case root (launch_t4f.sh runs reconstructPar; ruling condition 3) -- the
UMean it promotes and the G-row profiles it samples are the reconstructed fields, read exactly as for a
serial run.  The sampledSets time series stationarity_t4f.py reads is written to the case-root
postProcessing by the parallel functionObject (gathered), so it needs no reconstruction.  S3's max Co is
read from the combined master log.solve.  Verdict-safety under decomposition rests on the ruling's
ergodic argument + T4f's own S1/S2 gates (the converged time-average of a stationary flow is
decomposition-invariant to within the S2 sampling tolerance 1e-3, far inside the 0.02 band) -- cited, not
re-derived here (T4f_PARALLEL_DECOMPOSITION_RULING_2026-09-08.md).

Exit codes: 0 graded ; 2 REFUSAL (a precondition failed, or a planted control found the reader blind)
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T4 = os.path.join(os.path.dirname(HERE), "T4_runs")
sys.path.insert(0, T4)
sys.path.insert(0, HERE)
import analyse_t4 as A          # noqa: E402  FROZEN reader (blob 6f362447)
import stationarity_t4f as S    # noqa: E402  NEW instrument (S1/S2/period + its planted control)

CASE = "T4f_IJ_f"
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
EXIT_OK, EXIT_REFUSE = 0, 2
MAXCO = 0.9                     # S3 registered Courant bound


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ------------------------------------------------- the UMean -> U promotion
def promote_umean_to_u(case_dir, time):
    """Copy the case to scratch and rewrite <time>/UMean's FoamFile object to `U`, overwriting
    <time>/U, so the FROZEN analyse_t4.sample_profile (fields (U)) reads the TIME-AVERAGED field.
    Returns the scratch case dir (caller removes it).  NEVER writes into the live case."""
    tmp = tempfile.mkdtemp(prefix="t4f_prom_")
    dst = os.path.join(tmp, os.path.basename(case_dir))
    shutil.copytree(case_dir, dst, symlinks=True)
    if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
        shutil.rmtree(tmp, ignore_errors=True)
        refuse("promotion scratch copy resolved INSIDE the case tree; refusing")
    umean = os.path.join(dst, str(time), "UMean")
    if not os.path.isfile(umean):
        shutil.rmtree(tmp, ignore_errors=True)
        refuse("no UMean at %s/%s -- fieldAverage produced no time-averaged field; the transient "
               "measurement does not exist" % (case_dir, time))
    txt = open(umean).read()
    txt2, n = re.subn(r"(object\s+)UMean(\s*;)", r"\g<1>U\g<2>", txt)
    if n != 1:
        shutil.rmtree(tmp, ignore_errors=True)
        refuse("UMean FoamFile has %d `object UMean;` lines, expected exactly 1 -- refusing to "
               "promote a field whose header cannot be located structurally" % n)
    open(os.path.join(dst, str(time), "U"), "w").write(txt2)
    return tmp, dst


# ---------- NEW planted-zero control on the promotion path (CLAUDE.md rule 3) ----------
def promotion_planted_control(case_dir, time):
    """A reader that promotes UMean->U is not evidence until it is shown able to SEE a non-zero planted
    into UMean AND to read 0 when nothing is planted.  Mirrors the FROZEN analyse_t4 control's shape
    (aimed plant via the mesh's own cell centres, a blind arm, structural location) but on the UMean
    source field.  Reuses A.read_cell_centres / A.parse_internal_vectors / A.sample_profile unchanged."""
    # --- blind arm: promote unmodified UMean, read twice, require identical (0 change) ---
    tmp0, dst0 = promote_umean_to_u(case_dir, time)
    try:
        base = A.sample_profile(dst0, time, 1.0, FOAM)
        if base is None:
            refuse("promotion control: reader returned nothing on the unplanted promoted copy")
        again = A.sample_profile(dst0, time, 1.0, FOAM)
        dneg = max(abs(a[1] - b[1]) for a, b in zip(base, again))
        if dneg != 0.0:
            refuse("promotion control BLIND ARM FAILED: reader returned %.17g on identical bytes -- "
                   "noisy reader, its zeros are not zeros" % dneg)
    finally:
        shutil.rmtree(tmp0, ignore_errors=True)

    # --- positive arm: plant into UMean at the aimed cell, promote, require a visible change ---
    tmp1 = tempfile.mkdtemp(prefix="t4f_pz_")
    try:
        dst = os.path.join(tmp1, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)
        cc = A.read_cell_centres(dst, time, FOAM)
        if cc is None:
            refuse("promotion control: could not read cell centres to AIM the plant")
        _, centres = cc
        # aim at the cell nearest the G1 line's UMean peak
        tmpb, dstb = promote_umean_to_u(case_dir, time)
        try:
            b = A.sample_profile(dstb, time, 1.0, FOAM)
        finally:
            shutil.rmtree(tmpb, ignore_errors=True)
        y_peak = max(b, key=lambda t: t[1])[0] * A.D
        target = (1.0 * A.D, y_peak, 0.0)
        best_i = min(range(len(centres)),
                     key=lambda i: (centres[i][0] - target[0]) ** 2
                     + (centres[i][1] - target[1]) ** 2 + centres[i][2] ** 2)
        umean = os.path.join(dst, str(time), "UMean")
        pu = A.parse_internal_vectors(open(umean).read())
        if pu is None:
            refuse("promotion control: could not locate UMean internalField STRUCTURALLY")
        uidx, uvals = pu
        if best_i >= len(uidx):
            refuse("promotion control: cell centres and UMean entries disagree in length")
        line_no, comp_before = uidx[best_i], uvals[best_i][0]
        lines = open(umean).read().splitlines(True)
        m = re.match(r"\s*\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)\s*$", lines[line_no])
        lines[line_no] = "(%.17g %s %s)\n" % (comp_before + A.PLANT, m.group(2), m.group(3))
        open(umean, "w").write("".join(lines))
        # now promote the PLANTED UMean -> U and read
        txt = open(umean).read()
        txt2, _ = re.subn(r"(object\s+)UMean(\s*;)", r"\g<1>U\g<2>", txt)
        open(os.path.join(dst, str(time), "U"), "w").write(txt2)
        shutil.rmtree(os.path.join(dst, "postProcessing"), ignore_errors=True)
        got = A.sample_profile(dst, time, 1.0, FOAM)
        if got is None:
            refuse("promotion control: reader returned nothing after the planted promotion")
        dpos = max(abs(a[1] - g[1]) for a, g in zip(b, got))
        if dpos == 0.0:
            refuse("promotion control POSITIVE ARM FAILED: a %.6g m/s plant into UMean at line %d was "
                   "INVISIBLE after promotion -- the promotion or reader is BLIND to the mean field, "
                   "every T4f number is withdrawn" % (A.PLANT, line_no + 1))
        return dict(status="PASS", plant=A.PLANT, planted_line=line_no + 1, planted_cell=best_i,
                    recovered_max_abs_change=dpos, blind_arm=dneg)
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)


# --------------------------------------------------------- Courant (S3)
def max_courant(case_dir):
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return None
    mx = None
    for m in re.finditer(r"Courant Number mean:\s*\S+\s+max:\s*([0-9.eE+-]+)",
                         open(log, errors="replace").read()):
        v = float(m.group(1))
        mx = v if mx is None else max(mx, v)
    return mx


# --------------------------------------------------------------------- main
def main():
    global FOAM
    ap = argparse.ArgumentParser()
    ap.add_argument("--foam-bashrc", default=FOAM)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t4f.json"))
    a = ap.parse_args()
    FOAM = a.foam_bashrc

    case_dir = os.path.join(HERE, CASE)

    # --- C5: strict completion must have passed (marker on disk; mark_done_t4f decides, not us) ---
    if not os.path.isfile(os.path.join(HERE, "DONE.%s" % CASE)):
        refuse("no DONE.%s -- run mark_done_t4f.py; if it says NOT DONE that is the answer and this "
               "comparator does not overrule it (C5)." % CASE)
    time = A.latest_time(case_dir)
    if time is None:
        refuse("%s has no time directory beyond 0" % CASE)

    # --- rule 3: planted controls BEFORE any number is believed ---
    prom = promotion_planted_control(case_dir, time)                 # NEW: UMean->U promotion
    print("promotion planted-zero control: PASS (recovered %.6g from a %.6g plant into UMean; "
          "blind arm %.17g)" % (prom["recovered_max_abs_change"], prom["plant"], prom["blind_arm"]))
    # C4: the FROZEN control on the promoted MEAN field
    tmpp, dstp = promote_umean_to_u(case_dir, time)
    try:
        c4 = A.planted_zero_control(dstp, time, FOAM, r_over_d=1.0)
    finally:
        shutil.rmtree(tmpp, ignore_errors=True)
    print("frozen C4 planted-zero control on the mean field: %s" % c4["status"])

    # --- S1-S4: the transient-statistics gates (stationarity_t4f + Co) ---
    stat = S.evaluate(case_dir, FOAM, stations=[r for r, _ in ((1.0, "G1"), (2.0, "G2"), (3.0, "G3"))])
    co_max = max_courant(case_dir)
    s3 = (co_max is not None and co_max <= MAXCO)
    s_ok = stat["S1"] and stat["S2"] and s3 and stat["S4"]
    print("S1 stationarity=%s  S2 window=%s  S3 Co(max=%s)<=%.2f=%s  S4 dt=%s"
          % (stat["S1"], stat["S2"], co_max, MAXCO, s3, stat["S4"]))

    # --- the band grade, per row, from the peak of the TIME-AVERAGED profile.  NO triple, NO GCI. ---
    rows = []
    for rid, rd, reffile, half in A.GRADED:
        ref, _ = A.ref_peak(reffile)
        tmpg, dstg = promote_umean_to_u(case_dir, time)
        try:
            prof = A.sample_profile(dstg, time, rd, FOAM)
        finally:
            shutil.rmtree(tmpg, ignore_errors=True)
        if prof is None:
            refuse("could not sample r/D=%.1f on the mean field -- a missing number is not a zero" % rd)
        val = A.peak_of(prof)[0]
        in_band = (ref - half) <= val <= (ref + half)
        # gate (1): the statistical/iterative-plausibility controls fire NOT A RESULT first
        if not s_ok:
            verdict, note = "NOT A RESULT", "gate (1): a transient-statistics control (S1/S2/S3/S4) failed"
        else:
            verdict, note = ("PASS" if in_band else "GATE FAIL"), ""
        rows.append(dict(row=rid, r_over_D=rd, reference=ref, band=[ref - half, ref + half],
                         time_averaged_peak=val, deviation=val - ref, in_band=in_band,
                         triple=None, triple_state="NO TRIPLE (one mesh)", observed_order=None,
                         gci=None, verdict=verdict, note=note))
        print("%-3s r/D=%.1f  UMean-peak=%.4f  ref=%.4f  band=[%.4f,%.4f]  triple=NONE GCI=n/a  -> %s%s"
              % (rid, rd, val, ref, ref - half, ref + half, verdict, (" [" + note + "]") if note else ""))

    out = dict(rung="T4f", solver="buoyantBoussinesqPimpleFoam (URANS)",
               reference="ERCOFTAC case025 ij2lr (H/D=2, Re=23000)", mesh="fine only (138240 cells)",
               triple="NONE -- one mesh; no GCI, no observed order, no discretisation bound (rule 5)",
               promotion_planted_control=prom, frozen_C4=c4,
               transient_stats=dict(S1=stat["S1"], S2=stat["S2"], S3=s3, S4=stat["S4"],
                                    co_max=co_max, period_s=stat.get("period_s"),
                                    t_stat_s=stat.get("t_stat_s"), n_periods=stat.get("n_periods")),
               rows=rows)
    json.dump(out, open(a.json, "w"), indent=2)
    print("wrote %s" % a.json)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
