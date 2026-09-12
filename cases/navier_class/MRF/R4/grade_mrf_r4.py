#!/usr/bin/env python3
"""grade_mrf_r4.py -- the SINGLE-GRID comparator for MRF_R4.

Registered by verification/campaign/MRF_R4_PREREGISTRATION.md and pinned by the
queue entry's `grading_freeze`. It grades ONE level against ONE band and it
REFUSES (exit 2) rather than degrade.

WHAT IT WILL NOT DO, BY CONSTRUCTION:
  * it will not print `PASS`. R4 has no grid triple, so rule 5's PASS is not
    reachable and the word is absent from this file's output vocabulary
    (section 2.1 of the registration). The verdicts it can emit are
    GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED.
  * it will not accept a run at a rank count other than the registered 6
    (section 6) -- RANKS.txt is read and compared.
  * it will not report a zero it has not shown itself able to see: a planted
    perturbation is written into a COPY of moment.dat and read back through the
    same reader, and the script exits 2 if the reader cannot see it (rule 3).

ITERATIVE CONVERGENCE (section 5) -- every limb's window is ABSOLUTE. None is a
function of n_iters, so no limb can be flipped by lengthening the run on the same
events; IC-1 is monotone (once failed, failed at every longer n).

usage: grade_mrf_r4.py <RUNDIR> [--json OUT]
"""
import json, math, os, re, sys

BAND        = (5.29, 5.53)          # Beshay 5.41 +/- 2.3 %
ENVELOPE    = (4.54, 6.28)          # Beshay 5.41 +/- 16 %
PREDICTION  = (5.20, 5.40)          # frozen before the run, reported never gated
REF_MEASURED = 5.41
RHO, N, D   = 998.0, 5.0, 0.100
ENDTIME     = 8000
RANKS       = 6
N_WARMUP    = 2000                  # ABSOLUTE, never a fraction of n_iters
TAIL        = 2000                  # ABSOLUTE window length
FIELDS      = ["U", "p", "phi", "k", "omega", "nut"]
PLANT       = 1.234e-03
VOCAB       = {"GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED"}


def die(msg, code=2):
    print(f"REFUSING: {msg}", file=sys.stderr)
    sys.exit(code)


# --------------------------------------------------------------- the readers
def read_np_series(moment_dat):
    """iterations and Np from the z-moment column. One reader, used everywhere."""
    it, npv = [], []
    den = RHO * N ** 2 * D ** 5
    with open(moment_dat) as f:
        for line in f:
            if line.lstrip().startswith("#"):
                continue
            c = line.split()
            if len(c) < 4:
                continue
            it.append(float(c[0]))
            npv.append(2.0 * math.pi * abs(float(c[3])) / den)
    if not it:
        die(f"{moment_dat}: no data rows")
    return it, npv


def bounding_events(log):
    """iteration numbers at which a field was bounded or limited."""
    ev, n = [], 0
    pat_it = re.compile(r"^Time = (\d+)")
    pat_b = re.compile(r"bounding |Limiting |limiter ", re.I)
    for line in open(log, errors="ignore"):
        m = pat_it.match(line)
        if m:
            n = int(m.group(1))
        elif pat_b.search(line):
            ev.append(n)
    return ev


def final_residuals(log):
    out, pat = {}, re.compile(r"Solving for (\w+), Initial residual = ([\d.eE+-]+)")
    for line in open(log, errors="ignore"):
        m = pat.search(line)
        if m:
            out[m.group(1)] = float(m.group(2))
    cont = None
    for line in open(log, errors="ignore"):
        if "continuity errors" in line and "cumulative" in line:
            m = re.search(r"cumulative = ([\d.eE+-]+)", line)
            if m:
                cont = abs(float(m.group(1)))
    return out, cont


def nan_or_fpe(log):
    t = open(log, errors="ignore").read()
    return ("nan" in t.lower().split("floating")[0][-2_000_000:] and
            re.search(r"\bnan\b", t, re.I) is not None), ("Floating point exception" in t)


