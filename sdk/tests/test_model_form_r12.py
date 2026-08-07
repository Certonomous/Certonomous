"""Ruling R12's three mandatory conditions, pinned as behaviour.

R12 (docs/charters/SUPERVISOR_RULINGS.md, 2026-08-07): a canonical reference
grid may carry a model-form band above the mesh gate, provided (1) the band
artifact states the exemption with the failing number beside it, (2) the
exemption is scoped to model-form banding only and physics-gate paths refuse
it, (3) the exemption names its grid provenance. These tests fail the moment
any condition stops being enforced by ``sdk/scripts/model_form_batch.py``.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import model_form_batch as mfb  # noqa: E402

# The measured checkMesh verdict every family-N cell carries (the
# TMR-distributed coarse C-grid), exactly as mesh_verdict() builds it.
N_MESHV = {
    "max_non_ortho": 85.69872592,
    "max_skewness": 0.5068662781,
    "max_aspect_ratio": 20650841.43,
    "breaches": ["non-orthogonality 85.6987 > 70"],
}


class Condition1BandArtifactStatement(unittest.TestCase):
    """The exemption is stated on the band artifact, failing number beside."""

    def _n_record(self, converged: bool) -> dict:
        reasons, exemption = mfb.apply_mesh_gate(N_MESHV, "N")
        self.assertEqual(reasons, [])  # measured breach moved to exemption
        rec = {
            "cell_id": "N_a10_kOmegaSST", "group": "N_a10", "family": "N",
            "regime": "a10", "model": "kOmegaSST", "converged": converged,
            "excluded_reasons": [] if converged else ["residualControl not met"],
            "qoi": {"Cl": 1.1164336572, "Cd": 0.0044951723391},
            "core_min": 0.878, "mesh_gate_exemption": exemption,
        }
        return rec

    def test_statement_carries_the_failing_number(self):
        _, exemption = mfb.apply_mesh_gate(N_MESHV, "N")
        self.assertIsNotNone(exemption)
        statement = exemption["statement"]
        self.assertIn("85.70", statement)          # the failing number
        self.assertIn("70 deg hard gate", statement)  # beside the gate it fails
        self.assertIn("R12", statement)
        self.assertEqual(exemption["failing"],
                         ["max non-orthogonality 85.70 deg vs the "
                          "70 deg hard gate"])

    def test_band_group_carries_all_three_fields(self):
        band = mfb.build_band([self._n_record(converged=False)])
        grp = band["groups"][0]
        exemption = grp.get("mesh_gate_exemption")
        self.assertIsNotNone(
            exemption, "the band artifact must state the exemption (R12 c1)")
        for field in ("ruling", "scope", "grid_provenance", "failing",
                      "statement"):
            self.assertIn(field, exemption)
        self.assertIn("85.70", exemption["statement"])

    def test_band_markdown_prints_the_statement(self):
        band = mfb.build_band([self._n_record(converged=False)])
        text = mfb.band_markdown(band)
        self.assertIn("Mesh-gate exemption on this group (R12)", text)
        self.assertIn("85.70", text)
        self.assertIn("turbmodels.larc.nasa.gov", text)

    def test_exemption_survives_on_an_excluded_group(self):
        # The honest no-band outcome still states the exemption: a group
        # whose members fail residualControl carries the R12 statement even
        # though nothing banded.
        band = mfb.build_band([self._n_record(converged=False)])
        grp = band["groups"][0]
        self.assertEqual(grp["n_converged"], 0)
        self.assertIn("mesh_gate_exemption", grp)

    def test_unreadable_checkmesh_is_never_exempted(self):
        # No measured number, no statement, no exemption -- condition 1
        # cannot be met, so the cell stays excluded.
        meshv = {"max_non_ortho": None, "max_skewness": None,
                 "max_aspect_ratio": None,
                 "breaches": ["checkMesh non-orthogonality unreadable",
                              "checkMesh skewness unreadable"]}
        reasons, exemption = mfb.apply_mesh_gate(meshv, "N")
        self.assertIsNone(exemption)
        self.assertEqual(reasons, meshv["breaches"])


class Condition2BandingScopeOnly(unittest.TestCase):
    """The flag cannot be set on any physics-gate path."""

    def test_physics_gate_purpose_is_refused(self):
        for purpose in ("physics gate", "credential verdict",
                        "geometry study", ""):
            with self.assertRaises(RuntimeError) as ctx:
                mfb.mesh_gate_exemption("N", purpose)
            self.assertIn("REFUSED", str(ctx.exception))

    def test_banding_purpose_is_granted_for_n_only(self):
        info = mfb.mesh_gate_exemption("N", mfb.R12_BANDING_PURPOSE)
        self.assertIsNotNone(info)
        for family in ("P", "B"):
            self.assertIsNone(
                mfb.mesh_gate_exemption(family, mfb.R12_BANDING_PURPOSE))

    def test_non_exempt_families_keep_the_full_gate(self):
        # A P/B cell breaching the gate is excluded exactly as before.
        meshv = dict(N_MESHV)
        reasons, exemption = mfb.apply_mesh_gate(meshv, "P")
        self.assertIsNone(exemption)
        self.assertEqual(reasons, ["non-orthogonality 85.6987 > 70"])


class Condition3GridProvenance(unittest.TestCase):
    """The exemption names who published the grid, and where."""

    def test_provenance_names_publisher_and_location(self):
        info = mfb.MESH_GATE_EXEMPT_FAMILIES["N"]
        provenance = info["grid_provenance"]
        self.assertIn("NASA", provenance)
        self.assertIn("Turbulence Modeling Resource", provenance)
        self.assertIn("turbmodels.larc.nasa.gov", provenance)
        self.assertIn("n0012_113-33.p3dfmt", provenance)

    def test_registry_requires_all_three_fields(self):
        for field in mfb._R12_REQUIRED_FIELDS:
            self.assertTrue(mfb.MESH_GATE_EXEMPT_FAMILIES["N"].get(field))


if __name__ == "__main__":
    unittest.main()
