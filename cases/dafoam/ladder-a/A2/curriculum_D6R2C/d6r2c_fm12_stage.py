#!/usr/bin/env python3
# ===========================================================================
# d6r2c_fm12_stage.py -- THE ONE REGISTERED CHANGE OF ARM FM12
#                        M0b (PROVENANCE, for Zb) and M0o (DIFFERENCE, for Zo)
# ===========================================================================
#
# Registered by PREREGISTRATION_FM12_MATCHED_LIFT_PROVENANCE.md sections 2, 3
# and 6, and IN THE SAME COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS
# (CLAUDE.md rule 2).
#
# WHY THIS FILE EXISTS, IN ONE SENTENCE.  `FM11` was graded `BLOCKED` at its
# first staging step because the INHERITED `d6r2c_fm9_stage.py:95-100` raises
# `REFUSE_FRESH_IS_BASE` when the generated mesh's `points.gz` md5 equals the
# base mesh's -- and `FM11` introduced the state `Zb`, FOR WHICH THAT IDENTITY
# IS THE CORRECT AND EXPECTED OUTCOME.  MEASURED on FM11's own disk:
#
#     /home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM11-a2-wing-matched-lift/
#         FM11/Zb/constant/polyMesh/points.gz   md5 0fb1935a9b8781b73ac4ccb136e3ec68
#     .../CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/
#         base/constant/polyMesh/points.gz      md5 0fb1935a9b8781b73ac4ccb136e3ec68
#
# A mesh generated at ZERO shape from the BASE surface *should* be the base mesh.
# The inherited guard was written for FM9/FM10, where "fresh" always meant THE
# OPTIMUM'S mesh, so identity with base could only mean the staging had silently
# reused the base.  IT CANNOT TELL THE TWO SITUATIONS APART.  This is L-593:
# A PIN PROVES WHAT A FILE IS, NOT WHAT IT NEEDS.
#
# THE REPAIR, AND THE LINE THAT IS NOT CROSSED.  `M0`'s real purpose is to prove
# THE ARM'S OWN EXTRUSION ACTUALLY RAN and the mesh was not silently inherited.
# There are TWO gates here, not one relaxed gate covering both:
#
#   M0o  (sub-arm Zo) -- evidenced by DIFFERENCE FROM BASE, exactly as before.
#        `max_point_difference(generated, base) > 0.0`, strictly.  NOT WEAKENED
#        BY ONE BIT: the condition, the comparison and the refusal are the same
#        as `d6r2c_fm11_states.measure_against_base`'s `Zo` limb.
#
#   M0b  (sub-arm Zb) -- evidenced by PROVENANCE, because difference-from-base
#        is not available to it and inventing a tolerance would be exactly the
#        relaxation this file exists to avoid.  FOUR LIMBS, all refusing:
#          M0b.1  every build artifact `phase_mesh` writes EXISTS, and every one
#                 is NEWER THAN THE ARM'S OWN AGE DATUM (CLAUDE.md rule 4's age
#                 guard, applied to the mesh instead of to a field).  This is
#                 the load-bearing limb and it is LIVE-CONTROLLED: the seeded
#                 condition cases carry the base mesh at its PRESERVED mtime
#                 (`cp -a`), MEASURED 2026-07-28T00:18:12Z against FM11's datum
#                 of 2026-09-13T17:33:21Z -- 47.7 days older -- so a mesh that
#                 was silently inherited is 47.7 days too old to pass.
#          M0b.2  `mesh_generation.log` carries the step banner of EVERY step
#                 `phase_mesh` runs, in order.  An inherited mesh has no log.
#          M0b.3  the BUILD ORDER in time: surfaceMesh.cgns <= volumeMesh.xyz
#                 <= constant/polyMesh/points.  The extrusion's causal chain.
#          M0b.4  `mesh_rc.txt` reads 0, and the input surface `surfaceMesh.cgns`
#                 IS the registered base surface by md5 -- so "generated at zero
#                 shape from the base surface" is a checked claim, not a label.
#        And the fifth limb, which cannot run here because the solver has not
#        started yet, is carried by the producer and re-measured by the grader:
#          M0b.5  the polyMesh THE SOLVER ACTUALLY READ, rebuilt from its own
#                 `pointProcAddressing`, equals the mesh this arm generated.
#                 HONEST STATEMENT: this is the same measurement as `M1`
#                 restricted to `Zb`.  It is cited under M0b's name so that
#                 M0b's claim is evidenced rather than assumed; it is NOT a
#                 second independent reading and is not presented as one.
#
# WHY THE COPY LOOP IS SPELLED HERE AND NOT IMPORTED.  `d6r2c_fm9_stage.py` is a
# FROZEN instrument of FM9 and is NEVER EDITED (rule 6).  Its `stage_mesh()`
# FUSES the identity guard with the copying, so the operative half cannot be
# reached without the half that is wrong for `Zb`.  EVERY READER AND EVERY
# CONSTANT IS IMPORTED FROM IT AND NONE IS RE-TYPED (L-221/L-222); only the
# per-condition copy-and-remove loop is re-spelled -- and `--selftest` drives
# BOTH implementations on identical synthetic trees and REQUIRES THEIR RECORDS
# TO AGREE FIELD FOR FIELD, so the re-spelling cannot have drifted.
#
# HONEST GAP, NAMED BEFORE IT IS DISCOVERED.  This file has never run inside the
# container.  `--selftest` drives the pure logic and every refusal on synthetic
# trees; `--live-controls` drives M0b and M0o TO THEIR FAILING SIDES against the
# REAL artifacts FM11 left on disk, which is the part that CAN be exercised
# outside the container.
# ===========================================================================
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d6r2c_fm9_stage as stg          # noqa: E402  the readers and the constants

# ---- IMPORTED, NEVER RE-TYPED (L-221/L-222) -------------------------------
RUN_DIRS = stg.RUN_DIRS
MESH_FILES = stg.MESH_FILES
BASE_POINTS_MD5 = stg.BASE_POINTS_MD5
STALE_PROC_POINTS_MD5 = stg.STALE_PROC_POINTS_MD5
_md5 = stg._md5
read_points = stg.read_points
max_point_difference = stg.max_point_difference
processor_dirs = stg.processor_dirs
_open_either = stg._open_either

RECORD = "d6r2c_fm12_stage.json"

# ---- THE BUILD ARTIFACTS `d6r2c_freshmesh.py:phase_mesh` WRITES ------------
# Read off that function's own body (lines 384-407 of the frozen file): it
# stages the surface as surfaceMesh.cgns, runs genWingMesh.py which writes
# volumeMesh.xyz, appends every step to the log, and writes mesh_rc.txt last.
MESH_BUILD_ARTIFACTS = ("surfaceMesh.cgns", "volumeMesh.xyz",
                        "mesh_generation.log", "mesh_rc.txt")
# the five steps, in the order phase_mesh runs them.  The banner it writes is
# "\n=== <the whole command> ===\n", so a SUBSTRING of each command identifies it.
MESH_STEP_BANNERS = ("genWingMesh.py", "plot3dToFoam", "autoPatch",
                     "createPatch", "renumberMesh")
# the causal chain of the extrusion, in time order
BUILD_ORDER = ("surfaceMesh.cgns", "volumeMesh.xyz", "constant/polyMesh/points")
# the family script's own unmodified surface -- the launcher's MD5_SURFACE pin
BASE_SURFACE_MD5 = "3050ea454c2d0304bafa2c1a80c53b76"

