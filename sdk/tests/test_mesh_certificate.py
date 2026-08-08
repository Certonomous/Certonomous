"""Mesh birth certificates (Mesh Standard v1.1 section 6; Verification
Charter v1.5 section 9): the certificate parses from real checkMesh records,
binds to exactly one mesh by hash, and every cache layer quarantines an
entry that lacks one.

The motivating specimens are the 2026-08-08 audit's: the A3 vcoarse pyHyp
mesh (born broken, entered a case three times with zero certificate checks)
and the bare-polyMesh cache class behind 400+ run directories.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chief_engineer import mesh_certificate as mc
from chief_engineer import docker_dafoam
from chief_engineer.docker_dafoam import DockerDAFoamEngineer
from workflows import shock_bench

REPO = Path(__file__).resolve().parents[2]
AUDIT_LOGS = (REPO / "demo-output" / "website" / "campaign"
              / "MESH_AUDIT_runs" / "2026-08-08")

CLEAN_LOG = """Mesh stats
    cells:            99840
Checking geometry...
    Max aspect ratio = 608.207 OK.
    Mesh non-orthogonality Max: 61.4938 average: 13.697
    Max skewness = 2.30655 OK.
Mesh OK.
"""

BROKEN_LOG = """Mesh stats
    cells:            24960
Checking geometry...
 ***High aspect ratio cells found, Max aspect ratio: 2.07741e+95, number of cells 25
 ***Zero or negative cell volume detected.  Minimum negative volume: -3.30275e-09, Number of negative volume cells: 23
    Mesh non-orthogonality Max: 135.318 average: 15.8916
 ***Number of non-orthogonality errors: 43.
 ***Error in face pyramids: 144 faces are incorrectly oriented.
 ***Max skewness = 55.378, 3 highly skew faces detected which may impair the quality of the results
Failed 5 mesh checks.
"""

FLAGGED_LOG = """Mesh stats
    cells:            816
Checking geometry...
 ***High aspect ratio cells found, Max aspect ratio: 74041.2, number of cells 12
    Mesh non-orthogonality Max: 0.0 average: 0.0
    Max skewness = 1.2e-13 OK.
