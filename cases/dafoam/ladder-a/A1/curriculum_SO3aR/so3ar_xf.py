#!/usr/bin/env python
"""Curriculum SO-3aR -- NACA0012, THE ALPHA-MULTIPOINT WEIGHTED OBJECTIVE
`J = SUM_i w_i * CD_i(alpha_i)` on the verified incompressible ground: the
FD-VERIFIED MULTIPOINT GRADIENT RUNG.  PREREGISTRATION.md section 7 row 3,
frozen 1a06a7d6.  Modes X (adjoint / compute_totals) and F (central FD table).

DERIVED FROM `curriculum_SO2a/so2a_xg.py` (the parent named in section 7 row 3)
with EXACTLY the registered deltas below and no other.

  * THE GRADED QUANTITY IS THE MULTIPOINT OBJECTIVE `J` AND EACH SCENARIO'S
    `CL_i`, NOT the three geometric constraints.  SO-2a's `thickcon`/`volcon`/
    `rcon` family is GONE from this instrument, and with it `CONSTRAINTS`,
    `CON_SIZES_EXPECTED`, `con_vector` and `read_constraints`.  The quantities
    are line 3 of the frozen TEN LINES: `CD_i`, `CL_i` for i = 1,2,3; `J`;
    `J_adj[J, shape[k]]`; `J_adj[CL_i, shape[k]]`; the PER-SCENARIO
    decomposition `J_adj[CD_i, shape[k]]` that G-MP-STRUCT sums.

  * THREE OPERATING POINTS DIFFERING ONLY IN ANGLE OF ATTACK, and their alphas
    are READ BACK FROM THE MODEL rather than assumed from the constants.  Line 4
    registers {3.13918623195176, 5.13918623195176, 7.13918623195176} degrees.
    G-ALPHA in the comparator reads them out of the artefact's own identity
    record and REFUSES on a mismatch beyond 1e-12 absolute, so this instrument's
    duty is to RECORD WHAT THE MODEL ACTUALLY HELD, never to echo its own
    constant.  `alphas_read_back` is that reading and `alphas_registered` sits
    beside it so a reader compares two independently sourced lists.

  * `patchV` IS NOT A DESIGN VARIABLE IN THIS ITEM and is REMOVED from
    `COMPONENTS`, which is a registered removal (line 4) and not a silent one.
    alpha is the OPERATING POINT that distinguishes the scenarios, so it cannot
    simultaneously be a design variable trimmed to a lift target.  Consequently
    SO-2a's `STEPS["patchV"]` and its G-STRUCT exact-zero probe are BOTH gone;
    SO-3aR's structural gate is G-MP-STRUCT, on the assembly identity, and the
    per-scenario adjoint decomposition this file writes is what buys it.

  * THE STEP-BASED TRIVIAL BASELINE IS BACK, at h = 1e-8, and that is a
    registered REVERSAL of SO-2a's decision with SO-2a's own stated reason.
    SO-2a refused a step-based baseline because a GEOMETRIC constraint is
    bit-repeatable and h = 1e-8 never enters subtractive cancellation.  SO-3aR's
    quantity is a FLOW FUNCTIONAL again -- D15 measured eta_F = 1.30e-10 on this
    mesh -- so h = 1e-8 IS in the cancellation regime and IS a valid wrong step.
    That is SO-1a's `TB_STEPS` reading, restored for the quantity it fits.
    G-TB (section 3): PASS iff AT MOST 1 of the 4 registered components passes
    band D at the wrong step.

  * AN EVALUATION FAILURE IS A RECORDED, COUNTED, GRADABLE STATE.  Section 6
    registers P-EVAL: at least one of the 34 declared evaluations per F arm is
    expected to fail or return a non-finite value, because a multipoint
    evaluation survives only if ALL THREE primals converge.  So every primal is
    wrapped, `evaluations_declared` and `evaluations_failed` are written into the
    artefact PER ARM, and a failed step is written as `ok: False` with its error
    rather than omitted.  A row that is omitted cannot be graded; a row that is
    present and marked failed can.  D6-GRADER-DEF-1 is the cost of the other
    choice.

  * NON-FINITE IS A FAILURE, CHECKED HERE RATHER THAN LEFT TO THE READER.  IPOPT
    said `Invalid number in NLP function or derivative detected` because a model
    handed it a NaN; a NaN that reaches the artefact as a number is a NaN the
    comparator must re-detect.  `_finite_or_raise` turns it into a recorded
    failure at the point of measurement, where the tag is still known.

  * ARTEFACT CONSTRUCTION IS FACTORED INTO `build_X_record` / `build_F_record` /
    `build_fd_row` / `build_ctrl_row` / `write_artefact`, WHICH `main()` USES AND
    THE COMPARATOR'S SELFTEST IMPORTS AND DRIVES -- SO-2a's shape, kept.  Sanaa's
    birth requirement, 2026-08-28, verbatim: *"A planted control must travel the
    real production path -- written by the real producer's code, read through the
    real reader"*.  Nothing in this module imports mpi4py, openmdao, numpy or
    dafoam at module scope, so the writers are importable on the HOST without a
    container, which is what makes the requirement dischargeable at all.

  * AND ONE THING SO-2a DID NOT DO: THE PLANTED-CONTROL READ-BACK IS A NAMED
    FUNCTION, NOT AN INLINE BLOCK IN `main()`.  SO-2a's read-back refusal lives
    inside `main()` (so2a_xg.py:445-470), which needs MPI, openmdao and a
    container to reach -- so the refusal branch of this family's own rule-3
    control has never been driven on the host, only reasoned about.
    `ctrl_readback_check()` here takes a path and returns a verdict, and the
    comparator's selftest drives it in BOTH directions: a live plant SEEN, and a
    dead plant REFUSED.  A guard that cannot be driven is a guard nobody has
    tested (the SO-1b inline-heredoc lesson, applied one level down).

  * Printed tokens SO2A_* -> SO3AR_*; artefact names so2a_* -> so3ar_*.
  * The two-primal eta measurement, the CTRL planted-zero component with its
    disk read-back refusal, the emit/fsync discipline, the producer-md5 refusal
    and the MPI rank-0 file rule are SO-1a's / SO-2a's / D15's / D5's / D4's
    bytes.

DAFOAM_CHARTER.md section 2: an adjoint gradient is not a result until an FD
table stands beside it.  Section 3: the step is proved to lie in the plateau --
and section 7/G5J of the frozen registration requires that proof PER PAIR, never
once for the item.  Section 4: the gate names its trivial baseline BEFORE its own
run.  Section 5: serial before parallel, np = 1 on every arm.  Section 6: two
rows, identity by hash.  All five are instrumented here.
"""

