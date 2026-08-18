#!/usr/bin/env python
"""
Fresh-process probe: run A1's NACA0012 primal at one shape point, then read
the CONVERGED wall-face nutw (turbulent viscosity at the wing wall boundary,
as computed by nutUSpaldingWallFunctionFvPatchScalarFieldDF::calcNut()) DIRECTLY
off disk (the "wing" boundaryField block of the written nut file), rather than
through getOFField (which only exposes the volScalarField's INTERNAL field --
the wall FACE value from a wall function BC lives in the boundaryField and is
not reachable through that API).

Purpose: test the hypothesis that DASpalartAllmaras's wall treatment,
nutUSpaldingWallFunctionFvPatchScalarFieldDF::calcNut(), contains a genuine
discrete branch:

    tmp<scalarField> tnutw(
        max(scalar(0), sqr(calcUTau(magGradU)) / (magGradU + ROOTVSMALL) - nuw));

i.e. nutw is clipped to exactly 0 whenever the raw Newton-converged value
would be negative. If a leading-edge wall face sits close enough to this
clip that it is on one side of it at shape-eps and the other side at
shape-minus-eps, the quantity check_totals differences (CD as a function of
shape) is not differentiable there and a central finite difference is not
measuring dCD/dshape -- it is measuring the secant slope across a kink, while
the discrete adjoint (which linearizes around ONE fixed state, the baseline)
sees a locally-smooth branch. That would make the ADJOINT right and the FD
CHECK wrong for any component whose perturbation crosses this branch, and
would explain step-independence (every step size straddles the same kink).

Usage: python probeWallBranch.py --idx N --step H --tag NAME
  idx  : shape DV component to perturb (0-7), or -1 for baseline (shape=0)
  step : signed perturbation (e.g. 1e-4 or -1e-4); ignored if idx=-1
  tag  : label used only for the printed summary line

Runs SERIAL (no mpirun) deliberately, so the written field lands directly at
<caseDir>/<time>/nut (no processorN merging needed) and the wing patch's
full 126-face boundaryField block is available whole, in one place, after a
single run_model() call. daOptions/meshOptions/Top class are byte-identical
to runScript.py (this case's own trusted script) -- nothing else changed.
"""
import os
import re
import sys
import glob
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, required=True)
parser.add_argument("--step", type=float, default=0.0)
parser.add_argument("--tag", type=str, default="run")
args = parser.parse_args()

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
CL_target = 0.5
aoa0 = 5.13918623195176
A0 = 0.1
rho0 = 1.0

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-8,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "CD": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
        "CL": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "normalToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": nuTilda0 * 10.0, "phi": 1.0},
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {"type": "patchVelocity", "patches": ["inout"], "flowAxis": "x",
                   "normalAxis": "y", "components": ["solver", "function"]},
    },
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh", dafoam_builder.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))
        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        self.connect("geometry.x_aero0", "scenario1.x_aero")

    def configure(self):
        points = self.mesh.mphys_get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points)
        tri_points = self.mesh.mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_y = np.array([0.0, 1.0, 0.0])
        shapes = []
        for i in range(1, pts.shape[0] - 1):
            for j in range(pts.shape[1]):
                shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
        for i in [0, pts.shape[0] - 1]:
            shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)

        leList = [[1e-4, 0.0, 1e-4], [1e-4, 0.0, 0.1 - 1e-4]]
        teList = [[0.998 - 1e-4, 0.0, 1e-4], [0.998 - 1e-4, 0.0, 0.1 - 1e-4]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0])

        self.dvs.add_output("shape", val=np.array([0] * len(shapes)))
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        self.connect("patchV", "scenario1.patchV")
        self.connect("shape", "geometry.shape")

        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

nShape = 8
shapeVec = np.zeros(nShape)
if args.idx >= 0:
    shapeVec[args.idx] = args.step

prob.set_val("dvs.shape", shapeVec)
prob.set_val("dvs.patchV", np.array([U0, aoa0]))
prob.run_model()
cd = float(prob.get_val("scenario1.aero_post.CD")[0])
cl = float(prob.get_val("scenario1.aero_post.CL")[0])

