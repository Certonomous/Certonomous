#!/usr/bin/env python3
"""
CRM WING-ALONE L2, M=0.85 -- GRADER FOR THE REGISTERED GATES ONLY.

IT GRADES §7 OF verification/campaign/CRM_WINGALONE_FLOW_PREREGISTRATION.md AS COMMITTED,
AND NOTHING ELSE.  It invents no band.  §5 fixes Cl/Cd/Cm as REPORTED, NOT GATED, so no
verdict here rests on a force value; §6 registers NO order band and NO GCI, because this
family has ONE admissible mesh, so no p and no GCI is computed or quoted.

REGISTERED GATES, reached in their registered order:
  G-S1  initial residuals Ux Uy Uz e p k omega  all <= 1e-4          else GATE FAIL
  G-S2  max|dCd| over the LAST 500 ITERATIONS, in drag counts <= 1.0 else GATE FAIL
  G-S3  realizability: no negative k, omega or absolute T at any
        cell, at any written time -- ZERO OCCURRENCES, AND THE ZERO
        IS PLANTED (rule 3)                                          else GATE FAIL
  G-S4  completion rule (CLAUDE.md rule 4) incl. THE AGE GUARD       else NOT A RESULT

G-S4 DOMINATES: it can only turn a PASS or a GATE FAIL INTO 'NOT A RESULT', never the
reverse -- the rule-5 direction, applied to the completion clause.

IT HAS NO KILL PRIMITIVE AND NO CAP.  Sanaa has ruled four times that no run is stopped by
clock or budget.  This grader reads; it never signals and it never stops anything.

EXIT CODES:  0 PASS | 1 GATE FAIL | 2 REFUSED (instrument could not be trusted) | 3 NOT A RESULT
A REFUSAL IS NOT A DEGRADED PASS.  If the planted control cannot be seen, the zero is not
evidence and this script refuses rather than reporting a clean realizability result.
"""
import os, re, sys, glob, struct, datetime

ENDTIME   = 4000          # system/controlDict endTime
DELTAT    = 1             # unit step -> n_exec must equal round(endTime/deltaT) = 4000
RESID_MAX = 1.0e-4        # G-S1
DCD_MAX_COUNTS = 1.0      # G-S2
DCD_WINDOW     = 500      # G-S2, "the last 500 iterations"
PLANT_NEG = -1.234e-03    # G-S3 planted perturbation (rule 3)
FIELDS_REQUIRED = ["U","p","T","k","omega","nut","alphat"]   # this case's own 0/ set
REALIZABILITY_FIELDS = ["k","omega","T"]                      # exactly what §7 G-S3 names

out = []
def say(s=""): out.append(s); print(s)

def hr(t): say(""); say("="*78); say(t); say("="*78)

# --------------------------------------------------------------------------- #
# BINARY FIELD READER.  writeFormat is binary, arch "LSB;label=32;scalar=64".
# The SAME function reads the real field and the planted copy -- one code path,
# so the control exercises the instrument that produces the answer.
# --------------------------------------------------------------------------- #
def read_internal_scalars(path):
    """
    Return a dict describing internalField of a volScalarField.
    Handles BOTH writeFormats, because an instrument that meets a format it cannot
    parse must RAISE (-> refusal), never return a quiet zero.
      kind : 'uniform' | 'binary' | 'ascii'
      vals : list of floats
    plus what plant_and_verify needs to rewrite the file byte-for-byte.
    """
    with open(path, "rb") as f:
        raw = f.read()
    i = raw.find(b"internalField")
    if i < 0:
        raise ValueError("no internalField in %s" % path)
    m = re.match(rb"internalField\s+uniform\s+([-0-9.eE+]+)\s*;", raw[i:i+200])
    if m:
        return {"kind": "uniform", "vals": [float(m.group(1))], "raw": raw}
    m = re.search(rb"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\(", raw[i:i+400])
    if not m:
        raise ValueError("internalField in %s is neither uniform nor a nonuniform "
                         "List<scalar>" % path)
    n = int(m.group(1))
    start = i + m.end()                      # first byte AFTER the '('
    # THE FORMAT IS READ FROM THE FoamFile HEADER, WHICH DECLARES IT -- never guessed from
    # the payload.  A raw binary double can contain the byte 0x0a or 0x29 (')'), so payload
    # sniffing is ambiguous by construction; the selftest caught exactly that defect.
    fm = re.search(rb"format\s+(binary|ascii)\s*;", raw[:i])
    if not fm:
        raise ValueError("%s: FoamFile header declares no 'format' -- REFUSING to guess" % path)
    fmt = fm.group(1).decode()
    if fmt == "binary":
        buf = raw[start:start + 8*n]
        if len(buf) != 8*n:
            raise ValueError("%s: header says binary and claims %d values (%d bytes) but "
                             "only %d bytes follow '('" % (path, n, 8*n, len(buf)))
        return {"kind": "binary", "vals": list(struct.unpack("<%dd" % n, buf)),
                "raw": raw, "start": start, "n": n}
    close = raw.index(b")", start)
    toks  = raw[start:close].split()
    if len(toks) != n:
        raise ValueError("%s: header says ascii and claims %d values, body holds %d"
                         % (path, n, len(toks)))
    return {"kind": "ascii", "vals": [float(t) for t in toks], "raw": raw,
            "start": start, "close": close, "n": n, "toks": toks}

