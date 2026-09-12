#!/usr/bin/env python3
"""ARM P1C -- WRITE the three patches into a FRESH solve case.  Authorised by ADDENDUM 2
A2.5 (committed 122398334, 2026-09-12T03:23:42Z), which also records that no arm had ever
performed this write: the mesh carries exactly one `defaultFaces` patch.

IT NEVER TOUCHES L2/foam.  The source mesh is COPIED and every polyMesh file is sha256-pinned
BOTH SIDES, so the case that solves is provably the mesh that was graded.

The split comes from the SAME classifier object P1C graded with -- imported, not re-implemented.
"""
import sys, os, re, shutil, hashlib, json
P1B = "/home/ubuntu/Certonomous/verification/runs/CRM_WINGALONE_runs/P1B"
P1C = "/home/ubuntu/Certonomous/verification/runs/CRM_WINGALONE_runs/P1C"
sys.path.insert(0, P1B); sys.path.insert(0, P1C)
import split_patches_p1b as M
import split_patches_p1c as C

SRC = "/home/ubuntu/Certonomous/verification/runs/CRM_WINGALONE_runs/L2/foam"
DST = sys.argv[1]
MESH_UNIT_M = 6.976368          # §3: 1 mesh-unit = 6.976368 m.  ASSERTED, never assumed.

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

if os.path.exists(os.path.join(DST, "constant", "polyMesh", "boundary")):
    sys.stderr.write("REFUSED: %s already carries a polyMesh. Never overwrite a case.\n" % DST); sys.exit(2)
os.makedirs(os.path.join(DST, "constant"), exist_ok=True)
os.makedirs(os.path.join(DST, "system"), exist_ok=True)
shutil.copytree(os.path.join(SRC, "constant", "polyMesh"), os.path.join(DST, "constant", "polyMesh"))

pins = {}
for f in ("points", "faces", "owner", "neighbour", "boundary"):
    a = sha(os.path.join(SRC, "constant", "polyMesh", f))
    b = sha(os.path.join(DST, "constant", "polyMesh", f))
    if a != b:
        sys.stderr.write("REFUSED: sha256 mismatch on %s after copy.\n" % f); sys.exit(2)
    pins[f] = a
print("polyMesh copied, all 5 files sha256-identical both sides.")

pm = os.path.join(DST, "constant", "polyMesh")
faces, coords, nb, start = C.load(pm)

groups = {"wing": [], "farfield": [], "symmetry": []}
for k, pl in enumerate(faces):
    name, r = M.classify(pl, coords)
    groups[name].append(start + k)          # GLOBAL face index
exp = {"wing": 11136, "farfield": 11136, "symmetry": 14144}
for k, v in exp.items():
    if len(groups[k]) != v:
        sys.stderr.write("REFUSED: %s %d != registered %d\n" % (k, len(groups[k]), v)); sys.exit(2)
print("counts re-confirmed at write time: wing %d  farfield %d  symmetry %d" %
      (len(groups["wing"]), len(groups["farfield"]), len(groups["symmetry"])))

# ---- assert the unit system BEFORE any reference quantity is used (§3, predecessor §8 r5).
# OVER WING FACES ONLY: the farfield reaches y = 85.1 mesh-units, so a max over the whole
# boundary is not the tip and an assertion built on it is measuring the outer box.
wing_ids = set(groups["wing"])
tip_mu = max(coords[i][1] for k, pl in enumerate(faces) if (start + k) in wing_ids for i in pl)
print("UNIT ASSERTION: wing tip y = %.10f mesh-units = %.6f m at 1 mu = %.6f m"
      % (tip_mu, tip_mu * MESH_UNIT_M, MESH_UNIT_M))
if not (3.70 < tip_mu < 3.80):
    sys.stderr.write("REFUSED: wing tip y %.6f outside the registered 3.7666681523.\n" % tip_mu); sys.exit(2)
print("           matches the registered tip 3.7666681523 -> mesh is in mesh-units as declared.")

HDR = """FoamFile
{
    version     2.0;
    format      ascii;
    class       faceSet;
    location    "constant/polyMesh/sets";
    object      %s;
}
"""
sd = os.path.join(pm, "sets"); os.makedirs(sd, exist_ok=True)
for name, ids in groups.items():
    with open(os.path.join(sd, name), "w") as f:
        f.write(HDR % name); f.write("\n%d\n(\n" % len(ids))
        for i in ids: f.write("%d\n" % i)
        f.write(")\n")
    print("wrote faceSet %-9s %d faces" % (name, len(ids)))

with open(os.path.join(DST, "system", "createPatchDict"), "w") as f:
    f.write("""FoamFile { version 2.0; format ascii; class dictionary; object createPatchDict; }
pointSync false;
patches
(
    { name wing;     patchInfo { type wall; }          constructFrom set; set wing; }
    { name farfield; patchInfo { type patch; }         constructFrom set; set farfield; }
    { name symmetry; patchInfo { type symmetryPlane; } constructFrom set; set symmetry; }
);
""")
json.dump({"source": SRC, "sha256_polyMesh_at_copy": pins,
           "counts": {k: len(v) for k, v in groups.items()},
           "mesh_unit_m": MESH_UNIT_M, "tip_y_mesh_units": tip_mu,
           "authorised_by": "ADDENDUM 2 A2.5, commit 122398334"},
          open(os.path.join(DST, "PATCH_WRITE_MANIFEST.json"), "w"), indent=2)
print("createPatchDict + manifest written.  Now run createPatch -overwrite.")
