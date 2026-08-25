#!/usr/bin/env python3
"""F6a / C-15 grading wrapper -- the comparator for the FROZEN pre-registration
`verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md`.

WHAT THIS FILE IS. It implements gates that are ALREADY FROZEN. It defines none.
Every threshold below is transcribed from the frozen document with its section
number beside it, and `--show-frozen` prints them for a diff against that text.

THE HAZARD THIS FILE IS WRITTEN UNDER, STATED RATHER THAN LEFT IMPLICIT.
This code was written with **1.2531 already known** -- the SST reattachment this
box has measured for this case, mesh and closure. The risk is NOT that a gate
moves: the gates carry explicit numbers and are frozen.  The risk is that an
AMBIGUOUS CLAUSE GETS IMPLEMENTED IN THE DIRECTION OF THE EXPECTED ANSWER.

Three things blunt it, and they are named so a reader can check them rather than
trust them:
  1. The EXTRACTION path is PINNED BY HASH (`EXTRACTOR_SHA256`). The code that
     actually produces x_r/c and x_s/c is frozen and is invoked as a subprocess,
     never edited, never re-implemented here. A hash mismatch REFUSES.
  2. Section 3's clauses carry EXPLICIT NUMERIC thresholds -- peak-to-peak
     <= 0.0055 / 0.0033, at most ONE sign alternation across 10 samples -- so
     there is little room to implement them "in a direction".
  3. The one genuinely ambiguous clause is named in `select_bubble_pair()` and in
     the pre-registration's amendment, and it is resolved from GEOMETRY ALONE.

REFUSE, NEVER DEGRADE. Every unevaluable clause exits 2. A missing residual line,
a truncated log, fewer than 10 samples, a blind reader, a hash mismatch: all are
refusals. None is a pass.

Exit codes: 0 graded (verdict in the JSON) | 2 REFUSAL | 3 usage error.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"

# --------------------------------------------------------------------------
# FROZEN CONSTANTS. Every one is transcribed from the pre-registration, and the
# section it comes from is on the same line. NOTHING HERE IS THIS FILE'S CHOICE.
# --------------------------------------------------------------------------
PREREG = "verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md"
# THE FROZEN BODY, not the whole file. Rule 2 makes pre-compute amendments LEGAL and
# rule 6 appends them AT THE FOOT with the assertion `lines whose number changed above
# this section: 0`. Hashing the whole file would make the frozen text un-verifiable the
# moment a legal amendment landed -- and would quietly pressure a future lane to skip
# the amendment to keep a hash green. So the pin is on everything ABOVE the marker,
# which is byte-for-byte the document as frozen at commit 5b6b1ece.
PREREG_SHA256 = "9989f1f909b358ae30c663b041598358cf247f6aee2a8b3dcb6bda99543a30cc"
FROZEN_BODY_MARKER = "<!-- FROZEN-BODY-ENDS-HERE -->"

EXTRACTOR = "cases/dafoam/f6a_nasa_hump/case/hump_gate_analysis.py"   # ss9.3
EXTRACTOR_SHA256 = "9a6ec8553b863b3b43a1a3ca03970923778f7da5c2bf3e1cfacdfa8f6fd2414f"
EXTRACTOR_BLOB = "ec263bed8623a81b67106c3880febdca1b3d5eff"

CHORD = 0.42                       # ss6.1, m

P1_TARGET, P1_BAND = 0.665, (0.63175, 0.69825)   # ss2.2 / ss2.3 gate P1
P2_TARGET, P2_BAND = 1.10, (1.045, 1.155)        # ss2.2 / ss2.3 gate P2
MODEL_FORM_TOL = 0.05                            # ss2.3, +/-5 %, inherited from 74797a57

# REPORTED -- NOT A GATE. These never move a verdict (ss2.3, ss2.4, ss11).
REPORTED_SEP_2PCT_BAND = (0.6517, 0.6783)        # ss2.3
REPORTED_OILFILM_LIMB = 1.11                     # ss1.5.2 / ss2.1, off-centerline
REPORTED_OILFILM_BAND = (1.0545, 1.1655)         # ss2.1 robustness

# ss3.1 plateau clauses
RESIDUAL_CONTROLS = {"U": 5e-7, "p": 5e-7, "k": 5e-7, "omega": 1e-10}   # (P-b)
ENDTIME_CAP = 2000                                                      # (P-a)
SAMPLE_STRIDE = 50                                                      # (P-c)
SAMPLE_WINDOW = 500                                                     # (P-c)
N_SAMPLES = 10                                                          # (P-c)
PTP_MAX = {"reattachment": 0.0055, "separation": 0.0033}                # (P-c)
MAX_SIGN_ALTERNATIONS = 1                                               # (P-d)

# ss3.3 planted-zero control. Bands are LINE-INDEX positions into the raw file's
# data lines, chosen by POSITION and never by value match (rule 3).
PLANT_BANDS = ((40, 60), (120, 140), (200, 220), (300, 320))
PLANT_CF_FLOOR = 1e-5

REQUIRED_FIELDS = ("U", "p", "k", "omega", "nut")   # ss9.4 -- incompressible family
AGE_GUARD_ANCHOR = "0/U"                            # ss9.4 -- NOT 0/T; no T in this case

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


class Refusal(Exception):
    """Exit 2. An unevaluable clause is a refusal, never a pass (ss3.2)."""


def refuse(msg):
    raise Refusal(msg)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_pinned(repo=REPO):
    """rule 2 / ss9.3: the file that runs must BE the file that was frozen."""
    ep = os.path.join(repo, EXTRACTOR)
    if not os.path.exists(ep):
        refuse("extraction path absent: %s" % ep)
    got = sha256_of(ep)
    if got != EXTRACTOR_SHA256:
        refuse("EXTRACTOR HASH MISMATCH -- frozen %s, on disk %s. ss9.3: the campaign "
               "STOPS. The clause is not relaxed to match the code." % (EXTRACTOR_SHA256, got))
    pp = os.path.join(repo, PREREG)
    if os.path.exists(pp):
        raw = open(pp, "rb").read()
        marker = FROZEN_BODY_MARKER.encode()
        body = raw.split(marker, 1)[0] if marker in raw else raw
        gotp = hashlib.sha256(body).hexdigest()
        if gotp != PREREG_SHA256:
            refuse("PRE-REGISTRATION FROZEN-BODY HASH MISMATCH -- frozen %s, on disk %s. "
                   "The graded text is not the frozen text. ss9.3: the campaign STOPS."
                   % (PREREG_SHA256, gotp))
    return got


# --------------------------------------------------------------------------
# raw wall data
# --------------------------------------------------------------------------
def read_raw_lines(path):
    """Return (data_line_indices, rows). Line indices are POSITIONS in the file's
    data-line sequence -- the addressing rule 3's plant requires."""
    rows, idx = [], []
    with open(path) as fh:
        for n, line in enumerate(fh):
            if line.startswith("#") or not line.strip():
                continue
            idx.append(n)
            rows.append(line.split())
    if not rows:
        refuse("raw file has no data lines: %s" % path)
    return idx, rows


