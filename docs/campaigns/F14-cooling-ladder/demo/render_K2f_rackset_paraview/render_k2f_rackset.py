#!/usr/bin/env python3
"""render_k2f_rackset.py -- ParaView renders of the K2f/K2g rack-row set, for
Sanaa's 2026-09-12 ~20:30Z directive. RUN WITH pvpython.

    xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/render_K2f_rackset_paraview/render_k2f_rackset.py

HER DIRECTIVE, BYTE-EXACT (docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md)
------------------------------------------------------------------------------
    "whenever a run completes, i want the paraview visualization of its mesh
     saved. (when the run is complete). The paraview should show the coarse mesh
     (or meidum mesh if the coarse isnt converged). But all fields should be
     stored as the fine mesh result fields (whenever we have it)."

SO: THE MESH PICTURE IS THE COARSE LEVEL'S. THE FIELD PICTURES ARE THE FINEST
COMPLETED LEVEL'S. NOTHING IS INTERPOLATED BETWEEN THEM.
-----------------------------------------------------------------------------
Mesh from ``K2f_L1`` (58,368 cells). Fields from ``K2f_L3`` (664,848 cells) at
its last written time. Those are two different meshes, and a SINGLE image
claiming to be the coarse mesh carrying the fine fields would require resampling
one onto the other -- which manufactures values no solver wrote. This script
therefore renders each from the case that produced it and says so in every
caption, which is the honest reading of her instruction and the only one that
does not fabricate.

WHY COARSE AND NOT MEDIUM -- A MEASUREMENT, NOT A DEFAULT
---------------------------------------------------------
Her parenthetical allows medium "if the coarse isnt converged". ``K2f_L1`` IS
converged: final-300 per-iteration residual peak-to-peak **5.05e-11** on Ux, and
``DP_module`` monotone across all six checkpoints (0 sign changes, p2p
**3.11e-04** m2/s2). ``K2f_L2`` WOULD HAVE BEEN THE WRONG CHOICE on the same
evidence -- it limit-cycles at a 1e-4 residual floor (Ux 8 sign changes over the
final 300) and its ``DP_module`` TURNS (1 sign change, p2p 3.70e-03). Recorded in
``K2h_PREREGISTRATION.md`` section 2.

THE THING THIS FILE EXISTS TO PREVENT
--------------------------------------
**THE FIELDS BEING RENDERED CARRY NO GRADED VERDICT.** ``K2f_L3`` ran 803 of a
registered 2000 iterations and was stopped by its own registered stop rule R4 on
coherent oscillation in the graded quantity at 2.85x the registered
``PLATEAU_TOL``. It FAILS standing rule 4 (clause 3: last written time 803 !=
endTime 2000; clause 5: 803 ``ExecutionTime`` lines, expected 2000) and its
frozen comparator REFUSED IT AT EXIT 2. Its ``DP_module`` of 28.0521393 m2/s2
happens to lie inside the registered band -- **which is precisely what makes a
picture of it dangerous.** A render that looks like a result while carrying
ungraded fields is the most filmable form of the error this lab exists to refuse.

That is not left to whoever writes the caption. ``demo3d_render_common.CASE_FACTS``
records ``allowed_verdicts = {"NOT A RESULT"}`` for BOTH cases, and
``assert_stamp`` REFUSES any stamp carrying ``PASS`` or ``GATE REACHED`` -- before
a single pixel is rendered.

RE-POINTED, NOT REWRITTEN. Every figure function, the scratch-case reader, the
colour locking, the screenshot writer and the run-tree fingerprint come from the
committed ``render_K2bU3R3_paraview/render_k2bU3R3.py`` and
``scripts/demo3d_render_common.py``. This file rebinds that module's case-scoped
globals and calls its functions; it reimplements none of them. The two cases
share a geometry family -- the identical 3.6 x 3.5 x 2.7 m room, verified from
both cases' ``log.checkMesh`` bounding boxes -- which is what makes the re-point
legitimate rather than convenient.

NO SOLVER IS RUN AND NO RUN TREE IS WRITTEN. Fields are read through a scratch
case of symlinks; both graded trees are fingerprinted before and PROVED unchanged
after.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder",
                                "demo", "render_K2bU3R3_paraview"))

import demo3d_render_common as C          # noqa: E402
import render_k2bU3R3 as K2B              # noqa: E402  the committed renderer, re-pointed

OUT = os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder", "demo",
                   "figures_K2f_rackset")

MESH_CASE, MESH_END = "K2f_L1", "3000"
FIELD_CASE, FIELD_END = "K2f_L3", "803"

UNGRADED = ("fields NOT rule-4 complete ; no graded verdict ; NOT A RESULT")


def _repoint(case, end, stamp, geom):
    """Rebind the committed renderer's case-scoped globals. Explicit, and
    asserted: a silent re-point that missed one global would caption a figure
    with another case's verdict."""
    K2B.CASE, K2B.END, K2B.STAMP, K2B.GEOM = case, end, stamp, geom
    assert K2B.CASE == case and K2B.END == end and K2B.STAMP == stamp
    C.assert_stamp(stamp, case)           # REFUSES before any pixel is rendered
    C.announce(f"  re-pointed to {case} at t = {end}; stamp accepted: {stamp}")


