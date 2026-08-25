#!/usr/bin/env python3
"""Curriculum D8 GRADER.  FROZEN INSTRUMENT (PREREGISTRATION.md s9, md5).

It REFUSES (exit 2) rather than degrades.  Every gate below reads a number, and
every reader is planted, read back, and PROVED able to refuse before it is
believed (CLAUDE.md rule 3).

The three defects this grader is built against, by name:

  * `curriculum_D3/d3_grade.py` gate G3+G4 returns PASS at 0.0000 % with zero
    sign flips over an EMPTY COMPONENT SET: a present-but-unparseable FD block
    yields by_step[s] = [] with the KEY PRESENT, the refusal tests key presence
    and never non-emptiness, and a plateau step is selected without one
    comparison.  A PARTIAL PLANT READS ON THE PAGE EXACTLY LIKE A COMPLETE ONE.
    -> here the FD gate asserts the component COUNT IS EXACTLY 8, prints it, and
       refuses on any other value; the negative control proves the refusal fires
       on a 7-component set and on a 0-component set.

  * `A3/*/drive.sh` writes peak_rss_GiB = 0.000 from an UNINITIALISED awk
    variable with 2>/dev/null hiding a missing file (fired for real at
    curriculum_D3_attempt2/RESULTS.md:76).
    -> here peak RSS is initialised, a missing/empty/unparseable sample REFUSES,
       and the negative control proves it.

  * L-302: "an instrument that cannot say 'I measured nothing' will report a
    number it did not measure."

Usage:  d8_grade.py --selftest
        d8_grade.py <run_root>
"""
import json, os, re, sys, tempfile

# ------------------------------------------------------------------ registered
ETA            = 1.0910e-05     # N-D13, registered CD noise floor
CL_TARGET      = 0.5
G2_CL_TOL      = 5.0e-3         # feasibility band, frozen before compute
G3_MIN_DROP    = 10.0 * ETA     # 1.0910e-04 in CD -- ten times the noise floor
G4_AGG_BAND    = 5.0            # %, aggregate vector-relative error
G4_COMP_BAND   = 10.0           # %, per component
G5_PLATEAU     = 10.0           # %, |d(s_hi)-d(s_lo)|/|d(s_hi)|
G5_MAX_FAILS   = 2              # more than this -> G4 is NOT A RESULT
G6_RSS_BAND    = 11.0           # GiB, predicted peak
G6_CAP_B       = 12 * 1024**3   # the registered cgroup cap, 12 GiB
G7_MIN_C       = 5.0            # clearance at the graded step, on measured |J_fd|
N_GRADEABLE    = 8
GRADEABLE      = [("twist", 0), ("twist", 1), ("twist", 2), ("twist", 3),
                  ("twist", 4), ("twist", 5), ("patchV", 0), ("patchV", 1)]
EXCLUDED_BY_NAME = [("twist", 6)]
MESH_CELLS     = 41760
IDWARP_MD5     = "85f59e87253e0a71a813f64ca6e4c425"
COLD_CD_STORED = 0.03506349413916734   # reproduced 5x; P-BASE


class Refuse(Exception):
    pass


# ------------------------------------------------------------------- readers
def read_scalar(text, marker):
    """Last occurrence of `<marker> <python-repr float>`.  REFUSES if absent."""
    m = re.findall(r"^%s\s+(\S+)\s*$" % re.escape(marker), text, re.M)
    if not m:
        raise Refuse("marker %r absent -- cannot measure it" % marker)
    return float(m[-1])


def read_fd(text):
    """-> {(dv, idx): {step: deriv}}.  Never returns a silently empty inner map."""
    out = {}
    for dv, idx, step, deriv in re.findall(
            r"^FD_DERIV dv=(\S+) idx=(\d+) step=(\S+) deriv=(\S+)\s*$", text, re.M):
        out.setdefault((dv, int(idx)), {})[float(step)] = float(deriv)
    return out


def read_adj(text):
    out = {}
    for dv, idx, deriv in re.findall(
            r"^ADJ_DERIV dv=(\S+) idx=(\d+) deriv=(\S+)\s*$", text, re.M):
        out[(dv, int(idx))] = float(deriv)
    return out