def wall_crest_xc(raw_path):
    """ss2.2's 'the hump crest', resolved FROM GEOMETRY ALONE.

    THIS IS THE ONE PLACE THE FROZEN TEXT LEFT AN IMPLEMENTATION CHOICE, and it
    is made here in the open. ss2.2 says separation is 'the FIRST crossing
    downstream of the hump crest'; it does not give the crest a number.

    The crest is taken as the x of MAXIMUM WALL HEIGHT (the z column of the wall
    sample), read from the case's own geometry. WHY THIS CANNOT BE
    ANSWER-DIRECTED: wall height is a property of the MESH. It does not depend on
    the solution, on Cf, or on any closure, so it is identical for every run of
    this case and cannot be tuned toward 1.2531 or away from it. It is computed
    BEFORE any crossing is examined.

    On the shipped 51,626-cell mesh this returns x/c = 0.5147, which excludes the
    two spurious near-zero crossings the extractor reports (-0.0129, +0.0072) and
    admits the physical pair. The mutation control proves the exclusion bites.
    """
    _, rows = read_raw_lines(raw_path)
    best_x, best_z = None, None
    for r in rows:
        if len(r) < 3:
            refuse("malformed wall row (need x y z ...): %r" % (r,))
        x, z = float(r[0]), float(r[2])
        if best_z is None or z > best_z:
            best_x, best_z = x, z
    return best_x / CHORD, best_z


def select_bubble_pair(all_crossings, crest_xc):
    """ss2.2: separation = FIRST crossing downstream of the crest; reattachment =
    FIRST crossing downstream of separation. Refuses rather than guessing."""
    downstream = sorted([(float(x), t) for x, t in all_crossings if float(x) > crest_xc])
    if len(downstream) < 2:
        refuse("ss2.2 needs a separation and a reattachment downstream of the crest "
               "(x/c > %.6f); found %d crossing(s)" % (crest_xc, len(downstream)))
    x_s, t_s = downstream[0]
    x_r, t_r = downstream[1]
    if not t_s.startswith("sep"):
        refuse("ss2.2: first crossing downstream of the crest is %r, not a separation. "
               "Refusing rather than reinterpreting a frozen definition." % t_s)
    if not t_r.startswith("reattach"):
        refuse("ss2.2: first crossing after separation is %r, not a reattachment." % t_r)
    return x_s, x_r


