"""Build 0/wallShearStressData for the NASA hump from the NASA experimental Cf.

Reference = experimental Cf where the experiment has data (x/c in [-0.07, 1.57]);
= our own uncorrected SST baseline elsewhere (the far-upstream attached region the
experiment does not cover, where SST is already validated). The second choice is a
documented anchor, not a measurement: it makes those faces contribute ~0 to the
loss at beta=1 so the inversion is not driven by unmeasured stations.

Sign convention checked against F6a deviation #4 and DAFunctionVariance.C's own
shearB = (-Sf/magSf) & devRhoReff : Cf = -shear_x / (0.5 Uinf^2).
"""
import re, numpy as np, json, sys

CASE_SRC = "/home/ubuntu/Certonomous/demo-output/website/dafoam/f6a_nasa_hump/case"
EXP = "/home/ubuntu/Certonomous/demo-output/website/dafoam/f6a_nasa_hump/nasa_experimental_reference/noflow_cf.exp.dat"
OUT = "/home/ubuntu/certonomous-runs/S1-fiml/hump/0/wallShearStressData"
C, UINF = 0.42, 34.6244
Q = 0.5 * UINF**2

def patch_list(path, patch, ncomp):
    s = open(path).read()
    i = s.index("boundaryField"); j = s.index("\n    " + patch + "\n", i)
    m = re.search(r"nonuniform\s+List<(scalar|vector)>\s*\n?\s*(\d+)\s*\(", s[j:])
    n = int(m.group(2)); st = j + m.end()
    depth, k = 1, st
    while depth:
        if s[k] == "(": depth += 1
        elif s[k] == ")": depth -= 1
        k += 1
    toks = s[st:k-1].replace("(", " ").replace(")", " ").split()
    a = np.array([float(t) for t in toks])
    return a.reshape(n, ncomp) if ncomp > 1 else a

x = patch_list(CASE_SRC + "/0/Cx", "bottom", 1)
wss = patch_list(CASE_SRC + "/1772/wallShearStress", "bottom", 3)
xc = x / C
assert len(x) == len(wss) == 622, (len(x), len(wss))

rows = []
for L in open(EXP):
    t = L.split()
    if len(t) >= 2:
        try: rows.append([float(t[0]), float(t[1])])
        except ValueError: pass
e = np.array(rows); e = e[np.argsort(e[:, 0])]
lo, hi = e[:, 0].min(), e[:, 0].max()

cf_base = -wss[:, 0] / Q
cf_ref = cf_base.copy()
inb = (xc >= lo) & (xc <= hi)
cf_ref[inb] = np.interp(xc[inb], e[:, 0], e[:, 1])
tau_ref = -cf_ref * Q

print("bottom faces: %d   in experimental window: %d (%.1f%%)" % (len(x), inb.sum(), 100*inb.mean()))
print("exp x/c window: %.4f .. %.4f" % (lo, hi))
print("baseline Cf range: %.5f .. %.5f" % (cf_base.min(), cf_base.max()))
print("reference Cf range: %.5f .. %.5f" % (cf_ref.min(), cf_ref.max()))
print("initial per-face mean sq residual (in-window): %.6e"
      % np.mean((wss[inb,0] - tau_ref[inb])**2))

hdr = """FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      wallShearStressData;
}
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    inlet   { type calculated; value uniform (0 0 0); }
    outlet  { type calculated; value uniform (0 0 0); }
    top     { type symmetry; }
    sides   { type symmetry; }
    bottom
    {
        type            calculated;
        value           nonuniform List<vector>
%d
(
%s
)
;
    }
}
""" % (len(x), "\n".join("(%.12g 0 0)" % v for v in tau_ref))
open(OUT, "w").write(hdr)
np.save("/home/ubuntu/certonomous-runs/S1-fiml/hump_ref.npy",
        np.column_stack([xc, cf_base, cf_ref, inb.astype(float)]))
print("wrote", OUT)
