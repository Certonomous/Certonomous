#!/usr/bin/env python3
"""
Curriculum item D3 -- FROZEN COMPARATOR. Grades every registered gate from
artifacts on disk. FROZEN by the commit that carries PREREGISTRATION.md; it is
not edited after first compute (CLAUDE.md rule 6; PREREGISTRATION.md sec.4.3).

Vocabulary, and only this: PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING (CLAUDE.md rule 1).

CONTROLS (CLAUDE.md rule 3, as sharpened by L-273 -- "plant into a file the
producer actually wrote"):

  --selftest   plants into REAL A4 producer artifacts (that case's own
               opt_IPOPT.txt and its own check_totals text, written by the same
               code path this item runs) and asserts every reader SEES the
               plant. If any reader cannot, it refuses with exit 2.
  --keycheck   for d3_summary.json, no producer artifact can exist before the
               run, so the freeze invocation instead asserts the PRODUCER's key
               set (parsed out of the frozen d3_runScript.py) equals the
               CONSUMER's key set (parsed out of this file). This is L-273's
               second remedy and it runs in the same invocation as the freeze.
"""
import argparse
import json
import math
import os
import re
import sys

# ---------------------------------------------------------------- registered numbers
GATE = {
    "constr_viol_tol": 1.0e-6,
    "thick_lo": 0.85, "thick_hi": 1.15, "vol_lo": 0.98,
    "fd_band_pct": 15.0,             # G3 gate
    "fd_plateau_tol": 0.25,          # plateau rule: neighbours within 25% of the value
    "fd_steps_plateau": [1e-2, 1e-3, 1e-4],
    "fd_step_trivial": 1e-1,         # DAFOAM_CHARTER sec.4 deliberately-wrong step
    "eta_signal_ref": 1.40780e-03,   # A4 shipped first-major |dCD| (RESULTS sec.2 iter 0->1)
    "eta_pass_frac": 0.01,           # eta-PASS   : delta_repeat <= 1% of the signal
    "eta_marginal_frac": 0.10,       # eta-MARGIN : <= 10%; above that the item is BLOCKED
    "eta_plant_dv": 1.0e-4,
    "eta_plant_floor": 1.0e-5,       # the plant must move CD by at least this
    "theta_lo_deg": 12.0, "theta_hi_deg": 25.0,
    "mdef_lo": 0.45, "mdef_hi": 0.75,
    "reduction_floor_pct": 7.478,    # A4's own optimum: D3 must do at least as well
    "core_min_hard": 70.0,
    "rate_usd_per_core_h": 0.0513,
    "md5_patched": "85f59e87253e0a71a813f64ca6e4c425",
    "md5_shipped": "f0fcb488e0e98156575cd19548e91663",
}

# The FROZEN key set d3_runScript.py writes into d3_summary.json for Stage O.
PRODUCER_KEYS_O = [
    "base_CD", "base_CL", "base_shapeBreak", "base_shapeRear",
    "base_thickcon_slant", "base_volcon_aft",
    "final_CD", "final_CL", "final_shapeBreak", "final_shapeRear",
    "final_thickcon_slant", "final_volcon_aft",
    "reduction_pct", "task",
]
PRODUCER_KEYS_ETA = [
    "eta_call1_CD", "eta_call2_CD", "eta_delta_repeat",
    "eta_plant_CD", "eta_plant_dCD", "eta_plant_dv", "task",
]


# ---------------------------------------------------------------- parsers
def parse_ipopt(path):
    """Read an IPOPT output file. Returns the fields the gates need."""
    t = open(path, errors="replace").read()
    out = {"path": path}
    m = re.search(r"EXIT:\s*(.+?)\s*$", t, re.M)
    out["exit"] = m.group(1) if m else None
    for key, pat in (("n_iter", r"Number of Iterations\.*:\s*(\d+)"),
                     ("objective", r"Objective\.*:\s*([-\d.eE+]+)"),
                     ("constr_viol", r"Constraint violation\.*:\s*([-\d.eE+]+)"),
                     ("nlp_error", r"Overall NLP error\.*:\s*([-\d.eE+]+)")):
        mm = re.search(pat, t)
        out[key] = (int(mm.group(1)) if key == "n_iter" else float(mm.group(1))) if mm else None
    return out


