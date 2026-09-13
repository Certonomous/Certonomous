#!/usr/bin/env python3
# ===========================================================================
# d6r2c_fm12_states.py -- THE FM12 PRODUCER: every solve at ZERO shape and ZERO
#                         twist, on a mesh generated for that shape, TRIMMED.
# ===========================================================================
#
# Registered by PREREGISTRATION_FM12_MATCHED_LIFT_PROVENANCE.md sections 2, 3, 6
# and 7, and IN THE SAME COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS
# (rule 2).
#
# WHAT SEPARATES THIS FILE FROM `d6r2c_fm11_states.py`, WHICH IT FORKS AND WHOSE
# DESIGN WAS RIGHT.  `FM11` was graded `BLOCKED` at its first staging step: the
# INHERITED `d6r2c_fm9_stage.stage_mesh` raises `REFUSE_FRESH_IS_BASE` when the
# generated mesh equals the base mesh, and `Zb` is the state FOR WHICH THAT
# IDENTITY IS CORRECT.  THREE CHANGES, AND NOTHING ELSE:
#   (i)   staging goes through `d6r2c_fm12_stage.stage_mesh`, which dispatches
#         M0b (PROVENANCE, for Zb) or M0o (DIFFERENCE, for Zo) -- two gates with
#         two refusal families, NOT one relaxed gate covering both.  M0o's
#         condition is FM11's `worst > 0.0`, strictly, unweakened.
#   (ii)  the arm's AGE DATUM is threaded in, because M0b's load-bearing limb is
#         CLAUDE.md rule 4's age guard applied to the mesh: an inherited mesh is
#         47.7 days too old to pass.  `--datum-file` is REQUIRED, and a missing
#         datum REFUSES rather than defaulting to a permissive clock.
#   (iii) `M0b.5` -- the polyMesh the SOLVER ACTUALLY READ, rebuilt from its own
#         `pointProcAddressing` -- is recorded per state, so M0b's claim about
#         what the solver held is evidenced rather than assumed.
# `measure_against_base` is GONE from this file: its job is done by the two
# gates, and a second spelling of a mesh-identity decision is a second thing
# that can drift (L-221/L-222).
#
# WHY IT EXISTS, IN ONE SENTENCE.  d6r2c_freshmesh.py:phase_solve re-applies
# `shape` and `twist` on a volume mesh THAT WAS ALREADY BUILT FROM THE DEFORMED
# SURFACE -- `--phase deform` writes surfaceMesh_final.cgns at shape = s*,
# `--phase mesh` extrudes on it, and then `--phase solve` sets shape = s* again.
# MEASURED (DAFOAM_CHARTER.md sec 22.3, committed a2a1c9319): the fresh mesh's
# wall reproduces the deformed wall to 1.09e-09; the second warp is COLLINEAR
# with the first (cos angle median 0.99965, magnitude ratio 1.234); mid-span
# camber/chord runs base 0.00196 -> optimum 0.04810 -> FM10 0.09015, an
# increment of 1.91x; and the three conditions flew at CL +0.1493/+0.1516/+0.1524
# above target, THIRTY TIMES the registered CL_FINDING_TRIGGER of 5.0e-3.
# The cause class is PRODUCER, and every mesh class was EXCLUDED by measurement.
#
# THE ONE CHANGE THIS FILE MAKES.  In the solve phase it sets ONLY the patchV
# (incidence) design variables.  `shape` and `twist` are set to ZERO, because
# THE MESH ALREADY CARRIES THE DEFORMATION.  A mesh extruded around a given
# surface already IS that geometry; the correct design vector on it is zero.
#
# AND THE GUARD THAT BELONGS WITH IT (G-WALL).  A claim that the DV set moves
# nothing is checkable, so it is CHECKED: after every state this file rebuilds
# the global point cloud the solver actually held -- from its own
# processor*/<latest time>/polyMesh/points through constant/polyMesh/
# pointProcAddressing -- restricts it to the `wing` patch, and measures the
# maximum displacement from the generated fresh mesh's own wall.  On Zb and Zo
# that displacement is GATED at WALL_MOVE_TOL.  On Do -- the diagnostic that
# reproduces FM10 -- it is REPORTED, and a LARGE value there is the contrast
# that proves the guard is not simply blind.
#
# THE CHANNEL THAT WAS DELETED, AND WHY (DAFOAM_CHARTER.md sec 22.4 clause 3).
# `primal_residual.json` had FOUR READERS, ZERO WRITERS and zero such files
# anywhere on disk, and `conv[p] = True` stood for every condition of every arm.
# THIS FILE WRITES NO SUCH FIELD AND READS NO SUCH FILE.  Convergence evidence
# for FM12 comes from the arm log, whose writer is the solver itself and whose
# lines are countable -- see d6r2c_fm12_grade.py, clause H4.  A status channel
# with no writer defaults to success, silently; the repair is to delete it, not
# to read it more carefully.
#
# HONEST GAP, NAMED BEFORE IT IS DISCOVERED.  THIS FILE HAS NEVER BEEN EXECUTED
# AGAINST THE SOLVER.  It cannot be before the compute this registration
# authorises.  `--selftest` drives the pure logic -- DV assembly, the driver-
# scaled conversion, the wall reconstruction, the as-run mesh export and every
# refusal path -- on synthetic inputs, touching no container.  `--parse-only`
# drives THE EXACT ARGUMENT VECTOR THE LAUNCHER EMITS through argparse and the
# input validation and exits before mpi4py is imported, which is the part of the
# frozen command line that CAN be exercised outside the container (L-595).
# ===========================================================================
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# THE REGISTERED CONSTANTS.  Every one of them is either copied from a frozen
# document (and says which) or DERIVED HERE, IN THIS INVOCATION, and the derived
# value is the value used -- never a literal typed beside a derivation.
# ---------------------------------------------------------------------------
RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"   # PREREGISTRATION.md ADDENDUM 1
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"       # AFTER_ITEMS section 0b
FINAL_RECORD_N = 88                                  # AFTER_ITEMS section 1
WALL_PATCH = "wing"
RUN_DIRS = ("mp04", "mp05", "mp06")
RECORD = "d6r2c_fm12.jsonl"

