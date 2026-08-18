#!/usr/bin/env python
"""
Decisive test requested by the coordinator: tighten primalMinResTol by several
orders of magnitude (1e-8 -> 1e-12) and redo the dCD/dshape finite-difference
step-size study on the three flagged components (idx 0, 1, 6), to test the
hypothesis that the earlier disagreement was a finite-difference noise-floor
artifact of the primal's residual tolerance, not a real adjoint error.

Same daOptions/meshOptions/Top class as runScript.py and stepStudy.py, except
primalMinResTol is tightened from 1e-8 to 1e-12 here. controlDict endTime was
raised from 1000 to 3000 (see system/controlDict) to give the tighter-tolerance
primal solve room to actually reach the new tolerance instead of stalling at
the iteration cap.

This script also explicitly measures the CD noise floor: it re-solves the
baseline (shape=0) primal five times, each arrived at via a different path
(interspersed between the perturbed solves for idx0, idx1, idx6), and reports
the spread. That spread is the smallest CD difference this finite-difference
setup can trust, and therefore bounds the smallest safe step size h.
"""

import os
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
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
    "primalMinResTol": 1.0e-12,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["wing"],
            "directionMode": "parallelToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
        "CL": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["wing"],
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
            "patches": ["inout"],
            "flowAxis": "x",
            "normalAxis": "y",
            "components": ["solver", "function"],
        },
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


def runBaseline(tag):
    prob.set_val("dvs.shape", baselineShape)
    prob.set_val("dvs.patchV", np.array([U0, aoa0]))
    prob.run_model()
    cd = float(prob.get_val("scenario1.aero_post.CD")[0])
    if rank == 0:
        print("STEPSTUDY2 NOISEFLOOR_BASELINE_CD tag=%s value=%.15e" % (tag, cd))
    return cd


# ---- baseline #1 (cold start) + adjoint ----
cd_b1 = runBaseline("cold_start")

totals = prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["dvs.shape"])
adjointKey = [k for k in totals.keys() if k[1] == "dvs.shape"][0]
adjoint = np.array(totals[adjointKey]).flatten()
if rank == 0:
    for i in range(nShape):
        print("STEPSTUDY2 ADJOINT idx=%d value=%.15e" % (i, adjoint[i]))

# ---- baseline #2, reached via a warm-started re-solve at the same design point ----
cd_b2 = runBaseline("warm_restart_1")

flaggedIdx = [0, 1, 6]
steps = [1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]

baselineTags = iter(["after_idx0", "after_idx1", "after_idx6"])

for idx in flaggedIdx:
    for step in steps:
        plus = baselineShape.copy()
        plus[idx] = step
        prob.set_val("dvs.shape", plus)
        prob.set_val("dvs.patchV", np.array([U0, aoa0]))
        prob.run_model()
        CDp = float(prob.get_val("scenario1.aero_post.CD")[0])

        minus = baselineShape.copy()
        minus[idx] = -step
        prob.set_val("dvs.shape", minus)
        prob.set_val("dvs.patchV", np.array([U0, aoa0]))
        prob.run_model()
        CDm = float(prob.get_val("scenario1.aero_post.CD")[0])

        fd = (CDp - CDm) / (2.0 * step)
        if rank == 0:
            print(
                "STEPSTUDY2 FD idx=%d step=%.1e CD_plus=%.15e CD_minus=%.15e fd=%.15e"
                % (idx, step, CDp, CDm, fd)
            )

    # noise-floor sample: return to shape=0 via a different path after each component's sweep
    runBaseline(next(baselineTags))

if rank == 0:
    print("STEPSTUDY2 DONE")
