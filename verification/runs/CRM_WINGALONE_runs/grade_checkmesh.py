#!/usr/bin/env python3
"""G-M1/G-M2/G-M3 grader. Reads checkMesh's PRINTED VERDICT LINES, never its rc.
Thresholds are quoted from the frozen registration §10 and are not arguments."""
import sys, re
G_M1 = 70.0     # max non-orthogonality, hard gate; warning band 65-70
G_M2 = 4.0      # max skewness, BOUNDARY FACES INCLUDED
G_M3 = 1000.0   # aspect ratio — ADVISORY, NEVER a lone rejection
log = sys.argv[1]
txt = open(log, errors="replace").read()
lines = txt.splitlines()

# --- reader control: the reader is shown able to see a BREACHING value before
# --- any non-breaching verdict below is treated as evidence (rule 3 in spirit).
ctrl = "Mesh non-orthogonality Max: 88.8888 average: 12.0"
m = re.search(r"non-orthogonality Max:\s*([0-9.eE+-]+)", ctrl)
assert m and float(m.group(1)) > G_M1, "control failed: reader cannot see a breach"
print("READER CONTROL: planted line 'Max: 88.8888' parses as %.4f > gate %.1f -> "
      "the reader CAN see a breach. Verdicts below are therefore evidence." % (float(m.group(1)), G_M1))

def find(pat, cast=float):
    m = re.search(pat, txt)
    return cast(m.group(1)) if m else None

print("LOG %s" % log)
# dimensionality: match 'geometric' SPECIFICALLY. The 'solution (non-empty)
# directions' line four lines away reads 3 FOR A WEDGE and is NOT this.
geo = None; sol = None
for ln in lines:
    if "geometric" in ln and "directions" in ln:
        geo = ln.strip()
    if "solution" in ln and "directions" in ln:
        sol = ln.strip()
print("DIMENSIONALITY(geometric, the one that matters) : %s" % geo)
print("  [not graded, printed so it is not confused]   : %s" % sol)

cells = find(r"cells:\s+(\d+)", int)
points = find(r"points:\s+(\d+)", int)
faces = find(r"\n\s+faces:\s+(\d+)", int)
nonorth = find(r"non-orthogonality Max:\s*([0-9.eE+-]+)")
nonorth_av = find(r"non-orthogonality Max:.*?average:\s*([0-9.eE+-]+)")
skew = find(r"skewness.*?max skewness = ([0-9.eE+-]+)")
if skew is None:
    skew = find(r"Max skewness = ([0-9.eE+-]+)")
ar = find(r"aspect ratio.*?Max aspect ratio = ([0-9.eE+-]+)")
if ar is None:
    ar = find(r"Max aspect ratio = ([0-9.eE+-]+)")
print("CELLS %s  POINTS %s  FACES %s" % (cells, points, faces))

# the two verdict lines checkMesh prints for the whole mesh
for ln in lines:
    s = ln.strip()
    if s.startswith("Mesh OK") or s.startswith("Failed") or "***" in s:
        print("VERDICT_LINE: %s" % s)

def verdict(name, val, gate, advisory=False, warn=None):
    if val is None:
        print("%s : REFUSE — value not printed in the log; not graded on an absence." % name)
        return "REFUSE"
    if advisory:
        print("%s : %.6g  (ADVISORY threshold %.6g) -> %s — REPORTED, NEVER A LONE REJECTION"
              % (name, val, gate, "above advisory" if val > gate else "below advisory"))
        return "ADVISORY"
    ok = val <= gate
    extra = ""
    if warn is not None and ok and val >= warn:
        extra = "  [IN WARNING BAND %.0f-%.0f]" % (warn, gate)
    print("%s : %.6g  (gate <= %.6g) -> %s%s" % (name, val, gate, "PASS" if ok else "GATE FAIL", extra))
    return "PASS" if ok else "GATE FAIL"

v1 = verdict("G-M1 max non-orthogonality (deg)", nonorth, G_M1, warn=65.0)
if nonorth_av is not None:
    print("     (average non-orthogonality %.6g — reported, not gated)" % nonorth_av)
v2 = verdict("G-M2 max skewness (boundary faces incl.)", skew, G_M2)
v3 = verdict("G-M3 max aspect ratio", ar, G_M3, advisory=True)
print("SUMMARY G-M1=%s G-M2=%s G-M3=%s" % (v1, v2, v3))
sys.exit(0 if (v1 == "PASS" and v2 == "PASS") else 1)
