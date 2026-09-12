# DRIVER ONLY. Imports the FROZEN a3gc_grade.py (md5 73dbe368934956700da87e5a1f44ea0c)
# and calls its per-level limbs unchanged. Invents NO threshold: every constant used
# below comes out of the frozen module or out of A3GC_ANCHOR_RERUN_PREREGISTRATION.md Sec.4.
import sys, os, json, hashlib
GD = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3GC"
h = hashlib.md5(open(os.path.join(GD, "a3gc_grade.py"), "rb").read()).hexdigest()
if h != "73dbe368934956700da87e5a1f44ea0c":
    print("REFUSE: comparator md5 %s != frozen 73dbe368934956700da87e5a1f44ea0c" % h); sys.exit(2)
print("comparator md5 OK: %s" % h)
sys.path.insert(0, GD)
import a3gc_grade as G
G.guard_no_asserts()
print("guard_no_asserts OK (L-332)")

AR1 = "/home/ubuntu/certonomous-runs/A3GC-AR1"
log = G.read_log(os.path.join(AR1, "primal.log"))
log["printInterval"] = 100   # read back below, not assumed
import re
m = re.search(r'"printInterval"\s*:\s*([0-9]+)', open(os.path.join(AR1, "runScript_a3gc.py")).read())
log["printInterval"] = int(m.group(1))
print("printInterval read back from the case's own runScript = %d" % log["printInterval"])

report = {}
complete = G.gate_g_complete(AR1, log, "AR1", report)
floor = G.gate_g_tol(log, report)
res_ok = G.gate_g_res(log, floor, report)

# --- Sec.4 BAND. The frozen comparator defines ANCHOR_CD/ANCHOR_CL (lines 254-255)
#     but implements NO band limb -- its band gates are the TRIPLE's GCI bands.
#     The +-2 % band is registered in A3GC_ANCHOR_RERUN_PREREGISTRATION.md Sec.4,
#     frozen at 3d416043b, and is applied here verbatim. Nothing is widened.
BAND = 0.02
print("\n--- Sec.4 BAND  (AR1 PREREG Sec.4, frozen 3d416043b; +/- 2 %%) ---")
band = {}
for name, hist, anchor in (("CD", log["CD"], G.ANCHOR_CD), ("CL", log["CL"], G.ANCHOR_CL)):
    v = hist[-1]
    lo, hi = anchor * (1 - BAND), anchor * (1 + BAND)
    inside = lo <= v <= hi
    print("  %s = %.10g   anchor %.10g   band [%.10g, %.10g]   dev %+.4f %%   %s"
          % (name, v, anchor, lo, hi, 100 * (v - anchor) / anchor, "PASS" if inside else "GATE FAIL"))
    band[name] = {"value": v, "anchor": anchor, "lo": lo, "hi": hi, "inside": inside,
                  "dev_pct": 100 * (v - anchor) / anchor}

print("\n--- Sec.4 REPORTED, NOT GATED ---")
print("  p initRes at endTime = %.6e   (prediction ~3.74e-07)" % log["last_initRes"]["p"])
print("  yPlus / samples: %d CD samples, %d CL samples" % (len(log["CD"]), len(log["CL"])))

toks = []
toks.append(("G-COMPLETE", "PASS" if complete else "NOT A RESULT"))
toks.append(("G-RES Sec.5 gate 2", "PASS" if res_ok else "NOT A RESULT"))
for k in ("CD", "CL"):
    toks.append(("Sec.5 gate 3 band %s" % k, "PASS" if band[k]["inside"] else "GATE FAIL"))
print("\n--- COMPOSITION (frozen compose_verdicts, module ordering) ---")
for lab, t in toks:
    G.emit_verdict(lab, t)
overall = G.compose_verdicts(dict(toks))
print("\nA3GC-AR1 OVERALL: %s" % overall)
json.dump({"limbs": dict(toks), "band": band, "overall": overall, "report": report},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "a3gc_ar1_grade.json"), "w"),
          indent=1, default=str)