Failed 1 mesh checks.
"""


def _mesh_dir(root: Path, points: bytes = b"fixture-points-v1\n") -> Path:
    poly = root / "polyMesh"
    poly.mkdir(parents=True, exist_ok=True)
    (poly / "points").write_bytes(points)
    (poly / "owner").write_bytes(b"owner\n")
    return root


class ParseCheckLogTests(unittest.TestCase):
    def test_a_clean_log_is_clean_with_its_numbers(self):
        payload = mc.parse_check_log(CLEAN_LOG)
        self.assertEqual(payload["verdict"], "clean")
        self.assertEqual(payload["cells"], 99840)
        self.assertEqual(payload["max_aspect_ratio"], 608.207)
        self.assertEqual(payload["max_non_orthogonality"], 61.4938)
        self.assertEqual(payload["max_skewness"], 2.30655)
        self.assertEqual(payload["hard_errors"], [])

    def test_the_born_broken_signature_is_broken(self):
        payload = mc.parse_check_log(BROKEN_LOG)
        self.assertEqual(payload["verdict"], "broken")
        self.assertIn("negative-volume cells", payload["hard_errors"])
        self.assertIn("wrong-oriented face pyramids", payload["hard_errors"])
        self.assertIn("non-orthogonality errors", payload["hard_errors"])
        self.assertIn("flagged aspect ratio", payload["hard_errors"])

    def test_the_nasa_grid_flag_is_flagged_not_broken(self):
        """The reference-grid family's high-AR-only signature is admissible
        (Mesh Standard 3.3: aspect ratio is never a lone rejection)."""
        payload = mc.parse_check_log(FLAGGED_LOG)
        self.assertEqual(payload["verdict"], "flagged")

    @unittest.skipUnless(AUDIT_LOGS.exists(), "audit logs not present")
    def test_the_retained_audit_specimens_parse_to_their_verdicts(self):
        broken = (AUDIT_LOGS
                  / "A3-onera-m6-adjoint-vcoarse__constant__polyMesh"
                    ".log.checkMesh")
        clean = (AUDIT_LOGS
                 / "A3-onera-m6-adjoint-coarse__constant__polyMesh"
                   ".log.checkMesh")
        payload = mc.parse_check_log(broken.read_text(errors="replace"))
        self.assertEqual(payload["verdict"], "broken")
        self.assertEqual(payload["cells"], 24960)
        payload = mc.parse_check_log(clean.read_text(errors="replace"))
        self.assertEqual(payload["verdict"], "clean")
        self.assertEqual(payload["cells"], 99840)


class CertificateRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="mesh-cert-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        _mesh_dir(self.root)

    def test_write_read_admit(self):
        written = mc.write_certificate(self.root, check_log_text=CLEAN_LOG,
                                       generator="fixture")
        self.assertIsNotNone(written)
        self.assertEqual(written["verdict"], "clean")
        self.assertEqual(written["points_sha256"],
                         mc.points_sha256(self.root / "polyMesh"))
        admitted, reason = mc.certificate_admits(self.root)
        self.assertTrue(admitted, reason)

    def test_no_certificate_is_quarantine(self):
        admitted, reason = mc.certificate_admits(self.root)
        self.assertFalse(admitted)
        self.assertIn("quarantined", reason)

    def test_a_certificate_never_travels_to_a_different_mesh(self):
        mc.write_certificate(self.root, check_log_text=CLEAN_LOG)
        (self.root / "polyMesh" / "points").write_bytes(b"different mesh\n")
        admitted, reason = mc.certificate_admits(self.root)
        self.assertFalse(admitted)
        self.assertIn("different mesh", reason)

    def test_born_broken_does_not_enter(self):
        mc.write_certificate(self.root, check_log_text=BROKEN_LOG)
        admitted, reason = mc.certificate_admits(self.root)
        self.assertFalse(admitted)
        self.assertIn("born broken", reason)

    def test_flagged_reference_grid_enters(self):
        mc.write_certificate(self.root, check_log_text=FLAGGED_LOG)
        admitted, verdict = mc.certificate_admits(self.root)
        self.assertTrue(admitted)
        self.assertEqual(verdict, "flagged")

    def test_a_failed_check_never_certifies(self):
        """A log with no cell count is a failed or absent check; writing a
        certificate from it would mint cleanliness out of nothing."""
        self.assertIsNone(mc.write_certificate(
            self.root, check_log_text="bash: checkMesh: command not found"))
        self.assertIsNone(mc.write_certificate(self.root))


class ShockBenchCacheTests(unittest.TestCase):
    """The module-level cache the unsteady workflows share: certificate at
    save, quarantine at lookup, certificate travels on restore."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mesh-cert-cache-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = self.tmp / "case"
        _mesh_dir(self.case / "constant")
        (self.case / "log.checkMesh").write_text(CLEAN_LOG)
        patcher = mock.patch.object(shock_bench, "MESH_CACHE_ROOT",
                                    str(self.tmp / "cache"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_save_writes_certificate_and_lookup_admits(self):
        shock_bench.save_mesh_to_cache(self.case, "fixture-key")
        cache = shock_bench._cache_dir(str(self.tmp / "cache"), "fixture-key")
        self.assertTrue((cache / mc.CERTIFICATE_NAME).exists())
        self.assertTrue((cache / "log.checkMesh").exists())
        self.assertTrue(shock_bench.cached_mesh_available("fixture-key"))

    def test_an_uncertified_entry_is_not_cached(self):
        """The pre-rule cache class: bare polyMesh, no record. Quarantined,
        so the workflow re-meshes once and re-enters certified."""
        shock_bench.save_mesh_to_cache(self.case, "fixture-key")
        cache = shock_bench._cache_dir(str(self.tmp / "cache"), "fixture-key")
        (cache / mc.CERTIFICATE_NAME).unlink()
        self.assertFalse(shock_bench.cached_mesh_available("fixture-key"))
        dest = self.tmp / "dest"
        dest.mkdir()
        self.assertFalse(shock_bench.restore_cached_mesh(dest, "fixture-key"))

    def test_a_broken_entry_is_not_cached(self):
        (self.case / "log.checkMesh").write_text(BROKEN_LOG)
        shock_bench.save_mesh_to_cache(self.case, "fixture-key")
        self.assertFalse(shock_bench.cached_mesh_available("fixture-key"))

    def test_restore_carries_the_certificate_into_the_case(self):
        shock_bench.save_mesh_to_cache(self.case, "fixture-key")
        dest = self.tmp / "dest"
        dest.mkdir()
        self.assertTrue(shock_bench.restore_cached_mesh(dest, "fixture-key"))
        self.assertTrue(
            (dest / "constant" / mc.CERTIFICATE_NAME).exists())


class DockerDafoamCacheTests(unittest.TestCase):
    """The pyHyp entry path -- the pathology's generator gets the same
    mechanics."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mesh-cert-dafoam-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        patcher = mock.patch.object(docker_dafoam, "MESH_CACHE_ROOT",
                                    self.tmp / "cache")
        patcher.start()
        self.addCleanup(patcher.stop)
        self.engine = DockerDAFoamEngineer.__new__(DockerDAFoamEngineer)
        self.engine.remote_case = self.tmp / "case"
        self.engine._cached_cell_count = "24960"
        _mesh_dir(self.engine.remote_case / "constant")

    def test_save_certifies_and_restore_asserts(self):
        (self.engine.remote_case / "log.checkMesh").write_text(CLEAN_LOG)
        self.engine.save_mesh_to_cache("m6-fixture")
        cache = self.engine._mesh_cache_dir("m6-fixture")
        self.assertTrue((cache / mc.CERTIFICATE_NAME).exists())
        shutil.rmtree(self.engine.remote_case / "constant" / "polyMesh")
        self.assertTrue(self.engine.restore_cached_mesh("m6-fixture"))
        self.assertTrue((self.engine.remote_case / "constant"
                         / mc.CERTIFICATE_NAME).exists())

    def test_the_a3_pathology_is_unreachable_through_the_cache(self):
        """A born-broken pyHyp mesh saves with a broken certificate and can
        never restore -- the A3 vcoarse failure mode (same broken mesh,
        three case reconstructions, zero certificate checks) closed."""
        (self.engine.remote_case / "log.checkMesh").write_text(BROKEN_LOG)
        self.engine.save_mesh_to_cache("m6-vcoarse-fixture")
        cache = self.engine._mesh_cache_dir("m6-vcoarse-fixture")
        certificate = json.loads(
            (cache / mc.CERTIFICATE_NAME).read_text())
        self.assertEqual(certificate["verdict"], "broken")
        self.assertFalse(self.engine.restore_cached_mesh("m6-vcoarse-fixture"))

    def test_a_pre_rule_bare_entry_is_a_cold_miss(self):
        (self.engine.remote_case / "log.checkMesh").write_text(CLEAN_LOG)
        self.engine.save_mesh_to_cache("bare-fixture")
        cache = self.engine._mesh_cache_dir("bare-fixture")
        (cache / mc.CERTIFICATE_NAME).unlink()
        self.assertFalse(self.engine.restore_cached_mesh("bare-fixture"))


class ModelFormEntryRefusalTests(unittest.TestCase):
    """The batch refuses the launch instead of excluding the cell after the
    solve has spent its wall time."""

    @classmethod
    def setUpClass(cls):
        import importlib
        import sys
        scripts = str(REPO / "sdk" / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        cls.batch = importlib.import_module("model_form_batch")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mesh-cert-mfb-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_no_record_refuses_the_launch(self):
        with self.assertRaises(RuntimeError) as caught:
            self.batch.assert_mesh_certified_at_entry(
                self.tmp, "H", "H_fixture")
        self.assertIn("uncertified mesh", str(caught.exception))

    def test_a_clean_record_launches(self):
        (self.tmp / "log.checkMesh").write_text(CLEAN_LOG)
        self.batch.assert_mesh_certified_at_entry(self.tmp, "H", "H_fixture")

    def test_a_breaching_record_refuses_before_the_solve(self):
        (self.tmp / "log.checkMesh").write_text(BROKEN_LOG)
        with self.assertRaises(RuntimeError) as caught:
            self.batch.assert_mesh_certified_at_entry(
                self.tmp, "H", "H_fixture")
        self.assertIn("refused at entry", str(caught.exception))

    def test_the_r12_family_exemption_is_preserved(self):
        """Family N's TMR C-grid breaches non-orthogonality under ruling
        R12; the pre-launch gate must not refuse what the ruling admits."""
        (self.tmp / "log.checkMesh").write_text(
            "    cells:            3729\n"
            "    Mesh non-orthogonality Max: 85.70 average: 12.0\n"
            "    Max skewness = 1.2 OK.\n")
        self.batch.assert_mesh_certified_at_entry(self.tmp, "N", "N_fixture")

    def test_the_fallback_location_is_honoured(self):
        fallback = self.tmp / "out"
        fallback.mkdir()
        (fallback / "log.checkMesh").write_text(CLEAN_LOG)
        self.batch.assert_mesh_certified_at_entry(
            self.tmp / "absent", "H", "H_fixture", fallback=fallback)


if __name__ == "__main__":
    unittest.main()