def read_eta(text, n=20):
    """Last-`n` peak-to-peak of the printed CD, from the tail of a primal."""
    cds = [float(x) for x in re.findall(r"^CD:\s+(\S+)\s+final:", text, re.M)]
    if len(cds) < n:
        raise Refuse("only %d CD prints; need >= %d for eta" % (len(cds), n))
    tail = cds[-n:]
    return max(tail) - min(tail)


def read_peak_rss(path):
    """Initialised; a missing / empty / unparseable file REFUSES, never 0.000."""
    if not os.path.exists(path):
        raise Refuse("RSS sample file %s does not exist -- peak RSS NOT MEASURED" % path)
    vals = []
    for line in open(path):
        f = line.split()
        if len(f) < 3:
            continue
        v = f[2]
        try:
            if v.endswith("GiB"):
                vals.append(float(v[:-3]))
            elif v.endswith("MiB"):
                vals.append(float(v[:-3]) / 1024.0)
            elif v.endswith("KiB"):
                vals.append(float(v[:-3]) / 1048576.0)
        except ValueError:
            continue
    if not vals:
        raise Refuse("RSS file %s parsed to ZERO samples -- peak RSS NOT MEASURED" % path)
    return max(vals), len(vals)


# --------------------------------------------------------------------- gates
def gate_fd(fd, adj, plan_pairs):
    """The bright-line gate.  Refuses on a short or empty component set BY COUNT."""
    got = sorted(k for k in fd if len(fd[k]) >= 2)
    print("  FD component set parsed: %d component(s) with >= 2 steps: %s" % (len(got), got))
    leaked = [k for k in got if k in EXCLUDED_BY_NAME]
    if leaked:
        raise Refuse("component(s) excluded BY NAME appear in the FD table: %s" % leaked)
    if len(got) != N_GRADEABLE:
        raise Refuse("FD component count is %d, registered %d -- the FD table is SHORT or EMPTY; "
                     "NOT A RESULT, and no aggregate is computed" % (len(got), N_GRADEABLE))
    if sorted(got) != sorted(GRADEABLE):
        raise Refuse("FD component set %s != registered gradeable set %s" % (got, sorted(GRADEABLE)))
    rows, num, den, flips, plateau_fail = [], 0.0, 0.0, 0, []
    for key in sorted(GRADEABLE):
        steps = sorted(fd[key])
        if len(steps) < 2:
            raise Refuse("component %s has %d step(s); the plateau test needs 2" % (key, len(steps)))
        s_lo, s_hi = steps[0], steps[-1]
        d_lo, d_hi = fd[key][s_lo], fd[key][s_hi]
        if d_hi == 0.0:
            raise Refuse("component %s FD derivative at the graded step is exactly zero" % (key,))
        plat = abs(d_hi - d_lo) / abs(d_hi) * 100.0
        J = adj.get(key)
        if J is None:
            raise Refuse("no endpoint adjoint for component %s" % (key,))
        rel = abs(J - d_hi) / abs(d_hi) * 100.0
        C = 2.0 * abs(d_hi) * s_hi / ETA
        flip = (J * d_hi) < 0.0
        flips += int(flip)
        if plat > G5_PLATEAU:
            plateau_fail.append(key)
        num += (J - d_hi) ** 2
        den += d_hi ** 2
        rows.append(dict(dv=key[0], idx=key[1], J=J, s_lo=s_lo, s_hi=s_hi,
                         d_lo=d_lo, d_hi=d_hi, rel=rel, plateau=plat, C=C, flip=flip))
    agg = (num ** 0.5) / (den ** 0.5) * 100.0
    return rows, agg, flips, plateau_fail