Refusal = stg.Refusal


# ---------------------------------------------------------------------------
# M0o -- THE Zo GATE.  DIFFERENCE FROM BASE.  NOT WEAKENED BY ONE BIT.
# ---------------------------------------------------------------------------

def _read_registered_base(arm_dir, token):
    """The base mesh, identified by md5 before it is read.

    IT IS READ FROM mp04/constant/polyMesh, BEFORE STAGING, because `--phase
    mesh` has already overwritten arm_dir/constant/polyMesh with the generated
    mesh by the time this runs."""
    src = os.path.join(arm_dir, RUN_DIRS[0], "constant", "polyMesh")
    path = _open_either(os.path.join(src, "points"))
    got = _md5(path)
    if got != BASE_POINTS_MD5:
        raise Refusal("%s %s hashes %s, not the registered base mesh %s -- this "
                      "clause cannot compare against a mesh it cannot identify"
                      % (token, path, got, BASE_POINTS_MD5))
    return read_points(path), got, path


def m0o_decide(generated, base, base_md5="(identified by the caller)"):
    """THE DECISION, AS A PURE FUNCTION OVER TWO POINT CLOUDS.

    Deliberately pure: that is what lets a check OUTSIDE this file -- and the
    selftest, which cannot hold a cloud hashing to the registered base md5 --
    drive the gate to its failing side with a planted cloud.  A gate that can
    only be pointed at a live run can only ever be tested against whatever the
    run happens to do."""
    worst = max_point_difference(generated, base)
    if worst <= 0.0:
        raise Refusal(
            "REFUSE_M0O_MESH_IS_BASE the generated mesh reproduces the base "
            "mesh to %.17g m.  The deformation never reached the mesher and "
            "J_opt_fresh would be the base geometry's drag under another name"
            % worst)
    return {"gate": "M0o", "sub_arm": "Zo",
            "max_point_difference_from_base_m": worst,
            "base_points_md5": base_md5,
            "differs_from_base": True,
            "n_generated_points": len(generated),
            "role": "GATED ON DIFFERENCE.  The Zo mesh is extruded around the "
                    "FFD-updated surface and MUST differ from the base mesh.  "
                    "This condition is FM11's, unchanged: `worst > 0.0`, "
                    "strictly, with no tolerance of any kind.",
            "pass": True}


def gate_m0o(arm_dir, generated):
    """M0o: the Zo mesh MUST differ from the base mesh.  Identify the base, then
    decide.  The decision is `m0o_decide`, unchanged from FM11's own Zo limb."""
    base, got, _p = _read_registered_base(arm_dir, "REFUSE_M0O_NOT_THE_BASE_MESH")
    return m0o_decide(generated, base, got)


# ---------------------------------------------------------------------------
# M0b -- THE Zb GATE.  PROVENANCE, BECAUSE DIFFERENCE IS NOT AVAILABLE TO IT.
# ---------------------------------------------------------------------------

def _mtime(p):
    return os.stat(p).st_mtime


def _either(p):
    """The file, whether OpenFOAM wrote it compressed or plain, or None.
    NEVER a guess: the caller is handed the path that actually exists."""
    cands = [p]
    if p.endswith(".gz"):
        cands.append(p[:-3])
    else:
        cands.append(p + ".gz")
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def m0b_provenance(arm_dir, datum_epoch):
    """THE FOUR PROVENANCE LIMBS, as a function of the arm directory and the
    clock ALONE -- it never touches the base mesh and never compares point
    clouds, deliberately, so that a check outside this file can drive every one
    of them to its failing side without holding a cloud that hashes to the
    registered base md5.

    The arm's own extrusion RAN, proved by its build artifacts and their
    times -- never by what the mesh equals.

    `datum_epoch` is the arm's age datum: the launcher touches it AFTER every
    input is staged and BEFORE the container starts, so anything the arm itself
    produced is newer than it and anything seeded is older (CLAUDE.md rule 4)."""
    if datum_epoch is None:
        raise Refusal("REFUSE_M0B_NO_DATUM -- the age guard has no datum, and a "
                      "provenance gate with no clock is not a gate (rule 4)")
    datum_epoch = float(datum_epoch)
    rec = {"gate": "M0b", "sub_arm": "Zb", "datum_epoch": datum_epoch,
           "artifacts": {}, "steps_found": [], "build_order": []}

    # ---- M0b.1  EVERY BUILD ARTIFACT EXISTS AND IS NEWER THAN THE DATUM -----
    named = list(MESH_BUILD_ARTIFACTS) + [
        os.path.join("constant", "polyMesh", f) for f in MESH_FILES]
    for rel in named:
        p = _either(os.path.join(arm_dir, rel))
        if p is None:
            raise Refusal("REFUSE_M0B_NO_BUILD_ARTIFACT %s -- the extrusion's "
                          "own output is absent, so there is no evidence this "
                          "arm's mesher ran at all"
                          % os.path.join(arm_dir, rel))
        t = _mtime(p)
        rec["artifacts"][rel] = {"mtime": t, "newer_than_datum": t >= datum_epoch}
        if t < datum_epoch:
            raise Refusal(
                "REFUSE_M0B_STALE_ARTIFACT %s was written %.0f s BEFORE this "
                "arm's age datum (%.0f vs %.0f).  It was not produced by this "
                "arm's extrusion -- it was inherited, which is exactly what M0 "
                "exists to catch (CLAUDE.md rule 4)"
                % (p, datum_epoch - t, t, datum_epoch))

    # ---- M0b.2  EVERY MESH STEP LEFT ITS BANNER, IN ORDER -------------------
    log = open(os.path.join(arm_dir, "mesh_generation.log"), errors="replace").read()
    pos = -1
    for needle in MESH_STEP_BANNERS:
        i = log.find("=== ", pos + 1)
        found = -1
        while i >= 0:
            line = log[i:log.find("\n", i) if log.find("\n", i) > 0 else len(log)]
            if needle in line:
                found = i
                break
            i = log.find("=== ", i + 1)
        if found < 0:
            raise Refusal("REFUSE_M0B_NO_MESH_STEP the extrusion log carries no "
                          "banner for %r after position %d -- the step either "
                          "never ran or ran out of order" % (needle, pos))
        rec["steps_found"].append({"step": needle, "at_char": found})
        pos = found

    # ---- M0b.3  THE BUILD ORDER IN TIME -------------------------------------
    prev_name, prev_t = None, None
    for rel in BUILD_ORDER:
        p = os.path.join(arm_dir, rel)
        p = _either(p)
        if p is None:
            raise Refusal("REFUSE_M0B_NO_BUILD_ARTIFACT %s -- the build order "
                          "cannot be read without it"
                          % os.path.join(arm_dir, rel))
        t = _mtime(p)
        rec["build_order"].append({"artifact": rel, "mtime": t})
        if prev_t is not None and t < prev_t:
            raise Refusal("REFUSE_M0B_BUILD_ORDER %s (%.0f) is OLDER than %s "
                          "(%.0f) -- the extrusion's causal chain does not hold "
                          "and the mesh did not come from this surface"
                          % (rel, t, prev_name, prev_t))
        prev_name, prev_t = rel, t

    # ---- M0b.4  THE MESHER SUCCEEDED, ON THE REGISTERED BASE SURFACE --------
    rc_txt = open(os.path.join(arm_dir, "mesh_rc.txt")).read().strip()
    rec["mesh_rc"] = rc_txt
    if rc_txt != "0":
        raise Refusal("REFUSE_M0B_MESH_RC mesh_rc.txt reads %r, not 0 -- the "
                      "extrusion did not succeed" % rc_txt)
    surf = os.path.join(arm_dir, "surfaceMesh.cgns")
    got = _md5(surf)
    rec["surface_md5"] = got
    rec["surface_md5_registered"] = BASE_SURFACE_MD5
    if got != BASE_SURFACE_MD5:
        raise Refusal("REFUSE_M0B_NOT_BASE_SURFACE %s hashes %s, not the "
                      "registered base surface %s -- 'generated at zero shape "
                      "from the base surface' is then a label, not a fact"
                      % (surf, got, BASE_SURFACE_MD5))
    rec["pass"] = True
    return rec