def parse_check_totals(text):
    """Every 'Full Model:' block in a log. Returns a list of dicts with the RAW
    arrays -- the per-component numbers, never the printed aggregate."""
    blocks = []
    pat = re.compile(
        r"Full Model:\s*'([^']+)'\s*wrt\s*'([^']+)'(.*?)(?=Full Model:|\Z)", re.S)
    for m in pat.finditer(text):
        of, wrt, body = m.group(1), m.group(2), m.group(3)
        an = re.search(r"Raw Analytic Derivative \(Jfor\)\s*(\[\[.*?\]\])", body, re.S)
        fd = re.search(r"Raw FD Derivative \(Jfd\)\s*(\[\[.*?\]\])", body, re.S)
        if not (an and fd):
            continue
        def nums(s):
            return [float(x) for x in re.findall(r"[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?", s)]
        blocks.append({"of": of, "wrt": wrt,
                       "analytic": nums(an.group(1)), "fd": nums(fd.group(1))})
    return blocks


def per_component(block):
    """Per-component relative error and sign flips. A2 idx46 is why the aggregate
    is never the graded quantity."""
    rows = []
    a, f = block["analytic"], block["fd"]
    n = min(len(a), len(f))
    for i in range(n):
        denom = abs(f[i])
        rel = (abs(a[i] - f[i]) / denom * 100.0) if denom > 0 else float("inf")
        flip = (a[i] * f[i]) < 0.0
        rows.append({"idx": i, "analytic": a[i], "fd": f[i], "rel_pct": rel, "flip": flip})
    return rows


def steps_from_log(text):
    """Map each registered FD step to the check_totals blocks emitted under it,
    using the runScript's own D3_CHECK_TOTALS_BEGIN/END markers."""
    out = {}
    for m in re.finditer(
            r"D3_CHECK_TOTALS_BEGIN step=([-\d.eE+]+)(.*?)D3_CHECK_TOTALS_END", text, re.S):
        out[float(m.group(1))] = parse_check_totals(m.group(2))
    return out


# ---------------------------------------------------------------- gates
def g1_constraints(summary, ipopt):
    """G1 -- constraint satisfaction at the accepted design."""
    notes, ok = [], True
    cv = ipopt.get("constr_viol")
    if cv is None:
        return "NOT A RESULT", ["IPOPT printed no Constraint violation line"]
    if cv > GATE["constr_viol_tol"]:
        ok = False
        notes.append("IPOPT constraint violation %.3e > %.1e" % (cv, GATE["constr_viol_tol"]))
    else:
        notes.append("IPOPT constraint violation %.3e <= %.1e" % (cv, GATE["constr_viol_tol"]))
    tol = GATE["constr_viol_tol"]
    for i, v in enumerate(summary.get("final_thickcon_slant", []) or []):
        if not (GATE["thick_lo"] - tol <= v <= GATE["thick_hi"] + tol):
            ok = False
            notes.append("thickcon_slant[%d] = %.6f outside [%.2f, %.2f]"
                         % (i, v, GATE["thick_lo"], GATE["thick_hi"]))
    for i, v in enumerate(summary.get("final_volcon_aft", []) or []):
        if v < GATE["vol_lo"] - tol:
            ok = False
            notes.append("volcon_aft[%d] = %.6f below %.2f" % (i, v, GATE["vol_lo"]))
    nt = len(summary.get("final_thickcon_slant", []) or [])
    nv = len(summary.get("final_volcon_aft", []) or [])
    notes.append("rows read: thickcon_slant %d, volcon_aft %d" % (nt, nv))
    if nt == 0 or nv == 0:
        return "NOT A RESULT", notes + ["a constraint array is empty -- nothing was graded"]
    return ("PASS" if ok else "GATE FAIL"), notes


