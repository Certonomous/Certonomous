#!/usr/bin/env python3
"""OWN-FAMILY M6 CASE-FILE WRITER -- the ONE writer the fine-triple solve driver delegates to.

WHAT THIS FILE IS.  The solve driver run_m6_own_family_triple.sh (git blob 63ce12b9, frozen
prereg addendum 13.2) copies the level's screened mesh into <solve>/constant/polyMesh and then
calls THIS writer to author the rhoSimpleFoam case (0/, system/, constant/*Properties) for the
own-family {L2, L1, L0} solve.  The driver authors NO case file of its own; there is exactly
ONE case writer, and it is this file.

BYTE-IDENTITY TO RUNG1_M6_R2 IS ACHIEVED BY REUSE, NOT BY RE-TYPING.  Frozen prereg
M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md 5 requires the rhoSimpleFoam configuration
(fvSchemes, fvSolution, thermophysical/turbulence properties, boundary-condition types and
values, relaxation, controlDict) to be BYTE-IDENTICAL to the frozen M6 gate of RUNG1_M6_R2.
The registered instrument that emits those exact bytes is the pinned M6SR case writer
cases/M6SR/write_m6sr_case.py (whose 8-section content is itself transcribed byte-identical
from RUNG1_M6_R2 5).  Rather than carry a SECOND definition of "what a runnable M6 case is"
-- which would be free to drift from the pinned one -- this writer IMPORTS write_m6sr_case and
calls its dictionary functions VERBATIM:

    write_constant  write_fv_schemes  write_fv_solution  write_decompose_par_dict
    write_sample_dict  write_control_dict  write_zero  classify_patches
    freestream_vector  stations  _refuse_if_zero_or_time_dirs

The SAME code that writes the M6SR case writes this one, so the physics-bearing files are
byte-identical BY CONSTRUCTION.  The ONLY things this writer varies are the three things the
own family legitimately differs in and the prereg addendum accounts for:
  * PATCH NAMES -- {wing, symmetry, farfield} for this family vs M6SR's {wing, inout, sym}.
    They are NOT typed in here: write_m6sr_case.classify_patches() discovers them BY TYPE from
    THIS mesh's constant/polyMesh/boundary (wall -> wing, symmetry -> symmetry, patch ->
    farfield), so the boundary-condition VALUES and TYPES are identical and only the names the
    regexes match differ.  This writer additionally REFUSES unless the discovered names are
    exactly {wing, symmetry, farfield} (the own-family createPatchDict set, addendum 13.2).
  * RANKS -- passed by the driver (L2=4, L1=8, L0=14), written into decomposeParDict.
  * endTime -- passed by the driver (6000 per level, prereg 7.2), written into controlDict.

THIS IS A SOLVER INPUT, NOT A GRADER.  It computes no gate, reads no result, prints no verdict
(standing rule 2 fixes the GRADING path at the pre-registration commit; case files are inputs).
If any precondition does not hold it REFUSES (rc 2) rather than write a case it cannot justify;
a physics/config deviation from RUNG1_M6_R2 is never made silently (T25).

EXIT VOCABULARY (mirrors write_m6sr_case.py 9.2):
    0   the case was written; CASE_PROVENANCE.json records what was written and why.
    2   REFUSAL -- a precondition does not hold.
    70  INTERNAL DEFECT of this writer.  Never a finding about the M6.

NO BARE `assert` (rule: python3 -O deletes them).  Every guard is an explicit raise.

NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN.  SUBMISSIONS ARE PARKED (rule 7).
"""

import argparse
import json
import os
import sys

_THIS = os.path.abspath(__file__)
# .../verification/runs/M6_OWN_FAMILY_runs/write_m6_own_family_case.py -> repo root is 4 up.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_THIS))))
_M6SR_DIR = os.path.join(REPO, "cases", "M6SR")
if _M6SR_DIR not in sys.path:
    sys.path.insert(0, _M6SR_DIR)

try:
    import write_m6sr_case as W   # the pinned M6SR case writer; its writers are reused verbatim