def gate_m0b(arm_dir, datum_epoch, generated):
    """M0b: the four provenance limbs, plus R1 measured against the registered
    base mesh.  R1 is MEASURED here and GATED BY THE GRADER; it never refuses."""
    rec = m0b_provenance(arm_dir, datum_epoch)
    base, bgot, bpath = _read_registered_base(
        arm_dir, "REFUSE_M0B_NOT_THE_BASE_MESH")
    gpath = _open_either(os.path.join(arm_dir, "constant", "polyMesh", "points"))
    rec["R1"] = r1_measure(generated, base, gpath, bpath, bgot)
    rec["role"] = ("GATED ON PROVENANCE.  The Zb mesh is extruded around the "
                   "BASE surface by the same family script at the same "
                   "parameters, so reproducing the base mesh is the EXPECTATION "
                   "and difference-from-base carries no information here.  What "
                   "M0 must prove -- that THIS ARM'S extrusion ran and the mesh "
                   "was not silently inherited -- is proved by the build "
                   "artifacts and their times instead.")
    return rec


def r1_measure(generated, base, gpath, bpath, base_md5):
    """R1 -- MESHER DETERMINISM ACROSS TIME.  A PURE MEASUREMENT, taken here and
    GATED BY THE GRADER; it never flips this arm's label.

    Pure over the two clouds and the two paths, so that a check outside this
    file can drive it with a planted cloud."""
    worst = max_point_difference(generated, base)
    n_ident = sum(1 for a, b in zip(generated, base) if a == b)
    gm5 = _md5(gpath)
    gz_g, gz_b = _gzip_mtime_field(gpath), _gzip_mtime_field(bpath)
    return {
        "clause": "R1 -- MESHER DETERMINISM ACROSS TIME",
        "max_point_difference_from_base_m": worst,
        "n_points": len(base),
        "n_points_identical": n_ident,
        "all_points_identical": n_ident == len(base),
        "generated_points_md5": gm5,
        "base_points_md5": base_md5,
        "md5_identical": gm5 == base_md5,
        "elapsed_days": (_mtime(gpath) - _mtime(bpath)) / 86400.0,
        "base_points_mtime": _mtime(bpath),
        "generated_points_mtime": _mtime(gpath),
        "gzip_mtime_field_generated": gz_g,
        "gzip_mtime_field_base": gz_b,
        "gzip_mtime_field_is_zero": gz_g == 0 and gz_b == 0,
        "why_md5_is_meaningful_here":
            "OpenFOAM writes its .gz with the gzip header MTIME field set to 0, "
            "READ BACK from both files above.  md5 identity is therefore a true "
            "statement about the POINTS and not an artefact of two files having "
            "been written at the same second.  When either field is NOT zero "
            "the md5 claim is withdrawn and only the point measurement stands.",
        "role": "MEASURED HERE, GATED BY THE GRADER, AND IT NEVER FLIPS THIS "
                "ARM'S LABEL.  This arm's question is the drag ratio.",
    }


def _gzip_mtime_field(path):
    """The MTIME field of a gzip header, or None for a plain file.  Read so that
    R1's md5 claim is checked rather than asserted."""
    with open(path, "rb") as fh:
        h = fh.read(10)
    if len(h) < 10 or h[0] != 0x1F or h[1] != 0x8B:
        return None
    return int.from_bytes(h[4:8], "little")


# ---------------------------------------------------------------------------
# THE STAGING.  THE OPERATIVE HALF IS THE REMOVAL OF THE STALE DECOMPOSITION.
# ---------------------------------------------------------------------------

def stage_mesh(arm_dir, sub_arm, datum_epoch=None, run_dirs=RUN_DIRS,
               _skip_gate=False):
    """Put the generated mesh into every condition case and REMOVE the stale
    decomposition, AFTER the sub-arm's own extrusion-evidence gate has passed.

    THE REMOVAL IS THE OPERATIVE HALF.  Copying the mesh into
    mp0X/constant/polyMesh changes nothing on its own: DAFoam decomposes only
    when processorN/ is ABSENT, and if a decomposition is already there it reads
    that instead -- which is precisely how FM5, FM7 and FM8 solved on a mesh they
    had not generated (`d6r2c_fm9_stage.py`'s own header records the measurement).

    THE BODY BELOW IS THE INHERITED LOOP, RE-SPELLED BECAUSE THE FROZEN FILE
    FUSES IT WITH A GUARD THAT IS WRONG FOR Zb AND MAY NOT BE EDITED (rule 6).
    `--selftest` drives both implementations on identical trees and requires
    their records to agree field for field."""
    if sub_arm not in ("Zb", "Zo"):
        raise Refusal("REFUSE_UNKNOWN_SUB_ARM %r -- this file gates two sub-arms "
                      "and will not guess which gate a third one wants" % sub_arm)
    src = os.path.join(arm_dir, "constant", "polyMesh")
    if not os.path.isdir(src):
        raise Refusal("REFUSE_NO_FRESH_MESH %s -- phase mesh must run first" % src)
    for f in MESH_FILES:
        if not os.path.isfile(os.path.join(src, f)):
            raise Refusal("REFUSE_INCOMPLETE_FRESH_MESH %s missing from %s"
                          % (f, src))
    gpath = _open_either(os.path.join(src, "points"))
    fresh_md5 = _md5(gpath)

    # ---- THE GATE, BEFORE ANYTHING IS COPIED -------------------------------
    # The point cloud is read ONLY when a gate needs it; `_skip_gate` exists for
    # the equivalence control alone, which drives the copy loop against the
    # frozen implementation on a fixture that carries no readable point file.
    if _skip_gate:
        m0 = {"gate": "SKIPPED -- selftest equivalence control only", "pass": True}
    elif sub_arm == "Zo":
        m0 = gate_m0o(arm_dir, read_points(gpath))
    else:
        m0 = gate_m0b(arm_dir, datum_epoch, read_points(gpath))

    rec = {"kind": "FM12_STAGE", "sub_arm": sub_arm,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "uid": os.getuid(), "gid": os.getgid(),
           "fresh_points_md5": fresh_md5,
           "base_points_md5": BASE_POINTS_MD5,
           "stale_processor_points_md5": STALE_PROC_POINTS_MD5,
           "fresh_equals_base": fresh_md5 == BASE_POINTS_MD5,
           "fresh_equals_base_is_expected_here": sub_arm == "Zb",
           "M0": m0, "conditions": {}}

    for mp in run_dirs:
        dst_case = os.path.join(arm_dir, mp)
        if not os.path.isdir(dst_case):
            raise Refusal("REFUSE_NO_CONDITION_CASE %s" % dst_case)
        dst = os.path.join(dst_case, "constant", "polyMesh")
        before_p = os.path.join(dst, "points.gz")
        before = _md5(before_p) if os.path.isfile(before_p) else None
        os.makedirs(dst, exist_ok=True)
        for f in MESH_FILES:
            s = os.path.join(src, f)
            d = os.path.join(dst, f)
            for stale in (d, d + ".gz", d[:-3] if d.endswith(".gz") else d + ".gz"):
                if os.path.isfile(stale) and stale != s:
                    os.remove(stale)
            shutil.copyfile(s, d)
        after = _md5(os.path.join(dst, "points.gz"))
        if after != fresh_md5:
            raise Refusal("REFUSE_STAGE_READBACK %s/constant/polyMesh/points.gz "
                          "reads %s after the copy, not the fresh %s"
                          % (mp, after, fresh_md5))
        removed = []
        for pd in processor_dirs(dst_case):
            shutil.rmtree(os.path.join(dst_case, pd))
            removed.append(pd)
        left = processor_dirs(dst_case)
        if left:
            raise Refusal(
                "REFUSE_PROCESSOR_DIRS_REMAIN %s still carries %r after removal. "
                "THE SOLVER WOULD READ THEM INSTEAD OF DECOMPOSING THE FRESH "
                "MESH, which is exactly the FM5/FM7/FM8 defect" % (mp, left))
        rec["conditions"][mp] = {
            "constant_points_md5_before": before,
            "constant_points_md5_after": after,
            "was_base_before": before == BASE_POINTS_MD5,
            "processor_dirs_removed": removed,
            "processor_dirs_remaining": left,
        }
    rec["all_conditions_staged"] = len(rec["conditions"]) == len(run_dirs)
    return rec