def g2_termination(ipopt, summary):
    """G2 -- DAFOAM_CHARTER sec.9. A cap-stop is GATE REACHED or NOT A RESULT, never PASS."""
    ex = (ipopt.get("exit") or "").strip()
    err = ipopt.get("nlp_error")
    if ex.startswith("Optimal Solution Found") and err is not None and err < 1e-6:
        return "PASS", ["EXIT: %s; Overall NLP error %.4e < 1e-6; %s majors"
                        % (ex, err, ipopt.get("n_iter"))]
    red = summary.get("reduction_pct")
    met = red is not None and red >= GATE["reduction_floor_pct"]
    verdict = "GATE REACHED" if met else "NOT A RESULT"
    return verdict, ["EXIT: %s (not a convergence statement)" % ex,
                     "registered intermediate threshold reduction >= %.3f%%: %s (measured %s)"
                     % (GATE["reduction_floor_pct"], "MET" if met else "NOT MET", red)]


def g3_endpoint(by_step):
    """G3 + G4 -- plateau rule, per-component band, and the deliberately-wrong-step
    trivial baseline that must FAIL for the gate to be discriminating."""
    notes = []
    have = [s for s in GATE["fd_steps_plateau"] if s in by_step]
    if len(have) < 3:
        return "NOT A RESULT", ["plateau needs all of %s; log has %s"
                                % (GATE["fd_steps_plateau"], sorted(by_step))]
    comps = {}
    for s in have:
        for b in by_step[s]:
            for r in per_component(b):
                comps.setdefault((b["of"], b["wrt"], r["idx"]), {})[s] = r
    graded_step, plateau_note = None, []
    ordered = sorted(GATE["fd_steps_plateau"], reverse=True)
    for s in ordered[1:-1] or ordered:
        okall = True
        for key, byS in comps.items():
            v = byS[s]["fd"]
            for nb in (ordered[ordered.index(s) - 1], ordered[ordered.index(s) + 1]):
                if abs(byS[nb]["fd"] - v) > GATE["fd_plateau_tol"] * max(abs(v), 1e-30):
                    okall = False
                    plateau_note.append("%s: step %g vs %g differ > %.0f%%"
                                        % (str(key), s, nb, GATE["fd_plateau_tol"] * 100))
        if okall:
            graded_step = s
            break
    if graded_step is None:
        return "NOT A RESULT", ["no plateau step: " + "; ".join(plateau_note[:6])]
    notes.append("plateau step = %g (per component, neighbours within %.0f%%)"
                 % (graded_step, GATE["fd_plateau_tol"] * 100))
    worst, flips = 0.0, 0
    for key, byS in comps.items():
        r = byS[graded_step]
        worst = max(worst, r["rel_pct"])
        flips += 1 if r["flip"] else 0
        notes.append("  %s idx%d: analytic %.8e fd %.8e rel %.4f%% flip=%s"
                     % (key[1], key[2], r["analytic"], r["fd"], r["rel_pct"], r["flip"]))
    triv = by_step.get(GATE["fd_step_trivial"])
    if triv is None:
        return "NOT A RESULT", notes + ["trivial baseline at step %g absent -- the gate was "
                                        "never shown to discriminate (DAFOAM_CHARTER sec.4)"
                                        % GATE["fd_step_trivial"]]
    tworst, tflips = 0.0, 0
    for b in triv:
        for r in per_component(b):
            tworst = max(tworst, r["rel_pct"])
            tflips += 1 if r["flip"] else 0
    triv_fails = (tworst > GATE["fd_band_pct"]) or (tflips > 0)
    notes.append("trivial baseline step %g: worst %.4f%%, flips %d -> %s"
                 % (GATE["fd_step_trivial"], tworst, tflips,
                    "FAILS as required" if triv_fails else "PASSES -- gate NOT discriminating"))
    if not triv_fails:
        return "NOT A RESULT", notes
    ok = (worst <= GATE["fd_band_pct"]) and (flips == 0)
    notes.append("graded: worst per-component %.4f%% vs band %.1f%%, flips %d"
                 % (worst, GATE["fd_band_pct"], flips))
    return ("PASS" if ok else "GATE FAIL"), notes


