#!/usr/bin/env python3
"""
T9aH mesh verification for the three cases the frozen checker's list omits.

*** NEW FILE, and NOT covered by the supervisor's step-4 read.  Its output is
*** provenance until it has been read.  IT GRADES NOTHING: it is a GUARD
*** (Charter 2c) -- its failure withdraws the RUN, never the hypothesis.

The seven frozen case names are verified by the BYTE-IDENTICAL frozen
check_t9a_mesh.py (sha cb7fa05a...), whose main() walks T9a_registered.json's
own case list.  RL_f, H40_f and H4000_f are not in that list, so this file
drives the frozen check_wall() over them UNMODIFIED -- the T9a-D precedent
(check_t9aD_mesh.py) and section 6.6 of the pre-registration.

For the two contrast cases the registered layer-k map is overridden IN MEMORY
for the duration of one call and RESTORED, with the restoration asserted,
because the frozen checker verifies every cell's 0/DT against that map and
would otherwise correctly refuse a 0.4 or 0.004 field.  The frozen
T9a_registered.json on disk is never edited.

Zero solver compute.  It runs postProcess -func writeCellCentres at t = 0 once
per case (inside the frozen checker), which is a field-writing utility and not
a solver; that is stated rather than folded into "zero compute".
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_t9a_mesh as MESH      # noqa: E402  frozen, byte-identical
import analyse_t9a as A            # noqa: E402  frozen, byte-identical

EXTRA = (("RL_f", 0.04), ("H40_f", 0.4), ("H4000_f", 0.004))
GEOM = {"kind": "wall", "cells_per_layer": [26, 51, 13]}


def main():
    ok = True
    for name, k2 in EXTRA:
        saved_mesh = copy.deepcopy(MESH.REG["wall"]["layers"])
        saved_ana = copy.deepcopy(A.REG["wall"]["layers"])
        try:
            MESH.REG["wall"]["layers"][1]["k"] = k2
            A.REG["wall"]["layers"][1]["k"] = k2
            ok &= bool(MESH.check_wall(name, GEOM))
        finally:
            MESH.REG["wall"]["layers"] = saved_mesh
            A.REG["wall"]["layers"] = saved_ana
        assert MESH.REG["wall"]["layers"][1]["k"] == 0.04, \
            "frozen check_t9a_mesh.REG layer-k map was NOT restored"
        assert A.REG["wall"]["layers"][1]["k"] == 0.04, \
            "frozen analyse_t9a.REG layer-k map was NOT restored"
    print("\nALL EXTRA T9aH MESHES VERIFIED" if ok else
          "\nMESH VERIFICATION FAILED -- the RUN is withdrawn, not the hypothesis")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