# ---------------------------------------------------------------------------
# Mesh quality on THIS run's deformed (post-warp, post-converge) mesh, via
# DAFoam's own DACheckMesh (same tool/thresholds used elsewhere in this lab,
# e.g. B3's "max aspect ratio ..., max non-orthogonality ..., max skewness
# ..." check). Called explicitly AFTER run_model() so it inspects the shape
# actually solved in THIS process (idx/step), not the pristine baseline mesh
# checkMesh may also run once internally at solver construction time.
# ---------------------------------------------------------------------------
print("CHECKMESH_BEGIN tag=%s" % args.tag, flush=True)
DASolver = prob.model.scenario1.aero_post.functionals.DASolver
meshOK = DASolver.solver.checkMesh()
print("CHECKMESH_END tag=%s meshOK=%d" % (args.tag, int(meshOK)), flush=True)

# ---------------------------------------------------------------------------
# find the time directory this run just wrote (runTime.writeNow() at
# convergence writes the CURRENT time index, not a multiple of writeInterval)
# ---------------------------------------------------------------------------
timeDirs = []
for d in os.listdir("."):
    if re.match(r"^[0-9]+(\.[0-9]+)?$", d) and d not in ("0",):
        try:
            timeDirs.append((float(d), d))
        except ValueError:
            pass
if not timeDirs:
    print("PROBE_ERROR tag=%s no time directory found besides 0/" % args.tag, flush=True)
    sys.exit(1)
timeDirs.sort()
finalTimeVal, finalTimeDir = timeDirs[-1]

nutPath = os.path.join(finalTimeDir, "nut")
if os.path.exists(nutPath):
    with open(nutPath, "r") as f:
        content = f.read()
elif os.path.exists(nutPath + ".gz"):
    import gzip

    nutPath = nutPath + ".gz"
    with gzip.open(nutPath, "rt") as f:
        content = f.read()
else:
    print("PROBE_ERROR tag=%s no nut file (plain or .gz) in %s" % (args.tag, finalTimeDir), flush=True)
    sys.exit(1)

# extract the "wing" boundaryField block and its nonuniform value list
m = re.search(r'"?\(?wing\)?"?\s*\{(.*?)\n\s*\}', content, re.DOTALL)
if m is None:
    print("PROBE_ERROR tag=%s could not find wing boundaryField block in %s" % (args.tag, nutPath), flush=True)
    sys.exit(1)
block = m.group(1)

typeMatch = re.search(r"type\s+(\S+);", block)
bcType = typeMatch.group(1) if typeMatch else "UNKNOWN"

# nonuniform List<scalar> N ( v1 v2 ... vN )  -- OpenFOAM ascii list format
listMatch = re.search(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(([^)]*)\)", block)
if listMatch is not None:
    n = int(listMatch.group(1))
    vals = np.array([float(x) for x in listMatch.group(2).split()])
    assert len(vals) == n, "parsed %d values, header says %d" % (len(vals), n)
else:
    # uniform value fallback (shouldn't happen for a wall function patch, but handle it)
    uniMatch = re.search(r"uniform\s+([\-0-9.eE+]+)", block)
    if uniMatch is None:
        print("PROBE_ERROR tag=%s could not parse wing nut values from %s" % (args.tag, nutPath), flush=True)
        sys.exit(1)
    # need face count from boundary file; read it
    with open("constant/polyMesh/boundary", "r") as bf:
        bcontent = bf.read()
    nfMatch = re.search(r"wing\s*\{[^}]*nFaces\s+(\d+);", bcontent, re.DOTALL)
    n = int(nfMatch.group(1))
    vals = np.full(n, float(uniMatch.group(1)))

nZero = int(np.sum(vals == 0.0))
nPos = int(np.sum(vals > 0.0))
nNeg = int(np.sum(vals < 0.0))

print(
    "PROBE tag=%s idx=%d step=%.6e finalTime=%s CD=%.15e CL=%.15e bcType=%s nWingFaces=%d nZero=%d nPos=%d nNeg=%d"
    % (args.tag, args.idx, args.step, finalTimeDir, cd, cl, bcType, len(vals), nZero, nPos, nNeg),
    flush=True,
)
print("PROBE_VALUES tag=%s %s" % (args.tag, " ".join("%.10e" % v for v in vals)), flush=True)
print("PROBE_ZEROMASK tag=%s %s" % (args.tag, " ".join("1" if v == 0.0 else "0" for v in vals)), flush=True)
print("PROBE DONE tag=%s" % args.tag, flush=True)

