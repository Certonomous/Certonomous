#!/usr/bin/env python
r"""Curriculum D19O -- THE COMPRESSIBLE SINGLE-POINT SHAPE OPTIMISATION INSTRUMENT.

NACA0012, `DARhoSimpleFoam`, M 0.288 (U0 100.0 m/s, T0 300 K -> a = 347.19 m/s),
A1's own 4,032-cell mesh, np = 1 on every arm, BOTH TOOLCHAIN ROWS.

THREE MODES, one per arm kind:

  O   -- the IPOPT optimisation.  Writes `d19o_O.json` (the run's own record) and
         `d19o_xopt.json` (the FINAL DESIGN POINT, the input the endpoint arms
         read).  Terminal statement `D19O_O_WRITTEN`.
  XE  -- the ADJOINT gradient AT THE FINAL DESIGN POINT.  Writes `d19o_X.json`.
         Terminal statement `D19O_X_WRITTEN`.
  FE  -- the FINITE-DIFFERENCE table AT THE FINAL DESIGN POINT.  Writes
         `d19o_F.json`.  Terminal statement `D19O_F_WRITTEN`.

`DAFOAM_CHARTER.md` section 9, verbatim on why XE and FE exist and why they are
in THIS item's chain rather than deferred: *"a gradient verified at iteration 0
is not verified at iteration 47"*.  The mechanism is this toolchain's -- the
IDWarp `getRotationMatrix3d` degenerate-rotation branch is GUARANTEED to fire at
the undeformed baseline (`axisMag = 1e-15 < tol = sqrt(eps)`) and its second
regime D-A2 behaves DIFFERENTLY just above the threshold.  D15's, D19's and
D19R's FD tables were all measured at iteration 0.

===========================================================================
THE `shape[7]` HAZARD -- THIS ITEM'S CENTRAL, REGISTERED LIMITATION
===========================================================================
**THIS OPTIMISATION INHERITS AN UNVERIFIED GRADIENT, AND THE INSTRUMENT ENFORCES
THAT IT CANNOT BE PAPERED OVER.**  Two facts, both re-measured at this freeze
from the artefacts named beside them, not carried from any report:

  (1) THE COMPRESSIBLE SINGLE-POINT GRADIENT GATE HAS NO VERDICT AT ALL.
      D19R phase 1 ran clean (six arms, all rc=0, 12.416 core-min) and ITS
      GRADER REFUSED, rc=2, emitting no verdict.  Its successor D19R2's grading
      attempt 1 also returned NOT A RESULT (refusal `G19R-1h`).  So no graded
      compressible FD verdict exists on this ground.

  (2) THE PLATEAU DID NOT CLOSE, AND `shape[7]` IS WHY.  From
      `.../CURRICULUM-D19R-.../d19r_selected_step.json`: `all_two_sided = false`,
      `s* = {shape 1e-3, patchV 1e-2}`, `score_pct = 21.060684242435336`,
      `binding = ["shape[7]", "CD", "fine"]`.  NINE of the ten
      component/function pairs are two-sided at s* with a worst deviation of
      3.334 %; `shape[7]/CD` is one-sided at **21.0607 %** on the fine side.

      RE-MEASURED HERE from `.../X2/d19r_X.json`, the full 8-vector dCD/dshape:
        idx 0  -7.221766503489e-03      idx 4  +3.876018809723e-02
        idx 1  -1.890856088367e-02      idx 5  +4.092612805124e-02
        idx 2  +7.285025342493e-03      idx 6  -1.413381271968e-02
        idx 3  +9.290536413017e-03      idx 7  -2.099480176256e-04   <--
      `shape[7]` is the SMALLEST of the eight.  It is 34.40x smaller than the
      next smallest and 194.93x smaller than the largest, and it carries
      **0.3351 %** of the gradient's norm (2.0995e-04 of ||.|| = 6.2659e-02).

      From `.../S8/d19r_S.json`, `shape[7]/CD` against step (np=2):
        3e-2 -1.4732e-04 | 1e-2 -2.0891e-04 | 3e-3 -2.0956e-04 | 1e-3 -2.0649e-04
        3e-4 -1.9462e-04 | 1e-4 -1.6300e-04 | 3e-5 -4.9843e-05 | 1e-5 +2.5192e-04
      **IT CHANGES SIGN BETWEEN 3e-5 AND 1e-5.**

THE REGISTERED DISPOSITION -- RETAIN THE DV, EXCLUDE THE ROW BY NAME.
`shape[7]` IS RETAINED IN THE DESIGN VECTOR.  The producer declares
`add_design_var("shape", ...)` over the whole 8-vector through one FFD shape
function, and the geometric constraints are defined over that whole FFD;
masking one index would be a DIFFERENT optimisation problem from the one D15,
D19 and D19R measured a gradient for, and the item would then quietly describe
a design space nobody has verified either.

AND ITS FD ROW IS REGISTERED, BEFORE THE RUN, AS A NAMED NON-RESULT.
`EXCLUDED_FROM_AGGREGATE` below names `("shape", 7)`.  `DAFOAM_CHARTER.md`
section 3: a component that does not stabilise is *"flagged and excluded BY NAME
from any aggregate quoted as agreement -- never dropped silently, and never
rescued by a step at which it happens to cross."*  So:

  * every aggregate this instrument writes is over the FOUR remaining
    components and says so in its own key name (`aggregate_pct_excl_flagged`);
  * `shape[7]`'s own per-component reading is COMPUTED AND PUBLISHED beside the
    aggregate, with `graded: false` and `registered_non_result: true`;
  * the exclusion travels in `excluded_from_aggregate` on every record, so a
    reader cannot receive the aggregate without receiving the exclusion.

**AND IT IS NOT RESCUABLE BY A GOOD NUMBER.**  At s* the np=1 agreement on
`shape[7]` is 1.65155 % (FD -2.065369465905e-04 from `.../S1/d19r_S1.json`
against the adjoint above) -- INSIDE the 5 % band.  A lane that had seen only
that number would have graded it.  What is missing is not agreement; it is the
PROOF THAT THE FD ESTIMATE AT s* IS TRUSTWORTHY, and that proof is the plateau,
and the plateau did not close.  `registered_non_result` is therefore set from
the REGISTERED LIST and never from the measured value.

===========================================================================
THE PLATEAU TEST IS D19R's, UNCHANGED -- DECADE NEIGHBOURS, `max` NOT `min`
===========================================================================
`FD_STEPS_ENDPOINT` is s* with its DECADE neighbours (x10 and /10), and
`PLATEAU_TOL_PCT` is 10.0, both identical to `G19R-1b`.  A HALF-DECADE bracket
would be a WEAKER test, and adopting a weaker test after seeing which test the
component failed is exactly what `DAFOAM_CHARTER.md` section 3 forbids
(*"Selecting the step after seeing which one agrees"*).  Strictness is inherited,
not re-derived.

===========================================================================
THE ROW IS READ FROM THE TOOLCHAIN'S OWN IDENTITY, NEVER FROM A FLAG
===========================================================================
This instrument md5s the `libidwarp.so` THIS INTERPRETER ACTUALLY IMPORTED, from
inside the container, and maps it to a row.  **An md5 matching neither
registered toolchain REFUSES.**  A `-row PATCHED` flag would let a mislabelled
launch stamp the wrong row into the artefact the endpoint arm then reads.
"""
import hashlib
import json
import os
import sys
import time

