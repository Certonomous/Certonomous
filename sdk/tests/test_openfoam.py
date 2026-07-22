import sys
import tempfile
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.openfoam import (
    DEFAULT_DESIGN,
    SyntheticOpenFoamApi,
    build_case,
    openfoam_registry,
    parse_force_coefficients,
    parse_mesh_log,
    parse_solver_log,
)


class CaseGenerationTests(unittest.TestCase):
    def _case(self, design):
        root = Path(tempfile.mkdtemp())
        resolved = build_case(root, design)
        return root, resolved

    def test_case_contains_every_required_file(self):
        root, _resolved = self._case({})
        for relative in (
            "system/blockMeshDict", "system/controlDict", "system/fvSchemes",
            "system/fvSolution", "constant/transportProperties",
            "constant/turbulenceProperties", "0/U", "0/p",
        ):
            self.assertTrue((root / relative).exists(), relative)

    def test_design_parameters_reach_the_dictionaries(self):
        root, _resolved = self._case({
            "cylinder_diameter": 1.5,
            "inlet_velocity": 2.0,
            "kinematic_viscosity": 0.03,
        })
        control = (root / "system" / "controlDict").read_text()
        self.assertIn("lRef            1.5", control)
        self.assertIn("magUInf         2", control)
        transport = (root / "constant" / "transportProperties").read_text()
        self.assertIn("0.03", transport)
        velocity = (root / "0" / "U").read_text()
        self.assertIn("freestreamValue uniform (2 0 0)", velocity)

    def test_mesh_scales_with_refinement_and_stays_wellformed(self):
        coarse_root, _ = self._case({"mesh_refinement": 0.5})
        fine_root, _ = self._case({"mesh_refinement": 2.0})
        coarse = (coarse_root / "system" / "blockMeshDict").read_text()
        fine = (fine_root / "system" / "blockMeshDict").read_text()
        self.assertIn("(15 10 1)", coarse)
        self.assertIn("(60 40 1)", fine)
        for text in (coarse, fine):
            self.assertEqual(text.count("hex ("), 4)
            self.assertEqual(text.count("arc "), 16)
            for patch in ("cylinder", "farfield", "frontAndBack"):
                self.assertIn(patch, text)

    def test_geometry_scales_with_diameter(self):
        root, _ = self._case({"cylinder_diameter": 2.0})
        text = (root / "system" / "blockMeshDict").read_text()
        # Inner arc midpoint sits at radius D/2 on the +x axis; farfield at 10 D.
        self.assertIn("arc 0 1 (1 0 0)", text)
        self.assertIn("(20 0 0)", text)


class ParserTests(unittest.TestCase):
    MODERN = (
        "# Force coefficients\n"
        "# liftDir     : (0 1 0)\n"
        "# Time Cd Cs Cl CmRoll CmPitch CmYaw Cd(f) Cd(r)\n"
        "1 4.0 0 0.30 0 0 0 2.0 2.0\n"
        "2 2.4 0 0.20 0 0 0 1.2 1.2\n"
        "3 2.2 0 0.11 0 0 0 1.1 1.1\n"
        "4 2.1 0 0.10 0 0 0 1.05 1.05\n"
        "5 2.0 0 0.10 0 0 0 1.0 1.0\n"
    )
    LEGACY = (
        "# Time Cm Cd Cl Cl(f) Cl(r)\n"
        "100 0.0 1.62 0.01 0.005 0.005\n"
    )

    def test_modern_coefficient_table(self):
        parsed = parse_force_coefficients(self.MODERN)
        self.assertAlmostEqual(parsed["Cd"], 2.05)  # mean of the final-window rows
        self.assertAlmostEqual(parsed["Cl"], 0.10)
        self.assertIn("Cd_oscillation", parsed)

    def test_legacy_coefficient_table(self):
        parsed = parse_force_coefficients(self.LEGACY)
        self.assertAlmostEqual(parsed["Cd"], 1.62)
        self.assertAlmostEqual(parsed["Cl"], 0.01)

    def test_solver_log_reports_convergence_and_residuals(self):
        log = (
            "Time = 430\n"
            "smoothSolver:  Solving for Ux, Initial residual = 1e-05, Final residual = 3.1e-07, No Iterations 4\n"
            "smoothSolver:  Solving for Uy, Initial residual = 2e-05, Final residual = 4.2e-07, No Iterations 4\n"
            "GAMG:  Solving for p, Initial residual = 0.0001, Final residual = 8.5e-06, No Iterations 6\n"
            "SIMPLE solution converged in 431 iterations\n"
        )
        parsed = parse_solver_log(log)
        self.assertEqual(parsed["converged"], 1.0)
        self.assertEqual(parsed["solver_iterations"], 431.0)
        self.assertAlmostEqual(parsed["convergence_residual"], 8.5e-06)

    def test_unconverged_log_keeps_last_time(self):
        log = (
            "Time = 1999\n"
            "smoothSolver:  Solving for Ux, Initial residual = 0.01, Final residual = 0.002, No Iterations 4\n"
            "Time = 2000\n"
            "smoothSolver:  Solving for Ux, Initial residual = 0.01, Final residual = 0.001, No Iterations 4\n"
        )
        parsed = parse_solver_log(log)
        self.assertEqual(parsed["converged"], 0.0)
        self.assertEqual(parsed["solver_iterations"], 2000.0)
        self.assertAlmostEqual(parsed["convergence_residual"], 0.001)

    def test_mesh_log_cell_count(self):
        self.assertEqual(parse_mesh_log("  nPoints: 5000\n  nCells: 4800\n"), {"cell_count": 4800.0})


class SyntheticBackendTests(unittest.TestCase):
    def test_reynolds_and_determinism(self):
        api = SyntheticOpenFoamApi()
        first = api.evaluate({"inlet_velocity": 2.0, "cylinder_diameter": 1.0, "kinematic_viscosity": 0.05}, ["aerodynamics"])
        again = api.evaluate({"inlet_velocity": 2.0, "cylinder_diameter": 1.0, "kinematic_viscosity": 0.05}, ["aerodynamics"])
        self.assertEqual(first, again)
        self.assertAlmostEqual(first["Re"], 40.0)

    def test_finer_mesh_reduces_drag_error(self):
        api = SyntheticOpenFoamApi()
        coarse = api.evaluate({"mesh_refinement": 0.5}, ["aerodynamics"])
        fine = api.evaluate({"mesh_refinement": 3.0}, ["aerodynamics"])
        self.assertGreater(coarse["Cd"], fine["Cd"])
        self.assertGreater(fine["cell_count"], coarse["cell_count"])

    def test_convergence_degrades_past_steady_wake_limit(self):
        api = SyntheticOpenFoamApi()
        steady = api.evaluate({"kinematic_viscosity": 0.05}, ["aerodynamics"])      # Re = 20
        unsteady = api.evaluate({"kinematic_viscosity": 0.005}, ["aerodynamics"])   # Re = 200
        self.assertEqual(steady["converged"], 1.0)
        self.assertEqual(unsteady["converged"], 0.0)
        self.assertGreater(unsteady["convergence_residual"], steady["convergence_residual"])


if __name__ == "__main__":
    unittest.main()
