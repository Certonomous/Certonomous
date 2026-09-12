#!/usr/bin/env python3
"""
PLANTED FORCE PERTURBATION (CLAUDE.md rule 3), pre-registration §8.1.

A zero from a reader not shown able to see a non-zero is not evidence. The forces
functionObject is the instrument that produces CL, CD and CM, so before it is believed it is
made to see a KNOWN perturbation and the answer is checked against a value computed
independently of OpenFOAM.

METHOD. Raise the pressure field uniformly by a known dp. For a uniform pressure the pressure
force on the integrated surface is exactly dp * sum(Sf) over the wing and body patches, where
sum(Sf) is the vector area of those patches. That vector area is computed HERE, from the
source UGRID file's own wall faces, never from OpenFOAM. The functionObject must then report
a force change equal to it.

REFUSES (exit 2) if the reader cannot see the plant, or sees it wrong by more than 1e-6
relative -- it does not warn and continue.
"""
import os, sys, re, subprocess, shutil, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ugrid_to_gmsh import read_ugrid

FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
DP = 137.0          # Pa, the plant: arbitrary, known, and not a round number
WALL_TAGS = (1, 2)  # body, wing -- identified by area against GeoLab's documented .mapbc


def wall_vector_area(ugrid_path, scale=0.0254):
    """sum(Sf) over the wall patches, from the SOURCE file. Never touches OpenFOAM."""
    g = read_ugrid(ugrid_path)
    nodes = g["nodes"] * scale
    tags = g["tags"]
    ntri = len(g["tri"])
    tot = np.zeros(3)
    for conn, off in ((g["tri"], 0), (g["quad"], ntri)):
        if not len(conn):
            continue
        m = np.isin(tags[off:off + len(conn)], WALL_TAGS)
        pts = nodes[conn[m] - 1]
        if conn.shape[1] == 3:
            tot += (0.5 * np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])).sum(0)
        else:
            tot += (0.5 * np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])).sum(0)
            tot += (0.5 * np.cross(pts[:, 2] - pts[:, 0], pts[:, 3] - pts[:, 0])).sum(0)
    return tot


def read_force(case, t):
    """Total pressure force vector from the forces functionObject output."""
    for root, _, files in os.walk(os.path.join(case, "postProcessing")):
        for fn in files:
            if fn.startswith("force") and fn.endswith(".dat") and "coeff" not in fn:
                for line in reversed(open(os.path.join(root, fn)).read().splitlines()):
                    if line.startswith("#") or not line.strip():
                        continue
                    v = re.findall(r"\(([^)]*)\)", line)
                    if v:
                        return np.array([float(x) for x in v[0].split()])
    return None


def run(cmd, cwd, log):
    with open(log, "w") as lf:
        return subprocess.run(["bash", "-lc", f"source {FOAM} >/dev/null 2>&1; cd {cwd} && {cmd}"],
                              stdout=lf, stderr=subprocess.STDOUT).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mesh-case", required=True)
    ap.add_argument("--src-case", required=True)
    ap.add_argument("--ugrid", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()

    Sf = wall_vector_area(a.ugrid)
    print(f"sum(Sf) over wing+body, from the SOURCE file  = "
          f"({Sf[0]:.9e}, {Sf[1]:.9e}, {Sf[2]:.9e}) m^2")
    print(f"  |sum(Sf)| = {np.linalg.norm(Sf):.9e} m^2")
    expected = DP * Sf
    print(f"PREDICTED force change for dp = {DP} Pa: "
          f"({expected[0]:.9e}, {expected[1]:.9e}, {expected[2]:.9e}) N")

    if os.path.exists(a.work):
        shutil.rmtree(a.work)
    os.makedirs(a.work)
    os.symlink(os.path.join(a.mesh_case, "constant", "polyMesh"),
               os.path.join(a.work, "constant_polyMesh_tmp"))
    os.makedirs(os.path.join(a.work, "constant"))
    os.symlink(os.path.join(a.mesh_case, "constant", "polyMesh"),
               os.path.join(a.work, "constant", "polyMesh"))
    for f in ("thermophysicalProperties", "turbulenceProperties"):
        shutil.copy(os.path.join(a.src_case, "constant", f), os.path.join(a.work, "constant", f))
    shutil.copytree(os.path.join(a.src_case, "system"), os.path.join(a.work, "system"))
    shutil.copytree(os.path.join(a.src_case, "0"), os.path.join(a.work, "0"))
    open(os.path.join(a.work, "system", "controlDict"), "w").write(
        'FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}\n'
        'application rhoSimpleFoam; startFrom startTime; startTime 0; stopAt endTime;\n'
        'endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;\n'
        'functions { #include "forces" }\n')

    forces = {}
    for label, dp in (("clean", 0.0), ("planted", DP)):
        if dp:
            p = os.path.join(a.work, "0", "p")
            s = open(p).read()
            m = re.search(r"internalField\s+uniform\s+([0-9.eE+-]+);", s)
            base = float(m.group(1))
            s = re.sub(r"internalField\s+uniform\s+[0-9.eE+-]+;",
                       f"internalField   uniform {base + dp};", s)
            s = re.sub(r"(freestreamValue\s+uniform\s+)[0-9.eE+-]+;",
                       rf"\g<1>{base + dp};", s)
            open(p, "w").write(s)
            print(f"PLANTED: p {base} -> {base + dp} Pa")
        shutil.rmtree(os.path.join(a.work, "postProcessing"), ignore_errors=True)
        rc = run("postProcess -func forces -time 0 -fields '(U p T rho)'", a.work,
                 os.path.join(a.work, f"log.postProcess.{label}"))
        F = read_force(a.work, 0)
        if F is None:
            print(f"  {label}: NO FORCE READ -- REFUSE"); sys.exit(2)
        forces[label] = F
        print(f"  {label:<8} pressure force = ({F[0]:.9e}, {F[1]:.9e}, {F[2]:.9e}) N   rc={rc}")

    d = forces["planted"] - forces["clean"]
    print(f"\nOBSERVED change = ({d[0]:.9e}, {d[1]:.9e}, {d[2]:.9e}) N")
    print(f"PREDICTED       = ({expected[0]:.9e}, {expected[1]:.9e}, {expected[2]:.9e}) N")
    den = np.linalg.norm(expected)
    rel = np.linalg.norm(d - expected) / den if den else np.inf
    rel_neg = np.linalg.norm(d + expected) / den if den else np.inf
    print(f"relative error = {rel:.3e}   (opposite sign convention: {rel_neg:.3e})")
    if min(rel, rel_neg) < 1e-6:
        print("\nPLANTED FORCE CONTROL: PASS -- the forces functionObject is shown able to see a")
        print("known non-zero change on exactly the wing and body patches, so a force it reports")
        print("is evidence. Sign convention: " + ("as predicted" if rel < rel_neg else "outward-normal opposite, recorded"))
        sys.exit(0)
    print("\nPLANTED FORCE CONTROL: REFUSE -- reader did not reproduce the plant.")
    sys.exit(2)

if __name__ == "__main__":
    main()