ITEM = "D19O"
PRODUCER = "d19o_runScript.py"

# The producer is BYTE-IDENTICAL to `curriculum_D19R/d19r_runScript.py`, which is
# itself D15's with `max_iter` 100->40.  RE-COMPUTED at this freeze on disk, from
# the committed blob at HEAD, and from the copy in D19R's run root that ACTUALLY
# RAN -- all three agree.  Registered delta from the parent: NONE.
PRODUCER_MD5 = "a5e18503ea29d0e37c3cf1668533cd34"
# The header ABOVE the anchor -- 7,614 bytes, anchor appears exactly once.
HEADER_MD5_SHARED_WITH_D15 = "d1efc43583fbeb59fb5116816b055a07"
ANCHOR = "# OpenMDAO setup"

# ---- TOOLCHAIN IDENTITY, BY LIBRARY HASH (DAFOAM_CHARTER.md section 6) --------
# Both RE-MEASURED at this freeze by running each image and md5-ing the .so the
# interpreter imported.  A version string is not an identity.
ROW_BY_SO_MD5 = {
    "85f59e87253e0a71a813f64ca6e4c425": "PATCHED",   # dafoam-idwarp-rot:v1
    "f0fcb488e0e98156575cd19548e91663": "SHIPPED",   # dafoam/opt-packages:latest
}

# ---- np = 1 IS A CONDITION ON THE INHERITANCE, NOT A SETTING ------------------
# Every compressible FD reference this item can lean on that was taken SERIALLY
# is D19R's `S1` arm.  DAFOAM_CHARTER.md section 5 forbids carrying an FD
# reference across np, and A4 measured a 16,600x spread between two
# decompositions of one mesh.  np=1 ALSO makes D19R2's `MANIFEST_ENTRY_MUTATED`
# blocker unreachable: `decomposePar` never runs, so it never rewrites
# `system/decomposeParDict`.  Enforced here by MPI.Abort, in the launcher's
# `ranks_of`, and in the grader's `ARM_RANKS`.
NP_REQUIRED = 1

# ---- the graded components (D15's, D19's and D19R's, unchanged) --------------
COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7), ("patchV", 1)]