# ------------------------------------------------------------------ selftest
def selftest():
    ok = True

    def chk(label, cond):
        nonlocal ok
        ok &= bool(cond)
        print("SELFTEST %-46s %s" % (label, "OK" if cond else "FAILED"))

    PLANT_CD, PLANT_CL = 1.234567e-02, 4.321e-01
    log = "D8_FINAL_CD %r\nD8_FINAL_CL %r\n" % (PLANT_CD, PLANT_CL)
    chk("scalar plant read back (CD)", read_scalar(log, "D8_FINAL_CD") == PLANT_CD)
    chk("scalar plant read back (CL)", read_scalar(log, "D8_FINAL_CL") == PLANT_CL)
    try:
        read_scalar("nothing here\n", "D8_FINAL_CD"); chk("scalar REFUSES when absent", False)
    except Refuse:
        chk("scalar REFUSES when absent", True)

    # full 8-component plant, adjoint deliberately offset by a known 2.000 %
    adj, fdtxt = {}, []
    for i, (dv, idx) in enumerate(GRADEABLE):
        d_hi = -1.0e-3 * (i + 1)
        adj[(dv, idx)] = d_hi * 1.02
        fdtxt.append("FD_DERIV dv=%s idx=%d step=%r deriv=%r" % (dv, idx, 5e-2, d_hi * 1.005))
        fdtxt.append("FD_DERIV dv=%s idx=%d step=%r deriv=%r" % (dv, idx, 1e-1, d_hi))
    full = "\n".join(fdtxt) + "\n"
    rows, agg, flips, pf = gate_fd(read_fd(full), adj, None)
    chk("8-component plant: 8 rows", len(rows) == 8)
    chk("planted 2.000 %% recovered", abs(agg - 2.0) < 1e-6)
    chk("planted zero sign flips", flips == 0)
    chk("planted plateau all inside band", pf == [])

    # NEGATIVE CONTROL 1 -- a SHORT set must refuse, printing the count
    short = "\n".join(l for l in fdtxt if "idx=5" not in l) + "\n"
    try:
        gate_fd(read_fd(short), adj, None); chk("SHORT set (7) REFUSES", False)
    except Refuse as e:
        chk("SHORT set (7) REFUSES", "count is 7" in str(e))

    # NEGATIVE CONTROL 2 -- an EMPTY set must refuse, not PASS at 0.0000 %
    try:
        gate_fd(read_fd("FD_DERIV lines that do not parse\n"), adj, None)
        chk("EMPTY set REFUSES (the D3 defect)", False)
    except Refuse as e:
        chk("EMPTY set REFUSES (the D3 defect)", "count is 0" in str(e))

    # NEGATIVE CONTROL 3 -- a single-step component must refuse (no plateau test)
    one = "\n".join(l for l in fdtxt if not ("idx=4" in l and "0.05" in l)) + "\n"
    try:
        gate_fd(read_fd(one), adj, None); chk("1-step component REFUSES", False)
    except Refuse:
        chk("1-step component REFUSES", True)

    # NEGATIVE CONTROL 4 -- the by-name exclusion must refuse if idx6 leaks in
    leak = full + "FD_DERIV dv=twist idx=6 step=0.3 deriv=-1.3e-04\nFD_DERIV dv=twist idx=6 step=1.0 deriv=-1.3e-04\n"
    adj2 = dict(adj); adj2[("twist", 6)] = -1.3e-4
    try:
        gate_fd(read_fd(leak), adj2, None); chk("twist idx6 leak REFUSES", False)
    except Refuse as e:
        chk("twist idx6 leak REFUSES", "excluded BY NAME" in str(e))

    # NEGATIVE CONTROL 5 -- a planted SIGN FLIP must be counted, not smoothed
    adj3 = dict(adj); adj3[("twist", 0)] = -adj[("twist", 0)]
    _, _, flips3, _ = gate_fd(read_fd(full), adj3, None)
    chk("planted sign flip is counted", flips3 == 1)

    # NEGATIVE CONTROL 6 -- a planted plateau breach must be caught
    bad = full.replace("FD_DERIV dv=twist idx=2 step=0.05 deriv=-0.003",
                       "FD_DERIV dv=twist idx=2 step=0.05 deriv=-0.03")
    _, _, _, pf6 = gate_fd(read_fd(bad), adj, None)
    chk("planted plateau breach caught", ("twist", 2) in pf6)

    # peak RSS: plant, read back, and PROVE the refusals
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "rss.txt")
        open(p, "w").write("2026-01-01T00:00:00Z opt 3.500GiB / 12GiB\n"
                           "2026-01-01T00:00:15Z opt 512.0MiB / 12GiB\n")
        peak, n = read_peak_rss(p)
        chk("RSS plant read back 3.5 GiB", abs(peak - 3.5) < 1e-9 and n == 2)
        try:
            read_peak_rss(os.path.join(td, "absent.txt")); chk("RSS REFUSES on missing file", False)
        except Refuse:
            chk("RSS REFUSES on missing file", True)
        open(p, "w").write("")
        try:
            read_peak_rss(p); chk("RSS REFUSES on empty file (the A3 0.000 bug)", False)
        except Refuse:
            chk("RSS REFUSES on empty file (the A3 0.000 bug)", True)
        open(p, "w").write("garbage with no memory column\n")
        try:
            read_peak_rss(p); chk("RSS REFUSES on unparseable file", False)
        except Refuse:
            chk("RSS REFUSES on unparseable file", True)

    # eta reader: plant a known spread, and prove it refuses on a short tail
    cd_lines = "".join("CD: %r final: %r\n" % (0.035 + 1e-6 * (i % 2), 0.0) for i in range(20))
    chk("eta plant read back 1e-06", abs(read_eta(cd_lines) - 1e-6) < 1e-15)
    try:
        read_eta("CD: 0.035 final: 0.0\n"); chk("eta REFUSES on a short tail", False)
    except Refuse:
        chk("eta REFUSES on a short tail", True)

    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 2