# ---------------------------------------------------------------------------
# M0b.5 -- THE READ-BACK.  The polyMesh the SOLVER ACTUALLY READ.
# ---------------------------------------------------------------------------

def readback_m0b(arm_dir, generated, run_dirs=RUN_DIRS):
    """Rebuild, from each condition's own `pointProcAddressing`, the
    undecomposed mesh the solver loaded, and compare it for EXACT equality
    against the mesh this arm generated.

    HONEST STATEMENT: this is the same measurement the grader performs as `M1`,
    restricted to `Zb`.  It is recorded under M0b's name so that M0b's claim is
    evidenced rather than assumed.  It is NOT a second independent reading."""
    out = {"limb": "M0b.5", "conditions": {},
           "note": "the same measurement as M1 restricted to Zb, cited here so "
                   "M0b's claim about the mesh the SOLVER READ is evidenced"}
    ok = True
    for mp in run_dirs:
        mp_dir = os.path.join(arm_dir, mp)
        try:
            loaded = stg.reconstruct_loaded_points(mp_dir, len(generated))
            worst = max_point_difference(loaded, generated)
            row = {"max_point_difference_from_generated": worst,
                   "exact": worst == 0.0,
                   "n_processors": len(processor_dirs(mp_dir))}
        except Refusal as e:
            row = {"refusal": str(e), "exact": False,
                   "n_processors": len(processor_dirs(mp_dir))}
        ok = ok and row["exact"]
        out["conditions"][mp] = row
    out["pass"] = ok
    return out


# ---------------------------------------------------------------------------
# LIVE CONTROLS -- M0b AND M0o DRIVEN TO THEIR FAILING SIDES ON REAL ARTIFACTS
# ---------------------------------------------------------------------------
# These read FM11's own run root, which is GRADED (BLOCKED) and is READ-ONLY to
# this item.  Nothing here writes anything anywhere.
FM11_ARM = ("/home/ubuntu/certonomous-runs/"
            "CURRICULUM-D6R2C-FM11-a2-wing-matched-lift/FM11")
# the registered anchors on disk.  The selftest copies THESE into its fixtures
# rather than standing in for them, so its positive cases are driven against the
# real md5 the gate asserts -- never against a value the gate had to be loosened
# to accept.
REAL_BASE_SURFACE = "/home/ubuntu/certonomous-runs/A2-mach-wing/surfaceMesh.cgns"
REAL_BASE_POINTS = ("/home/ubuntu/certonomous-runs/"
                    "CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/"
                    "base/constant/polyMesh/points.gz")