import hashlib
import json
import math
import os
import sys
import time

PRODUCER = "so3ar_runScript.py"
# ---- THE PRODUCER PIN.  THIS CONSTANT IS THE WHOLE REASON SO-3aR EXISTS.
# ----
# ---- SO-3a shipped this line still holding a SENTINEL.  Its container started,
# ---- its solver exited 2 in ten seconds, and its log carried, verbatim:
# ----
# ----   SO3A_XF REFUSE producer md5 c0821199159026ec597549ee034b73ac
# ----           != frozen UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED
# ----
# ---- The pin WORKED.  It refused to run the instrument against an unverified
# ---- producer, and the md5 it printed was the correct md5 of the real
# ---- producer.  SO-3a could never have launched; item verdict NOT A RESULT.
# ----
# ---- The sentinel's design was RIGHT and its census was WRONG.  The value was
# ---- deliberately NOT 32 hex, so it could never accidentally equal a file's
# ---- digest -- and that same property put it OUTSIDE the pin census's rule
# ---- set, which selected pins by the SHAPE OF THE VALUE and read only the
# ---- chain driver.  The census reported "13 declared, 13 driven" and was
# ---- right about thirteen md5-shaped constants in one file and silent about a
# ---- fourteenth that was not.  `so3ar_pin_census.py` sweeps BY ROLE and
# ---- asserts, in A2, that a pin of this kind holds a real md5.
# ----
# ---- SET, and equal to md5(so3ar_runScript.py).  It is asserted by A3 of the
# ---- census on every drive, and DRIVEN in both directions by (p1)-(p4) of
# ---- `so3ar_groot5_selftest.sh`: REFUSE on a mutated producer, PASS on the
# ---- real one, restore proved byte-identical by hash.
PRODUCER_MD5 = "53ba67c95461f86a585cb7ec7cdc2b39"
ANCHOR = "# OpenMDAO setup"
ITEM = "SO3aR"

# ---- registered constants (PREREGISTRATION.md THE TEN LINES; that document
# ---- governs and NOTHING here may move a gate, threshold, cap or label) -------
ETA_FLOOR = 1.0e-14

# LINE 4.  THREE alpha, degrees.  The CENTRE is a QUOTATION from
# `curriculum_SO2a/so2a_runScript.py:35` -- the tutorial's own trimmed angle at
# CL_target = 0.5.  The +/-2 degree bracket is lane-chosen and registered as
# lane-chosen, on the three grounds line 4 states.
ALPHAS_REGISTERED = [3.13918623195176, 5.13918623195176, 7.13918623195176]
# LINE 4.  EQUAL WEIGHTS.  A choice, not a default, and named as one.  Written as
# 1.0/3.0 rather than 0.3333... so the artefact carries the exact binary value
# the objective actually used.
WEIGHTS_REGISTERED = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
# The scenario group names the PRODUCER declares.  The instrument reads the
# alphas back through these paths; a name that does not resolve is RECORDED as
# unresolved, never silently replaced by the registered constant.
SCENARIOS = ("point0", "point1", "point2")
N_SCEN = len(SCENARIOS)
OBJ_PATH = "obj.J"          # the om.ExecComp output that assembles J