# ---------------------------------------------------------------------- main
def main(root):
    if selftest() != 0:
        raise Refuse("selftest failed -- this grader is not entitled to grade anything")
    print("\n" + "=" * 78 + "\nD8 GRADING\n" + "=" * 78)
    ledger = open(os.path.join(root, "ledger.txt")).read()
    optlog = open(os.path.join(root, "opt.log"), errors="replace").read()
    verdicts = {}

    # ---- G0 identity and activity -----------------------------------------
    g0 = []
    g0.append(("IDWARP_SO_MD5", IDWARP_MD5 in optlog))
    g0.append(("ASSERT_MD5 OK in ledger", "ASSERT_MD5 OK" in ledger))
    g0.append(("nProcs : 1", bool(re.search(r"^nProcs\s*:\s*1\s*$", optlog, re.M))))
    g0.append(("transonicPCOption 1;", "transonicPCOption 1;" in optlog))
    g0.append(("Mesh region0 size: %d" % MESH_CELLS, "Mesh region0 size: %d" % MESH_CELLS in optlog))
    for k, v in g0:
        print("  G0 %-34s %s" % (k, "OK" if v else "FAIL"))
    verdicts["G0 identity/activity"] = "PASS" if all(v for _, v in g0) else "GATE FAIL"
    if not all(v for _, v in g0):
        raise Refuse("G0 failed -- the arm is VOID on identity/activity; nothing below is graded")

    # ---- P-BASE: the twist-only edit must be numerically inert -------------
    cold = read_scalar(optlog, "D8_COLD_CD")
    inert = (cold == COLD_CD_STORED)
    print("  P-BASE cold CD %r vs stored %r -> %s" % (cold, COLD_CD_STORED, "EXACT" if inert else "DIFFERS"))
    verdicts["P-BASE twist-only edit inert on the primal"] = "PASS" if inert else "GATE FAIL"

    # ---- G1 optimiser termination -----------------------------------------
    exit_ok = "EXIT: Optimal Solution Found." in optlog
    capped = bool(re.search(r"Maximum Number of Iterations Exceeded", optlog))
    complete = "D8_OPT_ARM_COMPLETE" in optlog
    rc_opt = re.search(r"ARM=opt .*? rc=(-?\d+)", ledger)
    rc_opt = int(rc_opt.group(1)) if rc_opt else None
    m_oom = re.search(r"ARM=opt .*?inspect\(exit,oomkilled\)=\[(.*?)\]", ledger)
    oom = bool(m_oom) and "true" in m_oom.group(1).lower()
    print("  G1 EXIT-Optimal=%s  cap-stop=%s  arm-complete=%s  rc=%s  oomkilled=%s"
          % (exit_ok, capped, complete, rc_opt, oom))
    if oom:
        verdicts["G1 optimiser termination"] = "PENDING"
    elif exit_ok and complete:
        verdicts["G1 optimiser termination"] = "PASS"
    elif capped and complete:
        verdicts["G1 optimiser termination"] = "GATE REACHED"
    else:
        verdicts["G1 optimiser termination"] = "NOT A RESULT"

    # ---- G2 CL feasibility --------------------------------------------------
    cl_f = read_scalar(optlog, "D8_FINAL_CL")
    dcl = abs(cl_f - CL_TARGET)
    print("  G2 |CL_final - %.3f| = %.6e  band %.1e" % (CL_TARGET, dcl, G2_CL_TOL))
    verdicts["G2 CL feasibility"] = "PASS" if dcl <= G2_CL_TOL else "GATE FAIL"

    # ---- G3 drag reduction, thresholded on this case's own noise floor ------
    cd_s = read_scalar(optlog, "D8_START_CD")
    cd_f = read_scalar(optlog, "D8_FINAL_CD")
    drop = cd_s - cd_f
    print("  G3 CD start %r -> final %r ; drop %+.6e ; required >= %.6e (10 eta)"
          % (cd_s, cd_f, drop, G3_MIN_DROP))
    print("     relative drop %+.4f %%" % (drop / cd_s * 100.0))
    verdicts["G3 drag reduction"] = "PASS" if drop >= G3_MIN_DROP else "GATE FAIL"

    # ---- G4/G5/G7 the bright line: endpoint FD vs endpoint adjoint ----------
    fdpath = os.path.join(root, "fd.log")
    if not os.path.exists(fdpath):
        verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "PENDING"
        verdicts["G5 plateau"] = "PENDING"
        verdicts["G7 clearance"] = "PENDING"
        rows = []
    else:
        fdlog = open(fdpath, errors="replace").read()
        adj = read_adj(optlog)
        print("  ADJ components parsed: %d" % len(adj))
        rows, agg, flips, pf = gate_fd(read_fd(fdlog), adj, None)
        print("\n| DV, idx | adjoint (endpoint) | FD @ graded step | rel err %% | C | plateau %% | sign |")
        print("|---|---|---|---|---|---|---|")
        for r in rows:
            print("| `%s` %d | `%+.6e` | `%+.6e` @ %g | **%.3f** | %.2f | %.2f | %s |"
                  % (r["dv"], r["idx"], r["J"], r["d_hi"], r["s_hi"], r["rel"], r["C"],
                     r["plateau"], "FLIP" if r["flip"] else "SAME"))
        worst = max(r["rel"] for r in rows)
        minC = min(r["C"] for r in rows)
        print("\n  aggregate vector-relative error over %d components = %.4f %% (band %.1f %%)"
              % (len(rows), agg, G4_AGG_BAND))
        print("  worst component %.4f %% (band %.1f %%) ; sign flips %d ; plateau failures %s"
              % (worst, G4_COMP_BAND, flips, pf))
        print("  min clearance at the graded step (measured |J_fd|) = %.2f x (bar %.1f x)" % (minC, G7_MIN_C))
        verdicts["G5 plateau (<= %.0f %%)" % G5_PLATEAU] = "PASS" if not pf else (
            "NOT A RESULT" if len(pf) > G5_MAX_FAILS else "GATE FAIL")
        verdicts["G7 clearance C >= 5 at the graded step"] = "PASS" if minC >= G7_MIN_C else "GATE FAIL"
        if len(pf) > G5_MAX_FAILS or minC < G7_MIN_C:
            verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "NOT A RESULT"
        elif agg <= G4_AGG_BAND and worst <= G4_COMP_BAND and flips == 0:
            verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "PASS"
        else:
            verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "GATE FAIL"
        # P-eta at the endpoint
        try:
            eta_m = read_eta(fdlog)
            print("  P-eta endpoint: measured %.4e vs registered %.4e (ratio %.3f)"
                  % (eta_m, ETA, eta_m / ETA))
            verdicts["P-eta endpoint within +/-50 %% of registered"] = \
                "PASS" if 0.5 <= eta_m / ETA <= 1.5 else "GATE FAIL"
        except Refuse as e:
            print("  P-eta REFUSED: %s" % e)
            verdicts["P-eta endpoint within +/-50 %% of registered"] = "NOT A RESULT"

    # ---- G6 memory envelope -------------------------------------------------
    try:
        peak, nsamp = read_peak_rss(os.path.join(root, "rss_opt.txt"))
        print("  G6 peak RSS %.3f GiB over %d samples (predicted <= %.1f, cap 12.0)" % (peak, nsamp, G6_RSS_BAND))
        cg = re.search(r"ARM=opt .*?cgroup_memory_peak_B=(\S+)", ledger)
        cgv = cg.group(1) if cg else "NOT_MEASURED"
        print("     cgroup memory.peak = %s B ; registered cap = %d B" % (cgv, G6_CAP_B))
        censored = oom or (cgv.isdigit() and int(cgv) >= G6_CAP_B)
        if censored:
            verdicts["G6 adjoint memory envelope"] = "PENDING"
            print("     RIGHT-CENSORED at the cap: this measures the cap, not the requirement.")
        else:
            verdicts["G6 adjoint memory envelope"] = "PASS" if peak <= G6_RSS_BAND else "GATE FAIL"
    except Refuse as e:
        print("  G6 REFUSED: %s" % e)
        verdicts["G6 adjoint memory envelope"] = "NOT A RESULT"

    verdicts["twist idx6 (FD-ungradeable, named in advance)"] = "NOT A RESULT"

    print("\n" + "-" * 78)
    for k in sorted(verdicts):
        print("VERDICT  %-52s %s" % (k, verdicts[k]))
    print("-" * 78)
    json.dump({"verdicts": verdicts, "rows": rows},
              open(os.path.join(root, "d8_grade.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    try:
        sys.exit(main(sys.argv[1]))
    except Refuse as e:
        print("REFUSE: %s" % e)
        sys.exit(2)


# =============================================================================
# AMENDMENT 1 -- 2026-08-25 -- d8_grade.py v1.0 -> v1.1
# **lines whose number changed above this section: 0**
#
# The frozen v1.0 G0 gate tests for the literal `Mesh region0 size: 41760` in the
# ARM log.  That string is emitted by mesh GENERATION (`base/logMeshGeneration.txt`
# line 437) and is NEVER emitted by a DAFoam run; the runtime log prints
# `Global Cells: 41760` instead.  As frozen the check therefore cannot pass on any
# arm, and G0's failure branch VOIDS the arm -- so v1.0 would have refused to grade
# a healthy run on the strength of a marker string that does not exist.
#
# Repaired under VERIFICATION_CHARTER s2d.1, all four conditions stated:
#  (1) DEMONSTRABLE ERROR, not a preference: the string occurs ZERO times in the
#      live arm log, zero times in `P3-a6-n16-rem/rem.log`, and 41,760 is confirmed
#      by BOTH `Global Cells: 41760` (runtime) and `logMeshGeneration.txt:437`.
#  (2) INSTRUMENT INDEPENDENT OF THE HYPOTHESIS: found by a plain string-presence
#      probe that grades nothing, run at 16:58Z -- BEFORE any graded quantity
#      existed.  No FD table, no endpoint adjoint, no CD, no optimiser exit had
#      been produced.  The probe cannot have been selected to move a verdict
#      because no verdict was available to move.  s2d.1's prohibition -- "nothing
#      a verdict depends on may be repaired on the authority of the verdict it
#      produces" -- is therefore not engaged: no verdict authorises this.
#  (3) DISCLOSED, instrument named, and what moved quantified: pre-repair the
#      grader REFUSES at G0 and grades NOTHING; post-repair G0 is evaluated.  No
#      gate, threshold, cap or label is altered -- G0's substance ("this arm ran
#      the 41,760-cell A6 N=16 mesh") is unchanged, and the check is made STRICTLY
#      STRONGER: it now requires the cell count in the RUNTIME log AND in the mesh
#      generation record, where v1.0 required it in neither.
#  (4) PRE-REPAIR VALUES beside the published ones: recorded in RESULTS.md s9.
#
# Rule 6 is honoured literally: not one line above this banner is edited or moved.
# The amended `main` below was produced mechanically from the frozen body and
# differs from it by exactly the one gate line reproduced here:
#   -    g0.append(("Mesh region0 size: %d" % MESH_CELLS, "Mesh region0 size: %d" % MESH_CELLS in optlog))
#   +    g0.append(("Global Cells: %d (runtime)" % MESH_CELLS, "Global Cells: %d" % MESH_CELLS in optlog))
#   +    _gen = os.path.join(root, "base", "logMeshGeneration.txt")
#   +    g0.append(("Mesh region0 size: %d (generation record)" % MESH_CELLS,
#   +               os.path.exists(_gen) and ("Mesh region0 size: %d" % MESH_CELLS)
#   +               in open(_gen, errors="replace").read()))
# =============================================================================

def main(root):
    if selftest() != 0:
        raise Refuse("selftest failed -- this grader is not entitled to grade anything")
    print("\n" + "=" * 78 + "\nD8 GRADING\n" + "=" * 78)
    ledger = open(os.path.join(root, "ledger.txt")).read()
    optlog = open(os.path.join(root, "opt.log"), errors="replace").read()
    verdicts = {}

    # ---- G0 identity and activity -----------------------------------------
    g0 = []
    g0.append(("IDWARP_SO_MD5", IDWARP_MD5 in optlog))
    g0.append(("ASSERT_MD5 OK in ledger", "ASSERT_MD5 OK" in ledger))
    g0.append(("nProcs : 1", bool(re.search(r"^nProcs\s*:\s*1\s*$", optlog, re.M))))
    g0.append(("transonicPCOption 1;", "transonicPCOption 1;" in optlog))
    g0.append(("Global Cells: %d (runtime)" % MESH_CELLS, "Global Cells: %d" % MESH_CELLS in optlog))
    _gen = os.path.join(root, "base", "logMeshGeneration.txt")
    g0.append(("Mesh region0 size: %d (generation record)" % MESH_CELLS,
               os.path.exists(_gen) and ("Mesh region0 size: %d" % MESH_CELLS)
               in open(_gen, errors="replace").read()))
    for k, v in g0:
        print("  G0 %-34s %s" % (k, "OK" if v else "FAIL"))
    verdicts["G0 identity/activity"] = "PASS" if all(v for _, v in g0) else "GATE FAIL"
    if not all(v for _, v in g0):
        raise Refuse("G0 failed -- the arm is VOID on identity/activity; nothing below is graded")

    # ---- P-BASE: the twist-only edit must be numerically inert -------------
    cold = read_scalar(optlog, "D8_COLD_CD")
    inert = (cold == COLD_CD_STORED)
    print("  P-BASE cold CD %r vs stored %r -> %s" % (cold, COLD_CD_STORED, "EXACT" if inert else "DIFFERS"))
    verdicts["P-BASE twist-only edit inert on the primal"] = "PASS" if inert else "GATE FAIL"

    # ---- G1 optimiser termination -----------------------------------------
    exit_ok = "EXIT: Optimal Solution Found." in optlog
    capped = bool(re.search(r"Maximum Number of Iterations Exceeded", optlog))
    complete = "D8_OPT_ARM_COMPLETE" in optlog
    rc_opt = re.search(r"ARM=opt .*? rc=(-?\d+)", ledger)
    rc_opt = int(rc_opt.group(1)) if rc_opt else None
    m_oom = re.search(r"ARM=opt .*?inspect\(exit,oomkilled\)=\[(.*?)\]", ledger)
    oom = bool(m_oom) and "true" in m_oom.group(1).lower()
    print("  G1 EXIT-Optimal=%s  cap-stop=%s  arm-complete=%s  rc=%s  oomkilled=%s"
          % (exit_ok, capped, complete, rc_opt, oom))
    if oom:
        verdicts["G1 optimiser termination"] = "PENDING"
    elif exit_ok and complete:
        verdicts["G1 optimiser termination"] = "PASS"
    elif capped and complete:
        verdicts["G1 optimiser termination"] = "GATE REACHED"
    else:
        verdicts["G1 optimiser termination"] = "NOT A RESULT"

    # ---- G2 CL feasibility --------------------------------------------------
    cl_f = read_scalar(optlog, "D8_FINAL_CL")
    dcl = abs(cl_f - CL_TARGET)
    print("  G2 |CL_final - %.3f| = %.6e  band %.1e" % (CL_TARGET, dcl, G2_CL_TOL))
    verdicts["G2 CL feasibility"] = "PASS" if dcl <= G2_CL_TOL else "GATE FAIL"

    # ---- G3 drag reduction, thresholded on this case's own noise floor ------
    cd_s = read_scalar(optlog, "D8_START_CD")
    cd_f = read_scalar(optlog, "D8_FINAL_CD")
    drop = cd_s - cd_f
    print("  G3 CD start %r -> final %r ; drop %+.6e ; required >= %.6e (10 eta)"
          % (cd_s, cd_f, drop, G3_MIN_DROP))
    print("     relative drop %+.4f %%" % (drop / cd_s * 100.0))
    verdicts["G3 drag reduction"] = "PASS" if drop >= G3_MIN_DROP else "GATE FAIL"

    # ---- G4/G5/G7 the bright line: endpoint FD vs endpoint adjoint ----------
    fdpath = os.path.join(root, "fd.log")
    if not os.path.exists(fdpath):
        verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "PENDING"
        verdicts["G5 plateau"] = "PENDING"
        verdicts["G7 clearance"] = "PENDING"
        rows = []
    else:
        fdlog = open(fdpath, errors="replace").read()
        adj = read_adj(optlog)
        print("  ADJ components parsed: %d" % len(adj))
        rows, agg, flips, pf = gate_fd(read_fd(fdlog), adj, None)
        print("\n| DV, idx | adjoint (endpoint) | FD @ graded step | rel err %% | C | plateau %% | sign |")
        print("|---|---|---|---|---|---|---|")
        for r in rows:
            print("| `%s` %d | `%+.6e` | `%+.6e` @ %g | **%.3f** | %.2f | %.2f | %s |"
                  % (r["dv"], r["idx"], r["J"], r["d_hi"], r["s_hi"], r["rel"], r["C"],
                     r["plateau"], "FLIP" if r["flip"] else "SAME"))
        worst = max(r["rel"] for r in rows)
        minC = min(r["C"] for r in rows)
        print("\n  aggregate vector-relative error over %d components = %.4f %% (band %.1f %%)"
              % (len(rows), agg, G4_AGG_BAND))
        print("  worst component %.4f %% (band %.1f %%) ; sign flips %d ; plateau failures %s"
              % (worst, G4_COMP_BAND, flips, pf))
        print("  min clearance at the graded step (measured |J_fd|) = %.2f x (bar %.1f x)" % (minC, G7_MIN_C))
        verdicts["G5 plateau (<= %.0f %%)" % G5_PLATEAU] = "PASS" if not pf else (
            "NOT A RESULT" if len(pf) > G5_MAX_FAILS else "GATE FAIL")
        verdicts["G7 clearance C >= 5 at the graded step"] = "PASS" if minC >= G7_MIN_C else "GATE FAIL"
        if len(pf) > G5_MAX_FAILS or minC < G7_MIN_C:
            verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "NOT A RESULT"
        elif agg <= G4_AGG_BAND and worst <= G4_COMP_BAND and flips == 0:
            verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "PASS"
        else:
            verdicts["G4 endpoint FD-vs-adjoint (8 gradeable)"] = "GATE FAIL"
        # P-eta at the endpoint
        try:
            eta_m = read_eta(fdlog)
            print("  P-eta endpoint: measured %.4e vs registered %.4e (ratio %.3f)"
                  % (eta_m, ETA, eta_m / ETA))
            verdicts["P-eta endpoint within +/-50 %% of registered"] = \
                "PASS" if 0.5 <= eta_m / ETA <= 1.5 else "GATE FAIL"
        except Refuse as e:
            print("  P-eta REFUSED: %s" % e)
            verdicts["P-eta endpoint within +/-50 %% of registered"] = "NOT A RESULT"

    # ---- G6 memory envelope -------------------------------------------------
    try:
        peak, nsamp = read_peak_rss(os.path.join(root, "rss_opt.txt"))
        print("  G6 peak RSS %.3f GiB over %d samples (predicted <= %.1f, cap 12.0)" % (peak, nsamp, G6_RSS_BAND))
        cg = re.search(r"ARM=opt .*?cgroup_memory_peak_B=(\S+)", ledger)
        cgv = cg.group(1) if cg else "NOT_MEASURED"
        print("     cgroup memory.peak = %s B ; registered cap = %d B" % (cgv, G6_CAP_B))
        censored = oom or (cgv.isdigit() and int(cgv) >= G6_CAP_B)
        if censored:
            verdicts["G6 adjoint memory envelope"] = "PENDING"
            print("     RIGHT-CENSORED at the cap: this measures the cap, not the requirement.")
        else:
            verdicts["G6 adjoint memory envelope"] = "PASS" if peak <= G6_RSS_BAND else "GATE FAIL"
    except Refuse as e:
        print("  G6 REFUSED: %s" % e)
        verdicts["G6 adjoint memory envelope"] = "NOT A RESULT"

    verdicts["twist idx6 (FD-ungradeable, named in advance)"] = "NOT A RESULT"

    print("\n" + "-" * 78)
    for k in sorted(verdicts):
        print("VERDICT  %-52s %s" % (k, verdicts[k]))
    print("-" * 78)
    json.dump({"verdicts": verdicts, "rows": rows},
              open(os.path.join(root, "d8_grade.json"), "w"), indent=1)
    return 0