except ImportError as _exc:        # pragma: no cover
    sys.stderr.write(
        "INTERNAL DEFECT: the pinned M6SR case writer cases/M6SR/write_m6sr_case.py is not "
        f"importable: {_exc}. This own-family writer carries NO second definition of the "
        "case dictionaries; it reuses the pinned ones. Cannot proceed.\n")
    sys.exit(70)


OWN_LEVELS = ("L2", "L1", "L0")
OWN_PATCH_NAMES = {"wall": "wing", "symmetry": ["symmetry"], "farfield": ["farfield"]}

# The reused pinned instrument, recorded for provenance (blob resolved at write time, below).
REUSED_FUNCTIONS = (
    "write_constant", "write_fv_schemes", "write_fv_solution",
    "write_decompose_par_dict", "write_sample_dict", "write_control_dict",
    "write_zero", "classify_patches", "freestream_vector", "stations",
    "_refuse_if_zero_or_time_dirs", "mesh_identity_token",
)


class Refusal(Exception):
    """rc 2 -- a precondition does not hold; refuse rather than write an unjustified case."""


class InternalDefect(Exception):
    """rc 70 -- a defect in THIS writer.  Never a finding about the M6."""


def _reused_blob():
    """git blob of the reused pinned writer, for the provenance record (best-effort)."""
    try:
        import subprocess
        out = subprocess.run(
            ["git", "-C", REPO, "hash-object", os.path.join("cases", "M6SR", "write_m6sr_case.py")],
            capture_output=True, text=True)
        return out.stdout.strip() or "unresolved"
    except Exception:                                            # pragma: no cover
        return "unresolved"