def live_controls(arm_root=FM11_ARM):
    """The controls that matter, on real disk:

      * M0b PASSES on FM11's Zb, which really was extruded by its own arm;
      * M0b REFUSES when pointed at a mesh that was SEEDED and not generated --
        the condition case `mp04`, whose base mesh `cp -a` left dated
        2026-07-28, 47.7 days before FM11's datum.  This is the live failing
        control for the age limb;
      * M0o REFUSES on FM11's Zo, whose `constant/polyMesh` is still the seeded
        base mesh because the arm blocked before Zo's mesh phase ran.  This is
        the live failing control for the difference limb, and its refusal is
        the CORRECT answer: Zo never generated a mesh."""
    out = {"arm_root": arm_root, "controls": []}

    def add(name, ok, detail):
        out["controls"].append({"control": name, "ok": bool(ok), "detail": detail})

    zb = os.path.join(arm_root, "Zb")
    datum_file = os.path.join(arm_root, ".d6r2c_age_datum")
    if not os.path.isfile(datum_file):
        raise Refusal("REFUSE_NO_LIVE_DATUM %s -- the live controls have no "
                      "clock" % datum_file)
    datum = float(open(datum_file).read().strip())
    gen = read_points(_open_either(os.path.join(zb, "constant", "polyMesh", "points")))

    # (1) M0b passes on the real Zb
    try:
        r = gate_m0b(zb, datum, gen)
        add("M0b PASSES on FM11's real Zb, whose extrusion genuinely ran",
            r["pass"], {"n_artifacts": len(r["artifacts"]),
                        "steps": [s["step"] for s in r["steps_found"]],
                        "R1_max_point_difference_m": r["R1"]["max_point_difference_from_base_m"],
                        "R1_elapsed_days": round(r["R1"]["elapsed_days"], 4),
                        "R1_n_points_identical": "%d/%d" % (r["R1"]["n_points_identical"],
                                                            r["R1"]["n_points"]),
                        "R1_md5_identical": r["R1"]["md5_identical"],
                        "R1_gzip_mtime_field_is_zero": r["R1"]["gzip_mtime_field_is_zero"]})
        r1 = r["R1"]
    except Refusal as e:
        add("M0b PASSES on FM11's real Zb", False, str(e))
        r1 = None

    # (2) THE FAILING CONTROL FOR THE AGE LIMB, on real disk
    seeded = os.path.join(zb, "mp04")
    try:
        gate_m0b(seeded, datum, gen)
        add("M0b REFUSES a SEEDED mesh (the live failing control)", False,
            "it PASSED a directory whose mesh was copied in, not generated")
    except Refusal as e:
        tok = str(e).split()[0]
        add("M0b REFUSES a SEEDED mesh (the live failing control)",
            tok in ("REFUSE_M0B_NO_BUILD_ARTIFACT", "REFUSE_M0B_STALE_ARTIFACT"),
            {"token": tok, "message": str(e)[:400]})
    # and the age limb specifically, isolated: the seeded points really are older
    sp = _open_either(os.path.join(seeded, "constant", "polyMesh", "points"))
    add("the seeded mesh is measurably OLDER than the datum, so the age limb is "
        "not merely finding a missing file",
        _mtime(sp) < datum,
        {"seeded_points_mtime": _mtime(sp), "datum": datum,
         "days_older": round((datum - _mtime(sp)) / 86400.0, 4)})

    # THE AGE LIMB, DRIVEN ON ITS OWN, ON REAL BYTES.  The control above refused
    # on a MISSING artifact, which is a different limb; this one hands M0b a
    # tree that is complete in every other respect and differs ONLY in that its
    # polyMesh is the SEEDED one -- the precise situation M0 exists to catch:
    # a mesh that was inherited rather than generated by this arm.
    import tempfile
    t2 = tempfile.mkdtemp(prefix="d6r2c_fm12_agelimb_")
    try:
        for rel in MESH_BUILD_ARTIFACTS:
            s = _either(os.path.join(zb, rel))
            if s:
                shutil.copy2(s, os.path.join(t2, os.path.basename(s)))
        pm = os.path.join(t2, "constant", "polyMesh")
        os.makedirs(pm)
        for f in MESH_FILES:
            s = _either(os.path.join(seeded, "constant", "polyMesh", f))
            if s:
                shutil.copy2(s, os.path.join(pm, os.path.basename(s)))
        for mp in RUN_DIRS:
            d = os.path.join(t2, mp, "constant", "polyMesh")
            os.makedirs(d)
            for f in MESH_FILES:
                s = _either(os.path.join(seeded, "constant", "polyMesh", f))
                if s:
                    shutil.copy2(s, os.path.join(d, os.path.basename(s)))
        try:
            m0b_provenance(t2, datum)
            add("M0b's AGE LIMB refuses an INHERITED polyMesh in an otherwise "
                "complete tree (the isolated live failing control)", False,
                "it PASSED a tree whose mesh predates the arm by 47.7 days")
        except Refusal as e:
            tok = str(e).split()[0]
            add("M0b's AGE LIMB refuses an INHERITED polyMesh in an otherwise "
                "complete tree (the isolated live failing control)",
                tok == "REFUSE_M0B_STALE_ARTIFACT",
                {"token": tok, "message": str(e)[:300]})
    finally:
        shutil.rmtree(t2, ignore_errors=True)

    # (3) THE FAILING CONTROL FOR M0o, on real disk
    zo = os.path.join(arm_root, "Zo")
    try:
        zgen = read_points(_open_either(os.path.join(zo, "constant", "polyMesh", "points")))
        gate_m0o(zo, zgen)
        add("M0o REFUSES a Zo whose mesh is still the base mesh (the live "
            "failing control)", False, "it PASSED the un-extruded Zo")
    except Refusal as e:
        tok = str(e).split()[0]
        add("M0o REFUSES a Zo whose mesh is still the base mesh (the live "
            "failing control)", tok == "REFUSE_M0O_MESH_IS_BASE",
            {"token": tok, "message": str(e)[:400]})

    # (4) AND THE POSITIVE FOR M0o, so its green is not vacuous: a synthetic
    #     Zo built from the real base mesh with ONE point moved must PASS.
    import tempfile
    tmp = tempfile.mkdtemp(prefix="d6r2c_fm12_m0o_")
    try:
        mp = os.path.join(tmp, RUN_DIRS[0], "constant", "polyMesh")
        os.makedirs(mp)
        shutil.copyfile(_open_either(os.path.join(zb, "mp04", "constant",
                                                  "polyMesh", "points")),
                        os.path.join(mp, "points.gz"))
        moved = list(gen)
        moved[0] = (moved[0][0] + 1.0e-9, moved[0][1], moved[0][2])
        r = gate_m0o(tmp, moved)
        add("M0o PASSES a Zo mesh that differs from base by ONE NANOMETRE -- the "
            "gate is live, not merely refusing everything",
            r["pass"] and abs(r["max_point_difference_from_base_m"] - 1.0e-9) < 1e-18,
            {"max_point_difference_m": r["max_point_difference_from_base_m"]})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out["all_ok"] = all(c["ok"] for c in out["controls"])
    out["R1_measured"] = r1
    return out


# ---------------------------------------------------------------------------
# SELFTEST -- pure logic, plus the equivalence control against the frozen file
# ---------------------------------------------------------------------------

HDR = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
       "    object %s;\n}\n"
       "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")


def _synth_mp(root, pts, n_proc=4, time_name="1000"):
    """A synthetic decomposed condition case whose processor dirs carry `pts`.

    A FIXTURE, NOT A READER.  Every READER in this file is imported from the
    frozen `d6r2c_fm9_stage.py` and none is re-spelled (L-221/L-222); this
    writes test input and is spelled here so that the STAGED SET does not have
    to carry another arm's frozen producer just to run a selftest -- which is
    what `G-DEPS` caught when this fixture was imported instead."""
    os.makedirs(root, exist_ok=True)
    n = len(pts)
    per = (n + n_proc - 1) // n_proc
    for i in range(n_proc):
        ids = list(range(i * per, min(n, (i + 1) * per)))
        cpm = os.path.join(root, "processor%d" % i, "constant", "polyMesh")
        tpm = os.path.join(root, "processor%d" % i, time_name, "polyMesh")
        os.makedirs(cpm, exist_ok=True)
        os.makedirs(tpm, exist_ok=True)
        with open(os.path.join(cpm, "pointProcAddressing"), "w") as fh:
            fh.write("FoamFile\n{\n}\n// * * *\n\n%d\n(\n%s\n)\n"
                     % (len(ids), "\n".join(str(g) for g in ids)))
        for d in (cpm, tpm):
            with open(os.path.join(d, "points"), "w") as fh:
                fh.write("FoamFile\n{\n}\n// * * *\n\n%d\n(\n" % len(ids))
                for g in ids:
                    fh.write("(%.17g %.17g %.17g)\n" % pts[g])
                fh.write(")\n")


def _mk_tree(root, fresh_tag="FRESH", n_mp=3, with_procs=True):
    """A synthetic arm the copy loop can actually stage."""
    src = os.path.join(root, "constant", "polyMesh")
    os.makedirs(src, exist_ok=True)
    for f in MESH_FILES:
        with open(os.path.join(src, f), "w") as fh:
            fh.write("%s %s\n" % (fresh_tag, f))
    for mp in RUN_DIRS[:n_mp]:
        d = os.path.join(root, mp, "constant", "polyMesh")
        os.makedirs(d, exist_ok=True)
        for f in MESH_FILES:
            with open(os.path.join(d, f), "w") as fh:
                fh.write("BASE %s\n" % f)
        if with_procs:
            for k in range(4):
                p = os.path.join(root, mp, "processor%d" % k, "constant", "polyMesh")
                os.makedirs(p, exist_ok=True)
                with open(os.path.join(p, "points.gz"), "w") as fh:
                    fh.write("STALE\n")
    return root