STEPS = {
    "shape": [1.0e-2, 1.0e-3, 1.0e-4],     # registered step set, FFD y units
}
# THE CHARTER-4 TRIVIAL BASELINE, REGISTERED BEFORE ITS OWN RUN: the SAME probe
# at a DELIBERATELY WRONG step five orders below the registered middle step.  On
# a derivative of order 1e-2 the FD numerator at h = 1e-8 is ~1e-10, at or below
# the primal repeatability eta (D15 measured eta_F = 1.30e-10 on this mesh), so
# the estimate is noise and MUST fail band D.  G-TB: PASS iff AT MOST 1 of the 4
# components passes band D here.  If 2 or more pass, that row's G5J verdict is
# WITHDRAWN to NOT A RESULT.
TB_STEPS = {
    "shape": [1.0e-8],
}
# THE REGISTERED DV SUBSET (line 3): four `shape` components, SO-1a's and SO-2a's
# own, so the three items' readings sit on the same components.  `patchV` is NOT
# here -- line 4 removes it, because alpha is this item's OPERATING POINT.
COMPONENTS = [
    ("shape", 0),
    ("shape", 3),
    ("shape", 6),
    ("shape", 7),
]
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03            # rule 3

# Section 4's evaluation census, COMPUTED FROM THE CONSTANTS ABOVE rather than
# copied as a literal, so a step or component added here cannot leave a stale
# count in the artefact.  2 baselines + 4 components x 3 steps x 2 signs
# + 4 components x 1 wrong step x 2 signs = 2 + 24 + 8 = 34 EVALUATIONS,
# each of which is 3 primals -> 102 primals per F arm.
EVALS_DECLARED = (2
                  + len(COMPONENTS) * len(STEPS["shape"]) * 2
                  + len(COMPONENTS) * len(TB_STEPS["shape"]) * 2)

OUT_X = "so3ar_X.json"
OUT_F = "so3ar_F.json"
JSONL_F = "so3ar_F.jsonl"
JSONL_X = "so3ar_X.jsonl"
TERMINAL_X = "SO3AR_X_WRITTEN"
TERMINAL_F = "SO3AR_F_WRITTEN"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def idwarp_identity():
    try:
        import idwarp
        p = idwarp.__file__
        so = os.path.join(os.path.dirname(p), "libidwarp.so")
        return {"idwarp_file": p, "libidwarp_so_md5": md5_of(so)}
    except Exception as exc:                                  # noqa: BLE001
        return {"idwarp_file": None, "libidwarp_so_md5": None, "error": repr(exc)[:200]}


def case_write_compression():
    """Read `writeCompression` from THE CASE'S OWN system/controlDict.

    AV-1 and AV-2 both returned NOT A RESULT on 2026-08-27 because a frozen
    comparator pinned the age-guard datum to the NAME `0/U` while
    `writeCompression on` rewrites it as `0/U.gz` on a serial arm.  The setting
    is a recorded datum of the run, never an assumption of a reader.
    """
    p = os.path.join("system", "controlDict")
    try:
        for line in open(p, errors="replace"):
            s = line.strip()
            if s.startswith("writeCompression"):
                return {"write_compression": s.rstrip(";").split()[-1],
                        "write_compression_source": os.path.abspath(p)}
    except OSError as exc:                                    # noqa: BLE001
        return {"write_compression": None, "write_compression_source": None,
                "write_compression_error": repr(exc)[:200]}
    return {"write_compression": None, "write_compression_source": os.path.abspath(p),
            "write_compression_error": "key absent from controlDict"}


# ===================== THE ARTEFACT WRITERS ===================================
# These functions ARE the production write path.  `main()` calls them and NOTHING
# ELSE writes an artefact.  The comparator's selftest IMPORTS AND CALLS THEM to
# build every fixture, so a fixture cannot carry a key this instrument does not
# emit and cannot miss a key it does.  They take plain Python floats and lists
# and import nothing beyond the stdlib, so they run on the host without DAFoam.

def s_(v):
    """One scalar as the artefact stores it: a `repr` string, so the artefact is
    exact and the reader's `float()` is the only conversion."""
    return repr(float(v))


def vec(values):
    return [s_(v) for v in values]


def weighted_J(cds, weights=None):
    """`J = SUM_i w_i * CD_i`, the multipoint objective, summed IN THE REGISTERED
    ORDER so the value is reproducible bit for bit from the artefact."""
    w = WEIGHTS_REGISTERED if weights is None else list(weights)
    tot = 0.0
    for wi, cd in zip(w, cds):
        tot += float(wi) * float(cd)
    return tot


