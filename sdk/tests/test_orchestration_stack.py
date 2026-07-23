import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.case_memory import CASE_MEMORY, retrieve
from chief_engineer.chief_researcher import approve_closure, select_runs
from chief_engineer.compute_audit import ComputeAudit
from chief_engineer.monte_carlo import running_statistics
from chief_engineer.openfoam import PARAMETER_SPECS
from chief_engineer.transcript import CHIEF_RESEARCHER, Transcript


class TranscriptTests(unittest.TestCase):
    def test_entries_render_with_role_and_citations(self):
        script = Transcript("t", echo=None)
        script.researcher("closure approved", citations=("docs/NUMERICS_KNOWLEDGE.md #2",))
        rendered = script.render()
        self.assertIn(CHIEF_RESEARCHER, rendered)
        self.assertIn("docs/NUMERICS_KNOWLEDGE.md #2", rendered)
        self.assertEqual(script.citations(), ["docs/NUMERICS_KNOWLEDGE.md #2"])


class ComputeAuditTests(unittest.TestCase):
    """Verdict logic is tested directly; the live probe is exercised by the demo."""

    def _audit(self, **kwargs):
        defaults = dict(
            cores_total=14, cores_reserved=2, load_1min=0.1, memory_total_mb=7846,
            memory_available_mb=7000, other_jobs=0, solver_jobs=0,
            scripted_load_jobs=0, requested_workers=8, memory_per_worker_mb=256,
            cores_free=12, workers_by_cores=12, workers_by_memory=27,
            capacity=12, fits=True, reason="ok")
        defaults.update(kwargs)
        return ComputeAudit(**defaults)

    def test_panel_reports_fit_state(self):
        self.assertEqual(self._audit().panel()["verdict"], "FITS")
        self.assertEqual(self._audit(fits=False).panel()["verdict"], "CONSTRAINED")

    def test_headline_states_yes_or_no(self):
        self.assertIn("YES", self._audit().headline())
        self.assertIn("NO", self._audit(fits=False, capacity=2).headline())


class RunSelectionTests(unittest.TestCase):
    BASELINE = {"cylinder_diameter": 1.0, "inlet_velocity": 1.0,
                "kinematic_viscosity": 0.05, "mesh_refinement": 1.0}

    def test_selection_respects_capacity_and_explains_every_run(self):
        selection = select_runs(self.BASELINE, PARAMETER_SPECS, capacity=4, requested=12)
        self.assertEqual(len(selection.runs), 4)
        self.assertEqual(selection.covered_by_rom, 8)
        self.assertTrue(all(run.rationale for run in selection.runs))
        self.assertTrue(selection.citations)

    def test_first_run_is_the_anchor_and_designs_stay_in_bounds(self):
        selection = select_runs(self.BASELINE, PARAMETER_SPECS, capacity=5, requested=5)
        self.assertEqual(selection.runs[0].name, "anchor")
        bounds = {spec.name: (spec.minimum, spec.maximum) for spec in PARAMETER_SPECS}
        for run in selection.runs:
            for name, value in run.design.items():
                if name in bounds:
                    low, high = bounds[name]
                    self.assertGreaterEqual(value, low)
                    self.assertLessEqual(value, high)


class ClosureApprovalTests(unittest.TestCase):
    def test_case_inside_envelope_is_approved_with_citation(self):
        decision = approve_closure(geometry="cylinder-2d", flow="steady-laminar",
                                   reynolds=20, cells=600)
        self.assertTrue(decision.approved)
        self.assertEqual(decision.model.name, "coarse-grid-cylinder-Cd")
        self.assertTrue(decision.citations)
        self.assertIn("VALIDATED", decision.uncertainty_language)

    def test_reynolds_outside_envelope_is_rejected_with_orders(self):
        decision = approve_closure(geometry="cylinder-2d", flow="steady-laminar",
                                   reynolds=100, cells=600)
        self.assertFalse(decision.approved)
        self.assertIn("UNVALIDATED", decision.uncertainty_language)
        self.assertTrue(any("probe" in order for order in decision.orders))
        self.assertTrue(decision.citations)

    def test_uncontained_resolution_is_rejected(self):
        decision = approve_closure(geometry="cylinder-2d", flow="steady-laminar",
                                   reynolds=20, cells=50)
        self.assertFalse(decision.approved)

    def test_unknown_configuration_never_invents_a_closure(self):
        decision = approve_closure(geometry="airfoil-3d", flow="steady-turbulent",
                                   reynolds=5e5, cells=100000)
        self.assertFalse(decision.approved)
        self.assertIsNone(decision.model)

    def test_approved_and_rejected_language_differ(self):
        approved = approve_closure(geometry="cylinder-2d", flow="steady-laminar",
                                   reynolds=20, cells=600)
        rejected = approve_closure(geometry="cylinder-2d", flow="steady-laminar",
                                   reynolds=100, cells=600)
        self.assertNotEqual(approved.uncertainty_language, rejected.uncertainty_language)


