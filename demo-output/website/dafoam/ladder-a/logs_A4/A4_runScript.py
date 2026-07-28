#!/usr/bin/env python
"""
DAFoam run script for the Ahmed body, 25 degree rear slant.
Ladder A4. Geometry: constant/triSurface/ahmed_25.stl, byte-identical to the
already-validated plain-OpenFOAM case at
mission-output/geometry-study/study-ahmed_25 (45,753 cells, kOmegaSST,
CD 0.08978 measured / 0.3219 rebased to frontal area, VALIDATED tier
against Ahmed, Ramm & Faltin 1984, SAE 840300, within 13% of Cd 0.285).
This script re-runs that SAME geometry and mesh recipe through DASimpleFoam
(pyDAFoam) so the primal is comparable to that credentialed result, and
wires up ONE shape design variable (FFD/ahmedFFD.xyz, rear-slant
break-line height) for the adjoint stage.
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
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
args = parser.parse_args()

# =============================================================================
# Input parameters -- match the validated OpenFOAM ahmed_25 case exactly
# =============================================================================
U0 = 40.0
p0 = 0.0
k0 = 0.24
omega0 = 8.56731
rho0 = 1.225
Aref = 0.401696  # measured planform area, same basis as the OpenFOAM baseline
lRef = 1.044

daOptions = {
    "designSurfaces": ["body"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-4,
    "primalMinResTolDiff": 1.0e5,
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["body"],
            "directionMode": "fixedDirection",
            "direction": [1.0, 0.0, 0.0],
            "scale": 1.0 / (0.5 * U0 * U0 * Aref * rho0),
        },
        "CL": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["body"],
            "directionMode": "fixedDirection",
            "direction": [0.0, 0.0, 1.0],
            "scale": 1.0 / (0.5 * U0 * U0 * Aref * rho0),
        },
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "k": k0,
        "omega": omega0,
        "phi": 1.0,
    },
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
    },
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    # full (non-half) Ahmed body mesh -- no real symmetry plane, but IDWarp
    # requires this key to be present for OpenFOAM meshes to skip its
    # (unsupported for OpenFOAM/PLOT3D) auto-detection of symmetry surfaces.
    "symmetryPlanes": [],
}


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)

        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh", dafoam_builder.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/ahmedFFD.xyz", type="ffd"))
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))

        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        self.connect("geometry.x_aero0", "scenario1.x_aero")

    def configure(self):
        points = self.mesh.mphys_get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points)

        # single rear-slant shape DV: move the i=1 (x=0.80, just upstream of
        # the slant break at x=0.8428) TOP row (k=1, z=0.31) of FFD control
        # points, both y, together, purely in z. Nose (i=0), rear tip (i=2)
        # and underbody (k=0) are untouched by construction.
        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_z = np.array([0.0, 0.0, 1.0])
        shapes = [{pts[1, 0, 1]: dir_z, pts[1, 1, 1]: dir_z}]
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)

        self.dvs.add_output("shape", val=np.array([0.0] * len(shapes)))
        self.connect("shape", "geometry.shape")

        self.add_design_var("shape", lower=-0.05, upper=0.05, scaler=1.0)
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
om.n2(prob, show_browser=False, outfile="mphys.html")

optFuncs = OptFuncs(daOptions, prob)

if args.task == "run_driver":
    prob.run_model()
    if MPI.COMM_WORLD.rank == 0:
        print("CD:", prob.get_val("scenario1.aero_post.CD"))
elif args.task == "run_model":
    prob.run_model()
    if MPI.COMM_WORLD.rank == 0:
        print("CD:", prob.get_val("scenario1.aero_post.CD"))
elif args.task == "compute_totals":
    prob.run_model()
    totals = prob.compute_totals()
    if MPI.COMM_WORLD.rank == 0:
        print("totals:", totals)
elif args.task == "check_totals":
    prob.run_model()
    prob.check_totals(
        compact_print=True,
        step=1e-3,
        form="central",
        step_calc="abs",
    )
else:
    print("task arg not supported!")
    exit(1)