def _finite(v):
    return isinstance(v, float) and math.isfinite(v)


def build_fd_row(step, plus, minus):
    """One central-difference entry over the multipoint quantities.

    `plus` / `minus` are {"J": float, "CD": [3 floats], "CL": [3 floats]} and the
    derivatives are computed HERE -- the grader never re-derives them, it reads
    what the producer wrote."""
    st = float(step)
    d = {"J": s_((float(plus["J"]) - float(minus["J"])) / (2.0 * st)),
         "CD": vec([(float(a) - float(b)) / (2.0 * st)
                    for a, b in zip(plus["CD"], minus["CD"])]),
         "CL": vec([(float(a) - float(b)) / (2.0 * st)
                    for a, b in zip(plus["CL"], minus["CL"])])}
    return {"step": st, "ok": True, "d": d,
            "plus": {"J": s_(plus["J"]), "CD": vec(plus["CD"]), "CL": vec(plus["CL"])},
            "minus": {"J": s_(minus["J"]), "CD": vec(minus["CD"]), "CL": vec(minus["CL"])}}


def build_fd_row_failed(step, error):
    """A FAILED evaluation is WRITTEN, not omitted.  Section 6 / G-EVALFAIL: an
    omitted row cannot be graded; a present row marked failed can, and its pairs
    read FD_STEP_FAILED_OR_ABSENT while the row is graded on the survivors."""
    return {"step": float(step), "ok": False, "error": str(error)[:400]}


def build_ctrl_row(J0, cd0, cl0):
    """THE RULE-3 PLANTED-ZERO CONTROL COMPONENT.  Synthetic, no solve.

    `fd`      -- identical values on both sides -> derivative EXACTLY 0.0 for
                 `J` and for every scenario's `CD` and `CL`.  This is the ZERO
                 the reader must be able to read.
    `planted` -- the plus side moved by PLANT on `J` and on every scenario's
                 `CD` and `CL` -> derivative EXACTLY PLANT/(2*CTRL_STEP)
                 everywhere.  This is the NON-ZERO the same reader must be able
                 to see, through the same keys, on the same path.

    A control that empties the tuple it tests certifies blindness.  This one
    changes VALUES inside tuples the reader must traverse in full -- three CD
    entries, three CL entries and the objective -- and both the instrument (on
    disk read-back, `ctrl_readback_check`) and the comparator re-read it.

    DISCLOSED, because it is the difference between an exact control and an
    approximate one: the planted `J` is written as `J0 + PLANT` DIRECTLY and is
    NOT re-summed from the moved `CD` vector.  `SUM_i w_i (CD_i + PLANT)` and
    `J0 + PLANT` are equal in real arithmetic and need not be equal in binary
    floating point, and a control whose expected value depends on a rounding is
    a control that can fail for a reason that is not the one it tests.  The
    read-back check is stated to a RELATIVE tolerance of 1e-12 for the same
    reason (SO-2a's own discipline, so2a_xg.py:461)."""
    zero = {"J": float(J0), "CD": [float(v) for v in cd0], "CL": [float(v) for v in cl0]}
    plant_plus = {"J": float(J0) + PLANT,
                  "CD": [float(v) + PLANT for v in cd0],
                  "CL": [float(v) + PLANT for v in cl0]}
    return {"dv": "CTRL", "idx": 0, "status": "CONTROL",
            "fd": {repr(CTRL_STEP): build_fd_row(CTRL_STEP, zero, zero)},
            "planted": build_fd_row(CTRL_STEP, plant_plus, zero),
            "plant": PLANT,
            "note": ("synthetic, no solve: `fd` has identical values on both sides so every "
                     "derivative -- J and all three CD and all three CL -- is exactly 0.0; "
                     "`planted` moves the plus side of every one of those seven quantities by "
                     "PLANT so every derivative is exactly PLANT/(2*step).  The planted J is "
                     "J0+PLANT written directly, NOT re-summed from the moved CD vector")}


def build_identity_block(alphas_read_back, alpha_paths, weights, dvs_alphas=None):
    """The multipoint identity G-ALPHA reads.  BOTH lists are carried: what the
    MODEL held (`alphas_read_back`) and what the DOCUMENT registered
    (`alphas_registered`).  The comparator compares them; this instrument never
    substitutes one for the other, because an instrument that echoes its own
    constant back cannot detect a scenario wired to the wrong angle."""
    return {"scenarios": list(SCENARIOS),
            "alphas_read_back": ([None if a is None else s_(a) for a in alphas_read_back]),
            "alphas_registered": vec(ALPHAS_REGISTERED),
            "alpha_read_paths": list(alpha_paths),
            "alphas_from_dvs": (None if dvs_alphas is None
                                else [None if a is None else s_(a) for a in dvs_alphas]),
            "weights": vec(weights),
            "weights_registered": vec(WEIGHTS_REGISTERED),
            "objective": "J = SUM_i w_i * CD_i",
            "objective_path": OBJ_PATH,
            "patchV_is_a_design_variable": False,
            "patchV_note": ("line 4: alpha is this item's OPERATING POINT and cannot "
                            "simultaneously be a design variable trimmed to a lift target.  "
                            "SO-1a's patchV[1] is REMOVED from the graded set and the removal "
                            "is registered, not silent")}


