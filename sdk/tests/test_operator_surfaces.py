"""One way in: the operator's surfaces come through the control room's port.

The bodies were reachable only through the static site, on a second port.
During filming that port was shut while the control room was open, so an act
that wanted an attached body could not get one and nothing said which of the
two doors had closed. These tests hold the single door open: the copy set is
listed and downloadable byte for byte through the control room's own port,
the staging area is not served, and what the copy set does not carry is named
rather than left silent.
"""
from __future__ import annotations

import http.client
import json
import os
import shutil
import tempfile
import threading
import unittest
from pathlib import Path

from chief_engineer import server as server_mod

_ENV_KEYS = ("CERTONOMOUS_SURFACES", "CERTONOMOUS_STAGING")


class OperatorSurfaces(unittest.TestCase):

    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in _ENV_KEYS}
        self.addCleanup(self._restore)
        self.root = Path(tempfile.mkdtemp(prefix="surfaces-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.copy_set = self.root / "copy-set"
        self.staging = self.root / "staging"
        self.copy_set.mkdir()
        self.staging.mkdir()
        # A copy set of two bodies, plus a note that is not a surface.
        self.b52 = b"solid b52\nfacet normal 0 0 1\nendsolid b52\n"
        (self.copy_set / "b52.stl").write_bytes(self.b52)
        (self.copy_set / "motorBike.obj").write_bytes(b"o bike\nv 0 0 0\n")
        (self.copy_set / "README.md").write_text("not a surface", "utf-8")
        # The staging area carries one body the copy set does not.
        (self.staging / "b52.stl").write_bytes(b"an upload overwrote this")
        (self.staging / "onera_m6_wing.stl").write_bytes(b"solid m6\n")
        os.environ["CERTONOMOUS_SURFACES"] = str(self.copy_set)
        os.environ["CERTONOMOUS_STAGING"] = str(self.staging)

        self.httpd = server_mod.ThreadingHTTPServer(
            ("127.0.0.1", 0), server_mod.Handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.port = self.httpd.server_address[1]

    def _restore(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _get(self, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request("GET", path)
        response = conn.getresponse()
        body = response.read()
        conn.close()
        return response.status, response.getheaders(), body

    def test_the_copy_set_is_listed_with_its_digests(self):
        status, _, body = self._get("/api/surfaces")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        names = [entry["name"] for entry in payload["surfaces"]]
        self.assertEqual(names, ["b52.stl", "motorBike.obj"])
        self.assertNotIn("README.md", names)
        entry = payload["surfaces"][0]
        self.assertEqual(entry["bytes"], len(self.b52))
        self.assertEqual(entry["url"], "/api/surfaces/b52.stl")
        self.assertEqual(len(entry["sha256"]), 64)

    def test_what_the_copy_set_does_not_carry_is_named(self):
        _, _, body = self._get("/api/surfaces")
        payload = json.loads(body)
        self.assertEqual(payload["staged_but_not_downloadable"],
                         ["onera_m6_wing.stl"])

    def test_a_surface_downloads_byte_for_byte_as_an_attachment(self):
        status, headers, body = self._get("/api/surfaces/b52.stl")
        self.assertEqual(status, 200)
        # The copy set, not the staging area an upload has overwritten.
        self.assertEqual(body, self.b52)
        head = {k.lower(): v for k, v in headers}
        self.assertEqual(head["content-type"], "application/octet-stream")
        self.assertIn("b52.stl", head["content-disposition"])
        self.assertEqual(head["content-length"], str(len(self.b52)))

    def test_the_staging_area_is_not_served_through_this_door(self):
        _, _, body = self._get("/api/surfaces/onera_m6_wing.stl")
        self.assertIn(b"unknown surface", body)

    def test_traversal_and_non_surfaces_are_refused(self):
        for path in ("/api/surfaces/../../../etc/passwd",
                     "/api/surfaces/README.md",
                     "/api/surfaces/absent.stl",
                     "/api/surfaces/b52.stl/extra"):
            status, _, _ = self._get(path)
            self.assertEqual(status, 404, path)

    def test_the_mission_surface_endpoint_still_answers_separately(self):
        # /api/surface/<dir>/<file> serves a mission-produced viewport
        # payload and is a different endpoint from /api/surfaces/<file>.
        # Adding the second must not shadow the first.
        status, _, _ = self._get("/api/surface/nowhere/none.stl")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