# THE SUB-ARMS AND THEIR STATES -- PREREGISTRATION_FM12_MATCHED_LIFT.md sec 2.
# Zo and Do SHARE ONE MESH and therefore one process; Zb has its own mesh.
SUB_ARMS = {"Zb": ["Zb"], "Zo": ["Zo", "Ez", "Do"]}
# shape = 0 and twist = 0.  THE MESH ALREADY CARRIES THE GEOMETRY.
ZERO_STATES = ("Zb", "Zo", "Ez")
# re-trimmed to the registered CL targets.  Ez is NOT trimmed: it is D1's
# measurement of what the incidence a*_opt gives at ZERO shape, which is the
# whole content of the double-deformation diagnostic.
TRIM_STATES = ("Zb", "Zo")
# G-WALL gates wherever the DV set is supposed to move nothing.  On Do it is
# REPORTED, and a LARGE displacement there is the contrast that shows the guard
# is not simply blind.
WALL_GATE_STATES = ("Zb", "Zo", "Ez")
# THE BASE MESH ANCHOR IS BOUND BELOW, AFTER THE IMPORTS -- it is IMPORTED from
# the stager that owns the M0 decisions and never re-typed here (L-221/L-222).
# FM11 carried its own copy of this literal alongside the inherited stager's,
# which is two spellings of one anchor.

# --- WALL_MOVE_TOL, DERIVED IN THIS INVOCATION AND THE DERIVED VALUE USED ----
# The wing's coordinates are O(1) m.  A warp of a wall point is a weighted sum
# over the CGNS surface's 1031 nodes, so the worst round-off a ZERO delta can
# leave is about n_nodes * eps * |x|.  WALL_MOVE_ROUNDOFF is that bound and
# WALL_MOVE_TOL is four times it -- a round-off allowance, NOT a physical band,
# and it is not a tolerance on anything the arm is measuring.
_EPS = sys.float_info.epsilon                     # 2.220446049250313e-16
CGNS_UNIQUE_NODES = 1031                          # AFTER_ITEMS sec 2c, measured
_WING_COORD_SCALE_M = 1.0
WALL_MOVE_ROUNDOFF = CGNS_UNIQUE_NODES * _EPS * _WING_COORD_SCALE_M
WALL_MOVE_TOL = 4.0 * WALL_MOVE_ROUNDOFF          # DERIVED, and this is the value used

# The planted perturbation of rule 3.  It is the lab's standing value and it is
# driven into the READ-BACK cloud, never into a registered copy.
PLANT = 1.234e-03

# DAFoam's OWN declared mesh-quality limit, read out of the frozen runScript's
# checkMeshThreshold block at d6r2c_opt_runScript.py:163.  NOT chosen here.
MAX_NONORTH_DECLARED = 70.0


class Refusal(Exception):
    """Refuse, never degrade."""


# ---------------------------------------------------------------------------
# THE LIBRARIES.  Imported, never re-spelled (L-221/L-222).  d6r2c_dec5_decomp
# owns the trim, the governor and the frozen-model loader; d6r2c_fm9_stage owns
# the OpenFOAM readers and the processor-addressing reconstruction;
# d6r2c_freshmesh owns the wall-patch point ids.
# ---------------------------------------------------------------------------
try:                                   # pragma: no cover - import shape only
    import d6r2c_dec5_decomp as dec
    import d6r2c_fm9_stage as stg
    import d6r2c_fm12_stage as stg12
    import d6r2c_freshmesh as fm
except ImportError as exc:             # pragma: no cover
    raise Refusal("REFUSE_MISSING_LIBRARY %s -- G-DEPS should have caught this "
                  "before the container started" % exc)

# THE BASE MESH, IMPORTED FROM THE FILE THAT OWNS THE M0 DECISIONS.
BASE_POINTS_MD5 = stg12.BASE_POINTS_MD5


# ---------------------------------------------------------------------------
# THE DESIGN VECTOR FOR EACH FM12 STATE.  Nothing else in this file decides
# what a state is, and the ONE CHANGE lives here and nowhere else.
# ---------------------------------------------------------------------------

def dv_for_fm12(state, dv_star, dv_x0):
    """PREREGISTRATION_FM12_MATCHED_LIFT.md section 2, the table.

    Zb / Zo -- shape = 0, twist = 0, incidence RE-TRIMMED to the registered CL.
               The mesh already carries whatever geometry it was built from.
    Ez      -- shape = 0, twist = 0, incidence a*_opt, NOT trimmed.  D1's own
               measurement: the CL excess the optimiser's incidence gives when
               NOTHING is re-applied to a mesh that already carries the shape.
    Do      -- shape = s*, twist = t*, incidence a*, NOT trimmed.  The diagnostic
               that reproduces FM10 ON THE SAME MESH, so that the excess can be
               attributed to the DVs or to the mesh by measurement."""
    if state not in ("Zb", "Zo", "Ez", "Do"):
        raise Refusal("REFUSE_UNKNOWN_STATE %r" % state)
    if "shape" not in dv_star or "twist" not in dv_star:
        raise Refusal("REFUSE_DV_STAR_INCOMPLETE shape/twist absent from the "
                      "inherited design vector")
    if state in ZERO_STATES:
        out = {"shape": [0.0] * len(dv_star["shape"]),
               "twist": [0.0] * len(dv_star["twist"])}
    else:
        out = {"shape": list(dv_star["shape"]), "twist": list(dv_star["twist"])}
    trim = state in TRIM_STATES
    # A TRIMMED state starts from x0's incidence and is re-trimmed to the
    # registered CL.  An UNTRIMMED state flies the optimiser's own a*, which is
    # what makes Ez and Do comparable to FM10 and to each other.
    src = dv_x0 if trim else dv_star
    n_patch = 0
    for k, v in src.items():
        if k.startswith("patchV_"):
            out[k] = list(v)
            n_patch += 1
    if n_patch == 0:
        raise Refusal("REFUSE_NO_PATCHV state %s found no patchV_* entry to set; "
                      "an untrimmed arm with no incidence is not a state" % state)
    out["_trim"] = trim
    return out