def build_X_record(nprocs, producer_md5, identity, mp_identity, adjoint,
                   J_baseline, cd_baseline, cl_baseline, totals_wall_s=None,
                   evaluations_declared=None, evaluations_failed=0, eval_failures=None):
    """The X (adjoint / total-derivative) artefact.

    `adjoint[of][dv]` is a FLAT list of repr strings over the dv vector.  `of`
    runs over "J", "CD0".."CD2" and "CL0".."CL2" -- the PER-SCENARIO CD rows are
    what G-MP-STRUCT sums against the assembled J row, and they are the reason
    this artefact is worth more than SO-1a's."""
    return {"item": ITEM, "mode": "X", "producer_md5": producer_md5, "nprocs": nprocs,
            "identity": identity, "multipoint": mp_identity,
            "adjoint": adjoint,
            "adjoint_of_keys": sorted(adjoint.keys()),
            "J_baseline": s_(J_baseline),
            "CD_baseline": vec(cd_baseline), "CL_baseline": vec(cl_baseline),
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "compute_totals_wall_s": totals_wall_s,
            "evaluations_declared": (1 if evaluations_declared is None
                                     else int(evaluations_declared)),
            "evaluations_failed": int(evaluations_failed),
            "evaluation_failures": list(eval_failures or []),
            "optimiser": None,
            "optimiser_note": ("G-NOOPT: this item runs NO optimiser.  There is no run_driver, "
                               "no pyOptSparse call, no major count and no IPOPT/SLSQP/SNOPT "
                               "exit line anywhere in the registered program, and the "
                               "comparator REFUSES on any artefact that carries one")}


def build_F_record(nprocs, producer_md5, identity, mp_identity, rows,
                   J_baseline, J_baseline_repeat, cd_baseline, cd_baseline_repeat,
                   cl_baseline, cl_baseline_repeat,
                   eta_raw, eta_used, eta_floored, baseline_dvs,
                   evaluations_declared=None, evaluations_failed=0, eval_failures=None):
    """The F (finite-difference) artefact."""
    return {"item": ITEM, "mode": "F", "producer_md5": producer_md5, "nprocs": nprocs,
            "identity": identity, "multipoint": mp_identity,
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": STEPS, "tb_steps": TB_STEPS, "ctrl_step": CTRL_STEP, "plant": PLANT,
            "J_baseline": s_(J_baseline), "J_baseline_repeat": s_(J_baseline_repeat),
            "CD_baseline": vec(cd_baseline), "CD_baseline_repeat": vec(cd_baseline_repeat),
            "CL_baseline": vec(cl_baseline), "CL_baseline_repeat": vec(cl_baseline_repeat),
            "eta_raw": s_(eta_raw), "eta_used": s_(eta_used), "eta_floored": bool(eta_floored),
            "eta_note": ("worst-quantity repeatability of J and of every scenario's CD and CL "
                         "across two baseline evaluations, MEASURED BEFORE ANY FD STEP IS "
                         "SIZED (line 3).  It is the floor the h = 1e-8 trivial baseline is "
                         "registered to sit at or below"),
            "baseline_dvs": baseline_dvs,
            "evaluations_declared": (EVALS_DECLARED if evaluations_declared is None
                                     else int(evaluations_declared)),
            "evaluations_failed": int(evaluations_failed),
            "evaluation_failures": list(eval_failures or []),
            "rows": rows, "n_rows": len(rows),
            "optimiser": None,
            "optimiser_note": ("G-NOOPT: no optimiser, no majors, no run_driver.  See "
                               "build_X_record's note; the comparator checks both artefacts")}


def write_artefact(path, rec, terminal, extra=""):
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("%s %s%s\n" % (terminal, path, extra))


# ===================== rule 3: THE READ-BACK, AS A DRIVABLE FUNCTION ==========
# SO-2a's equivalent lives inline in `main()` (so2a_xg.py:445-470), behind mpi4py,
# openmdao and a container, so its REFUSAL branch has never been driven on the
# host.  Here it is a function of a path, and the comparator's selftest drives it
# in both directions -- a live plant SEEN, a dead plant REFUSED.