class CaseMemoryTests(unittest.TestCase):
    def test_every_record_cites_a_real_source(self):
        for case in CASE_MEMORY:
            self.assertTrue(case.source.startswith("docs/"))
            self.assertTrue(case.validated_against)

    def test_retrieval_ranks_the_matching_case_first(self):
        matches = retrieve(dimensionality="3d", body_type="bluff",
                           flow="steady-turbulent", reynolds=3.0e5,
                           meshing="snappyHexMesh")
        self.assertEqual(matches[0].case.name, "motorbike-3d-turbulent")
        self.assertTrue(matches[0].shared)

    def test_mismatched_query_reports_differences(self):
        matches = retrieve(dimensionality="3d", body_type="streamlined",
                           flow="steady-turbulent", reynolds=5.0e5,
                           meshing="snappyHexMesh")
        self.assertTrue(matches[0].differing)


class MonteCarloStatisticsTests(unittest.TestCase):
    def test_running_band_tightens_with_more_samples(self):
        values = [2.0 + 0.05 * ((-1) ** i) * (i % 5) for i in range(40)]
        stats = running_statistics(values)
        early = stats["hi"][4] - stats["lo"][4]
        late = stats["hi"][-1] - stats["lo"][-1]
        self.assertLess(late, early)

    def test_single_sample_has_no_band(self):
        stats = running_statistics([1.5])
        self.assertEqual(stats["lo"][0], stats["hi"][0])


if __name__ == "__main__":
    unittest.main()


class RouterTests(unittest.TestCase):
    def _intent(self, text):
        from chief_engineer.router import classify
        return classify(text)

    def test_optimization_request_routes_to_shape_optimization(self):
        route = self._intent("Minimize drag on the cylinder body under constraints")
        self.assertEqual(route.intent, "shape-optimization")
        self.assertTrue(route.rationale)
        self.assertTrue(route.evidence)

    def test_deadline_routes_to_time_constrained_with_minutes(self):
        route = self._intent("I need drag for this case in 5 minutes")
        self.assertEqual(route.intent, "time-constrained")
        self.assertEqual(route.params["deadline_minutes"], 5.0)

    def test_reynolds_is_extracted_so_the_closure_ruling_follows_physics(self):
        route = self._intent("Drag for a cylinder at Re 100 within 10 minutes")
        self.assertEqual(route.intent, "time-constrained")
        self.assertEqual(route.params["reynolds"], 100.0)

    def test_unfamiliar_geometry_routes_to_unseen(self):
        route = self._intent("What drag for an airfoil? We have never run this geometry")
        self.assertEqual(route.intent, "unseen-geometry")
        self.assertFalse(route.params["geometry_known"])

    def test_confidence_question_routes_to_uncertainty_reduction(self):
        route = self._intent("How confident are we in that number? Tighten the error bars")
        self.assertEqual(route.intent, "uncertainty-reduction")

    def test_unmatched_request_falls_through_to_the_planner(self):
        from chief_engineer.router import GENERAL_MISSION
        self.assertEqual(self._intent("hello there").intent, GENERAL_MISSION)
        self.assertEqual(self._intent("").intent, GENERAL_MISSION)

    def test_every_route_explains_itself(self):
        for text in ("minimize drag", "in 5 minutes", "never run this geometry",
                     "how sure are you"):
            self.assertTrue(self._intent(text).rationale)

    def test_out_of_domain_physics_is_named(self):
        from chief_engineer.router import out_of_scope_domain
        self.assertEqual(out_of_scope_domain("simulate how the cube melts in a fire"),
                         "melting or phase change")
        self.assertIsNotNone(out_of_scope_domain("model the heat transfer on the wing"))
        self.assertIsNotNone(out_of_scope_domain("supersonic shock over the airframe"))

    def test_in_domain_requests_are_not_flagged_out_of_scope(self):
        from chief_engineer.router import out_of_scope_domain
        # Aerodynamics prompts, including "temperature" as a fluid property, stay in.
        for text in ("solve the drag on the b52 at cruise",
                     "optimize the L/D of an airliner for 300 passengers",
                     "what is the air temperature effect on the cylinder Cd",
                     "mesh and solve the motorbike"):
            self.assertIsNone(out_of_scope_domain(text), text)

    # -- professional demo directives (v2-E1): full engineering sentences,
    # not shorthand, must still land on the intended workflow. --
    def test_b52_directive_routes_to_geometry_study(self):
        route = self._intent(
            "Solve the external aerodynamics of the supplied B-52 geometry at "
            "240 m/s, sea-level conditions. Select the appropriate turbulence "
            "model and solver, gate the mesh on quality, and report drag and "
            "lift with confidence envelopes.")
        self.assertEqual(route.intent, "geometry-study")

    def test_motorbike_directive_routes_to_geometry_study(self):
        route = self._intent(
            "Solve the external aerodynamics of the supplied motorcycle-with-"
            "rider geometry at highway speed, sea-level conditions. Select the "
            "appropriate turbulence model and solver, gate the mesh on quality, "
            "and report the drag coefficient with a confidence envelope.")
        self.assertEqual(route.intent, "geometry-study")

    def test_naca4412_directive_routes_to_geometry_study(self):
        route = self._intent(
            "Solve the external aerodynamics of the supplied NACA 4412 "
            "finite-wing geometry at cruise Reynolds number. Select the "
            "appropriate turbulence model and solver, gate the mesh on "
            "quality, and report the lift and drag coefficients with "
            "confidence envelopes.")
        self.assertEqual(route.intent, "geometry-study")

    def test_airliner_directive_routes_to_aircraft_optimization(self):
        route = self._intent(
            "Optimize the lift-to-drag ratio of a twin-aisle airliner "
            "carrying 300 passengers over a 6000 km range, with take-off at "
            "85 m/s and landing at 72 m/s. Search the wing design space, mark "
            "any infeasible designs, and report the best feasible L/D with "
            "its envelope.")
        self.assertEqual(route.intent, "aircraft-optimization")

    def test_valve_directive_routes_to_valve_study(self):
        route = self._intent(
            "Optimize the leaflet opening angle of the aortic valve to "
            "minimize pressure loss over the cardiac cycle. Decompose the "
            "cycle into representative phase points, rule on the admissible "
            "method, and report the cycle-weighted loss with its uncertainty.")
        self.assertEqual(route.intent, "valve-study")