def g_eta(summary):
    """G-eta -- the registered stop rule. Rule 3 first: an unseen plant refuses."""
    d = summary.get("eta_delta_repeat")
    pl = summary.get("eta_plant_dCD")
    if d is None or pl is None:
        return "NOT A RESULT", ["eta summary incomplete"]
    notes = ["delta_repeat = %.6e" % d,
             "plant dv = %.1e moved CD by %.6e (floor %.1e)"
             % (summary.get("eta_plant_dv", GATE["eta_plant_dv"]), pl, GATE["eta_plant_floor"])]
    if pl < GATE["eta_plant_floor"]:
        return "BLOCKED", notes + ["the planted perturbation was NOT seen: this reader's zero "
                                   "is not evidence (CLAUDE.md rule 3). Stage O NOT LAUNCHED."]
    p = GATE["eta_pass_frac"] * GATE["eta_signal_ref"]
    m = GATE["eta_marginal_frac"] * GATE["eta_signal_ref"]
    notes.append("signal ref %.6e -> eta-PASS <= %.6e, eta-MARGINAL <= %.6e"
                 % (GATE["eta_signal_ref"], p, m))
    if d <= p:
        return "PASS", notes + ["Stage O launches, all gates live."]
    if d <= m:
        return "GATE REACHED", notes + [
            "eta-MARGINAL: Stage O launches; every major whose accepted |dCD| < %.6e is "
            "NOT A RESULT in advance, and the final reduction carries +-%.6e." % (10 * d, 10 * d)]
    return "BLOCKED", notes + ["eta-FAIL: the objective's noise floor exceeds %.0f%% of the "
                               "registered signal. Stage O is NOT LAUNCHED; the item reports "
                               "the noise floor and spends nothing further."
                               % (GATE["eta_marginal_frac"] * 100)]


def g_theta(summary, jac=None):
    """G-theta -- rear-slant angle, a graded MONITOR (not an optimiser constraint)."""
    d1 = summary.get("final_shapeBreak")
    d2 = summary.get("final_shapeRear")
    if d1 is None or d2 is None:
        return "NOT A RESULT", ["no final design vector"], None
    # Frozen trilinear-FFD coefficients (PREREGISTRATION sec.2.5). Stage G's
    # measured Jacobian replaces them when supplied, and the two must agree.
    cB, cR = 0.72287, -0.43863
    if jac:
        try:
            cB = jac["dzbreak_dshapeBreak"] - jac["dzrear_dshapeBreak"]
            cR = jac["dzbreak_dshapeRear"] - jac["dzrear_dshapeRear"]
        except (KeyError, TypeError):
            pass
    dz0, dx = 0.0938, 0.2012
    tan = (dz0 + cB * d1 + cR * d2) / dx
    th = math.degrees(math.atan(tan))
    ok = GATE["theta_lo_deg"] <= th <= GATE["theta_hi_deg"]
    return (("PASS" if ok else "GATE FAIL"),
            ["theta(optimum) = %.3f deg from d=(%.6g, %.6g), coeffs (%.5f, %.5f); band [%.1f, %.1f]"
             % (th, d1, d2, cB, cR, GATE["theta_lo_deg"], GATE["theta_hi_deg"])], th)