# ---------------------------------------------------------------------------
# G-WALL -- THE GUARD THAT BELONGS WITH THE ONE CHANGE
# ---------------------------------------------------------------------------

def latest_time_dir(proc_dir):
    """The numerically largest time directory under proc_dir that carries a
    polyMesh, or None.  A processor that wrote no moved mesh is NOT silently
    read from `constant`: the caller is told which it got."""
    best = None
    for d in sorted(os.listdir(proc_dir)):
        p = os.path.join(proc_dir, d)
        if not os.path.isdir(p) or not os.path.isdir(os.path.join(p, "polyMesh")):
            continue
        try:
            t = float(d)
        except ValueError:
            continue
        if best is None or t > best[0]:
            best = (t, d)
    return None if best is None else best[1]


def reconstruct_asrun_points(mp_dir, n_points):
    """The undecomposed point cloud THE SOLVER HELD AFTER THE FINAL DV
    APPLICATION, rebuilt from its own processor directories.

    The addressing is read from constant/polyMesh/pointProcAddressing -- which
    the decomposition writes and the warp never touches -- and the coordinates
    from the LATEST time directory, which is where IDWarp leaves the moved mesh.
    REFUSES on a hole, a duplicate or an out-of-range address: a partially
    rebuilt cloud cannot answer 'which mesh did the solver hold'."""
    procs = stg.processor_dirs(mp_dir)
    if not procs:
        raise Refusal("REFUSE_NO_PROCESSOR_DIRS in %s -- the solver left no "
                      "decomposition to read" % mp_dir)
    out = [None] * n_points
    used = {}
    for pd in procs:
        base = os.path.join(mp_dir, pd)
        cpm = os.path.join(base, "constant", "polyMesh")
        addr = stg.read_labels(stg._open_either(os.path.join(cpm, "pointProcAddressing")))
        t = latest_time_dir(base)
        if t is None:
            ppath = os.path.join(cpm, "points")
            used[pd] = "constant"
        else:
            ppath = os.path.join(base, t, "polyMesh", "points")
            used[pd] = t
        pts = stg.read_points(stg._open_either(ppath))
        if len(addr) != len(pts):
            raise Refusal("REFUSE_ADDR_COUNT %s: %d addresses, %d points"
                          % (pd, len(addr), len(pts)))
        for k, g in enumerate(addr):
            if not (0 <= g < n_points):
                raise Refusal("REFUSE_ADDR_RANGE %s: global point %d outside "
                              "[0, %d)" % (pd, g, n_points))
            if out[g] is not None and out[g] != pts[k]:
                raise Refusal("REFUSE_ADDR_CONFLICT %s: global point %d written "
                              "twice with different coordinates" % (pd, g))
            out[g] = pts[k]
    holes = [i for i, v in enumerate(out) if v is None]
    if holes:
        raise Refusal("REFUSE_ADDR_HOLE %d of %d points unwritten (first %r)"
                      % (len(holes), n_points, holes[:5]))
    return out, used


def wall_displacement(loaded, generated, wall_ids):
    """Max Euclidean displacement on the wall patch, and where it is.

    A PURE FUNCTION OVER TWO POINT CLOUDS AND AN ID LIST, deliberately: that is
    what lets a check OUTSIDE this file drive it to its failing side with a
    planted cloud.  A guard that can only be pointed at a live run can only ever
    be tested against whatever the run happens to do."""
    if len(loaded) != len(generated):
        raise Refusal("REFUSE_POINT_COUNT loaded %d, generated %d"
                      % (len(loaded), len(generated)))
    if not wall_ids:
        raise Refusal("REFUSE_NO_WALL_IDS -- a guard over an empty point set "
                      "returns 0.0 and means nothing (rule 3)")
    worst, where = 0.0, None
    for g in wall_ids:
        if not (0 <= g < len(loaded)):
            raise Refusal("REFUSE_WALL_ID_RANGE %d outside [0, %d)" % (g, len(loaded)))
        a, b = loaded[g], generated[g]
        d = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5
        if d > worst:
            worst, where = d, g
    return {"max_displacement_m": worst, "at_global_point": where,
            "n_wall_points": len(wall_ids), "tol_m": WALL_MOVE_TOL,
            "tol_basis": "DERIVED in the producer's own invocation: "
                         "4 x n_cgns_nodes(%d) x eps(%.6e) x 1 m = %.6e"
                         % (CGNS_UNIQUE_NODES, _EPS, WALL_MOVE_TOL),
            "pass": worst <= WALL_MOVE_TOL}


# ---------------------------------------------------------------------------
# THE AS-RUN MESH, EXPORTED AND CHECKED (charter rule 31)
# ---------------------------------------------------------------------------