def main() -> int:
    C.announce("=" * 74)
    C.announce("K2f rack-set renders -- COARSE mesh (L1) + FINEST fields (L3 at 803)")
    C.announce("=" * 74)
    version = C.assert_paraview_version()
    C.announce(f"  ParaView {version} (pinned {C.REQUIRED_PARAVIEW})")

    mesh_dir = C.facts(MESH_CASE)["case_dir"]
    field_dir = C.facts(FIELD_CASE)["case_dir"]
    before_mesh = C.run_tree_fingerprint(mesh_dir)
    before_field = C.run_tree_fingerprint(field_dir)

    os.makedirs(OUT, exist_ok=True)
    total, root = 0, None

    # ---- 1. THE MESH, from the COARSE level, which is the converged one ------
    try:
        _repoint(MESH_CASE, MESH_END,
                 f"{MESH_CASE} ; 58368 cells ; COARSE level mesh ; NOT A RESULT",
                 "Room 3.6 x 3.5 x 2.7 m ; 4 racks ; MESH of the COARSE level "
                 "(converged: residual p2p 5.05e-11, DP monotone)")
        reader, root, n = C.open_case(MESH_CASE, ["T", "U"], [MESH_END])
        C.announce(f"  mesh source {MESH_CASE}: {n:,} cells")
        total += K2B.fig_mesh(reader, os.path.join(OUT, "K2f_L1_coarse_mesh.png"))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)
        root = None

    # ---- 2. THE FIELDS, from the FINEST completed level ----------------------
    try:
        _repoint(FIELD_CASE, FIELD_END,
                 f"{FIELD_CASE} ; 664848 cells ; t=803 of endTime 2000 ; "
                 f"NOT A RESULT",
                 "Room 3.6 x 3.5 x 2.7 m ; 4 racks ; FINE-level fields ; "
                 "STOPPED at 803 by stop rule R4 ; " + UNGRADED)
        reader, root, n = C.open_case(FIELD_CASE, ["T", "U"], [FIELD_END])
        C.announce(f"  field source {FIELD_CASE}: {n:,} cells at t = {FIELD_END}")
        total += K2B.fig_aisles(reader, os.path.join(OUT, "K2f_L3_temperature_field.png"))
        total += K2B.fig_streamlines(reader, os.path.join(OUT, "K2f_L3_recirculation.png"))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)

    C.assert_run_tree_untouched(mesh_dir, before_mesh)
    C.assert_run_tree_untouched(field_dir, before_field)
    C.announce(f"  BOTH run trees PROVED unchanged: {mesh_dir} ; {field_dir}")
    C.announce(f"  {total:,} bytes written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
