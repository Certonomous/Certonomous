#!/usr/bin/env python
"""
DAFoam run script for the naca4412_wing case (lab inventory geometry,
mesh-cache key naca4412_wing/polyMesh, 337334 cells), adapted from the
naca0015_sail_coarse runScript.py (itself adapted from the
NACA0012_Airfoil_Incompressible tutorial runScript.py).

Flow conditions carried, unchanged, from the lab's own OpenFOAM-only case
mission-output/geometry-study/study-naca4412_wing/case (0/U, constant/
transportProperties, system/controlDict forceCoeffs1):
  U0 = 15 m/s, AoA = 0 deg (case 0/U: internalField/freestreamValue is exactly
  (15 -0 -0), i.e. flow purely along x, no artificial yaw needed -- the
  NACA4412 is cambered and produces lift at zero AoA, unlike the sail's
  symmetric NACA0015 section which needed an artificial 5 deg yaw for a
  non-degenerate side-force gradient),
  nu = 1.5e-5 (constant/transportProperties, identical value carried),
  lRef = 1.0003, Aref = 3.0009, dragDir = (1,-0,-0), liftDir = (0,0,1),
  CofR = (0.49985, 0, 0.0349165) (system/controlDict forceCoeffs1).
Not carried unchanged: the lab's own case used kOmegaSST turbulence with
rhoInf=1.225 (a dimensional forceCoeffs post-processing function object).
This script instead uses SpalartAllmaras with nuTilda0=4.5e-5 (the same
closure and freestream value as the tutorial and the sail case, the only
closure this DAFoam installation's adjoint has been checked against) and
rho0=1.0 (the standard DAFoam incompressible-function convention: p is
solved kinematically, so Cd/Cl are independent of the rho0 used in the
scale factor as long as it is applied consistently -- this reproduces the
same dimensionless Cd/Cl OpenFOAM's own forceCoeffs would report for any
rhoInf, since rhoInf cancels in the coefficient ratio for incompressible
flow).

Geometry orientation differs from the sail: here the wing lies with chord
along x [0,1], span along y [-1.5,1.5], and thickness/lift along z
[-0.029,0.099] (checked against work_sail/naca4412_wing_check/logMeshCheck.txt
body-patch bounding box). The sail's FFD/shape-function code perturbed
along y (its thickness axis); this script perturbs along z instead, using
an FFD box (FFD/wingFFD.xyz) built with chord as its first index, thickness
(real z) as its second index, and span (real y, tied across its two planes
so the shape mode is uniform along span, same convention as the sail and
the tutorial's two z-planes) as its third index.

No symmetry planes: this is a genuine 3D external domain (full wing span,
not a half-span with a symmetry plane). IDWarp still requires the
'symmetryPlanes' key to be present (it refuses to auto-detect symmetry for
OpenFOAM/PLOT3D meshes even when there are none), so pass an explicit
empty list, per the lesson from the sail case.
"""

import os
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP


parser = argparse.ArgumentParser()
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
parser.add_argument("-task", help="type of run to do", type=str, default="run_model")
args = parser.parse_args()

# =============================================================================
# Input Parameters (see docstring above for provenance of each)
# =============================================================================
U0 = 15.0
p0 = 0.0
nuTilda0 = 4.5e-05
aoa0 = 0.0  # degrees, pitch in the x-z plane; carried directly from the lab's own case (0/U is exactly (15,-0,-0))
A0 = 3.0009  # Aref, from the lab's forceCoeffs1
rho0 = 1.0