def export_asrun_case(arm_dir, state, points):
    """Write a serial OpenFOAM case whose constant/polyMesh IS the mesh that ran.

    The topology is the generated mesh's -- a warp moves points and touches no
    face, owner, neighbour or boundary -- and the POINTS are the reconstructed
    as-run cloud.  This is what checkMesh is then pointed at, so the quality
    numbers describe THE MESH THAT RAN and not the mesh as built."""
    src_pm = os.path.join(arm_dir, "constant", "polyMesh")
    dst = os.path.join(arm_dir, "asrun_%s" % state)
    dst_pm = os.path.join(dst, "constant", "polyMesh")
    if os.path.exists(dst):
        raise Refusal("REFUSE_ASRUN_EXISTS %s -- a guard refuses a case that "
                      "already exists (CLAUDE.md rule 4)" % dst)
    os.makedirs(dst_pm)
    for name in ("faces", "owner", "neighbour", "boundary"):
        for cand in (name, name + ".gz"):
            p = os.path.join(src_pm, cand)
            if os.path.isfile(p):
                shutil.copyfile(p, os.path.join(dst_pm, cand))
                break
        else:
            raise Refusal("REFUSE_MISSING_TOPOLOGY %s (and %s.gz) under %s"
                          % (name, name, src_pm))
    sys_src = os.path.join(arm_dir, "system")
    if not os.path.isdir(sys_src):
        raise Refusal("REFUSE_NO_SYSTEM %s" % sys_src)
    shutil.copytree(sys_src, os.path.join(dst, "system"))
    with open(os.path.join(dst_pm, "points"), "w") as fh:
        fh.write("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                 "    class       vectorField;\n    location    "
                 '"constant/polyMesh";\n    object      points;\n}\n'
                 "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")
        fh.write("%d\n(\n" % len(points))
        for p in points:
            fh.write("(%.17g %.17g %.17g)\n" % (p[0], p[1], p[2]))
        fh.write(")\n")
    return dst


def run_checkmesh(case_dir, log_path):
    """checkMesh on the as-run case.  A quality clause is REPORTED, so a failure
    to run it is RECORDED as a failure to run it -- never absorbed into a pass."""
    try:
        with open(log_path, "w") as lf:
            r = subprocess.run(["checkMesh", "-constant", "-case", case_dir],
                               stdout=lf, stderr=subprocess.STDOUT)
        rc = r.returncode
    except OSError as exc:
        with open(log_path, "w") as lf:
            lf.write("CHECKMESH_NOT_RUN %s\n" % exc)
        rc = None
    return {"rc": rc, "log": os.path.basename(log_path),
            "ran": rc is not None,
            "max_nonorth": parse_max_nonorth(log_path),
            "declared_max_nonorth": MAX_NONORTH_DECLARED}


def parse_max_nonorth(log_path):
    """The number checkMesh prints, or None.  NEVER a default."""
    if not os.path.isfile(log_path):
        return None
    out = None
    with open(log_path, errors="replace") as fh:
        for line in fh:
            if "non-orthogonality" in line and "ax" in line:
                for tok in line.replace(",", " ").split():
                    try:
                        v = float(tok)
                    except ValueError:
                        continue
                    out = v
                    break
    return out


# ---------------------------------------------------------------------------
# M0 -- THE EXTRUSION-EVIDENCE GATE.  TWO GATES, NOT ONE.
# ---------------------------------------------------------------------------
#
# FM11 asked ONE question of both sub-arms -- "does the generated mesh differ
# from the base mesh?" -- and the inherited stager then REFUSED the only answer
# `Zb` can give.  The question M0 actually needs answered is "did THIS ARM'S
# EXTRUSION RUN, or was a mesh silently inherited?", and the two sub-arms need
# DIFFERENT EVIDENCE for the same claim:
#
#   Zo -- evidenced by DIFFERENCE FROM BASE.  The mesh is extruded around the
#         FFD-updated surface and MUST differ.  Zero difference means the
#         deformation never reached the mesher and the comparison is vacuous.
#         UNCHANGED FROM FM11, condition for condition: `worst > 0.0`, strictly.
#   Zb -- evidenced by PROVENANCE.  Difference-from-base is not available to it
#         and a tolerance invented for it would be the relaxation this whole
#         repair exists to avoid.  Instead: every build artifact exists and is
#         newer than the arm's own age datum, every mesh step left its banner in
#         order, the build order holds in time, the mesher returned 0, and the
#         input surface IS the registered base surface.
#
# Both live in `d6r2c_fm12_stage.py`, with two distinct refusal families and a
# failing control for each -- including LIVE ones, driven against the real
# artifacts FM11 left on disk.  THIS FILE DISPATCHES; IT DOES NOT DECIDE, so
# there is exactly one spelling of each decision (L-221/L-222).


# ---------------------------------------------------------------------------
# THE RUN
# ---------------------------------------------------------------------------