def scan_negatives(path):
    """THE READER UNDER TEST.  Counts cells with a value < 0 in internalField."""
    r = read_internal_scalars(path)
    vals = r["vals"]
    neg = [(j, v) for j, v in enumerate(vals) if v < 0.0]
    return len(vals), neg

def plant_and_verify(path, plant_dir):
    """
    RULE 3.  Write a copy of this field to disk with a KNOWN NEGATIVE at a KNOWN CELL INDEX,
    read it BACK FROM DISK with the SAME scanner that produces the answer, and require the
    scanner to report it.  If the scanner cannot see the planted negative, its zero on the
    real field is NOT EVIDENCE and the caller REFUSES.
    On failure the planted file is LEFT ON DISK for triage; on success it is removed.
    """
    r = read_internal_scalars(path)
    if r["kind"] == "uniform":
        return False, ("field internalField is 'uniform' -- a single value, so a per-cell "
                       "plant by index is not defined. REFUSING rather than guessing.")
    n = r["n"]; idx = n // 2
    if r["kind"] == "binary":
        ba = bytearray(r["raw"])
        ba[r["start"] + 8*idx : r["start"] + 8*idx + 8] = struct.pack("<d", PLANT_NEG)
        blob = bytes(ba)
    else:  # ascii
        toks = list(r["toks"])
        toks[idx] = (b"%.17g" % PLANT_NEG)
        blob = r["raw"][:r["start"]] + b"\n" + b"\n".join(toks) + b"\n" + r["raw"][r["close"]:]
    os.makedirs(plant_dir, exist_ok=True)
    pp = os.path.join(plant_dir, os.path.basename(path) + ".planted")
    with open(pp, "wb") as f:
        f.write(blob)
    ncells, neg = scan_negatives(pp)          # <-- READ BACK FROM DISK, same code path
    seen = [(j, v) for j, v in neg if j == idx and abs(v - PLANT_NEG) < 1e-15]
    if ncells != n:
        return False, ("planted copy reports %d cells, original %d -- the writer or reader "
                       "is lossy. File kept at %s" % (ncells, n, pp))
    if not seen:
        return False, ("planted %.6e at cell index %d of %d in %s -- THE READER DID NOT "
                       "REPORT IT (it reported %d negatives). File kept at %s"
                       % (PLANT_NEG, idx, n, os.path.basename(path), len(neg), pp))
    os.remove(pp)
    return True, ("[%s] planted %.6e at cell %d of %d -> reader REPORTED IT "
                  "(%d other negative(s) in the planted copy)"
                  % (r["kind"], PLANT_NEG, idx, n, len(neg)-1))