# --------------------------------------------------- rule 3, planted control
def planted_zero_control(moment_dat, scratch):
    lines = open(moment_dat).read().splitlines()
    idx = next(i for i, l in enumerate(lines) if not l.lstrip().startswith("#"))
    c = lines[idx].split()
    c[3] = f"{float(c[3]) + PLANT:.8e}"
    lines[idx] = "\t".join(c)
    probe = os.path.join(scratch, "moment_planted.dat")
    open(probe, "w").write("\n".join(lines) + "\n")
    _, base = read_np_series(moment_dat)
    _, bump = read_np_series(probe)
    den = RHO * N ** 2 * D ** 5
    seen = abs(bump[0] - base[0])
    want = 2.0 * math.pi * PLANT / den
    ok = abs(seen - want) < 1e-9
    os.remove(probe)
    return {"planted_Nm": PLANT, "expected_dNp": want, "seen_dNp": seen,
            "reader": "read_np_series", "artifact": moment_dat, "passed": bool(ok)}


# --------------------------------------------------------------------- main
def main():
    if len(sys.argv) < 2:
        die("usage: grade_mrf_r4.py <RUNDIR> [--json OUT]")
    run = os.path.abspath(sys.argv[1])
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]
    log = os.path.join(run, "log.simpleFoam")
    mom = os.path.join(run, "postProcessing", "impellerForces", "0", "moment.dat")
    for p in (log, mom):
        if not os.path.isfile(p):
            die(f"missing required artifact: {p}")

    r = {"rung": "MRF_R4", "single_grid": True,
         "stamp": "SINGLE GRID -- NO GRID-CONVERGENCE CLAIM",
         "band": list(BAND), "envelope": list(ENVELOPE),
         "prediction_frozen_before_run": list(PREDICTION),
         "reference": {"value": REF_MEASURED,
                       "source": "Beshay, Kratena, Fort & Bruha, Acta Polytechnica 41(6) 2001, "
                                 "Table 3, small rig, h/T = 0.33, MEASURED by strain-gauge torquemeter",
                       "scatter_stated": "average relative standard deviation 2.3 to 16 %, "
                                         "given ACROSS impellers and NOT per impeller"},
         "run_dir": run}

    # --- rule 3 FIRST: a reader not shown able to see a non-zero is not evidence
    r["planted_zero"] = planted_zero_control(mom, os.path.dirname(mom))
    if not r["planted_zero"]["passed"]:
        die("PLANTED-ZERO CONTROL FAILED -- the reader cannot see a known perturbation")

    # --- registered rank count (section 6)
    rp = os.path.join(run, "RANKS.txt")
    ranks = int(open(rp).read().strip()) if os.path.isfile(rp) else None
    r["ranks"] = ranks
    if ranks != RANKS:
        r["verdict"] = "NOT A RESULT"
        r["why"] = (f"ranks = {ranks}, but MRF_R4 registers {RANKS} as the ONLY rank count "
                    "it may run at (section 6); a run at any other rank count is not this "
                    "registration's run")
        return emit(r, out_json)

    # --- rule 4 completion, every clause its own boolean
    rc_p = os.path.join(run, "RC.txt")
    times = sorted(float(d) for d in os.listdir(run)
                   if re.fullmatch(r"\d+(\.\d+)?", d) and os.path.isdir(os.path.join(run, d)))
    txt = open(log, errors="ignore").read()
    zero_t = os.path.join(run, "0")
    end_dir = os.path.join(run, str(ENDTIME))
    comp = {
        "rc_zero": os.path.isfile(rc_p) and open(rc_p).read().strip() == "0",
        "end_line": "\nEnd\n" in txt,
        "exec_count_equals_endTime": txt.count("ExecutionTime = ") == ENDTIME,
        "last_time_equals_endTime": bool(times) and times[-1] == float(ENDTIME),
        "fields_present": all(os.path.exists(os.path.join(end_dir, f)) for f in FIELDS),
        "age_guard": (os.path.isdir(end_dir) and os.path.isdir(zero_t) and
                      all(os.path.getmtime(os.path.join(end_dir, f)) >
                          os.path.getmtime(os.path.join(zero_t, "U"))
                          for f in FIELDS if os.path.exists(os.path.join(end_dir, f)))),
    }
    r["completion"] = comp
    if not all(comp.values()):
        r["verdict"] = "BLOCKED"
        r["why"] = ("rule 4 is all-or-nothing and these clauses are false: "
                    + ", ".join(k for k, v in comp.items() if not v))
        return emit(r, out_json)

    # --- iterative convergence, section 5. Every window ABSOLUTE.
    ev = bounding_events(log)
    res, cont = final_residuals(log)
    nan, fpe = nan_or_fpe(log)
    it, npv = read_np_series(mom)
    tail = [v for i, v in zip(it, npv) if i > it[-1] - TAIL]
    mean = sum(tail) / len(tail)
    spread = max(abs(v - mean) for v in tail) / mean
    n = len(tail)
    xs = list(range(n))
    xm, ym = sum(xs) / n, mean
    sxy = sum((x - xm) * (y - ym) for x, y in zip(xs, tail))
    sxx = sum((x - xm) ** 2 for x in xs) or 1.0
    drift = abs(sxy / sxx * (n - 1)) / mean
    ic = {
        "IC1_no_bounding_after_2000": {
            "events_after_warmup": [e for e in ev if e > N_WARMUP],
            "passed": not [e for e in ev if e > N_WARMUP],
            "window": f"({N_WARMUP}, n] -- ABSOLUTE left edge; extending can only ADD events"},
        "IC2_no_nan_no_fpe": {"nan": nan, "fpe": fpe, "passed": not (nan or fpe)},
        "IC3_residual_floor": {
            "final": {k: res.get(k) for k in ("Ux", "Uy", "Uz", "k", "omega")},
            "cumulative_continuity": cont,
            "passed": all((res.get(k) is not None and res[k] <= 1e-5)
                          for k in ("Ux", "Uy", "Uz", "k", "omega"))
                      and (cont is not None and cont <= 1e-6),
            "note": "p's raw initial residual is NOT gated: closed domain, floating "
                    "pressure reference (NUMERICS_KNOWLEDGE N-X4)"},
        "IC4_stationarity": {
            "window_iterations": TAIL, "mean_Np": mean,
            "max_rel_excursion": spread, "rel_linear_drift": drift,
            "passed": spread <= 0.005 and drift <= 0.002},
    }
    r["iterative_convergence"] = ic
    r["Np"] = npv[-1]
    r["Np_window_mean"] = mean
    if not all(v["passed"] for v in ic.values()):
        r["verdict"] = "NOT A RESULT"
        r["why"] = ("iterative convergence refused on: "
                    + ", ".join(k for k, v in ic.items() if not v["passed"])
                    + ". endTime is NOT extended to chase a limb (section 5).")
        return emit(r, out_json)

    # --- the band
    v = r["Np"]
    r["vs_reference_pct"] = 100.0 * (v - REF_MEASURED) / REF_MEASURED
    r["in_envelope"] = ENVELOPE[0] <= v <= ENVELOPE[1]
    r["prediction_satisfied"] = PREDICTION[0] <= v <= PREDICTION[1]
    r["verdict"] = "GATE REACHED" if BAND[0] <= v <= BAND[1] else "GATE FAIL"
    r["why"] = (f"Np = {v:.4f} against the registered band [{BAND[0]}, {BAND[1]}] "
                f"(Beshay measured {REF_MEASURED} +/- 2.3 %), {r['vs_reference_pct']:+.2f} % "
                f"from the measurement. SINGLE GRID -- no grid-convergence claim, and "
                f"PASS is not reachable by this rung.")
    if r["verdict"] == "GATE FAIL":
        r["sanaa_sentence"] = ("At t/D = 0.0155 our geometry is Beshay's geometry in every "
                               "ratio. THIS IS THE PROBLEM TO REPORT AND FIX, NOT TO EXPLAIN "
                               "AWAY. 'Different tank' is not an available explanation.")
    return emit(r, out_json)


def emit(r, out_json):
    assert r["verdict"] in VOCAB, f"verdict outside the fixed vocabulary: {r['verdict']}"
    assert "PASS" not in r["verdict"], "this comparator may not emit PASS"
    if out_json:
        with open(out_json, "w") as f:
            json.dump(r, f, indent=2)
    print(json.dumps(r, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
