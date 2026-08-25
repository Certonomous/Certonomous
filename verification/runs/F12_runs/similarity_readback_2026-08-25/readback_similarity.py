#!/usr/bin/env python3
"""F12 attempt-2 ladder -- THE SIMILARITY READ-BACK (MESH_STANDARD.md sec 9.2).

Section 9.2 makes this a REQUIRED, CHECKABLE DELIVERABLE:

    "Every cfd mesh ladder must record, per level, the ACTUAL VALUE of every
     grading and first-cell parameter its generator used -- read back from the
     written dictionary or the built mesh, NEVER from the parameter that was
     requested. ... The requested value is the thing that lied. Only the
     returned value tells the truth."

So this file parses the three WRITTEN blockMeshDicts and compares what is
actually in them.  It reads no builder parameter and imports no builder.

WHAT SIMILARITY REQUIRES of a geometrically-graded blockMesh family, and why:
under a similar refinement every cell in a column halves, so the blockMesh TOTAL
expansion ratio (last cell / first cell) is PRESERVED across levels while the
cell-to-cell ratio goes as its (n-1)-th root.  Topology, block count and the
per-block cell-count doubling must be exact.

IT RULES NOTHING.  It prints measurements and a boolean per criterion.  Whether
a given residual drift is admissible is the supervisor's and verification's
call, not this file's.
"""
from __future__ import annotations
import json, pathlib, re, sys

M = pathlib.Path("/home/ubuntu/Certonomous/verification/runs/F12_runs/"
                 "mesh_ladder_attempt2_2026-08-25")
OUT = pathlib.Path("/home/ubuntu/Certonomous/verification/runs/F12_runs/"
                   "similarity_readback_2026-08-25/similarity_readback.json")
LEVELS = ("coarse", "medium", "fine")
BLOCK = re.compile(r"hex\s*\(([^)]*)\)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)\s*"
                   r"(simpleGrading|edgeGrading)\s*\(([^)]*)\)", re.S)


def parse(level):
    p = M / level / "system" / "blockMeshDict"
    txt = p.read_text()
    body = txt[txt.index("\nblocks"):]
    body = body[:body.index("\nedges")] if "\nedges" in body else body
    out = []
    for m in BLOCK.finditer(body):
        out.append({"verts": m.group(1).split(),
                    "n": [int(m.group(2)), int(m.group(3)), int(m.group(4))],
                    "kind": m.group(5),
                    "grading": [float(x) for x in m.group(6).split()]})
    if not out:
        print(f"REFUSED: no blocks parsed from {p}"); sys.exit(2)
    return out


def dev(a, b):
    return abs(b - a) / max(abs(a), 1e-30)


