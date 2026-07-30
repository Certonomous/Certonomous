#!/usr/bin/env python3
"""Certonomous laptop replay console -- the offline backup for the shoot.

WHAT THIS IS, PLAINLY
---------------------
This starts the two demo surfaces on THIS machine, with no internet and no
EC2 box:

    control room   http://localhost:8765   -- replays recorded missions
    static site    http://localhost:8080   -- closure.html, benchmarks.html

WHAT IT CANNOT DO, AND WHY
--------------------------
It cannot LAUNCH a new mission. That is a hard limit, not a setting.

Measured on 2026-07-30 by tracing every process the four filmed acts spawn
(strace -f -e trace=execve):

  * the airliner and Monte-Carlo race acts executed the real VSPAERO binary
    102 times between them -- they are live solves, not replays;
  * the NASA hump and B-52 acts executed OpenFOAM utilities (checkMesh,
    decomposePar, foamToVTK, surfaceTransformPoints) AND compiled C++ at
    run time through OpenFOAM's dynamicCode path (16 g++ invocations,
    `wmake -s libso`).

None of that exists on a laptop with only Python installed. So rather than
let a prompt fail confusingly on camera, this console refuses the launch
endpoint with a plain message. Everything already recorded replays perfectly,
because a recorded mission is just JSON and PNG files on disk.

Nothing here is dressed up as a live measurement: a replay is announced as a
replay, and the numbers shown are the numbers the real run produced.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent

# Point the control room at the bundle's own copies BEFORE importing it --
# chief_engineer.server reads these at import time.
os.environ.setdefault("CERTONOMOUS_OUTPUT", str(BUNDLE / "mission-output"))
os.environ.setdefault("CHIEF_ENGINEER_STATE_DIR", str(BUNDLE / "mission-state"))
os.environ.setdefault("CERTONOMOUS_CREDENTIALS",
                      str(BUNDLE / "models" / "curriculum" / "results"))
sys.path.insert(0, str(BUNDLE / "sdk"))

from chief_engineer import server as cr  # noqa: E402

REFUSAL = (
    "This is the offline laptop console: it replays the recorded missions, "
    "it does not launch new ones. Launching needs the VSPAERO and OpenFOAM "
    "toolchains, which live on the lab box. Open a recorded act from the "
    "list instead."
)


def _snapshot(name: str):
    """A panel captured at build time with the whole repo present.

    The credentials wall and the lab-stats header are DERIVED at serve time
    from data far too large to ship (a 97 MB ledger; the full refinement
    ladders). Re-deriving them from a partial copy does not merely blank
    them -- it silently re-grades bodies UPWARD, so the laptop would claim
    more than the lab box. Serving the captured values keeps the two honest
    and identical.
    """
    path = BUNDLE / "snapshot" / f"{name}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


class ReplayHandler(cr.Handler):
    """The control-room handler with the launch endpoints honestly closed
    and the two derived panels served from the build-time snapshot."""

    def do_GET(self) -> None:  # noqa: D102
        from urllib.parse import urlparse

        path = urlparse(self.path).path
        if path == "/api/credentials":
            cards = _snapshot("credentials")
            if cards is not None:
                self._write_json(200, cards)
                return
        elif path == "/api/lab-stats":
            stats = _snapshot("lab_stats")
            if stats:
                self._write_json(200, stats)
                return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: D102
        from urllib.parse import urlparse

        path = urlparse(self.path).path
        if path in ("/api/missions", "/api/agenda/approve"):
            self._write_json(503, {"error": REFUSAL})
            return
        super().do_POST()


class _StrictServer(ThreadingHTTPServer):
    """A server that refuses to share a port.

    ``allow_reuse_address`` is ON by default in the standard library, and this
    lab has been bitten by it: a second server bound the same port beside a
    stale one, and the stale process answered the browser. On a laptop the
    right behaviour is to notice the port is taken and move up one.
    """

    allow_reuse_address = False


def _free_port(preferred: int, limit: int = 20) -> int:
    """The first genuinely free port at or above ``preferred``.

    The probe deliberately does NOT set SO_REUSEADDR. With it set, this bind
    succeeds even when another server already holds the port on 0.0.0.0 (the
    standard library sets SO_REUSEADDR on its servers), and the result is two
    listeners on one port with the wrong one answering.
    """
    for port in range(preferred, preferred + limit):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit(f"No free port between {preferred} and {preferred + limit}.")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    site_dir = BUNDLE / "site"
    control_port = _free_port(int(os.environ.get("CHIEF_ENGINEER_PORT", "8765")))
    site_port = _free_port(int(os.environ.get("CERTONOMOUS_SITE_PORT", "8080")))

    cr._rehydrate_missions()
    missions = len(cr._missions)

    # Bind to loopback only: this is a laptop, nothing should be exposed to
    # the room's wifi.
    control = _StrictServer(("127.0.0.1", control_port), ReplayHandler)
    site = _StrictServer(
        ("127.0.0.1", site_port),
        partial(SimpleHTTPRequestHandler, directory=str(site_dir)))

    for srv in (control, site):
        threading.Thread(target=srv.serve_forever, daemon=True).start()

    bar = "=" * 62
    print(bar)
    print("  CERTONOMOUS -- offline laptop console")
    print(bar)
    print(f"  Control room (replays)  http://localhost:{control_port}")
    print(f"  Static site             http://localhost:{site_port}/closure.html")
    print(f"  Recorded missions ready {missions}")
    print(bar)
    print("  Replay only. New missions cannot be launched here -- they need")
    print("  the VSPAERO and OpenFOAM toolchains on the lab box.")
    print("  Press Ctrl+C to stop.")
    print(bar, flush=True)

    if os.environ.get("CERTONOMOUS_NO_BROWSER") != "1":
        try:
            webbrowser.open(f"http://localhost:{control_port}")
        except Exception:
            pass

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