# ---------------------------------------------------------------------------
# LE-LOCALIZED cell volumes (coordinator's follow-up: is degradation
# restricted to/concentrated at the leading edge, not just a global stat?).
# DAFoam's getOFField only exposes internal fields registered by NAME in the
# object registry; raw per-cell volume (mesh.V()) is not one, so this uses
# the stock OpenFOAM function object 'writeCellVolumes' as a subprocess on
# the SAME deformed mesh this process just wrote to <finalTimeDir>/polyMesh,
# then maps each of the wing patch's 126 boundary faces to its OWNER
# (interior, wall-adjacent) cell via constant/polyMesh/owner, so the volume
# printed at index i below is the same physical wall-adjacent cell as the
# nutw value at index i above -- directly comparable, same indexing.
# ---------------------------------------------------------------------------
import subprocess
import gzip as _gzip

cellVolProc = subprocess.run(
    ["postProcess", "-func", "writeCellVolumes", "-time", finalTimeDir],
    capture_output=True,
    text=True,
)
print("WRITECELLVOLUMES_RC tag=%s rc=%d" % (args.tag, cellVolProc.returncode), flush=True)
if cellVolProc.returncode != 0:
    print("PROBE_ERROR tag=%s writeCellVolumes failed: %s" % (args.tag, cellVolProc.stderr[-500:]), flush=True)
    sys.exit(1)


def readFoamFile(path):
    if os.path.exists(path):
        with open(path, "r") as fh:
            return fh.read()
    elif os.path.exists(path + ".gz"):
        with _gzip.open(path + ".gz", "rt") as fh:
            return fh.read()
    else:
        return None


# parse boundary file for wing patch's startFace/nFaces (do not hardcode)
bcontent = readFoamFile("constant/polyMesh/boundary")
bm = re.search(r"wing\s*\{([^}]*)\}", bcontent, re.DOTALL)
startFace = int(re.search(r"startFace\s+(\d+);", bm.group(1)).group(1))
nFacesWing = int(re.search(r"nFaces\s+(\d+);", bm.group(1)).group(1))
assert nFacesWing == len(vals), "wing face count mismatch: boundary=%d nut=%d" % (nFacesWing, len(vals))

# parse owner list (labelList, plain "N (\n v0 \n v1 ... )" format, no "nonuniform" prefix)
ownerContent = readFoamFile("constant/polyMesh/owner")
om = re.search(r"\n(\d+)\s*\n\(\n(.*?)\n\)\n", ownerContent, re.DOTALL)
nOwnerTotal = int(om.group(1))
ownerList = [int(x) for x in om.group(2).split()]
assert len(ownerList) == nOwnerTotal, "owner list parse mismatch: got %d, header says %d" % (len(ownerList), nOwnerTotal)
wingOwnerCells = ownerList[startFace : startFace + nFacesWing]

# parse the freshly-written per-cell volume field (internal field only, no boundary needed)
vContent = readFoamFile(os.path.join(finalTimeDir, "V"))
vm = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(([^)]*)\)", vContent, re.DOTALL)
nCellsV = int(vm.group(1))
cellVols = np.array([float(x) for x in vm.group(2).split()])
assert len(cellVols) == nCellsV, "V field parse mismatch: got %d, header says %d" % (len(cellVols), nCellsV)

wingCellVols = cellVols[wingOwnerCells]
print(
    "PROBE_CELLVOL tag=%s %s"
    % (args.tag, " ".join("%.10e" % v for v in wingCellVols)),
    flush=True,
)
print(
    "PROBE_CELLVOL_SUMMARY tag=%s minCellVol=%.10e minCellVolIdx=%d nNegOrZero=%d"
    % (args.tag, float(np.min(wingCellVols)), int(np.argmin(wingCellVols)), int(np.sum(wingCellVols <= 0.0))),
    flush=True,
)
print("PROBE_CELLVOL_DONE tag=%s" % args.tag, flush=True)
