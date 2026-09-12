#!/usr/bin/env python3
"""Set OpenFOAM patch TYPES on a converted committee mesh.

gmshToFoam writes every physical surface as a generic `patch`. The wall patches must become
`wall` (otherwise wall functions, y+ and wall-distance are all wrong and the forces
functionObject has no wall to integrate), and the symmetry plane must become `symmetry`.

`symmetry` is used deliberately in preference to `symmetryPlane`: the Boeing Babcock symmetry
plane is planar only to 4.621e-06 in, and `symmetryPlane` demands coplanarity. This lab has
already lost 832 root-plane faces once to a tolerance tighter than the measured planarity.
"""
import sys, re, os
TYPES = {"wing": "wall", "body": "wall", "symmetry": "symmetry", "farfield": "patch"}

def main(path):
    s = open(path).read()
    out, changed = s, []
    for name, t in TYPES.items():
        pat = re.compile(r"(\b" + name + r"\s*\{[^}]*?\btype\s+)(\w+)(;)", re.S)
        m = pat.search(out)
        if not m:
            print(f"  {name}: NOT FOUND"); continue
        if m.group(2) != t:
            out = pat.sub(lambda mm: mm.group(1) + t + mm.group(3), out, count=1)
            changed.append(f"{name}: {m.group(2)} -> {t}")
        else:
            changed.append(f"{name}: already {t}")
    # a wall patch must also carry inGroups so wall-distance and y+ find it
    out = re.sub(r"(\b(?:wing|body)\s*\{\s*\n\s*type\s+wall;)",
                 r"\1\n        inGroups        1(wall);", out)
    open(path, "w").write(out)
    for c in changed: print("  " + c)
    if "defaultFaces" in out:
        print("  *** defaultFaces PRESENT -- the level is REFUSED (registered acceptance test)")
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
