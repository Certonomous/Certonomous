#!/usr/bin/env python3
"""
T9a-D mesh verification: the FROZEN check_t9a_mesh.check_wall(), imported
unmodified and driven over the D_* cases.

Zero solver compute (postProcess -func writeCellCentres only, and it deletes
what it writes).  For the H-C cases the registered layer-2 conductivity is
overridden IN MEMORY so that the frozen per-cell DT check grades the 0.4 W/mK
map it is supposed to; the file on disk is never written.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_t9a_mesh as CM        # frozen, imported, never edited

DREG = json.load(open(os.path.join(HERE, "T9aD_registered.json")))

def main():
    allok = True
    counts = {}
    for name, c in DREG["cases"].items():
        saved = CM.REG["wall"]["layers"][1]["k"]
        try:
            CM.REG["wall"]["layers"][1]["k"] = c["k2"]
            ok, n = CM.check_wall(name, dict(c, kind="wall"))
        finally:
            CM.REG["wall"]["layers"][1]["k"] = saved
        counts[name] = n
        allok &= ok
    print("\nrefinement ratios read from the meshes (nominal 1.6):")
    for a, b in (("D_A_c", "D_A_m"), ("D_A_m", "D_A_f"),
                 ("D_R_f", "D_B_x"), ("D_C_c", "D_C_m"), ("D_C_m", "D_C_f")):
        print(f"  {a}->{b}: " + ", ".join(
            f"{y/x:.3f}" for x, y in zip(counts[a], counts[b])))
    print(f"  frozen REG layer-2 k after all overrides: "
          f"{CM.REG['wall']['layers'][1]['k']} (must be 0.04)")
    print("\nALL D_* MESHES VERIFIED" if allok else "\nMESH VERIFICATION FAILED")
    return 0 if allok else 1

if __name__ == "__main__":
    sys.exit(main())