# ---- THE REGISTERED NON-RESULT.  See the module docstring. -------------------
EXCLUDED_FROM_AGGREGATE = [("shape", 7)]
EXCLUSION_REASON = (
    "REGISTERED BEFORE THE RUN as a NON-RESULT on the plateau clause, on BOTH "
    "rows, WHATEVER VALUE IT RETURNS.  D19R measured `shape[7]/CD` one-sided at "
    "21.060684242435336 % on the fine side of s*=1e-3 (`all_two_sided=false`, "
    "`binding=[shape[7],CD,fine]`), and the component changes SIGN between 3e-5 "
    "and 1e-5.  It carries 0.3351 % of ||dCD/dshape||.  DAFOAM_CHARTER.md "
    "section 3: flagged components are excluded BY NAME from any aggregate "
    "quoted as agreement, never dropped silently and never rescued by a step at "
    "which they happen to cross.")

# ---- s*, INHERITED BY CITATION, never re-derived by a lane with an answer -----
S_STAR = {"shape": 1.0e-3, "patchV": 1.0e-2}
S_STAR_SOURCE = ("/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-"
                 "subsonic-plateau/d19r_selected_step.json -> s_star")

# ---- the endpoint plateau test: s* WITH ITS DECADE NEIGHBOURS (G19R-1b's rule)
FD_STEPS_ENDPOINT = {"shape":  [1.0e-2, 1.0e-3, 1.0e-4],
                     "patchV": [1.0e-1, 1.0e-2, 1.0e-3]}
PLATEAU_TOL_PCT = 10.0      # G19R-1b's, unchanged
FD_BAND_PCT = 5.0           # band D, per component (VERIFICATION_CHARTER.md section 7)
AGG_BAND_PCT = 5.0          # band E, aggregate vector-relative

# ---- DAFOAM_CHARTER.md section 4: the trivial baseline, DELIBERATELY WRONG ----
# The same probe at a step five orders below s*.  On a `CD` derivative of order
# 1e-2 the FD numerator at 1e-8 is ~1e-10, at or below the MEASURED primal
# repeatability on this exact case at np=1 (`eta_used = 9.652218954658842e-11`,
# from `.../CURRICULUM-D19R-.../S1/d19r_S1.json`).  The estimate is noise and
# MUST fail band D.  A probe that ERRORS counts as failing the baseline: an
# unevaluable estimate is not a pass.
TB_STEP = 1.0e-8
TB_MAX_PASSING = 1          # >= 2 of the 4 graded components passing WITHDRAWS the row

# ---- CLAUDE.md rule 3: the RELATIVE planted control ---------------------------
PLANT_K = 5.0               # must cross the band with a 5x margin
PLANT_K_SHRUNK = 0.5        # RED leg: must NOT cross
CTRL_STEP = 1.0e-3

# ---- the optimiser (PREREGISTRATION.md section 9) ----------------------------
OPTIMIZER = "IPOPT"
OPT_TOL = 1.0e-5
MAX_MAJORS = 40             # a BUDGET, not a settle criterion.  Reaching it is
                            # GATE REACHED, never PASS.
EXPECTED_MAJOR_ROWS = 12    # MEASURED: SO-1bR O-P, SO-1bR O-S and D1 armO each
                            # returned exactly 11 IPOPT iterations / 12 table
                            # rows on this A1 case at np=1.  Used for PRICING
                            # ONLY; it gates nothing.
CL_TARGET = 0.5             # the producer's own; quoted, not chosen here

OUT = {"O": "d19o_O.json", "XE": "d19o_X.json", "FE": "d19o_F.json"}
XOPT = "d19o_xopt.json"
MODES = tuple(OUT)
ETA_FLOOR = 1.0e-14

CD = "scenario1.aero_post.CD"
CL = "scenario1.aero_post.CL"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def idwarp_identity():
    """The row, from the library this interpreter ACTUALLY imported."""
    import idwarp
    p = idwarp.__file__
    so = os.path.join(os.path.dirname(p), "libidwarp.so")
    m = md5_of(so)
    return {"idwarp_file": p, "libidwarp_so_md5": m, "row": ROW_BY_SO_MD5.get(m)}


def parse_mode(argv):
    mode = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    if mode not in MODES:
        sys.stderr.write("D19O_XF usage: d19o_xf.py -mode %s\n" % "|".join(MODES))
        sys.exit(64)
    return mode


def plant_relative(d_ref, band_pct, k):
    """plant = K * (band/100) * |d_ref|.  Identical to d19o_age_guard.plant_relative."""
    return k * (band_pct / 100.0) * abs(d_ref)


def is_excluded(dv, idx):
    return (dv, idx) in EXCLUDED_FROM_AGGREGATE


def rel_pct(a, b):
    """|a - b| / |b| in percent, or None where b is not usable as a denominator."""
    if b is None or a is None or b == 0.0:
        return None
    return abs(a - b) / abs(b) * 100.0


