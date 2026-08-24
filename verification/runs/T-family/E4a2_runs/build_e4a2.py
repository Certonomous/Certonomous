#!/usr/bin/env python3
"""
E4a2 case builder -- successor rung to E4a.  WRITES DICTIONARIES ONLY.  Runs
no OpenFOAM utility and no solver; creates no mesh and no time directory.

EVERY case input except system/controlDict is produced by the FROZEN E4a
builder's own functions, IMPORTED, never copied and never edited:
    build_e4a.p_field, .u_field, .block_mesh, .fv_schemes, .fv_solution,
    .transport, .turbulence, .header, .g, .fan_curve_entry
so the fields, mesh, schemes, relaxation, linear-solver tolerances and BCs of
E4a2 are byte-identical to E4a's by CONSTRUCTION, not by assertion.  The one
locally written dictionary is system/controlDict, and the only entries that
differ from E4a's are endTime (20000 -> 60000), writeInterval (5000 -> 2000)
and the comment prose.  Rule 6: the frozen file on disk is never touched.

The frozen builder's guard() and verify() are reused through the restoring
`in_dir` redirect of its module-level HERE (the with_ratio / T10aR in_tree
precedent), so the one-change-per-case structural check and the age guard are
the frozen ones, not re-implementations.

GUARDS: refuses if any case directory, DONE.*/STATUS.* marker or numeric time
directory already exists under this tree; refuses if any frozen instrument's
sha256 differs from the registered table.  The supervisor commits the freeze
BEFORE this builder runs.
"""
import sys
sys.dont_write_bytecode = True          # no __pycache__ in any frozen tree

import hashlib                                                     # noqa: E402
import json                                                        # noqa: E402
import os                                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TFAM = os.path.dirname(HERE)
E4_DIR = os.path.join(TFAM, "E4_runs")
sys.path.insert(0, E4_DIR)
import build_e4a as B4                                # noqa: E402  FROZEN

REG = json.load(open(os.path.join(HERE, "E4a2_registered.json")))
TIME = REG["time"]
CASES = REG["cases"]
EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def verify_frozen():
    for rel, want in REG["frozen_instruments"].items():
        p = os.path.join(TFAM, rel)
        got = sha256_of(p)
        if got != want:
            refuse(f"frozen instrument {rel} hashes {got}, registered {want}")
    for k in REG["carried_over_keys"]:
        if REG[k] != B4.REG[k]:
            refuse(f"carried-over key '{k}' differs from E4a's registered json")
    if HERE == B4.HERE:
        refuse("this builder resolves to E4a's own run tree")


class in_dir:
    """Redirect a frozen module's HERE to THIS rung's run tree for one block,
    restoring on exit.  The frozen FILE is never modified; only this process's
    imported module object, and only inside the `with`."""

    def __init__(self, mod, path):
        self.mod, self.path = mod, path

    def __enter__(self):
        self.old = self.mod.HERE
        self.mod.HERE = self.path
        return self

    def __exit__(self, *a):
        self.mod.HERE = self.old
        return False


def control_dict():
    """The ONE locally written dictionary.  Differences from the frozen
    build_e4a.control_dict(): endTime, writeInterval, and comment prose.
    purgeWrite stays 0 (retain every checkpoint), writePrecision stays 12,
    runTimeModifiable stays false, application/startFrom/stopAt/deltaT and
    writeControl/writeFormat/writeCompression/timeFormat/timePrecision are all
    unchanged."""
    return B4.header("dictionary", "controlDict", "system") + f"""
application     simpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {TIME['endTime']};
deltaT          {TIME['deltaT']};

// writeInterval STRICTLY < endTime (L-140).  purgeWrite 0 retains ALL
// {TIME['endTime'] // TIME['writeInterval']} checkpoints, so the FIRST CROSSING of the registered
// convergence floor is measurable and the plateau reading has a series to
// read -- the T3 ext1 lesson that purgeWrite 2 made over-shoot unmeasurable.
writeControl    timeStep;
writeInterval   {TIME['writeInterval']};
purgeWrite      {TIME['purgeWrite']};
writeFormat     ascii;
writePrecision  {TIME['writePrecision']};
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
"""


def write_case(name):
    spec = CASES[name]
    d = os.path.join(HERE, name)
    content = {
        "0.orig/p": B4.p_field(spec["curve"]),          # FROZEN
        "0.orig/U": B4.u_field(),                       # FROZEN
        "constant/transportProperties": B4.transport(),  # FROZEN
        "constant/turbulenceProperties": B4.turbulence(),  # FROZEN
        "system/blockMeshDict": B4.block_mesh(spec["nx"], spec["ny"]),  # FROZEN
        "system/controlDict": control_dict(),           # LOCAL, the one change
        "system/fvSchemes": B4.fv_schemes(),            # FROZEN
        "system/fvSolution": B4.fv_solution(),          # FROZEN
    }
    for rel, txt in content.items():
        path = os.path.join(d, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(txt)


def main():
    verify_frozen()
    with in_dir(B4, HERE):
        B4.guard()                       # FROZEN age/pre-existence guard
        for name in CASES:
            write_case(name)
        sha = B4.verify()                # FROZEN one-change-per-case check
    man = os.path.join(HERE, "BUILD_MANIFEST.txt")
    with open(man, "w") as fh:
        fh.write("E4a2 build manifest -- dictionaries only; no utility, no "
                 "solver, no mesh, no time directory was created.\n"
                 "Every file except system/controlDict is written by the "
                 "FROZEN build_e4a.py functions, imported.\n")
        for name in sorted(CASES):
            for rel in B4.FILES:
                fh.write(f"{sha[name][rel]}  {name}/{rel}\n")
    if B4.HERE != E4_DIR:
        refuse("in_dir did not restore the frozen builder's HERE")
    print(f"built {len(CASES)} case dictionaries; frozen verify() one-change "
          f"check passed; manifest {man}")
    for name in sorted(CASES):
        c = CASES[name]
        print(f"  {name:5s} curve {c['curve']:4s} ny {c['ny']:3d} nx "
              f"{c['nx']:3d} cells {c['nx']*c['ny']:6d} endTime "
              f"{TIME['endTime']} writeInterval {TIME['writeInterval']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