def g_cost(core_min):
    if core_min is None:
        return "PENDING", ["no cost ledger supplied"]
    usd = core_min / 60.0 * GATE["rate_usd_per_core_h"]
    v = "PASS" if core_min <= GATE["core_min_hard"] else "GATE FAIL"
    return v, ["%.3f core-min of the HARD %.1f; $%.6f DERIVED at $%.4f/core-h, "
               "REPORTED-BY-OWNER, NOT MEASURED"
               % (core_min, GATE["core_min_hard"], usd, GATE["rate_usd_per_core_h"])]


# ---------------------------------------------------------------- controls
def keycheck(runscript, verbose=True):
    """L-273 remedy 2: assert the PRODUCER's key set equals the CONSUMER's."""
    src = open(runscript).read()
    # _state(tag) emits '"%s_FIELD" % tag' -- the FIELD is the SUFFIX. Getting this
    # regex backwards is what the first run of this control caught, before the freeze.
    produced = set(re.findall(r'"%s_(\w+)"\s*%\s*tag', src))
    tags = set(re.findall(r'_state\("(\w+)"\)', src))
    keys = {"%s_%s" % (t, f) for t in tags for f in produced}
    keys |= set(re.findall(r'out\["(\w+)"\]\s*=', src))
    keys |= set(re.findall(r'"(\w+)":\s*"?\w', src)) & {"task"}
    consumed = set()
    me = open(__file__).read()
    for pat in (r'summary\.get\("(\w+)"', r'summary\[\s*"(\w+)"\s*\]'):
        consumed |= set(re.findall(pat, me))
    missing = sorted(consumed - keys)
    ok = not missing
    if verbose:
        print("KEYCHECK producer keys (%d): %s" % (len(keys), sorted(keys)))
        print("KEYCHECK consumer keys (%d): %s" % (len(consumed), sorted(consumed)))
        print("KEYCHECK consumed-but-never-produced: %s" % (missing or "NONE"))
        print("KEYCHECK: %s" % ("OK" if ok else "REFUSE -- L-273 defect present"))
    return ok