class CitationDisplayTests(unittest.TestCase):
    def _display(self, raw):
        from chief_engineer.citations import display
        return display(raw)

    def test_knowledge_entry_gets_a_human_title(self):
        shown = self._display("docs/NUMERICS_KNOWLEDGE.md #3 (convergence)")
        self.assertIn("Numerics knowledge", shown)
        self.assertIn("physical validity", shown)

    def test_lesson_gets_its_rule_spelled_out(self):
        shown = self._display("sdk/introspection/recipe/memory/LESSONS.md L-001")
        self.assertTrue(shown.startswith("Lesson L-001"))
        self.assertIn("irreducible", shown)

    def test_no_display_name_leaks_a_file_path(self):
        from chief_engineer.citations import contains_path
        raws = [
            "docs/NUMERICS_KNOWLEDGE.md #1 (validated cylinder benchmark)",
            "docs/NUMERICS_KNOWLEDGE.md #2 (grid convergence, this machine)",
            "docs/NUMERICS_KNOWLEDGE.md #3, #4 (unstable branch)",
            "sdk/introspection/recipe/memory/LESSONS.md L-001",
            "docs/NUMERICS_KNOWLEDGE.md (registry)",
            "some/unknown/file.py thing",
        ]
        for raw in raws:
            self.assertFalse(contains_path(self._display(raw)), raw)

    def test_transcript_entries_carry_display_citations(self):
        from chief_engineer.transcript import Transcript
        script = Transcript("t", echo=None)
        entry = script.engineer("x", citations=("docs/NUMERICS_KNOWLEDGE.md #3",))
        payload = entry.as_dict()
        self.assertIn("citations_display", payload)
        self.assertFalse(any("/" in name for name in payload["citations_display"]))


