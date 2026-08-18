#!/usr/bin/env python
"""
Use OpenMDAO's own check_partials (real, well-tested infrastructure, not a
hand-rolled script) on the mesh-warping component ONLY, in the real, fully-wired
Top model from runScript.py. This checks the DAFoamWarper component's
compute_jacvec_product (dXv/dXs, reverse mode -- the exact routine the real
adjoint uses) against OpenMDAO's own finite difference of that same component's
compute(), completely isolated from the CFD/adjoint (the CD/CL functionals and
their derivatives are not part of this component).

Unbuffered stdout, explicit component name discovery first, small step size
sweep, printed immediately (flush=True) so a slow/killed run still leaves a
usable partial log.
"""
import os
import sys
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
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
        self.add_constraint("scenario1.aero_post.CL", equals=0.5, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

rank = MPI.COMM_WORLD.rank
prob.set_val("dvs.shape", np.zeros(8))
prob.set_val("dvs.patchV", np.array([U0, aoa0]))
prob.run_model()

if rank == 0:
    print("DIAGPART === listing all component pathnames ===", flush=True)
    for absname, meta in prob.model.list_outputs(out_stream=None, prom_name=True):
        print("DIAGPART OUTPUT:", absname, flush=True)
    sys.stdout.flush()

if rank == 0:
    print("DIAGPART === check_partials: scenario1 coupling mesh warper component only ===", flush=True)

# the DAFoamWarper component lives inside scenario1's coupling group; find it by
# name pattern rather than hardcoding, then scope check_partials to it directly
warper_path = None
for absname, meta in prob.model.list_outputs(out_stream=None, prom_name=True):
    if "vol_coords" in absname and "scenario1" in absname:
        warper_path = absname.rsplit(".", 1)[0]
        break

if rank == 0:
    print("DIAGPART warper_path =", warper_path, flush=True)

if warper_path is not None:
    data = prob.check_partials(includes=[warper_path], compact_print=True, method="fd", step=1e-6)
    sys.stdout.flush()

if rank == 0:
    print("DIAGPART DONE", flush=True)