def selftest(a4_ipopt, a4_log):
    """G5 -- planted-zero control. Plants into files the A4 PRODUCER actually
    wrote (L-273), then asserts every reader SEES the plant."""
    print("=== G5 PLANTED-ZERO CONTROL (zero compute) ===")
    print("producer artifacts (written by A4's own runs, not by this control):")
    print("  %s" % a4_ipopt)
    print("  %s" % a4_log)
    seen = []

    base = parse_ipopt(a4_ipopt)
    print("\n[1] IPOPT reader, UNPLANTED: exit=%r n_iter=%s objective=%r constr_viol=%r nlp_error=%r"
          % (base["exit"], base["n_iter"], base["objective"], base["constr_viol"], base["nlp_error"]))
    if base["exit"] is None or base["objective"] is None:
        print("REFUSE (exit 2): the IPOPT reader cannot read a real IPOPT file.")
        return 2

    raw = open(a4_ipopt, errors="replace").read()
    p1 = raw.replace("EXIT: Optimal Solution Found.",
                     "EXIT: Maximum Number of Iterations Exceeded.")
    p1 = re.sub(r"(Constraint violation\.*:\s*)([-\d.eE+]+)", r"\g<1>3.7000000000000000e-03", p1)
    tmp = a4_ipopt + ".PLANTED.tmp"
    open(tmp, "w").write(p1)
    pl = parse_ipopt(tmp)
    os.unlink(tmp)
    print("[2] IPOPT reader, PLANTED (exit -> cap-stop, constr_viol -> 3.7e-03):")
    print("    exit=%r constr_viol=%r" % (pl["exit"], pl["constr_viol"]))
    ok1 = ("Maximum Number of Iterations" in (pl["exit"] or "")) and pl["constr_viol"] == 3.7e-3
    seen.append(("IPOPT exit + constraint violation", ok1))
    v, n = g2_termination(pl, {"reduction_pct": 1.0})
    print("    G2 on the planted file -> %s  (%s)" % (v, n[0]))
    seen.append(("G2 refuses a cap-stop", v != "PASS"))

    text = open(a4_log, errors="replace").read()
    blocks = parse_check_totals(text)
    print("\n[3] check_totals reader, UNPLANTED: %d block(s) in the real A4 log" % len(blocks))
    if not blocks:
        print("REFUSE (exit 2): the check_totals reader sees nothing in a log that has one.")
        return 2
    b = blocks[-1]
    rows = per_component(b)
    print("    wrt=%s analytic=%s fd=%s rel=%.4f%% flip=%s"
          % (b["wrt"], b["analytic"], b["fd"], rows[0]["rel_pct"], rows[0]["flip"]))
    seen.append(("check_totals reads a real block", rows[0]["rel_pct"] < 100.0))

    planted = dict(b)
    planted["fd"] = [-x for x in b["fd"]]           # plant: flip the FD sign
    rp = per_component(planted)
    print("[4] check_totals grading, PLANTED (FD sign flipped): rel=%.4f%% flip=%s"
          % (rp[0]["rel_pct"], rp[0]["flip"]))
    seen.append(("per-component sign flip is seen", rp[0]["flip"] is True))

    planted2 = dict(b)
    planted2["analytic"] = [x * 1.30 for x in b["analytic"]]   # plant: +30% error
    r2 = per_component(planted2)
    print("[5] check_totals grading, PLANTED (analytic x1.30): rel=%.4f%% (band %.1f%%)"
          % (r2[0]["rel_pct"], GATE["fd_band_pct"]))
    seen.append(("a %.0f%% error exceeds the %.0f%% band" % (30, GATE["fd_band_pct"]),
                 r2[0]["rel_pct"] > GATE["fd_band_pct"]))

    print("\n[6] G-eta, PLANTED unseen perturbation (plant moved CD by 0.0):")
    v, n = g_eta({"eta_delta_repeat": 1e-9, "eta_plant_dCD": 0.0,
                  "eta_plant_dv": GATE["eta_plant_dv"]})
    print("    -> %s  (%s)" % (v, n[-1]))
    seen.append(("G-eta refuses an unseen plant", v == "BLOCKED"))
    print("[7] G-eta, PLANTED noisy objective (delta_repeat = 1.0e-3):")
    v, n = g_eta({"eta_delta_repeat": 1.0e-3, "eta_plant_dCD": 2.4e-5,
                  "eta_plant_dv": GATE["eta_plant_dv"]})
    print("    -> %s  (%s)" % (v, n[-1]))
    seen.append(("G-eta blocks above the noise ceiling", v == "BLOCKED"))
    print("[8] G-eta, quiet objective (delta_repeat = 1.0e-9):")
    v, n = g_eta({"eta_delta_repeat": 1.0e-9, "eta_plant_dCD": 2.4e-5,
                  "eta_plant_dv": GATE["eta_plant_dv"]})
    print("    -> %s" % v)
    seen.append(("G-eta passes a quiet objective", v == "PASS"))

    print("\n[9] G1, PLANTED out-of-bound constraint (thickcon 0.5, volcon 0.90):")
    v, n = g1_constraints({"final_thickcon_slant": [1.0, 0.5], "final_volcon_aft": [0.90]},
                          {"constr_viol": 0.0})
    print("    -> %s  (%s)" % (v, "; ".join(n[1:3])))
    seen.append(("G1 sees an out-of-bound constraint", v == "GATE FAIL"))
    print("[10] G1, in-bound control:")
    v, _ = g1_constraints({"final_thickcon_slant": [1.0, 1.02], "final_volcon_aft": [1.00]},
                          {"constr_viol": 1e-9})
    print("    -> %s" % v)
    seen.append(("G1 passes an in-bound design", v == "PASS"))

    print("\n[11] G-theta, PLANTED angle outside the band (d=(+0.05, -0.05)):")
    v, n, th = g_theta({"final_shapeBreak": 0.05, "final_shapeRear": -0.05})
    print("    -> %s  theta=%.3f deg" % (v, th))
    seen.append(("G-theta sees an out-of-band angle", v == "GATE FAIL"))
    print("[12] G-theta, baseline control (d=(0,0)) must read 25.0 deg:")
    v, n, th = g_theta({"final_shapeBreak": 0.0, "final_shapeRear": 0.0})
    print("    -> %s  theta=%.4f deg" % (v, th))
    seen.append(("G-theta reproduces the 25 deg design angle", abs(th - 25.0) < 0.05))
    print("[13] G-theta at A4's own optimum (d=(-0.05, 0)):")
    v, n, th = g_theta({"final_shapeBreak": -0.05, "final_shapeRear": 0.0})
    print("    -> %s  theta=%.3f deg" % (v, th))

    print("\n=== CONTROL SUMMARY ===")
    bad = 0
    for name, ok in seen:
        print("  %-52s %s" % (name, "SEEN" if ok else "NOT SEEN"))
        bad += 0 if ok else 1
    if bad:
        print("\nCOMPARATOR REFUSES (exit 2): %d control(s) not seen. A zero from this "
              "reader would not be evidence (CLAUDE.md rule 3)." % bad)
        return 2
    print("\nALL CONTROLS SEEN. The comparator is shown able to produce a non-PASS "
          "on planted defects in files the A4 producer actually wrote (L-273).")
    return 0


