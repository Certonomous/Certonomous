#!/usr/bin/env python
"""
DAFoam run script for the naca0015_sail case (lab inventory geometry,
mesh-cache key naca0015_sail-rung-coarse-s23-b0.7, 63920 cells), adapted
from the NACA0012_Airfoil_Incompressible tutorial runScript.py.

Differences from the lab's own OpenFOAM-only setup in
mission-output/geometry-study/study-naca0015_sail (which used kOmegaSST with
wall functions at U0=75, AoA=0): this script switches the turbulence closure
to SpalartAllmaras (the closure DAFoam's adjoint is verified against on the
2D tutorial) and adds a 5-degree yaw angle so the side-force (CL-analog)
gradient is non-degenerate. U0=75, nu=1.5e-5, lRef=1.2, Aref=2.16,
liftDir=(0,1,0), dragDir=(1,0,0) are carried over unchanged from the lab's
own case (system/controlDict forceCoeffs1 in that directory).
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
U0 = 75.0
p0 = 0.0
nuTilda0 = 4.5e-05
aoa0 = 5.0  # degrees, yaw in the x-y plane (chosen for this diagnostic run)
A0 = 2.16  # Aref = chord(1.2) * span(1.8), from the lab's forceCoeffs1
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
            "normalAxis": "y",
            "components": ["solver", "function"],
        },
    },
}

# Mesh deformation setup. No symmetry planes: this is a genuine 3D external
# domain (unlike the tutorial's z-thin, symmetry-plane-bounded 2D mesh).
# IDWarp still requires the 'symmetryPlanes' key to be present (it refuses to
# auto-detect symmetry for OpenFOAM/PLOT3D meshes even when there are none),
# so pass an explicit empty list.
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
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/sailFFD.xyz", type="ffd"))
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))

        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        self.connect("geometry.x_aero0", "scenario1.x_aero")

    def configure(self):
        points = self.mesh.mphys_get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points)
        tri_points = self.mesh.mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        # FFD is 5 (chord) x 2 (thickness) x 2 (span) -- span planes (k=0,1)
        # are tied together so the shape mode is uniform along the span,
        # the same convention the tutorial uses for its two z-planes.
        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_y = np.array([0.0, 1.0, 0.0])
        shapes = []
        for i in range(1, pts.shape[0] - 1):
            for j in range(pts.shape[1]):
                shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
        for i in [0, pts.shape[0] - 1]:
            shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)

        # thickness/volume/LE-radius geometric constraints, evaluated at two
        # spanwise stations near the root and near the tip
        leList = [[1e-4, 0.0, 0.05], [1e-4, 0.0, 1.75]]
        teList = [[1.1988, 0.0, 0.05], [1.1988, 0.0, 1.75]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0])

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
