#!/usr/bin/env python3
"""Planted-value selftest for the F12 mesh-quality parse repair (CLAUDE.md rule 3).

WHAT THIS GUARDS. The F12 grading path reads mesh quality out of a ``checkMesh``
log through ``sdk.workflows.rae2822_case9.parse_check_mesh`` and gates on it in
``mesh_gate``. The F12-MESH successor pre-registration
(``verification/campaign/F12_MESH_SUCCESSOR_PREREGISTRATION.md`` section 4) records
a parse defect: on OpenFOAM v2606 the aspect ratio is printed on its OWN line,

    Max cell openness = 9.36526e-14 OK.
    Max aspect ratio = 805.199 OK.

but the reader matched only a COMBINED line (``startswith("Max cell openness")``
AND ``"aspect ratio" in s``), which never fires on v2606, so ``max_aspect_ratio``
was silently absent. The v2606 two-line form is real disk evidence:
``verification/runs/F12_runs/mesh_audit_2026-08-25/.../checkMesh`` logs print
``Max aspect ratio = 805.199 OK.`` on its own line.

THE CONTROL (rule 3 / a-zero-needs-a-live-planted-control). A reader that reports
zero (or ``None``) is evidence only once it is shown able to report a KNOWN
NON-ZERO through the SAME code path. So this selftest PLANTS a known aspect ratio
(and non-orthogonality and skewness) into a synthetic v2606-format log, reads them
back through ``parse_check_mesh``, and REFUSES (exit 2) if the reader cannot see
the plant. It also runs the plant in the REFUSING direction: a stand-in for the
pre-repair condition (combined-line only) is run against the same v2606 log and
MUST fail to see the planted aspect ratio, proving the control has teeth.

This is a selftest, not a grader: it produces no verdict on any run. The
cfd-supervisor owes the check-1 diff read of the ``parse_check_mesh`` repair
before its output counts (HARD CONSTRAINT of this lane's brief).
"""
from __future__ import annotations

import sys
from pathlib import Path

# import the live grading-path symbols by NAME (never by line number, L-492)
_SDK = Path(__file__).resolve().parents[4] / "sdk"
sys.path.insert(0, str(_SDK))
try:
    from workflows.rae2822_case9 import parse_check_mesh, mesh_gate, \
        MAX_NON_ORTHOGONALITY, MAX_SKEWNESS
except Exception as exc:  # absent module refuses, never degrades
    print(f"REFUSE (exit 2): cannot import the F12 grading path: {exc!r}")
    sys.exit(2)

# ---- planted controls -----------------------------------------------------
PLANT_AR = 805.199          # a known non-zero aspect ratio (v2606 disk value)
PLANT_NONORTHO = 72.542     # F12 fine-level breach, a known > 70 non-orthogonality
PLANT_SKEW = 0.827          # F12 measured skewness (passes its gate)


def synth_v2606_log(ar: float, nonortho: float, skew: float) -> str:
    """A minimal v2606-shaped checkMesh log with the three quantities on the
    lines checkMesh actually prints them on (aspect ratio STANDALONE)."""
    return (
        "Checking geometry...\n"
        "    Overall domain bounding box ...\n"
        "    Mesh has 2 solution directions ...\n"
        "    Mesh non-orthogonality Max: %s average: 4.11\n"
        "    Non-orthogonality check OK.\n"
        "    Max skewness = %s OK.\n"
        "    Max cell openness = 9.36526e-14 OK.\n"
        "    Max aspect ratio = %s OK.\n"
        "Mesh OK.\n"
    ) % (nonortho, skew, ar)


def _combined_line_only(text: str):
    """Stand-in for the PRE-REPAIR reader: matched aspect ratio only on a
    COMBINED 'Max cell openness ... aspect ratio ...' line. Reproduced here so
    the control can prove it fails to see the v2606 standalone line."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("Max cell openness") and "aspect ratio" in s:
            return float(s.split("=")[-1].split()[0].rstrip("."))
    return None


def refuse(msg: str) -> None:
    print(f"CONTROL FIRED / REFUSE (exit 2): {msg}")
    sys.exit(2)


def main() -> int:
    log = synth_v2606_log(PLANT_AR, PLANT_NONORTHO, PLANT_SKEW)

    # --- control (i): the repaired reader MUST see the planted non-zero AR ---
    parsed = parse_check_mesh(log)
    got_ar = parsed.get("max_aspect_ratio")
    if got_ar is None:
        refuse("planted aspect ratio 805.199 is UNSEEN by parse_check_mesh "
               "on a v2606 standalone-line log — the reader is blind, a zero "
               "from it would not be evidence.")
    if abs(got_ar - PLANT_AR) > 1e-6:
        refuse(f"planted aspect ratio read back as {got_ar}, expected {PLANT_AR}")
    print(f"CONTROL PASSED (i): planted aspect ratio {PLANT_AR} SEEN "
          f"through parse_check_mesh -> {got_ar}")

    # non-orthogonality and skewness also read back through the same reader
    if abs(parsed.get("max_non_orthogonality", -1) - PLANT_NONORTHO) > 1e-6:
        refuse(f"planted non-orthogonality {PLANT_NONORTHO} unseen "
               f"(got {parsed.get('max_non_orthogonality')})")
    if abs(parsed.get("max_skewness", -1) - PLANT_SKEW) > 1e-6:
        refuse(f"planted skewness {PLANT_SKEW} unseen "
               f"(got {parsed.get('max_skewness')})")
    print(f"CONTROL PASSED (i): non-orthogonality {PLANT_NONORTHO} and "
          f"skewness {PLANT_SKEW} SEEN through the same reader")

    # --- control (ii): the plant fires in the REFUSING direction against the
    #     pre-repair reader — it MUST be blind, else the control is toothless ---
    pre = _combined_line_only(log)
    if pre is not None:
        refuse("the pre-repair (combined-line-only) reader unexpectedly SAW the "
               "planted aspect ratio — the control cannot distinguish repaired "
               "from broken, so it is not evidence.")
    print("CONTROL PASSED (ii): the pre-repair combined-line-only reader is "
          "BLIND to the v2606 standalone aspect-ratio line (got None) — the "
          "repair is what makes the value visible.")

    # --- the gate consumes the parsed quality (nonortho breach is fail-closed) ---
    gate = mesh_gate(parsed)
    if gate["passed"]:
        refuse(f"mesh_gate PASSED a {PLANT_NONORTHO} deg non-orthogonality mesh "
               f"(> {MAX_NON_ORTHOGONALITY}) — the gate is not fail-closed.")
    print(f"GATE CHECK: mesh_gate correctly FAILS the planted mesh "
          f"(non-orthogonality {PLANT_NONORTHO} > {MAX_NON_ORTHOGONALITY}); "
          f"breaches={gate['breaches']}; advisory max_aspect_ratio="
          f"{gate['max_aspect_ratio']} (gated={gate['aspect_ratio_gated']})")

    print("\nSELFTEST PASS: parse_check_mesh reads the v2606 standalone aspect-"
          "ratio line, the planted-value control has teeth, and mesh_gate is "
          "fail-closed on the gated quantities.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