daOptions = {
    "designSurfaces": ["body"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-8,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["farfield"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["farfield"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["farfield"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["body"],
            "directionMode": "parallelToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
        "CL": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["body"],
            "directionMode": "normalToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "nuTilda": nuTilda0 * 10.0,
        "phi": 1.0,
    },
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {
            "type": "patchVelocity",
            "patches": ["farfield"],
            "flowAxis": "x",
            "normalAxis": "z",
            "components": ["solver", "function"],
        },
    },
}

# Mesh deformation setup. No symmetry planes: genuine 3D external domain
# (full-span wing). IDWarp requires 'symmetryPlanes' present; pass [].
meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [],
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

        # FFD is 5 (chord) x 2 (thickness, real z) x 2 (span, real y) --
        # span planes (k=0,1) are tied together so the shape mode is
        # uniform along the span, the same convention the sail and the
        # tutorial (its two z-planes) use. dir_z is the thickness/lift
        # perturbation direction here (the sail used dir_y for this role
        # since its thickness axis was real y; this wing's thickness axis
        # is real z).
        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_z = np.array([0.0, 0.0, 1.0])
        shapes = []
        for i in range(1, pts.shape[0] - 1):
            for j in range(pts.shape[1]):
                shapes.append({pts[i, j, 0]: dir_z, pts[i, j, 1]: dir_z})
        for i in [0, pts.shape[0] - 1]:
            shapes.append({pts[i, 0, 0]: dir_z, pts[i, 0, 1]: dir_z, pts[i, 1, 0]: -dir_z, pts[i, 1, 1]: -dir_z})
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)

        # thickness/volume/LE-radius geometric constraints, evaluated at two
        # spanwise stations near the root and near the tip. leList/teList
        # give [x, y, z] at the LE/TE; y is the span coordinate here (real
        # wing span -1.5 to 1.5), unlike the sail where z was span.
        # z~0 at LE/TE: NACA4412's camber line is zero at both the leading
        # and trailing edge by construction (camber only builds up over the
        # interior of the chord, peaking near 40% chord), so the true LE/TE
        # nose points sit near z~0, not at the mid-thickness bbox value (an
        # earlier attempt used z=0.035, the bbox midpoint, and pyGeo's
        # addLERadiusConstraints rejected it: "Leading edge radius points
        # are too far from the leading edge point to form a circle"). This
        # is corroborated by the lab's own CofR z=0.0349165 at the quarter
        # chord (system/controlDict forceCoeffs1), which matches the
        # standard NACA camber-line formula evaluated at x/c=0.25 for a
        # 4412 section (zc(0.25c) = 0.034375*c) to within rounding.
        #
        # x=2.5e-4 (0.025% chord) was ALSO rejected by addLERadiusConstraints,
        # still "too far ... to form a circle": at that station the local
        # thickness (from the standard NACA thickness formula, t=0.12,
        # d(x=2.5e-4) ~ 0.0055*c) is smaller than 2x the LE radius
        # (r_LE ~ 1.1019*t^2*c ~ 0.0159*c), so DVCon's own
        # d[i] >= 2*r[i] sanity check fails: the probe was placed inside the
        # LE nose radius itself, not outboard of it. x=0.02 (2% chord) gives
        # a local thickness ~0.047*c, comfortably more than 2x the LE
        # radius, so the up/down surface probe and the LE-nose probe no
        # longer coincide. z is bumped to the camber-line height at x=0.02c
        # (zc(0.02c) ~ 0.0039*c) for the same reason.
        leList = [[0.02, -1.45, 0.004], [0.02, 1.45, 0.004]]
        teList = [[0.999, -1.45, 0.0], [0.999, 1.45, 0.0]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 0.0, 1.0], [-1.0, 0.0, 0.0])

        self.dvs.add_output("shape", val=np.array([0.0] * len(shapes)))
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        self.connect("patchV", "scenario1.patchV")
        self.connect("shape", "geometry.shape")

        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)

        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("scenario1.aero_post.CL", equals=0.3, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

optFuncs = OptFuncs(daOptions, prob)

if args.task == "run_model":
    prob.run_model()
    if MPI.COMM_WORLD.rank == 0:
        print("RUNMODEL CD", prob.get_val("scenario1.aero_post.CD"))
        print("RUNMODEL CL", prob.get_val("scenario1.aero_post.CL"))
elif args.task == "compute_totals":
    prob.run_model()
    if MPI.COMM_WORLD.rank == 0:
        print("COMPUTETOTALS CD", prob.get_val("scenario1.aero_post.CD"))
        print("COMPUTETOTALS CL", prob.get_val("scenario1.aero_post.CL"))
    totals = prob.compute_totals()
    if MPI.COMM_WORLD.rank == 0:
        print(totals)
elif args.task == "check_totals":
    prob.run_model()
    prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")
else:
    print("task arg not found!")
    exit(1)
