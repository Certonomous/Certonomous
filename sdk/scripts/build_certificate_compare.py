"""Old-vs-new certificate PDFs for the B-52, side by side for sign-off.

Renders the CURRENT certificate (``build_certificate``) and the REDESIGN
proposal (``build_certificate_v2``) for the same B-52 record into
demo-output/website/certificates/, plus a README stating the substitution and
that the redesign is NOT the default until signed off.

Substitution note: the requested mission M-C13431539C15 is not in this repo's
records, and no B-52 geometry-study mission is persisted here either, so the
record below is built from the project's DOCUMENTED real B-52 solve (docs/HANDOFF
"What's built and validated": b52.stl, 193,880 cells, Cd 0.0471, ~8 core-min,
TREND ONLY, Aref = measured silhouette 601 m^2). Re-run against a live B-52
mission when one exists on this branch.

    python sdk/scripts/build_certificate_compare.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SDK = Path(__file__).resolve().parents[1]
if str(_SDK) not in sys.path:
    sys.path.insert(0, str(_SDK))

from chief_engineer import certificate  # noqa: E402

_OUT = _SDK.parent / "demo-output" / "website" / "certificates"

# Documented real B-52 solve (see module docstring). Mission slug substituted.
_MISSION_ID = "geometry-study-b52"
_ISSUED = "2026-07-21T18:04:00Z"
_OBJECTIVE = "Solve the drag on this airframe and paint the surface pressure field."
_SOLVER = "OpenFOAM simpleFoam · k-omega SST, steady RANS"

_REPORT_DOC = {
    "results": [
        {"quantity": "Drag coefficient", "value": "0.0471", "envelope": "0.0018",
         "tier": "TREND ONLY",
         "reason": "steady RANS on a watertight airframe with no in-regime "
                   "experimental anchor for this configuration; the reference area "
                   "is the measured silhouette (601 m^2), not the published wing area"},
        {"quantity": "Lift coefficient", "value": "0.0192", "envelope": "0.0041",
         "tier": "TREND ONLY", "reason": ""},
        {"quantity": "Mesh", "value": "193,880 cells",
         "envelope": "max non-orthogonality 62, max skewness 3.1",
         "tier": "TREND ONLY", "reason": ""},
    ],
    "compute": {"cells": 193880, "spent_core_minutes": 8.0, "full_fidelity": False},
    "uncertainty": [
        "Scale is stated (48.5 m reference length), not inferred.",
        "Single mesh: a two-mesh probe would give a grid difference, not a verified GCI.",
        "Fully-turbulent RANS with no transition model; Aref is the silhouette.",
    ],
}

_CHANNELS = [
    {"name": "Input", "value": "48.5 m ref. length", "quantified": True,
     "note": "reference length stated, not inferred; freestream at cruise"},
    {"name": "Numerical", "value": "grid difference", "quantified": False,
     "note": "single mesh; a two-mesh probe yields a grid difference, not a "
             "verified GCI (Eca & Hoekstra)"},
    {"name": "Model form", "value": "fully-turbulent RANS", "quantified": False,
     "note": "k-omega SST, no transition model; Aref is the measured silhouette, "
             "so Cd is not directly comparable to published book values"},
]

_README = """# Certificate redesign — old vs new (B-52), for sign-off

Two renders of the SAME B-52 record:

- `b52-certificate-current.pdf` — the current default (`build_certificate`).
- `b52-certificate-redesign.pdf` — the redesign proposal (`build_certificate_v2`).

**The redesign is NOT the default.** `build_certificate` is untouched; the new
layout is an additive `build_certificate_v2` and becomes default only on
sign-off.

## What changed in the redesign
- Serif/sans pairing; generous margins.
- Masthead carries a human **Certificate No. C-2026-NNNN** (deterministic from
  the seal); the mission slug is demoted to the provenance footer, never the title.
- Subject block leads with the geometry **display name** ("B-52
  Stratofortress-class airframe"); the filename is small metadata.
- Result block: value ± 95% CI with a **fidelity chip** (SOLVER-BACKED /
  RESEARCH MODEL / VALIDATED).
- Complete **three-channel** V&V-20 uncertainty table.
- Provenance footer: SHA-256 seal (truncated + full), mission id small,
  "Reproducible from the sealed evidence bundle".

## Substitution note
Requested mission **M-C13431539C15** is not in this repo's records, and no B-52
geometry-study mission is persisted here. The record is built from the project's
DOCUMENTED real B-52 solve (193,880 cells, Cd 0.0471, ~8 core-min, TREND ONLY).
Regenerate against a live B-52 mission when one exists on this branch.
"""


def main() -> int:
    _OUT.mkdir(parents=True, exist_ok=True)
    old = certificate.build_certificate(
        _REPORT_DOC, out_path=_OUT / "b52-certificate-current.pdf",
        geometry="b52", objective=_OBJECTIVE, mission_id=_MISSION_ID,
        issued_utc=_ISSUED, channels=_CHANNELS)
    new = certificate.build_certificate_v2(
        _REPORT_DOC, out_path=_OUT / "b52-certificate-redesign.pdf",
        geometry="b52", objective=_OBJECTIVE, mission_id=_MISSION_ID,
        issued_utc=_ISSUED, channels=_CHANNELS,
        source_filename="b52.stl", solver=_SOLVER)
    (_OUT / "README.md").write_text(_README, encoding="utf-8")
    print(f"[cert] current  -> {old['path']}")
    print(f"[cert] redesign -> {new['path']}  ({new['certificate_no']}, {new['fidelity']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
