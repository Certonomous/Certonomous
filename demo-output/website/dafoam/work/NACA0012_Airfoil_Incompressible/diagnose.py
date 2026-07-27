#!/usr/bin/env python
"""
Diagnostic script requested by the coordinator, checks 3 (chain isolation, attempted
via component-level check_partials on the mesh-warping / geometry components rather
than the full CFD-based finite difference) and 4 (idx6: what does it control, is a
geometric constraint active at baseline).

Same daOptions/meshOptions/Top class as runScript.py, primalMinResTol restored to
1e-8 (this script does not need the tight tolerance; it is not doing a CFD-level FD
comparison).
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
        print("DIAGNOSE pts.shape =", pts.shape)
        dir_y = np.array([0.0, 1.0, 0.0])
        shapes = []
        for i in range(1, pts.shape[0] - 1):
            for j in range(pts.shape[1]):
                shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
                print(f"DIAGNOSE shape idx={len(shapes)-1} station_i={i} side_j={j} (interior)")
        for i in [0, pts.shape[0] - 1]:
            shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
            print(f"DIAGNOSE shape idx={len(shapes)-1} station_i={i} (LE/TE combo, i=0 is LE, i={pts.shape[0]-1} is TE)")
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

if rank == 0:
    print("DIAGNOSE BASELINE_CD", float(prob.get_val("scenario1.aero_post.CD")[0]))
    print("DIAGNOSE BASELINE_CL", float(prob.get_val("scenario1.aero_post.CL")[0]))
    thickcon = prob.get_val("geometry.thickcon")
    volcon = prob.get_val("geometry.volcon")
    rcon = prob.get_val("geometry.rcon")
    print("DIAGNOSE BASELINE_thickcon", list(thickcon), "lower_bound=0.5 upper_bound=3.0")
    print("DIAGNOSE BASELINE_volcon", list(volcon), "lower_bound=1.0")
    print("DIAGNOSE BASELINE_rcon", list(rcon), "lower_bound=0.8")
    print(
        "DIAGNOSE rcon_min",
        float(np.min(rcon)),
        "distance_above_lower_bound",
        float(np.min(rcon) - 0.8),
        "relative_margin_pct",
        float((np.min(rcon) - 0.8) / 0.8 * 100.0),
    )
    print(
        "DIAGNOSE thickcon_min",
        float(np.min(thickcon)),
        "distance_above_lower_bound",
        float(np.min(thickcon) - 0.5),
    )
    print("DIAGNOSE volcon_min", float(np.min(volcon)), "distance_above_lower_bound", float(np.min(volcon) - 1.0))

# list all outputs/inputs to find the mesh-warping component name
if rank == 0:
    print("DIAGNOSE === model outputs (looking for mesh-warping component) ===")
    for absname, meta in prob.model.list_outputs(out_stream=None, prom_name=True):
        if "warp" in absname.lower() or "vol_coord" in absname.lower() or "idwarp" in absname.lower():
            print("DIAGNOSE OUTPUT:", absname, meta.get("prom_name", ""), meta.get("shape", ""))

# check_partials scoped to the geometry (FFD) component only: FFD/DVGeo Jacobian vs its own FD,
# no CFD, no mesh warping involved. This is a fast, low-risk isolation of the FFD parameterization
# derivative (already indirectly confirmed exact by the machine-precision thickcon/volcon/rcon match
# in check_totals, but checked here directly and explicitly).
if rank == 0:
    print("DIAGNOSE === check_partials on geometry component (FFD/DVGeo Jacobian only) ===")
data_geom = prob.check_partials(includes=["geometry"], compact_print=True, method="fd", step=1e-6)

if rank == 0:
    print("DIAGNOSE DONE")
