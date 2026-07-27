#!/usr/bin/env python
"""
Extend the refined-mesh (14720 cells, primalMinResTol=1e-11) test from
stepStudyRefined.py to ALL 8 shape components, not just the 3 flagged ones
(idx 0, 1, 6). stepStudyRefined.py only recomputed FD for idx 0/1/6 and left
idx 2,3,4,5,7 as adjoint-only on the refined mesh; but the refined-mesh
ADJOINT itself (already in stepstudy_refined_run1.log) moved a lot from the
coarse-mesh adjoint for several components -- including two sign changes
(idx1, idx7) -- which the coarse-vs-coarse check_totals comparison could not
have revealed. This script closes that gap: single central-difference step
h=1e-4 (already shown, for idx0/1/6, to sit in a converged plateau between
1e-4 and 1e-6 at this tolerance) for ALL 8 components, so AD-vs-FD can be
reported for the complete gradient on the refined mesh, not just the 3
originally-flagged components.

Identical daOptions/meshOptions/Top class to stepStudyRefined.py (same case,
same mesh, same primalMinResTol=1e-11).
"""
import os
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
CL_target = 0.5
aoa0 = 5.13918623195176
A0 = 0.1
rho0 = 1.0

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-11,
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

rank = MPI.COMM_WORLD.rank
nShape = 8
baselineShape = np.zeros(nShape)

prob.set_val("dvs.shape", baselineShape)
prob.set_val("dvs.patchV", np.array([U0, aoa0]))
prob.run_model()
cd0 = float(prob.get_val("scenario1.aero_post.CD")[0])
if rank == 0:
    print("CHECKALL8REF BASELINE_CD %.15e" % cd0, flush=True)

totals = prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["dvs.shape"])
adjointKey = [k for k in totals.keys() if k[1] == "dvs.shape"][0]
adjoint = np.array(totals[adjointKey]).flatten()
if rank == 0:
    for i in range(nShape):
        print("CHECKALL8REF ADJOINT idx=%d value=%.15e" % (i, adjoint[i]), flush=True)

h = 1e-4
for idx in range(nShape):
    plus = baselineShape.copy()
    plus[idx] = h
    prob.set_val("dvs.shape", plus)
    prob.set_val("dvs.patchV", np.array([U0, aoa0]))
    prob.run_model()
    CDp = float(prob.get_val("scenario1.aero_post.CD")[0])

    minus = baselineShape.copy()
    minus[idx] = -h
    prob.set_val("dvs.shape", minus)
    prob.set_val("dvs.patchV", np.array([U0, aoa0]))
    prob.run_model()
    CDm = float(prob.get_val("scenario1.aero_post.CD")[0])

    fd = (CDp - CDm) / (2.0 * h)
    relerr = (adjoint[idx] - fd) / fd if fd != 0 else float("nan")
    if rank == 0:
        print(
            "CHECKALL8REF FD idx=%d h=%.1e CD_plus=%.15e CD_minus=%.15e fd=%.15e adjoint=%.15e relerr=%.6e"
            % (idx, h, CDp, CDm, fd, adjoint[idx], relerr),
            flush=True,
        )

if rank == 0:
    print("CHECKALL8REF DONE", flush=True)