# --------------------------------------------------------------------------
# the pinned extractor, invoked -- never re-implemented
# --------------------------------------------------------------------------
def run_extractor(case, time, repo=REPO):
    assert_pinned(repo)
    src = os.path.join(repo, EXTRACTOR)
    proc = subprocess.run([sys.executable, src, case, str(time)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        refuse("pinned extractor exited %d for time %s:\n%s"
               % (proc.returncode, time, proc.stderr[-2000:]))
    out = os.path.join(case, "gate_result_%s.json" % time)
    if not os.path.exists(out):
        refuse("pinned extractor wrote no %s" % out)
    with open(out) as fh:
        return json.load(fh)


def extract_pair(case, time, repo=REPO):
    res = run_extractor(case, time, repo)
    raw = os.path.join(case, "postProcessing", "wallValues", str(time),
                       "wallShearStress_wallValues.raw")
    crest_xc, _ = wall_crest_xc(raw)
    x_s, x_r = select_bubble_pair(res["all_crossings"], crest_xc)
    return {"time": str(time), "separation": x_s, "reattachment": x_r,
            "crest_xc": crest_xc, "n_crossings": len(res["all_crossings"])}


# --------------------------------------------------------------------------
# ss3.3 PLANTED-ZERO CONTROL -- on the READER, planted BY LINE INDEX
# --------------------------------------------------------------------------
def plant_and_reread(case, time, scratch, repo=REPO):
    """rule 3: a zero from a reader not shown able to see a non-zero is not
    evidence. A known perturbation is written into a COPY of the extracted trace,
    re-read THROUGH THE SAME EXTRACTION PATH, and the reader REFUSES unless it
    comes back.

    Planted BY LINE INDEX into the raw file's data-line sequence -- never by
    value match -- so a reader that silently returns nothing cannot be mistaken
    for a reader that correctly found nothing.
    """
    src_dir = os.path.join(case, "postProcessing", "wallValues", str(time))
    if not os.path.isdir(src_dir):
        refuse("no wall sample directory to plant into: %s" % src_dir)

    baseline = run_extractor(case, time, repo)
    n_before = len(baseline["all_crossings"])

    plant_case = os.path.join(scratch, "plant_case")
    if os.path.exists(plant_case):
        shutil.rmtree(plant_case)
    dst_dir = os.path.join(plant_case, "postProcessing", "wallValues", str(time))
    os.makedirs(dst_dir)
    for name in os.listdir(src_dir):
        shutil.copy2(os.path.join(src_dir, name), os.path.join(dst_dir, name))

    tau_path = os.path.join(dst_dir, "wallShearStress_wallValues.raw")
    with open(tau_path) as fh:
        lines = fh.readlines()
    data_pos = [n for n, l in enumerate(lines) if not l.startswith("#") and l.strip()]

    chosen = None
    for i0, i1 in PLANT_BANDS:
        if i1 > len(data_pos):
            continue
        taus = [float(lines[data_pos[k]].split()[3]) for k in range(i0, i1)]
        signs = {t > 0 for t in taus}
        if len(signs) == 1 and min(abs(t) for t in taus) > PLANT_CF_FLOOR:
            chosen = (i0, i1)
            break
    if chosen is None:
        refuse("ss3.3: no line-index band qualified for planting. REFUSING rather "
               "than sliding to a band chosen by value.")
    i0, i1 = chosen

    xs_planted = []
    for k in range(i0, i1):
        n = data_pos[k]
        parts = lines[n].split()
        xs_planted.append(float(parts[0]) / CHORD)
        parts[3] = repr(-float(parts[3]))
        lines[n] = " ".join(parts) + "\n"
    with open(tau_path, "w") as fh:
        fh.writelines(lines)

    planted = run_extractor(plant_case, time, repo)
    n_after = len(planted["all_crossings"])
    lo, hi = min(xs_planted), max(xs_planted)

    # THE WINDOW MUST BRACKET THE FLIPPED BLOCK, NOT SPAN IT. A sign crossing is
    # INTERPOLATED between the last unflipped sample and the first flipped one, so
    # it lands one sample spacing OUTSIDE [lo, hi]. The first form of this control
    # spanned [lo, hi] and refused a reader that had demonstrably seen the plant
    # (4 -> 6 crossings): a control that is wrong in the refusing direction is still
    # wrong, and it is corrected here rather than loosened by a fudge factor.
    all_xc = sorted(float(r[0]) / CHORD for r in read_raw_lines(tau_path)[1])
    below = [x for x in all_xc if x < lo - 1e-12]
    above = [x for x in all_xc if x > hi + 1e-12]
    win_lo = max(below) if below else lo
    win_hi = min(above) if above else hi

    before_xc = [float(x) for x, _ in baseline["all_crossings"]]
    new_in_band = [float(x) for x, _ in planted["all_crossings"]
                   if win_lo - 1e-12 <= float(x) <= win_hi + 1e-12
                   and not any(abs(float(x) - b) < 1e-9 for b in before_xc)]

    ok = (n_after > n_before) and bool(new_in_band)
    detail = {"line_index_band": [i0, i1], "planted_xc_range": [lo, hi],
              "acceptance_window": [win_lo, win_hi],
              "crossings_before": n_before, "crossings_after": n_after,
              "new_crossings_in_planted_range": new_in_band, "seen": ok}
    if not ok:
        refuse("ss3.3 PLANT DID NOT COME BACK -- the Cf reader is not shown able to "
               "see a non-zero. No gate verdict is written by a comparator whose "
               "plant did not return. detail=%s" % json.dumps(detail))
    return detail


# --------------------------------------------------------------------------
# log parsing
# --------------------------------------------------------------------------
RE_CONVERGED = re.compile(r"SIMPLE solution converged in (\d+) iterations")
RE_TIME = re.compile(r"^Time = (\d+)")
RE_EXEC = re.compile(r"^ExecutionTime = ")
RE_RESID = re.compile(
    r"Solving for (\w+),\s*Initial residual = ([0-9eE+.\-]+),\s*Final residual = ([0-9eE+.\-]+)")


def parse_log(log_path):
    if not os.path.exists(log_path):
        refuse("solver log absent: %s" % log_path)
    with open(log_path, errors="replace") as fh:
        lines = fh.readlines()
    if not lines:
        refuse("solver log is empty: %s" % log_path)

    converged_at = None
    for l in lines:
        m = RE_CONVERGED.search(l)
        if m:
            converged_at = int(m.group(1))
    times, exec_count, has_end = [], 0, False
    blocks = {}
    cur = None
    for l in lines:
        m = RE_TIME.match(l)
        if m:
            cur = int(m.group(1))
            times.append(cur)
            blocks[cur] = {}
            continue
        if RE_EXEC.match(l):
            exec_count += 1
        if l.strip() == "End":
            has_end = True
        m = RE_RESID.search(l)
        if m and cur is not None:
            fld, init = m.group(1), float(m.group(2))
            # FIRST outer-corrector value in the block is the INITIAL residual (P-b).
            blocks[cur].setdefault(fld, {"initial": init, "final": float(m.group(3))})
    if not times:
        refuse("solver log has no 'Time = ' blocks -- truncated? %s" % log_path)
    return {"converged_at": converged_at, "times": times, "last_time": times[-1],
            "exec_count": exec_count, "has_end": has_end, "blocks": blocks}


# --------------------------------------------------------------------------
# ss3.1 CLAUSES (P-a) .. (P-d). Each returns (ok: bool, detail: dict).
# --------------------------------------------------------------------------
def clause_p_a(log, endtime_cap=ENDTIME_CAP):
    """residualControl TRIPPED, not the iteration cap reached."""
    n = log["converged_at"]
    if n is None:
        return False, {"clause": "P-a", "ok": False,
                       "why": "no 'SIMPLE solution converged' line -- the run reached "
                              "its iteration cap. Reaching the cap is NOT convergence.",
                       "converged_at": None, "cap": endtime_cap}
    ok = n < endtime_cap
    return ok, {"clause": "P-a", "ok": ok, "converged_at": n, "cap": endtime_cap,
                "why": "" if ok else "converged_at %d is not < cap %d" % (n, endtime_cap)}


def clause_p_b(log, controls=None):
    """INITIAL residuals, never Final. This lab has already paid for the
    Initial/Final confusion ON THIS EXACT CASE (F6a_epistemic_band.md's 1.0722)."""
    controls = controls or RESIDUAL_CONTROLS
    t = log["converged_at"] if log["converged_at"] is not None else log["last_time"]
    blk = log["blocks"].get(t)
    if not blk:
        refuse("(P-b) unevaluable: no residual block at the converging iteration %s. "
               "A missing residual line is a REFUSAL, not a pass." % t)
    checked, worst_ok = {}, True
    for field, limit in controls.items():
        if field == "U":
            names = [k for k in blk if k in ("Ux", "Uy", "Uz")]
            if not names:
                refuse("(P-b) unevaluable: no U-component residuals at iteration %s" % t)
        else:
            names = [k for k in blk if k == field]
            if not names:
                refuse("(P-b) unevaluable: no '%s' residual at iteration %s" % (field, t))
        for nm in names:
            init = blk[nm]["initial"]          # INITIAL -- asserted, see below
            ok = init <= limit
            checked[nm] = {"initial": init, "limit": limit, "ok": ok,
                           "column_read": "Initial"}
            worst_ok = worst_ok and ok
    return worst_ok, {"clause": "P-b", "ok": worst_ok, "iteration": t,
                      "asserts_reading_initial_column": True, "fields": checked}


def clause_p_c(samples):
    """THE GATED FUNCTIONAL ITSELF MUST BE FLAT -- the clause VMFL051 needed.
    A residual floor is a statement about the linear solve, not about the answer."""
    if len(samples) != N_SAMPLES:
        refuse("(P-c) unevaluable: %d samples, ss3.1 requires exactly %d. Fewer than "
               "10 available samples is a REFUSAL." % (len(samples), N_SAMPLES))
    out, ok_all = {}, True
    for key in ("separation", "reattachment"):
        vals = [s[key] for s in samples]
        ptp = max(vals) - min(vals)
        lim = PTP_MAX[key]
        ok = ptp <= lim
        ok_all = ok_all and ok
        out[key] = {"ptp": ptp, "limit": lim, "ok": ok, "values": vals}
    return ok_all, {"clause": "P-c", "ok": ok_all, "quantities": out}


def clause_p_d(samples):
    """NO OSCILLATION -- the VMFL051 clause. VMFL051's triple was OSCILLATORY at
    R = -1.3486 and its deviation still read like a PASS."""
    if len(samples) != N_SAMPLES:
        refuse("(P-d) unevaluable: %d samples, need %d" % (len(samples), N_SAMPLES))
    out, ok_all = {}, True
    for key in ("separation", "reattachment"):
        vals = [s[key] for s in samples]
        incs = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        signs = [(1 if d > 0 else -1) for d in incs if d != 0.0]
        alt = sum(1 for i in range(len(signs) - 1) if signs[i] != signs[i + 1])
        ok = alt <= MAX_SIGN_ALTERNATIONS
        ok_all = ok_all and ok
        out[key] = {"sign_alternations": alt, "max_allowed": MAX_SIGN_ALTERNATIONS,
                    "ok": ok, "increments": incs}
    return ok_all, {"clause": "P-d", "ok": ok_all, "quantities": out}


# --------------------------------------------------------------------------
# ss9.4 COMPLETION (rule 4), with the age guard anchored on 0/U
# --------------------------------------------------------------------------
def endtime_reconciliation(log, declared_endtime):
    """A CONFLICT BETWEEN TWO FROZEN CLAUSES, SURFACED RATHER THAN SILENTLY RESOLVED.

    ss3.1 (P-a) REQUIRES `SIMPLE solution converged in N iterations` with
    **N < the registered endTime cap** -- reaching the cap is not convergence.
    ss9.4 (rule 4) REQUIRES **last time == endTime**.

    Read with `endTime` meaning the controlDict literal (2000), those two clauses are
    MUTUALLY EXCLUSIVE: satisfying (P-a) guarantees failing ss9.4, and every converging
    run would be `NOT A RESULT` by construction.

    The reconciliation is a FACT ABOUT THE SOLVER, not a choice made to fit an answer:
    on convergence `simpleControl::loop()` calls `runTime.writeAndEnd()`, which SETS
    the run's endTime to the current time. The run's EFFECTIVE endTime therefore IS the
    converged iteration, and `last time == endTime` holds against it. (P-a) independently
    gates that the termination was a genuine residualControl trip and not a cap hit, so
    nothing is loosened by reading it this way.

    BOTH READINGS ARE RETURNED AND BOTH ARE PRINTED. This function resolves nothing on
    its own authority; it makes the choice visible in every record the comparator writes,
    and the conflict is reported to the supervisor for a ruling.
    """
    conv = log.get("converged_at")
    residual_terminated = conv is not None
    effective = conv if residual_terminated else log["last_time"]
    return {
        "CLAUSE_CONFLICT": ("ss3.1 (P-a) requires convergence BELOW the endTime cap; "
                            "ss9.4 requires last time == endTime. Read literally against "
                            "the controlDict endTime the two cannot both hold."),
        "declared_endtime_controlDict": declared_endtime,
        "effective_endtime_used": effective,
        "last_time_in_log": log["last_time"],
        "residual_control_terminated": residual_terminated,
        "basis": ("OpenFOAM resets the run's endTime via runTime.writeAndEnd() on "
                  "convergence, so the effective endTime IS the converged iteration. "
                  "A solver fact, not a grading choice."),
        "clause_would_fail_on_declared": (log["last_time"] != declared_endtime),
        "DISPOSITION": "REPORTED TO THE SUPERVISOR FOR RULING. Not resolved by this lane.",
    }



def completion_check(case, log, endtime, rc, declared_endtime=None):
    fails = []
    if rc != 0:
        fails.append("rc = %s, not 0" % rc)
    if not log["has_end"]:
        fails.append("no 'End' line")
    if log["last_time"] != endtime:
        fails.append("last time %s != endTime %s" % (log["last_time"], endtime))
    tdir = os.path.join(case, str(endtime))
    anchor = os.path.join(case, AGE_GUARD_ANCHOR)
    if not os.path.isdir(tdir):
        fails.append("no time directory %s" % tdir)
    else:
        for f in REQUIRED_FIELDS:
            fp = os.path.join(tdir, f)
            if not os.path.exists(fp):
                fails.append("field %s absent at endTime" % f)
        if not os.path.exists(anchor):
            fails.append("age-guard anchor %s absent" % AGE_GUARD_ANCHOR)
        else:
            a = os.path.getmtime(anchor)
            for f in REQUIRED_FIELDS:
                fp = os.path.join(tdir, f)
                if os.path.exists(fp) and os.path.getmtime(fp) <= a:
                    fails.append("AGE GUARD: %s at endTime is not newer than %s"
                                 % (f, AGE_GUARD_ANCHOR))
    detail = {"ok": len(fails) == 0, "failures": fails,
              "age_guard_anchor": AGE_GUARD_ANCHOR,
              "endtime_graded_against": endtime}
    if declared_endtime is not None:
        detail["endtime_reconciliation"] = endtime_reconciliation(log, declared_endtime)
    return (len(fails) == 0), detail


# --------------------------------------------------------------------------
# ss3.2 ORDERING + ss2.3 GATES
# --------------------------------------------------------------------------
def band_verdict(value, band):
    lo, hi = band
    return "PASS" if (lo <= value <= hi) else "GATE FAIL"


def grade(final, samples, log, completion_ok, plant_detail, endtime_cap=ENDTIME_CAP):
    """ss3.2: PLATEAU IS EVALUATED FIRST AND ITS RESULT IS BINDING. A deviation
    inside the band on a run that is NOT plateaued is NOT A RESULT -- it is NOT a
    PASS. Per rule 5 the plateau clause can only turn a PASS or GATE FAIL INTO
    NOT A RESULT, never the reverse."""
    clauses = []
    ok_a, d_a = clause_p_a(log, endtime_cap); clauses.append(d_a)
    ok_b, d_b = clause_p_b(log);              clauses.append(d_b)
    ok_c, d_c = clause_p_c(samples);          clauses.append(d_c)
    ok_d, d_d = clause_p_d(samples);          clauses.append(d_d)
    plateaued = ok_a and ok_b and ok_c and ok_d

    x_s, x_r = final["separation"], final["reattachment"]
    dev_s = (x_s - P1_TARGET) / P1_TARGET
    dev_r = (x_r - P2_TARGET) / P2_TARGET
    p1 = band_verdict(x_s, P1_BAND)
    p2 = band_verdict(x_r, P2_BAND)
    band_only = "PASS" if (p1 == "PASS" and p2 == "PASS") else "GATE FAIL"

    if not completion_ok:
        verdict = "NOT A RESULT"
        reason = "ss9.4 completion (rule 4) failed. The comparator refuses rather than degrades."
    elif not plateaued:
        verdict = "NOT A RESULT"
        reason = ("ss3.2: plateau evaluated FIRST and BINDING. A deviation inside the "
                  "band on a non-plateaued run is NOT A RESULT, not a PASS.")
    else:
        verdict = band_only
        reason = "plateau HOLDS; verdict is the band verdict (ss2.3)."

    # rule 1 binds EVERY cell, not just the headline. A per-gate cell carrying a
    # synonym or a hedge is the same defect as a hedged row verdict -- and the lab
    # already has an open conflict on record about ledger cells reading bare FAIL.
    # The mutation control for rule 1 caught this: a hedging band_verdict reached
    # gates.*.verdict while the headline stayed legal.
    for name, v in (("row", verdict), ("P1", p1), ("P2", p2), ("band", band_only)):
        if v not in VERDICTS:
            refuse("%s verdict %r is outside rule 1's fixed vocabulary %s"
                   % (name, v, list(VERDICTS)))
    # rule 5's one-way door, enforced in code: the plateau clause may only turn a
    # PASS or GATE FAIL INTO NOT A RESULT, never the reverse.
    if not plateaued and verdict != "NOT A RESULT":
        refuse("one-way door violated: non-plateaued run graded %r" % verdict)
    if plateaued and completion_ok and verdict != band_only:
        refuse("one-way door violated: plateaued run not graded on its band")

    reported = {
        "LABEL": "REPORTED -- NOT A GATE",
        "separation_2pct_reading": {
            "band": list(REPORTED_SEP_2PCT_BAND),
            "inside": REPORTED_SEP_2PCT_BAND[0] <= x_s <= REPORTED_SEP_2PCT_BAND[1],
            "note": "ss2.3. It can NEVER turn a PASS into a GATE FAIL or the reverse."},
        "oilfilm_limb": {
            "target": REPORTED_OILFILM_LIMB, "band": list(REPORTED_OILFILM_BAND),
            "deviation_pct": (x_r - REPORTED_OILFILM_LIMB) / REPORTED_OILFILM_LIMB * 100.0,
            "band_verdict_if_gated": band_verdict(x_r, REPORTED_OILFILM_BAND),
            "note": "ss1.5.2 / ss2.1. The oil-film limb is REPORTED, NOT GATED. Printed "
                    "so the record cannot later be read as resting on the limb."},
    }
    return {
        "campaign": "F6a / C-15 -- NASA wall-mounted hump vs Greenblatt AIAA-2004-2220 Table 2",
        "preregistration": PREREG, "preregistration_sha256": PREREG_SHA256,
        "extractor": EXTRACTOR, "extractor_sha256": EXTRACTOR_SHA256,
        "extractor_blob": EXTRACTOR_BLOB,
        "VERDICT": verdict, "verdict_reason": reason,
        "plateaued": plateaued, "completion_ok": completion_ok,
        "gates": {
            "P1_separation": {"value": x_s, "target": P1_TARGET, "band": list(P1_BAND),
                              "deviation_pct": dev_s * 100.0, "verdict": p1},
            "P2_reattachment": {"value": x_r, "target": P2_TARGET, "band": list(P2_BAND),
                                "deviation_pct": dev_r * 100.0, "verdict": p2},
        },
        "plateau_clauses": clauses,
        "planted_zero_control": plant_detail,
        "reported_not_gated": reported,
        "crest_xc": final.get("crest_xc"),
        "grid_convergence": {
            "triple": None, "gci": None, "observed_order": None,
            "note": "ss4 registers NO Roache triple, NO GCI and NO observed order. The G "
                    "column for C-15 remains NO. The graded value comes from a SINGLE "
                    "MESH LEVEL; no grid-convergence evidence supports it; it is not "
                    "asymptotic and nothing here may be read as saying so."},
        "declared_deviations": [
            "DEVIATION 1 (ss7.1): Re_c 936,000 run vs Table 2's 929,000 (+0.75 %). "
            "NO BOUND IS ASSERTED -- none has been measured.",
            "DEVIATION 2 (ss7.2): single mesh level, no grid convergence.",
            "DEVIATION 3 (ss7.3): stock kOmegaSST, measured inert to 0.02 %.",
            "DEVIATION 4 (ss7.4): p_ref convention on the REPORTED Cp; cannot affect a verdict.",
        ],
    }


def sample_times(converged_at, available):
    """ss3.1 (P-c): every SAMPLE_STRIDE iterations over the final SAMPLE_WINDOW."""
    lo = converged_at - SAMPLE_WINDOW
    want = sorted(t for t in available
                  if lo < t <= converged_at and t % SAMPLE_STRIDE == 0)
    if len(want) < N_SAMPLES:
        refuse("(P-c) unevaluable: %d sample times in (%d, %d] on the %d-iteration "
               "grid, need %d. REFUSAL, not a pass."
               % (len(want), lo, converged_at, SAMPLE_STRIDE, N_SAMPLES))
    return want[-N_SAMPLES:]


def show_frozen():
    print("FROZEN CONSTANTS, for a line-by-line diff against %s" % PREREG)
    print("  ss2.2/2.3 P1 separation   target %.3f  band %s" % (P1_TARGET, list(P1_BAND)))
    print("  ss2.2/2.3 P2 reattachment target %.2f   band %s" % (P2_TARGET, list(P2_BAND)))
    print("  ss2.3     model-form tol  +/- %.0f %% (inherited verbatim from 74797a57)"
          % (MODEL_FORM_TOL * 100))
    print("  ss2.3     REPORTED-NOT-A-GATE separation 2 %% reading %s" % list(REPORTED_SEP_2PCT_BAND))
    print("  ss2.1     REPORTED-NOT-A-GATE oil-film limb %.2f band %s"
          % (REPORTED_OILFILM_LIMB, list(REPORTED_OILFILM_BAND)))
    print("  ss3.1 P-a residualControl tripped, converged_at < cap %d" % ENDTIME_CAP)
    print("  ss3.1 P-b INITIAL residuals %s" % RESIDUAL_CONTROLS)
    print("  ss3.1 P-c %d samples every %d iters over the final %d; ptp <= %s"
          % (N_SAMPLES, SAMPLE_STRIDE, SAMPLE_WINDOW, PTP_MAX))
    print("  ss3.1 P-d at most %d sign alternation across the samples" % MAX_SIGN_ALTERNATIONS)
    print("  ss3.2 plateau FIRST and BINDING; rule 5 one-way door enforced in code")
    print("  ss3.3 plant BY LINE INDEX, bands %s" % (PLANT_BANDS,))
    print("  ss9.3 extractor %s" % EXTRACTOR)
    print("        sha256 %s" % EXTRACTOR_SHA256)
    print("        blob   %s" % EXTRACTOR_BLOB)
    print("  ss9.4 fields %s; age guard anchored on %s" % (list(REQUIRED_FIELDS), AGE_GUARD_ANCHOR))
    print("  ss4   NO triple, NO GCI, NO observed order. G stays NO.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--case")
    ap.add_argument("--log")
    ap.add_argument("--endtime", type=int)
    ap.add_argument("--rc", type=int, default=None)
    ap.add_argument("--rc-file", default=None,
                    help="ADDENDUM 4: read the solver exit code FROM DISK. rule 4's "
                         "rc limb is MEASURED, never inferred -- the supervisor refused "
                         "an inferred rc on attempt 2 and the row became NOT A RESULT.")
    ap.add_argument("--declared-endtime", type=int, default=None,
                    help="controlDict endTime, for the ss9.4 reconciliation")
    ap.add_argument("--scratch")
    ap.add_argument("--out")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--show-frozen", action="store_true")
    a = ap.parse_args(argv)

    if a.show_frozen:
        show_frozen()
        return 0
    if not (a.case and a.log and a.endtime and a.scratch and a.out):
        ap.error("--case --log --endtime --scratch --out are required")

    try:
        assert_pinned(a.repo)
        if a.rc_file:
            if not os.path.exists(a.rc_file):
                sys.stderr.write("REFUSAL: --rc-file %s does not exist. rule 4's rc limb "
                                 "is MEASURED, not inferred.\n" % a.rc_file)
                with open(a.out, "w") as fh:
                    json.dump({"VERDICT": "NOT A RESULT",
                               "REFUSAL": "solver rc was never persisted; the limb is "
                                          "unmeasured and an unmeasured limb in a "
                                          "conjunctive rule is a degradation."}, fh, indent=2)
                return 2
            raw = open(a.rc_file).read().strip()
            try:
                a.rc = int(raw)
            except ValueError:
                refuse("--rc-file %s holds %r, not an integer exit code. REFUSING."
                       % (a.rc_file, raw))
        if a.rc is None:
            refuse("no exit code supplied: pass --rc-file (preferred, MEASURED) or --rc")
        log = parse_log(a.log)
        conv = log["converged_at"] if log["converged_at"] is not None else log["last_time"]
        completion_ok, comp = completion_check(a.case, log, a.endtime, a.rc,
                                               a.declared_endtime)
        plant = plant_and_reread(a.case, conv, a.scratch, a.repo)
        wv = os.path.join(a.case, "postProcessing", "wallValues")
        available = sorted(int(d) for d in os.listdir(wv) if d.isdigit()) if os.path.isdir(wv) else []
        if not available:
            refuse("no wall sample times under %s" % wv)
        samples = [extract_pair(a.case, t, a.repo) for t in sample_times(conv, available)]
        final = extract_pair(a.case, conv, a.repo)
        result = grade(final, samples, log, completion_ok, plant)
        result["completion"] = comp
    except Refusal as e:
        payload = {"VERDICT": "NOT A RESULT", "REFUSAL": str(e),
                   "note": "The comparator REFUSES (exit 2) rather than degrades."}
        sys.stderr.write("REFUSAL: %s\n" % e)
        with open(a.out, "w") as fh:
            json.dump(payload, fh, indent=2)
        return 2

    with open(a.out, "w") as fh:
        json.dump(result, fh, indent=2)
    print("VERDICT: %s" % result["VERDICT"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