def write_own_case(solve, level, ranks, end_time):
    """Author the own-family solve case at <solve> for <level>.  -> provenance dict.

    Writes constant/*Properties, system/{fvSchemes,fvSolution,decomposeParDict,sampleDict,
    controlDict} and 0/ (0/U LAST -- the age guard, rule 4), reusing the pinned M6SR writers.
    """
    if level not in OWN_LEVELS:
        raise Refusal(f"{level!r} is not one of {OWN_LEVELS}. REFUSED.")
    try:
        ranks = int(ranks)
        end_time = int(end_time)
    except (TypeError, ValueError) as exc:
        raise Refusal(f"--ranks and --end-time must be integers; got ranks={ranks!r} "
                      f"end-time={end_time!r} ({exc}). REFUSED.")
    if ranks < 1:
        raise Refusal(f"--ranks must be >= 1; got {ranks}. REFUSED.")
    if end_time < 1:
        raise Refusal(f"--end-time must be >= 1; got {end_time}. REFUSED.")

    pm = os.path.join(solve, "constant", "polyMesh")
    if not os.path.isdir(pm):
        raise Refusal(
            f"{pm} is ABSENT. The driver must stage the screened mesh into "
            "<solve>/constant/polyMesh before this writer runs; boundary conditions are "
            "attached BY PATCH TYPE from this mesh's boundary file. An absent mesh never "
            "reads as a default patch set. REFUSED.")

    # Rule 4 age guard: refuse a case where 0/ or any time directory already exists (a
    # pre-existing 0/U makes the guard unprovable).  Reuse the pinned refusal verbatim.
    W._refuse_if_zero_or_time_dirs(solve)

    # Patches discovered BY TYPE (never typed in here), then REQUIRED to be the own-family set.
    pat, A = W.classify_patches(pm)
    if (pat["wall"] != OWN_PATCH_NAMES["wall"]
            or pat["symmetry"] != OWN_PATCH_NAMES["symmetry"]
            or pat["farfield"] != OWN_PATCH_NAMES["farfield"]):
        raise Refusal(
            "OWN-FAMILY PATCH-NAME MISMATCH. The frozen prereg addendum 13.2 pins the "
            "own-family createPatchDict names wing (wall), symmetry (symmetry), farfield "
            f"(patch). This mesh's boundary yields wall={pat['wall']!r}, "
            f"symmetry={pat['symmetry']!r}, farfield={pat['farfield']!r}. A different name set "
            "is a FINDING, not something to adapt to silently. REFUSED.")

    uvec, axes = W.freestream_vector(pm, A)          # refuses on an unexpected frame
    stns = W.stations(A.A_MAP_YB)                    # the pinned seven registered stations

    written = []
    # constant/ + system/ (physics-bearing files, reused verbatim -> byte-identical).
    written += W.write_constant(solve)               # thermophysical + turbulence properties
    written.append(W.write_fv_schemes(solve))
    written.append(W.write_fv_solution(solve))
    written.append(W.write_decompose_par_dict(solve, ranks))
    written.append(W.write_sample_dict(solve, pat, axes, stns))
    written.append(W.write_control_dict(solve, end_time, uvec, pat))
    # 0/ LAST, and write_zero() writes 0/U LAST within it -- Section 8.6 / rule 4 age guard.
    written += W.write_zero(solve, pat, uvec)

    import math
    mag = math.sqrt(sum(c * c for c in uvec))
    prov = {
        "writer": "verification/runs/M6_OWN_FAMILY_runs/write_m6_own_family_case.py",
        "level": level,
        "solve_case": solve,
        "polymesh_read": pm,
        "ranks": ranks,
        "end_time": end_time,
        "mesh_identity_token": W.mesh_identity_token(pm),
        "BYTE_IDENTITY_BASIS": (
            "The rhoSimpleFoam configuration is BYTE-IDENTICAL to RUNG1_M6_R2 5 by REUSE: "
            "this writer imports the pinned M6SR case writer cases/M6SR/write_m6sr_case.py "
            "and calls its dictionary functions VERBATIM. The same code that writes the M6SR "
            "case writes this one; the physics-bearing files are byte-identical BY "
            "CONSTRUCTION. Only patch NAMES (discovered by type -> wing/symmetry/farfield), "
            "ranks and endTime differ (prereg addendum 13.2, 13.3)."),
        "reused_from": {
            "path": "cases/M6SR/write_m6sr_case.py",
            "git_blob_at_write": _reused_blob(),
            "reused_functions": list(REUSED_FUNCTIONS),
        },
        "patches_by_TYPE_never_by_name": pat,
        "derived_axes": axes,
        "freestream": {
            "U_vector_written": uvec,
            "magnitude_written": mag,
            "Mach_reproduced": mag / W.A_INF,
            "Reynolds_reproduced_on_MAC": W.RHO_INF * mag * W.MAC_C / W.MU_INF,
        },
        "stations": stns,
        "b_semi_m_REGISTERED": W.B_SEMI_M,
        "Pr_registered": W.PR_REGISTERED,
        "Pr_achieved_derived": W.pr_achieved_from_eucken(),
        "written": written,
        "THIS_FILE_IS_A_SOLVER_INPUT_NOT_A_GRADER": (
            "It computes no gate, reads no result and prints no verdict. Standing rule 2 fixes "
            "the GRADING path at the pre-registration commit; case files are INPUTS."),
        "cost_basis": (
            "core-minutes = wall s x ranks / 60. Dollars are DERIVED, NOT MEASURED, at the "
            "owner-stated c7a.4xlarge $0.0513/core-h; RANKS ARE READ FROM THE SOLVER LOG'S "
            "BANNER by the grader, never from decomposeParDict."),
        "choices_inherited_from_M6SR_writer": getattr(W, "CHOICES_MADE_HERE", None),
        "L_HONEST_inherited": getattr(W, "L_HONEST", None),
    }
    W._write(os.path.join(solve, "CASE_PROVENANCE.json"), json.dumps(prov, indent=2) + "\n")
    return prov