def _mk_zb(root, datum, good=True, drop=None, rc="0", surface_ok=True,
           steps=MESH_STEP_BANNERS, order_ok=True, base_pts=None, gen_pts=None):
    """A synthetic Zb sub-arm with real build artifacts and controllable mtimes."""
    os.makedirs(root, exist_ok=True)
    base_pts = base_pts or [(float(i), 0.0, 0.0) for i in range(6)]
    gen_pts = gen_pts if gen_pts is not None else list(base_pts)
    pm = os.path.join(root, "constant", "polyMesh")
    os.makedirs(pm, exist_ok=True)
    for f in MESH_FILES:
        if f == "points.gz":
            continue
        open(os.path.join(pm, f), "w").write("TOPO %s\n" % f)
    _wpts(os.path.join(pm, "points"), gen_pts)
    # the base mesh sits in mp04, as the launcher seeds it
    for mp in RUN_DIRS:
        d = os.path.join(root, mp, "constant", "polyMesh")
        os.makedirs(d, exist_ok=True)
        _wpts(os.path.join(d, "points"), base_pts)
        for f in MESH_FILES:
            if f != "points.gz":
                open(os.path.join(d, f), "w").write("TOPO %s\n" % f)
    # THE REGISTERED BASE SURFACE ITSELF, when it is on disk -- so the positive
    # case is driven against the REAL anchor and not against a stand-in that
    # would need the gate relaxed to accept it.
    if surface_ok and os.path.isfile(REAL_BASE_SURFACE):
        shutil.copyfile(REAL_BASE_SURFACE, os.path.join(root, "surfaceMesh.cgns"))
    else:
        open(os.path.join(root, "surfaceMesh.cgns"), "w").write(
            "SURFACE_BASE\n" if surface_ok else "SURFACE_DEFORMED\n")
    open(os.path.join(root, "volumeMesh.xyz"), "w").write("PLOT3D\n")
    open(os.path.join(root, "mesh_generation.log"), "w").write(
        "".join("\n=== %s ===\nstep output\n" % s for s in steps))
    open(os.path.join(root, "mesh_rc.txt"), "w").write(rc)
    t = datum + 10.0
    for rel in ("surfaceMesh.cgns", "volumeMesh.xyz", "mesh_generation.log",
                "mesh_rc.txt"):
        os.utime(os.path.join(root, rel), (t, t))
    order = {"surfaceMesh.cgns": datum + 5.0, "volumeMesh.xyz": datum + 7.0}
    for rel, tt in order.items():
        os.utime(os.path.join(root, rel), (tt, tt))
    for f in MESH_FILES:
        p = os.path.join(pm, f if os.path.isfile(os.path.join(pm, f)) else "points")
        tt = datum + (3.0 if not order_ok else 9.0)
        os.utime(p, (tt, tt))
    if drop:
        os.remove(os.path.join(root, drop))
    if not good:
        p = os.path.join(root, "volumeMesh.xyz")
        os.utime(p, (datum - 1000.0, datum - 1000.0))
    return root


def _wpts(path, pts):
    with open(path, "w") as fh:
        fh.write(HDR % ("vectorField", "points")
                 + "%d\n(\n%s\n)\n" % (len(pts),
                                       "\n".join("(%.17g %.17g %.17g)" % p for p in pts)))