# ---------------------------------------------------------------- grade
def grade(a):
    print("=== D3 GRADING ===")
    summary = json.load(open(a.summary)) if a.summary and os.path.exists(a.summary) else {}
    jac = summary.get("G_jac")
    out = []
    if a.eta_summary and os.path.exists(a.eta_summary):
        es = json.load(open(a.eta_summary))
        out.append(("G-eta", ) + g_eta(es))
    if a.ipopt and os.path.exists(a.ipopt):
        ip = parse_ipopt(a.ipopt)
        out.append(("G1 constraints", ) + g1_constraints(summary, ip))
        out.append(("G2 termination", ) + g2_termination(ip, summary))
    if a.log and os.path.exists(a.log):
        text = open(a.log, errors="replace").read()
        out.append(("G3+G4 endpoint FD", ) + g3_endpoint(steps_from_log(text)))
        m = re.search(r"IDWARP_SO_MD5:\s*([0-9a-f]{32})", text)
        got = m.group(1) if m else None
        want = GATE["md5_%s" % a.row]
        out.append(("G7 image identity", "PASS" if got == want else "GATE FAIL",
                    ["row %s: read %s, registered %s" % (a.row, got, want)]))
    if summary.get("final_shapeBreak") is not None:
        v, n, _ = g_theta(summary, jac)
        out.append(("G-theta slant angle", v, n))
    out.append(("G10 cost", ) + g_cost(a.core_min))
    for name, verdict, notes in out:
        print("\n%-22s %s" % (name, verdict))
        for n in notes:
            print("    %s" % n)
    print("\nVocabulary: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--keycheck", metavar="RUNSCRIPT")
    ap.add_argument("--a4-ipopt",
                    default="/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt/opt_IPOPT.txt")
    ap.add_argument("--a4-log",
                    default="/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt.log")
    ap.add_argument("--summary")
    ap.add_argument("--eta-summary")
    ap.add_argument("--ipopt")
    ap.add_argument("--log")
    ap.add_argument("--row", choices=["patched", "shipped"], default="patched")
    ap.add_argument("--core-min", type=float)
    a = ap.parse_args()
    if a.keycheck:
        return 0 if keycheck(a.keycheck) else 2
    if a.selftest:
        return selftest(a.a4_ipopt, a.a4_log)
    return grade(a)


if __name__ == "__main__":
    sys.exit(main())