class GeometryTests(unittest.TestCase):
    def test_cylinder_surface_is_closed_and_scaled(self):
        from chief_engineer.geometry import cylinder_surface
        surface = cylinder_surface(2.0, segments=32)
        self.assertEqual(len(surface["faces"]), 64)
        self.assertAlmostEqual(surface["bounds"]["max"][0], 1.0, places=5)

    def test_binary_stl_round_trips(self):
        import struct, tempfile
        from pathlib import Path
        from chief_engineer.geometry import load_surface
        triangles = [((0, 0, 1), (0, 0, 0), (1, 0, 0), (0, 1, 0)),
                     ((0, 0, 1), (0, 0, 0), (1, 0, 0), (0, 0, 1))]
        blob = b"\0" * 80 + struct.pack("<I", len(triangles))
        for normal, a, b, c in triangles:
            blob += struct.pack("<12f", *normal, *a, *b, *c) + b"\0\0"
        path = Path(tempfile.mkdtemp()) / "part.stl"
        path.write_bytes(blob)
        surface = load_surface(path)
        self.assertEqual(surface["triangles_total"], 2)
        self.assertEqual(len(surface["faces"]), 2)

    def test_ascii_stl_is_detected(self):
        import tempfile
        from pathlib import Path
        from chief_engineer.geometry import load_surface
        text = ("solid s\nfacet normal 0 0 1\nouter loop\n"
                "vertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\n"
                "endloop\nendfacet\nendsolid s\n")
        path = Path(tempfile.mkdtemp()) / "part.stl"
        path.write_text(text)
        self.assertEqual(load_surface(path)["triangles_total"], 1)

    def test_large_surface_is_decimated_for_the_viewport(self):
        from chief_engineer.geometry import _package
        vertices = [[float(i), 0.0, 0.0] for i in range(3000)]
        faces = [[i, i + 1, i + 2] for i in range(0, 2990, 3)]
        packed = _package(vertices, faces, 100, "big")
        self.assertLessEqual(packed["triangles_shown"], 100)
        self.assertEqual(packed["triangles_total"], len(faces))
        self.assertTrue(all(max(f) < len(packed["vertices"]) for f in packed["faces"]))


class FieldRenderTests(unittest.TestCase):
    def _vtp(self, path):
        """A tiny two-triangle VTP with a point pressure field, base64 binary."""
        import base64, struct
        def arr(name, typ, fmt, values):
            raw = struct.pack(f"<{len(values)}{fmt}", *values)
            body = base64.b64encode(struct.pack("<Q", len(raw)) + raw).decode()
            return (f"<DataArray type='{typ}' Name='{name}' "
                    f"NumberOfComponents='{3 if name in ('Points',) else 1}' "
                    f"format='binary'>{body}</DataArray>")
        points = [0,0,0, 1,0,0, 0,1,0, 1,1,0]
        conn = [0,1,2, 1,3,2]
        offs = [3, 6]
        pres = [10.0, 20.0, 30.0, 40.0]
        xml = (
            "<?xml version='1.0'?>\n"
            "<VTKFile type='PolyData' version='0.1' byte_order='LittleEndian' header_type='UInt64'>\n"
            "<PolyData><Piece NumberOfPoints='4' NumberOfPolys='2'>\n"
            f"<Points>{arr('Points','Float32','f',points)}</Points>\n"
            f"<Polys>{arr('connectivity','Int64','q',conn)}{arr('offsets','Int64','q',offs)}</Polys>\n"
            f"<PointData>{arr('p','Float32','f',pres)}</PointData>\n"
            "</Piece></PolyData></VTKFile>\n")
        path.write_text(xml)
        return path

    def test_vtp_field_is_parsed_and_normalised(self):
        import tempfile
        from pathlib import Path
        from chief_engineer.field_render import load_field_surface
        vtp = self._vtp(Path(tempfile.mkdtemp()) / "body.vtp")
        payload = load_field_surface(vtp, field="p")
        self.assertEqual(payload["triangles_total"], 2)
        self.assertIsNotNone(payload["field"])
        self.assertEqual(payload["field"]["name"], "p")
        self.assertTrue(all(0.0 <= v <= 1.0 for v in payload["field"]["values"]))
        self.assertLess(payload["field"]["min"], payload["field"]["max"])

    def test_multiple_patches_merge(self):
        import tempfile
        from pathlib import Path
        from chief_engineer.field_render import load_field_surface
        root = Path(tempfile.mkdtemp())
        a = self._vtp(root / "patch_a.vtp")
        b = self._vtp(root / "patch_b.vtp")
        payload = load_field_surface([a, b], field="p")
        self.assertEqual(payload["triangles_total"], 4)
        self.assertEqual(len(payload["field"]["values"]), payload["triangles_shown"])