def selftest():
    """Planted control (rule 3): show the writer WRITES the registered value, not a stale one.

    Reuses the pinned M6SR writer's own k_inf mutation (W._mutate_k_and_write): a case written
    under a CORRUPTED k_inf must NOT still carry the registered value.  Driven on this family's
    L2 screened mesh.  A control that cannot fire (no mesh) is a REFUSAL, never a silent pass.
    """
    import shutil
    import tempfile
    l2_pm = os.path.join(os.path.dirname(_THIS), "L2", "case", "constant", "polyMesh")
    if not os.path.isdir(l2_pm):
        raise Refusal(f"selftest needs the L2 screened mesh at {l2_pm}; it is ABSENT. A "
                      "control that cannot be driven is a REFUSAL, never a pass. REFUSED.")
    scratch = tempfile.mkdtemp(prefix="m6own_writer_selftest_")
    try:
        pat, A = W.classify_patches(l2_pm)
        if (pat["wall"] != "wing" or pat["symmetry"] != ["symmetry"]
                or pat["farfield"] != ["farfield"]):
            raise Refusal(f"selftest mesh patch names are {pat}, not the own-family set. "
                          "REFUSED.")
        uvec, _axes = W.freestream_vector(l2_pm, A)
        keep = W.K_INF
        bad = keep * 2.0 + 1.0
        case4 = os.path.join(scratch, "mutated")
        fooled = W._mutate_k_and_write(case4, l2_pm, pat, uvec, keep, bad)
        if fooled:
            raise InternalDefect(
                "PLANTED CONTROL DID NOT FIRE: a case written under a corrupted k_inf still "
                f"carried the registered value {keep!r}. The writer would not be shown able "
                "to write the value it claims. FAILED (rule 3).")
        # And the honest half: under the registered k_inf the value IS present.
        case_ok = os.path.join(scratch, "clean")
        os.makedirs(os.path.join(case_ok, "constant"), exist_ok=True)
        shutil.copytree(l2_pm, os.path.join(case_ok, "constant", "polyMesh"))
        W.write_zero(case_ok, pat, uvec)
        if f"uniform {keep!r};" not in open(os.path.join(case_ok, "0", "k")).read():
            raise InternalDefect(
                "the case written under the REGISTERED k_inf does NOT carry it; the reader is "
                "blind to the very value the control mutates. FAILED (rule 3).")
        print("SELFTEST PASS: planted-k control fired (corrupted k_inf NOT written; registered "
              f"k_inf {keep!r} present under clean write).")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True, description=__doc__)
    ap.add_argument("--level", choices=OWN_LEVELS, help="L2 / L1 / L0 (coarse -> fine)")
    ap.add_argument("--solve", help="the solve case directory to write into "
                                    "(must already carry constant/polyMesh)")
    ap.add_argument("--ranks", type=int, help="decomposition ranks (L2=4, L1=8, L0=14)")
    ap.add_argument("--end-time", dest="end_time", type=int,
                    help="solver endTime in iterations (6000 per level, prereg 7.2)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted-k control and exit (writes nothing under solve)")
    args = ap.parse_args(argv[1:])

    if args.selftest:
        try:
            return selftest()
        except Refusal as exc:
            sys.stderr.write(f"REFUSAL (selftest): {exc}\n"); return 2
        except InternalDefect as exc:
            sys.stderr.write(f"INTERNAL DEFECT (selftest): {exc}\n"); return 70

    missing = [n for n, v in (("--level", args.level), ("--solve", args.solve),
                              ("--ranks", args.ranks), ("--end-time", args.end_time))
               if v is None]
    if missing:
        sys.stderr.write(f"REFUSAL: missing required argument(s): {', '.join(missing)}. "
                         "This writer authors no case with an unspecified level/solve/ranks/"
                         "endTime.\n")
        return 2
    try:
        prov = write_own_case(args.solve, args.level, args.ranks, args.end_time)
    except Refusal as exc:
        sys.stderr.write(f"REFUSAL: {exc}\n"); return 2
    except W.Refusal as exc:
        sys.stderr.write(f"REFUSAL (reused pinned writer): {exc}\n"); return 2
    except W.InternalDefect as exc:
        sys.stderr.write(f"INTERNAL DEFECT (reused pinned writer): {exc}\n"); return 70
    except InternalDefect as exc:
        sys.stderr.write(f"INTERNAL DEFECT: {exc}\n"); return 70
    print(f"WROTE own-family case: level {prov['level']}, {len(prov['written'])} files into "
          f"{prov['solve_case']} (ranks {prov['ranks']}, endTime {prov['end_time']}, patches "
          f"wall={prov['patches_by_TYPE_never_by_name']['wall']} "
          f"symmetry={prov['patches_by_TYPE_never_by_name']['symmetry']} "
          f"farfield={prov['patches_by_TYPE_never_by_name']['farfield']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