def plateau_reading(fd_by_step, dv, of_key):
    """The DECADE two-sided plateau at s*, G19R-1b's rule verbatim: BOTH
    neighbour deviations <= PLATEAU_TOL_PCT, `max` and not `min`."""
    steps = FD_STEPS_ENDPOINT[dv]                   # [coarse, s*, fine]
    coarse, centre, fine = steps[0], steps[1], steps[2]
    key = "dCD" if of_key == "CD" else "dCL"

    def val(s):
        r = fd_by_step.get(repr(s))
        if not r or not r.get("ok"):
            return None
        return float(r[key])

    c, m, f = val(coarse), val(centre), val(fine)
    cp, fp = rel_pct(c, m), rel_pct(f, m)
    two_sided = (cp is not None and fp is not None
                 and cp <= PLATEAU_TOL_PCT and fp <= PLATEAU_TOL_PCT)
    return {"s_star": centre, "coarse_step": coarse, "fine_step": fine,
            "coarse_pct": cp, "fine_pct": fp,
            "score_pct": max([x for x in (cp, fp) if x is not None], default=None),
            "two_sided": bool(two_sided),
            "rule": "DECADE neighbours, max over both sides, tol %.1f %% -- "
                    "G19R-1b's rule UNCHANGED" % PLATEAU_TOL_PCT}


def aggregate_excl_flagged(pairs):
    """||adj - fd|| / ||fd|| over the pairs handed in, which are ALWAYS the
    non-excluded ones.  The key name says `excl_flagged` so no reader can take
    it for an all-component aggregate."""
    import math
    if not pairs:
        return None
    num = math.sqrt(sum((a - f) ** 2 for a, f in pairs))
    den = math.sqrt(sum(f * f for _a, f in pairs))
    return None if den == 0.0 else num / den * 100.0


# ============================================================================
# THE WRITERS.  EVERY FIXTURE IN EVERY SELFTEST IN THIS ITEM IS BUILT BY THESE
# FUNCTIONS AND BY NOTHING ELSE.
#
# On 2026-08-31 SO-1c refused because its consumer read `gates` at the top level
# while its producer wrote them at `grade.gates`, and a 51-leg suite could not
# see it BECAUSE THE SUITE'S FIXTURES WERE HAND-BUILT FROM THE CONSUMER'S OWN
# EXPECTATIONS -- a tautology on schema.  These writers are the real producer's
# code; the grader's selftest imports them rather than reproducing their shape,
# so a producer/consumer divergence fails LOUDLY instead of passing quietly.
# ============================================================================
def build_fd_step(step, cdp, cdm, clp, clm):
    """One central-difference row, exactly as mode FE writes it."""
    dcd, dcl = (cdp - cdm) / (2.0 * step), (clp - clm) / (2.0 * step)
    ok = all(v == v and abs(v) != float("inf") for v in (dcd, dcl))
    return {"step": step, "dCD": repr(dcd), "dCL": repr(dcl),
            "CD_plus": repr(cdp), "CD_minus": repr(cdm),
            "CL_plus": repr(clp), "CL_minus": repr(clm),
            "ok": bool(ok), "is_trivial_baseline": bool(step == TB_STEP)}


def row_from_fd(dv, idx, fd):
    """Assemble ONE component row from an already-built `fd` dict.

    THE SINGLE WRITER FOR A COMPONENT ROW.  Mode FE calls this on the fd dict it
    accumulates step by step (it cannot use `build_fd_row`, because each of its
    steps is a real solve inside a try/except that must emit as it goes), and
    `build_fd_row` calls it too.  They therefore CANNOT drift: the exclusion
    flags and the plateau readings are written in exactly one place.  A selftest
    leg counts the `excluded_from_aggregate` sites and caught the earlier version
    of this file, in which the FE loop carried its own copy."""
    return {"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd,
            "excluded_from_aggregate": is_excluded(dv, idx),
            "registered_non_result": is_excluded(dv, idx),
            "plateau_CD": plateau_reading(fd, dv, "CD"),
            "plateau_CL": plateau_reading(fd, dv, "CL")}


def build_fd_row(dv, idx, per_step):
    """One component row from raw primal pairs.  `per_step` maps
    step -> (cdp, cdm, clp, clm).  Used to build every fixture in this item."""
    return row_from_fd(dv, idx, {repr(s): build_fd_step(s, *v)
                                 for s, v in per_step.items()})


def build_ctrl_row(cd0, cl0, k=PLANT_K, k_shrunk=PLANT_K_SHRUNK, band=FD_BAND_PCT):
    """The planted control, exactly as mode FE writes it."""
    plant = plant_relative(cd0, band, k)
    plant_sh = plant_relative(cd0, band, k_shrunk)
    moved = abs(plant) / abs(cd0) * 100.0
    moved_sh = abs(plant_sh) / abs(cd0) * 100.0
    return {"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "dCL": repr(0.0),
                          "CD_plus": repr(cd0), "CD_minus": repr(cd0),
                          "CL_plus": repr(cl0), "CL_minus": repr(cl0), "ok": True,
                          "note": "synthetic: identical DVs on both sides -> exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": repr(plant), "K": k,
                    "band_pct": band, "d_ref": repr(cd0),
                    "formula": "plant = K * (band/100) * |d_ref|",
                    "moved_pp": repr(moved), "crosses_band": bool(moved > band),
                    "dCD": repr(plant / (2.0 * CTRL_STEP)),
                    "CD_plus": repr(cd0 + plant), "CD_minus": repr(cd0), "ok": True},
        "planted_shrunk": {"step": CTRL_STEP, "plant": repr(plant_sh), "K": k_shrunk,
                           "band_pct": band, "moved_pp": repr(moved_sh),
                           "crosses_band": bool(moved_sh > band),
                           "dCD": repr(plant_sh / (2.0 * CTRL_STEP)),
                           "note": "SUFFICIENCY RED LEG -- must NOT cross the band"}}