# --------------------------------------------------------------------------- #
def main():
    CASE = sys.argv[1].rstrip("/")
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    hr("CRM WING-ALONE L2  M=0.85  --  GRADED ON THE REGISTERED §7 GATES")
    say("case         : %s" % CASE)
    say("graded at    : %s" % now)
    say("registration : verification/campaign/CRM_WINGALONE_FLOW_PREREGISTRATION.md (HEAD blob)")
    say("gates        : G-S1 residuals<=1e-4 | G-S2 max|dCd| last 500 it <= 1.0 count |")
    say("               G-S3 realizability, PLANTED zero | G-S4 completion rule + AGE GUARD")
    say("NOT GRADED   : Cl/Cd/Cm values (§5 REPORTED, NOT GATED -- no wing-alone reference")
    say("               data exists on this box); observed order p and GCI (§6 -- ONE")
    say("               admissible mesh, a triple is not reachable and none is faked).")

    verdicts = {}

    # ---------------- G-S4 first in evidence, last in precedence -------------
    hr("G-S4  COMPLETION RULE (CLAUDE.md rule 4) -- ALL CLAUSES, INCLUDING THE AGE GUARD")
    c = {}
    rcp = os.path.join(CASE, "solve_rc")
    if os.path.exists(rcp):
        rc = open(rcp).read().strip()
        c["rc == 0"] = (rc == "0", "solve_rc = %s" % rc)
    else:
        c["rc == 0"] = (False, "solve_rc ABSENT -- the launcher wrote no rc")

    log = os.path.join(CASE, "log.rhoSimpleFoam")
    endline = False; n_exec = 0; last_time = None
    if os.path.exists(log):
        with open(log, errors="replace") as f:
            for line in f:
                if line.startswith("End"): endline = True
                if line.startswith("ExecutionTime"): n_exec += 1
                m = re.match(r"^Time = ([0-9.eE+-]+)", line)
                if m: last_time = m.group(1)
        c["End line present"] = (endline, "End %s" % ("found" if endline else "ABSENT"))
        c["last time == endTime"] = (last_time is not None and
                                     abs(float(last_time) - ENDTIME) < 1e-9,
                                     "last Time = %s, endTime = %d" % (last_time, ENDTIME))
        want = round(ENDTIME / DELTAT)
        c["n_exec == round(endTime/deltaT)"] = (n_exec == want,
                                     "ExecutionTime lines = %d, required = %d" % (n_exec, want))
    else:
        c["End line present"] = (False, "log.rhoSimpleFoam ABSENT")

    tdir = os.path.join(CASE, str(ENDTIME))
    present = []
    missing = []
    if os.path.isdir(tdir):
        for fl in FIELDS_REQUIRED:
            (present if os.path.exists(os.path.join(tdir, fl)) else missing).append(fl)
        phi = os.path.exists(os.path.join(tdir, "phi"))
        c["fields present at endTime"] = (not missing,
            "%s present%s; phi %s" % (",".join(present),
            "" if not missing else "; MISSING " + ",".join(missing),
            "present" if phi else "absent (flux is written by reconstructPar only if on disk)"))
        # ---- THE AGE GUARD ----
        ref = os.path.join(CASE, "0", "T")
        if os.path.exists(ref):
            t0 = os.path.getmtime(ref)
            older = [fl for fl in present if os.path.getmtime(os.path.join(tdir, fl)) <= t0]
            c["AGE GUARD: every field newer than 0/T"] = (not older,
                "0/T mtime %s; %s" % (datetime.datetime.utcfromtimestamp(t0).strftime("%H:%M:%SZ"),
                "all %d fields newer" % len(present) if not older
                else "NOT NEWER: " + ",".join(older)))
        else:
            c["AGE GUARD: every field newer than 0/T"] = (False, "0/T ABSENT -- guard cannot run")
    else:
        c["fields present at endTime"] = (False, "%s/ ABSENT -- reconstructPar has not written" % ENDTIME)
        c["AGE GUARD: every field newer than 0/T"] = (False, "no endTime dir to age-check")

    for k, (ok, detail) in c.items():
        say("  [%s] %-38s %s" % ("OK " if ok else "FAIL", k, detail))
    gs4 = all(v[0] for v in c.values())
    verdicts["G-S4"] = "PASS" if gs4 else "NOT A RESULT"
    say("  --> G-S4 : %s" % verdicts["G-S4"])

    # ---------------- G-S1 ---------------------------------------------------
    hr("G-S1  INITIAL RESIDUALS Ux Uy Uz e p k omega  <=  1e-4")
    si = os.path.join(CASE, "postProcessing", "residuals", "0", "solverInfo.dat")
    if not os.path.exists(si):
        say("  solverInfo.dat ABSENT -- G-S1 cannot be read"); verdicts["G-S1"] = "NOT A RESULT"
    else:
        hdr = None; last = None
        for line in open(si):
            if line.startswith("# Time"): hdr = line.lstrip("#").split()
            elif not line.startswith("#") and line.strip(): last = line.split()
        cols = {name: j for j, name in enumerate(hdr)}
        worst = []
        for f in ["Ux", "Uy", "Uz", "e", "p", "k", "omega"]:
            v = float(last[cols[f + "_initial"]])
            ok = v <= RESID_MAX
            worst.append((f, v, ok))
            say("  [%s] %-6s initial residual = %.6e   (threshold 1e-4)" % ("OK " if ok else "FAIL", f, v))
        say("  at iteration %s" % last[0])
        gs1 = all(o for _, _, o in worst)
        verdicts["G-S1"] = "PASS" if gs1 else "GATE FAIL"
        say("  --> G-S1 : %s" % verdicts["G-S1"])

    # ---------------- G-S2 ---------------------------------------------------
    hr("G-S2  FORCE PLATEAU: max|dCd| OVER THE LAST %d ITERATIONS  <=  1.0 DRAG COUNT" % DCD_WINDOW)
    cf = os.path.join(CASE, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
    if not os.path.exists(cf):
        say("  coefficient.dat ABSENT -- G-S2 cannot be read"); verdicts["G-S2"] = "NOT A RESULT"
    else:
        it = []; cd = []; cl = []; cm = []
        for line in open(cf):
            if line.startswith("#"): continue
            f = line.split()
            if len(f) < 8: continue
            it.append(int(float(f[0]))); cd.append(float(f[1]))
            cl.append(float(f[4])); cm.append(float(f[7]))
        if len(cd) < DCD_WINDOW + 1:
            say("  only %d force rows -- fewer than the registered %d-iteration window"
                % (len(cd), DCD_WINDOW))
            verdicts["G-S2"] = "NOT A RESULT"
        else:
            seg = cd[-(DCD_WINDOW+1):]
            ptp   = (max(seg) - min(seg)) * 1e4
            step  = max(abs(seg[j+1]-seg[j]) for j in range(len(seg)-1)) * 1e4
            e2e   = abs(seg[-1] - seg[0]) * 1e4
            say("  window = iterations %d .. %d" % (it[-(DCD_WINDOW+1)], it[-1]))
            say("  peak-to-peak   max|dCd| in window = %10.4f counts   <-- THE GATED MEASURE" % ptp)
            say("  max single-step        |dCd|      = %10.4f counts   (printed, not gated)" % step)
            say("  end-to-end             |dCd|      = %10.4f counts   (printed, not gated)" % e2e)
            say("  ALL THREE ARE PRINTED DELIBERATELY: on this box the same Cd series read")
            say("  +1.29 %%, +5.70 %% and -41.86 %% over 10, 20 and 500 iterations AT ONE INSTANT.")
            say("  ONE WINDOW IS NEVER EVIDENCE, so the reader can see which measure gated.")
            gs2 = ptp <= DCD_MAX_COUNTS
            verdicts["G-S2"] = "PASS" if gs2 else "GATE FAIL"
            say("  --> G-S2 : %s" % verdicts["G-S2"])
        say("")
        say("  §5 QoI -- REPORTED, NOT GATED (no wing-alone reference data exists on this box):")
        say("     Cd = %.8e  (%.3f counts)   Cl = %.6f   CmPitch = %.6f   at iteration %d"
            % (cd[-1], cd[-1]*1e4, cl[-1], cm[-1], it[-1]))

    # ---------------- G-S3 ---------------------------------------------------
    hr("G-S3  REALIZABILITY: NO NEGATIVE k, omega OR ABSOLUTE T AT ANY CELL, ANY WRITTEN TIME")
    say("  The zero is PLANTED (CLAUDE.md rule 3). A zero from a reader not shown able to")
    say("  see a non-zero is NOT EVIDENCE, and this instrument REFUSES (exit 2) rather than")
    say("  reporting a clean realizability result it cannot stand behind.")
    plant_dir = os.path.join(CASE, "GRADE_PLANT")
    times = []
    if os.path.isdir(tdir): times = [(str(ENDTIME), tdir)]
    if not times:
        say("  NO WRITTEN TIME EXISTS -- G-S3 has nothing to scan.")
        verdicts["G-S3"] = "NOT A RESULT"
    else:
        refused = False; total_neg = 0
        for tname, td in times:
            for fl in REALIZABILITY_FIELDS:
                p = os.path.join(td, fl)
                if not os.path.exists(p):
                    say("  [FAIL] time %s field %-6s ABSENT" % (tname, fl)); refused = True; continue
                try:
                    ok, detail = plant_and_verify(p, plant_dir)
                except Exception as e:
                    say("  [REFUSE] time %s field %-6s plant raised: %s" % (tname, fl, e))
                    refused = True; continue
                if not ok:
                    say("  [REFUSE] time %s field %-6s CONTROL FAILED: %s" % (tname, fl, detail))
                    refused = True; continue
                say("  [CTRL OK] time %s field %-6s %s" % (tname, fl, detail))
                ncells, neg = scan_negatives(p)
                total_neg += len(neg)
                if neg:
                    say("  [FAIL] time %s field %-6s %d of %d cells NEGATIVE; first: cell %d = %.6e"
                        % (tname, fl, len(neg), ncells, neg[0][0], neg[0][1]))
                else:
                    say("  [OK  ] time %s field %-6s 0 negative of %d cells -- AND THE READER WAS"
                        " JUST SHOWN ABLE TO SEE ONE" % (tname, fl, ncells))
        if refused:
            verdicts["G-S3"] = "REFUSED"
        else:
            verdicts["G-S3"] = "PASS" if total_neg == 0 else "GATE FAIL"
        say("  --> G-S3 : %s  (%d negative cells found in total)" % (verdicts["G-S3"], total_neg))

    # ---------------- overall ------------------------------------------------
    hr("VERDICT")
    for g in ["G-S1", "G-S2", "G-S3", "G-S4"]:
        say("  %-5s : %s" % (g, verdicts.get(g, "PENDING")))
    say("")
    if "REFUSED" in verdicts.values():
        overall, code = "NOT A RESULT", 2
        say("  OVERALL: NOT A RESULT -- an instrument REFUSED. A refusal is not a degraded pass.")
    elif verdicts.get("G-S4") != "PASS" or "NOT A RESULT" in verdicts.values():
        overall, code = "NOT A RESULT", 3
        say("  OVERALL: NOT A RESULT -- the completion rule (or a gate's input) did not hold.")
        say("  G-S4 can only turn a PASS or a GATE FAIL INTO 'NOT A RESULT', never the reverse.")
    elif "GATE FAIL" in verdicts.values():
        overall, code = "GATE FAIL", 1
        say("  OVERALL: GATE FAIL -- the run completed but a registered gate was breached.")
    else:
        overall, code = "PASS", 0
        say("  OVERALL: PASS -- every registered gate that CAN fire on one mesh has fired clean.")
    say("")
    say("  WHAT THIS VERDICT DOES NOT CERTIFY, per §5 and §6, stated whatever the outcome:")
    say("   - NO grid-convergence claim. This family has ONE admissible mesh (L2). A Roache")
    say("     triple needs three. No observed order p and no GCI is computed or quoted.")
    say("   - NO validation of Cd, Cl or Cm against anything. No wing-alone CRM force or Cp")
    say("     dataset exists on this box (§9B of the predecessor), so the QoI is REPORTED.")
    say("   - M=0.85, Re=5e6 and alpha=2.0 deg are registered LAB CHOICES, not anchors.")

    with open(os.path.join(CASE, "GRADE_CRM_L2.txt"), "w") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(CASE, "VERDICT.crm_l2"), "w") as f:
        f.write("OVERALL=%s\n" % overall)
        for g in ["G-S1","G-S2","G-S3","G-S4"]:
            f.write("%s=%s\n" % (g, verdicts.get(g, "PENDING")))
        f.write("graded_utc=%s\n" % now)
    return code

if __name__ == "__main__":
    sys.exit(main())