def selftest():
    import tempfile
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r"
                  % (name, got, want))

    tmp = tempfile.mkdtemp(prefix="d6r2c_fm12_stage_selftest_")
    try:
        # ==== THE EQUIVALENCE CONTROL AGAINST THE FROZEN FILE ================
        # Two identical trees; the inherited stage_mesh on one, this file's on
        # the other, on a Zo-shaped case where BOTH are legal.  Their
        # per-condition records must agree FIELD FOR FIELD.
        a = _mk_tree(os.path.join(tmp, "eq_inherited"))
        b = _mk_tree(os.path.join(tmp, "eq_fm12"))
        ra = stg.stage_mesh(a)
        rb = stage_mesh(b, "Zo", _skip_gate=True)
        check("the re-spelled loop stages every condition, as the frozen one does",
              rb["all_conditions_staged"], ra["all_conditions_staged"])
        check("EQUIVALENCE: the per-condition records agree FIELD FOR FIELD with "
              "the frozen d6r2c_fm9_stage.stage_mesh",
              rb["conditions"], ra["conditions"])
        check("...and the fresh hash agrees too",
              rb["fresh_points_md5"], ra["fresh_points_md5"])
        check("no processor directory survives, in either implementation",
              sum(len(processor_dirs(os.path.join(b, mp))) for mp in RUN_DIRS), 0)

        # ==== M0o, IN BOTH DIRECTIONS ========================================
        # THE DECISION is driven directly, because no cloud built here can hash
        # to the registered base md5 -- and a gate that can only be exercised by
        # the live run can only be tested against what the run happens to do.
        base = [(float(i), 0.0, 0.0) for i in range(6)]
        try:
            m0o_decide(list(base), base)
            check("M0o refuses a mesh identical to base", "no refusal", "Refusal")
        except Refusal as e:
            check("M0o -> REFUSE_M0O_MESH_IS_BASE",
                  str(e).startswith("REFUSE_M0O_MESH_IS_BASE"), True)
            check("...and the refusal says J_opt_fresh would be the base "
                  "geometry's drag under another name",
                  "under another name" in str(e), True)
        moved = list(base)
        moved[2] = (2.0, 1.0e-12, 0.0)
        r = m0o_decide(moved, base)
        check("M0o PASSES a mesh that differs by ONE PICOMETRE", r["pass"], True)
        check("...and reports the difference it saw",
              abs(r["max_point_difference_from_base_m"] - 1.0e-12) < 1e-24, True)
        # and the identification limb, driven on a tree whose mp04 is not base
        zo = _mk_zb(os.path.join(tmp, "zo"), 1000.0, base_pts=base, gen_pts=base)
        try:
            gate_m0o(zo, base)
            check("M0o refuses an unidentifiable base", "no refusal", "Refusal")
        except Refusal as e:
            check("a base mesh at the wrong md5 -> REFUSE_M0O_NOT_THE_BASE_MESH",
                  str(e).startswith("REFUSE_M0O_NOT_THE_BASE_MESH"), True)
        # THE CONDITION IS FM11's, UNCHANGED -- asserted on this file's own
        # source, so a future edit that introduces a tolerance fails here.
        check("M0o's condition is `worst <= 0.0 -> refuse`, the same test FM11's "
              "own Zo limb ran, with no tolerance introduced",
              "if worst <= 0.0:" in open(__file__).read(), True)

        # ==== M0b, IN BOTH DIRECTIONS ========================================
        D = 100000.0
        zb = _mk_zb(os.path.join(tmp, "zb"), D, base_pts=base, gen_pts=base)
        r = m0b_provenance(zb, D)
        check("M0b PASSES a Zb whose extrusion left every artifact after the datum",
              r["pass"], True)
        check("...and it names all five mesh steps, in order",
              [s["step"] for s in r["steps_found"]], list(MESH_STEP_BANNERS))
        check("...and every named artifact is recorded as newer than the datum",
              sorted({v["newer_than_datum"] for v in r["artifacts"].values()}),
              [True])
        check("...and the artifact list covers the four phase_mesh outputs plus "
              "the whole polyMesh", len(r["artifacts"]),
              len(MESH_BUILD_ARTIFACTS) + len(MESH_FILES))

        # THE POINT OF THE WHOLE ARM: M0b passes a mesh IDENTICAL to the base.
        r1 = r1_measure(base, base, os.path.join(zb, "constant", "polyMesh", "points"),
                        os.path.join(zb, "mp04", "constant", "polyMesh", "points"),
                        _md5(os.path.join(zb, "mp04", "constant", "polyMesh", "points")))
        check("R1 measures ZERO difference on the exact case the inherited guard "
              "refused, which is what blocked FM11",
              r1["max_point_difference_from_base_m"], 0.0)
        check("...and counts every point as identical", r1["all_points_identical"], True)
        # ...and R1 is not blind: a one-nanometre move is visible
        m = list(base)
        m[1] = (1.0, 1.0e-9, 0.0)
        r1b = r1_measure(m, base, os.path.join(zb, "constant", "polyMesh", "points"),
                         os.path.join(zb, "mp04", "constant", "polyMesh", "points"), "x")
        check("R1 SEES a one-nanometre drift, so its zero is not a blind zero",
              abs(r1b["max_point_difference_from_base_m"] - 1.0e-9) < 1e-18, True)
        check("...and stops calling the points identical",
              r1b["all_points_identical"], False)
        check("R1 withdraws the md5 claim when a gzip MTIME field is not zero",
              r1["gzip_mtime_field_is_zero"], False)   # plain files -> None != 0

        # ---- EVERY PROVENANCE LIMB, DRIVEN TO ITS FAILING SIDE --------------
        # the age limb -- the load-bearing one
        stale = _mk_zb(os.path.join(tmp, "stale"), D, good=False,
                       base_pts=base, gen_pts=base)
        try:
            m0b_provenance(stale, D)
            check("M0b refuses a stale artifact", "no refusal", "Refusal")
        except Refusal as e:
            check("an artifact older than the datum -> REFUSE_M0B_STALE_ARTIFACT",
                  str(e).startswith("REFUSE_M0B_STALE_ARTIFACT"), True)
        # a missing artifact
        miss = _mk_zb(os.path.join(tmp, "miss"), D, drop="volumeMesh.xyz",
                      base_pts=base, gen_pts=base)
        try:
            m0b_provenance(miss, D)
            check("M0b refuses a missing artifact", "no refusal", "Refusal")
        except Refusal as e:
            check("a missing artifact -> REFUSE_M0B_NO_BUILD_ARTIFACT",
                  str(e).startswith("REFUSE_M0B_NO_BUILD_ARTIFACT"), True)
        # a missing mesh step
        nostep = _mk_zb(os.path.join(tmp, "nostep"), D, base_pts=base, gen_pts=base,
                        steps=("genWingMesh.py", "plot3dToFoam", "createPatch",
                               "renumberMesh"))
        try:
            m0b_provenance(nostep, D)
            check("M0b refuses a missing mesh step", "no refusal", "Refusal")
        except Refusal as e:
            check("a missing step banner -> REFUSE_M0B_NO_MESH_STEP",
                  str(e).startswith("REFUSE_M0B_NO_MESH_STEP"), True)
        # steps OUT OF ORDER
        badorder = _mk_zb(os.path.join(tmp, "badorder"), D, base_pts=base,
                          gen_pts=base,
                          steps=("plot3dToFoam", "genWingMesh.py", "autoPatch",
                                 "createPatch", "renumberMesh"))
        try:
            m0b_provenance(badorder, D)
            check("M0b refuses steps out of order", "no refusal", "Refusal")
        except Refusal as e:
            check("steps out of order -> REFUSE_M0B_NO_MESH_STEP",
                  str(e).startswith("REFUSE_M0B_NO_MESH_STEP"), True)
        # a non-zero mesh rc
        badrc = _mk_zb(os.path.join(tmp, "badrc"), D, rc="1", base_pts=base,
                       gen_pts=base)
        try:
            m0b_provenance(badrc, D)
            check("M0b refuses a failed extrusion", "no refusal", "Refusal")
        except Refusal as e:
            check("mesh_rc != 0 -> REFUSE_M0B_MESH_RC",
                  str(e).startswith("REFUSE_M0B_MESH_RC"), True)
        # the wrong input surface
        badsurf = _mk_zb(os.path.join(tmp, "badsurf"), D, surface_ok=False,
                         base_pts=base, gen_pts=base)
        try:
            m0b_provenance(badsurf, D)
            check("M0b refuses the wrong surface", "no refusal", "Refusal")
        except Refusal as e:
            check("a surface that is not the registered base -> "
                  "REFUSE_M0B_NOT_BASE_SURFACE",
                  str(e).startswith("REFUSE_M0B_NOT_BASE_SURFACE"), True)
        # the build order
        badord = _mk_zb(os.path.join(tmp, "badord2"), D, order_ok=False,
                        base_pts=base, gen_pts=base)
        try:
            m0b_provenance(badord, D)
            check("M0b refuses a broken build order", "no refusal", "Refusal")
        except Refusal as e:
            check("points older than the surface it came from -> "
                  "REFUSE_M0B_BUILD_ORDER",
                  str(e).startswith("REFUSE_M0B_BUILD_ORDER"), True)
        # no datum at all
        try:
            m0b_provenance(zb, None)
            check("M0b refuses with no datum", "no refusal", "Refusal")
        except Refusal as e:
            check("no age datum -> REFUSE_M0B_NO_DATUM",
                  str(e).startswith("REFUSE_M0B_NO_DATUM"), True)
        # and the base-identification limb
        try:
            gate_m0b(zb, D, base)
            check("M0b refuses an unidentifiable base", "no refusal", "Refusal")
        except Refusal as e:
            check("a base mesh at the wrong md5 -> REFUSE_M0B_NOT_THE_BASE_MESH",
                  str(e).startswith("REFUSE_M0B_NOT_THE_BASE_MESH"), True)

        # ==== THE TWO GATES ARE TWO GATES ====================================
        check("M0b and M0o are distinct callables, not one relaxed gate",
              gate_m0b is not gate_m0o, True)
        toks_b = {"REFUSE_M0B_NO_DATUM", "REFUSE_M0B_NO_BUILD_ARTIFACT",
                  "REFUSE_M0B_STALE_ARTIFACT", "REFUSE_M0B_NO_MESH_STEP",
                  "REFUSE_M0B_BUILD_ORDER", "REFUSE_M0B_MESH_RC",
                  "REFUSE_M0B_NOT_BASE_SURFACE", "REFUSE_M0B_NOT_THE_BASE_MESH"}
        toks_o = {"REFUSE_M0O_NOT_THE_BASE_MESH", "REFUSE_M0O_MESH_IS_BASE"}
        body = open(__file__).read()
        check("every M0b refusal token is spelled in this file",
              sorted(t for t in toks_b if t not in body), [])
        check("every M0o refusal token is spelled in this file",
              sorted(t for t in toks_o if t not in body), [])
        check("the two token families do not overlap", toks_b & toks_o, set())
        # THE SWEEP IS OVER EXECUTABLE LINES ONLY, and it cuts the file at this
        # function's own definition.  The header of this file QUOTES the
        # inherited refusal when it explains why FM11 blocked, and a sweep that
        # cannot tell an explanation from a call site is reading an adjacent
        # quantity (L-595) -- the very error this checklist exists to catch.
        head = body.split("def self" + "test():", 1)[0]
        exe = "\n".join(l for l in head.splitlines()
                        if not l.lstrip().startswith("#"))
        needle_old = "REFUSE_FRESH" + "_IS_BASE"
        check("the executable body NEVER RAISES the inherited fused refusal -- "
              "the frozen guard is left where it is, not weakened",
              needle_old in exe, False)
        check("...and the same sweep FINDS the needle when it is genuinely "
              "present, so the green is not vacuous",
              needle_old in ('raise Refusal("' + needle_old + '")'), True)
        check("...while the file's own header DOES quote it, explaining the "
              "block -- an explanation is not a call site",
              needle_old in body, True)

        # ==== the dispatcher refuses a sub-arm it does not gate ==============
        try:
            stage_mesh(_mk_tree(os.path.join(tmp, "zq")), "Zq")
            check("an unregistered sub-arm refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("an unregistered sub-arm -> REFUSE_UNKNOWN_SUB_ARM",
                  str(e).startswith("REFUSE_UNKNOWN_SUB_ARM"), True)

        # ==== the read-back limb, in both directions =========================
        gen = [(float(i), 0.0, 0.0) for i in range(20)]
        rb_root = os.path.join(tmp, "rb")
        for mp in RUN_DIRS:
            _synth_mp(os.path.join(rb_root, mp), gen, n_proc=4, time_name="1000")
        r = readback_m0b(rb_root, gen)
        check("M0b.5 PASSES when the loaded mesh IS the generated mesh",
              r["pass"], True)
        wrong = list(gen)
        wrong[3] = (3.0 + 1e-9, 0.0, 0.0)
        rb2 = os.path.join(tmp, "rb2")
        for mp in RUN_DIRS:
            _synth_mp(os.path.join(rb2, mp), wrong, n_proc=4, time_name="1000")
        r = readback_m0b(rb2, gen)
        check("M0b.5 FAILS on a ONE-NANOMETRE difference in the loaded mesh",
              r["pass"], False)

        # ==== THE END-TO-END CASE, AGAINST THE REAL REGISTERED ANCHORS =======
        # The selftest cannot invent a cloud that hashes to the registered base
        # md5, so it uses THE REGISTERED BASE MESH ITSELF.  This reproduces
        # FM11's exact blocking situation -- a generated mesh byte-identical to
        # the base -- and requires M0b to PASS it and M0o to REFUSE it.
        if os.path.isfile(REAL_BASE_POINTS) and os.path.isfile(REAL_BASE_SURFACE):
            e2e = _mk_zb(os.path.join(tmp, "e2e"), D, base_pts=base, gen_pts=base)
            for mp in RUN_DIRS:
                d = os.path.join(e2e, mp, "constant", "polyMesh")
                os.remove(os.path.join(d, "points"))
                shutil.copyfile(REAL_BASE_POINTS, os.path.join(d, "points.gz"))
            pm = os.path.join(e2e, "constant", "polyMesh")
            os.remove(os.path.join(pm, "points"))
            shutil.copyfile(REAL_BASE_POINTS, os.path.join(pm, "points.gz"))
            t = D + 9.0
            os.utime(os.path.join(pm, "points.gz"), (t, t))
            real = read_points(REAL_BASE_POINTS)
            g = gate_m0b(e2e, D, real)
            check("END TO END: M0b PASSES a generated mesh BYTE-IDENTICAL to the "
                  "registered base mesh -- the exact case that blocked FM11",
                  g["pass"], True)
            check("...and R1 measures EXACTLY zero on all 40209 points",
                  (g["R1"]["max_point_difference_from_base_m"],
                   g["R1"]["n_points_identical"], g["R1"]["n_points"]),
                  (0.0, 40209, 40209))
            check("...and the md5s are identical, on files whose gzip MTIME "
                  "field both read zero",
                  (g["R1"]["md5_identical"], g["R1"]["gzip_mtime_field_is_zero"]),
                  (True, True))
            check("...and the base mesh it compared against is the REGISTERED one",
                  g["R1"]["base_points_md5"], BASE_POINTS_MD5)
            try:
                gate_m0o(e2e, real)
                check("END TO END: M0o refuses the same mesh", "no refusal", "Refusal")
            except Refusal as e:
                check("END TO END: M0o REFUSES that same mesh -- the two gates "
                      "answer OPPOSITELY on identical input, which is the whole "
                      "reason they are two gates",
                      str(e).startswith("REFUSE_M0O_MESH_IS_BASE"), True)
            moved_real = list(real)
            moved_real[0] = (real[0][0] + 1.0e-9, real[0][1], real[0][2])
            r = gate_m0o(e2e, moved_real)
            check("END TO END: M0o PASSES the registered base mesh with ONE "
                  "point moved one nanometre", r["pass"], True)
        else:
            check("the registered anchors are on disk for the end-to-end case",
                  "%s / %s" % (os.path.isfile(REAL_BASE_POINTS),
                               os.path.isfile(REAL_BASE_SURFACE)), "True / True")

        # ==== the imported constants ARE the frozen file's ===================
        check("EXTERNAL: BASE_POINTS_MD5 is imported, not re-typed",
              BASE_POINTS_MD5 is stg.BASE_POINTS_MD5, True)
        check("EXTERNAL: the base mesh hash", BASE_POINTS_MD5,
              "0fb1935a9b8781b73ac4ccb136e3ec68")
        check("EXTERNAL: the registered base surface md5", BASE_SURFACE_MD5,
              "3050ea454c2d0304bafa2c1a80c53b76")
        check("EXTERNAL: the three conditions", RUN_DIRS, ("mp04", "mp05", "mp06"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_FM12_STAGE SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="FM12 staging: the generated mesh into the condition cases, "
                    "behind M0b (provenance, Zb) or M0o (difference, Zo).")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--live-controls", action="store_true",
                    help="drive M0b and M0o to their FAILING SIDES against the "
                         "real artifacts FM11 left on disk.  Reads only.")
    ap.add_argument("--arm-dir", default=os.getcwd())
    ap.add_argument("--sub-arm", choices=("Zb", "Zo"))
    ap.add_argument("--datum-file")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.live_controls:
        try:
            r = live_controls()
        except Refusal as e:
            print("D6R2C_FM12_STAGE LIVE CONTROLS REFUSED\n%s" % e)
            return 2
        for c in r["controls"]:
            print("LIVE %-4s %s\n        %s"
                  % ("ok" if c["ok"] else "FAIL", c["control"], c["detail"]))
        print("D6R2C_FM12_STAGE LIVE CONTROLS %s n=%d"
              % ("PASS" if r["all_ok"] else "FAIL", len(r["controls"])))
        return 0 if r["all_ok"] else 1
    if not a.sub_arm:
        ap.error("--sub-arm is required")
    datum = None
    if a.datum_file and os.path.isfile(a.datum_file):
        datum = float(open(a.datum_file).read().strip())
    try:
        rec = stage_mesh(a.arm_dir, a.sub_arm, datum)
    except Refusal as e:
        print("D6R2C_FM12_STAGE REFUSED\n%s" % e)
        return 2
    with open(os.path.join(a.arm_dir, RECORD), "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    print("D6R2C_FM12_STAGE sub_arm=%s fresh=%s conditions=%d all_staged=%s"
          % (rec["sub_arm"], rec["fresh_points_md5"][:12],
             len(rec["conditions"]), rec["all_conditions_staged"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