def _exec_header():
    """Exec the producer's FROZEN header and return its namespace.  The header is
    hashed against D15's before it is executed, so `G-HDR` reproduction is a
    property of the bytes and not of a comment."""
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D19O_XF REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)
    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D19O_XF REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]
    hmd5 = hashlib.md5(header.encode()).hexdigest()
    if hmd5 != HEADER_MD5_SHARED_WITH_D15:
        sys.stderr.write("D19O_XF REFUSE producer header md5 %s != D15's %s\n"
                         % (hmd5, HEADER_MD5_SHARED_WITH_D15))
        sys.exit(2)
    sys.stdout.write("D19O_HEADER_IDENTICAL_TO_D15 md5=%s\n" % hmd5)
    saved = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", OPTIMIZER]
    ns = {"__name__": "d19o_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved
    return ns, got, hmd5


def main():
    mode = parse_mode(sys.argv)
    ns, prod_md5, hmd5 = _exec_header()

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    if nprocs != NP_REQUIRED:
        sys.stderr.write("D19O_XF REFUSE np=%d; this item is registered at np=%d on EVERY "
                         "arm.  DAFOAM_CHARTER.md section 5 forbids carrying an FD "
                         "reference across np.\n" % (nprocs, NP_REQUIRED))
        MPI.COMM_WORLD.Abort(2)

    ident = idwarp_identity()
    if ident["row"] is None:
        sys.stderr.write("D19O_XF REFUSE libidwarp.so md5 %s matches NEITHER registered "
                         "toolchain %r -- this producer will not stamp a row it cannot "
                         "prove.\n" % (ident["libidwarp_so_md5"], sorted(ROW_BY_SO_MD5)))
        MPI.COMM_WORLD.Abort(2)
    row = ident["row"]
    sys.stdout.write("D19O_ROW_FROM_TOOLCHAIN row=%s libidwarp_so_md5=%s imported_from=%s\n"
                     % (row, ident["libidwarp_so_md5"], ident["idwarp_file"]))

    jsonl = OUT[mode].replace(".json", ".jsonl")

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def write_json(path, obj):
        with open(path, "w") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())

    emit({"kind": "identity", "item": ITEM, "mode": mode, "row": row, "nprocs": nprocs,
          "producer_md5": prod_md5, "header_md5": hmd5,
          "solverName": ns["daOptions"].get("solverName"),
          "primalMinResTol": ns["daOptions"].get("primalMinResTol"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "T0": ns.get("T0"),
          "p0": ns.get("p0"), "CL_target": ns.get("CL_target"), **ident})

    Top = ns["Top"]
    prob = om.Problem()
    prob.model = Top()

    # ======================= mode O: the optimisation =========================
    if mode == "O":
        prob.driver = om.pyOptSparseDriver()
        prob.driver.options["optimizer"] = OPTIMIZER
        prob.driver.opt_settings = {
            "tol": OPT_TOL,
            "constr_viol_tol": OPT_TOL,
            "max_iter": MAX_MAJORS,
            "print_level": 5,
            "output_file": "opt_IPOPT.txt",
            "mu_strategy": "adaptive",
            "limited_memory_max_history": 10,
            "nlp_scaling_method": "none",
            "alpha_for_y": "full",
            "recalc_y": "yes",
        }
        prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
        prob.driver.options["print_opt_prob"] = True
        prob.driver.hist_file = "OptView.hst"
        prob.setup(mode="rev")

        optFuncs = ns["OptFuncs"](ns["daOptions"], prob)
        b0 = {k: np.array(prob.get_val(k), dtype=float).copy() for k in ("shape", "patchV")}
        emit({"kind": "dv0", "shape": [repr(float(v)) for v in b0["shape"]],
              "patchV": [repr(float(v)) for v in b0["patchV"]],
              "n_shape": int(b0["shape"].size)})

        # The producer's own trim, quoted from `d19o_runScript.py:239`.  It moves
        # `patchV[1]` (aoa) to hit CL_target BEFORE the optimiser starts, so the
        # baseline CD/CL this item reports are the TRIMMED ones and are labelled so.
        t0 = time.time()
        optFuncs.findFeasibleDesign([CL], ["patchV"], targets=[CL_TARGET], designVarsComp=[1])
        trim_s = time.time() - t0
        prob.run_model()
        cd_b, cl_b = float(prob.get_val(CD)[0]), float(prob.get_val(CL)[0])
        b_trim = {k: np.array(prob.get_val(k), dtype=float).copy() for k in ("shape", "patchV")}
        emit({"kind": "baseline_trimmed", "CD": repr(cd_b), "CL": repr(cl_b),
              "patchV": [repr(float(v)) for v in b_trim["patchV"]],
              "trim_wall_s": round(trim_s, 3)})

        t0 = time.time()
        fail = prob.run_driver()
        opt_s = time.time() - t0

        cd_f, cl_f = float(prob.get_val(CD)[0]), float(prob.get_val(CL)[0])
        xopt = {k: np.array(prob.get_val(k), dtype=float).copy() for k in ("shape", "patchV")}

        # THE OPTIMISER'S OWN WORDS, READ FROM ITS OWN LOG.  Never inferred.
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import d19o_stall as STALL
        log = "opt_IPOPT.txt"
        if os.path.isfile(log):
            L = STALL.read_log(log)
        else:
            L = {"n_rows": 0, "convergence": {"exit": None, "n_iterations": None,
                                              "converged": False},
                 "stall": STALL.stall_reach([]), "cutbacks": {}}

        if rank == 0:
            red = (cd_b - cd_f) / cd_b * 100.0 if cd_b else None
            out = {
                "item": ITEM, "mode": "O", "row": row, "nprocs": nprocs,
                "producer_md5": prod_md5, "header_md5": hmd5, "identity": ident,
                "optimizer": OPTIMIZER, "opt_tol": OPT_TOL,
                "max_iter_registered": MAX_MAJORS,
                "expected_major_rows_for_pricing_only": EXPECTED_MAJOR_ROWS,
                "driver_fail_flag": bool(fail),
                # --- the four numbers a reader needs, and the CL pair travels ---
                "CD_baseline_trimmed": repr(cd_b), "CL_baseline_trimmed": repr(cl_b),
                "CD_final": repr(cd_f), "CL_final": repr(cl_f),
                "CL_target": CL_TARGET,
                "drag_reduction_pct": repr(red) if red is not None else None,
                "_drag_reduction_is_not_a_verdict":
                    "DAFOAM_CHARTER.md section 9 FORBIDS grading an optimisation by the "
                    "size of its improvement.  This number is reported; it grades nothing.",
                # --- the optimiser's own statement --------------------------------
                "ipopt_exit": L["convergence"]["exit"],
                "ipopt_n_iterations": L["convergence"]["n_iterations"],
                "ipopt_printed_convergence": L["convergence"]["converged"],
                "ipopt_table_rows": L["n_rows"],
                "stall": L["stall"], "cutbacks": L["cutbacks"],
                "_row_vs_label":
                    "`ipopt_table_rows` is a 1-based ROW COUNT; `ipopt_n_iterations` is "
                    "IPOPT's own 0-based label as printed.  Both are given because a "
                    "single number here would be an ambiguity (SO-3 section 9.3).",
                "wall_s_trim": round(trim_s, 3), "wall_s_optimiser": round(opt_s, 3),
                "dv_initial": {k: [repr(float(v)) for v in b0[k]] for k in b0},
                "dv_trimmed": {k: [repr(float(v)) for v in b_trim[k]] for k in b_trim},
                "dv_final": {k: [repr(float(v)) for v in xopt[k]] for k in xopt},
                "excluded_from_aggregate": [[d, i] for d, i in EXCLUDED_FROM_AGGREGATE],
                "excluded_from_aggregate_reason": EXCLUSION_REASON,
                "inherits_unverified_gradient": True,
                "_inherits_unverified_gradient_why":
                    "The compressible single-point FD gate has NO GRADED VERDICT "
                    "(D19R's grader refused rc=2; D19R2 grading attempt 1 = NOT A "
                    "RESULT), and D19R's plateau did not close: all_two_sided=false, "
                    "score_pct=21.060684242435336, binding=[shape[7],CD,fine].",
            }
            write_json(OUT["O"], out)
            write_json(XOPT, {
                "item": ITEM, "row": row, "producer_md5": prod_md5,
                "shape": [repr(float(v)) for v in xopt["shape"]],
                "patchV": [repr(float(v)) for v in xopt["patchV"]],
                "CD_final": repr(cd_f), "CL_final": repr(cl_f),
                "ipopt_printed_convergence": L["convergence"]["converged"],
                "_what_this_is": "THE FINAL DESIGN POINT.  The endpoint arms XE and FE "
                                 "read it and evaluate AT IT, which is what "
                                 "DAFOAM_CHARTER.md section 9 requires and what no item "
                                 "in this family had done before SO-3."})
            sys.stdout.write("D19O_O_WRITTEN %s rows=%d exit=%r converged=%s\n"
                             % (OUT["O"], L["n_rows"], L["convergence"]["exit"],
                                L["convergence"]["converged"]))
        MPI.COMM_WORLD.Barrier()
        return

    # =============== modes XE / FE: AT THE FINAL DESIGN POINT =================
    if not os.path.isfile(XOPT):
        sys.stderr.write("D19O_XF REFUSE mode %s needs %s from arm O -- an endpoint check "
                         "evaluated at the BASELINE would be the very thing "
                         "DAFOAM_CHARTER.md section 9 forbids.\n" % (mode, XOPT))
        MPI.COMM_WORLD.Abort(2)
    xo = json.load(open(XOPT))
    if xo.get("row") != row:
        sys.stderr.write("D19O_XF REFUSE %s was written on row %r; this arm is on row %r. "
                         "An endpoint gradient belongs to the optimum its OWN row "
                         "produced.\n" % (XOPT, xo.get("row"), row))
        MPI.COMM_WORLD.Abort(2)

    prob.setup(mode="rev")
    import numpy as np
    base = {"shape": np.array([float(v) for v in xo["shape"]], dtype=float),
            "patchV": np.array([float(v) for v in xo["patchV"]], dtype=float)}
    for k in ("shape", "patchV"):
        got_n = int(np.array(prob.get_val(k)).size)
        if got_n != base[k].size:
            sys.stderr.write("D19O_XF REFUSE %s length %d in %s but %d in the model\n"
                             % (k, base[k].size, XOPT, got_n))
            MPI.COMM_WORLD.Abort(2)
        prob.set_val(k, base[k].copy())
    emit({"kind": "design_point_record", "source": XOPT,
          "shape": [repr(float(v)) for v in base["shape"]],
          "patchV": [repr(float(v)) for v in base["patchV"]],
          "CD_at_optimum_from_O": xo.get("CD_final"), "CL_at_optimum_from_O": xo.get("CL_final")})

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        cd = float(prob.get_val(CD)[0])
        cl = float(prob.get_val(CL)[0])
        emit({"kind": "primal", "tag": tag, "CD": repr(cd), "CL": repr(cl),
              "wall_s": round(time.time() - t0, 3)})
        return cd, cl

    def set_perturbed(dv, idx, delta):
        for k in ("shape", "patchV"):
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    cd0, cl0 = primal("endpoint_baseline")

    # ======================= mode XE: the adjoint =============================
    if mode == "XE":
        t0 = time.time()
        totals = prob.compute_totals(of=[CD, CL], wrt=["shape", "patchV"])
        emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
        jadj = {}
        for of_name, of_key in ((CD, "CD"), (CL, "CL")):
            jadj[of_key] = {}
            for dv in ("shape", "patchV"):
                arr = np.atleast_1d(np.array(totals[(of_name, dv)]).ravel())
                jadj[of_key][dv] = [repr(float(v)) for v in arr]
                emit({"kind": "adjoint", "of": of_key, "dv": dv, "n": int(arr.size),
                      "values": jadj[of_key][dv]})
        if rank == 0:
            write_json(OUT["XE"], {
                "item": ITEM, "mode": "XE", "row": row, "nprocs": nprocs,
                "producer_md5": prod_md5, "header_md5": hmd5, "identity": ident,
                "at_design_point": XOPT,
                "design_point": {"shape": xo["shape"], "patchV": xo["patchV"]},
                "CD_at_design_point": repr(cd0), "CL_at_design_point": repr(cl0),
                "adjoint": jadj,
                "no_optimiser_ran": True,
                "excluded_from_aggregate": [[d, i] for d, i in EXCLUDED_FROM_AGGREGATE],
                "excluded_from_aggregate_reason": EXCLUSION_REASON})
            sys.stdout.write("D19O_X_WRITTEN %s\n" % OUT["XE"])
        MPI.COMM_WORLD.Barrier()
        return

    # ======================= mode FE: the endpoint FD table ===================
    cd0r, cl0r = primal("endpoint_baseline_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged,
          "note": "SAME-MESH rerun determinism AT THE OPTIMUM.  It is the WEAKEST "
                  "bound available and is not the perturbed-mesh noise; D19R's arm "
                  "N2 measured that one at the BASELINE and this item does not "
                  "re-measure it."})

    declared = 0
    rows = []
    evaluation_failures = []
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": int(base[dv].size), "fd": {}})
            continue
        fd = {}
        steps = list(FD_STEPS_ENDPOINT[dv]) + [TB_STEP]
        for s in steps:
            key = repr(s)
            declared += 2                       # a plus and a minus evaluation
            try:
                set_perturbed(dv, idx, +s)
                cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
                fd[key] = build_fd_step(s, cdp, cdm, clp, clm)   # THE WRITER
                ok = fd[key]["ok"]
                if not ok:
                    evaluation_failures.append({"dv": dv, "idx": idx, "step": s,
                                                "reason": "non-finite estimate"})
            except Exception as exc:                          # noqa: BLE001
                # A FAILED EVALUATION IS WRITTEN, NOT OMITTED.  An F arm that
                # silently writes fewer rows and calls itself complete is the
                # failure the census exists to catch.
                fd[key] = {"step": s, "ok": False, "error": repr(exc)[:400],
                           "is_trivial_baseline": bool(s == TB_STEP)}
                evaluation_failures.append({"dv": dv, "idx": idx, "step": s,
                                            "reason": repr(exc)[:200]})
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        rows.append(row_from_fd(dv, idx, fd))                   # THE SINGLE WRITER
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())
    declared += 2                                # the baseline and its repeat

    # ---- CLAUDE.md rule 3: the RELATIVE plant, BOTH LEGS, read back from disk
    d_ref = cd0
    plant = plant_relative(d_ref, FD_BAND_PCT, PLANT_K)
    plant_shrunk = plant_relative(d_ref, FD_BAND_PCT, PLANT_K_SHRUNK)
    moved_pp = abs(plant) / abs(d_ref) * 100.0
    moved_pp_shrunk = abs(plant_shrunk) / abs(d_ref) * 100.0
    ctrl = build_ctrl_row(cd0, cl0)                             # THE WRITER
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        seen_zero = seen_plant = seen_shrunk = None
        with open(jsonl) as fh:
            for line in fh:
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    r = rec["row"]
                    seen_zero = float(r["fd"][repr(CTRL_STEP)]["dCD"])
                    seen_plant = float(r["planted"]["dCD"])
                    seen_shrunk = float(r["planted_shrunk"]["dCD"])
        want, want_sh = plant / (2.0 * CTRL_STEP), plant_shrunk / (2.0 * CTRL_STEP)
        if (seen_zero != 0.0 or seen_plant is None
                or abs(seen_plant - want) > 1e-12 * abs(want)
                or seen_shrunk is None
                or abs(seen_shrunk - want_sh) > 1e-12 * abs(want_sh)):
            sys.stderr.write("D19O_XF REFUSE planted-zero control not seen on read-back: "
                             "zero=%r plant=%r want=%r shrunk=%r want_shrunk=%r\n"
                             % (seen_zero, seen_plant, want, seen_shrunk, want_sh))
            sys.exit(2)
        if not moved_pp > FD_BAND_PCT:
            sys.stderr.write("D19O_XF REFUSE plant at K=%r moves %.4f pp and does NOT cross "
                             "the %.1f pp band -- this is the SO-2M failure\n"
                             % (PLANT_K, moved_pp, FD_BAND_PCT))
            sys.exit(2)
        if moved_pp_shrunk > FD_BAND_PCT:
            sys.stderr.write("D19O_XF REFUSE shrunken plant at K=%r moves %.4f pp and DOES "
                             "cross the %.1f pp band -- the control is not measuring "
                             "crossing\n" % (PLANT_K_SHRUNK, moved_pp_shrunk, FD_BAND_PCT))
            sys.exit(2)
        sys.stdout.write("D19O_PLANTED_CONTROL_SEEN zero=%r K=%r moved=%.4f pp CROSSES | "
                         "K_shrunk=%r moved=%.4f pp DOES NOT CROSS (band %.1f pp)\n"
                         % (seen_zero, PLANT_K, moved_pp, PLANT_K_SHRUNK,
                            moved_pp_shrunk, FD_BAND_PCT))
        write_json(OUT["FE"], {
            "item": ITEM, "mode": "FE", "row": row, "nprocs": nprocs,
            "producer_md5": prod_md5, "header_md5": hmd5, "identity": ident,
            "at_design_point": XOPT,
            "design_point": {"shape": xo["shape"], "patchV": xo["patchV"]},
            "CD_at_design_point": repr(cd0), "CL_at_design_point": repr(cl0),
            "CD_at_design_point_repeat": repr(cd0r), "CL_at_design_point_repeat": repr(cl0r),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "components_requested": [[d, i] for d, i in COMPONENTS],
            "steps_endpoint": FD_STEPS_ENDPOINT, "s_star": S_STAR,
            "s_star_source": S_STAR_SOURCE,
            "trivial_baseline_step": TB_STEP, "tb_max_passing": TB_MAX_PASSING,
            "plateau_tol_pct": PLATEAU_TOL_PCT,
            "fd_band_pct": FD_BAND_PCT, "agg_band_pct": AGG_BAND_PCT,
            "evaluations_declared": declared,
            "evaluations_failed": len(evaluation_failures),
            "evaluation_failures": evaluation_failures,
            "ctrl_step": CTRL_STEP, "plant": repr(plant), "plant_K": PLANT_K,
            "plant_shrunk": repr(plant_shrunk), "plant_K_shrunk": PLANT_K_SHRUNK,
            "plant_moved_pp": repr(moved_pp), "plant_moved_pp_shrunk": repr(moved_pp_shrunk),
            "rows": rows, "n_rows": len(rows),
            "contains_adjoint": False,
            "no_optimiser_ran": True,
            "excluded_from_aggregate": [[d, i] for d, i in EXCLUDED_FROM_AGGREGATE],
            "excluded_from_aggregate_reason": EXCLUSION_REASON})
        sys.stdout.write("D19O_F_WRITTEN %s n_rows=%d evals_declared=%d evals_failed=%d\n"
                         % (OUT["FE"], len(rows), declared, len(evaluation_failures)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