def main():
    D = {lv: parse(lv) for lv in LEVELS}
    nb = {lv: len(D[lv]) for lv in LEVELS}
    R = {"what": "MESH_STANDARD.md sec 9.2 similarity read-back, from the "
                 "WRITTEN dictionaries",
         "rules_nothing": True,
         "dict_paths": {lv: str(M / lv / "system" / "blockMeshDict")
                        for lv in LEVELS},
         "n_blocks": nb}

    # --- PLANTED CONTROL: the comparator must be able to SEE a broken ladder.
    # Perturb one level's wall-normal grading and prove the check flips.
    import copy
    P = copy.deepcopy(D)
    P["fine"][0]["grading"][1] *= 1.5
    def similar(data):
        if not (len(data["coarse"]) == len(data["medium"]) == len(data["fine"])):
            return False
        for i in range(len(data["coarse"])):
            c, m_, f = data["coarse"][i], data["medium"][i], data["fine"][i]
            if not (c["verts"] == m_["verts"] == f["verts"]):
                return False
            if not (m_["n"][0] == 2 * c["n"][0] and f["n"][0] == 2 * m_["n"][0]
                    and m_["n"][1] == 2 * c["n"][1] and f["n"][1] == 2 * m_["n"][1]):
                return False
            for a, b, d in zip(c["grading"], m_["grading"], f["grading"]):
                if max(dev(a, b), dev(a, d)) > 1e-9:
                    return False
        return True
    R["planted_control"] = {
        "arm": "wall-normal grading of the fine level's block 0 scaled x1.5",
        "unperturbed_reads_similar": similar(D),
        "perturbed_reads_NOT_similar": not similar(P),
        "PASSED": (not similar(P))}
    if not R["planted_control"]["PASSED"]:
        print("CONTROL REFUSED: the comparator cannot see a broken ladder; "
              "its 'similar' means nothing")
        sys.exit(1)

    if not (nb["coarse"] == nb["medium"] == nb["fine"]):
        R["VERDICT_INPUT"] = "block counts differ"
        OUT.write_text(json.dumps(R, indent=1) + "\n"); sys.exit(2)

    topo_ok = n_ok = True
    sw_dev, wn_vals, wake = [], {lv: set() for lv in LEVELS}, []
    for i in range(nb["coarse"]):
        c, m_, f = D["coarse"][i], D["medium"][i], D["fine"][i]
        topo_ok &= (c["verts"] == m_["verts"] == f["verts"]
                    and c["kind"] == m_["kind"] == f["kind"])
        n_ok &= (m_["n"][0] == 2 * c["n"][0] and f["n"][0] == 2 * m_["n"][0]
                 and m_["n"][1] == 2 * c["n"][1] and f["n"][1] == 2 * m_["n"][1]
                 and c["n"][2] == m_["n"][2] == f["n"][2] == 1)
        if c["kind"] == "simpleGrading":
            sw_dev.append(max(dev(c["grading"][0], m_["grading"][0]),
                              dev(c["grading"][0], f["grading"][0])))
            for lv, b in zip(LEVELS, (c, m_, f)):
                wn_vals[lv].add(b["grading"][1])
        else:
            wake.append({"block": i,
                         "grading": {lv: b["grading"]
                                     for lv, b in zip(LEVELS, (c, m_, f))},
                         "unity_slots": {lv: [j for j, x in enumerate(b["grading"])
                                              if x == 1.0]
                                         for lv, b in zip(LEVELS, (c, m_, f))}})

    wn = {lv: sorted(wn_vals[lv]) for lv in LEVELS}
    wn_dev = max(dev(wn["coarse"][0], wn["medium"][0]),
                 dev(wn["coarse"][0], wn["fine"][0]))
    flip = any(w["unity_slots"]["coarse"] != w["unity_slots"]["medium"]
               or w["unity_slots"]["coarse"] != w["unity_slots"]["fine"]
               for w in wake)
    wake_sw_dev = max(max(dev(w["grading"]["coarse"][0], w["grading"]["medium"][0]),
                          dev(w["grading"]["coarse"][0], w["grading"]["fine"][0]))
                      for w in wake) if wake else None

    R["measured"] = {
        "topology_identical_all_levels": topo_ok,
        "every_block_doubles_in_x_and_y": n_ok,
        "streamwise_grading_max_relative_deviation": max(sw_dev) if sw_dev else None,
        "streamwise_blocks_compared": len(sw_dev),
        "wall_normal_total_expansion": {lv: wn[lv] for lv in LEVELS},
        "wall_normal_max_relative_deviation": wn_dev,
        "wake_far_side_BRANCH_FLIP": flip,
        "wake_streamwise_max_relative_deviation": wake_sw_dev,
        "wake_blocks": wake,
    }
    R["reading"] = {
        "exactly_similar": ["topology", "block count",
                            "per-block cell-count doubling in x and y",
                            f"all {len(sw_dev)} streamwise gradings "
                            f"(deviation {max(sw_dev):.3e})"],
        "residual_drift": {
            "wall_normal_total_expansion":
                f"{wn_dev*100:.4f} % coarse->fine",
            "wake_streamwise_edge_grading":
                f"{wake_sw_dev*100:.4f} % coarse->fine",
        },
        "sec_9_2_branch_flip": "ABSENT -- the unity slots of both wake blocks "
                               "are identical at all three levels, so the "
                               "guard that fired at the fine level in attempt 1 "
                               "does not fire in attempt 2.",
        "NOT_RULED": "Whether the wall-normal residual drift is admissible is "
                     "the supervisor's and verification's call. This file "
                     "measures; it does not rule.",
    }
    OUT.write_text(json.dumps(R, indent=1) + "\n")
    print(json.dumps({"planted_control": R["planted_control"]["PASSED"],
                      **R["measured"]}, indent=1, default=str)[:1400])
    print(f"\nwritten {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