def ctrl_readback_check(jsonl_path):
    """Re-read the CTRL row FROM DISK, through the same keys the comparator's
    reader traverses, and report whether the planted non-zero is visible.

    Returns (ok, detail).  `ok` is True ONLY when every zero-side derivative --
    J and all three CD and all three CL -- reads EXACTLY 0.0 AND every planted
    derivative reads PLANT/(2*CTRL_STEP) to a relative 1e-12.  A missing row, an
    emptied tuple and a dead plant are three DIFFERENT detail readings and none
    of them is `ok`."""
    want = PLANT / (2.0 * CTRL_STEP)
    row = None
    try:
        with open(jsonl_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    row = rec.get("row")
    except (OSError, ValueError) as exc:                      # noqa: BLE001
        return False, {"reason": "jsonl_unreadable", "path": jsonl_path,
                       "error": "%s: %s" % (type(exc).__name__, exc)}
    if row is None:
        return False, {"reason": "control_row_absent", "path": jsonl_path}
    try:
        z = row["fd"][repr(CTRL_STEP)]["d"]
        p = row["planted"]["d"]
        zeros = [float(z["J"])] + [float(v) for v in z["CD"]] + [float(v) for v in z["CL"]]
        plants = [float(p["J"])] + [float(v) for v in p["CD"]] + [float(v) for v in p["CL"]]
    except (KeyError, TypeError, ValueError) as exc:          # noqa: BLE001
        return False, {"reason": "control_row_malformed",
                       "error": "%s: %s" % (type(exc).__name__, exc)}
    # THE EMPTINESS CHECK COMES FIRST, BEFORE ANY VERDICT.  A control that empties
    # the tuple it tests must REFUSE, not pass over a zero-length loop -- every
    # `all()` over an empty sequence is True, and that is how a control certifies
    # blindness (Sanaa 2026-08-28).
    if len(zeros) != 1 + 2 * N_SCEN or len(plants) != 1 + 2 * N_SCEN:
        return False, {"reason": "control_tuple_EMPTY_or_short",
                       "n_zero_side": len(zeros), "n_plant_side": len(plants),
                       "expected": 1 + 2 * N_SCEN,
                       "note": "a control that empties the tuple it tests certifies blindness"}
    nonzero = [v for v in zeros if v != 0.0]
    dead = [v for v in plants
            if not _finite(v) or abs(v - want) > 1e-12 * abs(want)]
    if nonzero or dead:
        return False, {"reason": ("zero_side_not_zero" if nonzero else "plant_not_seen"),
                       "nonzero_in_zero_side": nonzero[:5], "planted_read": plants,
                       "want": want}
    return True, {"n_zero_entries_read": len(zeros), "planted_read": plants, "want": want,
                  "both_directions": True}


# ===================== the run ================================================
def parse_mode(argv):
    mode = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    if mode not in ("X", "F"):
        sys.stderr.write("SO3AR_XF usage: so3ar_xf.py -mode X|F\n")
        sys.exit(64)
    return mode


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("SO3AR_XF REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("SO3AR_XF REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "so3ar_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    jsonl = JSONL_F if mode == "F" else JSONL_X

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    ident.update(case_write_compression())
    emit({"kind": "identity", "item": ITEM, "mode": mode, "nprocs": nprocs,
          "producer_md5": got, "solverName": ns["daOptions"].get("solverName"),
          "U0": ns.get("U0"), "CL_target": ns.get("CL_target"), "p0": ns.get("p0"),
          "alphas_declared_by_producer": ns.get("ALPHAS"), "weights_declared_by_producer": ns.get("WEIGHTS"),
          **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    base = {"shape": np.array(prob.get_val("shape"), dtype=float).copy()}
    baseline_dvs = {"shape": [s_(v) for v in base["shape"]]}
    emit({"kind": "baseline_dvs", "n_shape": int(base["shape"].size), **baseline_dvs})

    # ---- G-ALPHA's SOURCE: what the MODEL actually holds, read back per scenario.
    # Two independent paths are tried and the one that resolved is RECORDED, so a
    # scenario whose angle never reached the solver cannot be papered over by the
    # dvs-side value.  An unresolved path is written as None, never as the
    # registered constant -- an instrument that echoes its own constant cannot
    # detect a scenario wired to the wrong angle.
    alphas_read, alpha_paths, dvs_alphas = [], [], []
    for i, sc in enumerate(SCENARIOS):
        a, used = None, None
        for cand in ("%s.patchV" % sc, "patchV%d" % i):
            try:
                v = np.atleast_1d(np.array(prob.get_val(cand), dtype=float).ravel())
                if v.size >= 2:
                    a, used = float(v[1]), cand
                    break
            except Exception:                                 # noqa: BLE001
                continue
        alphas_read.append(a)
        alpha_paths.append(used)
        d = None
        try:
            v = np.atleast_1d(np.array(prob.get_val("patchV%d" % i), dtype=float).ravel())
            if v.size >= 2:
                d = float(v[1])
        except Exception:                                     # noqa: BLE001
            d = None
        dvs_alphas.append(d)
    mp_ident = build_identity_block(alphas_read, alpha_paths, WEIGHTS_REGISTERED, dvs_alphas)
    emit({"kind": "multipoint_identity", **mp_ident})

    CD_PATHS = ["%s.aero_post.CD" % sc for sc in SCENARIOS]
    CL_PATHS = ["%s.aero_post.CL" % sc for sc in SCENARIOS]

    n_failed = [0]
    failures = []

    def primal(tag):
        """ONE MULTIPOINT EVALUATION = THREE PRIMALS.  It survives only if all
        three converge, which is section 6's whole arithmetic: a per-primal
        failure probability p becomes 1-(1-p)^3 per evaluation.  A failure --
        an exception OR a non-finite reading -- is RAISED here with its tag, and
        the caller records it as a FAILED ROW rather than dropping it."""
        t0 = time.time()
        prob.run_model()
        cds = [float(prob.get_val(p)[0]) for p in CD_PATHS]
        cls = [float(prob.get_val(p)[0]) for p in CL_PATHS]
        try:
            Jv = float(prob.get_val(OBJ_PATH)[0])
            j_source = OBJ_PATH
        except Exception:                                     # noqa: BLE001
            Jv = weighted_J(cds)
            j_source = "RE-SUMMED IN THE INSTRUMENT (the model exposed no %s)" % OBJ_PATH
        bad = [n for n, v in [("J", Jv)]
               + [("CD%d" % i, v) for i, v in enumerate(cds)]
               + [("CL%d" % i, v) for i, v in enumerate(cls)] if not _finite(v)]
        emit({"kind": "primal", "tag": tag, "J": s_(Jv), "J_source": j_source,
              "CD": vec(cds), "CL": vec(cls), "non_finite": bad,
              "wall_s": round(time.time() - t0, 3)})
        if bad:
            raise ValueError("NON-FINITE evaluation at %s: %s" % (tag, ",".join(bad)))
        return {"J": Jv, "CD": cds, "CL": cls}

    def evaluate(tag):
        """The counted wrapper.  Every declared evaluation goes through here so
        `evaluations_failed` is a COUNT OF ATTEMPTS THAT FAILED and not a guess."""
        try:
            return primal(tag), None
        except Exception as exc:                              # noqa: BLE001
            n_failed[0] += 1
            err = repr(exc)[:400]
            failures.append({"tag": tag, "error": err})
            emit({"kind": "evaluation_failed", "tag": tag, "error": err,
                  "note": "P-EVAL: a failed evaluation is a RECORDED, COUNTED, GRADABLE state"})
            return None, err

    b0, b0err = evaluate("baseline")
    if b0 is None:
        emit({"kind": "baseline_failed", "mode": mode, "error": b0err,
              "note": ("the BASELINE evaluation failed.  The artefact still lands, because "
                       "section 6 registers a failed evaluation as a GRADABLE state and a "
                       "refusal here would move D6-GRADER-DEF-1 one file upstream")})
        # The baseline itself failing is a real outcome and the artefact must
        # still land, so the comparator can grade a state it registered (section
        # 6).  A refusal here would be D6-GRADER-DEF-1 moved one file upstream.
        if rank == 0:
            mp = mp_ident
            if mode == "X":
                rec = build_X_record(nprocs, got, ident, mp, {}, float("nan"),
                                     [float("nan")] * N_SCEN, [float("nan")] * N_SCEN,
                                     None, 1, n_failed[0], failures)
                write_artefact(OUT_X, rec, TERMINAL_X, " baseline_evaluation_FAILED=1")
            else:
                rec = build_F_record(nprocs, got, ident, mp, [], float("nan"), float("nan"),
                                     [float("nan")] * N_SCEN, [float("nan")] * N_SCEN,
                                     [float("nan")] * N_SCEN, [float("nan")] * N_SCEN,
                                     0.0, ETA_FLOOR, True, baseline_dvs,
                                     EVALS_DECLARED, n_failed[0], failures)
                write_artefact(OUT_F, rec, TERMINAL_F, " n_rows=0 baseline_evaluation_FAILED=1")
        MPI.COMM_WORLD.Barrier()
        return

    if mode == "X":
        t0 = time.time()
        of = [OBJ_PATH] + CD_PATHS + CL_PATHS
        totals = prob.compute_totals(of=of, wrt=["shape"])
        tw = round(time.time() - t0, 3)
        emit({"kind": "compute_totals", "of": of, "wrt": ["shape"], "wall_s": tw})
        adj = {}
        keys = [("J", OBJ_PATH)] + [("CD%d" % i, p) for i, p in enumerate(CD_PATHS)] \
            + [("CL%d" % i, p) for i, p in enumerate(CL_PATHS)]
        for key, path in keys:
            arr = np.atleast_1d(np.array(totals[(path, "shape")]).ravel())
            adj[key] = {"shape": [s_(v) for v in arr]}
            emit({"kind": "adjoint", "of": key, "path": path, "dv": "shape",
                  "n": int(arr.size), "values": adj[key]["shape"]})
        if rank == 0:
            rec = build_X_record(nprocs, got, ident, mp_ident, adj, b0["J"], b0["CD"],
                                 b0["CL"], tw, 1, n_failed[0], failures)
            write_artefact(OUT_X, rec, TERMINAL_X)
        MPI.COMM_WORLD.Barrier()
        return

    # ---- mode F: eta on EVERY graded quantity, then central differences --------
    b1, b1err = evaluate("baseline_repeat")
    if b1 is None:
        b1 = {"J": b0["J"], "CD": list(b0["CD"]), "CL": list(b0["CL"])}
        emit({"kind": "eta_note", "error": b1err,
              "note": ("the baseline REPEAT evaluation failed; the repeat reading falls back to "
                       "the FIRST baseline, so eta_raw is EXACTLY 0.0, is FLOORED and is FLAGGED "
                       "-- `eta_floored` true beside a counted evaluation failure is how a reader "
                       "tells this state from a genuinely bit-repeatable one.  The failure is "
                       "counted in evaluations_failed and named in evaluation_failures")})
    eta_raw = 0.0
    for a, b in ([(b0["J"], b1["J"])]
                 + list(zip(b0["CD"], b1["CD"])) + list(zip(b0["CL"], b1["CL"]))):
        eta_raw = max(eta_raw, abs(float(a) - float(b)))
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": s_(eta_raw), "eta_used": s_(eta),
          "eta_floored": eta_flagged,
          "note": ("eta is the worst-quantity repeatability of J and of every scenario's CD and "
                   "CL across two baseline evaluations, measured BEFORE any FD step is sized")})

    def set_perturbed(dv, idx, delta):
        prob.set_val("shape", base["shape"].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    def fd_at(dv, idx, s, label):
        key = repr(s)
        set_perturbed(dv, idx, +s)
        pp, perr = evaluate("%s %s[%d]+%g" % (label, dv, idx, s))
        set_perturbed(dv, idx, -s)
        mm, merr = evaluate("%s %s[%d]-%g" % (label, dv, idx, s))
        if pp is None or mm is None:
            return key, build_fd_row_failed(s, perr or merr)
        try:
            return key, build_fd_row(s, pp, mm)
        except Exception as exc:                              # noqa: BLE001
            return key, build_fd_row_failed(s, repr(exc))

    rows = []
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": int(base[dv].size), "fd": {}, "tb": {}})
            continue
        fd = {}
        for s in STEPS[dv]:
            k, row = fd_at(dv, idx, s, "FD")
            fd[k] = row
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": row})
        # ---- THE CHARTER-4 TRIVIAL BASELINE at the DELIBERATELY WRONG step ----
        tb = {}
        for s in TB_STEPS[dv]:
            k, row = fd_at(dv, idx, s, "TB")
            tb[k] = row
            emit({"kind": "tb_step", "dv": dv, "idx": idx, "step": s, "row": row})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd, "tb": tb})
    prob.set_val("shape", base["shape"].copy())

    ctrl = build_ctrl_row(b0["J"], b0["CD"], b0["CL"])
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        # READ BACK FROM DISK what was just emitted; REFUSE if the plant is
        # invisible.  The check is a NAMED FUNCTION so its refusal branch is
        # drivable on the host without a container -- see `ctrl_readback_check`.
        ok, detail = ctrl_readback_check(jsonl)
        if not ok:
            sys.stderr.write("SO3AR_XF REFUSE planted-zero control not seen on read-back: %s\n"
                             % json.dumps(detail, sort_keys=True, default=str))
            sys.exit(2)
        sys.stdout.write("SO3AR_PLANTED_ZERO_CONTROL_SEEN n_zero_entries=%d want=%r\n"
                         % (detail["n_zero_entries_read"], detail["want"]))
        rec = build_F_record(nprocs, got, ident, mp_ident, rows, b0["J"], b1["J"],
                             b0["CD"], b1["CD"], b0["CL"], b1["CL"],
                             eta_raw, eta, eta_flagged, baseline_dvs,
                             EVALS_DECLARED, n_failed[0], failures)
        write_artefact(OUT_F, rec, TERMINAL_F,
                       " n_rows=%d evaluations_declared=%d evaluations_failed=%d"
                       % (len(rows), EVALS_DECLARED, n_failed[0]))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