def run(arm_dir, sub_arm, runscript, evals, x0_file, out_path, datum_epoch):
    from mpi4py import MPI
    rank0 = MPI.COMM_WORLD.rank == 0
    t_start = time.time()
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT this arm runs as ubuntu, never root "
                      "(Sanaa Launch item 6)")
    states = SUB_ARMS[sub_arm]

    dv_star, funcs_star, evals_md5 = dec.read_final_dv(evals)
    with open(x0_file) as fh:
        x0 = json.load(fh)
    dv_x0 = x0["dv_driver_scaled"]

    # the generated fresh mesh and its wall -- READ BEFORE THE MODEL IS BUILT,
    # so that what G-WALL compares against cannot have been touched by the solve
    pm = os.path.join(arm_dir, "constant", "polyMesh")
    generated = stg.read_points(stg._open_either(os.path.join(pm, "points")))
    wall_ids, wall_nfaces = fm.wall_point_ids(pm, patch=WALL_PATCH)
    gen_md5 = stg._md5(stg._open_either(os.path.join(pm, "points")))

    # ---- M0, then STAGING, and BOTH BEFORE THE MODEL IS BUILT --------------
    # The order is the whole point.  stage_mesh puts the generated mesh into
    # every condition case and REMOVES the stale decomposition, so that the
    # prob.setup() below decomposes THE MESH THIS ARM GENERATED.  Staging after
    # the model is built stages nothing the solver will ever read -- which is
    # the FM5/FM7/FM8 defect (d6r2c_fm9_stage.py's own header records it).
    staged = stg12.stage_mesh(arm_dir, sub_arm, datum_epoch)
    m0 = staged["M0"]
    if not staged.get("all_conditions_staged"):
        raise Refusal("REFUSE_STAGE_INCOMPLETE %r" % staged.get("conditions"))
    for mp in RUN_DIRS:
        left = stg.processor_dirs(os.path.join(arm_dir, mp))
        if left:
            raise Refusal("REFUSE_PROCESSOR_DIRS_BEFORE_SETUP %s still carries "
                          "%r -- prob.setup() would read them instead of "
                          "decomposing the generated mesh" % (mp, left))

    ns = dec.load_frozen_model(runscript)
    prob, optFuncs = ns["prob"], ns["optFuncs"]
    POINTS, TARGETS, WEIGHTS = ns["POINTS"], ns["CL_TARGETS"], ns["WEIGHTS"]

    if rank0:
        dec.append_record(out_path, {
            "kind": "HEADER", "sub_arm": sub_arm, "states": states,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "uid": os.getuid(), "gid": os.getgid(),
            "ranks": MPI.COMM_WORLD.size, "points": POINTS,
            "cl_targets": TARGETS, "weights": WEIGHTS,
            "evals_md5": evals_md5, "x0_md5": stg._md5(x0_file),
            "runscript_md5": RUNSCRIPT_MD5,
            "dv_source_record_n": FINAL_RECORD_N,
            "generated_points_md5": gen_md5,
            "n_generated_points": len(generated),
            "n_wall_points": len(wall_ids), "n_wall_faces": wall_nfaces,
            "M0": m0, "staging": staged, "datum_epoch": datum_epoch,
            "M0_gate": "M0b -- PROVENANCE" if sub_arm == "Zb" else
                       "M0o -- DIFFERENCE FROM BASE",
            "WALL_MOVE_TOL": WALL_MOVE_TOL,
            "WALL_MOVE_ROUNDOFF": WALL_MOVE_ROUNDOFF,
            "WALL_GATE_STATES": list(WALL_GATE_STATES),
            "MAX_NONORTH_DECLARED": MAX_NONORTH_DECLARED,
            "the_one_change": "the solve phase sets ONLY patchV_*; shape and "
                              "twist are ZERO on Zb and Zo because the mesh "
                              "already carries the geometry it was built from",
            "primal_residual_json": "DELETED.  It had four readers, zero writers "
                                    "and zero such files on disk; this file "
                                    "neither writes nor reads it, and no clause "
                                    "of FM12 defaults to converged (charter 22.4.3)",
            "DEADLINE_IN_CONTAINER_S": "NONE"})

    meta = prob.model.get_design_vars(recurse=True, get_sizes=True, use_prom_ivc=True)
    scalers = {k.split(".")[-1]: dec.dv_divisor(v) for k, v in meta.items()}

    def set_driver_scaled(name, vals):
        s = dec.dv_divisor_for(scalers, name)
        prob.set_val(name, [v / s for v in vals])

    gov = dec.IncidenceGovernor(prob, POINTS, scalers, dec.dv_divisor_for)

    rcs = 0
    for state in states:
        t0 = time.time()
        spec = dv_for_fm12(state, dv_star, dv_x0)
        do_trim = spec.pop("_trim")
        for name, vals in spec.items():
            set_driver_scaled(name, vals)
        n0, c0 = gov.n_evals, gov.n_continuation
        for p in POINTS:
            gov.visited[p] = []
        if do_trim:
            optFuncs.findFeasibleDesign(
                ["%s.aero_post.CL" % p for p in POINTS],
                ["patchV_" + p for p in POINTS],
                targets=[TARGETS[p] for p in POINTS],
                designVarsComp=[1] * len(POINTS))
        prob.run_model()
        n_cont = gov.n_continuation - c0
        n_trim = (gov.n_evals - n0) - n_cont
        cd = {p: float(prob.get_val("%s.aero_post.CD" % p)[0]) for p in POINTS}
        cl = {p: float(prob.get_val("%s.aero_post.CL" % p)[0]) for p in POINTS}
        aoa = {p: float(prob.get_val("patchV_" + p)[1]) for p in POINTS}
        MPI.COMM_WORLD.Barrier()

        wall, asrun, loaded_gate = {}, {}, {}
        if rank0:
            for mp in RUN_DIRS:
                mp_dir = os.path.join(arm_dir, mp)
                if not os.path.isdir(mp_dir):
                    raise Refusal("REFUSE_NO_CONDITION_DIR %s" % mp_dir)
                pts, used = reconstruct_asrun_points(mp_dir, len(generated))
                w = wall_displacement(pts, generated, wall_ids)
                w["time_dirs_read"] = used
                wall[mp] = w
                # the mesh the solver LOADED -- constant/polyMesh through the
                # same addressing.  Exact equality against the generated mesh.
                loaded = stg.reconstruct_loaded_points(mp_dir, len(generated))
                loaded_gate[mp] = {
                    "max_point_difference_from_generated":
                        stg.max_point_difference(loaded, generated),
                    "n_processors": len(stg.processor_dirs(mp_dir))}
            # ONE as-run case per state, exported from the MIDDLE condition, which
            # is the one the geometry constraints are attached to (mp05 carries
            # geometry_cl05 in the frozen runScript).
            mid = RUN_DIRS[1]
            pts, _u = reconstruct_asrun_points(os.path.join(arm_dir, mid), len(generated))
            case = export_asrun_case(arm_dir, state, pts)
            asrun = run_checkmesh(case, os.path.join(arm_dir,
                                                     "checkMesh_asrun_%s.log" % state))
            asrun["condition"] = mid
            asrun["breaches_declared_limit"] = (
                asrun["max_nonorth"] is not None
                and asrun["max_nonorth"] > MAX_NONORTH_DECLARED)

            gate = all(wall[mp]["pass"] for mp in RUN_DIRS)
            dec.append_record(out_path, {
                "kind": "STATE", "state": state, "sub_arm": sub_arm,
                "trimmed": do_trim, "n_trim_evals": n_trim,
                "n_continuation_steps": n_cont,
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "wall_s": time.time() - t0,
                "CD": cd, "CL": cl, "AoA_deg": aoa,
                "J": sum(WEIGHTS[p] * cd[p] for p in POINTS),
                "claimed_cl_miss": {p: abs(cl[p] - TARGETS[p]) for p in POINTS},
                "aoa_visited_deg": {p: list(gov.visited[p]) for p in POINTS},
                "shape_twist_set_to_zero": state in ZERO_STATES,
                "in_TRIM_STATES": state in TRIM_STATES,
                "G_WALL": wall,
                "G_WALL_gated": state in WALL_GATE_STATES,
                "G_WALL_pass": gate if state in WALL_GATE_STATES else None,
                "G_WALL_role_on_this_state":
                    ("GATED -- the DV set must move no wall point"
                     if state in WALL_GATE_STATES else
                     "REPORTED -- Do applies shape* and twist*, so a LARGE "
                     "displacement here is the contrast that shows the guard "
                     "is not blind"),
                "mesh_loaded": loaded_gate,
                # M0b.5 -- the polyMesh the SOLVER ACTUALLY READ, rebuilt from
                # its own pointProcAddressing.  HONEST STATEMENT: this is the
                # SAME measurement the grader performs as M1; it is recorded
                # under M0b's name so that M0b's claim about what the solver
                # held is evidenced rather than assumed.  It is NOT a second
                # independent reading and is not presented as one.
                "M0b_readback": stg12.readback_m0b(arm_dir, generated)
                                if sub_arm == "Zb" else None,
                "checkMesh_asrun": asrun})
        MPI.COMM_WORLD.Barrier()

    if rank0:
        dec.append_record(out_path, {
            "kind": "FOOTER", "sub_arm": sub_arm, "rc": rcs,
            "wall_s": time.time() - t_start,
            "n_primal_evals_total": gov.n_evals,
            "n_continuation_steps_total": gov.n_continuation,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    return rcs


# ---------------------------------------------------------------------------
# SELFTEST -- pure logic only.  Touches no container and no run directory.
# ---------------------------------------------------------------------------

def _synth_mp(root, pts, n_proc=4, time_name="1000"):
    """A synthetic decomposed condition case whose processor dirs carry `pts`."""
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


def selftest():
    import tempfile
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    # ---- the DERIVED tolerance is the value used, not a literal beside it ----
    check("WALL_MOVE_TOL is 4x the derived round-off bound",
          WALL_MOVE_TOL == 4.0 * CGNS_UNIQUE_NODES * _EPS * 1.0, True)
    check("WALL_MOVE_TOL is far below the PLANT it must catch",
          WALL_MOVE_TOL < PLANT / 1e6, True)

    # ---- the state table, in both directions --------------------------------
    dv_star = {"shape": [0.3, -0.2], "twist": [1.0, 2.0],
               "patchV_cl04": [100.0, 3.0], "patchV_cl05": [100.0, 4.0],
               "patchV_cl06": [100.0, 5.0]}
    dv_x0 = {"patchV_cl04": [100.0, 1.0], "patchV_cl05": [100.0, 2.0],
             "patchV_cl06": [100.0, 3.0]}
    for s in ("Zb", "Zo"):
        d = dv_for_fm12(s, dv_star, dv_x0)
        check("%s sets shape to ZERO" % s, d["shape"], [0.0, 0.0])
        check("%s sets twist to ZERO" % s, d["twist"], [0.0, 0.0])
        check("%s is TRIMMED" % s, d["_trim"], True)
        check("%s takes incidence from x0, not from the optimum" % s,
              d["patchV_cl06"], [100.0, 3.0])
    d = dv_for_fm12("Ez", dv_star, dv_x0)
    check("Ez sets shape to ZERO", d["shape"], [0.0, 0.0])
    check("Ez sets twist to ZERO", d["twist"], [0.0, 0.0])
    check("Ez is NOT trimmed -- it flies a*_opt, which is what D1 measures",
          d["_trim"], False)
    check("Ez takes incidence from the OPTIMUM, not from x0",
          d["patchV_cl06"], [100.0, 5.0])
    check("Ez and Do differ ONLY in the shape DVs",
          (dv_for_fm12("Ez", dv_star, dv_x0)["patchV_cl04"]
           == dv_for_fm12("Do", dv_star, dv_x0)["patchV_cl04"]), True)
    check("G-WALL gates Ez -- it sets the DVs to zero and must move nothing",
          "Ez" in WALL_GATE_STATES, True)
    check("G-WALL does NOT gate Do", "Do" in WALL_GATE_STATES, False)
    d = dv_for_fm12("Do", dv_star, dv_x0)
    check("Do carries shape*", d["shape"], [0.3, -0.2])
    check("Do carries twist*", d["twist"], [1.0, 2.0])
    check("Do is NOT trimmed", d["_trim"], False)
    check("Do takes incidence from the optimum", d["patchV_cl06"], [100.0, 5.0])
    try:
        dv_for_fm12("O", dv_star, dv_x0)
        check("an unregistered state refuses", "no refusal", "Refusal")
    except Refusal as e:
        check("unknown state -> REFUSE_UNKNOWN_STATE",
              str(e).startswith("REFUSE_UNKNOWN_STATE"), True)
    try:
        dv_for_fm12("Zb", dv_star, {})
        check("no patchV refuses", "no refusal", "Refusal")
    except Refusal as e:
        check("no patchV -> REFUSE_NO_PATCHV", str(e).startswith("REFUSE_NO_PATCHV"), True)
    check("Zo, Ez and Do share one sub-arm and therefore ONE mesh",
          SUB_ARMS["Zo"], ["Zo", "Ez", "Do"])
    check("Zb is alone on its own mesh", SUB_ARMS["Zb"], ["Zb"])
    check("every state of every sub-arm is a state the table knows",
          sorted({x for v in SUB_ARMS.values() for x in v}),
          ["Do", "Ez", "Zb", "Zo"])

    # ---- G-WALL, DRIVEN TO ITS FAILING SIDE ---------------------------------
    gen = [(float(i), 0.0, 0.0) for i in range(20)]
    ids = [3, 7, 11]
    check("G-WALL on identical clouds is exactly 0.0",
          wall_displacement(list(gen), gen, ids)["max_displacement_m"], 0.0)
    check("G-WALL on identical clouds PASSES",
          wall_displacement(list(gen), gen, ids)["pass"], True)
    moved = list(gen)
    moved[7] = (moved[7][0] + PLANT, moved[7][1], moved[7][2])
    r = wall_displacement(moved, gen, ids)
    check("G-WALL SEES the planted 1.234e-3 on a wall point", r["pass"], False)
    check("G-WALL names WHERE it saw it", r["at_global_point"], 7)
    # ... and the negative that proves it is a WALL guard and not a mesh guard
    off = list(gen)
    off[5] = (off[5][0] + PLANT, off[5][1], off[5][2])
    check("G-WALL ignores a point that is NOT on the wall",
          wall_displacement(off, gen, ids)["pass"], True)
    # a displacement at exactly the tolerance passes; one just above does not
    edge = list(gen)
    edge[3] = (edge[3][0] + WALL_MOVE_TOL, edge[3][1], edge[3][2])
    check("G-WALL passes AT the derived tolerance",
          wall_displacement(edge, gen, ids)["pass"], True)
    edge[3] = (gen[3][0] + WALL_MOVE_TOL * 1.001, gen[3][1], gen[3][2])
    check("G-WALL fails just ABOVE the derived tolerance",
          wall_displacement(edge, gen, ids)["pass"], False)
    try:
        wall_displacement(gen, gen, [])
        check("an empty wall set refuses", "no refusal", "Refusal")
    except Refusal as e:
        check("empty wall set -> REFUSE_NO_WALL_IDS",
              str(e).startswith("REFUSE_NO_WALL_IDS"), True)
    try:
        wall_displacement(gen[:5], gen, ids)
        check("a count mismatch refuses", "no refusal", "Refusal")
    except Refusal as e:
        check("count mismatch -> REFUSE_POINT_COUNT",
              str(e).startswith("REFUSE_POINT_COUNT"), True)

    tmp = tempfile.mkdtemp(prefix="d6r2c_fm12_selftest_")
    try:
        # ---- the as-run reconstruction reads the TIME dir, not `constant` ----
        mp = os.path.join(tmp, "mp05")
        warped = [(x + 0.5, y, z) for (x, y, z) in gen]
        _synth_mp(mp, gen, n_proc=4, time_name="1000")
        # overwrite the TIME points with the warped cloud, leaving constant alone
        _synth_mp(os.path.join(tmp, "mpW"), warped, n_proc=4, time_name="1000")
        for i in range(4):
            shutil.copyfile(os.path.join(tmp, "mpW", "processor%d" % i, "1000",
                                         "polyMesh", "points"),
                            os.path.join(mp, "processor%d" % i, "1000",
                                         "polyMesh", "points"))
        pts, used = reconstruct_asrun_points(mp, len(gen))
        check("as-run reconstruction returns the WARPED cloud", pts[7], warped[7])
        check("as-run reconstruction names the time dir it read",
              sorted(set(used.values())), ["1000"])
        loaded = stg.reconstruct_loaded_points(mp, len(gen))
        check("the LOADED reconstruction still returns `constant`", loaded[7], gen[7])
        check("the two readers DISAGREE on a warped case -- they are not one check",
              loaded[7] == pts[7], False)
        # a processor with no time dir is reported as `constant`, never silently
        shutil.rmtree(os.path.join(mp, "processor2", "1000"))
        _p, used2 = reconstruct_asrun_points(mp, len(gen))
        check("a processor with no moved mesh is NAMED as reading constant",
              used2["processor2"], "constant")
        # a hole REFUSES rather than returning a shorter cloud
        shutil.rmtree(os.path.join(mp, "processor3"))
        try:
            reconstruct_asrun_points(mp, len(gen))
            check("a hole refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("a hole -> REFUSE_ADDR_HOLE", str(e).startswith("REFUSE_ADDR_HOLE"), True)

        # ---- M0 -- TWO GATES, AND THIS FILE DISPATCHES WITHOUT DECIDING -----
        # The decisions live in d6r2c_fm12_stage.py and are driven there, on
        # synthetic trees AND against the real artifacts FM11 left on disk
        # (`--live-controls`).  What is asserted HERE is that this file has no
        # second spelling of them: the fused inherited stager is not called, no
        # mesh-identity decision is re-spelled, and the dispatch is by sub-arm.
        exe_body = "\n".join(
            l for l in open(__file__).read().split("def self" + "test():", 1)[0]
            .splitlines() if not l.lstrip().startswith("#"))
        check("the producer calls the FM12 stager, which dispatches M0b/M0o",
              "stg12.stage_mesh(arm_dir, sub_arm, datum_epoch)" in exe_body, True)
        check("the producer NEVER calls the inherited fused stager, whose "
              "identity guard is what blocked FM11",
              "stg.stage_mesh(" in exe_body, False)
        check("...and the same sweep would FIND that call if it were there",
              "stg.stage_mesh(" in ("    staged = stg.stage_mesh(arm_dir)"), True)
        check("this file spells no comparison against the BASE mesh of its own "
              "-- FM11's measure_against_base is gone, not edited",
              "measure_against_base" in exe_body, False)
        check("...and the base-mesh anchor is IMPORTED from the stager that owns "
              "the M0 decisions, never re-typed here (L-221/L-222)",
              (BASE_POINTS_MD5 is stg12.BASE_POINTS_MD5,
               '"0fb1935a9b8781b73ac4ccb136e3ec68"' in exe_body),
              (True, False))
        check("the ONE point comparison this file still makes is the READ-BACK "
              "of the loaded mesh against the generated mesh, which is M1's "
              "producer-side record and is not an identity test against base",
              "stg.max_point_difference(loaded, generated)" in exe_body, True)
        check("the two gates are reachable and are two distinct callables",
              (stg12.gate_m0b is not stg12.gate_m0o,
               callable(stg12.gate_m0b), callable(stg12.gate_m0o)),
              (True, True, True))
        check("the FM12 stager's own selftest is the place those gates are "
              "driven, and it passes", stg12.selftest(), 0)

        # ---- the checkMesh parser, on a REAL checkMesh line ------------------
        lg = os.path.join(tmp, "cm.log")
        with open(lg, "w") as fh:
            fh.write("Checking faces in error multiple times...\n"
                     "    Max non-orthogonality = 79.21 average: 8.4\n"
                     "Mesh OK.\n")
        check("the checkMesh parser reads the number OpenFOAM prints",
              parse_max_nonorth(lg), 79.21)
        check("79.21 is read as a BREACH of DAFoam's declared 70.0",
              parse_max_nonorth(lg) > MAX_NONORTH_DECLARED, True)
        with open(lg, "w") as fh:
            fh.write("    Max non-orthogonality = 66.32 average: 8.1\n")
        check("66.32 is read as WITHIN the declared limit",
              parse_max_nonorth(lg) > MAX_NONORTH_DECLARED, False)
        check("a log with no such line yields None, NEVER a default",
              parse_max_nonorth(os.path.join(tmp, "nope.log")), None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- the deleted channel is DELETED, asserted on this file's own bytes ---
    # THE SCOPE IS THE EXECUTABLE BODY, NOT THIS FUNCTION.  A source sweep that
    # includes its own needles reports a hit on itself and means nothing -- the
    # split below cuts the file at this function's own definition, and the
    # needles are assembled from fragments so that writing the control cannot
    # create the very string it hunts.
    # The sweep is over EXECUTABLE lines only.  Comment lines are dropped,
    # because the header of this file QUOTES both needles when it explains why
    # the channel was deleted -- and a sweep that cannot tell an explanation
    # from a call site is reading an adjacent quantity (L-595).
    head = open(__file__).read().split("def self" + "test():", 1)[0]
    body = "\n".join(l for l in head.splitlines() if not l.lstrip().startswith("#"))
    needle_read = "primal_res" + "idual.json"
    needle_default = "conv[p]" + " = True"
    check("the executable body READS no primal_residual.json",
          needle_read in body, False)
    check("the executable body DEFAULTS no convergence flag to True",
          needle_default in body, False)
    # and the sweep is driven to its FAILING side, so the green is not vacuous
    check("the same sweep FINDS the needle when it is genuinely present",
          needle_read in ("rp = " + needle_read), True)
    check("the same sweep FINDS the default when it is genuinely present",
          needle_default in ("    " + needle_default), True)

    print("D6R2C_FM12_STATES SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description="D6R2C FM12 producer: the matched-lift "
                                             "states on their own fresh meshes.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--parse-only", action="store_true",
                    help="drive THE LAUNCHER'S OWN ARGUMENT VECTOR through argparse "
                         "and the input validation, then exit BEFORE mpi4py is "
                         "imported.  This is the part of the frozen command line "
                         "that can be exercised outside the container (L-595).")
    ap.add_argument("--arm-dir", default=os.getcwd())
    ap.add_argument("--sub-arm", choices=tuple(sorted(SUB_ARMS)))
    ap.add_argument("--runscript", default="d6r2c_opt_runScript.py")
    ap.add_argument("--evals", default="d6r2c_evals_final.jsonl")
    ap.add_argument("--x0", default="d6r2c_x0_final.json")
    ap.add_argument("--out", default=RECORD)
    ap.add_argument("--datum-file", required=False,
                    help="the arm's age datum.  M0b's load-bearing limb is "
                         "CLAUDE.md rule 4's age guard applied to the mesh, so "
                         "this is REQUIRED when running: a missing datum "
                         "REFUSES rather than defaulting to a permissive clock.")
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.sub_arm:
        ap.error("--sub-arm is required")
    arm = a.arm_dir
    paths = {"runscript": os.path.join(arm, a.runscript),
             "evals": os.path.join(arm, a.evals),
             "x0": os.path.join(arm, a.x0)}
    if a.parse_only:
        # the SAME validation the run does, with the container-only work removed
        print("D6R2C_FM12_PARSE_ONLY sub_arm=%s states=%s arm_dir=%s"
              % (a.sub_arm, ",".join(SUB_ARMS[a.sub_arm]), arm))
        for k, p in sorted(paths.items()):
            print("D6R2C_FM12_PARSE_ONLY   %s=%s exists=%s"
                  % (k, p, os.path.isfile(p)))
        print("D6R2C_FM12_PARSE_ONLY   datum_file=%s exists=%s"
              % (a.datum_file, bool(a.datum_file) and os.path.isfile(a.datum_file)))
        return 0
    try:
        # THE AGE DATUM IS NOT OPTIONAL AT RUN TIME.  A provenance gate with no
        # clock is not a gate, and a default would be a permissive one.
        if not a.datum_file:
            raise Refusal("REFUSE_NO_DATUM_FILE --datum-file is required when "
                          "running: M0b's load-bearing limb is the age guard "
                          "and it has no clock without it (CLAUDE.md rule 4)")
        if not os.path.isfile(a.datum_file):
            raise Refusal("REFUSE_MISSING_DATUM_FILE %s" % a.datum_file)
        datum_epoch = float(open(a.datum_file).read().strip())
        return run(arm, a.sub_arm, paths["runscript"], paths["evals"],
                   paths["x0"], os.path.join(arm, a.out), datum_epoch)
    except Refusal as e:
        print("D6R2C_FM12_STATES REFUSED\n%s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
