#!/usr/bin/env python
"""
Step-size study for dCD/dshape on the NACA0012 incompressible tutorial case.

This reuses the exact same DAFoam/OpenMDAO problem setup as runScript.py (same
daOptions, meshOptions, Top class, flow conditions, mesh) so that the adjoint
value computed here is the same case as the one reported in compute_totals_run1.log
and check_totals_run1.log. It then:

  1. Recomputes the adjoint dCD/dshape via prob.compute_totals() as a sanity check
     against the earlier run.
  2. For the three shape design variables flagged as high relative-error in the
     step=1e-3 check_totals run (indices 0, 1, 6), sweeps the central-difference
     step size over 1e-4, 1e-5, 1e-6, 1e-7, 1e-8 and reports the resulting FD
     derivative at each step, so we can see whether FD is converging to the
     adjoint value, diverging from it, or noisy (cancellation) at small steps.

All CD values are the real converged CD from DAFoam's SIMPLE solver at the
same primalMinResTol tolerance as the production runs (1e-8).
"""

import os
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP

# =============================================================================
# Input Parameters (identical to runScript.py)
# =============================================================================
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

# ---- baseline primal + adjoint (sanity check against compute_totals_run1.log) ----
prob.set_val("dvs.shape", baselineShape)
prob.set_val("dvs.patchV", np.array([U0, aoa0]))
prob.run_model()
CD0 = float(prob.get_val("scenario1.aero_post.CD")[0])
if rank == 0:
    print("STEPSTUDY BASELINE_CD %.15e" % CD0)

totals = prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["dvs.shape"])
if rank == 0:
    print("STEPSTUDY RAW_TOTALS_DICT", totals)
# pull out whatever key OpenMDAO resolved this to (promoted name or absolute path)
adjointKey = [k for k in totals.keys() if k[1] == "dvs.shape"][0]
adjoint = np.array(totals[adjointKey]).flatten()
if rank == 0:
    for i in range(nShape):
        print("STEPSTUDY ADJOINT idx=%d value=%.15e" % (i, adjoint[i]))

# ---- step-size sweep for the flagged components ----
flaggedIdx = [0, 1, 6]
steps = [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]

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
                "STEPSTUDY FD idx=%d step=%.1e CD_plus=%.15e CD_minus=%.15e fd=%.15e"
                % (idx, step, CDp, CDm, fd)
            )

# reset back to baseline
prob.set_val("dvs.shape", baselineShape)
prob.set_val("dvs.patchV", np.array([U0, aoa0]))
prob.run_model()
if rank == 0:
    print("STEPSTUDY DONE")
