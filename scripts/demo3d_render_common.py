"""Shared machinery for rendering the lab's GENUINELY THREE-DIMENSIONAL solved
cases for the demo. REFUSES rather than renders.

WHY THIS FILE EXISTS AT ALL
---------------------------
Every rendered demo asset the lab owned before this module was Act A, and Act A
is a FIVE-DEGREE AXISYMMETRIC WEDGE. The two cases this module serves --
T18_CU_f (3-D transient conduction, 512,000 cells) and K2bU3R3_D59 (a 3-D data
centre rack row, 137,000 cells) -- are the lab's only genuinely 3-D solved cases
whose verdicts permit them to be shown as verified results, and neither had a
single rendered asset. This module is what they share.

It is a deliberate sibling of
``docs/campaigns/T-family/demo/render_actA_paraview/_actA_render_common.py``
and inherits that file's three refusals verbatim in intent:

1. **NOTHING IS EVER WRITTEN INTO A GRADED RUN TREE.** Not a ``.foam`` file, not
   a symlink, not a temp file, not a ``touch``. Both cases are under the strict
   completion rule and its age guard, whose whole content is that every field at
   ``endTime`` is newer than the case's own ``0/T``. A render tool dropping a
   file into the case directory invites exactly the "is this still the artefact
   that ran" question the guard exists to answer. :func:`materialise_case`
   builds a SCRATCH case of symlinks; :func:`assert_run_tree_untouched` proves
   afterwards that the case directory did not move.

2. **THE MESH MUST BE THE CASE'S MESH, AND THAT IS MEASURED.** Every reader
   asserts its loaded cell count against the count recorded for that case and
   refuses on mismatch. A render that quietly loaded a different mesh looks
   entirely plausible and is wrong.

3. **A RENDER THAT SILENTLY PRODUCES AN EMPTY OR STALE IMAGE IS A FALSE ZERO.**
   Every write goes through :func:`save_screenshot`, which refuses a file that
   does not appear, is suspiciously small, or is a leftover from a previous run.

AND THE REFUSAL THIS MODULE ADDS, WHICH ACT A DID NOT NEED
----------------------------------------------------------
**THE VERDICT WORD IS MECHANISED, NOT REMEMBERED.** Act A's two cases carried
one verdict between them. These two do not, and the difference is load-bearing:

* T18's graded rows G1, G2 and G3 are ``PASS``. The rung's registered ceiling is
  ``GATE REACHED`` and the registration says so in terms -- the reference is an
  EXACT analytic series, so the rung scores V and never P.
* K2bU3R3 is ``GATE REACHED`` **and never ``PASS``**. It is a survives/damps
  DISCRIMINATOR gate; ``PASS`` is a value-in-band term that gate does not
  possess. The word was corrected from ``PASS`` on 2026-09-09 under
  VERIFICATION_CHARTER section 2. A figure captioned ``PASS`` for K2bU3R3 would
  re-introduce precisely the defect that correction removed.

So the allowed verdict words are declared PER CASE in :data:`CASE_FACTS` and
:func:`assert_stamp` refuses a stamp that carries a verdict word the case does
not own, that carries no verdict word at all, or that softens one with prose.
A human being careful is not a control; a refusal is.

Nothing here chooses a number. Cell counts, solvers, geometry and verdicts are
read from :data:`CASE_FACTS`, whose every entry cites the artifact it came from.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

# ParaView 5.11.2, pinned exactly as Act A pins it. A render that moves with the
# reader version is not reproducible, and the version is asserted, not hoped for.
REQUIRED_PARAVIEW = "5.11"

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MIN_IMAGE_BYTES = 5000


class RenderRefusal(RuntimeError):
    """Raised instead of producing a picture nobody can defend."""


def refuse(message: str):
    raise RenderRefusal(message)


# ---------------------------------------------------------------------------
# THE FIXED VERDICT VOCABULARY (CLAUDE.md rule 1)
# ---------------------------------------------------------------------------

#: The complete vocabulary. No synonyms, no additions.
FIXED_VOCABULARY = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
                    "BLOCKED", "PENDING")

#: Prose that SOFTENS or UPGRADES a verdict. Every one of these has a specific
#: reason to be banned on these two figures:
#:
#: * "validated" / "validation" -- T18 is graded against an ANALYTIC SERIES, not
#:   an experiment. Calling it validation claims a comparison never made.
#: * "verified against experiment" -- same defect, stated outright.
#: * "excellent/good agreement" -- an adjective standing in for an interval.
#:   CLAUDE.md rule 1: honesty is carried by the value and its interval, never
#:   by adjectives.
#: * "converged"/"accurate"/"proves" as free prose -- upgrades a gated statement.
BANNED_STAMP_PROSE = {
    "validated": "T18 is graded against an ANALYTIC SERIES and K2bU3R3 against a "
                 "pre-registered discriminator threshold; neither is a comparison "
                 "with experiment, so neither is validation",
    "validation": "same as 'validated' -- no experimental comparison exists here",
    "verified against experiment": "no experimental comparison exists for either case",
    "excellent agreement": "an adjective standing in for an interval (rule 1)",
    "good agreement": "an adjective standing in for an interval (rule 1)",
    "close agreement": "an adjective standing in for an interval (rule 1)",
    "proves": "a render does not prove anything; the gate record does",
    "confirms": "a render does not confirm anything; the gate record does",
    "highly accurate": "an adjective standing in for an interval (rule 1)",
    "successfully": "hedging prose around a verdict word (rule 1)",
}

#: Glyphs MEASURED to be dropped by ParaView 5.11.2's caption font on this box.
#: Inherited from Act A's measurement 2026-09-01, re-asserted by the self-test.
KNOWN_DROPPED_GLYPHS = {
    "|": "rendered as nothing in ParaView 5.11.2 captions on this box, 2026-09-01",
}

#: Act A's measured-renderable set. Note what is ABSENT and must not be used:
#: no caret (so an 80-cubed mesh is written "80 x 80 x 80", never "80^3"),
#: no percent, no asterisk, no degree sign.
SAFE_CAPTION_CHARS = set(
    " (),+-./:;=_"
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
)


# ---------------------------------------------------------------------------
# THE RECORDED FACTS. Every field cites the artifact it was read from.
# A render never types a number this table does not carry.
# ---------------------------------------------------------------------------

CASE_FACTS = {
    # ---------------------------------------------------------------------
    # THE SUBOFF A1h FULL-DOMAIN DRIFT SWEEP, added 2026-09-13. BOTH ENTRIES OWN
    # EXACTLY ONE VERDICT WORD, "PENDING": all seven sweep points were still
    # running when these rows were written (about 2,450 to 2,640 of a registered
    # endTime 3000), and the registration forbids a derivative, a neutral point
    # or any gate verdict until the whole sweep lands. assert_stamp therefore
    # refuses a PASS, a GATE FAIL or a NOT A RESULT on any figure of this act.
    "SUBOFF_L1M_BETA_P00": {
        "case_dir": os.path.join(REPO, "verification", "runs", "navier_class",
                                 "SUBOFF_A1H_DRIFT", "L1M_SWEEP", "BETA_p00"),
        "cells": 6537226,                # constant/polyMesh/owner note: nCells:6537226
        "mesh_words": "6537226 cells, the mirrored L1 full domain",
        "solver": "simpleFoam",          # SOLVE_MANIFEST.json
        "end_time": "3000",              # SOLVE_MANIFEST.json endTime; NOT reached yet
        "fields": ("p", "U", "k", "omega", "nut"),
        "allowed_verdicts": {"PENDING"},
        "verdict_stamp": "PENDING",
        "source": "the sweep is live; no grading record exists yet",
    },
    "SUBOFF_L1M_MESH": {
        "case_dir": os.path.join(REPO, "verification", "runs", "navier_class",
                                 "SUBOFF_A1H_DRIFT", "MESH_FULL_L1M"),
        "cells": 6537226,                # log.checkMesh.FULLFLAG: "cells: 6537226"
        "mesh_words": "6537226 cells, the L1 mirror",
        "solver": "none -- this directory is a mesh, not a solve",
        "end_time": "constant",
        "fields": (),
        "allowed_verdicts": {"PENDING"},
        "verdict_stamp": "PENDING",
        "source": "MESH_FULL_L1M/M_GATES_RESULT.md",
    },
    # ---------------------------------------------------------------------
    # THE WOLF DYNAMICS DrivAer REPRODUCTION, added 2026-09-13. The case trees
    # live OUTSIDE the repository, under /home/ubuntu/certonomous-runs, which is
    # why these two entries carry an absolute case_dir rather than one built
    # from REPO.
    #
    # THE COARSE ENTRY OWNS "PASS" AND THE FINE ENTRY OWNS "PENDING", and the
    # difference is the point. The coarse case is COMPLETE at iteration 1000 and
    # graded PASS on G1, G2 and G3 in
    # verification/campaign/WOLFDYNAMICS_DRIVAER_COARSE_RESULTS.md. The fine
    # case was STILL RUNNING when these entries were written, so it owns only
    # PENDING -- the display/queue state -- and assert_stamp REFUSES a PASS on a
    # fine-level figure before a pixel is drawn.
    #
    # AND A DISCLOSURE THAT TRAVELS WITH EVERY COARSE FIGURE: the coarse result
    # is a REPRODUCTION, not a validation. Our forceCoeffs output is BYTE-
    # IDENTICAL to their shipped file, which proves the case ran verbatim and
    # CANNOT corroborate their number.
    "WD_DRIVAER_COARSE": {
        "case_dir": "/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/coarse_R1",
        "cells": 669416,                 # log.checkmesh: "cells: 669416"
        "mesh_words": "669416 cells, their coarse mesh",
        "solver": "simpleFoam",          # system/controlDict: application
        "end_time": "1000",              # controlDict endTime 1000, reached
        "fields": ("p", "U", "k", "omega", "nut", "yPlus"),
        "allowed_verdicts": {"PASS"},
        "verdict_stamp": "PASS",
        "source": "verification/campaign/WOLFDYNAMICS_DRIVAER_COARSE_RESULTS.md",
    },
    "WD_DRIVAER_FINE": {
        "case_dir": "/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/fine_R1",
        "cells": 4048483,                # log.checkmesh: "cells: 4048483"
        "mesh_words": "4048483 cells, their fine mesh",
        "solver": "simpleFoam",
        "end_time": "0",                 # RUNNING; no time directory written yet
        "fields": ("p", "U", "k", "omega", "nut"),
        "allowed_verdicts": {"PENDING"},
        "verdict_stamp": "PENDING",
        "source": "the run is live; no grading record exists yet",
    },
    # ---------------------------------------------------------------------
    # THE ONERA M6 J-FAMILY, added 2026-09-13 for the demo field panels. Two
    # entries because the mesh figure is the COARSE level's own mesh and the
    # field figures are the FINE level's own fields, per the owner's ParaView
    # rule, and NOTHING IS INTERPOLATED BETWEEN THEM.
    #
    # BOTH ENTRIES OWN EXACTLY ONE VERDICT WORD: "GATE FAIL". Every level of
    # this family misses the pre-registered B1 Cp band of 0.050 on the rows its
    # grade file names -- m6j_grade_M6J_L1.json, _L2.json and _L3.json, each
    # carrying "verdict": "GATE FAIL". A stamp claiming PASS or GATE REACHED on
    # these fields is REFUSED by assert_stamp before a pixel is rendered.
    "M6J_L1": {
        "case_dir": os.path.join(REPO, "verification", "runs", "M6J_runs",
                                 "M6J_L1"),
        "cells": 983040,                 # constant/polyMesh/owner note: nCells:983040
        "mesh_words": "983040 cells, fine level",
        "solver": "rhoSimpleFoam",       # system/controlDict: application
        "end_time": "8000",              # last written time directory
        "fields": ("p", "U", "T"),
        "allowed_verdicts": {"GATE FAIL"},
        "verdict_stamp": "GATE FAIL",
        "source": "verification/runs/M6J_runs/M6J_L1/m6j_grade_M6J_L1.json",
    },
    "M6J_L2": {
        "case_dir": os.path.join(REPO, "verification", "runs", "M6J_runs",
                                 "M6J_L2"),
        "cells": 122880,                 # constant/polyMesh/owner note: nCells:122880
        "mesh_words": "122880 cells, medium level",
        "solver": "rhoSimpleFoam",       # system/controlDict: application
        "end_time": "5000",              # last written time directory
        "fields": ("p", "U", "T"),
        "allowed_verdicts": {"GATE FAIL"},
        "verdict_stamp": "GATE FAIL",
        "source": "verification/runs/M6J_runs/M6J_L2/m6j_grade_M6J_L2.json",
    },
    "M6J_L3": {
        "case_dir": os.path.join(REPO, "verification", "runs", "M6J_runs",
                                 "M6J_L3"),
        "cells": 15360,                  # constant/polyMesh/owner note: nCells:15360
        "mesh_words": "15360 cells, coarse level",
        "solver": "rhoSimpleFoam",       # system/controlDict: application
        "end_time": "3000",              # last written time directory
        "fields": ("p", "U", "T"),
        "allowed_verdicts": {"GATE FAIL"},
        "verdict_stamp": "GATE FAIL",
        "source": "verification/runs/M6J_runs/M6J_L3/m6j_grade_M6J_L3.json",
    },
    "T18_CU_f": {
        "case_dir": os.path.join(REPO, "verification", "runs", "T-family",
                                 "T18_runs", "T18_CU_f"),
        "cells": 512000,                 # log.checkMesh: "cells: 512000"
        "mesh_words": "80 x 80 x 80",    # T18_registered.json /cases/T18_CU_f
        "solver": "laplacianFoam",       # system/controlDict: application
        "end_time": "2",                 # controlDict endTime 2 (Fo = 0.2)
        "fields": ("T",),                # laplacianFoam solves and writes T alone
        # THE VERDICT, and the whole reason this table exists.
        # Rows G1/G2/G3 PASS: T18_GRADE_OUTPUT_20260831T151113Z.txt.
        # Ceiling GATE REACHED: T18_registered.json /ceiling and gate_t18.json.
        "allowed_verdicts": {"PASS", "GATE REACHED"},
        "verdict_stamp": ("rows G1 G2 G3: PASS ; rung ceiling: GATE REACHED"),
        "source": "T18_GRADE_OUTPUT_20260831T151113Z.txt and gate_t18.json",
    },
    "K2bU3R3_D59": {
        "case_dir": os.path.join(REPO, "verification", "runs",
                                 "F14-cooling-ladder", "K2b_runs",
                                 "K2bU3R3_D59"),
        "cells": 137000,                 # log.checkMesh: "cells: 137000"
        "mesh_words": "137000 cells",
        "solver": "buoyantBoussinesqPimpleFoam",   # controlDict: application
        "end_time": "80",                # controlDict endTime 80.0
        "fields": ("T", "U"),
        # THE VERDICT. GATE REACHED and NEVER PASS -- this is a survives/damps
        # DISCRIMINATOR gate and PASS is a value-in-band term it does not own.
        # Corrected from PASS on 2026-09-09 under VERIFICATION_CHARTER section 2.
        # The absence of "PASS" from this set is what makes assert_stamp refuse it.
        "allowed_verdicts": {"GATE REACHED"},
        "verdict_stamp": "GATE REACHED",
        "source": "K2bU3R3_GRADE.txt",
    },
    # ---------------------------------------------------------------------
    # THE K2f RACK SET, added 2026-09-12 for Sanaa's ~20:30Z directive: the
    # render shows the COARSE level's mesh and the FINEST completed level's
    # fields. Two entries, because those are two different meshes and NOTHING
    # IS INTERPOLATED BETWEEN THEM -- the mesh picture is L1's own mesh and the
    # field pictures are L3's own fields, each rendered from the case that
    # produced it. A single image claiming to be a coarse mesh carrying fine
    # fields would require resampling one onto the other, which manufactures
    # values that no solver wrote.
    #
    # BOTH ENTRIES OWN EXACTLY ONE VERDICT WORD: "NOT A RESULT". That is not a
    # formality and it is the whole reason these rows exist. K2g's L3 ran 803 of
    # a registered 2000 iterations, was stopped by its own registered stop rule
    # R4 on coherent oscillation in the graded quantity, FAILS standing rule 4
    # (clause 3: last written time 803 != endTime 2000; clause 5: 803
    # ExecutionTime lines, expected 2000), and was REFUSED AT EXIT 2 by its
    # frozen comparator. Its DP_module of 28.0521393 m2/s2 lies inside the
    # registered band -- which is exactly why a figure of it is dangerous. Any
    # stamp claiming PASS or GATE REACHED on these fields is REFUSED by
    # assert_stamp before a single pixel is rendered.
    "K2f_L1": {
        "case_dir": os.path.join(REPO, "verification", "runs",
                                 "F14-cooling-ladder", "K2f_runs", "K2f_L1"),
        "cells": 58368,                  # log.checkMesh / K2g_PREREGISTRATION.md section 3
        "mesh_words": "58368 cells, coarse level",
        "solver": "buoyantBoussinesqSimpleFoam",   # controlDict: application
        "end_time": "3000",              # controlDict endTime 3000
        "fields": ("T", "U"),
        # THE MESH SOURCE. Chosen coarse, not medium, on a MEASUREMENT rather
        # than by default: Sanaa's directive says coarse "or medium if the
        # coarse isnt converged", and L1 IS converged -- final-300 per-iteration
        # residual p2p 5.05e-11 on Ux, and DP_module monotone across all six
        # checkpoints (0 sign changes, p2p 3.11e-04 m2/s2).
        "allowed_verdicts": {"NOT A RESULT"},
        "verdict_stamp": "NOT A RESULT",
        "source": "K2h_PREREGISTRATION.md section 2; K2g_GATE refusal at exit 2",
    },
    "K2f_L3": {
        "case_dir": os.path.join(REPO, "verification", "runs",
                                 "F14-cooling-ladder", "K2g_runs", "K2f_L3"),
        "cells": 664848,                 # K2g_PREREGISTRATION.md section 3
        "mesh_words": "664848 cells, fine level",
        "solver": "buoyantBoussinesqSimpleFoam",
        "end_time": "803",               # STOPPED at 803 against a registered endTime of 2000
        "fields": ("T", "U"),
        "allowed_verdicts": {"NOT A RESULT"},
        "verdict_stamp": "NOT A RESULT",
        "source": "autograde.K2f_L3.out: mark_done_k2f NOT DONE (clauses 3, 5); "
                  "analyse_k2g REFUSED exit 2",
    },
    # ------------------------------------------------------------------
    # K2h_L3 -- the SAME 664,848-cell mesh as K2f_L3, REUSED BIT FOR BIT
    # (K2h_PREREGISTRATION.md section 4), solved TRANSIENT because K2g's own
    # stop rule R4 voted the physics unsteady.  INSERTED, never replacing an
    # existing key: no other entry's values are touched by this addition.
    #
    # `allowed_verdicts` IS THE FULL SET SECTION 6 PERMITS AND IS FIXED HERE
    # BEFORE THE NUMBER EXISTS.  Section 6 admits exactly three outcomes for
    # this level -- PASS inside G-DPBAR, GATE FAIL outside it, NOT A RESULT on
    # D-COMPLETE or D-STATIONARY -- so all three are allowed and none is
    # chosen.  Narrowing this set after seeing DPbar would be choosing the
    # permissible caption to fit the answer, which is the same defect as
    # choosing a gate to fit it.  GATE REACHED is NOT admitted: this level has
    # a value-in-band gate, not a rung ceiling.
    "K2h_L3": {
        "case_dir": os.path.join(REPO, "verification", "runs",
                                 "F14-cooling-ladder", "K2h_runs", "K2h_L3"),
        "cells": 664848,                 # K2h_PREREGISTRATION.md section 4
        "mesh_words": "664848 cells, fine level, transient",
        "solver": "buoyantBoussinesqPimpleFoam",   # section 4
        "end_time": "112",               # section 5 E-ENDTIME
        "fields": ("TMean", "p_rghMean", "UMean", "T", "U", "p_rgh"),
        "allowed_verdicts": {"PASS", "GATE FAIL", "NOT A RESULT"},
        "verdict_stamp": "PENDING",      # replaced by the comparator's own word
        "source": "K2h_PREREGISTRATION.md section 6 (G-DPBAR, D-STATIONARY, "
                  "D-COMPLETE); AMENDMENT 1, ADDENDUM 1, its ERRATUM, ADDENDUM 2",
    },
}


def facts(case: str) -> dict:
    if case not in CASE_FACTS:
        refuse(f"{case!r} has no recorded facts in this module, so a render of "
               f"it would be stamping numbers nobody wrote down. Known cases: "
               f"{sorted(CASE_FACTS)}")
    return CASE_FACTS[case]


# ---------------------------------------------------------------------------
# The stamp guard -- the refusal this module exists for
# ---------------------------------------------------------------------------

def assert_caption_renderable(text: str) -> str:
    """REFUSE a caption containing a glyph not measured to render."""
    for ch in text:
        if ch in KNOWN_DROPPED_GLYPHS:
            refuse(f"caption uses {ch!r}, which is {KNOWN_DROPPED_GLYPHS[ch]}. "
                   f"The source would look correct and the screen would not: "
                   f"{text!r}")
        if ch not in SAFE_CAPTION_CHARS:
            refuse(f"caption uses {ch!r} (U+{ord(ch):04X}), which is not in the "
                   f"set of glyphs measured to render in this font: {text!r}")
    return text


def assert_stamp(text: str, case: str) -> str:
    """REFUSE a figure stamp that is not defensible for THIS case.

    Five refusals, in order:

    1. the stamp does not name the case it claims to show;
    2. the stamp carries no verdict word at all -- a figure without its verdict
       is not shippable;
    3. the stamp carries a verdict word THIS CASE DOES NOT OWN. This is the one
       that matters: it is what stops ``PASS`` appearing on a K2bU3R3 figure,
       mechanically, rather than relying on whoever writes the caption
       remembering that a discriminator gate has no PASS;
    4. the stamp softens or upgrades the verdict with prose;
    5. the stamp uses a glyph the font drops.
    """
    f = facts(case)

    if case not in text:
        refuse(f"the stamp does not name the case it shows. A figure whose "
               f"caption does not identify its own case cannot be checked "
               f"against a grade record: {text!r}")

    # Longest-first so "GATE REACHED" is matched before any shorter token.
    present = [v for v in sorted(FIXED_VOCABULARY, key=len, reverse=True)
               if v in text]
    if not present:
        refuse(f"the stamp carries NO verdict word from the fixed vocabulary "
               f"{FIXED_VOCABULARY}. A figure without its verdict word is not "
               f"shippable: {text!r}")

    allowed = f["allowed_verdicts"]
    for v in present:
        if v not in allowed:
            refuse(
                f"the stamp claims {v!r} for {case}, which owns only "
                f"{sorted(allowed)} per {f['source']}. "
                f"For K2bU3R3 in particular: its gate is a survives/damps "
                f"DISCRIMINATOR, PASS is a value-in-band term it does not "
                f"possess, and the word was deliberately corrected away from "
                f"PASS on 2026-09-09 under VERIFICATION_CHARTER section 2. "
                f"Refusing rather than re-introducing that defect: {text!r}")

    low = text.lower()
    for bad, why in BANNED_STAMP_PROSE.items():
        if bad in low:
            refuse(f"the stamp uses {bad!r}: {why}. Stamp was: {text!r}")

    return assert_caption_renderable(text)


# ---------------------------------------------------------------------------
# The scratch case -- nothing is ever written into a graded run tree
# ---------------------------------------------------------------------------

def _tree_fingerprint(root: str) -> set:
    out = set()
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        try:
            st = os.lstat(path)
        except OSError:
            continue
        out.add((entry, st.st_size, int(st.st_mtime)))
    return out


def run_tree_fingerprint(case_dir: str) -> set:
    return _tree_fingerprint(case_dir)


def assert_run_tree_untouched(case_dir: str, before: set) -> None:
    """Prove the graded case did not move while we rendered from it."""
    after = _tree_fingerprint(case_dir)
    if after != before:
        added = after - before
        removed = before - after
        refuse(f"the graded run tree at {case_dir} CHANGED during rendering "
               f"(added {sorted(added)[:3]}, removed {sorted(removed)[:3]}). A "
               f"render must never write into a case under the completion rule")


def materialise_case(case: str, time_dirs):
    """A scratch case built ENTIRELY of symlinks. Returns (root, foam_file).

    Both of these cases are single-region, so the layout is simply the case's
    own ``constant/polyMesh``, its ``system``, and the requested time
    directories. The ``.foam`` file goes in the SCRATCH root, never beside the
    graded case -- that is refusal 1, and it is the whole reason this function
    exists rather than a one-line ``touch case/x.foam``.
    """
    f = facts(case)
    case_dir = f["case_dir"]
    if not os.path.isdir(case_dir):
        refuse(f"the case directory {case_dir} is not on disk")

    mesh_src = os.path.join(case_dir, "constant", "polyMesh")
    system_src = os.path.join(case_dir, "system")
    if not os.path.isdir(mesh_src):
        refuse(f"no mesh at {mesh_src}; this render will not invent one")
    if not os.path.isdir(system_src):
        refuse(f"no case dictionaries at {system_src}")

    root = tempfile.mkdtemp(prefix=f"demo3d_{case}_")
    os.makedirs(os.path.join(root, "constant"))
    os.symlink(mesh_src, os.path.join(root, "constant", "polyMesh"))
    os.symlink(system_src, os.path.join(root, "system"))

    for td in time_dirs:
        src = os.path.join(case_dir, td)
        if not os.path.isdir(src):
            shutil.rmtree(root, ignore_errors=True)
            refuse(f"the fields at t = {td} are not on disk at {src}. This "
                   f"render will not substitute another time's data for them, "
                   f"and it will NOT run a solver to create them")
        dst = os.path.join(root, td)
        os.makedirs(dst)
        for name in sorted(os.listdir(src)):
            os.symlink(os.path.join(src, name), os.path.join(dst, name))

    foam = os.path.join(root, f"{case}.foam")
    with open(foam, "w", encoding="utf-8"):
        pass
    return root, foam


def open_case(case: str, arrays, time_dirs, time_value=None,
              decompose_polyhedra: bool = True):
    """Open a case and PROVE it is that case's mesh.

    Returns ``(reader, scratch_root, n_cells)``.

    ``decompose_polyhedra`` defaults to True, which is ParaView's own default and
    therefore the behaviour every existing caller already has. It must be set
    FALSE for a mesh whose cells are not all tetrahedra/hexahedra, or the reader
    splits them and the cell-count assertion below fires on a mesh that is
    perfectly correct. MEASURED on the Wolf Dynamics DrivAer coarse case, whose
    Fluent mesh checkMesh reports as 669,416 cells: the reader returned
    1,026,903 with decomposition on. The assertion is NOT relaxed to admit that
    number -- the reader is told not to change the mesh, and 669,416 is then
    asserted exactly.
    """
    from paraview.simple import OpenFOAMReader, UpdatePipeline

    f = facts(case)
    root, foam = materialise_case(case, time_dirs)
    reader = OpenFOAMReader(FileName=foam)
    if not decompose_polyhedra:
        reader.Decomposepolyhedra = 0
    reader.MeshRegions = ["internalMesh"]
    reader.CellArrays = list(arrays)
    if time_value is None:
        time_value = float(time_dirs[-1])
    UpdatePipeline(time=float(time_value), proxy=reader)

    info = reader.GetDataInformation()
    n_cells = info.GetNumberOfCells()
    want = f["cells"]
    if n_cells != want:
        shutil.rmtree(root, ignore_errors=True)
        refuse(f"the {case} render loaded {n_cells:,} cells where the mesh "
               f"record says {want:,}. This is the wrong mesh, and a wrong mesh "
               f"renders a perfectly plausible picture. Refusing")

    for name in arrays:
        arr = info.GetCellDataInformation().GetArrayInformation(name)
        if arr is None:
            shutil.rmtree(root, ignore_errors=True)
            refuse(f"{case} carries no field {name!r} at t = {time_dirs[-1]}, "
                   f"so nothing would be painted with it. NOT solving for it")
    return reader, root, n_cells


# ---------------------------------------------------------------------------
# Views, captions, and the image guard
# ---------------------------------------------------------------------------

def white_background(view) -> None:
    view.UseColorPaletteForBackground = 0
    view.BackgroundColorMode = "Single Color"
    view.Background = [1.0, 1.0, 1.0]
    view.OrientationAxesVisibility = 0


def caption(view, text: str, case: str, position=(0.02, 0.02), size=9,
            check_stamp: bool = True):
    """One caption line burned into the render.

    ``check_stamp`` is True for the verdict stamp -- the line that must name the
    case and carry a legal verdict word. Secondary lines (a geometry
    declaration, a colour-bar note) go through the glyph check only.
    """
    from paraview.simple import Show, Text

    if check_stamp:
        assert_stamp(text, case)
    else:
        assert_caption_renderable(text)
    src = Text(Text=text)
    disp = Show(src, view)
    disp.WindowLocation = "Any Location"
    disp.Position = list(position)
    disp.FontSize = size
    disp.Color = [0.15, 0.15, 0.15]
    return src


def verify_written_image(path: str) -> int:
    """REFUSE an image that is missing or too small to be a real picture."""
    if not os.path.isfile(path):
        refuse(f"the render wrote no file at {path}")
    n = os.path.getsize(path)
    if n < MIN_IMAGE_BYTES:
        refuse(f"the render at {path} is {n} bytes, below the {MIN_IMAGE_BYTES} "
               f"a real image occupies; an all-blank frame will not be shown")
    return n


def save_screenshot(view, path: str, size=(1600, 900)) -> int:
    """Write a render and REFUSE an image that is empty, missing or stale."""
    from paraview.simple import SaveScreenshot

    if view is None:
        refuse(f"no view was given to render {os.path.basename(path)} into, so "
               f"nothing would have been drawn")
    if os.path.exists(path):
        os.remove(path)          # never let a previous run's image stand in
    os.makedirs(os.path.dirname(path), exist_ok=True)
    SaveScreenshot(path, view, ImageResolution=list(size))
    return verify_written_image(path)


def assert_paraview_version() -> str:
    from paraview import simple

    version = simple.GetParaViewVersion()
    text = f"{version.major}.{version.minor}"
    if text != REQUIRED_PARAVIEW:
        refuse(f"these renders are pinned to ParaView {REQUIRED_PARAVIEW} and "
               f"this is {text}; a render that moves with the reader version "
               f"is not reproducible")
    return text


def announce(message: str) -> None:
    """Write a progress line straight to file descriptor 1.

    NOT ``print`` and NOT ``sys.stdout``: ``paraview.simple`` replaces
    ``sys.stdout`` with a wrapper that only reaches the real descriptor at
    interpreter finalisation, and these scripts end in ``os._exit`` so
    ParaView's GLX teardown cannot overwrite a computed result. The two together
    silently discard every progress line -- a run that does its work and reports
    nothing is indistinguishable from a run that did nothing.
    """
    os.write(1, (message + "\n").encode("utf-8", "replace"))


def announce_error(message: str) -> None:
    os.write(2, (message + "\n").encode("utf-8", "replace"))


# ---------------------------------------------------------------------------
# Framing -- shared, because both cases were mis-framed the same three ways
# ---------------------------------------------------------------------------

def frame_by_extent(view, focal, direction, up=(0.0, 0.0, 1.0),
                    bounds=None, pad=1.08, bottom_band=0.0):
    """Frame a scene by PROJECTING its eight corners onto the camera axes.

    ``bounds`` is ``(x0, x1, y0, y1, z0, z1)`` of the body to frame.
    Returns the parallel scale actually in force.

    THREE WAYS OF GETTING THIS WRONG, ALL OF THEM MET ON THIS BOX:

    1. **A hand-typed ``CameraParallelScale``.** It drew the data centre room at
       48 % of frame height inside a wall of white. The number was simply wrong
       and nothing in the pipeline said so.

    2. **``ResetCamera``.** It frames the bounding SPHERE. The room's diagonal is
       5.70 m against a 2.7 m height, so an axis-aligned view came out zoomed to
       a half-height of 2.85 m where the data needed 1.35 m -- half size, and
       looking entirely deliberate.

    3. **Setting the scale and rendering once.** THE FIRST ``Render`` ON A FRESH
       VIEW PERFORMS AN AUTOMATIC RESET THAT SILENTLY OVERWRITES THE SCALE. It
       was measured here: a requested 1.4850 came back as 2.2102, which is
       exactly the half-diagonal of the slice being drawn. Every figure written
       before this was found was framed by that reset rather than by its own
       code. So the scale is applied AFTER a first render, re-applied, and then
       ASSERTED -- an unasserted camera setting is not a setting, it is a wish.
    """
    import math
    from paraview.simple import Render

    if bounds is None:
        refuse("frame_by_extent needs the bounds of the body to frame; "
               "guessing them is how the bounding-sphere bug got in")

    def _norm(v):
        n = math.sqrt(sum(c * c for c in v))
        if n == 0:
            refuse("a zero-length camera vector cannot define a view")
        return [c / n for c in v]

    def _cross(a, b):
        return [a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0]]

    d = _norm(direction)                # the camera sits at focal + dist * d
    view_dir = [-c for c in d]          # and looks this way
    right = _norm(_cross(view_dir, up))
    true_up = _norm(_cross(right, view_dir))

    x0, x1, y0, y1, z0, z1 = bounds
    hs, vs = [], []
    for cx in (x0, x1):
        for cy in (y0, y1):
            for cz in (z0, z1):
                r = [cx - focal[0], cy - focal[1], cz - focal[2]]
                hs.append(sum(r[i] * right[i] for i in range(3)))
                vs.append(sum(r[i] * true_up[i] for i in range(3)))
    half_h = max(abs(min(hs)), abs(max(hs)))
    half_v = max(abs(min(vs)), abs(max(vs)))

    w, h = view.ViewSize
    scale = max(half_v, half_h / (float(w) / float(h))) * pad

    # Reserve a strip at the foot of the frame for the verdict stamp. Without
    # it the stamp is burnt over the field itself and, on a dark region, is
    # simply unreadable -- a figure whose verdict cannot be read has no verdict
    # on it. Widening the view and dropping the focal point by the same amount
    # lifts the data clear while keeping it centred horizontally.
    if not 0.0 <= bottom_band < 0.5:
        refuse(f"bottom_band must be a fraction of frame height below 0.5, "
               f"not {bottom_band!r}")
    if bottom_band:
        scale = scale / (1.0 - bottom_band)
        focal = [focal[i] - true_up[i] * scale * bottom_band for i in range(3)]

    dist = 12.0 * max(half_h, half_v, 1e-9) / max(half_h, half_v, 1e-9)
    span = max(x1 - x0, y1 - y0, z1 - z0)
    view.CameraFocalPoint = list(focal)
    view.CameraPosition = [focal[i] + 10.0 * span * d[i] for i in range(3)]
    view.CameraViewUp = list(true_up)
    view.CameraParallelProjection = 1

    view.CameraParallelScale = scale
    Render(view)                        # this first render may reset the scale
    view.CameraParallelScale = scale    # so put it back, now that it has
    Render(view)

    got = view.CameraParallelScale
    if abs(got - scale) > 1e-6 * max(1.0, abs(scale)):
        refuse(f"the camera parallel scale was set to {scale:.6f} and the view "
               f"reports {got:.6f}. The framing in this figure is not the "
               f"framing this code asked for")
    return got
